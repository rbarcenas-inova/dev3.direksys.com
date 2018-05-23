<?php
header("Last-Modified: " . gmdate("D, d M Y H:i:s") . " GMT");
header("Cache-Control: no-store, no-cache, must-revalidate, max-age=0");
header("Cache-Control: post-check=0, pre-check=0", false);
header("Pragma: no-cache");
header("Expires: Sat, 26 Jul 1997 05:00:00 GMT");

session_start();

ini_set('display_errors', '0');
error_reporting(0);

/*ini_set('display_startup_errors',1);
ini_set('display_errors', '1');
error_reporting(1);
error_reporting(E_ALL);*/

#echo "<br>entro";

/*if (isset($_REQUEST['RequestID']) and $_REQUEST['RequestID']) {*/

	#http://mx.direksys.com/cybersource_accept.php?RequestID=5071388211036066103049&OrderId=3352521&UpdatedStatus=ACCEPT&PayworksCode=00&PayworksText=ACCEPT&Date=04%2F10%2F2017+11%3A14%3A00

	require("nsAdmBase.php");

	$request = print_r($_REQUEST, true);

	$e = '12';#TESTING CAMBIAR A 12

	echo "<br>".$cfg['emp.'.$e.'.dbi_host'];
	echo "<br>".$cfg['emp.'.$e.'.dbi_user']; 
	echo "<br>".$cfg['emp.'.$e.'.dbi_pw'];
	echo "<br>".$cfg['emp.'.$e.'.dbi_db'];

	$conn = new mysqli('p:'.$cfg['emp.'.$e.'.dbi_host'], $cfg['emp.'.$e.'.dbi_user'], $cfg['emp.'.$e.'.dbi_pw'], $cfg['emp.'.$e.'.dbi_db']);
	if ($conn->connect_error) 
	{
		echo "Error: No se pudo conectar a MySQL.".PHP_EOL;
		echo $conn->connect_errno.PHP_EOL;
		echo $conn->connect_error.PHP_EOL;
		die();
	}
	$request = $conn->real_escape_string($request);
	$sql = "INSERT INTO sl_debug (cmd, id, log, Date, Time, ID_admin_users) VALUES ('cybersource_orig_req0', 9999, '".$request."', CURDATE(), CURTIME(), 6);";
	echo "<br>sql=".$sql;
	$conn->query($sql);

	#echo "<br><pre>request=".$request."</pre>";

	$myXMLData = trim($_REQUEST['content']); #TESTING DESCOMENTAR

	/*$myXMLData = trim(' <?xml version="1.0" encoding="UTF-8"?> <!DOCTYPE CaseManagementOrderStatus SYSTEM "https://ebctest.cybersource.com/ebctest/reports/dtd/cmorderstatus_1_1.dtd"> <CaseManagementOrderStatus xmlns="http://reports.cybersource.com/reports/cmos/1.0" MerchantID="banorteixe_inova1" Name="Case Management Order Status" Date="2017-10-26 17:15:19" Version="1.1"> <Update MerchantReferenceNumber="4457729" RequestID="5090561187016429503010"> <OriginalDecision>REVIEW</OriginalDecision>  <NewDecision>REJECT</NewDecision> <Reviewer>banorteixe_inova1</Reviewer> <ReviewerComments>This is a test message(1).</ReviewerComments> <Queue>TestQueue(1)</Queue> <Profile>TestProfile(1)</Profile> </Update> </CaseManagementOrderStatus>');*/
	$myXMLData = preg_replace('~<(?:!DOCTYPE|/?(?:html|body))[^>]*>\s*~i', '', $myXMLData);

	$xml = simplexml_load_string($myXMLData) or die("Error: Cannot create object");

	$RequestID = trim($xml->Update[0]['RequestID']);
	$OrderId = trim($xml->Update[0]['MerchantReferenceNumber']);
	#$UpdatedStatus = trim($xml->Update[0]->OriginalDecision);
	$NewDecision = trim($xml->Update[0]->NewDecision);

	$myXMLData = $conn->real_escape_string($myXMLData);
	$sql = "INSERT INTO sl_debug (cmd, id, log, Date, Time, ID_admin_users) VALUES ('cybersource_parse_xml', 9999, '".$myXMLData."', CURDATE(), CURTIME(), 6);";
	echo "<br>sql=".$sql;
	$conn->query($sql);

	$sql = "INSERT INTO sl_debug (cmd, id, log, Date, Time, ID_admin_users) VALUES ('cybersource_parse_requestid', 9999, '".$RequestID."', CURDATE(), CURTIME(), 6);";
	echo "<br>sql=".$sql;
	$conn->query($sql);

	$sql = "INSERT INTO sl_debug (cmd, id, log, Date, Time, ID_admin_users) VALUES ('cybersource_parse_orderid', 9999, '".$OrderId."', CURDATE(), CURTIME(), 6);";
	echo "<br>sql=".$sql;
	$conn->query($sql);

	$sql = "INSERT INTO sl_debug (cmd, id, log, Date, Time, ID_admin_users) VALUES ('cybersource_parse_newdesicion', 9999, '".$NewDecision."', CURDATE(), CURTIME(), 6);";
	echo "<br>sql=".$sql;
	$conn->query($sql);

	echo "<br>RequestID=".$RequestID;
	echo "<br>OrderId=".$OrderId;
	echo "<br>NewDecision=".$NewDecision;

	mysqli_close($conn);

	if ($OrderId > 3000000) {
		$e = '4';
		$conn = new mysqli('p:'.$cfg['emp.'.$e.'.dbi_host'], $cfg['emp.'.$e.'.dbi_user'], $cfg['emp.'.$e.'.dbi_pw'], $cfg['emp.'.$e.'.dbi_db']);
		if ($conn->connect_error) 
		{
			echo "Error: No se pudo conectar a MySQL.".PHP_EOL;
			echo $conn->connect_errno.PHP_EOL;
			echo $conn->connect_error.PHP_EOL;
			die();
		}
	} else {
		$e = '2';
		$conn = new mysqli('p:'.$cfg['emp.'.$e.'.dbi_host'], $cfg['emp.'.$e.'.dbi_user'], $cfg['emp.'.$e.'.dbi_pw'], $cfg['emp.'.$e.'.dbi_db']);
		if ($conn->connect_error) 
		{
			echo "Error: No se pudo conectar a MySQL.".PHP_EOL;
			echo $conn->connect_errno.PHP_EOL;
			echo $conn->connect_error.PHP_EOL;
			die();
		}
	}
	echo "<br>e=".$e;
	echo "<br>".$cfg['emp.'.$e.'.dbi_host'];
	echo "<br>".$cfg['emp.'.$e.'.dbi_user']; 
	echo "<br>".$cfg['emp.'.$e.'.dbi_pw'];
	echo "<br>".$cfg['emp.'.$e.'.dbi_db'];

	$sql = "SELECT sl_orders_payments_cybersource.ID_orders, sl_orders_payments_cybersource.ID_orders_payments
			FROM sl_orders_payments_cybersource
			INNER JOIN sl_orders_plogs ON sl_orders_plogs.ID_orders_payments = sl_orders_payments_cybersource.ID_orders_payments
				AND sl_orders_plogs.Data LIKE '%CYBERSOURCE%'
				AND sl_orders_plogs.Resp_code = ".$RequestID."
				#AND sl_orders_plogs.Resp_msg = 'REVIEW'
			WHERE sl_orders_payments_cybersource.ID_unique_cybersource = ".$OrderId."
			ORDER BY sl_orders_plogs.ID_orders_plogs DESC
			LIMIT 1;";

	$res = $conn->query($sql);
	$row = $res->fetch_assoc();

	echo "<br><pre>sql=".$sql."</pre>";
	echo "<br>ID_orders=".$row['ID_orders'];

	if ($row['ID_orders'] > 0) {

		$sql = "INSERT INTO sl_debug (cmd, id, log, Date, Time, ID_admin_users) VALUES ('cybersource_orig_req', $row[ID_orders], '".$request."', CURDATE(), CURTIME(), 6);";
		echo "<br>sql=".$sql;
		$conn->query($sql);

		$sql = "INSERT INTO sl_debug (cmd, id, log, Date, Time, ID_admin_users) VALUES ('cybersource_desicion', $row[ID_orders], '".$NewDecision."', CURDATE(), CURTIME(), 6);";
		echo "<br>sql=".$sql;
		$conn->query($sql);

		if ($NewDecision == 'ACCEPT') {

			$NewCode = '000';

			$sql = "INSERT INTO sl_debug (cmd, id, log, Date, Time, ID_admin_users) VALUES ('cybersource_review_accept', $row[ID_orders], '".$request."', CURDATE(), CURTIME(), 6);";
			$conn->query($sql);

			$actual_link = (isset($_SERVER['HTTPS']) ? "https" : "http") . "://$_SERVER[HTTP_HOST]/".basename(__FILE__);
			# Datos que se envian al log

			$data_log =  "============================================\n";
			$data_log .= "CYBERSOURCE MODE MANUALREVIEW \n";
			$data_log .= "============================================\n";
			$data_log .= "> > > Submited Info > > >\n\n";
			$data_log .= "IP1: ".get_ip()."\n";
			$data_log .= "IP2: ".$actual_link."\n";

			$callback2 = function ($value, $key) use (&$data_log) {
				$data_log .= $key.": ".utf8_decode($value)."\n";
			};
			array_walk_recursive($_REQUEST, $callback2);

			$sql2 = "SELECT Status FROM sl_orders_payments WHERE sl_orders_payments.ID_orders_payments = $row[ID_orders_payments];";

			$res2 = $conn->query($sql2);
			$row2 = $res2->fetch_assoc();

			echo "<br><pre>sql=".$sql2."</pre>";
			echo "<br>Status=".$row2['Status'];

			$sql = "INSERT INTO sl_debug (cmd, id, log, Date, Time, ID_admin_users) VALUES ('cybersource_status_pay', $row[ID_orders], '".$row2['Status']."', CURDATE(), CURTIME(), 6);";
			echo "<br>sql=".$sql;
			$conn->query($sql);

			if ($row2['Status'] == 'Approved') {

				#echo "<br>entro3";

				$data_log = $conn->real_escape_string($data_log);
				$NewDecision = $conn->real_escape_string($NewDecision);
				$NewCode = $conn->real_escape_string($NewCode);

				$sql = "INSERT INTO sl_orders_plogs SET ID_orders=$row[ID_orders]
						, ID_orders_payments=$row[ID_orders_payments]
						, Data='".$data_log."'
						, Resp_msg='".$NewDecision."'
						, Resp_code='".$NewCode."'
						, Date=CURDATE()
						, Time=CURTIME()
						, ID_admin_users=1";
				$conn->query($sql);

				#REQUEST TO PAYMENTGATEWAY
				$url = $cfg['url_paymentgateway']."?cmd=auth&id=".$row['ID_orders']."&idp=".$row['ID_orders_payments']."&idu=1&cybersource_id=".$RequestID."&e=".$e."&cybersource_review=1";
				echo "<br>".$url;

				$res_payw = file_get_contents($url);

				$url = $conn->real_escape_string($url);
				$sql = "INSERT INTO sl_debug (cmd, id, log, Date, Time, ID_admin_users) VALUES ('cybersource_url', $row[ID_orders], '".$url."', CURDATE(), CURTIME(), 6);";
				echo "<br>sql=".$sql;
				$conn->query($sql);
				echo "<br>res_payw=".$res_payw;
				$res_payw = $conn->real_escape_string($res_payw);
				$sql = "INSERT INTO sl_debug (cmd, id, log, Date, Time, ID_admin_users) VALUES ('cybersource_res_paymtgtwy', $row[ID_orders], '".$res_payw."', CURDATE(), CURTIME(), 6);";
				$conn->query($sql);
				echo "<br>sql=".$sql;
			} else {
				$data_log .= "CANNOT SEND TO PAYWORKS\n";
				$data_log .= "Status Payment:".$row2['Status']."\n";
				$NewDecision = 'THIS PAYMENT IS CANCELED';
				$NewCode = '0010';

				$data_log = $conn->real_escape_string($data_log);
				$NewDecision = $conn->real_escape_string($NewDecision);
				$NewCode = $conn->real_escape_string($NewCode);

				$sql = "INSERT INTO sl_orders_plogs SET ID_orders=$row[ID_orders]
						, ID_orders_payments=$row[ID_orders_payments]
						, Data='".$data_log."'
						, Resp_msg='".$NewDecision."'
						, Resp_code='".$NewCode."'
						, Date=CURDATE()
						, Time=CURTIME()
						, ID_admin_users=1";
				$conn->query($sql);
			}
		} else {
			$NewCode = '001';
			$sql = "UPDATE sl_orders SET Status = IF(Status = 'Shipped', Status, 'Cancelled'), StatusPay='None' WHERE ID_orders=$row[ID_orders];";

			$conn->query($sql);

			$sql = "INSERT INTO sl_orders_notes 
						SET ID_orders = $row[ID_orders],
						Notes = 'Cybersource ManualReview - Rejected Final Desicion -  Order changed to Cancelled',
						Type = 'High',
						ID_orders_notes_types = '3',
						Date = CURDATE(),
						Time = CURTIME(),
						ID_admin_users = 1;";

			$conn->query($sql);

			$sql = "INSERT INTO sl_debug (cmd, id, log, Date, Time, ID_admin_users) VALUES ('cybersource_reject', $row[ID_orders], '".$request."', CURDATE(), CURTIME(), 6);";
			$conn->query($sql);

			$actual_link = (isset($_SERVER['HTTPS']) ? "https" : "http") . "://$_SERVER[HTTP_HOST]/".basename(__FILE__);
			# Datos que se envian al log

			$data_log =  "============================================\n";
			$data_log .= "CYBERSOURCE MODE MANUALREVIEW \n";
			$data_log .= "============================================\n";
			$data_log .= "\n\n\n< < < Reply Info < < <\n\n";
			$data_log .= "IP1: ".get_ip()."\n";
			$data_log .= "IP2: ".$actual_link."\n";

			$callback2 = function ($value, $key) use (&$data_log) {
				$data_log .= $key.": ".utf8_decode($value)."\n";
			};
			array_walk_recursive($_REQUEST, $callback2);

			$data_log = $conn->real_escape_string($data_log);
			$NewDecision = $conn->real_escape_string($NewDecision);
			$NewCode = $conn->real_escape_string($NewCode);

			 $sql = "INSERT INTO sl_orders_plogs SET ID_orders=$row[ID_orders]
					, ID_orders_payments=$row[ID_orders_payments]
					, Data='".$data_log."'
					, Resp_msg='".$NewDecision."'
					, Resp_code='".$NewCode."'
					, Date=CURDATE()
					, Time=CURTIME()
					, ID_admin_users=1";
			$conn->query($sql);
		}
	} else {
		$sql = "INSERT INTO sl_debug (cmd, id, log, Date, Time, ID_admin_users) VALUES ('cybersource_orig_req_fail', 999, '".$request."', CURDATE(), CURTIME(), 6);";
		echo "<br>sql=".$sql;
		$conn->query($sql);
	}
	mysqli_close($conn);
/*}*/
session_destroy();