#!/usr/bin/perl
##################################################################
############                HOME                 #################
##################################################################

#if ($in{'clr_cust'}){
#	delete($cses{'id_customers'});
#}
	
sub confirm_customer {
# --------------------------------------------------------
# Created on: 10/26/2007 4:43PM
# Author: Rafael Sobrino
# Description : Creates a link that allows the rep to remove the id_customers value from the session

	if ($in{'id_customers'} >0 and $in{'step'} >1){
		return "[<a href='?cmd=console_order&clr_cust=1&step=$in{'step'}'> Nuevo Cliente </a>]";
	}
}

sub search_options {
# --------------------------------------------------------

# Author: Unknown
# Created on: Unknown
# Last Modified on: 07/28/2008
# Last Modified by: Jose Ramirez Garcia
# Description : 'SmallDescription','Description','SmallDescription_en','Description_en', were included in the keyword product search
# Forms Involved: 
# Parameters :
#
# Last Modified on: 09/15/08  11:14:49
# Last Modified by: Roberto Barcenas
# Last Modified Desc: $in{'tuser} . sltv web users are allowed to search and Add On-Air and Web Only Products
# Last Modified on: 03/17/09 16:36:21
# Last Modified by: MCC C. Gabriel Varela S: Par�metros para sltv_itemshipping. Se considera Ship COD
# Last Modified RB: 04/17/09  16:01:10 -- Se filtra la busqueda por DID.
# Last Modified on: 04/21/09 10:13:42
# Last Modified by: MCC C. Gabriel Varela S: Se corrige filtrado por DID.
# Last Modified on: 04/24/09 10:07:45
# Last Modified by: MCC C. Gabriel Varela S: Se corrige filtrado por DID para cuando no exista $cses{'id_dids'}
# Last Modified on: 07/07/09 19:50:56
# Last Modified by: MCC C. Gabriel Varela S: Se cambian los precios por download #
# Last Modified RB: 09/08/09  18:20:44 -- Se agrega opcion para desbloqueo de downsaleprice de acuerdo a codigo de autorizacion generado desde modulo supervisor
# Last Modified RB: 12/07/2010  19:06:44 -- Se agregan parametros para calculo de shipping
# Last Modified RB: 01/10/11  23:20:44 -- Se agrega busqueda de precio con tax incluido de acuerdo a zipcode
# Last Modified RB: 01/12/11  21:15:44 -- Se cambia modo de muestra de tabla por un fancybox
# Last Modified RB: 01/18/11  19:00:44 -- Se agrega calculo de shipping y precio total en la tabla fancybox
# Last Modified by RB on 04/15/2011 12:40:52 PM  : Se agrega cero(id_orders) como parametro para funcion calculate_taxes 
# Last modified on 6 May 2011 15:39:47
# Last modified by: MCC C. Gabriel Varela S. : Se hace que se filtre por grupo tambi�n.
# Last Modified by RB on 06/07/2011 01:25:41 PM : Se agrega City como parametro para calculate_taxes
# Last Time Modified by RB on 11/07/2011: Se agrego arbol de decision 
# Last Time Modified by RB on 11/09/2011: Se agergo pricetype(gross) para no calcular precios de envio e impuestos
# Last Time Modified by RB on 03/06/2012: Se agrego calculo de comision maxima para operadores de inbound
 	my ($pid);
	my $user_type;
	$user_type=&load_name('admin_users','ID_admin_users',$usr{'id_admin_users'},'user_type');

	##### SEARCHING CUSTOMERS ######
	if ($in{'customers'}){
		return &search_cust_options;
	}
	##### SEARCHING PRODUCTS ######
	if ($in{'action'} eq 'add_to_basket'){
		
		$va{'speechname'}= 'ccinbound:2c- Continue Shopping';
		return &build_page("console_search_add_another.html");

	}elsif($in{'action'} eq 'search'){

		##user type = sltv web is also allowed to see Web Only Products 
		$in{'tuser'} =  " = 'On-Air' ";
		$in{'tuser'} =  " IN('On-Air','Pauta Seca') " if ($cfg{'pauta_seca_enabled'} and $cfg{'pauta_seca_enabled'} == 1);
		($usr{'user_type'} eq 'sltv web') and ($in{'tuser'} =  " IN ('On-Air','Web Only') ");
		
		## El producto debe estar ligado al DID o bien no estar ligado a ningun DID para poderse mostrar
		$query_did = " AND (0 < (SELECT COUNT(ID_products) FROM sl_products_dids WHERE ID_products = sl_products.ID_products AND ID_dids = $cses{'id_dids'}) 
										OR 1 > (SELECT COUNT(ID_products) FROM sl_products_dids WHERE ID_products = sl_products.ID_products)) "if($cses{'id_dids'});
		
		if($in{'id_products'} and length($in{'id_products'}) == 4){
			my($sth) = &Do_SQL("SELECT COUNT(*) FROM sl_services WHERE ID_services = '$in{'id_products'}' ");
			$matches = $sth->fetchrow;
			if($matches > 0){
				&load_cfg('sl_services');
				my (%tmp) = &get_record('ID_services',$in{'id_products'},'sl_services');
				foreach my $key (keys %tmp){
					$in{$key} = $tmp{$key};
				}
				$va{'id_products'} = &format_sltvid(600000000+$in{'id_services'});
				
				return &build_page("console_search_showservices.html");
			}else{
				$va{'message'} = &trans_txt('search_noitem');
				$error{'id_products'} = &trans_txt('invalid');
				return &build_page("console_search_form.html");
			}	
		}
		
		if ($in{'pricerange'}){
			($form,$to) = split(/-/,$in{'pricerange'});
			$from =~ s/\$ //g;
			$to =~ s/\$ //g;
			$in{'from_sprice'} = $form;
			$in{'to_sprice'} = $to;
		}elsif ($in{'filter'} eq 'onairnow'){
			## productos pautados hoy
			my ($p);
			my ($sth0) = &Do_SQL("SELECT `Offer` FROM `sl_mediacontracts` WHERE `ESTDay`=CURDATE() GROUP BY `Offer`");
			while (my $key = $sth0->fetchrow){
				my ($sth2) = &Do_SQL("SELECT Pattern FROM `sl_media_prodfam` WHERE '$key' REGEXP Pattern");
				$p = $sth2->fetchrow;
				$in{'name'} .=  "$p|" if ($p);
			}
			chop($in{'name'});
			$in{'st'} = 'or';

		}elsif ($in{'filter'} eq 'proghoy'){
			$in{'id_mediacontracts'} = int($in{'id_mediacontracts'});
			if ($in{'id_mediacontracts'}>0){
				my ($sth0) = &Do_SQL("SELECT `Offer` FROM `sl_mediacontracts` WHERE ID_mediacontracts='$in{'id_mediacontracts'}'");
				while (my $key = $sth0->fetchrow){
					my ($sth2) = &Do_SQL("SELECT Pattern FROM `sl_media_prodfam` WHERE '$key' REGEXP Pattern");
					$p = $sth2->fetchrow;
					$in{'name'} .=  "$p|" if ($p);
				}
				chop($in{'name'});
				$in{'st'} = 'or';
			}else{
				## productos pautados hoy
				$va{'searchresults'} = &load_planning();
				return &build_page("console_planning.html");
			}
		}elsif ($in{'filter'} eq 'topsales'){
			my ($sth0) = &Do_SQL("SELECT RIGHT( sl_orders_products.ID_products, 6 ) AS ID_products, COUNT( * ) AS total 
													FROM sl_orders_products , sl_products
													WHERE sl_products.ID_products = RIGHT( sl_orders_products.ID_products, 6 )
													AND DATE_SUB(CURDATE(), INTERVAL 7 DAY)>=sl_orders_products.Date
													AND sl_orders_products.Status = 'Active'
													AND sl_products.Status $in{'tuser'} 
													AND sl_products.Sprice>5
													$query_did
													GROUP BY RIGHT( sl_orders_products.ID_products, 6 )
													ORDER BY total DESC LIMIT 10 ");
									
			while ($rec = $sth0->fetchrow_hashref){
				$in{'id_products'} .= $rec->{'ID_products'}."|";
			}
			$in{'st'} = 'or';
		}elsif ($in{'filter'} eq 'lastorder'){
			my($sth0) = &Do_SQL("SELECT RIGHT(sl_orders_products.ID_products,6) AS ID_products 
			FROM sl_orders_products 
			inner join sl_products on sl_products.ID_products=RIGHT(sl_orders_products.ID_products,6)
			WHERE sl_orders_products.ID_admin_users=$usr{'id_admin_users'} 
			and (user_type like '%$user_type%' or user_type='' or isnull(user_type))
			ORDER BY sl_orders_products.Date DESC");
			while ($rec = $sth0->fetchrow_hashref){
				++$cses{'items_in_basket'};
				$in{'id_products'} = &load_name('sl_skus','ID_products',$rec->{'ID_products'},'ID_sku_products');
				$cses{'items_'.$cses{'items_in_basket'}.'_id'} = $in{'id_products'}; #the console order function reads the id_sku_products to add the item to the basket
				$cses{'items_'.$cses{'items_in_basket'}.'_qty'} = 1;

			}
			
			print "<script>window.location.href = 'admin?cmd=console_order&step=3';</script>";
			#return &build_page("console_order3.html");
		}
		#JRG end#
		if ($in{'id_products'} =~ /\|/){
			#$in{'id_products'} =~ s/\|/,/g;
		}elsif ($in{'id_products'} =~ /(\d{3})[-|,](\d{3})/){
			$in{'id_products'} = "$1$2";
		}elsif ($in{'id_products'} =~ /(\d{6})/){
			$in{'id_products'} = "$1$2";
		}
		@db_cols = ('ID_products','Model','Name','SPrice','SmallDescription','Description','SmallDescription_en','Description_en');
		@headerfields = ('ID_products','Model','Name','SPrice');
    
		if ($in{'id_products'}>0  and length($in{'id_products'}) == 6){

			my ($sth) = &Do_SQL("SELECT COUNT(*) FROM sl_products WHERE Status NOT IN('Testing','Inactive') AND ID_products = '$in{'id_products'}'  $query_did and (user_type like '%$user_type%' or user_type='' or isnull(user_type))");
			if ($sth->fetchrow()>0){

				&load_cfg('sl_products');
				my (%tmp) = &get_record('ID_products',$in{'id_products'},'sl_products');
				
				foreach my $key (keys %tmp){
					$in{$key} = $tmp{$key};
				}

				$va{'speechname'}= 'ccinbound:2b- Product View';
				if($in{'duties'} > 0){	#RB Start - Adding mexican flag if products has mexican duties - apr2808
					$va{'sendoptions'} = qq|
																<tr><td align="center" colspan="2" class="menu_bar_title">Enviamos a</td>
    														</tr><tr><td colspan='2' align="center">
																<img src="$cfg{'path_ns_img'}/default/flag_mexico.gif" title="Mexico">
																</td></tr>|;
				}#RB End				
				
				($va{'shptotal1'},$va{'shptotal2'},$va{'shptotal3'},$va{'shptotal1pr'},$va{'shptotal2pr'},$va{'shptotal3pr'},$va{'shp_text1'},$va{'shp_text2'},$va{'shp_text3'},$va{'shp_textpr1'},$va{'shp_textpr2'},$va{'shp_textpr3'})= &sltv_itemshipping($tmp{'edt'},$tmp{'sizew'},$tmp{'sizeh'},$tmp{'sizel'},$tmp{'weight'},$tmp{'id_packingopts'},$tmp{'shipping_table'},$tmp{'shipping_discount'},$tmp{'id_products'});
				## US Continental
				#RB Start 04/15/08 - Add the submit button only for On-Air Products
				($in{'status'} eq 'On-Air' or ($in{'status'} eq 'Web Only' and $usr{'user_type'} eq 'sltv web')) and ($va{'submit_button'} = '<input type="button" value="Agregar a Carro" class="button" onClick="javascript:submit()">');
				$va{'submit_button'} = '<input type="button" value="Agregar a Carro" class="button" onClick="javascript:submit()">' if($cfg{'pauta_seca_enabled'} and $cfg{'pauta_seca_enabled'} == 1 and !$va{'submit_button'});

				#RB End			
				$va{'shptotal1'} = &format_price($va{'shptotal1'});
				$va{'shptotal2'} = &format_price($va{'shptotal2'});		
				$va{'shptotal3'} = &format_price($va{'shptotal3'});
				$va{'shptotalf'} = &format_price(0);		
				## Puerto Rico
				$va{'shptotal1pr'} = &format_price($va{'shptotal1pr'});
				$va{'shptotal2pr'} = &format_price($va{'shptotal2pr'});
				$va{'shptotal3pr'} = &format_price($va{'shptotal3pr'});
				$va{'shptotalfpr'} = &format_price(0);
				$in{'id_produc'}= $in{'id_products'};
				$va{'id_products'}= &format_sltvid($in{'id_products'});
				
				### Flexipago
				if ($in{'flexipago'} > 1){
					#GV Inicia modificaci�n 26may2008
					if($cses{'dayspay'} eq 15){
						$period = "quincenales";
					} elsif($cses{'dayspay'} eq 30){
						$period = "mensuales";
					} else {
						$period = "";
					}
					#GV Termina modificaci�n 26may2008
					if ($tmp{'downpayment'}>0){
						$va{'flexipago'} = qq|	<tr>
												<td valign='top'>Pago F&aacute;cil : </td>
												<td>Pago Inicial : | . &format_price($tmp{'downpayment'}) . qq|<br>$in{'flexipago'} pagos $period de &format_price(($in{'sprice'}-$tmp{'downpayment'})/$in{'flexipago'})</td>
										    </tr>\n|;
					}else{
						$va{'flexipago'} = qq|	<tr>
												<td>Pago F&aacute;cil : </td>
												<td>$in{'flexipago'} pagos $period de |.&format_price($in{'sprice'}/$in{'flexipago'}).qq|</td>
										    </tr>\n|;
					}
				}
				
				$va{'zipcode'}='n/a';
				($cses{'zipcode_selected'}) and ($va{'zipcode'} = $cses{'zipcode_selected'});
				($cses{'zipcode'}) and ($va{'zipcode'} = $cses{'zipcode'});


				## Net/Gross Prices
				# if($in{'pricetype'} eq 'Gross'){
				# 	$va{'pricetype'}='Gross';
				# 	$va{'fancybox_prices_cities'} = build_page("console_show_prices_gross.html");
				# }else{
					## Cities
					my $this_city;
					my ($sth) = &Do_SQL("SELECT CONCAT(State,'-',StateFullName)AS State, case CityAliasName when CityAliasName is not null then CityAliasName else City end as City, PrimaryRecord FROM sl_zipcodes WHERE ZipCode='$va{'zipcode'}' ORDER BY State,City;");
					if($sth->rows() > 0){
						while(my($state,$city,$primary) = $sth->fetchrow()){
							$va{'cities'} .= '<tr><td align="left">'.$state.'</td><td align="left">'.$city.'</td></tr>';
						}
						$this_city = $city if $primary eq 'P';
					}else{
							$va{'cities'} .= '<tr><td align="center" colspan="2">'.&trans_txt('search_nomatches').'</td></tr>';
					}


					## Prices + Tax + Shipping - Fancybox Table
					#my $state = &load_name('sl_zipcodes','ZipCode',$va{'zipcode'},"State");
					my $state = &load_db_names('sl_zipcodes','ZipCode',$va{'zipcode'},"[State]-[StateFullName]");
					my $taxes = &calculate_taxes($va{'zipcode'},$state,$this_city,0);


					#ADG este query me trae la tasa de impuesto que se utilizara para comparar contra la que usa el taxstate y taxcity
					# Se hace una validacion para ver la tasa de impuesto que aplica al producto
					#ADG MX
					if(uc($cfg{'country'}) eq 'MX')  {
						my ($sth) = &Do_SQL("SELECT max(sale_tax) FROM (
						SELECT if(sale_tax is null,0,sale_tax) as sale_tax
						FROM sl_skus_parts
						inner join sl_parts using(ID_parts)
						inner join sl_skus using(ID_sku_products)
						where ID_products='$in{'id_products'}')taxes");
						my($tax_product) = $sth->fetchrow();
						#cehcar siempre que el obternido sea > 0 par que sea valido
						if($tax_product > 0) {
							$tax_product = ($tax_product/100);
						}else {
							$tax_product = 0;
						}

						# NO ES LO MISMO 0 A QUE TENGA UN NULL EN EL TAX SALE DE UN PRODUCTO
						# METEMOS LA REGLA DE COMPARACION CLIENTE 
						if($tax_product < $taxes) {
							$taxes = $tax_product;
						}
					
					}
					#########################################ADG<-
					
					$va{'taxes'} = $taxes*100;

					## Fixed/Variable/Table Shipping ?
					my $shpcal  = &load_name('sl_products','ID_products',$in{'id_products'},'shipping_table');
					my $shpmdis = &load_name('sl_products','ID_products',$in{'id_products'},'	shipping_discount');
					my $idpacking = &load_name('sl_products','ID_products',$in{'id_products'},'ID_packingopts');
					($shptotal1,$shptotal2,$shptotal3,$shptotal1pr,$shptotal2pr,$shptotal3pr,$va{'shp_text1'},$va{'shp_text2'},$va{'shp_text3'},$va{'shp_textpr1'},$va{'shp_textpr2'},$va{'shp_textpr3'})= &sltv_itemshipping($cses{'edt'},$cses{'items_'.$i.'_size'},1,1,$cses{'items_'.$i.'_weight'},$idpacking,$shpcal,$shpmdis,$in{'id_products'});

					my $shp = $state=='PR-Puerto Rico' ? $shptotal1pr : $shptotal1;


					$va{'pprice'} = &format_price($in{'sprice'}+($in{'sprice'}*$taxes),2);
					$va{'spricet'} = &format_number($in{'sprice'},2);
					$va{'tsprice'} = &format_number($in{'sprice'} * $taxes,2);

					## Calculo de comision maxima
					my ($sth) = &Do_SQL("SELECT pbase_order,pbase_sale,tdc_C55*100/100,ticket_c200*100/100 FROM sl_rewards WHERE user_type = '$usr{'user_type'}';");
					my ($pbase_order, $pbase_sale,$bono_tdc,$bono_ticket) = $sth->fetchrow();

					my $base_order = $pbase_order ? $in{'sprice'} * $pbase_order / 100 : 0;
					my $pct_max = round($pbase_sale + $bono_ticket + $bono_tdc, 2);
					my $sprice_bonus = $base_order ? $in{'sprice'} * $pct_max /100 : 0;

					$va{'reward_info'} = '<p align="left" style="font-size:x-small;margin:10px;">* Comisi&oacute;n aproximada  basada en porcentaje m&aacute;ximo de ganancia <font color="red">('.$pct_max.'%)</font></p>' if $sprice_bonus;

					$va{'price_taxes'} .= qq|<tr>
											<td align="left">Al Aire</td>
											<td align="right">|.&format_price($in{'sprice'}) . qq|</td>
											<td align="right">|.&format_price($va{'tsprice'}). qq|</td>
											<td align="right">|.&format_price($shp,2). qq|</td>
											<td align="right">|.&format_price($in{'sprice'} + $shp + ($in{'sprice'} * $taxes),2). qq|</td>
											<td align="right">* |.&format_price($sprice_bonus).qq|</td>
										</tr>|;

					########
					######## Metodos de pago aceptados
					########					
					my ($sth) = &Do_SQL("SELECT ID_zones,Name,Payment_Type,ExpressShipping FROM sl_zones INNER JOIN sl_zipcodes USING(ID_zones) WHERE ZipCode = '$va{'zipcode'}';");
					my ($idz,$zn,$pt,$es) = $sth->fetchrow();

					$va{'paytype_accepted'} = '';
					$va{'zone_name'} = '';
					$va{'warehouses_zone'} = '';
					$va{'express_allowed'} = ($cfg{'express_delivery'} and $in{'expressshipping'} eq 'Yes' and $es eq 'Yes') ? 'on' : 'off';


					if($pt ne ''){

						$va{'zone_name'} = $zn;
						my @ary = split(/,/, $pt);
						for(0..$#ary){

							if($_ == 0){
								$va{'paytype_accepted'} .= qq|<tr>\n|;
							}elsif($_ % 3 == 0){
								$va{'paytype_accepted'} .= qq|</tr>\n<tr>\n|;
							}

							$va{'paytype_accepted'} .= qq|<td style="height:60px;width:100px;background:#F39814;color:#FFFFFF;text-align:center;font-size:1.2em" align="center">$ary[$_]</td>|;

						}

						my $x = 0;
						my ($sth1) = &Do_SQL("SELECT Name FROM sl_warehouses INNER JOIN sl_zones_warehouses USING(ID_warehouses) WHERE ID_zones = '$idz';");
						while( my($wn) = $sth1->fetchrow()) {

							if($x == 0){
								$va{'warehouses_zone'} .= qq|<tr>\n|;
							}elsif($x % 3 == 0){
								$va{'warehouses_zone'} .= qq|</tr>\n<tr>\n|;
							}

							$va{'warehouses_zone'} .= qq|<td style="height:60px;width:100px;background:#F39814;color:#FFFFFF;text-align:center;font-size:1.2em" align="center">$wn</td>|;
							$x++;
						}
						(!$x) and (qq|<td style="height:60px;width:300px;background:#F39814;color:#FFFFFF" align="center">|.&trans_txt('search_nomatches').qq|</td>|);

					}else{

						$va{'paytype_accepted'} .= qq|<td style="height:60px;width:300px;background:#F39814;color:#FFFFFF" align="center">|.&trans_txt('search_nomatches').qq|</td>|;
						$va{'warehouses_zone'} .= qq|<td style="height:60px;width:300px;background:#F39814;color:#FFFFFF" align="center">|.&trans_txt('search_nomatches').qq|</td>|;

					}

					## Pauta Seca Message
					$va{'display_pauta_seca'} = '<span style="border:solid 1px #D14400;margin-left:15px;padding:5px;width:auto;background-color:#F76925;color:#FFF;font-size:14px;font-weight:bold;">PAUTA SECA</span>' if ($in{'status'} eq 'Pauta Seca');

					$va{'fancybox_prices_cities'} = &console_step2_ajaxinfo();

					$va{'fancybox_prices_cities'} = qq|
					<!-- Fancybox -->
					<a id="fancybox_prices_table" href="#modal_prices_cities">Revisar Tabla</a>
					<div style="display: none;">
						<div id="modal_prices_cities" style="width:500px;overflow:auto;text-align:center;">
							|.$va{'fancybox_prices_cities'}.qq|
						</div>
					</div>
					<!-- Fancybox -->|;

					$va{'calc_price_zipcode'} = qq|
							<input type="text" name="zipcode" value="[va_zipcode]" id="pzipcode" size="5" maxlength="5">
							<input type="button" value="Calcular" id="btn_zipcode" class="button">|;
					
					# Termina Calculo de la comision
					
				#}


				# for my $i(1..4){
				# 	if ($in{'sprice'.$i}!=0) {
				# 		if ($in{'sprice'.$i.'name'}){
				# 			$pname = $in{'sprice'.$i.'name'};
				# 		}else{
				# 			$pname = 'Downsale '. $i;
				# 		}
				# 		my $sprice_bonus = $base_order ? $in{'sprice'.$i} * $pct_max /100 : 0;
				# 		$va{'price_taxes'} .= qq|<tr>
				# 									<td align='left'>$pname</td>
				# 									<td align='right'>|.&format_price($in{'sprice'.$i}).qq|</td>
				# 									<td align='right'>|.&format_price($in{'sprice'.$i} * $taxes,2).qq|</td>
				# 									<td align='right'>|.&format_price($shp,2) . qq|</td>
				# 									<td align='right'>|.&format_price($in{'sprice'.$i} + $shp + ($in{'sprice'.$i} * $taxes),2) . qq|</td>
				# 									<td align='right'>*|.&format_price($sprice_bonus).qq|</td>
				# 								</tr>|;

				# 		if ($cfg{'multiprice_reqpass'}){
				# 			$va{'opt_price'} .= qq|<tr>
				# 							<td width=50% nowrap><span id='span_pricenumber2'><input name='pricenumber2' id='pricenumber2' value='' size='5' maxlength='4' type='text' onFocus='focusOn( this )' onBlur='focusOff( this)' onKeyUp='passdownsale(this.id)';>&nbsp;&nbsp;&nbsp;</span>
				# 								<input type='radio' name='pricenumber' value='2' class='radio' disabled='true'> $pname :</td>
				# 							<td> |.&format_price($in{'sprice'.$i}).qq|</td>
				# 						</tr>|;
				# 		}else{
				# 			$va{'opt_price'} .= qq|<tr>
				# 							<td width=50% nowrap><input type='radio' name='pricenumber' value='|.($i+1).qq|' class='radio'> $pname :</td>
				# 							<td> |.&format_price($in{'sprice'.$i}).qq|</td>
				# 						</tr>|;
				# 		}
				# 	}
				# }
				# # ($in{'sprice2'}!=0) and ($va{'tsprice2'} = &format_price($in{'sprice2'} * $taxes,2)) and ($va{'price_taxes'} .='<tr><td align="left">Downsale 2</td><td align="right">'.&format_price($in{'sprice2'}).'</td><td align="right">'.$va{'tsprice2'}.'</td><td align="right">'.&format_price($shp,2).'</td><td align="right">* '.&format_price($in{'sprice2'} + $shp + ($in{'sprice2'} * $taxes),2).'</td><td align="right">'.&format_price(sprice2_bonus).'</td></tr>') and ($va{'opt_price'} .= qq|<tr><td nowrap><span id="span_pricenumber3"><input name="pricenumber3" id="pricenumber3" value="" size="5" maxlength="4" type="text" onFocus='focusOn( this )' onBlur='focusOff( this)' onKeyUp='passdownsale(this.id)';>&nbsp;&nbsp;&nbsp;</span><input type="radio" name="pricenumber" value="3" class="radio" disabled="true">Downsale 2 :</td><td> |.&format_price($in{'sprice2'}+$va{'tsprice2'},2).qq|</td></tr>|);
				# # ($in{'sprice3'}!=0) and ($va{'tsprice3'} = &format_price($in{'sprice3'} * $taxes,2)) and ($va{'price_taxes'} .='<tr><td align="left">Downsale 3</td><td align="right">'.&format_price($in{'sprice3'}).'</td><td align="right">'.$va{'tsprice3'}.'</td><td align="right">'.&format_price($shp,2).'</td><td align="right">* '.&format_price($in{'sprice3'} + $shp + ($in{'sprice3'} * $taxes),2).'</td><td align="right">'.&format_price($sprice3_bonus).'</td></tr>') and ($va{'opt_price'} .= qq|<tr><td nowrap><span id="span_pricenumber4"><input name="pricenumber4" id="pricenumber4" value="" size="5" maxlength="4" type="text" onFocus='focusOn( this )' onBlur='focusOff( this)' onKeyUp='passdownsale(this.id)';>&nbsp;&nbsp;&nbsp;</span><input type="radio" name="pricenumber" value="4" class="radio" disabled="true">Downsale 3 :</td><td> |.&format_price($in{'sprice3'}+$va{'tsprice3'},2).qq|</td></tr>|);
				# # ($in{'sprice4'}!=0) and ($va{'tsprice4'} = &format_price($in{'sprice4'} * $taxes,2)) and ($va{'price_taxes'} .='<tr><td align="left">Downsale 4</td><td align="right">'.&format_price($in{'sprice4'}).'</td><td align="right">'.$va{'tsprice4'}.'</td><td align="right">'.&format_price($shp,2).'</td><td align="right">* '.&format_price($in{'sprice4'} + $shp + ($in{'sprice4'} * $taxes),2).'</td><td align="right">'.&format_price($sprice4_bonus).'</td></tr>') and ($va{'opt_price'} .= qq|<tr><td nowrap><span id="span_pricenumber5"><input name="pricenumber5" id="pricenumber5" value="" size="5" maxlength="4" type="text" onFocus='focusOn( this )' onBlur='focusOff( this)' onKeyUp='passdownsale(this.id)';>&nbsp;&nbsp;&nbsp;</span><input type="radio" name="pricenumber" value="5" class="radio" disabled="true">Downsale 4 :</td><td> |.&format_price($in{'sprice4'}+$va{'tsprice4'},2).qq|</td></tr>|);
				# ($in{'sprice1'}!=0 or $in{'sprice2'}!=0 or $in{'sprice3'}!=0 or $in{'sprice4'}!=0) and ($va{'opt_price'} = qq|<table border="0" cellspacing="0" cellpadding="4" width="100%">$va{'opt_price'}</table>|);
				# $in{'sprice'} = &format_price($in{'sprice'});
				# (!$in{'pricenumber'}) and ($in{'pricenumber'}=1);


				############################
				############################
				############################
				###### Multi Price
				############################
				############################
				############################

				if($in{'err'}){
					$va{'mp_message'} = &trans_txt('step2_multiprice_' . $in{'err'} );
				}

				my $x=0;my $b='';$va{'opt_price2_auth'} = '';
				#my $cadtypespay = &paytypes_for_products();
				#$cadtypespay =~ s/\|/','/;
				#my $modq = $cadtypespay ne '' ? ", IF(PayType IN ('$cadtypespay'),'enabled','disabled')AS Visibility " : ", 'enabled' AS Visibility ";
				my $cadtypespay = $cses{'paytype_order'} ? $cses{'paytype_order'} : '';
				$cadtypespay =~ s/\,/','/g;
				my $modq = $cadtypespay ne '' ? ", IF(CONCAT(PayType,'-',FP) IN('$cadtypespay'),'enabled','disabled')AS Visibility " : ", 'enabled' AS Visibility ";

				## 18092013::AD:Se agrega listado de precios por consola
				# Se utilizan los "|" para separar las diferentes consolas en el campo
				if ($in{'id_salesorigins'}){
					$origins = "|$in{'id_salesorigins'}|";
					$add_sql = "AND if(length(sl_products_prices.origins)>0,sl_products_prices.origins LIKE('%$origins%'),1)";
				}

				my ($sth) = &Do_SQL("SELECT * $modq FROM sl_products_prices WHERE ID_products = '$in{'id_products'}' AND (BelongsTo IS NULL OR BelongsTo='') $add_sql ORDER BY PayType,FP DESC,Price DESC;");
				my $recs = 0;
				while($rec = $sth->fetchrow_hashref()) {
					$recs++;

					++$x;
					my $name = lc($rec->{'PayType'});
					$name =~ s/\s//g;

					(!$rec->{'ValidKits'}) and ($rec->{'ValidKits'} = 0);
					my $mod = $rec->{'AuthCode'} eq 'Yes' ? qq|<br>AuthCode| : '';
					$va{'opt_price2'} .= qq|<li title="|.&trans_txt('step_2_price_' . $rec->{'Visibility'}).qq|" class="ui-widget-content" id="$rec->{'Visibility'}_$rec->{'ID_products_prices'}_$rec->{'ValidKits'}">$rec->{'Name'}<br>$rec->{'PayType'} ($rec->{'FP'})<br>|.&format_price($rec->{'Price'}). $mod . qq|</li>\n|;

				}
				
				$va{'opt_price2'} .= qq|<span class="stdtxterr">|.&trans_txt('product_not_available_in_console').qq|</span>| if (!$recs);			

				&select_combos_op();
				$va{'strproducts'}=$va{'id_products'};

				return &build_page("console_search_showprod.html");
			}else{
				$va{'message'} = &trans_txt('search_noitem');
				$error{'id_products'} = &trans_txt('invalid');
				return &build_page("console_search_form.html");
			}
		}else{

			$db_valid_types{'sprice'} = 'currency';
			($numhits, @hits) = &prodquery('sl_products');
			
			if($numhits>0){
				return &search_prodlist($numhits, @hits);
			}else{
				$va{'message'} = &trans_txt('search_nomatches');
				return &build_page("console_search_form.html");		
			}			
		}
		return &build_page("console_search_form.html");

	}elsif($in{'action'} eq 'decision'){

		my ($fname) = 'decision_order';
		$fname .= '_'.$in{'pname'} if $in{'pname'};

		return &build_page($fname.'.html');
	
	}else{
		return &build_page("console_search_form.html");
	}
}


#############################################################################
#############################################################################
#   Function: console_step2_ajaxinfo
#
#       Es: Muestra las tablas con informacion extra para un producto.
#       En: 
#
#    Created on: 07/31/2013  16:21:10
#
#    Author: _RB_
#
#    Modifications:
#
#   Parameters:
#
#
#  Returns:
#
#
#   See Also:
#
#
sub  console_step2_ajaxinfo{
#############################################################################
#############################################################################
	

	
	my $this_page = "console_show_prices_gross.html";



	if($in{'e'} eq '1' or $in{'e'} eq '6' or $in{'e'} eq '8'){
		$this_page = "console_show_prices_cities.html";
	}
	 
	return &build_page($this_page);
}



sub select_combos_op{
# --------------------------------------------------------
# Last Modified on: 08/05/09 10:39:27
# Last Modified by: MCC C. Gabriel Varela S: Se hace que si es un promo se borren los choicenames

	## Load Promo
	my ($sth) = &Do_SQL("SELECT VValue FROM sl_vars WHERE VName='promo$in{'id_produc'}';");
	$cfg{'promo'.$in{'id_produc'}} = $sth->fetchrow;

	if ($cfg{'promo'.$in{'id_produc'}}){
		delete($in{'choicename1'});
		delete($in{'choicename2'});
		delete($in{'choicename3'});
		delete($in{'choicename4'});
	}

		if($in{'choicename1'}){										
			my($sku) = &Do_SQL("SELECT COUNT('*') FROM sl_skus WHERE ID_products=$in{'id_produc'} and choice1 != ''");				
			if ($sku->fetchrow()>0){
				my($sku) = &Do_SQL("SELECT ID_sku_products,choice1 FROM sl_skus WHERE ID_products=$in{'id_produc'} and choice1 != ''");
				$va{'skuschoice'} = " <tr>\n<td align='right'>$in{'choicename1'}:</td>\n";
				$va{'skuschoice'}.= " <td><select id='choice1' name='choice1' onFocus='focusOn( this )' onBlur='focusOff( this )' disabled='disabled'>\n";
				$va{'skuschoice'}.= "     <option value=''>---</option>\n";
				while ($rec = $sku->fetchrow_hashref){				
					$va{'skuschoice'}.="    <option id='choice1_$rec->{'ID_sku_products'}' value='$rec->{'choice1'}'>$rec->{'choice1'}</option>\n";				
				}			
				$va{'skuschoice'} .= "</select> \n </td> \n </tr>\n";
			}		
		}

		if($in{'choicename2'}){										
			my($sku) = &Do_SQL("SELECT COUNT('*') FROM sl_skus WHERE ID_products=$in{'id_produc'} and choice2 != ''");				
			if ($sku->fetchrow()>0){
				my($sku) = &Do_SQL("SELECT ID_sku_products,choice2 FROM sl_skus WHERE ID_products=$in{'id_produc'} and choice2 != ''");				
				$va{'skuschoice'}.= "<tr> \n <td align='right'>$in{'choicename2'}:</td>\n";
				$va{'skuschoice'}.= " <td><select id='choice2' name='choice2' onFocus='focusOn( this )' onBlur='focusOff( this )'>\n";
				$va{'skuschoice'}.= "     <option value=''>---</option>\n";
				while ($rec = $sku->fetchrow_hashref){				
					$va{'skuschoice'}.="    <option id='choice2_$rec->{'ID_sku_products'}' value='$rec->{'choice2'}'>$rec->{'choice2'}</option>\n";				
				}			
				$va{'skuschoice'}.= "</select>\n </td> \n </tr>\n";
			}				
		}
		if($in{'choicename3'}){										
			my($sku) = &Do_SQL("SELECT COUNT('*') FROM sl_skus WHERE ID_products=$in{'id_produc'} and choice3 != ''");				
			if ($sku->fetchrow()>0){
				my($sku) = &Do_SQL("SELECT ID_sku_products,choice3 FROM sl_skus WHERE ID_products=$in{'id_produc'} and choice3 != ''");				
				$va{'skuschoice'}.= " <tr> \n <td align='right'>$in{'choicename3'}:</td>\n";
				$va{'skuschoice'}.= " <td><select id='choice3' name='choice3' onFocus='focusOn( this )' onBlur='focusOff( this )'>\n";
				$va{'skuschoice'}.= "     <option value=''>---</option>\n";
				while ($rec = $sku->fetchrow_hashref){				
					$va{'skuschoice'}.="    <option id='choice3_$rec->{'ID_sku_products'}' value='$rec->{'choice3'}'>$rec->{'choice3'}</option>\n";				
				}			
				$va{'skuschoice'}.= "</select>\n</td>\n</tr>\n";
			}				
		}
		if($in{'choicename4'}){										
			my($sku) = &Do_SQL("SELECT COUNT('*') FROM sl_skus WHERE ID_products=$in{'id_produc'} and choice4 != ''");				
			if ($sku->fetchrow()>0){
				my($sku) = &Do_SQL("SELECTID_sku_products,choice4 FROM sl_skus WHERE ID_products=$in{'id_produc'} and choice4 != ''");				
				$va{'skuschoice'}.= " <tr>\n<td align='right'>$in{'choicename4'}:</td>\n";
				$va{'skuschoice'}.= " <td><select id='choice4' name='choice4' onFocus='focusOn( this )' onBlur='focusOff( this )'>\n";
				$va{'skuschoice'}.= "     <option value=''>---</option>\n";
				while ($rec = $sku->fetchrow_hashref){				
					$va{'skuschoice'}.="    <option id='choice4_$rec->{'ID_sku_products'}' value='$rec->{'choice4'}'>$rec->{'choice4'}</option></td>\n";				
				}
			  $va{'skuschoice'}.= "</select>\n</td>\n</tr>\n";
			}			
		}
		
		if((!$in{'choicename1'}) and (!$in{'choicename2'}) and (!$in{'choicename3'}) and (!$in{'choicename4'})){													
			$va{'skuschoice'}.= "<tr>";
			$va{'skuschoice'}.= "<td colspan='2' align='center'>No existe opciones</td>";
			$va{'skuschoice'}.= "</tr>";
			return;
		}
		
		if(($in{'choicename1'}) or ($in{'choicename2'}) or ($in{'choicename3'}) or ($in{'choicename4'})){										
			$va{'skuschoice'}.= "<tr>";
			#class="menu_bar_red"
			$va{'skuschoice'}.= "<td colspan='2' align='center' ><span class='stdtxterr'> Debe Seleccionar Choices para Agregar al carro</span></td>";
			$va{'skuschoice'}.= "</tr>";
		}
		
	#$va{'combosjava'} = "chg_select('choice1','[in_choice1]'); chg_select('choice2','[in_choice2]'); chg_select('choice3','[in_choice3]'); chg_select('choice4','[in_choice4]');\n";
	
	return;
		
		if(($in{'choice1'}) and ($in{'choice2'}) and ($in{'choice3'}) and ($in{'choice4'}) ){										
		   $va{'combosjava'}="<script language=\"JavaScript\">\n";
		   $va{'combosjava'}.="<!--\n";
		   $va{'combosjava'}.="chg_select('choice1','[in_choice1]'); chg_select('choice2','[in_choice2]'); chg_select('choice3','[in_choice3]'); chg_select('choice4','[in_choice4]');\n";
		   $va{'combosjava'}.="	function checkchoices(formObj) {\n";
		   $va{'combosjava'}.="		if (self.document.sitform.choice1.value &&  self.document.sitform.choice2.value &&  self.document.sitform.choice3.value &&  self.document.sitform.choice4.value){\n";
		   $va{'combosjava'}.="		 return true;}";
		   $va{'combosjava'}.="		return false;";
		   $va{'combosjava'}.=" }";
		   $va{'combosjava'}.="//-->";
		   $va{'combosjava'}.="</script>";
		}elsif(($in{'choice1'}) and ($in{'choice2'}) and ($in{'choice3'}) and (!$in{'choice4'})){										
		   $va{'combosjava'}="<script language=\"JavaScript\">\n";
		   $va{'combosjava'}.="<!--\n";
		   $va{'combosjava'}.="chg_select('choice1','[in_choice1]'); chg_select('choice2','[in_choice2]'); chg_select('choice3','[in_choice3]');\n ";
		   $va{'combosjava'}.="	function checkchoices(formObj) {\n";
		   $va{'combosjava'}.="		if (self.document.sitform.choice1.value &&  self.document.sitform.choice2.value &&  self.document.sitform.choice3.value ){\n";
		   $va{'combosjava'}.="			return true;}\n";
		   $va{'combosjava'}.="		return false;\n";
		   $va{'combosjava'}.=" }\n";
		   $va{'combosjava'}.="//-->\n";
		   $va{'combosjava'}.="</script>\n";
		}elsif(($in{'choice1'}) and ($in{'choice2'}) and (!$in{'choice3'}) and (!$in{'choice4'})){													
		   $va{'combosjava'}="<script language=\"JavaScript\">\n";
		   $va{'combosjava'}.="<!--\n";
		   $va{'combosjava'}.="chg_select('choice1','[in_choice1]'); chg_select('choice2','[in_choice2]');\n ";
		   $va{'combosjava'}.="	function checkchoices(formObj) {\n";
		   $va{'combosjava'}.="		if (self.document.sitform.choice1.value &&  self.document.sitform.choice2.value ){\n";
		   $va{'combosjava'}.="			return true;}\n";
		   $va{'combosjava'}.="	  return false;\n";
		   $va{'combosjava'}.=" }\n";
		   $va{'combosjava'}.="//-->\n";
		   $va{'combosjava'}.="</script>\n";
		}elsif(($in{'choice1'}) and (!$in{'choice2'}) and (!$in{'choice3'}) and (!$in{'choice4'})){										
		   $va{'combosjava'}="<script language=\"JavaScript\">\n";
		   $va{'combosjava'}.="<!--\n";
		   $va{'combosjava'}.="chg_select('choice1','[in_choice1]');\n ";
		   $va{'combosjava'}.="	function checkchoices(formObj) {\n";
		   $va{'combosjava'}.="		if (self.document.sitform.choice1.value ){\n";
		   $va{'combosjava'}.="			return true;}\n";
		   $va{'combosjava'}.="		return false;\n";
		   $va{'combosjava'}.=" }\n";
		   $va{'combosjava'}.="//-->\n";
		   $va{'combosjava'}.="</script>\n";
	    }elsif((!$in{'choice1'}) and (!$in{'choice2'}) and (!$in{'choice3'}) and (!$in{'choice4'})){										
		   $va{'combosjava'}="<script language=\"JavaScript\">\n";
		   $va{'combosjava'}.="<!--\n";
		   $va{'combosjava'}.="	function checkchoices(formObj) {\n";
		   $va{'combosjava'}.="		return false;\n";
		   $va{'combosjava'}.=" }\n";
		   $va{'combosjava'}.="//-->\n";
		   $va{'combosjava'}.="</script>\n";
	    }
}


sub search_prodlist {
# --------------------------------------------------------
	my ($numhits,@hits) = @_;
	$va{'matches'} = $numhits;

	my (%tmp, $qs, $add_title);
	my (@c) = split(/,/,$cfg{'srcolors'});
	my ($rows) = ($#hits+1)/($#db_cols+1);

	for (0 .. $rows-1) {

		$d = 1 - $d;
		%tmp = &array_to_hash($_, @hits);

		my ($sth) = &Do_SQL("SELECT MIN(Price) FROM sl_products_prices WHERE ID_products = '$tmp{'ID_products'}';");
		$tmp{'SPrice'} = $sth->fetchrow();

		$page .= qq|		    <tr onmouseover='m_over(this)' onmouseout='m_out(this)' bgcolor='$c[$d]' onClick="trjump('/cgi-bin/mod/sales/admin?cmd=console_order&id_products=$tmp{$db_cols[0]}&action=search&step=2')">\n|;
		for (0..$#headerfields){
			if ($headerfields[$_] =~ /([^:]+):([^\.]+)\.([^\.]+)/){
				## 1)DB  2)ID  3)Name
				$page .= "	<td valign='top'><a href='".&build_link($1,$2,$tmp{$2})."' class='error'>". &load_name($1,$2,$tmp{$2},$3) ."</a></td>\n";
			}elsif($headerfields[$_] eq 'ID_products'){
				$page .= qq|	<td valign='top' nowrap>|. &format_sltvid($tmp{$headerfields[$_]}) .qq|&nbsp;</td>\n|;
			}elsif($db_valid_types{lc($headerfields[$_])} eq "date"){
				$page .= qq|	<td align="center" nowrap valign='top'>| . &sql_to_date($tmp{$headerfields[$_]}) . qq|&nbsp;</td>\n|;
			}elsif($db_valid_types{lc($headerfields[$_])} eq "currency"){
				$page .= qq|	<td align="right" nowrap valign='top'>| . &format_price($tmp{$headerfields[$_]}) . qq|&nbsp;</td>\n|;
			}elsif ($db_valid_types{lc($headerfields[$_])} eq "numeric"){
				$page .= qq|	<td align="right" nowrap valign='top'>| . &format_number($tmp{$headerfields[$_]}) . qq|&nbsp;</td>\n|;
			}else{
				$tmp{$headerfields[$_]} =~ s/\n/<br>/g;
				$page .= qq|	<td valign='top'>$tmp{$headerfields[$_]}&nbsp;</td>\n|;
			}
		}
		$page .= "		</tr>";
	}
#@ivanmiranda
	$va{'search'} = ("from_sprice=$in{'from_sprice'}&amp;to_sprice=$in{'to_sprice'}&amp;keyword=$in{'keyword'}&amp;model=$in{'model'}&amp;nombre=$in{'nombre'}&amp;");
	$va{'searchresults'} = $page;
	($va{'pageslist'},$va{'qs'})  = &pages_list($in{'nh'},"$script_url",$numhits,$usr{'pref_maxh'});
	return &build_page("console_search_showlist.html");
}

sub search_cust_options {
# --------------------------------------------------------
	if ($in{'action'}){
		$va{'message'} = &trans_txt('searchempty');
	}
	return &build_page("console_search_custform.html");
}

sub itemsinbasket {
# --------------------------------------------------------
# Last Modified on: 10/30/08 12:07:54
# Last Modified by: MCC C. Gabriel Varela S: Se modifica para incluir memberprice
# Last Modified on: 02/02/09 16:32:18
# Last Modified by: MCC C. Gabriel Varela S: Se modifica para no calcular doble descuento al tener membres�a y 
# Last Modified on: 07/07/09 15:54:51
# Last Modified by: MCC C. Gabriel Varela S: Se hace que si hay pnum, se deshabilite flexipago.
# Last Modified on: 07/08/09 10:50:55
# Last Modified by: MCC C. Gabriel Varela S: Se hace que el precio de membres�a se asigne tambi�n tomando en cuenta multiprice
# Last Modified RB: 07/10/09  10:01:13 -- Si es promo los datos de precio se toman del articulo virtual
#Last modified on 3/31/11 11:44 AM
#Last modified by: MCC C. Gabriel Varela S. :Se hace que no se establezcan los valores para: _downpayment, fpprice, fpago, msprice, payments, pnum, price, shp1, shp2, shp3 para cuando el producto se agreg� por secret cupon
# Last Modified by RB on 07/18/2011 12:33:03 PM : Se agrega numero de flexipagos cuando es promo 2x1
# Last Time Modified by RB on 07/25/2013 : Se agrego calculo de multiprice basado en sl_products_prices


	my ($key,$cant,@desc,$output,$total,$rec,$prod);
	if ($cses{'items_in_basket'} > 0){

		for my $i(1..$cses{'items_in_basket'}){

			if ($cses{'items_'.$i.'_qty'}>0 and $cses{'items_'.$i.'_id'}>0){

				$cant += $cses{'items_'.$i.'_qty'};
				my ($sth) = &Do_SQL("SELECT * FROM sl_products WHERE ID_products='".substr($cses{'items_'.$i.'_id'},-6)."'");
				$prod = $sth->fetchrow_hashref;
				
				###### Si es promo, los valores son los del relid/#productos
				if ($cfg{'promo'.$cses{'items_'.$i.'_relid'}}){
					($prod->{'SPrice'},$prod->{'SPrice1'},$prod->{'SPrice2'},$prod->{'SPrice3'},$prod->{'SPrice4'},$prod->{'FPPrice'},$prod->{'MemberPrice'},$prod->{'PayType'},$prod->{'Downpayment'},$prod->{'Flexipago'}) = &get_promo_prices($cses{'items_'.$i.'_relid'}, $cses{'items_'.$i.'_pnum'}, $cses{'items_'.$i.'_promopct'}, $cses{'items_'.$i.'_promocal'});
				}
				
				if ($cfg{'multiprice'} and !$cfg{'promo'.$cses{'items_'.$i.'_relid'}} and $cses{'items_'.$i.'_pnum'} > 1){

					###############
					###############
					##### Cargado de Datos de tabla sl_products_prices
					###############
					################
					my ($sth) = &Do_SQL("SELECT Name, Price,FP, PayType FROM sl_products_prices WHERE ID_products_prices = '$cses{'items_'.$i.'_pnum'}' AND ID_products = '".substr($cses{'items_'.$i.'_id'},-6)."';");
					my ($m_name,$m_price,$m_fp,$m_pt) = $sth->fetchrow();

					if($m_fp) {

	
						$price = ($cses{'items_'.$i.'_secret_cupon'} and $cses{'items_'.$i.'_price'} != 0) ?
								$cses{'items_'.$i.'_price'} :
								$m_price;

						$cses{'items_'.$i.'_price'} = $price if(!$cses{'items_'.$i.'_secret_cupon'});
						$cses{'items_'.$i.'_fpago'} = $m_fp if(!$cses{'items_'.$i.'_secret_cupon'});
						$prod->{'FPPrice'} = $m_price; 


					}else{

						#$price = $prod->{'SPrice'.($cses{'items_'.$i.'_pnum'}-1)};
						$price = $m_price;
						$price=$cses{'items_'.$i.'_price'} if($cses{'items_'.$i.'_secret_cupon'} and $cses{'items_'.$i.'_price'}!=0);
						$cses{'items_'.$i.'_price'} = $price if(!$cses{'items_'.$i.'_secret_cupon'});
						$cses{'items_'.$i.'_fpago'} = $prod->{'Flexipago'}if(!$cses{'items_'.$i.'_secret_cupon'});
						#$cses{'items_'.$i.'_fpago'} = 1;

					}

				}else{
					$price    = $prod->{'SPrice'};
					$price=$cses{'items_'.$i.'_price'} if($cses{'items_'.$i.'_secret_cupon'} and $cses{'items_'.$i.'_price'}!=0);
					$cses{'items_'.$i.'_price'} = $prod->{'SPrice'} if(!$cses{'items_'.$i.'_secret_cupon'});
					$cses{'items_'.$i.'_fpago'} = $prod->{'Flexipago'}if(!$cses{'items_'.$i.'_secret_cupon'});
				}
				$desc[$i] = $prod->{'Name'};
				
				
				#Se comenta siguiente l�nea, est� mal porque as� se aplica doble descuento.
				#$cses{'items_'.$i.'_price'} = $rec->{'MemberPrice'} if ($cfg{'membership'} and $cses{'type'}eq'Membership' and $rec->{'MemberPrice'} > 0 and ($cses{'pay_type'} eq 'lay' or $cses{'pay_type'} eq 'cod'));
				$cses{'items_'.$i.'_fpprice'} = $prod->{'FPPrice'}if(!$cses{'items_'.$i.'_secret_cupon'});
				$cses{'items_'.$i.'_msprice'} = $prod->{'MemberPrice'}if(!$cses{'items_'.$i.'_secret_cupon'});
				$cses{'items_'.$i.'_downpayment'} = $prod->{'Downpayment'}if(!$cses{'items_'.$i.'_secret_cupon'});
				
				if(!$prod->{'MemberPrice'} or $prod->{'MemberPrice'}==0){
					if ($cfg{'multiprice'} and $cses{'items_'.$i.'_pnum'}>1)	{
						$cses{'items_'.$i.'_msprice'}=$prod->{'SPrice'.($cses{'items_'.$i.'_pnum'}-1)}if(!$cses{'items_'.$i.'_secret_cupon'});
					}else{
						$cses{'items_'.$i.'_msprice'} = $prod->{'SPrice'}if(!$cses{'items_'.$i.'_secret_cupon'});
					}
				}

				$cses{'items_'.$i.'_duties'} = $prod->{'Duties'};
				$cses{'items_'.$i.'_insurance'} = $prod->{'Insurance'};
				$total  += $price * $cses{'items_'.$i.'_qty'};
				$price	 = &format_price($price);
				#&cgierr($price)	;

				my ($sthk) = &Do_SQL("SELECT * FROM sl_skus WHERE ID_sku_products='$cses{'items_'.$i.'_id'}' and Status='Active'");
				$rec = $sthk->fetchrow_hashref;
				$output .= qq|
					<tr>
					   <td  nowrap>
					   <a href='/cgi-bin/mod/sales/admin?cmd=console_order&step=2&drop=$i'><img src='$va{'imgurl'}/$usr{'pref_style'}/b_drop.png' title='Drop' alt='' border='0'></a>
					   		</td>
					   <td >$cses{'items_'.$i.'_qty'} x</td>
					   <td  onClick="trjump('/cgi-bin/mod/sales/admin?cmd=console_order&step=2&action=search&id_products=|.substr($cses{'items_'.$i.'_id'},3,6).qq|&choice1=$rec->{'choice1'}&choice2=$rec->{'choice2'}&choice3=$rec->{'choice3'}&choice4=$rec->{'choice4'}')">|.substr($desc[$i],0,10).qq|</td>
					   <td  align="right" nowrap>$price</td>
					</tr>\n|;
			}
		}
		
		if ($cant){
			$output .= qq|
				<tr>
				   <td colspan="3"  align=right nowrap>|.&trans_txt('total').qq|</td>
				   <td align="right"  nowrap>|.&format_price($total).qq|</td>
				</tr>		
				<tr>
				   <td colspan="4" align="center"><br><br>
				    <a href="/cgi-bin/mod/sales/admin?cmd=console_order&step=3"	class=button>CREAR ORDEN</a>
				    <br><br>
				    </td>
				</tr>\n|;
			return $output;
		}else{
			return "<tr><td class='menu_bar' colspan='4'>".&trans_txt('empty_cart')."</td></tr>";
		}
	}else{
		return "<tr><td class='menu_bar' colspan='4'>".&trans_txt('empty_cart')."</td></tr>";
	}
}

sub products_inorder {
# --------------------------------------------------------
# Created on: 07/10/08 @ 16:11:02
# Author: Carlos Haas
# Last Modified on: 07/10/08 @ 16:11:02
# Last Modified by: Carlos Haas
# Description : 
# Parameters : 
#			   	
# Last Modified on: 08/04/08 10:11:44
# Last Modified by: MCC C. Gabriel Varela S
# Last Modified on: 10/20/08 12:27:57
# Last Modified by: MCC C. Gabriel Varela S: Se corrige nuevamente que no se tomen en cuenta los taxes para los servicios	   		   
# Last Modified on: 10/21/08 16:10:07
# Last Modified by: MCC C. Gabriel Varela S: Se hace que el n�mero de pagos sea diferente de 1 para tomarse como mensual y se agregan pagos semanales
# Last Modified on: 10/29/08 11:41:58
# Last Modified by: MCC C. Gabriel Varela S: Se corrige error de c�lculo en cuotas, se hace que se verifique que est� habilitado pagos quincenales en el sistema y que el pago sea diferente de 1.Adem�s se hace que no se elija pagos cada 20 d�as al menos que se haga por medio del m�todo normal. Tambi�n se hace que se valide la coexistencia de pagos con las combinaciones: de M a Q, M a C, M a S, Q a M, Q a C, Q a S, S a M, S a C y S a Q
# Last Modified on: 10/30/08 10:30:37
# Last Modified by: MCC C. Gabriel Varela S: Se hace que ya no exista downpayment del 7% para pagos quincenales y semanales. Tambi�n se habilita pago semanal 2(basado en 52 semanas). Se comienza a ver lo de precios con membres�a
# Last Modified on: 11/03/08 11:44:13
# Last Modified by: MCC C. Gabriel Varela S: Se hace que los pagos de los servicios siempre sean 1
# Last Modified RB: 12/02/08  18:56:59 Se cambio el fprice = msprice cuando se tenga membresia y sea layaway|cod
# Last Modified on: 12/18/08 11:51:14
# Last Modified by: MCC C. Gabriel Varela S: Se ponen descuentos de membres�as en pagos
# Last Modified on: 02/02/09 16:29:59
# Last Modified by: MCC C. Gabriel Varela S: Se hace que no se aplique doble descuento al tener membres�a con .
# Last Modified RB: 03/12/09  11:32:31 -- Agregue &save_callsession(); al final de la funcion
# Last Modified on: 03/17/09 16:38:06
# Last Modified by: MCC C. Gabriel Varela S: Par�metros para sltv_itemshipping. Se toma en cuenta Shipping COD
# Last Modified on: 07/06/09 18:37:47
# Last Modified by: MCC C. Gabriel Varela S: Se corrige precio para asignar cuando no tiene m�s de un precio.
# Last Modified on: 07/07/09 15:54:51
# Last Modified by: MCC C. Gabriel Varela S: Se hace que si hay pnum, se deshabilite flexipago.
# Last Modified on: 07/08/09 10:14:13
# Last Modified by: MCC C. Gabriel Varela S: Se corrige c�lculo del tax, cuando es un s�lo pago se debe de tomar price, no fpprice y tambi�n viceversa, se comentaron l�neas err�neas y se sustituyeron por las correctas. Tambi�n se corrige la asignaci�n de precio de membres�a cuando hay multiprice.
# Last Modified on: 07/10/09 12:46:53
# Last Modified by: MCC C. Gabriel Varela S: Se corrige el c�lculo del tax para el caso de productos que NO tienen precio de flexipago definido en BD
# Last Modified on: 07/10/09 18:20:51
# Last Modified by: MCC C. Gabriel Varela S: Se habilita free shipping tambi�n para COD
# Last Modified RB: 09/03/09  18:34:36 -- Se agrego descuento en shipping basado en configuracion(para TC)
# Last Modified RB: 10/09/09  16:17:11 -- Se corrige shipping para promos para tomar el shipping del producto virtual
# Last Modified RB: 10/09/09  16:51:30 -- Se toma un solo shipping para productos Promo y no shipping por producto
# Last Modified RB: 11/30/09  17:51:30 -- Se agrega label [Backorder] cuando el producto esta en ese Status
# Last Modified RB: 12/06/2010  18:35:30 -- Pendiente completar nueva tabla de shipping
# Last modified on 3/31/11 11:41 AM
# Last modified by: MCC C. Gabriel Varela S. :Se hace que no se establezcan los valores para: _downpayment, fpprice, fpago, msprice, payments, pnum, price, shp1, shp2, shp3 para cuando el producto se agreg� por secret cupon
# Last Time Modified by RB on 08/30/2011 : Se aregaron modificaciones para permitir downpaymwent + 1 pago
# Last Time Modified by RB on 11/08/2011 : Se agrego overwrite the datos(SPrice,FPPrice,Flexipago,Downpayment)
# Last Time Modified by RB on 11/09/2011 : Se agrego pricetype(gross) para calculo de precio con envio e impuestos incluidos
# Last Time Modified by AD on 28/01/2013 : Se agrego calculo de impuesto por producto que aplica solo para MX
# Last Time Modified by RB on 07/25/2013 : Se agrego calculo de multiprice basado en sl_products_prices

	my ($cant,@desc,$price,$output,$edt,$aux,$weight,$totalqty,$cupon,$choices,$flexipago,$fpdisc,$total,$total_tax,$onepay,$str_disc,$total_shptax,$total_servtax);
	$cses{'categories'}='';
	$va{'items_discounts'} = 0;

	my %config_values_prices = (
		'cod',	{1,'shipment_cod_standard',2,'shipment_cod_express',3,'shipment_cod_cod'}, 
		'cc',	{1,'shipment_cc_standard',2,'shipment_cc_express',3,'shipment_cc_cod' },
		'rd',	{1,'shipment_rd_standard',2,'shipment_rd_express',3,'shipment_rd_cod' }
	);
	
	if(length($in{'customers.zip'}) == 5) {
		$cses{'tax_total'} = &calculate_taxes($in{'customers.zip'}, 0, 0, 0);
	}elsif(length($in{'shp_zip'}) == 5) {
		$cses{'tax_total'} = &calculate_taxes($in{'shp_zip'}, 0, 0, 0);
	}
	

	if ($cses{'items_in_basket'} > 0 || $cses{'servis_in_basket'} > 0){

		$cses{'dayspay'}=1;
		#$cses{'dayspay'}=$in{'dayspay'} if ($in{'dayspay'});
		my ($banddays)=0;

		## Esta parte de codigo fue movida para obtener el costo del shipping al inicio y poder calcular el tax correspondiente
		&calculate_shipping;

		if(!$cses{'shp_type'}){

			$in{'shp_type'} = 1 if !($in{'shp_type'} and $cses{'pay_type'}ne'cod');
			$in{'shp_type'} = $cfg{'codshptype'} if($cses{'pay_type'} eq 'cod');
			$cses{'shp_type'} = $in{'shp_type'};

		}

		## FC ->
		my %config_values_prices = (
			'cod',	{1,'shipment_cod_standard',2,'shipment_cod_express',3,'shipment_cod_cod'}, 
			'cc',	{1,'shipment_cc_standard',2,'shipment_cc_express',3,'shipment_cc_cod' },
			'rd',	{1,'shipment_rd_standard',2,'shipment_rd_express',3,'shipment_rd_cod' }
		);

		if($cfg{'use_default_shipment'} and $cfg{'use_default_shipment'}==1){
			$cses{'shipping_total'} = $cfg{$config_values_prices{$cses{'pay_type'}}{$cses{'shp_type'}}};
		}else{
			$cses{'shipping_total'} = $va{'shptotal'.$in{'shp_type'}};
		}
		## <- FC

		##########################################
		#########  PRODUCTS    ###################
		##########################################
		my $flag=0;
		for my $i(1..$cses{'items_in_basket'}){

			my $str_disc	=	'';
			my $backorder='';

			if ($in{"fpago$i".$cses{'items_'.$i.'_id'}}){
				$cses{'items_'.$i.'_payments'} = $in{"fpago$i".$cses{'items_'.$i.'_id'}}if(!$cses{'items_'.$i.'_secret_cupon'});
			}

			if ($cses{'items_'.$i.'_qty'} > 0 and $cses{'items_'.$i.'_id'}>0){

				if((!$cses{'items_'.$i.'_promo'} or $flag != $cses{'items_'.$i.'_promo'})and(!$cses{'items_'.$i.'_secret_cupon'})){

					my $tprod='id';
					($cses{'items_'.$i.'_promo'}) and ($tprod = 'promo') and ($flag=$cses{'items_'.$i.'_promo'});

					my $shpcal;
					
					if($cses{'items_'.$i.'_shp_ow'}){

						## Overwrite Shipping	
						$cses{'items_'.$i.'_shp1'} = $cses{'items_'.$i.'_shp_ow'};
						$cses{'items_'.$i.'_shp2'} = $cses{'items_'.$i.'_shp_ow'};
						$cses{'items_'.$i.'_shp3'} = $cses{'items_'.$i.'_shp_ow'};
						$shpcal = $cses{'items_'.$i.'_shp_cal_ow'};

					}else{

						## Fixed/Variable/Table Shipping ? 
						$shpcal  = &load_name('sl_products','ID_products',substr($cses{'items_'.$i.'_'.$tprod},3,6),'shipping_table');
						my $shpmdis = &load_name('sl_products','ID_products',substr($cses{'items_'.$i.'_'.$tprod},3,6),'shipping_discount');
					
						my $idpacking = &load_name('sl_products','ID_products',substr($cses{'items_'.$i.'_'.$tprod},3,6),'ID_packingopts');
						($shptotal1,$shptotal2,$shptotal3,$shptotal1pr,$shptotal2pr,$shptotal3pr,$va{'shp_text1'},$va{'shp_text2'},$va{'shp_text3'},$va{'shp_textpr1'},$va{'shp_textpr2'},$va{'shp_textpr3'})= &sltv_itemshipping($cses{'edt'},$cses{'items_'.$i.'_size'},1,1,$cses{'items_'.$i.'_weight'},$idpacking,$shpcal,$shpmdis,substr($cses{'items_'.$i.'_'.$tprod},3,6));
						$cses{'items_'.$i.'_shp1'} = $shptotal1 if(!$cses{'items_'.$i.'_shpf'});
						$cses{'items_'.$i.'_shp2'} = $shptotal2  if(!$cses{'items_'.$i.'_shpf'});
						$cses{'items_'.$i.'_shp3'} = $shptotal3 if(!$cses{'items_'.$i.'_shpf'});

					}

					if($shpcal eq 'Fixed' and $cfg{'shpdis_cc'} and $cses{'pay_type'} eq 'cc'){

						##### Shipping discount in TDC Orders
						$cses{'items_'.$i.'_shp1'} = round($cses{'items_'.$i.'_shp1'} * $cfg{'shpdis_cc'},3);
						$cses{'items_'.$i.'_shp2'} = round($cses{'items_'.$i.'_shp2'} * $cfg{'shpdis_cc'},3);
						$cses{'items_'.$i.'_shp3'} = round($cses{'items_'.$i.'_shp3'} * $cfg{'shpdis_cc'},3);

					}
					
				}else{
					$cses{'items_'.$i.'_shp1'} = 0;
					$cses{'items_'.$i.'_shp2'} = 0;
					$cses{'items_'.$i.'_shp3'} = 0;
				}
				## FC ->
				if($cfg{'use_default_shipment'} and $cfg{'use_default_shipment'} == 1){
					$price_line1 = $cfg{$config_values_prices{$cses{'pay_type'}}{1}} / $cses{'items_in_basket'};
					$price_line2 = $cfg{$config_values_prices{$cses{'pay_type'}}{2}} / $cses{'items_in_basket'};
					$price_line3 = $cfg{$config_values_prices{$cses{'pay_type'}}{3}} / $cses{'items_in_basket'};
					$cses{'items_'.$i.'_shp1'} = $price_line1;
					$cses{'items_'.$i.'_shp2'} = $price_line2;
					$cses{'items_'.$i.'_shp3'} = $price_line3;
				}
				## <- FC

				$cant += $cses{'items_'.$i.'_qty'};
				$totalqty  += $cses{'items_'.$i.'_qty'};
				
				my ($sth) = &Do_SQL("SELECT * FROM sl_products WHERE ID_products='".substr($cses{'items_'.$i.'_id'},3,9)."'");
				$rec = $sth->fetchrow_hashref;
				
				###### Si es promo, los valores son los del relid/#productos
				## Load Promo
				my ($sth) = &Do_SQL("SELECT VValue FROM sl_vars WHERE VName='promo".$cses{'items_'.$i.'_relid'}."';");
				$cfg{'promo'.$cses{'items_'.$i.'_relid'}} = $sth->fetchrow;
				if ($cfg{'promo'.$cses{'items_'.$i.'_relid'}}){

					($rec->{'SPrice'},$rec->{'SPrice1'},$rec->{'SPrice2'},$rec->{'SPrice3'},$rec->{'SPrice4'},$rec->{'FPPrice'},$rec->{'MemberPrice'},$rec->{'PayType'},$rec->{'Downpayment'},$rec->{'Flexipago'}) = &get_promo_prices($cses{'items_'.$i.'_relid'}, $cses{'items_'.$i.'_pnum'}, $cses{'items_'.$i.'_promopct'}, $cses{'items_'.$i.'_promocal'});
				
				}elsif ($cfg{'multiprice'} and $cses{'items_'.$i.'_pnum'}){

					###############
					###############
					##### Cargado de Datos de tabla sl_products_prices
					###############
					################
					my ($sth) = &Do_SQL("SELECT Name, Price,Downpayment,FP, PayType FROM sl_products_prices WHERE ID_products_prices = '$cses{'items_'.$i.'_pnum'}' AND ID_products = '".substr($cses{'items_'.$i.'_id'},-6)."';");
					my ($m_name,$m_price,$m_dp,$m_fp,$m_pt) = $sth->fetchrow();
					
					if ($in{'dropshp'}) {
						#$m_price = $m_price - ($m_price * 0.15);
						#$m_price -= $in{'items_1_shp3'};
					}
					
					if($m_fp) {

						$rec->{'SPrice'} = $m_price;
						$rec->{'Downpayment'} = $m_dp;
						$rec->{'Flexipago'} = $m_fp;
						$rec->{'PayType'} = $m_pt;
						$rec->{'FPPrice'} = $m_fp > 1 ? $m_price : 0;
						$cses{'items_'.$i.'_oname'} = $m_name;
						
						
					}else{

						$rec->{'SPrice'} = $rec->{'SPrice'.($cses{'items_'.$i.'_pnum'}-1)};
						$rec->{'FPPrice'} = $price;
						
					}
					

				}


				###############
				###############
				##### Gross Price ?
				###############
				################
				my ($taxes,$taxesfp);

				if($cses{'pricetype'} eq 'Gross') {
					if($cfg{'shptax'} and (lc($cfg{'shptaxtype'}) eq 'net' or lc($cfg{'shptaxtype'}) eq 'gross')) {
						
						if(!$cses{'items_'.$i.'_price_ow'} and $cses{'items_1_shp1'}){

							if($cses{'tax_total'} and $cses{'tax_total'} > 0) {

								$taxes = $rec->{'SPrice'} - ($rec->{'SPrice'}/(1+$cses{'tax_total'}));
								$taxesfp = $rec->{'FPPrice'} - ($rec->{'FPPrice'}/(1+$cses{'tax_total'})) if $rec->{'FPPrice'} > 0;
								
								## Redondeo las cantidades al numero de decimales configurado default=2
								$sys{'fmt_curr_decimal_digits'} = ($sys{'fmt_curr_decimal_digits'})? int($sys{'fmt_curr_decimal_digits'}):2;
								# $taxes = sprintf("%.".$sys{'fmt_curr_decimal_digits'}."f",$taxes);
								$taxes = &round($taxes, $sys{'fmt_curr_decimal_digits'});
								$taxesfp = &round($taxesfp, $sys{'fmt_curr_decimal_digits'});
								# $rec->{'SPrice'} = sprintf("%.".$sys{'fmt_curr_decimal_digits'}."f",$rec->{'SPrice'});
								$rec->{'SPrice'} = &round($rec->{'SPrice'}, $sys{'fmt_curr_decimal_digits'});
								$rec->{'SPrice'} -= $taxes;
								#$rec->{'SPrice1'} -= $taxes if $rec->{'SPrice1'} > 0;
								#$rec->{'SPrice2'} -= $taxes if $rec->{'SPrice2'} > 0;
								#$rec->{'SPrice3'} -= $taxes if $rec->{'SPrice3'} > 0;
								#$rec->{'SPrice4'} -= $taxes if $rec->{'SPrice4'} > 0;
								$rec->{'FPPrice'} -= $taxes if $rec->{'FPPrice'} > 0;

								### Recalculo de taxes
								$taxes = $rec->{'SPrice'} * $cses{'tax_total'};
								$taxes = &round($taxes, $sys{'fmt_curr_decimal_digits'});

								$taxesfp = &round($taxesfp, $sys{'fmt_curr_decimal_digits'});
								$taxesfp = $rec->{'FPPrice'} * $cses{'tax_total'};
								
							}
						
						} elsif($cses{'items_1_shp1'} == 0){

							if($cses{'tax_total'} and $cses{'tax_total'} > 0) {

								$taxes = $rec->{'SPrice'} - ($rec->{'SPrice'}/(1+$cses{'tax_total'}));
								$taxesfp = $rec->{'FPPrice'} - ($rec->{'FPPrice'}/(1+$cses{'tax_total'})) if $rec->{'FPPrice'} > 0;

								## Redondeo las cantidades al numero de decimales configurado default=2
								$sys{'fmt_curr_decimal_digits'} = ($sys{'fmt_curr_decimal_digits'})? int($sys{'fmt_curr_decimal_digits'}):2;
								# $taxes = sprintf("%.".$sys{'fmt_curr_decimal_digits'}."f",$taxes);
								$taxes = &round($taxes, $sys{'fmt_curr_decimal_digits'});
								$taxesfp = &round($taxesfp, $sys{'fmt_curr_decimal_digits'});

								# $rec->{'SPrice'} = sprintf("%.".$sys{'fmt_curr_decimal_digits'}."f",$rec->{'SPrice'});
								$rec->{'SPrice'} = &round($rec->{'SPrice'}, $sys{'fmt_curr_decimal_digits'});
								$rec->{'SPrice'} -= $taxes;
								#$rec->{'SPrice1'} -= $taxes if $rec->{'SPrice1'} > 0;
								#$rec->{'SPrice2'} -= $taxes if $rec->{'SPrice2'} > 0;
								#$rec->{'SPrice3'} -= $taxes if $rec->{'SPrice3'} > 0;
								#$rec->{'SPrice4'} -= $taxes if $rec->{'SPrice4'} > 0;
								$rec->{'FPPrice'} -= $taxes if $rec->{'FPPrice'} > 0;

								### Recalculo de taxes
								$taxes = $rec->{'SPrice'} * $cses{'tax_total'};
								$taxes = &round($taxes, $sys{'fmt_curr_decimal_digits'});

								$taxesfp = &round($taxesfp, $sys{'fmt_curr_decimal_digits'});
								$taxesfp = $rec->{'FPPrice'} * $cses{'tax_total'};
							}
						}

					}else{
						#&cgierr(4);
						## Gross Price
						if(!$cses{'items_'.$i.'_price_ow'} and $cses{'items_1_shp'.$cses{'shp_type'}}){
							#&cgierr(5);
							$rec->{'SPrice'} -= $cses{'items_'.$i.'_shp'.$cses{'shp_type'}};
							#$rec->{'SPrice1'} -= $cses{'items_'.$i.'_shp'.$cses{'shp_type'}} if $rec->{'SPrice1'} > 0;
							#$rec->{'SPrice2'} -= $cses{'items_'.$i.'_shp'.$cses{'shp_type'}} if $rec->{'SPrice2'} > 0;
							#$rec->{'SPrice3'} -= $cses{'items_'.$i.'_shp'.$cses{'shp_type'}} if $rec->{'SPrice3'} > 0;
							#$rec->{'SPrice4'} -= $cses{'items_'.$i.'_shp'.$cses{'shp_type'}} if $rec->{'SPrice4'} > 0;
							$rec->{'FPPrice'} -= $cses{'items_'.$i.'_shp'.$cses{'shp_type'}} if $rec->{'FPPrice'} > 0;
							
							if($cses{'tax_total'} and $cses{'tax_total'} > 0){
								#&cgierr(6);
								my $taxes = $rec->{'SPrice'} - ($rec->{'SPrice'}/(1+$cses{'tax_total'}));
								$taxesfp = $rec->{'FPPrice'} - ($rec->{'FPPrice'}/(1+$cses{'tax_total'})) if $rec->{'FPPrice'} > 0;
								
								## Redondeo las cantidades al numero de decimales configurado default=2
								$sys{'fmt_curr_decimal_digits'} = ($sys{'fmt_curr_decimal_digits'})? int($sys{'fmt_curr_decimal_digits'}):2;
								# $taxes = sprintf("%.".$sys{'fmt_curr_decimal_digits'}."f",$taxes);
								$taxes = &round($taxes, $sys{'fmt_curr_decimal_digits'});
								$taxesfp = &round($taxesfp, $sys{'fmt_curr_decimal_digits'});

								$rec->{'SPrice'} -= $taxes;
								#$rec->{'SPrice1'} -= $taxes if $rec->{'SPrice1'} > 0;
								#$rec->{'SPrice2'} -= $taxes if $rec->{'SPrice2'} > 0;
								#$rec->{'SPrice3'} -= $taxes if $rec->{'SPrice3'} > 0;
								#$rec->{'SPrice4'} -= $taxes if $rec->{'SPrice4'} > 0;
								$rec->{'FPPrice'} -= $taxes if $rec->{'FPPrice'} > 0;

								### Recalculo de taxes
								$taxes = $rec->{'SPrice'} * $cses{'tax_total'};
								$taxes = &round($taxes, $sys{'fmt_curr_decimal_digits'});

								$taxesfp = &round($taxesfp, $sys{'fmt_curr_decimal_digits'});
								$taxesfp = $rec->{'FPPrice'} * $cses{'tax_total'};
								
							}

						}

					}

				} ## Gross Prices

				$price = $rec->{'SPrice'};
				$price=$cses{'items_'.$i.'_price'} if($cses{'items_'.$i.'_secret_cupon'} and $cses{'items_'.$i.'_price'}!=0);				
				# 21082014::AD Se corrige problema de centavos en OrderDisc redondeando decimales
				# $fpprice = $rec->{'FPPrice'};				
				$fpprice = &round($rec->{'FPPrice'}, $sys{'fmt_curr_decimal_digits'});
				
				$fpprice=$cses{'items_'.$i.'_fpprice'} if($cses{'items_'.$i.'_secret_cupon'} and $cses{'items_'.$i.'_fpprice'}!=0);
				
				$fpprice = $price if($fpprice eq'0.00' or $fpprice eq'' or $fpprice==0);
				
				
				###########
				########### Prices
				###########

				$cses{'items_'.$i.'_price'} = $price if(!$cses{'items_'.$i.'_secret_cupon'});
				$cses{'items_'.$i.'_fpprice'} = $fpprice if(!$cses{'items_'.$i.'_secret_cupon'});
				$cses{'items_'.$i.'_fpago'} = $rec->{'Flexipago'}if(!$cses{'items_'.$i.'_secret_cupon'});
			

				## Precio del producto
				$gross_price = $rec->{'SPrice'};
				
				## Overwrite Prices
				$rec->{'SPrice'} = $cses{'items_'.$i.'_price_ow'} if $cses{'items_'.$i.'_price_ow'};
				$rec->{'FPPrice'} = $cses{'items_'.$i.'_fpprice_ow'} if $cses{'items_'.$i.'_fpprice_ow'};
				$rec->{'Flexipago'} = $cses{'items_'.$i.'_fpago_ow'} if $cses{'items_'.$i.'_fpago_ow'};
				$rec->{'Downpayment'} = $cses{'items_'.$i.'_downpayment_ow'} if $cses{'items_'.$i.'_downpayment_ow'};
				$rec->{'shipping_table'} = $cses{'items_'.$i.'_shp_cal_ow'} if $cses{'items_'.$i.'_shp_cal_ow'};
				$rec->{'free_shp_opt'} = $cses{'items_'.$i.'_freeshp_ow'} if $cses{'items_'.$i.'_freeshp_ow'};
				


				$desc[$i] = $rec->{'Name'};
				$desc[$i] = substr($desc[$i],0,35);
				$cses{'items_'.$i.'_desc'} = $rec->{'Model'};
				$msprice=$rec->{'MemberPrice'};
				
				if(!$rec->{'MemberPrice'} or $rec->{'MemberPrice'}==0){
					if ($cfg{'multiprice'} and $cses{'items_'.$i.'_pnum'}>1){
						$msprice=$rec->{'SPrice'.($cses{'items_'.$i.'_pnum'}-1)};
					}else{
						$msprice=$rec->{'SPrice'};
					}
				}
				$cses{'items_'.$i.'_paytype'} = $rec->{'PayType'};
				$cses{'items_'.$i.'_downpayment'} = $rec->{'Downpayment'} if(!$cses{'items_'.$i.'_secret_cupon'}); 
				

				## Calculate EDT
				$aux = $rec->{'edt'};
				($aux>$edt) and ($edt = $aux);		
				
				####################################
				##### Check Cupons			
				####################################
				if ($cses{'cupon'}){
					my ($sth) = &Do_SQL("SELECT * FROM sl_products_categories WHERE ID_products = '$rec->{'ID_products'}'");
					#my ($sth) = &Do_SQL("SELECT * FROM sl_coupons WHERE PublicID='$cses{'cupon'}' AND Status='Active' AND (ValidFrom <= CURDATE() AND ValidTo >= CURDATE() )");
					$reccat = $sth->fetchrow_hashref;
					if ($reccat->{'ID_categories'}){
						$categories_ex='';
						#$categories_ex=&build_find_categories_ex();	
						if($categories_ex){
							$cses{'categories'}=1;
						}						
					}
				}

				(!$edt) and ($edt = 3);
				## Calculate Weight
				$cses{'items_'.$i.'_size'} = $rec->{'SizeW'}*$rec->{'SizeH'}*$rec->{'SizeL'};
				$cses{'items_'.$i.'_weight'} = $rec->{'Weight'};

				##########################################
				#########  Other Payment Types
				##########################################
				if ($cses{'pay_type'} ne 'cc' and $cses{'pay_type'} ne 'lay'){
					$cses{'items_'.$i.'_payments'} = 1;
				}
				##########################################
				#########  CALCULAR PAGO CONTADO
				##########################################
				#if($cses{'pay_type'} ne 'lay'){
					if($cfg{'membership'} and $cses{'type'}eq"Membership")
					{
						$str_price = &format_price($price);
						$total  += $price *  $cses{'items_'.$i.'_qty'};
						$onepay = $price;
						$cses{'items_'.$i.'_discount'} = 0;
						if($cses{'items_'.$i.'_payments'} >= 1 or $cses{'pay_type'} eq 'lay')
						{
							$va{'items_discounts'} += $price-$msprice;
							$str_disc = "Descuento de Membres&iacute;a: " . &format_price($price-$msprice) if(($price-$msprice)!=0);
							$cses{'items_'.$i.'_discount'} = $price-$msprice;
							$onepay = $msprice;
						}
						if($cses{'pay_type'} eq 'lay' or $cses{'pay_type'} eq 'cod'){
							$price = $rec->{'MemberPrice'};
							$price=$cses{'items_'.$i.'_price'} if($cses{'items_'.$i.'_secret_cupon'} and $cses{'items_'.$i.'_price'}!=0);
						}
					}
					elsif ($fpprice>0){
						$str_price = &format_price($fpprice);
						$total  += $fpprice *  $cses{'items_'.$i.'_qty'};
						$onepay = $price;
						if ($cses{'items_'.$i.'_payments'} == 1 or $cses{'items_'.$i.'_payments'} eq '3c'){
							$va{'items_discounts'} += $fpprice-$price;
							$str_disc = "Descuento : " . &format_price($fpprice-$price);
							$cses{'items_'.$i.'_discount'} = $fpprice-$price;
							#$cses{"dayspay"}=20;
						}
						
					}elsif($cses{'items_'.$i.'_id'} =~ /$cfg{'disc40'}/){
						$str_price = &format_price($price);
						$total  += $price *  $cses{'items_'.$i.'_qty'};
						$str_disc = " Descuento : " . &format_price( ($price-0) * 40/100);
						$onepay = $price - ($price * 40)/100;
						if ($cses{'items_'.$i.'_payments'} == 1 or $cses{'items_'.$i.'_payments'} eq '3c'){
							#$cses{"dayspay"}=20;
							$va{'items_discounts'} += $price * 40/100;
							$cses{'items_'.$i.'_discount'} = $price * 40/100;
						}
					}elsif ($cses{'items_'.$i.'_id'} =~ /$cfg{'disc30'}/){
						$str_price = &format_price($price);
						$total  += $price *  $cses{'items_'.$i.'_qty'};
						$str_disc = " Descuento : " . &format_price( ($price-0) * 30/100);
						$onepay = $price - ($price * 30)/100;
						if ($cses{'items_'.$i.'_payments'} == 1 or $cses{'items_'.$i.'_payments'} eq '3c'){
							$va{'items_discounts'} += $price * 30/100;
							$cses{'items_'.$i.'_discount'} = $price * 30/100;
							#$cses{"dayspay"}=20;
						}
					}else{
						$str_price = &format_price($price);
						$total  += $price *  $cses{'items_'.$i.'_qty'};
						if ($cfg{'fpdiscount'.$cses{'items_'.$i.'_fpago'}}>0 and ($cses{'items_'.$i.'_payments'} == 1 or $cses{'items_'.$i.'_payments'} eq '3c')){
							$va{'items_discounts'} += $price * $cfg{'fpdiscount'.$cses{'items_'.$i.'_fpago'}}/100;
							$cses{'items_'.$i.'_discount'} = $price * $cfg{'fpdiscount'.$cses{'items_'.$i.'_fpago'}}/100;
							#$cses{"dayspay"}=20;
						}
						if (($price * $cfg{'fpdiscount'.$cses{'items_'.$i.'_fpago'}}/100) >0){
							$str_disc = " Descuento : " . &format_price( $price * $cfg{'fpdiscount'.$cses{'items_'.$i.'_fpago'}}/100);
							$onepay = $price - $price * $cfg{'fpdiscount'.$cses{'items_'.$i.'_fpago'}}/100;
						}else{
							$onepay = $price;
						}
					}
				# }else{
				# 	$str_price = &format_price($price);
				# 	$str_disc = "";
				# 	$onepay = $price;
				# 	$total  += $price *  $cses{'items_'.$i.'_qty'};
				# }

				my ($sthk) = &Do_SQL("SELECT * FROM sl_skus WHERE ID_sku_products='$cses{'items_'.$i.'_id'}' and Status='Active'");
				$rec = $sthk->fetchrow_hashref;
				$choices = &load_choices('-',$rec->{'choice1'},$rec->{'choice2'},$rec->{'choice3'},$rec->{'choice4'});
				($rec->{'Status'} eq 'Backorder')	and	($backorder	=	'<span style="color:red;">[Backorder]</span>');
				$cses{'items_'.$i.'_payments'} = $in{"fpago$i".$cses{"items_".$i."_id"}} if ($in{"fpago$i".$cses{"items_".$i."_id"}} and $banddays==0);

				if ($cses{'pay_type'} eq 'cc' and $in{'step'} eq '7a'){
					##########################################
					#########  STEP 7
					##########################################
					#&cgierr($i);
					(!$cses{'items_'.$i.'_payments'}) and ($cses{'items_'.$i.'_payments'}=1);
				}elsif(($cses{'pay_type'} eq 'cc' or $cses{'pay_type'} eq 'lay') and $in{'step'} eq '8'){
					##########################################
					#########  STEP 8
					##########################################
					############################################################
					#Mensual a Quincenal o a Contado seg�n sea el caso
					############################################################
					#Si ya se ha establecido pago quincenal y el n�mero de pagos del producto en turno es diferente de uno y es igual al n�mero de pagos mensuales. Entonces
					if($cses{'items_'.$i.'_fpago'} eq $cses{'items_'.$i.'_payments'} and $banddays==1 and $cses{'dayspay'}==15 and $cses{'items_'.$i.'_fpago'}!=1){
						#Si est� habilitado pagos quincenales en el sistema o si el producto tiene tipo de pago Layaway entonces
						if($cfg{'fpbiweekly'} or $cses{'items_'.$i.'_paytype'}=~/Layaway/)
						{
							#Se establecen los pagos para el producto en turno en quincenales
							$cses{'items_'.$i.'_payments'}*=2;
						}
						else
						{
							#Si no entonces se establecen como pago de contado
							$cses{'items_'.$i.'_payments'}=1;
						}
					}
					############################################################
					#Mensual a Semanal o a Contado seg�n sea el caso
					############################################################
					#Si ya se ha establecido pago semanal y el n�mero de pagos del producto en turno es diferente de uno y es igual al n�mero de pagos mensuales. Entonces
					elsif($cses{'items_'.$i.'_fpago'} eq $cses{'items_'.$i.'_payments'} and $banddays==1 and $cses{'dayspay'}==7 and $cses{'items_'.$i.'_fpago'}!=1){
						#Si est� habilitado pagos semanales en el sistema o si el producto tiene tipo de pago Layaway entonces
						if($cfg{'fpweekly'} or $cses{'items_'.$i.'_paytype'}=~/Layaway/)
						{
							#Se establecen los pagos para el producto en turno en semanales
							$cses{'items_'.$i.'_payments'}*=4;
						}
						else
						{
							#Si no entonces se establecen como pago de contado
							$cses{'items_'.$i.'_payments'}=1;
						}
					}
					############################################################
					#Quincenal a Mensual
					############################################################
					#Si ya se ha establecido pago mensual y el producto en turno tiene pagos quincenales entonces
					elsif($cses{'items_'.$i.'_fpago'}*2 eq $cses{'items_'.$i.'_payments'} and $banddays==1 and $cses{'dayspay'}==30){
						 #se cambian por pagos mensuales
						$cses{'items_'.$i.'_payments'}/=2;
					}
					############################################################
					#Quincenal a Semanal
					############################################################
					#Si ya se ha establecido pago semanal y el producto en turno tiene pagos quincenales entonces
					elsif($cses{'items_'.$i.'_fpago'}*2 eq $cses{'items_'.$i.'_payments'} and $banddays==1 and $cses{'dayspay'}==7){
						#Si est� habilitado pagos semanales en el sistema o si el producto tiene tipo de pago Layaway entonces
						if($cfg{'fpweekly'} or $cses{'items_'.$i.'_paytype'}=~/Layaway/)
						{
							#se cambian por pagos semanales
							$cses{'items_'.$i.'_payments'}*=2;
						}
						else
						{
							#Si no entonces se establecen como pago de contado
							$cses{'items_'.$i.'_payments'}=1;
						}
					}
					############################################################
					#Semanal a Mensual
					############################################################
					#Si ya se ha establecido pago mensual y el producto en turno tiene pagos semanales entonces
					elsif($cses{'items_'.$i.'_fpago'}*4 eq $cses{'items_'.$i.'_payments'} and $banddays==1 and $cses{'dayspay'}==30){
						 #se cambian por pagos mensuales
						$cses{'items_'.$i.'_payments'}/=4;
					}
					############################################################
					#Semanal a Quincenal
					############################################################
					#Si ya se ha establecido pago quincenal y el producto en turno tiene pagos semanales entonces
					elsif($cses{'items_'.$i.'_fpago'}*4 eq $cses{'items_'.$i.'_payments'} and $banddays==1 and $cses{'dayspay'}==15){
						#Si est� habilitado pagos quincenales en el sistema o si el producto tiene tipo de pago Layaway entonces
						if($cfg{'fpbiweekly'} or $cses{'items_'.$i.'_paytype'}=~/Layaway/)
						{
						 	#se cambian por pagos quincenales
							$cses{'items_'.$i.'_payments'}/=2;
						}
						else
						{
							#Si no entonces se establecen como pago de contado
							$cses{'items_'.$i.'_payments'}=1;
						}
					}

					

					if($banddays==0){
						if($cses{'items_'.$i.'_fpago'} eq $cses{'items_'.$i.'_payments'} and $cses{'items_'.$i.'_fpago'}!=1){
							$cses{'dayspay'}=30;
							$banddays=1;
						}elsif($cses{'items_'.$i.'_fpago'}*2 eq $cses{'items_'.$i.'_payments'}){
							$cses{'dayspay'}=15;
							$banddays=1;
						}elsif($cses{'items_'.$i.'_fpago'}*4 eq $cses{'items_'.$i.'_payments'} or $cses{'items_'.$i.'_fpago'}*4+1 eq $cses{'items_'.$i.'_payments'}){
							$cses{'dayspay'}=7;
							$banddays=1;
						}
						elsif($cses{'items_'.$i.'_payments'} eq '3c'){
							$cses{'dayspay'}=20;
							$banddays=1;
						}
						else{
							$cses{'dayspay'}=1;
						}
					}
					#$cses{'items_'.$i.'_downpayment1'} = $cses{'items_'.$i.'_price'} * 0.07;
					if($cses{'items_'.$i.'_payments'} > 1 && $cses{'dayspay'}==15){ #quincenal
						#$total+=$cses{'items_'.$i.'_downpayment1'};
					} else { 
						#$total  += $price * $cses{'items_'.$i.'_qty'};
					}

					$cses{'items_'.$i.'_payments'} = $in{"fpago$i".$cses{"items_".$i."_id"}} if ($in{"fpago$i".$cses{"items_".$i."_id"}} > 0 and $banddays==0);
					## dp
					($in{"fpago$i".$cses{"items_".$i."_id"}} eq '1d' and $banddays==0) and ($cses{'items_'.$i.'_dponepay'}=1) and ($cses{'items_'.$i.'_payments'}= 1) and (&save_callsession());
					($in{"fpago$i".$cses{"items_".$i."_id"}} and $in{"fpago$i".$cses{"items_".$i."_id"}} ne '1d' and $cses{'items_'.$i.'_dponepay'}) and (delete($cses{'items_'.$i.'_dponepay'})) and (&save_callsession());
					if ($cses{'items_'.$i.'_downpayment'}>0)# or $cses{'items_'.$i.'_downpayment1'}>0)
					{
						$flexipago = &show_products_payments($i,$onepay,$price,$fpprice,$str_disc);
					}else{
						$flexipago = &show_products_payments($i,$onepay,$price,$fpprice,$str_disc);
					}
				}else{
					$flexipago = '';
				}
				
				$choiceslink = '';
				($in{'step'} =~ /8/) and ($choiceslink = &build_edit_choices_module(substr($cses{'items_'.$i.'_id'},3),$script_url,"cmd=console_order&step=$in{'step'}&drop=$i#tabs","tabchoice$i"));
				
				#if($cses{'items_'.$i.'_payments'}==2*$cses{'items_'.$i.'_fpago'}){
				#	$price1=$price + $cses{'items_'.$i.'_downpayment1'};
				#}else{
				#	$price1=$price;
				#}
				#$str_price	 = &format_price($price1);
				##$price	 = &format_price($price);
				$va{'itemsproducts_list'} .= qq|
						<tr  onmouseover='m_over(this)' onmouseout='m_out(this)'>
							<td class="smalltext">|;
				$va{'itemsproducts_list'} .= qq|<a href='/cgi-bin/mod/sales/admin?cmd=console_order&step=$in{"step"}&drop=$i#tabs'><img src='$va{'imgurl'}/$usr{'pref_style'}/b_drop.png' title='Drop' alt='' border='0'></a>| if ($in{'step'} =~ /8/);
				$va{'itemsproducts_list'} .= qq|			
									<a href="/cgi-bin/mod/sales/admin?cmd=console_order&step=2&action=search&id_products=|.substr($cses{'items_'.$i.'_id'},3,6).qq|&choice1=$rec->{'choice1'}&choice2=$rec->{'choice2'}&choice3=$rec->{'choice3'}&choice4=$rec->{'choice4'}"><img src='[va_imgurl]/[ur_pref_style]/b_view.gif' title='View' alt='' border='0'></a>
									 |. &format_sltvid($cses{'items_'.$i.'_id'}). qq|&nbsp; 
									 |. $choiceslink .qq|
									 </td>
							<td class="smalltext" id="tabchoice$i">$cses{'items_'.$i.'_qty'}</td>
							<td class="smalltext">$desc[$i] $backorder $choices <br>$flexipago</td>
							<td class="smalltext" align='right' nowrap>$str_price</td>
						</tr>\n|;

				## ADG ->
				# Calcula el impuesto por cada pruducto que agregue, asignar el formato 0.16			
				my ($tax_product);
				my ($id_products_temp) = substr($cses{'items_'.$i.'_id'},3,6);

		 		if($id_products_temp > 0) {
			 		my ($sth) = &Do_SQL("SELECT MAX(sale_tax) FROM (SELECT if(sale_tax IS NULL,0,sale_tax) AS sale_tax FROM sl_skus_parts INNER JOIN sl_parts USING(ID_parts) INNER JOIN sl_skus USING(ID_sku_products) WHERE ID_products='$id_products_temp')taxes");
			 		$tax_product = $sth->fetchrow();
		 		}

				if($tax_product > 0) {
					$tax_product = ($tax_product/100);
				}else {
					$tax_product = 0;
				}

				my ($tax_calculated_for_product) = $cses{'tax_total'};
		 		if($tax_product < $tax_calculated_for_product) {
		 			$tax_calculated_for_product = $tax_product;
		 		}
				
				## Se agrega Tax_percent en campo Tax_percent
				$cses{'items_'.$i.'_tax_percent'} = $tax_calculated_for_product;
				$cses{'items_'.$i.'_shptax'} = 0;
				$cses{'items_'.$i.'_shptax_percent'} = 0;



				$cses{'items_'.$i.'_tax'} = $taxesfp > 0 ? $taxesfp : $taxes;

			 	if($cfg{'shptax'}) {
			 		### Si se cobra impuesto al envio. 

			 		if ($cses{'tax_total'} > 0 and $cses{'shipping_total'} > 0 ) {

						my $shipping_costs = ($cses{'items_'.$i.'_shp'.$in{'shp_type'}})? $cses{'items_'.$i.'_shp'.$in{'shp_type'}} : 0;
						$shipping_costs = sprintf("%.".$sys{'fmt_curr_decimal_digits'}."f",$shipping_costs);
						if (lc($cfg{'shptaxtype'}) eq 'net') {

							### $cses{'items_'.$i.'_shptax'} = $cses{'shipping_total'} * $cses{'tax_total'};
							$cses{'items_'.$i.'_shptax'} = $shipping_costs * $cses{'tax_total'};
							# aplicamos el redondeo
							$cses{'items_'.$i.'_shptax'} = sprintf("%.".$sys{'fmt_curr_decimal_digits'}."f",$cses{'items_'.$i.'_shptax'});
							
							$cses{'items_'.$i.'_shptax_percent'} = $cses{'tax_total'};

							### Calculo de shipping por producto
							$cses{'items_'.$i.'_newshipping'} = $shipping_costs;
						}
						elsif (lc($cfg{'shptaxtype'}) eq 'gross') {

							$cses{'items_'.$i.'_shptax'} = ($shipping_costs - ($shipping_costs / (1+$cses{'tax_total'})));
							# aplicamos el redondeo
							$cses{'items_'.$i.'_shptax'} = sprintf("%.".$sys{'fmt_curr_decimal_digits'}."f",$cses{'items_'.$i.'_shptax'});
							
							$cses{'items_'.$i.'_shptax_percent'} = $cses{'tax_total'};

							### Calculo de shipping por producto
							$cses{'items_'.$i.'_newshipping'} = $shipping_costs - $cses{'items_'.$i.'_shptax'};
						}

					}

					$total_tax += $cses{'items_'.$i.'_tax'};
					$total_shptax += $cses{'items_'.$i.'_shptax'};

			 	}				


			 	### Si se cobra impuesto al envio. 
			 # 	if($cfg{'shptax'}) {

				# 	## Calculate Tax individually
				# 	$cses{'items_'.$i.'_tax'} = $taxesfp > 0 ? $taxesfp : $taxes;


				# 	if($fpprice > 0){

				# 		$cses{'items_'.$i.'_tax'} =

				# 		if ($cses{'items_'.$i.'_payments'} == 1 or $cses{'items_'.$i.'_payments'} eq '3c') {
							
				# 			## Se calcula tax en base al tipo de costo del producto
				# 			if($cses{'shptax'} eq 'Gross') {
				# 				$cses{'items_'.$i.'_tax'} = (($gross_price - $cses{'items_'.$i.'_discount'}) * $cses{'items_'.$i.'_qty'}) - ((($gross_price - $cses{'items_'.$i.'_discount'}) * $cses{'items_'.$i.'_qty'}) / (1 + $tax_calculated_for_product));
				# 			}else {
				# 				$cses{'items_'.$i.'_tax'} = ((($gross_price - $cses{'items_'.$i.'_discount'}) * $cses{'items_'.$i.'_qty'}) * $tax_calculated_for_product);
				# 			}

				# 		}else {

				# 			## Aun no estoy seguro como se debe calcular para este caso
				# 			$cses{'items_'.$i.'_tax'} = $cses{'items_'.$i.'_fpprice'} * $cses{'items_'.$i.'_qty'} * $tax_calculated_for_product;
				# 			$cses{'items_'.$i.'_discount'} = 0;
				# 		}

				# 	}else{

				# 		if($cfg{'membership'} and $cses{'type'}eq"Membership") {
							
				# 			## Se calcula tax en base al tipo de costo del producto
				# 			if($cses{'shptax'} eq 'Gross') {
				# 				$cses{'items_'.$i.'_tax'} = (($gross_price - $cses{'items_'.$i.'_discount'}) * $cses{'items_'.$i.'_qty'}) - ((($gross_price - $cses{'items_'.$i.'_discount'}) * $cses{'items_'.$i.'_qty'}) / (1 + $tax_calculated_for_product));
				# 			}else {
				# 				$cses{'items_'.$i.'_tax'} = ((($gross_price - $cses{'items_'.$i.'_discount'}) * $cses{'items_'.$i.'_qty'}) * $tax_calculated_for_product);
				# 			}

				# 		}
				# 		elsif ($cses{'items_'.$i.'_payments'} == 1 or $cses{'items_'.$i.'_payments'} eq '3c') {							
							
				# 			## Se calcula tax en base al tipo de costo del producto
				# 			if($cses{'shptax'} eq 'Gross') {
				# 				$cses{'items_'.$i.'_tax'} = (($gross_price - $cses{'items_'.$i.'_discount'}) * $cses{'items_'.$i.'_qty'}) - ((($gross_price - $cses{'items_'.$i.'_discount'}) * $cses{'items_'.$i.'_qty'}) / (1 + $tax_calculated_for_product));
				# 			}else {
				# 				$cses{'items_'.$i.'_tax'} = ((($gross_price - $cses{'items_'.$i.'_discount'}) * $cses{'items_'.$i.'_qty'}) * $tax_calculated_for_product);
				# 			}

				# 		}else{

				# 			## Aun no estoy seguro como se debe calcular para este caso
				# 			$cses{'items_'.$i.'_tax'} = $cses{'items_'.$i.'_fpprice'} * $cses{'items_'.$i.'_qty'} * $tax_calculated_for_product;
				# 			$cses{'items_'.$i.'_discount'} = 0;
				# 		}
				# 	}
					

				# 	## redondeamos el tax al numero de digitos configurado en el sistema para cuadrar cifras
				# 	$cses{'items_'.$i.'_tax'} = sprintf("%.".$sys{'fmt_curr_decimal_digits'}."f",$cses{'items_'.$i.'_tax'});					
			

				# 	### Configuramos el tax del shipping hasta que tenemos el shipping_total
				# 	## Determinamos el tax del shipping dependiendo si esta o no incluido en el precio(net / gross)
				# 	if ($cses{'tax_total'} > 0 and $cses{'shipping_total'} > 0 ) {

				# 		my $shipping_costs = ($cses{'items_'.$i.'_shp'.$in{'shp_type'}})? $cses{'items_'.$i.'_shp'.$in{'shp_type'}} : 0;
				# 		$shipping_costs = sprintf("%.".$sys{'fmt_curr_decimal_digits'}."f",$shipping_costs);
				# 		if (lc($cfg{'shptaxtype'}) eq 'net') {

				# 			### $cses{'items_'.$i.'_shptax'} = $cses{'shipping_total'} * $cses{'tax_total'};
				# 			$cses{'items_'.$i.'_shptax'} = $shipping_costs * $cses{'tax_total'};
				# 			# aplicamos el redondeo
				# 			$cses{'items_'.$i.'_shptax'} = sprintf("%.".$sys{'fmt_curr_decimal_digits'}."f",$cses{'items_'.$i.'_shptax'});
							
				# 			$cses{'items_'.$i.'_shptax_percent'} = $cses{'tax_total'};

				# 			### Calculo de shipping por producto
				# 			$cses{'items_'.$i.'_newshipping'} = $shipping_costs;
				# 		}
				# 		elsif (lc($cfg{'shptaxtype'}) eq 'gross') {

				# 			$cses{'items_'.$i.'_shptax'} = ($shipping_costs - ($shipping_costs / (1+$cses{'tax_total'})));
				# 			# aplicamos el redondeo
				# 			$cses{'items_'.$i.'_shptax'} = sprintf("%.".$sys{'fmt_curr_decimal_digits'}."f",$cses{'items_'.$i.'_shptax'});
							
				# 			$cses{'items_'.$i.'_shptax_percent'} = $cses{'tax_total'};

				# 			### Calculo de shipping por producto
				# 			$cses{'items_'.$i.'_newshipping'} = $shipping_costs - $cses{'items_'.$i.'_shptax'};
				# 		}

				# 	}

				# 	$total_tax += $cses{'items_'.$i.'_tax'};
				# 	$total_shptax += $cses{'items_'.$i.'_shptax'};

				# ## ADG <-
			 # 	}else { 

				# 	## Calculate Tax individually
				# 	if($fpprice > 0){
				# 			if ($cses{'items_'.$i.'_payments'} == 1 or $cses{'items_'.$i.'_payments'} eq '3c'){
				# 					$cses{'items_'.$i.'_tax'} = (($cses{'items_'.$i.'_price'} * $cses{'items_'.$i.'_qty'}) - ($cses{'items_'.$i.'_discount'} * $cses{'items_'.$i.'_qty'})) *  $cses{'tax_total'};
				# 			}else{
				# 					$cses{'items_'.$i.'_tax'} = $cses{'items_'.$i.'_fpprice'} * $cses{'items_'.$i.'_qty'} * $cses{'tax_total'};
				# 					$cses{'items_'.$i.'_discount'} = 0;
				# 			}
				# 	}else{
				# 			if($cfg{'membership'} and $cses{'type'}eq"Membership")
				# 			{
				# 				$cses{'items_'.$i.'_tax'} = (($cses{'items_'.$i.'_price'} * $cses{'items_'.$i.'_qty'})-($cses{'items_'.$i.'_discount'} * $cses{'items_'.$i.'_qty'})) *  $cses{'tax_total'};
				# 			}
				# 			elsif ($cses{'items_'.$i.'_payments'} == 1 or $cses{'items_'.$i.'_payments'} eq '3c'){
				# 					$cses{'items_'.$i.'_tax'} = (($cses{'items_'.$i.'_price'} * $cses{'items_'.$i.'_qty'}) - ($cses{'items_'.$i.'_discount'} * $cses{'items_'.$i.'_qty'})) *  $cses{'tax_total'};
				# 			}else{
				# 					##$cses{'items_'.$i.'_tax'} = $cses{'items_'.$i.'_price'} * $cses{'items_'.$i.'_qty'} * $cses{'tax_total'};
				# 					$cses{'items_'.$i.'_tax'} = $cses{'items_'.$i.'_fpprice'} * $cses{'items_'.$i.'_qty'} * $cses{'tax_total'};
				# 					$cses{'items_'.$i.'_discount'} = 0;
				# 			}
				# 	}

				# 	$total_tax += $cses{'items_'.$i.'_tax'};
				# }




			}
		}

		$cses{'total_i'}=$total;
		
		# &calculate_shipping;
		# if($in{'step'}eq 6){
		# 	$va{'shptotal1'} = &format_price($va{'shptotal1'});
		# 	$va{'shptotal2'} = &format_price($va{'shptotal2'});
		# 	$va{'shptotal3'} = &format_price($va{'shptotal3'});
		# 	$va{'shptotalf'} = &format_price(0);
		# }
		# $in{'shp_type'}=1 if !($in{'shp_type'} and $cses{'pay_type'}ne'cod');
		# $in{'shp_type'}=$cfg{'codshptype'} if($cses{'pay_type'}eq'cod');
		# $cses{'shipping_total'} = $va{'shptotal'.$in{'shp_type'}};
		# $cses{'shp_type'} = $in{'shp_type'};


		### Si se cobra impuesto al envio. Reasignamos costo para shipping

		## FC -> 		
		if( !$cfg{'use_default_shipment'} or $cfg{'use_default_shipment'}==0){
			if ($cfg{'shptax'}) {
				if (lc($cfg{'shptaxtype'}) eq 'net') {
					$cses{'shipping_total'} = $va{'shptotal'.$in{'shp_type'}};

				}elsif (lc($cfg{'shptaxtype'}) eq 'gross') {
				 	$cses{'shipping_total'} = $va{'shptotal'.$in{'shp_type'}} - $total_shptax;

				}
			}
		}

		## <- FC

		if($in{'step'}eq 6){

			$va{'shptotal1'} = &format_price($va{'shptotal1'});
			$va{'shptotal2'} = &format_price($va{'shptotal2'});
			$va{'shptotal3'} = &format_price($va{'shptotal3'});
			$va{'shptotalf'} = &format_price(0);

		}


		##########################################
		#########  SERVICES    ###################
		##########################################
		$banddays=0;
		for my $i(1..$cses{'servis_in_basket'}){
			if ($cses{'servis_'.$i.'_qty'}>0 and $cses{'servis_'.$i.'_id'}>0){

				### Si se cobra impuesto a Servicios. Agrega los taxes del servicio al total de taxes
				if ($cfg{'calc_tax_in_services'} and $cfg{'calc_tax_in_services'}==1){
					if ($cses{'servis_'.$i.'_tax'} == 0 and $cses{'servis_'.$i.'_tax_percent'} > 0){
						$cses{'servis_'.$i.'_tax'} = $cses{'servis_'.$i.'_price'} * $cses{'servis_'.$i.'_tax_percent'};
					}
					$total_servtax += $cses{'servis_'.$i.'_tax'};
				}

				$price=$cses{'servis_'.$i.'_price'};
				if($cses{'servis_'.$i.'_fpago'} eq $cses{'servis_'.$i.'_payments'} and $banddays==1 and $cses{'dayspay'}==15){
					$cses{'servis_'.$i.'_payments'}*=2;
				}elsif($cses{'servis_'.$i.'_fpago'}*2 eq $cses{'servis_'.$i.'_payments'} and $banddays==1 and $cses{'dayspay'}==30){
					$cses{'servis_'.$i.'_payments'}/=2;
				}
				($cses{'servis_'.$i.'_id'} eq "60000".$cfg{'postdatedfeid'}) and ($cses{'total_order'}-$cses{'shipping_total'}-$cses{'tax_total'} <= 350) and ($cses{'servis_'.$i.'_price'} = $cfg{'postdatedfesprice'});
				($cses{'servis_'.$i.'_id'} eq "60000".$cfg{'postdatedfeid'}) and ($cses{'total_order'}-$cses{'shipping_total'}-$cses{'tax_total'} >  350) and ($cses{'servis_'.$i.'_price'} = $cfg{'postdatedfesprice350'});
				$flexiserv='';
				if ($cses{'servis_'.$i.'_id'} eq "60000".$cfg{'extwarrid'}){
					@itemsessionid = &getsessionfieldid('items_','_id',$cses{'servis_'.$i.'_relid'},'');
					if($cses{'items_'.$itemsessionid[0].'_fpago'} and ($cses{'pay_type'} eq 'cc' or $cses{'pay_type'} eq 'lay') and $in{'step'} eq '8'){
						$cses{'servis_'.$i.'_fpago'}=$cses{'items_'.$itemsessionid[0].'_fpago'} if(!$cses{'servis_'.$i.'_fpago'});
						$cses{'servis_'.$i.'_fpago'}=1;
						$cses{'servis_'.$i.'_payments'}=$cses{'items_'.$itemsessionid[0].'_payments'} if(!$cses{'servis_'.$i.'_payments'});
						$cses{'servis_'.$i.'_payments'} = $in{"fpagoserv$i".$cses{'items_'.$itemsessionid[0].'_id'}} if ($in{"fpagoserv$i".$cses{'items_'.$itemsessionid[0].'_id'}} );
						if($cses{'servis_'.$i.'_payments'}==1){
							$cses{'servis_'.$i.'_price'}=$cfg{'extwarrpctsfp'}*$cses{'items_'.$itemsessionid[0].'_price'}/100;
						}else{
							$cses{'servis_'.$i.'_price'}=$cfg{'extwarrpct'}*$cses{'items_'.$itemsessionid[0].'_fprice'}/100;
							if($cses{'dayspay'}==1){
								if($banddays==0){
									if($cses{'servis_'.$i.'_fpago'}eq$cses{'servis_'.$i.'_payments'}){
										$cses{'dayspay'}=30;
										$banddays=1;
									}elsif($cses{'servis_'.$i.'_fpago'}*2 eq $cses{'servis_'.$i.'_payments'}){
										$cses{'dayspay'}=15;
										$banddays=1;
									}else{
										$cses{'dayspay'}=1;
									}
								}
							}
						}
						### Se cambia el precio de la garantia extendida por el minimo aceptado si es necesario
						$cses{'servis_'.$i.'_price'} = $cfg{'extwarminprice'} if $cses{'servis_'.$i.'_price'} < $cfg{'extwarminprice'};
						if ($in{'step'} eq '8'){
							##########################################
							#########  STEP 8
							##########################################
							$price = $cses{'servis_'.$i.'_price'};#$rec->{'SPrice'};
							if($cses{'servis_'.$i.'_id'} eq "60000".$cfg{'extwarrid'}){
								#$cses{'servis_'.$i.'_downpayment1'} = ($cfg{'extwarrpct'}*$cses{'items_'.$itemsessionid[0].'_price'}/100)*0.07;
							}
							if($cses{'servis_'.$i.'_payments'} > 1 && $cses{'dayspay'}==15){
								#$total+=$cses{'servis_'.$i.'_downpayment1'};
							}
							if($cses{'item_'.$i.'_payments'}/2 > $cses{'item_'.$i.'_fpago'}){
								$paysservices = $cses{'item_'.$i.'_payments'};
								$fpagoservices = $cses{'item_'.$i.'_fpago'};
							} else {
								$paysservices = $cses{'servis_'.$i.'_payments'};
								$fpagoservices = $cses{'servis_'.$i.'_fpago'};
							}
							if($paysservices/2 eq $fpagoservices){
								#$price1 = $price+$cses{'servis_'.$i.'_downpayment1'};
							}else{
								$price1 = $price;
							}
						}
						if ($cses{'servis_'.$i.'_downpayment'}>0)# or $cses{'servis_'.$i.'_downpayment1'}>0)
						{
							$cadpagoinicial=">";
							if($cses{'servis_'.$i.'_downpayment'}>0){
								$cadpagoinicial=">Pago Inicial ".&format_price($cses{'servis_'.$i.'_downpayment'})." + ";
							}
							$flexiserv = &show_servis_payments($i);
						}else{
							$flexiserv = &show_servis_payments($i);
						}
					}else{
						$flexiserv = '';
					}
				}
				$cant_s += $cses{'servis_'.$i.'_qty'};
				$totalqty_s  += $cses{'servis_'.$i.'_qty'};
				if ($cses{'servis_'.$i.'_ser'}){
					my ($sth) = &Do_SQL("SELECT * FROM sl_services WHERE ID_services ='".substr($cses{'servis_'.$i.'_id'},5,4)."'");
					$rec = $sth->fetchrow_hashref;
					$desc[$i] = $rec->{'Name'}." for the product ID: ".&format_sltvid($cses{'servis_'.$i.'_relid'});
					$cses{'servis_'.$i.'_desc'} = $rec->{'Description'};
					if($cses{'servis_'.$i.'_id'} eq "60000".$cfg{'duties'} || $cses{'servis_'.$i.'_id'} eq "60000".$cfg{'insurance'}){
						$price = $cses{'servis_'.$i.'_price'};
						$desc[$i] = $rec->{'Name'}." for the order";
					}
					if ($in{'step'} eq "7a"){
						$price = $cses{'servis_'.$i.'_price'};#$rec->{'SPrice'};
						if($cses{'servis_'.$i.'_id'} eq "60000".$cfg{'extwarrid'}){
							#$cses{'servis_'.$i.'_downpayment1'} = ($cfg{'extwarrpct'}*$cses{'items_'.$itemsessionid[0].'_price'}/100)*0.07;
						}
					}
				}
		    
				if($rec->{'SalesPrice'} eq 'Fixed'){
					if($rec->{'Tax'} eq 'Yes'){
						$total_p_f_ty+= ($price * $cses{'servis_'.$i.'_qty'});	      		
					}else{
						$total_p_f_tn+= ($price * $cses{'servis_'.$i.'_qty'});
					}
				}else{
					if($rec->{'Tax'} eq 'Yes'){
						$total_p_v_ty+= ($total * ($price /100));	
					}else{
						$total_p_v_tn+= ($total * ($price /100));	
					}
				}				
					
				$serviceid=&format_sltvid($cses{'servis_'.$i.'_id'});
				if($rec->{'Status'} ne 'Hidden' and $in{'step'} =~ /8/){
					$linkserv="<a href='$script_url?cmd=console_order&step=$in{'step'}&dropser=$i&id_services=$rec->{'ID_services'}#tabs'><img src='$va{'imgurl'}/$usr{'pref_style'}/b_drop.png' title='Drop' alt='' border='0'></a>";
				}else{
					$linkserv='';
				}
				if($rec->{'SalesPrice'} eq 'Fixed'){
					$total_cs = $price ;
					$cses{'servis_'.$i.'_price'} = $price;
					if($cses{'servis_'.$i.'_payments'}==2*$cses{'servis_'.$i.'_fpago'}){
						$price1=$price + $cses{'servis_'.$i.'_downpayment1'};
						#$total+=$cses{'servis_'.$i.'_downpayment1'} if ($in{'step'}eq'7a');
					}else{
						$price1=$price;
					}
					$price1	 = &format_price($price1);
					$price	 = &format_price($price);
					#&cgierr("$price y $price1");	
					#GV Inicia 27may2008
					$va{'itemsproducts_list'} .= qq|
						<tr  onmouseover='m_over(this)' onmouseout='m_out(this)'>
							<td class="smalltext">$linkserv
							<a href="/cgi-bin/mod/sales/admin?cmd=console_order&step=2&action=search&id_products=|.substr($cses{'servis_'.$i.'_id'},5).qq|"><img src='[va_imgurl]/[ur_pref_style]/b_view.gif' title='View' alt='' border='0'></a>
							$serviceid</td>
							<td class="smalltext">1</td>
							<td class="smalltext">$desc[$i] $flexiserv</td>
							<td class="smalltext" align='right' nowrap>$price1 </td>
						</tr>\n|;
				}else{					
					$total_cs= $cses{'total_i'} * ($rec->{'SPrice'}/100);
					$cses{'servis_'.$i.'_price'} = $total_cs;
					
					$total_cs=&format_price($total_cs);			
					$va{'itemsproducts_list'} .= qq|
						<tr  onmouseover='m_over(this)' onmouseout='m_out(this)'>
							<td class="smalltext">$linkserv $serviceid</td>
							<td class="smalltext">1</td>
							<td class="smalltext">$desc[$i]</td>
							<td class="smalltext" align='right'>$total_cs</td>
						</tr>\n|;
				}			
			}
		}
		
		$total+= $total_p_f_ty + $total_p_v_ty;
		$total+= $total_p_f_tn + $total_p_v_tn;
						
		$va{'shptype1_min'}=0;
		$va{'shptype1_max'}=0;
		($va{'shptype1_min'},$va{'shptype2_min'},$va{'shptype3_min'}) = split(/,/,$cfg{'shp_edt_min'});
		($va{'shptype1_max'},$va{'shptype2_max'},$va{'shptype3_max'}) = split(/,/,$cfg{'shp_edt_max'});
		$va{'shptype1_min'}	+= $edt;
		$va{'shptype1_max'}	+= $edt;
		
		$va{'shptype2_min'}	+= $edt;	
		$va{'shptype2_max'}	+= $edt;
		
		if($totalqty_s >= 1){
			$output .= "<br>".&trans_txt('msg_servis')." : $totalqty_s ";
		}else{
			$totalqty_s = 0;
			$output .= "<br>".&trans_txt('msg_servis')." : No selecciono servicios";
		}
	 	$va{'items_stotal'} = &format_price($total+$totaln);
		$va{'items_shipping'} = &format_price($cses{'shipping_total'});


		### Si se cobra impuesto al envio. Agrega los taxes del shipping al total de taxes
		if ($cfg{'shptax'}) {
			$total_tax += $total_shptax;	
			# linea original
			# $total_tax += $cses{'shipping_total'} * $cses{'tax_total'} if ($cfg{'shptax'} and $cses{'shipping_total'} > 0 and $cses{'tax_total'} > 0) ;	
		}

		### Service Tax
		if ($cfg{'calc_tax_in_services'} and $cfg{'calc_tax_in_services'}==1){
			$total_tax += $total_servtax;
		}
		
		if ($cses{'cupon'} and !$cses{'categories'}){
			my ($sth) = &Do_SQL("SELECT * FROM sl_coupons WHERE PublicID='$cses{'cupon'}' AND Status='Active' AND ValidFrom <= CURDATE() AND ValidTo >= CURDATE();");
			$rec = $sth->fetchrow_hashref;

			if( $total >= $rec->{'MinAmount'} ){

				$cses{'id_coupons'} = $rec->{'ID_coupons'};
				if ($rec->{'DiscPerc'}){
					$cupon = int($total * $rec->{'DiscPerc'})/100;
					$cses{'percent_disc'} = $rec->{'DiscPerc'};
					$output .= "<br>Cupon : $cses{'cupon'}  $rec->{'DiscPerc'} % = " . &format_price(-$cupon);	
				}elsif($rec->{'DiscValue'}){

					if($rec->{'Applied'} eq 'Gross'){
						$rec->{'DiscValue'} = $rec->{'DiscValue'} / ($cses{'tax_total'}+1);
					}

					if( $rec->{'DiscValue'} > $total){
						$rec->{'DiscValue'} = $total;
					}

					$cupon = $rec->{'DiscValue'};
					$cses{'percent_disc'} = ($rec->{'DiscValue'}*100)/$total;
					$output .= "<br>Cupon : $cses{'cupon'}  ".&format_price(-$rec->{'DiscValue'});	
				}

				if($cupon and $cses{'tax_total'}){
					$total_tax -= ($cupon * $cses{'tax_total'});
					$total_tax = 0 if($total_tax < 0);
				}
			}
		}

		if ($va{'items_discounts'}) {
			$cupon += $va{'items_discounts'};
			$va{'items_discounts'} = &format_price($va{'items_discounts'} + $cupon);	
		}elsif($cupon){
			$va{'items_discounts'} = &format_price($cupon);	
		}else{
			$va{'items_discounts'} = '---';
		}
		if ($cses{'tax_total'}){
			$va{'items_taxporc'} = " (".($cses{'tax_total'}*100)."%)";
			#$va{'items_tax'} = &format_price(($total-$cupon)*$cses{'tax_total'});
			#$va{'items_tax'} = &format_price(($cses{'total_i'}-$cupon)*$cses{'tax_total'});
			$va{'items_tax'} = &format_price($total_tax);
		}else{
			$va{'items_tax'} = '---';
		}
		
		
		$cses{'total_disc'} = $cupon;
		#Dejar �sta l�nea como est�, ya que as� no se calculan taxes sobre servicios.GV
		$cses{'total_order'} = int(($total+$totaln-$cupon+$cses{'shipping_total'}+($cses{'total_i'}-$cupon)*$cses{'tax_total'})*100+0.9)/100;
		### Si se cobra impuesto al envio. Agrega los taxes del shipping al total
		if ($cfg{'shptax'}) {
			if($cfg{'use_default_shipment'} or $cfg{'use_default_shipment'}==1){
				$total_shptax = $cfg{$config_values_prices{$cses{'pay_type'}}{1}}*0.16;
				$totalS =$total+$totaln+$cses{'shipping_total'}; 
				$tax_value = 1 + $cses{'tax_total'};
				$va{'items_tax'} = &format_price($totalS * $cses{'tax_total'});
				$cses{'total_order'} = $totalS * $tax_value;
			}else{
				$cses{'total_order'} += $total_shptax;
			}
		}

		### Service Tax
		if ($cfg{'calc_tax_in_services'} and $cfg{'calc_tax_in_services'}==1){
			$cses{'total_order'} += $total_servtax;
		}
		&save_callsession();
		
		$va{'items_total'} = &format_price($cses{'total_order'});
		$cses{'edt'} = $edt;
		return &build_page("console_prodinord.html");
	}else{
		return &trans_txt('empty_cart');
	}
}

sub build_select_pricerange {
# --------------------------------------------------------
	my ($output,$pname);
	my (@ary) = split(/,/,$cfg{'price_range'});
	
	for (0..$#ary){
		($p1,$p2) = split(/-/,$ary[$_],2);
		$pname = &format_price($p1) . " - " . &format_price($p2);
		$output .= "<option value='$ary[$_]'>$pname</option>\n";
	}
	(!$output) and ($output .= "<option value='---'>".&trans_txt('none')."</option>\n");
	return $output;
}


sub build_select_prdtype {
# --------------------------------------------------------
	my ($output);
	my (@ary) = split(/,/,$cfg{'prod_type'});
	for (0..$#ary){
		$output .= "<option value='$ary[$_]'>$ary[$_]</option>\n";
	}
	(!$output) and ($output .= "<option value='---'>".&trans_txt('none')."</option>\n");
	return $output;
}


##################################################################
############                HOME                 #################
##################################################################

sub console_header_links {
# --------------------------------------------------------
	my ($page);
	$page .= "<a href='$script_url?cmd=home'><img src='[va_imgurl]app_bar/home.gif' title='Logoff' alt='' border='0'></a>";
	$page .= "<a href='$script_url?cmd=console_newcall&origin=$in{'origin'}'><img src='[va_imgurl]app_bar/voip.gif' title='New Call' alt='' border='0'></a>";
	
	my (@ary_url,@ary_img,$output,%tmp);
	### Load Other Sessions
	if ($in{'e'}){
		if(open (CFG, "<../common/general.cfg")){
			LINE: while (<CFG>) {
				(/^#/)      and next LINE;
				(/^\s*$/)   and next LINE;
				$line = $_;
				$line =~ s/\n|\r//g;
				my ($td,$name,$value) = split (/\||\=/, $line,3);
				
				if ($td eq "conf" and ($name eq 'auth_dir' or $name eq 'app_title')) {
					$tmp{$name} = $value;
					next LINE;
				}
				if ($tmp{'auth_dir'} and $tmp{'app_title'}){
					if(open (CFG, "<$tmp{'auth_dir'}/$sid")){
						$page .= "<a href='$script_url?cmd=$in{'cmd'}&e=0'><img src='$va{'imgurl'}topimgs/icon.png' title='$tmp{'app_title'}' alt='' border='0'></a>\n";
						last LINE;
					}
				}
			}
		}
	}
	
	for my $i(1..5){
		($i eq $in{'e'}) and next;
		if(open (CFG, "<../common/general.e$i.cfg")){
			LINE: while (<CFG>) {
				(/^#/)      and next LINE;
				(/^\s*$/)   and next LINE;
				$line = $_;
				$line =~ s/\n|\r//g;
				my ($td,$name,$value) = split (/\||\=/, $line,3);
				
				if ($td eq "conf" and ($name eq 'auth_dir' or $name eq 'app_title')) {
					$tmp{$name} = $value;
					next LINE;
				}
				if ($tmp{'auth_dir'} and $tmp{'app_title'}){
					if(open (CFG, "<$tmp{'auth_dir'}/$sid")){
						$page .= "<a href='$script_url?cmd=$in{'cmd'}&e=$i'><img src='$va{'imgurl'}topimgs/icon.e$i.png' title='$tmp{'app_title'}' alt='' border='0'></a>\n";
						delete($tmp{'auth_dir'});
						delete($tmp{'app_title'});
						last LINE;
					}
				}
			}
		}
	}
	
	
	return $page;
}

sub paysummary {
# --------------------------------------------------------
# Last Modified on: 07/24/08 11:14:33
# Last Modified by: MCC C. Gabriel Varela S: Se verifica que la tarjeta no expire antes del �ltimo pago
# Last Modified on: 08/04/08 10:12:10
# Last Modified by: MCC C. Gabriel Varela S
# Last Modified on: 08/06/08 15:20:55
# Last Modified by: MCC C. Gabriel Varela S: Verificar que las cantidades en los pagos sea correcta cuando se mezclan pagos mensuales con 0-15-30
# Last Modified on: 10/28/08 14:51:50
# Last Modified by: MCC C. Gabriel Varela S: Se quita mensaje de son cada tal d�as si es un s�lo pago
# Last Modified on: 10/30/08 10:30:50
# Last Modified by: MCC C. Gabriel Varela S: Se hace que ya no exista downpayment del 7% para pagos quincenales y semanales
# Last Modified on: 11/11/08 17:17:41
# Last Modified by: MCC C. Gabriel Varela S: Se hace que si el tipo de pago es lay away el primer pago sea el �ltimo y como dice el dicho, los �ltimos ser�n los primeros
# Last Modified RB: 12/02/08  18:56:30 Se agrego el template para layaway M.O.
# Last Modified on: 12/18/08 13:49:41
# Last Modified by: MCC C. Gabriel Varela S: Se hace que cuando sea membership, y lay away, el primer pago incluya el precio de la membres�a
# Last Modified RB: 03/12/09  11:32:31 -- Agregue &save_callsession(); al final de la funcion
# Last modified on 4 Feb 2011 16:36:50
# Last modified by: MCC C. Gabriel Varela S. : Se pone por par�metro de configuraci�n los d�as m�nimos previos al vencimiento de la tarjeta y se cambia mensaje
# Last Time Modified by RB on 08/30/2011 : Se aregaron modificaciones para permitir downpaymwent + 1 pago

	if ($in{'pay_type'} eq 'cc' or $in{'pay_type'} eq 'lay'){
		my (@payments,$maxpaym,$fpdate,$tofp,$stfp,$price,$promo_cont,$onepay);
		my ($fpdias)= $cses{'dayspay'};
		my ($fpdiasdp)=0;
		$maxpaym = 1;
		
		$downpaymentinorder=0;
		$cses{'dpio'} = 0;
		if($cses{'dayspay'} eq 15){
			$downpaymentinorder=1;
			$cses{'dpio'} = 1;
		}else{
			## dp2
			for my $i(1..$cses{'items_in_basket'}){
				if ($cses{'items_'.$i.'_downpayment'}>0 && $cses{'items_'.$i.'_payments'} >= $cses{'items_'.$i.'_fpago'} && ($cses{'items_'.$i.'_payments'} >1 or $cses{'items_'.$i.'_dponepay'})) {
					$downpaymentinorder=1;
					$cses{'dpio'} = 1;
				}
			}			
		}
		########################################
		########### Items
		########################################
		PLINE: for my $i(1..$cses{'items_in_basket'}){
			(!$cses{'items_'.$i.'_qty'}) and (next PLINE);
			
			##########################################
			#########  CALCULAR PAGO CONTADO
			##########################################
#			if($cses{'pay_type'} ne 'lay'){
				if($cfg{'membership'} and $cses{'type'}eq"Membership")
				{
					$onepay = $cses{'items_'.$i.'_msprice'};
				}
				elsif ($cses{'items_'.$i.'_fpprice'}>0){
					$onepay = $cses{'items_'.$i.'_price'};
				}elsif($cses{'items_'.$i.'_id'} =~ /$cfg{'disc40'}/){
					$onepay = $cses{'items_'.$i.'_price'} - ($cses{'items_'.$i.'_price'}*(40/100));
				}elsif ($cses{'items_'.$i.'_id'} =~ /$cfg{'disc30'}/){
					$onepay = $cses{'items_'.$i.'_price'} - ($cses{'items_'.$i.'_price'}*(30/100));
				}else{
					$onepay = $cses{'items_'.$i.'_price'} - ($cses{'items_'.$i.'_price'}*$cfg{'fpdiscount'.$cses{'items_'.$i.'_fpago'}}/100);
				}
#			}

			## dp3
			if ($cses{'items_'.$i.'_id'} and $cses{'items_'.$i.'_payments'}==1 and !$downpaymentinorder){
				$payments[$_] += round($onepay,2);
			}elsif ($cses{'items_'.$i.'_payments'} eq '3c'){
				## Skip
				$promo_cont += $onepay/3;
			## dp4
			}elsif ($cses{'items_'.$i.'_id'} and ($cses{'items_'.$i.'_payments'}>1 or $cses{'items_'.$i.'_dponepay'})){
				if ($cses{'items_'.$i.'_downpayment'}>0) {
					$tofp = $cses{'items_'.$i.'_payments'}+1;
					$stfp = 2;
					($cses{'items_'.$i.'_dponepay'}) and ($fpdiasdp=30);#para downpayment sin flexipagos
				}
#				elsif($cses{'items_'.$i.'_downpayment1'}>0 and $cses{'dayspay'}!=30)
#					{
#						$tofp = $cses{'items_'.$i.'_payments'}+1;
#						$stfp = 2;
#				}
				else{
					$tofp = $cses{'items_'.$i.'_payments'};
					$stfp = 1;
				}
				if($cfg{'membership'} and $cses{'type'}eq"Membership")
				{
					$price = $cses{'items_'.$i.'_price'};
				}
				elsif ($cses{'items_'.$i.'_fpprice'}>0){
					$price = $cses{'items_'.$i.'_fpprice'};
				}else{
					$price = $cses{'items_'.$i.'_price'};
				}
				($maxpaym = $tofp) unless ($maxpaym > $tofp);
				for ($stfp..$tofp){
					if ($cses{'items_'.$i.'_payments'} eq '3c'){
						$payments[$_] += round($price/3,2);
					}elsif($cses{'items_'.$i.'_payments'} and $cses{'items_'.$i.'_downpayment'}>0) {
						$payments[$_] += round(($price-$cses{'items_'.$i.'_downpayment'})/($cses{'items_'.$i.'_payments'}),2);
					}
#					elsif($cses{'items_'.$i.'_payments'} and $cses{'items_'.$i.'_downpayment1'}>0 and ($cses{'dayspay'}!=30)){
#						$payments[$_] += round(($price-$cses{'items_'.$i.'_downpayment1'})/($cses{'items_'.$i.'_payments'}),2);
#					}
					elsif ($cses{'items_'.$i.'_payments'}){
						$payments[$_] += round($price/$cses{'items_'.$i.'_payments'},2);
					}
				}
			}
		}
		
		########################################
		########### Service
		########################################
		for my $i(1..$cses{'servis_in_basket'}){
			@itemsessionid=&getsessionfieldid('items_','_id',$cses{'servis_'.$i.'_relid'},''); #JRG 29-05-2008
			
			if ($cses{'servis_'.$i.'_id'} and $cses{'servis_'.$i.'_payments'}==1){
#				if($downpaymentinorder>0) {
#					$payments[2] += round($cses{'servis_'.$i.'_price'},2);
#					$payments[1] += 0;
#				} else {
					$payments[$_] += round($cses{'items_'.$i.'_price'},2);
#				}
			}elsif ($cses{'servis_'.$i.'_id'} and $cses{'servis_'.$i.'_payments'}>1){
#				if($cses{'servis_'.$i.'_downpayment1'}>0 && $cses{'servis_'.$i.'_payments'} > $cses{'servis_'.$i.'_fpago'}){
#					$tofp = $cses{'servis_'.$i.'_payments'}+1;
#					$stfp = 2;	
#					$cses{'total_order'} += $cses{'servis_'.$i.'_downpayment1'};				
#				}
#				 elsif ($cses{'servis_'.$i.'_downpayment1'}>0) {
#					$tofp = $cses{'servis_'.$i.'_payments'}+1;
#					$stfp = 2;
#				}
#				else{
					$tofp = $cses{'servis_'.$i.'_payments'};
					$stfp = 1;
#				}

				($maxpaym = $tofp) unless ($maxpaym > $tofp);
				for ($stfp..$tofp){
					if ($cses{'servis_'.$i.'_payments'} and $cses{'servis_'.$i.'_downpayment'}>0) {
						$payments[$_] += round(($cses{'servis_'.$i.'_price'}-$cses{'servis_'.$i.'_downpayment'})/($cses{'servis_'.$i.'_payments'}),2);
					}elsif ($cses{'servis_'.$i.'_payments'}){
						$payments[$_] += round($cses{'servis_'.$i.'_price'}/$cses{'servis_'.$i.'_payments'},2);
					}
				}
			}
		}
		if ($promo_cont>0 and $maxpaym>=2){
			$payments[2] += $promo_cont;
			$fpdias = 30;
			$payments[1] = $cses{'total_order'}- round($promo_cont,2);
		}elsif ($promo_cont>0 and $maxpaym<2){
			$payments[2] = $promo_cont;
			$maxpaym = 2;
			$fpdias = 30;
			$payments[1] = $cses{'total_order'} - round($promo_cont,2);
		}else{
			$payments[1] = $cses{'total_order'} - round($promo_cont,2)*2;
			#$payments[2] = $promo_cont;
		}
		## dp5
		($fpdias==1 and $fpdiasdp) and ($fpdias=$fpdiasdp);
		
		
		for (2..$maxpaym){
			$payments[1] -= round($payments[$_],2);
		}
	
		#Si el tipo de pago es layaway se cambian los pagos primero por el �ltimo.
		if($cses{'pay_type'}eq"lay")
		{
			my $temp;
			$temp=$payments[1];
			$payments[1]=$payments[$maxpaym];
			$payments[$maxpaym]=$temp;
			if($cfg{'membership'} and $cses{'type'}eq"Membership")
			{
				$pricetoapply=&load_name ('sl_services','ID_services',$cfg{'membershipservid'},'SPrice');
				$payments[1]+=$pricetoapply;
				$payments[$maxpaym]-=$pricetoapply;
			}
		}
		
		#&cgierr($payments[2]);
	
		my ($today) = &get_sql_date();
		$today = &sqldate_plus($today,$cses{'days'})	if	($cses{'days'} > 0 and $cses{'postdated'} eq '1');
		($cses{'pay_type'} eq 'lay' and $cses{'startdate'}) and ($today = $cses{'startdate'});
		for my $i(1..$maxpaym){
			$fpdate = &sqldate_plus($today,$fpdias*($i-1));
			if ($promo_cont>0 and $i >1){
				if ($i == 2){
					$cses{'fppayment2'} = round($promo_cont,2);
					$cses{'fpdate2'} = &sqldate_plus($today,15);
					$va{'amount'} .= &format_price($promo_cont) . " &nbsp; \@ &nbsp; $cses{'fpdate2'}<br>";
					#$payments[2] += round($promo_cont,2);
				}
				$cses{'fppayment'.($i+1)} =  round($payments[$i],2);
				$cses{'fpdate'.($i+1)} = $fpdate;
				$va{'amount'} .= &format_price($payments[$i]) . " &nbsp; \@ &nbsp; $fpdate<br>";
			}else{
				$cses{'fppayment'.$i} =  round($payments[$i],2);
				$cses{'fpdate'.$i} = $fpdate;
				$va{'amount'} .= &format_price($payments[$i]) . " &nbsp; \@ &nbsp; $fpdate<br>";
			}
		}
		#Comparar� la fecha de �ltimo pago con la de expiraci�n de la tarjeta
		if($cses{'pmtfield7'}eq"CreditCard" or $cses{'pmtfield7'}eq"DebitCard")
		{
			$fpdate=~/^(\d{2})(\d{2})-(\d{2})-(\d{2})$/;
			my $lpday=$4;
			$cses{'pmtfield4'}=~/^(\d{2})(\d{2})$/;
			my $edyear=$2;
			my $edmonth=$1;
			my $edday=28;
			if($edmonth==1 or $edmonth==3 or $edmonth==5 or $edmonth==7 or $edmonth==8 or $edmonth==10 or $edmonth==12)
			{
				$edday=31;
			}
			elsif($edmonth==4 or $edmonth==6 or $edmonth==9 or $edmonth==11)
			{
				$edday=30;
			}
			my ($diffs)=&Do_SQL("SELECT datediff('20$edyear-$edmonth-$edday','$fpdate')");
			my $diff=$diffs->fetchrow;
			if($diff<$cfg{'prevent_days'})
			{
				#ADG Se cambio el step 8 por el 7 porque se ciclaba
				$va{'amount'}.="<table border='0' cellspacing='0' cellpadding='2' width='100%'>
							<tr>
		  					<td class='stdtxterr' colspan='2'>Error: No se debe de Confirmar la Orden debido a que el &uacute;ltimo pago es igual o supera a la fecha de expiraci&oacute;n de la tarjeta($edmonth/20$edyear).</td>
							</tr>
						 </table>
						 <script language='javascript'>
						 var str=''+self.location;
							str=str.replace(/#tabs/, '');
							str+='?cmd=console_order&step=7&restartpayments=1#tabs';
							alert('Vencimiento Invalido, la fecha de vencimiento de la tarjeta debe ser al menos $cfg{'prevent_days'} dias despues del la ultima cuota($edmonth/20$edyear).');
						 window.location=str;
						 </script>
						 "
			}
		}
		
		$cses{'fppayments'} = $maxpaym;
		($promo_cont) and (++$cses{'fppayments'});
		$va{'fpdias'} = "";#$fpdias;
		$va{'fpdias'} ="SON CADA $fpdias DIAS." if($fpdias!=1);
		&save_callsession();
		
		if($cses{'pay_type'} eq 'cc' or $cses{'laytype'} eq 'cc'){
			$va{'last4dig'} = substr($cses{'pmtfield3'},-4);
			if ($cses{'pmtfield7'} eq 'DebitCard'){
				$va{'cardtype'} = 'd&eacute;bito';
				$va{'cardtype_en'} = 'debit';
			}else{
				$va{'cardtype'} = 'cr&eacute;dito';
				$va{'cardtype_en'} = 'credit';
			}
			
			return &build_page("console_order8a.html");
		}else{
			return &build_page("console_order8m.html");
		}
	}elsif ($in{'pay_type'} eq 'check'){
		for (1..$cses{'fppayments'}){
			delete($cses{'fppayment'.$_});
			delete($cses{'fpdate'.$_});
		}
		delete($cses{'fppayments'});
		
		return &build_page("console_order8b.html");
	}
}

sub build_find_categories_ex{
# --------------------------------------------------------
	my ($output,$rec,%cols,$key);
	
	my ($sth) = &Do_SQL("SELECT * FROM sl_categories WHERE Status='Active' ORDER BY ID_parent;");
	while ($rec = $sth->fetchrow_hashref){
		if ($rec->{'ID_parent'}>0){
			#$cols{$rec->{'ID_categories'}} = '['.$rec->{'ID_parent'} .']/'. $rec->{'Title'};
			$cols{$rec->{'ID_categories'}} = '['.$rec->{'ID_parent'} .']/'. $rec->{'ID_categories'};
		}else{
			$cols{$rec->{'ID_categories'}} = $rec->{'ID_categories'};
		}
	}	
	$output .= "<option value='---'>".&trans_txt('top_level')."</option>\n";
	foreach $key (sort keys %cols) {
		$cols{$key} =~ s/\[([^]]+)\]/$cols{$1}/;
		#$cols{$key} =~ s/    \[   ([^]]+)   \]   /$cols{$1}/;
	}
	foreach $key (sort {$cols{$a} cmp $cols{$b}} keys %cols ) {
		$output .= "<option value='$key'>$cols{$key}</option>\n";
	}
}

sub load_orderinfo {
# --------------------------------------------------------
	if($cses{'ordert'} ne ''){
		$va{'id_orders'} = $cses{'ordert'}.$cses{'id_orders'};
		$va{'id_customers'} = $cses{'ordert'}.$cses{'id_customers'};	
		$id_orders = $cses{'id_orders'};
		my ($sth) = &Do_SQL("SELECT Status FROM sl_orders WHERE ID_orders='$id_orders';");
		my ($status) = $sth->fetchrow();
		my ($sth) = &Do_SQL("SELECT * FROM `sl_orders_payments` WHERE ID_orders='$id_orders' ORDER BY `Paymentdate` ASC LIMIT 0,1;");
		my ($rec) = $sth->fetchrow_hashref();
		$va{'authcode'} = $rec->{'AuthCode'};
		$va{'payment'} = &format_price($rec->{'Amount'});
		
		if ($rec->{'ID_orders_payments'}>0 ){
			if ($rec->{'AuthCode'}){
				if ($rec->{'Credit-Card'}){
					##$va{'authorization'} qq|
					##This is a copy of your order and authorization.  Your electronic signature was received for this order authorizing charges to your debit card ending in XXXX in the amount of [amount of installment charge] on [dates of charge]." 
					##Esta es una copia de su pedido y de su autorizaci�n de pago. Su firma electr�nica fue recibida para esta orden, autorizando a SLTV efectuar cargos a su tarjeta de d�bito que termina en XXXX por la cantidad de [cantidad del cargo ] los d�as  [fechas del cargo]. 
				}else{
					$va{'authorization'} = '';
				}
				if ($status eq 'In Process'){
					return &build_page("console_order10_msg1.html");   # Order OK
				}else{
					return &build_page("console_order10_msg4.html");   # Order Pending
				}
			}else{#if($cses{'laytype'}eq'mo' ){
				return &build_page("console_order10_msg5.html");   # Order Pending
			}	
		}else{
			return;
		}	
	
	} elsif ($va{'id_orders'}){
		my ($sth) = &Do_SQL("SELECT Status  FROM sl_orders WHERE ID_orders='$va{'id_orders'}';");
		my ($status) = $sth->fetchrow();
		my ($sth) = &Do_SQL("SELECT * FROM `sl_orders_payments` WHERE ID_orders='$va{'id_orders'}' ORDER BY `Paymentdate` ASC LIMIT 0,1;");
		my ($rec) = $sth->fetchrow_hashref();
		$va{'authcode'} = $rec->{'AuthCode'};
		$va{'payment'} = &format_price($rec->{'Amount'});
		if ($rec->{'ID_orders_payments'}>0 ){
			if ($rec->{'AuthCode'}){
				if ($rec->{'Credit-Card'}){
					##$va{'authorization'} qq|
					##This is a copy of your order and authorization.  Your electronic signature was received for this order authorizing charges to your debit card ending in XXXX in the amount of [amount of installment charge] on [dates of charge]." 
					##Esta es una copia de su pedido y de su autorizaci�n de pago. Su firma electr�nica fue recibida para esta orden, autorizando a SLTV efectuar cargos a su tarjeta de d�bito que termina en XXXX por la cantidad de [cantidad del cargo ] los d�as  [fechas del cargo]. 
				}else{
					$va{'authorization'} = '';
				}
				if ($status eq 'Processed'){
					return &build_page("console_order10_msg1.html");   # Order OK
				}else{
					return &build_page("console_order10_msg4.html");   # Order Pending
				}
			}elsif($rec->{'Type'} ne 'Credit-Card'){
				return &build_page("console_order10_msg3.html");
			}else{
				return &build_page("console_order10_msg2.html");   # Order Void
			}
		}else{
			return;
		}
	}else{
		return ;
	}

}

sub flexiservice{
# --------------------------------------------------------
# Created on: 
# Last Modified on: 
# Last Modified by: 
# Author: 
# Description : 
# Parameters : 
#	
#	
	my ($id)=@_;
	#GV Inicia modificaci�n 23jun2008
	if ($in{"fpago$i".$cses{'items_'.$id.'_id'}}){
		$cses{'items_'.$id.'_payments'} = $in{"fpago$i".$cses{'items_'.$id.'_id'}}if(!$cses{'items_'.$i.'_secret_cupon'});
		#GV Termina modificaci�n 23jun2008
		#($tot_fp < $in{'fpago_'.$cses{'items_'.$id.'_id'}}) and ($tot_fp =  $in{'fpago_'.$cses{'items_'.$id.'_id'}})
	}
	
	if($cses{'items_'.$id.'_payments'}>1){
		if(!$cses{'items_'.$id.'_flexidone'})
		{
			++$cses{'servis_in_basket'};
			$cses{'servis_'.$cses{'servis_in_basket'}.'_id'} = "60000".$cfg{'flexiserviceid'};
			$cses{'servis_'.$cses{'servis_in_basket'}.'_qty'} = 1;
			$cses{'servis_'.$cses{'servis_in_basket'}.'_ser'} = 1;
			$cses{'servis_'.$cses{'servis_in_basket'}.'_price'} = $cfg{'flexiserviceporc'}/100*$cses{'items_'.$id.'_price'};
			$cses{'servis_'.$cses{'servis_in_basket'}.'_relid'}=$cses{'items_'.$id.'_id'};
			if($cses{'servis_'.$cses{'servis_in_basket'}.'_price'}<$cfg{'flexiservicemin'})
			{
				$cses{'servis_'.$cses{'servis_in_basket'}.'_price'}=$cfg{'flexiservicemin'};
			}
			elsif($cses{'servis_'.$cses{'servis_in_basket'}.'_price'}>$cfg{'flexiservicemax'})
			{
				$cses{'servis_'.$cses{'servis_in_basket'}.'_price'}=$cfg{'flexiservicemax'};
			}
			$cses{'items_'.$id.'_flexidone'}=$cses{'servis_in_basket'};
		}
#		else
#		{
#			#$cses{'servis_'.$cses{'items_'.$id.'_flexidone'}.'_price'} = $cfg{'flexiserviceporc'}/100*$cses{'items_'.$id.'_price'};
#		}
	}
	else
	{
		if($cses{'items_'.$id.'_flexidone'})
		{
			#Se borra el servicio por cobro de flexipago
			delete($cses{'servis_'.$cses{'items_'.$id.'_flexidone'}.'_id'});
			delete($cses{'servis_'.$cses{'items_'.$id.'_flexidone'}.'_qty'});
			delete($cses{'servis_'.$cses{'items_'.$id.'_flexidone'}.'_ser'});
			delete($cses{'servis_'.$cses{'items_'.$id.'_flexidone'}.'_relid'});
			delete($cses{'items_'.$id.'_flexidone'});
		}
	}
}

sub show_products_payments{
# --------------------------------------------------------
# Created on: 23/jun/2008 09:40:18 AM GMT -06:00
# Last Modified on: 7/7/2008 6:23:03 PM
# Last Modified by: CH
# Author: MCC C. Gabriel Varela S.
# Description : Desplegar� las opciones de pago para productos
# Parameters : $i: n�mero de registro actual
#		$onepay: Precio de contado
#		$fpprice: Precio en flexipagos
#		$str_disc: Descuento en caso de existir
#		$price: Precio del producto actual
# Last Modified on: 07/24/08 12:08:44
# Last Modified by: MCC C. Gabriel Varela S: Se incluye par�metro restartpayments para poner todos los pagos en 1 pago
# Last Modified on: 10/21/08 16:47:06
# Last Modified by: MCC C. Gabriel Varela S: Se corrige que se ponga downpayment 1 para pagos mensuales y semanales
# Last Modified on: 10/22/08 10:10:39
# Last Modified by: MCC C. Gabriel Varela S: Si se cumple que el tipo de pago de la orden no es lay, y adem�s el producto no tiene tipo de pago layaway, entonces se muestra la opci�n de pago de contado
# Last Modified on: 10/23/08 09:19:04
# Last Modified by: MCC C. Gabriel Varela S: Se habilita un solo pago para layaway
# Last Modified on: 10/28/08 14:52:09
# Last Modified by: MCC C. Gabriel Varela S: Siempre se ofrecen pagos semanales y quincenales al elegir Lay-away. Tambi�n se quitan los par�ntesis cuando no hay descuento
# Last Modified on: 10/29/08 09:32:11
# Last Modified by: MCC C. Gabriel Varela S: Se muestran las opciones de lay-away s�lo cuando el producto tiene esa forma de pago y adem�s se eligi� esa forma de pago en la orden.
# Last Modified on: 10/30/08 10:31:21
# Last Modified by: MCC C. Gabriel Varela S: Se hace que ya no exista downpayment del 7% para pagos quincenales y semanales. Tambi�n se habilita weekly 2 en caso de que haya lay-away. Se deja s�lo opci�n basada en 52 semanas
# Last Modified on: 12/18/08 11:43:58
# Last Modified by: MCC C. Gabriel Varela S: Se muestra descuento de membres�a en pagos.
# Last Modified on: 08/28/09 09:41:10
# Last Modified by: MCC C. Gabriel Varela S: Se pone denominador como 1 en caso de no existir.
# Last Time Modified by RB on 08/30/2011 : Se aregaron modificaciones para permitir downpaymwent + 1 pago
# Last Modified on: 16/08/13 12:01:10
# Last Modified by: Alejandro Diaz: Se selecciona automatico el  numero de meses a pagar

	my ($i,$onepay,$price,$fpprice,$str_disc)=@_;
	my ($output,$pagoini);
	$str_disc="($str_disc)" if($str_disc ne "");
	if($in{'restartpayments'}==1)
	{
		$cses{'items_'.$i.'_payments'}=1;
		$cses{'dayspay'}=1;
	}
	
		$output = qq|<SELECT size="1" name="fpago$i$cses{'items_'.$i.'_id'}" onFocus='focusOn( this )' onBlur='focusOff( this )' onChange="recharge(this);">\n|;
		
		if(1)#$cses{'items_'.$i.'_paytype'} !~ /Layaway/ and $cses{'pay_type'}ne"lay")
		{
			### Pago Contado
			$output .= qq|<option value="1"|; ($cses{'items_'.$i.'_payments'} eq '1') and ($output .= " selected "); $output.=qq|>Pago 1 Exhibici&oacute;n : |. &format_price($onepay) .qq| $str_disc</option>\n|;
		}
		
		### 3 Payments - Pago contado
		if ($cfg{'fp3promo'}){
		$output .= qq|<option value="3c" |; ($cses{'items_'.$i.'_payments'} eq '3c') and ($output .= " selected "); $output .= qq|> 3 Pagos (0-15-30 Dias) |. &format_price($onepay/3) .qq|</option>\n|;
		}
		
		### Weekly
#		if ($cfg{'fpweekly'} or ($cses{'items_'.$i.'_paytype'} =~/.*Layaway.*/ and $cses{'pay_type'}eq'lay')){
#		if($cses{'items_'.$i.'_downpayment'}>0)# or $cses{'items_'.$i.'_downpayment1'}>0)
#		{
#			#$pagoini="Pago Inicial ".&format_price($cses{'items_'.$i.'_downpayment'}+$cses{'items_'.$i.'_downpayment1'})." + ";
#			$pagoini="Pago Inicial ".&format_price($cses{'items_'.$i.'_downpayment'})." + ";
#		}
#		$fpprice=$price if($fpprice==0 or !$fpprice);
#		#$output .= qq|<option value=\"|.$cses{'items_'.$i.'_fpago'}*4 .qq|\"|; ($cses{'items_'.$i.'_payments'} eq $cses{'items_'.$i.'_fpago'}*4) and ($output .= " selected "); $output.= "> $pagoini " . ($cses{'items_'.$i.'_fpago'}*4) . " Pagos semanales de " . &format_price(($fpprice-$cses{'items_'.$i.'_downpayment'}-$cses{'items_'.$i.'_downpayment1'})/$cses{'items_'.$i.'_fpago'}/4) .qq|</option>\n|;
#		$output .= qq|<option value=\"|.$cses{'items_'.$i.'_fpago'}*4 .qq|\"|; ($cses{'items_'.$i.'_payments'} eq $cses{'items_'.$i.'_fpago'}*4) and ($output .= " selected "); $output.= "> $pagoini " . ($cses{'items_'.$i.'_fpago'}*4) . " Pagos semanales de " . &format_price(($fpprice-$cses{'items_'.$i.'_downpayment'})/$cses{'items_'.$i.'_fpago'}/4) .qq|</option>\n|;
#		}
		
		### Weekly2
		if ($cfg{'f2pweekly'} or ($cses{'items_'.$i.'_paytype'} =~/.*Layaway.*/ and $cses{'pay_type'}eq'lay'))
		{
			if($cses{'items_'.$i.'_downpayment'}>0)# or $cses{'items_'.$i.'_downpayment1'}>0)
			{
				#$pagoini="Pago Inicial ".&format_price($cses{'items_'.$i.'_downpayment'}+$cses{'items_'.$i.'_downpayment1'})." + ";
				$pagoini="Pago Inicial ".&format_price($cses{'items_'.$i.'_downpayment'})." + ";
			}
			$fpprice=$price if($fpprice==0 or !$fpprice);
			#$output .= qq|<option value=\"|.$cses{'items_'.$i.'_fpago'}*4 .qq|\"|; ($cses{'items_'.$i.'_payments'} eq $cses{'items_'.$i.'_fpago'}*4) and ($output .= " selected "); $output.= "> $pagoini " . ($cses{'items_'.$i.'_fpago'}*4) . " Pagos semanales de " . &format_price(($fpprice-$cses{'items_'.$i.'_downpayment'}-$cses{'items_'.$i.'_downpayment1'})/$cses{'items_'.$i.'_fpago'}/4) .qq|</option>\n|;
			my $numpayments;
			$numpayments=$cses{'items_'.$i.'_fpago'}*4+int($cses{'items_'.$i.'_fpago'}/3);
			$output .= qq|<option value=\"|.$numpayments.qq|\"|; ($cses{'items_'.$i.'_payments'} eq $cses{'items_'.$i.'_fpago'}*4+int($cses{'items_'.$i.'_fpago'}/3)) and ($output .= " selected "); $output.= "> $pagoini " . ($cses{'items_'.$i.'_fpago'}*4+int($cses{'items_'.$i.'_fpago'}/3)) . " Pagos semanales de " . &format_price(($fpprice-$cses{'items_'.$i.'_downpayment'})/$numpayments) .qq| $str_disc</option>\n|;
		}
		
		### Bi Weekly
		if ($cfg{'fpbiweekly'} or ($cses{'items_'.$i.'_paytype'} =~/.*Layaway.*/ and $cses{'pay_type'}eq'lay')){
		if($cses{'items_'.$i.'_downpayment'}>0)# or $cses{'items_'.$i.'_downpayment1'}>0)
		{
			#$pagoini="Pago Inicial ".&format_price($cses{'items_'.$i.'_downpayment'}+$cses{'items_'.$i.'_downpayment1'})." + ";
			$pagoini="Pago Inicial ".&format_price($cses{'items_'.$i.'_downpayment'})." + ";
		}
		$fpprice=$price if($fpprice==0 or !$fpprice);
		#$output .= qq|<option value=\"|.$cses{'items_'.$i.'_fpago'}*2 .qq|\"|; ($cses{'items_'.$i.'_payments'} eq $cses{'items_'.$i.'_fpago'}*2) and ($output .= " selected "); $output.= "> $pagoini " . ($cses{'items_'.$i.'_fpago'}*2) . " Pagos quincenales de " . &format_price(($fpprice-$cses{'items_'.$i.'_downpayment'}-$cses{'items_'.$i.'_downpayment1'})/$cses{'items_'.$i.'_fpago'}/2) .qq|</option>\n|;
		$output .= qq|<option value=\"|.$cses{'items_'.$i.'_fpago'}*2 .qq|\"|; ($cses{'items_'.$i.'_payments'} eq $cses{'items_'.$i.'_fpago'}*2) and ($output .= " selected "); $output.= "> $pagoini " . ($cses{'items_'.$i.'_fpago'}*2) . " Pagos quincenales de " . &format_price(($fpprice-$cses{'items_'.$i.'_downpayment'})/$cses{'items_'.$i.'_fpago'}/2) .qq| $str_disc</option>\n|;
		}
		
		## Monthly
		if ($cfg{'fpmonthly'} and $cses{'items_'.$i.'_fpago'}!=1){
			if($cses{'items_'.$i.'_downpayment'}>0){
				$pagoini = "Pago Inicial ".&format_price($cses{'items_'.$i.'_downpayment'})." + ";
			}
			else
			{
				$pagoini ="";
			}
			if ($fpprice>0){
				$output .= qq|<option value="$cses{'items_'.$i.'_fpago'}"|; ($cses{'items_'.$i.'_payments'} eq $cses{'items_'.$i.'_fpago'}) and ($output .= " selected "); $output.= qq|> $pagoini $cses{'items_'.$i.'_fpago'} Pagos mensuales de |. &format_price(($fpprice-$cses{'items_'.$i.'_downpayment'})/$cses{'items_'.$i.'_fpago'}) .qq| $str_disc</option>\n|;
			}else{
				my $denominador=$cses{'items_'.$i.'_fpago'};
				$denominador=1 if(!$denominador);
				$output .= qq|<option value="$cses{'items_'.$i.'_fpago'}"|; ($cses{'items_'.$i.'_payments'} eq $cses{'items_'.$i.'_fpago'}) and ($output .= " selected "); $output.= qq|> $pagoini $cses{'items_'.$i.'_fpago'} Pagos mensuales de |. &format_price(($price-$cses{'items_'.$i.'_downpayment'})/$cses{'items_'.$i.'_fpago'}) .qq| $str_disc</option>\n|;
			}
		}

		# dp1
		if($cses{'items_'.$i.'_fpago'}==1 and $cses{'items_'.$i.'_downpayment'}>0){
			$pagoini = "Pago Inicial ".&format_price($cses{'items_'.$i.'_downpayment'})." + ";
			my $denominador=$cses{'items_'.$i.'_fpago'};
			$denominador=1 if(!$denominador);
			$output .= qq|<option value="1d"|; ($cses{"items_".$i."_dponepay"}) and ($output .= " selected "); $output.= qq|> $pagoini 1 Pago mensual de |. &format_price($price-$cses{'items_'.$i.'_downpayment'}) .qq| $str_disc</option>\n|;
		}

	$output .= "</select>\n";
		
	if ($cses{'items_'.$i.'_fpago'} > 1){
		$output .= qq|<script type="text/javascript">
			chg_select('fpago$i|.$cses{'items_'.$i.'_id'}.qq|','|.$cses{'items_'.$i.'_fpago'}.qq|');
			</script>\n|;
	}

	return $output;
}

sub show_servis_payments{
# --------------------------------------------------------
# Created on: 23/jun/2008 01:32:18 PM GMT -06:00
# Last Modified on: 
# Last Modified by: 
# Author: MCC C. Gabriel Varela S.
# Description : Desplegar� las opciones de pago para servicios
# Parameters : $i: n�mero de registro actual
#								$fpdisc: Descuento en caso de existir
#								$price: Precio del producto actual
# Last Modified on: 10/30/08 10:31:09
# Last Modified by: MCC C. Gabriel Varela S: Se hace que ya no exista downpayment del 7% para pagos quincenales y semanales
	my ($i)=@_;
	my ($output,$cadpagoinicial,$line1,$line2);
	#$line1=
	$cadpagoinicial=">";
	if ($cses{'servis_'.$i.'_id'} eq "60000".$cfg{'extwarrid'}){
		$cses{'servis_'.$i.'_payments'} = 1;
		return qq|<input type='hidden' name='fpagoserv$i$cses{'items_'.$itemsessionid[0].'_id'}' value='1'>|;
	}
#	elsif ($cses{'servis_'.$i.'_downpayment1'}>0)	{
#		$cadpagoinicial=">Pago Inicial ".&format_price($cses{'servis_'.$i.'_downpayment1'})." + ";
#	}
	$output = qq|<select size="1" name="fpagoserv$i$cses{'items_'.$itemsessionid[0].'_id'}" onFocus='focusOn( this )' onBlur='focusOff( this )' onChange="recharge(this);">
						<option value="1"|; ($cses{'servis_'.$i.'_payments'} eq '1') and ($output .= " selected ");
	$output .= qq|>Pago 1 Exibici&oacute;n</option>|;
	if($cses{'dayspay'}!=30 and $cfg{'fpbiweekly'}==1){
		$output .= qq|	<option value=\"|.($cses{'servis_'.$i.'_fpago'}*2).qq|\"|; ($cses{'servis_'.$i.'_payments'} eq $cses{'servis_'.$i.'_fpago'}*2) and ($output .= " selected ") ; $output.=$cadpagoinicial.$cses{'servis_'.$i.'_fpago'}*2 .qq| Pagos quincenales de |. &format_price($cses{'items_'.$itemsessionid[0].'_price'}*$cfg{'extwarrpct'}/$cses{'servis_'.$i.'_fpago'}/100/2) .qq|</option>| ;
	}
	if($cses{'dayspay'}!=15){
		$output .= qq|	<option value="$cses{'servis_'.$i.'_fpago'}"|; ($cses{'servis_'.$i.'_payments'} eq $cses{'servis_'.$i.'_fpago'}) and ($output .= " selected "); $output.=qq|>$cses{'servis_'.$i.'_fpago'} Pagos mensuales de |. &format_price($cses{'items_'.$itemsessionid[0].'_price'}*$cfg{'extwarrpct'}/$cses{'servis_'.$i.'_fpago'}/100) .qq|</option>|;
	}
	$output .= qq| </select>\n|;
	return $output;
}

sub service_bydefault{
# --------------------------------------------------------
# Forms Involved: step 8
# Created on: 4/17/2008 11:43AM
# Last Modified on: 4/17/2008 
# Last Modified by: Roberto Barcenas
# Author: Roberto Barcenas
# Description : Add an extended warranty service by default to each item in basket
# Parameters : 
# Last Modified RB: 05/06/09  10:22:36 -- Las Garantias Extendidas por default solamente se aplican para SOSL
# Last Modified RB: 07/09/09  12:31:46 -- Las garantias extendidas aplican de acuerdo a parametro en el setup.cfg de inbound. Tambien se aplica costo minimo de acuerdo a parametro
# Last Modified on: 07/09/09 17:44:02
# Last Modified by: MCC C. Gabriel Varela S: Se hace que se pueda agregar garant�a extendida desde paso 2.


	delete($cses{'total_duties'});
	delete($cses{'total_insurance'});
	for my $i(1..$cses{'items_in_basket'}){
		### Garanti Extendida
		if ($cses{'items_'.$i.'_qty'}>0 and $cses{'items_'.$i.'_id'}>0 and !$cses{'items_'.$i.'_ew'} and ($cfg{'extwardefault'}or$cses{'apply_warranty'})){
			++$cses{'servis_in_basket'};
			$cses{'items_'.$i.'_ew'} = 1;
			$cses{'servis_'.$cses{'servis_in_basket'}.'_id'} = "60000".$cfg{'extwarrid'};
			$cses{'servis_'.$cses{'servis_in_basket'}.'_qty'} = 1;
			$cses{'servis_'.$cses{'servis_in_basket'}.'_ser'} = 1;
			$cses{'servis_'.$cses{'servis_in_basket'}.'_relid'} = $cses{'items_'.$i.'_id'};
			$price = &load_name ('sl_products','ID_products',substr($cses{'items_'.$i.'_id'},3),'SPrice') * ($cfg{'extwarrpctsfp'}/100);
			$cses{'servis_'.$cses{'servis_in_basket'}.'_price'} = $price;
			$cses{'servis_'.$cses{'servis_in_basket'}.'_price'} = $cfg{'extwarminprice'} if $cses{'servis_'.$cses{'servis_in_basket'}.'_price'} < $cfg{'extwarminprice'};
		}
		if ($cses{'items_'.$i.'_qty'}>0 and $cses{'items_'.$i.'_id'}>0){
			$cses{'total_duties'} += &load_name ('sl_products','ID_products',substr($cses{'items_'.$i.'_id'},3),'Duties');
			$cses{'total_insurance'} += &load_name ('sl_products','ID_products',substr($cses{'items_'.$i.'_id'},3),'Insurance');
			$id_services = &load_name('sl_products','ID_products',substr($cses{'items_'.$i.'_id'},3,6),'ID_services_related');
		}
		$cses{'servis_'.$cses{'servis_in_basket'}.'_discount'} = 0;
    $cses{'servis_'.$cses{'servis_in_basket'}.'_tax'} = 0;
    $cses{'servis_'.$cses{'servis_in_basket'}.'_payments'} = 1;
    $cses{'servis_'.$cses{'servis_in_basket'}.'_shp1'} = 0;
    $cses{'servis_'.$cses{'servis_in_basket'}.'_shp2'} = 0;
    if($cses{'items_'.$i.'_qty'}>0 and $cses{'items_'.$i.'_id'}>0 and !$cses{'items_'.$i.'_nir'} and $id_services){
    	$related_services = &add_related_services($i);
    }
	}
	#JRG start 09-06-2008 Add duties and insurance
	if($cfg{'duties_insurance'} && $cses{'country_tab'} eq 'mx'){ #validating if the shipping goes to Mexico
		if ($cses{'items_in_basket'}>0 and !$cses{'servis_dut'}){
			++$cses{'servis_in_basket'};
			$cses{'servis_dut'} = 1;
			$cses{'servis_'.$cses{'servis_in_basket'}.'_id'} = "60000".$cfg{'duties'};
			$cses{'servis_'.$cses{'servis_in_basket'}.'_qty'} = 1;
			$cses{'servis_'.$cses{'servis_in_basket'}.'_ser'} = 1;
			$cses{'servis_'.$cses{'servis_in_basket'}.'_price'} = $cses{'total_duties'};
			
		}
		if ($cses{'items_in_basket'}>0 and !$cses{'servis_ins'}){
			++$cses{'servis_in_basket'};
			$cses{'servis_ins'} = 1;
			$cses{'servis_'.$cses{'servis_in_basket'}.'_id'} = "60000".$cfg{'insurance'};
			$cses{'servis_'.$cses{'servis_in_basket'}.'_qty'} = 1;
			$cses{'servis_'.$cses{'servis_in_basket'}.'_ser'} = 1;
			$cses{'servis_'.$cses{'servis_in_basket'}.'_price'} = $cses{'total_insurance'};
			
		}
	}
}

sub add_related_services{
#-----------------------------------------
# Forms Involved: 
# Created on: 10/10/08  09:22:52
# Last Modified on: 10/10/08  09:22:52
# Last Modified by: JRG
# Last Modified Desc:
# Author: JRG
# Description :
# Parameters : 
	
	my ($i)=@_;
	$id_products = substr($cses{'items_'.$i.'_id'},3,6);
	$id_services = 600000000+&load_name('sl_products','ID_products',$id_products,'ID_services_related');
	if ($cses{'items_'.$i.'_qty'}>0 and $cses{'items_'.$i.'_id'}>0 and $id_services){
    ++$cses{'servis_in_basket'};
    #GV Modifica 21abr2008 Se cambia id_services por id_services
    if ($id_services){
      $cses{'servis_'.$cses{'servis_in_basket'}.'_id'} = $id_services;
      $cses{'servis_'.$cses{'servis_in_basket'}.'_qty'} = 1;
      $cses{'servis_'.$cses{'servis_in_basket'}.'_ser'} = 1;
      $cses{'servis_'.$cses{'servis_in_basket'}.'_relid'} = $cses{'items_'.$i.'_id'};
      $price=&load_name ('sl_services','ID_services',substr($id_services,5,4),'SPrice');
      $cses{'servis_'.$cses{'servis_in_basket'}.'_price'} = $price;
      $cses{'items_'.$i.'_nir'}=$id_services;
			return 1;
    }
	} else {
		return 0;
	}
}

sub getsessionfieldid
{
	#Acci�n: Creaci�n
	#Comentarios:
	# --------------------------------------------------------
	# Forms Involved: 
	# Created on: 18/abr/2008 12:14PM GMT -0600
	# Last Modified on:
	# Last Modified by:
	# Author: MCC C. Gabriel Varela S.
	# Description :  Obtiene un valor de una variable de sesi�n
	# Parameters : variable de sesi�n, campo de referencia para buscar, valor de campo de referencia a buscar, valor a regresar (si es vac�a regresa el id)
	($sessionvar, $fieldref, $fieldvalue, $valueret)=@_;
	$foundf=0;
	my @returnresults;
	for my $i(1..$cses{$sessionvar.'in_basket'}){
		if($cses{$sessionvar.$i.$fieldref}eq$fieldvalue)
		{
			if($valueret ne '')
			{
				push @returnresults, $cses{$sessionvar.$i.$valueret};
				$foundf=1;
			}
			else
			{
				#print "a: ".$cses{$sessionvar.$i.$fieldref}.", b: ".$fieldvalue;
				push @returnresults, $i;
				#print "Valor: ".$#returnresults;
				$foundf=1;
			}
		}
	}
	#GV Inicia Modificaci�n 22abr2008
	if(!$foundf)
	{
		return -1;
	}
	else
	{
		return @returnresults;
	}
	#GV Termina Modificaci�n 22abr2008
}

sub build_postdated_button{

	if($cfg{'postdatedbutton'}){
		#return '<input type="button"  value="Postfechada>>" class="button" OnClick="postdatedf()">';

		my $string = lc($cses{'pay_type'}) eq 'cc' ? &trans_txt('postdated') : &trans_txt('reprog');
		return '<input type="button" id="btnPostdated" value="'. $string .' >>" class="button" />';
		
	} else {
		return;
	}
	
}

sub prod_pay_priority_to_num{
# --------------------------------------------------------

# Author: Jose Ramirez Garcia
# Created on: 
# Last Modified on: 11/12/2008
# Last Modified by: 
# Description : 
# Forms Involved: 
# Parameters :
# Last Modified by RB on 07/05/2011 05:13:45 PM : Se evita regresar vacio ya que se interpreta como cero y devuelve COD como resultado verdadero 

	($str)=@_;
	@cfg_paytypes = split(/\$\|/,$cfg{'paypriority'});
	for my $i(0..$#cfg_paytypes){
		if($str eq $cfg_paytypes[$i]){
			return $i;
		}
	}
	return 100;
}


sub pay_types_compare_all{
# --------------------------------------------------------

# Author: Jose Ramirez Garcia
# Created on: 
# Last Modified on: 11/12/2008
# Last Modified by: 
# Description : 
# Forms Involved: 
# Parameters : 
	($value, $item, @arr) = @_;
	for my $a(1..$#arr){
		for my $b(1..$#{$arr[$a]}){
			if($b != $item && &prod_pay_priority_to_num($value)>&prod_pay_priority_to_num($arr[$a][$b])){
				return -1;
			}
		}
	}
	return &prod_pay_priority_to_num($value);
}

sub paytypes_intersection{
# --------------------------------------------------------

# Author: Jose Ramirez Garcia
# Created on: 
# Last Modified on: 11/12/2008
# Last Modified by: 
# Description : 
# Forms Involved: 
# Parameters : 
	my (@arr) = @_;
	my (@inters) = ();
	my ($res) = 0;
	my (@cont) = ();
	for my $a(1..$#arr){
		for my $b(1..$#{$arr[$a]}){
			$num = &prod_pay_priority_to_num($arr[$a][$b]);
			$cont[$num]++;
		}
	}
	@cfg_paytypes = split(/\$\|/,$cfg{'paypriority'});
	for($i=$#cfg_paytypes; $i>=0; $i--){
		if($cont[$i] == $#arr || ($#inters>0 && $cont[$i]>0)){
			$res++;
			$inters[$res]= $cfg_paytypes[$i];
		}
	}
	return @inters;
}


sub paytypes_for_products{
# --------------------------------------------------------

# Author: Jose Ramirez Garcia
# Created on: 
# Last Modified on: 11/12/2008
# Last Modified by: It search valid pay types and match with cses pay type
# Description : 
# Forms Involved: 
# Parameters : 
# Last Modified on: 11/14/08 13:01:48
# Last Modified by: MCC C. Gabriel Varela S: Se cambia para contemplar s�lo los productos v�lidos dentro del carrito
# Last Modified by RB: 10/09/09  16:14:14 -- Se valida tipo de pago para promos
# Last Modified by RB on 07/26/2013: El tipo de pago se toma de la sesion.


	my $cadtypespay;
	$cadtypespay="";
	@dbpaytypes="";
	my @product_pay_types=();
	@cfg_paytypes = split(/\$\|/,$cfg{'paypriority'});
	my $j=0;
	my @opt = ();

	for my $i(1..$cses{'items_in_basket'}){
		if($cses{'items_'.$i.'_id'} and $cses{'items_'.$i.'_qty'}){
			++$j;
	#		$cadtypespay.=$cses{'items_'.$i.'_paytype'};
			#my $tprod='id';
			#($cses{'items_'.$i.'_promo'}) and ($tprod = 'promo');
			#$db_pay_types = &load_name('sl_products','ID_products',substr($cses{'items_'.$i.'_'.$tprod},3,6),'PayType');
			$db_pay_types = $cses{'items_'.$i.'_paytype'};
			@dbpaytypes = split(/\|/,$db_pay_types);
			$cont=0;
			foreach my $value(@dbpaytypes){
				$cont++;
				$product_pay_types[$j][$cont] .= $value;
			}
		}
	}
	if(!$cadtypespay){
		@inter = &paytypes_intersection(@product_pay_types);
		if($#inter > 0){
			for my $i(1..$#inter){
				$cadtypespay.=$inter[$i]."|";
			}
		}
	}
	
	if(!$cadtypespay){
		$con_u=0;
		$con_o=0;
		$var = "";
		$ones = "";
		my (@unique) = ();
		my (@ones) = ();

		for my $a(1..$#product_pay_types){
			if($#{$product_pay_types[$a]} == 1){
				$con_u++;
				$unique[$con_u] = $product_pay_types[$a][1];
			}
			$con_o++;
			$ones[$con_o] = $product_pay_types[$a][1];
		}

		if($#unique > 0){

			my $min = "";
			for my $b(1..$#unique){
				$pr = index($cfg{'paypriority'},$unique[$b]);
				if($pr > -1){
					if(!$min || ($min && $pr < index($cfg{'paypriority'},$min))){
						$min = $unique[$b];
					}
				}
			}

			my ($all_paytypes) = "";
			for my $d(1..$#product_pay_types){
				for my $e(1..$#{$product_pay_types[$d]}){
					if($all_paytypes !~ /$product_pay_types[$d][$e]/){
						$all_paytypes .= $product_pay_types[$d][$e]."|";
					}
				}
			}

			my @in_paytypes = split(/\|/,$all_paytypes);
			$pr_limit = index($cfg{'paypriority'},$min);
			for($k=$#in_paytypes; $k>=0; $k--){
				$priority = index($cfg{'paypriority'},$in_paytypes[$k]);
				if($priority > -1 && $priority <= $pr_limit){
					$cadtypespay .= $in_paytypes[$k]."|";
				}
			}

		} else {

			my $max="";
			$cadtypespay = "";
			
			for my $o(1..$#ones){

				$pr_it = index($cfg{'paypriority'},$ones[$o]);
				
				if(!$max || ($max && $pr_it > index($cfg{'paypriority'},$max))){
					$max = $ones[$o];
				}

			}

			my ($all_paytypes) = "";
			for my $d(1..$#product_pay_types){

				for my $e(1..$#{$product_pay_types[$d]}){

					if($all_paytypes !~ /$product_pay_types[$d][$e]/){
						$all_paytypes .= $product_pay_types[$d][$e]."|";
					}

				}

			}

			my @in_paytypes = split(/\|/,$all_paytypes);
			$pr_max = index($cfg{'paypriority'},$max);
			
			for($n=$#in_paytypes; $n>=0; $n--){

				$priority_max = index($cfg{'paypriority'},$in_paytypes[$n]);
				if($priority_max > -1 && $priority_max <= $pr_max){
					$cadtypespay .= $in_paytypes[$n]."|";
				}

			}

		}

	}
	
	return $cadtypespay;
}	

sub pay_type_verification{
# --------------------------------------------------------

# Author: Jose Ramirez Garcia
# Created on: 
# Last Modified on: 11/12/2008
# Last Modified by: 
# Description : Validate pay type 
# Forms Involved: 
# Parameters :
# Last Time Modified by _RB_ on 07/24/2013: Se agrega verificacion de 

	(!$cses{'pay_type'} and $in{'pay_type'}) and ($cses{'pay_type'} = $in{'pay_type'});
	#&cgierr("$cses{'pay_type'} = $in{'pay_type'}");
	if($cses{'pay_type'}){

		%paytype = ('cc'=>'Credit-Card', 'check'=>'Check','wu' => 'WesternUnion','mo'=> 'Money-Order','fp'=> 'Fexipago','lay'=>'Layaway','cod'=>'COD','rd'=>'Referenced Deposit');
		$cadtypespay = &paytypes_for_products;
		$cadtypespay_zones = $cses{'id_zones'} > 0 ? &load_name('sl_zones','ID_zones',$cses{'id_zones'},'Payment_Type') : '';
		$onlyservices = &only_services_order;

		#&cgierr("hhhh cd: $cadtypespay   y cdz: $cadtypespay_zones   vs " . $paytype{$cses{'pay_type'}});
		if($cadtypespay =~ /$paytype{$cses{'pay_type'}}/ and ($cadtypespay_zones eq '' or $cadtypespay_zones =~ /$paytype{$cses{'pay_type'}}/) ){

			$avpaytypes .= qq|<input type="radio" name="pay_type" value="cc" class="radio">Tarjeta de Cr&eacute;dito&nbsp| if($cfg{'paytypescc'} and $cadtypespay=~/Credit-Card/);
			$avpaytypes .= qq|<input type="radio" name="pay_type" value="check" class="radio">Cheque &nbsp|if ($cfg{'paytypeschk'} and $cadtypespay=~/Check/);
			$avpaytypes .= qq|<input type="radio" name="pay_type" value="mo" class="radio">Money Order &nbsp|if ($cfg{'paytypesmo'} and $cadtypespay=~/Money-Order/);
			$avpaytypes .= qq|<input type="radio" name="pay_type" value="wu" class="radio">Western Union &nbsp|if ($cfg{'paytypeswu'} and $cadtypespay=~/WesternUnion/);
			$avpaytypes .= qq|<input type="radio" name="pay_type" value="lay" class="radio">Apartado&nbsp|if ($cfg{'paytypeslay'} and $cadtypespay=~/Layaway/);
			$avpaytypes .= qq|<input type="radio" name="pay_type" value="cod" class="radio">COD&nbsp|if ($cfg{'paytypescod'} and $cadtypespay=~/COD/);
			$avpaytypes .= qq|<input type="radio" name="pay_type" value="rd" class="radio">Referenced Deposit&nbsp|if ($cfg{'paytypesrd'} and $cadtypespay=~/Referenced Deposit/);

		}

		if(!$avpaytypes && !$onlyservices){
			#&cgierr("mmmm cd: $cadtypespay   y cdz: $cadtypespay_zones   vs " . $paytype{$cses{'pay_type'}});
			print "Content-type: text/html\n\n";
			print "<script>location.href='/cgi-bin/mod/sales/admin?cmd=console_order&step=3&payment_type_verification=1';</script>";
		} else {
			return 1;
		}
	} else {
		return 1;
	}

}


#############################################################################
#############################################################################
#   Function: paytype_fp_available
#
#       Es: Revisa cuando un producto tiene
#       En: 
#
#
#    Created on: 2013-06-18
#
#    Author: _RB_
#
#    Modifications:
#
#
#   Parameters:
#
#      - id_bills: ID_bills
#      - currency_exchange: Currency Exchange
#      
#
#  Returns:
#
#      - None
#
#   See Also:
#
#      <>
#
sub paytype_fp_available {
#############################################################################
#############################################################################

	my $id_products = int($in{'id_products'});
	my $pnum = int($in{'pricenumber'});


	if(!$cses{'paytype_available'}){

		my ($sth) = &Do_SQL("SELECT GROUP_CONCAT(DISTINCT CONCAT(PayType,'-',FP)) FROM sl_products_prices WHERE ID_products = '$id_products';");
		my ($res) = $sth->fetchrow();
		($res ne '') and ($cses{'paytype_available'} = $res);


		my ($sth1) = &Do_SQL("SELECT CONCAT(PayType,'-',FP) FROM sl_products_prices WHERE ID_products_prices = '$pnum' AND ID_products = '".$id_products."';");
		my ($res1) = $sth1->fetchrow();
		($res1 ne '') and ($cses{'paytype_order'} = $res1);

		return;
	
	}else{

		my ($sth) = &Do_SQL("SELECT CONCAT(PayType,'-',FP) FROM sl_products_prices WHERE ID_products_prices = '$pnum' AND ID_products = '".$id_products."';");
		my ($res) = $sth->fetchrow();

		if($res ne $cses{'paytype_order'}){

			delete($cses{'items_'.$cses{'items_in_basket'}.'_qty'});
			delete($cses{'items_'.$cses{'items_in_basket'}.'_id'});
			print "Content-type: text/html\n\n";
			print "<script>window.location.href = 'admin?cmd=console_order&step=2&id_products=$in{'id_products'}&action=search&err=3';</script>";

		}


	}

}



sub only_services_order{
# --------------------------------------------------------

# Author: Jose Ramirez Garcia
# Created on: 12/17/2008
# Last Modified on: 
# Last Modified by: 
# Description : 
# Forms Involved: 
# Parameters : 

	for my $i(1..$cses{'items_in_basket'}){
		$prod=0;
		if($cses{'items_'.$i.'_id'} && $cses{'items_'.$i.'_qty'}){
			$prod++;
		}
	}
	for my $i(1..$cses{'servis_in_basket'}){
		$serv=0;
		if($cses{'servis_'.$i.'_id'} && $cses{'servis_'.$i.'_qty'}){
			$serv++;
		}
	}
	if($serv && !$prod){
		return 1;
	} else {
		return 0;
	}
}


sub cod_redir{
# --------------------------------------------------------
# Author: Jose Ramirez Garcia
# Created on: 
# Last Modified on: 
# Last Modified by: 
# Description : 
# Forms Involved: 
# Parameters : 
# Last Modified RB: 05/11/09  13:53:32 -- Se agrega horario de entrega de COD
# Last Modified on: 07/08/09 16:30:58
# Last Modified by: MCC C. Gabriel Varela S: Se manda a llamar a cod_drivers_to_status
	
	if($cses{'pay_type'} eq "cod" or $cses{'pay_type'} eq "rd"){

		$in{'step'} =~ s/4/5/;
		&pay_type_verification if $in{'step'} < 10;

		if($in{'step'} =~ /5/ && $cses{'id_customers'}){
			
			my ($sth) = &Do_SQL("SELECT * FROM sl_customers WHERE id_customers='".$cses{'id_customers'}."'");
			while ($rec = $sth->fetchrow_hashref){
				$in{'shp_address1'} = $rec->{'Address1'};
				$in{'shp_address2'} = $rec->{'Address2'};
				$in{'shp_address3'} = $rec->{'Address3'};
				$in{'shp_city'} = $rec->{'City'};
				$in{'shp_state'} = $rec->{'State'};
				$in{'shp_zip'} = $rec->{'Zip'};
				
				#-- ADG -->
				#-- configuracion de direccion diferente para mexico
				if(uc($cfg{'country'}) eq 'MX')  {
					$in{'shp_address1'} = $rec->{'Address1'};
					$in{'shp_address2'} = $rec->{'Address2'};
					$in{'shp_address3'} = $rec->{'Address3'};
					$in{'shp_urbanization'} = $rec->{'Urbanization'};
					$in{'shp_city'} = $rec->{'City'};
					$in{'shp_state'} = $rec->{'State'};
					$in{'shp_zip'} = $rec->{'Zip'};
					
				}
				#<-- ADG --
			}

		} elsif($in{'step'} =~ 6 || $in{'step'} =~ 7 || $in{'step'} =~ 8){

			&pay_type_verification;
			if ($cses{'pay_type'} eq "rd"){
				$in{'step'} = '8';
				$cses{'status8'} = 'ok';
				$va{'paytype'} = &trans_txt('pay_type_'.$cses{'pay_type'});
				$va{'speechname'}= 'ccinbound:8rd- Confirm Order';
			}else{
				$in{'step'} = '8';
				$cses{'status8'} = 'ok';
				$va{'paytype'} = "C.O.D.";
				$va{'speechname'}= 'ccinbound:8- Confirm Order';

				#$va{'delivery_dates'} = 'Los posibles d&iacute;as de entrega de este producto son <span style="color:red;">'.&load_name("sl_deliveryschs","Zip",$in{'shp_zip'},"Delivery_days").'</span>  en horario de <span style="color:red;">'.&load_name("sl_deliveryschs","Zip",$in{'shp_zip'},"Delivery_hours").'</span>' if $in{'e'} eq '1';
				$va{'delivery_dates'} .='<table border="0" cellspacing="0" cellpadding="2" width="100%" style="border:1px solid #ccc;">
											<tr>
												<td class="gcell_on" align="center">Mensajer&iacute;a</td>
												<td class="gcell_on" align="center">D&iacute;as de Entrega</td>
												<td class="gcell_on" align="center">Horario de Servicio</td>
												<td class="gcell_on" align="center">Pronostico en d&iacute;as</td>
												<td class="gcell_on" align="center">Se acepta</td>
											</tr>
											'.&get_cod_delivery_dates($cses{'shp_zip'}).'
										</table>';
			}
															
			$va{'pdmaxdays'} = $cfg{'postdateddays'};
			
			&service_bydefault();
		
		}elsif($in{'step'} == 10){

			$va{'speechname'}= 'ccinbound:10- COD';
			$in{'id_orders'} = 'C'.$cses{'id_orders'};
			if($cses{'id_customers'}) {
				$in{'id_customers'} = 'C'.$cses{'id_customers'};
			} 
			#$in{'id_customers'} = 'C'.$cses{'id_customers'};
			require('admin.step10.html.cgi');

		}

	}

}

sub code_translate{
#-----------------------------------------
# Created on: 12/30/08  17:53:31 By  Roberto Barcenas
# Forms Involved: console.html.cgi step9
# Description : traduce el codigo incorrecto por el correcto
# Parameters :
# Last Modified RB: 03/11/09  15:47:55 -- Se agrego pay_type 'cod' 
	
	my ($config) = @_;
	my ($wprod,$rprod);
	
	if(length($cfg{$config}) == 13){
		$wprod = int('100'.substr( $cfg{$config},0,6));
		$rprod = int('100'.substr( $cfg{$config},7,6));
	}else{
		$wprod = int(substr( $cfg{$config},0,9));
		$rprod = int(substr( $cfg{$config},10,9));
	}
	

	my ($sth) = &Do_SQL("UPDATE sl_orders_products SET ID_products='$rprod' WHERE ID_products='$wprod' AND ID_orders = '$cses{'id_orders'}' ");
	my ($sth) = &Do_SQL("UPDATE sl_orders_products SET Related_ID_products='$rprod'  WHERE Related_ID_products='$wprod' AND ID_orders = '$cses{'id_orders'}' ");

}

sub nivelprecio{
# --------------------------------------------------------
# Created on: 7/4/2009 7:20:36 PM By  Carlos Haas
# Forms Involved: console.html.cgi step9
# Description : 
# Parameters :
# 
	
	return "<tr><td class='menu_bar' colspan='4'> ".$cses{'paytype_order'}."</td></tr>";

	my ($plavel)=0; my $pname;

	if ($cfg{'multiprice'}){

		if ($cses{'items_in_basket'}>=1){

			for my $i(1..$cses{'items_in_basket'}){

				if ($cses{'items_'.$i.'_qty'}>0 and $cses{'items_'.$i.'_id'}>0){

					if ($cses{'items_'.$i.'_pnum'} > $plavel){

						$plavel = $cses{'items_'.$i.'_pnum'};
						$pname = $cses{'items_'.$i.'_oname'};

					}

				}

			}
			
			if ($plavel){
				$cses{'id_pricelevels'} = $plavel;
				return "<tr><td class='menu_bar' colspan='4'>$plavel) ".$pname."</td></tr>";
			}else{
				return "<tr><td class='menu_bar' colspan='4'>".&trans_txt('empty_cart')."</td></tr>";
			}
		}else{
			return "<tr><td class='menu_bar' colspan='4'>".&trans_txt('empty_cart')."</td></tr>";
		}
	}
	return '';
}

sub show_shipments{

# --------------------------------------------------------
# Forms Involved: 
# Created on: 07/06/09 15:13:03
# Author: MCC C. Gabriel Varela S.
# Description :   
# Parameters :
# Last Modified on: 07/09/09 15:46:52
# Last Modified by: MCC C. Gabriel Varela S: Se habilita para paso 8
# Last Modified on: 07/10/09 18:21:24
# Last Modified by: MCC C. Gabriel Varela S: Se habilita para COD
# Last Modified RB: 09/03/09  18:34:36 -- Se agrego descuento en shipping basado en configuracion(para TC)
# Last Modified RB: 10/09/09  16:17:11 -- Se corrige shipping para promos para tomar el shipping del producto virtual.
# Last Modified RB: 10/09/09  16:51:30 -- Se toma un solo shipping para productos Promo y no shipping por producto
# Last Modified RB: 12/07/2010  19:05:30 -- Se agregan parametros para calculo de shipping 
# Last modified on 4/4/11 8:16 AM
# Last modified by: MCC C. Gabriel Varela S. :Se hace que no se muestre el shipping si el producto se agreg� por secret_cupon.
# Last Modified by RB on 06/03/2011 06:08:14 PM : Se agrega Prepaid-Card al descuento con TDC
# Last Modified by RB on 11/08/2011: Se agrega overwrite de shipping
# Last Modified by RB on 09/05/2012: Se agrega opcion para express delivery basado en configuracion. Para TDC
# Last Modified by FC on 09/09/2015: Se agregan costo de envio para order y no por linea de producto si esta activado en configuració.
	#$va{'shipments_options'} .= qq|Mensaje|;
	#&load_callsession();

	my %config_values_prices = (
		'cod',	{1,'shipment_cod_standard',2,'shipment_cod_express',3,'shipment_cod_cod'}, 
		'cc',	{1,'shipment_cc_standard',2,'shipment_cc_express',3,'shipment_cc_cod' },
		'rd',	{1,'shipment_rd_standard',2,'shipment_rd_express',3,'shipment_rd_cod' }
	);
	if(int($in{'chgshp_type'}) > 0 and $cfg{'express_delivery'}){
		$cses{'shp_type'} = int($in{'chgshp_type'});
	}


	## Shipment Type
	my (@types) = split(/,/,$cfg{'shp_types'});
	$va{'this_shp_type'} = qq|<b>|.$types[$cses{'shp_type'} - 1] .qq|</b> |;
	$va{'img_shp_' . $cses{'shp_type'}} = '<img src="/sitimages/delivery_'.$cses{'shp_type'}.'_on.jpg" title="'.$types[$cses{'shp_type'} - 1].'">';
	(lc($cses{'pay_type'}) ne 'cod') and ($va{'shp_notcod_display'} = 'display:table') and ($va{'shp_cod_display'} = 'display:none');
	(lc($cses{'pay_type'}) eq 'cod') and ($va{'shp_notcod_display'} = 'display:none') and ($va{'shp_cod_display'} = 'display:table');


	#######
	####### Express Delivery Allowance
	#######
	if($cfg{'express_delivery'}){

		my $i = 1;
		foreach my $type (@types) {
			if ($cses{'shp_type'} != $i and $i <= 3){
				$va{'img_shp_' . $i} = '<a href="'.$script_url.'?cmd=[in_cmd]&step=[in_step]&chgshp_type='.$i.'"><img src="/sitimages/delivery_'.$i.'_off.jpg" title="'.$types[$i - 1].'" name="delivery_'.$i.'" onmouseover="document.delivery_'.$i.'.src=\'/sitimages/delivery_'.$i.'_on.jpg\'" onmouseout="document.delivery_'.$i.'.src=\'/sitimages/delivery_'.$i.'_off.jpg\'"></a>';
			}
			$i++;
		}

	}
	# $va{'express_delivery'} = $cfg{'express_delivery'};
	$in{'shp_type'} = $cses{'shp_type'};
	
	if($in{'dropshp'}){
		if($cses{'pay_type'}eq'cod'){
			$cses{'items_'.$in{'dropshp'}.'_shpf'}=$cses{'items_'.$in{'dropshp'}.'_shp3'};
			$cses{'items_'.$in{'dropshp'}.'_shp3'}=0;
		}else{
			$cses{'items_'.$in{'dropshp'}.'_shpf'}=$cses{'items_'.$in{'dropshp'}.'_shp' . $cses{'shp_type'}};
			$cses{'items_'.$in{'dropshp'}.'_shp' . $cses{'shp_type'}}=0;
		}
		
	
	}elsif($in{'activateshp'}){
		if($cses{'pay_type'}eq'cod'){
			$cses{'items_'.$in{'activateshp'}.'_shp3'}=$cses{'items_'.$in{'activateshp'}.'_shpf'};
			delete($cses{'items_'.$in{'activateshp'}.'_shpf'});
		}else{
			$cses{'items_'.$in{'activateshp'}.'_shp' . $cses{'shp_type'}}=$cses{'items_'.$in{'activateshp'}.'_shpf'};
			delete($cses{'items_'.$in{'activateshp'}.'_shpf'});
		}
		
	}

	if ($cses{'items_in_basket'} > 0 || $cses{'servis_in_basket'} > 0){

		my $flag=0;
		my $orderShipment;
		$tot_shpa_st=0;
		$tot_shpa_ex=0;
		$tot_shpa_sc=0;

		my $express_delivery_valid = (!$cses{'id_zones_express_delivery'} or $cses{'id_zones_express_delivery'} ne 'Yes') ? 0 : 1; ## Abajo se valida por cada producto
		$va{'express_style'} = qq|style="display:none"|;

		PRODUCTS:for my $i(1..$cses{'items_in_basket'}){

			next PRODUCTS	if($cses{'items_'.$i.'_promo'} and $cses{'items_'.$i.'_qty'}>0  and $cses{'items_'.$i.'_id'}>0 and $flag == $cses{'items_'.$i.'_promo'});

			if ($cses{'items_'.$i.'_qty'}>0 and $cses{'items_'.$i.'_id'}>0){				

				my $tprod='id';
				($cses{'items_'.$i.'_promo'}) and ($tprod = 'promo') and ($flag=$cses{'items_'.$i.'_promo'});
				my ($sth) = &Do_SQL("SELECT * FROM sl_products WHERE ID_products='".substr($cses{'items_'.$i.'_id'},3,9)."'");
				$rec = $sth->fetchrow_hashref;
				$desc[$i] = $rec->{'Name'};
				$desc[$i] = substr($desc[$i],0,35);

				my $shpcal;
				## Overwrite Shipping
				if($cses{'items_'.$i.'_shp_ow'}){
					$shptotal1 = $cses{'items_'.$i.'_shp_ow'};
					$shptotal1 = $cses{'items_'.$i.'_shp_ow'};
					$shptotal1 = $cses{'items_'.$i.'_shp_ow'};
					$shpcal = $cses{'items_'.$i.'_shp_cal_ow'};
					$rec->{'free_shp_opt'} = $cses{'items_'.$i.'_freeshp_ow'}
				}else{
					my $idpacking = &load_name('sl_products','ID_products',substr($cses{'items_'.$i.'_'.$tprod},3,6),'ID_packingopts');
					$shpcal = &load_name('sl_products','ID_products',substr($cses{'items_'.$i.'_'.$tprod},3,6),'shipping_table');
					my $shpmdis = &load_name('sl_products','ID_products',substr($cses{'items_'.$i.'_'.$tprod},3,6),'shipping_discount');
					($va{'shptotal1'},$va{'shptotal2'},$va{'shptotal3'},$va{'shptotal1pr'},$va{'shptotal2pr'},$va{'shptotal3pr'},$va{'shp_text1'},$va{'shp_text2'},$va{'shp_text3'},$va{'shp_textpr1'},$va{'shp_textpr2'},$va{'shp_textpr3'})= &sltv_itemshipping($cses{'edt'},$cses{'items_'.$i.'_size'},1,1,$cses{'items_'.$i.'_weight'},$idpacking,$shpcal,$shpmdis,substr($cses{'items_'.$i.'_'.$tprod},3,6));
				}

				if($cfg{'shpdis_cc'} and $cses{'pay_type'} =~ /cc|ppc/ and $shpcal eq 'Fixed'){
					#&cgierr("$cfg{'shpdis_cc'} and $cses{'pay_type'}");
					$va{'shptotal1'} = round($va{'shptotal1'}*$cfg{'shpdis_cc'},3);	
					$va{'shptotal2'} = round($va{'shptotal2'}*$cfg{'shpdis_cc'},3);
					$va{'shptotal3'} = round($va{'shptotal3'}*$cfg{'shpdis_cc'},3);

					$va{'shptotal1pr'} = round($va{'shptotal1pr'}*$cfg{'shpdis_cc'},3);	
					$va{'shptotal2pr'} = round($va{'shptotal2pr'}*$cfg{'shpdis_cc'},3);
					$va{'shptotal3pr'} = round($va{'shptotal3pr'}*$cfg{'shpdis_cc'},3);					
				}
				
				my $this_cost_standard;
				my $this_cost_express;
				my $this_cost_scheduled;

				if ($cses{'items_'.$i.'_shpf'} or $cses{'items_'.$i.'_secret_cupon'}){

					$this_cost_standard = 0;
					$this_cost_express = 0;
					$this_cost_scheduled = 0;
					$decor = " style=' text-decoration: line-through'";

				}else{

					$this_cost_standard = $cses{'shp_state'} eq 'PR-Puerto Rico' ? $va{'shptotal1pr'} : $va{'shptotal1'};
					$this_cost_express = $cses{'shp_state'} eq 'PR-Puerto Rico' ? $va{'shptotal2pr'} : $va{'shptotal2'};
					$this_cost_scheduled = $cses{'shp_state'} eq 'PR-Puerto Rico' ? $va{'shptotal3pr'} : $va{'shptotal3'};

					$tot_shpa_st += $this_cost_standard;
					$tot_shpa_ex += $this_cost_express;
					$tot_shpa_sc += $this_cost_scheduled;

					$decor ='';

				}
				#&cgierr("MES:$in{'step'}");
				#$step=$in{'step'};

				if($in{'step'}<7){
					$step=6;
				}else{
					$step=8;
				}
				$orderShipment = $cfg{'use_default_shipment'} and $cfg{'use_default_shipment'} == 1 ? true : false;

				############################
				############################
				#### Standard Delivery
				############################
				############################
				$va{'shipments_options_standard'} .= qq|
						<tr  onmouseover='m_over(this)' onmouseout='m_out(this)'>
							<td class="smalltext">	
									<!--a href="/cgi-bin/mod/sales/admin?cmd=console_order&step=2&action=search&id_products=|.substr($cses{'items_'.$i.'_id'},3,6).qq|&choice1=$rec->{'choice1'}&choice2=$rec->{'choice2'}&choice3=$rec->{'choice3'}&choice4=$rec->{'choice4'}"><img src='[va_imgurl]/[ur_pref_style]/b_view.gif' title='View' alt='' border='0'></a-->
									 |. &format_sltvid($cses{'items_'.$i.'_id'}). qq|&nbsp;</td>
							<td class="smalltext">$desc[$i]</td>
							<td class="smalltext" align='right' nowrap $decor>|;


				if($cses{'shp_type'} == 1){
					if($rec->{'free_shp_opt'} eq 'Yes' and !$cses{'items_'.$i.'_shpf'} and !$orderShipment){			
						$va{'shipments_options_standard'} .= qq|<a href='/cgi-bin/mod/sales/admin?cmd=console_order&step=$step&dropshp=$i#tabs'>
													<img src='$va{'imgurl'}/$usr{'pref_style'}/checkmark_off.gif' title='Free Shipping' alt='Free Shipping' border='0'></a>|;
					}
					## $orderShipment bandera que verifica configuracion de sobreescritura de shipping
					if($rec->{'free_shp_opt'} eq 'Yes' and $cses{'items_'.$i.'_shpf'} and !$orderShipment){
						$va{'shipments_options_standard'} .= qq|<a href='/cgi-bin/mod/sales/admin?cmd=console_order&step=$step&activateshp=$i#tabs'>
													<img src='$va{'imgurl'}/$usr{'pref_style'}/checkmark.gif' title='Free Shipping' alt='Free Shipping' border='0'></a>|;
					}
				}
				if( !$orderShipment){
					$va{'shipments_options_standard'} .= &format_price($this_cost_standard).qq|</td>\n</tr>\n|;
				}


				############################
				############################
				#### Express Delivery
				############################
				############################
				(!$cses{'items_'.$i.'_express_delivery'} or $cses{'items_'.$i.'_express_delivery'} ne 'Yes') and ($express_delivery_valid = 0);

				$va{'shipments_options_express'} .= qq|
						<tr  onmouseover='m_over(this)' onmouseout='m_out(this)'>
							<td class="smalltext">	
									<!--a href="/cgi-bin/mod/sales/admin?cmd=console_order&step=2&action=search&id_products=|.substr($cses{'items_'.$i.'_id'},3,6).qq|&choice1=$rec->{'choice1'}&choice2=$rec->{'choice2'}&choice3=$rec->{'choice3'}&choice4=$rec->{'choice4'}"><img src='[va_imgurl]/[ur_pref_style]/b_view.gif' title='View' alt='' border='0'></a-->
									 |. &format_sltvid($cses{'items_'.$i.'_id'}). qq|&nbsp;</td>
							<td class="smalltext">$desc[$i]</td>
							<td class="smalltext" align='right' nowrap $decor>|;


				if($cses{'shp_type'} == 2){

					if($rec->{'free_shp_opt'} eq 'Yes' and !$cses{'items_'.$i.'_shpf'} and !$orderShipment){			
						$va{'shipments_options_express'} .= qq|<a href='/cgi-bin/mod/sales/admin?cmd=console_order&step=$step&dropshp=$i#tabs'>
													<img src='$va{'imgurl'}/$usr{'pref_style'}/checkmark_off.gif' title='Free Shipping' alt='Free Shipping' border='0'></a>|;
					}

					if($rec->{'free_shp_opt'} eq 'Yes' and $cses{'items_'.$i.'_shpf'} and !$orderShipment){
						$va{'shipments_options_express'} .= qq|<a href='/cgi-bin/mod/sales/admin?cmd=console_order&step=$step&activateshp=$i#tabs'>
													<img src='$va{'imgurl'}/$usr{'pref_style'}/checkmark.gif' title='Free Shipping' alt='Free Shipping' border='0'></a>|;
					}

				}

				if( !$orderShipment){
					$va{'shipments_options_express'} .= &format_price($this_cost_express).qq|</td>\n</tr>\n|;
				}


				############################
				############################
				#### Scheduled Delivery (COD)
				############################
				############################
				$va{'shipments_options_scheduled'} .= qq|
						<tr  onmouseover='m_over(this)' onmouseout='m_out(this)'>
							<td class="smalltext">	
									<!--a href="/cgi-bin/mod/sales/admin?cmd=console_order&step=2&action=search&id_products=|.substr($cses{'items_'.$i.'_id'},3,6).qq|&choice1=$rec->{'choice1'}&choice2=$rec->{'choice2'}&choice3=$rec->{'choice3'}&choice4=$rec->{'choice4'}"><img src='[va_imgurl]/[ur_pref_style]/b_view.gif' title='View' alt='' border='0'></a-->
									 |. &format_sltvid($cses{'items_'.$i.'_id'}). qq|&nbsp;</td>
							<td class="smalltext">$desc[$i]</td>
							<td class="smalltext" align='right' nowrap $decor>|;


				if($cses{'shp_type'} == 3){
					if($rec->{'free_shp_opt'} eq 'Yes' and !$cses{'items_'.$i.'_shpf'} and !$orderShipment){			
						$va{'shipments_options_scheduled'} .= qq|<a href='/cgi-bin/mod/sales/admin?cmd=console_order&step=$step&dropshp=$i#tabs'>
													<img src='$va{'imgurl'}/$usr{'pref_style'}/checkmark_off.gif' title='Free Shipping' alt='Free Shipping' border='0'></a>|;
					}

					if($rec->{'free_shp_opt'} eq 'Yes' and $cses{'items_'.$i.'_shpf'} and !$orderShipment){
						$va{'shipments_options_scheduled'} .= qq|<a href='/cgi-bin/mod/sales/admin?cmd=console_order&step=$step&activateshp=$i#tabs'>
													<img src='$va{'imgurl'}/$usr{'pref_style'}/checkmark.gif' title='Free Shipping' alt='Free Shipping' border='0'></a>|;
					}
				}
				if( !$orderShipment){
					$va{'shipments_options_scheduled'} .= &format_price($this_cost_scheduled).qq|</td>\n</tr>\n|;
				}else{
					$price_line = $cfg{$config_values_prices{$cses{'pay_type'}}{$cses{'shp_type'}}} / $cses{'items_in_basket'};
					$va{'shipments_options_scheduled'} .= qq|</td>\n</tr>\n|;
				}
			}
		}

		########
		######## Express Delivery allowed?
		########

		## FC-> Se valida configuracion en caso de existir sobrescribe precios de shipping, para cada tipo de envio.
		$va{'express_style'} = '' if $express_delivery_valid;
		if( !$orderShipment){

			$va{'shipments_options_standard'} .= qq|
							<tr  onmouseover='m_over(this)' onmouseout='m_out(this)'>
								<td class="smalltext" colspan=2 align='right' nowrap>Total Shp:</td>
								<td class="smalltext" align='right' nowrap>|.&format_price($tot_shpa_st).qq|</td>
							</tr>|;

			$va{'shipments_options_express'} .= qq|
							<tr  onmouseover='m_over(this)' onmouseout='m_out(this)'>
								<td class="smalltext" colspan=2 align='right' nowrap>Total Shp:</td>
								<td class="smalltext" align='right' nowrap>|.&format_price($tot_shpa_ex).qq|</td>
							</tr>|;				

			$va{'shipments_options_scheduled'} .= qq|
							<tr  onmouseover='m_over(this)' onmouseout='m_out(this)'>
								<td class="smalltext" colspan=2 align='right' nowrap>Total Shp:</td>
								<td class="smalltext" align='right' nowrap>|.&format_price($tot_shpa_sc).qq|</td>
							</tr>|;
		}else{

			$price = qq|
							<tr  onmouseover='m_over(this)' onmouseout='m_out(this)'>
								<td class="smalltext" colspan=2 align='right' nowrap>Total Shp:</td>
								<td class="smalltext" align='right' nowrap>|;

			$va{'shipments_options_standard'}.=$price.&format_price($cfg{$config_values_prices{$cses{'pay_type'}}{1}}).qq|</td>
							</tr>|;
			$va{'shipments_options_express'}.=$price.&format_price($cfg{$config_values_prices{$cses{'pay_type'}}{2}}).qq|</td>
							</tr>|;
			$va{'shipments_options_scheduled'}.=$price.&format_price($cfg{$config_values_prices{$cses{'pay_type'}}{3}}).qq|</td>
							</tr>|;
		
		}

		##<-FC
		#&save_callsession();

	}else{
		return "<td class='menu_bar' colspan='5'>".&trans_txt('empty_cart')."</td>";
	}
}


#############################################################################
#############################################################################
#   Function: display_points
#
#       Es: Muestra datos de los Puntos
#       En: show info for points on cc
#
#
#    Created on: 14/10/2015
#
#    Author: FC
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
sub display_points{
#############################################################################
#############################################################################
	$va{'used_points'} = &format_number($cses{'fppayment1'},2);
	$va{'url_diestel'} = "/cgi-bin/common/apps/ajaxbuild";
	$va{'autoget_points'} = $cfg{'autoget_points'};
	$va{'checked_use_points'} = 'false';
	my $val =length $in{'pmtfield5'};
	my $show = &Do_SQL("select if(count(*) > 0 , 'SI','NO') isSantander from sl_vars_config where command='diestel_points' and Code = '".substr($cses{'pmtfield3'},0,6)."'");
	my $res = $show->fetchrow_hashref();
	if($cfg{'use_points'} and $cfg{'use_points'} == 1 and $res->{'isSantander'} eq 'SI' and $val == 3){
		return &build_page("use_points.html");
	}else{
		return '';
	}
}


sub get_promo_prices{
#-----------------------------------------
# Created on: 07/09/09  12:37:37 By  Roberto Barcenas
# Forms Involved: 
# Description :
# Parameters :
# Last Modified by RB on 07/18/2011 12:32:20 PM : Se agrego Flexipago 

	my ($id_products_relid , $pnum, $this_pct, $this_method) = @_;

	(!$this_pct) and ($this_pct = 0);
	my $sp=0;$sp1=0;$sp2=0;$sp3=0;$sp4=0;$fpp=0;$mp=0;$dp=0,$fp=0;

	## Load Promo Count
	my ($sth) = &Do_SQL("SELECT TRIM(BOTH '|' FROM VValue) FROM sl_vars WHERE VName = 'promo".$id_products_relid."';");
	$cfg{'promo'.$id_products} = $sth->fetchrow;
	my @products = split(/\|/,$cfg{'promo'.$id_products});
	my $tproducts = scalar @products;


	if(!$pnum){

		my ($sth) = &Do_SQL("SELECT * FROM sl_products WHERE ID_products = '$id_products';");
		my ($rec) = $sth->fetchrow_hashref();

		if($this_method ne 'pct'){

			$sp = $rec->{'SPrice'}/$tproducts	if $rec->{'SPrice'} >=0;
			$sp1 = $rec->{'SPrice1'}/$tproducts if $rec->{'SPrice1'} >=0;
			$sp2 = $rec->{'SPrice2'}/$tproducts if $rec->{'SPrice2'} >=0;
			$sp3 = $rec->{'SPrice3'}/$tproducts if $rec->{'SPrice3'} >=0;
			$sp4 = $rec->{'SPrice4'}/$tproducts if $rec->{'SPrice4'} >=0;
			$fpp = $rec->{'FPPrice'}/$tproducts if $rec->{'FPPrice'} >=0;
			$mp = $rec->{'MemberPrice'}/$tproducts if $rec->{'MemberPrice'} >=0;
			$dp = $rec->{'Downpayment'}/$tproducts if $rec->{'Downpayment'} >=0;

		}else{

			$this_pct = $this_pct / 100 if $this_pct > 0;

			$sp = round($rec->{'SPrice'} * $this_pct,2) if $rec->{'SPrice'} >=0;
			$sp1 = round($rec->{'SPrice1'} * $this_pct,2) if $rec->{'SPrice1'} >=0;
			$sp2 = round($rec->{'SPrice2'} * $this_pct,2) if $rec->{'SPrice2'} >=0;
			$sp3 = round($rec->{'SPrice3'} * $this_pct,2) if $rec->{'SPrice3'} >=0;
			$sp4 = round($rec->{'SPrice4'} * $this_pct,2) if $rec->{'SPrice4'} >=0;
			$fpp = round($rec->{'FPPrice'} * $this_pct,2) if $rec->{'FPPrice'} >=0;
			$mp = round($rec->{'MemberPrice'} * $this_pct,2) if $rec->{'MemberPrice'} >=0;
			$dp = round($rec->{'Downpayment'} * $this_pct,2) if $rec->{'Downpayment'} >=0;

		}

		$pt = $rec->{'PayType'};
		$fp = $rec->{'Flexipago'};

	}else{	

		###############
		###############
		##### Cargado de Datos de tabla sl_products_prices
		###############
		################
		my ($sth) = &Do_SQL("SELECT Name, Price,Downpayment,FP, PayType FROM sl_products_prices WHERE ID_products_prices = '$pnum' AND ID_products = '$id_products_relid';");
		my ($m_name,$m_price,$m_dp,$m_fp,$m_pt) = $sth->fetchrow();

		if($m_fp) {

			if($this_method ne 'pct'){

				$sp = $m_price/$tproducts	if $m_price >=0;
				$sp1 = $m_price/$tproducts if $m_price >=0;
				$sp2 = $m_price/$tproducts if $m_price >=0;
				$sp3 = $m_price/$tproducts if $m_price >=0;
				$sp4 = $m_price/$tproducts if $m_price >=0;
				$fpp = $m_price/$tproducts if $m_fp >=0;
				$mp = $m_price/$tproducts if $m_price >=0;
				$dp = $m_dp/$tproducts if $m_dp >=0;

			}else{

				$this_pct = $this_pct / 100 if $this_pct > 0;

				$sp = round($m_price * $this_pct,2)	if $m_price >=0;
				$sp1 = round($m_price * $this_pct,2) if $m_price >=0;
				$sp2 = round($m_price * $this_pct,2) if $m_price >=0;
				$sp3 = round($m_price * $this_pct,2) if $m_price >=0;
				$sp4 = round($m_price * $this_pct,2) if $m_price >=0;
				$fpp = round($m_price * $this_pct,2) if $m_fp >=0;
				$mp = round($m_price * $this_pct,2) if $m_price >=0;
				$dp = round($m_dp * $this_pct,2) if $m_dp >=0;

			}
			
			$pt = $m_pt;
			$fp = $m_fp;	
			
		}

	}

	return ($sp,$sp1,$sp2,$sp3,$sp4,$fpp,$mp,$pt,$dp,$fp);

}


sub load_planning{
#-----------------------------------------
	my ($output, $rec);
	my (@c) = split(/,/,$cfg{'srcolors'});
	my ($sth) = &Do_SQL("SELECT * FROM sl_mediacontracts WHERE NOW()<=CONCAT(ESTDay,\" \",ESTTime) ORDER BY CONCAT(ESTDay,\" \",ESTTime) ASC LIMIT 10");
	while ($rec = $sth->fetchrow_hashref()){
		$d = 1 - $d;
		my ($sth2) = &Do_SQL("SELECT AVG(q) FROM (SELECT COUNT(*) AS q FROM `sl_mediacontracts` 
					LEFT JOIN sl_leads_calls ON sl_leads_calls.ID_mediacontracts=sl_mediacontracts.ID_mediacontracts
					WHERE `DestinationDID`=$rec->{'DestinationDID'}
					AND ESTDay BETWEEN  DATE_SUB(CURDATE() , INTERVAL 28 DAY) AND CURDATE() 
					AND Status='Transmitido' 
					GROUP BY sl_mediacontracts.ID_mediacontracts
					ORDER BY ESTDay DESC) AS tmp");
		$rec->{'calls'} = &format_number($sth2->fetchrow);
		$output .= qq|
			<tr  onmouseover='m_over(this)' onmouseout='m_out(this)' bgcolor='$c[$d]' onClick="trjump('/cgi-bin/mod/sales/admin?cmd=console_order&step=2&action=search&filter=proghoy&ID_mediacontracts=$rec->{'ID_mediacontracts'}')">
				<td>$rec->{'ESTDay'} \@ $rec->{'ESTTime'}</td>
				<td>$rec->{'Offer'}</td>
				<td>$rec->{'DMA'}</td>
				<td align='center'>$rec->{'DestinationDID'}</td>
				<td align='center'>$rec->{'calls'}</td>
			</tr>|;
	}
	if (!$output){
		$output = "
			<tr>
				<td colspan='5' align='center'>".&trans_txt('search_nomatches')."</td>
			</tr>";
	}
	return $output;
}

sub famprodlist{
#-----------------------------------------
	my (@files,$file,$output,$fname,$n);
	opendir (IMGDIR, "$cfg{'path_imgman'}prodfam") || &cgierr("Unable to open directory $cfg{'path_imgman'}prodfam",704,$!);
		@files = readdir(IMGDIR);		# Read in list of files in directory..
	closedir (IMGDIR);
	FILE: foreach $file (@files) {
		next if ($file =~ /^\./);		# Skip "." and ".." entries..
		next if ($file =~ /^index/);		# Skip index.htm type files..
		$file =~ /(\w+)\./;
		$output .= qq|<input class="radio" type="image" src="$cfg{'path_imgman_url'}prodfam/$file" name="prodfam.$1" value="$1" border="0">|;
		++$n;
		if ($n>6){
			$n=0;
			$output .= "<br>";
		}
	}
	return $output;
}

sub showprodfam{
#-----------------------------------------
	if ($cses{'prodfam'}){
		return qq|
			<a href="/cgi-bin/mod/sales/admin?cmd=console_order&step=2&action=search&name=$cses{'prodfam'}">
			<img src="$cfg{'path_imgman_url'}prodfam/$cses{'prodfam'}.jpg" border="0">
			</a>|;
	}
	return $cses{'prodfam'}
}

sub parts_more_info{
	$va{'parts_more_info'} = '';

	my $sql = "SELECT REPLACE(VValue, '|',',') FROM sl_vars WHERE VName ='promo$in{'id_products'}';";
	my ($sth) = &Do_SQL($sql);
	my $promo = $sth->fetchrow_array();
	$promo =~ s/^,//;

	my ($id_products);
	if ($promo){
		$sql = "SELECT group_concat(ID_products)ID_products FROM sl_products WHERE ID_products IN ($promo);";
		($sth) = &Do_SQL($sql);
		$id_products = $sth->fetchrow_array();
	}

	$in{'id_products'} = $id_products if ($promo and $id_products);

	$sql = "SELECT
		sl_skus_parts.ID_sku_products as ID_products
		, sl_skus_parts.id_skus_parts
		, sl_skus_parts.ID_parts
		, (sl_skus_parts.ID_parts+400000000) as SKU
		, sl_skus_parts.Qty
		, sl_parts.Model Name
		, sl_skus.Status
	FROM sl_products 
	INNER JOIN sl_skus ON sl_products.ID_products=sl_skus.ID_products AND sl_skus.Status='Active'
	INNER JOIN sl_skus_parts ON sl_skus_parts.ID_sku_products=sl_skus.ID_sku_products
	INNER JOIN sl_parts ON sl_skus_parts.ID_parts=sl_parts.ID_parts
	WHERE 1 AND sl_products.ID_products IN ($in{'id_products'})
	GROUP BY sl_skus_parts.ID_skus_parts 
	ORDER BY sl_skus_parts.ID_skus_parts ASC;";

	my ($sth) = &Do_SQL($sql);
	while ($rec = $sth->fetchrow_hashref()){		
		$va{'parts_more_info'} .= qq|<a href="/cgi-bin/common/apps/ajaxbuild?ajaxbuild=mer_parts_tecs_specs&id_parts=|.$rec->{'ID_parts'}.qq|" title="$rec->{'Name'}" class="fancy_modal_iframe"><img src="/intranet/images/ico3.png" style="vertical-align:middle;" border=0> $rec->{'Name'}</a><br>|;
	}

	return &build_page("parts_more_info.html");	
}

sub console_productinfo{
#-----------------------------------------
	(!$in{'tab'}) and ($in{'tab'}=1);

	return &build_page("console_productinfo".$in{'tab'}.".html");
}

sub console_extraslinks{
#-----------------------------------------
	(!$in{'tab'}) and ($in{'tab'}=1);
	$in{'nh'} ? ($nh = $in{'nh'}) : ($nh = 1);
	$first = ($usr{'pref_maxh'} * ($nh - 1));
		
	if ($in{'tab'} eq 1){
		##############################################
		## tab1 : RELACIONADOS
		##############################################
		#&load_callsession();
		my ($query);
		if ($cses{'items_in_basket'} > 0){
			my $j=0;
			$ids[$j]=0;
			for my $i(1..$cses{'items_in_basket'})	{
				if ($cses{'items_'.$i.'_qty'}>0 and $cses{'items_'.$i.'_id'}>0)	{
					$ids[$j]=substr($cses{'items_'.$i.'_id'},3,6);
					$j++;
				}
			}
			
			$insql=join(",", @ids);
			#GV Modificación Inicia 21abr2008 Se comenta lo relacionado a Non-Inventory
	#					union
	#					SELECT concat('50000',sl_noninv.ID_noninv) as ID_products, Name, Model, Price as Price, 'ni' as type
	#					FROM sl_noninv_related inner join sl_noninv on (sl_noninv.ID_noninv=sl_noninv_related.ID_noninv) WHERE sl_noninv_related.Status='Active' and sl_noninv.Status='Active' and sl_noninv_related.ID_products in (".$insql.")					
			$sth= &Do_SQL("SELECT concat('100',ID_products_options) as ID_products, sl_products_related.ID_products as relid, Name, Model, SPrice as Price, '' as type
			FROM sl_products_related inner join sl_products on (sl_products.ID_products=ID_products_options) WHERE sl_products_related.Status='Active' and sl_products.Status NOT IN('Testing','Inactive') and sl_products_related.ID_products in (".$insql.")
			LIMIT $first,$usr{'pref_maxh'}");
			#GV Modificación Termina 21abr2008 Se comenta lo relacionado a Non-Inventory
			$va{'matches'}=$sth->rows;
			while ($rec = $sth->fetchrow_hashref){
				$relid = "100".$rec->{'relid'};
				#RB Start 04/15/08 - Add a link to view the related product (lines 60,61,69)
				($rec->{'type'} ne 'ni') and ($link = '<a href="/cgi-bin/mod/sales/admin?cmd=console_order&id_products='.substr($rec->{'ID_products'},3).'&action=search&step=2"><img src="[va_imgurl]/[ur_pref_style]/b_view.gif" title="View" alt="" border="0"></a>');
				($rec->{'type'} eq 'ni') and ($link = '&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;');
				#RB End
				my (@c) = split(/,/,$cfg{'srcolors'});
				my ($sthk) = &Do_SQL("SELECT * FROM sl_skus WHERE ID_sku_products='$rec->{'ID_products'}' and Status='Active'");
				$reck = $sthk->fetchrow_hashref;
				$choices = &load_choices('-',$reck->{'choice1'},$reck->{'choice2'},$reck->{'choice3'},$reck->{'choice4'});
				$d = 1 - $d;
				$cadimages=&show_image_in_page($rec->{'ID_products'})."<br>";
				$cadimages=""if($cadimages=~/No hay images/);
				$va{'searchresults'} .="<tr onmouseover='m_over(this)' onmouseout='m_out(this)' bgcolor='$c[$d]' onclick=\"trjump('/cgi-bin/mod/sales/admin?cmd=console_order&step=8&tab=1&addrelprod".$rec->{'type'}."=1&relid=".$relid."&id_sku_products=".$rec->{'ID_products'}."')\">
																	<td>$link $cadimages".&format_sltvid($rec->{'ID_products'})."</td>
																	<td>".$rec->{'Name'}." ".$rec->{'Model'}."$choices</td>
																	<td>\$".$rec->{'Price'}."</td>
																</tr>";
			}
		}
		($va{'pageslist'},$va{'qs'})  = &pages_list($in{'nh'},"$script_url",$va{'matches'},$usr{'pref_maxh'});
		if($va{'matches'}==0){
			$va{'searchresults'} = qq|
			<tr>
				<td colspan='7' align='center'>|.&trans_txt('search_nomatches').qq| &nbsp;</td>
			</tr>\n|;
		}
	}elsif($in{'tab'} eq 2){
		##############################################
		## tab2 : Sugeridos
		##############################################
		my ($query);
		my (@c) = split(/,/,$cfg{'srcolors'});
		$sth= &Do_SQL("SELECT count(*) FROM sl_products WHERE Status = 'Up Sell'");
		$va{'matches'}=$sth->fetchrow;
		$sth= &Do_SQL("SELECT *  FROM sl_products WHERE Status = 'Up Sell' LIMIT $first,$usr{'pref_maxh'}");
		#$va{'matches'}=$sth->rows;
		($va{'pageslist'},$va{'qs'})  = &pages_list($in{'nh'},"$script_url",$va{'matches'},$usr{'pref_maxh'});
		if(!$va{'matches'})	{
			$va{'searchresults'} = qq|
			<tr>
				<td colspan='7' align='center'>|.&trans_txt('search_nomatches').qq|</td>
			</tr>\n|;
		}
		while ($rec = $sth->fetchrow_hashref)	{
			my ($sthk) = &Do_SQL("SELECT * FROM sl_skus WHERE ID_sku_products='$rec->{'ID_products'}' and Status='Active'");
			$reck = $sthk->fetchrow_hashref;
			$choices = &load_choices('-',$reck->{'choice1'},$reck->{'choice2'},$reck->{'choice3'},$reck->{'choice4'});
			$d = 1 - $d;
			$cadimages=&show_image_in_page($rec->{'ID_products'})."<br>";
			$cadimages=""if($cadimages=~/No hay images/);
			$va{'searchresults'} .="<tr onmouseover='m_over(this)' onmouseout='m_out(this)' bgcolor='$c[$d]' onclick=\"trjump('/cgi-bin/mod/sales/admin?cmd=console_order&step=8&tab=2&addrelprod=1&relid=-1&id_sku_products=100".$rec->{'ID_products'}."')\">
																<td>$cadimages".&format_sltvid('100'.$rec->{'ID_products'})."</td>
																<td>".$rec->{'Name'}."$choices</td>
																<td>\$".$rec->{'SPrice'}."</td>
															</tr>";
		}
	}elsif($in{'tab'} eq 3){
		##############################################
		## tab3 : Especiales
		##############################################
		my ($query);
		my (@c) = split(/,/,$cfg{'srcolors'});
		$sth= &Do_SQL("SELECT COUNT(*) FROM sl_products WHERE IsFinal='Yes'");
		$va{'matches'}=$sth->fetchrow;
		$sth= &Do_SQL("SELECT * FROM sl_products WHERE IsFinal='Yes' LIMIT $first,$usr{'pref_maxh'}");
		#$va{'matches'}=$sth->rows;
		($va{'pageslist'},$va{'qs'})  = &pages_list($in{'nh'},"$script_url",$va{'matches'},$usr{'pref_maxh'});
		if(!$va{'matches'})	{
			$va{'searchresults'} = qq|
			<tr>
				<td colspan='7' align='center'>|.&trans_txt('search_nomatches').qq|</td>
			</tr>\n|;
		}
		while ($rec = $sth->fetchrow_hashref)	{
			my ($sthk) = &Do_SQL("SELECT * FROM sl_skus WHERE ID_sku_products='$rec->{'ID_products'}' and Status='Active'");
			$reck = $sthk->fetchrow_hashref;
			$choices = &load_choices('-',$reck->{'choice1'},$reck->{'choice2'},$reck->{'choice3'},$reck->{'choice4'});
			$d = 1 - $d;
			$cadimages=&show_image_in_page($rec->{'ID_products'})."<br>";
			$cadimages=""if($cadimages=~/No hay images/);
			$va{'searchresults'} .="<tr onmouseover='m_over(this)' onmouseout='m_out(this)' bgcolor='$c[$d]' onclick=\"trjump('/cgi-bin/mod/sales/admin?cmd=console_order&step=8&tab=3&addrelprod=1&id_sku_products=100".$rec->{'ID_products'}."')\">
																<td>$cadimages".&format_sltvid('100'.$rec->{'ID_products'})."</td>
																<td>".$rec->{'Name'}."$choices</td>
																<td>\$".$rec->{'SPrice'}."</td>
															</tr>";
		}

	}elsif($in{'tab'} eq 4){
		##############################################
		## tab4 : Servicios
		##############################################
		$in{'op'}=int($in{'op'});
		my (@c) = split(/,/,$cfg{'srcolors'});
		#GV Modifica 21abr2008 Se cambia sl_services por sl_services
		my ($sth) = &Do_SQL("SELECT COUNT(*) FROM sl_services WHERE Status='Active'");
		$va{'matches'}=$sth->fetchrow;
		#($va{'pageslist'},$va{'qs'})  = &pages_list($in{'nh'},"$script_url",$va{'matches'},$usr{'pref_maxh'});
		if ($va{'matches'}>0){#GV Modifica 21abr2008 Se cambia sl_services por sl_services #GV Modifica 21abr2008 Se cambia ID_services por ID_services
			my ($sth) = &Do_SQL("SELECT concat('60000',ID_services) as ID_services,Name,Description,SPrice,SalesPrice,Status,ServiceType,Tax FROM sl_services WHERE Status = \'Active\' ORDER BY ID_services DESC /*LIMIT $first,$usr{'pref_maxh'}*/");
			while ($rec = $sth->fetchrow_hashref){
				$d = 1 - $d;
				$rec->{'Comments'} =~ s/\n/<br>/g;#GV Modifica 21abr2008 Se cambia ID_services por ID_services
				$va{'searchresults'} .= "<tr onmouseover='m_over(this)' onmouseout='m_out(this)' bgcolor='$c[$d]' onclick=\"trjump('/cgi-bin/mod/sales/admin?cmd=console_order&step=8&tab=4&ser=1&id_services=$rec->{'ID_services'}')\">\n";						
#						$va{'searchresults'} .= "  <td class='smalltext'><a href='$script_url?cmd=console_order&step=8&ser=1&id_services=$rec->{'ID_services'}'><img src='$va{'imgurl'}/$usr{'pref_style'}/b_add.gif' title='Add' alt='' border='0'></a></td>\n";					
				$va{'searchresults'} .= "   <td class='smalltext' valign='top' nowrap>".&format_sltvid($rec->{'ID_services'})."</td>\n";						
				$va{'searchresults'} .= "   <td class='smalltext' valign='top'>$rec->{'Name'}<BR>$rec->{'Description'}</td>\n";
				$va{'searchresults'} .= "   <td class='smalltext' valign='top'>$rec->{'ServiceType'}</td>\n";		
					if($rec->{'SalesPrice'} eq 'Fixed'){
					$total_sp = $rec->{'SPrice'} ;
					$va{'searchresults'} .= "   <td class='smalltext' align='right' nowrap valign='top'>".&format_price($total_sp)."</td>\n";
			  	}else{
			  		$total_sp = $cses{'total_i'} * ($rec->{'SPrice'}/100);
			 		$va{'searchresults'} .= "   <td class='smalltext' align='right' nowrap valign='top'>".&format_price($total_sp)."</td>\n";
				}										
				$va{'searchresults'} .= "   <td class='smalltext' valign='top'>$rec->{'Tax'}</td>\n";													
				$va{'searchresults'} .= "</tr>\n"; 
		  }	
		  $cses{'ser'} = $in{'ser'};				
		  #GV Modifica 21abr2008 Se cambia id_services por id_services	
		  $cses{'id_services'} = $in{'id_services'};					
		}else{
			$va{'searchresults'} = qq|
			<tr>
				<td colspan='7' align='center'>|.&trans_txt('search_nomatches').qq|</td>
			</tr>\n|;
		}	
		$va{'serlist'}=$va{'searchresults'};
	
	}
	return &build_page("console_extraslinks".$in{'tab'}.".html");
}

#############################################################################
#############################################################################
#   Function: match_totals
#
#       Es: Iguala el total del pedido con el del pago
#       En: Match the total order
#
#
#    Created on: 24/10/2013 11:00
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
sub match_totals{
#############################################################################
#############################################################################
	my ($id_orders) = @_;
	my ($payments,$total_payment,$total_order);
	if ($id_orders > 0){
		$sql="SELECT 
			(SELECT COUNT(*) FROM sl_orders_payments WHERE sl_orders_payments.Status NOT IN ('Cancelled','Void') AND sl_orders_payments.ID_orders='$id_orders')
			,(SELECT SUM(sl_orders_payments.Amount) FROM sl_orders_payments WHERE sl_orders_payments.Status NOT IN ('Cancelled','Void') AND sl_orders_payments.ID_orders='$id_orders')Payment
			,SUM(sl_orders_products.SalePrice - sl_orders_products.Discount + sl_orders_products.Tax + sl_orders_products.Shipping + sl_orders_products.ShpTax)Total FROM sl_orders_products  WHERE  Status NOT IN('Order Cancelled', 'Inactive') AND ID_orders='$id_orders';";
		$sth = &Do_SQL($sql);
		($payments, $total_payment, $total_order) = $sth->fetchrow_array();
		
		if ($total_payment != $total_order and $payments == 1){
			&Do_SQL("UPDATE sl_orders_payments SET Amount='$total_order' WHERE ID_orders='$id_orders' LIMIT 1");
		}
	}

	return $total_order;
}

1;