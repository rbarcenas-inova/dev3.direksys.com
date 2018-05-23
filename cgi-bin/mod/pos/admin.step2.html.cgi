#!/usr/bin/perl
##################################################################
############      CONSOLE STEP 2 : PRODUCT INFO
##################################################################
require ('../../mod/wms/admin.html.cgi');
require ('../../mod/wms/admin.cod.cgi');
require ('../../mod/wms/sub.base.html.cgi');
require ('../../mod/wms/sub.func.html.cgi');
require ("../../common/subs/sub.wms.html.cgi");

	$va{'steptemp'} = 2;
	$id_orders =  $in{'id_orders'};	 
	$sth = &Do_SQL("SELECT * FROM sl_orders_payments
			WHERE ID_orders = '$id_orders'
			AND Status != 'Cancelled'
			ORDER by ID_orders_payments DESC LIMIT 1");
	$payment = $sth->fetchrow_hashref;
	$idpp=$payment->{'ID_orders_payments'};
	# use Data::Dumper;
	# print '<pre>';
	# print Dumper $payment;
	# exit;
	#my $data = loadDataPos();
	#$id_customers = $data{'customer'};
	#$id_warehouses = $data{'warehouse'};
	my $sql1 = &Do_SQL("SELECT sl_vars.VValue, sl_vars.Subcode
							FROM sl_vars 
							WHERE vname = 'pos_config_$usr{'id_admin_users'}'");
	$vars = $sql1->fetchrow_hashref;
	$id_warehouses = $vars->{'Subcode'};    	
	$id_customers = &Do_SQL("select ID_customers from sl_customers where  CID= 'POS_$id_warehouses'")->fetchrow();


	# &Do_SQL("start TRANSACTION");
	# my $log = "START TRANSACTION\n";
	# &Do_SQL('START TRANSACTION');

	#  
	#  CREAR NUEVO USARIO
	#  
	$sql = "insert into `sl_customers` (`CID`, `FirstName`, `Address1`, `Address3`, `Urbanization`, `City`, `State`,`Country`,  `Type`, `Pterms`, `RFC`,  `Currency`, `Status`, `Date`, `Time`, `ID_admin_users`) values
		('$in{'invoice_rfc'}','$in{'invoice_name'}','$in{'invoice_street'} $in{'invoice_noext'} $in{'invoice_noint'}','$in{'invoice_city'}', '$in{'invoice_urbanization'}','$in{'invoice_city'}','$in{'state'}', '$cfg{'default_country'}','POS', 'CONTADO','$in{'invoice_rfc'}','".'CO$'."','Active',curdate(),curtime(), $in{'id_admin_users'})";
		# cgierr($sql);
	&Do_SQL($sql);
	$id_customers = Do_SQL("SELECT LAST_INSERT_ID();")->fetchrow();

	# 
	# 	ACTULIZAR USUARIO DE ORDEN
	# 
	$sql = "update sl_orders set 
		id_customers=$id_customers,
		Address1='$in{'invoice_street'} $in{'invoice_noext'} $in{'invoice_noint'}',
		Address2 = '',
		Address3 = '$in{'invoice_city'}', 
		Urbanization = '$in{'invoice_urbanization'}',
		City='$in{'invoice_city'}',
		State='$in{'state'}',
		Date=NOW(),
		Time=NOW()
	where id_orders = $id_orders";
	&Do_SQL($sql);
	my @params;
	if($in{'action'} eq 'cash' and $in{'id_orders'} > 0 and $in{'step'} eq '2'){
		if($payment->{'Captured'} ne 'Yes'){
			my ($sth) = &Do_SQL("UPDATE sl_orders SET status = 'Processed' WHERE ID_orders = '$id_orders'");
			# $Pmtfield7 = 'Cash';
			# $Pmtfield8 = '1'; 
			# # ACTUALIZA PAGO
			&Do_SQL("UPDATE sl_orders_payments SET 
				Captured = 'YES' , CapDate = NOW(), Type = 'COD', status = 'Approved'
				WHERE
				ID_orders_payments = '$payment->{ID_orders_payments}'");
			# my ($sth) = &Do_SQL("SELECT Ptype, Type FROM sl_orders INNER JOIN sl_customers USING(ID_customers) WHERE ID_orders = '$id_orders';");
			# ($order_type, $ctype) = $sth->fetchrow();
			# $ptype = get_deposit_type($idpp,'');
			# @params = ($id_orders, $idpp, 1);
			# &accounting_keypoints('order_deposit_'. lc($ctype) .'_'. lc($order_type) .'_'. lc($ptype), \@params );
			$va{'cashpayment'} = 'ok';
		}else{
			$va{'cashpayment'} = 'prevuis_pay';
		}
	}elsif($in{'action'} eq 'tpv' and $in{'id_orders'} > 0 and $in{'step'} eq '2'){
		if($payment->{'Captured'} ne 'Yes'){
			$Pmtfield7 = 'Tpv';
			$Pmtfield8 = '1'; 
			$authcode = $in{'authnumber'};
			$last4cc = $in{'last4cc'};
			my ($sth) = &Do_SQL("UPDATE sl_orders SET status = 'Processed' , Ptype = 'Credit-Card' WHERE ID_orders = '$id_orders'");
			my ($sth) = &Do_SQL("SELECT sl_banks.ID_accounts, sl_banks.ShortName, sl_banks.BankName FROM sl_banks WHERE sl_banks.ID_banks = '$in{'id_banks'}' LIMIT 1;");
			($ida_banks, $shortname, $bankname) = $sth->fetchrow();
			&Do_SQL("UPDATE sl_orders_payments SET 
				PmtField3 = '$last4cc', 
				PmtField1 = '$shortname',
				PmtField4 = '$Pmtfield4', PmtField5 = '$in{'pmtfield5'}', PmtField6 = '$in{'pmtfield6'}',  PmtField7 = 'Credit-Card',
				 PmtField8 = '$Pmtfield8',  PmtField10 = '$Pmtfield10',
				AuthCode = '$authcode', Captured = 'Yes', CapDate = NOW(), Type = 'Credit-Card'
				WHERE
				ID_orders_payments = '$payment->{ID_orders_payments}'");

			my ($sth) = &Do_SQL("SELECT Ptype, Type FROM sl_orders INNER JOIN sl_customers USING(ID_customers) WHERE ID_orders = '$id_orders';");
			($order_type, $ctype) = $sth->fetchrow();
			#$ptype = 'deposit';
			$ptype = 'Credit-Card';
			@params = ($id_orders, $idpp, $ida_banks,1);
			&accounting_keypoints('order_deposit_'. lc($ctype) .'_'. lc($order_type) .'_'. lc($ptype), \@params );
			$va{'tpvpayment'} = 'ok';
		}else{
			$va{'tpvpayment'} = 'prevuis_pay';
		}
	}elsif($in{'action'} eq 'referenced_deposit' and $in{'id_orders'} > 0 and $in{'step'} eq '2'){
		if($payment->{'Captured'} ne 'Yes'){
			my ($sth) = &Do_SQL("UPDATE sl_orders SET status = 'NEW', Ptype = 'Referenced Deposit' WHERE ID_orders = '$id_orders'");
			$va{'referenced_deposit'} = 'ok';
		}else{
			$va{'cashpayment'} = 'prevuis_pay';
		}
		$in{'label'}  = "Mostrar Bancos";
		$in{'url_label'} = "/cgi-bin/mod/pos/admin?cmd=rd&id_orders=$id_orders";
		&Do_SQL("COMMIT");
	}elsif($in{'action'} eq 'creditCard'){
		if($payment->{'Captured'} ne 'Yes'){


			if( $cfg{'encrypt_cc'} and $cfg{'encrypt_cc'} == 1 ){
				$or = $in{'pmtfield3'};
				&Do_SQL("delete from sl_orders_cardsdata where id_orders = '$id_orders' and id_orders_payments = '$idpp'");
				&encrypt_cc($id_orders, $idpp, $or, $in{'month'}.$in{'year'}, 'ok');
				$in{'pmtfield3'} = substr($or, 0, 6)."xxxxxx".substr($or, -4);
				$in{'pmtfield4'} = 'xxxx';
				$in{'pmtfield5'} = '';
			}
			$ptmfield7 = 'Credit-Card';
			&Do_SQL("UPDATE sl_orders_payments SET 
				PmtField1 = '$in{'pmtfield1'}', 
				PmtField2 = '$in{'pmtfield2'}',
				PmtField3 = '$in{'pmtfield3'}',
				PmtField4 = '$in{'pmtfield4'}',
				PmtField7 = '$ptmfield7',
				PmtField8 = '$in{'pmtfield8'}',
				Type = 'Credit-Card'
				WHERE
				ID_orders_payments = '$payment->{ID_orders_payments}'");
			# cgierr("UPDATE sl_orders_payments SET 
			# 	PmtField1 = '$in{'pmtfield1'}', 
			# 	PmtField2 = '$in{'pmtfield2'}',
			# 	PmtField3 = '$in{'pmtfield3'}',
			# 	PmtField4 = '$in{'month'}$in{'year'}',
			# 	PmtField7 = '$ptmfield7',
			# 	PmtField8 = '$in{'pmtfield8'}'
			# 	WHERE
			# 	ID_orders_payments = '$payment->{ID_orders_payments}'");
			&Do_SQL("COMMIT");
			# cgierr($payment->{ID_orders_payments});
			my ($status,$message,$cybcod)= split(/\n/, &load_webpage("$cfg{'url_paymentgateway'}?e=$in{'e'}&id=$id_orders&idp=$idpp&cmd=$cfg{'paymentgateway_cmd_default'}&idu=$usr{'id_admin_users'}"),3);
			# cgierr("($status,$message,$cybcod)");
			&Do_SQL("start TRANSACTION");

			if($status =~ /OK/){
				my ($sth) = &Do_SQL("SELECT Ptype, Type FROM sl_orders INNER JOIN sl_customers USING(ID_customers) WHERE ID_orders = '$id_orders';");
				($order_type, $ctype) = $sth->fetchrow();
				$ptype = 'deposit';
				@params = ($id_orders, $idpp,1);
				&accounting_keypoints('order_deposit_'. lc($ctype) .'_'. lc($order_type) .'_'. lc($ptype), \@params );
				$va{'payu'}='ok';
			}else{
				Do_SQL('ROLLBACK');
				$va{'steptemp'} = 1;
				$va{'open'} = '#creditCard';
				$va{'message'} = 'ERROR AL PROCESAR TARJETA. '.$message;
			}
		}	
	}
	if($va{'tpvpayment'} eq 'ok' or $va{'cashpayment'} eq 'ok' or $va{'payu'} eq 'ok'){
		$in{'tracking'} = "$cfg{'prefixentershipment'}$id_orders\n$cfg{'default_traking'}\n";
		$in{'id_warehouses'} = $id_warehouses;
		$in{'shpdate'} = &get_sql_date();
		$in{'bulk'} = 1;
		$tmp_cmd = $in{'cmd'};
		$in{'cmd'} = 'entershipment';
		$in{'action'} = '1';
		$in{'skip_batch'} = 1;
		$response = &entershipment_pos();

		&Do_SQL(qq|INSERT INTO sl_debug(ID_debug, cmd, log, date, time) values(
			'$id_orders', 'POS', '$response', curdate(), curtime()
		)|);
		$id_invoices = Do_SQL("select id_invoices from cu_invoices_lines where id_orders = $id_orders limit 1")->fetchrow();
		&Do_SQL(qq|INSERT INTO sl_debug(ID_debug, cmd, log, date, time) values(
			'$id_orders', 'POS', '$in{'tracking'}', curdate(), curtime()
			)|);
		if($id_invoices){
			Do_SQL("update cu_invoices set customer_fname = '$in{'invoice_name'}' where id_invoices = $id_invoices");
		}
		if($va{'cashpayment'} eq 'ok'){
			&Do_SQL("UPDATE sl_orders SET Ptype = 'COD' WHERE ID_orders = '$id_orders'");
			&Do_SQL("UPDATE sl_orders_payments SET 
				Captured = null , CapDate = '0000-00-00'
				WHERE
				ID_orders_payments = '$payment->{ID_orders_payments}'");

		}
		$in{'cmd'} = $tmp_cmd;
		&Do_SQL("COMMIT");
		$in{'label'} = 'Imprimir Nota de Remisi&oacute;n';
		$in{'url_label'} = "/cgi-bin/mod/pos/admin?cmd=invoices&id_orders=$id_orders";
	}
1;
