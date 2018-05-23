<?php
class XmlToBD{
	static $empresa;
	public static function init($empresa){
		self::$empresa = $empresa;
		//  Conexion con server produccion
		// config($name='Main', $server=false, $user=false, $pass=false, $database=false,$motor='mysql')
		MysqlBD::config('Main', '172.20.27.78','fcanaveral','XZGuCs05','direksys2_e'.$empresa);
		$con = MysqlBD::getConexion();
		$query = "select ci.ID_invoices, concat(ci.doc_serial, '_', ci.doc_num) doc
		from direksys2_e11.cu_invoices ci
		left join direksys2_repo.e11_xml_info xi using(id_invoices)
		where 1
			and ci.`Status` = 'Certified'
			and xi.ID_invoices is null";
		$folder_base = 'C:\Facturas\\UUID';
		$empresa = 'MOW1109201Y3';
		$res = $con->query($query);

		$aux = 0;
		logg('-------------------------------------------------------------');
		logg("Iniciando carga de xml a BD de $empresa ");
		echo 'HOLA';
		exit();
		$timer = new ExecutionTime();
		while( $row = $res->fetch(PDO::FETCH_OBJ) ){
			print_r($row);
			exit;
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
		$prefix = 'e'.EMPRESA;
		$conn = MysqlBD::getConexion($prefix);
		$query = 'select xml from xml_info where ID_invoices = ? limit 1';
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
		$conn = MysqlBD::getConexion($prefix);
		$query = 'select xml from '.$prefix.'_xml_info where ID_invoices = ? order by ID_xml_info desc limit 1';
		$sth = $conn->prepare($query);
		$sth->execute(array($id_invoices));
		$res = $sth->fetch();
		return gzuncompress($res['xml']);
	}
	protected static function getNumberDir($dir){
		if(intval($dir) < 1000)
			return '1';
		if(intval($dir) > 1000){
			return intval(intval($dir)/1000) * 1000;
		}
	}

}