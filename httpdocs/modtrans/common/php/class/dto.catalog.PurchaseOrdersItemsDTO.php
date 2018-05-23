<?php

require_once 'BaseDTO.php';

/**
 * Description
 *
 * @author L.C.I Cesar Cedillo
 */
class PurchaseOrdersItemsDTO extends BaseDTO {
    private $iD_purchaseorders_items;
    private $iD_purchaseorders;
    private $iD_products;
    private $qty;
    private $recieved;
    private $price;
    private $date;
    private $time;
    private $iD_admin_users;
    
    
    function __construct() {
        parent::__construct();
       
        $this->table_source = 'sl_purchaseorders_items'; 
        $this->field_list = array(
            'ID_purchaseorders_items',  
            'ID_purchaseorders',  
            'ID_products',  
            'Qty',  
            'Received',  
            'Price',  
            'Date',  
            'Time',  
            'ID_admin_users'
            );       
    }
    
    public function getID_purchaseorders_items() {
        return $this->iD_purchaseorders_items;
    }

    public function setID_purchaseorders_items($iD_purchaseorders_items) {
        $this->iD_purchaseorders_items = $iD_purchaseorders_items;
    }

    public function getID_purchaseorders() {
        return $this->iD_purchaseorders;
    }

    public function setID_purchaseorders($iD_purchaseorders) {
        $this->iD_purchaseorders = $iD_purchaseorders;
    }

    public function getID_products() {
        return $this->iD_products;
    }

    public function setID_products($iD_products) {
        $this->iD_products = $iD_products;
    }

    public function getQty() {
        return $this->qty;
    }

    public function setQty($qty) {
        $this->qty = $qty;
    }

    public function getRecieved() {
        return $this->recieved;
    }

    public function setRecieved($recieved) {
        $this->recieved = $recieved;
    }

    public function getPrice() {
        return $this->price;
    }

    public function setPrice($price) {
        $this->price = $price;
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
