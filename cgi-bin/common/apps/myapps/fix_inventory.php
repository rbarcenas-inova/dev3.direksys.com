<?php
	$server = "localhost";
	$dbname = "direksys2_e";
	$user = "direksysmx";
	$pswd = "D01NksjIw283hsl";

	// Empresa (default e11)
	$dbname .= ( isset($_GET["e"]) && !empty($_GET["e"]) ) ? (int)$_GET["e"] : 11;

	error_reporting(E_ALL);

	// Conexion
	$conex = new mysqli($server, $user, $pswd, $dbname);
	if ($conex->connect_errno) {
	    echo "ERROR: (" . $conex->connect_errno . ") " . $conex->connect_error;
	}

	$fecha = '2015-10-31';
	$conex->query("set @date=$fecha");

	
	$log = '';
	//---------------------------------------------------------
	// Recorrido de la tabla con saldos iniciales
	//---------------------------------------------------------
	$sql = "SELECT Product, SUM(Quantity) QtyIni, Avg_Cost
			FROM warehouse_20151031
			GROUP BY Product
			ORDER BY Product;";
	$rslt = $conex->query($sql);
	/*
	echo '<table style="min-width: 400px; border-spacing: 0;" border="1">';
	echo '<tr>';
	echo '	<th>SKU</th>';
	echo '	<th>Inv. Inicial</th>';
	echo '	<th>Cost_Avg Inicial</th>';
	echo '	<th>Inv. Fix</th>';
	echo '	<th>Cost. Fix</th>';
	echo '<tr>';
	*/

	while( $fila = $rslt->fetch_assoc() ){

		$log .= "<h3>ID_products: ".$fila["Product"]."</h3>\n";
		echo "<h3>ID_products: ".$fila["Product"]."</h3>\n";
		$log .= "<b>Inventario inicial: ".$fila["QtyIni"]."     Costo Inicial: ".$fila["Avg_Cost"]."</b>\n<br>";
		echo "<b>Inventario inicial: ".$fila["QtyIni"]."     Costo Inicial: ".$fila["Avg_Cost"]."</b>\n<br>";
		$data_fix = fix_inventory($fila["Product"], $fila["QtyIni"], $fila["Avg_Cost"]);
		/*
		echo '<tr>';
		echo '	<td style="text-align: center;">'.$fila["Product"].'</td>';
		echo '	<td style="text-align: right;">'.$fila["QtyIni"].'</td>';
		echo '	<td style="text-align: right;">'.$fila["Avg_Cost"].'</td>';
		echo '	<td style="text-align: right;">'.$data_fix["left_qty_total"].'</td>';
		echo '	<td style="text-align: right;">'.$data_fix["cost_avg"].'</td>';
		echo '<tr>';
		*/
		$log .= "-----------------------------------------------------------------------------------------\n<br>";
		echo "-----------------------------------------------------------------------------------------\n<br>";
	}

	//echo $log;

	//--------------------------------------------------------
	// Funciones
	//--------------------------------------------------------

	function fix_inventory($sku, $qty, $cost_avg){
		global $conex, $log;

		$sql_trs = "SELECT sl_skus_trans.ID_products, sl_skus_trans.tbl_name,sl_skus_trans.ID_trs
					FROM sl_skus_trans
					WHERE sl_skus_trans.Date>='2015-11-01' 
						AND tbl_name != 'sl_manifests' 
						AND NOT( sl_skus_trans.`Type` IN('Transfer In', 'Transfer Out') AND tbl_name='sl_orders' )
						AND ID_products = ".$sku."
					GROUP BY sl_skus_trans.ID_products, sl_skus_trans.tbl_name,sl_skus_trans.ID_trs
					ORDER BY sl_skus_trans.Date, sl_skus_trans.Time, sl_skus_trans.ID_products_trans;";			
		$rslt = $conex->query($sql_trs);

		if( !$rslt )
			return array("left_qty_total" => $qty, "cost_avg" => $cost_avg);

		while( $fila = $rslt->fetch_assoc() ){

			$log .= "<span style='color: blue;'>Transaccion: ".$fila["ID_trs"]."\t Tabla/Proceso: ".$fila["tbl_name"]."</span>\n<br>";
			echo "<span style='color: blue;'>Transaccion: ".$fila["ID_trs"]." \t Tabla/Proceso: ".$fila["tbl_name"]."</span>\n<br>";

			switch ($fila["tbl_name"]) {
				case 'sl_orders':
			 		$data_fix	= fix_orders_parts( $fila["ID_trs"], $sku, $qty, $cost_avg);

			 		$qty		= $data_fix["left_qty_total"];
			 		$cost_avg	= $data_fix["cost_avg"];
			 	break;
			 	case 'sl_parts_productions':
			 		$data_fix	= fix_parts_productions($fila["ID_trs"], $sku, $qty, $cost_avg);

			 		$qty		= $data_fix["left_qty_total"];
			 		$cost_avg	= $data_fix["cost_avg"];
			 	break;
			 	case 'sl_returns':
			 	case 'sl_creditmemos':
			 		$data_fix	= fix_returns($fila["tbl_name"], $fila["ID_trs"], $sku, $qty, $cost_avg);

			 		$qty		= $data_fix["left_qty_total"];
			 		$cost_avg	= $data_fix["cost_avg"];
			 	break;
			 	case 'sl_wreceipts':
			 		$data_fix	= fix_wreceipts($fila["ID_trs"], $sku, $qty, $cost_avg);

			 		$qty		= $data_fix["left_qty_total"];
			 		$cost_avg	= $data_fix["cost_avg"];
			 	break;
			 	case 'sl_purchaseorders':
			 		$data_fix	= fix_purchase_orders($fila["ID_trs"], $sku, $qty, $cost_avg);

			 		$qty		= $data_fix["left_qty_total"];
			 		$cost_avg	= $data_fix["cost_avg"];
			 	break;
			 	case 'sl_skustransfers':
			 		$data_fix	= fix_skustransfer($fila["ID_trs"], $sku, $qty, $cost_avg);

			 		$qty		= $data_fix["left_qty_total"];
			 		$cost_avg	= $data_fix["cost_avg"];
			 	break;
			}

			$log .= "=======> Inventario Resultante: ".$qty."\t &nbsp;&nbsp;&nbsp; Costo Promedio Resultante: ".$cost_avg."\n<br>";
			echo "=======> Inventario Resultante: ".$qty."\t &nbsp;&nbsp;&nbsp; Costo Promedio Resultante: ".$cost_avg."\n<br>";
		}
	
		return array("left_qty_total" => $qty, "cost_avg" => $cost_avg);
	}

	//----------------------------------------------------------------//
	/*Gil*/
	function fix_parts_productions($id_trs, $sku, $qty, $cost_avg){

		global $conex;

		$sql_chk = "SELECT sl_parts_productions.`Type`, In_out, SUM(Qty) Qty
					FROM sl_parts_productions
						INNER JOIN sl_parts_productions_items USING(ID_parts_productions)
					WHERE sl_parts_productions_items.ID_parts_productions=".$id_trs." 
						AND sl_parts_productions_items.ID_products=".$sku."
					GROUP BY sl_parts_productions_items.ID_products;";
		$rslt_chk = $conex->query($sql_chk);
		$data_chk = $rslt_chk->fetch_assoc();

		echo "Datos obtenidos: ";
		print_r($data_chk);
		echo "\n<br>";
		if( $data_chk["In_out"] == "in" ){
			// la trans. es una salida (OUT) y no afecta el costo promedio
			$qty -= $data_chk["Qty"];
		}else{
			// Implode
			if( $data_chk["Type"] == "Implode" ){
				$sql = "SELECT 
							sl_parts_productions_items.ID_products
							, sl_parts_productions_items.In_out
							, sl_parts_productions_items.Qty
						FROM sl_parts_productions_items 
						WHERE sl_parts_productions_items.ID_parts_productions = ".$id_trs."
							AND sl_parts_productions_items.In_out = 'in'
						ORDER BY sl_parts_productions_items.In_out;";
				$rslt = $conex->query($sql);
				
				$sum_cost = 0;
				while( $fila = $rslt->fetch_assoc() ){
					
					$sql_cost = "SELECT ID_products_trans, Cost
								FROM sl_skus_trans
								WHERE ID_trs=".$id_trs." 
									AND tbl_name = 'sl_parts_productions' 
									AND ID_products=".$fila["ID_products"].";";
					$rslt_cost = $conex->query($sql_cost);
					$data_cost = $rslt_cost->fetch_assoc();
					/*
					$sum_cost += $data_cost["Cost"];
					echo "Sumatoria costo: ".$sum_cost."\n<br>";
					*/
					//-- Alternativa 2
					
					$sql_wl = "SELECT SUM(Quantity) QtyIni, Avg_Cost
								FROM warehouse_20151031
								WHERE Product=".$fila["ID_products"].";";				
					$rslt_wl = $conex->query($sql_wl);
					$data_wl = $rslt_wl->fetch_assoc();
					//print_r($data_wl);
					//echo "\n<br>";
					$cost_ok = fix_cost_parts_prod($id_trs, $fila["ID_products"], $data_wl["QtyIni"], $data_wl["Avg_Cost"], $data_cost["ID_products_trans"]);
					//var_dump($cost_ok);
					$sum_cost += ($cost_ok != null) ? $cost_ok : $data_cost["Cost"];
					//var_dump($data_wl["Avg_Cost"]);
					echo "Sumatoria costo: ".$sum_cost."\n<br>";
					
				}

				$cost_avg = $sum_cost;
				$qty += $data_chk["Qty"];
			// Explode
			} else {
				$qty -= $data_chk["Qty"];
			}
		}
		
		$result = array("left_qty_total" => $qty, "cost_avg" => $cost_avg);

		return $result;
	}

	function fix_cost_parts_prod($id_trs, $sku, $qty, $cost_avg, $id_limit){
		global $conex;

		$sql_trs = "SELECT sl_skus_trans.ID_products, sl_skus_trans.tbl_name,sl_skus_trans.ID_trs
					FROM sl_skus_trans
					WHERE sl_skus_trans.Date>='2015-11-01' 
						AND tbl_name != 'sl_manifests' 
						AND NOT( sl_skus_trans.`Type` IN('Transfer In', 'Transfer Out') AND tbl_name='sl_orders' ) 
						AND ID_products = ".$sku."
						AND ID_products_trans < ".$id_limit." 
						AND ID_trs != ".$id_trs."
					GROUP BY sl_skus_trans.ID_products, sl_skus_trans.tbl_name,sl_skus_trans.ID_trs
					ORDER BY sl_skus_trans.Date, sl_skus_trans.Time, sl_skus_trans.ID_products_trans;";
		echo $sql_trs."\n<br>";
		$rslt = $conex->query($sql_trs);

		echo "Implode/Explode:: Obteniendo costo promedio de $sku\n<br>";

		if( !$rslt )
			return $cost_avg;

		while( $fila = $rslt->fetch_assoc() ){
			switch ($fila["tbl_name"]) {
				case 'sl_orders':
			 		$data_fix	= fix_orders_parts( $fila["ID_trs"], $sku, $qty, $cost_avg);

			 		$qty		= $data_fix["left_qty_total"];
			 		$cost_avg	= $data_fix["cost_avg"];
			 	break;
			 	case 'sl_parts_productions':
			 		$data_fix	= fix_parts_productions($fila["ID_trs"], $sku, $qty, $cost_avg);

			 		$qty		= $data_fix["left_qty_total"];
			 		$cost_avg	= $data_fix["cost_avg"];
			 	break;
			 	case 'sl_returns':
			 	case 'sl_creditmemos':
			 		$data_fix	= fix_returns($fila["tbl_name"], $fila["ID_trs"], $sku, $qty, $cost_avg);

			 		$qty		= $data_fix["left_qty_total"];
			 		$cost_avg	= $data_fix["cost_avg"];
			 	break;
			 	case 'sl_wreceipts':
			 	 	$data_fix	= fix_wreceipts($fila["ID_trs"], $sku, $qty, $cost_avg);

			 		$qty		= $data_fix["left_qty_total"];
			 		$cost_avg	= $data_fix["cost_avg"];
			 	break;
			 	case 'sl_purchaseorders':
			 		$data_fix	= fix_purchase_orders($fila["ID_trs"], $sku, $qty, $cost_avg);

			 		$qty		= $data_fix["left_qty_total"];
			 		$cost_avg	= $data_fix["cost_avg"];
			 	break;
			 	case 'sl_skustransfers':
			 		$data_fix	= fix_skustransfer($fila["ID_trs"], $sku, $qty, $cost_avg);

			 		$qty		= $data_fix["left_qty_total"];
			 		$cost_avg	= $data_fix["cost_avg"];
			 	break;
			}
		}

		return $cost_avg;
	}
	//----------------------------------------------------------------//

	/*Jon*/
	function fix_purchase_orders($ID_trs, $sku, $left_qty_total, $cost_avg) {

		global $conex;

		$sql = "SELECT pi.Qty thisQty
				FROM sl_purchaseorders p
				INNER JOIN sl_purchaseorders_items pi ON pi.ID_purchaseorders = p.ID_purchaseorders
				WHERE p.ID_purchaseorders = $ID_trs
				AND pi.ID_products = $sku;
				";
		$rslt = $conex->query($sql);

		$res = $rslt->fetch_assoc();

		$thisQty = $res['thisQty'];

		$result = array("left_qty_total" => $left_qty_total, "cost_avg" => $cost_avg);

		return $result;
	}

	/*Jon*/
	function fix_wreceipts($ID_trs, $sku, $left_qty_total, $cost_avg) {

		global $conex;

		$sql = "SELECT pi.Qty thisQty, pi.Price AS thisCost
				FROM sl_wreceipts w
				INNER JOIN sl_wreceipts_items wi ON wi.ID_wreceipts = w.ID_wreceipts
				INNER JOIN sl_purchaseorders_items pi ON pi.ID_purchaseorders = w.ID_purchaseorders
				INNER JOIN sl_purchaseorders po ON po.ID_purchaseorders = pi.ID_purchaseorders
				WHERE w.ID_wreceipts = $ID_trs 
				AND wi.ID_products = $sku ;
				";
		$rslt = $conex->query($sql);
		$res = $rslt->fetch_assoc();

		$thisQty = $res['thisQty'];
		$thisCost = $res['thisCost'];


		if( $cost_avg > 0 ){
			$total_cost = $thisQty * $thisCost;
			$total_cost_avg = $left_qty_total*$cost_avg;

			$cost_avg  = ($total_cost + $total_cost_avg) / ($left_qty_total + $thisQty);
			echo "Calculo: ($total_cost + $total_cost_avg) / ($left_qty_total + $thisQty)\n<br>";
		}else{
			$cost_avg = $thisCost;
			echo "Cost PO: ".$thisCost."\n<br>";
		}
		$cost_avg = number_format($cost_avg, 2, '.', '');

		$left_qty_total += $thisQty;

		$result = array("left_qty_total" => $left_qty_total, "cost_avg" => $cost_avg);

		return $result;
	}

	/*Fabian*/
	function fix_returns($table,$id_trs,$products,$total,$costo){
		global $conex;
		if($table == 'sl_returns'){
			$q = "select a.Quantity,a.Cost from sl_returns_upcs a inner join sl_returns b on a.ID_returns = b.ID_returns where b.date > @date and b.Status='Resolved' and a.id_returns=$id_trs and a.ID_parts= ".($products - 400000000);

		}elseif($table == 'sl_creditmemos'){
			$q = "select a.ID_products,a.Quantity,a.Cost from sl_creditmemos_products a inner join sl_creditmemos b on b.ID_creditmemos = a.ID_creditmemos where a.date > @date and ID_products = $products and a.id_creditmemos=$id_trs and b.Status='Applied'";
		}

		//echo "------------------ Fix Returns -------------------\n<br>";

		$response = array(
			'left_qty_total'=>$total,
			'cost_avg'=>$costo
		);
		if($conex->query($q)){
			$data = $conex->query($q)->fetch_object();
			echo "Datos obtenidos: ";
			print_r($data);
			echo "\n<br>";
			if( !is_null($data) ){
				$response['left_qty_total'] = $total+$data->Quantity;
				if($data->Cost > 0){
					$response['cost_avg'] = number_format ( ( ($costo*$total) + ($data->Quantity * $data->Cost) ) / ($total+$data->Quantity),2 );
				}else{
					$response['cost_avg'] = $costo;
				}
			}
		}
		//echo 'Datos resultantes: ';		
		//print_r($response);
		//echo "\n<br>";

		return $response;
	}

	/*Huitzi*/
	function fix_orders_parts($id_trs, $skus, $inventario_inicial, $cost_avg){
		global $conex;

		$sql 	= "	select o.id_orders, o.status, op.id_orders_products, id_products, p.id_orders_parts, sum(p.Quantity) Quantity, p.Cost from 
						(select id_orders, status from sl_orders where id_orders= '$id_trs') o
						left join (select id_orders_products, id_orders, id_products, related_id_products from sl_orders_products 
							       where date >= '2015-10-15' and Status='Active' and related_id_products = '$skus' ) op 
						on op.ID_orders = o.ID_orders
						left join (select * from sl_orders_parts where date >= '2015-10-15' and status='shipped') p 
						on op.id_orders_products=p.id_orders_products group by ID_parts";

		$rslt = $conex->query($sql);
		$registro = $rslt->fetch_assoc();
		
		$qty = $inventario_inicial - $registro['Quantity'];

		//echo "------------------ Fix Orders -------------------\n<br>";
		echo "||||    $inventario_inicial - $registro[Quantity] = $qty  |||| $cost_avg <br>";

		$result = array("left_qty_total" => $qty, "cost_avg" => $cost_avg);

		return $result;
	}

	/*Fabian*/
	function fix_skustransfer($id_trs,$products,$total,$costo){
		global $conex;
		$q = "select FromSku,ToSku,Qty from sl_skustransfers_items where id_skustransfers = $id_trs and (FromSku = $products or ToSku=$products);";
		$rs = $conex->query($q);
		$response = array(
			'left_qty_total'=>$total,
			'cost_avg'=>$costo
		);
		echo "------------------ Fix Skustransfer -------------------\n<br>";

		if($rs){
			$data = $rs->fetch_object();
			if(!is_null($data)){
				if($data->FromSku == $products){
					$response = array(
						'left_qty_total'=>$total-$data->Qty,
						'cost_avg'=>$costo
					);
					echo "SALIDA\n<br>";
				}else{
					$sql_cost = "SELECT ID_products_trans, Cost
							FROM sl_skus_trans
							WHERE ID_trs=".$id_trs." 
								AND tbl_name = 'sl_skustransfers' 
								AND ID_products=".$products.";";
					$limit = $conex->query($sql_cost)->fetch_object();
					$cost_avg_calc = fix_cost_skustransfer($id_trs,$data->FromSku,$total,$costo,$limit->ID_products_trans);
					$response = array(
						'left_qty_total'=>$total+$data->Qty,
						'cost_avg'=>is_null($cost_avg_calc) ? $costo : $cost_avg_calc
					);
					echo "<br>Datos Obtenidos qty: $data->Qty, costo : $response[cost_avg]<br>";
					echo "ENTRADA\n<br>";
				}
			}
		}
		return $response;
	}

	function fix_cost_skustransfer($id_trs,$sku,$qty,$cost_avg,$id_limit){
		global $conex;

		$sql_trs = "SELECT sl_skus_trans.ID_products, sl_skus_trans.tbl_name,sl_skus_trans.ID_trs
					FROM sl_skus_trans
					WHERE sl_skus_trans.Date>='2015-11-01' 
						AND tbl_name != 'sl_manifests' 
						AND NOT( sl_skus_trans.`Type` IN('Transfer In', 'Transfer Out') AND tbl_name='sl_orders' )
						AND ID_products = ".$sku."
						AND ID_products_trans < ".$id_limit." 
						AND ID_trs != ".$id_trs."
					GROUP BY sl_skus_trans.ID_products, sl_skus_trans.tbl_name,sl_skus_trans.ID_trs
					ORDER BY sl_skus_trans.Date, sl_skus_trans.Time, sl_skus_trans.ID_products_trans;";
		echo $sql_trs."\n<br>";
		$rslt = $conex->query($sql_trs);

		if( !$rslt )
			return $cost_avg;

		while( $fila = $rslt->fetch_assoc() ){
			switch ($fila["tbl_name"]) {
				case 'sl_orders':
			 		$data_fix	= fix_orders_parts( $fila["ID_trs"], $sku, $qty, $cost_avg);

			 		$qty		= $data_fix["left_qty_total"];
			 		$cost_avg	= $data_fix["cost_avg"];
			 	break;
			 	case 'sl_parts_productions':
			 		$data_fix	= fix_parts_productions($fila["ID_trs"], $sku, $qty, $cost_avg);

			 		$qty		= $data_fix["left_qty_total"];
			 		$cost_avg	= $data_fix["cost_avg"];
			 	break;
			 	case 'sl_returns':
			 	case 'sl_creditmemos':
			 		$data_fix	= fix_returns($fila["tbl_name"], $fila["ID_trs"], $sku, $qty, $cost_avg);

			 		$qty		= $data_fix["left_qty_total"];
			 		$cost_avg	= $data_fix["cost_avg"];
			 	break;
			 	case 'sl_wreceipts':
			 		$data_fix	= fix_wreceipts($fila["ID_trs"], $sku, $qty, $cost_avg);

			 		$qty		= $data_fix["left_qty_total"];
			 		$cost_avg	= $data_fix["cost_avg"];
			 	break;
			 	case 'sl_purchaseorders':
			 		$data_fix	= fix_purchase_orders($fila["ID_trs"], $sku, $qty, $cost_avg);

			 		$qty		= $data_fix["left_qty_total"];
			 		$cost_avg	= $data_fix["cost_avg"];
			 	break;
			 	case 'sl_skustransfers':
			 		$data_fix	= fix_skustransfer($fila["ID_trs"], $sku, $qty, $cost_avg);

			 		$qty		= $data_fix["left_qty_total"];
			 		$cost_avg	= $data_fix["cost_avg"];
			 	break;
			}
		}

		return $cost_avg;
	}
?>