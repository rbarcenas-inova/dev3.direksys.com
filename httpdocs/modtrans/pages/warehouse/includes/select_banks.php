<?php
/**
 * Description
 *
 * @author L.C.I Cesar Cedillo
 */
global $COMMON_PATH;

require_once $COMMON_PATH . '/trsBase.php';
require_once $COMMON_PATH .'/common/php/class/db/DbHandler.php';
require_once $COMMON_PATH . '/common/php/class/dao.catalog.BanksDAO.php';

$banksDTO = new BanksDTO();
$banksDAO = new BanksDAO();

$arr_banks = $banksDAO->selectRecords($banksDTO);

?>
<select name="lstBanks" id="lstBanks" class="text-box">
    <option value="">--- Seleccione ---</option>
    <?php
    foreach ($arr_banks as $banksDTO) {        
        ?>
    <option value="<?php echo $banksDTO->getID_banks() ?>|<?php echo $banksDTO->getCurrency() ?>" ><?php echo $banksDTO->getName();?><!--&nbsp;&nbsp;&lt;&nbsp;<?php echo $banksDTO->getBankName(); ?>&nbsp;&gt;--></option>
        <?php
    }
    ?>
</select>