<?php

require_once 'BaseDAO.php';
require_once 'InterfaceDAO.php';
require_once 'dto.catalog.PartsDTO.php';

/**
 * Description
 *
 * @author L.C.I Cesar Cedillo
 */
class PartsDAO extends BaseDAO implements InterfaceDAO {

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

        if ($objectDTO instanceof PartsDTO) {
            if ($this->connectDB()) {
                $array_fields = $objectDTO->getFieldList();
                $isWherePrev = FALSE;

                $cadena_sql = "SELECT * FROM " . $objectDTO->getTableSource();

                if (!(is_null($objectDTO->getID_parts())) && $objectDTO->getID_parts() != 0) {
                    $isWherePrev = TRUE;
                    $cadena_sql .= " WHERE ";
                    $cadena_sql .= "$array_fields[0] = " . $this->cleanSqlValue($objectDTO->getID_parts());
                }

                if (!(is_null($objectDTO->getModel())) && $objectDTO->getModel() != "") {
                    if ($isWherePrev) {
                        $cadena_sql .= " AND ";
                    } else {
                        $isWherePrev = TRUE;
                        $cadena_sql .= " WHERE ";
                    }
                    $cadena_sql .= "$array_fields[1]  LIKE '%" . $this->cleanSqlValue($objectDTO->getModel(), false) . "%'";
                }

                if (!(is_null($objectDTO->getName())) && $objectDTO->getName() != "") {
                    if ($isWherePrev) {
                        $cadena_sql .= " OR ";
                    } else {
                        $isWherePrev = TRUE;
                        $cadena_sql .= " WHERE ";
                    }
                    $cadena_sql .= "$array_fields[2]  LIKE '%" . $this->cleanSqlValue($objectDTO->getName(), false) . "%'";
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
                        $partsDTO = new PartsDTO();

                        $partsDTO->setID_parts($fila[$array_fields[$idx]]);
                        $partsDTO->setModel($fila[$array_fields[++$idx]]);
                        $partsDTO->setName($fila[$array_fields[++$idx]]);
                        $partsDTO->setID_categories($fila[$array_fields[++$idx]]);
                        $partsDTO->setStatus($fila[$array_fields[++$idx]]);
                        $partsDTO->setDate($fila[$array_fields[++$idx]]);
                        $partsDTO->setTime($fila[$array_fields[++$idx]]);
                        $partsDTO->setID_admin_users($fila[$array_fields[++$idx]]);

                        $array_result[] = $partsDTO;
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