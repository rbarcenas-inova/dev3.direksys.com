<?php
class Config{
	////Configuracion Base Datos/////
	public static $user;
	public static $pass;
	public static $bd;
	public static $server;
	////Configuracion Usuario Finkok/////
	public static $user_finkok='fcanaveral@inovaus.com';
	public static $pass_finkok='-1Password1-';
}
Config::$user=$GLOBALS['cfg']['dbi_user'];
Config::$pass=$GLOBALS['cfg']['dbi_pw'];
Config::$bd=$GLOBALS['cfg']['dbi_db'];
Config::$server=$GLOBALS['cfg']['dbi_host'];
Config::$user_finkok= isset($GLOBALS['cfg']['user_finkok']) ? $GLOBALS['cfg']['user_finkok'] : Config::$user_finkok;
Config::$pass_finkok= isset($GLOBALS['cfg']['pass_finkok']) ? $GLOBALS['cfg']['pass_finkok'] : Config::$pass_finkok;