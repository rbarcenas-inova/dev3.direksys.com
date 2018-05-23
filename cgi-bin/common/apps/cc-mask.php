#!/usr/bin/php -q
<?php
	require("../../../httpdocs/nsAdmBase.php");
 	require("../../../httpdocs/functions.php");

	$sth = mysql_query("SELECT ID_orders_payments, PmtField3 FROM sl_orders_payments 
						WHERE LENGTH(PmtField3) > 10 ORDER BY ID_orders_payments;");
	while(list($id,$cc) = mysql_fetch_row($sth)){
		$ccnew = encrip($cc);
		$q = "UPDATE sl_orders_payments SET PmtField3='$ccnew' WHERE ID_orders_payments = $id;";
		$sth2 = mysql_query($q);
		echo "CC: $cc\nNew:".$ccnew."\n$q\n\n";
		unset($q);
	}

?>