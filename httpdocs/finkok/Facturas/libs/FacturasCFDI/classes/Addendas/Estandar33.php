<?php
namespace FacturasCFDI\Addendas;
use MysqlBD;
class Estandar33{
	public static $id_invoices;
	public static $tipo;
	public static $conn;
	public static $struct;
	public static function getAddendaStruct($invoice){
		global $cfg;
		if(count($invoice->getDatos()) == 0)
			throw new \Exception("Sin datos de Invoice.");

		self::$id_invoices = $invoice->ID_invoices;
		
		self::$tipo = self::getComprobante(strtolower(trim($invoice->invoice_type)));

		self::$conn = MysqlBD::getConexion();
		
		$rfcEmisor = $invoice->expediter_fcode;

		if(isset($cfg['finkok_test_mode']) && $cfg['finkok_test_mode'] == 1){
			$rfcEmisor = getRFC();
		}
        /*
        "@Fecha": "2017-01-05T09:09:23", 
        "@Sello": "", 
        "@NoCertificado": "20001000000200001428", 
        "@Certificado": "", 
        "@SubTotal": "1000", 
        "@Moneda": "MXN", 
        "@Total": "1500", 
        "@TipoDeComprobante": "I", 
        "@FormaPago": "01", 
        "@MetodoPago": "PUE", 
        "@CondicionesDePago": "CONDICIONES", 
        "@Descuento": "0.00", 
        "@TipoCambio": "1.0", 
        "@LugarExpedicion": "45079",
        */
        // Catalogo Provisto por sat
		$invoice->payment_method = ($invoice->payment_method != '') ? $invoice->payment_method : '99';

		// $data = array(
		// 	'@Version'			 => "3.3",
		// 	'@Fecha' 			 => join('T',explode(' ',$invoice->doc_date)),
		// 	'@Moneda'			 => self::getMoneda(strtoupper(trim($invoice->currency))),
		// 	'@TipoDeComprobante' => self::getComprobante(strtolower(trim($invoice->invoice_type))),
		// 	'@NoCertificado'	 => @getKeyAndNumCert($invoice->expediter_fcode)['cert'],
		// 	'@LugarExpedicion'	 =>$invoice->expediter_faddress_zipcode,
  //       );
		
		// Obtenemos Encabezado de CFDI
		self::$struct = self::getHeaderInvoice($invoice);
		// Obtenemos UUID relacionados.	
		$related = self::getRelatedInvoices($invoice->ID_invoices);
		if(count($related) > 0)
			self::$struct['cfdi:CfdiRelacionados'] = $related;

		
		self::$struct['cfdi:Emisor'] = array(
			'@Rfc' => $rfcEmisor,
			'@Nombre' => limpiar($invoice->expediter_fname),
			'@RegimenFiscal' => self::getRegimen($invoice->expediter_fregimen)
		);
		self::$struct["cfdi:Receptor"] = array(
            "@Rfc" => $invoice->customer_fcode, 
            "@Nombre" => limpiar($invoice->customer_fname), 
            // "@UsoCFDI" => (self::$tipo == 'P') ? 'P01' : 'G01' // $invoice->use_cfdi
        );
		if(self::$tipo == 'P'){
			self::$struct["cfdi:Receptor"]['@UsoCFDI'] = 'P01';
		}elseif($invoice->use_cfdi != ''){
			self::$struct["cfdi:Receptor"]['@UsoCFDI'] = $invoice->use_cfdi;
		}elseif(self::$tipo == 'E' && $invoice->ID_creditmemos != ''){
			self::$struct["cfdi:Receptor"]['@UsoCFDI'] = 'G02';
		}else{
			self::$struct["cfdi:Receptor"]['@UsoCFDI'] = 'G01';

		}
		

        if(self::$tipo == 'I' || self::$tipo == 'E'){
        	self::$struct['@FormaPago'] = $invoice->payment_method;
			self::$struct['@MetodoPago'] = self::getMetodoPago(strtoupper(trim($invoice->payment_type)));
        }
        // Solo si es Diferente de Mexico
        if(self::getPais(trim($invoice->customer_address_country)) != 'MEX'){
        	self::$struct['cfdi:Receptor']['@ResidenciaFiscal'] = self::getPais(trim($invoice->customer_address_country));
        }

		// Obtenemos Descuentos 
		$rs = self::$conn->query("SELECT SUM(discount) descuento FROM cu_invoices_lines where discount > 0 and id_invoices = '".$invoice->ID_invoices."'");
		$descuento = $rs->fetch()['descuento'];

		if($descuento > 0 && self::$tipo != 'P' && self::$tipo != 'T'){
			self::$struct['@Descuento'] = $descuento;
		}


		if($invoice->doc_serial !='' and $invoice->doc_num !='0'){
			self::$struct['@Serie'] =$invoice->doc_serial;
			self::$struct['@Folio'] = $invoice->doc_num < 100000 ? str_pad($invoice->doc_num,5,"0", STR_PAD_LEFT) : $invoice->doc_num;
		}else{
			$serialNum = self::getInvoiceSerialNum($invoice->invoice_type);
			self::$struct['@Serie'] =$serialNum['doc_serial'];
			self::$struct['@Folio'] = $serialNum['doc_num'] < 100000 ? str_pad($serialNum['doc_num'],5,"0", STR_PAD_LEFT) : $serialNum['doc_num'];
		}

		$impuesto = 0;
		$retenido = 0;
		$conceptosQuery = "SELECT 
			cu_invoices_lines.ID_orders_products
			, cu_invoices_lines.ID_orders
			, cu_invoices_lines.ID_creditmemos
			, cu_invoices_lines.ID_sku
			, cu_invoices_lines.UPC
			, cu_invoices_lines.quantity
			, cu_invoices_lines.discount
			, cu_invoices_lines.measuring_unit
			, CONCAT(cu_invoices_lines.ID_sku, ' - ', cu_invoices_lines.description) Description
			, cu_invoices_lines.ID_sku_alias
			, CONCAT(cu_invoices_lines.ID_sku_alias, ' - ', cu_invoices_lines.description) AS 'CustomDescription'
			, cu_invoices_lines.unit_price
			, cu_invoices_lines.amount
			, cu_invoices_lines.tax
			, IF(crp1.ID_products_services is null, crp2.ID_products_services, crp1.ID_products_services) ID_products_services
			, IF(crp3.ID_products_services is null, '1010101', crp3.ID_products_services) ID_prod_services
			, cu_invoices_lines.tax2_base
			, cu_invoices_lines.tax2_rate
			, cu_invoices_lines.tax2_amount
		FROM cu_invoices_lines 
		LEFT JOIN cu_relations_products as crp1 ON cu_invoices_lines.ID_sku = crp1.ID_table AND crp1.table='sl_skus'
		LEFT JOIN cu_relations_products as crp2 ON SUBSTR(cu_invoices_lines.ID_sku,-4) = crp2.ID_table AND crp2.table='sl_services'
		LEFT JOIN cu_relations_products as crp3 ON RIGHT(cu_invoices_lines.ID_sku, 6) = RIGHT(crp3.ID_table,6) AND crp3.table='sl_products'
		WHERE ID_invoices = $invoice->ID_invoices";
		$conceptos = MysqlBD::selectQuery($conceptosQuery);
		$conc = array();
		$subtotal_invoice = 0;

		if(self::$tipo == 'P'){
			$v = array(
				"@ClaveProdServ" =>  '84111506', // Catalogo Relacional
				"@ClaveUnidad" => "ACT", // Valor FIJO H87 ==> PIEZA
				// "@NoIdentificacion" =>  $concepto->ID_sku, 
				"@Cantidad" => 1, 
				"@Descripcion" =>  'Pago', 
				"@ValorUnitario" => 0, 
				"@Importe" =>  0
			);
			$conc[] = $v;
		}else{
			for ($i=0; $i < $conceptos->num(); $i++) {
				$concepto = $conceptos->get($i);
				$impuesto += number_format($concepto->tax,2,'.','');
				$retenido += number_format($concepto->tax2_amount,2,'.','');
				$subtotal_invoice += number_format($concepto->amount,2,'.','');
				$table = ($concepto->ID_orders == 0) ? 'sl_creditmemos' : 'sl_orders';
		        $id_trs = ($concepto->ID_orders == 0) ? $concepto->ID_creditmemos : $concepto->ID_orders;
		        $id_product = $concepto->ID_sku;
	            
	            // Partes
	            ## ¿Es SKU o es PRODUCT?
				if (substr($concepto->ID_sku,0,1) == '1'){
					$queryPartes = "
					SELECT 
						sl_skus.ID_sku_products ID_sku
						, sl_skus.UPC
						, sl_skus_parts.Qty
						, CONCAT('40000', sl_skus_parts.ID_parts) ver
						, CONCAT('40000', sl_skus_parts.ID_parts, ' - ', sl_parts.Model) Description
						, cu_relations_products.ID_products_services
					FROM sl_skus
					INNER JOIN sl_skus_parts ON sl_skus.ID_sku_products = sl_skus_parts.ID_sku_products
					INNER JOIN sl_parts ON sl_skus_parts.ID_parts = sl_parts.ID_parts
					LEFT JOIN cu_relations_products ON CONCAT('40000', sl_skus_parts.ID_parts) = cu_relations_products.ID_table AND cu_relations_products.table='sl_skus'
					WHERE 1
						AND sl_skus.ID_sku_products = $concepto->ID_sku";
					$partes = MysqlBD::selectQuery($queryPartes);

					$partesArray = array();
					for ($j=0; $j < $partes->num(); $j++) {
						$parte = $partes->get($j);

						$query = "SELECT 
				            cu_customs_info.import_declaration_number
				        FROM 
				            sl_skus_trans 
				            INNER JOIN cu_customs_info ON sl_skus_trans.ID_customs_info=cu_customs_info.ID_customs_info 
				            LEFT JOIN sl_vendors ON sl_vendors.ID_vendors=cu_customs_info.ID_vendors 
				        WHERE  
				            sl_skus_trans.tbl_name='$table' and
				            sl_skus_trans.ID_trs=$id_trs and 
				            sl_skus_trans.ID_products=$parte->ID_sku 
				        GROUP BY sl_skus_trans.ID_products, sl_skus_trans.ID_customs_info 
				        ORDER BY sl_skus_trans.ID_products_trans;";
						$res = self::$conn->query($query);
						$datosAduana = array();
						$all = $res->fetchAll(\PDO::FETCH_NUM);
						foreach ($all as $key => $row) {
							$datosAduana[] = array(
								'@NumeroPedimento'=>preg_replace("/(\d{2})(\d{2})(\d{4})(\d{7})/", "$1  $2  $3  $4", limpiar($row[0]))
							);
						}

						if(substr($parte->ver,0,1) == '4' && $parte->ID_products_services == ''){
							throw new \Exception("El sku: $parte->ver, no tiene un ID del SAT asociado.");
						}

						if($parte->ID_products_services == '')
							$parte->ID_products_services = "1010101";
						$partePiece = array(
		                    "@ClaveProdServ" => $parte->ID_products_services == "1010101" ? "01010101" : $parte->ID_products_services, // Catalogo Relacional
		                    "@NoIdentificacion" => $parte->ID_sku, 
		                    "@Cantidad" => $parte->Qty, 
		                    "@Descripcion" => limpiar($parte->Description), 
		                    "@Unidad" => $concepto->measuring_unit, 
		                 );
		                if(count($datosAduana) > 0){
							$partePiece["cfdi:InformacionAduanera"] = $datosAduana;
						}
						$partesArray[] = $partePiece;
					}
				}

				if(substr($id_product,0,1) == '4' && $concepto->ID_products_services == '' && $concepto->ID_products_services > 0){
					throw new \Exception("El sku: $id_product, no tiene un ID del SAT asociado.");
				}

				// Informacion Aduanera //
				$datosAduana = array();
				if(substr($id_product,0,1) == '4'){
					$query = "SELECT 
			            cu_customs_info.import_declaration_number
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
					$res = self::$conn->query($query);
					$all = $res->fetchAll(\PDO::FETCH_NUM);
					foreach ($all as $key => $row) {
						$datosAduana[] = array(
							'@NumeroPedimento'=>preg_replace("/(\d{2})(\d{2})(\d{4})(\d{7})/", "$1  $2  $3  $4", limpiar($row[0]))
						);
					}

					// Sobrescribe la descripcion, por la descripcion con el UPC del cliente
					$concepto->Description = $concepto->CustomDescription;
				}

				// Información Aduanera //

				// exit;
				if($concepto->ID_prod_services == '' && $concepto->ID_products_services = '' && $concepto->ID_prod_services > 0 && $concepto->ID_products_services > 0){
					$concepto->ID_prod_services = "1010101";
				}elseif($concepto->ID_products_services != ''){
					$concepto->ID_prod_services	= $concepto->ID_products_services;
				}

				$v = array(
					"@ClaveProdServ" =>  $concepto->ID_prod_services == "1010101" ? "01010101" : $concepto->ID_prod_services, // Catalogo Relacional
	                "@ClaveUnidad" => self::getUnit($concepto->measuring_unit), // Valor FIJO H87 ==> PIEZA
	                "@NoIdentificacion" =>  $concepto->ID_sku, 
	                "@Cantidad" => $concepto->quantity, 
	                "@Unidad" => $concepto->measuring_unit,  //Cambio a Dato de Catalogo
	                "@Descripcion" =>  limpiar($concepto->Description), 
	                "@ValorUnitario" => number_format($concepto->unit_price,2,'.',''), 
	                "@Importe" =>  number_format($concepto->amount,2,'.',''), 
				);
				if($concepto->discount > 0 && self::$tipo != 'T'){
					$v['@Descuento'] = $concepto->discount;
				}
				if($concepto->tax > 0){
					$base = $concepto->amount;
					if($concepto->discount > 0){
						$base -= $concepto->discount;
					}
					$v['cfdi:Impuestos'] = array(
		                "cfdi:Traslados" => array(
		                    "cfdi:Traslado"=> array(
		                        "@Base"=> number_format($base,2,'.',''), 
		                        "@Impuesto"=> "002", // Aplica SOLO IVA @TODO es necesario otros ?? 
		                        "@TipoFactor"=> "Tasa", // SOLO IVA @TODO es necesario otros??
		                        "@TasaOCuota"=> "0.160000", // SOLO IVA @es necesario otros
		                        "@Importe"=> number_format($concepto->tax,2,'.','')
		                    )
		                ) 
	                );
				}

				## Retencion de IVA
				if($concepto->tax2_base > 0){
					$base = $concepto->tax2_base;
					
					$v['cfdi:Impuestos']['cfdi:Retenciones'] = array(
		                "cfdi:Retencion" => array(
	                        "@Base"=> number_format($base,2,'.',''), 
	                        "@Impuesto"=> "002", // Aplica SOLO IVA 
	                        "@TipoFactor"=> "Tasa", // SOLO IVA 
	                        "@TasaOCuota"=> str_pad(round($concepto->tax2_rate,2), 8, '0'), // SOLO IVA @es necesario otros
	                        "@Importe"=> number_format($concepto->tax2_amount,2,'.','')
		                ) 
	                );
				}


				if(count($partesArray) > 0){
					$v["cfdi:Parte"] = $partesArray;
				}

				if(count($datosAduana) > 0){
					$v["cfdi:InformacionAduanera"] = $datosAduana;
				}

				if($concepto->UPC != ''){
					$v['@NoIdentificacion']=$concepto->UPC;
				}
				$conc[] = $v;
			}
		}
		self::$struct['@SubTotal'] = (self::$tipo == 'P' || self::$tipo == 'T') ? 0 : number_format($subtotal_invoice,2,'.','');
		self::$struct['@Total'] = (self::$tipo == 'P' || self::$tipo == 'T') ? 0 : number_format($subtotal_invoice + $impuesto - $retenido- $descuento,2,'.','');

		self::$struct['cfdi:Conceptos']['cfdi:Concepto'] =$conc;

     // <cfdi:Impuestos TotalImpuestosRetenidos="1196492" TotalImpuestosTrasladados="363104">
	 //        <cfdi:Retenciones>
	 //            <cfdi:Retencion Impuesto="002" Importe="2720" />
	 //            <cfdi:Retencion Impuesto="003" Importe="1193772" />
	 //        </cfdi:Retenciones>
	 //        <cfdi:Traslados>
	 //            <cfdi:Traslado Impuesto="002" TipoFactor="Tasa" TasaOCuota="0.160000" Importe="363104" />
	 //        </cfdi:Traslados>
	 //    </cfdi:Impuestos>


		if($impuesto > 0 || $retenido > 0){
			if ( $retenido > 0 ){
				self::$struct['cfdi:Impuestos']['@TotalImpuestosRetenidos'] = number_format($retenido,2,'.','');
				self::$struct['cfdi:Impuestos']['cfdi:Retenciones'] = array(
					'cfdi:Retencion' =>array(
						"@Impuesto"=> "002", 
	                    // "@TipoFactor"=> "Tasa", 
	                    // "@TasaOCuota"=> "0.160000", 
	                    "@Importe"=> number_format($retenido,2,'.','')

					)
				);
			}
			if ( $impuesto > 0 ) 
				self::$struct['cfdi:Impuestos']['@TotalImpuestosTrasladados'] = number_format($impuesto,2,'.','');
				self::$struct['cfdi:Impuestos']['cfdi:Traslados'] = array(
					'cfdi:Traslado' =>array(
						"@Impuesto"=> "002", 
	                    "@TipoFactor"=> "Tasa", 
	                    "@TasaOCuota"=> "0.160000", 
	                    "@Importe"=> number_format($impuesto,2,'.','')

					)
				);
			
		}
		// show(self::$struct);
		$pagos = [];
		if(self::$tipo == 'P'){
			$qry = "
			SELECT * FROM (
				SELECT 
					IF(sl_banks_movements.BankDate is null, cu_invoices.doc_date,concat( sl_banks_movements.BankDate, ' ',curtime())) BankDate
					, ROUND(sum(cu_customers_payments_trans.Amount), 2)Amount
					, sl_banks_movements.bank
					, sl_banks_movements.fcode_bank
					, sl_banks_movements.ID_banks_movements

					, cu_invoices.operation_num AS 'NumOperacion'
					, cu_invoices.expediter_fcode_bank AS 'RfcEmisorCtaOrd'
					, cu_invoices.expediter_bank AS 'NomBancoOrdExt'
					, cu_invoices.expediter_account_number AS 'CtaOrdenante'
					, cu_invoices.customer_fcode_bank AS 'RfcEmisorCtaBen'
					, cu_invoices.customer_account_number AS 'CtaBeneficiario'
					, cu_customers_payments_trans.ID_tableused AS 'ID_invoice'
					, cu_customers_payments_trans.date
					, cu_customers_payments_trans.time
				FROM cu_customers_payments_trans
				LEFT JOIN sl_banks_movements  on cu_customers_payments_trans.ID_banks_movements = sl_banks_movements.ID_banks_movements
				LEFT JOIN cu_invoices ON cu_customers_payments_trans.ID_invoices = cu_invoices.ID_invoices
				WHERE cu_customers_payments_trans.id_invoices = '$invoice->ID_invoices'
				AND cu_customers_payments_trans.`type` in ('Apply')
				GROUP BY cu_customers_payments_trans.ID_tableused
				
				UNION
				
				SELECT 
					IF(sl_banks_movements.BankDate is null, cu_invoices.doc_date,concat( sl_banks_movements.BankDate, ' ',curtime())) BankDate
					, ROUND(sum(cu_customers_payments_trans.Amount), 2)Amount
					, sl_banks_movements.bank
					, sl_banks_movements.fcode_bank
					, sl_banks_movements.ID_banks_movements

					, cu_invoices.operation_num AS 'NumOperacion'
					, cu_invoices.expediter_fcode_bank AS 'RfcEmisorCtaOrd'
					, cu_invoices.expediter_bank AS 'NomBancoOrdExt'
					, cu_invoices.expediter_account_number AS 'CtaOrdenante'
					, cu_invoices.customer_fcode_bank AS 'RfcEmisorCtaBen'
					, cu_invoices.customer_account_number AS 'CtaBeneficiario'
					, cu_customers_payments_trans.ID_tableused AS 'ID_invoice'
					, cu_customers_payments_trans.date
					, cu_customers_payments_trans.time
				FROM cu_customers_payments_trans
				LEFT JOIN sl_banks_movements  on cu_customers_payments_trans.ID_banks_movements = sl_banks_movements.ID_banks_movements
				LEFT JOIN cu_invoices ON cu_customers_payments_trans.ID_invoices = cu_invoices.ID_invoices
				WHERE cu_customers_payments_trans.id_invoices = '$invoice->ID_invoices'
				AND cu_customers_payments_trans.`type` in ('Out')
				GROUP BY cu_customers_payments_trans.ID_invoices_related
			)T ORDER BY Date ASC , Time ASC";
			$rs = self::$conn->query($qry);
			$pagosDet = [];
			$auxPagos = 0;
			while($pago = $rs->fetch(\PDO::FETCH_OBJ)){
				$result = [];
				$result['@FechaPago'] = join('T',explode(' ',$pago->BankDate));

				if ($pago->ID_banks_movements != ''){
					$result['@FormaDePagoP'] = str_pad($invoice->payment_method,2,"0", STR_PAD_LEFT);
					if($pago->RfcEmisorCtaOrd!='' && $pago->CtaOrdenante!='' && $pago->RfcEmisorCtaBen!='' && $pago->NomBancoOrdExt!='' && $pago->CtaBeneficiario!='' ){
						
						// Nodo: Pago->NumOperacion
						if (isset($pago->NumOperacion) && $pago->NumOperacion!=''){
							$result['@NumOperacion'] = $pago->NumOperacion;
						}

						// Nodo: Pago->RfcEmisorCtaOrd
						if (isset($pago->RfcEmisorCtaOrd) && $pago->RfcEmisorCtaOrd!=''){
							$result['@RfcEmisorCtaOrd'] = $pago->RfcEmisorCtaOrd;
						}

						// Nodo: Pago->NomBancoOrdExt
						if (isset($pago->NomBancoOrdExt) && $pago->NomBancoOrdExt!=''){
							$result['@NomBancoOrdExt'] = $pago->NomBancoOrdExt;
						}

						// Nodo: Pago->CtaOrdenante
						if (isset($pago->CtaOrdenante) && $pago->CtaOrdenante!=''){
							$result['@CtaOrdenante'] = $pago->CtaOrdenante;
						}

						// Nodo: Pago->RfcEmisorCtaBen
						if (isset($pago->RfcEmisorCtaBen) && $pago->RfcEmisorCtaBen!=''){
							$result['@RfcEmisorCtaBen'] = $pago->RfcEmisorCtaBen;
						}

						// Nodo: Pago->CtaBeneficiario
						if (isset($pago->CtaBeneficiario) && $pago->CtaBeneficiario!=''){
							$result['@CtaBeneficiario'] = $pago->CtaBeneficiario;
						}
					}
				}else{
					$result['@FormaDePagoP'] = '17'; // Fijo Temporalmente
				}
				$result['@MonedaP'] = self::getMoneda(strtoupper(trim($pago->currency)));
				$result['@Monto'] = join('T',explode(' ',$pago->Amount));
				$result["pago10:DoctoRelacionado"] = [];
				if($pago->ID_banks_movements != ''){
					$query = "SELECT 
						id_tableused
						, parcialidades.Parcialidad
						, ROUND(cu_customers_payments_trans.base, 2) base
						, ROUND(cu_customers_payments_trans.amount, 2) amount
						, ROUND(cu_customers_payments_trans.balance, 2)balance 
						, cu_invoices.xml_uuid
						, cu_invoices.payment_type
						, cu_invoices.payment_method
						, ROUND(cu_invoices.invoice_total, 2)invoice_total
						, ROUND(cu_invoices.currency, 2) currency
					FROM cu_customers_payments_trans
					INNER JOIN cu_invoices ON cu_customers_payments_trans.id_tableused = cu_invoices.ID_invoices
					INNER JOIN (
						SELECT 
							cu_customers_payments_trans.id_invoices
							, (@cnt := @cnt + 1) AS Parcialidad
						FROM cu_customers_payments_trans
						CROSS JOIN (SELECT @cnt := 0) AS dummy
						WHERE 1
							AND cu_customers_payments_trans.ID_tableused = '$pago->ID_invoice'
							AND cu_customers_payments_trans.`amount` > 0
							AND cu_customers_payments_trans.`type` = 'Apply'
					)parcialidades on parcialidades.id_invoices = cu_customers_payments_trans.id_invoices
					WHERE 1
						AND cu_customers_payments_trans.id_invoices = '$invoice->ID_invoices'
						AND cu_customers_payments_trans.ID_tableused = '$pago->ID_invoice'
						AND cu_customers_payments_trans.`amount` > 0
						AND cu_customers_payments_trans.`type` = 'Apply'
						AND cu_customers_payments_trans.tableused = 'cu_invoices'
					ORDER BY cu_customers_payments_trans.date ASC, cu_customers_payments_trans.time ASC";
					$resultSet = self::$conn->query($query);
					// Recorremos Related Invoices
					while( $row = $resultSet->fetch(\PDO::FETCH_OBJ)){
						$result["pago10:DoctoRelacionado"][] = [
							"@IdDocumento" => strtoupper( $row->xml_uuid ), 
							"@MonedaDR" => self::getMoneda(strtoupper(trim($row->currency))), 
							"@MetodoDePagoDR" => self::getMetodoPago(strtoupper(trim($invoice->payment_type))), 
							"@NumParcialidad" =>  $row->Parcialidad, 
							// "@TipoCambioDR" => "1", 
							"@ImpSaldoAnt" => number_format($row->base,2,'.',''), 
							"@ImpPagado" => number_format($row->amount,2,'.',''), 
							"@ImpSaldoInsoluto" => number_format($row->balance,2,'.','')
						];
					}

				}else{
					$query = "select 
						id_tableused
						, ROUND(cu_customers_payments_trans.base, 2) base
						, ROUND(cu_customers_payments_trans.amount, 2) amount
						, ROUND(cu_customers_payments_trans.balance, 2)balance 
						, cu_invoices.xml_uuid
						, cu_invoices.payment_type
						, cu_invoices.payment_method
						, ROUND(cu_invoices.invoice_total, 2)invoice_total
						, ROUND(cu_invoices.currency, 2) currency
					from cu_customers_payments_trans
					inner join cu_invoices on cu_customers_payments_trans.id_tableused = cu_invoices.ID_invoices
					where 1
						and cu_customers_payments_trans.id_invoices = '$invoice->ID_invoices'
						and cu_customers_payments_trans.id_tableused = '$pago->ID_invoice'
						and cu_customers_payments_trans.`amount` > 0
						and cu_customers_payments_trans.`type` = 'Out'
						and cu_customers_payments_trans.tableused = 'cu_invoices'
					order by cu_customers_payments_trans.date ASC, cu_customers_payments_trans.time ASC";
					$resultSet = self::$conn->query($query);
					// Recorremos Related Invoices
					
					while( $row = $resultSet->fetch(\PDO::FETCH_OBJ)){
						$result["pago10:DoctoRelacionado"][] = [
							"@IdDocumento" => strtoupper( $row->xml_uuid ), 
							"@MonedaDR" => self::getMoneda(strtoupper(trim($row->currency))), 
							"@MetodoDePagoDR" => self::getMetodoPago(strtoupper(trim($invoice->payment_type))), 
							"@NumParcialidad" =>  "1", 
							// "@TipoCambioDR" => "1", 
							"@ImpSaldoAnt" => number_format($row->base,2,'.',''), 
							"@ImpPagado" => number_format($row->amount,2,'.',''), 
							"@ImpSaldoInsoluto" => number_format($row->balance,2,'.','')
						];
					}
				}
				$pagosDet[] = $result;
				$aux++;
			}



			$pagos = [
				'pago10:Pagos' => [
                	"@xmlns:pago10" => "http://www.sat.gob.mx/Pagos", 
	                "@Version" =>  "1.0", 
	                "@xsi:schemaLocation" => "http://www.sat.gob.mx/Pagos http://www.sat.gob.mx/sitio_internet/cfd/Pagos/Pagos10.xsd", 
					'pago10:Pago' => $pagosDet
				]
			];

		/*
		"pago10:DoctoRelacionado": [
                        {
                            "@IdDocumento": "970e4f32-0fe0-11e7-93ae-92361f002671", 
                            "@MonedaDR": "MXN", 
                            "@MetodoDePagoDR": "PIP", 
                            "@NumParcialidad": "1", 
                            "@ImpSaldoAnt": "10000", 
                            "@ImpPagado": "5000", 
                            "@ImpSaldoInsoluto": "5000"
                        }, 
                        {
                            "@IdDocumento": "970e5496-0fe0-11e7-93ae-92361f002672", 
                            "@MonedaDR": "USD", 
                            "@TipoCambioDR": "20.00", 
                            "@MetodoDePagoDR": "PIP", 
                            "@NumParcialidad": "2", 
                            "@ImpSaldoAnt": "250.00", 
                            "@ImpPagado": "250.00", 
                            "@ImpSaldoInsoluto": "0.00"
                        }
                    ], 
                    "pago10:Impuestos": {
                        "@TotalImpuestosRetenidos": "1600", 
                        "pago10:Retenciones": {
                            "pago10:Retencion": {
                                "@Impuesto": "002", 
                                "@Importe": "1600"
                            }
                        }
                    }

		*/


	   // "cfdi:Complemento": {
	   //          "pago10:Pagos": {
	   //              "pago10:Pago": {
	   //                  "@FechaPago": "2017-03-22T09:00:00", 
	   //                  "@FormaDePagoP": "06", 
	   //                  "@MonedaP": "MXN", 
	   //                  "@Monto": "10000", 
	   //                  "@RfcEmisorCtaOrd": "XEXX010101000", 
	   //                  "@CtaOrdenante": "1234567890", 
	   //                  "pago10:DoctoRelacionado": [
	   //                      {
	   //                          "@IdDocumento": "970e4f32-0fe0-11e7-93ae-92361f002671", 
	   //                          "@MonedaDR": "MXN", 
	   //                          "@MetodoDePagoDR": "PIP", 
	   //                          "@NumParcialidad": "1", 
	   //                          "@ImpSaldoAnt": "10000", 
	   //                          "@ImpPagado": "5000", 
	   //                          "@ImpSaldoInsoluto": "5000"
	   //                      }, 
	   //                      {
	   //                          "@IdDocumento": "970e5496-0fe0-11e7-93ae-92361f002672", 
	   //                          "@MonedaDR": "USD", 
	   //                          "@TipoCambioDR": "20.00", 
	   //                          "@MetodoDePagoDR": "PIP", 
	   //                          "@NumParcialidad": "2", 
	   //                          "@ImpSaldoAnt": "250.00", 
	   //                          "@ImpPagado": "250.00", 
	   //                          "@ImpSaldoInsoluto": "0.00"
	   //                      }
	   //                  ]
	   //              }
	   //          }
       // }
		}
		self::$struct['cfdi:Complemento'] = $pagos;
		// echo '<pre>';
		// print_r(self::$struct);
		// exit;
		session_start();
		$_SESSION['invoice'] = self::$struct;

		return self::$struct;
	}
	public static function getIdInvoice(){
		return self::$id_invoices;
	}
	protected static function getComprobante($comprobante = ''){
    	$comprobanteList = array(
    		'ingreso' 	=> 'I',
    		'egreso'	=> 'E',
    		'traslado'	=> 'T',
    		'nomina'	=> 'N',
    		'pago'		=> 'P'
    	);
    	return isset($comprobanteList[$comprobante]) ? $comprobanteList[$comprobante] : 'I';
	}
	protected static function getMoneda($moneda = ''){
		$monedaList = array(
        	'MX$' => 'MXN',
        	'MXP' => 'MXN',
        	'USD' => 'USD'
    	);
    	return isset($monedaList[$moneda]) ? $monedaList[$moneda] : 'MXN';

	}
	protected static function getMetodoPago($metodo = ''){
		if(strlen($metodo) == 3){
			return $metodo;
		}
    	$metodoPago = array(
    		'PAGO EN UNA SOLA EXHIBICION' => 'PUE'
    	);
    	return isset($metodoPago[$metodo]) ? $metodoPago[$metodo] : 'PUE';
	}
	protected static function getRegimen($regimen = ''){
    	$regimenList = array(
    		'REGIMEN GENERAL DE LEY PERSONAS MORALES' => '601'
    	);
    	return isset($regimenList[$regimen]) ? $regimenList[$regimen] : '601';
	}

	protected static function getPais($pais = ''){
		$paises = array(
			'MEXICO' => 'MEX',
			'ESTADOS UNIDOS MEXICANOS' => 'MEX',
			'ESTADOS UNIDOS' => 'USA'
		);
		return isset($paises[$pais]) ? $paises[$pais] : 'MEX';
	}

	protected static function getRelatedInvoices($idInvoices){
		$queryRelacionados = "
			SELECT
				relation_type
				, group_concat(uuid_related) uuids
			FROM cu_related_cfdi
			WHERE 1
				AND cu_related_cfdi.id_cfdi = {$idInvoices}
				AND cu_related_cfdi.uuid_related != ''
			GROUP BY relation_type;";
		$rs = self::$conn->query($queryRelacionados);
		$relacionados = [];
		$tipos = [];
		while($row = $rs->fetch(\PDO::FETCH_OBJ)){
			$uuids = explode(',', $row->uuids);
			$uuids = array_map(function($element){
				return [ '@UUID' => $element ];
			}, $uuids);
			$relacionados[] = [
				'@TipoRelacion' => $row->relation_type,
				'cfdi:CfdiRelacionado'	=> $uuids
			];
		}
		return $relacionados;
	}

	protected static function getUnit($unidad){
		if($unidad == 'PZA' || $unidad == '')
			return 'H87';
		return $unidad;
	}

	protected static function getHeaderInvoice($data){
		$numCertificado = @getKeyAndNumCert($data->expediter_fcode);
		$nodos = [
			'@Version'			 => '3.3',
			'@Fecha' 			 => join('T',explode(' ',$data->doc_date)),
			'@Moneda'			 => (self::$tipo == 'P') ? 'XXX' : self::getMoneda(strtoupper(trim($data->currency))),
			'@TipoDeComprobante' => self::$tipo,
			'@NoCertificado'	 => $numCertificado['cert'],
			'@LugarExpedicion'	 => $data->expediter_faddress_zipcode,
		];
		if($nodos['@Moneda'] != 'MXN' && $nodos['@Moneda'] != 'XXX'){
			$nodos['@TipoCambio'] = number_format($data->currency_exchange,2,'.','');
		}
		return $nodos;
	}


	// protected static function buildInvoice(){}
	// protected static function buildCreditNote(){}
	// protected static function buildTransferInvoice(){}
	// protected static function buildPaymentInvoice(){}

	protected static function getInvoiceSerialNum($type) {
	    $doc_serial = "";
	    $doc_num = 0;
	    $doc_name_available = [
	    	'ingreso' 	=> 'invoices_doc_',
	    	'egreso'  	=> 'creditnote_doc_',
	    	'traslado'	=> 'transfer_doc_',
	    	'pago'		=> 'payment_doc_'
	   	];
	    $doc_name = $doc_name_available[$type];

	    $query = "SELECT ID_vars, VValue FROM sl_vars WHERE VName = '{$doc_name}num' FOR UPDATE";
	    $res_num = self::$conn->query($query)->fetch(\PDO::FETCH_OBJ);
	    $doc_num = $res_num->VValue;
		
		$query = "SELECT VValue FROM sl_vars WHERE VName = '{$doc_name}serial'";
	    $doc_serial = self::$conn->query($query)->fetch(\PDO::FETCH_OBJ)->VValue;
	    $id_invoices = self::$id_invoices;
	    
	    $query = "UPDATE cu_invoices set doc_serial = '$doc_serial', doc_num = '$doc_num' WHERE ID_invoices = '{$id_invoices}'";

	    MysqlBD::executeQuery($query);
	    
	    $new_num = $doc_num + 1;
	    
	    $query = "UPDATE sl_vars SET VValue='{$new_num}' WHERE ID_vars = '{$res_num->ID_vars}'";
	    
	    MysqlBD::executeQuery($query);


	    return [
	        'doc_serial' => $doc_serial,
	        'doc_num' => $doc_num,
	    ];

	}
}