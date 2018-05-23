<?php
function detectarAddenda($rfc='', $id_customer = 0){
	if(file_exists(ADDENDAS.$rfc.'_'.$id_customer.'.php')){
		return $rfc.'_'.$id_customer;
	}elseif(file_exists(ADDENDAS.$rfc.'.php')){
		return $rfc;
	}else{
		return '';
	}
}
function send_gmail( $to, $subject, $ext_message ){
	require_once __DIR__."/../libs/phpmailer/class.phpmailer.php";
	global $cfg;

	$mail             = new PHPMailer();

	$mail->IsSMTP(); 										// telling the class to use SMTP
	$mail->Host       = "smtp.gmail.com"; 		// SMTP server
	$mail->SMTPDebug  = 0;                     				// enables SMTP debug information (for testing)
	                                           				// 1 = errors and messages
	                                           				// 2 = messages only
	$mail->SMTPSecure = 'tls';
	$mail->SMTPAuth   = true;                  				// enable SMTP authentication
	$mail->Host       = "smtp.gmail.com"; 		// sets the SMTP server
	$mail->Port       = 587;                    			// set the SMTP port for the GMAIL server
	$mail->Username   = $cfg['gmail_username']; 			// SMTP account username
	$mail->Password   = $cfg['gmail_passwd'];       		// SMTP account password

	$mail->SetFrom($cfg['gmail_username']);

	$mail->Subject    = $subject;
	$mail->MsgHTML($ext_message);

	$list = explode(',', $to);
	foreach ($list as $value) {
		$mail->AddAddress($value, '');
	}

	if(!$mail->Send()) {
	  echo "Mailer Error: " . $mail->ErrorInfo;
	  return 0;
	} else {
	  echo "Message sent!";
	  return 1;
	}
}

function getRFC($e = EMPRESA){
	global $cfg;
	if(isset($cfg['finkok_test_mode']) && $cfg['finkok_test_mode'] == 1)
	 	return 'ACO560518KW7';
	if($e == '11')
		return 'IML121023RE5';
	if($e == '4')
		return 'MOW1109201Y3';
	if($e == '2')
		return 'TLO1108314G2';
	if($e == '15')
		return 'TDS150924MR4';
	if($e == '3')
		return 'CMU060119UI7';

	// if($e == '')
	return false;
}
function parseConsoleArg($argv) {
    $_ARG = array();
    foreach ($argv as $arg) {
      if (preg_match('/--([^=]+)=(.*)/',$arg,$reg)) {
        $_ARG[$reg[1]] = $reg[2];
      } elseif(preg_match('/-([a-zA-Z0-9])/',$arg,$reg)) {
            $_ARG[$reg[1]] = 'true';
        }
  
    }
  return $_ARG;
}
function getKeyAndNumCert($rfc=''){
	global $cfg;
	if(isset($cfg['finkok_test_mode']) && $cfg['finkok_test_mode'] == 1)
	 	return array('pwd'=>'12345678a','cert'=>'20001000000300005692');
	if($rfc == 'TLO1108314G2')
		return array('pwd'=>'RoSYMC61','cert' =>'00001000000407020717');
	if($rfc == 'IML121023RE5')
		return array('pwd'=>'SUR3548j','cert'=>'00001000000407540450');
	if($rfc == 'MOW1109201Y3')
		return array('pwd'=>'Intweb1109','cert'=>'00001000000407500072');
	if($rfc == 'TDS150924MR4')
		return array('pwd'=>'IKMDLSja','cert'=>'00001000000400954554');
	if($rfc == 'CMU060119UI7')
		return array('pwd'=>'2MufAr18','cert'=>'00001000000405464452');

	return false;
}
function pintar($var,$type='var'){
	if($type== 'xml'){
		header("Content-type: text/xml");
		echo $var;
	}
}
function logg($data='',$fileName= 'log'){
	// if(PRINT_LOG){
	// 	$handle = fopen($fileName,'a');
	// 	fwrite($handle,$data.', '.date('Y-m-d @ H:i:s').PHP_EOL);
	// 	fclose($handle);
	// }
}
function clearArray($matriz){
	foreach($matriz as $key=>$value){
		$matriz[$key] = limpiar($value);
	}
	return $matriz;
} 
function limpiar($String){
	$String = utf8_encode($String);
    $String = str_replace(array('á','à','â','ã','ª','ä'),"a",$String);
    $String = str_replace(array('Á','À','Â','Ã','Ä'),"A",$String);
    $String = str_replace(array('Í','Ì','Î','Ï'),"I",$String);
    $String = str_replace(array('í','ì','î','ï'),"i",$String);
    $String = str_replace(array('é','è','ê','ë'),"e",$String);
    $String = str_replace(array('É','È','Ê','Ë'),"E",$String);
    $String = str_replace(array('ó','ò','ô','õ','ö','º'),"o",$String);
    $String = str_replace(array('Ó','Ò','Ô','Õ','Ö'),"O",$String);
    $String = str_replace(array('ú','ù','û','ü'),"u",$String);
    $String = str_replace(array('Ú','Ù','Û','Ü'),"U",$String);
    $String = str_replace(array('[','^','´','`','¨','~',']'),"",$String);
    $String = str_replace("ç","c",$String);
    $String = str_replace("Ç","C",$String);
    $String = str_replace("ñ","n",$String);
    $String = str_replace("Ñ","N",$String);
    $String = str_replace("Ý","Y",$String);
    $String = str_replace("ý","y",$String);
     
    $String = str_replace("&aacute;","a",$String);
    $String = str_replace("&Aacute;","A",$String);
    $String = str_replace("&eacute;","e",$String);
    $String = str_replace("&Eacute;","E",$String);
    $String = str_replace("&iacute;","i",$String);
    $String = str_replace("&Iacute;","I",$String);
    $String = str_replace("&oacute;","o",$String);
    $String = str_replace("&Oacute;","O",$String);
    $String = str_replace("&uacute;","u",$String);
    $String = str_replace("&Uacute;","U",$String);
    return $String;
}
function show($var,$type='var'){
	if(DEBUG){
		echo '<pre style="width: 95%; background: yellow none repeat scroll 0% 0%; font-weight: bold; padding: 27px; white-space: pre-wrap;">';
		if($type == 'var'){
			print_r(@$var);
		}elseif ($type == 'xml' || $type == 'html') {
			echo htmlentities($var);
		}
		echo '</pre>';
	}
}
function isNumberArray($array){
	if(!is_array($array))
		return FALSE;
	foreach(array_keys($array) as $key) {
		if (!is_int($key)) return FALSE;
    }
	return TRUE;
}
function load_in_data_(){
	$in = array();
	$in['thisurl'] = '';
	foreach ($_GET as $key => $value) {
		if (substr(strtolower($key), 0, 4) == "chk:") {
			list ($aux, $name) = split(":", $key);
			$name = str_replace("_", " ", $name);
			if (array_key_exists(strtolower($value), $in)) {
				$in[strtolower($value)] .= "|$name";
			} else {
				$in[strtolower($value)] .= "$name";
			}
		} else {
			$in[strtolower($key)] = $value;
		}
		if (strtolower($key) != 'help') {
			$in['thisurl'] .= strtolower($key) . "=$value&";
		}
	}
	foreach ($_POST as $key => $value) {
		if (substr(strtolower($key), 0, 4) == "chk:") {
			list ($aux, $name) = split(":", $key);
			$name = str_replace("_", " ", $name);
			if (array_key_exists(strtolower($value), $in)) {
				$in[strtolower($value)] .= "|$name";
			} else {
				$in[strtolower($value)] .= "$name";
			}
		} else {
			$in[strtolower($key)] = $value;
		}
		if (strtolower($key) != 'help') {
			$in['thisurl'] .= strtolower($key) . "=$value&";
		}
	}
	$in['thisurl'] = substr($in['thisurl'],0,-1);
	return $in;
}


function load_sys_data_($e = '') {
	$sys = array();
	$cfg = array();
	$cfg_folder = CFG_FOLDER;
	$local = PREFIX_CONFIG;
	if (file_exists($cfg_folder . "/general." . $local . ".cfg")) {
		if ($handle = fopen($cfg_folder . "/general." . $local . ".cfg", 'r')) {
			while (!feof($handle)) {
				$line = fgets($handle);
				if(strpos($line,'|') !== FALSE and $line[0] != '#'){
					list($type,$name,$value) = preg_split("/\||=/", $line, 3);
					if ($type == 'sys') {
						$sys[$name] = trim($value);
					} elseif ($type == 'conf' or $type == 'conf_local') {
						$cfg[$name] = trim($value);
					}
				}else{
					continue;
				}
			}
		}
	}

	if (file_exists($cfg_folder . "/general." . $local . ".e" . $e . ".cfg")) {
		if ($handle = fopen($cfg_folder . "/general." . $local . ".e" . $e . ".cfg", 'r')) {
			while (!feof($handle)) {
				$line = fgets($handle);
				if(strpos($line,'|') !== FALSE and $line[0] != '#'){
					$arry = preg_split("/\||=/", $line, 3);
					if(count($arry) == 3)
						list($type, $name, $value) = $arry;
					if ($type == 'sys') {
						$sys[$name] = trim($value);
					} elseif ($type == 'conf') {
						$cfg[$name] = trim($value);
					}
				}else{
					continue;
				}

			}
		}
	}

	if (file_exists($cfg_folder . '/general.e' . $e . '.cfg')) {
		if ($handle = fopen($cfg_folder . '/general.e' . $e . '.cfg', 'r')) {
		while (!feof($handle)) {
				$line = fgets($handle);
				if(strpos($line,'|') !== FALSE and $line[0] != '#'){
					$arry = preg_split("/\||=/", $line, 3);
					if(count($arry) == 3)
						list($type, $name, $value) = $arry;
					$cfg[$name] = trim($value);
				}else{
					continue;
				}
			}
		}
	}

	if (file_exists($cfg_folder . '/general.ex.cfg')) {            
		if ($handle = fopen($cfg_folder . '/general.ex.cfg', 'r')) {
			while (!feof($handle)) {
				$line = fgets($handle);
				if(strpos($line,'|') !== FALSE and $line[0] != '#'){
					$arry = preg_split("/\||=/", $line, 3);
					if(count($arry) == 3)
						list($type, $name, $value) = $arry;
					$cfg[$name] = trim($value);


				}else{
					continue;
				}
			}
		}
	} 
	return array($sys, $cfg);
}

function load_usr_data_($sid) {
    global $usr, $cfg;  
    if ($cfg['gensessiontype'] == 'mysql') {        
        ##print  load_name('admin_sessions','ses',$sid,'Content');

        $ary = preg_split("/\n/", load_name('admin_sessions', 'ses', $sid, 'Content'));
        //print "size:" . sizeof($ary) . "\n\n";
        for ($x = 0; $x < sizeof($ary); $x++) {
            if (preg_match("/([^=]+)=(.*)/", $ary[$x], $matches)) {
                $usr[strtolower($matches[1])] = $matches[2];
            }
        }
        (!$usr['pref_style']) and ($usr['pref_style'] = 'default');
        (!$usr['pref_lang']) and ($usr['pref_lang'] = 'en');
        if ($usr['id_admin_users'] > 0) {
            return 'ok';
        } else {
            return 'Please Login';
        }
    } else {
        if (file_exists($path_sessions . $sid)) {
            if ($handle = fopen($path_sessions . $sid, 'r')) {
                while (!feof($handle)) {
                    list($name, $value) = explode('=', fgets($handle), 2);
                    $usr[strtolower($name)] = trim($value);
                }
                (!$usr['pref_style']) and ($usr['pref_style'] = 'default');
                (!$usr['pref_lang']) and ($usr['pref_lang'] = 'en');
                return 'ok';
            } else {
                return 'Please Login';
            }
        } else {
            return 'Please Login';
        }
    }
}

function format_price_($num) {
    return ("$ " . number_format($num, 2));
}
function get_ip_() {
    if (getenv('REMOTE_ADDR')) {
        return getenv('REMOTE_ADDR');
    } elseif (getenv('REMOTE_HOST')) {
        return getenv('REMOTE_HOST');
    } elseif (getenv('HTTP_CLIENT_IP')) {
        return getenv('HTTP_CLIENT_IP');
    } else {
        return "Unknown";
    }
}


function load_name_($db,$id_name,$id_value,$field) {
	if($id_value!='NOW()' or $id_value!='CURDATE()')
		$id_value="'$id_value'";
	$sth = mysql_query("SELECT ".$field." FROM ".$db." WHERE ".$id_name."=".$id_value.";") or die("Query failed : " . mysql_error());
	return mysql_result($sth,0);
}


function encrip_ ($this_string){
	$xs = "";
	$xc = "";
	$xn = 0;
	$xn2 = 0;
	
	for ($i = 1; $i <= strlen($this_string); $i++)
	{
		$xc = substr ($this_string, ($i - 1), 1);
		$xn = ord ($xc);

		$xn2 = $xn;

		if (($xn >= 48) && ($xn < 58))
		{
			if (($xn + $i) > 57)
				$xn2 = (48 + ((($xn + $i) - 58) % 10));
			else
				$xn2 = ($xn + $i);
		}

		if (($xn >= 65) && ($xn < 91))
		{
			if (($xn + $i) > 90)
				$xn2 = (65 + ((($xn + $i) - 91) % 26));
			else
				$xn2 = ($xn + $i);
		}

		if (($xn >= 97) && ($xn < 123))
		{
			if (($xn + $i) > 122)
				$xn2 = (97 + ((($xn + $i) - 123) % 26));
			else
				$xn2 = ($xn + $i);
		}
		$xs = $xs . chr($xn2);
	}
	return($xs);
}

function decrip_ ($this_string){
	$xs = "";
	$xc = "";
	$xn = 0;
	$xn2 = 0;
	
	for ($i = 1; $i <= strlen($this_string); $i++)
	{
		$xc = substr ($this_string, ($i - 1), 1);
		$xn = ord ($xc);

		$xn2 = $xn;

		if (($xn >= 48) && ($xn < 58))
		{
			if (($xn - $i) < 48)
				$xn2 = 57 - ((58 - ($xn - ($i - 1))) % 10);
			else
				$xn2 = ($xn - $i);
		}

		if (($xn >= 65) && ($xn < 91))
		{
			if (($xn - $i) < 65)
				$xn2 = 90 - ((91 - ($xn - ($i - 1))) % 26);
			else
				$xn2 = ($xn - $i);
		}

		if (($xn >= 97) && ($xn < 123))
		{
			if (($xn - $i) < 97)
				$xn2 = 122 - ((123 - ($xn - ($i - 1))) % 26);
			else
				$xn2 = ($xn - $i);
		}
		$xs = $xs . chr($xn2);
	}
	return($xs);
}

function load_user_data_(){
	global $in;
	$sid =isset($in['slsid']) ? $in['slsid'] : @$_COOKIE['slsid'];
	if(!$sid)
		return;
	$conn = MysqlBD::getConexion();
	$query = 'select Content from admin_sessions where ses = ? limit 1';
	$sth = $conn->prepare($query);
	$sth->execute(array($sid));
	$res = $sth->fetch();
	$user = $res['Content'];
	$arry = explode("\n",$user);
	$return = array();
	foreach ($arry as $value) {
		if($value!=''){
			list($key,$val) = explode("=",$value);
			$return[$key] = limpiar($val);
		}
	}
	return $return;
}

function check_permissions($cmd, $action, $tab = '') {
# --------------------------------------------------------
	global $usr, $in, $cfg;
	$stype = 'admin';
	$resp = 1;

	if(preg_match("/dbman/i", $_SERVER['SCRIPT_FILENAME'])){
		$stype = 'dbman';
		
	}

	$conn = MysqlBD::getConexion();

	if (!$cfg['cd'] and $cmd){	
		$query = "SELECT COUNT(*)n FROM admin_perms WHERE  application=?  AND command=? AND type=?";
		$sth = $conn->prepare($query);
		$sth->execute(array($usr['application'], $cmd, $stype));
		$res = $sth->fetch();
		$user = $res['n'];

		if(!$user)
			return 0;
	}


	$q = "SELECT 
		IF(COUNT(*)>0,Type,'None') n
	FROM 
		admin_users_perms 
	WHERE 
		ID_admin_users='$usr[id_admin_users]' 
		AND application='$usr[application]' 
		AND (
				command='".$cmd.$action.$tab."' 
				OR command='".$cmd."'
			)";

	$sth = $conn->query($q);
	$utype = $sth->fetch()['n'];
	$q = "SELECT 
		IF(COUNT(*)>0,'Disallow','Allow') n
	FROM 
		admin_groups_perms 
	WHERE (
		ID_admin_groups IN (
			SELECT 
				admin_users_groups.ID_admin_groups 
			FROM 
				admin_users_groups 
			LEFT JOIN admin_groups 
				ON admin_groups.ID_admin_groups=admin_users_groups.ID_admin_groups  
			WHERE 
				admin_users_groups.ID_admin_users='$usr[id_admin_users]' 
				AND Status='Active'
		)
		OR ID_admin_groups = 0
	)
	AND application='$usr[application]' 
	AND (
		command='".$cmd.$action.$tab."' 
		OR command='".$cmd."'
	)";

	$sth = $conn->query($q);
	$gtype = $sth->fetch()['n'];


	if ($utype == 'Disallow' or ($gtype == 'Disallow' and  $utype != 'Allow')){
		return 0;
	}
	
	return 1;
}

function build_select_metodo_pago(){

	$conn = MysqlBD::getConexion();
	$query = "SELECT * FROM cu_metodo_pago WHERE 1;";
	$sth = $conn->prepare($query);
	$sth->execute();

	$output = '';
	while( $res = $sth->fetch() ){
		$output .= '<option value="'.$res['ID_metodo_pago'].'">'.$res['ID_metodo_pago'].' - '.utf8_encode($res['description']).'</option>';
	}

	return $output;

}

function build_select_forma_pago(){

	$conn = MysqlBD::getConexion();
	$query = "SELECT * FROM cu_forma_pago WHERE 1;";
	$sth = $conn->prepare($query);
	$sth->execute();

	$output = '';
	while( $res = $sth->fetch() ){
		$this_id = str_pad($res['ID_forma_pago'], 2, '0', STR_PAD_LEFT);
		$output .= '<option value="'.$this_id.'">'.$this_id.' - '.utf8_encode($res['description']).'</option>';
	}

	return $output;

}

function build_select_uso_cfdi(){

	$conn = MysqlBD::getConexion();
	$query = "SELECT * FROM cu_uso_cfdi WHERE 1;";
	$sth = $conn->prepare($query);
	$sth->execute();

	$output = '';
	while( $res = $sth->fetch() ){
		$output .= '<option value="'.$res['ID_uso_cfdi'].'">'.$res['ID_uso_cfdi'].' - '.utf8_encode($res['description']).'</option>';
	}

	return $output;

}