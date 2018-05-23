<?php
	$server = "172.20.27.78";
	$dbname = "direksys2_e";
	$user = "d2tmk";
	$pswd = "BVkdsU839*&783gsklNslkbHs";

	// Empresa (default e11)
	$dbname .= ( isset($_GET["e"]) && !empty($_GET["e"]) ) ? (int)$_GET["e"] : 2;

	error_reporting(E_ALL);

	// Conexion
	$conex = new mysqli($server, $user, $pswd, $dbname);
	if ($conex->connect_errno) {
	    echo "ERROR: (" . $conex->connect_errno . ") " . $conex->connect_error;
	}

	$fecha = '2015-10-31';
	$conex->query("set @date=$fecha");

	$orders = array(
9835283,
9835459,
9835857,
9836364,
9837203,
9837230,
9837297,
9837355,
9837793,
9838656,
9839383,
9839422,
9839485,
9839515,
9840192,
9840286,
9840287,
9840458,
9840511,
9840587,
9840624,
9840876,
9840877,
9840920,
9841233,
9841708,
9841792,
9841843,
9842014,
9842313,
9842318,
9842323,
9842328,
9842333,
9842340,
9842489,
9842548,
9842561,
9843393,
9843430,
9843530,
9843770,
9843800,
9843815,
9843824,
9844610,
9844763,
9844812,
9845257,
9845649,
9845815,
9845839,
9845938,
9845958,
9846554,
9846637,
9846711,
9846858,
9847194,
9847410,
9848395,
9848452,
9848949,
9849279,
9849564,
9849845,
9849993,
9850133,
9850161,
9850381,
9850384,
9850404,
9850410,
9850730,
9850881,
9851107,
9851380,
9851662,
9851680,
9851683,
9851726,
9852323,
9852353,
9852579,
9852816,
9853031,
9853238,
9853633,
9854934,
9855248,
9855337,
9855397,
9855883,
9857074,
9857373,
9857622,
9858406,
9859431,
9859753);


	$log = '';
		
	foreach ($orders as $id_orders) {
		$sql = "START TRANSACTION;";
		$log .= $sql.'<br /><br />';
		$rslt = $conex->query($sql);

		$sql = "Update sl_movements Set Status = 'Inactive'	
				Where tableused='sl_orders' And ID_tableused=".$id_orders." And ID_accounts=1244 And Category='Ventas' And Amount < 1 And Credebit='Credit' And Status='Active';";
		$log .= $sql.'<br /><br />';
		$conex->query($sql);

		$sql = "Update sl_movements Set Amount = (Select Round(Sum(SalePrice-Discount),2) From sl_orders_products Where ID_orders=".$id_orders.")	
				Where tableused='sl_orders' And ID_tableused=".$id_orders." And ID_accounts=1244 And Category='Ventas'	And Credebit='Credit' And Status='Active';";
		$log .= $sql.'<br /><br />';
		$conex->query($sql);

		$sql = "Update sl_movements Set Amount = (Select Round(Sum(Shipping),2) From sl_orders_products Where ID_orders=".$id_orders.")	
				Where tableused='sl_orders' And ID_tableused=".$id_orders." And ID_accounts=1245 And Category='Ventas'	And Credebit='Credit' And Status='Active';";
		$log .= $sql.'<br /><br />';
		$conex->query($sql);

		$sql = "Select ID_accounts From sl_movements
				Where tableused='sl_orders' And ID_tableused=".$id_orders." And ID_accounts=1245 And Category='Ventas'	And Credebit='Credit' And Status='Active';";
		$rslt = $conex->query($sql);
		$dat = $rslt->fetch_assoc();
		if( empty($dat['ID_accounts']) ){
			$sql = "Select EffDate, tablerelated, ID_tablerelated From sl_movements
					Where tableused='sl_orders' And ID_tableused=".$id_orders." And ID_accounts=1244 And Category='Ventas'	And Credebit='Credit' And Status='Active';";
			$rslt = $conex->query($sql);
			$dat_mov = $rslt->fetch_assoc();

			$sql = "Insert Into sl_movements Set ID_accounts=1245, Amount=(Select Round(Sum(Shipping),2) From sl_orders_products Where ID_orders=".$id_orders."), 
						EffDate='".$dat_mov['EffDate']."', tableused='sl_orders', ID_tableused=".$id_orders.", tablerelated='".$dat_mov['tablerelated']."', 
						ID_tablerelated=".$dat_mov['ID_tablerelated'].", Category='Ventas', Credebit='Credit', ID_segments=0, ID_journalentries=0, 
						Status='Active', Date=curdate(), Time=curtime(), ID_admin_users=1;";
			$conex->query($sql);
			$log .= $sql.'<br /><br />';
		}

		$sql = "Update sl_movements Set Amount = (Select Round(Sum(Tax+ShpTax),2) From sl_orders_products Where ID_orders=".$id_orders.")	
				Where tableused='sl_orders' And ID_tableused=".$id_orders." And ID_accounts=1188 And Category='Ventas'	And Credebit='Credit' And Status='Active';";
		$conex->query($sql);
		$log .= $sql.'<br /><br />';

		$sql = "Update sl_movements Set Status = 'Inactive'
				Where tableused='sl_orders' And ID_tableused=".$id_orders." And ID_accounts=1074 And Category='Ventas'	And Credebit='Credit' And Status='Active';";
		$conex->query($sql);

		$sql = "Select Sum(Amount) Suma From sl_movements
				Where tableused='sl_orders' And ID_tableused=".$id_orders." And Category='Ventas' And Credebit='Credit' And Status='Active';";
		$rslt = $conex->query($sql);
		$sum_mov1 = $rslt->fetch_assoc();

		$sql = "Select Sum(Amount) Suma From sl_movements
				Where tableused='sl_orders' And ID_tableused=".$id_orders." And Category='Ventas' And Credebit='Debit' And Status='Active';";
		$rslt = $conex->query($sql);
		$sum_mov2 = $rslt->fetch_assoc();

		$diff = abs($sum_mov1['Suma'] - $sum_mov2['Suma']);
		$log .= $diff.'<br /><br />';

		if( $diff > 0.5 ){			
			$sql = "ROLLBACK;";
			$log .= $sql.'<br /><br />';
			$rslt = $conex->query($sql);
		}else{
			$sql = "COMMIT;";
			$log .= $sql.'<br /><br />';
			$rslt = $conex->query($sql);
		}

		$log .= $sql.'<br />=====================================================================<br />';
	}
	
	echo $log;

?>