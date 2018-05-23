<?php
/**
 * Description
 *
 * @author L.C.I Cesar Cedillo
 */
session_start();

include_once '../../../trsBase.php';


$RELATIVE_COMMON_PATH = "../..";

$action = isset($_POST['action']) ? $_POST['action'] : $in['action'];

if (isset($_SESSION['ARRAY_PO_PARTS'])) {
    $array_order_parts = $_SESSION['ARRAY_PO_PARTS'];
} else {
    $array_order_parts = array();
}
//--- agrega una parte del widget de busqueda al listado
if ($action == 'add_part') {
    $part_qty = 1;
    $part_preqty = 0;
    $part_recvd = 0;
    $part_price = 0.00;
    $part_ship = 0;
    $part_tax = 0;
    $part_discount = 0;
    //- condicion del UPC
    $part_upc_status = 'Conforming';

    $ID_part = isset($_POST['pid']) ? $_POST['pid'] : $in['pid'];
    $part_sku = isset($_POST['psku']) ? $_POST['psku'] : $in['psku'];
    $part_model = isset($_POST['pmodel']) ? $_POST['pmodel'] : $in['pmodel'];
    $part_name = isset($_POST['pname']) ? $_POST['pname'] : $in['pname'];
    

    $array_part_info = array(
        'id_part' => $ID_part,
        'part_sku' => $part_sku,
        'part_model' => $part_model,
        'part_name' => $part_name,
        'part_qty' => $part_qty,
        'part_preqty' => $part_preqty,
        'part_recvd' => $part_recvd,
        'part_price' => $part_price,
        'part_total' => $part_qty * $part_price,
        'part_upcs_array' => array(),
        'part_exchange_array' => array()
    );


    $array_order_parts[] = $array_part_info;
    $_SESSION['ARRAY_PO_PARTS'] = $array_order_parts;

    showPartsList($array_order_parts);
} else if ($action == 'del_part') {   //-- Elimina un item del listado
    $idx = isset($_POST['idx']) ? $_POST['idx'] : $in['idx'];

    unset($array_order_parts[$idx]);
    $_SESSION['ARRAY_PO_PARTS'] = $array_order_parts;

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
    /*
      $part_pkg_condition = isset($_POST['ppckgcond']) ? $_POST['ppckgcond'] : $in['ppckgcond'];
      $part_item_condition = isset($_POST['pitemcond']) ? $_POST['pitemcond'] : $in['pitemcond'];
     */
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
    /*
      $array_part_info['part_pkg_condition'] = $part_pkg_condition;
      $array_part_info['part_item_condition'] = $part_item_condition;
     * 
     */
    $array_part_info['part_upc_status'] = $part_upc_status;

    $array_order_parts[$idx] = $array_part_info;

    $_SESSION['ARRAY_PO_PARTS'] = $array_order_parts;
    /*
      //- Compara si el numero de upcs es igual a la cantidad de items
      $isEqualUpcsItems = 0;  //- 0: no hay upcs,  1: upcs diferente de cantidad, 2: upcs iguales
      if(! empty($array_part_info['part_upcs_array'])){
      if(count($array_part_info['part_upcs_array']) == $part_qty){
      $isEqualUpcsItems = 2;
      }else{
      $isEqualUpcsItems = 1;
      }
      }

      echo $isEqualUpcsItems;
     */
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
    $_SESSION['ARRAY_PO_PARTS'] = $array_order_parts;

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
            <td width="3%" align="center">#</td>
            <td width="10%">SKU</td>
            <td>Modelo / Descripcion</td>
            <td style="min-width: 10%;" align="center">Cantidad</td>
            <td style="min-width: 10%;" align="center">Pre-Recepcion</td>
            <td style="min-width: 10%;" align="center">Recibido</td>
            <td style="min-width: 8%;" align="center">Precio</td>
            <td style="min-width: 10%;" align="center">Sub Total</td>
            <td></td>
        </tr>
    <?php
    $style = 0;
    $flagCSS = FALSE;
    $hasUPCS = "1"; //-- bandera para validar si todos los elementos tienen upc
    $itemCount = 0;
    foreach ($arr_order_parts as $idx => $arr_parts) {

        if ($flagCSS) {
            $style = 1;
            $flagCSS = FALSE;
        } else {
            $style = 0;
            $flagCSS = TRUE;
        }

        //--- UPCS
        $legendUpcsCSS = "color: #000000";
        if (empty($arr_parts['part_upcs_array'])) {
            $hasUPCS = "";
        } else if (count($arr_parts['part_upcs_array']) != $arr_parts["part_qty"]) {
            $hasUPCS = "";
            $legendUpcsCSS = "color: #D31E11";
        }
        ?>
            <tr class="tableFila<?php echo $style; ?>">
                <td align="center"><?php echo++$itemCount; ?></td>
                <td><?php echo $arr_parts["part_sku"]; ?></td>
                <td><?php echo $arr_parts["part_model"] . '<br>' . $arr_parts["part_name"]; ?></td>
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
                    <input type="text" value="<?php echo $arr_parts["part_total"]; ?>" name="txtOrdProductTotal-<?php echo $idx; ?>" id="txtOrdProductTotal-<?php echo $idx; ?>"  onkeyup="this.value = validar_numerico_keyup(this.value)" onfocus="$(this).select()" onclick="$(this).select()"class="text-box-price" size="10" readonly="" />
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
    </table>

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