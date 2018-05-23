<?php /*O3M*/
# --------------------------------------------------------
# Author: Oscar Maldonado
# Created on: 2013-11-07
# Description : Verify that the invoices files exist - PDF & XML
# Parameters : 
# Last Modified on: Load xml in DB on table xml_info, extract uuid and zip xml file, activate by parameter  -- 2015-12-02
# Last Modified by: Fabian Cañaveral
# Example: cfdi_verify.php?e=2&limit=300&mode=debug&log=1&txt=1$isegs=3600
##
require_once ("o3m_functions.php");
require_once ('ftp02.php');
require_once '../../phplibs/parsexml/src/autoload.php';
parse_form($_GET, $_POST);
$e=$in['e'];
$Mode=$in['mode'];
$printLog=$in['log'];
$txtLog=$in['txt'];
$limit=$in['limit'];
$intervalSegs=$in['isegs'];
if(!$limit){$limit=300;}
// if($_SERVER['HTTP_HOST']=='mx.direksys.com'){
	load_vars($filename='/home/www/domains/direksys.com/cgi-bin/common/general.e'.$e.'.cfg'); //Produccion
	load_vars($filename='/home/www/domains/direksys.com/cgi-bin/common/general.cfdi.cfg'); //Produccion
	load_vars($filename='/home/www/domains/direksys.com/cgi-bin/common/general.cfdi.e'.$e.'.cfg'); //Produccion
	$path_logs = '/home/www/domains/direksys.com/files/e'.$e.'/cfdi/logs/';
	$File_path_tmp = '/home/www/domains/direksys.com/files/e'.$e.'/cfdi/results/';
// }else{
// 	load_vars($filename='/home/www/domains/dev.omaldonado/dev2.direksys.com/cgi-bin/common/general.e'.$e.'.cfg');
// 	load_vars($filename='/home/www/domains/dev.omaldonado/dev2.direksys.com/cgi-bin/common/general.cfdi.cfg');
// 	load_vars($filename='/home/www/domains/dev.omaldonado/dev2.direksys.com/cgi-bin/common/general.cfdi.e'.$e.'.cfg');
// 	$path_logs = '/home/www/domains/dev.omaldonado/dev2.direksys.com/files/e'.$e.'/cfdi/logs/';
// 	$File_path_tmp = '/home/www/domains/dev.omaldonado/dev2.direksys.com/files/e'.$e.'/cfdi/results/';
// }
require_once ('conex.php');
$ipServer = $cfg['ip_server']; // IP de servidor Produccion
$total_folios = $cfg['cfdi_tot_folios'];
$ftpFolderRFC = $cfg['cfdi_ftp_path'].'/';
$ftp_path = "/".$ftpFolderRFC; 
$cmdMode = array('debug','commit');
list($debug, $commit) = $cmdMode;
##Start rutine
if(in_array($Mode,$cmdMode) && !empty($e)){
	$txtDebug.="Mode: ".strtoupper($Mode)."</br>";	
	#PASO 1 - Buscar en BD y mover archivos
	$txtDebug .= "--------------------Step 1<br/>\n\r";
	$sql="select ID_invoices,doc_serial,doc_num,concat(doc_serial,'_',doc_num) as invoice, Status from cu_invoices where status='InProcess' order by id_invoices limit $limit";
	$Rows=SQLQuery($sql);
	for($x=1; $x<count($Rows); $x++){
		$totRegs++;
		list($ID_invoices,$DocSerial,$DocNum,$Invoices,$Status) = $Rows[$x];
		$file_pdf=$Invoices.'.pdf';
		$file_xml=$Invoices.'.xml';
		$file_xml_adenda=$Invoices.'_A.xml';
		$txtDebug .= $x.' -- ['.date('Y-m-d H:i:s').'] -- '.$file_pdf.' | '.$file_xml.' | '.$file_xml_adenda.'|';
		##Folder path			
		$FolderSerial='/'.$ftpFolderRFC.$DocSerial.'/';
		$FolderName=folderNum($DocNum,$total_folios); 		
		$FolderNum=$FolderSerial.$FolderName.'/';
		if(!CheckFolder($FolderNum)){$txtDebug .= 'New Directory: '.$FolderNum.'|';}else{$txtDebug .= 'Exist Directory|';}
		if($Mode==$commit){
			if(!CheckFolder($FolderSerial)){MakeDir($FolderSerial);}
		    if(!CheckFolder($FolderNum)){MakeDir($FolderNum);}
		}	
		
		##Set diff on time
		$sql2="SELECT ID_invoices,Action,Timestamp FROM cu_invoices_logs WHERE Action='Sent' and ID_invoices='$ID_invoices' order by Timestamp DESC limit 1";
		$Rows2=SQLQuery($sql2);
		$txtDebug .= $sql2.' | ';
		list($ID_invoices2,$Action2,$Timestamp2) = $Rows2[1];
		if(!$intervalSegs){$intervalSegs=3600*2;} // 1 = un segundo; 3600 = 1 hora
		//$intervalSegs=3600*2; // 1 = un segundo; 3600 = 1 hora
		$sendDate=date('Y-m-d H:i:s',strtotime($Timestamp2));
		$delayDate=date('Y-m-d H:i:s');
		$diffDate=abs(strtotime($sendDate)-strtotime($delayDate)); // 1 = un segundo; 3600 = 1 hora
		##Search files
		$filesList=ListFilesArray($ftp_path);
		if($Status=='InProcess' && in_array($file_pdf,$filesList) && in_array($file_xml,$filesList)){  
			if($Mode==$commit){
	    		if(in_array($file_pdf,$filesList)){

                    MoveFile($ftp_path.$file_pdf, $FolderNum.$file_pdf); 
                    $txtDebug .= "$file_pdf | Movido a: $FolderNum | ";
                    usleep(100000); // 1000000 = 1seg
                } 
                if(in_array($file_xml_adenda,$filesList)){
                    MoveFile($ftp_path.$file_xml_adenda, $FolderNum.$file_xml_adenda);
                    $txtDebug .= "$file_xml_adenda | Movido a: $FolderNum | ";
                    if(isset($cfg['read_xml_from_db']) && $cfg['read_xml_from_db'] == 1 ){
	                    if(file_exists($FolderNum.$file_xml_adenda)){
	                    	$xml_content = clearBOM(file_get_contents($FolderNum.$file_xml_adenda));
	                    	$xml_zipped =gzcompress($xml_content) ;
							$xmlExtractor = new cfdiMX\Parser($xml_content);
							$xmlObject = (object)$xmlExtractor->jsonSerialize();
							$uuid = $xmlObject->Comprobante['Complemento']['TimbreFiscalDigital']['@atributos']['UUID'];
							SQLQuery("insert into xml_info(ID_invoices,uuid,xml) values('$ID_invoices','$uuid','$xml_zipped')");
	                    }
                    }
                    usleep(100000);
                }
                if(in_array($file_xml,$filesList)){
                    MoveFile($ftp_path.$file_xml, $FolderNum.$file_xml);
                    $txtDebug .= "$file_xml | Movido a: $FolderNum | ";
                    if(isset($cfg['read_xml_from_db']) && $cfg['read_xml_from_db'] == 1 ){
	                    if(file_exists($FolderNum.$file_xml)){
	                    	$xml_content = clearBOM(file_get_contents($FolderNum.$file_xml));
	                    	$xml_zipped =gzcompress($xml_content) ;
							$xmlExtractor = new cfdiMX\Parser($xml_content);
							$xmlObject = (object)$xmlExtractor->jsonSerialize();
							$uuid = $xmlObject->Comprobante['Complemento']['TimbreFiscalDigital']['@atributos']['UUID'];
							SQLQuery("insert into xml_info(ID_invoices,uuid,xml) values('$ID_invoices','$uuid','$xml_zipped')");
	                    }
	                }
                    usleep(100000);
                }
	    		##Update records
		       	$execStatus=updateStatus($ID_invoices); # Actualiza Status a Certified
		        $execRead=updateRead($ID_invoices,1); # Actualiza Viewed = 1
		        $execLog=Update_Invoice_logs($ID_invoices); # Actualiza cu_invoices_logs
	            DownloadFile($FolderNum.$file_xml, $File_path_tmp.$file_xml);
		    	$xmlInfo = xmlReader($File_path_tmp.$file_xml);
		    	$execXml=updateXmlInfo($ID_invoices, $xmlInfo['TimbreFiscalDigital']['UUID'],$xmlInfo['Comprobante']['fecha'],$xmlInfo['TimbreFiscalDigital']['FechaTimbrado']); # Actualiza cu_invoices
	            unlink($File_path_tmp.$file_xml);
	    	}
	    	$txtDebug .= "Status=$execStatus|Read=$execRead|InvoiceLog=$execLog|";
	    }elseif($Status=='InProcess' && $diffDate>$intervalSegs){
	    #ivanmiranda :: Se desactiva el reinicio del proceso pasado cierto tiempo, para evitar problema de facturas duplicadas
	    	#if($Mode==$commit){
		    #	$execStatus=updateStatus($ID_invoices,0); # Actualiza Status a Confirmed
			#	file_get_contents("http://".$ipServer."/cfdi/common/php/signature/layout_cfdi_builder.php?e=".$e."&id_invoice=".$ID_invoices);
			#	$execLog=Update_Invoice_logs($ID_invoices,1);
			#	usleep(1000000); // 1 segundo de espera
			#}
			#$diffTime=$diffDate/60;
			#$txtDebug .= "ID invoice: $Invoices con TimeDelay: ".$diffTime." mins., reenviado a timbrar a las: ".$delayDate."|";
		}else{$txtDebug .= "No existen archivos para $Invoices o no el registro no esta en 'InProcces'|";}
	    $txtDebug .= "<br/>\n\r";	    
	}
	$txtDebug .= "--------------------Step 2<br/>\n\r";
	#PASO 2 - Buscar carpeta FTP, mover archivos y afectar BD
	$filesList=ListFilesArray($ftp_path);	
	#if(count($filesList)<$limit){$limit=count($filesList);}
	#for($x=1; $x<=$limit; $x++){
	for($x=1; $x<=count($filesList); $x++){
		$totRegs++;
		$txtDebug .= $totRegs.' -- ['.date('Y-m-d H:i:s').'] -- '.$filesList[$x].' | ';
		$filesList[$x]=str_replace($ftp_path, '', $filesList[$x]);
		$sExt=explode('.',$filesList[$x]);
		$sInvoice=explode('_',$sExt[0]);
		$sql="select ID_invoices,doc_serial,doc_num,concat(doc_serial,'_',doc_num) as invoice, Status from cu_invoices where doc_serial='$sInvoice[0]' and doc_num='$sInvoice[1]'";
		$Rows=SQLQuery($sql);
		$txtDebug .= $sql.' | '; 
		list($ID_invoices,$DocSerial,$DocNum,$Invoices,$Status) = $Rows[1];
		if($ID_invoices>0){
			##Folder path			
			$FolderSerial='/'.$ftpFolderRFC.$sInvoice[0].'/';
			$FolderName=folderNum($sInvoice[1],$total_folios); 		
			$FolderNum=$FolderSerial.$FolderName.'/';
			if(!CheckFolder($FolderNum)){$txtDebug .= 'New Directory: '.$FolderNum.'|';}else{$txtDebug .= 'Exist Directory|';}
			if($Mode==$commit){
				#Create directories
				if(!CheckFolder($FolderSerial)){MakeDir($FolderSerial);}
			    if(!CheckFolder($FolderNum)){MakeDir($FolderNum);}
				#Move file
				MoveFile($ftp_path.$filesList[$x], $FolderNum.$filesList[$x]);
				$txtDebug .= $filesList[$x]." | Movido a: $FolderNum | ";
				usleep(100000);
				##Update records
				if($Status=='InProcess'){
			       	$execStatus=updateStatus($ID_invoices); # Actualiza Status a Certified
			        $execRead=updateRead($ID_invoices,1); # Actualiza Viewed = 1
			        #$execLog=Update_Invoice_logs($ID_invoices); # Actualiza cu_invoices_logs
			        if(strtolower($sExt[1])=='xml'){
			            DownloadFile($FolderNum.$filesList[$x], $File_path_tmp.$filesList[$x]);
				    	$xmlInfo=xmlReader($File_path_tmp.$filesList[$x]);
				    	$execXml=updateXmlInfo($ID_invoices, $xmlInfo['TimbreFiscalDigital']['UUID'],$xmlInfo['Comprobante']['fecha'],$xmlInfo['TimbreFiscalDigital']['FechaTimbrado']); # Actualiza cu_invoices_logs
			            unlink($File_path_tmp.$filesList[$x]);
		        	}
		        	$txtDebug .= "Status=$execStatus|Read=$execRead|InvoiceLog=$execLog|";
		        }else{$txtDebug .= "Status: $Status |";}
	        }
            $txtDebug .= "$filesList[$x] Movido a: $FolderNum | ";            
		}else{$txtDebug .= "No existe registro en cu_invoices para: ".$filesList[$x];}
		$txtDebug .= "<br/>\n\r";
	}
	$txtDebug .= "--------------------Step 3<br/>\n\r";
	#PASO 3 - Extraer Información de XML
	$sql="select ID_invoices,doc_serial,doc_num,concat(doc_serial,'_',doc_num) as invoice, Status from cu_invoices where Status='Certified' and xml_uuid is null";
	$Rows=SQLQuery($sql);
	for($x=1; $x<count($Rows); $x++){
		$totRegs++;
		$txtDebug .= $totRegs.' -- ['.date('Y-m-d H:i:s').'] -- '.$filesList[$x].' | ';
		list($ID_invoices,$DocSerial,$DocNum,$Invoices,$Status) = $Rows[$x];
		$file_xml=$Invoices.'.xml';
		##Folder path			
		$FolderSerial='/'.$ftpFolderRFC.$DocSerial.'/';
		$FolderName=folderNum($DocNum,$total_folios); 		
		$FolderNum=$FolderSerial.$FolderName.'/';
		## XML extract info
		if(SearchFile($FolderNum.$file_xml)){
			if($Mode==$commit){
				DownloadFile($FolderNum.$file_xml, $File_path_tmp.$file_xml);
				$xmlInfo = xmlReader($File_path_tmp.$file_xml);
				$execXml=updateXmlInfo($ID_invoices, $xmlInfo['TimbreFiscalDigital']['UUID'],$xmlInfo['Comprobante']['fecha'],$xmlInfo['TimbreFiscalDigital']['FechaTimbrado']); # Actualiza cu_invoices
				unlink($File_path_tmp.$file_xml);
			}
				$txtDebug .= "XML Info extraida de ".$file_xml." | ".$xmlInfo['TimbreFiscalDigital']['UUID']." | ".$xmlInfo['Comprobante']['fecha']." | ".$xmlInfo['TimbreFiscalDigital']['FechaTimbrado']."|<br/>\r\n";
		}else{$txtDebug .= "ERROR: El documento ".$FolderNum.$file_xml." no existe.";}		
	}
	$txtDebug .= "-----------End of rutine";
	##############

	##Print txtDebug
	if($printLog){echo $txtDebug;}
	##Create Log file
    if($txtLog){    
	    $fp = fopen($path_logs."verify.e".$e."_".date('Ymd-His').".txt","w+");
		fwrite($fp, $txtDebug);
		fclose($fp);
	}
}elseif(empty($e)){
	echo "Ingrese el numero de la empresa: e=?";
}else{echo "Sin autorizaci&oacuten";}
##End rutine

###---Functions---####
function updateStatus($ID_invoices, $Status=1) {
# --------------------------------------------------------
# Author: Oscar Maldonado
# Created on: 2013-11-07
# Description : Update cu_invoices:Status
# Parameters : 
# Last Modified on: 
# Last Modified by:
    $exito = FALSE;
    if(!$Status){$Status="Confirmed";}else{$Status="Certified";}
    $Sql="update cu_invoices set Status='$Status' where ID_invoices='$ID_invoices' limit 1";
    $exito = SQLExec($Sql);
    return $exito;
}
function updateRead($ID_invoices, $value=1) {
# --------------------------------------------------------
# Author: Oscar Maldonado
# Created on: 2013-11-07
# Description : Update cu_invoices:viwed
# Parameters : 
# Last Modified on: 
# Last Modified by:
    $exito = FALSE;
    $Sql="update cu_invoices set viewed='$value' where ID_invoices='$ID_invoices' limit 1";
    $exito = SQLExec($Sql);
    return $exito;
}
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
function Update_Invoice_logs($ID_Invoices='0', $Action=0){
# --------------------------------------------------------
# Author: Oscar Maldonado
# Created on: 2013-11-07
# Description : Update cu_invoices_logs
# Parameters : 
# Last Modified on: 
# Last Modified by:
	$exito = FALSE;
	if(!$Action){$Action='Received';}else{$Action='Sent';}
    #date_default_timezone_set("America/Mexico_City");
    #$Timestamp=date("Y-m-d G:i:s"); 
    $sql="insert into cu_invoices_logs 
            (Action, ID_invoices, doc_serial, doc_num, doc_date, ID_orders, ID_creditmemos, Timestamp, ID_admin_users)
            select '$Action', a.ID_invoices, a.doc_serial, a.doc_num, a.doc_date, b.ID_orders, b.ID_creditmemos, CURRENT_TIMESTAMP(), a.ID_admin_users
            from cu_invoices a
            left join cu_invoices_lines b using(ID_invoices) 
            where a.ID_invoices='$ID_Invoices'
            group by a.ID_invoices";
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