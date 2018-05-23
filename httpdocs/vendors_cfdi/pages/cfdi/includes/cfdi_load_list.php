<?php
global $COMMON_PATH;

require_once $COMMON_PATH  . '/common/php/class/db/DbHandler.php';
require_once $COMMON_PATH  . '/common/php/class/dto.catalog.InvoicesDTO.php';
require_once $COMMON_PATH  . '/common/php/class/dao.catalog.InvoicesDAO.php';

//---- parametros de paginacion 
/*
$results_per_page = isset($_POST['results_per_page']) ? $_POST['results_per_page'] : (isset($_GET['results_per_page']) ? $_GET['results_per_page'] : $cfg['results_page']);
$page = isset($_POST['page']) ? $_POST['page'] : (isset($_GET['page'])?$_GET['page'] : 1);
$start = ($page - 1) * $results_per_page;

$invoicesDTO = new InvoicesDTO();
$invoicesDAO = new InvoicesDAO();

$invoicesDAO->onlyCountRows(TRUE);
$invoicesDAO->selectRecords($invoicesDTO);
$total_results = $invoicesDAO->getNumRows();

$invoicesDAO->setOrderBy("ID_invoices_desc");
$invoicesDAO->setPagerStart($start);
$invoicesDAO->setPagerPerPage($results_per_page);

$vector_cfdi = $invoicesDAO->selectRecords($invoicesDTO);

$pages = ceil($total_results / $results_per_page);

$_SESSION['TOTAL_PAGINAS_CFDI'] = $pages;
unset($_SESSION['TOTAL_RESULTADOS_CFDI']);
*/
?>