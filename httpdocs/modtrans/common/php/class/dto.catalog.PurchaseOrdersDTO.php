<?php

require_once 'BaseDTO.php';

/**
 * Description
 *
 * @author L.C.I Cesar Cedillo
 */
class PurchaseOrdersDTO extends BaseDTO {

    private $iD_purchaseorders;
    private $iD_vendors;
    private $refNumber;
    private $poDate;
    private $cancelDate;
    private $poTerms;
    private $poTermsDesc;
    private $type;
    private $shipVia;
    private $otherDesc;
    private $iD_warehouses;
    private $discountPorc;
    private $discountDays;
    private $authBy;
    private $auth;
    private $status;
    private $etd;
    private $date;
    private $time;
    private $iD_admin_users;

    function __construct() {
        parent::__construct();
        $this->table_source = "sl_purchaseorders";
        $this->field_list = array(
            'ID_purchaseorders',
            'ID_vendors',
            'RefNumber',
            'PODate',
            'CancelDate',
            'POTerms',
            'POTerms_Desc',
            'Type',
            'Shipvia',
            'Other_Desc',
            'ID_warehouses',
            'DiscountPorc',
            'DiscountDays',
            'AuthBy',
            'Auth',
            'Status',
            'Etd',
            'Date',
            'Time',
            'ID_admin_users'
        );
        
        $this->type  = "Purchase Order";
    }

    public function getID_purchaseorders() {
        return $this->iD_purchaseorders;
    }

    public function setID_purchaseorders($iD_purchaseorders) {
        $this->iD_purchaseorders = $iD_purchaseorders;
    }

    public function getID_vendors() {
        return $this->iD_vendors;
    }

    public function setID_vendors($iD_vendors) {
        $this->iD_vendors = $iD_vendors;
    }

    public function getRefNumber() {
        return $this->refNumber;
    }

    public function setRefNumber($refNumber) {
        $this->refNumber = $refNumber;
    }

    public function getPoDate() {
        return $this->poDate;
    }

    public function setPoDate($poDate) {
        $this->poDate = $poDate;
    }

    public function getCancelDate() {
        return $this->cancelDate;
    }

    public function setCancelDate($cancelDate) {
        $this->cancelDate = $cancelDate;
    }

    public function getPoTerms() {
        return $this->poTerms;
    }

    public function setPoTerms($poTerms) {
        $this->poTerms = $poTerms;
    }

    public function getPoTermsDesc() {
        return $this->poTermsDesc;
    }

    public function setPoTermsDesc($poTermsDesc) {
        $this->poTermsDesc = $poTermsDesc;
    }

    public function getType() {
        return $this->type;
    }

    public function setType($type) {
        $this->type = $type;
    }

    public function getShipVia() {
        return $this->shipVia;
    }

    public function setShipVia($shipVia) {
        $this->shipVia = $shipVia;
    }

    public function getOtherDesc() {
        return $this->otherDesc;
    }

    public function setOtherDesc($otherDesc) {
        $this->otherDesc = $otherDesc;
    }

    public function getID_warehouses() {
        return $this->iD_warehouses;
    }

    public function setID_warehouses($iD_warehouses) {
        $this->iD_warehouses = $iD_warehouses;
    }

    public function getDiscountPorc() {
        return $this->discountPorc;
    }

    public function setDiscountPorc($discountPorc) {
        $this->discountPorc = $discountPorc;
    }

    public function getDiscountDays() {
        return $this->discountDays;
    }

    public function setDiscountDays($discountDays) {
        $this->discountDays = $discountDays;
    }

    public function getAuthBy() {
        return $this->authBy;
    }

    public function setAuthBy($authBy) {
        $this->authBy = $authBy;
    }

    public function getAuth() {
        return $this->auth;
    }

    public function setAuth($auth) {
        $this->auth = $auth;
    }

    public function getStatus() {
        return $this->status;
    }

    public function setStatus($status) {
        $this->status = $status;
    }

    public function getEtd() {
        return $this->etd;
    }

    public function setEtd($etd) {
        $this->etd = $etd;
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