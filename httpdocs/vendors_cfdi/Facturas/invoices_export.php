<?php 
include_once 'autoload.php';

$conect_to = 'e'.EMPRESA;
$conn = MysqlBD::getConexion($conect_to);

/*if( check_permissions('mod_vendor_cfdi_export', 'admin') !== 1 ){
	$msj_error = "No cuenta con permisos suficientes para esta operacion";

	header("Content-Type: application/force-download");
	header("Content-Type: application/octet-stream");
	header("Content-Type: application/download");

	// disposition / encoding on response body
	$filename = 'invoices_vendors_error';
	header("Content-Disposition: attachment; filename=$filename.csv;");
	header("Content-Transfer-Encoding: binary");
	header('Content-Type: application/csv');
	echo $msj_error;
	exit();
}*/

$from_table = "e".EMPRESA."_xml_info_vendor";
$query = "
	SELECT
		ID_xml_info_vendor as ID
		, ID_bills
		, ID_vendors
		, serie
		, folio
		, tipo
		, uuid
		, fecha_emision
		, fecha_certificacion
		, rfc
		, razon_social
		, total
		, `Status`
		, Concat(Date, ' ', Time)fh_recep
	FROM $from_table";

$where = ' WHERE 1 ';

if ($_GET['xml_uuid'] != '')		$where .= " AND uuid = '".$_GET['xml_uuid']."'";
if ($_GET['id_document'] != '')		$where .= " AND ID_xml_info_vendor = ".$_GET['id_document'];
if ($_GET['id_bills'] != '')		$where .= " AND ID_bills = ".$_GET['id_bills'];
if ($_GET['rfc'] != '')				$where .= " AND rfc LIKE '%".$_GET['rfc']."%'";
if ($_GET['razon_social'] != '')	$where .= " AND razon_social LIKE '%".$_GET['razon_social']."%'";
if ($_GET['serie'] != '')			$where .= " AND serie = '".$_GET['serie']."'";
if ($_GET['folio1'] != '')			$where .= " AND folio >= ".$_GET['folio1'];
if ($_GET['folio2'] != '')			$where .= " AND folio <= ".$_GET['folio2'];
if ($_GET['date1'] != '')			$where .= " AND DATE(fecha_certificacion) >= '".$_GET['date1']."'";
if ($_GET['date2'] != '')			$where .= " AND DATE(fecha_certificacion) <= '".$_GET['date2']."'";
if ($_GET['date3'] != '')			$where .= " AND Date >= '".$_GET['date3']."'";
if ($_GET['date4'] != '')			$where .= " AND Date <= '".$_GET['date4']."'";
if ($_GET['lstDocType'] != '')		$where .= " AND tipo = '".$_GET['lstDocType']."'";
if ($_GET['lstDocStatus'] != '')	$where .= " AND ´Status´ = '".$_GET['lstDocStatus']."'";
					
$groupBy = ' ';
$orderBy = ' ORDER BY ID_xml_info_vendor DESC';
/*
if ($_GET['order'][0]['column'] == 0){
	$orderBy = ' ORDER BY ID_xml_info_vendor DESC';
}else{
	$orderBy = ' ORDER BY '.$filters[$_POST['order'][0]['column']].' '.$in['order'][0]['dir'];
}

$limit = " LIMIT $in[start] , $in[length] ";
*/
$query_filter = $query.$where.$groupBy.$orderBy;
//echo $query_filter;

$res = $conn->query($query_filter);
//$all = $res->fetchAll(PDO::FETCH_ASSOC);

$data_export = "\"FOLIO RECEPCION\",\"SERIE\",\"FOLIO\",\"UUID\",\"FECHA/HORA CERT.\",\"RFC\",\"RAZON SOCIAL\",\"TOTAL\",\"TIPO\",\"ESTATUS\",\"FECHA RECEPCION\"\n";
while ($row = $res->fetch() ) {
	$data_export .= "\"".$row["ID"]."\",";
	$data_export .= "\"".$row["serie"]."\",";
	$data_export .= "\"".$row["folio"]."\",";
	$data_export .= "\"".$row["uuid"]."\",";
	$data_export .= "\"".$row["fecha_certificacion"]."\",";
	$data_export .= "\"".$row["rfc"]."\",";
	$data_export .= "\"".$row["razon_social"]."\",";
	$data_export .= "\"$ ".number_format($row["total"], '2', '.', ',')."\",";
	$data_export .= "\"".$row["tipo"]."\",";
	$data_export .= "\"".$row["Status"]."\",";
	$data_export .= "\"".$row["fh_recep"]."\"";
	$data_export .= "\n";
}

header("Content-Type: application/force-download");
header("Content-Type: application/octet-stream");
header("Content-Type: application/download");

// disposition / encoding on response body
$filename = 'invoices_vendors';
header("Content-Disposition: attachment; filename=$filename.csv;");
header("Content-Transfer-Encoding: binary");
header('Content-Type: application/csv');

echo $data_export;