<?php
/**
 * Description
 *
 * @author L.C.I Cesar Cedillo
 */
global $ck_name; // from trsBase.php
global $cfg;    // from trsBase.php
global $sid;    // from trsBase.php

if (isset($_COOKIE[$ck_name]) || $sid != '') {    
    //$ssid = isset($_COOKIE[$ck_name]) ? $_COOKIE[$ck_name] : $sid;
    $ssid = $sid != '' ? $sid : (isset($_COOKIE[$ck_name]) ? $_COOKIE[$ck_name] : $sid);
    $session_status = load_usr_data($ssid);
    if (preg_match("/\bok\b/i", $session_status)) {
        //--- Encontro los datos de la sesion
    } else {
        header('Location: ' . $cfg['auth_logoff']);
    }
} else {
    header('Location: ' . $cfg['auth_logoff']);
}
?>