<?php
require_once 'BaseDTO.php';

/**
 * Description
 *
 * @author L.C.I Cesar Cedillo
 */
class PartsDTO extends BaseDTO {
    private $iD_parts;
    private $model;
    private $name;
    private $iD_categories;
    private $status;
    private $date;
    private $time;
    private $iD_admin_users;
    
    
    function __construct() {
       parent::__construct();

       $this->table_source = "sl_parts";
       $this->field_list = array(
           'ID_parts',  
           'Model',  
           'Name',  
           'ID_categories',  
           'Status',  
           'Date',  
           'Time',  
           'ID_admin_users'
       );

    }
    
    public function getID_parts() {
        return $this->iD_parts;
    }

    public function setID_parts($iD_parts) {
        $this->iD_parts = $iD_parts;
    }

    public function getModel() {
        return $this->model;
    }

    public function setModel($model) {
        $this->model = $model;
    }

    public function getName() {
        return $this->name;
    }

    public function setName($name) {
        $this->name = $name;
    }

    public function getID_categories() {
        return $this->iD_categories;
    }

    public function setID_categories($iD_categories) {
        $this->iD_categories = $iD_categories;
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