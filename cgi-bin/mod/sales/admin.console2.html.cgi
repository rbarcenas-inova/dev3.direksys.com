#!/usr/bin/perl
##################################################################
############                HOME                 #################
##################################################################

use Date::Calc qw();
use Date::Calc qw(Add_Delta_Days);


##################################################################
############                ORDER                 ################
##################################################################
sub console_sales {
# --------------------------------------------------------
		
	&load_callsession();
	
	$va{'step'} = ($in{'step'}) ? int($in{'step'}) : int($cses{'step'});

	if( !$cses{'time_ini'} and int($va{'step'}) == 1 ){
		my $sth = &Do_SQL("SELECT NOW();");
		$cses{'time_ini'} = 'Inicio: '.$sth->fetchrow()."\n\n";
	}

	### Canal de venta
	$cses{'id_salesorigins'}	= ($in{'id_salesorigins'}) ? ($in{'id_salesorigins'}) : $cses{'id_salesorigins'};
	#$cses{'id_salesorigins'} = 1;
	$va{'id_salesorigins'}		= $cses{'id_salesorigins'};
	$cses{'salesorigins.channel'} 	= &load_name('sl_salesorigins','ID_salesorigins',$cses{'id_salesorigins'},'Channel') if( $cses{'id_salesorigins'} );
	$va{'salesorigins.channel'} 	= $cses{'salesorigins.channel'};

	### Controla el CID de la orden
	$cses{'phone_cid'} = ( $in{'phone_cid'} ) ? $in{'phone_cid'} : $cses{'phone_cid'};
	$va{'phone_cid'} = $cses{'phone_cid'};

	### Datos del cliente
	if( $va{'step'} == 2 and $in{'action'} eq 'customer' ){
		### Se valida el ID del cliente
		$cses{'id_customers'} = int($in{'id_customers'});
		if( $cses{'id_customers'} > 0 ){
			my $sql_cus = "SELECT ID_customers FROM sl_customers WHERE ID_customers = '".$cses{'id_customers'}."' LIMIT 1;";
			my $sth_cus = &Do_SQL($sql_cus);
			my $this_id_customers = $sth_cus->fetchrow();
			if( !$this_id_customers ){
				$cses{'id_customers'} = 0;
			}
		}

		$cses{'phone'}			= $in{'phone'};
		$cses{'firstname'}		= $in{'firstname'};
		$cses{'lastname1'}		= $in{'lastname1'};
		$cses{'lastname2'}		= $in{'lastname2'};
		$cses{'zipcode'}		= $in{'zipcode'};
		$cses{'address1'}		= $in{'address1'};
		$cses{'urbanization'}	= uc($in{'urbanization'});
		$cses{'city'}			= uc($in{'city'});
		$cses{'state'}			= uc($in{'state'});
	}
	if( $in{'action'} eq 'address' ){
		$cses{'firstname'}		= $in{'firstname'};
		$cses{'lastname1'}		= $in{'lastname1'};
		$cses{'lastname2'}		= $in{'lastname2'};
		$cses{'sex'}			= $in{'sex'};
		$cses{'address1'}		= $in{'address1'};
		$cses{'address2'}		= $in{'address2'};
		$cses{'address3'}		= $in{'address3'};
		$cses{'urbanization'}	= uc($in{'urbanization'});
		$cses{'city'}			= uc($in{'city'});
		$cses{'state'}			= uc($in{'state'});
		$cses{'zipcode'}		= $in{'zipcode'};
		$cses{'phone'}			= $in{'phone'};
		$cses{'phone2'}			= $in{'phone2'};
		$cses{'cellphone'}		= $in{'cellphone'};
		$cses{'email'}			= $in{'email'};
		$cses{'contact_mode'}	= $in{'contact_mode'};
		$cses{'birthday'}		= $in{'birthday'};
		$cses{'bday_month'}		= substr($in{'birthday'}, 5, 2);
		$cses{'bday_day'}		= substr($in{'birthday'}, 8, 2);
		$cses{'orders_notes'}	= $in{'orders_notes'};

		$cses{'shp_name'}		= $in{'shp_name'};
		$cses{'shp_address1'}	= $in{'shp_address1'};
		$cses{'shp_urbanization'}=uc($in{'shp_urbanization'});
		$cses{'shp_city'}		= uc($in{'shp_city'});
		$cses{'shp_state'}		= uc($in{'shp_state'});
		$cses{'shp_zipcode'}	= $in{'shp_zipcode'};
		$cses{'shp_address2'}	= $in{'shp_address2'};
		$cses{'shp_address3'}	= $in{'shp_address3'};
		$cses{'atime'}			= $in{'atime'};
		$cses{'shp_notes'}		= $in{'shp_notes'};
	}
	$va{'id_customers'}		= $cses{'id_customers'};
	$va{'customers'}		= (int($va{'id_customers'}) > 0) ? $va{'id_customers'} : 'Nuevo';
	$va{'firstname'}		= $cses{'firstname'};
	$va{'lastname1'}		= $cses{'lastname1'};
	$va{'lastname2'}		= $cses{'lastname2'};
	$va{'sex'}				= $cses{'sex'};
	$va{'fullname'}			= $va{'firstname'}.' '.$va{'lastname1'}.' '.$va{'lastname2'};
	$va{'address1'}			= $cses{'address1'};
	$va{'address2'}			= $cses{'address2'};
	$va{'address3'}			= $cses{'address3'};
	$va{'urbanization'}		= uc($cses{'urbanization'});
	$va{'city'}				= $cses{'city'};
	$va{'state'}			= $cses{'state'};
	$va{'zipcode'}			= $cses{'zipcode'};
	$va{'phone'}			= $cses{'phone'};
	$va{'phone2'}			= $cses{'phone2'};
	$va{'cellphone'}		= $cses{'cellphone'};
	$va{'email'}			= $cses{'email'};
	$va{'contact_mode'}		= $cses{'contact_mode'};
	$va{'birthday'}			= $cses{'birthday'};
	$va{'bday_month'}		= $cses{'bday_month'};
	$va{'bday_day'}			= $cses{'bday_day'};
	$va{'shp_name'}			= $cses{'shp_name'};
	$va{'shp_address1'}		= $cses{'shp_address1'};
	$va{'shp_urbanization'}	= $cses{'shp_urbanization'};
	$va{'shp_city'}			= $cses{'shp_city'};
	$va{'shp_state'}		= $cses{'shp_state'};
	$va{'shp_zipcode'}		= $cses{'shp_zipcode'};
	$va{'shp_address2'}		= $cses{'shp_address2'};
	$va{'shp_address3'}		= $cses{'shp_address3'};
	$va{'atime'}			= $cses{'atime'};
	$va{'shp_notes'}		= $cses{'shp_notes'};
	$va{'orders_notes'}		= $cses{'orders_notes'};

	$va{'show_shp_zipcode'} = ' / <span id="spn_shp_zipcode_content">'.$va{'shp_zipcode'}.'</span>' if( $va{'shp_zipcode'} ne '' and $va{'shp_zipcode'} ne $va{'zipcode'} );

	### Datos del tipo de envio
	$va{'zones_express_delivery'} = $cses{'zones_express_delivery'} if( $cses{'zones_express_delivery'} );

	### Datos completos?
	$va{'full_data'}	= ($in{'full_data'}) ? $in{'full_data'} : '0';
	$va{'full_data'} 	= $cses{'full_data'} if( $cses{'full_data'} and !$in{'full_data'} );
	$cses{'full_data'} 	= $va{'full_data'};

	### Datos de la forma de pago
	if( $in{'pay_type'} ){
		$va{'pay_type'} 	= 'cc' if( $in{'pay_type'} eq 'Credit-Card' );
		$va{'pay_type'} 	= 'rd' if( $in{'pay_type'} eq 'Referenced Deposit' );
		$va{'pay_type'} 	= 'cod' if( $in{'pay_type'} eq 'COD' );
		$cses{'pay_type'} 	= $va{'pay_type'};
	}

	if( $in{'rst_pay_type'} and int($in{'rst_pay_type'}) == 1 ){
		if( $cses{'pay_type'} eq 'rd' and $cses{'products_express_delivery'} eq 'Yes' ){
			$cses{'products_express_delivery'} = 'No';
		}
		$cses{'order_shipping'} = 0;
		$va{'order_shipping'} = $cses{'order_shipping'};
		delete($cses{'shp_type'});
		$va{'shp_type'} = '';#$cses{'shp_type'};
		delete($cses{'pay_type'});
		delete($cses{'total_pmts'});
	}

	### Impuestos
	$va{'taxes'} = $cses{'taxes'} if( $cses{'taxes'} );

	### CC info	
	$va{'pmtfield7'}	= $cses{'pmtfield7'} if( $cses{'pmtfield7'} );#Type	
	$va{'pmtfield2'}	= $cses{'pmtfield2'} if( $cses{'pmtfield2'} );#Name	
	$va{'pmtfield3'}	= $cses{'pmtfield3'} if( $cses{'pmtfield3'} );#Number
	$va{'pmtfield1'}	= $cses{'pmtfield1'} if( $cses{'pmtfield1'} );#Red
	$va{'cc_month'}		= $cses{'cc_month'}  if( $cses{'cc_month'} );#Month exp.
	$va{'cc_year'}		= $cses{'cc_year'}   if( $cses{'cc_year'} );#Year exp.
	$va{'pmtfield5'}	= $cses{'pmtfield5'} if( $cses{'pmtfield5'} );#CVN
	$va{'pmtfield6'}	= $cses{'pmtfield6'} if( $cses{'pmtfield6'} );#Phone

	### Promos de MOW
	if( int($cfg{'promos_mow'}) == 1 ){
		$cses{'promos_mow'} = 1;
		$va{'promos_mow'} = 1;
	}

	### Coupon
	$cses{'coupon'} = ($in{'coupon'}) ? $in{'coupon'} : $cses{'coupon'};

	### Folio Promoción
	if( int($in{'folio_valid'}) > 0 ){
		$cses{'folio_promo'} = '' if( !$cses{'folio_promo'} );
		$cses{'folio_promo'} = ($in{'folio_promo'}) ? $in{'folio_promo'} : $cses{'folio_promo'};
		$cses{'folio_valid'} = int($in{'folio_valid'}); ## ID_promotions
		$cses{'id_customers_promo'} = int($in{'id_customers_promo'}); ## ID_customers

		if( $cses{'promos_mow'} == 1 ){
			### Evita la validacion de correspondencia entre el folio-cliente registrado y el folio-cliente proporcionados
		} elsif( int($in{'id_customers_promo'}) != int($cses{'id_customers'}) ){
			$cses{'folio_promo'} = '';
			$cses{'folio_valid'} = '0';
			$cses{'id_customers_promo'} = '0';
		}

	} elsif( $va{'step'} == 2 and $in{'action'} eq 'customer' ) {
		$cses{'folio_promo'} = '';
		$cses{'folio_valid'} = '0'; ## ID_promotions
		$cses{'id_customers_promo'} = '0'; ## ID_customers
	}
	$va{'folio_promo'} = $cses{'folio_promo'};
	$va{'folio_valid'} = $cses{'folio_valid'};
	$va{'id_customers_promo'} = $cses{'id_customers_promo'};
	if( ($va{'folio_promo'} and !$cses{'promos_mow'}) or int($cses{'id_customers_promo'}) > 0 ){
		$va{'lnk_folio_promo_info'} = '<a href="#" id="btn_validate_folio" class="" rel="folio" title="Visualizar folio...">
											<img src="/sitimages/default/b_view.gif" class="ico" alt="search" style="width: 18px;" />
										</a>';
	}

	### PostDate
	if( $in{'postdate_date'} and $in{'postdate'} eq 'Yes' ){
		$cses{'postdated'} = 'Yes';
		$cses{'postdated_date'} = $in{'postdate_date'};
		$cses{'postdated_days'} = 15;
	}

	### Guarda los datos de la sesión
	&save_callsession();

	### Vuelve a cargar los datos de la sesión
	&load_callsession();
	
	### Ejecuta funcionalidades propias de cada paso
	my $fn_name = "admin_console_step".int($va{'step'});
	&$fn_name;

	### Speech
	&get_speech();


	#### Debug
	if( int($va{'step'}) > 0 ){

		my $this_debug = "";
		if( $cses{'debug_sales'} ){
			$this_debug = $cses{'debug_sales'};
			delete($cses{'debug_sales'});
		}
		$this_debug .= "=============================================================================<br>\n";
		$this_debug .= "Step :: ".$va{'step'}."<br>\n";
		$this_debug .= "=============================================================================<br>\n";

		# $cses{'debug_sales'} .= "=============================================================================<br>\n";
		# $cses{'debug_sales'} .= "Step :: ".$va{'step'}."<br>\n";
		# $cses{'debug_sales'} .= "=============================================================================<br>\n";
		foreach my $key (keys %cses){
		 	if( $key ne 'debug_sales' ){
		 		# $cses{'debug_sales'} .= qq|$key -> $cses{$key}<br>\n|;
		 		$this_debug .= qq|$key -> $cses{$key}<br>\n|;
		 	}
		}

		&set_debug_sales($this_debug);
	}
	### Se guarda el debug si se llegó al paso final
	if( int($va{'step'}) == 6 ){#$cses{'debug_sales'} and
		my $sth = &Do_SQL("SELECT NOW();");
		$va{'time_end'} = 'Fin: '.$sth->fetchrow()."\n\n";
		# $cses{'debug_sales'} .= "\n".$va{'time_end'};

		my $debug = &get_debug_sales();
		$debug .= "\n".$va{'time_end'};
		&Do_SQL("INSERT INTO sl_debug (cmd, id, log, Date, Time, ID_admin_users) VALUES ('console_order_v2', '$cses{'id_orders'}', '".&filter_values($debug)."', CURDATE(), CURTIME(), '$usr{'id_admin_users'}');");

		## Se inserta en la tabla de tiempos
		&Do_SQL("INSERT INTO sl_orders_time SET 
					ID_orders = ".$cses{'id_orders'}."
					, Date = CURDATE() 
					, TimeStart = '".substr($cses{'time_ini'}, 8, 19)."'
					, TimeEnd = '".substr($va{'time_end'}, 5, 19)."'
				ON DUPLICATE KEY UPDATE
					TimeStart = '".substr($cses{'time_ini'}, 8, 19)."'
					, TimeEnd = '".substr($va{'time_end'}, 5, 19)."'
				;");
	}

	### Guarda los datos de la sesión
	&save_callsession();

	### Datos para el Depósito Referenciado
	$va{'banorte_company_name'} = $cfg{'banorte_company_name'};
	$va{'banorte_company_num'} = $cfg{'banorte_company_num'};
	$va{'azteca_company_name'} = $cfg{'azteca_company_name'};
	$va{'azteca_company_num'} = $cfg{'azteca_company_num'};
	$va{'cybersource_orgid'} = $cfg{'cybersource_orgid'};
	$va{'cybersource_merchantid'} = $cfg{'cybersource_merchantid'};

	### Genera el HTML
	print "Content-type: text/html\n\n";
	print &build_page("sales_step$va{'step'}.html");
	
}

##################################################################
############ Step 0 :: Inicio
##################################################################
sub admin_console_step0{

	foreach my $key (keys %cses){
	 	if( $key ne 'salesorigins.channel' and $key ne 'id_salesorigins' ){
	 		delete($cses{$key});
	 	}
	}

	&delete_debug_sales();
}

##################################################################
############ Step 1 :: Llamada
##################################################################
sub admin_console_step1{

	## Speech Code
	$va{'speech_code'} = 'ccinbound:'.$va{'step'}.'-Customer Call';

	$va{'phone_required'} = int($cfg{'required_phone'});
	$va{'firstname_required'} = int($cfg{'required_name'});

	$va{'view_promo_div'} = ( int($cfg{'promo_folios'}) == 1 ) ? 'display: block;' : 'display: none;';

	### -------------------------------------------------
	### Currency format
	### -------------------------------------------------
	### Carga la configuracion de moneda
	$va{'format_number'} = $sys{'fmt_curr_symbol'}.$sys{'fmt_curr_thousands_sep'}.$sys{'fmt_curr_decimal_point'};
	$va{'format_number'} =~ s/ //g; 
}

##################################################################
############ Step 2 :: Productos
##################################################################
sub admin_console_step2{
	
	$va{'zipcode'} = ($in{'zipcode'}) ? $in{'zipcode'} : $cses{'zipcode'};

	### -------------------------------------------------
	### Taxes
	### -------------------------------------------------
	my $taxes = &calculate_taxes($va{'zipcode'},'','',0);
	#ADG este query me trae la tasa de impuesto que se utilizara para comparar contra la que usa el taxstate y taxcity
	# Se hace una validacion para ver la tasa de impuesto que aplica al producto
	#ADG MX
	# if( uc($cfg{'country'}) eq 'MX' ){
	# 	my ($sth) = &Do_SQL("SELECT MAX(sale_tax)
	# 						FROM (
	# 							SELECT IF(sale_tax IS NULL,0,sale_tax) AS sale_tax
	# 							FROM sl_skus_parts
	# 								INNER JOIN sl_parts USING(ID_parts)
	# 								INNER JOIN sl_skus USING(ID_sku_products)
	# 							WHERE ID_products='$va{'id_products'}'
	# 						)taxes;");
	# 	my($tax_product) = $sth->fetchrow();
	# 	#checar siempre que el obternido sea > 0 para que sea valido
	# 	if($tax_product > 0) {
	# 		$tax_product = ($tax_product/100);
	# 	}else {
	# 		$tax_product = 0;
	# 	}

	# 	# NO ES LO MISMO 0 A QUE TENGA UN NULL EN EL TAX SALE DE UN PRODUCTO
	# 	# METEMOS LA REGLA DE COMPARACION CLIENTE 
	# 	if($tax_product < $taxes) {
	# 		$taxes = $tax_product;
	# 	}
	
	# }
	$va{'taxes'}	= $taxes;
	$cses{'taxes'}	= $va{'taxes'};

	### -------------------------------------------------
	### Payments Type
	### -------------------------------------------------	
	### Se obtienen los datos necesario de la zona en base al zipcode proporcionado
	### para la busqueda dinamica de productos
	$va{'pay_type_available'} = '';	
	if( $va{'zipcode'} > 0 ){
		if( !$cses{'shp_zipcode'} or $cses{'shp_zipcode'} eq '' ){
			&express_delivery_zones($va{'zipcode'});
		}else{
			&express_delivery_zones($cses{'shp_zipcode'});
		}
	}

	### -------------------------------------------------
	### Shipping
	### -------------------------------------------------
	# my (@pay_type) = split(/\,/,$va{'pay_type_available'}) if( $va{'pay_type_available'} );
	# for( 0..$#pay_type ){
	# 	if( $pay_type[$_] eq 'Credit-Card' ){
	# 		$cses{'shipping'} = $cfg{'shipment_cc_standard'}.'|';
	# 	}elsif( $pay_type[$_] eq 'Referenced Deposit' ){
	# 		$cses{'shipping'} .= $cfg{'shipment_rd_standard'}.'|';
	# 	}elsif( $pay_type[$_] eq 'COD' ){
	# 		$cses{'shipping'} .= $cfg{'shipment_cod_standard'}.'|';
	# 	}
	# }
	# $va{'shipping'} 	= substr($cses{'shipping'}, 0, -1);
	# $cses{'shipping'}	= $va{'shipping'};

	### -------------------------------------------------
	### Currency format
	### -------------------------------------------------
	### Carga la configuracion de moneda
	$va{'format_number'} = $sys{'fmt_curr_symbol'}.$sys{'fmt_curr_thousands_sep'}.$sys{'fmt_curr_decimal_point'};
	$va{'format_number'} =~ s/ //g; 
	
	### COD Config.
	$cses{'cod_limit_amt'} = $cfg{'cod_limit_amt'};
	$va{'cod_limit_amt'} = $cses{'cod_limit_amt'};

	## Speech Code
	$va{'speech_code'} = 'ccinbound:'.$va{'step'}.'-Products Search';
}

##################################################################
############ Step 3 :: Dirección  
##################################################################
sub admin_console_step3{

	my $zipcode_express = ( $va{'shp_zipcode'} and $va{'shp_zipcode'} != '' ) ? $va{'shp_zipcode'} : $va{'zipcode'};
	&express_delivery_zones($zipcode_express);

	if( $in{'products'} and $in{'products'} ne '' ){	
		$va{'shop_cart_products'} = $in{'products'};
		$cses{'shop_cart_products'} = $va{'shop_cart_products'};
	}
	
	### Verifica la disponibilidad del envio express de los productos
	&express_delivery_products();

	$va{'diff_amount_shp'} = 0;
	if( $cses{'products_express_delivery'} eq 'Yes' and $cses{'pay_type'} ne '' ){
		$va{'diff_amount_shp'} = $cfg{'shipment_'.$cses{'pay_type'}.'_express'} - $cfg{'shipment_'.$cses{'pay_type'}.'_standard'};
		$va{'diff_amount_shp'} = &format_price($va{'diff_amount_shp'});
		$va{'cost_shp_express'} = $cfg{'shipment_'.$cses{'pay_type'}.'_express'};		
	}
	$va{'cost_shp_standard'} = $cfg{'shipment_'.$cses{'pay_type'}.'_standard'};

	### Info. extra del cliente seleccionado
	if( $cses{'id_customers'} ){
		my $sql = "SELECT Sex, Address2, Address3, Cellphone, Phone2, Birthday, Email FROM sl_customers WHERE ID_customers = ".$cses{'id_customers'}.";";
		my $sth = &Do_SQL($sql);
		my $data = $sth->fetchrow_hashref();
		$cses{'sex'}		= $data->{'Sex'} if( !$cses{'sex'} );
		$va{'sex'}			= $cses{'sex'};
		$cses{'address2'}	= $data->{'Address2'} if( !$cses{'address2'} );
		$va{'address2'}		= $cses{'address2'};
		$cses{'address3'}	= $data->{'Address3'} if( !$cses{'address3'} );
		$va{'address3'}		= $cses{'address3'};
		$cses{'birthday'}	= ($data->{'Birthday'} ne '0000-00-00') ? $data->{'Birthday'} : '';
		$va{'birthday'}		= $cses{'birthday'};
		$cses{'cellphone'}	= $data->{'Cellphone'} if( !$cses{'cellphone'} );
		$va{'cellphone'}	= $cses{'cellphone'};
		$cses{'cellphone'}	= $data->{'Phone2'} if( !$cses{'phone2'} );
		$va{'phone2'}		= $cses{'phone2'};
		$cses{'email'}		= $data->{'Email'} if( !$cses{'Email'} );
		$va{'email'}		= $cses{'email'};
	}

	### Límite para la fecha de nacimiento(18 años atras)
	my $sth = &Do_SQL("SELECT DATE_SUB(CURDATE(), INTERVAL 18 YEAR);");
	$va{'max_birthday'} = $sth->fetchrow();
	$va{'max_birthday'} =~ s/-//g;

	## Speech Code
	$va{'speech_code'} = 'ccinbound:'.$va{'step'}.'-Customer Info';

}

##################################################################
############ Step 4 :: Pago
##################################################################
sub admin_console_step4{

	$va{'diff_amount_shp'} = 0;
	if( $cses{'products_express_delivery'} eq 'Yes' and $cses{'pay_type'} ne '' ){
		$va{'diff_amount_shp'} = $cfg{'shipment_'.$cses{'pay_type'}.'_express'} - $cfg{'shipment_'.$cses{'pay_type'}.'_standard'};
		$va{'diff_amount_shp'} = &format_price($va{'diff_amount_shp'});
		$va{'cost_shp_express'} = $cfg{'shipment_'.$cses{'pay_type'}.'_express'};
	}

	if( !$cses{'pmtfield7'} || $cses{'pmtfield7'} eq '' ){
		$cses{'pmtfield7'} = 'CreditCard';
		$va{'pmtfield7'} = $cses{'pmtfield7'};
	}

	## Speech Code
	$va{'speech_code'} = 'ccinbound:'.$va{'step'}.'-Payment';

}

##################################################################
############ Step 5 :: Confirmar
##################################################################
sub admin_console_step5{

	### Credit-Card Info
	if( $in{'pmtfield3'} ){
		$cses{'pmtfield7'}	= $in{'pmtfield7'};#Type
		$va{'pmtfield7'}	= $cses{'pmtfield7'};#Type
		$cses{'pmtfield2'}	= $in{'pmtfield2'};#Name
		$va{'pmtfield2'}	= $cses{'pmtfield2'};#Name
		$cses{'pmtfield3'}	= $in{'pmtfield3'};#Number
		$va{'pmtfield3'}	= $cses{'pmtfield3'};#Number
		$cses{'pmtfield1'}	= $in{'pmtfield1'};#Red
		$va{'pmtfield1'}	= $cses{'pmtfield1'};#Red
		$cses{'cc_month'}	= $in{'month'};#Month exp.
		$va{'cc_month'}		= $cses{'cc_month'};#Month exp.
		$cses{'cc_year'}	= $in{'year'};#Year exp.
		$va{'cc_year'}		= $cses{'cc_year'};#Year exp.
		$cses{'pmtfield5'}	= $in{'pmtfield5'};#CVN
		$va{'pmtfield5'}	= $cses{'pmtfield5'};#CVN
		$cses{'pmtfield6'}	= $in{'pmtfield6'};#Phone
		$va{'pmtfield6'}	= $cses{'pmtfield6'};#Phone

		if( $cses{'pmtfield7'} eq 'CreditCard' ){ 
			$va{'cardtype'} =  'crédito';
			$va{'cardtype_en'} = 'credit';
		}else{
			$va{'cardtype'} =  'débito';
			$va{'cardtype_en'} = 'debit';
		}
		$va{'last4dig'} = substr($cses{'pmtfield3'},-4);
	}
	## Pmt Type
	if( $cses{'pay_type'} eq 'cc' ){		
		$cses{'order_ptype'} = 'Credit-Card';
	}elsif( $cses{'pay_type'} eq 'rd' ){
		$cses{'order_ptype'} = 'Referenced Deposit';
	}elsif( $cses{'pay_type'} eq 'cod' ){
		$cses{'order_ptype'} = 'COD';
		$in{'shp_type'} = 3 if( !$in{'shp_type'} );
	}

	### Products list
	if( $in{'products'} and $in{'products'} ne '' ){	
		$va{'shop_cart_products'} = $in{'products'};
		$cses{'shop_cart_products'} = $va{'shop_cart_products'};
	}elsif( $cses{'shop_cart_products'} and $cses{'shop_cart_products'} ne '' ){
		$va{'shop_cart_products'} = $cses{'shop_cart_products'};
	}

	### Verifica la disponibilidad del envio express para los productos
	&express_delivery_products();

	### Verifica la disponibilidad del envio express en la zona actual
	if( $cses{'zipcode'} ne $cses{'shp_zipcode'} ){
		&express_delivery_zones($cses{'shp_zipcode'});
	}

	$va{'shipping_amt'} = $in{'shipping'};
	### Shipping Info
	$cses{'shp_type'} = ($in{'shp_type'}) ? $in{'shp_type'} : 1;
	if( $cses{'shp_type'} == 2 and ($cses{'zones_express_delivery'} eq 'No' or $cses{'products_express_delivery'} eq 'No') ){
		$cses{'shp_type'} = ( $cses{'pay_type'} eq 'cod' ) ? 3 : 1;
		$va{'shp_type'} = $cses{'shp_type'};
		$va{'shipping_amt'} = $cfg{'shipment_'.$cses{'pay_type'}.'_standard'};
	}

	$va{'shp_type'} = $cses{'shp_type'};
	if( $va{'shp_type'} == 1 or $va{'shp_type'} == 3 ){
		$va{'html_delivery_types'} = '<a href="#" id="lnk_delivery_standard" class="lnk_delivery_types_on" title="Este env&iacute;o es por tierra" data-type="1" data-descrip="Standard" data-cost="'.$cfg{'shipment_'.$cses{'pay_type'}.'_standard'}.'">
										  <img src="/sitimages/sales/delivery_1_blue.png" class="ico"  width="36px">Standard
									  </a>';
	}else{
		my $this_shp_type = ( $cses{'pay_type'} eq 'cod' ) ? 3 : 1;
		$va{'html_delivery_types'} = '<a href="#" id="lnk_delivery_standard" class="lnk_delivery_types_off" title="Este env&iacute;o es por tierra" data-type="'.$this_shp_type.'" data-descrip="Standard" data-cost="'.$cfg{'shipment_'.$cses{'pay_type'}.'_standard'}.'">
										  <img src="/sitimages/sales/delivery_1_blue.png" class="ico"  width="36px">Standard
									  </a>';
	}
	if( $cses{'zones_express_delivery'} eq 'Yes' and $va{'shp_type'} != 2 and $cses{'products_express_delivery'} eq 'Yes' ){
		$va{'html_delivery_types'} .= '&nbsp;<a href="#" id="lnk_delivery_express" class="lnk_delivery_types_off" title="Este env&iacute;o es el mismo d&iacute;a" data-type="2" data-descrip="Express" data-cost="'.$cfg{'shipment_'.$cses{'pay_type'}.'_express'}.'">
										  <img src="/sitimages/sales/delivery_2_blue.png" class="ico"  width="36px">Express
									  </a>';
	}elsif( $va{'shp_type'} == 2 and $cses{'products_express_delivery'} eq 'Yes' ){
		$va{'html_delivery_types'} .= '&nbsp;<a href="#" id="lnk_delivery_express" class="lnk_delivery_types_on" title="Este env&iacute;o es el mismo d&iacute;a" data-type="2" data-descrip="Express" data-cost="'.$cfg{'shipment_'.$cses{'pay_type'}.'_express'}.'">
											<img src="/sitimages/sales/delivery_2_blue.png" class="ico"  width="36px">Express
									   </a>';
	}

	### Totales
	$va{'order_totalnet'}	= 0;
	$va{'order_discount'}	= 0;
	$va{'order_taxes'}		= 0;
	$va{'order_shipping'}	= 0;
	$va{'order_total'}		= 0;
	delete($cses{'order_products_list'});
	delete($cses{'order_totalnet'});
	delete($cses{'order_qty'});
	delete($cses{'order_discount'});
	delete($cses{'order_taxes'});
	delete($cses{'order_shipping'});


	$va{'list_products_shop_cart'} = '';
	if( $va{'shop_cart_products'} ){
		&products_order_list();
	}

	### Coupon / Discount
	$cses{'coupon'} = ($in{'coupon'} and !$cses{'coupon'}) ? $in{'coupon'} : $cses{'coupon'};
	$va{'coupon'} = $cses{'coupon'};
	$va{'type_input_coupon'} = ( $cfg{'coupon_hide'} and $cfg{'coupon_hide'} == 1 ) ? 'password' : 'text';

	### Folio Promoción
	

	### Se calculan los subotales y el total de la orden
	&order_totals();

	### Costo de envio gratis
	$va{'lnk_drop_shipping'} = '<a href="#"><img src="/sitimages/default/b_drop.png" alt="X" style="border: none; height: 14px; width: 14px;"/></a>';

	### Datos de la tarjeta
	if( $in{'month'} and $in{'year'} ){
		$in{'pmtfield4'} = $in{'month'}.'/'.$in{'year'};
	}


	# Date	
	my ($y, $m, $d) = Date::Calc::Today();
	($y, $m, $d) = Add_Delta_Days($y, $m, $d, 1);
	$va{'curdate'} = sprintf('%02d-%02d-%02d', $y, $m, $d);

	### CC->MSI
	$cses{'total_pmts'} = $in{'total_pmts'};
	$va{'total_pmts'} = $cses{'total_pmts'};
	$cses{'fpdays'} = 1;
	if( $va{'total_pmts'} > 1 ){
		$cses{'fpdays'} = 30; # Dias entre cada pago

		$va{'fpdays_html'} = '<tr>
								  <td colspan="7" align="right">LEER LAS FECHAS DE PAGO AL CLIENTE.<BR>
								  			SON CADA '.$cses{'fpdays'}.' DIAS.<br>
								  			<span style="color: #B40404;">Los pagos atrasados tienen un recargo.</span></td>
								</tr>';

		&fpays_order_list();
		$va{'pmts_list_html'} = '<tr>
								  <td id="td_order_pays_list" colspan="7" align="right">'.$va{'pays_list'}.'</td>
								</tr>';
	}
	$va{'fpdays'} = $cses{'fpdays'};

	$cses{'pmtfield4'} = $cses{'cc_month'}.$cses{'cc_year'};
	$va{'pmtfield4'} = $cses{'pmtfield4'};

	### PostDate	
	if( $cfg{'postdatedbutton'} and $cfg{'postdatedbutton'} == 1 and $cses{'pay_type'} ne 'rd' ){
		$va{'id_postdate'}		= ($cfg{'postdatedfeid'}) ? $cfg{'postdatedfeid'} : 0;
		$va{'postdatedmaxdays'}	= ($cfg{'postdateddays'}) ? $cfg{'postdateddays'} : 0;
		$va{'postdatedfesprice'}= ($cfg{'postdatedfesprice'}) ? $cfg{'postdatedfesprice'} : 0;
		$va{'descrip_postdate'} = &load_name('sl_services', 'ID_services', $va{'id_postdate'}, 'Name') if($va{'id_postdate'} != 0);

		my $title_btn_postdate = '';
		if( $cses{'pay_type'} eq 'cod' ){
			$title_btn_postdate = 'Reprogramar el env&iacute;o de la orden';
			$legend_postdate = 'Reprogramar';
		}elsif( $cses{'pay_type'} eq 'cc' ){
			$title_btn_postdate = 'Posfechar el cobro de la orden';
			$legend_postdate = 'Posfechar';
		}
		$va{'html_postdate'} = '<a href="#" id="lnk_postdate" class="lnk_button_icon" title="'.$title_btn_postdate.'" 
									data-id="'.$va{'id_postdate'}.'" 
									data-maxdays="'.$va{'postdatedmaxdays'}.'" 
									data-price="'.$va{'postdatedfesprice'}.'" 
									data-tax_pct="0" 
									data-name="'.$va{'descrip_postdate'}.'">
									<img src="/sitimages/sales/postdate.png" class="ico" style="height: 25px; width: 25px;">
									'.$legend_postdate.'
								</a>';
	}	

	## Speech Code
	$va{'speech_code'} = 'ccinbound:'.$va{'step'}.'-Order Confirm';
}

##################################################################
############ Step 6 :: Info. Extra
##################################################################
sub admin_console_step6{

	### Products list
	if( $in{'products'} and $in{'products'} ne '' ){	
		$va{'shop_cart_products'} = $in{'products'};
		$cses{'shop_cart_products'} = $va{'shop_cart_products'};
	}elsif( $cses{'shop_cart_products'} and $cses{'shop_cart_products'} ne '' ){
		$va{'shop_cart_products'} = $cses{'shop_cart_products'};
	}

	### Validacion adicional del Tax
	$cses{'taxes'} = &calculate_taxes($cses{'zipcode'},'','',0) if(!$cses{'taxes'});

	delete($cses{'order_products_list'});
	$va{'list_products_shop_cart'} = '';
	&products_order_list();

	$cses{'coupon'} = $in{'coupon'};
	if( $cses{'order_discount'} and $cses{'order_discount'} ne '' and $cses{'coupon'} eq '' ){
		$cses{'order_discount'} = 0;
		$va{'order_discount'} = 0;
	}

	### Posfecha
	if( $in{'postdate'} ){
		$va{'postdate'} = $in{'postdate'};
	}

	### Se calculan los subotales y el total de la orden
	&order_totals();

	&create_orders();

	###-------------------------------------------------------
	### Validación adicional para solucionar los casos en los que se pierde la orden y el cliente
	###-------------------------------------------------------
	my $sql_val = "SELECT ID_orders FROM sl_orders WHERE ID_orders = ".$cses{'id_orders'}.";";
	my $sth_val = &Do_SQL($sql_val);
	my $new_id_orders = $sth_val->fetchrow();
	if( !$new_id_orders ){

		my $from_email = $cfg{'from_email'};
		my $to_email = 'gquirino@inovaus.com';
		my $subject = 'New Sales - Order Error '.$cses{'id_orders'};

		if( $cses{'order_status'} and $cses{'order_status'} eq 'Processed' and $cses{'pay_type'} eq 'cc' ){
			my $body = 'Error en la orden '.$cses{'id_orders'};
			&send_mandrillapp_email_attachment($from_email, $to_email, $subject, $body, 'none', 'none');
		}else{
			$cses{'old_id_orders'} = $cses{'id_orders'};
			delete($cses{'id_orders'});
			delete($cses{'id_customers'}) if( $cses{'repeatedcustomer'} eq 'No' );
			&create_orders();

			$subject = 'New Sales - Order Alert '.$cses{'old_id_orders'};
			my $body = 'Error en la orden '.$cses{'old_id_orders'}.'.<br />Se generó una nueva orden: '.$cses{'id_orders'};
			&send_mandrillapp_email_attachment($from_email, $to_email, $subject, $body, 'none', 'none');
		}

	}
	###-------------------------------------------------------

	$va{'order_ftotal'} = &format_price($va{'order_total'});

	### Datos iniciales de facturación
	$va{'invoice_country'} = uc($cfg{'acc_default_country'}) if( $cfg{'acc_default_country'} );
	# Si el cliente ya existe y cuenta con datos de facturación
	if( $cses{'repeatedcustomer'} eq 'Yes' ){
		my $sql = "SELECT cu_customers_addresses.Alias 
						, cu_customers_addresses.cu_Street
						, cu_customers_addresses.cu_Num
						, cu_customers_addresses.cu_Num2
						, cu_customers_addresses.cu_Urbanization
						, cu_customers_addresses.cu_District
						, cu_customers_addresses.cu_City
						, cu_customers_addresses.cu_State
						, cu_customers_addresses.cu_Country
						, cu_customers_addresses.cu_Zip
						, sl_customers.RFC
					FROM sl_customers
						INNER JOIN cu_customers_addresses ON sl_customers.ID_customers = cu_customers_addresses.ID_customers
					WHERE sl_customers.ID_customers = ".$cses{'id_customers'}." 
						AND cu_customers_addresses.Status = 'Active' 
						AND cu_customers_addresses.PrimaryRecord = 'Yes'
					ORDER BY cu_customers_addresses.ID_customers_addresses DESC
					LIMIT 1;";
		my $sth_cust = &Do_SQL($sql);
		my $rec_cust = $sth_cust->fetchrow_hashref();

		$va{'invoice_rfc'}			= $rec_cust->{'RFC'};
		$va{'invoice_name'}			= $rec_cust->{'Alias'};
		$va{'invoice_street'}		= $rec_cust->{'cu_Street'};
		$va{'invoice_noext'}		= $rec_cust->{'cu_Num'};
		$va{'invoice_noint'}		= $rec_cust->{'cu_Num2'};
		$va{'invoice_urbanization'}	= $rec_cust->{'cu_Urbanization'};
		$va{'invoice_distrit'}		= $rec_cust->{'cu_District'};
		$va{'invoice_city'}			= $rec_cust->{'cu_City'};
		$va{'invoice_state'}		= $rec_cust->{'cu_State'};
		$va{'invoice_country'}		= $rec_cust->{'cu_Country'};
		$va{'invoice_zipcode'}		= $rec_cust->{'cu_Zip'};
	}

	### Se asigna el código de autorización
	$va{'auth_code'} = $cses{'auth_code'};

	### Prefix
	$va{'order_prefix'} = $cfg{'prefixentershipment'};

	## Speech Code
	$va{'speech_code'} = 'ccinbound:'.$va{'step'}.'-Order Finish';

	### Envío de Email y/o SMS
	if( $cses{'pay_type'} ne 'cc' ){
		&send_mail_sales($cses{'id_orders'}, 'received');
	}

}

##################################################################
############ Funciones Adicionales
##################################################################
sub get_speech{

	my $sql = '';

	if( $va{'speech_code'} ne '' ){
		my $this_pay_type = uc($va{'pay_type'});

		$sql = "SELECT sl_speech.Name, sl_speech.Speech 
				FROM sl_speech 
				WHERE 1
					AND sl_speech.`Status` = 'Active'
					AND sl_speech.`Type` = 'ccinbound:Console Sales V2'
					AND (sl_speech.Name = '".$va{'speech_code'}."' OR sl_speech.Name = '".$va{'speech_code'}.' '.$this_pay_type."');";
		my $sth = &Do_SQL($sql);
		while( my $rec = $sth->fetchrow_hashref() ){
			$va{'speech_content'} .= $rec->{'Speech'};			
		}
	}

}

sub express_delivery_zones{

	my ($zipcode) = @_;

	$sql = "SELECT 
				sl_zones.Name
				, sl_zones.Payment_Type
				, sl_zones.ExpressShipping
			FROM sl_zipcodes
				INNER JOIN sl_zones USING(ID_zones)
			WHERE 1
				AND sl_zipcodes.ZipCode='".$zipcode."' 
				AND sl_zipcodes.`Status` = 'Active' 
				AND sl_zones.`Status` = 'Active';";
	my $sth_zone = &Do_SQL($sql);
	my $data_zone = $sth_zone->fetchrow_hashref();

	$va{'pay_type_available'}	= $data_zone->{'Payment_Type'};
	$va{'zones_express_delivery'}	= $data_zone->{'ExpressShipping'};
	$cses{'pay_type_available'}	= $va{'pay_type_available'};
	$cses{'zones_express_delivery'}	= $va{'zones_express_delivery'};
}

sub express_delivery_products{

	if( $va{'shop_cart_products'} and $va{'shop_cart_products'} ne '' and $cses{'pay_type'} ne 'rd' ){

		### Si el envio express está disponible para la zona<->código postal
		#if( $cses{'zones_express_delivery'} eq 'Yes' ){
			### Se valida que todos los productos de la orden tengan envío express
			my $products = '';
			my @products_info = split(/\;/, substr($va{'shop_cart_products'}, 0, -1));
			foreach my $i (0 .. $#products_info){
				my @this_info = split(/\:/,$products_info[$i]);
				$products .= $this_info[0].',';
			}
			$products = substr($products, 0, -1);

			my $sql = "SELECT ExpressShipping
						FROM sl_products							
						WHERE ID_products IN(".$products.");";
			my $sth = &Do_SQL($sql);
			my $express = 'Yes';
			while( my $rec = $sth->fetchrow_hashref() ){
				if( uc($rec->{'ExpressShipping'}) eq 'NO' ){
					$express = 'No';
					last;
				}
			}
			$cses{'products_express_delivery'} = $express;

		# }else{
		# 	$cses{'products_express_delivery'} = 'No';
		# }

		$va{'products_express_delivery'} = ($cses{'products_express_delivery'}) ? $cses{'products_express_delivery'} : 'No';

	}else{
		$cses{'products_express_delivery'} = 'No';
		$va{'products_express_delivery'}	= $cses{'products_express_delivery'};
	}
}

sub products_order_list{

	my $products = substr($cses{'shop_cart_products'}, 0, -1);
	my @products_info = split(/\;/,$products);

	$va{'totalnet_serv'} = 0;
	$va{'totaltax_serv'} = 0;
	$va{'order_qty'} = 0;

	my $old_id_prod = 0;
	foreach my $i (0 .. $#products_info){
		my @this_info = split(/\:/,$products_info[$i]);

		my $price_net = 0;
		if( int($this_info[5]) == 1 ){

			my $is_product = 1;
			my $img_prod = '&nbsp;';
			my $label_item = 'Product ID: ';
			my $sql = "";
			### Products
			if( int($this_info[1]) < 200000000 ){
				$sql = "SELECT ID_products, Model, Name, free_shp_opt
						FROM sl_products
						WHERE ID_products=".int($this_info[0]).";";
			### Services
			}elsif( int($this_info[1]) > 600000000 ){
				$sql = "SELECT ID_services AS ID_products, Name AS Model
						FROM sl_services
						WHERE ID_services=".int($this_info[0]).";";
				$is_product = 0;
				$label_item = 'Service ID: ';
				$va{'totalnet_serv'} += round($this_info[2] / (1 + $this_info[3]), 2);
				$va{'totaltax_serv'} += round($this_info[2] * $this_info[3], 2);
			}
			my $sth_prod = &Do_SQL($sql);
			my $rec_prod = $sth_prod->fetchrow_hashref();

			my $lnk_drop_serv = '';
			### Is Product			
			if( $is_product == 1 ){
				$img_prod = '<img src="/sitimages/sales/prod/'.$rec_prod->{'ID_products'}.'.jpg" onerror="this.onerror=null;this.src=\'/sitimages/sales/prod/none.jpg\';" style="border: 1px solid silver; width: 70px; float: left; margin-right: 15px">';
			### Other item type
			}else{
				$lnk_drop_serv = '&nbsp;<a href="#" id="lnk_drop-'.$rec_prod->{'ID_products'}.'-'.$this_info[6].'" data-id="'.$rec_prod->{'ID_products'}.'" data-parent="'.$this_info[6].'" class="lnk_drop_services" title="Cancelar este servicio"><img src="/sitimages/default/b_drop.png" alt="X" class="ico" style="border: none; height: 14px; width: 14px;"/></a>';
			}
			$va{'list_products_shop_cart'} .= '<tr id="tr_'.$rec_prod->{'ID_products'}.'_'.$this_info[6].'">
												<td style="border-bottom: 1px solid silver; width: 70px; vertical-align: top;"> 
													'.$img_prod.'
												</td>
												<td style="border-bottom: 1px solid silver; width: 68%;">
													<span style="font-size: 12pt;">'.$rec_prod->{'Model'}.'</span><br>		
													<span style="display: inline-block; margin-bottom: 7px;">'.$label_item.' '.$rec_prod->{'ID_products'}.'</span>'.$lnk_drop_serv;
			
			### Precios
			$price_net = round($this_info[2] / (1 + $this_info[3]), 2);

			### Si se trata de una promo., se obtienen los productos que la conforman
			if( $this_info[0] ne substr($this_info[1], 3) and $is_product == 1 ){
				my $main_prod = $this_info[6];
				my $this_id = 0;
				my $j = $i;
				do{
					my @this_info2 = split(/\:/,$products_info[$j]);
					$this_id = $this_info2[6];
					if( $main_prod eq $this_id ){
						my $sql = "SELECT sl_products.Model, sl_products.Name, Choice1, Choice2, Choice3, Choice4
									FROM sl_products
										INNER JOIN sl_skus USING(ID_products)
									WHERE ID_sku_products=".int($this_info2[1]).";";
						my $sth_prod2 = &Do_SQL($sql);
						my $rec_prod2 = $sth_prod2->fetchrow_hashref();

						my $choices = '(';
						$choices .= $rec_prod2->{'Choice1'}.':' if( $rec_prod2->{'Choice1'} and $rec_prod2->{'Choice1'} ne $rec_prod2->{'Model'} );
						$choices .= $rec_prod2->{'Choice2'}.':' if( $rec_prod2->{'Choice2'} and $rec_prod2->{'Choice2'} ne $rec_prod2->{'Model'} );
						$choices .= $rec_prod2->{'Choice3'}.':' if( $rec_prod2->{'Choice3'} and $rec_prod2->{'Choice3'} ne $rec_prod2->{'Model'} );
						$choices .= $rec_prod2->{'Choice4'}.':' if( $rec_prod2->{'Choice4'} and $rec_prod2->{'Choice4'} ne $rec_prod2->{'Model'} );
						$choices = substr($choices, 0, -1);
						$choices .= ')' if( $choices ne '' );

						$va{'list_products_shop_cart'} .= '<span style="display: block; margin: 3px 0 3px 10px;">'.$this_info2[1].' - '.$rec_prod2->{'Model'}.' <span class="shop_cart_choices">'.$choices.'</span></span>';
						$va{'list_products_shop_cart'} .= &get_skus_parts($this_info2[1]);

						### Precios
						my @this_info_promo = split(/\:/,$products_info[$j+1]);
						if( $this_info_promo[6] eq $main_prod ){
							$price_net += round($this_info_promo[2] / (1 + $this_info_promo[3]), 2);
						}
					}
					++$j;
				}while($main_prod eq $this_id and $j<100);
			} else {
				my $this_id_products = (int($rec_prod->{'ID_products'}) < 100000000) ? (100000000+$rec_prod->{'ID_products'}) : $rec_prod->{'ID_products'};
				$va{'list_products_shop_cart'} .= &get_skus_parts($this_id_products);
			}

			$va{'list_products_shop_cart'} .= '</td>
												<td align="center" style="border-bottom: 1px solid silver; vertical-align: top;">'.$this_info[4].'</td>
												<td align="right" style="border-bottom: 1px solid silver; vertical-align: top;">'.&format_price($price_net).'</td>
											</tr>';
		}

		### Se genera el listado de productos
		$cses{'order_products_list'} .= $this_info[1].',';

		### Sumatoria del totalnet de la orden
		$va{'order_totalnet'} += $price_net;
		++$va{'order_qty'};

		$old_id_prod = int($this_info[0]);
		
	}#foreach
}

sub get_skus_parts{
	my ($id_products) = @_;
	my $html_skus_parts = '';

	my $sth = &Do_SQL("SELECT ID_parts, Qty FROM sl_skus_parts WHERE ID_sku_products=".int($id_products).";");
	while( my $rec = $sth->fetchrow_hashref() ){
		
		for my $i(1..$rec->{'Qty'}){
			my $sth_part = &Do_SQL("SELECT Model, Name FROM sl_parts WHERE ID_parts = ".int($rec->{'ID_parts'}).";");
			my $part = $sth_part->fetchrow_hashref();
			if( $part->{'Model'} ){
				$html_skus_parts .= '<span style="color: #848484; display: block; font-size: 7.5pt; font-weight: bold; margin-left: 25px;"><img src="/sitimages/'.$usr{'pref_style'}.'/tri.gif">&nbsp;'.&format_sltvid(400000000+$rec->{'ID_parts'}).' &nbsp; '.$part->{'Model'}.' :: '.$part->{'Name'}.'</span>';
			}
		}

	}

	return $html_skus_parts;
}

sub fpays_order_list{

	# Date	
	my ($y, $m, $d) = Date::Calc::Today();
	($y, $m, $d) = Add_Delta_Days($y, $m, $d, 1);
	$va{'curdate'} = sprintf('%02d-%02d-%02d', $y, $m, $d);

	### Se obtiene el monto de cada pago
	my $pmts_amount = round(($va{'order_totalnet'} - $va{'order_discount'} - $va{'totalnet_serv'}) / $cses{'total_pmts'}, 2);
	$va{'pmts_amount'} = $pmts_amount;
	### Se calcula el monto del primer pago
	$va{'order_first_pmt'} = $pmts_amount + $va{'order_taxes'} + $va{'order_shipping'} + ($va{'totalnet_serv'} + $va{'totaltax_serv'});
	$va{'order_ffirst_pmt'} = &format_price($va{'order_first_pmt'});
	### Se obtiene el listado del resto de los pagos			
	for my $i(1 .. int($cses{'total_pmts'}) - 1){
		#my $new_date = $curdate->add( days => $cses{'fpdays'} )->ymd('-'); # 'aaaa-mm-dd'
		($y, $m, $d) = Add_Delta_Days($y, $m, $d, $cses{'fpdays'});
		my $new_date = sprintf('%02d-%02d-%02d', $y, $m, $d);
		$va{'pays_list'} .= '<span id="fpmt-'.$i.'" data-value="'.$pmts_amount.'">'.&format_price($pmts_amount).'</span> &nbsp;&#64;&nbsp; '.$new_date.'<br />';
	}

}


sub order_totals{
	## Subtotal
	$va{'order_ftotalnet'} = &format_price($va{'order_totalnet'});

	## Shipping
	$va{'order_shipping'} = ($in{'shipping'}) ? $in{'shipping'} : 0;
	$va{'order_fshipping'} = &format_price($va{'order_shipping'});
	$cses{'order_shipping'} = $va{'order_shipping'};

	## Descuentos
	$va{'order_discount'} = 0;
	$va{'disc_applied'} = '';
	if( $cses{'coupon'} and $cses{'coupon'} ne '' ){
		my ($sth) = &Do_SQL("SELECT * FROM sl_coupons WHERE PublicID='".$cses{'coupon'}."' AND Status='Active' AND (ValidFrom <= CURDATE() AND ValidTo >= CURDATE())");
		$rec = $sth->fetchrow_hashref();
		$va{'disc_applied'} = $rec->{'Applied'};
		if( $rec->{'Applied'} eq 'Net' ){
			if( $rec->{'DiscPerc'} ){
				$va{'order_discount'} = round($va{'order_totalnet'} * ($rec->{'DiscPerc'} / 100), 2);
			}else{
				$va{'order_discount'} = ( $va{'order_totalnet'} >= $rec->{'DiscValue'} ) ? $rec->{'DiscValue'} : $va{'order_totalnet'};
			}
		}elsif( $rec->{'Applied'} eq 'Gross' ){
			my $this_order_tax = round(($va{'order_totalnet'} * $cses{'taxes'}), 2);# + ($va{'order_shipping'} * $cses{'taxes'}), 2);
			my $this_order_total = $va{'order_totalnet'}  + $this_order_tax;# + $va{'order_shipping'};
			if( $rec->{'DiscPerc'} ){
				$va{'order_discount'} = round($this_order_total * ($rec->{'DiscPerc'} / 100), 2);
			}else{
				$va{'order_discount'} = ( $this_order_total >= $rec->{'DiscValue'} ) ? $rec->{'DiscValue'} : $this_order_total;
			}
		}
		$cses{'order_discount'} = $va{'order_discount'};
	}
	$va{'order_fdiscount'} = &format_price($va{'order_discount'});

	## Taxes
	$va{'ftaxes'} = $cses{'taxes'} * 100;
	if( !$cses{'coupon'} or ($cses{'coupon'} and $cses{'coupon'} ne '' and $va{'disc_applied'} eq 'Net') ){
		$va{'order_taxes'} = round((($va{'order_totalnet'} - $va{'order_discount'}) * $cses{'taxes'}) + ($va{'order_shipping'} * $cses{'taxes'}), 2);
	}elsif( $cses{'coupon'} and $cses{'coupon'} ne '' and $va{'disc_applied'} eq 'Gross' ){
		$va{'order_taxes'} = round(($va{'order_totalnet'} * $cses{'taxes'}) + ($va{'order_shipping'} * $cses{'taxes'}), 2);
	}
	$va{'order_ftaxes'} = &format_price($va{'order_taxes'});

	## Total General
	$va{'order_total'} = ($va{'order_totalnet'} - $va{'order_discount'}) + $va{'order_taxes'} + $va{'order_shipping'};
	$va{'order_ftotal'} = &format_price($va{'order_total'});
	$va{'order_first_pmt'} = $va{'order_total'};
	$va{'order_ffirst_pmt'} = &format_price($va{'order_first_pmt'});
}


sub create_orders{

	&Do_SQL("START TRANSACTION;");

	### ---------------------------------------------
	### Se crea o actualiza el cliente
	### ---------------------------------------------
	&create_customers();


	### ---------------------------------------------
	### Se obtiene los datos necesarios para la orden
	### ---------------------------------------------	
	### Zones
	my ($sth_zip)=&Do_SQL("SELECT DISTINCT ID_zones FROM sl_zipcodes WHERE ZipCode = '".$cses{'shp_zipcode'}."' LIMIT 1;");
	$va{'id_zones'} = $sth_zip->fetchrow();
	### Extra. info
	$va{'id_pricelevels'} = 1;
	$va{'pterms'} = 'CONTADO';
	$va{'language'} = 'spanish';
	$va{'status_prd'} = 'None';
	$va{'status_pay'} = 'None';
	$va{'dayspay'} = 1;

	### Se obtiene el ID del cupon
	$va{'id_coupons'} = 0;
	if( $cses{'coupon'} ){
		my $sql = "SELECT ID_coupons, Applied, DiscPerc, DiscValue FROM sl_coupons WHERE PublicID = '".$cses{'coupon'}."';";
		my $sth = &Do_SQL($sql);
		($va{'id_coupons'}, $va{'disc_applied'}, $va{'disc_perc'}, $va{'disc_value'}) = $sth->fetchrow();
	}

	### Validacion adicional del Tax
	$cses{'taxes'} = &calculate_taxes($cses{'zipcode'},'','',0) if(!$cses{'taxes'});
	$va{'order_taxes'} = (!$cses{'taxes'} and $cfg{'taxp_default'}) ? $cfg{'taxp_default'} : $cses{'taxes'};
	
	### ---------------------------------------------
	### Creación o actualización de la orden
	### ---------------------------------------------
	my $sql = "";
	my $oper = 'Insert';
	if( $cses{'id_orders'} ){
		my $sql_status = ( $cses{'pay_type'} ne 'cc' ) ? ", Status = 'New'" : "";

		$sql = "UPDATE sl_orders SET 
					ID_customers = ".$cses{'id_customers'}."
					, Address1 = UPPER('".&filter_values($cses{'address1'})."')
					, Address2 = UPPER('".&filter_values($cses{'address2'})."')
					, Address3 = UPPER('".&filter_values($cses{'address3'})."')
					, Urbanization = UPPER('".&filter_values($cses{'urbanization'})."')
					, City = UPPER('".$cses{'city'}."')
					, State = '".$cses{'state'}."'
					, Zip = '".$cses{'zipcode'}."'
					, Country = 'MEXICO'
					, BillingNotes = UPPER('".&filter_values($cses{'billingnotes'})."')
					, shp_type = '".$cses{'shp_type'}."'
					, shp_name = UPPER('".&filter_values($cses{'shp_name'})."')
					, shp_Address1 = UPPER('".&filter_values($cses{'shp_address1'})."')
					, shp_Address2 = UPPER('".&filter_values($cses{'shp_address2'})."')
					, shp_Address3 = UPPER('".&filter_values($cses{'shp_address3'})."')
					, shp_Urbanization = UPPER('".&filter_values($cses{'shp_urbanization'})."')
					, shp_City = UPPER('".$cses{'shp_city'}."')
					, shp_State = '".$cses{'shp_state'}."'
					, shp_Zip = '".$cses{'shp_zipcode'}."'
					, shp_Country = 'MX'
					, shp_Notes = UPPER('".&filter_values($cses{'shp_notes'})."')
					, ID_zones = '".$va{'id_zones'}."'
					, OrderNotes = '".&filter_values($va{'orders_notes'})."'
					, OrderQty = ".int($va{'order_qty'})."
					, OrderShp = ".$va{'order_shipping'}."
					, OrderDisc = ".$va{'order_discount'}."
					, OrderTax = ".$va{'order_taxes'}."
					, OrderNet = ".$va{'order_totalnet'}."
					, PostedDate = NULL
					, ID_pricelevels = ".int($va{'id_pricelevels'})."
					, dayspay = ".$va{'dayspay'}."
					, ID_orders_related = '0'
					, repeatedcustomer = '".$cses{'repeatedcustomer'}."'
					, Coupon = ".int($va{'id_coupons'})."
					, ID_salesorigins = '".$cses{'id_salesorigins'}."'
					, Ptype = '".$cses{'order_ptype'}."'
					, Pterms = '".$va{'pterms'}."'
					, language = '".$va{'language'}."'
					/*, StatusPrd = '".$va{'status_prd'}."'
					, StatusPay = '".$va{'status_pay'}."'*/ 
					".$sql_status."
				WHERE ID_orders = ".$cses{'id_orders'}.";";
		$oper = 'Update';

	}else{
		$sql = "INSERT INTO sl_orders SET 
					ID_customers = ".$cses{'id_customers'}."
					, Address1 = UPPER('".&filter_values($cses{'address1'})."')
					, Address2 = UPPER('".&filter_values($cses{'address2'})."')
					, Address3 = UPPER('".&filter_values($cses{'address3'})."')
					, Urbanization = UPPER('".&filter_values($cses{'urbanization'})."')
					, City = UPPER('".$cses{'city'}."')
					, State = '".$cses{'state'}."'
					, Zip = '".$cses{'zipcode'}."'
					, Country = 'MEXICO'
					, BillingNotes = UPPER('".&filter_values($cses{'billingnotes'})."')
					, shp_type = '".$cses{'shp_type'}."'
					, shp_name = UPPER('".&filter_values($cses{'shp_name'})."')
					, shp_Address1 = UPPER('".&filter_values($cses{'shp_address1'})."')
					, shp_Address2 = UPPER('".&filter_values($cses{'shp_address2'})."')
					, shp_Address3 = UPPER('".&filter_values($cses{'shp_address3'})."')
					, shp_Urbanization = UPPER('".&filter_values($cses{'shp_urbanization'})."')
					, shp_City = UPPER('".$cses{'shp_city'}."')
					, shp_State = '".$cses{'shp_state'}."'
					, shp_Zip = '".$cses{'shp_zipcode'}."'
					, shp_Country = 'MX'
					, shp_Notes = '".&filter_values($cses{'shp_notes'})."'
					, ID_zones = '".$va{'id_zones'}."'
					, OrderNotes = '".&filter_values($va{'orders_notes'})."'
					, OrderQty = ".int($va{'order_qty'})."
					, OrderShp = ".$va{'order_shipping'}."
					, OrderDisc = ".$va{'order_discount'}."
					, OrderTax = ".$va{'order_taxes'}."
					, OrderNet = ".$va{'order_totalnet'}."
					, PostedDate = NULL
					, ID_pricelevels = ".int($va{'id_pricelevels'})."
					, dayspay = ".$va{'dayspay'}."
					, ID_orders_related = '0'
					, repeatedcustomer = '".$cses{'repeatedcustomer'}."'
					, Coupon = ".int($va{'id_coupons'})."
					, ID_salesorigins = '".$cses{'id_salesorigins'}."'
					, Ptype = '".$cses{'order_ptype'}."'
					, Pterms = '".$va{'pterms'}."'
					, language = '".$va{'language'}."'
					, StatusPrd = '".$va{'status_prd'}."'
					, StatusPay = '".$va{'status_pay'}."'
					, Status = 'New'
					, Date = CURDATE()
					, Time = CURTIME()
					, ID_admin_users = ".$usr{'id_admin_users'}."
				;";
		
	}
	$cses{'sql_orders'} .= $sql;
	$cses{'sql_orders'} =~ s/\n/ /g;

	$sth = &Do_SQL($sql);
	$cses{'id_orders'} = ( !$cses{'id_orders'} ) ? $sth->{'mysql_insertid'} : $cses{'id_orders'};
	if( $oper eq 'Insert' ){
		## Logs
		$in{'db'} = 'sl_orders';
		&auth_logging('opr_orders_added', $cses{'id_orders'});
	}

	### Coupon
	if( $cses{'coupon'} and int($va{'id_coupons'}) > 0 ){
		&Do_SQL("DELETE FROM sl_coupons_trans WHERE ID_coupons=".$va{'id_coupons'}." AND ID_orders=".$cses{'id_orders'}.";");
		&Do_SQL("INSERT INTO sl_coupons_trans SET 
					ID_coupons=".$va{'id_coupons'}."
					, ID_orders=".$cses{'id_orders'}."
					, Date=CURDATE()
					, Time=CURTIME()
					, ID_admin_users=".$usr{'id_admin_users'}.";");
	}

	### Promotions
	if( $cses{'folio_promo'} and $cses{'folio_promo'} ne '' and int($cses{'folio_valid'}) > 0 and int($cses{'promos_mow'}) == 1 and int($cses{'id_customers_promo'}) == 0 ){
		&Do_SQL("UPDATE cu_customer_promotions_mow SET 
					ID_orders = ".$cses{'id_orders'}."
				 WHERE ID_customers_promotions = ".int($cses{'folio_valid'})." 
				 	AND Unique_code = '".$cses{'folio_promo'}."';");
	} elsif( $cses{'folio_promo'} and $cses{'folio_promo'} ne '' and int($cses{'folio_valid'}) > 0 ){
		&Do_SQL("UPDATE cu_customer_promotions SET 
					ID_orders = ".$cses{'id_orders'}."
				 WHERE ID_promotions = ".int($cses{'folio_valid'})." 
				 	AND ID_customers = ".int($cses{'id_customers_promo'})."
				 	AND Unique_code = '".$cses{'folio_promo'}."';");
	}

	### Productos
	&create_products();

	### Payments
	&create_payments();

	$va{'id_orders'} = $cses{'id_orders'};

	### Log Order Status
	&status_logging($va{'id_orders'},'New');

	&Do_SQL("COMMIT;");
}

sub create_products{

	if( $cses{'order_status'} and $cses{'order_status'} eq 'Processed' ){
		return;
	}

	$cses{'sql_products'} = '';
	### Se eliminan los productos de esta orden
	&Do_SQL("DELETE FROM sl_orders_products WHERE ID_orders = ".$cses{'id_orders'}.";");
	$cses{'sql_products'} = "DELETE FROM sl_orders_products WHERE ID_orders = ".$cses{'id_orders'}.";\n";

	$va{'order_totalnet'} = 0;
	$va{'order_taxes'} = 0;
	
	my $products = substr($cses{'shop_cart_products'}, 0, -1);
	my @products_info = split(/\;/,$products);

	my $discount_res = 0;#Contendrá el resto del descuento cuando se aplique a varios productos
	my $total_order_amt = 0;
	$cses{'taxes'} = 0;
	foreach my $i (0 .. $#products_info){
		my $upsell = 'Yes';
		my @this_info = split(/\:/,$products_info[$i]);

		my $id_products		= $this_info[0];
		my $id_sku_products = $this_info[1];
		my $related_id_prod = ( $id_products ne substr($id_sku_products, -6) ) ? $id_products : 'NULL';
		my $sale_price		= $this_info[2];
		my $tax_pct			= $this_info[3];
		my $qty				= $this_info[4];

		$cses{'taxes'} = $tax_pct if( $tax_pct > 0 );

		my $this_item_type = 1;#1: Producto, 2: Servicio
		if( int($this_info[1]) < 200000000 ){
			$this_item_type = 1;
		}elsif( int($this_info[1]) >= 600000000 ){
			$this_item_type = 2;
		}

		### Cálculo de montos netos y taxes
		my $sale_price_net	= round($sale_price / (1 + $tax_pct), 2);
		$va{'order_totalnet'} += $sale_price_net;
		##-------------------------
		## Descuentos
		##-------------------------
		if( $va{'disc_applied'} eq 'Gross' ){
			$cses{'order_discount'} = $cses{'order_discount'} / (1+$tax_pct);
		}
		$discount_res = $cses{'order_discount'} if( $i == 0 );
		my $this_discount = 0;
		if( $discount_res > 0 ){
			if( $discount_res > $sale_price_net ){
				$this_discount = $sale_price_net;
				$discount_res -= $sale_price_net;
			}else{
				$this_discount = $discount_res;
				$discount_res = 0;
			}
		}
		##-------------------------
		#my $products_tax	= ( $va{'disc_applied'} eq 'Net' ) ? round(($sale_price_net - $this_discount) * $tax_pct, 2) : round(($sale_price - $this_discount) * $tax_pct, 2);
		my $products_tax	= round(($sale_price_net - $this_discount) * $tax_pct, 2);
		my $this_shipping	= 0;
		my $this_shp_tax	= 0;
		my $this_shp_tax_pct= 0.16;
		if( $i == 0 ){
			$this_shipping	= $cses{'order_shipping'};
			$this_shp_tax = round($this_shipping * $this_shp_tax_pct, 2);
			$upsell = 'No';
		}
		$va{'order_taxes'} += $products_tax;

		### Total de la orden
		my $total_price =  round($sale_price_net -  $this_discount + $this_shipping + $products_tax + $this_shp_tax, 2);
		$total_order_amt += $total_price;

		### Se recuperan los valores de las variables en caso de pérdida
		$cses{'order_ptype'} = $in{'pay_type'} if( !$cses{'order_ptype'} and $in{'pay_type'} ne '');
		$cses{'total_pmts'} = $in{'total_pmts'} if( !$cses{'total_pmts'} and $in{'total_pmts'} ne '');
		$cses{'id_salesorigins'} = $in{'id_salesorigins'} if( !$cses{'id_salesorigins'} and $in{'id_salesorigins'} ne '');

		### Se obtiene el ID_products_prices
		if( $this_item_type == 1 ){

			$sql_p = "SELECT ID_products_prices 
					  FROM sl_products_prices 
					  WHERE 1
						AND sl_products_prices.ID_products=".$id_products."
						AND sl_products_prices.PayType='".$cses{'order_ptype'}."'
						AND sl_products_prices.FP=".$cses{'total_pmts'}."
						AND sl_products_prices.Origins LIKE '%|".$cses{'id_salesorigins'}."|%' 
					  LIMIT 1;";
			$sth_p = &Do_SQL($sql_p);
			$id_products_prices = $sth_p->fetchrow();
			$id_products_prices = int($id_products_prices);
		}else{
			$id_products_prices = 'NULL';
		}
		
		### Cero aritmético
		if( $sale_price_net == 0 and $cfg{'arithmetic_zero'} == 1 ){
			$sale_price_net = $cfg{'arithmetic_zero_amt'};
			$this_discount = $cfg{'arithmetic_zero_amt'};
			$va{'order_totalnet'} += $sale_price_net;
			$va{'order_discount'} += $this_discount;
		}

		my $sql = "INSERT INTO sl_orders_products SET 
					ID_orders = ".$cses{'id_orders'}." 
					, ID_packinglist = 0 
					, ID_products = ".$id_sku_products." 
					, Related_ID_products = ".$related_id_prod."
					, ID_products_prices = ".$id_products_prices."
					, Quantity = ".$qty."
					, SalePrice = ".$sale_price_net."
					, Tax = ".$products_tax."
					, Tax_percent = ".$tax_pct."
					, Discount = ".$this_discount."
					, Shipping = ".$this_shipping."
					, ShpTax = ".$this_shp_tax."
					, ShpTax_percent = ".$this_shp_tax_pct."
					, FP = ".$cses{'total_pmts'}."
					, Upsell = '".$upsell."'
					, Date = CURDATE()
					, Time = CURTIME()
					, ID_admin_users = ".$usr{'id_admin_users'}."
					;";
		my $sth = &Do_SQL($sql);
		$sql =~ s/\n/\t/g;
		$cses{'sql_products'} .= $sql."\n";

		
	}#foreach

	my $sql = "UPDATE sl_orders SET 					
					OrderTax = ".$cses{'taxes'}."
					, OrderNet = ".$va{'order_totalnet'}."
					, OrderDisc = ".$va{'order_discount'}."
				WHERE ID_orders = ".$cses{'id_orders'}.";";
	&Do_SQL($sql);
	$sql =~ s/\n/\t/g;
	$cses{'sql_products'} .= $sql."\n";

	$va{'order_total'} = $total_order_amt;
}

sub create_payments{

	if( $cses{'order_status'} and $cses{'order_status'} eq 'Processed' ){
		$va{'pmtfield3_mask'} = $cses{'pmtfield3_mask'} if( $cses{'pmtfield3_mask'} );
		return;
	}

	my $cc_number = '';
	my $cc_date = '';
	my $cc_cvn = '';

	# Date	
	my ($y, $m, $d) = Date::Calc::Today();
	$va{'curdate'} = sprintf('%02d-%02d-%02d', $y, $m, $d);

	$cses{'sql_payments'} = '';
	### Se cancelan los payments de esta orden
	&Do_SQL("UPDATE sl_orders_payments SET `Status` = 'Cancelled' WHERE ID_orders = ".$cses{'id_orders'}." AND (Captured != 'Yes' OR Captured IS NULL);");
	$cses{'sql_payments'} = "UPDATE sl_orders_payments SET `Status` = 'Cancelled' WHERE ID_orders = ".$cses{'id_orders'}.";";
	if( $cses{'pay_type'} eq 'cc' ){
		# Informacion para Puntos Diestel
		$cses{'use_points'} = $in{'activar_puntos'};
		$cses{'used_points'} = $in{'used_points'};
		$cses{'consultas'} = $in{'consultas'};
		$cses{'auth_code_consulta'} = $in{'auth-codes'};
		$cses{'id-transaccion'} = $in{'id-transaccion'};
		$cses{'comision'} = $in{'comision'};

		my $mask = '';
		if( $cfg{'encrypt_cc'} and $cfg{'encrypt_cc'} == 1 ){
			$cc_number = &filter_values($cses{'pmtfield3'});
			$mask = ( length($cc_number) == 16 ) ? 'xxxxxx' : 'xxxxx';
			$va{'pmtfield3'} = substr($cc_number, 0, 6).$mask.substr($cc_number, -4);
			$cc_date = &filter_values($cses{'pmtfield4'});
			$va{'pmtfield4'} = 'xxxx';
			$cc_cvn = &filter_values($cses{'pmtfield5'});
			$va{'pmtfield5'} = ( length($cc_cvn) == 3 ) ? 'xxx' : 'xxxx';
		}
		$cses{'pmtfield3_mask'} = 'xxxxxx'.$mask.substr($cc_number, -4);
		$va{'pmtfield3_mask'} = $cses{'pmtfield3_mask'};

		$cses{'pmtfield8'} = $cses{'total_pmts'};
		$va{'pmtfield8'} = $cses{'pmtfield8'};
	}else{
		$va{'pmtfield1'} = '';
		$va{'pmtfield2'} = '';		
		$va{'pmtfield3'} = '';
		$va{'pmtfield4'} = '';
		$va{'pmtfield5'} = '';
		$va{'pmtfield6'} = '';
		$va{'pmtfield7'} = '';
		$va{'pmtfield8'} = '';
		$va{'pmtfield9'} = '';
		$va{'pmtfield10'} = '';
		$va{'pmtfield11'} = '';

		if( $cses{'pay_type'} eq 'rd' ){
			$va{'pmtfield3'} = &ref_banco_azteca($cses{'id_orders'});
			$va{'ref_banco_azteca'} = $va{'pmtfield3'};
		}
	}

	my $sql_postdate = '';
	if( $cses{'postdated'} eq 'Yes' and $cses{'postdated_date'} ){
		$va{'payment_date'} = $cses{'postdated_date'};
		$sql_postdate = ", PostedDate = '".$va{'payment_date'}."'";
	}else{
		$va{'payment_date'} = $va{'curdate'};
	}

	my $sql = "INSERT INTO sl_orders_payments SET 
					ID_orders = ".$cses{'id_orders'}."
					, Type = '".$cses{'order_ptype'}."'
					, Pmtfield1 = '".$va{'pmtfield1'}."'
					, Pmtfield2 = '".&filter_values($va{'pmtfield2'})."'
					, Pmtfield3 = '".$va{'pmtfield3'}."'
					, Pmtfield4 = '".$va{'pmtfield4'}."'
					, Pmtfield5 = '".$va{'pmtfield5'}."'
					, Pmtfield6 = '".$va{'pmtfield6'}."'
					, Pmtfield7 = '".$va{'pmtfield7'}."'
					, Pmtfield8 = '".$va{'pmtfield8'}."'
					, Pmtfield9 = '".$va{'pmtfield9'}."'
					, Pmtfield10 = '".$va{'pmtfield10'}."'
					, Pmtfield11 = '".$va{'pmtfield11'}."'
					, Amount = ".$va{'order_total'}."
					, AuthCode = ''
					, AuthDateTime = ''
					, Paymentdate = '".$va{'payment_date'}."'
					".$sql_postdate."
					, Status = 'Approved'
					, Date = CURDATE()
					, Time = CURTIME()
					, ID_admin_users = ".$usr{'id_admin_users'}."
				;";
	my $sth = &Do_SQL($sql);
	$id_payments = $sth->{'mysql_insertid'};
	$cses{'id_orders_payments'} = $id_payments;
	$in{'id_orders_payments'} = $id_payments;
	$sql =~ s/\n/\t/g;
	$cses{'sql_payments'} .= $sql."\n";

	### Encrypt CC
	if( $cses{'pay_type'} eq 'cc' and ($cfg{'encrypt_cc'} and $cfg{'encrypt_cc'} == 1) ){
		&encrypt_cc($cses{'id_orders'}, $id_payments, $cc_number, $cc_date, $cc_cvn);
	}

	### PostFecha
	if( $cses{'postdated'} eq 'Yes' ){
		&Do_SQL("UPDATE sl_orders SET Status='New', StatusPay='Post-Dated' WHERE ID_orders = ".$cses{'id_orders'}.";");
		$cses{'sql_payments'} .= "UPDATE sl_orders SET Status='New', StatusPay='Post-Dated' WHERE ID_orders = ".$cses{'id_orders'}.";\n";
		
		if($cfg{'use_points'} and $cses{'use_points'} eq 'on'){
			if($cses{'used_points'} == $va{'order_total'}){
				$query = "UPDATE sl_orders_payments set Pmtfield1 = 'Mastercard - Puntos', Pmtfield9='Mastercard - Puntos' where id_orders_payments = '$id_payments'";
				&Do_SQL($query);
				$cses{'sql_payments'}.= $query;
			}else{
				$new_amount = $va{'order_total'} - $cses{'used_points'};
				$id_orders = $cses{'id_orders'};
				&Do_SQL("update sl_orders_payments set Amount='$new_amount' where id_orders_payments=$id_payments");
				$cses{'sql_payments'}.= "update sl_orders_payments set Amount='$new_amount' where id_orders_payments=$id_payments";

				# Creamos Payments de Puntos.
				&Do_SQL("insert into sl_orders_payments 
					(PmtField1, PmtField2, PmtField3, Amount, Type, ID_orders, PmtField9, Paymentdate, Date, Time, ID_admin_users)
					SELECT 'Mastercard - Puntos' PmtField1, PmtField2, PmtField3, ' $cses{'used_points'}' Amount,  Type, ID_orders, 'Mastercard - Puntos' PmtField9, '$cses{'postdated_date'}', Date, Time, ID_admin_users 
					FROM sl_orders_payments WHERE id_orders_payments= '$id_payments' limit 1;");
				$id_orders_payments_puntos = &Do_SQL("SELECT LAST_INSERT_ID();")->fetchrow();
				$cses{'sql_payments'}.= "insert into sl_orders_payments 
					(PmtField1, PmtField2, PmtField3, Amount, Type, ID_orders, PmtField9,Date, Time, ID_admin_users)
					SELECT 'Mastercard - Puntos' PmtField1, PmtField2, PmtField3, ' $cses{'used_points'}' Amount,  Type, ID_orders, 'Mastercard - Puntos' PmtField9,Date, Time, ID_admin_users 
					FROM sl_orders_payments WHERE id_orders_payments= '$id_payments' limit 1;";



				&Do_SQL("INSERT INTO sl_orders_cardsdata
					(ID_orders, ID_orders_payments, card_number, card_date, card_cvn, Date, Time, ID_admin_users)
					SELECT ID_orders, '$id_orders_payments_puntos' ID_orders_payments, card_number, card_date, card_cvn, Date, Time, ID_admin_users 
					FROM sl_orders_cardsdata
					WHERE id_orders = '$id_orders' AND id_orders_payments = '$id_payments' LIMIT 1;");

				$cses{'sql_payments'}.= "INSERT INTO sl_orders_cardsdata
					(ID_orders, ID_orders_payments, card_number, card_date, card_cvn, Date, Time, ID_admin_users)
					SELECT ID_orders, '$id_orders_payments_puntos' ID_orders_payments, card_number, card_date, card_cvn, Date, Time, ID_admin_users 
					FROM sl_orders_cardsdata
					WHERE id_orders = '$id_orders' AND id_orders_payments = '$id_payments' LIMIT 1;";
			}
		}
		#&Do_SQL("DELETE FROM sl_orders_notes WHERE ID_orders = ".$cses{'id_orders'}." AND Notes LIKE 'La fecha de hoy es:%' LIMIT 1;");
		my $sql_notes = "INSERT INTO sl_orders_notes SET 
							ID_orders = ".$cses{'id_orders'}."
							, Notes = CONCAT('Los días elegidos para la posfecha son: ', DATEDIFF('".$cses{'postdated_date'}."', CURDATE()), '\nLa nueva fecha de cobro es: ".$cses{'postdated_date'}."')
							, Type = 'Low'
							, ID_orders_notes_types = 1
							, Date = Curdate()
							, Time = CURTIME()
							, ID_admin_users=".$usr{'id_admin_users'}.";";
		&Do_SQL($sql_notes);
		$sql_notes =~ s/\n/\t/g;
		$cses{'sql_payments'} .= $sql_notes."\n";


	}
}

sub create_customers{

	$va{'customers_type'} = $cfg{'customer_type_default'};
	$va{'pterms'} = 'CONTADO';
	#$va{'contact_mode'} = 'phone_call';
	$va{'currency'} = 'MX$';

	if( $cses{'id_customers'} ){		
		$sql = "UPDATE sl_customers SET 
					CID = '".&filter_values($cses{'phone_cid'})."'
					, FirstName = UPPER('".&filter_values($cses{'firstname'})."')
					, LastName1 = UPPER('".&filter_values($cses{'lastname1'})."')
					, LastName2 = UPPER('".&filter_values($cses{'lastname2'})."')
					, Sex = '".$cses{'sex'}."'
					, Phone1 = '".&filter_values($cses{'phone'})."'
					, Phone2 = '".&filter_values($cses{'phone2'})."'
					, Cellphone = '".&filter_values($cses{'cellphone'})."'
					, atime = '".$cses{'atime'}."'
					, Email = '".&filter_values($cses{'email'})."'
					, Birthday = '".$cses{'birthday'}."'
					, Address1 = UPPER('".&filter_values($cses{'address1'})."')
					, Address2 = UPPER('".&filter_values($cses{'address2'})."')
					, Address3 = UPPER('".&filter_values($cses{'address3'})."')
					, Urbanization = UPPER('".&filter_values($cses{'urbanization'})."')
					, City = UPPER('".$cses{'city'}."')
					, State = '".$cses{'state'}."'
					, Zip = '".$cses{'zipcode'}."'
					, Country = 'MEXICO'
					, Type = '".$va{'customers_type'}."'
					, Pterms = '".$va{'pterms'}."'
					, contact_mode = '".$va{'contact_mode'}."'
					, Currency = '".$va{'currency'}."'
					, Status = 'Active'	
				WHERE ID_customers = ".$cses{'id_customers'}.";";

		$cses{'repeatedcustomer'} = 'Yes' if( !$cses{'repeatedcustomer'} );

	}else{

		$sql = "INSERT INTO sl_customers SET 
					CID = '".&filter_values($cses{'phone_cid'})."'
					, FirstName = UPPER('".&filter_values($cses{'firstname'})."')
					, LastName1 = UPPER('".&filter_values($cses{'lastname1'})."')
					, LastName2 = UPPER('".&filter_values($cses{'lastname2'})."')
					, Sex = '".$cses{'sex'}."'
					, Phone1 = '".&filter_values($cses{'phone'})."'
					, Phone2 = '".&filter_values($cses{'phone2'})."'
					, Cellphone = '".&filter_values($cses{'cellphone'})."'
					, atime = '".$cses{'atime'}."'
					, Email = '".&filter_values($cses{'email'})."'
					, Birthday = '".$cses{'birthday'}."'
					, Address1 = UPPER('".&filter_values($cses{'address1'})."')
					, Address2 = UPPER('".&filter_values($cses{'address2'})."')
					, Address3 = UPPER('".&filter_values($cses{'address3'})."')
					, Urbanization = UPPER('".&filter_values($cses{'urbanization'})."')
					, City = UPPER('".$cses{'city'}."')
					, State = '".$cses{'state'}."'
					, Zip = '".$cses{'zipcode'}."'
					, Country = 'MEXICO'
					, Type = '".$va{'customers_type'}."'
					, Pterms = '".$va{'pterms'}."'
					, contact_mode = '".$va{'contact_mode'}."'
					, Currency = '".$va{'currency'}."'
					, Status = 'Active'			
					, Date = CURDATE() 
					, Time = CURTIME()			
					, ID_admin_users = ".$usr{'id_admin_users'}."		
				;";


		$cses{'repeatedcustomer'} = 'No';
	}
	$sth = &Do_SQL($sql);
	$sql =~ s/\n/ /g;
	$cses{'sql_customers'} .= $sql;

	$cses{'id_customers'} = ( !$cses{'id_customers'} ) ? $sth->{'mysql_insertid'} : $cses{'id_customers'};
	$va{'id_customers'} = $cses{'id_customers'};
	$va{'customers'} = $va{'id_customers'};
}




sub send_mail_sales{
# --------------------------------------------------------
# Forms Involved: 
# Created on: unknown
# Last Modified on: 13/Feb/2017
# Last Modified by: HCJ
# Author: 
# Description : 
# Parameters : 
# 


	my ($id_orders, $type_tpl) = @_;

	my $pmail_path = 'emails/';
	my $email_template = '';
	my $subject = '';
	my $rslt_mail = -1;	
	my $body ='';
	my $suffix_product = '';


	if( $cfg{'email_confirmation'} and $cfg{'email_confirmation'} == 1 ){

		## Determinamos el from_email correcto
		my ($from_email) = $cfg{'from_email'};

		## Si en la configuración presenta correo de Sognare, este correo es valido, el usuario no es 5333 de la empresa MOW y alguno de los producto tiene 'Sognare' en el nombre. 
		if( $cfg{'from_email_sognare'} and $cfg{'from_email_sognare'}   =~ /^.+\@(\[?)[a-zA-Z0-9\-\.]+\.([a-zA-Z]{2,3}|[0-9]{1,3})(\]?)$/ and !($in{'e'} eq 4 and &load_name('sl_customers','ID_customers',$id_customers,'ID_admin_users') eq '5333')){ 
			$sth_prod = &Do_SQL("SELECT count(sl_products.Name) sognare FROM sl_orders_products inner join sl_products on right(sl_orders_products.ID_products,6) = sl_products.ID_products WHERE sl_products.Name like '%sognare%' and sl_orders_products.ID_orders = '$id_orders';");
			my $rec = $sth_prod->fetchrow_hashref();
			if( $rec->{'sognare'} > 0 ){
				$from_email = $cfg{'from_email_sognare'}; 		
				$suffix_product = '_sognare' ;
			}
		}


		## ---------------------------------
		## Contenido
		## ---------------------------------
		## plantilla
		if( $type_tpl eq 'charged' ){	
			$email_template = 'charged'.$suffix_product.'.html';
			$subject = "Gracias por su pago";
		}else{
			$email_template = 'received'.$suffix_product.'.html';
			$subject = "Hemos recibido tu pedido";
		}

		## Datos
		$va{'id_orders'} = $id_orders;

		my $sql = "SELECT sl_customers.FirstName
					, sl_customers.LastName1
					, sl_customers.LastName2
					, sl_customers.Email
					, sl_orders.Address1
					, sl_orders.Address2
					, sl_orders.Address3
					, sl_orders.Urbanization
					, sl_orders.City
					, sl_orders.State
					, sl_orders.Zip
					, sl_orders.shp_name
					, sl_orders.shp_Address1
					, sl_orders.shp_Address2
					, sl_orders.shp_Address3
					, sl_orders.shp_Urbanization
					, sl_orders.shp_City
					, sl_orders.shp_State
					, sl_orders.shp_Zip
					/*Datos de facturación*/
					, sl_customers.RFC
					, cu_customers_addresses.Alias
					, cu_customers_addresses.cu_Street
					, cu_customers_addresses.cu_Num
					, cu_customers_addresses.cu_Num2
					, cu_customers_addresses.cu_Urbanization
					, cu_customers_addresses.cu_City
					, cu_customers_addresses.cu_District
					, cu_customers_addresses.cu_State
					, cu_customers_addresses.cu_Country
					, cu_customers_addresses.cu_Zip
				FROM sl_orders
					INNER JOIN sl_customers ON sl_orders.ID_customers = sl_customers.ID_customers
					LEFT JOIN cu_customers_addresses ON sl_orders.ID_customers = cu_customers_addresses.ID_customers AND cu_customers_addresses.PrimaryRecord = 'Yes'
				WHERE sl_orders.ID_orders = ".int($va{'id_orders'}).";";
		my $sth_ord = &Do_SQL($sql);
		my $rec_ord = $sth_ord->fetchrow_hashref();
		$va{'firstname'} 	= $rec_ord->{'FirstName'};
		$va{'lastname1'} 	= $rec_ord->{'LastName1'};
		$va{'lastname2'} 	= $rec_ord->{'LastName2'};
		$va{'email'}		= $rec_ord->{'Email'};
		$va{'address1'}		= $rec_ord->{'Address1'};
		$va{'address2'}		= $rec_ord->{'Address2'};
		$va{'address3'}		= $rec_ord->{'Address3'};
		$va{'urbanization'}	= $rec_ord->{'Urbanization'};
		$va{'city'}			= $rec_ord->{'City'};
		$va{'state'}		= $rec_ord->{'State'};
		$va{'zipcode'}		= $rec_ord->{'Zip'};
		$va{'shp_name'}			= $rec_ord->{'shp_name'};
		$va{'shp_address1'}		= $rec_ord->{'shp_Address1'};
		$va{'shp_address2'}		= $rec_ord->{'shp_Address2'};
		$va{'shp_address3'}		= $rec_ord->{'shp_Address3'};
		$va{'shp_urbanization'}	= $rec_ord->{'shp_Urbanization'};
		$va{'shp_city'}			= $rec_ord->{'shp_City'};
		$va{'shp_state'}		= $rec_ord->{'shp_State'};
		$va{'shp_zipcode'}		= $rec_ord->{'shp_Zip'};			
		$va{'name'} = lc($va{'firstname'});
		$va{'id_orders_full'} = $cfg{'prefixentershipment'}.$va{'id_orders'};

		### Datos de facturación
		if( $rec_ord->{'RFC'} ne '' ){
			$va{'inv_rfc'}			= $rec_ord->{'RFC'};
			$va{'inv_name'}			= $rec_ord->{'Alias'};
			$va{'inv_addess'}		= $rec_ord->{'cu_Street'}.' No. '.$rec_ord->{'cu_Num'};
			$va{'inv_addess'} 		.= ' Int. '.$rec_ord->{'cu_Num2'} if( $rec_ord->{'cu_Num'} ne '' );
			$va{'inv_urbanization'}	= $rec_ord->{'cu_Urbanization'};
			$va{'inv_city'}			= $rec_ord->{'cu_City'};
			$va{'inv_district'}		= $rec_ord->{'cu_District'};
			$va{'inv_state'}		= $rec_ord->{'cu_State'};
			$va{'inv_country'}		= $rec_ord->{'cu_Country'};
			$va{'inv_zipcode'}		= $rec_ord->{'cu_Zip'};

			$va{'invoice_info'} = '<font face="arial, verdana">
										<font face="century gothic, verdana" size="3" color="#2ab10b">Datos de Facturación:</font>										
										<div style="text-transform:uppercase;margin-left:10px;font-size:12px;">
											<br>
											[va_inv_rfc]<br>
											[va_inv_name]<br>
											[va_inv_addess]<br>
											[va_inv_urbanization]<br>					
											[va_inv_city]<br>
											[va_inv_state], [va_inv_country].<br>
											C.P. [va_inv_zipcode].<br>
										</div>
									</font>';
		}

		## Productos
		my $sql = "SELECT sl_orders_products.ID_products
						, IFNULL(sl_products.Model, sl_services.Name) Model
						, sl_skus.choice1
						, sl_skus.choice2
						, sl_skus.choice3
						, sl_skus.choice4
						, sl_orders_products.SalePrice
						, sl_orders_products.Discount
						, sl_orders_products.Quantity
						, sl_orders_products.Shipping				
						, sl_orders_products.Tax				
						, sl_orders_products.ShpTax				
					FROM sl_orders_products
						LEFT JOIN sl_products ON RIGHT(sl_orders_products.ID_products, 6) = sl_products.ID_products 
						LEFT JOIN sl_services ON RIGHT(sl_orders_products.ID_products, 4) = sl_services.ID_services
						LEFT JOIN sl_skus ON sl_orders_products.ID_products = sl_skus.ID_sku_products
					WHERE sl_orders_products.ID_orders = ".int($va{'id_orders'})." 
						AND sl_orders_products.`Status` = 'Active';";
		my $sth_prod = &Do_SQL($sql);

		my $total_net = 0;
		my $total_disc = 0;
		my $total_tax = 0;
		my $total_shp = 0;
		my $total_order = 0;
		$va{'email_products_list'} = '';
		while( my $rec = $sth_prod->fetchrow_hashref() ){
			$this_prod = $rec->{'Model'};

			my $this_choices = '';
			if( $rec->{'choice1'} ne '' or $rec->{'choice2'} ne '' or $rec->{'choice3'} ne '' or $rec->{'choice4'} ne '' ){
				$this_choices .= '(';
				$this_choices .= $rec->{'choice1'}.':' if( $rec->{'choice1'} ne '' );
				$this_choices .= $rec->{'choice2'}.':' if( $rec->{'choice2'} ne '' );
				$this_choices .= $rec->{'choice3'}.':' if( $rec->{'choice3'} ne '' );
				$this_choices .= $rec->{'choice4'} if( $rec->{'choice4'} ne '' );
				$this_choices = substr($this_choices, 0, length($this_choices)-1) if( substr($this_choices, -1, 1) eq ':' );
				$this_choices .= ')';
			}
			$this_prod .= '&nbsp;'.$this_choices;

			$total_net += $rec->{'SalePrice'};
			$total_disc += $rec->{'Discount'};
			$total_tax += $rec->{'Tax'} + $rec->{'ShpTax'};
			$total_shp += $rec->{'Shipping'};

			$va{'email_products_list'} .= '<tr>';
			$va{'email_products_list'} .= '	<td style="padding: 3px; text-align: center; vertical-align: top;">'.$rec->{'Quantity'}.'</td>';
			$va{'email_products_list'} .= '	<td style="padding: 3px; text-align: left;">'.$this_prod.'</td>';
			$va{'email_products_list'} .= '	<td style="padding: 3px; text-align: right; vertical-align: top;">'.&format_price($rec->{'SalePrice'}).'</td>';
			$va{'email_products_list'} .= '</tr>';
		}
		$total_order = ($total_net - $total_disc) + $total_tax + $total_shp;

		$va{'email_total_order'} = '<tr><td style="padding: 1px 3px 0 3px; text-align: right; width: 75%;">Subtotal:</td><td style="padding: 1px 3px 0 3px;	text-align: right;">'.&format_price($total_net).'</td></tr>';
		$va{'email_total_order'} .= '<tr><td style="padding: 1px 3px 0 3px; text-align: right; width: 75%;">Env&iacute;o y Manejo: </td><td style="padding: 1px 3px 0 3px; text-align: right;">'.&format_price($total_shp).'</td></tr>';
		$va{'email_total_order'} .= '<tr><td style="padding: 1px 3px 0 3px; text-align: right; width: 75%;">Descuentos:</td><td style="padding: 1px 3px 0 3px; text-align: right;">'.&format_price($total_disc).'</td></tr>';
		$va{'email_total_order'} .= '<tr><td style="padding: 1px 3px 0 3px; text-align: right; width: 75%;">Impuestos:</td><td style="padding: 1px 3px 0 3px; text-align: right;">'.&format_price($total_tax).'</td></tr>';
		$va{'email_total_order'} .= '<tr><td style="padding: 1px 3px 0 3px; text-align: right; width: 75%;" style="font-weight: bold;">Total:</td><td style="padding: 1px 3px 0 3px;	text-align: right;" style="font-weight: bold;">'.&format_price($total_order).'</td></tr>';

		### Pago
		my $sql = "SELECT sl_orders_payments.Pmtfield3
						, sl_orders_payments.Amount
						, sl_orders_payments.`Type`
						, sl_orders_payments.AuthCode 
					FROM sl_orders_payments 
					WHERE sl_orders_payments.ID_orders = ".int($va{'id_orders'})."
						AND sl_orders_payments.`Status` In('Approved','Pending')
					LIMIT 1;";
		my $sth_pay = &Do_SQL($sql);
		my $rec_pay = $sth_pay->fetchrow_hashref();
		#$va{'email_total_order'} = &format_price($rec_pay->{'Amount'});

		### Forma de pago
		if( $rec_pay->{'Type'}  eq 'COD' ){
			$va{'ptype_info'} = '<div style="font-size: 10pt;">
									<br><span style="font-size: 12pt;">Pago contra Entrega</span>
									<br><img src="https://s3.us-east-2.amazonaws.com/direksys-cloudfront/iconCOD.png"> 
									<br>Le agradeceremos tener listo su pago al recibir su mercancía
								</div>';
		}elsif( $rec_pay->{'Type'}  eq 'Referenced Deposit' ){
			$va{'ref_banco_azteca'} = $rec_pay->{'Pmtfield3'};
			
			$va{'banorte_company_name'} = $cfg{'banorte_company_name'};
			$va{'banorte_company_num'} = $cfg{'banorte_company_num'};
			$va{'azteca_company_name'} = $cfg{'azteca_company_name'};
			$va{'azteca_company_num'} = $cfg{'azteca_company_num'};

			$va{'ptype_info'} = '<div style="font-size: 10pt;">			
									<br>
									Le agradeceremos su pronto pago en alguna de las siguientes instituciones bancarias: [va_sty_show_pay_rd]
									<br>
									<br>
									<table width="100%" cellpadding="0" cellspacing="0" border="0">
										<tr>
											<td class="cont">
												<center>
												<img src="https://s3.us-east-2.amazonaws.com/direksys-cloudfront/banorte.png" style="width: 160px;">
												<br>BANORTE - Banco Mercantil del Norte, S. A. <br>
												EMPRESA : <strong>[va_banorte_company_name]</strong><br>
												NO. DE EMPRESA : <strong>[va_banorte_company_num]</strong><br>
												REFERENCIA : <strong>[va_id_orders]</strong><br> 
											</td>
										</tr>
										<tr><td>&nbsp;</td></tr>
										<tr>
											<td class="cont">
												<center>
												<img src="https://s3.us-east-2.amazonaws.com/direksys-cloudfront/bancoazteca.png" style="width: 160px;">
												<br>BANCO AZTECA<br>
												EMISORA : <strong>[va_azteca_company_name]</strong><br>
												REFERENCIA : <strong>[va_ref_banco_azteca]</strong><br> 
											</td>
										</tr>
									</table>
								</div>';
		}elsif( $rec_pay->{'Type'}  eq 'Credit-Card' ){
			$va{'cc_number'} = substr($rec_pay->{'Pmtfield3'}, -4, 4);
			$va{'auth_code'} = $rec_pay->{'AuthCode'};
			$va{'ptype_info'} = '<div style="font-size: 10pt;">
									<br><span style="font-size: 10pt;">Forma de Pago:</span>
									<br><span style="font-size: 12pt;">Tarjeta de Crédito</span>
									<br><img src="https://s3.us-east-2.amazonaws.com/direksys-cloudfront/iconCredit-Card.png"> 
								</div>';
		}


		## Fecha
		my ($y, $m, $d) = Date::Calc::Today();
		$va{'order_date'} = sprintf('%02d-%02d-%02d', $y, $m, $d);

		## Se genera html completo
		$body = &build_page($pmail_path . $email_template);
		## ---------------------------------

		## Destinatario
		$to_email = $va{'email'};

		## Envío		
		if( $to_email ne '' ){
			$subject = $va{'id_orders_full'}.": ".$subject;

			## Debug Email
			$to_email .= ','.$cfg{'to_debug_email_sales'} if($cfg{'debug_email_sales'} and $cfg{'debug_email_sales'} == 1 and $cfg{'to_debug_email_sales'});

			$rslt_mail = &send_mandrillapp_email_attachment($from_email, $to_email, $subject, $body, 'none', 'none');

		}else{
			$rslt_mail = 'ok';
		}
	}

	return $rslt_mail;
}
##################################################################
############             Functions Ajax.          ################
##################################################################
sub ajax_pays_list{
	use JSON;
	my %json_data;

	&load_callsession();

	$cses{'coupon'} = $in{'coupon'};
	if( $cses{'order_discount'} and $cses{'order_discount'} ne '' and $cses{'coupon'} eq '' ){
		$cses{'order_discount'} = 0;
		$va{'order_discount'} = 0;
	}

	&products_order_list();
	### Se calculan los subotales y el total de la orden
	&order_totals();
	### Se genera el listado de pagos/fechas (MSI)
	&fpays_order_list();

	&save_callsession();

	$json_data{'html_pmts'} = $va{'pays_list'};
	$json_data{'pmts_amount'} = $va{'pmts_amount'};

	print "Content-type: application/json\n\n";
	print encode_json(\%json_data);
}

sub ajax_clear_discount{
	&load_callsession();
	delete($cses{'coupon'});
	delete($cses{'order_discount'});
	&save_callsession();

	print "Content-type: application/html\n\n";
	print "OK";
}

sub ajax_set_shop_cart_products{
	&load_callsession();
	$cses{'shop_cart_products'} = $in{'products'};
	&save_callsession();

	print "Content-type: application/html\n\n";
	print "OK";
}

sub ajax_payment_charge{
	use JSON;
	my %json_data;

	&load_callsession();
	
	require ("../../common/apps/cybersubs.cgi");
	
	if($cses{'use_points'} eq 'on' and $cfg{'use_points'} and $cfg{'use_points'} == 1){
		($json_data{'status'}, $json_data{'msg'}, $json_data{'code'}) = &sltvcyb_auth($cses{'id_orders'}, $cses{'id_orders_payments'}, $cses{'use_points'}, $cses{'used_points'});
	}else{
		($json_data{'status'}, $json_data{'msg'}, $json_data{'code'}) = &sltvcyb_auth($cses{'id_orders'}, $cses{'id_orders_payments'});
	}
	### Se inserta la nota con el resultado
	my $sql_notes = "INSERT INTO sl_orders_notes SET 
							ID_orders = ".$cses{'id_orders'}."
							, Notes = 'Status=".&filter_values($json_data{'status'}).", Msg=".&filter_values($json_data{'msg'}).", Code=".&filter_values($json_data{'code'}).", Retries=".int($in{'retries'})."'
							, Type = 'Low'
							, ID_orders_notes_types = 1
							, Date = Curdate()
							, Time = CURTIME()
							, ID_admin_users=".$usr{'id_admin_users'}.";";
	&Do_SQL($sql_notes);
	$sql_notes =~ s/\n/\t/g;
	$cses{'sql_payments'} .= $sql_notes."\n";
	
	### Se procesa el resultado y se genera la respuesta
	if( $json_data{'status'} =~ /OK/ ){
		$cses{'order_status'} = 'Processed';
		my $auth_code = &load_name('sl_orders_payments', 'ID_orders_payments', $cses{'id_orders_payments'}, 'AuthCode');
		$cses{'auth_code'} = $auth_code;
		$json_data{'auth_code'} = $auth_code;


		## Se envían los emails
		my $rslt_mail_ord = &send_mail_sales($cses{'id_orders'}, 'received');
		$json_data{'rslt_mail_ord'} = $rslt_mail_ord;
		my $rslt_mail_pay = &send_mail_sales($cses{'id_orders'}, 'charged');
		$json_data{'rslt_mail_pay'} = $rslt_mail_pay;
	}
	&save_callsession();

	print "Content-type: application/json\n\n";
	print encode_json(\%json_data);
}

sub ajax_validate_cc{
	use JSON;
	my %json_data;

	my $param = $in{'param'};
	my $lgth_cc = int($in{'lgth'});
	my $date_cc = substr($param, 0, 4);
	my $num_cc = substr($param, 4, $lgth_cc);
	my $cvn_cc = substr($param, (4+$lgth_cc));

	&load_callsession();

	### ------------------------------------
	### Se valida el número de tarjeta
	### ------------------------------------
	my $prefix_cc = substr($num_cc, 0, 6);
	$json_data{'pmtfield3'}{'prefix_cc'} = $prefix_cc;
	$json_data{'pmtfield3'}{'result'} = 'OK';
	if( $prefix_cc =~ /^4/ and $lgth_cc == 16 ){	
		$json_data{'pmtfield3'}{'network'} = 'Visa';
	}elsif( $prefix_cc =~ /^(34|37)/ and $lgth_cc == 15 ){
		$json_data{'pmtfield3'}{'network'} = 'American Express';
	}elsif( $prefix_cc =~ /^(51|52|53|54|55|504|589)/ and $lgth_cc == 16 ){
		$json_data{'pmtfield3'}{'network'} = 'Mastercard';
	}else{
		$json_data{'pmtfield3'}{'result'} = 'Invalid';
	}
	# Info. adicional de la tarjeta
	if( $json_data{'pmtfield3'}{'result'} eq 'OK' ){
		my $sql = "SELECT Bank, `Type`, Network 
					FROM cu_cardprefix 
					WHERE Prefix = '".$prefix_cc."' AND `Status` = 'Active';";
		my $sth = &Do_SQL($sql);
		my $data_cc = $sth->fetchrow_hashref();
		if( $data_cc->{'Bank'} ){			
			$json_data{'pmtfield3'}{'type'} =  $data_cc->{'Type'};
			$json_data{'pmtfield3'}{'bank'} =  $data_cc->{'Bank'};
		}
	}

	### ------------------------------------
	### Se valida la vigencia de la tarjeta
	### ------------------------------------
	my ($y, $m, $d) = Date::Calc::Today();
	($y, $m, $d) = Add_Delta_Days($y, $m, $d, 1);
	$va{'curdate'} = sprintf('%02d-%02d-%02d', $y, $m, $d);

	### Se obtiene la fecha del ultimo pago
	$cses{'total_pmts'} = $in{'total_pmts'};
	if( int($cses{'total_pmts'}) > 1 ){
		for my $i(1 .. int($cses{'total_pmts'}) - 1){
			($y, $m, $d) = Add_Delta_Days($y, $m, $d, $cses{'fpdays'});
			my $new_date = sprintf('%02d-%02d-%02d', $y, $m, $d);
			$va{'last_date_pay'} = $new_date;
		}
	}else{
		$va{'last_date_pay'} = $va{'curdate'};
	}
	&save_callsession();

	$month_cc = int(substr($date_cc, 0, 2));
	$year_cc = '20'.substr($date_cc, 2, 2);
	$days_cc = 28;
	if( $month_cc == 1 or $month_cc == 3 or $month_cc == 5 or $month_cc == 7 or $month_cc == 8 or $month_cc == 12 ){
		$days_cc = 31;
	}elsif( $month_cc == 4 or $month_cc == 6 or $month_cc == 9 or $month_cc == 11 ){
		$days_cc = 30;
	}

	my $sth = &Do_SQL("SELECT DATEDIFF('".$year_cc."-".$month_cc."-".$days_cc."', '".$va{'last_date_pay'}."');");
	my $diff = $sth->fetchrow();
	$json_data{'pmtfield4'}{'result'} = 'OK';
	if( $diff < $cfg{'prevent_days'} ){
		$json_data{'pmtfield4'}{'result'} = 'Invalid';
	}

	$json_data{'pmtfield4'}{'last_date_pay'} = $va{'last_date_pay'};
	$json_data{'pmtfield4'}{'prevent_days'} = $cfg{'prevent_days'};

	### ------------------------------------
	### Se valida el CVN
	### ------------------------------------
	$json_data{'pmtfield5'}{'result'} = 'OK';
	if( $json_data{'pmtfield3'}{'result'} eq 'Invalid' ){
		$json_data{'pmtfield5'}{'result'} = 'Invalid';
	}else{
		if( (length($cvn_cc) == 3 and $json_data{'pmtfield3'}{'network'} eq 'American Express') 
			or (length($cvn_cc) == 4 and ($json_data{'pmtfield3'}{'network'} eq 'Mastercard' or $json_data{'pmtfield3'}{'network'} eq 'Visa')) )
		{
			$json_data{'pmtfield5'}{'result'} = 'Invalid';
		}
	}

	print "Content-type: application/json\n\n";
	print encode_json(\%json_data);
}

sub ajax_validate_exp_cc{
	my $date_cc = $in{'date_cc'};

	use JSON;
	my %json_data;

	&load_callsession();

	# Date	
	my ($y, $m, $d) = Date::Calc::Today();
	($y, $m, $d) = Add_Delta_Days($y, $m, $d, 1);
	$va{'curdate'} = sprintf('%02d-%02d-%02d', $y, $m, $d);

	### Se obtiene la fecha del ultimo pago
	$cses{'total_pmts'} = $in{'total_pmts'};
	if( int($cses{'total_pmts'}) > 1 ){
		for my $i(1 .. int($cses{'total_pmts'}) - 1){
			($y, $m, $d) = Add_Delta_Days($y, $m, $d, $cses{'fpdays'});
			my $new_date = sprintf('%02d-%02d-%02d', $y, $m, $d);
			$va{'last_date_pay'} = $new_date;
		}
	}else{
		$va{'last_date_pay'} = $va{'curdate'};
	}
	&save_callsession();

	$month_cc = int(substr($date_cc, 0, 2));
	$year_cc = '20'.substr($date_cc, 2, 2);
	$days_cc = 28;
	if( $month_cc == 1 or $month_cc == 3 or $month_cc == 5 or $month_cc == 7 or $month_cc == 8 or $month_cc == 12 ){
		$days_cc = 31;
	}elsif( $month_cc == 4 or $month_cc == 6 or $month_cc == 9 or $month_cc == 11 ){
		$days_cc = 30;
	}

	my $sth = &Do_SQL("SELECT DATEDIFF('".$year_cc."-".$month_cc."-".$days_cc."', '".$va{'last_date_pay'}."');");
	my $diff = $sth->fetchrow();
	$json_data{'result'} = 1;
	if( $diff < $cfg{'prevent_days'} ){
		$json_data{'result'} = 0;
	}

	$json_data{'last_date_pay'} = $va{'last_date_pay'};
	$json_data{'prevent_days'} = $cfg{'prevent_days'};
	#$json_data{'month_cc'} = $month_cc;
	#$json_data{'year_cc'} = $year_cc;
	#$json_data{'days_cc'} = $days_cc;

	print "Content-type: application/json\n\n";
	print encode_json(\%json_data);
}

sub ajax_save_invoice_data{
	use JSON;
	my %json_data;

	my $sql = '';

	&Do_SQL("SET CHARACTER SET utf8;");
	$sql = "SELECT sl_customers.Address1
				, sl_customers.Address2
				, sl_customers.Address3
				, sl_customers.Urbanization
				, sl_customers.City
				, sl_customers.State
				, sl_customers.Zip
				, sl_customers.Country
				, cu_customers_addresses.ID_customers_addresses
			FROM sl_customers
				LEFT JOIN cu_customers_addresses ON sl_customers.ID_customers = cu_customers_addresses.ID_customers
			WHERE sl_customers.ID_customers=".int($in{'id_customers'}).";";
	$sth_cus = &Do_SQL($sql);
	$dat_cus = $sth_cus->fetchrow_hashref();

	### Se actualizan los datos de facturacion
	if( int($dat_cus->{'ID_customers_addresses'}) > 0 ){		
		$upd = "UPDATE cu_customers_addresses SET 
					ID_customers = ".int($in{'id_customers'})."
					, Alias = '".&filter_values($in{'invoice_name'})."'
					, Address1 = '".$dat_cus->{'Address1'}."'
					, Address2 = '".$dat_cus->{'Address2'}."'
					, Address3 = '".$dat_cus->{'Address3'}."'
					, Urbanization = '".$dat_cus->{'Urbanization'}."'
					, City = '".$dat_cus->{'City'}."'
					, State = '".$dat_cus->{'State'}."'
					, Country = '".$dat_cus->{'Country'}."'
					, Zip = '".$dat_cus->{'Zip'}."'
					, cu_Street = '".&filter_values($in{'invoice_street'})."'
					, cu_Num = '".&filter_values($in{'invoice_noext'})."'
					, cu_Num2 = '".&filter_values($in{'invoice_noint'})."'
					, cu_Urbanization = '".&filter_values($in{'invoice_urbanization'})."'
					, cu_City = '".&filter_values($in{'invoice_city'})."'
					, cu_State = '".&filter_values($in{'invoice_state'})."'
					, cu_Country = '".&filter_values($in{'invoice_country'})."'
					, cu_Zip = '".&filter_values($in{'invoice_zipcode'})."'
					, PrimaryRecord = 'Yes'
					, Status = 'Active'
				WHERE ID_customers_addresses = ".$dat_cus->{'ID_customers_addresses'}.";";
		&Do_SQL($upd);
		$json_data{'action'} = 'Update';

	### Se crea el registro con los datos de facturación
	}else{
		$ins = "INSERT INTO cu_customers_addresses SET 
					ID_customers = ".int($in{'id_customers'})."
					, Alias = '".&filter_values($in{'invoice_name'})."'
					, Address1 = '".$dat_cus->{'Address1'}."'
					, Address2 = '".$dat_cus->{'Address2'}."'
					, Address3 = '".$dat_cus->{'Address3'}."'
					, Urbanization = '".$dat_cus->{'Urbanization'}."'
					, City = '".$dat_cus->{'City'}."'
					, State = '".$dat_cus->{'State'}."'
					, Country = '".$dat_cus->{'Country'}."'
					, Zip = '".$dat_cus->{'Zip'}."'
					, cu_Street = '".&filter_values($in{'invoice_street'})."'
					, cu_Num = '".&filter_values($in{'invoice_noext'})."'
					, cu_Num2 = '".&filter_values($in{'invoice_noint'})."'
					, cu_Urbanization = '".&filter_values($in{'invoice_urbanization'})."'
					, cu_City = '".&filter_values($in{'invoice_city'})."'
					, cu_State = '".&filter_values($in{'invoice_state'})."'
					, cu_Country = '".&filter_values($in{'invoice_country'})."'
					, cu_Zip = '".&filter_values($in{'invoice_zipcode'})."'
					, PrimaryRecord = 'Yes'
					, Status = 'Active'
					, Date = CURDATE()
					, Time = CURTIME()
					, ID_admin_users = ".$usr{'id_admin_users'}."
				;";
		&Do_SQL($ins);
		$json_data{'action'} = 'Insert';
	}
	### Se actualizan el RFC y el CompanyName en sl_customers
	$upd = "UPDATE sl_customers SET 
				RFC = '".$in{'invoice_rfc'}."' 
				, company_name = '".$in{'invoice_name'}."' 
			WHERE ID_customers = ".$in{'id_customers'}.";";
	&Do_SQL($upd);

	print "Content-type: application/json\n\n";
	print encode_json(\%json_data);
}

sub ajax_save_email{
	use JSON;
	my %json_data;

	my $sql = '';

	$sql = "UPDATE sl_customers SET Email = '".&filter_values($in{'email'})."' WHERE ID_customers = ".$in{'id_customers'}.";";
	&Do_SQL($sql);

	&load_callsession();
	$cses{'email'} = &filter_values($in{'email'});
	$va{'email'} = $cses{'email'};
	&save_callsession();

	$json_data{'result'} = 'OK';

	print "Content-type: application/json\n\n";
	print encode_json(\%json_data);
}

sub ajax_send_mail{
	use JSON;
	my %json_data;

	&load_callsession();

	## Se envían los emails
	my $rslt_mail = &send_mail_sales($cses{'id_orders'}, 'received');
	$json_data{'rslt_mail'} = $rslt_mail;

	print "Content-type: application/json\n\n";
	print encode_json(\%json_data);
}

##################################################################
############              Functions Aux.          ################
##################################################################
sub build_select_zipcodes_state{
	my $sql = "SELECT StateFullName
				FROM sl_zipcodes
				WHERE StateFullName != '' AND StateFullName IS NOT NULL
				GROUP BY StateFullName
				ORDER BY StateFullName;";
	my $sth = &Do_SQL($sql);

	my $html_opt = '';
	while( my $rec = $sth->fetchrow_hashref() ){
		$html_opt .= '<option value="'.$rec->{'StateFullName'}.'">'.$rec->{'StateFullName'}.'</option>';
	}

	return $html_opt;
}

sub build_select_zipcodes_city{
	my $state = @_;

	my $sql = "SELECT City
				FROM sl_zipcodes
				WHERE StateFullName='".$state."' AND City != '' AND City IS NOT NULL
				GROUP BY City
				ORDER BY City;";
	my $sth = &Do_SQL($sql);

	my $html_opt = '';
	while( my $rec = $sth->fetchrow_hashref() ){
		$html_opt .= '<option value="'.$rec->{'City'}.'">'.$rec->{'City'}.'</option>';
	}

	return $html_opt;
}


sub build_button_notepad{
	my $val ='';
	$va{'test'} = &check_permissions('button_notepad','','');
	if($cfg{'activate_notepad'} and $cfg{'activate_notepad'} == 1 and &check_permissions('button_notepad','','')){
		$val=q|<a href="#" id="btn_notepad"><img src="/sitimages/notas.png" title="Notepad" alt="notepad" border="0"> </a>|;
	}
	return $val;
}


sub set_debug_sales{

	my ($debug) = @_;
	my $file_name = $usr{'id_admin_users'}.'_sales_debug.txt';

	open(this_file, '>>'.$cfg{'path_layouts'}.'/'.$file_name) || die "lo siento, no puedo abrir el archivo $file_name\n";

	print this_file $debug;
}

sub get_debug_sales{
	my $file_name = $usr{'id_admin_users'}.'_sales_debug.txt';

	open(this_file, $cfg{'path_layouts'}.'/'.$file_name) || die "lo siento, no puedo abrir el archivo $file_name\n";

	my $this_debug = '';
	while(<this_file>){
		$this_debug .= $_;
	}

	return $this_debug;
}

sub delete_debug_sales{
	
	my $file_name = $usr{'id_admin_users'}.'_sales_debug.txt';

	unlink($cfg{'path_layouts'}.'/'.$file_name);
}


##################################################################
############                HOME                 #################
##################################################################
sub chgmode {
# --------------------------------------------------------
	if ($usr{'mode'} eq 'in'){
		$usr{'mode'} = 'out';
	}else{
		$usr{'mode'} = 'in';
	}
	&save_auth_data;
	&console;
}

sub chgexten {
# --------------------------------------------------------
	if ($in{'action'}){
		$va{'passnum'} = '----';
		my ($sth) = &Do_SQL("SELECT extension FROM admin_users WHERE extenpass='0' AND ID_admin_users='$usr{'id_admin_users'}'");
		$usr{'extension'} = $sth->fetchrow();
		if ($usr{'extension'}){
			&save_auth_data;
			$va{'message'} = &trans_txt('extenlogin_ok');
		}else{
			$va{'message'} = &trans_txt('extenlogin_error');
		}
	}elsif($usr{'extension'}){
		$va{'passnum'} = '----';
		$va{'message'} = &trans_txt('extenlogin_ok');
	}else{
		srand( time() ^ ($$ + ($$ << 15)) );
		$va{'passnum'} = substr((int(rand(10000000000)) + 1),4,4);
		my ($sth) = &Do_SQL("SELECT COUNT(*) FROM admin_users WHERE extenpass='$va{'passnum'}' AND ID_admin_users='$usr{'id_admin_users'}'");
		while ($sth->fetchrow() !=0){
			$va{'passnum'} = substr((int(rand(10000000000)) + 1),4,4);
			$sth = &Do_SQL("SELECT COUNT(*) FROM admin_users WHERE extenpass='$va{'passnum'}' AND ID_admin_users='$usr{'id_admin_users'}'");	
		}
		$sth = &Do_SQL("UPDATE admin_users SET extenpass='$va{'passnum'}' WHERE ID_admin_users='$usr{'id_admin_users'}'");	
	}
	
	print "Content-type: text/html\n\n";
	print &build_page("chg_exten.html");
}


##################################################################
############                HELP                 #################
##################################################################
sub help {
# --------------------------------------------------------
	print "Content-type: text/html\n\n";
	print &build_page("help.html");
}

sub html_console_unauth {
# --------------------------------------------------------
	print "Content-type: text/html\n\n";
	print &build_page("unauth.html");
}


1;

