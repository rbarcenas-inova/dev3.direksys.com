<?php
$COMMON_PATH = "../../..";
require_once $COMMON_PATH . '/trsBase.php';
require_once $COMMON_PATH . '/common/php/class/db/DbHandler.php';
require_once $COMMON_PATH . '/common/php/class/dto.common.SerialDTO.php';
require_once $COMMON_PATH . '/common/php/class/dao.common.SerialDAO.php';

session_start();

$serialDAO = new InvoicesSerialDAO();
$serialDTO = new InvoicesSerialDTO();
$serialDTO->setVname('IS');
$vector_invoice = $serialDAO->selectRecords($serialDTO);
$serialDTO = $vector_invoice[0];
$ISerial=$serialDTO->getVvalue();
$serialDAO = new InvoicesSerialDAO();
$serialDTO = new InvoicesSerialDTO();
$serialDTO->setVname('IN');
$vector_invoice = $serialDAO->selectRecords($serialDTO);
$serialDTO = $vector_invoice[0];
$INumber=$serialDTO->getVvalue();

$serialDAO = new InvoicesSerialDAO();
$serialDTO = new InvoicesSerialDTO();
$serialDTO->setVname('CS');
$vector_invoice = $serialDAO->selectRecords($serialDTO);
$serialDTO = $vector_invoice[0];
$CSerial=$serialDTO->getVvalue();
$serialDAO = new InvoicesSerialDAO();
$serialDTO = new InvoicesSerialDTO();
$serialDTO->setVname('CN');
$vector_invoice = $serialDAO->selectRecords($serialDTO);
$serialDTO = $vector_invoice[0];
$CNumber=$serialDTO->getVvalue();

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
                
                var ISeries = $("#ISerie").val();
                var INumbers = $("#INumber").val();
                var CSeries = $("#CSerie").val();
                var CNumbers = $("#CNumber").val();
                
                var errores_validacion = ""; 

                if(ISeries == ""){
                    errores_validacion +="- Debe ingresar una Serie valida.<br>";
                }             
                if(INumbers == ""){
                    errores_validacion +="- Debe ingresar un Folio inicial valido.<br>";
                }
                if(CSeries == ""){
                    errores_validacion +="- Debe ingresar una Serie valida.<br>";
                }             
                if(CNumbers == ""){
                    errores_validacion +="- Debe ingresar un Folio inicial valido.<br>";
                }

                if(errores_validacion == ""){
                    saveInfo(ISeries, INumbers, CSeries, CNumbers)
                }else{
                    $.msgbox("Se encontraron los siguientes errores en la informacion:<br>"+errores_validacion, {
                        buttons : [
                            {type: "submit", value: "Aceptar"},
                        ]
                    });                   
                }                    
            }
            
            
            function saveInfo(ISeries,INumbers,CSeries,CNumbers){
                
                var ajax_url = '../process/cfdi_edit_save.php';
               
                $.ajax({
                    type: 'POST',
                    url: ajax_url,
                    data: {
                        ISeries : ISeries,
                        INumbers: INumbers, 
                        CSeries : CSeries,
                        CNumbers: CNumbers, 
                        action : 'save_series'
                    },
                    success: function(data){
                        parent.closePopUp();
                    }
                });                
            }
                        
        </script>
    </head>
    <body>        
        <div id="popup-upcs" style="width: 99%; height: 99%; border-width: 1px; border-color: #f8f8ff #f8f8ff #f8f8ff #808080; border-style: outset;">
            <div class="popup_bar_title">
                <img id="close-button" src="<?php echo $COMMON_PATH; ?>/common/img/popupclose.gif" class="simplemodal-close" style="margin-right: 20px; cursor: pointer;" onclick="parent.closePopUp()" />
                Series / Folios para facturación
            </div>
            <div style="font-family: Arial; font-size: 12px; width: 100%; float: left; margin-right: 0px; margin-bottom: 2px; text-align: left; margin-top: 0px;">
                <fieldset>
                    <legend>Facturas - Ingreso</legend>
                    <table width="100%" align="center">
                        <tr>
                            <td><label>Serie:</label></td>
                            <td>                                
                                <input type="text" name="ISerie" id="ISerie" size="10" class="text-box"  onFocus="javascript: focusOn(this.id);" onBlur="javascript: focusOff(this.id)" value="<?php echo $ISerial; ?>">
                            </td>
                        </tr>

                        <tr>
                            <td><label>Folio:</label></td>
                            <td>                                
                                <input type="text" name="INumber" id="INumber" size="10" class="text-box"  onFocus="javascript: focusOn(this.id);" onBlur="javascript: focusOff(this.id)" value="<?php echo $INumber; ?>">
                            </td>
                        </tr>                       
                    </table>
                </fieldset>

                <fieldset>
                    <legend>Notas de Crédito - Egreso</legend>
                    <table width="100%" align="center">
                        <tr>
                            <td><label>Serie:</label></td>
                            <td>                                
                                <input type="text" name="CSerie" id="CSerie" size="10" class="text-box"  onFocus="javascript: focusOn(this.id);" onBlur="javascript: focusOff(this.id)" value="<?php echo $CSerial; ?>">
                            </td>
                        </tr>

                        <tr>
                            <td><label>Folio:</label></td>
                            <td>                                
                                <input type="text" name="CNumber" id="CNumber" size="10" class="text-box"  onFocus="javascript: focusOn(this.id);" onBlur="javascript: focusOff(this.id)" value="<?php echo $CNumber; ?>">
                            </td>
                        </tr>                       
                    </table>
                </fieldset>
                <table width="100%" align="center">                                                 
                    <tr>
                        <td align="center" colspan="2">                    
                            <input type="button" name="Send" value="Actualizar Datos"  class="button" onclick="javascript: validateInformation();"/>
                        </td>
                    </tr>                        
                </table>
            </div>            
        </div>        
    </body>
</html>