.<?php
session_start();

$COMMON_PATH = "../..";

include_once $COMMON_PATH . '/trsBase.php';
include_once $COMMON_PATH . '/session.php';

include_once 'includes/cfdi_load_data.php';
global $vector_invoices;
global $vector_invoices_lines;
global $vector_invoices_notes;
global $list_orders_invoice;
global $list_creditmemo_invoice;
$e=$in['e'];
if(!empty($list_orders_invoice)){$NumDoc=$list_orders_invoice; $txtNumDoc='N&uacute;mero de Pedido:';
}else{$NumDoc=$list_creditmemo_invoice; $txtNumDoc='No. Credit Memo:';}
//global $vector_orders_invoice;
$page = isset($_POST['pagenum']) ? $_POST['pagenum'] : (isset($_GET['pagenum']) ? $_GET['pagenum'] : 1);

$invoicesDTO = new InvoicesDTO();
$invoicesLinesDTO = new InvoicesLinesDTO();

$arr_taxes = array(); //-- array asociativo:  tax_name=> nombre del tax | tax_rate=> tasa del tax | sum_taxes=> suma de los taxes

if (empty($vector_invoices)) {
    header('Location: /finkok');
}

//-- recupera los datos generales del invoice
$invoicesDTO = $vector_invoices[0];
//-- Detecta el tipo de moneda
switch(strtoupper($invoicesDTO->getCurrency())){
  case 'MXP': $Moneda='Pesos'; $Sigla=' M.N.'; $Signo='$'; break;
  case 'USD': $Moneda='Dolares'; $Sigla=' US Cy'; $Signo='US$';break;
  default: $Moneda='Pesos'; $Sigla=' M.N.'; $Signo='$';
}
?>
<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN">
<html>
    <head>
        <meta http-equiv="Content-Type" content="text/html; charset=ISO-8859-1">
        <title></title>
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

        <!--<script src="<?php echo $COMMON_PATH ?>/common/js/msgBox/Scripts/jquery-1.4.1.js" type="text/javascript"></script>-->
        <script src="<?php echo $COMMON_PATH ?>/common/js/msgBox/Scripts/jquery.msgBox.js" type="text/javascript"></script>
        <link href="<?php echo $COMMON_PATH ?>/common/js/msgBox/Styles/msgBoxLight.css" rel="stylesheet" type="text/css">

  <link rel="stylesheet" type="text/css" href="/sitimages/app_bar/mod/Xtyle<?php echo $in{'e'}; ?>.css" />
  <link rel="stylesheet" type="text/css" href="/sitimages/default/main.css" />

        <script type="text/javascript">
            $(document).ready(function() {
                
                refreshNotesList();
                
                $("#frmEditInvoice").submit(function() {
                    $.ajax({
                        type: 'POST',
                        url: $(this).attr('action'),
                        data: $(this).serialize(),
                        // Mostramos un mensaje con la respuesta de PHP
                        success: function(data) {
                            if(data !=''){
                                var exito = data;
                                if(exito == '1'){
                                                                        
                                    $.msgbox("Se modificaron los datos para la factura exitosamente.<br>", {
                                        type: "info",
                                        buttons : [
                                            {type: "submit", value: "Yes"}
                                        ]
                                    }, function(result) {                                                                        
                                        confirmInvoice();
                                        //location.href="/finkok";
                                    });
                                }else{
                                    $.msgbox("No se pudieron modificar los datos de la factura.");
                                }
                            }else{
                                $.msgbox("Ocurrio un error al procesar los datos de la devolucion.", {
                                    type: "error" });
                            }
                        }
                    })
                    return false;
                });
                
                $("#txtOrderAlias").val('<?php echo $invoicesDTO->getID_orders_alias(); ?>');

                /* Fecha txtOrderAliasDate, txtExchangeReceiptDate */
                //var t = new Date();
                //var today = t.getFullYear() + '-' + (t.getMonth()+1) + '-' + t.getDate();
                //$("#txtOrderAliasDate").val(today)
                var dates = $( "#txtOrderAliasDate, #txtExchangeReceiptDate" ).datepicker({
                    dateFormat: 'yy-mm-dd',
                    setDate: new Date(),
                    defaultDate: new Date(),
                    changeMonth: true,
                    numberOfMonths: 3
                });
                /* Fin Fecha */
                
            });
            


                function copyExpediterFiscalAddress(){
                    
                    $("#txtExpediterAddressStreet").val($("#txtExpediterFAddressStreet").val());
                    $("#txtExpediterAddressNum").val($("#txtExpediterFAddressNum").val());
                    $("#txtExpediterAddressNum2").val($("#txtExpediterFAddressNum2").val());
                    $("#txtExpediterAddressUrbanization").val($("#txtExpediterFAddressUrbanization").val());
                    $("#txtExpediterAddressUrbanization").val($("#txtExpediterFAddressUrbanization").val());
                    $("#txtExpediterAddressDistrict").val($("#txtExpediterFAddressDistrict").val());
                    $("#txtExpediterAddressZipcode").val($("#txtExpediterFAddressZipcode").val());
                    $("#txtExpediterAddressState").val($("#txtExpediterFAddressState").val());
                    $("#txtExpediterAddressCity").val($("#txtExpediterFAddressCity").val());
                    $("#txtExpediterAddressCountry").val($("#txtExpediterFAddressCountry").val());
                }
                
                function copyCustomerFiscalAddress(){
                    $("#txtCustomerShpAddressStreet").val($("#txtCustomerAddressStreet").val());
                    $("#txtCustomerShpAddressNum").val($("#txtCustomerAddressNum").val());
                    $("#txtCustomerShpAddressNum2").val($("#txtCustomerAddressNum2").val());
                    $("#txtCustomerShpAddressUrbanization").val($("#txtCustomerAddressUrbanization").val());
                    $("#txtCustomerShpAddressDistrict").val($("#txtCustomerAddressDistrict").val());
                    $("#txtCustomerShpAddressZipcode").val($("#txtCustomerAddressZipcode").val());
                    $("#txtCustomerShpAddressState").val($("#txtCustomerAddressState").val());
                    $("#txtCustomerShpAddressCity").val($("#txtCustomerAddressCity").val());
                    $("#txtCustomerShpAddressCountry").val($("#txtCustomerAddressCountry").val());
                }

            //--------------------------------------------------------------
            function validarDatosFormulario(validation_type){
                var errores="";
                var errores_msg ="";
                
                <?php if($e!=2){?>
                if($.trim($("#txtOrderAlias").val()) != "" && ($.trim($("#txtOrderAliasDate").val())=="" || $.trim($("#txtOrderAliasDate").val())=="0000-00-00") ){
                     errores += "- Ingrese la fecha del Pedido del cliente.<br>";
                }

                if(($.trim($("#txtOrderAliasDate").val())!="" && $.trim($("#txtOrderAliasDate").val())!="0000-00-00") && $.trim($("#txtOrderAlias").val()) == "" ){
                     errores += "- Ingrese el No. de Pedido del cliente.<br>";
                }

                if($.trim($("#txtExchangeReceipt").val()) != "" && ($.trim($("#txtExchangeReceiptDate").val())=="" || $.trim($("#txtExchangeReceiptDate").val())=="0000-00-00") ){
                     errores += "- Ingrese la fecha del No. de Contrarecibo.<br>";
                }

                if(($.trim($("#txtExchangeReceiptDate").val())!="" && $.trim($("#txtExchangeReceiptDate").val())!="0000-00-00") && $.trim($("#txtExchangeReceipt").val()) == "" ){
                     errores += "- Ingrese el No. Contrarecibo.<br>";
                }
                <?php } ?>
                if($.trim($("#txtExpediterFCode").val()) == ""){
                     errores += "- El RFC del Emisor no debe ir vacio.<br>";
                }
                
                if($.trim($("#txtExpediterFName").val()) == ""){
                     errores += "- La Razon Social del Emisor no debe ir vacia.<br>";
                }                

                if($.trim($("#txtExpediterFRegimen").val()) == ""){
                     errores += "- El Regimen Fiscal del Emisor no debeir vacio.<br>";
                }

                if($.trim($("#txtExpediterFAddressStreet").val()) == ""){
                     errores += "- La calle de la direccion fiscal del Emisor no debe ir vacia.<br>";
                }

                if($.trim($("#txtExpediterFAddressNum").val()) == ""){
                     errores += "- El numero exterior de la direccion fiscal del Emisor no debe ir vacia.<br>";
                }

                if($.trim($("#txtExpediterFAddressUrbanization").val()) == ""){
                     errores += "- La Colonia de la direccion fiscal del Emisor no debe ir vacia.<br>";
                }

                if($.trim($("#txtExpediterFAddressZipcode").val()) == ""){
                     errores += "- El Codigo Postal de la direccion fiscal del Emisor no debe ir vacia.<br>";
                }

                if($.trim($("#txtExpediterFAddressState").val()) == ""){
                     errores += "- El Estado de la direccion fiscal del Emisor no debe ir vacia.<br>";
                }

                if($.trim($("#txtExpediterFAddressCity").val()) == ""){
                     errores += "- La Delegacion o Municipio de la direccion fiscal del Emisor no debe ir vacia.<br>";
                }

                if($.trim($("#txtExpediterFAddressCountry").val()) == ""){
                     errores += "- El Pais de la direccion fiscal del Emisor no debe ir vacia.<br>";
                }
                
                if($.trim($("#txtExpediterAddressStreet").val()) == ""){
                     errores += "- La calle de la direccion del Emisor no debe ir vacia.<br>";
                }

                if($.trim($("#txtExpediterAddressNum").val()) == ""){
                     errores += "- El numero exterior de la direccion del Emisor no debe ir vacia.<br>";
                }

                if($.trim($("#txtExpediterAddressUrbanization").val()) == ""){
                     errores += "- La Colonia de la direccion del Emisor no debe ir vacia.<br>";
                }

                if($.trim($("#txtExpediterAddressZipcode").val()) == ""){
                     errores += "- El Codigo Postal de la direccion del Emisor no debe ir vacia.<br>";
                }

                if($.trim($("#txtExpediterAddressState").val()) == ""){
                     errores += "- El Estado de la direccion del Emisor no debe ir vacia.<br>";
                }

                if($.trim($("#txtExpediterAddressCity").val()) == ""){
                     errores += "- La Delegacion o Municipio de la direccion del Emisor no debe ir vacia.<br>";
                }

                if($.trim($("#txtExpediterAddressCountry").val()) == ""){
                     errores += "- El Pais de la direccion del Emisor no debe ir vacia.<br>";
                }                
                //----
                if($.trim($("#txtCustomerFCode").val()) == ""){
                     errores += "- El RFC del Receptor no debe ir vacio.<br>";
                }
                
                if($.trim($("#txtCustomerFName").val()) == ""){
                     errores += "- La Razon Social del Receptor no debe ir vacia.<br>";
                }                

                if($.trim($("#txtCustomerAddressStreet").val()) == ""){
                     errores += "- La calle de la direccion fiscal del Receptor no debe ir vacia.<br>";
                }

                if($.trim($("#txtCustomerAddressNum").val()) == ""){
                     errores += "- El numero exterior de la direccion fiscal del Receptor no debe ir vacia.<br>";
                }

                if($.trim($("#txtCustomerAddressUrbanization").val()) == ""){
                     errores += "- La Colonia de la direccion fiscal del Receptor no debe ir vacia.<br>";
                }

                if($.trim($("#txtCustomerAddressZipcode").val()) == ""){
                     errores += "- El Codigo Postal de la direccion fiscal del Receptor no debe ir vacia.<br>";
                }

                if($.trim($("#txtCustomerAddressState").val()) == ""){
                     errores += "- El Estado de la direccion fiscal del Receptor no debe ir vacia.<br>";
                }

                if($.trim($("#txtCustomerAddressCity").val()) == ""){
                     errores += "- La Delegacion o Municipio de la direccion fiscal del Receptor no debe ir vacia.<br>";
                }

                if($.trim($("#txtCustomerAddressCountry").val()) == ""){
                     errores += "- El Pais de la direccion fiscal del Receptor no debe ir vacia.<br>";
                }                
              

                if($.trim($("#txtCustomerShpAddressStreet").val()) == ""){
                     errores += "- La calle de la direccion de entrega del Receptor no debe ir vacia.<br>";
                }
                <?php if($e!=2){?>
                if($.trim($("#txtCustomerShpAddressNum").val()) == ""){
                     errores += "- El numero exterior de la direccion de entrega del Receptor no debe ir vacia.<br>";
                }
                <?php } ?>
                if($.trim($("#txtCustomerShpAddressUrbanization").val()) == ""){
                     errores += "- La Colonia de la direccion de entrega del Receptor no debe ir vacia.<br>";
                }

                if($.trim($("#txtCustomerShpAddressZipcode").val()) == ""){
                     errores += "- El Codigo Postal de la direccion de entrega del Receptor no debe ir vacia.<br>";
                }

                if($.trim($("#txtCustomerShpAddressState").val()) == ""){
                     errores += "- El Estado de la direccion de entrega del Receptor no debe ir vacia.<br>";
                }

                if($.trim($("#txtCustomerShpAddressCity").val()) == ""){
                     errores += "- La Delegacion o Municipio de la direccion de entrega del Receptor no debe ir vacia.<br>";
                }

                if($.trim($("#txtCustomerShpAddressCountry").val()) == ""){
                     errores += "- El Pais de la direccion de entrega del Receptor no debe ir vacia.<br>";
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
                else {
                    if(validation_type=='form'){
                    $.msgbox("Esta a punto de modificar la informacion de la factura, &iquest;Desea continuar?", {
                        type: "confirm",
                        buttons : [
                            {type: "submit", value: "Ok"},                  
                            {type: "cancel", value: "Cancelar"}
                        ]
                    }, function(result) {
                        if(result == "Ok"){
                            $("#subSend").click();
                        }
                    });                   
                    } else if(validation_type=='confirm'){
                        confirmInvoice();
                    }
                }
            }    
            
            //-- Guardar los datos de las notas
            function saveInvoiceNotes(){
                $.msgbox("Desea guardar las notas para la factura?", {
                    type: "confirm",
                    buttons : [
                        {type: "submit", value: "Si"},                  
                        {type: "cancel", value: "Cancelar"}
                    ]
                }, function(result) {
                    if(result == "Si"){
                        //-- ajax para modificar el status
                        var ajax_url = 'process/cfdi_edit_save.php';
                
                        $.ajax({
                            type: 'POST',
                            url: ajax_url,
                            data: {
                                hdIdInvoice : <?php echo $invoicesDTO->getID_invoices(); ?>,                                
                                action : 'save_notes'
                            },
                            success: function(data){                          
                                if(data !=''){
                                    var exito = data;
                                    if(exito == '1'){
                                                                        
                                        $.msgbox("Se guardaron las notas para la factura exitosamente.<br>", {
                                            type: "info",
                                            buttons : [
                                                {type: "submit", value: "Ok"}
                                            ]
                                        }, function(result) {                                                                        
                                            location.href="/finkok";
                                            //opener.location.reload();
                                            //window.close();
                                        });
                                    }else{
                                        $.msgbox("No se agrego ninguna nota para la factura.");
                                    }
                                }else{
                                    $.msgbox("Error al procesar la peticion.", {
                                        type: "error" });
                                }                                
                            }
                        });
                    }
                });               
            }
            
            
            //-- cambio de status de los invoices
            function updateInvoiceStatus(id_invoices,status, msg){
                $.msgbox(msg, {
                    type: "confirm",
                    buttons : [
                        {type: "submit", value: "Si"},                  
                        {type: "cancel", value: "Cancelar"}
                    ]
                }, function(result) {
                    if(result == "Si"){
                        //-- ajax para modificar el status
                        var ajax_url = 'process/cfdi_edit_save.php';
                
                        $.ajax({
                            type: 'POST',
                            url: ajax_url,
                            data: {
                                hdIdInvoice : id_invoices,
                                status: status,
                                action : 'update_status'
                            },
                            success: function(data){                          
                                if(data !=''){
                                    var exito = data;
                                    if(exito == '1'){
                                                                        
                                        $.msgbox("Se actualizo el status de la factura exitosamente.<br>", {
                                            type: "info",
                                            buttons : [
                                                {type: "submit", value: "Ok"}
                                            ]
                                        }, function(result) {                                                                        
                                            location.href="/finkok";
                                            //opener.location.reload();
                                            //window.close();
                                        });
                                    } else if(exito == '-1'){
                                        $.msgbox("No se actualizo el status de la factura debido a que ya se encuentra en proceso de certificacion o bien, ya se encuentra cancelada.");
                                    } else{
                                        $.msgbox("Error al actualizar el status de la factura.");
                                    }
                                }else{
                                    $.msgbox("Error al procesar la peticion.", {
                                        type: "error" });
                                }                                
                            }
                        });
                    }
                });               
            }
            
            function voidInvoice(){
                var msg="Esta a punto de anular la factura y ya no se podra timbrar, &iquest;Desea continuar?";
                var status="Void";
                var id_invoice = <?php echo $invoicesDTO->getID_invoices(); ?>;
                
                updateInvoiceStatus(id_invoice, status, msg);
            }
            
            function reactivateInvoice(){
                var msg="Esta a punto de reactivar la factura, se podra modificar y tambien se podra timbrar, &iquest;Desea continuar?";
                var status="New";
                var id_invoice = <?php echo $invoicesDTO->getID_invoices(); ?>;
                updateInvoiceStatus(id_invoice, status, msg);
            }
            
            function confirmInvoice(){
                var msg="&iquest;Desea confirmar los datos de la factura para enviarlos a timbrar?";
                var status="<?=$in['e'] == 11 ? 'Confirmed' : 'New' ?>";
                var id_invoice = <?php echo $invoicesDTO->getID_invoices(); ?>;
                updateInvoiceStatus(id_invoice, status, msg);
            }
            
            function cancelCertificationProcess(){
                var msg="&iquest;Desea quitar la factura para el proceso de timbrado?. Esta factura se podra timbrar posteriormente mediante la confirmacion.";
                var status="New";
                var id_invoice = <?php echo $invoicesDTO->getID_invoices(); ?>;
                updateInvoiceStatus(id_invoice, status, msg);
            }

            function cancelInvoice(){
                var msg="&iquest;Desea Cancelar este documento?. Recuerde que tambi&eacuten deber&aacute realizar la cancelaci&oacuten ante el SAT (PAC).";
                var status="Cancelled";
                var id_invoice = <?php echo $invoicesDTO->getID_invoices(); ?>;
                updateInvoiceStatus(id_invoice, status, msg);
            }


            function duplicateInvoice(){
                var msg="&iquest;Desea duplicar los datos de la factura?. Esta factura se podra timbrar posteriormente mediante la confirmacion.";
                
                var id_invoices = <?php echo $invoicesDTO->getID_invoices(); ?>;
                
                $.msgbox(msg, {
                    type: "confirm",
                    buttons : [
                        {type: "submit", value: "Si"},                  
                        {type: "cancel", value: "Cancelar"}
                    ]
                }, function(result) {
                    if(result == "Si"){
                        //-- ajax para modificar el status
                        var ajax_url = 'process/cfdi_edit_save.php';
                
                        $.ajax({
                            type: 'POST',
                            url: ajax_url,
                            data: {
                                hdIdInvoice : id_invoices,                                
                                action : 'duplicate_invoice'
                            },
                            success: function(data){                          
                                if(data !=''){
                                    var obJson = eval( "(" + data + ")" );
                                    
                                    var exito = obJson ['exito'];
                                    if(exito == '1'){
                                        var id_new_invoice = obJson ['id_new_invoices'];
                                        $.msgbox("Se duplico la informacion de la factura exitosamente.<br>El nuevo ID de la factura es: " + id_new_invoice, {
                                            type: "info",
                                            buttons : [
                                                {type: "submit", value: "Ok"}
                                            ]
                                        }, function(result) {                                                                        
                                            location.href="/finkok";
                                            //opener.location.reload();
                                            //window.close();
                                        });
                                    } else{
                                        $.msgbox("Error al duplicar la informacion de la factura.");
                                    }
                                }else{
                                    $.msgbox("Error al procesar la peticion.", {
                                        type: "error" });
                                }                                
                            }
                        });
                    }
                });               
            }

            function creditNote(){
                var msg="&iquest;Desea crear una Nota de Credito con el importe total de esta factura?. Esta factura se cancelara y la nueva Nota de Credito se podra timbrar posteriormente mediante la confirmacion.";
                
                var id_invoices = <?php echo $invoicesDTO->getID_invoices(); ?>;
                
                $.msgbox(msg, {
                    type: "confirm",
                    buttons : [
                        {type: "submit", value: "Si"},                  
                        {type: "cancel", value: "Cancelar"}
                    ]
                }, function(result) {
                    if(result == "Si"){
                        //-- ajax para modificar el status
                        var ajax_url = 'process/cfdi_edit_save.php';
                
                        $.ajax({
                            type: 'POST',
                            url: ajax_url,
                            data: {
                                hdIdInvoice : id_invoices,                                
                                action : 'credit_note'
                            },
                            success: function(data){                          
                                if(data !=''){
                                    var obJson = eval( "(" + data + ")" );
                                    
                                    var exito = obJson ['exito'];
                                    if(exito == '1'){
                                        var id_new_invoice = obJson ['id_new_invoices'];
                                        $.msgbox("Se creo exitosamente una Nota de Credito con el importe total de esta factura.<br>El ID de la Nota de Credito es: " + id_new_invoice, {
                                            type: "info",
                                            buttons : [
                                                {type: "submit", value: "Ok"}
                                            ]
                                        }, function(result) {                                                                        
                                            location.href="/finkok";
                                            //opener.location.reload();
                                            //window.close();
                                        });
                                    } else{
                                        $.msgbox("Error al crear nota de credito.");
                                    }
                                }else{
                                    $.msgbox("Error al procesar la peticion.", {
                                        type: "error" });
                                }                                
                            }
                        });
                    }
                });               
            }

        </script>
        <script type="text/javascript">
            // -- Funciones para manejar la ventana modal de las notas
            function closePopUp()
            {
                $.modal.close();
            }


            function closeRefreshNotesList(){
                $.modal.close();
                refreshNotesList();
            }

            function refreshNotesList(){
                var ajax_url = "ajax/ajax_cfdi_notes_control.php";
                $.ajax({
                    type: 'POST',
                    url: ajax_url,
                    data: {
                        id_invoices : <?php echo $invoicesDTO->getID_invoices() ?>,
                        action: 'show_notes_list'
                    },
                    success: function(data){                        
                        $("#invoice-notes-list").html(data);
                    }
                });
            }

            function loadPopupNotes(id_invoices, note_type){
                
                var src = "includes/popup_add_notes.php?id_invoices="+id_invoices+"&note_type="+note_type;
                function setSrc(){
                    $('#iframeid').attr("src", src);
                }

                $.modal('<iframe src="" id="iframeid" width="540" height="220" style="border:0" frameBorder="0">', {
                    opacity:80,
                    overlayCss: {backgroundColor:"#fff"},
                    closeHTML:"",
                    containerCss:{
                        backgroundColor:"#fff",
                        borderColor:"#fff",
                        height:230,
                        width:560,
                        padding:0
                    },
                    overlayClose:true,
                    onShow: function(dialog) {
                        setSrc();
                    }
                });
            }
            
            function deleteNote(index){
                $.msgbox("Desea quitar la nota seleccionada lista?", {
                    type: "confirm",
                    buttons : [
                        {type: "submit", value: "Si"},                  
                        {type: "cancel", value: "No"}
                    ]
                }, function(result) {
                    if(result == "Si"){
                        var ajax_url = "ajax/ajax_cfdi_notes_control.php";
                        $.ajax({
                            type: 'POST',
                            url: ajax_url,
                            data: {
                                idx: index,
                                action: 'del_note'
                            },
                            success: function(data){
                                refreshNotesList();
                            }
                        });
                    }
                });            
            }
            
            
            function loadPopupCustoms(id_invoices_lines, description, id_invoice){                
                var src = "includes/popup_add_customs.php?id_invoices_lines="+id_invoices_lines+"&description="+description+"&id_invoice="+id_invoice;
                function setSrc(){
                    $('#iframeid').attr("src", src);
                }

                $.modal('<iframe src="" id="iframeid" width="540" height="220" style="border:0" frameBorder="0">', {
                    opacity:80,
                    overlayCss: {backgroundColor:"#fff"},
                    closeHTML:"",
                    containerCss:{
                        backgroundColor:"#fff",
                        borderColor:"#fff",
                        height:230,
                        width:560,
                        padding:0
                    },
                    overlayClose:true,
                    onShow: function(dialog) {
                        setSrc();
                    }
                });
            }

            //Crea Nota de credito y duplica factura - TMK
            function otherInvoice(){
                $.msgBox({
                    title: "Pregunta",
                    content: "Esta acci&oacuten crear&aacute una Nota de Cr&eacutedito con el total de &eacutesta factura, adem&aacutes se crear&aacute un registro con estatus 'OnEdition'. \nDesea continuar?",
                    type: "confirm",
                    opacity: 0.5,
                    buttons: [{ value: "Si" }, { value: "No" }]
                    ,success: function (result) {
                        if(result == "Si"){
                            //Nota de credito
                            var id_invoices = <?php echo $invoicesDTO->getID_invoices(); ?>;
                            var ajax_url = 'process/cfdi_edit_save.php';                
                            $.ajax({
                                type: 'POST',
                                url: ajax_url,
                                data: {
                                    hdIdInvoice : id_invoices,                                
                                    action : 'credit_note'
                                },
                                success: function(data){                          
                                    if(data !=''){
                                        var obJson = eval( "(" + data + ")" );                                        
                                        var exito = obJson ['exito'];
                                        if(exito == '1'){
                                            var id_nc_invoice = obJson ['id_new_invoices'];
                                            //Duplicar registro 'onEdition'
                                            $.ajax({
                                                type: 'POST',
                                                url: ajax_url,
                                                data: {
                                                    hdIdInvoice : id_invoices,                                
                                                    action : 'onedition_invoice'
                                                },
                                                success: function(data){                          
                                                    if(data !=''){
                                                        var obJson = eval( "(" + data + ")" );                                                        
                                                        var exito = obJson ['exito'];
                                                        if(exito == '1'){
                                                            var id_new_invoice = obJson ['id_new_invoices'];
                                                            $.msgBox({
                                                                type: "info",
                                                                title:"Resultado",
                                                                content:"Se cre&oacute la Nota de Cr&eacutedito:"+id_nc_invoice+"<br>Se cre&oacute la factura 'OnEdition' con el ID: " + id_new_invoice
                                                                ,success: function (data) {location.href="/finkok";}
                                                            });

                                                        } else{
                                                            $.msgBox({
                                                                type: "error",
                                                                title:"Error",
                                                                content:"Error al duplicar la informacion de la factura."
                                                                ,success: function (data) {location.href="/finkok";}
                                                            });
                                                        }
                                                    }else{
                                                        $.msgBox({
                                                            type: "error",
                                                            title:"Error",
                                                            content:"Error al procesar la peticion."
                                                            ,success: function (data) {location.href="/finkok";}
                                                        });
                                                    }                                
                                                }
                                            });
                                        } else{
                                            $.msgBox({
                                                type: "error",
                                                title:"Error",
                                                content:"Error al crear nota de credito."
                                                ,success: function (data) {location.href="/finkok";}
                                            });
                                        }
                                    }else{
                                        $.msgBox({
                                            type: "error",
                                            title:"Error",
                                            content:"Error al procesar la peticion."
                                            ,success: function (data) {location.href="/finkok";}
                                        });
                                    }                                
                                }
                            });
                            
                        }
                    }                
                });
            }

            
        </script>        
    </head>
    <body>       
            <?php
            include_once '../includes/header_bar.php';
            ?> 

 
            <div id="main-container" class="form-container" style="">


                    <table border="0" cellspacing="0" cellpadding="0" width="100%" bgcolor="#bbbbbb">
                        <tr  bgcolor="#ffffff">
                            <td  valign=top align=left>
                                <div style="background-color:#ffffff;margin:15px;">    


                <form name="frmEditInvoice" id="frmEditInvoice" action="process/cfdi_edit_save.php">
                    <input type="submit" name="subSend" id="subSend" style="display: none;" />
                    <input type="hidden" name="action" id="action" value="save_invoice" style="display: none;" />
                    <fieldset class="field-set" style="width: 96%; margin-left:1%;">
                        <legend>
                        <?php
                        if($invoicesDTO->getInvoiceType()=='ingreso'){echo 'Datos de la Factura';
                        }elseif($invoicesDTO->getInvoiceType()=='egreso'){echo 'Datos de la Nota de Cr&eacutedito';}
                        ?>
                        </legend>
                        <table style="width: 100%;" border="0">
                            <tr>
                                <td><label>ID de Factura:</label></td>
                                <td>
                                    <span style="font: bold 9pt Arial;"><?php echo $invoicesDTO->getID_invoices(); ?></span>
                                    <input type="hidden" name="hdIdInvoice" id="hdIdInvoice" value="<?php echo $invoicesDTO->getID_invoices() ?>">
                                    <input type="hidden" name="InvoiceType" id="InvoiceType" value="<?php echo $invoicesDTO->getInvoiceType() ?>">
                                </td>
                            </tr>
                            <tr>
                                <td><label><?php echo $txtNumDoc; ?></label></td>
                                <td ><span style="font: bold 9pt Arial;"><?php echo $NumDoc; ?></span></td>
                            </tr>
                            <tr>
                                <td><label>Serie / Folio:</label></td>
                                <td><span style="font: bold 9pt Arial;"><?php echo $invoicesDTO->getDocSerial(); ?> / <?php echo $invoicesDTO->getDocNum(); ?></span></td>
                            </tr>
                            <tr>
                                <td colspan="4" >&nbsp;</td>
                            </tr>
                            <tr>
                                <td style="vertical-align: top;"><label>No. Pedido de Cliente:</label></td>
                                <td style="vertical-align: top;">
                                    <input type="text" value="<?php echo $invoicesDTO->getID_orders_alias(); ?>" size="20" maxlength='20' class="input" id="txtOrderAlias" name="txtOrderAlias" ></td>
                                <td style="vertical-align: top;"><label>Fecha Pedido de Cliente:</label></td>
                                <td style="vertical-align: top;" ><input type="text" value="<?php echo $invoicesDTO->getID_orders_alias_date(); ?>" size="10" class="input" id="txtOrderAliasDate" name="txtOrderAliasDate" ></td>                                
                            </tr>
                            <tr>
                                <td style="vertical-align: top;"><label>No. Contrarecibo:</label></td>
                                <td style="vertical-align: top;"><input type="text" value="<?php echo $invoicesDTO->getExchangeReceipt(); ?>" size="20" maxlength='20' class="input" id="txtExchangeReceipt" name="txtExchangeReceipt" ></td>
                                <td style="vertical-align: top;"><label>Fecha de Contrarecibo:</label></td>
                                <td style="vertical-align: top;"><input type="text" value="<?php echo $invoicesDTO->getExchangeReceiptDate(); ?>" size="10" class="input" id="txtExchangeReceiptDate" name="txtExchangeReceiptDate" ></td>
                            </tr>
                            <tr>
                                <td style="vertical-align: top;"><label>Dias de Cr&eacute;dito:</label></td>
                                <td style="vertical-align: top;"><input type="text" value="<?php echo $invoicesDTO->getCreditDays(); ?>" size="5" class="input" id="txtCreditDays" name="txtCreditDays" style="text-align: left;"  ></td>
                                <td style="vertical-align: top;"><label>Condiciones</label></td>
                                <td style="vertical-align: top;"><input type="text" value="<?php echo $invoicesDTO->getConditions(); ?>" size="25" class="input" id="txtConditions" name="txtConditions" ></td>
                            </tr>
                            <tr>
                                <td style="vertical-align: top;"><label>Lote:</label></td>
                                <td style="vertical-align: top;"><input type="text" value="<?php echo $invoicesDTO->getBatchNum(); ?>" size="25" class="input" id="txtBatch" name="txtBatch" ></td>
                                <td style="vertical-align: top;"><label>Digitos Cta. Pago:</label></td>
                                <td style="vertical-align: top;">
                                    <input type="text" value="<?php echo $invoicesDTO->getPaymentDigits(); ?>" size="25" class="input" id="txtPaymentDigits" name="txtPaymentDigits" >
                                </td>
                            </tr>
                        </table>
                    </fieldset>
                    <br>
                    <fieldset class="field-set" style="width: 96%; margin-left:1%;">
                        <legend>Datos del Emisor</legend>
                        <table style="width: 100%;" >
                            <tr>
                                <td width="180px"><label>RFC:</label></td>
                                <td>
                                    <input type="text" name="txtExpediterFCode" id="txtExpediterFCode" value="<?php echo $invoicesDTO->getExpediterFiscalCode() ?>" class="input" size="17" maxlength="13" />
                                </td>
                            </tr>
                            <tr>
                                <td><label>Raz&oacute;n Social: </label></td>
                                <td>
                                    <input type="text" name="txtExpediterFName" id="txtExpediterFName" value="<?php echo $invoicesDTO->getExpediterName() ?>" class="input" size="60" />
                                </td>                            
                            </tr>                                    
                            <tr>
                                <td><label>Regim&eacute;n Fiscal: </label></td>
                                <td>
                                    <input type="text" name="txtExpediterFRegimen" id="txtExpediterFRegimen"  class="input" size="70" value="<?php echo $invoicesDTO->getExpediterRegimen(); ?>"  />
                                </td>
                            </tr>
                        </table>
                        <br>
                        <fieldset style="width: 96%; margin-left:1%;">
                            <legend>Domicilio Fiscal</legend>
                            <div id="exp-domfiscal" style="display: block;">
                                <table style="width: 100%;">
                                    <tr>
                                        <td><label>Calle: </label></td>
                                        <td>
                                            <input type="text" name="txtExpediterFAddressStreet" id="txtExpediterFAddressStreet"  class="input" size="50" value="<?php echo $invoicesDTO->getExpediterFAddressStreet(); ?>"  />
                                        </td>
                                        <td><label>No. Exterior: </label></td>
                                        <td>
                                            <input type="text" name="txtExpediterFAddressNum" id="txtExpediterFAddressNum"  class="input" size="10" value="<?php echo $invoicesDTO->getExpediterFAddressNum(); ?>"  />
                                        </td>
                                        <td><label>No. Interior: </label></td>
                                        <td>
                                            <input type="text" name="txtExpediterFAddressNum2" id="txtExpediterFAddressNum2"  class="input" size="25" value="<?php echo $invoicesDTO->getExpediterFAddressNum2(); ?>"  />
                                        </td>                            
                                    </tr> 
                                    <tr>
                                        <td><label>Colonia: </label></td>
                                        <td>
                                            <input type="text" name="txtExpediterFAddressUrbanization" id="txtExpediterFAddressUrbanization"  class="input" size="50" value="<?php echo $invoicesDTO->getExpediterFAddressUrbanization(); ?>"  />
                                        </td>
                                        <td><label>Localidad: </label></td>
                                        <td>
                                            <input type="text" name="txtExpediterFAddressDistrict" id="txtExpediterFAddressDistrict"  class="input" size="35" value="<?php echo $invoicesDTO->getExpediterFAddressDistrict(); ?>"  />
                                        </td>
                                        <td><label>C.P: </label></td>
                                        <td>
                                            <input type="text" name="txtExpediterFAddressZipcode" id="txtExpediterFAddressZipcode"  class="input" size="8" value="<?php echo $invoicesDTO->getExpediterFAddressZipcode(); ?>"  />
                                        </td>
                                    </tr>
                                    <tr>
                                        <td><label>Estado: </label></td>
                                        <td>
                                            <input type="text" name="txtExpediterFAddressState" id="txtExpediterFAddressState"  class="input" size="35" value="<?php echo $invoicesDTO->getExpediterFAddressState(); ?>"  />
                                        </td>
                                        <td><label>Delegaci&oacute;n / Mpio.: </label></td>
                                        <td>
                                            <input type="text" name="txtExpediterFAddressCity" id="txtExpediterFAddressCity"  class="input" size="35" value="<?php echo $invoicesDTO->getExpediterFAddressCity(); ?>"  />
                                        </td> 
                                        <td><label>Pa&iacute;s: </label></td>
                                        <td>
                                            <input type="text" name="txtExpediterFAddressCountry" id="txtExpediterFAddressCountry"  class="input" size="25" value="<?php echo $invoicesDTO->getExpediterFAddressCountry(); ?>"  />
                                        </td> 

                                    </tr>
                                </table>
                            </div>
                        </fieldset style="width: 96%; margin-left:1%;">
                        <br>
                        <fieldset style="width: 96%; margin-left:1%;">
                            <legend>Lugar de Emisi&oacute;n&nbsp;&nbsp;[<span id="spn-eq-expediterdomfiscal" onclick="copyExpediterFiscalAddress()" style="text-decoration: underline; cursor: pointer;">Copiar Domicilio Fiscal</span>]&nbsp;</legend>
                            <div id="exp-domemision" style="display: block;">
                                <table style="width: 100%;">
                                    <tr>
                                        <td><label>Calle: </label></td>
                                        <td>
                                            <input type="text" name="txtExpediterAddressStreet" id="txtExpediterAddressStreet"  class="input" size="50" value="<?php echo $invoicesDTO->getExpediterAddressStreet(); ?>"  />
                                        </td>
                                        <td><label>No. Exterior: </label></td>
                                        <td>
                                            <input type="text" name="txtExpediterAddressNum" id="txtExpediterAddressNum"  class="input" size="10" value="<?php echo $invoicesDTO->getExpediterAddressNum(); ?>"  />
                                        </td>
                                        <td><label>No. Interior: </label></td>
                                        <td>
                                            <input type="text" name="txtExpediterAddressNum2" id="txtExpediterAddressNum2"  class="input" size="25" value="<?php echo $invoicesDTO->getExpediterAddressNum2(); ?>"  />
                                        </td>                            
                                    </tr> 
                                    <tr>
                                        <td><label>Colonia: </label></td>
                                        <td>
                                            <input type="text" name="txtExpediterAddressUrbanization" id="txtExpediterAddressUrbanization"  class="input" size="50" value="<?php echo $invoicesDTO->getExpediterAddressUrbanization(); ?>"  />
                                        </td>
                                        <td><label>Localidad: </label></td>
                                        <td>
                                            <input type="text" name="txtExpediterAddressDistrict" id="txtExpediterAddressDistrict"  class="input" size="35" value="<?php echo $invoicesDTO->getExpediterAddressDistrict(); ?>"  />
                                        </td>
                                        <td><label>C.P: </label></td>
                                        <td>
                                            <input type="text" name="txtExpediterAddressZipcode" id="txtExpediterAddressZipcode"  class="input" size="8" value="<?php echo $invoicesDTO->getExpediterAddressZipcode(); ?>"  />
                                        </td>
                                    </tr>
                                    <tr>
                                        <td><label>Estado: </label></td>
                                        <td>
                                            <input type="text" name="txtExpediterAddressState" id="txtExpediterAddressState"  class="input" size="35" value="<?php echo $invoicesDTO->getExpediterAddressState(); ?>"  />
                                        </td>
                                        <td><label>Delegaci&oacute;n / Mpio.: </label></td>
                                        <td>
                                            <input type="text" name="txtExpediterAddressCity" id="txtExpediterAddressCity"  class="input" size="35" value="<?php echo $invoicesDTO->getExpediterAddressCity(); ?>"  />
                                        </td> 
                                        <td><label>Pa&iacute;s: </label></td>
                                        <td>
                                            <input type="text" name="txtExpediterAddressCountry" id="txtExpediterAddressCountry"  class="input" size="25" value="<?php echo $invoicesDTO->getExpediterAddressCountry(); ?>"  />
                                        </td> 

                                    </tr>
                                </table>
                            </div>
                        </fieldset>                            
                    </fieldset>
                    <br>
                    <fieldset class="field-set" style="width: 96%; margin-left:1%;">
                        <legend>Datos del Receptor</legend>                        
                        <table style="width: 100%;">
                            <tr>
                                <td width="180px"><label>RFC:</label></td>
                                <td>
                                    <input type="text" name="txtCustomerFCode" id="txtCustomerFCode" value="<?php echo $invoicesDTO->getCustomerFiscalCode() ?>" class="input" size="17" maxlength="13" />
                                </td>
                            </tr>
                            <tr>
                                <td><label>Nombre o Raz&oacute;n Social: </label></td>
                                <td>
                                    <input type="text" name="txtCustomerFName" id="txtCustomerFName" value="<?php echo $invoicesDTO->getCustomerName() ?>" class="input" size="60" />
                                </td>                                                        
                            </tr> 
                            <tr>
                                <td><label>Clave de Contacto o Depto.: </label></td>
                                <td>
                                    <input type="text" name="txtCustomerShpAddressContact" id="txtCustomerShpAddressContact" value="<?php echo $invoicesDTO->getCustomerShpaddressContact() ?>" class="input" size="10" />
                                </td>                                                        
                            </tr> 
                        </table>
                        <br>
                        <fieldset style="width: 96%; margin-left:1%;">
                            <legend>Domicilio Fiscal</legend>
                            <div id="rcp-domfiscal">
                                <table style="width: 100%;">
                                    <tr>
                                        <td><label>Calle: </label></td>
                                        <td>
                                            <input type="text" name="txtCustomerAddressStreet" id="txtCustomerAddressStreet"  class="input" size="50" value="<?php echo $invoicesDTO->getCustomerFAddressStreet(); ?>"  />
                                        </td>
                                        <td><label>No. Exterior: </label></td>
                                        <td>
                                            <input type="text" name="txtCustomerAddressNum" id="txtCustomerAddressNum"  class="input" size="10" value="<?php echo $invoicesDTO->getCustomerFAddressNum(); ?>"  />
                                        </td>
                                        <td><label>No. Interior: </label></td>
                                        <td>
                                            <input type="text" name="txtCustomerAddressNum2" id="txtCustomerAddressNum2"  class="input" size="25" value="<?php echo $invoicesDTO->getCustomerFAddressNum2(); ?>"  />
                                        </td>                            
                                    </tr> 
                                    <tr>
                                        <td><label>Colonia: </label></td>
                                        <td>
                                            <input type="text" name="txtCustomerAddressUrbanization" id="txtCustomerAddressUrbanization"  class="input" size="50" value="<?php echo $invoicesDTO->getCustomerFAddressUrbanization(); ?>"  />
                                        </td>
                                        <td><label>Localidad: </label></td>
                                        <td>
                                            <input type="text" name="txtCustomerAddressDistrict" id="txtCustomerAddressDistrict"  class="input" size="35" value="<?php echo $invoicesDTO->getCustomerFAddressDistrict(); ?>"  />
                                        </td>
                                        <td><label>C.P: </label></td>
                                        <td><input type="text" name="txtCustomerAddressZipcode" id="txtCustomerAddressZipcode"  class="input" size="8" value="<?php echo $invoicesDTO->getCustomerFAddressZipcode(); ?>"  /></td>
                                    </tr>
                                    <tr>
                                        <td><label>Estado: </label></td>
                                        <td>
                                            <input type="text" name="txtCustomerAddressState" id="txtCustomerAddressState"  class="input" size="35" value="<?php echo $invoicesDTO->getCustomerFAddressState(); ?>"  />
                                        </td>
                                        <td><label>Delegaci&oacute;n / Mpio.: </label></td>
                                        <td>
                                            <input type="text" name="txtCustomerAddressCity" id="txtCustomerAddressCity"  class="input" size="35" value="<?php echo $invoicesDTO->getCustomerFAddressCity(); ?>"  />
                                        </td> 
                                        <td><label>Pa&iacute;s: </label></td>
                                        <td>
                                            <input type="text" name="txtCustomerAddressCountry" id="txtCustomerAddressCountry"  class="input" size="25" value="<?php echo $invoicesDTO->getCustomerFAddressCountry(); ?>"  />
                                        </td> 
                                    </tr>                            
                                </table>
                            </div>
                        </fieldset>         
                        <br>               
                        <fieldset style="width: 96%; margin-left:1%;">
                            <legend>Lugar de Entrega&nbsp;&nbsp;[<span id="spn-eq-customerfiscal" style="text-decoration: underline; cursor: pointer;" onclick="copyCustomerFiscalAddress()">Copiar Domicilio Fiscal</span>]&nbsp;</legend>
                            <div id="rcp-shpdom">
                                <table style="width: 100%;">
                                    <tr>
                                        <td><label>Calle: </label></td>
                                        <td>
                                            <input type="text" name="txtCustomerShpAddressStreet" id="txtCustomerShpAddressStreet"  class="input" size="50" value="<?php echo $invoicesDTO->getCustomerShpAddressStreet(); ?>"  />
                                        </td>
                                        <td><label>No. Exterior: </label></td>
                                        <td>
                                            <input type="text" name="txtCustomerShpAddressNum" id="txtCustomerShpAddressNum"  class="input" size="10" value="<?php echo $invoicesDTO->getCustomerShpAddressNum(); ?>"  />
                                        </td>
                                        <td><label>No. Interior: </label></td>
                                        <td>
                                            <input type="text" name="txtCustomerShpAddressNum2" id="txtCustomerShpAddressNum2"  class="input" size="25" value="<?php echo $invoicesDTO->getCustomerShpAddressNum2(); ?>"  />
                                        </td>                            
                                    </tr> 
                                    <tr>
                                        <td><label>Colonia: </label></td>
                                        <td>
                                            <input type="text" name="txtCustomerShpAddressUrbanization" id="txtCustomerShpAddressUrbanization"  class="input" size="50" value="<?php echo $invoicesDTO->getCustomerShpAddressUrbanization(); ?>"  />
                                        </td>
                                        <td><label>Localidad: </label></td>
                                        <td>
                                            <input type="text" name="txtCustomerShpAddressDistrict" id="txtCustomerShpAddressDistrict"  class="input" size="35" value="<?php echo $invoicesDTO->getCustomerShpAddressDistrict(); ?>"  />
                                        </td>
                                        <td><label>C.P: </label></td>
                                        <td><input type="text" name="txtCustomerShpAddressZipcode" id="txtCustomerShpAddressZipcode"  class="input" size="8" value="<?php echo $invoicesDTO->getCustomerShpAddressZipcode(); ?>"  /></td>
                                    </tr>
                                    <tr>
                                        <td><label>Estado: </label></td>
                                        <td>
                                            <input type="text" name="txtCustomerShpAddressState" id="txtCustomerShpAddressState"  class="input" size="35" value="<?php echo $invoicesDTO->getCustomerShpAddressState(); ?>"  />
                                        </td>
                                        <td><label>Delegaci&oacute;n / Mpio.: </label></td>
                                        <td>
                                            <input type="text" name="txtCustomerShpAddressCity" id="txtCustomerShpAddressCity"  class="input" size="35" value="<?php echo $invoicesDTO->getCustomerShpAddressCity(); ?>"  />
                                        </td> 
                                        <td><label>Pa&iacute;s: </label></td>
                                        <td>
                                            <input type="text" name="txtCustomerShpAddressCountry" id="txtCustomerShpAddressCountry"  class="input" size="25" value="<?php echo $invoicesDTO->getCustomerShpAddressCountry(); ?>"  />
                                        </td> 
                                    </tr>                            
                                </table>
                            </div>
                        </fieldset>                                                
                    </fieldset>
                </form>
                <br>
                <!-- Lineas de la Factura -->
                <div id="invoice-items">
                    <?php
                    if (!empty($vector_invoices_lines)) {
                        ?>
                        <table width="98%" align="center"  class="List">
                            <tr class="tableListColumn">                            
                                <td style="width: 6%;" align="center">CANTIDAD</td>
                                <td style="width: 6%;" align="center">UM</td>
                                <td style="min-width: 25%;" align="center">DESCRIPCION</td>
                                <td style="width: 10%;" align="center">P UNIT</td>
                                <td style="width: 10%;" align="center">IMPORTE</td>
                                <td style="width: 10%;" align="center">% IMPUESTO</td> 
                                <td style="width: 1%;" align="center">ADUANA</td>                            
                            </tr>                        
                            <?php
                            $style = 0;
                            $flagCSS = FALSE;
                            foreach ($vector_invoices_lines as $invoicesLinesDTO) {
                                $arr_taxes[$invoicesLinesDTO->getTaxName()][$invoicesLinesDTO->getTaxRate()] += $invoicesLinesDTO->getTax();

                                if ($flagCSS) {
                                    $style = 1;
                                    $flagCSS = FALSE;
                                } else {
                                    $style = 0;
                                    $flagCSS = TRUE;
                                }
                                ?>
                                <tr class="tableFila<?php echo $style; ?>">                            
                                    <td align="center"><?php echo $invoicesLinesDTO->getQuantity() ?></td>
                                    <td align="center"><?php echo $invoicesLinesDTO->getMeasuringUnit() ?></td>
                                    <?php 
                                    if($invoicesLinesDTO->getIdSkuAlias()==''){$Sku=$invoicesLinesDTO->getUPC();
                                    }else{$Sku=$invoicesLinesDTO->getIdSkuAlias();}
                                    if($Sku=='' || $Sku<=0){$Sku=$invoicesLinesDTO->getIdSku();}
                                    ?>
                                    <td align="left"><?php echo $Sku . ' - ' . $invoicesLinesDTO->getDescription() ?></td>
                                    <td align="right" style="padding-right: 5px;">$&nbsp;<?php echo number_format($invoicesLinesDTO->getUnitPrice(), 2, '.', ','); ?></td>
                                    <td align="right" style="padding-right: 5px;">$&nbsp;<?php echo number_format($invoicesLinesDTO->getAmount(),2,'.',','); ?></td>
                                    <td align="center" style="padding-right: 5px;"><?php echo $invoicesLinesDTO->getTaxRate() * 100 ?></td>
                                    <td align="center" style="padding-right: 5px;"><span style="cursor: pointer;" onclick="loadPopupCustoms(<?php echo $invoicesLinesDTO->getID_invoices_lines(); ?> , '<?php echo $invoicesLinesDTO->getDescription(); ?>', '<?php echo $invoicesDTO->getID_invoices(); ?>')"><img src="../../common/img/b_edit.png" border="0"></span></td>
                                </tr>
                                <?php
                            }
                            ?>
                        </table>
                        <?php
                    }
                    ?>
                </div>
                <br>                
                <div>
                    <table align="center" style="min-width: 98%; border-width: 1px 1px 1px 1px;    border-spacing: 0px;    border-style: solid solid solid solid;    border-color: #778b9d #778b9d #778b9d #778b9d;">
                        <tr>
                            <td style="width: 85%; text-align: right;"><label>Sub Total</label></td>                        
                            <td align="right" style="padding-right: 5px;"><label><?php echo $Signo.' '.number_format($invoicesDTO->getInvoiceNet(), 2, '.', ',') ?></label></td>
                        </tr>
                        <tr>
                            <td style="width: 85%; text-align: right;"><label>Total Descuentos</label></td>                        
                            <td align="right" style="padding-right: 5px;"><label><?php echo $Signo.' '.number_format($invoicesDTO->getDiscount(), 2, '.', ',') ?></label></td>
                        </tr>
                        <tr>
                            <td style="width: 85%; text-align: right;"><label>Total Cargos</label></td>                        
                            <td align="right" style="padding-right: 5px;"><label><?php echo $Signo.' ';?>0.00</label></td>
                        </tr>
                        <tr>
                            <td style="width: 85%; text-align: right;"><label>Sub Total</label></td>                        
                            <td align="right" style="padding-right: 5px;"><label><?php echo $Signo.' '.number_format($invoicesDTO->getInvoiceNet()-$invoicesDTO->getDiscount(), 2, '.', ',') ?></label></td>
                        </tr>                       
                        <!-- iterar -->
                        <?php
                        foreach ($arr_taxes as $tax_name => $arr_tax_rate) {
                            foreach ($arr_tax_rate as $tax_rate => $tax_total) {
                                ?>
                                <tr>                        
                                    <td style="width: 85%; text-align: right;"><label><?php echo $tax_name . ' ' . ($tax_rate * 100); ?> %</label></td>
                                    <td align="right" style="padding-right: 5px;"><label><?php echo $Signo.' '.number_format($tax_total, 2, '.', ','); ?></label></td>
                                </tr>
                                <?php
                            }
                        }
                        ?>
                        <tr>                        
                            <td style="width: 85%; text-align: right;"><label>Total</label></td>
                            <td align="right" style="padding-right: 5px;"><label><?php echo $Signo.' '.number_format($invoicesDTO->getInvoiceTotal(), 2, '.', ','); ?></label></td>
                        </tr>
                    </table>
                </div>                
                <div id="invoice-notes-container">
                    <br>
                    <fieldset class="field-set" style="width: 96%; margin-left:1%;">
                        <legend>Notas</legend>
                        <div style="width: 100%; text-align: center; text-decoration: underline; font-size: 9pt; " >
                            <span style="cursor: pointer;" onclick="loadPopupNotes(<?php echo $invoicesDTO->getID_invoices(); ?>,'Note')"><img src="../../common/img/b_add.gif">&nbsp;Agregar Nota</span>
                            <span id="spn-nota-imp" style="cursor: pointer; padding-left: 20px;" onclick="loadPopupNotes(<?php echo $invoicesDTO->getID_invoices(); ?>,'ToPrint')"><img src="../../common/img/b_add.gif">&nbsp;Agregar observaciones para comprobante impreso</span>
                        </div>
                        <div id="invoice-notes-list"></div>   
                    </fieldset>
                </div>
                <br>
                <div style="text-align: center;">
                    <?php
                    //--Desaparece botones para documentos del mes anterior $cfg['cfdi_close_capture']
                    $Fecha=explode('-',$invoicesDTO->getDate());
                    if($Fecha[1]!=date('m') && $cfg['cfdi_close_capture']==1){
                        echo "- Captura cerrada - <br /> Este registro pertenece a un mes anterior al actual.";
                        echo "<br />";
                        if ($invoicesDTO->getStatus() == 'New'  || $invoicesDTO->getStatus() == 'OnEdition' || $invoicesDTO->getStatus() == 'Confirmed' || $invoicesDTO->getStatus() == 'Retry') {
                            ?>                    
                            <span id="btn-anulate">
                                <input type="button" name="" value="Anular Documento"  class="button" onclick="voidInvoice()"/>
                            </span>
                            <?php
                        }
                        
                        if ($invoicesDTO->getStatus() == 'Cancelled' || $invoicesDTO->getStatus() == 'Void') {
                            ?>                    
                            <span id="btn-duplicate">
                                <input type="button" name="" value="Duplicar Documento"  class="button" onclick="duplicateInvoice()"/>
                            </span>
                            <?php
                        }
                        ##Si es TMK o MOW permite crear la factura nueva
                        if ($e==2 || $e==4 || $e==3 || $e==11 || $e==7 || $e==13) {
                            ?>                    
                            <span id="btn-otherinvoice">
                                <input type="button" name="" value="Crear factura de Cliente"  class="button" onclick="otherInvoice()"/>
                            </span>
                            <?php
                        }
                    }else{
                        //--- validacion de status para mostrar el boton de guardado de informacion
                        if ($invoicesDTO->getStatus() == 'New'  || $invoicesDTO->getStatus() == 'OnEdition' || $invoicesDTO->getStatus() == 'Retry') {
                            ?>
                            <span id="btn-save">
                                <input type="button" name="" value="Guardar Informaci&oacute;n"  class="button" onclick="validarDatosFormulario('form')"/>
                            </span>
                            <?php
                        }

                        /*
                        if ($invoicesDTO->getStatus() == 'Confirmed') {
                            ?>
                            <span id="btn-save">
                                <input type="button" name="" value="Cancelar proceso de Timbrado"  class="button" onclick="cancelCertificationProcess()"/>
                            </span>                    
                            <?php
                        }
                        */

                        if ($invoicesDTO->getStatus() == 'New'  || $invoicesDTO->getStatus() == 'OnEdition' || $invoicesDTO->getStatus() == 'Retry') {
                            ?>
                            <span id="btn-confirm">
                                <input type="button" name="" value="Confirmar para Timbrar"  class="button" onclick="validarDatosFormulario('form')"/>
                            </span>
                            <?php
                        }

                        /*
                          if ($invoicesDTO->getStatus() == 'Void') {
                          ?>
                          <span id="btn-reactivate">
                          <input type="button" name="" value="Reactivar Documento"  class="button" onclick="reactivateInvoice()"/>
                          </span>
                          <?php
                          }
                         */
                        //-- guardar unicamente notas
                        if ($invoicesDTO->getStatus() == 'Confirmed' || $invoicesDTO->getStatus() == 'Void' || $invoicesDTO->getStatus() == 'Failed' || $invoicesDTO->getStatus() == 'Certified' || $invoicesDTO->getStatus() == 'Rety' || $invoicesDTO->getStatus() == 'Cancelled') {
                            ?>
                            <span id="btn-savenotes">
                                <input type="button" name="" value="Guardar Notas"  class="button" onclick="saveInvoiceNotes()"/>
                            </span> 
                            <?php
                        }

                        if ($invoicesDTO->getStatus() == 'New' || $invoicesDTO->getStatus() == 'OnEdition' || $invoicesDTO->getStatus() == 'Confirmed' || $invoicesDTO->getStatus() == 'Retry') {
                            ?>                    
                            <span id="btn-anulate">
                                <input type="button" name="" value="Anular Documento"  class="button" onclick="voidInvoice()"/>
                            </span>
                            <?php
                        }

                        if ($invoicesDTO->getStatus() == 'Cancelled' || $invoicesDTO->getStatus() == 'Void') {
                            ?>                    
                            <span id="btn-duplicate">
                                <input type="button" name="" value="Duplicar Documento"  class="button" onclick="duplicateInvoice()"/>
                            </span>
                            <?php
                        }

                        if (($e==2 || $e==4 || $e==12)  && $invoicesDTO->getInvoiceType() == 'ingreso' && $invoicesDTO->getStatus() != 'OnEdition' && $invoicesDTO->getStatus() != 'New' ) {
                            ?>                    
                            <span id="btn-otherinvoice">
                                <input type="button" name="" value="Crear factura de Cliente"  class="button" onclick="otherInvoice()"/>
                            </span>
                            <?php
                        }
                        if ($invoicesDTO->getStatus() == 'Certified') {
                            ?>                    
                            <span id="btn-cancel">
                                <input type="button" name="" value="Cancelar Documento"  class="button" onclick="cancelInvoice()"/>
                            </span>
                            <?php
                        }
                        /*
                        if ($invoicesDTO->getInvoiceType() == 'ingreso' && $invoicesDTO->getStatus() == 'Certified') {
                            ?>
                            <!--
                            <span id="btn-credit">
                                <input type="button" name="" value="Nota de Credito por Importe Total"  class="button" onclick="creditNote()"/>
                            </span>
                            -->
                            <?php
                        }
                        */
                    }
                    ?>
                </div>
                <div style="width: 100%; text-align: center; text-decoration: underline; font-size: 9pt; margin-top:10px; margin-bottom:10px;" >
                    <!--<span style="cursor: pointer;" onclick="location.href='/finkok'">Regresar</span>-->
                    <input type="button" name="" value="Regresar"  class="button" onclick="location.href='/finkok'"/>
                </div>
                                </div>
                            </td>
                        </tr>
                    </table>
            </div>



            <?php
            include_once '../includes/footer.php';
            ?>  
 
        </div>
    </body>
</html>
