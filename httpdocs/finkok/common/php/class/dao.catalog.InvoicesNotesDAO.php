<?php

require_once 'BaseDAO.php';
require_once 'InterfaceDAO.php';
require_once 'dto.catalog.InvoicesNotesDTO.php';

/**
 * Description of dao
 *
 * @author ccedillo
 */
class InvoicesNotesDAO extends BaseDAO implements InterfaceDAO {

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
        if ($objectDTO instanceof InvoicesNotesDTO) {
            if ($this->connectDB()) {
                $cadena_sql = "INSERT INTO " . $objectDTO->getTableSource() . " (" . $objectDTO->getStringTableMetadata(TRUE) . ") VALUES ";
                $cadena_sql .="(" .
                        $this->cleanSqlValue($objectDTO->getID_invoices()) . "," . $this->cleanSqlValue($objectDTO->getNotes()) . ",
                    " . $this->cleanSqlValue($objectDTO->getType()) . ",
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

        if ($objectDTO instanceof InvoicesNotesDTO) {
            if ($this->connectDB()) {
                $cadena_sql = "SELECT * FROM " . $objectDTO->getTableSource() . " WHERE  1 ";

                if (!is_null($objectDTO->getID_invoices()) && $objectDTO->getID_invoices() > 0) {
                    $cadena_sql .="AND ID_invoices = " . $this->cleanSqlValue($objectDTO->getID_invoices());
                }

                if (!is_null($objectDTO->getType())) {
                    $cadena_sql .="AND Type = " . $this->cleanSqlValue($objectDTO->getType());
                }
                
                
                $cadena_sql .= " ORDER BY ID_invoices_notes ASC";

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
                        $invoicesNotesDTO = new InvoicesNotesDTO();
                        
                        $invoicesNotesDTO->setID_invoices_notes($fila['ID_invoices_notes']);
                        $invoicesNotesDTO->setID_invoices($fila['ID_invoices']);
                        $invoicesNotesDTO->setNotes($fila['Notes']);
                        $invoicesNotesDTO->setType($fila['Type']);
                        $invoicesNotesDTO->setDate($fila['Date']);
                        $invoicesNotesDTO->setTime($fila['Time']);
                        $invoicesNotesDTO->setID_admin_users($fila['ID_admin_users']);
                        
                        $array_result[] = $invoicesNotesDTO;
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
