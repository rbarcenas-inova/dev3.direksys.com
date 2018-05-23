<?php
// Constantes
if(!isset($_COOKIE['slsid']))
	header('Location: /');
define('DEBUG',1);
define('CLASS_FOLDER','libs');
define('FUNC_FOLDER','functions');
define('LIBS_NAMESPACES','FacturasCFDI,Mysql');
define('AUTOLOAD_FILE',__DIR__ . DIRECTORY_SEPARATOR .CLASS_FOLDER. DIRECTORY_SEPARATOR . 'Autoloader.php');
define('FUNC_FILE',__DIR__ . DIRECTORY_SEPARATOR .FUNC_FOLDER. DIRECTORY_SEPARATOR . 'funciones.php');
define('DATE_FORMAT_LONG', '%A %d %B, %Y');
define('CFG_FOLDER',explode('httpdocs',getcwd())[0].'cgi-bin/common');
define('SH_TRANSDORM',__DIR__.'files'.DIRECTORY_SEPARATOR.'create_pem.sh');
define('ROOT_FOLDER',__DIR__);
// Datos FTP
define("SERVER","172.16.1.23");
define("PORT",21);
define("USER","EDX");
define("PASSWORD","F4cXmL.13#");
define("PASV",true);
define("LAGTIME",100000);
// 
// 
if(DEBUG == 1){
	error_reporting(E_ALL);
	ini_set('display_errors', 1);
}
require_once FUNC_FILE;
require_once AUTOLOAD_FILE;
// Configuración de Direksys
$e = -1;
if (isset($_GET['e'])) {
    $e = $_GET['e'];
    setcookie('e', $e);
} elseif (isset($in['e'])) {
    $e = $in['e'];
    setcookie('e', $e);
} elseif (isset($_COOKIE['e'])) {
    $e = $_COOKIE['e'];
}
define('WS_SING',(isset($cfg['finkok_ws']) && $cfg['finkok_ws'] != '' ) ? $cfg['finkok_ws'] : 'http://demo-facturacion.finkok.com/servicios/soap');
define('CERT_FOLDER',(isset($cfg['cert_folder']) && $cfg['cert_folder']!='') ? $cfg['cert_folder'] : ROOT_FOLDER.DIRECTORY_SEPARATOR.'files'.DIRECTORY_SEPARATOR.'certificados' );
define('EMPRESA',$e == '-1' ? '' : $e);
define('PREFIX_CONFIG','cfdi');
list ($sys,$cfg) = load_sys_data($e);
$in = load_in_data();


