<?php
/**
 * Description
 *
 * @author L.C.I Cesar Cedillo
 */

include_once '../../../../trsBase.php';

require_once '../../class/db/DbHandler.php';
require_once '../../class/dto.catalog.PartsDTO.php';
require_once '../../class/dao.catalog.PartsDAO.php';
require_once '../../functions/pagination.php';

//--- parametros de configuracion del paginador
$data_url = $_POST['data_url'];
$paginator_container = $_POST['paginator_container'];
$data_container = $_POST['data_contanier'];
$results_per_page = $_POST['results_per_page'];

$ID_part = trim(isset($_POST['pid']) ? $_POST['pid'] : $in['pid']);
$part_model = trim(isset($_POST['pmodel']) ? $_POST['pmodel'] : $in['pmodel']);
$part_name = trim(isset($_POST['pname']) ? $_POST['pname'] : $in['pname']);
$target_usge = isset($in['target_usage']) ? $in['target_usage'] : isset($_POST['target_usage']) ? $_POST['target_usage'] : "";
$id_popup = isset($in['idpopup']) ? $in['idpopup'] : isset($_POST['idpopup']) ? $_POST['idpopup'] : "";

//--- Crea los objetos
$partsDAO = new PartsDAO();
$partsDTO = new PartsDTO();

    $partsDTO->setID_parts(is_numeric($ID_part) ? $ID_part : 0);
    $partsDTO->setModel($part_model);
    $partsDTO->setName($part_name);

$partsDAO->onlyCountRows(TRUE);
$partsDAO->selectRecords($partsDTO);

$totalResults = $partsDAO->getNumRows();


$array_url_params = array(
    "pid" => $ID_part,
    "pmodel" => $part_model,
    "pname" => $part_name,
    "target_usage" => $target_usge,
    "results_per_page" => $results_per_page,
    "popup" => $id_popup
    
);

createPaginator($totalResults, $results_per_page, $data_url, $array_url_params, $paginator_container, $data_container);

?>