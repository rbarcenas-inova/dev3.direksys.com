<?php

require_once 'BaseDAO.php';
require_once 'InterfaceDAO.php';
require_once 'dto.catalog.ReturnsDTO.php';

/**
 * Description
 *
 * @author L.C.I Cesar Cedillo
 */
class ReturnsDAO extends BaseDAO implements InterfaceDAO {

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
        if ($objectDTO instanceof ReturnsDTO) {

            if ($this->connectDB()) {
                $cadena_sql = "INSERT INTO " . $objectDTO->getTableSource() . " (" . $objectDTO->getStringTableMetadata(TRUE) . ") VALUES ";
                $cadena_sql .="(
                    " . $this->cleanSqlValue($objectDTO->getID_orders_products()) . "," . $this->cleanSqlValue($objectDTO->getID_customers()) . ",
                    " . $this->cleanSqlValue($objectDTO->getID_orders()) . "," . $this->cleanSqlValue($objectDTO->getAmount()) . ",
                    " . $this->cleanSqlValue($objectDTO->getType()) . "," . $this->cleanSqlValue($objectDTO->getGeneralpckgcondition()) . ",
                    " . $this->cleanSqlValue($objectDTO->getItemsqty()) . "," . $this->cleanSqlValue($objectDTO->getReceptionnotes()) . ",
                    " . $this->cleanSqlValue($objectDTO->getProdCondition()) . "," . $this->cleanSqlValue($objectDTO->getSerialNumber()) . ",
                    " . $this->cleanSqlValue($objectDTO->getProdnotes()) . "," . $this->cleanSqlValue($objectDTO->getMerAction()) . ",
                    " . $this->cleanSqlValue($objectDTO->getWorkdone()) . "," . $this->cleanSqlValue($objectDTO->getID_products_exchange()) . ",
                    " . $this->cleanSqlValue($objectDTO->getActnotes()) . "," . $this->cleanSqlValue($objectDTO->getQcReturnFees()) . ",
                    " . $this->cleanSqlValue($objectDTO->getQcRestockFees()) . "," . $this->cleanSqlValue($objectDTO->getQcProcessed()) . ",
                    " . $this->cleanSqlValue($objectDTO->getATCReturnFees()) . "," . $this->cleanSqlValue($objectDTO->getATCRestockFees()) . ",
                    " . $this->cleanSqlValue($objectDTO->getATCProcessed()) . "," . $this->cleanSqlValue($objectDTO->getOldShpReturn()) . ",
                    " . $this->cleanSqlValue($objectDTO->getNewShp()) . "," . $this->cleanSqlValue($objectDTO->getAuthBy()) . ",
                    " . $this->cleanSqlValue($objectDTO->getPackingListStatus()) . "," . $this->cleanSqlValue($objectDTO->getStatus()) . ",
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
