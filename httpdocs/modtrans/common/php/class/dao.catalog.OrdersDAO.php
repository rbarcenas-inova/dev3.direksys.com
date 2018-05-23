<?php

require_once 'BaseDAO.php';
require_once 'InterfaceDAO.php';
require_once 'dto.catalog.OrdersDTO.php';

/**
 * Description
 *
 * @author L.C.I Cesar Cedillo
 */
class OrdersDAO extends BaseDAO implements InterfaceDAO {

    function __construct() {
        parent::__construct();
        
        $this->resultSet = NULL;
        $this->numRows = -1;
        $this->operationSuccess = FALSE;
        $this->pagerPage = -1;
        $this->pagerLimit = -1;
    }

    public function deleteRecord(&$objectDTO) {
        
    }

    public function insertRecord(&$objectDTO, $useAutoIncrement = TRUE) {
        $this->operationSuccess = FALSE;
        if ($objectDTO instanceof OrdersDTO) {

            if ($this->connectDB()) {
                $cadena_sql = "INSERT INTO " . $objectDTO->getTableSource() . " (" . $objectDTO->getStringTableMetadata($useAutoIncrement) . ") VALUES ";
                $cadena_sql .="(";
                
                if(!$useAutoIncrement){
                    $cadena_sql .= $this->cleanSqlValue($objectDTO->getID_orders()) . ",";
                }
                
                $cadena_sql .= $this->cleanSqlValue($objectDTO->getID_customers()) . "," . $this->cleanSqlValue($objectDTO->getAddress1()) . ",
                    " . $this->cleanSqlValue($objectDTO->getAddress2()) . "," . $this->cleanSqlValue($objectDTO->getAddress3()) . ",
                    " . $this->cleanSqlValue($objectDTO->getUrbanization()) . "," . $this->cleanSqlValue($objectDTO->getCity()) . ",
                    " . $this->cleanSqlValue($objectDTO->getState()) . "," . $this->cleanSqlValue($objectDTO->getZip()) . ",
                    " . $this->cleanSqlValue($objectDTO->getCountry()) . "," . $this->cleanSqlValue($objectDTO->getShpType()) . ",
                    " . $this->cleanSqlValue($objectDTO->getShpName()) . "," . $this->cleanSqlValue($objectDTO->getShpAddress1()) . ",
                    " . $this->cleanSqlValue($objectDTO->getShpAddress2()) . "," . $this->cleanSqlValue($objectDTO->getShpAddress3()) . ",
                    " . $this->cleanSqlValue($objectDTO->getShpUrbanization()) . "," . $this->cleanSqlValue($objectDTO->getShpCity()) . ",
                    " . $this->cleanSqlValue($objectDTO->getShpState()) . "," . $this->cleanSqlValue($objectDTO->getShpZip()) . ",
                    " . $this->cleanSqlValue($objectDTO->getShpCountry()) . "," . $this->cleanSqlValue($objectDTO->getShpNotes()) . ",
                    " . $this->cleanSqlValue($objectDTO->getOrderNotes()) . "," . $this->cleanSqlValue($objectDTO->getOrderQty()) . ",
                    " . $this->cleanSqlValue($objectDTO->getOrderShp()) . "," . $this->cleanSqlValue($objectDTO->getOrderDisc()) . ",
                    " . $this->cleanSqlValue($objectDTO->getOrderTax()) . "," . $this->cleanSqlValue($objectDTO->getOrderNet()) . ",
                    " . $this->cleanSqlValue($objectDTO->getPostedDate()) . ",
                    " . $this->cleanSqlValue($objectDTO->getID_ordersRelated()) . "," . $this->cleanSqlValue($objectDTO->getRepeatedCustomer()) . ",                    
                    " . $this->cleanSqlValue($objectDTO->getDNIS()) . "," . $this->cleanSqlValue($objectDTO->getID_mediaContracts()) . ",
                    " . $this->cleanSqlValue($objectDTO->getPType()) . "," . $this->cleanSqlValue($objectDTO->getID_warehouses()) . ",
                    " . $this->cleanSqlValue($objectDTO->getLanguage()) . "," . $this->cleanSqlValue($objectDTO->getStatusPrd()) . ",
                    " . $this->cleanSqlValue($objectDTO->getStatusPay()) . "," . $this->cleanSqlValue($objectDTO->getStatus()) . ",
                    curdate(), curtime(),
                    " . $this->cleanSqlValue($objectDTO->getID_adminUsers()) . "
                    )";

                if ($this->executeSQLcommand($cadena_sql) > 0) {
                    $this->operationSuccess = TRUE;
                    $this->lastInsertId = $this->getInsertId();
                }
            }
            $this->disconnectDB();
        }
        return $this->operationSuccess;
    }

    public function selectRecords(&$objectDTO) {
        
    }

    public function updateRecord(&$objectDTO) {
        
    }
    
    public function updateOrderTotals(&$objectDTO){
        $this->operationSuccess = FALSE;
        
        if ($objectDTO instanceof OrdersDTO) {
            if($this->connectDB()){
                
                $cadena_sql = "UPDATE " . $objectDTO->getTableSource() . " SET ";
                
                if($objectDTO->getOrderQty() != 0){
                    $cadena_sql .= "OrderQty=" . $this->cleanSqlValue($objectDTO->getOrderQty()) . ",";
                }
                if($objectDTO->getOrderShp() != 0){
                    $cadena_sql .= "OrderShp=" . $this->cleanSqlValue($objectDTO->getOrderShp()) . ",";
                }
                if($objectDTO->getOrderDisc() != 0){
                    $cadena_sql .= "OrderDisc=" . $this->cleanSqlValue($objectDTO->getOrderDisc()) . ",";
                }
                if($objectDTO->getOrderTax() != 0){
                    $cadena_sql .= "OrderTax=" . $this->cleanSqlValue($objectDTO->getOrderTax()) . ",";
                }
                if($objectDTO->getOrderNet() != 0){
                    $cadena_sql .= "OrderNet=" . $this->cleanSqlValue($objectDTO->getOrderNet()) . ",";
                }
                
                $cadena_sql = substr($cadena_sql, 0, strlen($cadena_sql)-1);                
                $cadena_sql .= " WHERE ID_orders=" . $this->cleanSqlValue($objectDTO->getID_orders());
                
                if($this->executeSQLcommand($cadena_sql) > 0){
                    $this->operationSuccess = TRUE;
                }
            }
            $this->disconnectDB();
        }        
        return $this->operationSuccess;
    }

}

?>