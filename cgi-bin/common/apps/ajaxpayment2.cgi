#!/usr/bin/perl
#######################################################################
#######################################################################
#######################################################################
use DBI;
use DBIx::Connector;
use DBD::mysql;

# Load the form information and set the config file and userid.
local(%in) = &parse_form;
local($sid,%perm);
$in{'sid'} ? ($sid   = $in{'sid'}): ($sid   = '');

# Required Libraries
# --------------------------------------------------------
eval {
	require ("../subs/auth.cgi");
	require ("../subs/sub.base.html.cgi");
	require ("ajaxpayment.cfg");
	};
if ($@) { &cgierr ("Error loading required Libraries",300,$@); }

eval { &main; };
if ($@) { &cgierr("Fatal error,301,$@"); }

exit;

sub main {
# --------------------------------------------------------
	$|++;
	&connect_db;
	&auth_cleanup;
	my ($status) = &auth_check_password;
	if ($status eq "ok") {
		my ($cmd) = $in{'ajaxbuild'};
		if (defined &$cmd){	
			&connect_db;
			&$cmd();
			return;
		}
		&html_blank;
	}else {
		&html_blank;
	}
	&disconnect_db;
}

##########################################################
##		CREDIT CARD
##########################################################

sub creditcard {
# --------------------------------------------------------
# Last Modified on: 10/02/08 13:11:30
# Last Modified by: MCC C. Gabriel Varela S: Se actualizará el posteddate en caso de que el pago sea procedente de un return de tipo Refund
# Last Modified on: 15/08/2017 18:30:30 : Jonathan Alcantara : Se reemplaza cmd en la URL del paymentgateway para que lo tome de $cfg

	my ($status,$message,$cybcod)= split(/\n/, &load_webpage("$cfg{'url_paymentgateway'}?id=$in{'id_orders'}&idp=$in{'id_orders_payments'}&cmd=$cfg{'paymentgateway_cmd_default'}&idu=$usr{'id_admin_users'}"),3);

	print "Content-type: text/html\n\n";
	($status eq 'ERROR') ? ($message = "<p>&nbsp;</p><b>$message</b><p>&nbsp;</p>"):
		($message = "<b>Authorization Approved</b><br>$message</b><p>&nbsp;</p>");
	print qq|
				<table border="0" cellspacing="0" cellpadding="2" width="350" bgcolor="#FFCFCE">
				<tr>
					<td align="center">$message</td>
				</tr>
				</table>
			|;	
	return;
}					

sub ccsale {
#-----------------------------------------
# Created on: 
# Forms Involved: 
# Description : Authorize/Capture payment lines
# Parameters : $in{'id_orders'}	$in{'id_orders_payments'}
# Last Modified RB: 12/02/08  09:54:32 Added StatusPay change for pending payments

	my ($status,$message,$cybcod)= split(/\n/, &load_webpage("$cfg{'url_paymentgateway'}?id=$in{'id_orders'}&idp=$in{'id_orders_payments'}&cmd=$cfg{'paymentgateway_cmd_sale'}&idu=$usr{'id_admin_users'}"),3);

	print "Content-type: text/html\n\n";
	($status eq 'ERROR') ? ($message = "<p>&nbsp;</p><b>$message</b><p>&nbsp;</p>"):
		($message = "<b>SALE Approved (Auth+Capt))</b><br>$message</b><p>&nbsp;</p>");
	print qq|
				<table border="0" cellspacing="0" cellpadding="2" width="350" bgcolor="#FFCFCE">
				<tr>
					<td align="center">$message</td>
				</tr>
				</table>
			|;	
	return;
}	

sub cccredit {
#-----------------------------------------
# Created on: 12/02/08  09:58:01 By  Roberto Barcenas
# Forms Involved: 
# Description : Capture credit lines
# Parameters : $in{'id_orders'}	$in{'id_orders_payments'}
# Last Modified on: 10/02/08 12:03:22
# Last Modified by: MCC C. Gabriel Varela S: Se actualizará el posteddate en caso de que el pago sea procedente de un return de tipo Refund
# Last Modified RB: 12/02/08  09:58:40

	my ($status,$message,$cybcod)= split(/\n/, &load_webpage("$cfg{'url_paymentgateway'}?id=$in{'id_orders'}&idp=$in{'id_orders_payments'}&cmd=$cfg{'paymentgateway_cmd_credit'}&idu=$usr{'id_admin_users'}"),3);

	print "Content-type: text/html\n\n";
	($status eq 'ERROR') ? ($message = "<p>&nbsp;</p><b>$message</b><p>&nbsp;</p>"):
		($message = "<b>Credit Approved</b><br>$message</b><p>&nbsp;</p>");
	print qq|
				<table border="0" cellspacing="0" cellpadding="2" width="350" bgcolor="#FFCFCE">
				<tr>
					<td align="center">$message</td>
				</tr>
				</table>
			|;	
	return;
}

sub capture {
# ----------------------------------------------------------------------------
	my ($status,$message,$cybcod)= split(/\n/, &load_webpage("$cfg{'url_paymentgateway'}?id=$in{'id_orders'}&idp=$in{'id_orders_payments'}&cmd=sltvcyb_capture&idu=$usr{'id_admin_users'}"),3);

	print "Content-type: text/html\n\n";
	($status eq 'ERROR') ? ($message = "<p>&nbsp;</p><b>$message</b><p>&nbsp;</p>"):
		($message = "<b>Transaction Captured</b><br>$message</b><p>&nbsp;</p>");
	print qq|
				<table border="0" cellspacing="0" cellpadding="2" width="350" bgcolor="#FFCFCE">
				<tr>
					<td align="center">$message</td>
				</tr>
				</table>
			|;	
	return;
}


sub tocapture {
# ----------------------------------------------------------------------------
	print "Content-type: text/html\n\n";
	print qq|
				<table border="0" cellspacing="0" cellpadding="2" width="350" bgcolor="#DEFFCA">
				<tr>
					<td align="center"><p>&nbsp;</p><b>Order $in{'id_orders'} to Captured</b><p>&nbsp;</p></td>
				</tr>
				</table>\n|;
	## CAPTURE REJECTED
	
	&add_order_notes_by_type($in{'id_orders'},"Set to Captured","Low");
	my ($sth) = &Do_SQL("UPDATE sl_orders_payments SET Captured='Yes' WHERE ID_orders_payments='$in{'id_orders_payments'}'");
	&auth_logging('opr_orders_caperror',$in{'id_orders'});
}


##########################################################
##		LAYAWAY 
##########################################################


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

sub importcapture {
# ----------------------------------------------------------------------------
	print "Content-type: text/html\n\n";
	print qq|
				<table border="0" cellspacing="0" cellpadding="2" width="350" bgcolor="#DEFFCA">
				<tr>
					<td align="center"><p>&nbsp;</p><b>Order $in{'id_orders'} to Captured on: $in{'cdate'}</b><p>&nbsp;</p></td>
				</tr>
				</table>\n|;
	## CAPTURE REJECTED
	my ($sth) = &Do_SQL("INSERT INTO sl_import_log SET ID_import_log='$in{'refnum'}',Type='Cybersource',ID_orders='$in{'id_orders'}',ID_orders_payments='$in{'id_orders_payments'}',IData='---',Date=Curdate(),Time=NOW(),ID_admin_users='$usr{'id_admin_users'}';");
	my ($sth) = &Do_SQL("UPDATE sl_orders_payments SET Captured='Yes',CapDate='$rec{'cdate'}' WHERE ID_orders_payments='$in{'id_orders_payments'}'");
}

##########################################################
##		GENERAL SUBS			##
##########################################################
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
		foreach $key (keys %tmp){
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
	my($pRequest, $pReply) = @_;
	my ($output);
	$output = "Submited Info\n";
	foreach $key (keys %{$pRequest}){
		$output .= "$key = $pRequest->{$key}\n";
	}
	$output .= "\nReply Info\n";
	foreach $key (keys %{$pReply}){
		$output .= "$key = $pReply->{$key}\n";
	}
	return &filter_values($output);
}

sub handleError {
# ----------------------------------------------------------------------------
	my($nStatus, $pRequest, $pReply) = @_;

	#print "RunTransaction Status: $nStatus\n";

	if ( $nStatus == CYBS_S_PERL_PARAM_ERROR ) {
		#printf( "Please check the parameters passed to cybs_run_transaction for correctness.\n" );
		return  "Please check the parameters passed to cybs_run_transaction for correctness.";
	}elsif ( $nStatus == CYBS_S_PRE_SEND_ERROR ) {
		#printf(	"The following error occurred before the request could be sent:\n%s\n",
		#		$$pReply{+CYBS_SK_ERROR_INFO} );
		return "The following error occurred before the request could be sent: " . $$pReply{+CYBS_SK_ERROR_INFO};
	}elsif ( $nStatus == CYBS_S_SEND_ERROR ) {
		#printf( "The following error occurred while sending the request:\n%s\n",
		#		$$pReply{+CYBS_SK_ERROR_INFO} );
		return "The following error occurred while sending the request: " . $$pReply{+CYBS_SK_ERROR_INFO}
	}elsif ( $nStatus == CYBS_S_RECEIVE_ERROR ) {
		#printf( "The following error occurred while waiting for or retrieving the reply:\n%s\n",
		#		$$pReply{+CYBS_SK_ERROR_INFO} );
		return "The following error occurred while waiting for or retrieving the reply: " . $$pReply{+CYBS_SK_ERROR_INFO} . handleCriticalError($nStatus, $pRequest, $pReply);
	}elsif ( $nStatus == CYBS_S_POST_RECEIVE_ERROR ) {
		#printf(	"The following error occurred after receiving and during processing of the reply:\n%s\n",
		#		$$pReply{+CYBS_SK_ERROR_INFO} );
		return "The following error occurred after receiving and during processing of the reply: " . $$pReply{+CYBS_SK_ERROR_INFO} . handleCriticalError($nStatus, $pRequest, $pReply);
	}elsif ( $nStatus == CYBS_S_CRITICAL_SERVER_FAULT ) {
		#printf( "The server returned a CriticalServerError fault:\n%s\n", 
		#		getFaultContent($pReply) );
		return "The server returned a CriticalServerError fault: ". getFaultContent($pReply) . handleCriticalError($nStatus, $pRequest, $pReply);
	}elsif ( $nStatus == CYBS_S_SERVER_FAULT ) {
		#printf( "The server returned a ServerError fault:\n%s\n", getFaultContent($pReply) );
		return "The server returned a ServerError fault: " . getFaultContent($pReply);
	}elsif ( $nStatus == CYBS_S_OTHER_FAULT ) {
		#printf( "The server returned a fault:\n%s\n", getFaultContent($pReply) );
		return "The server returned a fault: " . getFaultContent($pReply) ;
	}elsif ( $nStatus == CYBS_S_HTTP_ERROR ) {
		#printf(	"An HTTP error occurred:\n%s\nResponse Body:\n%s\n",
		#		$$pReply{+CYBS_SK_ERROR_INFO}, $$pReply{+CYBS_SK_RAW_REPLY} );
		return "An HTTP error occurred:\n%s\nResponse Body: " . $$pReply{+CYBS_SK_ERROR_INFO} . $$pReply{+CYBS_SK_RAW_REPLY};
	}
}


# ----------------------------------------------------------------------------
# If an error occurs after the request has been sent to the server, but the
# client cannot determine whether the transaction was successful, then the
# error is considered critical.  If a critical error happens, the transaction
# may be complete in the CyberSource system but not complete in your order
# system.  Because the transaction may have been successfully processed by
# CyberSource, you should not resend the transaction, but instead send the
# error information and the order information (customer name, order number,
# etc.) to the appropriate personnel at your company.  They should use the
# information as search criteria within the CyberSource Transaction Search
# Screens to find the transaction and determine if it was successfully
# processed. If it was, you should update your order system with the
# transaction information. Note that this is only a recommendation; it may not
# apply to your business model.

sub handleCriticalError {
# ----------------------------------------------------------------------------
	my($nStatus, $pRequest, $pReply) = @_;
	my($ReplyType, $ReplyText, $messageToSend);

	$ReplyType = NULL;
	$ReplyText = NULL;
	
	if ($nStatus == CYBS_S_CRITICAL_SERVER_FAULT) {
		$ReplyType = 'FAULT DETAILS: ';
		$ReplyText = getFaultContent( $pReply );
	}else {
		$ReplyText = $$pReply{+CYBS_SK_RAW_REPLY};
		if ($ReplyText != NULL) {
			$ReplyType = 'RAW REPLY: ';
		} else {
			$ReplyType = "No Reply available.";
		}
	}

	$messageToSend = sprintf( "STATUS: %d\nERROR INFO: %s\nREQUEST: \n%s\n%s\n%s\n",
							  nStatus, $$pReply{+CYBS_SK_ERROR_INFO},
							  getArrayContent( $pRequest ), $ReplyType, $ReplyText );
		  
	# send $messageToSend to the appropriate personnel at your company
	# using any suitable method, e.g. e-mail, multicast log, etc.
	#
	# this sample code simply sends it to standard output.

	#printf( "\nThis is a critical error.  Send the following information to the appropriate personnel at your company: \n%s\n",
	#		$messageToSend );
	return "This is a critical error.  Send the following information to the appropriate personnel at your company: " . $messageToSend;
}


sub getFaultContent {
# ----------------------------------------------------------------------------
	my($pReply) = @_;
	my $requestID;
	
	$requestID = $$pReply{+CYBS_SK_FAULT_REQUEST_ID};
	if ( $requestID == "") {
		$requestID = "(unavailable)";
	}
	
	return( sprintf( "Fault code: %s\nFault string: %s\nRequestID: %s\nFault document: %s",
					 $$pReply{+CYBS_SK_FAULT_CODE}, $$pReply{+CYBS_SK_FAULT_STRING},
					 $requestID, $$pReply{+CYBS_SK_FAULT_DOCUMENT} ) );
}

				
sub getArrayContent {
# ----------------------------------------------------------------------------
	my($phash) = @_;
	my($key, $value);
	my $content = '';

	while ( ($key,$value) = each %$phash ) {
		$content = $content . $key . ' => ' . $value . "\n";
	}

	return( $content );
}

##########################################################
##		CHECK 
########################################################
sub certegycheck {
# --------------------------------------------------------
# Last Modified on: 10/02/08 12:03:22
# Last Modified by: MCC C. Gabriel Varela S: Se actualizará el posteddate en caso de que el pago sea procedente de un return de tipo Refund
	use HTTP::Request::Common qw(POST);
	use HTML::Form;
	use LWP::UserAgent;
	use Switch;
	print "Content-type: text/html\n\n";
	my ($id_orders) = $in{'id_orders'};
	my ($id_orders_payments) = $in{'id_orders_payments'};
	### Load Order / Payment Info
	my (%rec,$decition,$message,$msg_code,$auth_code);
	my ($sth) = &Do_SQL("SELECT * FROM sl_orders WHERE ID_orders='$in{'id_orders'}'");
	my ($rec_order) = $sth->fetchrow_hashref;
	
	my ($sth) = &Do_SQL("SELECT * FROM sl_customers WHERE ID_customers='$rec_order->{'ID_customers'}'");
	my ($rec_cust) = $sth->fetchrow_hashref;
	
	my ($sth) = &Do_SQL("SELECT * FROM sl_orders_payments WHERE ID_orders_payments='$in{'id_orders_payments'}'");
	my ($rec_pay) = $sth->fetchrow_hashref;



	#################################
	#### Check ALREADY Processed
	#################################
	if  (($rec_pay->{'AuthCode'} ne '0000' and $rec_pay->{'AuthCode'}) and ($rec_pay->{'Status'} eq 'Approved' or $rec_pay->{'AuthCode'})){
		print qq|
				<table border="0" cellspacing="0" cellpadding="2" width="350" bgcolor="#FFCFCE">
				<tr>
					<td align="center"><p>&nbsp;</p><b>Check Already Proceesed</b><p>&nbsp;</p></td>
				</tr>
				</table>
			|;	
		return;
	}



	#SI Driver License State
	$rec{'SI'} = substr($rec_pay->{'PmtField7'},0,2);

	#Customer_Id
	$rec{'Customer_Id'} = $rec_order->{'ID_customers'};
	
	#SA Current Address Street
	$rec{'SA'} = $rec_order->{'Address1'};
	#CT Current Address
	$rec{'CT'} = $rec_order->{'City'};
	#ST State
	$rec{'ST'} = substr($rec_order->{'State'},0,2);	
	#ZP zip code
	$rec{'ZP'} = $rec_order->{'Zip'};
	#HP Home Phone
	$rec{'HP'} = $rec_pay->{'PmtField9'};

	
#NM Company Name
	$rec{'NM'} = $rec_pay->{'PmtField1'};
	
	#FM&nbsp; FULL MCIR  *063100277*0911895435434*12215467*
	$rec{'FM'} = "*$rec_pay->{'PmtField2'}*$rec_pay->{'PmtField3'}*$rec_pay->{'PmtField4'}*";

	#Driver Licence
	$rec{'DL'} = $rec_pay->{'PmtField6'};
	
	#Chk_Check_No
	$rec{'Chk_Check_No'} = $rec_pay->{'PmtField4'};
	
	#DB Date of Birth MMDDYYY
	($month,$day,$year) = split(/-/,$rec_pay->{'PmtField5'},3);
	$rec{'DB'} = "$month$day$year";
	
	#Chk_Check_Type
	$rec{'Chk_Check_Type'} = uc($rec_pay->{'PmtField8'});
	
	#Extended_Results
	$rec{'Extended_Results'} = 'X';
	
	#Chk_Station_Number
	if ($rec{'Chk_Check_Type'} eq 'P'){
		$rec{'Chk_Station_Number'} = "1069512205";
		my (@ary) = split(/,/,$rec_pay->{'PmtField1'},2);
		#FN First Name
		$rec{'FN'} = $ary[0];
		#LN last name
		$rec{'LN'} = $ary[1];	
	}else{
		my (@ary) = split(/,/,$rec_pay->{'PmtField1'},3);
		#FN First Name
		$rec{'FN'} = $ary[0];
		#LN last name
		$rec{'LN'} = $ary[1];

		$rec{'Chk_Station_Number'} = "1069512303";
		$rec{'NM'} = $ary[2];
	}
	# 1069512205 = TEL Personal<br>
	# 1069512303 = TEL Company<br>
	# 1069586906 = WEB Personal<br>
	# 1069587000 = WEB Company<br>
	
	#Total_Amount_of_Purchase
	$rec{'Total_Amount_of_Purchase'} = $rec_pay->{'Amount'};
	
	#Paynet
	$rec{'Paynet'} = "Pay+By+Check";
	
	#Merchant_Transaction_No
	$rec{'Merchant_Transaction_No'} = "1184080536785";
	
	#Service_Request
	$rec{'Service_Request'} = "L1a";
	
	#Merchant_Id
	$rec{'Merchant_Id'} = "0000214781";

	############
	$output = "## Submitted Data\n";
	foreach $key (keys %rec){
		$tmpStr .= "$key=$rec{$key}&";
		$output .= "$key=$rec{$key}\n";
	}
	chop($tmpStr);
	$output .= "\n\n## First Reply Info";
	#$cfg{'cd'}=1;
	#&cgierr("$id_orders - $id_orders_payments  ");
	$ua = LWP::UserAgent->new;
	$ua->default_header('Authorization' => "Basic UGF5TmV0LlNob3Bsbjo1ZW14NGdueGdhaHQxNDN3cXVr");

	if ($cfg{'cd'}){
		$req = HTTP::Request->new(POST =>'https://transtest2.certegy.com/webapp/PayNet/L1/pgMerchantL1');
	}else{
		$req = HTTP::Request->new(POST =>'https://transprod.certegy.com/webapp/PayNet/L1/pgMerchantL1');
	}
	$req->content_type('application/x-www-form-urlencoded');
	$req->content($tmpStr);
	$response = $ua->request($req);
	$reply = $response->content;
	
	#print "start<br>";
	#print $reply;
	#print "end<br>";
	
	$merchantId =  trans( substr( $reply, 2, 13 ) );
	$transNum = trans( substr( $reply, 15, 30 ) );
	$transId = trans( substr( $reply, 45, 30 ) );
	$transStatus = trans( substr( $reply, 75, 2 ) );
	$echeckAuth = trans( substr($reply, 77, 8) );
	$echeckNum = trans( substr($reply, 85, 10) );
	$echeckDate = trans( substr($reply, 95, 8) );
	$echeckAmt = trans( substr($reply, 103, 10) );
	$response = trans( substr($reply, 113, 4) );
	
	if ($response ne '0101'){
		$decition = "REJECT";
		$message = &load_chkerror_msg($transStatus,$response);
		$msg_code = "$transStatus $response";
		$output .= "decision=REJECT\n";
		$output .= "decision_msg=$message\n";
		$do_2step = 0;
	}else{
		$do_2step = 1;
		$auth_code = $echeckAuth;
	}
	### First Step Resp
	$output .= "MerchantID=$merchantId\n";
	$output .= "MerchantTransactionNumber=$transNum\n";
	$output .= "PayNetTransactionID=$transId\n";
	$output .= "PayNetTransactionStatus=$transStatus\n";
	$output .= "PayNetECheckAuthorizationNumber=$echeckAuth\n";
	$output .= "PayNetECheckNumber=$echeckNum\n";
	$output .= "PayNetECheckDate=$echeckDate\n";
	$output .= "PayNetECheckAmount=$echeckAmt\n";
	$output .= "PayNetResponseSubcode=$response\n";
	#$output .= "PayNetResponse=".getCodeDef( $transStatus, $response )."\n";

	#print "2";
	
	if ($do_2step ){
		$output .= "\n\n";
		$merchantId = int($merchantId);
		$transId = int($transId);
		$echeckAmt =~ s/\s//g;
		#sleep(2);
		$tmpstr = "Merchant_Id=0000214781&PayNet_Transaction_Id=$transId&Request_Type=RECEIPT&Adjustment_Amount=$echeckAmt&Paynet=Cancel+Auth"; 
		#print "<br>Return STR<br>$tmpstr<br>";
		
		$ua = LWP::UserAgent->new;
		$ua->default_header('Authorization' => "Basic UGF5TmV0LlNob3Bsbjo1ZW14NGdueGdhaHQxNDN3cXVr");
		
		#$req2 = HTTP::Request->new(POST =>'https://transprod.certegy.com/webapp/PayNet/Receipt/pgReceiptVerification');
		#$req = HTTP::Request->new(POST =>'https://transtest2.certegy.com/webapp/PayNet/Receipt/pgReceiptVerification');
		
		if ($cfg{'cd'}){
			$response = $ua->get("https://transtest2.certegy.com/webapp/PayNet/Receipt/pgReceiptVerification?$tmpstr");
		}else{
			$response = $ua->get("https://transprod.certegy.com/webapp/PayNet/Receipt/pgReceiptVerification?$tmpstr");
		}
		$output .= "##SecondResponse\n";
		
		#print "3";
		if ($response->is_success){
			$decition = "APPROVED";
			$output .= "Response=OK\n";
			$txt = $response->content;
			$txt = substr($txt,36);
			$txt =~ s/<INPUT name="//g;
			$txt =~ s/" type="hidden" value="/=/g;
			$txt =~ s/" >//g;
			$txt =~ s/    //g;
			$txt =~ s/<\/body>//g;
			$txt =~ s/<\/html>//g;
			$txt =~ s/>//g;
			$txt =~ s/<//g;
			
			$output .= $txt;
		}else{
			$decition = "ERROR";
			$message = $response->status_line;
			$output .= "Error=$message\n";
		}
	}
	if ($decition eq "APPROVED"){
		print qq|
				<table border="0" cellspacing="0" cellpadding="2" width="350" bgcolor="#DEFFCA">
				<tr>
					<td align="center"><p>&nbsp;</p><b>Check Approved<br>
					Order: $id_orders</b><p>&nbsp;</p></td>
				</tr>
				</table>
			|;
		
		if ($rec_order->{'Status'} ne 'Shipped'){

			my ($sth) = &Do_SQL("UPDATE sl_orders SET Status='Processed' WHERE ID_orders='$id_orders'");
			&auth_logging('opr_orders_stProcessed',$id_orders);
			&status_logging($id_orders,'Processed');

		}


		my ($sth) = &Do_SQL("UPDATE sl_orders_payments SET Status='Approved',AuthCode='$auth_code ',AuthDateTime=NOW(),CapDate=IF(TIMESTAMPDIFF(SECOND,CONCAT(CURDATE(),' 21:00:00'),NOW()) >= 1,DATE_ADD(CURDATE(),INTERVAL 1 DAY),CURDATE()),Captured='Yes' WHERE ID_orders_payments='$in{'id_orders_payments'}'");
		
		&add_order_notes_by_type($id_orders,"Order Processed","Low");
		
		#Se actualizará el posteddate en caso de que el pago sea procedente de un return de tipo Refund
		if(&load_name('sl_orders_payments','ID_orders_payments',$in{'id_orders_payments'},'Reason')eq"Refund")
		{
			#Entonces se hará la actualización de posteddate
			&Do_SQL("Update sl_orders_payments set PostedDate=Curdate() where ID_orders=$in{'id_orders'} and isnull(PostedDate)");
			&Do_SQL("Update sl_orders_products set PostedDate=Curdate() where (isnull(PostedDate) and (Quantity=-1 or ID_products like '6%$cfg{'returnfeeid'}' or ID_products like '6%$cfg{'restockfeeid'}' or ID_products like '6%$cfg{'extwarrid'}') and ID_orders=$in{'id_orders'})");
		}
		
	}else{
		print qq|
				<table border="0" cellspacing="0" cellpadding="2" width="350" bgcolor="#FFCFCE">
				<tr>
					<td align="center"><p>&nbsp;</p><b>Check $decition</b><br>
					Reason : $message<br>
					Code : $msg_code</b><br>
					<p>&nbsp;</p></td>
				</tr>
				</table>
			|;
		if ($msg_code eq '97 0001' or $msg_code eq '97 0002'){
			
		}else{

			if ($rec_order->{'Status'} ne 'Shipped'){

				my ($sth) = &Do_SQL("UPDATE sl_orders SET Status='Pending' WHERE ID_orders='$id_orders'");
				&auth_logging('opr_orders_stPending',$id_orders);
				&status_logging($id_orders,'Pending');

			}
			
			my ($sth) = &Do_SQL("UPDATE sl_orders_payments SET Status='Denied' WHERE ID_orders_payments='$in{'id_orders_payments'}'");
			
			&add_order_notes_by_type($id_orders,"Check paylogs","Low");
		}
	}
	my ($sth) = &Do_SQL("INSERT INTO sl_orders_plogs SET ID_orders='$id_orders',ID_orders_payments='$in{'id_orders_payments'}',Data='".&filter_values($output)."',Date=Curdate(),Time=NOW(),ID_admin_users='$usr{'id_admin_users'}'");
	return;
}

sub trans {
# --------------------------------------------------------
	my ($line) = @_[0];
	$line =~ tr/+//;
	#$line =~ s/\n|\r//g;
	$line =~ s/\+//g;
	return $line;
}

sub load_chkerror_msg {
# ----------------------------------------------------------------------------
	my ($vvalue,$subcode) = @_;
	
	my ($sth) = &Do_SQL("SELECT Definition_En FROM sl_vars WHERE VName='Certegy' AND VValue='$vvalue' and Subcode='$subcode'");
	return $sth->fetchrow;

}

##########################################################
##		COMMON SUBS			##
##########################################################
sub parse_form {
# --------------------------------------------------------
	my (@pairs, %in);
	my ($buffer, $pair, $name, $value);

	if ($ENV{'REQUEST_METHOD'} eq 'GET') {
		@pairs = split(/&/, $ENV{'QUERY_STRING'});
	}elsif ($ENV{'REQUEST_METHOD'} eq 'POST') {
		read(STDIN, $buffer, $ENV{'CONTENT_LENGTH'});
 		@pairs = split(/&/, $buffer);
	}else {
		&cgierr ("This script must be called from the Web\nusing either GET or POST requests\n\n");
	}
	PAIR: foreach $pair (@pairs) {
		($name, $value) = split(/=/, $pair);

		$name =~ tr/+/ /;
		$name =~ s/%([a-fA-F0-9][a-fA-F0-9])/pack("C", hex($1))/eg;
		$name = lc($name);

		$value =~ tr/+/ /;
		$value =~ s/%([a-fA-F0-9][a-fA-F0-9])/pack("C", hex($1))/eg;

		$value =~ s/^\s+//g;
		$value =~ s/\s+$//g;

		#$value =~ s/\r//g;
		$value =~ s/<!--(.|\n)*-->//g;			# Remove SSI.
		if ($value eq "---") { next PAIR; }		# This is used as a default choice for select lists and is ignored.
		(exists $in{$name}) ?
			($in{$name} .= "|$value") :		# If we have multiple select, then we tack on
			($in{$name}  = $value);			# using the ~~ as a seperator.
	}
	return %in;
}