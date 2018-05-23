#########################################################
##		MERCHANDISING : BILLS
##########################################################

sub view_mer_bills {
# --------------------------------------------------------
	if ($in{'toprint'}){

       	# Movements
       	$va{'searchresults'} = '';
		$va{'searchresults_dc_print'} = '';
		$va{'searchresults_dc2_print'} = '';
		$va{'searchresults_po_print'} = '';
		$va{'mov_searchresults'} = '';
       	$va{'tab_type'}  = 'movs';
       	$va{'tab_title'} = &trans_txt('logs');
       	$va{'tab_table'} = 'sl_bills';
       	$va{'tab_idvalue'} = $in{'id_bills'};
       	$va{'mov_searchresults'} = &load_tabs_movs();
       	$va{'tab_idvalue'} = '';

   		## Si este bill esta pagado solo mostramos los datos del PO al que se aplico   		
		my ($sth) = &Do_SQL("SELECT count(*) FROM sl_bills INNER JOIN sl_bills_pos USING(ID_bills) INNER JOIN sl_purchaseorders USING(ID_purchaseorders)  WHERE 1 AND ID_bills='$in{'id_bills'}';");
		$va{'matches'} = $sth->fetchrow;

		## PO pagadas con este Bill
		if ($va{'matches'}>0){
			
			$va{'searchresults_po_print'} .= qq|
			<h3>POs Relacionados</h3>
			<table border="0" cellspacing="0" cellpadding="4" width="100%" class="formtable">
      			<tr>         	
					<td class="menu_bar_title" width="10%" align="center">OC</td>
					<td class="menu_bar_title" width="35%" align="center">Fecha</td>
					<td class="menu_bar_title" width="14%" align="center">Terminos</td>
					<td class="menu_bar_title" width="14%" align="center">Monto</td>
					<td class="menu_bar_title" width="15%" align="center">Monto Pendiente</td>
					<td class="menu_bar_title" width="22%" align="center">Monto Pagado</td>
			 	</tr>|;

			(!$in{'nh'}) and ($in{'nh'}=1);
			$first = ($in{'nh'} - 1) * $usr{'pref_maxh'};			
			($va{'pageslist'},$qs) = &pages_list($in{'nh'},"/cgi-bin/mod/$usr{'application'}/dbman",$va{'matches'},$usr{'pref_maxh'});
			
			my ($total_po,$total_due,$total_amount);
			## Necesitamos conocer la deuda de acuerdo a lo Recibido
			my ($sth) = &Do_SQL("SELECT sl_bills_pos.Amount, sl_purchaseorders.ID_purchaseorders, sl_purchaseorders.Date, sl_purchaseorders.POTerms
				, ifnull((SELECT SUM(Total) FROM sl_purchaseorders_items WHERE ID_purchaseorders = sl_purchaseorders.ID_purchaseorders),0)as Total
				, ifnull((SELECT SUM(sl_bills_pos.Amount) FROM sl_bills INNER JOIN sl_bills_pos USING(ID_bills) WHERE ID_purchaseorders = sl_purchaseorders.ID_purchaseorders AND sl_bills.Status = 'Paid'),0)as TotalPaid
				, ifnull((SELECT SUM(sl_bills_pos.Amount) FROM sl_bills INNER JOIN sl_bills_pos USING(ID_bills) WHERE ID_purchaseorders = sl_purchaseorders.ID_purchaseorders AND sl_bills.Status <> 'Void'),0)as TotalInBills
				, ifnull((SELECT SUM(Total) FROM sl_purchaseorders_adj WHERE ID_purchaseorders = sl_purchaseorders.ID_purchaseorders),0)as TotalAdj
				, ifnull((SELECT SUM(Received * Price *(1+Tax_percent)) FROM sl_purchaseorders_items WHERE ID_purchaseorders =sl_purchaseorders.ID_purchaseorders),0)as Total_Received							
				FROM sl_bills INNER JOIN sl_bills_pos USING(ID_bills) 
				INNER JOIN sl_purchaseorders USING(ID_purchaseorders) 
				WHERE 1 AND ID_bills='$in{'id_bills'} '
				ORDER BY sl_bills.Date DESC;");
			
			while ($rec = $sth->fetchrow_hashref){
				$d = 1 - $d;

				# monto total del PO.
				($in{'amount_po'}) = $rec->{'Total'};
				
				# monto total de adjustments.
				($in{'amount_po_adj'}) = $rec->{'TotalAdj'};
				
				# monto total del PO apliacando ajustes
				$in{'amount_po'} = $in{'amount_po'};# + $in{'amount_po_adj'};

				# monto total pagado
				$in{'amount_billsp'} = $rec->{'TotalPaid'} > 0 ? round($rec->{'TotalPaid'},2) : 0;
				$in{'amount_billsa'} = $rec->{'TotalInBills'} > 0 ? round($rec->{'TotalInBills'},2) : 0;

				# Monto total del PO - El monto que se ha pagado
				# Nota. Se debe dejar de usar este y $in{'amount_billsp'}?
				$va{'total_due2'} = ($in{'amount_po'} - $in{'amount_billsp'});

				# Monto total del PO - El monto que hay en bills activos
				$va{'total_due'} = ($in{'amount_po'} - $in{'amount_billsa'});

				my $po_blocked_bybill = $va{'total_due'} > 0 ? 0 : 1;

				$total_po += $rec->{'Total'};
				$total_due += $rec->{'Total_Received'};
				$total_amount += $rec->{'Amount'};

				my $amount_due = ($rec->{'Total'}-$rec->{'Amount'});
				$va{'searchresults_po_print'} .= "<tr bgcolor='$c[$d]' onmouseover='m_over(this)' onmouseout='m_out(this)'>\n";
				$va{'searchresults_po_print'} .= "   <td class='smalltext'>".$rec->{'ID_purchaseorders'}."</td>\n";
				$va{'searchresults_po_print'} .= "   <td class='smalltext'>".$rec->{'Date'}."</td>\n";
				$va{'searchresults_po_print'} .= "   <td class='smalltext'>".$rec->{'POTerms'}."</td>\n";
				$va{'searchresults_po_print'} .= "   <td class='smalltext' align='right'>".&format_price($rec->{'Total'})."</td>\n";
				$va{'searchresults_po_print'} .= "   <td class='smalltext' align='right'>".&format_price($rec->{'Total_Received'})."</td>\n";
				$va{'searchresults_po_print'} .= "   <td class='smalltext' align='right'>".&format_price($rec->{'Amount'})."</td>\n";
				$va{'searchresults_po_print'} .= "</tr>\n";
			}

			$va{'searchresults_po_print'} .= "<tr>\n";
			$va{'searchresults_po_print'} .= "   <td colspan='3' class='smalltext' align='right'>Total</td>\n";
			$va{'searchresults_po_print'} .= "   <td class='smalltext' align='right'>".&format_price($total_po)."</td>\n";
			$va{'searchresults_po_print'} .= "   <td class='smalltext' align='right'>".&format_price($total_due)."</td>\n";
			$va{'searchresults_po_print'} .= "   <td class='smalltext' align='right'>".&format_price($total_amount)."</td>\n";
			$va{'searchresults_po_print'} .= "</tr>\n";
			$va{'searchresults_po_print'} .= qq|</table>|;
		}

		## Anticipos y Notas de Credito Pagadas con este Bill
		my ($sth) = &Do_SQL("SELECT COUNT(*) FROM sl_bills INNER JOIN sl_bills_applies USING(ID_bills) WHERE sl_bills_applies.ID_bills_applied='$in{'id_bills'}' AND sl_bills.Type IN ('Deposit','Credit') AND sl_bills.ID_vendors = '$in{'id_vendors'}' ;");
		$va{'matches'} = $sth->fetchrow;
		if ($va{'matches'}>0){
			$va{'searchresults_dc_print'} .= qq|
			<h3>Bills Relacionados</h3>
			<table border="0" cellspacing="0" cellpadding="4" width="100%" class="formtable">
      			<tr>         	
					<td class="menu_bar_title" width="10%" align="center">ID_Bill</td>
					<td class="menu_bar_title" width="35%" align="center">Date</td>
					<td class="menu_bar_title" width="14%" align="center">Bill Type</td>
					<td class="menu_bar_title" width="14%" align="center">Amount Bill</td>
					<td class="menu_bar_title" width="15%" align="center">Billed Amount</td>
			 	</tr>|;
						
			my ($sth) = &Do_SQL("SELECT ID_bills, sl_bills.Amount, Type, ID_vendors as idvendor
			, (SELECT Amount FROM sl_bills WHERE ID_bills = sl_bills_applies.ID_bills) as AmountBill
			, sl_bills_applies.Amount as AmountSpent, sl_bills.Date, sl_bills.Time
			FROM sl_bills INNER JOIN sl_bills_applies USING(ID_bills)
			WHERE sl_bills_applies.ID_bills_applied='$in{'id_bills'}'
			AND sl_bills.Type IN ('Deposit','Credit')
			AND sl_bills.ID_vendors = '$in{'id_vendors'}'
			AND sl_bills.ID_bills NOT IN ('$in{'id_bills'}')
			ORDER BY sl_bills.Date DESC");
			$va{'total_depcred'} = 0;
			while ($rec = $sth->fetchrow_hashref){
				$d = 1 - $d;
				$va{'vendors'} = &load_db_names('sl_vendors','ID_vendors',$rec->{'ID_vendors'},'([ID_vendors]) [CompanyName]');
				my $remaining = $rec->{'Amount'}-$rec->{'AmountSpent'};
				$va{'total_depcred'} += $rec->{'AmountSpent'};

				$va{'searchresults_dc_print'} .= "<tr bgcolor='$c[$d]'>\n";
				$va{'searchresults_dc_print'} .= "  <td class='smalltext'>$rec->{'ID_bills'}</td>\n";
				$va{'searchresults_dc_print'} .= "  <td class='smalltext'>".$rec->{'Date'}." ".$rec->{'Time'}."</td>\n";
				$va{'searchresults_dc_print'} .= "  <td class='smalltext'>$rec->{'Type'}</td>\n";
				$va{'searchresults_dc_print'} .= "  <td class='smalltext' align='right'>".&format_price($rec->{'AmountBill'})."</td>\n";
				$va{'searchresults_dc_print'} .= "  <td class='smalltext' align='right'>".&format_price($rec->{'AmountSpent'})."</td>\n";
				$va{'searchresults_dc_print'} .= "</tr>\n";
			}
			if ($va{'total_depcred'} > 0) {

				$va{'searchresults_dc_print'} .= qq|<tr>
													<td colspan="5"><hr class=""></td>
												</tr>
												<tr bgcolor='$c[$d]'>\n|;
				$va{'searchresults_dc_print'} .= "  <td class='smalltext' colspan='4' align='right'>Total</td>\n";
				$va{'searchresults_dc_print'} .= "  <td class='smalltext' align='right'>".&format_price($va{'total_depcred'})."</td>\n";
				$va{'searchresults_dc_print'} .= "</tr></table>\n";
			}
		}

		## Anticipos y Notas de Credito Pagadas con este Bill (Al reves)
		my ($sth) = &Do_SQL("SELECT COUNT(*) FROM sl_bills INNER JOIN sl_bills_applies USING(ID_bills) WHERE sl_bills_applies.ID_bills='$in{'id_bills'}' AND sl_bills.Type IN ('Deposit','Credit') AND sl_bills.ID_vendors = '$in{'id_vendors'}' ;");
		$va{'matches'} = $sth->fetchrow;
		if ($va{'matches'}>0){
			$va{'searchresults_dc2_print'} .= qq|
			<h3>Bills Relacionados</h3>
			<table border="0" cellspacing="0" cellpadding="4" width="100%" class="formtable">
      			<tr>         	
					<td class="menu_bar_title" width="10%" align="center">ID_Bill</td>
					<td class="menu_bar_title" width="35%" align="center">Date</td>
					<td class="menu_bar_title" width="14%" align="center">Bill Type</td>
					<td class="menu_bar_title" width="14%" align="center">Amount Bill</td>
					<td class="menu_bar_title" width="15%" align="center">Billed Amount</td>
			 	</tr>|;
						
			my ($sth) = &Do_SQL("SELECT ID_bills_applied ID_bills, sl_bills.Amount, Type, ID_vendors as idvendor
			, (SELECT Amount FROM sl_bills WHERE ID_bills = sl_bills_applies.ID_bills) as AmountBill
			, sl_bills_applies.Amount as AmountSpent, sl_bills.Date, sl_bills.Time
			FROM sl_bills INNER JOIN sl_bills_applies USING(ID_bills)
			WHERE sl_bills_applies.ID_bills='$in{'id_bills'}'
			AND sl_bills.Type IN ('Deposit','Credit')
			AND sl_bills.ID_vendors = '$in{'id_vendors'}'
			-- AND sl_bills.ID_bills NOT IN ('$in{'id_bills'}')
			ORDER BY sl_bills.Date DESC");
			$va{'total_depcred'} = 0;
			while ($rec = $sth->fetchrow_hashref){
				$d = 1 - $d;
				$va{'vendors'} = &load_db_names('sl_vendors','ID_vendors',$rec->{'ID_vendors'},'([ID_vendors]) [CompanyName]');
				my $remaining = $rec->{'Amount'}-$rec->{'AmountSpent'};
				$va{'total_depcred'} += $rec->{'AmountSpent'};

				$va{'searchresults_dc2_print'} .= "<tr bgcolor='$c[$d]'>\n";
				$va{'searchresults_dc2_print'} .= "  <td class='smalltext'>$rec->{'ID_bills'}</td>\n";
				$va{'searchresults_dc2_print'} .= "  <td class='smalltext'>".$rec->{'Date'}." ".$rec->{'Time'}."</td>\n";
				$va{'searchresults_dc2_print'} .= "  <td class='smalltext'>$rec->{'Type'}</td>\n";
				$va{'searchresults_dc2_print'} .= "  <td class='smalltext' align='right'>".&format_price($rec->{'AmountBill'})."</td>\n";
				$va{'searchresults_dc2_print'} .= "  <td class='smalltext' align='right'>".&format_price($rec->{'AmountSpent'})."</td>\n";
				$va{'searchresults_dc2_print'} .= "</tr>\n";
			}
			if ($va{'total_depcred'} > 0) {

				$va{'searchresults_dc2_print'} .= qq|<tr>
													<td colspan="5"><hr class=""></td>
												</tr>
												<tr bgcolor='$c[$d]'>\n|;
				$va{'searchresults_dc2_print'} .= "  <td class='smalltext' colspan='4' align='right'>Total</td>\n";
				$va{'searchresults_dc2_print'} .= "  <td class='smalltext' align='right'>".&format_price($va{'total_depcred'})."</td>\n";
				$va{'searchresults_dc2_print'} .= "</tr></table>\n";
			}
		}
	}

	##-------------------------------------------------
	## Valida si es un bill de servicios(Expenses)
	##-------------------------------------------------
	my $sth = &Do_SQL("SELECT COUNT(*) FROM sl_bills_expenses WHERE ID_bills = ".$in{'id_bills'}.";");
	my $exist_expenses = $sth->fetchrow();
	##-------------------------------------------------

	## 
	##
	## Verificamos que tenga autorización
	##
	##
	my ($st) = &Do_SQL("SELECT COUNT(*) from sl_bills WHERE (AuthBy = 1 OR AuthBy IS NULL) AND ID_bills='$in{'id_bills'}'");
	$va{'match_auth'} = $st->fetchrow;

	if ($in{'chgstatusto'} and &check_permissions('mer_bills_change_status','','') and $va{'match_auth'} == 0) {
		##---------------------------------------------------
		## Si el cambio es a New, 
		## 	-> verifica si existen movimientos contables
		##	-> verifica si el bill es de gastos de aterrizaje
		##---------------------------------------------------
		$nmov = 0;
		$npo_adj = 0;
		if( $in{'chgstatusto'} eq 'New' ){
			## Verifica si existe contabilidad
			my $sth = &Do_SQL("SELECT COUNT(*) AS nmov 
								FROM sl_movements 
								WHERE tableused = 'sl_bills' 
									AND ID_tableused = ".$in{'id_bills'}." 	
									AND Category = 'Gastos'								
									AND `Status` = 'Active'
									AND (ID_journalentries IS NOT NULL AND ID_journalentries <> '' AND ID_journalentries <> 0);");
			$nmov = $sth->fetchrow();

			## Verifica si el bill es de gastos de aterrizaje
			my $sth1 = &Do_SQL("SELECT COUNT(*) AS npo_adj 
								FROM sl_bills_pos 
								WHERE ID_bills = ".$in{'id_bills'}."
									AND ID_purchaseorders_adj <> 0;");
			$npo_adj = $sth1->fetchrow();

			if( $nmov > 0 and $npo_adj == 0 ){
				$va{'message'} = &trans_txt('invalid') .' '. &trans_txt('bills_account_trans_active');
				++$err;				
			}
		}
		##---------------------------------------------------

		if( $nmov == 0 or $npo_adj > 0 ){
			my $chgstatus = 1;
			###-------------------------------------
			### Cambio de status a To Pay para Bills de PO Services
			###-------------------------------------
			if( $in{'chgstatusto'} eq 'Processed' ){
				### Se valida que el bill sea de tipo PO Services
				my $sth = &Do_SQL("SELECT sl_purchaseorders.ID_purchaseorders, sl_purchaseorders.`Type`, sl_bills.AuthToPay
									FROM sl_bills
										INNER JOIN sl_bills_pos ON sl_bills.ID_bills = sl_bills_pos.ID_bills
										INNER JOIN sl_purchaseorders ON sl_bills_pos.ID_purchaseorders = sl_purchaseorders.ID_purchaseorders
									WHERE sl_bills.ID_bills = ".int($in{'id_bills'}).";");
				my ($id_po, $po_type, $auth_to_pay) = $sth->fetchrow_array();
				if( $po_type and $po_type eq 'PO Services' and int($auth_to_pay) == 1 ){
					&bills_po_services_toprocessed($in{'id_bills'}, $id_po);
				} elsif ( $po_type and $po_type eq 'PO Services' and int($auth_to_pay) == 0 ){
					$va{'message'} = &trans_txt('unauth_action');
					$chgstatus = 0;
				}
			} elsif( $in{'chgstatusto'} eq 'New' and $in{'status'} eq 'Processed' ){
				### Se valida que el bill sea de tipo PO Services
				my $sth = &Do_SQL("SELECT sl_purchaseorders.ID_purchaseorders, sl_purchaseorders.`Type`
									FROM sl_bills
										INNER JOIN sl_bills_pos ON sl_bills.ID_bills = sl_bills_pos.ID_bills
										INNER JOIN sl_purchaseorders ON sl_bills_pos.ID_purchaseorders = sl_purchaseorders.ID_purchaseorders
									WHERE sl_bills.ID_bills = ".int($in{'id_bills'}).";");
				my ($id_po, $po_type) = $sth->fetchrow_array();
				if( $po_type eq 'PO Services' ){
					$va{'message'} = &trans_txt('unauth_action');
					$chgstatus = 0;
				}
			}

			if( $chgstatus == 1 ){
				my ($sth)	= &Do_SQL("UPDATE sl_bills SET Status='".&filter_values($in{'chgstatusto'})."' WHERE ID_bills='$in{'id_bills'}' LIMIT 1;");		
				&auth_logging(&trans_txt('bills_change_status').' From: '.$in{'status'}.' To: '.$in{'chgstatusto'},$in{'id_bills'});		
				$in{'status'} = $in{'chgstatusto'};
				&bills_to_void($in{'id_bills'}) if ($in{'chgstatusto'} eq 'Void');

				if( $in{'chgstatusto'} eq 'New' and $exist_expenses ){
					### Cancela la contabilidad si no tiene journal
					&Do_SQL("UPDATE sl_movements SET Status='Inactive' WHERE tableused = 'sl_bills' AND ID_tableused = ".$in{'id_bills'}." AND Category = 'Gastos' AND `Status` = 'Active' AND (ID_journalentries IS NULL OR ID_journalentries = 0);");
				}

				###########################
				###########################
				## Procesa la contabilidad
				###########################
				&processed_bills_pos_adj($in{'id_bills'}, $in{'id_vendors'}, $in{'chgstatusto'}) if ($in{'chgstatusto'} eq 'Processed' or $in{'chgstatusto'} eq 'New');

				$va{'message'} = "Change to ".$in{'chgstatusto'};
			}
		}

	}	
	
	#############################################################
	#############################################################
	#############################################################
	#
	#			PAGO PROCESADO
	#
	#############################################################
	#############################################################
	#############################################################
	if ($in{'to_process'}){

		# If it is an expense bill must be validated before
		my ($sth) = &Do_SQL("SELECT sl_bills.Amount BillAmount, SUM(sl_bills_expenses.Amount)Amount, COUNT(*) AS nlines FROM sl_bills INNER JOIN sl_bills_expenses USING(ID_bills) WHERE ID_bills='$in{'id_bills'}';");
		my ($amount_bill, $amount_lines, $no_lines) = $sth->fetchrow_array();
				
		if ($in{'type'} eq 'Bill' and $no_lines > 0 and ($amount_lines <= 0 or $amount_bill != $amount_lines)){

			$va{'message'} = &trans_txt('bills_amounts_not_match');

		}else{

			my ($t_amount) =  $in{'amount'};
			$in{'amount'} = $in{'amount'}*$in{'currency_exchange'} if ($in{'currency'} ne $cfg{'acc_default_currency'} and $in{'currency_exchange'});

			### Se valida si es un Bill de PO de Servicios
			my $sth = &Do_SQL("SELECT sl_purchaseorders.ID_purchaseorders, sl_purchaseorders.`Type`
								FROM sl_bills_pos 
									INNER JOIN sl_purchaseorders ON sl_bills_pos.ID_purchaseorders = sl_purchaseorders.ID_purchaseorders
								WHERE sl_bills_pos.ID_bills = ".int($in{'id_bills'}).";");
			my ($id_po, $po_type) = $sth->fetchrow_array();

			if( $id_po > 0 and $po_type eq 'PO Services' ){

				&bills_po_services_toprocessed($in{'id_bills'}, $id_po);

				my ($sth) = &Do_SQL("UPDATE sl_bills SET Status='Processed' WHERE ID_bills='$in{'id_bills'}';");		
				&auth_logging(&trans_txt('bills_change_status').' From: '.$in{'status'}.' To: Processed',$in{'id_bills'});
				$in{'status'} = 'Processed';

			}elsif ($cfg{'bills_autoproc_'.lc($in{'type'})} and $t_amount > $cfg{'bills_autoproc_'.lc($in{'type'})}  and $in{'status'} eq 'New'){
				
				if (&check_permissions('mer_bills_toprocessed','','')){

					my ($sth) = &Do_SQL("UPDATE sl_bills SET Status='Pending' WHERE ID_bills='$in{'id_bills'}';");
					
					&auth_logging('mer_bills_topending',$in{'id_bills'});
					$va{'message'} = &trans_txt('mer_bills_topending');
					$in{'status'} = 'Pending';

				}else{
					$va{'message'} = &trans_txt('unauth_action');
				}

			}elsif ($cfg{'bills_autoproc_'.lc($in{'type'})} and $t_amount > $cfg{'bills_autoproc_'.lc($in{'type'})}  and $in{'status'} eq 'Pending'){
				
				if (&check_permissions('mer_bills_pendauth','','')){

					###########################
					###########################
					####
					#### Pasa a Processed
					####
					###########################
					###########################

					&bills_to_processed($in{'id_bills'},$in{'currency_exchange'});

				}else{
					$va{'message'} = &trans_txt('unauth_action');
				}

			}elsif (&check_permissions('mer_bills_toprocessed','','')){				
				###########################
				###########################
				####
				#### Pasa a Processed
				####
				###########################
				###########################

				&bills_to_processed($in{'id_bills'},$in{'currency_exchange'});

				###########################
				###########################
				## Procesa la contabilidad
				###########################				
				&processed_bills_pos_adj($in{'id_bills'}, $in{'id_vendors'}, 'Processed');

			}else{
				$va{'message'} = &trans_txt('unauth_action');
			}
		}
	}

	#############################################################
	#############################################################
	## Valida si el usuario tiene permisos para modificar el
	## estatus del bill, y genera los links según sea el caso.
	#############################################################
	if (!&check_permissions('mer_bills_change_status','','')) {
		$va{'chgstatus'} = qq| <span class="smallfieldterr">|.&trans_txt('unauth_action').qq|</span>|;
	} else {
		if($in{'to_process'}){
			$va{'match_auth'} = 0;
		}
		if($va{'match_auth'} == 0){
			my (@ary) = &load_enum_toarray('sl_bills','Status');
			for (0..$#ary) {
				my $auth_shw = 0;
				if( ($exist_expenses > 0 and $ary[$_] ne 'Processed') or ($exist_expenses > 0 and $in{'status'} eq 'To Pay' and $ary[$_] eq 'Processed') or $exist_expenses == 0 ){
					$auth_shw = 1;
				}

				if ($ary[$_] ne $in{'status'} and ($ary[$_] ne 'Void' and $in{'status'} ne 'Paid') and $auth_shw == 1){
					$va{'chgstatus'} .= qq| <a href="/cgi-bin/mod/$usr{'application'}/dbman?cmd=mer_bills&view=$in{'id_bills'}&chgstatusto=$ary[$_]">$ary[$_]</a> &nbsp;&nbsp;&nbsp;|;
				}
			}
		}
	}

	#############################################################
	#############################################################
	#############################################################
	#
	#			PAGO CANCELADO
	#
	#############################################################
	#############################################################
	#############################################################
	if ($in{'cancel_payment'} and &check_permissions('mer_bills_partial_cancellation_payments','','')){

		# buscar todos los payments y duplicarlos con montos negativos(Debits)
		my ($sth) = &Do_SQL("SELECT Amount, ID_banks_movements, ID_banks_movrel
		FROM sl_banks_movrel INNER JOIN sl_banks_movements USING(ID_banks_movements) 
		WHERE tablename='bills' AND tableid='".&filter_values($in{'view'})."' AND ID_banks_movements='".$in{'cancel_payment'}."' AND Amount > 0
		AND (SELECT count(*) FROM sl_banks_movements_notes WHERE Type='Cancel' AND ID_banks_movements=sl_banks_movements.ID_banks_movements) = 0;");
		while ($rec = $sth->fetchrow_hashref){

			if (!$rec->{'duplicated'}) {

				my($tmp_sth2) = &Do_SQL("SELECT  ID_banks,  ConsDate,  Amount,  currency_exchange,  RefNum  FROM sl_banks_movements WHERE ID_banks_movements = '".$rec->{'ID_banks_movements'}."';");
				my($tmp_id_banks,$tmp_consdate,$tmp_amount,$tmp_currency_exchange,$tmp_refnum) = $tmp_sth2->fetchrow_array();

				my ($sth2) = &Do_SQL("INSERT INTO sl_banks_movements (ID_banks,  Type,  BankDate,  ConsDate,  Amount,  currency_exchange,  RefNum,  Memo,  Date,  Time,  ID_admin_users ) values 
				('$tmp_id_banks',  'Debits',  '$tmp_curdate',  '$tmp_consdate',  '$tmp_amount',  '$tmp_currency_exchange',  '$tmp_refnum',  'Cancel Bank Movement',  CURDATE(),  CURTIME(),  $usr{'id_admin_users'} );");
				$id_banks_movements = $sth2->{'mysql_insertid'};

				my ($sth) = &Do_SQL("INSERT INTO sl_banks_movrel SET ID_banks_movements = '$id_banks_movements', tablename = 'bills', tableid = '".$in{'id_bills'}."', DATE = CURDATE(), TIME = CURTIME(), ID_admin_users='$usr{'id_admin_users'}'");

				# La nota me indicara si este movimineto esta cancelado
				my ($sth) = &Do_SQL("INSERT INTO sl_banks_movements_notes (ID_banks_movements_notes,  ID_banks_movements,  Notes,  Type,  Date,  Time,  ID_admin_users )
				VALUES(NULL, $in{'cancel_payment'}, 'This movement has been cancelled.', 'Cancel', CURDATE(), CURTIME(),$usr{'id_admin_users'});");
				
				# pasar el status del bill a New o Partly Paid o el que le corresponda
				# calcular el due y sobre eso definirlo

				$sql_string = "SELECT Amount, IFNULL(Amount - (SELECT IFNULL(SUM(Amount),0)as Amount FROM sl_banks_movrel INNER JOIN sl_banks_movements USING(ID_banks_movements) WHERE tablename='bills' AND tableid=bills.ID_bills) - (SELECT IFNULL(SUM(sl_bills_applies.Amount),0)as Amount FROM sl_bills_applies INNER JOIN sl_bills USING(ID_bills) WHERE ID_bills_applied = bills.ID_bills AND sl_bills.Type IN ('Deposit','Credit')), 0)as Amount FROM sl_bills as bills WHERE ID_bills ='".$in{'view'}."';";
				if ($in{'currency'} ne $cfg{'acc_default_currency'}) {
					$sql_string = "SELECT Amount, IFNULL(Amount - (SELECT IFNULL(SUM(AmountCurrency),0)as Amount FROM sl_banks_movrel INNER JOIN sl_banks_movements USING(ID_banks_movements) WHERE tablename='bills' AND tableid=bills.ID_bills) - (SELECT IFNULL(SUM(sl_bills_applies.Amount),0)as Amount FROM sl_bills_applies INNER JOIN sl_bills USING(ID_bills) WHERE ID_bills_applied = bills.ID_bills AND sl_bills.Type IN ('Deposit','Credit')), 0)as Amount FROM sl_bills as bills WHERE ID_bills ='".$in{'view'}."';";
				}
				my ($sth) = &Do_SQL($sql_string);
				my ($bill_amount,$bill_amount_payable) = $sth->fetchrow_array();

				my $status = ($bill_amount==$bill_amount_payable)?'New':'Partly Paid';

				my ($sth) = &Do_SQL("UPDATE sl_bills SET Status='$status' WHERE ID_bills = '".$in{'id_bills'}."' LIMIT 1;");
				$in{'status'} = &load_name("sl_bills","ID_bills",$in{'view'},"Status");

				# grabar en el log estos movimientos
				$in{'db'} = "sl_bills";
				&auth_logging('mer_bills_payment_canceled', $in{'id_bills'});
			}
		}

	}


	## Cancel bill payment
	if ($in{'cancel'} and $in{'status'} eq 'Paid' and &check_permissions('mer_bills_cancel','','')){
		
		# buscar todos los deposits y credits y desligarlos (borrarlos de la tabla sl_bills_applies)
		my ($sth) = &Do_SQL("SELECT sl_bills_applies.ID_bills_applies FROM sl_bills INNER JOIN sl_bills_applies USING(ID_bills) WHERE sl_bills_applies.ID_bills_applied='$in{'id_bills'}' AND sl_bills.Type IN ('Deposit','Credit','Debit') AND sl_bills.ID_vendors = '$in{'id_vendors'}' AND sl_bills.ID_bills NOT IN ('$in{'id_bills'}');");
		while ($rec = $sth->fetchrow_hashref){
			my ($sth2) = &Do_SQL("DELETE FROM sl_bills_applies WHERE ID_bills_applies = '".$rec->{'ID_bills_applies'}."' LIMIT 1;");
		}
		
		# buscar todos los POs (borrarlos de la tabla sl_bills_pos)
		my ($sth) = &Do_SQL("SELECT ID_bills_pos FROM sl_bills INNER JOIN sl_bills_pos USING(ID_bills) INNER JOIN sl_purchaseorders USING(ID_purchaseorders)  WHERE 1 AND ID_bills='$in{'id_bills'}';");
		while ($rec = $sth->fetchrow_hashref){
			my ($sth2) = &Do_SQL("DELETE FROM sl_bills_pos WHERE ID_bills_pos = '".$rec->{'ID_bills_pos'}."' LIMIT 1;");
		}

		# buscar todos los payments y duplicarlos con montos negativos(Debits)
		my ($sth) = &Do_SQL("SELECT ID_banks_movements, ID_banks_movrel FROM sl_banks_movrel INNER JOIN sl_banks_movements USING(ID_banks_movements) WHERE tablename='bills' AND tableid='".&filter_values($in{'view'})."';");
		while ($rec = $sth->fetchrow_hashref){

			my ($tmp_sth2) = &Do_SQL("SELECT  ID_banks,  ConsDate,  Amount,  currency_exchange,  RefNum FROM sl_banks_movements WHERE ID_banks_movements = '".$rec->{'ID_banks_movements'}."';");
			my ($tmp_id_banks,$tmp_consdate,$tmp_amount,$tmp_currency_exchange,$tmp_refnum) = $tmp_sth2->fetchrow_array();

			my ($sth2) = &Do_SQL("INSERT INTO sl_banks_movements (ID_banks,  Type,  BankDate,  ConsDate,  Amount,  currency_exchange,  RefNum,  Memo,  Date,  Time,  ID_admin_users ) values
				('$tmp_id_banks',  'Debits',  curdate(),  '$tmp_consdate',  '$tmp_amount',  '$tmp_currency_exchange',  '$tmp_refnum',  'Cancel Bank Movement',  curdate(),  curtime(),  $usr{'id_admin_users'} );");
			$id_banks_movements = $sth2->{'mysql_insertid'};

			my ($sth) = &Do_SQL("INSERT INTO sl_banks_movrel SET ID_banks_movements = $id_banks_movements, tablename = 'bills', tableid = '".$in{'id_bills'}."', DATE = Curdate(), TIME = NOW(), ID_admin_users='$usr{'id_admin_users'}'");
			# le falta agregar el AmountPaid

			# La nota me indicara si este movimineto esta cancelado
			my ($sth) = &Do_SQL("INSERT INTO sl_banks_movements_notes (ID_banks_movements_notes,  ID_banks_movements,  Notes,  Type,  Date,  Time,  ID_admin_users )
			VALUES(NULL, $rec->{'ID_banks_movements'}, 'This movement has been cancelled.', 'Cancel', CURDATE(), CURTIME(),$usr{'id_admin_users'});");
		}		

		# pasar el status del bill a Void
		my ($sth) = &Do_SQL("UPDATE sl_bills SET Status='Void' WHERE ID_bills = '".$in{'id_bills'}."' LIMIT 1;");
		$in{'status'} = &load_name("sl_bills","ID_bills",$in{'view'},"Status") if (!$in{'status'});

		# grabar en el log todos estos movimientos
		$in{'db'} = "sl_bills";
		&auth_logging('mer_bills_canceled', $in{'id_bills'});
	}

	## Button Cancel bill payment
	if ($in{'status'} eq 'Paid' and &check_permissions('mer_bills_cancel','','')){
		$va{'cancel_bill_payment'} .= '&nbsp;  <a href="/cgi-bin/mod/'.$usr{'application'}.'/dbman?cmd=[in_cmd]&view='.$in{'id_bills'}.'&cancel=1"><img src="[va_imgurl]/[ur_pref_style]/delete.png" title="'.trans_txt('mer_bills_cancel').'" onclick="return Confirm_to_continue()"></a>';
	}


	#############################################################
	#############################################################
	#############################################################
	#
	#			ACCIONES
	#
	#############################################################
	#############################################################
	#############################################################
	if($in{'action'}){

		###
		### tab 2
		###
		$in{'n_amount'} = &filter_values($in{'n_amount'});
		$in{'n_amount'} = $in{'amount'} if (!$in{'n_amount'} and $in{'amount'} > 0);
		my $val_id_accounts_ml = $in{'id_accounts_ml'};
		$val_id_accounts_ml =~ s/\|//g;
		my $add_sql = ($val_id_accounts_ml eq '')? ",ID_accounts = '".&filter_values($in{'n_id_accounts'})."' ":",ID_accounts = NULL ";

		if (!$in{'n_amount'} or $in{'n_amount'} eq "" or $in{'n_amount'} <= 0 and (!$in{'delete_line'} and !$in{'id_segments'} and !$in{'amount_ml'})){
			$error{'n_amount'} = &trans_txt('required');
			++$err;
		}
		if ((int($in{'n_id_accounts'}) == 0) and !&bills_expenses_detection($in{'id_bills'}) and (!$in{'delete_line'} and !$in{'id_segments'} and !$in{'amount_ml'})){
			$error{'n_id_accounts'} = &trans_txt('required');
			++$err;
		}

		if (!$err and !$in{'search'} and !$in{'add'}) {

			#validar el n_amount como numero y el id accounts
			my ($sth) = &Do_SQL("UPDATE sl_bills  SET Amount = ".$in{'n_amount'}." ".$add_sql." WHERE ID_bills = $in{'id_bills'} LIMIT 1;");
			&auth_logging('mer_bills_amount_edited',$in{'id_bills'});
			$va{'tab_messages'} = &trans_txt("bills_amount_edited");

		}elsif( !$in{'search'} and !$in{'add'} ) {

			if (!$in{'delete_line'} and !$in{'id_segments'} and !$in{'amount_ml'} and (int($in{'tab'}) == 1 and !$in{'id_purchaseorders'})) {
				$va{'tab_messages'} = &trans_txt('reqfields_short');
				delete($in{'action'});
			}

		}

		# Procesamiento de detalle multilinea
		if ($in{'tab'} == 2 and int($in{'view'}) > 0 ) {

			if ($in{'delete_line'}) {

				###########################
				###########################
				## Borrado de lineas
				## ToDo AD: Agregar un boton de Cerrado de Bill expense para guardar en ese momento la contabilidad del expense
				## ToDo AD: Al borrar, revisar si la contabilidad ya fue posteada, como borrar. Preferible borar toda la contabilidad de el expense 
				###########################
				###########################

				$related = &load_name("sl_bills_expenses","id_bills_expenses",$in{'delete_line'},"Related_ID_bills_expenses");

				my ($sth) = &Do_SQL("DELETE FROM sl_bills_expenses WHERE id_bills_expenses = '$in{'delete_line'}' LIMIT 1;");
				# Log
				$in{'db'} = "sl_bills";
				&auth_logging('bills_expenses_line_removed',$in{'view'});
				
				my ($sth) = &Do_SQL("DELETE FROM sl_bills_expenses WHERE Related_ID_bills_expenses = '$in{'delete_line'}' LIMIT 1;");
				# Log
				$in{'db'} = "sl_bills";
				&auth_logging('bills_expenses_line_removed',$in{'view'});
				
			}else {

				my @arr_amount_ml = split /\|/, $in{'amount_ml'};
				my @arr_id_accounts_ml = split /\|/, $in{'id_accounts_ml'};
				my @arr_id_bills_expenses = split /\|/, $in{'id_bills_expenses'};
				my @arr_tax_amount_ml = split /\|/, $in{'tax_amount_ml'};
				my @arr_tax_id_accounts_ml = split /\|/, $in{'tax_id_accounts_ml'};
				my @arr_id_segments = split /\|/, $in{'id_segments'};


				my $total_lines, $lines;
				for my $i (0..$#arr_id_accounts_ml) {
					my $amount_ml = &filter_values($arr_amount_ml[$i]);
					my $id_accounts_ml = $arr_id_accounts_ml[$i];
					my $id_bills_expenses = int($arr_id_bills_expenses[$i]);
					my $tax_amount_ml = &filter_values($arr_tax_amount_ml[$i]);
					my $tax_id_accounts_ml = int($arr_tax_id_accounts_ml[$i]);
					my $id_segments = int($arr_id_segments[$i]);
					
					# Validar si vienen los campos requeridos
					if (int($id_accounts_ml) > 0 and $amount_ml > 0 ) {
						# Obtengo el valor total del Bill, Monto Restante em detalle, Monto Detallado en lineas
						my ($sth) = &Do_SQL("SELECT IFNULL(sl_bills.Amount,0)Amount, IFNULL(sl_bills.Amount - IFNULL(SUM(sl_bills_expenses.Amount),0),0)AmountRemaining, IFNULL(SUM(sl_bills_expenses.Amount),0)AmountLines FROM sl_bills LEFT JOIN sl_bills_expenses USING(ID_bills) WHERE ID_bills = '".$in{'view'}."'");
						my ($bill_amount, $amount_remaining, $amount_lines) = $sth->fetchrow_array();

						# &cgierr($amount_ml.'---'.$amount_remaining);
						# Lo cancelo temporalmente
						# if ($amount_ml <= $amount_remaining){

							my $deductible = ($in{'deductible'})? "Deductible = 'Yes', ": "Deductible = 'No',";
							my $sth = &Do_SQL("INSERT INTO sl_bills_expenses SET $deductible `ID_segments` = '$id_segments', `ID_bills` = '$in{'view'}',  `Amount` = '$amount_ml',  `ID_accounts` = '$id_accounts_ml',  `Date` = CURDATE(),  `Time` = CURTIME(),  `ID_admin_users` = '$usr{'id_admin_users'}';");
							my $id_bills_expenses = $sth->{'mysql_insertid'};
							$in{'id_bills_expenses'} .= $id_bills_expenses.',';
							
							if (int($id_bills_expenses)> 0){

								# Log
								$in{'db'} = "sl_bills";
								&auth_logging('bills_expenses_line_added',$in{'view'});

								## revisamos si se agrega linea Related de tax
								# and $tax_amount_ml > 0
								if (int($tax_id_accounts_ml) > 0) {
									# Obtengo el valor total del Bill, Monto Restante em detalle, Monto Detallado en lineas
									my ($sth) = &Do_SQL("SELECT IFNULL(sl_bills.Amount,0)Amount, IFNULL(sl_bills.Amount - IFNULL(SUM(sl_bills_expenses.Amount),0),0)AmountRemaining, IFNULL(SUM(sl_bills_expenses.Amount),0)AmountLines FROM sl_bills LEFT JOIN sl_bills_expenses USING(ID_bills) WHERE ID_bills = '".$in{'view'}."'");
									my ($bill_amount, $amount_remaining, $amount_lines) = $sth->fetchrow_array();

									# if ($tax_amount_ml <= $amount_remaining) {
										my $sth = &Do_SQL("INSERT INTO sl_bills_expenses SET $deductible `ID_segments` = '$id_segments', `ID_bills` = '$in{'view'}',  `Amount` = '$tax_amount_ml',  `ID_accounts` = '$tax_id_accounts_ml',  `Date` = CURDATE(),  `Time` = CURTIME(),  `ID_admin_users` = '$usr{'id_admin_users'}';");
										my $id_related = $sth->{'mysql_insertid'};
										$in{'id_bills_expenses'} .= $id_related.',';

										my $sth = &Do_SQL("UPDATE sl_bills_expenses SET Related_ID_bills_expenses='$id_bills_expenses' WHERE ID_bills_expenses='$id_related' LIMIT 1;");
										
										if (int($id_related)> 0){

											# Log
											$in{'db'} = "sl_bills";
											&auth_logging('bills_expenses_line_added',$in{'view'});
										}
									# }else {							
									# 	$va{'tab_messages'} = &trans_txt('bills_expenses_line_amount_higher');
									# }
								}
							}

						# }else {							
						# 	$va{'tab_messages'} = &trans_txt('bills_expenses_line_amount_higher');
						# }
					}else {
						# $va{'messages'} .= &trans_txt('required').' : Bill '.$id_creddep.'<br>';
						
					}
				}#for
			}
		}

	}	
	
	if ($in{'addpo'}) {
		if( $in{'adj'} ){
			my ($sth) = &Do_SQL("INSERT INTO sl_bills_pos SET ID_bills='$in{'id_bills'}', ID_purchaseorders=0, ID_purchaseorders_adj=$in{'addpo'}, Date=CURDATE(),Time=CURTIME(),ID_admin_users=$usr{'id_admin_users'}");	
		}else{
			my ($sth) = &Do_SQL("INSERT INTO sl_bills_pos SET ID_bills='$in{'id_bills'}', ID_purchaseorders=$in{'addpo'}, ID_purchaseorders_adj=0, Date=CURDATE(),Time=CURTIME(),ID_admin_users=$usr{'id_admin_users'}");	
		}
		$va{'tab_messages'} = &trans_txt('po_added');
	}elsif($in{'delpo'}) {		
		#my $amount = &load_name("sl_bills_pos","ID_bills_pos",$in{'delpo'},"Amount");
		my ($sth) = &Do_SQL("DELETE FROM sl_bills_pos WHERE ID_bills='$in{'id_bills'}' AND ID_bills_pos=$in{'delpo'} LIMIT 1;");
		&update_amount_bill($in{'id_bills'});
		$va{'tab_messages'} = &trans_txt('po_delete');
	}
		
	if($in{'addbills'}){
		my ($sth) = &Do_SQL("INSERT INTO sl_bills_applies SET ID_bills = $in{'id_bills'}, ID_bills_applied = $in{'addbills'},DATE = CURRENT_DATE(), TIME = CURRENT_TIME(), ID_admin_users=$usr{'id_admin_users'}");	
		$va{'tab_messages'} = &trans_txt('bills_applied');
	}elsif($in{'delbills'}){
		my ($sth) = &Do_SQL("DELETE FROM sl_bills_applies WHERE ID_bills='$in{'id_bills'}' AND ID_bills_applied = $in{'delbills'} LIMIT 1;");	
		$va{'tab_messages'} = &trans_txt('bills_applied_delete');
	}
	
	if ($in{'updateinfo'}) {

		################################
		################################
		################################
		#######
		#######  Edicion de Montos para PO a pagar
		#######
		################################
		################################
		################################


		##############
		############## 1) SE revisan los montos (Query igual al que esta en cgi-bin\common\tabs\bills.cgi)
		##############
		my $sth;
		my $sthd;
		if( $in{'id_po_adj'} ){
			$sth = &Do_SQL("SELECT 
								sl_purchaseorders_adj.TotalOriginal,
								sl_purchaseorders_adj.Amount_original,	
								sl_purchaseorders_adj.Total,
								sl_purchaseorders_adj.Status,  
								IFNULL((SELECT SUM(sl_bills_pos.Amount) FROM sl_bills INNER JOIN sl_bills_pos USING(ID_bills) WHERE ID_purchaseorders_adj = sl_purchaseorders_adj.ID_purchaseorders_adj AND sl_bills.Status = 'Paid'),0)as TotalPaid,
								IFNULL((SELECT SUM(sl_bills_pos.Amount) FROM sl_bills INNER JOIN sl_bills_pos USING(ID_bills) WHERE ID_purchaseorders_adj = sl_purchaseorders_adj.ID_purchaseorders_adj AND sl_bills.Status <> 'Void'),0)as TotalInBills,
								(Select SUM(IF(po_adj.TotalOriginal > 0, po_adj.TotalOriginal, po_adj.Total)) From sl_purchaseorders_adj po_adj Where po_adj.ID_purchaseorders=sl_purchaseorders_adj.ID_purchaseorders) As SumTotalOriginal,
								(Select SUM(po_adj.Total) From sl_purchaseorders_adj po_adj Where po_adj.ID_purchaseorders=sl_purchaseorders_adj.ID_purchaseorders) As SumTotal
							FROM sl_purchaseorders  
								INNER JOIN sl_purchaseorders_adj USING(ID_purchaseorders)
							WHERE 1
								AND sl_purchaseorders.Status NOT IN('Cancelled','Paid')
					 		    AND sl_purchaseorders.Auth = 'Approved'
					 		    AND sl_purchaseorders_adj.ID_purchaseorders_adj = '$in{'id_po_adj'}'
							    AND (SELECT ifnull(SUM(Received),0)as Received FROM sl_purchaseorders_items WHERE ID_purchaseorders =sl_purchaseorders.ID_purchaseorders) > 0;");
			## Monto actual en el Bill
			$sthd = &Do_SQL("SELECT IFNULL(ROUND(SUM(sl_bills_pos.Amount),2),0)
							 FROM sl_bills_pos 
								INNER JOIN sl_bills USING(ID_bills)
							 WHERE ID_bills = '$in{id_bills}'
								AND ID_purchaseorders_adj = $in{'id_po_adj'};");

		}elsif( $in{'id_po_item'} > 0 ){
			$sth = &Do_SQL("SELECT 
								sl_purchaseorders_items.Total
								, sl_purchaseorders_items.Total_edited								
							FROM sl_purchaseorders_items  								
							WHERE 1								
					 		    AND sl_purchaseorders_items.Received > 0
					 		    AND sl_purchaseorders_items.ID_purchaseorders_items = '$in{'id_po_item'}'
							;");
			## Monto actual en el Bill
			$sthd = &Do_SQL("SELECT SUM(Amount) 
							 FROM sl_bills_pos
							 WHERE ID_purchaseorders = '$in{'id_po'}';");

		}elsif( $in{'id_po'} ){
			$sth = &Do_SQL("SELECT /*, po_items.TotalPO,*/ po_items.TotalWR
								, IFNULL(bills_pos.TotalInBills, 0) AS TotalInBills								
								, IFNULL((SELECT SUM(sl_bills_pos.Amount) FROM sl_bills INNER JOIN sl_bills_pos USING(ID_bills) WHERE ID_purchaseorders = sl_purchaseorders.ID_purchaseorders AND sl_bills.Status = 'Paid'), 0) AS TotalPaid
							FROM sl_purchaseorders
								INNER JOIN (
									SELECT /*SUM(Total) AS TotalPO,*/ ROUND(SUM((Price*Received)*(1+Tax_percent)), 3) TotalWR, IFNULL(SUM(Received),0)as TotalReceived, sl_purchaseorders_items.ID_purchaseorders
									FROM sl_purchaseorders_items
									GROUP BY sl_purchaseorders_items.ID_purchaseorders
								) AS po_items USING(ID_purchaseorders)
								LEFT JOIN(
									SELECT sl_bills_pos.ID_purchaseorders, SUM(sl_bills_pos.Amount) AS TotalInBills
									FROM sl_bills 
										INNER JOIN sl_bills_pos USING(ID_bills)
									WHERE sl_bills.Status <> 'Void'
									GROUP BY sl_bills_pos.ID_purchaseorders
								) AS bills_pos USING(ID_purchaseorders) 
							WHERE 1 
								AND sl_purchaseorders.ID_purchaseorders = '$in{'id_po'}' 
								AND sl_purchaseorders.Status NOT IN('Cancelled','Paid')
								AND sl_purchaseorders.Auth = 'Approved' 
								AND TotalReceived > 0;");
			## Monto actual en el Bill
			$sthd = &Do_SQL("SELECT IFNULL(ROUND(SUM(sl_bills_pos.Amount),2),0)
							 FROM sl_bills_pos 
								INNER JOIN sl_bills USING(ID_bills)
							 WHERE ID_bills = '$in{id_bills}'
								AND ID_purchaseorders = $in{'id_po'};");
		}
		my $rec = $sth->fetchrow_hashref();		
		my ($this_amt) = $sthd->fetchrow();

		my $val_amt;

		if( $in{'id_po_adj'} ){
			# Se obtiene el currency del proveedor
			my $vendor_currency = &load_db_names('sl_vendors','ID_vendors',$in{'id_vendors'},'[Currency]');

			my $total_amount_adj = 0;
			if( $vendor_currency eq 'MX$' ){
				if( $rec->{'TotalOriginal'} > 0 ){					
					$in{'amount_po'} = round($rec->{'TotalOriginal'},2);
				}else{#elsif( $rec->{'Status'} eq "Active" ){
					$in{'amount_po'} = round($rec->{'Amount_original'},2);

				}
				# Monto total de los gastos
				$total_amount_adj = $rec->{'SumTotalOriginal'};
			}else{
				$in{'amount_po'} = round($rec->{'Total'},2);
				# Monto total de los gastos
				$total_amount_adj = $rec->{'SumTotal'};
			}

			# monto total en Bills
			$in{'amount_billsa'} = $rec->{'TotalInBills'} > 0 ? round($rec->{'TotalInBills'},2) : 0;
			$in{'amount_billsa'} -= $this_amt;

			# Monto Adeudado
			$va{'total_due'} = ($in{'amount_po'} - $in{'amount_billsa'});			

			my $amount_limit = (1+$cfg{'perc_dif_po_adj'}) * $total_amount_adj;
			$amount_limit -= $in{'amount_billsa'};
			
			# Se aplica la validacion
			$val_amt = ( $in{'ajaxamount'} <= $amount_limit or $rec->{'Amount_original'} > $total_amount_adj ) ? 'OK' : 'NO';
			#&cgierr("amount_po: ".$in{'amount_po'}.", TotalAdj: ".$total_amount_adj.", amount_limit: ".$amount_limit." - ".$val_amt);

		}elsif( $in{'id_po_item'} > 0 ){

			my $this_diff_amt = ($rec->{'Total_edited'} == 0) ? ($rec->{'Total'} - $in{'ajaxamount'}) : ($rec->{'Total_edited'} - $in{'ajaxamount'});
			if( $this_diff_amt > 0 ){
				$va{'total_due'} = $this_amt - abs($this_diff_amt);
			} else {
				$va{'total_due'} = $this_amt + abs($this_diff_amt);
			}

			$val_amt = ( $in{'ajaxamount'} <= ($rec->{'Total'} * 1.5) ) ? 'OK' : 'NO';

		}else{
			$in{'amount_po'} = round($rec->{'TotalWR'}, 2);

			# monto total en Bills
			$in{'amount_billsp'} = $rec->{'TotalPaid'} > 0 ? round($rec->{'TotalPaid'},2) : 0;
			$in{'amount_billsa'} = $rec->{'TotalInBills'} > 0 ? round($rec->{'TotalInBills'},2) : 0;
			$in{'amount_billsa'} -= $this_amt;
			
			# Monto Adeudado
			$va{'total_due'} = ($in{'amount_po'} - $in{'amount_billsa'});

			# Se aplica la validacion
			$val_amt = ( $in{'ajaxamount'} <= $va{'total_due'} ) ? 'OK' : 'NO';	

			# Se valida el tipo de PO
			if( $val_amt eq 'NO' and $in{'ajaxamount'} > 0 and $va{'total_due'} > 0 ){
				my $po_type = &load_name('sl_purchaseorders', 'ID_purchaseorders', $in{'id_po'}, 'Type');
				$val_amt = 'OK' if($po_type eq 'PO Services');
			}
		}
		
		if($val_amt eq 'OK' and $in{'ajaxamount'} > 0){

			if( $in{'id_po_item'} > 0 ){
				&Do_SQL("START TRANSACTION;");
				### Se modifica el monto en purchaseorders_items
				$in{'ajaxamount'} = 0 if( $rec->{'Total'} == $in{'ajaxamount'} );
				&Do_SQL("UPDATE sl_purchaseorders_items SET Total_edited = ".$in{'ajaxamount'}." WHERE ID_purchaseorders_items = ".$in{'id_po_item'}.";");
				&Do_SQL("UPDATE sl_bills_pos SET Amount = ".$va{'total_due'}." WHERE ID_bills_pos = ".$in{'id_bills_pos'}.";");
				### Notes
				&Do_SQL("INSERT sl_bills_notes SET ID_bills = ".$in{'id_bills'}.", Notes = 'PO Services Item edited:\nID: ".$in{'id_po_item'}." :: ".&format_price($in{'ajaxamount'})."', `Type` = 'High', Date = CURDATE(), Time = CURTIME(), ID_admin_users = ".$usr{'id_admin_users'}.";");

				&Do_SQL("COMMIT");

				$va{'tab_messages'} = &trans_txt('mer_bills_amount_edited');
			} else {
				my ($query,@cols);
				@cols = ('Amount');
				for(0..$#cols){
					if ($in{'type'} and $in{'type'} eq 'Bill') {
						$query .= " $cols[$_]='".&filter_values($in{'ajax'.lc($cols[$_])})."',";
					}elsif ($in{'type'} and $in{'type'} eq 'Credit') {
						$query .= " $cols[$_]='".&filter_values($in{'ajax'.lc($cols[$_])})."',";
					}
				}
				chop($query);
				my ($sth) = &Do_SQL("UPDATE sl_bills_pos SET $query WHERE ID_bills_pos='$in{'id_bills_pos'}' LIMIT 1;");
			}
			
			&update_amount_bill($in{'id_bills'});

		}else{
			$va{'tab_messages'} = 'XX ::'.&trans_txt('bills_amount_invalid');
		}
	}
	
	######
	###### Cambio de Bill -> Deposit
	######
	if($in{'type'} eq 'Bill' and &check_permissions('mer_bills_to_deposit','','')){

		if($in{'todeposit'}){

			###
			### Si el Bill esta pagado, cambiamos su contabilidad para ser la de un Deposit 
			### ToDo. Los Deposit deberia ir ligados al Bill y segunda tabla al vendor, contrario a lo actual
			###
			my ($sth) = &Do_SQL("SELECT COUNT(*) FROM sl_bills_pos WHERE ID_bills = '$in{'id_bills'}';");
			my ($these_pos) = $sth->fetchrow();

			my ($sth) = &Do_SQL("SELECT COUNT(*) FROM sl_bills_applies WHERE ID_bills_applied = '$in{'id_bills'}';");
			my ($these_applies) = $sth->fetchrow();			

			if(!$these_pos and !$these_applies){

				if($in{'status'} =~ /Paid/){

					###
					### a) Si el Bill estaba Pagado o Parcialmente Pagado, tenemos que generar nueva contabilidad
					###
					my ($sth) = &Do_SQL("SELECT ID_banks, AmountPaid, currency_exchange, BankDate, IF(MONTH(BankDate) = MONTH(CURDATE()) AND YEAR(BankDate) = YEAR(CURDATE()),1,0)AS Valid FROM sl_banks_movements INNER JOIN sl_banks_movrel USING(ID_banks_movements) WHERE tableid = '". int($in{'id_bills'}) ."' AND tablename = 'bills';");
					my ($id_banks, $amount, $currency_exchange, $bankdate, $valid) = $sth->fetchrow();

					if($valid){
					
						my ($sth) = &Do_SQL("SELECT sl_banks.ID_accounts 
											 FROM sl_banks 
											 	INNER JOIN sl_accounts ON sl_accounts.ID_accounts = sl_banks.ID_accounts
											 WHERE ID_banks = ". int($id_banks) ." 
											 	AND sl_banks.`Status` = 'Active' 
											 	AND sl_accounts.`Status` = 'Active'
											 LIMIT 1;");
						my ($ida_banks) = $sth->fetchrow();

						if(!$ida_banks){
							$va{'message'} = &trans_txt('mer_bills_bank_accounting_missing');
							++$err;	
						}

						if(!$va{'message'}){

							my $vendor_category = &load_name('sl_vendors','ID_vendors', $in{'id_vendors'},'Category');
							$currency_exchange = 1 if !$currency_exchange;
							my @params = ($in{'id_vendors'}, $in{'id_bills'}, $ida_banks,$bankdate, $amount, $currency_exchange);
							#&cgierr('vendor_deposit_' . lc($vendor_category) . " --- $vendor_category $in{'id_vendors'}, $in{'id_bills'}, $ida_banks, $bankdate, $amount, $currency_exchange");
							&accounting_keypoints('vendor_deposit_' . lc($vendor_category), \@params );

						}

					}else{

						$va{'message'} = &trans_txt('mer_bills_to_deposit_invalid');

					}

				}

				###
				### b) Inactivamos Contabilidad anterior y cambiamos el tipo
				###
				if(!$va{'message'}){

					&Do_SQL("UPDATE sl_movements SET Status = 'Inactive' WHERE tableused = 'sl_bills' AND ID_tableused = '". int($in{'id_bills'})."';");
					&Do_SQL("UPDATE sl_bills SET Type = 'Deposit' WHERE ID_bills = '$in{'id_bills'}' AND Type = 'Bill';");
					&auth_logging('mer_bills_to_deposit',$in{'id_bills'});
					$va{'message'} = &trans_txt('done');
					$in{'type'} = 'Deposit';

				}

			}else{

				$va{'message'} = &trans_txt('mer_bills_to_deposit_invalid');

			}

			### Si el bill es de gastos y se cuenta con el permiso, entonces
			### solo se cambia el tipo de documento
			if( $va{'message'} ){				
				my $sql = "SELECT COUNT(*) AS expenses FROM sl_bills_expenses WHERE id_bills = ".$in{'id_bills'}.";";
				my $sth = &Do_SQL($sql);
				my $expenses = $sth->fetchrow();
				if( int($expenses) > 0 and &check_permissions('mer_bills_to_deposit_skip_accounting','','') ){
					&Do_SQL("UPDATE sl_bills SET Type = 'Deposit' WHERE ID_bills = ".$in{'id_bills'}." AND Type = 'Bill';");
					&auth_logging('mer_bills_to_deposit', $in{'id_bills'});
					$va{'message'} = &trans_txt('done').' : Skip accounting';
					$in{'type'} = 'Deposit';
				}
			}

		}

		$va{'link_bill_to_deposit'} = $in{'type'} eq 'Bill' ? qq|<a onclick="return Confirm_to_continue();" href="/cgi-bin/mod/$usr{'application'}/dbman?cmd=$in{'cmd'}&view=$in{'id_bills'}&tab=&$in{'tab'}&todeposit=1"> \||.&trans_txt('mer_bills_to_deposit').qq|</a>| : '';
	}


	if($in{'up_amount'}){

		#sE OBTIENEN LOS DATOS DEL BILL tipo DEPOSITO		
		my ($sthb) = &Do_SQL("SELECT Amount
					FROM sl_bills
					WHERE ID_bills = ($in{'id_bills'})");
		($in{'amount_bill'}) = $sthb->fetchrow_array();
		
		#Se obtiene el monto total del Bill
		
		my ($sth2) = &Do_SQL("SELECT Amount FROM sl_bills WHERE ID_bills = $in{'bill_use'}");
		($in{'amount_bill_ap'}) = $sth2->fetchrow_array();
		
		#Se suma el monto total del Bill Deposit.
		my ($sth2) = &Do_SQL("SELECT SUM(Amount) 
					FROM sl_bills_applies 
					WHERE ID_bills_applied = $in{'bill_use'}
					 AND  ID_bills NOT IN($in{'id_bills'})");
		($in{'amount_applied'}) = $sth2->fetchrow_array();		
		$va{'total'}       = ($in{'amount_applied'}+$in{'ajaxamount'});
		$va{'amount_disp'} = $in{'amount_bill_ap'} - ($va{'total'});

		#Se suma el monto total de Depositos del Bill.
		my ($sth2) = &Do_SQL("SELECT SUM(Amount) FROM sl_bills_applies WHERE ID_bills = $in{'id_bills'}");
		($va{'total_bill'}) = $sth2->fetchrow_array();
		$va{'total_real'} = $va{'total_bill'} + $va{'total'};
		
		if($in{'ajaxamount'} <= $va{'amount_disp'} and $va{'total_real'} <= $in{'amount_bill'}){
			my ($query,@cols);
				@cols = ('Amount');
			for(0..$#cols){
				$query .= " $cols[$_]='".&filter_values($in{'ajax'.lc($cols[$_])})."',";
			}
			chop($query);
			my ($sth) = &Do_SQL("UPDATE sl_bills_applies SET $query WHERE ID_bills_applies='$in{'id_bills_apps'}'");			
			$va{'tab_messages'} = &trans_txt('bills_applied');
		}else{
			$va{'tab_messages'} = &trans_txt('bills_amount_invalid');
		}
	}

	if($in{'status'} ne 'Paid'){
		$va{'idbutton'} = &template_idbutton;
	}else {

		if ($in{'type'} ne 'Bill') {
			my ($sth) = &Do_SQL("SELECT sl_banks_movements.ID_banks, sl_banks_movements.RefNum, sl_banks_movements.ID_banks_movements
			FROM sl_banks_movrel INNER JOIN sl_banks_movements ON sl_banks_movrel.ID_banks_movements = sl_banks_movements.ID_banks_movements
			WHERE tablename = 'bills' AND tableid   = $in{'id_bills'}");
			$data = $rec = $sth->fetchrow_hashref;
			if (int($rec->{'ID_banks'}) > 0) {
				$va{'bank'} = &load_name("sl_banks","ID_banks",$rec->{'ID_banks'},"Name");
				$va{'paid_info'} = qq| <tr>
						<td width="30%" valign="top">Paid Info :</span></td>
						<td class="smalltext">
						<a href=\"/cgi-bin/mod/$usr{'application'}/dbman?cmd=fin_banks_movements&view=$rec->{'ID_banks_movements'}\">($rec->{'ID_banks_movements'}) $va{'bank'} Num. Ref: $rec->{'RefNum'}</a>
						</td>
						</tr>|;
			}
		}
	}
	
	$in{'amount'}      = &load_name("sl_bills","ID_bills",$in{'id_bills'},"Amount");
	$va{'id_vendors'} = $in{'id_vendors'};	
	$va{'vendors'} = &load_db_names('sl_vendors','ID_vendors',$in{'id_vendors'},'([ID_vendors]) [CompanyName]');
	$in{'id_vendors'} =  "<a href=\"/cgi-bin/mod/$usr{'application'}/dbman?cmd=mer_vendors&view=$in{'id_vendors'}\">$va{'vendors'}</a>";	
	if($in{'id_accounts'} and $in{'id_accounts'} ne "NULL"){
		$va{'n_accounts'} = &load_name("sl_accounts","ID_accounts",$in{'id_accounts'},"NAME");
		
		my $link_accounts = qq|<a href='javascript:trjump("/cgi-bin/mod/$usr{'application'}/dbman?cmd=fin_accounts&view=$in{'id_accounts'}")'>
		($in{'id_accounts'}) $va{'n_accounts'}</a>|;

		$va{'accounts'} = qq| <tr><td width="30%" valign="top">Account :</span></td>
					  <td class="smalltext">$link_accounts</td> </tr> |;
	}

	if ($in{'type'} eq 'Bill') {
		$va{'bill_amount_due'} = &format_price(&bills_amount_due($in{'id_bills'}));
	}
	$va{'only_nopadided'} = ($in{'type'} eq 'Bill' and $in{'status'} ne 'Paid')?'':'display:none';
	
	$in{'v_amount'} = &format_price($in{'amount'});

	$va{'display_only_internationals'} = ($in{'currency'} ne $cfg{'acc_default_currency'})? '':'display:none;';
	
	if ($in{'authby'}>0){
		$va{'authorization'} = "($in{'authby'}) " . &load_db_names('admin_users','ID_admin_users',$in{'authby'},"[FirstName] [LastName]");
	}else{
		$va{'authorization'} = "---";

		### Se valida que el bill sea de tipo PO Services y que tenga un proceso de autorización activo
		my $sth = &Do_SQL("SELECT sl_purchaseorders.ID_purchaseorders, sl_purchaseorders.`Type`, sl_bills.AuthToPay
							FROM sl_bills
								INNER JOIN sl_bills_pos ON sl_bills.ID_bills = sl_bills_pos.ID_bills
								INNER JOIN sl_purchaseorders ON sl_bills_pos.ID_purchaseorders = sl_purchaseorders.ID_purchaseorders
							WHERE sl_bills.ID_bills = ".int($in{'id_bills'}).";");
		my ($id_po, $po_type, $auth_to_pay) = $sth->fetchrow_array();
		if( $po_type and $po_type eq 'PO Services' and int($auth_to_pay) == 0 ){
			my $val = &Do_SQL("SELECT ID_vars FROM sl_vars WHERE VName = 'po_bills_auth' AND VValue = UPPER(SHA1('".int($in{'id_bills'})."'));");
			my $id_vars_exists = $val->fetchrow();
			if( $id_vars_exists > 0 ){
				$va{'authorization'} = &trans_txt('auth_in_process');
			}
		}

	}


	if ($cfg{'mod_vendors_cfdi_url'}){
		## Reescribe la conexion a Base de Datos
		&connect_db_w($cfg{'repo_db'},$cfg{'repo_host'},$cfg{'repo_user'},$cfg{'repo_pw'});
		
		my $id_xml_info_vendor = &Do_SQL("SELECT ID_xml_info_vendor FROM direksys2_repo.e".$in{'e'}."_xml_info_vendor WHERE ID_bills = $in{'id_bills'};", 1)->fetchrow();
		if ($id_xml_info_vendor){
			$va{'url_pdf'} = $cfg{'mod_vendors_cfdi_url'}."/Facturas/?e=$in{'e'}&action=showPDF&id_invoices=$id_xml_info_vendor";
			$va{'url_pdf'} = qq|<a href="$va{'url_pdf'}" target="_blank"><img src="/sitimages/default/pdf.gif" title="PDF" alt="PDF" border="0"></a>|;
		}
	}

}


sub update_amount_bill{
# --------------------------------------------------------
	my ($idbills) = @_;
	
	my ($sth) = &Do_SQL("UPDATE sl_bills  SET Amount = (SELECT IFNULL((SELECT SUM(sl_bills_pos.Amount) FROM sl_bills_pos WHERE ID_bills = '$idbills'),0)) WHERE ID_bills = '$idbills' LIMIT 1;");
}

sub bill_status{
# --------------------------------------------------------
	my ($output);

	if (&check_permissions('mer_bills_actions','','')){
		if ($in{'type'} eq 'Bill') {
			
			# Detectamos si es un Bill de Expenses
			my ($sth) = &Do_SQL("SELECT SUM(sl_bills_expenses.Amount)Amount, COUNT(*)AS nlines FROM sl_bills INNER JOIN sl_bills_expenses USING(ID_bills) WHERE ID_bills='$in{'id_bills'}';");
			my ($amount_lines, $no_lines) = $sth->fetchrow_array();
			
			if ($no_lines > 0 and $in{'status'} eq 'New' ){
				$output = qq|<a href='/cgi-bin/mod/[ur_application]/dbman?cmd=$in{'cmd'}&view=$in{'view'}&to_process=1' onclick="return Confirm_to_continue()"><img src='[va_imgurl]/[ur_pref_style]/b_ok.png' title='Auth' alt='Process' border='0'></a>|;
			}elsif($no_lines > 0 and $in{'status'} eq 'Pending'){
				$output = qq|<a href='/cgi-bin/mod/[ur_application]/dbman?cmd=$in{'cmd'}&view=$in{'view'}&to_process=1' onclick="return Confirm_to_continue()"><img src='[va_imgurl]/[ur_pref_style]/b_ok.png' title='Auth' alt='Process' border='0'><img src='[va_imgurl]/[ur_pref_style]/b_ok.png' title='Auth' alt='Process' border='0'></a>|;
			}elsif($in{'status'} eq 'New' and $in{'amount'} > 0){
				$output = qq|<a href='/cgi-bin/mod/[ur_application]/dbman?cmd=$in{'cmd'}&view=$in{'view'}&to_process=1' onclick="return Confirm_to_continue()"><img src='[va_imgurl]/[ur_pref_style]/b_ok.png' title='Auth' alt='Process' border='0'></a>|;
			}elsif($in{'status'} eq 'Pending' and $in{'amount'} > 0){
				$output = qq|<a href='/cgi-bin/mod/[ur_application]/dbman?cmd=$in{'cmd'}&view=$in{'view'}&to_process=1' onclick="return Confirm_to_continue()"><img src='[va_imgurl]/[ur_pref_style]/b_ok.png' title='Auth' alt='Process' border='0'><img src='[va_imgurl]/[ur_pref_style]/b_ok.png' title='Auth' alt='Process' border='0'></a>|;
			}elsif($in{'status'} eq 'Processed' and $in{'amount'} > 0){
				$output = qq|<a href='/cgi-bin/mod/[ur_application]/admin?cmd=mer_bills_payments&id_vendors=$va{'id_vendors'}' onclick="return Confirm_to_continue()"><img src='[va_imgurl]/[ur_pref_style]/b_cauth.gif' title='Pay' alt='Pay' border='0'></a>|;
			}

			### Revisamos si el Bill es de un PO de Servicios
			if( int($cfg{'default_auth_bill'}) == 0 ){
				my $sth = &Do_SQL("SELECT sl_purchaseorders.`Type`
									FROM sl_bills_pos
										INNER JOIN sl_purchaseorders ON sl_bills_pos.ID_purchaseorders = sl_purchaseorders.ID_purchaseorders
									WHERE sl_bills_pos.ID_bills =".$in{'id_bills'}.";");
				my $po_type = $sth->fetchrow();
				if( $po_type and $po_type eq 'PO Services' ){
					if( ($in{'status'} eq 'New' or $in{'status'} eq 'Processed') and $in{'amount'} > 0 ){
						$output = '';
					}
				}
			}

		}elsif (($in{'type'} eq 'Deposit' or $in{'type'} eq 'Debit') and $in{'amount'} > 0) {
			if($in{'status'} eq 'New'){
				$output = qq|<a href='/cgi-bin/mod/[ur_application]/dbman?cmd=$in{'cmd'}&view=$in{'view'}&to_process=1' onclick="return Confirm_to_continue()"><img src='[va_imgurl]/[ur_pref_style]/b_ok.png' title='Auth' alt='Process' border='0'></a>|;
			}elsif($in{'status'} eq 'Pending'){
				$output = qq|<a href='/cgi-bin/mod/[ur_application]/dbman?cmd=$in{'cmd'}&view=$in{'view'}&to_process=1' onclick="return Confirm_to_continue()"><img src='[va_imgurl]/[ur_pref_style]/b_ok.png' title='Auth' alt='Process' border='0'><img src='[va_imgurl]/[ur_pref_style]/b_ok.png' title='Auth' alt='Process' border='0'></a>|;
			}elsif($in{'status'} =~ /Processed|Partly Paid/ ){
				$output = qq|<a href='/cgi-bin/mod/[ur_application]/admin?cmd=mer_bills_dd_payments&id_vendors=$va{'id_vendors'}' onclick="return Confirm_to_continue()"><img src='[va_imgurl]/[ur_pref_style]/b_cauth.gif' title='Pay' alt='Pay' border='0'></a>|;
			}elsif($in{'status'} eq 'Paid'){
				my ($sth) = &Do_SQL("SELECT (Amount - (SELECT IFNULL(SUM(Amount),0)as Amount FROM sl_bills_applies WHERE ID_bills = sl_bills.ID_bills))as AmountAvailable FROM sl_bills WHERE 1 AND ID_bills = '".$in{'view'}."';");
				my ($amount_available) = $sth->fetchrow_array();
				if ($amount_available > 0) {
					$output = qq|<a href='/cgi-bin/mod/[ur_application]/admin?cmd=mer_bills_payments&id_vendors=$va{'id_vendors'}' onclick="return Confirm_to_continue()"><img src='[va_imgurl]/[ur_pref_style]/b_ok.png' title='Apply' alt='Apply' border='0'></a>|;
				}

			}
		}else {
			if($in{'status'} eq 'New' and $in{'amount'} > 0){
				$output = qq|<a href='/cgi-bin/mod/[ur_application]/dbman?cmd=$in{'cmd'}&view=$in{'view'}&to_process=1' onclick="return Confirm_to_continue()"><img src='[va_imgurl]/[ur_pref_style]/b_ok.png' title='Auth' alt='Process' border='0'></a>|;
			}elsif($in{'status'} eq 'Pending' and $in{'amount'} > 0){
				$output = qq|<a href='/cgi-bin/mod/[ur_application]/dbman?cmd=$in{'cmd'}&view=$in{'view'}&to_process=1' onclick="return Confirm_to_continue()"><img src='[va_imgurl]/[ur_pref_style]/b_ok.png' title='Auth' alt='Process' border='0'><img src='[va_imgurl]/[ur_pref_style]/b_ok.png' title='Auth' alt='Process' border='0'></a>|;
			}elsif($in{'status'} =~ /Processed|Partly Paid/ and $in{'amount'} > 0){
				$output = qq|<a href='/cgi-bin/mod/[ur_application]/admin?cmd=mer_bills_payments&id_vendors=$va{'id_vendors'}' onclick="return Confirm_to_continue()"><img src='[va_imgurl]/[ur_pref_style]/b_ok.png' title='Apply' alt='Apply' border='0'></a>|;
			}
		}
	}

	return $output;
}
#############################################################################
#############################################################################
#   Function: validate_mer_bills
#       Es: Procesa datos de sl_bills antes de ser editados
#       En: 
#
#    Created on: 26/03/2013
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
sub validate_mer_bills {
# --------------------------------------------------------
	my ($err);
	
	$in{'currency'} = &load_name("sl_vendors","ID_vendors",$in{'id_vendors'},"Currency");
	$in{'paymentmethod'} = &load_name("sl_vendors","ID_vendors",$in{'id_vendors'},"PaymentMethod");
	delete($in{'currency_exchange'}) if ($cfg{'acc_default_currency'} eq $in{'currency'});
	if (!$in{'currency_exchange'} and $cfg{'acc_default_currency'} ne $in{'currency'}) {
	 	$error{'currency_exchange'} = &trans_txt('required');
	 	++$err;
	}

	if ($in{'add'}){

		##############################
		##############################
		##############################
		#####
		##### 1) New
		#####
		##############################
		##############################
		##############################

		$in{'status'} = 'New';

	}else{

		##############################
		##############################
		##############################
		#####
		##### 2) Edit
		#####
		##############################
		##############################
		##############################

		my $sth2=&Do_SQL("SELECT * FROM sl_bills WHERE ID_bills='".$in{'id_bills'}."';");
		my $rec=$sth2->fetchrow_hashref;

		## Validamos si este movimiento es editable
		if ($in{'status'} and $in{'status'} eq 'Paid' and $in{'id_bills'}) {

			$in{'amount'}=$rec->{'Amount'};
			$in{'id_accounts'}=$rec->{'ID_accounts'};
			$in{'terms'}=$rec->{'Terms'};
			$in{'status'}=$rec->{'Status'};
			$in{'type'}=$rec->{'Type'};
			$in{'id_vendors'}=$rec->{'ID_vendors'};
			$in{'currency'}=$rec->{'Currency'};

		}elsif ($in{'id_bills'} and ($in{'type'} eq 'Deposit' or $in{'type'} eq 'Credit') ) {

			my ($sth) = &Do_SQL("SELECT ifnull(Amount,0)Amount, ID_accounts, Status
				,(select count(*) from sl_banks_movrel where tablename='bills' and tableid=sl_bills.ID_bills)billsmovrel
				,(select count(*) from sl_bills_pos where ID_bills=sl_bills.ID_bills)billspos
				,(select count(*) from sl_bills_applies where ID_bills=sl_bills.ID_bills)billsapplies
				FROM sl_bills WHERE ID_bills='$in{'id_bills'}'; ");
			my ($amount, $id_accounts, $status, $billsmovrel, $billspos, $billsapplies) = $sth->fetchrow_array();

			if ($billsapplies > 0) {
				$in{'amount'}=$rec->{'Amount'};
				$in{'id_accounts'}=$rec->{'ID_accounts'};
				$in{'terms'}=$rec->{'Terms'};
				$in{'status'}=$rec->{'Status'};
				$in{'type'}=$rec->{'Type'};
				$in{'id_vendors'}=$rec->{'ID_vendors'};
				$in{'currency'}=$rec->{'Currency'};
			}
			
		}else {
			$in{'amount'}=$rec->{'Amount'};
			$in{'id_accounts'}=$rec->{'ID_accounts'};
			$in{'status'}=$rec->{'Status'};
		}

	}


	##############################
	##############################
	##############################
	#####
	##### 3) Invoice Validation either New/Modify
	#####
	##############################
	##############################
	##############################
	if($in{'invoice'} ne ''){

		######
		###### 3.1) Invoice validation
		######
		my $modquery = $in{'id_bills'} ? "AND ID_bills <> '". $in{'id_bills'} ."' " : '';
		my ($sth) = &Do_SQL("SELECT ID_bills FROM sl_bills WHERE ID_vendors = '". $in{'id_vendors'} ."' $modquery AND (Invoice = '". &filter_values($in{'invoice'}) ."' OR Memo LIKE '". &filter_values($in{'invoice'}) ."%');");
		my ($this_bill) = $sth->fetchrow();
		
		if($this_bill){

			######
			###### 3.1.1) Invoice Found
			######
			$error{'invoice'} = &trans_txt('invalid');
 			++$err;

		}	

	}

	return $err;
}


#############################################################################
#############################################################################
#   Function: loading_mer_bills
#
#       Es: Procesa datos de sl_bills antes de ser cargados por la accion view
#       En: 
#
#    Created on: 
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
sub loading_mer_bills {
#############################################################################
#############################################################################

	## Validamos si este movimiento es editable
	if ($in{'id_bills'} and $in{'status'} and $in{'status'} eq 'Paid') {
		$va{'restrict_type'} = ' style="display:none;" ';
		$va{'restrict_id_vendors'} = 'disabled="disabled"';
		$va{'restrict_lens_id_vendors'} = ' style="display:none;" ';
		$va{'restrict_currency'} = ' style="display:none;" ';
	}

	if ($in{'id_bills'} and ($in{'type'} eq 'Deposit' or $in{'type'} eq 'Credit') ) {
		my ($sth) = &Do_SQL("SELECT ifnull(Amount,0)Amount, ID_accounts, Status
			,(select count(*) from sl_banks_movrel where tablename='bills' and tableid=sl_bills.ID_bills)billsmovrel
			,(select count(*) from sl_bills_pos where ID_bills=sl_bills.ID_bills)billspos
			,(select count(*) from sl_bills_applies where ID_bills=sl_bills.ID_bills)billsapplies
			FROM sl_bills WHERE ID_bills='$in{'id_bills'}'; ");
		my ($amount, $id_accounts, $status, $billsmovrel, $billspos, $billsapplies) = $sth->fetchrow_array();

		if ($billsapplies > 0) {
			$va{'restrict_type'} = ' style="display:none;" ';
			$va{'restrict_id_vendors'} = 'disabled="disabled"';
			$va{'restrict_lens_id_vendors'} = ' style="display:none;" ';
			$va{'restrict_currency'} = ' style="display:none;" ';
		}
	}
}

sub bills_to_void {
#############################################################################
#############################################################################

	my ($id_bills) = @_;
	my $id_vendors = &load_name('sl_bills','ID_bills',$id_bills,'ID_vendors');
	my $status = &load_name('sl_bills','ID_bills',$id_bills,'Status');

	if ($status eq 'Partly Paid' or $status eq 'Paid'){

	}else{
		my ($sth) = &Do_SQL("SELECT ID_movements, ID_accounts, Amount, Reference, EffDate, tableused, ID_tableused, Category, Credebit, ID_segments, ID_journalentries, Status, Date, Time, ID_admin_users
			FROM sl_movements WHERE tableused='sl_bills' AND ID_tableused='$id_bills';");
		while (my $rec = $sth->fetchrow_hashref){
			if ($rec->{'ID_journalentries'} > 0){

				if ($rec->{'Credebit'} eq 'Credit'){
					# Debit required for reverse
					my ($sthd) = &Do_SQL("INSERT INTO sl_movements SET
						ID_accounts='".$rec->{'ID_accounts'}."'
						, Amount='".$rec->{'Amount'}."'
						, Reference='".$rec->{'Reference'}."'
						, EffDate='".$rec->{'EffDate'}."'
						, tableused='".$rec->{'tableused'}."'
						, ID_tableused='".$rec->{'ID_tableused'}."'
						, Category='".$rec->{'Category'}."'
						, Credebit='Debit'
						, ID_segments='".$rec->{'ID_segments'}."'
						, ID_journalentries=NULL
						, Status='Active'
						, Date=CURDATE()
						, Time=CURTIME()
						, ID_admin_users='$usr{'id_admin_users'}';");
					my ($idm_debit) = $sthd->{'mysql_insertid'};
				}elsif ($rec->{'Credebit'} eq 'Debit'){
					# Credit required for reverse
					my ($sthd) = &Do_SQL("INSERT INTO sl_movements SET
						ID_accounts='".$rec->{'ID_accounts'}."'
						, Amount='".$rec->{'Amount'}."'
						, Reference='".$rec->{'Reference'}."'
						, EffDate='".$rec->{'EffDate'}."'
						, tableused='".$rec->{'tableused'}."'
						, ID_tableused='".$rec->{'ID_tableused'}."'
						, Category='".$rec->{'Category'}."'
						, Credebit='Credit'
						, ID_segments='".$rec->{'ID_segments'}."'
						, ID_journalentries=NULL
						, Status='Active'
						, Date=CURDATE()
						, Time=CURTIME()
						, ID_admin_users='$usr{'id_admin_users'}';");
					my ($idm_credit) = $sthc->{'mysql_insertid'};
				}
			}else{
				# Delete records
				my ($sthd) = &Do_SQL("DELETE FROM sl_movements WHERE ID_movements='".$rec->{'ID_movements'}."' LIMIT 1;");
			}
		}
	}

	return;
}


#############################################################################
#############################################################################
#   Function: processed_bills_pos_adj
#
#       Es: Modifica la contabilidad para relacionar el bill con la recepción
#       En: 
#
#   Created on: 
#
#   Author: Gilberto Quirino
#
#   Modifications:
#
#	Parameters:
#
#	Returns:
#
#   See Also:
#
sub processed_bills_pos_adj {
#############################################################################
#############################################################################
	my ($id_bills, $id_vendors, $tostatus) = @_;

	if( !$tostatus or $tostatus eq 'Processed' ){
		## Ejecuta el keypoint correspondiente
		$vendor_category = &load_db_names('sl_vendors', 'ID_vendors', $id_vendors, '[Category]');
		my @params = ($id_bills);
		&accounting_keypoints('po_adj_process_'.lc($vendor_category), \@params);		

	}elsif( $tostatus eq 'New' ){
		###########################################################
		###########################################################
		## Si el cambio de status del Bill es a New
		## se modifica la contabilidad para ligarla con el
		## PO al que está ligado el Bill actual
		###########################################################
		my $qMov = "SELECT 
						sl_movements.ID_movements, 
						sl_movements.Reference
					FROM 
						sl_purchaseorders_adj
						INNER JOIN sl_bills_pos ON sl_purchaseorders_adj.ID_purchaseorders_adj = sl_bills_pos.ID_purchaseorders_adj					
						INNER JOIN sl_movements ON sl_bills_pos.ID_bills = sl_movements.ID_tablerelated
					WHERE 
					  	sl_bills_pos.ID_bills = $id_bills					
						AND sl_movements.ID_tableused = sl_purchaseorders_adj.ID_purchaseorders
						AND sl_movements.tableused = 'sl_purchaseorders' 
						AND sl_movements.ID_tablerelated = sl_bills_pos.ID_bills 
						AND sl_movements.tablerelated = 'sl_bills'
						AND sl_movements.`Status`='Active';";
		$sthMov = &Do_SQL($qMov);
		
		while ( $recMov = $sthMov->fetchrow_hashref ) {
			if( $recMov->{'Reference'} eq 'VCE' ){
				&Do_SQL("UPDATE sl_movements
			 			 SET 
			 			 	Status = 'Inactive'
			 			 WHERE
			 			 	ID_movements = ".$recMov->{'ID_movements'}.";");
			}else{
				my $id_wreceipts = substr($recMov->{'Reference'}, rindex($recMov->{'Reference'}, " "));
				my $original_reference = substr($recMov->{'Reference'}, 0, index($recMov->{'Reference'}, "-")-1);

			 	&Do_SQL("UPDATE sl_movements
			 			 SET 
			 			 	tablerelated = 'sl_wreceipts',
			 			 	ID_tablerelated = ".$id_wreceipts.",
			 			 	Reference = '".$original_reference."'
			 			 WHERE
			 			 	ID_movements = ".$recMov->{'ID_movements'}.";");
			}
		}
	}	
}

sub add_mer_bills{
	## Reescribe la conexion a Base de Datos
	&connect_db_w($cfg{'repo_db'},$cfg{'repo_host'},$cfg{'repo_user'},$cfg{'repo_pw'});

	$sql = "UPDATE direksys2_repo.e".$in{'e'}."_xml_info_vendor SET
		ID_bills = '$in{'id_bills'}',
		ID_vendors = '$in{'id_vendors'}'
	WHERE
		uuid = '$in{'invoice'}'
	LIMIT 1";
	$sth = &Do_SQL($sql, 1);
}

sub loaddefault_mer_bills{
	$va{'required'} = 1;
}

sub updated_mer_bills{
	if( $in{'invoice'} and $in{'invoice'} ne '' ){
		## Reescribe la conexion a Base de Datos
		&connect_db_w($cfg{'repo_db'},$cfg{'repo_host'},$cfg{'repo_user'},$cfg{'repo_pw'});

		$sql = "UPDATE direksys2_repo.e".$in{'e'}."_xml_info_vendor SET
			ID_bills = '$in{'id_bills'}',
			ID_vendors = '$in{'id_vendors'}'
		WHERE
			uuid = '$in{'invoice'}'
		LIMIT 1";
		$sth = &Do_SQL($sql, 1);
	}
}

#############################################################################
#############################################################################
#   Function: bills_po_services_toprocessed
#
#       Es: Contabilidad para las provisiones de los POs de Servicios cuando
#			el bill se pase a Status=Processed
#       En: 
#
#   Created on: 2017-03-17
#
#   Author: Gilberto Quirino
#
#   Modifications:
#
#	Parameters:
#
#	Returns:
#
#   See Also:
#
sub bills_po_services_toprocessed {
#############################################################################
#############################################################################
	
	my($id_bills, $id_po) = @_;

	### Se obtienen los datos necesarios del PO
	my $sth = &Do_SQL("SELECT SUM(sl_purchaseorders_items.Total) TotalPO, sl_vendors.Category, sl_vendors.ID_accounts_credit
						FROM sl_purchaseorders 
							INNER JOIN sl_purchaseorders_items ON sl_purchaseorders.ID_purchaseorders = sl_purchaseorders_items.ID_purchaseorders
							INNER JOIN sl_vendors ON sl_purchaseorders.ID_vendors = sl_vendors.ID_vendors
						WHERE sl_purchaseorders.ID_purchaseorders = ".int($id_po)."
						GROUP BY sl_purchaseorders.ID_purchaseorders;");
	my $po = $sth->fetchrow_hashref();
	my $po_amount = $po->{'TotalPO'};
	my $vendor_category = $po->{'Category'};
	my $ida_vendor_credit = $po->{'ID_accounts_credit'};

	### Se obtiene el monto total del Bill
	my $bill_amount = &load_name('sl_bills', 'ID_bills', $id_bills, 'Amount');
	$bill_amount = 0 if( !$bill_amount );

	### Calcula alguna diferencia entre el monto del Bill(pagar) y el monto original del PO(deuda)
	my $diff_amount = 0;
	if( round($po_amount, 2) != round($bill_amount, 2) ){
		$diff_amount = abs($po_amount - $bill_amount);
	}

	### Se genera la contabilidad que cancela la provision
	my $sth = &Do_SQL("SELECT sl_purchaseorders_items.Total
							, sl_purchaseorders_items.Total_edited
							, sl_purchaseorders_items.Tax_percent
							, sl_services.PurchaseID_accounts
							, sl_services.ID_services
						FROM sl_services
							INNER JOIN sl_purchaseorders_items ON sl_services.ID_services = RIGHT(sl_purchaseorders_items.ID_products, 4)							
						WHERE sl_purchaseorders_items.ID_purchaseorders = ".int($id_po).";");
	my $cont = 1;
	while( my $rec = $sth->fetchrow_hashref() ){
		my $total_amt = $rec->{'Total'};
		my $total_amt_edt = $rec->{'Total_edited'};
		my $this_diff_amt = ($rec->{'Total_edited'} > 0) ? ($rec->{'Total'} - $rec->{'Total_edited'}) : 0;
		my $tax_pct = $rec->{'Tax_percent'};

		my $id_services = $rec->{'ID_services'};
		my $ida_services = $rec->{'PurchaseID_accounts'};

		## Diferencia de MENOS
		my $this_diff_type = '';
		if( $this_diff_amt > 0 ){
			$this_diff_type = 'Credit';
		## Diferencia de MAS
		} elsif( $this_diff_amt < 0 ) {
			$this_diff_type = 'Debit';
		}
		$this_diff_amt = abs($this_diff_amt);

		# if( $this_diff_amt > 0 and $this_diff_type eq 'Credit' and $total_amt >= $diff_amount ){
		# 	$total_amt -= $diff_amount;
		# }

		## Se ejecuta el keypoint
		my @params = ($id_po, $id_bills, $total_amt, $tax_pct, $id_services, $ida_services, $ida_vendor_credit, $this_diff_amt, $this_diff_type);
		&accounting_keypoints('po_services_topay_'.$vendor_category, \@params);

		$cont++;
		$diff_amount = 0;
		# $diff_type = '';
	}

}

1;