<?php
namespace FacturasCFDI\Addendas;
use MysqlBD;
use PDO;
class NWM9709244W4{
    public static function getAddendaStruct($data) {
    	$conn = MysqlBD::getConexion();
    	$query = "select 
			DATE_FORMAT(cu_invoices.doc_date, '%Y') AS 'AddendaWalmart->Anio'
			, cu_invoices.exchange_receipt AS 'AddendaWalmart->FolioRecibo' 
			, IF(cu_invoices.invoice_type='ingreso',cu_invoices.ID_orders_alias,'') AS 'AddendaWalmart->ordenCompra'
			, sl_customers.PersonalID AS 'AddendaWalmart->numeroProveedor'
			, (SELECT cu_customers_addresses.Code FROM cu_customers_addresses WHERE cu_customers_addresses.Alias = cu_invoices.customer_shpaddress_alias AND cu_customers_addresses.Alias <> '' LIMIT 1) AS 'AddendaWalmart->unidadCEDIS'
			, cu_invoices.customer_shpaddress_code
			, cu_invoices.customer_shpaddress_alias -- su descripcion
			from cu_invoices
			inner join cu_invoices_lines ON cu_invoices_lines.ID_invoices=cu_invoices.ID_invoices
			inner join sl_customers ON sl_customers.ID_customers=cu_invoices.ID_customers
			where 1 
				AND	cu_invoices.customer_fcode='NWM9709244W4'
				AND cu_invoices.ID_invoices = $data->ID_invoices
			group by cu_invoices_lines.ID_invoices";
		$rs = $conn->query($query);
		$row = $rs->fetch(PDO::FETCH_OBJ);
        $structuraAddenda = array(
			"cfdi:Addenda" => array(
	            "AddendaWalmart"=>array(
	                "@xmlns"=>"http://www.pegasotecnologia.com/secfd/Schemas/Receptor/Walmart", 
	                "@xsi:schemaLocation"=>"http://www.pegasotecnologia.com/secfd/Schemas/Receptor/Walmart http://www.pegasotecnologia.com/secfd/Schemas/Receptor/AddendaWalmart.xsd", 
	                "@Anio"=>$row->{'AddendaWalmart->Anio'}, 
	                "@numeroProveedor"=>$row->{'AddendaWalmart->numeroProveedor'}, 
	                "@FolioRecibo"=>$row->{'AddendaWalmart->FolioRecibo'}, 
	                "@ordenCompra"=>$row->{'AddendaWalmart->ordenCompra'}, 
	                "@unidadCEDIS"=>$row->{'AddendaWalmart->unidadCEDIS'}
	            )
	        )
        );
        return $structuraAddenda;
    }
}
