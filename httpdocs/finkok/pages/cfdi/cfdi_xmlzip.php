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
	if(substr($File[$x],strlen($File[$x])-4,4)!='.xml'){$FileAdenda[$x]=$File[$x].'_A.xml';}
	if(substr($File[$x],strlen($File[$x])-4,4)!='.xml'){$File[$x].='.xml';}		

	/*Establece carpeta correspondiente al folio del invoice*/
	$Folio=explode('.',$File[$x]);
	$Folio=explode('_',$Folio[0]);
	if($Folio[1]>=$total_folios){
	    $Folder=floor($Folio[1]/$total_folios)*$total_folios;
	}else{$Folder=1;}
	$Folder='/'.$ftp_path.$Folio[0].'/'.$Folder.'/';
	/**/

	if(SearchFile($Folder.$FileAdenda[$x])){
		$File[$x]=$FileAdenda[$x];
		$FileTmp=$File_path.$File[$x];
		DownloadFile($Folder.$File[$x], $FileTmp);
	}elseif(SearchFile($Folder.$File[$x])){
		$FileTmp=$File_path.$File[$x];
		DownloadFile($Folder.$File[$x], $FileTmp);
	}else{echo "ERROR: El documento $Folder $File[$x] no existe.";}
}
#----Crea Zip
chdir($File_path);
$ZipName = 'XML_CMU060119UI7_'.date('Ymd-His').'.zip';
$FileResult = new ZipArchive;
$FileResult->open($ZipName, ZipArchive::CREATE);
foreach ($File as $InZip) {
  $FileResult->addFile($InZip);
}
$FileResult->close();
#----
for($x=0; $x<=$FilesTot; $x++){unlink($File_path.$File[$x]);}
if(file_exists($ZipName)){
	header('Content-Type: application/zip');
	header('Content-disposition: attachment; filename='.$ZipName);
	header('Content-Length: ' . filesize($ZipName));
	readfile($ZipName);
	unlink($ZipName);
}else{
	// Intenta recargar hasta 3 veces el documento, en caso de que no se cargue correctamente.
	if($_GET['r']<1){$_GET['r']=1;}else{$_GET['r']++;}
		if($_GET['r']<4){
			echo "<meta content='1;URL=".$PHP_SELF."?f=".$_GET['f']."&m=".$_GET['m']."&r=".$_GET['r']."' http-equiv='REFRESH'></meta>";
			echo "Intentando acceder al documento... ".$File." <br /><a href='".$PHP_SELF."?f=".$_GET['f']."&m=".$_GET['m']."&r=".$_GET['r']."'>[Ver Ahora]</a>";
		}else{echo "ERROR: No se puede acceder al documento.";}
}
/**/
?>