<?php

require_once 'BaseDAO.php';
require_once 'InterfaceDAO.php';
require_once 'dto.catalog.SkusDTO.php';
/*
 * To change this template, choose Tools | Templates
 * and open the template in the editor.
 */

/**
 * Description
 *
 * @author L.C.I Cesar Cedillo
 */
class SkusDAO extends BaseDAO implements InterfaceDAO {

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

        if ($objectDTO instanceof SkusDTO) {

            $array_fields = $objectDTO->getFieldList();

            if ($this->connectDB()) {

                $isWherePrev = FALSE;
                $cadena_sql = "SELECT " . $objectDTO->getStringTableMetadata() . " FROM " . $objectDTO->getTableSource();

                if ($objectDTO->getID_skus() != "") {
                    $cadena_sql .= " WHERE ";
                    $isWherePrev = TRUE;

                    $cadena_sql .= $array_fields[0] . " = " . $this->cleanSqlValue($objectDTO->getID_skus());
                }

                if ($objectDTO->getID_sku_products() != "") {
                    if ($isWherePrev) {
                        $cadena_sql .= " AND ";
                    } else {
                        $cadena_sql .= " WHERE ";
                        $isWherePrev = TRUE;
                    }
                    $cadena_sql .= $array_fields[1] . " = " . $this->cleanSqlValue($objectDTO->getID_sku_products());
                }

                if ($objectDTO->getID_products() != "") {
                    if ($isWherePrev) {
                        $cadena_sql .= " AND ";
                    } else {
                        $cadena_sql .= " WHERE ";
                        $isWherePrev = TRUE;
                    }
                    $cadena_sql .= $array_fields[2] . " = " . $this->cleanSqlValue($objectDTO->getID_products());
                }

                if ($objectDTO->getUPC() != "") {
                    if ($isWherePrev) {
                        $cadena_sql .= " AND ";
                    } else {
                        $cadena_sql .= " WHERE ";
                        $isWherePrev = TRUE;
                    }
                    $cadena_sql .= $array_fields[4] . " = " . $this->cleanSqlValue($objectDTO->getUPC());
                }

                $cadena_sql .=" ORDER BY $array_fields[3] ASC";

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
                        $skuDTO = new SkusDTO();

                        $skuDTO->setID_skus($fila[$array_fields[$idx]]);
                        $skuDTO->setID_sku_products($fila[$array_fields[++$idx]]);
                        $skuDTO->setID_products($fila[$array_fields[++$idx]]);
                        $skuDTO->setVendorSKU($fila[$array_fields[++$idx]]);
                        $skuDTO->setUPC($fila[$array_fields[++$idx]]);
                        $skuDTO->setIsSet($fila[$array_fields[++$idx]]);
                        $skuDTO->setChoice1($fila[$array_fields[++$idx]]);
                        $skuDTO->setChoice2($fila[$array_fields[++$idx]]);
                        $skuDTO->setChoice3($fila[$array_fields[++$idx]]);
                        $skuDTO->setChoice4($fila[$array_fields[++$idx]]);
                        $skuDTO->setStatus($fila[$array_fields[++$idx]]);
                        $skuDTO->setDate($fila[$array_fields[++$idx]]);
                        $skuDTO->setTime($fila[$array_fields[++$idx]]);
                        $skuDTO->setID_admin_users($fila[$array_fields[++$idx]]);
                        
                        $array_result[] = $skuDTO;
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
