<?php

require_once 'BaseDTO.php';

/*
 * To change this template, choose Tools | Templates
 * and open the template in the editor.
 */

/**
 * Description of dto
 *
 * @author ccedillo
 * @author Oscar Maldonado
 * @author ivan.miranda
 */
class InvoicesDTO extends BaseDTO {

    private $ID_invoices;
    //private $ID_orders;
    private $ID_customers;
    private $docSerial;
    private $docNum;
    private $docDate;
    private $paymentType;
    private $paymentMethod;
    private $paymentDigits;
    private $invoiceNet;
    private $invoiceTotal;
    private $discount;
    private $totalTaxesDetained;
    private $totalTaxesTransfered;
    private $currency;
    private $currencyExchange;
    private $invoiceType;
    private $placeConsignment;
    private $expediterFiscalCode;
    private $expediterName;
    private $expediterRegimen;
    private $expediterFAddressStreet;
    private $expediterFAddressNum;
    private $expediterFAddressNum2;
    private $expediterFAddressUrbanization;
    private $expediterFAddressDistrict;
    private $expediterFAddressCity;
    private $expediterFAddressState;
    private $expediterFAddressCountry;
    private $expediterFAddressZipcode;
    private $expediterAddressStreet;
    private $expediterAddressNum;
    private $expediterAddressNum2;
    private $expediterAddressUrbanization;
    private $expediterAddressDistrict;
    private $expediterAddressCity;
    private $expediterAddressState;
    private $expediterAddressCountry;
    private $expediterAddressZipcode;
    private $customerFiscalCode;
    private $customerName;
    private $customerFAddressStreet;
    private $customerFAddressNum;
    private $customerFAddressNum2;
    private $customerFAddressUrbanization;
    private $customerFAddressDistrict;
    private $customerFAddressCity;
    private $customerFAddressState;
    private $customerFAddressCountry;
    private $customerFAddressZipcode;    
    private $customerShpAddressStreet;
    private $customerShpAddressNum;
    private $customerShpAddressNum2;
    private $customerShpAddressUrbanization;
    private $customerShpAddressDistrict;
    private $customerShpAddressCity;
    private $customerShpAddressState;
    private $customerShpAddressCountry;
    private $customerShpAddressZipcode;    
    private $xmlCFD;
    private $xmlCFDI;
    private $xmlAddenda;
    private $uuid;
    private $originalString;
    private $relatedID_invoice;
    private $iD_orders_alias;
    private $iD_orders_alias_date;
    private $exchangeReceipt;
    private $exchangeReceiptDate;
    private $creditDays;
    private $conditions;
    private $batchNum;
    private $imr_code;
    private $status;
    private $VendorID;
    private $CustomerShpaddressContact;
    private $CustomerShpaddressCode;
    private $CustomerShpaddressAlias;
    private $CustomerAddressGln;
    private $CustomerShpaddressGln;
    private $viewed;
    private $Date;
    private $Time;
    private $iDAdminUsers;
    private $extraField;
    private $numAduanas;
#Datos de XML (@ivan.miranda)
    private $xml_uuid;
    private $xml_fecha_emision;
    private $xml_fecha_certificacion;
    
    

    function __construct() {
        parent::__construct();

        $this->table_source = 'cu_invoices';

        $this->field_list = array(
            'ID_invoices',            
            #'ID_orders',
            'ID_customers',
            'doc_serial',
            'doc_num',
            'doc_date',
            'payment_type',
            'payment_method',
            'payment_digits',
            'invoice_net',
            'invoice_total',
            'discount',
            'total_taxes_detained',
            'total_taxes_transfered',
            'currency',
            'currency_exchange',
            'invoice_type',
            'place_consignment',
            'expediter_fcode',
            'expediter_fname',
            'expediter_fregimen',
            'expediter_faddress_street',
            'expediter_faddress_num',
            'expediter_faddress_num2',
            'expediter_faddress_urbanization',
            'expediter_faddress_district',
            'expediter_faddress_city',
            'expediter_faddress_state',
            'expediter_faddress_country',
            'expediter_faddress_zipcode',
            'expediter_address_street',
            'expediter_address_num',
            'expediter_address_num2',
            'expediter_address_urbanization',
            'expediter_address_district',
            'expediter_address_city',
            'expediter_address_state',
            'expediter_address_country',
            'expediter_address_zipcode',
            'customer_fcode',
            'customer_fname',
            'customer_address_street',
            'customer_shpaddress_num',
            'customer_shpaddress_num2',
            'customer_shpaddress_urbanization',
            'customer_shpaddress_district',
            'customer_shpaddress_city',
            'customer_shpaddress_state',
            'customer_shpaddress_country',
            'customer_shpaddress_zipcode',
            'customer_shpaddress_street',
            'customer_address_num',
            'customer_address_num2',
            'customer_address_urbanization',
            'customer_address_district',
            'customer_address_city',
            'customer_address_state',
            'customer_address_country',
            'customer_address_zipcode',            
            'xml_cfd',
            'xml_cfdi',
            'xml_addenda',
            'uuid',
            'original_string',
            'related_ID_invoices',
            'ID_orders_alias',
            'ID_orders_alias_date',
            'exchange_receipt',
            'exchange_receipt_date',
            'credit_days',
            'conditions',
            'batch_num',            
            'imr_code',
            'Status',
            'VendorID',
            'customer_shpaddress_contact',
            'customer_shpaddress_code',
            'customer_shpaddress_alias',
            'customer_address_gln',
            'customer_shpaddress_gln',
            'viewed',
            'Date',
            'Time',
            'ID_admin_users',
        #Soporte para datos de XML (@ivanmiranda)
            'xml_uuid',
            'xml_fecha_emision',
            'xml_fecha_certificacion'
        );
        /*
          $this->totalTaxesDetained = 0.00;
          $this->totalTaxesTransfered = 0.00;
          $this->currency = "MXP";
          $this->currencyExchange = "0.00";
          $this->invoiceType = "ingreso";
          $this->expediterAddressCountry = "MEXICO";
          $this->status = "nueva";
         */
    }

    public function getNumAduanas() {
        return $this->numAduanas;
    }

    public function setNumAduanas($numAduanas) {
        $this->numAduanas = $numAduanas;
    }

    public function getID_invoices() {
        return $this->ID_invoices;
    }

    public function setID_invoices($ID_invoices) {
        $this->ID_invoices = $ID_invoices;
    }
    /*
    public function getID_orders() {
        return $this->ID_orders;
    }

    public function setID_orders($ID_orders) {
        $this->ID_orders = $ID_orders;
    }
    */
    public function getID_customers() {
        return $this->ID_customers;
    }

    public function setID_customers($ID_customers) {
        $this->ID_customers = $ID_customers;
    }

    public function getDocSerial() {
        return $this->docSerial;
    }

    public function setDocSerial($docSerial) {
        $this->docSerial = $docSerial;
    }

    public function getDocNum() {
        return $this->docNum;
    }

    public function setDocNum($docNum) {
        $this->docNum = $docNum;
    }

    public function getDocDate() {
        return $this->docDate;
    }

    public function setDocDate($docDate) {
        $this->docDate = $docDate;
    }

    public function getPaymentType() {
        return $this->paymentType;
    }

    public function setPaymentType($paymentType) {
        $this->paymentType = $paymentType;
    }

    public function getPaymentMethod() {
        return $this->paymentMethod;
    }

    public function setPaymentMethod($paymentMethod) {
        $this->paymentMethod = $paymentMethod;
    }

    public function getPaymentDigits() {
        return $this->paymentDigits;
    }

    public function setPaymentDigits($paymentDigits) {
        $this->paymentDigits = $paymentDigits;
    }
        
    public function getInvoiceNet() {
        return $this->invoiceNet;
    }

    public function setInvoiceNet($invoiceNet) {
        $this->invoiceNet = $invoiceNet;
    }

    public function getInvoiceTotal() {
        return $this->invoiceTotal;
    }

    public function setInvoiceTotal($invoiceTotal) {
        $this->invoiceTotal = $invoiceTotal;
    }

    public function getDiscount() {
        return $this->discount;
    }

    public function setDiscount($discount) {
        $this->discount = $discount;
    }

    public function getTotalTaxesDetained() {
        return $this->totalTaxesDetained;
    }

    public function setTotalTaxesDetained($totalTaxesDetained) {
        $this->totalTaxesDetained = $totalTaxesDetained;
    }

    public function getTotalTaxesTransfered() {
        return $this->totalTaxesTransfered;
    }

    public function setTotalTaxesTransfered($totalTaxesTransfered) {
        $this->totalTaxesTransfered = $totalTaxesTransfered;
    }

    public function getCurrency() {
        return $this->currency;
    }

    public function setCurrency($currency) {
        $this->currency = $currency;
    }

    public function getCurrencyExchange() {
        return $this->currencyExchange;
    }

    public function setCurrencyExchange($currencyExchange) {
        $this->currencyExchange = $currencyExchange;
    }

    public function getInvoiceType() {
        return $this->invoiceType;
    }

    public function setInvoiceType($invoiceType) {
        $this->invoiceType = $invoiceType;
    }

    public function getPlaceConsignment() {
        return $this->placeConsignment;
    }

    public function setPlaceConsignment($placeConsignment) {
        $this->placeConsignment = $placeConsignment;
    }

    public function getExpediterFiscalCode() {
        return $this->expediterFiscalCode;
    }

    public function setExpediterFiscalCode($expediterFiscalCode) {
        $this->expediterFiscalCode = $expediterFiscalCode;
    }

    public function getExpediterName() {
        return $this->expediterName;
    }

    public function setExpediterName($expediterName) {
        $this->expediterName = $expediterName;
    }

    public function getExpediterRegimen() {
        return $this->expediterRegimen;
    }

    public function setExpediterRegimen($expediterRegimen) {
        $this->expediterRegimen = $expediterRegimen;
    }

    public function getExpediterFAddressStreet() {
        return $this->expediterFAddressStreet;
    }

    public function setExpediterFAddressStreet($expediterFAddressStreet) {
        $this->expediterFAddressStreet = $expediterFAddressStreet;
    }

    public function getExpediterFAddressNum() {
        return $this->expediterFAddressNum;
    }

    public function setExpediterFAddressNum($expediterFAddressNum) {
        $this->expediterFAddressNum = $expediterFAddressNum;
    }

    public function getExpediterFAddressNum2() {
        return $this->expediterFAddressNum2;
    }

    public function setExpediterFAddressNum2($expediterFAddressNum2) {
        $this->expediterFAddressNum2 = $expediterFAddressNum2;
    }

    public function getExpediterFAddressUrbanization() {
        return $this->expediterFAddressUrbanization;
    }

    public function setExpediterFAddressUrbanization($expediterFAddressUrbanization) {
        $this->expediterFAddressUrbanization = $expediterFAddressUrbanization;
    }

    public function getExpediterFAddressDistrict() {
        return $this->expediterFAddressDistrict;
    }

    public function setExpediterFAddressDistrict($expediterFAddressDistrict) {
        $this->expediterFAddressDistrict = $expediterFAddressDistrict;
    }

    public function getExpediterFAddressCity() {
        return $this->expediterFAddressCity;
    }

    public function setExpediterFAddressCity($expediterFAddressCity) {
        $this->expediterFAddressCity = $expediterFAddressCity;
    }

    public function getExpediterFAddressState() {
        return $this->expediterFAddressState;
    }

    public function setExpediterFAddressState($expediterFAddressState) {
        $this->expediterFAddressState = $expediterFAddressState;
    }

    public function getExpediterFAddressCountry() {
        return $this->expediterFAddressCountry;
    }

    public function setExpediterFAddressCountry($expediterFAddressCountry) {
        $this->expediterFAddressCountry = $expediterFAddressCountry;
    }

    public function getExpediterFAddressZipcode() {
        return $this->expediterFAddressZipcode;
    }

    public function setExpediterFAddressZipcode($expediterFAddressZipcode) {
        $this->expediterFAddressZipcode = $expediterFAddressZipcode;
    }

    public function getExpediterAddressStreet() {
        return $this->expediterAddressStreet;
    }

    public function setExpediterAddressStreet($expediterAddressStreet) {
        $this->expediterAddressStreet = $expediterAddressStreet;
    }

    public function getExpediterAddressNum() {
        return $this->expediterAddressNum;
    }

    public function setExpediterAddressNum($expediterAddressNum) {
        $this->expediterAddressNum = $expediterAddressNum;
    }

    public function getExpediterAddressNum2() {
        return $this->expediterAddressNum2;
    }

    public function setExpediterAddressNum2($expediterAddressNum2) {
        $this->expediterAddressNum2 = $expediterAddressNum2;
    }

    public function getExpediterAddressUrbanization() {
        return $this->expediterAddressUrbanization;
    }

    public function setExpediterAddressUrbanization($expediterAddressUrbanization) {
        $this->expediterAddressUrbanization = $expediterAddressUrbanization;
    }

    public function getExpediterAddressDistrict() {
        return $this->expediterAddressDistrict;
    }

    public function setExpediterAddressDistrict($expediterAddressDistrict) {
        $this->expediterAddressDistrict = $expediterAddressDistrict;
    }

    public function getExpediterAddressCity() {
        return $this->expediterAddressCity;
    }

    public function setExpediterAddressCity($expediterAddressCity) {
        $this->expediterAddressCity = $expediterAddressCity;
    }

    public function getExpediterAddressState() {
        return $this->expediterAddressState;
    }

    public function setExpediterAddressState($expediterAddressState) {
        $this->expediterAddressState = $expediterAddressState;
    }

    public function getExpediterAddressCountry() {
        return $this->expediterAddressCountry;
    }

    public function setExpediterAddressCountry($expediterAddressCountry) {
        $this->expediterAddressCountry = $expediterAddressCountry;
    }

    public function getExpediterAddressZipcode() {
        return $this->expediterAddressZipcode;
    }

    public function setExpediterAddressZipcode($expediterAddressZipcode) {
        $this->expediterAddressZipcode = $expediterAddressZipcode;
    }

    public function getCustomerFiscalCode() {
        return $this->customerFiscalCode;
    }

    public function setCustomerFiscalCode($customerFiscalCode) {
        $this->customerFiscalCode = $customerFiscalCode;
    }

    public function getCustomerName() {
        return $this->customerName;
    }

    public function setCustomerName($customerName) {
        $this->customerName = $customerName;
    }

    public function getCustomerFAddressStreet() {
        return $this->customerFAddressStreet;
    }

    public function setCustomerFAddressStreet($customerFAddressStreet) {
        $this->customerFAddressStreet = $customerFAddressStreet;
    }

    public function getCustomerFAddressNum() {
        return $this->customerFAddressNum;
    }

    public function setCustomerFAddressNum($customerFAddressNum) {
        $this->customerFAddressNum = $customerFAddressNum;
    }

    public function getCustomerFAddressNum2() {
        return $this->customerFAddressNum2;
    }

    public function setCustomerFAddressNum2($customerFAddressNum2) {
        $this->customerFAddressNum2 = $customerFAddressNum2;
    }

    public function getCustomerFAddressUrbanization() {
        return $this->customerFAddressUrbanization;
    }

    public function setCustomerFAddressUrbanization($customerFAddressUrbanization) {
        $this->customerFAddressUrbanization = $customerFAddressUrbanization;
    }

    public function getCustomerFAddressDistrict() {
        return $this->customerFAddressDistrict;
    }

    public function setCustomerFAddressDistrict($customerFAddressDistrict) {
        $this->customerFAddressDistrict = $customerFAddressDistrict;
    }

    public function getCustomerFAddressCity() {
        return $this->customerFAddressCity;
    }

    public function setCustomerFAddressCity($customerFAddressCity) {
        $this->customerFAddressCity = $customerFAddressCity;
    }

    public function getCustomerFAddressState() {
        return $this->customerFAddressState;
    }

    public function setCustomerFAddressState($customerFAddressState) {
        $this->customerFAddressState = $customerFAddressState;
    }

    public function getCustomerFAddressCountry() {
        return $this->customerFAddressCountry;
    }

    public function setCustomerFAddressCountry($customerFAddressCountry) {
        $this->customerFAddressCountry = $customerFAddressCountry;
    }

    public function getCustomerFAddressZipcode() {
        return $this->customerFAddressZipcode;
    }

    public function setCustomerFAddressZipcode($customerFAddressZipcode) {
        $this->customerFAddressZipcode = $customerFAddressZipcode;
    }

    public function getCustomerShpAddressStreet() {
        return $this->customerShpAddressStreet;
    }

    public function setCustomerShpAddressStreet($customerShpAddressStreet) {
        $this->customerShpAddressStreet = $customerShpAddressStreet;
    }

    public function getCustomerShpAddressNum() {
        return $this->customerShpAddressNum;
    }

    public function setCustomerShpAddressNum($customerShpAddressNum) {
        $this->customerShpAddressNum = $customerShpAddressNum;
    }

    public function getCustomerShpAddressNum2() {
        return $this->customerShpAddressNum2;
    }

    public function setCustomerShpAddressNum2($customerShpAddressNum2) {
        $this->customerShpAddressNum2 = $customerShpAddressNum2;
    }

    public function getCustomerShpAddressUrbanization() {
        return $this->customerShpAddressUrbanization;
    }

    public function setCustomerShpAddressUrbanization($customerShpAddressUrbanization) {
        $this->customerShpAddressUrbanization = $customerShpAddressUrbanization;
    }

    public function getCustomerShpAddressDistrict() {
        return $this->customerShpAddressDistrict;
    }

    public function setCustomerShpAddressDistrict($customerShpAddressDistrict) {
        $this->customerShpAddressDistrict = $customerShpAddressDistrict;
    }

    public function getCustomerShpAddressCity() {
        return $this->customerShpAddressCity;
    }

    public function setCustomerShpAddressCity($customerShpAddressCity) {
        $this->customerShpAddressCity = $customerShpAddressCity;
    }

    public function getCustomerShpAddressState() {
        return $this->customerShpAddressState;
    }

    public function setCustomerShpAddressState($customerShpAddressState) {
        $this->customerShpAddressState = $customerShpAddressState;
    }

    public function getCustomerShpAddressCountry() {
        return $this->customerShpAddressCountry;
    }

    public function setCustomerShpAddressCountry($customerShpAddressCountry) {
        $this->customerShpAddressCountry = $customerShpAddressCountry;
    }

    public function getCustomerShpAddressZipcode() {
        return $this->customerShpAddressZipcode;
    }

    public function setCustomerShpAddressZipcode($customerShpAddressZipcode) {
        $this->customerShpAddressZipcode = $customerShpAddressZipcode;
    }
        
    public function getXmlCFD() {
        return $this->xmlCFD;
    }

    public function setXmlCFD($xmlCFD) {
        $this->xmlCFD = $xmlCFD;
    }

    public function getXmlCFDI() {
        return $this->xmlCFDI;
    }

    public function setXmlCFDI($xmlCFDI) {
        $this->xmlCFDI = $xmlCFDI;
    }

    public function getXmlAddenda() {
        return $this->xmlAddenda;
    }

    public function setXmlAddenda($xmlAddenda) {
        $this->xmlAddenda = $xmlAddenda;
    }

    public function getUuid() {
        return $this->uuid;
    }

    public function setUuid($uuid) {
        $this->uuid = $uuid;
    }

    public function getOriginalString() {
        return $this->originalString;
    }

    public function setOriginalString($originalString) {
        $this->originalString = $originalString;
    }

    public function getRelatedID_invoice() {
        return $this->relatedID_invoice;
    }

    public function setRelatedID_invoice($relatedID_invoice) {
        $this->relatedID_invoice = $relatedID_invoice;
    }

    public function getID_orders_alias() {
        return $this->iD_orders_alias;
    }

    public function setID_orders_alias($iD_orders_alias) {
        $this->iD_orders_alias = $iD_orders_alias;
    }

    public function getID_orders_alias_date() {
        return $this->iD_orders_alias_date;
    }

    public function setID_orders_alias_date($iD_orders_alias_date) {
        $this->iD_orders_alias_date = $iD_orders_alias_date;
    }

    public function getExchangeReceipt() {
        return $this->exchangeReceipt;
    }

    public function setExchangeReceipt($exchangeReceipt) {
        $this->exchangeReceipt = $exchangeReceipt;
    }

    public function getExchangeReceiptDate() {
        return $this->exchangeReceiptDate;
    }

    public function setExchangeReceiptDate($exchangeReceiptDate) {
        $this->exchangeReceiptDate = $exchangeReceiptDate;
    }

    public function getCreditDays() {
        return $this->creditDays;
    }

    public function setCreditDays($creditDays) {
        $this->creditDays = $creditDays;
    }

    public function getConditions() {
        return $this->conditions;
    }

    public function setConditions($conditions) {
        $this->conditions = $conditions;
    }

    public function getBatchNum() {
        return $this->batchNum;
    }

    public function setBatchNum($batchNum) {
        $this->batchNum = $batchNum;
    }
        
    public function getImr_code() {
        return $this->imr_code;
    }

    public function setImr_code($imr_code) {
        $this->imr_code = $imr_code;
    }
        
    public function getStatus() {
        return $this->status;
    }

    public function setStatus($status) {
        $this->status = $status;
    }

    public function getVendorID() {
        return $this->VendorID;
    }

    public function setVendorID($VendorID) {
        $this->VendorID = $VendorID;
    }

    public function getCustomerShpaddressContact() {
        return $this->CustomerShpaddressContact;
    }

    public function setCustomerShpaddressContact($CustomerShpaddressContact) {
        $this->CustomerShpaddressContact = $CustomerShpaddressContact;
    }

    public function getCustomerShpaddressCode() {
        return $this->CustomerShpaddressCode;
    }

    public function setCustomerShpaddressCode($CustomerShpaddressCode) {
        $this->CustomerShpaddressCode = $CustomerShpaddressCode;
    }
    
    public function getCustomerShpaddressAlias() {
        return $this->CustomerShpaddressAlias;
    }

    public function setCustomerShpaddressAlias($CustomerShpaddressAlias) {
        $this->CustomerShpaddressAlias = $CustomerShpaddressAlias;
    }

    public function getCustomerAddressGln() {
        return $this->CustomerAddressGln;
    }

    public function setCustomerAddressGln($CustomerAddressGln) {
        $this->CustomerAddressGln = $CustomerAddressGln;
    }

    public function getCustomerShpaddressGln() {
        return $this->CustomerShpaddressGln;
    }

    public function setCustomerShpaddressGln($CustomerShpaddressGln) {
        $this->CustomerShpaddressGln = $CustomerShpaddressGln;
    }

    public function getViewed() {
        return $this->viewed;
    }

    public function setViewed($viewed) {
        $this->viewed = $viewed;
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

    public function getExtraField() {
        return $this->extraField;
    }

    public function setExtraField($extraField) {
        $this->extraField = $extraField;
    }
#Datos de XML (@ivan.miranda)
    public function setXml_uuid($Value){
        $this->xml_uuid = $Value;
    }
    public function getXml_uuid(){
        return $this->xml_uuid;
    }

    public function setXml_fecha_emision($Value){
        $this->xml_fecha_emision = $Value;
    }
    public function getXml_fecha_emision(){
        return $this->xml_fecha_emision;
    }

    public function setXml_fecha_certificacion($Value){
        $this->xml_fecha_certificacion = $Value;
    }
    public function getXml_fecha_certificacion(){
        return $this->xml_fecha_certificacion;
    }

}

?>
