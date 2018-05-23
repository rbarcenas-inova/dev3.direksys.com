<?php
$bold = "\033[1m";
$normal = "\033[m";
function displayMenu(){
	global $bold, $normal,$in;
	if(!isset($in['status'])){
		$in['status'] = 'Confirmed';
	}
	$all = MysqlBD::consultarTablaF('cu_invoices',array(),array('Status'=>$in['status']))->getDatos();
	if(count($all) == 0){
		echo "$bold No hay Facturas pendientes de Timbrar $normal".PHP_EOL;
		exit();
	}
	echo "$bold ¿Esta seguro que quiere Timbrar las siguientes Facturas? $normal ".PHP_EOL;
	foreach ($all as $key => $value) {
		$datos = new Tabla($value);
		echo $datos->doc_serial.'-'.$datos->doc_num.PHP_EOL;
	}
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
			$all = MysqlBD::consultarTablaF('cu_invoices',array(),array('Status'=>$in['status']))->getDatos();
			MysqlBD::executeQuery("update cu_invoices set `Status`='InProcess' where Status='$in[status]'");
			foreach ($all as $key => $value) {
				MysqlBD::getConexion()->beginTransaction();
				$xml = new FacturasCFDI\Factura();
				$response[$value['ID_invoices']] = $xml->setDatos(new Tabla($value))->setAddenda(detectarAddenda($value['customer_fcode']))->Timbrar($value['ID_invoices']);
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
		$id_facturas = explode(',',$in['facturas']);
		$response = array();
		echo $bold.'Se enviaran a timbrar ' .count($id_facturas). ' Facturas'.$bold.PHP_EOL.PHP_EOL;
		foreach ($id_facturas as $key => $value) {
			$factura = MysqlBD::consultarTablaF('cu_invoices',array(),array('ID_invoices'=>$value,'Status'=>'Confirmed'))->getDatos();
			if(count($factura) == 0){
				echo '$boldNo existe Factura con ID: '.$value.$bold.PHP_EOL;
				continue;
			}
			$factura = clearArray($factura[0]);
			$xml = new FacturasCFDI\Factura();
			$response[] = $xml->setDatos(new Tabla($factura))->setAddenda(detectarAddenda($factura['customer_fcode']))->createXMLFile();
			echo json_encode(array('code'=>200, 'response'=>$response));
			echo PHP_EOL.PHP_EOL.$bold.'Timbrando Factura con ID: '. $value.$bold.PHP_EOL;
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
			        $conex->beginTransaction();
			        $row = $conex->query("Select xml_uuid from cu_invoices where id_invoices='$buffer' limit 1")->fetch(PDO::FETCH_OBJ);
			        $rfc = getRFC();
			        echo 'Cancelando Invoice => '.$buffer. " uuid==> ".$row->xml_uuid. " rfc==> ".$rfc;
			        FinkokWS::cancelInvoice($uuid = array($row->xml_uuid),$rfc = $rfc,$buffer, 'Error en Descuento');
			        $conex->commit();
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
	default:
		# code...
		break;
}