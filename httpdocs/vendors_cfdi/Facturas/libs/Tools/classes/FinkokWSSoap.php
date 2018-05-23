<?php
class FinkokWSSoap{
	public static $requests;
	public static $responses;
	public static $ws = WS_SING;
	public static function Timbrar($xmlString,$rfc,$invoice=0){
		$folder = '';
		$config = $GLOBALS['cfg']['path_invoices_tocert'];
		if(CREATE_EMISOR == 1)
			self::addCustomer($rfc);
		$url = self::$ws."/stamp.wsdl";
		$username = Config::$user_finkok;
		$password = Config::$pass_finkok;
		$client = new SoapClient($url);
		$params = array(
			'xml' => $xmlString,
			'username' => $username,
			'password' => $password
		);
		$funcion = 'stamp';
		self::$requests[] = array('url'=>$url,'params'=>$params,'function'=>$funcion);
		$response = $client->__soapCall($funcion, array($params));
		self::$responses[] = array('response'=>$response);
		$errores = '';
		if(!isset($response->stampResult->UUID)){
			if(is_array($response->stampResult->Incidencias)){
				$inc = $response->stampResult->Incidencias;
				foreach ($inc as $key => $value) {
					logg($value->CodigoError.' => '.$value->MensajeIncidencia);		
					$errores.=' '.$value->CodigoError.' => '.$value->MensajeIncidencia."\n";
				}
			}else{
				$inc = $response->stampResult->Incidencias->Incidencia;
				logg($inc->CodigoError.' => '.$inc->MensajeIncidencia);
				$errores.=' '.$inc->CodigoError.' => '.$inc->MensajeIncidencia."\n";
			}
			MysqlBD::executeQuery("update cu_invoices set `Status`='Failed' where id_invoices='$invoice'");
			MysqlBD::executeQuery("insert into cu_invoices_notes(ID_invoices,Notes,Type,Date,Time,ID_admin_users) values ('$invoice','$errores','Error',curdate(),curtime(),1)");
			return $response;
		}
		
		if(strlen($response->stampResult->xml) > 0){
			MysqlBD::executeQuery("update cu_invoices set `Status`='Certified' where id_invoices='$invoice'");
			$save = array(
				'ID_invoices'=>$invoice,
				'uuid'=>$response->stampResult->UUID,
				'xml'=>$response->stampResult->xml,
				'Status'=>'Certified'
			);
			XmlToBD::saveRow($save);
			MysqlBD::executeQuery("insert into cu_invoices_notes(ID_invoices,Notes,Type,Date,Time,ID_admin_users) values ('$invoice','Timbrado Exitoso','Note',curdate(),curtime(),1)");
			return $response->stampResult->xml;
		}
		return FALSE;
	}

	public static function cancelInvoice($uuid = array(),$rfc = '',$invoice = 0, $nota){
		if(count($uuid) == 0 || $rfc == '')
			return FALSE;
		$url = self::$ws."/cancel.wsdl";
		$username = Config::$user_finkok;
		$password = Config::$pass_finkok;
		$client = new SoapClient($url);
		$cer_path = '';
		if(file_exists(CERT_FOLDER.DIRECTORY_SEPARATOR.strtolower($rfc).'.cer.pem')){
			$cer_path = CERT_FOLDER.DIRECTORY_SEPARATOR.strtolower($rfc).'.cer.pem';
		}elseif (file_exists(CERT_FOLDER.DIRECTORY_SEPARATOR.strtoupper($rfc).'.cer.pem')) {
			$cer_path = CERT_FOLDER.DIRECTORY_SEPARATOR.strtoupper($rfc).'.cer.pem';
		}else{
			return FALSE;
		}
		// $cer_path = "goya780416gm0.cer.pem";
		$cer_file = fopen($cer_path, "r");
		$cer_content = fread($cer_file, filesize($cer_path));
		fclose($cer_file);
		$key_path = '';
		if(file_exists(CERT_FOLDER.DIRECTORY_SEPARATOR.strtolower($rfc).'.key.pem')){
			$key_path = CERT_FOLDER.DIRECTORY_SEPARATOR.strtolower($rfc).'.key.pem';
		}elseif (file_exists(CERT_FOLDER.DIRECTORY_SEPARATOR.strtoupper($rfc).'.key.pem')) {
			$key_path = CERT_FOLDER.DIRECTORY_SEPARATOR.strtoupper($rfc).'.key.pem';
		}else{
			return false;
		}
		// $key_path = "goya780416gm0.key.pem";
		$key_file = fopen($key_path, "r");
		$key_content = fread($key_file,filesize($key_path));
		fclose($key_file);
		$params = array(
			'UUIDS' => array('uuids'=>$uuid),
			'username'=>$username,
			'password'=>$password,
			'taxpayer_id'=>$rfc,
			'cer'=>$cer_content,
			'key'=>$key_content
		);
		$response = $client->__soapCall("cancel", array($params));
		return $response;
	}

	private static function addCustomer($rfc){
		$url = self::$ws."/registration.wsdl";
		$username = Config::$user_finkok;
		$password = Config::$pass_finkok;
		$client = new SoapClient($url);
		$params = array(
			'taxpayer_id' => $rfc,
			'reseller_username' => $username,
			'reseller_password' => $password
		);
		$funcion = 'get';
		self::$requests[] = array('url'=>$url,'params'=>$params,'function'=>$funcion);
		$response = $client->__soapCall($funcion, array($params));
		self::$responses[] = array('response'=>$response);
		if( count((array)$response->getResult->users) == 0){
			$funcion='add';
			self::$requests[] = array('url'=>$url,'params'=>$params,'function'=>$funcion);
			$response = $client->__soapCall($funcion, array($params));
			self::$responses[] = array('response'=>$response);
		}
		return true;
	}
}