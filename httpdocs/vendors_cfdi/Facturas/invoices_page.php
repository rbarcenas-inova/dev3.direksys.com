<?php 
include_once 'autoload.php';

$conect_to = 'e'.EMPRESA;
$conn = MysqlBD::getConexion($conect_to);

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

if ($in['search']['value'] != ''){
	$where .= " AND (ID_xml_info_vendor = '".$in['search']['value']."' 
					OR ID_bills = '".$in['search']['value']."' 
					OR ID_vendors = '".$in['search']['value']."' 
					OR serie ='".$in['search']['value']."' 
					OR tipo = '".$in['search']['value']."' 
					OR uuid = '".$in['search']['value']."' 
					OR rfc like '%".$in['search']['value']."%' 
					OR razon_social like '%".$in['search']['value']."%'
					OR total = '".$in['search']['value']."'
					OR `Status` = '".$in['search']['value']."' 
				) ";
}

$filters_s = array('','ID_xml_info_vendor','serie','folio','fecha_certificacion','rfc','razon_social','total','tipo','`Status`','uuid','ID_vendors','ID_bills','Date');

foreach ($in['columns'] as $key => $value){
	if ( ( $key == '1' or $key == '2' or $key == '7' or $key == '8' or $key == '9') and $value['search']['value'] != '' ){
		$where .= " and  $filters_s[$key] = '".$value['search']['value']."' ";
	}elseif ( ($key == '5' or $key == '6') and $value['search']['value'] != '' and strlen($value['search']['value']) >= 4 ){
		$where .= " and  $filters_s[$key] LIKE '%".$value['search']['value']."%' ";
	}elseif ($key == '4' and $value['search']['value'] != ''){
		$d = explode("|",$value['search']['value']);
		if($d[0] != '' and $d[1] == ''){
			$where .= " AND DATE(".$filters_s[$key].") >= '".$d[0]."'";
		}elseif($d[0] == '' and $d[1] != ''){
			$where .= " AND DATE(".$filters_s[$key].") <= '".$d[1]."'";
		}elseif($d[0] != '' and $d[1] != ''){
			$where .= " AND DATE(".$filters_s[$key].") >= '".$d[0]."' AND DATE(".$filters_s[$key].") <= '".$d[1]."' ";
		// Filtro por fecha de recepción
		}elseif($d[2] != '' and $d[3] == ''){
			$where .= " AND ".$filters_s[$key+9]." >= '".$d[2]."'";
		}elseif($d[2] == '' and $d[3] != ''){
			$where .= " AND ".$filters_s[$key+9]." <= '".$d[3]."'";
		}elseif($d[2] != '' and $d[3] != ''){
			$where .= " AND ".$filters_s[$key+9]." >= '".$d[2]."' AND ".$filters_s[$key+9]." <= '".$d[3]."' ";
		}
	}elseif ($key == '3' and $value['search']['value'] != ''){
		$d = explode("|",$value['search']['value']);
		if ($d[0] != '' and $d[1] == ''){
			$where .= " and $filters_s[$key] >= '$d[0]'";
		}elseif ($d[0] == '' and $d[1] != ''){
			$where .= " and $filters_s[$key] <= '$d[1]' ";
		}elseif ($d[0] != '' and $d[1] != ''){
			$where .= " and $filters_s[$key] >= '$d[0]' and $filters_s[$key] <= '$d[1]' ";
		}
	}elseif ($value['search']['value'] != ''){
		$where .= " and  $filters_s[$key] like '".$value['search']['value']."%' ";
	}
}

$filters = array('','ID_xml_info_vendor','serie','folio','fecha_certificacion','rfc', 'razon_social', 'total', 'tipo', '`Status`');

$groupBy = ' ';

if ($in['order'][0]['column'] == 0){
	$orderBy = ' ORDER BY ID_xml_info_vendor DESC';
}else{
	$orderBy = ' ORDER BY '.$filters[$in['order'][0]['column']].' '.$in['order'][0]['dir'];
}

$limit = " LIMIT $in[start] , $in[length] ";

$query_filter = $query.$where.$groupBy.$orderBy;
$query.=$where.$groupBy.$orderBy.$limit;

$res = $conn->query($query);
$all = $res->fetchAll(PDO::FETCH_ASSOC);

$q = $query;
foreach ($all as $key => $value) {
	$all[$key] = clearArray($value);
	$icons = '';
	
	$icons = '<input data-id="'.$value['ID'].'" data-check="s" type="checkbox" name="checks" value="1">';

	$icons.='
	<a data-type="showPdf" target="_blank" href="/vendors_cfdi/Facturas/?e='.EMPRESA.'&action=showPDF&id_invoices='.$value['ID'].'" title="Ver PDF" class="grid_icons">
		<img alt="PDF" src="common/img/pdf.gif">
	</a>';
	
	$icons.='
	<a target="_blank" data-type="showXml"  href="/vendors_cfdi/Facturas/?e='.EMPRESA.'&action=showXML&id_invoices='.$value['ID'].'" title="Ver XML" class="grid_icons">
		<img alt="XML" src="common/img/xml.gif">
	</a>';
	
	$icons.='
	<a alt="Descargar PDF" target="_blank" data-type="downloadPdf" href="/vendors_cfdi/Facturas/?e='.EMPRESA.'&action=downloadPDF&id_invoices='.$value['ID'].'" title="Descargar PDF" class="grid_icons">
		<img alt="PDF" src="common/img/pdf_download.gif">
	</a>';

	$icons.='
	<a target="_blank" href="/vendors_cfdi/Facturas/?e='.EMPRESA.'&action=downloadXML&id_invoices='.$value['ID'].'" data-type="downloadXml" title="Descargar XML" class="grid_icons">
		<img alt="XML" src="common/img/xml_download.gif">
	</a>';
	if( $value['Status'] == 'Certified' && check_permissions('mod_vendor_cfdi_cancel', 'admin') == 1 ){
		$icons.='
		<a href="#" onclick="cancelInvoice(this)" data-id="'.$value['ID'].'" data-type="cancelCFDI" title="Cancelar CFDI" class="grid_icons">
			<img alt="Cancell" style="height: 18px; width: 18px;" src="common/img/delete.png">
		</a>';
	}

	$icons.='</span>';

	$all[$key]['usuario'] = '';
	$all[$key]['acciones'] = $icons;
 	$all[$key]['serie_folio'] = $value['folio'];
 	$all[$key]['orden'] = '';
 	$all[$key]['total'] = format_price_($value['total']);
 	$all[$key]['status'] = $value['Status'];
 	$all[$key]['id'] = $value['ID'];
 	$all[$key]['fecha_hora'] = $value['fecha_certificacion'];
 	
 	if( $value['ID_bills'] != '' && $value['ID_bills'] > 0 ){
		$all[$key]['total'] = '<a href="../cgi-bin/mod/'.$usr['application'].'/dbman?cmd=mer_bills&view='.$value['ID_bills'].'&second_conn=0" target="_blank" style="float: left;"><img src="common/img/bill.png" style="width: 16px" alt="bill" title="Bill: '.$value['ID_bills'].'" /></a> '.$all[$key]['total'];
	}
 	
}

$queryTotal = 'SELECT COUNT(*) total FROM '.$from_table;
$rs = $conn->query($queryTotal);
$rs = $rs->fetch(PDO::FETCH_ASSOC);

$queryFiltros = 'SELECT COUNT(*) total FROM ('.$query_filter.')tmp';
$rs2 = $conn->query($queryFiltros);
$rs2 = $rs2->fetch(PDO::FETCH_ASSOC);

$response = array(
	'data'=>$all,
	'draw'=>$in['draw'],
	'recordsTotal'=>$rs['total'],
	'recordsFiltered'=>$rs2['total']
);

header('Content-Type: application/json');
echo json_encode($response);