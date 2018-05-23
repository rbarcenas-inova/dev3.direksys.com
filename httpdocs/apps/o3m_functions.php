<?php
/**
* Funciones genericas para diversa aplicaciones.
* @author Oscar Maldonado [O3M]
*
**/
function load_vars($filename='') {
#Load config information from system.cfg file.
	global $sys, $cfg;	
	if (file_exists($filename)) {
        if ($handle = fopen($filename, 'r')) {
            while (!feof($handle)) {
                list($type, $name, $value) = preg_split("/\||=/", fgets($handle), 3);
				if ($type == 'sys') {
					$sys[$name] = trim($value);
					$val.=$type.' | '.$name.' = '.$value."<br/>\n\r";
				} elseif ($type == 'conf' or $type == 'conf_local') { 
					$cfg[$name] = trim($value);
					$val.=$type.' | '.$name.' = '.$value."<br/>\n\r";
				}
            }
        }
		return $val;
    }	   
}
function parse_form($g,$p){
# --------------------------------------------------------
# Author: Oscar Maldonado
# Created on: 2013-11-07
# Description : Load form information ($_GET/$_POST) into array $in[], $cmd[]
# Parameters : parse_form($_GET, $_POST);
# Last Modified on: 
# Last Modified by:
	global $in, $cmd;
	if(!empty($g)){
		$tvars = count($g);
		$vnames = array_keys($g);
		$vvalues = array_values($g);
	}elseif(!empty($p)){
		$tvars = count($p);
		$vnames = array_keys($p);
		$vvalues = array_values($p);
	}
	for($i=0;$i<$tvars;$i++){
		if($vnames[$i]=='cmd'){$cmd=$vvalues[$i];}
		$in[$vnames[$i]]=$vvalues[$i];
	}
}
function SQLLink(){
# --------------------------------------------------------
# Author: Oscar Maldonado
# Created on: 2013-11-07
# Description : Conection to MySQL
# Parameters : 
# Last Modified on: 
# Last Modified by:
	global $DBIConex;
	$Link=mysql_connect($DBIConex['Server'], $DBIConex['User'], $DBIConex['Password']) or die(mysql_error());
	mysql_select_db($DBIConex['DataBase'],$Link);
	mysql_query("SET NAMES 'utf8'", $Link);
	return $Link;
}
function SQLQuery($Sql='',$Table=0){
# --------------------------------------------------------
# Author: Oscar Maldonado
# Created on: 2013-11-07
# Description : Excecute a SELECT query and return the results
# Parameters : 
# Last Modified on: 
# Last Modified by:
	if(!empty($Sql)){
		$Cmd=array('SELECT');
		$vSql=explode(' ',$Sql);
		if(in_array(strtoupper($vSql[0]),$Cmd)){
			$Link=SQLLink();
			$Con=mysql_query($Sql, $Link)or die(mysql_error());	
			$TotRows=mysql_num_rows($Con);
			$TotCols=mysql_num_fields($Con);
			if($TotRows){		
				$y=0;
				$rKeys=array_keys(mysql_fetch_array($Con));	
				foreach($rKeys as $rkey){	
				##Table Titles in $Rows[0]
					if($z){$Rows[$y][$x] = $rKeys[$x]; $z=0;}else{$z++;}	
					$x++;
				}
				$y++;
				mysql_data_seek($Con,0);
				while($Row=mysql_fetch_array($Con)){
				##First record in $Rows[1]
					for($x=0; $x<=$TotCols; $x++){$Rows[$y][$x] = utf8_decode($Row[$x]);}
					$y++;
				}			
				if($Table){
				##Debug mode - Print HTML table with query results.
					$Result .= "<table border='1'>";
					foreach($Rows as $Row){
						$Result .= "<tr>";
						foreach($Row as $Cell){$Result .= "<td>".$Cell."</td>";}
						$Result .= "</tr>";
					}
					$Result .= "</table>";
				}else{$Result = $Rows;}
			}else{$Result = 0;}
			mysql_free_result($Con); 
			mysql_close($Link);
		}else{$Result = "Error: Wrong SQL instruction";}
	}else{$Result = "Error: Empty sel-query";}
	return $Result;
}
function SQLExec($Sql=''){
# --------------------------------------------------------
# Author: Oscar Maldonado
# Created on: 2013-11-07
# Description : Execute a INSERT,UPDATE,DELETE query and return the affected rows
# Parameters : 
# Last Modified on: 
# Last Modified by:
	if(!empty($Sql)){
		$Cmd=array('INSERT','UPDATE','DELETE');
		$vSql=explode(' ',$Sql);
		if(in_array(strtoupper($vSql[0]),$Cmd)){
			$Link=SQLLink();
			$Con=mysql_query($Sql, $Link)or die(mysql_error());	
			$TotRows=mysql_affected_rows();
			if($TotRows){$Result = $TotRows;}else{$Result = 0;}
			mysql_close($Link);
		}else{$Result = "Error: Wrong SQL instruction";}
	}else{$Result = "Error: Empty exe-query";}
	return $Result;
}
function xmlReader($xmlFile='', $debug=0){
# --------------------------------------------------------
# Author: Oscar Maldonado
# Created on: 2013-04-09
# Description : Lee un archivo xml con el formato CFDI (adaptado al formato generado por Signature EDX) (factura electr�nica) y muestra su contenido.
# Parameters : parse_form($_GET, $_POST);
# Last Modified on: 2013-12-11
# Last Modified by: O3M
	if(!empty($xmlFile)){
		//---Crea objeto xml
		$xml = simplexml_load_file($xmlFile);
		//---Define prefijos para Xpath
		$NameSpaces=$xml->getNamespaces(true);
		$ns=array('cfdi','tfd', 'ecfd', 'xmlns', 'xsi', 'xmlns');
		for ($x=1; $x<=count($ns); $x++){
			$xml->registerXPathNamespace($ns[$x], $NameSpaces[$ns[$x]]);
		}
		//---Define la secciones
		$Traces = array(
				'Comprobante' => '//cfdi:Comprobante',
				'Emisor' => '//cfdi:Comprobante//cfdi:Emisor',
				'Receptor' => '//cfdi:Comprobante//cfdi:Receptor',
				'Conceptos' => '//cfdi:Comprobante//cfdi:Conceptos',
				'Impuestos' => '//cfdi:Comprobante//cfdi:Impuestos',
				'Complemento' => '//cfdi:Comprobante//cfdi:Complemento',
				'Adenda' => '//cfdi:Comprobante//cfdi:Adenda',
				'DomicilioFiscal' => '//cfdi:Comprobante//cfdi:Emisor//cfdi:DomicilioFiscal',
				'ExpedidoEn' => '//cfdi:Comprobante//cfdi:Emisor//cfdi:ExpedidoEn',
				'RegimenFiscal' => '//cfdi:Comprobante//cfdi:Emisor//cfdi:RegimenFiscal',
				'ReceptorDomicilio' => '//cfdi:Comprobante//cfdi:Receptor//cfdi:Domicilio',
				'Concepto' => '//cfdi:Comprobante//cfdi:Conceptos//cfdi:Concepto',
				'Traslados' => '//cfdi:Comprobante//cfdi:Impuestos//cfdi:Traslados//cfdi:Traslado',
				'TimbreFiscalDigital' => '//cfdi:Comprobante//cfdi:Complemento//tfd:TimbreFiscalDigital',
				'ecfd' => '//ecfd:ECFD',
				'Documento' => '//ecfd:ECFD//ecfd:Documento',
				'Personalizados' => '//ecfd:ECFD//ecfd:Personalizados',
				'Encabezado' => '//ecfd:ECFD//ecfd:Documento//ecfd:Encabezado',
				'Detalle' => '//ecfd:ECFD//ecfd:Documento//ecfd:Detalle',
				'Referencia' => '//ecfd:ECFD//ecfd:Documento//ecfd:Referencia',
				'TimeStamp' => '//ecfd:ECFD//ecfd:Documento//ecfd:TimeStamp',
				'CampoString' => '//ecfd:ECFD//ecfd:Personalizados//ecfd:campoString',
				'IdDoc' => '//ecfd:ECFD//ecfd:Documento//ecfd:Encabezado//ecfd:IdDoc',
				'ExEmisor' => '//ecfd:ECFD//ecfd:Documento//ecfd:Encabezado//ecfd:ExEmisor',
				'DomFiscal' => '//ecfd:ECFD//ecfd:Documento//ecfd:Encabezado//ecfd:ExEmisor//ecfd:DomFiscal',
				'LugarExped' => '//ecfd:ECFD//ecfd:Documento//ecfd:Encabezado//ecfd:ExEmisor//ecfd:LugarExped',
				'ExReceptor' => '//ecfd:ECFD//ecfd:Documento//ecfd:Encabezado//ecfd:ExReceptor',
				'DomFiscalRcp' => '//ecfd:ECFD//ecfd:Documento//ecfd:Encabezado//ecfd:ExReceptor//ecfd:DomFiscalRcp',
				'LugarRecep' => '//ecfd:ECFD//ecfd:Documento//ecfd:Encabezado//ecfd:ExReceptor//ecfd:LugarRecep',
				'Totales' => '//ecfd:ECFD//ecfd:Documento//ecfd:Encabezado//ecfd:Totales',
				'ExImpuestos' => '//ecfd:ECFD//ecfd:Documento//ecfd:Encabezado//ecfd:ExImpuestos',
				'ImpuestosDet' => '//ecfd:ECFD//ecfd:Documento//ecfd:Detalle//ecfd:ImpuestosDet'
				);
		//---Define los campos de cada seccion
		$Fields['Comprobante'] = array('NumCtaPago','LugarExpedicion','metodoDePago','tipoDeComprobante','total','Moneda','TipoCambio','descuento','subTotal','condicionesDePago','certificado','noCertificado','formaDePago','sello','fecha','folio','serie','version','xsi:schemaLocation','xmlns:cfdi','xmlns:xsi');
		$Fields['Emisor'] = array('rfc','nombre');
		$Fields['DomicilioFiscal'] = array('calle','noExterior','noInterior','colonia','municipio','estado','pais','codigoPostal');
		$Fields['ExpedidoEn'] = array('calle','noExterior','noInterior','colonia','municipio','estado','pais','codigoPostal');
		$Fields['RegimenFiscal'] = array('Regimen');
		$Fields['Receptor'] = array('rfc','nombre');
		$Fields['ReceptorDomicilio'] = array('calle','noExterior','noInterior','colonia','municipio','estado','pais','codigoPostal');
		$Fields['Concepto'] = array('cantidad','unidad','descripcion','valorUnitario','importe');
		$Fields['Impuestos'] = array('totalImpuestosTrasladados');
		$Fields['Traslados'] = array('impuesto','tasa', 'importe');
		$Fields['Complemento'] = array('');
		$Fields['TimbreFiscalDigital'] = array('version','UUID','FechaTimbrado','selloCFD','noCertificadoSAT','selloSAT','xmlns:tfd','xsi:schemaLocation');
		$Fields['Adenda'] = array('xmlns:ecfd','xsi:schemaLocation');
		$Fields['ecfd'] = array('version');
		$Fields['Documento'] = array('ID');
		$Fields['Encabezado'] = array('');
		$Fields['IdDoc'] = array('NroAprob','AnoAprob','Tipo','Serie','Folio','Estado','NumeroInterno','FechaEmis','FormaPago','MedioPago','LugarExpedicion','NumCtaPago','CondPago','TermPagoCdg','TermPagoDias');
		$Fields['ExEmisor'] = array('RFCEmisor','NmbEmisor',);
		$Fields['DomFiscal'] = array('Calle','NroExterior','NroInterior','Colonia','Municipio','Estado','Pais','CodigoPostal');
		$Fields['LugarExped'] = array('Calle','NroExterior','NroInterior','Colonia','Municipio','Estado','Pais','CodigoPostal');
		$Fields['ExReceptor'] = array('RFCRecep','NmbRecep',);
		$Fields['DomFiscalRcp'] = array('Calle','NroExterior','NroInterior','Colonia','Municipio','Estado','Pais','CodigoPostal');
		$Fields['LugarRecep'] = array('Calle','NroExterior','NroInterior','Colonia','Municipio','Estado','Pais','CodigoPostal');
		$Fields['Totales'] = array('Moneda','FctConv','SubTotal','MntDcto','MntBase','MntImp','VlrPagar','VlrPalabras');
		$Fields['ExImpuestos'] = array('TipoImp','TasaImp','MontoImp');
		$Fields['Detalle'] = array('NroLinDet','DscLang','DscItem','QtyItem','UnmdItem','PrcNetoItem','MontoNetoItem');
		$Fields['ImpuestosDet'] = array('TipoImp','TasaImp','MontoImp');
		$Fields['Referencia'] = array('NroLinRef','TpoDocRef','FolioRef');
		$Fields['Documento'] = array('TimeStamp');
		//---Campos Personalizados NOTA: @array(0=>Nombre de etiqueta, 1=>Nombre de atributo)
		//---		ejem: <[Etiqueta] [Atributo]="1">Txt</[Etiqueta]>
		$Fields['Personalizados'] = array('campoString','name');
		//---Asignar valores del xml a una matriz
		$xmlFields = array();
		for($x=1; $x<=count($Fields); $x++){
			$Name=key($Fields);	
			while(list(, $Field)=each($Fields[$Name])){
				if(empty($Field)){break;}		
				if($type==0){
					//---Con atributos con valores
					foreach ($xml->xpath($Traces[$Name]) as $cfdiData){
					  if($debug){echo "\$xmlArray['".key($Fields).$TitleExtra."']['".$Field."']=".$cfdiData[$Field]."<br/>";}
					  $xmlFields[key($Fields).$TitleExtra][$Field]=$cfdiData[$Field];
					}			
				}elseif($type==1){
					//---Sin atributos y con valores fuera de las etiquetas
					foreach ($xml->xpath($Traces[$Name].'//ecfd:'.$Field) as $cfdiData){
					  if($debug){echo "\$xmlArray['".key($Fields).$TitleExtra."']['".$Field."']=".$cfdiData[0]."<br/>";}					    
					  $xmlFields[key($Fields).$TitleExtra][$Field]=$cfdiData[$cfdiData[0]];
					}
				}elseif($type==2){
					//---Con atributos con valores y con valores fuera de las etiquetas
					foreach ($xml->xpath($Traces[$Name].'//ecfd:'.$Field) as $cfdiData){
						if($debug){echo "\$xmlArray['".key($Fields).$TitleExtra."']['".$cfdiData[$Fields[$Name][1]]."']=".$cfdiData[0]."<br/>";}						
						$xmlFields[key($Fields).$TitleExtra][$cfdiData[$Fields[$Name][1]]]=$cfdiData[$cfdiData[0]];
					}				
				}
			}
			next($Fields); 
		}
		return $xmlFields; 
	}else{return "No hay archivo XML seleccionado.";}
}

/**
 *          clearBOM Limpia de caracteres BOM a string
 *          @param  $string 	   Cadena a limpiar
 *          @return String         Cadena Limpia.
 *          @author Fabian Cañaveral
 */
function clearBOM($string){
	if (substr($string, 0, 3) == "\xef\xbb\xbf") {
	    $string = substr($string, 3);
	}
	return $string;
}

/*O3M*/
?>