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


$RELATIVE_COMMON_PATH = "../..";

//---- parametros de paginacion 
$results_per_page = isset($_POST['results_per_page']) ? $_POST['results_per_page'] : $_GET['results_per_page'];
$page = isset($_POST['page']) ? $_POST['page'] : $_GET['page'];
$start = ($page - 1) * $results_per_page;


//---- Recibe los parametros desde la llamada ajax

$vendorID = trim(isset($_POST['vid']) ? $_POST['vid'] : $_GET['vid']);
$vendorName = trim(isset($_POST['vname']) ? $_POST['vname'] : $_GET['vname']);

//--- Crea los objetos
$vendorDTO = new VendorsDTO();
$vendorDAO = new VendorsDAO();

if (is_numeric($vendorID) || strlen($vendorName) > 0) {
    $vendorDTO->setID_vendors(is_numeric($vendorID) ? $vendorID : 0);
    $vendorDTO->setCompanyName($vendorName);

//--- Ejecuta la consulta
    $vendorDAO->setPagerStart($start);
    $vendorDAO->setPagerPerPage($results_per_page);

    $arr_result = $vendorDAO->selectRecords($vendorDTO);
} else {
    $arr_result = array();
}
?>

<?php
if (!empty($arr_result)) {
?>
    <table width="100%" align="center"  class="List">
        <tr class="tableListColumn">
            <td>ID</td>
            <td>Nombre</td>
            <td>Direccion</td>
            <td>Estado / Pais</td>
            <td>Telefono</td>
            <td></td>
        </tr>
    <?php
    $style = 0;
    $flagCSS = FALSE;

    foreach ($arr_result as $vendorDTO) {
        if ($flagCSS) {
            $style = 1;
            $flagCSS = FALSE;
        } else {
            $style = 0;
            $flagCSS = TRUE;
        }
    ?>
        <tr class="tableFila<?php echo $style; ?>">
            <td><?php echo $vendorDTO->getID_vendors() ?></td>
            <td><?php echo utf8_encode($vendorDTO->getCompanyName()); ?></td>
            <td><?php echo utf8_encode($vendorDTO->getAddress()); ?></td>
            <td><?php echo utf8_encode($vendorDTO->getState() . ", " . $vendorDTO->getCountry()) ?></td>
            <td><?php echo $vendorDTO->getPhone(); ?></td>
            <td><img src="<?php echo $RELATIVE_COMMON_PATH ?>/common/img/sel_ok.png" height="12px" width="12px" style="cursor: pointer" onclick="ajaxSelectVendor(<?php echo $vendorDTO->getID_vendors(); ?>)" /></td>
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