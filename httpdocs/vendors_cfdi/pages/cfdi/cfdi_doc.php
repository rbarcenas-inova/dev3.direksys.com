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
$File=$File_path.$File_name;
/*Establece carpeta correspondiente al folio del invoice*/
$Folio=explode('.',$File_name);
$Folio=explode('_',$Folio[0]);
if($Folio[1]>=$total_folios){
    $Folder=floor($Folio[1]/$total_folios)*$total_folios;
}else{$Folder=1;}
$Folder='/'.$ftp_path.$Folio[0].'/'.$Folder.'/';
/**/
if(SearchFile($Folder.$File_name)){
	DownloadFile($Folder.$File_name, $File);	
	if(file_exists($File)){
		$Handle = fopen($File, 'rb');
		$Content = fread($Handle, filesize($File));		
		fclose($Handle);
		if(strtolower(substr($File, -3))=='pdf'){
			header("Content-type: application/pdf");
		}
		if(strtolower(substr($File, -3))=='xml'){
			header ("Content-type: application/xml");			
		}
		if($Mode==0){
			header ("Content-Disposition: attachment; filename=".$File_name);
			header ("Content-Type: application/octet-stream");
		}
		if(!empty($ID_invoices) && $ID_invoices>0){$exit=updateRead($ID_invoices);}	//Actualiza campo viewed
		echo $Content;
		unlink($File);
	}else{
		// Intenta recargar hasta 3 veces el documento, en caso de que no se cargue correctamente.
		if($_GET['r']<1){$_GET['r']=1;}else{$_GET['r']++;}
			if($_GET['r']<4){
				echo "<meta content='1;URL=".$PHP_SELF."?f=".$_GET['f']."&id=".$_GET['id']."&r=".$_GET['r']."' http-equiv='REFRESH'></meta>";
				echo "Intentando acceder al documento... ".$File." <br /><a href='".$PHP_SELF."?f=".$_GET['f']."&id=".$_GET['id']."&r=".$_GET['r']."'>[Ver Ahora]</a>";
			}else{echo "ERROR: No se puede acceder al documento.";}
	}
}else{echo "ERROR: El documento no existe.";}

function updateRead($ID_invoices) {
    $exito = FALSE;
    $invoicesDTO = new InvoicesDTO();
    $invoicesDAO = new InvoicesDAO();
    $invoicesDTO->setID_invoices($ID_invoices);
    $invoicesDTO->setViewed(1);
    $exit = $invoicesDAO->updateRecord($invoicesDTO);
    return $exit;
}
?>