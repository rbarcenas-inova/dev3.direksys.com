#!/usr/bin/perl
##################################################################
############      CONSOLE STEP 2 : PRODUCT INFO
##################################################################
# Last Modified on: 12/17/08 12:54:39
# Last Modified by: MCC C. Gabriel Varela S: Se toma en cuenta membresía
# Last Modified on: 05/12/09 15:42:32
# Last Modified by: MCC C. Gabriel Varela S: Se agrega variable para determinar si existe membresía en la orden
# Last Modified on: 05/14/09 12:18:30
# Last Modified by: MCC C. Gabriel Varela S: Agregar rel id para productos de promoción.
# Last Modified RB: 07/08/09  17:11:52 -- Se soluciona problema de promo 2x1 cuando ambos productos son el mismo
# Last Modified RB: 07/09/09  19:52:49 -- Se pasa el $in{'pricenumber'} a los productos con choice para aplicar el multiprice
# Last Modified on: 07/10/09 09:50:30
# Last Modified by: MCC C. Gabriel Varela S, Lic. Roberto Bárcenas: Se arregla cuestión de pnum para productos con choices.
# Last Modified RB: 09/08/09  18:09:10 -- Se agrega sesion $cses{'downsale_authcode'} para registrar una nota al final de la venta de quien autorizo el downsale del producto
# Last Modified RB: 10/09/09  17:03:31 -- SE agrega sesion $cses{'items_'.'$i.'_promo} para sacar shipping y paytype del producto virtual en la promo
# Last Modified RB: 11/30/09  17:51:30 -- Se acepta agregar productos en Backorder
# Last Modified on: 04/12/11 06:14:22 PM
# Last Modified by: MCC C. Gabriel Varela S: Se hace que no se borren productos de más, se corrige condición de _relid. También se hace que se reestablezca bandera de secret_cupon en caso de borrar el producto de secret_cupon
# Last Modified RB: 11/08/2011  17:51:30 -- Se agrega overwrite de precios por configuracion(setup.cfg)
# Last Modified RB: 11/09/2011  19:51:30 -- Se agrega pricetype(net/gross) al producto para calculo de precio
	
	$va{'speechname'}= 'ccinbound:2- Product Search';
	
	## Zip Selected for Pay Type
	$cses{'zipcode_selected'} = $in{'zipcode'} if($in{'zipcode'});

	my $x=0;
	for my $i(1..$cses{'items_in_basket'}){
		if ($cses{'items_'.$i.'_qty'} > 0 and $cses{'items_'.$i.'_id'} > 0){
			++$x;
		}
	}
	(!$x and $cses{'paytype_available'}) and (delete($cses{'paytype_available'})) and (delete($cses{'paytype_order'}));

	if ($in{'id_customers'} ne ""){
		$cses{'id_customers'} = $in{'id_customers'};
	}
	
	## Load data from CDR/Flash
	$cses{'cid'} = $in{'cid'} if ($in{'cid'});
	$cses{'did'} = $in{'did'} if ($in{'did'});
	$cses{'dnis'} = $in{'did'} if ($in{'did'});
	
	if ($in{'updates7'}){
		$cses{'dids7'} = $in{'dids7'};
		$cses{'updates7'} = 1;
	}


	my($sth);		
	if ($in{'end'}){

		&console;
		return;

	}elsif($in{'drop'}){
		
		###############################################
		###############################################
		###############################################
		############
		############ 1) Drop From Basket
		############
		###############################################
		###############################################
		###############################################

		for my $i(1..$cses{'items_in_basket'}){
        	if ($cses{'items_'.$i.'_qty'}>0 and $cses{'items_'.$i.'_id'}>0){
        		#Verifica si tiene producto ligado
        		if(($cses{'items_'.$in{'drop'}.'_id'}!=$cses{'items_'.$i.'_id'})and($cses{'items_'.$in{'drop'}.'_relid'}==$cses{'items_'.$i.'_relid'}) and ($cses{'items_'.$i.'_relid'}ne'')){
        			#Recorre los servicios
			        for my $j(1..$cses{'servis_in_basket'}){
			            if ($cses{'servis_'.$j.'_qty'}>0 and $cses{'servis_'.$j.'_id'}>0){
			                #Verifica si tiene servicio ligado
			                if($cses{'items_'.$i.'_id'}==$cses{'servis_'.$j.'_relid'} || $cses{'servis_'.$j.'_id'} eq "60000".$cfg{'duties'} || $cses{'servis_'.$j.'_id'} eq "60000".$cfg{'insurance'}){ #RB Modify
								delete($cses{'servis_dut'});
								delete($cses{'servis_ins'});
			                    delete($cses{'servis_'.$j.'_id'});
			                    delete($cses{'servis_'.$j.'_qty'});
			                    delete($cses{'servis_'.$j.'_ser'});
			                    delete($cses{'servis_'.$j.'_relid'});
			                    delete($cses{'servis_'.$j.'_desc'});
			                    delete($cses{'servis_'.$j.'_fpago'});
			                    delete($cses{'servis_'.$j.'_payments'});
			                    delete($cses{'servis_'.$j.'_price'});
			                    delete($cses{'servis_'.$j.'_discount'});
			                    delete($cses{'servis_'.$j.'_shp1'});
			                    delete($cses{'servis_'.$j.'_shp2'});
			                    delete($cses{'servis_'.$j.'_tax'});
			                }
			            }
			        }

					delete($cses{'items_'.$i.'_desc'});
			        delete($cses{'items_'.$i.'_downpayment'});
			        delete($cses{'items_'.$i.'_id'});
			        delete($cses{'items_'.$i.'_duties'});
					delete($cses{'items_'.$i.'_fpprice'});
					delete($cses{'items_'.$i.'_insurance'});
					delete($cses{'items_'.$i.'_msprice'});
        			delete($cses{'items_'.$i.'_price'});
			        delete($cses{'items_'.$i.'_qty'});
			        delete($cses{'items_'.$i.'_fpago'});
			        delete($cses{'items_'.$i.'_payments'});
			        delete($cses{'items_'.$i.'_discount'});
			        delete($cses{'items_'.$i.'_tax'});

			        ### Fix Sales GQ
			        if( $cses{'items_total'} > 0 ){
			        	--$cses{'items_total'};
			        }
        		}
        	}
        }

        ### Fix Sales GQ
        if( $cses{'items_total'} > 0 ){
        	--$cses{'items_total'};
        }
        
        
        delete($cses{'items_'.$in{'drop'}.'_desc'});
        delete($cses{'items_'.$in{'drop'}.'_downpayment'});
        delete($cses{'items_'.$in{'drop'}.'_id'});
        delete($cses{'items_'.$in{'drop'}.'_duties'});
		delete($cses{'items_'.$in{'drop'}.'_fpprice'});
		delete($cses{'items_'.$in{'drop'}.'_insurance'});
		delete($cses{'items_'.$in{'drop'}.'_msprice'});
  		delete($cses{'items_'.$in{'drop'}.'_price'});
        delete($cses{'items_'.$in{'drop'}.'_qty'});
        delete($cses{'items_'.$in{'drop'}.'_fpago'});
        delete($cses{'items_'.$in{'drop'}.'_payments'});
        delete($cses{'items_'.$in{'drop'}.'_discount'});
        delete($cses{'items_'.$in{'drop'}.'_tax'});
        delete($cses{'items_'.$in{'drop'}.'_expressshipping'});
        while( my($key, $value) = each %cses){
			if($key =~ m/_shipping/ or $key =~ m/shipping_/  or $key =~ m/shipping/ or $key =~ m/shp_/ or $key =~ m/_shp/){
				delete($cses{$key});
			}
			if($key =~ m/items_$in{'drop'}/){
				delete($cses{$key});
			}
		}
		while( my($key, $value) = each %in){
			if($key =~ m/_shipping/ or $key =~ m/shipping_/  or $key =~ m/shipping/ or $key =~ m/shp_/ or $key =~ m/_shp/){
				delete($in{$key});
			}
			if($key =~ m/items_$in{'drop'}_/){
				delete($cses{$key});
			}
		}
		while( my($key, $value) = each %va){
			if($key =~ m/_shipping/ or $key =~ m/shipping_/  or $key =~ m/shipping/ or $key =~ m/shp_/ or $key =~ m/_shp/){
				delete($va{$key});
			}
			if($key =~ m/items_/){
				delete($cses{$key});
			}
		}
		

        if($in{'drop'}==$cses{'secret_cupon_item'}){
	        delete($cses{'items_'.$in{'drop'}.'_secret_cupon'});
	        delete($cses{'secret_cupon_applied'});
	        delete($cses{'secret_cupon_item'});
	        delete($cses{'cupon_id_products'});
        }
        
        ### Fix Sales GQ
		if( $cses{'items_total'} == 0 ){
		 	$cses{'pay_type'} = '';
		}

        &save_callsession();
		
	}elsif($in{'action'} eq 'add_to_basket'){

		###############################################
		###############################################
		###############################################
		############
		############ 2) Add To BAsket
		############
		###############################################
		###############################################
		###############################################


		my @ids_products;
		if($in{'id_products'} =~ m/\|/) {
			@ids_products = split(/\|/,$in{'id_products'});
		}
		
		if($#ids_products == -1) {
			$ids_products[0] = $in{'id_products'};
		}

		for (0..$#ids_products){

			$in{'id_products'} = $ids_products[$_];
			if(int($in{'id_products'})>0) {
				
				#Inicia Se agrega servicio de membresía
				if($in{'add_membership'}==1){
					++$cses{'servis_in_basket'};
					$in{'id_services'}=600000000+$cfg{'membershipservid'};
					$cses{'servis_'.$cses{'servis_in_basket'}.'_id'} = $in{'id_services'};
					$cses{'servis_'.$cses{'servis_in_basket'}.'_discount'} = 0;
					$cses{'servis_'.$cses{'servis_in_basket'}.'_fpago'} = 1;
					$cses{'servis_'.$cses{'servis_in_basket'}.'_payments'} = 1;
					$cses{'servis_'.$cses{'servis_in_basket'}.'_qty'} = 1;
					$cses{'servis_'.$cses{'servis_in_basket'}.'_ser'} = 1;
					$price=&load_name ('sl_services','ID_services',substr($in{'id_services'},5,4),'SPrice');
					$cses{'servis_'.$cses{'servis_in_basket'}.'_price'} = $price;
					$cses{'type'} = "Membership";
					$cses{'membershipinorder'} = "1";
				}
				#Termina Se agrega servicio de membresía
				if($in{'add_warranty'}==1){
					$cses{'apply_warranty'}=1;
					&save_callsession();
					&service_bydefault();
					&save_callsession();
				}elsif($in{'authcode_downsale'}){
					$cses{'authcode_downsale'} = $in{'authcode_downsale'};
					&save_callsession();
				}
				
				if($in{'skupro'}){

					#########################
					#########################
					###### Add Product
					#########################
					#########################

					###########
					###########
					#### MultiPrice Validation
					###########
					###########
					my $valid = 1;my $res_auth = 0;
					if ($in{'pricenumber2'}) {

						if(!$cfg{'multiprice'}){

							$valid = 0;
							print "Content-type: text/html\n\n";
							print "<script>window.location.href = 'admin?cmd=console_order&step=2&id_products=$in{'id_products'}&action=search&err=1';</script>";

						}else{

							#### Pricenumber2 Tiene el valor de sl_products_prices.ID_products_prices
							my $rauth = &load_name('sl_products_prices','ID_products_prices', $in{'pricenumber2'}, 'AuthCode');
							if($rauth eq 'Yes'){

								$res_auth = $rauth eq 'Yes' ? &passdownsale($in{'authcode'}) : -1;
								if($res_auth == -1){
									$valid = 0;
									print "Content-type: text/html\n\n";
									print "<script>window.location.href = 'admin?cmd=console_order&step=2&id_products=$in{'id_products'}&action=search&err=2';</script>";
								}

							}

						}
						$in{'pricenumber'} = $in{'pricenumber2'};

					}

					#&cgierr("valid: $valid - $res_auth -- $in{'pricenumber'} = $in{'pricenumber2'}");
					if($valid) {

						#############
						#############
						##### Valid Means No Need for AuthCode or AutChode OK
						#############
						#############
							
						&get_shipping_data();
						$cses{'pricetype'}=$in{'pricetype'} if $in{'pricetype'};

						if($in{'sk_op'}){

							++$cses{'items_in_basket'};
							### Fix Sales GQ
							++$cses{'items_total'};

							$in{'id_prod'}=$in{'id_products'};
							$cses{'items_'.$cses{'items_in_basket'}.'_id'} = $in{'id_sku_products'};
							$cses{'items_'.$cses{'items_in_basket'}.'_qty'} = 1;

							if ($cfg{'multiprice'}){
								$cses{'items_'.$cses{'items_in_basket'}.'_pnum'} = $in{'pricenumber'};
								$cses{'items_'.$cses{'items_in_basket'}.'_authcode'} = $res_auth;
							}

							#####
							#####  Creacion de variables  paytype_available y fp_available
							#####
							&paytype_fp_available();

						}else{
							$in{'id_prod'}=$in{'id_products'};
							# &cgierr($in{'id_prod'}.'->else->'.$in{'pricenumber'});
							delete($va{'msg_sku'});


							if($in{'choice1'} or $in{'choice2'} or $in{'choice3'} or $in{'choice4'}){

								#################
								#################
								###### Choice
								#################
								#################

								my ($query,$strc);
								for (1..4){
									if ($in{'choice'.$_}){
										$query .= " AND choice$_='$in{'choice'.$_}'";
										$strt .= $in{'choice'.$_} . ',';
									}
								}
								chop($strt);

								$sth = &Do_SQL("SELECT COUNT(*) FROM sl_skus WHERE ID_products='$in{'id_prod'}' $query AND Status != 'Inactive'");
								if ($sth->fetchrow()>0){
								
									$sth = &Do_SQL("SELECT * FROM sl_skus WHERE ID_products='$in{'id_prod'}' $query AND Status != 'Inactive'");
									$rec = $sth->fetchrow_hashref;

									#####
									##### Validacion Oferta / Precio
									#####
									my ($sthp) = &Do_SQL("SELECT Price,IF(ValidKits IS NULL OR ValidKits = '' OR ValidKits LIKE '%$rec->{'ID_sku_products'}%',1,0) AS ValidPrice 
										FROM sl_products_prices WHERE ID_products_prices = '$in{'pricenumber'}' AND ID_products = '$in{'id_prod'}';");
									my ($this_price,$valid_price) = $sthp->fetchrow();

									if($valid_price){

										($rec->{'Status'} eq 'Backorder')	and ($va{'msg_backorder'}	=	'<tr><td colspan="4" align="center" class="stdtxterr">El Producto agregado esta en Backorder</td></tr>');
										++$cses{'items_in_basket'};	
										### Fix Sales GQ
										++$cses{'items_total'};		
										$cses{'items_'.$cses{'items_in_basket'}.'_id'} = $rec->{'ID_sku_products'};
										$cses{'items_'.$cses{'items_in_basket'}.'_qty'} = 1;
										$cses{'items_'.$cses{'items_in_basket'}.'_express_delivery'} = &load_name('sl_products','ID_products',substr($in{'id_prod'},-6),'ExpressShipping');

										if ($cfg{'multiprice'}){
											$cses{'items_'.$cses{'items_in_basket'}.'_pnum'} = $in{'pricenumber'};
										}  
									
										#####
										#####  Creacion de variables  paytype_available y fp_available
										#####
										&paytype_fp_available();

										}else{

											$va{'msg_sku'} = 2;
											$va{'choice_name'} = $strt;
											$va{'choice_price'} = $this_price;

										}

								}else{
									$sth = &Do_SQL("SELECT COUNT(*) FROM sl_skus WHERE ID_products='$in{'id_prod'}'");
									if ($sth->fetchrow()>0){
										$va{'msg_sku'} = 1;	
									}
								}

							}else{

								## Load Promo
								#my ($sth) = &Do_SQL("SELECT TRIM(BOTH '|' FROM VValue)FROM sl_vars WHERE VName='promo$in{'id_prod'}';");
								my $sth = &Do_SQL("SELECT 
									(SELECT TRIM( BOTH '|' FROM VValue ) FROM sl_vars WHERE sl_vars.VName = 'promo$in{'id_prod'}') AS ID_products
									, (SELECT TRIM( BOTH '|' FROM VValue ) FROM sl_vars WHERE sl_vars.VName = 'percent_promo$in{'id_prod'}') AS Percents");
								my ($promo,$percents) = $sth->fetchrow;
								#$cfg{'promo'.$in{'id_prod'}} = $sth->fetchrow;
								$cfg{'promo'.$in{'id_prod'}} = $promo;

								if ($cfg{'promo'.$in{'id_prod'}}){

									#################
									#################
									###### Promos (2x1, 3x2 etc)
									#################
									#################

									$va{'msg_sku'} =1; my $is_pct = 0;
									my (@products) = split(/\|/,$promo);
									my (@arypercents) = split(/\|/,$percents);
									if (scalar @arypercents > 0 and scalar @arypercents == scalar @products){ $is_pct = 1; }

									my $promo_pct_total = 0; my $actual_basket = $cses{'items_in_basket'} +1;
									for (0..$#products){

										#######
										####### Promo could be in the format of idpromo:price_percentage
										#######
										my $this_idp = int($products[$_]); my $this_pct = $is_pct ? @arypercents[$_] : 0;
										(!$this_pct) and ($this_pct = 0);
										$this_idp = int($this_idp); $promo_pct_total += round($this_pct,2);

										if ($in{'idp'.$this_idp.($_+1)}){

											++$cses{'items_in_basket'};
											### Fix Sales GQ
											++$cses{'items_total'};
											$cses{'items_'.$cses{'items_in_basket'}.'_promo'} = $in{'id_prod'}+ 100000000;
											$cses{'items_'.$cses{'items_in_basket'}.'_id'} = $in{'idp'.$this_idp.($_+1)};
											$cses{'items_'.$cses{'items_in_basket'}.'_qty'} = 1;
											$cses{'items_'.$cses{'items_in_basket'}.'_relid'} = $in{'id_prod'};
											$cses{'items_'.$cses{'items_in_basket'}.'_pnum'} = $in{'pricenumber'}if ($cfg{'multiprice'});
											$cses{'items_'.$cses{'items_in_basket'}.'_promopct'} = $this_pct;
											$cses{'items_'.$cses{'items_in_basket'}.'_promocal'} = $is_pct ? 'pct' : 'tot';
											$cses{'items_'.$cses{'items_in_basket'}.'_express_delivery'} = &load_name('sl_products','ID_products',substr($in{'id_prod'},-6),'ExpressShipping');
											delete($va{'msg_sku'});

											#####
											#####  Creacion de variables  paytype_available y fp_available
											#####
											&paytype_fp_available();

										}
									}

									###### Promo Pct Validation (Must be equal to 100 to be valid)
									if($promo_pct_total > 0 and abs($promo_pct_total - 100) > 0){
										for ($actual_basket..$cses{'items_in_basket'}) { $cses{'items_'.$_.'_promopct'} = 0; $cses{'items_'.$_.'_promocal'} = 'tot'; }
									}

								}else{

									#################
									#################
									###### Regular Product
									#################
									#################

								  	$sth = &Do_SQL("SELECT COUNT(*) FROM sl_skus WHERE ID_products=$in{'id_prod'} AND Status !='Inactive' ");									 
								  	if ($sth->fetchrow == 1){
								  		my ($sth) = &Do_SQL("SELECT * FROM sl_skus WHERE ID_products=$in{'id_prod'} AND Status !='Inactive' ");	
									  	$rec = $sth->fetchrow_hashref;
									  	($rec->{'Status'} eq 'Backorder')	and ($va{'msg_backorder'}	=	'<tr><td colspan="4" align="center" class="stdtxterr">El Producto agregado esta en Backorder</td></tr>');
											++$cses{'items_in_basket'};	
											### Fix Sales GQ
											++$cses{'items_total'};						
											$cses{'items_'.$cses{'items_in_basket'}.'_id'} = $rec->{'ID_sku_products'};
											$cses{'items_'.$cses{'items_in_basket'}.'_qty'} = 1;
											$cses{'items_'.$cses{'items_in_basket'}.'_express_delivery'} = &load_name('sl_products','ID_products',substr($in{'id_prod'},-6),'ExpressShipping');

											if ($cfg{'multiprice'}){
												$cses{'items_'.$cses{'items_in_basket'}.'_pnum'} = $in{'pricenumber'};
											}

											#####
											#####  Creacion de variables  paytype_available y fp_available
											#####
											&paytype_fp_available();

									}else{
										$va{'msg_sku'} =1;
									}
								}
							}

							## Overwrite Prices
							if($in{'overwrite_option'} and $cfg{'overwrite' .$in{'overwrite_option'} . $in{'id_products'}}){
								my ($price,$fpprice,$flexipago,$downpayment,$shp,$shpcal,$freeshp) = split(/\|/,$cfg{'overwrite' .$in{'overwrite_option'} . $in{'id_products'}});
								$cses{'items_'.$cses{'items_in_basket'}.'_price_ow'} = $price;
								$cses{'items_'.$cses{'items_in_basket'}.'_fpprice_ow'} = $fpprice;
								$cses{'items_'.$cses{'items_in_basket'}.'_fpago_ow'} = $flexipago;
								$cses{'items_'.$cses{'items_in_basket'}.'_downpayment_ow'} = $downpayment;
								$cses{'items_'.$cses{'items_in_basket'}.'_shp_ow'} = $shp;
								$cses{'items_'.$cses{'items_in_basket'}.'_shp_cal_ow'} = $shpcal;
								$cses{'items_'.$cses{'items_in_basket'}.'_freeshp_ow'} = $freeshp;
							}

							################################
							## Choices List
							################################
							if ($va{'msg_sku'} and $cfg{'promo'.$in{'id_prod'}}){
								$va{'msg_sku'} = qq|
									<form action="/cgi-bin/mod/sales/admin" method="post" name="sitform"  onsubmit="return checkchoices();">
										<input type="hidden" name="cmd" value="console_order">
										<input type="hidden" name="step" value="2">
										<input type="hidden" name="action" value="add_to_basket">
										<input type="hidden" name="skupro" value="1">
										<input type="hidden" name="pricenumber" value="$in{'pricenumber'}">
										<input type="hidden" name="id_products" value="$in{'id_prod'}">

							  	<tr>
										<td align="center" class="titletext" colspan="4">Debe seleccionar una opcion de la Lista</td>
								</tr>\n|;
								my (@pary) = split(/\|/,$cfg{'promo'.$in{'id_prod'}});

								for (0..$#pary){

									$va{'msg_sku'} .= qq|
									<tr>
										<td align="center" class="menu_bar_title" colspan="4">Opciones de Productos : $pary[$_] |.&load_db_names('sl_products','ID_products',$pary[$_],'[Name]/[Model]') . qq|</td>
									</tr>|;
									my $is_checked=0;
									my ($choices);
									my (@c) = split(/,/,$cfg{'srcolors'});						
									my ($sth) = &Do_SQL("SELECT * FROM sl_skus WHERE ID_products=$pary[$_] and Status != 'Inactive' ORDER BY ID_sku_products");
									while ($rec = $sth->fetchrow_hashref){
										$d = 1 - $d;
										my $cadchecked='';
										(!$is_checked) and ($cadchecked='checked="checked"') and ($is_checked=1);
										$backorder='';
										($rec->{'Status'} eq 'Backorder')	and ($backorder	=	'<span style="color:red;">[Backorder]</span>');
										$choices = &load_choices('-',$rec->{'choice1'},$rec->{'choice2'},$rec->{'choice3'},$rec->{'choice4'});
										$va{'msg_sku'} .= qq| 
												<tr bgcolor='$c[$d]'>
													<td class='smalltext' colspan="2" nowrap>
															<input type='radio' class='radio' name='idp$pary[$_]|.($_+1).qq|' value='$rec->{'ID_sku_products'}' $cadchecked>
															|.&format_sltvid($rec->{'ID_sku_products'}).qq|</td>
													<td class='smalltext' colspan="2">$choices $backorder</td>
												</tr>\n|;
									}
									##onClick="trjump('$script_url?cmd=console_order&step=2&action=add_to_basket&skupro=1&id_products=$pary[$_]&choice1=$rec->{'choice1'}&choice2=$rec->{'choice2'}&choice3=$rec->{'choice3'}&choice4=$rec->{'choice4'}')
								}

								$va{'msg_sku'} .= qq|
								<form>
							  	<tr>
										<td align="center" class="titletext" colspan="4"><input type="submit" class="button" value="Agregar al Carro"</td>
								</tr></form>\n|;
								
							}elsif ($va{'msg_sku'}){
								delete($va{'msg_sku'});
								my $linkmultiprice = '';
								$linkmultiprice = "&pricenumber=$in{'pricenumber'}"	if $cfg{'multiprice'};
								

								if($va{'choice_price'}){

									$va{'msg_sku'} .= qq|
													  	<tr>
															<td align="center" class="stdtxterr" colspan="4">La opcion $va{'choice_name'} no es elegible para el precio de |.&format_price($va{'choice_price'}).qq|</td>
														</tr>|;

								}

								$va{'msg_sku'} .= qq|
							  	<tr>
										<td align="center" class="titletext" colspan="4">Debe seleccionar una opcion de la Lista</td>
									</tr>
									<tr>
										<td align="center" class="menu_bar_title" colspan="4">Opciones de Productos</td>
									</tr>|;
												
								my ($choices);
								my (@c) = split(/,/,$cfg{'srcolors'});						
								my ($sth) = &Do_SQL("SELECT * FROM sl_skus WHERE ID_products=$in{'id_prod'} and Status != 'Inactive' ORDER BY ID_sku_products");
								while ($rec = $sth->fetchrow_hashref){
									$d = 1 - $d;
									$backorder='';
									$choices = &load_choices('-',$rec->{'choice1'},$rec->{'choice2'},$rec->{'choice3'},$rec->{'choice4'});
									($rec->{'Status'} eq 'Backorder') and ($backorder	=	'<span style="color:red;">(Backorder)</span>');
									$va{'msg_sku'} .= qq| 
											<tr onmouseover='m_over(this)' onmouseout='m_out(this)' bgcolor='$c[$d]' onClick="trjump('$script_url?cmd=console_order&step=2&action=add_to_basket&skupro=1&id_products=$in{'id_prod'}&choice1=|.uri_escape($rec->{'choice1'}).qq|&choice2=|.uri_escape($rec->{'choice2'}).qq|&choice3=|.uri_escape($rec->{'choice3'}).qq|&choice4=|.uri_escape($rec->{'choice4'}).qq|$linkmultiprice')">
												<td class='smalltext' colspan="2" nowrap>|.&format_sltvid($rec->{'ID_sku_products'}).qq|</td>
												<td class='smalltext' colspan="2">$choices $backorder</td>
											</tr>\n|;
								}	
							}

				 		}

					} ## Valid


				} ## sku_pro			
				
			} ## $in{'id_products'}

		} ## for

		### Fix Sales GQ
		if( !$cses{'pay_type'} and $cses{'items_total'} > 0 ){
			if( $cses{'paytype_order'} ne '' ){
				$cses{'pay_type'} = 'cc' if( $cses{'paytype_order'} =~ /Credit-Card/ );
				$cses{'pay_type'} = 'cod' if( $cses{'paytype_order'} =~ /COD/ );
				$cses{'pay_type'} = 'rd' if( $cses{'paytype_order'} =~ /Referenced Deposit/ );
			}else{
				for my $i(1..$cses{'items_in_basket'}){
					if( $cses{'items_'.$i.'_paytype'} ){
						$cses{'pay_type'} = "cc" if( $cses{'items_'.$i.'_paytype'} eq 'Credit-Card' );
						$cses{'pay_type'} = "cod" if( $cses{'items_'.$i.'_paytype'} eq 'COD' );
						$cses{'pay_type'} = "rd" if( $cses{'items_'.$i.'_paytype'} eq 'Referenced Deposit' );			
						last;
					}
				}
			}
		}		

	}


1;