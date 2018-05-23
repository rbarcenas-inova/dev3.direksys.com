<?php

//include_once '../../../../trsBase.php';
/*
  Function: ajax_popup_parts_generator

  Genera un popup dinamico para las parts utilizadas en las ordenes.

  Parameters:

  x - The first integer.
  y - The second integer.

  Returns:

  Div con el popup configurado.

  See Also:

  <Divide>
 */

$COMMON_PATH = "../..";

//-- Recepcion de parametros para la construccion del popup

$id_popup = isset($in['id_popup']) ? $in['id_popup'] : $_POST['id_popup'];
$popup_title = isset($in['popup_title']) ? $in['popup_title'] : $_POST['popup_title'];

$first_popup = isset($in['first_popup']) ? $in['first_popup'] : isset($_POST['first_popup']) ? $_POST['first_popup'] : "";
$target_usge = isset($in['target_usage']) ? $in['target_usage'] : isset($_POST['target_usage']) ? $_POST['target_usage'] : "";


if (trim($first_popup) != "") {
    ?>
    <script type="text/javascript">
      
          
        /******* FUNCION ORIGINAL **********
        function ajaxSearchParts(id_popup){
                    
            var ajax_url = "<?php echo $COMMON_PATH ?>" + "/common/php/popup/ajax/ajax_search_parts.php";
                    
            var partID = $("#txtSearchPartID-" + id_popup).val();
            var partModel = $("#txtSearchPartModel-" + id_popup).val();
            var partName = $("#txtSearchPartName-" + id_popup).val();
            var targetUsage = '<?php echo $target_usge; ?>';

            if($.trim(partID).length > 3 || $.trim(partModel).length > 2 || $.trim(partName).length > 2){
                    
                $.ajax({
                    type: 'POST',
                    url: ajax_url,
                    data: {
                        pid: partID,
                        pmodel: partModel,
                        pname : partName,
                        target_usage : targetUsage
                    },
                    success: function(data){
                        $("#" + id_popup + "-table-results").html(data);
                    }
                });
            }else{
                var errores_msg = "La longitud del criterio de busqueda debe ser de al menos 3 caracteres.";
                $.msgbox(errores_msg, {
                    //type : "info",
                    buttons : [
                        {type: "submit", value: "Aceptar"},
                    ]
                });
            }
        }
         */     
               
               
        function ajaxSearchParts(id_popup,target_usage){
                    
            var partID = $("#txtSearchPartID-" + id_popup).val();
            var partModel = $("#txtSearchPartModel-" + id_popup).val();
            var partName = $("#txtSearchPartName-" + id_popup).val();
            var targetUsage = target_usage;

            if($.trim(partID).length > 3 || $.trim(partModel).length > 2 || $.trim(partName).length > 2){
                ajaxGeneratePaginatorParts(id_popup, partID,partModel,partName,targetUsage)
            }else{
                var errores_msg = "La longitud del criterio de busqueda debe ser de al menos 3 caracteres.";
                $.msgbox(errores_msg, {
                    //type : "info",
                    buttons : [
                        {type: "submit", value: "Aceptar"},
                    ]
                });
            }
        }           
               
        function ajaxGeneratePaginatorParts(id_popup, partID,partModel,partName,targetUsage){            
            //--- variables de paginacion
            var results_per_page = 10;
            var id_data_container = '-table-results';
            var id_paginator_container = 'parts-paginator-' + id_popup;  
                
            var ajax_data_url = "<?php echo $COMMON_PATH ?>" + "/common/php/popup/ajax/ajax_search_parts.php";
            var ajax_url = "<?php echo $COMMON_PATH ?>" + "/common/php/popup/ajax/ajax_search_parts_paginator.php";
            $.ajax({
                type: 'POST',
                url: ajax_url,
                data: {
                    pid: partID,
                    pmodel: partModel,
                    pname : partName,
                    idpopup : id_popup,
                    target_usage : targetUsage,
                    data_url : ajax_data_url,
                    paginator_container: id_paginator_container,
                    data_contanier : id_popup + id_data_container,
                    results_per_page : results_per_page
                },
                success: function(data){                    
                    $("#" + id_paginator_container).html(data);
                }
            });
        }        
                
        /*
        function ajaxSelectParts(cusomerID){
            var ajax_url = "<?php echo $COMMON_PATH ?>" + "/common/php/popup/ajax/ajax_select_customer.php";
            $.ajax({
                type: 'POST',
                url: ajax_url,
                data: {
                    cid: cusomerID
                },
                success: function(data){
                    if(data != '')
                        var obJson = eval( "(" + data + ")" );
                    $("#txtCustomerID").val(obJson ['customerID']);  
                    $("#txtCustomerName").val(obJson ['customerName']);  
                    $("#txtCustomerAddress1").val(obJson ['customerAddress1']);  
                    $("#txtCustomerCity").val(obJson ['customerCity']);  
                    $("#txtCustomerState").val(obJson ['customerState']);  
                    $("#txtCustomerZip").val(obJson ['customerZip']);  
                    $("#txtCustomerPhone").val(obJson ['customerPhone']);  
                                   
                    $("#close-button").click();
                    //$("#popup-customers").hide();
                }
            });
        }
         */
    </script>
    <?php
}
?>
<div id="<?php echo $id_popup; ?>" class="popup-container">
    <div class="popup_bar_title">
        <img id="close-button-<?php echo $id_popup; ?>" src="<?php echo $COMMON_PATH; ?>/common/img/popupclose.gif" class="simplemodal-close" style="margin-right: 20px; cursor: pointer;" />
        <?php echo $popup_title; ?>
    </div>
    <div class="popup-table">        
        <div style="width: 100%; min-height: 250px;">
            <div style="width: 100%; margin: 0 auto;">
                <form id="frm-<?php echo $id_popup; ?>">
                    <fieldset>
                        <legend>Search Criteria</legend>
                        <label>Part ID:</label>&nbsp;&nbsp;<input type="text" name="txtSearchPartID-<?php echo $id_popup; ?>" id="txtSearchPartID-<?php echo $id_popup; ?>" class="text-box" /><br>
                        <label>Model:</label>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<input type="text" name="txtSearchPartModel-<?php echo $id_popup; ?>" id="txtSearchPartModel-<?php echo $id_popup; ?>" class="text-box" /><br>
                        <label>Name:</label>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<input type="text" name="txtSearchPartName-<?php echo $id_popup; ?>" id="txtSearchPartName-<?php echo $id_popup; ?>" class="text-box" /><br>
                        <center><input type="button" value="Search" onclick="ajaxSearchParts('<?php echo $id_popup; ?>','<?php echo $target_usge; ?>')"/></center>
                        <input type="reset" id="res-<?php echo $id_popup; ?>" value="Search" style="visibility: hidden; display: none;"/>
                        <input type="hidden" id="hdRelatedPartID-<?php echo $id_popup; ?>" value="" style="visibility: hidden; display: none;"/>
                    </fieldset>
                </form>
            </div>
            <div id="<?php echo $id_popup; ?>-table-results" style="width: 100%; max-height: 155px; overflow: auto;">
                <table width="99%" align="center"  class="List">
                    <tr class="">
                        <td></td>
                        <td></td>
                        <td></td>
                        <td></td>
                        <td></td>
                        <td> - </td>
                    </tr>
                </table>
            </div>
        </div>
    </div>
    <div id="parts-paginator-<?php echo $id_popup; ?>" style="width: 100%; position: relative; float: left;"></div>
</div>