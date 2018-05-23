<?php

require_once 'BaseDTO.php';


/**
 * Description
 *
 * @author L.C.I Cesar Cedillo
 */
class BillsPosDTO extends BaseDTO {
    
    private $iD_bills_pos;
    private $iD_bills;
    private $iD_purchaseorders;
    private $amount;
    private $date;
    private $time;
    private $iD_admin_users;
    
    function __construct() {
        parent::__construct();
        
        $this->table_source = 'sl_bills_pos';
        $this->field_list = array(
            'ID_bills_pos',  'ID_bills',  'ID_purchaseorders',  'Amount',  'Date',  'Time',  'ID_admin_users'
        );
    }
    
    public function getID_bills_pos() {
        return $this->iD_bills_pos;
    }

    public function setID_bills_pos($iD_bills_pos) {
        $this->iD_bills_pos = $iD_bills_pos;
    }

    public function getID_bills() {
        return $this->iD_bills;
    }

    public function setID_bills($iD_bills) {
        $this->iD_bills = $iD_bills;
    }

    public function getID_purchaseorders() {
        return $this->iD_purchaseorders;
    }

    public function setID_purchaseorders($iD_purchaseorders) {
        $this->iD_purchaseorders = $iD_purchaseorders;
    }

    public function getAmount() {
        return $this->amount;
    }

    public function setAmount($amount) {
        $this->amount = $amount;
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
