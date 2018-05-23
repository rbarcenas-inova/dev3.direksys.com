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
		
		$conect_to = 'e'.EMPRESA;
		$conn = MysqlBD::getConexion($conect_to);
		$table = 'e'.EMPRESA.'_xml_info_vendor';
		// Se modifica el Status del registro
		$conn->query("UPDATE $table SET `Status` = 'Cancelled' WHERE ID_xml_info_vendor = ".$in['id_invoices']);
		// Se agrega la nota de la cancelación
		$conn->query("INSERT INTO ".$table."_notes SET ID_xml_info_vendor = ".$in['id_invoices'].", Notes='".utf8_decode($in['nota'])."', `Type`='High', Date=CURDATE(), Time=CURTIME(), ID_admin_users=".$usr['id_admin_users'].";");
		
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

			$api_url = $cfg['api_getinvoice_url'].'?';
			$api_token = $cfg['api_getinvoice_token'];
			$params = 'e='.EMPRESA.'&format=xml&invoices='.$in['id_invoices'].'&download=0&vendor=1';

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
			echo json_encode(array('code'=>200, 'response'=>$response));
		}
		break;
	case 'showPDF':
		if(isset($in['id_invoices']) && $in['id_invoices']!= ''){

			$api_url = $cfg['api_getinvoice_url'].'?';
			$api_token = $cfg['api_getinvoice_token'];
			$params = 'e='.EMPRESA.'&format=pdf&invoices='.$in['id_invoices'].'&download=0&vendor=1';

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

		}else{
			echo json_encode(array('code'=>200, 'response'=>$response));
		}
		break;
	case 'downloadXML':
		$id_invoices = explode(',',$in['id_invoices']);
		if(count($id_invoices)>1){
			$api_url = $cfg['api_getinvoice_url'].'?';
			$api_token = $cfg['api_getinvoice_token'];
			$params = 'e='.EMPRESA.'&format=xml&invoices='.$in['id_invoices'].'&download=0&vendor=1';

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

			exit;
		}else{

			$api_url = $cfg['api_getinvoice_url'].'?';
			$api_token = $cfg['api_getinvoice_token'];
			$params = 'e='.EMPRESA.'&format=xml&invoices='.$in['id_invoices'].'&download=0&vendor=1';

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
						$filename = $in['id_invoices'].'.xml';
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

		}
		break;
	case 'downloadPDF':
		$id_invoices = explode(',',$in['id_invoices']);
		if(count($id_invoices)>1){			

			$api_url = $cfg['api_getinvoice_url'].'?';
			$api_token = $cfg['api_getinvoice_token'];
			$params = 'e='.EMPRESA.'&format=pdf&invoices='.$in['id_invoices'].'&download=0&vendor=1';

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
				
			exit;
		}else{

			$api_url = $cfg['api_getinvoice_url'].'?';
			$api_token = $cfg['api_getinvoice_token'];
			$params = 'e='.EMPRESA.'&format=pdf&invoices='.$in['id_invoices'].'&download=0&vendor=1';

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
