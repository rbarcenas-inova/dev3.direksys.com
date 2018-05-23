#!/usr/bin/php -q
<?php

$cfg['dbi_db']   = 'asteriskcdrdb';
$cfg['dbi_pw']   = 's11tos7';
$cfg['dbi_user'] = 'devmia';
$cfg['dbi_host'] = '63.95.246.130';
$cfg['file'] = '/home/www/domains/direksys.com/files/progfiles/lost_calls_'.date('d-m-Y').'.txt';

mysql_pconnect ($cfg['dbi_host'], $cfg['dbi_user'], $cfg['dbi_pw']) or die('Error 0000000001 ');
mysql_select_db ($cfg['dbi_db']) or die('Error 0000000002 ');

/*
$allowed_ip  = '63.95.246.135';
#$this_client = $_SERVER['REMOTE_ADDR'];

$this_client = 


$queryip = "SELECT IF( INET_ATON( '$allowed_ip' ) = INET_ATON( '$this_client' ) , 'ok', 'attack' ) ;";
$xip = mysql_query($queryip);
list($this_valid_ip) = mysql_fetch_row($xip);

echo "$queryip \n $allowed_ip - $this_client -- $this_valid_ip\n\n";

if($this_valid_ip == 'ok'){
*/
	## DIDS No USA (Excluir)
	$sthd = mysql_query("SELECT GROUP_CONCAT(`didusa`) FROM `sl_numbers` WHERE `grupo` <> 'US';");
	list($dids_nousa) = mysql_fetch_row($sthd);
	$ary_dids_nousa = explode(',',$dids_nousa);


	$querydays  = "SELECT DATE_FORMAT(DATE_SUB(CURDATE(), INTERVAL 1 DAY),GET_FORMAT(DATETIME,'ISO'))AS FromDate,NOW() AS ToDate";
	$queryhours = "SELECT DATE_FORMAT( SUBTIME( NOW( ) , '02:00:00' ) , GET_FORMAT( DATETIME, 'ISO' ) ) AS FromDate, DATE_FORMAT( SUBTIME( NOW( ) , '01:00:00' ) , GET_FORMAT( DATETIME, 'ISO' ) ) AS ToDate";


	$sth = mysql_query($queryhours);
	list($arr_parameters[ 'StartDate' ], $arr_parameters[ 'EndDate' ]) = mysql_fetch_row($sth);


	$Auth = new SoapClient( 'https://services.inphonex.com/0.7/soap/Auth/Auth.php?wsdl' );
	$arr_parameters[ 'AuthSet' ][ 'auth' ][ 'username' ] = '6218';
	$arr_parameters[ 'AuthSet' ][ 'auth' ][ 'password' ] = 'shopping';
	$arr_parameters[ 'AuthSet' ][ 'type' ] = 'reseller';
	$arr_parameters[ 'AuthSet' ][ 'test_mode' ] = 'true';
	try {
		$stateID = $Auth->Login( $arr_parameters )->LoginReturn;

		$Call = new SoapClient( 'https://services.inphonex.com/0.7/soap/Calls/Call.php?wsdl' );
		$arr_parameters[ 'StateId' ] = $stateID;
		#$arr_parameters[ 'StartDate' ] = '2011-08-08 00:00:00';
		#$arr_parameters[ 'EndDate' ] = '2011-08-08 23:59:59';
		$arr_parameters[ 'CallSearch' ][ 'start_row' ] = '0';
		$arr_parameters[ 'CallSearch' ][ 'limit' ] = '100';
		#$arr_parameters[ 'CallSearch' ][ 'customer_id' ] = '999999';
		#$arr_parameters[ 'CallSearch' ][ 'virtual_number' ] = '1235566';
		$arr_parameters[ 'CallSearch' ][ 'call_duration' ] = '0';

		$arr_parameters[ 'CallSearch' ][ 'disposition' ] = 'CANCELED';
		#$arr_parameters[ 'CallSearch' ][ 'ani' ] = '12345678';
		#$arr_parameters[ 'CallSearch' ][ 'called_number' ] = '33224455';
		#print_r($arr_parameters);
		try {
			$obj_return = $Call->ListCalls( $arr_parameters )->ListCallsReturn;


			## Guardamos la fecha en que se corrio
			$fp = fopen($cfg['file'], 'a');
			fwrite($fp, 'From:'.$arr_parameters[ 'StartDate' ]."\nTo:".$arr_parameters[ 'EndDate' ]."\n");
			fclose($fp);

			#print_r($obj_return);
			#$a = xml_parse($obj_return);

			foreach($obj_return as $keys=>$values){
				if(is_array($values)){
					$string .= "TOTAL Calls :".$obj_return->total_rows ."\n\n";
					foreach($values as $calls){
						#print_r($calls);
						if ($calls->call_duration <= 5  and $calls->did >00){
							++$drop;
						}
						
						## Excluir DID no USA
						if(in_array($calls->virtual_number,$ary_dids_nousa) === TRUE ){
							$string .= "Src: " . $calls->ani . "\nDID Not USA: " . $calls->virtual_number . "\n\n";
							continue;
						}
		

						$ani = $calls->ani ;
						$sth = mysql_query("SELECT COUNT(*) FROM `cdr` WHERE `src` = '$ani' AND DATE(calldate) = DATE('".$arr_parameters[ 'StartDate' ]."') ");
						$matches =  mysql_fetch_row($sth);
						if ($matches[0] == 0){
							$calldate = $calls->call_date;
							$clid = $calls->ani;
							$src = $calls->ani;
							$dst = '';
							$dcontext = 'from-lost';
							$channel = 'SIP/'.$calls->called_number;
							$dstchannel = 'IAX2/vixicom2-Lost';
							$lastapp = 'Dial';
							$lastdata = '';
							$duration = $calls->call_duration;
							$billsec = $calls->call_duration;
							$disposition = $calls->disposition;
							$amaflags = 3;
							$accountcode = $calls->virtual_number;
							$uniqueid = $calls->unique_id;
							$userfield = '';
							#$calls->founded='no';
							#$string .="\n$ani No Call\n";

							$query = "INSERT INTO `cdr` (`calldate`, `clid`, `src`, `dst`, `dcontext`, `channel`, `dstchannel`, `lastapp`, `lastdata`, `duration`, `billsec`, `disposition`, `amaflags`, `accountcode`, `uniqueid`, `userfield`) VALUES ";
							$query .= "('$calldate', '<$clid>','$src', '$dst', '$dcontext', '$channel', '$dstchannel', '$lastapp','$lastdata',$duration ,$billsec ,'$disposition',$amaflags,'$accountcode','$uniqueid','$userfield');";
							mysql_query($query);

							$string .="$query\n";

							++$lost;
						}
					}

				}else if(is_object($values)){
					$string .= ">>>> object $keys\n";
					foreach($values as $keysv=>$valuesv){
						$string .="$keysv=$valuesv\n";
					}
				}else{
					$string .= "$keys=$values\n";
				}
			}


			$fp = fopen($cfg['file'], 'a');
			fwrite($fp, $string ."\n");
			fclose($fp);
			unset($string);


			#print "\n\n\n";
			#print_r($obj_return);
			#print $obj_return[0][0];
		} catch ( Exception $e ) {

			$fp = fopen($cfg['file'], 'a');
			fwrite($fp,$e->getMessage());
			fclose($fp);
			exit;
		}

		$fp = fopen($cfg['file'], 'a');
		fwrite($fp, "Total Drop: $drop\nTotal Lost: $lost\n\n");
		fclose($fp);
		unset($lost);
		echo "End OK\n";
	} catch ( Exception $e ) {
		echo $e->getMessage();
		exit;
	}

/*
}else{

	$fp = fopen($cfg['file'], 'a');
	fwrite($fp, "Possible Attack From IP:$this_client \n\n");
	fclose($fp);

}
*/

  ?>
