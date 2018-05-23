<?php
/**
 * Description
 *
 * @author L.C.I Cesar Cedillo
 */
global $COMMON_PATH;
require_once $COMMON_PATH . '/common/php/class/db/DbHandler.php';
require_once $COMMON_PATH . '/common/php/class/dto.catalog.WarehousesDTO.php';
require_once $COMMON_PATH . '/common/php/class/dao.catalog.WarehousesDAO.php';


$wh_type = 'Virtual'; //-- busca todos lo que no sean virtuales

$whDAO = new WarehousesDAO();
$whDTO = new WarehousesDTO();

$whDTO->setType($wh_type);
$whDTO->setStatus("Active");
$array_wh = $whDAO->selectRecords($whDTO,TRUE);

?>

<select name="lstWarehouse" id="lstWarehouse" class="text-box">
    <option value="">--- Seleccione ---</option>
    <?php
    foreach ($array_wh as $whDTO) {        
        ?>
    <option value="<?php echo $whDTO->getID_warehouses()?>" ><?php echo $whDTO->getName(); ?>&nbsp;&lt;<?php echo $whDTO->getState(); ?>,&nbsp;<?php echo $whDTO->getCity(); ?>&nbsp;&gt;</option>
        <?php
    }
    ?>
</select>