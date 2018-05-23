<?php

global $COMMON_PATH;

require_once $COMMON_PATH . '/common/php/class/db/DbHandler.php';
require_once $COMMON_PATH . '/common/php/class/dto.catalog.InvoicesDTO.php';
require_once $COMMON_PATH . '/common/php/class/dto.catalog.InvoicesLinesDTO.php';

require_once $COMMON_PATH . '/common/php/class/dao.catalog.InvoicesDAO.php';
require_once $COMMON_PATH . '/common/php/class/dao.catalog.InvoicesLinesDAO.php';

$id_invoices = trim($_POST['id_invoice']);  //-- numero del invoice para la consulta de los datos completos
if(empty($_POST['id_invoice'])){$id_invoices = trim($_GET['id_invoice']);}

$invoicesDTO = new InvoicesDTO();
$invoicesDAO = new InvoicesDAO();
$invoicesLinesDTO = new InvoicesLinesDTO();
$invoicesLinesDAO = new InvoicesLinesDAO();

$invoicesDTO->setID_invoices($id_invoices);
$vector_invoices = $invoicesDAO->selectRecords($invoicesDTO);

$invoicesLinesDTO->setID_invoices($id_invoices);
$vector_invoices_lines = $invoicesLinesDAO->selectRecords($invoicesLinesDTO);

$vector_orders_invoice = $invoicesLinesDAO->selcectOrdersFromInvoce($invoicesLinesDTO);


//-- construye la cadena de texto con el numero de ordenes
$list_orders_invoice = "";
foreach ($vector_orders_invoice as $invoicesLines1DTO){
    $list_orders_invoice .= $invoicesLines1DTO->getID_orders() . ", ";
}
$list_orders_invoice = substr($list_orders_invoice, 0, -2);

$vector_creditmemo_invoice = $invoicesLinesDAO->selectCreditmemoFromInvoce($invoicesLinesDTO);
$list_creditmemo_invoice = "";
foreach ($vector_creditmemo_invoice as $invoicesLines1DTO){
    $list_creditmemo_invoice .= $invoicesLines1DTO->getID_creditmemos() . ", ";
}
$list_creditmemo_invoice = substr($list_creditmemo_invoice, 0, -2);

unset($_SESSION['ARRAY_NOTES']);
?>