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
		$va{'tab_table'} = 'sl_debitmemos_notes';
	}elsif($in{'tab'} eq 3){
		## Notes Tab
		$va{'tab_type'}  = 'logs';
		$va{'tab_title'} = &trans_txt('logs');
		$va{'tab_table'} = 'sl_debitmemos';
	}elsif($in{'tab'} eq 6){
		## Logs Tab
		$va{'tab_type'}  = 'movs';
		$va{'tab_title'} = &trans_txt('movs');
		$va{'tab_table'} = 'sl_debitmemos';
		$va{'tab_idvalue'} = $in{'id_debitmemos'};
	}
}

#############################################################################
#############################################################################
#	Function: load_tabs2
#
#	Created on: 29/11/2013
#
#	Author: Oscar Maldonado
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
	
	my ($status) = &load_name('sl_debitmemos','ID_debitmemos',$in{'id_debitmemos'},'Status');
	if ($status eq 'New'){
		$va{'updatebtn'} = "<input value='". &trans_txt('opr_debitmemos_updbtn'). "' class='button' type='submit'>";
	}
	my (@c) = split(/,/,$cfg{'srcolors'});
	my ($sth) = &Do_SQL("SELECT COUNT(*) FROM sl_debitmemos_payments WHERE ID_debitmemos='".&filter_values($in{'view'})."';");

	$va{'matches'} = $sth->fetchrow;
	if ($va{'matches'}>0){
		(!$in{'nh'}) and ($in{'nh'}=1);
		$first = ($in{'nh'} - 1) * $usr{'pref_maxh'};			
		($va{'pageslist'},$qs) = &pages_list($in{'nh'},"/cgi-bin/mod/$usr{'application'}/dbman",$va{'matches'},$usr{'pref_maxh'});
					
		my ($sth) = &Do_SQL("SELECT sl_orders.ID_orders, sl_orders.Date,sl_orders.OrderNet, sl_orders.Status, sl_debitmemos_payments.Amount FROM sl_debitmemos_payments LEFT JOIN sl_orders ON sl_debitmemos_payments.ID_orders=sl_orders.ID_orders WHERE ID_debitmemos='".&filter_values($in{'view'})."';");
		$va{'total'} = 0;
		while ($rec = $sth->fetchrow_hashref){
			$d = 1 - $d;
			$va{'total'} += $rec->{'Amount'};

			$va{'searchresults'} .= "<tr bgcolor='$c[$d]'>\n";
			$va{'searchresults'} .= "  <td class='smalltext'>";
				$va{'searchresults'} .= "<a href='/cgi-bin/mod/$usr{'application'}/dbman?cmd=opr_debitmemos&view=".$in{'id_debitmemos'}."&delorder=".$rec->{'ID_orders'}."&tab=2'><img src='$va{'imgurl'}/$usr{'pref_style'}/b_drop.png' title='Drop' alt='' border='0'></a>" if ($status eq 'New');
				$va{'searchresults'} .=	"</td>\n";
			$va{'searchresults'} .= "  <td class='smalltext'><a href=\"/cgi-bin/mod/$usr{'application'}/dbman?cmd=opr_orders&view=$rec->{'ID_orders'}\">$rec->{'ID_orders'}</a></td>\n";
			$va{'searchresults'} .= "  <td class='smalltext'>".$rec->{'Date'}."</td>\n";
			$va{'searchresults'} .= "  <td class='smalltext'>".&format_price($rec->{'OrderNet'})."</td>\n";
			my ($sth2) = &Do_SQL("SELECT SUM(Amount) FROM sl_orders_payments WHERE ID_orders='$rec->{'ID_orders'}' AND Amount>0 AND (Captured='No' OR Captured IS NULL);");
			$va{'searchresults'} .= "  <td class='smalltext'>".&format_price($sth2->fetchrow())."</td>\n";
			$va{'searchresults'} .= "  <td class='smalltext'>".&invoices_list($rec->{'ID_orders'})."</td>\n";
			$va{'searchresults'} .= "  <td class='smalltext'>".$rec->{'Status'}."</td>\n";
			if ($status eq 'New'){
				$va{'searchresults'} .= qq|  <td class='smalltext' align='right'><input name="orderamount_$rec->{'ID_orders'}" style="text-align:right" value="$rec->{'Amount'}" size="20" onfocus="focusOn( this )" onblur="focusOff( this )" type="text"><span class='smallfieldterr'>$error{'order'.$rec->{'ID_orders'}}</span></td>\n|;
			}else{
				$va{'searchresults'} .= "  <td class='smalltext' align='right'>".&format_price($rec->{'Amount'})."</td>\n";
			}
			$va{'searchresults'} .= "</tr>\n";
		}
		if ($va{'total'} > 0) {
			$d = 1 - $d;
			$va{'searchresults'} .= "<tr bgcolor='$c[$d]'>\n";
			$va{'searchresults'} .= "  <td class='smalltext' colspan='7' align='right'>".&trans_txt('total')."  </td>\n";
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
#	Created on: 29/11/2013
#
#	Author: Oscar Maldonado
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
	
	my ($status) = &load_name('sl_debitmemos','ID_debitmemos',$in{'id_debitmemos'},'Status');
	if ($status eq 'New'){
		$va{'updatebtn'} = "<input value='". &trans_txt('opr_debitmemos_updbtn'). "' class='button' type='submit'>";
	}
	my (@c) = split(/,/,$cfg{'srcolors'});
	my ($sth) = &Do_SQL("SELECT COUNT(*) FROM sl_debitmemos_products WHERE ID_debitmemos='".&filter_values($in{'view'})."';");

	$va{'matches'} = $sth->fetchrow;
	if ($va{'matches'}>0){
				
		my ($sth) = &Do_SQL("SELECT * FROM sl_debitmemos_products WHERE ID_debitmemos='".&filter_values($in{'view'})."';");
		$va{'total'} = 0;
		while ($rec = $sth->fetchrow_hashref){
			#cgierr($rec->{'Tax_percent'});
			$d = 1 - $d;
			$va{'total'} += $rec->{'Amount'};
			my ($line_tax);
			if ($status eq 'New'){
				$va{'searchresults'} .= "<tr bgcolor='$c[$d]'>\n";
				$va{'searchresults'} .= "  <td class='smalltext'>";
				$va{'searchresults'} .= " <a href='/cgi-bin/mod/$usr{'application'}/dbman?cmd=opr_debitmemos&view=".$in{'id_debitmemos'}."&delprod=".$rec->{'ID_debitmemos_products'}."&tab=4'><img src='$va{'imgurl'}/$usr{'pref_style'}/b_drop.png' title='Drop' alt='' border='0'></a></td>\n";
				if (substr($rec->{'ID_products'},0,1) eq 4){
					$va{'searchresults'} .= "  <td class='smalltext' valign='top'><a href=\"/cgi-bin/mod/$usr{'application'}/dbman?cmd=mer_parts&view=".($rec->{'ID_products'}-400000000)."\">". &format_sltvid($rec->{'ID_products'})."</a></td>\n";
					$va{'searchresults'} .= "  <td class='smalltext' valign='top'>".&load_db_names('sl_parts','ID_parts',$rec->{'ID_products'}-400000000,'[Name]<br>[Model]')."</td>\n";
					$line_tax = (($rec->{'SalePrice'}*$rec->{'Quantity'})-$rec->{'Discount'})*$rec->{'Tax_percent'}/100;
					$line_tax += $rec->{'Shipping'} * $rec->{'Tax_percent'}/100 if ($cfg{'shptax'});
				}else{
					$va{'searchresults'} .= "  <td class='smalltext'><a href=\"/cgi-bin/mod/$usr{'application'}/dbman?cmd=mer_services&view=".($rec->{'ID_products'}-600000000)."\">$rec->{'ID_products'}</a></td>\n";
					$va{'searchresults'} .= "  <td class='smalltext'>".&load_name('sl_services','ID_services',$rec->{'ID_products'}-600000000,'Name')."</td>\n";
					$line_tax = $rec->{'Tax'};
				}
				$va{'searchresults'} .= qq|  <td class='smalltext' align='right'><input name="prods_qty_$rec->{'ID_debitmemos_products'}" style="text-align:right" value="$rec->{'Quantity'}" size="5" onfocus="focusOn( this )" onblur="focusOff( this )" type="text"><span class='smallfieldterr'>$error{'prods_qty_'.$rec->{'ID_debitmemos_products'}}</span></td>\n|;
				$va{'searchresults'} .= qq|  <td class='smalltext' align='right'><input name="prods_saleprice_$rec->{'ID_debitmemos_products'}" style="text-align:right" value="$rec->{'SalePrice'}" size="10" onfocus="focusOn( this )" onblur="focusOff( this )" type="text"><span class='smallfieldterr'>$error{'prods_saleprice_'.$rec->{'ID_debitmemos_products'}}</span></td>\n|;
				if (substr($rec->{'ID_products'},0,1) eq 4){
					$va{'searchresults'} .= qq|  <td class='smalltext' align='right'><input name="prods_discount_$rec->{'ID_debitmemos_products'}" style="text-align:right" value="$rec->{'Discount'}" size="10" type="text"></td>\n|;
					$va{'searchresults'} .= qq|  <td class='smalltext' align='right'><input name="prods_shipping_$rec->{'ID_debitmemos_products'}" style="text-align:right" value="$rec->{'Shipping'}" size="10" onfocus="focusOn( this )" onblur="focusOff( this )" type="text"><span class='smallfieldterr'>$error{'prods_shipping_'.$rec->{'ID_debitmemos_products'}}</span></td>\n|;
					$va{'searchresults'} .= qq|  <td class='smalltext' align='right'><input name="prods_cost_$rec->{'ID_debitmemos_products'}" style="text-align:right" value="$rec->{'Cost'}" size="10" onfocus="focusOn( this )" onblur="focusOff( this )" type="text"><span class='smallfieldterr'>$error{'prods_cost_'.$rec->{'ID_debitmemos_products'}}</span></td>\n|;
				}else{
					$va{'searchresults'} .= qq|  <td class='smalltext' align='right'><input name="prods_discount_$rec->{'ID_debitmemos_products'}" style="text-align:right" value="$rec->{'Discount'}" size="10" type="text"></td>\n|;
					$va{'searchresults'} .= qq|  <td class='smalltext' align='right'><input name="prods_shipping_$rec->{'ID_debitmemos_products'}" style="text-align:right" value="$rec->{'Shipping'}" type="hidden">---</td>\n|;
					$va{'searchresults'} .= qq|  <td class='smalltext' align='right'><input name="prods_cost_$rec->{'ID_debitmemos_products'}" style="text-align:right" value="$rec->{'Cost'}" type="hidden">---</td>\n|;
				}
				$va{'searchresults'} .= "  <td class='smalltext' align='right'>".&format_price($line_tax)." ($rec->{'Tax_percent'} %)</td>\n";
				$va{'total'} = (($rec->{'Quantity'}*$rec->{'SalePrice'})-$rec->{'Discount'}) + $line_tax + $rec->{'Shipping'} ;
				$va{'searchresults'} .= "  <td class='smalltext' align='right'>".&format_price($va{'total'})."</td>\n";
				$va{'searchresults'} .= "</tr>\n";
			}else{
				$va{'searchresults'} .= "<tr bgcolor='$c[$d]'>\n";
				$va{'searchresults'} .= "  <td class='smalltext'></td>\n";
				if (substr($rec->{'ID_products'},0,1) eq 4){
					$va{'searchresults'} .= "  <td class='smalltext' valign='top' rowspan='2'><a href=\"/cgi-bin/mod/$usr{'application'}/dbman?cmd=mer_parts&view=".($rec->{'ID_products'}-400000000)."\">".&format_sltvid($rec->{'ID_products'})."</a></td>\n";
					$va{'searchresults'} .= "  <td class='smalltext' valign='top'>".&load_db_names('sl_parts','ID_parts',$rec->{'ID_products'}-400000000,'[Name]<br>[Model]')."</td>\n";
					$line_tax = (($rec->{'SalePrice'}*$rec->{'Quantity'})-$rec->{'Discount'})*$rec->{'Tax_percent'}/100;
					$line_tax += $rec->{'Shipping'} * $rec->{'Tax_percent'}/100 if ($cfg{'shptax'});
				}else{
					$va{'searchresults'} .= "  <td class='smalltext'><a href=\"/cgi-bin/mod/$usr{'application'}/dbman?cmd=mer_services&view=".($rec->{'ID_products'}-600000000)."\">".&format_sltvid($rec->{'ID_products'})."</a></td>\n";
					$va{'searchresults'} .= "  <td class='smalltext'>".&load_name('sl_services','ID_services',$rec->{'ID_products'}-600000000,'Name')."</td>\n";
					$line_tax = $rec->{'Tax'};
				}
				$va{'searchresults'} .= qq|  <td class='smalltext' align='right'>$rec->{'Quantity'}</td>\n|;
				$va{'searchresults'} .= qq|  <td class='smalltext' align='right'>|. &format_price($rec->{'SalePrice'}). qq|</td>\n|;

				$va{'searchresults'} .= qq|  <td class='smalltext' align='right'>|. &format_price($rec->{'Discount'}). qq|</td>\n|;

				$va{'searchresults'} .= qq|  <td class='smalltext' align='right'>|. &format_price($rec->{'Shipping'}).qq|</td>\n|;
				$va{'searchresults'} .= qq|  <td class='smalltext' align='right'>|. &format_price($rec->{'Cost'}).qq|</td>\n|;
				$va{'searchresults'} .= "  <td class='smalltext' align='right'>".&format_price($line_tax)." ($rec->{'Tax_percent'} %)</td>\n";
				$va{'total'} = (($rec->{'Quantity'}*$rec->{'SalePrice'})-$rec->{'Discount'}) + $line_tax + $rec->{'Shipping'};
				$va{'searchresults'} .= "  <td class='smalltext' align='right'>".&format_price($va{'total'})."</td>\n";
				$va{'searchresults'} .= "</tr>\n";
				if (substr($rec->{'ID_products'},0,1) eq 4){
					$rec->{'ShpDate'} = '---' if (!$rec->{'ShpDate'});
					$va{'searchresults'} .= "<tr bgcolor='$c[$d]'>\n";
					$va{'searchresults'} .= "  <td class='smalltext'></td>\n";
					$va{'searchresults'} .= qq|  <td class='smalltext' colspan="7">|.&trans_txt('recepinfo').qq| : $rec->{'ShpDate'}</td>\n|;
					$va{'searchresults'} .= "</tr>\n";
				}
			}
			$cm_total+=$va{'total'};
		}
		if ($va{'total'} > 0) {
			$va{'searchresults'} .= "<tr bgcolor='$c[$d]'>\n";
			$va{'searchresults'} .= "  <td class='smalltext' colspan='9' align='right'>Total</td>\n";
			$va{'searchresults'} .= "  <td class='smalltext' align='right' style='border-top:thick double #808080;'>".&format_price($cm_total)."</td>\n";
			$va{'searchresults'} .= "</tr>\n";
		}

	}else{
		$va{'pageslist'} = 1;
		$va{'searchresults'} = qq|
			<tr>
				<td colspan='9' align='center'>|.&trans_txt('search_nomatches').qq|</td>
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
	if ($in{'geninvoice'}) {
		if (&check_permissions('orders_toinvoice','','')) {
				# Generate Invoice
				&Do_SQL("START TRANSACTION;");
				my $status;

				# Generate Credit Note
				($va{'tabmessages'}, $status) = &export_info_for_invoices($in{'id_orders'});

				if ($status =~ /OK/i){
					&Do_SQL("COMMIT;");
				}else{
					&Do_SQL("ROLLBACK;");
				}
		}else {
			$va{'tabmessages'} = &trans_txt('unauth_action');
		}
	}

	my (@c) = split(/,/,$cfg{'srcolors'});
	my ($sth) = &Do_SQL("SELECT COUNT(*) FROM (SELECT 1 FROM cu_invoices_lines INNER JOIN cu_invoices USING(ID_invoices) WHERE ID_debitmemos = '$in{'id_debitmemos'}' GROUP BY ID_invoices)AS invoices");
	$va{'matches'} = $sth->fetchrow();
	#$va{'geninvoice'} = '';
	
	if ($va{'matches'} > 0){
		(!$in{'nh'}) and ($in{'nh'}=1);
		$first = ($in{'nh'} - 1) * $usr{'pref_maxh'};			
		($va{'pageslist'},$qs) = &pages_list($in{'nh'},"/cgi-bin/mod/$usr{'application'}/dbman",$va{'matches'},$usr{'pref_maxh'});
		$sth = &Do_SQL("SELECT CONCAT(doc_serial,doc_num) AS invoice, cu_invoices.ID_invoices,ID_customers,ID_debitmemos,CONCAT(customer_fcode,' ',customer_fname) AS NAME, cu_invoices.Status,cu_invoices.Date, doc_serial, doc_num
				FROM cu_invoices_lines
				INNER JOIN cu_invoices ON cu_invoices.ID_invoices = cu_invoices_lines.ID_invoices
				WHERE ID_debitmemos = '$in{'id_debitmemos'}'
				GROUP BY ID_invoices
				ORDER BY ID_invoices DESC LIMIT $first,$usr{'pref_maxh'};");
		while ($rec = $sth->fetchrow_hashref){
			$d = 1 - $d;
			
			my $pdf_name = $rec->{'doc_serial'}.'_'.$rec->{'doc_num'};
			my $link_pdf = "/cfdi/pages/cfdi/cfdi_doc.php?f=".$pdf_name.".pdf";
			$va{'searchresults'} .= "<tr bgcolor='$c[$d]'>\n";
			$va{'searchresults'} .= ($rec->{'Status'} eq 'Certified')?
									"   <td class='smalltext'><a href='$link_pdf' target='_blank'><img src='[va_imgurl]/[ur_pref_style]/pdf.gif' title='PDF' alt='PDF' border='0'></a></td>\n":
									"   <td class='smalltext'></td>\n";
			$va{'searchresults'} .= "   <td class='smalltext'><a href=\"/cgi-bin/mod/$usr{'application'}/dbman?cmd=opr_invoices&view=$rec->{'ID_invoices'}\">$rec->{'ID_invoices'}</a></td>\n";
			$va{'searchresults'} .= "   <td class='smalltext'>$rec->{'invoice'}</td>\n";
			$va{'searchresults'} .= "   <td class='smalltext'><a href=\"/cgi-bin/mod/$usr{'application'}/dbman?cmd=opr_customers&view=$rec->{'ID_customers'}\">($rec->{'ID_customers'}) $rec->{'NAME'}</a></td>\n";
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
					WHERE ID_orders = '".$in{'id_debitmemos'}."' 
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

	#$va{'geninvoice'} .= qq|&nbsp;&nbsp;<a onclick="return confirm_continue();" href="/cgi-bin/mod/|.$usr{'application'}.qq|/dbman?cmd=|.$in{'cmd'}.qq|&view=|.$in{'view'}.qq|&tab=|.$in{'tab'}.qq|&creditnote=1">|.&trans_txt('opr_orders_generate_creditnote').qq|</a>|;
	#$va{'geninvoice'} = qq|<a onclick="return confirm_continue();" href="/cgi-bin/mod/|.$usr{'application'}.qq|/dbman?cmd=opr_orders&view=|.$in{'id_orders'}.qq|&tab=|.$in{'tab'}.qq|&geninvoice=1">|.&trans_txt('opr_orders_generate_invoice').qq|</a>|;
	$va{'geninvoice'} = qq|&nbsp;&nbsp;<a onclick="return Confirm_to_continue()" href="/cgi-bin/mod/|.$usr{'application'}.qq|/dbman?cmd=|.$in{'cmd'}.qq|&view=|.$in{'view'}.qq|&tab=|.$in{'tab'}.qq|&geninvoice=1">|.&trans_txt('opr_orders_generate_invoice').qq|</a>|;

}



1;