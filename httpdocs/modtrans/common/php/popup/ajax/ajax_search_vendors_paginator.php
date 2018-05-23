<?php
/**
 * Description
 *
 * @author L.C.I Cesar Cedillo
 */

include_once '../../../../trsBase.php';

require_once '../../class/db/DbHandler.php';
require_once '../../class/dto.catalog.VendorsDTO.php';
require_once '../../class/dao.catalog.VendorsDAO.php';
require_once '../../functions/pagination.php';

//--- parametros de configuracion del paginador
$data_url = $_POST['data_url'];
$paginator_container = $_POST['paginator_container'];
$data_container = $_POST['data_contanier'];
$results_per_page = $_POST['results_per_page'];

$vendorID = trim(isset($_POST['vid']) ? $_POST['vid'] : $_GET['cid']);
$vendorName = trim(isset($_POST['vname']) ? $_POST['vname'] : $_GET['vname']);

$vendorDTO = new VendorsDTO();
$vendorDAO = new VendorsDAO();

$vendorDTO->setID_vendors(is_numeric($vendorID) ? $vendorID : 0);
$vendorDTO->setCompanyName($vendorName);


$vendorDAO->onlyCountRows(TRUE);
$vendorDAO->selectRecords($vendorDTO);
$totalResults = $vendorDAO->getNumRows();


$array_url_params = array(
    "vid" => $vendorID,
    "vname" => $vendorName,
    "results_per_page" => $results_per_page
);

createPaginator($totalResults, $results_per_page, $data_url, $array_url_params, $paginator_container, $data_container);
?>