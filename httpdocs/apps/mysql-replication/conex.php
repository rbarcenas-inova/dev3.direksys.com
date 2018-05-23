<?php /*O3M*/
###Conexión Data###
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
				##First record in $Rows[1]...$Rows[n]
					for($x=0; $x<$TotCols; $x++){$Rows[$y][$x] = utf8_decode($Row[$x]);}
					$y++;
				}			
				if($Table){
				##Debug mode - Print HTML table with query results.
					$Result .= "<table class='tablaSQL' >";
					foreach($Rows as $Row){
						$label1 = (!$l)?"<th>":"<td>";
						$label2 = (!$l)?"</th>":"</td>";
						$Result .= "<tr>";
						foreach($Row as $Cell){$Result .= $label1.$Cell.$label2;}
						$Result .= "</tr>";
						$l++;
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
		$Cmd=array('STOP, SET, START');
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
function fechaHoy(){
$dia=date("l");
if ($dia=="Monday") $dia="Lunes";
if ($dia=="Tuesday") $dia="Martes";
if ($dia=="Wednesday") $dia="Miercoles";
if ($dia=="Thursday") $dia="Jueves";
if ($dia=="Friday") $dia="Viernes";
if ($dia=="Saturday") $dia="Sabado";
if ($dia=="Sunday") $dia="Domingo";
$dia2=date("d");
$mes=date("F");
if ($mes=="January") $mes="Enero";
if ($mes=="February") $mes="Febrero";
if ($mes=="March") $mes="Marzo";
if ($mes=="April") $mes="Abril";
if ($mes=="May") $mes="Mayo";
if ($mes=="June") $mes="Junio";
if ($mes=="July") $mes="Julio";
if ($mes=="August") $mes="Agosto";
if ($mes=="September")$mes="Septiembre";
if ($mes=="October") $mes="Octubre";
if ($mes=="November") $mes="Noviembre";
if ($mes=="December") $mes="Diciembre";
$ano=date("Y");
return "$dia $dia2 de $mes del $ano";
}
/*O3M*/
?>