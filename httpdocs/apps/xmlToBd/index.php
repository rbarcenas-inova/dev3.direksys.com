<?php
require_once 'autoload.php';
XmlToBD::init();
// show($cfg);
// header('Content-Type: application/json');
// !isset($in['action']) and $in['action']='';
// switch ($in['action']) {
// 	case 'all':
// 		$all = MysqlBD::consultarTablaF('cu_invoices',array(),array('Status'=>'Confirmed'))->getDatos();
// 		$response = array();
// 		foreach ($all as $key => $value) {
// 			$xml = new FacturasCFDI\Factura();
// 			$value = clearArray($value);
// 			$response[] = $xml->setDatos(new Tabla($value))->setAddenda(detectarAddenda($value['customer_fcode']))->createXMLFile();
// 		}
// 		break;
// 	case 'list':
// 		if(!isset($in['facturas'])){
// 			echo json_encode(array('code'=>500,'msg'=>'Error'));
// 			exit;
// 		}
// 		$id_invoices = explode(',',$in['facturas']);
// 		$response = array();
// 		foreach ($id_invoices as $key => $value) {
// 			$invoice = MysqlBD::consultarTablaF('cu_invoices',array(),array('ID_invoices'=>$value,'Status'=>'Confirmed'))->getDatos();
// 			$invoice = clearArray($invoice[0]);
// 			$xml = new FacturasCFDI\Factura();
// 			$response[] = $xml->setDatos(new Tabla($invoice))->setAddenda(detectarAddenda($invoice['customer_fcode']))->createXMLFile();
// 			echo json_encode(array('code'=>200, 'response'=>$response));
// 		}
// 		break;
// 	default:
// 		echo json_encode(array('code'=>500,'msg'=>'Error'));
// 		break;
// }
