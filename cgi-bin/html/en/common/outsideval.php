<?php
$ip = $_SERVER["REMOTE_ADDR"];

if( !empty($ip) ){
	$aip = explode(".", $ip);
	if( $aip[0] == "172" and $aip[1] == "20" ){
		$json_rslt["result"] = "in";
	}elseif( $aip[0] == "192" and $aip[1] == "168" and ($aip[2] == "11" or $aip[2] == "3") ){
		$json_rslt["result"] = "in";
	}else{
		$json_rslt["result"] = "out";	
	}
}else{
	$json_rslt["result"] = "out";
}

echo json_encode($json_rslt);
?>