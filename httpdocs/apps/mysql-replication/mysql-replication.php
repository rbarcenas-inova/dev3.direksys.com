<?php /*O3M*/
/**
* Description:	Verifica que un servidor MySQL configurado como esclavo este replicando
* 				correctamente, sino intenta restablecer la replicación y guarda un archivo
*				de logs con el error presentado.
* Fecha:		14-01-2014
* @author 		Oscar Maldonado
* @param		auth => 1 (Ejecuta query's), auth => other value (Modo debug, no file log .txt)
*				test => any value (ejecuta rutina, pero no query's, crea file log .txt)
*/
extract($_GET, EXTR_PREFIX_ALL, "v");
extract($_POST, EXTR_PREFIX_ALL, "v");
global $ipServerSlave;
$rows=SQLQuery('SHOW SLAVE STATUS');
$rowsResutls=$rows;
$titles=$rowsResutls[0];
unset($rowsResutls[0]);
$rowsResutls = array_combine($titles, $rowsResutls[1]);
date_default_timezone_set("America/Mexico_City");
$vNow=date('Ymd-His');
$ipServerSlave = "172.20.27.77";
$ipServerMaster = $rowsResutls['Master_Host'];
$lastInsert=SQLQuery("SELECT concat(LogDate,' ',LogTime) AS LogTime FROM admin_logs ORDER BY ID_admin_logs DESC LIMIT 1");
//$enviar_correo=SQLQuery("SELECT VValue FROM sl_vars WHERE VName='Replication_Slave_ON' LIMIT 1");
$scrTxt.= "<span style='color:blue;'>Fecha de ultimo registro insertado en direksys2_e2.admin_logs: </span>".$lastInsert[1][0]."<br>\r\n";
$scrTxt.= "<br>\r\n";
if($v_test){
	$ioRun='No';
	$sqlRun='No';
	$lastError='test'; 
	$lasSqlError='test';
	$fTest="_Test";
}else{
	$ioRun=$rowsResutls['Slave_IO_Running'];
	$sqlRun=$rowsResutls['Slave_SQL_Running'];
	$lastError=$rowsResutls['Last_Error'];
	$lasSqlError=$rowsResutls['Last_SQL_Error'];
	
	## Actualización de variabble Replication_Slave_ON en sl_vars
	$secondsBehind=$rowsResutls['Seconds_Behind_Master'];

	$cabeceras = 'From: direksys@inovaus.com' . "\r\n" .
    'Reply-To: direksys@inovaus.com' . "\r\n" .
    'X-Mailer: PHP/' . phpversion();

	if($sqlRun == "Yes" and $ioRun == "Yes"){
		#echo "<h1>REPLICACI&Oacute;N ACTIVA</h1><hr/>";
	}else{
		#echo "<h1>NO HAY REPLICACI&Oacute;N</h1><hr/>";
		mail('imiranda@inovaus.com,adiaz@inovaus.com,rbarcenas@inovaus.com', 'Replicación no activa', "NO HAY REPLICACIÓN ACTIVA\r\nMas información en http://mx.direksys.com/apps/mysql-replication", $cabeceras);
	}

	if((($secondsBehind/60)/60) > 1){
		mail('imiranda@inovaus.com,adiaz@inovaus.com,rbarcenas@inovaus.com', 'Desfase en replicación', "ALERTA :: Hay un desfase de más de una hora en la replicación\r\nMas información en http://mx.direksys.com/apps/mysql-replication", $cabeceras);
		#mail('imiranda@inovaus.com', 'Desfase en replicación', "ALERTA :: Hay un desfase de más de una hora en la replicación\r\nMas información en http://mx.direksys.com/apps/mysql-replication", $cabeceras);
	}

	#echo "<hr/><strong>Slave Status</strong><br/>";
	#echo "Seconds_Behind_Master : $secondsBehind<br/>Slave_IO_Running : $ioRun<br/>Slave_SQL_Running : $sqlRun<br/><hr/>";

	#$slvars=($secondsBehind>=1)?0:1;
	#$slvarsSql=SQLExec("UPDATE sl_vars SET VValue='$slvars' WHERE VName='Replication_Slave_ON' LIMIT 1;");
	##--
}

#echo $scrTxt;

###Functions###
function SQLLink(){
##Conexion to MySQL
	global $ipServerSlave;
	#$Server = $ipServerSlave;
	$Server = "172.20.27.77";
	$User = "root";
	$Password = "HjsLIwhglOPqw1278";
	$DataBase = "direksys2_e2"; 
	$DBIConex = array('Server'=>$Server,'User'=>$User,'Password'=>$Password,'DataBase'=>$DataBase);
	##
	$Link=mysql_connect($DBIConex['Server'], $DBIConex['User'], $DBIConex['Password']) or die(mysql_error());
	mysql_select_db($DBIConex['DataBase'],$Link);
	mysql_query("SET NAMES 'utf8'", $Link);
	return $Link;
}
function SQLQuery($Sql='',$Table=0){
##Excecute a SELECT query and return the results
	if(!empty($Sql)){
		$Cmd=array('SELECT', 'SHOW');
		$vSql=explode(' ',$Sql);
		if(in_array(strtoupper($vSql[0]),$Cmd)){
			$Link=SQLLink();
			$Con=mysql_query($Sql, $Link)or die(mysql_error());	
			$TotRows=mysql_num_rows($Con);
			$TotCols=mysql_num_fields($Con);
			if($TotRows){		
				$y=0;
				$rKeys=array_keys(mysql_fetch_array($Con));	
				foreach($rKeys as $rkey){	
				##Table Titles in $Rows[0]
					if($z){$Rows[$y][$x] = $rKeys[$x]; $z=0;}else{$z++;}	
					$x++;
				}
				$y++;
				mysql_data_seek($Con,0);
				while($Row=mysql_fetch_array($Con)){
				##First record in $Rows[1]
					for($x=0; $x<$TotCols; $x++){$Rows[$y][$x] = utf8_decode($Row[$x]);}
					$y++;
				}			
				if($Table){
				##Debug mode - Print HTML table with query results.
					$Result .= "<table class='tablaSQL' border='1'>";
					foreach($Rows as $Row){
						$label1 = (!$l)?"<th>":"<td>";
						$label2 = (!$l)?"</th>":"</td>";
						$Result .= "<tr>";
						foreach($Row as $Cell){$Result .= $label1.$Cell.$label2;}
						$Result .= "</tr>";
					}
					$Result .= "</table>";
				}else{$Result = $Rows;}
			}else{$Result = 0;}
			mysql_free_result($Con); 
			mysql_close($Link);
		}else{$Result = "Error: Wrong SQL instruction";}
	}else{$Result = "Error: Empty sel-query";}
	return $Result;
}
function SQLExec($Sql=''){
##Execute a query and return a message
	if(!empty($Sql)){
		$Cmd=array('STOP, SET, START, UPDATE, INSERT, DELETE');
		$vSql=explode(' ',$Sql);
		#if(in_array(strtoupper($vSql[0]),$Cmd)){
			$Link=SQLLink();
			$Con=mysql_query($Sql, $Link)or die(mysql_error());	
			$TotRows=mysql_affected_rows();
			#if($TotRows){$Result = $TotRows;}else{$Result = 0;}
			$Result = mysql_error();
			mysql_close($Link);
		#}else{$Result = false;}
	}else{$Result = false;}
	return $Result;
}
/*O3M*/
?>