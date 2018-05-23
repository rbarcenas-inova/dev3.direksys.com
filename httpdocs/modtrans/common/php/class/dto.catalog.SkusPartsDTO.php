<?php

require_once 'BaseDTO.php';

/**
 * Description
 *
 * @author L.C.I Cesar Cedillo
 */
class SkusPartsDTO extends BaseDTO {
    
    private $iD_skus_parts;
    private $iD_skus_products;
    private $iD_parts;
    private $qty;
    private $date;
    private $time;
    private $iD_admin_users;

    function __construct() {
        parent::__construct();
        
        $this->table_source = "sl_skus_parts";
        $this->field_list = array(
            'ID_skus_parts',  
            'ID_sku_products',  
            'ID_parts',  
            'Qty',  
            'Date',  
            'Time',  
            'ID_admin_users'
        );
    }
    
    public function getID_skus_parts() {
        return $this->iD_skus_parts;
    }

    public function setID_skus_parts($iD_skus_parts) {
        $this->iD_skus_parts = $iD_skus_parts;
    }

    public function getID_skus_products() {
        return $this->iD_skus_products;
    }

    public function setID_skus_products($iD_skus_products) {
        $this->iD_skus_products = $iD_skus_products;
    }

    public function getID_parts() {
        return $this->iD_parts;
    }

    public function setID_parts($iD_parts) {
        $this->iD_parts = $iD_parts;
    }

    public function getQty() {
        return $this->qty;
    }

    public function setQty($qty) {
        $this->qty = $qty;
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