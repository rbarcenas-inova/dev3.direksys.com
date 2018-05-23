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


$RELATIVE_COMMON_PATH = "../..";

//---- parametros de paginacion 
$results_per_page = isset($_POST['results_per_page']) ? $_POST['results_per_page'] : $_GET['results_per_page'];
$page = isset($_POST['page']) ? $_POST['page'] : $_GET['page'];
$start = ($page - 1) * $results_per_page;


//---- Recibe los parametros desde la llamada ajax
$poID = trim(isset($_POST['poid']) ? $_POST['poid'] : $_GET['poid']);

//--- Crea los objetos
$poDAO = new PurchaseOrdersDAO();
$poDTO = new PurchaseOrdersDTO();

if (is_numeric($poID)) {
    $poDTO->setID_purchaseorders($poID);

//--- Ejecuta la consulta
    $poDAO->setPagerStart($start);
    $poDAO->setPagerPerPage($results_per_page);

    $arr_result = $poDAO->selectRecords($poDTO);
} else {
    $arr_result = array();
}
?>

<?php
if (!empty($arr_result)) {
?>
    <table width="100%" align="center"  class="List">
        <tr class="tableListColumn">
            <td>OC#</td>
            <td>Proveedor ID</td>
            <td>OC Fecha</td>
            <td>OC Terms</td>
            <td>OC Status</td>
            <td></td>
        </tr>
    <?php
    $style = 0;
    $flagCSS = FALSE;

    foreach ($arr_result as $poDTO) {
        if ($flagCSS) {
            $style = 1;
            $flagCSS = FALSE;
        } else {
            $style = 0;
            $flagCSS = TRUE;
        }
    ?>
        <tr class="tableFila<?php echo $style; ?>">
            <td><?php echo $poDTO->getID_purchaseorders() ?></td>
            <td><?php echo utf8_encode($poDTO->getID_vendors()); ?></td>
            <td><?php echo $poDTO->getPoDate(); ?></td>
            <td><?php echo utf8_encode($poDTO->getPoTerms()); ?></td>
            <td><?php echo utf8_encode($poDTO->getStatus()); ?></td>
            <td><img src="<?php echo $RELATIVE_COMMON_PATH ?>/common/img/sel_ok.png" height="12px" width="12px" style="cursor: pointer" onclick="ajaxSelectPO(<?php echo $poDTO->getID_purchaseorders(); ?>)" /></td>
        </tr>
    <?php
    }
    ?>
</table>    
<?php
} else {
?>
    <table width="100%" align="center"  class="List">
        <tr>
            <td align="center">
                No se encontraron resultados.
            </td>
        </tr>
    </table>
<?php
}
?>