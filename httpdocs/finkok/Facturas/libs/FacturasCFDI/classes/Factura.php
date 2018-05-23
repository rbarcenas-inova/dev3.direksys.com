<?php
namespace FacturasCFDI;
use DOMDocument;
use XSLTProcessor;
use FinkokWS;
use MysqlBD;
use Tabla;
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
	protected $version;
	protected $facturaAdded;
	protected $addendaAdded;
	protected $signService;
	protected $id_invoices;
	public function __construct($datos, $version = '3.2'){
		$this->xml = new DOMDocument('1.0','UTF-8');
		$this->root = $this->xml->createElement('cfdi:Comprobante');
		$this->root = $this->xml->appendChild($this->root);
		$this->addenda = array();
		$this->standard = array();
		$this->validacionErrores = array();
		$this->rawXML = '';
		$this->cadenaOriginal = '';
		$this->certificados = CERT_FOLDER;
		$this->facturaAdded = false;
		$this->addendaAdded = false;
		$this->setVersion($version);
		if($datos)
			$this->setDatos($datos);
		$this->signService = 'FinkokWS';
	}

	public function setVersion($version = '3.2'){
		if($version == '3.2'){
			$this->cadenaOriginalXsl = __DIR__.DIRECTORY_SEPARATOR.'..'.DIRECTORY_SEPARATOR.'sat'.DIRECTORY_SEPARATOR.'cadenaoriginal_3_2.xslt.xml';
			$this->validadorCFDI = __DIR__.DIRECTORY_SEPARATOR.'..'.DIRECTORY_SEPARATOR.'sat'.DIRECTORY_SEPARATOR.'cfdv32.xsd.xml';
		}
		elseif($version == '3.3')
			$this->cadenaOriginalXsl = __DIR__.DIRECTORY_SEPARATOR.'..'.DIRECTORY_SEPARATOR.'../../../cfdi3.3'.DIRECTORY_SEPARATOR.'cadenaoriginal_3_3.xslt';
		else
			throw new Exception("Version {$version} no es soportado.");
		
		$this->version = $version;
		return $this;
	}
	public function setDatos($datos){
		$this->datos = $datos;
		if($this->version == '3.2')
			$addenda = "FacturasCFDI\Addendas\Estandar";
		else if($this->version == '3.3')
			$addenda = "FacturasCFDI\Addendas\Estandar33";
		else {
			throw new \Exception("Version {$this->version} de CFDI No definida");
		}
		try{
			$this->id_invoices = $datos->ID_invoices;
		}catch(Exception $e){
			throw new \Exception("ID_invoices No definida");		
		}
		$this->standard = $addenda::getAddendaStruct($datos);

		return $this;
	}
	public function getDatos(){
		return $this->datos;
	}
	public function createXML($simple = false, $withoutAddenda = false){
		if($this->datos->invoice_type == 'pago')
			$withoutAddenda = true;
		if(!$this->facturaAdded){
			$this->addNamespaces();
			$this->createNodes($this->standard);
			$this->facturaAdded = true;
		}
		if(!$withoutAddenda)
			if(count($this->addenda) > 0)
				if(!$this->addendaAdded){
					$this->createNodes($this->addenda);
					$this->addendaAdded = true;
				}
		if($simple){
			$this->rawXML = $this->xml->saveXML();
			if(mb_detect_encoding($this->rawXML,  'UTF-8') != 'UTF-8');
				$this->rawXML = utf8_encode($this->rawXML);
			return $this->rawXML;	
		}
		$this->addSign();
		$this->xml->formatOutput = true;
		$this->rawXML = $this->xml->saveXML();
		if(mb_detect_encoding($this->rawXML,  'UTF-8') != 'UTF-8');
			$this->rawXML = utf8_encode($this->rawXML);
		return $this->rawXML;

		// TO DO Validacion Local para 3.3
		// $verify = $this->validarFactura($this->rawXML);
		// // echo $this->rawXML;
		// if($verify === TRUE){
		// 	return $this->rawXML;
		// }else{
		// 	return $verify;
		// }
	}
	public function setAddenda($addendaName = ''){
		if($addendaName != ''){
			$addenda = "FacturasCFDI\Addendas\\".$addendaName;
			$this->addenda = $addenda::getAddendaStruct($this->datos, $this);
			$this->addendaName = $addendaName;
		}
		return $this;
	}
	public function genCadenaOriginal(){
		$xmlString = $this->createXML(true, true);
		if(mb_detect_encoding($xmlString,  'UTF-8') != 'UTF-8');
			$xmlString = utf8_encode($xmlString);
		if($this->version == '3.2'){
			$paso = new DOMDocument("1.0","utf-8");
			if(mb_detect_encoding($xmlString,  'UTF-8') != 'UTF-8');
				$xmlString = utf8_encode($xmlString);
			$paso->loadXML($xmlString);
			$xsl = new DOMDocument('1.0','utf-8');
			$xsl->load($this->cadenaOriginalXsl);
			$proc = new XSLTProcessor();
			$proc->importStyleSheet($xsl);
			$this->cadenaOriginal = $proc->transformToXML($paso);
		}else if($this->version == '3.3'){
			$ran = md5(microtime());
			$fichero = __DIR__."/../../../files/xml_$ran.xml";
			$xslt = $this->cadenaOriginalXsl;
			file_put_contents($fichero, $xmlString);
			$cadena = exec("xsltproc $xslt $fichero");
			unlink($fichero);
			$this->cadenaOriginal = trim($cadena);
		}else{
			throw new \Exception("Version {$this->version} de CFDI No definida");
		}
		return $this->cadenaOriginal;
	}

	public function timbrar(){
		$xml = $this->createXML();
		return call_user_func_array(
			"{$this->signService}::Timbrar", array(
				$xml, 
				getRFC(EMPRESA), 
				$this->id_invoices
			)
		);
	}


	/*
	* 
	* Funciones Protegidas Solo para manipulacion del XML
	* 
	*/
	protected function getStandard(){
		return $this->standard;
	}
	protected function addNamespaces(){
		// Namespace SAT Genericos
		$this->addAtt(
			array(
				'key'=>"xmlns:xsi",
				'value'=>"http://www.w3.org/2001/XMLSchema-instance"
			)
		);
		$this->addAtt(
			array(
				'key'=>"xmlns:cfdi",
				'value'=>"http://www.sat.gob.mx/cfd/3"
			)
		);
		if($this->version == '3.2'){
			if($this->addendaName == 'detallista' or $this->addendaName == 'DLI931201MI9'){
				$this->addAtt(array('key'=>'xmlns:detallista','value'=>'http://www.sat.gob.mx/detallista'));
				$this->addAtt(
					array(
						'key'=>'xsi:schemaLocation', 
						'value'=>"http://www.sat.gob.mx/cfd/3 http://www.sat.gob.mx/sitio_internet/cfd/3/cfdv32.xsd http://www.sat.gob.mx/detallista http://www.sat.gob.mx/sitio_internet/cfd/detallista/detallista.xsd"
					)
				);
			}else{
				$this->addAtt(
					array(
						'key'=>"xsi:schemaLocation",
						'value'=>"http://www.sat.gob.mx/cfd/3 http://www.sat.gob.mx/sitio_internet/cfd/3/cfdv32.xsd"
					)
				);
			}
		}elseif($this->version == '3.3'){
			if($this->addendaName == 'detallista' or $this->addendaName == 'DLI931201MI9'){
				$this->addAtt(array('key'=>'xmlns:detallista','value'=>'http://www.sat.gob.mx/detallista'));
				$this->addAtt(
					array(
						'key'=>'xsi:schemaLocation', 
						'value'=>"http://www.sat.gob.mx/cfd/3 http://www.sat.gob.mx/sitio_internet/cfd/3/cfdv32.xsd http://www.sat.gob.mx/detallista http://www.sat.gob.mx/sitio_internet/cfd/detallista/detallista.xsd"
					)
				);
			}else{
				$this->addAtt(
					array(
						'key'=>"xsi:schemaLocation",
						'value'=>"http://www.sat.gob.mx/cfd/3 http://www.sat.gob.mx/sitio_internet/cfd/3/cfdv33.xsd"
					)
				);
			}
			
		}else{
			throw new Exception("Version {$this->version} no es soportado.");
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
		if($this->version == '3.2'){
			$nums = getKeyAndNumCert($this->getStandard()['cfdi:Emisor']['@rfc']);
			if($nums === FALSE)
				return;
			$certificado = $this->getStandard()['cfdi:Emisor']['@rfc'];
			$file=$this->certificados.DIRECTORY_SEPARATOR.strtolower($certificado).".key.pem";
		}else{
			$nums = getKeyAndNumCert($this->getStandard()['cfdi:Emisor']['@Rfc']);
			if($nums === FALSE)
				return;
			$certificado = $this->getStandard()['cfdi:Emisor']['@Rfc'];
			$file=$this->certificados.DIRECTORY_SEPARATOR.strtolower($certificado).".key.pem";
		}
		if(!file_exists($file)){
			$file=$this->certificados.DIRECTORY_SEPARATOR.strtoupper($certificado).".key.pem";
		}
		$pkeyid = openssl_get_privatekey(file_get_contents($file),$nums['pwd']);
		// show($file);
		// show(var_dump(file_get_contents($file));
		// exit;
		$cadena = $this->genCadenaOriginal();
		// Guardar Cadena en cu_invoices
		\Invoice::updateInvoice(intval($this->id_invoices), ['original_string' => $cadena]);
		if($this->version == '3.2'){
			openssl_sign($cadena, $crypttext, $pkeyid, OPENSSL_ALGO_SHA1);
		}else{
			openssl_sign($cadena, $crypttext, $pkeyid, "sha256WithRSAEncryption");
		}
		openssl_free_key($pkeyid);
		$sello = base64_encode($crypttext);
		if($this->version == '3.2'){
			$this->root->setAttribute("sello",$sello);
		}else{
			$this->root->setAttribute("Sello",$sello);
		}

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
		if($this->version == '3.2'){
			$this->root->setAttribute("certificado",$ce);
		}else{
			$this->root->setAttribute("Certificado",$ce);
		}
	}
	protected function validarFactura($xmlString = ''){
		libxml_disable_entity_loader(false);
		if($xmlString == '')
			return FALSE;
		$paso = new DOMDocument("1.0","UTF-8");
		$paso->loadXML(utf8_encode($xmlString));
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
		// $value = preg_replace('/\s\s\s+/',' ', $value);
		$value = trim($value);
		if(strlen($value) > 0){
			$value = str_replace(array('"','>','<'), '\'', $value);
			$value = utf8_encode(str_replace('|', '/', $value));
		}
		return $value;
	}
}