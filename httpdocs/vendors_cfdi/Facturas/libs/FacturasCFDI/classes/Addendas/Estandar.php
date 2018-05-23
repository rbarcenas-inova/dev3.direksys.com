<?php
namespace FacturasCFDI\Addendas;
use MysqlBD;
class Estandar{
	public static $id_invoices;
	public static function getAddendaStruct($invoice){
		self::$id_invoices = $invoice->ID_invoices;
		$conn = MysqlBD::getConexion();
		global $cfg;
		$rfcEmisor = $invoice->expediter_fcode;
		if(isset($cfg['finkok_test_mode']) && $cfg['finkok_test_mode'] == 1){
			$rfcEmisor = getRFC();
		}
		$data = array(
			'@formaDePago' => $invoice->payment_type,
			'@tipoDeComprobante' => $invoice->invoice_type,
			'@total' => $invoice->invoice_total,
			'@subTotal' => $invoice->invoice_net,
			'@noCertificado' => @getKeyAndNumCert($invoice->expediter_fcode)['cert'],
			'@NumCtaPago'=>$invoice->payment_digits!='' ? $invoice->payment_digits : 'NO IDENTIFICADO' ,
			'@LugarExpedicion'=>limpiar($invoice->expediter_faddress_country.','.$invoice->expediter_faddress_state),
			// '@serie' => $invoice->doc_serial,
			'@fecha' => join('T',explode(' ',$invoice->doc_date)),
			// '@folio' => $invoice->doc_num,
			'@version'=>"3.2",
			// '@FolioFiscalOrig'=>'',
			// '@SerieFolioFiscalOrig'=>'',
			// '@FechaFolioFiscalOrig'=>'',
			// '@MontoFolioFiscalOrig'=>'',
			// '@noAprobacion' => '',
			// '@anoAprobacion' => '2015',
			// '@noCertificador' => $certificados[strtoupper($invoice->expediter_fcode)],

			'cfdi:Emisor'=>array(
				'@rfc' => $rfcEmisor,
				'@nombre' => $invoice->expediter_fname,
				'cfdi:DomicilioFiscal'=>array(
					'@calle' => limpiar($invoice->expediter_faddress_street),
					'@noExterior' => $invoice->expediter_faddress_num,
					'@noInterior' => limpiar($invoice->expediter_faddress_num2) == '' ? 'S/N' : limpiar($invoice->expediter_faddress_num2),
					'@colonia' => limpiar($invoice->expediter_faddress_urbanization),
					'@municipio' => limpiar($invoice->expediter_faddress_city),
					'@estado' => limpiar($invoice->expediter_faddress_state),
					'@pais' => limpiar($invoice->expediter_faddress_country),
					'@codigoPostal' => $invoice->expediter_faddress_zipcode
					),
				'cfdi:ExpedidoEn'=>array(
					'@calle' => limpiar($invoice->expediter_faddress_street),
					'@noExterior' => limpiar($invoice->expediter_faddress_num),
					'@noInterior' => limpiar($invoice->expediter_faddress_num2) == '' ? 'S/N' : limpiar($invoice->expediter_faddress_num2),
					'@colonia' => limpiar($invoice->expediter_faddress_urbanization),
					'@municipio' => limpiar($invoice->expediter_faddress_city),
					'@estado' => limpiar($invoice->expediter_faddress_state),
					'@pais' => limpiar($invoice->expediter_faddress_country),
					'@codigoPostal' => limpiar($invoice->expediter_faddress_zipcode)
					),
				'cfdi:RegimenFiscal'=>array(
					'@Regimen'=>$invoice->expediter_fregimen
					)
				),
				
			'cfdi:Receptor'=>array(
				'@rfc' => $invoice->customer_fcode,
				'@nombre' => $invoice->customer_fname,
				'cfdi:Domicilio' => array(
					'@calle' => limpiar($invoice->customer_address_street),
					'@noExterior' => limpiar($invoice->customer_address_num) == '' ? 'S/N' : limpiar($invoice->customer_address_num),
					'@colonia' => limpiar($invoice->customer_address_urbanization),
					'@municipio' => limpiar($invoice->customer_address_city),
					'@estado' => limpiar($invoice->customer_address_state),
					'@pais' => limpiar($invoice->customer_address_country),
					'@codigoPostal' => limpiar($invoice->customer_address_zipcode),
					'@noInterior' => limpiar($invoice->customer_address_num2) == '' ? 'S/N' : limpiar($invoice->customer_address_num2),
					'@localidad' => limpiar($invoice->customer_address_city)
					)
				)
			);
		$metodosPago = array(
			'Credit-Card'=>'TARJETA DE CREDITO',
			'Referenced Deposit'=>'DEPOSITO REFERENCIADO',
			'COD'=>'NO IDENTIFICADO',
			'Deposit'=>'NO IDENTIFICADO',
			'Wire Transfer'=>'DEPOSITO'
		);


		// Obtenemos Descuentos 
		$rs = $conn->query("SELECT SUM(discount) descuento FROM cu_invoices_lines where discount > 0 and id_invoices = '".$invoice->ID_invoices."'");
		$descuento = $rs->fetch()['descuento'];
		if($descuento > 0){
			$data['@descuento'] = $descuento;
		}

		if($invoice->payment_method != '')
			$data['@metodoDePago'] =$invoice->payment_method;//$metodosPago[$invoice->payment_method];
		else
			$data['@metodoDePago'] = 'NO IDENTIFICADO';

		if($invoice->doc_serial !='' and $invoice->doc_num !='0'){
			$data['@serie'] =$invoice->doc_serial;
			$data['@folio'] =$invoice->doc_num;
		}else{
			$serialNum = self::getInvoiceSerialNum($invoice->invoice_type);
			$data['@serie'] =$serialNum['doc_serial'];
			$data['@folio'] =$serialNum['doc_num'];
		}

		$conceptos = MysqlBD::consultarTablaF('cu_invoices_lines',array(),array('ID_invoices'=>$invoice->ID_invoices));
		$impuesto = 0;
		$conc = array();
		for ($i=0; $i < $conceptos->num(); $i++) {
			$concepto = $conceptos->get($i);
			$impuesto +=$concepto->tax;

			$table = ($concepto->ID_orders == '') ? 'sl_creditmemos' : 'sl_orders';
	        $id_trs = ($concepto->ID_orders == '') ? $concepto->ID_debitmemos : $concepto->ID_orders;
	        $id_product = $concepto->ID_sku;
	        $query = "SELECT 
	            sl_skus_trans.ID_products_trans,
	            cu_customs_info.import_declaration_number ,
	            cu_customs_info.import_declaration_date ,
	            cu_customs_info.customs ,
	            sl_vendors.CompanyName 
	        FROM 
	            sl_skus_trans 
	            INNER JOIN cu_customs_info ON sl_skus_trans.ID_customs_info=cu_customs_info.ID_customs_info 
	            LEFT JOIN sl_vendors ON sl_vendors.ID_vendors=cu_customs_info.ID_vendors 
	        WHERE  
	            sl_skus_trans.tbl_name='$table' and
	            sl_skus_trans.ID_trs=$id_trs and 
	            sl_skus_trans.ID_products=$id_product 
	        GROUP BY sl_skus_trans.ID_products, sl_skus_trans.ID_customs_info 
	        ORDER BY sl_skus_trans.ID_products_trans;";

			$res = $conn->query($query);
			$datosAduana = array();
			$all = $res->fetchAll(\PDO::FETCH_NUM);
			foreach ($all as $key => $row) {
				$datosAduana[] = array(
					'@fecha'=>limpiar($row[2]),
					'@aduana'=>limpiar($row[3]),
					'@numero'=>limpiar($row[1])
				);
			}
			if(count($datosAduana)>0){
				$conc[] = array(
					'@cantidad' => $concepto->quantity,
					'@unidad'=>$concepto->measuring_unit,
					'@noIdentificacion'=>$concepto->UPC,
					'@descripcion' =>  limpiar($concepto->ID_sku.'-'.$concepto->description),
					'@valorUnitario' => number_format($concepto->unit_price,2,'.',''),
					'@importe'=>number_format($concepto->amount,2,'.',''),
					'cfdi:InformacionAduanera'=>$datosAduana
				);
			}else{
				$v = array(
					'@cantidad' => $concepto->quantity,
					'@unidad'=>$concepto->measuring_unit,
					'@noIdentificacion'=>'0',
					'@descripcion' =>  limpiar($concepto->ID_sku.'-'.$concepto->description),
					'@valorUnitario' => number_format($concepto->unit_price,2,'.',''),
					'@importe'=>number_format($concepto->amount,2,'.','')
				);
				if($concepto->UPC != ''){
					$v['@noIdentificacion']=$concepto->UPC;
				}
				$conc[] = $v;
			}
		}

		$data['cfdi:Conceptos']['cfdi:Concepto'] =$conc;
		$data['cfdi:Impuestos'] = array(
			'@totalImpuestosTrasladados'=>number_format($impuesto,2,'.',''),
			'cfdi:Traslados'=>array(
				'cfdi:Traslado' =>array(
					'@impuesto'=>'IVA',
					'@tasa'=>'16.00',
					'@importe'=>number_format($impuesto,2,'.','')
					)
				)
			);
		return $data;
	}
	protected static function getInvoiceSerialNum($Tipo) {
	    $doc_serial = "";
	    $doc_num = 0;
		$conn = MysqlBD::getConexion();
	    if($Tipo=='ingreso'){
	    	$query = "SELECT VName, VValue FROM sl_vars WHERE VName = 'invoices_doc_serial'";
	    	$r = $conn->query($query);
	    	$r = $r->fetch();
	    	$doc_serial = $r['VValue'];
	    	$query = "SELECT VName, VValue FROM sl_vars WHERE VName = 'invoices_doc_num'";
	    	$r = $conn->query($query);
	    	$r = $r->fetch();
	    	$doc_num = $r['VValue'];
	        //--- actualiza el dato del folio para generar el consecutivo
	        $next_num = intval($doc_num) + 1;
	        $query = "UPDATE sl_vars SET VValue='$next_num' WHERE VName = 'invoices_doc_num'";
	        $conn->query($query);
	    }elseif($Tipo=='egreso'){
	        //-- Obtiene el numero de serie para la factura
	        $query = "SELECT VName, VValue FROM sl_vars WHERE VName = 'creditnote_doc_serial'";
	    	$r = $conn->query($query);
	    	$r = $r->fetch();
	    	$doc_serial = $r['VValue'];
	    	$query = "SELECT VName, VValue FROM sl_vars WHERE VName = 'creditnote_doc_num'";
	    	$r = $conn->query($query);
	    	$r = $r->fetch();
	    	$doc_num = $r['VValue'];
	        //--- actualiza el dato del folio para generar el consecutivo
	        $next_num = intval($doc_num) + 1;
	        $query = "UPDATE sl_vars SET VValue='$next_num' WHERE VName = 'creditnote_doc_num'";
	        $conn->query($query);
	    }
        MysqlBD::executeQuery('Update cu_invoices set doc_serial=\''.$doc_serial.'\', doc_num='.$doc_num.' where id_invoices='.self::$id_invoices);
	    $arr_doc_serial = array(
	        'doc_serial' => $doc_serial,
	        'doc_num' => $doc_num,
	    );
	    return $arr_doc_serial;
	}
}