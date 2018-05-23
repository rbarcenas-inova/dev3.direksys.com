<?php
// Constantes
define('DEBUG',0);
define('CONSOLE_ONLY',0);
define('CLASS_FOLDER','libs');
define('FUNC_FOLDER','functions');
define('CMD', 'mod_vendor_cfdi');
define('LIBS_NAMESPACES','FacturasCFDI,Mysql');
define('AUTOLOAD_FILE',__DIR__ . DIRECTORY_SEPARATOR .CLASS_FOLDER. DIRECTORY_SEPARATOR . 'Autoloader.php');
define('FUNC_FILE',__DIR__ . DIRECTORY_SEPARATOR .FUNC_FOLDER. DIRECTORY_SEPARATOR . 'AutoloaderFunc.php');
define('DATE_FORMAT_LONG', '%A %d %B, %Y');
define('CFG_FOLDER',explode('httpdocs',getcwd())[0].'cgi-bin/common');
define('SH_TRANSDORM',__DIR__.'files'.DIRECTORY_SEPARATOR.'create_pem.sh');
define('ROOT_FOLDER',__DIR__);
define('CREATE_EMISOR',1);
if(DEBUG == 1){
	ini_set('display_errors', 1);
	ini_set('display_startup_errors', 1);
	error_reporting(E_ERROR);
}
if(CONSOLE_ONLY == 1 and PHP_SAPI != 'cli'){
	die('Solo funciona en modo Consola.');
}elseif(PHP_SAPI != 'cli' && !isset($_GET['re'])){
	if(!isset($_COOKIE['slsid']))
		header('Location: /');
}
require_once FUNC_FILE;
require_once AUTOLOAD_FILE;
// Configuración de Direksys
$e = -1;
$cli = array();
if(PHP_SAPI == 'cli'){
	$cli = parseConsoleArg($argv);
	if(isset($cli['e'])){
		$e = $cli['e'];
	}
}elseif (isset($_GET['e'])) {
    $e = $_GET['e'];
    setcookie('e', $e);
    setcookie('e', $e, 0, "/vendors_cfdi/Facturas/");
    setcookie('e', $e, 0, "/vendors_cfdi/");
    setcookie('e', $e, 0, "/");
} elseif (isset($in['e'])) {
    $e = $in['e'];
    setcookie('e', $e);
    setcookie('e', $e, 0, "/vendors_cfdi/Facturas/");
    setcookie('e', $e, 0, "/vendors_cfdi/");
    setcookie('e', $e, 0, "/");
} elseif (isset($_COOKIE['e'])) {
    $e = $_COOKIE['e'];
}

$loader = new FacturasCFDI\Autoloader();
$loader->register();

define('CERT_FOLDER',(isset($cfg['cert_folder']) && $cfg['cert_folder']!='') ? $cfg['cert_folder'] : ROOT_FOLDER.DIRECTORY_SEPARATOR.'files'.DIRECTORY_SEPARATOR.'certificados' );
define('EMPRESA',$e == '-1' ? '' : $e);
define('PREFIX_CONFIG','cfdi');
list ($sys,$cfg) = load_sys_data_($e);
$usr = load_user_data_();
$in = load_in_data_();
$in = array_merge($in,$cli);
if($GLOBALS['cfg']['finkok_method_rest']==1){
	define('WS_SING',(isset($cfg['finkok_rest_host']) && $cfg['finkok_rest_host'] != '' ) ? $cfg['finkok_rest_host'] : 'https://finkok.io/api/v2/');
}else{
	define('WS_SING',(isset($cfg['finkok_soap_host']) && $cfg['finkok_soap_host'] != '' ) ? $cfg['finkok_soap_host'] : 'http://demo-facturacion.finkok.com/servicios/soap/');
}
// echo '<pre>';
// print_r($in);
// print_r($usr);
if(check_permissions(CMD, 'admin') == 0){
	header('Location: /?e='.EMPRESA);
}



// print_r($GLOBALS['cfg']);

// exit;
// 
// echo $User;

// $User = $cfg['dbi_user'];
// $Password = $cfg['dbi_pw'];
// $Server = $cfg['dbi_host'];
// $DataBase = $cfg['dbi_db'];


// load_usr_data();


