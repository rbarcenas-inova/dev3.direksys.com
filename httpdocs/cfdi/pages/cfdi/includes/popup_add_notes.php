<?php
session_start();

$COMMON_PATH = '../../..';

$ID_invoices = isset($_POST['id_invoices']) ? $_POST['id_invoices'] : $_GET['id_invoices'];

$notes_type = isset($_POST['note_type']) ? $_POST['note_type'] : $_GET['note_type'];

//--- obtiene el arreglo con los datos en sesion
$notes = "";
if($notes_type == 'ToPrint'){
    $array_notes = isset($_SESSION['ARRAY_NOTES']) ? $_SESSION['ARRAY_NOTES'] : array();
    
    foreach($array_notes as $a_note){
        if($a_note['type'] == 'ToPrint'){
            $notes = $a_note['notes'];
            break;
        }
    }
}

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
                
                var invoices_notes = $("#txtNotes").val();
                var type = $("#lstNoteType").val();
                
                var errores_validacion = "";                

                if(invoices_notes == ""){
                    errores_validacion +="- Debe agregar una nota.<br>";
                }
                
                if(errores_validacion == ""){
                    saveInfo(invoices_notes, type)
                }else{
                    $.msgbox("Se encontraron los siguientes errores en la informacion:<br>"+errores_validacion, {
                        buttons : [
                            {type: "submit", value: "Aceptar"},
                        ]
                    });                   
                }                    
            }
            
            
            function saveInfo(invoices_notes,type){
                
                var ajax_url = '../ajax/ajax_cfdi_notes_control.php';
                
                $.ajax({
                    type: 'POST',
                    url: ajax_url,
                    data: {
                        notes_type : type,
                        invoice_notes: invoices_notes,
                        action : 'add_note'
                    },
                    success: function(data){                          
                        parent.closeRefreshNotesList();
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
        <div id="popup-upcs" style="width: 99%; height: 99%; border-width: 1px; border-color: #f8f8ff #f8f8ff #f8f8ff #808080; border-style: outset;">
            <div class="popup_bar_title">
                <img id="close-button" src="<?php echo $COMMON_PATH; ?>/common/img/popupclose.gif" class="simplemodal-close" style="margin-right: 20px; cursor: pointer;" onclick="parent.closePopUp()" />
                NOTAS
            </div>
            <div style="font-family: Arial; font-size: 12px; width: 100%; float: left; margin-right: 0px; margin-bottom: 2px; text-align: left; margin-top: 0px;">
                <fieldset>
                    <legend>Informaci&oacute;n de las notas para el comprobante fiscal</legend>
                    <table width="100%" align="center">
                        <tr>
                            <td><label>Tipo:</label></td>
                            <td>                               
                                <select name="lstNoteType" id="lstNoteType"  class="text-box"  onFocus="javascript: focusOn(this.id);" onBlur="javascript: focusOff(this.id)">
                                    <?php
                                    if ($notes_type == 'ToPrint') {
                                        ?>
                                        <option value="ToPrint">Observaciones para Impresi&oacute;n</option>                                    
                                        <?php
                                    } else {
                                        ?>
                                        <option value="Note">Nota</option>
                                        <?php
                                    }
                                    ?>
                                </select>
                            </td>
                        </tr>
                        <tr>
                            <td><label>Texto:</label></td>
                            <td>
                                <textarea name="txtNotes" id="txtNotes" cols="60" rows="2" class="text-box"  onFocus="javascript: focusOn(this.id);" onBlur="javascript: focusOff(this.id)"><?php echo $notes;?></textarea>
                            </td>
                        </tr>                          
                        <tr>
                            <td align="center" colspan="2">
                                <input type="button" name="" value="Agregar Notas"  class="button" onclick="validateInformation()"/>
                            </td>
                        </tr>                        
                    </table>
                </fieldset>
            </div>            
        </div>        
    </body>
</html>