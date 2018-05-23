<?php
require_once 'BaseDTO.php';


/**
 * Description
 *
 * @author L.C.I Cesar Cedillo
 */
class OrdersPartsDTO extends BaseDTO{
    
    private $iD_orders_parts;
    private $iD_parts;
    private $iD_orders_products;
    private $quantity;
    private $cost;
    private $serialNumber;
    private $shpDate;
    private $tracking;
    private $shpProvider;
    private $postedDate;
    private $status;
    private $date;
    private $time;
    private $iD_admin_users;
            
    function __construct() {
        parent::__construct();
        
        $this->table_source = 'sl_orders_parts';
        $this->field_list = array(
            'ID_orders_parts',  
            'ID_parts',  
            'ID_orders_products',  
            'Quantity',  
            'Cost',  
            'SerialNumber',  
            'ShpDate',  
            'Tracking',  
            'ShpProvider',  
            'PostedDate',  
            'Status',  
            'Date',  
            'Time',  
            'ID_admin_users'
        );
        
        $this->cost = 0.00;
        $this->serialNumber = NULL;
        //$this->shpDate = "0000-00-00";    // misma fecha que postedDate
        //$this->tracking = "Local";
        //$this->shpProvider = "Local";
        //$this->postedDate = "0000-00-00";
        $this->status = "Shipped";        
    }
 
    public function getID_orders_parts() {
        return $this->iD_orders_parts;
    }

    public function setID_orders_parts($iD_orders_parts) {
        $this->iD_orders_parts = $iD_orders_parts;
    }

    public function getID_parts() {
        return $this->iD_parts;
    }

    public function setID_parts($iD_parts) {
        $this->iD_parts = $iD_parts;
    }

    public function getID_orders_products() {
        return $this->iD_orders_products;
    }

    public function setID_orders_products($iD_orders_products) {
        $this->iD_orders_products = $iD_orders_products;
    }

    public function getQuantity() {
        return $this->quantity;
    }

    public function setQuantity($quantity) {
        $this->quantity = $quantity;
    }

    public function getCost() {
        return $this->cost;
    }

    public function setCost($cost) {
        $this->cost = $cost;
    }

    public function getSerialNumber() {
        return $this->serialNumber;
    }

    public function setSerialNumber($serialNumber) {
        $this->serialNumber = $serialNumber;
    }

    public function getShpDate() {
        return $this->shpDate;
    }

    public function setShpDate($shpDate) {
        $this->shpDate = $shpDate;
    }

    public function getTracking() {
        return $this->tracking;
    }

    public function setTracking($tracking) {
        $this->tracking = $tracking;
    }

    public function getShpProvider() {
        return $this->shpProvider;
    }

    public function setShpProvider($shpProvider) {
        $this->shpProvider = $shpProvider;
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