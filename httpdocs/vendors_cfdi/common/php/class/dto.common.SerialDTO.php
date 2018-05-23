<?php

require_once 'BaseDTO.php';


/**
 * Description of dto
 *
 * @author Oscar Maldonado
 */
class InvoicesSerialDTO extends BaseDTO {

    private $Vname;
    private $Vvalue;
    private $invoices_doc_serial;
    private $invoices_doc_num;
    #private $Date;
    #private $Time;
    #private $iDAdminUsers;
    
    function __construct() {
        parent::__construct();

        $this->table_source = 'sl_vars';
        $this->field_list = array(
            'VName',
            'VValue'
            #'Date',
            #'Time',
            #'ID_admin_users'
        );
    }

    public function getVname() {
        return $this->Vname;
    }

    public function setVname($Vname) {
        $this->Vname = $Vname;
    }

    public function getVvalue() {
        return $this->Vvalue;
    }

    public function setVvalue($Vvalue) {
        $this->Vvalue = $Vvalue;
    }

    public function getInvoicesDocSerial() {
        return $this->invoices_doc_serial;
    }

    public function setInvoicesDocSerial($invoices_doc_serial) {
        $this->invoices_doc_serial = $invoices_doc_serial;
    }

    public function getInvoicesDocNum() {
        return $this->invoices_doc_num;
    }

    public function setInvoicesDocNum($invoices_doc_num) {
        $this->invoices_doc_num = $invoices_doc_num;
    }

/*
    public function getDate() {
        return $this->Date;
    }

    public function setDate($Date) {
        $this->Date = $Date;
    }

    public function getTime() {
        return $this->Time;
    }

    public function setTime($Time) {
        $this->Time = $Time;
    }

    public function getID_admin_users() {
        return $this->iDAdminUsers;
    }

    public function setID_admin_users($iDAdminUsers) {
        $this->iDAdminUsers = $iDAdminUsers;
    }
*/

}

?>