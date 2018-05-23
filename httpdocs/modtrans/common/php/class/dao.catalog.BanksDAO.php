<?php
require_once 'BaseDAO.php';
require_once 'InterfaceDAO.php';
require_once 'dto.catalog.BanksDTO.php';

/**
 * Description
 *
 * @author L.C.I Cesar Cedillo
 */
class BanksDAO extends BaseDAO implements InterfaceDAO {
    
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

        if ($objectDTO instanceof BanksDTO) {
            if ($this->connectDB()) {
                $array_fields = $objectDTO->getFieldList();
                $isWherePrev = FALSE;

                $cadena_sql = "SELECT * FROM " . $objectDTO->getTableSource();

                if (!(is_null($objectDTO->getID_banks())) && $objectDTO->getID_banks() != 0) {
                    $isWherePrev = TRUE;
                    $cadena_sql .= " WHERE ";
                    $cadena_sql .= "$array_fields[0] = " . $this->cleanSqlValue($objectDTO->getID_banks());
                }

                if (!(is_null($objectDTO->getName())) && $objectDTO->getName() != "") {
                    if ($isWherePrev) {
                        $cadena_sql .= " AND ";
                    } else {
                        $isWherePrev = TRUE;
                        $cadena_sql .= " WHERE ";
                    }
                    $cadena_sql .= "$array_fields[1]  LIKE '%" . $this->cleanSqlValue($objectDTO->getName(), false) . "%'";
                }

                if (!(is_null($objectDTO->getShortName())) && $objectDTO->getShortName() != "") {
                    if ($isWherePrev) {
                        $cadena_sql .= " OR ";
                    } else {
                        $isWherePrev = TRUE;
                        $cadena_sql .= " WHERE ";
                    }
                    $cadena_sql .= "$array_fields[2]  LIKE '%" . $this->cleanSqlValue($objectDTO->getShortName(), false) . "%'";
                }

                if (!(is_null($objectDTO->getBankName())) && $objectDTO->getBankName() != "") {
                    if ($isWherePrev) {
                        $cadena_sql .= " AND ";
                    } else {
                        $isWherePrev = TRUE;
                        $cadena_sql .= " WHERE ";
                    }
                    $cadena_sql .= "$array_fields[4]  LIKE '%" . $this->cleanSqlValue($objectDTO->getBankName(), false) . "%'";
                }

                if (!(is_null($objectDTO->getStatus())) && $objectDTO->getStatus() != "") {
                    if ($isWherePrev) {
                        $cadena_sql .= " OR ";
                    } else {
                        $isWherePrev = TRUE;
                        $cadena_sql .= " WHERE ";
                    }
                    $cadena_sql .= "$array_fields[17]  = " . $this->cleanSqlValue($objectDTO->getStatus());
                }                
                
                $cadena_sql .=" ORDER BY $array_fields[1] ASC";

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
                        $bankDTO = new BanksDTO();

                        $bankDTO->setID_banks($fila[$array_fields[$idx]]);
                        $bankDTO->setName($fila[$array_fields[++$idx]]);
                        $bankDTO->setShortName($fila[$array_fields[++$idx]]);
                        $bankDTO->setDescription($fila[$array_fields[++$idx]]);
                        $bankDTO->setBankName($fila[$array_fields[++$idx]]);
                        $bankDTO->setBankAddress($fila[$array_fields[++$idx]]);
                        $bankDTO->setBankContact($fila[$array_fields[++$idx]]);
                        $bankDTO->setBankContactPhone($fila[$array_fields[++$idx]]);
                        $bankDTO->setCurrency($fila[$array_fields[++$idx]]);
                        
                        $array_result[] = $bankDTO;
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
