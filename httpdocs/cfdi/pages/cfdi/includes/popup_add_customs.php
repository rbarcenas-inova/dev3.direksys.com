<?php
$COMMON_PATH = "../../..";
require_once $COMMON_PATH . '/trsBase.php';
require_once $COMMON_PATH . '/common/php/class/db/DbHandler.php';
require_once $COMMON_PATH . '/common/php/class/dto.catalog.InvoicesLinesDTO.php';
require_once $COMMON_PATH . '/common/php/class/dao.catalog.InvoicesLinesDAO.php';
require_once $COMMON_PATH . '/common/php/class/dao.catalog.InvoicesDAO.php';
#require_once $COMMON_PATH . '/common/php/class/dao.catalog.InvoicesDTO.php';

session_start();
$ID_invoices_lines = isset($_POST['id_invoices_lines']) ? $_POST['id_invoices_lines'] : $_GET['id_invoices_lines'];
$Description = isset($_POST['description']) ? $_POST['description'] : $_GET['description'];
$ID_invoices = isset($_POST['id_invoice']) ? $_POST['id_invoice'] : $_GET['id_invoice'];
#$glnCustoms = isset($_POST['glnCustoms']) ? $_POST['glnCustoms'] : $_GET['glnCustoms'];

$invoicesLinesDAO = new InvoicesLinesDAO();
$invoicesLinesDTO = new InvoicesLinesDTO();
$invoicesLinesDTO->setID_invoices_lines($ID_invoices_lines);
$vector_invoices = $invoicesLinesDAO->selectRecords($invoicesLinesDTO);
$invoicesLinesDTO = $vector_invoices[0];

$invoicesDAO = new InvoicesDAO();
$invoicesDTO = new InvoicesDTO();
$invoicesDTO->setID_invoices($ID_invoices);
$vector_invoice = $invoicesDAO->selectRecords($invoicesDTO);
$invoicesDTO = $vector_invoice[0];

?>

<html>
    <head>
        <meta http-equiv="Content-Type" content="text/html; charset=UTF-8">
        <title></title>        
        <link href="<?php echo $COMMON_PATH ?>/common/css/common.css" rel="stylesheet" type="text/css" />
        <link href="<?php echo $COMMON_PATH ?>/common/css/main.css" rel="stylesheet" type="text/css" />
        <link href="<?php echo $COMMON_PATH ?>/common/js/css/smoothness/jquery-ui-1.8.17.custom.css" type="text/css" rel="stylesheet"/>
        <link href="<?php echo $COMMON_PATH ?>/common/js/jquery.msgbox.css" type="text/css" rel="stylesheet"/>        

        <script type="text/javascript" src="<?php echo $COMMON_PATH ?>/common/js/jquery-1.6.4.min.js"></script>
        <script type="text/javascript" src="<?php echo $COMMON_PATH ?>/common/js/jquery-ui.min.js"></script>        
        <script type="text/javascript" src="<?php echo $COMMON_PATH ?>/common/js/jquery.msgbox.min.js"></script>
        <script type="text/javascript" src="<?php echo $COMMON_PATH ?>/common/js/validaciones.js"></script>
        <script type="text/javascript" src="<?php echo $COMMON_PATH ?>/common/js/functions.js"></script>


        <script type="text/javascript">
            $(document).ready(function(){
                $("body").css({ 'background-color': '#ffffff' });
                $("body").css('background-image', 'none');
            });
            
            
            function validateInformation(){
                
                var idInvoiceLines = $("#idInvoiceLines").val();
                //var glnCustoms = $("#glnCustoms").val();
                var nameCustoms = $("#nameCustoms").val();
                var numCustoms = $("#numCustoms").val();
                var dateCustoms = $("#dateCustoms").val();
                
                var errores_validacion = "";                
                /*
                if(glnCustoms == ""){
                    errores_validacion +="- Debe ingresar el codigo GLN de la aduana.<br>";
                }    
                */           
                if(nameCustoms == ""){
                    errores_validacion +="- Debe ingresar el nombre de la Aduana.<br>";
                }
                /*
                if(numCustoms == ""){
                    errores_validacion +="- Debe ingresar el número de pedimento.<br>";
                }
                if(dateCustoms == ""){
                    errores_validacion +="- Debe ingresar la fecha de expedición del documento.<br>";
                }
                */
                if(errores_validacion == ""){
                    saveInfo(idInvoiceLines, nameCustoms, numCustoms, dateCustoms)
                }else{
                    $.msgbox("Se encontraron los siguientes errores en la informacion:<br>"+errores_validacion, {
                        buttons : [
                            {type: "submit", value: "Aceptar"},
                        ]
                    });                   
                }                    
            }
            
            
            function saveInfo(idInvoiceLines,nameCustoms,numCustoms,dateCustoms){
                
                var ajax_url = '../process/cfdi_edit_save.php';
               
                $.ajax({
                    type: 'POST',
                    url: ajax_url,
                    data: {
                        idInvoiceLines : idInvoiceLines,
                        nameCustoms: nameCustoms,
                        numCustoms : numCustoms,
                        dateCustoms : dateCustoms,  
                        action : 'save_customs'
                    },
                    success: function(data){  
                        parent.closePopUp();
                    }
                });                
            }
            


            $(function() {
                $("#dateCustoms").datepicker(
                {
                    dateFormat: "yy-mm-dd",
                    setDate: new Date(),
                    defaultDate: new Date(),
                    changeMonth: true,
                    changeYear: true,
                    numberOfMonths: 1
                }
            );
            });            
        </script>
    </head>
    <body>        
        <div id="popup-upcs" style="width: 99%; height: 99%; border-width: 1px; border-color: #f8f8ff #f8f8ff #f8f8ff #808080; border-style: outset;">
            <div class="popup_bar_title">
                <img id="close-button" src="<?php echo $COMMON_PATH; ?>/common/img/popupclose.gif" class="simplemodal-close" style="margin-right: 20px; cursor: pointer;" onclick="parent.closePopUp()" />
                INFORMACIÓN ADUANAL
            </div>
            <div style="font-family: Arial; font-size: 12px; width: 100%; float: left; margin-right: 0px; margin-bottom: 2px; text-align: left; margin-top: 0px;">
                <fieldset>
                    <legend><?php echo $Description; ?></legend>
                    <table width="100%" align="center">
                        <!--
                        <tr>
                            <td><label>Codigo GLN:</label></td>
                            <td>                                
                                <input type="text" name="glnCustoms" id="glnCustoms" size="20" class="text-box"  onFocus="javascript: focusOn(this.id);" onBlur="javascript: focusOff(this.id)" value="">
                            </td>
                        </tr>
                        --> 
                        <tr>
                            <td><label>Aduana:</label></td>
                            <td>
                                <!--<input type="text" name="nameCustoms" id="nameCustoms" size="40" class="text-box"  onFocus="javascript: focusOn(this.id);" onBlur="javascript: focusOff(this.id)" value="">-->
                                <input type="hidden" id="idInvoiceLines" name="idInvoiceLines" value="<?php echo $ID_invoices_lines;?>">
                                <select name="nameCustoms" id="nameCustoms" onFocus="javascript: focusOn(this.id);" onBlur="javascript: focusOff(this.id)" class="text-box">
                                    <option value="<?php echo $invoicesLinesDTO->getCustomsName() ?>" selected="selected"><?php echo $invoicesLinesDTO->getCustomsName() ?></option>
                                    <option value="LAZARO CARDENAS">LAZARO CARDENAS-510</option>
                                    <option value="MANZANILLO">MANZANILLO-160</option>
                                    <option value="AEROPUERTO">AEROPUERTO-470</option>
                                    <option value="LAREDO">LAREDO-240</option>
                                </select>
                            </td>
                        </tr> 
                        <tr>
                            <td><label>No. de Pedimento:</label></td>
                            <td>
                                <input type="text" name="numCustoms" id="numCustoms" size="20" class="text-box"  onFocus="javascript: focusOn(this.id);" onBlur="javascript: focusOff(this.id)" value="<?php echo $invoicesLinesDTO->getCustomsNum() ?>">
                            </td>
                        </tr> 
                        <tr>
                            <td><label>Fecha de expedición:</label></td>
                            <td>
                                <input type="text" name="dateCustoms" id="dateCustoms" size="10" class="text-box"  onFocus="javascript: focusOn(this.id);" onBlur="javascript: focusOff(this.id)" value="<?php echo $invoicesLinesDTO->getCustomsDate() ?>">
                            </td>
                        </tr> 
                        <tr>
                            <td><label></label></td>
                            <td></td>
                        </tr>                          
                        <tr>
                            <td align="center" colspan="2">
                                <?php
                                if ($invoicesDTO->getStatus() == 'New' OR $invoicesDTO->getStatus() == 'OnEdition') {
                                ?>                    
                                <input type="button" name="" value="Agregar Info"  class="button" onclick="validateInformation()"/>
                                <?php
                                }
                                ?>

                            </td>
                        </tr>                        
                    </table>
                </fieldset>
            </div>            
        </div>        
    </body>
</html>