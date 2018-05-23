<?php
session_start();
$COMMON_PATH = "../..";
include_once $COMMON_PATH . '/trsBase.php';
require_once $COMMON_PATH . '/common/php/class/db/DbHandler.php';
require_once $COMMON_PATH . '/common/php/class/dao.catalog.InvoicesDAO.php';
require_once $COMMON_PATH . '/common/php/class/dto.catalog.InvoicesDTO.php';
require_once $COMMON_PATH . '/ftp02.php';
require_once $COMMON_PATH . '/common/php/pdf/implode-pdf.php';
$PathPDF=$COMMON_PATH . '/common/php/pdf/';
$total_folios = $cfg['cfdi_tot_folios'];
$e=$in['e'];
$File_path = $cfg['path_invoices_tocert'].'e'.$e.'/cfdi/results/';
$ftp_path = $cfg['cfdi_ftp_path'];
if($ftp_path!=''){$ftp_path.='/';}
$File_name=$_GET['f'];
$ID_invoices=$_GET['id'];
$Mode=$_GET['m'];
#$File_name=substr($File_name,0,strlen($File_name)-1);
$File=explode('|',$File_name);
$FilesTot=count($File)-1;

for($x=0; $x<=$FilesTot; $x++){
	if(substr($File[$x],strlen($File[$x])-4,4)!='.pdf'){$File[$x].='.pdf';}
	$FileTmp=$File_path.$File[$x];

	/*Establece carpeta correspondiente al folio del invoice*/
	$Folio=explode('.',$File[$x]);
	$Folio=explode('_',$Folio[0]);
	if($Folio[1]>=$total_folios){
	    $Folder=floor($Folio[1]/$total_folios)*$total_folios;
	}else{$Folder=1;}
	$Folder='/'.$ftp_path.$Folio[0].'/'.$Folder.'/';
	/**/

	if(SearchFile($Folder.$File[$x])){
		DownloadFile($Folder.$File[$x], $FileTmp);
	}else{echo "ERROR: El documento $File[$x] no existe.";}
}
$FileResult=ImplodePDF($File_path,$File_name,'|','Facturas_CMU060119UI7',$PathPDF,true,$Mode);
for($x=0; $x<=$FilesTot; $x++){
	unlink($File_path.$File[$x]); 
	#$exit=updateRead($ID_invoices);	//Actualiza campo viewed
}
if(file_exists($FileResult)){
	$Handle = fopen($FileResult, 'rb');
	$Content = fread($Handle, filesize($FileResult));		
	fclose($Handle);
	if(strtolower(substr($FileResult, -3))=='pdf'){
		header("Content-type: application/pdf");
	}
	#if(!empty($ID_invoices) && $ID_invoices>0){$exit=updateRead($ID_invoices);}	//Actualiza campo viewed
	echo $Content;
	unlink($FileResult);
}else{
	// Intenta recargar hasta 3 veces el documento, en caso de que no se cargue correctamente.
	if($_GET['r']<1){$_GET['r']=1;}else{$_GET['r']++;}
		if($_GET['r']<4){
			echo "<meta content='1;URL=".$PHP_SELF."?f=".$_GET['f']."&m=".$_GET['m']."&r=".$_GET['r']."' http-equiv='REFRESH'></meta>";
			echo "Intentando acceder al documento... ".$File." <br /><a href='".$PHP_SELF."?f=".$_GET['f']."&m=".$_GET['m']."&r=".$_GET['r']."'>[Ver Ahora]</a>";
		}else{echo "ERROR: No se puede acceder al documento.";}
}
?>