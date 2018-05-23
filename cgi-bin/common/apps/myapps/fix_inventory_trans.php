<?php
	
	require("../../../httpdocs/nsAdmBase.php");

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

	error_reporting(E_ALL);

	$skus = array(
		400008741
		);
	$costos = array(
		479.19
		);

	$skus_especial = "";
	$total_process = 0;
	$total_especial = 0;

	$log .= "Analizando los movimientos de SKUs\n<br>";
	$conex->query("START TRANSACTION;");
	$log .= "===> START TRANSACTION;\n<br>";
	foreach ($skus as $key => $sku) {
		$log .= "------------------------------------------------------------------\n<br>";
		$log .= "==> Analizando el SKU: $sku  :: Cost: ".$costos[$key]."\n<br>";
		$log .= "------------------------------------------------------------------\n<br>";

		$sql_chk = "Select Count(*) trans From sl_skus_trans 
					Where 1 
						And ID_products = $sku 
						And Date>='2015-11-27'
						And Date<'2015-11-28'
						And ID_products_trans < 318562						
						And tbl_name In('sl_parts_productions', 'sl_skustransfers', 'sl_wreceipts', 'sl_returns');";
		$rslt_chk = $conex->query($sql_chk)->fetch_assoc();
		if( (int)$rslt_chk["trans"] == 0 ){
			$sql_trans = "Select * From sl_skus_trans 
							Where 1 And ID_products = $sku And Date>='2015-11-27' And Date<'2015-11-28' And ID_products_trans < 318562
							Order by ID_products_trans Asc Limit 5000;";
			$rslt_trans = $conex->query($sql_trans);
			$id_trans_ant = 0;
			while ( $ftrans = $rslt_trans->fetch_assoc() ) {
				$log .= "ID_trs: ".$ftrans["ID_trs"].", Type: ".$ftrans["Type"].", tbl_name: ".$ftrans["tbl_name"]."\n<br>";

				// Se rastrea la orden y su contabilidad
				if( $ftrans["Type"] == "Sale" && $ftrans["tbl_name"] == "sl_orders" ){

					if( $ftrans["ID_trs"] != $id_trans_ant ){
						$sql_dat = "Select ROUND(".$costos[$key]." * sl_orders_products.Quantity, 3) Total_Cost_OK
										, sl_orders_products.ID_orders_products, sl_orders_products.Related_ID_products
										, sl_orders_products.ID_orders, sl_orders_products.Quantity
										, sl_orders_products.Cost, sl_orders_parts.Cost UnitCost
									From sl_orders_products 
										Inner Join sl_orders_parts Using(ID_orders_products)
									Where sl_orders_products.ID_orders=".$ftrans["ID_trs"]." 
										And sl_orders_parts.ID_parts=$sku - 400000000;";
						$rslt_dat = $conex->query($sql_dat);
						while ( $fdat = $rslt_dat->fetch_assoc() ) {
							
							$log .= "ID_orders_products: ".$fdat["ID_orders_products"].", Quantity: ".$fdat["Quantity"].", Cost: ".$fdat["Cost"].", UnitCost: ".$fdat["UnitCost"]."\n<br>";

							// sl_orders_products
							$sql_upd_prods = "Update sl_orders_products Set Cost = ".$fdat["Total_Cost_OK"]." Where ID_orders_products = ".$fdat["ID_orders_products"].";";
							$conex->query($sql_upd_prods);
							$log .= $sql_upd_prods."\n<br>";

							// sl_orders_parts
							$sql_upd_parts = "Update sl_orders_parts Set Cost = ".$costos[$key]." Where ID_orders_products = ".$fdat["ID_orders_products"]." And sl_orders_parts.ID_parts = $sku - 400000000;";
							$conex->query($sql_upd_parts);
							$log .= $sql_upd_parts."\n<br>";

							// sl_movements
							$sql_mov = "Select Group_Concat(ID_movements) ids_mov From sl_movements Where tableused='sl_orders' And ID_tableused=".$ftrans["ID_trs"]." And Amount=".$fdat["Cost"]." And Category='Costos' Limit 2;";
							$log .= $sql_mov."\n<br>";
							$rslt_mov = $conex->query($sql_mov);
							$dat_mov = $rslt_mov->fetch_assoc();
							$log .= "IDs Movements: ".$dat_mov["ids_mov"]."\n<br>";
							if( !empty($dat_mov["ids_mov"]) ){
								$sql_upd_mov = "Update sl_movements Set Amount = ".$fdat["Total_Cost_OK"]." Where ID_movements In(".$dat_mov["ids_mov"].");";
								$conex->query($sql_upd_mov);
								$log .= $sql_upd_mov."\n<br>";
							}
						}

					}else{
						$log .= "Procesada en la iteracion anterior...\n<br>";
					}
					$sql_upd_trans = "Update sl_skus_trans Set Cost_Avg = $costos[$key], Cost = $costos[$key] Where ID_products_trans = ".$ftrans["ID_products_trans"].";";
					$conex->query($sql_upd_trans);
					$log .= $sql_upd_trans."\n<br>";
					$id_trans_ant = $ftrans["ID_trs"];

				// Solo se corrige el Cost_Avg y Cost
				}else{
					$sql_upd_trans = "Update sl_skus_trans Set Cost_Avg = $costos[$key], Cost = $costos[$key] Where ID_products_trans = ".$ftrans["ID_products_trans"].";";
					$conex->query($sql_upd_trans);
					$log .= $sql_upd_trans."\n<br>";
				}
				$log .= "\n<br>";
			}

			$total_process++;
		}else{
			$log .= "Tiene movimientos especiales\n<br>";
			$skus_especial .= $sku."\n<br>";
			$total_especial++;
		}
		$log .= "------------------------------------------------------------------\n<br>";
		$log .= "\n<br>";
	}
	//$conex->query("COMMIT;");
	$conex->query("ROLLBACK;");
	$log .= " <=== ROLLBACK;\n<br>";

	echo $log;

	echo "SKUs Procesados : $total_process\n<br>";
	echo "SKUs Especiales : $total_especial\n<br>";
	echo $skus_especial;
?>