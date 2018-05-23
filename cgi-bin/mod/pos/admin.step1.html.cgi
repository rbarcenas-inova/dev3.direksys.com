#!/usr/bin/perl
##################################################################
############      CONSOLE STEP 1           #################
##################################################################
	&load_callsession();
	
	$va{'steptemp'} = 1;
	#my $data = &loadDataPos();
	$in{'id_orders'} = !$in{'id_orders'} ? $cses{'id_orders'} : $in{'id_order'};
	# save_callsession();
	# cgierr(Dumper \%cses);
	#$id_customers = $data{'customer'};
	#$id_warehouses = $data{'warehouse'};
	my $sql1 = &Do_SQL("SELECT sl_vars.VValue, sl_vars.Subcode 
							FROM sl_vars 
							WHERE vname LIKE 'pos_config_$usr{'id_admin_users'}'");
	$vars = $sql1->fetchrow_hashref;
	$id_warehouses = $vars->{'Subcode'};
	$id_customers = &Do_SQL("select ID_customers from sl_customers where  CID= 'POS_$id_warehouses'")->fetchrow();
	if ($in{'action'} eq 'add_to_cart' and $in{'step'} eq "1" and !$in{'id_orders'}){
    	&Do_SQL('START TRANSACTION');
		my ($sth) = &Do_SQL("SELECT * FROM sl_customers WHERE ID_customers = '$id_customers'");
		$rec = $sth->fetchrow_hashref;
		my ($sth) = &Do_SQL("SELECT * FROM sl_customers WHERE ID_customers = '$cfg{id_customer_generic_pos}'");
		$rec_shp = $sth->fetchrow_hashref;
		$payment = 'Credit-Card';
		$saleorigins = $cfg{'sale_origin_pos'};
		if( $id_warehouses <= 0 and $id_customers <= 0 ){
			return;
		}
		my ($sth2) = &Do_SQL("INSERT INTO sl_orders
		(ID_customers, Address1, Address2, Address3, Urbanization, City, State, Zip, Country, shp_Address1, shp_Address2, shp_Address3, shp_Urbanization, shp_City, shp_State, shp_Zip, shp_Country, ID_zones, Ptype, Pterms, StatusPrd, StatusPay, ID_salesorigins, Date, Time, ID_admin_users, ID_warehouses )
		VALUES
		('$rec->{ID_customers}', '$rec->{Address1}', '$rec->{Address2}', '$rec->{Address3}', '$rec->{Urbanization}', '$rec->{City}', '$rec->{State}', '$rec->{Zip}', '$rec->{Country}', '$rec_shp->{Address1}', '$rec_shp->{Address2}', '$rec_shp->{Address3}', '$rec_shp->{Urbanization}', '$rec_shp->{City}', '$rec_shp->{State}', '$rec_shp->{Zip}', '$rec_shp->{Country}', $cfg{id_zones_pos}, '$payment', '$rec->{Pterms}', 'None', 'None', '$saleorigins', NOW(), NOW(), '$usr{'id_admin_users'}', $id_warehouses)");
		$id_orders = $sth2->{'mysql_insertid'};
		### Shopping Cart
		my ($cant);
		if($id_orders <= 0){
			return;
		}

		$increment = 100000000;
		foreach $key (keys %in){

			if ($key =~ /add_(\d+)/ and int($in{$key})>0){

				my $qty = $in{$key};
				++$cant;
				## TO-DO
				## Validar que exista el inventario en el WH del usuario
				my ($sth4) = &Do_SQL("SELECT 							
							sl_warehouses_location.ID_warehouses,
							sl_warehouses_location.ID_products,
							sl_warehouses_location.Location,
							sl_warehouses_location.Quantity,
							sl_skus.UPC,
							sl_parts.Model,
							sl_parts.Name,
							sl_customers_parts.ID_customers,
							sl_customers_parts.SPrice,
							sl_parts.Sale_Tax
							FROM sl_warehouses_location
							INNER JOIN sl_skus ON 
							(sl_warehouses_location.ID_products = sl_skus.ID_sku_products)
							INNER JOIN sl_parts ON 
							(sl_skus.ID_products = sl_parts.ID_parts)
							INNER JOIN sl_customers_parts ON
							(sl_parts.ID_parts = sl_customers_parts.ID_parts)
							WHERE 1
							AND sl_warehouses_location.ID_warehouses = '$id_warehouses'
							AND sl_skus.Status = 'Active'
							AND sl_parts.Status = 'Active'
							AND sl_customers_parts.ID_customers = '$id_customers'
							AND sl_warehouses_location.Quantity > 0
							AND sl_skus.ID_sku_products = '$1'
							;");
				my ($rec_sku) = $sth4->fetchrow_hashref;
				$Tax_percent = $rec_sku->{Sale_Tax} / 100;
				$totalPrice = ($qty * $rec_sku->{SPrice});
				$Tax = $totalPrice * $Tax_percent;
				$totalTax += $Tax;
				$orderNet += $totalPrice;				
				if($1 <= 0){
					return;
				}
				my ($sth5) = &Do_SQL("INSERT INTO sl_orders_products
				(ID_products, ID_orders, Related_ID_products, Quantity, SalePrice, Tax, Tax_percent, FP, Shipping, Status, Date, Time, ID_admin_users)
				VALUES
				('$increment', '$id_orders', '$rec_sku->{ID_products}', '$qty', '$totalPrice', '$Tax', '$Tax_percent', 1, '0.00', 'Active', NOW(), NOW(), '$usr{'id_admin_users'}')");
				$increment = ($increment + 1000000) ;
				
			}
		}
		$totalAmount = $totalTax + $orderNet;
		$in{'amount'} = &format_price($totalAmount);
		$cses{'amount'} = $totalAmount;
		#$in{'id_ware_location'} = $idWareLocation;		
		# use Data::Dumper;
		# cgierr(Dumper \%cses);
		my ($sth6) = &Do_SQL("UPDATE sl_orders SET OrderQty='$cant', OrderTax='$Tax_percent', OrderNet='$orderNet' WHERE ID_orders='$id_orders'");
		&Do_SQL("INSERT INTO sl_orders_payments 
			(ID_orders, Type, Amount, Reason, Paymentdate, Status, Date, Time, ID_admin_users)
			VALUES 
			('$id_orders', '$type_payment', '$cses{'amount'}', 'Sale', NOW(), 'Approved', NOW(), NOW(), '$usr{'id_admin_users'}')");
		$cses{'id_orders'} = $id_orders;
		$in{'id_orders'} = $id_orders;
		&save_callsession();
		&Do_SQL('COMMIT');
	}
	$type_payment = 'Credit-Card';
	$va{'message'} .= qq||;
	$va{'min_installments'} = $cfg{'payments_min_installments'};
	$va{'max_installments'} = $cfg{'payments_max_installments'};


1;