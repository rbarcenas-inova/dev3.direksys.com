#!/usr/bin/perl
##################################################################
############      CONSOLE STEP 3 : TO CUSTOMER SUPPORT OR START ORDER / SELECT ITEM
##################################################################
# Last Modified on: 10/29/08 09:58:18
# Last Modified by: MCC C. Gabriel Varela S, L.I. Roberto B�rcenas: Se hace que se muestren las opciones de pago dependiendo de las variables de configuraci�n de sistema y adem�s las del tipo de pagos del producto
# Last Modified on: 10/30/08 10:17:32
# Last Modified by: MCC C. Gabriel Varela S: Se hace que se establezca la variable de sesi�n Type de acuerdo a si el cliente es tipo Retail o Membership
# Last Modified RB: 12/02/08  18:58:01 Se divide layaway en CC y MO
# Last Modified on: 12/17/08 13:54:56
# Last Modified by: MCC C. Gabriel Varela S: Se modifica para soportar s�lo comprar membres�a en radiobotones de tipo de pago
# Last Modified RB: 12/02/08  18:58:01 Se cancelan tipos de pago de preorden si existe un intento de cobro con CC
# Last Modified by RB on 06/02/2011 05:39:12 PM : Se agrega Prepaid-Card - pay_type=ppc

	$va{'speechname'} = 'ccinbound:3- Customer Info';

	## Zip Selected for Pay Type
	$in{'shp_zip'} = $cses{'zipcode_selected'} if($cses{'zipcode_selected'});

	if($in{'change_customer'}){

		delete($cses{'id_customers'});
		delete($in{'firstname'});
		delete($in{'lastname1'});
		delete($in{'lastname1'});
		$new_customer = 1;

	}

	if(!$in{'action'}){

		$in{'id_pricelevels'} =  &load_name('sl_orders','ID_customers',$cses{'id_customers'},'ID_pricelevels') if $cses{'id_customers'} > 0;
		$in{'birthcountry'} = &load_name('sl_customers','ID_customers',$cses{'id_customers'},'BirthCountry') if $cses{'id_customers'} > 0;
		$in{'sex'} = &load_name('sl_customers','ID_customers',$cses{'id_customers'},'Sex') if $cses{'id_customers'} > 0;
		$in{'repeatedcustomer'} = 'Yes' if $cses{'id_customers'} > 0;
		$in{'atime'} = &load_name('sl_customers','ID_customers',$cses{'id_customers'},'atime') if $cses{'id_customers'} > 0;

	}
	
	###
	### Se obtienen $in{'shp_city'}, $in{'shp_state'} y $cses{'id_zones'}
	###
	&get_shipping_data();
	$cadtypespay = &paytypes_for_products;
	$cadtypespay_zones = $cses{'id_zones'} > 0 ? &load_name('sl_zones','ID_zones',$cses{'id_zones'},'Payment_Type') : '';
	my $tempzone = $cses{'zipcode_selected'} ? &load_name('sl_zipcodes','ZipCode',$cses{'zipcode_selected'},'ID_zones') : 0;
	$cadtypespay_zones = ($cses{'zipcode_selected'} > 0 and $tempzone and !$in{'payment_type_verification'}) ? &load_name('sl_zones','ID_zones',$tempzone,'Payment_Type') : $cadtypespay_zones;
	#&cgierr("cd: $cadtypespay   y cdz: $cadtypespay_zones ");

	$va{'avpaytypes'} .= qq|<input type="radio" name="pay_type" id="pay_type_cc" value="cc" class="radio"><label for="pay_type_cc">Tarjeta de Cr&eacute;dito</label>&nbsp| if($cfg{'paytypescc'} and $cadtypespay=~/Credit-Card/ and ($cadtypespay_zones =~ /Credit-Card/ or $cadtypespay_zones eq '') )or($cfg{'paytypescc'} and $cadtypespay eq "" and $cadtypespay_zones eq '' and $cses{'servis_in_basket'}>0);
	$va{'avpaytypes'} .= qq|<input type="radio" name="pay_type" id="pay_type_ppc" value="ppc" class="radio"><label for="pay_type_ppc">Prepaid Card</label>&nbsp;|if (($cfg{'paytypesppc'} and $cadtypespay=~/Prepaid/ and ($cadtypespay_zones =~ /Prepaid/ or $cadtypespay_zones eq '') ) or($cfg{'paytypesppc'} and $cadtypespay eq "" and $cadtypespay_zones eq '' and $cses{'servis_in_basket'}>0));
	$va{'avpaytypes'} .= qq|<input type="radio" name="pay_type" id="pay_type_check" value="check" class="radio"><label for="pay_type_check">Cheque</label>&nbsp|if ($cfg{'paytypeschk'} and $cadtypespay=~/Check/ and ($cadtypespay_zones =~ /Check/ or $cadtypespay_zones eq '')) or ($cfg{'paytypeschk'} and $cadtypespay eq "" and $cadtypespay_zones eq '' and $cses{'servis_in_basket'}>0);
	$va{'avpaytypes'} .= qq|<input type="radio" name="pay_type" id="pay_type_rd" value="rd" class="radio"><label for="pay_type_rd">Deposito Referenciado</label>&nbsp| if($cfg{'paytypesrd'} and $cadtypespay=~/Referenced Deposit/ and ($cadtypespay_zones =~ /Referenced Deposit/ or $cadtypespay_zones eq '') ) or ($cfg{'paytypesrd'} and $cadtypespay eq "" and $cadtypespay_zones eq '' and $cses{'servis_in_basket'} > 0);

	
	### Build Payment Types with Alerts
	if (!$cses{'retries'}){
		#$va{'avpaytypes'} .= qq|<input type="radio" name="pay_type" value="ppc" class="radio">Prepaid Card&nbsp|if ($cfg{'paytypesppc'} and $cadtypespay=~/Prepaid/)or($cfg{'paytypesppc'} and $cadtypespay eq"" and $cses{'servis_in_basket'}>0);
		$va{'avpaytypes'} .= qq|<input type="radio" name="pay_type" id="pay_type_mo" value="mo" class="radio" OnClick="popup_show('ajax_windows', 'ajax_drag', 'ajax_exit', 'element-right', -1, -1,'wumsg');loadDoc('/cgi-bin/common/apps/ajaxbuild?ajaxbuild=showscript&name=ccinbound:7e- Money Order')"><label for="pay_type_mo">Money Order</label>&nbsp|if ($cfg{'paytypesmo'} and $cadtypespay=~/Money-Order/ and ($cadtypespay_zones =~ /Money-Order/ or $cadtypespay_zones eq '') )or($cfg{'paytypesmo'} and $cadtypespay eq"" and $cses{'servis_in_basket'}>0);
		$va{'avpaytypes'} .= qq|<input type="radio" name="pay_type" id="pay_type_wu" value="wu" class="radio" OnClick="popup_show('ajax_windows', 'ajax_drag', 'ajax_exit', 'element-right', -1, -1,'wumsg');loadDoc('/cgi-bin/common/apps/ajaxbuild?ajaxbuild=showscript&name=ccinbound:7c- WesterUnion Agents')"><label for="pay_type_wu">Western Union</label>&nbsp|if ($cfg{'paytypeswu'} and $cadtypespay=~/WesternUnion/ and ($cadtypespay_zones =~ /WesternUnion/ or $cadtypespay_zones eq '') )or($cfg{'paytypeswu'} and $cadtypespay eq"" and $cses{'servis_in_basket'}>0);
		$va{'avpaytypes'} .= qq|<input type="radio" name="pay_type" id="pay_type_lay" value="lay" class="radio"  OnClick="popup_show('ajax_windows', 'ajax_drag', 'ajax_exit', 'element-right', -1, -1,'wumsg');loadDoc('/cgi-bin/common/apps/ajaxbuild?ajaxbuild=showscript&name=ccinbound:7f- Layaway')"><label for="pay_type_lay">Apartado C.C. (o TDC en un Pago)</label>&nbsp
								<input type="radio" name="pay_type" id="pay_type_laymo" value="laymo" class="radio" OnClick="popup_show('ajax_windows', 'ajax_drag', 'ajax_exit', 'element-right', -1, -1,'wumsg');loadDoc('/cgi-bin/common/apps/ajaxbuild?ajaxbuild=showscript&name=ccinbound:7f- Layaway')"><label for="pay_type_laymo">Apartado M.O. (o MO en un Pago)</label>&nbsp|if ($cfg{'paytypeslay'} and $cadtypespay=~/Layaway/)or($cfg{'paytypeslay'} and $cadtypespay eq"" and $cses{'servis_in_basket'}>0);		
		$va{'avpaytypes'} .= qq|<input type="radio" name="pay_type" id="pay_type_cod" value="cod" class="radio" OnClick="popup_show('ajax_windows', 'ajax_drag', 'ajax_exit', 'element-right', -1, -1,'wumsg');loadDoc('/cgi-bin/common/apps/ajaxbuild?ajaxbuild=showscript&name=ccinbound:7g- COD')"><label for="pay_type_cod">COD</label>&nbsp|if ($cfg{'paytypescod'} and $cadtypespay=~/COD/ and ($cadtypespay_zones =~ /COD/ or $cadtypespay_zones eq '') )or($cfg{'paytypescod'} and $cadtypespay eq"" and $cses{'servis_in_basket'}>0);

		
	}else{	    
			$va{'avpaytypes'} .= qq|<input type="radio" name="pay_type" id="pay_type_mo" value="mo" class="radio"><label for="pay_type_mo">Money Order</label>&nbsp|if ($cfg{'paytypesmo'} and $cadtypespay=~/Money-Order/ and ($cadtypespay_zones =~ /Money-Order/ or $cadtypespay_zones eq '') )or($cfg{'paytypesmo'} and $cadtypespay eq"" and $cses{'servis_in_basket'}>0);
			$va{'avpaytypes'} .= qq|<input type="radio" name="pay_type" id="pay_type_wu" value="wu" class="radio"><label for="pay_type_wu">Western Union</label>&nbsp|if ($cfg{'paytypeswu'} and $cadtypespay=~/WesternUnion/ and ($cadtypespay_zones =~ /WesternUnion/ or $cadtypespay_zones eq '') )or($cfg{'paytypeswu'} and $cadtypespay eq"" and $cses{'servis_in_basket'}>0);
			$va{'avpaytypes'} .= qq|<input type="radio" name="pay_type" id="pay_type_lay" value="lay" class="radio"><label for="pay_type_lay">Apartado C.C. (o TDC en un Pago)</label>&nbsp<input type="radio" name="pay_type" id="pay_type_laymo" value="laymo" class="radio"><label for="pay_type_laymo">Apartado M.O. (o MO en un Pago)</label>&nbsp|if ($cfg{'paytypeslay'} and $cadtypespay=~/Layaway/)or($cfg{'paytypeslay'} and $cadtypespay eq"" and $cses{'servis_in_basket'}>0);		
			$va{'avpaytypes'} .= qq|<input type="radio" name="pay_type" id="pay_type_cod" value="cod" class="radio"><label for="pay_type_cod">COD</label>&nbsp;|if (($cfg{'paytypescod'} and $cadtypespay=~/COD/ and ($cadtypespay_zones =~ /COD/ or $cadtypespay_zones eq '') )or($cfg{'paytypescod'} and $cadtypespay eq"" and $cses{'servis_in_basket'}>0)) and ($cfg{'allow_chg_cod'} != 0 or $cses{'pay_type'} eq 'cod');
			$va{'avpaytypes'} .= qq|<br><span class="stdtxterr">Si hiciste un intento de cobro con Tarjeta y deseas pasar la orden a COD, elige la opci&oacute;n No tiene otra forma de Pago en el paso 8. La orden puede ser pasada desde el m&oacute;dulo de tu Supervisor.</span>|	if ($cses{'pay_type'} eq 'cc' and $cfg{'allow_chg_cod'} ==0);
	}

	if(!$va{'avpaytypes'} or $in{'payment_type_verification'}){
		chop($cadtypespay);
		$va{'avpaytypes'} = &trans_txt('step3_noavpaytypes');
		$va{'avpaytypes'} .= qq|<br>Order Payment: $cadtypespay <br>Zone Payment: $cadtypespay_zones|;  
	}

	############################################################
	############################################################
	#################
	#################
	################# STEP 3 : CUSTOMER BASIC INFO
	#################
	#################
	############################################################
	############################################################
	
	&load_cfg('sl_customers');
	$in{'type'} = 'Retail' if(!$cses{'type'});
	$in{'type'} = &load_name('sl_customers','ID_customers',$cses{'id_customers'},'Type') if($cses{'id_customers'} and !$cses{'type'});

	if ($in{'action'} && !$new_customer){

		if (!$in{'id_pricelevels'}){

			$error{'id_pricelevels'} = &trans_txt('required');
			$in{'step'} = 3;
			++$err;

		}else{
			$cses{'id_pricelevels'} = $in{'id_pricelevels'};
		}

		$in{'status'} = 'Active';
		$in{'cid'} = $cses{'cid'};
		
		($err,$query) = &validate_cols('1');
		#&cgierr("$err<br>$query");

		if (!$in{'pay_type'}){

			$error{'pay_type'} = &trans_txt('required');
			++$err;

		}

		($in{'pay_type'} eq 'cod' and $cses{'shp_type'} < 3) and ($cses{'shp_type'} = 3); 
		($in{'pay_type'} ne 'cod' and $cses{'shp_type'} == 3) and ($cses{'shp_type'} = 1);

		#VALIDAMOS FECHA DE CUMPLEAÑOS
		if ( ! $in{'birthday'} or $in{'birthday'} eq '') {
			$error{'birthday'} = &trans_txt('required');
			++$err;
		}

		##########################
		##########################
		#######
		####### Check Cupon
		#######
		##########################
		##########################

		#&cgierr('in:'.$in{'cupon'});

		if ($in{'cupon'}){

			my ($sth) = &Do_SQL("SELECT * FROM sl_coupons WHERE PublicID='".$in{'cupon'}."' AND Status='Active' AND (ValidFrom <= CURDATE() AND ValidTo >= CURDATE())");
      		$vara = $sth->fetchrow_hashref;		


			if ($vara->{'PublicID'})
			{

				if ($cses{'id_customers'})
				{
			
					##
					## Revisar otras limitaciones
					#$sth = &Do_SQL("SELECT COUNT(*) FROM sl_coupons_trans WHERE ID_customers='$cses{'id_customers'}'");
					#if ($sth->fetchrow >0){
									      
					$sthc = &Do_SQL("SELECT count(sl_orders.ID_customers) as cus FROM sl_coupons_trans inner join sl_orders on sl_coupons_trans.ID_orders=sl_orders.ID_orders WHERE id_coupons = '$vara->{'ID_coupons'}' and sl_orders.ID_customers = '$cses{'id_customers'}' group by id_coupons");
					$varc = $sth->fetchrow_hashref;			
					if($varc->{'cus'} >= $vara->{'MaxPerCust'}){					      
						$error{'cupon'} = &trans_txt('cupon_used');
						$err++;													
					}else{
						#$sth = &Do_SQL("_SELECT * FROM sl_coupons WHERE PublicID='$in{'cupon'}' AND Status='Active' AND (ValidFrom <= CURDATE() AND ValidTo >= CURDATE())");
			      		#$vara = $sth->fetchrow_hashref;				

						$sth = &Do_SQL("SELECT ID_coupons, count(sl_orders.ID_customers) as cus, count(shp_State) as s_sta, count(shp_Zip) as s_zip FROM sl_coupons_trans inner join sl_orders on sl_coupons_trans.ID_orders=sl_orders.ID_orders WHERE  id_coupons = '$vara->{'ID_coupons'}' and sl_orders.ID_customers = $cses{'id_customers'} GROUP by id_coupons, sl_orders.id_customers, shp_State, shp_Zip;");
			      		$varb = $sth->fetchrow_hashref;			
						if ( $vara{'MaxPerCust'}  <= $varb->{'cus'}   and   $vara->{'MaxPerState'} <= $varb->{'sta'}   and   $vara->{'MaxPerZip'} <= $varb->{'zip'}   ){
							$error{'cupon'} = &trans_txt('cupon_used');
							$err++;
						}else{
							$error{'cupon'} = &trans_txt('valid');
							$cses{'cupon'} = $in{'cupon'};								
					  	}
					}
				}else{
					$error{'cupon'} = &trans_txt('valid');
					$cses{'cupon'} = $in{'cupon'};
				}
			}else{
				$error{'cupon'} = &trans_txt('invalid');
				$err++;
			}
		}else{
			$error{'cupon'} = &trans_txt('invalid');
			$cses{'cupon'} = '';
		}


		if(!$err){

			delete($va{'message'});
			local(%error);

			if ($in{'country_tab'}){
				$in{'step'} = "4$in{'country_tab'}";
			}else{
				$in{'step'} = '4us';
			}

			if(!$in{'id_pricelevels'}){
				
				$in{'step'} = 3;

			}else{

				$cses{'id_pricelevels'} = $in{'id_pricelevels'};
				$cses{'answers0'} = $in{'answers0'};
				$cses{'answers1'} = $in{'answers1'};
				$cses{'answers2'} = $in{'answers2'};
				$cses{'answers3'} = $in{'answers3'};
				$cses{'answers4'} = $in{'answers4'};
			}

			#&cgierr($in{'step'});
			$va{'speechname'}= 'ccinbound:4- Billing Info';
			for (1..$#db_cols-3){
				($in{lc($db_cols[$_])}) and ($cses{lc($db_cols[$_])} = $in{lc($db_cols[$_])});
				#$cses{lc($db_cols[$_])} = $in{lc($db_cols[$_])};
			}

			$cses{'pay_type'} = $in{'pay_type'};
			$cses{'repeatedcustomer'} = $in{'repeatedcustomer'};
			$cses{'cupon'} = $in{'cupon'};
			
			if($in{'pay_type'} eq 'laymo'){
				$cses{'pay_type'} = 'lay';
				$cses{'laytype'} = 'mo';
			}elsif($in{'pay_type'} eq 'lay'){
				$cses{'laytype'} = 'cc';
			}elsif($cses{'laytype'}){
				delete($cses{'laytype'});
			}	
			$cses{'status3'} = 'ok';

		}else{

			if(!$in{'id_pricelevels'}){
				$in{'step'} = 3;
				$err=0;
			}
			$cses{'status3'} = 'err';
			$va{'message'} = &trans_txt('reqfields');

		}

	}
	
	if($cses{'id_customers'} && $in{'step'} eq 3){
		$in{'step'} = $in{'step'}."a";
	}
		
	($cses{'zipcode_selected'}) and ($va{'zipcode'} = $cses{'zipcode_selected'});
	($cses{'zipcode'}) and ($va{'zipcode'} = $cses{'zipcode'});

	#&cgierr("x$in{'step'}");
	if ($in{'action'}){ delete($in{'action'}) &cod_redir; }

1;