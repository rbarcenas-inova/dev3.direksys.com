#!/usr/bin/perl
#####################################################################
########                   APARTS	        		           		#########
#####################################################################
sub load_tabsconf {
# --------------------------------------------------------

	if($in{'tab'} eq 6){
		## Logs Tab
		$va{'tab_type'}  = 'movs';
		$va{'tab_title'} = &trans_txt('movs');
		$va{'tab_table'} = 'sl_orders';
		$va{'tab_idvalue'} = $in{'id_orders'};
	}elsif($in{'tab'} eq 12){
		## Logs Tab
		$va{'tab_type'}  = 'logs';
		$va{'tab_title'} = &trans_txt('logs');
		$va{'tab_table'} = 'sl_orders';
	}
}

sub proc_pay_data {
# --------------------------------------------------------
	my ($data) = @_;
	my ($output,@ary,$key,$value,%rec);
	if ($data =~ /^Submited Info|^=====/ or $data =~ /SKO|Order Captured|Already Captured|Monterey Deal|Moved to: Monterey/){
		$data =~ s/\n/<br>/g;
		return $data;
	}
	
	
	@ary = split(/\n/,$data);
	for (0..$#ary){
		($key,$value) = split(/=/,$ary[$_],2);
		$rec{$key} = $value;
	}
	if ($rec{'card_cardtype'}){
		# Credit card Info
		delete($rec{'decision_publicsignature'});
		delete($rec{'orderamount_publicsignature'});
		delete($rec{'ordercurrency_publicsignature'});
		delete($rec{'ordernumber_publicsignature'});
		delete($rec{'orderpage_requesttoken'});
		delete($rec{'signedfields'});
		delete($rec{'transactionsignature'});
		delete($rec{'sid'});
		delete($rec{'return_cc'});
		
		$rec{'message'} = "<font color='red'>".&cybersource_codes($rec{'reasoncode'}).'</font>';
		#		$va{'speechname'}= 'ccinbound:7a- Payment Info Credit Card';
		#	}elsif($cses{'pay_type'} eq 'check'){
		#		$va{'speechname'}= 'ccinbound:7b- Check Declined';
		#		$va{'message'} = &trans_txt('ck_problem') . &certegy_codes($tmp{'PayNetResponseSubcode'},%tmp);
		#	}
		
	}elsif($rec{'MerchantID'}){
		# Check Info
		$rec{'message'} = "<font color='red'>".&certegy_codes($rec{'PayNetResponseSubcode'}).'</font>';
	}
	foreach $key (sort keys %rec){
		($rec{$key} = substr($rec{$key},0,40)) unless ($key eq 'message');
		($rec{$key}) and ($output .= "$key = $rec{$key}<br>");
	}
	
	return $output;
}

sub cybersource_codes {
# --------------------------------------------------------
	my ($code)= @_;
	my ($sth) = &Do_SQL("SELECT * FROM sl_vars WHERE VName='cybersource' AND VValue='$code'");
	my ($rec) = $sth->fetchrow_hashref;
	#"<br>$tmp{'reasoncode'} " . $rec->{'Definition_En'} . ;
	my (%fname)= ('card_accountNumber'=>'pmtfield3');
	return "$rec->{'Definition_En'} ";
}

sub certegy_codes {
# --------------------------------------------------------
	my ($code)= @_;
	my ($sth) = &Do_SQL("SELECT * FROM sl_vars WHERE VName='Certegy' AND Subcode='$code'");
	my ($rec) = $sth->fetchrow_hashref;
	return "$rec->{'Definition_En'}";
}

sub load_tabs1 {
########################
##	Tab1.- Items  ##
########################
# --------------------------------------------------------
# Forms Involved: 
# Created on: 11/13/08 12:44:15
# Author: MCC C. Gabriel Varela S.
# Description :   
# Parameters :
# Last Modified on: 11/19/08 13:18:44
# Last Modified by: MCC C. Gabriel Varela S: Se hace que cuando un servicio tiene status inactive, se tache la cantidad el shipping y el sale price
# Last Modified on: 12/04/08 09:19:19
# Last Modified by: MCC C. Gabriel Varela S: Se comenta edici�n de productos.
# Last Modified on: 12/15/08 17:29:10
# Last Modified by: MCC C. Gabriel Varela S: Se deshabilita drop
# Last Modified on: 01/07/09 13:22:14
# Last Modified by: Jose Ramirez Garcia: Se agrega la opcion de borrar tracking info
# Last Modified on: 01/08/09 13:10:07
# Last Modified by: MCC C. Gabriel Varela S: Se modifica para ver que se puedan editar los productos si el usuario tiene usergroup = 1
# Last Modified RB: 01/15/09  11:32:43 - Solo developeres borran tracking info
# Last Modification by JRG : 03/05/2009 : Se agrega el log
# Last Modified RB: 03/11/2011  15:50:43 - Se muestran todos los productos. Antes solo se mostraban los productos que el SKU estuviera Active 

#Last modified on 8 Jun 2011 15:41:06
#Last modified by: MCC C. Gabriel Varela S. :variable va_secret_cupon is set

#Last modified on: 06/04/2015
#Last modified by: ISC Gilberto Quirino: Se elimina el link para editar la orden en el tab Items.

	##--------------------------------------------------------------------
	## Se comenta todo este bloque para quitar el link para editar la
	## orden desde el tab de Items
	##--------------------------------------------------------------------
	# if(&is_adm_order($in{'id_orders'}) or is_exportation_order($in{'id_orders'})){
	# 	my $locked = load_name("sl_orders","ID_orders",$in{'id_orders'},"Status") eq 'Shipped' ? "alert('Order already Shipped. No further modification allowed');" : 'edit_order_wqty();';
	# 	if(&check_permissions('edit_order_wholesale_ajaxmode','','')) {
	# 		# $va{'editorder'} = qq|<a href="javascript:return false;" class="scroll" onClick="$locked">Edit Order with quantity</a>|;

	# 		## New Edit
	# 		$va{'editorder'} .= qq|<a href="javascript:return false;" class="scroll" onClick="edit_order_new()">..::Edit Order::..</a>|; # if ($usr{'id_admin_users'}==5);
	# 	}
	# }else{
	# 	my $locked = load_name("sl_orders","ID_orders",$in{'id_orders'},"Status") eq 'Shipped' ? "alert('Order already Shipped. No further modification allowed');" : 'edit_order();';
	# 	if(&check_permissions('edit_order_wholesale_ajaxmode','','')) {
	# 		$va{'editorder'} = qq|<a href="javascript:return false;" class="scroll" onClick="$locked">Edit Order</a>|;
	# 		# $va{'editorder'} = qq|<a href="javascript:return false;" class="scroll" onClick="popup_show('ajax_windows', 'ajax_drag', 'ajax_exit', 'element-right', -1, -1,'prdmenu');loadDoc('/cgi-bin/common/apps/ajaxbuild?ajaxbuild=orders_tab1&id_orders=[in_id_orders]');">Order Actions</a>|	if $cfg{'order_old_edition'} == 1;
		
	# 		# 230813-AD: Se bloquea totalmente la edicion de ordenes para TMK hasta nuevo aviso
	# 		# $va{'editorder'} = qq|<a href="javascript:return false;" class="scroll" onClick="alert('Operation not allowed');">Edit Order</a>| if(!&check_permissions('edit_order_edit_price','',''));
	# 		$va{'editorder'} = qq|<a href="javascript:return false;" class="scroll" onClick="edit_order_new()">..::Edit Order::..</a>|;
	# 	}
	# }

	### New Edit Order
	# if ($usr{'id_admin_users'}==5 and &check_permissions('edit_order_ajaxmode','','')){
	#  	$va{'editorder'} .= qq|<a href="javascript:return false;" class="scroll" onClick="edit_order_new()">New Edit</a>|;
	# }
	##--------------------------------------------------------------------
	
	# Validation to edit orders processed
	if (($in{'status'} eq 'Processed' or $in{'status'} eq 'Shipped') and !&check_permissions('edit_order_processed','','')){
		$va{'editorder'} = &trans_txt('opr_orders_cant_edit_order_processed');
	}

	# $va{'editorder'} = qq|<a href="javascript:return false;" class="scroll" onClick="edit_order_new()">..::Edit Order::..</a>|;

	# if($usr{'application'} eq 'crm'){
		# #$va{'secret_cupon'}='<a href="javascript:return false;" onclick="check_cuponf();"><img src="/sitimages/main/b_primary.png" name="check_cupon" id="check_cupon" border="0" ></a>';
	# }

	&loaddatapayment($in{'id_orders'});	
	if ($in{$key}){
		foreach my $key (keys %in){
			if ($in{$key} eq 'add_itemser'){				#GV Modifica 21abr2008 Se cambia sl_services por sl_services			
				my ($sth) = &Do_SQL("SELECT COUNT(*) FROM sl_services WHERE ID_services='".substr($key,7,2)."'");
				if ($sth->fetchrow ==0){
					my ($sth) = &Do_SQL("INSERT INTO sl_orders_products SET  ID_products='".substr($key,4,6)."',ID_orders='$in{'id_orders'}',Quantity=1,Date=Curdate(),Time=NOW(),ID_admin_users='$usr{'id_admin_users'}'");
					&auth_logging('orders_products_added',$sth->{'mysql_insertid'});
					++$new_items;
					$in{'tabs'} = 1;
				}
			}		
		}

		if ($new_items){
			$va{'tabmessages'} = &trans_txt('opr_orders_added');
			&auth_logging('opr_orders_added',$in{'id_orders'});
		}					
	}

	$in{'drop'} = int($in{'drop'});
	if ($in{'drop'}>0){
		my ($sth) = &Do_SQL("UPDATE sl_orders_products SET Status='Inactive' WHERE ID_orders='$in{'id_orders'}' AND ID_orders_products='$in{'drop'}'");
		&auth_logging('opr_orders_itemdroped',$in{'id_orders'});
		$va{'tabmessages'} = &trans_txt('opr_orders_itemdroped');
		$in{'tabs'} = 1;
		#RB Start - Add servicesItems - apr2108 - 
	}elsif($in{'addnitem'}){
		my ($sprice) = &load_name('sl_services','ID_services',$in{'addnitem'},'SPrice');
		if ($sprice>0){
			$sku_id=600000000+$in{'addnitem'};
			my ($stu1) = &Do_SQL("INSERT INTO sl_orders_products SET ID_products=$sku_id,ID_orders=$in{'id_orders'},Quantity=1,SalePrice='$sprice',Status='Active',PostedDate=CURDATE(),Date=CURDATE(),Time=NOW(),ID_admin_users='$usr{'id_admin_users'}'");
			&auth_logging('opr_orders_itemadded',$in{'id_orders'});
			delete($in{'id_products'});
		}else{
			$va{'tabmessages'} = "<br>".&trans_txt('reqfields');
		}
		$in{'tabs'} = 1;

	}elsif($in{'additem'}){
		my ($sprice);				
		my ($sth) = &Do_SQL("SELECT SPrice FROM  sl_products WHERE ID_products='$in{'additem'}' AND Status NOT IN ('Testing','Inactive') AND SPrice>0");;
		$sprice = $sth->fetchrow;
		if ($sprice>0){
			$sku_id=100000000+$in{'additem'};
			my ($sth) = &Do_SQL("INSERT INTO sl_orders_products SET Status='Active',ID_products='$sku_id',ID_orders='$in{'id_orders'}',Quantity=1,SalePrice='$sprice',Date=Curdate(),Time=NOW(),ID_admin_users='$usr{'id_admin_users'}'");;
			&calc_tax_disc_shp(0,1);
			&auth_logging('opr_orders_itemadded',$in{'id_orders'});
			delete($in{'id_products'});
			$in{'tabs'} = 1;
		}else{
			$va{'tabmessages'} = "<br>".&trans_txt('reqfields');
		}
	}elsif($in{'ajaxresp'}){			
		my ($sth) = &Do_SQL("UPDATE sl_orders_products SET ID_products='$in{'ajaxresp'}' WHERE ID_orders_products='$in{'id_orders_products'}'");
		&auth_logging('ope_orders_itemupd',$in{'id_orders_products'});
		$va{'tabmessages'} = &trans_txt('ope_orders_itemupd');					
		$in{'tabs'} = 1;
	#JRG start 19-06-2008 shipping discount/charges
	}elsif($in{'shipping'}){
		my ($sprice) = $in{'amount'};
		if ($sprice>0){
			if($in{'shpdiscount'}){
				$sku_id=600001007;
				#my ($pd) = ''; // Tomar en cuenta que esto puede afectar el reporte del closebatch
				#$pd  = &load_name('sl_orders','ID_orders',$in{'id_orders'},'PostedDate');
				my ($stu1) = &Do_SQL("INSERT INTO sl_orders_products SET ID_products=$sku_id,ID_orders=$in{'id_orders'},Quantity=1,SalePrice='-$sprice',Status='Active',PostedDate=CURDATE(),Date=CURDATE(),Time=NOW(),ID_admin_users='$usr{'id_admin_users'}'");
				&auth_logging('opr_orders_shippingdiscount',$in{'id_orders'});
			}elsif($in{'shpcharges'}){
				$sku_id=600001009;
				my ($stu1) = &Do_SQL("INSERT INTO sl_orders_products SET ID_products=$sku_id,ID_orders=$in{'id_orders'},Quantity=1,SalePrice='$sprice',Status='Active',PostedDate=CURDATE(),Date=CURDATE(),Time=NOW(),ID_admin_users='$usr{'id_admin_users'}'");
				&auth_logging('opr_orders_shippingcharges',$in{'id_orders'});
			}
			delete($in{'id_products'});
		}else{
			$va{'tabmessages'} = "<br>".&trans_txt('reqfields');
		}
		$in{'tabs'} = 1;
	#JRG end 19-06-2008 shipping discount/charges
	#JRG start 20-06-2008 return/restock fee
	}elsif($in{'fee'}){
		if($in{'returnfee'}){
			if($in{'weight'}>5){
				$sprice = $cfg{'greaterfee'};
			} else {
				$sprice = $cfg{'minorfee'};
			}
			if ($sprice>0){
				$sku_id=600001014;
				my ($stu1) = &Do_SQL("INSERT INTO sl_orders_products SET ID_products=$sku_id,ID_orders=$in{'id_orders'},Quantity=1,SalePrice='$sprice',Related_ID_products='$in{'related_id'}',Status='Active',PostedDate=CURDATE(),Date=CURDATE(),Time=NOW(),ID_admin_users='$usr{'id_admin_users'}'");
				&auth_logging('opr_orders_returnfee',$in{'id_orders'});
			}
		}elsif($in{'restockfee'}){
			$sprice = $in{'product_sprice'}*0.15;
			if ($sprice>0){
				$sku_id=600001006;
				my ($stu1) = &Do_SQL("INSERT INTO sl_orders_products SET ID_products=$sku_id,ID_orders=$in{'id_orders'},Quantity=1,SalePrice='$sprice',Related_ID_products='$in{'related_id'}',Status='Active',PostedDate=CURDATE(),Date=CURDATE(),Time=NOW(),ID_admin_users='$usr{'id_admin_users'}'");
				&auth_logging('opr_orders_restockfee',$in{'id_orders'});
			}
		}else{
			$va{'tabmessages'} = "<br>".&trans_txt('reqfields');
		}
		$in{'tabs'} = 1;
	}elsif($in{'addsample'}){
		$sku_id=500000000+$in{'addsample'};
		my ($sth) = &Do_SQL("INSERT INTO sl_orders_products SET Status='Active',ID_products='$sku_id',ID_orders='$in{'id_orders'}',Quantity=1,SalePrice='0',Date=Curdate(),Time=NOW(),ID_admin_users='$usr{'id_admin_users'}'");;
		&calc_tax_disc_shp(0,1);
		&auth_logging('opr_orders_sampleadded',$in{'id_orders'});
		delete($in{'id_products'});
		$in{'tabs'} = 1;
	}elsif($in{'remove_tracking_info'} and &check_permissions('edit_order_cleanup','','')){
		my ($sth) = &Do_SQL("UPDATE sl_orders_products SET Cost='0', ShpDate=NULL, Tracking=NULL, ShpProvider=NULL, PostedDate=NULL, PostedDate=NULL WHERE ID_orders_products=$in{'remove_tracking_info'}");
		&auth_logging('opr_orders_products_updated',$in{'remove_tracking_info'});
		&add_order_notes_by_type($in{'id_orders'},"The tracking info was removed for order product $in{'remove_tracking_info'}","Low");

		&auth_logging('opr_orders_noteadded',$in{'id_orders'});
	}
	
	## Items List
	my ($tot_qty,$tot_ord,$decor,$col,$link,$linkprod,$linkpack,$linkparts,$linkser);
	$linkprod = 'mer_products';
	$linkpack = 'opr_packinglist';
	$linkparts = 'mer_parts';
	$linkser = 'mer_services';
  
	($usr{'application'}) and ($linkprod = 'mer_products') and ($linkpack = 'opr_packinglist') and ($linkparts = 'mer_parts') and ($linkser = 'mer_services');
  
	my (@c) = split(/,/,$cfg{'srcolors'});
	$hide_inactives = '';
	$hide_op = '';
	if($cfg{'productos_create_newline'}){
		$hide_inactives = qq|AND Status not in ('Inactive')|;
		$hide_op = qq|AND op.Status not in ('Inactive') |;
	}
	my ($sth) = &Do_SQL("SELECT COUNT(*) FROM sl_orders_products WHERE ID_orders='$in{'id_orders'}' $hide_inactives");
	$va{'matches'} = $sth->fetchrow;

	if ($va{'matches'}>0){

		my $skus_or_products = &is_exportation_order($in{'id_orders'});

		my ($sth1) = &Do_SQL("SELECT 
				op.*
				, DATEDIFF(op.DeliveryDate,op.ShpDate) AS Lapse 
				, op2.Quantity OriginalQty
			FROM sl_orders_products op
			LEFT JOIN sl_orders_products op2 on op.ID_related_original_orders_products = op2.ID_orders_products
			WHERE 1
				AND op.ID_orders=$in{'id_orders'}
				$hide_op
			ORDER BY op.ID_orders_products,op.Date,op.Time");
		while ($col = $sth1->fetchrow_hashref){

			my $cmdorder = 'opr_orders';
			my $tax_price = ($col->{'Quantity'} > 0) ? ($col->{'Tax'} / $col->{'Quantity'} ): 0;
			my $unit_price = ($col->{'Quantity'} > 0) ? ($col->{'SalePrice'} / $col->{'Quantity'} ): 0;
			$unit_price = round($unit_price + $tax_price,2);
			my $total_price = round($col->{'SalePrice'} - $col->{'Discount'} + $col->{'Shipping'} + $col->{'Tax'} + $col->{'ShpTax'},2);

			#$cmdorder = 'orders'	if /cgi-bin/mod/$usr{'application'}/dbman =~	/crm/;
			$d = 1 - $d;			
			if(!$skus_or_products and (substr($col->{'ID_products'},0,1) < 8 and int($col->{'Related_ID_products'}) < 100000000)) {

				##################################################
				##################################################
				##################################################
				#########
				#########   REGULAR PRODUCTS
				#########
				##################################################
				##################################################
				##################################################
				$sku_id_p=substr($col->{'ID_products'},3,6);
				$sku_id_e=$col->{'ID_products'};
				$sku_id_d=format_sltvid($col->{'ID_products'});
				
				if ($col->{'Status'} ne 'Inactive'){

					$tot_qty += $col->{'Quantity'};
					$tot_ord += $total_price; #$col->{'SalePrice'};

				}
										
				my ($sthk) = &Do_SQL("SELECT * FROM sl_skus WHERE ID_sku_products='$col->{'ID_products'}' /*and Status='Active'*/");
				$rec = $sthk->fetchrow_hashref;
				$choices = &load_choices('-',$rec->{'choice1'},$rec->{'choice2'},$rec->{'choice3'},$rec->{'choice4'});
				
													
	      		if ($rec->{'IsSet'} eq 'Y'){

	      			#################
					################# SETS (PRODUCTS & PARTS)
					#################	
	      			&check_kit_shipped($col->{'ID_orders_products'},'orders');
	      			### SETS / Kits
					$va{'searchresults'} .= "<tr bgcolor='$c[$d]' onmouseover='m_over(this)' onmouseout='m_out(this)'>\n";
					$va{'searchresults'} .= " <td class='smalltext' valign='top'>";
					if ((!$col->{'ShpDate'} or $col->{'ShpDate'} eq '0000-00-00') and $col->{'Status'} eq 'Active'){
							#$va{'searchresults'} .= qq| <a href="/cgi-bin/mod/$usr{'application'}/dbman?cmd=opr_orders&view=$in{'id_orders'}&tab=1&drop=$col->{'ID_orders_products'}"><img src='$va{'imgurl'}/$usr{'pref_style'}/b_drop.png' title='Drop' alt='' border='0'></a>|;
					}
            	
		        	$va{'searchresults'} .= qq| <a href="/cgi-bin/mod/$usr{'application'}/dbman?cmd=$linkprod&view=$sku_id_p"><img src='$va{'imgurl'}/$usr{'pref_style'}/b_view.gif' title='View' alt='' border='0'></a>|;
		        	$va{'searchresults'} .= qq| <a href="/cgi-bin/mod/$usr{'application'}/dbman?cmd=$linkpack&view=$in{'id_orders'}&ID_orders_products=$col->{'ID_orders_products'}&choices=$choices"><img src='$va{'imgurl'}/$usr{'pref_style'}/b_packinglist.gif' title='Packing List' alt='' border='0'></a>|;
					$va{'searchresults'} .= "<br>$sku_id_d ";
                    if (!$col->{'Tracking'} and &check_permissions('edit_choices','','') ){
                        $va{'searchresults'} .= &build_edit_choices($col->{'ID_products'},"/cgi-bin/mod/$usr{'application'}/dbman","cmd=$cmdorder&view=$in{'id_orders'}&tab=1&ID_orders_products=$col->{'ID_orders_products'}")
                    }					
					$va{'searchresults'} .= "</td>\n";
					(!$col->{'SerialNumber'}) and ($col->{'SerialNumber'} = '---');
					($status,%tmp) = &load_product_info($sku_id_p);
					&load_cfg('sl_orders');

					if ( $col->{'ShpDate'} && ( ($col->{'ShpProvider'} eq 'FEDEX' && length($col->{'Tracking'}) == 34 ) || ($col->{'ShpProvider'} eq 'ESTAFETA' && length($col->{'Tracking'}) == 22 ) || ($col->{'ShpProvider'} eq 'UPS' && length($col->{'Tracking'}) == 18 ) )  ){
						$col->{'ShpDate'} = ($col->{'DeliveryDate'} and $col->{'DeliveryDate'} ne '0000-00-00') ? "<div><img src='/sitimages/enviado2.gif' style='position:relative; top:5px;'> ".$col->{'ShpDate'}." / <span style='color:blue;'>".$col->{'DeliveryDate'}."</span> ".$col->{'Lapse'}."</div>" : "<div><img src='/sitimages/enviado1.gif' style='position:relative; top:5px;'> ".$col->{'ShpDate'}."</div>";
					}
					
					# datos
					
					if ($col->{'Status'} eq 'Inactive'){
							$decor = " style=' text-decoration: line-through;  color:#aaaaaa; font-weight:normal; '";
					}else{
							$decor ='';
					}
				

					$va{'searchresults'} .= "  <td class='smalltext' valign='top' $decor>$tmp{'model'}<br>".substr($tmp{'name'},0,30)." ".$choices."</td>\n";
					$va{'searchresults'} .= "  <td class='smalltext' valign='top' $decor>".&build_tracking_link($col->{'Tracking'},$col->{'ShpProvider'},$col->{'ShpDate'},$col->{'ID_products'})."<br></td>\n";

					$va{'searchresults'} .= "  <td class='smalltext' align='right' valign='top' $decor>".&format_price($unit_price)."</td>\n";
					$va{'searchresults'} .= "  <td class='smalltext' align='right' valign='top' $decor>".&format_price(($col->{'Discount'}*-1))."</td>\n";
					$va{'searchresults'} .= "  <td class='smalltext' align='right' valign='top' $decor>".&format_price($col->{'Shipping'} + $col->{'ShpTax'})."</td>\n";
					$va{'searchresults'} .= "  <td class='smalltext' align='right' valign='top' $decor>".&format_number($col->{'Quantity'}) ."</td>\n";
					$va{'searchresults'} .= "  </td>\n<td class='smalltext' align='right' valign='top' $decor nowrap>".&format_price($total_price);
					
					#Se comenta edici�n de productos
					if (&check_permissions('edit_order_edit_price','','')){
							$va{'searchresults'} .= qq| 
							<div id="divpayment$rec->{'ID_orders_products'}"><a href="#tabs" onClick="popup_show('ajax_windows', 'ajax_drag', 'ajax_exit', 'element-right', -1, -1,'tabs');loadDoc('/cgi-bin/common/apps/ajaxbuild?ajaxbuild=edit_products&id_orders=$col->{'ID_orders'}&id_orders_products=$col->{'ID_orders_products'}&cmd=$in{'cmd'}&script_url=/cgi-bin/mod/$usr{'application'}/dbman');"><img src='$va{'imgurl'}/$usr{'pref_style'}/b_edit.png' title='Edit In Clean up Mode' alt='' border='0'></a></div>|;
					}
			
					$va{'searchresults'} .= "</td>\n";
					$va{'searchresults'} .= "</tr>\n";	
				
					my ($sth2) = &Do_SQL("SELECT * FROM sl_skus_parts WHERE ID_sku_products='$rec->{'ID_sku_products'}';");
					while ($tmp = $sth2->fetchrow_hashref){
							for my $i(1..$tmp->{'Qty'}){
									my ($sth3) = &Do_SQL("SELECT * FROM sl_orders_parts WHERE ID_orders_products='$col->{'ID_orders_products'}' AND ID_parts='$tmp->{'ID_parts'}' LIMIT ".($i-1).",1;");
									my ($shp) = $sth3->fetchrow_hashref;
									$va{'searchresults'} .= qq|
									<tr bgcolor='$c[$d]'>
									<td class="smalltext" $style valign="top" align="right"  onmouseover='m_over(this)' onmouseout='m_out(this)' OnClick="trjump('/cgi-bin/mod/$usr{'application'}/dbman?cmd=$linkparts&view=$tmp->{'ID_parts'}')" $decor><img src="$va{'imgurl'}/$usr{'pref_style'}/tri.gif" border="0"> |.
									&format_sltvid(400000000+$tmp->{'ID_parts'}).qq|</td>
									<td class="smalltext" $style valign="top" $decor>|.&load_db_names('sl_parts','ID_parts',$tmp->{'ID_parts'},'[Model]<br>[Name]').qq|</td>
									<td class="smalltext" $style valign="top" $decor>|.&build_tracking_link($shp->{'Tracking'},$shp->{'ShpProvider'},$shp->{'ShpDate'},400000000+$tmp->{'ID_parts'}).qq|</td>
									<td class="smalltext" valign="top" $decor>$shp->{'ShpDate'}</td>
									<td class="smalltext" $style valign="top" $decor>$tmp->{'Serial'}</td>
									<td class="smalltext" colspan="4" $decor></td>
									</tr>\n|;
							}
					}
				

	     		}elsif($col->{'ID_products'} < 99999 or substr($col->{'ID_products'},0,1) == 6){

	     			########################################################
					################## SERVICES
					########################################################
	      			(substr($col->{'ID_products'},0,1) == 6) and ($col->{'ID_products'} = substr($col->{'ID_products'},5));
					$va{'searchresults'} .= "<tr bgcolor='$c[$d]' onmouseover='m_over(this)' onmouseout='m_out(this)'>\n";
					$va{'searchresults'} .= " <td class='smalltext' valign='top'>";

					if ((!$col->{'ShpDate'} or $col->{'ShpDate'} eq '0000-00-00') and $col->{'Status'} eq 'Active'){
						#$va{'searchresults'} .= qq| <a href="/cgi-bin/mod/$usr{'application'}/dbman?cmd=opr_orders&view=$in{'id_orders'}&tab=1&drop=$col->{'ID_orders_products'}"><img src='$va{'imgurl'}/$usr{'pref_style'}/b_drop.png' title='Drop' alt='' border='0'></a>|;
					}
	
					$va{'searchresults'} .= qq| <a href="/cgi-bin/mod/$usr{'application'}/dbman?cmd=$linkser&view=$col->{'ID_products'}"><img src='$va{'imgurl'}/$usr{'pref_style'}/b_view.gif' title='View' alt='' border='0'></a>|;
					my ($sth5) = &Do_SQL("SELECT * FROM sl_services WHERE ID_services = '$col->{'ID_products'}' ;");
					$serdata = $sth5->fetchrow_hashref;
					$col->{'SerialNumber'}='';
					$col->{'ShpProvider'}='';
					$col->{'Tracking'}='';
					$col->{'ShpDate'}='';
					$va{'searchresults'} .= "<br>".&format_sltvid(600000000+$col->{'ID_products'})."</td>\n";		
					$va{'searchresults'} .= "  <td class='smalltext'>$tmp{'model'}<br>".substr($serdata->{'Name'},0,30)."</td>\n";
					$va{'searchresults'} .= "  <td class='smalltext' valign='top'>".&build_tracking_link($col->{'Tracking'},$col->{'ShpProvider'},$col->{'ShpDate'},600000000+$col->{'ID_products'})."</td>\n";			
					
					if ($col->{'Status'} eq 'Inactive'){
							$decor = " style=' text-decoration: line-through;'";
					}else{
							$decor ='';
					}
					
					$va{'searchresults'} .= "  <td class='smalltext' align='right' valign='top' $decor>".&format_price($unit_price)."</td>\n";
					$va{'searchresults'} .= "  <td class='smalltext' align='right' valign='top' $decor>".&format_price(($col->{'Discount'}*-1))."</td>\n";
					$va{'searchresults'} .= "  <td class='smalltext' align='right' valign='top' $decor>N/A&nbsp;&nbsp;&nbsp;</td>\n";
					$va{'searchresults'} .= "  <td class='smalltext' align='right' valign='top' $decor>".&format_number($col->{'Quantity'})."</td>\n";
					$va{'searchresults'} .= "  <td class='smalltext' align='right' valign='top' $decor nowrap>".&format_price($total_price);
					#Se comenta edici�n de productos
					if (&check_permissions('edit_order_edit_price','','')){
						$va{'searchresults'} .= qq| <div id="divpayment$rec->{'ID_orders_products'}"><a href="#tabs" onClick="popup_show('ajax_windows', 'ajax_drag', 'ajax_exit', 'element-right', -1, -1,'tabs');loadDoc('/cgi-bin/common/apps/ajaxbuild?ajaxbuild=edit_products&id_orders=$col->{'ID_orders'}&id_orders_products=$col->{'ID_orders_products'}&cmd=$in{'cmd'}&script_url=/cgi-bin/mod/$usr{'application'}/dbman');"><img src='$va{'imgurl'}/$usr{'pref_style'}/b_edit.png' title='Edit In Clean up Mode' alt='' border='0'></a></div>|;
					}
					$va{'searchresults'} .= "</td>\n";
					$va{'searchresults'} .= "</tr>\n";	
					
				} elsif(substr($col->{'ID_products'},0,1) == 5){
				
					$va{'searchresults'} .= "<tr bgcolor='$c[$d]' onmouseover='m_over(this)' onmouseout='m_out(this)'>\n";
					$va{'searchresults'} .= " <td class='smalltext' valign='top'>";
					$va{'searchresults'} .= qq| <a href="/cgi-bin/mod/$usr{'application'}/dbman?cmd=$linkser&view=$col->{'ID_products'}"><img src='$va{'imgurl'}/$usr{'pref_style'}/b_view.gif' title='View' alt='' border='0'></a>|;
					$id_samples = $col->{'ID_products'}-500000000;
					my ($sth5) = &Do_SQL("SELECT * FROM sl_samples WHERE ID_samples = '$id_samples' ;");
					$serdata = $sth5->fetchrow_hashref;
					$col->{'SerialNumber'}='';
					$col->{'ShpProvider'}='';
					$col->{'Tracking'}='';
					$col->{'ShpDate'}='';
					$va{'searchresults'} .= "<br>".&format_sltvid($col->{'ID_products'})."</td>\n";		
					$va{'searchresults'} .= "  <td class='smalltext'>$tmp{'model'}<br>".substr($serdata->{'Name'},0,30)."</td>\n";
					$va{'searchresults'} .= "  <td class='smalltext' valign='top'>".&build_tracking_link($col->{'Tracking'},$col->{'ShpProvider'},$col->{'ShpDate'},600000000+$col->{'ID_products'})."</td>\n";			
			
					if ($col->{'Status'} eq 'Inactive'){
							$decor = " style=' text-decoration: line-through; '";
					}else{
							$decor ='';
					}
			
					$va{'searchresults'} .= "  <td class='smalltext' align='right' valign='top' $decor>".&format_price($unit_price)."</td>\n";
					$va{'searchresults'} .= "  <td class='smalltext' align='right' valign='top' $decor>".&format_price(($col->{'Discount'}*-1))."</td>\n";
					$va{'searchresults'} .= "  <td class='smalltext' align='right' valign='top' $decor>N/A&nbsp;&nbsp;&nbsp;</td>\n";
					$va{'searchresults'} .= "  <td class='smalltext' align='right' valign='top' $decor>".&format_number($col->{'Quantity'})."</td>\n";
					$va{'searchresults'} .= "  <td class='smalltext' align='right' valign='top' $decor nowrap>".&format_price($total_price);
					#Se comenta edici�n de productos
					if (&check_permissions('edit_order_edit_price','','')){
						$va{'searchresults'} .= qq| <div id="divpayment$rec->{'ID_orders_products'}"><a href="#tabs" onClick="popup_show('ajax_windows', 'ajax_drag', 'ajax_exit', 'element-right', -1, -1,'tabs');loadDoc('/cgi-bin/common/apps/ajaxbuild?ajaxbuild=edit_products&id_orders=$col->{'ID_orders'}&id_orders_products=$col->{'ID_orders_products'}&cmd=$in{'cmd'}&script_url=/cgi-bin/mod/$usr{'application'}/dbman');"><img src='$va{'imgurl'}/$usr{'pref_style'}/b_edit.png' title='Edit In Clean up Mode' alt='' border='0'></a></div>|;
					}
					$va{'searchresults'} .= "</td>\n";
					$va{'searchresults'} .= "</tr>\n";
	
				}else{

					########################################################
					#################### PRODUCTS 
					########################################################
					my (%tmp);
					$va{'searchresults'} .= "<tr bgcolor='$c[$d]' onmouseover='m_over(this)' onmouseout='m_out(this)'>\n";
					$va{'searchresults'} .= " <td class='smalltext' valign='top'>";
					if ((!$col->{'ShpDate'} or $col->{'ShpDate'} eq '0000-00-00') and $col->{'Status'} eq 'Active'){
						#$va{'searchresults'} .= qq| <a href="/cgi-bin/mod/$usr{'application'}/dbman?cmd=opr_orders&view=$in{'id_orders'}&tab=1&drop=$col->{'ID_orders_products'}"><img src='$va{'imgurl'}/$usr{'pref_style'}/b_drop.png' title='Drop' alt='' border='0'></a>|;
					}
	            	### Products
	            	$va{'searchresults'} .= qq| <a href="/cgi-bin/mod/$usr{'application'}/dbman?cmd=$linkprod&&view=$sku_id_p"><img src='$va{'imgurl'}/$usr{'pref_style'}/b_view.gif' title='View' alt='' border='0'></a>|;
	            	$va{'searchresults'} .= qq| <a href="/cgi-bin/mod/$usr{'application'}/dbman?cmd=$linkpack&view=$in{'id_orders'}&ID_orders_products=$col->{'ID_orders_products'}&choices=$choices"><img src='$va{'imgurl'}/$usr{'pref_style'}/b_packinglist.gif' title='Packing List' alt='' border='0'></a>|;
	            	$va{'searchresults'} .= "<br>".&format_sltvid($col->{'ID_products'});
                    if (!$col->{'Tracking'} and &check_permissions('edit_choices','','') ){
                        $va{'searchresults'} .= &build_edit_choices($col->{'ID_products'},"/cgi-bin/mod/$usr{'application'}/dbman","cmd=$cmdorder&view=$in{'id_orders'}&tab=1&ID_orders_products=$col->{'ID_orders_products'}&tabs=1")
                    }					$va{'searchresults'} .= "</td>\n";
					(!$col->{'SerialNumber'}) and ($col->{'SerialNumber'} = '---');
	
					($status,%tmp) = &load_product_info($sku_id_p);
					&load_cfg('sl_orders');
					$va{'searchresults'} .= "  <td class='smalltext' valign='top'>$tmp{'model'}<br>".substr($tmp{'name'},0,30)." ".$choices."</td>\n";
					$va{'searchresults'} .= "  <td class='smalltext' valign='top'>".&build_tracking_link($col->{'Tracking'},$col->{'ShpProvider'},$col->{'ShpDate'},$col->{'ID_products'}).&remove_tracking($col->{'Tracking'},$col->{'ShpProvider'},$col->{'ShpDate'},$col->{'ID_orders_products'})."</td>\n";
	
					if ($col->{'Status'} eq 'Inactive'){
						$decor = " style=' text-decoration: line-through;'";
					}else{
						$decor ='';
					}
					
					$va{'searchresults'} .= "  <td class='smalltext' align='right' valign='top' $decor>".&format_price($unit_price)."</td>\n";
					$va{'searchresults'} .= "  <td class='smalltext' align='right' valign='top' $decor>".&format_price(($col->{'Discount'}*-1))."</td>\n";
					$va{'searchresults'} .= "  <td class='smalltext' align='right' valign='top' $decor>".&format_price($col->{'Shipping'} + $col->{'ShpTax'})."</td>\n";
					$va{'searchresults'} .= "  <td class='smalltext' align='right' valign='top' $decor>".&format_number($col->{'Quantity'})."</td>\n";
					$va{'searchresults'} .= "  </td>\n<td class='smalltext' align='right' valign='top' $decor nowrap>".&format_price($total_price);
					#Se comenta edici�n de productos
					if (&check_permissions('edit_order_edit_price','','')){
						$va{'searchresults'} .= qq| <div id="divpayment$rec->{'ID_orders_products'}"><a href="#tabs" onClick="popup_show('ajax_windows', 'ajax_drag', 'ajax_exit', 'element-right', -1, -1,'tabs');loadDoc('/cgi-bin/common/apps/ajaxbuild?ajaxbuild=edit_products&id_orders=$col->{'ID_orders'}&id_orders_products=$col->{'ID_orders_products'}&cmd=$in{'cmd'}&script_url=/cgi-bin/mod/$usr{'application'}/dbman');"><img src='$va{'imgurl'}/$usr{'pref_style'}/b_edit.png' title='Edit In Clean up Mode' alt='' border='0'></a></div>|;
					}
					$va{'searchresults'} .= "</td>\n";
					$va{'searchresults'} .= "</tr>\n";	
	
				}


			}elsif(substr($col->{'ID_products'},0,1) == 8 and int($col->{'Related_ID_products'}) > 0) {				
				####################################################
				####################################################
				####################
				#################### CREDIT MEMO
				####################
				####################################################
				####################################################

				if( $skus_or_products )
				{
					#my ($sth5) = &Do_SQL("SELECT ID_creditmemos FROM sl_creditmemos_payments WHERE ID_orders_products_added = '$col->{'ID_orders_products'}' ;");
					#$col->{'ID_creditmemos'} = $sth5->fetchrow();
					$va{'searchresults'} .= "<tr bgcolor='$c[$d]' onmouseover='m_over(this)' onmouseout='m_out(this)'>\n";
					$va{'searchresults'} .= " <td class='smalltext' valign='top'>";
					$va{'searchresults'} .= qq| <a href="/cgi-bin/mod/$usr{'application'}/dbman?cmd=opr_creditmemos&&view=$col->{'Related_ID_products'}"><img src='$va{'imgurl'}/$usr{'pref_style'}/b_view.gif' title='View' alt='' border='0'></a>| if ($col->{'Related_ID_products'}>0);
					$va{'searchresults'} .= "<br>".&format_sltvid($col->{'ID_products'})."</td>\n";		
					$va{'searchresults'} .= "  <td class='smalltext'>Credit Memo : $col->{'Related_ID_products'}</td>\n";
					$va{'searchresults'} .= "  <td class='smalltext' valign='top'></td>\n";			
					if ($col->{'Status'} eq 'Inactive'){
							$decor = " style=' text-decoration: line-through'";
					}else{
							$decor ='';
					}
		
					$va{'searchresults'} .= "  <td class='smalltext' align='right' valign='top' $decor>".&format_price($unit_price)."</td>\n";
					$va{'searchresults'} .= "  <td class='smalltext' align='right' valign='top' $decor>".&format_price(($col->{'Discount'}*-1))."</td>\n";
					$va{'searchresults'} .= "  <td class='smalltext' align='right' valign='top' $decor>N/A&nbsp;&nbsp;&nbsp;</td>\n";
					$va{'searchresults'} .= "  <td class='smalltext' align='right' valign='top' $decor>".&format_number($col->{'Quantity'})."</td>\n";
					$va{'searchresults'} .= "  <td class='smalltext' align='right' valign='top' $decor nowrap>".&format_price($total_price);
					$va{'searchresults'} .= "</td>\n";
					$va{'searchresults'} .= "</tr>\n";
					
				}				
				else
				{
					my $cmname = &load_name('sl_creditmemos', 'ID_creditmemos', $col->{'Related_ID_products'}, 'Description');
					my $cm_return = &load_name('sl_creditmemos', 'ID_creditmemos', $col->{'Related_ID_products'}, 'Reference');
					$cmname .= qq|: <a href="/cgi-bin/mod/$usr{'application'}/dbman?cmd=opr_returns&view=$cm_return">$cm_return</a>|;

					$va{'searchresults'} .= "<tr bgcolor='$c[$d]' onmouseover='m_over(this)' onmouseout='m_out(this)'>\n";
					$va{'searchresults'} .= " <td class='smalltext' valign='top' nowrap>";
		        	$va{'searchresults'} .= qq| <a href="/cgi-bin/mod/$usr{'application'}/dbman?cmd=opr_creditmemos&view=$col->{'Related_ID_products'}"><img src='$va{'imgurl'}/$usr{'pref_style'}/b_view.gif' title='View' alt='' border='0'></a>\n|;
					$va{'searchresults'} .= "<br>". &format_sltvid($col->{'ID_products'},0,1) ."</td>\n";		
					
					$va{'searchresults'} .= "  <td class='smalltext' valign='top'>$cmname</td>\n";
					$va{'searchresults'} .= "  <td class='smalltext' valign='top'>---</td>\n";

					if ($col->{'Status'} eq 'Inactive'){
							$decor = " style=' text-decoration: line-through'";
					}else{
							$decor ='';
					}
				
					$va{'searchresults'} .= "  <td class='smalltext' align='right' valign='top' $decor>".&format_price($unit_price)."</td>\n";
					$va{'searchresults'} .= "  <td class='smalltext' align='right' valign='top' $decor>".&format_price(($col->{'Discount'}*-1))."</td>\n";
					$va{'searchresults'} .= "  <td class='smalltext' align='right' valign='top' $decor>".&format_price($col->{'Shipping'} + $col->{'ShpTax'})."</td>\n";
					$va{'searchresults'} .= "  <td class='smalltext' align='right' valign='top' $decor>".&format_number($col->{'Quantity'})."</td>\n";
					$va{'searchresults'} .= "  </td>\n<td class='smalltext' align='right' valign='top' $decor nowrap>".&format_price($total_price)."</td>\n";
					$va{'searchresults'} .= "</tr>\n";	
				
					my ($sth2) = &Do_SQL("SELECT 
											ID_products
											, ID_parts
											, Quantity
											, CONCAT(Name,' / ',Model)AS Name
										FROM sl_creditmemos_products 
										INNER JOIN sl_parts 
											ON ID_products - 400000000 = ID_parts 
										WHERE ID_creditmemos = '". $col->{'Related_ID_products'} ."' 
											AND sl_creditmemos_products.Status = 'Active';");

					while ($tmp = $sth2->fetchrow_hashref){

						for my $i(1..$tmp->{'Quantity'}){
				
							$va{'searchresults'} .= qq|
							<tr bgcolor='$c[$d]'>
							<td class="smalltext" nowrap $style valign="top" align="right"  onmouseover='m_over(this)' onmouseout='m_out(this)' OnClick="trjump('/cgi-bin/mod/$usr{'application'}/dbman?cmd=opr_parts&view=$tmp->{'ID_parts'}')"><img src="$va{'imgurl'}/$usr{'pref_style'}/tri.gif" border="0"> |.
							&format_sltvid($tmp->{'ID_products'}).qq|</td>
							<td class="smalltext" $style valign="top">|.$tmp->{'Name'}.qq|</td>
							<td class="smalltext" $style valign="top">---</td>
							<td class="smalltext">---</td>
							<td class="smalltext" $style valign="top">---</td>
							<td class="smalltext" colspan="4"></td>
							</tr>\n|;

						}
					}
				}
			}else{
				####################################################
				####################################################
				####################
				#################### WHOLESALE
				####################
				####################################################
				####################################################
				
				$sku_id_p=$col->{'Related_ID_products'}-400000000;
				$sku_id_e=$col->{'Related_ID_products'};
				$sku_id_d=format_sltvid($col->{'Related_ID_products'});
				
				if ($col->{'Status'} ne 'Inactive'){

					$tot_qty += $col->{'Quantity'};
					$tot_ord += $total_price; #$col->{'SalePrice'};

				}

				if(substr($col->{'Related_ID_products'},0,1) == 6){

	      			(substr($col->{'Related_ID_products'},0,1) == 6) and ($col->{'Related_ID_products'} = substr($col->{'Related_ID_products'},5));
					$va{'searchresults'} .= "<tr bgcolor='$c[$d]' onmouseover='m_over(this)' onmouseout='m_out(this)'>\n";
					$va{'searchresults'} .= " <td class='smalltext' valign='top'>";
					if ((!$col->{'ShpDate'} or $col->{'ShpDate'} eq '0000-00-00') and $col->{'Status'} eq 'Active'){
						#$va{'searchresults'} .= qq| <a href="/cgi-bin/mod/$usr{'application'}/dbman?cmd=opr_orders&view=$in{'id_orders'}&tab=1&drop=$col->{'ID_orders_products'}"><img src='$va{'imgurl'}/$usr{'pref_style'}/b_drop.png' title='Drop' alt='' border='0'></a>|;
					}
	
					$va{'searchresults'} .= qq| <a href="/cgi-bin/mod/$usr{'application'}/dbman?cmd=$linkser&view=$col->{'Related_ID_products'}"><img src='$va{'imgurl'}/$usr{'pref_style'}/b_view.gif' title='View' alt='' border='0'></a>|;
					my ($sth5) = &Do_SQL("SELECT * FROM sl_services WHERE ID_services = '$col->{'Related_ID_products'}' ;");
					$serdata = $sth5->fetchrow_hashref;
					$col->{'SerialNumber'}='';
					$col->{'ShpProvider'}='';
					$col->{'Tracking'}='';
					$col->{'ShpDate'}='';
					$va{'searchresults'} .= "<br>".&format_sltvid(600000000+$col->{'Related_ID_products'})."</td>\n";		
					$va{'searchresults'} .= "  <td class='smalltext'>$tmp{'model'}<br>".substr($serdata->{'Name'},0,30)."</td>\n";
					$va{'searchresults'} .= "  <td class='smalltext' valign='top'>".&build_tracking_link($col->{'Tracking'},$col->{'ShpProvider'},$col->{'ShpDate'},600000000+$col->{'Related_ID_products'})."</td>\n";			
					if ($col->{'Status'} eq 'Inactive'){
							$decor = " style=' text-decoration: line-through'";
					}else{
							$decor ='';
					}

					$va{'searchresults'} .= "  <td class='smalltext' align='right' valign='top' $decor>".&format_price($unit_price)."</td>\n";
					$va{'searchresults'} .= "  <td class='smalltext' align='right' valign='top' $decor>".&format_price(($col->{'Discount'}*-1))."</td>\n";
					$va{'searchresults'} .= "  <td class='smalltext' align='right' valign='top' $decor>N/A&nbsp;&nbsp;&nbsp;</td>\n";
					$va{'searchresults'} .= "  <td class='smalltext' align='right' valign='top' $decor>".&format_number($col->{'Quantity'}). "</td>\n";
					$va{'searchresults'} .= "  <td class='smalltext' align='right' valign='top' $decor nowrap>".&format_price($total_price);
					#Se comenta edici�n de productos
					if (&check_permissions('edit_order_edit_price','','')){
						$va{'searchresults'} .= qq| <div id="divpayment$rec->{'ID_orders_products'}"><a href="#tabs" onClick="popup_show('ajax_windows', 'ajax_drag', 'ajax_exit', 'element-right', -1, -1,'tabs');loadDoc('/cgi-bin/common/apps/ajaxbuild?ajaxbuild=edit_products&id_orders=$col->{'ID_orders'}&id_orders_products=$col->{'ID_orders_products'}&cmd=$in{'cmd'}&script_url=/cgi-bin/mod/$usr{'application'}/dbman');"><img src='$va{'imgurl'}/$usr{'pref_style'}/b_edit.png' title='Edit In Clean up Mode' alt='' border='0'/></a></div>|;
					}
					$va{'searchresults'} .= "</td>\n";
					$va{'searchresults'} .= "</tr>\n";

				}elsif(substr($col->{'ID_products'},0,1) == 8){

					my ($sth5) = &Do_SQL("SELECT ID_creditmemos FROM sl_creditmemos_payments WHERE ID_orders_products_added = '$col->{'ID_orders_products'}' ;");
					$col->{'ID_creditmemos'} = $sth5->fetchrow();
					$va{'searchresults'} .= "<tr bgcolor='$c[$d]' onmouseover='m_over(this)' onmouseout='m_out(this)'>\n";
					$va{'searchresults'} .= " <td class='smalltext' valign='top'>";
					$va{'searchresults'} .= qq| <a href="/cgi-bin/mod/$usr{'application'}/dbman?cmd=opr_creditmemos&&view=$col->{'ID_creditmemos'}"><img src='$va{'imgurl'}/$usr{'pref_style'}/b_view.gif' title='View' alt='' border='0'></a>| if ($col->{'ID_creditmemos'}>0);
					$va{'searchresults'} .= "<br>".&format_sltvid($col->{'ID_products'})."</td>\n";		
					$va{'searchresults'} .= "  <td class='smalltext'>Credit Memo : $col->{'ID_creditmemos'}</td>\n";
					$va{'searchresults'} .= "  <td class='smalltext' valign='top'></td>\n";			
					if ($col->{'Status'} eq 'Inactive'){
							$decor = " style=' text-decoration: line-through'";
					}else{
							$decor ='';
					}
		
					$va{'searchresults'} .= "  <td class='smalltext' align='right' valign='top' $decor>".&format_price($unit_price)."</td>\n";
					$va{'searchresults'} .= "  <td class='smalltext' align='right' valign='top' $decor>".&format_price(($col->{'Discount'}*-1))."</td>\n";
					$va{'searchresults'} .= "  <td class='smalltext' align='right' valign='top' $decor>N/A&nbsp;&nbsp;&nbsp;</td>\n";
					$va{'searchresults'} .= "  <td class='smalltext' align='right' valign='top' $decor>".&format_number($col->{'Quantity'})."</td>\n";
					$va{'searchresults'} .= "  <td class='smalltext' align='right' valign='top' $decor nowrap>".&format_price($total_price);
					$va{'searchresults'} .= "</td>\n";
					$va{'searchresults'} .= "</tr>\n";

						my ($sthk) = &Do_SQL("SELECT * FROM sl_skus WHERE ID_sku_products='$col->{'ID_products'}'");
				}else{

					my (%tmp);
					$va{'searchresults'} .= "<tr bgcolor='$c[$d]' onmouseover='m_over(this)' onmouseout='m_out(this)'>\n";
					$va{'searchresults'} .= " <td class='smalltext' valign='top'>";

	            	### Products
	            	$va{'searchresults'} .= qq| <a href="/cgi-bin/mod/$usr{'application'}/dbman?cmd=$linkparts&&view=$sku_id_p"><img src='$va{'imgurl'}/$usr{'pref_style'}/b_view.gif' title='View' alt='' border='0'></a>|;
	            	$va{'searchresults'} .= qq| <a href="/cgi-bin/mod/$usr{'application'}/dbman?cmd=$linkpack&view=$in{'id_orders'}&ID_orders_products=$col->{'ID_orders_products'}&choices=$choices"><img src='$va{'imgurl'}/$usr{'pref_style'}/b_packinglist.gif' title='Packing List' alt='' border='0'></a>|;
	            	$va{'searchresults'} .= "<br>".&format_sltvid($col->{'Related_ID_products'});
					$va{'searchresults'} .= "</td>\n";
					(!$col->{'SerialNumber'}) and ($col->{'SerialNumber'} = '---');
	
					($status,%tmp) = &load_product_info($sku_id_p);
					&load_cfg('sl_orders');
					$cadname=&load_name('sl_parts','ID_parts',$sku_id_p,'Name');
						$cadname=substr($cadname,0,30);
					$cadmodel=&load_name('sl_parts','ID_parts',$sku_id_p,'Model');

						if ($col->{'Amazon_ID_products'}){
							my ($sthAzn) = &Do_SQL("SELECT Name FROM cu_products_amazon WHERE ID_products_amazon = '$col->{'Amazon_ID_products'}';");
							$cadname = $sthAzn->fetchrow_array();
							$cadname=substr($cadname,0,30);
							$cadname = qq|<a href="/cgi-bin/mod/$usr{'application'}/dbman?cmd=mer_products_amazon&view=$col->{'Amazon_ID_products'}">$cadname</a>|;
						}
					
						$va{'searchresults'} .= "  <td class='smalltext' valign='top'>$cadmodel<br>".$cadname." ".$choices."</td>\n";
					$va{'searchresults'} .= "  <td class='smalltext' valign='top'>".&build_tracking_link($col->{'Tracking'},$col->{'ShpProvider'},$col->{'ShpDate'},$col->{'ID_products'}).&remove_tracking($col->{'Tracking'},$col->{'ShpProvider'},$col->{'ShpDate'},$col->{'ID_orders_products'})."</td>\n";
	
					if ($col->{'Status'} eq 'Inactive'){
						$decor = " style=' text-decoration: line-through'";
					}else{
						$decor ='';
					}
					
					my $split_qty = '';
					if ($in{'status'} ne 'Shipped' and &check_permissions('edit_order_wholesale_ajaxmode','','')) {
						$split_qty = qq| <div id="divpayment$rec->{'ID_orders_products'}"><a href="#tabs" onClick="popup_show('ajax_windows', 'ajax_drag', 'ajax_exit', 'element-right', -1, -1,'tabs');loadDoc('/cgi-bin/common/apps/ajaxbuild?ajaxbuild=split_products_qty&id_orders=$col->{'ID_orders'}&id_orders_products=$col->{'ID_orders_products'}&cmd=$in{'cmd'}&script_url=/cgi-bin/mod/$usr{'application'}/dbman&current_qty=$col->{'Quantity'}&date=$col->{'Date'}&time=$col->{'Time'}');"><img src='$va{'imgurl'}/$usr{'pref_style'}/b_edit.png' title='Edit In Clean up Mode' alt='' border='0'></a></div>|;
					}
					
					$add_original_qty = '';
					# if($cfg{'productos_create_newline'}){
					# 	$add_original_qty = " (". &format_number($col->{'OriginalQty'}) . ")";
					# }
					$va{'searchresults'} .= "  <td class='smalltext' align='right' valign='top' $decor>".&format_price($unit_price)."</td>\n";
					$va{'searchresults'} .= "  <td class='smalltext' align='right' valign='top' $decor>".&format_price(($col->{'Discount'}*-1))."</td>\n";
					$va{'searchresults'} .= "  <td class='smalltext' align='right' valign='top' $decor>".&format_price($col->{'Shipping'} + $col->{'ShpTax'})."";
					$va{'searchresults'} .= "  <td class='smalltext' align='right' valign='top' $decor>".&format_number($col->{'Quantity'}). $add_original_qty . $split_qty. "</td>\n";
					$va{'searchresults'} .= "  </td>\n<td class='smalltext' align='right' valign='top' $decor nowrap>".&format_price($total_price);
					#Se comenta edici�n de productos
					if (&check_permissions('edit_order_edit_price','','')){
						$va{'searchresults'} .= qq| <div id="divpayment$rec->{'ID_orders_products'}"><a href="#tabs" onClick="popup_show('ajax_windows', 'ajax_drag', 'ajax_exit', 'element-right', -1, -1,'tabs');loadDoc('/cgi-bin/common/apps/ajaxbuild?ajaxbuild=edit_products&id_orders=$col->{'ID_orders'}&id_orders_products=$col->{'ID_orders_products'}&cmd=$in{'cmd'}&script_url=/cgi-bin/mod/$usr{'application'}/dbman');"><img src='$va{'imgurl'}/$usr{'pref_style'}/b_edit.png' title='Edit In Clean up Mode' alt='' border='0'></a></div>|;
					}
					$va{'searchresults'} .= "</td>\n";
					$va{'searchresults'} .= "</tr>\n";	
				}
			}
		}

		$va{'searchresults'} .= qq|
			<tr>
				<td colspan='7' class='smalltext' align="right">|.&trans_txt('mer_vpo_total').qq|</td>
				<td align="right" class='smalltext' style="border-top:thick double #808080;">|.&format_price($tot_ord).qq|</td>
			</tr>\n|;
	}else{
		$va{'pageslist'} = 1;
		$va{'searchresults'} = qq|
			<tr>
				<td colspan='8' align="center">|.&trans_txt('search_nomatches').qq|</td>
			</tr>\n|;
	}
}

sub load_tabs2{
########################
##   Tab2.- Payments  ##
########################
# --------------------------------------------------------
# Forms Involved: 
# Created on: 11/13/08 13:21:17
# Author: MCC C. Gabriel Varela S.
# Description :   
# Parameters :
# Last Modified on: 12/04/08 09:21:09
# Last Modified by: MCC C. Gabriel Varela S: Se comenta edici�n de pagos.
# Last Modified on: 12/10/08 16:48:04
# Last Modified by: MCC C. Gabriel Varela S: Se hace que los status "no v�lidos" se tomen en cuenta y que se consideren como Cancelled
# Last Modified on: 12/15/08 17:29:27
# Last Modified by: MCC C. Gabriel Varela S: Se deshabilita drop
# Last Modified RB: 12/18/08  12:36:25 - Added 30 days older capture validation
# Last Modified on: 12/29/08 17:54:14
# Last Modified by: MCC C. Gabriel Varela S: Se hace que al cambiar de tarjeta de cr�dito, no se cancelen los pagos Financed
# Last Modified on: 01/06/09 15:19:56
# Last Modified by: MCC C. Gabriel Varela S: Se habilita edici�n de pagos s�lo si est� habilitada por sistema old_edition
# Last Modified on: 01/07/09 12:52:49
# Last Modified by: MCC C. Gabriel Varela S: Se modifica para ver que se puedan editar los pagos si el usuario tiene usergroup = 1
# Last Modification by JRG : 03/05/2009 : Se agrega el log
# Last Modified RB: 03/19/09  11:44:23 -- Se habilitan imagenes pare diferenciar pagos autorizados/capturados a usuarios operadores.
# Last Modified RB: 09/24/09  13:53:39 -- Solamente el area de finanzas y developers pueden capturas creditos. Se agrega el color de pagos autorizados/capturados a todos los tipos de pago.
# Last Modified RB: 11/29/2010  18:45:00 -- Se agrega comando para autorizacion de pagos paypal
# Last Time Modified by RB on 18/10/2011: Se agrego mascara para cc number
	$va{'display_orders_options'} = ($cfg{'display_orders_options'})? '' : 'display:none;';
	## Transform the order to flexipay
	if($in{'action'} eq 'add_flexipay'){
		#JRG start 24-06-2008 modify vars to change payments
		if($in{'flexipays'} > 0 && $in{'flexipays'} <= 24){
			if($in{'chk_accept'} eq "yes"){
				## Set the past payments inactive
				my ($sth) = &Do_SQL("UPDATE sl_orders_payments SET Status = 'Cancelled' WHERE ID_orders = '$in{'id_orders'}'");
				&auth_logging('opr_orders_pay_updated',$in{'id_orders'});
			}
			&loaddatapayment($in{'id_orders'});	
			if($in{'firstpay'}){
				$fpdate = $in{'firstpay'};
			} else {
				my ($std) = &Do_SQL("SELECT CURDATE()");
				$fpdate = $std->fetchrow;										
			}
			for (1..9){
				$query .= ',PmtField'.$_.' = \''.$in{'pmtfield'.$_}.'\'';
			}
			## Build the new payments
			for(1..$in{'flexipays'}){
				($in{'typefp'} eq 'MONTH') and ($interval = '1*'.$_.' MONTH') and ($dpay = 30);
				($in{'typefp'} eq 'DAY') and ($interval = '15*'.$_.' DAY') and ($dpay = 15);;
				my ($sth) = &Do_SQL("INSERT INTO sl_orders_payments SET ID_orders = $in{'id_orders'},Type = '$in{'type'}' $query, Amount = '$in{'payment'}', PaymentDate = '$fpdate',Status= 'Approved',PostedDate=CURDATE(),Date=CURDATE(),Time=NOW(),ID_admin_users='$usr{'id_admin_users'}';");
				&auth_logging('orders_payments_added',$sth->{'mysql_insertid'});	
				$std = &Do_SQL("SELECT DATE_ADD(CURDATE(),INTERVAL $interval)");
				$fpdate = $std->fetchrow;											
			}
			## Set the dayspay to sl_orders
			&Do_SQL("UPDATE sl_orders SET dayspay = $dpay WHERE ID_orders = $in{'id_orders'}");
			&auth_logging('opr_orders_updated',$in{'id_orders'});
		}
		if ($err){
			$va{'tabmessages'} = &trans_txt('reqfields');
		}
		#JRG end 24-06-2008	
	}elsif ($in{'action'} eq 'add_chk'){
		####
		#### Validate Checks
		####
		$in{'year'} = int($in{'year'});
		if ($in{'month'} and $in{'day'} and $in{'year'}){
			$in{'pmtfield5'} = "$in{'month'}-$in{'day'}-$in{'year'}";	
		}
		$in{'pmtfield9'} = int($in{'pmtfield9'});
		for my $i(1..9){
			if (!$in{'pmtfield'.$i}){
				$error{'pmtfield'.$i} = &trans_txt('required');
				++$err;
			}
		}
		if (length($in{'pmtfield9'}) ne 10){
			$error{'pmtfield9'} = &trans_txt('invalid');
			++$err;
		}
		if ($in{'year'} > 2000 or $in{'year'}<1900){
			$error{'pmtfield5'} = &trans_txt('invalid');
			++$err;
		}
		
		#$in{'amount'} = &format_sltvprice($in{'amount'});

		if (!$in{'amount'}){
			$error{'amount'} = &trans_txt('invalid');
			++$err;
		}
		if ($err){
			$va{'autorun_js'} = 'add_chk();';
			$va{'tbmessage'} = &trans_txt('reqfields');
		}else{
			for my $i(1..9){
				$query .= "PmtField$i='".&filter_values($in{'pmtfield'.$i})."',";
			}
			chop($query);
			my ($sth) = &Do_SQL("INSERT INTO sl_orders_payments SET ID_orders='$in{'id_orders'}',Type='Check',$query ,Amount='$in{'amount'}',Status='Pending',PostedDate=CURDATE(), Date=Curdate(),Time=NOW(),ID_admin_users='$usr{'id_admin_users'}'");
			&auth_logging('opr_orders_payadded_chk',$in{'id_orders'});
			$va{'tabmessages'} = &trans_txt('opr_orders_payadded_chk');
		}
		$in{'tabs'} = 1;
	}elsif ($in{'action'} eq 'add_cc'){
		####
		#### Validate Credit Card
		####
		$in{'pmtfield4'} = "$in{'month'}$in{'year'}";
		$in{'pmtfield6'} = int($in{'pmtfield6'});
		for my $i(1..6){
			if (!$in{'pmtfield'.$i}){
				$error{'pmtfield'.$i} = &trans_txt('required');
				++$err;
			}
			$cses{'pmtfield'.$i} = $in{'pmtfield'.$i};
		}
		if (length($in{'pmtfield6'}) ne 10){
			$error{'pmtfield6'} = &trans_txt('invalid');
		}
		
		#$in{'amount'} = &format_sltvprice($in{'amount'});
		if (!$in{'amount'}){
			$error{'amount'} = &trans_txt('requires');
			++$err;
		}
		if (!$in{'paymentdate'}){
			$error{'paymentdate'} = &trans_txt('requires');
			++$err;
		}
		if ($err){
			$va{'autorun_js'} = 'add_cc()';
			$va{'tbmessage'} = &trans_txt('reqfields');
		}else{
			for my $i(1..9){
				$query .= "PmtField$i='".&filter_values($in{'pmtfield'.$i})."',";
			}
			chop($query);
			my ($sth) = &Do_SQL("INSERT INTO sl_orders_payments SET ID_orders='$in{'id_orders'}',Type='Credit-Card',$query ,Paymentdate='".&filter_values($in{'paymentdate'})."',Amount='$in{'amount'}',Status='Approved',AuthCode='0000',PostedDate=CURDATE(), Date=Curdate(),Time=NOW(),ID_admin_users='$usr{'id_admin_users'}'");
			&auth_logging('opr_orders_payadded_cc',$in{'id_orders'});
			$va{'tabmessages'} = &trans_txt('opr_orders_payadded_cc');
		}
		$in{'tabs'} = 1;
	#JRG start 25-08-2008 add charges
	}elsif ($in{'action'} eq 'add_chrg'){
		if($in{'id_orders_payments'} && $in{'amount'} && $in{'id_orders'}){
			if($in{'amount'} =~ m/^[0-9]+(\.[0-9]+)?$/){
				my ($sth) = &Do_SQL("SELECT COUNT(*) FROM sl_orders_payments WHERE id_orders_payments='$in{'id_orders_payments'}';");
				$va{'matches'} = $sth->fetchrow;
				if($va{'matches'}==1){
					my ($sth) = &Do_SQL("SELECT * FROM sl_orders_payments WHERE id_orders_payments='$in{'id_orders_payments'}';");
					$rec = $sth->fetchrow_hashref;
					for my $i(1..9){
						$query .= "PmtField$i='".&filter_values($rec->{'PmtField'.$i})."',";
					}
					chop($query);
					my ($sth) = &Do_SQL("INSERT INTO sl_orders_payments SET ID_orders='$in{'id_orders'}',Type='Credit-Card',$query ,Amount='$in{'amount'}',Status='Approved',AuthCode='0000', PostedDate=CURDATE(),Date=Curdate(),Time=NOW(),ID_admin_users='$usr{'id_admin_users'}'");
					&auth_logging('orders_payments_added',$sth->{'mysql_insertid'});
				}
			} else {
				$error{'amount'} = &trans_txt('invalid');
				$va{'tabmessage'} = &trans_txt('reqfields');
			}
		} else{
			$va{'tabmessage'} = &trans_txt('reqfields');
		}
	#JRG end 25-08-2008 add charges
	########################
	##MFS BUY BACK##
	########################
	} elsif($in{'action'} eq 'mfs_buyback'){
		$newstatus= "Approved";
		my ($sth) = &Do_SQL("SELECT *, SUM(Amount) as sum_fin FROM sl_orders_payments WHERE id_orders='$in{'id_orders'}' AND Status='Financed' GROUP BY ID_orders");
		$rec = $sth->fetchrow_hashref;
		$old_query = ",Type='$rec->{'Type'}',PmtField1='$rec->{'PmtField1'}',PmtField2='$rec->{'PmtField2'}',PmtField3='$rec->{'PmtField3'}',PmtField4='$rec->{'PmtField4'}',PmtField5='$rec->{'PmtField5'}',PmtField6='$rec->{'PmtField6'}',PmtField7='$rec->{'PmtField7'}',PmtField8='$rec->{'PmtField8'}',PmtField9='$rec->{'PmtField9'}' ";
		$sum_fin = $rec->{'sum_fin'};
		if($sum_fin){
			my ($sth) = &Do_SQL("INSERT INTO sl_orders_payments SET ID_orders='$in{'id_orders'}',Amount='$sum_fin',Status='Financed',Captured='Yes',CapDate='$rec->{'CapDate'}',PostedDate=CURDATE(),Date=Curdate(),Time=NOW(),ID_admin_users='$usr{'id_admin_users'}'".$old_query);
			&auth_logging('orders_payments_added',$sth->{'mysql_insertid'});
			my ($sth) = &Do_SQL("SELECT last_insert_id(ID_orders_payments)as last from sl_orders_payments order by last desc limit 1");
			$last_created = $sth->fetchrow;
			$sum_fin_neg = $rec->{'sum_fin'}*-1;
			my ($sth) = &Do_SQL("INSERT INTO sl_orders_payments SET ID_orders='$in{'id_orders'}',Amount='$sum_fin_neg',Status='Counter Finance',Captured='Yes',CapDate='$rec->{'CapDate'}',PostedDate=CURDATE(),Date=Curdate(),Time=NOW(),ID_admin_users='$usr{'id_admin_users'}'".$old_query);
			&auth_logging('orders_payments_added',$sth->{'mysql_insertid'});
			my ($sth) = &Do_SQL("UPDATE sl_orders_payments SET Status='$newstatus',CapDate=NULL,Captured='No' WHERE Status='Financed' AND ID_orders='$in{'id_orders'}' AND ID_orders_payments<>$last_created");
			&auth_logging('opr_orders_pay_updated',$in{'id_orders'});
		}
	########################
	##MFS FPD##
	########################						
	} elsif($in{'action'} eq 'mfs_fpd'){
		my ($sthr) = &Do_SQL("SELECT COUNT(*) FROM sl_returns, sl_orders_products WHERE sl_returns.id_orders_products=sl_orders_products.id_orders_products AND sl_orders_products.id_orders='$in{'id_orders'}';");
		$returns = $sthr->fetchrow;
		if($returns){
			$newstatus= "Cancelled";
		} else {
			$newstatus= "Approved";
		}
		my ($sth) = &Do_SQL("SELECT *, SUM(Amount) as sum_fin FROM sl_orders_payments WHERE id_orders='$in{'id_orders'}' AND Status='Financed' GROUP BY ID_orders");
		$rec = $sth->fetchrow_hashref;
		$old_query = ",Type='$rec->{'Type'}',PmtField1='$rec->{'PmtField1'}',PmtField2='$rec->{'PmtField2'}',PmtField3='$rec->{'PmtField3'}',PmtField4='$rec->{'PmtField4'}',PmtField5='$rec->{'PmtField5'}',PmtField6='$rec->{'PmtField6'}',PmtField7='$rec->{'PmtField7'}',PmtField8='$rec->{'PmtField8'}',PmtField9='$rec->{'PmtField9'}' ";
		$sum_fin = $rec->{'sum_fin'};
		if($sum_fin){
			my ($sth) = &Do_SQL("INSERT INTO sl_orders_payments SET ID_orders='$in{'id_orders'}',Amount='$sum_fin',Status='Financed',Captured='Yes',CapDate='$rec->{'CapDate'}',PostedDate=CURDATE(),Date=Curdate(),Time=NOW(),ID_admin_users='$usr{'id_admin_users'}'".$old_query);
			&auth_logging('orders_payments_added',$sth->{'mysql_insertid'});
			my ($sth) = &Do_SQL("SELECT last_insert_id(ID_orders_payments)as last from sl_orders_payments order by last desc limit 1");
			$last_created = $sth->fetchrow;
			$sum_fin_neg = $rec->{'sum_fin'}*-1;
			my ($sth) = &Do_SQL("INSERT INTO sl_orders_payments SET ID_orders='$in{'id_orders'}',Amount='$sum_fin_neg',Status='Counter Finance',Captured='Yes',CapDate='$rec->{'CapDate'}',PostedDate=CURDATE(),Date=Curdate(),Time=NOW(),ID_admin_users='$usr{'id_admin_users'}'".$old_query);
			&auth_logging('orders_payments_added',$sth->{'mysql_insertid'});
			my ($sth) = &Do_SQL("UPDATE sl_orders_payments SET Status='$newstatus',CapDate=NULL,Captured='No' WHERE Status='Financed' AND ID_orders='$in{'id_orders'}' AND ID_orders_payments<>$last_created");						
			&auth_logging('opr_orders_pay_updated',$in{'id_orders'});
			my ($sth) = &Do_SQL("UPDATE sl_orders SET StatusPay='On Collection' WHERE ID_orders='$in{'id_orders'}'");
			&auth_logging('opr_orders_updated',$in{'id_orders'});
			$in{'statuspay'} = 'On Collection';
		}
	########################
	##MFS NA##
	########################						
	} elsif($in{'action'} eq 'mfs_na'){
		$newstatus= "Approved";
		my ($sth)=&Do_SQL("UPDATE sl_orders_payments SET Status='$newstatus', CapDate=NULL, Captured='No' WHERE id_orders='$in{'id_orders'}' AND Status='Financed'");
		&auth_logging('opr_orders_pay_updated',$in{'id_orders'});
	########################
	##Change CC##
	########################
	}elsif($in{'action'} eq 'changecc'){
		$newstatus= "Cancelled";
		
		if($in{'changepaymentss'}) {
			my ($mod);
			$mod = '';
			
			#Primero se hace el select
			my ($sloc)=&Do_SQL("SELECT * FROM sl_orders_payments WHERE ID_orders_payments IN ($in{'changepaymentss'}) $mod ");
			my ($recloc);

			while($recloc=$sloc->fetchrow_hashref()) {
				#Despu�s se hace el insert
				my($sth) = &Do_SQL("INSERT INTO sl_orders_payments SET ID_orders='$recloc->{'ID_orders'}',Type='Credit-Card',PmtField1='$in{'pmtfield1_new'}',PmtField2='$in{'pmtfield2_new'}',PmtField3='$in{'pmtfield3_new'}',PmtField4='$in{'month_new'}$in{'year_new'}',PmtField5='$in{'pmtfield5_new'}',PmtField6='$recloc->{'PmtField6'}',PmtField7='$recloc->{'PmtField7'}',PmtField8='$recloc->{'PmtField8'}',PmtField9='$recloc->{'PmtField9'}',PmtField10='03',Amount='$recloc->{'Amount'}',Paymentdate='$recloc->{'Paymentdate'}',PostedDate='$recloc->{'PostedDate'}',Status='Pending',Date=Curdate(),Time=NOW(),ID_admin_users='$usr{'id_admin_users'}'");
				&auth_logging('orders_payments_added',$sth->{'mysql_insertid'});
			}

			#Y al �ltimo el update
			&Do_SQL("UPDATE sl_orders_payments SET Status='$newstatus' WHERE ID_orders_payments in ($in{'changepaymentss'}) $mod and Status!='Financed'");
			&auth_logging('bulk_opr_orders_pay_updated',$in{'changepaymentss'});
		
		}
		
	}elsif ($in{'drop'}){
		my ($sth) = &Do_SQL("UPDATE sl_orders_payments SET Status='Cancelled',AuthCode='' WHERE ID_orders='$in{'id_orders'}' AND ID_orders_payments='$in{'drop'}'");;
		&auth_logging('opr_orders_paydroped',$in{'id_orders'});
		$va{'tabmessages'} = &trans_txt('opr_orders_paydroped');
		$in{'tabs'} = 1;
	}
	
#############################################
#############################################
#########	Payments List	      #######
#############################################
#############################################
	
	my ($tot_pay);
	my $num_cols = 6;
	my (@c) = split(/,/,$cfg{'srcolors'});
	my ($sth) = &Do_SQL("SELECT COUNT(*) FROM sl_orders_payments WHERE ID_orders='$in{'id_orders'}'");
	$va{'matches'} = $sth->fetchrow;

	if($va{'matches'}>0){

        my ($sth) = &Do_SQL("SELECT * FROM sl_orders_payments WHERE ID_orders='$in{'id_orders'}'  ORDER BY Status, Date DESC,CapDate DESC,Paymentdate DESC;");
		while ($rec = $sth->fetchrow_hashref){


			my $ajaxcmd_auth = 'creditcard';
			my $ajaxcmd_sale = 'ccsale';
			my $ajaxcmd_capture = 'capture';
			my $is_chargeback = 0;
			my $set_form2 = $rec->{'Reason'} =~ /Exchange|Refund/ ? '&format=2' : '';

			$d = 1 - $d;
			
			#####
			##### Captcolor debe ser una imagen en lugar de un color
			#####
			
			my $captcolor = '';
			$captcolor = 'color:blue;'	if($rec->{'AuthCode'} and $rec->{'AuthCode'} ne '' and $rec->{'AuthCode'} ne '0000' and (!$rec->{'Captured'} or $rec->{'Captured'} eq 'Yes') and (!$rec->{'CapDate'} or $rec->{'CapDate'} eq '' or $rec->{'CapDate'}eq'0000-00-00')); 
			$captcolor = 'color:green;'	if $rec->{'Captured'} eq 'Yes';
			
			my ($ccmethod) = &load_name('sl_orders_payments','ID_orders_payments',$rec->{'ID_orders_payments'},'PmtField3');	
			($ccmethod eq 'PayPal') and ($ajaxcmd_auth .= '_paypal') and ($ajaxcmd_sale .= '_paypal') and ($ajaxcmd_capture .= '_paypal');


			if ($rec->{'Status'} eq 'Cancelled' or $rec->{'Status'} eq 'Order Cancelled'){

				$decor = " style=' text-decoration: line-through'";

			}else{

				$decor ='';
				$tot_pay += $rec->{'Amount'} if ($rec->{'Status'} ne 'Order Cancelled' and $rec->{'Status'} ne 'Cancelled');
				$strt .= "$rec->{'ID_orders_payments'} - $rec->{'Amount'}<br>";
			}


			# Detail of the Banks Movements
			my ($sth_banksmovs) = &Do_SQL("SELECT sl_banks.BankName, sl_banks.Currency, sl_banks.SubAccountOf, sl_banks_movements.BankDate, sl_banks_movements.ID_banks_movements, sl_banks_movements.RefNum, sl_banks_movements.Memo
				FROM sl_banks_movements INNER JOIN sl_banks_movrel USING(ID_banks_movements) INNER JOIN sl_banks USING(ID_banks) WHERE tablename = 'orders_payments'
				AND tableid = '".$rec->{'ID_orders_payments'}."';");
			$rec_banksmovs = $sth_banksmovs->fetchrow_hashref();


			if ($rec_banksmovs->{'ID_banks_movements'}){

				########################################
				########################################
				########################################
				########
				######## Bank Movements
				########
				########################################
				########################################
				########################################

				$num_cols = 9;
				$va{'searchresults'} .= "<tr>\n";
				$va{'searchresults'} .= "   <td class='menu_bar_title'>Type</td>\n";
				$va{'searchresults'} .= "   <td class='menu_bar_title'>ID</td>\n";
				$va{'searchresults'} .= "	<td class='menu_bar_title'>Bank Date</td>\n";	
				$va{'searchresults'} .= "   <td class='menu_bar_title'>Sub Account Of</td>\n";
				$va{'searchresults'} .= "   <td class='menu_bar_title'>Bank Name</td>\n";
				$va{'searchresults'} .= "	<td class='menu_bar_title'>Currency</td>\n";	
				$va{'searchresults'} .= "   <td class='menu_bar_title'>Ref Num</td>\n";
				$va{'searchresults'} .= "   <td class='menu_bar_title'>Memo</td>\n";
				$va{'searchresults'} .= "	<td class='menu_bar_title'>Status</td>\n";
				$va{'searchresults'} .= "	<td class='menu_bar_title' align='right'>Amount</td>\n";
				$va{'searchresults'} .= " </tr>\n";

				$va{'searchresults'} .= " <tr bgcolor='$c[$d]' onmouseover='m_over(this)' onmouseout='m_out(this)'>\n";
				$va{'searchresults'} .= "   <td class='smalltext' nowrap $decor>".$rec->{'Type'}."</td>";
				$va{'searchresults'} .= "   <td class='smalltext' nowrap $decor><a href=\"/cgi-bin/mod/[ur_application]/dbman?cmd=fin_banks_movements&view=".$rec_banksmovs->{'ID_banks_movements'}."\">".$rec_banksmovs->{'ID_banks_movements'}."</a></td>";
				$va{'searchresults'} .= "   <td class='smalltext' nowrap $decor>".$rec_banksmovs->{'BankDate'}."</td>";
				$va{'searchresults'} .= "   <td class='smalltext' nowrap $decor>".$rec_banksmovs->{'SubAccountOf'}."</td>";
				$va{'searchresults'} .= "   <td class='smalltext' nowrap $decor>".$rec_banksmovs->{'BankName'}."</td>";
				$va{'searchresults'} .= "   <td class='smalltext' nowrap $decor>".$rec_banksmovs->{'Currency'}."</td>";
				$va{'searchresults'} .= "   <td class='smalltext' nowrap $decor>".$rec_banksmovs->{'RefNum'}."</td>";
				$va{'searchresults'} .= "   <td class='smalltext' nowrap $decor>".$rec_banksmovs->{'Memo'}."</td>";
				$va{'searchresults'} .= "   <td class='smalltext' $decor valign='top'> $rec->{'Status'}<br>$rec->{'AuthCode'}</td>\n";
				$va{'searchresults'} .= "   <td class='smalltext' $decor align='right' valign='top'> ".&format_price($rec->{'Amount'})."<br>$rec->{'Paymentdate'}<br><span style='$captcolor'>$rec->{'CapDate'}</span>\n";
				
				#Se comenta edici�n de pagos.
				if (&check_permissions('edit_order_cleanup','','')){

					$va{'searchresults'} .= qq| <div id="divpayment$rec->{'ID_orders_products'}"><a href="#tabs" onClick="popup_show('ajax_windows', 'ajax_drag', 'ajax_exit', 'element-right', -1, -1,'tabs');loadDoc('/cgi-bin/common/apps/ajaxbuild?ajaxbuild=edit_payments&id_orders=$rec->{'ID_orders'}&id_orders_payments=$rec->{'ID_orders_payments'}|. $set_form2 .qq|&cmd=$in{'cmd'}&script_url=/cgi-bin/mod/$usr{'application'}/dbman');"><img src='$va{'imgurl'}/$usr{'pref_style'}/b_edit.png' title='Edit In Clean up Mode $rec->{'Reason'}' alt='' border='0'></a></div>|;
				
				}
				
				$va{'searchresults'} .= "</td>\n";
				$va{'searchresults'} .= "</tr>\n";
			
			}elsif ($rec->{'Type'} eq "Check"){

				########################################
				########################################
				########################################
				########
				######## Check
				########
				########################################
				########################################
				########################################


				$va{'searchresults'} .= "<tr>\n";
				$va{'searchresults'} .= "   <td class='menu_bar_title'>&nbsp;</td>\n";
				$va{'searchresults'} .= "   <td class='menu_bar_title'>Name on Check</td>\n";
				$va{'searchresults'} .= "   <td class='menu_bar_title'>Routing ABA/ Account/ Chk</td>\n";
				$va{'searchresults'} .= "   <td class='menu_bar_title'>P/C</td>\n";
				$va{'searchresults'} .= "   <td class='menu_bar_title'>D.O.B<br>License/State<br>Phone</td>\n";
				$va{'searchresults'} .= "	<td class='menu_bar_title'>Status<br>Cod Auth</td>\n";
				$va{'searchresults'} .= "	<td class='menu_bar_title'>Amount</td>\n";
				$va{'searchresults'} .= "</tr>\n";
				$va{'searchresults'} .= "<tr bgcolor='$c[$d]' onmouseover='m_over(this)' onmouseout='m_out(this)'>\n";
				$va{'searchresults'} .= "   <td nowrap>";
				if ($rec->{'Status'} ne 'Cancelled' and $rec->{'Status'} ne 'Order Cancelled' and $rec->{'Status'} ne 'Void' and (($rec->{'Status'} ne 'Approved' or $rec->{'AuthCode'} eq '0000') or ($rec->{'Status'} eq 'Approved' and !$rec->{'AuthCode'}))){
					#$va{'searchresults'} .= qq| <a href="/cgi-bin/mod/$usr{'application'}/dbman?cmd=opr_orders&view=$in{'id_orders'}&tab=2&drop=$rec->{'ID_orders_payments'}"><img src='$va{'imgurl'}/$usr{'pref_style'}/b_drop.png' title='Drop' alt='' border='0'></a>|;
					#$va{'searchresults'} .= qq| <a href="/cgi-bin/mod/$usr{'application'}/dbman?cmd=opr_orders&view=$in{'id_orders'}&tab=2&auth=$rec->{'ID_orders_payments'}"><img src='$va{'imgurl'}/$usr{'pref_style'}/b_pauth.gif' title='Authorize' alt='' border='0'></a>|;
					$va{'searchresults'} .= qq| <div id="divpayment$rec->{'ID_orders'}"><a href="#tabs" onClick="popup_show('ajax_windows', 'ajax_drag', 'ajax_exit', 'element-right', -1, -1,'tabs');loadDoc('/cgi-bin/common/apps/ajaxpayment?ajaxbuild=certegycheck&id_orders=$rec->{'ID_orders'}&id_orders_payments=$rec->{'ID_orders_payments'}&e=$in{'e'}');delete_div('divorder$rec->{'ID_orders'}');delete_div('divpayment$rec->{'ID_orders'}');"><img src='$va{'imgurl'}/$usr{'pref_style'}/b_pauth.gif' title='Authorize' alt='' border='0'></a></div>|;
				}
				
				$va{'searchresults'} .= "   </td>"; 
				$va{'searchresults'} .= "   <td class='smalltext' valign='top' $decor> $rec->{'PmtField1'}</td>\n";
				$va{'searchresults'} .= "   <td class='smalltext' valign='top' $decor> $rec->{'PmtField2'}<div>$rec->{'PmtField3'}</div><div>$rec->{'PmtField4'}</div>";
				$va{'searchresults'} .= "   </td>"; 
				$va{'searchresults'} .= "   <td class='smalltext' valign='top' $decor> $rec->{'PmtField8'}</td>\n";
				$va{'searchresults'} .= "   <td class='smalltext' valign='top' $decor> $rec->{'PmtField5'}<br> $rec->{'PmtField6'}<br>$rec->{'PmtField7'}<br>$rec->{'PmtField9'}</td>\n";
				$va{'searchresults'} .= "   <td class='smalltext' valign='top' $decor> $rec->{'Status'}<br>$rec->{'AuthCode'}</td>\n";							
				$va{'searchresults'} .= "   <td class='smalltext' valign='top' $decor align='right'> ".&format_price($rec->{'Amount'})."<br>$rec->{'Paymentdate'}<br><span style='$captcolor'>$rec->{'CapDate'}</span>\n";
				#Se comenta edici�n de pagos.
				if (&check_permissions('edit_order_cleanup','','')){
					$va{'searchresults'} .= qq| <div id="divpayment$rec->{'ID_orders_products'}"><a href="#tabs" onClick="popup_show('ajax_windows', 'ajax_drag', 'ajax_exit', 'element-right', -1, -1,'tabs');loadDoc('/cgi-bin/common/apps/ajaxbuild?ajaxbuild=edit_payments&id_orders=$rec->{'ID_orders'}&id_orders_payments=$rec->{'ID_orders_payments'}&cmd=$in{'cmd'}|. $set_form2 .qq|&script_url=/cgi-bin/mod/$usr{'application'}/dbman');"><img src='$va{'imgurl'}/$usr{'pref_style'}/b_edit.png' title='Edit In Clean up Mode' alt='' border='0'></a></div>|;
				}
				$va{'searchresults'} .= "</td>\n";
				$va{'searchresults'} .= "</tr>\n";


			}elsif($rec->{'Type'} eq "WesternUnion"){

				########################################
				########################################
				########################################
				########
				######## Wester Union
				########
				########################################
				########################################
				########################################


				$va{'searchresults'} .= "<tr>\n";
				$va{'searchresults'} .= "   <td class='menu_bar_title' colspan='5'>WesterUnion Payment</td>\n";
				$va{'searchresults'} .= "	<td class='menu_bar_title'>Status<br>Cod Auth</td>\n";							
				$va{'searchresults'} .= "	<td class='menu_bar_title'>Amount</td>\n";
				$va{'searchresults'} .= "</tr>\n";
				$va{'searchresults'} .= "<tr bgcolor='$c[$d]' onmouseover='m_over(this)' onmouseout='m_out(this)'>\n";
				$va{'searchresults'} .= "   <td nowrap>";
				
				if ($rec->{'Status'} ne 'Cancelled' and $rec->{'Status'} ne 'Order Cancelled' and $rec->{'Status'} ne 'Void' and ($rec->{'Status'} ne 'Approved' or $rec->{'AuthCode'} eq '0000')){
					#$va{'searchresults'} .= qq| <a href="/cgi-bin/mod/$usr{'application'}/dbman?cmd=opr_orders&view=$in{'id_orders'}&tab=2&drop=$rec->{'ID_orders_payments'}"><img src='$va{'imgurl'}/$usr{'pref_style'}/b_drop.png' title='Drop' alt='' border='0'></a>|;
				}
				
				$va{'searchresults'} .= "   </td>";
				$va{'searchresults'} .= "   <td class='smalltext' valign='top' $decor colspan='4'> No Information Required For WU Payments</td>\n";
				$va{'searchresults'} .= "   <td class='smalltext' valign='top' $decor> $rec->{'Status'}<br>$rec->{'AuthCode'}</td>\n";							
				$va{'searchresults'} .= "   <td class='smalltext' valign='top' $decor align='right'> ".&format_price($rec->{'Amount'})."<br>$rec->{'Paymentdate'}<br><span style='$captcolor'>$rec->{'CapDate'}</span></td>\n";
				$va{'searchresults'} .= "</tr>\n";	


			}elsif($rec->{'Type'} eq "Credit-Card"){


				########################################
				########################################
				########################################
				########
				######## Credit-Card
				########
				########################################
				########################################
				########################################


				$num_cols = 9;
				$va{'searchresults'} .= "<tr>\n";
				$va{'searchresults'} .= "   <td class='menu_bar_title'>Select</td>\n";
				$va{'searchresults'} .= "   <td class='menu_bar_title'>Type</td>\n";
				$va{'searchresults'} .= "   <td class='menu_bar_title' colspan='2' align='center'>Name on Card<br>Card Number</td>\n";
				$va{'searchresults'} .= "   <td class='menu_bar_title'>Exp</td>\n";
				$va{'searchresults'} .= "   <td class='menu_bar_title'>CVN</td>\n";
				$va{'searchresults'} .= "	<td class='menu_bar_title'>Status<br>Cod Auth</td>\n";			
				$va{'searchresults'} .= "	<td class='menu_bar_title'>Months</td>\n";
				$va{'searchresults'} .= "	<td class='menu_bar_title' colspan='2' align='right'>Amount</td>\n";
				$va{'searchresults'} .= " </tr>\n";
				$va{'searchresults'} .= " <tr bgcolor='$c[$d]' onmouseover='m_over(this)' onmouseout='m_out(this)'>\n";
				$va{'searchresults'} .= "   <td nowrap>";

				###########
				########### CC Mask for operator|user|cdr only users				
				###########
				(!&check_permissions('view_info_tdc','','')) and ($rec->{'PmtField3'} = 'xxxx-xxxx-xxxx-'.substr($rec->{'PmtField3'},-4))  and ($rec->{'PmtField5'} = '****') and ($rec->{'PmtField4'} = '****');
				if ($rec->{'Captured'} eq 'Yes' or $rec->{'Status'} eq 'Order Cancelled' or $rec->{'Status'} eq 'Cancelled' or $rec->{'Status'} eq 'Void'){
					$va{'searchresults'} .= '&nbsp;';
					if ($rec->{'Status'} eq 'Financed' and &check_permissions('edit_order_cleanup','','')){
						$va{'searchresults'} .= "<input type='checkbox' class='checkbox' name='changepayments' value='$rec->{'ID_orders_payments'}'>\n";
					}

				
				}elsif ($rec->{'AuthCode'} ne '' and length($rec->{'AuthCode'}) >= 2){

					if(&check_permissions('order_capture_payments','','')) {

						##########
						########## Capture Payment (Previously Authorized)
						##########
						$va{'searchresults'} .= qq| <div id="divpayment$rec->{'ID_orders_payments'}"><a href="#order$rec->{'ID_orders'}" id='ajax_btn' onClick="popup_show('ajax_windows', 'ajax_drag', 'ajax_exit', 'element-right', -1, -1,'tabsl');loadDoc('/cgi-bin/common/apps/ajaxpayment?ajaxbuild=$ajaxcmd_capture&id_orders=$rec->{'ID_orders'}&id_orders_payments=$rec->{'ID_orders_payments'}&e=$in{'e'}');delete_div('divpayment$rec->{'ID_orders_payments'}');"><img src='$va{'imgurl'}/$usr{'pref_style'}/b_cauth.gif' title='Capture' alt='' border='0'></a></div>|;

					}
				
				}elsif ($rec->{'Amount'} < 0 and $rec->{'Status'} ne 'Credit by Monterey'){

					#############
					############# Customer Credit
					#############

					if(&check_permissions('order_capture_credits','','')) {

						##########
						########## Chargeback credit?
						##########	
						my ($sth) = &Do_SQL("SELECT COUNT(*) FROM sl_returns WHERE ID_orders = '$in{'id_orders'}' AND merAction = 'Chargeback' AND Status = 'Resolved' AND PackingListStatus NOT IN ('Done','Void');");
						$is_chargeback = $sth->fetchrow();


						##########
						########## Capture Credit
						##########
						if(!$is_chargeback){

							$va{'searchresults'} .= qq| <div id="divpayment$rec->{'ID_orders'}"><a href="#order$rec->{'ID_orders'}" id='ajax_btn' onClick="popup_show('ajax_windows', 'ajax_drag', 'ajax_exit', 'element-right', -1, -1,'tabsl');loadDoc('/cgi-bin/common/apps/ajaxpayment?ajaxbuild=cccredit&id_orders=$rec->{'ID_orders'}&id_orders_payments=$rec->{'ID_orders_payments'}&e=$in{'e'}');delete_div('divorder$rec->{'ID_orders'}');delete_div('divpayment$rec->{'ID_orders'}');"><img src='$va{'imgurl'}/$usr{'pref_style'}/b_pauth.gif' title='Capture Refund' alt='' border='0'></a></div>|;

						}

					}
					
					if(&check_permissions('edit_order_cleanup','','')){
						$va{'searchresults'} .= "<input type='checkbox' class='checkbox' name='changepayments' value='$rec->{'ID_orders_payments'}'>\n";
					}else{
						$va{'searchresults'} .= '&nbsp;';
					}

				}elsif ( $rec->{'Status'} ne 'Cancelled' and $rec->{'Status'} ne 'Credit by Monterey' and (($rec->{'Status'} ne 'Approved' or $rec->{'AuthCode'} eq '0000') or ($rec->{'Status'} eq 'Approved' and !$rec->{'AuthCode'}))){

					
					#######################################################
					#######################################################
					#######################################################
					################
					################ Auth and Sale
					################
					#######################################################
					#######################################################
					#######################################################
					
					###
					### Nota. Se puede agregar una captura especial dependiendo el tipo de tarjeta de credito
					### Basado en get_bin_creditcard_type y el parametro $cfg{'order_capture_payments_' . $this_cc_type }


					####
					#### CC Type Detection (based on bines)
					####
					my $this_cc_type = &get_bin_creditcard_type($rec->{'ID_orders_payments'}, 'bank');

					
					#$va{'searchresults'} .= qq| <a href="/cgi-bin/mod/$usr{'application'}/dbman?cmd=opr_orders&view=$in{'id_orders'}&tab=2&drop=$rec->{'ID_orders_payments'}"><img src='$va{'imgurl'}/$usr{'pref_style'}/b_drop.png' title='Drop' alt='' border='0'></a>|;
					if(&check_permissions('order_authorize_payments','','')) {
						$va{'searchresults'} .= qq|<div id="divpayment$rec->{'ID_orders'}"><a href="#order$rec->{'ID_orders'}" id='ajax_btn' onClick="popup_show('ajax_windows', 'ajax_drag', 'ajax_exit', 'element-right', -1, -1,'tabsl');loadDoc('/cgi-bin/common/apps/ajaxpayment?ajaxbuild=$ajaxcmd_auth&id_orders=$rec->{'ID_orders'}&id_orders_payments=$rec->{'ID_orders_payments'}&e=$in{'e'}');delete_div('divorder$rec->{'ID_orders'}');delete_div('divpayment$rec->{'ID_orders'}');"><img src='$va{'imgurl'}/$usr{'pref_style'}/b_pauth.gif' title='Authorize' alt='' border='0'></a></div>|;
					}

					if(&check_permissions('order_capture_payments','','')) {
						$va{'searchresults'} .= qq| <div id="divpayment$rec->{'ID_orders'}"><a href="#order$rec->{'ID_orders'}" id='ajax_btn' onClick="popup_show('ajax_windows', 'ajax_drag', 'ajax_exit', 'element-right', -1, -1,'tabsl');loadDoc('/cgi-bin/common/apps/ajaxpayment?ajaxbuild=$ajaxcmd_sale&id_orders=$rec->{'ID_orders'}&id_orders_payments=$rec->{'ID_orders_payments'}&e=$in{'e'}');delete_div('divorder$rec->{'ID_orders'}');delete_div('divpayment$rec->{'ID_orders'}');"><img src='$va{'imgurl'}/$usr{'pref_style'}/b_fpauth.gif' title='Facil Pago Authorize/Capture' alt='' border='0'></a></div>|;
					}

					if($cfg{'order_capture_payments_' . $this_cc_type } and &check_permissions('order_capture_payments_' . $this_cc_type,'','') ) {
						my $id_banks_debit = $cfg{'order_capture_payments_' . $this_cc_type };
						$va{'searchresults'} .= qq|<div id="divpayment$rec->{'ID_orders_payments'}" name="divpayment$rec->{'ID_orders_payments'}" ><a href="#tabs" name="anchor_divpayment$rec->{'ID_orders_payments'}" onClick="popup_show('ajax_windows', 'ajax_drag', 'ajax_exit', 'element-right', -1, -1,'tabsl');loadDoc('/cgi-bin/common/apps/ajaxbuild?ajaxbuild=edit_payments&id_orders=$rec->{'ID_orders'}&id_orders_payments=$rec->{'ID_orders_payments'}&ida_banks=$id_banks_debit&format=2&cmd=$in{'cmd'}&script_url=/cgi-bin/mod/$usr{'application'}/dbman');"><img src='$va{'imgurl'}amex_32x32.png' title='Capture $this_cc_type' alt='' border='0'></a></div>|;
					}

					if(&check_permissions('order_change_payments','','')) {
						$va{'searchresults'} .= "<input type='checkbox' class='checkbox' name='changepayments' value='$rec->{'ID_orders_payments'}'>\n";
					}

				}elsif($rec->{'Status'} eq 'Approved' and $rec->{'AuthCode'} and $rec->{'AuthCode'} ne '0000' and $rec->{'Captured'} ne 'Yes'){
					## Capture & Force Capt
					if(&check_permissions('order_capture_payments','','')) {
						$va{'searchresults'} .= qq| <div id="divpayment$rec->{'ID_orders_payments'}"><a href="#order$rec->{'ID_orders'}" id='ajax_btn' onClick="popup_show('ajax_windows', 'ajax_drag', 'ajax_exit', 'element-right', -1, -1,'tabsl');loadDoc('/cgi-bin/common/apps/ajaxpayment?ajaxbuild=$ajaxcmd_capture&id_orders=$rec->{'ID_orders'}&id_orders_payments=$rec->{'ID_orders_payments'}&e=$in{'e'}');delete_div('divpayment$rec->{'ID_orders_payments'}');"><img src='$va{'imgurl'}/$usr{'pref_style'}/b_cauth.gif' title='Capture' alt='' border='0'></a></div>|;
					}

					#($btns =~ /x/i) and ($va{'searchresults'} .= qq| <div id="divpayment$rec->{'ID_orders_payments'}"><a href="#order$rec->{'ID_orders'}" id='ajax_btn' onClick="popup_show('ajax_windows', 'ajax_drag', 'ajax_exit', 'element-right', -1, -1,'tabs');loadDoc('/cgi-bin/common/apps/ajaxpayment?ajaxbuild=tocapture&id_orders=$rec->{'ID_orders'}&id_orders_payments=$rec->{'ID_orders_payments'}&e=$in{'e'}');delete_div('divpayment$rec->{'ID_orders_payments'}');"><img src='$va{'imgurl'}/$usr{'pref_style'}/b_xauth.gif' title='To Capture' alt='' border='0'></a></div>|);
					$va{'searchresults'} .= "&nbsp;&nbsp;&nbsp;&nbsp;";
				}else{
					$va{'searchresults'} .=  qq|<img src='$va{'imgurl'}/$usr{'pref_style'}/auth-fu.png' width='14' height='14' title='Authorized' alt='' border='0'>|	if($rec->{'AuthCode'} and $rec->{'AuthCode'} ne '' and $rec->{'AuthCode'} ne '0000' and (!$rec->{'Captured'} or $rec->{'Captured'} eq 'Yes') and (!$rec->{'CapDate'} or $rec->{'CapDate'} eq '' or $rec->{'CapDate'}eq'0000-00-00')); 
					$va{'searchresults'} .=  qq|<img src='$va{'imgurl'}/$usr{'pref_style'}/capt-fu.png' width='14' height='14' title='Captured' alt='' border='0'>|	if $rec->{'Captured'} eq 'Yes';
				}
				
                
                ### Permite ver todos los numeros de la tarjeta
                if( &check_permissions('view_full_cardnumber_tdc','','') == 1 )
                {
                    my $sql_cc = "SELECT card_number FROM sl_orders_cardsdata WHERE ID_orders_payments=".$rec->{'ID_orders_payments'}.";";
                    my $sth_cc = &Do_SQL($sql_cc);
                    my $data_cc = $sth_cc->fetchrow_hashref();
                    $rec->{'PmtField3'} = &LeoDecrypt($data_cc->{'card_number'});
                }



				$va{'searchresults'} .= "   </td>";
				$va{'searchresults'} .= "   <td class='smalltext' $decor valign='top' colspan='2'>$rec->{'PmtField1'}<br>$rec->{'PmtField7'}</td>\n";
				$va{'searchresults'} .= "   <td class='smalltext' $decor valign='top'>$rec->{'PmtField2'}<br>$rec->{'PmtField3'}</td>\n";
				$va{'searchresults'} .= "   <td class='smalltext' $decor valign='top'>$rec->{'PmtField4'}</td>\n";
				$va{'searchresults'} .= "   <td class='smalltext' $decor valign='top'>$rec->{'PmtField5'}</td>\n";
				$va{'searchresults'} .= "   <td class='smalltext' $decor valign='top'>$rec->{'Status'}<br>$rec->{'AuthCode'}</td>\n";
				$va{'searchresults'} .= "   <td class='smalltext' $decor valign='top'>$rec->{'PmtField8'}</td>\n";
				$va{'searchresults'} .= "   <td class='smalltext' $decor align='right' valign='top' colspan='2'> ".&format_price($rec->{'Amount'})."<br>$rec->{'Paymentdate'}<br><span style='$captcolor'>$rec->{'CapDate'}</span>\n";
				
				#Se comenta edici�n de pagos.
				if (&check_permissions('edit_order_cleanup','','')){

					$va{'divpayment_name'} = "divpayment$rec->{'ID_orders_payments'}";
					$va{'searchresults'} .= qq| <div id="divpayment$rec->{'ID_orders_products'}" name="divpayment$rec->{'ID_orders_products'}" style="display: none;" ><a href="#tabs" name="anchor_divpayment$rec->{'ID_orders_products'}" onClick="popup_show('ajax_windows', 'ajax_drag', 'ajax_exit', 'element-right', -1, -1,'tabs');loadDoc('/cgi-bin/common/apps/ajaxbuild?ajaxbuild=edit_payments&id_orders=$rec->{'ID_orders'}&id_orders_payments=$rec->{'ID_orders_payments'}&cmd=$in{'cmd'}&script_url=/cgi-bin/mod/$usr{'application'}/dbman');"><img src='$va{'imgurl'}/$usr{'pref_style'}/b_edit.png' title='Edit In Clean up Mode' alt='' border='0'></a></div>|;

					if ( $rec->{'Status'} =~ /Approved|Pending/ or ( $rec->{'Status'} eq 'Credit' and $is_chargeback ) ){

						$va{'searchresults'} .= qq| <div id="divpayment|.$rec->{'ID_orders_payments'}.qq|f2" name="divpayment|.$rec->{'ID_orders_payments'}.qq|f2" style="display: none;" ><a href="#tabs" name="anchor_divpayment|.$rec->{'ID_orders_payments'}.qq|f2" onClick="popup_show('ajax_windows', 'ajax_drag', 'ajax_exit', 'element-right', -1, -1,'tabs');loadDoc('/cgi-bin/common/apps/ajaxbuild?ajaxbuild=edit_payments&id_orders=|.$rec->{'ID_orders'}.qq|&id_orders_payments=|.$rec->{'ID_orders_payments'}.qq|&cmd=|.$in{'cmd'}.qq|&format=2&script_url=/cgi-bin/mod/|.$usr{'application'}.qq|/dbman');"><img src='$va{'imgurl'}/|.$usr{'pref_style'}.qq|/b_edit.png' title='Edit In Clean up Mode F2' alt='' border='0'></a></div>|;
						$va{'searchresults'} .= qq|<img src='$va{'imgurl'}/$usr{'pref_style'}/b_edit.png' title='Edit In Clean up Mode' alt='' border='0' onclick="function sel_div_pay(){ var format_cc = jQuery('input[name=format_credit_card]').val(); if (typeof format_cc  !== 'undefined') { jQuery('a[name=anchor_divpayment|.$rec->{'ID_orders_payments'}.qq|f2]').click(); } else { jQuery('a[name=anchor_divpayment|.$rec->{'ID_orders_payments'}.qq|]').click(); }  } sel_div_pay();" />|;

					}

				}

				$va{'searchresults'} .= "</td>\n";
				$va{'searchresults'} .= "</tr>\n";


			}elsif($rec->{'Type'} eq "Referenced Deposit"){


				########################################
				########################################
				########################################
				########
				######## Referenced Deposit
				########
				########################################
				########################################
				########################################

				$num_cols = 9;

				$va{'searchresults'} .= "<tr>\n";
				$va{'searchresults'} .= "   <td colspan='2' class='menu_bar_title'>ID</td>\n";
				$va{'searchresults'} .= "   <td colspan='2' class='menu_bar_title'>Type</td>\n";
				$va{'searchresults'} .= "	<td colspan='2' class='menu_bar_title'>Reference</td>\n";	
				# $va{'searchresults'} .= "   <td class='menu_bar_title'>Sub Account Of</td>\n";
				# $va{'searchresults'} .= "   <td class='menu_bar_title'>Bank Name</td>\n";
				# $va{'searchresults'} .= "	<td class='menu_bar_title'>Currency</td>\n";	
				# $va{'searchresults'} .= "   <td class='menu_bar_title'>Ref Num</td>\n";
				# $va{'searchresults'} .= "   <td class='menu_bar_title'>Memo</td>\n";
				$va{'searchresults'} .= "	<td colspan='2' class='menu_bar_title'>Status</td>\n";
				$va{'searchresults'} .= "	<td colspan='2' class='menu_bar_title' align='right'>Amount</td>\n";
				$va{'searchresults'} .= " </tr>\n";

				$va{'searchresults'} .= " <tr bgcolor='$c[$d]' onmouseover='m_over(this)' onmouseout='m_out(this)'>\n";
				$va{'searchresults'} .= "   <td colspan='2' class='smalltext' nowrap $decor>".$rec->{'ID_orders_payments'}."</td>";
				$va{'searchresults'} .= "   <td colspan='2' class='smalltext' nowrap $decor>".$rec->{'Type'}."</td>";
				$va{'searchresults'} .= "   <td colspan='2' class='smalltext' nowrap $decor>".$rec->{'PmtField3'}."</td>";
				$va{'searchresults'} .= "   <td colspan='2' class='smalltext' $decor valign='top' $decor> $rec->{'Status'}<br>$rec->{'AuthCode'}</td>\n";
				$va{'searchresults'} .= "   <td colspan='2' class='smalltext' $decor align='right' valign='top' $decor> ".&format_price($rec->{'Amount'})."<br>$rec->{'Paymentdate'}<br><span style='$captcolor'>$rec->{'CapDate'}</span>\n";
				
				#Se comenta edici�n de pagos.
				if (&check_permissions('edit_order_cleanup','','') && !$decor){
				
					#$va{'searchresults'} .= qq| <div id="divpayment$rec->{'ID_orders_products'}"> :P <a href="#tabs" onClick="popup_show('ajax_windows', 'ajax_drag', 'ajax_exit', 'element-right', -1, -1,'tabsl');loadDoc('/cgi-bin/common/apps/ajaxbuild?ajaxbuild=pay_referenced_deposit&id_orders=$rec->{'ID_orders'}&id_orders_payments=$rec->{'ID_orders_payments'}&cmd=$in{'cmd'}|. $set_form2 .qq|&script_url=/cgi-bin/mod/$usr{'application'}/dbman');"><img src='$va{'imgurl'}/$usr{'pref_style'}/b_edit.png' title='Payment Charge' alt='Payment Charge' border='0'></a></div>|;
					
					$va{'searchresults'} .= qq| <div id="divpayment|.$rec->{'ID_orders_payments'}.qq|f2" name="divpayment|.$rec->{'ID_orders_payments'}.qq|f2" style="display: none;" ><a href="#tabs" name="anchor_divpayment|.$rec->{'ID_orders_payments'}.qq|f2" onClick="popup_show('ajax_windows', 'ajax_drag', 'ajax_exit', 'element-right', -1, -1,'tabs');loadDoc('/cgi-bin/common/apps/ajaxbuild?ajaxbuild=edit_payments&id_orders=|.$rec->{'ID_orders'}.qq|&id_orders_payments=|.$rec->{'ID_orders_payments'}.qq|&cmd=|.$in{'cmd'}.qq|&format=2&script_url=/cgi-bin/mod/|.$usr{'application'}.qq|/dbman');"><img src='$va{'imgurl'}/|.$usr{'pref_style'}.qq|/b_edit.png' title='Edit In Clean up Mode F2' alt='' border='0'></a></div>|;
					$va{'searchresults'} .= qq|<img src='$va{'imgurl'}/$usr{'pref_style'}/b_edit.png' title='Edit In Clean up Mode' alt='' border='0' onclick="function sel_div_pay(){ var format_cc = jQuery('input[name=format_credit_card]').val(); if (typeof format_cc  !== 'undefined') { jQuery('a[name=anchor_divpayment|.$rec->{'ID_orders_payments'}.qq|f2]').click(); } else { jQuery('a[name=anchor_divpayment|.$rec->{'ID_orders_payments'}.qq|]').click(); }  } sel_div_pay();" />|;

				
				}
				
				$va{'searchresults'} .= "</td>\n";
				$va{'searchresults'} .= "</tr>\n";

			}else{

				########################################
				########################################
				########################################
				########
				######## COD
				########
				########################################
				########################################
				########################################

				$num_cols = 9;
				$va{'searchresults'} .= "<tr>\n";
				$va{'searchresults'} .= "   <td class='menu_bar_title'>Type</td>\n";
				$va{'searchresults'} .= "   <td class='menu_bar_title'>ID</td>\n";
				$va{'searchresults'} .= "	<td class='menu_bar_title'>Bank Date</td>\n";	
				$va{'searchresults'} .= "   <td class='menu_bar_title'>Sub Account Of</td>\n";
				$va{'searchresults'} .= "   <td class='menu_bar_title'>Bank Name</td>\n";
				$va{'searchresults'} .= "	<td class='menu_bar_title'>Currency</td>\n";	
				$va{'searchresults'} .= "   <td class='menu_bar_title'>Ref Num</td>\n";
				$va{'searchresults'} .= "   <td class='menu_bar_title'>Memo</td>\n";
				$va{'searchresults'} .= "	<td class='menu_bar_title'>Status</td>\n";
				$va{'searchresults'} .= "	<td class='menu_bar_title' align='right'>Amount</td>\n";
				$va{'searchresults'} .= " </tr>\n";

				$va{'searchresults'} .= " <tr bgcolor='$c[$d]' onmouseover='m_over(this)' onmouseout='m_out(this)'>\n";
				$va{'searchresults'} .= "   <td class='smalltext' nowrap $decor>".$rec->{'Type'}."</td>";
				$va{'searchresults'} .= "   <td class='smalltext' nowrap $decor colspan='7'>&nbsp</td>";
				#@ivanmiranda :: Se activa el vinculo al CM que 'paga'
				if($rec->{'AuthCode'} =~ /CM-(\d{1,})/ and $rec->{'Status'} eq 'Approved'){
					$rec->{'AuthCode'} = $1;
					$va{'searchresults'} .= "   <td class='smalltext' $decor valign='top' $decor> $rec->{'Status'}<br><a href='dbman?cmd=opr_creditmemos&view=$rec->{'AuthCode'}'>CM <strong>$rec->{'AuthCode'}</strong></a></td>\n";
				}elsif($rec->{'Reason'} eq 'Sale' and $rec->{'AuthCode'} =~ /CA-/){
					my @id_customers_advances = split('-', $rec->{'AuthCode'});
					$va{'searchresults'} .= "   <td class='smalltext' $decor valign='top' $decor> $rec->{'Status'}<br><a href='dbman?cmd=opr_customers_advances&view=$id_customers_advances[1]'><strong>$rec->{'AuthCode'}</strong></a></td>\n";
				}else{
					$va{'searchresults'} .= "   <td class='smalltext' $decor valign='top' $decor> $rec->{'Status'}<br>$rec->{'AuthCode'}</td>\n";
				}
				$va{'searchresults'} .= "   <td class='smalltext' $decor align='right' valign='top' $decor> ".&format_price($rec->{'Amount'})."<br>$rec->{'Paymentdate'}<br><span style='$captcolor'>$rec->{'CapDate'}</span>\n";
				
				#Se comenta edici�n de pagos.
				if (&check_permissions('edit_order_cleanup','','')){
				#@ivanmiranda :: Los pagos de un CM no se editan
					if($rec->{'Reason'} ne 'Refund'){
						$va{'searchresults'} .= qq| <div id="divpayment$rec->{'ID_orders_products'}"><a href="#tabs" onClick="popup_show('ajax_windows', 'ajax_drag', 'ajax_exit', 'element-right', -1, -1,'tabs');loadDoc('/cgi-bin/common/apps/ajaxbuild?ajaxbuild=edit_payments&id_orders=$rec->{'ID_orders'}&id_orders_payments=$rec->{'ID_orders_payments'}&cmd=$in{'cmd'}|. $set_form2 .qq|&script_url=/cgi-bin/mod/$usr{'application'}/dbman');"><img src='$va{'imgurl'}/$usr{'pref_style'}/b_edit.png' title='Edit In Clean up Mode $rec->{'Reason'}' alt='' border='0'></a></div>|;
					}

				}
				$va{'searchresults'} .= "</td>\n";
				$va{'searchresults'} .= "</tr>\n";
				
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
						
		} ## END while

		if (&check_permissions('edit_order_cleanup','','')){			
			$va{'flexipago'} = qq|&nbsp; - &nbsp; <a href='#tabs'>Update Dates</a>|;
		}
		$va{'searchresults'} .= qq|
			<tr>
				<td colspan='$num_cols' class='smalltext' align="right">|.&trans_txt('mer_vpo_total').qq|</td>
				<td align="right" class='smalltext' style="border-top:thick double #808080;">|.&format_price($tot_pay).qq|</td>
			</tr>\n|;
			
			
			
		&auth_logging('opr_orders_viewpay',$in{'id_orders'});
	}else{
		$va{'pageslist'} = 1;
		$va{'searchresults'} = qq|
		    <tr>
				<td colspan='8' class='menu_bar_title' align="center">&nbsp;</td>
			</tr>
			<tr>
				<td colspan='8' align="center">|.&trans_txt('search_nomatches').qq|</td>
			</tr>\n|;
	}
	
}

sub load_tabs3{
########################
##   Tab3.- Paylogs   ##
########################
# --------------------------------------------------------
# Forms Involved: 
# Created on: 11/13/08 13:24:02
# Author: MCC C. Gabriel Varela S.
# Description :   
# Parameters :
# Last Time Modified by RB on 18/10/2011: Se agrego mascara para cc number
	&auth_logging('opr_orders_viewpaylog',$in{'id_orders'});		
	my (@c) = split(/,/,$cfg{'srcolors'});
	my ($sth) = &Do_SQL("SELECT COUNT(*) FROM sl_orders_plogs WHERE ID_orders='$in{'id_orders'}' ORDER BY ID_orders_plogs DESC");
	$va{'matches'} = $sth->fetchrow;
	if ($va{'matches'}>0){
		(!$in{'nh'}) and ($in{'nh'}=1);
		$first = ($in{'nh'} - 1) * $usr{'pref_maxh'};			
		($va{'pageslist'},$qs) = &pages_list($in{'nh'},"/cgi-bin/mod/$usr{'application'}/dbman",$va{'matches'},$usr{'pref_maxh'});
		my ($sth) = &Do_SQL("SELECT * FROM sl_orders_plogs WHERE ID_orders='$in{'id_orders'}' ORDER BY ID_orders_plogs DESC");
		while ($rec = $sth->fetchrow_hashref){
			$d = 1 - $d;
			#$rec->{'Data'} =~ s/\n/<br>/g;
			$rec->{'Data'} = &proc_pay_data($rec->{'Data'});

			## CC Mask for operator|user|cdr only users
			if($rec->{'Data'} =~ /card_accountNumber = (\d{12,20})/){

				if(!&check_permissions('view_info_tdc','','')){
					my $ccmask = substr($1,-4);
					$rec->{'Data'} =~ s/card_accountNumber = \d{12,20}/card_accountNumber = xxxx-xxxx-xxxx-$ccmask/;
				}

			}elsif($rec->{'Data'} =~ /Number=(\d{12,20})/){

				if(!&check_permissions('view_info_tdc','','')){
					my $ccmask = substr($1,-4);
					$rec->{'Data'} =~ s/Number=\d{12,20}/Number = xxxx-xxxx-xxxx-$ccmask/;
					$rec->{'Data'} =~ s/Expires=\d{4,5}/Expires = xxxx/;
					$rec->{'Data'} =~ s/Expires=...../Expires = xxxx/;
					$rec->{'Data'} =~ s/Cvv2Val=\d{3,4}/Cvv2Val = xxxx/;
				}
			}

			$va{'searchresults'} .= "<tr bgcolor='$c[$d]'>\n";
			$va{'searchresults'} .= "  <td class='smalltext' valign='top'>$rec->{'Date'} $rec->{'Time'}<br>($rec->{'ID_admin_users'}) ".&load_db_names('admin_users','ID_admin_users',$rec->{'ID_admin_users'},'[FirstName] [LastName]')."</td>\n";
			$va{'searchresults'} .= "  <td class='smalltext'>$rec->{'Data'}</td>\n";
			$va{'searchresults'} .= "</tr>\n";
		}
	}else{
		$va{'pageslist'} = 1;
		$va{'searchresults'} = qq|
			<tr>
				<td colspan='2' align="center">|.&trans_txt('search_nomatches').qq|</td>
			</tr>\n|;
	}

}


sub load_tabs4 {
########################
##   Tab4.- Notes     ##
########################	
# --------------------------------------------------------
# Forms Involved: 
# Created on: 11/13/08 13:24:02
# Author: Cesar Cedillo
# Description :   
# Parameters :
# Last Time Modified by RB on 19/12/2012

	#cgierr("El tipo es ". $in{'typen'});
	if ($in{'action'}){
		if (($in{'tmpflag'} and (!$in{'true_notes'} or !$in{'typen'})) and !$in{'edit'}){
			$va{'tabmessages'} = &trans_txt('reqfields_short');
		}else{
		
			if(!$in{'true_notes'} and $in{'notes'}){
				$in{'true_notes'}=$in{'notes'};
				$in{'typen'}=$in{'notestype'};
			}
		  ## Actualizacion en sl_cod_sales
			if($in{'ptype'} eq 'COD'){
			  
				if($in{'ptype'} eq 'COD') {
					my($o_status,$never,$more,$seven,$two,$one,$id_warehouses) = &get_cod_sale_status($in{'id_orders'}) 		
				}
			  
			  	if(!$one and $id_warehouses){
			  
			    $id_warehouses =~ s/\|/,/g;
			    ## Unica Suma
			    &Do_SQL("UPDATE sl_cod_sales SET One=One+1 WHERE Status='$o_status' AND ID_warehouses IN($id_warehouses);");

			    
			    ## Posibles Restas
			    &Do_SQL("UPDATE sl_cod_sales SET More=More-1 WHERE Status='$o_status' AND ID_warehouses IN($id_warehouses);") if $more;
			    &Do_SQL("UPDATE sl_cod_sales SET Seven=Seven-1 WHERE Status='$o_status' AND ID_warehouses IN($id_warehouses);") if $seven;
			    &Do_SQL("UPDATE sl_cod_sales SET Two=Two-1 WHERE Status='$o_status' AND ID_warehouses IN($id_warehouses);") if $two;
			    &Do_SQL("UPDATE sl_cod_sales SET Never=Never-1 WHERE Status='$o_status' AND ID_warehouses IN($id_warehouses);") if $never;
			}
		}
		
			$va{'tabmessages'} = &trans_txt('opr_orders_noteadded');

			&add_order_notes_by_type($in{'id_orders'},&filter_values($in{'true_notes'}),$in{'typen'});
			$in{'type'}=$in{'typen'};
			$in{'notes'}=$in{'true_notes'};
			&auth_logging('opr_orders_noteadded',$in{'id_orders'});
			delete($in{'true_notes'});
			delete($in{'typen'});
			delete($in{'action'});
			$in{'tabs'} = 1;
		}
	}
	## VRM

	$in{'ptype'} = load_name('sl_orders','ID_orders',$in{'id_orders'},'Ptype');
	$va{'pp_order'} = lc($in{'ptype'}) eq 'cod' ? '<input type="radio" name="notestype" class="radio" value="PP Order" onClick="fillOrderNote(11);">PP Order' : '';
	
	#my (@types) = &load_enum_toarray('sl_orders_notes','Type');
	#for(0..$#types){
	#	my ($type) = $types[$_];
	#	$va{'filter_links'} .= qq|<a href="[va_script_url]?cmd=[in_cmd]&view=[in_id_orders]&tab=4&filter=$type">$type</a> - |;
	#}

	my ($sth_types) = &Do_SQL('select Type from sl_orders_notes_types');
	$va{'filter_links'}='<select name="slctFilterLinks" id="slctFilterLinks">';
	while ($rec = $sth_types->fetchrow_hashref){
		$va{'filter_links'} .= qq|<option lnk="/cgi-bin/mod/[ur_application]/dbman?cmd=[in_cmd]&view=[in_id_orders]&tab=4&filter=$rec->{'Type'}">$rec->{'Type'}</option> - |;	

	}
	$va{'filter_links'}.='</select>';


	chop($va{'filter_links'});
	chop($va{'filter_links'});
	
	my ($query);
	if ($in{'filter'}){
		$query = "AND Type='".&filter_values($in{'filter'})."' ";
		$va{'query'} = $in{'filter'};
		$in{'tabs'} = 1;
	}
	my (@c) = split(/,/,$cfg{'srcolors'});
	my ($sth) = &Do_SQL("SELECT COUNT(*) FROM sl_orders_notes WHERE ID_orders='$in{'id_orders'}' $query");
	$va{'matches'} = $sth->fetchrow;
	if ($va{'matches'}>0){
		(!$in{'nh'}) and ($in{'nh'}=1);
		$first = ($in{'nh'} - 1) * $usr{'pref_maxh'};			
		($va{'pageslist'},$qs) = &pages_list($in{'nh'},"/cgi-bin/mod/$usr{'application'}/dbman",$va{'matches'},$usr{'pref_maxh'});
		my ($sth) = &Do_SQL("SELECT sl_orders_notes.ID_admin_users,sl_orders_notes.Date as mDate,sl_orders_notes.Time as mTime,FirstName,LastName,Type,Notes FROM sl_orders_notes,admin_users WHERE ID_orders='$in{'id_orders'}' AND sl_orders_notes.ID_admin_users=admin_users.ID_admin_users $query ORDER BY sl_orders_notes.Date DESC,sl_orders_notes.Time DESC LIMIT $first,$usr{'pref_maxh'} ;");

		while ($rec = $sth->fetchrow_hashref){
			$d = 1 - $d;
			$rec->{'Notes'} =~ s/\n/<br>/g;
			$va{'searchresults'} .= "<tr bgcolor='$c[$d]'>\n";
			$va{'searchresults'} .= "  <td class='smalltext'>$rec->{'mDate'} &nbsp; $rec->{'mTime'}<br>($rec->{'ID_admin_users'}) $rec->{'FirstName'} $rec->{'LastName'}</td>\n";
			$va{'searchresults'} .= "  <td class='smalltext'>$rec->{'Type'}</td>\n";
			$va{'searchresults'} .= "  <td class='smalltext'>$rec->{'Notes'}</td>\n";
			$va{'searchresults'} .= "</tr>\n";
		}
	}else{
		$va{'pageslist'} = 1;
		$va{'searchresults'} = qq|
			<tr>
				<td colspan='3' align="center">|.&trans_txt('search_nomatches').qq|</td>
			</tr>\n|;
	}
	
}


sub load_tabs5 {
########################
##   Tab5.- Leads     ##
########################	
# --------------------------------------------------------
# Forms Involved: 
# Created on: 02/03/2011 18:00:02
# Author: Roberto Barcenas.
# Description :   Out Calls
# Parameters :

	## Get Calls 
	my $sth = &Do_SQL("SELECT CID, Phone1, Phone2, Cellphone  FROM sl_orders INNER JOIN sl_customers ON sl_orders.ID_customers = sl_customers.ID_customers WHERE ID_orders='$in{'id_orders'}'");
	$rec=$sth->fetchrow_hashref;
	my($query) ='';
	$rec->{'Phone1'} =~ s/-|\(|\)|\+|\.|\s//g;
	if ($rec->{'Phone1'} ne ''){
		$query = " AND (ID_leads='".substr($rec->{'Phone1'},-10)."' or ID_leads='1".substr($rec->{'Phone1'},-10)."' or ID_leads='".$rec->{'Phone1'}."') ";
	}
	$rec->{'Phone2'} =~ s/-|\(|\)|\+|\.|\s//g;
	if ($rec->{'Phone2'}ne '' and $query !~ /$rec->{'Phone2'}/){
		$query .= ($query ne '')? " OR ":"";
		$query .= " (ID_leads='".substr($rec->{'Phone2'},-10)."' or ID_leads='1".substr($rec->{'Phone2'},-10)."' or ID_leads='".$rec->{'Phone2'}."') ";
	}
	$rec->{'Cellphone'} =~ s/-|\(|\)|\+|\.|\s//g;
	if ($rec->{'Cellphone'} ne '' and $query !~ /$rec->{'Cellphone'}/){
		$query .= ($query ne '')? " OR ":"";
		$query .= " (ID_leads='".substr($rec->{'Cellphone'},-10)."' or ID_leads='1".substr($rec->{'Cellphone'},-10)."' or ID_leads='".$rec->{'Cellphone'}."') ";
	}
	$rec->{'CID'} =~ s/-|\(|\)|\+|\.|\s//g;
	if ($rec->{'CID'}ne '' and $query !~ /$rec->{'CID'}/){
		$query .= ($query ne '')? " OR ":"";
		$query .= " (ID_leads='".substr($rec->{'CID'},-10)."' or ID_leads='1".substr($rec->{'CID'},-10)."' or ID_leads='".$rec->{'CID'}."') ";
	}

	my (@c) = split(/,/,$cfg{'srcolors'});
	my ($sth) = &Do_SQL("SELECT COUNT(*) FROM sl_leads_calls  WHERE 1 $query");
	$va{'matches'} = $sth->fetchrow;
	if ($va{'matches'}>0){
		(!$in{'nh'}) and ($in{'nh'}=1);
		$first = ($in{'nh'} - 1) * $usr{'pref_maxh'};			
		
		($va{'pageslist'},$qs) = &pages_list($in{'nh'},"/cgi-bin/mod/$usr{'application'}/dbman",$va{'matches'},$usr{'pref_maxh'});
		my ($sth) = &Do_SQL("SELECT * FROM sl_leads_calls  WHERE 1 $query ORDER BY ID_leads_calls DESC LIMIT $first,$usr{'pref_maxh'};");
		while ($rec = $sth->fetchrow_hashref){
			$d = 1 - $d;
			(!$rec->{'Duration'}) and ($rec->{'Duration'} = 'N/A');
			$va{'searchresults'} .= "<tr bgcolor='$c[$d]'>\n";
			$va{'searchresults'} .= "  <td class='smalltext'>".&format_phone($rec->{'ID_leads'})."</td>\n";
			$va{'searchresults'} .= "  <td class='smalltext'>$rec->{'IO'}</td>\n";
			$va{'searchresults'} .= "  <td class='smalltext'>".&load_name("admin_users","ID_admin_users",$rec->{'ID_admin_users'},"CONCAT(FirstName,' ',LastName)")." ($rec->{'ID_admin_users'})</td>\n";
			$va{'searchresults'} .= "  <td class='smalltext'>$rec->{'Calif'}</td>\n";
			$va{'searchresults'} .= "  <td class='smalltext'>$rec->{'Duration'}</td>\n";
			
			$va{'searchresults'} .= "  <td class='smalltext'>$rec->{'Date'}</td>\n";
			$va{'searchresults'} .= "  <td class='smalltext'>$rec->{'Time'}</td>\n";
			$va{'searchresults'} .= "</tr>\n";
			&auth_logging('opr_orders_outcall_viewed',$in{'id_orders'});
		}
	}else{
		$va{'pageslist'} = 1;
		$va{'searchresults'} = qq|
			<tr>
				<td colspan='5' align='center'>|.&trans_txt('search_nomatches').qq|</td>
			</tr>\n|;
	}

}

sub load_tabs7{
########################
##   Tab7.- Returns ##
########################
# --------------------------------------------------------
# Forms Involved: 
# Created on: 11/13/08 13:24:02
# Author: MCC C. Gabriel Varela S.
# Description :   
# Parameters :
##Notes
# Last Modified RB: 11/20/08  17:22:41  -- Fixed Returns list
	
	
	if ($in{'action'} and $in{'id_returns'}){
		if ((!$in{'notes'} or !$in{'notestype'}) and !$in{'edit'}){
			$va{'tabmessages'} = &trans_txt('reqfields');
		}else{
			
			$va{'tabmessages'} = &trans_txt('opr_returns_noteadded');
			my ($sth) = &Do_SQL("INSERT INTO sl_returns_notes SET id_returns='$in{'id_returns'}',Notes='".&filter_values($in{'notes'})."',Type='$in{'notestype'}',Date=Curdate(),Time=NOW(),ID_admin_users='$usr{'id_admin_users'}'");
			delete($in{'notes'});
			delete($in{'notestype'});
			&auth_logging('opr_returns_noteadded',$in{'id_returns'});
			$in{'tabs'} = 1;
		}
	}
					
	### VRM
	my (@c) = split(/,/,$cfg{'srcolors'});
	my ($sth) = &Do_SQL("SELECT COUNT(*) FROM sl_returns WHERE ID_orders = '$in{'id_orders'}'");
	$va{'matches'} = $sth->fetchrow;
	if ($va{'matches'}>0){
	my ($sth) = &Do_SQL("SELECT * FROM sl_returns WHERE ID_orders =  $in{'id_orders'} ORDER BY Date DESC;");
												
		while ($rec = $sth->fetchrow_hashref){
			$in{'id_returns'} = $rec->{'ID_returns'};
			my ($cmd) = 'opr_returns';		
			#$cmd = &load_prefixtab($cmd) if /cgi-bin/mod/$usr{'application'}/dbman =~	/admin/;
			
			$d = 1 - $d;
			$va{'searchresults'} .= "<tr bgcolor='$c[$d]'>\n";
			$va{'searchresults'} .= "		<td class='smalltext'><a href=\"/cgi-bin/mod/$usr{'application'}/dbman?cmd=$cmd&view=$rec->{'ID_returns'}\">$rec->{'ID_returns'}</a></td>\n";
	    $va{'searchresults'} .= "		<td class='smalltext'>$rec->{'Type'}</td>\n";
			$va{'searchresults'} .= "		<td class='smalltext'>$rec->{'merAction'}</td>\n";
			$va{'searchresults'} .= "		<td class='smalltext'>$rec->{'Status'}</td>\n";
			$va{'searchresults'} .= "		<td class='smalltext'>$rec->{'Date'}</td>\n";
			$va{'searchresults'} .= "</tr>\n";
		}
	}else{
		$va{'searchresults'} = qq|
			<tr>
				<td colspan='6' align="center">|.&trans_txt('search_nomatches').qq|</td>
			</tr>\n|;
	}
	
}

sub load_tabs8{
##############################
##   Tab8.- Orders/Clients ##
##############################	
# --------------------------------------------------------
# Forms Involved: 
# Created on: 11/13/08 13:24:02
# Author: MCC C. Gabriel Varela S.
# Description :   
# Parameters :
	## Orders
	my (@c) = split(/,/,$cfg{'srcolors'});
	$idc = &load_name("sl_orders","ID_orders",$in{'id_orders'},"ID_customers");
	my ($sth) = &Do_SQL("SELECT COUNT(*) FROM sl_orders WHERE ID_customers='$idc' ");
	
	my @ary = split(/\//,"/cgi-bin/mod/$usr{'application'}/dbman");	
	my $cmdorder = 'opr_orders';
	my $cmdprod = 'mer_products';
	my $cmdserv = 'mer_services';
	
	$va{'matches'} = $sth->fetchrow;
	if ($va{'matches'}>0){
		
		(!$in{'nh'}) and ($in{'nh'}=1);
		$first = ($in{'nh'} - 1) * $usr{'pref_maxh'};			
		($va{'pageslist'},$qs) = &pages_list($in{'nh'},"/cgi-bin/mod/$usr{'application'}/dbman",$va{'matches'},$usr{'pref_maxh'});
		
		$sth = &Do_SQL("SELECT sl_orders_products.Date, sl_orders_products.Time, 
					CONCAT( sl_orders_products.Date, sl_orders_products.Time ) AS orderDate, sl_orders.ID_orders,
					IF(RIGHT(sl_orders_products.ID_products,6)=000000,Related_ID_products,sl_orders_products.ID_products)AS ID_products,
					sl_orders_products.Quantity,sl_orders.Status
					FROM sl_orders 
					INNER JOIN sl_orders_products 
						ON sl_orders.ID_orders = sl_orders_products.ID_orders
					WHERE ID_customers= $idc
					ORDER BY sl_orders.ID_orders DESC
					LIMIT $first,$usr{'pref_maxh'};");
		while ($rec = $sth->fetchrow_hashref){
			my ($idp);
			#Services		
			if($rec->{'ID_products'} < 99999 or substr($rec->{'ID_products'},0,1) == 6){				
				$link_ts = "mer_services";
				$idp		= $rec->{'ID_products'}-600000000;
				$rec->{'Name'}	= &load_name("sl_services","ID_services",$idp,"Name");
			#Skus	
			}elsif(substr($rec->{'ID_products'},0,1) == 4){
				$idp=$rec->{'ID_products'}-400000000;
				$link_ts 	= "mer_parts";
				$rec->{'Name'} 	= &load_name("sl_parts","ID_parts",$idp,"Name");
				$rec->{'Model'}	= &load_name("sl_parts","ID_parts",$idp,"Model");
			#Products	
			}else{
				$idp=$rec->{'ID_products'}-100000000;
				$link_ts 	= "mer_products";
				$rec->{'Name'}	= &load_name("sl_products","ID_products",$idp,"Name");
				$rec->{'Model'}	= &load_name("sl_products","ID_products",$idp,"Model");
			}
			$d = 1 - $d;
			$va{'searchresults'} .= "<tr bgcolor='$c[$d]'>\n";
			$va{'searchresults'} .= "   <td class='smalltext'>$rec->{'Date'} / $rec->{'Time'}</td>\n";
			$va{'searchresults'} .= "   <td class='smalltext'><a href=\"/cgi-bin/mod/$usr{'application'}/dbman?cmd=opr_orders&view=$rec->{'ID_orders'}\">$rec->{'ID_orders'}</a></td>\n";
			
			$va{'searchresults'} .= "   <td class='smalltext'><a href=\"/cgi-bin/mod/$usr{'application'}/dbman?cmd=".$link_ts."&view=".$idp."\">".&format_sltvid($rec->{'ID_products'})."</a></td>\n";
			$va{'searchresults'} .= "   <td class='smalltext'>$rec->{'Name'}/$rec->{'Model'}</td>\n";					
			$va{'searchresults'} .= "   <td class='smalltext'>$rec->{'Status'}</td>\n";
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

sub load_tabs9{
##############################
##   Tab9.- Rep. Memos      ##
##############################	
# --------------------------------------------------------
# Forms Involved: 
# Created on: 11/13/08 13:24:02
# Author: MCC C. Gabriel Varela S.
# Description :   
# Parameters :
	my (@c) = split(/,/,$cfg{'srcolors'});
	my ($sth) = &Do_SQL("SELECT COUNT(*) FROM sl_repmemos WHERE ID_orders = '$in{'id_orders'}'");
	$va{'matches'} = $sth->fetchrow;
	if ($va{'matches'}>0){
		(!$in{'nh'}) and ($in{'nh'}=1);
		$first = ($in{'nh'} - 1) * $usr{'pref_maxh'};			
		($va{'pageslist'},$qs) = &pages_list($in{'nh'},"/cgi-bin/mod/$usr{'application'}/dbman",$va{'matches2'},$usr{'pref_maxh'});
		my ($sth) = &Do_SQL("SELECT * FROM sl_repmemos WHERE ID_orders = '$in{'id_orders'}' ORDER BY Date DESC LIMIT $first,$usr{'pref_maxh'};");
		while ($rec = $sth->fetchrow_hashref){
			$d = 1 - $d;
			$rec->{'Notes'} =~ s/\n/<br>/g;
			$va{'searchresults'} .= "<tr bgcolor='$c[$d]'>\n";
			$va{'searchresults'} .= "  <td class='smalltext'><a href=\"/cgi-bin/mod/$usr{'application'}/dbman?cmd=opr_repmemos&view=$rec->{'ID_repmemo'}\">$rec->{'ID_repmemo'}</a></td>\n";
			$va{'searchresults'} .= "  <td class='smalltext'>$rec->{'ID_orders'}</td>\n";
			$va{'searchresults'} .= "  <td class='smalltext'>$rec->{'ID_products'}</td>\n";
			$va{'searchresults'} .= "  <td class='smalltext'>$rec->{'Reson'}</td>\n";
			$va{'searchresults'} .= "  <td class='smalltext'>$rec->{'ProdCategory'}</td>\n";
			$va{'searchresults'} .= "  <td class='smalltext'>$rec->{'Status'}</td>\n";
			$va{'searchresults'} .= "</tr>\n";
			&auth_logging('opr_repmemos_viewed',$in{'id_orders'});
		}
	}else{
		$va{'pageslist'} = 1;
		$va{'searchresults'} = qq|
			<tr>
				<td colspan='6' align='center'>|.&trans_txt('search_nomatches').qq|</td>
			</tr>\n|;
	}
	
}

sub load_tabs10{
##############################
##   Tab10.- Claims         ##
##############################
# --------------------------------------------------------
# Forms Involved: 
# Created on: 11/13/08 13:24:02
# Author: MCC C. Gabriel Varela S.
# Description :   
# Parameters :
	my (@c) = split(/,/,$cfg{'srcolors'});
	my ($sth) = &Do_SQL("SELECT COUNT(*) FROM sl_claims,sl_orders_products WHERE sl_orders_products.ID_orders_products = sl_claims.ID_orders_products AND ID_orders = '$in{'id_orders'}'");
	$va{'matches'} = $sth->fetchrow;
	if ($va{'matches'}>0){
		
		(!$in{'nh'}) and ($in{'nh'}=1);
		$first = ($in{'nh'} - 1) * $usr{'pref_maxh'};			
		($va{'pageslist'},$qs) = &pages_list($in{'nh'},"/cgi-bin/mod/$usr{'application'}/dbman",$va{'matches2'},$usr{'pref_maxh'});
		my ($sth) = &Do_SQL("SELECT sl_claims.* FROM sl_claims,sl_orders_products WHERE sl_orders_products.ID_orders_products = sl_claims.ID_orders_products AND ID_orders = '$in{'id_orders'}' ORDER BY Date DESC LIMIT $first,$usr{'pref_maxh'};");
		while ($rec = $sth->fetchrow_hashref){
			$d = 1 - $d;
			$rec->{'Notes'} =~ s/\n/<br>/g;
			$va{'searchresults'} .= "<tr bgcolor='$c[$d]'>\n";
			$va{'searchresults'} .= "  <td class='smalltext'><a href=\"/cgi-bin/mod/$usr{'application'}/dbman?cmd=opr_claims&view=$rec->{'ID_claims'}\">$rec->{'ID_claims'}</a></td>\n";
			$va{'searchresults'} .= "  <td class='smalltext'>$rec->{'ClaimTo'}</td>\n";
			$va{'searchresults'} .= "  <td class='smalltext'>$rec->{'ProdCategory'}</td>\n";
			#$va{'searchresults'} .= "  <td class='smalltext'>$rec->{'Notes'}</td>\n";
			$va{'searchresults'} .= "  <td class='smalltext'>$rec->{'Status'}</td>\n";
			$va{'searchresults'} .= "</tr>\n";
			&auth_logging('opr_claims_viewed',$in{'id_orders'});
		}
	}else{
		$va{'pageslist'} = 1;
		$va{'searchresults'} = qq|
			<tr>
				<td colspan='6' align='center'>|.&trans_txt('search_nomatches').qq|</td>
			</tr>\n|;
	}
	
}

sub load_tabs11{
##############################
##   Tab11.- Chargebacks    ##
##############################	
# --------------------------------------------------------
# Forms Involved: 
# Created on: 11/13/08 13:24:02
# Author: MCC C. Gabriel Varela S.
# Description :   
# Parameters :
# 
	my (@c) = split(/,/,$cfg{'srcolors'});
	#my ($sth) = &Do_SQL("SELECT COUNT(*) FROM sl_chargebacks,sl_orders_products WHERE sl_orders_products.ID_orders_products = sl_chargebacks.ID_orders_products AND ID_orders = '$in{'id_orders'}'");
	#$va{'matches'} = $sth->fetchrow;
	if ($va{'matches'}>0){
		(!$in{'nh'}) and ($in{'nh'}=1);
		$first = ($in{'nh'} - 1) * $usr{'pref_maxh'};			
		($va{'pageslist'},$qs) = &pages_list($in{'nh'},"/cgi-bin/mod/$usr{'application'}/dbman",$va{'matches2'},$usr{'pref_maxh'});
		my ($sth) = &Do_SQL("SELECT sl_chargebacks.* FROM sl_chargebacks,sl_orders_products WHERE sl_orders_products.ID_orders_products = sl_chargebacks.ID_orders_products AND ID_orders = '$in{'id_orders'}' ORDER BY Date DESC LIMIT $first,$usr{'pref_maxh'};");
		while ($rec = $sth->fetchrow_hashref){
			$d = 1 - $d;
			$rec->{'Notes'} =~ s/\n/<br>/g;
			$va{'searchresults'} .= "<tr bgcolor='$c[$d]'>\n";
			$va{'searchresults'} .= "  <td class='smalltext'><a href=\"/cgi-bin/mod/$usr{'application'}/dbman?cmd=opr_chargebacks&view=$rec->{'ID_chargebacks'}\">$rec->{'ID_chargebacks'}</a></td>\n";
			$va{'searchresults'} .= "  <td class='smalltext'>$rec->{'ChargeBackTo'}</td>\n";
			$va{'searchresults'} .= "  <td class='smalltext'>$rec->{'ProdCategory'}</td>\n";
			$va{'searchresults'} .= "  <td class='smalltext'>$rec->{'Status'}</td>\n";
			$va{'searchresults'} .= "</tr>\n";
			&auth_logging('opr_chargebacks_viewed',$in{'id_orders'});
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
#   Function: load_tabs13
#
#       Es: Muestra los Invoices relacionados a la orden.
#
#
#    Created on: 30/01/2013 18:00:00
#
#    Author: Enrique Pe�a
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
sub load_tabs13 {
#############################################################################
#############################################################################
use MIME::Base64 qw( encode_base64 );
	## Process Invoice/Credit Note
	if ($in{'geninvoice'}) {
		if (&check_permissions('orders_toinvoice','','')) {
			
			&Do_SQL("START TRANSACTION;");
			my $status;
			if($in{'transferinvoice'}){
				# Generate Invoice
				($va{'tabmessages'}, $status) = &export_info_for_transfer_invoice($in{'id_orders'});	
			}elsif($in{'creditnote'}){
				# Generate Credit Note
				($va{'tabmessages'}, $status) = &export_info_for_invoices($in{'id_orders'});
			}else{
				# Generate Invoice
				($va{'tabmessages'}, $status) = &export_info_for_invoices($in{'id_orders'});
			}
			

			if ($status =~ /OK/i){
				&Do_SQL("COMMIT;");
			}else{
				&Do_SQL("ROLLBACK;");
			}

		}else {
			$va{'tabmessages'} = &trans_txt('opr_orders_invoice_noauth');
		}
	}

	my (@c) = split(/,/,$cfg{'srcolors'});
	### Count CreditMemos
	my ($sth) = &Do_SQL("SELECT COUNT(*) FROM sl_creditmemos_payments WHERE ID_orders = '$in{'id_orders'}';");
	my ($count_creditmemos) = $sth->fetchrow();

	my ($sth) = &Do_SQL("SELECT COUNT(*) FROM (SELECT 1 FROM cu_invoices_lines INNER JOIN cu_invoices USING(ID_invoices) WHERE ID_orders = '$in{'id_orders'}' AND cu_invoices.Status <> 'Void' GROUP BY ID_invoices)AS invoices");	
	$va{'matches'} = int($sth->fetchrow_array) + int($count_creditmemos);
	$va{'geninvoice'} = '';
	
	if ($va{'matches'} and $va{'matches'} > 0){

		(!$in{'nh'}) and ($in{'nh'}=1);
		$first = ($in{'nh'} - 1) * $usr{'pref_maxh'};			
		($va{'pageslist'},$qs) = &pages_list($in{'nh'},"/cgi-bin/mod/$usr{'application'}/dbman",$va{'matches'},$usr{'pref_maxh'});

		my ($sth) = &Do_SQL("SELECT GROUP_CONCAT(ID_creditmemos) FROM sl_creditmemos_payments WHERE ID_orders = '$in{'id_orders'}';");
		my ($id_creditmemos) = $sth->fetchrow();
		my ($mod) = $id_creditmemos ? " OR ID_creditmemos IN ($id_creditmemos) " : '';

		$sth = &Do_SQL("SELECT 
						CONCAT(doc_serial,doc_num) AS invoice
						, cu_invoices.ID_invoices
						, UPPER(invoice_type) AS invoice_type
						, ID_customers
						, ID_orders
						, CONCAT(customer_fcode,' ',customer_fname) AS NAME
						, cu_invoices.Status
						, DATE(cu_invoices.doc_date)Date
						, doc_serial
						, doc_num
						, cu_invoices.invoice_total
				FROM cu_invoices_lines
				INNER JOIN cu_invoices ON cu_invoices.ID_invoices = cu_invoices_lines.ID_invoices
				WHERE 1
					AND (ID_orders = '$in{'id_orders'}' $mod )
					AND cu_invoices.Status <> 'Void'
				GROUP BY ID_invoices
				ORDER BY ID_invoices DESC");#LIMIT $first,$usr{'pref_maxh'};
		
		while ($rec = $sth->fetchrow_hashref){

			$d = 1 - $d;
			my $pdf_name = $rec->{'doc_serial'}.'_'.$rec->{'doc_num'};

			# my $link_pdf = $in{'e'} == 4 ? "/finkok/Facturas/?action=showPDF&id_invoices=$rec->{'ID_invoices'}&e=4" : "/cfdi/pages/cfdi/cfdi_doc.php?f=".encode_base64($pdf_name.".pdf")."&id=$rec->{'ID_invoices'}&m=2&readXml=1&e=$in{'e'}";
			my $link_pdf = "/finkok/Facturas/?action=showPDF&id_invoices=$rec->{'ID_invoices'}&e=".$in{'e'};
			my $link_xml = "/finkok/Facturas/?action=downloadXML&id_invoices=$rec->{'ID_invoices'}&e=".$in{'e'};

			$va{'searchresults'} .= "<tr bgcolor='$c[$d]'>\n";
			$va{'searchresults'} .= "   <td class='smalltext'>";
			if($rec->{'Status'} eq 'Certified' or $rec->{'Status'} eq 'Cancelled'){
				$va{'searchresults'} .= "   <a href='$link_pdf' target='_blank'><img src='[va_imgurl]/[ur_pref_style]/pdf.gif' title='Ver PDF' alt='PDF' border='0'></a>&nbsp;";
				$va{'searchresults'} .= "   <a href='$link_xml' target='_blank'><img src='[va_imgurl]/[ur_pref_style]/xml_dwd.gif' title='Descargar XML' alt='PDF' border='0' style='width: 18px;'></a>";
			}
			$va{'searchresults'} .= "   </td>";
									"   <td class='smalltext'></td>\n";
			$va{'searchresults'} .= "   <td class='smalltext'><a href=\"/cgi-bin/mod/$usr{'application'}/dbman?cmd=opr_invoices&view=$rec->{'ID_invoices'}\">$rec->{'ID_invoices'}</a></td>\n";
			$va{'searchresults'} .= "   <td class='smalltext'>$rec->{'invoice'}</td>\n";
			$va{'searchresults'} .= "   <td class='smalltext'>$rec->{'invoice_type'}</td>\n";
			$va{'searchresults'} .= "   <td class='smalltext'><a href=\"/cgi-bin/mod/$usr{'application'}/dbman?cmd=opr_customers&view=$rec->{'ID_customers'}\">($rec->{'ID_customers'}) $rec->{'NAME'}</a></td>\n";
			$va{'searchresults'} .= "   <td class='smalltext'>".&format_price($rec->{'invoice_total'})."</td>\n";
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
					WHERE ID_orders = '".$in{'id_orders'}."' 
					  AND sl_orders_products.Status IN('Active') 
					  AND sl_orders_products.SalePrice >= 0
					GROUP BY IF(Related_ID_products IS NULL,sl_orders_products.ID_products,Related_ID_products);");
	my ($rec_upc);
	my $invalid_upc = 0;
	while ($rec_upc = $sth_upc->fetchrow_hashref) {
		if ($rec_upc->{'UPC'} eq '') {
			$invalid_upc = 1;
			if ($rec_upc->{'ID_products'}>=600000000 or ($rec_upc->{'ID_products'}>=100000000 and $rec_upc->{'ID_products'}<200000000)) {
				$invalid_upc = 0;
			}
			
		}
		
	}

	if ($invalid_upc) {
		$va{'geninvoice'} = '<span class="smallfieldterr">'.&trans_txt('opr_orders_invoice_invalid_upc').'</span>';
	} else {
		# Validation: ordered vs invoiced		
		my ($sth) = &Do_SQL("SELECT COUNT(*)pend_invoiced
		,(SELECT COUNT(*) FROM sl_orders_products WHERE sl_orders_products.ID_orders = '$in{'id_orders'}' AND Status NOT IN('Order Cancelled','Inactive'))ordered
		,(SELECT COUNT(*) FROM sl_orders_products WHERE sl_orders_products.ID_orders = '$in{'id_orders'}' AND Status NOT IN('Order Cancelled','Inactive')AND SalePrice < 0)creditnote
		FROM sl_orders_products WHERE sl_orders_products.ID_orders = '$in{'id_orders'}' AND Status NOT IN('Order Cancelled','Inactive')
		AND ID_orders_products NOT IN (
			SELECT ID_orders_products FROM cu_invoices_lines INNER JOIN cu_invoices USING(ID_invoices)  WHERE cu_invoices_lines.ID_orders = '$in{'id_orders'}' AND cu_invoices.`Status` NOT IN ('Void','Cancelled') AND cu_invoices.invoice_type != 'traslado' 
		);	");
		my ($pend_invoiced,$prods_ordered,$prods_creditnote) = $sth->fetchrow_array();

		if ($in{'cmd'} eq 'opr_orders') {
			if (&check_permissions('orders_toinvoice','','')) {


				if ($pend_invoiced > 0) {
					$va{'geninvoice'} = qq|<a onclick="return confirm_continue();" href="/cgi-bin/mod/|.$usr{'application'}.qq|/dbman?cmd=opr_orders&view=|.$in{'id_orders'}.qq|&tab=|.$in{'tab'}.qq|&geninvoice=1">|.&trans_txt('opr_orders_generate_invoice').qq|</a>|;

					if ($prods_creditnote > 0) {
						$va{'geninvoice'} .= qq|&nbsp;&nbsp;<a onclick="return confirm_continue();" href="/cgi-bin/mod/|.$usr{'application'}.qq|/dbman?cmd=opr_orders&view=|.$in{'id_orders'}.qq|&tab=|.$in{'tab'}.qq|&geninvoice=1&creditnote=1">|.&trans_txt('opr_orders_generate_creditnote').qq|</a>|;
					}
				}elsif ($prods_ordered == 0){
				 	$va{'geninvoice'} = '<span class="smallfieldterr">'.&trans_txt('opr_orders_invoice_noitems').'</span>';
				}

				$_val = &Do_SQL(qq|SELECT  IF( count(*) >= 1, 'Yes', 'No' ) transfer 
				FROM sl_orders
				INNER JOIN sl_zones ON sl_zones.ID_zones = sl_orders.ID_zones
				WHERE 1
					AND sl_orders.ID_orders = $in{'id_orders'}
					AND sl_zones.BorderZone = 'Yes'
					AND sl_orders.Status = 'Processed'
					AND sl_orders.Ptype = 'COD';|)->fetchrow();
				
				if($_val eq 'Yes'){
					$va{'geninvoice'} .= qq| <a onclick="return confirm_continue();" href="/cgi-bin/mod/|.$usr{'application'}.qq|/dbman?cmd=opr_orders&view=|.$in{'id_orders'}.qq|&tab=|.$in{'tab'}.qq|&geninvoice=1&transferinvoice=1">|.&trans_txt('opr_orders_generate_transfer_invoice').qq|</a>|;
				}
			}else {
				$va{'geninvoice'} = '<span class="smallfieldterr">'.&trans_txt('opr_orders_invoice_noauth').'</span>';
			}
		}	
	}
}

#############################################################################
#############################################################################
#   Function: load_tabs14
#
#       Es: Informacion basica del pago
#       En: Payments Info Basic
#
#
#    Created on: 
#
#    Author: Alejandro Diaz
#
#    Modifications:
#
#        - Modified on 
#
#   Parameters:
#      - 
#
#  Returns:
#
#      - 
#
#   See Also:
#
#
sub load_tabs14{
########################
##   Tab14.- Payments Info Basic ##
########################
					
	my (@c) = split(/,/,$cfg{'srcolors'});
	my ($sth) = &Do_SQL("SELECT COUNT(*) FROM sl_orders_payments WHERE ID_orders = '$in{'id_orders'}'");
	$va{'matches'} = $sth->fetchrow;
	if ($va{'matches'}>0){
	my ($sth) = &Do_SQL("SELECT ID_orders_payments, ID_orders, Type, Amount, IF(Captured ='Yes','Yes','No')Captured, CapDate, AuthCode, Status FROM sl_orders_payments WHERE ID_orders =  $in{'id_orders'} ORDER BY Date DESC;");
		($va{'pageslist'},$qs) = &pages_list($in{'nh'},"/cgi-bin/mod/$usr{'application'}/dbman",$va{'matches'},$usr{'pref_maxh'});								
		while ($rec = $sth->fetchrow_hashref){
			
			$d = 1 - $d;
			my ($img_captured) = ($rec->{'Captured'} eq 'Yes')? 'yes':'no';
			$decor = ($col->{'Status'} eq 'Inactive')? " style=' text-decoration: line-through'":"";
			$va{'searchresults'} .= "<tr bgcolor='$c[$d]'>\n";
			$va{'searchresults'} .= "		<td class='smalltext'>$rec->{'ID_orders_payments'}</td>\n";
			$va{'searchresults'} .= "		<td class='smalltext'>$rec->{'ID_orders'}</td>\n";
	    	$va{'searchresults'} .= "		<td class='smalltext'>$rec->{'Type'}</td>\n";
			$va{'searchresults'} .= "		<td class='smalltext' $decor align='right'>".&format_price($rec->{'Amount'})."</td>\n";
			$va{'searchresults'} .= "		<td class='smalltext' align='center'><img src='/sitimages/status_payments/".lc($rec->{'Status'}).".png' title='Status Payment' alt='Status Payment' border='0'></td>\n";
			$va{'searchresults'} .= "		<td class='smalltext' align='right'>
												<img src='/sitimages/status_payments/".$img_captured.".png' title='' alt='' border='0'>";
			# $va{'searchresults'} .= "			<br />$rec->{'CapDate'}" if ($rec->{'CapDate'});
			# $va{'searchresults'} .= "			<br />$rec->{'AuthCode'}" if ($rec->{'AuthCode'});
			$va{'searchresults'} .= "		</td>\n";
			$va{'searchresults'} .= "</tr>\n";
		}
	}else{
		$va{'pageslist'} = 1;
		$va{'searchresults'} = qq|
			<tr>
				<td colspan='6' align="center">|.&trans_txt('search_nomatches').qq|</td>
			</tr>\n|;
	}
	
}

#############################################################################
#############################################################################
#   Function: load_tabs14
#
#       Es: Informacion basica del pago
#       En: Payments Info Basic
#
#
#    Created on: 
#
#    Author: Alejandro Diaz
#
#    Modifications:
#
#        - Modified on 
#
#   Parameters:
#      - 
#
#  Returns:
#
#      - 
#
#   See Also:
#
#
sub load_tabs15{
########################
##   Tab15.- Tickets
########################
					
	my (@c) = split(/,/,$cfg{'srcolors'});
	my ($sth) = &Do_SQL("SELECT COUNT(*) FROM sl_crmtickets WHERE ID_ref = '$in{'id_orders'}' and ID_type='orders'");
	$va{'matches'} = $sth->fetchrow;
	if ($va{'matches'}>0){
		my ($sth) = &Do_SQL("SELECT 
								ID_crmtickets
								, sl_crmtickets.Date
								, sl_crmtickets.Time
								, sl_crmtickets_type.Description
								, sl_crmtickets.Status 
							FROM sl_crmtickets 
								LEFT JOIN sl_crmtickets_type ON sl_crmtickets.ID_crmtickets_type = sl_crmtickets_type.ID_crmtickets_type 
							WHERE ID_ref = '$in{'id_orders'}' 
								AND ID_type='orders' 
							ORDER BY Date DESC;");
		($va{'pageslist'},$qs) = &pages_list($in{'nh'},"/cgi-bin/mod/$usr{'application'}/dbman",$va{'matches'},$usr{'pref_maxh'});										
		while ($rec = $sth->fetchrow_hashref){
			
			$d = 1 - $d;
			my ($img_captured) = ($rec->{'Captured'} eq 'Yes')? 'yes':'no';
			#$decor = ($col->{'Status'} eq 'Inactive')? " style=' text-decoration: line-through'":"";
			$va{'searchresults'} .= "<tr bgcolor='$c[$d]'>\n";
			$va{'searchresults'} .= "		<td class='smalltext'><a href='/cgi-bin/mod/$usr{'application'}/dbman?cmd=opr_crmtickets&view=$rec->{'ID_crmtickets'}'>$rec->{'ID_crmtickets'}</a></td>\n";
			$va{'searchresults'} .= "		<td class='smalltext'>$rec->{'Description'}</td>\n";
	    	$va{'searchresults'} .= "		<td class='smalltext'>$rec->{'Time'} $rec->{'Date'} </td>\n";
	    	$va{'searchresults'} .= "		<td class='smalltext'>$rec->{'Status'}</td>\n";
			$va{'searchresults'} .= "</tr>\n";
		}
	}else{
		$va{'pageslist'} = 1;
		$va{'searchresults'} = qq|
			<tr>
				<td colspan='4' align="center">|.&trans_txt('search_nomatches').qq|</td>
			</tr>\n|;
	}
	
}


#############################################################################
#############################################################################
#   Function: load_tabs16
#
#       Es: Items originales de la Orden
#       En: 
#
#
#    Created on: 
#
#    Author: Fabian Cañaveral
#
#    Modifications:
#
#        - Modified on 
#
#   Parameters:
#      - 
#
#  Returns:
#
#      - 
#
#   See Also:
#
#
sub load_tabs16{
########################
##   Tab15.- Items Originales
########################
	my ($items) = &Do_SQL("SELECT 
		op.*
	FROM sl_orders_products op
	WHERE 1
		AND op.ID_orders=$in{'id_orders'}
		AND op.original = 1
	ORDER BY op.ID_orders_products,op.Date,op.Time");

	$va{'searchresults'} = '';	
	$i = 0;
	while ($col = $items->fetchrow_hashref) {
		$i++;
		$sku_id_p=$col->{'Related_ID_products'}-400000000;
		$sku_id_e=$col->{'Related_ID_products'};
		$sku_id_d=format_sltvid($col->{'Related_ID_products'});
		my $cmdorder = 'opr_orders';
		my $tax_price = ($col->{'Quantity'} > 0) ? ($col->{'Tax'} / $col->{'Quantity'} ): 0;
		my $unit_price = ($col->{'Quantity'} > 0) ? ($col->{'SalePrice'} / $col->{'Quantity'} ): 0;
		$unit_price = round($unit_price + $tax_price,2);
		my $total_price = round($col->{'SalePrice'} - $col->{'Discount'} + $col->{'Shipping'} + $col->{'Tax'} + $col->{'ShpTax'},2);


		# if ($col->{'Status'} ne 'Inactive'){

		$tot_qty += $col->{'Quantity'};
		$tot_ord += $total_price; #$col->{'SalePrice'};

		# }

		if(substr($col->{'Related_ID_products'},0,1) == 6){

				(substr($col->{'Related_ID_products'},0,1) == 6) and ($col->{'Related_ID_products'} = substr($col->{'Related_ID_products'},5));
			$va{'searchresults'} .= "<tr bgcolor='$c[$d]' onmouseover='m_over(this)' onmouseout='m_out(this)'>\n";
			$va{'searchresults'} .= " <td class='smalltext' valign='top'>";

			$va{'searchresults'} .= qq| <a href="/cgi-bin/mod/$usr{'application'}/dbman?cmd=$linkser&view=$col->{'Related_ID_products'}"><img src='$va{'imgurl'}/$usr{'pref_style'}/b_view.gif' title='View' alt='' border='0'></a>|;
			my ($sth5) = &Do_SQL("SELECT * FROM sl_services WHERE ID_services = '$col->{'Related_ID_products'}' ;");
			$serdata = $sth5->fetchrow_hashref;
			$col->{'SerialNumber'}='';
			$col->{'ShpProvider'}='';
			$col->{'Tracking'}='';
			$col->{'ShpDate'}='';
			$va{'searchresults'} .= "<br>".&format_sltvid(600000000+$col->{'Related_ID_products'})."</td>\n";		
			$va{'searchresults'} .= "  <td class='smalltext'>$tmp{'model'}<br>".substr($serdata->{'Name'},0,30)."</td>\n";
			$va{'searchresults'} .= "  <td class='smalltext' valign='top'>".&build_tracking_link($col->{'Tracking'},$col->{'ShpProvider'},$col->{'ShpDate'},600000000+$col->{'Related_ID_products'})."</td>\n";			

			$va{'searchresults'} .= "  <td class='smalltext' align='right' valign='top' $decor>".&format_price($unit_price)."</td>\n";
			$va{'searchresults'} .= "  <td class='smalltext' align='right' valign='top' $decor>".&format_price(($col->{'Discount'}*-1))."</td>\n";
			$va{'searchresults'} .= "  <td class='smalltext' align='right' valign='top' $decor>N/A&nbsp;&nbsp;&nbsp;</td>\n";
			$va{'searchresults'} .= "  <td class='smalltext' align='right' valign='top' $decor>".&format_number($col->{'Quantity'}). "</td>\n";
			$va{'searchresults'} .= "  <td class='smalltext' align='right' valign='top' $decor nowrap>".&format_price($total_price);
			#Se comenta edici�n de productos
			if (&check_permissions('edit_order_edit_price','','')){
				$va{'searchresults'} .= qq| <div id="divpayment$rec->{'ID_orders_products'}"><a href="#tabs" onClick="popup_show('ajax_windows', 'ajax_drag', 'ajax_exit', 'element-right', -1, -1,'tabs');loadDoc('/cgi-bin/common/apps/ajaxbuild?ajaxbuild=edit_products&id_orders=$col->{'ID_orders'}&id_orders_products=$col->{'ID_orders_products'}&cmd=$in{'cmd'}&script_url=/cgi-bin/mod/$usr{'application'}/dbman');"><img src='$va{'imgurl'}/$usr{'pref_style'}/b_edit.png' title='Edit In Clean up Mode' alt='' border='0'/></a></div>|;
			}
			$va{'searchresults'} .= "</td>\n";
			$va{'searchresults'} .= "</tr>\n";
		}elsif(substr($col->{'ID_products'},0,1) == 8){

			my ($sth5) = &Do_SQL("SELECT ID_creditmemos FROM sl_creditmemos_payments WHERE ID_orders_products_added = '$col->{'ID_orders_products'}' ;");
			$col->{'ID_creditmemos'} = $sth5->fetchrow();
			$va{'searchresults'} .= "<tr bgcolor='$c[$d]' onmouseover='m_over(this)' onmouseout='m_out(this)'>\n";
			$va{'searchresults'} .= " <td class='smalltext' valign='top'>";
			$va{'searchresults'} .= qq| <a href="/cgi-bin/mod/$usr{'application'}/dbman?cmd=opr_creditmemos&&view=$col->{'ID_creditmemos'}"><img src='$va{'imgurl'}/$usr{'pref_style'}/b_view.gif' title='View' alt='' border='0'></a>| if ($col->{'ID_creditmemos'}>0);
			$va{'searchresults'} .= "<br>".&format_sltvid($col->{'ID_products'})."</td>\n";		
			$va{'searchresults'} .= "  <td class='smalltext'>Credit Memo : $col->{'ID_creditmemos'}</td>\n";
			$va{'searchresults'} .= "  <td class='smalltext' valign='top'></td>\n";			
			if ($col->{'Status'} eq 'Inactive'){
					$decor = " style=' text-decoration: line-through'";
			}else{
					$decor ='';
			}

			$va{'searchresults'} .= "  <td class='smalltext' align='right' valign='top' $decor>".&format_price($unit_price)."</td>\n";
			$va{'searchresults'} .= "  <td class='smalltext' align='right' valign='top' $decor>".&format_price(($col->{'Discount'}*-1))."</td>\n";
			$va{'searchresults'} .= "  <td class='smalltext' align='right' valign='top' $decor>N/A&nbsp;&nbsp;&nbsp;</td>\n";
			$va{'searchresults'} .= "  <td class='smalltext' align='right' valign='top' $decor>".&format_number($col->{'Quantity'})."</td>\n";
			$va{'searchresults'} .= "  <td class='smalltext' align='right' valign='top' $decor nowrap>".&format_price($total_price);
			$va{'searchresults'} .= "</td>\n";
			$va{'searchresults'} .= "</tr>\n";

				my ($sthk) = &Do_SQL("SELECT * FROM sl_skus WHERE ID_sku_products='$col->{'ID_products'}'");
		}else{

			my (%tmp);
			$va{'searchresults'} .= "<tr bgcolor='$c[$d]' onmouseover='m_over(this)' onmouseout='m_out(this)'>\n";
			$va{'searchresults'} .= " <td class='smalltext' valign='top'>";

        	### Products
        	$va{'searchresults'} .= qq| <a href="/cgi-bin/mod/$usr{'application'}/dbman?cmd=$linkparts&&view=$sku_id_p"><img src='$va{'imgurl'}/$usr{'pref_style'}/b_view.gif' title='View' alt='' border='0'></a>|;
        	$va{'searchresults'} .= qq| <a href="/cgi-bin/mod/$usr{'application'}/dbman?cmd=$linkpack&view=$in{'id_orders'}&ID_orders_products=$col->{'ID_orders_products'}&choices=$choices"><img src='$va{'imgurl'}/$usr{'pref_style'}/b_packinglist.gif' title='Packing List' alt='' border='0'></a>|;
        	$va{'searchresults'} .= "<br>".&format_sltvid($col->{'Related_ID_products'});
			$va{'searchresults'} .= "</td>\n";
			(!$col->{'SerialNumber'}) and ($col->{'SerialNumber'} = '---');

			($status,%tmp) = &load_product_info($sku_id_p);
			&load_cfg('sl_orders');
			$cadname=&load_name('sl_parts','ID_parts',$sku_id_p,'Name');
				$cadname=substr($cadname,0,30);
			$cadmodel=&load_name('sl_parts','ID_parts',$sku_id_p,'Model');

				if ($col->{'Amazon_ID_products'}){
					my ($sthAzn) = &Do_SQL("SELECT Name FROM cu_products_amazon WHERE ID_products_amazon = '$col->{'Amazon_ID_products'}';");
					$cadname = $sthAzn->fetchrow_array();
					$cadname=substr($cadname,0,30);
					$cadname = qq|<a href="/cgi-bin/mod/$usr{'application'}/dbman?cmd=mer_products_amazon&view=$col->{'Amazon_ID_products'}">$cadname</a>|;
				}
			
				$va{'searchresults'} .= "  <td class='smalltext' valign='top'>$cadmodel<br>".$cadname." ".$choices."</td>\n";
			$va{'searchresults'} .= "  <td class='smalltext' valign='top'></td>\n";

		
			my $split_qty = '';
			
			$add_original_qty = '';

			$va{'searchresults'} .= "  <td class='smalltext' align='right' valign='top' $decor>".&format_price($unit_price)."</td>\n";
			$va{'searchresults'} .= "  <td class='smalltext' align='right' valign='top' $decor>".&format_price(($col->{'Discount'}*-1))."</td>\n";
			$va{'searchresults'} .= "  <td class='smalltext' align='right' valign='top' $decor>".&format_price($col->{'Shipping'} + $col->{'ShpTax'})."";
			$va{'searchresults'} .= "  <td class='smalltext' align='right' valign='top' $decor>".&format_number($col->{'Quantity'}). $add_original_qty . $split_qty. "</td>\n";
			$va{'searchresults'} .= "  </td>\n<td class='smalltext' align='right' valign='top' $decor nowrap>".&format_price($total_price);
			
			$va{'searchresults'} .= "</td>\n";
			$va{'searchresults'} .= "</tr>\n";	
		}



	}
	$va{'searchresults'} .= qq|
			<tr>
				<td colspan='7' class='smalltext' align="right">|.&trans_txt('mer_vpo_total').qq|</td>
				<td align="right" class='smalltext' style="border-top:thick double #808080;">|.&format_price($tot_ord).qq|</td>
			</tr>\n|;
	$va{'matches'} = $i;

}

1;
