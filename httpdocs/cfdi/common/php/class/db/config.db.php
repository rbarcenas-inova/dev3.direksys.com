<?php

/**
 * Description of config
 *
 * @author ccedillo
 */
global $User;
global $Password;
global $Server;
global $DataBase;
global $cfg;

$User = $cfg['dbi_user'];
$Password = $cfg['dbi_pw'];
$Server = $cfg['dbi_host'];
$DataBase = $cfg['dbi_db'];


/*
  $User = "root";
  $Password = "inova";
  $Server = "localhost";
  $DataBase = "direksys2_e2";
 
 */
 
/*
$User = $cfg['emp.' . $in['e'] . '.dbi_user'];
$Password = $cfg['emp.' . $in['e'] . '.dbi_pw'];
$Server = $cfg['emp.' . $in['e'] . '.dbi_host'];

 *
 */
?>