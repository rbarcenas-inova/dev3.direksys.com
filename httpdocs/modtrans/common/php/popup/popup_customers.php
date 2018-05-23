<?php
/**
 * Description
 *
 * @author L.C.I Cesar Cedillo
 */
global $COMMON_PATH;
?>
<script type="text/javascript">
    

    
    /****** FUNCTION ORIGINAL *******
    function ajaxSearchCustomers(){
        
        var ajax_url = "<?php echo $COMMON_PATH ?>" + "/common/php/popup/ajax/ajax_search_customers.php";
        
        var custID = $("#txtSearchCustID").val();
        var custName = $("#txtSearchCustName").val();
        var custLName1 = $("#txtSearchCustLName1").val();
        var custLName2 = $("#txtSearchCustLName2").val();

        if($.trim(custID).length > 2 || $.trim(custName).length > 2 || $.trim(custLName1).length > 2 || $.trim(custLName2).length > 2){
        
            $.ajax({
                type: 'POST',
                url: ajax_url,
                data: {
                    cid: custID,
                    cname : custName,
                    clname1 : custLName1,
                    clname2 : custLName2,
                    results_per_page : results_per_page,
                    page : 1
                },
                success: function(data){
                    if(data != ''){
                        //$("#customer-table-results").html(data);
                        //$("#" + id_data_container).html(data);
                        ajaxGeneratePaginator(custID,custName,custLName1,custLName2);
                    }
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
   
   
    function ajaxSearchCustomers(){         
        var custID = $("#txtSearchCustID").val();
        var custName = $("#txtSearchCustName").val();
        var custLName1 = $("#txtSearchCustLName1").val();
        var custLName2 = $("#txtSearchCustLName2").val();

        if($.trim(custID).length > 2 || $.trim(custName).length > 2 || $.trim(custLName1).length > 2 || $.trim(custLName2).length > 2){
            ajaxGeneratePaginatorCustomer(custID,custName,custLName1,custLName2);            
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
    
    
    
    function ajaxGeneratePaginatorCustomer(custID,custName,custLName1,custLName2){  
            //--- variables de paginacion
        var results_per_page = 25;
        var id_data_container = 'customer-table-results';
        var id_paginator_container = 'customer-paginator';
        
        var ajax_data_url = "<?php echo $COMMON_PATH ?>" + "/common/php/popup/ajax/ajax_search_customers.php";
        var ajax_url = "<?php echo $COMMON_PATH ?>" + "/common/php/popup/ajax/ajax_search_customers_paginator.php";
        $.ajax({
            type: 'POST',
            url: ajax_url,
            data: {
                cid: custID,
                cname : custName,
                clname1 : custLName1,
                clname2 : custLName2,
                data_url : ajax_data_url,
                paginator_container: id_paginator_container,
                data_contanier : id_data_container,
                results_per_page : results_per_page
            },
            beforeSend: function(){
                $("#customer-loader").show();
                $("#customer-table-results").hide();                
            },
            success: function(data){
                $("#" + id_paginator_container).html(data);
                $("#customer-loader").hide();
                $("#customer-table-results").show();                

            }
        });
    }
    
    function ajaxSelectCustomer(cusomerID){
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
                var nombreCompleto = $("<span/>").html(obJson ['customerName']).text();
                var address1 = $("<span/>").html(obJson ['customerAddress1']).text();
                var address2 = $("<span/>").html(obJson ['customerAddress2']).text();
                var address3 = $("<span/>").html(obJson ['customerAddress3']).text();
                var urbanization = $("<span/>").html(obJson ['customerUrbanization']).text();
                var city = $("<span/>").html(obJson ['customerCity']).text();
                var state = $("<span/>").html(obJson ['customerState']).text();
                var country = $("<span/>").html(obJson ['customerCountry']).text();
                $("#txtCustomerID").val(obJson ['customerID']);                  
                $("#txtCustomerName").val(nombreCompleto);
                $("#txtCustomerAddress1").val(address1);  
                $("#txtCustomerAddress2").val(address2);  
                $("#txtCustomerAddress3").val(address3);  
                $("#txtCustomerUrbanization").val(urbanization);  
                
                $("#txtCustomerCity").val(city);  
                $("#txtCustomerState").val(state);  
                $("#txtCustomerCountry").val(country); 
                $("#txtCustomerZip").val(obJson ['customerZip']);  
                $("#txtCustomerPhone").val(obJson ['customerPhone']);  
                
                $("#close-button").click();
                /*
                $("#txtCustomerName").val(obJson ['customerName']);  
                $("#txtCustomerAddress1").val(obJson ['customerAddress1']);  
                $("#txtCustomerAddress2").val(obJson ['customerAddress2']);  
                $("#txtCustomerAddress3").val(obJson ['customerAddress3']);  
                $("#txtCustomerUrbanization").val(obJson ['customerUrbanization']);  
                
                $("#txtCustomerCity").val(obJson ['customerCity']);  
                $("#txtCustomerState").val(obJson ['customerState']);  
                */

                /*
                $("#txtCustomerCountry").val(obJson ['customerCountry']);  
                */     

                //$("#popup-customers").hide();
            }
        });
    }
</script>


<div id="popup-customers" class="popup-container">
    <div class="popup_bar_title">
        <img id="close-button" src="<?php echo $COMMON_PATH; ?>/common/img/popupclose.gif" class="simplemodal-close" style="margin-right: 20px; cursor: pointer;" />
        Clientes
    </div>
    <div class="popup-table">        
        <div style="width: 100%; min-height: 250px;">
            <div style="width: 100%; margin: 0 auto;">
                <form id="customer-search-criteria">
                     <fieldset>
                        <legend>Criterio de b&uacute;squeda</legend>
                    <table width="100%">                         
                        <tr style="display: none;">
                            <td><label style="visibility: hidden">Customer ID:</label></td>
                            <td><input type="text" style="visibility: hidden" name="txtSearchCustID" id="txtSearchCustID" class="text-box" /></td>
                        </tr>
                        <tr>
                            <td><label>Nombre:</label></td>
                            <td colspan="3"><input type="text" name="txtSearchCustName" id="txtSearchCustName" class="text-box" /><br></td>
                        </tr>
                        <tr>
                            <td><label>Apellido Paterno:</label></td>
                            <td><input type="text" name="txtSearchCustLName1" id="txtSearchCustLName1" class="text-box" /></td>
                            <td><label>Apellido Materno:</label></td>
                            <td><input type="text" name="txtSearchCustLName2" id="txtSearchCustLName2" class="text-box" /></td>
                        </tr>
                        <tr>
                            <td colspan="4">
                        <center><input type="button" value="Search" onclick="ajaxSearchCustomers()"/></center>
                        <input type="reset" id="resCustomerSearch" value="Buscar" style="visibility: hidden; display: none;"/>
                        </td>
                        </tr>
                    </table>
                     </fieldset>
                </form>
            </div>
            <div id="customer-table-results" style="width: 100%; max-height: 130px; overflow: auto;">
            </div>            
            <div id="customer-loader" style="width: 100%; max-height: 130px; overflow: auto; text-align: center; display: none;">
                <img src="<?php echo $COMMON_PATH; ?>/common/img/loader.gif" />
            </div>                

        </div>        
    </div>
    <div id="customer-paginator" style="width: 100%; position: relative; float: left;"></div>
</div>
