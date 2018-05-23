<?php
/**
 * Description
 *
 * @author L.C.I Cesar Cedillo
 */
global $COMMON_PATH;
?>
<script type="text/javascript">

    function ajaxSearchPOs(){
        
        var poID = $("#txtSearchPOID").val();
        

        if($.trim(poID).length > 0){
            ajaxGeneratePaginatorPOs(poID);
        }else{
            var errores_msg = "Debe establecer el criterio de busqueda.";
            $.msgbox(errores_msg, {
                //type : "info",
                buttons : [
                    {type: "submit", value: "Aceptar"},
                ]
            });
        }
    }
       
    
    function ajaxGeneratePaginatorPOs(poID){
        //--- variables de paginacion
        var results_per_page = 25;
        var id_data_container = 'po-table-results';
        var id_paginator_container = 'po-paginator';
        var id_loader = 'po-loader';
        
        var ajax_data_url = "<?php echo $COMMON_PATH ?>" + "/common/php/popup/ajax/ajax_search_pos.php";
        var ajax_url = "<?php echo $COMMON_PATH ?>" + "/common/php/popup/ajax/ajax_search_pos_paginator.php";

        $.ajax({
            type: 'POST',
            url: ajax_url,
            data: {
                poid: poID,                
                data_url : ajax_data_url,
                paginator_container: id_paginator_container,
                data_contanier : id_data_container,
                results_per_page : results_per_page
            },
            beforeSend: function(){
                $("#" + id_loader).show();
                $("#" + id_data_container).hide();
            },
            success: function(data){
                $("#" + id_paginator_container).html(data);
                $("#" + id_loader).hide();
                $("#" + id_data_container).show();

            }
        });
    }
    
</script>


<div id="popup-pos" class="popup-container">
    <div class="popup_bar_title">
        <img id="close-button" src="<?php echo $COMMON_PATH; ?>/common/img/popupclose.gif" class="simplemodal-close" style="margin-right: 20px; cursor: pointer;" />
        Ordenes de Compra
    </div>
    <div class="popup-table">        
        <div style="width: 100%; min-height: 250px;">
            <div style="width: 100%; margin: 0 auto;">
                <form id="po-search-criteria">
                    <fieldset>
                        <legend>Criterio de b&uacute;squeda</legend>
                        <table width="100%">                         
                            <tr>
                                <td><label>Orden de Compra ID:</label></td>
                                <td colspan="3"><input type="text" name="txtSearchPOID" id="txtSearchPOID" class="text-box" /></td>
                            </tr>
                            <tr>
                                <td colspan="4">
                            <center><input type="button" value="Search" onclick="ajaxSearchPOs()"/></center>
                            <input type="reset" id="resPOSearch" value="Buscar" style="visibility: hidden; display: none;"/>
                            </td>
                            </tr>
                        </table>
                    </fieldset>
                </form>
            </div>
            <div id="po-table-results" style="width: 100%; max-height: 130px; overflow: auto;">
            </div>            
            <div id="po-loader" style="width: 100%; max-height: 130px; overflow: auto; text-align: center; display: none;">
                <img src="<?php echo $COMMON_PATH; ?>/common/img/loader.gif" />
            </div>                

        </div>        
    </div>
    <div id="po-paginator" style="width: 100%; position: relative; float: left;"></div>
</div>