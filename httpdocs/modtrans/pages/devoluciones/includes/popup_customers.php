        <div id="popup-customers" class="popup-container">
            <div class="popup_bar_title">
                <img src="<?php echo $COMMON_PATH; ?>/common/img/popupclose.gif" class="simplemodal-close" style="margin-right: 20px; cursor: pointer;" />
                Customers
            </div>
            <div class="popup-table">                
                <div style="width: 550px; height: 280px;">
                    <div style="width: 540px; margin: 0 auto; position: relative;">
                        <form id="customer-search-criteria">
                        <fieldset>
                            <legend>Search Criteria</legend>
                            <label>Customer ID:</label>&nbsp;&nbsp;<input type="text" name="txtSearchCustID" id="txtSearchCustID" class="text-box" /><br>
                            <label>First Name:</label>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<input type="text" name="txtSearchCustName" id="txtSearchCustName" class="text-box" /><br>
                            <label>Last Name:</label>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<input type="text" name="txtSearchCustLName1" id="txtSearchCustLName1" class="text-box" />&nbsp;&nbsp;
                            <label>Last Name 2:</label>&nbsp;<input type="text" name="txtSearchCustLName2" id="txtSearchCustLName2" class="text-box" /><br>
                            <center><input type="button" value="Search"/></center>
                            <input type="reset" id="resCustomerSearch" value="Search" style="visibility: hidden; display: none;"/>
                        </fieldset>
                        </form>
                    </div>
                    <div id="customer-table-results" style="width: 540px; height: 155px; margin: 0 auto; position: relative; overflow: auto">
                        <table width="99%" align="center"  class="List">
                            <tr class="tableListColumn">
                                <td>ID</td>
                                <td>Name</td>
                                <td>Last Name</td>
                                <td>Addres</td>
                                <td>Phone</td>
                                <td> - </td>
                            </tr>
                        </table>
                    </div>
                    
                </div>
            </div>
        </div>
