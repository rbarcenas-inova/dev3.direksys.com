<?php
/**
 * Description
 *
 * @author L.C.I Cesar Cedillo
 */
global $COMMON_PATH;
?>
<script type="text/javascript">
    function ajaxSearchVendors(){
        
        var vendorID = $("#txtSearchVendorID").val();
        var vendorName = $("#txtSearchVendorName").val();

        if($.trim(vendorID).length > 2 || $.trim(vendorName).length > 2){
            ajaxGeneratePaginatorVendors(vendorID,vendorName);
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
    
    
    
    function ajaxGeneratePaginatorVendors(vendorID,vendorName){
            //--- variables de paginacion
        var results_per_page = 25;
        var id_data_container = 'vendor-table-results';
        var id_paginator_container = 'vendor-paginator';
        
        var ajax_data_url = "<?php echo $COMMON_PATH ?>" + "/common/php/popup/ajax/ajax_search_vendors.php";
        var ajax_url = "<?php echo $COMMON_PATH ?>" + "/common/php/popup/ajax/ajax_search_vendors_paginator.php";
        $.ajax({
            type: 'POST',
            url: ajax_url,
            data: {
                vid: vendorID,
                vname : vendorName,
                data_url : ajax_data_url,
                paginator_container: id_paginator_container,
                data_contanier : id_data_container,
                results_per_page : results_per_page
            },
            beforeSend: function(){
                $("#vendor-loader").show();
                $("#" + id_data_container).hide();
            },
            success: function(data){
                $("#" + id_paginator_container).html(data);
                $("#vendor-loader").hide();
                $("#" + id_data_container).show();

            }
        });
    }
    
    function ajaxSelectVendor(vendorID){
        var ajax_url = "<?php echo $COMMON_PATH ?>" + "/common/php/popup/ajax/ajax_select_vendor.php";
        $.ajax({
            type: 'POST',
            url: ajax_url,
            data: {
                vid: vendorID
            },
            success: function(data){
                if(data != '')
                var obJson = eval( "(" + data + ")" );
                var address = obJson ['vendorZip'] + " " + obJson ['vendorAddress'] + " " + obJson ['vendorCity'] + " " + obJson ['vendorState'] + " " + obJson ['vendorCountry'];
            
                $("#txtVendorID").val(obJson ['vendorID']);  
                $("#txtVendorName").html(obJson ['vendorName']);  
                $("#txtVendorAddress").html(address);                        
                $("#close-button").click();
                //$("#popup-customers").hide();
            }
        });
    }
</script>


<div id="popup-vendors" class="popup-container">
    <div class="popup_bar_title">
        <img id="close-button" src="<?php echo $COMMON_PATH; ?>/common/img/popupclose.gif" class="simplemodal-close" style="margin-right: 20px; cursor: pointer;" />
        Proveedores
    </div>
    <div class="popup-table">        
        <div style="width: 100%; min-height: 250px;">
            <div style="width: 100%; margin: 0 auto;">
                <form id="customer-search-criteria">
                     <fieldset>
                        <legend>Criterio de b&uacute;squeda</legend>
                    <table width="100%">                         
                        <tr>
                            <td><label>Proveedor ID:</label></td>
                            <td colspan="3"><input type="text" name="txtSearchVendorID" id="txtSearchVendorID" class="text-box" /></td>
                        </tr>
                        <tr>
                            <td><label>Nombre:</label></td>
                            <td colspan="3"><input type="text" name="txtSearchVendorName" id="txtSearchVendorName" class="text-box" /><br></td>
                        </tr>
                        <tr>
                            <td colspan="4">
                        <center><input type="button" value="Search" onclick="ajaxSearchVendors()"/></center>
                        <input type="reset" id="resVendorSearch" value="Buscar" style="visibility: hidden; display: none;"/>
                        </td>
                        </tr>
                    </table>
                     </fieldset>
                </form>
            </div>
            <div id="vendor-table-results" style="width: 100%; max-height: 130px; overflow: auto;">
            </div>            
            <div id="vendor-loader" style="width: 100%; max-height: 130px; overflow: auto; text-align: center; display: none;">
                <img src="<?php echo $COMMON_PATH; ?>/common/img/loader.gif" />
            </div>                

        </div>        
    </div>
    <div id="vendor-paginator" style="width: 100%; position: relative; float: left;"></div>
</div>
