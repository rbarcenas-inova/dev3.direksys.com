<?php
	
	$server = "172.20.27.78";
	$dbname = "direksys2_e";
	$user = "d2tmk";
	$pswd = "BVkdsU839*&783gsklNslkbHs";
	/*
	$server = "localhost";
	$pswd = "jKSu2&&28GjngbKJSWH*(*289HK";
	*/
	// Empresa (default e11)
	$dbname .= ( isset($_GET["e"]) && !empty($_GET["e"]) ) ? (int)$_GET["e"] : 2;

	error_reporting(E_ALL);

	// Conexion
	$conex = new mysqli($server, $user, $pswd, $dbname);
	if ($conex->connect_errno) {
	    echo "ERROR: (" . $conex->connect_errno . ") " . $conex->connect_error;
	}

	//$fecha = '2015-10-31';
	//$conex->query("set @date=$fecha");
	$rslt_main = $conex->query("SELECT o.ID_orders, o.Ptype, o.`Status`, o.Date
							FROM sl_orders o 
							WHERE 1
								#AND o.ID_orders IN(10053528,10053543,10053542,10053561,10053580,10053581,10053575,10053608,10053617,10053620,10053625,10053644,10053645,10053656,10053474,10053674,10053684,10052749,10053694,10053696,10053711,10053713,10053706,10051105,10053734,10053737,10053738,10051280,10053755,10053760,10053754,10048172,10053780,10053786,10053787,10053789,10053788,10053796,10053800,10053790,10049378,10053816,10053825,10052333,10053776,10053840,10053852,10053865,10053877,10053883,10053892,10052243,10053902,10053905,10053941,10053907,10053752,10053970,10050576,10053977,10053982,10053869,10053990,10054025,10054026,10054027,10054020,10054030,10054039,10054042,10054044,10054047,10054056,10054065,10051714,10054072,10053764,10054083,10054085,10054086,10054087,10054101,10054102,10054106,10054107,10054113,10054134,10054140,10054142,10054154,10054164,10054173,10054185,10054188,10054200,10054218,10054236,10054241,10054243,10054253,10054268,10054271,10054288,10049652,10048999,10048371,10054296,10054347,10054363,10054365,10054383,10054390,10054398,10054402,10054423,10054428,10054302,10054433,10054442,10054457,10054458,10054446,10054461,10054419,10054468,10054473,10054510,10054527,10054538,10054531,10054519,10054473,10054614,10054640,10054643,10054650,10054652,10054670,10047598,10054677,10054715,10054743,10054758,10054730,10054780,10054499,10054788,10053450,10054555,10054858,10054860,10054870,10054877,10052760,10054904,10054907,10054705,10054917,10054922,10054927,10054932,10054933,10054939,10054919,10054951,10054956,10054960,10054968,10054973,10054976,10053023,10054984)
								AND o.ID_orders IN(10053851,10053826,10053735,10053647,10054118,10053562,10054169,10054016,10053954,10053889,10053853,10053697,10053687,10053624,10053548,10054821,10054491,10054258,10054901,10054540,10054528,10054472,10054237,10054226)
							;");
			

	$log = '';
	
	$ida_ant_debit		= 1046; //BANORTE 801611522 ING/EG
	$ida_ant_credit		= 1173; //ANT BANORTE 801611522
	$ida_venta_venta	= 1244; //VENTAS
	$ida_venta_iva		= 1188; //IVA 16% DE FACTURAS COBRADAS
	$ida_venta_ant		= 1173; //ANT BANORTE 801611522
	$ida_costo_debit	= 1253; //COSTO DE VENTAS
	$ida_costo_credit	= 1106; //INVENTARIO DE ARTS P/ VENTA
	//foreach ($orders as $id_orders) {
	$log = "START TRANSACTION;<br />";
	$log_sql = "START TRANSACTION;\n";
	while( $orden = $rslt_main->fetch_assoc() ){
		
		$log .= 'ID_orders :: '.$orden['ID_orders'].'<br /><br />';
		$log_sql .= "\n/*--------- ID_orders :: ".$orden['ID_orders']." ---------*/\n";
		$log .= $sql.'<br /><br />';
		//$rslt = $conex->query($sql);		

		// Se obtienen los montos para la contabilidad de anticipos y ventas
		$sql = "SELECT ROUND(SUM(SalePrice - Discount), 2) OrderNet
					, ROUND(SUM(Shipping), 2) Shipping
					, ROUND(SUM(Tax+ShpTax), 2) Tax
					, ROUND(SUM(SalePrice - Discount + Shipping + Tax + ShpTax), 2) OrderTotal
					, sl_orders_products.ShpDate
					, sl_orders_payments.CapDate
				FROM sl_orders_products
					INNER JOIN sl_orders_payments ON sl_orders_products.ID_orders = sl_orders_payments.ID_orders AND sl_orders_payments.`Status`='Approved'
				WHERE sl_orders_products.ID_orders=".$orden['ID_orders']." AND sl_orders_products.`Status`='Active'
				GROUP BY sl_orders_products.ID_orders;";
		$log .= $sql.'<br /><br />';
		$rslt = $conex->query($sql);
		$dat_prod = $rslt->fetch_assoc();

		// Se generan los mov. de anticipos
		$log .= 'Anticipos ====> <br />';
		$log_sql .= "/*------ Anticipos ------*/\n";
		$params['id_orders']	= $orden['ID_orders'];
		$params['id_accounts']	= 1517;//$ida_ant_debit;  Banco
		$params['amount']		= $dat_prod['OrderTotal'];
		$params['effdate']		= $dat_prod['CapDate'];
		$params['tablerelated'] = '';
		$params['id_tablerelated'] = 0;
		$params['category']		= 'Anticipo Clientes';
		$params['credebit']		= 'Debit';
		$params['execute']		= 0;
		// Ant. Debit
		$rslt_fun = add_mov($params);
		$log .= ($rslt_fun != false) ? $rslt_fun.'<br />' : 'Error<br />';
		$log_sql .= ($rslt_fun != false) ? $rslt_fun : "; Error; \nROLLBACK;\n";
		// Ant. Credit
		$params['credebit']		= 'Credit';
		$params['id_accounts']	= 1518;//$ida_ant_credit; Anticipo
		$rslt_fun = add_mov($params);
		$log .= ($rslt_fun != false) ? $rslt_fun.'<br />' : 'Error<br />';
		$log_sql .= ($rslt_fun != false) ? $rslt_fun : "; Error; \nROLLBACK;\n";
		
		// Si el pedido ya se escaneó
		if( $orden['Status'] == 'Shipped' ){
			$log_sql .= "UPDATE sl_movements SET ID_accounts = 1518
						 WHERE tableused='sl_orders' 
						 	AND ID_tableused=".$orden['ID_orders']." 
						 	AND ID_accounts=1074 
						 	AND Category='Ventas' 
						 	AND Credebit='Debit' 
						 	AND `Status`='Active';\n";

			/*
			// Se obtiene el id de la factura de la orden
			$log .= 'Ventas ====> <br />';
			$log_sql .= "/*------ Ventas ------/\n";
			$sql = "SELECT cu_invoices_lines.ID_invoices
					FROM cu_invoices_lines
					WHERE cu_invoices_lines.ID_orders = ".$orden['ID_orders']."
					LIMIT 1;";
			$log .= $sql.'<br />';
			$rslt_fact = $conex->query($sql);
			$dat_fact = $rslt_fact->fetch_assoc();

			// Se generan los mov. de ventas
			$params['id_accounts']	= $ida_venta_venta;
			$params['amount']		= $dat_prod['OrderNet'];
			$params['effdate']		= $dat_prod['ShpDate'];
			$params['tablerelated'] = 'cu_invoices';
			$params['id_tablerelated'] = $dat_fact['ID_invoices'];
			$params['category']		= 'Ventas';
			$params['credebit']		= 'Credit';
			$params['execute']		= 0;
			// Venta Credit
			$rslt_fun = add_mov($params);
			$log .= ($rslt_fun != false) ? $rslt_fun.'<br />' : 'Error<br />';
			$log_sql .= ($rslt_fun != false) ? $rslt_fun : "; Error; \nROLLBACK;\n";
			// Venta Credit IVA
			$params['id_accounts']	= $ida_venta_iva;
			$params['amount']		= $dat_prod['Tax'];
			$rslt_fun = add_mov($params);
			$log .= ($rslt_fun != false) ? $rslt_fun.'<br />' : 'Error<br />';
			$log_sql .= ($rslt_fun != false) ? $rslt_fun : "; Error; \nROLLBACK;\n";
			// Venta Debit
			$params['id_accounts']	= $ida_venta_ant;
			$params['amount']		= $dat_prod['OrderTotal'];
			$params['credebit']		= 'Debit';
			$rslt_fun = add_mov($params);
			$log .= ($rslt_fun != false) ? $rslt_fun.'<br />' : 'Error<br />';
			$log_sql .= ($rslt_fun != false) ? $rslt_fun : "; Error; \nROLLBACK;\n";


			// Se obtienen los costos de cada producto escaneado
			$sql = "SELECT (sl_orders_parts.ID_parts + 400000000) ID_parts, SUM(sl_orders_parts.Quantity) Qty
					FROM sl_orders_products
					INNER JOIN sl_orders_parts USING(ID_orders_products)
					WHERE sl_orders_products.ID_orders = ".$orden['ID_orders']." 
						AND sl_orders_products.ID_products < 600000000 
						AND sl_orders_products.`Status` = 'Active'
					GROUP BY sl_orders_parts.ID_parts;";
			$log .= $sql.'<br />';
			$rslt_part = $conex->query($sql);

			$total_cost = 0;
			while( $part = $rslt_part->fetch_assoc() ){
				$sql = "SELECT sl_skus_trans.Cost_Avg
						FROM sl_skus_trans
						WHERE sl_skus_trans.ID_trs = ".$orden['ID_orders']." 
							AND sl_skus_trans.tbl_name = 'sl_orders' 
							AND sl_skus_trans.ID_products=".$part['ID_parts'].";";
				$log .= $sql.'<br />';
				$rslt_cost = $conex->query($sql);
				$dat_cost = $rslt_cost->fetch_assoc();

				$total_cost += ($dat_cost['Cost_Avg'] * $part['Qty']);
			}

			// Se generan los mov. de Costos
			$log .= 'Costos ====> <br />';
			$log_sql .= "/*------ Costos ------/\n";
			$params['id_accounts']	= $ida_costo_credit;
			$params['amount']		= $total_cost;
			$params['effdate']		= $dat_prod['ShpDate'];
			$params['tablerelated'] = 'cu_invoices';
			$params['id_tablerelated'] = $dat_fact['ID_invoices'];
			$params['category']		= 'Costos';
			$params['credebit']		= 'Credit';
			$params['execute']		= 0;
			// Costos Credit
			$rslt_fun = add_mov($params);
			$log .= ($rslt_fun != false) ? $rslt_fun.'<br />' : 'Error<br />';
			$log_sql .= ($rslt_fun != false) ? $rslt_fun : "; Error; \nROLLBACK;\n";
			// Costos Debit
			$params['id_accounts']	= $ida_costo_debit;
			$params['credebit']		= 'Debit';
			$rslt_fun = add_mov($params);
			$log .= ($rslt_fun != false) ? $rslt_fun.'<br />' : 'Error<br />';
			$log_sql .= ($rslt_fun != false) ? $rslt_fun : "; Error; \nROLLBACK;\n";
			*/

		}

		//$rslt = $conex->query($sql);
		
		$log .= '<br />=====================================================================<br />';
	}
	$sql = "COMMIT;";
	$log_sql .= "\n\nCOMMIT;";
	$log .= $sql.'<br /><br />';

	echo $log;

	$fp = fopen('fix_mov_mow_newsales.txt', 'w');
	fwrite($fp, $log_sql);
	fclose($fp);


function add_mov($params){
	$sql = "INSERT INTO sl_movements SET 
				ID_accounts=".$params['id_accounts']."
				, Amount=".$params['amount']."
				, EffDate='".$params['effdate']."'
				, tableused='sl_orders'
				, ID_tableused=".$params['id_orders']."
				, tablerelated='".$params['tablerelated']."'
				, ID_tablerelated=".$params['id_tablerelated']."
				, Category='".$params['category']."'
				, Credebit='".$params['credebit']."'
				, ID_segments=0
				, ID_journalentries=0
				, Status='Active'
				, Date=CURDATE()
				, Time=CURTIME()
				, ID_admin_users=11;\n";
	if( isset($params['execute']) && $params['execute'] == 1 ){
		if( $conex->query($sql) ){
			return $sql;
		}else{
			return false;
		}	
	}else{
		return $sql;
	}
}

?>