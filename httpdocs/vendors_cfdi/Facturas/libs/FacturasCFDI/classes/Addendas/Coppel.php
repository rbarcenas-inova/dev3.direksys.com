<?php
namespace FacturasCFDI\Addendas;
class Coppel{
	public static function getAddendaStruct($data){
		
$structuraAddenda = array(
	'cfdi:Addenda' => array(
		'requestForPayment' => array(
			'@type' => 'SimpleInvoiceType',
			'@contentVersion' => '1.0',
			'@documentStructureVersion' => 'CPLM1.0',
			'@documentStatus' => 'ORIGINAL',
			'@DeliveryDate' => '20150423',
			'requestForPaymentIdentification' => array(
				'entityType' => 'INVOICE',
				'uniqueCreatorIdentification' => 'IFA8618',
				) ,
			'orderIdentification' => array(
				'referenceIdentification' => array(
					'@type' => 'ON',
					'#text' => '267996',
					) ,
				'ReferenceDate' => '2015-04-20',
				'FechaPromesaEnt' => '2015-04-23',
				) ,
			'seller' => array(
				'gln' => '77178',
				'alternatePartyIdentification' => array(
					'@type' => 'SELLER_ASSIGNED_IDENTIFIER_FOR_A_PARTY',
					'#text' => '77178',
					) ,
				'IndentificaTipoProv' => '1',
				) ,
			'shipTo' => array(
				'nameAndAddress' => array(
					'name' => 'PUEBLA',
					'streetAddressOne' => 'Av. 18 de Noviembre',
					'city' => 'BODEGA PUEBLA',
					'postalCode' => '72320',
					'BodegaDestino' => '30009',
					'BodegaReceptora' => '30009',
					) ,
				) ,
			'currency' => array(
				'@currencyISOCode' => 'MXN',
				'currencyFunction' => 'PAYMENT_CURRENCY',
				) ,
			'FleteCaja' => array(
				'@type' => 'SELLER_PROVIDED',
				'#text' => 'IMPORTACIONES DE MEXICO Y LATINOAMERICA S DE RL DE CV',
				) ,
			'allowanceCharge' => array(
				'@settlementType' => 'BILL_BACK',
				'@allowanceChargeType' => 'ALLOWANCE_GLOBAL',
				'specialServicesType' => 'AJ',
				'monetaryAmountOrPercentage' => array(
					'rate' => array(
						'@base' => 'INVOICE_VALUE',
						'percentage' => '0.00',
						) ,
					) ,
				) ,
			'lineItem' => array(
				0 => array(
					'@type' => 'SimpleInvoiceLineItemType',
					'@number' => '1',
					'tradeItemIdentification' => array(
						'gtin' => '910831',
						) ,
					'alternateTradeItemIdentification' => array(
						'@type' => 'BUYER_ASSIGNED',
						'#text' => '910831',
						) ,
					'codigoTallaInternoCorp' => array(
						'codigo' => '910831',
						'talla' => '0',
						) ,
					'tradeItemDescriptionInformation' => array(
						'@language' => 'ES',
						'longText' => '910831-EAGLE EYES CELEBRITY ORANGE',
						) ,
					'invoicedQuantity' => array(
						'@unitOfMeasure' => 'PCE',
						'#text' => '4.00',
						) ,
					'grossPrice' => array(
						'Amount' => '559.91',
						) ,
					'netPrice' => array(
						'Amount' => '559.91',
						) ,
					'modeloInformation' => array(
						'longText' => 'Modelo del articulo',
						) ,
					'palletInformation' => array(
						'palletQuantity' => NULL,
						'description' => array(
							'@type' => 'BOX',
							) ,
						'transport' => array(
							'methodOfPayment' => 'PREPAID_BY_SELLER',
							) ,
						'prepactCant' => '0',
						) ,
					'allowanceCharge' => array(
						'@allowanceChargeType' => 'ALLOWANCE_GLOBAL',
						'specialServicesType' => NULL,
						'monetaryAmountOrPercentage' => array(
							'percentagePerUnit' => '0.00',
							'ratePerUnit' => array(
								'amountPerUnit' => '0.00',
								) ,
							) ,
						) ,
					'tradeItemTaxInformation' => array(
						'taxTypeDescription' => 'VAT',
						'tradeItemTaxAmount' => array(
							'taxPercentage' => '16.00',
							'taxAmount' => '358.34',
							) ,
						) ,
					'totalLineAmount' => array(
						'grossAmount' => array(
							'Amount' => '2239.64',
							) ,
						'netAmount' => array(
							'Amount' => '2239.64',
							) ,
						) ,
					) ,
1 => array(
	'@type' => 'SimpleInvoiceLineItemType',
	'@number' => '2',
	'tradeItemIdentification' => array(
		'gtin' => '920053',
		) ,
	'alternateTradeItemIdentification' => array(
		'@type' => 'BUYER_ASSIGNED',
		'#text' => '920053',
		) ,
	'codigoTallaInternoCorp' => array(
		'codigo' => '920053',
		'talla' => '0',
		) ,
	'tradeItemDescriptionInformation' => array(
		'@language' => 'ES',
		'longText' => '920053-EAGLE EYES EXPLORER',
		) ,
	'invoicedQuantity' => array(
		'@unitOfMeasure' => 'PCE',
		'#text' => '28.00',
		) ,
	'grossPrice' => array(
		'Amount' => '344.40',
		) ,
	'netPrice' => array(
		'Amount' => '344.40',
		) ,
	'modeloInformation' => array(
		'longText' => 'Modelo del articulo',
		) ,
	'palletInformation' => array(
		'palletQuantity' => NULL,
		'description' => array(
			'@type' => 'BOX',
			) ,
		'transport' => array(
			'methodOfPayment' => 'PREPAID_BY_SELLER',
			) ,
		'prepactCant' => '0',
		) ,
	'allowanceCharge' => array(
		'@allowanceChargeType' => 'ALLOWANCE_GLOBAL',
		'specialServicesType' => NULL,
		'monetaryAmountOrPercentage' => array(
			'percentagePerUnit' => '0.00',
			'ratePerUnit' => array(
				'amountPerUnit' => '0.00',
				) ,
			) ,
		) ,
	'tradeItemTaxInformation' => array(
		'taxTypeDescription' => 'VAT',
		'tradeItemTaxAmount' => array(
			'taxPercentage' => '16.00',
			'taxAmount' => '1542.91',
			) ,
		) ,
	'totalLineAmount' => array(
		'grossAmount' => array(
			'Amount' => '9643.20',
			) ,
		'netAmount' => array(
			'Amount' => '9643.20',
			) ,
		) ,
	) ,
2 => array(
	'@type' => 'SimpleInvoiceLineItemType',
	'@number' => '3',
	'tradeItemIdentification' => array(
		'gtin' => '910813',
		) ,
	'alternateTradeItemIdentification' => array(
		'@type' => 'BUYER_ASSIGNED',
		'#text' => '910813',
		) ,
	'codigoTallaInternoCorp' => array(
		'codigo' => '910813',
		'talla' => '0',
		) ,
	'tradeItemDescriptionInformation' => array(
		'@language' => 'ES',
		'longText' => '910813-EAGLE EYES CELEBRITY PINK',
		) ,
	'invoicedQuantity' => array(
		'@unitOfMeasure' => 'PCE',
		'#text' => '4.00',
		) ,
	'grossPrice' => array(
		'Amount' => '559.91',
		) ,
	'netPrice' => array(
		'Amount' => '559.91',
		) ,
	'modeloInformation' => array(
		'longText' => 'Modelo del articulo',
		) ,
	'palletInformation' => array(
		'palletQuantity' => NULL,
		'description' => array(
			'@type' => 'BOX',
			) ,
		'transport' => array(
			'methodOfPayment' => 'PREPAID_BY_SELLER',
			) ,
		'prepactCant' => '0',
		) ,
	'allowanceCharge' => array(
		'@allowanceChargeType' => 'ALLOWANCE_GLOBAL',
		'specialServicesType' => NULL,
		'monetaryAmountOrPercentage' => array(
			'percentagePerUnit' => '0.00',
			'ratePerUnit' => array(
				'amountPerUnit' => '0.00',
				) ,
			) ,
		) ,
	'tradeItemTaxInformation' => array(
		'taxTypeDescription' => 'VAT',
		'tradeItemTaxAmount' => array(
			'taxPercentage' => '16.00',
			'taxAmount' => '358.34',
			) ,
		) ,
	'totalLineAmount' => array(
		'grossAmount' => array(
			'Amount' => '2239.64',
			) ,
		'netAmount' => array(
			'Amount' => '2239.64',
			) ,
		) ,
	) ,
3 => array(
	'@type' => 'SimpleInvoiceLineItemType',
	'@number' => '4',
	'tradeItemIdentification' => array(
		'gtin' => '967701',
		) ,
	'alternateTradeItemIdentification' => array(
		'@type' => 'BUYER_ASSIGNED',
		'#text' => '967701',
		) ,
	'codigoTallaInternoCorp' => array(
		'codigo' => '967701',
		'talla' => '0',
		) ,
	'tradeItemDescriptionInformation' => array(
		'@language' => 'ES',
		'longText' => '967701-EAGLE EYES AVIATOR',
		) ,
	'invoicedQuantity' => array(
		'@unitOfMeasure' => 'PCE',
		'#text' => '9.00',
		) ,
	'grossPrice' => array(
		'Amount' => '344.40',
		) ,
	'netPrice' => array(
		'Amount' => '344.40',
		) ,
	'modeloInformation' => array(
		'longText' => 'Modelo del articulo',
		) ,
	'palletInformation' => array(
		'palletQuantity' => NULL,
		'description' => array(
			'@type' => 'BOX',
			) ,
		'transport' => array(
			'methodOfPayment' => 'PREPAID_BY_SELLER',
			) ,
		'prepactCant' => '0',
		) ,
	'allowanceCharge' => array(
		'@allowanceChargeType' => 'ALLOWANCE_GLOBAL',
		'specialServicesType' => NULL,
		'monetaryAmountOrPercentage' => array(
			'percentagePerUnit' => '0.00',
			'ratePerUnit' => array(
				'amountPerUnit' => '0.00',
				) ,
			) ,
		) ,
	'tradeItemTaxInformation' => array(
		'taxTypeDescription' => 'VAT',
		'tradeItemTaxAmount' => array(
			'taxPercentage' => '16.00',
			'taxAmount' => '495.94',
			) ,
		) ,
	'totalLineAmount' => array(
		'grossAmount' => array(
			'Amount' => '3099.60',
			) ,
		'netAmount' => array(
			'Amount' => '3099.60',
			) ,
		) ,
	) ,
4 => array(
	'@type' => 'SimpleInvoiceLineItemType',
	'@number' => '5',
	'tradeItemIdentification' => array(
		'gtin' => '910856',
		) ,
	'alternateTradeItemIdentification' => array(
		'@type' => 'BUYER_ASSIGNED',
		'#text' => '910856',
		) ,
	'codigoTallaInternoCorp' => array(
		'codigo' => '910856',
		'talla' => '0',
		) ,
	'tradeItemDescriptionInformation' => array(
		'@language' => 'ES',
		'longText' => '910856-EAGLE EYES CELEBRITY GREEN',
		) ,
	'invoicedQuantity' => array(
		'@unitOfMeasure' => 'PCE',
		'#text' => '3.00',
		) ,
	'grossPrice' => array(
		'Amount' => '559.91',
		) ,
	'netPrice' => array(
		'Amount' => '559.91',
		) ,
	'modeloInformation' => array(
		'longText' => 'Modelo del articulo',
		) ,
	'palletInformation' => array(
		'palletQuantity' => NULL,
		'description' => array(
			'@type' => 'BOX',
			) ,
		'transport' => array(
			'methodOfPayment' => 'PREPAID_BY_SELLER',
			) ,
		'prepactCant' => '0',
		) ,
	'allowanceCharge' => array(
		'@allowanceChargeType' => 'ALLOWANCE_GLOBAL',
		'specialServicesType' => NULL,
		'monetaryAmountOrPercentage' => array(
			'percentagePerUnit' => '0.00',
			'ratePerUnit' => array(
				'amountPerUnit' => '0.00',
				) ,
			) ,
		) ,
	'tradeItemTaxInformation' => array(
		'taxTypeDescription' => 'VAT',
		'tradeItemTaxAmount' => array(
			'taxPercentage' => '16.00',
			'taxAmount' => '268.76',
			) ,
		) ,
	'totalLineAmount' => array(
		'grossAmount' => array(
			'Amount' => '1679.73',
			) ,
		'netAmount' => array(
			'Amount' => '1679.73',
			) ,
		) ,
	) ,
5 => array(
	'@type' => 'SimpleInvoiceLineItemType',
	'@number' => '6',
	'tradeItemIdentification' => array(
		'gtin' => '906077',
		) ,
	'alternateTradeItemIdentification' => array(
		'@type' => 'BUYER_ASSIGNED',
		'#text' => '906077',
		) ,
	'codigoTallaInternoCorp' => array(
		'codigo' => '906077',
		'talla' => '0',
		) ,
	'tradeItemDescriptionInformation' => array(
		'@language' => 'ES',
		'longText' => '906077-EAGLE EYES MAGELLAN GUNMETAL',
		) ,
	'invoicedQuantity' => array(
		'@unitOfMeasure' => 'PCE',
		'#text' => '5.00',
		) ,
	'grossPrice' => array(
		'Amount' => '773.71',
		) ,
	'netPrice' => array(
		'Amount' => '773.71',
		) ,
	'modeloInformation' => array(
		'longText' => 'Modelo del articulo',
		) ,
	'palletInformation' => array(
		'palletQuantity' => NULL,
		'description' => array(
			'@type' => 'BOX',
			) ,
		'transport' => array(
			'methodOfPayment' => 'PREPAID_BY_SELLER',
			) ,
		'prepactCant' => '0',
		) ,
	'allowanceCharge' => array(
		'@allowanceChargeType' => 'ALLOWANCE_GLOBAL',
		'specialServicesType' => NULL,
		'monetaryAmountOrPercentage' => array(
			'percentagePerUnit' => '0.00',
			'ratePerUnit' => array(
				'amountPerUnit' => '0.00',
				) ,
			) ,
		) ,
	'tradeItemTaxInformation' => array(
		'taxTypeDescription' => 'VAT',
		'tradeItemTaxAmount' => array(
			'taxPercentage' => '16.00',
			'taxAmount' => '618.97',
			) ,
		) ,
	'totalLineAmount' => array(
		'grossAmount' => array(
			'Amount' => '3868.55',
			) ,
		'netAmount' => array(
			'Amount' => '3868.55',
			) ,
		) ,
	) ,
) ,
'totalAmount' => array(
	'Amount' => '22770.36',
	) ,
'TotalAllowanceCharge' => array(
	'@allowanceOrChargeType' => 'ALLOWANCE',
	'specialServicesType' => NULL,
	'Amount' => '0.00',
	) ,
'baseAmount' => array(
	'Amount' => '22770.36',
	) ,
'tax' => array(
	'@type' => 'VAT',
	'taxPercentage' => '16.00',
	'taxAmount' => '3643.26',
	'taxCategory' => 'TRANSFERIDO',
	) ,
'payableAmount' => array(
	'Amount' => '26413.62',
	) ,
'cadenaOriginal' => array(
	'Cadena' => '||3.2|IFA|8618|2015-04-23T17:09:50|||ingreso|PAGO EN UNA SOLA EXHIBICION|CREDITO 60 DIAS|22770.36|0.00|26413.62|TRANSFERENCIA ELECTRONICA|ESTADOS UNIDOS MEXICANOS, Distrito Federal|8711|1|MXP|IML121023RE5|IMPORTACIONES DE MEXICO Y LATINOAMERICA S DE RL DE CV|CALLE 2|No 246||GRANJAS SAN ANTONIO||IZTAPALAPA|Distrito Federal|ESTADOS UNIDOS MEXICANOS|09070|CALLE 2|No 246|GRANJAS SAN ANTONIO|IZTAPALAPA|Distrito Federal|ESTADOS UNIDOS MEXICANOS|09070|REGIMEN GENERAL DE LEY PERSONAS MORALES|COP920428Q20|COPPEL S.A. DE C.V.|Republica|2855|PTE.|RECURSOS HIDRAULICOS|CULIACAN|30009|CULIACAN|Sinaloa|MEXICO|80105|4.00|PZA|810712011924|910831-EAGLE EYES CELEBRITY ORANGE|559.91|2239.64|28.00|PZA|810712010057|920053-EAGLE EYES EXPLORER|344.40|9643.20|4.00|PZA|810712012013|910813-EAGLE EYES CELEBRITY PINK|559.91|2239.64|9.00|PZA|810712010033|967701-EAGLE EYES AVIATOR|344.40|3099.60|3.00|PZA|810712011993|910856-EAGLE EYES CELEBRITY GREEN|559.91|1679.73|5.00|PZA|810712010062|906077-EAGLE EYES MAGELLAN GUNMETAL GOLD|773.71|3868.55|IVA|16.00|3643.26|3643.26||',
	) ,
) ,
) ,
);
return $structuraAddenda;
}
}