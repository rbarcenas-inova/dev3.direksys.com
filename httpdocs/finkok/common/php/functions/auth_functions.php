<?php

/* * **************************************
 * Incluir previamente las clases requeridas para conexion de bd y logging
 * 
 */

function auth_logging($message, $action, $id_admin_users, $tbl_name = '', $cmd = '') {
    $ip_address = $_SERVER["REMOTE_ADDR"];

    $adminLogsDTO = new AdminLogsDTO();
    $adminLogsDAO = new AdminLogsDAO();

    if ($message == 'login' || $message == 'logout') {
        $type = 'Access';
    } else {
        $type = 'Application';
    }

    $adminLogsDTO->setTblName($tbl_name);
    $adminLogsDTO->setLogCmd($cmd);
    $adminLogsDTO->setType($type);
    $adminLogsDTO->setAction($action);
    $adminLogsDTO->setMessage($message);
    $adminLogsDTO->setIP($ip_address);
    $adminLogsDTO->setID_admin_users($id_admin_users);
    
    $adminLogsDAO->insertRecord($adminLogsDTO);    
}

?>