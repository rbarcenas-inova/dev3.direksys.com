<?php
require_once 'autoload.php';
$class = new ReflectionClass('Config');
$arr = $class->getStaticProperties();
// echo '<pre>';
// print_r($arr);
// exit;

if(isset($in['id_invoices']) && $in['id_invoices']!= ''){
	$all = MysqlBD::consultarTablaF('cu_invoices',array(),array('id_invoices'=>$in['id_invoices']),0,0,0,1)->getDatos();
	// print_r($all);
	// exit;
	// echo '<pre style="white-space: pre-wrap; width:80%">';
	foreach ($all as $key => $value) {
		try{
			$xml = new FacturasCFDI\Factura(new Tabla($value), $in['v']);
			$xml->setAddenda(detectarAddenda($value['customer_fcode'], $value['ID_customers']));
		}catch(Exception $e){
			Invoice::addNote(intval($in['id_invoices']), "{$e->getMessage()}");
			continue;			
		}

		if(isset($in['sign']) && $in['sign'] == '1'){
			// echo '<pre style="white-space: pre-wrap; width:80%">';
			try{
				$result = $xml->timbrar($value['ID_customers']);
			}catch(Exception $e){
				Invoice::addNote(intval($in['id_invoices']), "{$e->getMessage()}");
				echo "<h3>{$e->getMessage()}</h3>";
				MysqlBD::executeQuery("update cu_invoices set  `Status` = 'OnEdition' where ID_invoices ='{$in['id_invoices']}'");
				continue;
			}
			if(is_string($result)){
				header("Content-type: text/xml");
				echo $result;
			}else
				print_r($result);
		}
		else{
			ob_clean();
			header("Content-type: text/xml");
			echo $xml->createXML();
			
		}
		
	}
	// print_r($xml);
}
exit;
