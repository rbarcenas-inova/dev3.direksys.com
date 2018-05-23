<?php

/**
 * Description
 *
 * @author L.C.I Cesar Cedillo
 */

include_once '../../../../trsBase.php';

require_once '../../class/db/DbHandler.php';
require_once '../../class/dto.catalog.PurchaseOrdersDTO.php';
require_once '../../class/dao.catalog.PurchaseOrdersDAO.php';
require_once '../../functions/pagination.php';

//--- parametros de configuracion del paginador
$data_url = $_POST['data_url'];
$paginator_container = $_POST['paginator_container'];
$data_container = $_POST['data_contanier'];
$results_per_page = $_POST['results_per_page'];

$poID = trim(isset($_POST['poid']) ? $_POST['poid'] : $_GET['poid']);

$poDTO = new PurchaseOrdersDTO();
$poDAO = new PurchaseOrdersDAO();

$poDTO->setID_purchaseorders(is_numeric($poID) ? $poID : 0);

$poDAO->onlyCountRows(TRUE);
$poDAO->selectRecords($poDTO);
$totalResults = $poDAO->getNumRows();


$array_url_params = array(
    "poid" => $poID,    
    "results_per_page" => $results_per_page
);

createPaginator($totalResults, $results_per_page, $data_url, $array_url_params, $paginator_container, $data_container);
?>