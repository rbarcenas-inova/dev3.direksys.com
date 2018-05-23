<?php

require_once 'BaseDTO.php';


/**
 * Description
 *
 * @author L.C.I Cesar Cedillo
 */
class OrdersDateCodDTO extends BaseDTO {
    
    private $iD_orders_datecod;
    private $iD_orders;
    private $iD_warehouses;
    private $dateCod;
    private $dateCancelled;
    private $status;
    private $time;
    private $iD_admin_users;
    
    
    function __construct() {
        parent::__construct();
        
        $this->table_source = 'sl_orders_datecod';
        $this->field_list = array(
            'ID_orders_datecod',  
            'ID_orders',  
            'ID_warehouses',  
            'DateCOD',  
            'DateCancelled',  
            'Status',  
            'Time',  
            'ID_admin_users'
        );                
    }
    
    public function getID_orders_datecod() {
        return $this->iD_orders_datecod;
    }

    public function setID_orders_datecod($iD_orders_datecod) {
        $this->iD_orders_datecod = $iD_orders_datecod;
    }

    public function getID_orders() {
        return $this->iD_orders;
    }

    public function setID_orders($iD_orders) {
        $this->iD_orders = $iD_orders;
    }

    public function getID_warehouses() {
        return $this->iD_warehouses;
    }

    public function setID_warehouses($iD_warehouses) {
        $this->iD_warehouses = $iD_warehouses;
    }

    public function getDateCod() {
        return $this->dateCod;
    }

    public function setDateCod($dateCod) {
        $this->dateCod = $dateCod;
    }

    public function getDateCancelled() {
        return $this->dateCancelled;
    }

    public function setDateCancelled($dateCancelled) {
        $this->dateCancelled = $dateCancelled;
    }

    public function getStatus() {
        return $this->status;
    }

    public function setStatus($status) {
        $this->status = $status;
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