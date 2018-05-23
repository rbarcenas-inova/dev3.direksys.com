<?php
class XmlToBD{
	public static $empresa = '';
	public static function init($empresa){
		self::$empresa = $empresa;
		$con = MysqlBD::getConexion();
		$query = "select ID_invoices,doc_serial,uuid,doc_num,concat(doc_serial,'_',doc_num) invoice_file from cu_invoices where doc_serial !='' and status='Certified' and doc_num !=0 order by ID_invoices";
		$folder_base = 'C:\Facturas';
		$empresa = 'TLO1108314G2';
		$res = $con->query($query);
		// show($all);
		// exit;
		$aux = 0;
		logg('-------------------------------------------------------------');
		logg("Iniciando carga de xml a BD de $empresa ");
		$timer = new ExecutionTime();
		while( $row = $res->fetch(PDO::FETCH_OBJ) ){
			$foldersearch = $folder_base.DIRECTORY_SEPARATOR.$empresa.DIRECTORY_SEPARATOR.$row->doc_serial.DIRECTORY_SEPARATOR.self::getNumberDir($row->doc_num);
			$a = $foldersearch.DIRECTORY_SEPARATOR.$row->invoice_file.'.xml';
			$b = $foldersearch.DIRECTORY_SEPARATOR.$row->invoice_file.'_A.xml';
			$file = '';
			$flag = false;
			if(file_exists($a)){
				$file = $a;
				$flag = true;
			}
			elseif(file_exists($b)){
				$file = $b;
				$flag = true;
			}else{
				logg("File $row->invoice_file",'faltante.txt');
				continue;
			}
			if($flag){
				$aux++;
				$xml_content = clearBOM(file_get_contents($file));
				try{
					$xmlExtractor = new cfdiMX\Parser($xml_content);
				}catch(Exception $e){
					logg("Error de Lectura $row->invoice_file");
					$aux--;
					continue;
				}

				$xmlObject = (object)$xmlExtractor->jsonSerialize();
				self::saveRow(
					array(
						'ID_invoices'=>$row->ID_invoices,
						'uuid'=>strtoupper($xmlObject->Comprobante['Complemento']['TimbreFiscalDigital']['@atributos']['UUID']),
						'xml'=>$xml_content
					)
				);
			}
			echo '.';
		}
		logg('# Archivos Encontrados => '.$aux);
		logg("Tiempo de Ejecución : $timer");
		logg('-------------------------------------------------------------');

	}
	public static function showXML($id){
		MysqlBD::config('172.20.27.78','fcanaveral','XZGuCs05','direksys2_e4');
		$conn = MysqlBD::getConexion();
		$query = 'select xml from xml_info where ID_xml_info = ? limit 1';
		$sth = $conn->prepare($query);
		$sth->execute(
			array(
					$id
				)
			);
		$res = $sth->fetch();
		show(gzuncompress($res['xml']),'xml');
	}
	public static function saveRow($data){
		$prefix = 'e'.EMPRESA;
		$conn = MysqlBD::getConexion($prefix);
		$query = 'insert into '.$prefix.'_xml_info(ID_invoices,uuid,xml,Status) values(?,?,?,?)';
		$sth = $conn->prepare($query);
		$status = isset($data['Status']) ? $data['Status'] : 'Certified';
		$sth->execute(
			array(
					$data['ID_invoices'],
					$data['uuid'],
					gzcompress($data['xml']),
					$status
				)
			);
		logg('Guardando Registro en xml_info datos: ID_invoices => '.$data['ID_invoices'] );
		// $conn->query("insert into xml_info(ID_invoices,uuid,xml) values('".$data['ID_invoices']."','".$data['uuid']."',compress('".$data['xml']."') )");
	}
	public static function updateRow($data){
		$prefix = 'e'.EMPRESA;
		$conn = MysqlBD::getConexion($prefix);
		$query = 'update '.$prefix.'_xml_info set Status=\'Cancelled\' where id_invoices=? ';
		$sth = $conn->prepare($query);
		$sth->execute(
			array(
					$data['ID_invoices'],
				)
			);
		logg('Actualizar Registro en xml_info datos: ID_invoices => '.$data['ID_invoices'] );
	}
	public function showXMLFromDB($id_invoices = 0){
		$prefix = 'e'.EMPRESA;
		$from_table = $prefix."_xml_info_vendor";
		$conn = MysqlBD::getConexion($prefix);
		$query = 'select xml from '.$from_table.' where ID_xml_info_vendor = ? ;';
		$sth = $conn->prepare($query);
		$sth->execute(array($id_invoices));
		$res = $sth->fetch();
		return gzuncompress($res['xml']);
	}
	public static function getNumberDir($dir){
		if(intval($dir) < 1000)
			return '1';
		if(intval($dir) > 1000){
			return intval(intval($dir)/1000) * 1000;
		}
	}

}