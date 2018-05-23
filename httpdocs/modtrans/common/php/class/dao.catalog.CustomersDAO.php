<?php

/**
 * Description
 *
 * @author L.C.I Cesar Cedillo
 */
require_once 'BaseDAO.php';
require_once 'InterfaceDAO.php';
require_once 'dto.catalog.CustomersDTO.php';

class CustomersDAO extends BaseDAO implements InterfaceDAO {

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
        
    }

    public function updateRecord(&$objectDTO) {
        
    }

    public function searchByCustomerName(&$objectDTO) {

        $array_result = array();

        if ($objectDTO instanceof CustomersDTO) {

            $array_fields = $objectDTO->getFieldList();

            if ($this->connectDB()) {

                $isWherePrev = FALSE;
                $cadena_sql = "SELECT " . $objectDTO->getStringTableMetadata() . " FROM " . $objectDTO->getTableSource();

                if ($objectDTO->getFirstName() != "") {
                    $cadena_sql .= " WHERE ";
                    $isWherePrev = TRUE;

                    $cadena_sql .= $array_fields[2] . " LIKE  '" . $this->cleanSqlValue($objectDTO->getFirstName() , false) . "%'";
                }

                if ($objectDTO->getLastName() != "") {
                    if ($isWherePrev) {
                        $cadena_sql .= " AND ";
                    } else {
                        $cadena_sql .= " WHERE ";
                        $isWherePrev = TRUE;
                    }
                    $cadena_sql .= $array_fields[3] . " LIKE  '" . $this->cleanSqlValue($objectDTO->getLastName(), false) . "%'";
                }

                if ($objectDTO->getLastName2() != "") {
                    if ($isWherePrev) {
                        $cadena_sql .= " AND ";
                    } else {
                        $cadena_sql .= " WHERE ";
                        $isWherePrev = TRUE;
                    }
                    $cadena_sql .= $array_fields[4] . " LIKE  '" . $this->cleanSqlValue($objectDTO->getLastName2(), false) . "%'";
                }

                if ($objectDTO->getID_customers() != "" && $objectDTO->getID_customers() != 0) {
                    if ($isWherePrev) {
                        $cadena_sql .= " AND ";
                    } else {
                        $cadena_sql .= " WHERE ";
                        $isWherePrev = TRUE;
                    }
                    $cadena_sql .= $array_fields[0] . " = " . $this->cleanSqlValue($objectDTO->getID_customers());
                }

                if ($this->orderBy != "") {
                    if ($this->orderBy == "LastName2") {
                        $cadenaSQL .= " ORDER BY $array_fields[4] ASC";
                    }
                    if ($this->orderBy == "ID_customer") {
                        $cadenaSQL .= " ORDER BY $array_fields[0] ASC";
                    }
                } else {
                    $cadena_sql .=" ORDER BY $array_fields[2] ASC, $array_fields[3] ASC, $array_fields[4] ASC";
                }


                if ($this->pagerPage > -1 && $this->pagerLimit > -1) {
                    $cadena_sql .= " LIMIT " . $this->pagerPage . "," . $this->pagerLimit;
                }

                $this->selectSQLcommand($cadena_sql);

                if($this->onlyCountRows){
                    $this->onlyCountRows = FALSE;
                    $this->disconnectDB();
                    return;
                }
                
                
                if ($this->numRows > 0) {
                    while ($fila = $this->fetchAssocNextRow()) {
                        $idx = 0;
                        $customerDTO = new CustomersDTO();

                        $customerDTO->setID_customers($fila[$array_fields[$idx]]);
                        $customerDTO->setCID($fila[$array_fields[++$idx]]);
                        $customerDTO->setFirstName($fila[$array_fields[++$idx]]);
                        $customerDTO->setLastName($fila[$array_fields[++$idx]]);
                        $customerDTO->setLastName2($fila[$array_fields[++$idx]]);
                        $customerDTO->setSex($fila[$array_fields[++$idx]]);
                        $customerDTO->setPhone1($fila[$array_fields[++$idx]]);
                        $customerDTO->setAddress1($fila[$array_fields[++$idx]]);
                        $customerDTO->setAddress2($fila[$array_fields[++$idx]]);
                        $customerDTO->setAddress3($fila[$array_fields[++$idx]]);
                        $customerDTO->setUrbanization($fila[$array_fields[++$idx]]);
                        $customerDTO->setCity($fila[$array_fields[++$idx]]);
                        $customerDTO->setState($fila[$array_fields[++$idx]]);
                        $customerDTO->setZip($fila[$array_fields[++$idx]]);
                        $customerDTO->setCountry($fila[$array_fields[++$idx]]);

                        $array_result[] = $customerDTO;
                    }
                }
                $this->dbFreeResult();
            }

            $this->disconnectDB();
        }
        return $array_result;
    }

}

?>