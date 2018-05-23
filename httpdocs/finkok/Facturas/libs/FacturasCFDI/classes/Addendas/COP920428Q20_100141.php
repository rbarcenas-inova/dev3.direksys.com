<?php
namespace FacturasCFDI\Addendas;
use MysqlBD;
class COP920428Q20_100141{
	public static function getAddendaStruct($invoice, $facturaObj = null){
		// self::$id_invoices = $invoice->ID_invoices;
		$conn = MysqlBD::getConexion();
		$cadenaOriginal = $facturaObj->genCadenaOriginal();
		global $cfg;
		$rfcEmisor = $invoice->expediter_fcode;
		if(isset($cfg['finkok_test_mode']) && $cfg['finkok_test_mode'] == 1){
			$rfcEmisor = getRFC();
		}
		$query = "SELECT
			cu_invoices_lines.ID_sku
			, cu_invoices_lines.ID_orders
			, cu_invoices_lines.ID_debitmemos
			, DATE_FORMAT(cu_invoices.doc_date,'%Y%m%d') AS 'requestForPayment->DeliveryDate'
			, CASE 
				WHEN cu_invoices.invoice_type='ingreso' THEN 'INVOICE'
				WHEN cu_invoices.invoice_type='egreso' THEN 'CREDIT_NOTE'
				ELSE ''
			END AS 'requestForPayment->requestForPaymentIdentification->entityType'
			, CONCAT(cu_invoices.doc_serial,cu_invoices.doc_num) AS 'requestForPayment->requestForPaymentIdentification->uniqueCreatorIdentification'

			, cu_invoices.ID_orders_alias AS 'requestForPayment->orderIdentification->referenceIdentification'
			, cu_invoices.ID_orders_alias_date AS 'requestForPayment->orderIdentification->ReferenceDate'
			, ADDDATE(cu_invoices.ID_orders_alias_date, INTERVAL 7 DAY) AS 'requestForPayment->orderIdentification->FechaPromesaEnt' # Ernesto Velazco me comento que 7 dias despues de generar el pedido
			, sl_customers.PersonalID AS 'requestForPayment->seller->gln'
			, 'SELLER_ASSIGNED_IDENTIFIER_FOR_A_PARTY' AS 'requestForPayment->seller->alternatePartyIdentification->type'
			, sl_customers.PersonalID AS 'requestForPayment->seller->alternatePartyIdentification'
			, 1 AS 'requestForPayment->seller->IndentificaTipoProv'

			, cu_invoices.customer_shpaddress_alias AS 'requestForPayment->shipTo->nameAndAddress->name'
			, cu_invoices.customer_shpaddress_street AS 'requestForPayment->shipTo->nameAndAddress->streetAddressOne'
			, cu_invoices.customer_shpaddress_city AS 'requestForPayment->shipTo->nameAndAddress->city'
			, cu_invoices.customer_shpaddress_zipcode AS 'requestForPayment->shipTo->nameAndAddress->postalCode'
			, cu_invoices.customer_shpaddress_code AS 'requestForPayment->shipTo->nameAndAddress->BodegaDestino'
			, cu_invoices.customer_shpaddress_code AS 'requestForPayment->shipTo->nameAndAddress->BodegaReceptora'

			, CASE 
				WHEN cu_invoices.currency='MX$' THEN 'MXN'
				WHEN cu_invoices.currency='MXP' THEN 'MXN'
				WHEN cu_invoices.currency='USD' THEN 'USD'
				ELSE 'MXN'
			END AS 'requestForPayment->currency->currencyISOCode'
			, 'PAYMENT_CURRENCY' AS 'requestForPayment->currencyFunction'

			, 'SELLER_PROVIDED' AS 'requestForPayment->FleteCaja->type'
			, cu_invoices.expediter_fname AS 'requestForPayment->FleteCaja' # Esto no cuadra
			, 'BILL_BACK' AS 'requestForPayment->allowanceCharge->settlementType'
			, 'ALLOWANCE_GLOBAL' AS 'requestForPayment->allowanceCharge->allowanceChargeType'
			, 'AJ' AS 'requestForPayment->allowanceCharge->specialServicesType'
			, 'INVOICE_VALUE' AS 'requestForPayment->monetaryAmountOrPercentage->rate->base'
			, 0.00 AS 'requestForPayment->monetaryAmountOrPercentage->rate->percentage'

			, 'SimpleInvoiceLineItemType' AS 'requestForPayment->lineItem->type'

			-- , cu_invoices_lines.UPC AS 'requestForPayment->lineItem->tradeItemIdentification->gtin'
			, cu_invoices_lines.ID_sku_alias AS 'requestForPayment->lineItem->tradeItemIdentification->gtin'

			, cu_invoices_lines.ID_sku_alias AS 'requestForPayment->lineItem->alternateTradeItemIdentification'
			, 'BUYER_ASSIGNED' AS 'requestForPayment->lineItem->alternateTradeItemIdentification->type'

			, cu_invoices_lines.ID_sku_alias AS 'requestForPayment->lineItem->codigoTallaInternoCorp->codigo'
			, 0 AS 'requestForPayment->lineItem->codigoTallaInternoCorp->talla'

			, 'ES' AS 'requestForPayment->lineItem->tradeItemDescriptionInformation->language'
			, CONCAT(cu_invoices_lines.ID_sku_alias,'-',cu_invoices_lines.description) AS 'requestForPayment->lineItem->tradeItemDescriptionInformation->language->longText'

			, cu_invoices_lines.quantity AS 'requestForPayment->lineItem->invoicedQuantity'
			, 'PCE' AS 'requestForPayment->lineItem->invoicedQuantity->unitOfMeasure'

			, cu_invoices_lines.unit_price AS 'requestForPayment->lineItem->grossPrice->Amount'

			, cu_invoices_lines.unit_price AS 'requestForPayment->lineItem->netPrice->Amount'

			, 'Modelo del articulo' AS 'requestForPayment->lineItem->modeloInformation->longText'

			, '?' AS 'requestForPayment->lineItem->palletInformation->palletQuantity'
			, 'BOX' AS 'requestForPayment->lineItem->palletInformation->description->type'
			, 'PREPAID_BY_SELLER' AS 'requestForPayment->lineItem->palletInformation->transport->methodOfPayment'
			, '?' AS 'requestForPayment->lineItem->palletInformation->prepactCant'

			, 'ALLOWANCE_GLOBAL' AS 'requestForPayment->lineItem->allowanceCharge->allowanceChargeType'
			, 0.00 AS 'requestForPayment->lineItem->allowanceCharge->monetaryAmountOrPercentage->percentagePerUnit'
			, 0.00 AS 'requestForPayment->lineItem->allowanceCharge->monetaryAmountOrPercentage->ratePerUnit'

			, 'VAT' AS 'requestForPayment->lineItem->tradeItemTaxInformation->taxTypeDescription'
			, (cu_invoices_lines.tax_rate*100) AS 'requestForPayment->lineItem->tradeItemTaxInformation->tradeItemTaxAmount->taxPercentage'
			, ROUND(cu_invoices_lines.tax,2) AS 'requestForPayment->lineItem->tradeItemTaxInformation->tradeItemTaxAmount->taxAmount'

			, cu_invoices_lines.amount AS 'requestForPayment->lineItem->totalLineAmount->grossAmount'
			, cu_invoices_lines.amount AS 'requestForPayment->lineItem->totalLineAmount->netAmount'

			, cu_invoices.invoice_net AS 'requestForPayment->totalAmount->Amount'

			, 'ALLOWANCE' AS 'requestForPayment->TotalAllowanceCharge->allowanceOrChargeType'
			, 0.00 AS 'requestForPayment->TotalAllowanceCharge->Amount'

			, cu_invoices.invoice_net AS 'requestForPayment->baseAmount->Amount'

			, 'VAT' AS 'requestForPayment->tax->type'
			, 16.00 AS 'requestForPayment->tax->taxPercentage'
			, cu_invoices.total_taxes_transfered AS 'requestForPayment->tax->taxAmount'
			, 'TRANSFERIDO' AS 'requestForPayment->tax->taxCategory' # TRANSFERIDO
			, cu_invoices_lines.Tax AS 'ItemTax'
			, cu_invoices.invoice_total AS 'requestForPayment->payableAmount->Amount'

			, '?' AS 'requestForPayment->cadenaOriginal->Cadena'
			-- *****************************************************************************************************
			from cu_invoices
			inner join cu_invoices_lines ON cu_invoices_lines.ID_invoices=cu_invoices.ID_invoices
			inner join sl_customers on sl_customers.ID_customers=cu_invoices.ID_customers
			where 1
				AND cu_invoices.customer_fcode='COP920428Q20'
				AND cu_invoices.ID_invoices = $invoice->ID_invoices;";
			//order by cu_invoices.ID_invoices desc, cu_invoices_lines.ID_invoices_lines;";
		$rs = $conn->query($query);
		// while($rs->fetch(\PDO::FETCH_OBJ)){

		// }
		$items = $conn->query($query);
		$itemsArry = array();
		$aux = 1;
		$impuesto = 0;
		while($item = $items->fetch(\PDO::FETCH_OBJ)){
			// Inf Aduanera
			$table = ($item->ID_orders == '') ? 'sl_creditmemos' : 'sl_orders';
			$impuesto += number_format($item->ItemTax,2,'.','');
			$id_trs = ($item->ID_orders == '') ? $item->ID_debitmemos : $item->ID_orders;
			$id_product = $item->ID_sku;
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
	        $conn = MysqlBD::getConexion();
			$res = $conn->query($query);
			// print_r($res->fetch(\PDO::FETCH_OBJ));
			$aduanas = '';
			while($row = $res->fetch(\PDO::FETCH_OBJ)){
				$aduanas = $row->customs;
			}
			// exit;
			$itemsArry[] = array(
				'@type' => $item->{'requestForPayment->lineItem->type'},
				'@number' => $aux,
				'tradeItemIdentification' => array(
					'gtin' => $item->{'requestForPayment->lineItem->tradeItemIdentification->gtin'},
				) ,
				'alternateTradeItemIdentification' => array(
					'@type' => $item->{'requestForPayment->lineItem->alternateTradeItemIdentification->type'},
					'#text' => $item->{'requestForPayment->lineItem->codigoTallaInternoCorp->codigo'}
				) ,
				'codigoTallaInternoCorp' => array(
					'codigo' => $item->{'requestForPayment->lineItem->codigoTallaInternoCorp->codigo'},
					'talla' => '0'//$item->{'requestForPayment->lineItem->codigoTallaInternoCorp->codigo'}
				) ,
				'tradeItemDescriptionInformation' => array(
					'@language' => $item->{'requestForPayment->lineItem->tradeItemDescriptionInformation->language'},
					'longText' => $item->{'requestForPayment->lineItem->tradeItemDescriptionInformation->language->longText'},
				) ,
				'invoicedQuantity' => array(
					'@unitOfMeasure' => $item->{'requestForPayment->lineItem->invoicedQuantity->unitOfMeasure'},
					'#text' => $item->{'requestForPayment->lineItem->invoicedQuantity'},
				) ,
				'grossPrice' => array(
					'Amount' => $item->{'requestForPayment->lineItem->grossPrice->Amount'},
				) ,
				'netPrice' => array(
					'Amount' => $item->{'requestForPayment->lineItem->netPrice->Amount'},
				) ,
				'modeloInformation' => array(
					'longText' => $item->{'requestForPayment->lineItem->modeloInformation->longText'},
				) ,
				'palletInformation' => array(
					'palletQuantity' => $aduanas,
					'description' => array(
						'@type' => $item->{'requestForPayment->lineItem->palletInformation->description->type'},
					) ,
					'transport' => array(
						'methodOfPayment' => $item->{'requestForPayment->lineItem->palletInformation->transport->methodOfPayment'},
					) ,
					// 'prepactCant' => '0',
				) ,
				'allowanceCharge' => array(
					'@allowanceChargeType' => $item->{'requestForPayment->lineItem->allowanceCharge->allowanceChargeType'},
					'specialServicesType' => '',
					'monetaryAmountOrPercentage' => array(
						'percentagePerUnit' => $item->{'requestForPayment->lineItem->allowanceCharge->monetaryAmountOrPercentage->percentagePerUnit'},
						'ratePerUnit' => array(
							'amountPerUnit' => $item->{'requestForPayment->lineItem->allowanceCharge->monetaryAmountOrPercentage->ratePerUnit'},
						) ,
					) ,
				) ,
				'tradeItemTaxInformation' => array(
					'taxTypeDescription' => $item->{'requestForPayment->lineItem->tradeItemTaxInformation->taxTypeDescription'},
					'tradeItemTaxAmount' => array(
						'taxPercentage' => $item->{'requestForPayment->lineItem->tradeItemTaxInformation->tradeItemTaxAmount->taxPercentage'},
						'taxAmount' => $item->{'requestForPayment->lineItem->tradeItemTaxInformation->tradeItemTaxAmount->taxAmount'},
					) ,
				) ,
				'totalLineAmount' => array(
					'grossAmount' => array(
						'Amount' => $item->{'requestForPayment->lineItem->totalLineAmount->grossAmount'},
					) ,
					'netAmount' => array(
						'Amount' => $item->{'requestForPayment->lineItem->totalLineAmount->netAmount'},
					) ,
				) ,
			);
			$aux++;
		}

		$row = $rs->fetch(\PDO::FETCH_OBJ);
		$structuraAddenda = array(
			'cfdi:Addenda' => array(
				'requestForPayment' => array(
					'@type' => 'SimpleInvoiceType',
					'@contentVersion' => '1.0',
					'@documentStructureVersion' => 'CPLM1.0',
					'@documentStatus' => 'ORIGINAL',
					'@DeliveryDate' => $row->{'requestForPayment->DeliveryDate'},
					'requestForPaymentIdentification' => array(
						'entityType' => $row->{'requestForPayment->requestForPaymentIdentification->entityType'},
						'uniqueCreatorIdentification' => $row->{'requestForPayment->requestForPaymentIdentification->uniqueCreatorIdentification'},
						) ,
					'orderIdentification' => array(
						'referenceIdentification' => array(
							'@type' => 'ON',
							'#text' => $row->{'requestForPayment->orderIdentification->referenceIdentification'},
							) ,
						'ReferenceDate' => $row->{'requestForPayment->orderIdentification->ReferenceDate'},
						'FechaPromesaEnt' => $row->{'requestForPayment->orderIdentification->FechaPromesaEnt'},
						) ,
					'seller' => array(
						'gln' => $row->{'requestForPayment->seller->gln'},
						'alternatePartyIdentification' => array(
							'@type' => 'SELLER_ASSIGNED_IDENTIFIER_FOR_A_PARTY',
							'#text' => $row->{'requestForPayment->seller->alternatePartyIdentification'},
							) ,
						'IndentificaTipoProv' => '1',
						) ,
					'shipTo' => array(
						'nameAndAddress' => array(
							'name' => $row->{'requestForPayment->shipTo->nameAndAddress->name'},
							'streetAddressOne' => $row->{'requestForPayment->shipTo->nameAndAddress->streetAddressOne'},
							'city' => $row->{'requestForPayment->shipTo->nameAndAddress->city'},
							'postalCode' => $row->{'requestForPayment->shipTo->nameAndAddress->postalCode'},
							'BodegaDestino' => $row->{'requestForPayment->shipTo->nameAndAddress->BodegaDestino'},
							'BodegaReceptora' => $row->{'requestForPayment->shipTo->nameAndAddress->BodegaReceptora'},
							) ,
						) ,
					'currency' => array(
						'@currencyISOCode' => $row->{'requestForPayment->currency->currencyISOCode'},
						'currencyFunction' => $row->{'requestForPayment->currencyFunction'},
						) ,
					'FleteCaja' => array(
						'@type' => $row->{'requestForPayment->FleteCaja->type'},
						'#text' => $row->{'requestForPayment->FleteCaja'},
						) ,
					'allowanceCharge' => array(
						'@settlementType' => $row->{'requestForPayment->allowanceCharge->settlementType'},
						'@allowanceChargeType' => $row->{'requestForPayment->allowanceCharge->allowanceChargeType'},
						'specialServicesType' => $row->{'requestForPayment->allowanceCharge->specialServicesType'},
						'monetaryAmountOrPercentage' => array(
							'rate' => array(
								'@base' => $row->{'requestForPayment->monetaryAmountOrPercentage->rate->base'},
								'percentage' => $row->{'requestForPayment->monetaryAmountOrPercentage->rate->percentage'},
								) ,
							) ,
						) ,
					'lineItem' => $itemsArry,
					'totalAmount' => array(
						'Amount' => $row->{'requestForPayment->totalAmount->Amount'},
					) ,
					'TotalAllowanceCharge' => array(
						'@allowanceOrChargeType' => $row->{'requestForPayment->TotalAllowanceCharge->allowanceOrChargeType'},
						'specialServicesType' => '',
						'Amount' => $row->{'requestForPayment->TotalAllowanceCharge->Amount'},
					) ,
					'baseAmount' => array(
						'Amount' => $row->{'requestForPayment->baseAmount->Amount'},
					) ,
					'tax' => array(
						'@type' => $row->{'requestForPayment->tax->type'},
						'taxPercentage' => $row->{'requestForPayment->tax->taxPercentage'},
						'taxAmount' => $impuesto,
						'taxCategory' => $row->{'requestForPayment->tax->taxCategory'},
					) ,
					'payableAmount' => array(
						'Amount' => $row->{'requestForPayment->payableAmount->Amount'},
					) ,
					'cadenaOriginal' => array(
						'Cadena' => $cadenaOriginal,
					) ,
				) ,
			) ,
		);
		return $structuraAddenda;
	}
}