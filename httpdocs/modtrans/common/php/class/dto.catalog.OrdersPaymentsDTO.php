<?php

require_once 'BaseDTO.php';
/*
 * To change this template, choose Tools | Templates
 * and open the template in the editor.
 */

/**
 * Description
 *
 * @author L.C.I Cesar Cedillo
 */
class OrdersPaymentsDTO extends BaseDTO {

    private $iD_orders_payments;
    private $iD_orders;
    private $type;
    private $pmtField1;
    private $pmtField2;
    private $pmtField3;
    private $pmtField4;
    private $pmtField5;
    private $pmtField6;
    private $pmtField7;
    private $pmtField8;
    private $pmtField9;
    private $amount;
    private $reason;
    private $paymentDate;
    private $authCode;
    private $authDateTime;
    private $captured;
    private $capDate;
    private $postedDate;
    private $status;
    private $date;
    private $time;
    private $iD_admin_users;


    function __construct() {
        parent::__construct();

        $this->table_source = 'sl_orders_payments';
        $this->field_list = array(
            'ID_orders_payments',
            'ID_orders',
            'Type',
            'PmtField1',
            'PmtField2',
            'PmtField3',
            'PmtField4',
            'PmtField5',
            'PmtField6',
            'PmtField7',
            'PmtField8',
            'PmtField9',
            'Amount',
            'Reason',
            'Paymentdate',
            'AuthCode',
            'AuthDateTime',
            'Captured',
            'CapDate',
            'PostedDate',
            'Status',
            'Date',
            'Time',
            'ID_admin_users'
        );
        
        $this->type ="COD";
        $this->pmtField1 = "";
        $this->pmtField2 = "";
        $this->pmtField3 = "";
        $this->pmtField4 = "";
        $this->pmtField5 = "";
        $this->pmtField6 = "";
        $this->pmtField7 = "";
        $this->pmtField8 = "";
        $this->pmtField9 = "";
        $this->amount = 0.0;
        $this->reason = "Other";
        $this->paymentDate = "0000-00-00";
        $this->authCode = "";
        $this->authDateTime = "";
        $this->captured ="No";        
        $this->postedDate = "0000-00-00";
        $this->status = "Approved";
        $this->iD_admin_users = 0;
        
    }

    
    public function getID_orders_payments() {
        return $this->iD_orders_payments;
    }

    public function setID_orders_payments($iD_orders_payments) {
        $this->iD_orders_payments = $iD_orders_payments;
    }

    public function getID_orders() {
        return $this->iD_orders;
    }

    public function setID_orders($iD_orders) {
        $this->iD_orders = $iD_orders;
    }

    public function getType() {
        return $this->type;
    }

    public function setType($type) {
        $this->type = $type;
    }

    public function getPmtField1() {
        return $this->pmtField1;
    }

    public function setPmtField1($pmtField1) {
        $this->pmtField1 = $pmtField1;
    }

    public function getPmtField2() {
        return $this->pmtField2;
    }

    public function setPmtField2($pmtField2) {
        $this->pmtField2 = $pmtField2;
    }

    public function getPmtField3() {
        return $this->pmtField3;
    }

    public function setPmtField3($pmtField3) {
        $this->pmtField3 = $pmtField3;
    }

    public function getPmtField4() {
        return $this->pmtField4;
    }

    public function setPmtField4($pmtField4) {
        $this->pmtField4 = $pmtField4;
    }

    public function getPmtField5() {
        return $this->pmtField5;
    }

    public function setPmtField5($pmtField5) {
        $this->pmtField5 = $pmtField5;
    }

    public function getPmtField6() {
        return $this->pmtField6;
    }

    public function setPmtField6($pmtField6) {
        $this->pmtField6 = $pmtField6;
    }

    public function getPmtField7() {
        return $this->pmtField7;
    }

    public function setPmtField7($pmtField7) {
        $this->pmtField7 = $pmtField7;
    }

    public function getPmtField8() {
        return $this->pmtField8;
    }

    public function setPmtField8($pmtField8) {
        $this->pmtField8 = $pmtField8;
    }

    public function getPmtField9() {
        return $this->pmtField9;
    }

    public function setPmtField9($pmtField9) {
        $this->pmtField9 = $pmtField9;
    }

    public function getAmount() {
        return $this->amount;
    }

    public function setAmount($amount) {
        $this->amount = $amount;
    }

    public function getReason() {
        return $this->reason;
    }

    public function setReason($reason) {
        $this->reason = $reason;
    }

    public function getPaymentDate() {
        return $this->paymentDate;
    }

    public function setPaymentDate($paymentDate) {
        $this->paymentDate = $paymentDate;
    }

    public function getAuthCode() {
        return $this->authCode;
    }

    public function setAuthCode($authCode) {
        $this->authCode = $authCode;
    }

    public function getAuthDateTime() {
        return $this->authDateTime;
    }

    public function setAuthDateTime($authDateTime) {
        $this->authDateTime = $authDateTime;
    }

    public function getCaptured() {
        return $this->captured;
    }

    public function setCaptured($captured) {
        $this->captured = $captured;
    }

    public function getCapDate() {
        return $this->capDate;
    }

    public function setCapDate($capDate) {
        $this->capDate = $capDate;
    }

    public function getPostedDate() {
        return $this->postedDate;
    }

    public function setPostedDate($postedDate) {
        $this->postedDate = $postedDate;
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