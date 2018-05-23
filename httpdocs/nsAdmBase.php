<?php
	/* ********************************************************************** */
	/* ** nsBase                                                           ** */
	/* **                                                        03/31/04  ** */
	/* ********************************************************************** */

	######################################################
	####	Check if language is Present ####################
	######################################################


	#########################################################
	#### INIT System Data
	#########################################################
	$in  = array();
	$va  = array();
	$trs = array();
	$usr = array();
	$sys = array();
	$cfg = array();
	$conn = null;
	######################################################
	##### Configuration File ############################
	######################################################
	$dir = getcwd();
	list($b_cgibin,$a_cgibin) = strpos( $dir, 'httpdocs' ) !== false ?
		explode('httpdocs',$dir) :
		explode('cgi-bin/',$dir);
	$cfg_folder = $b_cgibin.'cgi-bin/common/';

	######################################################
	##### Load Paths and URLs ############################
	######################################################
	load_sys_data(); //Load $sys

	if (isset($_COOKIE['sit_lang'])){
		$usr['pref_language'] = $_COOKIE['sit_lang'];
	}
	$lang              = $usr['pref_language'];
	(!$lang) and ($lang = $cfg['default_lang']);

	$path_templates    = $cfg['path_templates'];
	$path_templates    = preg_replace("/\[lang\]/",$lang,$path_templates);

	$path_sessions     = $cfg['auth_dir'];


	$ck_name           = "slsid";
	$in['systememail'] = "webmaster@nowsee.com";
	$in['debug_mode']  = 1;

	$va['imgurl']       = $cfg['path_ns_img'];
	$va['app_title']    = $cfg['app_title'];
	$va['mootools_url'] = $cfg['mootools_url'];
	$va['yui_url']      = $cfg['yui_url'];
	$va['show_err_dsession'] = "none;";
	
	#require_once('DB.php'); //PEAR must be installed
	#$datasource = 'mysql://'.$cfg[dbi_user].':'.$cfg[dbi_pw].'@'.$cfg[dbi_host].'/'.$cfg[dbi_db];
	##### Load Data to $in ##############
	#####################################
     $in['thisurl'] = '';
	foreach ($_GET as $key=>$value ) {
		if (substr(strtolower($key), 0,4)=="chk:"){
			list ($aux,$name) = explode(":",$key);
			$name = str_replace("_"," ",$name);
			if (array_key_exists(strtolower($value), $in)){
				$in[strtolower($value)] .= "|$name";
			}else{
				$in[strtolower($value)] .= "$name";
			}
		}else{
			$in[strtolower($key)] = $value;
		}
		if (strtolower($key) != 'help'){
			$in['thisurl'] .= strtolower($key)."=$value&";
		}
	}
	foreach ($_POST as $key=>$value ) {
		if (substr(strtolower($key), 0,4)=="chk:"){
			list ($aux,$name) = explode(":",$key);
			$name = str_replace("_"," ",$name);
			if (array_key_exists(strtolower($value), $in)){
				$in[strtolower($value)] .= "|$name";
			}else{
				$in[strtolower($value)] .= "$name";
			}
		}else{
			$in[strtolower($key)] = $value;
		}
		if (strtolower($key) != 'help'){
			$in['thisurl'] .= strtolower($key)."=$value&";
		}
	}
	(!$in['nh']) and ($in['nh']=1);
	(!isset($in['e']) or intval($in['e']) <= 0) and ($in['e']=$cfg['def_e']);
	$in['e'] = intval($in['e']);
	
	
	######################################################
	### Load Sysytem con figuration
	###############################################
	#// Connect Persistent to DB
	if ($cfg['oper_mode'] != 'updating' or $cfg['oper_mode'] == 'closed'){	
		#(strlen($in['e'])>1) and ($in['e'] = substr($in['e'], -1));
		if ($in['e'] or $_COOKIE['e']){
			if ($in['e']){
				$_COOKIE['e'] = $in['e'];
				setcookie('e', $in['e']);
			}else{
				$in['e'] = $_COOKIE['e'];
			}
			// echo "DB=".$cfg['emp.'.$in['e'].'.dbi_db']." Host ".$cfg['emp.'.$in['e'].'.dbi_host']."<br>";
			$conn = mysqli_connect ($cfg['emp.'.$in['e'].'.dbi_host'], $cfg['emp.'.$in['e'].'.dbi_user'], $cfg['emp.'.$in['e'].'.dbi_pw'], $cfg['emp.'.$in['e'].'.dbi_db']) or die();
			$va['eimg'] = '.e'.$in['e'];
		}else{
			$conn = mysqli_connect ($cfg['dbi_host'], $cfg['dbi_user'], $cfg['dbi_pw'], $cfg['dbi_db']) or die(mysqli_error($conn));
			
		}
	}

	############################################################################
	##### Functions                                                        #####
	############################################################################

	function filter_values($input){
		$output = preg_replace("/\'/", "\\'/", $input);
		return $output;
	}

	// -------------------------------------------------------------------------
	function format_price($num) {
		return ("$ " . number_format($num,2)) ;
	}

	// -------------------------------------------------------------------------
	function date_to_sql($in_date) {
		global $usr;
		#$months = array ("jan" => array(1,31), "feb" => array(2,28), "mar" => array(3,31), "apr" => array(4,30), "may" => array(5,31), "jun" => array(6,30),
	     #              	"jul" => array(7,31), "aug" => array(8,31), "sep" => array(9,30), "oct" => array(10,31), "nov" => array(11,30), "dec" => array(12,31),
		#		  		"ene" => array(1,31), "abr" => array(4,30), "ago" => array(8,31), "dic" => array(12,31));
		#$months = array ("ene" => 1, "feb" => 2, "mar" => 3, "abr" => 4, "may" => 5, "jun" => 6,"jul" => 7, "ago" => 8, "sep" => 9, "oct" => 10, "nov" => 11, "dic" =>12);
		#$dmonths = array ("ene" => 31, "feb" => 28, "mar" => 31, "abr" => 30, "may" =>31, "jun" => 30,"jul" => 31, "ago" => 30, "sep" =>30, "oct" =>31, "nov" =>30, "dic" =>31);
		if ($usr['pref_language']=='en'){
			$months = array ("jan" => 1, "feb" => 2, "mar" => 3, "apr" => 4, "may" => 5, "jun" => 6,"jul" => 7, "aug" => 8, "sep" => 9, "oct" => 10, "nov" => 11, "dec" =>12);
			$dmonths = array ("jan" => 31, "feb" => 28, "mar" => 31, "apr" => 30, "may" =>31, "jun" => 30,"jul" => 31, "aug" => 30, "sep" =>30, "oct" =>31, "nov" =>30, "dec" =>31);
		}else{
			$months = array ("ene" => 1, "feb" => 2, "mar" => 3, "abr" => 4, "may" => 5, "jun" => 6,"jul" => 7, "ago" => 8, "sep" => 9, "oct" => 10, "nov" => 11, "dic" =>12);
			$dmonths = array ("ene" => 31, "feb" => 28, "mar" => 31, "abr" => 30, "may" =>31, "jun" => 30,"jul" => 31, "ago" => 30, "sep" =>30, "oct" =>31, "nov" =>30, "dic" =>31);
		}

		$ar= preg_split("/-|\/|:/", $in_date);
		$day = intval($ar[0]);
		$mon = strtolower($ar[1]);
		$year = intval($ar[2]);

		($year < 100) and ($year += 2000);
		$yy1 = $year/4;
		$yy2 = intval($year/4);
		$mon = strtolower($mon);

		// ### Años Viciestos
		if ($yy1 == $yy2){
			++$months['feb'];
		}
		// ######## Month ####
		if (!$months[$mon]){
			return 0;
		}
		// ######## Day ####
		if ($day>$dmonths[$mon]){
			return 0;
		}
		return ("$year-$months[$mon]-$day");
	}

	// -------------------------------------------------------------------------
	function  sql_to_date($date) {
		global $usr;
		if ($usr['pref_language']=='en'){
			$months  = array('Nul','Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec');
		}else{
			$months  = array('Nul','Ene','Feb','Mar','Abr','May','Jun','Jul','Ago','Sep','Oct','Nov','Dic');
		}

		list($year,$mon,$day) = explode('[/.-]', $date);
		if ($day<10){
			$day = "0". intval($day);
		}
		$mon = intval($mon);
		if ($date){
			return "$day-$months[$mon]-$year";
		}else{
			return "";
		}
	}

	// -------------------------------------------------------------------------
	function save_auth_data($sid,$sdata) {
		global $conn;
		global $path_sessions, $cfg, $va;
		$output = '';
		foreach ($sdata as $key=>$value ) {
			if ($key != "password" and $key){
				$value = preg_replace("/\r/", "", $value);
				$value = preg_replace("/\n/", "``", $value);
				$output .= "$key=$value\n";
			}
		}		
		
		if ($cfg['gensessiontype'] == 'mysql'){
		#@ivanmiranda :: Soporte para colisión de sesiones
			$_sesiones = mysqli_query($conn, "SELECT * FROM admin_sessions WHERE createdBy=$sdata[id_admin_users] AND TIMESTAMPDIFF(SECOND,ExpDateTime,NOW()) <= 21600 AND ip != '".get_ip()."';");
			if($_activa = mysqli_fetch_assoc($_sesiones)) {
				#$_apagar = mysql_query("SELECT * FROM admin_sessions WHERE createdBy=$sdata[id_admin_users] AND TIMESTAMPDIFF(SECOND,ExpDateTime,NOW()) <= 21600 AND ip != '".get_ip()."';");
				#while ($_sesion = mysql_fetch_assoc($_apagar)) {
					#echo "INSERT INTO admin_logs SET LogDate=CURDATE(),LogTime=CURTIME(), ID_admin_users='$sdata[id_admin_users]', Type='Access', Message='SECURITY', Action='Cierre de sesiones duplicadas para el usuario ".$_sesion['ses']."', IP='".get_ip()."';";
					#mysql_query("INSERT INTO admin_logs SET LogDate=CURDATE(),LogTime=CURTIME(), ID_admin_users='$sdata[id_admin_users]', Type='Access', Message='SECURITY', Action='Cierre de sesiones duplicadas para el usuario ".$_sesion['ses']."', IP='".get_ip()."';");
				#}
				#die();
				mysqli_query($conn, "INSERT INTO admin_logs SET LogDate=CURDATE(),LogTime=CURTIME(), ID_admin_users='$sdata[id_admin_users]', Type='Access', Message='SECURITY', Action='Cierre de sesiones duplicadas para el usuario', IP='".get_ip()."';");
				mysqli_query($conn, "DELETE FROM admin_sessions WHERE createdBy=$sdata[id_admin_users];");
				// $page = build_page("login.html");
				// $_mensaje = '<body onLoad="document.sitform.username.focus()">
				// <div class="repetida">
				// <img src="sitimages/srepetida.png" align=left style="margin-right:15px; position:relative; top:-4px;">
				// 	<font size=4px>Sesion repetida</font><br>
				// 	Hay otra cuenta con los mismos datos, por seguridad las dos sesiones han sido cerradas
				// </div>';
				// $page = str_replace('<body onLoad="document.sitform.username.focus()">', $_mensaje, $page);
				// echo $page;
			} else {
				$sth = mysqli_query($conn, "INSERT INTO admin_sessions SET ses='$sid', Content='".filter_values($output)."', CreatedBy=$sdata[id_admin_users], CreatedDateTime=NOW(),ExpDateTime=NOW(),ip='".get_ip()."';");
			}
		}else{
			if ($handle = fopen($path_sessions.$sid,'w')){
				fwrite($handle,"$output\n");
				fclose($handle);
			}
		}
	}

	// -------------------------------------------------------------------------
	function load_usr_data($sid) {
		global $usr,$cfg,$path_sessions;
		if ($cfg['gensessiontype'] == 'mysql'){
			#print "<pre>";
			##print  load_name('admin_sessions','ses',$sid,'Content');
			
			$ary = preg_split("/\n/", load_name('admin_sessions','ses',$sid,'Content'));
			for ($x = 0; $x<sizeof($ary); $x++) {
				if (preg_match("/([^=]+)=(.*)/",$ary[$x],$matches)){
					$usr[strtolower($matches[1])] = $matches[2];
				}
			}
			(!$usr['pref_style']) and ($usr['pref_style']='default');
			(!$usr['pref_lang'])  and ($usr['pref_lang'] ='en');
			if($usr['id_admin_users']>0){
				return 'ok';
			}else{
				return 'Please Login';
			}
		}else{
			if (file_exists($path_sessions.$sid)) {
				if ($handle = fopen($path_sessions.$sid,'r')){
					while (!feof($handle)) {
						list($name,$value) = explode('=',fgets($handle),2);
						$usr[strtolower($name)]=trim($value);
					}
					(!$usr['pref_style']) and ($usr['pref_style']='default');
					(!$usr['pref_lang'])  and ($usr['pref_lang'] ='en');
					return 'ok';
				}else{
					return 'Please Login';
				}
			}else{
				return 'Please Login';
			}
		}
	}

	// -------------------------------------------------------------------------
	function logout($sid) {
		global $ck_name, $path_sessions;
		setcookie($ck_name, '');
		setcookie('sessionid', '');
		setcookie('kp3', '');
		setcookie('gwa', '');
		if (file_exists($path_sessions.$sid)) {
			unlink($path_sessions.$sid);
		}
	}

	// -------------------------------------------------------------------------
	function load_page($fname) {
		global $usr,$cfg;
		$tmpname = $fname;
		(!$usr['pref_language']) and ($usr['pref_language']=$cfg['default_lang']);
		if (preg_match("/(.*)\/([a-z]*)_(.*)$/",$fname,$matches) and $cfg['path_ns_cgi_'.$matches[2]]){
			$tmpname = $matches[1]."/".$matches[2]."/".$matches[3];
		}
		$tmpname = preg_replace("/\[lang\]/", $usr['pref_language'], $tmpname);
		if (file_exists("$tmpname")) {
			if ($handle = fopen("$tmpname",'r')){
				while (!feof($handle)) {
					$page .= fgets($handle);
				}
				return $page;
			}else{
				return '';
			}
		}else{
			
			$tmpname = $fname;
			$str = $usr['pref_language'].'/common';
			$tmpname = preg_replace("/\[lang\]/", $str , $tmpname);
			if (file_exists("$tmpname")) {
				if ($handle = fopen("$tmpname",'r')){
					while (!feof($handle)) {
						$page .= fgets($handle);
					}
					return $page;
				}else{
					return '';
				}
			}else{
				return '';
			}
		}
	}

	// -------------------------------------------------------------------------
	function build_page($tname) {
		global $path_templates, $in, $usr, $va, $error,$cfg;
		$page = load_page($cfg['path_templates'] . $tname);
		while (preg_match("/\[([^]]+)\]/", $page, $matches) and $num<99){
			$field    = $matches[1];
			$cmdname  = strtolower(substr($field,3));
			$cmdtype  = substr($field,0,3);
			if ($cmdtype == 'ck_'){
				$rep_str = $_COOKIE[$cmdname];
			}elseif($cmdtype == 'in_'){
				$rep_str = $in[$cmdname];
			}elseif($cmdtype == 'va_'){
				$rep_str = $va[$cmdname];
			}elseif($cmdtype == 'er_'){
				$rep_str = $error[$cmdname];
			}elseif($cmdtype == 'ur_'){
				$rep_str = $usr[$cmdname];
			}elseif($cmdtype == 'ip_'){
				$rep_str = build_page($cmdname.'.html');
			}elseif($cmdtype == 'fc_'){
				if (function_exists($cmdname)){
					$rep_str = $cmdname();
				}else{
					$rep_str = '';
				}
			}else{
				$rep_str ='';
			}
			$page = preg_replace("#\[$field\]#i",$rep_str,$page);
			++$num;
		}
		return $page;
	}

	// -------------------------------------------------------------------------
	function pages_list($this_page, $numhits, $maxhits) {
		global $in;

		if ($numhits == 0){
			return array('1','');
		}else{
			###########################################
			###### Built Pages Link
			###########################################
			if (!array_key_exists("nh", $in)){
				$in['nh'] = 1;
			}

			if ($numhits <= $maxhits) {
				return '1';
			}

			if ($numhits > $maxhits) {
				$next_hit = $in['nh'] + 1;
				$prev_hit = $in['nh'] - 1;

				$left  = $in['nh'];
				$right = intval($numhits/$maxhits) - $in['nh'];
				($left > 7)  ? ($lower = $left - 7) : ($lower = 1);
				($right > 7) ? ($upper = $in['nh'] + 7)   : ($upper = intval($numhits/$maxhits) + 1);
				if (7 - $in['nh'] >= 0) {
					$upper = $upper + (8 - $in['nh']);
				}
				if ($in['nh'] > ($numhits/$maxhits - 7)) {
					$lower = $lower - ($in['nh'] - intval($numhits/$maxhits - 7) - 1);
				}
				$output = "";

				if ($in['nh'] > 1) {
					$output .= "<a href='$this_page&nh=$prev_hit'> <<< </a> ";
				}
				for ($i = 1; $i <= intval($numhits/$maxhits) + 1; $i++) {
					if ($i < $lower) {
						$output .= " ... ";
						$i = ($lower-1);
					}else{
						($i == $in['nh']) ?
							($output .= "<b>$i</b> ") :
							($output .= "<a href='$this_page&nh=$i'>$i</a> ");
						if (($i * $maxhits) >= $numhits) {
							break;
						}
					}
					if ($i > $upper) {
						$output .= " ... ";
						break;
					}
				}
				if ($in['nh'] <= intval($numhits/$maxhits)){
					$output .= "<a href='$this_page&nh=$next_hit'> >>> </a> ";
				}
			}else{
				$output  = "1";
			}
			return $output;
		}
	}

	// -------------------------------------------------------------------------
	function load_cfg($tbl_name){
		global $conn;
		global $db_cols, $db_valid_types, $db_not_null;
		$sth = mysqli_query("show tables like '$tbl_name';");
		$ary = mysqli_fetch_array($sth);
		if (!$ary[0]){
			return;
		}
		$db_cols = array();
		$sth = mysqli_query("describe $tbl_name;");
		while ($ary = mysqli_fetch_array($sth)) {
			#print_r($ary);
			$db_cols[] = $ary[0];
			if ($ary[5] == "auto_increment"){
				$db_valid_types[$ary[0]] = "auto_increment";
				$ary[2] = "YES";
			}elseif (preg_match("/varchar/i", $ary[1])){
				if ($ary[4] == "email"){
					$db_valid_types[$ary[0]] = "email";
				}else{
					$db_valid_types[$ary[0]] = "alpha";
				}
			}elseif ($ary[1] == "date"){
				$db_valid_types[$ary[0]] = "date";
			}elseif (preg_match("/^int/", $ary[1]) || $ary[1] == "decimal(5,3)"){
				$db_valid_types[$ary[0]] = "numeric";
			}elseif (preg_match("/^dec/", $ary[1])){
				$db_valid_types[$ary[0]] = "currency";
			}else{
				$db_valid_types[$ary[0]] = "alpha";
			}
			if (!$ary[2] or $ary[2] == 'NO'){
				$db_not_null[$ary[0]] = 1;
			}
		}
		return;
	}

	// -------------------------------------------------------------------------
	function validate_cols($db_cols) {
		global $in,$error;
		$error['return-query'] = '';
		
		foreach ($db_cols as $col=>$value ) {
			$lc_col = strtolower($col);
			$val = $in[$lc_col];
			##### Not Null Check #####
			if (!$val and $value[1]) {
				$error[$lc_col] = trans_txt("required");
				++$err;
				#echo "$col<br>";
			##### Valid E-Mail Check #####
			}elseif ($value[0] == "email" and ($val and !check_email_address($val))){
				$error[$lc_col] = trans_txt("invalid");
				++$err;
				#echo "$col<br>";
			##### Valid numeric field Check #####
			}elseif ($value[0] == "numeric" and !is_numeric($val)){
				$error[$lc_col] = trans_txt("invalid");
				++$err;
				#echo "$col<br>";
			##### Valid Date field Check #####
			#}elsif ($db_valid_types[$col] eq "date" and $val !~ /^\s*$/){
			#	if (&date_to_sql($in[$col]) == 0){
			#		$error[$col] = "<span class='error'>Inv lido</span>";
			#		++$err;
			#	}
			}
			$error['return-query'] .= "$col='".filter_values($val)."',";
			#echo("$col :  $db_valid_types[$col]  : Req=$db_not_null[$col] : $err : $error[$col] : val=$val : isnull=".is_null($val)."<br>");
		}
		$error['return-query'] = substr($error['return-query'],0,-1);
		if ($err>0){
			$error['return-status'] = 'error';
		}else{
			$error['return-status'] = 'ok';
		}
		return $error;
	}

	// -------------------------------------------------------------------------
	function save_page($fname,$data) {
		if ($handle = fopen($fname,'w')){
			fwrite($handle,"$data");
			fclose($handle);
		}
	}

	// -------------------------------------------------------------------------
	function sid_dv($input) {
		$input .= get_ip;
		$lg = strlen($input);
		for ($i = 1; $i <= $lg; $i++) {
			$tot +=  ord(substr($input,$i,1)) + ord(substr($input,$i+1,1)) - 30 - $i;
		}
		$dv = intval(($tot/11-intval($tot/11))*11);
		if ($dv==10){
			$dv='K';
		}
		return $dv;
	}

	// -------------------------------------------------------------------------
	function get_ip (){
		## AD::Se agrega validacion para suprimir el error generado por el Servidor de Balanceo
		$headers = getallheaders();

		if (isset($headers['X-Real-IP']) and $headers['X-Real-IP'] !=''){
			return $headers['X-Real-IP'];
		}elseif (getenv('REMOTE_ADDR')){
			return getenv('REMOTE_ADDR');
		}elseif (getenv('REMOTE_HOST')){
			return getenv('REMOTE_HOST');
		}elseif (getenv('HTTP_CLIENT_IP')){
			return getenv('HTTP_CLIENT_IP');
		}else{
			return "Unknown";
		}
	}
	function checkip ($ipfilter){
		global $conn;
		$ip = get_ip();
		#echo "$ipfilter <br>.. $ip<br><br>";
		$ip1 = preg_split("/\./",$ip,4);
		$ips = preg_split("/,|\n/",$ipfilter);
		
		#echo "<br>size".sizeof($ips);
		for ($x = 0; $x<sizeof($ips); $x++) {
			$ips[$x] = preg_replace("/\r/", "", $ips[$x]);
			$ip2 = preg_split("/\./",$ips[$x],4);
			$ok = 1;
			#echo "<br>cheking: $ips[$x]=?$ip : $x<br>";
			for ($i = 0; $i <= 3; $i++) {
				#echo "&nbsp;&nbsp;&nbsp;&nbsp; $ip1[$i] != $ip2[$i]";
				if ($ip1[$i] != $ip2[$i] and $ip2[$i] != 'x'){
					$ok = 0;
					#echo " : ERR";
				}
				#echo "<br>";
				
			}
			if ($ok){
				#echo "IP OKM<br>"; 
				$sth = mysqli_query($conn, "SELECT COUNT(*) FROM admin_IPlist WHERE Type='Black' AND IP='$ip'");
				$ary = mysqli_fetch_array($sth);
				if ($ary[0]>0){
					return 0;
				}else{
					return 1;	
				}
			}
		}
		return 0;
	}

#############################################################################
#############################################################################
#	Function: valip
#
#	Created on: 01/10/2015 17:42
#
#	Author: Jonathan Alcantara
#
#	Modifications:
#
#	Parameters:
#
#	Returns: Bandera de ip trusted
#
#	See Also:
#
function valip($validate_origin, $ID_admin_users = 0) {
	global $conn;
	#OBTENEMOS LA IP A VALIDAR
	$log = "";
	$my_ip = get_ip();
	$log .= "<br>my_ip=".$my_ip;
	$ok = 0;
	$log .= "<br>ok=".$ok;
	$log .= "<br>validate_origin=".$validate_origin;
	#VALIDAMOS IP'S DEPENDIENDO DEL ORIGEN DE LA VALIDACION
	if ($validate_origin == 'sl_ipmanager') {
		$qry2 = "SELECT IP AS ip_trusted FROM sl_ipmanager WHERE Type='Trusted' AND IP NOT LIKE '%x%' AND Status = 'Active';";
		$res2 = mysqli_query($conn, $qry2) or die("Query failed: ".mysqli_error($conn));
		#RECORREMOS LAS IPS TRUSTED SIN X Y VALIDAMOS
		while ($rec2 = mysqli_fetch_assoc($res2)) {
			$log .= "<br>VALIDATING WITHOUT X ip_trusted=".$rec2['ip_trusted'];
			#SI LA IP SE ENCUENTRA REGISTRADA PASA Y SE LOGEA NORMALMENTE
			if ($rec2['ip_trusted'] == $my_ip) {
				$log .= "<br>".$rec2['ip_trusted']."=".$my_ip;
				$ok = 1;
				$log .= "<br>ok=".$ok;
				break;
			}
		}
		if ( ! $ok) {
			$log .= "<br>ok=".$ok;
			#SI NO SE ENCONTRO LA IP VALIDAMOS LAS IP'S TRUSTED CON X
			$qry3 = "SELECT IP AS ip_trusted FROM sl_ipmanager WHERE Type='Trusted' AND IP LIKE '%x%' AND Status = 'Active';";
			$res3 = mysqli_query($conn, $qry3) or die("Query failed: ".mysqli_error($conn));
			#RECORREMOS LAS IPS TRUSTED CON X Y VALIDAMOS
			while ($rec3 = mysqli_fetch_assoc($res3)) {
				$log .= "<br>VALIDATING WITH X ip_trusted=".$rec3['ip_trusted'];
				$log .= "<br>valip_wildcard()";
				$ok = valip_wildcard($my_ip, $rec3['ip_trusted']);
				$log .= "<br>ok=".$ok;
				if ($ok) {
					break;
				}
			}
		}
	} elseif ($validate_origin == 'admin_users' and $ID_admin_users > 0) {
		$qry3 = "SELECT IPFilter FROM admin_users WHERE ID_admin_users=".$ID_admin_users.";";
		$res3 = mysqli_query($conn, $qry3) or die("Query failed: ".mysqli_error($conn));
		$row3 = mysqli_fetch_assoc($res3);
		$ips_trusted = explode("\n", $row3['IPFilter']);
		$log .= "<br>ips_trusted=".print_r($ips_trusted, true);
		
		foreach ($ips_trusted as $key => $ip_trusted) {
			$log .= "<br>VALIDATING WITHOUT X ip_trusted=".$ip_trusted;
			$ip_trusted = trim($ip_trusted);
			#SI LA IP SE ENCUENTRA REGISTRADA PASA Y SE LOGEA NORMALMENTE
			$find_x   = 'x';
			$find_X   = 'X';
			$find_1 = strpos($ip_trusted, $find_x);
			$find_2 = strpos($ip_trusted, $find_X);
			$log .= "<br>find_1=".$find_1;
			$log .= "<br>find_2=".$find_2;

			#VALIDAMOS IP's TRUSTED SIN X PRIMERO
			if ($find_1 === false and $find_2 === false) {
				$log .= "<br>FALSE===FALSE";
				$log .= "<br>ip_trusted==my_ip".$ip_trusted.'=='.$my_ip;
				if ($ip_trusted == $my_ip) {
					$log .= "<br>".$ip_trusted."=".$my_ip;
					$ok = 1;
					$log .= "<br>ok=".$ok;
					break;
				}
			}
		}
		if ( ! $ok) {
			#VALIDAMOS IP's TRUSTED CON X
			foreach ($ips_trusted as $key => $ip_trusted) {
				$log .= "<br>VALIDATING WITH X ip_trusted=".$ip_trusted;
				$ip_trusted = trim($ip_trusted);
				#SI LA IP SE ENCUENTRA REGISTRADA PASA Y SE LOGEA NORMALMENTE
				$find_x   = 'x';
				$find_X   = 'X';
				$find_1 = strpos($ip_trusted, $find_x);
				$find_2 = strpos($ip_trusted, $find_X);

				if ($find_1 !== false or $find_2 !== false) {
					$log .= "<br>valip_wildcard()";
					$ok = valip_wildcard($my_ip, $ip_trusted);
					$log .= "<br>ok=".$ok;
					if ($ok) {
						break;
					}
				}
			}
		}
	} else {
		$log .= "<br>no origin";
		#echo $log; exit;
		return $ok;
	}
	#SI TENEMOS BANDERA OK ENCENDIDA QUIERE DECIR QUE ES UNA IP TRUSTED Y SE LOGEA NORMALEMNTE
	#DE LO CONTRARIO SE PROCEDE AL LOGEO EN 2 PASOS
	#echo $log; exit;
	return $ok;
}

#############################################################################
#############################################################################
#	Function: valip_wildcard
#
#	Created on: 21/06/2017 17:28
#
#	Author: Jonathan Alcantara
#
#	Modifications:
#
#	Parameters:
#
#	Returns: Bandera de ip trusted por comodin
#
#	See Also:
#
function valip_wildcard($my_ip, $ip_trusted) {
	$ok = 0;
	#EXPLOTAMOS LA IP A VALIDAR
	$my_ip_arr = explode('.', $my_ip);
	#REMOVEMOS LAS X DE IP TRUSTED
	$ip_trusted = str_replace('.x', '', $ip_trusted);
	$ip_trusted = str_replace('.X', '', $ip_trusted);
	#EXPLOTAMOS LA IP TRUSTED
	$ip_trusted_arr = explode('.', $ip_trusted);
	#INICIALIZAMOS LA BANDERA DE PRE VALIDACION
	$pre_ok = 1;
	for ($i = 0; $i<count($ip_trusted_arr); $i++) {
		#SI LA BANDERA DE PRE VALIDACION SIGUE EN 1 Y LOS VALORES POR INDICE IGUAL DE AMBAS IPS COINCIDE CONSERVAMOS LA BANDERA EN 1
		if ($pre_ok == 1 and $my_ip_arr[$i] == $ip_trusted_arr[$i]) {
			$pre_ok = 1;
		} else {
			#SI EN ALGUN MOMENTO LOS VALORES POR INDICE NO COINCIDEN, LA BANDERA DE PREVALIDACION PASA A 0 Y DEJA DE VALIDARSE ESTA IP
			$pre_ok = 0;
		}
		#SI AL FINAL DEL RECORRIDO DE LOS INDICES DE LA ACTUAL IP TRUSTED SIGUE EN 1 LA BANDERA DE PREVALIDACION
		#QUIERE DECIR QUE ES UNA IP TRUSTED Y ENCENDEMOS BANDERA OK
		#EL SIGUIENTE RECORRIDO NO LE AFECTA YA QUE NO APAGAMOS LA BANDERA
		if ($i == (count($ip_trusted_arr)-1) and $pre_ok == 1) {
			$ok = 1;
		}
	}
	return $ok;
}





	// -------------------------------------------------------------------------
	function save_logs($message,$action){
		global $usr,$in, $conn;
		if ($message == 'login' or $message == 'logout'){
			$type = 'Access';
		}else{
			$type = 'Action';
		}
		$sth = mysqli_query($conn, "INSERT INTO admin_logs SET LogDate=NOW(),LogTime=NOW(),Logcmd='$in[cmd]',Type='$type',Message='$message',Action='".filter_values($action)."',ID_admin_users='$usr[id_admin_users]',IP='".get_ip()."'");
	}


	// -------------------------------------------------------------------------
	#function save_voxchgs($action){
	#	global $usr,$db;
	#	$result = $db->query("INSERT INTO vxd_changes SET Date=NOW(),Time=NOW(),Action='".filter_values($action)."',ID_admin_users='$usr[id_admin_users]'");
	#	#echo "INSERT INTO vox_changes SET Date=NOW(),Time=NOW(),Action='".filter_values($action)."',ID_admin_users='$usr[id_admin_users]'";
	#}

	// -------------------------------------------------------------------------
	function nsmail($from,$to,$subject,$body,$html){
		$headers = "From: $from <$from>\n";
		$headers .= "MIME-Version: 1.0\CRLF\n";
		##; charset=iso-8859-9
		if ($html){
			$headers .= "Content-type: text/html\n";
		}
		$headers .= "Reply-To: Comerciototal <$from>\n";
		$headers .= "X-Priority: 1\n";
		$headers .= "X-MSmail-Priority: Low\n";
		#$headers .= "Content-type: text/html\n";
		$headers .= "X-mailer: Comerciototal";

		mail(" $to <$to>", $subject,$body,$headers);
	}

	// -------------------------------------------------------------------------
	function check_email_address($email,$dns) {
		// First, we check that there's one @ symbol, and that the lengths are right
		if(!$email){
			return false;
		}
		if (!ereg("[^@]{1,64}@[^@]{1,255}", $email)) {
			// Email invalid because wrong number of characters in one section, or wrong number of @ symbols.
			return false;
		}
		// explode it into sections to make life easier
		$email_array = explode("@", $email);
		$local_array = explode(".", $email_array[0]);
		for ($i = 0; $i < sizeof($local_array); $i++) {
			if (!ereg("^(([A-Za-z0-9!#$%&'*+/=?^_`{|}~-][A-Za-z0-9!#$%&'*+/=?^_`{|}~\.-]{0,63})|(\"[^(\\|\")]{0,62}\"))$", $local_array[$i])) {
				return false;
			}
		}
		if (!ereg("^\[?[0-9\.]+\]?$", $email_array[1])) { // Check if domain is IP. If not, it should be valid domain name
			$domain_array = explode(".", $email_array[1]);
			if (sizeof($domain_array) < 2) {
		   		return false; // Not enough parts to domain
			}
			for ($i = 0; $i < sizeof($domain_array); $i++) {
				if (!ereg("^(([A-Za-z0-9][A-Za-z0-9-]{0,61}[A-Za-z0-9])|([A-Za-z0-9]+))$", $domain_array[$i])) {
					return false;
				}
			}
		}
		if ($dns){
			$dom = explode('@', $email);
			if(checkdnsrr($dom[1].'.', 'MX') ) return true;
			if(checkdnsrr($dom[1].'.', 'A') ) return true;
			if(checkdnsrr($dom[1].'.', 'CNAME') ) return true;
			return false;
		}
		return true;
	}

	// -------------------------------------------------------------------------
	function build_radio ($tbl,$field){
		global $db;
		$result = $db->query("DESCRIBE $tbl $field;");
		$output = '';
		if (!DB::isError($result)) {
			$rec = $result->fetchRow(DB_FETCHMODE_ASSOC);
			$list = preg_split("/','/", substr($rec[1],6,-2));
			for ($i = 0; $i < sizeof($list); $i++) {
				$output .= "<input type='radio' name='$field' value='$list[$i]' class='checkbox'>$list[$i]\n";
			}
		}
		return $output;
	}

	// -------------------------------------------------------------------------
	#function load_name($tbl,$where,$resp){
	#	global $db;
	#	$result = $db->query("SELECT * FROM $tbl WHERE $where;");
	#	if (!DB::isError($result)) {
	#		$rec = $result->fetchRow(DB_FETCHMODE_ASSOC);
	#		foreach ($rec as $key=>$value ) {
	#			$resp = preg_replace("/\[$key\]/", $value, $resp);
	#		}
	#		return $resp;
	#	}else{
	#		return '';
	#	}
	#}

	// -------------------------------------------------------------------------
	function load_sys_data() {
		global $sys,$cfg,$cfg_folder;
		
	#	echo $cfg_folder."/general.ex.cfg";
		if (file_exists($cfg_folder."/general.ex.cfg")){
			if ($handle = fopen($cfg_folder."/general.ex.cfg",'r')){
				#echo "file OK<br>";
				while (!feof($handle)) {
					@list($type,$name,$value) = preg_split("/\||=/", fgets($handle),3);
					if ($type=='sys'){
						$sys[$name]=trim($value);
						#echo "$name = $value <br>";
					}elseif ($type=='conf' or $type=='conf_local'){
						$cfg[$name]=trim($value);
						#echo "$name = $value <br>";
					}
				}
				$max_e = $cfg['max_e'];
				$def_e = $cfg['def_e'];
			}else
				echo "no lee el file";
		}
		#php_error("$max_e  $def_e ");

		for ($i = 1; $i <= $cfg['max_e']; $i++) {
			if (file_exists($cfg_folder .'general.e'.$i.'.cfg')) {
				if ($handle = fopen($cfg_folder .'general.e'.$i.'.cfg','r')){
					#print $cfg_folder .'general.e'.$i.'.cfg';
					while (!feof($handle)) {
						@list($type,$name,$value) = preg_split("/\||=/", fgets($handle),3);
						#print "$type $name,$value<br>";
						if (($name == 'auth_dir' or $name == 'dbi_db' or $name == 'dbi_host' or $name == 'dbi_pw' or $name == 'dbi_user' or $name == 'app_title') and $type=='conf'){
							$cfg['emp.'.$i.'.'.$name]= trim($value);
						}
						if ($type=='sys' and $i == $cfg['def_e']){
							$sys[$name]=trim($value);
						}elseif (($type=='conf' or $type=='conf_local') and $i == $cfg['def_e']){
							$cfg[$name]=trim($value);
						}
					}
				}
			}
		}
	}

	// -------------------------------------------------------------------------
	function trans_txt($to_trans) {
		global $trs;
		global $path_templates;
		if ($trs[$to_trans]){
			return $trs[$to_trans];
		}else{

			if (file_exists($path_templates."messages.txt")) {
				if ($handle = fopen($path_templates."messages.txt",'r')){
					while (!feof($handle)) {
						$ary = explode("=", fgets($handle),2);
						$trs[$ary[0]]=trim($ary[1]);
					}
				}
			}
			return $trs[$to_trans];
		}
	}

	// -------------------------------------------------------------------------
	function php_error($sys_err) {
		global $in,$error,$va;
		require('phperror.php');
		exit;
	}

	// -------------------------------------------------------------------------
	#function addrecord($db_name) {
	#	global $db,$in, $usr, $db_cols, $db_valid_types;
	#	load_cfg($db_name);
	#	$query = '';
	#	for ($i = 1; $i < sizeof($db_cols)-3; $i++) {
	#		$query .= "$db_cols[$i]='" . filter_values($in[strtolower($db_cols[$i])]) . "',";
	#	}
	#	$query .= "Date=NOW(), Time=NOW(),ID_admin_users='".$usr[id_admin_users]."'";
	#	$result = $db->query("INSERT INTO $db_name SET $query");
	#	// Always check that $result is not an error
	#	if (DB::isError($result)) {
	#		return trans_txt("db_error") . $result->getMessage();
	#	}else{
	#		return 'ok';
	#	}
	#}

	function auth_logging($message,$action)
	{
        global $cfg,$cses,$va,$in,$usr,$device,$conn,$ip;

		if(!$usr{'id_admin_users'}) 
			$usr{'id_admin_users'} = 0;
		
		$pattern    = '<li>';
		preg_replace($pattern,' ',$action);
		$pattern    = '</li>';
		str_replace($pattern,', ',$action);
		
		if ($message=='login' or $message=='logout'){
			$type = 'Access';
		}else{
			$type = 'Application';
		}

		//&connect_db;
		$value = "LogDate=Curdate(), LogTime=NOW(), ID_admin_users=1, tbl_name='".$in['db']."',Logcmd='".$in['cmd']."', Type='$type',Message='".$message."', Action='".$action."', IP='".$ip."'";
		$sth = mysqli_query($conn, "INSERT INTO admin_logs SET $value")or die(mysqli_error($conn));		
	}

	/* - - - - - - - - - - - - - - 
	Creado el: 19-01-2018
	Por: ISC Alejandro Diaz
	 - - - - - - - - - - - - - - */
	function isadmin($id_admin_users) {
		global $cfg,$in;

		if ($id_admin_users){
			$conn = mysqli_connect ($cfg['emp.'.$in['e'].'.dbi_host'], $cfg['emp.'.$in['e'].'.dbi_user'], $cfg['emp.'.$in['e'].'.dbi_pw'], $cfg['emp.'.$in['e'].'.dbi_db']) or die(mysqli_error($conn));

			$id_admin_groups = (isset($cfg['admin_groups']) and trim($cfg['admin_groups'])!='')? trim($cfg['admin_groups']) : 1;
			$sql = "SELECT COUNT(*) AS 'isadm' from admin_users_groups where ID_admin_users=".$id_admin_users." AND ID_admin_groups IN(".$id_admin_groups.");";
			$result = mysqli_query($conn, $sql);
			$rec = mysqli_fetch_assoc($result);

			mysqli_close($conn);

			if ($rec['isadm']){
				return true;
			}
		}
		return false;
	}

#############################################################################
#############################################################################
#	Function: validate_ip_blocked
#
#	Created on: 2018-03-09
#
#	Author: Jonathan Alcantara
#
#	Modifications:
#
#	Parameters:
#
#	Returns: 
#
#	See Also:
#
function validate_ip_blocked() {
	global $conn;
	$ip = get_ip();

	$result = mysqli_query($conn, "SELECT COUNT(DISTINCT sl_ipmanager.ID_ipmanager) AS totals
							FROM sl_ipmanager
							WHERE sl_ipmanager.IP = '$ip'
							AND sl_ipmanager.`Type` = 'Blocked'
							AND sl_ipmanager.`Status` = 'Active'
							;"
						) or die(mysqli_error($conn));
	$rec = mysqli_fetch_assoc($result);
	return $rec['totals'] ? 1 : 0;

}
