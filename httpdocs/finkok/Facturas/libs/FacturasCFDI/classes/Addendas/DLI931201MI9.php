<?php
namespace FacturasCFDI\Addendas;
use EnLetras;
use MysqlBD;
class DLI931201MI9{
	public static function getAddendaStruct($data){
		$letras = new EnLetras();
		if($data->invoice_type == 'egreso'){
			return [];
		}
		$structuraAddenda = array(
			'cfdi:Complemento' => array(
				"detallista:detallista"=>array(
		            "@type"=> "SimpleInvoiceType",
		            "@contentVersion"=> "1.3.1",
		            "@documentStructureVersion"=> "AMC8.1",
		            "@documentStatus"=> "ORIGINAL",
		            'detallista:requestForPaymentIdentification'=>array(
		            	'detallista:entityType'=>$data->invoice_type == 'ingreso' ? 'INVOICE' : 'CREDIT_NOTE'
		            ),
		            'detallista:specialInstruction'=>array(
		            	'@code'=>'ZZZ',
		            	'detallista:text'=>$letras->ValorEnLetras($data->invoice_total)
		            ),
		            "detallista:orderIdentification"=> array(
	                    "detallista:referenceIdentification"=> array(
	                        "@type"=> "ON",
	                        "#text"=> $data->ID_orders_alias
	                    ),
	                    "detallista:ReferenceDate"=> $data->ID_orders_alias_date
	                ),
		            "detallista:AdditionalInformation"=> array(
		                "detallista:referenceIdentification"=> array(
		                    "@type"=> "ATZ",
		                    "#text"=> "12345"
		                )
		            ),
					"detallista:DeliveryNote"=>array(
		                "detallista:referenceIdentification"=> $data->exchange_receipt,
		                "detallista:ReferenceDate"=> $data->exchange_receipt_date
		            ),
		            "detallista:buyer"=>array(
		                "detallista:gln"=> $data->customer_address_gln,
		                "detallista:contactInformation"=>array(
		                    "detallista:personOrDepartmentName"=>array(
		                        "detallista:text"=> $data->customer_shpaddress_contact
		                    )
		                )
		            ),
		            "detallista:seller"=>array(
		                "detallista:gln"=> $data->customer_shpaddress_gln,
		                "detallista:alternatePartyIdentification"=>array(
		                    "@type"=> "SELLER_ASSIGNED_IDENTIFIER_FOR_A_PARTY",
		                    "#text"=> $data->VendorID
		                )
		            ),
		            "detallista:currency"=>array(
		                "@currencyISOCode"=> "MXN",
		                "detallista:currencyFunction"=> "BILLING_CURRENCY",
		                "detallista:rateOfChange"=> $data->currency_exchange
		            ),
		            "detallista:allowanceCharge"=>array(
		                "@allowanceChargeType"=> "ALLOWANCE_GLOBAL",
		                "@settlementType"=> "OFF_INVOICE",
		                "detallista:specialServicesType"=> "AJ",
		                "detallista:monetaryAmountOrPercentage"=>array(
		                    "detallista:rate"=>array(
		                        "@base"=> "INVOICE_VALUE",
		                        "detallista:percentage"=> "0.00"
		                    )
		                )
		            )
				)
			)
		);
		$conceptos = MysqlBD::consultarTablaF(
			'cu_invoices_lines',
			array(),
			array('ID_invoices'=>$data->ID_invoices)
		);
		$lineas = array();
		$total = 0;
		for ($i=0; $i < $conceptos->num(); $i++) { 
			$concepto = $conceptos->get($i);
			$total+=$concepto->amount;
			$lineas[] = array(
				"@number"=> $i+1,
	            "@type"=> "SimpleInvoiceLineItemType",
				"detallista:tradeItemIdentification"=>array(
	                "detallista:gtin"=> $concepto->UPC
	            ),
	            "detallista:alternateTradeItemIdentification"=>array(
	                "@type"=> "BUYER_ASSIGNED",
	                "#text"=> $concepto->UPC
	            ),
	            "detallista:tradeItemDescriptionInformation"=>array(
	                "@language"=> "ES",
	                "detallista:longText"=> limpiar($concepto->ID_sku_alias.'-'.$concepto->description)
	            ),
	            "detallista:invoicedQuantity"=>array(
	                "@unitOfMeasure"=> $concepto->measuring_unit,
	                "#text"=> $concepto->quantity
	            ),
	            "detallista:grossPrice"=>array(
	                "detallista:Amount"=> number_format( ($concepto->amount/ $concepto->quantity) ,2, '.', '')
	            ),
	            "detallista:netPrice"=>array(
	                "detallista:Amount"=> number_format( ($concepto->amount/ $concepto->quantity),2, '.', '')
	            ),
	            "detallista:tradeItemTaxInformation"=>array(
	                "detallista:taxTypeDescription"=> "VAT",
	                "detallista:tradeItemTaxAmount"=>array(
	                    "detallista:taxPercentage"=> number_format(($concepto->tax_rate * 100),2, '.', ''),
	                    "detallista:taxAmount"=> number_format($concepto->tax,2, '.', '')
	                )
	            ),
	            "detallista:totalLineAmount"=>array(
	                "detallista:grossAmount"=>array(
	                    "detallista:Amount"=> number_format($concepto->amount,2, '.', '')
	                ),
	                "detallista:netAmount"=>array(
	                    "detallista:Amount"=> number_format($concepto->amount,2, '.', '')
	                )
	            )
			);
		
		}
		$structuraAddenda['cfdi:Complemento']['detallista:detallista']["detallista:lineItem"] = $lineas; 
		$structuraAddenda['cfdi:Complemento']['detallista:detallista']['detallista:totalAmount'] = array(
			'detallista:Amount'=>number_format($total,2, '.', '')
		);
		$structuraAddenda['cfdi:Complemento']['detallista:detallista']['detallista:TotalAllowanceCharge']= array(
		        "@allowanceOrChargeType"=> "ALLOWANCE",
		        "detallista:specialServicesType"=> "AJ",
		        "detallista:Amount"=> "0.00"
		);
		// show($structuraAddenda);
		return $structuraAddenda;
	}
}
// }


