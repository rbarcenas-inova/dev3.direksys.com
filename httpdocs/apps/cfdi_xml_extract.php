<?php /*O3M*/
# --------------------------------------------------------
# Author: Oscar Maldonado
# Created on: 2013-12-17
# Description : Extract xml info
# Parameters : 
# Last Modified on: 
# Last Modified by:
# Example: cfdi_xml_extract.php?e=2&mode=debug&id=000000
##
require_once ("o3m_functions.php");
require_once ('ftp02.php');
parse_form($_GET, $_POST);
$e=$in['e'];
$ID_invoices= $in['id'];
if(!$limit){$limit=300;}
if($_SERVER['HTTP_HOST']=='mx.direksys.com'){
	load_vars($filename='/home/www/domains/direksys.com/cgi-bin/common/general.e'.$e.'.cfg'); //Produccion
	load_vars($filename='/home/www/domains/direksys.com/cgi-bin/common/general.cfdi.cfg'); //Produccion
	load_vars($filename='/home/www/domains/direksys.com/cgi-bin/common/general.cfdi.e'.$e.'.cfg'); //Produccion
	$path_logs = '/home/www/domains/direksys.com/files/e'.$e.'/cfdi/logs/';
	$File_path_tmp = '/home/www/domains/direksys.com/files/e'.$e.'/cfdi/results/';
}else{
	load_vars($filename='/home/www/domains/dev.omaldonado/dev2.direksys.com/cgi-bin/common/general.e'.$e.'.cfg');
	load_vars($filename='/home/www/domains/dev.omaldonado/dev2.direksys.com/cgi-bin/common/general.cfdi.cfg');
	load_vars($filename='/home/www/domains/dev.omaldonado/dev2.direksys.com/cgi-bin/common/general.cfdi.e'.$e.'.cfg');
	$path_logs = '/home/www/domains/dev.omaldonado/dev2.direksys.com/files/e'.$e.'/cfdi/logs/';
	$File_path_tmp = '/home/www/domains/dev.omaldonado/dev2.direksys.com/files/e'.$e.'/cfdi/results/';
}
require_once ('conex.php');
$ipServer = $cfg['ip_server']; // IP de servidor Produccion
$total_folios = $cfg['cfdi_tot_folios'];
$ftpFolderRFC = $cfg['cfdi_ftp_path'].'/';
$ftp_path = "/".$ftpFolderRFC; 
$cmdMode = array('debug','commit');
list($debug, $commit) = $cmdMode;
##---
if(in_array($Mode,$cmdMode) && !empty($e)){
	$sql="select ID_invoices,doc_serial,doc_num,concat(doc_serial,'_',doc_num) as invoice, Status from cu_invoices where Status='Certified' and xml_uuid is null";
	$Rows=SQLQuery($sql);
	for($x=1; $x<count($Rows); $x++){
		list($ID_invoices,$DocSerial,$DocNum,$Invoices,$Status) = $Rows[$x];
		$file_xml=$Invoices.'.xml';
		##Folder path			
		$FolderSerial='/'.$ftpFolderRFC.$DocSerial.'/';
		$FolderName=folderNum($DocNum,$total_folios); 		
		$FolderNum=$FolderSerial.$FolderName.'/';
		## XML extract info
		if(SearchFile($FolderNum.$file_xml)){
				DownloadFile($FolderNum.$file_xml, $File_path_tmp.$file_xml);
				$xmlInfo = xmlReader($File_path_tmp.$file_xml);
				$execXml=updateXmlInfo($ID_invoices, $xmlInfo['TimbreFiscalDigital']['UUID'],$xmlInfo['Comprobante']['fecha'],$xmlInfo['TimbreFiscalDigital']['FechaTimbrado']); # Actualiza cu_invoices
				unlink($File_path_tmp.$file_xml);
				echo "Listo ID_invoices: <a href='http://mx.direksys.com/files/e".$e."/cfdi/results/".$file_xml."' target='_blank'>".$file_xml."</a><br/>";
		}else{echo "ERROR: El documento ".$FolderNum.$file_xml." no existe.";}		
	}
}elseif(empty($e)){
	echo "Ingrese el numero de la empresa: e=?";
}else{echo "Sin autorizaci&oacuten";}
##---Functions
function updateXmlInfo($ID_invoices, $xml_uuid, $xml_fecha_emision, $xml_fecha_certificacion) {
# --------------------------------------------------------
# Author: Oscar Maldonado
# Created on: 2013-12-11
# Description : Update cu_invoices:xml_uuid, cu_invoices:xml_fecha_emision, cu_invoices:xml_fecha_certificacion
# Parameters : 
# Last Modified on: 
# Last Modified by:
    $exito = FALSE;
    $fEmision=explode('T',$xml_fecha_emision);
    $fCertificacion=explode('T',$xml_fecha_certificacion);
    $Sql="update cu_invoices set xml_uuid='$xml_uuid', xml_fecha_emision='$fEmision[0]', xml_fecha_certificacion='$fCertificacion[0]' where ID_invoices='$ID_invoices' limit 1";
    $exito = SQLExec($Sql);
    return $exito;
}
function folderNum($Folio=1, $Total=1){
# --------------------------------------------------------
# Author: Oscar Maldonado
# Created on: 2013-12-11
# Description : Obtiene el bloque al que pertenece un folio
# Parameters : $Folio INT, $Total INT ($Total corresponde al limite del bloque)
# Last Modified on: 
# Last Modified by:
	if($Folio>=$Total){
		 $Folder = floor($Folio/$Total)*$Total;
		 return $Folder;
	}else{return 1;} 
}
/*O3M*/
?>