<?php
require_once 'BaseDTO.php';


/**
 * Description
 *
 * @author L.C.I Cesar Cedillo
 */
class BillsPaymentsDTO extends BaseDTO {
    private $iD_billspayments;
    private $iD_banks;
    private $iD_vendors;
    private $name;
    private $description;
    private $amount;
    private $currency;
    private $status;
    private $date;
    private $time;
    private $iD_admin_users;
    
    
    function __construct() {
        parent::__construct();
        $this->table_source = 'sl_billspayments';
        $this->field_list = array(
            'ID_billspayments',  
            'ID_banks',  
            'ID_vendors',  
            'Name',  
            'Description',  
            'Amount',  
            'Currency',  
            'Status',  
            'Date',  
            'Time',  
            'ID_admin_users'
        );
    }
    
    public function getID_billspayments() {
        return $this->iD_billspayments;
    }

    public function setID_billspayments($iD_billspayments) {
        $this->iD_billspayments = $iD_billspayments;
    }

    public function getID_banks() {
        return $this->iD_banks;
    }

    public function setID_banks($iD_banks) {
        $this->iD_banks = $iD_banks;
    }

    public function getID_vendors() {
        return $this->iD_vendors;
    }

    public function setID_vendors($iD_vendors) {
        $this->iD_vendors = $iD_vendors;
    }

    public function getName() {
        return $this->name;
    }

    public function setName($name) {
        $this->name = $name;
    }

    public function getDescription() {
        return $this->description;
    }

    public function setDescription($description) {
        $this->description = $description;
    }

    public function getAmount() {
        return $this->amount;
    }

    public function setAmount($amount) {
        $this->amount = $amount;
    }

    public function getCurrency() {
        return $this->currency;
    }

    public function setCurrency($currency) {
        $this->currency = $currency;
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