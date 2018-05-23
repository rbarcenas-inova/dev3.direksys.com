<?php

require_once 'BaseDTO.php';


/**
 * Description of dto
 *
 * @author ccedillo
 * @author Oscar Maldonado
 */
class InvoicesLinesDTO extends BaseDTO {

    private $iD_invoices_lines;
    private $iD_invoices;
    private $iD_orders;
    private $iD_creditmemos;
    private $iD_orders_products;
    private $lineNum;
    private $quantity;
    private $measuringUnit;
    private $referenceID;
    private $description;
    private $unitPrice;
    private $amount;
    private $tax;
    private $taxType;
    private $taxName;
    private $taxRate;
    private $discount;
    private $CustomsGLN;
    private $CustomsName;
    private $CustomsNum;
    private $CustomsDate;
    private $iD_sku;
    private $iD_sku_alias;
    private $size;
    private $packing_type;
    private $packing_unit;
    private $UPC;
    private $Date;
    private $Time;
    private $iDAdminUsers;
    private $extraID_field;
    private $palletInformation;
    private $prepactCant;
    
    function __construct() {
        parent::__construct();

        $this->table_source = 'cu_invoices_lines';
        $this->field_list = array(
            'ID_invoices_lines',
            'ID_invoices',
            'ID_orders',
            'ID_creditmemos',
            'ID_orders_products',
            'line_num',
            'quantity',
            'measuring_unit',
            'reference_id',
            'description',
            'unit_price',
            'amount',
            'tax',
            'tax_type',
            'tax_name',
            'tax_rate',
            'discount',
            'customs_gln',
            'customs_name',
            'customs_num',
            'customs_date',
            'ID_sku',
            'ID_sku_alias',
            'size',
            'packing_type',
            'packing_unit',
            'UPC',
            'Date',
            'Time',
            'ID_admin_users'
        );
    }

    public function getID_invoices_lines() {
        return $this->iD_invoices_lines;
    }

    public function setID_invoices_lines($iD_invoices_lines) {
        $this->iD_invoices_lines = $iD_invoices_lines;
    }

    public function getID_invoices() {
        return $this->iD_invoices;
    }

    public function setID_invoices($iD_invoices) {
        $this->iD_invoices = $iD_invoices;
    }

    public function getID_orders() {
        return $this->iD_orders;
    }

    public function setID_orders($iD_orders) {
        $this->iD_orders = $iD_orders;
    }

    public function getID_creditmemos() {
        return $this->iD_creditmemos;
    }

    public function setID_creditmemos($iD_creditmemos) {
        $this->iD_creditmemos = $iD_creditmemos;
    }

    public function getID_orders_products() {
        return $this->iD_orders_products;
    }

    public function setID_orders_products($iD_orders_products) {
        $this->iD_orders_products = $iD_orders_products;
    }
        
    public function getLineNum() {
        return $this->lineNum;
    }

    public function setLineNum($lineNum) {
        $this->lineNum = $lineNum;
    }

    public function getQuantity() {
        return $this->quantity;
    }

    public function setQuantity($quantity) {
        $this->quantity = $quantity;
    }

    public function getMeasuringUnit() {
        return $this->measuringUnit;
    }

    public function setMeasuringUnit($measuringUnit) {
        $this->measuringUnit = $measuringUnit;
    }

    public function getReferenceID() {
        return $this->referenceID;
    }

    public function setReferenceID($referenceID) {
        $this->referenceID = $referenceID;
    }

    public function getDescription() {
        return $this->description;
    }

    public function setDescription($description) {
        $this->description = $description;
    }

    public function getUnitPrice() {
        return $this->unitPrice;
    }

    public function setUnitPrice($unitPrice) {
        $this->unitPrice = $unitPrice;
    }

    public function getAmount() {
        return $this->amount;
    }

    public function setAmount($amount) {
        $this->amount = $amount;
    }

    public function getTax() {
        return $this->tax;
    }

    public function setTax($tax) {
        $this->tax = $tax;
    }

    public function getTaxType() {
        return $this->taxType;
    }

    public function setTaxType($taxType) {
        $this->taxType = $taxType;
    }

    public function getTaxName() {
        return $this->taxName;
    }

    public function setTaxName($taxName) {
        $this->taxName = $taxName;
    }

    public function getTaxRate() {
        return $this->taxRate;
    }

    public function setTaxRate($taxRate) {
        $this->taxRate = $taxRate;
    }

    public function getDiscount() {
        return $this->discount;
    }

    public function setDiscount($discount) {
        $this->discount = $discount;
    }

    public function getCustomsGLN() {
        return $this->CustomsGLN;
    }
    public function setCustomsGLN($CustomsGLN) {
        $this->CustomsGLN = $CustomsGLN;
    }

    public function getCustomsName() {
        return $this->CustomsName;
    }
    public function setCustomsName($CustomsName) {
        $this->CustomsName = $CustomsName;
    }

    public function getCustomsNum() {
        return $this->CustomsNum;
    }
    public function setCustomsNum($CustomsNum) {
        $this->CustomsNum = $CustomsNum;
    }

    public function getCustomsDate() {
        return $this->CustomsDate;
    }
    public function setCustomsDate($CustomsDate) {
        $this->CustomsDate = $CustomsDate;
    }


    public function getIdSku() {
        return $this->iD_sku;
    }
    public function setIdSku($iD_sku) {
        $this->iD_sku = $iD_sku;
    }

    public function getIdSkuAlias() {
        return $this->iD_sku_alias;
    }
    public function setIdSkuAlias($iD_sku_alias) {
        $this->iD_sku_alias = $iD_sku_alias;
    }

    public function getSize() {
        return $this->size;
    }
    public function setSize($size) {
        $this->size = $size;
    }

    public function getPackingType() {
        return $this->packing_type;
    }
    public function setPackingType($packing_type) {
        $this->packing_type = $packing_type;
    }

    public function getPackingUnit() {
        return $this->packing_unit;
    }
    public function setPackingUnit($packing_unit) {
        $this->packing_unit = $packing_unit;
    }
    
    public function getUPC() {
        return $this->UPC;
    }
    public function setUPC($UPC) {
        $this->UPC = $UPC;
    }

    public function getDate() {
        return $this->Date;
    }

    public function setDate($Date) {
        $this->Date = $Date;
    }

    public function getTime() {
        return $this->Time;
    }

    public function setTime($Time) {
        $this->Time = $Time;
    }

    public function getID_admin_users() {
        return $this->iDAdminUsers;
    }

    public function setID_admin_users($iDAdminUsers) {
        $this->iDAdminUsers = $iDAdminUsers;
    }

    public function getExtraID_field() {
        return $this->extraID_field;
    }

    public function setExtraID_field($extraID_field) {
        $this->extraID_field = $extraID_field;
    }


    public function getPalletInformation() {
        return $this->palletInformation;
    }

    public function setPalletInformation($palletInformation) {
        $this->palletInformation = $palletInformation;
    }

    public function getPrepactCant() {
        return $this->prepactCant;
    }

    public function setPrepactCant($prepactCant) {
        $this->prepactCant = $prepactCant;
    }


}

?>