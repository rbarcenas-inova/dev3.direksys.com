<?php
//include_once '../../../nsAdmBase.php';

include_once '../../../../trsBase.php';

require_once '../../class/db/DbHandler.php';
require_once '../../class/dto.catalog.CustomersDTO.php';
require_once '../../class/dao.catalog.CustomersDAO.php';

$customerID = trim($_POST['cid']);

//--- Crea los objetos
$customerDTO = new CustomersDTO();
$customerDAO = new CustomersDAO();

$customerDTO->setID_customers($customerID);

//--- Ejecuta la consulta
$arr_result = $customerDAO->searchByCustomerName($customerDTO);

//--- Almacena los resultados en un array tipo JSON
$array_json = array(
    'customerID' => $arr_result[0]->getID_customers(),
    'customerName' => $arr_result[0]->getFirstName() . " " . $arr_result[0]->getLastName() . " " . $arr_result[0]->getLastName2(),
    'customerPhone' => $arr_result[0]->getPhone1(),
    'customerAddress1' => $arr_result[0]->getAddress1(),
    'customerAddress2' => $arr_result[0]->getAddress2(),
    'customerAddress3' => $arr_result[0]->getAddress3(),
    'customerUrbanization' => $arr_result[0]->getUrbanization(),
    'customerCity' => $arr_result[0]->getCity(),
    'customerState' => $arr_result[0]->getState(),
    'customerCountry' => $arr_result[0]->getCountry(),
    'customerZip' => $arr_result[0]->getZip()
);

echo json_encode($array_json); json
?>