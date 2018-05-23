<?php
	require("../../../httpdocs/nsAdmBase.php");
	if(isset($argv[1]) and $argv[1]!='') {
		$in['e'] = $argv[1];
	}
	define('NL','<br>'.PHP_EOL);
	error_reporting(E_ERROR);
	$show_log = false;
	if(isset($argv) and in_array('debug',$argv)){
		$show_log = true;
	}else{
		$show_log = isset($in["debug"]) ? true : false;
	}

	$server = $cfg['emp.'.$in['e'].'.dbi_host'];
	$dbname = $cfg['emp.'.$in['e'].'.dbi_db'];
	$user = $cfg['emp.'.$in['e'].'.dbi_user'];
	$pswd = $cfg['emp.'.$in['e'].'.dbi_pw'];

	// Conexion
	$conex = new mysqli($server, $user, $pswd, $dbname);
	if ($conex->connect_errno) {
	    _echo("ERROR: (" . $conex->connect_errno . ") " . $conex->connect_error);
	}

	_echo("<h3>Conectado a ==> $server :: $dbname</h3>");
	
	$product = 0;
	if(isset($argv[2]) and $argv[2] != 'debug'){
		$product = (int)$argv[2];
	}else{
		$product = ( isset($in["sku"]) && !empty($in["sku"]) ) ? (int)$in["sku"] : 0;
	}


	$tmp = ($in['e'] == 2) ? '_tmp' : '';
	$sql_sku_filter = ( $product > 0 ) ? " AND Product = ".$product : "";

	// Conexion
	$conex = new mysqli($server, $user, $pswd, $dbname);
	if ($conex->connect_errno) {
	    _echo("ERROR: (" . $conex->connect_errno . ") " . $conex->connect_error);
	}
	

	$fecha = '2015-10-31';
	$conex->query("set @date=$fecha");

	
	$log = '';
	//---------------------------------------------------------
	// Recorrido de la tabla con saldos iniciales
	//---------------------------------------------------------
	if(isset($argv) and !$show_log){
		echo "CREANDO TABLAS TEMPORALES\r" ;
	}

	$skus_trans_table = 'sl_skus_trans';
	// $conex->query("truncate $skus_trans_table");
	// $conex->query("INSERT INTO $skus_trans_table
	// Select * From sl_skus_trans
	// Where sl_skus_trans.Date>'2015-10-31' and  sl_skus_trans.Date < '2015-12-1'");

	$orders_table = 'sl_orders';
	// $conex->query("truncate $orders_table");
	// $conex->query("INSERT INTO $orders_table
	// Select sl_orders.* 
	// From sl_orders 
	// 	Inner Join (
	// 		Select ID_trs 
	// 		From sl_skus_trans
	// 		Where Date > '2015-10-31' And tbl_name = 'sl_orders' And Type = 'Sale'
	// 		Group by ID_trs
	// 	)sl_skus_trans ON sl_orders.ID_orders = sl_skus_trans.ID_trs
	// Where 1");
	$orders_parts_table = 'sl_orders_parts';
	// $conex->query("truncate $orders_parts_table");
	// $conex->query("INSERT INTO $orders_parts_table
	// Select sl_orders_parts.*
	// From sl_orders_parts
	// 	Inner Join sl_orders_products Using(ID_orders_products)
	// Where 1");



	$orders_products_table = 'sl_orders_products';
	// $conex->query("truncate $orders_products_table");
	// $conex->query("INSERT INTO $orders_table
	// Select sl_orders_products.* 
	// From sl_orders_products
	// Where 1 and  Date>'2015-10-31'");
	$orders_parts_table = 'sl_orders_parts';
	// $conex->query("truncate $orders_parts_table");
	// $conex->query("INSERT INTO $orders_parts_table
	// Select sl_orders_parts.*
	// From sl_orders_parts where Date>'2015-10-31'");



	$conex->query("CREATE TEMPORARY TABLE IF NOT EXISTS $orders_products_table AS (SELECT * FROM sl_orders_products where Date > '2015-10-31');");
	

	$sql = "SELECT Product, SUM(Quantity) QtyIni, Avg_Cost
			FROM warehouse_20151031 
			WHERE 1
				".$sql_sku_filter."
			GROUP BY Product
			ORDER BY Product";
	$rslt = $conex->query($sql);


	$filename = $dbname.'__'.rand(100,999);
	log_file("SKU,INVENTARIO INICIAL,INVENTARIO FINAL,TOTAL TRANSACCIONES DE ENTRADAS, TOTAL DE TRANSACCIONES DE SALIDAS,TOTAL INV ENTRADA, TOTAL INV SALIDA",$filename.'.csv','csv');
	$timer = new ExecutionTime();
	$aux = 0;
	_echo(NL);
	$total = $rslt->num_rows;
	$helper = 0;
	if(isset($argv) and !$show_log){
		echo "                                      \r" ;
	}
	while( $fila = $rslt->fetch_assoc() ){
		$helper++;

		if(isset($argv) and !$show_log){
			echo "PROCESO : ".( number_format( ($helper*100/$total) ,2) )."\r" ;
		}
		$log .= "ID_products: ".$fila["Product"].NL;

		$log .= "Inventario inicial: ".$fila["QtyIni"]."     Costo Inicial: ".$fila["Avg_Cost"].NL;

		$data_fix = fix_inventory($fila["Product"], $fila["QtyIni"], $fila["Avg_Cost"]);
		log_file("$fila[Product],$fila[QtyIni],$data_fix[left_qty_total],$data_fix[entradas],$data_fix[salidas],$data_fix[entro],$data_fix[salio]",$filename.'.csv','csv');
	}
	_echo(NL);
	// _echo($log);
	log_file($log, $dbname.'.txt', 'txt');
	//_echo(".\nFinalizado : $timer\n");
	log_file("TIEMPO DE EJECUCION: $timer,,,,,,,,,,,",$filename.'.csv','csv');
	

	//--------------------------------------------------------
	// Funciones
	//--------------------------------------------------------
	function fix_inventory($sku, $qty, $cost_avg){
		global $conex,$orders_table,$orders_parts_table, $log,$skus_trans_table;
		$entradas = 0;
		$salidas = 0;
		$otro = 0;
		$totalEntro = 0;
		$totalSalio = 0;
		$sql_trs = "SELECT $skus_trans_table.ID_products, $skus_trans_table.tbl_name,$skus_trans_table.ID_trs
					FROM $skus_trans_table
					WHERE $skus_trans_table.Date>='2015-11-01' 
						AND tbl_name != 'sl_manifests' 
						AND NOT( $skus_trans_table.`Type` IN('Transfer In', 'Transfer Out') AND tbl_name='$orders_table' )
						AND ID_products = ".$sku."
					GROUP BY $skus_trans_table.ID_products, $skus_trans_table.tbl_name,$skus_trans_table.ID_trs
					ORDER BY $skus_trans_table.Date, $skus_trans_table.Time, $skus_trans_table.ID_products_trans;";			
		$rslt = $conex->query($sql_trs);
		if( !$rslt )
			return array("left_qty_total" => $qty);

		while( $fila = $rslt->fetch_assoc() ){

			$log .= "<span style='color: blue;'>Transaccion: ".$fila["ID_trs"]." Tabla/Proceso: ".$fila["tbl_name"]."</span>\n<br>";
			_echo("<span style='color: blue;'>Transaccion: ".$fila["ID_trs"]." \t Tabla/Proceso: ".$fila["tbl_name"]." \t Inventario Inicial: ".$qty."</span>\n<br>");
			$data_fix = [];
			switch ($fila["tbl_name"]) {
				case 'sl_orders':
			 		$data_fix	= fix_orders_parts($fila["ID_trs"], $sku, $qty, $cost_avg);

			 		$totalSalio+= $data_fix["qty"];
			 		$qty		= $data_fix["left_qty_total"];
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
			 		$$data_fix['tipo']++;

			 	break;
			 	case 'sl_returns':
			 	case 'sl_creditmemos':
			 		$data_fix	= fix_returns($fila["tbl_name"], $fila["ID_trs"], $sku, $qty, $cost_avg);
					$totalEntro += $data_fix["qty"];
			 		$qty		= $data_fix["left_qty_total"];
			 		$entradas++;

			 	break;
			 	case 'sl_wreceipts':
			 		$data_fix	= fix_wreceipts($fila["ID_trs"], $sku, $qty, $cost_avg);

					$totalEntro += $data_fix["qty"];
			 		$qty		= $data_fix["left_qty_total"];
			 		$entradas++;

			 	break;
			 	case 'sl_purchaseorders':
			 		$data_fix	= fix_purchase_orders($fila["ID_trs"], $sku, $qty, $cost_avg);

			 		$totalSalio+= $data_fix["qty"];
			 		$qty		= $data_fix["left_qty_total"];
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
			 		$$data_fix['tipo']++;

			 	break;
			}

			$log .= "=======> Inventario Resultante: ".$qty."\t &nbsp;&nbsp;&nbsp; Costo Promedio Resultante: ".$cost_avg."\n<br>";
			_echo("=======> Inventario Resultante: ".$data_fix['left_qty_total']."\t TOTAL SALIO: $totalSalio TOTAL ENTRO: $totalEntro".NL);
		}
	
		return array("left_qty_total"	=> $qty, 
					 'entradas'			=> $entradas, 
					 'salidas'			=> $salidas, 
					 'entro'			=> $totalEntro, 
					 'salio'			=> $totalSalio);
	}

	//----------------------------------------------------------------//
	/*Gil*/
	function fix_parts_productions($id_trs, $sku, $qty, $cost_avg){

		global $conex,$orders_table,$orders_parts_table, $log,$skus_trans_table;

		$sql_chk = "SELECT sl_parts_productions.`Type`, In_out, SUM(Qty) Qty
					FROM sl_parts_productions
						INNER JOIN sl_parts_productions_items USING(ID_parts_productions)
					WHERE sl_parts_productions_items.ID_parts_productions=".$id_trs." 
						AND sl_parts_productions_items.ID_products=".$sku."
					GROUP BY sl_parts_productions_items.ID_products;";
		$rslt_chk = $conex->query($sql_chk);
		$data_chk = $rslt_chk->fetch_assoc();

		if( $data_chk["In_out"] == "in" ){
			$qty -= $data_chk["Qty"];
			$result['tipo'] = 'salidas';
		}else{
			$qty += $data_chk["Qty"];
			$result['tipo'] = 'entradas';
		}

		$result['left_qty_total'] =$qty;
		$result['cost_avg'] =  $cost_avg;
		$result['qty'] =  $data_chk["Qty"];
		return $result;
	}

	/*Jon*/
	function fix_purchase_orders($ID_trs, $sku, $left_qty_total, $cost_avg) {

		global $conex,$orders_table,$orders_parts_table, $log,$skus_trans_table;

		$sql = "SELECT pi.Qty thisQty
				FROM sl_purchaseorders p
				INNER JOIN sl_purchaseorders_items pi ON pi.ID_purchaseorders = p.ID_purchaseorders
				WHERE p.ID_purchaseorders = $ID_trs
				AND pi.ID_products = $sku;
				";
		$rslt = $conex->query($sql);
		$res = $rslt->fetch_assoc();

		$left_qty_total -= $res['thisQty'];

		$result = array("left_qty_total" => $left_qty_total);
		$result['qty'] = $res['thisQty'];

		return $result;
	}

	/*Jon*/
	function fix_wreceipts($ID_trs, $sku, $left_qty_total, $cost_avg) {

		global $conex,$orders_table,$orders_parts_table, $log,$skus_trans_table;

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

		$left_qty_total += $res['thisQty'];

		$result = array("left_qty_total" => $left_qty_total);
		$result['qty'] = $res['thisQty'];
		return $result;
	}

	/*Fabian*/
	function fix_returns($table,$id_trs,$products,$total,$costo){
		global $conex,$orders_table,$orders_parts_table, $log,$skus_trans_table;

		if($table == 'sl_returns'){
			$q = "select a.Quantity,a.Cost from sl_returns_upcs a inner join sl_returns b on a.ID_returns = b.ID_returns where b.date > @date and a.id_returns=$id_trs and a.ID_parts= ".($products - 400000000);

		}elseif($table == 'sl_creditmemos'){
			$q = "select a.ID_products,a.Quantity,a.Cost from sl_creditmemos_products a inner join sl_creditmemos b on b.ID_creditmemos = a.ID_creditmemos where a.date > @date and ID_products = $products and a.id_creditmemos=$id_trs";
		}
		$entro = 0;
		_echo("------------------ Fix Returns -------------------\n<br>");
		$response = array(
			'left_qty_total'=>$total,
			'qty'=>0
		);
		if($conex->query($q)){
			$data = $conex->query($q)->fetch_object();
			if( !is_null($data) ){
				$response['left_qty_total'] = $total+$data->Quantity;
				$response['qty'] = $data->Quantity;
				$entro = $data->Quantity;
			}
		}
		_echo("ENTRO: $entro".NL);
		return $response;
	}

	/*Huitzi*/
	function fix_orders_parts($id_trs, $skus, $inventario_inicial, $cost_avg){
		global $conex,$orders_table,$orders_products_table,$orders_parts_table, $log,$skus_trans_table;
		$conex->report_mode = MYSQLI_REPORT_ALL;
		$sql 	= 	"SELECT IFNULL(SUM(sl_orders_parts.Quantity),0) Quantity FROM sl_orders  INNER JOIN sl_orders_products ON sl_orders.ID_orders=sl_orders_products.ID_orders INNER JOIN sl_orders_parts ON sl_orders_products.ID_orders_products=sl_orders_parts.ID_orders_products WHERE sl_orders.ID_orders='$id_trs' AND (400000000+sl_orders_parts.ID_parts)='$skus' GROUP BY sl_orders_parts.ID_orders_products, sl_orders_parts.ID_parts";
		// }else{
		// 	$sql 	= "SELECT IFNULL(SUM(sl_orders_parts.Quantity),0)Quantity
 	// FROM sl_orders
 	// INNER JOIN sl_orders_products ON sl_orders.ID_orders=sl_orders_products.ID_orders
 	// INNER JOIN sl_orders_parts ON sl_orders_products.ID_orders_products=sl_orders_parts.ID_orders_products
 	// WHERE sl_orders.ID_orders='".$id_trs."'
 	// AND (400000000+sl_orders_parts.ID_parts)='".$skus."'
 	// GROUP BY sl_orders_parts.ID_orders_products, sl_orders_parts.ID_parts";
		// }
		_echo("------------------ Fix Orders -------------------\n<br>");
		_echo("\n".$sql."\n");
		$rslt = $conex->query($sql);
		// $registro = $rslt->fetch_assoc();
		echo NL;
		echo NL;
		echo '<pre>';
		var_dump($rslt);
		var_dump($conex->error);
		var_dump($rslt->fetch_assoc());
		echo '</pre>';
		echo NL;
		echo NL;

		echo NL;
		echo NL;


		$qty = $inventario_inicial - $registro['Quantity'];

		$log .= "Inventario: $inventario_inicial - $registro[Quantity] = $qty   ==> Cost_avg= $cost_avg\n<br>";
		// _echo("||||    $inventario_inicial - $registro[Quantity] = $qty  |||| $cost_avg <br>");
		_echo("SALIO: $registro[Quantity]".NL);

		$result = array("left_qty_total" => $qty, "cost_avg" => $cost_avg,'qty'=>$registro['Quantity']);

		return $result;
	}

	/*Fabian*/
	function fix_skustransfer($id_trs,$products,$total,$costo){
		global $conex,$orders_table,$orders_parts_table, $log,$skus_trans_table;

		$q = "select FromSku,ToSku,Qty from sl_skustransfers_items where id_skustransfers = $id_trs and (FromSku = $products or ToSku=$products);";
		$rs = $conex->query($q);
		$response = array(
			'left_qty_total'=>$total,
			'cost_avg'=>$costo,
			'tipo'=>'otro',
			'qty'=>0
		);
		_echo("------------------ Fix Skustransfer -------------------\n<br>");

		if($rs){
			$data = $rs->fetch_object();
			if(!is_null($data)){
				if($data->FromSku == $products){
					$response = array(
						'left_qty_total'=>$total-$data->Qty,
						'tipo'=>'salidas',
						'qty'=>$data->Qty

					);
					// $log .= "SALIDA\n<br>";
					_echo("SALIO: $data->Qty".NL);

				}else{
					$response = array(
						'left_qty_total'=>$total+$data->Qty,
						'tipo'=>'entradas',
						'qty'=>$data->Qty
					);
					_echo("ENTRO: $data->Qty".NL);

				}
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

function _echo($echo){
	global $show_log;
	if($show_log)
		echo $echo;

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