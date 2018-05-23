<?php
/**
 * Description
 *
 * @author L.C.I Cesar Cedillo
 */
session_start();
include_once '../../../trsBase.php';
require_once '../../../common/php/class/db/DbHandler.php';

require_once '../../../common/php/class/dto.catalog.PurchaseOrdersItemsDTO.php';
require_once '../../../common/php/class/dao.catalog.PurchaseOrdersItemsDAO.php';

$action = $_POST['action'];
$exito = 0;

$id_admin_users = isset($usr['id_admin_users']) ? $usr['id_admin_users'] : 0;

if($action=='update_qty'){
    $ID_purchaseorders_items = trim($_POST['id_items']);
    $rec = $_POST['qtty'];
    
    $poItemsDTO = new PurchaseOrdersItemsDTO();
    $poItemsDAO = new PurchaseOrdersItemsDAO();
    
    $poItemsDTO->setID_purchaseorders_items($ID_purchaseorders_items);
    $poItemsDTO->setRecieved($rec);
    $poItemsDTO->setID_admin_users($id_admin_users);
    
    if($poItemsDAO->updateRecord($poItemsDTO)){
        $exito = 1;
    }
}

echo $exito;
?>