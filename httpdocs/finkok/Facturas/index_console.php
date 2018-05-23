<?php
$bold = "\033[1m";
$normal = "\033[m";
function displayMenu($id_invoices = ''){
	global $bold, $normal,$in;
	if(!isset($in['status'])){
		$in['status'] = 'Confirmed';
	}
	$all = array();
	if($id_invoces == '')
		$all = MysqlBD::consultarTablaF('cu_invoices',array(),array('Status'=>$in['status']))->getDatos();
	if(count($all) == 0){
		echo "$bold No hay Facturas pendientes de Timbrar $normal".PHP_EOL;
		exit();
	}
	echo "$bold ¿Esta seguro que quiere Timbrar las siguientes Facturas? $normal ".PHP_EOL;
	foreach ($all as $key => $value) {
		$datos = new Tabla($value);
		echo "\tID => ". $datos->ID_invoices. " ==> ". $datos->doc_serial.'-'.$datos->doc_num.PHP_EOL;
	}
	echo PHP_EOL;
}
require_once 'autoload.php';
extract($_GET);
echo PHP_EOL;
switch ($in['type']) {
	case 'all':
		$line = 'No';
		if(isset($in['confirm']) && strtolower($in['confirm']) == 'yes'){
			$line = 'Yes';
		}else{
			displayMenu();
			$line = readline('(Yes/No): ');
		}
		if(strtolower($line) == 'yes'){
			passthru('clear');
			echo 'Timbrando XML...'.PHP_EOL;
			logg('---------------  TIMBRANDO XML  ---------------');
			$response = array();
			$all = null;
			if(!isset($in['status'])){
				$in['status'] = 'Confirmed';
			}
			$all = MysqlBD::consultarTablaF('cu_invoices',array(),array('Status'=>$in['status']),0,0,0,100)->getDatos();
			// logg(print_r($all, 1));

			MysqlBD::executeQuery("update cu_invoices set `Status`='InProcess' where Status='$in[status]'");
			foreach ($all as $key => $value) {
				MysqlBD::getConexion()->beginTransaction();
				$conn = MysqlBD::getConexion();
				$queryVal = "SELECT IF( (n > 0 AND uuid_related != '') OR n = 0, 'SI', 'NO') timbrar
							FROM(
								SELECT 
									COUNT(*)n
									, cu_related_cfdi.uuid_related 
								FROM cu_related_cfdi
								WHERE ID_cfdi = {$value['ID_invoices']}
									OR (
										SELECT sl_orders.Date
										FROM cu_invoices_lines
											INNER JOIN sl_creditmemos_payments ON cu_invoices_lines.ID_creditmemos = sl_creditmemos_payments.ID_creditmemos
											INNER JOIN sl_orders ON sl_creditmemos_payments.ID_orders = sl_orders.ID_orders
										WHERE cu_invoices_lines.ID_invoices = {$value['ID_invoices']}
										GROUP BY cu_invoices_lines.ID_creditmemos
									) = '2010-12-31'
							)tmp;";
				$row = $conn->query($queryVal)->fetch(PDO::FETCH_OBJ)->timbrar;
				if($row == 'NO'){
					MysqlBD::getConexion()->rollback();				
					MysqlBD::executeQuery("update cu_invoices set  `Status` = 'New' where ID_invoices ='{$value['ID_invoices']}'");
					continue;
				}
				$xml = new FacturasCFDI\Factura();
				if($cfg['cfdi_version'] == '3.3'){
					$xml->setVersion('3.3');
				}elseif(isset($in['v'])){
					$xml->setVersion($in['v']);
				}
				logg(detectarAddenda($value['customer_fcode']));
				try{
					$response[$value['ID_invoices']] = $xml->setDatos(new Tabla($value))
						->setAddenda(detectarAddenda($value['customer_fcode'], $value['ID_customers']))
						->Timbrar($value['ID_invoices']);
				}catch(Exception $e){
					MysqlBD::getConexion()->rollback();				
					Invoice::addNote(intval($value['ID_invoices']), $e->getMessage());
					MysqlBD::executeQuery("update cu_invoices set  `Status` = 'OnEdition' where ID_invoices ='{$value['ID_invoices']}'");
					continue;
				}
				sleep(2);
				MysqlBD::getConexion()->commit();
			}
			$correo = 'ID INVOICES CON ERROR: <br>';
			foreach ($response as $key => $value) {
				if($value == 0){
					$correo.=PHP_EOL. $key . '<br>' . PHP_EOL;
				}
			}
			// send_gmail($cfg['to_error_invoices'], "Facturas con Errores", $correo);
			print_r($response);
			// logg(print_r($response,1));
			logg('--------------- FIN DE TIMBRADO ---------------');

			// echo 'Hecho...'.PHP_EOL;
			// echo 'Timbrando...'.PHP_EOL;
			// print_r($response);
			// echo PHP_EOL.PHP_EOL.$bold.'Timbrado Con exito'.$bold.PHP_EOL.PHP_EOL;
		}
		break;
	case 'list':
		$line = 'No';
		if(isset($in['confirm']) && strtolower($in['confirm']) == 'yes'){
			$line = 'Yes';
		}else{
			echo "$bold ¿Esta seguro que quiere Timbrar las siguientes Facturas? $normal ".PHP_EOL;
			echo "\t".$in['facturas'];
			echo PHP_EOL;
			$line = readline('(Yes/No): ');
		}
		if(strtolower($line) == 'no')
			exit;
		$id_facturas = explode(',',$in['facturas']);
		$response = array();
		echo "$bold".'Se enviaran a timbrar ' .count($id_facturas). ' Facturas'."$normal".PHP_EOL.PHP_EOL;
		if(!isset($in['status'])){
			$in['status'] = 'Confirmed';
		}
		foreach ($id_facturas as $key => $value) {
			$factura = MysqlBD::consultarTablaF('cu_invoices',array(),array('ID_invoices'=>$value,'Status'=>$in['status']))->getDatos();
			if(count($factura) == 0){
				echo "$bold".'No existe Factura con ID: '.$value."$normal".PHP_EOL;
				continue;
			}
			$conn = MysqlBD::getConexion();
			$queryVal = "SELECT IF( (n > 0 AND uuid_related != '') OR n = 0, 'SI', 'NO') timbrar
			FROM(
				SELECT 
					COUNT(*)n
					, cu_related_cfdi.uuid_related 
				FROM cu_related_cfdi
				WHERE 1
					AND ID_cfdi = {$value}
			)tmp;";
			$row = $conn->query($queryVal)->fetch(PDO::FETCH_OBJ)->timbrar;
			if($row == 'NO'){
				continue;					
			}
			$factura = clearArray($factura[0]);
			$xml = new FacturasCFDI\Factura();

			$response[] = $xml->setDatos(new Tabla($factura))
			->setAddenda(detectarAddenda($factura['customer_fcode'], $factura['ID_customers']))
			// ->createXML();
			->Timbrar($value);
			echo json_encode(array('code'=>200, 'response'=>$response));
			echo PHP_EOL.PHP_EOL."$bold".'Timbrando Factura con ID: '. $value."$normal".PHP_EOL;
		}
		echo PHP_EOL.PHP_EOL;
		break;
	case 'cancel':
		if(isset($in['filename'])){
			$handle = fopen($in['filename'], "r") or die("No existe el archivo $in[filename]");
			if ($handle) {
			    while (!feof($handle)) {
			        $buffer = trim(fgets($handle, 4096));
			        if($buffer == '')
			        	continue;
			        $conex = MysqlBD::getConexion();
			        // $conex->beginTransaction();
			        $row = $conex->query("Select xml_uuid from cu_invoices where id_invoices='$buffer' limit 1")->fetch(PDO::FETCH_OBJ);
			        $rfc = getRFC();
			        echo 'Cancelando Invoice => '.$buffer. " uuid==> ".$row->xml_uuid. " rfc==> ".$rfc;
			        FinkokWS::cancelInvoice($uuid = array($row->xml_uuid),$rfc = $rfc,$buffer, 'Error en Descuento');
			        sleep(1);
			        // $conex->commit();
					echo PHP_EOL;
			    }
			    fclose($handle);
			}
		}else{
			die("Debe definir un archivo con los id de facturas a cancelar.");
		}
		// $id_facturas = explode(',',$in['facturas']);
		// $response = array();
		// echo $bold.'Se enviaran a cancelar ' .count($id_facturas). ' Facturas'.$bold.PHP_EOL.PHP_EOL;
		// foreach ($id_facturas as $key => $value) {
		// 	echo 'Factura a Cancelar ==> '.$value;
		// }
		echo PHP_EOL.PHP_EOL;
		break;
	case 'cancelUUID' : 
		if(isset($in['filename'])){
			$handle = fopen($in['filename'], "r") or die("No existe el archivo $in[filename]");
			if ($handle) {
			    while (!feof($handle)) {
			        $buffer = trim(fgets($handle, 4096));
			        if($buffer == '')
			        	continue;
			        $conex = MysqlBD::getConexion();
			        // $conex->beginTransaction();
			        // $row = $conex->query("Select xml_uuid from cu_invoices where id_invoices='$buffer' limit 1")->fetch(PDO::FETCH_OBJ);
			        $rfc = getRFC();
			        echo 'Cancelando Invoice => '.$buffer. " uuid==> ".$buffer. " rfc==> ".$rfc;
			        var_dump(FinkokWS::cancelUUID($uuid = array($buffer),$rfc = $rfc));
			        sleep(1);
			        // $conex->commit();
					echo PHP_EOL;
			    }
			    fclose($handle);
			}
		}else{
			die("Debe definir un archivo con los uuid de facturas a cancelar.");
		}
		break;
	default:
		# code...
		break;
}