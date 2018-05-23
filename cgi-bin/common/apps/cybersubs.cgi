#!/usr/bin/perl
##
## CyberSource Routines
##
##use CyberSource::SOAPI;
##%config = cybs_load_config( $cfg{'path_cybersource'}.'cybs.ini' );

sub capture_paypal {
# ----------------------------------------------------------------------------

	my ($id_orders,$id_orders_payments) = @_;

	my ($status,$message,$cybcod)= &paypal_capture($id_orders,$id_orders_payments);
	
	if($status =~ /ok/i) {

		my ($order_type, $ctype, $ptype,@params);
		my ($sth) = &Do_SQL("SELECT Ptype, Type FROM sl_orders INNER JOIN sl_customers USING(ID_customers) WHERE ID_orders = '$id_orders';");
		($order_type, $ctype) = $sth->fetchrow();
		$ptype = get_deposit_type($id_orders_payments,'');
		@params = ($id_orders, $id_orders_payments, 1);
		&accounting_keypoints('order_deposit_'. $ctype .'_'. $order_type .'_'. $ptype, \@params);

		### Revisar si necesita cambio de Status
		if ($cfg{'risk_status'} ne ''){

			use Cwd;
			my $dir = getcwd;
			my($home_dir,$a_cgibin) = split(/cgi-bin/,$dir);
			
			require ( $home_dir . '/cgi-bin/common/subs/sub.base.html.cgi');
			&orders_payments_risk_status($id_orders);
			
		}


	}
	
	return ($status,$message,$code);
}


sub sltvcyb_capture {
# ----------------------------------------------------------------------------
# Last Modified on: 09/30/08 11:13:51
# Last Modified by: MCC C. Gabriel Varela S: Se imprime el status que regresa la función cybs_run_transaction
# Last Modified on 12/10/2013 by: I.S.C. Alejandro Diaz: Se agrega switch para poder cobrar por plataforma banamex

	my ($id_orders,$id_orders_payments) = @_;
	my ($status,$message,$code);
	
	my ($banamex) = 0;
	if($cfg{'use_banamex_collection'} and $cfg{'use_banamex_collection'} == 1){
		my ($tmp_number) = &load_name('sl_orders_payments','ID_orders_payments',$id_orders_payments,'PmtField3');
		my ($sth) = &Do_SQL("SELECT count(*) FROM cu_cardprefix WHERE Prefix=left('$tmp_number',6) AND Bank like('BANAMEX%') AND Status='Active'");
		$banamex = $sth->fetchrow();
	}
	
	## Switch
	if($banamex and $cfg{'url_paymentgateway_banamex'} and $cfg{'url_paymentgateway_banamex'} ne ''){
		($status,$message,$code) = split(/\n/, &load_webpage("$cfg{'url_paymentgateway_banamex'}?id=$id_orders&idp=$id_orders_payments&cmd=$cfg{'paymentgateway_cmd_capture'}&idu=$usr{'id_admin_users'}&e=$in{'e'}"),3);
	}else{
		($status,$message,$code) = split(/\n/, &load_webpage("$cfg{'url_paymentgateway'}?id=$id_orders&idp=$id_orders_payments&cmd=$cfg{'paymentgateway_cmd_capture'}&idu=$usr{'id_admin_users'}&e=$in{'e'}"),3);
	}

	if($status =~ /ok/i) {

		my ($order_type, $ctype, $ptype,@params);
		my ($sth) = &Do_SQL("SELECT Ptype, Type FROM sl_orders INNER JOIN sl_customers USING(ID_customers) WHERE ID_orders = '$id_orders';");
		($order_type, $ctype) = $sth->fetchrow();
		$ptype = get_deposit_type($id_orders_payments,'');
		@params = ($id_orders, $id_orders_payments, 1);
		&accounting_keypoints('order_deposit_'. $ctype .'_'. $order_type .'_'. $ptype, \@params);

		### Revisar si necesita cambio de Status
		if ($cfg{'risk_status'} ne ''){

			use Cwd;
			my $dir = getcwd;
			my($home_dir,$a_cgibin) = split(/cgi-bin/,$dir);
			
			require ( $home_dir . '/cgi-bin/common/subs/sub.base.html.cgi');
			&orders_payments_risk_status($id_orders);
			
		}

	}
	#&cgierr("$status,$message") if $status !~/ok/i;
	
	return ($status,$message,$code);
}


sub sltvcyb_auth {
# --------------------------------------------------------
# Last Modified on: 15/08/2017 18:30:30 : Jonathan Alcantara : Se reemplaza cmd en la URL del paymentgateway para que lo tome de $cfg
	my ($id_orders, $id_orders_payments) = @_;
	my ($autoapproved, %request, $autocaptured, $comments);
	my ($status,$message,$code);

###
##	FC
###
	my ($activate_points,$points_to_use);
	if( $cfg{'use_points'} and $cfg{'use_points'} == 1 ){
		($id_orders,$id_orders_payments,$activate_points,$points_to_use) = @_;
	}
###
##	FC
###
	if ($usr{'application'} eq 'sales' and !$sys{'cc_verification_inb'}){
		$autoapproved =1;
	}elsif(!$sys{'cc_verification'} and !$in{'fromapp'}){
		$autoapproved =1;
	}else{
		$autoapproved = 0;
	}

	my ($order_type, $ctype, $ptype,@params);
	my ($sth) = &Do_SQL("SELECT Ptype, Type FROM sl_orders INNER JOIN sl_customers USING(ID_customers) WHERE ID_orders = '$id_orders';");
	($order_type, $ctype) = $sth->fetchrow();
	$ptype = get_deposit_type($id_orders_payments,'');
	@params = ($id_orders, $id_orders_payments, 1);
	

	if ($autoapproved){

		my ($sth) = &Do_SQL("UPDATE sl_orders SET Status='New' WHERE ID_orders='$id_orders' LIMIT 1;");
		my ($sth) = &Do_SQL("UPDATE sl_orders_payments SET Status='Approved',AuthCode='0000' WHERE ID_orders_payments='$id_orders_payments' LIMIT 1;");
		my ($sth) = &Do_SQL("INSERT INTO sl_orders_plogs SET ID_orders='$id_orders',ID_orders_payments='$id_orders_payments',Data='".&filter_values("Auto Approved Payment\n\nID_orders_payments=$id_orders_payments")."',Date=CURDATE(),Time=CURTIME(),ID_admin_users='$usr{'id_admin_users'}'");
		
		&auth_logging('opr_orders_stNew',$id_orders);
		&status_logging($id_orders,'New');

		if($cfg{'account_in_auth'}){
		
			&accounting_keypoints('order_deposit_'. $ctype .'_'. $order_type .'_'. $ptype, \@params);
			### Revisar si necesita cambio de Status
			if ($cfg{'risk_status'} ne ''){

				use Cwd;
				my $dir = getcwd;
				my($home_dir,$a_cgibin) = split(/cgi-bin/,$dir);
				
				require ( $home_dir . '/cgi-bin/common/subs/sub.base.html.cgi');
				&orders_payments_risk_status($id_orders);
				
			}

		}

		return ('OK','auto approved',0);
	}
	# exit;
###
##	FC
###
	my $url;
	if( $cfg{'use_points'} and $cfg{'use_points'} == 1 and $activate_points eq 'on' and $points_to_use > 0){
		# Banco de Puntos Santander Diestel
		$idBank = &Do_SQL("select Subcode from sl_vars_config 
			inner join sl_orders_payments on sl_vars_config.Code = substring(sl_orders_payments.PmtField3, 1 , 6)  
			where id_orders_payments='$id_orders_payments' limit 1")->fetchrow();
		$points_to_use =~ s/,//;
		my $onlyPoints = 0;
		# Cambiar monto del cobro
		# $num_consultas = $cses{'consultas'};
		# $folio = $cses{'id-transaccion'};
		# $comision = $cses{'comision'};
		$new_amount = &load_name("sl_orders_payments","id_orders_payments",$id_orders_payments,"amount") - $points_to_use;
		if($new_amount <= 0){
			$onlyPoints = 1;
		}

		if($onlyPoints){
			&Do_SQL("update sl_orders_payments set PmtField1='Mastercard - Puntos' where id_orders_payments=$id_orders_payments");
			$url_puntos = "$cfg{'url_paymentgateway'}?id=$id_orders&idp=$id_orders_payments&cmd=$cfg{'paymentgateway_cmd_puntos_santander'}&amount=$points_to_use&idu=$usr{'id_admin_users'}&e=$in{'e'}";

			# cgierr(&load_webpage($url_puntos));

			my ($statusPuntos,$msgPuntos,$codePuntos) = split(/\n/, &load_webpage($url_puntos),3);
			if($statusPuntos =~ /OK/i ){
				
				# Contabilidad de Puntos
				@params = ($id_orders, $id_orders_payments, $idBank, 1);
				&accounting_keypoints('order_deposit_'. $ctype .'_'. $order_type .'_'. $ptype, \@params);

				if ($cfg{'risk_status'} ne ''){
					use Cwd;
					my $dir = getcwd;
					my($home_dir,$a_cgibin) = split(/cgi-bin/,$dir);
					require ( $home_dir . '/cgi-bin/common/subs/sub.base.html.cgi');
					&orders_payments_risk_status($id_orders);
				}

				return ($statusPuntos,"$msgPuntos",$codePuntos);

			}else{
				return ($statusPuntos,"$msgPuntos",$codePuntos);
			}
		}else{
			# Actualizar Payment Original.
			&Do_SQL("update sl_orders_payments set Amount='$new_amount' where id_orders_payments=$id_orders_payments");
			# Creamos Payments de Puntos.
			&Do_SQL("insert into sl_orders_payments 
				(PmtField1, PmtField2, PmtField3, Amount, Type, ID_orders,Date, Time, ID_admin_users)
				SELECT 'Mastercard - Puntos' PmtField1, PmtField2, PmtField3, '$points_to_use' Amount,  Type, ID_orders, Date, Time, ID_admin_users 
				FROM sl_orders_payments WHERE id_orders_payments= $id_orders_payments limit 1;");

			$id_orders_payments_puntos = &Do_SQL("SELECT LAST_INSERT_ID();")->fetchrow();

			&Do_SQL("INSERT INTO sl_orders_cardsdata
				(ID_orders, ID_orders_payments, card_number, card_date, card_cvn, Date, Time, ID_admin_users)
				SELECT ID_orders, '$id_orders_payments_puntos' ID_orders_payments, card_number, card_date, card_cvn, Date, Time, ID_admin_users 
				FROM sl_orders_cardsdata
				WHERE id_orders = '$id_orders' AND id_orders_payments = '$id_orders_payments' LIMIT 1;");
			
			my $url = "$cfg{'url_paymentgateway'}?id=$id_orders&idp=$id_orders_payments&cmd=$cfg{'paymentgateway_cmd_default'}&idu=$usr{'id_admin_users'}&e=$in{'e'}";

			$url_puntos = "$cfg{'url_paymentgateway'}?id=$id_orders&idp=$id_orders_payments_puntos&cmd=$cfg{'paymentgateway_cmd_puntos_santander'}&amount=$points_to_use&idu=$usr{'id_admin_users'}&e=$in{'e'}";

			my ($statusCobro,$msgCobro,$codeCobro) = split(/\n/, &load_webpage($url),3);
			
			if($statusCobro =~ /OK/i){

				my ($statusPuntos,$msgPuntos,$codePuntos) = split(/\n/, &load_webpage($url_puntos),3);

				if($statusPuntos =~ /OK/i ){

					# Contabilidad de Cobro Normal
					&accounting_keypoints('order_deposit_'. $ctype .'_'. $order_type .'_'. $ptype, \@params);

					# Contabilidad de Puntos
					@params = ($id_orders, $id_orders_payments_puntos, $idBank, 1);
					&accounting_keypoints('order_deposit_'. $ctype .'_'. $order_type .'_'. $ptype, \@params);

					if ($cfg{'risk_status'} ne ''){
						use Cwd;
						my $dir = getcwd;
						my($home_dir,$a_cgibin) = split(/cgi-bin/,$dir);
						require ( $home_dir . '/cgi-bin/common/subs/sub.base.html.cgi');
						&orders_payments_risk_status($id_orders);
					}

					return ($statusPuntos,"$msgPuntos",$codePuntos);

				}else{

					my $url = "$cfg{'url_paymentgateway'}?id=$id_orders&idp=$id_orders_payments&cmd=$cfg{'paymentgateway_cmd_void'}&idu=$usr{'id_admin_users'}&e=$in{'e'}";
			
					# Reversar Pago Normal
					my ($statusReversa,$msgReversa,$codeReversa) = split(/\n/, &load_webpage($url),3);
					
					return ($statusPuntos,"$msgPuntos",$codePuntos);

				}

			}else{
				return ($statusCobro,$msgCobro,$codeCobro);
			}
		}
	}else{
		if ($cfg{'cybersource_enabled'} and $cfg{'cybersource_enabled'} == 1) {
			my ($sth) = &Do_SQL("SELECT sl_orders_plogs.Resp_code cybersource_id
								FROM sl_orders_payments
								INNER JOIN sl_orders_plogs ON sl_orders_plogs.ID_orders_payments = sl_orders_payments.ID_orders_payments
									AND sl_orders_plogs.Data LIKE '%CYBERSOURCE MODE%'
									AND sl_orders_plogs.Resp_msg = 'ACCEPT'
								WHERE sl_orders_payments.ID_orders_payments = ".$id_orders_payments."
								ORDER BY sl_orders_plogs.ID_orders_plogs DESC
								LIMIT 1
								;");
			$va{'cybersource_id'} = $sth->fetchrow;

			if ($va{'cybersource_id'} > 0) {
				$url = "$cfg{'url_paymentgateway'}?id=$id_orders&idp=$id_orders_payments&cmd=$cfg{'paymentgateway_cmd_default'}&idu=$usr{'id_admin_users'}&e=$in{'e'}&cybersource_id=$va{'cybersource_id'}";
			} else {
				$url = "$cfg{'url_paymentgateway'}?id=$id_orders&idp=$id_orders_payments&cmd=$cfg{'paymentgateway_cmd_default'}&idu=$usr{'id_admin_users'}&e=$in{'e'}";
			}
		} else {
			$url = "$cfg{'url_paymentgateway'}?id=$id_orders&idp=$id_orders_payments&cmd=$cfg{'paymentgateway_cmd_default'}&idu=$usr{'id_admin_users'}&e=$in{'e'}";
		}
		($status,$message,$code) = split(/\n/, &load_webpage($url),3);
	}
	# exit;
###
##	FC
###

	# &cgierr('url='.$url.'<br>'.'status='.$status.'<br>'.'message='.$message.'<br>'.'code='.$code.'<br>');
	# &cgierr(&load_webpage("$cfg{'url_paymentgateway'}?id=$id_orders&idp=$id_orders_payments&cmd=$cfg{'paymentgateway_cmd_default'}&idu=$usr{'id_admin_users'}&e=$in{'e'}"));
	
	if($status =~ /OK/i and $cfg{'account_in_auth'}) {

		
		&accounting_keypoints('order_deposit_'. $ctype .'_'. $order_type .'_'. $ptype, \@params);
		### Revisar si necesita cambio de Status
		if ($cfg{'risk_status'} ne ''){

			use Cwd;
			my $dir = getcwd;
			my($home_dir,$a_cgibin) = split(/cgi-bin/,$dir);
			
			require ( $home_dir . '/cgi-bin/common/subs/sub.base.html.cgi');
			&orders_payments_risk_status($id_orders);
			
		}

	}
	# cgierr("($status,$message,$code)");
	return ($status,$message,$code);

}

sub sltvcyb_postauth {
# --------------------------------------------------------
# Last Modified on: 
	my ($id_orders, $id_orders_payments) = @_;
	my ($autoapproved, %request, $autocaptured, $comments);
	my ($status,$message,$code);

	if ($usr{'application'} eq 'sales' and !$sys{'cc_verification_inb'}){
		$autoapproved =1;
	}elsif(!$sys{'cc_verification'} and !$in{'fromapp'}){
		$autoapproved =1;
	}else{
		$autoapproved = 0;
	}

	my ($order_type, $ctype, $ptype,@params);
	my ($sth) = &Do_SQL("SELECT Ptype, Type FROM sl_orders INNER JOIN sl_customers USING(ID_customers) WHERE ID_orders = '$id_orders';");
	($order_type, $ctype) = $sth->fetchrow();
	$ptype = get_deposit_type($id_orders_payments,'');
	@params = ($id_orders, $id_orders_payments, 1);

	if ($autoapproved){

		my ($sth) = &Do_SQL("UPDATE sl_orders SET Status='New' WHERE ID_orders='$id_orders' LIMIT 1;");
		my ($sth) = &Do_SQL("UPDATE sl_orders_payments SET Status='Approved',AuthCode='0000' WHERE ID_orders_payments='$id_orders_payments' LIMIT 1;");
		my ($sth) = &Do_SQL("INSERT INTO sl_orders_plogs SET ID_orders='$id_orders',ID_orders_payments='$id_orders_payments',Data='".&filter_values("Auto Approved Payment\n\nID_orders_payments=$id_orders_payments")."',Date=CURDATE(),Time=CURTIME(),ID_admin_users='$usr{'id_admin_users'}'");
		
		&auth_logging('opr_orders_stNew',$id_orders);
		&status_logging($id_orders,'New');

		if($cfg{'account_in_auth'}){
		
			&accounting_keypoints('order_deposit_'. $ctype .'_'. $order_type .'_'. $ptype, \@params);
			### Revisar si necesita cambio de Status
			if ($cfg{'risk_status'} ne ''){

				use Cwd;
				my $dir = getcwd;
				my($home_dir,$a_cgibin) = split(/cgi-bin/,$dir);
				
				require ( $home_dir . '/cgi-bin/common/subs/sub.base.html.cgi');
				&orders_payments_risk_status($id_orders);
				
			}

		}

		return ('OK','auto approved',0);
	}

	my $url;
	
	$url = "$cfg{'url_paymentgateway'}?id=$id_orders&idp=$id_orders_payments&cmd=$cfg{'paymentgateway_cmd_postauth'}&idu=$usr{'id_admin_users'}&e=$in{'e'}";

	($status,$message,$code) = split(/\n/, &load_webpage($url),3);
	
	if($status =~ /OK/i and $cfg{'account_in_auth'}) {

		
		&accounting_keypoints('order_deposit_'. $ctype .'_'. $order_type .'_'. $ptype, \@params);
		### Revisar si necesita cambio de Status
		if ($cfg{'risk_status'} ne ''){

			use Cwd;
			my $dir = getcwd;
			my($home_dir,$a_cgibin) = split(/cgi-bin/,$dir);
			
			require ( $home_dir . '/cgi-bin/common/subs/sub.base.html.cgi');
			&orders_payments_risk_status($id_orders);
			
		}

	}
	# cgierr("($status,$message,$code)");
	return ($status,$message,$code);
}					

sub sltvcyb_sale {
# --------------------------------------------------------
	my ($id_orders,$id_orders_payments) = @_;
	my ($autoapproved);
	if ($usr{'application'} eq 'sales' and !$sys{'cc_verification_inb'}){
		$autoapproved =1;
	}elsif(!$sys{'cc_verification'} and !$in{'fromapp'}){
		$autoapproved =1;
	}else{
		$autoapproved = 0
	}


	my ($order_type, $ctype, $ptype,@params);
	my ($sth) = &Do_SQL("SELECT Ptype, Type FROM sl_orders INNER JOIN sl_customers USING(ID_customers) WHERE ID_orders = '$id_orders';");
	($order_type, $ctype) = $sth->fetchrow();
	$ptype = get_deposit_type($id_orders_payments,'');
	@params = ($id_orders, $id_orders_payments, 1);


	if ($autoapproved){

		my ($sth) = &Do_SQL("UPDATE sl_orders SET Status='".$cfg{'statuscreateorder'}."' WHERE ID_orders='$id_orders'");
		my ($sth) = &Do_SQL("UPDATE sl_orders_payments SET Status='Approved',AuthCode='0000',CapDate=CURDATE() WHERE ID_orders_payments='$id_orders_payments'");
		my ($sth) = &Do_SQL("INSERT INTO sl_orders_plogs SET ID_orders='$id_orders',ID_orders_payments='$id_orders_payments',Data='".&filter_values("Auto Approved Payment\n\nID_orders_payments=$id_orders_payments")."',Date=Curdate(),Time=NOW(),ID_admin_users='$usr{'id_admin_users'}'");
		&auth_logging('opr_orders_st' . $cfg{'statuscreateorder'},$id_orders);
		&status_logging($id_orders, $cfg{'statuscreateorder'});
		
		## Movimientos Contables		
		&accounting_keypoints('order_deposit_'. $ctype .'_'. $order_type .'_'. $ptype, \@params);
		### Revisar si necesita cambio de Status
		if ($cfg{'risk_status'} ne ''){

			use Cwd;
			my $dir = getcwd;
			my($home_dir,$a_cgibin) = split(/cgi-bin/,$dir);
			
			require ( $home_dir . '/cgi-bin/common/subs/sub.base.html.cgi');
			&orders_payments_risk_status($id_orders);
			
		}

		return ('OK','auto approved',0);
	} 

	my ($status,$message)= split(/\n/,&load_webpage("$cfg{'url_paymentgateway'}?id=$id_orders&idp=$id_orders_payments&cmd=$cfg{'paymentgateway_cmd_sale'}&idu=$usr{'id_admin_users'}&e=$in{'e'}"),2); 

	## Movimientos Contables
	if($status =~ /ok/i) {

		&accounting_keypoints('order_deposit_'. $ctype .'_'. $order_type .'_'. $ptype, \@params);
		### Revisar si necesita cambio de Status
		if ($cfg{'risk_status'} ne ''){

			use Cwd;
			my $dir = getcwd;
			my($home_dir,$a_cgibin) = split(/cgi-bin/,$dir);
			
			require ( $home_dir . '/cgi-bin/common/subs/sub.base.html.cgi');
			&orders_payments_risk_status($id_orders);
			
		}

	}

	
	return ($status,$message);
}


sub sltvcyb_credit {
# --------------------------------------------------------
	my ($id_orders,$id_orders_payments) = @_;
	
	##use CyberSource::SOAPI;
	##%config = cybs_load_config( $cfg{'path_cybersource'}.'cybs.ini' );
	#$requestID = runAuth( \%config );


    # set up the request by creating an hash and adding fields to it
	my %request;
	my ($sth) = &Do_SQL("SELECT * FROM sl_orders WHERE ID_orders='$id_orders'");
	my ($rec_order) = $sth->fetchrow_hashref;
	
	my ($sth) = &Do_SQL("SELECT * FROM sl_customers WHERE ID_customers='$rec_order->{'ID_customers'}'");
	my ($rec_cust) = $sth->fetchrow_hashref;
	
	my ($sth) = &Do_SQL("SELECT * FROM sl_orders_payments WHERE ID_orders_payments='$id_orders_payments'");
	my ($rec_pay) = $sth->fetchrow_hashref;


	my ($status,$message)= split(/\n/, &load_webpage("$cfg{'url_paymentgateway'}?id=$id_orders&idp=$id_orders_payments&cmd=$cfg{'paymentgateway_cmd_credit'}&idu=$usr{'id_admin_users'}&e=$in{'e'}"),2);
	
	if($status =~ /ok/i) {

		my ($order_type, $ctype, $ptype,@params);
		my ($sth) = &Do_SQL("SELECT Ptype, Type FROM sl_orders INNER JOIN sl_customers USING(ID_customers) WHERE ID_orders = '$in{'id_orders'}';");
		($order_type, $ctype) = $sth->fetchrow();
		$ptype = get_deposit_type($id_orders_payments,'');
		@params = ($id_orders, $id_orders_payments, 1);
		&accounting_keypoints('order_refund_'. $ctype .'_'. $order_type .'_'. $ptype, \@params);

	}


	return ($status,$message);
}

sub load_ccerror_msg {
# ----------------------------------------------------------------------------
	my (%tmp) = @_;
	#	AVS : ($reply{'ccAuthReply_avsCode'}) $reply{'msg_avsCode'}<br>
	#	Risk Factor Code : ($reply{'ccAuthReply_authFactorCode'}) $reply{'msg_authFactorCode'}<br>
	#	CVN Code : ($reply{'ccAuthReply_cvCode'}) $reply{'msg_cvCode'}<br>
	
	my ($sth) = &Do_SQL("SELECT Definition_En FROM sl_vars WHERE VName='cybavs' AND VValue='$tmp{'ccAuthReply_avsCode'}'");
	$tmp{'msg_avsCode'} = $sth->fetchrow;
	
	my ($sth) = &Do_SQL("SELECT Definition_En FROM sl_vars WHERE VName='cybfactor' AND VValue='$tmp{'ccAuthReply_authFactorCode'}'");
	$tmp{'msg_authFactorCode'} = $sth->fetchrow;
	
	my ($sth) = &Do_SQL("SELECT Definition_En FROM sl_vars WHERE VName='cybcvn' AND VValue='$tmp{'ccAuthReply_cvCode'}'");
	$tmp{'msg_cvCode'} = $sth->fetchrow;
	
	my ($sth) = &Do_SQL("SELECT Definition_En FROM sl_vars WHERE VName='cybersource' AND VValue='$tmp{'reasonCode'}'");
	$tmp{'msg_reasonCode'} = $sth->fetchrow;
	if ($tmp{'reasonCode'} eq '101' or $tmp{'reasonCode'} eq '102'){
		foreach my $key (keys %tmp){
			if ($key =~ /^missingField_\d+/){
				$tmp{'msg_reasonCode'} .= "<br> $tmp{$key} Missing";
			}elsif($key =~ /invalidField_\d+/){
				$tmp{'msg_reasonCode'} .= "<br> $tmp{$key} Invalid";
			}
		}
	}
	return %tmp;
}

sub load_paylogs_ccdata {
# ----------------------------------------------------------------------------
	my ($pRequest, $pReply) = @_;
	my ($output) = "Submited Info\n";
	foreach my $key (keys %{$pRequest}){
		$output .= "$key = $pRequest->{$key}\n";
	}
	$output .= "\nReply Info\n";
	foreach my $key (keys %{$pReply}){
		$output .= "$key = $pReply->{$key}\n";
	}
	return &filter_values($output);
}


sub check_address {
# --------------------------------------------------------
	my ($id_orders) = @_;
	my ($sth,$rec,$bill,$shp);
	my ($sth) = &Do_SQL("SELECT * FROM sl_orders WHERE ID_orders='$id_orders'");
	my ($rec) = $sth->fetchrow_hashref;

	##################################
	# Create a request (BILLING INFO)
	##################################
	use LWP::UserAgent;
	use HTTP::Request::Common;
	$ua=new LWP::UserAgent;		
	my $req = HTTP::Request->new(GET => "http://zip4.usps.com/zip4/zcl_0_results.jsp?visited=1&pagenumber=0&firmname=0&address2=$rec->{'Address1'}&address1=$rec->{'Address2'}&city=$rec->{'City'}&urbanization=$rec->{'Urbanization'}&zip5=$rec->{'Zip'}&city=>$rec->{'City'}&state=");
	
	# Pass request to the user agent and get a response back
	$resp = $ua->request($req);
	if ($resp->is_success){
		my (@lines,$error,$prt);
		@lines = split(/\n/,$resp->content);
		for (0..$#lines){
			($prt) and ($output .= $lines[$_]);
			if ($lines[$_] =~ /headers="non"/){
				$error = 1;
				$prt = 1;
			}elsif ($prt and $lines[$_] =~ /<\/td>/){
				$prt = 0;
			}elsif ($lines[$_] =~ /headers="full"/){
				$ok = 1;
				$prt = 1;
			}
			
		}
		if ($ok){
			$bill = 'OK';
		}else{
			$bill = 'ERROR';
		}
	}else{
		$bill = 'ERROR';
	}
	
	##################################
	# Create a request (BILLING INFO)
	##################################
	$output = '';
	$ok = '';
	my $req = HTTP::Request->new(GET => "http://zip4.usps.com/zip4/zcl_0_results.jsp?visited=1&pagenumber=0&firmname=0&address2=$rec->{'shp_Address1'}&address1=$rec->{'shp_Address2'}&city=$rec->{'shp_City'}&urbanization=$rec->{'shp_Urbanization'}&zip5=$rec->{'shp_Zip'}&city=>$rec->{'shp_City'}&state=");
	
	# Pass request to the user agent and get a response back
	$resp = $ua->request($req);
	print "&nbsp;";
	if ($resp->is_success){
		my (@lines,$error,$prt);
		@lines = split(/\n/,$resp->content);
		for (0..$#lines){
			($prt) and ($output .= $lines[$_]);
			if ($lines[$_] =~ /headers="non"/){
				$error = 1;
				$prt = 1;
			}elsif ($prt and $lines[$_] =~ /<\/td>/){
				$prt = 0;
			}elsif ($lines[$_] =~ /headers="full"/){
				$ok = 1;
				$prt = 1;
			}
			
		}
		if ($ok){
			$shp = 'OK';
		}else{
			$shp = 'ERROR';
		}
	}else{
		$shp = 'ERROR';
	}
	return ($bill,$shp);
}

sub filter_chars {
# ----------------------------------------------------------------------------
	my (%tmp) = @_;
	foreach $key (keys %tmp){
		$tmp{$key} =~ s/á/a/g;
		$tmp{$key} =~ s/é/e/g;
		$tmp{$key} =~ s/í/i/g;
		$tmp{$key} =~ s/ó/o/g;
		$tmp{$key} =~ s/ú/u/g;
		$tmp{$key} =~ s/Á/A/g;
		$tmp{$key} =~ s/É/E/g;
		$tmp{$key} =~ s/Í/I/g;
		$tmp{$key} =~ s/Ó/O/g;
		$tmp{$key} =~ s/Ú/U/g;
		$tmp{$key} =~ s/ñ/n/g;
		$tmp{$key} =~ s/Ñ/N/g;
	}
	return %tmp;
}



sub checkavs {
# --------------------------------------------------------
# Created on: 01/08/09 @ 13:39:28
# Author: Carlos Haas
# Last Modified on: 01/08/09 @ 13:39:28
# Last Modified by: Carlos Haas
# Description : 
# Parameters : 
#	
	my (@ary) = split(/\n/, &load_webpage("$cfg{'url_paymentgateway'}?id=$in{'id_orders'}&idp=$in{'id_orders_payments'}&cmd=$cfg{'paymentgateway_cmd_checkavs'}&idu=$usr{'id_admin_users'}&e=$in{'e'}"),2);
	print $ary[1];
}


1;
