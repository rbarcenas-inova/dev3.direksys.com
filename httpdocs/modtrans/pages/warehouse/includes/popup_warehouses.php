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
        
        <script type="text/javascript" src="<?php echo $COMMON_PATH ?>/common/js/jquery-1.6.4.min.js"></script>
        <script type="text/javascript" src="<?php echo $COMMON_PATH ?>/common/js/jquery-ui.min.js"></script>        
        <script type="text/javascript" src="<?php echo $COMMON_PATH ?>/common/js/jquery.msgbox.min.js"></script>
        <script type="text/javascript" src="<?php echo $COMMON_PATH ?>/common/js/validaciones.js"></script>
        

        <script type="text/javascript">
            $(document).ready(function(){
                loadWarehouses(<?php echo $idx ?>);
            });
            
            function loadWarehouses(index){
                var ajax_url = '../ajax/ajax_order_items_control_undelivered.php';
                $.ajax({
                    type: 'POST',
                    url: ajax_url,
                    data: {
                        idx: index,                        
                        action : 'show_warehouse'
                    },
                    success: function(data){                                                
                        $("#lst-warehouses").html(data);                        
                    }
                });
            }
            
            function validateWarehouse(idx){
                var id_warehouse = $("#lstDestWarehouse").val();
                
                if(id_warehouse != ""){
                        saveWarehouse(idx)
                    }else{
                        $.msgbox("Debe seleccionar un almacen de destino para el retorno de la mercancia.", {
                            buttons : [
                                {type: "submit", value: "Aceptar"},
                            ]
                        });                   
                    }                    
                }
            
            
            function saveWarehouse(idx){
                var ajax_url = '../ajax/ajax_order_items_control_undelivered.php';
                
                var id_warehouse = $("#lstDestWarehouse").val();
                
                $.ajax({
                    type: 'POST',
                    url: ajax_url,
                    data: {
                        idx: idx,           
                        id_wh_dest: id_warehouse,
                        action : 'save_warehouse'
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
        <div id="popup-upcs" style="width: 550px; height: 220px; border-width: 1px; border-color: #f8f8ff #f8f8ff #f8f8ff #808080; border-style: outset;">
            <div class="popup_bar_title">
                <img id="close-button" src="<?php echo $COMMON_PATH; ?>/common/img/popupclose.gif" class="simplemodal-close" style="margin-right: 20px; cursor: pointer;" onclick="parent.closePopUp()" />
                ALMACENES
            </div>
            <div style="font-family: Arial; font-size: 12px; width: 100%; float: left; margin-right: 0px; margin-bottom: 2px; text-align: left; margin-top: 20px;">
                <fieldset>
                    <legend>Lista de Almacenes para Retorno</legend>
                    <table width="100%" align="center">
                        <tr>
                            <td style="vertical-align: top;" ><label>Almac&eacute;n Destino:</label></td>
                            <td>
                                <div id="lst-warehouses">
                                    <select name="lstDestWarehouse" id="lstDestWarehouse" class="text-box">
                                        <option value="">--- Seleccione ---</option>
                                    </select>
                                </div>
                            </td>
                        </tr>
                        <tr>
                            <td colspan="2">&nbsp;<br></td>
                        </tr>
                        <tr>
                            <td align="center" colspan="2">
                                <input type="button" name="" value="Guardar Almac&eacute;n"  class="button" onclick="validateWarehouse(<?php echo $idx ?>)"/>
                            </td>
                        </tr>
                    </table>
                </fieldset>
            </div>
        </div>
    </body>
</html>