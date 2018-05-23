<?php

require_once 'BaseDTO.php';

/**
 * Description
 *
 * @author L.C.I Cesar Cedillo
 */
class VendorsDTO extends BaseDTO {

    private $iD_vendors;
    private $companyName;
    private $rFC;
    private $address;
    private $city;
    private $state;
    private $zip;
    private $country;
    private $phone;
    private $fax;
    private $webSite;
    private $comments;
    private $type;
    private $paymentTerms;
    private $shippingOptions;
    private $returnPolicy;
    private $discounts;
    private $airProgram;
    private $specialProgram;
    private $merchandiseFormat;
    private $status;
    private $date;
    private $time;
    private $iD_admin_users;

    function __construct() {
        parent::__construct();

        $this->table_source = 'sl_vendors';
        $this->field_list = array(
            'ID_vendors',
            'CompanyName',
            'RFC',
            'Address',
            'City',
            'State',
            'Zip',
            'Country',
            'Phone',
            'Fax',
            'WebSite',
            'Comments',
            //'Type',
            //'PaymentTerms',
            //'ShippingOptions',
            //'ReturnPolicy',
            //'Discounts',
            //'AirProgram',
            //'SpecialProgram',
            //'MerchandiseFormat',
            'Status',
            'Date',
            'Time',
            'ID_admin_users'
        );

        $this->iD_vendors = 0;
        $this->companyName = '';
    }

    public function getID_vendors() {
        return $this->iD_vendors;
    }

    public function setID_vendors($iD_vendors) {
        $this->iD_vendors = $iD_vendors;
    }

    public function getCompanyName() {
        return $this->companyName;
    }

    public function setCompanyName($companyName) {
        $this->companyName = $companyName;
    }

    public function getRFC() {
        return $this->rFC;
    }

    public function setRFC($rFC) {
        $this->rFC = $rFC;
    }

        
    public function getAddress() {
        return $this->address;
    }

    public function setAddress($address) {
        $this->address = $address;
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

    public function getPhone() {
        return $this->phone;
    }

    public function setPhone($phone) {
        $this->phone = $phone;
    }

    public function getFax() {
        return $this->fax;
    }

    public function setFax($fax) {
        $this->fax = $fax;
    }

    public function getWebSite() {
        return $this->webSite;
    }

    public function setWebSite($webSite) {
        $this->webSite = $webSite;
    }

    public function getComments() {
        return $this->comments;
    }

    public function setComments($comments) {
        $this->comments = $comments;
    }


    public function getPaymentTerms() {
        return $this->paymentTerms;
    }

    public function setPaymentTerms($paymentTerms) {
        $this->paymentTerms = $paymentTerms;
    }

    public function getShippingOptions() {
        return $this->shippingOptions;
    }

    public function setShippingOptions($shippingOptions) {
        $this->shippingOptions = $shippingOptions;
    }

    public function getReturnPolicy() {
        return $this->returnPolicy;
    }

    public function setReturnPolicy($returnPolicy) {
        $this->returnPolicy = $returnPolicy;
    }

    public function getDiscounts() {
        return $this->discounts;
    }

    public function setDiscounts($discounts) {
        $this->discounts = $discounts;
    }

    public function getAirProgram() {
        return $this->airProgram;
    }

    public function setAirProgram($airProgram) {
        $this->airProgram = $airProgram;
    }

    public function getSpecialProgram() {
        return $this->specialProgram;
    }

    public function setSpecialProgram($specialProgram) {
        $this->specialProgram = $specialProgram;
    }

    public function getMerchandiseFormat() {
        return $this->merchandiseFormat;
    }

    public function setMerchandiseFormat($merchandiseFormat) {
        $this->merchandiseFormat = $merchandiseFormat;
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
