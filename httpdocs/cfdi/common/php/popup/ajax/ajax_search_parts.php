<?php
/*
  Function: ajax_search_parts

  Busca los datos de la tabla sl_parts en base a los parametros requeridos

  Parameters:

  pid - ID de la parte.
  pmodel - Modelo de la parte.
  pname - Nombre de la parte.

  Returns:

  Listado con todos los productos encontrados.

  See Also:

  /common/php/popup/ajax/ajax_popup_parts_generator.php
 */

//include_once '../../../nsAdmBase.php';

include_once '../../../../trsBase.php';

require_once '../../class/db/DbHandler.php';
require_once '../../class/dto.catalog.PartsDTO.php';
require_once '../../class/dao.catalog.PartsDAO.php';
include_once '../../functions/products_functions.php';

//--- Constantes
$RELATIVE_COMMON_PATH = "../..";
$PRODUCT_SKU = 400000000;

//---- parametros de paginacion 
$results_per_page = isset($_POST['results_per_page']) ? $_POST['results_per_page'] : $_GET['results_per_page'];
$page = isset($_POST['page']) ? $_POST['page'] : $_GET['page'];
$start = ($page - 1) * $results_per_page;

//---- Recibe los parametros desde la llamada ajax
$ID_part = trim(isset($_POST['pid']) ? $_POST['pid'] : isset($in['pid']) ? $in['pid'] : $_GET['pid'] );
$part_model = trim(isset($_POST['pmodel']) ? $_POST['pmodel'] : isset($in['pmodel']) ? $in['pmodel'] : $_GET['pmodel']);
$part_name = trim(isset($_POST['pname']) ? $_POST['pname'] : isset($in['pname']) ? $in['pname'] : $_GET['pname']);
//$target_usge = isset($in['target_usage']) ? $in['target_usage'] : isset($_POST['target_usage']) ? $_POST['target_usage'] : isset($_GET['target_usage']) ? $_GET['target_usage'] : "";

if(isset($_GET['target_usage'])){
    $target_usage = $_GET['target_usage'];
}elseif(isset($_POST['target_usage'])){
     $target_usage = $_POST['target_usage'];
}elseif(isset($in['target_usage'])){
    $target_usage = $in['target_usage'];
}else{
    $target_usage = '';
}

if(isset($_GET['popup'])){
    $popup_id = $_GET['popup'];
}elseif(isset($_POST['popup'])){
     $popup_id = $_POST['popup'];
}elseif(isset($in['popup'])){
    $popup_id = $in['popup'];
}else{
    $popup_id = '';
}


//--- Crea los objetos
$partsDAO = new PartsDAO();
$partsDTO = new PartsDTO();

if (is_numeric($ID_part) || strlen($part_model) > 2 || strlen($part_name) > 2) {

    $partsDTO->setID_parts(is_numeric($ID_part) ? $ID_part : 0);
    $partsDTO->setModel($part_model);
    $partsDTO->setName($part_name);

    $partsDAO->setPagerStart($start);
    $partsDAO->setPagerPerPage($results_per_page);
//--- Ejecuta la consulta
    $arr_result = $partsDAO->selectRecords($partsDTO);
} else {
    $arr_result = array();
}
?>
<?php
if (!empty($arr_result)) {
    ?>
    <table width="100%" align="center"  class="List">

        <tr class="tableListColumn">
            <td>ID Part</td>
            <td>Model</td>
            <td>Name</td>
            <td>Cost</td>
            <td></td>
            <td></td>
        </tr>    
        <?php
        $style = 0;
        $flagCSS = FALSE;

        foreach ($arr_result as $partsDTO) {
            if ($flagCSS) {
                $style = 1;
                $flagCSS = FALSE;
            } else {
                $style = 0;
                $flagCSS = TRUE;
            }

            $sku_part = $PRODUCT_SKU + (int) $partsDTO->getID_parts();
            $part_cost = load_sltvcost($sku_part);
            $part_cost = number_format($part_cost, 2, '.', '');
            ?>
            <tr class="tableFila<?php echo $style; ?>">
                <td><?php echo $partsDTO->getID_parts() ?></td>
                <td><?php echo $partsDTO->getModel(); ?></td>
                <td><?php echo $partsDTO->getName(); ?></td>
                <td><?php echo $part_cost; ?></td>
                <td></td>
                <td>                    
                    <?php /* <img src="<?php echo $RELATIVE_COMMON_PATH ?>/common/img/sel_ok.png" height="12px" width="12px" style="cursor: pointer" onclick="ajaxSelectPart('<?php echo $target_usage; ?>',<?php echo $partsDTO->getID_parts() ?> , <?php echo $sku_part; ?> ,'<?php echo $partsDTO->getModel(); ?>','<?php echo $partsDTO->getName(); ?>',<?php echo $part_cost; ?>)" /> */ ?>
                    <img src="<?php echo $RELATIVE_COMMON_PATH ?>/common/img/sel_ok.png" height="12px" width="12px" style="cursor: pointer" onclick="ajaxSelectPart('<?php echo $target_usage; ?>',<?php echo $partsDTO->getID_parts() ?> , <?php echo $sku_part; ?> ,'<?php echo $partsDTO->getModel(); ?>','<?php echo $partsDTO->getName(); ?>',<?php echo $part_cost; ?>, $('#hdRelatedPartID-<?php echo $popup_id;?>').val())" />
                </td>
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