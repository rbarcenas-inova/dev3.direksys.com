<?php

function select_language(){
	global $cfg;
	$list = preg_split("/,/", $cfg['langs']);
	$output = "<select name='pref_language' onFocus='focusOn( this )' onBlur='focusOff( this )'><option value=''>---</option>";
	for ($i = 0; $i < sizeof($list)/2; $i++) {
		$output .= "<option value='".$list[$i*2+1]."'>".$list[$i*2]."</option>\n";
	}
	$output .= "</select>";
	return $output;
}

function table_width(){
	global $cfg;
	$list = preg_split("/,/", $cfg['screenres']);
	$output = "<select name='table_width' onFocus='focusOn( this )' onBlur='focusOff( this )'><option value=''>---</option>";
	for ($i = 0; $i < sizeof($list);$i++) {
		$output .= "<option value='".$list[$i]."'>".$list[$i]."</option>\n";
	}
	$output .= "</select>";
	return $output;
}

function select_style(){
	global $cfg;
	$list = preg_split("/,/", $cfg['styles']);
	$output = "<select name='pref_style' onFocus='focusOn( this )' onBlur='focusOff( this )'><option value=''>---</option>";
	$output .= "<option value='default'>Default</option>\n";
	for ($i = 0; $i < sizeof($list); $i++) {
		$output .= "<option value='".$list[$i]."'>".$list[$i]."</option>\n";
	}
	$output .= "</select>";
	return $output;
}


##############################################################
##############################################################
#Function: load_db_names
#	Extract specific field values from a table

#Created by:
#_Carlos Haas_
#
#Modified By:
#
#
#Parameters:
#- db: Table name
#- id_name: Field to look for
#- id_value: Value of the field
#- str_out: Names of the field to be returned
#
#Returns:
#A string with one or more field values concateated
#
#See Also:
#- load_name
#
function multicompany(){
##############################################################
##############################################################

	global $cfg,$def_e,$max_e;

	for ($i = 1; $i <= $cfg['max_e']; $i++) {
		
		unset($selected);
		$selected='';
		($i == 1) and ($selected='selected="selected"');
		
		if(!empty($cfg['app_e'.$i])) {
			$output .= "<option value='$i' $selected>".$cfg['app_e'.$i]."</option>\n";
		}
	}
	if ($output) {
		$output = "
		<select name='e' class='logdrop'>
			<option value=''>---</option>
			<!--<option value='0'>". $cfg['app_e'.$i] ."</option>-->
			$output
		</select>";
		
	}
	
	return $output;
}	

function load_others_ses($ses,$username,$passwd,$passwdsha1) {
#---------------------------------------------------------
#---------------------------------------------------------
# Last Modified by RB on 11/08/2010: Shoplatino access blocked		
//Last modified on 16 Dec 2010 12:23:54
//Last modified by: MCC C. Gabriel Varela S. :Se incorpora Sha1
# Last Modified by RB on 05/04/2011 08:55:11 PM : Se activa la session de SOSL para que pueda entrar Bernardo
//Last modified on 11 May 2011 16:29:50
//Last modified by: MCC C. Gabriel Varela S. : Se hace ip global
	global $cfg,$path_sessions,$usr,$ip;
	global $conn;

	## Others Sessions
	for ($e = 1; $e <= $cfg['max_e']; $e++) {
		if ($cfg['emp.'.$e.'.dbi_db']){
			//mysql_pconnect ($cfg['emp.'.$e.'.dbi_host'], $cfg['emp.'.$e.'.dbi_user'], $cfg['emp.'.$e.'.dbi_pw']) or die(mysql_error());
			//mysql_select_db ($cfg['emp.'.$e.'.dbi_db']) or die(mysql_error());
			$conn = mysqli_connect ($cfg['emp.'.$e.'.dbi_host'], $cfg['emp.'.$e.'.dbi_user'], $cfg['emp.'.$e.'.dbi_pw'], $cfg['emp.'.$e.'.dbi_db']);
            if( !is_null($conn) ){

				$result = mysqli_query($conn, "SELECT * FROM admin_users WHERE UserName='$username' AND Status='Active'  AND ((length(Password)=13 and Password='$passwd')or(length(Password)=40 and Password='$passwdsha1'))"); // AND (expiration>NOW() or isNULL(expiration) or expiration = '0000-00-00' )");
				$rec = mysqli_fetch_assoc($result);

				if ($rec['ID_admin_users'] and ($rec['expiration'] >= date('Y-m-d') or $rec['expiration'] == NULL or $rec['expiration'] == '0000-00-00')){
					#if ($rec['IPFilter'] and checkip($rec['IPFilter'])){
						$sdata = '';
						foreach ($rec as $key=>$value){
							$sdata[strtolower($key)] = $value;
						}

						$usr['id_admin_users'] = $rec['ID_admin_users'];
						### Update User Info
						if ($in['pref_language']){
							$sdata['pref_language'] = $in['pref_language'];
							$result = mysqli_query($conn, "UPDATE admin_users SET LastLogin=NOW(),LastIP='$ip',pref_language='".$in['pref_language']."' WHERE ID_admin_users='".$rec['ID_admin_users']."'");
						}else{
							$result = mysqli_query($conn, "UPDATE admin_users SET LastLogin=NOW(),LastIP='$ip' WHERE ID_admin_users='".$rec['ID_admin_users']."'");
						}
						(!$sdata['maxhits']) and ($sdata['maxhits'] = 20);
						(!$sdata['pref_style']) and ($sdata['pref_style'] = $cfg['default_style']);
						(!$sdata['pref_language'])  and ($sdata['pref_lang']  = $cfg['default_lang']);

						$path_sessions     = $cfg['emp.'.$e.'.auth_dir'];
						setcookie('app_e'.$e, 'active');
						### Save Session & Log
						save_auth_data($ses,$sdata);
						save_logs('login','');
					#}
				}
			}
        }
	}
	//	exit;
}

function load_name($db,$id_name,$id_value,$field) {
// --------------------------------------------------------
	global $conn;
if($id_value!='NOW()' or $id_value!='CURDATE()')
	$id_value="'$id_value'";
$sth = mysqli_query($conn, "SELECT ".$field." FROM ".$db." WHERE ".$id_name."=".$id_value.";") or die("Query failed : " . mysqli_error($conn));
return mysqli_field_seek($sth,0);
}


#############################################################################
#############################################################################
#   Function: encrip
#
#       Es: encrip. Codifica una cadena
#       En: 
#
#
#    Created on: 
#
#    Author: _Roberto Barcenas_
#
#    Modifications:
#
#        - Modified on ** by _Roberto Barcenas_ : 
#
#   Parameters:
#
#      - this_string: cadena para codificar 
#
#  Returns:
#
#      - xs: cadena codificada
#
#
#   See Also:
#
#      <decrip>
#
function encrip ($this_string){
#############################################################################
#############################################################################


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

#############################################################################
#############################################################################
#   Function: decrip
#
#       Es: Invrsa a decrip. Decodifica una cadena codificada con la funcion encrip previamente
#       En: 
#
#
#    Created on: 
#
#    Author: _Roberto Barcenas_
#
#    Modifications:
#
#        - Modified on ** by _Roberto Barcenas_ : 
#
#   Parameters:
#
#      - this_string: cadena codificada 
#
#  Returns:
#
#      - xs: cadena decodificada
#
#
#   See Also:
#
#      <encrip>
#
function decrip ($this_string){
#############################################################################
#############################################################################


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

################################################################
############              ENCRYPTION             ###############
################################################################
function LeoEncrypt($text, $passphrase='') {
# --------------------------------------------------------
    if ( substr($text, 0, 2) == 'ok' )
    	return $text;

    $holder = chr(127);
    $text = str_replace("\r", "", $text);    
    $text = str_replace("\t", "", $text);
    $text = str_replace("\n", "", $text);
    $text = LeoPermute($text, $passphrase, 1);
    $text = str_replace(".", "a", $text);
    $text = str_replace(":", "b", $text);
    $text = str_replace("~", "c", $text);
    $text = str_replace("-", "d", $text);
    $text = str_replace("_", "e", $text);
    $text = str_replace("/", "f", $text);
    $text = str_replace("\\", "g", $text);
    return 'ok' . $text;
}

function LeoDecrypt($text, $passphrase='') {
# --------------------------------------------------------

    if( substr($text, 0, 2) != 'ok' )
        return $text;
    $text = preg_replace('/^ok/', "", $text); 

    $holder = chr(127);
    $text = str_replace("a", ".", $text);
    $text = str_replace("b", ":", $text);
    $text = str_replace("c", "~", $text);
    $text = str_replace("d", "-", $text);
    $text = str_replace("e", "_", $text);
    $text = str_replace("f", "/", $text);
    $text = str_replace("g", "\\", $text);   
    $text = str_replace("\r", "", $text);
    $text = str_replace("\n", "", $text);
    $text = LeoPermute($text, $passphrase, -1);
    $text = str_replace($holder, "\n", $text);
    $text = str_replace("x", "Z", $text);
    
    return $text;
}

function LeoPermute($text, $strphrase='', $multFactor) {
# --------------------------------------------------------
    #### Calculate Phrase
    while (strlen($strphrase) < 10) {
        $strphrase .= "x";
    }
    
    $a = -1;
    $phrase = 0;
    for ($ind = 0; $ind<=strlen($strphrase)-1; $ind++) {
        $phrase += pow($a, $ind) * ord(substr($strphrase, $ind, 1));
    }
    $phrase = abs($phrase);
    
    ### Built Chards Array
    $chars = array();
    $c = 'Z1A2Q3W4S5X6C7D8ERF9V0BGTYHNMJUIKLOP.:~-_/\\';
    $clen = strlen($c);
    for ($i=0; $i<=$clen-1; $i++) {
        $chars[] = substr($c, $i, 1);
    }
    array_unshift($chars, 'x');
    $plain = array();
    for ($i=0; $i<=count($chars); $i++) {
        $plain[$chars[$i]] = $i;
    }    
    $holder = chr(127);
   
    ### Permute
    $new_text = '';
    for ($i=0; $i<=strlen($text)-1; $i++){
        $character = substr($text,$i,1);
        if ($character != $holder) {
            $pos = $plain[$character];
            $pos2 = abs((int)(sin($i+ $phrase)*$clen));
            $shift = $pos + $multFactor * $pos2;
            if ($shift >= $clen) {
                $shift -= $clen;
            } else if ($shift < 0) {
                $shift += $clen;
            }
           
            $character = $chars[$shift];
            $new_text .= $character;
        }
    }
    return $new_text;
}

function sendsms($cellphone,$message){	
    global $cfg;

    $url = $cfg['sms_url']."?";
	$cellphone = str_replace('+', '%2B', $cellphone);
    $url .= (isset($cfg['twilio_apiversion']) and $cfg['twilio_apiversion']!='')?"twilio_apiversion=".$cfg['twilio_apiversion']:"";
    $url .= (isset($cfg['twilio_accountsid']) and $cfg['twilio_accountsid']!='')?"&twilio_accountsid=".$cfg['twilio_accountsid']:"";
    $url .= (isset($cfg['twilio_authtoken']) and $cfg['twilio_authtoken']!='')?"&twilio_authtoken=".$cfg['twilio_authtoken']:"";
    $url .= (isset($cfg['twilio_from']) and $cfg['twilio_from']!='')?"&twilio_from=".$cfg['twilio_from']:"";
    $url .= (isset($cellphone) and $cellphone!='')?"&Recipient=".$cellphone:"";
    $url .= (isset($message) and $message!='')?"&Message=".urlencode($message):"";
    
    // echo $url;

    if (isset($cfg['sms_url']) and $cfg['sms_url']!=''){
        $fields = array(
            'message' => urlencode($message)
        );		
        foreach($fields as $key=>$value) { 
            $fields_string .= $key.'='.$value.'&';
        }
        rtrim($fields_string, '&');

        $ch = curl_init();

        #curl_setopt($ch,CURLOPT_SSL_VERIFYPEER, false);
        #curl_setopt($ch,CURLOPT_PORT,443);
        curl_setopt($ch,CURLOPT_URL, $url);
        curl_setopt($ch,CURLOPT_POST, count($fields));
        curl_setopt($ch,CURLOPT_POSTFIELDS, $fields_string);

        $result = curl_exec($ch);

        curl_close($ch);
    } else {
        echo  'Configuration not found.';
    }
}

/*********************************************
	# Alejandro Diaz
	# 2016-05-18
	# Prevenir posible SQLinjection
	# Seguridad
*********************************************/
function escape_string($var_string=''){
	global $conn;
	if ($var_string != ''){
		return mysqli_escape_string($conn, $var_string);
	}else{
		return $var_string;
	}
}

function get_db_to_inactivate_user($username,$ip){
		$single_pattern =  '/general.e\d.cfg/';
		$double_pattern =  '/general.e\d\d.cfg/';
		$valid_conf_pattern='/conf/';
		$invalid_conf_pattern='/#conf/';
		$act_company_pattern='/app_e/';


		$dir='../cgi-bin/common/';
		$conf_file="general.ex.cfg";

		//Checar el numero maximo de compañias 
		$file=$dir.$conf_file;		
		$file_handle = fopen($file, "r");
		$conf=[];

		while (!feof($file_handle)) {
			$line = fgets($file_handle);
			if(preg_match_all($valid_conf_pattern, $line) && !preg_match_all($invalid_conf_pattern, $line)){
				list($param_type,$param_val_compose)=explode('|',$line);
				list($param_name,$param_val)=explode('=',$param_val_compose);


				if(preg_match_all($act_company_pattern, $param_name)){								
					// echo "$param_type|$param_name=$param_val<br>";
					$companie_number = preg_replace("/[^0-9,.]/", "", $param_name);
					// echo "$companie_number<br>";

					//Se abre el archivo correspondiente a la compañia valida
					$file="general.e".$companie_number.".cfg";				
					$file=$dir.$file;		
					// echo "$file<br>";
					$current_file_handle = fopen($file, "r");				
					$dbi_db=$dbi_host=$dbi_pw=$dbi_user='';
					while (!feof($current_file_handle)) {
					   	$current_line = fgets($current_file_handle);
					   	list($current_param_type,$current_param_val_compose)=explode('|',$current_line);
						list($current_param_name,$current_param_val)=explode('=',$current_param_val_compose);

						switch($current_param_name){
							case "dbi_db":							
								$dbi_db=trim($current_param_val);
								break;
							case "dbi_host":
								$dbi_host=trim($current_param_val);
								break;
							case "dbi_pw":
								$dbi_pw=trim($current_param_val);
								break;
							case "dbi_user":
								$dbi_user=trim($current_param_val);
								break;
						}					
					}
					
					inactivate_users_in_active_companies($dbi_db,$dbi_host,$dbi_pw,$dbi_user,$username,$ip);

					fclose($current_file_handle);

				}
			}		
		}
		fclose($file_handle);
	}

	function inactivate_users_in_active_companies($dbi_db,$dbi_host,$dbi_pw,$dbi_user,$username,$ip){		
		global $in,$ip,$conn;
		$conex = new mysqli($dbi_host, $dbi_user, $dbi_pw, $dbi_db);
		$conn=$conex;

		if ($conex->connect_errno) {
			echo("ERROR: (" . $conex->connect_errno . ") " . $conex->connect_error)."<br>";
		}


		// //Checar si el usuario existe, en caso de que si exista, se desactiva y bloqueamos la IP
		$q_user='SELECT * FROM admin_users WHERE Username="'.$username.'"';
		$q_user_result = $conex->query($q_user);
		$q_user_ary = $q_user_result->fetch_assoc();

		$row_cnt = $q_user_result->num_rows;
		if($row_cnt>0){						
		 	/* Crear una tabla que no devuelve un conjunto de resultados */
		 	$q_disable_user='UPDATE admin_users SET Status="Inactive" WHERE Username="'.$username.'"';
			$conex->query($q_disable_user);		 	
			// echo $q_disable_user."<br>";
					 	
			//Verificamos que la IP no haya sido insertada anteriormente
			$q_check_blocked_ip='	SELECT * 
									FROM sl_ipmanager 
									WHERE 
									sl_ipmanager.IP="'.$ip.'" 
									AND sl_ipmanager.Description="Suspect IP"';
			$res_ip_blocked = $conex->query($q_check_blocked_ip);
			$row_ip_blocked = $res_ip_blocked->fetch_assoc();
			$row_cnt_ip_blocked = $res_ip_blocked->num_rows;


			if($row_cnt_ip_blocked==0){				
		 		//Insertar bloquear IP
		 		$q_block_ip='INSERT INTO sl_ipmanager SET IP="'.$ip.'",Type="Blocked",Description="Suspect IP",Block_DateTime=NOW(),Status="Inactive",Date=CURDATE(),Time=CURTIME(),ID_admin_users=1';
		 		$conex->query($q_block_ip);	
		 		$ID_ip_managet=mysqli_insert_id($conex);

		 		//Add record to admin_users_blocked
				$q_admin_users_blocked='INSERT INTO admin_users_locked SET 
										  ID_admin_users='.$q_user_ary['ID_admin_users'].
										',ID_ipmanager='.$ID_ip_managet.
										',Time=CURTIME(),Date=CURDATE()';
				$conex->query($q_admin_users_blocked);

				//Insert log   				
				$in['db']='admin_users';
   				$in['cmd']='usr_admin_banned';
				auth_logging("admin_users_locked",$q_user_ary['ID_admin_users']);

		 	}else{
		 		//VErificamos que no se haya insertado antes ya esa misma IP en la relacion de usuario bloqueados		 		
		 		$q_check_admin_users_locked='SELECT * FROM admin_users_locked WHERE ID_admin_users='.$q_user_ary['ID_admin_users'].' AND ID_ipmanager='.$row_ip_blocked['ID_ipmanager'];
				$e_check_admin_users_locked = $conex->query($q_check_admin_users_locked);
				$r_check_admin_users_locked = $e_check_admin_users_locked->fetch_assoc();
				$r_count_check_admin_users_locked = $e_check_admin_users_locked->num_rows;				
		 		
		 		//En caso de no existis, se agrega a la relacion
		 		if($r_count_check_admin_users_locked==0){		 			
					$q_admin_users_blocked='INSERT INTO admin_users_locked SET 
											  ID_admin_users='.$q_user_ary['ID_admin_users'].
											',ID_ipmanager='.$row_ip_blocked['ID_ipmanager'].
											',Time=CURTIME(),Date=CURDATE()';
					$conex->query($q_admin_users_blocked);

					//Insert log   					
					$in['db']='admin_users';
	   				$in['cmd']='usr_admin_banned';
					auth_logging("admin_users_locked",$q_user_ary['ID_admin_users']);
				}
		 	}
		}

		unset($conex);
	}


	function send_mandrill_mail($params){
		try {
		    $mandrill = new Mandrill($params['mandrillapp_key']);
		    $message = array(
		        'html' => $params['msg'],
		        'text' => utf8_encode($params['msg']),
		        'subject' => $params['subject'],
		        'from_email' => $params['mandrillapp_user'],
		        'from_name' => $params['from_name'],
		        'to' => array(
		            array(
		                'email'=> $params['to'],
		                'name' => utf8_encode($params['to_name']),
		                'type' => 'to'
		            )
		        ),
		        'headers' => array('Reply-To' => $params['mandrillapp_user'])		        
		    );
		    $async = false;
		    $ip_pool = 'Main Pool';
		    $send_at = date('Y-m-d H:i:s');
		    $result = $mandrill->messages->send($message, $async, $ip_pool, $send_at);		    
		    // print_r($result);
		} catch(Mandrill_Error $e) {
		    echo 'A mandrill error occurred: ' . get_class($e) . ' - ' . $e->getMessage();
		    throw $e;
		}		
	}

	function notificate_admins_sms($sms_message){		
		global $cfg;		

		$q_to='';
		$q_to.='SELECT homeSMS FROM admin_users ';
		$q_to.='WHERE admin_users.`Status`="Active" ';
		$q_to.='AND admin_users.ID_admin_users<=3000 ';
		$q_to.='AND admin_users.homeSMS IS NOT NULL ';
		$q_to.='AND admin_users.homeSMS <> "" ';		
		
		$e_to=mysql_query($q_to) or die("Query failed: ".mysql_error());

		while($r_to = mysql_fetch_assoc($e_to)){													
		  	$sms_phone = $cfg['sms_area_code'].$r_to['homeSMS'];		  
		  	$result = sendsms($sms_phone,$sms_message);		  	
		}					
	}

	/*********************************************
		# Alejandro Diaz
		# 2018-03-20
		# Geolocator IP
	*********************************************/
	function geolocation_ip(){
		global $ip;
		$location = '';
		
		// $query = @unserialize(file_get_contents('http://ip-api.com/php/'.$ip));
		// if($query && $query['status'] == 'success') {
		// 	$location = $query['city'].', '.$query['country'];
		// }
		
		return $location;

	}