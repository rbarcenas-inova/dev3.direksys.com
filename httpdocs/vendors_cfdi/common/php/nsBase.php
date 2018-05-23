<?php
	require("functions.php");
	//require("functions_port.php");

	#########################################################
	#### INIT System Data
	#########################################################
	$in  = array();
	$va  = array();
	$trs = array();
	$usr = array();
	$sys = array();
	$cfg = array();
	$tpl = array();
	$cses= array();
	$error= array();
	$device=array();

	## Deteccion de Devices
	#require_once('wurfl/getClientDevice.php');
	#$device['is_mobile_device'] = !empty($_GET['mobiledev']) ? true : false;
	#$device['is_mobile_device'] = !empty($_GET['mobiledev']) ? true : $device['is_mobile_device'];
	#$device['is_mobile_device'] = false;
	#if(!empty($device['is_mobile_device']) ) { print_r($device); }
	define('DATE_FORMAT_LONG', '%A %d %B, %Y');

	######################################################
	##### Configuration File
	######################################################
    $cfg_folder = getcwd();

	load_sys_data(); //Load $sys
	#RB
	$ck_name  =  $cfg['ckname'];
	$sid="";
	######################################################
	##### Load Paths and URLs ############################
	######################################################
	// Connect Persistent to DB
        //die(print_r($cfg));
        die( $in['e'] . '.dbi_user');
	mysql_pconnect ($cfg['dbi_host'], $cfg['dbi_user'], $cfg['dbi_pw']) or die("Error en conexión ".mysql_error()."$cfg[dbi_host], $cfg[dbi_user], $cfg[dbi_pw]");
	mysql_select_db ($cfg['dbi_db']) or die("Error en selección ".$cfg['dbi_db']." ".mysql_error());
	#general_tracker();
	set_data_profiler($cfg['prof_url'], $_SERVER['HTTP_REFERER']);
	// System Data
	$in  = array();
	$tpl = array();
	$tpl['pagetitle'] = $cfg['app_title'];

	// Load Data
	foreach ($_GET as $key=>$value ) {
		if($value != '[QSA]'){
			if (array_key_exists(strtolower($key), $in)){
				$in[strtolower($key)] .= "|$value";
			}else{
				$in[strtolower($key)] = $value;
			}
		}
	}
	foreach ($_POST as $key=>$value ) {
		if (array_key_exists(strtolower($key), $in)){
			$in[strtolower($key)] .= "|$value";
		}else{
			$in[strtolower($key)] = $value;
		}
		//print "$key : $value<br>";
	}
	$in{'fullquery'} = getenv(QUERY_STRING);
	
	// Create Session
	create_session();
	
	## Language Selection
	if ($in['lang']){
		$_SESSION['lang'] = $in['lang'];
	}elseif (isset($_COOKIE['lang'])){
		$usr['pref_language'] = $_COOKIE['lang'];
	}else{
		$usr['pref_language'] = $cfg['default_lang'];
	}
	$cfg['path_templates'] = preg_replace("/\[lang\]/", $usr['pref_language'] , $cfg['path_templates']);
	
	#RB
	if (isset($_COOKIE[$ck_name])){
		$sid = $_COOKIE[$ck_name];
	}

	##################
	##################
	## Paypal globals
	##################
	##################
	$API_UserName = "";
	$API_Password = "";
	$API_Signature = "";
	$API_Endpoint = "";
	$PAYPAL_URL = "";
	$PROXY_HOST = '127.0.0.1';
	$PROXY_PORT = '808';
	$sBNCode = "PP-ECWizard";	// BN Code 	is only applicable for partners
	$USE_PROXY = false;
	$version = $cfg['paypal_version'];



	###########################################
	###### Shopping Cart 
	###########################################	
	
	if($_COOKIE['ps']=='Off' and !($in['cmd']=='cart' and $in['checkout']==1 and $in['step']==4) and !($in['cmd']=='page' and $in['fname']=='404'))
	{
		setcookie('ps','On',0,'/');
// 		setcookie('ins',print_r($in,true));
// 		echo "Entra";
// 		echo "Ines:";
// 	print_r($in);
// 		print_r($in);
		save_callsession(1);
	}
	if(is_readable("$cfg[auth_dir]/cart_".session_id())){
		load_callsession();
		if($cses['paytype']=='google-checkout'and $cses['final']==1)
		{
			setcookie('ps','On',0,'/');
// 			setcookie('ins',print_r($in,true));
			save_callsession(1);
		}
		if(!isset($cses['random_memorial']))
		{
			$cses['random_memorial']=rand(1,5)*5;
			save_callsession(0);
		}
	}else{
		//Si es la primera vez que entra, o si se va a realizar una nueva compra.
		$cses['items_in_basket'] = 0;
		$cses['payments']=1;
		$cses['shp_type']=1;
		
		$cses['random_memorial']=rand(1,5)*5;
		
		save_callsession(0);
	}
	load_usr_data($sid);
	
	$va['step']=1;
#	if($cses['step1'] == "done" /*and isset($usr['id_customers']) and $usr['id_customers'] > 0*/){
#		$va['step']=2;
#	}
	
	## Templates por defecto
	$tpl["nsFilename"] = "default.html";
	$tpl['filename']   = 'content/home.html';

	if($device['is_mobile_device']){
		$cfg['path_templates'] .= 'mobile/';
		$tpl['skel'] = 'skeleton.html';
	}


	###2x1
	if(!empty($cfg['two_for_one_use'])){

		if( !empty($cfg['products2x1_fromdate']) and !empty($cfg['products2x1_todate']) ){
			$mod = " BETWEEN '".$cfg['products2x1_fromdate']."' AND '".$cfg['products2x1_todate']."' ";
		}elseif( !empty($cfg['products2x1_fromdate']) ){
			$mod = " >= '".$cfg['products2x1_fromdate']."' ";
		}elseif ( $cfg['products2x1_todate'] ) {
			$mod = " <= '".$cfg['products2x1_todate']."' ";
		}else{
			$cfg['is2x1_valid'] = 1;
		}

		if(!empty($mod) ){
			$q1 = "SELECT IF(NOW() $mod ,1,0);";
			$sth = mysql_query($q1);
			list($cfg['is2x1_valid']) = mysql_fetch_row($sth);
		}

	}

	if (array_key_exists("cmd", $in)){
		if ($in['cmd'] == 'productinfo'){
			($in['fb']) and ($cses['fb'] = $in['fb']) and (save_callsession());
			(isset($cses['fb'])) and ($in['fb'] = $cses['fb']);
			require("cmd_productinfo.php");
		}elseif ($in['cmd'] == 'show_description'){
			require("cmd_show_description.php");
		}elseif ($in['cmd'] == 'search'){
			require("cmd_search.php");
		}elseif ($in['cmd'] == 'admincart'){
			require("cmd_admincart.php");
		}elseif ($in['cmd'] == 'cart'){
			require("cmd_cart.php");
		}elseif ($in['cmd'] == 'page'){
			require("cmd_page.php");
			
			#print "SELECT * FROM nsc_templates WHERE Name='".filter_values($in[fname])."' AND Type='page-content' AND Status='Active'";
			$sth = mysql_query("SELECT * FROM nsc_templates WHERE cmdName='".filter_values(strtolower($in['fname']))."' AND Type='page-content' AND Status='Active'");
			if($sth and mysql_num_rows($sth) > 0){
			        $rec = mysql_fetch_assoc($sth);
			        if ($rec['ID_templates']){
				        foreach ($rec as $key => $value ) {
					        $tpl[strtolower($key)] = $value;
				        }
			        }
			}else{
			        #$tpl['skel'] = 'default.html';
			        $tpl['filename'] = '/content/'.$in['fname'].'.html';
			}
			$cmdname = "runcmd_".$in['fname'];
			if (function_exists($cmdname)){
				$rep_str = $cmdname();
			}
		}elseif ($in['cmd'] == 'prodpagetab'){
			$tpl['skel']="cart_product_tab.html";
			if (file_exists("$cfg[path_templates]cart/products/".$in['id_products']."_tab".$in['tab'].".html") and is_file("$cfg[path_templates]cart/products/".$in['id_products']."_tab".$in['tab'].".html")){
		    	$in['srcfile']="/cgi-bin/nsc_admin/templates/sp/cart/products/".$in['id_products'].".html";
				$tpl['filename'] = "cart/products/".$in['id_products']."_tab".$in['tab'].".html";
		    	#$tpl[filename]="/cart/content/detail_product.html";
				#require("$cfg[path_templates]cart/products/".$rec[ID_products].".html");
			}else{
		    	$in['srcfile']="/cgi-bin/nsc_admin/templates/sp/cart/products/".$in['id_products'].".html";
				$tpl['filename']="cart/products/blank.html";
			}
		}elseif ($in['cmd'] == 'contenttab'){
			$tpl['skel']="cart_product_tab.html";
			if (file_exists("$cfg[path_templates]content/".$in['content']."_tab".$in['tab'].".html") and is_file("$cfg[path_templates]content/".$in['content']."_tab".$in['tab'].".html")){
				$in['srcfile']="/cgi-bin/nsc_admin/templates/sp/content/".$in['content'].".html";
				$tpl['filename'] = "content/".$in['content']."_tab".$in['tab'].".html";
			}else{
				$in['srcfile']="/cgi-bin/nsc_admin/templates/sp/content/".$in['content'].".html";
				$tpl['filename']="$cfg[path_templates]content/".$in['content']."_tab".$in['tab'].".html";
			}
		}elseif($in['cmd'] == 'login'){
			$tpl['skel'] = 'cart_product.html';
			$tpl['filename'] = '/content/'.$in{'cmd'}.'.html';
			$va['message']  =  trans_txt('user_not_found');
			########## Validacion de Usuario
			if ($in['email'] and $in['password']){

				if(start_login($in['email'],$in['password'])=='ok'){
					########## Usuario Valido
					$in{'cmd'}  = 'home';
					require("admincart.php");
				}else{
					save_logs("log_invalidlogin", $in['username']);
				}
			}
			
		}elseif(preg_match('/^home|orders|ccard|chgpass|techsupp|shpaddress$/',$in['cmd'])){
			require("admincart.php");
		}elseif($in{'cmd'} == 'logoff'){
			logout();
		}elseif($in['cmd'] == 'descuentolibre'){
			$tpl['filename']="content/".$in['cmd'].".html";
		}elseif(preg_match('/^ax_(.*)/',$in['cmd'], $matches)){
		    # Descuento libre
			require("cmd_descuentolibre.php");
		}elseif (stristr($in['cmd'],"ppresponse") !== "FALSE"){
			$ary_step = explode("_",$in['cmd']);
			$in['cmd'] = 'cart';
			$in['checkout'] = 1;
			$in['step'] = intval($ary_step['1']);
			($in['step'] == 4) and ($in['step']=3) and ($in['skip_shipinfo_paypal']=1);
			require("cmd_cart.php");
		}elseif (/*$in['cmd'] == 'ppcallback' /*and */isset($_REQUEST['token'])){
			$txt_req = implode("\r\n",$_REQUEST);
			mail("roberto.barcenas@gmail.com","Se recibio el Callback","$txt_req");
			$token = $_REQUEST['token'];
			require("cmd_paypal_callback.php");
		}
	}else{

		if(empty($device['is_mobile_device'])){

				$tpl["nsMaxHits"]  = 20;
				$tpl["top_image"]  = 'top.jpg';
				$tpl["nsFilename"] = "default.html";
				$tpl['filename']   = 'content/home.html';
				$tpl['page_title'] = $cfg['app_title'];
				
				$va['facebook_opengraph'] = get_facebook_opgraph();

		}else{
			$tpl['filename']   = 'content/home.html';
			$tpl['page_title'] = $cfg['app_title'];	
		}
		
	}


	#### Paginas de Contenido
	if(!empty($in['pcontent']) and empty($device['is_mobile_device']) and empty($in['product']) ){
		$tpl['skel'] = 'for_content.html';
	}



	###########################################
	###### This Page url
	###########################################	
	$this_url = "id=$in[id]";
	for ($i=0; $i<count($db_cols);++$i){
		if (array_key_exists($db_cols[$i], $in) ){
			$this_url .= "&$db_cols[$i]=".$in[$db_cols[$i]];
		}
	}
	if (array_key_exists('nsparent', $in) ){
		$this_url .= "&nsParent=".$in[nsparent];
	}
	if (array_key_exists('catsearch', $in) ){
		$this_url .= "&catsearch=".$in[catsearch];
	}
	if (array_key_exists('keyword', $in) ){
		$this_url .= "&keyword=".$in[keyword];
	}
	
	
?>
