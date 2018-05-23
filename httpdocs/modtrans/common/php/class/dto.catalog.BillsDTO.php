<?php

require_once 'BaseDTO.php';

/**
 * Description
 *
 * @author L.C.I Cesar Cedillo
 */
class BillsDTO extends BaseDTO {

    private $iD_bills;
    private $iD_vendors;
    private $type;
    private $currency;
    private $amount;
    private $terms;
    private $memo;
    private $billDate;
    private $dueDate;
    private $authBy;
    private $status;
    private $date;
    private $time;
    private $iD_admin_users;

    function __construct() {
        parent::__construct();
        $this->table_source = 'sl_bills';
        $this->field_list = array(
            'ID_bills',
            'ID_vendors',
            'Type',
            'Currency',
            'Amount',
            'Terms',
            'Memo',
            'BillDate',
            'DueDate',
            'AuthBy',
            'Status',
            'Date',
            'Time',
            'ID_admin_users'
        );
    }

    public function getID_bills() {
        return $this->iD_bills;
    }

    public function setID_bills($iD_bills) {
        $this->iD_bills = $iD_bills;
    }

    public function getID_vendors() {
        return $this->iD_vendors;
    }

    public function setID_vendors($iD_vendors) {
        $this->iD_vendors = $iD_vendors;
    }

    public function getType() {
        return $this->type;
    }

    public function setType($type) {
        $this->type = $type;
    }

    public function getCurrency() {
        return $this->currency;
    }

    public function setCurrency($currency) {
        $this->currency = $currency;
    }

    public function getAmount() {
        return $this->amount;
    }

    public function setAmount($amount) {
        $this->amount = $amount;
    }

    public function getTerms() {
        return $this->terms;
    }

    public function setTerms($terms) {
        $this->terms = $terms;
    }

    public function getMemo() {
        return $this->memo;
    }

    public function setMemo($memo) {
        $this->memo = $memo;
    }

    public function getBillDate() {
        return $this->billDate;
    }

    public function setBillDate($billDate) {
        $this->billDate = $billDate;
    }

    public function getDueDate() {
        return $this->dueDate;
    }

    public function setDueDate($dueDate) {
        $this->dueDate = $dueDate;
    }

    public function getAuthBy() {
        return $this->authBy;
    }

    public function setAuthBy($authBy) {
        $this->authBy = $authBy;
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