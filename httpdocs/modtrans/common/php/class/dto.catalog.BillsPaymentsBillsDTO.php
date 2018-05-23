<?php
require_once 'BaseDTO.php';


/**
 * Description
 *
 * @author L.C.I Cesar Cedillo
 */
class BillsPaymentsBillsDTO extends BaseDTO {
    private $iD_payments_bills;
    private $iD_billspayments;
    private $iD_bills;
    private $status;
    private $date;
    private $time;
    private $iD_admin_users;
 
    function __construct() {
        parent::__construct();
        
        $this->table_source = 'sl_billspayments_bills';
        $this->field_list = array(
            'ID_billspayments_bills',  
            'ID_billspayments',  
            'ID_bills',  
            'Status',  
            'Date',  
            'Time',  
            'ID_admin_users'
        );
    }

    public function getID_payments_bills() {
        return $this->iD_payments_bills;
    }

    public function setID_payments_bills($iD_payments_bills) {
        $this->iD_payments_bills = $iD_payments_bills;
    }

    public function getID_billspayments() {
        return $this->iD_billspayments;
    }

    public function setID_billspayments($iD_billspayments) {
        $this->iD_billspayments = $iD_billspayments;
    }

    public function getID_bills() {
        return $this->iD_bills;
    }

    public function setID_bills($iD_bills) {
        $this->iD_bills = $iD_bills;
    }

    public function getStatus() {
        return $this->status;
    }

    public function setStatus($status) {
        $this->status = $status;
    }

    public function getDate() {
        return $this->date;
    }

    public function setDate($date) {
        $this->date = $date;
    }

    public function getTime() {
        return $this->time;
    }

    public function setTime($time) {
        $this->time = $time;
    }

    public function getID_admin_users() {
        return $this->iD_admin_users;
    }

    public function setID_admin_users($iD_admin_users) {
        $this->iD_admin_users = $iD_admin_users;
    }

}
?>