#!/usr/bin/perl
#######################################################################
#######################################################################
#######################################################################
# Para revisar codigos de error y su significado, consultar
# https://cms.paypal.com/us/cgi-bin/?cmd=_render-content&content_ID=developer/e_howto_api_nvp_errorcodes

# Para consultar todas las operaciones relacionadas con el API de PayPal
# https://cms.paypal.com/us/cgi-bin/?&cmd=_render-content&content_ID=developer/e_howto_api_nvp_r_DoCapture

use FileHandle; 
 
use LWP::UserAgent ;
use HTTP::Request;
use HTTP::Response;
use HTTP::Headers;
use URI::Escape; 
use Data::Dumper;
 
use LWP::Debug qw( + ); 


sub paypal_search{
# --------------------------------------------------------
# Forms Involved: 
# Created on: 08/04/2010
# Author: Roberto Barcenas.
# Description : Realiza una busqueda de transaccion en PayPal   
# Parameters : 
  # Required (METHOD): Must be TransactionSearch.
  # Required (STARTDATE): The earliest transaction date at which to start the search. YYYY-MM-DDTHH:MM:SSZ

  # Optionals(ENDDATE,EMAIL ,RECEIVER ,RECEIPTID ,INVNUM ,TRANSACTIONID ,ACCT ,AUCTIONITEMNUMBER ,TRANSACTIONCLASS ,AMT+CURRENCYCODE ,STATUS )
  # Optionals(SALUTATION, FIRSTNAME , MIDDLENAME ,LASTNAME ,SUFFIX)

# https://cms.paypal.com/us/cgi-bin/?&cmd=_render-content&content_ID=developer/e_howto_api_nvp_r_TransactionSearch

	my ($id_orders,$id_orders_payments) = @_;

	my $nvp_string ='';
	my $methodName = 'TransactionSearch';
	
	my ($authRequestID) = &getauthRequestID_PayPal($id_orders_payments);
	my ($amount) = &load_name('sl_orders_payments','ID_orders_payments',$id_orders_payments,'Amount');

	if($authRequestID ne 'error'){

		$nvp_string .= "&TRANSACTIONID=". $authRequestID;
		$nvp_string .= "&STARTDATE=2010-07-20T00:00:00Z"; # Cambiar Fecha por una dinamica recibida via variable

		my ($status,%reply) = api_call($methodName,$nvp_string);


		if($status eq 'ok'){

		}
	}


}


sub paypal_reauth
{
# --------------------------------------------------------
# Forms Involved: 
# Created on: 08/04/2010
# Author: Roberto Barcenas.
# Description : Realiza una Re-Autorizacion de un pago previamente Autorizado   
# Parameters : 
  # Required (METHOD): Must be DoReauthorization.
  # Required (AUTHORIZATIONID): The value of a previously authorized transaction identification number returned by PayPal.
  # Required (AMT): Amount to reauthorize. Value is a positive number which cannot exceed $10,000 USD in any currency. No currency symbol. Must have two decimal places, decimal separator must be a period (.), and the optional thousands separator must be a comma (,).

  # Optionals(CURRENCYCODE)

# https://cms.paypal.com/us/cgi-bin/?cmd=_render-content&content_ID=developer/e_howto_api_nvp_r_DoReauthorization

	my ($id_orders,$id_orders_payments) = @_;

	my $nvp_string ='';
	my $methodName = 'DoReauthorization';
	
	my ($authRequestID) = &getauthRequestID_PayPal($id_orders_payments);
	my ($amount) = &load_name('sl_orders_payments','ID_orders_payments',$id_orders_payments,'Amount');

	if($authRequestID ne 'error'){

		$nvp_string .= "&AUTHORIZATIONID=". $authRequestID;
		$nvp_string .= "&AMT=". $amount;

		my ($status,%reply) = api_call($methodName,$nvp_string);
		my ($sth) = &Do_SQL("INSERT INTO sl_orders_plogs SET ID_orders='$id_orders',ID_orders_payments='$id_orders_payments',Data='".&load_paylogs_ccdata("METHOD=$methodName".$nvp_string, \%reply)."',Date=Curdate(),Time=CURTIME(),ID_admin_users='$usr{'id_admin_users'}'");

		if($status eq 'ok'){
			
				if ($reply{'ACK'} =~ /SUCCESS/i) {
						## AUTH APROVED
						my ($sth) = &Do_SQL("UPDATE sl_orders SET Status='Processed',StatusPay='None' WHERE ID_orders='$id_orders'");
						#my ($sth) = &Do_SQL("INSERT INTO sl_orders_notes SET ID_orders='$id_orders',Notes='Order Processed by PayPal ReAuthorization',Type='Low',Date=Curdate(),Time=CURTIME(),ID_admin_users='$usr{'id_admin_users'}'");
						&add_order_notes_by_type($id_orders,"Order Processed by PayPal ReAuthorization","Low");
						&auth_logging('opr_orders_to_proc',$id_orders);

						return ('OK',"Re-Auth Approved",0);		
						&auth_logging('opr_orders_to_proc',$id_orders);
				}else{
						## AUTH REJECTED
						&auth_logging('opr_orders_payments_reauth_rejected',$id_orders);
						return ('ERROR',"($reply{'L_LONGMESSAGE0'}) $reply{'L_ERRORCODE0'}",0);
				}
				
		}else {
			return ('ERROR',"General Error",0);
		}
	}
}


sub paypal_capture{
# --------------------------------------------------------
# Forms Involved: 
# Created on: 08/04/2010
# Author: Roberto Barcenas.
# Description : Realiza una Captura de un pago previamente Autorizado   
# Parameters : 
  # Required (METHOD): Must be DoCapture.
  # Required (AUTHORIZATIONID): The authorization identification number of the payment you want to capture. 
  # Required (AMT): Value is a positive number which cannot exceed $10,000 USD in any currency. No currency symbol. Must have two decimal places, decimal separator must be a period (.), and the optional thousands separator must be a comma (,).
  # Required (COMPLETETYPE): The value Complete indicates that this the last capture you intend to make. The value NotComplete indicates that you intend to make additional captures

  # Optionals(CURRENCYCODE, INVNUM , NOTE, SOFTDESCRIPTOR)

# https://cms.paypal.com/us/cgi-bin/?&cmd=_render-content&content_ID=developer/e_howto_api_nvp_r_DoCapture

	my ($id_orders,$id_orders_payments) = @_;

	my $nvp_string ='';
	my $methodName = 'DoCapture';
	my $completeType = 'Complete';
	
	my ($authRequestID) = &getauthRequestID_PayPal($id_orders_payments);
	my ($amount) = &load_name('sl_orders_payments','ID_orders_payments',$id_orders_payments,'Amount');

	if($authRequestID ne 'error'){

		$nvp_string .= "&AUTHORIZATIONID=". $authRequestID;
		$nvp_string .= "&AMT=". $amount;
		$nvp_string .= "&COMPLETETYPE=". $completeType;
		$nvp_string .= "&INVNUM=". $id_orders;

		my ($status,%reply) = api_call($methodName,$nvp_string);
		my ($sth) = &Do_SQL("INSERT INTO sl_orders_plogs SET ID_orders='$id_orders',ID_orders_payments='$id_orders_payments',Data='".&load_paylogs_ccdata("METHOD=$methodName".$nvp_string, \%reply)."',Date=Curdate(),Time=CURTIME(),ID_admin_users='$usr{'id_admin_users'}'");

		if($status eq 'ok'){

			if ($reply{'ACK'} =~ /SUCCESS/i) {
				## CAPTURE Approved 
				my ($sth) = &Do_SQL("UPDATE sl_orders_payments SET Captured='Yes',CapDate=IF(TIMESTAMPDIFF(SECOND,CONCAT(CURDATE(),' 21:00:00'),NOW()) >= 1,DATE_ADD(CURDATE(),INTERVAL 1 DAY),CURDATE()) WHERE ID_orders_payments='$id_orders_payments'");
				
				
				&add_order_notes_by_type($id_orders,"Order Captured via PayPal","Low");
				&auth_logging('opr_orders_captured',$id_orders);
				my ($sth) = &Do_SQL("UPDATE sl_orders SET Status='Processed',StatusPay='None' WHERE ID_orders='$id_orders'");
				my ($sth) = &Do_SQL("INSERT INTO sl_orders_notes SET ID_orders='$id_orders',Notes='Order Processed',Type='Low',Date=Curdate(),Time=CURTIME(),ID_admin_users='$usr{'id_admin_users'}'");
				&auth_logging('opr_orders_to_proc',$id_orders);
				#&cgierr(&load_paylogs_ccdata($nvp_string, \%reply));

				&auth_logging('opr_orders_captured',$id_orders);
				$status = &send_text_mail($cfg{'from_email'},$cfg{'to_email_accounting'},"PayPal Order Captured ($id_orders)",&load_paylogs_ccdata("METHOD=$methodName".$nvp_string, \%reply)) if $cfg{'to_email_accounting'};

				return ('OK',"Capture Approved",0);
			}else{
				&auth_logging('opr_orders_caperror',$id_orders);
				if($reply{'L_ERRORCODE0'} eq '10601'){
					
					&send_text_mail($cfg{'from_email'},$cfg{'from_email'},"PayPal authorization set as expired",&load_paylogs_ccdata("METHOD=$methodName".$nvp_string, \%reply));
					my ($sth) = &Do_SQL("UPDATE sl_orders_payments SET AuthCode='0000' WHERE ID_orders_payments='$id_orders_payments'");
					## CAPTURE REJECTED
					
					
					&add_order_notes_by_type($id_orders,"Authorization Expired. Set to Unauthorized","Low");
					
					return ($reply{'L_SHORTMESSAGE0'},"autoset to Unauthorized",$reply{'L_ERRORCODE0'});

				}else{
					## CAPTURE REJECTED
					my ($sth) = &Do_SQL("INSERT INTO sl_orders_notes SET ID_orders='$id_orders',Notes='Error During The Capture in PayPal',Type='Low',Date=Curdate(),Time=CURTIME(),ID_admin_users='$usr{'id_admin_users'}'");
					my ($sth) = &Do_SQL("UPDATE sl_orders SET StatusPay='Payment Declined' WHERE ID_orders='$id_orders'");
					my ($sth) = &Do_SQL("UPDATE sl_orders_payments SET Status='Denied' WHERE ID_orders_payments='$id_orders_payments'");

					return ($reply{'L_SHORTMESSAGE0'},"Capture Rejected : ($reply{'L_LONGMESSAGE0'}) $reply{'L_ERRORCODE0'}",$reply{'L_ERRORCODE0'});
				}
			}
		}else {
			return ('ERROR',"General Error",0);
		}
	}
}


sub api_call
{
# --------------------------------------------------------
# Forms Involved: 
# Created on: 08/04/2010
# Author: Roberto Barcenas.
# Description : Ejecuta los request al API de PayPal   
# Parameters : 
#	$API_Method: El metodo a ejecutar
#	$nvpStr: Cadena con los parametros a pasar al AP en formato &$key=$value

	my($API_Method,$nvpStr) = @_;

	my ($API_UserName,$API_Password,$API_Signature,$API_Endpoint,$PAYPAL_URL);
	my ($request,$response,$nvpreq);
	my $uname = `uname -n`;
	my $API_Version = $cfg{'paypal_version'};

	if($uname !~ /hawking|n3|washydoro/i and $cfg{'paypal_go_live'} == 1){

		$API_UserName=$cfg{'paypal_username'};
		$API_Password=$cfg{'paypal_password'};
		$API_Signature=$cfg{'paypal_signature'};

		$API_Endpoint = $cfg{'paypal_api'};
		$PAYPAL_URL = $cfg{'paypal_url'};

	}else{

		$API_UserName=$cfg{'paypal_sandbox_username'};
		$API_Password=$cfg{'paypal_sandbox_password'};
		$API_Signature=$cfg{'paypal_sandbox_signature'};

		$API_Endpoint = $cfg{'paypal_sandbox_api'};
		$PAYPAL_URL = $cfg{'paypal_sandbox_url'};

	}
  
	$nvpreq="METHOD=" . uri_escape($API_Method) . "&VERSION=" . uri_escape($API_Version) . "&PWD=" . uri_escape($API_Password) . "&USER=" . uri_escape($API_UserName) . "&SIGNATURE=" . uri_escape($API_Signature) . $nvpStr;
	
	#&cgierr($API_Endpoint . $nvpreq);
	my $ua = LWP::UserAgent->new;
	
	$request = HTTP::Request->new( POST => $API_Endpoint );
	$request->content_type( 'application/x-www-form-urlencoded' );
	$request->content( $nvpreq );
	$response = $ua->request( $request );
	
	my $response_str = uri_unescape($response->content);
	my (@lines,$error,$prt,%reply);
	@lines = split(/&/,$response_str);
	for (0..$#lines){
		if($lines[$_] =~ /^(.*)=(.*)$/ ){
		        $reply{$1} = $2; 
		}
	}

	if($response->is_success) {
		return ("ok",%reply)
	}
	else{
		return (uri_unescape($response->status_line),%reply);
	}
}


sub getauthRequestID_PayPal
{
# --------------------------------------------------------
# Forms Involved: 
# Created on: 08/04/2010
# Author: Roberto Barcenas.
# Description : Busca el TransactionID de un pago PayPal y lo devuelve   
# Parameters : 
#	$id_payments: El id del pago.


	my ($id_payments) = @_;
	my $authcode = "error";

	$authcode = &load_name('sl_orders_payments','ID_orders_payments',$id_payments,'AuthCode');

	if(!$authcode or $authcode eq '' or $authcode eq '0000'){
		$authcode = "error";
		my ($sth) = &Do_SQL("SELECT COUNT(*) FROM sl_orders_plogs WHERE ID_orders_payments = '$id_payments' AND Data REGEXP 'PAYMENTSTATUS = Pending' AND Data REGEXP 'ACK = Success'; ");
		$total = $sth->fetchrow();
		if ($total > 0){
			my ($sth) = &Do_SQL("SELECT Data FROM sl_orders_plogs WHERE ID_orders_payments='$id_payments' AND Data REGEXP 'PAYMENTSTATUS = Pending' AND Data REGEXP 'ACK = Success' ORDER BY ID_orders_plogs DESC LIMIT 1;");
			my (@ary) = split (/\n/, $sth->fetchrow);
			for (0..$#ary){
				if ($ary[$_] =~ /^TRANSACTIONID = (\w*)/i){
					$authcode = $1;
				}
			}
		}
	}
	return $authcode;
}



sub load_paylogs_ccdata
{
# --------------------------------------------------------
# Forms Involved: 
# Created on: 08/04/2010
# Author: Roberto Barcenas.
# Description : Devuelve una sola cadena con el paylog a ingresar. Contiene los datos enviados y la respuesta de PayPal recibida   
# Parameters :
    # $pRequest: Cadena con los datos enviados a PayPal
    # $pReply: hash con la respuesta de PayPal
 
	my ($pRequest, $pReply) = @_;

	my ($output) = "Submited Info\n";
	$pRequest =~ s/&/\n/g;
	$output .= $pRequest;

	$output .= "\n\nReply Info\n";
	foreach $key (keys %{$pReply}){
		$output .= "$key = $pReply->{$key}\n";
	}
	return &filter_values($output);
}

1;
