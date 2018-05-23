<?php
namespace FacturasCFDI\Addendas;
class Soriana{
    public static function getAddendaStruct($data) {
        $structuraAddenda = array(
        	"cfdi:Addenda"=>array(
	            "DSCargaRemisionProv"=>array(
	                "@xmlns"=> "http://tempuri.org/DSCargaRemisionProv.xsd",
	                "Remision"=>array(
	                    "Proveedor"=> "8356",
	                    "Remision"=> "442",
	                    "Consecutivo"=> "0",
	                    "FechaRemision"=> "2015-11-02T00:00:00",
	                    "Tienda"=> "5542",
	                    "TipoMoneda"=> "1",
	                    "TipoBulto"=> "1",
	                    "EntregaMercancia"=> "41",
	                    "CumpleReqFiscales"=> "true",
	                    "CantidadBultos"=> "60.000000",
	                    "Subtotal"=> "95389.200000",
	                    "Descuentos"=> "0.000000",
	                    "IEPS"=> "0.000000",
	                    "IVA"=> "15262.270000",
	                    "OtrosImpuestos"=> "0.000000",
	                    "Total"=> "110651.470000",
	                    "CantidadPedidos"=> "1",
	                    "FechaEntregaMercancia"=> "2015-11-04T00:00:00"
	                ),
	                "Pedidos"=>array(
	                    "Proveedor"=> "8356",
	                    "Remision"=> "442",
	                    "FolioPedido"=> "28679441",
	                    "Tienda"=> "5542",
	                    "CantidadArticulos"=> "1"
	                ),
	                "Articulos"=>array(
	                    "Proveedor"=> "8356",
	                    "Remision"=> "442",
	                    "FolioPedido"=> "28679441",
	                    "Tienda"=> "5542",
	                    "Codigo"=> "854258000011",
	                    "CantidadUnidadCompra"=> "60.000000",
	                    "CostoNetoUnidadCompra"=> "1589.820000",
	                    "PorcentajeIEPS"=> "0.000000",
	                    "PorcentajeIVA"=> "16.000000"
	                )
	            )
        	)
        )

        return $structuraAddenda;
    }
}
