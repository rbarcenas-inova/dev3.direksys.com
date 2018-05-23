<?php

require_once 'BaseDTO.php';

/**
 * Description
 *
 * @author L.C.I Cesar Cedillo
 */
class ReturnsUpcsDTO extends BaseDTO {

    private $iD_returns_upcs;
    private $iD_returns;
    private $uPC;
    private $iD_warehouses;
    private $inOrder;
    private $status;
    private $location;
    private $quantity;
    private $date;
    private $time;
    private $iD_admin_users;

    function __construct() {
        parent::__construct();
        $this->table_source = 'sl_returns_upcs';
        $this->field_list = array( 
            'ID_returns_upcs',  
            'ID_returns',  
            'UPC',  
            'ID_warehouses',  
            'InOrder',  
            'Status',  
            'Location',  
            'Quantity',  
            'Date',  
            'Time',  
            'ID_admin_users'
            );

        $this->iD_warehouses = 0;
        $this->inOrder = "yes";
        $this->location = "";
    }
    
    public function getID_returns_upcs() {
        return $this->iD_returns_upcs;
    }

    public function setID_returns_upcs($iD_returns_upcs) {
        $this->iD_returns_upcs = $iD_returns_upcs;
    }

    public function getID_returns() {
        return $this->iD_returns;
    }

    public function setID_returns($iD_returns) {
        $this->iD_returns = $iD_returns;
    }

    public function getUPC() {
        return $this->uPC;
    }

    public function setUPC($uPC) {
        $this->uPC = $uPC;
    }

    public function getID_warehouses() {
        return $this->iD_warehouses;
    }

    public function setID_warehouses($iD_warehouses) {
        $this->iD_warehouses = $iD_warehouses;
    }

    public function getInOrder() {
        return $this->inOrder;
    }

    public function setInOrder($inOrder) {
        $this->inOrder = $inOrder;
    }

    public function getStatus() {
        return $this->status;
    }

    public function setStatus($status) {
        $this->status = $status;
    }

    public function getLocation() {
        return $this->location;
    }

    public function setLocation($location) {
        $this->location = $location;
    }

    public function getQuantity() {
        return $this->quantity;
    }

    public function setQuantity($quantity) {
        $this->quantity = $quantity;
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