<?php

require_once 'BaseDAO.php';
require_once 'InterfaceDAO.php';
require_once 'dto.catalog.BillsDTO.php';

/**
 * Description
 *
 * @author L.C.I Cesar Cedillo
 */
class BillsDAO extends BaseDAO implements InterfaceDAO {

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
        if ($objectDTO instanceof BillsDTO) {

            if ($this->connectDB()) {
                $cadena_sql = "INSERT INTO " . $objectDTO->getTableSource() . " (" . $objectDTO->getStringTableMetadata($useAutoIncrement) . ") VALUES ";
                $cadena_sql .="(";

                if (!$useAutoIncrement) {
                    $cadena_sql .= $this->cleanSqlValue($objectDTO->getID_bills()) . ",";
                }

                $cadena_sql .= $this->cleanSqlValue($objectDTO->getID_vendors()) . "," . $this->cleanSqlValue($objectDTO->getType()) . ",
                    " . $this->cleanSqlValue($objectDTO->getCurrency()) . "," . $this->cleanSqlValue($objectDTO->getAmount()) . ",
                    " . $this->cleanSqlValue($objectDTO->getTerms()) . "," . $this->cleanSqlValue($objectDTO->getMemo()) . ",
                    " . $this->cleanSqlValue($objectDTO->getBillDate()) . "," . $this->cleanSqlValue($objectDTO->getDueDate()) . ",
                    " . $this->cleanSqlValue($objectDTO->getAuthBy()) . "," . $this->cleanSqlValue($objectDTO->getStatus()) . ",
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
