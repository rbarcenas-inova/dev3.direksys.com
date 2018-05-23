<?php
/**
 * Description
 *
 * @author L.C.I Cesar Cedillo
 */
session_start();

include_once '../../../trsBase.php';
require_once '../../../common/php/class/db/DbHandler.php';
require_once '../../../common/php/class/dto.catalog.WarehousesDTO.php';
require_once '../../../common/php/class/dao.catalog.WarehousesDAO.php';

$RELATIVE_COMMON_PATH = "../..";

$return_action = isset($_SESSION['RETURN_ACTION']) ? $_SESSION['RETURN_ACTION'] : 'chg_total';


$action = isset($_POST['action']) ? $_POST['action'] : $in['action'];

if (isset($_SESSION['ARRAY_ORDER_PARTS'])) {
    $array_order_parts = $_SESSION['ARRAY_ORDER_PARTS'];
} else {
    $array_order_parts = array();
}
//--- agrega una parte del widget de busqueda al listado
if ($action == 'add_part') {
    $part_qty = 1;
    $part_sprice = 0.01;
    $part_ship = 0;
    $part_tax = 0;
    $part_discount = 0;
    $part_pkg_condition = "New/Undeliverable";
    $part_item_condition = "New";
    //- condicion del UPC
    $part_upc_status = 'Conforming';

    $ID_part = isset($_POST['pid']) ? $_POST['pid'] : $in['pid'];
    $part_sku = isset($_POST['psku']) ? $_POST['psku'] : $in['psku'];
    $part_model = isset($_POST['pmodel']) ? $_POST['pmodel'] : $in['pmodel'];
    $part_name = isset($_POST['pname']) ? $_POST['pname'] : $in['pname'];
    $part_cost = isset($_POST['pcost']) ? $_POST['pcost'] : $in['pcost'];


    $array_part_info = array(
        'id_part' => $ID_part,
        'part_sku' => $part_sku,
        'part_model' => $part_model,
        'part_name' => $part_name,
        'part_cost' => $part_cost,
        'part_qty' => $part_qty,
        'part_sprice' => $part_sprice,
        'part_discount' => $part_discount,
        'part_shipping' => $part_ship,
        'part_tax' => $part_tax,
        'part_total' => $part_qty * $part_sprice,
        'part_pkg_condition' => $part_pkg_condition,
        'part_item_condition' => $part_item_condition,
        'part_upc_status' => $part_upc_status, //- condicion del upc
        'part_upcs_array' => array(),
        'part_exchange_array' => array(),
        'id_warehouse_dest' => 0
    );

    $array_order_parts[] = $array_part_info;
    $_SESSION['ARRAY_ORDER_PARTS'] = $array_order_parts;

    showPartsList($array_order_parts);
} else if ($action == 'del_part') {   //-- Elimina un item del listado
    $idx = isset($_POST['idx']) ? $_POST['idx'] : $in['idx'];

    unset($array_order_parts[$idx]);
    $_SESSION['ARRAY_ORDER_PARTS'] = $array_order_parts;

    showPartsList($array_order_parts);
} else if ($action == 'mod_part_info') {   //-- modifica la informacion de los items
    $idx = isset($_POST['idx']) ? $_POST['idx'] : $in['idx'];
    $part_qty = isset($_POST['pqty']) ? $_POST['pqty'] : $in['pqty'];
    $part_cost = isset($_POST['pcost']) ? $_POST['pcost'] : $in['pcost'];
    $part_total = isset($_POST['ptotal']) ? $_POST['ptotal'] : $in['ptotal'];
    $part_sprice = isset($_POST['psprice']) ? $_POST['psprice'] : $in['psprice'];
    $part_discount = isset($_POST['pdiscount']) ? $_POST['pdiscount'] : $in['pdiscount'];
    $part_ship = isset($_POST['pship']) ? $_POST['pship'] : $in['pship'];
    $part_tax = isset($_POST['ptax']) ? $_POST['ptax'] : $in['ptax'];

    //- status del upc
    $part_upc_status = isset($_POST['pupcstatus']) ? $_POST['pupcstatus'] : $in['pupcstatus'];

    //--- Obtiene el array con la informacion de la parte a actualizar
    $array_part_info = $array_order_parts[$idx];
    //--- Actualiza la informacion en el arreglo de la informacion de la parte
    $array_part_info['part_qty'] = $part_qty;
    $array_part_info['part_cost'] = $part_cost;
    $array_part_info['part_total'] = $part_total;
    $array_part_info['part_sprice'] = $part_sprice;
    $array_part_info['part_discount'] = $part_discount;
    $array_part_info['part_shipping'] = $part_ship;
    $array_part_info['part_tax'] = $part_tax;

    $array_part_info['part_upc_status'] = $part_upc_status;

    $array_order_parts[$idx] = $array_part_info;

    $_SESSION['ARRAY_ORDER_PARTS'] = $array_order_parts;

} else if ($action == 'update_order_totals') {  //-- Actualiza los totales de la orden
    echo jsonOrdersTotal($array_order_parts);
} else if ($action == 'save_upcs') {  //-- guarda la informacion de los upcs
    $idx = isset($_POST['idx']) ? $_POST['idx'] : $in['idx'];
    $part_upcs_list = isset($_POST['upcs_list']) ? $_POST['upcs_list'] : $in['upcs_list'];

    //-- separa la cadena de los upcs por medio del espacio ' '    
    $part_upcs_array = explode(' ', $part_upcs_list);

    //-- obtiene los datos de sesion para almacenarlo en el arreglo
    $array_part_info = $array_order_parts[$idx];
    $array_part_info['part_upcs_array'] = $part_upcs_array;
    $array_order_parts[$idx] = $array_part_info;

    //-- guarda los datos en sesion
    $_SESSION['ARRAY_ORDER_PARTS'] = $array_order_parts;

    echo 1;
} else if ($action == 'show_upcs') {  //-- muestra la informacion de los upcs
    $idx = isset($_POST['idx']) ? $_POST['idx'] : $in['idx'];

    $array_part_info = $array_order_parts[$idx];
    $part_upcs_array = $array_part_info['part_upcs_array'];

    $part_upcs_list = "";
    foreach ($part_upcs_array as $upc) {
        $part_upcs_list .= $upc . ' ';
    }
    $part_upcs_list = trim($part_upcs_list);

    echo $part_upcs_list;
} else if ($action == 'save_warehouse') {  //-- guarda la informacion de los upcs
    $idx = isset($_POST['idx']) ? $_POST['idx'] : $in['idx'];
    
    $id_warehouse = isset($_POST['id_wh_dest']) ? $_POST['id_wh_dest'] : $in['id_wh_dest'];
   
    //-- obtiene los datos de sesion para almacenarlo en el arreglo
    $array_part_info = $array_order_parts[$idx];
    $array_part_info['id_warehouse_dest'] = $id_warehouse;
    $array_order_parts[$idx] = $array_part_info;

    //-- guarda los datos en sesion
    $_SESSION['ARRAY_ORDER_PARTS'] = $array_order_parts;

    echo 1;
} else if ($action == 'show_warehouse') {
    $idx = isset($_POST['idx']) ? $_POST['idx'] : $in['idx'];
    $array_part_info = $array_order_parts[$idx];

    showWarehouseList($array_part_info);
} else if ($action == 'show_parts_list') {
    showPartsList($array_order_parts);
}
?>
<?php

function showPartsList($arr_order_parts) {
    global $return_action;
    global $RELATIVE_COMMON_PATH;
    ?>

    <table width="100%" align="center"  class="List">
        <tr class="tableListColumn">
            <td width="10%">SKU</td>
            <td>Informacion del Item</td>
            <td style="min-width: 6%;" align="center">Cant.</td>
            <td style="min-width: 6%;" align="center">Precio Vta.</td>
            <td style="min-width: 6%;" align="center">Desc.</td>
            <td style="min-width: 6%;" align="center">Env.</td>
            <td style="min-width: 5%;" align="center">Costo</td>
            <td style="min-width: 6%;" align="center">Imp.</td>
            <td style="min-width: 6%;" align="center">Total</td>
            <td align="center">Almacen Dest.</td>
            <td align="center">Estado</td>
            <td></td>
            <td></td>
        </tr>
        <?php
        $style = 0;
        $flagCSS = FALSE;
        $hasUPCS = "1"; //-- bandera para validar si todos los elementos tienen upc

        foreach ($arr_order_parts as $idx => $arr_parts) {
            if ($flagCSS) {
                $style = 1;
                $flagCSS = FALSE;
            } else {
                $style = 0;
                $flagCSS = TRUE;
            }

            $legendWarehousesCSS = "color: #000000";
            if ($arr_parts['id_warehouse_dest'] != 0) {
                $hasWarehouse = "1";
            } else {
                $hasWarehouse = "";
                $legendWarehousesCSS = "color: #D31E11";
            }
            ?>
            <tr class="tableFila<?php echo $style; ?>">
                <td><?php echo $arr_parts["part_sku"]; ?></td>
                <td><?php echo $arr_parts["part_name"]; ?></td>
                <td align="center">
                    <input type="text" value="<?php echo $arr_parts["part_qty"]; ?>" name="txtOrdProductQty-<?php echo $idx; ?>" id="txtOrdProductQty-<?php echo $idx; ?>" onkeyup="this.value = validar_numerico_keyup(this.value)" onfocus="$(this).select()" onclick="$(this).select()" onchange="validateOrderProductInformation(<?php echo $idx; ?>)"  class="text-box-price" size="7"  />
                </td>
                <td align="center">
                    <input type="text" value="<?php echo $arr_parts["part_sprice"]; ?>" name="txtOrdProductSPrice-<?php echo $idx; ?>" id="txtOrdProductSPrice-<?php echo $idx; ?>" onkeyup="this.value = validar_numerico_keyup(this.value)" onfocus="$(this).select()" onclick="$(this).select()" onchange="validateOrderProductInformation(<?php echo $idx; ?>)"  class="text-box-price" size="7"  />
                </td>
                <td align="center">
                    <input type="text" value="<?php echo $arr_parts["part_discount"]; ?>" name="txtOrdProductDisc-<?php echo $idx; ?>" id="txtOrdProductDisc-<?php echo $idx; ?>" onkeyup="this.value = validar_numerico_keyup(this.value)" onfocus="$(this).select()" onclick="$(this).select()" onchange="validateOrderProductInformation(<?php echo $idx; ?>)"  class="text-box-price" size="7"  />
                </td>                
                <td align="center">
                    <input type="text" value="<?php echo $arr_parts["part_shipping"]; ?>" name="txtOrdProductShipping-<?php echo $idx; ?>" id="txtOrdProductShipping-<?php echo $idx; ?>" onkeyup="this.value = validar_numerico_keyup(this.value)" onfocus="$(this).select()" onclick="$(this).select()" onchange="validateOrderProductInformation(<?php echo $idx; ?>)"  class="text-box-price" size="7"  />
                </td>                
                <td align="center">
                    <input type="text" value="<?php echo $arr_parts["part_cost"]; ?>" name="txtOrdProductCost-<?php echo $idx; ?>" id="txtOrdProductCost-<?php echo $idx; ?>" onkeyup="this.value = validar_numerico_keyup(this.value)" onfocus="$(this).select()" onclick="$(this).select()" onchange="validateOrderProductInformation(<?php echo $idx; ?>)" class="text-box-price" size="6" />
                </td>
                <td align="center">
                    <input type="text" value="<?php echo $arr_parts["part_tax"]; ?>" name="txtOrdProductTax-<?php echo $idx; ?>" id="txtOrdProductTax-<?php echo $idx; ?>" onkeyup="this.value = validar_numerico_keyup(this.value)" onfocus="$(this).select()" onclick="$(this).select()" onchange="validateOrderProductInformation(<?php echo $idx; ?>)"  class="text-box-price" size="7"  />
                </td>                 
                <td align="center">
                    <input type="text" value="<?php echo $arr_parts["part_total"]; ?>" name="txtOrdProductTotal-<?php echo $idx; ?>" id="txtOrdProductTotal-<?php echo $idx; ?>"  onkeyup="this.value = validar_numerico_keyup(this.value)" onfocus="$(this).select()" onclick="$(this).select()"class="text-box-price" size="10" readonly="" />
                </td>
                
                <td align="center">
                    <span id="spnLegendWhs-<?php echo $idx; ?>" style="<?php echo $legendWarehousesCSS; ?>">
                        <?php echo $arr_parts['id_warehouse_dest'] == 0 ? 'No' : 'Si'; ?>
                    </span>
                    <img src="<?php echo $RELATIVE_COMMON_PATH ?>/common/img/b_edit.gif" height="14px" width="14px" style="cursor: pointer" onclick="loadPopupWarehouses(<?php echo $idx; ?>)" alt="Modificar Warehouse"  title="Modificar Warehouse" />
                </td>

                <td align="center">
                    <select name="lstUpcStatus-<?php echo $idx; ?>" id="lstUpcStatus-<?php echo $idx; ?>" class="text-box" onchange="validateOrderProductInformation(<?php echo $idx; ?>)">
                        <option value="Conforming" <?php echo $arr_parts["part_upc_status"] == 'Conforming' ? 'selected' : ''; ?>>Conforming</option>
                        <option value="NC-Open Box" <?php echo $arr_parts["part_upc_status"] == 'NC-Open Box' ? 'selected' : ''; ?>>NC-Open Box</option>
                        <option value="NC-Damaged" <?php echo $arr_parts["part_upc_status"] == 'NC-Damaged' ? 'selected' : ''; ?>>NC-Damaged</option>
                        <option value="NC Scrap" <?php echo $arr_parts["part_upc_status"] == 'NC Scrap' ? 'selected' : ''; ?>>NC Scrap</option>
                        <option value="TBD" <?php echo $arr_parts["part_upc_status"] == 'TBD' ? 'selected' : ''; ?>>TBD</option>
                    </select>
                </td>
                <td align="center">
                    <?php
                    if ($return_action == 'chg_fisico') {
                        ?>
                        <img src="<?php echo $RELATIVE_COMMON_PATH ?>/common/img/workflow.png" height="18px" width="18px" style="cursor: pointer" onclick="triggerPopupParts('popup-parts2',60,'','<?php echo $idx; ?>')" alt="Agregar Item para Intercambio" title="Agregar Item para Intercambio" />
                        <?php
                    }
                    ?>
                </td>
                <td align="center">
                    <img src="<?php echo $RELATIVE_COMMON_PATH ?>/common/img/delete.png" height="12px" width="12px" style="cursor: pointer" onclick="ajaxDeleteOrderPart(<?php echo $idx; ?>)" />
                </td>
            </tr>
            <?php
        }
        ?>
        <?php /*
          <input type="hidden" id="hdHasUpcs" value="<?php echo $hasUPCS; ?>" style="visibility: hidden; display: none;" />
         * 
         */        
        ?>
            <input type="hidden" id="hdHasWarehouse" value="<?php echo $hasWarehouse; ?>" style="visibility: hidden; display: none;" />
    </table>

    <?php
}
?>
<?php

function showWarehouseList($array_part_info) {


    $id_warehouse = $array_part_info['id_warehouse_dest'];

    $wh_type = 'Virtual';

    $whDAO = new WarehousesDAO();
    $whDTO = new WarehousesDTO();

    $whDTO->setType($wh_type);
    $whDTO->setStatus("Active");
    $array_wh = $whDAO->selectRecords($whDTO, TRUE);
    ?>

    <select name="lstDestWarehouse" id="lstDestWarehouse" class="text-box">
        <option value="">--- Seleccione ---</option>
    <?php
    foreach ($array_wh as $whDTO) {
        ?>
        <option value="<?php echo $whDTO->getID_warehouses() ?>" <?php echo $whDTO->getID_warehouses() == $id_warehouse ? 'selected' : ''; ?> ><?php echo $whDTO->getName(); ?>&nbsp;&lt;<?php echo $whDTO->getState(); ?>,&nbsp;<?php echo $whDTO->getCity(); ?>&nbsp;&gt;</option>
        <?php
        }
        ?>
    </select>

    <?php
}
?>
<?php

function jsonOrdersTotal($arr_order_parts) {
    $total_items = 0;
    $total_order = 0;
    $total_ship = 0;
    $total_tax = 0;
    $total_disc = 0;
    $total_product_list = 0;

    foreach ($arr_order_parts as $arr_parts) {
        $total_items += $arr_parts["part_qty"];
        $total_order += $arr_parts["part_total"];
        $total_ship += $arr_parts["part_shipping"];
        $total_tax += $arr_parts["part_tax"];
        $total_disc += $arr_parts["part_discount"];
    }

    $total_product_list = count($arr_order_parts);

    $array_json = array(
        "total_items" => number_format($total_items, 2, '.', ','),
        'total_order' => number_format($total_order, 2, '.', ','),
        'total_ship' => number_format($total_ship, 2, '.', ','),
        'total_disc' => number_format($total_disc, 2, '.', ','),
        'total_tax' => number_format($total_tax, 2, '.', ','),
        'total_product_list' => $total_product_list
    );

    return json_encode($array_json);
}
?>