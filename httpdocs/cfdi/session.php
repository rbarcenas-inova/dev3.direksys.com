<?php
global $ck_name; // from trsBase.php
global $cfg;    // from trsBase.php
global $sid;    // from trsBase.php

if (isset($_COOKIE[$ck_name]) || $sid != '') {    

    $permisions_effect = $cfg['perm_tree_effect'] ? $cfg['perm_tree_effect'] : 'Allow';
    $permisions_uneffect = strtolower($permisions_effect) === 'allow' ? 'Disallow' : 'Allow';
    $resp = strtolower($permisions_effect) === 'allow' ? 0 : 1;

    //$ssid = isset($_COOKIE[$ck_name]) ? $_COOKIE[$ck_name] : $sid;
    $ssid = $sid != '' ? $sid : (isset($_COOKIE[$ck_name]) ? $_COOKIE[$ck_name] : $sid);
    $session_status = load_usr_data($ssid);
    $res1 = mysql_fetch_assoc(mysql_query("SELECT IF(COUNT(*) > 0,Type,'None') Entra FROM admin_users_perms WHERE ID_admin_users='".$usr['id_admin_users']."' AND application='admin' AND command='mod_cfdi';"));
    $res2 = mysql_fetch_assoc(mysql_query("SELECT IF(COUNT(*) > 0,'". $permisions_effect ."','". $permisions_uneffect ."') Entra FROM admin_groups_perms WHERE (ID_admin_groups IN (SELECT admin_users_groups.ID_admin_groups FROM admin_users_groups LEFT JOIN admin_groups ON admin_groups.ID_admin_groups=admin_users_groups.ID_admin_groups  WHERE admin_users_groups.ID_admin_users='".$usr['id_admin_users']."' AND Status='Active') OR ID_admin_groups = 0) AND application='admin' AND command='mod_cfdi';"));
    if($res1['Entra'] == "Allow" OR $res2['Entra'] == 'Allow')
    	echo "";
    else
   		header('Location: ' . $cfg['auth_logoff']);
    if (preg_match("/\bok\b/i", $session_status)) {
        //--- Encontro los datos de la sesion
    } else {
        header('Location: ' . $cfg['auth_logoff']);
    }

} else {

    header('Location: ' . $cfg['auth_logoff']);

}

?>