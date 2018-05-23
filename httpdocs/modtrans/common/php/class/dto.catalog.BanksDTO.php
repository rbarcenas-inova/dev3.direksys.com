<?php

require_once 'BaseDTO.php';

/**
 * Description
 *
 * @author L.C.I Cesar Cedillo
 */
class BanksDTO extends BaseDTO {
    private $iD_banks;
    private $name;
    private $shortName;
    private $description;
    private $bankName;
    private $bankAddress;
    private $bankContact;
    private $bankContactPhone;
    private $currency;
    private $abaRouting;
    private $abaAch;
    private $abaWire;
    private $swift;
    private $subAccountOf;
    private $openingBalance;
    private $openingDate;
    private $checkReminder;
    private $status;
    private $date;
    private $time;
    private $iD_admin_users;
    
    function __construct() {
        parent::__construct();
        
        $this->table_source = 'sl_banks';
        $this->field_list = array(
            'ID_banks',  
            'Name',  
            'ShortName',  
            'Description',  
            'BankName',  
            'BankAddress',  
            'BankContact',  
            'BankContactPhone',  
            'Currency',  
            'ABA-Routing',  
            'ABA-ACH',  
            'ABA-Wire',  
            'SWIFT',  
            'SubAccountOf',  
            'OpeningBalance',  
            'OpeningDate',  
            'CheckReminder',  
            'Status',  
            'Date',  
            'Time',  
            'ID_admin_users'
        );
    }
    
    public function getID_banks() {
        return $this->iD_banks;
    }

    public function setID_banks($iD_banks) {
        $this->iD_banks = $iD_banks;
    }

    public function getName() {
        return $this->name;
    }

    public function setName($name) {
        $this->name = $name;
    }

    public function getShortName() {
        return $this->shortName;
    }

    public function setShortName($shortName) {
        $this->shortName = $shortName;
    }

    public function getDescription() {
        return $this->description;
    }

    public function setDescription($description) {
        $this->description = $description;
    }

    public function getBankName() {
        return $this->bankName;
    }

    public function setBankName($bankName) {
        $this->bankName = $bankName;
    }

    public function getBankAddress() {
        return $this->bankAddress;
    }

    public function setBankAddress($bankAddress) {
        $this->bankAddress = $bankAddress;
    }

    public function getBankContact() {
        return $this->bankContact;
    }

    public function setBankContact($bankContact) {
        $this->bankContact = $bankContact;
    }

    public function getBankContactPhone() {
        return $this->bankContactPhone;
    }

    public function setBankContactPhone($bankContactPhone) {
        $this->bankContactPhone = $bankContactPhone;
    }

    public function getCurrency() {
        return $this->currency;
    }

    public function setCurrency($currency) {
        $this->currency = $currency;
    }

    public function getAbaRouting() {
        return $this->abaRouting;
    }

    public function setAbaRouting($abaRouting) {
        $this->abaRouting = $abaRouting;
    }

    public function getAbaAch() {
        return $this->abaAch;
    }

    public function setAbaAch($abaAch) {
        $this->abaAch = $abaAch;
    }

    public function getAbaWire() {
        return $this->abaWire;
    }

    public function setAbaWire($abaWire) {
        $this->abaWire = $abaWire;
    }

    public function getSwift() {
        return $this->swift;
    }

    public function setSwift($swift) {
        $this->swift = $swift;
    }

    public function getSubAccountOf() {
        return $this->subAccountOf;
    }

    public function setSubAccountOf($subAccountOf) {
        $this->subAccountOf = $subAccountOf;
    }

    public function getOpeningBalance() {
        return $this->openingBalance;
    }

    public function setOpeningBalance($openingBalance) {
        $this->openingBalance = $openingBalance;
    }

    public function getOpeningDate() {
        return $this->openingDate;
    }

    public function setOpeningDate($openingDate) {
        $this->openingDate = $openingDate;
    }

    public function getCheckReminder() {
        return $this->checkReminder;
    }

    public function setCheckReminder($checkReminder) {
        $this->checkReminder = $checkReminder;
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