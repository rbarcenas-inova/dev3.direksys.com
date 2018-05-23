<?php

require_once 'BaseDAO.php';
require_once 'InterfaceDAO.php';
require_once 'dto.catalog.PurchaseOrdersDTO.php';

/**
 * Description
 *
 * @author L.C.I Cesar Cedillo
 */
class PurchaseOrdersDAO extends BaseDAO implements InterfaceDAO {

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
        if ($objectDTO instanceof PurchaseOrdersDTO) {

            if ($this->connectDB()) {
                $cadena_sql = "INSERT INTO " . $objectDTO->getTableSource() . " (" . $objectDTO->getStringTableMetadata($useAutoIncrement) . ") VALUES ";
                $cadena_sql .="(";

                if (!$useAutoIncrement) {
                    $cadena_sql .= $this->cleanSqlValue($objectDTO->getID_purchaseorders()) . ",";
                }

                $cadena_sql .= $this->cleanSqlValue($objectDTO->getID_vendors()) . "," . $this->cleanSqlValue($objectDTO->getRefNumber()) . ",
                    " . $this->cleanSqlValue($objectDTO->getPoDate()) . "," . $this->cleanSqlValue($objectDTO->getCancelDate()) . ",
                    " . $this->cleanSqlValue($objectDTO->getPoTerms()) . "," . $this->cleanSqlValue($objectDTO->getPoTermsDesc()) . ",
                    " . $this->cleanSqlValue($objectDTO->getType()) . "," . $this->cleanSqlValue($objectDTO->getShipVia()) . ",
                    " . $this->cleanSqlValue($objectDTO->getOtherDesc()) . "," . $this->cleanSqlValue($objectDTO->getID_warehouses()) . ",
                    " . $this->cleanSqlValue($objectDTO->getDiscountPorc()) . "," . $this->cleanSqlValue($objectDTO->getDiscountDays()) . ",
                    " . $this->cleanSqlValue($objectDTO->getAuthBy()) . "," . $this->cleanSqlValue($objectDTO->getAuth()) . ",
                    " . $this->cleanSqlValue($objectDTO->getStatus()) . "," . $this->cleanSqlValue($objectDTO->getEtd()) . ",
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

        if ($objectDTO instanceof PurchaseOrdersDTO) {

            $array_fields = $objectDTO->getFieldList();

            if ($this->connectDB()) {

                $isWherePrev = FALSE;
                $cadena_sql = "SELECT " . $objectDTO->getStringTableMetadata() . " FROM " . $objectDTO->getTableSource();

                if ($objectDTO->getID_purchaseorders() != "") {
                    $cadena_sql .= " WHERE ";
                    $isWherePrev = TRUE;

                    $cadena_sql .= $array_fields[0] . " = " . $this->cleanSqlValue($objectDTO->getID_purchaseorders());
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
                        $poDTO = new PurchaseOrdersDTO();

                        $poDTO->setID_purchaseorders($fila[$array_fields[$idx]]);
                        $poDTO->setID_vendors($fila[$array_fields[++$idx]]);
                        $poDTO->setRefNumber($fila[$array_fields[++$idx]]);
                        $poDTO->setPoDate($fila[$array_fields[++$idx]]);
                        $poDTO->setCancelDate($fila[$array_fields[++$idx]]);
                        $poDTO->setPoTerms($fila[$array_fields[++$idx]]);
                        $poDTO->setPoTermsDesc($fila[$array_fields[++$idx]]);
                        $poDTO->setType($fila[$array_fields[++$idx]]);
                        $poDTO->setShipVia($fila[$array_fields[++$idx]]);
                        $poDTO->setOtherDesc($fila[$array_fields[++$idx]]);
                        $poDTO->setID_warehouses($fila[$array_fields[++$idx]]);
                        $poDTO->setDiscountPorc($fila[$array_fields[++$idx]]);
                        $poDTO->setDiscountDays($fila[$array_fields[++$idx]]);
                        $poDTO->setAuthBy($fila[$array_fields[++$idx]]);
                        $poDTO->setAuth($fila[$array_fields[++$idx]]);
                        $poDTO->setStatus($fila[$array_fields[++$idx]]);
                        $poDTO->setEtd($fila[$array_fields[++$idx]]);
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
        
    }

}

?>
