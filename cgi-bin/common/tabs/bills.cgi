#!/usr/bin/perl
#####################################################################
########                   BILLS	      		    #########
#####################################################################
sub load_tabsconf {
# --------------------------------------------------------
	if ($in{'tab'} eq 6){
		## Notes Tab
		$va{'tab_type'}  = 'notes';
		$va{'tab_title'} = &trans_txt('notes');
		$va{'tab_table'} = 'sl_bills_notes';
	}elsif($in{'tab'} eq 7){
		## Notes Tab
		$va{'tab_type'}  = 'logs';
		$va{'tab_title'} = &trans_txt('logs');
		$va{'tab_table'} = 'sl_bills';
	}elsif($in{'tab'} eq 4){
		## Movs Tab
		$va{'tab_type'}  = 'movs';
		$va{'tab_title'} = &trans_txt('logs');
		$va{'tab_table'} = 'sl_bills';
		$va{'tab_idvalue'} = $in{'id_bills'};
	}else {
		$in{'tab'} = 3;
	}
}

sub load_tabs1 {	
# --------------------------------------------------------
	$in{'type'} = &load_name("sl_bills","ID_bills",$in{'view'},"Type") if (!$in{'type'});
	$in{'status'} = &load_name("sl_bills","ID_bills",$in{'view'},"Status") if (!$in{'status'});
	$in{'amount'} = &load_name("sl_bills","ID_bills",$in{'view'},"Amount") if (!$in{'amount'});
	$in{'id_vendors'} = &load_name("sl_bills","ID_bills",$in{'id_bills'},"ID_vendors");
	delete($in{'add'});

	my ($bill_amount_remaining) = &bills_amount_due($in{'view'});
	$va{'messages'} = '';
	
	if ($in{'type'} !~ /Bill|Credit/ ) {

		$va{'tab_messages'} = &trans_txt('This info is only for Bills');
		$va{'tabvisible'} = ' style="display:none;"';

	}else {

		if ($in{'status'} ne 'New') {
			## Si este bill esta pagado solo mostramos los datos del PO al que se aplico
			
			my (@c) = split(/,/,$cfg{'srcolors'});
			my ($sth) = &Do_SQL("SELECT count(*) FROM sl_bills INNER JOIN sl_bills_pos USING(ID_bills) INNER JOIN sl_purchaseorders USING(ID_purchaseorders)  WHERE 1 AND ID_bills='$in{'id_bills'}' AND sl_purchaseorders.`Type` != 'PO Services';");
			$va{'matches'} = $sth->fetchrow;

			if ($va{'matches'}>0){

				(!$in{'nh'}) and ($in{'nh'}=1);
				$first = ($in{'nh'} - 1) * $usr{'pref_maxh'};			
				($va{'pageslist'},$qs) = &pages_list($in{'nh'},"/cgi-bin/mod/$usr{'application'}/dbman",$va{'matches'},$usr{'pref_maxh'});
				
				my ($total_po,$total_due,$total_amount);
				## Necesitamos conocer la deuda de acuerdo a lo Recibido
				my ($sth) = &Do_SQL("SELECT sl_bills_pos.Amount, sl_purchaseorders.ID_purchaseorders, sl_purchaseorders.Date, sl_purchaseorders.POTerms
										, ifnull((SELECT SUM(Total) FROM sl_purchaseorders_items WHERE ID_purchaseorders = sl_purchaseorders.ID_purchaseorders), 0)as TotalPO
										, ifnull((SELECT SUM(sl_bills_pos.Amount) FROM sl_bills INNER JOIN sl_bills_pos USING(ID_bills) WHERE ID_purchaseorders = sl_purchaseorders.ID_purchaseorders AND sl_bills.Status = 'Paid'), 0)as TotalPaid
										, ifnull((SELECT SUM(sl_bills_pos.Amount) FROM sl_bills INNER JOIN sl_bills_pos USING(ID_bills) WHERE ID_purchaseorders = sl_purchaseorders.ID_purchaseorders AND sl_bills.Status <> 'Void'), 0)as TotalInBills
										/*, ifnull((SELECT SUM(Total) FROM sl_purchaseorders_adj WHERE ID_purchaseorders = sl_purchaseorders.ID_purchaseorders),0)as TotalAdj*/
										, ifnull((SELECT SUM(Received * Price *(1+Tax_percent)) FROM sl_purchaseorders_items WHERE ID_purchaseorders = sl_purchaseorders.ID_purchaseorders), 0)as TotalWR							
									FROM sl_bills 
										INNER JOIN sl_bills_pos USING(ID_bills) 
										INNER JOIN sl_purchaseorders USING(ID_purchaseorders) 
									WHERE 1 
										AND ID_bills=$in{'id_bills'} 
										AND sl_purchaseorders.`Type` != 'PO Services'
									ORDER BY sl_bills.Date DESC LIMIT $first,$usr{'pref_maxh'};");
				
				while ($rec = $sth->fetchrow_hashref){
					$d = 1 - $d;

					$total_po += $rec->{'TotalPO'};
					$total_wr += $rec->{'TotalWR'};
					$total_in_bills += $rec->{'TotalInBills'};
					$total_paid += $rec->{'TotalPaid'};
					$total_due += ($rec->{'TotalWR'} - $rec->{'TotalInBills'});
					$total_amount += $rec->{'Amount'};


					my $amount_due = ($rec->{'Total'}-$rec->{'Amount'});
					$va{'searchresults'} .= "<tr bgcolor='$c[$d]' onmouseover='m_over(this)' onmouseout='m_out(this)'>\n";
					$va{'searchresults'} .= "   <td class='smalltext'></td>\n";
					$va{'searchresults'} .= "   <td><a href=\"/cgi-bin/mod/[ur_application]/dbman?cmd=mer_po&view=".$rec->{'ID_purchaseorders'}."\">".$rec->{'ID_purchaseorders'}."</a></td>\n";
					$va{'searchresults'} .= "   <td class='smalltext'>".$rec->{'Date'}."</td>\n";
					$va{'searchresults'} .= "   <td class='smalltext'>".$rec->{'POTerms'}."</td>\n";
					$va{'searchresults'} .= "   <td class='smalltext' align='right' style='color: #5c5b5b;'>".&format_price($rec->{'TotalPO'})."</td>\n";
					$va{'searchresults'} .= "   <td class='smalltext' align='right'>".&format_price($rec->{'TotalWR'})."</td>\n";
					$va{'searchresults'} .= "   <td class='smalltext' align='right'>".&format_price($rec->{'TotalInBills'})."</td>\n";
					$va{'searchresults'} .= "   <td class='smalltext' align='right'>".&format_price($rec->{'TotalPaid'})."</td>\n";
					$va{'searchresults'} .= "   <td class='smalltext' align='right'>".&format_price($rec->{'TotalWR'} - $rec->{'TotalInBills'})."</td>\n";
					$va{'searchresults'} .= "   <td class='smalltext' align='right'>".&format_price($rec->{'Amount'})."</td>\n";
					$va{'searchresults'} .= "</tr>\n";
				}

				$va{'searchresults'} .= "<tr>\n";
				$va{'searchresults'} .= "   <td colspan='4' class='smalltext' align='right'>Total</td>\n";
				$va{'searchresults'} .= "   <td class='smalltext' align='right' style='color: #5c5b5b;'>".&format_price($total_po)."</td>\n";
				$va{'searchresults'} .= "   <td class='smalltext' align='right'>".&format_price($total_wr)."</td>\n";
				$va{'searchresults'} .= "   <td class='smalltext' align='right'>".&format_price($total_in_bills)."</td>\n";
				$va{'searchresults'} .= "   <td class='smalltext' align='right'>".&format_price($total_paid)."</td>\n";
				$va{'searchresults'} .= "   <td class='smalltext' align='right'>".&format_price($total_due)."</td>\n";
				$va{'searchresults'} .= "   <td class='smalltext' align='right'>".&format_price($total_amount)."</td>\n";
				$va{'searchresults'} .= "</tr>\n";
			}else{
				$va{'matches'} =0;
				$va{'pageslist'} = 1;
				$va{'searchresults'} = qq|
					<tr>
						<td colspan='7' align='center'>|.&trans_txt('search_nomatches').qq|</td>
					</tr>\n|;
			}

		}else {

			$in{'addpo'} = int ($in{'addpo'});
			$in{'delpo'} = int ($in{'delpo'});
			
			my ($sth) = &Do_SQL("SELECT Amount FROM sl_bills_pos WHERE ID_bills='$in{'id_bills'}' AND ID_purchaseorders=$in{'delpo'}");
			($va{'amount'}) = $sth->fetchrow_array();	

			my ($sth) = &Do_SQL("SELECT Type, ID_vendors, Status, Amount FROM sl_bills WHERE ID_bills='$in{'id_bills'}'");
			($in{'type'}, $in{'id_vendors'}, $in{'status'}, $va{'amount'}) = $sth->fetchrow_array();

			my (@c) = split(/,/,$cfg{'srcolors'});
			my ($d,$query);
			
			my $where = "";
			if( ($in{'type'} eq 'Credit') ){
				$sth_po = &Do_SQL("SELECT ID_purchaseorders 
									FROM sl_bills_pos  
									WHERE ID_bills='$in{'id_bills'}';");
				my $id_po_rvendor = $sth_po->fetchrow();
				$where = "AND sl_purchaseorders.ID_purchaseorders='$id_po_rvendor'";
			}else{
				$where = "AND sl_purchaseorders.ID_vendors = '$in{'id_vendors'}'
						  AND sl_purchaseorders.Status NOT IN('Cancelled','Paid')
						  AND sl_purchaseorders.Auth = 'Approved' 
						  AND TotalReceived > 0
						  AND ROUND(IFNULL((SELECT SUM(sl_bills_pos.Amount) FROM sl_bills INNER JOIN sl_bills_pos USING(ID_bills) WHERE ID_purchaseorders = sl_purchaseorders.ID_purchaseorders AND sl_bills.Status = 'Paid'), 0), 2) < ROUND(TotalWR, 2)";
			}
			$where .= " AND sl_purchaseorders.`Type` != 'PO Services'";
			
			#if ($va{'amount'} or $va{'amount'} eq "0.00" or int($va{'amount'}) == 0){
				
				my ($sth) = &Do_SQL("SELECT COUNT(*) 
									FROM sl_purchaseorders 
										INNER JOIN (
											SELECT SUM(Total) AS TotalPO, ROUND(SUM((Price*Received) * (1+Tax_percent)), 3) TotalWR, IFNULL(SUM(Received),0)as TotalReceived, sl_purchaseorders_items.ID_purchaseorders
											FROM sl_purchaseorders_items
											GROUP BY sl_purchaseorders_items.ID_purchaseorders
										) AS po_items USING(ID_purchaseorders)
										LEFT JOIN(
											SELECT sl_bills.Status, sl_bills_pos.ID_purchaseorders, SUM(sl_bills_pos.Amount) AS TotalInBills
											FROM sl_bills 
												INNER JOIN sl_bills_pos USING(ID_bills) 
											WHERE sl_bills.Status <> 'Void'
											GROUP BY sl_bills_pos.ID_purchaseorders
										) AS bills_pos USING(ID_purchaseorders)
									WHERE 1 $where;");
				$va{'matches'} = $sth->fetchrow;
				
				if ($va{'matches'} > 0){
					(!$in{'nh'}) and ($in{'nh'}=1);
					$first = ($in{'nh'} - 1) * $usr{'pref_maxh'};			
					($va{'pageslist'},$qs) = &pages_list($in{'nh'},"/cgi-bin/mod/$usr{'application'}/dbman",$va{'matches'},$usr{'pref_maxh'});
					
					my ($sth) = &Do_SQL("SELECT 
											sl_purchaseorders.Status, ID_purchaseorders, PODate, POTerms
											, po_items.TotalPO, po_items.TotalWR 
											, IFNULL(bills_pos.TotalInBills, 0) AS TotalInBills
											, bills_pos.Status AS StatusBill
											, IFNULL((SELECT SUM(sl_bills_pos.Amount) FROM sl_bills INNER JOIN sl_bills_pos USING(ID_bills) WHERE ID_purchaseorders = sl_purchaseorders.ID_purchaseorders AND sl_bills.Status = 'Paid'), 0) AS TotalPaid
										FROM sl_purchaseorders 
											INNER JOIN (
												SELECT SUM(Total) AS TotalPO, ROUND(SUM((Price*Received) * (1+Tax_percent)), 3) TotalWR, IFNULL(SUM(Received),0)as TotalReceived, sl_purchaseorders_items.ID_purchaseorders
												FROM sl_purchaseorders_items
												GROUP BY sl_purchaseorders_items.ID_purchaseorders
											) AS po_items USING(ID_purchaseorders)
											LEFT JOIN(
												SELECT sl_bills.Status, sl_bills_pos.ID_purchaseorders, SUM(sl_bills_pos.Amount) AS TotalInBills
												FROM sl_bills 
													INNER JOIN sl_bills_pos USING(ID_bills)
												WHERE sl_bills.Status <> 'Void'
												GROUP BY sl_bills_pos.ID_purchaseorders
											) AS bills_pos USING(ID_purchaseorders)
										WHERE 1 
											$where 
										ORDER BY sl_purchaseorders.Date DESC
										LIMIT $first,$usr{'pref_maxh'};");
					while ($rec = $sth->fetchrow_hashref) {
						
						# monto total del PO.
						$in{'amount_po'} = $rec->{'TotalPO'};

						# monto total de la Recepcion
						$in{'amount_wr'} = $rec->{'TotalWR'};						
						
						# monto total pagado
						$in{'amount_billsa'} = $rec->{'TotalInBills'} > 0 ? $rec->{'TotalInBills'} : 0;

						# Monto total del PO - El monto que hay en bills activos
						$va{'total_due'} = ($in{'amount_wr'} - $in{'amount_billsa'});

						# Estilos
						my $po_line_style = '#5c5b5b';
						my $wr_line_style = ($in{'amount_po'} > $in{'amount_wr'}) ? '#550202;' : '#0f0f0f';						
						my $ba_line_style = ($rec->{'TotalInBills'} > 0) ? '#2b5e9c' : '#0f0f0f';
						my $bp_line_style = ($rec->{'TotalPaid'} > 0) ? '#025e02' : '#0f0f0f';

						my ($sth5) = &Do_SQL("SELECT sl_bills.ID_bills, sl_bills_pos.Amount, sl_bills_pos.ID_bills_pos FROM sl_bills INNER JOIN sl_bills_pos USING(ID_bills) WHERE ID_bills = '".$in{'id_bills'}."' AND ID_purchaseorders = '".$rec->{'ID_purchaseorders'}."' ");
						$rec5 = $sth5->fetchrow_hashref;

						##########
						########## Revisamos que el PO no este activo en otro Bill Pendiente de cerrarse
						##########
						my $po_blocked_bybill = $va{'total_due'} > 0 ? 0 : 1;

						$va{'searchresults2'} = "   <td class='smalltext' align='right'>".&format_price($rec->{'Amount'})."</td>\n";

						# El PO esta en este Bill, si ya se encuentra en otro no se deberia de mostrar
						if ($rec5->{'ID_bills'} eq $in{'id_bills'} and $in{'status'} ne "Paid" and $in{'status'} ne "Processed") {
							$va{'searchresults'} .= "   <td class='smalltext'><a href='/cgi-bin/mod/$usr{'application'}/dbman?cmd=mer_bills&view=".$in{'id_bills'}."&delpo=".$rec5->{'ID_bills_pos'}."&nh=$in{'nh'}'><img src='$va{'imgurl'}/$usr{'pref_style'}/b_drop.png' title='Drop' alt='' border='0'></a></td>\n";					
							
							$va{'searchresults2'} = qq|   <td class='smalltext' align='right' valign='top'>
											<span >|.&format_price($rec5->{'Amount'}).qq|</span> 
											<span >
												<a href="#tabs" onClick="popup_show('ajax_windows', 'ajax_drag', 'ajax_exit', 'element-right', -1, -1,'tabs');
												loadDoc('/cgi-bin/common/apps/ajaxbuild?ajaxbuild=edit_bills_pos&id_bills=|.$rec5->{'ID_bills'}.qq|&id_bills_pos=|.$rec5->{'ID_bills_pos'}.qq|&id_po=|.$rec->{'ID_purchaseorders'}.qq|&amtdue=$va{'total_due'}&cmd=|.$in{'cmd'}.qq|&script_url=/cgi-bin/mod/|.$usr{'application'}.qq|/dbman');"><img src='$va{'imgurl'}/$usr{'pref_style'}/b_edit.png' title='Edit Amount' alt='' border='0'></a>
											</span>
											
											</td>\n|;
						}elsif (!$po_blocked_bybill and $in{'status'} ne "Paid"  and $in{'status'} ne "Processed" and $va{'total_due'} > 0) {
							$va{'searchresults'} .= "   <td class='smalltext'><a href='/cgi-bin/mod/$usr{'application'}/dbman?cmd=mer_bills&view=$in{'id_bills'}&addpo=$rec->{'ID_purchaseorders'}&nh=$in{'nh'}'><img src='$va{'imgurl'}/$usr{'pref_style'}/b_ok.png' title='Add' alt='' border='0'></a></td>\n";
						}else {
							$va{'searchresults'} .= "   <td class='smalltext'>---</td>\n";
						}
						
						$va{'searchresults'} .= "   <td class='smalltext'><a href='/cgi-bin/mod/$usr{'application'}/dbman?cmd=mer_po&view=$rec->{'ID_purchaseorders'}'>$rec->{'ID_purchaseorders'}</a></td>\n";
						$va{'searchresults'} .= "   <td class='smalltext'>$rec->{'PODate'}</td>\n";
						$va{'searchresults'} .= "   <td class='smalltext'>$rec->{'POTerms'}</td>\n";				
						$va{'searchresults'} .= "   <td class='smalltext' align='right' style='color:$po_line_style'>".&format_price($in{'amount_po'})."</td>\n";
						$va{'searchresults'} .= "   <td class='smalltext' align='right' style='color:$wr_line_style'>".&format_price($in{'amount_wr'})."</td>\n";
						$va{'searchresults'} .= "   <td class='smalltext' align='right' style='color:$ba_line_style'>".&format_price($rec->{'TotalInBills'})."</td>\n";
						$va{'searchresults'} .= "   <td class='smalltext' align='right' style='color:$bp_line_style'>".&format_price($rec->{'TotalPaid'})."</td>\n";
						$va{'searchresults'} .= "   <td class='smalltext' align='right' style='color:$due_line_style'>".&format_price($va{'total_due'})."</td>\n";
						$va{'searchresults'} .= $va{'searchresults2'};
						$va{'searchresults'} .= "</tr>\n";				
					}
				}else{
					$va{'matches'} =0;
					$va{'pageslist'} = 1;
					$va{'searchresults'} = qq|
						<tr>
							<td colspan='7' align='center'>|.&trans_txt('search_nomatches').qq|</td>
						</tr>\n|;
				}
			# }else{
			# 	$va{'matches'} =0;
			# 	$va{'pageslist'} = 1;
			# 	$va{'searchresults'} = qq|
			# 		<tr>
			# 			<td colspan='7' align='center'>|.&trans_txt('deposit_type').qq|</td>
			# 		</tr>\n|;
			# }

		}
	}
}

#############################################################################
#############################################################################
#	Function: load_tabs2
#
#	Created on: 05/02/2013  17:32:10
#
#	Author: Enrique Peña
#
#	Modifications: Alejandro Diaz:23042013
#
#	Parameters:
#
#	Returns:
#
#	See Also:
#
#
#
sub load_tabs2 {
#############################################################################
#############################################################################

	$in{'type'} = &load_name("sl_bills","ID_bills",$in{'view'},"Type") if (!$in{'type'});
	$in{'currency'} = &load_name("sl_bills","ID_bills",$in{'view'},"Currency") if (!$in{'currency'});
	$in{'status'} = &load_name("sl_bills","ID_bills",$in{'view'},"Status") if (!$in{'status'});
	$in{'id_vendors'} = &load_name("sl_bills","ID_bills",$in{'view'},"ID_vendors");
	$in{'currency_vendor'} = &load_name("sl_vendors","ID_vendors",$in{'id_vendors'},"Currency");
	$in{'amount'} = &load_name("sl_bills","ID_bills",$in{'view'},"Amount") if (!$in{'amount'});
	$in{'n_amount'} = $in{'amount'} if (!$in{'n_amount'} and $in{'amount'} > 0);
	$in{'n_id_accounts'} = $in{'id_accounts'} if ($in{'id_accounts'});
	
	my $special_perm = &check_permissions('mer_bills_modify_expense_paid','','') ? 1 : 0;
	my($sum_amount, $sum_tax);

	# Detectamos si es un Bill de Expenses
	my ($sth) = &Do_SQL("SELECT SUM(sl_bills_expenses.Amount)Amount, COUNT(*)AS nlines FROM sl_bills INNER JOIN sl_bills_expenses USING(ID_bills) WHERE ID_bills='$in{'view'}';");
	my ($amount_lines, $no_lines) = $sth->fetchrow_array();

			
	my ($sth) = &Do_SQL("SELECT ID_bills_expenses, Deductible, ID_bills,  Amount,  ID_accounts, ID_segments, ifnull(Related_ID_bills_expenses,0)Related FROM sl_bills_expenses WHERE ID_bills='$in{'view'}' AND ifnull(Related_ID_bills_expenses,0)=0 ORDER BY Date DESC");
	my $records = 0;
	while ($rec = $sth->fetchrow_hashref){

		$d = 1 - $d;
		$records++;
		$account_name = &load_name('sl_accounts','ID_accounts',$rec->{'ID_accounts'},'Name');
		$account = &load_db_names('sl_accounts','ID_accounts',$rec->{'ID_accounts'},'[ID_accounting]');
		$link_account = qq|<a href="/cgi-bin/mod/|.$usr{'application'}.qq|/dbman?cmd=fin_accounts&view=|.$rec->{'ID_accounts'}.qq|">|.&format_account($account).qq|</a> $account_name|;

		my ($rel_id_bills_expenses, $rel_amount, $rel_id_accounts);
		
		my ($sth_rel) = &Do_SQL("SELECT ID_bills_expenses,  Amount,  ifnull(ID_accounts,0)ID_accounts FROM sl_bills_expenses WHERE Related_ID_bills_expenses='$rec->{'ID_bills_expenses'}' LIMIT 1;");
		($rel_id_bills_expenses, $rel_amount, $rel_id_accounts) = $sth_rel->fetchrow_array;

		$account_rel_name = &load_name('sl_accounts','ID_accounts',$rel_id_accounts,'Name');
		$rel_account = &load_db_names('sl_accounts','ID_accounts',$rel_id_accounts,'[ID_accounting]') if ($rel_id_accounts);
		$link_rel_account = qq|<a href="/cgi-bin/mod/|.$usr{'application'}.qq|/dbman?cmd=fin_accounts&view=|.$rel_id_accounts.qq|">|.&format_account($rel_account).qq|</a> $account_rel_name|;
			
		$sum_amount += $rec->{'Amount'};
		$sum_tax += $rel_amount;

		$va{'lines_result'} .= qq|
			<tr>
				<td class="smalltext" >|;

		$va{'lines_result'} .= ( $no_lines > 0 and ( $in{'status'} eq 'New' or $special_perm )) 
								? qq|<a href="/cgi-bin/mod/|.$usr{'application'}.qq|/dbman?cmd=|.$in{'cmd'}.qq|&view=|.$in{'view'}.qq|&action=1&tab=2&delete_line=|.$rec->{'ID_bills_expenses'}.qq|"><img src="[va_imgurl]/[ur_pref_style]/b_drop.png" title="Drop" alt="" border="0"></a>|
								: '';

		$va{'lines_result'} .= qq|					
				</td>
				<td class="smalltext" >|.&load_name('sl_accounts_segments','ID_accounts_segments',$rec->{'ID_segments'},'Name').qq|</td>
				<td class="smalltext"  nowrap align="right"  style="border:0;border-left:1px solid silver;">|.&format_price($rec->{'Amount'}).qq|</td>
				<td class="smalltext"  nowrap>|.$link_account.qq|</td>
				<td class="smalltext"  nowrap align="right"  style="border:0;border-left:1px solid silver;">|.&format_price($rel_amount).qq|</td>
				<td class="smalltext"  nowrap>|.$link_rel_account.qq|</td>
				<td class="smalltext"  nowrap  style="border:0;border-left:1px solid silver;">|.$rec->{'Deductible'}.qq|</td>
			</tr>|;
	}

	if ($records == 0) {
		$va{'lines_result'} = qq|
			<tr>
				<td colspan='5' align='center'>|.&trans_txt('search_nomatches').qq|</td>
			</tr>\n|;
	}else{
		$va{'lines_result'} .= qq|<tr>
									<td colspan="2" style="border-top:1px solid silver;">&nbsp;</td>
									<td class="smalltext" nowrap align="right" style="border:0;border-top:1px solid silver;">Total: |.&format_price($sum_amount).qq|</td>
									<td style="border:0;border-top:1px solid silver;">&nbsp;</td>
									<td class="smalltext" nowrap align="right" style="border:0;border-top:1px solid silver;">Total: |.&format_price($sum_tax).qq|</td>
									<td colspan="2" style="border:0;border-top:1px solid silver;">&nbsp;</td>
								</tr>|;
	}
	
	#No tiene asignados PO´s
	$in{'type'} = &load_name("sl_bills","ID_bills",$in{'view'},"Type");
	if (&haspo eq "no"){

		$va{'disablea'} = qq| |;

	}else{		

		$va{'disablea'}	= qq| style="display:none;"|;
		$va{'tabvisible'} = ' style="display:none;"';		
		
		if ($in{'type'} ne "Deposit"){
			$va{'tab_messages'} = &trans_txt('pos_added');
		}else{
			$va{'tab_messages'} = &trans_txt('deposit_type');
		}

	}

	$va{'show_edit_amount'} = ($in{'status'} ne 'New' and !$special_perm ) ? "display:none;" : '';
	$va{'display_form'} = ($in{'status'} ne 'New' and !$special_perm) ? "display:none;" : '';
}

#############################################################################
#############################################################################
#	Function: load_tabs3
#
#       Es: Muestra los pagos 
#       En: English description if possible
#
#
#	Created on: 05/02/2013  17:32:10
#
#	Author: Enrique Peña
#
#	Modifications: Alejandro Diaz::03/04/2013
#
#	Parameters:
#
#	Returns:
#
#	See Also:
#
#
#
sub load_tabs3{
#############################################################################
#############################################################################
	$in{'type'} = &load_name("sl_bills","ID_bills",$in{'view'},"Type") if (!$in{'type'});
	$in{'status'} = &load_name("sl_bills","ID_bills",$in{'view'},"Status") if (!$in{'status'});
	
	if ($in{'type'} ne 'Bill' ) {
		$va{'tab_messages'} = &trans_txt('bills_tab_info_for_bills');
	}

	# Muestra los depositos creditos aplicados a este bill
	my (@c) = split(/,/,$cfg{'srcolors'});
	$in{'id_vendors'} = &load_name("sl_bills","ID_bills",$in{'id_bills'},"ID_vendors");

	my ($sth) = &Do_SQL("SELECT COUNT(*) FROM sl_bills INNER JOIN sl_bills_applies USING(ID_bills) WHERE sl_bills_applies.ID_bills_applied='$in{'id_bills'}' AND sl_bills.Type IN ('Deposit','Credit') AND sl_bills.ID_vendors = '$in{'id_vendors'}' ;");
	# AND sl_bills.Status NOT IN ('Void','Paid')
	$va{'matches'} = $sth->fetchrow;
	if ($va{'matches'}>0){
		(!$in{'nh'}) and ($in{'nh'}=1);
		$first = ($in{'nh'} - 1) * $usr{'pref_maxh'};			
		($va{'pageslist'},$qs) = &pages_list($in{'nh'},"/cgi-bin/mod/$usr{'application'}/dbman",$va{'matches'},$usr{'pref_maxh'});
					
		my ($sth) = &Do_SQL("SELECT ID_bills, sl_bills.Amount, Type, ID_vendors as idvendor
		, (SELECT Amount FROM sl_bills WHERE ID_bills = sl_bills_applies.ID_bills) as AmountBill
		, sl_bills_applies.Amount as AmountSpent, sl_bills_applies.Date, sl_bills_applies.Time
		FROM sl_bills INNER JOIN sl_bills_applies USING(ID_bills)
		WHERE sl_bills_applies.ID_bills_applied='$in{'id_bills'}'
		AND sl_bills.Type IN ('Deposit','Credit')
		AND sl_bills.ID_vendors = '$in{'id_vendors'}'
		AND sl_bills.ID_bills NOT IN ('$in{'id_bills'}')
		ORDER BY sl_bills_applies.Date DESC LIMIT $first,$usr{'pref_maxh'};");
		# AND sl_bills.Status NOT IN ('Void','Paid')
		$va{'total_depcred'} = 0;
		while ($rec = $sth->fetchrow_hashref){
			$d = 1 - $d;
			$va{'vendors'} = &load_db_names('sl_vendors','ID_vendors',$rec->{'ID_vendors'},'([ID_vendors]) [CompanyName]');
			my $remaining = $rec->{'Amount'}-$rec->{'AmountSpent'};
			$va{'total_depcred'} += $rec->{'AmountSpent'};

			$va{'searchresults'} .= "<tr bgcolor='$c[$d]'>\n";
			$va{'searchresults'} .= "  <td class='smalltext'><a href=\"/cgi-bin/mod/$usr{'application'}/dbman?cmd=$in{'cmd'}&view=$rec->{'ID_bills'}\">$rec->{'ID_bills'}</a></td>\n";
			$va{'searchresults'} .= "  <td class='smalltext'>".$rec->{'Date'}." ".$rec->{'Time'}."</td>\n";
			$va{'searchresults'} .= "  <td class='smalltext'>$rec->{'Type'}</td>\n";
			$va{'searchresults'} .= "  <td class='smalltext' align='right'>".&format_price($rec->{'AmountBill'})."</td>\n";
			$va{'searchresults'} .= "  <td class='smalltext' align='right'>".&format_price($rec->{'AmountSpent'})."</td>\n";
			$va{'searchresults'} .= "</tr>\n";
		}
		if ($va{'total_depcred'} > 0) {
			$va{'searchresults'} .= "<tr bgcolor='$c[$d]'>\n";
			$va{'searchresults'} .= "  <td class='smalltext' colspan='4' align='right'>Total</td>\n";
			$va{'searchresults'} .= "  <td class='smalltext' align='right'>".&format_price($va{'total_depcred'})."</td>\n";
			$va{'searchresults'} .= "</tr>\n";
		}
		# $va{'total_depcred'} = &format_price($va{'total_depcred'});
	}else{
		$va{'pageslist'} = 1;
		$va{'searchresults'} = qq|
			<tr>
				<td colspan='5' align='center'>|.&trans_txt('search_nomatches').qq|</td>
			</tr>\n|;
	}
}

#############################################################################
#############################################################################
#	Function: load_tabs5
#
#       Es: Muestra el listado de todos los Movimientos Bancarios Aplicados a un Bill
#
#	Created on: 12/04/2013 
#
#	Author: Alejandro Diaz
#
#	Modifications: Alejandro Diaz
#
#	Parameters:
#
#	Returns:
#
#	See Also:
#
#
#
sub load_tabs5 {
#############################################################################
#############################################################################
	my ($totcols);
	# TAB Balance
	$in{'type'} = &load_name("sl_bills","ID_bills",$in{'view'},"Type") if (!$in{'type'});
	$in{'status'} = &load_name("sl_bills","ID_bills",$in{'view'},"Status") if (!$in{'status'});
	$in{'amount'} = &load_name("sl_bills","ID_bills",$in{'view'},"Amount") if (!$in{'amount'});

	my ($sth) = &Do_SQL("SELECT CompanyName, Currency, ID_vendors FROM sl_vendors WHERE ID_vendors = (SELECT ID_vendors FROM sl_bills WHERE ID_bills =$in{'view'} )");
	($va{'vendor_name'},$va{'vendor_currency'},$va{'id_vendors'}) = $sth->fetchrow_array();

	$va{'vendors'} = "($va{'id_vendors'}) $va{'vendor_name'}";
	
	## Load Vendor Info & Currency Info
	if ($va{'vendor_currency'} ne $cfg{'acc_default_currency'} and $cfg{'acc_default_currency'}){
		## Other Currency
		$va{'tab_headers'} = "<tr><td class='menu_bar_title'>".&trans_txt('mer_bills_htab5')."</td></tr>\n";
 		$va{'tab_headers'} =~ s/,/<\/td><td class='menu_bar_title'>/g;
 		$totcols = 10;
	}else{
		## Same Currency
		$va{'tab_headers'} = "<tr><td class='menu_bar_title'>".&trans_txt('mer_bills_htab5b')."</td></tr>\n";
 		$va{'tab_headers'} =~ s/,/<\/td><td class='menu_bar_title'>/g;
 		$totcols = 8;
	}

	# Muestra los depositos creditos aplicados a este bill
	my (@c) = split(/,/,$cfg{'srcolors'});
	my ($sth) = &Do_SQL("SELECT COUNT(*) FROM sl_banks_movrel INNER JOIN sl_banks_movements USING(ID_banks_movements) WHERE tablename='bills' AND tableid='".&filter_values($in{'view'})."';");

	$va{'matches'} = $sth->fetchrow;
	if ($va{'matches'}>0){
		(!$in{'nh'}) and ($in{'nh'}=1);
		$first = ($in{'nh'} - 1) * $usr{'pref_maxh'};			
		($va{'pageslist'},$qs) = &pages_list($in{'nh'},"/cgi-bin/mod/$usr{'application'}/dbman",$va{'matches'},$usr{'pref_maxh'});
					
		my ($sth) = &Do_SQL("SELECT ID_banks_movements, currency_exchange, BankDate, ConsDate, Amount, AmountPaid, if ((length(RefNumCustom)=0 or RefNumCustom is null ),RefNum,RefNumCustom)RefNum, Memo, sl_banks.BankName, sl_banks.SubAccountOf ,sl_banks.Currency,ID_banks,Type,AmountCurrency
		FROM sl_banks_movrel INNER JOIN sl_banks_movements USING(ID_banks_movements) INNER JOIN sl_banks USING(ID_banks)
		WHERE tablename='bills' 
		AND tableid=".&filter_values($in{'view'})."
		ORDER BY sl_banks_movements.Date,sl_banks_movements.Time LIMIT $first,$usr{'pref_maxh'};");
		$va{'total'} = 0;
		$va{'total_oc'} = 0;
		while ($rec = $sth->fetchrow_hashref){
			$d = 1 - $d;
			
			$amount_exchange = $rec->{'AmountPaid'} if ($va{'vendor_currency'} ne $cfg{'acc_default_currency'} and $cfg{'acc_default_currency'});
			if ($rec->{'Type'} eq 'Credit'){
				$va{'total'} += $rec->{'AmountPaid'};
				if ($rec->{'currency_exchange'} and $rec->{'currency_exchange'} > 0) {
					$va{'total_oc'} += $amount_exchange;
				}
			}elsif ($rec->{'Type'} eq 'Debit'){
				$va{'total'} -= $rec->{'AmountPaid'};
				if ($rec->{'currency_exchange'} and $rec->{'currency_exchange'} > 0) {
					$va{'total_oc'} -= $amount_exchange;
				}
			}
			
			$va{'searchresults'} .= "<tr bgcolor='$c[$d]'>\n";

			## Partial cancellation payments
			my ($sth) = &Do_SQL("SELECT count(*) FROM sl_banks_movements_notes WHERE Type='Cancel' AND ID_banks_movements='$rec->{'ID_banks_movements'}';");
			my ($already_canceled)= $sth->fetchrow_array();

			if ($rec->{'Type'} eq 'Credit' and !$already_canceled and $rec->{'AmountPaid'}>0 and &check_permissions('mer_bills_partial_cancellation_payments','','')){
				$va{'searchresults'} .= qq|  <td class='smalltext'>
					<a href="/cgi-bin/mod/$usr{'application'}/dbman?cmd=$in{'cmd'}&view=$in{'view'}&tab=5&cancel_payment=$rec->{'ID_banks_movements'}" onclick="return Confirm_to_continue()"><img src='$va{'imgurl'}/$usr{'pref_style'}/b_drop.png' title='Drop' alt='' border='0'></a>
				</td>\n|;
			}else{
				$va{'searchresults'} .= "  <td class='smalltext'>&nbsp;</td>\n";
			}
			$va{'searchresults'} .= "  <td class='smalltext'><a href=\"/cgi-bin/mod/$usr{'application'}/dbman?cmd=fin_banks_movements&view=$rec->{'ID_banks_movements'}\">$rec->{'ID_banks_movements'}</a></td>\n";
			$va{'searchresults'} .= "  <td class='smalltext'>".$rec->{'BankName'}."</td>\n";
			$va{'searchresults'} .= "  <td class='smalltext'>".$rec->{'SubAccountOf'}."</td>\n";
			$va{'searchresults'} .= "  <td class='smalltext'>".$rec->{'BankDate'}."</td>\n";
			$va{'searchresults'} .= "  <td class='smalltext'>".$rec->{'RefNum'}."</td>\n";
			$va{'searchresults'} .= "  <td class='smalltext'>".$rec->{'Memo'}."</td>\n";
			$va{'searchresults'} .= "  <td class='smalltext'>".$rec->{'Type'}."</td>\n";
			if ($va{'vendor_currency'} ne $cfg{'acc_default_currency'} and $cfg{'acc_default_currency'}){
				$va{'searchresults'} .= "  <td class='smalltext' align='right'>".&format_price($amount_exchange)."</td>\n";
				$va{'searchresults'} .= "  <td class='smalltext' align='right'>".($rec->{'currency_exchange'})."</td>\n";
				$va{'searchresults'} .= "  <td class='smalltext' align='right'>".$cfg{'acc_default_currency'}.' '.&format_price($rec->{'Amount'})."</td>\n";
			}else{
				$va{'searchresults'} .= "  <td class='smalltext' align='right'>".&format_price($rec->{'Amount'})."</td>\n";
			}
			
			$va{'searchresults'} .= "</tr>\n";
		}
		if ($va{'total'} > 0) {
			$va{'searchresults'} .= "<tr bgcolor='$c[$d]'>\n";
			$va{'searchresults'} .= "  <td class='smalltext' colspan='".($totcols-1)."' align='right'>Total</td>\n";
			if ($va{'vendor_currency'} ne $cfg{'acc_default_currency'} and $cfg{'acc_default_currency'}){
				$va{'searchresults'} .= "  <td class='smalltext' align='right'>".$cfg{'acc_default_currency'}.' '.&format_price($va{'total'})."</td>\n";
			}else{
				$va{'searchresults'} .= "  <td class='smalltext' align='right'>".&format_price($va{'total'})."</td>\n";
			}
			$va{'searchresults'} .= "</tr>\n";
		}

	}else{
		$va{'pageslist'} = 1;
		$va{'searchresults'} = qq|
			<tr>
				<td colspan='$totcols' align='center'>|.&trans_txt('search_nomatches').qq|</td>
			</tr>\n|;
	}
}

#############################################################################
#############################################################################
#	Function: load_tabs8
#
#       Es: Genera el listado de los gastos de aterrizajes si fuera el caso
#
#	Created on: 12/04/2013 
#
#	Author: Alejandro Diaz
#
#	Modifications: Gilberto Quirino
#
#	Parameters:
#
#	Returns:
#
#	See Also:
#
#
#
sub load_tabs8 {
#############################################################################
#############################################################################
	$in{'type'} = &load_name("sl_bills","ID_bills",$in{'view'},"Type") if (!$in{'type'});
	$in{'status'} = &load_name("sl_bills","ID_bills",$in{'view'},"Status") if (!$in{'status'});
	$in{'amount'} = &load_name("sl_bills","ID_bills",$in{'view'},"Amount") if (!$in{'amount'});
	$in{'id_vendors'} = &load_name("sl_bills","ID_bills",$in{'id_bills'},"ID_vendors");
	delete($in{'add'});

	my ($bill_amount_remaining) = &bills_amount_due($in{'view'});
	$va{'messages'} = '';
	
	if ($in{'type'} !~ /Bill|Credit/ ) {

		$va{'tab_messages'} = &trans_txt('This info is only for Bills');
		$va{'tabvisible'} = ' style="display:none;"';

	}else {		

		###
 		### Búqueda por PO
 		###
 		my $sql_search = '';
 		if( $in{'id_purchaseorders'} ){
 			$sql_search = " AND sl_purchaseorders_adj.ID_purchaseorders = ".$in{'id_purchaseorders'}." ";
 			$va{'tab_messages'} = '';
 		}

		if ($in{'status'} ne 'New') {
			## Si este bill esta pagado solo mostramos los datos del PO al que se aplico
			
			my (@c) = split(/,/,$cfg{'srcolors'});
			my ($sth) = &Do_SQL("SELECT count(*) 
								FROM sl_bills 
									INNER JOIN sl_bills_pos USING(ID_bills)  
									INNER JOIN sl_purchaseorders_adj ON sl_bills_pos.ID_purchaseorders_adj = sl_purchaseorders_adj.ID_purchaseorders_adj 
								WHERE 1 AND ID_bills='$in{'id_bills'}';");
			$va{'matches'} = $sth->fetchrow;

			if ($va{'matches'}>0){

				(!$in{'nh'}) and ($in{'nh'}=1);
				$first = ($in{'nh'} - 1) * $usr{'pref_maxh'};			
				($va{'pageslist'},$qs) = &pages_list($in{'nh'},"/cgi-bin/mod/$usr{'application'}/dbman",$va{'matches'},$usr{'pref_maxh'});
				
				# Se obtiene el currency del proveedor
				my $vendor_currency = &load_db_names('sl_vendors','ID_vendors',$in{'id_vendors'},'[Currency]');

				my ($total_po,$total_due,$total_billed,$total_amount);
				## Necesitamos conocer la deuda de acuerdo a lo Recibido
				my ($sth) = &Do_SQL("SELECT 		
										sl_purchaseorders_adj.ID_purchaseorders,								
										sl_purchaseorders_adj.ID_wreceipts,
										sl_purchaseorders_adj.ID_purchaseorders_adj,
										sl_purchaseorders_adj.Type AS Description,
										sl_purchaseorders_adj.Date,										
										sl_purchaseorders_adj.Total,
										sl_purchaseorders_adj.Amount_original,
										sl_purchaseorders_adj.TotalOriginal,
										sl_purchaseorders_adj.Status,
										sl_bills_pos.Amount,
										sl_purchaseorders_adj.Tax, 
										IFNULL((SELECT SUM(sl_bills_pos.Amount) 
												FROM sl_bills 
													INNER JOIN sl_bills_pos USING(ID_bills) 
												WHERE ID_purchaseorders_adj = sl_purchaseorders_adj.ID_purchaseorders_adj 
													AND sl_bills.Status = 'Paid')
											, 0) AS TotalPaid,
										IFNULL((SELECT SUM(sl_bills_pos.Amount) 
												FROM sl_bills 
													INNER JOIN sl_bills_pos USING(ID_bills) 
												WHERE ID_purchaseorders_adj = sl_purchaseorders_adj.ID_purchaseorders_adj 
													AND sl_bills.Status <> 'Void')
											, 0) AS TotalInBills
									FROM sl_bills 
										INNER JOIN sl_bills_pos USING(ID_bills) 
										INNER JOIN sl_purchaseorders_adj ON sl_bills_pos.ID_purchaseorders_adj = sl_purchaseorders_adj.ID_purchaseorders_adj  
									WHERE 1 AND ID_bills=$in{'id_bills'} 
									ORDER BY										
										sl_purchaseorders_adj.ID_wreceipts DESC,
										sl_purchaseorders_adj.Type,
										sl_purchaseorders_adj.ID_purchaseorders_adj
									LIMIT $first,$usr{'pref_maxh'};");
				
				while ($rec = $sth->fetchrow_hashref){
					$d = 1 - $d;

					# monto total del PO.
					if( $vendor_currency eq 'MX$' ){
						if( $rec->{'TotalOriginal'} > 0 ){
							$in{'amount_po'} = $rec->{'TotalOriginal'};
						}else{#if( $rec->{'Status'} eq "Active" ){
							$in{'amount_po'} = $rec->{'Amount_original'};
						}
					}else{
						$in{'amount_po'} = $rec->{'Total'};
					}

					### Se hace la conversion del Tax
					# if( $rec->{'Tax'} > 0 ){
					# 	my $sth = &Do_SQL("SELECT sl_exchangerates.exchange_rate
					# 						FROM sl_wreceipts
					# 							INNER JOIN sl_exchangerates USING(ID_exchangerates)
					# 						WHERE sl_wreceipts.ID_wreceipts=".$rec->{'ID_wreceipts'}." 
					# 							AND sl_wreceipts.ID_exchangerates > 0;");
					# 	my($exchange_rate) = $sth->fetchrow();
					# 	$exchange_rate = 1 if( !exchange_rate );
					# 	$rec->{'Tax'} *= $exchange_rate;
					# }

					# monto total pagado
					$in{'amount_billsp'} = ($rec->{'TotalPaid'} > 0) ? round($rec->{'TotalPaid'},2) : 0;
					$in{'amount_billsa'} = ($rec->{'TotalInBills'} > 0) ? round($rec->{'TotalInBills'},2) : 0;

					# Monto total del PO - El monto que se ha pagado
					# Nota. Se debe dejar de usar este y $in{'amount_billsp'}?
					#$va{'total_due2'} = ($in{'amount_po'} - $in{'amount_billsp'});

					# Monto total del PO - El monto que hay en bills activos
					$va{'total_due'} = ($in{'amount_po'} - $in{'amount_billsa'});

					my $po_blocked_bybill = $va{'total_due'} > 0 ? 0 : 1;

					$total_po += $in{'amount_po'};
					$total_paid += $rec->{'TotalPaid'};
					$total_due += $va{'total_due'};
					$total_billed += $rec->{'TotalInBills'};
					$total_amount += $rec->{'Amount'};

					my $amount_due = ($rec->{'Total'}-$rec->{'Amount'});
					$va{'searchresults'} .= "<tr bgcolor='$c[$d]' onmouseover='m_over(this)' onmouseout='m_out(this)'>\n";
					$va{'searchresults'} .= "   <td class='smalltext'></td>\n";
					$va{'searchresults'} .= "   <td class='smalltext'><a href='/cgi-bin/mod/$usr{'application'}/dbman?cmd=mer_po&view=$rec->{'ID_purchaseorders'}'>$rec->{'ID_purchaseorders'}</a></td>\n";
					$va{'searchresults'} .= "   <td class='smalltext'>$rec->{'ID_wreceipts'}</td>\n";
					$va{'searchresults'} .= "   <td class='smalltext'>$rec->{'ID_purchaseorders_adj'}</td>\n";
					$va{'searchresults'} .= "   <td class='smalltext'>".$rec->{'Date'}."</td>\n";
					$va{'searchresults'} .= "   <td class='smalltext'>".$rec->{'Description'}."</td>\n";
					$va{'searchresults'} .= "   <td class='smalltext' align='right'>".&format_price($in{'amount_po'})."</td>\n";
					#$va{'searchresults'} .= "   <td class='smalltext' align='right'>".&format_price($rec->{'Tax'})."</td>\n";
					$va{'searchresults'} .= "   <td class='smalltext' align='right'>".&format_price($rec->{'TotalPaid'})."</td>\n";
					$va{'searchresults'} .= "   <td class='smalltext' align='right'>".&format_price($va{'total_due'})."</td>\n";
					$va{'searchresults'} .= "   <td class='smalltext' align='right'>".&format_price($rec->{'TotalInBills'})."</td>\n";
					$va{'searchresults'} .= "   <td class='smalltext' align='right'>".&format_price($rec->{'Amount'})."</td>\n";
					$va{'searchresults'} .= "</tr>\n";
				}

				$va{'searchresults'} .= "<tr>\n";
				$va{'searchresults'} .= "   <td colspan='6' class='smalltext' align='right'>Total</td>\n";
				$va{'searchresults'} .= "   <td class='smalltext' align='right'>".&format_price($total_po)."</td>\n";
				$va{'searchresults'} .= "   <td class='smalltext' align='right'>".&format_price($total_paid)."</td>\n";
				$va{'searchresults'} .= "   <td class='smalltext' align='right'>".&format_price($total_due)."</td>\n";
				$va{'searchresults'} .= "   <td class='smalltext' align='right'>".&format_price($total_billed)."</td>\n";
				$va{'searchresults'} .= "   <td class='smalltext' align='right'>".&format_price($total_amount)."</td>\n";
				$va{'searchresults'} .= "</tr>\n";
			}else{
				$va{'matches'} =0;
				$va{'pageslist'} = 1;
				$va{'searchresults'} = qq|
					<tr>
						<td colspan='7' align='center'>|.&trans_txt('search_nomatches').qq|</td>
					</tr>\n|;
			}

		}else {

			$in{'addpo'} = int ($in{'addpo'});
			$in{'delbillpos'} = int ($in{'delbillpos'});
			
			my ($sth) = &Do_SQL("SELECT Amount FROM sl_bills_pos WHERE ID_bills='$in{'id_bills'}' AND ID_purchaseorders=$in{'delbillpos'}");
			($va{'amount'}) = $sth->fetchrow_array();	

			my ($sth) = &Do_SQL("SELECT Type, ID_vendors, Status, Amount FROM sl_bills WHERE ID_bills='$in{'id_bills'}'");
			($in{'type'}, $in{'id_vendors'}, $in{'status'}, $va{'amount'}) = $sth->fetchrow_array();

			my (@c) = split(/,/,$cfg{'srcolors'});
			my ($d,$query);
						
			my ($sth2) = &Do_SQL("SELECT COUNT(*) FROM sl_bills INNER JOIN sl_bills_pos USING(ID_bills) WHERE ID_bills = '$in{'id_bills'}'");
			($va{'total_pos'}) = $sth2->fetchrow_array();
			
			#($in{'type'} eq 'Credit') ? ($query = "Return to Vendor"):($query = "Purchase Order");
			my $where = "";
			if( ($in{'type'} eq 'Credit') ){
				$sth_po = &Do_SQL("SELECT ID_purchaseorders 
									FROM sl_bills_pos  
									WHERE ID_bills='$in{'id_bills'}';");
				my $id_po_rvendor = $sth_po->fetchrow();
				$where = "AND sl_purchaseorders.ID_purchaseorders='$id_po_rvendor'";
			}else{				
				$where = "AND sl_purchaseorders.Status NOT IN('Cancelled','Paid')
				 		  AND sl_purchaseorders.Auth = 'Approved'
				 		  AND sl_purchaseorders_adj.ID_vendors = '$in{'id_vendors'}'				 		  
				 		  AND sl_purchaseorders_adj.`Status` <> 'Inactive'
				 		  AND sl_purchaseorders_adj.Paid = 0 
				 		  /*AND sl_purchaseorders_adj.InCOGS = 'Yes'*/
						  AND (SELECT ifnull(SUM(Received),0)as Received FROM sl_purchaseorders_items WHERE ID_purchaseorders =sl_purchaseorders.ID_purchaseorders) > 0";
			}

			### Valida que no sea PO de Servicios
			my $sth_po = &Do_SQL("SELECT sl_bills_pos.ID_purchaseorders FROM sl_bills_pos WHERE ID_bills = ".$in{'id_bills'}.";");
			my $id_po = $sth_po->fetchrow();
			
			#if ($va{'total_pos'} > 0 and $va{'amount'} or $va{'amount'} eq "0.00"){
			if( !$id_po or $id_po == 0 ){
				
				my ($sth) = &Do_SQL("SELECT COUNT(*) 
									FROM sl_purchaseorders 
										/*LEFT JOIN sl_bills_pos USING(ID_purchaseorders)*/ 
										INNER JOIN sl_purchaseorders_adj USING(ID_purchaseorders)  
									WHERE 1 
										".$where."
 										".$sql_search."
									;");
				$va{'matches'} = $sth->fetchrow;
				
				if ($va{'matches'} > 0){
					(!$in{'nh'}) and ($in{'nh'}=1);
					$first = ($in{'nh'} - 1) * $usr{'pref_maxh'};			
					($va{'pageslist'},$qs) = &pages_list($in{'nh'},"/cgi-bin/mod/$usr{'application'}/dbman",$va{'matches'},$usr{'pref_maxh'});
					
					# Se obtiene el currency del proveedor
					my $vendor_currency = &load_db_names('sl_vendors','ID_vendors',$in{'id_vendors'},'[Currency]');

					my ($sth) = &Do_SQL("SELECT 
											sl_purchaseorders.ID_purchaseorders,
											sl_purchaseorders_adj.ID_wreceipts,
											sl_purchaseorders_adj.ID_purchaseorders_adj,
											sl_purchaseorders_adj.Type AS Description,
											sl_purchaseorders_adj.Date,
											sl_purchaseorders_adj.`Type`,
											sl_purchaseorders_adj.Total,
											sl_purchaseorders_adj.Amount_original,
											sl_purchaseorders_adj.TotalOriginal,
											sl_purchaseorders_adj.Status,
											sl_purchaseorders_adj.Tax,
											IFNULL((SELECT SUM(sl_bills_pos.Amount)
													FROM sl_bills  
														INNER JOIN sl_bills_pos USING(ID_bills) 
													WHERE ID_purchaseorders_adj = sl_purchaseorders_adj.ID_purchaseorders_adj 
														AND sl_bills.Status = 'Paid')
												, 0) AS TotalPaid,
											IFNULL((SELECT SUM(sl_bills_pos.Amount) 
													FROM sl_bills 
														INNER JOIN sl_bills_pos USING(ID_bills) 
													WHERE ID_purchaseorders_adj = sl_purchaseorders_adj.ID_purchaseorders_adj 
														AND sl_bills.Status <> 'Void')
												, 0) AS TotalInBills
										FROM sl_purchaseorders 
											INNER JOIN sl_purchaseorders_adj USING(ID_purchaseorders)
										WHERE 1 
											".$where."
 											".$sql_search."
										ORDER BY 
											sl_purchaseorders.ID_purchaseorders DESC, 
											sl_purchaseorders_adj.ID_wreceipts DESC,
											sl_purchaseorders_adj.Type,
											sl_purchaseorders_adj.ID_purchaseorders_adj
										LIMIT $first,$usr{'pref_maxh'};");
					while ($rec = $sth->fetchrow_hashref) {						

						# monto total del PO.
						if( $vendor_currency eq 'MX$' ){
							if( $rec->{'TotalOriginal'} and $rec->{'TotalOriginal'} ne '' and $rec->{'TotalOriginal'} > 0 ){
								$in{'amount_po'} = $rec->{'TotalOriginal'};
							}else{#elsif( $rec->{'Status'} eq "Active" ){
								$in{'amount_po'} = $rec->{'Amount_original'};
							}
						}else{
							$in{'amount_po'} = $rec->{'Total'};
						}
						
						### Se hace la conversion del Tax
						# if( $rec->{'Tax'} > 0 ){
						# 	my $sth = &Do_SQL("SELECT sl_exchangerates.exchange_rate
						# 						FROM sl_wreceipts
						# 							INNER JOIN sl_exchangerates USING(ID_exchangerates)
						# 						WHERE sl_wreceipts.ID_wreceipts=".$rec->{'ID_wreceipts'}." 
						# 							AND sl_wreceipts.ID_exchangerates > 0;");
						# 	my($exchange_rate) = $sth->fetchrow();
						# 	$exchange_rate = 1 if( !exchange_rate );
						# 	$rec->{'Tax'} *= $exchange_rate;
						# }

						# monto total pagado
						$in{'amount_billsp'} = $rec->{'TotalPaid'} > 0 ? round($rec->{'TotalPaid'},2) : 0;
						$in{'amount_billsa'} = $rec->{'TotalInBills'} > 0 ? round($rec->{'TotalInBills'},2) : 0;

						# Monto total del PO - El monto que se ha pagado
						# Nota. Se debe dejar de usar este y $in{'amount_billsp'}?
						#$va{'total_due2'} = ($in{'amount_po'} - $in{'amount_billsp'});

						# Monto total del PO - El monto que hay en bills activos
						$va{'total_due'} = ($in{'amount_po'} - $in{'amount_billsa'});

						my $po_line_style = $in{'amount_po'} > $va{'total_due'} ? '#00688B' : '#2f2f2f';
						

						my ($sth5) = &Do_SQL("SELECT sl_bills.ID_bills, sl_bills_pos.Amount, sl_bills_pos.ID_bills_pos FROM sl_bills INNER JOIN sl_bills_pos USING(ID_bills) WHERE ID_bills = '".$in{'id_bills'}."' AND ID_purchaseorders_adj = '".$rec->{'ID_purchaseorders_adj'}."' ");
						$rec5 = $sth5->fetchrow_hashref;

						##########
						########## Revisamos que el PO no este activo en otro Bill Pendiente de cerrarse
						##########
						#my ($sth6) = &Do_SQL("SELECT COUNT(ID_bills) FROM sl_bills INNER JOIN sl_bills_pos USING(ID_bills) WHERE ID_bills <> '".$in{'id_bills'}."' AND ID_purchaseorders = '".$rec->{'ID_purchaseorders'}."' AND Status NOT IN('Partly Paid','Paid','Void') ");
						#my ($po_blocked_bybill) = $sth6->fetchrow();
						my $po_blocked_bybill = $va{'total_due'} > 0 ? 0 : 1;

						$va{'searchresults2'} = "   <td class='smalltext' align='right'>".&format_price($rec->{'Amount'})."</td>\n";

						# El PO esta en este Bill, si ya se encuentra en otro no se deberia de mostrar
						if ($rec5->{'ID_bills'} eq $in{'id_bills'} and $in{'status'} ne "Paid" and $in{'status'} ne "Processed") {
							$va{'searchresults'} .= "   <td class='smalltext'><a href='/cgi-bin/mod/$usr{'application'}/dbman?cmd=mer_bills&view=".$in{'id_bills'}."&delpo=".$rec5->{'ID_bills_pos'}."&id_purchaseorders=".$in{'id_purchaseorders'}."&tab=8&adj=1&nh=$in{'nh'}'><img src='$va{'imgurl'}/$usr{'pref_style'}/b_drop.png' title='Drop' alt='' border='0'></a></td>\n";
							
							$va{'searchresults2'} = qq| <td class='smalltext' align='right' valign='top'>
															<span >|.&format_price($rec5->{'Amount'}).qq|</span> 
															<span >
																<a href="#tabs" onClick="popup_show('ajax_windows', 'ajax_drag', 'ajax_exit', 'element-right', -1, -1,'tabs');

																	loadDoc('/cgi-bin/common/apps/ajaxbuild?ajaxbuild=edit_bills_pos&id_bills=|.$rec5->{'ID_bills'}.qq|&id_bills_pos=|.$rec5->{'ID_bills_pos'}.qq|&id_po_adj=|.$rec->{'ID_purchaseorders_adj'}.qq|&id_purchaseorders=$in{'id_purchaseorders'}&amtdue=$va{'total_due'}&cmd=|.$in{'cmd'}.qq|&script_url=/cgi-bin/mod/|.$usr{'application'}.qq|/dbman&nh=$in{'nh'}');"><img src='$va{'imgurl'}/$usr{'pref_style'}/b_edit.png' title='Edit Amount' alt='' border='0'>

																</a>
															</span>
														</td>\n|;
						}elsif (!$po_blocked_bybill and $in{'status'} ne "Paid"  and $in{'status'} ne "Processed" and $va{'total_due'} > 0) {
							$va{'searchresults'} .= "   <td class='smalltext'>

															<a href='/cgi-bin/mod/$usr{'application'}/dbman?cmd=mer_bills&view=$in{'id_bills'}&addpo=$rec->{'ID_purchaseorders_adj'}&id_purchaseorders=$in{'id_purchaseorders'}&tab=8&adj=1&nh=$in{'nh'}'>
																<img src='$va{'imgurl'}/$usr{'pref_style'}/b_ok.png' title='Add' alt='' border='0'>
															</a>
														</td>\n";
						}else {
							$va{'searchresults'} .= "   <td class='smalltext'>---</td>\n";
						}
						
						$va{'searchresults'} .= "   <td class='smalltext'><a href='/cgi-bin/mod/$usr{'application'}/dbman?cmd=mer_po&view=$rec->{'ID_purchaseorders'}'>$rec->{'ID_purchaseorders'}</a></td>\n";
						$va{'searchresults'} .= "   <td class='smalltext'>$rec->{'ID_wreceipts'}</td>\n";
						$va{'searchresults'} .= "   <td class='smalltext'>$rec->{'ID_purchaseorders_adj'}</td>\n";
						$va{'searchresults'} .= "   <td class='smalltext'>$rec->{'Date'}</td>\n";
						$va{'searchresults'} .= "   <td class='smalltext'>$rec->{'Description'}</td>\n";				
						$va{'searchresults'} .= "   <td class='smalltext' align='right' style='color:$po_line_style'>".&format_price($in{'amount_po'})."</td>\n";
						#$va{'searchresults'} .= "   <td class='smalltext' align='right' style='color:$po_line_style'>".&format_price($rec->{'Tax'})."</td>\n";
						$va{'searchresults'} .= "   <td class='smalltext' align='right' style='color:$po_line_style'>".&format_price($in{'amount_billsp'})."</td>\n";
						$va{'searchresults'} .= "   <td class='smalltext' align='right' style='color:$po_line_style'>".&format_price($va{'total_due'})."</td>\n";
						$va{'searchresults'} .= "   <td class='smalltext' align='right' style='color:$po_line_style'>".&format_price($rec->{'TotalInBills'})."</td>\n";
						$va{'searchresults'} .= $va{'searchresults2'};
						$va{'searchresults'} .= "</tr>\n";				
					}
				}else{
					$va{'matches'} =0;
					$va{'pageslist'} = 1;
					$va{'searchresults'} = qq|
						<tr>
							<td colspan='7' align='center'>|.&trans_txt('search_nomatches').qq|</td>
						</tr>\n|;
				}

			}else{
				$va{'matches'} =0;
				$va{'pageslist'} = 1;
				$va{'searchresults'} = qq|
					<tr>
						<td colspan='7' align='center'>|.&trans_txt('search_nomatches').qq|</td>
					</tr>\n|;
			}

		}
	}
}

#############################################################################
#############################################################################
#	Function: load_tabs9
#
#       Es: Genera el listado de las OC de Servicio
#
#	Created on: 12/06/2016
#
#	Author: Gilberto Quirino
#
#	Modifications: 
#
#	Parameters:
#
#	Returns:
#
#	See Also:
#
#
#
sub load_tabs9 {
#############################################################################
#############################################################################
	
	my $id_bills = $in{'view'};
	$in{'type'} = &load_name("sl_bills","ID_bills",$id_bills,"Type") if (!$in{'type'});
	$in{'status'} = &load_name("sl_bills","ID_bills",$id_bills,"Status") if (!$in{'status'});
	$in{'amount'} = &load_name("sl_bills","ID_bills",$id_bills,"Amount") if (!$in{'amount'});
	$in{'id_vendors'} = &load_name("sl_bills","ID_bills",$id_bills,"ID_vendors") if (!$in{'id_vendors'});

	# if( $in{'status'} eq 'New' or $in{'status'} eq 'Processed' ){

		my $sql = "SELECT *
						, IFNULL((SELECT SUM(Total) FROM sl_purchaseorders_items WHERE ID_purchaseorders = sl_purchaseorders.ID_purchaseorders), 0) AS TotalPO
						, IFNULL((SELECT SUM(sl_bills_pos.Amount) FROM sl_bills INNER JOIN sl_bills_pos USING(ID_bills) WHERE ID_purchaseorders = sl_purchaseorders.ID_purchaseorders AND sl_bills.Status = 'Paid'), 0) AS TotalPaid
						, IFNULL((SELECT SUM(sl_bills_pos.Amount) FROM sl_bills INNER JOIN sl_bills_pos USING(ID_bills) WHERE ID_purchaseorders = sl_purchaseorders.ID_purchaseorders AND sl_bills.Status <> 'Void'), 0) AS TotalInBills
					FROM sl_purchaseorders
						INNER JOIN sl_bills_pos ON sl_purchaseorders.ID_purchaseorders = sl_bills_pos.ID_purchaseorders
					WHERE sl_bills_pos.ID_bills = ".$id_bills.";";
		my $sth = &Do_SQL($sql);

		while( my $po = $sth->fetchrow_hashref() ){

			my $amount_due = ($po->{'TotalPO'} - $po->{'TotalPaid'});

			$va{'searchresults'} .= '<tr>';
			$va{'searchresults'} .= '	<td><a href="/cgi-bin/mod/[ur_application]/dbman?cmd=mer_po&view='.$po->{'ID_purchaseorders'}.'">'.$po->{'ID_purchaseorders'}.'</a></td>';
			$va{'searchresults'} .= '	<td>'.$po->{'PODate'}.'</td>';
			$va{'searchresults'} .= '	<td>'.$po->{'POTerms'}.'</td>';
			$va{'searchresults'} .= '	<td style="text-align: right;">'.&format_price($po->{'TotalPO'}).'</td>';
			$va{'searchresults'} .= '	<td style="text-align: right;">'.&format_price($po->{'TotalInBills'}).'</td>';
			$va{'searchresults'} .= '	<td style="text-align: right;">'.&format_price($po->{'TotalPaid'}).'</td>';
			$va{'searchresults'} .= '	<td style="text-align: right;">'.&format_price($amount_due).'</td>';
			$va{'searchresults'} .= '	<td style="text-align: right;">'.&format_price($po->{'TotalInBills'}).'</td>';	
			$va{'searchresults'} .= '</tr>';

			### PO Items
			my $sql_items = "SELECT sl_purchaseorders_items.*, sl_services.Name
							FROM sl_purchaseorders_items
								INNER JOIN sl_services ON RIGHT(sl_purchaseorders_items.ID_products, 4) = sl_services.ID_services
							WHERE sl_purchaseorders_items.ID_purchaseorders = ".$po->{'ID_purchaseorders'}.";";
			my $sth_items = &Do_SQL($sql_items);
			$va{'searchresults'} .= '<tr>';
			$va{'searchresults'} .= '	<td>&nbsp;</td>';
			$va{'searchresults'} .= '	<td colspan="7">';
			$va{'searchresults'} .= '	<table class="formtable" style="border-collapse: collapse; width: 100%;">';
			$va{'searchresults'} .= '	<tr>
											<td class="menu_bar_title">Item ID</td>
											<td class="menu_bar_title">Description</td>
											<td class="menu_bar_title" align="right">Qty</td>
											<td class="menu_bar_title" align="right">Unit Price</td>						
											<td class="menu_bar_title" align="right">STotal</td>
											<td class="menu_bar_title" align="right">Tax(%)</td>
											<td class="menu_bar_title" align="right">Tax($)</td>
											<td class="menu_bar_title" align="right">Tax Hold.($)</td>
											<td class="menu_bar_title" align="right">Other Tax($)</td>
											<td class="menu_bar_title" align="right">Total</td>
										</tr>';
			while( my $po_item = $sth_items->fetchrow_hashref() ){
				$va{'searchresults'} .= '<tr>';
				$va{'searchresults'} .= '	<td>'.$po_item->{'ID_purchaseorders_items'}.'</td>';
				$va{'searchresults'} .= '	<td>'.$po_item->{'Name'}.'</td>';
				$va{'searchresults'} .= '	<td>'.$po_item->{'Qty'}.'</td>';
				$va{'searchresults'} .= '	<td style="text-align: right;">'.&format_price($po_item->{'Price'}).'</td>';
				$va{'searchresults'} .= '	<td style="text-align: right;">'.&format_price($po_item->{'Price'} * $po_item->{'Qty'}).'</td>';
				$va{'searchresults'} .= '	<td style="text-align: right;">'.&format_price($po_item->{'Tax_percent'}).'</td>';
				$va{'searchresults'} .= '	<td style="text-align: right;">'.&format_price($po_item->{'Tax'}).'</td>';	
				$va{'searchresults'} .= '	<td style="text-align: right;">'.&format_price($po_item->{'Tax_withholding'}).'</td>';	
				$va{'searchresults'} .= '	<td style="text-align: right;">'.&format_price($po_item->{'Tax_other'}).'</td>';	
				$va{'searchresults'} .= '	<td style="text-align: right;">';
				my $total = ( $po_item->{'Total_edited'} > 0 ) ? $po_item->{'Total_edited'} : $po_item->{'Total'};
				$va{'searchresults'} .= &format_price($total);
				if( $in{'status'} eq 'New' ){
					$va{'searchresults'} .= "<span>
												<a href=\"#tabs\" onClick=\"popup_show('ajax_windows', 'ajax_drag', 'ajax_exit', 'element-right', -1, -1, 'tabs');
													loadDoc('/cgi-bin/common/apps/ajaxbuild?ajaxbuild=edit_bills_pos&id_bills=".$in{'id_bills'}."&id_bills_pos=".$po->{'ID_bills_pos'}."&id_po_item=".$po_item->{'ID_purchaseorders_items'}."&id_po=".$po->{'ID_purchaseorders'}."&amtdue=".$total."&cmd=".$in{'cmd'}."&script_url=/cgi-bin/mod/".$usr{'application'}."/dbman');\">
													<img src=\"".$va{'imgurl'}."/".$usr{'pref_style'}."/b_edit.png\" title=\"Edit Amount\" alt=\"\" border=\"0\">
												</a>
											</span>";
				}
					#'<a href="#"><img src="'.$va{'imgurl'}.'/'.$usr{'pref_style'}.'/b_edit.png" title="Edit Amount" alt="" border="0"></a>' : '&nbsp;';
				
				$va{'searchresults'} .= '	</td>';
				$va{'searchresults'} .= '</tr>';
			}
			$va{'searchresults'} .= '	</table>';
			$va{'searchresults'} .= '	</td>';
			$va{'searchresults'} .= '</tr>';
			
		}

	# } else {

	# }

}

sub haspo{
	my $pos = "si";
	my ($sth) = &Do_SQL("SELECT COUNT(*) FROM sl_bills_pos WHERE ID_bills = '$in{'id_bills'}'");
	$va{'matches'} = $sth->fetchrow;
	$pos = "no"  if($va{'matches'}<1);
	return $pos;	
}

#############################################################################
#############################################################################
#   Function: bills_edition
#
#       Es: Valora un bill para ver si puede ser editado ono
#       En: 
#
#    Created on: 09/04/2013
#
#    Author: Alejandro Diaz
#
#    Modifications:
#
#
#   Parameters:
#
#  Returns:
#
#   See Also:
#
#
sub bills_edition {
#############################################################################
#############################################################################
	my ($id_bills, $type) = @_;

	my ($sth) = &Do_SQL("SELECT ifnull(Amount,0)Amount, ID_accounts, Status
		,(select count(*) from sl_banks_movrel where tablename='bills' and tableid=sl_bills.ID_bills)billsmovrel
		,(select count(*) from sl_bills_pos where ID_bills=sl_bills.ID_bills)billspos
		,(select count(*) from sl_bills_applies where ID_bills=sl_bills.ID_bills)apply
		,(select count(*) from sl_bills_applies where ID_bills_applied=sl_bills.ID_bills)applied
		FROM sl_bills WHERE ID_bills='$id_bills' ; ");
	my ($amount, $id_accounts, $status, $billsmovrel, $billspos, $apply, $applied) = $sth->fetchrow_array();

	if ($type eq 'Bill') {
		# Si tiene POs ** si ya fue aplicado un banks_movrel para este bill, NO se puede editar
		# Si tiene Expenses 
		# ** si tiene un Amount > 0 y ID_accounts > 0  y no tiene POS <---esto es un tab expense
		# ** si tiene un Amount == 0 y ID_accounts == 0  y tiene POS <---esto es un tab POs
		# ** si el bill tiene Amount y no tiene ID_accounts <----esto es un Bill POs

		# ** si es recien creado no tiene POS ni Amount ni ID_accounts, se puede editar<---esto es un tab expense and POs
		if ($billspos == 0 and $amount == 0 and $id_accounts == 0) {
			return 1;
		}else {
			# ** si tiene ya aplicados en bills_applies ID_bill, NO se puede editar
			if ($billsapplies > 0 or $apply > 0 or $billsmovrel > 0) {
				return 0;
			}else {
				return 1;
			}
		}
	}elsif ($type eq 'Debit' or $type eq 'Deposit' or $type eq 'Credit') {
		if ($type eq 'Deposit' or $type eq 'Debit') {
			if ($status eq 'Paid') {
				return 0;
			}
		}

		if ($apply > 0) {
			return 0;
		}else {
			return 1;
		}
	}else {
		return 1;
	}

}

1;