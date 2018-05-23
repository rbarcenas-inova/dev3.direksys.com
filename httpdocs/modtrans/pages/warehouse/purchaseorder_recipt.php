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

unset($_SESSION['ARRAY_PO_PARTS']);
unset($_SESSION['ARRAY_PO_PAYMENTS']);
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
            var return_type = "<?php echo $return_type ?>";

            function changeHeaderModName(){

                var module_name = "Recepcion de Mercancia";
                var module_name = $("#spn-mod-name").html(module_name);
            }


            $(document).ready(function(){
                $("#popup-pos").hide();


                changeHeaderModName();
            });

            function resetSearchPopUp(idBtnReset,idTableResults){
                $("#"+ idBtnReset).click();
                $("#"+ idTableResults).html("");
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

        </script>
        <script>
            /**************************************************************************/
            /* SCRIPTS Y FUNCIONES PARA LA MANIPULACION DEL PO*/
            /**************************************************************************/   
            
            
            function triggerPopupPOs(){
                resetSearchPopUp('resPOSearch','po-table-results');

                $("#popup-pos").modal({
                    position: ['40',]
                });

                $("#popup-pos").show();
            }
            
            function ajaxSelectPO(poID){
                var ajax_url = "ajax/ajax_select_po.php";
                $.ajax({
                    type: 'POST',
                    url: ajax_url,
                    data: {
                        poid: poID
                    },
                    success: function(data){
                        if(data != ''){
                            var obJson = eval( "(" + data + ")" );
                            var address = obJson ['vendorZip'] + " " + obJson ['vendorAddress'] + " " + obJson ['vendorCity'] + " " + obJson ['vendorState'] + " " + obJson ['vendorCountry'];
                            var vendorInfo = "(" + obJson ['vendorID'] + ")&nbsp;" + obJson ['vendorName'];
                            $("#txtPOID").val(obJson ['purchaseOrderID']);  
                            $("#spnVendorID").html(vendorInfo);
                            $("#spnPODate").html(obJson ['poDate']);
                            $("#spnPOTerms").html(obJson ['poTerms']);
                            $("#hdVendorID").val(obJson ['vendorID']);
                            $("#spnPOStatus").html(obJson ['status']);
                            
                            var htmlListItems = obJson ['htmlPOItems'];
                            htmlListItems = $.trim(htmlListItems);
                            
                            if(htmlListItems != ""){
                                $("#table-items").show();
                                $("#div-order-products").html(htmlListItems);
                            }else{
                                $("#table-items").hide();
                            }
                            
                            //--- refresca la lista de pagos
                            refreshPaymentList();

                            $("#close-button").click();                            
                        }
                    }
                });
            }    
        </script>
        <script type="text/javascript">
            // -- Funciones para manejar la ventana modal de los anticipos
            function closePopUp()
            {
                $.modal.close();
            }


            function closeRefreshList(){
                $.modal.close();
                refreshPaymentList();
            }

            function refreshPaymentList(){
                var ajax_url = "ajax/ajax_po_payments_control.php";
                $.ajax({
                    type: 'POST',
                    url: ajax_url,
                    data: {
                        action: 'show_payments_list'
                    },
                    success: function(data){                        
                        $("#table-payment-info").html(data);
                    }
                });
            }

            function loadPopupPOPayments(){
                var src = "includes/popup_po_payments.php";
                function setSrc(){
                    $('#iframeid').attr("src", src);
                }

                $.modal('<iframe src="" id="iframeid" width="560" style="height:225px;border:0" frameBorder="0">', {
                    opacity:80,
                    overlayCss: {backgroundColor:"#fff"},
                    closeHTML:"",
                    containerCss:{
                        backgroundColor:"#fff",
                        borderColor:"#fff",
                        height:"225px",
                        width:"560px",
                        padding:0
                    },
                    overlayClose:true,
                    onShow: function(dialog) {
                        setSrc();
                    }
                });
            }
        </script>
        <script type="text/javascript">
            function ajaxPOPayment(index){
                $.msgbox("Desea quitar la informacion del pago?", {
                    type: "confirm",
                    buttons : [
                        {type: "submit", value: "Si"},
                        {type: "cancel", value: "No"}
                    ]
                }, function(result) {
                    if(result == "Si"){
                        var ajax_url = "ajax/ajax_po_payments_control.php";
                        $.ajax({
                            type: 'POST',
                            url: ajax_url,
                            data: {
                                idx: index,
                                action: 'del_payment'
                            },
                            success: function(data){
                                $("#table-payment-info").html(data);
                            }
                        });
                    }
                });
            }
        </script>
        <script type="text/javascript">
            $(document).ready(function() {
                $("#frmRegistroWRecipt").submit(function() {
                    $.ajax({
                        type: 'POST',
                        url: $(this).attr('action'),
                        data: $(this).serialize(),
                        // Mostramos un mensaje con la respuesta de PHP
                        success: function(data) {
                            if(data !=''){
                                var obJson = eval( "(" + data + ")" );
                                var exito = obJson ['exito'];
                                var msg = obJson ['msg'];

                                if(exito == '1'){
                                    $.msgbox("Se guardo la informacion de los anticipos para la orden de compra exitosamente.<br>", {
                                        type: "info",
                                        buttons : [
                                            {type: "submit", value: "Aceptar"}
                                        ]
                                    }, function(result) {
                                        location.href="purchaseorder_recipt.php";
                                    });
                                }else{
                                    $.msgbox("No se pudieron procesar los datos de la devolucion. <br>" + msg);
                                }
                            }else{
                                $.msgbox("Ocurrio un error al procesar los datos de la devolucion.", {
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

                with(document.frmRegistroWRecipt){

                    if($("#txtPOID").val() =="" ){
                        errores += "- Debe seleccionar una orden de compra.<br>";
                    }
                    
                    var list_items =  $("#div-order-products").html();
                    list_items = $.trim(list_items);                    
                    if(list_items == ""){
                        errores += "- Debe seleccionar una orden de compra valida.<br>";
                    }
                    
                    var list_payments = $("#table-payment-info").html();
                    list_payments = $.trim(list_payments);                    
                    if(list_payments == ""){
                        errores += "- Debe agregar un anticipo o de lo contrario debe crear la orden de compras por Direksys.<br>";
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
            
            function updateRecievedQty(id_po_items,qty){
                var ajax_url = "ajax/ajax_po_operations.php";
                $.ajax({
                    type: 'POST',
                    url: ajax_url,
                    data: {
                        id_items: id_po_items,
                        qtty: qty,
                        action: 'update_qty'
                    },
                    success: function(data){
                        if(data == 1){
                            $("#sp-rcv-"+id_po_items).html(qty);
                            triggerEditQty(id_po_items);
                        }
                    }
                });            
            }
            
            function validateQty(id_po_items){
                var errores="";
                var qty = $("#hdqty-"+id_po_items).val();
                var rcvd = $("#txrcv-"+id_po_items).val();
                
                if(!validar_flotante(parseFloat(rcvd))){
                    errores+= "- La cantidad de recepcion no es valida."
                }else{
                    if(parseFloat(rcvd) > parseFloat(qty)){
                        errores+= "- La cantidad de recepcion no puede ser mayor a la cantidad solicitada."    
                    }
                }
            
                if(errores!=''){
                    var errores_msg = "Verifique la siguiente informaci&oacute;n:<br><br>"+errores;
                    $.msgbox(errores_msg, {
                        buttons : [
                            {type: "submit", value: "Aceptar"},
                        ]
                    });
                }
                else{
                    updateRecievedQty(id_po_items,rcvd);
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
            
            var editStatus = 0;                        
            function triggerEditQty(id_po_items){                
                if(editStatus==0){
                    $("#txrcv-"+id_po_items).css("display", "inline");
                    $("#img-cancelupdate-"+id_po_items).css("display", "inline");
                    $("#sp-rcv-"+id_po_items).css("display", "none");                
                    $("#img-edit-"+id_po_items).css("display", "none");                
                    editStatus = 1;
                }else if(editStatus==1){
                    $("#txrcv-"+id_po_items).css("display", "none");
                    $("#img-cancelupdate-"+id_po_items).css("display", "none");
                    $("#sp-rcv-"+id_po_items).css("display", "inline"); 
                    $("#img-edit-"+id_po_items).css("display", "inline"); 
                    editStatus = 0;
                }                
            }
            
            
        </script>
    </head>
    <body>
        <div id="contenedor">
            <?php include '../includes/header_bar.php'; ?>
            <div id="main-container" class="form-container" style="">
                <?php
                include_once $COMMON_PATH . '/common/php/popup/popup_po.php';
                ?>
                <form id="frmRegistroWRecipt" name="frmRegistroWRecipt" action="process/po_wrecipt_procesar.php">
                    <input type='submit' id='subProcesar' style='display:none;'/>
                    <input type="hidden" name="hdReturnType" id="hdReturnType" style="visibility: hidden; display: none;" value="<?php echo $return_type ?>" />
                    <input type="hidden" name="hdReturnAction" id="hdReturnAction" style="visibility: hidden; display: none;" value="<?php echo $return_action ?>" />
                    <table width="100%">
                        <tr>
                            <td>
                                <fieldset class="field-set" style="min-width: 450px;">
                                    <legend>Informaci&oacute;n de la Orden de Compra</legend>
                                    <table width="100%">
                                        <tr>
                                            <td width="180px"><label>Orden ID:</label></td>
                                            <td  colspan="3">
                                                <span>
                                                    <input type="text" name="txtPOID" id="txtPOID" value="" class="text-box" size="10" readonly />
                                                    &nbsp;&nbsp;<img src="<?php echo $COMMON_PATH ?>/common/img/icsearchsmall.gif" border="0" style="cursor: pointer;" onclick="triggerPopupPOs()" />
                                                </span>
                                            </td>
                                        </tr>
                                        <tr>
                                            <td width="180px"><label>Proveedor:</label></td>
                                            <td>
                                                <input type="hidden" name="hdVendorID" id="hdVendorID" value="" readonly />
                                                <span id="spnVendorID" style="display: block;width: 420px; font-size: 8pt; font-weight: bold;"></span>
                                            </td>
                                        </tr>
                                        <tr>
                                            <td><label>Fecha: </label></td>
                                            <td>
                                                <span id="spnPODate" style="display: block;width: 420px; font-size: 8pt; font-weight: normal;"></span>                                                
                                            </td>
                                        </tr>
                                        <tr>
                                            <td><label>Terminos: </label></td>
                                            <td>
                                                <span id="spnPOTerms" style="display: block;width: 420px; font-size: 8pt; font-weight: normal;"></span>
                                            </td>
                                        </tr>
                                        <tr>
                                            <td><label>Status: </label></td>
                                            <td>
                                                <span id="spnPOStatus" style="display: block;width: 420px; font-size: 8pt; font-weight: normal;"></span>
                                            </td>
                                        </tr>                                        
                                        <tr>
                                            <td colspan="2"><br></td>
                                        </tr>
                                        <tr>
                                            <td colspan="2">
                                                <div id="table-items" style="display: none;">
                                                    <table width="99%" align="center"  class="List">
                                                        <tr class="tableListTittle">
                                                            <td colspan="6" align="center">LISTA DE ITEMS</td>
                                                        </tr>
                                                        <tr>
                                                            <td>
                                                                <div id="div-order-products" style="width: 100%"></div>
                                                            </td>
                                                        </tr>
                                                    </table>                                                
                                                </div>
                                            </td>
                                        </tr>
                                    </table>
                                </fieldset>
                            </td>
                        </tr>

                        <tr>
                            <td>
                                <fieldset class="field-set" style="min-width: 450px;">
                                    <legend>Informaci&oacute;n de los Pagos</legend>
                                    <table style="width: 100%;">
                                        <tr>
                                            <td align="center" >
                                                <label><span style="cursor: pointer; text-decoration: underline;" onclick="loadPopupPOPayments();">Agregar Informaci&oacute;n de Pago / Anticipo</span></label>
                                                <br>
                                            </td>
                                        </tr>
                                        <tr>
                                            <td>                                                
                                                <div id="table-payment-info"></div>
                                            </td>
                                        </tr>
                                    </table>
                                </fieldset>
                            </td>
                        </tr>                        
                    </table>
                </form>
                <br>
                <div style="text-align: center;">
                    <input type="button" name="" value="Guardar Informaci&oacute;n"  class="button" onclick="validarDatosFormulario()"/>
                </div>
                <br>
            </div>
        </div>
    </body>
</html>