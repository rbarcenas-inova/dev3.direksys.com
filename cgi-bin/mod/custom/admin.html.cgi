###################################################
#### PURCHASE ORDERS
###################################################

sub cus_pos{
#-------------------------------
	my ($err);
	if ($in{'action'}){
		$in{'id_purchaseorders'} = int($in{'id_purchaseorders'});
		if ($in{'id_purchaseorders'}>0){
			my ($sth) = &Do_SQL("SELECT COUNT(*) FROM sl_purchaseorders WHERE Auth='In Process' AND Status='New' AND ID_purchaseorders=$in{'id_purchaseorders'} ");
			if ($sth->fetchrow ne 1){
				++$err;
			}
			if (!$err){
				my ($sth) = &Do_SQL("SELECT COUNT(*) FROM sl_movements WHERE  tableused='sl_purchaseorders' AND ID_tableused=$in{'id_purchaseorders'} ");
				if ($sth->fetchrow >0){
					++$err;
				}
			}
		}else{
			++$err;
		}
		if (!$err){
			&cus_pos_view;
			return;
		}else{
			$error{'id_purchaseorders'} = &trans_txt('invalid');
			$va{'message'} = &trans_txt('searcherror');
		}
			
	}
	print "Content-type: text/html\n\n";
	print &build_page('cus_pos.html');
}


sub cus_pos_view{
#-------------------------------
	&load_cfg('sl_purchaseorders');
	my (%rec) = &get_record('ID_purchaseorders',$in{'id_purchaseorders'},'sl_purchaseorders');
	foreach $key (sort keys %rec) {
		$in{lc($key)} = $rec{$key};
		($db_valid_types{lc($key)} ne 'html') and ($in{lc($key)} =~ s/\n/<br>/g);
	}
	
	if ($in{'id_vendors'}){
		$va{'vendor_name'} = &load_db_names('sl_vendors','ID_vendors',$in{'id_vendors'},'[CompanyName]<br>[address] [city] <br>[state] [zip]');
	}
	if ($in{'authby'}){
		$in{'authby_name'} = &load_db_names('admin_users','ID_admin_users',$in{'authby'},'[Firstname] [Lastname]');
	}else{
		$in{'authby'} = &trans_txt('not_auth');
		$in{'auth'}   = 'In Process';
		delete($in{'authby_name'});
	}
	if ($in{'id_warehouses'}){
		$va{'warehouseinfo'} = &load_db_names('sl_warehouses','ID_warehouses',$in{'id_warehouses'},'[Name]<br>[address1] [address2] [address3]<br>[city] [state] [zip]');
	}
	
	$va{'shiptoaddress'} = $va{'warehouseinfo'};
	$in{'currency_exchange'} = &format_price($in{'currency_exchange'}) if $in{'currency_exchange'};
	$va{'currency'} = $in{'currency_exchange'} ? $cfg{'acc_default_currency'} . " * 1 " . &load_name('sl_vendors','ID_vendors',$in{'id_vendors'},'Currency') : '';
	$va{'curstyle'} = $va{'currency'} ne '' ? '' : qq|style="display:none;"|;
	
	
	## Build PO List
	## Converted to function because needs to be called from:
	## 
	&build_po_list();

	
	## Build Shipping Instructions
	my ($sth) = &Do_SQL("SELECT COUNT(*) FROM sl_purchaseorders_shipping WHERE ID_purchaseorders='$in{'id_purchaseorders'}' AND Type='Add to the PO'");
	if ($sth->fetchrow>0){
		my ($sth) = &Do_SQL("SELECT Notes FROM sl_purchaseorders_shipping WHERE ID_purchaseorders='$in{'id_purchaseorders'}' AND Type='Add to the PO'");
		while ($note = $sth->fetchrow){
			$note =~ s/\n/<br>/g;
			$va{'shipping_inst'} = "<li>$note</li>\n";
		}
	}else{
		$va{'shipping_inst'} = "---";
	}
	
	print "Content-type: text/html\n\n";
	print &build_page('cus_pos_view.html');	

}

#############################################################################
#############################################################################
#   Function: build_po_list
#
#       Es: Genera el listado de PO Items/Adjustments
#       En: Build PO Items/Adjustments List 
#
#
#    Created on: 2013-03-07
#
#    Author: _Roberto Barcenas_
#
#    Modifications:
#
#        - Modified on ** by _Roberto Barcenas_ : 
#
#   Parameters:
#
#
#  Returns:
#
#      - 
#
#   See Also:
#
#      <view_mer_po>
#
sub build_po_list {
#############################################################################
#############################################################################

	delete($va{'polist'}); delete($va{'pototal'});
	my $authby = &load_name('sl_purchaseorders','ID_purchaseorders',$in{'id_purchaseorders'},'AuthBy');
	my ($choices,$tot_qty,$tot_po,$tax_po,$subtot_po,$vendor_sku,$line,$name,$cmdlink,$unit);
	my (@c) = split(/,/,$cfg{'srcolors'});
	my ($sth) = &Do_SQL("SELECT COUNT(*) FROM sl_purchaseorders_items WHERE ID_purchaseorders='$in{'id_purchaseorders'}'");
	if ($sth->fetchrow>0){
		my ($sth) = &Do_SQL("SELECT *, (Qty - Received) as quantity FROM sl_purchaseorders_items WHERE ID_purchaseorders='$in{'id_purchaseorders'}' ORDER BY ID_purchaseorders_items DESC;");
		while ($rec = $sth->fetchrow_hashref){
			$d = 1 - $d;
			++$line;

			# Color in Received
			$color = ($rec->{'quantity'}==0)? ' style="color:#73AB00"' : ' style="color:#FF0000"';
			
			## Choices
			my ($sth2) = &Do_SQL("SELECT * FROM sl_skus WHERE ID_sku_products='$rec->{ID_products}' and Status='Active'");
			$tmp = $sth2->fetchrow_hashref;
			$choices = &load_choices('-',$rec->{'choice1'},$rec->{'choice2'},$rec->{'choice3'},$rec->{'choice4'});
			
			## Name Model
			if ($rec->{'ID_products'} =~ /^5/){
				## Non Inventory
				$cmdlink = 'mer_noninventory';
				$unit = &load_db_names('sl_noninventory','ID_noninventory',($rec->{ID_products}-500000000),'[Units]');
				$name = &load_db_names('sl_noninventory','ID_noninventory',($rec->{ID_products}-500000000),'[Name]');
			}elsif ($rec->{'ID_products'}  =~ /^4/){
				## Part
				$unit  = "Unit";
				$cmdlink = 'mer_parts';
				$name = &load_db_names('sl_parts','ID_parts',($rec->{ID_products}-400000000),'[Model]<br>[Name]');
			}
			

			$va{'polist'} .= "<tr bgcolor='$c[$d]'>\n";
			$va{'polist'} .= "   <td class='smalltext' valign='top'>$line </td>\n";
			$va{'polist'} .= "   <td class='smalltext' valign='top' nowrap><a href='/cgi-bin/mod/$usr{'application'}/dbman?cmd=$cmdlink&view=".substr($rec->{'ID_products'},3,6)."'>".&format_sltvid($rec->{'ID_products'})."</a></td>\n";
			$va{'polist'} .= "   <td class='smalltext' valign='top'>$tmp->{'VendorSKU'}</td>\n";
			$va{'polist'} .= "   <td class='smalltext' valign='top'>$name </td>\n";
			$va{'polist'} .= "   <td class='smalltext'  valign='top'>".&format_number($rec->{'Qty'})."</td>\n";
			$va{'polist'} .= "   <td class='smalltext' align='right' valign='top'>".&format_price($rec->{'Price'})."</td>\n";
			$va{'polist'} .= "   <td class='smalltext' valign='top'>".($rec->{'Tax_percent'}*100)."</td>\n";
			$va{'polist'} .= "   <td class='smalltext' valign='top'><span id='span_received_$rec->{'ID_purchaseorders_items'}' class='editable'>".&format_number($rec->{'Received'})."</span> $unit <span id='span_chg_received_$rec->{'ID_purchaseorders_items'}'><img id='btn_chg_received_$rec->{'ID_purchaseorders_items'}' class='triggers_editable' src='$va{'imgurl'}/$usr{'pref_style'}/b_edit.png' title='".&trans_txt('clicktoedit')."' style='cursor:pointer;'></span></td>\n";
			$va{'polist'} .= "   <td class='smalltext' align='right' valign='top' nowrap> ".&format_price($rec->{'Qty'} * $rec->{'Price'})."</td>\n";
			$va{'polist'} .= "   <td class='smalltext' align='right' valign='top'>\$ ".&format_number($rec->{'Tax'},2)."</td>\n";
			$va{'polist'} .= "   <td class='smalltext' align='right' valign='top' nowrap> ".&format_price($rec->{'Total'})."</td>\n";
			$va{'polist'} .= "</tr>\n";
			$tot_qty += $rec->{'Qty'};
			$tot_po += $rec->{'Total'};
			$tax_po += $rec->{'Tax'};
			$subtot_po += ($rec->{'Price'}*$rec->{'Qty'});
			#&cgierr("$rec->{'Price'}*$rec->{'Qty'}*$rec->{'Tax_percent'}") if $rec->{'Tax_percent'} > 0 ;
		}
	}else{
		$va{'polist'} = qq|
			<tr>
				<td colspan='11' align="center">|.&trans_txt('search_nomatches').qq|</td>
			</tr>\n|;
	}
	
	my ($sth) = &Do_SQL("SELECT COUNT(*) FROM sl_purchaseorders_adj WHERE ID_purchaseorders='$in{'id_purchaseorders'}'");
	if ($sth->fetchrow>0){
		my ($sth) = &Do_SQL("SELECT * FROM sl_purchaseorders_adj WHERE ID_purchaseorders='$in{'id_purchaseorders'}'");
		while ($rec = $sth->fetchrow_hashref){
			$d = 1 - $d;
			++$line;
			$rec->{'Qty'} = 1;
			$va{'polist'} .= "<tr bgcolor='$c[$d]'>\n";
			$va{'polist'} .= "   <td class='smalltext'>$line</td>\n";
			$va{'polist'} .= "   <td class='smalltext' align='center'>---</td>\n";
			$va{'polist'} .= "   <td class='smalltext' align='center'>---</td>\n";
			$va{'polist'} .= "   <td class='smalltext'>$rec->{'Type'}: $rec->{'Description'}</td>\n";
			$va{'polist'} .= "   <td class='smalltext'>".&format_number($rec->{'Qty'})."</td>\n";
			$va{'polist'} .= "   <td class='smalltext' valign='top'>".($rec->{'Tax_percent'}*100)."</td>\n";
			$va{'polist'} .= "   <td class='smalltext' align='center'>".&format_number($rec->{'Received'})."</td>\n";
			$va{'polist'} .= "   <td class='smalltext' align='center'>---</td>\n";
			$va{'polist'} .= "   <td class='smalltext' align='right'> ".&format_price($rec->{'Amount'})."</td>\n";
			$va{'polist'} .= "   <td class='smalltext' align='right' valign='top'>\$ ".&format_number($rec->{'Tax'},2)."</td>\n";
			$va{'polist'} .= "   <td class='smalltext' align='right'> ".&format_price($rec->{'Total'})."</td>\n";
			$va{'polist'} .= "</tr>\n";
			$tot_po += $rec->{'Total'};
			$tax_po += $rec->{'Tax'};
			$subtot_po += ($rec->{'Price'}*$rec->{'Qty'});
		}
	}
	$va{'posubtot'} = &format_price($subtot_po);
	$va{'potottax'} = &format_price($tax_po);
	$va{'pototal'} = &format_price($tot_po);

}

	
###################################################
####  ORDERS
###################################################

sub cus_orders{
#-------------------------------
	my ($err);
	if ($in{'action'}){
		$in{'id_orders'} = int($in{'id_orders'});
		if ($in{'id_orders'}>0){
			my ($sth) = &Do_SQL("SELECT COUNT(*) FROM sl_orders WHERE Status='New' AND id_orders=$in{'id_orders'} ");
			if ($sth->fetchrow ne 1){
				++$err;
			}
			if (!$err){
				my ($sth) = &Do_SQL("SELECT COUNT(*) FROM sl_movements WHERE  tableused='sl_orders' AND ID_tableused=$in{'id_orders'} ");
				if ($sth->fetchrow >0){
					++$err;
				}
			}
		}else{
			++$err;
		}
		if (!$err){
			&cus_orders_view;
			return;
		}else{
			$error{'id_orders'} = &trans_txt('invalid');
			$va{'message'} = &trans_txt('searcherror');
		}
			
	}
	print "Content-type: text/html\n\n";
	print &build_page('cus_orders.html');
}

sub cus_orders_view{
#-------------------------------
	&load_cfg('sl_orders');
	my (%rec) = &get_record('ID_orders',$in{'id_orders'},'sl_orders');
	foreach $key (sort keys %rec) {
		$in{lc($key)} = $rec{$key};
		($db_valid_types{lc($key)} ne 'html') and ($in{lc($key)} =~ s/\n/<br>/g);
	}
	if ($in{'id_customers'}){
		my ($sth) = &Do_SQL("SELECT * FROM sl_customers WHERE ID_customers='$in{'id_customers'}';");
		$rec = $sth->fetchrow_hashref;
		foreach my $key (keys %{$rec}){
			#$in{'customers.'.lc($key)} = uc($rec->{$key});
			$in{'customers.'.lc($key)} = $rec->{$key};
		}
	}
	my (@types) = split(/,/,$cfg{'shp_types'});
	foreach my $type (@types) {
		if ($in{'shp_type'} eq 1) {
			$in{'shp_type'} = "$types[0]";
		}elsif ($in{'shp_type'} eq 2) {
			$in{'shp_type'} = "$types[1]";		
		}elsif ($in{'shp_type'} eq 3){
			$in{'shp_type'} = "$types[2]"; 
			## COD Table
			$va{'cod_table'} = &get_cod_table($in{'id_orders'});
		}
	}
	$va{'cmd_customer'} = 'opr_customers';
	$va{'cmd_did'} = 'mm_dids';
	### Warning Message
	$va{'waringmsg'} = qq|<a href="/cgi-bin/mod/admin/dbman?cmd=opr_invoices&view=[in_id_orders]"><img src='[va_imgurl]/[ur_pref_style]/warning.gif' title='Warining' alt='Invoice' border='0'></a>|;;
	
	### Station Name
	$va{'pricelevels_name'} = &load_db_names('sl_pricelevels','ID_pricelevels',$in{'id_pricelevels'},'[Name]');

	### Orders Totals
	my ($sth) = &Do_SQL("SELECT 
	                    	SUM(Tax + ShpTax)AS TotalTax,
	                    	SUM(SalePrice)AS OrderNet,
	                    	SUM(Discount)AS Discount,
	                    	SUM(Shipping)AS Shipping,
	                    	SUM(SalePrice - Discount + Shipping + Tax + ShpTax) AS OrderTotal
	                    	FROM sl_orders_products
	                    WHERE ID_orders = '$in{'id_orders'}' AND Status NOT IN ('Inactive','Order Cancelled');");
	my ($tot_tax,$ordernet,$discount,$shipping,$total_order) = $sth->fetchrow();

	$va{'total_taxes'} = &format_price($tot_tax);
	$va{'total_order'} = &format_price($total_order);
	$va{'ordernet'} = &format_price($ordernet);
	$va{'orderdisc'} = &format_price($discount);
	$va{'ordershp'} = &format_price($shipping);

	################################################################################	
	my ($sth2) = &Do_SQL("SELECT SUM(Tax) Tot_tax, Tax_percent FROM sl_orders_products WHERE ID_orders='$in{'id_orders'}' AND Status NOT IN('Order Cancelled', 'Inactive')  GROUP BY Tax_percent ORDER BY Tax_percent DESC");
	my ($rec_tax);
	$va{'tax_lines'} = '';
	my $tax_line_c = 0;
	while ($rec_tax = $sth2->fetchrow_hashref) {
		
		if ($tax_line_c == 0) {
			$va{'tax_lines'} .= qq|
					<tr>
						<td class="smalltext" align="right">$in{'orderqty'} <input type="hidden" name="orderqty" value="$in{'orderqty'}"></td>
						<td class="smalltext" align="right">$va{'ordernet'} <input type="hidden" name="orderqty" value="$in{'ordernet'}"></td>
						<td class="smalltext" align="right" style="color:red">$va{'orderdisc'} <input type="hidden" name="orderdisc" value="$in{'orderdisc'}"></td>
						<td class="smalltext" align="right">$va{'ordershp'} <input type="hidden" name="ordershp" value="$in{'ordershp'}"></td>
						<td class="smalltext" align="right">|.&format_price($rec_tax->{'Tot_tax'}).' ('.($rec_tax->{'Tax_percent'}*100).qq|%) <input type="hidden" name="ordertax" value="$in{'ordertax'}"></td>
						<td class="smalltext" align="right">$va{'total_order'}</td>
					</tr>|;
					
					
					
		} else {
			$va{'tax_lines'} .= qq|
					<tr>
						<td class="smalltext" align="center">&nbsp; </td>
						<td class="smalltext" align="center">&nbsp; </td>
						<td class="smalltext" align="center" style="color:red">&nbsp; </td>
						<td class="smalltext" align="center">&nbsp; </td>
						<td class="smalltext" align="right">|.&format_price($rec_tax->{'Tot_tax'}).' ('.($rec_tax->{'Tax_percent'}*100).qq|%) <input type="hidden" name="ordertax" value="$in{'ordertax'}"></td>
						<td class="smalltext" align="center">&nbsp; </td>
					</tr>|;
		}
		$tax_line_c++;
	}	
	################################################################################
		
	## No Posted Date
	(!$in{'posteddate'}) and ($in{'posteddate'}='---');
	
	$va{'tax'} = $in{'ordertax'}*100;
	$va{'ordertax'} = &format_number($in{'ordertax'}*100);
	&build_product_list;
	&build_payments_list;
	
	print "Content-type: text/html\n\n";
	print &build_page('cus_orders_view.html');	

}


#############################################################################
#############################################################################
#   Function: build_product_list
#
#
#
#    Created on: 2013-03-07
#
#    Author: _CARLOS HAAS_
#
#    Modifications:
#
#
#   Parameters:
#
#
#  Returns:
#
#      - 
#
#   See Also:
#
#
sub build_product_list {
#############################################################################
#############################################################################

	my (@c) = split(/,/,$cfg{'srcolors'});
	my ($sth) = &Do_SQL("SELECT COUNT(*) FROM sl_orders_products WHERE ID_orders='$in{'id_orders'}'");
	$va{'matches'} = $sth->fetchrow;
	if ($va{'matches'}>0){
		my ($sth1) = &Do_SQL("SELECT * FROM sl_orders_products WHERE ID_orders='$in{'id_orders'}' ORDER BY ID_orders_products,Date,Time");
		while ($col = $sth1->fetchrow_hashref){
			my $cmdorder = 'opr_orders';
			my $unit_price = ($col->{'Quantity'}>0)?($col->{'SalePrice'}/$col->{'Quantity'}):0;

			$d = 1 - $d;
			
			if(!&is_exportation_order($in{'id_orders'})){

				$sku_id_p=substr($col->{'ID_products'},3,6);
				$sku_id_e=$col->{'ID_products'};
				$sku_id_d=format_sltvid($col->{'ID_products'});
				if ($col->{'Status'} ne 'Inactive'){
					$tot_qty += $col->{'Quantity'};
					$tot_ord +=$col->{'SalePrice'};
				}
										
				my ($sthk) = &Do_SQL("SELECT * FROM sl_skus WHERE ID_sku_products='$col->{'ID_products'}' /*and Status='Active'*/");
				$rec = $sthk->fetchrow_hashref;
				$choices = &load_choices('-',$rec->{'choice1'},$rec->{'choice2'},$rec->{'choice3'},$rec->{'choice4'});
					
				###################################################
				################# SETS (PRODUCTS & PARTS)
				###################################################	
													
	      	if ($rec->{'IsSet'} eq 'Y'){
	      		&check_kit_shipped($col->{'ID_orders_products'},'orders');
	      		### SETS / Kits
				$va{'productslist'} .= "<tr bgcolor='$c[$d]' onmouseover='m_over(this)' onmouseout='m_out(this)'>\n";
				$va{'productslist'} .= " <td class='smalltext' valign='top'>";
				if ((!$col->{'ShpDate'} or $col->{'ShpDate'} eq '0000-00-00') and $col->{'Status'} eq 'Active'){
					#$va{'productslist'} .= qq| <a href="/cgi-bin/mod/$usr{'application'}/dbman?cmd=opr_orders&view=$in{'id_orders'}&tab=1&drop=$col->{'ID_orders_products'}"><img src='$va{'imgurl'}/$usr{'pref_style'}/b_drop.png' title='Drop' alt='' border='0'></a>|;
				}
	            	

				$va{'productslist'} .= "<br>$sku_id_d ";
				if (!$col->{'Tracking'}){
					$va{'productslist'} .= &build_edit_choices($col->{'ID_products'},"/cgi-bin/mod/$usr{'application'}/dbman","cmd=$cmdorder&view=$in{'id_orders'}&tab=1&ID_orders_products=$col->{'ID_orders_products'}")
				}
					
				$va{'productslist'} .= "</td>\n";		
				(!$col->{'SerialNumber'}) and ($col->{'SerialNumber'} = '---');
				($status,%tmp) = &load_product_info($sku_id_p);
				&load_cfg('sl_orders');
				$va{'productslist'} .= "  <td class='smalltext' valign='top'>$tmp{'model'}<br>".substr($tmp{'name'},0,30)." ".$choices."</td>\n";
				$va{'productslist'} .= "  <td class='smalltext' valign='top'> $col->{'SerialNumber'} </td>\n";
				$va{'productslist'} .= "  <td class='smalltext' valign='top'>".&build_tracking_link($col->{'Tracking'},$col->{'ShpProvider'},$col->{'ShpDate'},$col->{'ID_products'})."</td>\n";
	
				if ($col->{'Status'} eq 'Inactive'){
					$decor = " style=' text-decoration: line-through'";
				}else{
					$decor ='';
				}
				
				$va{'productslist'} .= "  <td class='smalltext' align='right' valign='top' $decor>".&format_number($col->{'Quantity'})."</td>\n";
				$va{'productslist'} .= "  <td class='smalltext' align='right' valign='top' $decor>".&format_price($unit_price)."</td>\n";
				$va{'productslist'} .= "  <td class='smalltext' align='right' valign='top' $decor>".&format_price($col->{'Shipping'});
				$va{'productslist'} .= "  </td>\n<td class='smalltext' align='right' valign='top' $decor nowrap>".&format_price($col->{'SalePrice'});
				
				#Se comenta edición de productos
				if (&check_permissions('edit_order_cleanup','','')){
						$va{'productslist'} .= qq| 
						<div id="divpayment$rec->{'ID_orders_products'}"><a href="#tabs" onClick="popup_show('ajax_windows', 'ajax_drag', 'ajax_exit', 'element-right', -1, -1,'tabs');loadDoc('/cgi-bin/common/apps/ajaxbuild?ajaxbuild=edit_products&id_orders=$col->{'ID_orders'}&id_orders_products=$col->{'ID_orders_products'}&cmd=$in{'cmd'}&script_url=/cgi-bin/mod/$usr{'application'}/dbman');"><img src='$va{'imgurl'}/$usr{'pref_style'}/b_edit.png' title='Edit In Clean up Mode' alt='' border='0'></a></div>|;
				}
			
				$va{'productslist'} .= "</td>\n";
				$va{'productslist'} .= "</tr>\n";	
			
				my ($sth2) = &Do_SQL("SELECT * FROM sl_skus_parts WHERE ID_sku_products='$rec->{'ID_sku_products'}';");
				while ($tmp = $sth2->fetchrow_hashref){
						for my $i(1..$tmp->{'Qty'}){
								my ($sth3) = &Do_SQL("SELECT * FROM sl_orders_parts WHERE ID_orders_products='$col->{'ID_orders_products'}' AND ID_parts='$tmp->{'ID_parts'}' LIMIT ".($i-1).",1;");
								my ($shp) = $sth3->fetchrow_hashref;
								$va{'productslist'} .= qq|
								<tr bgcolor='$c[$d]'>
								<td class="smalltext" $style valign="top" align="right"  onmouseover='m_over(this)' onmouseout='m_out(this)' OnClick="trjump('/cgi-bin/mod/$usr{'application'}/dbman?cmd=$linkparts&view=$tmp->{'ID_parts'}')"><img src="$va{'imgurl'}/$usr{'pref_style'}/tri.gif" border="0"> |.
								&format_sltvid(400000000+$tmp->{'ID_parts'}).qq|</td>
								<td class="smalltext" $style valign="top">|.&load_db_names('sl_parts','ID_parts',$tmp->{'ID_parts'},'[Model]<br>[Name]').qq|</td>
								<td class="smalltext" $style valign="top">|.&build_tracking_link($shp->{'Tracking'},$shp->{'ShpProvider'},$shp->{'ShpDate'},400000000+$tmp->{'ID_parts'}).qq|</td>
								<td class="smalltext" $style valign="top">$tmp->{'Serial'}</td>
								<td class="smalltext" colspan="4"></td>
								</tr>\n|;
						}
				}
				
			########################################################
			################## SERVICES
			########################################################
	     	}elsif($col->{'ID_products'} < 99999 or substr($col->{'ID_products'},0,1) == 6){
	      			(substr($col->{'ID_products'},0,1) == 6) and ($col->{'ID_products'} = substr($col->{'ID_products'},5));
					$va{'productslist'} .= "<tr bgcolor='$c[$d]' onmouseover='m_over(this)' onmouseout='m_out(this)'>\n";
					$va{'productslist'} .= " <td class='smalltext' valign='top'>";
					if ((!$col->{'ShpDate'} or $col->{'ShpDate'} eq '0000-00-00') and $col->{'Status'} eq 'Active'){
						#$va{'productslist'} .= qq| <a href="/cgi-bin/mod/$usr{'application'}/dbman?cmd=opr_orders&view=$in{'id_orders'}&tab=1&drop=$col->{'ID_orders_products'}"><img src='$va{'imgurl'}/$usr{'pref_style'}/b_drop.png' title='Drop' alt='' border='0'></a>|;
					}
	
					$va{'productslist'} .= qq| <a href="/cgi-bin/mod/$usr{'application'}/dbman?cmd=$linkser&view=$col->{'ID_products'}"><img src='$va{'imgurl'}/$usr{'pref_style'}/b_view.gif' title='View' alt='' border='0'></a>|;
					my ($sth5) = &Do_SQL("SELECT * FROM sl_services WHERE ID_services = '$col->{'ID_products'}' ;");
					$serdata = $sth5->fetchrow_hashref;
					$col->{'SerialNumber'}='';
					$col->{'ShpProvider'}='';
					$col->{'Tracking'}='';
					$col->{'ShpDate'}='';
					$va{'productslist'} .= "<br>".&format_sltvid(600000000+$col->{'ID_products'})."</td>\n";		
					$va{'productslist'} .= "  <td class='smalltext'>$tmp{'model'}<br>".substr($serdata->{'Name'},0,30)."</td>\n";
					$va{'productslist'} .= "  <td class='smalltext' valign='top'>---</td>\n";
					$va{'productslist'} .= "  <td class='smalltext' valign='top'>".&build_tracking_link($col->{'Tracking'},$col->{'ShpProvider'},$col->{'ShpDate'},600000000+$col->{'ID_products'})."</td>\n";			
					if ($col->{'Status'} eq 'Inactive'){
							$decor = " style=' text-decoration: line-through'";
					}else{
							$decor ='';
					}
					$va{'productslist'} .= "  <td class='smalltext' align='right' valign='top' $decor>".&format_number($col->{'Quantity'})."</td>\n";
					$va{'productslist'} .= "  <td class='smalltext' align='right' valign='top' $decor>".&format_price($unit_price)."</td>\n";
					$va{'productslist'} .= "  <td class='smalltext' align='right' valign='top' $decor>N/A&nbsp;&nbsp;&nbsp;</td>\n";
					$va{'productslist'} .= "  <td class='smalltext' align='right' valign='top' $decor nowrap>".&format_price($col->{'SalePrice'});
					#Se comenta edición de productos
					if (&check_permissions('edit_order_cleanup','','')){
						$va{'productslist'} .= qq| <div id="divpayment$rec->{'ID_orders_products'}"><a href="#tabs" onClick="popup_show('ajax_windows', 'ajax_drag', 'ajax_exit', 'element-right', -1, -1,'tabs');loadDoc('/cgi-bin/common/apps/ajaxbuild?ajaxbuild=edit_products&id_orders=$col->{'ID_orders'}&id_orders_products=$col->{'ID_orders_products'}&cmd=$in{'cmd'}&script_url=/cgi-bin/mod/$usr{'application'}/dbman');"><img src='$va{'imgurl'}/$usr{'pref_style'}/b_edit.png' title='Edit In Clean up Mode' alt='' border='0'></a></div>|;
					}
					$va{'productslist'} .= "</td>\n";
					$va{'productslist'} .= "</tr>\n";	
					
			} elsif(substr($col->{'ID_products'},0,1) == 5){
				
					$va{'productslist'} .= "<tr bgcolor='$c[$d]' onmouseover='m_over(this)' onmouseout='m_out(this)'>\n";
					$va{'productslist'} .= " <td class='smalltext' valign='top'>";
					$va{'productslist'} .= qq| <a href="/cgi-bin/mod/$usr{'application'}/dbman?cmd=$linkser&view=$col->{'ID_products'}"><img src='$va{'imgurl'}/$usr{'pref_style'}/b_view.gif' title='View' alt='' border='0'></a>|;
					$id_samples = $col->{'ID_products'}-500000000;
					my ($sth5) = &Do_SQL("SELECT * FROM sl_samples WHERE ID_samples = '$id_samples' ;");
					$serdata = $sth5->fetchrow_hashref;
					$col->{'SerialNumber'}='';
					$col->{'ShpProvider'}='';
					$col->{'Tracking'}='';
					$col->{'ShpDate'}='';
					$va{'productslist'} .= "<br>".&format_sltvid($col->{'ID_products'})."</td>\n";		
					$va{'productslist'} .= "  <td class='smalltext'>$tmp{'model'}<br>".substr($serdata->{'Name'},0,30)."</td>\n";
					$va{'productslist'} .= "  <td class='smalltext' valign='top'>---</td>\n";
					$va{'productslist'} .= "  <td class='smalltext' valign='top'>".&build_tracking_link($col->{'Tracking'},$col->{'ShpProvider'},$col->{'ShpDate'},600000000+$col->{'ID_products'})."</td>\n";			
					if ($col->{'Status'} eq 'Inactive'){
							$decor = " style=' text-decoration: line-through'";
					}else{
							$decor ='';
					}
					$va{'productslist'} .= "  <td class='smalltext' align='right' valign='top' $decor>".&format_number($col->{'Quantity'})."</td>\n";
					$va{'productslist'} .= "  <td class='smalltext' align='right' valign='top' $decor>".&format_price($unit_price)."</td>\n";
					$va{'productslist'} .= "  <td class='smalltext' align='right' valign='top' $decor>N/A&nbsp;&nbsp;&nbsp;</td>\n";
					$va{'productslist'} .= "  <td class='smalltext' align='right' valign='top' $decor nowrap>".&format_price($col->{'SalePrice'});
					#Se comenta edición de productos
					if (&check_permissions('edit_order_cleanup','','')){
						$va{'productslist'} .= qq| <div id="divpayment$rec->{'ID_orders_products'}"><a href="#tabs" onClick="popup_show('ajax_windows', 'ajax_drag', 'ajax_exit', 'element-right', -1, -1,'tabs');loadDoc('/cgi-bin/common/apps/ajaxbuild?ajaxbuild=edit_products&id_orders=$col->{'ID_orders'}&id_orders_products=$col->{'ID_orders_products'}&cmd=$in{'cmd'}&script_url=/cgi-bin/mod/$usr{'application'}/dbman');"><img src='$va{'imgurl'}/$usr{'pref_style'}/b_edit.png' title='Edit In Clean up Mode' alt='' border='0'></a></div>|;
					}
					$va{'productslist'} .= "</td>\n";
					$va{'productslist'} .= "</tr>\n";
	
				########################################################
				#################### PRODUCTS 
				########################################################
	
				}else{
					my (%tmp);
					$va{'productslist'} .= "<tr bgcolor='$c[$d]' onmouseover='m_over(this)' onmouseout='m_out(this)'>\n";
					$va{'productslist'} .= " <td class='smalltext' valign='top'>";
					if ((!$col->{'ShpDate'} or $col->{'ShpDate'} eq '0000-00-00') and $col->{'Status'} eq 'Active'){
						#$va{'productslist'} .= qq| <a href="/cgi-bin/mod/$usr{'application'}/dbman?cmd=opr_orders&view=$in{'id_orders'}&tab=1&drop=$col->{'ID_orders_products'}"><img src='$va{'imgurl'}/$usr{'pref_style'}/b_drop.png' title='Drop' alt='' border='0'></a>|;
					}
	            	### Products
	            	$va{'productslist'} .= "<br>".&format_sltvid($col->{'ID_products'});
	            	if (!$col->{'Tracking'}){
	            		$va{'productslist'} .= &build_edit_choices($col->{'ID_products'},"/cgi-bin/mod/$usr{'application'}/dbman","cmd=$cmdorder&view=$in{'id_orders'}&tab=1&ID_orders_products=$col->{'ID_orders_products'}&tabs=1")
	            	}
					$va{'productslist'} .= "</td>\n";
					(!$col->{'SerialNumber'}) and ($col->{'SerialNumber'} = '---');
	
					($status,%tmp) = &load_product_info($sku_id_p);
					&load_cfg('sl_orders');
					$va{'productslist'} .= "  <td class='smalltext' valign='top'>$tmp{'model'}<br>".substr($tmp{'name'},0,30)." ".$choices."</td>\n";
					$va{'productslist'} .= "  <td class='smalltext' valign='top'> $col->{'SerialNumber'}</td>\n";
					$va{'productslist'} .= "  <td class='smalltext' valign='top'>".&build_tracking_link($col->{'Tracking'},$col->{'ShpProvider'},$col->{'ShpDate'},$col->{'ID_products'}).&remove_tracking($col->{'Tracking'},$col->{'ShpProvider'},$col->{'ShpDate'},$col->{'ID_orders_products'})."</td>\n";
	
					if ($col->{'Status'} eq 'Inactive'){
						$decor = " style=' text-decoration: line-through'";
					}else{
						$decor ='';
					}
					$va{'productslist'} .= "  <td class='smalltext' align='right' valign='top' $decor>".&format_number($col->{'Quantity'})."</td>\n";
					$va{'productslist'} .= "  <td class='smalltext' align='right' valign='top' $decor>".&format_price($unit_price)."</td>\n";
					$va{'productslist'} .= "  <td class='smalltext' align='right' valign='top' $decor>".&format_price($col->{'Shipping'})."";
					$va{'productslist'} .= "  </td>\n<td class='smalltext' align='right' valign='top' $decor nowrap>".&format_price($col->{'SalePrice'});
					#Se comenta edición de productos
					if (&check_permissions('edit_order_cleanup','','')){
						$va{'productslist'} .= qq| <div id="divpayment$rec->{'ID_orders_products'}"><a href="#tabs" onClick="popup_show('ajax_windows', 'ajax_drag', 'ajax_exit', 'element-right', -1, -1,'tabs');loadDoc('/cgi-bin/common/apps/ajaxbuild?ajaxbuild=edit_products&id_orders=$col->{'ID_orders'}&id_orders_products=$col->{'ID_orders_products'}&cmd=$in{'cmd'}&script_url=/cgi-bin/mod/$usr{'application'}/dbman');"><img src='$va{'imgurl'}/$usr{'pref_style'}/b_edit.png' title='Edit In Clean up Mode' alt='' border='0'></a></div>|;
					}
					$va{'productslist'} .= "</td>\n";
					$va{'productslist'} .= "</tr>\n";	
	
				}
			}else{
				$sku_id_p=$col->{'Related_ID_products'}-400000000;
				$sku_id_e=$col->{'Related_ID_products'};
				$sku_id_d=format_sltvid($col->{'Related_ID_products'});
				if ($col->{'Status'} ne 'Inactive')
				{
					$tot_qty += $col->{'Quantity'};
					$tot_ord +=$col->{'SalePrice'};
				}
				if($col->{'Related_ID_products'} < 99999 or substr($col->{'Related_ID_products'},0,1) == 6){
	      			(substr($col->{'Related_ID_products'},0,1) == 6) and ($col->{'Related_ID_products'} = substr($col->{'Related_ID_products'},5));
					$va{'productslist'} .= "<tr bgcolor='$c[$d]' onmouseover='m_over(this)' onmouseout='m_out(this)'>\n";
					$va{'productslist'} .= " <td class='smalltext' valign='top'>";
					if ((!$col->{'ShpDate'} or $col->{'ShpDate'} eq '0000-00-00') and $col->{'Status'} eq 'Active'){
						#$va{'productslist'} .= qq| <a href="/cgi-bin/mod/$usr{'application'}/dbman?cmd=opr_orders&view=$in{'id_orders'}&tab=1&drop=$col->{'ID_orders_products'}"><img src='$va{'imgurl'}/$usr{'pref_style'}/b_drop.png' title='Drop' alt='' border='0'></a>|;
					}
	
					my ($sth5) = &Do_SQL("SELECT * FROM sl_services WHERE ID_services = '$col->{'Related_ID_products'}' ;");
					$serdata = $sth5->fetchrow_hashref;
					$col->{'SerialNumber'}='';
					$col->{'ShpProvider'}='';
					$col->{'Tracking'}='';
					$col->{'ShpDate'}='';
					$va{'productslist'} .= "<br>".&format_sltvid(600000000+$col->{'Related_ID_products'})."</td>\n";		
					$va{'productslist'} .= "  <td class='smalltext'>$tmp{'model'}<br>".substr($serdata->{'Name'},0,30)."</td>\n";
					$va{'productslist'} .= "  <td class='smalltext' valign='top'>---</td>\n";
					$va{'productslist'} .= "  <td class='smalltext' valign='top'>".&build_tracking_link($col->{'Tracking'},$col->{'ShpProvider'},$col->{'ShpDate'},600000000+$col->{'Related_ID_products'})."</td>\n";			
					if ($col->{'Status'} eq 'Inactive'){
							$decor = " style=' text-decoration: line-through'";
					}else{
							$decor ='';
					}
					$va{'productslist'} .= "  <td class='smalltext' align='right' valign='top' $decor>".&format_number($col->{'Quantity'})."</td>\n";
					$va{'productslist'} .= "  <td class='smalltext' align='right' valign='top' $decor>".&format_price($unit_price)."</td>\n";
					$va{'productslist'} .= "  <td class='smalltext' align='right' valign='top' $decor>N/A&nbsp;&nbsp;&nbsp;</td>\n";
					$va{'productslist'} .= "  <td class='smalltext' align='right' valign='top' $decor nowrap>".&format_price($col->{'SalePrice'});
					#Se comenta edición de productos
					if (&check_permissions('edit_order_cleanup','','')){
						$va{'productslist'} .= qq| <div id="divpayment$rec->{'ID_orders_products'}"><a href="#tabs" onClick="popup_show('ajax_windows', 'ajax_drag', 'ajax_exit', 'element-right', -1, -1,'tabs');loadDoc('/cgi-bin/common/apps/ajaxbuild?ajaxbuild=edit_products&id_orders=$col->{'ID_orders'}&id_orders_products=$col->{'ID_orders_products'}&cmd=$in{'cmd'}&script_url=/cgi-bin/mod/$usr{'application'}/dbman');"><img src='$va{'imgurl'}/$usr{'pref_style'}/b_edit.png' title='Edit In Clean up Mode' alt='' border='0'></a></div>|;
					}
					$va{'productslist'} .= "</td>\n";
					$va{'productslist'} .= "</tr>\n";	
					
				}else{
					my (%tmp);
					$va{'productslist'} .= "<tr bgcolor='$c[$d]' onmouseover='m_over(this)' onmouseout='m_out(this)'>\n";
					$va{'productslist'} .= " <td class='smalltext' valign='top'>";
					if ((!$col->{'ShpDate'} or $col->{'ShpDate'} eq '0000-00-00') and $col->{'Status'} eq 'Active'){
						#$va{'productslist'} .= qq| <a href="/cgi-bin/mod/$usr{'application'}/dbman?cmd=opr_orders&view=$in{'id_orders'}&tab=1&drop=$col->{'ID_orders_products'}"><img src='$va{'imgurl'}/$usr{'pref_style'}/b_drop.png' title='Drop' alt='' border='0'></a>|;
					}
	            	### Products
	            	$va{'productslist'} .= "<br>".&format_sltvid($col->{'Related_ID_products'});
					$va{'productslist'} .= "</td>\n";
					(!$col->{'SerialNumber'}) and ($col->{'SerialNumber'} = '---');
	
					($status,%tmp) = &load_product_info($sku_id_p);
					&load_cfg('sl_orders');
					$cadname=&load_name('sl_parts','ID_parts',$sku_id_p,'Name');
					$cadmodel=&load_name('sl_parts','ID_parts',$sku_id_p,'Model');
					
					
					$va{'productslist'} .= "  <td class='smalltext' valign='top'>$cadmodel<br>".substr($cadname,0,30)." ".$choices."</td>\n";
					$va{'productslist'} .= "  <td class='smalltext' valign='top'> $col->{'SerialNumber'}</td>\n";
					$va{'productslist'} .= "  <td class='smalltext' valign='top'>".&build_tracking_link($col->{'Tracking'},$col->{'ShpProvider'},$col->{'ShpDate'},$col->{'ID_products'}).&remove_tracking($col->{'Tracking'},$col->{'ShpProvider'},$col->{'ShpDate'},$col->{'ID_orders_products'})."</td>\n";
	
					if ($col->{'Status'} eq 'Inactive'){
						$decor = " style=' text-decoration: line-through'";
					}else{
						$decor ='';
					}
					$va{'productslist'} .= "  <td class='smalltext' align='right' valign='top' $decor>".&format_number($col->{'Quantity'})."</td>\n";
					$va{'productslist'} .= "  <td class='smalltext' align='right' valign='top' $decor>".&format_price($unit_price)."</td>\n";
					$va{'productslist'} .= "  <td class='smalltext' align='right' valign='top' $decor>".&format_price($col->{'Shipping'})."";
					$va{'productslist'} .= "  </td>\n<td class='smalltext' align='right' valign='top' $decor nowrap>".&format_price($col->{'SalePrice'});
					#Se comenta edición de productos
					if (&check_permissions('edit_order_cleanup','','')){
						$va{'productslist'} .= qq| <div id="divpayment$rec->{'ID_orders_products'}"><a href="#tabs" onClick="popup_show('ajax_windows', 'ajax_drag', 'ajax_exit', 'element-right', -1, -1,'tabs');loadDoc('/cgi-bin/common/apps/ajaxbuild?ajaxbuild=edit_products&id_orders=$col->{'ID_orders'}&id_orders_products=$col->{'ID_orders_products'}&cmd=$in{'cmd'}&script_url=/cgi-bin/mod/$usr{'application'}/dbman');"><img src='$va{'imgurl'}/$usr{'pref_style'}/b_edit.png' title='Edit In Clean up Mode' alt='' border='0'></a></div>|;
					}
					$va{'productslist'} .= "</td>\n";
					$va{'productslist'} .= "</tr>\n";	
	
				}
				
				
			}
		}

		$va{'productslist'} .= qq|
			<tr>
				<td colspan='7' class='smalltext' align="right">|.&trans_txt('mer_vpo_total').qq|</td>
				<td align="right" class='smalltext'>|.&format_price($tot_ord).qq|</td>
			</tr>\n|;
	}else{
		$va{'pageslist'} = 1;
		$va{'productslist'} = qq|
			<tr>
				<td colspan='8' align="center">|.&trans_txt('search_nomatches').qq|</td>
			</tr>\n|;
	}
}


#############################################################################
#############################################################################
#   Function: build_payments_list
#
#
#
#    Created on: 2013-03-07
#
#    Author: _CARLOS HAAS_
#
#    Modifications:
#
#
#   Parameters:
#
#
#  Returns:
#
#      - 
#
#   See Also:
#
#
sub build_payments_list {
#############################################################################
#############################################################################
	my ($tot_pay);
	my (@c) = split(/,/,$cfg{'srcolors'});
	my ($sth) = &Do_SQL("SELECT COUNT(*) FROM sl_orders_payments WHERE ID_orders='$in{'id_orders'}'");
	$va{'matches'} = $sth->fetchrow;
	if($va{'matches'}>0){
		my ($sth) = &Do_SQL("SELECT * FROM sl_orders_payments WHERE ID_orders='$in{'id_orders'}'  ORDER BY Date DESC,CapDate DESC,Paymentdate DESC;");
		while ($rec = $sth->fetchrow_hashref){
			my $ajaxcmd_auth = 'creditcard';
			my $ajaxcmd_sale = 'ccsale';
			my $ajaxcmd_capture = 'capture';
			$d = 1 - $d;
			
				#####
				##### Captcolor debe ser una imagen en lugar de un color
				#####
				
				my $captcolor = '';
				$captcolor = 'color:blue;'	if($rec->{'AuthCode'} and $rec->{'AuthCode'} ne '' and $rec->{'AuthCode'} ne '0000' and (!$rec->{'Captured'} or $rec->{'Captured'} eq 'Yes') and (!$rec->{'CapDate'} or $rec->{'CapDate'} eq '' or $rec->{'CapDate'}eq'0000-00-00')); 
				$captcolor = 'color:green;'	if $rec->{'Captured'} eq 'Yes';
				
				my ($ccmethod) = &load_name('sl_orders_payments','ID_orders_payments',$rec->{'ID_orders_payments'},'PmtField3');	
				($ccmethod eq 'PayPal') and ($ajaxcmd_auth .= '_paypal') and ($ajaxcmd_sale .= '_paypal') and ($ajaxcmd_capture .= '_paypal');
			
			if ($rec->{'Type'} eq "Check"){
				$va{'paymentlist'} .= "<tr>\n";
				$va{'paymentlist'} .= "   <td class='menu_bar_title'>&nbsp;</td>\n";
				$va{'paymentlist'} .= "   <td class='menu_bar_title'>Name on Check</td>\n";
				$va{'paymentlist'} .= "   <td class='menu_bar_title'>Routing ABA/ Account/ Chk</td>\n";
				$va{'paymentlist'} .= "   <td class='menu_bar_title'>P/C</td>\n";
				$va{'paymentlist'} .= "   <td class='menu_bar_title'>D.O.B<br>License/State<br>Phone</td>\n";
				$va{'paymentlist'} .= "	<td class='menu_bar_title'>Status<br>Cod Auth</td>\n";
				$va{'paymentlist'} .= "	<td class='menu_bar_title'>Amount</td>\n";
				$va{'paymentlist'} .= "</tr>\n";
				$va{'paymentlist'} .= "<tr bgcolor='$c[$d]' onmouseover='m_over(this)' onmouseout='m_out(this)'>\n";
				$va{'paymentlist'} .= "   <td nowrap>";
				if ($rec->{'Status'} ne 'Cancelled' and $rec->{'Status'} ne 'Order Cancelled' and $rec->{'Status'} ne 'Void' and (($rec->{'Status'} ne 'Approved' or $rec->{'AuthCode'} eq '0000') or ($rec->{'Status'} eq 'Approved' and !$rec->{'AuthCode'}))){
					#$va{'paymentlist'} .= qq| <a href="/cgi-bin/mod/$usr{'application'}/dbman?cmd=opr_orders&view=$in{'id_orders'}&tab=2&drop=$rec->{'ID_orders_payments'}"><img src='$va{'imgurl'}/$usr{'pref_style'}/b_drop.png' title='Drop' alt='' border='0'></a>|;
					#$va{'paymentlist'} .= qq| <a href="/cgi-bin/mod/$usr{'application'}/dbman?cmd=opr_orders&view=$in{'id_orders'}&tab=2&auth=$rec->{'ID_orders_payments'}"><img src='$va{'imgurl'}/$usr{'pref_style'}/b_pauth.gif' title='Authorize' alt='' border='0'></a>|;
					$va{'paymentlist'} .= qq| <div id="divpayment$rec->{'ID_orders'}"><a href="#tabs" onClick="popup_show('ajax_windows', 'ajax_drag', 'ajax_exit', 'element-right', -1, -1,'tabs');loadDoc('/cgi-bin/common/apps/ajaxpayment?ajaxbuild=certegycheck&id_orders=$rec->{'ID_orders'}&id_orders_payments=$rec->{'ID_orders_payments'}&e=$in{'e'}');delete_div('divorder$rec->{'ID_orders'}');delete_div('divpayment$rec->{'ID_orders'}');"><img src='$va{'imgurl'}/$usr{'pref_style'}/b_pauth.gif' title='Authorize' alt='' border='0'></a></div>|;
				}
				
				if ($rec->{'Status'} eq 'Cancelled' or $rec->{'Status'} eq 'Order Cancelled'){
					$decor = " style=' text-decoration: line-through'";
				}else{
					$decor ='';
					$tot_pay += $rec->{'Amount'} if ($rec->{'Status'} ne 'Order Cancelled' and $rec->{'Status'} ne 'Cancelled');
				}
				
				$va{'paymentlist'} .= "   </td>"; 
				$va{'paymentlist'} .= "   <td class='smalltext' valign='top' $decor> $rec->{'PmtField1'}</td>\n";
				$va{'paymentlist'} .= "   <td class='smalltext' valign='top' $decor> $rec->{'PmtField2'}<div>$rec->{'PmtField3'}</div><div>$rec->{'PmtField4'}</div>";
				
				# shows the detail of the Banks Movements
				my ($sth_banksmovs) = &Do_SQL("SELECT sl_banks.BankName, sl_banks.Currency, sl_banks.SubAccountOf, sl_banks_movements.BankDate, sl_banks_movements.ID_banks_movements, sl_banks_movements.RefNum
					FROM sl_banks_movements INNER JOIN sl_banks_movrel USING(ID_banks_movements) INNER JOIN sl_banks USING(ID_banks) WHERE tablename = 'orders_payments'
					AND tableid = '".$rec->{'ID_orders_payments'}."';");
				while ($rec_banksmovs = $sth_banksmovs->fetchrow_hashref()) {
					$va{'paymentlist'} .= qq|<div onclick="trjump('/cgi-bin/mod/[ur_application]/dbman?cmd=fin_banks_movements&view=|.$rec_banksmovs->{'ID_banks_movements'}.qq|');">
					<div >|.$rec_banksmovs->{'BankName'}.qq|</div>
					<div >|.$rec_banksmovs->{'SubAccountOf'}.qq|</div>
					<div >|.$rec_banksmovs->{'BankDate'}.qq|</div>
					<div >|.$rec_banksmovs->{'RefNum'}.qq|</div>
					</div>|;
				}
				
				$va{'paymentlist'} .= "   </td>"; 
				$va{'paymentlist'} .= "   <td class='smalltext' valign='top' $decor> $rec->{'PmtField8'}</td>\n";
				$va{'paymentlist'} .= "   <td class='smalltext' valign='top' $decor> $rec->{'PmtField5'}<br> $rec->{'PmtField6'}<br>$rec->{'PmtField7'}<br>$rec->{'PmtField9'}</td>\n";
				$va{'paymentlist'} .= "   <td class='smalltext' valign='top' $decor> $rec->{'Status'}<br>$rec->{'AuthCode'}</td>\n";							
				$va{'paymentlist'} .= "   <td class='smalltext' valign='top' $decor align='right'> ".&format_price($rec->{'Amount'})."<br>$rec->{'Paymentdate'}<br><span style='$captcolor'>$rec->{'CapDate'}</span>\n";
				#Se comenta edición de pagos.
				if (&check_permissions('edit_order_cleanup','','')){
					$va{'paymentlist'} .= qq| <div id="divpayment$rec->{'ID_orders_products'}"><a href="#tabs" onClick="popup_show('ajax_windows', 'ajax_drag', 'ajax_exit', 'element-right', -1, -1,'tabs');loadDoc('/cgi-bin/common/apps/ajaxbuild?ajaxbuild=edit_payments&id_orders=$rec->{'ID_orders'}&id_orders_payments=$rec->{'ID_orders_payments'}&cmd=$in{'cmd'}&script_url=/cgi-bin/mod/$usr{'application'}/dbman');"><img src='$va{'imgurl'}/$usr{'pref_style'}/b_edit.png' title='Edit In Clean up Mode' alt='' border='0'></a></div>|;
				}
				$va{'paymentlist'} .= "</td>\n";
				$va{'paymentlist'} .= "</tr>\n";					
			}elsif($rec->{'Type'} eq "WesternUnion"){
				$va{'paymentlist'} .= "<tr>\n";
				$va{'paymentlist'} .= "   <td class='menu_bar_title' colspan='5'>WesterUnion Payment</td>\n";
				$va{'paymentlist'} .= "	<td class='menu_bar_title'>Status<br>Cod Auth</td>\n";							
				$va{'paymentlist'} .= "	<td class='menu_bar_title'>Amount</td>\n";
				$va{'paymentlist'} .= "</tr>\n";
				$va{'paymentlist'} .= "<tr bgcolor='$c[$d]' onmouseover='m_over(this)' onmouseout='m_out(this)'>\n";
				$va{'paymentlist'} .= "   <td nowrap>";
				if ($rec->{'Status'} ne 'Cancelled' and $rec->{'Status'} ne 'Order Cancelled' and $rec->{'Status'} ne 'Void' and ($rec->{'Status'} ne 'Approved' or $rec->{'AuthCode'} eq '0000')){
					#$va{'paymentlist'} .= qq| <a href="/cgi-bin/mod/$usr{'application'}/dbman?cmd=opr_orders&view=$in{'id_orders'}&tab=2&drop=$rec->{'ID_orders_payments'}"><img src='$va{'imgurl'}/$usr{'pref_style'}/b_drop.png' title='Drop' alt='' border='0'></a>|;
				}
				
				if ($rec->{'Status'} eq 'Cancelled' or $rec->{'Status'} eq 'Order Cancelled'){
					$decor = " style=' text-decoration: line-through'";
				}else{
					$decor ='';
					$tot_pay += $rec->{'Amount'} if ($rec->{'Status'} ne 'Order Cancelled' and $rec->{'Status'} ne 'Cancelled');
				}
				
				$va{'paymentlist'} .= "   </td>";
				$va{'paymentlist'} .= "   <td class='smalltext' valign='top' $decor colspan='4'> No Information Required For WU Payments</td>\n";
				$va{'paymentlist'} .= "   <td class='smalltext' valign='top' $decor> $rec->{'Status'}<br>$rec->{'AuthCode'}</td>\n";							
				$va{'paymentlist'} .= "   <td class='smalltext' valign='top' $decor align='right'> ".&format_price($rec->{'Amount'})."<br>$rec->{'Paymentdate'}<br><span style='$captcolor'>$rec->{'CapDate'}</span></td>\n";
				$va{'paymentlist'} .= "</tr>\n";	
			}elsif($rec->{'Type'} eq "Credit-Card"){
				$va{'paymentlist'} .= "<tr>\n";
				$va{'paymentlist'} .= "   <td class='menu_bar_title'>Select</td>\n";
				$va{'paymentlist'} .= "   <td class='menu_bar_title'>Type</td>\n";
				$va{'paymentlist'} .= "   <td class='menu_bar_title'>Name on Card<br>Card Number</td>\n";
				$va{'paymentlist'} .= "   <td class='menu_bar_title'>Exp</td>\n";
				$va{'paymentlist'} .= "   <td class='menu_bar_title'>CVN</td>\n";
				$va{'paymentlist'} .= "	<td class='menu_bar_title'>Status<br>Cod Auth</td>\n";			
				$va{'paymentlist'} .= "	<td class='menu_bar_title'>Amount</td>\n";
				$va{'paymentlist'} .= " </tr>\n";
				$va{'paymentlist'} .= " <tr bgcolor='$c[$d]' onmouseover='m_over(this)' onmouseout='m_out(this)'>\n";
				$va{'paymentlist'} .= "   <td nowrap>";

				## CC Mask for operator|user|cdr only users				
				(!&check_permissions('view_info_tdc','','')) and ($rec->{'PmtField3'} = 'xxxx-xxxx-xxxx-'.substr($rec->{'PmtField3'},-4));
				if ($rec->{'Captured'} eq 'Yes' or $rec->{'Status'} eq 'Order Cancelled' or $rec->{'Status'} eq 'Cancelled' or $rec->{'Status'} eq 'Void'){
					$va{'paymentlist'} .= '&nbsp;';
					if ($rec->{'Status'} eq 'Financed' and &check_permissions('edit_order_cleanup','','')){
						$va{'paymentlist'} .= "<input type='checkbox' class='checkbox' name='changepayments' value='$rec->{'ID_orders_payments'}'>\n";
					}

				#}elsif ($rec->{'AuthCode'}>0){
				}elsif ($rec->{'AuthCode'} ne '' and length($rec->{'AuthCode'}) >= 2){
					if(&check_permissions('order_capture_payments','','')) {
						$va{'paymentlist'} .= qq| <div id="divpayment$rec->{'ID_orders_payments'}"><a href="#order$rec->{'ID_orders'}" id='ajax_btn' onClick="popup_show('ajax_windows', 'ajax_drag', 'ajax_exit', 'element-right', -1, -1,'tabsl');loadDoc('/cgi-bin/common/apps/ajaxpayment?ajaxbuild=$ajaxcmd_capture&id_orders=$rec->{'ID_orders'}&id_orders_payments=$rec->{'ID_orders_payments'}&e=$in{'e'}');delete_div('divpayment$rec->{'ID_orders_payments'}');"><img src='$va{'imgurl'}/$usr{'pref_style'}/b_cauth.gif' title='Capture' alt='' border='0'></a></div>|;
					}
				#############
				#############
				# Customer Credit
				#############
				#############
				}elsif ($rec->{'Amount'}<0 and $rec->{'Status'}ne'Credit by Monterey'){
					########### Solamente Developers y el Area de Finanzas puede capturar una devolucion de dinero

					if(&check_permissions('order_capture_credits','','')) {
						$va{'paymentlist'} .= qq| <div id="divpayment$rec->{'ID_orders'}"><a href="#order$rec->{'ID_orders'}" id='ajax_btn' onClick="popup_show('ajax_windows', 'ajax_drag', 'ajax_exit', 'element-right', -1, -1,'tabsl');loadDoc('/cgi-bin/common/apps/ajaxpayment?ajaxbuild=cccredit&id_orders=$rec->{'ID_orders'}&id_orders_payments=$rec->{'ID_orders_payments'}&e=$in{'e'}');delete_div('divorder$rec->{'ID_orders'}');delete_div('divpayment$rec->{'ID_orders'}');"><img src='$va{'imgurl'}/$usr{'pref_style'}/b_pauth.gif' title='Authorize' alt='' border='0'></a></div>|;
					}
					
					if(&check_permissions('edit_order_cleanup','','')){
						$va{'paymentlist'} .= "<input type='checkbox' class='checkbox' name='changepayments' value='$rec->{'ID_orders_payments'}'>\n";
					}else{
						$va{'paymentlist'} .= '&nbsp;';
					}

				}elsif ( $rec->{'Status'} ne 'Cancelled' and $rec->{'Status'}ne'Credit by Monterey' and (($rec->{'Status'} ne 'Approved' or $rec->{'AuthCode'} eq '0000') or ($rec->{'Status'} eq 'Approved' and !$rec->{'AuthCode'}))){
					## Auth and Sale
					#$va{'paymentlist'} .= qq| <a href="/cgi-bin/mod/$usr{'application'}/dbman?cmd=opr_orders&view=$in{'id_orders'}&tab=2&drop=$rec->{'ID_orders_payments'}"><img src='$va{'imgurl'}/$usr{'pref_style'}/b_drop.png' title='Drop' alt='' border='0'></a>|;
					#&cgierr(2);
					if(&check_permissions('order_authorize_payments','','')) {
						$va{'paymentlist'} .= qq| <div id="divpayment$rec->{'ID_orders'}"><a href="#order$rec->{'ID_orders'}" id='ajax_btn' onClick="popup_show('ajax_windows', 'ajax_drag', 'ajax_exit', 'element-right', -1, -1,'tabsl');loadDoc('/cgi-bin/common/apps/ajaxpayment?ajaxbuild=$ajaxcmd_auth&id_orders=$rec->{'ID_orders'}&id_orders_payments=$rec->{'ID_orders_payments'}&e=$in{'e'}');delete_div('divorder$rec->{'ID_orders'}');delete_div('divpayment$rec->{'ID_orders'}');"><img src='$va{'imgurl'}/$usr{'pref_style'}/b_pauth.gif' title='Authorize' alt='' border='0'></a></div>|;
					}

					if(&check_permissions('order_capture_payments','','')) {
						$va{'paymentlist'} .= qq| <div id="divpayment$rec->{'ID_orders'}"><a href="#order$rec->{'ID_orders'}" id='ajax_btn' onClick="popup_show('ajax_windows', 'ajax_drag', 'ajax_exit', 'element-right', -1, -1,'tabsl');loadDoc('/cgi-bin/common/apps/ajaxpayment?ajaxbuild=$ajaxcmd_sale&id_orders=$rec->{'ID_orders'}&id_orders_payments=$rec->{'ID_orders_payments'}&e=$in{'e'}');delete_div('divorder$rec->{'ID_orders'}');delete_div('divpayment$rec->{'ID_orders'}');"><img src='$va{'imgurl'}/$usr{'pref_style'}/b_fpauth.gif' title='Facil Pago Authorize/Capture' alt='' border='0'></a></div>|;
					}

					if(&check_permissions('order_change_payments','','')) {
						$va{'paymentlist'} .= "<input type='checkbox' class='checkbox' name='changepayments' value='$rec->{'ID_orders_payments'}'>\n";
					}

				}elsif($rec->{'Status'} eq 'Approved' and $rec->{'AuthCode'} and $rec->{'AuthCode'} ne '0000' and $rec->{'Captured'} ne 'Yes'){
					## Capture & Force Capt
					if(&check_permissions('order_capture_payments','','')) {
						$va{'paymentlist'} .= qq| <div id="divpayment$rec->{'ID_orders_payments'}"><a href="#order$rec->{'ID_orders'}" id='ajax_btn' onClick="popup_show('ajax_windows', 'ajax_drag', 'ajax_exit', 'element-right', -1, -1,'tabsl');loadDoc('/cgi-bin/common/apps/ajaxpayment?ajaxbuild=$ajaxcmd_capture&id_orders=$rec->{'ID_orders'}&id_orders_payments=$rec->{'ID_orders_payments'}&e=$in{'e'}');delete_div('divpayment$rec->{'ID_orders_payments'}');"><img src='$va{'imgurl'}/$usr{'pref_style'}/b_cauth.gif' title='Capture' alt='' border='0'></a></div>|;
					}

					#($btns =~ /x/i) and ($va{'paymentlist'} .= qq| <div id="divpayment$rec->{'ID_orders_payments'}"><a href="#order$rec->{'ID_orders'}" id='ajax_btn' onClick="popup_show('ajax_windows', 'ajax_drag', 'ajax_exit', 'element-right', -1, -1,'tabs');loadDoc('/cgi-bin/common/apps/ajaxpayment?ajaxbuild=tocapture&id_orders=$rec->{'ID_orders'}&id_orders_payments=$rec->{'ID_orders_payments'}&e=$in{'e'}');delete_div('divpayment$rec->{'ID_orders_payments'}');"><img src='$va{'imgurl'}/$usr{'pref_style'}/b_xauth.gif' title='To Capture' alt='' border='0'></a></div>|);
					$va{'paymentlist'} .= "&nbsp;&nbsp;&nbsp;&nbsp;";
				}else{
					$va{'paymentlist'} .=  qq|<img src='$va{'imgurl'}/$usr{'pref_style'}/auth-fu.png' width='14' height='14' title='Authorized' alt='' border='0'>|	if($rec->{'AuthCode'} and $rec->{'AuthCode'} ne '' and $rec->{'AuthCode'} ne '0000' and (!$rec->{'Captured'} or $rec->{'Captured'} eq 'Yes') and (!$rec->{'CapDate'} or $rec->{'CapDate'} eq '' or $rec->{'CapDate'}eq'0000-00-00')); 
					$va{'paymentlist'} .=  qq|<img src='$va{'imgurl'}/$usr{'pref_style'}/capt-fu.png' width='14' height='14' title='Captured' alt='' border='0'>|	if $rec->{'Captured'} eq 'Yes';
				}
				
				if ($rec->{'Status'} eq 'Cancelled' or $rec->{'Status'} eq 'Order Cancelled'){
					$decor = " style=' text-decoration: line-through'";
				}else{
					$decor ='';
					$tot_pay += $rec->{'Amount'} if ($rec->{'Status'} ne 'Order Cancelled' and $rec->{'Status'} ne 'Cancelled');
				}
				
				$va{'paymentlist'} .= "   </td>";
				$va{'paymentlist'} .= "   <td class='smalltext' $decor valign='top'>$rec->{'PmtField1'}<br>$rec->{'PmtField7'}</td>\n";
				$va{'paymentlist'} .= "   <td class='smalltext' $decor valign='top'>$rec->{'PmtField2'}<br>$rec->{'PmtField3'}</td>\n";
				$va{'paymentlist'} .= "   <td class='smalltext' $decor valign='top'>$rec->{'PmtField4'}</td>\n";
				$va{'paymentlist'} .= "   <td class='smalltext' $decor valign='top'>$rec->{'PmtField5'}</td>\n";
				$va{'paymentlist'} .= "   <td class='smalltext' $decor valign='top'>$rec->{'Status'}<br>$rec->{'AuthCode'}</td>\n";
				$va{'paymentlist'} .= "   <td class='smalltext' $decor align='right' valign='top'> ".&format_price($rec->{'Amount'})."<br>$rec->{'Paymentdate'}<br><span style='$captcolor'>$rec->{'CapDate'}</span>\n";
				#Se comenta edición de pagos.
				if (&check_permissions('edit_order_cleanup','','')){
					$va{'paymentlist'} .= qq| <div id="divpayment$rec->{'ID_orders_products'}"><a href="#tabs" onClick="popup_show('ajax_windows', 'ajax_drag', 'ajax_exit', 'element-right', -1, -1,'tabs');loadDoc('/cgi-bin/common/apps/ajaxbuild?ajaxbuild=edit_payments&id_orders=$rec->{'ID_orders'}&id_orders_payments=$rec->{'ID_orders_payments'}&cmd=$in{'cmd'}&script_url=/cgi-bin/mod/$usr{'application'}/dbman');"><img src='$va{'imgurl'}/$usr{'pref_style'}/b_edit.png' title='Edit In Clean up Mode' alt='' border='0'></a></div>|;
				}
				$va{'paymentlist'} .= "</td>\n";
				$va{'paymentlist'} .= "</tr>\n";
			}else{
				$va{'paymentlist'} .= "<tr>\n";
				$va{'paymentlist'} .= "   <td class='menu_bar_title'>&nbsp;</td>\n";
				$va{'paymentlist'} .= "   <td class='menu_bar_title'>Type</td>\n";
				$va{'paymentlist'} .= "	<td class='menu_bar_title'>Pay Form</td>\n";	
				$va{'paymentlist'} .= "   <td class='menu_bar_title' colspan='2'>Manual Payment</td>\n";
				$va{'paymentlist'} .= "	<td class='menu_bar_title'>Status</td>\n";	
				$va{'paymentlist'} .= "	<td class='menu_bar_title'>Amount</td>\n";
				$va{'paymentlist'} .= " </tr>\n";
				
				if ($rec->{'Status'} eq 'Cancelled' or $rec->{'Status'} eq 'Order Cancelled'){
					$decor = " style=' text-decoration: line-through'";
				}else{
					$decor ='';
					$tot_pay += $rec->{'Amount'} if ($rec->{'Status'} ne 'Order Cancelled' and $rec->{'Status'} ne 'Cancelled');
				}
				
				$va{'paymentlist'} .= " <tr bgcolor='$c[$d]' onmouseover='m_over(this)' onmouseout='m_out(this)'>\n";
				$va{'paymentlist'} .= "   <td>&nbsp;</td>\n";
				$va{'paymentlist'} .= "   <td class='smalltext' nowrap $decor>$rec->{'Type'}</td>";
				$va{'paymentlist'} .= "   <td class='smalltext' nowrap $decor>$rec->{'PmtField1'}</td>";
				$va{'paymentlist'} .= "   <td class='smalltext' $decor valign='top' colspan='2' $decor> No Extra Information Required for This Type of Payment $rec->{'PmtField9'}</td>\n";
				$va{'paymentlist'} .= "   <td class='smalltext' $decor valign='top' $decor> $rec->{'Status'}<br>$rec->{'AuthCode'}</td>\n";
				$va{'paymentlist'} .= "   <td class='smalltext' $decor align='right' valign='top' $decor> ".&format_price($rec->{'Amount'})."<br>$rec->{'Paymentdate'}<br><span style='$captcolor'>$rec->{'CapDate'}</span>\n";
				#Se comenta edición de pagos.
				if (&check_permissions('edit_order_cleanup','','')){
					$va{'paymentlist'} .= qq| <div id="divpayment$rec->{'ID_orders_products'}"><a href="#tabs" onClick="popup_show('ajax_windows', 'ajax_drag', 'ajax_exit', 'element-right', -1, -1,'tabs');loadDoc('/cgi-bin/common/apps/ajaxbuild?ajaxbuild=edit_payments&id_orders=$rec->{'ID_orders'}&id_orders_payments=$rec->{'ID_orders_payments'}&cmd=$in{'cmd'}&script_url=/cgi-bin/mod/$usr{'application'}/dbman');"><img src='$va{'imgurl'}/$usr{'pref_style'}/b_edit.png' title='Edit In Clean up Mode' alt='' border='0'></a></div>|;
				}

				$va{'paymentlist'} .= "</td>\n";
				$va{'paymentlist'} .= "</tr>\n";
			}
			
			if (!$in{'action'}){
				for (1..8){
					$in{'pmtfield'.$_} = $rec->{'PmtField'.$_};
				}
				if ($rec->{'Type'} eq "Check"){
					$in{'month'} = substr($rec->{'PmtField5'},0,2);
					$in{'day'} = substr($rec->{'PmtField5'},3,2);
					$in{'year'} = substr($rec->{'PmtField5'},6,4);
				}else{
					$in{'month'} = substr($rec->{'PmtField4'},0,2);
					$in{'year'} = substr($rec->{'PmtField4'},2,2);
				}
			}			
						
		}		
		if (&check_permissions('edit_order_cleanup','','')){			
			$va{'flexipago'} = qq|&nbsp; - &nbsp; <a href='#tabs'>Update Dates</a>|;
		}
		$va{'paymentlist'} .= qq|
			<tr>
				<td colspan='6' class='smalltext' align="right">|.&trans_txt('mer_vpo_total').qq|</td>
				<td align="right" class='smalltext'>|.&format_price($tot_pay).qq|</td>
			</tr>\n|;
			
			
			
		&auth_logging('opr_orders_viewpay',$in{'id_orders'});
	}else{
		$va{'pageslist'} = 1;
		$va{'paymentlist'} = qq|
		    <tr>
				<td colspan='8' class='menu_bar_title' align="center">&nbsp;</td>
			</tr>
			<tr>
				<td colspan='8' align="center">|.&trans_txt('search_nomatches').qq|</td>
			</tr>\n|;
	}

}

1;

