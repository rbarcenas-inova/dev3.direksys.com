##########################################################
##		MERCHANDISING  :  PRODUCTS  		  ##
##########################################################
sub presearch_mer_products {
# --------------------------------------------------------
	$in{'id_products'} =~ s/\D//g;
}

sub preadvsearch_mer_products {
# --------------------------------------------------------
	$in{'id_products'} =~ s/\D//g;
	$in{'sl_products.id_products'} =~ s/\D//g;
}

sub loaddefault_mer_products {
# --------------------------------------------------------
	#$in{'status'} = 'Inactive';
	$in{'status'} = 'Testing';
	$in{'pricetype'} = 'Gross';
}

sub loading_mer_products{
# --------------------------------------------------------
	$in{'id_products_code'} = &format_sltvid($in{'id_products'});
	$in{'landedcost'} = $in{'sltv_netcost'} +  $in{'wholesalepriceorigin'};
	$in{'margin'} = ($in{'sprice'} > 0)?($in{'sprice'} - $in{'landedcost'}) / $in{'sprice'}:0;
	$in{'margin'} = sprintf("%.2f", $in{'margin'});	
	$in{'margin'} = $in{'margin'}* 100.00;	
	my $id_product_service = &Do_SQL(qq|SELECT CONCAT(cu_products_services.ID_product_service, ' - ', cu_products_services.description ) product
		FROM cu_relations_products
		INNER JOIN cu_products_services on cu_products_services.ID_product_service = cu_relations_products.ID_products_services
		WHERE 1
			AND id_table = $in{'modify'}
			AND `table` = 'sl_products'|)->fetchrow();
	$in{'id_product_service'} = $id_product_service;

	$va{'products_services'} = &build_page('products_chosen.html');
}



sub add_mer_products {
# --------------------------------------------------------
# Forms Involved: 
# Created on: 1/1/2007 9:43AM
# Last Modified on:
# Last Modified by:
# Author: Carlos Haas
# Description : This sub add 100 before id_product into sl_skus table
#								Example id_product 123456 = 100123456 in id_sku_products each time 
#								the product is being creating in sl_products
# Parameters : 
# Last Modification by JRG : 03/11/2009 : Se agrega log

	my ($sth) = &Do_SQL("INSERT INTO sl_skus SET ID_sku_products='100$in{'id_products'}',ID_products='$in{'id_products'}',Status='Active',Date=Curdate(),Time=NOW(),ID_admin_users='$usr{'id_admin_users'}';");
	&auth_logging('sku_added',$sth->{'mysql_insertid'});

	$in{'id_product_service'} =~ s/\D//g;
	&Do_SQL("INSERT INTO cu_relations_products (`id_table`, `table`, `ID_products_services`) VALUES ( $in{'id_products'}, 'sl_products', '$in{'id_product_service'}')");
}

sub view_mer_products {
# --------------------------------------------------------
# Forms Involved: products_view.html
# Created on:
# Last Modified on: 7/7/2008 6:16:08 PM
# Last Modified by: CH
# Author: CH
# Description : 
# Last Modification by JRG : 03/10/2009 : Se agrega log
# Last Modified on: 03/17/09 16:44:36
# Last Modified by: MCC C. Gabriel Varela S: par�metros para sltv_itemshipping
# Last Modification by RB on 04/22/2010 : Solo developers pueden cambiar a Web Only
# Last Modification by PH on 02/16/2012 : Correo de notificaci�n cuando se actualiza a On-Air|Web Only

    $in{'id_products_code'} = &format_sltvid($in{'id_products'});
	if ($in{'update'}){
		$in{'speech'} =~ s/\n//g;
		my ($sth) = &Do_SQL("UPDATE sl_products SET $in{'field_name'}='".&filter_values($in{'speech'})."' WHERE ID_products=$in{'id_products'};");
		$in{$in{'field_name'}} = $in{'speech'};
		&auth_logging('mer_products_updated',$in{'id_products'});
	}	
	if ($in{'field'}){		
		&load_descriptions;
		$va{'activeIndex'} = '2';
	}else{
		&load_links;
	}

	### Testing
	$va{'edit_product_sale'} = &check_permissions('edit_product_sale','','') ? '' : 'disabled="disabled"';
	my ($error_message);


	if ($in{'action'}) { 


		if($in{'tab'} eq '4'){

			############################
			############################
			############################
			####### Tab4: Prices Configuration 
			############################
			############################
			############################


			if($in{'add_new'}) {

				############################
				#### New Price - Add
				############################
				
				if ( !$in{'new_price'} or !$in{'new_name'}  or !$in{'new_paytype'} ){

					$va{'tabmessages'} = &trans_txt('reqfields');
					

				}else{
					if ($in{'status'} ne 'On-Air' and $in{'status'} ne 'Pauta Seca') {
						my $name = &filter_values($in{'new_name'});
						my $fp = int($in{'new_fp'}) > 0 ? int($in{'new_fp'}) : 1;
						my $ptype = &filter_values($in{'new_paytype'});
						my $auth = $in{'new_auth'} ? &filter_values($in{'new_auth'}) : '';
						my $price = &filter_values($in{'new_price'});
						my $originalprice = &filter_values($in{'new_originalprice'});
						my $downpayment = &filter_values($in{'new_dp'});
						my $validkits = &filter_values($in{'validkits'});
						$price =~ s/\$|,//g;
						$downpayment =~ s/\$|,//g;
						my $modauth = $auth ne '' ? 'Yes' : 'No';
						my $add_sql = ($in{'id_salesorigins'} ne '')? ", Origins='|$in{'id_salesorigins'}|'":"";

						my $query = "INSERT IGNORE INTO sl_products_prices SET ID_products = '$in{'id_products'}', Name = '$name', Price = '$price', OriginalPrice = '$originalprice', Downpayment = '$downpayment', AuthCode = '$modauth', PayType = '$ptype', ValidKits='$validkits', FP = '$fp' $add_sql, belongsto='$in{'belongsto'}', Status = 'Active', Date = CURDATE(), Time = CURTIME(), ID_admin_users = '$usr{'id_admin_users'}';";
						my ($sth) = &Do_SQL($query);
						my ($t) = $sth->rows();

						if($t){

							$va{'tabmessages'} = &trans_txt('mer_products_price_added');
							$va{'message_good'} = &trans_txt('mer_products_price_added');
							&auth_logging('mer_products_price_added',$in{'id_products'});

						}
					} else {
						$va{'tabmessages'} = &trans_txt('mer_products_error_price');
						$va{'message_error'} = &trans_txt('mer_products_error_price');
					}

				}

			}elsif($in{'drop'}){


				############################
				#### New Price - Drop
				############################

				my $idpp = int($in{'drop'});

				if ( !$idpp ){

					$va{'tabmessages'} = &trans_txt('reqfields');
				
				}else{
					if ($in{'status'} ne 'On-Air' and $in{'status'} ne 'Pauta Seca') {
						my $query = "DELETE FROM sl_products_prices WHERE ID_products_prices = '$idpp' ;";
						my ($sth) = &Do_SQL($query);
						my ($t) = $sth->rows();

						if($t){

							$va{'tabmessages'} = &trans_txt('mer_products_price_dropped');
							$va{'message_good'} = &trans_txt('mer_products_price_dropped');
							&auth_logging($va{'tabmessages'}.' '.$idpp, $in{'id_products'});

						}
					} else {
						$va{'tabmessages'} = &trans_txt('mer_products_error_price');
						$va{'message_error'} = &trans_txt('mer_products_error_price');
					}

				}

			}

		}elsif($in{'tab'} eq '5' ){


			############################
			############################
			############################
			####### Tab5: Testing/Auth Product
			############################
			############################
			############################

			if ((!$in{'notes'} or !$in{'notestype'}) and !$in{'edit'}){
				$va{'tabmessages'} = &trans_txt('reqfields');
			}else{
				$va{'tabmessages'} = &trans_txt('mer_products_testadded');
				my ($sth) = &Do_SQL("INSERT INTO sl_products_tests SET id_products='$in{'id_products'}',Notes='".&filter_values($in{'notes'})."',Type='$in{'notestype'}',Date=Curdate(),Time=NOW(),ID_admin_users='$usr{'id_admin_users'}'");
				&auth_logging('mer_products_testadded',$in{'id_products'});	
				if ($in{'finaldec'} and &check_permissions('edit_product_sale','','')){

					if ($in{'notestype'} eq 'Passed'){

						###################
						###################
						## Product Approved
						###################
						###################

						my $err=0;
						my $error_message="";

						#####
						##### SKU Validation
						#####
						## Load Promo
						my ($sth) = &Do_SQL("SELECT VValue FROM sl_vars WHERE VName='promo$in{'id_products'}';");
						$cfg{'promo'.$in{'id_products'}} = $sth->fetchrow;
						if (!$cfg{'promo'.$in{'id_products'}}){
							my ($sth) = &Do_SQL("SELECT ID_sku_products FROM sl_skus WHERE ID_products = '$in{'id_products'}' AND Status != 'Inactive';");
							if($sth->rows == 0){
									$error_message = &trans_txt('invalid') . "ID Product: $in{'id_products'} Without SKU<br>";
									$err++;
							}else{
								while(my($idsku) = $sth->fetchrow()){
										my ($sth) = &Do_SQL("SELECT COUNT(*) FROM sl_skus_parts WHERE ID_sku_products = '$idsku';");
										if($sth->fetchrow() <= 0){
											$err++;
											$error_message .= "SKU:$idsku Without Part assigned<br>";
										}
								}
							}
						}

						######
						###### Category Validation
						######
						my ($sth) = &Do_SQL("SELECT COUNT(*) FROM sl_products_categories WHERE ID_products = '$in{'id_products'}';");
						if($sth->fetchrow() == 0){
							$error_message .= &trans_txt('mer_products_uncategorized');
							$err++;
						}

						######
						###### Price Validation
						######
						my ($sth) = &Do_SQL("SELECT COUNT(*) FROM sl_products_prices WHERE ID_products = '$in{'id_products'}';");
						if($sth->fetchrow() == 0){
							$error_message .= &trans_txt('mer_products_unpriced');
							$err++;
						}						


						if(!$err){
								my ($sth) = &Do_SQL("UPDATE sl_products SET Testing='Approved',Status='Active',Testing_AuthBy='$usr{'id_admin_users'}' WHERE ID_products='$in{'id_products'}'");
								$in{'status'} = 'Active';
						}else{
								my ($sth) = &Do_SQL("INSERT INTO sl_products_tests SET id_products='$in{'id_products'}',Notes='".$error_message. ". The Products Was Not Activated',Type='Failed',Date=CURDATE(),Time=CURTIME(),ID_admin_users='$usr{'id_admin_users'}'");
						}
						
					}else{
						my ($sth) = &Do_SQL("UPDATE sl_products SET Testing='Rejected',Status='Inactive',Testing_AuthBy='$usr{'id_admin_users'}' WHERE ID_products='$in{'id_products'}'");
					}
					$in{'testing_authby'} = $usr{'id_admin_users'};
					&auth_logging('mer_products_test_auth_final',$in{'id_products'});
					$in{'tabs'} = 1;
				}
				delete($in{'notes'});
				delete($in{'notestype'});
			}

		}

	
	}


	### Status Management
	if ($in{'chgstatus'} and &check_permissions('edit_product_status','','')) {

		my ($sth) = &Do_SQL("SELECT Status, Name FROM sl_products  WHERE ID_products=$in{'id_products'};");
		while ($rec = $sth->fetchrow_hashref){
			$status = $rec->{'Status'};
			$name = $rec->{'Name'};
		}
			
		### send email notification
		if (($in{'status'} eq "On-Air" and $in{'web_available'} eq "yes") or $in{'status'} eq "Web Only"){
				my ($sth) = &Do_SQL("SELECT COUNT(ID_products_w) FROM sl_products_w  where ID_products='$in{'id_products'}';");
				$webavailable =$sth->fetchrow;
				if($webavailable){
					$subject = "Warning: Ecommerce Product";
					$body    = "El producto $in{'id_products'} $name paso del Status anterior $status al Status nuevo $in{'chgstatus'}";
					&send_mail("sales\@innovagroupusa.com","rbarcenas\@inovaus.com",$subject,$body);
				}
		}
		
		my ($sth) = &Do_SQL("UPDATE sl_products SET Status='$in{'chgstatus'}' WHERE ID_products=$in{'id_products'};");			
		&auth_logging('mer_products_updated',$in{'id_products'});
		$in{'status'} = $in{'chgstatus'};
		
		### record change status event in log file
		if ($in{'status'} eq "On-Air"){
			&auth_logging('mer_products_statuschg_onair',$in{'id_products'});
		}elsif ($in{'chgstatus'} eq "Active"){
			&auth_logging('mer_products_statuschg_active',$in{'id_products'});
		}elsif ($in{'chgstatus'} eq "Inactive"){
			&auth_logging('mer_products_statuschg_inactive',$in{'id_products'});
		}elsif ($in{'chgstatus'} eq "Web Only"){
			&auth_logging('mer_products_statuschg_webonly',$in{'id_products'});
		}elsif ($in{'chgstatus'} eq "Up Sell"){
			&auth_logging('mer_products_statuschg_upsell',$in{'id_products'});
		}
	}

	if ($in{'status'} ne 'Testing'){

		my(@ary) = ($cfg{'pauta_seca_enabled'} and $cfg{'pauta_seca_enabled'} == 1)? ('On-Air', 'Web Only','Up Sell', 'Active', 'Inactive','Pauta Seca') : ('On-Air', 'Web Only','Up Sell', 'Active', 'Inactive');

		for (0..$#ary){
			if ($in{'status'} ne $ary[$_]){
				if($ary[$_] eq 'Web Only' and &check_permissions('edit_product_ecommerce','','')){
					$va{'changestatus'} .= qq|<a href="/cgi-bin/mod/$usr{'application'}/dbman?cmd=mer_products&view=$in{'id_products'}&chgstatus=$ary[$_]&tab=$in{'tab'}">$ary[$_]</a> : |;
				}elsif($ary[$_] ne 'Web Only'){
					$va{'changestatus'} .= qq|<a href="/cgi-bin/mod/$usr{'application'}/dbman?cmd=mer_products&view=$in{'id_products'}&chgstatus=$ary[$_]&tab=$in{'tab'}">$ary[$_]</a> : |;
				}
			}
		}
		$va{'changestatus'} = substr($va{'changestatus'},0,-2);
	}else {
		$va{changestatus} = " &nbsp; ---";
	}
	
	if (!$in{'testing_authby'}){
		$va{'authby'} = "---";
	}else{
		$va{'authby'} = "($in{'testing_authby'}) ". &load_db_names('admin_users','ID_admin_users',$in{'testing_authby'},'[Firstname] [Lastname]');
	}

	if(!$in{testing}){
		$in{testing} = " &nbsp; &nbsp; ---";
	}
	
	### Brands
	if ($in{'id_brands'}){
		$in{'brands_name'} = &load_name('sl_brands','ID_brands',$in{'id_brands'},'Name');
	}else{
		$in{'id_brands'} = '---';
	}
	
	$in{'landedcost'} = $in{'sltv_netcost'} +  $in{'wholesalepriceorigin'};
	
	if ($in{'sprice'}>0){
		$in{'margin'} = ($in{'sprice'} - $in{'landedcost'}) / $in{'sprice'};
	}else{
		$in{'margin'} = 0;
	}
	$in{'margin'} = $in{'margin'} * 100.00;	
	$in{'margin'} = sprintf("%2.2f", $in{'margin'});	
	
	
	$in{'landedcost'} =  &format_price($in{'landedcost'}); 

	$in{'wholesalepriceorigin'} = &format_price($in{'wholesalepriceorigin'});
	$in{'wholesaleorigin'} = $in{'wholesaleorigin'};
	$in{'wholesaleprice'} = $in{'wholesaleprice'};
	$in{'sltv_netcost'} = &format_price($in{'sltv_netcost'});
	$in{'msrp'} = &format_price($in{'msrp'});
	$in{'map'} = &format_price($in{'map'});

	if ($in{'id_products'}){
		$va{'price'} = &load_name('sl_products_sprices','ID_products',$in{'id_products'},'Price');
	}

	### Calculate Shipping Charges
	($va{'shptotal1'},$va{'shptotal2'},$va{'shptotal3'},$va{'shptotal1pr'},$va{'shptotal2pr'},$va{'shptotal3pr'},$va{'shp_text1'},$va{'shp_text2'},$va{'shp_text3'},$va{'shp_textpr1'},$va{'shp_textpr2'},$va{'shp_textpr3'})= 	&sltv_itemshipping($in{'edt'},$in{'sizew'},$in{'sizeh'},$in{'sizel'},$in{'weight'},$in{'id_packingopts'},$in{'shipping_table'},$in{'shipping_discount'},$in{'id_products'});
	$va{'shptotal1'} = &format_price($va{'shptotal1'});
	$va{'shptotal2'} = &format_price($va{'shptotal2'});
	$va{'shptotal1pr'} = &format_price($va{'shptotal1pr'});
	$va{'shptotal2pr'} = &format_price($va{'shptotal2pr'});
	
	## Prices
	$in{'sprice'} = &format_price($in{'sprice'});
	$in{'sprice1'} = &format_price($in{'sprice1'});
	$in{'sprice2'} = &format_price($in{'sprice2'});
	$in{'sprice3'} = &format_price($in{'sprice3'});
	$in{'sprice4'} = &format_price($in{'sprice4'});
	$in{'paytype'} =~ s/\|/&nbsp;-&nbsp;/g;

	#$in{'pactive'} = "SPrice1";

	## Packing Options
	if ($in{'id_packingopts'}){
		$in{'pckoptsname'} = &load_name('sl_packingopts','ID_packingopts',$in{'id_packingopts'},'Name');
		$in{'shpcharges'}  = &load_name('sl_packingopts','ID_packingopts',$in{'id_packingopts'},'Shipping');
		$in{'shpcharges'}  = &format_price($in{'shpcharges'});
	}
	
	## Shipping Prices
	if($in{'shipping_table'} eq 'Fixed'){
		$va{'shipping_options'} = qq|<td width="30%" valign="top">Packing/Shipping Options : </td>
				  											 <td class="smalltext">([in_shpcharges]) [in_pckoptsname]</td>|;
	}elsif($in{'shipping_table'} eq 'Variable'){
		$va{'shipping_options'} = qq|aqui va la tabla de valores variables|;
	}elsif($in{'shipping_table'} eq 'Table'){
		
		## Add row/col?
		if($in{'add_shptable_data'}){
			if($in{'add_type'} eq 'amount'){
				
					my ($sth) = &Do_SQL("SELECT DISTINCT(Quantity) FROM sl_products_shipping WHERE Zone='$in{'zone'}' AND Method='$in{'method'}' ORDER BY Quantity;");
					while(my($base_value) = $sth->fetchrow()){
						push(@ary_data,$base_value)	
					}
				
					for(0..$#ary_data){			
						$squery .= "INSERT INTO sl_products_shipping VALUES(0,$in{'id_products'},'$in{'zone'}','$in{'method'}',$ary_data[$_],'$in{'add_value'}','','Active',CURDATE(),CURTIME(),$usr{'id_admin_users'});";
					}
					my ($sth) = &Do_mSQL($squery);
					&auth_logging('mer_products_shptable_'.$in{'add_type'}.'_added',$in{'id_products'});
					
			}elsif($in{'add_type'} eq 'quantity'){
				
				my ($sth) = &Do_SQL("SELECT DISTINCT(Amount) FROM sl_products_shipping WHERE Zone='$in{'zone'}' AND Method='$in{'method'}' ORDER BY Amount;");
					while(my($base_value) = $sth->fetchrow()){
						push(@ary_data,$base_value)	
					}
				
					for(0..$#ary_data){			
						$squery .= "INSERT INTO sl_products_shipping VALUES(0,$in{'id_products'},'$in{'zone'}','$in{'method'}','$in{'add_value'}',$ary_data[$_],'','Active',CURDATE(),CURTIME(),$usr{'id_admin_users'});";
					}
					my ($sth) = &Do_mSQL($squery);
					&auth_logging('mer_products_shptable_'.$in{'add_type'}.'_added',$in{'id_products'});
				
			}
			delete($in{'add_shptable_data'});
			delete($in{'add_type'});
			delete($in{'add_value'});
		}
		
		$va{'shipping_options'} = qq|
		<td valign="top" colspan="2">Shipping Prices:<br>
						<table align="center" width="70%">
							<tr>
								<td>
									[tb_products_shipping_table]
								</td>
							</tr>
						</table>
			 </td>|
	}
	
	
	## Flexipago
	$in{'downpayment'} = &format_price($in{'downpayment'});
	$in{'fpprice'} = &format_price($in{'fpprice'});
	
	
	## Load Inventory
	if (&load_name('sl_skus','ID_products',$in{'id_products'},'IsSet') eq 'Y'){
		$in{'inventory'} = "SET";
	}else{
		my ($sth) = &Do_SQL("SELECT SUM(Quantity) FROM sl_warehouses_location  WHERE RIGHT(ID_products,6)='$in{'id_products'}';");
		$in{'inventory'} = &format_number($sth->fetchrow);
	}
	
	## Status Image
	&load_status_image;
	
	#### Expand the apropiate accordion
	$va{'actual_item'} = 3;
	$va{'actual_item'} = 0	if $in{'field'};
	
	($in{'user_type'} eq '') and ($in{'user_type'} = 'Browsable by all operators');

	## Downsale Names
	for my $i(1..4){
		if ($in{'sprice'.$i.'name'} eq '') {
			$in{'sprice'.$i.'name'} = 'Downsale '.$i;
		}
	}

	## Price percents
	if ($in{'upd_percent'}){

		my (@percents) = split(/\|/,$in{'price_percent'.$in{'id_products'}});
		
		my ($total_price_percent)=0;
		my ($clean_value)='';
		for (0..$#percents){
			my $temp_val = (int($percents[$_]) == 0)? 0:int($percents[$_]);
			$clean_value.= $temp_val.'|';
			$total_price_percent += $temp_val;
		}
		chop($clean_value);

		if ($clean_value eq ''){
			&Do_SQL("DELETE FROM sl_vars WHERE VName='percent_promo".$in{'id_products'}."';");
			$va{'tabmessage'}=&trans_txt('deleted_percent_price_promo') 
		}else{
			if ( abs($total_price_percent - 100) > 0){
				$va{'tabmessage'}=&trans_txt('error_percent_price_promo') 
			}else{
				&Do_SQL("DELETE FROM sl_vars WHERE VName='percent_promo".$in{'id_products'}."';");
				&Do_SQL("INSERT INTO sl_vars SET VName='percent_promo".$in{'id_products'}."', VValue='".$clean_value."';");
				$va{'tabmessage'}=&trans_txt('updated_percent_price_promo') 
			}
		}

		&auth_logging('mer_products_promo_upd',$in{'id_products'});
	}
	

	## Load SAT ID
	my $id_product_service = &Do_SQL(qq|SELECT CONCAT(cu_products_services.ID_product_service, ' - ', cu_products_services.description ) product
		FROM cu_relations_products
		INNER JOIN cu_products_services on cu_products_services.ID_product_service = cu_relations_products.ID_products_services
		WHERE 1
			AND id_table = '$in{'view'}'
			AND `table` = 'sl_products'|)->fetchrow();
	
	$in{'id_product_service'} = $id_product_service;

}

sub updated_mer_products {
# --------------------------------------------------------
# Forms Involved: 
# Created on: 1/1/2007 9:43AM
# Last Modified on:
# Last Modified by:
# Author: 
# Description : 
# Parameters : 
  
  $in{'id_products_code'} = &format_sltvid($in{'id_products'});
  
	if ($in{'oldpactive'} ne $in{'pactive'}){
		&auth_logging('mer_products_priceact',$in{'id_products'});
	}
	
	if ($in{'oldsprice'} ne $in{'sprice'}){
		## Precio  cambio
		my ($sth) = &Do_SQL("INSERT INTO sl_products_sprices SET ID_products='$in{'id_products'}',Name='".&filter_values($in{'spricename'})."',Price='$in{'sprice'}',OldPrice='$in{'oldsprice'}',Date=Curdate(),Time=NOW(),ID_admin_users='$usr{'id_admin_users'}'");
		&auth_logging('mer_products_priceupdated',$in{'id_products'});
	}
	for my $i(1..4){
		if ($in{'oldsprice'.$i} ne $in{'sprice'.$i}){
			my ($sth) = &Do_SQL("INSERT INTO sl_products_sprices SET ID_products='$in{'id_products'}',Name='".&filter_values($in{'spricename'}.$i)."',Price='$in{'sprice'.$i}',OldPrice='$in{'oldsprice'.$i}',Date=Curdate(),Time=NOW(),ID_admin_users='$usr{'id_admin_users'}'");
			&auth_logging('mer_products_priceupdated',$in{'id_products'});
		}
	}
	#if ($in{'oldsprice1'} ne $in{'sprice1'}){
	#	## Precio  cambio
	#	&auth_logging('mer_products_priceadded',$in{'id_products'});
	#}
	#if ($in{'oldsprice2'} ne $in{'sprice2'}){
	#	## Precio  cambio
	#	&auth_logging('mer_products_priceadded',$in{'id_products'});
	#}
	#if ($in{'oldsprice3'} ne $in{'sprice3'}){
	#	## Precio  cambio
	#	&auth_logging('mer_products_priceadded',$in{'id_products'});
	#}
	#if ($in{'oldsprice4'} ne $in{'sprice4'}){
	#	## Precio  cambio
	#	&auth_logging('mer_products_priceadded',$in{'id_products'});
	#}




	$exists = &Do_SQL("SELECT count(*) FROM cu_relations_products WHERE id_table = '$in{'id_products'}' and `table` = 'sl_products' ")->fetchrow();
	if($exists){
		$in{'id_product_service'} =~ s/\D//g;
		&Do_SQL("UPDATE cu_relations_products SET `ID_products_services` = '$in{'id_product_service'}' WHERE `id_table` = '$in{'id_products'}' AND `table` = 'sl_products'");
	}else{
        $in{'id_product_service'} =~ s/\D//g;
		&Do_SQL("INSERT INTO cu_relations_products (`id_table`, `table`, `ID_products_services`) VALUES ($in{'id_products'}, 'sl_products', '$in{'id_product_service'}')");
		
	}
}


sub advsearch_mer_products {
# --------------------------------------------------------
# Forms Involved: 
# Created on: 1/1/2007 9:43AM
# Last Modified on:
# Last Modified by:
# Author: 
# Description : 
# Parameters : 
	$in{'id_products_code'} = &format_sltvid($in{'id_products'});
	if ($in{'upc'}){
		my ($sth) = &Do_SQL("SELECT ID_products FROM sl_skus WHERE UPC='$in{'upc'}'");
		$in{'id_products'} = $sth->fetchrow;
		if ($in{'id_products'}>0){
			$in{'tab'}=3;
			return &query('sl_products');
		}else{
			return ();
		}
	}elsif($in{'sl_products_categories.id_categories'}){
		###querydb2($db1,$db2,$jqry,$header_fields)
		my ($hfields);
		$in{'sl_products_categories.sx'}=1;
		$in{'st'} = 'AND';
		for (0..$#headerfields){
			$hfields .= "sl_products.$headerfields[$_],";
		} 
		chop($hfields);

		return &querydb2('sl_products','sl_products_categories','sl_products.ID_products=sl_products_categories.ID_products',$hfields);
	
	}else{
		my ($fname);
		for (0..$#db_cols){
			$fname = lc($db_cols[$_]);
			($in{'sl_products.'.$fname}) and ($in{$fname} = $in{'sl_products.'.$fname});
			delete($in{'sl_products.'.$fname});
		}
		return &query('sl_products');
	}
}


#	Function: validate_mer_products
#
#   	Validates mer_products with specific rules
#
#	Created by: _Carlos Haas_
#
#	Modified By:
#
#		Roberto Barcenas on 03/22/2012: SpriceNames editable
#
#   	Parameters:
#
#		None
#
#   	Returns:
#
#		After evaluate could return error to the form
#
#   	See Also:
#
#		products_view.html, products_form.html      
sub validate_mer_products {


	my $err;

	# if($in{'paytype'} eq ""){
	# 	++$err;
	# 	$error{'paytype'}=&trans_txt('required');;
	# }

	(!$in{'shipping_discount'}) and ($in{'shipping_discount'} = 'No');
	(!$in{'shipping_table'}) and ($in{'shipping_table'} = 'Fixed');
	(!$in{'expressshipping'}) and ($in{'expressshipping'} = 'No');
	if ($in{'add'}){
		my ($count);
		$in{'not_autoincrement'} = 1;
		delete($in{'id_products'});
		while (!$in{'id_products'} and $in{'id_products'}<=100000 and $count<300){
			$in{'id_products'} = substr(int(rand(10000000000)) + 1,2,6);
			my ($sth) = &Do_SQL("SELECT COUNT(*) FROM sl_products WHERE ID_products='$in{'id_products'}';");
			if ($sth->fetchrow >0 or $in{'id_products'}<=100000){
				delete($in{'id_products'});
			}
			++$count;
		}
		if (!$in{'id_products'}){
			&load_new_prodid;
		}

		## Downsale Names
		for my $i(1..4){
			if ($in{'sprice'.$i.'name'} eq '') {
				if($i == 1){
					$in{'sprice'.$i.'name'} = 'Upsell';
				}elsif($i==4){
					$in{'sprice'.$i.'name'} = 'Fidelizacion';
				}else{
					$in{'sprice'.$i.'name'} = 'Downsale ' . $i;
				}
			}
		}
	}
	elsif($in{'edit'}){
		$in{'smalldescription'} = &load_name('sl_products','ID_products',$in{'id_products'},'SmallDescription');
		$in{'description'} = &load_name('sl_products','ID_products',$in{'id_products'},'Description');
		$in{'description_en'} = &load_name('sl_products','ID_products',$in{'id_products'},'Description_en');
		$in{'smalldescription_en'} = &load_name('sl_products','ID_products',$in{'id_products'},'SmallDescription_en');		
	}

	
	# (!$in{'pactive'}) and ($in{'pactive'} = 'SPrice');
	# if (!$in{'flexipago'}){
	# 	$error{'flexipago'} = &trans_txt('required');
	# }
	
	# if ($in{'pactive'}){
	# 	if ($in{lc($in{'pactive'})}>=0.01){
	# 		$in{'sprice'} = $in{lc($in{'pactive'})};
	# 		$in{'spricename'} = $in{lc($in{'pactive'}).'name'};
	# 	}else{
	# 		$error{lc($in{'pactive'})} = &trans_txt('required');
	# 		++$err;
	# 	}
	# }
	&set_products_dids($in{'id_products'},$in{'dids'}) if !$err;
	
	my $is_webavailable='';
	## Verifying web_available option
	($in{'add'}) ?
		$is_webavailable='No' :
		$is_webavailable = &load_name('sl_products','ID_products',$in{'id_products'},'web_available');
	
	if($in{'web_available'} eq 'Yes' and $is_webavailable ne 'Yes'){
		&write_to_list('Innovashop','products',3000,0,$in{'id_products'},'sl_products');
		&write_to_list('Innovashop','products',2983,0,$in{'id_products'},'sl_products');
	}
	&load_cfg('sl_products');
	return $err;
}

sub load_links {
# --------------------------------------------------------
# Forms/subroutines Involved: helper of load_descriptions and view_mer_products subs
# Created on: 9/10/2007
# Last Modified on:
# Last Modified by:
# Author: Rafael Sobrino
# Description : loads the links and the values of the description fields in the html editor in mer_products_view.html
	
	$in{'id_products_code'} = &format_sltvid($in{'id_products'});
	if (!$perm{'mer_products_edit'}) {
		$va{'pageslist'} = 1;
		 $va{'searchpayments'} = qq|
			<tr>
				<td colspan='6' align="center" class="stdtxterr">|.&trans_txt('not_auth').qq|</td>
			</tr>\n|;
	}else{	
		### Editor Links
		$in{'smalldescription_link'} = $in{'field'} eq "smalldescription" ? "" : "[ <a href='/cgi-bin/mod/admin/dbman?cmd=mer_products&view=[in_id_products]&field=smalldescription'>Edit</a> ]";
		$in{'description_link'} = $in{'field'} eq "description" ? "" : "[ <a href='/cgi-bin/mod/admin/dbman?cmd=mer_products&view=[in_id_products]&field=description'>Edit</a> ]";
		$in{'smalldescription_en_link'} = $in{'field'} eq "smalldescription_en" ? "" : "[ <a href='/cgi-bin/mod/admin/dbman?cmd=mer_products&view=[in_id_products]&field=smalldescription_en'>Edit</a> ]";
		$in{'description_en_link'} = $in{'field'} eq "description_en" ? "" : "[ <a href='/cgi-bin/mod/admin/dbman?cmd=mer_products&view=[in_id_products]&field=description_en'>Edit</a> ]";
		$in{'disclaimer_link'} = $in{'field'} eq "disclaimer" ? "" : "[ <a href='/cgi-bin/mod/admin/dbman?cmd=mer_products&view=[in_id_products]&field=disclaimer'>Edit</a> ]";
		$in{'countryorigin_link'} = $in{'field'} eq "countryorigin" ? "" : "[ <a href='/cgi-bin/mod/admin/dbman?cmd=mer_products&view=[in_id_products]&field=countryorigin'>Edit</a> ]";
	}
	
	### Field values
	$in{'smalldescription_text'} = $in{'field'} eq "smalldescription" ? "&nbsp;" : "$in{'smalldescription'}";
	$in{'description_text'} = $in{'field'} eq "description" ? "&nbsp;" : $in{'description'};				
	$in{'smalldescription_en_text'} = $in{'field'} eq "smalldescription_en" ? "&nbsp;" : $in{'smalldescription_en'};
	$in{'description_en_text'} = $in{'field'} eq "description_en" ? "&nbsp;" : $in{'description_en'};	
	$in{'disclaimer_text'} = $in{'field'} eq "disclaimer" ? "&nbsp;" : $in{'disclaimer'};		
	$in{'countryorigin_text'} = $in{'field'} eq "countryorigin" ? "&nbsp;" : $in{'countryorigin'};			
}


#	Function: products_moreinfo
#
#   	Validates mer_products with specific rules
#
#	Created by: _Carlos Haas_
#
#	Modified By:
#
#
#   	Parameters:
#
#		None
#
#   	Returns:
#
#		Links for products advance editing
#
#   	See Also:
#
#		products_view.html, products_form.html      
sub products_moreinfo {
	
	if ($in{'edit'} or $in{'modify'} ){
		return &build_page('forms:products_links.html');
	}
}

sub search_mer_products {
	my ($output);
	
	$output = qq| <tr>
			<td width="30%">Keywords : <span class="smallfieldterr">[er_keyword]</span></td>
			<td class="smalltext"><input type="text" name="keyword" value="[in_keyword]" size="60" style="width: 100%" onFocus='focusOn( this )' onBlur='focusOff( this )'></td>
		       </tr>
			<input type="hidden" name="oldpactive" value="SPrice">
			<input type="hidden" name="pactive"  value="SPrice"> 
			<input type="hidden" name="spricename" value="Precio 1">| if(!$in{'search'});
	return $output;
}





1;