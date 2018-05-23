<?php
	$server = "172.20.27.78";
	$user = "d2mow";
	$pswd = "jKSu2&&28GjngbKJSWH*(*289HK";
	$dbname = "direksys2_";
	// $server = "localhost";
	// $user = "direksysmx";
	// $pswd = "D01NksjIw283hsl";
	// $dbname = "pp_direksys2_";

	// Empresa (default e11)
	$e = ( isset($_GET["e"]) && !empty($_GET["e"]) ) ? (int)$_GET["e"] : 11;
	$dbname .= 'e'.$e;

	error_reporting(E_ALL);

	// Conexion
	$conex = new mysqli($server, $user, $pswd, $dbname);
	if ($conex->connect_errno) {
	    echo "ERROR: (" . $conex->connect_errno . ") " . $conex->connect_error;
	}
	
	$log = '';
	$log_sql = '';
	$errors = 0;
	
	// IDs Limite con Costo
	/*
	e11 : 8861
	e2 : 8242
	e3 : None
	e4 : 7891
	*/

	$log .= "===========================================================================<br />";
	$log .= "Conectado a <b>".$server."</b> :: BD => ".$dbname."<br />";
	$log .= "===========================================================================<br /><br />";
	
	$sql = "START TRANSACTION;";
	$log .= $sql.'<br /><br />';
	//$rslt = $conex->query($sql);

	//----------------------------------------------------------
	// Se genera el trans por cada sku	
	//----------------------------------------------------------
	$log .= '<br /><b>=====================================================================<br />';
	$log .= 'Carga de Costos para las Receipciones ya procesadas';
	$log .= '<br />=====================================================================</b><br />';

	//echo $log;
	$sql = "SELECT ID_wreceipts
				, ID_vendors
				, ID_purchaseorders
				, ID_exchangerates
				, `Status`
			FROM sl_wreceipts
			WHERE `Status`='Processed' AND `Type`='Warehouse Receipt'
			ORDER BY ID_wreceipts DESC 
			;";
	//$log .= $sql.'<br /><br />';

	$log .= '<table border="1" style="border-collapse: collapse;">';
	
	$rslt = $conex->query($sql);
	while( $fila = $rslt->fetch_assoc() ){


		// Se obtiene el ID_products_trans inicial
		$sql = "SELECT sl_purchaseorders_wreceipts.ID_purchaseorders_wreceipts
					, sl_purchaseorders_wreceipts.ID_purchaseorders_items
					, sl_purchaseorders_wreceipts.ID_wreceipts_items
					, sl_purchaseorders_wreceipts.ID_products
					, sl_purchaseorders_wreceipts.ID_warehouses
					, sl_purchaseorders_wreceipts.Quantity
					, sl_purchaseorders_items.Price
					, (sl_purchaseorders_wreceipts.Quantity * sl_purchaseorders_items.Price) line_amt
				FROM sl_purchaseorders_wreceipts
					INNER JOIN sl_wreceipts_items ON sl_purchaseorders_wreceipts.ID_wreceipts_items = sl_wreceipts_items.ID_wreceipts_items
					INNER JOIN sl_purchaseorders_items ON sl_purchaseorders_wreceipts.ID_purchaseorders_items = sl_purchaseorders_items.ID_purchaseorders_items
				WHERE sl_wreceipts_items.ID_wreceipts = ".$fila['ID_wreceipts']." AND sl_purchaseorders_wreceipts.Cost = 0;";
		$rslt_po_wr_items = $conex->query($sql);

		if( $rslt_po_wr_items->num_rows > 0 ){

			$log .= '	<tr>';
			$log .= '		<td colspan="16" style="background-color: silver; text-align: center; font-weight: bold;">ID WReceipts: '.$fila['ID_wreceipts'].' <- PO: '.$fila['ID_purchaseorders'].'</td>';
			$log .= '	</tr>';

			$log .= '	<tr>';
			$log .= '		<td style="text-align: center; font-weight: bold;">ID Products</td>';
			$log .= '		<td style="text-align: center; font-weight: bold;">Price</td>';
			$log .= '		<td style="text-align: center; font-weight: bold;">Quantity</td>';
			$log .= '		<td style="text-align: center; font-weight: bold;">Exchange Rate</td>';
			$log .= '		<td style="text-align: center; font-weight: bold;">Part. Cost</td>';
			$log .= '		<td style="text-align: center; font-weight: bold;">Adj. Calc.</td>';
			$log .= '		<td style="text-align: center; font-weight: bold;">Cost Adj</td>';
			$log .= '		<td style="text-align: center; font-weight: bold;">Cost</td>';
			$log .= '		<td style="text-align: center; font-weight: bold;"> VS </td>';
			$log .= '		<td style="text-align: center; font-weight: bold;">ID Trans.</td>';
			$log .= '		<td style="text-align: center; font-weight: bold;">ID Products</td>';
			$log .= '		<td style="text-align: center; font-weight: bold;">Quantity</td>';
			$log .= '		<td style="text-align: center; font-weight: bold;">Cost</td>';
			$log .= '		<td style="text-align: center; font-weight: bold;">Cost Adj</td>';
			$log .= '		<td style="text-align: center; font-weight: bold;">Cost AVG</td>';
			$log .= '	</tr>';
			
			// Se obtiene el monto total de la recepcion
			$sql = "SELECT SUM(sl_purchaseorders_wreceipts.Quantity * sl_purchaseorders_items.Price) AmtWR
					FROM sl_purchaseorders_wreceipts
						INNER JOIN sl_wreceipts_items ON sl_purchaseorders_wreceipts.ID_wreceipts_items = sl_wreceipts_items.ID_wreceipts_items
						INNER JOIN sl_purchaseorders_items ON sl_purchaseorders_wreceipts.ID_purchaseorders_items = sl_purchaseorders_items.ID_purchaseorders_items	
					WHERE sl_wreceipts_items.ID_wreceipts = ".$fila['ID_wreceipts']."
					GROUP BY sl_wreceipts_items.ID_wreceipts;";
			$rslt_amt_wr = $conex->query($sql);
			$data_amt_wr = $rslt_amt_wr->fetch_assoc();
			$total_amt_wr = $data_amt_wr['AmtWR'];

			// Se obtiene el monto total de los GA
			$rslt_po_adj = $conex->query("SELECT IFNULL(SUM(Total-Tax), 0) AmtAdj FROM sl_purchaseorders_adj WHERE ID_purchaseorders = ".$fila['ID_purchaseorders']." AND ID_wreceipts = ".$fila['ID_wreceipts']." AND InCOGS = 'Yes';");
			$data_po_adj = $rslt_po_adj->fetch_assoc();
			$total_amt_adj = $data_po_adj['AmtAdj'];

			while( $po_wr_items = $rslt_po_wr_items->fetch_assoc() ){
				
				// Se obtiene el tipo de cambio
				if( !empty($fila['ID_exchangerates']) ){
					$rslt_ex_rt = $conex->query("SELECT exchange_rate FROM sl_exchangerates WHERE ID_exchangerates = ".$fila['ID_exchangerates'].";");
					$data_ex_rate = $rslt_ex_rt->fetch_assoc();
					$exchange_rate = $data_ex_rate['exchange_rate'];
				}else{
					$exchange_rate = 1;
				}

				// Se calcula el costo unitario
				$cost = round($po_wr_items['Price'] * $exchange_rate, 3);

				// Se calcula el monto de los gastos de aterrizaje
				$cost_adj = 0;
				$form_cal_adj = '';
				if( $total_amt_adj > 0 ){
					$pct_adj = $po_wr_items['line_amt'] / $total_amt_wr;
					$cost_adj = round(($total_amt_adj * $pct_adj * $exchange_rate) / $po_wr_items['Quantity'], 3);
					$form_cal_adj = "($total_amt_adj * $pct_adj * $exchange_rate) / ".$po_wr_items['Quantity'];
				}

				// Costo + GA
				$this_cost = $cost + $cost_adj;

				// Se obtiene los registros en sl_skus_trans de la recepción
				$sql = "SELECT sl_skus_trans.ID_products
							, sl_skus_trans.Quantity
							, sl_skus_trans.Cost
							, sl_skus_trans.Cost_Adj
							, sl_skus_trans.ID_trs
							, sl_skus_trans.Date
							, sl_skus_trans.Cost_Avg
						FROM sl_skus_trans
						WHERE sl_skus_trans.`Type` = 'Purchase' 
							AND ID_trs = ".$fila['ID_wreceipts']."
							AND ID_products = ".$po_wr_items['ID_products'].";";
				$rslt_trans = $conex->query($sql);
				$data_trans = $rslt_trans->fetch_assoc();

				$sty_diff_cost = '';
				if( !empty($data_trans['ID_products']) && abs(round($data_trans['Cost'],3) - round($this_cost, 3)) > 0 && $data_trans['Cost'] > 0 ){
					$sty_diff_cost = 'background-color: #F3E2A9;';
				}

				// Impresion de datos
				$log .= '<tr style="'.$sty_diff_cost.'">';
				$log .= '	<td style="text-align: center;">'.$po_wr_items['ID_products'].'</td>';
				$log .= '	<td style="text-align: right;">'.$po_wr_items['Price'].'</td>';
				$log .= '	<td style="text-align: right;">'.$po_wr_items['Quantity'].'</td>';
				$log .= '	<td style="text-align: right;">'.$exchange_rate.'</td>';
				$log .= '	<td style="text-align: right;">'.$cost.'</td>';
				$log .= '	<td style="text-align: center;">'.$form_cal_adj.'</td>';
				$log .= '	<td style="text-align: right;">'.$cost_adj.'</td>';
				$log .= '	<td style="text-align: right; color: blue;">'.$this_cost.'</td>';
				$log .= '	<td style="text-align: center;"> :: </td>';
				$log .= '	<td style="text-align: center;">'.$data_trans['ID_trs'].'</td>';
				$log .= '	<td style="text-align: center;">'.$data_trans['ID_products'].'</td>';
				$log .= '	<td style="text-align: right;">'.$data_trans['Quantity'].'</td>';
				$color = ( $data_trans['Cost'] == 0 ) ? 'red' : 'blue';
				$log .= '	<td style="text-align: right; color: '.$color.';">'.$data_trans['Cost'].'</td>';
				$log .= '	<td style="text-align: right;">'.$data_trans['Cost_Adj'].'</td>';
				$log .= '	<td style="text-align: right;">'.$data_trans['Cost_Avg'].'</td>';				
				$log .= '</tr>';

				// Update Cost				
				$log_sql .= "UPDATE sl_purchaseorders_wreceipts SET Cost = ".$this_cost.", Cost_Adj = ".$cost_adj.", exchange_rate = ".$exchange_rate."	WHERE ID_purchaseorders_wreceipts = ".$po_wr_items['ID_purchaseorders_wreceipts'].";\n";
			}
		}
	}
	$log .= '</table><br />';
	echo $log;

	$file = fopen("load_cost_wreceipts_e".$e.".sql", "w");
	fwrite($file, $log_sql);
	fclose($file);

	$conex->close();

?>