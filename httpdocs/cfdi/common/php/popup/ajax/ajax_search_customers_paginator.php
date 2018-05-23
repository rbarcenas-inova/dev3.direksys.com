<?php

//include_once '../../../nsAdmBase.php';
include_once '../../../../trsBase.php';

require_once '../../class/db/DbHandler.php';
require_once '../../class/dto.catalog.CustomersDTO.php';
require_once '../../class/dao.catalog.CustomersDAO.php';
require_once '../../functions/pagination.php';

//--- parametros de configuracion del paginador
$data_url = $_POST['data_url'];
$paginator_container = $_POST['paginator_container'];
$data_container = $_POST['data_contanier'];
$results_per_page = $_POST['results_per_page'];


$customerID = trim($_POST['cid']);
$customerName = trim($_POST['cname']);
$customerLName1 = trim($_POST['clname1']);
$customerLName2 = trim($_POST['clname2']);


$customerDTO = new CustomersDTO();
$customerDAO = new CustomersDAO();

$customerDTO->setID_customers(is_numeric($customerID) ? $customerID : 0);
$customerDTO->setFirstName($customerName);
$customerDTO->setLastName($customerLName1);
$customerDTO->setLastName2($customerLName2);

$customerDAO->onlyCountRows(TRUE);
$customerDAO->searchByCustomerName($customerDTO);
$totalResults = $customerDAO->getNumRows();


$array_url_params = array(
    "cid" => $customerID,
    "cname" => $customerName,
    "clname1" => $customerLName1,
    "clname2" => $customerLName2,
    "results_per_page" => $results_per_page
    
);

createPaginator($totalResults, $results_per_page, $data_url, $array_url_params, $paginator_container, $data_container);

?>