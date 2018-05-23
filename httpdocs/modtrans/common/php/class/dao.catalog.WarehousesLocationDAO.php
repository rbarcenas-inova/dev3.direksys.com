<?php

require_once 'BaseDAO.php';
require_once 'InterfaceDAO.php';
require_once 'dto.catalog.WarehousesLocationDTO.php';

/**
 * Description
 *
 * @author L.C.I Cesar Cedillo
 */
class WarehousesLocationDAO extends BaseDAO implements InterfaceDAO {

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
        if ($objectDTO instanceof WarehousesLocationDTO) {

            if ($this->connectDB()) {
                
                $cadena_sql = "INSERT INTO " . $objectDTO->getTableSource() . " (" . $objectDTO->getStringTableMetadata(TRUE) . ") VALUES (
                    " . $this->cleanSqlValue($objectDTO->getIdWarehouses()) . "," . $this->cleanSqlValue($objectDTO->getIdProducts()) . ",
                    " . $this->cleanSqlValue($objectDTO->getLocation()) . "," . $this->cleanSqlValue($objectDTO->getQuantity()) . ",
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
        
    }

    public function updateRecord(&$objectDTO) {
        
    }

}

?>