<?php
/**
 * Description
 *
 * @author L.C.I Cesar Cedillo
 */
session_start();

include_once '../../trsBase.php';
include_once '../../session.php';

$COMMON_PATH = "../..";

unset($_SESSION['ARRAY_ORDER_PARTS']);

//-- parametros validos para la accion
/*
 * : chg_total  => Cambio total por lo que viene en la orden
 * : chg_fisico => Cambio por otra mercancia que el cliente elige
 *  
 */

//-- recepcion del parametro para el tipo de retorno
$return_type = isset($_GET['return']) ? $_GET['return'] : (isset($in['return']) ? $in['return'] : 'Returned for Refund');
$return_action = isset($_GET['action']) ? $_GET['action'] : (isset($in['action']) ? $in['action'] : 'chg_total');
$order_type = isset($_GET['type']) ?  $_GET['type'] : '';

$_SESSION['RETURN_ACTION'] = $return_action;
$_SESSION['ORDER_TYPE'] = $order_type;
?>
<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN">
<html>
    <head>
        <meta http-equiv="Content-Type" content="text/html; charset=UTF-8">
        <title></title>   
        <link href="<?php echo $COMMON_PATH ?>/common/css/main.css" rel="stylesheet" type="text/css" />
        <link href="<?php echo $COMMON_PATH ?>/common/css/common.css" rel="stylesheet" type="text/css" />
        <link href="<?php echo $COMMON_PATH ?>/common/js/jquery.msgbox.css" type="text/css" rel="stylesheet"/>
        <link href="<?php echo $COMMON_PATH ?>/common/js/css/smoothness/jquery-ui-1.8.17.custom.css" type="text/css" rel="stylesheet"/>        
        <link href="<?php echo $COMMON_PATH ?>/common/js/css/simplemodal.css" type="text/css" rel="stylesheet" media="screen" />
        <script type="text/javascript" src="<?php echo $COMMON_PATH ?>/common/js/jquery-1.6.4.min.js"></script>
        <script type="text/javascript" src="<?php echo $COMMON_PATH ?>/common/js/jquery-ui.min.js"></script>
        <script type="text/javascript" src="<?php echo $COMMON_PATH ?>/common/js/jquery.ui.datepicker-es.js"></script>
        <script type="text/javascript" src="<?php echo $COMMON_PATH ?>/common/js/jquery.msgbox.min.js"></script>
        <script type="text/javascript" src="<?php echo $COMMON_PATH ?>/common/js/validaciones.js"></script>
        <script type="text/javascript" src="<?php echo $COMMON_PATH ?>/common/js/jquery.simplemodal.1.4.3.min.js"></script>        

        <script type="text/javascript">
            var return_type = "<?php echo $return_type; ?>";
            var order_type = "<?php echo $order_type; ?>";
            
            function changeHeaderModName(){
                var module_name = "Ordenes de Venta";
                
                
                if(order_type=="cod"){
                    module_name += " > COD";
                }
                if(order_type=="tc"){
                    module_name += " > T.C";
                }
                                
                               
                var module_name = $("#spn-mod-name").html(module_name);
            }
            
            
            $(document).ready(function(){
                $("#popup-customers").hide();
                //$("#popup-customers").css({"top" : "30px" , "left" : "130px"});
                resetSearchPopUp('resCustomerSearch','customer-table-results');
                
                var id_popup1 = "popup-parts1";
                var id_popup2 = "popup-parts2";
                
                createPopUpItems(id_popup1, "Items de la Orden", "yes", "main-container","orders");
                //createPopUpItems(id_popup2, "Return Parts", "", "main-container","changes");
                createPopUpItems(id_popup2, "Items de Intercambio", "", "main-container","refunds");
                
                $("#popup-parts1").hide();
                $("#popup-parts2").hide();
                
                changeHeaderModName();
            });
            
            function resetSearchPopUp(idBtnReset,idTableResults){
                $("#"+ idBtnReset).click();
                $("#"+ idTableResults).html("");
            }
            
            function triggerPopupCustomers(){
                resetSearchPopUp('resCustomerSearch','customer-table-results');
                
                $("#popup-customers").modal({                    
                    position: ['40',]
                });
                
                $("#popup-customers").show();
            }
            
            function createPopUpItems(idPopup, popupTitle, isFirst, targetContainer,targetUsage){
                var ajax_url = "<?php echo $COMMON_PATH ?>" + "/common/php/popup/ajax/ajax_popup_parts_generator.php";;
                $.ajax({
                    type: 'POST',
                    url: ajax_url,
                    data: {
                        id_popup: idPopup,
                        popup_title : popupTitle,
                        first_popup : isFirst,
                        target_usage : targetUsage
                    },
                    success: function(data){                        
                        $("#" + targetContainer).append(data);
                        $("#" + idPopup).hide();
                    }
                });
            }
            
            function triggerPopupParts(idPopup, top, left, relatedPartID){
                resetSearchPopUp(idPopup);
                $("#"+idPopup).modal({                    
                    onShow: function(dialog){                        
                        $("#hdRelatedPartID-"+idPopup).val(relatedPartID);
                    },
                    position: [top ,]
                });
            }
            
            function resetSearchPopUp(idPopup){
                $("#frm-" + idPopup).click();
                $("#"+ idPopup + "-table-results").html("");
            }
            
                       
            $(function() {
                $("#txtPaymentDate").datepicker(
                {
                    dateFormat: "yy-mm-dd",
                    buttonImage: '<?php echo $COMMON_PATH; ?>/common/img/calendar.gif',                                       
                    buttonImageOnly: true,
                    showOn: 'button'
                }
            );

            });
            
        </script>
        <script type="text/javascript">
            /**************************************************************************/
            /* SCRIPTS Y FUNCIONES PARA LA MANIPULACION DE LAS PARTS*/
            /**************************************************************************/
        
            /*
            Function: ajaxSelectPart

            Selecciona una Part del listado de busqueda y la agrega a la tabla en pantalla.

            Parameters:

               targetUsage - Uso que se le dará en la pagina en caso de que se requiera mas de 1 listado en la misma pagina..
               idPart - Identificador de la parte.
               skuPart - SKU de la parte.
               partModel - Modelo de pa parte.
               partName - Nombre de la parte.
               partCost - Costo de la parte.
    
            Returns:

               Nothing.

            See Also:

               /common/php/popup/ajax/ajax_popup_parts_generator.php
             */
            
            var SIZE_PRODUCT_LIST = 0;
            var SIZE_EXCHANGE_LIST = 0;
            
            function ajaxSelectPart(targetUsage,idPart,skuPart,partModel,partName,partCost, relatedPartID){
                
                var ajax_url = "";
                var ajax_response_container = "";
                
                if(parseFloat(partCost) < 0){
                    partCost = 0.00;    //-- costo por default
                }
                
                
                
                if(targetUsage == 'orders'){                
                    //ajaxAddOrderPart(idPart,skuPart,partModel,partName,partCost);
                    ajax_url = "ajax/ajax_order_items_control.php";
                    ajax_response_container = "div-order-products";                    
                }else if(targetUsage == 'refunds'){
                    
                    ajax_url = "ajax/ajax_exchange_items_control.php";
                    ajax_response_container = "div-exchange-products";                    
                }
                
                $.ajax({
                    type: 'POST',
                    url: ajax_url,
                    data: {
                        pid: idPart,
                        psku : skuPart,
                        pmodel : partModel,
                        pname : partName,
                        pcost: partCost,
                        relpidx : relatedPartID,
                        action: 'add_part'
                    },
                    success: function(data){
                        if(targetUsage == 'orders'){
                            ajaxUpdateOrderTotals();
                        }else if(targetUsage == 'refunds'){
                            ajaxUpdateExchangeTotals();
                        }                        
                        $("#" + ajax_response_container).html(data);
                        
                    }
                });
            }
            
            
            /*
            function ajaxAddOrderPart(idPart,skuPart,partModel,partName,partCost){
                var ajax_url = "ajax/ajax_order_items_control.php";
                $.ajax({
                    type: 'POST',
                    url: ajax_url,
                    data: {
                        pid: idPart,
                        psku : skuPart,
                        pmodel : partModel,
                        pname : partName,
                        pcost: partCost,
                        action: 'add_part'
                    },
                    success: function(data){                        
                        $("#div-order-products").html(data);
                    }
                });
            }
             */
            
            function ajaxDeleteOrderPart(index){
                $.msgbox("Desea quitar el producto de la lista?", {
                    type: "confirm",
                    buttons : [
                        {type: "submit", value: "Yes"},                  
                        {type: "cancel", value: "Cancel"}
                    ]
                }, function(result) {
                    if(result == "Yes"){
                        var ajax_url = "ajax/ajax_order_items_control.php";
                        $.ajax({
                            type: 'POST',
                            url: ajax_url,
                            data: {
                                idx: index,
                                action: 'del_part'
                            },
                            success: function(data){
                                if(SIZE_EXCHANGE_LIST > 0){
                                    refreshExchangeList();
                                    ajaxUpdateExchangeTotals();
                                }
                                ajaxUpdateOrderTotals();
                                $("#div-order-products").html(data);
                            }
                        });
                    }
                });            
            }            
            
            
            function ajaxDeleteExchangePart(index, index_exchg){
                $.msgbox("Desea quitar el producto de la lista?", {
                    type: "confirm",
                    buttons : [
                        {type: "submit", value: "Yes"},                  
                        {type: "cancel", value: "Cancel"}
                    ]
                }, function(result) {
                    if(result == "Yes"){
                        var ajax_url = "ajax/ajax_exchange_items_control.php";
                        $.ajax({
                            type: 'POST',
                            url: ajax_url,
                            data: {
                                idx: index,
                                relpidx: index,
                                exchgidx: index_exchg,
                                action: 'del_part'
                            },
                            success: function(data){                                
                                ajaxUpdateExchangeTotals();
                                $("#div-exchange-products").html(data);
                            }
                        });
                    }
                });  
            }
            
            function ajaxUpdateProductInformation(idx){
                var ajax_url = "ajax/ajax_order_items_control.php";
                
                var product_qty = $("#txtOrdProductQty-"+idx).val();
                var product_sprice = $("#txtOrdProductSPrice-"+idx).val();
                var product_discount = $("#txtOrdProductDisc-"+idx).val();
                var product_shipping = $("#txtOrdProductShipping-"+idx).val();                
                var product_cost = $("#txtOrdProductCost-"+idx).val();
                var product_tax = $("#txtOrdProductTax-"+idx).val();
                var product_total = $("#txtOrdProductTotal-"+idx).val();
                var product_upc_status = $("#lstUpcStatus-"+idx).val();
                /*
                var product_pkg_condition = $("#lstProductPkgCondition-"+idx).val();
                var product_item_condition = $("#lstItemCondition-"+idx).val();
                 */
               
                $.ajax({
                    type: 'POST',
                    url: ajax_url,
                    data: {
                        idx: idx,
                        pqty: product_qty,
                        pcost : product_cost,                        
                        ptotal: product_total,
                        psprice : product_sprice,
                        pdiscount : product_discount,
                        pship : product_shipping,
                        ptax : product_tax,
                        /* ppckgcond : product_pkg_condition,
                        pitemcond : product_item_condition, */                  
                        pupcstatus : product_upc_status,
                        action: 'mod_part_info'
                    },
                    success: function(data){

                        ajaxUpdateOrderTotals();
                    }
                });
            }
            
           
            function ajaxUpdateOrderTotals(){                
                var ajax_url = "ajax/ajax_order_items_control.php";
                $.ajax({
                    type: 'POST',
                    url: ajax_url,
                    data: {                        
                        action: 'update_order_totals'
                    },
                    success: function(data){                        
                        if(data != ''){
                            var obJson = eval( "(" + data + ")" );
                            
                            $("#spnOrderItemsTotal").html(obJson ['total_items']);  
                            $("#spnOrderItemsTotalShip").html(obJson ['total_ship']);  
                            $("#spnOrderItemsTotalDisc").html(obJson ['total_disc']);  
                            $("#spnOrderItemsTotalTax").html(obJson ['total_tax']);  
                            $("#spnOrderTotal").html(obJson ['total_order']);  
                            
                            SIZE_PRODUCT_LIST = obJson ['total_product_list']
                            
                            $("#div-order-totals").css({'display':'block'});                            
                        }else{
                            $("#div-order-totals").css({'display':'none'});
                        }
                    }
                });
            }
            
         
            //-----------------------------------------------------------------//
            
            
            function validateOrderProductInformation(idx){
    
                var success= false;
                var error_msg = "";
                var txtOrdProductTotal = 0;
                
                var product_qty = $("#txtOrdProductQty-"+idx).val();
                var product_sprice = $("#txtOrdProductSPrice-"+idx).val();
                var product_discount = $("#txtOrdProductDisc-"+idx).val();
                var product_shipping = $("#txtOrdProductShipping-"+idx).val();                
                var product_cost = $("#txtOrdProductCost-"+idx).val();
                var product_tax = $("#txtOrdProductTax-"+idx).val();
                
                if(validar_flotante(product_qty)){
                    if(parseFloat(product_qty) <= 0){
                        error_msg += "- La cantidad debe ser mayor a 0.<br>";
                        product_qty = 1;
                        $("#txtOrdProductQty-" + idx).val(product_qty);
                        $("#txtOrdProductQty-" + idx).focus();
                    }
                }else{
                    error_msg += "- La cantidad debe ser un numero v&aacute;lido.<br>";
                    product_qty = 1;
                    $("#txtOrdProductQty-" + idx).val(product_qty);
                    $("#txtOrdProductQty-" + idx).focus();                    
                }

                if(validar_flotante(product_sprice)){
                    if(parseFloat(product_sprice) <= 0){
                        error_msg += "- El precio de venta debe ser mayor a 0.<br>";
                        product_sprice = 0.01;
                        $("#txtOrdProductSPrice-" + idx).val(product_sprice);
                        $("#txtOrdProductSPrice-" + idx).focus();
                    }
                }else{
                    error_msg += "- El precio de venta debe ser un n&uacute;mero v&aacute;lido.<br>";
                    product_sprice = 0.01;
                    $("#txtOrdProductSPrice-" + idx).val(product_sprice);
                    $("#txtOrdProductSPrice-" + idx).focus();                    
                }


                if(validar_flotante(product_discount)){
                    if(parseFloat(product_discount) < 0){
                        error_msg += "- El descuento debe ser mayor o igual a 0.<br>";
                        product_discount = 0.00;
                        $("#txtOrdProductDisc-" + idx).val(product_discount);
                        $("#txtOrdProductDisc-" + idx).focus();
                    }
                }else{
                    error_msg += "- El descuento debe ser un n&uacute;mero v&aacute;lido.<br>";
                    product_discount = 0.00;
                    $("#txtOrdProductDisc-" + idx).val(product_discount);
                    $("#txtOrdProductDisc-" + idx).focus();                    
                }

                if(validar_flotante(product_shipping)){
                    if(parseFloat(product_shipping) < 0){
                        error_msg += "- El costo del envio debe ser mayor o igual a 0.<br>";
                        $("#txtOrdProductShipping-" + idx).val("0.00");
                        $("#txtOrdProductShipping-" + idx).focus();
                    }
                }else{
                    error_msg += "- El costo del envio debe ser un n&uacute;mero v&aacute;lido.<br>";
                    $("#txtOrdProductShipping-" + idx).val("0.00");
                    $("#txtOrdProductShipping-" + idx).focus();                    
                }
        
                if(validar_flotante(product_cost)){
                    if(parseFloat(product_cost) < 0){
                        error_msg += "- El costo del item debe ser mayor o igual a 0.<br>";
                        $("#txtOrdProductCost-" + idx).val("0.00");
                        $("#txtOrdProductCost-" + idx).focus();
                    }
                }else{
                    error_msg += "- El costo del item debe ser un n&uacute;mero v&aacute;lido.<br>";
                    $("#txtOrdProductCost-" + idx).val("0.00");
                    $("#txtOrdProductCost-" + idx).focus();                   
                }
        
                if(validar_flotante(product_tax)){
                    if(parseFloat(product_tax) < 0){
                        error_msg += "- El tax del item debe ser mayor o igual a 0.<br>";
                        $("#txtOrdProductCost-" + idx).val("0.00");
                        $("#txtOrdProductCost-" + idx).focus();
                    }
                }else{
                    error_msg += "- El tax del item debe ser un n&uacute;mero v&aacute;lido.<br>";
                    $("#txtOrdProductTax-" + idx).val("0.00");
                    $("#txtOrdProductTax-" + idx).focus();                   
                }

                txtOrdProductTotal = calculateProductTotal(product_qty,product_sprice);
                $("#txtOrdProductTotal-" + idx).val(txtOrdProductTotal);

                if(error_msg == ""){
                    txtOrdProductTotal = calculateProductTotal(product_qty,product_sprice);
                    $("#txtOrdProductTotal-" + idx).val(txtOrdProductTotal);
                    ajaxUpdateProductInformation(idx);
                    success = true;
                }else{
                    $.msgbox("Se encontraron los siguientes errores:<br><br>" + error_msg, {                            
                        buttons : [
                            {type: "submit", value: "Ok"}
                        ]
                    },function(result) {
                        txtOrdProductTotal = calculateProductTotal(product_qty,product_sprice);
                        $("#txtOrdProductTotal-" + idx).val(txtOrdProductTotal);
                        ajaxUpdateProductInformation(idx);
                    });
                }
                return success;
            }
            
            
            function validateExchangeProductInformation(idx,idxex){
    
                var success= false;
                var error_msg = "";
                var txtOrdProductTotal = 0;
                
                var product_qty = $("#txtOrdProductQty-"+idx + "-" + idxex).val();
                var product_sprice = $("#txtOrdProductSPrice-"+idx + "-" + idxex).val();
                var product_discount = $("#txtOrdProductDisc-"+idx + "-" + idxex).val();
                var product_shipping = $("#txtOrdProductShipping-"+idx + "-" + idxex).val();                
                var product_cost = $("#txtOrdProductCost-"+idx + "-" + idxex).val();
                var product_tax = $("#txtOrdProductTax-"+idx + "-" + idxex).val();
                
                if(validar_flotante(product_qty)){
                    if(parseFloat(product_qty) <= 0){
                        error_msg += "- La cantidad debe ser mayor a 0.<br>";
                        product_qty = 1;
                        $("#txtOrdProductQty-" + idx + "-" + idxex).val(product_qty);
                        $("#txtOrdProductQty-" + idx + "-" + idxex).focus();
                    }
                }else{
                    error_msg += "- La cantidad debe ser un numero v&aacute;lido.<br>";
                    product_qty = 1;
                    $("#txtOrdProductQty-" + idx + "-" + idxex).val(product_qty);
                    $("#txtOrdProductQty-" + idx + "-" + idxex).focus();                    
                }

                if(validar_flotante(product_sprice)){
                    if(parseFloat(product_sprice) <= 0){
                        error_msg += "- El precio de venta debe ser mayor a 0.<br>";
                        product_sprice = 0.01;
                        $("#txtOrdProductSPrice-" + idx + "-" + idxex).val(product_sprice);
                        $("#txtOrdProductSPrice-" + idx + "-" + idxex).focus();
                    }
                }else{
                    error_msg += "- El precio de venta debe ser un n&uacute;mero v&aacute;lido.<br>";
                    product_sprice = 0.01;
                    $("#txtOrdProductSPrice-" + idx + "-" + idxex).val(product_sprice);
                    $("#txtOrdProductSPrice-" + idx + "-" + idxex).focus();                    
                }


                if(validar_flotante(product_discount)){
                    if(parseFloat(product_discount) < 0){
                        error_msg += "- El descuento debe ser mayor o igual a 0.<br>";
                        product_discount = 0.00;
                        $("#txtOrdProductDisc-" + idx + "-" + idxex).val(product_discount);
                        $("#txtOrdProductDisc-" + idx + "-" + idxex).focus();
                    }
                }else{
                    error_msg += "- El descuento debe ser un n&uacute;mero v&aacute;lido.<br>";
                    product_discount = 0.00;
                    $("#txtOrdProductDisc-" + idx + "-" + idxex).val(product_discount);
                    $("#txtOrdProductDisc-" + idx + "-" + idxex).focus();                    
                }

                if(validar_flotante(product_shipping)){
                    if(parseFloat(product_shipping) < 0){
                        error_msg += "- El costo del envio debe ser mayor o igual a 0.<br>";
                        $("#txtOrdProductShipping-" + idx + "-" + idxex).val("0.00");
                        $("#txtOrdProductShipping-" + idx + "-" + idxex).focus();
                    }
                }else{
                    error_msg += "- El costo del envio debe ser un n&uacute;mero v&aacute;lido.<br>";
                    $("#txtOrdProductShipping-" + idx + "-" + idxex).val("0.00");
                    $("#txtOrdProductShipping-" + idx + "-" + idxex).focus();                    
                }
        
                if(validar_flotante(product_cost)){
                    if(parseFloat(product_cost) < 0){
                        error_msg += "- El costo del item debe ser mayor o igual a 0.<br>";
                        $("#txtOrdProductCost-" + idx + "-" + idxex).val("0.00");
                        $("#txtOrdProductCost-" + idx + "-" + idxex).focus();
                    }
                }else{
                    error_msg += "- El costo del item debe ser un n&uacute;mero v&aacute;lido.<br>";
                    $("#txtOrdProductCost-" + idx + "-" + idxex).val("0.00");
                    $("#txtOrdProductCost-" + idx + "-" + idxex).focus();                   
                }
        
                if(validar_flotante(product_tax)){
                    if(parseFloat(product_tax) < 0){
                        error_msg += "- El tax del item debe ser mayor o igual a 0.<br>";
                        $("#txtOrdProductCost-" + idx + "-" + idxex).val("0.00");
                        $("#txtOrdProductCost-" + idx + "-" + idxex).focus();
                    }
                }else{
                    error_msg += "- El tax del item debe ser un n&uacute;mero v&aacute;lido.<br>";
                    $("#txtOrdProductTax-" + idx + "-" + idxex).val("0.00");
                    $("#txtOrdProductTax-" + idx + "-" + idxex).focus();                   
                }

                txtOrdProductTotal = calculateProductTotal(product_qty,product_sprice);
                $("#txtOrdProductTotal-" + idx + "-" + idxex).val(txtOrdProductTotal);

                if(error_msg == ""){
                    txtOrdProductTotal = calculateProductTotal(product_qty,product_sprice);
                    $("#txtOrdProductTotal-" + idx + "-" + idxex).val(txtOrdProductTotal);
                    ajaxUpdateProductExchangeInformation(idx,idxex);
                    success = true;
                }else{
                    $.msgbox("Se encontraron los siguientes errores:<br><br>" + error_msg, {                            
                        buttons : [
                            {type: "submit", value: "Ok"}
                        ]
                    },function(result) {
                        txtOrdProductTotal = calculateProductTotal(product_qty,product_sprice);
                        $("#txtOrdProductTotal-" + idx + "-" + idxex).val(txtOrdProductTotal);
                        ajaxUpdateProductExchangeInformation(idx,idxex);
                    });
                }
                return success;
            }
            
            
            
            function calculateProductTotal(qty,salePrice){
                var total = 0;
                total = parseFloat(qty) * parseFloat(salePrice);    
                return total;
            }            
        </script>
        <script type="text/javascript">
            // -- Funciones para manejar la ventana modal de los UPCS
            function closePopUp()
            {
                $.modal.close();                
            }
            
            
            function closeRefreshList(){
                $.modal.close();
                var ajax_url = "ajax/ajax_order_items_control.php";
                $.ajax({
                    type: 'POST',
                    url: ajax_url,
                    data: {                                
                        action: 'show_parts_list'
                    },
                    success: function(data){
                        //ajaxUpdateOrderTotals();
                        $("#div-order-products").html(data);
                    }
                });    
            }
            
            
            function refreshOrderList(){
                
            }
            
           
        </script>
        <script type="text/javascript">
            $(document).ready(function() {
                $("#frmCreateOrders").submit(function() {
                    $.ajax({
                        type: 'POST',
                        url: $(this).attr('action'),
                        data: $(this).serialize(),
                        // Mostramos un mensaje con la respuesta de PHP
                        success: function(data) {
                            if(data !=''){
                                var obJson = eval( "(" + data + ")" );
                                var exito = obJson ['exito'];
                                
                                if(exito == '1'){
                                    var id_order = obJson ['id_order'];
                                    
                                    $.msgbox("Se guardaron los datos para la orden de venta exitosamente.<br><br>- No. Orden: "+id_order, {
                                        type: "info",
                                        buttons : [
                                            {type: "submit", value: "Yes"}
                                        ]
                                    }, function(result) {                                                                        
                                        location.href="create_order.php?type=<?php echo $order_type?>";
                                    });
                                }else{
                                    $.msgbox("No se pudieron procesar los datos de la orden de venta.");
                                }
                            }else{
                                $.msgbox("Ocurrio un error al procesar los datos de la orden de venta.", {
                                    type: "error" });
                            }
                        }
                    })
                    return false;
                });
            });
            
            function validarDatosFormulario(){
                var errores="";
                var errores_msg ="";
                    
                with(document.frmCreateOrders){

                    if($("#txtCustomerID").val() =="" ){
                        errores += "- Debe seleccionar un Cliente.<br>";
                    }

                    if($("#txtPrevOrderID").val() =="" ){
                        errores += "- Debe introducir el numero de orden previo.<br>";
                    }

                    if($("#txtOrderNotes").val() =="" ){
                        errores += "- Debe introducir una nota para la orden.<br>";
                    }


                    if(SIZE_PRODUCT_LIST <= 0){
                        errores += "- Debe agregar por lo menos un item a la lista.<br>";
                    } /* else if($("#hdHasUpcs").val() ==""){
                        errores += "- Falta por completar el listado de UPCs de algunos items.<br>";
                    }
                     */
                    
                    if(return_type == "Exchange"){
                        if(SIZE_EXCHANGE_LIST <= 0){
                            errores += "- Debe existir por lo menos un item a la lista de productos para cambio fisico.<br>";
                        }
                    }
                }

                if(errores!='')
                {
                    errores_msg = "Verifique la siguiente informaci&oacute;n requerida:<br><br>"+errores;
                    $.msgbox(errores_msg, {
                        buttons : [
                            {type: "submit", value: "Aceptar"},
                        ]
                    });
                }
                else
                {
                    $.msgbox("Esta a punto de guardar la informacion del formulario, &iquest;Desea continuar?", {
                        type: "confirm",
                        buttons : [
                            {type: "submit", value: "Ok"},                  
                            {type: "cancel", value: "Cancelar"}
                        ]
                    }, function(result) {
                        if(result == "Ok"){
                            $("#subProcesar").click();
                        }
                    });                   
                }
            }
        </script>
        <script type="text/javascript">
            function validaFlotantes(value){
                var numero = 0.00;
                if(validar_flotante(value)){
                    numero = value;
                }
                return numero;
            }
        </script>
    </head>
    <body>
        <div id="contenedor">
            <?php include '../includes/header_bar.php'; ?>
            <div id="main-container" class="form-container" style="">
                <?php
                include_once $COMMON_PATH . '/common/php/popup/popup_customers.php';
                ?>
                <form id="frmCreateOrders" name="frmCreateOrders" action="process/order_procesar.php">
                    <input type='submit' id='subProcesar' style='display:none;'/>
                    <input type="hidden" name="hdReturnType" id="hdReturnType" style="visibility: hidden; display: none;" value="<?php echo $return_type ?>" />
                    <input type="hidden" name="hdReturnAction" id="hdReturnAction" style="visibility: hidden; display: none;" value="<?php echo $return_action ?>" />
                    <table width="100%">
                        <tr>
                            <td>
                                <fieldset class="field-set" style="min-width: 450px;">
                                    <legend>Informaci&oacute;n del Cliente</legend>
                                    <table>
                                        <tr>
                                            <td width="180px"><label>Cliente ID:</label></td>
                                            <td  colspan="3">
                                                <span>
                                                    <input type="text" name="txtCustomerID" id="txtCustomerID" value="" class="text-box" size="10" readonly />
                                                    &nbsp;&nbsp;<img src="<?php echo $COMMON_PATH ?>/common/img/icsearchsmall.gif" border="0" style="cursor: pointer;" onclick="triggerPopupCustomers()" />
                                                </span>
                                            </td>
                                        </tr>
                                        <tr>
                                            <td><label>Nombre: </label></td>
                                            <td  colspan="3"><input type="text" name="txtCustomerName" id="txtCustomerName" value="" class="text-box-disabled" size="50" readonly/></td>
                                        </tr>
                                        <tr>
                                            <td><label>Calle y No.:</label></td>
                                            <td  colspan="3"><input type="text" name="txtCustomerAddress1" id="txtCustomerAddress1" value="" class="text-box-disabled" size="80" readonly/></td>
                                        </tr>
                                        <tr>
                                            <td><label>Colonia:</label></td>
                                            <td  colspan="3"><input type="text" name="txtCustomerUrbanization" id="txtCustomerUrbanization" value="" class="text-box-disabled" size="80" readonly/></td>
                                        </tr>                                                                                
                                        <tr>
                                            <td><label>Entre Calles:</label></td>
                                            <td colspan="3"><input type="text" name="txtCustomerAddress2" id="txtCustomerAddress2" value="" class="text-box-disabled" size="80" readonly/></td>
                                        </tr>
                                        <tr>
                                            <td><label>Referencias:</label></td>
                                            <td colspan="3"><input type="text" name="txtCustomerAddress3" id="txtCustomerAddress3" value="" class="text-box-disabled" size="80" readonly/></td>
                                        </tr> 
                                        <tr>
                                            <td>
                                                <label>Pa&iacute;s:</label>                                                
                                            </td>
                                            <td>
                                                <input type="text" name="txtCustomerCountry" id="txtCustomerCountry" value="" size="30" class="text-box-disabled" readonly/>                                            
                                            </td>       
                                            <td><label>Estado:</label></td>
                                            <td>
                                                <input type="text" name="txtCustomerState" id="txtCustomerState" value="" class="text-box-disabled" readonly/>
                                            </td>
                                        </tr>
                                        <tr>
                                            <td><label>Municipio:</label></td>
                                            <td><input type="text" name="txtCustomerCity" id="txtCustomerCity" value="" size="30" class="text-box-disabled" readonly/></td>
                                            <td><label>C.P:</label></td>
                                            <td>
                                                <input type="text" name="txtCustomerZip" id="txtCustomerZip" value="" class="text-box-disabled" size="6" readonly/>
                                            </td>
                                        </tr>
                                        <tr>
                                            <td><label>Tel&eacute;fono:</label></td>
                                            <td><input type="text" name="txtCustomerPhone" id="txtCustomerPhone" value="" class="text-box-disabled" readonly/></td>
                                        </tr>

                                    </table>
                                </fieldset>
                            </td>
                        <tr>
                        <tr>
                            <td>                            
                                <fieldset class="field-set" style="min-width: 450px;">
                                    <legend>Informaci&oacute;n de la Orden</legend>
                                    <table>
                                        <tr>
                                            <td width="180px"><label>No. Orden Original:</label></td>
                                            <td>
                                                <input type="text" name="txtPrevOrderID" id="txtPrevOrderID" value="" class="text-box" size="10"/>
                                            </td>
                                        </tr>                                    
                                        <tr>
                                            <td><label>Notas: </label></td>
                                            <td><textarea name="txtOrderNotes" id="txtOrderNotes" class="text-box" cols="50" rows="2"></textarea></td>
                                        </tr>                                    
                                    </table>
                                </fieldset>
                            </td>
                        </tr>                    

                        <tr style="display: none;">
                            <td>                            
                                <fieldset class="field-set" style="min-width: 450px;">
                                    <legend>Informaci&oacute;n del Pago</legend>
                                    <table>
                                        <tr>
                                            <td width="180px"><label>Fecha de Pago:</label></td>
                                            <td>
                                                <input type="text" name="txtPaymentDate" id="txtPaymentDate"  class="text-box" size="10" readonly/>&nbsp;&nbsp;                                            
                                            </td>
                                        </tr>   

                                    </table>
                                </fieldset>
                            </td>
                        </tr>
                    </table>
                </form>
                <br>
                <center><input type="button" name="" value="Agregar Producto"  class="button" onclick="triggerPopupParts('popup-parts1',60,'')"/></center>
                <br>
                <table width="99%" align="center"  class="List">
                    <tr class="tableListTittle">
                        <td colspan="6" align="center">LISTA DE PRODUCTOS</td>
                    </tr>
                    <tr>
                        <td>
                            <div id="div-order-products" style="width: 100%"></div>
                        </td>
                    </tr>                   
                </table>

                <br>
                <div id ="div-order-totals" style="display: none;">
                    <table width="99%" align="center" class="List">
                        <tr class="tableListColumn">
                            <td colspan="5" align="center">Total de la Orden</td>
                        </tr>
                        <tr class="tableFila0">
                            <td align="center">Total de Items</td>
                            <td align="center">Total de Envio</td>
                            <td align="center">Total de Descuento</td>
                            <td align="center">Impuestos</td>
                            <td align="center">Importe Neto</td>                            
                        </tr>
                        <tr class="tableFila1">
                            <td align="center"><span id="spnOrderItemsTotal"></span></td>
                            <td align="center"><span id="spnOrderItemsTotalShip"></span><!-- <input class="text-box" type="text" name="txtOrderShip" id="txtOrderShip"  value="0.00" style="text-align: right;" onkeyup="this.value = validar_numerico_keyup(this.value)" onfocus="$(this).select()" onclick="$(this).select()" size="7" /> --></td>
                            <td align="center"><span id="spnOrderItemsTotalDisc"></span><!-- <input class="text-box" type="text" name="txtOrderDisc" id="txtOrderDisc"  value="0.00" style="text-align: right;" onkeyup="this.value = validar_numerico_keyup(this.value)" onfocus="$(this).select()" onclick="$(this).select()" size="7" /> --></td>
                            <td align="center"><span id="spnOrderItemsTotalTax"></span><!-- <input class="text-box" type="text" name="txtOrderTax" id="txtOrderTax"  value="0.00" style="text-align: right;" onkeyup="this.value = validar_numerico_keyup(this.value)" onfocus="$(this).select()" onclick="$(this).select()" size="7" /> --></td>
                            <td align="center">$&nbsp;<span id="spnOrderTotal"></span></td>                            
                        </tr>
                    </table>
                </div>
                <br>
                <?php
                if ($return_type == 'Exchange') {
                    include 'includes/div_exchange_products.php';
                }
                ?>
                <div style="text-align: center;">
                    <input type="button" name="" value="Guardar Informaci&oacute;n"  class="button" onclick="validarDatosFormulario()"/>
                </div>

            </div>
        </div>
    </body>
</html>