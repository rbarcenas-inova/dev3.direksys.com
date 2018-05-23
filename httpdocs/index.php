<?php 
	// error_reporting(E_ALL);
	// ini_set("display_errors", 1);

	if (preg_match('/(?i)msie /',$_SERVER['HTTP_USER_AGENT'])){
		// if IE
		header ('Location:firefox.html' );
		exit;
	}
	/* ********************************************************************** */
	/* ** nsBase                                                           ** */
	/* **                                                        03/31/04  ** */
	/* ********************************************************************** */
	
	require_once 'service/vendor/mandrill/mandrill/src/Mandrill.php';
	require("nsAdmBase.php");
	require("functions.php");
	require("commands.php");	


	$sid     = 0;
	$message = '';

	$ip = getenv("REMOTE_ADDR");
	// echo '<pre>';
	// var_dump($cfg);
	// exit();
	## AD::Se agrega validacion para suprimir el error generado por el Servidor de Balanceo
	$headers = getallheaders();
	$ip = (isset($headers['X-Real-IP']) and $headers['X-Real-IP'] !='')? $headers['X-Real-IP'] : $ip ;
	$hostname = (isset($headers['Host-Name']) and $headers['Host-Name'] !='')? $headers['Host-Name'] : $_SERVER['SERVER_NAME'] ;

	if ($cfg['oper_mode'] == 'updating'){
		(!$usr['pref_style']) and ($usr['pref_style'] = 'default');
		(!$usr['pref_lang']) and ($usr['pref_lang'] = 'en');
		(!$usr['pref_screenres']) and ($usr['pref_screenres'] = '100%');
		echo build_page('mode_updating.html');
		return;
	}elseif($cfg['oper_mode'] == 'closed'){
		(!$usr['pref_style']) and ($usr['pref_style'] = 'default');
		(!$usr['pref_lang']) and ($usr['pref_lang'] = 'en');
		(!$usr['pref_screenres']) and ($usr['pref_screenres'] = '100%');	
		echo build_page('mode_stopped.html');
		return;
	}

	/* ***************************************** */
	/* **  I N D E X         ******************* */
	/* ***************************************** */
	if (isset($_COOKIE[$ck_name]) and !$in['login']){
		##########################
		###       TCAM       #####
		##########################
		$sid = $_COOKIE[$ck_name];
		#echo "e=$_COOKIE[e]";
		$message = load_usr_data($sid);
		
		## Cargar Lenguaje
		$lang              = $usr['pref_language'];
		(!$lang) and ($lang = $cfg['default_lang']);

		$path_templates    = $cfg['path_templates'];
		$path_templates    = preg_replace("/\[lang\]/",$lang,$path_templates);


		##
		## Expiracion sesiones
		##

		#### Logofff
		if ($in['logoff']){
			save_logs('logout','');
			logout("$sid");
			$message = "";
		}else{
			### Load Pages
			if ($message == 'Please Login'){
				setcookie($ck_name, '');
				$va['errormessage'] = trans_txt('nologin');
			}else{
				goto_page();
				return;
			}
		}

	}else{
		### Update User Info
		if ($in['pref_language']){
			## Load Lang
			$lang              = $in['pref_language'];
			$path_templates    = $cfg['path_templates'];
			$path_templates    = preg_replace("/\[lang\]/",$lang,$path_templates);
		}



		if ($in['username'] and $in['password']){				

			# Prevenir posible SQLinjection
			$in['username'] = escape_string($in['username']);
			$in['password'] = escape_string($in['password']);

			
			$result = mysqli_query($conn, "SELECT * FROM admin_users WHERE UserName='$in[username]' AND Status='Active'" ) or die("Query failed: ".mysql_error()); // AND (expiration>NOW() or isNULL(expiration) or expiration = '0000-00-00' )");
			$rec = mysqli_fetch_assoc($result);
			$sms_message='';
			$sms_message_no_encode='';

			if ($rec['expiration'] >= date('Y-m-d') or $rec['expiration'] == NULL or $rec['expiration'] == '0000-00-00'){
				if (((strlen($rec['Password'])==13) and $rec['Password'] == crypt($in['password'],substr(crypt($in['password'],'ns'),3,7)))or((strlen($rec['Password'])==40) and $rec['Password'] == sha1($in['password']))){
					#if ($rec['IPFilter'] and !checkip($rec['IPFilter'])){
					#	$va['errormessage'] = trans_txt("log_unauthlogin");
					#	save_logs("log_unauthlogin", $in['username']);
					#}else{
						$usr['tem'] = 'db='.$cfg['emp.'.$in['e'].'.dbi_db'];
						foreach ($rec as $key=>$value){
							$usr[strtolower($key)] = $value;
						}
						$usr['application'] = $rec['application'];
						srand(time());
						$sid = $usr['id_admin_users'].'-'.(intval(rand(1,100000))) .  time() . (intval(rand(1,1000000000)));
						$sid .= sid_dv($sid);
	
						# Set Cookies
						setcookie($ck_name, $sid);
						setcookie('voxhelp', 'On');
						setcookie('e', $in['e']);
						
						### Update User Info
						if ($in['pref_language']){
							$usr['pref_language'] = $in['pref_language'];
							setcookie('nslang', $in['pref_language']);
							$result = mysqli_query($conn, "UPDATE admin_users SET LastLogin=NOW(),LastIP='$ip',pref_language='$in[pref_language]' WHERE ID_admin_users='$usr[id_admin_users]'");
						}else{
							$result = mysqli_query($conn, "UPDATE admin_users SET LastLogin=NOW(),LastIP='$ip' WHERE ID_admin_users='$usr[id_admin_users]'");
						}
						(!$usr['maxhits']) and ($usr['maxhits'] = 20);
						(!$usr['pref_style']) and ($usr['pref_style'] = $cfg['default_style']);
						(!$usr['pref_language'])  and ($usr['pref_lang']  = $cfg['default_lang']);
						($in['table_width'])  and ($usr['table_width']  = $in['table_width']);
						(!$usr['table_width'])  and ($usr['table_width']  = 860);
						
						save_logs('login','');

						$blocked_ip = validate_ip_blocked();

						if ( ! $blocked_ip) {
							if (trim($rec['IPFilter']) == "") {

								# Validacion por codigo de seguridad enviado por SMS
								# Si tiene configurado un num de cel autorizado para que se le envien SMS

								if ( ! valip('sl_ipmanager')) {
									/*inicio de la creacion del mensaje */
									$verification_code ='';
									$id_verification_code = $rec['ID_admin_users']."-".$rec['homeSMS'];
									$result = mysqli_query($conn, "SELECT COUNT(*)vars FROM sl_vars WHERE vname='SMS Verification' AND VValue='$id_verification_code' AND Expiration>NOW();");
									$rec_vars = mysqli_fetch_assoc($result);
									$va['homesms'] = "********".substr($rec['homeSMS'], 6, 4);
									if ($rec_vars['vars'] > 0 and ! isset($in['codigo'])) {
										setcookie($ck_name, '');
										echo build_page('verify.html');
										return;
									}
									if ($rec['homeSMS'] != '' and $usr['homecountry'] != '' and $rec_vars['vars'] == 0) {
										setcookie($ck_name, '');
										mysqli_query($conn, "DELETE FROM sl_vars WHERE vname='SMS Verification' AND VValue='$id_verification_code' AND Expiration<NOW();");
										$pair1 = str_pad(rand(0, 99),2,'0',STR_PAD_LEFT);
										$pair2 = str_pad(rand(0, 99),2,'0',STR_PAD_LEFT);
										$pair3 = str_pad(rand(0, 99),2,'0',STR_PAD_LEFT);
										$verification_code = $pair1.$pair2.$pair3;
										$minutes = ($cfg['sms_verification_expiration_minutes'])? (int)$cfg['sms_verification_expiration_minutes']:15;
										$result = mysqli_query($conn, "INSERT IGNORE sl_vars (VName, VValue, Subcode, Expiration) VALUES ('SMS Verification', '$id_verification_code', '$verification_code', DATE_ADD(NOW(), INTERVAL $minutes MINUTE));");
										
										// setcookie($ck_name, $sid);
										// $cfg['sms_verification']
										// $cfg['sms_verification_prefix']
										$sms_message = urlencode('Tu codigo de verificacion de Direksys '.$cfg['app_title'].' es DKS-'.$verification_code);
										$sms_phone = '';
										
										if (isset($cfg['sms_area_code'.$usr['homecountry']]) and $cfg['sms_area_code'.$usr['homecountry']]) {
											$sms_phone = $cfg['sms_area_code'.$usr['homecountry']].$rec['homeSMS'];
										} elseif (isset($cfg['sms_area_code']) and $cfg['sms_area_code']) {
											$sms_phone = $cfg['sms_area_code'].$rec['homeSMS'];
										}
										#$in['codigo'] = $verification_code;
										$result = sendsms($sms_phone,$sms_message);
										echo build_page('verify.html');
										return;

									} elseif ( ! $rec['homeSMS'] or ! $usr['homecountry']) {
										setcookie($ck_name, '');
										$va['errormessage'] = str_replace("#IP#", get_ip(), trans_txt('ip_not_trusted'));
										echo build_page('login.html');
										return;
									}
									if (isset($in['codigo'])) {
										$codigo = $in['codigo'];
										$qry = "Select * From sl_vars Where Subcode = '$codigo';";

										$res = mysqli_query($conn, $qry) or die("Query failed: ".mysql_error($conn));
										$rec = mysqli_fetch_array($res);

										if ($in['codigo'] != $rec["Subcode"]) {
											setcookie($ck_name, '');
											$in['username'];
											$in['password'];
											echo build_page('verify.html');
											return;
										} else {
											$qry = "Delete From sl_vars Where Subcode = '$codigo';";
											$res = mysqli_query($qry) or die("Query failed: ".mysql_error($conn));
											load_others_ses($sid,$in['username'],crypt($in['password'],substr(crypt($in['password'],'ns'),3,7)),sha1($in['password']));
											(!$usr['pref_style']) and ($usr['pref_style'] = 'default');
											(!$usr['pref_lang']) and ($usr['pref_lang'] = 'en');
											goto_page();
											return;
										}
									}
								} else {
									load_others_ses($sid,$in['username'],crypt($in['password'],substr(crypt($in['password'],'ns'),3,7)),sha1($in['password']));
									(!$usr['pref_style']) and ($usr['pref_style'] = 'default');
									(!$usr['pref_lang']) and ($usr['pref_lang'] = 'en');
									goto_page();
									return;
								}
							} else {
								if ( ! valip('admin_users', $rec['ID_admin_users'])) {
									setcookie($ck_name, '');
									$va['errormessage'] = trans_txt('ip_not_allowed');
									echo build_page('login.html');
									return;
								} else {
									load_others_ses($sid,$in['username'],crypt($in['password'],substr(crypt($in['password'],'ns'),3,7)),sha1($in['password']));
									(!$usr['pref_style']) and ($usr['pref_style'] = 'default');
									(!$usr['pref_lang']) and ($usr['pref_lang'] = 'en');
									goto_page();
									return;
								}
							}
						} else {
							setcookie($ck_name, '');
							$va['errormessage'] = trans_txt('ip_not_allowed');
							echo build_page('login.html');
							return;
						}
					#}
				}else{					
					//Evaluate attempts to access to send sms notification					
					$sms_message_no_encode='Usuario '.$in['username'].", ha excedido el No. De intentos para ingresar a e".$in['e'].' desde '.$hostname.' '.date('Y-m-d H:i:s').'.  IP bloqueada:'.$ip;
					$sms_message = urlencode('ALERTA: '.$sms_message_no_encode);

					$max_failed_attempts = (isset($cfg['max_failed_attempts']) && (int)$cfg['max_failed_attempts'] > 0 )? (int)$cfg['max_failed_attempts'] : 3 ;
					$va['max_failed_attempts'] = $max_failed_attempts;

					if(!isset($_COOKIE['attempts'])){										
						setcookie('attempts',1);
					}else{
						if($_COOKIE['attempts']==$max_failed_attempts){
							if($rec['IPFilter']=="" || $rec['IPFilter']==null || $rec['IPFilter']!=$ip){		
								$servername = parse_url($hostname);
								// notificate_admins_sms($sms_message);
								get_db_to_inactivate_user($in['username'],$ip);

								$va['ip_info'] = $ip;
								$va['user_info'] = $in['username'];
								$va['datetime'] = date(DATE_RFC2822);
								$va['hostname'] = $hostname;
								$va['company_info'] = $cfg['app_e'.$in['e']];
								$va['ip_info'] = $ip;
								$va['ip_location'] = geolocation_ip();
								$email_msg = build_page('common/emails/login_failed.html');
								
								//Send mail to desarrollo@inovaus.com
								$params=array(
									'msg'=>$email_msg,
									'subject'=>trans_txt("login_failed_subject").' '.$hostname,
									'from_name'=>'Direksys',
									'to'=>$cfg['team_direksys_email'],
									'to_name'=>"Desarrollo",
									'mandrillapp_user'=>$cfg['mandrillapp_user'],
									'mandrillapp_key'=>$cfg['mandrillapp_key']
								);
								send_mandrill_mail($params);
							}
							setcookie('attempts',1);							
						}else{
							setcookie('attempts',($_COOKIE['attempts']+1));					
						}
					}

					//Data for email notification
					$result_mail = mysqli_query($conn, "SELECT Email,FirstName,MiddleName,LastName FROM admin_users WHERE UserName='$in[username]'") or die("Query failed: ".mysqli_error($conn)); // AND (expiration>NOW() or isNULL(expiration) or expiration = '0000-00-00' )");
					$rec_mail = mysqli_fetch_assoc($result_mail);

					$va['ip_info'] = $ip;
					$va['user_info'] = $in['username'];
					$va['user_name'] = $rec_mail['FirstName'];
					$va['datetime'] = date(DATE_RFC2822);
					$va['hostname'] = $hostname;
					$va['company_info'] = $cfg['app_e'.$in['e']];
					$va['ip_info'] = $ip;
					$va['ip_location'] = geolocation_ip();
					$email_msg = build_page('common/emails/login_failed_notification.html');
					
					//Send mail to desarrollo@inovaus.com
					$params=array(
						'msg'=>$email_msg,
						'subject'=>trans_txt("login_failed_subject").' '.$hostname,
						'from_name'=>'Direksys',
						'to'=>$rec_mail['Email'],
						'to_name'=>$rec_mail['FirstName']." ".$rec_mail['LastName'],
						'mandrillapp_user'=>$cfg['mandrillapp_user'],
						'mandrillapp_key'=>$cfg['mandrillapp_key']
					);
					
					if(isset($rec_mail['Email']) && $rec_mail['Email']!='' && $rec_mail['Email']!=null){
						send_mandrill_mail($params);
					}

					$va['errormessage'] = trans_txt("password_error");
					save_logs("log_invalidlogin", $in['username']);
					(!$usr['pref_style']) and ($usr['pref_style'] = 'default');
					(!$usr['pref_lang']) and ($usr['pref_lang'] = 'en');
					goto_page();
					return;
				}
			}else{
				$va['errormessage'] = trans_txt("password_expiration");
				save_logs("log_invalidlogin", $in['username']);
				(!$usr['pref_style']) and ($usr['pref_style'] = 'default');
				(!$usr['pref_lang']) and ($usr['pref_lang'] = 'en');
				goto_page();
				return;
			}
		}
	}
	(!$usr['pref_style']) and ($usr['pref_style'] = 'default');
	(!$usr['pref_lang']) and ($usr['pref_lang'] = 'en');
	goto_page();
	return;
	#echo "vars<br>";
	#echo "pref_style : $usr[pref_style]<br>";
	#echo "pref_lang : $usr[pref_lang]<br>";
	#echo "imgurl  : $va[imgurl] <br>";
	
	
	
	function goto_page(){
		global $usr,$in,$sid,$cfg,$va,$ip,$usr,$hostname;
		if (!$sid or !$usr['application']){
			#not logged in
			$va['softversion'] = $cfg['ver_admin'];
			echo build_page('login.html');
			return;
		}
		
		## SMS Login Notification
		$sms_message = urlencode('Haz iniciado sesion en '.$hostname.' "'.$cfg['app_e'.$in['e']].'" desde la IP '.$ip.' '.date(DATE_RFC2822));
		$sms_phone = '';
		
		if (isset($cfg['sms_area_code'.$usr['homecountry']]) and $cfg['sms_area_code'.$usr['homecountry']]) {
			$sms_phone = $cfg['sms_area_code'.$usr['homecountry']].$usr['homesms'];
		} elseif (isset($cfg['sms_area_code']) and $cfg['sms_area_code']) {
			$sms_phone = $cfg['sms_area_code'].$usr['homesms'];
		}

		$user_is_admin = 0;
		$user_is_admin = isadmin($usr['id_admin_users']);

		if ($in['login'] and strlen($sms_phone) > 10 and $user_is_admin){
			sendsms($sms_phone,$sms_message);
		}

		if (isset($usr['email']) and filter_var($usr['email'], FILTER_VALIDATE_EMAIL) and $user_is_admin){
			$va['user_info'] = $usr['username'];
			$va['datetime'] = date(DATE_RFC2822);
			$va['hostname'] = $hostname;
			$va['company_info'] = $cfg['app_e'.$in['e']];
			$va['ip_info'] = $ip;
			$va['ip_location'] = geolocation_ip();
			$email_msg = build_page('common/emails/login_notification.html');
			
			$params=array(
				'msg'=>$email_msg,
				'subject'=>'Nuevo inicio de sesión en tu cuenta de Direksys',
				'from_name'=>'Direksys',
				'to'=>$usr['email'],
				'to_name'=>$usr['firstname'].' '.$usr['lastname'],
				'mandrillapp_user'=>$cfg['mandrillapp_user'],
				'mandrillapp_key'=>$cfg['mandrillapp_key']
			);	
			send_mandrill_mail($params);
		}

		header("Location: /cgi-bin/mod/".$usr['application']."/admin?cmd=home");
		return;
	}

?>
