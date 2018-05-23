<?php
error_reporting(E_ALL);

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
$File_name=base64_decode($_GET['f']);
$ID_invoices=$_GET['id'];
$Mode=$_GET['m'];
$File=$File_path.$File_name;
/*Establece carpeta correspondiente al folio del invoice*/
$Folio=explode('.',$File_name);
$Folio=explode('_',$Folio[0]);
$Folder=$ftp_path.$Folio[0].DIRECTORY_SEPARATOR.getNumberDir($Folio[1]).DIRECTORY_SEPARATOR;

/**/
if(isset($cfg['read_xml_from_db']) && $cfg['read_xml_from_db'] == 1 ){
	require_once $COMMON_PATH . '/../phplibs/create_pdf.php';
	$file = substr($File_name,0,-4);
	$query = "select xml,id_orders from xml_info inner join ( select id_invoices,concat(doc_serial,'_',doc_num)invoice,id_orders from cu_invoices a inner join cu_invoices_lines b using (id_invoices))sl_orders using (id_invoices) where sl_orders.invoice = '$file'";
	$rs = mysql_query($query);
	$res = mysql_fetch_object($rs);
	$xml_content = gzuncompress($res->xml);

	if(strtolower(substr($File, -3))=='pdf'){
		header("Content-type: application/pdf");
		echo createPDF($res->id_orders,$xml_content,"string");
	}
	if(strtolower(substr($File, -3))=='xml'){
		header ("Content-type: application/xml");
		echo $xml_content;			
	}
}elseif (isset($_GET['readXml'])) {
	// define('ROOT_FOLDER','./../../../finkok/Facturas/');
	if($e == 11){
		require_once './../../../phplibs/create_pdf.php';
	}else{
		$_GET['re'] = 1;
		require_once './../../../finkok/Facturas/config.php';
		$in['e'] = $e;
	}
	// require_once './../../../finkok/Facturas/libs/free/create_pdf.php';
	$dbh = new DbHandler();
	$dbh->connect();
	$File_name = str_replace('.pdf', '.xml', $File_name);
	if(SearchFile($Folder.$File_name)){
		DownloadFile($Folder.$File_name, $File);
		if(file_exists($File)){
			if(!empty($ID_invoices) && $ID_invoices>0){
				$exit=updateRead($ID_invoices);
			}
			$rs = $dbh->selectSQLcommand("select id_orders from cu_invoices_lines where id_invoices = '$ID_invoices' limit 1");
			$res = $dbh->fetchAssocNextRow();
			$Handle = fopen($File, 'rb');
			$Content = fread($Handle, filesize($File));		
			fclose($Handle);
			// header("Content-type: application/pdf");
			echo createPDF($ID_invoices,$Content,"show");
			unlink($File);
		}
	}
}else{
	$addendaCopel = false;	
	$dbh = new DbHandler();
	$dbh->connect();
	$query = "select customer_fcode, id_customers from cu_invoices where id_invoices = $ID_invoices";
	$rs = mysql_query($query);
	$res = mysql_fetch_object($rs);
	if($res->customer_fcode == 'COP920428Q20' && $res->id_customers == '100037' && substr($File, -3) == 'xml'){
		$File_name = substr($File_name, 0,-4).'_A.xml';
		$addendaCopel = true;
	}
	if(SearchFile($Folder.$File_name)){
		DownloadFile($Folder.$File_name, $File);	
		if(file_exists($File)){
			$Handle = fopen($File, 'rb');
			$Content = fread($Handle, filesize($File));		
			fclose($Handle);
			$xml = false;
			if(strtolower(substr($File, -3))=='pdf'){
				header("Content-type: application/pdf");
			}
			if(strtolower(substr($File, -3))=='xml'){
				header ("Content-type: application/xml");	
				$xml = true;		
			}
			if($Mode==0){
				header ("Content-Disposition: attachment; filename=".$File_name);
				header ("Content-Type: application/octet-stream");
			}
			if(!empty($ID_invoices) && $ID_invoices>0){$exit=updateRead($ID_invoices);}	//Actualiza 
			if($addendaCopel){
				$xmlObj = simplexml_load_string($Content);
				$lineas = $xmlObj->xpath("//cfdi:Addenda/requestForPayment/lineItem");
				$defaultBoxSize = 16;
				$totalLotes = 0;
				$useDiff = false;
	
				foreach ($lineas as $key => $value) {
					$dbh->connect();
					$upc = (int)$value->tradeItemIdentification->gtin;
					$query = "select sl_customers_parts.packing_unit, sl_customers_parts.packing_type, sl_skus.UPC, sl_customers_parts.size, sl_customers_parts.sku_customers from sl_customers_parts 
						inner join sl_skus on sl_skus.ID_products = sl_customers_parts.ID_parts
						where sl_customers_parts.id_customers = 100037 and sl_skus.UPC = '$upc'";
					$rs = mysql_query($query);
					$res = mysql_fetch_object($rs);
					$boxSize = $defaultBoxSize;
					$boxType = 'BOX';

					if(isset($res->packing_unit))
						$boxSize = $res->packing_unit;
					if(isset($res->packing_type))
						$boxType = $res->packing_type;
					$totalLinea = (float)$value->palletInformation->palletQuantity;
					
					$value->palletInformation->description->attributes()->type = $boxType;
					
					$value->codigoTallaInternoCop->codigo = $res->sku_customers;
					$value->codigoTallaInternoCop->talla = $res->size;
					
					$value->palletInformation->prepactCant = $boxSize;
					$valPack = ceil($totalLinea / $boxSize);
					if(!$useDiff){
						$valPack2 = ceil($totalLinea / ($boxSize+1));
						$valPack3 = ceil($totalLinea / ($boxSize-1));
						if($valPack2 == $valPack){
							$value->palletInformation->prepactCant = $boxSize+1;
							$useDiff = true;
						}elseif($valPack3 == $valPack){
							$value->palletInformation->prepactCant = $boxSize-1;
							$useDiff = true;
						}
					}
					$totalLotes+= $valPack;
				}
				$lotes = $xmlObj->xpath("//cfdi:Addenda/requestForPayment/TotalLotes");
				$lotes[0]->cantidad = $totalLotes;
				echo $xmlObj->asXML();
			}else{
				echo $Content;
			}	

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
}



function updateRead($ID_invoices) {
    $exito = FALSE;
    $invoicesDTO = new InvoicesDTO();
    $invoicesDAO = new InvoicesDAO();
    $invoicesDTO->setID_invoices($ID_invoices);
    $invoicesDTO->setViewed(1);
    $exit = $invoicesDAO->updateRecord($invoicesDTO);
    return $exit;
}

function getNumberDir($dir){
	if(intval($dir) < 1000)
		return '1';
	if(intval($dir) > 1000){
		return intval(intval($dir)/1000) * 1000;
	}
}
?>