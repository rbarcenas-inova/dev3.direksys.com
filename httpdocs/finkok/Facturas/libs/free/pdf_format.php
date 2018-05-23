<?php
// header('Content-Type: text/html; charset=ISO-8859-1');
// require_once ROOT_FOLDER.'/../../phplibs/fpdf17/fpdf.custom.php';
// require_once ROOT_FOLDER.'/../../phplibs/qrcode/qrcode.class.php';
// require_once ROOT_FOLDER.'/../../../../cfdi/common/php/letras.php';

function pdf($id_invoices,$xml_string='',$type="show",$invoiceInfo = array(), $tt){
	if($xml_string == '')
		return '';
	$conn = MysqlBD::getConexion();
	$notasRS = $conn->query("SELECT * FROM cu_invoices_notes where ID_invoices= $id_invoices and type='ToPrint'")->fetchAll(PDO::FETCH_OBJ);
	$datosEnvio = $conn->query("Select 
		*
		from cu_invoices 
		inner join cu_invoices_lines on cu_invoices.ID_invoices = cu_invoices_lines.ID_invoices
		where id_invoices = $id_invoices group by ID_invoices limit 1")->fetch(PDO::FETCH_OBJ);
	$
	$notas = '';
	foreach ($notasRS as $key => $value) {
		$notas.= $value->Notes." \n ";
	}
	
	$invoiceI = MysqlBD::consultarTablaF('cu_invoices',array(),array('ID_invoices'=>$invoices->ID_invoices));
	$notas = str_split(strtoupper(limpiar($notas)), 65);
	// Parse XML
	$parser = new cfdiMx\Parser($xml_string);
	$xml = $parser->jsonSerialize();
	// Recepción de valores por bloques
	$xml_factura_datgral	= array_replace($xml["Comprobante"]["@atributos"]);
	$xml_factura_emisor		= array_replace($xml["Comprobante"]["Emisor"]);
	$xml_factura_cliente	= array_replace($xml["Comprobante"]["Receptor"]);
	$xml_factura_conceptos	= array_replace($xml["Comprobante"]["Conceptos"]);
	$xml_factura_impuestos	= array_replace($xml["Comprobante"]["Impuestos"]);
	$xml_factura_complement	= array_replace($xml["Comprobante"]["Complemento"]);
	$xml_factura_addenda	= array_replace($xml["Comprobante"]["Addenda"]["ECFD"]["Documento"]["Encabezado"]);

	// Datos del Emisor
	$factura['empresa_nombre']		= strtoupper($xml_factura_emisor["@atributos"]["nombre"]);
	$factura['empresa_rfc']			= strtoupper($xml_factura_emisor["@atributos"]["rfc"]);
	$factura['empresa_domiclio']	= strtoupper($xml_factura_emisor["DomicilioFiscal"]["@atributos"]["calle"])." ".$xml_factura_emisor["DomicilioFiscal"]["@atributos"]["noExterior"]." ".$xml_factura_emisor["DomicilioFiscal"]["@atributos"]["noInterior"];
	$factura['empresa_domiclio']	.= strtoupper(" Col. ".$xml_factura_emisor["DomicilioFiscal"]["@atributos"]["colonia"]);
	$factura['empresa_domiclio']	.= strtoupper(" Del. ".$xml_factura_emisor["DomicilioFiscal"]["@atributos"]["municipio"]).", ";	
	$factura['empresa_domiclio']	.= strtoupper($xml_factura_emisor["DomicilioFiscal"]["@atributos"]["pais"]. ", ".$xml_factura_emisor["DomicilioFiscal"]["@atributos"]["estado"] ." ").$xml_factura_emisor["DomicilioFiscal"]["@atributos"]["codigoPostal"];	
	$factura['num_serie_sat']		= $xml_factura_complement["TimbreFiscalDigital"]["@atributos"]["noCertificadoSAT"];
	$factura['num_serie_emisor']	= $xml_factura_datgral["noCertificado"];
	// Datos del Cliente
	$factura['cliente_nombre']		= strtoupper($xml_factura_cliente["@atributos"]["nombre"]);
	$factura['cliente_rfc']			= strtoupper($xml_factura_cliente["@atributos"]["rfc"]);
	$factura['cliente_domicilio']	= strtoupper($xml_factura_cliente["DomicilioFiscal"]["@atributos"]["calle"])." ".$xml_factura_cliente["DomicilioFiscal"]["@atributos"]["noExterior"]." ".$xml_factura_cliente["DomicilioFiscal"]["@atributos"]["noInterior"];
	$factura['cliente_domicilio']	.= strtoupper(" Col. ".$xml_factura_cliente["DomicilioFiscal"]["@atributos"]["colonia"]).", ";
	$factura['cliente_domicilio']	.= strtoupper(" Del./Mpio. ".$xml_factura_cliente["DomicilioFiscal"]["@atributos"]["municipio"])."\n";	
	$factura['cliente_domicilio']	.= strtoupper($xml_factura_cliente["DomicilioFiscal"]["@atributos"]["estado"].", C.P. ").$xml_factura_cliente["DomicilioFiscal"]["@atributos"]["codigoPostal"];	
	// Datos emision
	$factura['fecha_hora_emision']	= $xml_factura_datgral["fecha"];
	$factura['fecha_hora_certif']	= $xml_factura_complement["TimbreFiscalDigital"]["@atributos"]["FechaTimbrado"];
	$factura['folio']				= $xml_factura_datgral["serie"]."-".$xml_factura_datgral["folio"];
	$factura['folio_fiscal']		= $xml_factura_complement["TimbreFiscalDigital"]["@atributos"]["UUID"];
	$factura['lugar_expedicion']	= strtoupper($xml_factura_datgral["LugarExpedicion"]);
	$factura['tipo_comprobante']	= strtoupper($xml_factura_datgral["TipoDeComprobante"]);
	// Datos entrega
	$factura['recibo_entrega']		= "";
	$factura['fecha_entrega']		= "";
	$factura['entrega_lugar']		= strtoupper($xml_factura_addenda["ExReceptor"]["LugarRecep"]["Calle"]." ".$xml_factura_addenda["ExReceptor"]["LugarRecep"]["NroExterior"]);
	$factura['entrega_lugar']		.= strtoupper(" Col. ".$xml_factura_addenda["ExReceptor"]["LugarRecep"]["Colonia"]);
	$factura['entrega_lugar']		.= strtoupper(" Del./Mpio. ".$xml_factura_addenda["ExReceptor"]["LugarRecep"]["Municipio"])." ";
	$factura['entrega_lugar']		.= strtoupper($xml_factura_addenda["ExReceptor"]["LugarRecep"]["Estado"].", C.P. ").$xml_factura_addenda["ExReceptor"]["LugarRecep"]["CodigoPostal"];
	$factura['observaciones']		= $notas;

	$factura['num_orden_compra']	= $datosEnvio->ID_orders_alias;
	$factura['num_pedido']			= $datosEnvio->id_orders;
	$factura['datos_entrega'] 		= strtoupper( limpiar("$datosEnvio->customer_shpaddress_street $datosEnvio->customer_shpaddress_num $datosEnvio->customer_shpaddress_num2 Col. $datosEnvio->customer_shpaddress_urbanization Del./Mpio. $datosEnvio->customer_shpaddress_city, $datosEnvio->customer_shpaddress_state $datosEnvio->customer_shpaddress_country, C.P. $datosEnvio->customer_shpaddress_zipcode ") );
	$factura['num_contrarecibo']	= "";
	$factura['dias_credito']		= $datosEnvio->credit_days;
	$factura['condiciones']			= $datosEnvio->conditions;
	$factura['lote']				= "";
	$factura['forma_pago']			= strtoupper($xml_factura_datgral["metodoDePago"]);
	$factura['num_cuenta']			= isset($xml_factura_datgral["NumCtaPago"]) && $xml_factura_datgral["NumCtaPago"] != '' ? strtoupper($xml_factura_datgral["NumCtaPago"]) : 'NO IDENTIFICADO';
	$factura['regimen_fiscal']		= $xml_factura_emisor["RegimenFiscal"]["@atributos"]["Regimen"];
	$factura['cadena_original']		= "||";
	$factura['cadena_original']		.= number_format($xml_factura_complement["TimbreFiscalDigital"]["@atributos"]["version"],1)."|";
	$factura['cadena_original']		.= $xml_factura_complement["TimbreFiscalDigital"]["@atributos"]["UUID"]."|";
	$factura['cadena_original']		.= $xml_factura_complement["TimbreFiscalDigital"]["@atributos"]["FechaTimbrado"]."|";
	$factura['cadena_original']		.= $xml_factura_complement["TimbreFiscalDigital"]["@atributos"]["selloCFD"]."|";
	$factura['cadena_original']		.= $xml_factura_complement["TimbreFiscalDigital"]["@atributos"]["noCertificadoSAT"];
	$factura['cadena_original']		.= "||";	
	$factura['sello_digital']		= $xml_factura_complement["TimbreFiscalDigital"]["@atributos"]["selloCFD"];
	$factura['sello_sat']			= $xml_factura_complement["TimbreFiscalDigital"]["@atributos"]["selloSAT"];
	// Productos
	$productos = array_replace($xml["Comprobante"]["Conceptos"]["Concepto"]["@atributos"]);

	// Totales
	$totales['subtotal']	= $xml_factura_datgral["subtotal"];
	$totales['descuento']	= $xml_factura_datgral["descuento"];
	$totales['total']		= $xml_factura_datgral["total"];
	$totales['moneda']		= $xml_factura_datgral["moneda"];
	$totales['tipo_cambio']	= $xml_factura_datgral["TipoCambio"];
	// Importe con letras
	$letras = new EnLetras();
	$factura['monto_letra']	= utf8_decode($letras->ValorEnLetras($totales['total'], $totales['moneda']));
	// Impuestos
	$impuestos = array_replace($xml["Comprobante"]["Impuestos"]);

	$pdf = new PDF('P', 'mm', 'letter');
	$pdf->StartPageGroup();
	$pdf->SetMargins(10, 5, 5);
	$pdf->SetAutoPageBreak(true, 10);

	// Página inicial
	$pdf->AddPage();

	$pagina_altura = 260;

	// Encabezado y datos generales de la factura
	invoice_header($pdf, $factura);
		
	//-----------------------------------------------------------//
	//-- Bloque de productos
	//-----------------------------------------------------------//
	$x = 10;
	$y = 80;
	$descrip_x = 117;
	$params['x'] = $x;
	$params['y'] = $y;	
	$params['descrip_x'] = $descrip_x;

	// Encabezados dela tabla
	$y = products_header($pdf, $params);
		
	$y_alto = 5;

	$pdf->SetFont('Arial', '', 6.5);
	$pdf->SetFillColor(215);

	$cont = 1;
	$sum_subtotal = 0;
	$sum_descuentos = 0;
	$sum_cargos = 0;
	foreach ($productos as $prod) {
		$fn_cell = 'Cell';
		$fila_altura = 5;
		$blq_aduanas_altura = 0;

		// Valida el tamaño de la descripcion del producto		
		$descrip_tam_x = $pdf->GetStringWidth($prod['descripcion']);
		if( $descrip_tam_x > $descrip_x ){
			$fn_cell = 'MultiCell';
			$y_alto = 4;
			$num_filas = ($descrip_tam_x / $descrip_x);
			$num_filas = ($descrip_tam_x % $descrip_x > 0) ? $num_filas + 1 : $num_filas;
			$fila_altura = (int)($num_filas * $y_alto);
		}else{
			$y_alto = 5;
		}

		// Controla la impresión de datos aduanales
		$total_aduanas = count($prod['aduanas']);
		$blq_aduanas_altura = 4 * $total_aduanas;
		$lineas_aduanas_disponibles = $total_aduanas;
		$altura_restante = 0;
		if( ($blq_aduanas_altura + $y) >= $pagina_altura ){
			$altura_restante = $pagina_altura - $y;
			$lineas_aduanas_disponibles = (int)($altura_restante / 4);
		}

		$fila_altura += $lineas_aduanas_disponibles * 4;

		// controla es estilo cebra en el listado
		$fill_cell = ( $cont % 2 == 0 ) ? true : false;

		$pdf->SetFont('Arial', '', 6.5);
		
		// Fila de relleno
		$pdf->SetXY($x, $y);
		$pdf->Cell(195, $fila_altura, '', 0, 0, 'L', $fill_cell);
		$fila_altura -= $lineas_aduanas_disponibles * 4;

		// Impresion de los datos				
		$pdf->SetXY($x, $y);
		$pdf->Cell(18, $y_alto, number_format($prod['cantidad'],2), 0, 0, 'L', $fill_cell);
		$pdf->SetXY($x+18, $y);
		$pdf->Cell(12, $y_alto, $prod['unidad'], 0, 0, 'L', $fill_cell);		
		$pdf->SetXY($x+18+12, $y);
		$pdf->$fn_cell($descrip_x, $y_alto, $prod['descripcion']);
		$pdf->SetXY($x+18+12+$descrip_x, $y);
		$pdf->Cell(23, $y_alto, '$ '.number_format($prod['valorUnitario'], 2, '.', ','), 0, 0, 'R', $fill_cell);
		$pdf->SetXY($x+18+12+$descrip_x+23, $y);
		$pdf->Cell(25, $y_alto, '$ '.number_format($prod['importe'], 2, '.', ','), 0, 0, 'R', $fill_cell);
		// Impresion de datos aduanales
		if(isset($prod['aduanas'])){
			$cont_aduanas = 1;
			foreach ($prod['aduanas'] as $aduana) {
				$fila_altura += 4;				
				
				$aduana = $aduana['@attributes'];
				$pdf->SetFont('Arial', '', 5.5);
				$pdf->SetXY($x+18+12, $y+($fila_altura-4));
				$pdf->Cell(30, 4, 'PED.: '.$aduana['numero'], 0, 0, 'L', $fill_cell);
				$pdf->SetXY($x+18+12+30, $y+($fila_altura-4));
				$pdf->Cell(28, 4, 'FECHA: '.$aduana['fecha'], 0, 0, 'L', $fill_cell);
				$pdf->SetXY($x+18+12+30+28, $y+($fila_altura-4));
				$pdf->Cell(57, 4, $aduana['aduana'], 0, 0, 'L', $fill_cell);
				$pdf->SetFont('Arial', '', 6.5);				
				
				if( $cont_aduanas >= $lineas_aduanas_disponibles && ($altura_restante > 0 && $altura_restante < $blq_aduanas_altura) ){
					// Linea final de la tabla(en esta página)
					$y += $fila_altura;
					$pdf->Line($x, $y, $x+195, $y);
					$pdf->Line($x, $y-$fila_altura, $x, $y);
					$pdf->Line($x+18, $y-$fila_altura, $x+18, $y);
					$pdf->Line($x+18+12, $y-$fila_altura, $x+18+12, $y);
					$pdf->Line($x+18+12+$descrip_x, $y-$fila_altura, $x+18+12+$descrip_x, $y);
					$pdf->Line($x+18+12+$descrip_x+23, $y-$fila_altura, $x+18+12+$descrip_x+23, $y);
					$pdf->Line($x+18+12+$descrip_x+23+25, $y-$fila_altura, $x+18+12+$descrip_x+23+25, $y);
					// Nueva página
					$pdf->AddPage();
					invoice_header($pdf, $factura);
					$pdf->SetFillColor(215);
					$y = products_header($pdf, $params);
					$fila_altura = ($total_aduanas - $lineas_aduanas_disponibles) * 4;

					// Fila de relleno
					$pdf->SetXY($x, $y);
					$pdf->Cell(195, $fila_altura, '', 0, 0, 'L', $fill_cell);
					$fila_altura = 0;
					$cont_aduanas = 0;
					$lineas_aduanas_disponibles = $total_aduanas;
				}
				$cont_aduanas++;
			}
		}
		
		// Sumatorias
		$sum_subtotal += $prod['importe'];
		$sum_descuentos += 0;
		$sum_cargos += 0;

		// Lineas verticales
		$pdf->Line($x, $y, $x, $y+$fila_altura);
		$pdf->Line($x+18, $y, $x+18, $y+$fila_altura);
		$pdf->Line($x+18+12, $y, $x+18+12, $y+$fila_altura);
		$pdf->Line($x+18+12+$descrip_x, $y, $x+18+12+$descrip_x, $y+$fila_altura);
		$pdf->Line($x+18+12+$descrip_x+23, $y, $x+18+12+$descrip_x+23, $y+$fila_altura);
		$pdf->Line($x+18+12+$descrip_x+23+25, $y, $x+18+12+$descrip_x+23+25, $y+$fila_altura);

		$y += $fila_altura;
		$cont++;

		// Nueva página
		if( $y >= $pagina_altura && $cont < count($productos)){
			// Linea final de la tabla(en esta página)
			$pdf->Line($x, $y, $x+195, $y);

			$pdf->AddPage();		
			invoice_header($pdf, $factura);
			$pdf->SetFillColor(215);
			$y = products_header($pdf, $params);
		}
	}
	// Controla la estética de la lista de productos en caso de que estos sean pocos
	if( $y < 165 ){
		$faltante = 165 - $y;

		$pdf->Line($x, $y, $x, $y+$faltante);
		$pdf->Line($x+18, $y, $x+18, $y+$faltante);
		$pdf->Line($x+18+12, $y, $x+18+12, $y+$faltante);
		$pdf->Line($x+18+12+$descrip_x, $y, $x+18+12+$descrip_x, $y+$faltante);
		$pdf->Line($x+18+12+$descrip_x+23, $y, $x+18+12+$descrip_x+23, $y+$faltante);
		$pdf->Line($x+18+12+$descrip_x+23+25, $y, $x+18+12+$descrip_x+23+25, $y+$faltante);

		$y += $faltante;
	}
	// Linea final de la tabla
	$pdf->Line($x, $y, $x+195, $y);
	$y += 0.8;

	// Nueva página
	if( $y >= 245 ){
		$pdf->AddPage();
		invoice_header($pdf, $factura);
		$y = 70;
	}

	//-----------------------------------------------------------//
	//-- Resumen de totales
	//-----------------------------------------------------------//
	$pdf->Rect($x, $y, 195, 26.5);
	$pdf->Line($x+147, $y, $x+147, $y+26.5);
	$pdf->Line($x+170, $y, $x+170, $y+26.5);

	$pdf->SetFont('Arial', '', 6.5);
	$pdf->SetXY($x, $y);
	$pdf->Cell(150, 5, $factura['monto_letra']);
	// Subtotales
	$pdf->SetXY($x+150, $y);
	$pdf->Cell(20, 3.8, 'Subtotal:', 0, 0, 'R');
	$pdf->SetFont('Arial', 'B', 6.5);
	$pdf->SetXY($x+170, $y);
	$pdf->Cell(25, 3.8, '$ '.number_format($totales['subtotal'], 2, '.', ','), 0, 0, 'R');
	$y += 3.8;
	$pdf->SetFont('Arial', '', 6.5);
	$pdf->SetXY($x+150, $y);
	$pdf->Cell(20, 3.8, 'Total Descuentos:', 0, 0, 'R');
	$pdf->SetFont('Arial', 'B', 6.5);
	$pdf->SetXY($x+170, $y);
	$pdf->Cell(25, 3.8, '$ '.number_format($totales['descuento'], 2, '.', ','), 0, 0, 'R');
	$y += 3.8;
	$pdf->SetFont('Arial', '', 6.5);
	$pdf->SetXY($x+150, $y);
	$pdf->Cell(20, 3.8, 'Total Cargos:', 0, 0, 'R');
	$pdf->SetFont('Arial', 'B', 6.5);
	$pdf->SetXY($x+170, $y);
	$pdf->Cell(25, 3.8, '$ '.number_format($sum_cargos, 2, '.', ','), 0, 0, 'R');
	$y += 3.8;
	$subtotal_general = ($totales['subtotal'] + $sum_cargos - $totales['descuento']);
	$pdf->SetFont('Arial', '', 6.5);
	$pdf->SetXY($x+150, $y);
	$pdf->Cell(20, 3.8, 'Subtotal:', 0, 0, 'R');
	$pdf->SetFont('Arial', 'B', 6.5);
	$pdf->SetXY($x+170, $y);
	$pdf->Cell(25, 3.8, '$ '.number_format($subtotal_general, 2, '.', ','), 0, 0, 'R');
	$y += 3.8;
	// Impuestos	
	foreach( $impuestos["Traslados"]["Traslado"]["@atributos"] As $impuesto ){
		$pdf->SetFont('Arial', '', 6.5);
		$pdf->SetXY($x+150, $y);
		$pdf->Cell(20, 3.8, $impuesto["impuesto"].' '.$impuesto["tasa"].'%:', 0, 0, 'R');
		$pdf->SetFont('Arial', 'B', 6.5);
		$pdf->SetXY($x+170, $y);
		$pdf->Cell(25, 3.8, '$ '.number_format($impuesto["importe"], 2, '.', ','), 0, 0, 'R');
		$y += 3.8;
	}
	if( count($impuestos["Traslados"]["Traslado"]["@atributos"]) == 1 ){
		$pdf->SetFont('Arial', '', 6.5);
		$pdf->SetXY($x+150, $y);
		$pdf->Cell(20, 3.8, 'IVA 0%:', 0, 0, 'R');
		$pdf->SetFont('Arial', 'B', 6.5);
		$pdf->SetXY($x+170, $y);
		$pdf->Cell(25, 3.8, '$ 0.00', 0, 0, 'R');
		$y += 3.8;
	}
	// Total general
	$pdf->SetFont('Arial', '', 6.5);
	$pdf->SetXY($x+150, $y);
	$pdf->Cell(20, 3.8, 'Total:', 0, 0, 'R');
	$pdf->SetFont('Arial', 'B', 6.5);
	$pdf->SetXY($x+170, $y);
	$pdf->Cell(25, 3.8, '$ '.number_format($totales['total'], 2, '.', ','), 0, 0, 'R');
	$y += 7;

	//-----------------------------------------------------------//
	//-- Resumen de la factura y sellos fiscales
	//-----------------------------------------------------------//
	// Nueva página
	if( $y >= 252 ){
		$pdf->AddPage();
		invoice_header($pdf, $factura);
		$y = 70;
	}
	// Texto
	$pdf->SetFont('Arial', '', 7);
	$pdf->SetXY($x, $y);
	$pdf->Cell(95, 4, '****EFECTOS FISCALES AL PAGO****', 0, 0, 'C');
	$pdf->Cell(95, 4, utf8_decode('****PAGO EN UNA SOLA EXHIBICIÓN****'), 0, 0, 'C');
	$y += 10;

	// Nueva página
	if( $y >= 248 ){
		$pdf->AddPage();
		invoice_header($pdf, $factura);
		$y = 90;
	}

	// Datos del pago
	$pdf->SetXY($x, $y);
	$pdf->Cell(100, 4, utf8_decode('MÉTODO DE PAGO: '.$factura['forma_pago']));

	$pdf->SetXY($x+100, $y);
	$pdf->Cell(100, 4, utf8_decode('OBSERVACIONES: '));
	$pdf->SetXY($x+100, $y+4);
	$pdf->Cell(100, 4, utf8_decode(array_shift($factura['observaciones'])));
	$auxx = $y+8;
	foreach ($factura['observaciones'] as $key => $value) {
		$pdf->SetXY($x+100, $auxx);
		$pdf->Cell(100, 4, utf8_decode($value));
		$auxx+=4;
	}

	$y += 4;
	$pdf->SetXY($x, $y);
	$pdf->Cell(100, 4, utf8_decode('NÚMERO DE CUENTA: ').$factura['num_cuenta']);
	$y += 4;
	$pdf->SetXY($x, $y);
	$pdf->Cell(100, 4, 'REGIMEN FISCAL: '.$factura['regimen_fiscal']);
	$y += 15;

	// Nueva página
	if( $y >= 240 ){
		$pdf->AddPage();
		invoice_header($pdf, $factura);
		$y = 70;
	}

	// Cadena original
	$pdf->SetFont('Arial', 'B', 5.8);
	$pdf->SetXY($x, $y);
	$pdf->Cell(150, 3, utf8_decode('Cadena original del complemento de certificación digital del SAT'));
	$y += 3;
	$pdf->SetFont('Arial', '', 5.8);
	$pdf->SetXY($x, $y);
	$pdf->MultiCell(150, 3, $factura['cadena_original']);
	//$pdf->SetLineWidth(0.2);
	$y += 7;

	// Sello digital del CFDI y sello del SAT
	$pdf->SetFont('Arial', 'B', 5.8);
	$pdf->SetXY($x, $y);
	$pdf->Cell(100, 4, 'Sello digital del CFDI');
	$y += 4;
	$pdf->SetFont('Arial', '', 5.8);
	$pdf->SetXY($x, $y);
	$pdf->MultiCell(110, 3, $factura['sello_digital']);	
	$y += 7;

	$pdf->SetFont('Arial', 'B', 5.8);
	$pdf->SetXY($x, $y);
	$pdf->Cell(100, 4, 'Sello del SAT');
	$y += 4;
	$pdf->SetFont('Arial', '', 5.8);
	$pdf->SetXY($x, $y);
	$pdf->MultiCell(110, 3, $factura['sello_sat']);

	// Código QR
	$ary_total = explode(".", $totales['total']);
	$total_to_qr = (strlen($ary_total[0]) < 6) ? str_pad($ary_total[0], 6, '0', STR_PAD_LEFT) : $ary_total[0];
	$total_to_qr .= str_pad($ary_total[1], 6, '0', STR_PAD_LEFT);

	$msg = 're='.$factura['empresa_rfc'].'&rr='.$factura['cliente_rfc'].'&tt='.$total_to_qr.'&id='.$factura['folio_fiscal'];
	$err = 'M';
	$qrcode = new QRcode2(utf8_encode($msg), $err);
	$qrcode->disableBorder();
	$qrcode->displayFPDF($pdf, $x+157, $y-29, 37);	

	$y += 7;
	$pdf->SetFont('Arial', 'B', 5.8);
	$pdf->SetXY($x, $y);
	$pdf->Cell(100, 4, utf8_decode('ESTE DOCUMENTO ES UNA REPRESENTACIÓN IMPRESA DE UN CFDI'));

	// Salida del pdf
	if($type == 'show')
		$pdf->Output();
	elseif($type=='download')
		$pdf->Output("$factura[folio].pdf",'D');
	elseif($type=='string')
		return $pdf->Output("$factura[folio].pdf",'S');
}


/**
 *------------------------------------------------------------------------
 * FUNCIONES AUXILIARES
 *------------------------------------------------------------------------
 */

/**
 * Función que muestra el encabezado y los datos generales de la factura
 *
 */
function invoice_header($pdf, $factura){
	$x = 10;
	$y = 10;

	//-----------------------------------------------------------//
	//-- Encabezado
	//-----------------------------------------------------------//
	$x = 50;
	$y = 15;
	// Logo
	$pdf->Image(ROOT_FOLDER.'/../../sitimages/default/inbound-innova.png', 10, 15, 35, 13.7);
	// Datos de la empresa
	$pdf->SetFont('Arial', 'B', 9);
	$pdf->SetXY($x, $y);
	$pdf->Cell(90, 4, utf8_decode($factura['empresa_nombre']), 'L');
	$y += 4;
	$pdf->SetXY($x, $y);
	$pdf->Cell(60, 4, utf8_decode($factura['empresa_rfc']), 'L');
	$pdf->SetFont('Arial', '', 6);
	$y += 4;
	$pdf->SetXY($x, $y);	
	$pdf->MultiCell(78, 3, utf8_decode($factura['empresa_domiclio']), 'L');
	$y += 6;
	$pdf->SetXY($x, $y);	
	$pdf->Cell(70, 2, '', 'L');
	$y += 3;
		
	// Folios
	$fill_color_header = 50;
	$pdf->SetFillColor($fill_color_header);
	$x = 140;
	$y = 15;
	$pdf->RoundedRect($x, $y, 65, 7, 2, 'DF');
	$pdf->SetTextColor(255);
	$pdf->SetFont('Arial', '', 8);	
	$pdf->SetXY($x, $y);
	$pdf->Cell(65, 5, 'FOLIO FISCAL', 0, 0, 'C', false);
	$y += 5;
	$pdf->SetFillColor(255);
	$pdf->SetTextColor(0);
	$pdf->SetXY($x, $y);
	$pdf->Cell(65, 5, $factura['folio_fiscal'], 1, 0, 'C', true);
	$pdf->SetFillColor($fill_color_header);
	$y += 5;
	$pdf->SetTextColor(255);
	$pdf->SetFont('Arial', '', 8);	
	$pdf->SetXY($x, $y);
	$pdf->Cell(65, 4.5, 'FOLIO', 1, 0, 'C', true);
	$y += 4.5;
	$pdf->SetTextColor(0);
	$pdf->SetXY($x, $y);
	$pdf->Cell(65, 4.5, $factura['folio'], 1, 0, 'C');
	$y += 4.5;	
	$pdf->SetTextColor(255);
	$pdf->SetFont('Arial', '', 8);	
	$pdf->SetXY($x, $y);
	$pdf->Cell(65, 4.5, 'No de Serie del Certificado del SAT', 1, 0, 'C', true);
	$y += 4.5;
	$pdf->SetTextColor(0);
	$pdf->SetXY($x, $y);
	$pdf->Cell(65, 4.5, $factura['num_serie_sat'], 1, 0, 'C');
	$y += 4.5;
	$pdf->SetTextColor(255);
	$pdf->SetFont('Arial', '', 8);	
	$pdf->SetXY($x, $y);
	$pdf->Cell(65, 4.5, 'No de Serie del Certificado del Emisor', 1, 0, 'C', true);
	$y += 4.5;
	$pdf->SetTextColor(0);
	$pdf->SetXY($x, $y);
	$pdf->Cell(65, 4.5, $factura['num_serie_emisor'], 1, 0, 'C');
	$y += 4.5;
	$pdf->SetTextColor(255);
	$pdf->SetFont('Arial', '', 8);	
	$pdf->SetXY($x, $y);
	$pdf->Cell(32.5, 4.5, utf8_decode('EMISIÓN'), 1, 0, 'C', 'true');
	$pdf->Cell(32.5, 4.5, utf8_decode('CERTIFICACIÓN'), 1, 0, 'C', true);
	$y += 4.5;
	$pdf->SetTextColor(0);
	$pdf->SetXY($x, $y);
	$pdf->Cell(32.5, 4.5, $factura['fecha_hora_emision'], 1, 0, 'C');	
	$pdf->Cell(32.5, 4.5, $factura['fecha_hora_certif'], 1, 0, 'C');
	
	// Tipo de documento
	$x = 10;
	$y = 31;
	$pdf->SetFont('Arial', 'B', 9);
	$pdf->SetXY($x, $y);
	if( strtoupper($factura['tipo_comprobante']) == 'INGRESO' ){
		$pdf->Cell(130, 5, utf8_decode('FACTURA'), 'T', 0, 'C');
	}else{
		$pdf->Cell(130, 5, utf8_decode('NOTA DE CRÉDITO'), 'T', 0, 'C');
	}

	// Información del cliente y de la compra
	$x = 10;
	$y = 36;
	// Encabezados
	$pdf->SetFont('Arial', 'B', 8);
	$pdf->SetXY($x, $y);
	$pdf->Cell(70, 5, utf8_decode('INFORMACIÓN DEL CLIENTE'));
	$pdf->Cell(60, 5, utf8_decode('INFORMACIÓN DE COMPRA'));
	$y += 6;
	// Cliente
	$pdf->SetFont('Arial', '', 7);
	$pdf->SetXY($x+2, $y);
	$pdf->Cell(60, 3.5, utf8_decode($factura['cliente_nombre']));
	$y += 3.5;
	$pdf->SetXY($x+2, $y);
	$pdf->Cell(60, 3.5, utf8_decode($factura['cliente_rfc']));
	$y += 3.5;
	$pdf->SetXY($x+2, $y);
	$pdf->MultiCell(60, 3.5, utf8_decode($factura['cliente_domicilio']));
	$y += 10;

	// Datos de la compra
	$x = 82;
	$y = 40;
	$pdf->SetFont('Arial', '', 7);
	$pdf->SetXY($x, $y);
	$pdf->Cell(65, 3.5, 'No. Orden Compra: '.$factura['num_orden_compra']);
	$y += 3.7;
	$pdf->SetFont('Arial', '', 7);
	$pdf->SetXY($x, $y);
	$pdf->Cell(65, 3.5, 'No. Pedido CI: '.$factura['num_pedido']);
	$y += 3.7;
	$pdf->SetFont('Arial', '', 7);
	$pdf->SetXY($x, $y);
	$pdf->Cell(65, 3.5, 'No. Contrarecibo: '.$factura['num_contrarecibo']);
	$y += 3.7;
	$pdf->SetFont('Arial', '', 7);
	$pdf->SetXY($x, $y);
	$pdf->Cell(65, 3.5, utf8_decode('Días Credito: '.$factura['dias_credito']));
	$y += 3.7;$pdf->SetFont('Arial', '', 7);
	$pdf->SetXY($x, $y);
	$pdf->Cell(65, 3.5, 'Condiciones: '.utf8_decode($factura['condiciones']));
	$y += 3.5;
	$pdf->SetFont('Arial', '', 7);
	$pdf->SetXY($x, $y);
	$pdf->Cell(65, 3, 'Lote: '.$factura['lote']);
	
	// Info. adicional
	$x = 10;
	$y = 61;	
	$pdf->SetXY($x, $y);
	$pdf->Cell(195, 4, strtoupper(utf8_decode('Expedido en: '.$factura['lugar_expedicion'])), 0, 0, 'R');
	$y += 4;

	//  Info direccion de entrega
	$pdf->SetXY($x, $y);
	$pdf->SetFont('Arial', 'B', 7);
	$pdf->Cell(195, 5, utf8_decode('DIRECCIÓN DE ENVÍO'), 'T');
	$y += 4;
	// Cliente
	$pdf->SetFont('Arial', '', 7);
	$pdf->SetXY($x+2, $y);
	$pdf->SetXY($x+2, $y);
	$pdf->MultiCell(127, 3.5, utf8_decode(strtoupper($factura['datos_entrega'])));
	$y += 10;

}

/**
 * Función que muestra el encabezado del listado de productos
 *
 */

function products_header($pdf, $params){
	$x = $params['x'];
	$y = $params['y'];
	$descrip_x = $params['descrip_x'];

	$pdf->SetFont('Arial', 'B', 7);
	$pdf->SetXY($x, $y);
	$pdf->Cell(18, 4, 'CANTIDAD', 1, 0, 'C');
	$pdf->Cell(12, 4, 'UM', 1, 0, 'C');
	$pdf->Cell($descrip_x, 4, utf8_decode('DESCRIPCIÓN'), 1, 0, 'L');
	$pdf->Cell(23, 4, 'P. UNIT.', 1, 0, 'R');
	$pdf->Cell(25, 4, 'IMPORTE', 1, 0, 'R');
	$y += 4;

	return $y;
}

?>