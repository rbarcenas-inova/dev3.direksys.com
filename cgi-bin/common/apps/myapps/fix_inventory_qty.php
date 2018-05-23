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
	
	// Filtro por SKU
	$product = 0;
	if(isset($argv[2])){
		$product = (int)$argv[2];
	}else{
		$product = ( isset($in["sku"]) && !empty($in["sku"]) ) ? (int)$in["sku"] : 0;
	}
	$sql_sku_filter = ( $product > 0 ) ? " AND Product = ".$product : "";

	// Necesario para mejorar el rendimiento en TMK
	$tmp = ($in['e'] == 2) ? '_tmp' : '';
	

	// Fecha inicial
	$conex->query("SET @fecha='2015-11-01';");

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
			LIMIT 100;";
	echo $sql;
	$rslt = $conex->query($sql);
	
	$filename = $dbname.'_'.rand(100,999);
	
	//log_file("SKU,INVENTARIO INICIAL,COSTO INICIAL,INVENTARIO FINAL, COSTO FINAL, TOTAL ENTRADAS, TOTAL SALIDAS,TOTAL QTY ENTRADA, TOTAL QTY SALIDA,INVENTARIO SKUS_TRANS, COSTO SKUS_TRANS, INTENTARIO WarehousesLocation",$filename.'.csv','csv');
	$timer = new ExecutionTime();
	//echo 'Corriendo ';
	while( $fila = $rslt->fetch_assoc() ){
		$log .= "<h3>ID_products: ".$fila["Product"]."</h3>\n";
		//echo "<h3>ID_products: ".$fila["Product"]."</h3>\n";
		$log .= "<b>Inventario inicial: ".$fila["QtyIni"]."     Costo Inicial: ".$fila["Avg_Cost"]."</b>\n<br>";
		//echo "<b>Inventario inicial: ".$fila["QtyIni"]."     Costo Inicial: ".$fila["Avg_Cost"]."</b>\n<br>";
		$data_fix = fix_inventory($fila["Product"], $fila["QtyIni"], $fila["Avg_Cost"]);

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
	function fix_inventory($sku, $qty, $cost_avg=0){
		global $conex, $log;

		$entradas	= 0;
		$salidas 	= 0;
		$totalEntro = 0;
		$totalSalio = 0;

		$sql_trs = "SELECT sl_skus_trans$tmp.ID_products, sl_skus_trans$tmp.tbl_name,sl_skus_trans$tmp.ID_trs
					FROM sl_skus_trans$tmp
					WHERE sl_skus_trans$tmp.Date>=@fecha 
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
			 		$data_fix	= fix_orders_parts($fila["ID_trs"], $sku, $qty);

			 		$qty		= $data_fix["left_qty_total"];
			 		$totalSalio	+= $data_fix["qty"];
			 		$salidas++;			 		

			 	break;
			 	case 'sl_parts_productions':
			 		$data_fix	= fix_parts_productions($fila["ID_trs"], $sku, $qty);

			 		$qty		= $data_fix["left_qty_total"];
			 		if($data_fix['tipo'] == 'entradas'){
			 			$totalEntro += $data_fix["qty"];			 			
			 		}elseif($data_fix['tipo'] == 'salidas'){
			 			$totalSalio += $data_fix["qty"];
			 		}
			 		$$data_fix['tipo']++;

			 	break;
			 	case 'sl_returns':
			 	case 'sl_creditmemos':
			 		$data_fix	= fix_returns($fila["tbl_name"], $fila["ID_trs"], $sku, $qty);

			 		$qty		= $data_fix["left_qty_total"];
					$totalEntro += $data_fix["qty"];
			 		$entradas++;

			 	break;
			 	case 'sl_wreceipts':
			 		$data_fix	= fix_wreceipts($fila["ID_trs"], $sku, $qty);

			 		$qty		= $data_fix["left_qty_total"];
					$totalEntro += $data_fix["qty"];
			 		$entradas++;

			 	break;
			 	case 'sl_purchaseorders':
			 		$data_fix	= fix_purchase_orders($fila["ID_trs"], $sku, $qty);

			 		$qty		= $data_fix["left_qty_total"];
			 		$totalSalio	+= $data_fix["qty"];
			 		$salidas++;

			 	break;
			 	case 'sl_skustransfers':
			 		$data_fix	= fix_skustransfer($fila["ID_trs"], $sku, $qty);
			 		
			 		$qty		= $data_fix["left_qty_total"];
			 		if($data_fix['tipo'] == 'entradas'){
			 			$totalEntro += $data_fix["qty"];
			 		}elseif($data_fix['tipo'] == 'salidas'){
			 			$totalSalio += $data_fix["qty"];
			 		}
			 		$$data_fix['tipo']++;

			 	break;
			}

			$log .= "=======> Inventario Resultante: ".$qty."\t &nbsp;&nbsp;&nbsp; Costo Promedio Resultante: ".$cost_avg."\n<br>";
			//echo "=======> Inventario Resultante: ".$qty."\t &nbsp;&nbsp;&nbsp; Costo Promedio Resultante: ".$cost_avg."\n<br>";
		}
	
		return array("left_qty_total"	=> $qty,
					 'entradas'			=> $entradas, 
					 'salidas'			=> $salidas, 
					 'entro'			=> $totalEntro, 
					 'salio'			=> $totalSalio);
	}

	/*Gil*/
	function fix_parts_productions($id_trs, $sku, $qty){

		global $conex, $log;

		$sql_chk = "SELECT sl_parts_productions.`Type`, In_out, SUM(Qty) Qty
					FROM sl_parts_productions
						INNER JOIN sl_parts_productions_items USING(ID_parts_productions)
					WHERE sl_parts_productions_items.ID_parts_productions=".$id_trs." 
						AND sl_parts_productions_items.ID_products=".$sku."
					GROUP BY sl_parts_productions_items.ID_products;";
		$rslt_chk = $conex->query($sql_chk);
		$data_chk = $rslt_chk->fetch_assoc();
		
		if( $data_chk["In_out"] == "in" ){
			// la trans. es una salida (OUT) y no afecta el costo promedio
			$qty -= $data_chk["Qty"];
			$result['tipo'] = 'salidas';
		}else{
			$result['tipo'] = 'entradas';			
			$qty += $data_chk["Qty"];
		}
		
		$log .= "Quantity ==> ".$data_chk["Qty"]."\n<br>";

		$result['left_qty_total'] = $qty;
		$result['qty'] = $data_chk["Qty"];
		return $result;
	}	

	/*Jon - Return to vendor*/
	function fix_purchase_orders($id_trs, $sku, $qty) {

		global $conex, $log;

		$sql = "SELECT pi.Qty thisQty
				FROM sl_purchaseorders p
				INNER JOIN sl_purchaseorders_items pi ON pi.ID_purchaseorders = p.ID_purchaseorders
				WHERE p.ID_purchaseorders = $id_trs
				AND pi.ID_products = $sku;
				";
		$rslt = $conex->query($sql);
		$res = $rslt->fetch_assoc();

		$log .= "Quantity ==> ".$res['thisQty']."\n<br>";

		$qty -= $res['thisQty'];
		$result["left_qty_total"] = $qty;
		$result['qty'] = $res['thisQty'];

		return $result;
	}

	/*Jon*/
	function fix_wreceipts($id_trs, $sku, $qty) {

		global $conex, $log;

		$sql = "SELECT pi.Qty thisQty, pi.Price AS thisCost, v.Currency, er.exchange_rate
				FROM sl_wreceipts w
					INNER JOIN sl_wreceipts_items wi ON wi.ID_wreceipts = w.ID_wreceipts
					INNER JOIN sl_purchaseorders_items pi ON pi.ID_purchaseorders = w.ID_purchaseorders
					INNER JOIN sl_purchaseorders po ON po.ID_purchaseorders = pi.ID_purchaseorders
					INNER JOIN sl_vendors v ON po.ID_vendors = v.ID_vendors
					LEFT JOIN sl_exchangerates er ON w.ID_exchangerates = er.ID_exchangerates
				WHERE w.ID_wreceipts = $id_trs 
					AND wi.ID_products = $sku 
					AND pi.ID_products = $sku
				GROUP BY wi.ID_products;
				";
		$rslt = $conex->query($sql);
		$res = $rslt->fetch_assoc();

		$log .= "Quantity ==> ".$res['thisQty']."\n<br>";

		$qty += $res['thisQty'];
		$result["left_qty_total"] = $qty;
		$result['qty'] = $res['thisQty'];

		return $result;
	}

	/*Fabian*/
	function fix_returns($table, $id_trs, $sku, $qty){
		global $conex, $log;

		if($table == 'sl_returns'){
			$q = "select a.Quantity,a.Cost from sl_returns_upcs a inner join sl_returns b on a.ID_returns = b.ID_returns where b.date > @fecha and b.Status='Resolved' and a.id_returns=$id_trs and a.ID_parts= ".($sku - 400000000);
		}elseif($table == 'sl_creditmemos'){
			$q = "select a.ID_products,a.Quantity,a.Cost from sl_creditmemos_products a inner join sl_creditmemos b on b.ID_creditmemos = a.ID_creditmemos where a.date > @fecha and ID_products = $sku and a.id_creditmemos=$id_trs and b.Status='Applied'";
		}
		
		$response = array(
			'left_qty_total' => $qty,
			'qty' => 0
		);

		if($conex->query($q)){
			$data = $conex->query($q)->fetch_object();
			
			$response['left_qty_total'] = $qty + $data->Quantity;
			$result['qty'] = $data->Quantity;			
		}

		$log .= "Quantity ==> ".$result['qty']."\n<br>";

		return $response;
	}

	/*Huitzi*/
	function fix_orders_parts($id_trs, $sku, $qty){
		global $conex, $log;

		if($_GET['e'] == 11 || $_GET['e'] == 3 ){
			$sql 	= "	select o.id_orders, o.status, op.id_orders_products, id_products, p.id_orders_parts, sum(p.Quantity) Quantity, p.Cost from 
							(select id_orders, status from sl_orders$tmp where id_orders= '$id_trs') o
							inner join (select id_orders_products, id_orders, id_products, related_id_products from sl_orders_products$tmp 
								       where Status='Active' and related_id_products = '$sku' and id_orders= '$id_trs' ) op 
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
							(select * from sl_orders_parts$tmp where status='shipped' and id_parts = $sku - 400000000) p 
							on op.id_orders_products=p.id_orders_products 
							group by ID_parts";
		}
		
		$rslt = $conex->query($sql);
		$registro = $rslt->fetch_assoc();
		
		$qty -= $registro['Quantity'];

		$log .= "Quantity ==> ".$registro['Quantity']."\n<br>";

		$result = array("left_qty_total" => $qty, 'qty' => $registro['Quantity']);

		return $result;
	}

	/*Fabian*/
	function fix_skustransfer($id_trs, $sku, $total){
		global $conex, $log;

		$q = "select FromSku,ToSku,Qty from sl_skustransfers_items where id_skustransfers = $id_trs and (FromSku = $sku or ToSku=$sku);";
		$rs = $conex->query($q);

		$response = array(
			'left_qty_total'=>$total,
			'tipo'=>'otro',
			'qty'=>0
		);
		
		if($rs){
			$data = $rs->fetch_object();
			if(!is_null($data)){
				if($data->FromSku == $sku){
					$response = array(
						'left_qty_total' => $qty - $data->Qty,
						'tipo'=>'salidas'
					);
					$log .= "SALIDA ==> ".$data->Qty."\n<br>";
					// echo "SALIDA\n<br>";
				}else{
					$response = array(
						'left_qty_total' => $qty + $data->Qty,
						'tipo' => 'entradas'
					);
					$log .= "ENTRADA ==> ".$data->Qty."\n<br>";
				}
				$response['qty'] = $data->Qty;
			}
		}
		return $response;
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