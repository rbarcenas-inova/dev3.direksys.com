<!DOCTYPE html>
<html>
<head>
	<meta charset="UTF-8">
	<title>Monitor de Replicación</title>

	<style type="text/css">
		.tbserver{
			border-collapse: collapse;
			border-left: 2px solid gray;
			border-right: 2px solid gray;
			border-bottom: 2px solid gray;
			float: left;
			font-family: arial, sans-serif;
			font-size: 10pt;
			margin: 3px;
			width: auto;
		}
		.tbserver thead{
			width: 100%;
		}
		.tbserver thead th{
			background-color: #B2B1B1;
			border-top: 2px double gray;
			border-bottom: 2px double gray;
			padding: 3px 7px 3px 7px;
		}
		.tbserver tbody{
			width: 100%;
		}
		.tbserver tbody td{
			padding: 3px 7px 3px 7px;
		}
		.tdchannel{
			background-color: #D3D3D3;
		}
		.tdlastrow{
			color: #002661;
		}
		.dverror{
			border: 1px dotted gray; 
			font-size: 8pt;
			font-weight: normal;
			max-width: 260px; 
			overflow: auto; 
			padding: 3px;
		}
		.spnsucess{
			background-color: green; 
			border-radius: 8px;
			color: white; 
			display: block; 
			font-weight: bold; 
			padding: 3px 2px 3px 7px;
			width: auto;
		}
		.spnerror{
			background-color: red; 
			border-radius: 8px;
			color: white; 
			display: block; 
			font-weight: bold; 
			padding: 3px 2px 3px 7px;
			width: auto;
		}
	</style>

	<script type="text/javascript">
		// Se actualiza la página cada 3 min.
		setTimeout(function(){ location.reload(); }, 180000);
	</script>

</head>
<body>

<?php

	ini_set('display_errors', 1);
	ini_set('display_startup_errors', 1);
	error_reporting(E_ERROR);

	date_default_timezone_set("America/Mexico_City");

	//====================================================================================================
	// $api_url = 'http://gq.apidireksys.com/api/replication/monitor?';
	$api_url = 'https://api.direksys.com/api/replication/monitor?';
	// $api_token = 'eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiIsImp0aSI6IjA2OTkzNGUwZDRkOTE5ZmE5NGQ4ZDUyNTdhMzM0YWJjOWNmMjJjZmVlYTJjYzkxZWQxM2NlM2UyMTJjMjhlODZiOGU4N2ZjZTUwYzU2NDM5In0.eyJhdWQiOiIxNSIsImp0aSI6IjA2OTkzNGUwZDRkOTE5ZmE5NGQ4ZDUyNTdhMzM0YWJjOWNmMjJjZmVlYTJjYzkxZWQxM2NlM2UyMTJjMjhlODZiOGU4N2ZjZTUwYzU2NDM5IiwiaWF0IjoxNTAzNjE5NTQ1LCJuYmYiOjE1MDM2MTk1NDUsImV4cCI6MTgxOTE1MjM0NCwic3ViIjoiMTMiLCJzY29wZXMiOltdfQ.0D0BpsS03MqJZz-Q1iGs7-Ma9RbpUzwtzGumbo0gMFfL25d5C-hag3vo3lxnM9oZWMrNLzkKl1uDpr2Z8-us_GtJfLnCRYJB2veH3iTaEctccFvEWUM6HRsIQcfu0JGS_EkIki3y9ruZZ-IcGfcte7KWdQIOFwCQbCh7EimYd5O--fPOmGwtSYUSeJuN2uF5KpoQZOVK-BxXHX3VnA_QEb-MbC-Aqe1d42b61TDbjOQ3EtdY07aaIim1GONYKrZ7Emx926kqJlnljg4H11WZ05fynbffPXohDe1bxBDH6l8rgz_GZqNB_XQ6DND-VhQAPIE7AqfpbGZozpdadV7BNhEJdNp9nkpTvE-0Ts_Ig6QCwUHlSd8sSEgZXW8qDnZ6i98bXAYYSgyDYksqTaMJTAbC_cSYFPHhHWf-6wqtOGTx7wuYax8E4X-nZYQ90hwo4FS97dWLirbx5b2vcHe-Xzq1uqYnd5W4UrKS7A1ZX3xOZovOleNDoeG1WUKhMfFr7iICFHhpdhuZjZ_enLI2dN0HhRV9BBRaUF6crgicF7gAExy_Ue2OS2DY9Yd2k0LWgAQF2BsCQnZr9gIjzP3OYG7UsxdtWsWoSofrsL4FA6x-BwRZa9WWoh5Mexjrlv1MG50h6AKobLU8hJ2FLqY3tg7ItqjsT2bHvIYIdhblc9c';
	$api_token = 'eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiIsImp0aSI6ImQ4MjY0ZTczNTcxZWQ3OWMyZGI0MDYwMTA5YjA1OTk4Y2Y1Y2IxYjk1MGJlMzliNjM0MDU5NTBhMzQwOGZiOTMxZWFmNzBmMjdhNjE5ODUwIn0.eyJhdWQiOiIxNSIsImp0aSI6ImQ4MjY0ZTczNTcxZWQ3OWMyZGI0MDYwMTA5YjA1OTk4Y2Y1Y2IxYjk1MGJlMzliNjM0MDU5NTBhMzQwOGZiOTMxZWFmNzBmMjdhNjE5ODUwIiwiaWF0IjoxNTA4OTY5MTgxLCJuYmYiOjE1MDg5NjkxODEsImV4cCI6MTgyNDUwMTk4MSwic3ViIjoiOCIsInNjb3BlcyI6W119.VJYiTTWfwbZElgq2TqBX6_o1a3F7zqixmGG5ltgYPD91jQGqH1wMQAxsb824k04awMT5gIglpLXB64yb-0RVyb-qTQ7MpHT7B0ZJjzs4vC9A0pmKJ3b1-ckVGFnIoVrkKNomrI-M9BXyOgzLtA0wf44xjcpNpR3hntgk7xi-f-ZDqlCtd8uhRqXAOv3rghcrD-RwiI-c1J4PQpa9jsk5USvj530HAWObJzF2UsaOGKoumFPxoFMNBM55emjIC_P9hhTk_onSvSr_KF6rwYUW81Ot2le93MffaAqw69_sILvJFZ73TH8XWLc0vGy0RGCPoN8--pi949OfnrAyHnUCUf_DkMQFcfjgOO_CaB_LlPmdSQO-ko0Eu6Zgt4tKZFJNKfbApZIQZjfhFCEaQzCA5Qwxwx6ExqVeM5LgJwagDOtp4kC-vcfkt67UHiZ30bHCBfR1a-oOFXgJwMTsH3oBs6vbxE76H1GItc_Clx-Bk1ki0_OK41qeQuSu6cTNAiA2VfAwbFwbfv7F-Bnx6FnADiTOsCUIcHe382I7HSqMp2Nq9LEzd827Xtl7lIlvcWOmpaAQLNUQ2hl6melAxQAzB59fm9WehssNT0PHhx0Bq7UvbPNQF98MzKK_VViqLzh5GJ5KBZm7tc9CNyIEof547e4lufK_oguCM9-bcP1TMEU';
	$params = '';

	//setup the request, you can also use CURLOPT_URL
	$ch = curl_init($api_url.$params);
	// Returns the data/output as a string instead of raw data
	curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
	//Set your auth headers
	curl_setopt($ch, CURLOPT_HTTPHEADER, array(
	    'Content-Type: application/json',
	    'Authorization: Bearer ' . $api_token
	    )
	);
	// get stringified data/output. See CURLOPT_RETURNTRANSFER
	$data = curl_exec($ch);

	if (!curl_errno($ch)) {
		switch ($http_code = curl_getinfo($ch, CURLINFO_HTTP_CODE)) {
			case 200: 
				
				$response = json_decode($data);
	            foreach ($response[0] as $key => $resp) {	
					echo '<table class="tbserver" style="width: 49%;">';
					echo '	<thead>';
					echo '		<tr>';
					echo '			<th colspan="2" style="font-size: 12pt;">'.$resp->Host_Name.' ('.$key.')</th>';
					echo '		</tr>';
					echo '	</thead>';
					//---------------------------------------------------
					// Se consulta el status de la replicacion
					//---------------------------------------------------
					echo '	<tbody>';					
					if( isset($resp->General_Error) ){
						echo '	<tr>';
						echo '		<td colspan="2" style="color: red;"><b>'.$resp->General_Error.'</b></td>';
						echo '	</tr>';
					} else {

						if( !isset($resp->Channels) ){
							echo '	<tr>';
							echo '		<td colspan="2" style="color: red; text-align: center;"><b>NO HAY REPLICACIÓN !!!</b></td>';
							echo '	</tr>';
						} else {

							foreach ($resp->Channels as $channel) {
								
								$this_status = '';
								if($channel->Slave_IO_Running == "Yes" && $channel->Slave_SQL_Running == "Yes"){
									$this_status = '<span class="spnsucess">SUCESS</span>';
								}else{
									$this_status = '<span class="spnerror">ERROR !!!</span>';
								}

								$mins_lag = ($channel->Seconds_Behind_Master/60);
								if( $mins_lag > 30 ){
									$this_status .= '<span style="color: #DF3A01; font-size: 9pt; font-weight: bold;">ALERTA :: Hay un desfase de '.round($mins_lag, 2).' minutos</span>';
								}

								echo '	<tr>';
								echo '		<td class="tdchannel" style="max-width: 40%;">Channel : </td>';
								echo '		<td class="tdchannel" style="min-width: 60%;"><b>'.$channel->Channel_Name.'</b></td>';
								echo '	</tr>';
								echo '	<tr>';
								echo '		<td>Status : </td>';
								echo '		<td>'.$this_status.'</td>';
								echo '	</tr>';
								echo '	<tr>';
								echo '		<td>Seconds Behind Master : </td>';
								echo '		<td><b>'.$channel->Seconds_Behind_Master.'</b></td>';
								echo '	</tr>';
								echo '	<tr>';
								echo '		<td>Slave IO Running  : </td>';
								echo '		<td><b>'.$channel->Slave_IO_Running.'</b></td>';
								echo '	</tr>';
								echo '	<tr>';
								echo '		<td>Slave SQL Running : </td>';
								echo '		<td><b>'.$channel->Slave_SQL_Running.'</b></td>';
								echo '	</tr>';
								echo '		<td>Slave SQL Running State : </td>';
								echo '		<td><b>'.$channel->Slave_SQL_Running_State.'</b></td>';
								echo '	</tr>';
								if( !empty($channel->Last_SQL_Error) ){
									echo '	<tr>';
									echo '		<td>Last SQL Error : </td>';
									echo '		<td><div class="dverror">'.$channel->Last_SQL_Error.'</div></td>';
									echo '	</tr>';
								}
								if( !empty($channel->Last_SQL_Error) && $channel->Last_SQL_Error != $channel->Last_Error ){
									echo '	<tr>';
									echo '		<td>Last Error : </td>';
									echo '		<td><div class="dverror">'.$channel->Last_Error.'</div></td>';
									echo '	</tr>';
								}
								echo '	<tr><td colspan="2">&nbsp;</td></tr>';

							}					

							echo '		<tr>';
							echo '			<td class="tdlastrow">Último registro en<br/> '.$resp->Last_Insert_Database.'.'.$resp->Last_Insert_Table.' : </td>';
							echo '			<td class="tdlastrow"><b>'.$resp->Last_Insert_Row.'</b></td>';
							echo '		</tr>';
						}

					}

					echo '	</tbody>';
					//---------------------------------------------------
					echo '</table>';
				}

			break;
			default:
				echo 'Unexpected HTTP code: ', $http_code, "\n";
		}
	}
	// close curl resource to free up system resources 
	curl_close($ch);
	//====================================================================================================

?>

</body>
</html>