<?php
/**
 * Description
 *
 * @author L.C.I Cesar Cedillo
 */
session_start();

$COMMON_PATH = '../../..';

$idx = $_GET['idx'];
$qty = $_GET['qty'];

//--- obtiene el arreglo con los datos de las partes que estan en sesion
?>
<html>
    <head>
        <meta http-equiv="Content-Type" content="text/html; charset=UTF-8">
        <title></title>
        <link href="<?php echo $COMMON_PATH ?>/common/js/css/smoothness/jquery-ui-1.8.17.custom.css" type="text/css" rel="stylesheet"/>
        <link href="<?php echo $COMMON_PATH ?>/common/css/common.css" rel="stylesheet" type="text/css" />
        <link href="<?php echo $COMMON_PATH ?>/common/js/jquery.msgbox.css" type="text/css" rel="stylesheet"/>        
        <link href="<?php echo $COMMON_PATH ?>/common/js/jpaginate/css/style.css" type="text/css" rel="stylesheet" media="screen" />

        <script type="text/javascript" src="<?php echo $COMMON_PATH ?>/common/js/jquery-1.6.4.min.js"></script>
        <script type="text/javascript" src="<?php echo $COMMON_PATH ?>/common/js/jquery-ui.min.js"></script>        
        <script type="text/javascript" src="<?php echo $COMMON_PATH ?>/common/js/jquery.msgbox.min.js"></script>
        <script type="text/javascript" src="<?php echo $COMMON_PATH ?>/common/js/validaciones.js"></script>


        <script type="text/javascript">
            function validateInformation(){
                var payment_date = $("#txtPaymentDate").val();
                var payment_amount = $("#txtPaymentAmount").val(); 
                var bank_currency = $("#lstBanks").val();
                var payment_notes = $("#txtNotes").val();
                
                var arr_bank_curr = bank_currency.split("|");     //-- Separa los datos del valor del select de bancos           
                var payment_bank = arr_bank_curr[0];    //-- Id del banco
                var payment_currency = arr_bank_curr[1]; //-- Currency del banco

                var errores_validacion = "";                

                if(payment_bank == ""){
                    errores_validacion +="- Debe seleccionar una entidad bancaria.<br>";
                }

                if(payment_date == ""){
                    errores_validacion +="- Debe seleccionar una fecha para el pago.<br>";
                }
                
                if(validar_flotante(payment_amount)){
                    if(payment_amount <= 0){
                        errores_validacion +="- El monto debe ser mayor a cero.<br>";                    
                    }
                }else{
                    errores_validacion +="- El monto no es una cantidad valida.<br>";
                }
                
                if(errores_validacion == ""){
                    savePaymentInfo(payment_date,payment_amount,payment_notes,payment_bank,payment_currency)
                }else{
                    $.msgbox("Se encontraron los siguientes errores en la informacion:<br>"+errores_validacion, {
                        buttons : [
                            {type: "submit", value: "Aceptar"},
                        ]
                    });                   
                }                    
            }
            
            
            function savePaymentInfo(payment_date,payment_amount,payment_notes,payment_bank,payment_currency){
                var payment_bank_name = $("#lstBanks option:selected").text();                
                
                var ajax_url = '../ajax/ajax_po_payments_control.php';
                
                $.ajax({
                    type: 'POST',
                    url: ajax_url,
                    data: {
                        pay_date: payment_date,           
                        pay_amount: payment_amount,
                        pay_notes: payment_notes,
                        pay_bank: payment_bank,
                        pay_bank_name: payment_bank_name,
                        pay_currency: payment_currency,
                        action : 'add_payment'
                    },
                    success: function(data){                          
                        parent.closeRefreshList();
                    }
                });
                
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
    </head>
    <body>
        <div id="popup-upcs" style="width: 550px; height: 220px; border-width: 1px; border-color: #f8f8ff #f8f8ff #f8f8ff #808080; border-style: outset;">
            <div class="popup_bar_title">
                <img id="close-button" src="<?php echo $COMMON_PATH; ?>/common/img/popupclose.gif" class="simplemodal-close" style="margin-right: 20px; cursor: pointer;" onclick="parent.closePopUp()" />
                PAGOS / ANTICIPOS
            </div>
            <div style="font-family: Arial; font-size: 12px; width: 100%; float: left; margin-right: 0px; margin-bottom: 2px; text-align: left; margin-top: 0px;">
                <fieldset>
                    <legend>Informaci&oacute;n del Pago</legend>
                    <table width="100%" align="center">
                        <tr>
                            <td style="width: 180px;"><label>Entidad Bancaria:</label></td>
                            <td>
                                <?php include 'select_banks.php'; ?>
                            </td>
                        </tr>                        
                        <tr>
                            <td style="width: 180px;"><label>Fecha del Pago:</label></td>
                            <td>
                                <input type="text" name="txtPaymentDate" id="txtPaymentDate"  class="text-box" size="10" readonly/>
                            </td>
                        </tr>
                        <tr>
                            <td><label>Monto:</label></td>
                            <td>
                                <input type="text" name="txtPaymentAmount" id="txtPaymentAmount"  class="text-box" size="10" style="text-align: right;" />&nbsp;
                            </td>
                        </tr>
                        <tr>
                            <td><label>Notas:</label></td>
                            <td><textarea name="txtNotes" id="txtNotes" cols="50" rows="1" class="text-box"></textarea></td>
                        </tr>
                        <tr>
                            <td align="center" colspan="2">
                                <input type="button" name="" value="Agregar Informacion"  class="button" onclick="validateInformation()"/>
                            </td>
                        </tr>
                    </table>
                </fieldset>
            </div>
        </div>
    </body>
</html>