<?php
define('BASE', __DIR__);
define('BIN_FOLDER', BASE.'/bin/');
define('LOG_FILE', 'log');
define('INIT', 1);
define('DEBUG', 1);
define('DEFAULT_E', 2);
define('CFG_FOLDER',explode('httpdocs',getcwd())[0].'cgi-bin/common');
define('CONFIG_FILE', BASE. '/config.ini');
define('PREFIX_CONFIG', '');
if(DEBUG == 1){
	error_reporting(E_ALL);
	ini_set('display_errors', 1);
	set_time_limit(0);
}

require BASE . '/vendor/autoload.php';

// GLOBALS VARS
$cli = array();
$in = load_in();
$e = load_e_value(DEFAULT_E);
$cfg = load_sys_data_helper($e);


