<?php 
include_once 'autoload.php';
$conn = MysqlBD::getConexion();
$query = "SELECT 
	cu_invoices.id_invoices id
	, id_customers
	, IF( doc_num = 0 , '', concat(doc_serial, '-', doc_num )) folio
	, CASE
    	WHEN cu_invoices.invoice_type = 'ingreso' THEN 'Factura'
    	WHEN cu_invoices.invoice_type = 'egreso' THEN 'Nota de Credito'
    	WHEN cu_invoices.invoice_type = 'traslado' THEN 'Traslado'
    	WHEN cu_invoices.invoice_type = 'pago' THEN 'Pago'
	  END tipodoc
	, `Status` status
	, doc_date fecha_hora
	, xml_uuid uuid
	, customer_fcode rfc
	, customer_fname razon
	, invoice_total total
	, (if(ID_orders != 0,ID_orders,ID_creditmemos)) orden 
	, (if(ID_orders != 0,'orden','creditmemo')) tipo
	, (
		select 
			concat('Created by (',admin_users.id_admin_users,') ',  firstName, ' ' ,middleName, ' ', lastName ) name
 		from admin_users 
 		where 
 			admin_users.id_admin_users = cu_invoices.id_admin_users 
 		limit 1
 	) usuario
	, cu_invoices.use_cfdi
	, cu_invoices.payment_type
	, cu_invoices.payment_method
	, cu_invoices.customer_fcode_bank
	, cu_invoices.customer_bank
	, cu_invoices.customer_account_number
	,(
		SELECT GROUP_CONCAT( CONCAT(Date,' ', Time, ' : ',  Notes) ORDER BY Date DESC SEPARATOR \"<br><hr>\") Notas
		FROM cu_invoices_notes
		WHERE ID_invoices=cu_invoices.ID_invoices AND `Type` = 'Error'
	 )Notas
	FROM 
		cu_invoices 
	INNER JOIN cu_invoices_lines on cu_invoices_lines.ID_invoices = cu_invoices.ID_invoices ";

$where = ' WHERE 1';

if($in['search']['value'] != ''){
	$where .= " and (cu_invoices.id_invoices = '".$in['search']['value']."' or
	id_customers = '".$in['search']['value']."' or
	doc_serial like '%".$in['search']['value']."%' or
	doc_num like '%".$in['search']['value']."%' or
	invoice_type like '%".$in['search']['value']."%' or
	`Status` like '%".$in['search']['value']."%' or
	xml_uuid like '".$in['search']['value']."' or
	cu_invoices_lines.ID_orders like '%".$in['search']['value']."%' or
	cu_invoices_lines.ID_creditmemos like '%".$in['search']['value']."%' or
	customer_fcode = '".$in['search']['value']."' or
	customer_fname like '%".$in['search']['value']."%' or
	invoice_total like '%".$in['search']['value']."%') ";
}
$filters_s = array('cu_invoices.id_customers','cu_invoices.id_invoices','doc_serial','doc_num','doc_date', 'xml_uuid', 'customer_fname', 'invoice_total', 'invoice_type', '`Status`','xml_uuid','id_customers');
foreach($in['columns'] as $key => $value){
	if($key == '11' and $value['search']['value'] != ''){
		$where.= " AND (ID_orders = ".$value['search']['value']." OR ID_creditmemos = ".$value['search']['value']." ) ";
	}elseif( ( $key == '1' or $key == '0' or $key == '5' or $key == '2' or $key == '9' or $key == '8' or $key == '10') and $value['search']['value'] != ''){
		$where.=" and  $filters_s[$key] = '".$value['search']['value']."' ";
	}elseif($key == '4' and $value['search']['value'] != ''){
		$d = explode("|",$value['search']['value']);
		if($d[0] != '' and $d[1] == ''){
			$where.=" AND DATE(".$filters_s[$key].") >= '".$d[0]."'";
		}elseif($d[0] == '' and $d[1] != ''){
			$where.=" AND DATE(".$filters_s[$key].") <= '".$d[1]."'";
		}elseif($d[0] != '' and $d[1] != ''){
			$where.=" AND DATE(".$filters_s[$key].") >= '".$d[0]."' AND DATE(".$filters_s[$key].") <= '".$d[1]."' ";
		}
	}elseif($key == '3' and $value['search']['value'] != ''){
		$d = explode("|",$value['search']['value']);
		if($d[0] != '' and $d[1] == ''){
			$where.=" and $filters_s[$key] >= '$d[0]'";
		}elseif($d[0] == '' and $d[1] != ''){
			$where.=" and $filters_s[$key] <= '$d[1]' ";
		}elseif($d[0] != '' and $d[1] != ''){
			$where.=" and $filters_s[$key] >= '$d[0]' and $filters_s[$key] <= '$d[1]' ";
		}
	}elseif($value['search']['value'] != ''){
		$where.=" and  $filters_s[$key] like '%".$value['search']['value']."%' ";
	}
}

$limit = " LIMIT $in[start] , $in[length] ";
$filters = array('','cu_invoices.id_invoices','ID_orders','doc_serial','doc_num','doc_date', 'xml_uuid', 'customer_fname', 'invoice_total', 'invoice_type', '`Status`','xml_uuid','id_customers');
// print_r($in);

if($in['order'][0]['column'] == 0){
	$orderBy = ' order by cu_invoices.id_invoices desc ';
}else{
	$orderBy = ' order by '.$filters[$in['order'][0]['column']].' '.$in['order'][0]['dir'];
}
$groupBy = ' GROUP BY cu_invoices.id_invoices ';
$query.=$where.$groupBy.$orderBy.$limit;

$res = $conn->query($query);
$all = $res->fetchAll(PDO::FETCH_ASSOC);
$q = $query;
foreach ($all as $key => $value) {
	$all[$key] = clearArray($value);
	$icons = '';
	//downloadXML
	if($value['status'] == 'Certified' || $value['status'] == 'Cancelled' ){
		$icons = '<input data-id="'.$value['id'].'" data-check="s" type="checkbox" name="checks" value="1">';
		$icons .= '<span class="icons" data-id_invoice="'.$value['id'].'">';
		if(in_array($value['tipodoc'], ['Factura', 'Nota de Credito']))
			$icons .='<img width="18px" height="18px" target="_blank" alt="Detalle" onclick="editCFDI('.$value['id'].',1)" style="cursor: pointer" src="common/img/view.png">';

		if(EMPRESA == '15'){
			$icons.='<a data-type="showPdf" target="_blank" href="/finkok/Facturas/?action=showPDF&id_invoices='.$value['id'].'&tt=1" >
				<img width="24px" height="24px" style="cursor: pointer" src="common/img/pdf.gif">
			</a>';
		}
		$icons.='<a data-type="showPdf" target="_blank" href="/finkok/Facturas/?action=showPDF&id_invoices='.$value['id'].'" >
			<img width="24px" height="24px" style="cursor: pointer" src="common/img/pdf.gif">
		</a>
		<a target="_blank" data-type="showXml"  href="/finkok/Facturas/?action=showXML&id_invoices='.$value['id'].'">
			<img width="24px" height="24px" alt="XML" style="cursor: pointer" src="common/img/xml.gif">
		</a><a alt="Descargar PDF" target="_blank" data-type="downloadPdf" href="/finkok/Facturas/?action=downloadPDF&id_invoices='.$value['id'].'">
			<img width="24px" height="24px" style="cursor: pointer" src="common/img/pdf_download.gif">
		</a>
		<a target="_blank" href="/finkok/Facturas/?action=downloadXML&id_invoices='.$value['id'].'" data-type="downloadXml">
		<img width="24px" height="24px" alt="XML" style="cursor: pointer" src="common/img/xml_download.gif">
		</a>';
		if($cfg['fac_type'] != 'edx'){
			$icons .= $value['status'] == 'Cancelled' ? '</span>' : 
			'<a data-id="'.$value['id'].'" data-factura="'.$value['serie'].'-'.$value['folio'].'" onclick="cancelInvoice(this)"><img width="18px" height="18px" alt="Cancel Invoice" style="cursor:pointer" src="/sitimages/default/delete.png"></a>';
		}		
		$icons.='</span>';
	}else{
		$icons='<input id="'.$value['id'].'" type="checkbox" name="checks" value="1" style="opacity:0" disable>';
		if(in_array($value['tipodoc'], ['Factura', 'Nota de Credito', 'Pago']))
			$icons.='<span class="icons" data-id_invoice="'.$value['id'].'">
	<img width="18px" height="18px" target="_blank" alt="Detalle" onclick="editCFDI('.$value['id'].',1)" style="cursor: pointer" src="common/img/view.png"></span>';
		
		// Edit
		if( $value['status'] != 'Certified' && $value['status'] != 'Cancelled' ){
			$icons .= '<a data-id="'.$value['id'].'" data-factura="'.$value['serie'].'-'.$value['folio'].'" data-use="'.$value['use_cfdi'].'" data-ptype="'.$value['payment_method'].'" data-pmethod="'.$value['payment_type'].'" data-doctype="'.$value['tipodoc'].'" data-cusfcode_bank="'.$value['customer_fcode_bank'].'" data-cusbank="'.$value['customer_bank'].'" data-cusaccount_number="'.$value['customer_account_number'].'" onclick="editInvoice(this)" title="Edit Invoice" class="lnk_edit_invoice">
							<img width="17px" height="17px" alt="Edit Invoice" style="cursor:pointer" src="/sitimages/default/edit.png">
						</a>';
		}	
	}

	if( $all[$key]['status'] == 'OnEdition' ){
		$all[$key]['status'] = $all[$key]['status']. '<a href="#" onclick="openModal(`'.$all[$key]['Notas'].'`)" class="notas"><img src="/sitimages//default/warning.gif" style="width: 15px;margin: -3px 0;"></a>'; 
		$all[$key]['status'] .= '&nbsp;<a href="#" data-id="'.$value['id'].'" onclick="changeStatus(this)" title="Reintentar..."><img src="/sitimages//default/reload.png" style="width: 15px;margin: -3px 0;"></a>'; 
	} else {
		$all[$key]['status'];
	}
	$all[$key]['usuario'] = '<img title="'.$all[$key]['usuario'].'" src="/sitimages/hsi3.jpg"> ';
	$all[$key]['acciones'] = $icons;
 	$all[$key]['serie_folio'] = $value['folio'];
 	$all[$key]['orden'] = $value['tipo'] == 'orden' ? '<a target="_blank" href="/cgi-bin/mod/admin/dbman?cmd=opr_orders&view='.$all[$key]['orden'].'">'.$all[$key]['orden'].'</a>' : '<a href="/cgi-bin/mod/admin/dbman?cmd=opr_creditmemos&view='.$all[$key]['orden'].'">'.$all[$key]['orden'].'</a>';

 	$all[$key]['total'] = '$ '.number_format($value['total'],2);
}
$queryTotal = 'select count(*) total from cu_invoices';
$rs = $conn->query($queryTotal);
$rs = $rs->fetch(PDO::FETCH_ASSOC);
$queryFiltros = 'select count(*) total from (select count(*) total from cu_invoices inner join cu_invoices_lines on cu_invoices_lines.ID_invoices = cu_invoices.ID_invoices '.$where.$groupBy.')tmp';

$rs2 = $conn->query($queryFiltros);
$rs2 = $rs2->fetch(PDO::FETCH_ASSOC);
$response = array(
	'data'=>$all,
	'draw'=>$in['draw'],
	'recordsTotal'=>$rs['total'],
	'query'=>$q,
	'recordsFiltered'=>$rs2['total']
);
// show(json);
ob_flush();
header('Content-Type: application/json');
echo json_encode($response);

