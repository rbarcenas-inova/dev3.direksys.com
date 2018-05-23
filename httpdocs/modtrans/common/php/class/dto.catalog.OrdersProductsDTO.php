<?php

require_once 'BaseDTO.php';

/**
 * Description
 *
 * @author L.C.I Cesar Cedillo
 */
class OrdersProductsDTO extends BaseDTO {

    private $iD_orders_products;
    private $iD_products;
    private $iD_orders;
    private $iD_packinglist;
    private $related_ID_products;
    private $quantity;
    private $salePrice;
    private $shipping;
    private $cost;
    private $tax;
    private $discount;
    private $fP;
    private $serialNumber;
    private $shpDate;
    private $tracking;
    private $shpProvider;
    private $postedDate;
    private $upSell;
    private $status;
    private $date;
    private $time;
    private $iD_admin_users;

    function __construct() {
        parent::__construct();

        $this->table_source = "sl_orders_products";
        $this->field_list = array(
            'ID_orders_products',
            'ID_products',
            'ID_orders',
            'ID_packinglist',
            'Related_ID_products',
            'Quantity',
            'SalePrice',
            'Shipping',
            'Cost',
            'Tax',
            'Discount',
            'FP',
            'SerialNumber',
            'ShpDate',
            'Tracking',
            'ShpProvider',
            'PostedDate',
            'Upsell',
            'Status',
            'Date',
            'Time',
            'ID_admin_users'
        );
                
        $this->iD_products = 100000000;
        $this->iD_orders = 0;
        $this->iD_packinglist = 0;        
        $this->related_ID_products = NULL;
        $this->salePrice = 0.00;
        $this->shipping = 0.00;
        $this->cost = 0.00;
        $this->tax = 0.00;
        $this->discount = 0.00;
        $this->fP = 1;               
        $this->status = "Active";
    }

    public function getID_orders_products() {
        return $this->iD_orders_products;
    }

    public function setID_orders_products($iD_orders_products) {
        $this->iD_orders_products = $iD_orders_products;
    }

    public function getID_products() {
        return $this->iD_products;
    }

    public function setID_products($iD_products) {
        $this->iD_products = $iD_products;
    }

    public function getID_orders() {
        return $this->iD_orders;
    }

    public function setID_orders($iD_orders) {
        $this->iD_orders = $iD_orders;
    }

    public function getID_packinglist() {
        return $this->iD_packinglist;
    }

    public function setID_packinglist($iD_packinglist) {
        $this->iD_packinglist = $iD_packinglist;
    }

    public function getRelated_ID_products() {
        return $this->related_ID_products;
    }

    public function setRelated_ID_products($related_ID_products) {
        $this->related_ID_products = $related_ID_products;
    }

    public function getQuantity() {
        return $this->quantity;
    }

    public function setQuantity($quantity) {
        $this->quantity = $quantity;
    }

    public function getSalePrice() {
        return $this->salePrice;
    }

    public function setSalePrice($salePrice) {
        $this->salePrice = $salePrice;
    }

    public function getShipping() {
        return $this->shipping;
    }

    public function setShipping($shipping) {
        $this->shipping = $shipping;
    }

    public function getCost() {
        return $this->cost;
    }

    public function setCost($cost) {
        $this->cost = $cost;
    }

    public function getTax() {
        return $this->tax;
    }

    public function setTax($tax) {
        $this->tax = $tax;
    }

    public function getDiscount() {
        return $this->discount;
    }

    public function setDiscount($discount) {
        $this->discount = $discount;
    }

    public function getFP() {
        return $this->fP;
    }

    public function setFP($fP) {
        $this->fP = $fP;
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

    public function getUpSell() {
        return $this->upSell;
    }

    public function setUpSell($upSell) {
        $this->upSell = $upSell;
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