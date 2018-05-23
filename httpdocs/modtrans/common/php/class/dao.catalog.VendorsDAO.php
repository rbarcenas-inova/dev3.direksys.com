<?php

require_once 'BaseDAO.php';
require_once 'InterfaceDAO.php';
require_once 'dto.catalog.VendorsDTO.php';

/**
 * Description
 *
 * @author L.C.I Cesar Cedillo
 */
class VendorsDAO extends BaseDAO implements InterfaceDAO {

    //put your code here
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

        if ($objectDTO instanceof VendorsDTO) {
            $array_fields = $objectDTO->getFieldList();

            if ($this->connectDB()) {
                $isWherePrev = FALSE;
                $cadena_sql = "SELECT * FROM " . $objectDTO->getTableSource();

                if($objectDTO->getID_vendors() > 0){
                    $cadena_sql .= " WHERE ";
                    $isWherePrev = TRUE;

                    $cadena_sql .=  $array_fields[0] . " = " . $this->cleanSqlValue($objectDTO->getID_vendors());
                }

                if ($objectDTO->getCompanyName() != "") {
                    if ($isWherePrev) {
                        $cadena_sql .= " AND ";
                    } else {
                        $cadena_sql .= " WHERE ";
                        $isWherePrev = TRUE;
                    }

                    $cadena_sql .= $array_fields[1] . " LIKE  '%" . $this->cleanSqlValue($objectDTO->getCompanyName() , false) . "%'";
                }


                if ($this->orderBy != "") {
                    if ($this->orderBy == "LastName2") {
                        $cadenaSQL .= " ORDER BY $array_fields[4] ASC";
                    }
                    if ($this->orderBy == "ID_customer") {
                        $cadenaSQL .= " ORDER BY $array_fields[0] ASC";
                    }
                } else {
                    $cadena_sql .=" ORDER BY $array_fields[1] ASC";
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
                        $vendorDTO = new VendorsDTO();
                        $vendorDTO->setID_vendors($fila[$array_fields[$idx]]);
                        $vendorDTO->setCompanyName($fila[$array_fields[++$idx]]);
                        $vendorDTO->setRFC($fila[$array_fields[++$idx]]);
                        $vendorDTO->setAddress($fila[$array_fields[++$idx]]);
                        $vendorDTO->setCity($fila[$array_fields[++$idx]]);
                        $vendorDTO->setState($fila[$array_fields[++$idx]]);
                        $vendorDTO->setZip($fila[$array_fields[++$idx]]);
                        $vendorDTO->setCountry($fila[$array_fields[++$idx]]);
                        $vendorDTO->setPhone($fila[$array_fields[++$idx]]);

                        $array_result[] = $vendorDTO;
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