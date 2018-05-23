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
class WarehousesLocationDTO extends BaseDTO {

    private $iD_warehouses_location;
    private $idWarehouses;
    private $idProducts;
    private $location;
    private $quantity;
    private $date;
    private $time;
    private $iD_admin_users;

    function __construct() {
        parent::__construct();

        $this->table_source = 'sl_warehouses_location';
        $this->field_list = array(
            'ID_warehouses_location',
            'ID_warehouses',
            'ID_products',
            'Location',
            'Quantity',
            'Date',
            'Time',
            'ID_admin_users'
        );

        $this->location = "";
    }

    public function getID_warehouses_location() {
        return $this->iD_warehouses_location;
    }

    public function setID_warehouses_location($iD_warehouses_location) {
        $this->iD_warehouses_location = $iD_warehouses_location;
    }

    public function getIdWarehouses() {
        return $this->idWarehouses;
    }

    public function setIdWarehouses($idWarehouses) {
        $this->idWarehouses = $idWarehouses;
    }

    public function getIdProducts() {
        return $this->idProducts;
    }

    public function setIdProducts($idProducts) {
        $this->idProducts = $idProducts;
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