<?php

require_once 'BaseDAO.php';
require_once 'InterfaceDAO.php';
require_once 'dto.catalog.InvoicesLinesDTO.php';

class InvoicesLinesDAO extends BaseDAO implements InterfaceDAO {

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

    public function insertRecord(&$objectDTO) {
        
    }

    public function selectRecords(&$objectDTO) {
        $array_result = array();
        if ($objectDTO instanceof InvoicesLinesDTO) {
            if ($this->connectDB()) {
                $cadena_sql = "SELECT * FROM " . $objectDTO->getTableSource() . " WHERE  1 ";

                if (!is_null($objectDTO->getID_invoices()) && $objectDTO->getID_invoices() > 0) {
                    $cadena_sql .="AND ID_invoices = " . $this->cleanSqlValue($objectDTO->getID_invoices());
                }

                if (!is_null($objectDTO->getID_invoices_lines()) && $objectDTO->getID_invoices_lines() > 0) {
                    $cadena_sql .="AND ID_invoices_lines = " . $this->cleanSqlValue($objectDTO->getID_invoices_lines());
                }

                $cadena_sql .= " ORDER BY ID_invoices ASC, line_num ASC ";

                if ($this->pagerPage > -1 && $this->pagerLimit > -1) {
                    $cadena_sql .= " LIMIT " . $this->pagerPage . "," . $this->pagerLimit;
                }

                $this->selectSQLcommand($cadena_sql);

                if ($this->onlyCountRows) {
                    $this->onlyCountRows = FALSE;
                    $this->disconnectDB();
                    return;
                }

                if ($this->numRows > 0) {
                    while ($fila = $this->fetchAssocNextRow()) {
                        $invoicesLinesDTO = new InvoicesLinesDTO();

                        $invoicesLinesDTO->setID_invoices_lines($fila['ID_invoices_lines']);
                        $invoicesLinesDTO->setID_invoices($fila['ID_invoices']);
                        $invoicesLinesDTO->setID_orders($fila['ID_orders']);
                        $invoicesLinesDTO->setID_creditmemos($fila['ID_creditmemos']);
                        $invoicesLinesDTO->setID_orders_products($fila['ID_orders_products']);
                        $invoicesLinesDTO->setLineNum($fila['line_num']);
                        $invoicesLinesDTO->setQuantity($fila['quantity']);
                        $invoicesLinesDTO->setMeasuringUnit($fila['measuring_unit']);
                        $invoicesLinesDTO->setReferenceID($fila['reference_id']);
                        $invoicesLinesDTO->setDescription($fila['description']);
                        $invoicesLinesDTO->setUnitPrice($fila['unit_price']);
                        $invoicesLinesDTO->setAmount($fila['amount']);
                        $invoicesLinesDTO->setTax($fila['tax']);
                        $invoicesLinesDTO->setTaxType($fila['tax_type']);
                        $invoicesLinesDTO->setTaxName($fila['tax_name']);
                        $invoicesLinesDTO->setTaxRate($fila['tax_rate']);
                        $invoicesLinesDTO->setDiscount($fila['discount']);
                        $invoicesLinesDTO->setCustomsGLN($fila['customs_gln']);
                        $invoicesLinesDTO->setCustomsName($fila['customs_name']);
                        $invoicesLinesDTO->setCustomsNum($fila['customs_num']);
                        $invoicesLinesDTO->setCustomsDate($fila['customs_date']);
                        $invoicesLinesDTO->setIdSku($fila['ID_sku']);
                        $invoicesLinesDTO->setIdSkuAlias($fila['ID_sku_alias']);
                        $invoicesLinesDTO->setSize($fila['size']);
                        $invoicesLinesDTO->setPackingType($fila['packing_type']);
                        $invoicesLinesDTO->setPackingUnit($fila['packing_unit']);
                        $invoicesLinesDTO->setUPC($fila['UPC']);
                        $invoicesLinesDTO->setDate($fila['Date']);
                        $invoicesLinesDTO->setTime($fila['Time']);
                        $invoicesLinesDTO->setID_admin_users($fila['ID_admin_users']);

                        $array_result[] = $invoicesLinesDTO;
                    }
                }
                $this->dbFreeResult();
            }
            $this->disconnectDB();
        }
        return $array_result;
    }

    public function updateRecord(&$objectDTO) {
        $this->operationSuccess = FALSE;
        if ($objectDTO instanceof InvoicesLinesDTO) {
            if ($this->connectDB()) {

                $needAnd = FALSE;

                $cadena_sql = "UPDATE " . $objectDTO->getTableSource() . " SET ";

                if (!is_null($objectDTO->getCustomsGLN())) {
                    $cadena_sql .= "customs_gln = " . $this->cleanSqlValue($objectDTO->getCustomsGLN());
                    $needAnd = TRUE;
                }

                if (!is_null($objectDTO->getCustomsName())) {
                    if ($needAnd) {
                        $cadena_sql .= ", ";
                    }                    
                    $cadena_sql .= "customs_name = " . $this->cleanSqlValue($objectDTO->getCustomsName());
                    $needAnd = TRUE;
                }
                
                if (!is_null($objectDTO->getCustomsNum())) {
                    if ($needAnd) {
                        $cadena_sql .= ", ";
                    }                    
                    $cadena_sql .= "customs_num = " . $this->cleanSqlValue($objectDTO->getCustomsNum());
                    $needAnd = TRUE;
                }
                
                if (trim($objectDTO->getCustomsDate()) != '') {
                    if ($needAnd) {
                        $cadena_sql .= ", ";
                    }                    
                    $cadena_sql .= "customs_date = " . $this->cleanSqlValue($objectDTO->getCustomsDate());
                    $needAnd = TRUE;
                }

                if (trim($objectDTO->getIdSku()) != '') {
                    if ($needAnd) {
                        $cadena_sql .= ", ";
                    }                    
                    $cadena_sql .= "ID_sku = " . $this->cleanSqlValue($objectDTO->getIdSku());
                    $needAnd = TRUE;
                }
                if (trim($objectDTO->getIdSkuAlias()) != '') {
                    if ($needAnd) {
                        $cadena_sql .= ", ";
                    }                    
                    $cadena_sql .= "ID_sku_alias = " . $this->cleanSqlValue($objectDTO->getIdSkuAlias());
                    $needAnd = TRUE;
                }
                if (trim($objectDTO->getUPC()) != '') {
                    if ($needAnd) {
                        $cadena_sql .= ", ";
                    }                    
                    $cadena_sql .= "UPC = " . $this->cleanSqlValue($objectDTO->getUPC());
                    $needAnd = TRUE;
                }

                /*
                if ($needAnd) {
                    $cadena_sql .= ", ";
                }
                $cadena_sql .= " Date = CURDATE(), Time = CURTIME(), ID_admin_users = " . $this->cleanSqlValue($objectDTO->getID_admin_users());
                */
                
                $cadena_sql .= " WHERE ";
                if ($objectDTO->getID_invoices_lines() > 0) {
                    $cadena_sql .= "ID_invoices_lines = " . $this->cleanSqlValue($objectDTO->getID_invoices_lines());
                }


                if ($this->executeSQLcommand($cadena_sql) >= 0) {
                    $this->operationSuccess = TRUE;
                }
            }
            $this->disconnectDB();
        }
        return $this->operationSuccess;
    }

    public function duplicateRecord(&$objectDTO) {
        $this->operationSuccess = FALSE;

        if ($objectDTO instanceof InvoicesLinesDTO) {
            if ($this->connectDB()) {

                if (!is_null($objectDTO->getID_invoices()) && $objectDTO->getID_invoices() > 0) {
                    $cadena_sql = "INSERT INTO " . $objectDTO->getTableSource() . " (" . $objectDTO->getStringTableMetadata(TRUE) . ") 
                    SELECT " . $this->cleanSqlValue($objectDTO->getExtraID_field()) . ", ID_orders, ID_creditmemos, ID_orders_products, line_num, quantity, measuring_unit, reference_id, description, unit_price, amount, tax, tax_type, tax_name, tax_rate, discount, customs_gln, customs_name, customs_num, customs_date, ID_sku, ID_sku_alias, size, packing_type, packing_unit, UPC, CURDATE(), CURTIME(), " . $objectDTO->getID_admin_users() . " FROM " . $objectDTO->getTableSource() . " WHERE ";

                    if (!is_null($objectDTO->getID_invoices()) && $objectDTO->getID_invoices() > 0) {
                        $cadena_sql .= "ID_invoices = " . $this->cleanSqlValue($objectDTO->getID_invoices());
                    }

                    if ($this->executeSQLcommand($cadena_sql) > 0) {
                        $this->operationSuccess = TRUE;
                        $this->lastInsertId = $this->getInsertId();
                    }
                }
            }
            $this->disconnectDB();
        }

        return $this->operationSuccess;
    }

    function selcectOrdersFromInvoce(&$objectDTO){
        $array_result = array();
        if ($objectDTO instanceof InvoicesLinesDTO) {
            if($this->connectDB()){
                $cadena_sql = "SELECT T0.ID_orders FROM " . $objectDTO->getTableSource() . " T0 WHERE 1 AND ";
                   
                if (!is_null($objectDTO->getID_invoices()) && $objectDTO->getID_invoices() > 0) {
                    $cadena_sql .=" T0.ID_invoices = " . $this->cleanSqlValue($objectDTO->getID_invoices());
                }
                
                $cadena_sql .= " GROUP BY T0.ID_orders";
                
                $this->selectSQLcommand($cadena_sql);
                
                if($this->numRows > 0){
                    while ($fila = $this->fetchAssocNextRow()) {
                        $invoicesLinesDTO = new InvoicesLinesDTO();
                        
                        $invoicesLinesDTO->setID_invoices($objectDTO->getID_invoices());
                        $invoicesLinesDTO->setID_orders($fila['ID_orders']);
                        
                        $array_result[] = $invoicesLinesDTO;
                    }
                }
            }
            $this->disconnectDB();
        }  
        return $array_result;
    }

    function selectCreditmemoFromInvoce(&$objectDTO){
        $array_result = array();
        if ($objectDTO instanceof InvoicesLinesDTO) {
            if($this->connectDB()){
                $cadena_sql = "SELECT T0.ID_creditmemos FROM " . $objectDTO->getTableSource() . " T0 WHERE 1 AND ";
                   
                if (!is_null($objectDTO->getID_invoices()) && $objectDTO->getID_invoices() > 0) {
                    $cadena_sql .=" T0.ID_invoices = " . $this->cleanSqlValue($objectDTO->getID_invoices());
                }
                
                $cadena_sql .= " GROUP BY T0.ID_invoices";
                
                $this->selectSQLcommand($cadena_sql);
                
                if($this->numRows > 0){
                    while ($fila = $this->fetchAssocNextRow()) {
                        $invoicesLinesDTO = new InvoicesLinesDTO();
                        
                        $invoicesLinesDTO->setID_invoices($objectDTO->getID_invoices());
                        $invoicesLinesDTO->setID_creditmemos($fila['ID_creditmemos']);
                        
                        $array_result[] = $invoicesLinesDTO;
                    }
                }
            }
            $this->disconnectDB();
        }   
        return $array_result;
    }

}

?>
