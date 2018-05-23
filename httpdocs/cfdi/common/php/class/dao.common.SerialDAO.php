<?php

require_once 'BaseDAO.php';
require_once 'InterfaceDAO.php';
require_once 'dto.common.SerialDTO.php';

/**
 * Description of dao
 *
 * @author Oscar Maldonado
 */
class InvoicesSerialDAO extends BaseDAO implements InterfaceDAO {

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
        if ($objectDTO instanceof InvoicesSerialDTO) {
            if ($this->connectDB()) {
                #if(strtoupper($objectDTO->getVname())=='S'){$Field='invoices_doc_serial';}
                #else{$Field='invoices_doc_num';}

                switch(strtoupper($objectDTO->getVname())){
                    case 'IS' : $Field='invoices_doc_serial'; break; #Factura - Serie
                    case 'IN' : $Field='invoices_doc_num'; break; #Factura - Folio
                    case 'CS' : $Field='creditnote_doc_serial'; break; #Nota de Credito - Serie
                    case 'CN' : $Field='creditnote_doc_num'; break; #Nota de Credito - Folio
                }

                $cadena_sql = "SELECT VValue FROM " . $objectDTO->getTableSource() . " WHERE  1 ";
                if (!is_null($objectDTO->getVname()) && $objectDTO->getVname() != "") {
                    $cadena_sql .=" AND VName='" . $Field . "'";
                }
                $this->selectSQLcommand($cadena_sql);

                if ($this->onlyCountRows) {
                    $this->onlyCountRows = FALSE;
                    $this->disconnectDB();
                    return;
                }

                if ($this->numRows > 0) {
                    while ($fila = $this->fetchAssocNextRow()) {
                        $invoicesDTO = new InvoicesSerialDTO();
                        $invoicesDTO->setVvalue($fila['VValue']);                       
                        $array_result[] = $invoicesDTO;
                    }
                }
            }
        }
        return $array_result;
    }

    public function updateRecord(&$objectDTO) {
        $this->operationSuccess = FALSE;
        if ($objectDTO instanceof InvoicesSerialDTO) {
            if ($this->connectDB()) {

                #if(strtoupper($objectDTO->getVname())=='S'){$Field='invoices_doc_serial';}
                #else{$Field='invoices_doc_num';}

                switch(strtoupper($objectDTO->getVname())){
                    case 'IS' : $Field='invoices_doc_serial'; break; #Factura - Serie
                    case 'IN' : $Field='invoices_doc_num'; break; #Factura - Folio
                    case 'CS' : $Field='creditnote_doc_serial'; break; #Nota de Credito - Serie
                    case 'CN' : $Field='creditnote_doc_num'; break; #Nota de Credito - Folio
                }

                $needAnd = FALSE;

                $cadena_sql = "UPDATE " . $objectDTO->getTableSource() . " SET ";
                if (trim($objectDTO->getVvalue()) != '') {
                    $cadena_sql .= "VValue = " . $this->cleanSqlValue($objectDTO->getVvalue());
                    $needAnd = TRUE;
                }
                $cadena_sql .= " WHERE ";
                #if ($objectDTO->getVvalue() > 0) {
                    $cadena_sql .= " VName = '".$Field."'";
                #}

                if ($this->executeSQLcommand($cadena_sql) >= 0) {
                    $this->operationSuccess = TRUE;
                }
            }
            $this->disconnectDB();
        }
        return $this->operationSuccess;
    }

    public function duplicateRecord(&$objectDTO) {
       
    }

}

?>
