<?php
require_once 'autoload.php';
!isset($in['action']) and $in['action']='';
switch ($in['action']) {
	case 'showNewXML':
		// header('Content-Type: application/json');
		$all = MysqlBD::consultarTablaF('cu_invoices',array(),array('Status'=>'Confirmed'))->getDatos();
		$xml = new FacturasCFDI\Factura();
		// MysqlBD::executeQuery("update cu_invoices_notes set `Status`='InProcess' where id_invoices='$value[ID_invoices]'");
		foreach ($all as $key => $value) {
			$xml = new FacturasCFDI\Factura();
			// MysqlBD::executeQuery("update cu_invoices_notes set `Status`='InProcess' where id_invoices='$value[ID_invoices]'");
			// $response[] = $xml->setDatos(new Tabla($value))->setAddenda(detectarAddenda($value['customer_fcode']))->Timbrar($value['ID_invoices']);
			$response[] = $xml->setDatos(new Tabla($value))->setAddenda(detectarAddenda($value['customer_fcode']))->Timbrar($value['ID_invoices']);
			echo $response[0];
		}
		// echo json_encode(array('code'=>200));
		break;
	case 'cron':
		system('php index_console.php --e='.EMPRESA.' --type=all --confirm=yes --status=New >> /dev/null 2>&1 &');
		echo 'php index_console.php --e='.EMPRESA.' --type=all --confirm=yes --status=New >> /dev/null 2>&1 &';
		// header('Content-Type: application/json');
		// echo json_encode(array('code'=>200));
		break;
	case 'cronPdf':
		if(isset($in['id_invoices']) && $in['id_invoices']!= ''){
			$xml = new XmlToBD();
			$res = $xml->showXMLFromDB($in['id_invoices']);
			if($res !== FALSE){
				header("Content-Type: text/plain");
				echo base64_encode(createPDF($in['id_invoices'], $res, 'string'));
			}
		}
		break;
	case 'all':
		system('php index_console.php --e='.EMPRESA.' --type=all --confirm=yes >> /dev/null 2>&1 &');
		header('Content-Type: application/json');
		echo json_encode(array('code'=>200));
		break;
	case 'cancelInvoice':
		header('Content-Type: application/json');
		if(!isset($in['id_invoices']) || $in['id_invoices'] == ''){
			echo json_encode(array('code'=>500,'msg'=>'Error, Id de factura no existe'));
			exit;
		}
		$invoice = MysqlBD::consultarTablaF('cu_invoices',array(),array('ID_invoices'=>$in['id_invoices'],'Status'=>'Certified'))->getDatos();
		$invoice = clearArray($invoice[0]);
		$conn = MysqlBD::getConexion("e".EMPRESA);
		$uuid = $conn->query("select uuid from e".EMPRESA."_xml_info where id_invoices = $in[id_invoices] order by ID_xml_info desc limit 1")->fetch(PDO::FETCH_OBJ)->uuid;
		$response = FinkokWS::cancelInvoice(array($uuid),getRFC(),$in['id_invoices'],$in['nota']);
		if( $GLOBALS['cfg']['finkok_method_rest']==1 ){
			header('Content-Type: application/json');
			if($response)
				echo json_encode( array('code'=>200, 'response' => $response ) );
			else
				echo json_encode( array('code'=>500, 'response' => $response ) );
		}else{
			if(isset($response->cancelResult->CodEstatus)){
				MysqlBD::executeQuery("insert into cu_invoices_notes(ID_invoices,Notes,Type,Date,Time,ID_admin_users) values ('".$in['id_invoices']."','".htmlentities($response->cancelResult->CodEstatus)."','Error',curdate(),curtime(),1)");
				header('Content-Type: application/json');
				echo json_encode( array('code'=>500, 'response' => $response ) );
			}else{
				MysqlBD::executeQuery("insert into cu_invoices_notes(ID_invoices,Notes,Type,Date,Time,ID_admin_users) values 
				(".$in['id_invoices'].",'Razon de Cancelacion: $in[nota] ".' --> '.htmlentities($response->cancelResult->Fecha).", Cancelado Exitoso','Note',curdate(),curtime(),1)");
				MysqlBD::executeQuery("update cu_invoices set `Status`='Cancelled' where id_invoices='".$in['id_invoices']."'");
				header('Content-Type: application/json');
				echo json_encode( array('code'=>200, 'response' => $response ) );
			}
		}
		break;
	case 'editInvoice':
		header('Content-Type: application/json');
		if(!isset($in['id_invoices']) || $in['id_invoices'] == ''){
			echo json_encode(array('code'=>500,'msg'=>'Error, Id de factura no existe'));
			exit;
		}
		
		MysqlBD::executeQuery("UPDATE cu_invoices SET 
									use_cfdi='".$in['usocfdi']."'
									, payment_type='".$in['metodopago']."'
									, payment_method='".$in['formapago']."' 
									, customer_fcode_bank = IF(invoice_type = 'pago', '".$in['rfc_banco']."', customer_fcode_bank) 
									, customer_bank = IF(invoice_type = 'pago', '".$in['banco']."', customer_bank) 
									, customer_account_number = IF(invoice_type = 'pago', '".$in['cuenta_banco']."', customer_account_number) 
								WHERE ID_invoices='".$in['id_invoices']."';");
		MysqlBD::executeQuery("INSERT INTO cu_invoices_notes(ID_invoices,Notes,Type,Date,Time,ID_admin_users) VALUES 
		(".$in['id_invoices'].",'Invoice edited','Note',curdate(),curtime(),".$usr['id_admin_users'].")");
		header('Content-Type: application/json');
		$response = "";
		echo json_encode( array('code'=>200, 'response' => $response ) );
		
		break;
	case 'changeStatus':
		header('Content-Type: application/json');
		if(!isset($in['id_invoices']) || $in['id_invoices'] == ''){
			echo json_encode(array('code'=>500,'msg'=>'Error, Id de factura no existe'));
			exit;
		}

		if( !empty($in['chg_status']) ){
			MysqlBD::executeQuery("UPDATE cu_invoices SET `Status`='".$in['chg_status']."', doc_date = IF(TIMESTAMPDIFF(HOUR, doc_date, NOW()) >= 70, NOW(), doc_date) WHERE ID_invoices='".$in['id_invoices']."'");
			MysqlBD::executeQuery("INSERT INTO cu_invoices_notes(ID_invoices,Notes,Type,Date,Time,ID_admin_users) 
									VALUES(".$in['id_invoices'].",'Change status to: ".$in['chg_status']."','Note',curdate(),curtime(),".$usr['id_admin_users'].")");
			$response = "";
		} else {
			$response = "Falta definir el Status";
		}

		header('Content-Type: application/json');
		echo json_encode( array('code'=>200, 'response' => $response ) );
		
		break;
	case 'list':
		header('Content-Type: application/json');
		if(!isset($in['facturas'])){
			echo json_encode(array('code'=>500,'msg'=>'Error'));
			exit;
		}
		$id_invoices = explode(',',$in['facturas']);
		$response = array();
		foreach ($id_invoices as $key => $value) {
			$invoice = MysqlBD::consultarTablaF('cu_invoices',array(),array('ID_invoices'=>$value,'Status'=>'Confirmed'))->getDatos();
			$invoice = clearArray($invoice[0]);
			$xml = new FacturasCFDI\Factura();
			$response[] = $xml->setDatos(new Tabla($invoice))->setAddenda(detectarAddenda($invoice['customer_fcode']))->createXMLFile();
			echo json_encode(array('code'=>200, 'response'=>$response));
		}
		break;
	case 'showXML':
		if(isset($in['id_invoices']) && $in['id_invoices']!= ''){
			if($cfg['fac_type'] != 'edx'){
				$api_url = $cfg['api_getinvoice_url'].'?';
				$api_token = $cfg['api_getinvoice_token'];
				$params = 'e='.EMPRESA.'&format=xml&invoices='.$in['id_invoices'].'&download=0';

				//setup the request, you can also use CURLOPT_URL
				$ch = curl_init($api_url.$params);
				// Returns the data/output as a string instead of raw data
				curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
				//Set your auth headers
				curl_setopt($ch, CURLOPT_HTTPHEADER, array(
				    'Content-Type: application/json',
				    'Authorization: Bearer ' . $api_token
				    ));
				// get stringified data/output. See CURLOPT_RETURNTRANSFER
				$data = curl_exec($ch);

				if (!curl_errno($ch)) {
					switch ($http_code = curl_getinfo($ch, CURLINFO_HTTP_CODE)) {
						case 200: 
							$filename = $in['id_invoices'].'.pdf';
							header("Pragma: public");
				            header("Expires: 0");
				            header("Cache-Control: must-revalidate, post-check=0, pre-check=0"); 
				            header("Content-Type: application/xml");
				            header("Content-Disposition: inline; filename=".$filename);
				            header("Content-Transfer-Encoding: binary");
				            echo $data;
						break;
						default:
							echo 'Unexpected HTTP code: ', $http_code, "\n";
					}
				}
				// close curl resource to free up system resources 
				curl_close($ch);

			}else{
				$conn = MysqlBD::getConexion();
				$nameFile = $conn->query("SELECT concat(doc_serial, '_', doc_num)invoice from cu_invoices where id_invoices = ".$in['id_invoices'].";")->fetch(PDO::FETCH_OBJ)->invoice. ".xml";
				$f = base64_encode($nameFile);
				header("Location: /cfdi/pages/cfdi/cfdi_doc.php?f=$f&id=$in[id_invoices]&m=2");
			}

		}else{
			echo json_encode(array('code'=>200, 'response'=>$response));
		}
		break;
	case 'showPDF':
		if(isset($in['id_invoices']) && $in['id_invoices']!= ''){
			
			if($cfg['fac_type'] != 'edx'){

				$api_url = $cfg['api_getinvoice_url'].'?';
				$api_token = $cfg['api_getinvoice_token'];
				$params = 'e='.EMPRESA.'&format=pdf&invoices='.$in['id_invoices'].'&download=0';
				if( isset($in['tt']) )	$params .= '&tt='.$in['tt'];

				//setup the request, you can also use CURLOPT_URL
				$ch = curl_init($api_url.$params);
				// Returns the data/output as a string instead of raw data
				curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
				//Set your auth headers
				curl_setopt($ch, CURLOPT_HTTPHEADER, array(
				    'Content-Type: application/json',
				    'Authorization: Bearer ' . $api_token
				    ));
				// get stringified data/output. See CURLOPT_RETURNTRANSFER
				$data = curl_exec($ch);

				if (!curl_errno($ch)) {
					switch ($http_code = curl_getinfo($ch, CURLINFO_HTTP_CODE)) {
						case 200: 
							$conn = MysqlBD::getConexion('Main');
							$folio = $conn->query("select CONCAT(doc_serial,'-',doc_num) AS folio from direksys2_e".EMPRESA.".cu_invoices where id_invoices = $in[id_invoices] limit 1")->fetch(PDO::FETCH_OBJ)->folio;
							$filename = $folio.'.pdf';
							header("Pragma: public");
				            header("Expires: 0");
				            header("Cache-Control: must-revalidate, post-check=0, pre-check=0"); 
				            header("Content-Type: application/pdf");            
				            header("Content-Disposition: inline; filename=".$filename);
				            header("Content-Transfer-Encoding: binary");
				            echo $data;
						break;
						default:
							echo 'Unexpected HTTP code: ', $http_code, "\n";
					}
				}
				// close curl resource to free up system resources 
				curl_close($ch);

			} else {

				$conn = MysqlBD::getConexion();
				$nameFile = $conn->query("SELECT concat(doc_serial, '_', doc_num)invoice from cu_invoices where id_invoices = ".$in['id_invoices'].";")->fetch(PDO::FETCH_OBJ)->invoice. ".pdf";
				$f = base64_encode($nameFile);
				header("Location: /cfdi/pages/cfdi/cfdi_doc.php?f=".$f."&id=".$in['id_invoices']."&m=2&readXml=1&e=".EMPRESA);

			}

		}else{
			echo json_encode(array('code'=>200, 'response'=>$response));
		}
		break;
	case 'downloadXML':
		$id_invoices = explode(',',$in['id_invoices']);
		if(count($id_invoices)>1){

			if($cfg['fac_type'] != 'edx'){
				$api_url = $cfg['api_getinvoice_url'].'?';
				$api_token = $cfg['api_getinvoice_token'];
				$params = 'e='.EMPRESA.'&format=xml&invoices='.$in['id_invoices'].'&download=0&vendor=0';

				//setup the request, you can also use CURLOPT_URL
				$ch = curl_init($api_url.$params);
				// Returns the data/output as a string instead of raw data
				curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
				//Set your auth headers
				curl_setopt($ch, CURLOPT_HTTPHEADER, array(
				    'Content-Type: application/json',
				    'Authorization: Bearer ' . $api_token
				    ));
				// get stringified data/output. See CURLOPT_RETURNTRANSFER
				$data = curl_exec($ch);

				if (!curl_errno($ch)) {
					switch ($http_code = curl_getinfo($ch, CURLINFO_HTTP_CODE)) {
						case 200:
							$filename = "download.zip";
							header("Content-type: application/zip"); 
							header("Content-Disposition: attachment; filename=$filename"); 
							header("Pragma: no-cache"); 
							header("Expires: 0"); 
							readfile("$filename");
							echo $data;
						break;
						default:
							echo 'Unexpected HTTP code: ', $http_code, "\n";
					}
				}
				// close curl resource to free up system resources 
				curl_close($ch);

			}else{
				$conn = MysqlBD::getConexion();
				$filesname = $conn->query("SELECT group_concat(concat(doc_serial, '_', doc_num) SEPARATOR '|')invoices data from cu_invoices where id_invoices in( $in[id_invoices] )")->fetch(PDO::FETCH_OBJ)->invoices;
				header("Location: /cfdi/pages/cfdi/cfdi_xmlzip.php?f=$filesname");
			}
			exit;
		}else{

			if($cfg['fac_type'] != 'edx'){
				$api_url = $cfg['api_getinvoice_url'].'?';
				$api_token = $cfg['api_getinvoice_token'];
				$params = 'e='.EMPRESA.'&format=xml&invoices='.$in['id_invoices'].'&download=0&vendor=0';

				//setup the request, you can also use CURLOPT_URL
				$ch = curl_init($api_url.$params);
				// Returns the data/output as a string instead of raw data
				curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
				//Set your auth headers
				curl_setopt($ch, CURLOPT_HTTPHEADER, array(
				    'Content-Type: application/json',
				    'Authorization: Bearer ' . $api_token
				    ));
				// get stringified data/output. See CURLOPT_RETURNTRANSFER
				$data = curl_exec($ch);

				if (!curl_errno($ch)) {
					switch ($http_code = curl_getinfo($ch, CURLINFO_HTTP_CODE)) {
						case 200:
							$conn = MysqlBD::getConexion('Main');
							$folio = $conn->query("select CONCAT(doc_serial,'-',doc_num) AS folio from direksys2_e".EMPRESA.".cu_invoices where id_invoices = $in[id_invoices] limit 1")->fetch(PDO::FETCH_OBJ)->folio;
							$filename = $folio.'.xml';
							header("Pragma: public");
				            header("Expires: 0");
				            header("Cache-Control: must-revalidate, post-check=0, pre-check=0"); 
				            header("Content-Type: application/xml");            
				            header("Content-Disposition: attachment; filename=".$filename);
				            header("Content-Transfer-Encoding: binary");
				            echo $data;
						break;
						default:
							echo 'Unexpected HTTP code: ', $http_code, "\n";
					}
				}

				// close curl resource to free up system resources 
				curl_close($ch);

			}else{
				$conn = MysqlBD::getConexion();
				$nameFile = $conn->query("SELECT concat(doc_serial, '_', doc_num)invoice from cu_invoices where id_invoices = $id_invoices[0]")->fetch(PDO::FETCH_OBJ)->invoice. ".xml";
				$f = base64_encode($nameFile);
				header("Location: /cfdi/pages/cfdi/cfdi_doc.php?f=$f&id=$id_invoices[0]&m=0");
			}

		}
		break;
	case 'downloadPDF':
		$id_invoices = explode(',',$in['id_invoices']);
		if(count($id_invoices)>1){

			if($cfg['fac_type'] != 'edx'){
				$api_url = $cfg['api_getinvoice_url'].'?';
				$api_token = $cfg['api_getinvoice_token'];
				$params = 'e='.EMPRESA.'&format=pdf&invoices='.$in['id_invoices'].'&download=0&vendor=0';

				//setup the request, you can also use CURLOPT_URL
				$ch = curl_init($api_url.$params);
				// Returns the data/output as a string instead of raw data
				curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
				//Set your auth headers
				curl_setopt($ch, CURLOPT_HTTPHEADER, array(
				    'Content-Type: application/json',
				    'Authorization: Bearer ' . $api_token
				    ));
				// get stringified data/output. See CURLOPT_RETURNTRANSFER
				$data = curl_exec($ch);

				if (!curl_errno($ch)) {
					switch ($http_code = curl_getinfo($ch, CURLINFO_HTTP_CODE)) {
						case 200:
							$filename = "download.pdf";
							header("Content-type: application/pdf"); 
							header("Content-Disposition: attachment; filename=$filename"); 
							header("Pragma: no-cache"); 
							header("Expires: 0"); 
							readfile("$filename");
							echo $data;
						break;
						default:
							echo 'Unexpected HTTP code: ', $http_code, "\n";
					}
				}
				// close curl resource to free up system resources 
				curl_close($ch);

			}else{

				$conn = MysqlBD::getConexion();
				$filesname = $conn->query("SELECT group_concat(concat(doc_serial, '_', doc_num) SEPARATOR '|')invoices data from cu_invoices where id_invoices in( $in[id_invoices] )")->fetch(PDO::FETCH_OBJ)->invoices;
				header("Location: /cfdi/pages/cfdi/cfdi_pdfprint.php?f=$filesname");
			}
			exit;
		}else{
			if($cfg['fac_type'] != 'edx'){
				$api_url = $cfg['api_getinvoice_url'].'?';
				$api_token = $cfg['api_getinvoice_token'];
				$params = 'e='.EMPRESA.'&format=pdf&invoices='.$in['id_invoices'].'&download=0&vendor=0';
				if( isset($in['tt']) )	$params .= '&tt='.$in['tt'];

				//setup the request, you can also use CURLOPT_URL
				$ch = curl_init($api_url.$params);
				// Returns the data/output as a string instead of raw data
				curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
				//Set your auth headers
				curl_setopt($ch, CURLOPT_HTTPHEADER, array(
				    'Content-Type: application/json',
				    'Authorization: Bearer ' . $api_token
				    ));
				// get stringified data/output. See CURLOPT_RETURNTRANSFER
				$data = curl_exec($ch);

				if (!curl_errno($ch)) {
					switch ($http_code = curl_getinfo($ch, CURLINFO_HTTP_CODE)) {
						case 200:
							$conn = MysqlBD::getConexion('Main');
							$folio = $conn->query("select CONCAT(doc_serial,'-',doc_num) AS folio from direksys2_e".EMPRESA.".cu_invoices where id_invoices = $in[id_invoices] limit 1")->fetch(PDO::FETCH_OBJ)->folio;
							$filename = $folio.'.pdf';
							header("Pragma: public");
				            header("Expires: 0");
				            header("Cache-Control: must-revalidate, post-check=0, pre-check=0"); 
				            header("Content-Type: application/pdf");            
				            header("Content-Disposition: attachment; filename=".$filename);
				            header("Content-Transfer-Encoding: binary");
				            echo $data;
						break;
						default:
							echo 'Unexpected HTTP code: ', $http_code, "\n";
					}
				}

				// close curl resource to free up system resources 
				curl_close($ch);
			}else{
				$conn = MysqlBD::getConexion();
				$nameFile = $conn->query("SELECT concat(doc_serial, '_', doc_num)invoice from cu_invoices where id_invoices = $id_invoices[0]")->fetch(PDO::FETCH_OBJ)->invoice. ".pdf";
				$f = base64_encode($nameFile);
				header("Location: /cfdi/pages/cfdi/cfdi_doc.php?f=$f&id=$id_invoices[0]&m=0&e=2");
			}
		}
		break;
	case 'downloadXMLCatalogoSat':
		header("Content-type: text/xml");
		header('Content-Disposition: attachment; filename="'.getRFC().'.xml"');
		$xml = new FacturasCFDI\CatalogoCuentas();
		echo $xml->createXML();
		break;
	case 'downloadXMLBalanzaSat':
		header("Content-type: text/xml");
		$filenamezip = getRFC().'201604BN.zip';
		$filenamexml = getRFC().'201604BN.xml';
		$zip = new ZipArchive();
		if(file_exists($filenamezip))
			unlink($filenamezip);
		if ($zip->open($filenamezip, ZipArchive::CREATE)!==TRUE) {
			exit;
		}
		$xml = new FacturasCFDI\Balanza();
		$zip->addFromString($filenamexml,$xml->createXML());
		$zip->close();
		header("Content-type: application/zip"); 
		header("Content-Disposition: attachment; filename=$filenamezip"); 
		header("Pragma: no-cache"); 
		header("Expires: 0"); 
		readfile("$filenamezip");
		break;
	default:
		echo json_encode(array('code'=>500,'msg'=>'Error'));
		break;
}
