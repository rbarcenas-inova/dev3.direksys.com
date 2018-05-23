<?php

require_once 'BaseDAO.php';
require_once 'InterfaceDAO.php';
require_once 'dto.catalog.WarehousesDTO.php';

/**
 * Description
 *
 * @author L.C.I Cesar Cedillo
 */
class WarehousesDAO extends BaseDAO implements InterfaceDAO {

    public function deleteRecord(&$objectDTO) {
        
    }

    public function insertRecord(&$objectDTO) {
        
    }

    public function selectRecords(&$objectDTO, $notInType = FALSE) {

        $array_result = array();

        if ($objectDTO instanceof WarehousesDTO) {

            $array_fields = $objectDTO->getFieldList();

            if ($this->connectDB()) {

                $isWherePrev = FALSE;
                $cadena_sql = "SELECT " . $objectDTO->getStringTableMetadata() . " FROM " . $objectDTO->getTableSource();

                if (is_numeric($objectDTO->getID_warehouses())) {
                    $cadena_sql .= " WHERE ";
                    $isWherePrev = TRUE;

                    $cadena_sql .= $array_fields[0] . " = " . $this->cleanSqlValue($objectDTO->getID_warehouses());
                }

                if ($objectDTO->getName() != "") {
                    if ($isWherePrev) {
                        $cadena_sql .= " AND ";
                    } else {
                        $cadena_sql .= " WHERE ";
                        $isWherePrev = TRUE;
                        $cadena_sql .= $array_fields[1] . " = " . $this->cleanSqlValue($objectDTO->getName()) ;
                    }
                }

                if ($objectDTO->getType() != "") {
                    if ($isWherePrev) {
                        $cadena_sql .= " AND ";
                    } else {
                        $cadena_sql .= " WHERE ";
                        $isWherePrev = TRUE;
                    }

                    if ($notInType) {
                        $cadena_sql .= $array_fields[2] . " NOT IN (" . $this->cleanSqlValue($objectDTO->getType()) . ") ";
                    } else {
                        $cadena_sql .= $array_fields[2] . " = " . $this->cleanSqlValue($objectDTO->getType());
                    }
                }

                if ($objectDTO->getZip() != "") {
                    if ($isWherePrev) {
                        $cadena_sql .= " AND ";
                    } else {
                        $cadena_sql .= " WHERE ";
                        $isWherePrev = TRUE;
                    }
                    $cadena_sql .= $array_fields[8] . " = " . $this->cleanSqlValue($objectDTO->getZip());
                }

                if ($objectDTO->getDropShipper() != "") {
                    if ($isWherePrev) {
                        $cadena_sql .= " AND ";
                    } else {
                        $cadena_sql .= " WHERE ";
                        $isWherePrev = TRUE;
                    }
                    $cadena_sql .= $array_fields[11] . " = " . $this->cleanSqlValue($objectDTO->getDropShipper());
                }


                if ($objectDTO->getStatus() != "") {
                    if ($isWherePrev) {
                        $cadena_sql .= " AND ";
                    } else {
                        $cadena_sql .= " WHERE ";
                        $isWherePrev = TRUE;
                    }
                    $cadena_sql .= $array_fields[14] . " = " . $this->cleanSqlValue($objectDTO->getStatus());
                }


                if ($this->orderBy != "") {
                    if ($this->orderBy == "Name") {
                        $cadenaSQL .= " ORDER BY $array_fields[1] ASC";
                    }
                    if ($this->orderBy == "State") {
                        $cadenaSQL .= " ORDER BY $array_fields[7] ASC";
                    }
                } else {
                    $cadena_sql .=" ORDER BY $array_fields[7] ASC, $array_fields[6] ASC, $array_fields[1] ASC, $array_fields[2] ASC";
                }


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
                        $whDTO = new WarehousesDTO();

                        $whDTO->setID_warehouses($fila[$array_fields[$idx]]);
                        $whDTO->setName($fila[$array_fields[++$idx]]);
                        $whDTO->setType($fila[$array_fields[++$idx]]);
                        $whDTO->setAddress1($fila[$array_fields[++$idx]]);
                        $whDTO->setAddress2($fila[$array_fields[++$idx]]);
                        $whDTO->setAddress3($fila[$array_fields[++$idx]]);
                        $whDTO->setCity($fila[$array_fields[++$idx]]);
                        $whDTO->setState($fila[$array_fields[++$idx]]);
                        $whDTO->setZip($fila[$array_fields[++$idx]]);
                        $whDTO->setCoverage($fila[$array_fields[++$idx]]);
                        $whDTO->setNotes($fila[$array_fields[++$idx]]);
                        $whDTO->setDropShipper($fila[$array_fields[++$idx]]);
                        $whDTO->setWManager($fila[$array_fields[++$idx]]);
                        $whDTO->setCodList($fila[$array_fields[++$idx]]);
                        $whDTO->setStatus($fila[$array_fields[++$idx]]);


                        $array_result[] = $whDTO;
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