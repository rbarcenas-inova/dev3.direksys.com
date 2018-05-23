<?php
	$local = php_uname ("n"); # exactamente como funciona esto ?
	$local = '1';
	
	############################################################################
	##### Functions                                                        #####
	############################################################################
	function load_object($obj){
		global $cfg, $in, $usr, $va, $error,$tpl,$cses;
		if (file_exists($cfg['path_templates'].$obj) and is_file($cfg['path_templates'].$obj)) {
			require($cfg['path_templates'].$obj);
		}
		return;
	}



	function filter_values($input){
		$output = preg_replace("/\'/", "\\'/", $input);
		return $output;
	}

	// -------------------------------------------------------------------------
	function format_price($num) {
		return ("$ " . number_format($num,2)) ;
	}
	
	function format_id($num) {
		if (strlen($num==9)){
			return (substr($num,0,3) . '-'. substr($num,3,3). '-'. substr($num,6,3)) ;
		}else{
			return (substr($num,0,3) . '-'. substr($num,3,3)) ;
		}
	}

	// -------------------------------------------------------------------------
	function date_to_sql($in_date) {
		global $usr;
		
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

		// ### A?os Viciestos
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

		list($year,$mon,$day) = split('[/.-]', $date);
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
	function save_auth_data($sid) {
		global $cfg, $usr;
		#echo "Saving in $cfg[auth_dir]$sid<br>";
		if ($handle = fopen($cfg['auth_dir'].$sid,'w')){
			foreach ($usr as $key=>$value ) {
				if ($key != "password" and $key){
					$value = preg_replace("/\r/", "", $value);
					$value = preg_replace("/\n/", "``", $value);
					fwrite($handle,"$key=$value\n");
				}
			}
			fclose($handle);
		}
	}

	// -------------------------------------------------------------------------
	function load_usr_data($sid) {
		global $usr,$cfg;
		if (file_exists($cfg['auth_dir'].$sid)) {
			if ($handle = fopen($cfg['auth_dir'].$sid,'r')){
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

	// -------------------------------------------------------------------------
	function logout() {
	//Last modified on 12 May 2011 11:00:25
//Last modified by: MCC C. Gabriel Varela S. : Se hace que setcookie aplique a raíz
		global $ck_name,$cfg,$usr;

		$sid = $_COOKIE[$ck_name];
		setcookie($ck_name, '',time()-3600,'/');
		setcookie('sessionid', '',time()-3600,'/');
		if (file_exists($cfg['auth_dir'].$sid) and is_file($cfg['auth_dir'].$sid)) {
			unlink($cfg['auth_dir'].$sid);
		}
		$sid='';
		foreach($usr as $key){
		    unset($key);   
		}
		#echo "logout : $ck_name = $sid<br>";
	}

	// -------------------------------------------------------------------------
	function load_page($fname) {
		global $usr,$cfg;
		(!$usr['pref_language']) and ($usr['pref_language']=$cfg['default_lang']);
		if (preg_match("/(.*)\/([a-z]*)_(.*)$/",$fname,$matches) and $cfg['path_ns_cgi_'.$matches[2]]){
			$fname = $matches[1]."/".$matches[2]."/".$matches[3];
		}
		$fname = preg_replace("/\[lang\]/", $usr['pref_language'], $fname);
		#echo "fname $fname<br>";
		if (file_exists("$fname")) {
			if ($handle = fopen("$fname",'r')){
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

	// -------------------------------------------------------------------------
	function build_page($tname) {

	//Last modified on 31 Mar 2010 11:48:04
//Last modified by: MCC C. Gabriel Varela S. :Se modifica para que lea tambi¨¦n de cfg
//Last modified on 16 Nov 2010 12:36:01
//Last modified by: MCC C. Gabriel Varela S. :Se modifica para hacer que no reemplace los corchetes que no tienen por qué ser reemplazados. ejemplo: [0,130]
		global $cfg, $in, $usr, $va, $cses, $error ;

		$path_file = is_file($cfg['path_templates'] . $tname) ? $cfg[path_templates] : str_replace('mobile/', '', $cfg['path_templates']); 
		$page = load_page($path_file . $tname);
		//while (preg_match("/\[([^]]+)\]/", $page, $matches) and $num<99){
		while (preg_match("/\[(\w{2,3})_([^\]]+)\]/", $page, $matches) and $num<99){
// 			$field    = $matches[2];
// 			$cmdname  = strtolower(substr($field,3));
// 			$cmdtype  = substr($field,0,3);
			$cmdtype  = strtolower($matches[1]).'_';
			$cmdname  = strtolower($matches[2]);
			$field    = "$matches[1]_$matches[2]";

			if ($cmdtype == 'cf_'){
				$rep_str = $cfg[$cmdname];
			}elseif ($cmdtype == 'ck_'){
				$rep_str = $_COOKIE[$cmdname];
			}elseif($cmdtype == 'in_'){
				$rep_str = $in[$cmdname];
			}elseif($cmdtype == 'va_'){
				$rep_str = $va[$cmdname];
			}elseif($cmdtype == 'er_'){
				$rep_str = $error[$cmdname];
			}elseif($cmdtype == 'ur_'){
				$rep_str = $usr[$cmdname];
			}elseif($cmdtype == 'cs_'){
				$rep_str = $cses[$cmdname];
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
		global $db_cols, $db_valid_types, $db_not_null;
		$sth = mysql_query("show tables like '$tbl_name';");
		$ary = mysql_fetch_array($sth);
		if (!$ary[0]){
			return;
		}
		$db_cols = array();
		$sth = mysql_query("describe $tbl_name;");
		while ($ary = mysql_fetch_array($sth)) {
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
	function validate_cols($db_cols,$req,$type,$savesess){
		global $in, $error,$cses ;
		//Function Number 022
		$function_number="022";
		for ($i = 0; $i < count($db_cols); $i++){
			$col = $db_cols[$i];
			$val = trim($in[strtolower($col)]);
			
			##### Not Null Check #####
			if (!$val and $req[$i]) {
				$error[$col] = "<span class='error'>".trans_txt('required')."</span>";
				++$err;
				#echo "$col <br>";
			##### Valid E-Mail Check #####
			}elseif ($type[$i] == "email" and ($val and !check_email_address($val,0))){
				$error[$col] = "<span class='error'>".trans_txt('invalid')."</span>";
				++$err;
				#echo "$col<br>";
			##### Valid numeric field Check #####
			}elseif ($type[$i] == "numeric" and !is_numeric($val) and $val!=''){
				$error[$col] = "<span class='error'>".trans_txt('invalid')."</span>";
				++$err;
				#echo "$col<br>";
			##### Valid Date field Check #####
			#}elsif ($db_valid_types[$col] eq "date" and $val !~ /^\s*$/){
			#	if (&date_to_sql($in[$col]) == 0){
			#		$error[$col] = "<span class='error'>Inv&aacute;lido</span>";
			#		++$err;
			#	}
			}elseif ($type[$i] == "phone" and preg_match("/[^\(\)\d- ]/",$val) and $val!=''){
				$error[$col] = "<span class='error'>".trans_txt('invalid')."</span>";
				++$err;
			}
			if ($savesess){
				$cses[$col] = $val;
			}
		}
		if ($err>0){
			return "error";
		}else{
			return "ok";
		}
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
		if (getenv('REMOTE_ADDR')){
			return getenv('REMOTE_ADDR');
		}elseif (getenv('REMOTE_HOST')){
			return getenv('REMOTE_HOST');
		}elseif (getenv('HTTP_CLIENT_IP')){
			return getenv('HTTP_CLIENT_IP');
		}else{
			return "Unknown";
		}
	}

	function ip_block ($ipfilter){
		if (trim($ipfilter)!=''){
			$ip = get_ip();
			$ips = explode(',',$ipfilter);

			if (in_array($ip, $ips)){
				return 0;
			}else{
				return 1;
			}
		}else{
			return 0;
		}
	}

	function check_ip ($ipfilter){
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
				$sth = mysql_query("SELECT COUNT(*) FROM admin_IPlist WHERE Type='Black' AND IP='$ip'");
				$ary = mysql_fetch_array($sth);
				if ($ary[0]>0){
					return 0;
				}else{
					return 1;	
				}
			}
		}
		return 0;
	}

	// -------------------------------------------------------------------------
	function save_logs($message,$action){
		global $usr,$in;
		if ($message == 'login' or $message == 'logout'){
			$type = 'Access';
		}else{
			$type = 'Action';
		}
		$sth = mysql_query("INSERT INTO admin_logs SET LogDate=NOW(),LogTime=NOW(),Logcmd='".mysql_real_escape_string($in[cmd])."',Type='$type',Message='$message',Action='".filter_values($action)."',ID_admin_users='$usr[id_admin_users]',IP='".get_ip()."'");
	}


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
		// Split it into sections to make life easier
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
	function load_sys_data() {
		global $sys,$cfg,$cfg_folder,$local;

		if (file_exists($cfg_folder."/general.".$local.".cfg")) {
			
			if ($handle = fopen($cfg_folder."/general.".$local.".cfg",'r')){
				while (!feof($handle)) {
					list($type,$name,$value) = preg_split("/\||=/", fgets($handle),3);
					if ($type=='sys'){
						$sys[$name]=trim($value);
					}elseif ($type=='conf' or $type=='conf_local'){
						$cfg[$name]=trim($value);
					}
				}
			}
		}
		
		for ($i = 1; $i <= 5; $i++) {
			if (file_exists($cfg_folder .'general.'.$local.'.e'.$i.'.cfg')) {
				if ($handle = fopen($cfg_folder .'general.'.$local.'.e'.$i.'.cfg','r')){
					while (!feof($handle)) {
						list($type,$name,$value) = preg_split("/\||=/", fgets($handle),3);
						if (($name == 'auth_dir' or $name == 'dbi_db' or $name == 'dbi_host' or $name == 'dbi_pw' or $name == 'dbi_user' or $name == 'app_title') and $type=='conf'){
							$cfg['emp.'.$i.'.'.$name]= trim($value);
						}
					}
				}
			}
		}
	}

	// -------------------------------------------------------------------------
	function load_custom_data($e) {
		global $sys, $cfg, $cfg_folder, $local;
		$dir = getcwd();
    	list($b_cgibin,$a_cgibin) = strpos( $dir, 'httpdocs' ) !== false ?
    		explode('httpdocs',$dir) :
    		explode('cgi-bin/',$dir);
            
    	$cfg_folder = $b_cgibin.'cgi-bin/common/';
		$file_cfg = $cfg_folder."general.e".$e.".cfg";
		if (file_exists($file_cfg)) {
			if ($handle = fopen($file_cfg, 'r')) {
				while (!feof($handle)) {
					list($type, $name, $value) = preg_split("/\||=/", fgets($handle), 3);
					if ($type == 'sys') {
						$sys[$name] = trim($value);
					}elseif ($type == 'conf' or $type == 'conf_local') {
						$cfg[$name] = trim($value);
					}
				}
			}
		}
        

		// for ($i = 1; $i <= 5; $i++) {
		// 	$file_cfg = "setup.e".$i.".cfg";
		// 	if (file_exists($cfg_folder . "/" . $file_cfg)) {
		// 		if ($handle = fopen($cfg_folder . "/" . $file_cfg, 'r')) {
		// 			while (!feof($handle)) {
		// 				list($type, $name, $value) = preg_split("/\||=/", fgets($handle), 3);
		// 				if (($name == 'auth_dir' or $name == 'dbi_db' or $name == 'dbi_host' or $name == 'dbi_pw' or $name == 'dbi_user' or $name == 'app_title') and $type == 'conf'){
		// 					$cfg[$name] = trim($value);
		// 				}
		// 				if ($type == 'sys') {
		// 					$sys[$name] = trim($value);
		// 				}elseif ($type == 'conf' or $type == 'conf_local') {
		// 					$cfg[$name] = trim($value);
		// 				}
		// 			}
		// 		}
		// 	}
		// }
	}

	// -------------------------------------------------------------------------
	function trans_txt($to_trans) {
		global $trs,$cfg;
		if ($trs[$to_trans]){
			return $trs[$to_trans];
		}else{
			$path_file = str_replace('mobile/', '', $cfg['path_templates']);
			if (file_exists($path_file ."messages.txt")) {
				if ($handle = fopen($path_file . "messages.txt",'r')){
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

function load_callsession() {
	global $in,$cfg,$cses;
	$pattern	=	"/([^=]+)=(.*)/";
	if ($AUTH	=	fopen("$cfg[auth_dir]/cart_".session_id(),"r")){
		while(!feof($AUTH)){
			$line	=	fgets($AUTH);
			if(preg_match($pattern,$line,$data)){
				$key	=	$data[1];
				$value	=	$data[2];
				$cses[$key]	=	$value;
			}
		}
		fclose($AUTH);
	}
	else	
		die("Unable to open rmode file: $cfg[auth_dir]/cart_".session_id());
	return;
}

function save_callsession($deleteall=0) {
	global $in,$cfg,$cses;
	$key='';
	$value='';
	if ($deleteall){
		if(is_readable("$cfg[auth_dir]/cart_".session_id()))
	  	unlink("$cfg[auth_dir]/cart_".session_id());
		session_destroy();
		create_session();
		return;
	}
	
	if ($AUTH	=	fopen("$cfg[auth_dir]/cart_".session_id(),"w")){
		//sort($cses);
		foreach ($cses as $key=>$value ){
			if(fwrite($AUTH,"$key=$value\n")===FALSE)
				echo "Error writting";
		}
		fclose($AUTH); 
  }else{
  	die ("Unable to open wmode file: $cfg[auth_dir]/cart_".session_id());
  }
}

function build_search_select (){
	global $cfg;
	$sth = mysql_query("Select *
from(Select 
	if(not isnull(sl_products_w.Title),sl_products_w.Title,if(not isnull(sl_categories.Title),sl_categories.Title,'".trans_txt('other')."'))as Title,
	if(not isnull(sl_products_prior.web_available) and sl_products_prior.web_available!='',sl_products_prior.web_available,sl_products.web_available) as web_available,
	if(not isnull(sl_products_prior.Status) and sl_products_prior.Status!='',sl_products_prior.Status,sl_products.Status) as Status
from sl_products
left join sl_products_prior on(sl_products.ID_products=sl_products_prior.ID_products)
and sl_products_prior.belongsto='$cfg[owner]'
inner join sl_products_w on(sl_products.ID_products=sl_products_w.ID_products)
left join sl_products_categories on(sl_products.ID_products=sl_products_categories.ID_products)
left join sl_categories on (sl_products_categories.ID_categories=sl_categories.ID_categories)
where $cfg[whereproducts])as sl_products
group by Title;") or die("Query failed : " . mysql_error());
	$output = "<select name=\"category\" id=\"category\" style='border: 1px solid #ffffff; width:70px;height:23px; padding-left:0px; font-family:verdana; font-size:12px; font-weight:normal; color:#555555;'>";
	$output .= "<option value=''>".trans_txt('all')."</option>\n";
	while ($rec = mysql_fetch_assoc($sth)){
		$output .= "<option value=\"".ucfirst(strtolower($rec['Title']))."\">".ucfirst(strtolower($rec['Title']))."</option>\n";
	}
	$output .= "</select>";
	return $output;
}

function get_order_info($id_orders=0){
# --------------------------------------------------------
# Forms Involved: 
# Created on: 11/04/09 10:17:00
# Author: MCC C. Gabriel Varela S.
# Description :   
# Parameters :
//Last modified on 2 Mar 2011 16:03:16
//Last modified by: MCC C. Gabriel Varela S. :Se incluye birthday
	global $in,$local;

	if($id_orders==0){

		session_start();
		global $in,$cfg,$cses,$usr,$cfg_folder,$trs;
	  
		#########################################################
		#### INIT System Data
		#########################################################
		$in  = array();
		$va  = array();
		$trs = array();
		$usr = array();
		$sys = array();
		$cfg = array();
		$cses= array();
		$error= array();
		
		if($local == "n3"){
		    $cfg_folder        = "/home/www/inn_domains/dev.innovashop.tv/cgi-bin/nsc_admin/common/";
		}
		elseif($local == "s12.shoplatinotv.com"){
		    $cfg_folder        = "/home/www/domains/innovashop.tv/cgi-bin/nsc_admin/common/";
		}
		else{
// MOD*OSANCHEZ			
//		    $cfg_folder        = "/windows/D/home/www/domains/dev2.innovashop.tv/cgi-bin/nsc_admin/common/";
		    $cfg_folder        = "/home/www/domains_local/dev.innovashop.tv/cgi-bin/nsc_admin/common/";
		}
		
		load_sys_data();
		if(is_readable("$cfg[auth_dir]/cart_".session_id())){
			load_callsession();
		}
		
		$id_orders = $cses['id_orders']; 

		## Language Selection
		if ($in['lang']){
			$_SESSION['lang'] = $in['lang'];
		}elseif (isset($_COOKIE['lang'])){
			$usr['pref_language'] = $_COOKIE['lang'];
		}else{
			$usr['pref_language'] = $cfg['default_lang'];
		}
		$cfg['path_templates'] = preg_replace("/\[lang\]/", $usr['pref_language'] , $cfg['path_templates']);

		(!isset($usr['pref_maxh'])) and ($usr['pref_maxh'] = 20);

		mysql_pconnect ($cfg['dbi_host'], $cfg['dbi_user'], $cfg['dbi_pw']) or die("Error en conexion");
		mysql_select_db ($cfg['dbi_db']) or die("Error en selecci??".$cfg['dbi_db']." ".mysql_error());
	}
	if(!$id_orders)
		return;
	
	$sth = mysql_query("SELECT sl_orders.status,statuspay,statusprd,sl_orders.date,sl_orders.time,sl_orders.id_customers,firstname,lastname1,lastname2,birthday,date_format(birthday,'%m')as birthday_month,day(birthday)as birthday_day,sex,phone1,phone2,cellphone,atime,shp_name,sl_orders.address1,sl_orders.address2,sl_orders.address3,sl_orders.urbanization,sl_orders.city,sl_orders.state,sl_orders.zip,sl_orders.country,sl_orders.billingnotes,sl_orders.shp_notes,sl_orders.shp_type,ordernotes,orderqty,ordernet,ordershp,ordertax,sum( if(not isnull(Tax),Tax,0) ) as total_taxes,round((Sum(if(ID_products not like '6%' and not isnull(ID_products),if(not isnull(SalePrice),SalePrice,0),0))-OrderDisc)*(1+OrderTax)+OrderShp+Sum(if(ID_products like '6%' and not isnull(ID_products),if(not isnull(SalePrice),SalePrice,0),0)),2) as total_order
FROM sl_orders
inner join sl_customers on(sl_orders.ID_customers=sl_customers.ID_customers)

left JOIN sl_orders_products ON ( sl_orders.ID_orders = sl_orders_products.ID_orders ) 
left join (select ID_orders,sum(amount)as SumPay 
           from sl_orders_payments 
           where ID_orders=$id_orders
           and Status not in ('Cancelled','Void','Order Cancelled') 
           group by ID_orders)as tempo on (tempo.ID_orders=sl_orders.ID_orders)
where sl_orders.id_orders=$id_orders AND (sl_orders_products.Status not in('Inactive')or isnull(sl_orders_products.Status))
GROUP BY sl_orders.ID_orders") or die("Query failed : " . mysql_error());
$rec = mysql_fetch_assoc($sth);
//echo "Total: ".$rec['OrderNet'];
foreach ($rec as $key=>$value )
{
	$in[strtolower($key)] = "$value";
}
setlocale(LC_MONETARY, 'en_US');
$in['ordernet']= format_price($in['ordernet']);
$in['ordershp']=format_price($in['ordershp']);
$in['ordertax']=number_format($in['ordertax'],3);
$in['total_taxes']=format_price($in['total_taxes']);
$in['total_order']=format_price($in['total_order']);

}

function html_invoice($id_orders,$returndata=0,$email_version=0) {
# --------------------------------------------------------
# Author: Oscar Sanchez Villavicencio
# Created on: gedit
# Last Modified on: 24-01-2012
# Last Modified by: 
# Description : 
# Forms Involved: 
# Parameters :
# Last Time Modified By RB on 03/19/2012: Servicio de Continuidad no impreso. 

	global $in,$cfg,$cses,$va;
	$total_tax=0;$total_discount=0;$total_shipping=0;$tot_ord=0;$total_order=0;

	$sth = mysql_query("SELECT COUNT(*) FROM sl_orders_products WHERE ID_orders='$id_orders' AND Status!='Inactive' and '$id_orders'!=''") or die("Query failed : " . mysql_error());
	$va['matches'] = mysql_result($sth,0);
	if ($va['matches']>0) {
		$sth1 = mysql_query("SELECT * FROM sl_orders_products WHERE ID_orders='$id_orders' AND Status!='Inactive' and '$id_orders'!='' ORDER BY ID_orders_products  DESC;") or die("Query failed : " . mysql_error());
		while ($rec = mysql_fetch_assoc($sth1)) {

			$va['INNOVENTIONS'] = "INNOVENTIONS INTERNATIONAL<br>2308 Peck Road <br>City of Industry, CA 90601<br>Tel. 1-888-339-2990";
			$va['customer_data'] = $cses['firstname']." ".$cses['lastname1']." ".$cses['lastname2']."<br>".$cses['address1']."<br>".$cses['address2']."<br>".$cses['address3']."<br>".$cses['urbanization']."<br>".$cses['city']."<br>".$cses['state']." ".$cses['zip'];
			$va['customer_destination'] = $cses['firstname']." ".$cses['lastname1']." ".$cses['lastname2']."<br>".$cses['shp_address1']."<br>".$cses['shp_address2']."<br>".$cses['shp_address3']."<br>".$cses['shp_urbanization']."<br>".$cses['shp_city']."<br>".$cses['shp_state']." ".$cses['shp_zip'];

			$tot_qty += $rec['Quantity'];
			$tot_ord +=$rec['SalePrice']*$rec['Quantity'];
			$tot_ord_item =$rec['SalePrice']*$rec['Quantity'];
			$total_tax += $rec['Tax'];
			$total_shipping += $rec['Shipping'];
			$total_discount += $rec['Discount'];
			$total_order += ($rec['SalePrice']*$rec['Quantity']) - $rec['Discount'] + $rec['Shipping'] + $rec['Tax'];

			$va['subtotal'] = format_price($tot_ord);
			$va['send_and_handle'] = format_price($total_shipping);
			$va['discount'] = format_price($total_discount);
			$va['tax'] = format_price($total_tax);
			$va['total'] = format_price($total_order);

			## It's a service?
			$ptype = substr($rec['ID_products'],0,1);
			if($ptype != 6 and $ptype != 4){ 
					$name=load_name('sl_products','ID_products',substr($rec['ID_products'],3,6),'Name');
			}elseif($ptype == 6){
					$name .=load_name('sl_services','ID_services',substr($rec['ID_products'],5,4),'Name');
					
					if(load_name('sl_services','ID_services',substr($rec['ID_products'],5,4),'ServiceType') == 'Refill'){
						$name = trans_txt('refill_service') . ' ('. $name .')';
						##Skip printing Refill Service
						continue;
					}

			}

			$va_detail .= "
<table cellpadding=0 cellspacing=0 border=0 height=80px>
<tr>
	<td width=90px valign=top align=left><font class=detalles>".format_sltvid($rec['ID_products'])."
		<div style='position:relative;right:27px;bottom:18px;'>".$rec['Quantity']."</div>
	</td>        
	<td width=350px valign=top align=left><font class=detalles>".$name."
	</td>
	<td width=70px valign=top align=left><font class=detalles>".format_price($rec['SalePrice'])."</td>
	<td width=60px valign=top align=left><font class=detalles>".format_price($tot_ord_item)."</td>
</tr>
</table>";
		
		}  // End While

		$va['detail'] = $va_detail;
		$va['href_nota1'] = "<a href='$cfg[signin_urlconfirm]/regalo-d'>";
		$va['href_nota2'] = "<a href='$cfg[signin_urlconfirm]/index.php?cmd=search&keyword=bioxtron'>";
		$va['href_nota3'] = "<a href='$cfg[signin_urlconfirm]/login-D'>";
		$va['href_end'] = "</a>";

		$in['pmtfield1'] = $cses["pmtfield1"];

		$in['pmtfield7'] = $cses["pmtfield7"];
		$in['pmtfield2'] = $cses["firstname"]." ".$cses["lastname"];
		$va['last4dig'] = substr($cses["pmtfield3"],-4);
		$in['pmtfield4'] = $cses["expmm"].$cses["expyy"];
		$va['amount'] = $total_order;
		$va['fpdias'] = $cses["fpdate1"];
		$va['cardtype'] = strtolower(trans_txt($cses["pmtfield7"]));

		$va['mo_data'] = $cfg['shop_rfc'];
		$va['total_order'] = format_price($total_order);

		switch($cses["paytype"]) {
			case "Credit-Card"	: $paysummary_file = "paysummary_cc.html"; break;
			case "COD"	: $paysummary_file = "paysummary_cod.html"; break;
			case "paypal"	: $paysummary_file = "paysummary_paypal.html"; break;
			case "descuentolibre"	: $paysummary_file = "paysummary_descuentolibre.html"; break;
			default : $paysummary_file = "paysummary_check.html"; break;
		}  // End switch

		$note = build_page("cart/content/".$paysummary_file);
		$va['note'] = $note;

		$file = $email_version ? 'invoice_email.html' : 'invoice.html';
		$invoice_body = build_page('cart/content/' . $file);

		return $invoice_body;
	}  // End if
}  // End function


function load_order_products($id_orders,$returndata=0) {
# --------------------------------------------------------
# Author: Unknown
# Created on: Unknown
# Last Modified on: 08/18/2008
# Last Modified by: Jose Ramirez Garcia
# Description : Se agrego el parametro de products a la funcion build_tracking_link
# Forms Involved: 
# Parameters : 
//Last modified on 12 May 2011 16:20:56
//Last modified by: MCC C. Gabriel Varela S. :Se hace que no se imprima ningún dato si no existe orden.

	global $in,$cfg,$cses;

	$total_tax=0;$total_discount=0;$total_shipping=0;$tot_ord=0;$total_order=0;

	$sth = mysql_query("SELECT COUNT(*) FROM sl_orders_products WHERE ID_orders='$id_orders' AND Status!='Inactive' and '$id_orders'!=''") or die("Query failed : " . mysql_error());
	$va['matches'] = mysql_result($sth,0);
	if ($va['matches']>0){
		$c = explode(",",$cfg{'srcolors'});
		$sth1 = mysql_query("SELECT * FROM sl_orders_products WHERE ID_orders='$id_orders' AND Status!='Inactive' and '$id_orders'!='' ORDER BY ID_orders_products  DESC;") or die("Query failed : " . mysql_error());
		while ($rec = mysql_fetch_assoc($sth1))
		{
			$d = 1 - $d;
			$output .= "<tr bgcolor='$c[$d]'>\n";
			
			if($in{'toprint'} or isset($cses['final']))
					$output .= "   <td valign='top' class='l1_text'>".format_sltvid($rec['ID_products'])." </td>\n";
			else
			{
				$name=load_name('sl_products','ID_products',substr($rec['ID_products'],3,6),'Name');
				$namep=load_name('sl_products_prior','ID_products',substr($rec['ID_products'],3,6),'Name');
				if($namep!='')
					$name=$namep;
				$name=replace_in_string($name);
				$output .= "   <td valign='top' class='l1_text'><a href='/".$name."-a' title='".trans_txt('goto_product')."' class='m_text'>".format_sltvid($rec['ID_products'])." </a></td>\n";
			}

			##Modelo/Nombre del Producto
			if(substr($rec['ID_products'],0,1)  ==  6){
				$name=load_name('sl_services','ID_services',substr($rec['ID_products'],5,4),'Name');
				$name=replace_in_string($name);
				$output .= "  <td class='l1_text'>".$namep."</td>\n";
			}else{
				$name=load_name('sl_products','ID_products',substr($rec['ID_products'],3,6),'Name');
				$namep=load_name('sl_products_prior','ID_products',substr($rec['ID_products'],3,6),'Name');
				if($namep != '')
					$name=$namep;
				$name=replace_in_string($name);
				$output .= "  <td class='l1_text'>".$name." ".load_choices($rec['ID_products'])."</td>\n";
			}
			
			
			  
		  ## Fecha de Envio/Retorno del Producto
		  
			if($rec['ShpDate']){#JRG show the return date
			    $output .= "  <td valign='top' align='right' class='l1_text'>".build_tracking_link($rec['Tracking'],$rec['ShpProvider'],$rec['ShpDate'],$rec["ID_orders_products"],$in{'toprint'},1)."</td>\n";
			}else {
				#$returndate = load_name('sl_returns',"ID_orders_products",$rec["ID_orders_products"],'Date');
				if($returndate){
					$output .= "  <td valign='top' align='right' class='l1_text'>".$returndate."</td>\n";
				} else {
					$output .= "  <td valign='top' align='right' class='l1_text'>&nbsp;</td>\n";
				}
			}
			
			$tot_qty += $rec['Quantity'];
			$tot_ord +=$rec['SalePrice']*$rec['Quantity'];
			$total_tax += $rec['Tax'];
			$total_shipping += $rec['Shipping'];
			$total_discount += $rec['Discount'];
			$total_order += ($rec['SalePrice']*$rec['Quantity']) - $rec['Discount'] + $rec['Shipping'] + $rec['Tax'];
			$output .= "  <td align='center' class='l1_text'>".$rec['Quantity']."</td>\n";
			$output .= "  <td align='right' class='l1_text'>". format_price($rec['SalePrice']) ."</td>\n";
			$output .= "</tr>\n";						
		}
		$output .= "
			<tr>
				<td colspan='4' align='right' class='l1_text'><strong>Subtotal</strong></td>
				<td align='right' class='l1_text'><strong>". format_price($tot_ord) ."</strong></td>
			</tr>
			<tr>
				<td colspan='4' align='right' class='l1_text'>". trans_txt('discount')."</td>
				<td align='right' class='l1_text'>". format_price($total_discount) ."</td>
			</tr>
			<tr>
				<td colspan='4' align='right' class='l1_text'>S&H</td>
				<td align='right' class='l1_text'>". format_price($total_shipping) ."</td>
			</tr>
			<tr>
				<td colspan='4' align='right' class='l1_text'>Tax</td>
				<td align='right' class='l1_text'>". format_price($total_tax) ."</td>
			</tr>
			<tr>
				<td colspan='4' align='right' class='dat'><strong>Total</strong></td>
				<td align='right' class='head2'><strong>". format_price($total_order) ."</strong></td>
			</tr>\n";
	}else{
		$output = "
			<tr>
				<td colspan='6' align='center' class='l1_text'>".trans_txt('search_nomatches')."</td>
			</tr>\n";
	}	
	
	if($returndata==1)
	    return $output;
	else
	    echo $output;
}

function format_sltvid($id) {
# --------------------------------------------------------
	
	if (strlen($id) ==9){
		return substr($id,0,3) .'-'.substr($id,3,3) . '-' . substr($id,6,3);
	}else{
		return substr($id,0,3) .'-'.substr($id,3,3);
	}
}

function load_choices($id,$choices='') {
# --------------------------------------------------------
# Forms Involved: 
# Created on: 9/12/2007 11:29AM
# Last Modified on:
# Last Modified by:
# Author: Carlos Haas
# Description : 

	if ($choices[0] or $choices[1] or $choices[2] or $choices[3]){
		$output = implode(',',$choices);
	}else{
		$output = &load_db_names('sl_skus','ID_sku_products',$id,'[choice1],[choice2],[choice3],[choice4]');
	}
	
	$output=preg_replace('/,,|,$/','',$output);
	
	if($output){
		$output = "<br><span class='help_on'>".trans_txt('choice').": $output</span>";
	}
	#$output .= "es este";
	return $output;
}


/*
	Function: load_name
   		Extract a specific value frm a specif table

	Created by:
		_Carlos Haas_

	Modified By:


   	Parameters:
		- db: Table name
		- id_name: Field to look for
		- id_value: Value of the field
		- field: Name of the vield to be returned

   	Returns:
		The specified field value

   	See Also:

      load_db_names
*/
function load_name($db,$id_name,$id_value,$field) {
    if($id_value!='NOW()' or $id_value!='CURDATE()')
		$id_value="'$id_value'";
	$sth = mysql_query("SELECT ".$field." FROM ".$db." WHERE ".$id_name."=".$id_value.";") or die("Query failed : " . mysql_error());
    if(mysql_num_rows($sth) > 0)
        return mysql_result($sth,0);
}


function load_names($table, $id_name, $id_value, $fields, $conn) {
    if($id_value!='NOW()' or $id_value!='CURDATE()')
		$id_value="'$id_value'";
	
	$sql = "SELECT ".$fields." FROM ".$table." WHERE ".$id_name."=".$id_value.";";
	$sth = mysql_query($sql, $conn) or die("Query failed : " . mysql_error());
    if(mysql_num_rows($sth) > 0) {
    	$res = mysql_fetch_assoc($sth);
    	return $res;
    }
}

/*
	Function: load_db_names
   		Extract specific field values from a table

	Created by:
		_Carlos Haas_

	Modified By:


   	Parameters:
		- db: Table name
		- id_name: Field to look for
		- id_value: Value of the field
		- str_out: Names of the field to be returned

   	Returns:
		A string with one or more field values concateated

   	See Also:
		- load_name
*/
function load_db_names($db,$id_name,$id_value,$str_out) {
# --------------------------------------------------------

	$sth = mysql_query("SELECT * FROM $db WHERE $id_name='$id_value';") or die("Query failed : " . mysql_error());
	$rec = mysql_fetch_assoc($sth);
	if ($rec[$id_name]>0){
		foreach ($rec as $key=>$value )
		{
			$str_out=preg_replace("/\[$key\]/",$rec[$key],$str_out);
		}
		return $str_out;
	}else{
		return '';
	}
}

function itemshipping($edt,$sizew,$sizeh,$sizel,$weight,$idpacking,$shpcal,$shpmdis,$id_products) {
# --------------------------------------------------------
# Created on: 07/10/08 @ 16:21:10
# Author: Carlos Haas
# Last Modified on: 07/10/08 @ 16:21:10
# Last Modified by: Carlos Haas
# Description : 
# Parameters : 
# Last Modified on: 03/17/09 16:00:32
# Last Modified by: MCC C. Gabriel Varela S: Se considera total3
# Last Time Modified by RB on 12/13/2010: Se agregan parametros para calculo con shipping_table			   
# Last Time Modified by RB on 01/21/2011: Se corrigio busqueda de Zona 

	global $cses,$cfg;

	//Function Number 019
	$function_number="019";
	
	if($shpcal == 'Table'){

		## Zone?
		$zone = 'USA';
		if($cses['shp_state'] != ''){
			$sth =  mysql_query("SELECT GROUP_CONCAT( DISTINCT Zone SEPARATOR ':' ) FROM `sl_products_shipping` ;");
			list($shipping_zones) = mysql_fetch_row($sth);
			$ary_zones = explode(':',$shipping_zones); 
	
			while(list(,$value) = each($ary_zones)){
					if(preg_match('/'.$cses['shp_state'].'/',$value)){
						$zone = $value;
					}	
			}	
		}
		
		## Method?
		$method = 'credit-card';
		($cses['paytype'] != '') and ($method = strtolower($cses['paytype']));
		($method != 'cod') and ($method = 'credit-card'); 
		
		## Amount ?
		$amount = '0.01';
		($shpmdis == 'Yes' and $cses['total_i'] > 0) and ($amount = $cses['total_i']);
		
		## Quantity
		$quantity = 1;
		
		if($shpmdis == 'Yes'){
			## Revisar cantidad en 
			if($cses['items_in_basket'] > 0 ){
				for ($i=1; $i <= $cses['items_in_basket']; $i++){
					if ($cses['items_'.$i.'_qty'] > 0  and $cses['items_'.$i.'_id'] > 0 and substr($cses['items_'.$i.'_id'],3,6) == $id_products){
						$quantity++;
					}
				}
				$quantity--;
			}
			## 
		}
		$sth = mysql_query("SELECT Shipping_price FROM `sl_products_shipping` WHERE ID_products = '$id_products' AND `Zone` = '$zone' AND LOWER(`Method`) = '$method' AND `Quantity` <= $quantity AND Amount <= $amount ORDER BY Amount DESC, Quantity DESC LIMIT 1; ");
		list($shprice)= mysql_fetch_row($sth);
		
		$shptotal1 = $shprice;
		$shptotal2 = $shprice;	
		$shptotal3 = $shprice;	
		$shptotal1pr = $shprice;
		$shptotal2pr = $shprice;
		$shptotal3pr = $shprice;
			
	}elseif ($idpacking>0){
		## US Continental
		$shptotal1 = load_name('sl_packingopts','ID_packingopts',$idpacking,'Shipping');
		$shptotal2 = $shptotal1+14;		
		$shptotal3 = $shptotal1;		
		#$shptotal2 = 16;
		## Puerto Rico
		$shptotal1pr = $shptotal1;
		$shptotal2pr = $shptotal1+14;
		$shptotal3pr = $shptotal1;

		$shipping_a['shptype1_min']	+= $edt;
		$shipping_a['shptype1_max']	+= $edt;
		$shipping_a['shptype2_min']	+= $edt;
		$shipping_a['shptype2_max']	+= $edt;		
		$shipping_a['shptype3_min']	+= $edt;
		$shipping_a['shptype3_max']	+= $edt;
	}else{
		### Shipping US continental
		
		$shipping_a['shptype1_min']	+= $edt;
		$shipping_a['shptype1_max']	+= $edt;
		$shipping_a['shptype2_min']	+= $edt;
		$shipping_a['shptype2_max']	+= $edt;
		$shipping_a['shptype3_min']	+= $edt;
		$shipping_a['shptype3_max']	+= $edt;
		
		## Shipping type 1
		$aux = round($sizew*$sizeh*$sizel/$shipping_a['shpconv1']+0.9);
		if ($aux > $weight){
			$weight = $aux;
		}
		if ($weight>1){
			$shptotal1 = round($shipping_a['shptype1_1lb'] + $shipping_a['shptype1_add']*($weight -1 + 0.9));
		}else{
			$shptotal1 = $shipping_a['shptype1_1lb'];
		}
	
		## Shipping type 2
		$aux = round($sizew*$sizeh*$sizel/$shipping_a['shpconv2']+0.9);
		if ($aux > $weight){
			$weight = $aux;
		}
		if ($weight>1){
			$shptotal2 = round($shipping_a['shptype2_1lb'] + $shipping_a['shptype2_add']*($weight-1 + 0.9));
		}else{
			$shptotal2 = $shipping_a['shptype2_1lb'];
		}
		
		## Shipping type 3
		$aux = round($sizew*$sizeh*$sizel/$shipping_a['shpconv3']+0.9);
		if ($aux > $weight){
			$weight = $aux;
		}
		if ($weight>1){
			$shptotal3 = round($shipping_a['shptype3_1lb'] + $shipping_a['shptype3_add']*($weight -1 + 0.9));
		}else{
			$shptotal3 = $shipping_a['shptype3_1lb'];
		}
		
		
		## Shipping type 1
		$aux = round($sizew*$sizeh*$sizel/$shipping_a['shpconv1pr']+0.9);
		if ($aux > $weight){
			$weight = $aux;
		}
		if ($weight>1){
			$shptotal1pr = round($shipping_a['shptype1pr_1lb'] + $shipping_a['shptype1pr_add']*($weight -1 + 0.9));
		}else{
			$shptotal1pr = $shipping_a['shptype1pr_1lb'];
		}
	
		## Shipping type 2
		$aux = round($sizew*$sizeh*$sizel/$shipping_a['shpconv2pr']+0.9);
		if ($aux > $weight){
			$weight = $aux;
		}
		if ($weight>1){
			$shptotal2pr = round($shipping_a['shptype2pr_1lb'] + $shipping_a['shptype2pr_add']*($weight-1 + 0.9));
		}else{
			$shptotal2pr = $shipping_a['shptype2pr_1lb'];
		}
		
		## Shipping type 3
		$aux = round($sizew*$sizeh*$sizel/$shipping_a['shpconv3pr']+0.9);
		if ($aux > $weight){
			$weight = $aux;
		}
		if ($weight>1){
			$shptotal3pr = round($shipping_a['shptype3pr_1lb'] + $shipping_a['shptype3pr_add']*($weight -1 + 0.9));
		}else{
			$shptotal3pr = $shipping_a['shptype3pr_1lb'];
		}
		
	}
	
	$shipping_a['shptype1pr_min']	+= $edt;
	$shipping_a['shptype1pr_max']	+= $edt;
	$shipping_a['shptype2pr_min']	+= $edt;
	$shipping_a['shptype2pr_max']	+= $edt;	
	$shipping_a['shptype3pr_min']	+= $edt;
	$shipping_a['shptype3pr_max']	+= $edt;
	
	
	
	#######  Shipping in Dates
	$shp_text1 =  $shipping_a['shptype1']." (".$shipping_a['shptype1_min']."-".$shipping_a['shptype1_max']." D&iacute;as)";
	$shp_text2 =  $shipping_a['shptype2']." (".$shipping_a['shptype2_min']."-".$shipping_a['shptype2_max']." D&iacute;as)";
	$shp_text3 =  $shipping_a['shptype3']." (".$shipping_a['shptype3_min']."-".$shipping_a['shptype3_max']." D&iacute;as)";
		
	#######  Shipping-PR in Dates
	$shp_text1 =  $shipping_a['shptype1pr']." (".$shipping_a['shptype1pr_min']."-".$shipping_a['shptype1pr_max']." D&iacute;as)";
	$shp_text2 =  $shipping_a['shptype2pr']." (".$shipping_a['shptype2pr_min']."-".$shipping_a['shptype2pr_max']." D&iacute;as)";
	$shp_text3 =  $shipping_a['shptype3pr']." (".$shipping_a['shptype3pr_min']."-".$shipping_a['shptype3pr_max']." D&iacute;as)";		

	return array($shptotal1,$shptotal2,$shptotal3,$shptotal1pr,$shptotal2pr,$shptotal3pr,$shp_text1,$shp_text2,$shp_text3,$shp_textpr1,$shp_textpr2,$shp_textpr3);
}

function calculate_shipping() {
#-----------------------------------------------
# Last Time Modified by RB on 12/13/2010 : Se agregan paramentros para calculo via tabla de shippings y posible descuento en envio via general.cfg	
# Last modified on 04/13/11 04:56:16 PM
# Last modified by: MCC C. Gabriel Varela S. :Se integra reward points
# Last modified by RB on 11/24/2011: Se agrega $cses['items_'.$i.'_free'] para productos con envio gratis (usado en productos 2x1)
# Last modified by RB on 04/28/2012: Se valida que exista en el arreglo $cses['items_'.$i.'_gift'] para devolver shipping de gift

	global $cses,$cfg;
	
	## Calculate Shipping
	$shptotal1 = 0;
	$shptotal2 = 0;
	$shptotal3 = 0;
	$shptotalf = 0;
	
	if ($cses['items_in_basket'] > 0){
		for ($i=1;$i<=$cses['items_in_basket'];$i++){
			if ($cses['items_'.$i.'_qty']>0  and $cses['items_'.$i.'_id']>0){

				if(!empty($cses['items_'.$i.'_free'])){
					continue;
				}

 				//echo "Valur: ".$cses['items_'.$i.'_qty'].",".$cses['items_'.$i.'_id']."\n";
				$tprod='id';
				$idpacking = load_name('sl_products','ID_products',substr($cses['items_'.$i.'_'.$tprod],3,6),'ID_packingopts');
				
				$q1 = "SELECT ID_packingopts FROM sl_products_prior WHERE ID_products = '".substr($cses['items_'.$i.'_'.$tprod],3,6)."' AND BelongsTo = '".$cfg['owner']."';";
				$sth = mysql_query($q1);
				list($idpackingp) = mysql_fetch_row($sth);

				
				## By Table?
				$shpcal = load_name('sl_products','ID_products',substr($cses['items_'.$i.'_'.$tprod],3,6),'shipping_table');
				$shpmdis = load_name('sl_products','ID_products',substr($cses['items_'.$i.'_'.$tprod],3,6),'shipping_discount');
				$shpcalp = load_name('sl_products_prior','ID_products',substr($cses['items_'.$i.'_'.$tprod],3,6),'shipping_table');
				
				if($shpcalp != ''){
					$shpcal = $shpcalp;
					$shpmdis = load_name('sl_products_prior','ID_products',substr($cses['items_'.$i.'_'.$tprod],3,6),'shipping_discount');
				}
				
				if($idpackingp!='' and $idpackingp > 0)
					$idpacking=$idpackingp;
				if(substr($cses['items_'.$i.'_id'],3,6)==$cses['reward_points_used'] and $cses['items_'.$i.'_reward_points'] and $cses['reward_points_applied']==1)
				{
					$shippings=array($cfg['reward_points_id_promo_shipping'],$cfg['reward_points_id_promo_shipping'],$cfg['reward_points_id_promo_shipping'],$cfg['reward_points_id_promo_shipping'],$cfg['reward_points_id_promo_shipping'],$cfg['reward_points_id_promo_shipping']);
				}
				else if(substr($cses['items_'.$i.'_id'],3,6)==$cfg['gifts_ids'] and !empty($cses['items_'.$i.'_gift']) )
				{
					$shippings=array($cfg['gifts_shippings'],$cfg['gifts_shippings'],$cfg['gifts_shippings'],$cfg['gifts_shippings'],$cfg['gifts_shippings'],$cfg['gifts_shippings']);
				}
				else
				{
					$shippings= itemshipping($cses[edt],$cses['items_'.$i.'_size'],1,1,$cses['items_'.$i.'_weight'],$idpacking,$shpcal,$shpmdis,substr($cses['items_'.$i.'_'.$tprod],3,6));
				}

				## general.cfg discount?
				if($cfg['shpdis_cc'] > 0 and $cses['paytype'] == 'Credit-Card' and $shpcal == 'Fixed' and substr($cses['items_'.$i.'_id'],3,6)!=$cfg['gifts_ids'] and($cses['items_'.$i.'_reward_points']!=1 or !isset($cses['items_'.$i.'_reward_points']) ) ){
					$shippings[0] *= $cfg['shpdis_cc'];
					$shippings[1] *= $cfg['shpdis_cc'];
					$shippings[2] *= $cfg['shpdis_cc'];
					$shippings[3] *= $cfg['shpdis_cc'];
					$shippings[4] *= $cfg['shpdis_cc'];
					$shippings[5] *= $cfg['shpdis_cc'];
				}


				if ($shpcal != 'Table' and ($cses[shp_state] == 'PR-Puerto Rico' or $cses[shp_state] == 'AK-Alaska' or $cses[shp_state] == 'HI-Hawaii')){
					$shptotal1 += $shippings[3];
					$shptotal2 += $shippings[4];
					$shptotal3 += $shippings[5];
				}else{
					$shptotal1 += $shippings[0];
					$shptotal2 += $shippings[1];
					$shptotal3 += $shippings[2];
				}
			}
		}
	}
	return array($shptotal1,$shptotal2,$shptotal3);
}

function shipping_box($rec){
# --------------------------------------------------------
# Forms Involved: 
# Created on: 05/10/10 13:29:24
# Author: MCC C. Gabriel Varela S.
# Description :   
# Parameters :
#global $in;
# Last Time Modified by RB on 12/13/2010: Se agregan parametros para calculo de shipping con tabla

	global $va,$cfg;	
	
	(!$rec['size']) and ($rec['size']=1);
	$idpacking = load_name('sl_products','ID_products',$rec['id_products'],'ID_packingopts');

	$q1 = "SELECT ID_packingopts FROM sl_products_prior WHERE ID_products = '".$rec['id_products']."' AND BelongsTo = '".$cfg['owner']."';";
	$sth = mysql_query($q1);
	list($idpackingp) = mysql_fetch_row($sth);
	
	## By Table?
	$shpcal = load_name('sl_products','ID_products',$rec['id_products'],'shipping_table');
	$shpmdis = load_name('sl_products','ID_products',$rec['id_products'],'shipping_discount');
	$shpcalp = load_name('sl_products_prior','ID_products',$rec['id_products'],'shipping_table');
	
	if($shpcalp != ''){
		$shpcal = $shpcalp;
		$shpmdis = load_name('sl_products_prior','ID_products',$rec['id_products'],'shipping_discount');
	}
	
	$va['shp-alert'] = $shpcal != 'Table' ? '' : '<img id="shipping_alert" src="/images/shipping-alert.png" title="El costo del envío de este producto será calcualdo en base al zipcode, por lo que es posible que varíe." >';
	
	if($idpackingp!=0)
		$idpacking=$idpackingp;
	$shippings= itemshipping($rec['edt'],$rec['size'],1,1,$rec['weight'],$idpacking,$shpcal,$shpmdis,$rec['id_products']);
	
	return $shippings[0];
//	if ($cses[shp_state] == 'PR-Puerto Rico' or $cses[shp_state] == 'AK-Alaska' or $cses[shp_state] == 'HI-Hawaii'){
//		$shptotal1 += $shippings[3];
//		$shptotal2 += $shippings[4];
//		$shptotal3 += $shippings[5];
//	}else{
//		$shptotal1 += $shippings[0];
//		$shptotal2 += $shippings[1];
//		$shptotal3 += $shippings[2];
//	}
}

function update_cart_session(){
// --------------------------------------------------------
// Forms Involved: 
// Created on: 5 Jan 2010 10:10:25
// Author: MCC C. Gabriel Varela S.
// Description :   
// Parameters :
//Last modified on 04/13/11 04:57:17 PM
//Last modified by: MCC C. Gabriel Varela S. : Se integra reward_points
//Last modified on 2 May 2011 13:17:38
//Last modified by: MCC C. Gabriel Varela S. : Se integra promo_campaign
	global $cses,$in,$usr;
	//Calcular type
	#$cses['type']='Retail';
	$cses['products_in_basket'] = 0;
	//Calcular dayspay
	#$cses['dayspay']=1;
	//Calcular tax
	$cses['tax_total']=calculate_taxes($cses['shp_zip'],$cses['shp_state']);
	//Calcular shp_type
	if($cses['paytype']=='COD')
		$cses['shp_type']=3;
	elseif($cses['paytype']=='Credit-Card')
		$cses['shp_type']=1;
	else
		$cses['shp_type']= 1;
	//Calcular shipping_total
	$tot_shps=calculate_shipping();
	
	$cses['shipping_total']=$tot_shps[$cses['shp_type']-1];
 	
	//Calcular total_i
	$total_i=0;
	for ($i=1;$i<=$cses['items_in_basket'];$i++){
		if ($cses['items_'.$i.'_qty']>0  and $cses['items_'.$i.'_id']>0){
			if($cses['items_'.$i.'_fpprice'] > 0){
				$total_i+=$cses['items_'.$i.'_qty']*$cses['items_'.$i.'_fpprice'];
			}else{
				$total_i+=$cses['items_'.$i.'_qty']*$cses['items_'.$i.'_price'];
			}
			++$cses['products_in_basket'];
		}
	}
	$cses['total_i']=$total_i;
	
	//Calcula descuentos
	if($cses['coupon_used']!='' and $usr['type']!='Membership' and (!isset($cfg['promo_campaign']) or $cfg['promo_campaign']==0))
	{
	 	for ($i=1; $i <= $cses['items_in_basket']; $i++)
		{
			if ($cses['items_'.$i.'_qty'] > 0 and $cses['items_'.$i.'_id'] > 0)
			{
				if($cses['total_i']>=$cses['coupon_minimum_external'])
					$cses['items_'.$i.'_discount']=$cses['items_discounts']/$cses['products_in_basket'];
				else
					$cses['items_'.$i.'_discount']=0;
				//Calcula taxes
				$cses['items_'.$i.'_tax']=($cses['items_'.$i.'_price']-$cses['items_'.$i.'_discount'])*$cses['items_'.$i.'_qty']*$cses['tax_total'];
			}
		}
		if($cses['total_i']< $cses['coupon_minimum_external'])
		{
			$va['message']	=	trans_txt('error_coupon');
			$cses['items_discounts']=0;
		}
		else
		{
			$in['coupon']=$cses['coupon_used'];
			//echo check_coupon();
		}
	}
	
	//Se Verifica reward_points
	if($cses['reward_points_used']!='' and $usr['type']!='Membership' and (!isset($cfg['promo_campaign']) or $cfg['promo_campaign']==0))
	{
	 	if($cses['total_i']< $cses['reward_points_minimum_external'])
		{
			$va['message']	=	trans_txt('error_reward_points');
		}
		else
		{
			$in['id_products']=$cses['reward_points_used'];
		}
	}
	
	//Calcular total_order
	$cses['total_order']=$cses['total_i']-$cses['items_discounts']+$cses['shipping_total']+($cses['total_i']-$cses['items_discounts'])*$cses['tax_total'];
}

function calculate_taxes($zip,$state) {
// --------------------------------------------------------
# Last Time Modified by RB on 08/18/2011: Se agrega fecha actual y calculo de tax por City


	if ($state!='--' and $state!=''){
		$sthc= mysql_query("SELECT Tax FROM sl_taxstate WHERE State = '".mysql_real_escape_string($state)."' AND Status='Active' AND ToDate >= CURDATE() ORDER BY ToDate LIMIT 1;") or die("Query failed : " . mysql_error());
		$taxes += mysql_result($sthc,0) / 100;
	}
	
	if ($zip){
		$sthc=mysql_query("SELECT SUM(Tax) FROM sl_taxcounty,sl_zipcodes WHERE ZipCode='".mysql_real_escape_string($zip)."' AND sl_taxcounty.County=sl_zipcodes.CountyName AND sl_taxcounty.State='".mysql_real_escape_string($state)."' AND PrimaryRecord='P' AND FromDate<=CURDATE() AND ToDate>=CURDATE() AND Status='Active'") or die("Query failed : " . mysql_error());
		$taxes += mysql_result($sthc,0);

		if ($city){
		  $city=trim($city);
		  $city = str_replace('.','',$city);
		  $sthc = mysql_query("SELECT IF(SUM(Tax) IS NULL,0,SUM(Tax))AS TaxCity FROM sl_taxcity,sl_zipcodes WHERE ZipCode='$zip' AND sl_taxcity.County=sl_zipcodes.CountyName AND sl_taxcity.State='$state' AND PrimaryRecord='P' AND FromDate <= CURDATE() AND ToDate >= CURDATE() AND Status='Active' AND UPPER(sl_taxcity.City) = UPPER('$city') AND (UPPER(CityAliasAbbreviation) = UPPER(sl_taxcity.City) OR UPPER(sl_zipcodes.City) = UPPER(sl_taxcity.City) OR UPPER(CityAliasName) = UPPER(sl_taxcity.City));");
		  $taxes += mysql_result($sthc,0);
		}

	}
	return $taxes;
}


function link_thisuser_anotheruser($returndata=0){
 global $usr,$cfg;
 
 #
 $output='';
 
 if(isset($_COOKIE['ishop_buyemail']) or $usr['email']){
     #print_r($usr);
     ($usr['email'])  ? $user_email = $usr['email'] : $user_email = $_COOKIE['ishop_buyemail'];
     #$output .= trans_txt('notuser').' <strong>'.substr($user_email,0,10).'</strong>?<a href="" onClick="deleteBuyCookie(-1);return false;" class="m1_text"> '.trans_txt('clickhere').'</a>'."\n";
     $output .= '<a href="" onClick="deleteBuyCookie(-1);return false;" class="mc">Cambiar Usuario</a>';

 }
 
  if($returndata==1)
	    return $output;
	else
	    echo $output;
}


function link_signin_customer($cmd='',$returndata=0){
 global $usr,$cfg;
 
 $output= $cmd;
 
 if($usr['id_customers'] > 0){
         $output = "index.php?cmd=home";
 }
 
  if($returndata==1)
	    return $output;
	else
	    echo $output;
}

function link_step($step=1){
 global $usr,$cfg;
 
 	if($usr['id_customers'] > 0){
         $step=2;
 }
 	return $step;
}

function build_tracking_link($Tracking,$ShpProvider,$ShpDate,$id_orders_products,$invoice=0,$returnData=0) {
# --------------------------------------------------------

# Author: Unknown
# Created on:  Unknown
# Description : More info was added to show stock, po and po notes
# Forms Involved: 
# Parameters :
# Last Modified RB: 10/14/08  16:21:15 void if call comes from returns 
# Last Modified RB: 10/27/08  15:38:36 Added Fedex Link
# Last Modified RB: 01/07/09  12:04:08 remove "<td>" in $link
# Last Modified on: 07/09/09 11:00:00
# Last Modified by: MCC C. Gabriel Varela S: Se agrega compatibilidad con IW

	$output="";
	
	    
    if (!$Tracking or !$ShpProvider or $ShpDate == '0000-00-00'){
        ## Search the Parts Tracking
        $sth = mysql_query("SELECT DISTINCT ShpDate,Tracking,ShpProvider FROM sl_orders_parts WHERE ID_orders_products = $id_orders_products ORDER BY ShpDate DESC;");
        
        if(mysql_num_rows($sth) > 0){
            while(list($shpdate,$track,$shpprov) = mysql_fetch_row($sth)){
                $Date[]      =   $shpDate;
                $Track[]     =   $track;
                $Provider[]  =   $shpprov;
            }
        }
    }
    
    if(!isset($Date)){
        $Date[]      =   $ShpDate;
        $Track[]     =   $Tracking;
        $Provider[]  =   $ShpProvider;
    }
    
    
    $i=0;
    foreach($Provider as $ShpProvider){
        $link="";
        if($i > 0)
            $output .= "<br>";
    
        if(!$invoice){
        
            if($ShpProvider == 'UPS'){
              $link .= '<a href="http://wwwapps.ups.com/tracking/tracking.cgi?tracknum='.$Track[$i].'" target="_blank" title="UPS" class="idno">'.$Track[$i].'</a>';
            }elseif($ShpProvider == 'FEDEX'){
              $link = '<a href="http://www.fedex.com/Tracking?ascend_header=1&clienttype=dotcom&cntry_code=us&language=english&tracknumbers='.$Track[$i].'" target="_blank" title="Fedex" class="idno">'.$Track[$i].'</a>';
            }elseif ($ShpProvider == 'USPS'){						
              $link .= '<a href="http://trkcnfrm1.smi.usps.com/PTSInternetWeb/InterLabelInquiry.do?strOrigTrackNum='.$Track[$i].'" target="_blank" title="USPS" class="idno">'.$Track[$i].'</a>';
            }elseif ($ShpProvider == 'DHL Ground' or $ShpProvider == 'DHL'){						
              $link .= '<a href="http://track.dhl-usa.com/TrackByNbr.asp?nav=Tracknbr&txtTrackNbrs='.$Track[$i].'" target="_blank" title="DHL" class="idno">'.$Track[$i].'</a>';
            }elseif ($ShpProvider == 'Fedex'){						
              $link .= '<a href="http://www.fedex.com/Tracking?ascend_header=1&clienttype=dotcomreg&cntry_code=us_espanol&language=espanol&tracknumbers='.$Track[$i].'" target="_blank" title="Fedex" class="idno">'.$Track[$i].'</a>';
            }elseif ($ShpProvider == 'IW'){						
              $link .= '<a href="http://www.islandwide.com/TrackResult.asp?num='.$Track[$i].'" target="_blank" title="Islan Wide" class="idno">'.$Track[$i].'</a>';
            }
        }
        $output .= "$ShpDate &nbsp;$link";
      
        $i++;
    }
	
	if($returnData == 1)
	    return $output;
	else
	    echo $output;
}

function build_select_state() {
# --------------------------------------------------------
	return build_select_from_enum('State','sl_orders');
#	$output='';
#	$fields = load_enum_toarray('State','sl_orders');
#	foreach($fields as $field) {
#		$output .= "<option value='$field'>$field</option>\n";
#	}
#	return $output;
}

function build_radio_atime() {
# --------------------------------------------------------
	return build_radio_from_enum('atime','sl_customers');
}

function build_select_from_enum($column,$tbl_name){
# --------------------------------------------------------

	$data='';
	$output='';

	$fields = load_enum_toarray($tbl_name,$column);
	if (count($fields) == 0) {
		$db_select_fields{$column} = &trans_txt('none');
		return $output;
	}
	
	foreach($fields as $field) {
		$output .= "<option value='$field'>$field</option>\n";
	}
	return $output;
}

function build_checkbox_from_enum($column,$tbl_name) {
# --------------------------------------------------------
	$data='';
	$output='';

	$fields = load_enum_toarray($tbl_name,$column);
	if (count($fields) == 0) {
		$db_select_fields{$column} = &trans_txt('none');
		return $output;
	}

	foreach($fields as $field) {
		$output .= "<span style='white-space:nowrap'><input type='checkbox' name='$column' value='$field' class='checkbox'> $field </span>\n";
	}

	return $output;
}

function  build_radio_from_enum($column,$tbl_name) {
# --------------------------------------------------------
	$data='';
	$output='';

	$fields = load_enum_toarray($tbl_name,$column);
	if (count($fields) == 0) {
		$db_select_fields{$column} = &trans_txt('none');
		return $output;
	}

	foreach($fields as $field) {
		$output .= "<span style='white-space:nowrap'><input type='radio' name='$column' value='$fields' class='radio'> $field </span>\n";
	}

	return $output;
}

function load_enum_toarray($tbl_name,$col_name) {
# --------------------------------------------------------
	$ary='';
	$matches=array();
	$fields=array();
	$data='';
	
	###### Load Table Properties
	$sth = mysql_query("describe $tbl_name $col_name;");

	while ($ary = mysql_fetch_array($sth) ){
		$ary[0] = strtolower($ary[0]);
		$pattern= "/enum\((.*)/";
		#echo $ary[1];
		if (preg_match($pattern,$ary[1],$matches)){
			$data = $matches[1];
			$data = str_replace("'","",$data);
			$data = substr($data,0,-1);
		}
	}
	$fields = explode(",",$data);
	return $fields;
}

function start_login($login_user,$login_password){
# --------------------------------------------------------
# Forms Involved: 
# Created on: 01/07/10 16:38:23
# Author: MCC C. Gabriel Varela S.
# Description :   
# Parameters :
//Last modified on 20 Dec 2010 11:46:55
//Last modified by: MCC C. Gabriel Varela S. : Se cambia para también evaluar sha1
//Last modified on 2 Mar 2011 18:52:29
//Last modified by: MCC C. Gabriel Varela S. :Se integra cumpleaños
//Last modified on 3/21/11 1:34 PM
//Last modified by: MCC C. Gabriel Varela S. :Se modifica también para combo
//Last modified on 04/13/11 04:57:58 PM
//Last modified by: MCC C. Gabriel Varela S. : Se corrige query para contemplar sólo los que tienen password
//Last modified on 12 May 2011 11:01:50
//Last modified by: MCC C. Gabriel Varela S. :Se hace que setcookie aplique a raíz
//Last modified on 13 Jul 2011 12:05:52
//Last modified by: MCC C. Gabriel Varela S. :It register failed logins

  global $usr,$in,$ck_name,$sid,$cses;

  $valid=-1;
  $login_user = strtolower($login_user);
//   echo "SELECT *,date_format(birthday,'%m')as birthday_month,day(birthday)as birthday_day FROM sl_customers WHERE Email='".mysql_real_escape_string($login_user)."' AND Status='Active'<br>";
  $result = mysql_query("SELECT *,
  date_format(birthday,'%m')as birthday_month,
  day(birthday)as birthday_day 
  FROM sl_customers 
  WHERE Email='".mysql_real_escape_string($login_user)."' 
  AND Status='Active'
  and not isnull(password) 
  and password!=''" );
  $rec = mysql_fetch_assoc($result);
  #echo crypt($login_password,substr(crypt($login_password,'ns'),3,7));
  if ((strlen($rec['Password'])==13 and $rec['Password'] == crypt($login_password,substr(crypt($login_password,'ns'),3,7)))or(strlen($rec['Password'])==40 and $rec['Password'] == sha1($login_password)))
  {
  	$cses['type']=$rec[Type];
	  foreach ($rec as $key=>$value){
		  $usr[strtolower($key)] = $value;
	  }
	  
// 	  if(isset($usr['birthday'])and $usr['birthday']!='' and $usr['birthday']!='0000-00-00')
// 	  {
// 		  if(preg_match("/^(\d{4})\-(\d{2})\-(\d{2})$/",$usr['birthday'],$birthday))
// 			{
// 				$usr['birthday']=$birthday[2].'-'.$birthday[3].'-'.$birthday[1];
// 			}
// 	  }

	  srand(time());
	  $sid = $usr[id_customers].'-'.(intval(rand(1,100000))) .  time() . (intval(rand(1,1000000000)));
	  $sid .= sid_dv($sid);

	  setcookie($ck_name, $sid,0,'/');
   
	  ### Update User Info
	  if ($in[pref_language]){
		  $usr['pref_language'] = $in[pref_language];
		  setcookie('nslang', $in[pref_language],0,'/');
		  # $result = mysql_query("UPDATE admin_users SET LastLogin=NOW(),LastIP='$ip',pref_language='$in[pref_language]' WHERE ID_admin_users='$usr[id_admin_users]'");
	  }else{
		  # $result = mysql_query("UPDATE admin_users SET LastLogin=NOW(),LastIP='$ip' WHERE ID_admin_users='$usr[id_admin_users]'");
	  }

	  (!$usr['maxhits']) and ($usr['maxhits'] = 20);
	  (!$usr['pref_language'])  and ($usr['pref_lang']  = $cfg['default_lang']);

	  #save_logs('login','');
	  $in{'cmd'}  = 'home';
	  save_auth_data($sid);
    
	  $valid = "ok";
  }
  if($valid!='ok')
  {
	  auth_logging("innovashop_invalid_login",mysql_real_escape_string($login_user));
  }
  #echo $rec[Password]."=".crypt($login_password,substr(crypt($login_password,'ns'),3,7)) . ":: $valid";
  save_callsession();
  return $valid;
}

function get_tries($id_orders){
# --------------------------------------------------------
# Forms Involved: 
# Created on: 10/15/09 18:35:43
# Author: MCC C. Gabriel Varela S.
# Description :   
# Parameters :
	if(!$id_orders)
		return 0;
	$sth = mysql_query("Select count(*) from sl_orders_plogs where ID_orders=$id_orders") or die("Query failed get_tries: " . mysql_error());
	$to_return=mysql_result($sth,0);
	if(!$to_return)
		return 0;
	return $to_return;
}

function create_order(){
	// --------------------------------------------------------
	// Forms Involved: 
	// Created on: 09/18/09 16:05:01
	// Author: MCC C. Gabriel Varela S.
	// Description :   
	// Parameters :
	
	global $cfg,$cses;
	//global $id_orders,$id_customers;
	//Revisi?n de par?metros necesarios.
	if($cses['paytype']=='Credit-Card')
		$req_cols=array('firstname','lastname1','phone1','email','address1','city','state','zip','pmtfield1','pmtfield3','pmtfield4','pmtfield5','paytype');
	else if($cses['paytype']=='COD')
		$req_cols=array('firstname','lastname1','phone1','email','address1','city','state','zip','paytype');
	else if($cses['paytype']=='paypal' or $cses['paytype']=='google-checkout')
		$req_cols=array('firstname','lastname1','email','address1','city','state','zip','paytype');
	
	
	for ($i = 0; $i < count($req_cols); $i++)
	{
		$col = $req_cols[$i];
		$val = trim($cses[strtolower($col)]);
		if (!$val or $val=='')
			return ":Missing fields: $col";
	}
	//$shptype=get_promo_value()+1;
	if($cses['paytype']=="COD")
		$shptype=3;
	
	// iniciamos ptype
	$ptype = $cses['paytype'];
	
	//2 Se selecciona la base
	mysql_select_db($cfg['dbi_db']) or die("Select DB: ".mysql_error());
	if($cses['id_orders'] and $cses['id_customers'] > 0)
	{
		$id_customers=$cses['id_customers'];
		$sth = mysql_query("Delete from sl_orders_payments where ID_orders=".$cses['id_orders']) or die("Query failed : " . mysql_error());
		//6 Inserta payment
//		if($cses[payments] > 1){
//			$sprice=0;
//			for ($i=1;$i<=$cses[items_in_basket];$i++)
//				if ($cses['items_'.$i.'_qty']>0  and $cses['items_'.$i.'_id']>0)
//					$sprice+=$cses['items_'.$i.'_price']; 
//
//			$shptax=$cses[total_order] - round($sprice,3)+round($sprice/$cses[payments],3);
//			$amount	=	round($sprice/$cses[payments],3);
//			
//			$payments=$cses[payments];
//			while($payments > 0){
//				
//				if($payments ==	1)	$amount	=	$shptax;
//				
//				$id_orders_payments=create_payment($payments,$amount);	
//				if(!is_numeric($id_orders_payments))
//					return $id_orders_payments;	
//				$payments--;	
//			} 
//		}else{
//			$id_orders_payments=create_payment(1,$cses[total_order]);	
//			if(!is_numeric($id_orders_payments))
//				return $id_orders_payments;
//		}

			// Iserta pago basado en $cses[fppayments]
			$id_orders_payments=create_payment(1,$cses['total_order']);	
			if(!is_numeric($id_orders_payments)){
				return $id_orders_payments;
			}

	}
	else
	{
		//3 Inserta cliente
// 		if(isset($cses['id_customers']) and is_numeric($cses['id_customers'])){
// 			$id_customers=$cses['id_customers'];
// 		}else{

			$id_customers=create_customer();
// 		}

		$cses['id_customers']=$id_customers;
		if(!is_numeric($id_customers))
			return $id_customers;

		($cses['paytype'] == 'paypal' or $cses['paytype'] == 'google-checkout') and ($ptype = 'Credit-Card'); 
		$insert = "INSERT INTO sl_orders set ID_customers='$id_customers',Address1='".mysql_real_escape_string($cses['address1'])."',Address2='".mysql_real_escape_string($cses['address2'])."',Address3='".mysql_real_escape_string($cses['address3'])."',Urbanization='".mysql_real_escape_string($cses['urbanization'])."',City='".mysql_real_escape_string($cses['city'])."',State='".mysql_real_escape_string($cses['state'])."',Zip='".mysql_real_escape_string($cses['zip'])."',shp_type='$cses[shp_type]',shp_name='".mysql_real_escape_string($cses['firstname'])." ".mysql_real_escape_string($cses['lastname1'])."',shp_Address1='".mysql_real_escape_string($cses['address1'])."',shp_Address2='".mysql_real_escape_string($cses['address2'])."',shp_Address3='".mysql_real_escape_string($cses['address3'])."',shp_Urbanization='".mysql_real_escape_string($cses['urbanization'])."',shp_City='".mysql_real_escape_string($cses['city'])."',shp_State='".mysql_real_escape_string($cses['state'])."',shp_Zip='".mysql_real_escape_string($cses['zip'])."',Country='".mysql_real_escape_string($cses['country'])."',shp_Country='".mysql_real_escape_string($cses['country'])."',OrderQty=1,OrderShp='$cses[shipping_total]',OrderDisc=0,OrderTax='$cses[tax_total]',OrderNet=0,ID_salesorigins=6,DIDS7='$cfg[dids7]',Ptype='$ptype',StatusPrd='None',StatusPay='None',Status='$cfg[order_status]',Date=CURDATE(),Time=CURTIME(),ID_admin_users='$cfg[id_admin_users]'";
		mysql_query($insert) or die("Query failed : " . mysql_error());
		$cses[id_orders]=mysql_insert_id();
		set_data_profiler($cfg['prof_idorder'], $cses['id_orders']);
		//5 Inserta producto
		$id_orders_products=create_product();
		if(!is_numeric($id_orders_products))
			return $id_orders_products;
		

		//6 Inserta payment
//		if($cses[payments] > 1){
//			$sprice=0;
//			for ($i=1;$i<=$cses[items_in_basket];$i++)
//				if ($cses['items_'.$i.'_qty']>0  and $cses['items_'.$i.'_id']>0)
//					$sprice+=$cses['items_'.$i.'_price'];
//					
//			$shptax=$cses[total_order] - round($sprice,3)+round($sprice/$cses[payments],3);
//			$amount	=	round($sprice/$cses[payments],3);
//			
//			$payments=$cses[payments];
//			
//			while($payments > 0){
//				
//				if($payments ==	1)	$amount	=	$shptax;
//				
//				$id_orders_payments=create_payment($payments,$amount);	
//				if(!is_numeric($id_orders_payments))
//					return $id_orders_payments;	
//				$payments--;	
//			}
//		}else{
//			$id_orders_payments=create_payment(1,$cses[total_order]);	
//			if(!is_numeric($id_orders_payments))
//				return $id_orders_payments;
//		}

			// Iserta pago basado en $cses[fppayments]
			$id_orders_payments=create_payment(1,$cses['total_order']);	
			if(!is_numeric($id_orders_payments)){
				return $id_orders_payments;
			}
	}
	//Hacer Recalc aqu?
	recalc_totals($cses['id_orders'],$cses['zip'],$cses['state']);
	//7 Intenta hacer cobro
	if($cses['paytype']=='Credit-Card'){
		$status_payment=make_payment_auth($cses['id_orders'],$id_orders_payments,$cfg['enterprise']);
	}elseif($cses['paytype']=='paypal'){
		require_once('cmd_paypal_confirmation_step3.php');
		$status_payment = $resArray;
	}
//	elseif($cses['paytype']=='google-checkout'){
//		require_once('cmd_paypal_confirmation_step3.php');
//		$status_payment = $resArray;
//	}
	
	if($cses['paytype']=='Credit-Card')
	{
			if(count($status_payment) > 0 and $status_payment[0] != ''){
					foreach ($status_payment as $line_num => $line) {
	    				$return.= $line;
					}
			}else{
					$return .= "APIFailed";
			}
	}elseif($cses['paytype']=='paypal')
	{
		if(count($status_payment) > 0 and array_key_exists('ACK',$status_payment)){
			foreach ($status_payment as $line_num => $line) {
	    			$return.= $line;
			}
		}else{
			$return .= "PaypalFailed";
		}
	
	}else{
		$return .="OK";
	}
	
	return $return;
}

function getamount($id_orders){
	# --------------------------------------------------------
	# Forms Involved: 
	# Created on: 10/14/09 14:37:15
	# Author: MCC C. Gabriel Varela S.
	# Description :   
	# Parameters :
	global $in;

		$sth = mysql_query("SELECT (Sum(if(ID_products not like '6%' and sl_orders_products.Status!='Inactive',if(not isnull(SalePrice),SalePrice,0)-if(not isnull(Discount),Discount,0)+if(not isnull(Tax),Tax,0)+if(not isnull(Shipping),Shipping,0),0)))+Sum(if(ID_products like '6%' and sl_orders_products.Status!='Inactive',SalePrice,0))-if(not isnull(Sumpay),Sumpay,0) as Diff
FROM sl_orders_products
left join (select ID_orders,sum(amount)as SumPay 
           from sl_orders_payments 
           where ID_orders=$id_orders
           and Status not in ('Cancelled','Void','Order Cancelled') 
           group by ID_orders)as tempo on (tempo.ID_orders=sl_orders_products.ID_orders)
where sl_orders_products.ID_orders=$id_orders
GROUP BY sl_orders_products.ID_orders") or die("Query failed : " . mysql_error());
		return mysql_result($sth,0);
	}
	
	function getpayments($product_id){
# --------------------------------------------------------
# Forms Involved: 
# Created on: 10/13/09 17:38:32
# Author: MCC C. Gabriel Varela S.
# Description :   
# Parameters :
	global $in,$id_products,$products_payments;
	$i=0;
	
	$i=1;
	foreach ($in as $key=>$value )
	{
		if($key==sprintf("id_products%02d",$i) )
		{
			if($in[$key]  == $id_products[$in['e']]['promocion']&& $value==$product_id and get_promo_value()==1)
				return $products_payments[$in['e']]['promocion'];
			$i++;
		}
	}
		
	$i=0;
	foreach($id_products[$in['e']][$in['promo_name']] as $value)
	{
		if($value==$product_id)
			if($cses[paytype]=='COD')
				return 1;
			else
				return $products_payments[$in['e']][$in['promo_name']][$i];
		$i++;
	}
	return -1;
}

	function create_payment($payments,$amount){
// --------------------------------------------------------
// Forms Involved: 
// Created on: 09/24/09 15:25:19
// Author: MCC C. Gabriel Varela S.
// Description :   
// Parameters :
		global $cses,$cfg;
		if($cses['paytype']=='Credit-Card')
			$req_cols=array('id_orders','firstname','lastname1','phone1','pmtfield1','pmtfield3','pmtfield4','pmtfield5','paytype');
		else if($cses['paytype']=='COD')
			$req_cols=array('id_orders','firstname','lastname1','phone1','paytype');
		else if($cses['paytype']=='paypal' or $cses['paytype']=='google-checkout')
			$req_cols=array('id_orders','firstname','lastname1','paytype');	
		
		$id_payment = "General Error";
		
		#if($amount=='')
		#	return "Missing fields: amount=$amount";
		for ($i = 0; $i < count($req_cols); $i++)
		{
			$col = $req_cols[$i];
			$val = trim($cses[strtolower($col)]);
			if (!$val)
				return "Missing fields: $col";
		}

		if(isset($cses['fppayments']) and $cses['fppayments'] >= 1){
		
				for($i=1; $i <= $cses['fppayments'];$i++){
			
						$amount  = $cses['fppayment'.$i];
						$paydate = $cses['fpdate'.$i];
						
						if($amount=='' or $amount <= 0){
							return "Missing fields: amount=$amount";
						}
						
						($paydate=='') and ($paydate = "DATE_ADD(CURDATE(),INTERVAL ".$payments."-1 MONTH)");
			
						if($cses['paytype']=='Credit-Card'){
							$insert = "INSERT INTO sl_orders_payments set ID_orders='".mysql_real_escape_string(intval($cses['id_orders']))."',Type='Credit-Card',Pmtfield1='".mysql_real_escape_string($cses['pmtfield1'])."',Pmtfield2='".mysql_real_escape_string($cses['pmtfield2'])." ".mysql_real_escape_string($cses['lastname1'])."',Pmtfield3='".mysql_real_escape_string($cses['pmtfield3'])."',Pmtfield4='".mysql_real_escape_string($cses['expmm']).substr(mysql_real_escape_string($cses['expyy']),-2)."',Pmtfield5='".mysql_real_escape_string($cses['pmtfield5'])."',Pmtfield6='".mysql_real_escape_string($in['phone1'])."',Pmtfield7='".mysql_real_escape_string($cses['pmtfield7'])."',Amount='".mysql_real_escape_string(floatval($amount))."',Reason='Sale',PaymentDate='$paydate',Status='Approved',Date=Curdate(),Time=CURTIME(),ID_admin_users='$cfg[id_admin_users]'";
						}elseif($cses['paytype']=='COD'){
							$insert = "INSERT INTO sl_orders_payments set ID_orders='".mysql_real_escape_string(intval($cses['id_orders']))."',Type='COD',Amount='".mysql_real_escape_string(floatval($amount))."',Reason='Sale',PaymentDate='$paydate',Status='Approved',Date=Curdate(),Time=CURTIME(),ID_admin_users='$cfg[id_admin_users]'";
						}elseif($cses['paytype']=='paypal'){
							$insert = "INSERT INTO sl_orders_payments set ID_orders='".mysql_real_escape_string(intval($cses['id_orders']))."',Type='Credit-Card',Pmtfield1='Visa', PmtField2='".mysql_real_escape_string($cses['firstname'])." ".mysql_real_escape_string($cses['lastname1'])."',Pmtfield3='PayPal',Amount='".mysql_real_escape_string(floatval($amount))."',Reason='Sale',PaymentDate='$paydate',Status='Approved',Date=Curdate(),Time=CURTIME(),ID_admin_users='$cfg[id_admin_users]'";
						}elseif($cses['paytype']=='google-checkout'){
							$insert = "INSERT INTO sl_orders_payments set ID_orders='".mysql_real_escape_string(intval($cses['id_orders']))."',Type='Credit-Card',Pmtfield1='Visa', PmtField2='".mysql_real_escape_string($cses['firstname'])." ".mysql_real_escape_string($cses['lastname1'])."',Pmtfield3='Google-checkout',Amount='".mysql_real_escape_string(floatval($amount))."',Reason='Sale',PaymentDate='$paydate',Status='Approved',Date=Curdate(),Time=CURTIME(),ID_admin_users='$cfg[id_admin_users]'";
						}elseif($cses['paytype']=='descuentolibre'){
							$insert = "INSERT INTO sl_orders_payments set ID_orders='".mysql_real_escape_string(intval($cses['id_orders']))."',Type='Credit-Card',Pmtfield1='Visa', PmtField2='".mysql_real_escape_string($cses['firstname'])." ".mysql_real_escape_string($cses['lastname1'])."',Pmtfield3='Descuentolibre',Amount='".mysql_real_escape_string(floatval($amount))."',Reason='Sale',PaymentDate='$paydate',Status='Approved', Captured='Yes', CapDate=Curdate(), Date=Curdate(),Time=CURTIME(),ID_admin_users='$cfg[id_admin_users]'";
						}
						mysql_query($insert) or die("Query failedb : " . mysql_error());
						$id_payment = mysql_insert_id();
				}
		
		}elseif($cses['paytype']=='COD' and $amount > 0){
			$insert = "INSERT INTO sl_orders_payments set ID_orders='".mysql_real_escape_string(intval($cses['id_orders']))."',Type='COD',Amount='".mysql_real_escape_string(floatval($amount))."',Reason='Sale',PaymentDate=DATE_ADD(CURDATE(),INTERVAL ".$payments."-1 MONTH),Status='Approved',Date=Curdate(),Time=CURTIME(),ID_admin_users='$cfg[id_admin_users]'";
			mysql_query($insert) or die("Queryc failed : " . mysql_error());
			$id_payment = mysql_insert_id();
		}elseif($cses['paytype']=='paypal' and $amount > 0){
			$insert = "INSERT INTO sl_orders_payments set ID_orders='".mysql_real_escape_string(intval($cses['id_orders']))."',Type='Credit-Card',Pmtfield1='Visa', PmtField2='".mysql_real_escape_string($cses['firstname'])." ".mysql_real_escape_string($cses['lastname1'])."',Pmtfield3='PayPal',Amount='".mysql_real_escape_string(floatval($amount))."',Reason='Sale',PaymentDate='$paydate',Status='Approved',Date=Curdate(),Time=CURTIME(),ID_admin_users='$cfg[id_admin_users]'";
			mysql_query($insert) or die("Queryd failed : " . mysql_error());
			$id_payment = mysql_insert_id();
		}elseif($cses['paytype']=='google-checkout'){
			$insert = "INSERT INTO sl_orders_payments set ID_orders='".mysql_real_escape_string(intval($cses['id_orders']))."',Type='Credit-Card',Pmtfield1='Visa', PmtField2='".mysql_real_escape_string($cses['firstname'])." ".mysql_real_escape_string($cses['lastname1'])."',Pmtfield3='Google-checkout',Amount='".mysql_real_escape_string(floatval($amount))."',Reason='Sale',PaymentDate='$paydate',Status='Approved',Date=Curdate(),Time=CURTIME(),ID_admin_users='$cfg[id_admin_users]'";
			mysql_query($insert) or die("Querye failed : " . mysql_error());
			$id_payment = mysql_insert_id();
		}elseif($amount=='' or $amount <= 0){
			return "Missing fields: amount=$amount";
		}
		
		return $id_payment;
	}
	
function create_customer(){
// --------------------------------------------------------
// Forms Involved: 
// Created on: 09/24/09 15:25:19
// Author: MCC C. Gabriel Varela S.
// Description :   
// Parameters :

//Pendiente, ver la posibilidad de regresar el ID de un cliente si ya existe
//Last modified on 2 Mar 2011 16:06:13
//Last modified by: MCC C. Gabriel Varela S. :Se incluye birthday
//Last modified on 1 Jun 2011 17:01:10
//Last modified by: MCC C. Gabriel Varela S. :a \n is included after each field on the insertion of the changes in customer information

	global $cfg,$cses,$in,$error;
	#Revision de parametros necesarios.

// MOD OSANCHEZ
//	$req_cols=array('firstname','lastname1','phone1','email','address1','city','state','zip');
	$req_cols=array('firstname','lastname1','phone1','address1','city','state','zip');
	($cses['paytype'] == 'paypal') and ($req_cols=array('firstname','lastname1','email','address1','city','state','zip'));
	for ($i = 0; $i < count($req_cols); $i++)
	{
		$col = $req_cols[$i];
		$val = trim($cses[strtolower($col)]);
		if (!$val){
			return trans_txt('missing_fields') . ": $col";
		}
	}

	if(!isset($cses['country'])){
	    $cses['country'] = 'UNITED STATES';
	}
	
	$search_customer = mysql_query("SELECT COUNT(*) FROM sl_customers WHERE Email = '".mysql_real_escape_string($cses['email'])."' AND (FirstName = '".mysql_real_escape_string($cses['firstname'])."' AND LastName1 = '".mysql_real_escape_string($cses['lastname1'])."' AND Address1 = '".mysql_real_escape_string($cses['address1'])."' ) ");
	if($search_customer and mysql_result($search_customer,0) > 0){
		$old_customer = mysql_query("SELECT ID_customers FROM sl_customers WHERE Email = '".mysql_real_escape_string($cses['email'])."' AND (FirstName = '".mysql_real_escape_string($cses['firstname'])."' AND LastName1 = '".mysql_real_escape_string($cses['lastname1'])."' AND Address1 = '".mysql_real_escape_string($cses['address1'])."' ) ");	
		$id_customers = mysql_result($old_customer,0);

		## Actualizamos los datos del cliente
		
		$birthday_to_insert='2011-'.$cses['birthday_month'].'-'.$cses['birthday_day'];
// 		if(isset($cses['birthday'])and $cses['birthday']!='')
// 		{
// 			if(preg_match("/^(\d{2})\-(\d{2})\-(\d{4})$/",$cses['birthday'],$birthday))
// 			{
// 				$birthday_to_insert=$birthday[3].'-'.$birthday[1].'-'.$birthday[2];
// 			}
// 		}
		
		$phone1 = str_replace(array("-","|"," "),array("","",""),$cses['phone1']);
		$insert = mysql_query("UPDATE sl_customers SET FirstName='".mysql_real_escape_string($cses['firstname'])."',LastName1='".mysql_real_escape_string($cses['lastname1'])."',LastName2='".mysql_real_escape_string($cses['lastname2'])."',Birthday='".mysql_real_escape_string($birthday_to_insert)."',Sex='".mysql_real_escape_string($cses['sex'])."',Phone1='".mysql_real_escape_string($phone1)."',Cellphone='".mysql_real_escape_string($cses['cellphone'])."',Email='".mysql_real_escape_string($cses['email'])."',Address1='".mysql_real_escape_string($cses['address1'])."',Address2='".mysql_real_escape_string($cses['address2'])."',Address3='".mysql_real_escape_string($cses['address3'])."',Urbanization='".mysql_real_escape_string($cses['urbanization'])."',City='".mysql_real_escape_string($cses['city'])."',State='".mysql_real_escape_string($cses['state'])."',Zip='".mysql_real_escape_string($cses['zip'])."',Country='".mysql_real_escape_string(($cses['country']))."',Status='Active' WHERE ID_customers = '$id_customers';");
		$insert = mysql_query("insert into sl_customers_notes SET ID_customers='$id_customers', Notes='Se actualizan datos del cliente: FirstName=".mysql_real_escape_string($cses['firstname']).",\nLastName1=".mysql_real_escape_string($cses['lastname1']).",\nLastName2=".mysql_real_escape_string($cses['lastname2']).",\nBirthday=".mysql_real_escape_string($birthday_to_insert).",\nSex=".mysql_real_escape_string($cses['sex']).",\nPhone1=".mysql_real_escape_string($phone1).",\nCellphone=".mysql_real_escape_string($cses['cellphone']).",\nEmail=".mysql_real_escape_string($cses['email']).",\nAddress1=".mysql_real_escape_string($cses['address1']).",\nAddress2=".mysql_real_escape_string($cses['address2']).",\nAddress3=".mysql_real_escape_string($cses['address3']).",\nUrbanization=".mysql_real_escape_string($cses['urbanization']).",\nCity=".mysql_real_escape_string($cses['city']).",\nState=".mysql_real_escape_string($cses['state']).",\nZip=".mysql_real_escape_string($cses['zip']).",\nCountry=".mysql_real_escape_string(($cses['country']))."',Type='Low',Date=curdate(),Time=curtime(),ID_admin_users='$cfg[id_admin_users]';") or die("Query failed : " . mysql_error());

		return $id_customers;
	}

	$cadmail = "";
	$cadmail = ", Email='".mysql_real_escape_string($cses['email'])."' ";
	if($cses['usertype']=='new'){
		$cses['new_customer']='checkout_newcustomer';		
	}
	
#	elseif($cses['usertype']=='registration'){
#	    $cadmail = ", Email='".mysql_real_escape_string($cses['email'])."' ";
#	}
	
	$birthday_to_insert='2011-'.$usr['birthday_month'].'-'.$usr['birthday_day'];
// 	if(isset($cses['birthday'])and $cses['birthday']!='')
// 	{
// 		if(preg_match("/^(\d{2})\-(\d{2})\-(\d{4})$/",$cses['birthday'],$birthday))
// 		{
// 			$birthday_to_insert=$birthday[3].'-'.$birthday[1].'-'.$birthday[2];
// 		}
// 	}
	
	$phone1 = str_replace(array("-","|"," "),array("","",""),$cses['phone1']);
	$insert = "INSERT INTO sl_customers SET FirstName='".mysql_real_escape_string($cses['firstname'])."',LastName1='".mysql_real_escape_string($cses['lastname1'])."',LastName2='".mysql_real_escape_string($cses['lastname2'])."',Birthday='".mysql_real_escape_string($birthday_to_insert)."',Sex='".mysql_real_escape_string($cses['sex'])."',Phone1='".mysql_real_escape_string($phone1)."',Cellphone='".mysql_real_escape_string($cses['cellphone'])."',Address1='".mysql_real_escape_string($cses['address1'])."',Address2='".mysql_real_escape_string($cses['address2'])."',Address3='".mysql_real_escape_string($cses['address3'])."',Urbanization='".mysql_real_escape_string($cses['urbanization'])."',City='".mysql_real_escape_string($cses['city'])."',State='".mysql_real_escape_string($cses['state'])."',Zip='".mysql_real_escape_string($cses['zip'])."',Country='".mysql_real_escape_string(($cses['country']))."',Status='Active',Type='Retail',Date=Curdate(),Time=CURTIME(),ID_admin_users='".$cfg['id_admin_users']."' $cadmail; ";
	mysql_query($insert) or die("Query failed : " . mysql_error());
	return mysql_insert_id();
}

function gen_passwd(){
# --------------------------------------------------------
# Form: validate_man_users in dbman.html.cgi
# Service: 
# Type : subroutine
# Time Last : 9/06/2007 4:34PM
# Author: Rafael Sobrino
# Description : generates a 6-character (upper/lower alpha + numeric) random password 

	$len      = 6;		# length of the random password
	$chars    = array();
	$password = '';
	$exclude  =  array('\\','[',']','^','`');
	$i=1;
	
	foreach(range('A','z') as $char){
			if(!in_array($char,$exclude)){
					array_push($chars,$char);
			}
	}
	foreach(range(0,9) as $char){
		array_push($chars,$char);
	}
	
	while($i <= $len){
		$password .= $chars[rand(0,count($chars))];
		$i++;
	}
	return $password;	
}


	function create_product(){
// --------------------------------------------------------
// Forms Involved: 
// Created on: 09/24/09 15:25:19
// Author: MCC C. Gabriel Varela S.
// Description :   
// Parameters :
// Last Time Modified by RB on 12/13/2010: Se agrega validacion de $cses['items_'.$i.'_fpprice']


	global $cses,$cfg;
	global $related_products;
	//Revision de parametros necesarios.
	$req_cols=array('id_orders');
	for ($i = 0; $i < count($req_cols); $i++)
	{
		$col = $req_cols[$i];
		$val = trim($cses[strtolower($col)]);
		if (!$val)
			return "Missing fields: $col";
	}

	for ($i=1;$i<=$cses['items_in_basket'];$i++)
	{
		if ($cses['items_'.$i.'_qty'] > 0  and $cses['items_'.$i.'_id'] > 0)
		{
			$insert='';
			($cses['items_'.$i.'_shp'.$cses['shp_type']] == '') and ($cses['items_'.$i.'_shp'.$cses['shp_type']]=0);
			($cses['items_'.$i.'_fpprice'] == '' or $cses['items_'.$i.'_fpprice'] < $cses['items_'.$i.'_price']) and ($cses['items_'.$i.'_fpprice'] = 0);
			$insert = "INSERT INTO sl_orders_products set ID_products='".mysql_real_escape_string($cses['items_'.$i.'_id'])."',ID_orders='".mysql_real_escape_string(intval($cses['id_orders']))."',Quantity='".$cses['items_'.$i.'_qty']."',SalePrice=IF(".$cses['items_'.$i.'_fpprice']." > 0,'".$cses['items_'.$i.'_fpprice']."','".$cses['items_'.$i.'_price']."'),Shipping='".$cses['items_'.$i.'_shp'.$cses['shp_type']]."',Cost=0,Tax='".$cses['items_'.$i.'_tax']."',Discount='".$cses['items_'.$i.'_discount']."',FP='".$cses['items_'.$i.'_payments']."',Status='Active',Date=CURDATE(),Time=CURTIME(),ID_admin_users='".$cfg['id_admin_users']."'";
			#echo $insert;
			mysql_query($insert) or die("Query failed : " . mysql_error());
			$id_orders_products=mysql_insert_id();
	    //Calcular Shp,Disc,Tax, etc. aqui
			calc_tax_disc_shp($id_orders_products,0,0);
			
			$id_services = 0;		
			$id_services = intval(load_name('sl_products','ID_products',substr($cses['items_'.$i.'_id'],-6),'ID_services_related'));
			if($id_services > 0){
					## Producto tiene servicio relacionado
					$insert2='';
					$price = 0;
					$price = &load_name ('sl_services','ID_services',$id_services,'SPrice');
					$id_services += 600000000;
					
					$insert2 = "INSERT INTO sl_orders_products set ID_products='$id_services',ID_orders='".mysql_real_escape_string(intval($cses['id_orders']))."',Quantity=1,Related_ID_products='".mysql_real_escape_string($cses['items_'.$i.'_id'])."',SalePrice='".$price."',Shipping=0,Cost=0,Tax=0,Discount=0,FP=1,Status='Active',Date=CURDATE(),Time=CURTIME(),ID_admin_users='".$cfg['id_admin_users']."'";
					mysql_query($insert2) or die("Query failed : " . mysql_error());
					#echo $insert2;
			}
		}
	}
	return $id_orders_products;
}

	function recalc_totals($idorders,$zip,$state){
	//Acci?n: Creaci?n
	//Comentarios:
	// --------------------------------------------------------
	// Forms Involved: 
	// Created on: 06/27/2008 07:41AM GMT -0600
	// Last Modified on: 06/27/2008
	// Last Modified by: 
	// Author: MCC C. Gabriel Varela S.
	// Description : Recalcula los totales de ?rdenes
	// Parameters :
	//							$idorder: ID de la orden
	// Last Modified on: 09/02/08 12:29:20
// Last Modified by: MCC C. Gabriel Varela S: Se hace que cuando el shipping sea 0, se deje como est?
// Last Modified on: 09/10/08 11:37:20
// Last Modified by: MCC C. Gabriel Varela S: Se hace que tambi?n se contemple el descuento
// Last Modified on: 03/13/09 09:44:08
// Last Modified by: MCC C. Gabriel Varela S: Se cambia condici?n a if ($rec->{'SalePrice'}!=0 or 1) porque no consideraba los casos que no tienen costo, pero s? shipping.
// Last Modified on: 03/17/09 16:21:59
// Last Modified by: MCC C. Gabriel Varela S: Se incluyen par?metros para sltv_itemshipping
//	delete($in{'orderqty'});
//	delete($in{'ordernet'});
//	delete($in{'ordershp'});
//	delete($in{'ordertax'});
//	delete($in{'orderdisc'});
	global $cses;
	$orderqty=0;$ordernet=0;$orderdisc=0;$ordershp=0;

	$sth = mysql_query("SELECT * FROM sl_orders_products WHERE ID_orders='".$idorders."' AND Status<>'Inactive';") or die("Query failed : " . mysql_error());
	while ($rec = mysql_fetch_assoc($sth)){
		$aa .= $rec['ID_products']." <br>";
		$orderqty += $rec['Quantity'];
		$ordernet += $rec['SalePrice'];
		$orderdisc += $rec['Discount'];
		if (preg_match("/^1/",$rec['ID_products'])){
			if ($rec['SalePrice']!=0 or 1){
				if ($rec['Status'] == 'Returned'){
					$ordershp += $rec['Shipping'];
				}elseif($rec['Shipping'] == ''){
//					($va{'shptotal1'},$va{'shptotal2'},$va{'shptotal3'},$va{'shptotal1pr'},$va{'shptotal2pr'},$va{'shptotal3pr'},$va{'shp_text1'},$va{'shp_text2'},$va{'shp_text3'},$va{'shp_textpr1'},$va{'shp_textpr2'},$va{'shp_textpr3'})= &sltv_itemshipping($prd['edt'],$prd['SizeW'],$prd['SizeH'],$prd['SizeL'],$prd['Weight'],$prd['ID_packingopts']);
//					$ordershp += $va{'shptotal'.$in['shp_type']};
				}else{
					$ordershp += $rec['Shipping'];
				}
			}
		}else{
			$ordershp += $rec['Shipping'];
		}
	}

	$ordertax = calculate_taxes(load_name("sl_orders","ID_orders",$idorders,'Zip'),load_name("sl_orders","ID_orders",$idorders,'State'));
	$sth= mysql_query("UPDATE sl_orders SET OrderQty='".$orderqty."',OrderShp='".$ordershp."',OrderTax='".$ordertax."',OrderNet='".$ordernet."',OrderDisc='".$orderdisc."' WHERE ID_orders='".$idorders."'") or die("Query failed : " . mysql_error());
	auth_logging("opr_orders_recalc",$idorders);
}

	function make_payment_auth($id_orders,$id_orders_payments,$e){
	// --------------------------------------------------------
	// Forms Involved: 
	// Created on: 09/17/09 15:26:19
	// Author: MCC C. Gabriel Varela S.
	// Description :   
	// Parameters :
		global $cfg;
    $status=@file("$cfg[url_paymentgateway]?id=$id_orders&idp=$id_orders_payments&cmd=sltvcyb_auth&idu=1&e=$e");
    #print "$cfg[url_paymentgateway]?id=$id_orders&idp=$id_orders_payments&cmd=sltvcyb_auth&idu=1&e=$e";
    
    $txt_status = implode("\n",$status);
    @mail("roberto.barcenas@gmail.com","Intento de Cobro Innovashop","$txt_status");
   
		return $status;
	}
	
	function calc_tax_disc_shp($id_orders_products,$shippingf,$discountf){
//	// --------------------------------------------------------
//	// Forms Involved: 
//	// Created on: 09/04/08 13:43:57
//	// Author: MCC C. Gabriel Varela S.
//	// Description : Calcula los valores para tax, discount y shp para un id_orders_products recibido. Basada en admin_rep_estabdisctaxshp de Y:\domains\dev.shoplatinotv.com\cgi-bin\administration\admin.reports.cgi
//	// Parameters :
//	// Last Modified on: 09/05/08 10:12:48
//	// Last Modified by: MCC C. Gabriel Varela S: Se toma en cuenta ahora tambi?n FP
//	// Last Modified on: 09/08/08 17:21:12
//	// Last Modified by: MCC C. Gabriel Varela S: 
//	// Last Modified on: 09/09/08 12:56:06
//	// Last Modified by: MCC C. Gabriel Varela S: Se actualiza la forma en que se calcular?n las cosas
//	// Last Modified on: 09/10/08 10:11:45
//	// Last Modified by: MCC C. Gabriel Varela S: Se actualiza la forma en que se calcular? o no el descuento
//	// Last Modified on: 09/15/08 11:59:22
//	// Last Modified by: MCC C. Gabriel Varela S: Se filtra para cuando no exista id de producto
//	// Last Modified on: 09/19/08 11:32:50
//	// Last Modified by: MCC C. Gabriel Varela S: Se cambia la forma de contar productos, los servicios no contar?n
//	// Last Modified on: 01/05/09 13:30:38
//	// Last Modified by: MCC C. Gabriel Varela S: Se cambia el criterio para determinar si est? bien establecido el tax
//	// Last Modified on: 03/17/09 10:18:11
//	// Last Modified by: MCC C. Gabriel Varela S: Par?metros para sltv_itemshipping
//	// Last Modified RB: 08/07/09  13:33:03 -- $discb se verifica que no sea una cadena vacia.
//	// Last Modified RB: 09/01/09  15:25:28 ShippingB,TaxB,DiscB. Cuando son iguales a "0" es un posible error y se recalcula el valor, de lo contrario se salta. $shippingf sirve para no calcular el shipping nuevamente
	
		global $cses;

		$sth=mysql_query("Select 
 sl_orders_products.ID_orders_products,
 sl_orders_products.ID_products,
 sl_products.edt,
 sl_products.SizeW,
 sl_products.SizeH,
 sl_products.SizeL,
 sl_products.flexipago,
 sl_products.Weight,
 sl_orders_products.ID_orders,
 sl_orders.shp_type,
 if((sl_orders_products.Discount=0 and sl_orders.OrderDisc!=0 and not isnull(OrderDisc)),0,1) as DiscB,
 if((sl_orders_products.Tax=0 and OrderTax!=0 and not isnull(OrderTax) and SalePrice!=0)or isnull(Tax),0,1) as TaxB,
 if(sl_orders_products.Shipping=0 and OrderShp!=0 and not isnull(OrderShp),0,1)as ShippingB, 
 Products, 
 OrderTax, 
 SalePrice, 
 OrderShp, 
 OrderDisc,
 sl_orders_products.Discount, 
 Tax,
 Shipping,
 Quantity 
from sl_orders_products 
inner join sl_orders on(sl_orders_products.ID_orders=sl_orders.ID_orders) 
inner join sl_products on (right(sl_orders_products.ID_products,6)=sl_products.ID_products) 
inner join(Select sl_orders_products.ID_orders, count(ID_orders_products) as Products
           from sl_orders_products 
           where id_products not like '6%' 
           group by sl_orders_products.ID_orders)as tempo on(tempo.ID_orders=sl_orders.ID_orders) 
where sl_orders_products.ID_products not like '6%' 
and sl_orders_products.ID_orders_products=$id_orders_products")or die("Query failed : " . mysql_error());
		$rec=mysql_fetch_assoc($sth);
		
		$discb=$rec['Discount'];
		$taxb=$rec['Tax'];
		$shippingb=$rec['Shipping'];
		if($rec['ID_products']!='')
		{
			//////////////////////////////////////////////////
			//Se establece el Shipping
			//////////////////////////////////////////////////
			if($rec['ShippingB']==0)
			{
//				if($rec['Products']==1)
//				{
//					$totshpord=$rec['OrderShp'];
//				}
//				else
//				{
					//Ser? fijo por configuraci?n.
					//$totshpord=getshipping($rec['ID_products']);
//				}
				$shippingb=$totshpord;
			}
			////////////////////////////////////////////////////
			//Se establece el Descuento
			////////////////////////////////////////////////////
			if($rec['DiscB']==0 and $discountf==1)
			{
//				Ser? fijo por configuraci?n
//				$fpago=&load_name('sl_products','ID_products',substr($rec['ID_products'],3,6),'flexipago');
//				$discb=($rec['SalePrice']*$cfg{'fpdiscount'.$fpago}/100);
			}
			
	
			////////////////////////////////////////
			//Se establece el Tax
			////////////////////////////////////////
			if($rec['TaxB']==0)
			{
				$taxb=$rec['OrderTax']*($rec['SalePrice']-$discb);
			}
			////////////////////////////////
			//Se establece FP
			////////////////////////////////
			$fpb=1;
			if($discb=='')
				$discb=0;
			if($taxb=='')
				$taxb=0;
			if($shippingb=='')
				$shippingb=0;
			if($shippingf)
				$shippingcad="Shipping='$shippingb',";
			mysql_query("update sl_orders_products set ".$shippingcad." Tax='".$taxb."', Discount='".$discb."', FP='".$fpb."' where ID_orders_products='".$rec["ID_orders_products"]."';") or die("Query failed : " . mysql_error());
		}
//		#return ($taxb,$discb,$shippingb);
	}

	function auth_logging($message,$action) {
// --------------------------------------------------------
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
	$value = "LogDate=Curdate(),LogTime=NOW(), ID_admin_users=1, tbl_name='".$in['db']."',Logcmd='".$in['cmd']."', Type='$type',Message='".mysql_real_escape_string($message)."', Action='".mysql_real_escape_string($action)."', IP=''";
	$sth = mysql_query("INSERT INTO admin_logs SET $value") or die("Query failed : " . mysql_error());
}
	
function sendFinalEmail($response){
#-----------------------------------------
# Created on: 11/10/09  11:20:25 By  Roberto Barcenas
# Forms Involved: 
# Description : Envia Email de Confirmacion de Compra al Usuario
# Parameters : 	

	global $cses,$cfg,$in,$va,$device;
	$va['pname']="";
	$va['paymentData']="";
	$va['paysummary']="";
	$in['filepage'] = "/cart/content/";

	for ($i=1;$i<=$cses['items_in_basket'];$i++)
		if ($cses['items_'.$i.'_qty']>0  and $cses['items_'.$i.'_id']>0)
		{
			$name=load_name('sl_products',"ID_products",substr($cses['items_'.$i.'_id'],3),"Name");
			$namep=load_name('sl_products_prior',"ID_products",substr($cses['items_'.$i.'_id'],3),"Name");
			if($namep!='')
				$name=$namep;
			$name=replace_in_string($name);
			$va['pname'] .= $name." x ".$cses['items_'.$i.'_qty']."<br>";
		}
	
	$va['tax_total']=calculate_taxes($cses['zip'],$cses['state']);
	$va["tax_total"]     = "(".($va['tax_total']*100)."%)";
	$va['paymentData'] = showPaymentData($cses['zip'],$cses['state']);
	$va['paysummary'] = paysummary(1);
	$va['cservice_phone'] = $cfg['cservice_phone'];
	$va['cservice_email'] = $cfg['cservice_email'];
	$va['ccardnum'] = str_pad(substr($cses['pmtfield3'], -4), strlen($cses['pmtfield3']), 'x', STR_PAD_LEFT);
	($cses['sex']=='Male')?	$va['sex']= trans_txt('male')	: $va['sex']= trans_txt('female');
	
	$cabeceras_sm  = 'MIME-Version: 1.0' . "\r\n";
	$cabeceras_sm .= 'Content-type: text/html; charset=utf-8' . "\r\n";
	$cabeceras_sm .= 'From: '.$cfg['app_title'].' <'.$cfg['cservice_email'].'>' . "\r\n";
	$asunto = trans_txt('shopping_info') . ' #'.$cses['id_orders'];
	$destinatarios="$cses[email]";

	if(strpos($response,"OK")=== false)
		$response.="<br>".trans_txt('order_void');
	
	$va['invoice_body'] = html_invoice($cses['id_orders'],0,1);
	$cuerpo_sendmail = build_page($in['filepage'] . 'checkout_mail.html');

	// S12 Mail
//	@mail($cfg['final_email_administrators'],$asunto,$cuerpo_sendmail,$cabeceras_sm);

	// Gmail Mail
	$cabeceras_sm = '';
	send_mail($destinatarios,$asunto,$cuerpo_sendmail,$cabeceras_sm);

	## Device Properties
	$this_device_info = print_r($device, TRUE);
	$cuerpo_sendmail .= '<br><br>Dispositivo del cliente:<br>' . $this_device_info;
	send_mail($cfg['final_email_administrators'],$asunto,$cuerpo_sendmail,$cabeceras_sm);

}


/**
*	Function: send_mail
*   		Send email using gmail service
*
*	Created by:
*		_Carlos Haas_
*
*	Modified By:
*		- Oscar Sanchez:
*
*
*   	Parameters:
*		- to: To mail
*		- subject: Subject Mai
*		- ext_message: Message Mail
*		- ext_headers: Headers Mail
*
*   	Returns:
*		0: Message Failed
*		1: Message Sent
*
*   	See Also:
*
*/
function send_mail($to, $subject, $ext_message, $ext_headers){

	global $cfg;

	set_include_path($cfg['mail_pear_path']);
	require_once($cfg['mail_pear_path'] . 'Mail.php');

	$body = $ext_message;
	$host = "ssl://smtp.gmail.com"; //ssl://
	$port = "465";
	$from = $cfg['gmail_username'];
	$username = $cfg['gmail_username'];
	$password = $cfg['gmail_passwd'];

	$headers["MIME-Version"] = "1.0";
	$headers["Content-Type"] = "text/html; charset=iso-8859-1";
	$headers["From"] = $from;
	$headers["To"] = $to;
	$headers["Subject"] = $subject;

	if (is_array($ext_headers)) {
		foreach($ext_headers as $k => $v) {
			$k = strtolower($k);
			switch ($k) {
				case ("mime-version") : $k = "MIME-Version"; break;
				case ("content-type") : $k = "Content-Type"; break;
				case ("from") : $k = "From"; break;
				case ("to") : $k = "To"; break;
				case ("subject") : $k = "Subject"; break;
				case ("reply-to") : $k = "Reply-To"; break;
				case ("cc") : $k = "CC"; break;
				case ("bcc") : $k = "BCC"; break;
			}  // End switch
			$headers["$k"] = "$v";
		}
	}  // End if

	$smtp_array = array ('host' => $host,
			'port' => $port,
			'auth' => true,
			'username' => $username,
			'password' => $password);

	$smtp = Mail::factory('smtp',$smtp_array);

	$mail = $smtp->send($to, $headers, $body);

 	if (PEAR::isError($mail)) {
		#echo("<p>This is: " . $mail->getMessage() . "</p>");
		return 0;
	} else {
		#echo("<p>Message successfully sent!</p>");
		return 1;
	}  // End if

}  // End function

	
function showPaymentData($zipcode,$state){
#-----------------------------------------
# Created on: 11/04/09  17:34:10 By  Roberto Barcenas
# Forms Involved: confirmacion.php
# Description : Devuelve el total a pagar y el desglose de pagos para la orden
# Parameters : 	
	
	global $cses;
	
	$strout = '';
	$payments = $cses[payments];
	
	while($payments > 0){
		if($payments ==	1)	$fprice	=	round($amount - $sumprice,2);	
			$strout ='<tr>
					<td class="m_text">'.trans_txt('payment').'('.$payments.')</td>
					<td style="font-family:Arial, Helvetica, sans-serif; color:#708090;font-size:12px; text-left:right; height:20px;">$'.number_format(round($cses['total_order'],2),2).'</td>
				</tr>'	.	$strout;
			$sumprice+=round($fprice,2);					
		$payments--;					
	}
	
	$strout	='<tr>
			<td class="m_text">'.trans_txt('order_total').'</td>
			<td class="m1_text" height:20px;">$'.number_format(round($cses['total_order'],2),2).' '.trans_txt('order_inc').'</td>
		</tr>'	.	$strout;

	return $strout;
}

function build_edit_choices_module($id,$url,$param,$module,$content_link=''){
# --------------------------------------------------------

	$output='';$family='';
	
	if (strlen($id)	>	6){
		$family = substr($id,3,6);
	}else{
		$family = $id;
	}	
	
	$sth = mysql_query("SELECT COUNT(*) FROM sl_skus WHERE ID_products='$family' AND Status='Active';");
	list($choices) =  mysql_fetch_row($sth);
	if ($choices >	1){
		if(/*substr($id,0,3)>100 and*/ substr($id,0,3)!=999)
			$img='cart/edit_btn.gif';
		else
			$img='sel.gif';
		if($content_link=='')
			$content_link="<img src='/images/$img' title='Edit' alt='' border='0'>";
		$output = "<br><a href='#$module' class='l_text'  id='ajax_btn' name='choices_btn' onClick=\"popup_show('ajax_windows', 'ajax_drag', 'ajax_exit', 'element-right', -1, -1,'$module');loadDoc('/cgi-bin/nsc_admin/common/apps/ajaxbuild?ajaxbuild=choices&id_products=$family&url=$url&$param');\">$content_link</a> ";
	}
	return $output;
}	

function drop_item(){
# --------------------------------------------------------
# Created on: 01/11/2010
# Author: RB
# Last Modified on: 01/11/2010 @ 16:21:02
# Last Modified by: RB
# Description : Drop an item from the cart
# Parameters : 
#		
	global $cses,$cfg,$in;

  #Recorre los servicios
  for ($i=1;$i <= $cses['servis_in_basket'];$i++){
      if ($cses['servis_'.$i.'_qty']>0 and $cses['servis_'.$i.'_id']>0){
          #Verifica si tiene servicio ligado
          if($cses['items_'.$in['do'].'_id']==$cses['servis_'.$i.'_relid'] or $cses['servis_'.$i.'_id'] == "60000".$cfg['duties'] or $cses['servis_'.$i.'_id'] == "60000".$cfg['insurance']){
			unset($cses['servis_dut']);
			unset($cses['servis_ins']);
			unset($cses['servis_'.$i.'_id']);
			unset($cses['servis_'.$i.'_qty']);
			unset($cses['servis_'.$i.'_ser']);
			unset($cses['servis_'.$i.'_relid']);
			unset($cses['servis_'.$i.'_desc']);
			unset($cses['servis_'.$i.'_fpago']);
			unset($cses['servis_'.$i.'_payments']);
			unset($cses['servis_'.$i.'_price']);
			unset($cses['servis_'.$i.'_discount']);
			unset($cses['servis_'.$i.'_shp1']);
			unset($cses['servis_'.$i.'_shp2']);
			unset($cses['servis_'.$i.'_tax']);
          }
      }
  }
    
	#Recorre los productos
	for ($i=1;$i <= $cses['items_in_basket']; $i++){
		if ($cses['items_'.$i.'_qty'] > 0 and $cses['items_'.$i.'_id'] > 0){
			#Verifica si tiene producto ligado
			#if($cses['items_'.$in['do'].'_id'] != $cses['items_'.$i.'_id'] and isset($cses['items_'.$in['do'].'_relid']) and $cses['items_'.$in['do'].'_relid']==$cses['items_'.$i.'_relid']){
			if($in['do']!=$i and isset($cses['items_'.$in['do'].'_relid']) and $cses['items_'.$in['do'].'_relid']==$i){
				#echo "<br>encontre producto ligado ".$cses['items_'.$in['do'].'_relid']."<br>";
				#Recorre los servicios
				for($j=1;$j <= $cses['servis_in_basket']; $j++){
					if ($cses['servis_'.$j.'_qty']>0 and $cses['servis_'.$j.'_id'] > 0){
						#Verifica si tiene servicio ligado
						if($cses['items_'.$i.'_id']==$cses['servis_'.$j.'_relid'] || $cses['servis_'.$j.'_id']=="60000".$cfg['duties'] || $cses['servis_'.$j.'_id']=="60000".$cfg['insurance']){ #RB Modify
							#echo "encontre servicio ".$cses['servis_'.$j.'_id']."<br>";
							unset($cses['servis_dut']);
							unset($cses['servis_ins']);
							unset($cses['servis_'.$j.'_id']);
							unset($cses['servis_'.$j.'_qty']);
							unset($cses['servis'.$in['do'].'_price']);
							unset($cses['servis_'.$j.'_fpprice']);
							unset($cses['servis_'.$j.'_paytype']);
							unset($cses['servis_'.$j.'_ser']);
							unset($cses['servis_'.$j.'_relid']);
							unset($cses['servis_'.$j.'_desc']);
							unset($cses['servis_'.$j.'_fpago']);
							unset($cses['servis_'.$j.'_payments']);
							unset($cses['servis_'.$j.'_price']);
							unset($cses['servis_'.$j.'_discount']);
							unset($cses['servis_'.$j.'_shp1']);
							unset($cses['servis_'.$j.'_shp2']);
							unset($cses['servis_'.$j.'_tax']);
						}
					}
				}
				#echo "Borrando los datos de $i -- ".$cses['items_'.$i.'_id']."<br>";
				unset($cses['items_'.$i.'_desc']);
				unset($cses['items_'.$i.'_downpayment']);
				unset($cses['items_'.$i.'_id']);
				unset($cses['items_'.$i.'_qty']);
				unset($cses['items_'.$i.'_price']);
				unset($cses['items_'.$i.'_fpprice']);
				unset($cses['items_'.$i.'_paytype']);
				unset($cses['items_'.$i.'_weight']);
				unset($cses['items_'.$i.'_size']);
				unset($cses['items_'.$i.'_fpago']);
				unset($cses['items_'.$i.'_payments']);
				unset($cses['items_'.$i.'_discount']);
				unset($cses['items_'.$i.'_tax']);
			}
		}
	}
	
	#echo "queriendo borrar los datos de ".$cses['items_'.$in['do'].'_id']."<br>";
	unset($cses['items_'.$in['do'].'_desc']);
	unset($cses['items_'.$in['do'].'_downpayment']);
	unset($cses['items_'.$in['do'].'_id']);
	unset($cses['items_'.$in['do'].'_qty']);
	unset($cses['items_'.$in['do'].'_price']);
	unset($cses['items_'.$in['do'].'_fpprice']);
	unset($cses['items_'.$in['do'].'_paytype']);
	unset($cses['items_'.$in['do'].'_weight']);
	unset($cses['items_'.$in['do'].'_size']);
	unset($cses['items_'.$in['do'].'_fpago']);
	unset($cses['items_'.$in['do'].'_payments']);
	unset($cses['items_'.$in['do'].'_discount']);
	unset($cses['items_'.$in['do'].'_tax']);
	--$cses[products_in_basket];
}


function edit_choice(){
# --------------------------------------------------------
# Created on: 01/11/2010
# Author: RB
# Last Modified on: 01/11/2010 @ 16:21:02
# Last Modified by: RB
# Description : Change the choice of a product from the cart
# Parameters : 
#		
	global $cses,$cfg,$in;	
	
	

	# Changing the choice
	for ($i=1;$i <=	$cses['items_in_basket'];$i++){
	    if($cses['items_'.$i.'_qty']	>	0 and $i == $in['do'])
	        #echo "Cambiando ".$cses['items_'.$i.'_id']." por ".$in['ajaxresp'];
	        $cses['items_'.$i.'_id'] = $in['ajaxresp'];
	}
	
	#Changing service related
	for ($i=1;$i <= $cses['servis_in_basket'];$i++){
	    if($cses['servis_'.$i.'_qty']	>	0 and $cses['servis_'.$i.'_relid'] == $in['idchoiceold'])
	    	$cses['servis_'.$i.'_relid'] = $in['ajaxresp'];
	}
}


function get_cod_delivery_dates($zipcode,$mode=0){
#-----------------------------------------
# Created on: 07/09/09  18:07:14 By  Roberto Barcenas
# Forms Involved: 
# Description :
# Parameters : 

	global $cses,$cfg;
	if($cses['paytype']=='Credit-Card'){
		echo "";
		return;
	}
	$strout = '';
	
	$sth = mysql_query("SELECT Name,Delivery_days,Delivery_hours FROM codagents WHERE Zip = '".mysql_real_escape_string($zipcode)."';") or die("Query failed : " . mysql_error());
		
	while ($rec= mysql_fetch_array($sth)){
		$codagents=$rec[0];
		$dates=$rec[1];
		$hours=$rec[2];
		$codtakes = 'MO';
		if(preg_match_all("/[^(ups)(iw)]/i",$codagents,$matches))
			$codtakes .= ','.trans_txt('cash');
			$strout .= '<tr class="titulos"><td>'.$codagents.'</td>';
		if($cfg[default_lang]=='sp'){
			$strout .= '<td>'.$dates.'</td>';
			$strout .= '<td>'.$hours.'</td>';
		}elseif($cfg[default_lang]=='en'){
			$dates=str_replace('Lunes','Monday',$dates);
			$dates=str_replace('Martes','Tuesday',$dates);
			$dates=str_replace('Miercoles','Wednesday',$dates);
			$dates=str_replace('Jueves','Thursday',$dates);
			$dates=str_replace('Viernes','Friday',$dates);
			$dates=str_replace('Sabado','Saturday',$dates);
			$dates=str_replace('Domingo','Sunday',$dates);
			
			$hours=str_replace(' a ',' to ',$hours);
			
			$strout .= '<td>'.$dates.'</td>';
			$strout .= '<td>'.$hours.'</td>';
		}
		
		$strout .= '<td>'.$codtakes.'</td></tr>';
		$strout .= '<tr><td colspan="4">&nbsp;</td></tr>';

	}
	if($mode==0)
		echo $strout;
	else
		return $strout;
}

function specialsum($scr,$act){
# --------------------------------------------------------
# Forms Involved: 
# Created on: 01/13/10 17:50:02
# Author: MCC C. Gabriel Varela S.
# Description :   
# Parameters :
	if($act==0)
	{
		$link = preg_replace("/\+/", "``", $scr);
//		
//		$link = preg_replace("/\"/", "`", $link);
//		#$link = preg_replace("/\'\'/", "``", $link);
//		$link = preg_replace("/\s/", "-", $link);
	}
	elseif($act==1)
	{
		$link = preg_replace("/``/", "+", $scr);
//		
//		$link = preg_replace("/`/", "\"", $link);
//		#$link = preg_replace("/``/", "\'\'", $link);
//		$link = preg_replace("/-/", " ", $link);
	}
	return $link;
}
	
function show_image_in_page($id,$img,$type,$gift=0){
# --------------------------------------------------------
# Forms Involved: 
# Created on: 05/11/09 17:19:02
# Author: MCC C. Gabriel Varela S.
# Description :   
# Parameters :
# Last Modified on: 05/12/09 12:21:30
# Last Modified by: MCC C. Gabriel Varela S: Se manda par?tro img
# Last Modified by RB on 04/17/2012: Se agrega envio de variable $gift para mostrar foto de producto regalo

	global $cfg;
	$output='';
	$bandexit=0;
	$bandfound=0;
	## if the product is a set, assign that value to id_products
	for($i=1;$i<10 and $bandexit==0;$i++)
	{
		if ((file_exists($cfg['path_imgmanf'].$id."c$i.jpg")or file_exists($cfg['path_imgmanf'].$id."c$i.gif")or file_exists($cfg['path_imgmanf'].$id."c$i.jpeg")) and $type=='c') {
			if($i==1)
				$imglink="<img src='/cgi-bin/showimages.cgi?id=$id&img=$img&type=c&spict=$img' alt='' style='border:0px;'>";
			else
				$imglink="";
			$output.="<a href=\"/cgi-bin/showimages.cgi?id=$id&pict=$i\" Title='Images' rel='rel$id'>$imglink</a>";
			$bandfound=1;
		}elseif ((file_exists($cfg['path_imgmanf'].$id."b$i.gif")or file_exists($cfg['path_imgmanf'].$id."b$i.jpg")or file_exists($cfg['path_imgmanf'].$id."b$i.jpeg")) and ($type=='b' or $type=='c')) {
			if($i==1)
				$imglink="<img src='/cgi-bin/showimages.cgi?id=$id&img=$img&type=b&spict=$img&gift=$gift' alt='' style='border:0px;'>";
			else
				$imglink="";
			$output.="<a href=\"/cgi-bin/showimages.cgi?id=$id&pict=$i\" Title='Images' rel='rel$id'>$imglink</a>";
			$bandfound=1;
			echo "/cgi-bin/showimages.cgi?id=$id&pict=$i";
		}elseif (file_exists($cfg['path_imgmanf'].$id."a$i.gif")or file_exists($cfg['path_imgmanf'].$id."a$i.jpg")or file_exists($cfg['path_imgmanf'].$id."a$i.jpeg")) {
			if($i==1)
				$imglink="<img src='/cgi-bin/showimages.cgi?id=$id&img=$img&type=a&spict=$img' alt='' style='border:0px;'>";
			else
				$imglink="";
			$output.="<a href=\"/cgi-bin/showimages.cgi?id=$id&pict=$i\" Title='Images' rel='rel$id'>$imglink</a>";
			$bandfound=1;
		}else{
			if($i==1)
				$output = "<p align='center'><img src='$cfg[url_images]Picture-Not-Available.gif' alt='$cfg[url_images]noimage.jpeg' width='99' height='99'></p>";
			$bandexit=1;
		}
	}
	return $output;
}

function show_counter($type){
# --------------------------------------------------------
	$counter_query = mysql_query("SELECT startdate, counter FROM nsc_counter");

	if ($type == 'counter'){
		if (!mysql_num_rows($counter_query)) {
			$date_now = date('Ymd');
			mysql_query("INSERT INTO nsc_counter (startdate, counter) VALUES ('" . $date_now . "', '1')");
			$counter_startdate = $date_now;
			$counter_now = 1;
		} else {
			$counter = mysql_fetch_array($counter_query);
			$counter_startdate = $counter['startdate'];
			$counter_now = ($counter['counter'] + 1);
			mysql_query("UPDATE nsc_counter set counter = '" . $counter_now . "'");
		}
		return (number_format($counter_now));
	}else{
		if (!mysql_num_rows($counter_query)) {
			$counter_startdate = date('Ymd');
		}else{
			$counter_startdate = $counter['startdate'];
		}
  		return strftime(DATE_FORMAT_LONG, mktime(0, 0, 0, substr($counter_startdate, 4, 2), substr($counter_startdate, -2), substr($counter_startdate, 0, 4)));
  	}

}



function load_cartimage(){
# --------------------------------------------------------
# Created on: 07/10/08 @ 16:11:02
# Author: Carlos Haas
# Last Modified on: 07/10/08 @ 16:11:02
# Last Modified by: Carlos Haas
# Description : 
# Parameters : 
#		
	global $cfg,$cses;
	$image	= '/cart/basket_sp'.$cses['products_in_basket']	.	'.png';
	#$cfg['url_images'] . '/cart/basket_sp
	if(!is_file($cfg['path_images'].$image) or !is_readable($cfg['path_images'].$image)){
		$image	= $cfg['url_images'] . '/cart/basket_sp0.png';
	}else{
		$image	= $cfg['url_images']. $image;
	}
	$strout = '';
	
	if(isset($cses['products_in_basket']) and $cses['products_in_basket'] > 0){
		$strout =	'<a href="http://'.$cfg['maindomain'].'/-editing_cart" alt="'.$cfg['app_title'].'"><img src="'.$image.'" width="150" height="55" border="0" alt="'.$cfg['app_title'].'" /></a>';
	}
	return $strout;
}


## Function products_inorder . Move it to functions.php? 
function products_inorder(){
# --------------------------------------------------------
# Created on: 07/10/08 @ 16:11:02
# Author: Carlos Haas
# Last Modified on: 07/10/08 @ 16:11:02
# Last Modified by: Carlos Haas
# Description : 
# Parameters : 
#	Last Time Modified by RB on 12/13/2010 : Se agregan parametros para calculo con shipping_table / Se habilita el arreglo $shippings al calcular itemshipping		   	
//Last modified on 4 Feb 2011 16:06:17
//Last modified by: MCC C. Gabriel Varela S. :Se hace que no se pueda avanzar si por cambio de pagos el último pago es mayor que la fecha de vencimiento de la tarjeta
//Last modified on 04/13/11 04:58:45 PM
//Last modified by: MCC C. Gabriel Varela S. : Se integra reward_points
//Last modified on 2 May 2011 12:41:40
//Last modified by: MCC C. Gabriel Varela S. : Se implementa promo_campaign

	global $cfg,$cses,$va,$in,$usr,$device;

	$cant=0;$desc=array();$price=0;$output='';$edt='';$aux='';$weight=0;$totalqty=0;$cupon=0;$choices='';
	$flexipago=0;$fpdisc=0;$total=0;$total_tax=0;$onepay=0;$banddays=0;
	
	$cses['categories']='';
	$va['items_discounts'] = 00;
	$va['itemsproducts_list'] = '';
	
	if ($cses['items_in_basket'] > 0 or $cses['servis_in_basket'] > 0){
		(!isset($cses['dayspay'])) and ($cses['dayspay'] =1);

		##########################################
		#########  PRODUCTS    ###################
		##########################################
		$flag=0;
		$c = explode(",",$cfg{'srcolors'});
		for ($i=1; $i <= $cses['items_in_basket']; $i++){
			$d = 1 - $d;
			$str_disc	=	'';
			$backorder='';
			$warning_choice = '';
			
			if ($in['action']=='restartpayments'){
				$cses['items_'.$i.'_payments'] = 1;
			}
			
			if ($in["fpago$i".$cses['items_'.$i.'_id']]){
				$cses['items_'.$i.'_payments'] = $in["fpago$i".$cses['items_'.$i.'_id']];
			}
			
			if ($cses['items_'.$i.'_qty'] > 0 and $cses['items_'.$i.'_id'] > 0){
				
				if((!isset($cses['items_'.$i.'_promo']) and !isset($cses['items_'.$i.'_idpromo']) and !isset($cses['items_'.$i.'_reward_points']) and empty($cses['items_'.$i.'_free'])) or $flag != $cses['items_'.$i.'_promo']){
					$tprod='id';
					
					if(isset($cses['items_'.$i.'_promo'])){ 
						$tprod 	= 'promo'; 
						$flag		=	$cses['items_'.$i.'_promo'];
					}
					
					## By Table?
					$shpcal = load_name('sl_products','ID_products',substr($cses['items_'.$i.'_'.$tprod],3,6),'shipping_table');
					$shpmdis = load_name('sl_products','ID_products',substr($cses['items_'.$i.'_'.$tprod],3,6),'shipping_discount');
					$shpcalp = load_name('sl_products_prior','ID_products',substr($cses['items_'.$i.'_'.$tprod],3,6),'shipping_table');
					
					if($shpcalp != ''){
						$shpcal = $shpcalp;
						$shpmdis = load_name('sl_products_prior','ID_products',substr($cses['items_'.$i.'_'.$tprod],3,6),'shipping_discount');
					}
					
					$idpacking = load_name('sl_products','ID_products',substr($cses['items_'.$i.'_'.$tprod],3,6),'ID_packingopts');
					
					$q1 = "SELECT ID_packingopts FROM sl_products_prior WHERE ID_products = '".substr($cses['items_'.$i.'_'.$tprod],3,6)."' AND BelongsTo = '".$cfg['owner']."';";
					$sth = mysql_query($q1);
					list($idpackingp) = mysql_fetch_row($sth);


					if($idpackingp!='')
						$idpacking=$idpackingp;
					
					$shippings = itemshipping($cses['edt'],$cses['items_'.$i.'_size'],1,1,$cses['items_'.$i.'_weight'],$idpacking,$shpcal,$shpmdis,substr($cses['items_'.$i.'_'.$tprod],3,6));
					
					if(!isset($cses['items_'.$i.'_shpf']))	$cses['items_'.$i.'_shp1'] = $shippings[0] ;
					$cses['items_'.$i.'_shp2'] = $shippings[1];
					if(!isset($cses['items_'.$i.'_shpf']))	$cses['items_'.$i.'_shp3'] = $shippings[2];
					
					##### Shipping discount
					if($shpcal == 'Fixed' and isset($cfg['shpdis_cc']) and $cses['paytype'] == 'Credit-Card'){
						$cses['items_'.$i.'_shp1'] = round($cses['items_'.$i.'_shp1']*$cfg['shpdis_cc'],3);	
						$cses['items_'.$i.'_shp2'] = round($cses['items_'.$i.'_shp2']*$cfg['shpdis_cc'],3);
						$cses['items_'.$i.'_shp3'] = round($cses['items_'.$i.'_shp3']*$cfg['shpdis_cc'],3);
					}
					
				}else{
					$cses['items_'.$i.'_shp1'] = 0;
					$cses['items_'.$i.'_shp2'] = 0;
					$cses['items_'.$i.'_shp3'] = 0;
				}

			
				$cant += $cses['items_'.$i.'_qty'];
				$totalqty  += $cses['items_'.$i.'_qty'];

				## Buscamos la info del producto solo si no es un idpromo (de cupon)

				$str_join_coupon= ($cses['items_'.$i.'_idpromo'] == 1 or $cses['items_'.$i.'_reward_points']==1) ? 'left' : 'inner';
				$sth = mysql_query("Select * 
				from (Select 
				if(not isnull(sl_products_prior.SPrice) and sl_products_prior.SPrice!=0,sl_products_prior.SPrice,sl_products.SPrice)as SPrice,
				sl_products.ID_products,
				if(not isnull(sl_products_prior.Name) and sl_products_prior.Name!='',sl_products_prior.Name,sl_products.Name) as Name,
				if(not isnull(sl_products_prior.Model)and sl_products_prior.Model!='',sl_products_prior.Model,sl_products.Model) as Model,
				if(not isnull(sl_products_prior.Weight)and sl_products_prior.Weight!=0 and sl_products_prior.Weight!='',sl_products_prior.Weight,sl_products.Weight) as Weight,
				if(not isnull(sl_products_prior.SizeW)and sl_products_prior.SizeW!=0 and sl_products_prior.SizeW!='',sl_products_prior.SizeW,sl_products.SizeW) as SizeW,
				if(not isnull(sl_products_prior.SizeH)and sl_products_prior.SizeH!=0 and sl_products_prior.SizeH!='',sl_products_prior.SizeH,sl_products.SizeH) as SizeH,
				if(not isnull(sl_products_prior.SizeL)and sl_products_prior.SizeL!=0 and sl_products_prior.SizeL!='',sl_products_prior.SizeL,sl_products.SizeL) as SizeL,
				if(not isnull(sl_products_prior.Flexipago)and sl_products_prior.Flexipago!=0 and sl_products_prior.Flexipago!='',sl_products_prior.Flexipago,sl_products.Flexipago) as Flexipago,
				if(not isnull(sl_products_prior.FPPrice)and sl_products_prior.FPPrice!=0 and sl_products_prior.FPPrice!='',sl_products_prior.FPPrice,sl_products.FPPrice) as FPPrice,
				/*0 as FPPrice,*/
				if(not isnull(sl_products_prior.MemberPrice)and sl_products_prior.MemberPrice!=0 and sl_products_prior.MemberPrice!='',sl_products_prior.MemberPrice,sl_products.MemberPrice) as MemberPrice,
				if(not isnull(sl_products_prior.PayType)and sl_products_prior.PayType!='',sl_products_prior.PayType,sl_products.PayType) as PayType,
				if(not isnull(sl_products_prior.edt)and sl_products_prior.edt!=0 and sl_products_prior.edt!='',sl_products_prior.edt,sl_products.edt) as edt,
				if(not isnull(sl_products_prior.ID_packingopts)and sl_products_prior.ID_packingopts!='',sl_products_prior.ID_packingopts,sl_products.ID_packingopts) as ID_packingopts,
				if(not isnull(sl_products_prior.Downpayment)and sl_products_prior.Downpayment!=0 and sl_products_prior.Downpayment!='',sl_products_prior.Downpayment,sl_products.Downpayment) as Downpayment
			from sl_products
			left join sl_products_prior on(sl_products.ID_products=sl_products_prior.ID_products)
   and sl_products_prior.belongsto='$cfg[owner]'
			$str_join_coupon join sl_products_w on(sl_products.ID_products=sl_products_w.ID_products)
			left join sl_products_categories on(sl_products.ID_products=sl_products_categories.ID_products)
			left join sl_categories on (sl_products_categories.ID_categories=sl_categories.ID_categories)
			where $cfg[whereproducts])as sl_products
where 1 and ID_products='".substr($cses['items_'.$i.'_id'],3,6)."';") or die("Query failed C6555555: " . mysql_error());
				#$sth = mysql_query("SELECT * FROM sl_products WHERE ID_products='".substr($cses['items_'.$i.'_id'],3,9)."' ;");

				$rec = mysql_fetch_assoc($sth);

				###### Si es promo, los valores son los del relid/#productos
				if (isset($cfg['promo'.$cses['items_'.$i.'_relid']])){
					#$rec['SPrice'],$rec['SPrice1'],$rec['SPrice2'],$rec['SPrice3'],$rec['SPrice4'],$rec['FPPrice'],$rec['MemberPrice'],$rec['PayType'],$rec-['Downpayment']) = 
					get_promo_prices($cses['items_'.$i.'_relid']);
				}
				
				if ($cfg['multiprice'] and $cses['items_'.$i.'_pnum']	>	1){
						$price    = $rec['SPrice'.($cses['items_'.$i.'_pnum']-1)];
						$fpprice = $price;
						if((!$cses['items_'.$i.'_price'] and $price)or($cses['items_'.$i.'_price'] and $price and $cses['items_'.$i.'_price']!=$price))
						{
							//Se comenta
							//$cses['items_'.$i.'_price'] = $price;
						}
						//Se comenta
						//$cses['items_'.$i.'_fpago'] = 1;
				}elseif($cses['items_'.$i.'_idpromo'] == 1 or substr($cses['items_'.$i.'_id'],3,6)==$cfg['gifts_ids'] or $cses['items_'.$i.'_reward_points']==1){
						$price = $cses['items_'.$i.'_price'];
						$fpprice = 0;
				}else{
						//Se evalúa price
						if(isset($cses['items_'.$i.'_price']))
						{
							$price = $cses['items_'.$i.'_price'];
						}
						else
						{
							$price = $rec['SPrice'];
						}
						if(isset($cses['items_'.$i.'_fpprice']))
						{
							$fpprice = $cses['items_'.$i.'_fpprice'];
						}
						else
						{
							$fpprice = $rec['FPPrice'];
						}
						#$fpprice = $price;
						if((!$cses['items_'.$i.'_price'] and $price)or($cses['items_'.$i.'_price'] and $price and $cses['items_'.$i.'_price']!=$price))
						{
							//Se comenta
							//$cses['items_'.$i.'_price'] = $price;
						}
						if((!$cses['items_'.$i.'_fpprice'] and $fpprice)or($cses['items_'.$i.'_fpprice'] and $fpprice and $cses['items_'.$i.'_fpprice'] != $fpprice))
						{
							//Se comenta
							//$cses['items_'.$i.'_fpprice'] = $fpprice;
						}
						if((!$cses['items_'.$i.'_fpago'] and $rec['Flexipago'])or($cses['items_'.$i.'_fpago'] and $rec['Flexipago'] and $cses['items_'.$i.'_fpago'] != $rec['Flexipago']))
						{
							//Se comenta
							//$cses['items_'.$i.'_fpago'] = $rec['Flexipago'];
						}
				}
				
				$desci[$i] = $rec['Name'];
				$name_w = load_name('sl_products_w','ID_products',substr($cses['items_'.$i.'_id'],3,6),'Name');
				($name_w != '') and ($desci[$i]= $name_w);
				($desci[$i] == '') and ($desci[$i] =$cses['items_'.$i.'_desc']);
				$desci[$i] = substr($desci[$i],0,35);
				
				if((!$cses['items_'.$i.'_desc'] and $rec['Model'])or($cses['items_'.$i.'_desc'] and $rec['Model'] and $cses['items_'.$i.'_desc'] != $rec['Model']))
				{
					//Se comenta
					//$cses['items_'.$i.'_desc'] = $rec['Model'];
				}
				$msprice=$rec['MemberPrice'];
				
				if(!isset($rec['MemberPrice']) or $rec['MemberPrice']	==	0){
					if ($cfg['multiprice'] and $cses['items_'.$i.'_pnum']	>	1)
						$msprice=$rec['SPrice'.($cses['items_'.$i.'_pnum']-1)];
					else
					{
						//Se cambia evaluación
						if(isset($cses['items_'.$i.'_price']))
						{
							$msprice=$cses['items_'.$i.'_price'];
						}
						else if($rec['SPrice'])
							$msprice=$rec['SPrice'];
						else
							$msprice=$price;
					}
				}
				
				if((!$cses['items_'.$i.'_paytype'] and $rec['PayType'])or($cses['items_'.$i.'_paytype'] and $rec['PayType'] and $cses['items_'.$i.'_paytype'] != $rec['PayType']))
				{
					//Se comenta
					//$cses['items_'.$i.'_paytype'] = $rec['PayType'];
				}
				if((!$cses['items_'.$i.'_downpayment'] and $rec['Downpayment'])or($cses['items_'.$i.'_downpayment'] and  $rec['Downpayment'] and $cses['items_'.$i.'_downpayment'] != $rec['Downpayment']))
				{
					//Se comenta
					//$cses['items_'.$i.'_downpayment'] = $rec['Downpayment']; 
				}
				
				## Calculate EDT
				$aux = $rec['edt'];
				if($aux	>	$edt) $edt = $aux;		
				
				####################################
				##### Check Cupons			
				####################################
				if (isset($cses['cupon'])){
					$sth = mysql_query("SELECT * FROM sl_products_categories WHERE ID_products = '$rec[ID_products]' ;");
					$reccat = mysql_fetch_assoc($sth);
					if (isset($reccat['ID_categories'])){
						$categories_ex	='';
						if(isset($categories_ex))
							$cses['categories']=1;
					}
				}

				if(!isset($edt))	$edt = 3;
				
				## Calculate Weight
				//Se comenta
				//$cses['items_'.$i.'_size'] 	= $rec['SizeW']*$rec['SizeH']*$rec['SizeL'];
				//$cses['items_'.$i.'_weight'] 	= $rec['Weight'];


				##########################################
				#########  Other Payment Types
				##########################################
				if ($cses['paytype'] != 'Credit-Card' and $cses['paytype'] != 'lay'){
					$cses['items_'.$i.'_payments'] = 1;
				}
				
				##########################################
				#########  CALCULAR PAGO CONTADO
				##########################################
					if(isset($cfg['promo_campaign']) and $cfg['promo_campaign']==1){
						$str_price = format_price($price);
						$total  += $price *  $cses['items_'.$i.'_qty'];
						$onepay = $price;
						$cses['items_'.$i.'_discount'] = 0;
						
						if($cses['items_'.$i.'_payments'] >= 1 or $cses['paytype'] == 'Layaway' or $cses['paytype'] == 'Credit-Card'){
							$va['items_discounts'] 	+= $price-$msprice;
							if(($price-$msprice)!=	0)	$str_disc = " (Descuento por Promoción " . format_price($price-$msprice) . ")";
							$cses['items_'.$i.'_discount'] = $price-$msprice;
							$onepay = $msprice;
						}
						
						if($cses['paytype'] == 'Credit-Card' or $cses['paytype'] == 'Layaway' or $cses['paytype'] == 'cod')
							$price = $rec['MemberPrice'];
					
					}elseif(isset($cfg['membership']) and $cfg['membership']==1 and $usr['type']	==	"Membership"){
						$str_price = format_price($price);
						$total  += $price *  $cses['items_'.$i.'_qty'];
						$onepay = $price;
						$cses['items_'.$i.'_discount'] = 0;
						
						if($cses['items_'.$i.'_payments'] >= 1 or $cses['paytype'] == 'Layaway' or $cses['paytype'] == 'Credit-Card'){
							$va['items_discounts'] 	+= $price-$msprice;
							if(($price-$msprice)!=	0)	$str_disc = " (Descuento de Membresia " . format_price($price-$msprice) . ")";
							$cses['items_'.$i.'_discount'] = $price-$msprice;
							$onepay = $msprice;
						}
						
						if($cses['paytype'] == 'Credit-Card' or $cses['paytype'] == 'Layaway' or $cses['paytype'] == 'cod')
							$price = $rec['MemberPrice'];
					
					}elseif ($fpprice > 0){
						$str_price = &format_price($fpprice);
						$total  += $fpprice *  $cses['items_'.$i.'_qty'];
						$onepay = $price;
						$str_disc = " (Descuento : " . format_price($fpprice-$price) . ")";
						
						if ($cses['items_'.$i.'_payments'] == 1 or $cses['items_'.$i.'_payments'] == '3c'){
							$va['items_discounts'] += $fpprice-$price;
							($cses['items_'.$i.'_discount'] == 0) and ($cses['items_'.$i.'_discount'] = $fpprice-$price);
						}else{
							$va['items_discounts'] = $va['items_discounts'] - ($fpprice-$price) >= 0 ? $fpprice-$price : 0;  
							$cses['items_'.$i.'_discount'] = 0;
						}
						
					}elseif(strstr($cses['items_'.$i.'_id'],$cfg['disc40']) !== FALSE){
						$str_price = format_price($price);
						$total  += $price *  $cses['items_'.$i.'_qty'];
						$str_disc = " (Descuento : " . format_price( ($price-0) * 40/100) . ")";
						$onepay = $price - ($price * 40)/100;
						
						if ($cses['items_'.$i.'_payments'] == 1 or $cses['items_'.$i.'_payments'] == '3c'){
							$va['items_discounts'] += $price * 40/100;
							$cses['items_'.$i.'_discount'] = $price * 40/100;
						}
						
					}elseif (strstr($cses['items_'.$i.'_id'],$cfg['disc30']) !== FALSE){
						$str_price = format_price($price);
						$total  += $price *  $cses['items_'.$i.'_qty'];
						$str_disc = " (Descuento : " . format_price( ($price-0) * 30/100) .")";
						$onepay = $price - ($price * 30)/100;
						
						if ($cses['items_'.$i.'_payments'] == 1 or $cses['items_'.$i.'_payments'] == '3c'){
							$va['items_discounts'] += $price * 30/100;
							$cses['items_'.$i.'_discount'] = $price * 30/100;
						}
						
					}else{
						$str_price = format_price($price);
						$total  += $price *  $cses['items_'.$i.'_qty'];
						
						if ($cfg['fpdiscount'.$cses['items_'.$i.'_fpago']]	>	0 and ($cses['items_'.$i.'_payments'] == 1 or $cses['items_'.$i.'_payments'] == '3c')){
							$va['items_discounts'] += $price * $cfg['fpdiscount'.$cses['items_'.$i.'_fpago']]	/	100;
							$cses['items_'.$i.'_discount'] = $price * $cfg['fpdiscount'.$cses['items_'.$i.'_fpago']]	/	100;
						}
						
						if (($price * $cfg['fpdiscount'.$cses['items_'.$i.'_fpago']]	/	100) >0){
							$str_disc = " (Descuento : " . format_price( $price * $cfg['fpdiscount'.$cses['items_'.$i.'_fpago']]	/	100) . ")";
							$onepay = $price - $price * $cfg['fpdiscount'.$cses['items_'.$i.'_fpago']]	/	100;
						}else{
							$onepay = $price;
						}
					}
				
				
				
				$sthk = mysql_query("SELECT * FROM sl_skus WHERE ID_sku_products='".$cses['items_'.$i.'_id']."'");
				$rec = mysql_fetch_assoc($sthk);
				$thischoices = "$rec[choice1],$rec[choice2],$rec[choice3],$rec[choice4]";
				$thischoices = explode(",",$thischoices);
				$choices = load_choices('-',$thischoices);
				
				if($rec['Status'] == 'Backorder')	$backorder	=	'<span style="color:red;">[Backorder]</span>';
				if (isset($in["fpago$i".$cses["items_".$i."_id"]]) and $banddays	==	0)	$cses['items_'.$i.'_payments'] = $in["fpago$i".$cses["items_".$i."_id"]];

					## Se comenta toda la parte de los flexipagos debido a que en estos momentos no es necesario. Sin embargo cuando sea necesario debe pasarse el codigo a php

				(!$cses['items_'.$i.'_payments']) and ($cses['items_'.$i.'_payments']=1);

				if(($cses['paytype'] == 'Credit-Card' or $cses['paytype'] == 'Layaway') and $in['step'] == '4' and !isset($cses['id_orders'])){
					
					##########################################
					#########  STEP 4
					##########################################
					############################################################
					#Mensual a Quincenal o a Contado según sea el caso
					############################################################
					#Si ya se ha establecido pago quincenal y el número de pagos del producto en turno es diferente de uno y es igual al número de pagos mensuales. Entonces
					if($cses['items_'.$i.'_fpago'] == $cses['items_'.$i.'_payments'] and $banddays==1 and $cses['dayspay']==15 and $cses['items_'.$i.'_fpago']!=1){
						#Si est„1¤7habilitado pagos quincenales en el sistema o si el producto tiene tipo de pago Layaway entonces
						if($cfg['fpbiweekly'] or stristr($cses['items_'.$i.'_paytype'],"Layaway") != FALSE)
						{
							#Se establecen los pagos para el producto en turno en quincenales
							$cses['items_'.$i.'_payments']*=2;
						}
						else
						{
							#Si no entonces se establecen como pago de contado
							$cses['items_'.$i.'_payments']=1;
						}
					}
					############################################################
					#Mensual a Semanal o a Contado según sea el caso
					############################################################
					#Si ya se ha establecido pago semanal y el número de pagos del producto en turno es diferente de uno y es igual al número de pagos mensuales. Entonces
					elseif($cses['items_'.$i.'_fpago'] == $cses['items_'.$i.'_payments'] and $banddays==1 and $cses['dayspay']==7 and $cses['items_'.$i.'_fpago']!=1){
						#Si est„1¤7habilitado pagos semanales en el sistema o si el producto tiene tipo de pago Layaway entonces
						if($cfg['fpweekly'] or stristr($cses['items_'.$i.'_paytype'],"Layaway") != FALSE)
						{
							#Se establecen los pagos para el producto en turno en semanales
							$cses['items_'.$i.'_payments']*=4;
						}
						else
						{
							#Si no entonces se establecen como pago de contado
							$cses['items_'.$i.'_payments']=1;
						}
					}
					############################################################
					#Quincenal a Mensual
					############################################################
					#Si ya se ha establecido pago mensual y el producto en turno tiene pagos quincenales entonces
					elseif($cses['items_'.$i.'_fpago']*2 == $cses['items_'.$i.'_payments'] and $banddays==1 and $cses['dayspay']==30){
						 #se cambian por pagos mensuales
						$cses['items_'.$i.'_payments']/=2;
					}
					############################################################
					#Quincenal a Semanal
					############################################################
					#Si ya se ha establecido pago semanal y el producto en turno tiene pagos quincenales entonces
					elseif($cses['items_'.$i.'_fpago']*2 == $cses['items_'.$i.'_payments'] and $banddays==1 and $cses['dayspay']==7){
						#Si est„1¤7habilitado pagos semanales en el sistema o si el producto tiene tipo de pago Layaway entonces
						if($cfg['fpweekly'] or stristr($cses['items_'.$i.'_paytype'],"Layaway") != FALSE)
						{
							#se cambian por pagos semanales
							$cses['items_'.$i.'_payments']*=2;
						}
						else
						{
							#Si no entonces se establecen como pago de contado
							$cses['items_'.$i.'_payments']=1;
						}
					}
					############################################################
					#Semanal a Mensual
					############################################################
					#Si ya se ha establecido pago mensual y el producto en turno tiene pagos semanales entonces
					elseif($cses['items_'.$i.'_fpago']*4 == $cses['items_'.$i.'_payments'] and $banddays==1 and $cses['dayspay']==30){
						 #se cambian por pagos mensuales
						$cses['items_'.$i.'_payments']/=4;
					}
					############################################################
					#Semanal a Quincenal
					############################################################
					#Si ya se ha establecido pago quincenal y el producto en turno tiene pagos semanales entonces
					elseif($cses['items_'.$i.'_fpago']*4 == $cses['items_'.$i.'_payments'] and $banddays==1 and $cses['dayspay']==15){
						#Si est„1¤7habilitado pagos quincenales en el sistema o si el producto tiene tipo de pago Layaway entonces
						if($cfg['fpbiweekly'] or stristr($cses['items_'.$i.'_paytype'],"Layaway") != FALSE)
						{
						 	#se cambian por pagos quincenales
							$cses['items_'.$i.'_payments']/=2;
						}
						else
						{
							#Si no entonces se establecen como pago de contado
							$cses['items_'.$i.'_payments']=1;
						}
					}

					
					#echo $banddays  ." y ". $cses['items_'.$i.'_fpago'] ."==". $cses['items_'.$i.'_payments'] ."and". $cses['items_'.$i.'_fpago'];
					if($banddays==0){
						if($cses['items_'.$i.'_fpago'] == $cses['items_'.$i.'_payments'] and $cses['items_'.$i.'_fpago'] > 1){
							$cses['dayspay']=30;
							$banddays=1;
						}elseif($cses['items_'.$i.'_fpago']*2 == $cses['items_'.$i.'_payments']){
							$cses['dayspay']=15;
							$banddays=1;
						}elseif($cses['items_'.$i.'_fpago']*4 == $cses['items_'.$i.'_payments'] or $cses['items_'.$i.'_fpago']*4+1 == $cses['items_'.$i.'_payments']){
							$cses['dayspay']=7;
							$banddays=1;
						}
						elseif($cses['items_'.$i.'_payments'] == '3c'){
							$cses['dayspay']=20;
							$banddays=1;
						}
						else{
							$cses['dayspay']=1;
						}
					}
					

					#$cses{'items_'.$i.'_downpayment1'} = $cses['items_'.$i.'_price'] * 0.07;
					if($cses['items_'.$i.'_payments'] > 1 && $cses['dayspay']==15){ #quincenal
						#$total+=$cses{'items_'.$i.'_downpayment1'};
					} else { 
						#$total  += $price * $cses['items_'.$i.'_qty'];
					}
					

					if ($in{"fpago$i".$cses{"items_".$i."_id"}} and $banddays==0){
						$cses['items_'.$i.'_payments'] = $in["fpago$i".$cses["items_".$i."_id"]];
					}

					if ($cses['items_'.$i.'_downpayment'] > 0)# or $cses{'items_'.$i.'_downpayment1'}>0)
					{
						$flexipago = show_products_payments($i,$onepay,$price,$fpprice,$str_disc);
					}elseif($cses['items_'.$i.'_idpromo'] == 1){ ## items via cupon
						$flexipago = '<span style="color:red">'.trans_txt('idpromo_coupon_text').'</span>';
					}elseif($cses['items_'.$i.'_reward_points'] == 1){ ## items via reward_points
						$flexipago = '<span style="color:red">'.trans_txt('idpromo_reward_points_text').'</span>';
					}else{
						$flexipago = show_products_payments($i,$onepay,$price,$fpprice,$str_disc);
					}
				}else{
					$flexipago = '';
				}
				
				#$flexipago='';
				#$cses['items_'.$i.'_payments']=	1;
				$choiceslink = '';
				
				if ($in['step'] == '4' and !isset($cses['id_orders'])){
					#$choiceslink = build_edit_choices_module(substr($cses['items_'.$i.'_id'],3),"index.php","cmd=cart&step=$in[step]&to_do=drop&do=$i&checkout=1#tabs","tabchoice$i");
				}
				#($in{'step'}=='8') and ($choiceslink = &build_edit_choices_module(substr($cses['items_'.$i.'_id'],3),$script_url,"cmd=console_order&step=$in{'step'}&drop=$i#tabs","tabchoice$i"));
				$id=$cses['items_'.$i.'_id']; 
			
				## Item has choices and user hasn't choose yet.
				if(substr($cses['items_'.$i.'_id'],0,3) == '999'){
				    $warning_choice	=	'<br><span style="color:#b83333;font-size:10px;">'.build_edit_choices_module(substr($cses['items_'.$i.'_id'],3),"index.php","cmd=cart&step=$in[step]&to_do=drop&do=$i&checkout=1#tabs","tabchoice$i").'</span>';
				}


				$va['itemsproducts_list'] .= "
						<tr bgcolor='$c[$d]'>
							<td class='m_text' align='left' nowrap>";
							
				if ($in['step'] == '4' and !isset($cses['id_orders'])){
					$va['itemsproducts_list'] .= "<a href='$cfg[stepconfirm]-checkout-delete_$i'><img src='$cfg[url_images]delete.gif' title='Drop' alt='' border='0'></a> ";
				}			
				$va['itemsproducts_list'] .= "<a href='/$name_w-a' title='".trans_txt('goto_product')."' class='l1_text' target='_blank'>". 				
									format_sltvid($cses['items_'.$i.'_id']). "</a>&nbsp; 
									 ". $choiceslink ." </td>
							<td class='m_text' id='tabchoice$i' align='right'>".$cses['items_'.$i.'_qty']."</td>
							<td class='m_text' align='left'>$desci[$i] $backorder $choices $warning_choice<br>$flexipago</td>
							<td class='l1_text' align='right' nowrap>$str_price </td>
						</tr>";
				
				## Calculate Tax individually
				if($fpprice > 0){
						if ($cses['items_'.$i.'_payments'] == 1 or $cses['items_'.$i.'_payments'] == '3c'){
								$cses['items_'.$i.'_tax'] = (($cses['items_'.$i.'_fpprice'] - $cses['items_'.$i.'_discount']) * $cses['items_'.$i.'_qty']) *   $cses['tax_total'];
								#echo $cses['items_'.$i.'_tax'] .'= (('.$cses['items_'.$i.'_fpprice'].' - '.$cses['items_'.$i.'_discount'].') * '.$cses['items_'.$i.'_qty'].') *   '.$cses['tax_total'].'<br>';
						}else{
								$cses['items_'.$i.'_tax'] = $cses['items_'.$i.'_fpprice'] * $cses['items_'.$i.'_qty'] * $cses['tax_total'];
								#echo $cses['items_'.$i.'_tax'] .'= '.$cses['items_'.$i.'_fpprice'].' * '.$cses['items_'.$i.'_qty'].' *   '.$cses['tax_total'].'<br>';
								$cses['items_'.$i.'_discount'] = 0;
						}
				}else{
						if(($cfg['membership'] and $usr['type']	==	"Membership")or(isset($cfg['promo_campaign']) and $cfg['promo_campaign']==1)){
							$cses['items_'.$i.'_tax'] = (($cses['items_'.$i.'_price'] * $cses['items_'.$i.'_qty'])-($cses['items_'.$i.'_discount'] * $cses['items_'.$i.'_qty'])) *  $cses['tax_total'];
						}elseif ($cses['items_'.$i.'_payments'] == 1 or $cses['items_'.$i.'_payments'] == '3c'){	
							$cses['items_'.$i.'_tax'] = (($cses['items_'.$i.'_price'] * $cses['items_'.$i.'_qty'])-($cses['items_'.$i.'_discount'] * $cses['items_'.$i.'_qty'])) *  $cses['tax_total'];
							#echo $cses['items_'.$i.'_tax'] .'= (('.$cses['items_'.$i.'_price'].' - '.$cses['items_'.$i.'_discount'].') * '.$cses['items_'.$i.'_qty'].') *   '.$cses['tax_total'].'<br>';
						}else{
							$cses['items_'.$i.'_tax'] = $cses['items_'.$i.'_fpprice'] * $cses['items_'.$i.'_qty'] * $cses['tax_total'];
							$cses['items_'.$i.'_discount'] = 0;
						}
				}
				$total_tax += $cses['items_'.$i.'_tax'];
				##
			}
		}

		$cses['total_i']=$total;
		
//		calculate_shipping;
//		if($in{'step'}== 6){
//			$va{'shptotal1'} = &format_price($va{'shptotal1'});
//			$va{'shptotal2'} = &format_price($va{'shptotal2'});
//			$va{'shptotal3'} = &format_price($va{'shptotal3'});
//			$va{'shptotalf'} = &format_price(0);
//		}

		if($cses['paytype']	==	'COD')	
			$in['shp_type']=$cfg['codshptype'];
		else
			$in['shp_type']=$cfg['ccshptype'];
		//Se comenta
		//$cses['shipping_total'] = $va['shptotal'.$in['shp_type']];
		//$cses['shp_type'] = $in['shp_type'];
		update_cart_session();

		##########################################
		#########  SERVICES    ###################
		##########################################
		$banddays=0;
//		for$i(1..$cses['servis_in_basket']){
//			if ($cses['servis_'.$i.'_qty']>0 and $cses['servis_'.$i.'_id']>0){
//				$price=$cses['servis_'.$i.'_price'];
//				if($cses['servis_'.$i.'_fpago']==$cses['servis_'.$i.'_payments'] and $banddays==1 and $cses['dayspay']==15){
//					$cses['servis_'.$i.'_payments']*=2;
//				}elsif($cses['servis_'.$i.'_fpago']*2==$cses['servis_'.$i.'_payments'] and $banddays==1 and $cses['dayspay']==30){
//					$cses['servis_'.$i.'_payments']/=2;
//				}
//				($cses['servis_'.$i.'_id']=="60000".$cfg{'postdatedfeid'}) and ($cses['total_order']-$cses['shipping_total']-$cses['tax_total'] <= 350) and ($cses['servis_'.$i.'_price'] = $cfg{'postdatedfesprice'});
//				($cses['servis_'.$i.'_id']=="60000".$cfg{'postdatedfeid'}) and ($cses['total_order']-$cses['shipping_total']-$cses['tax_total'] >  350) and ($cses['servis_'.$i.'_price'] = $cfg{'postdatedfesprice350'});
//				$flexiserv='';
//				if ($cses['servis_'.$i.'_id']=="60000".$cfg{'extwarrid'}){
//					@itemsessionid = &getsessionfieldid('items_','_id',$cses['servis_'.$i.'_relid'],'');
//					if($cses{'items_'.$itemsessionid[0].'_fpago'} and ($cses{'paytype'}=='cc' or $cses{'paytype'}=='lay') and $in{'step'}=='8'){
//						$cses['servis_'.$i.'_fpago']=$cses{'items_'.$itemsessionid[0].'_fpago'} if(!$cses['servis_'.$i.'_fpago']);
//						$cses['servis_'.$i.'_fpago']=1;
//						$cses['servis_'.$i.'_payments']=$cses{'items_'.$itemsessionid[0].'_payments'} if(!$cses['servis_'.$i.'_payments']);
//						$cses['servis_'.$i.'_payments'] = $in{"fpagoserv$i".$cses{'items_'.$itemsessionid[0].'_id'}} if ($in{"fpagoserv$i".$cses{'items_'.$itemsessionid[0].'_id'}} );
//						if($cses['servis_'.$i.'_payments']==1){
//							$cses['servis_'.$i.'_price']=$cfg{'extwarrpctsfp'}*$cses{'items_'.$itemsessionid[0].'_price'}/100;
//						}else{
//							$cses['servis_'.$i.'_price']=$cfg{'extwarrpct'}*$cses{'items_'.$itemsessionid[0].'_fprice'}/100;
//							if($cses['dayspay']==1){
//								if($banddays==0){
//									if($cses['servis_'.$i.'_fpago']eq$cses['servis_'.$i.'_payments']){
//										$cses['dayspay']=30;
//										$banddays=1;
//									}elsif($cses['servis_'.$i.'_fpago']*2==$cses['servis_'.$i.'_payments']){
//										$cses['dayspay']=15;
//										$banddays=1;
//									}else{
//										$cses['dayspay']=1;
//									}
//								}
//							}
//						}
//						### Se cambia el precio de la garantia extendida por el minimo aceptado si es necesario
//						$cses['servis_'.$i.'_price'] = $cfg{'extwarminprice'} if $cses['servis_'.$i.'_price'] < $cfg{'extwarminprice'};
//						if ($in{'step'}=='8'){
//							##########################################
//							#########  STEP 8
//							##########################################
//							$price = $cses['servis_'.$i.'_price'];#$rec->{'SPrice'};
//							if($cses['servis_'.$i.'_id']=="60000".$cfg{'extwarrid'}){
//								#$cses{'servis_'.$i.'_downpayment1'} = ($cfg{'extwarrpct'}*$cses{'items_'.$itemsessionid[0].'_price'}/100)*0.07;
//							}
//							if($cses['servis_'.$i.'_payments'] > 1 && $cses['dayspay']==15){
//								#$total+=$cses{'servis_'.$i.'_downpayment1'};
//							}
//							if($cses{'item_'.$i.'_payments'}/2 > $cses{'item_'.$i.'_fpago'}){
//								$paysservices = $cses{'item_'.$i.'_payments'};
//								$fpagoservices = $cses{'item_'.$i.'_fpago'};
//							} else {
//								$paysservices = $cses['servis_'.$i.'_payments'];
//								$fpagoservices = $cses['servis_'.$i.'_fpago'];
//							}
//							if($paysservices/2==$fpagoservices){
//								#$price1 = $price+$cses{'servis_'.$i.'_downpayment1'};
//							}else{
//								$price1 = $price;
//							}
//						}
//						if ($cses{'servis_'.$i.'_downpayment'}>0)# or $cses{'servis_'.$i.'_downpayment1'}>0)
//						{
//							$cadpagoinicial=">";
//							if($cses{'servis_'.$i.'_downpayment'}>0){
//								$cadpagoinicial=">Pago Inicial ".&format_price($cses{'servis_'.$i.'_downpayment'})." + ";
//							}
//							$flexiserv = &show_servis_payments($i);
//						}else{
//							$flexiserv = &show_servis_payments($i);
//						}
//					}else{
//						$flexiserv = '';
//					}
//				}
//				$cant_s += $cses['servis_'.$i.'_qty'];
//				$totalqty_s  += $cses['servis_'.$i.'_qty'];
//				if ($cses['servis_'.$i.'_ser']){
//					my ($sth) = &Do_SQL("SELECT * FROM sl_services WHERE ID_services ='".substr($cses['servis_'.$i.'_id'],5,4)."'");
//					$rec = $sth->fetchrow_hashref;
//					$desc[$i] = $rec->{'Name'}." for the product ID: ".&format_sltvid($cses['servis_'.$i.'_relid']);
//					$cses['servis_'.$i.'_desc'] = $rec->{'Description'};
//					if($cses['servis_'.$i.'_id']=="60000".$cfg['duties'] || $cses['servis_'.$i.'_id']=="60000".$cfg['insurance']){
//						$price = $cses['servis_'.$i.'_price'];
//						$desc[$i] = $rec->{'Name'}." for the order";
//					}
//					if ($in{'step'}=="7a"){
//						$price = $cses['servis_'.$i.'_price'];#$rec->{'SPrice'};
//						if($cses['servis_'.$i.'_id']=="60000".$cfg{'extwarrid'}){
//							#$cses{'servis_'.$i.'_downpayment1'} = ($cfg{'extwarrpct'}*$cses{'items_'.$itemsessionid[0].'_price'}/100)*0.07;
//						}
//					}
//				}
//		    
//				if($rec->{'SalesPrice'}=='Fixed'){
//					if($rec->{'Tax'}=='Yes'){
//						$total_p_f_ty+= ($price * $cses['servis_'.$i.'_qty']);	      		
//					}else{
//						$total_p_f_tn+= ($price * $cses['servis_'.$i.'_qty']);
//					}
//				}else{
//					if($rec->{'Tax'}=='Yes'){
//						$total_p_v_ty+= ($total * ($price /100));	
//					}else{
//						$total_p_v_tn+= ($total * ($price /100));	
//					}
//				}				
//					
//				$serviceid=&format_sltvid($cses['servis_'.$i.'_id']);
//				if($rec->{'Status'} ne 'Hidden' and $in{'step'}=='8'){
//					$linkserv="<a href='$script_url?cmd=console_order&step=$in{'step'}&dropser=$i&id_services=$rec->{'ID_services'}#tabs'><img src='$va{'imgurl'}/$usr{'pref_style'}/b_drop.png' title='Drop' alt='' border='0'></a>";
//				}else{
//					$linkserv='';
//				}
//				if($rec->{'SalesPrice'}=='Fixed'){
//					$total_cs = $price ;
//					$cses['servis_'.$i.'_price'] = $price;
//					if($cses['servis_'.$i.'_payments']==2*$cses['servis_'.$i.'_fpago']){
//						$price1=$price + $cses{'servis_'.$i.'_downpayment1'};
//						#$total+=$cses{'servis_'.$i.'_downpayment1'} if ($in{'step'}eq'7a');
//					}else{
//						$price1=$price;
//					}
//					$price1	 = &format_price($price1);
//					$price	 = &format_price($price);
//					#&cgierr("$price y $price1");	
//					#GV Inicia 27may2008
//					$va{'itemsproducts_list'} .= qq|
//						<tr  onmouseover='m_over(this)' onmouseout='m_out(this)'>
//							<td class="smalltext">$linkserv
//							<a href="/cgi-bin/mod/sales/console?cmd=console_order&step=2&action=search&id_products=|.substr($cses['servis_'.$i.'_id'],5).qq|"><img src='[va_imgurl]/[ur_pref_style]/b_view.gif' title='View' alt='' border='0'></a>
//							$serviceid</td>
//							<td class="smalltext">1</td>
//							<td class="smalltext">$desc[$i] $flexiserv</td>
//							<td class="smalltext" align='right' nowrap>$price1 </td>
//						</tr>\n|;
//				}else{					
//					$total_cs= $cses['total_i'] * ($rec->{'SPrice'}/100);
//					$cses['servis_'.$i.'_price'] = $total_cs;
//					
//					$total_cs=&format_price($total_cs);			
//					$va{'itemsproducts_list'} .= qq|
//						<tr  onmouseover='m_over(this)' onmouseout='m_out(this)'>
//							<td class="smalltext">$linkserv $serviceid</td>
//							<td class="smalltext">1</td>
//							<td class="smalltext">$desc[$i]</td>
//							<td class="smalltext" align='right'>$total_cs</td>
//						</tr>\n|;
//				}			
//			}
//		}		
		
				
		$total+= $total_p_f_ty + $total_p_v_ty;
		$total+= $total_p_f_tn + $total_p_v_tn;
						
		$va['shptype1_min']=0;
		$va['shptype1_max']=0;
		$shp_min=explode(",",$cfg['shp_edt_min']);
		$shp_max=explode(",",$cfg['shp_edt_max']);
		$va['shptype1_min']= $shp_min[0];$va['shptype2_min']=$shp_min[1];$va['shptype3_min']=$shp_min[2];
		$va['shptype1_max']= $shp_max[0];$va['shptype2_max']=$shp_max[1];$va['shptype3_max']=$shp_max[2];
		$va['shptype1_min']	+= $edt;
		$va['shptype1_max']	+= $edt;
		
		$va['shptype2_min']	+= $edt;	
		$va['shptype2_max']	+= $edt;
		
		if($totalqty_s >= 1){
			$output .= "<br>".trans_txt('msg_servis')." : $totalqty_s ";
		}else{
			$totalqty_s = 0;
			$output .= "<br>".trans_txt('msg_servis')." : No selecciono servicios";
		}
		
	 	$va['items_stotal'] = format_price($total+$totaln);
		$va['items_shipping'] = format_price($cses['shipping_total']);
		

		
		###### Suma los taxes del shipping
		if (isset($cfg['shptax']) and $cses['shipping_total'] > 0 and $cses['tax_total'] > 0) $total_tax += $cses['shipping_total'] * $cses['tax_total'];	
		
		
		if ($cses['tax_total']){
			$va['items_taxporc'] = " (".($cses['tax_total']*100)."%)";
			$va['items_tax'] = format_price($total_tax);
		}else{
			$va['items_tax'] = '---';
		}
		
		if ($cses['cupon'] and !$cses['categories']){
			$sth = mysql_query("SELECT * FROM sl_coupons WHERE PublicID='$cses[cupon]' AND Status='Active' AND (ValidFrom <= CURDATE() AND ValidTo >= CURDATE())");
			$rec = mysql_fetch_assoc($sth);
			if ($rec['DiscPerc']){
				$cupon = int($total * $rec['DiscPerc'])/100;
				$output .= "<br>Cupon : $cses[cupon]  $rec[DiscPerc] % = " . format_price(-$cupon);	
			}else{
				$cupon = $rec['DiscValue'];
				$output .= "<br>Cupon : $cses[cupon]  ".format_price(-$rec['DiscValue']);	
			}
		}
		
		if($cses['discount_applied']==1)
			$va['items_discounts']=$cses['items_discounts'];
		
		if ($va['items_discounts']) {
			$cupon += $va['items_discounts'];
			$cses['items_discounts'] =$va['items_discounts'];
			$va['items_discounts'] = format_price($va['items_discounts']);
		}else{
			$cses['items_discounts']=$va['items_discounts'];
			$va['items_discounts'] = '---';
		}
		if ($cses['tax_total']){
			$va['items_taxporc'] = " (".($cses['tax_total']*100)."%)";
			$va['items_tax'] = format_price($total_tax);
		}else{
			$va['items_tax'] = '---';
		}

				
		$cses['total_disc'] = $cupon;
		#Dejar ?a l?a como est?1„1¤7ya que as?1„1¤7o se calculan taxes sobre servicios.GV
		$cses['total_order'] = intval(($total+$totaln-$cupon+$cses['shipping_total']+($cses['total_i']-$cupon)*$cses['tax_total'])*100+0.9)/100;
		
		$va['items_total'] = format_price($cses['total_order']);
		$cses['edt'] = $edt;
		
	}else{
		return trans_txt('empty_cart');
	}
	update_cart_session();
}


function build_checkout_steps(){
# -------------------------------------------------------- 
    global $cses,$in,$cfg;
    $strout .= <<<QQ
    
 <table border="0" cellspacing="0" cellpadding="0">
	<tr>
QQ;

		$strout .= "<td onmouseover='m_over(this)' onmouseout='m_out(this)' onClick=\"trjump('/-editing_cart')\"><img border='0' src='$cfg[url_images]/cart/c_1.gif' width='130' height='25'></td>\n";
    
//    if(isset($cses['step1']) and $cses['step1'] ==  'done'){
//        if($in['step']  != 'shp_pay02' and !isset($cses['step5']))
//            $strout .= '<a href="/index.php?cmd=cart&checkout=1&step=shp_pay02&edit_cfn=1">'.trans_txt('path_shipping_info').'</a> - ';
//        else{
//            if($in['step']  == 'shp_pay02')
//                $strout .= '<span class="step_path_active">'.trans_txt('path_shipping_info') .'</span> - ';
//        }
		if ($in[step]>='2'){
			$link="";
			#$in[btn4]='Editar';
			if ($in[step]>'2' and $cses[step5]!='done' and $cses['paytype'] != 'paypal')
				$link=" onmouseover='m_over(this)' onmouseout='m_out(this)' onClick=\"trjump('/2&btn4=Editar-checkout')\"";
			$strout .= "<td $link><img border='0' src='$cfg[url_images]/cart/c_2.gif' width='130' height='25'></td>\n";
		}else{
			$strout .= "<td><img border='0' src='$cfg[url_images]/cart/c_2_off.gif' width='130' height='25'></td>\n";
		}
        
//        if(isset($cses['step2']) and $cses['step2'] ==  'done' and $in['step']  != 'paytype03' and !isset($cses['step5']))
//            $strout .= '<a href="/index.php?cmd=cart&checkout=1&step=paytype03&edit_cfn=1">'.trans_txt('path_paytype').'</a> - ';
//        else{
//            if($in['step']  == 'paytype03')
//                  $strout .= '<span class="step_path_active">'.trans_txt('path_paytype') .'</span> - ';
//      
		if ($in[step]>='3'){
			$link="";
			if ($in[step]>'3' and $cses[step5]!='done' and $cses['paytype'] != 'paypal')
				$link="onmouseover='m_over(this)' onmouseout='m_out(this)' onClick=\"trjump('/3&btn4=Editar-checkout')\"";
			$strout .= "<td $link><img border='0' src='$cfg[url_images]/cart/c_3.gif' width='130' height='25'></td>\n";
		}else{
			$strout .= "<td><img border='0' src='$cfg[url_images]/cart/c_3_off.gif' width='130' height='25'></td>\n";
		}
    
//        if(isset($cses['step3']) and $cses['step3'] ==  'done' and $in['step']  != 'confirm04' and !isset($cses['step5']))
//            $strout .= '<a href="/index.php?cmd=cart&checkout=1&step=confirm04&edit_cfn=1">'.trans_txt('path_confirm').'</a> - ';
//        else{
//            if($in['step']  == 'confirm04')
//                 $strout .= '<span class="step_path_active">'.trans_txt('path_confirm') .'</span> - ';
//        }
		if ($in[step]>=4){
			$link="";
			if ($in[step]>4 and $cses[step5]!='done' and $cses['paytype'] != 'paypal')
				$link="onmouseover='m_over(this)' onmouseout='m_out(this)' onClick=\"trjump('/4&btn4=Editar-checkout')\"";
			$strout .= "<td $link><img border='0' src='$cfg[url_images]/cart/c_4.gif' width='130' height='25'></td>\n";
		}else{
			$strout .= "<td><img border='0' src='$cfg[url_images]/cart/c_4_off.gif' width='130' height='25'></td>\n";
		}
            
//        if($in['step']  == 'final05')
//              $strout .= '<span class="step_path_active">'.trans_txt('path_finalsale');
		if ($in[step]>=5)
			$strout .= "<td><img border='0' src='$cfg[url_images]/cart/c_5.gif' width='130' height='25'></td>\n";
		else
			$strout .= "<td><img border='0' src='$cfg[url_images]/cart/c_5_off.gif' width='130' height='25'></td>\n";

                
//    }
	$strout .= <<<QQ
	</tr>
</table>
QQ;
	return $strout;
}

function run_port_function(array $params){
# --------------------------------------------------------
# Forms Involved: 
# Created on: 03/25/10 17:21:39
# Author: MCC C. Gabriel Varela S.
# Description :   
# Parameters :
	global $in,$error,$cfg;
	$in[filepage]="functions/".$params[0].".html";
	$cmdname = "runport_".$params[0];
	if (function_exists($cmdname))
		$rep_str = $cmdname($params);
	return build_page($in[filepage]);
}


function validate_email($mail){
# --------------------------------------------------------
# Forms Involved: 
# Created on: 03/26/10 12:48:39
# Author: RB
# Description : Determines wheter is valid or not an email
# Parameters : the string containing the email address

      $valid=false;

      $regular = "^[a-z0-9_\+-]+(\.[a-z0-9_\+-]+)*@[a-z0-9-]+(\.[a-z0-9-]+)*\.([a-z]{2,4})$";
      $strange = "^[a-z0-9,!#\$%&'\*\+/=\?\^_`\{\|}~-]+(\.[a-z0-9,!#\$%&'\*\+/=\?\^_`\{\|}~-]+)*@[a-z0-9-]+(\.[a-z0-9-]+)*\.([a-z]{2,})$";

      if (eregi($regular, $mail) | eregi($strange, $mail)){
	$valid=true;
      }
 
      return $valid;
}

function build_categories_links (){
	global $cfg;
	$i=0;
	$banddiv=0;
	$sth = mysql_query("Select *
from(Select 
	if(not isnull(sl_products_w.Title),sl_products_w.Title,if(not isnull(sl_categories.Title),sl_categories.Title,'".trans_txt('other')."'))as Title,
	if(not isnull(sl_products_prior.web_available)and sl_products_prior.web_available!='',sl_products_prior.web_available,sl_products.web_available) as web_available,
	if(not isnull(sl_products_prior.Status)and sl_products_prior.Status!='',sl_products_prior.Status,sl_products.Status) as Status
from sl_products
left join sl_products_prior on(sl_products.ID_products=sl_products_prior.ID_products)
and sl_products_prior.belongsto='$cfg[owner]'
inner join sl_products_w on(sl_products.ID_products=sl_products_w.ID_products)
left join sl_products_categories on(sl_products.ID_products=sl_products_categories.ID_products)
left join sl_categories on (sl_products_categories.ID_categories=sl_categories.ID_categories)
where $cfg[whereproducts])as sl_products
group by Title;") or die("Query failed : " . mysql_error());
	$count=mysql_num_rows($sth);
	while ($rec = mysql_fetch_assoc($sth)){
		#$output .= "<option value=\"$rec[Title]\">$rec[Title]</option>\n";
		$output .= "<div align=\"left\" class=\"m1_text\" style=\"margin-left:3px; margin-top:0px\">
								<img alt='' src='images/arrow.jpg' hspace='0' vspace='0' border='0' align='left' style='margin-right:3px; margin-top:3px'>
								<a href='http://".$cfg['maindomain']."/".ucfirst(strtolower($rec[Title]))."-b' class='text'>".ucfirst(strtolower($rec[Title]))."</a>
							</div>
							<div style='margin-left:px; margin-top:2px;'>
								<img alt=''  border='0'  src='images/line.jpg'>
							</div>";
		$i++;
		if($i>=($count/2) and $banddiv==0)
		{
			$output .= "</td>
						<td width='122' style='height:px' valign='top'>";
			$banddiv=1;
		}
	}
	return $output;
}

function do_for_one_product(){
// --------------------------------------------------------
// Forms Involved: 
// Created on: 2 Apr 2010 18:54:23
// Author: MCC C. Gabriel Varela S.
// Description :   
// Parameters :
// Last time modified by RB on 06/23/2010 : Se agrega precio de Membresia para Club Innova
// Last time modified by RB on 06/24/2010 : Se modifica para presentar templates extension .club.html si el cliente es Miembro Club Innova
// Last time modified by RB on 12/30/2010 : Se agrega llamado a boton like de facebook
// Last time modified by RB on 12/31/2010 : Se agrega creacion de metatags opengraph de facebook
//Last modified on 2 May 2011 11:58:44
//Last modified by: MCC C. Gabriel Varela S. : Se hace que también se condicione el mostrar el ícono de membership. Se incorpora promo_campaign

	global $tpl,$in,$cfg,$usr,$va,$device;

	$tpl['skel'] = $device['is_mobile_device'] ? $tpl['skel'] : "cart_product.html";

	if($in['product']!=''){
// 		if($in[fullquery]!='')
// 		{
// 			preg_match("/product=(.*)/",$in[fullquery],$matches);
// 			$in[product]=$matches[1];
// 		}
		$msg="$in[product]<br>\n";
		#$link=specialsum($in[product],1);
		#$link=utf8_decode($link);
		$where.=" and (Name_link='".mysql_real_escape_string($in['product'])."' or ID_products='".mysql_real_escape_string($in['product'])."') ";
	}

	$modwhere = ( (!empty($in['action']) and $in['action']) =='cart_add') ? " OR sl_products.Status = 'Active' " : "";

	$this_query = "Select * 
from (Select 
				if(not isnull(sl_products_prior.SPrice)and sl_products_prior.SPrice!=0 and sl_products_prior.SPrice!='',sl_products_prior.SPrice,sl_products.SPrice)as SPrice,
				if(not isnull(sl_products_prior.MemberPrice)and sl_products_prior.MemberPrice > 0,sl_products_prior.MemberPrice,sl_products.MemberPrice)as MemberPrice,
				if(not isnull(sl_products_prior.Status)and sl_products_prior.Status!='',sl_products_prior.Status,sl_products.Status) as Status,
				if(not isnull(sl_products_w.Title)and sl_products_w.Title!='',sl_products_w.Title,if(not isnull(sl_categories.Title),sl_categories.Title,'".trans_txt('other')."'))as Title,
				sl_products.ID_products,
				if(not isnull(sl_products_prior.Name)and sl_products_prior.Name!='',sl_products_prior.Name,sl_products.Name) as Name,
				if(not isnull(sl_products_w.Name),sl_products_w.Name,'Other') as Name_link,
				if(not isnull(sl_products_prior.Model)and sl_products_prior.Model!='',sl_products_prior.Model,sl_products.Model) as Model,
				if(not isnull(sl_products_prior.SmallDescription)and sl_products_prior.SmallDescription!='',sl_products_prior.SmallDescription,sl_products.SmallDescription) as SmallDescription,
				if(not isnull(sl_products_prior.Description)and sl_products_prior.Description!='',sl_products_prior.Description,sl_products.Description) as Description,
				if(not isnull(sl_products_prior.Weight)and sl_products_prior.Weight!=0 and sl_products_prior.Weight!='',sl_products_prior.Weight,sl_products.Weight) as Weight,
				if(not isnull(sl_products_prior.SizeW)and sl_products_prior.SizeW!=0 and sl_products_prior.SizeW!='',sl_products_prior.SizeW,sl_products.SizeW) as SizeW,
				if(not isnull(sl_products_prior.SizeH)and sl_products_prior.SizeH!=0 and sl_products_prior.SizeH!='',sl_products_prior.SizeH,sl_products.SizeH) as SizeH,
				if(not isnull(sl_products_prior.SizeL)and sl_products_prior.SizeL!=0 and sl_products_prior.SizeL!='',sl_products_prior.SizeL,sl_products.SizeL) as SizeL,
				if(not isnull(sl_products_prior.Flexipago)and sl_products_prior.Flexipago!=0,sl_products_prior.Flexipago,sl_products.Flexipago) as Flexipago,
				/*if(not isnull(sl_products_prior.FPPrice)and sl_products_prior.FPPrice!=0,sl_products_prior.FPPrice,sl_products.FPPrice) as FPPrice,*/
				0 as FPPrice,
				if(not isnull(sl_products_prior.PayType)and sl_products_prior.PayType!='',sl_products_prior.PayType,sl_products.PayType) as PayType,
				if(not isnull(sl_products_prior.edt)and sl_products_prior.edt!=0 and sl_products_prior.edt!='',sl_products_prior.edt,sl_products.edt) as edt,
				if(not isnull(sl_products_prior.ID_packingopts)and sl_products_prior.ID_packingopts!=0 and sl_products_prior.ID_packingopts!='',sl_products_prior.ID_packingopts,sl_products.ID_packingopts) as ID_packingopts,
				if(not isnull(sl_products_prior.Downpayment)and sl_products_prior.Downpayment!=0 and sl_products_prior.Downpayment!='',sl_products_prior.Downpayment,sl_products.Downpayment) as Downpayment,
				if(not isnull(sl_products_prior.ChoiceName1)and sl_products_prior.ChoiceName1!='',sl_products_prior.ChoiceName1,sl_products.ChoiceName1) as ChoiceName1,
				if(not isnull(sl_products_prior.ChoiceName2)and sl_products_prior.ChoiceName2!='',sl_products_prior.ChoiceName2,sl_products.ChoiceName2) as ChoiceName2,
				if(not isnull(sl_products_prior.ChoiceName3)and sl_products_prior.ChoiceName3!='',sl_products_prior.ChoiceName3,sl_products.ChoiceName3) as ChoiceName3,
				if(not isnull(sl_products_prior.ChoiceName4)and sl_products_prior.ChoiceName4!='',sl_products_prior.ChoiceName4,sl_products.ChoiceName4) as ChoiceName4,
				if(not isnull(sl_products_prior.web_available)and sl_products_prior.web_available!='',sl_products_prior.web_available,sl_products.web_available) as web_available,
				maxqty
			from sl_products
			left join sl_products_prior on(sl_products.ID_products=sl_products_prior.ID_products)
   and sl_products_prior.belongsto='$cfg[owner]'
			inner join sl_products_w on(sl_products.ID_products=sl_products_w.ID_products)
			left join sl_products_categories on(sl_products.ID_products=sl_products_categories.ID_products)
			left join sl_categories on (sl_products_categories.ID_categories=sl_categories.ID_categories)
			where 
			((sl_products.Status='On-Air' AND sl_products.web_available='Yes') OR sl_products.Status='Web Only' $modwhere)  and sl_products_w.belongsto='innovashop'
			)as sl_products
where 1 $where;";

	$sth = mysql_query($this_query) or die("Query failed C6555555: " . mysql_error());
	#echo "$msg<br>\n";

	if(mysql_num_rows($sth)>0){
		$rec = mysql_fetch_assoc($sth);
		$rec['Name']=replace_in_string($rec['Name']);

		foreach($rec as $key => $value){
			$in[strtolower($key)]=$rec[$key];
		}

		$in['category']=$rec['Title'];
		$in['size']=$rec['sizew']*$rec['sizeh']*$rec['sizel'];
		if($rec['Flexipago']>1){
		    $va['tooltip']="<script>$(function() { $('#flexipago').tooltip();});</script>";
		    $va['isflexipago']="Pague en ".$rec['Flexipago']." Mensualidades <img id=flexipago src='/images/help.png' title='Usted podra elegir la cantidad de pagos en la pantalla de confirmaci&oacute;n' >";
		}		
		$in['shippingprice']=shipping_box($in);
		$va['shippingprice']= format_price($in['shippingprice']);
			
		$tpl['pagetitle'] = $cfg['app_title'] . ' :: ' . $in['category'] . ' :: ' . $in['name'];
		$in['keywords'] = strip_tags($rec['Name'] . " " . $rec['Model'] . " ");
		if($rec['Description'] != ''){
		    $in['keywords'] .= strip_tags($rec['Description']); 
		}elseif($rec['SmallDescription'] != ''){
		    $in['keywords'] .= strip_tags($rec['SmallDescription']); 
		}

		$va['item_htmlprice'] = html_item_price($rec['ID_products']);
		$va['item_htmlshipping'] = html_item_shp($rec['ID_products']);
		$va['description'] = $rec['Description'];

		## Espacio para cargar pre landings
		$tpl['pre_landing'] = '';

		if(isset($in['fb']) and $cfg['usecoupons'] == 1 and is_promo_facebook($in['name_link'])){
			$tpl['pre_landing'] = 'cart/content/promo_facebook.html';
		}
			

		# Precio
		$in['item_price'] = format_price($in['sprice']);
		if(isset($cfg['promo_campaign']) and $cfg['promo_campaign']==1){
				if($in['memberprice'] > 0  and $in['memberprice'] < $in['sprice'])
				{
					$in['item_price'] = '<span style="text-decoration:line-through;">'. $in['item_price'] . '</span> - ' .format_price($in['memberprice']);
					$in['item_price'] .= ' &nbsp;<img src="/images/cart/promo_campaign.jpg">';
				}
		}elseif($usr['type'] == 'Membership' and $cfg['membership'] == 1){
				if($in['memberprice'] > 0  and $in['memberprice'] < $in['sprice'])
				{
					$in['item_price'] = '<span style="text-decoration:line-through;">'. $in['item_price'] . '</span> - ' .format_price($in['memberprice']);
					$in['item_price'] .= ' &nbsp;<img src="/images/cart/club.jpg">';
				}
		}

		## Facebook Like Button
		#$url = $cfg['signin_urlconfirm'] . $in['name_link'].'-a';
		$url = $cfg['facebook_url'];
		$va['facebook_like_button'] = get_facebook_like_button('',$url,array('ref'=> 'product_detail','width'=>'190'),array());
		$va['plusone']='<g:plusone href="'.$cfg['signin_urlconfirm'].$in['name_link'].'-a" size="medium" annotation="bubble" expandTo="right" width="70" ></g:plusone>';

		## Facebook Opengraph metatags
		$url = $cfg['signin_urlconfirm'] . $in['name_link'].'-a';
		$fb_opgraph=array('title' => $rec['Name'],'url' => $url);
		
		if (file_exists($cfg['path_imgmanf'].$rec['ID_products']."b1.gif") or file_exists($cfg['path_imgmanf'].$rec['ID_products'].'b1.jpg') or file_exists($cfg['path_imgmanf'].$rec['ID_products'].'b1.jpeg')){
				$fb_opgraph['image'] = $cfg['signin_urlconfirm'].'cgi-bin/showimages.cgi?id='.$rec['ID_products'].'&img=1&type=b&spict=1';
		}
		
		if (strlen($rec['SmallDescription']) > 10 ){
				$fb_opgraph['description'] = substr(strip_tags($rec['SmallDescription']),0,150).' ...';
		}elseif(strlen($rec['Description']) > 10 ){
				$fb_opgraph['description'] = substr(strip_tags($rec['Description']),0,150).' ...';
		}

		$va['facebook_opengraph'] = get_facebook_opgraph($fb_opgraph);
		

		##2x1 Promotion
		if(!empty($cfg['is2x1_valid']) and (stripos($cfg['products2x1'],$rec['ID_products'])!==false or (!empty($cfg['productsnot2x1']) and stripos($cfg['productsnot2x1'],$rec['ID_products'])===false)) and $rec['SPrice'] >= $cfg['products2x1_minprice']){
			$tpl['pre_landing']='objects/prelanding_2x1.html';

		}elseif (!empty($cfg['gifts_use']) and stripos($cfg['gifts_triggers'],$rec['ID_products']) !== false ) {
			$tpl['pre_landing']='objects/prelanding_gift.html';
		}


		## Si existe template para el producto, se carga
		if(isset($cfg['promo_campaign']) and $cfg['promo_campaign']==1 and is_readable($cfg['path_templates'] . 'cart/products/' . $rec['ID_products'] . '.promo_campaign.html')){
			$tpl['skel']="cart_product_cust.html";
			$in['srcfile']="/cgi-bin/nsc_admin/templates/sp/cart/products/".$rec['ID_products'].".promo_campaign.html";
			$tpl['filename'] = "cart/products/".$rec['ID_products'].".promo_campaign.html";

		}elseif($usr['type'] == 'Membership' and $cfg['membership'] == 1 and is_readable($cfg['path_templates'] . 'cart/products/' . $rec['ID_products'] . '.club.html')){
			$tpl['skel']="cart_product_cust.html";
			$in['srcfile']="/cgi-bin/nsc_admin/templates/sp/cart/products/".$rec['ID_products'].".club.html";
			$tpl['filename'] = "cart/products/".$rec['ID_products'].".club.html";

		}elseif (file_exists("$cfg[path_templates]cart/products/".$rec['ID_products'].".html") and is_file("$cfg[path_templates]cart/products/".$rec['ID_products'].".html")){
			$tpl['skel']="cart_product_cust.html";
			$in['srcfile']="/cgi-bin/nsc_admin/templates/sp/cart/products/".$rec['ID_products'].".html";
			$tpl['filename'] = "cart/products/".$rec['ID_products'].".html";

		}else{
		## Si no hay template, se carga default
			$in['srcfile']="/?cmd=show_description&id=$in[id_products]";
			$tpl['filename'] = $device['is_mobile_device'] ? "/content/vermas.html"  : "/cart/content/detail_product.html";
		}

		set_data_profiler($cfg['prof_viewproduct'], $rec['ID_products']);
		## Para ambos casos, se busca que existan productos relacionados 
		get_related_products($rec['ID_products']);
	}else{
	## No existe el producto
		check_404();
		$tpl['skel']= "broken.html"; //"cart_product.html";
		$in['message']=trans_txt("no_product");
		$in['srcfile']="/?cmd=show_description&id=$in[id_products]";
		$tpl['filename'] = $device['is_mobile_device'] ? "/content/no_product.html"  : "/cart/content/no_product.html";
		return -1;
	}

}

 function do_search(){
// --------------------------------------------------------
// Forms Involved: 
// Created on: 6 Apr 2010 17:02:39
// Author: MCC C. Gabriel Varela S.
// Description :   
// Parameters :
// Las Time Modified by RB on 05/10/2010: Se guardan los keywords de los clientes
// Last time modified by RB on 06/23/2010 : Se agrega precio de Membresia para Club Innova
// Last time modified by RB on 12/09/2010 : Se cambia link de la foto principal, ya no abre modal de fotos sino que va directo a la pagina
// Last time modified by RB on 03/18/2011 : Se agrega rel="nofollow" a links -e
//Last modified on 4/4/11 6:22 PM
//Last modified by: MCC C. Gabriel Varela S. :Se agrega validación de producto gratis para secret_cupon
//Last modified on 2 May 2011 11:59:17
//Last modified by: MCC C. Gabriel Varela S. : Se hace que también se condicione el mostrar el ícono de membership. Se incorpora promo_campaign
//Last modified on 17 May 2011 14:06:45
//Last modified by: MCC C. Gabriel Varela S. :Se incluye group by ID_products
//Last modified on 13 Jun 2011 17:23:49
//Last modified by: MCC C. Gabriel Varela S. :the sounds like statement is included
//Last modified on 14 Jun 2011 17:12:37
//Last modified by: MCC C. Gabriel Varela S. :full text search is implemented
//Last modified on 16 Jun 2011 16:24:47
//Last modified by: MCC C. Gabriel Varela S. :the keyword input is splited by space
//Last modified on 20 Jun 2011 11:34:39
//Last modified by: MCC C. Gabriel Varela S. :$wherein is corrected

	global $in,$cfg,$tpl,$usr,$device;

    set_data_profiler($cfg['prof_search'], $in['keyword']);
    set_data_profiler($cfg['prof_category'], $in['category']);
	$where="";
	$wherein="";
	$cadkeyword="";
	$item_price=0;


	## Mobile /PC Default templates
	$tpl['filename'] = $device['is_mobile_device'] ? "/content/lista.html"  : "/cart/content/results_home.html";
	$tpl['skel'] = $device['is_mobile_device'] ? $tpl['skel'] : "results_list.html";
	$cfg['ppl'] = $device['is_mobile_device'] ? $cfg['ppl_mobile'] : $cfg['ppl'];
	$cfg['ppp'] = $device['is_mobile_device'] ? $cfg['ppp_mobile'] : $cfg['ppp'];

	
	if(isset($in['id_customers'])and $in['id_customers']!='' and isset($in['id_orders']) and $in['id_orders']!=''){
		validate_customer($in['id_customers'],$in['id_orders']);
	}

	if($in['category']!=''){
//  		if($in[fromh]==1)
//  			$in[category]=utf8_decode($in[category]);
		$in['category']=mysql_real_escape_string($in['category']);
		if(preg_match("/\|/",$in['category']))
		{
			$where=$in['category'];
			$where = preg_replace("/\|/", "','", $where);
			$in['message'].=trans_txt('categ').": '$where'<br>\n";
			$where=" and Title in ('$where') ";
		}
		else
		{
			$in['message'].=trans_txt('categ').": $in[category]<br>\n";
			$where.=" and Title='$in[category]' ";
		}
	}if($in['keyword']!=''){
	    
		$inkeyword=preg_replace("/\"/", "", $in['keyword']);
		$inkeyword=preg_replace("/\'/", "", $inkeyword);
		$inkeyword=mysql_real_escape_string($inkeyword);
		$inkeyword=trim($inkeyword);
		$in['message'].=trans_txt('keyword').": $inkeyword<br>\n";
		$where.=" 
		and (0 ";
		#split $inkeyword
		$keywords_by_space=explode(" ", $inkeyword);
		#start cycle
		for($i=0;$i<count($keywords_by_space);$i++)
		{
			if(preg_match("/^de$|^la$|^el$|^y$|^en$|^para$|^in$|^te$|^and$/",$keywords_by_space[$i])==0)
			{
				$where.=" 
					or Model like '%$keywords_by_space[$i]%' 
					or Name like '%$keywords_by_space[$i]%' 
					or SmallDescription like '%$keywords_by_space[$i]%' 
					or Title like '%$keywords_by_space[$i]%' 
					or ID_products like '%$keywords_by_space[$i]%' 
					or concat(replace(Name,' ',''),replace(Model,' ',''),replace(SmallDescription,' ',''),replace(Title,' ','')) like '%$keywords_by_space[$i]%'
					or keyword like '%$keywords_by_space[$i]%' 
					or Model sounds like '$keywords_by_space[$i]' 
					or Name sounds like '$keywords_by_space[$i]' 
					or Title sounds like '$keywords_by_space[$i]'";
			}
		}
		$where.=")";
		$wherein="or (MATCH (sl_products.Model,sl_products.Name ) AGAINST ('$inkeyword') and $cfg[whereproducts])";
	}
//   	echo $where;
	$in['page']=intval($in['page']);
	if(!isset($in['page']) or $in['page']<=0)
		$in['page']=1;
	
	$in['ini']=($in['page']-1)*$cfg['ppp'];
	
	#$in[limit]=$in[ini]+$cfg[ppp];
	$sth = mysql_query("Select count(*) as total_records
from (Select 
				if(not isnull(sl_products_prior.SPrice)and sl_products_prior.SPrice!=0,sl_products_prior.SPrice,sl_products.SPrice)as SPrice,
				if(not isnull(sl_products_prior.MemberPrice)and sl_products_prior.MemberPrice > 0,sl_products_prior.MemberPrice,sl_products.MemberPrice)as MemberPrice,
				if(not isnull(sl_products_prior.Status)and sl_products_prior.Status!='',sl_products_prior.Status,sl_products.Status) as Status,
				if(not isnull(sl_products_w.Title)and sl_products_w.Title!='',sl_products_w.Title,if(not isnull(sl_categories.Title),sl_categories.Title,'".trans_txt('other')."'))as Title,
				sl_products.ID_products,
				if(not isnull(sl_products_prior.Name)and sl_products_prior.Name!='',sl_products_prior.Name,sl_products.Name) as Name,
				if(not isnull(sl_products_w.Name),sl_products_w.Name,'Other') as Name_link,
				if(not isnull(sl_products_prior.Model)and sl_products_prior.Model!='',sl_products_prior.Model,sl_products.Model) as Model,
				if(not isnull(sl_products_prior.SmallDescription)and sl_products_prior.SmallDescription!='',sl_products_prior.SmallDescription,sl_products.SmallDescription) as SmallDescription,
				if(not isnull(sl_products_prior.Description)and sl_products_prior.Description!='',sl_products_prior.Description,sl_products.Description) as Description,
				if(not isnull(sl_products_prior.Weight)and sl_products_prior.Weight!=0,sl_products_prior.Weight,sl_products.Weight) as Weight,
				if(not isnull(sl_products_prior.SizeW)and sl_products_prior.SizeW!=0 and sl_products_prior.SizeW!='',sl_products_prior.SizeW,sl_products.SizeW) as SizeW,
				if(not isnull(sl_products_prior.SizeH)and sl_products_prior.SizeH!=0 and sl_products_prior.SizeH!='',sl_products_prior.SizeH,sl_products.SizeH) as SizeH,
				if(not isnull(sl_products_prior.SizeL)and sl_products_prior.SizeL!=0 and sl_products_prior.SizeL!='',sl_products_prior.SizeL,sl_products.SizeL) as SizeL,
				if(not isnull(sl_products_prior.Flexipago)and sl_products_prior.Flexipago!=0,sl_products_prior.Flexipago,sl_products.Flexipago) as Flexipago,
				/*if(not isnull(sl_products_prior.FPPrice)and sl_products_prior.FPPrice!=0,sl_products_prior.FPPrice,sl_products.FPPrice) as FPPrice,*/
				0 as FPPrice,
				if(not isnull(sl_products_prior.PayType)and sl_products_prior.PayType!='',sl_products_prior.PayType,sl_products.PayType) as PayType,
				if(not isnull(sl_products_prior.edt)and sl_products_prior.edt!=0 and sl_products_prior.edt!='',sl_products_prior.edt,sl_products.edt) as edt,
				if(not isnull(sl_products_prior.ID_packingopts)and sl_products_prior.ID_packingopts!=0 and sl_products_prior.ID_packingopts!='',sl_products_prior.ID_packingopts,sl_products.ID_packingopts) as ID_packingopts,
				if(not isnull(sl_products_prior.Downpayment)and sl_products_prior.Downpayment!=0,sl_products_prior.Downpayment,sl_products.Downpayment) as Downpayment,
				if(not isnull(sl_products_prior.ChoiceName1)and sl_products_prior.ChoiceName1!='',sl_products_prior.ChoiceName1,sl_products.ChoiceName1) as ChoiceName1,
				if(not isnull(sl_products_prior.ChoiceName2)and sl_products_prior.ChoiceName2!='',sl_products_prior.ChoiceName2,sl_products.ChoiceName2) as ChoiceName2,
				if(not isnull(sl_products_prior.ChoiceName3)and sl_products_prior.ChoiceName3!='',sl_products_prior.ChoiceName3,sl_products.ChoiceName3) as ChoiceName3,
				if(not isnull(sl_products_prior.ChoiceName4)and sl_products_prior.ChoiceName4!='',sl_products_prior.ChoiceName4,sl_products.ChoiceName4) as ChoiceName4,
				if(not isnull(sl_products_prior.web_available)and sl_products_prior.web_available!='',sl_products_prior.web_available,sl_products.web_available) as web_available,
				keyword
			from sl_products
			left join sl_products_prior on(sl_products.ID_products=sl_products_prior.ID_products)
   and sl_products_prior.belongsto='$cfg[owner]'
			inner join sl_products_w on(sl_products.ID_products=sl_products_w.ID_products)
			left join sl_products_categories on(sl_products.ID_products=sl_products_categories.ID_products)
			left join sl_categories on (sl_products_categories.ID_categories=sl_categories.ID_categories)
			where $cfg[whereproducts] $wherein
			group by ID_products)as sl_products
where 1 $where;") or die("Query failed C6555555-1: " . mysql_error());
	$rec = mysql_fetch_assoc($sth);
	$in['total_records']=$rec['total_records'];


	$sth = mysql_query("Select * $cadkeyword
from (Select 
				if(not isnull(sl_products_prior.SPrice)and sl_products_prior.SPrice!=0,sl_products_prior.SPrice,sl_products.SPrice)as SPrice,
				if(not isnull(sl_products_prior.MemberPrice)and sl_products_prior.MemberPrice > 0,sl_products_prior.MemberPrice,sl_products.MemberPrice)as MemberPrice,
				if(not isnull(sl_products_prior.Status)and sl_products_prior.Status!='',sl_products_prior.Status,sl_products.Status) as Status,
				if(not isnull(sl_products_w.Title)and sl_products_w.Title!='',sl_products_w.Title,if(not isnull(sl_categories.Title),sl_categories.Title,'".trans_txt('other')."'))as Title,
				sl_products.ID_products,
				if(not isnull(sl_products_prior.Name)and sl_products_prior.Name!='',sl_products_prior.Name,sl_products.Name) as Name,
				if(not isnull(sl_products_w.Name),sl_products_w.Name,'Other') as Name_link,
				if(not isnull(sl_products_prior.Model)and sl_products_prior.Model!='',sl_products_prior.Model,sl_products.Model) as Model,
				if(not isnull(sl_products_prior.SmallDescription)and sl_products_prior.SmallDescription!='',sl_products_prior.SmallDescription,sl_products.SmallDescription) as SmallDescription,
				if(not isnull(sl_products_prior.Description)and sl_products_prior.Description!='',sl_products_prior.Description,sl_products.Description) as Description,
				if(not isnull(sl_products_prior.Weight)and sl_products_prior.Weight!=0,sl_products_prior.Weight,sl_products.Weight) as Weight,
				if(not isnull(sl_products_prior.SizeW)and sl_products_prior.SizeW!=0 and sl_products_prior.SizeW!='',sl_products_prior.SizeW,sl_products.SizeW) as SizeW,
				if(not isnull(sl_products_prior.SizeH)and sl_products_prior.SizeH!=0 and sl_products_prior.SizeH!='',sl_products_prior.SizeH,sl_products.SizeH) as SizeH,
				if(not isnull(sl_products_prior.SizeL)and sl_products_prior.SizeL!=0 and sl_products_prior.SizeL!='',sl_products_prior.SizeL,sl_products.SizeL) as SizeL,
				if(not isnull(sl_products_prior.Flexipago)and sl_products_prior.Flexipago!=0,sl_products_prior.Flexipago,sl_products.Flexipago) as Flexipago,
				/*if(not isnull(sl_products_prior.FPPrice)and sl_products_prior.FPPrice!=0,sl_products_prior.FPPrice,sl_products.FPPrice) as FPPrice,*/
				0 as FPPrice,
				if(not isnull(sl_products_prior.PayType)and sl_products_prior.PayType!='',sl_products_prior.PayType,sl_products.PayType) as PayType,
				if(not isnull(sl_products_prior.edt)and sl_products_prior.edt!=0 and sl_products_prior.edt!='',sl_products_prior.edt,sl_products.edt) as edt,
				if(not isnull(sl_products_prior.ID_packingopts)and sl_products_prior.ID_packingopts!=0 and sl_products_prior.ID_packingopts!='',sl_products_prior.ID_packingopts,sl_products.ID_packingopts) as ID_packingopts,
				if(not isnull(sl_products_prior.Downpayment)and sl_products_prior.Downpayment!=0,sl_products_prior.Downpayment,sl_products.Downpayment) as Downpayment,
				if(not isnull(sl_products_prior.ChoiceName1)and sl_products_prior.ChoiceName1!='',sl_products_prior.ChoiceName1,sl_products.ChoiceName1) as ChoiceName1,
				if(not isnull(sl_products_prior.ChoiceName2)and sl_products_prior.ChoiceName2!='',sl_products_prior.ChoiceName2,sl_products.ChoiceName2) as ChoiceName2,
				if(not isnull(sl_products_prior.ChoiceName3)and sl_products_prior.ChoiceName3!='',sl_products_prior.ChoiceName3,sl_products.ChoiceName3) as ChoiceName3,
				if(not isnull(sl_products_prior.ChoiceName4)and sl_products_prior.ChoiceName4!='',sl_products_prior.ChoiceName4,sl_products.ChoiceName4) as ChoiceName4,
				if(not isnull(sl_products_prior.web_available)and sl_products_prior.web_available!='',sl_products_prior.web_available,sl_products.web_available) as web_available,
				keyword
			from sl_products
			left join sl_products_prior on(sl_products.ID_products=sl_products_prior.ID_products)
   and sl_products_prior.belongsto='$cfg[owner]'
			inner join sl_products_w on(sl_products.ID_products=sl_products_w.ID_products)
			left join sl_products_categories on(sl_products.ID_products=sl_products_categories.ID_products)
			left join sl_categories on (sl_products_categories.ID_categories=sl_categories.ID_categories)
			where $cfg[whereproducts] $wherein
			group by ID_products)as sl_products
where 1 $where
limit $in[ini],$cfg[ppp];") or die("Query failed C6555555-2: " . mysql_error());


	//echo "$msg<br>\n";
	if(isset($in['keyword']) and $in['keyword']!= ''){
			#echo "si entra $in[keyword]" . mysql_num_rows($sth);
			do_save_keyword($in['keyword'],mysql_num_rows($sth));	
	}
	
	if(mysql_num_rows($sth)>1 or $in['page']>1){
		$cg=0;

		while ($rec = mysql_fetch_assoc($sth)){
			//Aqui se llamaria a little_product
			//Imagen, Nombre, Precio
			//Cambiar signos de mas por otra cosa
			
			#$link=specialsum($rec[Name_link],0);
			$rec['Name']=replace_in_string($rec['Name']);
			$link=htmlentities($rec['Name_link']);

			
			# Precio
			$item_price = format_price($rec['SPrice']);
			if(isset($cfg['promo_campaign']) and $cfg['promo_campaign']==1){
					if($rec['MemberPrice'] > 0 and $rec['MemberPrice'] < $rec['SPrice'])
					{
						$item_price = '<span style="text-decoration:line-through;">'. $item_price . '</span> - ' . format_price($rec['MemberPrice']);
						$item_price .= ' &nbsp;<img src="/images/cart/promo_campaign.jpg"  border="0">';
					}
			}elseif($usr['type'] == 'Membership' and $cfg['membership'] == 1){
					if($rec['MemberPrice'] > 0 and $rec['MemberPrice'] < $rec['SPrice'])
					{
						$item_price = '<span style="text-decoration:line-through;">'. $item_price . '</span> - ' . format_price($rec['MemberPrice']);
						$item_price .= ' &nbsp;<img src="/images/cart/club.jpg" border="0">';
					}
			}
			
			/* 2x1 Promotion */
			if(!empty($cfg['is2x1_valid'])){
				$is2x1 = ($cfg['two_for_one_use']==1 and (stripos($cfg['products2x1'],$rec['ID_products'])!==false or (!empty($cfg['productsnot2x1']) and stripos($cfg['productsnot2x1'],$rec['ID_products'])===false)) and $rec['SPrice'] >= $cfg['products2x1_minprice'] ) ? 
						'<center><img src="/images/promociones/mini_2x1.png" title="2x1 en '.$rec['Name'].'" border="0"></center>' : 
						'<center><img src="/images/promociones/mini.png" border="0"></center>';
			}

			/* Gifts  */
			$is2x1 = (!empty($cfg['gifts_use']) and stripos($cfg['gifts_triggers'],$rec['ID_products']) !== false ) ?
						'<center><img src="/images/promociones/mini_gift.png" title="Llevate un regalo en '.$rec['Name'].'"  border="0"></center>' : 
						'<center><img src="/images/promociones/mini.png" border="0"></center>';


			if($device['is_mobile_device']){

				###############################################################
				###############################################################
				###############################################################
				##### Mobile Content
				###############################################################
				###############################################################
				###############################################################

				$in['results'].=  '<a href="/'.$link.'-a" class="prodmain">	
									<table cellpadding="0" cellspacing="0" width="100%">
										<td align="center" valign="top" width="40%">
											<img src="/cgi-bin/showimages.cgi?id='.$rec['ID_products'].'&img=1&type=b&spict=1" width="95%" align="left" border=0>
										</td>
										<td align=center valign=top width=60%>
										<table width=90% cellpadding=0 cellspacing=0>
											<td align=left>
												<span style="height:40px;display:block;overflow:hidden;"><font class=mbtxt>
												<font class=protxt><b>'.$rec['Name'].'</b></span>
												<font class=protxt>Código: <b>'.$rec['ID_products'].'</b> <br>
												<font class=protxt>Precio: <b>'. $item_price .'</b> <br>
											</td>
										</table>
										<center>
										<a href="/'.$link.'-e"><img src="/mobile/images/comprar.jpg" border=0 width=80%></a>
										</td>
									</table>
								</a>

								<img src="/mobile/images/hr.gif" width=100% height=1px style="margin-bottom:5px;margin-top:15px;" border=0><br>';


			}else{

				if($cg %$cfg['ppl']==0){
					$in['results'].="<tr>";
				}
				###############################################################
				###############################################################
				###############################################################
				##### PC/Laptop Content
				###############################################################
				###############################################################
				###############################################################

				$in['results'].= "<td  class='menuoff' onmouseover=className='menuon'; onmouseout=className='menuoff';  align=center>
									<a href=\"http://$cfg[maindomain]/$link-a\" class=prod>
										<img src='/cgi-bin/showimages.cgi?id=".$rec['ID_products']."&img=1&type=b&spict=1' alt='' style='border:0px;margin-top:7px;margin-bottom:7px;' width=190px height=190px>
										$is2x1
										<font class=proname>$rec[Name]</font>
										<font class=protxt>Precio</ont><br>
										<font class=proprice>". $item_price ."</font><br>
		
		      							<table cellpadding=0 cellspacing=3 style='margin-top:7px;'>
											<tr>
												<td align=center colspan=2><!-- Agregar -->
													<a href=\"/$link-e\" class='l1_text' rel='nofollow'><img src=images/add.jpg border=0></a>
												</td>
											</tr>
											<tr>
												<td align=center><!-- Fotos -->
													<a href=\"cgi-bin/showimages.cgi?id=$rec[ID_products]&pict=1\" Title='Images' rel='rel$rec[ID_products]' class='l1_text'><img src=images/1f.jpg border=0></a>
												</td>
												<td align=center><!-- Mas Info -->
													<a href=\"/$link-a\" class='l1_text'><img src=images/1mi.jpg border=0></a>
												</td>
											</tr>
										</table>
									</a>
								</td> \n";

				if($cg %$cfg['ppl']==$cfg['ppl']-1)
					$in['results'].="</tr>
					<tr>
						<td colspan='$cfg[ppl]' style='border-bottom:1px solid #ccc;'>&nbsp;&nbsp;&nbsp;</td>
					</tr>";
			}

			unset($is2x1);
			$cg++;
			$tpl['pagetitle'] = $cfg['app_title'] . ' :: ' . $rec['Title'];
			
		}
		
		//load_object('/skeleton/cart.html');
	}elseif(mysql_num_rows($sth)==1){
		$rec = mysql_fetch_assoc($sth);
		$in['product']=$rec['ID_products'];

		## Mobile /PC Default templates
		$tpl['filename'] = $device['is_mobile_device'] ? "/content/vermas.html"  : "/cart/content/detail_product.html";
		$tpl['skel'] = $device['is_mobile_device'] ? $tpl['skel'] : "cart_product.html";
		//load_object('/skeleton/cart_product.html');
		do_for_one_product();
	}else{
		check_404();
		$tpl['skel']= "broken.html"; //"cart_product.html";
		$in['message']=trans_txt("no_product");
		$in['srcfile']="/?cmd=show_description&id=$in[id_products]";
		$tpl['filename'] = $device['is_mobile_device'] ? "/content/no_product.html"  : "/cart/content/no_product.html";
		return -1;
	}
}

function create_session(){
// --------------------------------------------------------
// Forms Involved: 
// Created on: 9 Apr 2010 15:39:45
// Author: MCC C. Gabriel Varela S.
// Description :   
// Parameters :
	global $cfg;
	if(session_id()==""){
		ini_set('session.save_path', $cfg[auth_dir]);	
		session_start();
		session_name("nsc_session");

		if (!isset($_SESSION[total_qty])){
			$_SESSION[total_qty] = 0;
		}
		if (!isset($_SESSION[total_price])){
			$_SESSION[total_price] = 0;
		}
	}

}

function paytypes_for_products(){
# --------------------------------------------------------

# Author: Jose Ramirez Garcia
# Created on: 
# Last Modified on: 11/12/2008
# Last Modified by: It search valid pay types and match with cses pay type
# Description : 
# Forms Involved: 
# Parameters : 
# Last Modified on: 11/14/08 13:01:48
# Last Modified by: MCC C. Gabriel Varela S: Se cambia para contemplar sólo los productos válidos dentro del carrito
# Last Modified RB: 10/09/09  16:14:14 -- Se valida tipo de pago para promos

	global $cfg,$cses;
	$cadtypespay="";
	$dbpaytypes=array();
	$product_pay_types=array();
	$cfg_paytypes = explode("$|",$cfg['paypriority']);
	$j=0;
	$opt = array();


	for($i=1;$i<=$cses['items_in_basket'];$i++)
	{
		$db_pay_types="";
		$prelated=0;
		$stype=0;
		if($cses['items_'.$i.'_id'] and $cses['items_'.$i.'_qty']){
			$j++;
	#		$cadtypespay.=$cses['items_'.$i.'_paytype'];
			$tprod='id';
			if($cses['items_'.$i.'_promo']) 
				$tprod = 'promo';
			$db_pay_types = &load_name('sl_products_prior','ID_products',substr($cses['items_'.$i.'_'.$tprod],3,6),'PayType');
			if($db_pay_types=="")
				$db_pay_types = &load_name('sl_products','ID_products',substr($cses['items_'.$i.'_'.$tprod],3,6),'PayType');

			## Check Wheter it's allowed to pay with paypal and google checkout
			$prelated = &load_name('sl_products_prior','ID_products',substr($cses['items_'.$i.'_'.$tprod],3,6),'ID_services_related');
			if(strlen($prelated) < 4)
				$prelated = &load_name('sl_products','ID_products',substr($cses['items_'.$i.'_'.$tprod],3,6),'ID_services_related');
			if(strlen($prelated) == 4){
				$stype = &load_name('sl_services','ID_services',$prelated,'ServiceType');
			}
			#echo substr($cses['items_'.$i.'_'.$tprod],3,6)." -- $tprod -- $db_pay_types - $stype";
			($stype === 'Refill') and ($db_pay_types = str_replace(array("|paypal","|google"),array("",""),$db_pay_types));
			#echo " -- $db_pay_types<br>";
			$dbpaytypes = explode("|",$db_pay_types);
			$cont=0;
			foreach ($dbpaytypes as $key=>$value ) {
				$cont++;
				$product_pay_types[$j][$cont] .= $value;
			}
		}
	}
	if(!$cadtypespay){
		$inter = paytypes_intersection($product_pay_types);
		foreach($inter as $key=>$value){
			$cadtypespay.=$value."|";
		}
	}
	
	if(!$cadtypespay){
		$con_u=0;
		$con_o=0;
		$var = "";
		$ones = "";
		$unique = array();
		$ones = array();
		for ($a=1;$a<=count($product_pay_types);$a++){
			if(count($product_pay_types[$a]) == 1){
				$con_u++;
				$unique[$con_u] = $product_pay_types[$a][1];
			}
			$con_o++;
			$ones[$con_o] = $product_pay_types[$a][1];
		}
		if(count($unique) > 0){
			$min = "";
			for ($b=1;$b<=count($unique);$b++){
				$pr = strpos($cfg[paypriority],$unique[$b]);
				if($pr !== false){
					if(!$min || ($min && $pr < strpos($cfg[paypriority],$min))){
						$min = $unique[$b];
					}
				}
			}
			$all_paytypes = "";
			for ($d=1;$d<=count($product_pay_types);$d++){
				for ($e=1;$e<=count($product_pay_types[$d]);$e++){
					if(preg_match("/$product_pay_types[$d][$e]/",$all_paytypes)==0){
						$all_paytypes .= $product_pay_types[$d][$e]."|";
					}
				}
			}
			$in_paytypes = explode("|",$all_paytypes);
			$pr_limit = strpos($cfg[paypriority],$min);
			for($k=count($in_paytypes); $k>=0; $k--){
				$priority = strpos($cfg[paypriority],$in_paytypes[$k]);
				if($priority !== false && $priority <= $pr_limit){
					$cadtypespay .= $in_paytypes[$k]."|";
				}
			}
		} else {
			$max="";
			$cadtypespay = "";
			for ($o=1;$o<=count($ones);$o++){
				$pr_it = strpos($cfg[paypriority],$ones[$o]);
				if(!$max || ($max && $pr_it > strpos($cfg[paypriority],$max))){
					$max = $ones[$o];
				}
			}
			$all_paytypes = "";
			for ($d=1;$d<=count($product_pay_types);$d++){
				for ($e=1;$e<=count($product_pay_types[$d]);$e++){
					if(preg_match("/$product_pay_types[$d][$e]/",$all_paytypes)==0){
						$all_paytypes .= $product_pay_types[$d][$e]."|";
					}
				}
			}			
			$in_paytypes = explode("|",$all_paytypes);
			$pr_max = strpos($cfg[paypriority],$max);
			for($n=count($in_paytypes); $n>=0; $n--){
				$priority_max = strpos($cfg[paypriority],$in_paytypes[$n]);
				if($priority_max !== false && $priority_max <= $pr_max){
					$cadtypespay .= $in_paytypes[$n]."|";
				}
			}
		}
	}
	
	return $cadtypespay;
}	

function paytypes_intersection($arr){
# --------------------------------------------------------

# Author: Jose Ramirez Garcia
# Created on: 
# Last Modified on: 11/12/2008
# Last Modified by: 
# Description : 
# Forms Involved: 
# Parameters : 
# Last Modified by RB on 08/02/2010: Se corrgige funcion para devolver solo los tipos de pago de interseccion

	global $cfg;
	$inters = array();
	$res = 0;
	$cont = array();
	for ($a=1;$a<=count($arr);$a++){
		for ($b=1;$b<=count($arr[$a]);$b++){
			$num = prod_pay_priority_to_num($arr[$a][$b]);
			$cont[$num]++;
		}
	}
#print_r($cont);
	$cfg_paytypes = explode("$|",$cfg['paypriority']);
	for($i=count($cfg_paytypes) -1; $i>=0; $i--){
		#echo "$i--" .$cfg_paytypes[$i] ."<br>". $cont[$i] ."==". count($arr) ."|| (". count($inters) ."> 0 && ". $cont[$i] ."> 0)<br><br>";
		if($cont[$i] == count($arr) /*|| (count($inters) > 0 && $cont[$i]>0)*/){
			$res++;
			$inters[$res]= $cfg_paytypes[$i];
		}
	}
	return $inters;
}


function prod_pay_priority_to_num($str){
# --------------------------------------------------------

# Author: Jose Ramirez Garcia
# Created on: 
# Last Modified on: 11/12/2008
# Last Modified by: 
# Description : 
# Forms Involved: 
# Parameters : 

	global $cfg;
	$cfg_paytypes = explode("$|",$cfg['paypriority']);
	for ($i=0;$i<count($cfg_paytypes);$i++){
		if(strtolower($str) == strtolower($cfg_paytypes[$i])){
			return $i;
		}
	}
	return "";
}

function display_paytypesav(){
# --------------------------------------------------------
# Forms Involved: 
# Created on: 04/14/10 15:35:14
# Author: MCC C. Gabriel Varela S.
# Description :   
# Parameters :
	global $cfg,$cses,$va;
	$cadtypespay = paytypes_for_products();

	if(($cfg['paytypescc'] and preg_match("/Credit-Card/",$cadtypespay)!=0)or($cfg[paytypescc] and $cadtypespay =="" and $cses[servis_in_basket]>0))
		$va['avpaytypes'] .= "<input class=\"radio\" value=\"Credit-Card\" name=\"paytype\" id=\"paytype\" onfocus=\"focusOn( this )\" onblur=\"focusOff( this )\" onclick=\"show_sub(this.value)\" type=\"radio\"> ".trans_txt('creditcard') .'&nbsp;&nbsp;&nbsp;';
	if (($cfg['paytypeschk'] and preg_match("/Check/",$cadtypespay)!=0)or($cfg[paytypeschk] and $cadtypespay =="" and $cses[servis_in_basket]>0))
		$va['avpaytypes'] .= "<input class=\"radio\" value=\"check\" name=\"paytype\" id=\"paytype\" onfocus=\"focusOn( this )\" onblur=\"focusOff( this )\" onclick=\"show_sub(this.value)\" type=\"radio\">".trans_txt('check')." &nbsp;&nbsp;&nbsp;";
	if (($cfg['paytypesmo'] and preg_match("/Money-Order/",$cadtypespay)!=0)or($cfg[paytypesmo] and $cadtypespay =="" and $cses[servis_in_basket]>0))
		$va['avpaytypes'] .= "<input class=\"radio\" value=\"mo\" name=\"paytype\" id=\"paytype\" onfocus=\"focusOn( this )\" onblur=\"focusOff( this )\" onclick=\"show_sub(this.value)\" type=\"radio\">".trans_txt('mo')." &nbsp;&nbsp;&nbsp;";
	if (($cfg['paytypeswu'] and preg_match("/WesternUnion/",$cadtypespay)!=0)or($cfg[paytypeswu] and $cadtypespay =="" and $cses[servis_in_basket]>0))
		$va['avpaytypes'] .= "<input class=\"radio\" value=\"wu\" name=\"paytype\" id=\"paytype\" onfocus=\"focusOn( this )\" onblur=\"focusOff( this )\" onclick=\"show_sub(this.value)\" type=\"radio\">".trans_txt('wu')." &nbsp;&nbsp;";
	if (($cfg['paytypeslay'] and preg_match("/Layaway/",$cadtypespay)!=0)or($cfg[paytypeslay] and $cadtypespay =="" and $cses[servis_in_basket]>0))
		$va['avpaytypes'] .= "<input class=\"radio\" value=\"lay\" name=\"paytype\" id=\"paytype\" onfocus=\"focusOn( this )\" onblur=\"focusOff( this )\" onclick=\"show_sub(this.value)\" type=\"radio\">".trans_txt('lay')."&nbsp;&nbsp;&nbsp;
								<input class=\"radio\" value=\"laymo\" name=\"paytype\" id=\"paytype\" onfocus=\"focusOn( this )\" onblur=\"focusOff( this )\" onclick=\"show_sub(this.value)\" type=\"radio\">".trans_txt('laymo')."&nbsp;&nbsp;&nbsp;";
	if (($cfg['paytypescod'] and preg_match("/COD/",$cadtypespay)!=0)or($cfg['paytypescod'] and $cadtypespay =="" and $cses[servis_in_basket]>0))
		$va['avpaytypes'] .= "<input class=\"radio\" value=\"COD\" name=\"paytype\" id=\"paytype\" onfocus=\"focusOn( this )\" onblur=\"focusOff( this )\" onclick=\"show_sub(this.value)\" type=\"radio\"> ".trans_txt('cod').'&nbsp;&nbsp;&nbsp;';

	$va['avpaytypes'] .= "<br><br>";

	if (($cfg['paytypespaypal'] and preg_match("/paypal/i",$cadtypespay)!=0)or($cfg['paytypespaypal'] and $cadtypespay =="" and $cses['servis_in_basket']>0))
		$va['avpaytypes'] .= '<input class="radio" value="paypal" name="paytype" id="paytype" onfocus="focusOn( this )" onblur="focusOff( this )" onclick="show_sub(this.value)" type="radio">&nbsp;<img src="https://www.paypal.com/en_US/i/logo/PayPal_mark_37x23.gif" style="margin-right:7px;"><!--<span style="font-size:11px; font-family: Arial, Verdana;">'. trans_txt('paypal_slogan').'</span>-->';
}


function is_owner($type='orders',$value=0){
	global $usr,$cfg;	
	$valid=-1;

	if($type=='orders'){
		$sth = mysql_query("Select IF(ID_customers = '".$usr['id_customers']."',1,-1) FROM sl_orders WHERE ID_orders='$value'; ");
		if($count=mysql_num_rows($sth) > 0){
			$valid = mysql_result($sth,0);
		}
	}elseif($type=='techsupport'){
		$id_parent;
		$id_parent = load_name('nsc_customers_support','ID_customers_support',$value,'ID_parent');
		($id_parent > 0) and ($value = $id_parent);
		$sth = mysql_query("Select IF(ID_customers = '".$usr['id_customers']."',1,-1) FROM nsc_customers_support WHERE ID_customers_support = '$value' ;");
		if($count=mysql_num_rows($sth) > 0){
			$valid = mysql_result($sth,0);
		}
	}

	($value == 0) and ($valid = -1);    
	return $valid;
}


function build_multi_promo($num=1,$breakline=1){
# --------------------------------------------------------
# Forms Involved: 
# Created on: 04/14/10 15:35:14
# Author: Roberto Barcenas
# Description :  Imprime multi promos de manera aleatoria a partir de los elementos de la carpeta /images/promos que empiecen con el id del producto. 
# Parameters : num= numero de promos a imprimir (1 por defecto)
# Las time Modified by RB on 06/24/2010 : Se modifica para leer del directorio club las promociones. Aplica para Miembros Club Innova
//Last modified on 2 May 2011 13:07:49
//Last modified by: MCC C. Gabriel Varela S. : Se incorpora promo_campaign
	
		global $cfg,$usr,$va;

		#$promo_folder = $cfg[path_promo_template] . $usr[pref_language] . "/functions/promo/";
		$promo_folder = $cfg['path_images'] . "promos/";
		(isset($cfg['promo_campaign']) and $cfg['promo_campaign']==1 and is_dir($promo_folder . 'promo_campaign') and count(scandir($promo_folder . 'promo_campaign')) > 2) and ($promo_folder .= 'promo_campaign/');
		($usr['type'] == 'Membership' and $cfg['membership'] == 1 and is_dir($promo_folder . 'club') and count(scandir($promo_folder . 'club')) > 2) and ($promo_folder .= 'club/');

		if(is_dir($promo_folder)){
			
			$tfiles = count(scandir($promo_folder));
			
			if($tfiles > 3){

				$my_array= array();
				$tries=0;
				$pattern = "/^\d{6}/";
				while($num > 0 or $tries >= 3){
					$my_temp_array = scandir($promo_folder);
					
					if(count($my_temp_array) > 3){
						do{
							$file = $my_temp_array[rand(0,$tfiles-1)];
						}while(!preg_match($pattern,$file) or (in_array($file,$my_array) and $tfiles-3 > count($my_array)));
						  
						array_push($my_array,$file);
						$data_file = explode("_",$file);
						$file = explode(".",$file);
						$query = build_do_for_one_product_query("Name_link","AND sl_products.ID_products = $data_file[0] ");

						$sth = mysql_query($query);
						list($link) = mysql_fetch_row($sth);
						$link=specialsum($link,0);
						$link=utf8_decode($link);
						$va['item_price'] = html_item_price($data_file[0]);

						## Club?
						(strstr($promo_folder,'club')) and ($file[0] = 'club/' . $file[0]);

						echo run_port_function(array('promo_link',$file[0],"$link-a"));
						if($breakline==1)
							echo '<div style="margin-top:11px;margin-bottom:11px;"><img alt=""  border="0"  src="images/line2.jpg" width="286"></div>';
						$num--;
					
					}else{
						$tries++;
					}
				}
			}
		}else{
			echo "$promo_folder no es folder";
		}
}

function build_do_for_one_product_query($rows='*',$where=''){
#-----------------------------------------------------------#
# Las time modified by RB on 06/23/2010 : Se agrega precio de Miembro Club Innova

	global $cfg;	
	
	return "Select $rows 
from (Select 
				if(not isnull(sl_products_prior.SPrice)and sl_products_prior.Sprice!=0,sl_products_prior.SPrice,sl_products.SPrice)as SPrice,
				if(not isnull(sl_products_prior.MemberPrice)and sl_products_prior.MemberPrice > 0,sl_products_prior.MemberPrice,sl_products.MemberPrice)as MemberPrice,
				if(not isnull(sl_products_prior.Status)and sl_products_prior.Status!='',sl_products_prior.Status,sl_products.Status) as Status,
				if(not isnull(sl_products_w.Title)and sl_products_w.Title!='',sl_products_w.Title,if(not isnull(sl_categories.Title),sl_categories.Title,'".trans_txt('other')."'))as Title,
				sl_products.ID_products,
				if(not isnull(sl_products_prior.Name)and sl_products_prior.Name!='',sl_products_prior.Name,sl_products.Name) as Name,
				if(not isnull(sl_products_w.Name),sl_products_w.Name,'Other') as Name_link,
				if(not isnull(sl_products_prior.Model)and sl_products_prior.Model!='',sl_products_prior.Model,sl_products.Model) as Model,
				if(not isnull(sl_products_prior.SmallDescription)and sl_products_prior.SmallDescription!='',sl_products_prior.SmallDescription,sl_products.SmallDescription) as SmallDescription,
				if(not isnull(sl_products_prior.Description)and sl_products_prior.Description!='',sl_products_prior.Description,sl_products.Description) as Description,
				if(not isnull(sl_products_prior.Weight)and sl_products_prior.Weight!=0,sl_products_prior.Weight,sl_products.Weight) as Weight,
				if(not isnull(sl_products_prior.SizeW)and sl_products_prior.SizeW!=0 and sl_products_prior.SizeW!='',sl_products_prior.SizeW,sl_products.SizeW) as SizeW,
				if(not isnull(sl_products_prior.SizeH)and sl_products_prior.SizeH!=0 and sl_products_prior.SizeH!='',sl_products_prior.SizeH,sl_products.SizeH) as SizeH,
				if(not isnull(sl_products_prior.SizeL)and sl_products_prior.SizeL!=0 and sl_products_prior.SizeL!='',sl_products_prior.SizeL,sl_products.SizeL) as SizeL,
				if(not isnull(sl_products_prior.Flexipago)and sl_products_prior.Flexipago!=0,sl_products_prior.Flexipago,sl_products.Flexipago) as Flexipago,
				/*if(not isnull(sl_products_prior.FPPrice)and sl_products_prior.FPPrice!=0,sl_products_prior.FPPrice,sl_products.FPPrice) as FPPrice,*/
				0 as FPPrice,
				if(not isnull(sl_products_prior.PayType)and sl_products_prior.PayType!='',sl_products_prior.PayType,sl_products.PayType) as PayType,
				if(not isnull(sl_products_prior.edt)and sl_products_prior.edt!=0 and sl_products_prior.edt!='',sl_products_prior.edt,sl_products.edt) as edt,
				if(not isnull(sl_products_prior.ID_packingopts)and sl_products_prior.ID_packingopts!=0 and sl_products_prior.ID_packingopts!='',sl_products_prior.ID_packingopts,sl_products.ID_packingopts) as ID_packingopts,
				if(not isnull(sl_products_prior.Downpayment)and sl_products_prior.Downpayment!=0,sl_products_prior.Downpayment,sl_products.Downpayment) as Downpayment,
				if(not isnull(sl_products_prior.ChoiceName1)and sl_products_prior.ChoiceName1!='',sl_products_prior.ChoiceName1,sl_products.ChoiceName1) as ChoiceName1,
				if(not isnull(sl_products_prior.ChoiceName2)and sl_products_prior.ChoiceName2!='',sl_products_prior.ChoiceName2,sl_products.ChoiceName2) as ChoiceName2,
				if(not isnull(sl_products_prior.ChoiceName3)and sl_products_prior.ChoiceName3!='',sl_products_prior.ChoiceName3,sl_products.ChoiceName3) as ChoiceName3,
				if(not isnull(sl_products_prior.ChoiceName4)and sl_products_prior.ChoiceName4!='',sl_products_prior.ChoiceName4,sl_products.ChoiceName4) as ChoiceName4,
				if(not isnull(sl_products_prior.web_available)and sl_products_prior.web_available!='',sl_products_prior.web_available,sl_products.web_available) as web_available
			from sl_products
			left join sl_products_prior on(sl_products.ID_products=sl_products_prior.ID_products)
   and sl_products_prior.belongsto='$cfg[owner]'
			inner join sl_products_w on(sl_products.ID_products=sl_products_w.ID_products)
			left join sl_products_categories on(sl_products.ID_products=sl_products_categories.ID_products)
			left join sl_categories on (sl_products_categories.ID_categories=sl_categories.ID_categories)
			where $cfg[whereproducts])as sl_products
where 1 $where;";

}


function show_products_payments($i,$onepay,$price,$fpprice,$str_disc){
# --------------------------------------------------------
# Created on: 23/jun/2008 09:40:18 AM GMT -06:00
# Last Modified on: 7/7/2008 6:23:03 PM
# Last Modified by: CH
# Author: MCC C. Gabriel Varela S.
# Description : Desplegar„1¤7las opciones de pago para productos
# Parameters : $i: número de registro actual
#		$str_disc: Descuento en caso de existir
#		$price: Precio del producto actual
# Last Modified on: 07/24/08 12:08:44
# Last Modified by: MCC C. Gabriel Varela S: Se incluye parámetro restartpayments para poner todos los pagos en 1 pago
# Last Modified on: 10/21/08 16:47:06
# Last Modified by: MCC C. Gabriel Varela S: Se corrige que se ponga downpayment 1 para pagos mensuales y semanales
# Last Modified on: 10/22/08 10:10:39
# Last Modified by: MCC C. Gabriel Varela S: Si se cumple que el tipo de pago de la orden no es lay, y además el producto no tiene tipo de pago layaway, entonces se muestra la opción de pago de contado
# Last Modified on: 10/23/08 09:19:04
# Last Modified by: MCC C. Gabriel Varela S: Se habilita un solo pago para layaway
# Last Modified on: 10/28/08 14:52:09
# Last Modified by: MCC C. Gabriel Varela S: Siempre se ofrecen pagos semanales y quincenales al elegir Lay-away. También se quitan los paréntesis cuando no hay descuento
# Last Modified on: 10/29/08 09:32:11
# Last Modified by: MCC C. Gabriel Varela S: Se muestran las opciones de lay-away sólo cuando el producto tiene esa forma de pago y además se eligi„1¤7esa forma de pago en la orden.
# Last Modified on: 10/30/08 10:31:21
# Last Modified by: MCC C. Gabriel Varela S: Se hace que ya no exista downpayment del 7% para pagos quincenales y semanales. También se habilita weekly 2 en caso de que haya lay-away. Se deja sólo opción basada en 52 semanas
# Last Modified on: 12/18/08 11:43:58
# Last Modified by: MCC C. Gabriel Varela S: Se muestra descuento de membresía en pagos.
# Last Modified on: 08/28/09 09:41:10
# Last Modified by: MCC C. Gabriel Varela S: Se pone denominador como 1 en caso de no existir.


global $cfg,$cses,$in;
	
	#($str_disc == "") and ($str_disc=" ($str_disc) ");
	if($in['restartpayments']==1)
	{
		$cses['items_'.$i.'_payments']=1;
		$cses['dayspay']=1;
	}
	
		$output = '<SELECT size="1" name="fpago'. $i . $cses['items_'.$i.'_id'].'" onFocus="focusOn( this )" onBlur="focusOff( this )" onChange="recharge(this);">'; 
		
		if(1)#$cses['items_'.$i.'_paytype'] !~ /Layaway/ and $cses['paytype']ne"lay")
		{
			### Pago Contado
			$output .=  '<option value="1" '; 
			($cses['items_'.$i.'_payments'] == '1') and ($output .= " selected "); 
			$output .= '>Pago 1 Exhibición : '. format_price($onepay) . $str_disc ."</option>\n";
		}
		
		### 3 Payments - Pago contado
		if ($cfg{'fp3promo'}){
			$output .= '<option value="3c" '; 
			($cses['items_'.$i.'_payments'] == '3c') and ($output .= " selected "); 
			$output .= '> 3 Pagos (0-15-30 Dias) '. format_price($onepay/3) ."</option>\n";
		}
		
		### Weekly
#		if ($cfg{'fpweekly'} or (stristr($cses['items_'.$i.'_paytype'],"Layaway") != FALSE and $cses['paytype']eq'lay')){
#		if($cses['items_'.$i.'_downpayment']>0)# or $cses{'items_'.$i.'_downpayment1'}>0)
#		{
#			#$pagoini="Pago Inicial ".&format_price($cses['items_'.$i.'_downpayment']+$cses{'items_'.$i.'_downpayment1'})." + ";
#			$pagoini="Pago Inicial ".&format_price($cses['items_'.$i.'_downpayment'])." + ";
#		}
#		$fpprice=$price if($fpprice==0 or !$fpprice);
#		#$output .= qq|<option value=\"|.$cses['items_'.$i.'_fpago']*4 .qq|\"|; ($cses['items_'.$i.'_payments'] eq $cses['items_'.$i.'_fpago']*4) and ($output .= " selected "); $output.= "> $pagoini " . ($cses['items_'.$i.'_fpago']*4) . " Pagos semanales de " . &format_price(($fpprice-$cses['items_'.$i.'_downpayment']-$cses{'items_'.$i.'_downpayment1'})/$cses['items_'.$i.'_fpago']/4) .qq|</option>\n|;
#		$output .= qq|<option value=\"|.$cses['items_'.$i.'_fpago']*4 .qq|\"|; ($cses['items_'.$i.'_payments'] eq $cses['items_'.$i.'_fpago']*4) and ($output .= " selected "); $output.= "> $pagoini " . ($cses['items_'.$i.'_fpago']*4) . " Pagos semanales de " . &format_price(($fpprice-$cses['items_'.$i.'_downpayment'])/$cses['items_'.$i.'_fpago']/4) .qq|</option>\n|;
#		}
		
		### Weekly2
		if ($cfg['f2pweekly'] or (stristr($cses['items_'.$i.'_paytype'],"Layaway") != FALSE and $cses['paytype'] == 'Layaway'))
		{
			if($cses['items_'.$i.'_downpayment']>0)# or $cses{'items_'.$i.'_downpayment1'}>0)
			{
				$pagoini="Pago Inicial ".format_price($cses['items_'.$i.'_downpayment'])." + ";
			}
			($fpprice==0 or !$fpprice) and ($fpprice=$price);
			$numpayments=0;
			$numpayments=$cses['items_'.$i.'_fpago']*4+int($cses['items_'.$i.'_fpago']/3);
			$output .= '<option value="'.$numpayments.'" '; 
			($cses['items_'.$i.'_payments'] == $cses['items_'.$i.'_fpago'] * 4 + intval($cses['items_'.$i.'_fpago']/3)) and ($output .= " selected "); 
			$output.= "> $pagoini " . ($cses['items_'.$i.'_fpago'] * 4 + intval($cses['items_'.$i.'_fpago']/3)) . " Pagos semanales de " . format_price(($fpprice-$cses['items_'.$i.'_downpayment'])/$numpayments) ." $str_disc</option>\n";
		}
		
		### Bi Weekly
		if ($cfg['fpbiweekly'] or (stristr($cses['items_'.$i.'_paytype'],"Layaway") != FALSE and $cses['paytype'] == 'Layaway')){
			if($cses['items_'.$i.'_downpayment']>0)# or $cses{'items_'.$i.'_downpayment1'}>0)
			{
				$pagoini="Pago Inicial ".format_price($cses['items_'.$i.'_downpayment'])." + ";
			}

			($fpprice==0 or !$fpprice) and ($fpprice=$price);
			$output .= '<option value="'.$cses['items_'.$i.'_fpago']*2 .'" '; 
			($cses['items_'.$i.'_payments'] == $cses['items_'.$i.'_fpago']*2) and ($output .= " selected "); 
			$output.= "> $pagoini " . ($cses['items_'.$i.'_fpago']*2) . " Pagos quincenales de " . format_price(($fpprice-$cses['items_'.$i.'_downpayment'])/$cses['items_'.$i.'_fpago']/2) ." $str_disc</option>\n";
		}
		
		## Monthly
		if ($cfg['fpmonthly'] == 1 and $cses['items_'.$i.'_fpago']!=1){
			if($cses['items_'.$i.'_downpayment']>0){
				$pagoini = "Pago Inicial ".format_price($cses['items_'.$i.'_downpayment'])." + ";
			}
			else
			{
				$pagoini ="";
			}

			if ($fpprice>0){
				$output .= '<option value="'.$cses['items_'.$i.'_fpago'].'" '; 
				($cses['items_'.$i.'_payments'] == $cses['items_'.$i.'_fpago']) and ($output .= " selected "); 
				$output.= '> '. $pagoini . $cses['items_'.$i.'_fpago'] .' Pagos mensuales de '. format_price(($fpprice-$cses['items_'.$i.'_downpayment'])/$cses['items_'.$i.'_fpago']) ." <!--$str_disc--></option>\n";
			}else{
				$denominador=$cses['items_'.$i.'_fpago'];
				(!$denominador) and ($denominador=1);
				$output .= '<option value="'.$cses['items_'.$i.'_fpago'].'" '; 
				($cses['items_'.$i.'_payments'] == $cses['items_'.$i.'_fpago']) and ($output .= " selected "); 
				$output.= '> '. $pagoini . $cses['items_'.$i.'_fpago'] .' Pagos mensuales de '. format_price(($price-$cses['items_'.$i.'_downpayment'])/$cses['items_'.$i.'_fpago']) ." $str_disc</option>\n";
			}
		}

	$output .= "</select>\n";
	return $output;
}



function paysummary($tovariable=0) {
# --------------------------------------------------------
# Last Modified on: 07/24/08 11:14:33
# Last Modified by: MCC C. Gabriel Varela S: Se verifica que la tarjeta no expire antes del último pago
# Last Modified on: 08/04/08 10:12:10
# Last Modified by: MCC C. Gabriel Varela S
# Last Modified on: 08/06/08 15:20:55
# Last Modified by: MCC C. Gabriel Varela S: Verificar que las cantidades en los pagos sea correcta cuando se mezclan pagos mensuales con 0-15-30
# Last Modified on: 10/28/08 14:51:50
# Last Modified by: MCC C. Gabriel Varela S: Se quita mensaje de son cada tal días si es un sólo pago
# Last Modified on: 10/30/08 10:30:50
# Last Modified by: MCC C. Gabriel Varela S: Se hace que ya no exista downpayment del 7% para pagos quincenales y semanales
# Last Modified on: 11/11/08 17:17:41
# Last Modified by: MCC C. Gabriel Varela S: Se hace que si el tipo de pago es lay away el primer pago sea el último y como dice el dicho, los últimos serán los primeros
# Last Modified RB: 12/02/08  18:56:30 Se agrego el template para layaway M.O.
# Last Modified on: 12/18/08 13:49:41
# Last Modified by: MCC C. Gabriel Varela S: Se hace que cuando sea membership, y lay away, el primer pago incluya el precio de la membresía
# Last Modified RB: 03/12/09  11:32:31 -- Agregue &save_callsession(); al final de la funcion
//Last modified on 4 Feb 2011 16:06:17
//Last modified by: MCC C. Gabriel Varela S. :Se hace que no se pueda avanzar si por cambio de pagos el último pago es mayor que la fecha de vencimiento de la tarjeta
//Last modified on 2 May 2011 13:10:34
//Last modified by: MCC C. Gabriel Varela S. : Se incorpora promo_campaign


global $cfg,$cses,$in,$va,$usr;

	if ($cses['paytype'] == 'Credit-Card' or $cses['paytype'] == 'Layaway'){
		$payments=array();
		$maxpaym=1;
		$fpdate='';
		$tofp='';
		$stfp='';
		$price=0;
		$promo_cont=0;
		$onepay=0;
		$fpdias= $cses['dayspay'];
		$maxpaym = 1;
		$downpaymentinorder=0;
		$cses['dpio'] = 0;

		if($cses['dayspay'] == 15){
			$downpaymentinorder=1;
			$cses['dpio'] = 1;
		}else{
			for ($i=1; $i <= $cses['items_in_basket']; $i++){
				if ($cses['items_'.$i.'_downpayment']>0 && $cses['items_'.$i.'_payments'] >= $cses['items_'.$i.'_fpago'] && $cses['items_'.$i.'_payments'] >1) {
					$downpaymentinorder=1;
					$cses['dpio'] = 1;
				}
			}			
		}
		########################################
		########### Items
		########################################
		for ($i=1; $i <= $cses['items_in_basket']; $i++){
			if(isset($cses['items_'.$i.'_qty']) and $cses['items_'.$i.'_qty'] > 0){
				

				##########################################
				#########  CALCULAR PAGO CONTADO
				##########################################
				if(($cfg['membership'] and $usr['type']=="Membership")or(isset($cfg['promo_campaign']) and $cfg['promo_campaign']==1))
				{
					$onepay = $cses['items_'.$i.'_msprice'];
				}
				elseif ($cses['items_'.$i.'_fpprice']>0){
					$onepay = $cses['items_'.$i.'_price'];
				}elseif(stristr($cses['items_'.$i.'_id'],$cfg['disc40']) != FALSE){
					$onepay = $cses['items_'.$i.'_price'] - ($cses['items_'.$i.'_price']*(40/100));
				}elseif (stristr($cses['items_'.$i.'_id'],$cfg['disc30']) != FALSE){
					$onepay = $cses['items_'.$i.'_price'] - ($cses['items_'.$i.'_price']*(30/100));
				}else{
					$onepay = $cses['items_'.$i.'_price'] - ($cses['items_'.$i.'_price']*$cfg['fpdiscount'.$cses['items_'.$i.'_fpago']]/100);
				}
	
				
				if ($cses['items_'.$i.'_id'] and $cses['items_'.$i.'_payments']==1){
					$payments[1] += round($onepay,2);
				}elseif ($cses['items_'.$i.'_payments'] == '3c'){
					## Skip
					$promo_cont += $onepay/3;
				}elseif ($cses['items_'.$i.'_id'] and $cses['items_'.$i.'_payments']>1){
					if ($cses['items_'.$i.'_downpayment']>0) {
						$tofp = $cses['items_'.$i.'_payments']+1;
						$stfp = 2;
					}
					else{
						$tofp = $cses['items_'.$i.'_payments'];
						$stfp = 1;
					}
					if(($cfg['membership'] and $usr['type']=="Membership")or(isset($cfg['promo_campaign']) and $cfg['promo_campaign']==1))
					{
						$price = $cses['items_'.$i.'_price'];
					}
					elseif ($cses['items_'.$i.'_fpprice']>0){
						$price = $cses['items_'.$i.'_fpprice'];
					}else{
						$price = $cses['items_'.$i.'_price'];
					}
					($maxpaym <= $tofp) and ($maxpaym = $tofp);
	
					for ($j=$stfp; $j <= $tofp; $j++){
						if ($cses['items_'.$i.'_payments'] == '3c'){
							$payments[$j] += round($price/3,2);
						}elseif($cses['items_'.$i.'_payments'] and $cses['items_'.$i.'_downpayment']>0) {
							$payments[$j] += round(($price-$cses['items_'.$i.'_downpayment'])/($cses['items_'.$i.'_payments']),2);
						}
						elseif ($cses['items_'.$i.'_payments']){
							$payments[$j] += round($price/$cses['items_'.$i.'_payments'],2);
						}
					}
				}
			}
		}

		
		#print_r($payments);
		#echo "Total de pagos:$maxpaym";
		########################################
		########### Service
		########################################
#		for my $i(1..$cses{'servis_in_basket'}){
#			@itemsessionid=&getsessionfieldid('items_','_id',$cses{'servis_'.$i.'_relid'},''); #JRG 29-05-2008
#			
#			if ($cses{'servis_'.$i.'_id'} and $cses{'servis_'.$i.'_payments'}==1){
##				if($downpaymentinorder>0) {
##					$payments[2] += round($cses{'servis_'.$i.'_price'},2);
##					$payments[1] += 0;
##				} else {
#					$payments[$_] += round($cses['items_'.$i.'_price'],2);
##				}
#			}elsif ($cses{'servis_'.$i.'_id'} and $cses{'servis_'.$i.'_payments'}>1){
##				if($cses{'servis_'.$i.'_downpayment1'}>0 && $cses{'servis_'.$i.'_payments'} > $cses{'servis_'.$i.'_fpago'}){
##					$tofp = $cses{'servis_'.$i.'_payments'}+1;
##					$stfp = 2;	
##					$cses['total_order'] += $cses{'servis_'.$i.'_downpayment1'};				
##				}
##				 elsif ($cses{'servis_'.$i.'_downpayment1'}>0) {
##					$tofp = $cses{'servis_'.$i.'_payments'}+1;
##					$stfp = 2;
##				}
##				else{
#					$tofp = $cses{'servis_'.$i.'_payments'};
#					$stfp = 1;
##				}
#
#				($maxpaym = $tofp) unless ($maxpaym > $tofp);
#				for ($stfp..$tofp){
#					if ($cses{'servis_'.$i.'_payments'} and $cses{'servis_'.$i.'_downpayment'}>0) {
#						$payments[$_] += round(($cses{'servis_'.$i.'_price'}-$cses{'servis_'.$i.'_downpayment'})/($cses{'servis_'.$i.'_payments'}),2);
#					}elsif ($cses{'servis_'.$i.'_payments'}){
#						$payments[$_] += round($cses{'servis_'.$i.'_price'}/$cses{'servis_'.$i.'_payments'},2);
#					}
#				}
#			}
#		}
		if ($promo_cont > 0 and $maxpaym >= 2){
			$payments[2] += $promo_cont;
			$fpdias = 30;
			$payments[1] = $cses['total_order']- round($promo_cont,2);
		}elseif ($promo_cont > 0 and $maxpaym < 2){
			$payments[2] = $promo_cont;
			$maxpaym = 2;
			$fpdias = 30;
			$payments[1] = $cses['total_order'] - round($promo_cont,2);
		}else{
			$payments[1] = $cses['total_order'] - round($promo_cont,2)*2;
		}

		#print_r($payments);
		#echo "Total de pagos:$maxpaym";
		
		for ($x=2; $x <= $maxpaym; $x++){
			$payments[1] -= round($payments[$x],2);
		}

		#print_r($payments);
		#echo "Total de pagos:$maxpaym";
	
		#Si el tipo de pago es layaway se cambian los pagos primero por el último.
		if($cses['paytype']=="Layaway")
		{
			$temp=0;
			$temp=$payments[1];
			$payments[1]=$payments[$maxpaym];
			$payments[$maxpaym]=$temp;
			if(($cfg['membership']==1 and $usr['type']=="Membership")or(isset($cfg['promo_campaign']) and $cfg['promo_campaign']==1))
			{
				$pricetoapply= load_name('sl_services','ID_services',$cfg['membershipservid'],'SPrice');
				$payments[1]+=$pricetoapply;
				$payments[$maxpaym]-=$pricetoapply;
			}
		}
		
		#&cgierr($payments[2]);
	
		$today = date("Y-m-d H:i:s");
		($cses['days'] > 0 and $cses['postdated'] == '1') and ($today = sqldate_plus($today,$cses['days']));
		($cses['paytype'] == 'Layaway' and $cses['startdate']) and ($today = $cses['startdate']);
		
		$va[amount] = '';
		for ($i=1; $i <= $maxpaym; $i++){
			$fpdate = sqldate_plus($today,$fpdias*($i-1));
			
			if ($promo_cont > 0 and $i > 1){
				if ($i == 2){
					$cses['fppayment2'] = round($promo_cont,2);
					$cses['fpdate2'] = sqldate_plus($today,15);
					$va['amount'] .= format_price($promo_cont) ." &nbsp; \@ &nbsp; ". $cses['fpdate2'] ."<br>";
					#$payments[2] += round($promo_cont,2);
				}
				$cses['fppayment'.($i+1)] =  round($payments[$i],2);
				$cses['fpdate'.($i+1)] = $fpdate;
				$va['amount'] .= format_price($payments[$i]) . " &nbsp; \@ &nbsp; $fpdate<br>";
			}else{
				$cses['fppayment'.$i] =  round($payments[$i],2);
				$cses['fpdate'.$i] = $fpdate;
				$va['amount'] .= format_price($payments[$i]) . " &nbsp; \@ &nbsp; $fpdate<br>";
			}
		}
		#Comparar„1¤7la fecha de último pago con la de expiración de la tarjeta
		if($cses['pmtfield7']=="CreditCard" or $cses['pmtfield7']=="DebitCard")
		{
			$pattern_day = "/^(\d{2})(\d{2})-(\d{2})-(\d{2})$/";
			$pattern_exp = "/^(\d{2})(\d{2})$/";

			preg_match($pattern_day,$fpdate,$dates);
			$lpday=$dates[4];
			(!isset($cses['pmtfield4'])) and ($cses['pmtfield4'] = $cses['expmm'] . $cses['expyy']);
			
			preg_match($pattern_exp,$cses['pmtfield4'],$ccdates);
			$edyear=$ccdates[2];
			$edmonth=$ccdates[1];
			$edday=28;

			if($edmonth==1 or $edmonth==3 or $edmonth==5 or $edmonth==7 or $edmonth==8 or $edmonth==10 or $edmonth==12)
			{
				$edday=31;
			}
			elseif($edmonth==4 or $edmonth==6 or $edmonth==9 or $edmonth==11)
			{
				$edday=30;
			}

			$diffs = mysql_query("SELECT DATEDIFF('20$edyear-$edmonth-$edday','$fpdate')");
			list($diff) = mysql_fetch_row($diffs);

			if($diff < $cfg['prevent_days'])
			{
				$va['amount'].=" <script language='javascript'>
				var str=''+self.location;
							str='/2-checkout-restartpayments';
							alert('Vencimiento Invalido, la fecha de vencimiento de la tarjeta debe ser al menos $cfg[prevent_days] dias despues del la ultima cuota($edmonth/20$edyear).');
							window.location=str;
					        </script>";
			}
		}
		
		(!isset($in[pmtfield4])) and ($in['pmtfield4'] = $in['expmm'].'/'.$in['expyy']);
		$cses['fppayments'] = $maxpaym;
		($promo_cont) and (++$cses['fppayments']);
		$va['fpdias'] = $fpdias;
		($fpdias!=1) and ($va['fpdias'] ="SON CADA $fpdias DIAS.");
		save_callsession();
		
		if($cses['paytype'] == 'Credit-Card' or $cses['laytype'] == 'Credit-Card'){
			$va['last4dig'] = substr($cses['pmtfield3'],-4);
			if ($cses['pmtfield7'] == 'DebitCard'){
				$va['cardtype'] = 'débito';
				$va['cardtype_en'] = 'debit';
			}else{
				$va['cardtype'] = 'crédito';
				$va['cardtype_en'] = 'credit';
			}

			##
			(!isset($in['pmtfield1'])) and ($in['pmtfield1'] = $cses['pmtfield1']);
			(!isset($in['pmtfield2'])) and ($in['pmtfield2'] = $cses['pmtfield2']);
			(!isset($in['pmtfield4'])) and ($in['pmtfield4'] = $cses['pmtfield4']);
			(!isset($in['pmtfield5'])) and ($in['pmtfield5'] = $cses['pmtfield5']);
			(!isset($in['pmtfield7'])) and ($in['pmtfield7'] = $cses['pmtfield7']);
			(isset($cses['pmtfield4'])) and ($in['pmtfield4'] = $cses['pmtfield4']);

			if($tovariable==0){
			    echo build_page($in['filepage'] . "paysummary_cc.html");
			}else{
			    return build_page($in['filepage'] . "paysummary_cc.html");
			}
		}else{
			$va['mo_data'] =  $cfg['shop_rfc'];

			if($tovariable==0){
			    echo build_page($in['filepage'] . "paysummary_layaway.html");
			}else{
			    return build_page($in['filepage'] . "paysummary_layaway.html");
			}
		}
	}else{
		
		for ($z=1; $z<= $cses['fppayments']; $z++){
			unset($cses['fppayment'.$z]);
			unset($cses['fpdate'.$z]);
		}
		
		$cses['fppayments']=1;
		$cses['fppayment1'] = $cses['total_order'];
		$cses['fpdate1'] = sqldate_plus(date("Y-m-d"),$cfg['cod_payday']);
		$va['fpdias'] = $cfg['cod_payday'];
		save_callsession();
		
		if($cses['paytype'] == 'COD'){
				$va['mo_data'] =  $cfg['shop_rfc'];
				$va['total_order'] = format_price($cses['total_order'],2);

				if($tovariable==0){
				    echo build_page($in['filepage'] . "paysummary_cod.html");
				}else{
				    return build_page($in['filepage'] . "paysummary_cod.html");
				}
		}elseif($cses['paytype'] == 'paypal'){
				$va['total_order'] = format_price($cses['total_order'],2);

				if($tovariable==0){
				    echo build_page($in['filepage'] . "paysummary_paypal.html");
				}else{
				    return build_page($in['filepage'] . "paysummary_paypal.html");
				}	
		}elseif($cses['paytype'] == 'descuentolibre'){
		    #validacion fecha descuentolibre
		    $cses['fpdate1']=$va['fpdate1_lib'];
		}else{
			if($tovariable==0){  
			    echo build_page($in['filepage'] . "paysummary_check.html");
			}else{
			    return build_page($in['filepage'] . "paysummary_check.html");
			}
		}
	}
}


function sqldate_plus($date,$plus=0){
# --------------------------------------------------------

	(!$date) and ($date=date("Y-m-d H:i:s"));
	$plus = intval($plus);
	$sth = mysql_query("SELECT DATE_ADD('$date', INTERVAL $plus DAY)");
	#echo "SELECT DATE_ADD('$date', INTERVAL $plus DAY)";
	list($new_date) = mysql_fetch_row($sth);

	return substr($new_date,0,10);
}


function do_save_keyword($keyword='',$results=0){
// --------------------------------------------------------
// Forms Involved: 
// Created on 05/10/2010 15:12:39
// Author: RB
// Description :   Guarda en DB el keyword y numero de resultados encontrados
// Parameters  : keyword, results	
	
	if($keyword != ''){
			mysql_query("INSERT INTO nsc_searchkeywords SET keywords='".mysql_real_escape_string($keyword)."', results='$results',IP_Address=INET_ATON('".$_SERVER['REMOTE_ADDR']."'), Date=CURDATE(), Time=CURTIME();");
	}
}


function do_build_tagclouds(){
// --------------------------------------------------------
// Forms Involved: 
// Created on 05/11/2010 15:45:39
// Author: RB
// Description :   Genera tag cloud basados en keywords
// Parameters  : 

    global $cfg,$in;

    ################################
    ################################ Keywords


    if($in['custom_keywords']){
        $tagclouds = $in['custom_keywords'];
    }else{

	    if(isset($in['id_products'])){
	        $query = " AND ID_products IN($in[id_products]) ";
	    }

	    $sth = mysql_query("SELECT GROUP_CONCAT(keyword) FROM sl_products WHERE keyword IS NOT NULL AND keyword !='' $query;");
	    list($tagclouds) = mysql_fetch_row($sth);

	    if($tagclouds == ''){

	        include('class.autokeyword.php');

	        $params['content'] = $in['keywords']; //page content
	        
	        $params['min_word_length'] = $cfg['kw_min_word_length'];  //minimum length of single words
	        $params['min_word_occur'] = $cfg['kw_min_word_occur'];  //minimum occur of single words

	        $params['min_2words_length'] = $cfg['kw_min_2words_length'];  //minimum length of words for 2 word phrases
	        $params['min_2words_phrase_length'] = $cfg['kw_min_2words_phrase_length']; //minimum length of 2 word phrases
	        $params['min_2words_phrase_occur'] = $cfg['kw_min_2words_phrase_occur']; //minimum occur of 2 words phrase

	        $params['min_3words_length'] = $cfg['kw_min_3words_length'];  //minimum length of words for 3 word phrases
	        $params['min_3words_phrase_length'] = $cfg['kw_min_3words_phrase_length']; //minimum length of 3 word phrases
	        $params['min_3words_phrase_occur'] = $cfg['kw_min_3words_phrase_occur']; //minimum occur of 3 words phrase

	        $keyword = new autokeyword($params, "iso-8859-1");
	        $tagclouds = $keyword->get_keywords();

	    }
    }

    ### Se verifica si se quieren sobreescribir los metatags y keywords
    if($cfg['rewrite_keywords']==1 and isset($in['id_products']) and strlen($in['id_products']) == 6){
	    mysql_query("UPDATE sl_products SET keyword='".mysql_real_escape_string($tagclouds)."' WHERE ID_products = '$in[id_products]';");
    }
    if($cfg['rewrite_metatags']==1 and isset($in['id_products']) and strlen($in['id_products']) == 6){
	    // Falta sobreescribir los metatags de los productos
    }

    ################################
    ################################ Tag Cloud
    $tagclouds = explode(",",$tagclouds);

    $factor = $cfg['tc_factor'];
    $starting_font_size = $cfg['tc_fontsize'];
    $tag_separator = $cfg['tc_separator'];
    $random_order = $cfg['tc_random'];

    

    $max_count = count($tagclouds);

    if($random_order){
        $tagclouds = randomize_array($tagclouds);
    }

    foreach($tagclouds as $tag){
        $rating = rand(1,10);
        $x = round(($rating * 100) / $max_count) * $factor;
        $font_size = $starting_font_size + $x.'px';
        echo "<span style='font-size: ".$font_size."; color: #676F9D;'>
	    <a href='$in[product]-a' class='tagcloud'>".$tag."</a></span>".$tag_separator;
    }
}


function randomize_array($array){
// --------------------------------------------------------
// Forms Involved: 
// Created on 05/11/2010 15:45:39
// Author: RB
// Description :   Regresa un arreglo con orden aleatorio
// Parameters  : 

    $rand_items = array_rand($array, count($array));
    $new_array = array();

    foreach($rand_items as $value){
        $new_array[$value] = $array[$value];
    }
    return $new_array;
}

function check_coupon(){
// --------------------------------------------------------
// Forms Involved: 
// Created on: 12 May 2010 10:41:23
// Author: MCC C. Gabriel Varela S.
// Description :   
// Parameters :
// Last time modified by RB on 08/16/2010 : si el cupon viene en una $cses, de manera automatica se agrega el producto
//Last modified on 3/15/11 12:24 PM
//Last modified by: MCC C. Gabriel Varela S. : Se cambia la forma de evaluar los cupones

	global $in,$va,$cses,$cfg,$usr;

	if(($in['coupon']!='' or $cses['coupon_to_apply'] != '') and !isset($cses['discount_applied']))
	{
		(isset($cses['coupon_to_apply'])) and ($in['coupon'] = $cses['coupon_to_apply']);
		$query = "Select 
		if(Status='Active',1,0)as isactive,
		if(curdate()<=expiration,1,0)as isvalid,
		coupon_value,
		expiration,
		ID_promo,
		percentage,
		maxdiscount,
		minimum_external,
		Status 
		from sl_coupons_external 
		where coupon_value='".mysql_real_escape_string($in['coupon'])."';";
		$sth = mysql_query($query) or die("Query failed : S" . mysql_error());
		
		if(mysql_num_rows($sth) == 0){
		 	return array(-1,0,0,0,'0000-00-00',0,0,0,0,'Invalid');
		}
		
		/*Aquí se obtienen los datos*/
		$rec = mysql_fetch_assoc($sth);
		
		if($rec['isactive']==0)
		{
			return array(-4,$rec['isactive'],$rec['isvalid'],$rec['coupon_value'],$rec['expiration'],$rec['ID_promo'],$rec['percentage'],$rec['maxdiscount'],$rec['minimum_external'],$rec['Status']);
		}
		
		if($rec['isvalid']==0)
		{
			return array(-5,$rec['isactive'],$rec['isvalid'],$rec['coupon_value'],$rec['expiration'],$rec['ID_promo'],$rec['percentage'],$rec['maxdiscount'],$rec['minimum_external'],$rec['Status']);
		}

		if($cses['total_i'] < $rec['minimum_external']){
			return array(-2,$rec['isactive'],$rec['isvalid'],$rec['coupon_value'],$rec['expiration'],$rec['ID_promo'],$rec['percentage'],$rec['maxdiscount'],$rec['minimum_external'],$rec['Status']);
		}
		
		// Producto de Regalo?
		if($rec['ID_promo'] != '' and strlen($rec['ID_promo']) >= 6){
				(strlen($rec['ID_promo']) == 9) and ($rec['ID_promo'] = substr($rec['ID_promo'],-6) );


				## Agregamos el producto al carrito
				++$cses['items_in_basket'];
				++$cses['products_in_basket'];
				if(build_edit_choices_module($in['id_products'],'','','')==''){
					$cses['items_'.$cses['items_in_basket'].'_id']="100$rec[ID_promo]";
				}else{
					$cses['items_'.$cses['items_in_basket'].'_id']="999$rec[ID_promo]";
				}
				
				$cses['items_'.$cses['items_in_basket'].'_qty']+=1;
				$cses['items_'.$cses['items_in_basket'].'_payments']=1;
				$cses['items_'.$cses['items_in_basket'].'_paytype']= isset($in['paytype']) ? $in['paytype'] : $cses['paytype'];
				$cses['items_'.$cses['items_in_basket'].'_price']= isset($cfg['id_promo_price']) ? $cfg['id_promo_price'] : 0;
				$cses['items_'.$cses['items_in_basket'].'_desc']= load_name('sl_products','ID_products',$rec['ID_promo'],'Name');
				$cses['items_'.$cses['items_in_basket'].'_discount']=0;
				$cses['items_'.$cses['items_in_basket'].'_coupon_discount']=0;
				$cses['items_'.$cses['items_in_basket'].'_idpromo']=1;
				
				$today=getdate();
				$cses['items_'.$cses['items_in_basket'].'_year']=$today['year'];
				$cses['items_'.$cses['items_in_basket'].'_month']=trans_txt('mon'.$today['mon']);
				$cses['items_'.$cses['items_in_basket'].'_day']=$today['mday'];
				
				$cses['items_'.$cses['items_in_basket'].'_shp1']=isset($cfg['id_promo_shipping']) ? $cfg['id_promo_shipping'] : 0;
				$cses['items_'.$cses['items_in_basket'].'_shp2']=isset($cfg['id_promo_shipping']) ? $cfg['id_promo_shipping'] : 0;
				$cses['items_'.$cses['items_in_basket'].'_shp3']=isset($cfg['id_promo_shipping']) ? $cfg['id_promo_shipping'] : 0; 
				
				//Calcular tax
				$cses['items_'.$cses['items_in_basket'].'_tax']=($cses['items_'.$cses['items_in_basket'].'_price']-$cses['items_'.$cses['items_in_basket'].'_discount']-$cses['items_'.$cses['items_in_basket'].'_coupon_discount'])*$cses['items_'.$cses['items_in_basket'].'_qty']*$cses['tax_total'];
			
				$cses['item_promo'] = $cses['items_in_basket'];
				//mysql_query("Update sl_coupons_external set Status='Used' where ID_coupons_external= " . $rec['ID_coupons_external'] . ";");						
				$discount_amt=0;
		}else{
				//validar contra max_discount
				//calcula cantidad a descontar
				if($rec['percentage']!=0)
					$discount_amt=round($in['ordernet']*$rec['percentage']/100,2);
				elseif($rec['percentage']==0 and $rec['maxdiscount']!=0)
					$discount_amt=$rec['maxdiscount'];
				if($rec['maxdiscount'] < $discount_amt and $rec['maxdiscount']!=0)
					$discount_amt=$rec['maxdiscount'];
		}
		
		$cses['items_discounts']=$discount_amt;
		$cses['discount_applied']=1;
		//Registra código utilizado
		$cses['coupon_used']=$rec['coupon_value'];
		$cses['coupon_minimum_external']=$rec['minimum_external'];
		$va['message']	=	trans_txt('good_coupon');
		update_cart_session();
		save_callsession(0);
		return array(1,$rec['isactive'],$rec['isvalid'],$rec['coupon_value'],$rec['expiration'],$rec['ID_promo'],$rec['percentage'],$rec['maxdiscount'],$rec['minimum_external'],$rec['Status']);
	}
	else
	{
		return array(-3,$rec['isactive'],$rec['isvalid'],$rec['coupon_value'],$rec['expiration'],$rec['ID_promo'],$rec['percentage'],$rec['maxdiscount'],$rec['minimum_external'],$rec['Status']);
	}
}

function verify_discount(){
// --------------------------------------------------------
// Forms Involved: 
// Created on: 09 Jun 2010 15:30:23
// Author: RB.
// Description : Revisa que una orden con descuento cumpla con los requisitos.  
// Parameters :

	global $cses,$cfg,$in,$va;

	
	if(array_key_exists('coupon_used',$cses)){
  
		if($cses['total_i'] < $cses['coupon_minimum_external']){

			if(array_key_exists('item_promo',$cses)){
				$cses['item_promo'] = rtrim($cses['item_promo'],"|");

				$ary = explode("|",$cses['item_promo']);
				foreach($ary as $key => $value){
					if($value != '' and isset($cses['items_'. $value .'_id'])){
						unset($cses['items_'. $value .'_id']);
						unset($cses['items_'. $value .'_qty']);
						unset($cses['items_'. $value .'_price']);
						unset($cses['items_'. $value .'_payments']);
						--$cses['products_in_basket'];
					}
				}
				unset($cses['item_promo']);
			}else{
				unset($cses['items_discounts']); 
			}
			unset($cses['coupon_used']);
			unset($cses['discount_applied']);
			$va['message'] =  trans_txt('error_coupon');
			
		}
	}
	update_cart_session();
}




function validate_qty(){
// --------------------------------------------------------
// Forms Involved: 
// Created on: 14 May 2010 10:04:28
// Author: MCC C. Gabriel Varela S.
// Description :   
// Parameters :
	global $cses,$in;
	$sth = mysql_query("Select if(not isnull(maxqty),maxqty,0)as maxqty from sl_products_w where Id_products='".mysql_real_escape_string($in[id_products])."'") or die("Query failed : " . mysql_error());
	$rec = mysql_fetch_assoc($sth);
	if($rec[maxqty]!=0)
	{
		//No permitir agregar en la misma orden
		//Verificar si hay ¨®rdenes anteriores
		for ($i=1;$i<=$cses[items_in_basket];$i++)
		{
			if ($cses['items_'.$i.'_qty']>0  and $cses['items_'.$i.'_id']>0 and substr($cses['items_'.$i.'_id'],3,6)==$in[id_products])
			{
				$qtyinorder++;
			}
		}
		if($qtyinorder>=$rec[maxqty])
			return -1;
		else
			return 1;
	}
	else
	{
		return 1;
	}
}


function get_related_products($id_products=0){
// --------------------------------------------------------
// Created on: 27 May 2010 11:04:28
// Author: RB.
// Forms Involved: 
// Description :   Busca productos relacionados y construye una tabla en base a ellos
// Parameters :
// Last time modified by RB on 03/18/2011 : Se agrega rel="nofollow" a links -e
//Last modified on 2 May 2011 11:59:43
//Last modified by: MCC C. Gabriel Varela S. : Se hace que también se condicione el mostrar el ícono de membership


	global $va,$in,$cfg,$usr;

	$query = '';
	$cad_related = '';
	$ary_related = array();


	if($id_products == 0){
	        if(isset($in['id_products'])){
		        $id_products = intval($in['id_products']);
	        }
	}

	if($id_products > 0){
		$sth = mysql_query("SELECT ID_products_options FROM sl_products_related WHERE ID_products = ". intval($id_products) ." AND Status = 'Active' ORDER BY ID_products_options;");

		if(mysql_numrows($sth) > 0){
		
			while(list($id_related) = mysql_fetch_row($sth)){
				array_push($ary_related , $id_related);
			}
			
			$query = build_do_for_one_product_query($rows='ID_products,SPrice,MemberPrice,Name,Name_link',$where=" AND ID_products IN(". implode(",", $ary_related) .")");
			$sth2 = mysql_query($query);

			if(mysql_numrows($sth2) > 0){
				$in['related_template'] = 'cart_related_products.html';
				while(list($id_rel,$sprice,$memberprice,$pname,$plink) = mysql_fetch_row($sth2)){

					    $image ='';
					    
					    if(is_readable($cfg['path_imgmansi'] . $id_rel .'b1.gif')){
						    $image = $cfg['path_imgman'] . $id_rel .'b1.gif';

					    }elseif(is_readable($cfg['path_imgmansi'] . $id_rel .'b1.jpg')){
						    $image = $cfg['path_imgman'] . $id_rel .'b1.jpg';

					    }elseif(is_readable($cfg['path_imgmansi'] . $id_rel .'b1.png')){
						    $image = $cfg['path_imgman'] . $id_rel .'b1.png';
					    }

							# Precio
							$item_price = format_price($sprice);
							if(isset($cfg['promo_campaign']) and $cfg['promo_campaign']==1){
									if($memberprice > 0 and $memberprice < $sprice) 
									{
										$item_price = '<span style="text-decoration:line-through;">'. $item_price . '</span> - ' . format_price($memberprice);
										$item_price .= ' &nbsp;<img src="/images/cart/promo_campaign.jpg">';
									}
									($memberprice > 0) and ($item_price = format_price($memberprice));
									
							}
							elseif($usr['type'] == 'Membership' and $cfg['membership'] == 1){
									if($memberprice > 0 and $memberprice < $sprice) 
									{
										$item_price = '<span style="text-decoration:line-through;">'. $item_price . '</span> - ' . format_price($memberprice);
										$item_price .= ' &nbsp;<img src="/images/cart/club.jpg">';
									}
									($memberprice > 0) and ($item_price = format_price($memberprice));
									
							}

					    $va['related_products'] .= '<div><table border="0" width="540" background="images/h300.png">
					<td>
						<a href="/'.$plink.'-a">
			      <img src="'.$image.'" border="0" width="190"/>
						</a>
					</td>
					<td align="center">
					<a href="/'.$plink.'-a" class="act"><font face="century gothic, verdana" size=3>'.$pname.'</a><br>'.$item_price.' <br><br>
					<a href="/'.$plink.'-e"  rel="nofollow"><img src="/images/add.png" name="cmd_cart_add1" height="34" border="0" width="110"></a>
					</td>
				</tr>
			</table>
		</div>';
				}
			}  
		}

	}
}

function cart_to_xml(){
// --------------------------------------------------------
// Forms Involved: 
// Created on: 22 Jul 2010 16:15:35
// Author: MCC C. Gabriel Varela S.
// Description :   Convierte el carrito en formato xml
// Parameters :
//Last modified on 14 Jul 2011 13:03:23
//Last modified by: MCC C. Gabriel Varela S. :The site name is added
	global $cfg,$in,$cses;
	$cart="";
	$items="";
	
	for ($i=1;$i<=$cses[items_in_basket];$i++)
	{
		$id_name='';
		$id_model='';
		$sprice=0;
		if ($cses['items_'.$i.'_qty']>0  and $cses['items_'.$i.'_id']>0)
		{
			$id_name = load_name('sl_products_w','ID_products',substr($cses['items_'.$i.'_id'],3,6),'Name');
			$id_model= load_name('sl_products','ID_products',substr($cses['items_'.$i.'_id'],3,6),'Model');
			$sprice=get_item_price(substr($cses['items_'.$i.'_id'],3,6));
			$items.="<item>
          <merchant-item-id>".$cses['items_'.$i.'_id']."</merchant-item-id>
          <item-name>$id_name</item-name>
          <item-description>$id_model</item-description>
          <unit-price currency='USD'>$sprice</unit-price>
          <quantity>".$cses['items_'.$i.'_qty']."</quantity>
          <merchant-private-item-data>
					   <item-local-session-id>$i</item-local-session-id>
					</merchant-private-item-data>
     </item>";
		}
	}
	
	$cart="<?xml version='1.0' encoding='UTF-8'?>

  <checkout-shopping-cart xmlns='http://checkout.google.com/schema/2'>
    <shopping-cart>
     <items>
     $items
     </items>
     <merchant-private-data>
     	<site_domain>".$cfg['site_domain']."</site_domain>
     	<session_id>".session_id()."</session_id>
     	<id_admin_users>$cfg[id_admin_users]</id_admin_users>
     </merchant-private-data>
    </shopping-cart>
    <checkout-flow-support>
     <merchant-checkout-flow-support>
     <shipping-methods>
          <flat-rate-shipping name='UPS'>
          <price currency='USD'>".$cses['shipping_total']."</price>
          </flat-rate-shipping>
     </shipping-methods>
     </merchant-checkout-flow-support>
    </checkout-flow-support>
  </checkout-shopping-cart>";
  return $cart;
}

function get_item_price($id_products){
// --------------------------------------------------------
// Forms Involved: 
// Created on: 22 Jul 2010 17:13:44
// Author: MCC C. Gabriel Varela S.
// Description :   
// Parameters :
//Last modified on 3 May 2011 13:15:34
//Last modified by: MCC C. Gabriel Varela S. : Se incorpora promo_campaign
	global $cfg,$in;

	$sth = mysql_query("Select *
from (Select 
				if(not isnull(sl_products_prior.SPrice)and sl_products_prior.SPrice!=0 and sl_products_prior.SPrice!='',sl_products_prior.SPrice,sl_products.SPrice)as SPrice,
				if(not isnull(sl_products_prior.MemberPrice)and sl_products_prior.MemberPrice > 0,sl_products_prior.MemberPrice,sl_products.MemberPrice)as MemberPrice,
				sl_products.ID_products
			from sl_products
			left join sl_products_prior on(sl_products.ID_products=sl_products_prior.ID_products)
			and sl_products_prior.belongsto='$cfg[owner]'
			inner join sl_products_w on(sl_products.ID_products=sl_products_w.ID_products)
			left join sl_products_categories on(sl_products.ID_products=sl_products_categories.ID_products)
			left join sl_categories on (sl_products_categories.ID_categories=sl_categories.ID_categories)
			where $cfg[whereproducts])as sl_products
where ID_products=$id_products;") or die("Query failed : " . mysql_error());
	$rec = mysql_fetch_assoc($sth);
	if(isset($cfg['promo_campaign']) and $cfg['promo_campaign']==1){
		if($rec['MemberPrice'] > 0  and $rec['MemberPrice'] < $rec['SPrice'])
		{
			return $rec['MemberPrice'];
		}
		else
		{
			return $rec['SPrice'];
		}
	}
	return $rec['SPrice'];
}

function html_item_price($id_products){
// --------------------------------------------------------
// Forms Involved: 
// Created on: 7/23/2010 12:56:43 PM
// Author: Carlos
// Description :   
// Parameters :
	$price = get_item_price($id_products);
	$price = number_format($price,2);
	$ary = preg_split("/\./",$price,2);
	return $ary[0].'.<sup style="font-size:0.6em">'.$ary[1].'</sup>';	
}

function html_item_shp($id_products){
// --------------------------------------------------------
// Forms Involved: 
// Created on: 7/23/2010 12:56:43 PM
// Author: Carlos
// Description :   
// Parameters :
	global $cfg;
	#$temp_in = $in;
	$sth = mysql_query("Select * from (Select 

if(not isnull(sl_products_prior.SPrice)and sl_products_prior.SPrice!=0 and sl_products_prior.SPrice!='',sl_products_prior.SPrice,sl_products.SPrice)as SPrice, 

if(not isnull(sl_products_prior.edt)and sl_products_prior.edt!=0 and sl_products_prior.edt!='',sl_products_prior.edt,sl_products.edt)as edt,

if(not isnull(sl_products_prior.SizeW)and sl_products_prior.SizeW!=0 and sl_products_prior.SizeW!='',sl_products_prior.SizeW,sl_products.SizeW)as SizeW,

if(not isnull(sl_products_prior.SizeH)and sl_products_prior.SizeH!=0 and sl_products_prior.SizeH!='',sl_products_prior.SizeH,sl_products.SizeH)as SizeH,

if(not isnull(sl_products_prior.SizeL)and sl_products_prior.SizeL!=0 and sl_products_prior.SizeL!='',sl_products_prior.SizeL,sl_products.SizeL)as SizeL,

if(not isnull(sl_products_prior.Weight)and sl_products_prior.Weight!=0 and sl_products_prior.Weight!='',sl_products_prior.Weight,sl_products.Weight)as Weight,


sl_products.ID_products from sl_products left join sl_products_prior on(sl_products.ID_products=sl_products_prior.ID_products) inner join sl_products_w on(sl_products.ID_products=sl_products_w.ID_products) left join sl_products_categories on(sl_products.ID_products=sl_products_categories.ID_products) left join sl_categories on (sl_products_categories.ID_categories=sl_categories.ID_categories) where ((sl_products.Status='On-Air' AND sl_products.web_available='Yes') OR sl_products.Status='Web Only'))as sl_products where ID_products=$id_products;") or die("Query failed : " . mysql_error());
	$rec = mysql_fetch_assoc($sth);
	$rec['id_products'] = $id_products;
	$rec['size'] = $rec[SizeW]*$rec[SizeH]*$rec[SizeL];
	#foreach ($in as $key=>$value ) {
	#	echo "$key : $value<br>";
	#}
	$sh = shipping_box($rec);
	$sh = number_format($sh,2);
	return $sh;
	#$ary = preg_split("/\./",$sh,2);
	#return "$ary[0]<sup>$ary[1]</sup>";	
}

function cart_to_paypal(){
// --------------------------------------------------------
// Forms Involved: 
// Created on: 22 Jul 2010 16:15:35
// Author: MCC C. Gabriel Varela S.
// Description :   Convierte el carrito en formato xml
// Parameters :

	global $cfg,$in,$cses;
	$cart="";
	$items="";

	$num=0;
	for ($i=1; $i <= $cses['items_in_basket']; $i++)
	{
		$id_name='';
		$id_model='';
		$sprice=0;
		if ($cses['items_'.$i.'_qty'] > 0  and $cses['items_'.$i.'_id'] > 0)
		{
			$items .= '&L_NAME'.($num).'='. str_replace("&","AND",$cses['items_'.$i.'_desc']);
			$items .= '&L_NUMBER'.($num).'='. $cses['items_'.$i.'_id'];
			$items .= '&L_DESC'.($num).'='. str_replace("&","AND",$cses['items_'.$i.'_desc']);
			$items .= '&L_AMT'.($num).'='. $cses['items_'.$i.'_price'];
			$items .= '&L_QTY'.($num).'='. $cses['items_'.$i.'_qty'];
			$num++;
		}
	}
	
	$items .= '&L_SHIPPINGOPTIONNAME0=Standard Shipping'; 
	$items .= '&L_SHIPPINGOPTIONLABEL0=Standard Shipping'; 
	$items .= '&L_SHIPPINGOPTIONAMOUNT0='. $cses['shipping_total'];
	$items .= '&L_SHIPPINGOPTIONISDEFAULT0=true';
	$items .= '&ITEMAMT='. $cses['total_i'];
	$items .= '&TAXAMT='. round($cses['total_i'] * $cses['tax_total'],2);
	$items .= '&SHIPPINGAMT='. $cses['shipping_total'];
	$items .= '&HANDLINGAMT=0.00';
	$items .= '&MAXAMT='. ($cses['total_i'] * 2 + $cses['shipping_total']);
	
	return $items;
}

function check_products_wochoices(){
# --------------------------------------------------------
# Forms Involved: 
# Created on: 07/29/10 16:08:28
# Author: MCC C. Gabriel Varela S.
# Description :   
# Parameters :
	global $cses;
	$wchoice=0;
	for ($i=1;$i<=$cses['items_in_basket'] and $wchoice==0;$i++){
		if ($cses['items_'.$i.'_qty']>0  and $cses['items_'.$i.'_id']>0){
			if(substr($cses['items_'.$i.'_id'],0,3)==999)
				$wchoice=$i;
			}
	}
	return $wchoice;	
}


function get_promo_facebook($promo){
#-----------------------------------------
# Created on: 05/12/2010  12:05:02 By  Roberto Barcenas
# Forms Involved: 
# Description : Creates new coupons for facebook customers
# Parameters :  Dependiendo del numero de cupones a imprimir, cambiar el rango, 
#	      Los id's, compra minima y expiracion salen de vars $id_products,$coupons

    global $in,$cfg,$cses,$va;

    $num=0;$expiration=7;$id_promo=0;$min=0;$url=$cfg['maindomain'];
		
		$ary_options = explode("|",$cfg['id_promo_'. $promo]);
		$qty = count($ary_options);
		
    for($num=1; $num <= $qty; $num++){
    	
    		$ary_products = explode(":",$ary_options[$num-1]);
    		$id_promo = $ary_products[0];
    		$min = $ary_products[1];
				$percentage = $ary_products[2];
				$maxdis = $ary_products[3];

        $sth = mysql_query("SELECT COUNT(*) FROM sl_products WHERE ID_products = '".substr($id_promo,-6)."';");
        list($valid) = mysql_fetch_row($sth);

        if($valid == 1){
	        $cses['coupon'.$num] = set_coupon_external($expiration,$id_promo,$percentage,$maxdis,$min,$url);
        }
    }

    (strlen($cses['coupon1']) != 16) and ($cses['coupon1'] = trans_txt('coupon_notavailable'));
    (strlen($cses['coupon2']) != 16) and ($cses['coupon2'] = trans_txt('coupon_notavailable'));
    (strlen($cses['coupon3']) != 16) and ($cses['coupon3'] = trans_txt('coupon_notavailable'));
    (strlen($cses['coupon4']) != 16) and ($cses['coupon4'] = trans_txt('coupon_notavailable'));

    if(strlen($cses['coupon1']) == 16 or strlen($cses['coupon2']) == 16 or strlen($cses['coupon3']) == 16 or strlen($cses['coupon4']) == 16 ){
        $cses['coupon_facebook'] = 1;
    }

    $sth = mysql_query("SELECT DATE_ADD(CURDATE(), INTERVAL $expiration day);");
    list($cses['vigencia']) = mysql_fetch_row($sth);

}

function set_coupon_external($cp_expiration=0,$cp_idpromo='',$cp_percentage=0,$cp_maxdiscount=0,$cp_minexternal=0,$cp_externalurl=''){
#-----------------------------------------
# Created on: 05/12/2010  12:05:02 By  Roberto Barcenas
# Forms Involved: 
# Description : Creates new coupon
# Parameters :

	global $cfg;
	$coupon_value = 0;
	$count=1;
	$query='';
	$flag=0;
	

	while ($flag==0 and $count < 300){
		$coupon_value = promocode_generate($coupon_value);
		$query_sc = "SELECT COUNT(*) FROM sl_coupons_external WHERE coupon_value = '$coupon_value';";
		$sth = mysql_query($query_sc);
		if (mysql_num_rows($sth) == 0 and strlen($coupon_value) == 16){
			$flag = 1;
			break;
		}
		
		if($count%100 == 1){
			$coupon_value=0;
		}
		++$count;
	}

#	$coupon_value = &promocode_generate($coupon_value);
	if($coupon_value){
		$query='';
		if($cp_externalname != ''){
			$query .= " name_external= '$cp_externalname' , ";
		}

		if($cp_expiration == '' or $cp_expiration == 0){
			$cp_expiration = 30;
		}
		$query .= " expiration= DATE_ADD(CURDATE(), INTERVAL $cp_expiration day),";

		if($cp_idpromo != '' and strlen($cp_idpromo) >= 6){
			$query .= " ID_promo = $cp_idpromo ,";
		}

		if($cp_percentage != '' and $cp_percentage > 0){
			$query .= " percentage = $cp_percentage ,";
		}

		if($cp_maxdiscount != '' and $cp_maxdiscount > 0){
			$query .= " maxdiscount = $cp_maxdiscount , ";
		}

		if($cp_minexternal !='' and $cp_minexternal > 0){
			$query .= " minimum_external = $cp_minexternal , ";
		}

		if($cp_externalurl != ''){
			$query .= " url_external = '$cp_externalurl' , ";
		}

		$queryc = "INSERT INTO sl_coupons_external SET coupon_value = '$coupon_value', $query Status='Active',Date=CURDATE(), Time=CURTIME(),ID_admin_users='$cfg[id_admin_users]';";
		$sth=mysql_query($queryc);
		if(mysql_affected_rows()== 1)
		    return $coupon_value;
		else
		    return -1;
		
	}
	return -1;
}

function promocode_generate($ini=0) {
# --------------------------------------------------------
    $p1=0;
    $p2=0;
    $p3=0;
    $c =0;
    mt_srand(make_seed());
    
    $c = (intval(mt_rand(1000000000,mt_getrandmax())) + 1) .  (intval(mt_rand(1000000000,mt_getrandmax())) + 1).  (intval(mt_rand(1000000000,mt_getrandmax())) + 1);
    $p1 = substr($c,0,5); 
    $p2 = substr($c,7,5); 
    $p3 = substr($c,8,3);
    #print promocode_dv($p1). $p1. promocode_dv($p1.$p2). $p2. promocode_dv($p2) . $p3 ." ";
    return (promocode_dv($p1). $p1. promocode_dv($p1.$p2). $p2. promocode_dv($p2) . $p3);
}

function make_seed(){
# --------------------------------------------------------	
  list($usec, $sec) = explode(' ', microtime());
  return (float) $sec + ((float) $usec * 100000);
}

function promocode_dv($input=0,$tot=0) {
# --------------------------------------------------------
   
    $lg = strlen($input);
    
    for ($i=0;$i <= $lg; $i++){
        $tot += ord(substr($input,$i,1)) + ord(substr($input,$i+1,1)) - 30 - $i;
    }
    $dv = intval(($tot/11-intval($tot/11))*11);
    ($dv==10) and ($dv=0);
    return $dv;
}

function is_promo_facebook($name_product = ''){
#-----------------------------------------
# Created on: 05/12/2010  12:05:02 By  Roberto Barcenas
# Forms Involved: 
# Description : Check if a product has a facebook promo
# Parameters :

	global $cfg;
	
	$ary = explode("|",$cfg['promofb']);
	
	if($name_product == '' or count($ary) == 0){
		return FALSE;
	}else{
		
		foreach($ary as $promo){
			if(stristr($name_product,$promo) !== FALSE){
				return TRUE;
			}
		}
		
	}
}

function check_gift(){
# --------------------------------------------------------
# Forms Involved: 
# Created on: 09/02/10 16:03:19
# Author: MCC C. Gabriel Varela S.
# Description :   
# Parameters :
# Last Time Modified by RB on 04/17/2012: Se agrega pisibilidad de regalo no basado en compra minima sino en arreglo de productos $cfg['gift_triggers']


	global $cfg,$cses,$va,$in;
	if($cfg['gifts_use'])
	{
		#print "$cses[total_i]>$cfg[gifts_sale_min] -- $cses[gifts_applied]<br>";
		$ary_triggers = !empty($cfg['gifts_triggers']) ? explode('|',$cfg['gifts_triggers']) : 0;
		if($cses['total_i']>$cfg['gifts_sale_min'] or (is_array($ary_triggers) and in_array( $in['id_products'], $ary_triggers ) ))
		{
			unset($non_dropship_items);
			$non_dropship_items = get_nondropship_items_in_cart();

			//Evalúa si no ha aplicado el Regalo
			if(!$cses['gifts_applied'] and $non_dropship_items > 0 and (empty($ary_triggers) or in_array( $in['id_products'], $ary_triggers ) ) )
			{
				## Agregamos el producto al carrito
				++$cses['items_in_basket'];
				++$cses['products_in_basket'];
				if(build_edit_choices_module($in['id_products'],'','','')==''){
					$cses['items_'.$cses['items_in_basket'].'_id']="100$cfg[gifts_ids]";
				}else{
					$cses['items_'.$cses['items_in_basket'].'_id']="999$cfg[gifts_ids]";
				}
				
				$cses['items_'.$cses['items_in_basket'].'_qty']+=1;
				$cses['items_'.$cses['items_in_basket'].'_payments']=1;
				$cses['items_'.$cses['items_in_basket'].'_paytype']= isset($in['paytype']) ? $in['paytype'] : $cses['paytype'];
				$cses['items_'.$cses['items_in_basket'].'_price']= isset($cfg['gifts_prices']) ? $cfg['gifts_prices'] : 0;
				$cses['items_'.$cses['items_in_basket'].'_desc']= load_name('sl_products','ID_products',$cfg['gifts_ids'],'Name');
				$cses['items_'.$cses['items_in_basket'].'_discount']=0;
				$cses['items_'.$cses['items_in_basket'].'_coupon_discount']=0;
				$cses['items_'.$cses['items_in_basket'].'_gift']=1;
				
				$today=getdate();
				$cses['items_'.$cses['items_in_basket'].'_year']=$today['year'];
				$cses['items_'.$cses['items_in_basket'].'_month']=trans_txt('mon'.$today['mon']);
				$cses['items_'.$cses['items_in_basket'].'_day']=$today['mday'];
				
				$cses['items_'.$cses['items_in_basket'].'_shp1']=isset($cfg['gifts_shippings']) ? $cfg['gifts_shippings'] : 0;
				$cses['items_'.$cses['items_in_basket'].'_shp2']=isset($cfg['gifts_shippings']) ? $cfg['gifts_shippings'] : 0;
				$cses['items_'.$cses['items_in_basket'].'_shp3']=isset($cfg['gifts_shippings']) ? $cfg['gifts_shippings'] : 0; 
				
				//Calcular tax
				$cses['items_'.$cses['items_in_basket'].'_tax']=($cses['items_'.$cses['items_in_basket'].'_price']-$cses['items_'.$cses['items_in_basket'].'_discount']-$cses['items_'.$cses['items_in_basket'].'_coupon_discount'])*$cses['items_'.$cses['items_in_basket'].'_qty']*$cses['tax_total'];
				$cses['item_gifts'] = $cses['items_in_basket'];

				## Si el producto no se regala por minimo monto comprado, ligar regalo con producto trigger
				if(is_array($ary_triggers) and in_array( $in['id_products'], $ary_triggers ) ){
					$cses['items_'.($cses['items_in_basket'] - 1).'_relid'] =  $cses['items_in_basket'];
				}

				$cses['gifts_applied']=1;
				//Registra código utilizado
				$cses['gifts_used']=$cfg['gifts_ids'];
				$cses['gifts_minimum_external']=$cfg['gifts_sale_min'];
				$va['message'] = trans_txt('good_gift');
				$in['message'] = trans_txt('good_gift');
				update_cart_session();
				save_callsession(0);
				return 1;
			}
		}
		else
		{
			return -2;
		}
	}
	return -1;
}

function verify_gifts(){
# --------------------------------------------------------
# Forms Involved: 
# Created on: 09/02/10 17:00:58
# Author: MCC C. Gabriel Varela S.
# Description :   
# Parameters :
# Last Time Modified by RB on 04/17/2012: Se descomenta el reseteo de gifts_applied

	global $cses,$cfg,$in,$va;

	if(array_key_exists('gifts_used',$cses)){

		unset($non_dropship_items);
		$non_dropship_items = get_nondropship_items_in_cart();

		if($cses['total_i'] < $cfg['gifts_sale_min'] or $non_dropship_items == 1){
			unset($cses['gifts_used']);
			unset($cses['gifts_applied']);
			unset($cses['gifts_minimum_external']);
			$va['message'] =  trans_txt('error_gifts');
			$in['message'] =  trans_txt('error_gifts');
			if($cses['item_gifts'] != '' and isset($cses['items_'. $cses['item_gifts'] .'_id'])){
				unset($cses['items_'. $cses['item_gifts'] .'_id']);
				unset($cses['items_'. $cses['item_gifts'] .'_qty']);
				unset($cses['items_'. $cses['item_gifts'] .'_price']);
				unset($cses['items_'. $cses['item_gifts'] .'_payments']);
				unset($cses['item_gifts']);
				--$cses['products_in_basket'];
			}
		}
	}
	if($in['do']!='' and $cses['item_gifts'] != '' and $in['do']==$cses['item_gifts']){
		unset($cses['gifts_used']);
		unset($cses['gifts_applied']);//borrar applied de verdad?
		unset($cses['item_gifts']);
		unset($cses['gifts_minimum_external']);
	}
	update_cart_session();
}


function get_nondropship_items_in_cart(){
#-----------------------------------------
# Created on: 09/15/2010  14:15:13 By  Roberto Barcenas
# Forms Involved: 
# Description : Regrega el total de items non dropship contiene la orden
# Parameters : id_orders

	global $cses;
	$no_dropship=0;

	for ($i=1;$i<=$cses['items_in_basket'];$i++){
		if ($cses['items_'.$i.'_qty']>0  and $cses['items_'.$i.'_id']>0){
			unset($actual_id);
			$actual_id = substr($cses['items_'.$i.'_id'],-6);
			if(load_name('sl_products','ID_products',$actual_id,'DropShipment') == 'No'){
				$no_dropship++;
			}
		}
	}
	return $no_dropship;
}


function send_dropship_alert($id_orders=0)
{
#-----------------------------------------
# Created on: 09/15/2010  14:15:13 By  Roberto Barcenas
# Forms Involved: 
# Description : Revisa si es necesario enviar correo a persona encargada de Dropship Orders con el file de productos a enviar
# Parameters : id_orders

	global $cfg,$cses,$va;

	($id_orders == 0 and $cses['id_orders'] > 0) and ($id_orders = intval($cses['id_orders']));
	unset($ds_products);
	unset($fname);

	if($id_orders > 0){
  
		$sth = mysql_query("SELECT COUNT(*)
				FROM sl_orders_products
				INNER JOIN sl_products
				ON RIGHT(sl_orders_products.ID_products,6) = sl_products.ID_products
				WHERE ID_orders IN($id_orders) AND sl_orders_products.Status NOT IN('Order Cancelled','Inactive') AND DropShipment = 'Yes' GROUP BY ID_orders;");
		list($ds_products) = mysql_fetch_row($sth);
		
		if($ds_products > 0){
			$fname = build_dropship_file($id_orders);

			if($fname != -1 and $fname != -2){
				unset($mail_headers);
				unset($mail_body);
				unset($attachment);

				$mail_subject = 'Dropship Order ('. $id_orders .')';
				$mail_headers = "";
				$mail_body = 'Este mensaje ha sido generado debido a que se concreto una orden en el sitio Innovashop.'. "\r\n".'Contiene adjunta la informacion de productos para envio' . "\r\n\r\n";
				$mail_body .=  $va['dropship_orders_info'] . "\r\n";
			
				$attachment = array(array('type' => 'application/csv',
						'name' => $fname,
						'data' => file_get_contents($cfg['path_dsfiles'] . $fname)));

				send_mail_attachment($cfg['dropship_email_alert'],$mail_subject , $mail_body, $mail_headers,'utf-8',$attachment);
				send_mail_attachment($cfg['mail_developer_rb'],$mail_subject , $mail_body, $mail_headers,'utf-8',$attachment);
				unset($va['dropship_orders_info']);
			}
		}
	}
}

function build_dropship_file($id_orders){
#-----------------------------------------
# Created on: 09/14/2010  17:15:13 By  Roberto Barcenas
# Forms Involved: 
# Description : Genera un archivo de exportacion basado en configuracion del general.cfg
# Parameters : id_orders

	global $cfg,$va;
	
	$header_fields = explode(',',$cfg['dropship_titles']);
	$db_fields = explode(',',$cfg['dropship_fields']);
	$ncols = sizeof($db_fields);
	
	$dir = $cfg['path_dsfiles'];
	$fname = $cfg['dropship_name'] . '_' . date('Y-m-d') . '_' . str_replace(',','-',$id_orders) . '.csv';
	
	$sth = mysql_query("SELECT 
	sl_orders.ID_orders AS ID_orders,
	shp_name,
	shp_Address1,
	shp_Address2,
	shp_Address3,
	shp_Urbanization,
	shp_City,
	shp_State,
	shp_Zip,
	shp_Country,
	ID_stations,
	DNIS,
	ID_salesorigins,
	shp_Notes,
	sl_orders.Status AS OrderStatus,
	sl_orders.Date AS OrderDate,
	sl_customers.*,
	ID_products,
	Items,
	SumItem,
	SumService,
	SumTax,
	SumShipping,
	SumDiscount,
	tmpprod.OrderNet AS OrderNet,
	OrderTotal,
	NumItems,
	QtyItems,
	PayType,
	SumPayments,
	QtyPayments
FROM sl_orders
INNER JOIN
sl_customers
ON sl_orders.ID_customers = sl_customers.ID_customers 
INNER JOIN
(
	SELECT 
	ID_orders,
	GROUP_CONCAT(sl_products.ID_products) AS ID_products,
	GROUP_CONCAT(sl_orders_products.ID_products SEPARATOR '|') AS Items,
	SUM(IF(LEFT(sl_orders_products.ID_products,1) <> '6',SalePrice,0))AS SumItem,
	SUM(IF(LEFT(sl_orders_products.ID_products,1) = '6',SalePrice,0))AS SumService,
	SUM(Tax)AS SumTax,
	SUM(Shipping)AS SumShipping,
	SUM(sl_orders_products.Discount)AS SumDiscount,
	SUM(SalePrice-sl_orders_products.Discount)AS OrderNet,
	SUM(SalePrice-sl_orders_products.Discount+Shipping+Tax)AS OrderTotal,
	COUNT(sl_orders_products.ID_products) AS NumItems,
	GROUP_CONCAT(Quantity SEPARATOR '|') AS QtyItems
	FROM sl_orders_products
	INNER JOIN sl_products
	ON RIGHT(sl_orders_products.ID_products,6) = sl_products.ID_products
	WHERE ID_orders IN($id_orders) AND sl_orders_products.Status NOT IN('Order Cancelled','Inactive') AND DropShipment = 'Yes' GROUP BY ID_orders
)AS tmpprod
ON tmpprod.ID_orders = sl_orders.ID_orders
INNER JOIN
(
	SELECT 
	ID_orders,
	Type AS PayType,
	SUM(Amount)AS SumPayments,
	COUNT(*)AS QtyPayments
	FROM sl_orders_payments 
	WHERE ID_orders IN($id_orders) AND Status NOT IN('Order Cancelled', 'Cancelled')
	GROUP BY ID_orders
)AS tmppay
ON tmppay.ID_orders = sl_orders.ID_orders
WHERE sl_orders.ID_orders IN($id_orders); ");

	if(mysql_num_rows($sth) > 0){

		if ($handle = fopen($dir . $fname,'w')){
			fwrite($handle,$cfg['dropship_titles'] . "\r\n");
		}

		unset($va['dropship_orders_info']);
		$cols = array();
		$pattern = '/\s|-/';

		while ($rec = mysql_fetch_array($sth)){

			### Llenamos el arreglo
			for ($i=0; $i < $ncols; $i++){
				if($cols[$i] == ''){
					$tmpcols=array();
					### Si es columna compuesta
					if(preg_match($pattern,$db_fields[$i])){
						$tmpcols = explode(' ',$db_fields[$i]);
						(sizeof($tmpcols) == 0) and ($tmpcols = explode('-',$db_fields[$i]));
						for ($j=0; $j< sizeof($tmpcols); $j++){
							(preg_match('/-/',$db_fields[$i])) and ($cols[$i] .= $rec[$tmpcols[$j]] .'-');
							(preg_match('/\s/',$db_fields[$i])) and ($cols[$i] .= $rec[$tmpcols[$j]] . ' ');
						}
						chop($cols[$i],"-,\s");
					### Si es columna simple	
					}else{
						if($db_fields[$i] == 'NameItems' or $db_fields[$i] == 'ModelItems'){
						
							$sth = mysql_query("SELECT GROUP_CONCAT(Model SEPARATOR '|')AS ModelItems,GROUP_CONCAT(Name SEPARATOR '|') AS NameItems FROM sl_products WHERE ID_products IN(".$rec['ID_products'].");");
							list($model,$name) = mysql_fetch_row($sth);
							$rec['ModelItems'] = $model;
							$rec['NameItems'] = $name;
						}
						$cols[$i] = $rec[$db_fields[$i]];
					}
					$va['dropship_orders_info'] .= $header_fields[$i] . ' = '. $cols[$i] ."\r\n";
				}
			}
			
			if ($handle = fopen($dir . $fname,'a')){
				fwrite($handle,join(',', $cols)."\r\n");
				fclose($handle);
			}
			$va['dropship_orders_info'] .= "\r\n\r\n";

		}#end while

		if(is_readable($dir . $fname)){
			return $fname;
		}else{
			return -2;
		}
	}else{
		return -1;
	}
}


function send_mail_attachment($to, $subject, $message, $headers = '', $charset = 'utf-8', $files = array()){
#-----------------------------------------
# Created on: 09/15/2010  18:15:13 By  Roberto Barcenas
# Forms Involved: 
# Description : Esta funcion puede ser utilizada para enviar correos con o sin archivos adjuntos
# Parameters : para archivos adjuntos, recibe un arreglo con type,name y data (revisar funcion send_dropship_alert para ejemplo)


  global $cfg;

  if (!count($files))
  {
    $ext_headers  = $headers;
    $ext_headers .= "Content-Type: text/plain; charset=\"$charset\"\r\n";
    $ext_message  = $message;
  }
  else
  {
    $boundary = 'a6cd792e';
    while (true)
    {
      if (strpos($subject, $boundary) !== false ||
          strpos($message, $boundary) !== false) { $boundary .= dechex(rand(0, 15)) . dechex(rand(0, 15)); continue; }
      foreach ($files as $fi_name => $fi_data)
      if (strpos($fi_name, $boundary) !== false ||
          strpos($fi_data, $boundary) !== false) { $boundary .= dechex(rand(0, 15)) . dechex(rand(0, 15)); continue; }
      break;
    }

      $ext_headers  = $headers;
      $ext_headers .= "From: ". $cfg['cservice_email'] ."\r\nReply-To: ". $cfg['cservice_email'] ."\r\nBCC:". $cfg['mail_developer_rb'] ."\r\n";
      $ext_headers .= "MIME-Version: 1.0\r\n";
      $ext_headers .= "Content-Type: multipart/mixed; boundary=\"$boundary\"\r\n";

      $ext_message  = "This is a multi-part message in MIME format.";
      $ext_message .= "\r\n--$boundary\r\n";

      $ext_message .= "Content-Type: text/plain; charset=\"$charset\"\r\n\r\n";
      $ext_message .= $message;
      $ext_message .= "\r\n--$boundary\r\n";

    foreach ($files as $i => $x)
    {
      $ext_message .= "Content-Type: {$x['type']}; name=\"{$x['name']}\"\r\n";
      $ext_message .= "Content-Disposition: attachment\r\n";
      $ext_message .= "Content-Transfer-Encoding: base64\r\n\r\n";
      $ext_message .= chunk_split(base64_encode($x['data']));
      $ext_message .= "\r\n--$boundary\r\n";
    }
  }

  $error_reportings = error_reporting(E_ERROR | E_PARSE);
  $res = mail($to, $subject, $ext_message, $ext_headers);
  $error_reportings = error_reporting($error_reportings);

  return $res;
}

function verify_freeshp_bytotals(){
// --------------------------------------------------------
// Forms Involved: 
// Created on: 1 Oct 2010 16:25:45
// Author: MCC C. Gabriel Varela S.
// Description :   
// Parameters :
	global $cses,$cfg,$in,$va;

	if(array_key_exists('freeshp_bytotals_applied',$cses)){

		if($cses['total_i'] < $cses['freeshp_sale_min']){
			unset($cses['freeshp_bytotals_applied']);
			unset($cses['freeshp_sale_min']);
			
			for ($i=1;$i<=$cses[items_in_basket];$i++)
			{
				if ($cses['items_'.$i.'_qty']>0  and $cses['items_'.$i.'_id']>0)
				{
					$cses['items_'.$i.'_shp'.$cses['shp_type']]=$cses['items_'.$i.'_discshp'];
				}
			}
			
			$va['message'] .=  trans_txt('error_freeshp_bytotals');
			$in['message'] .=  trans_txt('error_freeshp_bytotals');
		}
	}
	update_cart_session();
}

function check_freeshp_bytotals(){
// --------------------------------------------------------
// Forms Involved: 
// Created on: 1 Oct 2010 16:26:26
// Author: MCC C. Gabriel Varela S.
// Description :   
// Parameters :
	global $cfg,$cses,$va,$in;
	if($cfg['freeshp_bytotal'])
	{
		if($cses['total_i']>$cfg['freeshp_sale_min'])
		{
			//Evalúa si no ha aplicado el descuento
			if(!$cses['freeshp_bytotals_applied'] or 1)
			{
				for ($i=1;$i<=$cses[items_in_basket];$i++){
					if ($cses['items_'.$i.'_qty']>0  and $cses['items_'.$i.'_id']>0){
						
						$cses['items_'.$i.'_discshp']=$cses['items_'.$i.'_shp'.$cses['shp_type']];
						if(isset($cses['items_'.$i.'_discount']) and $cses['items_'.$i.'_price']>$cses['items_'.$i.'_shp'.$cses['shp_type']] and !$cses['items_'.$i.'_discshp'])
						{
							$cses['items_'.$i.'_discount']+=$cses['items_'.$i.'_shp'.$cses['shp_type']];
						}
						else if($cses['items_'.$i.'_price']>$cses['items_'.$i.'_shp'.$cses['shp_type']] and !$cses['items_'.$i.'_discshp'])
						{
							$cses['items_'.$i.'_discount']=$cses['items_'.$i.'_shp'.$cses['shp_type']];
						}
						$cses['items_'.$i.'_shp'.$cses['shp_type']]=0;
						
					}
				}
			}
			$cses['freeshp_bytotals_applied']=1;
			$cses['freeshp_sale_min']=$cfg['freeshp_sale_min'];
			$va['message'] .= trans_txt('good_freeshp_bytotals').' $'.$cfg['freeshp_sale_min'].'.';
			$in['message'] .= trans_txt('good_freeshp_bytotals').' $'.$cfg['freeshp_sale_min'].'.';
			update_cart_session();
			save_callsession(0);
			return 1;
		}
		else
		{
			return -2;
		}
	}
	return -1;
}

function is_gift_cardable(){
// --------------------------------------------------------
// Forms Involved: 
// Created on: 23 Nov 2010 13:18:20
// Author: MCC C. Gabriel Varela S.
// Description :   
// Parameters :
	global $cses,$in,$cfg;
	if(isset($cfg['gift_card_use']) and $cfg['gift_card_use']==1)
	{
		if($cses['total_i']>=$cfg['gift_card_sale_min'])
			return 1;
		else
			return 0;
	}
	else
		return 0;


}

function calculate_gift_card_values(){
// --------------------------------------------------------
// Forms Involved: 
// Created on: 23 Nov 2010 13:52:25
// Author: MCC C. Gabriel Varela S.
// Description :   
// Parameters :
	global $cses,$cfg;
	$found=0;
	$value=0;
	for($i=1;$i<=$cfg['gift_card_total'] and $found==0;$i++)
	{
		if(isset($cfg['gift_card_min'.$i])and isset($cfg['gift_card_max'.$i])and $cses['total_i']>=$cfg['gift_card_min'.$i] and $cses['total_i']<=$cfg['gift_card_max'.$i])
		{
			$value=$cfg['gift_card_value'.$i];
			$found=$i;
		}
	}
	return array("value"=>$value,"expiration_days"=>$cfg['gift_card_expiration_days'.$found],"id_promo"=>$cfg['gift_card_id_promo'.$found],"percentage"=>$cfg['gift_card_percentage'.$i],"sale_min"=>$cfg['gift_card_coupon_sale_min'.$i],"url_external"=>$cfg['gift_card_url_external'.$i]);
}

function general_tracker($keypoint){
// --------------------------------------------------------
// Forms Involved: 
// Created on: 27 Dec 2010 15:36:16
// Author: MCC C. Gabriel Varela S.
// Description :   
// Parameters :
	global $cfg,$in,$cses;
	
	//Identifica si la IP se omitirá
	if(preg_match("/$_SERVER[REMOTE_ADDR]/",$cfg['exclude_ips']))
	{
		return;
	}
	
	include_once($cfg['geoip_path']."geoipcity.inc");
	include_once($cfg['geoip_path']."geoipregionvars.php");

// uncomment for Shared Memory support
// geoip_load_shared_mem("/usr/local/share/GeoIP/GeoIPCity.dat");
// $gi = geoip_open("/usr/local/share/GeoIP/GeoIPCity.dat",GEOIP_SHARED_MEMORY);

	$gi = geoip_open($cfg['geoip_path']."GeoLiteCity.dat",GEOIP_STANDARD);
	// $record = geoip_record_by_addr($gi,"24.24.24.24");
	$record = geoip_record_by_addr($gi,$_SERVER['REMOTE_ADDR']);

	geoip_close($gi);
	
	//echo "<!--".$_SERVER['HTTP_USER_AGENT'] . "-->\n\n";
	$values=get_browser(null,true);
	$user_agent='';
	$user_agent=$values['platform'].':'.$values['parent'];
	if($user_agent=='')
	{
		$user_agent=$_SERVER['HTTP_USER_AGENT'];
	}
	
	$sth = mysql_query("insert into innovausa.nsc_general_tracker set 
	Host='".$_SERVER['HTTP_HOST']."',
	user_agent='".$user_agent."',
	accept_language='".$_SERVER['HTTP_ACCEPT_LANGUAGE']."',
	accept_encoding='".$_SERVER['HTTP_ACCEPT_ENCODING']."',
	accept_charset='".$_SERVER['HTTP_ACCEPT_CHARSET']."',
	referer='".$_SERVER['HTTP_REFERER']."',
	server_name='".$_SERVER['SERVER_NAME']."',
	remote_address=inet_aton('".$_SERVER['REMOTE_ADDR']."'),
	redirect_query_string='".$_SERVER['REDIRECT_QUERY_STRING']."',
	redirect_url='".$_SERVER['REDIRECT_URL']."',
	query_string='".$_SERVER['QUERY_STRING']."',
	request_uri='".$_SERVER['REQUEST_URI']."',
	script_name='".$_SERVER['SCRIPT_NAME']."',
	/*php_self='".$_SERVER['PHP_SELF']."',*/
	keypoint='".$keypoint."',
	ID_orders='".$cses['id_orders']."',
	city='".$record->city."',
	state='".$record->region."',
	zipcode='".$record->postal_code."',
	Date=curdate(),
	Time=curtime()") or die("Query failed : " . mysql_error());

}


function get_facebook_like_button($like_type='xfbml',$url='',$like_cfg=array(), $url_args=array()){
// --------------------------------------------------------
// Forms Involved: 
// Created on: 30 Dec 2010 15:42:16
// Author: Roberto Barcenas.
// Description : Render a Facebook Like Button  
// Parameters : like_type[str]:iframe|xfbml ,like_setup:href|layout|show_faces|width|action|font|colorscheme|ref ,  $like_args[ary]: an array with additional arguments to the link

	global $cfg;
	
	if($cfg['facebook_like_show'] == 0){
		return '';
	}
	
	#($url=='') and ($url = $cfg['signin_urlconfirm'] . 'index.php');
	($url=='') and ($url = 'http://www.facebook.com/innovashop.tv');
	
	
	## Like Setup
	$like_setup['href'] = $url;
	$ary_setup = explode('|',$cfg['facebook_like_setup']);
	$like_setup['layout'] = $ary_setup[0];
	$like_setup['show_faces'] = $ary_setup[1];
	$like_setup['width'] = $ary_setup[2];
	$like_setup['action'] = $ary_setup[3];
	$like_setup['font'] = $ary_setup[4];
	$like_setup['colorscheme'] = $ary_setup[5];
	$like_setup['ref'] = $ary_setup[6];
	$like_setup['send'] = $ary_setup[7];
			
	## URL args
	if(count($url_args) > 0){
		$like_setup['href'] .= '?';
		while(list($key,$value) = each($url_args)){
				$like_setup['href'] .= $key.'='.$value.'&';
		}
		$like_setup['href'] = substr($like_setup['href'],0,-1);
	}
	
	
	if($like_type == 'iframe'){ 
		
		while(list($key,$value) = each($like_setup)){
			(array_key_exists($key,$like_cfg)) and  ($value = $like_cfg[$key]);
			$like_url .= $key.'='.$value.'&';
		}
		$like_url .= 'height=80&locale=es_LA';
	
		return '<iframe src="http://www.facebook.com/plugins/like.php?'.urlencode($like_url).'" scrolling="no" frameborder="0" style="border:none; overflow:hidden; width:'.$like_setup['width'].'px; height:80px;" allowTransparency="true"></iframe>';
		
	}else{
		
		while(list($key,$value) = each($like_setup)){
			(array_key_exists($key,$like_cfg)) and  ($value = $like_cfg[$key]);
			$like_url .= ' '.$key.'="'.$value.'" ';
		}
		
		return '<fb:like '.$like_url.'></fb:like>'; 
	}
}

function get_facebook_opgraph($opgrapgh_arg=array()){
// --------------------------------------------------------
// Forms Involved: 
// Created on: 31 Dec 2010 12:40:16
// Author: Roberto Barcenas.
// Description : Returns facebook metatags for opengraph  
// Parameters : opgrapgh_arg: array with the elements	
		
			global $cfg;
	
			$ary_options = explode('|',$cfg['facebook_opgraph']);
			$ary_default=array('title' => $cfg['app_title'],'type' => 'product','url' => $cfg['signin_urlconfirm'],
												'image'=> $cfg['signin_urlconfirm'].'images/facebook/fb.jpg','site_name' => $cfg['app_title'],
												'description' => 'Productos Fuera de lo ordinario.
												Como usted lo vio en la tele. Los productos más espectaculares y los productos fuera de lo ordinario.');
			unset($str);
			$ary_default['url'] = str_replace('https','http',$ary_default['url']);
			$opgrapgh_arg['url'] = str_replace('https','http',$opgrapgh_arg['url']);
			$ary_default['image'] = str_replace('https','http',$ary_default['image']);
			$opgrapgh_arg['image'] = str_replace('https','http',$opgrapgh_arg['image']);
		
			while(list(,$value) = each($ary_options)){
					if(array_key_exists($value,$opgrapgh_arg)){
						$ary_default[$value] = $opgrapgh_arg[$value];	
					}
					$str .= '<meta property="og:'.$value.'" content="'.$ary_default[$value].'"/>'."\r\n";
			}
			$str .= '<meta property="fb:admins" content="'.$cfg['facebook_uid'].'"/>'."\r\n";
	
			if($cfg['opgraph_curl_reset'] === TRUE){
	
					// create curl resource
		      $ch = curl_init(); 
		      // set url
		      curl_setopt($ch, CURLOPT_URL, $ary_default['url'] );
		      curl_setopt($ch, CURLOPT_SSL_VERIFYPEER, false);
		      // $output contains the output string
		      $output = curl_exec($ch);
					// close curl resource to free up system resources
		      curl_close($ch);
    	}
      
			return $str;
	
}

function select_birthday_day(){
// --------------------------------------------------------
// Forms Involved: 
// Created on: 11 Mar 2011 11:58:14
// Author: MCC C. Gabriel Varela S.
// Description :   
// Parameters :
	$return='<select class="inputbox" name="birthday_day" id="birthday_day" onfocus="focusOn( this )" onblur="focusOff( this )" >';
	$return.="<option value=''>---</option>";
	for($day=1;$day<=31;$day++)
	{
		$return.="<option value=$day>$day</option>";
	}
	$return.='</select>';
	return $return;
}

function validate_customer($id_customers,$id_orders){
// --------------------------------------------------------
// Forms Involved: 
// Created on: 4/4/11 5:32 PM
// Author: MCC C. Gabriel Varela S.
// Description :   
// Parameters :
//Verifica que exista el cliente
//Last modified on 04/12/11 03:00:54 PM
//Last modified by: MCC C. Gabriel Varela S. : Se integra decodificación base64
//Last modified on 1 Jun 2011 13:05:40
//Last modified by: MCC C. Gabriel Varela S. :The user id is fixed to 4688
	global $usr,$in,$cfg;
	$sth = mysql_query("select * 
	from sl_orders 
	where ID_customers='".base64_decode(mysql_real_escape_string($id_customers))."' 
	and ID_orders='".base64_decode(mysql_real_escape_string($id_orders))."'") or die("Query failed : " . mysql_error());
	if(mysql_num_rows($sth) ==1)
	{
		mysql_query("insert into sl_orders_notes set ID_orders='".base64_decode(mysql_real_escape_string($id_orders))."',notes='Se confirmó producto gratis vía Innovashop',Type='Low',Date=curdate(),Time=curtime(),ID_admin_users='$cfg[id_admin_users]';") or die("Query failed : " . mysql_error());
		$in['message'].=trans_txt('customer_validated');
	}
	else
	{
		$in['message'].=trans_txt('customer_not_validated');
	}
}

function get_reward_points($id_orders,$id_customers){
// --------------------------------------------------------
// Forms Involved: 
// Created on: 4/6/11 4:29 PM
// Author: MCC C. Gabriel Varela S.
// Description :   
// Parameters :
	$sth = mysql_query("Select * 
	from sl_customers_points 
	where 
	ID_orders='$id_orders' 
	and ID_customers='$id_customers' 
	and Status='Active'") or die("Query failed : " . mysql_error());
	$rec = mysql_fetch_assoc($sth);
	return $rec['Points'];
}

function get_reward_products(){
// --------------------------------------------------------
// Forms Involved: 
// Created on: 4/6/11 6:12 PM
// Author: MCC C. Gabriel Varela S.
// Description :   
// Parameters :
//Last modified on 26 May 2011 19:05:41
//Last modified by: MCC C. Gabriel Varela S. : the way it works is changed to take in account the records in sl_customers_points instead of sl_reward_points_gifts
//Last modified on 27 May 2011 12:18:34
//Last modified by: MCC C. Gabriel Varela S. :get_total_reward_points is removed
	global $cfg,$va,$usr;
	$output="";
	
	$sth = mysql_query("Select * 
	from sl_customers_points
	where ID_customers='$usr[id_customers]'
	and ID_products!=''
	and not isnull(ID_products)
	and Status='Active'
	and (isnull(UsedOn)or UsedOn='' or UsedOn='0000-00-00')
	and expiration>=curdate()
	order by Date asc
	limit 1") or die("Query failed : " . mysql_error());
	$rec = mysql_fetch_assoc($sth);
	$product_name='';
	if($rec['ID_products']!='')
	{
		$va['reward_pic'] = '<img src="/images/reward_points/'.intval($rec['ID_products']).'.png">';
		$product_name=load_name('sl_products','ID_products',$rec['ID_products'],'Name');
		$output .= "<input type='hidden' name='id_products' value='$rec[ID_products]'><strong>$product_name</strong><br>\n";
	}
	return $output;
}

function get_total_reward_points($id_customers){
// --------------------------------------------------------
// Forms Involved: 
// Created on: 4/7/11 9:32 AM
// Author: MCC C. Gabriel Varela S.
// Description :   
// Parameters :
	$sth = mysql_query("Select sum(Points)as Points from sl_customers_points where ID_customers='$id_customers' and Status='Active'") or die("Query failed : " . mysql_error());
	$rec = mysql_fetch_assoc($sth);
	return $rec['Points'];
}

function check_reward_points(){
// --------------------------------------------------------
// Forms Involved: 
// Created on: 4/7/11 10:35 AM
// Author: MCC C. Gabriel Varela S.
// Description :   
// Parameters :
//Last modified on 27 May 2011 12:18:58
//Last modified by: MCC C. Gabriel Varela S. :get_total_reward_points is removed. expiration is considered
	global $in,$va,$cses,$cfg,$usr;

	if(!empty($cfg['reward_points_use']) and ($in['id_products']!='' or $cses['reward_id_products_to_apply'] != '') and !isset($cses['reward_points_applied']))
	{
		(isset($cses['reward_id_products_to_apply'])) and ($in['id_products'] = $cses['reward_id_products_to_apply']);
		$query = "Select 
		if(Status='Active',1,0)as isactive,
		/*if(curdate()<=expiration,1,0)as isvalid,*/
		id_products,
		Points_needed,
		minimum_external,
		Status 
		from sl_reward_points_gifts 
		where id_products='".mysql_real_escape_string($in['id_products'])."';";
		$sth = mysql_query($query) or die("Query failed : Sss" . mysql_error());
		
		if(mysql_num_rows($sth) == 0){
		 	return array(-1,0,'',0,0,'Invalid');
		}
		
		/*Aquí se obtienen los datos*/
		$rec = mysql_fetch_assoc($sth);
		
		if($rec['isactive']==0)
		{
			return array(-4,$rec['isactive'],$rec['id_products'],$rec['Points_needed'],$rec['minimum_external'],$rec['Status']);
		}
		
// 		if($rec['isvalid']==0)
// 		{
// 			return array(-5,$rec['isactive'],$rec['id_products'],$rec['Points_needed'],$rec['minimum_external'],$rec['Status']);
// 		}
		
		if($cses['total_i'] < $rec['minimum_external']){
			return array(-2,$rec['isactive'],$rec['id_products'],$rec['Points_needed'],$rec['minimum_external'],$rec['Status']);
		}
		
// 		if(get_total_reward_points($usr['id_customers'])<$rec['Points_needed'])
// 		{
// 			return array(-5,$rec['isactive'],$rec['id_products'],$rec['Points_needed'],$rec['minimum_external'],$rec['Status']);
// 		}
		
		// Producto de Regalo?
		if($rec['id_products'] != '' and strlen($rec['id_products']) >= 6){
				(strlen($rec['id_products']) == 9) and ($rec['id_products'] = substr($rec['id_products'],-6) );


				## Agregamos el producto al carrito
				++$cses['items_in_basket'];
				++$cses['products_in_basket'];
				if(build_edit_choices_module($in['id_products'],'','','')==''){
					$cses['items_'.$cses['items_in_basket'].'_id']="100$rec[id_products]";
				}else{
					$cses['items_'.$cses['items_in_basket'].'_id']="999$rec[id_products]";
				}
				
				$cses['items_'.$cses['items_in_basket'].'_qty']+=1;
				$cses['items_'.$cses['items_in_basket'].'_payments']=1;
				$cses['items_'.$cses['items_in_basket'].'_paytype']= isset($in['paytype']) ? $in['paytype'] : $cses['paytype'];
				$cses['items_'.$cses['items_in_basket'].'_price']= isset($cfg['reward_points_id_promo_price']) ? $cfg['reward_points_id_promo_price'] : 0;
				$cses['items_'.$cses['items_in_basket'].'_desc']= load_name('sl_products','ID_products',$rec['id_products'],'Name');
				$cses['items_'.$cses['items_in_basket'].'_discount']=0;
				$cses['items_'.$cses['items_in_basket'].'_coupon_discount']=0;
				$cses['items_'.$cses['items_in_basket'].'_reward_points']=1;
				
				$today=getdate();
				$cses['items_'.$cses['items_in_basket'].'_year']=$today['year'];
				$cses['items_'.$cses['items_in_basket'].'_month']=trans_txt('mon'.$today['mon']);
				$cses['items_'.$cses['items_in_basket'].'_day']=$today['mday'];
				
				$cses['items_'.$cses['items_in_basket'].'_shp1']=isset($cfg['reward_points_id_promo_shipping']) ? $cfg['reward_points_id_promo_shipping'] : 0;
				$cses['items_'.$cses['items_in_basket'].'_shp2']=isset($cfg['reward_points_id_promo_shipping']) ? $cfg['reward_points_id_promo_shipping'] : 0;
				$cses['items_'.$cses['items_in_basket'].'_shp3']=isset($cfg['reward_points_id_promo_shipping']) ? $cfg['reward_points_id_promo_shipping'] : 0; 
				$cses['item_reward_points'] = $cses['items_in_basket'];
				
				//Calcular tax
				$cses['items_'.$cses['items_in_basket'].'_tax']=($cses['items_'.$cses['items_in_basket'].'_price']-$cses['items_'.$cses['items_in_basket'].'_discount']-$cses['items_'.$cses['items_in_basket'].'_coupon_discount'])*$cses['items_'.$cses['items_in_basket'].'_qty']*$cses['tax_total'];
			
// 				$cses['item_promo'] = $cses['items_in_basket'];
				//mysql_query("Update sl_coupons_external set Status='Used' where ID_coupons_external= " . $rec['ID_coupons_external'] . ";");						
				$discount_amt=0;
		}
		
		//$cses['items_discounts']=$discount_amt;
		$cses['reward_points_applied']=1;
		//Registra código utilizado
		$cses['reward_points_used']=$rec['id_products'];
		$cses['reward_points_minimum_external']=$rec['minimum_external'];
		$va['message']	=	trans_txt('good_reward_points');
		update_cart_session();
		save_callsession(0);
		//Actualiza los puntos
// 		sub_reward_points($usr['id_customers'],$rec['Points_needed']);
		//Finaliza actualización de puntos
		return array(1,$rec['isactive'],$rec['id_products'],$rec['Points_needed'],$rec['minimum_external'],$rec['Status']);
	}
	else
	{
		return array(-3,$rec['isactive'],$rec['id_products'],$rec['Points_needed'],$rec['minimum_external'],$rec['Status']);
	}
}

function sub_reward_points($id_customers,$points){
// --------------------------------------------------------
// Forms Involved: 
// Created on: 4/7/11 11:55 AM
// Author: MCC C. Gabriel Varela S.
// Description :   
// Parameters :
//Last modified on 27 May 2011 13:11:25
//Last modified by: MCC C. Gabriel Varela S. :the way it works is changed
	
	global $cses,$usr;
	$sth = mysql_query("update sl_customers_points
	set Status='Used',UsedOn=curdate()
	where ID_customers='$usr[id_customers]'
	and ID_products!=''
	and not isnull(ID_products)
	and Status='Active'
	and (isnull(UsedOn)or UsedOn='' or UsedOn='0000-00-00')
	and expiration>=curdate()
	and ID_products='$cses[reward_points_used]'
	order by Date asc
	limit 1") or die("Query failed : " . mysql_error());
	$rec = mysql_fetch_assoc($sth);
	
	return 1;
}

function verify_reward_points(){
// --------------------------------------------------------
// Forms Involved: 
// Created on: 4/8/11 9:35 AM
// Author: MCC C. Gabriel Varela S.
// Description :   
// Parameters :
//Last modified on 04/12/11 05:25:00 PM
//Last modified by: MCC C. Gabriel Varela S. : Se hace que se pueda borrar y aplicar nuevamente
	global $cses,$cfg,$in,$va;

	
	if(array_key_exists('reward_points_used',$cses)){
  
		if($cses['total_i'] < $cses['reward_points_minimum_external']){
			
			unset($cses['reward_points_used']);
			unset($cses['reward_points_applied']);
			unset($cses['reward_points_minimum_external']);
			$va['message'] =  trans_txt('error_reward_points');
			$in['message'] =  trans_txt('error_reward_points');
			if($cses['item_reward_points'] != '' and isset($cses['items_'. $cses['item_reward_points'] .'_id'])){
				unset($cses['items_'. $cses['item_reward_points'] .'_id']);
				unset($cses['items_'. $cses['item_reward_points'] .'_qty']);
				unset($cses['items_'. $cses['item_reward_points'] .'_price']);
				unset($cses['items_'. $cses['item_reward_points'] .'_payments']);
				unset($cses['item_reward_points']);
				--$cses['products_in_basket'];
			}
		}
	}
	if($in['do']!='' and $cses['item_reward_points'] != '' and $in['do']==$cses['item_reward_points']){
		unset($cses['reward_points_used']);
		unset($cses['reward_points_applied']);//borrar applied de verdad?
		unset($cses['item_reward_points']);
		unset($cses['reward_points_minimum_external']);
	}
	update_cart_session();
}


function check_404(){
// --------------------------------------------------------
// Forms Involved:
// Created on: 12/19/2011 15:36
// Author: Roberto Barcenas
// Description : Revisa los errores 404 para filtrar intentos de ataque
// Parameters :
# Last Modified by OS on 02/14/2012: Se distigue de urls finalizadas en '-a','-d','-p','-e'

	global $cfg;

	$keywords_file = $cfg['blacklist_path'] . 'keywords.txt';
	$blackwords_file = $cfg['blacklist_path'] . 'blackwords.txt';
	$blacklist_file  = $cfg['blacklist_path'] . 'blacklist.txt';
	$this_file = substr($_SERVER['REDIRECT_URL'],1);
	$url = 'http://'.$cfg['maindomain'] . '/' . $this_file ;
	$this_ip = $_SERVER['REMOTE_ADDR'];
	$arr_htaccess_rewrite = array('-a','-d','-p','-e');

	if(strlen($this_file) > 2){

		// Using the optional flags parameter since PHP 5
		$blackwords_array = file($blackwords_file, FILE_IGNORE_NEW_LINES | FILE_SKIP_EMPTY_LINES);


		## Evaluate hacking attempt
		while(list($key,$blackword) = each($blackwords_array)){

			#echo "Evaluando File:$blackword vs KeyWord:$this_file<br>";

			if(stripos($this_file,$blackword) !== FALSE ){

				#print "Palabra prohibida $this_file<br>";
				// Using the optional flags parameter since PHP 5
				$blacklist_array = file($blacklist_file, FILE_IGNORE_NEW_LINES | FILE_SKIP_EMPTY_LINES);

				while(list($key,$black_ip) = each($blacklist_array)){

					#echo "Evaluando $black_ip vs $this_ip<br>";
					if(ip2long($this_ip) == ip2long($black_ip)){
						print "$black_ip == $this_ip<br>";
						$store_this = 1;
						break;
					}

				}

				if(empty($store_this)){
					#print "Guardando IP nueva:$this_ip<br>";
					$fp = fopen($blacklist_file,'a');
					fwrite($fp, $this_ip."\n");
					fclose($fp);
				}else{
					#echo "IP Domain already blocked<br>";
				}

				$flag=1;
				break;
			}
		}

		if(empty($flag)){
			## Possible keyword missed
			$fp = fopen($keywords_file,'a');
			fwrite($fp, "$this_ip\t$this_file\t$url\t".date('M-Y')."\n");
			fclose($fp);

			$cabeceras_sm  = 'MIME-Version: 1.0' . "\r\n";
			$cabeceras_sm .= 'Content-type: text/html; charset=utf-8' . "\r\n";
			$cabeceras_sm .= 'From: '.$cfg['app_title'].'<'.$cfg['cservice_email'].'>' . "\r\n";
			$cabeceras_sm .= 'Cc: ' . $cfg['mail_developer_ac'] . "\r\n";

			$subject = in_array(substr(trim($this_file),-2), $arr_htaccess_rewrite) ? 'Posible link roto' : 'Error 404';
			$body = "IP:$this_ip<br>File:$url";

			@mail($cfg['mail_developer_rb'],$subject,$body,$cabeceras_sm);

		}
	}
}

function get_cc_years(){
// --------------------------------------------------------
// Forms Involved:
// Created on: 01/05/2012 11:41
// Author: Roberto Barcenas
// Description : Devuelve dropdownmenu con valores para anio
// Parameters :

	$i=0;
	while($i<10){
		$short=date("y")+$i;
		$long=date("Y")+$i;
		$option .= '<option value="'.$short.'">'.$long.'</option>';
		$i++;
	}
	print $option;
}


function replace_in_string($str_txt=''){
// --------------------------------------------------------
// Forms Involved:
// Created on: 01/12/2012 12:29
// Author: Roberto Barcenas
// Description : Devuelve la cadena eliminando contenido dentro de []
// Parameters :

	$pattern='/\[.*?\]/';

	$str_txt = preg_replace($pattern,'',$str_txt);
	return $str_txt;

}

function set_data_profiler($action, $data=''){
    // --------------------------------------------------------
    // Forms Involved:
    // Created on: 29/05/2012 11:00
    // Author:
    // Description :
    // Parameters :
    $valid_data = filter_profiler($action, $data);
    if($valid_data){
        set_session_profiler();
        if(!empty($action)){
            $idsession = get_session_profiler();
             
            if(!empty($idsession)){
                set_curl_profiler($idsession, $action, $data);
            }
        }
    }
}

function set_session_profiler(){
    // --------------------------------------------------------
    // Forms Involved:
    // Created on: 25/05/2012 17:29
    // Author:
    // Description :
    // Parameters :
    $idsession = get_session_profiler();
    if(empty($idsession)){
        create_new_session_profiler();
    }
}

function set_curl_profiler($idsession, $action, $data){
    // --------------------------------------------------------
    // Forms Involved:
    // Created on: 25/05/2012 17:29
    // Author:
    // Description :
    // Parameters :
    //http://www.innovashop.tv/profiler/index.php
    //http://dev.profiler.com/index.php

    global $cfg;
    $data = urlencode($data);
    $url = $cfg['prof_urlsend']."?s=".$idsession."&a=".$action."&d=".$data."&e=".$cfg['prof_ecomm'];
    
    $handler = curl_init($url);
    $response = curl_exec ($handler);
    curl_close($handler);
}

function create_new_session_profiler(){
    // --------------------------------------------------------
    // Forms Involved:
    // Created on: 25/05/2012 17:29
    // Author:
    // Description :
    // Parameters :

    $idsession = make_idsession();
    setcookie("sesprf", base64_encode($idsession), time() + (20 * 365 * 24 * 60 * 60));
     
    return $idsession;
}

function get_session_profiler(){
    // --------------------------------------------------------
    // Forms Involved:
    // Created on: 25/05/2012 15:00
    // Author:
    // Description :
    // Parameters :
     
    return $_COOKIE["sesprf"];
}

function make_idsession(){
    // --------------------------------------------------------
    // Forms Involved:
    // Created on: 25/05/2012 14:29
    // Author:
    // Description :
    // Parameters :
     
    return (intval(rand(1,100000))).time().(intval(rand(1,1000000000)));
}

function filter_profiler($action, $data){
    // --------------------------------------------------------
    // Forms Involved:
    // Created on: 25/05/2012 14:29
    // Author:
    // Description :
    // Parameters :

    global $cfg;
    $domain = $cfg['maindomain'];
    $response = true;

    if(!empty($action) && !empty($data)){
        if($action==4){
            $response = search_url_filter($domain, $data);
        }
        return $response;
    }
}

function search_url_filter($domain, $url){
    // --------------------------------------------------------
    // Forms Involved:
    // Created on: 25/05/2012 14:29
    // Author:
    // Description :
    // Parameters :

    $isvalid_domain = false;
    $isvalid_words  = true;
    $response = false;
    $words = array();
    $words[] = "google";
    $words[] = "gclid";

    if (preg_match('/^(http|https):\/\/('.$domain.')\/.*$/', $url)) {
        $isvalid_domain = true;
    }
    for($j=0;$j<count($words);$j++){
        if(preg_match('/'.$words[$j].'/i', $url)){
            $isvalid_words = false;
            break;
        }
    }
    if($isvalid_domain == true && $isvalid_words == true){
        $response = true;
    }
    return $response;
}



#########################################################	
#	Function: load_adwords_conversion_files
#   		- This function receives the new Order ID generated and load adwords conversion files
#
#	Created by:
#		_Roberto Barcenas_
#
#	Modified By:
#
#
#   	Parameters: 
#			- ID Order
#
#   	Returns:
#				- Load Adword files
#   	See Also:
#				- checkout_neworder.html
#
function load_adwords_conversion_files($id_orders=0){
#########################################################

	global $cfg,$local;

	if($local == 's12.shoplatinotv.com'){

		load_object("/objects/adwords_general.html");

		$q1 = "SELECT Adwords_file FROM sl_orders_products INNER JOIN sl_products_prior
				ON RIGHT(sl_orders_products.ID_products, 6) = sl_products_prior.ID_products
				WHERE ID_orders = '".intval($id_orders)."' AND BelongsTo = '".$cfg['owner']."' 
				AND Adwords_file IS NOT NULL GROUP BY Adwords_file;";

		$sth = mysql_query($q1);
		$rows = mysql_numrows($sth);

		if($rows > 0){
			while(list($file) = mysql_fetch_row($sth)){
				load_object('/objects/adwords_'.$file.'.html');
			}
		}

	}
}


#########################################################	
#	Function: get_mobile_categories
#   		- Generates the categories for mobile content
#
#	Created by:
#		_Roberto Barcenas_
#
#	Modified By:
#
#   	Parameters: 
#
#   	Returns:  $va['categories']
# 
#   	See Also:
#
function get_mobile_categories(){
#########################################################
	global $va,$cfg;

  $query = mysql_query("SELECT GROUP_CONCAT(DISTINCT `Title`)
  FROM `sl_products_w`
  INNER JOIN sl_products_prior
  USING(ID_products)
  WHERE sl_products_w.`BelongsTo` = '".$cfg['owner']."'
  AND sl_products_prior.`BelongsTo` = '".$cfg['owner']."'
  AND `Title` IS NOT NULL AND Status IN('Web Only','On-Air')");
  list($c) = mysql_fetch_row($query);
  $categories = explode(',', $c);
  sort($categories);

  foreach ($categories as $category) {
    $img_name = strtolower(substr($category,0,3)) == 'rel' ? strtolower(substr($category,1,3)) : strtolower(substr($category,0,3));
    $va['categories'] .= '<a href="/'.$category.'-b" class="glow"><img src="/mobile/images/ico-'.$img_name.'.png" border="0" width="90px"></a>'."\n";
  }
 
}


#########################################################	
#	Function: set_device_note
#   		- Guarda una nota en la orden con la informacion del dispositivo de acceso
#
#	Created by:
#		_Roberto Barcenas_
#
#	Modified By:
#
#   	Parameters: id_orders 
#
#   	Returns: 
# 
#   	See Also:
#
function set_device_note($id_orders){
#########################################################

	global $device,$cfg;

	if(!empty($device['is_mobile_device'])){

		foreach ($device as $key => $value) {
			$value = !empty($value) ? $value : 'N/A';
			$str .= ucfirst(str_replace(array('is_','_'), array('',' '), $key)) . ' = ' . $value . "\n";
		}
		$q = "INSERT INTO sl_orders_notes SET ID_orders='".intval($id_orders)."',Notes='Informacion de Dispositivo\n$str\n',Type='Low',Date=CURDATE(),Time=CURTIME(),ID_admin_users='$cfg[id_admin_users]';";
		mysql_query($q) or die("Query failed : " . mysql_error());

	}

}


function get_values() {
	global $in;
	foreach ($_GET as $key=>$value ) {
		if($value != '[QSA]'){
			if (in_array(strtolower($key), $in)){
				$in[strtolower($key)] .= "|$value";
			}else{
				$in[strtolower($key)] = $value;
			}
		}
	}
    
	foreach ($_POST as $key=>$value ) {
		if (in_array(strtolower($key), $in)){
			$in[strtolower($key)] .= "|$value";
		}else{
			$in[strtolower($key)] = $value;
		}
	}

}

?>
