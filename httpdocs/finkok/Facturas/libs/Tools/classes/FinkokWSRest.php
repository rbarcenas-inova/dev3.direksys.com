<?php
class FinkokWSRest{
	public static $requests;
	public static $responses;
	public static $ws = WS_SING;
	public static function Timbrar($xmlString,$rfc,$invoice=0, $time = ''){
		$folder = '';
		$config = $GLOBALS['cfg']['path_invoices_tocert'];
		// self::addCustomer($rfc);
		$url = self::$ws.'cfdi/factura/';//."/stamp.wsdl";
		$key = Config::$finkok_key;
		if(CREATE_EMISOR == 1)
			self::addEmisor();

		$xml_json = str_replace("\/",'/',json_encode(array('xml'=>$xmlString,'emisor'=> trim($rfc))));
		$configCurl = array(
			'method'=>'POST',
			'url'=>$url,
			'params'=> $xml_json,
			'header'=>array("Content-Type: application/json","Authorization: Token $key", "Request-ID: ".md5(trim($rfc).$invoice.$time.rand(10000, 99999))),
			'parseFrom' => 'json'
		);
		self::$requests[] = array('url'=>$url,'params'=>$xmlString,'function'=>'timbrar');
		$response = CurlClient::request($configCurl);
		self::$responses[] = array('response'=>$response);
		$errores = '';
		
		if(isset($response->uuid)){
			MysqlBD::executeQuery("update cu_invoices set `Status`='Certified', xml_uuid='$response->uuid' where id_invoices='$invoice'");
			$save = array(
				'ID_invoices'=>$invoice,
				'uuid'=>$response->uuid,
				'xml'=>$response->xml,
				'Status'=>'Certified'
			);
			XmlToBD::saveRow($save);
			MysqlBD::executeQuery("insert into cu_invoices_notes(ID_invoices,Notes,Type,Date,Time,ID_admin_users) values ('$invoice','Timbrado Exitoso','Note',curdate(),curtime(),1)");
			return 1;
		}elseif(isset($response->incidencias)){
			$errores = join("\n",$response->incidencias);
			MysqlBD::executeQuery("update cu_invoices set `Status`='OnEdition' where id_invoices='$invoice'");
			MysqlBD::executeQuery("insert into cu_invoices_notes(ID_invoices,Notes,Type,Date,Time,ID_admin_users) values ('$invoice','$errores','Error',curdate(),curtime(),1)");
			return 0;
		}else{
			MysqlBD::executeQuery("update cu_invoices set `Status`='New' where id_invoices='$invoice'");
			MysqlBD::executeQuery("insert into cu_invoices_notes(ID_invoices,Notes,Type,Date,Time,ID_admin_users) values ('$invoice','WS ERROR','Error',curdate(),curtime(),1)");
			return "ERROR DE WS => ". print_r($response, 1);
		}
		return 0;
	}
	public static function cancelUUID($uuid, $rfc){
		$url = self::$ws.'cfdi/cancelar/';//."/stamp.wsdl";
		$key = Config::$finkok_key;
		$request = array('uuid'=>$uuid, 'rfc'=>$rfc);
		$configCurl = array(
			'method'=>'POST',
			'url'=>$url,
			'params'=> json_encode($request),
			'header'=>array("Content-Type: application/json","Authorization: Token $key"),
			'parseFrom' => 'json'
		);
		$response = CurlClient::request($configCurl);
		logg(print_r($response,1), 'cancelUUID.log');
		return $response;
	}
	public static function cancelInvoice($uuid = array(),$rfc = '',$invoice = 0, $nota){
		if(count($uuid) == 0 || $rfc == '')
			return FALSE;
		if(CREATE_EMISOR == 1)
			self::addEmisor();
		$url = self::$ws.'cfdi/cancelar/';//."/stamp.wsdl";
		$key = Config::$finkok_key;
		$uuid = array_shift($uuid);
		$request = array('uuid'=>$uuid, 'rfc'=>$rfc);
		$configCurl = array(
			'method'=>'POST',
			'url'=>$url,
			'params'=> json_encode($request),
			'header'=>array("Content-Type: application/json","Authorization: Token $key"),
			'parseFrom' => 'json'
		);
		self::$requests[] = array('url'=>$url,'params'=>$request,'function'=>'cancelar');
		$response = CurlClient::request($configCurl);
		logg(print_r($request,1));
		logg(print_r($response,1));
		self::$responses[] = array('response'=>$response);
		$errores = '';
		if(isset($response->acuse_cancelacion_xml) ){

			MysqlBD::executeQuery("update cu_invoices set `Status`='Cancelled' where id_invoices='$invoice'");
			$admin_user = isset($GLOBALS['usr']) ? $GLOBALS['usr']['id_admin_users'] : 1;
			$save = array(
				'ID_invoices'=>$invoice,
			);
			XmlToBD::updateRow($save);
			MysqlBD::executeQuery("insert into cu_invoices_notes(ID_invoices,Notes,Type,Date,Time,ID_admin_users) values ('$invoice','Razon de Cancelacion: $nota ;".addslashes(htmlspecialchars("Factura con Folio Fiscal: $uuid se cancelo. -> Fecha y Hora: ".$response->fecha_cancelacion))."','Note',curdate(),curtime(),$admin_user)");
			return TRUE;
		}else{
			return $response;
		}
	}

	private static function addEmisor(){
		if(CREATE_EMISOR == 0)
			return TRUE;
		$method = 'PUT';
		$url = self::$ws."cfdi/emisor/".getRFC()."/";
		$key_file = file_get_contents(CERT_FOLDER.'/'.getRFC().'.key');
		$cer_file = file_get_contents(CERT_FOLDER.'/'.getRFC().'.cer');
		$passphrase = getKeyAndNumCert(getRFC())['pwd'];
		$key = Config::$finkok_key;
		$name = MysqlBD::getConexion()->query("select * from cu_company_legalinfo where PrimaryRecord='Yes'")->fetch(PDO::FETCH_OBJ);
		$address = MysqlBD::getConexion()->query("select * from cu_company_addresses where PrimaryRecord='Yes'")->fetch(PDO::FETCH_OBJ);
		$params = array(
			'rfc' =>getRFC(),
			'nombre' => limpiar($name->Name),
			'regimenes_fiscales'=>array(limpiar($name->Regime)),
			'domicilio_fiscal' => array(
		        "calle"=> limpiar($address->Street),
		        "no_exterior"=> $address->Num,
		        "colonia"=> limpiar($address->Urbanization),
		        "municipio"=>limpiar($address->City),
		        "codigo_postal"=> $address->Zip,
		        "estado"=> limpiar($address->State),
		        "pais"=> limpiar($address->Country)
			),
			'certificado'=>array(
				'password'=>$passphrase,
				'key'=>base64_encode($key_file),
				'cer'=>base64_encode($cer_file)
			)
		);
		// $funcion = 'get';
		$configCurl = array(
			'method'=>$method,
			'url'=>$url,
			'params'=>str_replace("\/",'/',json_encode($params)),
			'header'=>array("Content-Type: application/json","Authorization: Token $key"),
			'parseFrom' => 'json'
		);
		self::$requests[] = array('url'=>$url,'params'=>$params,'function'=>'Create Emisor');
		$response = CurlClient::request($configCurl);
		self::$responses[] = array('response'=>$response);
		$errores = '';
		// print_r($response);
		// if( count((array)$response->getResult->users) == 0){
		// 	$funcion='add';
		// 	self::$requests[] = array('url'=>$url,'params'=>$params,'function'=>$funcion);
		// 	$response = $client->__soapCall($funcion, array($params));
		// 	self::$responses[] = array('response'=>$response);
		// }
		return true;
	}
}