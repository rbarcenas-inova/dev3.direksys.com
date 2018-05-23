<?php
// header('Content-Type: text/html; charset=ISO-8859-1');
require_once ROOT_FOLDER.'/../../phplibs/fpdf17/fpdf.custom.php';
require_once ROOT_FOLDER.'/../../phplibs/qrcode/qrcode.class.php';
// require_once ROOT_FOLDER.'/../../../../cfdi/common/php/letras.php';

function createPDF($id_invoices,$xml_string='',$type="show",$invoiceInfo = array(), $tt = 0){
	global $cfg;
	$earr = explode('_', $cfg['dbi_db']);
	$e = $earr[count($earr)-1];
	$filePdf = 'pdf_format';
	$extension = 'php';
	$fileVal = ROOT_FOLDER.'/libs/free/'.$filePdf.'.'.$e.'.'.$extension;
	$fileDefault = ROOT_FOLDER.'/libs/free/'.$filePdf.'.'.$extension;
	if( file_exists( $fileVal ) ){
		require_once $fileVal;
	}else{
		require_once $fileDefault;
	}
	return pdf($id_invoices,$xml_string,$type,$invoiceInfo, $tt);
}
