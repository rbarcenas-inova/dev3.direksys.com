<?php

require_once 'BaseDTO.php';

/**
 * Description
 *
 * @author L.C.I Cesar Cedillo
 */
class CustomersDTO extends BaseDTO {

    private $iD_customers;
    private $cID;
    private $firstName;
    private $lastName;
    private $lastName2;
    private $sex;
    private $phone1;
    private $address1;
    private $address2;
    private $address3;
    private $urbanization;
    private $city;
    private $state;
    private $zip;
    private $country;

    function __construct() {
        parent::__construct();
        $this->table_source = 'sl_customers';
        $this->field_list = array(
            'ID_customers',
            'CID',
            'FirstName',
            'LastName1',
            'LastName2',
            'Sex',
            'Phone1',
            'Address1',
            'Address2',
            'Address3',
            'Urbanization',
            'City',
            'State',
            'Zip',
            'Country'
        );

        $this->iD_customers = 0;
        $this->cID = 0;
        $this->firstName = "";
        $this->lastName = "";
        $this->lastName2 = "";
        $this->sex;
        $this->phone1;
        $this->address1;
        $this->address2 = NULL;
        $this->address3 = NULL;
        $this->urbanization = "";
        $this->city;
        $this->state;
        $this->zip;
        $this->country = NULL;
    }

    public function getID_customers() {
        return $this->iD_customers;
    }

    public function setID_customers($iD_customers) {
        $this->iD_customers = $iD_customers;
    }

    public function getCID() {
        return $this->cID;
    }

    public function setCID($cID) {
        $this->cID = $cID;
    }

    public function getFirstName() {
        return $this->firstName;
    }

    public function setFirstName($firstName) {
        $this->firstName = $firstName;
    }

    public function getLastName() {
        return $this->lastName;
    }

    public function setLastName($lastName) {
        $this->lastName = $lastName;
    }

    public function getLastName2() {
        return $this->lastName2;
    }

    public function setLastName2($lastName2) {
        $this->lastName2 = $lastName2;
    }

    public function getSex() {
        return $this->sex;
    }

    public function setSex($sex) {
        $this->sex = $sex;
    }

    public function getPhone1() {
        return $this->phone1;
    }

    public function setPhone1($phone1) {
        $this->phone1 = $phone1;
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

    public function getUrbanization() {
        return $this->urbanization;
    }

    public function setUrbanization($urbanization) {
        $this->urbanization = $urbanization;
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
        return $this->zip;
    }

    public function setZip($zip) {
        $this->zip = $zip;
    }

    public function getCountry() {
        return $this->country;
    }

    public function setCountry($country) {
        $this->country = $country;
    }

}

?>