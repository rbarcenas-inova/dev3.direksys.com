<?php
class FinkokWS{
	public static $requests;
	public static $responses;
	public static $ws = WS_SING;
	public static function Timbrar($xmlString,$rfc,$invoice=0){
		if($GLOBALS['cfg']['finkok_method_rest']==1){
			return FinkokWSRest::Timbrar($xmlString,$rfc,$invoice);
		}else{
			return FinkokWSSoap::Timbrar($xmlString,$rfc,$invoice);
		}
	}
	public static function cancelInvoice($uuid = array(),$rfc = '',$invoice = 0,$nota = ''){
		if($GLOBALS['cfg']['finkok_method_rest']==1){
			return FinkokWSRest::cancelInvoice($uuid,$rfc,$invoice, $nota);
		}else{
			return FinkokWSSoap::cancelInvoice($uuid,$rfc,$invoice, $nota);
		}
	}
	
	private static function addCustomer($rfc){
		if($GLOBALS['cfg']['finkok_method_rest']==1){
			return FinkokWSRest::addCustomer($rfc);
		}else{
			return FinkokWSSoap::addCustomer($rfc);
		}
	}
}