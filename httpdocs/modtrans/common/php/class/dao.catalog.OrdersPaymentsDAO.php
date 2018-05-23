<?php

require_once 'BaseDAO.php';
require_once 'InterfaceDAO.php';
require_once 'dto.catalog.OrdersPaymentsDTO.php';
/**
 * Description
 *
 * @author L.C.I Cesar Cedillo
 */
class OrdersPaymentsDAO extends BaseDAO implements InterfaceDAO {

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

        if ($objectDTO instanceof OrdersPaymentsDTO) {

            if ($this->connectDB()) {
                $cadena_sql = "INSERT INTO " . $objectDTO->getTableSource() . " (" . $objectDTO->getStringTableMetadata(TRUE) . ") VALUES ";
                $cadena_sql .="(
                    " . $this->cleanSqlValue($objectDTO->getID_orders()) . "," . $this->cleanSqlValue($objectDTO->getType()) . ",
                    " . $this->cleanSqlValue($objectDTO->getPmtField1()) . "," . $this->cleanSqlValue($objectDTO->getPmtField2()) . ",
                    " . $this->cleanSqlValue($objectDTO->getPmtField3()) . "," . $this->cleanSqlValue($objectDTO->getPmtField4()) . ",
                    " . $this->cleanSqlValue($objectDTO->getPmtField5()) . "," . $this->cleanSqlValue($objectDTO->getPmtField6()) . ",
                    " . $this->cleanSqlValue($objectDTO->getPmtField7()) . "," . $this->cleanSqlValue($objectDTO->getPmtField8()) . ",
                    " . $this->cleanSqlValue($objectDTO->getPmtField9()) . "," . $this->cleanSqlValue($objectDTO->getAmount()) . ",
                    " . $this->cleanSqlValue($objectDTO->getReason()) . "," . $this->cleanSqlValue($objectDTO->getPaymentDate()) . ",
                    " . $this->cleanSqlValue($objectDTO->getAuthCode()) . "," . $this->cleanSqlValue($objectDTO->getAuthDateTime()) . ",
                    " . $this->cleanSqlValue($objectDTO->getCaptured()) . "," . $this->cleanSqlValue($objectDTO->getCapDate()) . ",
                    " . $this->cleanSqlValue($objectDTO->getPostedDate()) . "," . $this->cleanSqlValue($objectDTO->getStatus()) . ",                                 
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
