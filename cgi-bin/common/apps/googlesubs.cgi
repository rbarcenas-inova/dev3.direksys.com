#!/usr/bin/perl
#######################################################################
#######################################################################
#######################################################################


sub google_capture{
# --------------------------------------------------------
# Forms Involved: 
# Created on: 08/04/2010
# Author: Roberto Barcenas.
# Description : Realiza una Captura de un pago previamente Autorizado   
# Parameters : 
  # Required (id_orders)
  # Required (id_orders_payments)



	my ($id_orders,$id_orders_payments) = @_;

	my $nvp_string ='';	
	my ($amount) = &load_name('sl_orders_payments','ID_orders_payments',$id_orders_payments,'Amount');
	my ($id_google) = &load_name('sl_orders_google','ID_orders',$id_orders,'google_order');


	if($id_google > 0 and $amount > 0){

		my ($status,$message,$cybcod) = split(/\n/,&api_call("idd=$id_orders&idg=$id_google&idp=$id_orders_payments&api=google_capture&amt=$amount&idu=$usr{'id_admin_users'}&e=$in{'e'}"),3);

		## Movimientos Contables
		if($status = ~/ok/i) {

			&auth_logging('opr_orders_captured',$id_orders);
			my ($order_type, $ctype, $ptype,@params);
			my ($sth) = &Do_SQL("SELECT Ptype, Type FROM sl_orders INNER JOIN sl_customers USING(ID_customers) WHERE ID_orders = '$id_orders';");
			($order_type, $ctype) = $sth->fetchrow();
			$ptype = 'Google Checkout';
			@params = ($id_orders, id_orders_payments, 1);
			&accounting_keypoints('order_deposit_'. $ctype .'_'. $order_type .'_'. $ptype, \@params );

		}

		return ($status,$message,$code);

	}else {
		&auth_logging('opr_orders_captured_failed',$id_orders);
		&cgierr("No estan los datos completos\n\n idd=$id_orders&idg=$id_google&idp=$id_orders_payments&cmd=google_capture&idu=$usr{'id_admin_users'}&e=$in{'e'} ");
		return ('ERROR',"General Error",0);

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

use LWP::UserAgent ;
use HTTP::Request;
use HTTP::Response;
use HTTP::Headers;
 
use LWP::Debug qw( + ); 


	my($nvpStr) = @_;

	my $API_Endpoint = $cfg{'url_googlegateway'};
	my $uname = `uname -n`;

	#if($uname !~ /hawking|n3|washydoro/i and $cfg{'google_go_live'} == 1){
	if($uname =~ /s11/i and $cfg{'google_go_live'} == 1){

		$merchant_id = $cfg{'google_merchand_id'};
		$merchant_key = $cfg{'google_merchand_key'};

	}else{

		$merchant_id = $cfg{'google_sandbox_merchand_id'};
		$merchant_key = $cfg{'google_sandbox_merchand_key'};

	}
  
	my $url = $API_Endpoint . '?' .$nvpStr;
	my $ua = LWP::UserAgent->new;
	
	$request = HTTP::Request->new( GET => $url );
	$request->authorization_basic($merchant_id,$merchant_key);
	$response = $ua->request( $request );
	
	
	if ($response->is_success){
		return $response->content;
		#&cgierr($response->content);
		#&cgierr("Si pasa ".$response->content );
 	}else{
 		return $response->status_line;
		#&cgierr($response->status_line);
		#&cgierr("No pasa ".$response->status_line);
	}
}


1;
