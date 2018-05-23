<?php
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
        <link href="<?php echo $COMMON_PATH ?>/common/css/common.css" rel="stylesheet" type="text/css" />
        <link href="<?php echo $COMMON_PATH ?>/common/js/jquery.msgbox.css" type="text/css" rel="stylesheet"/>        
        <link href="<?php echo $COMMON_PATH ?>/common/js/jpaginate/css/style.css" type="text/css" rel="stylesheet" media="screen" />
        <link href="<?php echo $COMMON_PATH ?>/common/js/css/simplemodal.css" type="text/css" rel="stylesheet" media="screen" />
        <script type="text/javascript" src="<?php echo $COMMON_PATH ?>/common/js/jquery-1.6.4.min.js"></script>
        <script type="text/javascript" src="<?php echo $COMMON_PATH ?>/common/js/jquery-ui.min.js"></script>        
        <script type="text/javascript" src="<?php echo $COMMON_PATH ?>/common/js/jquery.msgbox.min.js"></script>
        <script type="text/javascript" src="<?php echo $COMMON_PATH ?>/common/js/validaciones.js"></script>
        <script type="text/javascript" src="<?php echo $COMMON_PATH ?>/common/js/jquery.simplemodal.1.4.3.min.js"></script>

        <script type="text/javascript">
            $(document).ready(function(){
                loadUpcs(<?php echo $idx ?>);
            });
            
            function loadUpcs(index){
                var ajax_url = '../ajax/ajax_order_items_control.php';
                $.ajax({
                    type: 'POST',
                    url: ajax_url,
                    data: {
                        idx: index,                        
                        action : 'show_upcs'
                    },
                    success: function(data){                        
                        data = $.trim(data);
                        $("#txtUpcsList").val(data);                        
                        
                    }
                });
            }
            
            function validateUpcs(idx){
                var txt_list_upcs = $.trim($("#txtUpcsList").val());
                
                if(txt_list_upcs != ""){
                
                    var items_qty = <?php echo $qty; ?>;            
                    var array_upcs = txt_list_upcs.split(" ");
                
                    if(array_upcs.length == items_qty ){
                        saveUpcs(idx)
                    }else{
                        $.msgbox("La cantidad de UPCS no coincide con la cantidad de Items", {
                            buttons : [
                                {type: "submit", value: "Aceptar"},
                            ]
                        });                   
                    }                    
                }
            }
            
            function saveUpcs(idx){
                var ajax_url = '../ajax/ajax_order_items_control.php';
                
                var txt_list_upcs = $.trim($("#txtUpcsList").val());
                
                $.ajax({
                    type: 'POST',
                    url: ajax_url,
                    data: {
                        idx: idx,           
                        upcs_list: txt_list_upcs,
                        action : 'save_upcs'
                    },
                    success: function(data){  
                        //alert(data);
                        parent.closeRefreshList();
                    }
                });
            }            
        </script>
    </head>
    <body>
        <div id="popup-upcs" style="width: 450px; height: 220px; border-width: 1px; border-color: #f8f8ff #f8f8ff #f8f8ff #808080; border-style: outset;">
            <div class="popup_bar_title">
                <img id="close-button" src="<?php echo $COMMON_PATH; ?>/common/img/popupclose.gif" class="simplemodal-close" style="margin-right: 20px; cursor: pointer;" onclick="parent.closePopUp()" />
                ITEM UPCS
            </div>
            <div style="font-family: Arial; font-size: 12px; width: 100%; float: left; margin-right: 0px; margin-bottom: 2px; text-align: left; margin-top: 20px;">
                <fieldset>
                    <legend>UPCS Information</legend>
                    <table width="90%" align="center">
                        <tr>
                            <td style="vertical-align: top;" ><label>UPCS List:</label> </td>
                            <td><textarea name="txtUpcsList" id="txtUpcsList" class="text-box" rows="5" cols="40"></textarea></td>
                        </tr>
                        <tr>
                            <td align="center" colspan="2">
                                <input type="button" name="" value="Guardar UPCS"  class="button" onclick="validateUpcs(<?php echo $idx ?>)"/>
                            </td>
                        </tr>
                    </table>
                </fieldset>
            </div>
        </div>
    </body>
</html>