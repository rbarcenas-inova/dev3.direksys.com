<?php
	require("../../../httpdocs/nsAdmBase.php");

	error_reporting(E_ERROR);

	$server = $cfg['emp.'.$in['e'].'.dbi_host'];
	$dbname = $cfg['emp.'.$in['e'].'.dbi_db'];
	$user = $cfg['emp.'.$in['e'].'.dbi_user'];
	$pswd = $cfg['emp.'.$in['e'].'.dbi_pw'];

	// Conexion
	$conex = new mysqli($server, $user, $pswd, $dbname);
	if ($conex->connect_errno) {
	    echo "ERROR: (" . $conex->connect_errno . ") " . $conex->connect_error;
	}

	echo "<h3>Conectado a ==> $server :: $dbname</h3>";
	
	$product = 0;
	if(isset($argv[2])){
		$product = (int)$argv[2];
	}else{
		$product = ( isset($in["sku"]) && !empty($in["sku"]) ) ? (int)$in["sku"] : 0;
	}

	$tmp = ($in['e'] == 2) ? '_tmp' : '';
	$sql_sku_filter = ( $product > 0 ) ? " AND Product = ".$product : "";

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
			WHERE 1
				".$sql_sku_filter."
			GROUP BY Product
			ORDER BY Product
			LIMIT 500;";
	echo $sql;
	$rslt = $conex->query($sql);
	
	
	$filename = $dbname.'__'.rand(100,999);
	
	//log_file("SKU,INVENTARIO INICIAL,COSTO INICIAL,INVENTARIO FINAL, COSTO FINAL, TOTAL ENTRADAS, TOTAL SALIDAS,TOTAL QTY ENTRADA, TOTAL QTY SALIDA,INVENTARIO SKUS_TRANS, COSTO SKUS_TRANS, INTENTARIO WarehousesLocation",$filename.'.csv','csv');
	$timer = new ExecutionTime();
	//echo 'Corriendo ';
	$aux = 0;
	while( $fila = $rslt->fetch_assoc() ){
		//echo '.';
		$log .= "<h3>ID_products: ".$fila["Product"]."</h3>\n";
		echo "<h3>ID_products: ".$fila["Product"]."</h3>\n";
		$log .= "<b>Inventario inicial: ".$fila["QtyIni"]."     Costo Inicial: ".$fila["Avg_Cost"]."</b>\n<br>";
		//echo "<b>Inventario inicial: ".$fila["QtyIni"]."     Costo Inicial: ".$fila["Avg_Cost"]."</b>\n<br>";
		$data_fix = fix_inventory($fila["Product"], $fila["QtyIni"], $fila["Avg_Cost"]);

		/*
		$sku_trans = $conex->query("select left_quantity_total,Cost_Avg  from sl_skus_trans$tmp where id_products = $fila[Product] and date >= '2015-11-01' order by id_products_trans desc limit 1;")->fetch_object();
		$sku_wh = $conex->query("select sum(Quantity) qty from sl_warehouses_location where id_products = $fila[Product] group by id_products")->fetch_object();
		log_file("$fila[Product],$fila[QtyIni],$fila[Avg_Cost],$data_fix[left_qty_total],$data_fix[cost_avg],$data_fix[entradas],$data_fix[salidas],$data_fix[entro],$data_fix[salio],".@$sku_trans->left_quantity_total.", ".@$sku_trans->Cost_Avg.",".@$sku_wh->qty,$filename.'.csv','csv');
		

		log_file("INSERT into cu_skus_trans (ID_products, left_quantity_total, Cost_Avg, Cost, Cost_Adj, Cost_Add, ID_customs_info, Date, Time) 
		 	select ID_products, left_quantity_total,Cost_Avg, Cost, Cost_Adj,Cost_Add, ID_customs_info, curdate(), curtime() 
		 	from sl_skus_trans$tmp where ID_products = $fila[Product] order by ID_products_trans desc limit 1
			 on duplicate key update left_quantity_total = $data_fix[left_qty_total], Cost_Avg = $data_fix[cost_avg];",$filename.'.sql');
		*/		
		$log .= "-----------------------------------------------------------------------------------------\n<br>";
		//echo "-----------------------------------------------------------------------------------------\n<br>";
	}
	echo $log;
	log_file($log, $dbname.'.txt', 'txt');
	//echo ".\nFinalizado : $timer\n";
	//log_file("TIEMPO DE EJECUCION: $timer,,,,,,,,,,,",$filename.'.csv','csv');;
	

	//--------------------------------------------------------
	// Funciones
	//--------------------------------------------------------
	function fix_inventory($sku, $qty, $cost_avg){
		global $conex, $log;
		$entradas = 0;
		$salidas = 0;
		$otro = 0;
		$totalEntro = 0;
		$totalSalio = 0;
		$sql_trs = "SELECT sl_skus_trans$tmp.ID_products, sl_skus_trans$tmp.tbl_name,sl_skus_trans$tmp.ID_trs
					FROM sl_skus_trans$tmp
					WHERE sl_skus_trans$tmp.Date>='2015-11-01' 
						AND tbl_name != 'sl_manifests' 
						AND NOT( sl_skus_trans$tmp.`Type` IN('Transfer In', 'Transfer Out') AND tbl_name='sl_orders$tmp' )
						AND ID_products = ".$sku."
					GROUP BY sl_skus_trans$tmp.ID_products, sl_skus_trans$tmp.tbl_name,sl_skus_trans$tmp.ID_trs
					ORDER BY sl_skus_trans$tmp.Date, sl_skus_trans$tmp.Time, sl_skus_trans$tmp.ID_products_trans;";			
		$rslt = $conex->query($sql_trs);

		if( !$rslt )
			return array("left_qty_total" => $qty, "cost_avg" => $cost_avg);

		while( $fila = $rslt->fetch_assoc() ){

			$log .= "<span style='color: blue;'>Transaccion: ".$fila["ID_trs"]." Tabla/Proceso: ".$fila["tbl_name"]."</span>\n<br>";
			// echo "<span style='color: blue;'>Transaccion: ".$fila["ID_trs"]." \t Tabla/Proceso: ".$fila["tbl_name"]."</span>\n<br>";

			switch ($fila["tbl_name"]) {
				case 'sl_orders':
			 		$data_fix	= fix_orders_parts($fila["ID_trs"], $sku, $qty, $cost_avg);

			 		$totalSalio+= $data_fix["qty"];
			 		$qty		= $data_fix["left_qty_total"];
			 		$cost_avg	= $data_fix["cost_avg"];
			 		if( $data_fix["qty"] > 0 ){
			 			$salidas++;
			 		}

			 	break;
			 	case 'sl_parts_productions':
			 		$data_fix	= fix_parts_productions($fila["ID_trs"], $sku, $qty, $cost_avg);
			 		if($data_fix['tipo'] == 'entradas'){
			 			$totalEntro += $data_fix["qty"];			 			
			 		}elseif($data_fix['tipo'] == 'salidas'){
			 			$totalSalio += $data_fix["qty"];
			 		}

			 		$qty		= $data_fix["left_qty_total"];
			 		$cost_avg	= $data_fix["cost_avg"];
			 		$$data_fix['tipo']++;

			 	break;
			 	case 'sl_returns':
			 	case 'sl_creditmemos':
			 		$data_fix	= fix_returns($fila["tbl_name"], $fila["ID_trs"], $sku, $qty, $cost_avg);

					$totalEntro += $data_fix["qty"];
			 		$qty		= $data_fix["left_qty_total"];
			 		$cost_avg	= $data_fix["cost_avg"];
			 		$entradas++;

			 	break;
			 	case 'sl_wreceipts':
			 		$data_fix	= fix_wreceipts($fila["ID_trs"], $sku, $qty, $cost_avg);

					$totalEntro += $data_fix["qty"];
			 		$qty		= $data_fix["left_qty_total"];
			 		$cost_avg	= $data_fix["cost_avg"];
			 		$entradas++;

			 	break;
			 	case 'sl_purchaseorders':
			 		$data_fix	= fix_purchase_orders($fila["ID_trs"], $sku, $qty, $cost_avg);

			 		$totalSalio+= $data_fix["qty"];
			 		$qty		= $data_fix["left_qty_total"];
			 		$cost_avg	= $data_fix["cost_avg"];
			 		$salidas++;

			 	break;
			 	case 'sl_skustransfers':
			 		$data_fix	= fix_skustransfer($fila["ID_trs"], $sku, $qty, $cost_avg);
			 		if($data_fix['tipo'] == 'entradas'){
			 			$totalEntro += $data_fix["qty"];
			 		}elseif($data_fix['tipo'] == 'salidas'){
			 			$totalSalio += $data_fix["qty"];
			 		}
			 		$qty		= $data_fix["left_qty_total"];
			 		$cost_avg	= $data_fix["cost_avg"];
			 		$$data_fix['tipo']++;

			 	break;
			}

			$log .= "=======> Inventario Resultante: ".$qty."\t &nbsp;&nbsp;&nbsp; Costo Promedio Resultante: ".$cost_avg."\n<br>";
			//echo "=======> Inventario Resultante: ".$qty."\t &nbsp;&nbsp;&nbsp; Costo Promedio Resultante: ".$cost_avg."\n<br>";
		}
	
		return array("left_qty_total"	=> $qty, 
					 "cost_avg"			=> $cost_avg, 
					 'entradas'			=> $entradas, 
					 'salidas'			=> $salidas, 
					 'entro'			=> $totalEntro, 
					 'salio'			=> $totalSalio);
	}

	//----------------------------------------------------------------//
	/*Gil*/
	function fix_parts_productions($id_trs, $sku, $qty, $cost_avg){

		global $conex, $log;

		$sql_chk = "SELECT sl_parts_productions.`Type`, In_out, SUM(Qty) Qty
					FROM sl_parts_productions
						INNER JOIN sl_parts_productions_items USING(ID_parts_productions)
					WHERE sl_parts_productions_items.ID_parts_productions=".$id_trs." 
						AND sl_parts_productions_items.ID_products=".$sku."
					GROUP BY sl_parts_productions_items.ID_products;";
		$rslt_chk = $conex->query($sql_chk);
		$data_chk = $rslt_chk->fetch_assoc();

		// echo "Datos obtenidos: ";
		// print_r($data_chk);
		// echo "\n<br>";
		if( $data_chk["In_out"] == "in" ){
			// la trans. es una salida (OUT) y no afecta el costo promedio
			$qty -= $data_chk["Qty"];
			$result['tipo'] = 'salidas';
		}else{
			$result['tipo'] = 'entradas';
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
								FROM sl_skus_trans$tmp
								WHERE ID_trs=".$id_trs." 
									AND tbl_name = 'sl_parts_productions' 
									AND ID_products=".$fila["ID_products"].";";
					//$log .= $sql_cost."\n<br>";
					$rslt_cost = $conex->query($sql_cost);
					$data_cost = $rslt_cost->fetch_assoc();
					
					//-- Alternativa 2					
					$sql_wl = "SELECT SUM(Quantity) QtyIni, Avg_Cost
								FROM warehouse_20151031
								WHERE Product=".$fila["ID_products"].";";
					//$log .= $sql_wl."\n<br>";				
					$rslt_wl = $conex->query($sql_wl);
					$data_wl = $rslt_wl->fetch_assoc();
					if( is_null($data_wl["QtyIni"]) ){
						$sum_cost += $data_cost["Cost"];
					}else{

						$log .= "---------- Subproceso Parts Production ---------\n<br>";
						$cost_ok = fix_cost_parts_prod($id_trs, $fila["ID_products"], $data_wl["QtyIni"], $data_wl["Avg_Cost"], $data_cost["ID_products_trans"]);
						$log .= "---------------- Fin subproceso -----------------\n<br>";
						$sum_cost += ($cost_ok != null) ? $cost_ok : $data_cost["Cost"];
					}

					$log .= "Sumatoria costo: ".$sum_cost."\n<br>";
					// echo "Sumatoria costo: ".$sum_cost."\n<br>";
					
				}

				$total_cost_avg = $cost_avg*$qty;
				$qty += $data_chk["Qty"];
				$cost_avg  = round(( ($total_cost_avg) + ($data_chk["Qty"] * $sum_cost) ) / ($qty), 3);
				$log .= "( (total_cost_avg) + (data_chk[Qty] * sum_cost) ) / (qty) = ( ($total_cost_avg) + ($data_chk[Qty] * $sum_cost) ) / ($qty)\n<br>";
				//$cost_avg = $sum_cost;
			// Explode
			} else {
				$qty -= $data_chk["Qty"];
			}
		}
		
		// $result = array("left_qty_total" => $qty, "cost_avg" => $cost_avg);
		$result['left_qty_total'] =$qty;
		$result['cost_avg'] =  $cost_avg;
		$result['qty'] =  $data_chk["Qty"];
		return $result;
	}

	function fix_cost_parts_prod($id_trs, $sku, $qty, $cost_avg, $id_limit){
		global $conex, $log;

		$sql_trs = "SELECT sl_skus_trans$tmp.ID_products, sl_skus_trans$tmp.tbl_name,sl_skus_trans$tmp.ID_trs
					FROM sl_skus_trans$tmp
					WHERE sl_skus_trans$tmp.Date>='2015-11-01' 
						AND tbl_name != 'sl_manifests' 
						AND NOT( sl_skus_trans$tmp.`Type` IN('Transfer In', 'Transfer Out') AND tbl_name='sl_orders$tmp' ) 
						AND ID_products = ".$sku."
						AND ID_products_trans < ".$id_limit." 
						AND ID_trs != ".$id_trs."
					GROUP BY sl_skus_trans$tmp.ID_products, sl_skus_trans$tmp.tbl_name,sl_skus_trans$tmp.ID_trs
					ORDER BY sl_skus_trans$tmp.Date, sl_skus_trans$tmp.Time, sl_skus_trans$tmp.ID_products_trans;";
		// echo $sql_trs."\n<br>";
		$rslt = $conex->query($sql_trs);

		$log .= "Implode/Explode:: Obteniendo costo promedio de $sku\n<br>";
		// echo "Implode/Explode:: Obteniendo costo promedio de $sku\n<br>";

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

		global $conex, $log;

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
		$result['qty'] = $res['thisQty'];

		return $result;
	}

	/*Jon*/
	function fix_wreceipts($ID_trs, $sku, $left_qty_total, $cost_avg) {

		global $conex, $log;

		$sql = "SELECT pi.Qty thisQty, pi.Price AS thisCost, v.Currency, er.exchange_rate
				FROM sl_wreceipts w
					INNER JOIN sl_wreceipts_items wi ON wi.ID_wreceipts = w.ID_wreceipts
					INNER JOIN sl_purchaseorders_items pi ON pi.ID_purchaseorders = w.ID_purchaseorders
					INNER JOIN sl_purchaseorders po ON po.ID_purchaseorders = pi.ID_purchaseorders
					INNER JOIN sl_vendors v ON po.ID_vendors = v.ID_vendors
					LEFT JOIN sl_exchangerates er ON w.ID_exchangerates = er.ID_exchangerates
				WHERE w.ID_wreceipts = $ID_trs 
					AND wi.ID_products = $sku 
					AND pi.ID_products = $sku
				GROUP BY wi.ID_products;
				";
		//$log .= $sql."\n<br>";
		$rslt = $conex->query($sql);
		$res = $rslt->fetch_assoc();

		$thisQty = $res['thisQty'];
		$thisCost = ($res["exchange_rate"] > 0 and !is_null($res["exchange_rate"])) ? ($res['thisCost'] * $res['exchange_rate']) : $res['thisCost'];

		if( $cost_avg > 0 ){
			$total_cost = $thisQty * $thisCost;
			$log .= "Total Cost: $total_cost = $thisQty * $thisCost\n<br>";
			$total_cost_avg = ($left_qty_total > 0) ? $left_qty_total*$cost_avg : $cost_avg;
			$log .= "Total Cost Avg: $left_qty_total * $cost_avg\n<br>";

			if( $left_qty_total < 0 ) $left_qty_total = 0;
			$cost_avg  = ($total_cost + $total_cost_avg) / ($left_qty_total + $thisQty);

			$log .= "Calculo: ($total_cost + $total_cost_avg) / ($left_qty_total + $thisQty)\n<br>";
			// echo "Calculo: ($total_cost + $total_cost_avg) / ($left_qty_total + $thisQty)\n<br>";
		}else{
			$cost_avg = $thisCost;

			$log .= "Cost PO: ".$thisCost."\n<br>";
			// echo "Cost PO: ".$thisCost."\n<br>";
		}
		$cost_avg = round($cost_avg, 3);

		$left_qty_total += $thisQty;

		$result = array("left_qty_total" => $left_qty_total, "cost_avg" => $cost_avg);
		$result['qty'] = $res['thisQty'];
		return $result;
	}

	/*Fabian*/
	function fix_returns($table,$id_trs,$products,$total,$costo){
		global $conex, $log;

		if($table == 'sl_returns'){
			$q = "select a.Quantity,a.Cost from sl_returns_upcs a inner join sl_returns b on a.ID_returns = b.ID_returns where b.date > @date and b.Status='Resolved' and a.id_returns=$id_trs and a.ID_parts= ".($products - 400000000);

		}elseif($table == 'sl_creditmemos'){
			$q = "select a.ID_products,a.Quantity,a.Cost from sl_creditmemos_products a inner join sl_creditmemos b on b.ID_creditmemos = a.ID_creditmemos where a.date > @date and ID_products = $products and a.id_creditmemos=$id_trs and b.Status='Applied'";
		}

		// echo "------------------ Fix Returns -------------------\n<br>";
		// echo "$q\n";
		$response = array(
			'left_qty_total'=>$total,
			'cost_avg'=>$costo,
			'qty'=>0
		);
		if($conex->query($q)){
			$data = $conex->query($q)->fetch_object();
			// echo "Datos obtenidos: ";
			// print_r($data);
			// echo "\n<br>";
			if( !is_null($data) ){
				$response['left_qty_total'] = $total+$data->Quantity;
				$result['qty'] = $data->Quantity;
				if($data->Cost > 0){
					$log .= "$table: Calculo: (($costo*$total) + ($data->Quantity * $data->Cost)) / ($total+$data->Quantity)\n<br>";
					$response['cost_avg'] = round(( ($costo*$total) + ($data->Quantity * $data->Cost) ) / ($total+$data->Quantity),3);
				}else{
					$log .= "$table: Mismo Costo: $costo\n<br>";
					$response['cost_avg'] = $costo;
				}
			}
		}
		// echo 'Datos resultantes: ';		
		// print_r($response);
		// echo "\n<br>";

		return $response;
	}

	/*Huitzi*/
	function fix_orders_parts($id_trs, $skus, $inventario_inicial, $cost_avg){
		global $conex, $log;

		if($_GET['e'] == 11 || $_GET['e'] == 3 ){
			$sql 	= "	select o.id_orders, o.status, op.id_orders_products, id_products, p.id_orders_parts, sum(p.Quantity) Quantity, p.Cost from 
							(select id_orders, status from sl_orders$tmp where id_orders= '$id_trs') o
							inner join (select id_orders_products, id_orders, id_products, related_id_products from sl_orders_products$tmp 
								       where Status='Active' and related_id_products = '$skus' and id_orders= '$id_trs' ) op 
							on op.ID_orders = o.ID_orders
							inner join (select * from sl_orders_parts$tmp where status='shipped') p 
							on op.id_orders_products=p.id_orders_products group by ID_parts";
		}else{
			$sql 	= "select o.id_orders, o.status, op.id_orders_products, id_products, p.id_orders_parts, sum(p.Quantity
				) Quantity, p.Cost 
						from 
							(select id_orders, status from sl_orders$tmp where id_orders= '$id_trs') o
							inner join 
							(select id_orders_products, id_orders, id_products, related_id_products from sl_orders_products$tmp 
							 where Status='Active' and id_orders= '$id_trs') op 
							on op.ID_orders = o.id_orders
							inner join 
							(select * from sl_orders_parts$tmp where status='shipped' and id_parts = $skus - 400000000) p 
							on op.id_orders_products=p.id_orders_products 
							group by ID_parts";
		}
		// echo "------------------ Fix Orders -------------------\n<br>";
		// echo "\n".$sql."\n";
		$rslt = $conex->query($sql);
		$registro = $rslt->fetch_assoc();
		
		$qty = $inventario_inicial - $registro['Quantity'];

		$log .= "Inventario: $inventario_inicial - $registro[Quantity] = $qty   ==> Cost_avg= $cost_avg\n<br>";
		// echo "||||    $inventario_inicial - $registro[Quantity] = $qty  |||| $cost_avg <br>";

		$result = array("left_qty_total" => $qty, "cost_avg" => $cost_avg,'qty'=>$registro['Quantity']);

		return $result;
	}

	/*Fabian*/
	function fix_skustransfer($id_trs,$products,$total,$costo){
		global $conex, $log;

		$q = "select FromSku,ToSku,Qty from sl_skustransfers_items where id_skustransfers = $id_trs and (FromSku = $products or ToSku=$products);";
		$rs = $conex->query($q);
		$response = array(
			'left_qty_total'=>$total,
			'cost_avg'=>$costo,
			'tipo'=>'otro',
			'qty'=>0
		);
		// echo "------------------ Fix Skustransfer -------------------\n<br>";
		// echo $q;
		if($rs){
			$data = $rs->fetch_object();
			if(!is_null($data)){
				if($data->FromSku == $products){
					$response = array(
						'left_qty_total'=>$total-$data->Qty,
						'cost_avg'=>$costo,
						'tipo'=>'salidas'
					);
					$log .= "SALIDA\n<br>";
					// echo "SALIDA\n<br>";
				}else{

					// Se obtiene el Costo y limite en skus_trans
					$sql_cost = "SELECT ID_products_trans, Cost
							FROM sl_skus_trans$tmp
							WHERE ID_trs=".$id_trs." 
								AND tbl_name = 'sl_skustransfers' 
								AND ID_products=".$data->FromSku.";";
					//$log .= $sql_cost."\n<br>";
					$limit = $conex->query($sql_cost)->fetch_object();
					// Se obtiene el inventario y costo inicial del SKU origen
					$sql_wl = "SELECT SUM(Quantity) QtyIni, Avg_Cost
								FROM warehouse_20151031
								WHERE Product=".$data->FromSku.";";		
					$rslt_wl = $conex->query($sql_wl);
					$data_wl = $rslt_wl->fetch_assoc();

					// SKU Origen: Si no tiene datos iniciales entonces toma el costo registrado en la transaccion(sl_skus_trans)
					if( is_null($data_wl["QtyIni"]) ){
						$cost_avg_calc = $limit->Cost;
					// SKU Origen: Si cuenta con datos iniciales entonces se le aplica el calculo de su costo promedio
					}else{
						$log .= "---------- Subproceso Skus Transfers ----------\n<br>";
						$cost_avg_calc = fix_cost_skustransfer($id_trs, $data->FromSku, $data_wl["QtyIni"], $data_wl["Avg_Cost"], $limit->ID_products_trans);
						$log .= "--------------- Fin del subproceso -------------\n<br>";
					}

					$log .= "From SKU: $data->FromSku, Cost: $cost_avg_calc\n<br>";

					// Se calcula el nuevo costo promedio del SKU resultante (ToSku)
					$cost_avg_calc = round(( ($costo*$total) + ($data->Qty * $cost_avg_calc) ) / ($total+$data->Qty),3);
					$log .= "( (costo*total) + (data->Qty * cost_avg_calc) ) / (total+data->Qty) = ( ($costo*$total) + ($data->Qty * $cost_avg_calc) ) / ($total+$data->Qty)\n<br>";

					$response = array(
						'left_qty_total'=>$total+$data->Qty,
						'cost_avg'=>$cost_avg_calc,
						'tipo'=>'entradas'
					);
					$log .= "ENTRADA\n<br>";
					// echo "ENTRADA\n<br>";
					$log .= "Datos Obtenidos qty: $data->Qty, costo : $response[cost_avg]\n<br>";
					// echo "<br>Datos Obtenidos qty: $data->Qty, costo : $response[cost_avg]<br>";
				}
				$response['qty'] = $data->Qty;
			}
		}
		return $response;
	}

	function fix_cost_skustransfer($id_trs,$sku,$qty,$cost_avg,$id_limit){
		global $conex, $log;

		$sql_trs = "SELECT sl_skus_trans$tmp.ID_products, sl_skus_trans$tmp.tbl_name,sl_skus_trans$tmp.ID_trs
					FROM sl_skus_trans$tmp
					WHERE sl_skus_trans$tmp.Date>='2015-11-01' 
						AND tbl_name != 'sl_manifests' 
						AND NOT( sl_skus_trans$tmp.`Type` IN('Transfer In', 'Transfer Out') AND tbl_name='sl_orders$tmp' )
						AND ID_products = ".$sku."
						AND ID_products_trans < ".$id_limit." 
						AND ID_trs != ".$id_trs."
					GROUP BY sl_skus_trans$tmp.ID_products, sl_skus_trans$tmp.tbl_name,sl_skus_trans$tmp.ID_trs
					ORDER BY sl_skus_trans$tmp.Date, sl_skus_trans$tmp.Time, sl_skus_trans$tmp.ID_products_trans;";
		// echo $sql_trs."\n<br>";
		$rslt = $conex->query($sql_trs);

		$log .= "SkusTransfers : Obteniendo costo promedio de $sku\n<br>";

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



function log_file($data, $fileName = 'log',$type='log'){
	$file = $fileName;
	$handle = fopen($file,'a');
	fwrite($handle,$data.PHP_EOL);
	fclose($handle);
}



class ExecutionTime{
	private $startTime;
	private $endTime;
	public function __construct(){
		$this->startTime = microtime(true);
		$this->endTime = 0;
	}
	public function start(){
		$this->startTime = microtime(true);
		return $this;
	}
	public function end(){
		$this->endTime = microtime(true);
		return $this;
	}
	public function reset(){
		$this->startTime = 0;
		$this->endTime = 0;
		return $this;
	}
	public function __toString(){
		if($this->endTime == 0){
			$this->end();
		}
		return $this->endTime - $this->startTime . ' s.';
	}
}