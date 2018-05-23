<?php

require_once 'BaseDAO.php';
require_once 'InterfaceDAO.php';
require_once 'dto.catalog.PurchaseOrdersItemsDTO.php';

/**
 * Description
 *
 * @author L.C.I Cesar Cedillo
 */
class PurchaseOrdersItemsDAO extends BaseDAO implements InterfaceDAO {

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
        $this->operationSuccess = FALSE;
        if ($objectDTO instanceof PurchaseOrdersItemsDTO) {

            if ($this->connectDB()) {
                $cadena_sql = "INSERT INTO " . $objectDTO->getTableSource() . " (" . $objectDTO->getStringTableMetadata(TRUE) . ") VALUES ";
                $cadena_sql .="(" .
                        $this->cleanSqlValue($objectDTO->getID_purchaseorders()) . "," . $this->cleanSqlValue($objectDTO->getID_products()) . ",
                    " . $this->cleanSqlValue($objectDTO->getQty()) . "," . $this->cleanSqlValue($objectDTO->getRecieved()) . ",
                    " . $this->cleanSqlValue($objectDTO->getPrice()) . ",
                    curdate(), curtime(),
                    " . $this->cleanSqlValue($objectDTO->getID_admin_users()) . "
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
        $array_result = array();

        if ($objectDTO instanceof PurchaseOrdersItemsDTO) {

            $array_fields = $objectDTO->getFieldList();

            if ($this->connectDB()) {

                $isWherePrev = FALSE;
                $cadena_sql = "SELECT " . $objectDTO->getStringTableMetadata() . " FROM " . $objectDTO->getTableSource();

                if (is_numeric($objectDTO->getID_purchaseorders())) {
                    $cadena_sql .= " WHERE ";
                    $isWherePrev = TRUE;

                    $cadena_sql .= $array_fields[1] . " = " . $this->cleanSqlValue($objectDTO->getID_purchaseorders());
                }

                $cadena_sql .=" ORDER BY $array_fields[0] ASC";

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
                        $idx = 0;
                        $poDTO = new PurchaseOrdersItemsDTO();

                        $poDTO->setID_purchaseorders_items($fila[$array_fields[$idx]]);
                        $poDTO->setID_purchaseorders($fila[$array_fields[++$idx]]);
                        $poDTO->setID_products($fila[$array_fields[++$idx]]);
                        $poDTO->setQty($fila[$array_fields[++$idx]]);
                        $poDTO->setRecieved($fila[$array_fields[++$idx]]);
                        $poDTO->setPrice($fila[$array_fields[++$idx]]);
                        $poDTO->setDate($fila[$array_fields[++$idx]]);
                        $poDTO->setTime($fila[$array_fields[++$idx]]);
                        $poDTO->setID_admin_users($fila[$array_fields[++$idx]]);

                        $array_result[] = $poDTO;
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
        if ($objectDTO instanceof PurchaseOrdersItemsDTO) {
            if ($this->connectDB()) {
                $cadena_sql = "UPDATE " . $objectDTO->getTableSource() . " SET ";
                $comma = FALSE;

                if (!is_null($objectDTO->getRecieved())) {
                    $cadena_sql .= "Received = " . $this->cleanSqlValue($objectDTO->getRecieved());
                    $comma = TRUE;
                }

                if ($comma) {
                    $cadena_sql .= ",";
                }
                $cadena_sql .="Date = CURDATE(), TIME = CURTIME(), ID_admin_users = " . $this->cleanSqlValue($objectDTO->getID_admin_users());
                $cadena_sql .=" WHERE ID_purchaseorders_items = " . $objectDTO->getID_purchaseorders_items();
                
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