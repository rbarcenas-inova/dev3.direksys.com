<?php

require_once 'BaseDTO.php';

/**
 * Description
 *
 * @author L.C.I Cesar Cedillo
 */
class SkusDTO extends BaseDTO {
    
    private $iD_skus;
    private $iD_sku_products;
    private $iD_products;
    private $vendorSKU;
    private $uPC;
    private $isSet;
    private $choice1;
    private $choice2;
    private $choice3;
    private $choice4;
    private $status;
    private $date;
    private $time;
    private $iD_admin_users;

    function __construct() {
        parent::__construct();
        
        $this->table_source = "sl_skus";
        $this->field_list = array(
            'ID_skus',  
            'ID_sku_products',  
            'ID_products',  
            'VendorSKU',  
            'UPC',  
            'IsSet',  
            'choice1',  
            'choice2',  
            'choice3',  
            'choice4',  
            'Status',  
            'Date',  
            'Time',  
            'ID_admin_users'
        );
    }
   
    public function getID_skus() {
        return $this->iD_skus;
    }

    public function setID_skus($iD_skus) {
        $this->iD_skus = $iD_skus;
    }

    public function getID_sku_products() {
        return $this->iD_sku_products;
    }

    public function setID_sku_products($iD_sku_products) {
        $this->iD_sku_products = $iD_sku_products;
    }

    public function getID_products() {
        return $this->iD_products;
    }

    public function setID_products($iD_products) {
        $this->iD_products = $iD_products;
    }

    public function getVendorSKU() {
        return $this->vendorSKU;
    }

    public function setVendorSKU($vendorSKU) {
        $this->vendorSKU = $vendorSKU;
    }

        
    public function getUPC() {
        return $this->uPC;
    }

    public function setUPC($uPC) {
        $this->uPC = $uPC;
    }

    public function getIsSet() {
        return $this->isSet;
    }

    public function setIsSet($isSet) {
        $this->isSet = $isSet;
    }

    public function getChoice1() {
        return $this->choice1;
    }

    public function setChoice1($choice1) {
        $this->choice1 = $choice1;
    }

    public function getChoice2() {
        return $this->choice2;
    }

    public function setChoice2($choice2) {
        $this->choice2 = $choice2;
    }

    public function getChoice3() {
        return $this->choice3;
    }

    public function setChoice3($choice3) {
        $this->choice3 = $choice3;
    }

    public function getChoice4() {
        return $this->choice4;
    }

    public function setChoice4($choice4) {
        $this->choice4 = $choice4;
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