<?php
namespace FacturasCFDI;
use DOMDocument;
use XSLTProcessor;
use FinkokWS;
use MysqlBD;
class Factura{
	protected $xml;
	protected $root;
	protected $datos;
	protected $cadenaOriginalXsl;
	protected $cadenaOriginal;
	protected $certificados;
	protected $addenda;
	protected $standard;
	protected $addendaName;
	protected $rawXML;
	protected $validadorCFDI;
	protected $validacionErrores;
	public function __construct($datos = array()){
		$this->xml = new DOMDocument('1.0','utf-8');
		$this->root = $this->xml->createElement('cfdi:Comprobante');
		$this->root = $this->xml->appendChild($this->root);
		$this->cadenaOriginalXsl = __DIR__.DIRECTORY_SEPARATOR.'..'.DIRECTORY_SEPARATOR.'sat'.DIRECTORY_SEPARATOR.'cadenaoriginal_3_2.xslt.xml';
		$this->validadorCFDI = __DIR__.DIRECTORY_SEPARATOR.'..'.DIRECTORY_SEPARATOR.'sat'.DIRECTORY_SEPARATOR.'cfdv32.xsd.xml';
		$this->cadenaOriginal = '';
		$this->certificados = CERT_FOLDER;
		$this->datos = $datos;	
		$this->addenda = array();
		$this->standard = array();
		$this->validacionErrores = array();
		$this->rawXML = '';
	}
	public function setDatos($datos){
		$this->datos = $datos;
		$addenda = "FacturasCFDI\Addendas\Estandar";
		$this->standard = $addenda::getAddendaStruct($datos);
		return $this;
	}
	public function getDatos(){
		return $this->datos;
	}
	public function createXMLFile(){
		$folder = '';
		$config = $GLOBALS['cfg']['path_invoices_tocert'];
		if( isset($config) && $config !=''){
			$folder = $config.'e'.EMPRESA.DIRECTORY_SEPARATOR.'cfdi'.DIRECTORY_SEPARATOR.'xml'.DIRECTORY_SEPARATOR.date('Y').DIRECTORY_SEPARATOR.date('Ymd');
		}
		if(!file_exists($folder))
			exec('mkdir -p -m 777 '.$folder);
		$file_name = $this->datos->ID_invoices.'-'.$this->datos->doc_serial.'-'.$this->datos->doc_num.'-'.date('G.m.s').'_tem'.'.xml';
		$file = $folder.DIRECTORY_SEPARATOR.$file_name;
		$xml = $this->createXML();
		if(is_array($xml) || $xml === FALSE){
			return array('Errores'=>$xml);
		}else{
			if(file_put_contents($file,$xml) === FALSE){
				return 'Error al Crear el XML : '.$file_name;
			}else{
				return 'XML : '.$file_name. ' Creado con Exito';
			}
		}

	}
	public function createXML(){
		$this->addNamespaces();
		$this->createNodes($this->standard);
		if(count($this->addenda) > 0)
			$this->createNodes($this->addenda);
		$this->addSign();
		$this->xml->formatOutput = true;
		$this->rawXML = $this->xml->saveXML();
		$verify = $this->validarFactura($this->rawXML);
		// echo $this->rawXML;
		if($verify === TRUE){
			return $this->rawXML;
		}else{
			return $verify;
		}
	}
	public function setAddenda($addendaName = ''){
		if($addendaName != ''){
			$addenda = "FacturasCFDI\Addendas\\".$addendaName;
			$this->addenda = $addenda::getAddendaStruct($this->datos);
			$this->addendaName = $addendaName;
		}
		return $this;
	}
	public function genCadenaOriginal(){
		$paso = new DOMDocument("1.0","utf-8");
		$paso->loadXML($this->xml->saveXML());
		$xsl = new DOMDocument('1.0','utf-8');
		$xsl->load($this->cadenaOriginalXsl);
		$proc = new XSLTProcessor();
		$proc->importStyleSheet($xsl);
		$this->cadenaOriginal = $proc->transformToXML($paso);
		return $this->cadenaOriginal;
	}
	public function getXMLFile(){
		header("Content-type: text/xml; charset=utf-8");
		$this->xml->formatOutput = true;
		echo $this->createXML();
	}
	public function timbrar($invoice = 0){
		$xml = $this->createXML();
		// print_r($xml);
		// print_r($this->validacionErrores);
		// print_r($this->validacionErrores);
		if(count($this->validacionErrores) == 0 and getRFC(EMPRESA) !== FALSE and !is_array($xml)) 
			return FinkokWS::Timbrar($xml,getRFC(EMPRESA),$invoice);
		$errores = '';
		foreach ($xml['errores'] as $key => $value) {
			$errores.= addslashes(htmlspecialchars($value->message))."\n<br>";
		}
		MysqlBD::executeQuery("update cu_invoices set `Status`='OnEdition' where id_invoices='$invoice'");
		MysqlBD::executeQuery("insert into cu_invoices_notes(ID_invoices,Notes,Type,Date,Time,ID_admin_users) values ('$invoice','$errores','Error',curdate(),curtime(),1)");
		return FALSE;
	}
	protected function getStandard(){
		return $this->standard;
	}
	protected function addNamespaces(){
		// Namespace SAT Genericos
		$this->addAtt(
			array('key'=>"xmlns:xsi",'value'=>"http://www.w3.org/2001/XMLSchema-instance")
			);
		$this->addAtt(
			array('key'=>"xmlns:cfdi",'value'=>"http://www.sat.gob.mx/cfd/3")
			);
		if($this->addendaName == 'detallista' or $this->addendaName == 'Liverpool'){
			$this->addAtt(array('key'=>'xmlns:detallista','value'=>'http://www.sat.gob.mx/detallista'));
			$this->addAtt(
			array('key'=>'xsi:schemaLocation', 'value'=>"http://www.sat.gob.mx/cfd/3 http://www.sat.gob.mx/sitio_internet/cfd/3/cfdv32.xsd http://www.sat.gob.mx/detallista http://www.sat.gob.mx/sitio_internet/cfd/detallista/detallista.xsd")
			);
		}else{
			$this->addAtt(
			array('key'=>"xsi:schemaLocation",'value'=>"http://www.sat.gob.mx/cfd/3 http://www.sat.gob.mx/sitio_internet/cfd/3/cfdv32.xsd")
			);
		}
	}
	protected function createNode($name,$value,$parent){
		$node = $this->xml->createElement($name,$value);
		if(is_null($parent))
			$node = $this->root->appendChild($node);
		else
			$node = $parent->appendChild($node);
		return $node;
	}
	protected function createNodes($datos,$parent = null){
		foreach($datos as $key => $value){
			if( isNumberArray($value) ){
				foreach ($value as $k => $v) {
					$tmp = $this->createNode($key,'',$parent);
					$this->createNodes($v,$tmp);	
				}
			}else{
				if( $key[0] == '@' ){
					$this->addAtt(array('key'=>substr($key,1),'value'=>$value),$parent);
				}elseif($key[0] != '#'){
					if(is_array($value)){
						$v = isset($value['#text']) ? $value['#text'] : '';
						$this->createNodes($value,$this->createNode($key,$v,$parent));
					}
					else{
						$this->createNode($key,$value,$parent);
					}
				}
			}
		}
	}
	protected function addAtt($atributo = array(),$parent = null){
		if(is_null($parent))
			$this->root->setAttribute($atributo['key'],$this->clearAtt($atributo['value']));
		else
			$parent->setAttribute($atributo['key'],$this->clearAtt($atributo['value']));
	}
	protected function addSign(){
		$nums = getKeyAndNumCert($this->getStandard()['cfdi:Emisor']['@rfc']);
		if($nums === FALSE)
			return;
		$certificado = $this->getStandard()['cfdi:Emisor']['@rfc'];
		$file=$this->certificados.DIRECTORY_SEPARATOR.strtolower($certificado).".key.pem";
		if(!file_exists($file)){
			$file=$this->certificados.DIRECTORY_SEPARATOR.strtoupper($certificado).".key.pem";
		}
		$pkeyid = openssl_get_privatekey(file_get_contents($file),$nums['pwd']);
		openssl_sign($this->genCadenaOriginal(), $crypttext, $pkeyid, OPENSSL_ALGO_SHA1);
		openssl_free_key($pkeyid);
		$sello = base64_encode($crypttext);
		$this->root->setAttribute("sello",$sello);

		$file=$this->certificados.DIRECTORY_SEPARATOR.strtolower($certificado).".cer.pem";
		if(!file_exists($file)){
			$file=$this->certificados.DIRECTORY_SEPARATOR.strtoupper($certificado).".cer.pem";
		}
		$datos = file($file);
		$ce = ""; $carga=false;
		for ($i=0; $i<sizeof($datos); $i++) {
		    if (strstr($datos[$i],"END CERTIFICATE")) $carga=false;
		    if ($carga) $ce .= trim($datos[$i]);
		    if (strstr($datos[$i],"BEGIN CERTIFICATE")) $carga=true;
		}
		$this->root->setAttribute("certificado",$ce);
	}
	protected function validarFactura($xmlString = ''){
		if($xmlString == '')
			return FALSE;
		$paso = new DOMDocument("1.0","UTF-8");
		$paso->loadXML($xmlString);
		libxml_use_internal_errors(true);
	    $ok = $paso->schemaValidate($this->validadorCFDI);
		$this->validacionErrores = libxml_get_errors();
		libxml_clear_errors();
		// echo $xmlString;
	    if($ok === TRUE && count($this->validacionErrores) == 0)
			return TRUE;
		else{
			return array('xml'=>$xmlString,'errores'=>$this->validacionErrores);
		}
	}
	protected function clearAtt($value){
		for ($i=0; $i < strlen($value); $i++) { 
			$a = substr($value,$i,1);
			if( $a > chr(127) && $a !== chr(219) && $a !== chr(211) && $a !== chr(209)){
				$value=substr_replace($value,'.',$i,1);
			}
		}
		$value = preg_replace('/\s\s+/',' ', $value);
		$value = trim($value);
		if(strlen($value) > 0){
			$value = str_replace(array('"','>','<'), '\'', $value);
			$value = utf8_encode(str_replace('|', '/', $value));
		}
		return $value;
	}
}