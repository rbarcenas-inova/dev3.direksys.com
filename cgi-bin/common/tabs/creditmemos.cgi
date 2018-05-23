#!/usr/bin/perl
#####################################################################
########                   APARTS	        		           		#########
#####################################################################
sub load_tabsconf {
# --------------------------------------------------------
	if ($in{'tab'} eq 1){
		## Notes Tab
		$va{'tab_type'}  = 'notes';
		$va{'tab_title'} = &trans_txt('notes');
		$va{'tab_table'} = 'sl_creditmemos_notes';
	}elsif($in{'tab'} eq 3){
		## Notes Tab
		$va{'tab_type'}  = 'logs';
		$va{'tab_title'} = &trans_txt('logs');
		$va{'tab_table'} = 'sl_creditmemos';
	}elsif($in{'tab'} eq 6){
		## Logs Tab
		$va{'tab_type'}  = 'movs';
		$va{'tab_title'} = &trans_txt('movs');
		$va{'tab_table'} = 'sl_creditmemos';
		$va{'tab_idvalue'} = $in{'id_creditmemos'};
	}
}

#############################################################################
#############################################################################
#	Function: load_tabs2
#
#	Created on: 5/9/2013 3:14:10 PM
#
#	Author: Carlos Haas
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
sub load_tabs2 {
#############################################################################
#############################################################################
	
	my ($status) = &load_name('sl_creditmemos','ID_creditmemos',$in{'id_creditmemos'},'Status');
	$boledit = 0;
	## 1250 -> 40201001 - DEVOLUCIONES
	# my ($sth_movements) = &Do_SQL("SELECT COUNT(*)
	# 								FROM sl_movements
	# 								WHERE tableused='sl_creditmemos' 
	# 									AND ID_tableused=".$in{'id_creditmemos'}."
	# 									AND ID_accounts IN (SELECT ID_accounts FROM sl_accounts WHERE ID_accounting = '40201001');");
	# my ($mov_devol) = $sth_movements->fetchrow();
	if($status ne 'Applied'){
		$boledit = 1;
	}
	if($status eq 'New'){
		$boledit = 1;
	}
	if($boledit){
		$va{'updatebtn'} = "<input value=' ". &trans_txt('opr_creditmemos_updbtn'). "' class='button' type='submit'>";
		$va{'addorder'} = "<a href='javascript:add_order()'>Add Order</a>";
	}

	my (@c) = split(/,/,$cfg{'srcolors'});
	my ($sth) = &Do_SQL("SELECT COUNT(*) FROM sl_creditmemos_payments WHERE ID_creditmemos='".&filter_values($in{'view'})."';");

	$va{'matches'} = $sth->fetchrow;
	if ($va{'matches'}>0){

		##################
		################## START (2/2) -  Seccion con el mismo codigo que funcion view de dbman.opr.html.cgi
		################## Si se mueve logica aqui, debe revisare el otro archivo
		##################
		my ($sthp1) = &Do_SQL("SELECT SUM(Amount) FROM sl_creditmemos_payments WHERE ID_creditmemos = '$in{'id_creditmemos'}';");
		my ($sthp2) = &Do_SQL("SELECT SUM( (SalePrice * Quantity) + Tax - Discount ) FROM sl_creditmemos_products WHERE ID_creditmemos = '$in{'id_creditmemos'}';");
		my ($amt_thiscreditmemo)= $sthp1->fetchrow();
		my ($sum_thiscreditmemo)= $sthp2->fetchrow();
		(!$amt_thiscreditmemo) and ($amt_thiscreditmemo = 0);
		(!$sum_thiscreditmemo) and ($sum_thiscreditmemo = 0);

		my $max_allowed = $sum_thiscreditmemo - $amt_thiscreditmemo;
		##################
		################## END (1/2)-  Seccion con el mismo codigo que funcion view de dbman.opr.html.cgi
		##################

		(!$in{'nh'}) and ($in{'nh'}=1);
		$first = ($in{'nh'} - 1) * $usr{'pref_maxh'};			
		($va{'pageslist'},$qs) = &pages_list($in{'nh'},"/cgi-bin/mod/$usr{'application'}/dbman",$va{'matches'},$usr{'pref_maxh'});
					
		my ($sth) = &Do_SQL("SELECT sl_orders.ID_orders, sl_orders.Date,sl_orders.OrderNet, sl_orders.Status, sl_creditmemos_payments.Amount FROM sl_creditmemos_payments LEFT JOIN sl_orders ON sl_creditmemos_payments.ID_orders=sl_orders.ID_orders WHERE ID_creditmemos='".&filter_values($in{'view'})."';");
		$va{'total'} = 0;
		while ($rec = $sth->fetchrow_hashref){

			$d = 1 - $d;
			$va{'total'} += $rec->{'Amount'};

			##################
			################## START (2/2) -  Seccion con el mismo codigo que funcion view de dbman.opr.html.cgi
			################## Si se mueve logica aqui, debe revisare el otro archivo
			##################
			my ($sth1) = &Do_SQL("SELECT SUM(SalePrice + Shipping + Tax + ShpTax - Discount) FROM sl_orders_products WHERE ID_orders = '$rec->{'ID_orders'}' AND Status NOT IN('Order Cancelled','Inactive');");
			my ($sth2) = &Do_SQL("SELECT IFNULL(SUM(Amount),0) FROM sl_orders_payments WHERE ID_orders = '$rec->{'ID_orders'}' AND Reason='Sale' AND (Captured='No' OR Captured IS NULL OR Captured = '' OR CapDate IS NULL OR CapDate = '0000-00-00') AND `Status` != 'Cancelled';");
			my ($sth3) = &Do_SQL("select sum(pay.amount)
				from sl_creditmemos_payments pay
				inner join sl_creditmemos cre using(ID_creditmemos)
				where pay.id_orders='$rec->{'ID_orders'}' and cre.status='New' and cre.id_creditmemos != ".&filter_values($in{'view'}).";");
		
			my ($order_total) = $sth1->fetchrow();
			my ($order_unpaid) = $sth2->fetchrow();
			my ($amt_increditmemos) = $sth3->fetchrow();
			(!$amt_increditmemos) and ($amt_increditmemos = 0);

			if($amt_increditmemos + $max_allowed > $order_unpaid){
				$max_allowed -= round($amt_increditmemos,2);
			}

			##################
			################## END (2/2) -  Seccion con el mismo codigo que funcion view de dbman.opr.html.cgi
			##################

			if($rec->{'Amount'} - 0 == 0){


				$rec->{'Amount'} = $order_unpaid - $amt_increditmemos <= $max_allowed ? round($order_unpaid - $amt_increditmemos,2) : round($max_allowed,2);

			}
			
			## Debugging?
			#&cgierr("<br>OT: $order_total<br>UN: $order_unpaid<br>MAX: $max_allowed<br>AMT: $rec->{'Amount'}");
			$rec->{'ID_orders'} = int($rec->{'ID_orders'});
			$va{'searchresults'} .= "<tr bgcolor='$c[$d]'>\n";
			$va{'searchresults'} .= "	<td class='smalltext'>";
			$va{'searchresults'} .= "		<a href='/cgi-bin/mod/$usr{'application'}/dbman?cmd=opr_creditmemos&view=".$in{'id_creditmemos'}."&delorder=".$rec->{'ID_orders'}."&tab=2'><img src='$va{'imgurl'}/$usr{'pref_style'}/b_drop.png' title='Drop' alt='' border='0'></a>" if ($status eq 'New');
			$va{'searchresults'} .=	"	</td>\n";
			$va{'searchresults'} .= "	<td class='smalltext'><a href=\"/cgi-bin/mod/$usr{'application'}/dbman?cmd=opr_orders&view=$rec->{'ID_orders'}\">$rec->{'ID_orders'}</a></td>\n";
			if($rec->{'ID_orders'} > 0){
				$va{'searchresults'} .= "<td class='smalltext'>".&invoices_list($rec->{'ID_orders'})."</td>\n";
			} else {
				$va{'searchresults'} .= "<td class='smalltext'>&nbsp;</td>\n";
			}
			$va{'searchresults'} .= "  <td class='smalltext' align='right'>".$rec->{'Date'}."</td>\n";
			$va{'searchresults'} .= "  <td class='smalltext' align='right'>".&format_price($order_total)."</td>\n";			
			$va{'searchresults'} .= "  <td class='smalltext' align='right'>".&format_price($order_unpaid)."</td>\n";
			$va{'searchresults'} .= "  <td class='smalltext' align='right' style='color:orange;font-size:bold'>".&format_price($amt_increditmemos)."</td>\n";
			$va{'searchresults'} .= "  <td class='smalltext' align='right'>".$rec->{'Status'}."</td>\n";
			
			if ($boledit){
				$va{'searchresults'} .= qq|  <td class='smalltext' align='right'><input name="orderamount_$rec->{'ID_orders'}" style="text-align:right" value="$rec->{'Amount'}" size="20" onfocus="focusOn( this )" onblur="focusOff( this )" type="text"><span class='smallfieldterr'>|. $error{'order'.$rec->{'ID_orders'}} .qq|</span></td>\n|;
			}else{
				$va{'searchresults'} .= "  <td class='smalltext' align='right'>".&format_price($rec->{'Amount'})."</td>\n";
			}

			$va{'searchresults'} .= "</tr>\n";
		}


		if ($va{'total'} > 0) {

			$d = 1 - $d;
			$va{'searchresults'} .= "<tr bgcolor='$c[$d]'>\n";
			$va{'searchresults'} .= "  <td class='smalltext' colspan='8' align='right'>".&trans_txt('total')."  </td>\n";
			$va{'searchresults'} .= "  <td class='smalltext' align='right' style='border-top:thick double #808080;'>".&format_price($va{'total'})."</td>\n";
			$va{'searchresults'} .= "</tr>\n";
			
		}

	}else{
		$va{'pageslist'} = 1;
		$va{'searchresults'} = qq|
			<tr>
				<td colspan='6' align='center'>|.&trans_txt('search_nomatches').qq|</td>
			</tr>\n|;
	}
}

#############################################################################
#############################################################################
#	Function: load_tabs4
#
#	Created on: 5/9/2013 3:14:10 PM
#
#	Author: Carlos Haas
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
sub load_tabs4{
#############################################################################
#############################################################################
	
	my ($status) = &load_name('sl_creditmemos','ID_creditmemos',$in{'id_creditmemos'},'Status');
	my ($sth_movements) = &Do_SQL("select count(*) 
		from sl_movements
		where 
			tableused='sl_creditmemos' and id_tableused='$in{'id_creditmemos'}' and
			ID_accounts in (select id_accounts from sl_accounts where id_accounting = '10705000');");
	my ($mov_devol) = $sth_movements->fetchrow();
	if ($status eq 'New'){
		$va{'updatebtn'} = "<input value='". &trans_txt('opr_creditmemos_updbtn'). "' class='button' type='submit'>";
	}
	my (@c) = split(/,/,$cfg{'srcolors'});
	my ($sth) = &Do_SQL("SELECT COUNT(*) FROM sl_creditmemos_products WHERE ID_creditmemos='".&filter_values($in{'view'})."';");
	$va{'matches'} = $sth->fetchrow;
	if ($va{'matches'}>0){
		#&cgierr("SELECT * FROM sl_creditmemos_products WHERE ID_creditmemos='".&filter_values($in{'view'})."';");
		my ($sth) = &Do_SQL("SELECT * FROM sl_creditmemos_products WHERE Status='Active' AND ID_creditmemos='".&filter_values($in{'view'})."';");
		$va{'total'} = 0;
		while ($rec = $sth->fetchrow_hashref){
			$d = 1 - $d;
			my ($line_tax);
			#Cuando el estatus es New, se puede editar cualquier registro de productos
			if ($status eq 'New' and &check_permissions('opr_creditmemos_products_edit','','')){
				$va{'searchresults'} .= "<tr bgcolor='$c[$d]'>\n";
				#$va{'searchresults'} .= "  <td class='smalltext'></td>";
				#$va{'searchresults'} .= "  <td class='smalltext'>";
				#$va{'searchresults'} .= " <a href='/cgi-bin/mod/$usr{'application'}/dbman?cmd=opr_creditmemos&view=".$in{'id_creditmemos'}."&delprod=".$rec->{'ID_creditmemos_products'}."&tab=4'><img src='$va{'imgurl'}/$usr{'pref_style'}/b_drop.png' title='Drop' alt='' border='0'></a></td>\n";
				if (substr($rec->{'ID_products'},0,1) eq 4){
					$va{'searchresults'} .= "  <td class='smalltext' valign='top'><a href=\"/cgi-bin/mod/$usr{'application'}/dbman?cmd=mer_parts&view=".($rec->{'ID_products'}-400000000)."\">". &format_sltvid($rec->{'ID_products'})."</a></td>\n";
					$va{'searchresults'} .= "  <td class='smalltext' valign='top'>".&load_db_names('sl_parts','ID_parts',$rec->{'ID_products'}-400000000,'[Name]<br>[Model]')."</td>\n";
					$line_tax = (($rec->{'SalePrice'}*$rec->{'Quantity'})-$rec->{'Discount'})*$rec->{'Tax_percent'}/100;
					$line_tax += $rec->{'Shipping'} * $rec->{'ShpTax_percent'}/100 if ($cfg{'shptax'});
				}else{
					$va{'searchresults'} .= "  <td class='smalltext'><a href=\"/cgi-bin/mod/$usr{'application'}/dbman?cmd=mer_services&view=".($rec->{'ID_products'}-600000000)."\">$rec->{'ID_products'}</a></td>\n";
					$va{'searchresults'} .= "  <td class='smalltext'>".&load_name('sl_services','ID_services',$rec->{'ID_products'}-600000000,'Name')."</td>\n";
					$line_tax = $rec->{'Tax'};
				}
				$va{'searchresults'} .= qq|  <td class='smalltext' align='right'><input name="prods_qty_$rec->{'ID_creditmemos_products'}" style="text-align:right" value="$rec->{'Quantity'}" size="5" onfocus="focusOn( this )" onblur="focusOff( this )" type="text"><span class='smallfieldterr'>$error{'prods_qty_'.$rec->{'ID_creditmemos_products'}}</span></td>\n|;
				$va{'searchresults'} .= qq|  <td class='smalltext' align='right'><input name="prods_saleprice_$rec->{'ID_creditmemos_products'}" style="text-align:right" value="$rec->{'SalePrice'}" size="10" onfocus="focusOn( this )" onblur="focusOff( this )" type="text"><span class='smallfieldterr'>$error{'prods_saleprice_'.$rec->{'ID_creditmemos_products'}}</span></td>\n|;
				if (substr($rec->{'ID_products'},0,1) eq 4){
					$va{'searchresults'} .= qq|  <td class='smalltext' align='right'><input name="prods_discount_$rec->{'ID_creditmemos_products'}" style="text-align:right" value="$rec->{'Discount'}" size="10" type="text"></td>\n|;
					$va{'searchresults'} .= qq|  <td class='smalltext' align='right'><input name="prods_shipping_$rec->{'ID_creditmemos_products'}" style="text-align:right" value="$rec->{'Shipping'}" size="10" onfocus="focusOn( this )" onblur="focusOff( this )" type="text"><span class='smallfieldterr'>$error{'prods_shipping_'.$rec->{'ID_creditmemos_products'}}</span><input name="prods_cost_$rec->{'ID_creditmemos_products'}" style="text-align:right" value="$rec->{'Cost'}" size="10" onfocus="focusOn( this )" onblur="focusOff( this )" type="hidden"></td>\n|;
					#$va{'searchresults'} .= qq|  <td class='smalltext' align='right'><span class='smallfieldterr'>$error{'prods_cost_'.$rec->{'ID_creditmemos_products'}}</span></td>\n|;
				}else{
					$va{'searchresults'} .= qq|  <td class='smalltext' align='right'><input name="prods_discount_$rec->{'ID_creditmemos_products'}" style="text-align:right" value="$rec->{'Discount'}" size="10" type="text"></td>\n|;
					$va{'searchresults'} .= qq|  <td class='smalltext' align='right'><input name="prods_shipping_$rec->{'ID_creditmemos_products'}" style="text-align:right" value="$rec->{'Shipping'}" type="hidden">---<input name="prods_cost_$rec->{'ID_creditmemos_products'}" style="text-align:right" value="$rec->{'Cost'}" type="hidden"></td>\n|;
					#$va{'searchresults'} .= qq|  <td class='smalltext' align='right'>---</td>\n|;
				}
				$va{'searchresults'} .= "  <td class='smalltext' align='right'>".&format_price($line_tax)." ($rec->{'Tax_percent'} %)</td>\n";
				$va{'total'} = (($rec->{'Quantity'}*$rec->{'SalePrice'})-$rec->{'Discount'}) + $line_tax + $rec->{'Shipping'} ;
				$va{'searchresults'} .= "  <td class='smalltext' align='right'>".&format_price($va{'total'})."</td>\n";
				$va{'searchresults'} .= "</tr>\n";
			}else{
				$va{'searchresults'} .= "<tr bgcolor='$c[$d]'>\n";
				#$va{'searchresults'} .= "  <td class='smalltext'></td>\n";
				if (substr($rec->{'ID_products'},0,1) eq 4){
					$va{'searchresults'} .= "  <td class='smalltext' valign='top'><a href=\"/cgi-bin/mod/$usr{'application'}/dbman?cmd=mer_parts&view=".($rec->{'ID_products'}-400000000)."\">".&format_sltvid($rec->{'ID_products'})."</a></td>\n";
					$va{'searchresults'} .= "  <td class='smalltext' valign='top'>".&load_db_names('sl_parts','ID_parts',$rec->{'ID_products'}-400000000,'[Name]<br>[Model]')."</td>\n";
					$line_tax = (($rec->{'SalePrice'}*$rec->{'Quantity'})-$rec->{'Discount'})*$rec->{'Tax_percent'}/100;
					$line_tax += $rec->{'Shipping'} * $rec->{'ShpTax_percent'}/100 if ($cfg{'shptax'});
				}else{
					$va{'searchresults'} .= "  <td class='smalltext'><a href=\"/cgi-bin/mod/$usr{'application'}/dbman?cmd=mer_services&view=".($rec->{'ID_products'}-600000000)."\">".&format_sltvid($rec->{'ID_products'})."</a></td>\n";
					$va{'searchresults'} .= "  <td class='smalltext'>".&load_name('sl_services','ID_services',$rec->{'ID_products'}-600000000,'Name')."</td>\n";
					$line_tax = $rec->{'Tax'};
				}
				$va{'searchresults'} .= qq|  <td class='smalltext' align='right'>$rec->{'Quantity'}</td>\n|;
				$va{'searchresults'} .= qq|  <td class='smalltext' align='right'>|. &format_price($rec->{'SalePrice'}). qq|</td>\n|;

				$va{'searchresults'} .= qq|  <td class='smalltext' align='right'>|. &format_price($rec->{'Discount'}). qq|</td>\n|;

				$va{'searchresults'} .= qq|  <td class='smalltext' align='right'>|. &format_price($rec->{'Shipping'}).qq|</td>\n|;
				#$va{'searchresults'} .= qq|  <td class='smalltext' align='right'>|. &format_price($rec->{'Cost'}).qq|</td>\n|;
				$va{'searchresults'} .= "  <td class='smalltext' align='right'>".&format_price($line_tax)." ($rec->{'Tax_percent'} %)</td>\n";
				$va{'total'} = (($rec->{'Quantity'}*$rec->{'SalePrice'})-$rec->{'Discount'}) + $line_tax + $rec->{'Shipping'};
				$va{'searchresults'} .= "  <td class='smalltext' align='right'>".&format_price($va{'total'})."</td>\n";
				$va{'searchresults'} .= "</tr>\n";
				if (substr($rec->{'ID_products'},0,1) eq 4){
					$rec->{'ShpDate'} = '---' if (!$rec->{'ShpDate'});
					$va{'searchresults'} .= "<tr bgcolor='$c[$d]'>\n";
					#$va{'searchresults'} .= "  <td class='smalltext'>&nbsp;</td>\n";
					if($rec->{'ShpDate'} == '---'){
						$va{'searchresults'} .= qq|  <td class='smalltext' colspan="8">|.&trans_txt('recepinfo').qq| : <span style='color:red'>In Transit</span></td>\n|;
					}else{
						$va{'searchresults'} .= qq|  <td class='smalltext' colspan="8">|.&trans_txt('recepinfo').qq| : $rec->{'ShpDate'}</td>\n|;
					}

					$va{'searchresults'} .= "</tr>\n";
				}
			}
			$cm_total+=$va{'total'};
		}
		if ($va{'total'} > 0) {
			$va{'searchresults'} .= "<tr bgcolor='$c[$d]'>\n";
			$va{'searchresults'} .= "  <td class='smalltext' colspan='7' align='right'>Total </td>\n";
			$va{'searchresults'} .= "  <td class='smalltext' align='right' style='border-top:thick double #808080;'>".&format_price($cm_total)."</td>\n";
			$va{'searchresults'} .= "</tr>\n";
		}

	}else{
		$va{'pageslist'} = 1;
		$va{'searchresults'} = qq|
			<tr>
				<td colspan='8' align='center'>|.&trans_txt('search_nomatches').qq|</td>
			</tr>\n|;
	}
}

#############################################################################
#############################################################################
#   Function: load_tabs13
#
#       Es: Muestra los Invoices relacionados a la orden.
#
#
#    Created on: 30/01/2013 18:00:00
#
#    Author: Enrique Peña
#
#    Modifications: ADG-10/06/2013-Se agrega boton Nota de Credito
#
#   Parameters:
#
#  Returns:
#
#   See Also: export_info_for_invoices()
#
#
#
sub load_tabs5 {
#############################################################################
#############################################################################

	## Process Invoice/Credit Note
	if ($in{'creditnote'}) {
		## Validacion NO se puede generar Nota de Credito sin tener la devolucion previamente en el almacen
		my ($this_res, $this_message) = &creditmemos_return_validation($in{'id_creditmemos'});
		if ($this_res !~ /ok/i){
				$va{'tabmessages'} = ($va{'tabmessages'} eq '')?&trans_txt('incomplete_return_in_cm').'::'.$this_res.'::'.$this_message :"<br>".&trans_txt('incomplete_return_in_cm');
		}else{
			if (&check_permissions('creditmemos_toinvoice','','')) {

				&Do_SQL("START TRANSACTION;");
				my $status;

				# Generate Credit Note
				($va{'tabmessages'}, $status) = &export_info_for_credits_notes($in{'id_creditmemos'});

				if ($status =~ /OK/i){
					&Do_SQL("COMMIT;");
					# &Do_SQL("ROLLBACK;"); ## Only debug
				}else{
					&Do_SQL("ROLLBACK;");
				}

			}else {
				$va{'tabmessages'} = &trans_txt('unauth_action');
			}
		}
	}

	my (@c) = split(/,/,$cfg{'srcolors'});
	my ($sth) = &Do_SQL("SELECT COUNT(*) FROM (SELECT 1 FROM cu_invoices_lines INNER JOIN cu_invoices USING(ID_invoices) WHERE ID_creditmemos = '$in{'id_creditmemos'}' GROUP BY ID_invoices)AS invoices");
	$va{'matches'} = $sth->fetchrow();
	$va{'geninvoice'} = '';
	
	if ($va{'matches'} > 0){
		(!$in{'nh'}) and ($in{'nh'}=1);
		$first = ($in{'nh'} - 1) * $usr{'pref_maxh'};			
		($va{'pageslist'},$qs) = &pages_list($in{'nh'},"/cgi-bin/mod/$usr{'application'}/dbman",$va{'matches'},$usr{'pref_maxh'});
		$sth = &Do_SQL("SELECT CONCAT(doc_serial,doc_num) AS invoice, cu_invoices.ID_invoices,ID_customers,ID_creditmemos,CONCAT(customer_fcode,' ',customer_fname) AS NAME, cu_invoices.Status,cu_invoices.Date, doc_serial, doc_num
				, UPPER(invoice_type) AS invoice_type
				, cu_invoices.invoice_total
				FROM cu_invoices_lines
				INNER JOIN cu_invoices ON cu_invoices.ID_invoices = cu_invoices_lines.ID_invoices
				WHERE ID_creditmemos = '$in{'id_creditmemos'}'
				GROUP BY ID_invoices
				ORDER BY ID_invoices DESC LIMIT $first,$usr{'pref_maxh'};");
		while ($rec = $sth->fetchrow_hashref){
			$d = 1 - $d;
			
			# my $pdf_name = $rec->{'doc_serial'}.'_'.$rec->{'doc_num'};
			# my $link_pdf = "/cfdi/pages/cfdi/cfdi_doc.php?f=".$pdf_name.".pdf";
			my $link_pdf = "/finkok/Facturas/?action=showPDF&id_invoices=$rec->{'ID_invoices'}&e=".$in{'e'};
			my $link_xml = "/finkok/Facturas/?action=downloadXML&id_invoices=$rec->{'ID_invoices'}&e=".$in{'e'};
			$va{'searchresults'} .= "<tr bgcolor='$c[$d]'>\n";
			$va{'searchresults'} .= "   <td class='smalltext'>";
			if($rec->{'Status'} eq 'Certified' or $rec->{'Status'} eq 'Cancelled'){
				$va{'searchresults'} .= "   <a href='$link_pdf' target='_blank'><img src='[va_imgurl]/[ur_pref_style]/pdf.gif' title='Verd PDF' alt='PDF' border='0'></a>&nbsp;";
				$va{'searchresults'} .= "   <a href='$link_xml' target='_blank'><img src='[va_imgurl]/[ur_pref_style]/xml_dwd.gif' title='Descargar XML' alt='XML' border='0' style='width: 18px;'></a>";
			}
			$va{'searchresults'} .= "   </td>";
									"   <td class='smalltext'></td>\n";
			$va{'searchresults'} .= "   <td class='smalltext'><a href=\"/cgi-bin/mod/$usr{'application'}/dbman?cmd=opr_invoices&view=$rec->{'ID_invoices'}\">$rec->{'ID_invoices'}</a></td>\n";
			$va{'searchresults'} .= "   <td class='smalltext'>$rec->{'invoice'}</td>\n";
			$va{'searchresults'} .= "   <td class='smalltext'>$rec->{'invoice_type'}</td>\n";
			$va{'searchresults'} .= "   <td class='smalltext'><a href=\"/cgi-bin/mod/$usr{'application'}/dbman?cmd=opr_customers&view=$rec->{'ID_customers'}\">($rec->{'ID_customers'}) $rec->{'NAME'}</a></td>\n";			
			$va{'searchresults'} .= "   <td class='smalltext' style='text-align: right;'>".&format_price($rec->{'invoice_total'})."</td>\n";
			$va{'searchresults'} .= "   <td class='smalltext'>$rec->{'Status'}</td>\n";
			$va{'searchresults'} .= "   <td class='smalltext'>$rec->{'Date'}</td>\n";
			$va{'searchresults'} .= "</tr>\n";
		}
	}else{
		
		$va{'pageslist'} = 1;
		$va{'searchresults'} = qq|
			<tr>
				<td colspan='6' align='center'>|.&trans_txt('search_nomatches').qq|</td>
			</tr>\n|;		
	}
	
	my ($sth_upc) = &Do_SQL("SELECT ID_orders_products,
					IF(RIGHT(sl_orders_products.ID_products,6)=000000,Related_ID_products,sl_orders_products.ID_products)AS ID_products
					,sl_skus.ID_sku_products AS ID_sku
					,if(sl_customers_parts.sku_customers is null, sl_skus.UPC,sl_customers_parts.sku_customers) AS ID_sku_alias
					,sl_skus.UPC as UPC
					FROM sl_orders_products
					LEFT JOIN sl_customers_parts ON sl_customers_parts.ID_parts=SUBSTR(sl_orders_products.Related_ID_products,2,8)*1 
					LEFT JOIN sl_skus ON sl_skus.ID_sku_products=sl_orders_products.Related_ID_products
					WHERE ID_orders = '".$in{'id_creditmemos'}."' 
					  AND sl_orders_products.Status IN('Active') 
					  AND sl_orders_products.SalePrice >= 0
					GROUP BY IF(Related_ID_products IS NULL,sl_orders_products.ID_products,Related_ID_products);");
	my ($rec_upc);
	my $invalid_upc = 0;
	while ($rec_upc = $sth_upc->fetchrow_hashref) {
		if ($rec_upc->{'UPC'} eq '') {
			$invalid_upc = 1;
			if ($rec_upc->{'ID_products'}>=600000000) {
				$invalid_upc = 0;
			}
			
		}
		
	}
	
	## Validacion NO se puede generar Nota de Credito si el Status no es Applied
	my ($status) = &load_name('sl_creditmemos','ID_creditmemos',$in{'id_creditmemos'},'Status');
	## Con excepcion de los CMs de Mercancía
	my $sql_cm_prod = "SELECT SUM(SalePrice) TotalAmt FROM sl_creditmemos_products WHERE ID_creditmemos = ".$in{'id_creditmemos'}." AND `Status` = 'Active' AND ID_products > 400000000 AND ID_products < 600000000;";
	my $sth_cm_prod = &Do_SQL($sql_cm_prod);
	my $total_amt_prods = $sth_cm_prod->fetchrow();

	if ($status eq 'Applied' or ($status eq 'Approved' and $total_amt_prods > 0)){
		$va{'geninvoice'} .= qq|&nbsp;&nbsp;<a onclick="return confirm_continue();" href="/cgi-bin/mod/|.$usr{'application'}.qq|/dbman?cmd=|.$in{'cmd'}.qq|&view=|.$in{'view'}.qq|&tab=|.$in{'tab'}.qq|&creditnote=1">|.&trans_txt('opr_orders_generate_creditnote').qq|</a>|;
	}else{
		$va{'geninvoice'} = '';
	}

}


1;