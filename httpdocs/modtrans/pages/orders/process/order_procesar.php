<?php
/**
 * Description
 *
 * @author L.C.I Cesar Cedillo
 */
session_start();

include_once '../../../trsBase.php';
include_once '../../../session.php';
require_once '../../../common/php/class/db/DbHandler.php';
require_once '../../../common/php/class/dto.catalog.OrdersDTO.php';
require_once '../../../common/php/class/dao.catalog.OrdersDAO.php';
require_once '../../../common/php/class/dto.catalog.OrdersNotesDTO.php';
require_once '../../../common/php/class/dao.catalog.OrdersNotesDAO.php';
require_once '../../../common/php/class/dto.catalog.OrdersPartsDTO.php';
require_once '../../../common/php/class/dao.catalog.OrdersPartsDAO.php';
require_once '../../../common/php/class/dto.catalog.OrdersProductsDTO.php';
require_once '../../../common/php/class/dao.catalog.OrdersProductsDAO.php';
require_once '../../../common/php/class/dto.catalog.OrdersPaymentsDTO.php';
require_once '../../../common/php/class/dao.catalog.OrdersPaymentsDAO.php';
require_once '../../../common/php/class/dto.catalog.ReturnsDTO.php';
require_once '../../../common/php/class/dao.catalog.ReturnsDAO.php';
require_once '../../../common/php/class/dto.catalog.ReturnsNotesDTO.php';
require_once '../../../common/php/class/dao.catalog.ReturnsNotesDAO.php';
require_once '../../../common/php/class/dto.catalog.ReturnsUpcsDTO.php';
require_once '../../../common/php/class/dao.catalog.ReturnsUpcsDAO.php';
require_once '../../../common/php/class/dto.catalog.SkusDTO.php';
require_once '../../../common/php/class/dao.catalog.SkusDAO.php';

require_once '../../../common/php/class/dao.catalog.AdminLogsDAO.php';

include_once '../../../common/php/functions/orders_functions.php';
include_once '../../../common/php/functions/auth_functions.php';


//-- PARAMETROS DE CONFIGURACION
global $cfg;
$ID_ORDER_LOWER_LIMIT = $cfg['id_orders_min'];
$ID_ORDER_UPPER_LIMIT = $cfg['id_orders_max'];
//$ID_ORDER_LOWER_LIMIT = 10000;
//$ID_ORDER_UPPER_LIMIT = 99999;

$USE_ORDER_AUTOINCREMENT = FALSE;   //-- permite utilizar o no, el valor AUTO_INCREMENT  del campo ID_orders de la tabla sl_orders 
if($cfg['use_id_order_autoincrement'] == '1'){
    $USE_ORDER_AUTOINCREMENT = TRUE;
}

//$ID_WAREHOUSE = 0;
$ID_WAREHOUSE = $cfg['default_warehouse'];

$exito = 0;  //-- Variable para marcar si la operacion tuvo o no exito:  0 - No exitosa, 1 - Exitosa
$process_msg = ""; //- Mensaje que se muestra al usuario

$ID_orders = 0; //-- ID de la orden
$ID_orders_to_insert = 0;


//-- TIPOS DE DEVOLUCION
/*
 *  Refund: Devolucion total,  Exchange: cambio fisico
 */
//- datos del tipo de retorno
if (isset($_POST['hdReturnType'])) {
    $return_type = $_POST['hdReturnType'];
} elseif (isset($in['hdReturnType'])) {
    $return_type = $in['hdReturnType'];
} else {
    $return_type = 'Returned for Refund';
}

if (isset($_POST['hdReturnAction'])) {
    $return_action = $_POST['hdReturnAction'];
} elseif (isset($in['hdReturnAction'])) {
    $return_action = $in['hdReturnAction'];
} else {
    $return_action = 'chg_total';
}

$reception_notes = isset($_POST['txtGeneralReturnNotes']) ? $_POST['txtGeneralReturnNotes'] : $in['txtGeneralReturnNotes'];

//- Datos del cliente
$id_customers = isset($_POST['txtCustomerID']) ? $_POST['txtCustomerID'] : $in['txtCustomerID'];
$cust_name = isset($_POST['txtCustomerName']) ? $_POST['txtCustomerName'] : $in['txtCustomerName'];
$cust_address1 = isset($_POST['txtCustomerAddress1']) ? $_POST['txtCustomerAddress1'] : $in['txtCustomerAddress1'];
$cust_address2 = isset($_POST['txtCustomerAddress2']) ? $_POST['txtCustomerAddress2'] : $in['txtCustomerAddress2'];
$cust_address3 = isset($_POST['txtCustomerAddress3']) ? $_POST['txtCustomerAddress3'] : $in['txtCustomerAddress3'];
$cust_city = isset($_POST['txtCustomerCity']) ? $_POST['txtCustomerCity'] : $in['txtCustomerCity'];
$cust_state = isset($_POST['txtCustomerState']) ? $_POST['txtCustomerState'] : $in['txtCustomerState'];
$cust_zip = isset($_POST['txtCustomerZip']) ? $_POST['txtCustomerZip'] : $in['txtCustomerZip'];
$cust_urbanization = isset($_POST['txtCustomerUrbanization']) ? $_POST['txtCustomerUrbanization'] : $in['txtCustomerUrbanization'];
$cust_phone = isset($_POST['txtCustomerPhone']) ? $_POST['txtCustomerPhone'] : $in['txtCustomerPhone'];
$cust_country = isset($_POST['txtCustomerCountry']) ? $_POST['txtCustomerCountry'] : $in['txtCustomerCountry'];

//-
if (trim($cust_state) == "") {
    $cust_state = NULL;
}

//- Totales de la orden
$orderQty = 0;
$orderShip = 0;
$orderDisc = 0;
$orderTax = 0;
$orderTaxPerc = 0; // porcentaje de tax (cantidad / 100)
//$orderPartsWithTax = 0;
$orderNet = 0;  //- Suma de los SalePrice products
//- Datos de la entrega
$shp_type = 1;
$shp_address1 = $cust_address1;
$shp_address2 = $cust_address2;
$shp_address3 = $cust_address3;
$shp_urbanization = $cust_urbanization;
$shp_city = $cust_city;
$shp_state = $cust_state;
$shp_zip = $cust_zip;
$shp_country = $cust_country;
//$shp_date = isset($_POST['txtShpDate']) ? $_POST['txtShpDate'] : $in['txtShpDate'];
//$postedDate = $shp_date;
$shp_date = NULL;
$postedDate = $shp_date;

//- Notas de la Orden
$prev_id_order = isset($_POST['txtPrevOrderID']) ? $_POST['txtPrevOrderID'] : $in['txtPrevOrderID'];
$order_notes = isset($_POST['txtOrderNotes']) ? $_POST['txtOrderNotes'] : $in['txtOrderNotes'];
$order_status = "New";

//- Datos generales de la orden
$order_status_prd = "None";
$order_status_pay = "None";

$order_payment_type = "";
$order_type = isset($_SESSION['ORDER_TYPE']) ? $_SESSION['ORDER_TYPE'] : '';
if($order_type == "tc"){
    $order_payment_type='Credit-Card';
}elseif($order_type == "cod"){
    $order_payment_type='COD';
}else{
    $order_payment_type='Money Order';    
}

$order_ptype = $order_payment_type;
//$order_ptype = "Money Order";
//- Hash con los datos de los items y sus respectivos ID_orders_products => ['ID_part'] ['ID_orders_products']
$array_id_orders_products = array();

//- Info del sistema
$id_admin_users = isset($usr['id_admin_users']) ? $usr['id_admin_users'] : 0;

//- Info del pago

$payment_type = $order_payment_type;
$payment_pmtField1 = "";
$payment_pmtField2 = "";
$payment_pmtField3 = "";
$payment_pmtField4 = "";
$payment_pmtField5 = "";
$payment_pmtField6 = "";
$payment_pmtField7 = "";
$payment_pmtField8 = "";
$payment_pmtField9 = "";

$payment_status = "Pending";
$payment_reason = "Sale";

$payment_date = isset($_POST['txtPaymentDate']) ? $_POST['txtPaymentDate'] : $in['txtPaymentDate'];
$payment_date = ($payment_date == "") ? date("Y-m-d") : $payment_date;

//- Info de pago para returns
$payment_amount_diff = isset($_POST['txtAmountDiff']) ? $_POST['txtAmountDiff'] : $in['txtAmountDiff'];

//- Informacion para el return
$return_merAction = 'Refund';
$return_general_pkg_condition = isset($_POST['lstProductPkgCondition']) ? $_POST['lstProductPkgCondition'] : $in['lstProductPkgCondition'];
$return_prod_condition = isset($_POST['lstItemCondition']) ? $_POST['lstItemCondition'] : $in['lstItemCondition'];

//------------------------------------------------------------------//
//---------- Procesamiento de los datos de la orden ----------------//
//------------------------------------------------------------------//
$ordersDTO = new OrdersDTO();
$ordersDAO = new OrdersDAO();

if (!$USE_ORDER_AUTOINCREMENT) {
    //- Obtiene el ID order maximo en el rango establecido
    $ID_orders_to_insert = getMaxOrderInRange($ID_ORDER_LOWER_LIMIT, $ID_ORDER_UPPER_LIMIT);
    if ($ID_orders_to_insert == 0) {
        $ID_orders_to_insert = $ID_ORDER_LOWER_LIMIT;
    } else {
        ++$ID_orders_to_insert;
    }
    $ordersDTO->setID_orders($ID_orders_to_insert);
}

$ordersDTO->setID_customers($id_customers);
$ordersDTO->setAddress1($cust_address1);
$ordersDTO->setAddress2($cust_address2);
$ordersDTO->setAddress3($cust_address3);
$ordersDTO->setUrbanization($cust_urbanization);
$ordersDTO->setCity($cust_city);
$ordersDTO->setState($cust_state);
$ordersDTO->setZip($cust_zip);
$ordersDTO->setCountry($cust_country);

$ordersDTO->setShpType($shp_type);
$ordersDTO->setShpName($cust_name);
$ordersDTO->setShpAddress1($shp_address1);
$ordersDTO->setShpAddress2($shp_address2);
$ordersDTO->setShpAddress3($shp_address3);
$ordersDTO->setShpUrbanization($shp_urbanization);
$ordersDTO->setShpCity($shp_city);
$ordersDTO->setShpState($shp_state);
$ordersDTO->setShpZip($shp_zip);
$ordersDTO->setShpCountry($shp_country);

$ordersDTO->setOrderNotes("Orden Original No: " . $prev_id_order . "    - " . $order_notes);
$ordersDTO->setOrderQty($orderQty);
$ordersDTO->setOrderShp($orderShip);
$ordersDTO->setOrderDisc($orderDisc);
$ordersDTO->setOrderTax($orderTax);
$ordersDTO->setOrderNet($orderNet);

$ordersDTO->setPostedDate($postedDate);

$ordersDTO->setPType($order_ptype);
$ordersDTO->setStatusPrd($order_status_prd);
$ordersDTO->setStatusPay($order_status_pay);
$ordersDTO->setStatus($order_status);
$ordersDTO->setID_adminUsers($id_admin_users);

//- Inserta los datos de la Orden
if ($ordersDAO->insertRecord($ordersDTO, $USE_ORDER_AUTOINCREMENT)) {
    $ID_orders = $ordersDAO->getLastInsertId();

    $orderNotesDTO = new OrdersNotesDTO();
    $orderNotesDAO = new OrdersNotesDAO();

    $orderNotesDTO->setID_orders($ID_orders);
    $orderNotesDTO->setNotes("Orden Original No: " . $prev_id_order . "    - " . $order_notes);
    $orderNotesDTO->setType("Low");
    $orderNotesDTO->setID_admin_users($id_admin_users);

    if ($orderNotesDAO->insertRecord($orderNotesDTO)) {

        //-- Inserta los datos de los productos
        $orderProductsDTO = new OrdersProductsDTO();
        $orderProductsDAO = new OrdersProductsDAO();

        //-- Contador inicial para el ID de la parte
        //$ID_products_counter = 100000000;
        $ID_products_counter = 100;

        //- Order parts en Sesion
        $array_order_parts = $_SESSION['ARRAY_ORDER_PARTS'];

        //- Status del Product de la orden
        $order_product_status = "Active";
        $exito_inserted_products = false;

        foreach ($array_order_parts as $array_part_info) {
            $ID_part = $array_part_info['id_part'];
            $part_sku = $array_part_info['part_sku'];
            $part_model = $array_part_info['part_model'];
            $part_name = $array_part_info['part_name'];
            $part_cost = $array_part_info['part_cost'];
            $part_qty = $array_part_info['part_qty'];
            $part_price = $array_part_info['part_sprice'];
            $part_discount = $array_part_info['part_discount'];
            $part_shipping = $array_part_info['part_shipping'];
            $part_tax = $array_part_info['part_tax'];
            $part_total = $array_part_info['part_total'];

            $orderNet += $part_total;
            $orderQty += $part_qty;
            $orderDisc += $part_discount;
            $orderShip += $part_shipping;
            $orderTax += $part_tax;

            $orderTaxPerc += calculatePercentValue($part_tax);
            
            $related_ID_products = 400000000 + (int) $ID_part;

            $orderProductsDTO->setID_orders($ID_orders);
            $orderProductsDTO->setID_products($ID_products_counter . "000000");
            $orderProductsDTO->setRelated_ID_products($related_ID_products);
            $orderProductsDTO->setQuantity($part_qty);            
            $orderProductsDTO->setSalePrice($part_total);
            $orderProductsDTO->setShipping($part_shipping);
            $orderProductsDTO->setCost($part_cost);
            $orderProductsDTO->setTax($part_tax);
            $orderProductsDTO->setDiscount($part_discount);
            $orderProductsDTO->setPostedDate($postedDate);
            $orderProductsDTO->setStatus($order_product_status);
            $orderProductsDTO->setID_admin_users($id_admin_users);

            //-- Inserta los datos del producto en la orden
            if ($orderProductsDAO->insertRecord($orderProductsDTO)) {
                $exito_inserted_products = true;

            } else {
                $process_msg .= "- No se guardo la informacion del item no. " + $related_ID_products;
                $exito_inserted_products = false;
                break;
            }
        }

        //--- Procesa los datos para los items de intercambio
        if ($exito_inserted_products && $return_type == 'Exchange') {
            processProductsExchange($ID_orders, $array_order_parts, $ID_products_counter);
        }

        //-- Verifica que se hayan insertado correctamente todos los productos
        if ($exito_inserted_products) {

            $paymentAmount = 0;
            $taxPercent = (floatval($orderTaxPerc)/floatval(count($array_order_parts)));
            $paymentAmount = (floatval($orderNet - $orderDisc) * (1+ $taxPercent)) + $orderShip;
            //- Inserta la informacion de los pagos
            $orderPaymentsDTO = new OrdersPaymentsDTO();
            $orderPaymentsDAO = new OrdersPaymentsDAO();

            $orderPaymentsDTO->setID_orders($ID_orders);
            $orderPaymentsDTO->setType($payment_type);
            $orderPaymentsDTO->setPmtField1($payment_pmtField1);
            $orderPaymentsDTO->setPmtField2($payment_pmtField2);
            $orderPaymentsDTO->setPmtField3($payment_pmtField3);
            $orderPaymentsDTO->setPmtField4($payment_pmtField4);
            $orderPaymentsDTO->setPmtField5($payment_pmtField5);
            $orderPaymentsDTO->setPmtField6($payment_pmtField6);
            $orderPaymentsDTO->setPmtField7($payment_pmtField7);
            $orderPaymentsDTO->setPmtField8($payment_pmtField8);
            $orderPaymentsDTO->setPmtField9($payment_pmtField9);
            $orderPaymentsDTO->setAmount($paymentAmount);
            $orderPaymentsDTO->setReason($payment_reason);
            $orderPaymentsDTO->setPaymentDate($payment_date);
            $orderPaymentsDTO->setPostedDate($postedDate);
            $orderPaymentsDTO->setCaptured("Yes");
            $orderPaymentsDTO->setAuthCode("");
            $orderPaymentsDTO->setAuthDateTime("");
            $orderPaymentsDTO->setStatus($payment_status);
            $orderPaymentsDTO->setID_admin_users($id_admin_users);


            if ($orderPaymentsDAO->insertRecord($orderPaymentsDTO)) {
                //- Actualiza los totales de la orden
                $ordersDTO = new OrdersDTO();
                $ordersDTO->setID_orders($ID_orders);
                $ordersDTO->setOrderQty($orderQty);
                $ordersDTO->setOrderDisc($orderDisc);
                $ordersDTO->setOrderNet($orderNet);
                $ordersDTO->setOrderShp($orderShip);
                $ordersDTO->setOrderTax(floatval($orderTaxPerc)/floatval(count($array_order_parts)));
             
                if ($ordersDAO->updateOrderTotals($ordersDTO)) {
                    $exito = 1;
                    
                    auth_logging('opr_orders_added', $ID_orders, $id_admin_users, 'sl_orders', 'modtran');

                    unset($_SESSION['ARRAY_ORDER_PARTS']);
                } else {
                    $process_msg .= "- No se se actualizaron los totales de la orden";
                }
            } else {
                $process_msg .= "- No se guardo la informacion del pago de la orden";
            }
        }
    } else {
        $process_msg .= "- No se guardo la informacion de las notas la orden";
    }
} else {
    $process_msg .= "- No se guardo la informacion de la orden";
}



$status_process = array(
    "exito" => $exito,
    "id_order" => $ID_orders,
    "msg" => $process_msg
);

echo json_encode($status_process);
?>