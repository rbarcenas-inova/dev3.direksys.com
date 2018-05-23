<?php

require_once 'BaseDTO.php';

/**
 * Description
 *
 * @author L.C.I Cesar Cedillo
 */
class OrdersDTO extends BaseDTO {

    private $iD_orders;           // int
    private $trackOrderNumber;    // int: NULL
    private $iD_customers;        // int
    private $address1;            // varchar
    private $address2;            // varchar: NULL
    private $address3;            // varchar: NULL
    private $urbanization;        // varchar: NULL
    private $city;                // varchar
    private $state;               // enum
    private $zip;                 // varchar    
    private $country;             // varchar: NULL
    private $billingNotes;        // text: NULL
    private $shpType;             // int
    private $shpName;             // varchar: NULL
    private $shpAddress1;         // varchar
    private $shpAddress2;         // varchar: NULL
    private $shpAddress3;         // varchar: NULL
    private $shpUrbanization;     // varchar: NULL
    private $shpCity;             // varchar
    private $shpState;            // enum
    private $shpZip;              // varchar: NULL
    private $shpCountry;          // varchar: NULL
    private $shpNotes;            // varchar: NULL
    private $orderNotes;          // text: NULL
    private $orderQty;            // decimal: NULL
    private $orderShp;            // decimal: NULL
    private $orderDisc;            // decimal: NULL
    private $orderTax;            // decimal: NULL
    private $orderNet;            // decimal: NULL
    private $postedDate;          // date: NULL
    private $iD_priceLevels;       // int: NULL
    private $daysPay;             // varchar: NULL
    private $iD_ordersRelated;    // int: NULL;  
    private $question1;
    private $question2;
    private $question3;
    private $question4;
    private $question5;
    private $answer1;
    private $answer2;
    private $answer3;
    private $answer4;
    private $answer5;
    private $repeatedCustomer;    //enum: NULL
    private $cupon;               // int: NULL;
    private $flags;               // bigint: NULL;
    private $dNIS;                // int: NULL;
    private $iD_salesOrigins;     // int: NULL;
    private $iD_mediaContracts;   // int: NULL;
    private $dIDS7;               // int: NULL;
    private $pType;               // enum; Default: COD
    private $letter;              // int: NULL;
    private $iD_warehouses;       // int: NULL;
    private $firstCall;           // enum: null
    private $language;            // enum: null
    private $statusPrd;           // enum
    private $statusPay;           // enum
    private $status;              // enum
    private $date;                // date
    private $time;                // time
    private $iD_adminUsers;       // int 

    function __construct() {
        parent::__construct();
        $this->table_source = 'sl_orders';
        
        $this->field_list = array("ID_orders",
        //    "trackordernumber",
            "ID_customers",
            "Address1",
            "Address2",
            "Address3",
            "Urbanization",
            "City",
            "State",
            "Zip",
            "Country",
        //    "BillingNotes",
            "shp_type",
            "shp_name",
            "shp_Address1",
            "shp_Address2",
            "shp_Address3",
            "shp_Urbanization",
            "shp_City",
            "shp_State",
            "shp_Zip",
            "shp_Country",
            "shp_Notes",
            "OrderNotes",
            "OrderQty",
            "OrderShp",
            "OrderDisc",
            "OrderTax",
            "OrderNet",
            "PostedDate",
        //    "ID_pricelevels",
        //    "dayspay",
            "ID_orders_related",
        //    "question1",
        //    "answer1",
        //    "question2",
        //    "answer2",
        //    "question3",
        //    "answer3",
        //    "question4",
        //    "answer4",
        //    "question5",
        //    "answer5",
            "repeatedcustomer",
        //    "Coupon",
        //    "Flags",
            "DNIS",
        //    "ID_salesorigins",
            "ID_mediacontracts",
        //    "DIDS7",
            "Ptype",
        //    "Letter",
            "ID_warehouses",
        //    "first_call",
            "language",
            "StatusPrd",
            "StatusPay",
            "Status",
            "Date",
            "Time",
            "ID_admin_users");
        
        $this->iD_customers  = 0;
        $this->address1 = "";
        $this->address2 = "";
        $this->address3 = "";
        $this->city = "";
        $this->state = "";
        $this->zip = "";       
        $this->shpType = "";
        $this->shpAddress1 = "";
        //$this->shpAddress2 = "";
        //$this->shpAddress3 = "";
        $this->shpCity = "";
        $this->shpState = "";
        $this->shpZip = "";
        $this->orderQty = number_format(0.00, 2);
        $this->orderDisc = number_format(0.00, 2);
        $this->orderTax = number_format(0.00, 2);
        $this->orderNet = number_format(0.00, 2);
        $this->orderShp = number_format(0.00, 2);
        $this->pType = "COD";
        $this->language = "spanish";                        
        $this->statusPrd = "None";
        $this->statusPay = "None";
        $this->status = "Shipped";
        //$this->dNIS = 0;
        //$this->iD_mediaContracts = 0;
        //$this->iD_warehouses = NULL;
        $this->iD_adminUsers =  0;
    }
    
    public function getID_orders() {
        return $this->iD_orders;
    }

    public function setID_orders($iD_orders) {
        $this->iD_orders = $iD_orders;
    }

    public function getTrackOrderNumber() {
        return $this->trackOrderNumber;
    }

    public function setTrackOrderNumber($trackOrderNumber) {
        $this->trackOrderNumber = $trackOrderNumber;
    }

    public function getID_customers() {
        return $this->iD_customers;
    }

    public function setID_customers($iD_customers) {
        $this->iD_customers = $iD_customers;
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

    public function getBillingNotes() {
        return $this->billingNotes;
    }

    public function setBillingNotes($billingNotes) {
        $this->billingNotes = $billingNotes;
    }

    public function getShpType() {
        return $this->shpType;
    }

    public function setShpType($shpType) {
        $this->shpType = $shpType;
    }

    public function getShpName() {
        return $this->shpName;
    }

    public function setShpName($shpName) {
        $this->shpName = $shpName;
    }

    public function getShpAddress1() {
        return $this->shpAddress1;
    }

    public function setShpAddress1($shpAddress1) {
        $this->shpAddress1 = $shpAddress1;
    }

    public function getShpAddress2() {
        return $this->shpAddress2;
    }

    public function setShpAddress2($shpAddress2) {
        $this->shpAddress2 = $shpAddress2;
    }

    public function getShpAddress3() {
        return $this->shpAddress3;
    }

    public function setShpAddress3($shpAddress3) {
        $this->shpAddress3 = $shpAddress3;
    }

    public function getShpUrbanization() {
        return $this->shpUrbanization;
    }

    public function setShpUrbanization($shpUrbanization) {
        $this->shpUrbanization = $shpUrbanization;
    }

    public function getShpCity() {
        return $this->shpCity;
    }

    public function setShpCity($shpCity) {
        $this->shpCity = $shpCity;
    }

    public function getShpState() {
        return $this->shpState;
    }

    public function setShpState($shpState) {
        $this->shpState = $shpState;
    }

    public function getShpZip() {
        return $this->shpZip;
    }

    public function setShpZip($shpZip) {
        $this->shpZip = $shpZip;
    }

    public function getShpCountry() {
        return $this->shpCountry;
    }

    public function setShpCountry($shpCountry) {
        $this->shpCountry = $shpCountry;
    }

    public function getShpNotes() {
        return $this->shpNotes;
    }

    public function setShpNotes($shpNotes) {
        $this->shpNotes = $shpNotes;
    }

    public function getOrderNotes() {
        return $this->orderNotes;
    }

    public function setOrderNotes($orderNotes) {
        $this->orderNotes = $orderNotes;
    }

    public function getOrderQty() {
        return $this->orderQty;
    }

    public function setOrderQty($orderQty) {
        $this->orderQty = $orderQty;
    }

    public function getOrderShp() {
        return $this->orderShp;
    }

    public function setOrderShp($orderShp) {
        $this->orderShp = $orderShp;
    }

    public function getOrderDisc() {
        return $this->orderDisc;
    }

    public function setOrderDisc($orderDisc) {
        $this->orderDisc = $orderDisc;
    }

    public function getOrderTax() {
        return $this->orderTax;
    }

    public function setOrderTax($orderTax) {
        $this->orderTax = $orderTax;
    }

    public function getOrderNet() {
        return $this->orderNet;
    }

    public function setOrderNet($orderNet) {
        $this->orderNet = $orderNet;
    }

    public function getPostedDate() {
        return $this->postedDate;
    }

    public function setPostedDate($postedDate) {
        $this->postedDate = $postedDate;
    }

    public function getID_priceLevels() {
        return $this->iD_priceLevels;
    }

    public function setID_priceLevels($iD_priceLevels) {
        $this->iD_priceLevels = $iD_priceLevels;
    }

    public function getDaysPay() {
        return $this->daysPay;
    }

    public function setDaysPay($daysPay) {
        $this->daysPay = $daysPay;
    }

    public function getID_ordersRelated() {
        return $this->iD_ordersRelated;
    }

    public function setID_ordersRelated($iD_ordersRelated) {
        $this->iD_ordersRelated = $iD_ordersRelated;
    }

    public function getQuestion1() {
        return $this->question1;
    }

    public function setQuestion1($question1) {
        $this->question1 = $question1;
    }

    public function getQuestion2() {
        return $this->question2;
    }

    public function setQuestion2($question2) {
        $this->question2 = $question2;
    }

    public function getQuestion3() {
        return $this->question3;
    }

    public function setQuestion3($question3) {
        $this->question3 = $question3;
    }

    public function getQuestion4() {
        return $this->question4;
    }

    public function setQuestion4($question4) {
        $this->question4 = $question4;
    }

    public function getQuestion5() {
        return $this->question5;
    }

    public function setQuestion5($question5) {
        $this->question5 = $question5;
    }

    public function getAnswer1() {
        return $this->answer1;
    }

    public function setAnswer1($answer1) {
        $this->answer1 = $answer1;
    }

    public function getAnswer2() {
        return $this->answer2;
    }

    public function setAnswer2($answer2) {
        $this->answer2 = $answer2;
    }

    public function getAnswer3() {
        return $this->answer3;
    }

    public function setAnswer3($answer3) {
        $this->answer3 = $answer3;
    }

    public function getAnswer4() {
        return $this->answer4;
    }

    public function setAnswer4($answer4) {
        $this->answer4 = $answer4;
    }

    public function getAnswer5() {
        return $this->answer5;
    }

    public function setAnswer5($answer5) {
        $this->answer5 = $answer5;
    }

    public function getRepeatedCustomer() {
        return $this->repeatedCustomer;
    }

    public function setRepeatedCustomer($repeatedCustomer) {
        $this->repeatedCustomer = $repeatedCustomer;
    }

    public function getCupon() {
        return $this->cupon;
    }

    public function setCupon($cupon) {
        $this->cupon = $cupon;
    }

    public function getFlags() {
        return $this->flags;
    }

    public function setFlags($flags) {
        $this->flags = $flags;
    }

    public function getDNIS() {
        return $this->dNIS;
    }

    public function setDNIS($dNIS) {
        $this->dNIS = $dNIS;
    }

    public function getID_salesOrigins() {
        return $this->iD_salesOrigins;
    }

    public function setID_salesOrigins($iD_salesOrigins) {
        $this->iD_salesOrigins = $iD_salesOrigins;
    }

    public function getID_mediaContracts() {
        return $this->iD_mediaContracts;
    }

    public function setID_mediaContracts($iD_mediaContracts) {
        $this->iD_mediaContracts = $iD_mediaContracts;
    }

    public function getDIDS7() {
        return $this->dIDS7;
    }

    public function setDIDS7($dIDS7) {
        $this->dIDS7 = $dIDS7;
    }

    public function getPType() {
        return $this->pType;
    }

    public function setPType($pType) {
        $this->pType = $pType;
    }

    public function getLetter() {
        return $this->letter;
    }

    public function setLetter($letter) {
        $this->letter = $letter;
    }

    public function getID_warehouses() {
        return $this->iD_warehouses;
    }

    public function setID_warehouses($iD_warehouses) {
        $this->iD_warehouses = $iD_warehouses;
    }

    public function getFirstCall() {
        return $this->firstCall;
    }

    public function setFirstCall($firstCall) {
        $this->firstCall = $firstCall;
    }

    public function getLanguage() {
        return $this->language;
    }

    public function setLanguage($language) {
        $this->language = $language;
    }

    public function getStatusPrd() {
        return $this->statusPrd;
    }

    public function setStatusPrd($statusPrd) {
        $this->statusPrd = $statusPrd;
    }

    public function getStatusPay() {
        return $this->statusPay;
    }

    public function setStatusPay($statusPay) {
        $this->statusPay = $statusPay;
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

    public function getID_adminUsers() {
        return $this->iD_adminUsers;
    }

    public function setID_adminUsers($iD_adminUsers) {
        $this->iD_adminUsers = $iD_adminUsers;
    }

}

?>