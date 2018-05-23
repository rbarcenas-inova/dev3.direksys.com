<?php
require_once 'BaseDTO.php';


/**
 * Description
 *
 * @author L.C.I Cesar Cedillo
 */
class WarehousesDTO extends BaseDTO {
    private $iD_warehouses;
    private $name;
    private $type;
    private $address1;
    private $address2;
    private $address3;
    private $city;
    private $state;
    private $Zip;
    private $coverage;
    private $notes;
    private $dropShipper;
    private $wManager;
    private $codList;
    private $status;
    private $date;
    private $time;
    private $iD_admin_users;
    
    function __construct() {
        parent::__construct();
        
        $this->table_source = 'sl_warehouses';
        $this->field_list = array(
            'ID_warehouses',  
            'Name',  
            'Type',  
            'Address1',  
            'Address2',  
            'Address3',  
            'City',  
            'State',  
            'Zip',  
            'Coverage',  
            'Notes',  
            'DropShipper',  
            'WManager',  
            'codlist',  
            'Status',  
            'Date',  
            'Time',  
            'ID_admin_users'
            );
        
        
    }
    
    public function getID_warehouses() {
        return $this->iD_warehouses;
    }

    public function setID_warehouses($iD_warehouses) {
        $this->iD_warehouses = $iD_warehouses;
    }

    public function getName() {
        return $this->name;
    }

    public function setName($name) {
        $this->name = $name;
    }

    public function getType() {
        return $this->type;
    }

    public function setType($type) {
        $this->type = $type;
    }

    public function getAddress1() {
        return $this->address1;
    }

    public function setAddress1($address1) {
        $this->address1 = $address1;
    }

    public function getAddress2() {
        return $this->address2;
    }

    public function setAddress2($address2) {
        $this->address2 = $address2;
    }

    public function getAddress3() {
        return $this->address3;
    }

    public function setAddress3($address3) {
        $this->address3 = $address3;
    }

    public function getCity() {
        return $this->city;
    }

    public function setCity($city) {
        $this->city = $city;
    }

    public function getState() {
        return $this->state;
    }

    public function setState($state) {
        $this->state = $state;
    }

    public function getZip() {
        return $this->Zip;
    }

    public function setZip($Zip) {
        $this->Zip = $Zip;
    }

    public function getCoverage() {
        return $this->coverage;
    }

    public function setCoverage($coverage) {
        $this->coverage = $coverage;
    }

    public function getNotes() {
        return $this->notes;
    }

    public function setNotes($notes) {
        $this->notes = $notes;
    }

    public function getDropShipper() {
        return $this->dropShipper;
    }

    public function setDropShipper($dropShipper) {
        $this->dropShipper = $dropShipper;
    }

    public function getWManager() {
        return $this->wManager;
    }

    public function setWManager($wManager) {
        $this->wManager = $wManager;
    }

    public function getCodList() {
        return $this->codList;
    }

    public function setCodList($codList) {
        $this->codList = $codList;
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