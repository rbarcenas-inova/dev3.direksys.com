<?php
/**
 * Description
 *
 * @author L.C.I Cesar Cedillo
 */

include_once '../../../../trsBase.php';

require_once '../../class/db/DbHandler.php';
require_once '../../class/dto.catalog.CustomersDTO.php';
require_once '../../class/dao.catalog.CustomersDAO.php';


$RELATIVE_COMMON_PATH = "../..";

//---- parametros de paginacion 
$results_per_page = isset($_POST['results_per_page']) ? $_POST['results_per_page'] : $_GET['results_per_page'];
$page = isset($_POST['page']) ? $_POST['page'] : $_GET['page'];
$start = ($page - 1) * $results_per_page;


//---- Recibe los parametros desde la llamada ajax

$customerID = trim(isset($_POST['cid']) ? $_POST['cid'] : $_GET['cid']);
$customerName = trim(isset($_POST['cname']) ? $_POST['cname'] : $_GET['cname']);
$customerLName1 = trim(isset($_POST['clname1']) ? $_POST['clname1'] : $_GET['clname1']);
$customerLName2 = trim(isset($_POST['clname2']) ? $_POST['clname2'] : $_GET['clname2']);



//--- Crea los objetos
$customerDTO = new CustomersDTO();
$customerDAO = new CustomersDAO();

if (is_numeric($customerID) || strlen($customerName) > 0 || strlen($customerLName1) > 0 || strlen($customerLName1) > 0 ) {

    $customerDTO->setID_customers(is_numeric($customerID) ? $customerID : 0);
    $customerDTO->setFirstName($customerName);
    $customerDTO->setLastName($customerLName1);
    $customerDTO->setLastName2($customerLName2);

//--- Ejecuta la consulta
    $customerDAO->setPagerStart($start);
    $customerDAO->setPagerPerPage($results_per_page);
    
    $arr_result = $customerDAO->searchByCustomerName($customerDTO);
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
            <td>Name</td>
            <td>Last Name</td>
            <td>Addres</td>
            <td>Phone</td>
            <td></td>
        </tr>    
        <?php
        $style = 0;
        $flagCSS = FALSE;

        foreach ($arr_result as $customerDTO) {
            if ($flagCSS) {
                $style = 1;
                $flagCSS = FALSE;
            } else {
                $style = 0;
                $flagCSS = TRUE;
            }
            ?>
            <tr class="tableFila<?php echo $style; ?>">
                <td><?php echo $customerDTO->getID_customers(); ?></td>
                <td><?php echo utf8_encode($customerDTO->getFirstName()); ?></td>
                <td><?php echo utf8_encode($customerDTO->getLastName() . " " . $customerDTO->getLastName2()); ?></td>
                <td><?php echo utf8_encode($customerDTO->getAddress1() . ", " . $customerDTO->getState()) ?></td>
                <td><?php echo $customerDTO->getPhone1(); ?></td>
                <td><img src="<?php echo $RELATIVE_COMMON_PATH ?>/common/img/sel_ok.png" height="12px" width="12px" style="cursor: pointer" onclick="ajaxSelectCustomer(<?php echo $customerDTO->getID_customers(); ?>)" /></td>
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