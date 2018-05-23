<?php
class Config{
	////Configuracion Base Datos/////
	public static $connections;
	////Configuracion Usuario Finkok/////

	// public static $user_finkok='finkok@inova.com.mx';
	// public static $pass_finkok='2a8a=WeXus=u';

	public static $user_finkok='fcanaveral@inovaus.com';
	public static $pass_finkok='-P4ssw0rd-';

	public static $finkok_key = 'priv_aef6e3c9a6888670c0a088c780d70bfee2c38554';
}

Config::$user_finkok = $GLOBALS['cfg']['finkok_soap_user'];
Config::$pass_finkok = $GLOBALS['cfg']['finkok_soap_password'];

Config::$connections = array(
	'Main'=>array(
		'server'=>$GLOBALS['cfg']['dbi_host'],
		'user'=>$GLOBALS['cfg']['dbi_user'],
		'pass'=>$GLOBALS['cfg']['dbi_pw'],
		'database'=>$GLOBALS['cfg']['dbi_db']
	),
	'e2'=>array(
		'server'=>$GLOBALS['cfg']['repo_host'],
		'user'=>$GLOBALS['cfg']['repo_user_e2'],
		'pass'=>$GLOBALS['cfg']['repo_pass_e2'],
		'database'=>$GLOBALS['cfg']['repo_db']
	),
	'e10'=>array(
		'server'=>$GLOBALS['cfg']['repo_host'],
		'user'=>$GLOBALS['cfg']['repo_user_e10'],
		'pass'=>$GLOBALS['cfg']['repo_pass_e10'],
		'database'=>$GLOBALS['cfg']['repo_db']
	),
	'e3'=>array(
		'server'=>$GLOBALS['cfg']['repo_host'],
		'user'=>$GLOBALS['cfg']['repo_user_e3'],
		'pass'=>$GLOBALS['cfg']['repo_pass_e3'],
		'database'=>$GLOBALS['cfg']['repo_db']
	),
	'e4'=>array(
		'server'=>$GLOBALS['cfg']['repo_host'],
		'user'=>$GLOBALS['cfg']['repo_user_e4'],
		'pass'=>$GLOBALS['cfg']['repo_pass_e4'],
		'database'=>$GLOBALS['cfg']['repo_db']
	),
	'e12'=>array(
		'server'=>$GLOBALS['cfg']['repo_host'],
		'user'=>$GLOBALS['cfg']['repo_user_e12'],
		'pass'=>$GLOBALS['cfg']['repo_pass_e12'],
		'database'=>$GLOBALS['cfg']['repo_db']
	),
	'e11'=>array(
		'server'=>$GLOBALS['cfg']['repo_host'],
		'user'=>$GLOBALS['cfg']['repo_user_e11'],
		'pass'=>$GLOBALS['cfg']['repo_pass_e11'],
		'database'=>$GLOBALS['cfg']['repo_db']
	),
	'e13'=>array(
		'server'=>$GLOBALS['cfg']['repo_host'],
		'user'=>$GLOBALS['cfg']['repo_user_e11'],
		'pass'=>$GLOBALS['cfg']['repo_pass_e11'],
		'database'=>$GLOBALS['cfg']['repo_db']
	),
	'e15'=>array(
		'server'=>@$GLOBALS['cfg']['repo_host'],
		'user'=>@$GLOBALS['cfg']['repo_user_e15'],
		'pass'=>@$GLOBALS['cfg']['repo_pass_e15'],
		'database'=>@$GLOBALS['cfg']['repo_db']
	),
);


if(isset($GLOBALS['cfg']['finkok_test_mode']) && $GLOBALS['cfg']['finkok_test_mode'] == 1 ){
	Config::$finkok_key = $GLOBALS['cfg']['finkok_test_apikey'];
}else{
	Config::$finkok_key = $GLOBALS['cfg']['finkok_production_apikey'];
}

