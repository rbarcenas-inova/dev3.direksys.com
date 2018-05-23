<?php

require_once 'BaseDAO.php';
require_once 'InterfaceDAO.php';
require_once 'dto.catalog.AdminLogsDTO.php';

/**
 * Description of dao
 *
 * @author ccedillo
 */
class AdminLogsDAO extends BaseDAO implements InterfaceDAO {

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
        if ($objectDTO instanceof AdminLogsDTO) {

            if ($this->connectDB()) {
                $cadena_sql = "INSERT INTO " . $objectDTO->getTableSource() . " (" . $objectDTO->getStringTableMetadata(TRUE) . ") VALUES ";
                $cadena_sql .="(
                    curdate(), curtime(),
                    " . $this->cleanSqlValue($objectDTO->getMessage()) . ",
                    " . $this->cleanSqlValue($objectDTO->getAction()) . ",
                    " . $this->cleanSqlValue($objectDTO->getType()) . ",
                    " . $this->cleanSqlValue($objectDTO->getTblName()) . ",
                    " . $this->cleanSqlValue($objectDTO->getLogCmd()) . ",
                    " . $this->cleanSqlValue($objectDTO->getID_admin_users()) . ",
                    " . $this->cleanSqlValue($objectDTO->getIP()) . "
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
