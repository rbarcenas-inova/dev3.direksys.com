
sub load_product_info {
# --------------------------------------------------------
# Last Modified on: 03/17/09 17:21:37
# Last Modified by: MCC C. Gabriel Varela S: Parámetros sltv_itemshipping
# Last Modified By RB on 12/16/2010 : Se agregan parametros para calculo con shipping_table

	my ($id) = @_;
	&load_cfg('sl_products');
	(length($id)>6) and ($id = substr($id,3,6));
	
	my (%tmp) = &get_record('ID_products',$id,'sl_products');
	if ($tmp{'id_products'}>0){
		foreach my $key (keys %tmp){
			$in{$key} = $tmp{$key};
		}
		my ($shptotal1,$shptotal2,$shptotal3,$shptotal1pr,$shptotal2pr,$shptotal3pr,$shp_text1,$shp_text2,$shp_text3,$shp_textpr1,$shp_textpr2,$shp_textpr3) = &sltv_itemshipping($in{'edt'},$in{'SizeW'},$in{'SizeH'},$in{'SizeL'},$in{'Weight'},$in{'ID_packingopts'},$in{'shipping_table'},$in{'shipping_discount'},$in{'id_products'});
		$va{'shptotal1'}   = &format_price($va{'shptotal1'});
		$va{'shptotal2'}   = &format_price($va{'shptotal2'});
		$va{'shptotal1pr'} = &format_price($va{'shptotal1pr'});
		$va{'shptotal2pr'} = &format_price($va{'shptotal2pr'});
	
		
		### Calculate Shipping Charges
		#$size = $tmp{'sizew'}*$tmp{'sizeh'}*$tmp{'sizel'};
		#$weight = $tmp{'weight'};
		
		#($va{'shptype1_1lb'},$va{'shptype2_1lb'},$va{'shptype3_1lb'}) = split(/,/,$cfg{'shp_factors1'});
		#($va{'shptype1_add'},$va{'shptype2_add'},$va{'shptype3_add'}) = split(/,/,$cfg{'shp_factors2'});
		#($va{'shpconv1'},$va{'shpconv2'},$va{'shpconv3'}) = split(/,/,$cfg{'shp_wvconv'});
		#$weight = int($size/$va{'shpconv1'}+0.999);
		#if ($weight < $tmp{'weight'}){
		#	$weight = $tmp{'weight'};
		#}
		#if ($weight>1){
		#	$weight = int($va{'shptype1_1lb'} + $va{'shptype1_add'}*($weight- 1 + 0.99));
		#}else{
		#	$weight = $va{'shptype1_1lb'};
		#}
		$tmp{'shpcharges'} = &format_price($weight);
		
		#### MSRP
		$tmp{'msrp'} = &format_price($tmp{'msrp'});
		
		### Brands
		if ($tmp{'id_brands'}){
			$tmp{'brands_name'} = &load_name('sl_brands','ID_brands',$tmp{'id_brands'},'Name');
		}else{
			$tmp{'id_brands'} = '---';
			$tmp{'brands_name'} = '';
		}
		return ('ok',%tmp);
	}else{
		return 'error';
	}
}


#RB Start - Adding Non Inventory Items Info - apr2408
sub load_services_info {
# --------------------------------------------------------
	my ($id) = @_;
	&load_cfg('sl_services');
	(length($id)>6) and ($id = substr($id,5));
	
	my (%tmp) = &get_record('ID_services',$id,'sl_services');
	if ($tmp{'id_services'}>0){
		
		foreach my $key (keys %tmp){
			$in{$key} = $tmp{$key};
		}				
		return ('ok',%tmp);
	}else{
		return 'error';
	}
}
#RB End

sub load_order_products {
# --------------------------------------------------------
# Author: Unknown
# Created on: Unknown
# Last Modified on: 08/18/2008
# Last Modified by: Jose Ramirez Garcia
# Description : Se agrego el parametro de products a la funcion build_tracking_link
# Forms Involved: 
# Parameters : 
# Last Modified by RB : Se agrega informacion de parte cuando se trata de orden de exportacion

	my ($output,$col,$d,$rec,$choices,$tot_qty,$tot_ord,$link);
	my ($sth) = &Do_SQL("SELECT COUNT(*) FROM sl_orders_products WHERE ID_orders='$in{'id_orders'}' AND Status!='Inactive'");
	$va{'matches'} = $sth->fetchrow;
	if ($va{'matches'}>0){
		my ($sth1) = &Do_SQL("SELECT * FROM sl_orders_products WHERE ID_orders='$in{'id_orders'}' AND Status!='Inactive' ORDER BY ID_orders_products  DESC;");
		while ($col = $sth1->fetchrow_hashref){

			if(&is_exportation_order($in{'id_orders'})){
			      $sku_id_p = $col->{'Related_ID_products'}-400000000;
			      $sku_id_e=$col->{'Related_ID_products'};
			}else{
			      $sku_id_p = $col->{'ID_products'}; 
			}

			$d = 1 - $d;
			$output .= "<tr bgcolor='$c[$d]'>\n";
			$output .= "   <td class='smalltext' valign='top'>".&format_sltvid($col->{'ID_products'})." </td>\n";
			(!$col->{'SerialNumber'}) and ($col->{'SerialNumber'} = '---');

		
			(substr($col->{'ID_products'},0,1) ne 6) and (($status,%tmp) = &load_product_info($sku_id_p));
			(substr($col->{'ID_products'},0,1) eq 6) and (($status,%tmp) = &load_services_info($sku_id_p));
			$tmp{'model'} = &load_name('sl_parts','ID_parts',$sku_id_p,'Model')	if &is_exportation_order($in{'id_orders'});
			$tmp{'name'} = &load_name('sl_parts','ID_parts',$sku_id_p,'Name')	if &is_exportation_order($in{'id_orders'});

			$output .= "  <td class='smalltext'>$tmp{'model'}<br>".substr($tmp{'name'},0,30)."<br>".&load_choices($col->{'ID_products'})."</td>\n";
			$output .= "  <td class='smalltext'> $col->{'SerialNumber'}</td>\n";
			if($col->{'Tracking'} && $col->{'ShpProvider'} && $col->{'ShpDate'}){#JRG show the return date
				$output .= "  <td class='smalltext' valign='top'>".&build_tracking_link($col->{'Tracking'},$col->{'ShpProvider'},$col->{'ShpDate'},$col->{'ID_products'})."</td>\n";
			} else {
				$returndate = &load_name('sl_returns','ID_orders_products',$col->{'ID_orders_products'},'Date');
				if($returndate){
					$output .= "  <td class='smalltext' valign='top'>".$returndate."</td>\n";
				} else {
					$output .= "  <td class='smalltext' valign='top'>N / A</td>\n";
				}
			}
			$tot_qty += $col->{'Quantity'};
			(!&is_exportation_order($in{'id_orders'})) ?
			    $tot_ord +=$col->{'SalePrice'}*$col->{'Quantity'} :
			    $tot_ord +=$col->{'SalePrice'};
			
			$output .= "  <td class='smalltext' align='right'>".&format_number($col->{'Quantity'})."</td>\n";
			$output .= "  <td class='smalltext' align='right'>".&format_price($col->{'SalePrice'})."</td>\n";
			$output .= "</tr>\n";						
		}
		$output .= qq|
			<tr>
				<td colspan='5' class='smalltext' align="right">|.&trans_txt('mer_vpo_total').qq|</td>
				<td align="right" class='smalltext'>|.&format_price($tot_ord).qq|</td>
			</tr>\n|;
	}else{
		$output = qq|
			<tr>
				<td colspan='6' align="center">|.&trans_txt('search_nomatches').qq|</td>
			</tr>\n|;
	}	
}

sub load_order_payments {
# --------------------------------------------------------
# Last Modified by RB : Se agrega informacion
	
	## Payment List
	my ($tot_pay,$output);
	my (@c) = split(/,/,$cfg{'srcolors'});
	my ($sth) = &Do_SQL("SELECT COUNT(*) FROM sl_orders_payments WHERE ID_orders='$in{'id_orders'}'");
	$va{'matches'} = $sth->fetchrow;
	if($va{'matches'}>0){
		my ($sth) = &Do_SQL("SELECT * FROM sl_orders_payments WHERE ID_orders='$in{'id_orders'}' AND Status NOT IN('Order Cancelled','Cancelled') ORDER BY ID_orders_payments  DESC;");
		while ($rec = $sth->fetchrow_hashref){
			$d = 1 - $d;
			$tot_pay += $rec->{'Amount'};
			if ($rec->{'Type'} eq "Check"){
				$output .= "<tr>\n";
				$output .= "   <td class='menu_bar_title'>Name on Check</td>\n";
				$output .= "   <td class='menu_bar_title'>Routing ABA/ Account/ Chk</td>\n";
				$output .= "   <td class='menu_bar_title'>P/C</td>\n";
				$output .= "   <td class='menu_bar_title'>D.O.B<br>License/State<br>Phone</td>\n";
				$output .= "	<td class='menu_bar_title'>Status<br>Cod Auth</td>\n";							
				$output .= "	<td class='menu_bar_title'>Amount</td>\n";
				$output .= "</tr>\n";
				$output .= "<tr>\n";
				$output .= "   <td class='smalltext' valign='top' $decor> $rec->{'PmtField1'}</td>\n";
				$output .= "   <td class='smalltext' valign='top' $decor> $rec->{'PmtField2'}<br>$rec->{'PmtField3'}<br>$rec->{'PmtField4'}</td>\n";
				$output .= "   <td class='smalltext' valign='top' $decor> $rec->{'PmtField8'}</td>\n";
				$output .= "   <td class='smalltext' valign='top' $decor> $rec->{'PmtField5'}<br> $rec->{'PmtField6'}<br>$rec->{'PmtField7'}<br>$rec->{'PmtField9'}</td>\n";
				$output .= "   <td class='smalltext' valign='top' $decor> $rec->{'Status'}<br>$rec->{'AuthCode'}</td>\n";							
				$output .= "   <td class='smalltext' valign='top' $decor align='right'> ".&format_price($rec->{'Amount'})."</td>\n";
				$output .= "</tr>\n";					
			}elsif($rec->{'Type'} eq "WesternUnion"){
				$output .= "<tr>\n";
				$output .= "   <td class='menu_bar_title' colspan='4'>WesterUnion Payment</td>\n";
				$output .= "	<td class='menu_bar_title'>Status<br>Cod Auth</td>\n";							
				$output .= "	<td class='menu_bar_title'>Amount</td>\n";
				$output .= "</tr>\n";
				$output .= "<tr>\n";
				$output .= "   <td class='smalltext' valign='top' $decor colspan='4'> No Information Required For WU Payments</td>\n";
				$output .= "   <td class='smalltext' valign='top' $decor> $rec->{'Status'}<br>$rec->{'AuthCode'}</td>\n";							
				$output .= "   <td class='smalltext' valign='top' $decor align='right'> ".&format_price($rec->{'Amount'})."</td>\n";
				$output .= "</tr>\n";
			 }elsif($rec->{'Type'} eq "Credit-Card"){
				$output .= "<tr>\n";
				$output .= "   <td class='menu_bar_title'>Type</td>\n";
				$output .= "   <td class='menu_bar_title'>Name on Card<br>Card Number</td>\n";
				$output .= "   <td class='menu_bar_title'>Exp</td>\n";
				$output .= "   <td class='menu_bar_title'>CVN</td>\n";
				$output .= "	<td class='menu_bar_title'>Status<br>Cod Auth</td>\n";			
				$output .= "	<td class='menu_bar_title'>Amount</td>\n";
				$output .= " </tr>\n";
				$output .= " <tr>\n";
				$output .= "   <td class='smalltext' $decor valign='top'> $rec->{'PmtField1'}</td>\n";
				#$output .= "   <td class='smalltext' $decor valign='top'> $rec->{'PmtField2'}<br>$rec->{'PmtField3'}</td>\n";
				$output .= "   <td class='smalltext' $decor valign='top'> $rec->{'PmtField2'}<br>";
				#$usr(group); #$rec->{'PmtField3'}kkk</td>\n";
				
				### modified by rafael on 2007-10-09 @6:07PM - Hide credit card to some users
				if ($usr{'usergroup'} eq 1 and $usr{'usergroup'} eq 2){
					$output .= "$rec->{'PmtField3'}</td>\n";
				}else{
					my ($cc) = $rec->{'PmtField3'};
					$output .= "xxxx-xxxx-xxxx-".substr($cc,$#cc-4,4)."</td>\n";
				}
				###############################################################################
				$output .= "   <td class='smalltext' $decor valign='top'> $rec->{'PmtField4'}</td>\n";
				$output .= "   <td class='smalltext' $decor valign='top'> $rec->{'PmtField5'}</td>\n";
				$output .= "   <td class='smalltext' $decor valign='top'> $rec->{'Status'}<br>$rec->{'AuthCode'}</td>\n";
				$output .= "   <td class='smalltext' $decor align='right' valign='top'> ".&format_price($rec->{'Amount'})."<br>$rec->{'Paymentdate'}</td>\n";
				$output .= "</tr>\n";
			}else{
				$output .= "<tr>\n";
				$output .= "   <td class='menu_bar_title'>Payment Type</td>\n";
				$output .= "   <td class='menu_bar_title' colspan='3'>Manual Payment</td>\n";
				$output .= "	<td class='menu_bar_title'>Status/Auth. Code</td>\n";							
				$output .= "	<td class='menu_bar_title'>Amount/CapDate</td>\n";
				$output .= "</tr>\n";
				$output .= "<tr>\n";
				$output .= "   <td class='smalltext' valign='top'>$rec->{'Type'}</td>\n";
				$output .= "   <td class='smalltext' valign='top' $decor colspan='3'> No Information Required For This Type of Payment </td>\n";
				$output .= "   <td class='smalltext' valign='top' $decor> $rec->{'Status'}<br>$rec->{'AuthCode'}</td>\n";							
				$output .= "   <td class='smalltext' valign='top' $decor align='right'> ".&format_price($rec->{'Amount'})."<br><strong>$rec->{'CapDate'}</strong></td>\n";
				$output .= "</tr>\n";
			}
		}
		$output .= qq|
			<tr>
				<td colspan='5' class='smalltext' align="right">|.&trans_txt('mer_vpo_total').qq|</td>
				<td align="right" class='smalltext'>|.&format_price($tot_pay).qq|</td>
			</tr>\n|;
	}else{
		$va{'pageslist'} = 1;
		$va{'searchresults'} = qq|
			<tr>
				<td colspan='8' align="center">|.&trans_txt('search_nomatches').qq|</td>
			</tr>\n|;
	}
	return $output;
}


sub load_inv_products {
# --------------------------------------------------------
	return &load_ordproducts_list('std');
}

sub load_inv_upcproducts {
# --------------------------------------------------------
	return &load_ordproducts_list('upc');
}

sub load_inv_cusupcproducts {
# --------------------------------------------------------
	return &load_ordproducts_list('custupc');
}


sub load_ordproducts_list {
# --------------------------------------------------------
	my ($list_type) = @_;
	my ($style,$output,$tot_qty,$tot_ord,$choices,$prefix,$id_products);
	
	### TODO: Parametrizar en template
	
	$query='';
	my ($query)='';
	
	$prefix="Related_"if(&is_adm_order($in{'id_orders'}));
	$id_products=$prefix."ID_products";
	
	if ($in{'toprint'}){
		$style = 'stdtext';
	}else{
		$style = 'smalltext';
	}
		
	$query = " AND ID_products  =  $in{'id_products'} "  if ($in{'id_products'} and  length($in{'id_products'})	== 9 and substr($in{'id_products'},0,1)==4);
	
	my ($sth) = &Do_SQL("SELECT COUNT(*) FROM sl_orders_products WHERE ID_orders='$in{'id_orders'}' AND Status NOT IN('Order Cancelled', 'Inactive') $query");
	$va{'matches'} = $sth->fetchrow; 	
	if ($va{'matches'}>0){
		my $is_refill=0;
		my ($sth1) = &Do_SQL("SELECT * FROM sl_orders_products WHERE ID_orders='$in{'id_orders'}' AND Status NOT IN('Order Cancelled', 'Inactive') $query ORDER BY ID_orders_products");
		my ($col);	
		while ($col = $sth1->fetchrow_hashref){	
			my $refill_mark='';
			$d = 1 - $d;
			my ($sthk) = &Do_SQL("SELECT * FROM sl_skus WHERE ID_sku_products='$col->{$id_products}' and Status='Active'");
			$rec = $sthk->fetchrow_hashref;

			if ($col->{$id_products} < 5000){
				### Services in Order
				$output .= "   <td width=90px valign=top align=left><font class=detalles>$col->{'$id_products'}&nbsp;";
				$output .= "   ".&format_number($col->{'Quantity'})."</td>\n";
				#GV Modifica 21abr2008 Se cambia sl_services por sl_services #GV Modifica 21abr2008 Se cambia ID_services por ID_services
				$output .= "   <td width=350px valign=top align=left><font class=detalles>".&load_name('sl_services','ID_services',$col->{$id_products},'Name')."</td>\n";
			}elsif($col->{$id_products}>600000000){
				### Services in Order
				(&load_name('sl_services','ID_services',$col->{$id_products}-600000000,'ServiceType') eq 'Refill') and ($is_refill = 1) and ($refill_mark = ' <strong>**</strong> ');
				$output .= "   <td width=90px valign=top align=left><font class=detalles>".&format_sltvid($col->{$id_products})."&nbsp;";
				$output .= "   <td width=350px valign=top align=left><font class=detalles>".&load_name('sl_services','ID_services',$col->{$id_products}-600000000,'Name')." $refill_mark</td>\n";
				$output .= "   <td align=right>".&format_number($col->{'Quantity'})."</td>\n";
			}else{
				### Products in Order
				if ($list_type eq 'upc'){
					$output .= "   <td width=90px valign=top align=left><font class=detalles>".$rec->{'UPC'}."&nbsp;";
				}elsif($list_type eq 'custupc'){
					my ($sth_custid) = &Do_SQL("SELECT sku_customers FROM sl_customers_parts WHERE ID_parts='$col->{$id_products}' and ID_customers='$in{'id_customers'}'");
					my ($tmp_idprod) = $sth_custid->fetchrow();
					if ($tmp_idprod){
						$output .= "   <td width=90px valign=top align=left><font class=detalles>$tmp_idprod &nbsp;";
					}else{
						$output .= "   <td width=90px valign=top align=left><font class=detalles>".&format_sltvid($col->{$id_products})."&nbsp;";
					}
				}else{
					$output .= "   <td width=90px valign=top align=left><font class=detalles>".&format_sltvid($col->{$id_products})."&nbsp;";
				}
				
				#$output .= "   <!--div style='position:relative;right:27px;bottom:18px;'-->".&format_number($col->{'Quantity'})."</div></td>\n";
				($col->{'SerialNumber'}) and ($col->{'SerialNumber'} = "<br>$col->{'SerialNumber'}");
				($status,%tmp) = &load_product_info($col->{$id_products});

				if(&is_exportation_order($in{'id_orders'}) or $query ne '')	{
					$tmp{'model'}=&load_name('sl_parts','ID_parts',$col->{$id_products}-400000000,'Model');
					$tmp{'name'}=&load_name('sl_parts','ID_parts',$col->{$id_products}-400000000,'Name');
				}

				$tmp{'model'} = &replace_in_string($tmp{'model'});
				$tmp{'name'} = &replace_in_string($tmp{'name'});

				$output .= "   <td width=350px valign=top align=left><font class=detalles>$tmp{'model'}<br>$tmp{'name'} ".
								"<span class='smalltext'>".&load_parts($col->{$id_products})."</span></td>";
				if(&is_exportation_order($in{'id_orders'})){
					$output .= "  <td class='$style' align='right' nowrap>".$col->{'Quantity'}."</td>\n";
					$output .= ($col->{'Quantity'} != 0)?"  <td class='$style' align='right' nowrap>".&format_price($col->{'SalePrice'}/ $col->{'Quantity'})."</td>\n":"  <td class='$style' align='right' nowrap>".''."</td>\n";
					
					$output .= "  <td class='$style' align='right' nowrap>".&format_price($col->{'SalePrice'})."</td>\n"	if $col->{'SalePrice'} > 0;
					$output .= "  <td class='$style' align='right' nowrap>".&format_price($col->{'SalePrice'}*-1)."</td>\n"	if $col->{'SalePrice'} < 0;
					$tot_ord +=$col->{'SalePrice'} if $col->{'SalePrice'} >0;
					$tot_ord -= $col->{'SalePrice'} if $col->{'SalePrice'} <0;
				}else{
					$output .= "  <td class='$style' align='right' nowrap>".$col->{'Quantity'}."</td>\n";
					$output .= "  <td class='$style' align='right' nowrap>".&format_price($col->{'SalePrice'})."</td>\n";
					$output .= "  <td class='$style' align='right' nowrap>".&format_price($col->{'SalePrice'}*$col->{'Quantity'})."</td>\n"	if $col->{'SalePrice'} > 0;
					$output .= "  <td class='$style' align='right' nowrap>".&format_price($col->{'SalePrice'}*$col->{'Quantity'}*-1)."</td>\n"	if $col->{'SalePrice'} < 0;
					$tot_ord +=$col->{'SalePrice'} * $col->{'Quantity'} if $col->{'SalePrice'} >0; 
					$tot_ord -= $col->{'SalePrice'} * $col->{'Quantity'} if $col->{'SalePrice'} <0;
				}
			}
			$output .= "</tr>\n";
			$tot_qty += $col->{'Quantity'};
		}
		 
		################################################
		my ($sth2) = &Do_SQL("SELECT SUM(Tax) Tot_tax, Tax_percent FROM sl_orders_products WHERE ID_orders='$in{'id_orders'}' AND Status NOT IN('Order Cancelled', 'Inactive') $query GROUP BY Tax_percent ORDER BY ID_orders_products");
		my ($rec_tax);
		my $tax_lines;
		while ($rec_tax = $sth2->fetchrow_hashref) {
			$tax_lines .= qq|<tr>
						<td colspan='4' class='' align="right">Taxes= (|.($rec_tax->{'Tax_percent'}*100).qq| %)</td>
						<td align="right" class=''>|.&format_price($rec_tax->{'Tot_tax'}).qq|</td>
					</tr>|;
		}
		################################################
		 
		 
		### Orders Totals
		$taxes = &products_sum_in_order($in{'id_orders'}, "Tax");
		$va{'total_taxes'} = &format_price($taxes);
		$va{'total_order'} = &format_price(&total_orders_products($in{'id_orders'}));	
		$va{'ordernet'} = &format_price($in{'ordernet'});
		$va{'ordershp'} = &format_price(&products_sum_in_order($in{'id_orders'}, "Shipping"));
		$va{'orderdisc'} = &format_price(&products_sum_in_order($in{'id_orders'}, "Discount"));
		$va{'tax'} = $in{'ordertax'}*100;
		$va{'ordertax'} = &format_number($in{'ordertax'}*100);
		
		#$va{'total_order'} = &format_price($in{'ordernet'}+$in{'ordershp'}+$in{'ordernet'}*$in{'ordertax'});		
		#$va{'total_order'} = &format_price(int((($in{'ordernet'}*$tot_qty)  +$in{'ordershp'}-$va{'orderdisc'}+$in{'ordernet'}*$in{'ordertax'})*100+0.9)/100);				
		my $refill_txt='&nbsp;';
		if($is_refill){
			$refill_txt .= qq|
				    &nbsp;<tr>
					    <td colspan='5'>
						 <strong>|.&trans_txt('refill_disclaimer_title').qq|</strong><br>
						 |.&trans_txt('refill_disclaimer_desc').qq|
					    </td>
				    </tr>&nbsp;|;

		}
		##Points
		my $points_info='';
		$va{'points_info'}='';
		$va{'points_info'}=&get_points_info($in{'id_customers'},$in{'id_orders'});
		$points_info=qq|[ip_forms:reward_points]| if($va{'points_info'}ne'');
		
		## Coupons?
		my $add_coupon = '';
		if($cfg{'coupons'} and $in{'ordernet'} >= $cfg{'coupons_mindireksys'}){
			
			$result = &get_coupon_external('sl_orders',$in{'id_orders'});

			if($result > 0){
				$add_coupon = qq|[ip_forms:coupons_external_view]|;
			}
		}

		if(&is_exportation_order($in{'id_orders'})){
			$output .= qq|
				<tr>
					<td colspan='5' class='$style'><p>&nbsp;</p></td>
				</tr>		
				<tr>
					<td colspan='4' class='$style' align="right">|.&trans_txt('stotal').qq|</td>
					<td align="right" class='$style'>|.&format_price($tot_ord).qq|</td>
				</tr>
				<tr>
					<td colspan='4' class='$style' align="right">S&H=</td>
					<td align="right" class='$style'>$va{'ordershp'}</td>
				</tr>
				<tr>
					<td colspan='4' class='$style' align="right">Discounts=</td>
					<td align="right" class='$style'>$va{'orderdisc'}</td>
				</tr>			
				$tax_lines
				<tr>
					<td colspan='4' class='$style' align="right">|.&trans_txt('total').qq|</td>
					<td align="right" class='$style'>$va{'total_order'}</td>
				</tr>
				$refill_txt
				<tr>
					<td colspan='5' align="left" class="smalltext">[fc_load_invoice_data]</td>
				</tr>
				<tr>
					<td colspan='5' align="center" class="smalltext"><p>&nbsp;</p>&nbsp;</td>
				</tr>
				<tr>
					<td colspan='5' align="left" class="smalltext"><p></p>&nbsp;</td>
				</tr>
				<tr>
					<td colspan='5' align="center" class="smalltext"><p>&nbsp;</p>&nbsp;</td>
				</tr>|;
		}else{
			#$va{'total_order'} = &format_price(&total_orders_products($in{'id_orders'})*$tot_qty);	
			$output .= qq|
				<tr>
					<td colspan='5' class='$style'><p>&nbsp;</p></td>
				</tr>		
				<tr>
					<td colspan='4' class='$style' align="right">|.&trans_txt('stotal').qq|</td>
					<td align="right" class='$style'>|.&format_price($tot_ord).qq|</td>
				</tr>
				<tr>
					<td colspan='4' class='$style' align="right">|.&trans_txt('shipping').qq|</td>
					<td align="right" class='$style'>$va{'ordershp'}</td>
				</tr>
				<tr>
					<td colspan='4' class='$style' align="right">|.&trans_txt('discounts').qq|</td>
					<td align="right" class='$style'>$va{'orderdisc'}</td>
				</tr>			
				<tr>
					<td colspan='4' class='$style' align="right">|.&trans_txt('taxes').qq| ($va{'tax'} %)</td>
					<td align="right" class='$style'>$va{'total_taxes'}</td>
				</tr>
				<tr>
					<td colspan='4' class='$style' align="right">|.&trans_txt('total').qq|</td>
					<td align="right" class='$style'>$va{'total_order'}</td>
				</tr>
				$refill_txt
				<tr>
					<td colspan='5' align="left" class="smalltext">[fc_load_invoice_data]</td>
				</tr>
				<tr>
					<td colspan='5' align="left" class="smalltext"><p>&nbsp;</p>&nbsp;</td>
				</tr>
				<tr>
					<td colspan='5' align="left" ><p>$points_info</p>&nbsp;</td>
				</tr>
				<tr>
					<td colspan='5' align="left" class="smalltext"><p>$add_coupon</p>&nbsp;</td>
				</tr>
				<tr>
					<td colspan='5' align="center" class="smalltext"><p>&nbsp;</p>&nbsp;</td>
				</tr>|;
		}		
			 
		 
	}else{
		$output = qq|
			<tr>
				<td colspan='5' align="center">|.&trans_txt('search_nomatches').qq|</td>
			</tr>\n|;
	}	
	return $output;	
}

sub load_parts {	
# --------------------------------------------------------
# Last Time Modified by RB on 01/12/2012: Se quita contenido dentro de [] en los nombres

	my ($id_products)= @_;
	my ($output);
	# 10-09-2013::AD: Se elimina filtro and Status='Active'
	my ($sthk) = &Do_SQL("SELECT * FROM sl_skus WHERE ID_sku_products='$id_products' ");
	$rec = $sthk->fetchrow_hashref;
	if ($rec->{'IsSet'} eq 'Y'){
  		### SETS / Kits
		my ($sth2) = &Do_SQL("SELECT * FROM sl_skus_parts WHERE ID_sku_products='$id_products';");
		while ($tmp = $sth2->fetchrow_hashref){
			my ($this_partname) = &load_db_names('sl_parts','ID_parts',$tmp->{'ID_parts'},'[Model]<br>[Name]');
			$this_partname = &replace_in_string($this_partname);
			$output .= qq|<br><img src="/sitimages/tri.gif" border="0"> $tmp->{'Qty'} x |.
					&format_sltvid(400000000+$tmp->{'ID_parts'})." ".
					$this_partname;
		}
		return $output;
	}else{
		return &load_choices('-',$rec->{'choice1'},$rec->{'choice2'},$rec->{'choice3'},$rec->{'choice4'});
	}
}

sub load_parts_upc {	
# --------------------------------------------------------
# Last Time Modified by AD on 25/09/2013: Se muestra UPC

	my ($id_products)= @_;
	my ($output);

	my ($sthk) = &Do_SQL("SELECT * FROM sl_skus WHERE ID_sku_products='$id_products' ");
	$rec = $sthk->fetchrow_hashref;
	if ($rec->{'IsSet'} eq 'Y'){
  		### SETS / Kits
		my ($sth2) = &Do_SQL("SELECT * 
			FROM sl_skus INNER JOIN sl_skus_parts ON sl_skus.ID_sku_products=(400000000+sl_skus_parts.ID_parts) 
			WHERE sl_skus_parts.ID_sku_products='$id_products';");
		while ($tmp = $sth2->fetchrow_hashref){
			my ($this_partname) = &load_db_names('sl_parts','ID_parts',$tmp->{'ID_parts'},'[Model]<br>[Name]');

			$this_partname = &replace_in_string($this_partname);
			$output .= qq|<br><img src="/sitimages/tri.gif" border="0"> $tmp->{'Qty'} x |.
					$tmp->{'UPC'}." ".$this_partname;
		}
		return $output;
	}else{
		return &load_choices('-',$rec->{'choice1'},$rec->{'choice2'},$rec->{'choice3'},$rec->{'choice4'});
	}
}

sub load_customer_name {	
# --------------------------------------------------------
# Created on: 07/10/08 @ 12:54:00
# Author: Carlos Haas
# Last Modified on: 07/10/08 @ 12:54:00
# Last Modified by: Carlos Haas
# Description : 
# Parameters :
#Last modified on 7 Feb 2011 18:56:59
#Last modified by: MCC C. Gabriel Varela S. :Se hace que seleccione el company_name si existe 
#Last modified on 8 Feb 2011 11:28:21
#Last modified by: MCC C. Gabriel Varela S. :Se hace que si la orden es wholesale, el nombre siempre sea company_name
#			   
  		
  my $is_whole=&is_adm_order($in{'id_orders'});
	my ($sth) = &Do_SQL("SELECT 
	if('$is_whole',company_name,CONCAT(FirstName,' ',LastName1)),
	Phone1, Phone2, Cellphone	  
	FROM sl_customers WHERE ID_customers='$in{'id_customers'}';");
	my ($cust, $p1, $p2, $p3) = $sth->fetchrow;
	my $output = $cust;

	$va{'shp_phone'} = $p1;
	($p2) and ($va{'shp_phone'} .= qq| / $p2|);
	($p3) and ($va{'shp_phone'} .= qq| / $p3|);
			
	return $output;
}

sub load_pl_products {
# --------------------------------------------------------	
# Created on: 07/10/08 @ 12:53:55
# Author: Carlos Haas
# Last Modified on: 07/10/08 @ 12:53:55
# Last Modified by: Carlos Haas
# Description : 
# Parameters : 
#			   
#			   
	my ($style,$output,$tot_qty,$tot_ord,$choices);
	my ($style);
	if ($in{'toprint'}){
		$style = 'stdtext';
	}else{
		$style = 'smalltext';
	}

	my ($sth) = &Do_SQL("SELECT COUNT(*) FROM sl_orders_products WHERE ID_orders='$in{'id_orders'}' AND ID_orders_products='$in{'id_orders_products'}' AND Status!='Inactive'");
	$va{'matches'} = $sth->fetchrow;
	if ($va{'matches'}>0){
		my ($sth1) = &Do_SQL("SELECT * FROM sl_orders_products WHERE ID_orders='$in{'id_orders'}' AND ID_orders_products='$in{'id_orders_products'}' AND Status!='Inactive' ORDER BY ID_products DESC;");
		my ($col);
		while ($col = $sth1->fetchrow_hashref){
			$d = 1 - $d;
			my ($sthk) = &Do_SQL("SELECT * FROM sl_skus WHERE ID_sku_products='$col->{'ID_products'}' and Status='Active'");
			$rec = $sthk->fetchrow_hashref;
			
			if ($col->{'ID_products'} < 5000){
				### Services in Order
				$output .= "<tr bgcolor='$c[$d]'>\n";
				$output .= "   <td class='$style' valign='top' align='right' nowrap>$col->{'ID_products'}&nbsp;</td>\n";
				#GV Modifica 21abr2008 Se cambia sl_services por sl_services #GV Modifica 21abr2008 Se cambia ID_services por ID_services
				$output .= "   <td class='$style'>".&load_name('sl_services','ID_services',$col->{'ID_products'},'Name')."</td>\n";
				$output .= "   <td class='$style' align='right'>".&format_number($col->{'Quantity'})."</td>\n";
				$output .= "   <td class='$style' align='right' nowrap>".&format_price($col->{'SalePrice'})."</td>\n";
				$output .= "   <td class='$style' align='right' nowrap>".&format_price($col->{'SalePrice'}*$col->{'Quantity'})."</td>\n";
				$output .= "</tr>\n";
				$tot_qty += $col->{'Quantity'};
				$tot_ord +=$col->{'SalePrice'}*$col->{'Quantity'};
			}else{
				### Products in Order
				$output .= "<tr bgcolor='$c[$d]'>\n";
				$output .= "   <td class='$style' valign='top' align='right' nowrap>".&format_sltvid($col->{'ID_products'})."&nbsp;</td>\n";
				($col->{'SerialNumber'}) and ($col->{'SerialNumber'} = "<br>$col->{'SerialNumber'}");
				($status,%tmp) = &load_product_info($col->{'ID_products'});
				$output .= "  <td class='$style'>$tmp{'model'}<br>$tmp{'name'} ".&load_choices('-',$rec->{'choice1'},$rec->{'choice2'},$rec->{'choice3'},$rec->{'choice4'})." $col->{'SerialNumber'} ".&build_tracking_link($col->{'Tracking'},$col->{'ShpProvider'},$col->{'ShpDate'},$col->{'ID_products'})."</td>\n";
				$tot_qty += $col->{'Quantity'};
				$tot_ord +=$col->{'SalePrice'}*$col->{'Quantity'};
				$output .= "  <td class='$style' align='right'>".&format_number($col->{'Quantity'})."</td>\n";
				$output .= "   <td class='$style' align='right' nowrap>".&format_price($col->{'SalePrice'})."</td>\n";
				$output .= "   <td class='$style' align='right' nowrap>".&format_price($col->{'SalePrice'}*$col->{'Quantity'})."</td>\n";
				$output .= "</tr>\n";
			}
		}		
	}else{
		$output = qq|
			<tr>
				<td colspan='5' align="center">|.&trans_txt('search_nomatches').qq|</td>
			</tr>\n|;
	}	
	
	return $output;
}


sub load_batch_products {
# --------------------------------------------------------

# Author: Unknown
# Created on: Unknown
# Last Modified on: 08/27/2008
# Last Modified by: Jose Ramirez Garcia
# Description : 
# Forms Involved: 
# Parameters : 
# Notes : the orderdisc was added to ordertax

	my ($style,$output,$tot_qty,$tot_ord);
	if ($in{'toprint'}){
		$style = 'stdtext';
	}else{
		$style = 'smalltext';
	}

	my ($sth) = &Do_SQL("SELECT COUNT(*) FROM sl_orders_products WHERE ID_orders='$in{'id_orders'}' AND Status='Active'");
	$va{'matches'} = $sth->fetchrow;
	if ($va{'matches'}>0){
		my ($sth1) = &Do_SQL("SELECT * FROM sl_orders_products WHERE ID_orders='$in{'id_orders'}' AND Status='Active' ORDER BY ID_products DESC;");
		my ($col);
		while ($col = $sth1->fetchrow_hashref){
			$d = 1 - $d;
			my ($sthk) = &Do_SQL("SELECT * FROM sl_skus WHERE ID_sku_products='$col->{'ID_products'}' and Status='Active'");
			$rec = $sthk->fetchrow_hashref;
			if ($col->{'ID_products'} < 5000){
				### Services in Order
				$output .= "<tr bgcolor='$c[$d]'>\n";
				$output .= "   <td class='$style' valign='top' align='right' nowrap>$col->{'ID_products'}&nbsp;</td>\n";
				#GV Modifica 21abr2008 Se cambia sl_services por sl_services #GV Modifica 21abr2008 Se cambia ID_services por ID_services
				$output .= "   <td class='$style'>".&load_name('sl_services','ID_services',$col->{'ID_products'},'Name')."<br>".&load_choices('-',$rec->{'choice1'},$rec->{'choice2'},$rec->{'choice3'},$rec->{'choice4'})."</td>\n";
				$output .= "   <td class='$style' align='right'>".&format_number($col->{'Quantity'})."</td>\n";
				$output .= "   <td class='$style' align='right' nowrap>".&format_price($col->{'SalePrice'})."</td>\n";
				$output .= "   <td class='$style' align='right' nowrap>".&format_price($col->{'SalePrice'}*$col->{'Quantity'})."</td>\n";
				$output .= "</tr>\n";
				$tot_qty += $col->{'Quantity'};
				$tot_ord +=$col->{'SalePrice'}*$col->{'Quantity'};
			}else{
				### Products in Order
				$output .= "<tr bgcolor='$c[$d]'>\n";
				$output .= "   <td class='$style' valign='top' align='right' nowrap>".&format_sltvid($col->{'ID_products'})."&nbsp;</td>\n";
				(!$col->{'SerialNumber'}) and ($col->{'SerialNumber'} = '---');
				($status,%tmp) = &load_product_info($col->{'ID_products'});
				$output .= "  <td class='$style'>$tmp{'model'}<br>$tmp{'name'}<br>$choices<br>$col->{'SerialNumber'}</td>\n";
				$tot_qty += $col->{'Quantity'};
				$tot_ord +=$col->{'SalePrice'}*$col->{'Quantity'};
				$output .= "  <td class='$style' align='right'>".&format_number($col->{'Quantity'})."</td>\n";
				$output .= "  <td class='$style' align='right' nowrap>".&format_price($col->{'SalePrice'})."</td>\n";
				$output .= "  <td class='$style' align='right' nowrap>".&format_price($col->{'SalePrice'}*$col->{'Quantity'})."</td>\n";
				$output .= "  <td class='$style' align='right' nowrap>".&format_price($tmp{'sltv_netcost'}*$col->{'Quantity'})."</td>\n";
				$output .= "</tr>\n";
			}
		}
		### Orders Totals
		$va{'total_taxes'} = &format_price((&taxables_in_order($in{'id_orders'})-$in{'orderdisc'})*$in{'ordertax'});
		$va{'total_order'} = &format_price($in{'ordernet'}+$in{'ordershp'}+$in{'ordernet'}*$in{'ordertax'});
		$va{'total_order'} = &format_price(int(($in{'ordernet'}+$in{'ordershp'}-$va{'orderdisc'}+$in{'ordernet'}*$in{'ordertax'})*100+0.9)/100);
		$va{'ordernet'} = &format_price($in{'ordernet'});
		$va{'ordershp'} = &format_price($in{'ordershp'});
		$va{'orderdisc'} = &format_price($in{'orderdisc'});
		$va{'tax'} = $in{'ordertax'}*100;
		$va{'ordertax'} = &format_number($in{'ordertax'}*100);
		
		$output .= qq|
			<tr>
				<td colspan='5' class='$style'><p>&nbsp;</p></td>
			</tr>		
			<tr>
				<td colspan='5' class='$style' align="right">|.&trans_txt('stotal').qq|</td>
				<td align="right" class='$style'>|.&format_price($tot_ord).qq|</td>
			</tr>
			<tr>
				<td colspan='5' class='$style' align="right">|.&trans_txt('shipping').qq|</td>
				<td align="right" class='$style'>$va{'ordershp'}</td>
			</tr>
			<tr>
				<td colspan='5' class='$style' align="right">|.&trans_txt('discounts').qq|</td>
				<td align="right" class='$style'>$va{'orderdisc'}</td>
			</tr>			
			<tr>
				<td colspan='5' class='$style' align="right">|.&trans_txt('taxes').qq| ($va{'tax'} %)</td>
				<td align="right" class='$style'>$va{'total_taxes'}</td>
			</tr>
			<tr>
				<td colspan='5' class='$style' align="right">|.&trans_txt('total').qq|</td>
				<td align="right" class='$style'>$va{'total_order'}</td>
			</tr>\n|;
		my ($sth1) = &Do_SQL("SELECT COUNT(*) FROM sl_orders_payments WHERE ID_orders='$in{'id_orders'}' AND Status<>'Cancelled'");
		if ($sth1->fetchrow >1){
			$output .= qq|
			<tr>
				<td colspan='6' align="center">|.&trans_txt('flexipago').qq|</td>
			</tr>\n|;			
			my ($sth1) = &Do_SQL("SELECT * FROM sl_orders_payments WHERE ID_orders='$in{'id_orders'}' AND Status<>'Cancelled' ORDER BY Paymentdate ASC");
			while ($col = $sth1->fetchrow_hashref){
				$output .= qq|
			<tr>
				<td colspan='6' align="center" class="smalltext">|. &format_price($col->{'Amount'}).qq| \@ $col->{'Paymentdate'}</td>
			</tr>\n|;
			}
		}
	}else{
		$output = qq|
			<tr>
				<td colspan='5' align="center">|.&trans_txt('search_nomatches').qq|</td>
			</tr>\n|;
	}	
	
	return $output;
}

sub load_batch_payments {
# --------------------------------------------------------	
	## Items List
	my ($tot_pay,$output);
	my (@c) = split(/,/,$cfg{'srcolors'});
	my ($sth) = &Do_SQL("SELECT COUNT(*) FROM sl_orders_payments WHERE ID_orders='$in{'id_orders'}'");
	$va{'matches'} = $sth->fetchrow;
	if($va{'matches'}>0){
		my ($sth) = &Do_SQL("SELECT * FROM sl_orders_payments WHERE ID_orders='$in{'id_orders'}' AND Status IN('Approved','Pending') ORDER BY ID_orders_payments  DESC;");
		while ($rec = $sth->fetchrow_hashref){
			$d = 1 - $d;
			$tot_pay += $rec->{'Amount'};
			if ($rec->{'Type'} eq "Check"){
				$output .= "<tr>\n";
				$output .= "   <td class='menu_bar_title'>Name on Check</td>\n";
				$output .= "   <td class='menu_bar_title'>Routing ABA/ Account/ Chk</td>\n";
				$output .= "   <td class='menu_bar_title'>P/C</td>\n";
				$output .= "   <td class='menu_bar_title'>D.O.B<br>License/State<br>Phone</td>\n";
				$output .= "	<td class='menu_bar_title'>Status<br>Cod Auth</td>\n";							
				$output .= "	<td class='menu_bar_title'>Amount</td>\n";
				$output .= "</tr>\n";
				$output .= "<tr>\n";
				$output .= "   <td class='smalltext' valign='top' $decor> $rec->{'PmtField1'}</td>\n";
				$output .= "   <td class='smalltext' valign='top' $decor> $rec->{'PmtField2'}<br>$rec->{'PmtField3'}<br>$rec->{'PmtField4'}</td>\n";
				$output .= "   <td class='smalltext' valign='top' $decor> $rec->{'PmtField8'}</td>\n";
				$output .= "   <td class='smalltext' valign='top' $decor> $rec->{'PmtField5'}<br> $rec->{'PmtField6'}<br>$rec->{'PmtField7'}<br>$rec->{'PmtField9'}</td>\n";
				$output .= "   <td class='smalltext' valign='top' $decor> $rec->{'Status'}<br>$rec->{'AuthCode'} \@ $rec->{'AuthDateTime'}</td>\n";							
				$output .= "   <td class='smalltext' valign='top' $decor align='right'> ".&format_price($rec->{'Amount'})."</td>\n";
				$output .= "</tr>\n";					
			}elsif($rec->{'Type'} eq "WesternUnion"){
				$output .= "<tr>\n";
				$output .= "   <td class='menu_bar_title' colspan='4'>WesterUnion Payment</td>\n";
				$output .= "	<td class='menu_bar_title'>Status<br>Cod Auth</td>\n";							
				$output .= "	<td class='menu_bar_title'>Amount</td>\n";
				$output .= "</tr>\n";
				$output .= "<tr>\n";
				$output .= "   <td class='smalltext' valign='top' $decor colspan='4'> No Information Required For WU Payments</td>\n";
				$output .= "   <td class='smalltext' valign='top' $decor> $rec->{'Status'}<br>$rec->{'AuthCode'}</td>\n";							
				$output .= "   <td class='smalltext' valign='top' $decor align='right'> ".&format_price($rec->{'Amount'})."</td>\n";
				$output .= "</tr>\n";	
			}else{
				$output .= "<tr>\n";
				$output .= "   <td class='menu_bar_title'>Type</td>\n";
				$output .= "   <td class='menu_bar_title'>Name on Card<br>Card Number</td>\n";
				$output .= "   <td class='menu_bar_title'>Exp</td>\n";
				$output .= "   <td class='menu_bar_title'>CVN</td>\n";
				$output .= "	<td class='menu_bar_title'>Status<br>Cod Auth</td>\n";			
				$output .= "	<td class='menu_bar_title'>Amount</td>\n";
				$output .= " </tr>\n";
				$output .= " <tr>\n";
				$output .= "   <td class='smalltext' $decor valign='top'> $rec->{'PmtField1'}</td>\n";
				#$output .= "   <td class='smalltext' $decor valign='top'> $rec->{'PmtField2'}<br>$rec->{'PmtField3'}</td>\n";
				$output .= "   <td class='smalltext' $decor valign='top'> $rec->{'PmtField2'}<br>";
				
				### modified by rafael on 2007-10-09 @6:07PM - Hide credit card to some users
				$output .= "xxxx-xxxx-xxxx-".substr($cc,$#cc-4,4)."</td>\n";

				###############################################################################
				$output .= "   <td class='smalltext' $decor valign='top'> $rec->{'PmtField4'}</td>\n";
				$output .= "   <td class='smalltext' $decor valign='top'> $rec->{'PmtField5'}</td>\n";
				$output .= "   <td class='smalltext' $decor valign='top'> $rec->{'Status'}<br>$rec->{'AuthCode'} \@ $rec->{'AuthDateTime'}</td>\n";
				$output .= "   <td class='smalltext' $decor align='right' valign='top'> ".&format_price($rec->{'Amount'})."<br>$rec->{'Paymentdate'}</td>\n";
				$output .= "</tr>\n";
			}
		}
		$output .= qq|
			<tr>
				<td colspan='5' class='smalltext' align="right">|.&trans_txt('mer_vpo_total').qq|</td>
				<td align="right" class='smalltext'>|.&format_price($tot_pay).qq|</td>
			</tr>\n|;
	}else{
		$va{'pageslist'} = 1;
		$va{'searchresults'} = qq|
			<tr>
				<td colspan='8' align="center">|.&trans_txt('search_nomatches').qq|</td>
			</tr>\n|;
	}
	return $output;
}


sub load_set_ids {
# --------------------------------------------------------
	my ($id) = @_;
	my (@ary);
	my ($sth) = &Do_SQL("SELECT COUNT(*) FROM sl_setproducts WHERE ID_setproducts='$id';");
	if ($sth->fetchrow()>0){
		## Load Items in SET
		&load_cfg('sl_setproducts');
		my ($sth) = &Do_SQL("SELECT ID_products FROM sl_setproducts_items WHERE ID_setproducts='$id';");
		while ($rec = $sth->fetchrow()){
			push(@ary,$rec);
		}
	}
	return @ary;
}

sub load_skuchoices {
# --------------------------------------------------------
	my ($output);
	#################################
	##### build Vendor SKUs
	#################################
	my ($id_product) = $in{'id_products'};
	if (length($in{'id_products'})>6){
		$id_product = substr($in{'id_products'},3,6);
	}else{
		$id_product = $in{'id_products'};
	}
	my (@c) = split(/,/,$cfg{'srcolors'});
	my ($sth) = &Do_SQL("SELECT * FROM sl_skus WHERE ID_products='$id_product' ORDER BY ID_sku_products;");
	while ($rec = $sth->fetchrow_hashref){
		$d = 1 - $d;
		(!$rec->{'choice2'}) and ($rec->{'choice2'}='---');
		(!$rec->{'choice3'}) and ($rec->{'choice3'}='---');
		(!$rec->{'choice4'}) and ($rec->{'choice4'}='---');
		$output .= qq|
		<tr bgcolor='$c[$d]'>
			<td align="center" class="smalltext" $style>|.format_sltvid($rec->{'ID_sku_products'}).qq|</a></td>
			<td align="center" class="smalltext" $style>$rec->{'choice1'}</td>
			<td align="center" class="smalltext" $style>$rec->{'choice2'}</td>
			<td align="center" class="smalltext" $style>$rec->{'choice3'}</td>
			<td align="center" class="smalltext" $style>$rec->{'choice4'}</td>
			<td align="center" class="smalltext" $style>$rec->{'VendorSKU'}</td>
			<td align="center" class="smalltext" $style>$rec->{'UPC'}</td>
			<td align="center" class="smalltext" $style>$rec->{'Status'}</td>
		</tr>\n|;
	}
	
	return $output;
}

sub load_inventory_list {
# --------------------------------------------------------
# Last Modified RB: 03/02/09  10:03:26 -- Se agrupo el producto por warehouse y se totalizo
# Last Modified RB: 05/15/09  17:41:49 -- Se incorpora la suma de partes 


	my ($output,$choices,$total);
	my (@c) = split(/,/,$cfg{'srcolors'});
	
	my ($sth) = &Do_SQL("SELECT IsSet FROM sl_skus WHERE RIGHT(ID_sku_products,6)='$in{'id_products'}'");
	if ($sth->fetchrow eq 'Y'){
		my ($sth) = &Do_SQL("SELECT sl_skus_parts.ID_parts FROM sl_skus_parts,sl_parts_vendors WHERE sl_skus_parts.ID_parts=sl_parts_vendors.ID_parts AND RIGHT(ID_sku_products,6)='$in{'id_products'}';");
		while ($id = $sth->fetchrow){
			$id += 400000000;
			my ($sth) = &Do_SQL("SELECT *,SUM(Quantity)AS QtyGroup FROM sl_warehouses_location,sl_warehouses WHERE sl_warehouses_location.ID_warehouses=sl_warehouses.ID_warehouses AND ID_products='$id' AND Quantity>0 GROUP BY sl_warehouses.ID_warehouses,ID_products ORDER BY sl_warehouses_location.ID_warehouses,ID_products;");
			if($sth->rows() > 0){
				while ($rec = $sth->fetchrow_hashref){
					$d = 1 - $d;
					$output .= "<tr bgcolor='$c[$d]'>\n";
					$output .= "   <td class='smalltext'>$rec->{'ID_warehouses'} $rec->{'Name'},$rec->{'City'} </td>\n";
					$output .= "   <td class='smalltext' valign='top'>".&format_sltvid($rec->{'ID_products'})."</td>\n";
					$output .= "   <td class='smalltext' valign='top'>&nbsp;</td>\n";
					$output .= "   <td class='smalltext' align='right' valign='top'>$rec->{'QtyGroup'}</td>\n";
					$output .= "</tr>\n";
					$total +=$rec->{'QtyGroup'}; 
				}
			}else{
				$output .= "<tr bgcolor='$c[$d]'>\n";
					$output .= "   <td class='smalltext'>$rec->{'ID_warehouses'} N/A} </td>\n";
					$output .= "   <td class='smalltext' valign='top'>".&format_sltvid($rec->{'ID_products'})."</td>\n";
					$output .= "   <td class='smalltext' valign='top'>&nbsp;</td>\n";
					$output .= "   <td class='smalltext' align='right' valign='top'>0</td>\n";
					$output .= "</tr>\n";
			}					
		}
	}else{
		my ($sth) = &Do_SQL("SELECT *,SUM(Quantity)AS QtyGroup FROM sl_warehouses_location,sl_warehouses WHERE sl_warehouses_location.ID_warehouses=sl_warehouses.ID_warehouses AND RIGHT(ID_products,6)='$in{'id_products'}' AND Quantity>0 GROUP BY sl_warehouses.ID_warehouses,ID_products ORDER BY sl_warehouses_location.ID_warehouses,ID_products;");
		while ($rec = $sth->fetchrow_hashref){
			$d = 1 - $d;
			$output .= "<tr bgcolor='$c[$d]'>\n";
			$output .= "   <td class='smalltext'>$rec->{'ID_warehouses'} $rec->{'Name'},$rec->{'City'} </td>\n";
			$output .= "   <td class='smalltext' valign='top'>".&format_sltvid($rec->{'ID_products'})."</td>\n";
			$output .= "   <td class='smalltext' valign='top'>".&load_choices($rec->{'ID_products'})."</td>\n";
			$output .= "   <td class='smalltext' align='right' valign='top'>$rec->{'QtyGroup'}</td>\n";
			$output .= "</tr>\n";
			$total +=$rec->{'QtyGroup'}; 
		}
	}
	$output .= "<tr bgcolor='$c[$d]'>\n<td class='smalltext' colspan='3'>&nbsp;</td><td class='smalltext' align='right'>Total: $total</td></tr>"	if	$output;



	(!$output) and ($output = "<tr>\n<td colspan='4' align='center'>".&trans_txt('nostock')."</td></tr>");
	return $output;
}

sub load_vinventory_list {
# --------------------------------------------------------
	my ($output,$choices);
	my (@c) = split(/,/,$cfg{'srcolors'});
	my ($sth) = &Do_SQL("SELECT * FROM sl_vpurchaseorder_items,sl_vpurchaseorders WHERE sl_vpurchaseorder_items.ID_vpurchaseorders=sl_vpurchaseorders.ID_vpurchaseorders AND RIGHT(ID_products,6)='$in{'id_products'}' AND Status='In Process' AND OhStartDate<=Curdate() AND OhEndDate>=Curdate() ORDER BY sl_vpurchaseorder_items.ID_vpurchaseorder_items;");
	while ($rec = $sth->fetchrow_hashref){
		$d = 1 - $d;
		$output .= "<tr bgcolor='$c[$d]'>\n";
		$output .= "   <td class='smalltext'>($rec->{'ID_vendors'}) ".&load_name('sl_vendors','ID_vendors',$rec->{'ID_vendors'},'CompanyName')."</td>\n";
		$output .= "   <td class='smalltext' valign='top'>".&format_sltvid($rec->{'ID_products'})."</td>\n";
		$output .= "   <td class='smalltext' valign='top'>".&load_choices($rec->{'ID_products'})."</td>\n";
		$output .= "   <td class='smalltext' align='right' valign='top'>$rec->{'Qty'}</td>\n";
		$output .= "</tr>\n";
	}

	(!$output) and ($output = "<tr>\n<td colspan='4' align='center'>".&trans_txt('nostock')."</td></tr>");
	return $output;
}

sub load_choices {
# --------------------------------------------------------
# Forms Involved: 
# Created on: 9/12/2007 11:29AM
# Last Modified on:
# Last Modified by:
# Author: Carlos Haas
# Description : 
	my ($id,@choices) = @_;
	my ($output);
	if ($choices[0] or $choices[1] or $choices[2] or $choices[3]){
		$output = join(',',@choices);
	}else{
		## Evitamos el query si no es necesario
		if (int($id)>0){
			$output = &load_db_names('sl_skus','ID_sku_products',$id,'[choice1],[choice2],[choice3],[choice4]');
		}
	}
	$output =~ s/,,|,$//g;
	($output) and ($output = "<br><span class='help_on'>".&trans_txt('choices').": $output</span>");
	
	return $output;
}


sub load_topparent_id {
# --------------------------------------------------------
	my ($idcat) = @_;
	my ($ncat) = &load_name('sl_categories','ID_categories',$idcat,'ID_parent');
	while ($ncat > 0){
		$idcat = $ncat;
		$ncat = &load_name('sl_categories','ID_categories',$idcat,'ID_parent');
	}
	return $idcat;	
}


###############################################################################
#   Function: valid_refcost
#
#       Es: valida si el Costo de un SKUm es valido
#
#   Created by:
#       ISC Gilberto Quirino
#
#   Modified By:
#   	
#
#   Parameters:
#
#       id_sku, cost
#
#   Returns:
#   	string: Yes, No
#   	
#
#
sub valid_refcost {
###############################################################################

	my($id_sku, $cost) = @_;

	### Se obtienen el costo de referencia y el porcentaje para el margen de variación del costo
	my ($sth) = &Do_SQL("SELECT RefCost, RefcostPct FROM sl_skus WHERE sl_skus.ID_sku_products = '".int($id_sku)."';");
	my ($refcost,$refcost_pct) = $sth->fetchrow(); 

	if( $refcost > 0 and $refcost_pct > 0 ){
		my $variation = round($refcost * $refcost_pct / 100, 2);

		my $cost_min = $refcost - $variation;
		my $cost_max = $refcost + $variation;

		my $rslt = ( $cost >= $cost_min and $cost <= $cost_max ) ? 'Yes' : 'No';
		#&cgierr($rslt.":: Cost=".$cost." :: refcost=".$refcost." :: variation=".$variation." :: cost_min=".$cost_min." :: cost_max=".$cost_max);
		return $rslt;

	}else{
		return 'Yes';
	}

}


###############################################################################
#   Function: load_sltvcost
#
#       Es: Busca el costo de un producto (sku) especifico
#
#   Created by:
#       _RB_
#
#   Modified By:
#   	
#   		Last Modified on 07/09/09 12:04:48 by: MCC C. Gabriel Varela S: Se hace que regrese 0, porque puede ser que exista una parte que no tenga registros de costo y al final regresa null.	
#			Last Modified on 10/08/15 by: ISC Gilberto Quirino: Se agrega validación para el costo del SKU en base al costo de referencia
#
#   Parameters:
#
#       ID_products
#
#   Returns:
#   
#   	Cost
#
#
sub load_sltvcost {
###############################################################################

	my ($idproduct) = @_;
	#my ($interval1) = 0; my ($interval2) = 0;
	my @ary_types = ('Purchase','Sale','Production','Transfer In','Transfer Out','Adjustment');
			
	if ($cfg{'acc_inventoryout_method_cost'} and lc($cfg{'acc_inventoryout_method_cost'}) eq 'average'){

		my ($cost,$to_dump, $id_customs_info, $cost_adj, $cost_add) = &get_average_cost($idproduct);
		return ($cost, $cost_adj, $id_customs_info, $cost_add);

	}else{
		#####Busqueda del producto en sl_skus_trans | Basado en arreglo de tipos de transaccion
		for(0..$#ary_types){

			my $this_type = $ary_types[$_];
		
			my ($sth) = &Do_SQL("SELECT Cost, Cost_Adj, ID_customs_info, Cost_Add 
								  FROM sl_skus_trans 
								  WHERE Type = '". $this_type ."' AND ID_products = '$idproduct' AND Cost > 0 
								  ORDER BY Date DESC;");
			while ( $rec = $sth->fetchrow_hashref() ){
				
				if( &valid_refcost($idproduct, $rec->{'Cost'}) eq 'Yes' ){

					return ($rec->{'Cost'}, $rec->{'Cost_Adj'}, $rec->{'ID_customs_info'}, $rec->{'Cost_Add'});

				}
				
			} 

		}
	}

	return (0,0,0,0);
}


sub load_sltvcost_dates {
# --------------------------------------------------------
#-----------------------------------------
# Forms Involved: 
# Created on: 10/31/08  15:54:01
# Last Modified on: 10/31/08  15:54:01
# Last Modified by: Roberto Barcenas
# Last Modified Desc:
# Author: Roberto Barcenas
# Description : Return the AVG Cost of a product based on dates
# Parameters : 

	my ($idproduct,$fromdate,$todate) = @_;
	my ($prod_cost) = 0;
	my ($query) = '';
	
	if($fromdate ne '' and $todate ne ''){
			$query = " AND Date BETWEEN '$fromdate' AND '$todate' ";
	}elsif($fromdate ne ''){
			$query = " AND Date >= '$fromdate' ";
	}elsif($todate ne ''){
			$query = " AND Date <= '$todate' ";
	}
	
	#####Searching from sl_purchaseorders_items
	my ($sth2) = &Do_SQL("SELECT AVG(Price) FROM sl_purchaseorders_items WHERE ID_products = '$idproduct' AND Received > 0 $query");
	$prod_cost=$sth2->fetchrow;
	if (!$prod_cost or $prod_cost eq '' or $prod_cost <= 0){
		#####Searching from sl_skus_cost
		my ($sth3) = &Do_SQL("SELECT AVG(Cost) FROM sl_skus_cost WHERE ID_products = '$idproduct' $query");
		$prod_cost=$sth3->fetchrow;
		if ($idproduct =~ /^1/ and (!$prod_cost or $prod_cost eq '' or $prod_cost <= 0)){ 
			#####Searching from sl_products.SLTV_NetCost
			$prod_cost = &load_name('sl_products','ID_products',substr($idproduct,3,6),'SLTV_NetCost');
		}
	} 
	return $prod_cost;
}

sub load_prod_info {
# --------------------------------------------------------
# Last Modified on: 03/17/09 16:18:16
# Last Modified by: MCC C. Gabriel Varela S: Se incluyen los nuevos parámetros de sltv_itemshipping
# Last Modified RB: 12/07/2010  19:06:44 -- Se agregan parametros para calculo de shipping
	my ($id) = @_;
	&load_cfg('sl_products');
	my (%tmp) = &get_record('ID_products',$id,'sl_products');
	$prod=0;
	if ($tmp{'id_products'}>0){
		$prod=1;
		
		foreach my $key (keys %tmp){
			$in{$key} = $tmp{$key};
		}
		$in{'id_products_code'} = substr($in{'id_products'},0,3) .'-'.substr($in{'id_products'},3,3);
				
		my ($shptotal1,$shptotal2,$shptotal3,$shptotal1pr,$shptotal2pr,$shptotal3pr,$shp_text1,$shp_text2,$shp_text3,$shp_textpr1,$shp_textpr2,$shp_textpr3) = &sltv_itemshipping($in{'edt'},$in{'SizeW'},$in{'SizeH'},$in{'SizeL'},$in{'Weight'},$in{'ID_packingopts'},$in{'shipping_table'},$in{'shipping_discount'},$in{'ID_products'});
		$va{'shptotal1'} = &format_price($va{'shptotal1'});
		$va{'shptotal2'} = &format_price($va{'shptotal2'});
		$va{'shptotal1pr'} = &format_price($va{'shptotal1pr'});
		$va{'shptotal2pr'} = &format_price($va{'shptotal2pr'});
	
		### Calculate Shipping Charges
		#$size = $in{'sizew'}*$in{'sizeh'}*$in{'sizel'};
		#$weight = $in{'weight'};
		#($va{'shptype1_1lb'},$va{'shptype2_1lb'},$va{'shptype3_1lb'}) = split(/,/,$cfg{'shp_factors1'});
		#($va{'shptype1_add'},$va{'shptype2_add'},$va{'shptype3_add'}) = split(/,/,$cfg{'shp_factors2'});
		#($va{'shpconv1'},$va{'shpconv2'},$va{'shpconv3'}) = split(/,/,$cfg{'shp_wvconv'});
		#$weight = int($size/$va{'shpconv1'}+0.999);
		#if ($weight < $in{'weight'}){
		#	$weight = $in{'weight'};
		#}
		#if ($weight>1){
		#	$weight = int($va{'shptype1_1lb'} + $va{'shptype1_add'}*($weight- 1 + 0.99));
		#}else{
		#	$weight = $va{'shptype1_1lb'};
		#}
		$in{'shpcharges'} = &format_price($weight);
		
		#### MSRP
		$in{'msrp'} = &format_price($in{'msrp'});
		
		
		
		### Brands
		if ($in{'id_brands'}){
			$in{'brands_name'} = &load_name('sl_brands','ID_brands',$in{'id_brands'},'Name');
		}else{
			$in{'id_brands'} = '---';
			$in{'brands_name'} = '';
		}
		
		return 'ok';
	}else{
		return 'error';
	}
}

sub load_product_name {
# --------------------------------------------------------
	my ($sltvid) = @_;
	if (length($sltvid) eq 9){
		my ($tid) = substr($sltvid,0,1);
		if ($tid eq 1){
			return &load_db_names('sl_products','ID_products',substr($sltvid,3,6),'[Model] / [Name]')
		}elsif ($tid eq 4){
			return &load_db_names('sl_parts','ID_parts',substr($sltvid,3,6),'[Model] / [Name]')
		}elsif ($tid eq 6){
			return &load_name('sl_services','ID_services',substr($sltvid,3,6),'Name')
		}else{
			return '---';
		}
	}elsif (length($sltvid) eq 6){
		return &load_db_names('sl_products','ID_products',$sltvid,'[Model] / [Name]')
	}else{
		return '---';
	}
}



sub load_contract_totals{
# --------------------------------------------------------
# Created :  Roberto Barcenas 10/26/2011 4:05:28 PM
# Last Update by RB on 06/29/2012: Se adecua para spots ($mintime)
#
	my ($contract,$edt,$edd,$did)=@_;
#	$i = 17;
#	$edt = '08:30:00';
#	$edd = '2011-01-01';
#	$did = 1133;

	$mintime = $va{'id_mediacontracts_rep'} ? 0 : -30;

	my ($nextcontract, $rec1,$rec2);
	if ($did > 9900){
		my $sth2 = &Do_SQL("SELECT DATE(DATE_ADD(CONCAT('$edd', ' ', '$edt'), INTERVAL 1 DAY))"); 
		$nextcontract = $sth2->fetchrow . "00:00:00";
		#### Deberia er un query diferente
		my $q1 = "
		SELECT
		SUM(P1qtyTDC) AS P1qtyTDC, SUM(P1totTDC)AS P1totTDC, SUM(P1qtyCOD) AS P1qtyCOD, SUM(P1totCOD) AS P1totCOD,

		SUM(OqtyTDC) AS OqtyTDC, SUM(OtotTDC)AS OtotTDC, SUM(OqtyCOD) AS OqtyCOD, SUM(OtotCOD) AS OtotCOD,
        SUM(SqtyTDC) AS SqtyTDC, SUM(StotTDC) AS StotTDC, SUM(SqtyCOD) AS SqtyCOD, SUM(StotCOD) AS StotCOD,
        SUM(COGS) AS COGS
FROM

(SELECT

IF(sl_orders.Status <> 'System Error' AND Ptype='Credit-Card' AND SalePrice>0,1,0)  AS P1qtyTDC,
SUM(IF(sl_orders.Status <> 'System Error' AND Ptype='Credit-Card' AND SalePrice>0,SalePrice,0)) AS P1totTDC,

IF(sl_orders.Status <> 'System Error' AND Ptype='COD' AND SalePrice>0,1,0)  AS P1qtyCOD,
SUM(IF(sl_orders.Status <> 'System Error' AND Ptype='COD' AND SalePrice>0,SalePrice,0)) AS P1totCOD,

IF(sl_orders.Status <> 'System Error' AND Ptype='Credit-Card' AND SalePrice>0,1,0)  AS OqtyTDC,
SUM(IF(sl_orders.Status <> 'System Error' AND Ptype='Credit-Card' AND SalePrice>0,SalePrice,0)) AS OtotTDC,

IF(sl_orders.Status <> 'System Error' AND Ptype='COD' AND SalePrice>0,1,0)  AS OqtyCOD,
SUM(IF(sl_orders.Status <> 'System Error' AND Ptype='COD' AND SalePrice>0,SalePrice,0))  AS OtotCOD,

IF(sl_orders.Status = 'Shipped' AND Ptype='Credit-Card' AND SalePrice>0,1,0)  AS SqtyTDC,
SUM(IF(sl_orders.Status = 'Shipped' AND Ptype='Credit-Card' AND SalePrice>0,SalePrice,0)) AS StotTDC,

IF(sl_orders.Status = 'Shipped' AND Ptype='COD' AND SalePrice>0,1,0)  AS SqtyCOD,
SUM(IF(sl_orders.Status = 'Shipped' AND Ptype='COD' AND SalePrice>0,SalePrice,0))  AS StotCOD,

SUM(IF(sl_orders.Status = 'Shipped' ,Cost,0))  AS COGS

FROM sl_orders INNER JOIN sl_orders_products
ON sl_orders.ID_orders = sl_orders_products.ID_orders

WHERE ID_mediacontracts='$contract' AND  sl_orders.Date = '$edd'
AND sl_orders_products.Status='Active' GROUP BY sl_orders.ID_Orders ) AS tmp";
		my ($sth) = &Do_SQL($q1);
		$rec1 = $sth->fetchrow_hashref();
		
	}else{
		my $q2 = "
SELECT
		SUM(P1qtyTDC) AS P1qtyTDC, SUM(P1totTDC)AS P1totTDC, SUM(P1qtyCOD) AS P1qtyCOD, SUM(P1totCOD) AS P1totCOD,
		SUM(P2qtyTDC) AS P2qtyTDC, SUM(P2totTDC)AS P2totTDC, SUM(P2qtyCOD) AS P2qtyCOD, SUM(P2totCOD) AS P2totCOD,
		SUM(P3qtyTDC) AS P3qtyTDC, SUM(P3totTDC)AS P3totTDC, SUM(P3qtyCOD) AS P3qtyCOD, SUM(P3totCOD) AS P3totCOD,

		SUM(OqtyTDC) AS OqtyTDC, SUM(OtotTDC)AS OtotTDC, SUM(OqtyCOD) AS OqtyCOD, SUM(OtotCOD) AS OtotCOD,
        SUM(SqtyTDC) AS SqtyTDC, SUM(StotTDC) AS StotTDC, SUM(SqtyCOD) AS SqtyCOD, SUM(StotCOD) AS StotCOD,
        SUM(COGS) AS COGS
FROM

(SELECT

IF(TIMESTAMPDIFF(MINUTE, '$edd $edt', CONCAT( sl_orders.Date, ' ', sl_orders.Time ) ) BETWEEN $mintime AND 90 AND sl_orders.Status <> 'System Error' AND Ptype='Credit-Card' AND SalePrice>0,1,0)  AS P1qtyTDC,
SUM(IF(TIMESTAMPDIFF(MINUTE, '$edd $edt', CONCAT( sl_orders.Date, ' ', sl_orders.Time ) ) BETWEEN $mintime AND 90 AND sl_orders.Status <> 'System Error' AND Ptype='Credit-Card' AND SalePrice>0,SalePrice,0)) AS P1totTDC,

IF(TIMESTAMPDIFF(MINUTE, '$edd $edt', CONCAT( sl_orders.Date, ' ', sl_orders.Time ) ) BETWEEN $mintime AND 90 AND sl_orders.Status <> 'System Error' AND Ptype='COD' AND SalePrice>0,1,0)  AS P1qtyCOD,
SUM(IF(TIMESTAMPDIFF(MINUTE, '$edd $edt', CONCAT( sl_orders.Date, ' ', sl_orders.Time ) ) BETWEEN $mintime AND 90 AND sl_orders.Status <> 'System Error' AND Ptype='COD' AND SalePrice>0,SalePrice,0)) AS P1totCOD,

IF(TIMESTAMPDIFF(MINUTE, '$edd $edt', CONCAT( sl_orders.Date, ' ', sl_orders.Time ) ) BETWEEN 91 AND 360 AND sl_orders.Status <> 'System Error' AND Ptype='Credit-Card' AND SalePrice>0,1,0)  AS P2qtyTDC,
SUM(IF(TIMESTAMPDIFF(MINUTE, '$edd $edt', CONCAT( sl_orders.Date, ' ', sl_orders.Time ) ) BETWEEN 91 AND 360 AND sl_orders.Status <> 'System Error' AND Ptype='Credit-Card' AND SalePrice>0,SalePrice,0)) AS P2totTDC,

IF(TIMESTAMPDIFF(MINUTE, '$edd $edt', CONCAT( sl_orders.Date, ' ', sl_orders.Time ) ) BETWEEN 91 AND 360 AND sl_orders.Status <> 'System Error' AND Ptype='COD' AND SalePrice>0,1,0)  AS P2qtyCOD,
SUM(IF(TIMESTAMPDIFF(MINUTE, '$edd $edt', CONCAT( sl_orders.Date, ' ', sl_orders.Time ) ) BETWEEN 91 AND 360 AND sl_orders.Status <> 'System Error' AND Ptype='COD' AND SalePrice>0,SalePrice,0)) AS P2totCOD,

IF(TIMESTAMPDIFF(MINUTE, '$edd $edt', CONCAT( sl_orders.Date, ' ', sl_orders.Time ) ) > 360 AND sl_orders.Status <> 'System Error' AND Ptype='Credit-Card' AND SalePrice>0,1,0)  AS P3qtyTDC,
SUM(IF(TIMESTAMPDIFF(MINUTE, '$edd $edt', CONCAT( sl_orders.Date, ' ', sl_orders.Time ) ) > 360 AND sl_orders.Status <> 'System Error' AND Ptype='Credit-Card' AND SalePrice>0,SalePrice,0)) AS P3totTDC,

IF(TIMESTAMPDIFF(MINUTE, '$edd $edt', CONCAT( sl_orders.Date, ' ', sl_orders.Time ) ) > 360 AND sl_orders.Status <> 'System Error' AND Ptype='COD' AND SalePrice>0,1,0)  AS P3qtyCOD,
SUM(IF(TIMESTAMPDIFF(MINUTE, '$edd $edt', CONCAT( sl_orders.Date, ' ', sl_orders.Time ) ) > 360 AND sl_orders.Status <> 'System Error' AND Ptype='COD' AND SalePrice>0,SalePrice,0)) AS P3totCOD,

IF(sl_orders.Status <> 'System Error' AND Ptype='Credit-Card' AND SalePrice>0,1,0)  AS OqtyTDC,
SUM(IF(sl_orders.Status <> 'System Error' AND Ptype='Credit-Card' AND SalePrice>0,SalePrice,0)) AS OtotTDC,

IF(sl_orders.Status <> 'System Error' AND Ptype='COD' AND SalePrice>0,1,0)  AS OqtyCOD,
SUM(IF(sl_orders.Status <> 'System Error' AND Ptype='COD' AND SalePrice>0,SalePrice,0))  AS OtotCOD,

IF(sl_orders.Status = 'Shipped' AND Ptype='Credit-Card' AND SalePrice>0,1,0)  AS SqtyTDC,
SUM(IF(sl_orders.Status = 'Shipped' AND Ptype='Credit-Card' AND SalePrice>0,SalePrice,0)) AS StotTDC,

IF(sl_orders.Status = 'Shipped' AND Ptype='COD' AND SalePrice>0,1,0)  AS SqtyCOD,
SUM(IF(sl_orders.Status = 'Shipped' AND Ptype='COD' AND SalePrice>0,SalePrice,0))  AS StotCOD,

SUM(IF(sl_orders.Status = 'Shipped' ,Cost,0))  AS COGS

FROM sl_orders INNER JOIN sl_orders_products
ON sl_orders.ID_orders = sl_orders_products.ID_orders

WHERE ID_mediacontracts='$contract'
AND sl_orders_products.Status='Active' GROUP BY sl_orders.ID_Orders ) AS tmp";
		my ($sth) = &Do_SQL($q2);
		$rec1 = $sth->fetchrow_hashref();
	}

	
	my $q3 = "
SELECT
		SUM(RqtyTDC) AS RqtyTDC, SUM(RtotTDC)AS RtotTDC, SUM(RqtyCOD) AS RqtyCOD, SUM(RtotCOD) AS RtotCOD,
		SUM(XqtyTDC) AS XqtyTDC, SUM(XtotTDC)AS XtotTDC, SUM(XqtyCOD) AS XqtyCOD, SUM(XtotCOD) AS XtotCOD
FROM
(SELECT

IF(Ptype='COD' AND Reason='Refund' AND Amount<0,1,0)  AS RqtyCOD,
SUM(IF(Ptype='COD' AND Reason='Refund' AND Amount<0,Amount,0))  AS RtotCOD,

IF(Ptype='Credit-Card' AND Reason='Refund' AND Amount<0,1,0)  AS RqtyTDC,
SUM(IF(Ptype='Credit-Card' AND Reason='Refund' AND Amount<0,Amount,0)) AS RtotTDC,

IF(Ptype='COD' AND Reason='Exchange' AND Amount<0,1,0)  AS XqtyCOD,
SUM(IF(Ptype='COD' AND Reason='Exchange' AND Amount<0,Amount,0))  AS XtotCOD,

IF(Ptype='Credit-Card' AND Reason='Exchange' AND Amount<0,1,0)  AS XqtyTDC,
SUM(IF(Ptype='Credit-Card' AND Reason='Exchange' AND Amount<0,Amount,0)) AS XtotTDC

FROM sl_orders INNER JOIN sl_orders_payments ON sl_orders.ID_Orders = sl_orders_payments.ID_Orders
WHERE ID_mediacontracts='$contract' AND Amount < 0 AND Captured='Yes'
AND sl_orders.Status NOT IN('System Error','Void','Cancelled')
AND sl_orders_payments.Status='Approved'
GROUP BY sl_orders.ID_orders)as tmp;";
	my ($sth) = &Do_SQL($q3);
	$rec2 = $sth->fetchrow_hashref();

	return ($rec1,$rec2);
}



#	Function: load_count_rep
#
#   		Load the configuration data from general.ex.cfg and general.e1.cfg files
#
#	Created by:
#		_Carlos Haas_
#
#	Modified By:
#
#
#   	Parameters:
#
#
#   	Returns:
#
#
#   	See Also:
#
sub load_count_rep{
# --------------------------------------------------------
	my ($id_cont,$repESTDate,$repESTTime)=@_;

	## Next Spot.
	my ($sth3) = &Do_SQL("SELECT CONCAT(repESTDate,' ',repESTTime)AS nexspot FROM sl_mediacontracts_rep WHERE ID_mediacontracts = '$id_cont' AND CONCAT(repESTDate,' ',repESTTime) > '$repESTDate $repESTTime' ORDER BY CONCAT(repESTDate,' ',repESTTime) LIMIT 1;");
	my ($next_date) = $sth3->fetchrow();
	my ($nextcall,$nextorder);

	if ($next_date){
		$nextcall =  " AND CONCAT(Date, ' ', Time) < '$next_date' "; 
		$nextorder = " AND CONCAT(sl_orders.Date, ' ', sl_orders.Time) < '$next_date' "; 
	}else{
		$nextcall = '';
		$nextorder = '';
	}
	
	my ($sth3) = &Do_SQL("SELECT COUNT(*) FROM sl_leads_calls WHERE ID_mediacontracts='$id_cont' AND CONCAT(Date, ' ', Time)>='$repESTDate $repESTTime' AND IO='In' $nextcall ");
	my ($calls) = $sth3->fetchrow();
	
	my $q3 = "SELECT SUM(OqtyTDC), SUM(OtotTDC), SUM(OqtyCOD) , SUM(OtotCOD), 
								 SUM(SqtyTDC), SUM(StotTDC), SUM(SqtyCOD) , SUM(StotCOD),
								 COGS
				FROM
				(SELECT
				1 AS Label, 
				IF(sl_orders.Status <> 'System Error' AND Ptype='Credit-Card' AND SalePrice>0,1,0)  AS OqtyTDC,
				IF(sl_orders.Status <> 'System Error' AND Ptype='Credit-Card' AND SalePrice>0,SalePrice,0) AS OtotTDC,
				
				IF(sl_orders.Status <> 'System Error' AND Ptype='COD' AND SalePrice>0,1,0)  AS OqtyCOD,
				IF(sl_orders.Status <> 'System Error' AND Ptype='COD' AND SalePrice>0,SalePrice,0) AS OtotCOD,

				IF(sl_orders.Status = 'Shipped' AND Ptype='Credit-Card' AND SalePrice>0,1,0)  AS SqtyTDC,
				IF(sl_orders.Status = 'Shipped' AND Ptype='Credit-Card' AND SalePrice>0,SalePrice,0) AS StotTDC,
				
				IF(sl_orders.Status = 'Shipped' AND Ptype='COD' AND SalePrice>0,1,0)  AS SqtyCOD,
				IF(sl_orders.Status = 'Shipped' AND Ptype='COD' AND SalePrice>0,SalePrice,0) AS StotCOD,
				
				IF(sl_orders.Status = 'Shipped' ,Cost,0)  AS COGS
				
				FROM sl_orders INNER JOIN sl_orders_products ON sl_orders.ID_orders = sl_orders_products.ID_orders
				WHERE ID_mediacontracts='$id_cont' AND CONCAT(sl_orders.Date, ' ', sl_orders.Time)>='$repESTDate $repESTTime' $nextorder
				AND sl_orders_products.Status='Active' GROUP BY sl_orders.ID_Orders) AS tmp GROUP BY Label";

	my ($sth3) = &Do_SQL($q3);
	
	my ($qtdc,$ttdc,$qcod,$tcod ,$sqtdc,$sttdc,$sqcod,$stcod, $cogs) = $sth3->fetchrow_array();
	return ($calls,$ttdc,$tcod,$qtdc,$qcod, $sttdc.$stcod,$sqtdc,$sqcod, $cogs);
}


sub load_convfile {
# --------------------------------------------------------
# Created on : 01/02/2008 3:15PM
# Author : Rafael Sobrino
# Modified: Alejadro Diaz on 07/05/2013
# Description : uploads a file to the server while removing double quotes, replacing commas with tabs, and converting the file name to lower case.
# Notes : 

	my ($temp_file,$bin,$allowed_extensions) = @_;
	$allowed_extensions = $cfg{'upload_allowed_file_extensions'} if (!$allowed_extensions or $allowed_extensions eq '');
	$filename = $in{'file'};
	$filename =~ s/.*[\/\\](.*)/$1/;
	
	$temp = lc($temp_file);
	my ($ext) = $filename =~ /(\.[^.]+)$/;
	my ($only_ext) = $ext;
	$only_ext =~ s/\.//g;
	
	if ($allowed_extensions ne '') {
		@extensions = split /\,/, $allowed_extensions;
		if (grep( /^$only_ext$/, @extensions )) {
			$temp =~ s/$ext/.txt/g;
		}else {
			return 2;
		}
	}else {
		$temp =~ s/.csv|.xls/.txt/g;
	}

	if (open(my $save, ">", $temp_file)){
		($bin) and (binmode ($save));
		my ($total_size) =0;
		my $line="";
		while ($size = read($filename,$line,1024)){
			if(!$bin)
			{
				$line =~ s/\"//g;	# remove all double quotes
				$line =~ s/,/\t/g;	# replace all commas with tabs
			}
			print $save $line;
			$total_size += $size;
		}

		## file successfully uploaded		
		if ($total_size > 0){
			rename ("$temp_file","$temp");
			return 1; 
		}
	}
	return 0;
}



sub load_customer_phone {	
# --------------------------------------------------------

# Author: Jose Ramirez Garcia
# Created on: 
# Last Modified on: 
# Last Modified by: 
# Description : 
# Forms Involved: 
## Parameters : 
# Last Modified RB: 07/30/09  12:40:56 -- InnovaUSA no devuelve Telefonos.


  my ($id_customers) = @_; 		
  my $output = '';
  
  ###### IF LA
  return $output if $in{'e'} == 1;
  		
	my ($sth) = &Do_SQL("SELECT 
											CONCAT( 
											IF(Phone1 IS NOT NULL AND Phone1 != '',Phone1,''),
											IF(Phone2 IS NOT NULL AND Phone2 != '',CONCAT('<br>',Phone2),''),
											IF(Cellphone IS NOT NULL AND Cellphone != '',CONCAT('<br>',Cellphone),'')) AS Phone 
											FROM sl_customers WHERE ID_customers='$id_customers';");
	$output = $sth->fetchrow;
	
	return "Tels:".$output."<br>";
}

sub load_file {
# --------------------------------------------------------
# Created on : 11/15/2007 3:15PM
# Author : Rafael Sobrino
# Description : uploads a file to the server
# Notes : 
# Modified on 12/28/2007 by Rafael Sobrino
# Reason : 

	my ($temp_file,$bin) = @_;
	$filename = $in{'file'};
	$filename =~ s/.*[\/\\](.*)/$1/;
	
	if (open(my $save,">", $temp_file)){
		($bin) and (binmode ($save));
		my ($total_size) =0;
		while ($size = read($filename,$line,1024)){
			print $save $line;		
			$total_size += $size;
		}

				
		if ($total_size >0){ return 1; }	## file successfully uploaded
	}
	return 0;
}

sub load_invoice_data{
#-----------------------------------------
# Forms Involved: load_inv_products
# Created on: 07/15/08  10:54:36
# Last Modified on: 07/15/08  10:54:36
# Last Modified by: Roberto Barcenas
# Last Modified Desc:
# Author: Roberto Barcenas
# Description : Print client payment information to invoice
# Parameters : 
# Last Modified RB: 03/25/09  11:41:24 -- Se discriminan los pagos 'Cancelled',' Order Cancelled' y Amount < 0. Ademas los producots Order Cancelled. 	
#Last modified on 7 Feb 2011 17:52:40
#Last modified by: MCC C. Gabriel Varela S. :Se incluyen textos en inglés
# Last Time Modified By RB on 02/08/2011 : Se vuelve a activar el texto que indica la cantidad de pagos y cada cuanto se cobraran
#Last modified on 15 Feb 2011 15:31:55
#Last modified by: MCC C. Gabriel Varela S. : Por indicación de Carlos se quita mensaje invoice_fp
# Last Time Modified By RB on	02/23/2011: Si es un solo pago no dice el primero de n pagos.
# Last Time Modified By RB on	03/21/2011 06:50:27 PM: Solo se agrega mensaje para TDC o Layaway
# Last Modified on: 04/18/11 12:08:44 PM
# Last Modified by: MCC C. Gabriel Varela S: Se hace que las postdated no se recalculen pagos.

		my ($data,$rec,$npayments,$amount,$d1,$d2,$fpay,$d2,$porder);
	
		$dd1 = '0,1';
		$dd2 = '1,1';
		$data2 = '';
		$va{'fp_msg'} = '';
		# Si la orden es COD no lleva extra info?
		return if ($in{'ptype'} ne 'Credit-Card' and $in{'ptype'} ne 'Layaway');
		
		## Reasignamos fechas de Paymentdate
		if(!is_postdated($in{'id_orders'})){		#$cfg{'shprecaldate'}
			my ($today) = &get_sql_date(0);
			$orderdate = &load_name('sl_orders','ID_orders',$in{'id_orders'},'Date');
			my ($dth) = Do_SQL("SELECT COUNT(*) FROM sl_orders_payments WHERE ID_orders = '$in{'id_orders'}' AND Captured='Yes' AND CapDate > '2000-01-01';");
			if($dth->fetchrow() > 0){
				my $sth = &Do_SQL("SELECT CapDate FROM sl_orders_payments WHERE ID_orders = '$in{'id_orders'}' AND Captured='Yes' AND CapDate > '2000-01-01' ORDER BY CapDate LIMIT 1;");
				$today = $sth->fetchrow();
			}
			&update_flexipago($in{'id_orders'},$today);
		}
		
		my ($sth) = &Do_SQL("SELECT IF(CapDate IS NULL OR CapDate = '0000-00-00' OR AuthCode IS NULL OR AuthCode = '' OR AuthCode = '0000',CURDATE(),CapDate) AS CapDate,RIGHT(PmtField3,4) AS ccard,Amount FROM `sl_orders_payments` WHERE ID_orders = $in{'id_orders'} AND Status NOT IN ('Order Cancelled', 'Cancelled') AND Amount > 0 ORDER BY Paymentdate  LIMIT 1");
		$rec = $sth->fetchrow_hashref;
	
		my ($sth) = &Do_SQL("SELECT COUNT(*) FROM `sl_orders_payments` WHERE ID_orders = $in{'id_orders'} AND Status NOT IN ('Order Cancelled', 'Cancelled') AND Amount > 0 ");
		$npayments = $sth->fetchrow;
		
		
		($npayments > 2) and ($dd1 = '1,1') and ($dd2 = '2,1');
	
		my ($sth) = &Do_SQL("SELECT Amount FROM `sl_orders_payments` WHERE ID_orders = $in{'id_orders'} AND Status NOT IN ('Order Cancelled', 'Cancelled') AND Amount > 0 ORDER BY Paymentdate DESC LIMIT 1");
		$amount = $sth->fetchrow;
	
		my ($sth) = &Do_SQL("SELECT Paymentdate FROM `sl_orders_payments` WHERE ID_orders = $in{'id_orders'} AND Status NOT IN ('Order Cancelled', 'Cancelled') AND Amount > 0 ORDER BY Paymentdate LIMIT $dd1 ");
		$d1 = $sth->fetchrow;
	
		my ($sth) = &Do_SQL("SELECT Paymentdate FROM `sl_orders_payments` WHERE ID_orders = $in{'id_orders'} AND Status NOT IN ('Order Cancelled', 'Cancelled') AND Amount > 0 ORDER BY Paymentdate LIMIT $dd2 ");
		$d2 = $sth->fetchrow;
	
		my ($sth) = &Do_SQL("SELECT DATEDIFF('$d2','$d1') ");
		$fpay = $sth->fetchrow;
	

		# Extraemos el idioma del invoice
		my $order_lang= &load_name('sl_orders','ID_orders',$in{'id_orders'},'language')eq'english' ? 'en' : 'sp';

		if($porder == 0){
			
			my ($sth) = &Do_SQL("SELECT GROUP_CONCAT(Paymentdate,'  \$',Amount ORDER BY Paymentdate SEPARATOR ' , ') FROM sl_orders_payments WHERE ID_orders = '$in{'id_orders'}' AND Status NOT IN ('Order Cancelled', 'Cancelled') AND Captured='No' AND Amount > 0;");
			$dates_amounts = $sth->fetchrow();
			
			if($npayments > 1){
				if(&is_adm_order($in{'id_orders'}) or $order_lang eq 'en'){
					$data2 .= qq| You have |.($npayments -1).qq| pending payments, for the amount of |.&format_price($amount).qq| each one. They will be charged every $fpay days.|;
				}else{
					($npayments -1 == 1) and ($data2 .= qq| El pago restante, por un monto de |.&format_price($amount).qq| ser&aacute; capturado en $fpay d&iacute;as.|);
					($npayments -1  > 1) and ($data2 .= qq| Los |.($npayments -1).qq| pagos restantes, por un monto de |.&format_price($amount).qq| cada uno ser&aacute;n cargados a su cuenta cada $fpay d&iacute;as ($dates_amounts).|);
				}
			}
			if(&is_adm_order($in{'id_orders'}) or $order_lang eq 'en'){
				$data .= qq|<p>&nbsp;</p>Your Credit Card ************$rec->{'ccard'} was charged on $rec->{'CapDate'}. The first of $npayments payments was for |.&format_price($rec->{'Amount'}).qq|. 
								It includes S&H and applicable taxes(FL and CA residents). $data2|;
			}else{
				$data .= qq|En fecha $rec->{'CapDate'} el primero de $npayments pagos fu&eacute; cargado a su cuenta con terminaci&oacute;n $rec->{'ccard'} por un monto de |.&format_price($rec->{'Amount'}).qq|<br> $data2 | if $npayments > 1;
				$data .= qq|En fecha $rec->{'CapDate'} un monto de |.&format_price($rec->{'Amount'}).qq| fu&eacute; cargado a su cuenta con terminaci&oacute;n $rec->{'ccard'}| if $npayments == 1;
			}
			if(&is_adm_order($in{'id_orders'}) or $order_lang eq 'en'){
				#$va{'fp_msg'} = &trans_txt('invoice_fpen')	if $npayments > 1;
				$va{'fp_msg'} =''	if $npayments > 1;
			}else{
				$va{'fp_msg'}  = $data . qq|<p> * Incluye gastos de envio y manejo (impuestos en estados donde aplique).<br>|;
				$va{'fp_msg'}  .= '</p>';
			}
		}						
}	

sub load_variables(%cses){
#-------------------------------------------------------------------------------
# Forms Involved: 
# Created on: 07/14/08 11:29:25
# Author: MCC C. Gabriel Varela S.
# Description :  Crea las variables del tipo va para ser utilizadas en los speeches
# Parameters : 
# Last Modified on: 07/15/08 09:33:59
# Last Modified by: MCC C. Gabriel Varela S: Se agrega validación para ver si existe la tabla.
# Last Modified on: 07/29/08 18:05:54
# Last Modified by: MCC C. Gabriel Varela S: Se pone el nombre de variable por [tabla].[campo]
# Last Modified on: 09/03/08 09:54:46
# Last Modified by: MCC C. Gabriel Varela S: Se hace la validación tomando en cuenta también el modelo del producto
# Last Modified on: 03/17/09 16:30:55
# Last Modified by: MCC C. Gabriel Varela S: Nuevos parámetros para sltv_itemshipping
# Last Modified RB: 12/07/2010  19:06:44 -- Se agregan parametros para calculo de shipping

	my (%cses)=@_;
	my ($key,$i);
	&converts_in_to_va();
	&converts_cses_to_va(%cses);
	foreach my $key (keys %va)
	{
		if($key=~ /^(id_)(.*)$/)
		{
			
			#Checar si existe la tabla
			my ($ct)=&Do_SQL("SHOW TABLES like 'sl_$2'");
			my ($et)=$ct->fetchrow();
			if ($et ne '')
			{

				my ($hts)=&Do_SQL("SELECT * FROM sl_$2 WHERE id_$2='$va{$key}'");
				my @cer=$hts->fetchrow_array();
				my ($hts1)=&Do_SQL("describe sl_$2");
				$i=0;
				while(my @cer1=$hts1->fetchrow_array())
				{
					$vaname=lc($cer1[0]);
					$va{"$2.$vaname"}=$cer[$i] if (!$va{"$2.$vaname"} and $cer[$i] ne '');
#					$una=$va{"$vaname"};
#					$texto.="$vaname: $una\n";
					$i++;
				}
			}
		}
		#$texto.="$key: $va{$key}\n";
	}
	if($va{'products.name'}ne"" or $va{'products.model'}ne"")
	{

		if(!$va{'products.sprice'} or $va{'products.sprice'} == 0 ){

			my ($sth) = &Do_SQL("SELECT Price,FP FROM sl_products_prices WHERE ID_products = '$va{'products.id_products'}' AND PayType = '$cfg{'payments_default_type'}' ORDER BY Price LIMIT 1;");
			my ($price,$fp) = $sth->fetchrow();
			$va{'products.sprice'} = $price > 0 ? $price : 1;
			$va{'products.flexipago'} = $fp > 0 ? $fp : 1;		

		}

		$va{'products.priceafterrebate'}=&format_price($va{'products.sprice'}-$va{'products.rebate'});
		$va{'products.rebate'}=&format_price($va{'products.rebate'});
		$va{'products.msrp'}=&format_price($va{'products.msrp'});
		($shptotal1,$shptotal2,$shptotal3,$shptotal1pr,$shptotal2pr,$shptotal3pr,$va{'shp_text1'},$va{'shp_text2'},$va{'shp_text3'},$va{'shp_textpr1'},$va{'shp_textpr2'},$va{'shp_textpr3'})= &sltv_itemshipping($va{'products.edt'},$va{'products.sizew'}*$va{'products.sizeh'}*$va{'products.sizel'},1,1,$va{'products.weight'},$va{'products.id_packingopts'},$va{'products.shipping_table'},$va{'products.shipping_discount'},$va{'products.id_products'});
		$va{'products.shipping'} = $shptotal1 if ($va{'products.shipping'}eq"");
		$va{'products.shipping'} = &format_price($va{'products.shipping'},2);
		
		$va{'products.weeks'}=$va{'products.flexipago'}*4;
		$va{'products.months'}=$va{'products.flexipago'};
		
		if ($va{'products.fpprice'}>0){
			$va{'products.discountporc'} = int($va{'products.sprice'}/$va{'products.fpprice'});
			$va{'products.discountvakue'} = &format_price($va{'products.fpprice'}-$va{'products.sprice'});
			$va{'products.onepayment'} = &format_price($va{'products.sprice'});
			$va{'products.weeklyprice'}=&format_price($va{'products.fpprice'}/$va{'products.flexipago'}/4);
			$va{'products.monthlyprice'}=&format_price($va{'products.fpprice'}/$va{'products.flexipago'});
			$va{'products.sprice'}=&format_price($va{'products.fpprice'});
			$va{'products.weekdownpayment'}=&format_price($va{'products.fpprice'}/$va{'products.flexipago'}/4+99+$va{'products.shipping'});
		}else{
			if ($idproducts =~ /$cfg{'disc40'}/){
				$va{'products.discountporc'}= 40;
				$va{'products.discountvakue'}=&format_price($va{'products.sprice'}*40/100);
				$va{'products.onepayment'} = &format_price($va{'products.sprice'}-$va{'products.sprice'}*40/100);
			}elsif ($idproducts =~ /$cfg{'disc30'}/){
				$va{'products.discountporc'}= 30;
				$va{'products.discountvakue'}=&format_price($va{'products.sprice'}*30/100);
				$va{'products.onepayment'} = &format_price($va{'products.sprice'}-$va{'products.sprice'}*30/100);
			}else{
				$va{'products.discountporc'}=$cfg{'fpdiscount'.$va{'products.flexipago'}};
				$va{'products.discountvakue'}=&format_price($va{'products.sprice'}*$cfg{'fpdiscount'.$va{'products.flexipago'}}/100);
				$va{'products.onepayment'} = &format_price($va{'products.sprice'}-$va{'products.sprice'}*$cfg{'fpdiscount'.$va{'products.flexipago'}}/100);
			}
			$va{'products.weeklyprice'}=&format_price($va{'products.sprice'}/$va{'products.flexipago'}/4);
			$va{'products.monthlyprice'}=&format_price($va{'products.sprice'}/$va{'products.flexipago'});
			$va{'products.sprice'}=&format_price($va{'products.sprice'});
			$va{'products.weekdownpayment'}=&format_price($va{'products.sprice'}/$va{'products.flexipago'}/4+99+$va{'products.shipping'});
		}
	}
}

sub load_plogs{
# --------------------------------------------------------
# Created on: 01/19/09 @ 12:56:13
# Author: Carlos Haas
# Last Modified on: 01/19/09 @ 12:56:13
# Last Modified by: Carlos Haas
# Description : 
# Parameters : 
#			 
	my (@output,$key,%tmp,$value,$a,@ary);
	my ($data,$fnames) = @_;
	$fnames = ",$fnames,";
	my (@ary) = split(/\n/,$data);
	for (0..$#ary){
		($key,$value) = split(/=/,$ary[$_],2);
		$key =~ s/\s//g; $value =~ s/\s//g;
		if ($fnames =~ /,$key,/i){
			push(@output, $value);
		}
	}
	return @output;
}


sub load_invoice_products{
# --------------------------------------------------------
# Forms Involved: invoice_view.html
# Created on: 30 Aug 2011 13:50:19
# Author: Roberto Barcenas.
# Description : Sustituye a la funcion load_inv_products por nueva forma
# Parameters :
# Last Time Modified by RB on 09/01/2011: Los points se expresan solo como id_products de regalo y se ocupan en el template a manera de imagen
# Last Time Modified by RB on 10/06/2011: Se cambia is_adm_order por is_exportation_order
# Last Time Modified by RB on 01/12/2012: Se quita contenido dentro de [] en los nombres

	my ($style,$output,$tot_qty,$tot_ord,$choices,$prefix,$id_products);
	$query='';
	my ($query)='';

	$va{'e_prefix'} = $cfg{'prefixentershipment'};
	$va{'extra_output'}='';
	
	$prefix="Related_"if(&is_exportation_order($in{'id_orders'}));
	$id_products=$prefix."ID_products";

	if ($in{'toprint'}){
		$style = 'stdtext';
	}else{
		$style = 'smalltext';
	}

	$query = " AND ID_products  =  $in{'id_products'} "  if ($in{'id_products'} and  length($in{'id_products'})	== 9 and substr($in{'id_products'},0,1)==4);

	my ($sth) = &Do_SQL("SELECT COUNT(*) FROM sl_orders_products WHERE ID_orders='$in{'id_orders'}' AND Status NOT IN('Order Cancelled', 'Inactive') $query");
	$va{'matches'} = $sth->fetchrow;
	if ($va{'matches'}>0){
		my $is_refill=0;
		my ($sth1) = &Do_SQL("SELECT * FROM sl_orders_products WHERE ID_orders='$in{'id_orders'}' AND Status NOT IN('Order Cancelled', 'Inactive') $query ORDER BY ID_orders_products");
		my ($col);
		while ($col = $sth1->fetchrow_hashref){

			$output .= "<tr style='padding-top:25px;'>";


			my $refill_mark='';
			$d = 1 - $d;
			
			if ($col->{$id_products} < 5000){
				### Services in Order
				$output .= "   <td width=35px valign=top align=center style='border-right: 1px solid black;'><font class=detalles><br>".&format_number($col->{'Quantity'})."</font></td>";
				$output .= "   <td width=90px valign=top align=left style='padding-left:4px;'><font class=detalles><br>$col->{'$id_products'}&nbsp;</td>\n";
				#GV Modifica 21abr2008 Se cambia sl_services por sl_services #GV Modifica 21abr2008 Se cambia ID_services por ID_services
				$output .= "   <td width=350px valign=top align=left><font class=detalles><br>".&load_name('sl_services','ID_services',$col->{$id_products},'Name')."</td>\n";
			}elsif($col->{$id_products}>600000000){
				### Services in Order
				(&load_name('sl_services','ID_services',$col->{$id_products}-600000000,'ServiceType') eq 'Refill') and ($is_refill = 1) and ($refill_mark = ' <strong>**</strong> ');
				$output .= "   <td width=35px valign=top align=center style='border-right: 1px solid black;'><font class=detalles><br>".&format_number($col->{'Quantity'})."</font></td>";
				$output .= "   <td width=90px valign=top align=left style='padding-left:4px;'><font class=detalles><br>".&format_sltvid($col->{$id_products})."&nbsp;</td>\n";
				$output .= "   <td width=350px valign=top align=left><font class=detalles><br>".&load_name('sl_services','ID_services',$col->{$id_products}-600000000,'Name')." $refill_mark</td>\n";
			}else{
				### Products in Order
				$output .= "   <td width=35px valign=top align=center style='border-right: 1px solid black;'><font class=detalles><br>".&format_number($col->{'Quantity'})."</font></td>";
				$output .= "   <td width=90px valign=top align=left style='padding-left:4px;'><font class=detalles><br>".&format_sltvid($col->{$id_products})."&nbsp;</td>\n";
				($col->{'SerialNumber'}) and ($col->{'SerialNumber'} = "<br>$col->{'SerialNumber'}");
				($status,%tmp) = &load_product_info($col->{$id_products});

				if ((!$col->{'Amazon_ID_products'} and &is_exportation_order($in{'id_orders'})) or $query ne ''){
					$tmp{'model'}=&load_name('sl_parts','ID_parts',$col->{$id_products}-400000000,'Model');
					$tmp{'name'}=&load_name('sl_parts','ID_parts',$col->{$id_products}-400000000,'Name');
				}elsif ($col->{'Amazon_ID_products'}){
					my ($sthAzn) = &Do_SQL("SELECT Name FROM cu_products_amazon WHERE ID_products_amazon = '$col->{'Amazon_ID_products'}';");
					$tmp{'model'} = $sthAzn->fetchrow_array();
					$tmp{'name'}='';
				}

				$tmp{'model'} = &replace_in_string($tmp{'model'});
				$tmp{'name'} = &replace_in_string($tmp{'name'});

				if ($in{'print_upc'}){

					$output .= "   <td width=350px valign=top align=left><font class=detalles><br>$tmp{'model'}<br>$tmp{'name'} ".
								"<span class='smalltext'><br>".&load_parts_upc($col->{$id_products})."</span>".
								" $col->{'SerialNumber'} ".&build_tracking_link($col->{'Tracking'},$col->{'ShpProvider'},$col->{'ShpDate'},$col->{$id_products})."</td>\n";
				}else{

					$output .= "   <td width=350px valign=top align=left><font class=detalles><br>$tmp{'model'}<br>$tmp{'name'} ".
								"<span class='smalltext'><br>".&load_parts($col->{$id_products})."</span>".
								" $col->{'SerialNumber'} ".&build_tracking_link($col->{'Tracking'},$col->{'ShpProvider'},$col->{'ShpDate'},$col->{$id_products})."</td>\n";
				}

			}

			if(&is_exportation_order($in{'id_orders'})){
				$output .= "   <td width=65px valign=top align=right><font class=detalles><br>".&format_price($col->{'SalePrice'} / $col->{'Quantity'})."</td>\n";
				$output .= "   <td width=65px valign=top align=right><font class=detalles><br>".&format_price($col->{'SalePrice'})."</td>\n"	if $col->{'SalePrice'} > 0;
				$output .= "   <td width=65px valign=top align=right nowrap><font class=detalles><br>".&format_price($col->{'SalePrice'}*-1)."</td>\n"	if $col->{'SalePrice'} < 0;
				$tot_ord +=$col->{'SalePrice'}if $col->{'SalePrice'} >0;
				$tot_ord -= $col->{'SalePrice'}if $col->{'SalePrice'} <0;
			}else{
				$output .= "   <td width=65px valign=top align=right nowrap><font class=detalles><br>".&format_price($col->{'SalePrice'})."</td>\n";
				$output .= "   <td width=65px valign=top align=right nowrap><font class=detalles><br>".&format_price($col->{'SalePrice'}*$col->{'Quantity'})."</td>\n"	if $col->{'SalePrice'} > 0;
				$output .= "   <td width=65px valign=top align=right nowrap><font class=detalles><br>".&format_price($col->{'SalePrice'}*$col->{'Quantity'}*-1)."</td>\n"	if $col->{'SalePrice'} < 0;
				$tot_ord +=$col->{'SalePrice'}*$col->{'Quantity'} if $col->{'SalePrice'} >0;
				$tot_ord -= $col->{'SalePrice'}*$col->{'Quantity'} if $col->{'SalePrice'} <0;
			}

			$output .= "</tr>\n";
			$tot_qty += $col->{'Quantity'};





		}
		### Orders Totals
		$va{'total_order'} = &format_price(&total_orders_products($in{'id_orders'}));
		$va{'ordernet'} = &format_price(&products_sum_in_order($in{'id_orders'}, "SalePrice"));
		$va{'ordershp'} = &format_price(&products_sum_in_order($in{'id_orders'}, "Shipping"));
		$va{'orderdisc'} = &format_price(&products_sum_in_order($in{'id_orders'}, "Discount"));
		$taxes = &products_sum_in_order($in{'id_orders'}, "Tax");
		$va{'total_taxes'} = &format_price($taxes);

		$va{'tax'} = $in{'ordertax'}*100;
		$va{'ordertax'} = &format_number($in{'ordertax'}*100);

		my $refill_txt='';
		if($is_refill){
			$refill_txt .= qq|
				    &nbsp;<tr>
					    <td colspan='5'>
						 <strong>|.&trans_txt('refill_disclaimer_title').qq|</strong><br>
						 |.&trans_txt('refill_disclaimer_desc').qq|
					    </td>
				    </tr>&nbsp;|;

		}
		##Points
##		my $points_info='';
##		$va{'points_info'}='';
##		$va{'points_info'}=&get_points_info($in{'id_customers'},$in{'id_orders'});
##		$points_info=qq|[ip_forms:reward_points]| if($va{'points_info'}ne'');
		&get_points_info($in{'id_customers'},$in{'id_orders'});


		## Coupons?
		my $add_coupon = '';
		if($cfg{'coupons'} and $in{'ordernet'} >= $cfg{'coupons_mindireksys'}){

			$result = &get_coupon_external('sl_orders',$in{'id_orders'});

			if($result > 0){
				$add_coupon = qq|[ip_forms:coupons_external_view]|;
			}
		}

		$va{'extra_output'} .= qq|
			$refill_txt
			<tr>
				<td align="left" class="smalltext">[fc_load_invoice_data]</td>
			</tr>|;

		if(!&is_adm_order($in{'id_orders'})){
			$va{'extra_output'} .= qq|
				<tr>
					<td align="left" class="smalltext"><p>&nbsp;</p>&nbsp;</td>
				</tr>|;

			#$va{'extra_output'} .= qq|
			#	<tr>
			#		<td align="left" ><p>$points_info</p>&nbsp;</td>
			#	</tr>| if $points_info;

			$va{'extra_output'} .= qq|
				<tr>
					<td align="left" class="smalltext"><p>$add_coupon</p>&nbsp;</td>
				</tr>| if $add_coupon;
		}

	}else{
		$output = qq|
			<tr>
				<td colspan='5' align="center">|.&trans_txt('search_nomatches').qq|</td>
			</tr>\n|;
	}

	## Amazon Promo
	# if($cfg{'amazon_free'}){
		# my $id_admin_users = &load_name('sl_orders','ID_orders',$in{'id_orders'},'ID_admin_users');
		# my $admin_users = &load_name('admin_users','ID_admin_users',$id_admin_users,'LastName');

		# if($admin_users =~ /amazon/i){
			# $va{'amazonfree'} = &build_page('func/amazonfree.html');
		# }
	# }

	&load_cfg('sl_orders');	
	return $output;
}


sub load_order_total {
# --------------------------------------------------------
	my ($id,$posteddate) = @_;
	my ($prefix,$query);
	if ($id > 500000){
		$prefix = 'pre'
	}
	if ($posteddate and !$prefix){
		$query = "AND PostedDate='$posteddate'";
	}
	
	my ($sth)= &Do_SQL("SELECT OrderTax FROM sl_".$prefix."orders WHERE ID_".$prefix."orders=$id");
	my ($tax) = $sth->fetchrow();
	
	
	my ($sth)= &Do_SQL("SELECT SUM(SalePrice),SUM(Discount) FROM sl_".$prefix."orders_products WHERE (ID_products LIKE '4%' OR ID_products LIKE '5%' OR ID_products LIKE '6%') AND ID_".$prefix."orders=$id AND sl_".$prefix."orders_products.Status!='Inactive' ");
	my ($tserv,$tser_disc) = $sth->fetchrow_array();
	
	my ($sth)= &Do_SQL("SELECT SUM(SalePrice),SUM(Discount),SUM(Shipping) FROM sl_".$prefix."orders_products WHERE (ID_products NOT LIKE '4%' OR ID_products NOT LIKE '5%' OR ID_products NOT LIKE '6%') AND ID_".$prefix."orders=$id AND sl_".$prefix."orders_products.Status!='Inactive' ");
	my ($tprod,$tprod_disc,$tprod_shp) = $sth->fetchrow_array();
	return $tserv-$tser_disc+$tprod_shp+int(($tprod-$tprod_disc)*(1+$tax/100)*100+0.9)/100;
}

sub load_ccwpage {
# --------------------------------------------------------
	if (open (my $cfg, "<", "./pages/wpage$sys{'wpage_'.$usr{'application'}}.html")){
		return (join("",<$cfg>));
	}
}

sub load_pricelevels_name {
# --------------------------------------------------------	
# Created on: 2007/10/11 10:02AM
# Author: Rafael Sobrino
# Description : Load a pricelevels name
# Action Taken : (Modified by : Modified on :)

	### pricelevels name
	my ($pricelevels) = "";
	if($in{'id_pricelevels'} > 0){		
		$pricelevels =&load_db_names('sl_pricelevels','ID_pricelevels',$in{'id_pricelevels'},'[Name]');
	}else{
		$pricelevels = '---';
	}	
	return $pricelevels;
}

sub load_station_qa {
# --------------------------------------------------------	
# Created on: 2007/10/11 10:49AM
# Author: Rafael Sobrino
# Description : Load station questions/answers
#
# Modified by :
# Modified on :
# Action Taken :
	
	my ($qa) = "";
	for (1..5){
		$question = !$in{'question'.$_} eq "" ? $in{'question'.$_} : "---";
		$answer =  !$in{'answer'.$_} eq "" ? $in{'answer'.$_} : "---";
		
		if ($question ne "---" and $answer ne "---"){
			$qa .= "<tr>\n".
				"  <td valign='top' width='50%' valign='top'>$question : </td>\n".
				"  <td class='smalltext' valign='top'>$answer</td>\n".
				"</tr>\n";
		}
	}	
	if (!$qa){
		$qa = "<tr><td align='center' colspan='2'>".&trans_txt('no_qa_available')."</td></tr>";		
	}
	return $qa;
}

sub load_images {
# --------------------------------------------------------	
	my ($output,$id);
	## if the product is a set, assign that value to id_products

	if (-e "$cfg{'path_imgman'}/$in{'id_products'}b1.gif"){
		$output = qq|<IFRAME SRC="/cgi-bin/showimages.cgi?id=$in{'id_products'}&e=$in{'e'}" name="rcmd" TITLE="Show Products" width="100%" height="115" FRAMEBORDER="0" MARGINWIDTH="0" MARGINHEIGHT="0" SCROLLING="auto">
			<H2>Unable to do the script</H2>
			<H3>Please update your Browser</H3>
		</IFRAME>|;
	}else{
		$output = "<p align='center'>".&trans_txt('no_imgs_available')."</p>";
	}	
	return $output;
}


sub load_status_image {
# --------------------------------------------------------
	if ($in{'testing'} eq "Approved" and $in{'status'} eq "Active"){
		$va{'testing_image'} = "<img src='[va_imgurl]/[ur_pref_style]/approved.gif' title='$in{'testing'}' alt='$in{'testing'}' border='0'></a><br><span class='help_on'>$in{'testing'}</span>";
	}elsif ($in{'testing'} eq "Rejected"){
		$va{'testing_image'} = "<img src='[va_imgurl]/[ur_pref_style]/rejected.gif' title='$in{'testing'}' alt='$in{'testing'}' border='0'></a><br><span class='help_on'>$in{'testing'}</span>";
	}elsif ($in{testing} eq null){
		$va{'testing_image'} = "";
	}

	if ($in{'status'} eq "Active"){
		$status_image = "active.png";
	}elsif ($in{'status'} eq "Inactive"){
		$status_image = "inactive.png";
	}elsif ($in{'status'} eq "On-Air"){
		$status_image = "on_air.png";
	}elsif ($in{'status'} eq "Testing"){
		$status_image = "testing.png";
	}elsif ($in{'status'} eq "Web Only"){
		$status_image = "web_only.png";
	}elsif ($in{'status'} eq "Up Sell"){
		$status_image = "up-sell.png";
	}elsif ($in{'status'} eq "Pauta Seca"){
		$status_image = "pauta_seca.png";
	}
	
	$va{'status_image'} = "<img src='[va_imgurl]/$status_image' title='$in{'status'}' alt='$in{'status'}' border='0'></a><br><span class='help_on'>$in{'status'}</span>";

}

sub load_webpage{
## --------------------------------------------------------
	my ($url) = @_;
	use LWP::UserAgent;
	use HTTP::Request::Common;
	$ua=new LWP::UserAgent;
	
	# Create a request
	my $req = HTTP::Request->new(GET => "$url");
	# Pass request to the user agent and get a response back
	$resp = $ua->request($req);
	
	if ($resp->is_success){
		return 	$resp->content;
 	}else{
 		return $resp->status_line;
 	} 
}

sub load_regular_shipping {
# --------------------------------------------------------
# Last Modified on: 03/17/09 16:14:22
# Last Modified by: MCC C. Gabriel Varela S: Se cambian los parámetros al llamar a sltv_itemshipping
# Last Modified RB: 12/07/2010  19:06:44 -- Se agregan parametros para calculo de shipping

	my ($id_prod) = @_;
	my ($sth) = &Do_SQL("SELECT sl_products.edt, sl_products.SizeW, sl_products.SizeH, sl_products.SizeL, sl_products.Weight, sl_products.ID_packingopts, sl_products.shipping_table, sl_products.shipping_discount FROM sl_products WHERE ID_products='$id_prod';");	
	my ($rec) = $sth->fetchrow_hashref;
	my ($shptotal1,$shptotal2,$shptotal3,$shptotal1pr,$shptotal2pr,$shptotal3pr,$shp_text1,$shp_text2,$shp_text3,$shp_textpr1,$shp_textpr2,$shp_textpr3) = &sltv_itemshipping($rec->{'edt'},$rec->{'SizeW'},$rec->{'SizeH'},$rec->{'SizeL'},$rec->{'Weight'},$rec->{'ID_packingopts'},$rec->{'shipping_table'},$rec->{'shipping_discount'},$id_prod);
	
	return $shptotal1;
}

#############################################################################
#############################################################################
#   Function: load_po_upcitems
#
#       Es: Lista los items de una orden de compra, con UPC
#       En: List the items of a purchase order, with UPC
#
#
#    Created on: 27/05/2013  10:50:00
#
#    Author: Alejandro Diaz
#
#    Modifications:
#
#
#   Parameters:
#
#      - 
#
#  Returns:
#
#      - Items de un PO, asi como resumen (Descripcion,TOTAL)
#
#   See Also:
#
#
#
sub load_po_upcitems {
# --------------------------------------------------------
	return &load_po_items('upc');
}

#############################################################################
#############################################################################
#   Function: load_po_items
#
#       Es: Lista los items de una orden de compra
#       En: List the items of a purchase order
#
#
#    Created on: 30/01/2013  12:00:00
#
#    Author: Enrique Peña
#
#    Modifications: 27/05/2013 - Alejandro Diaz
#
#
#   Parameters:
#
#      - id_po Id Purcharse Order
#
#  Returns:
#
#      - Items de un PO, asi como resumen (Descripcion,TOTAL)
#
#   See Also:
#
#
#
sub load_po_items{
#############################################################################
#############################################################################	
	my ($list_type) = @_;
	my ($choices,$tot_qty,$tot_po,$subtotal_po,$tax_po,$tax1_po,$tax2_po,$vendor_sku,$line,$name,$cmdlink,$unit,$output);
	$output = "";
	my (@c) = split(/,/,$cfg{'srcolors'});
	my ($sth) = &Do_SQL("SELECT COUNT(*) FROM sl_purchaseorders_items WHERE ID_purchaseorders='$in{'id_purchaseorders'}'");
	if ($sth->fetchrow>0){
		my ($sth) = &Do_SQL("SELECT * FROM sl_purchaseorders_items WHERE ID_purchaseorders='$in{'id_purchaseorders'}' ORDER BY ID_purchaseorders_items DESC;");
		while ($rec = $sth->fetchrow_hashref){
			$d = 1 - $d;
			++$line;
			
			## Choices
			my ($sth2) = &Do_SQL("SELECT * FROM sl_skus WHERE ID_sku_products='$rec->{ID_products}' and Status='Active'");
			$tmp = $sth2->fetchrow_hashref;
			$choices = &load_choices('-',$rec->{'choice1'},$rec->{'choice2'},$rec->{'choice3'},$rec->{'choice4'});
			my $upc = $tmp->{'UPC'};
			
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
			}elsif ($rec->{'ID_products'}  =~ /^6/){
				## Part
				$unit  = "Unit";
				$cmdlink = 'mer_services';
				$name = &load_db_names('sl_services','ID_services',($rec->{ID_products}-600000000),'[Name]');
				$segment_area = &load_db_names('sl_accounts_segments','ID_accounts_segments',($rec->{ID_segments}),'[Name]');
			}

			$subtotal = ($rec->{'Price'}*$rec->{'Qty'});

			if($in{'f'} eq "1" or !$in{'f'}){
				$tot_imp  = (($subtotal*$rec->{'Tax_percent'}) +$subtotal);
				$output .= "<tr bgcolor='$c[$d]'>\n";
				$output .= "   <td class='infot' valign='top'>$line</td>\n";
				$output .= "   <td class='infot' valign='top'> $name</td>\n";
				$output .= "   <td class='infot' valign='top' nowrap>".$upc."</td>";
				$output .= "   <td class='infot' valign='top' nowrap>".($rec->{'ID_products'})."</td>";
				$output .= "   <td class='infot' valign='top'>".&format_number($rec->{'Qty'})."</td>\n";
				$output .= "   <td class='infot' valign='top' nowrap>".&format_number($rec->{'Received'})."</td>\n";
				$output .= "   <td class='infot' valign='top' nowrap>".&format_price($rec->{'Price'})."</td>\n";			
				$output .= "   <td class='infot' align='right' valign='top' nowrap> ".&format_price($subtotal)."</td>\n";
				$output .= "   <td class='infot' align='right' valign='top' nowrap>(".($rec->{'Tax_percent'}*100)."%) ".&format_price($rec->{'Tax'})." </td>\n";
				$output .= "   <td class='infot' align='right' valign='top' nowrap>".&format_price($tot_imp)."</td>\n";
				$output .= "</tr>\n";
				$tot_qty += $rec->{'Qty'};
				$tot_po  += $tot_imp;
			}elsif($in{'f'} eq "4"){
				$output .= "<tr>\n";
				$output .= "   <td class='infot' valign='top'>$line</td>\n";
				$output .= "   <td class='infot' valign='top'> $name</td>\n";
				$output .= "   <td class='infot' valign='top' align='right' nowrap>".&format_number($rec->{'Qty'})."</td>\n";
				$output .= "   <td class='infot' valign='top' align='right' nowrap>".&format_price($rec->{'Price'})."</td>\n";			
				$output .= "   <td class='infot' valign='top' align='right' nowrap> ".&format_price($subtotal)."</td>\n";
				$output .= "</tr>\n";
				$tot_qty += $rec->{'Qty'};
				$tot_po  += $subtotal;				
			}elsif($in{'f'} eq "5"){
				my $this_subtotal = ($rec->{'Total'});
				$output .= "<tr bgcolor='$c[$d]'>\n";
				$output .= "   <td class='infot' valign='top'>$line</td>\n";
				$output .= "   <td class='infot' valign='top'> $name</td>\n";
				$output .= "   <td class='infot' valign='top' nowrap>".($rec->{'ID_products'})."</td>";
				$output .= "   <td class='infot' valign='top'>".$segment_area."</td>";
				$output .= "   <td class='infot' valign='top' align='right' nowrap>".&format_number($rec->{'Qty'})."</td>\n";
				# $output .= "   <td class='infot' valign='top' align='right' nowrap>".&format_number($rec->{'Received'})."</td>\n";
				$output .= "   <td class='infot' valign='top' align='right' nowrap>".&format_price($rec->{'Price'})."</td>\n";			
				$output .= "   <td class='infot' valign='top' align='right' nowrap> ".&format_price($subtotal)."</td>\n";
				$output .= "   <td class='infot' align='right' valign='top' nowrap>(".($rec->{'Tax_percent'}*100)."%) ".&format_price($rec->{'Tax'})." </td>\n";
				$output .= "   <td class='infot' align='right' valign='top' nowrap>(".($rec->{'Tax_withholding_pct'}*100)."%) ".&format_price($rec->{'Tax_withholding'})." </td>\n";
				$output .= "   <td class='infot' align='right' valign='top' nowrap>(".($rec->{'Tax_other_pct'}*100)."%) ".&format_price($rec->{'Tax_other'})." </td>\n";
				$output .= "   <td class='infot' align='right' valign='top' nowrap>".&format_price($this_subtotal)."</td>\n";
				$output .= "</tr>\n";
				$tot_qty += $rec->{'Qty'};

				$tot_po  += $this_subtotal;
				$tax1_po  += $rec->{'Tax_withholding'};
				$tax2_po  += $rec->{'Tax_other'};
			}else{
				$output .= "<tr bgcolor='$c[$d]'>\n";
				$output .= "   <td class='infot' valign='top'>$line</td>\n";
				$output .= "   <td class='infot' valign='top'> $name</td>\n";
				$output .= "   <td class='infot' valign='top' nowrap>".$upc."</td>";
				$output .= "   <td class='infot' valign='top' nowrap>".($rec->{'ID_products'})."</td>";
				$output .= "   <td class='infot' valign='top' align='right' nowrap>".&format_number($rec->{'Qty'})."</td>\n";
				$output .= "   <td class='infot' valign='top' align='right' nowrap>".&format_number($rec->{'Received'})."</td>\n";
				$output .= "   <td class='infot' valign='top' align='right' nowrap>".&format_price($rec->{'Price'})."</td>\n";			
				$output .= "   <td class='infot' valign='top' align='right' nowrap> ".&format_price($subtotal)."</td>\n";
				$output .= "</tr>\n";
				$tot_qty += $rec->{'Qty'};
				$tot_po  += $subtotal;
			}
			$subtotal_po +=$subtotal;
			$tax_po += $rec->{'Tax'};
		}		
		
		if($in{'f'} eq "1" or !$in{'f'}){
			$output .= qq|</table><table border=0 width=100% style="border:1px solid #111111; border-top:0px;"><tr bgcolor=#ffffff>
				<td align=right>
				<table cellpadding=0 cellspacing=5 align=right style="margin-right:0px;" border=0>

				<tr>
				<td valign=top align=right><font class=infot>Subtotal:</td>
				<td valign=top align=right ><font class=info>|.&format_price($subtotal_po).qq|</td>
				</tr>
				<tr>
				<td valign=top align=right><font class=infot>IVA:</td>
				<td valign=top align=right ><font class=info>|.&format_price($tax_po).qq|</td>
				</tr>
				<tr>
				<td valign=top align=right><font class=infot>Total:</td>
				<td valign=top align=right width=90px><font class=info>|.&format_price($tot_po).qq|</td></tr>|;
		}elsif($in{'f'} eq "5" or !$in{'f'}){
			$output .= qq|</table><table border=0 width=100% style="border:1px solid #111111; border-top:0px;"><tr bgcolor=#ffffff>
				<td align=right>
				<table cellpadding=0 cellspacing=5 align=right style="margin-right:0px;" border=0>
				<tr>
					<td valign=top align=right><font class=infot>Subtotal:</td>
					<td valign=top align=right ><font class=info>|.&format_price($subtotal_po).qq|</td>
				</tr>
				<tr>
					<td valign=top align=right><font class=infot>Impuestos Trasladados (IVA) :</td>
					<td valign=top align=right ><font class=info>|.&format_price($tax_po).qq|</td>
				</tr>
				<tr>
					<td valign=top align=right><font class=infot>Impuestos Retenidos ISR :</td>
					<td valign=top align=right ><font class=info>|.&format_price($tax2_po).qq|</td>
				</tr>
				<tr>
					<td valign=top align=right><font class=infot>IVA :</td>
					<td valign=top align=right ><font class=info>|.&format_price($tax1_po).qq|</td>
				</tr>
				<tr>
					<td valign=top align=right><font class=infot>Total:</td>
					<td valign=top align=right width=90px><font class=info>|.&format_price($tot_po).qq|</td>
				</tr>|;
		}else{
			$output .= qq|</table>
			<table border=0 width=100% style="border:1px solid #111111; border-top:0px;"><tr bgcolor=#ffffff>
				<td align=right>
				<table cellpadding=0 cellspacing=5 align=right style="margin-right:0px;" border=0>
				<td valign=top align=right><font class=infot>Total:</td>
				<td valign=top align=right width=90px><font class=info>|.&format_price($tot_po).qq|</td></tr>|;
		}		
	}else{
		$output = qq| <tr>
					<td colspan='7' align="center">|.&trans_txt('search_nomatches').qq|</td>
				    </tr>\n|;
	}

	return $output;
}


#########################################################################################################
#########################################################################################################
#
#	Function: load_customer_addres_code
#   		Imprime el codigo y alias de la tienda
#
#	Created by:
#		_Roberto Barcenas_
#
#	Modified By:
#	
#   	Parameters:
#					id_customers_addresses
#
#   	Returns:
#		None
#
#   	See Also:
#
sub load_customer_addres_code {
#########################################################################################################
#########################################################################################################

	my ($sth) = &Do_SQL("SELECT CONCAT(Code,' - ',Alias) FROM cu_customers_addresses WHERE ID_customers_addresses = '$in{'id_customers_addresses'}';");
	my ($output) = $sth->fetchrow();
	$output .= qq|<br>| if $output;
	$output .= qq|$in{'shp_name'}<br>| if $in{'shp_name'};
	return $output;

}


#########################################################################################################
#########################################################################################################
#
#	Function: load_shplabel_info
#   		Carga variables para el formato de shipping label de ordenes en remesa
#
#	Created by:
#		_Roberto Barcenas_
#
#	Modified By: 24092014::AD::Se elimina filtro 'Inactive' en linea 2278
#	
#   	Parameters:
#					id_customers_addresses
#
#   	Returns:
#		None
#
#   	See Also:
#
sub load_shplabel_info {
#########################################################################################################
#########################################################################################################

	my $tot_shp = 0; my $tot_tax = 0; my $tot_dis = 0; my $tot_net = 0; my $tot_ord = 0; my $output;

	$va{'e_prefix'} = $cfg{'prefixentershipment'};
	$in{'id_warehouses'} = &load_name('sl_warehouses_batches','ID_warehouses_batches',$in{'id_warehouses_batches'},'ID_warehouses');
	$va{'batch_date'} = &load_name('sl_warehouses_batches','ID_warehouses_batches',$in{'id_warehouses_batches'},'date');

	my ($sth) = &Do_SQL("SELECT COUNT(*) FROM sl_orders_products INNER JOIN sl_warehouses_batches_orders USING(ID_orders_products)
						WHERE ID_orders='$in{'id_orders'}' AND ID_warehouses_batches = '$in{'id_warehouses_batches'}' 
						AND sl_orders_products.Status NOT IN('Order Cancelled')
						AND sl_warehouses_batches_orders.Status NOT IN ('Cancelled','Error');");
	$va{'matches'} = $sth->fetchrow;

	if ($va{'matches'}>0){

		my ($stht) = &Do_SQL("SELECT COUNT(DISTINCT ID_warehouses_batches) -1 FROM sl_orders_products 
							INNER JOIN sl_warehouses_batches_orders USING(ID_orders_products)
							WHERE ID_orders='$in{'id_orders'}' 
							AND sl_orders_products.Status NOT IN('Order Cancelled')
							AND sl_warehouses_batches_orders.id_warehouses_batches <= '$in{'id_warehouses_batches'}'
							/*WHERE ID_orders='$in{'id_orders'}' AND sl_orders_products.Status NOT IN('Order Cancelled', 'Inactive')
							AND sl_warehouses_batches_orders.Status NOT IN ('Cancelled','Error')*/;");

		my ($t) = $stht->fetchrow();
		$t = 0 if $t < 0;
		$va{'tracking'} = $in{'id_orders'} . $t;


		my ($sthc) = &Do_SQL("SELECT Phone1,Phone2, Cellphone FROM sl_orders INNER JOIN sl_customers USING(ID_customers) WHERE ID_orders = '$in{'id_orders'}';");
		my ($p1,$p2,$p3) = $sthc->fetchrow();
		$va{'phone'} = $p1;
		($p2) and ($va{'phone'} .= qq| / $p2 |);
		($p3) and ($va{'phone'} .= qq| / $p3 |);

		my ($sth1) = &Do_SQL("SELECT * FROM sl_orders_products INNER JOIN sl_warehouses_batches_orders USING(ID_orders_products)
						WHERE ID_orders='$in{'id_orders'}' AND ID_warehouses_batches = '$in{'id_warehouses_batches'}' 
						AND sl_orders_products.Status NOT IN('Order Cancelled')
						AND sl_warehouses_batches_orders.Status NOT IN ('Cancelled','Error');");

		my ($col);
		my $x = 0;
		while ($col = $sth1->fetchrow_hashref){

			++$x;
			$in{'admin_users'} = $col->{'ID_admin_users'};
			$output .= "<tr>";

			my $refill_mark='';
			$d = 1 - $d;
			my ($sthk) = &Do_SQL("SELECT * FROM sl_skus WHERE ID_sku_products='$col->{'$id_products'}' and Status='Active'");
			$rec = $sthk->fetchrow_hashref;

			if($col->{$id_products}>600000000){
				### Services in Order
				(&load_name('sl_services','ID_services',$col->{$id_products}-600000000,'ServiceType') eq 'Refill') and ($is_refill = 1) and ($refill_mark = ' <strong>**</strong> ');
				$output .= "   <td width=60px valign=top align=left class='line'><font class='line'>".$col->{'ID_products'}."&nbsp;</td>\n";
				$output .= "   <td width=145px valign=top align=left class='line'><font class='line'>".&load_name('sl_services','ID_services',$col->{'ID_products'}-600000000,'Name')." $refill_mark</td>\n";
			}else{
				### Products in Order
				$output .= "   <td width=60px valign=top align=left class='line'><font class='line'>".$col->{'ID_products'}."&nbsp;</td>\n";
				

				if(&is_exportation_order($in{'id_orders'}) or $query ne ''){
					$tmp{'name'}=&load_name('sl_parts','ID_parts',$col->{'ID_products'}-400000000,'Name');
				}else{
					$tmp{'name'}=&load_name('sl_products','ID_products',substr($col->{'ID_products'},-6),'Name');
				}

				$tmp{'name'} = &replace_in_string($tmp{'name'});

				$output .= "   <td width=140px valign=top align=left class='line'><font class='line'>$tmp{'name'}</td>\n";
								
			}
		
			$output .= "   <td width=62px valign=top align=right nowrap class='line'><font class='line'>".&format_price( ($col->{'SalePrice'} + $col->{'ShpTax'}) / $col->{'Quantity'})."</td>\n";
			$output .= "   <td width=20px valign=top align=center nowrap class='line'><font class='line'>".$col->{'Quantity'}."</td>\n";
			$output .= "   <td width=63px valign=top align=right nowrap class='line'><font class='line'>".&format_price($col->{'SalePrice'} + $col->{'ShpTax'})."</td>\n";
			$output .= "</tr>\n";

			$tot_shp += $col->{'Shipping'};
			$tot_dis += $col->{'Discount'};
			$tot_tax += round($col->{'Tax'} + $col->{'ShpTax'});
			$tot_net += $col->{'SalePrice'};
			$tot_ord += $col->{'SalePrice'} + $col->{'Shipping'} + $col->{'Tax'} + $col->{'ShpTax'} - $col->{'Discount'};
			

		}

		for($x..4){
			$output .= qq|<tr><td width=60px valign=top align=left class='line'><font class='line'>&nbsp;</td>|;
			$output .= qq|<td width=145px valign=top align=left class='line'><font class='line'>&nbsp;</td>|;
			$output .= qq|<td width=55px valign=top align=left class='line'><font class='line'>&nbsp;</td>|;
			$output .= qq|<td width=30px valign=top align=left class='line'><font class='line'>&nbsp;</td>|;
			$output .= qq|<td width=55px valign=top align=left class='line'><font class='line'>&nbsp;</td></tr>|;

		}
		$va{'searchresults'} = $output;


	}else{
		$va{'searchresults'} = qq|<tr><td colspan="5">|.&trans_txt('search_nomatches').qq|</td></tr>|;
	}
		### Orders Totals
		
		$va{'customers_atime'} = $in{'customers.atime'};
		$va{'tot_net'} = &format_price($tot_net);
		$va{'tot_shp'} = &format_price($tot_shp);
		$va{'tot_dis'} = &format_price($tot_dis);
		$va{'tot_tax'} = &format_price($tot_tax);
		$va{'tot_ord'} = &format_price($tot_net + $tot_tax + $tot_shp - $tot_dis);
		return;

}


#########################################################################################################
#########################################################################################################
#
#	Function: load_bill_amt_negative
#
#   	Es:	Devuelve la suma de los montos negativos del Bill
#
#	Created by:
#		_Roberto Barcenas_
#
#	Modified By:
#	
#   	Parameters:
#					id_bills, tbl
#
#   	Returns:
#		None
#
#   	See Also:
#
sub load_bill_amt_negative {
#########################################################################################################
#########################################################################################################


	my ($id_bills, $tbl) = @_;

	my $sth = &Do_SQL("SELECT 
						SUM(ABS(Amount))
						FROM $tbl WHERE ID_bills = '". $id_bills ."'
						AND Amount < 0;");
	my ($amt) = $sth->fetchrow();
	(!$amt) and ($amt = 0);

	return $amt;

}

#########################################################################################################
#########################################################################################################
#
#	Function: load_invoice_products_pos
#
#   	Es:	Devuelve el listado de productos contenidos en la orden
#
#	Created by:
#		ISC Alejandro Diaz
#
#	Modified By:
#	
#   	Parameters:
#
#
#   	Returns:
#		None
#
#   	See Also:
#
sub load_invoice_products_pos{
#########################################################################################################
#########################################################################################################

	my ($style,$output,$tot_qty,$tot_ord,$choices,$prefix,$id_products);
	my ($query)='';
	
	$prefix="Related_"if(&is_exportation_order($in{'id_orders'}));
	$id_products=$prefix."ID_products";

	if ($in{'toprint'}){
		$style = 'stdtext';
	}else{
		$style = 'smalltext';
	}

	$query = " AND ID_products  =  $in{'id_products'} "  if ($in{'id_products'} and  length($in{'id_products'})	== 9 and substr($in{'id_products'},0,1)==4);

	my ($sth) = &Do_SQL("SELECT COUNT(*) FROM sl_orders_products WHERE ID_orders='$in{'id_orders'}' AND Status NOT IN('Order Cancelled', 'Inactive') $query");
	$va{'matches'} = $sth->fetchrow;
	if ($va{'matches'}>0){
		my $is_refill=0;
		my ($sth1) = &Do_SQL("SELECT * FROM sl_orders_products WHERE ID_orders='$in{'id_orders'}' AND Status NOT IN('Order Cancelled', 'Inactive') $query ORDER BY ID_orders_products");
		my ($col);
		while ($col = $sth1->fetchrow_hashref){

			$output .= "<tr>";


			my $refill_mark='';
			$d = 1 - $d;
			# 10-09-2013::AD: Se elimina filtro and Status='Active'
			my ($sthk) = &Do_SQL("SELECT * FROM sl_skus WHERE ID_sku_products='$col->{'$id_products'}' ");
			$rec = $sthk->fetchrow_hashref;

			$output .= "   <td width=90px valign=top align=left><font class=detalles>$col->{'Quantity'}&nbsp;";
			if ($col->{$id_products} < 5000){
				### Services in Order
				$output .= "   <td width=90px valign=top align=left><font class=detalles>$col->{'$id_products'}&nbsp;</td>\n";
				#GV Modifica 21abr2008 Se cambia sl_services por sl_services #GV Modifica 21abr2008 Se cambia ID_services por ID_services
				$output .= "   <td width=350px valign=top align=left><font class=detalles>".&load_name('sl_services','ID_services',$col->{$id_products},'Name')."</td>\n";
			}elsif($col->{$id_products}>600000000){
				### Services in Order
				(&load_name('sl_services','ID_services',$col->{$id_products}-600000000,'ServiceType') eq 'Refill') and ($is_refill = 1) and ($refill_mark = ' <strong>**</strong> ');
				$output .= "   <td width=90px valign=top align=left><font class=detalles>".&format_sltvid($col->{$id_products})."&nbsp;</td>\n";
				$output .= "   <td width=350px valign=top align=left><font class=detalles>".&load_name('sl_services','ID_services',$col->{$id_products}-600000000,'Name')." $refill_mark</td>\n";
			}else{
				### Products in Order

				$output .= "   <td width=90px valign=top align=left><font class=detalles>".&format_sltvid($col->{$id_products})."&nbsp;</td>\n";
				($col->{'SerialNumber'}) and ($col->{'SerialNumber'} = "<br>$col->{'SerialNumber'}");
				($status,%tmp) = &load_product_info($col->{$id_products});

				if(&is_exportation_order($in{'id_orders'}) or $query ne '')
				{
					$tmp{'model'}=&load_name('sl_parts','ID_parts',$col->{$id_products}-400000000,'Model');
					$tmp{'name'}=&load_name('sl_parts','ID_parts',$col->{$id_products}-400000000,'Name');
				}

				$tmp{'model'} = &replace_in_string($tmp{'model'});
				$tmp{'name'} = &replace_in_string($tmp{'name'});

				if ($in{'print_upc'}){

					$output .= "   <td width=350px valign=top align=left><font class=detalles>$tmp{'model'} ".
								"<span class='smalltext'>".&load_parts_upc($col->{$id_products})."</span>".
								" $col->{'SerialNumber'} ".&build_tracking_link($col->{'Tracking'},$col->{'ShpProvider'},$col->{'ShpDate'},$col->{$id_products})."</td>\n";
				}else{

					$output .= "   <td width=350px valign=top align=left><font class=detalles>$tmp{'model'} ".
								"<span class='smalltext'>".&load_parts($col->{$id_products})."</span>".
								" $col->{'SerialNumber'} ".&build_tracking_link($col->{'Tracking'},$col->{'ShpProvider'},$col->{'ShpDate'},$col->{$id_products})."</td>\n";
				}

			}

			if(&is_exportation_order($in{'id_orders'})){
				# $output .= "   <td width=65px valign=top align=right><font class=detalles>".&format_price($col->{'SalePrice'} / $col->{'Quantity'})."</td>\n";
				$output .= "   <td width=65px valign=top align=right><font class=detalles>".&format_price($col->{'SalePrice'})."</td>\n"	if $col->{'SalePrice'} > 0;
				$output .= "   <td width=65px valign=top align=right nowrap><font class=detalles>".&format_price($col->{'SalePrice'}*-1)."</td>\n"	if $col->{'SalePrice'} < 0;
				$tot_ord +=$col->{'SalePrice'}if $col->{'SalePrice'} >0;
				$tot_ord -= $col->{'SalePrice'}if $col->{'SalePrice'} <0;
			}else{
				$output .= "   <td width=65px valign=top align=right nowrap><font class=detalles>".&format_price($col->{'SalePrice'})."</td>\n";
				$output .= "   <td width=65px valign=top align=right nowrap><font class=detalles>".&format_price($col->{'SalePrice'}*$col->{'Quantity'})."</td>\n"	if $col->{'SalePrice'} > 0;
				$output .= "   <td width=65px valign=top align=right nowrap><font class=detalles>".&format_price($col->{'SalePrice'}*$col->{'Quantity'}*-1)."</td>\n"	if $col->{'SalePrice'} < 0;
				$tot_ord +=$col->{'SalePrice'}*$col->{'Quantity'} if $col->{'SalePrice'} >0;
				$tot_ord -= $col->{'SalePrice'}*$col->{'Quantity'} if $col->{'SalePrice'} <0;
			}

			$output .= "</tr>\n";
			$tot_qty += $col->{'Quantity'};

		}
		### Orders Totals
		$va{'total_order'} = &format_price(&total_orders_products($in{'id_orders'}));
		$va{'ordernet'} = &format_price(&products_sum_in_order($in{'id_orders'}, "SalePrice"));
		$va{'ordershp'} = &format_price(&products_sum_in_order($in{'id_orders'}, "Shipping"));
		$va{'orderdisc'} = &format_price(&products_sum_in_order($in{'id_orders'}, "Discount"));
		$taxes = &products_sum_in_order($in{'id_orders'}, "Tax");
		$va{'total_taxes'} = &format_price($taxes);

		$va{'tax'} = $in{'ordertax'}*100;
		$va{'ordertax'} = &format_number($in{'ordertax'}*100);

		my $refill_txt='';
		if($is_refill){
			$refill_txt .= qq|
				    &nbsp;<tr>
					    <td colspan='5'>
						 <strong>|.&trans_txt('refill_disclaimer_title').qq|</strong><br>
						 |.&trans_txt('refill_disclaimer_desc').qq|
					    </td>
				    </tr>&nbsp;|;

		}

		## Coupons?
		my $add_coupon = '';
		if($cfg{'coupons'} and $in{'ordernet'} >= $cfg{'coupons_mindireksys'}){

			$result = &get_coupon_external('sl_orders',$in{'id_orders'});

			if($result > 0){
				$add_coupon = qq|[ip_forms:coupons_external_view]|;
			}
		}

		$va{'extra_output'} .= qq|
			$refill_txt
			<tr>
				<td align="left" class="smalltext">[fc_load_invoice_data]</td>
			</tr>|;

		if(!&is_adm_order($in{'id_orders'})){
			$va{'extra_output'} .= qq|
				<tr>
					<td align="left" class="smalltext"><p>&nbsp;</p>&nbsp;</td>
				</tr>|;

			$va{'extra_output'} .= qq|
				<tr>
					<td align="left" class="smalltext"><p>$add_coupon</p>&nbsp;</td>
				</tr>| if $add_coupon;
		}

	}else{
		$output = qq|
			<tr>
				<td colspan='5' align="center">|.&trans_txt('search_nomatches').qq|</td>
			</tr>\n|;
	}

	&load_cfg('sl_orders');	
	return $output;
}

###############################################################################
#   Function: load_last_purchase_cost
#
#       Es: Costo de ultima compra de un SKU
#       En: Cost in last purchase
#
#   Created by:
#       ISC Alejandro DIAZ::10-09-2015
#
#   Modified By:
#   	
#
#   Parameters:
#
#       ID_products
#
#   Returns:
#   
#   	Cost
#
sub load_last_purchase_cost {
###############################################################################

    my ($id_products, $id_purchaseorders) = @_;
    my ($cost, $cost_adj, $cost_add);

    if ($id_products){
    	my $add_sql = ($id_purchaseorders)? " AND sl_wreceipts.ID_purchaseorders = '".$id_purchaseorders."' ":"";

    	if ($id_purchaseorders){
    		$sql = "SELECT sl_skus_trans.Cost, Cost_Adj, Cost_Add
			FROM sl_skus_trans
			LEFT JOIN sl_wreceipts_items ON sl_wreceipts_items.ID_wreceipts=sl_skus_trans.ID_trs AND sl_wreceipts_items.ID_products=sl_skus_trans.ID_products
			LEFT JOIN sl_wreceipts ON sl_wreceipts.ID_wreceipts=sl_wreceipts_items.ID_wreceipts
			WHERE sl_skus_trans.ID_products = '".$id_products."'
			$add_sql
			ORDER BY sl_skus_trans.Date DESC, sl_skus_trans.Time DESC, sl_skus_trans.ID_products_trans DESC
			LIMIT 1";
			my $sth = &Do_SQL($sql);
			($cost, $cost_adj, $cost_add) = $sth->fetchrow_array();
    	}else{
    		## Costo de ultimpo Implode
			$sql = "SELECT sl_skus_trans.Cost, Cost_Adj, Cost_Add
			FROM sl_skus_trans
			INNER JOIN sl_parts_productions ON sl_parts_productions.ID_parts_productions=sl_skus_trans.ID_trs
			WHERE sl_skus_trans.ID_products = '".$id_products."'
			AND sl_skus_trans.tbl_name = 'sl_parts_productions' 
			AND sl_skus_trans.Type = 'Production' 
			AND sl_skus_trans.Type_trans = 'IN'
			AND sl_parts_productions.Type='Implode'
			ORDER BY sl_skus_trans.Date DESC, sl_skus_trans.Time DESC, sl_skus_trans.ID_products_trans DESC
			LIMIT 1";
			my $sth = &Do_SQL($sql);
			($cost, $cost_adj, $cost_add) = $sth->fetchrow_array();
			
			if ($cost <= 0){
				## Costo de ultima recepcion
				$sql = "SELECT sl_skus_trans.Cost, Cost_Adj, Cost_Add
				FROM sl_skus_trans
				LEFT JOIN sl_wreceipts_items ON sl_wreceipts_items.ID_wreceipts=sl_skus_trans.ID_trs AND sl_wreceipts_items.ID_products=sl_skus_trans.ID_products
				LEFT JOIN sl_wreceipts ON sl_wreceipts.ID_wreceipts=sl_wreceipts_items.ID_wreceipts
				WHERE sl_skus_trans.ID_products = '".$id_products."'
				ORDER BY sl_skus_trans.Date DESC, sl_skus_trans.Time DESC, sl_skus_trans.ID_products_trans DESC
				LIMIT 1";
				my $sth = &Do_SQL($sql);
				($cost, $cost_adj, $cost_add) = $sth->fetchrow_array();
			}
    	}

    }

    return ($cost, $cost_adj, $cost_add);

}

1;