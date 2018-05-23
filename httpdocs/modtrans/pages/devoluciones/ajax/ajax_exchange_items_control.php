<?php
/**
 * Description
 *
 * @author L.C.I Cesar Cedillo
 */
session_start();

include_once '../../../trsBase.php';


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
    //--- recibe los parametros
    //- condicion del UPC
    $part_upc_status = 'Conforming';

    $ID_part = isset($_POST['pid']) ? $_POST['pid'] : $in['pid'];
    $part_sku = isset($_POST['psku']) ? $_POST['psku'] : $in['psku'];
    $part_model = isset($_POST['pmodel']) ? $_POST['pmodel'] : $in['pmodel'];
    $part_name = isset($_POST['pname']) ? $_POST['pname'] : $in['pname'];
    $part_cost = isset($_POST['pcost']) ? $_POST['pcost'] : $in['pcost'];

    //--- indice de la part de la orden a la que se relaciona el item
    $idx = isset($_POST['relpidx']) ? $_POST['relpidx'] : $in['relpidx'];
    //--- Obtiene el array con la informacion de item al que se vinculara el item de intercambio
    $array_part_info = $array_order_parts[$idx];
    //--- Obtiene el array con la informacion de los items de intercambios
    $array_items_exchange = $array_part_info['part_exchange_array'];

    $part_qty = 1;
    $part_sprice = 0.01;
    $part_ship = 0;
    $part_tax = 0;
    $part_discount = 0;
    //$part_pkg_condition = "New/Undeliverable";
    //$part_item_condition = "New";

    $array_items_exchg_info = array(
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
        'part_total' => $part_qty * $part_sprice
            //'part_pkg_condition' => $part_pkg_condition,
            //'part_item_condition' => $part_item_condition,
            //'part_upc_status' => $part_upc_status,    //- condicion del upc
            //'part_upcs_array' => array()
    );

    $array_items_exchange[] = $array_items_exchg_info;
    $array_part_info['part_exchange_array'] = $array_items_exchange;
    $array_order_parts[$idx] = $array_part_info;

    $_SESSION['ARRAY_ORDER_PARTS'] = $array_order_parts;

    showPartsList($array_order_parts);
} else if ($action == 'del_part') {   //-- Elimina un item del listado
    $idx = isset($_POST['relpidx']) ? $_POST['relpidx'] : $in['relpidx'];
    $idx_exchg = isset($_POST['exchgidx']) ? $_POST['exchgidx'] : $in['exchgidx'];
    
    
    unset($array_order_parts[$idx]['part_exchange_array'][$idx_exchg]);
    $_SESSION['ARRAY_ORDER_PARTS'] = $array_order_parts;

    showPartsList($array_order_parts);
} else if ($action == 'mod_part_info') {   //-- modifica la informacion de los items
    $idx = isset($_POST['idx']) ? $_POST['idx'] : $in['idx'];
    $idxex = isset($_POST['relpidx']) ? $_POST['relpidx'] : $in['relpidx'];;
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
    $array_part_info = $array_order_parts[$idx]['part_exchange_array'][$idxex];
    //--- Actualiza la informacion en el arreglo de la informacion de la parte
    $array_part_info['part_qty'] = $part_qty;
    $array_part_info['part_cost'] = $part_cost;
    $array_part_info['part_total'] = $part_total;
    $array_part_info['part_sprice'] = $part_sprice;
    $array_part_info['part_discount'] = $part_discount;
    $array_part_info['part_shipping'] = $part_ship;
    $array_part_info['part_tax'] = $part_tax;
        

    $array_order_parts[$idx]['part_exchange_array'][$idxex] = $array_part_info;

    $_SESSION['ARRAY_ORDER_PARTS'] = $array_order_parts;

} else if ($action == 'update_exchange_totals') {  //-- Actualiza los totales de la orden
    echo jsonOrdersTotal($array_order_parts);
    
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
            <td width="10%">SKU Cambio</td>
            <td>Informacion del Item</td>
            <td style="min-width: 6%;" align="center">Cant.</td>
            <td style="min-width: 6%;" align="center">Precio Vta.</td>
            <td style="min-width: 6%;" align="center">Desc.</td>
            <td style="min-width: 6%;" align="center">Env.</td>
            <td style="min-width: 5%;" align="center">Costo</td>
            <td style="min-width: 6%;" align="center">Imp.</td>
            <td style="min-width: 6%;" align="center">Total</td>           
            <td align="center"></td>            
            <td></td>
        </tr>
        <?php
        $style = 0;
        $flagCSS = FALSE;
        //print_r($arr_order_parts);
        foreach ($arr_order_parts as $idx => $arr_inorders_parts) {
            $arr_exchg_parts = $arr_inorders_parts['part_exchange_array'];
            $sku_order_part = $arr_inorders_parts['part_sku'];
            
            foreach ($arr_exchg_parts as $idx_exchg => $arr_parts) {
                
                if ($flagCSS) {
                    $style = 1;
                    $flagCSS = FALSE;
                } else {
                    $style = 0;
                    $flagCSS = TRUE;
                }

                ?>
                <tr class="tableFila<?php echo $style; ?>">
                    <td><?php echo $sku_order_part; ?></td>
                    <td><?php echo $arr_parts["part_sku"]; ?></td>
                    <td><?php echo $arr_parts["part_name"]; ?></td>
                    <td align="center">
                        <input type="text" value="<?php echo $arr_parts["part_qty"]; ?>" name="txtOrdProductQty-<?php echo $idx . '-' . $idx_exchg?>" id="txtOrdProductQty-<?php echo $idx . '-' . $idx_exchg?>" onkeyup="this.value = validar_numerico_keyup(this.value)" onfocus="$(this).select()" onclick="$(this).select()" onchange="validateExchangeProductInformation(<?php echo $idx; ?>,<?php echo $idx_exchg?>)"  class="text-box-price" size="7"  />
                    </td>
                    <td align="center">
                        <input type="text" value="<?php echo $arr_parts["part_sprice"]; ?>" name="txtOrdProductSPrice-<?php echo $idx . '-' . $idx_exchg?>" id="txtOrdProductSPrice-<?php echo $idx . '-' . $idx_exchg?>" onkeyup="this.value = validar_numerico_keyup(this.value)" onfocus="$(this).select()" onclick="$(this).select()" onchange="validateExchangeProductInformation(<?php echo $idx; ?>,<?php echo $idx_exchg?>)"  class="text-box-price" size="7"  />
                    </td>
                    <td align="center">
                        <input type="text" value="<?php echo $arr_parts["part_discount"]; ?>" name="txtOrdProductDisc-<?php echo $idx . '-' . $idx_exchg?>" id="txtOrdProductDisc-<?php echo $idx . '-' . $idx_exchg?>" onkeyup="this.value = validar_numerico_keyup(this.value)" onfocus="$(this).select()" onclick="$(this).select()" onchange="validateExchangeProductInformation(<?php echo $idx; ?>,<?php echo $idx_exchg?>)"  class="text-box-price" size="7"  />
                    </td>                
                    <td align="center">
                        <input type="text" value="<?php echo $arr_parts["part_shipping"]; ?>" name="txtOrdProductShipping-<?php echo $idx . '-' . $idx_exchg?>" id="txtOrdProductShipping-<?php echo $idx . '-' . $idx_exchg?>" onkeyup="this.value = validar_numerico_keyup(this.value)" onfocus="$(this).select()" onclick="$(this).select()" onchange="validateExchangeProductInformation(<?php echo $idx; ?>,<?php echo $idx_exchg?>)"  class="text-box-price" size="7"  />
                    </td>                
                    <td align="center">
                        <input type="text" value="<?php echo $arr_parts["part_cost"]; ?>" name="txtOrdProductCost-<?php echo $idx . '-' . $idx_exchg?>" id="txtOrdProductCost-<?php echo $idx . '-' . $idx_exchg?>" onkeyup="this.value = validar_numerico_keyup(this.value)" onfocus="$(this).select()" onclick="$(this).select()" onchange="validateExchangeProductInformation(<?php echo $idx; ?>,<?php echo $idx_exchg?>)" class="text-box-price" size="6" />
                    </td>
                    <td align="center">
                        <input type="text" value="<?php echo $arr_parts["part_tax"]; ?>" name="txtOrdProductTax-<?php echo $idx . '-' . $idx_exchg?>" id="txtOrdProductTax-<?php echo $idx . '-' . $idx_exchg?>" onkeyup="this.value = validar_numerico_keyup(this.value)" onfocus="$(this).select()" onclick="$(this).select()" onchange="validateExchangeProductInformation(<?php echo $idx; ?>,<?php echo $idx_exchg?>)"  class="text-box-price" size="7"  />
                    </td>                 
                    <td align="center">
                        <input type="text" value="<?php echo $arr_parts["part_total"]; ?>" name="txtOrdProductTotal-<?php echo $idx . '-' . $idx_exchg?>" id="txtOrdProductTotal-<?php echo $idx . '-' . $idx_exchg?>"  onkeyup="this.value = validar_numerico_keyup(this.value)" onfocus="$(this).select()" onclick="$(this).select()"class="text-box-price" size="10" readonly="" />
                    </td>       

                    <td align="center">
                    </td>
                    <td align="center">
                        <img src="<?php echo $RELATIVE_COMMON_PATH ?>/common/img/delete.png" height="12px" width="12px" style="cursor: pointer" onclick="ajaxDeleteExchangePart(<?php echo $idx; ?>, <?php echo $idx_exchg;?>)" />
                    </td>
                </tr>
                <?php
            }
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

    foreach ($arr_order_parts as $order_parts) {
        $arr_parts_exchange = $order_parts['part_exchange_array'];
        
        foreach ($arr_parts_exchange as $arr_parts){
        
            $total_items += $arr_parts["part_qty"];
            $total_order += $arr_parts["part_total"];
            $total_ship += $arr_parts["part_shipping"];
            $total_tax += $arr_parts["part_tax"];
            $total_disc += $arr_parts["part_discount"];
        }
        $total_product_list += count($arr_parts_exchange);
    }
    

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