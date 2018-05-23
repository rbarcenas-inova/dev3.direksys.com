<?php
namespace FacturasCFDI\Addendas;
use EnLetras;
use MysqlBD;
class ECE9610253TA{
	public static function getAddendaStruct($data){
		$letras = new EnLetras();
		$tipoAddenda = $data->invoice_type == 'ingreso' ? 'if:FacturaInterfactura' : 'if:NotaCreditoInterfactura';
		$tipo = $data->invoice_type == 'ingreso' ? 'Factura' : 'NotaCredito';
		$structuraAddenda = null;
		$cuerpo = array();
		$conceptos = MysqlBD::consultarTablaF(
			'cu_invoices_lines',
			array(),
			array('ID_invoices'=>$data->ID_invoices)
		);
		$lineas = array();
		$total = 0;
		for ($i=0; $i < $conceptos->num(); $i++) { 
			$concepto = $conceptos->get($i);
			$total+=number_format($concepto->amount,2);
			$cuerpo[] = array(
				"@Renglon" => $i+1,
                "@Concepto" => limpiar($concepto->ID_sku_alias.'-'.$concepto->description),
                "@Cantidad" => number_format($concepto->quantity,2),
                "@PUnitario"=>number_format($concepto->amount,2),
                "@Importe"=>number_format($concepto->amount*$concepto->quantity,2)
			);
					
		}
		if($tipo == 'Factura'){
			$structuraAddenda = array(
				"cfdi:Addenda"=>array(
		            'if:FacturaInterfactura'=>array(
		                "@schemaLocation"=>"https://www.interfactura.com/Schemas/Documentos https://www.interfactura.com/Schemas/Documentos/DocumentoInterfactura.xsd",
		                "@TipoDocumento"=>'Factura',
		                "@xmlns:if"=>"https://www.interfactura.com/Schemas/Documentos",
		                "if:Emisor"=>array(
		                    "@RI"=>"0142108"
		                ),
		                "if:Receptor"=>array(
		                    "@RI"=>"00009"
		                ),
		                "if:Encabezado"=>array(
		                    "@TipoProveedorEKT"=>"1",
		                    "@Fecha"=>join('T',explode(' ',$data->doc_date)),
		                    "@MonedaDoc"=>"MXN",
		                    "@IVAPCT"=>"16",
		                    "@Iva"=>number_format($data->total_taxes->transfered,2),
		                    "@SubTotal"=>number_format($data->invoice_net,2),
		                    "@Total"=>number_format($data->invoice_total,2),
		                    "@NumProveedor"=>"701378",
		                    "@FolioOrdenCompra"=>"614979",
		                    "@PorcentajeDescuentoPromo"=>"0.00",
		                    "@PorcentajeMerma"=>"0",
		                    "@TotalDescuento"=>"0",
		                    "@TotalMerma"=>"0",
		                    "@Descuento"=>"0.00",
		                    "if:Cuerpo"=>$cuerpo
		                )
		            )
		        )
			);
		}else{
	 		$structuraAddenda = ["cfdi:Addenda"=>array(
	            "if:NotaCreditoInterfactura"=>array(
	                "@schemaLocation"=>"https://www.interfactura.com/Schemas/Documentos ",
	                "@TipoDocumento"=>"NotaCredito",
	                "@xmlns:if"=>"https://www.interfactura.com/Schemas/Documentos",
	                "if:Emisor"=>array(
	                    "@NumProveedor"=>" 701378",
	                    "@RI"=>"0142108"
	                	),
	                "if:Receptor"=>array(
	                    "@RI"=>"00009"
	                	),
	                "if:Encabezado"=>array(
	                    "@NumProveedor"=>" 701378",
	                    "@Fecha"=>join('T',explode(' ',$data->doc_date)),
	                    "@MonedaDoc"=>"MXN",
	                    "@IVAPCT"=>"16",
	                    "@Iva"=>number_format($data->total_taxes->transfered,2),
	                    "@SubTotal"=>number_format($data->invoice_net,2),
	                    "@Total"=>number_format($data->invoice_total,2),
	                    "@PorcentajeDescuento"=>"NaN",
	                    "@PorcentajeDescuentoPromo"=>"0.00",
	                    "@PorcentajeMerma"=>"0",
	                    "@TotalDescuento"=>"0",
	                    "@TotalMerma"=>"0",
	                    "@Descuento"=>"0.00",
	                    "if:Cuerpo"=>$cuerpo
	                	)
	            	)
	        	)
	 		];
		}
		
		return $structuraAddenda;
	}
}
// }


