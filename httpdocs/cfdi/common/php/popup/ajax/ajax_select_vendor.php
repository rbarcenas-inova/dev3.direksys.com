<?php
//include_once '../../../nsAdmBase.php';

include_once '../../../../trsBase.php';

require_once '../../class/db/DbHandler.php';
require_once '../../class/dto.catalog.VendorsDTO.php';
require_once '../../class/dao.catalog.VendorsDAO.php';

$vendorID = trim($_POST['vid']);

//--- Crea los objetos
$vendorDAO = new VendorsDAO();
$vendorDTO = new VendorsDTO();

$vendorDTO->setID_vendors($vendorID);


//--- Ejecuta la consulta
$arr_result = $vendorDAO->selectRecords($vendorDTO);

//--- Almacena los resultados en un array tipo JSON
$array_json = array(
    'vendorID' => $arr_result[0]->getID_vendors(),
    'vendorName' => $arr_result[0]->getCompanyName(),
    'vendorPhone' => $arr_result[0]->getPhone(),
    'vendorAddress' => $arr_result[0]->getAddress(),
    'vendorCity' => $arr_result[0]->getCity(),
    'vendorState' => $arr_result[0]->getState(),
    'vendorCountry' => $arr_result[0]->getCountry(),
    'vendorZip' => $arr_result[0]->getZip()
);

echo json_encode($array_json);
?>