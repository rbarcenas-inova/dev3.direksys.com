<?php

require_once 'BaseDAO.php';
require_once 'InterfaceDAO.php';
require_once 'dto.catalog.InvoicesDTO.php';

/**
 * Description of dao
 *
 * @author ccedillo
 * @author Oscar Maldonado
 * @author ivan.miranda
 */
class InvoicesDAO extends BaseDAO implements InterfaceDAO {

    function __construct() {
        parent::__construct();
        $this->resultSet = NULL;
        $this->numRows = -1;
        $this->operationSuccess = FALSE;
        $this->pagerPage = -1;
        $this->pagerLimit = -1;
    }

    public function deleteRecord(&$objectDTO) {
        
    }

    public function insertRecord(&$objectDTO) {
        
    }

    public function selectRecords(&$objectDTO) {
        $array_result = array();
        if ($objectDTO instanceof InvoicesDTO) {
            if ($this->connectDB()) {
                $cadena_sql = "SELECT * FROM " . $objectDTO->getTableSource() . " WHERE  1 ";

                if (!is_null($objectDTO->getID_invoices()) && $objectDTO->getID_invoices() > 0) {
                    $cadena_sql .="AND ID_invoices = " . $this->cleanSqlValue($objectDTO->getID_invoices());
                }

                /*
                if (!is_null($objectDTO->getID_orders()) && $objectDTO->getID_orders() > 0) {
                    $cadena_sql .="AND ID_orders = " . $this->cleanSqlValue($objectDTO->getID_orders());
                }
                 * 
                 */

                if (!is_null($objectDTO->getID_customers()) && $objectDTO->getID_customers() > 0) {
                    $cadena_sql .="AND ID_customers = " . $this->cleanSqlValue($objectDTO->getID_customers());
                }

                if (!is_null($objectDTO->getCustomerName()) && $objectDTO->getCustomerName() != "") {
                    $cadena_sql .="AND customer_fname LIKE '%" . $this->cleanSqlValue($objectDTO->getCustomerName(), false) . "%'";
                }

                if (!is_null($objectDTO->getCustomerFiscalCode()) && $objectDTO->getCustomerFiscalCode() != "") {
                    $cadena_sql .="AND customer_fcode LIKE '" . $this->cleanSqlValue($objectDTO->getCustomerFiscalCode(), false) . "%'";
                }
                
                if (!is_null($objectDTO->getDocSerial()) && $objectDTO->getDocSerial() != "") {
                    $cadena_sql .="AND doc_serial LIKE '" . $this->cleanSqlValue($objectDTO->getDocSerial(), false) . "%'";
                }

                if (!is_null($objectDTO->getDocNum()) && $objectDTO->getDocNum() != "") {
                    $cadena_sql .="AND doc_num = " . $this->cleanSqlValue($objectDTO->getDocNum());
                }

                if((is_null($objectDTO->getDocDate()) && !is_null($objectDTO->getExtraField())) || ($objectDTO->getDocDate() == "" && $objectDTO->getExtraField() != "")) {
                    $cadena_sql .="AND doc_date<= " . $this->cleanSqlValue($objectDTO->getExtraField());
                }
                elseif ((!is_null($objectDTO->getDocDate()) && !is_null($objectDTO->getExtraField())) && ($objectDTO->getDocDate() != "" && $objectDTO->getExtraField() != "")) {
                    $cadena_sql .="AND doc_date BETWEEN " . $this->cleanSqlValue($objectDTO->getDocDate()) . " AND " . $this->cleanSqlValue($objectDTO->getExtraField());
                }

                if (!is_null($objectDTO->getInvoiceType()) && $objectDTO->getInvoiceType() != "") {
                    $cadena_sql .="AND invoice_type = " . $this->cleanSqlValue($objectDTO->getInvoiceType());
                }

                if (!is_null($objectDTO->getStatus()) && $objectDTO->getStatus() != "") {
                    $cadena_sql .="AND Status = " . $this->cleanSqlValue($objectDTO->getStatus());
                }

                if (!is_null($objectDTO->getUuid()) && $objectDTO->getUuid() != "") {
                    $cadena_sql .="AND uuid = " . $this->cleanSqlValue($objectDTO->getInvoiceType());
                }

                if (!is_null($objectDTO->getViewed()) && $objectDTO->getViewed() != "") {
                    $cadena_sql .="AND viewed = " . $this->cleanSqlValue($objectDTO->getViewed());
                }

                if ($this->orderBy == "ID_invoices_asc") {
                    $cadena_sql .= " ORDER BY ID_invoices ASC";
                } elseif ($this->orderBy == "ID_invoices_desc") {
                    $cadena_sql .= " ORDER BY ID_invoices DESC";
                } elseif ($this->orderBy == "docdate_asc") {
                    $cadena_sql .= " ORDER BY ID_invoices ASC";
                } elseif ($this->orderBy == "docdate_desc") {
                    $cadena_sql .= " ORDER BY ID_invoices DESC";
                } else if (trim($this->orderBy) != "") {
                    $cadena_sql .= " ORDER BY " . $this->cleanSqlValue($this->orderBy) . ";";
                }

                if ($this->pagerPage > -1 && $this->pagerLimit > -1) {
                    $cadena_sql .= " LIMIT " . $this->pagerPage . "," . $this->pagerLimit;
                }

                $this->selectSQLcommand($cadena_sql);

                if ($this->onlyCountRows) {
                    $this->onlyCountRows = FALSE;
                    $this->disconnectDB();
                    return;
                }

                if ($this->numRows > 0) {
                    while ($fila = $this->fetchAssocNextRow()) {
                        $invoicesDTO = new InvoicesDTO();

                        $invoicesDTO->setID_invoices($fila['ID_invoices']);
                        //$invoicesDTO->setID_orders($fila['ID_orders']);
                        $invoicesDTO->setID_customers($fila['ID_customers']);
                        $invoicesDTO->setDocSerial($fila['doc_serial']);
                        $invoicesDTO->setDocNum($fila['doc_num']);
                        $invoicesDTO->setDocDate($fila['doc_date']);
                        $invoicesDTO->setPaymentType($fila['payment_type']);
                        $invoicesDTO->setPaymentMethod($fila['payment_method']);
                        $invoicesDTO->setPaymentDigits($fila['payment_digits']);
                        $invoicesDTO->setInvoiceNet($fila['invoice_net']);
                        $invoicesDTO->setInvoiceTotal($fila['invoice_total']);
                        $invoicesDTO->setDiscount($fila['discount']);
                        $invoicesDTO->setTotalTaxesDetained($fila['total_taxes_detained']);
                        $invoicesDTO->setTotalTaxesTransfered($fila['total_taxes_transfered']);
                        $invoicesDTO->setCurrency($fila['currency']);
                        $invoicesDTO->setCurrencyExchange($fila['currency_exchange']);
                        $invoicesDTO->setInvoiceType($fila['invoice_type']);
                        $invoicesDTO->setPlaceConsignment($fila['place_consignment']);
                        $invoicesDTO->setExpediterFiscalCode($fila['expediter_fcode']);
                        $invoicesDTO->setExpediterName($fila['expediter_fname']);
                        $invoicesDTO->setExpediterRegimen($fila['expediter_fregimen']);
                        $invoicesDTO->setExpediterFAddressStreet($fila['expediter_faddress_street']);
                        $invoicesDTO->setExpediterFAddressNum($fila['expediter_faddress_num']);
                        $invoicesDTO->setExpediterFAddressNum2($fila['expediter_faddress_num2']);
                        $invoicesDTO->setExpediterFAddressUrbanization($fila['expediter_faddress_urbanization']);
                        $invoicesDTO->setExpediterFAddressDistrict($fila['expediter_faddress_district']);
                        $invoicesDTO->setExpediterFAddressCity($fila['expediter_faddress_city']);
                        $invoicesDTO->setExpediterFAddressState($fila['expediter_faddress_state']);
                        $invoicesDTO->setExpediterFAddressCountry($fila['expediter_faddress_country']);
                        $invoicesDTO->setExpediterFAddressZipcode($fila['expediter_faddress_zipcode']);

                        $invoicesDTO->setExpediterAddressStreet($fila['expediter_address_street']);
                        $invoicesDTO->setExpediterAddressNum($fila['expediter_address_num']);
                        $invoicesDTO->setExpediterAddressNum2($fila['expediter_address_num2']);
                        $invoicesDTO->setExpediterAddressUrbanization($fila['expediter_address_urbanization']);
                        $invoicesDTO->setExpediterAddressDistrict($fila['expediter_address_district']);
                        $invoicesDTO->setExpediterAddressCity($fila['expediter_address_city']);
                        $invoicesDTO->setExpediterAddressState($fila['expediter_address_state']);
                        $invoicesDTO->setExpediterAddressCountry($fila['expediter_address_country']);
                        $invoicesDTO->setExpediterAddressZipcode($fila['expediter_address_zipcode']);

                        $invoicesDTO->setCustomerFiscalCode($fila['customer_fcode']);
                        $invoicesDTO->setCustomerName($fila['customer_fname']);
                        $invoicesDTO->setCustomerFAddressStreet($fila['customer_address_street']);
                        $invoicesDTO->setCustomerFAddressNum($fila['customer_address_num']);
                        $invoicesDTO->setCustomerFAddressNum2($fila['customer_address_num2']);
                        $invoicesDTO->setCustomerFAddressUrbanization($fila['customer_address_urbanization']);
                        $invoicesDTO->setCustomerFAddressDistrict($fila['customer_address_district']);
                        $invoicesDTO->setCustomerFAddressCity($fila['customer_address_city']);
                        $invoicesDTO->setCustomerFAddressState($fila['customer_address_state']);
                        $invoicesDTO->setCustomerFAddressCountry($fila['customer_address_country']);
                        $invoicesDTO->setCustomerFAddressZipcode($fila['customer_address_zipcode']);
                        
                        $invoicesDTO->setCustomerShpAddressStreet($fila['customer_shpaddress_street']);
                        $invoicesDTO->setCustomerShpAddressNum($fila['customer_shpaddress_num']);
                        $invoicesDTO->setCustomerShpAddressNum2($fila['customer_shpaddress_num2']);
                        $invoicesDTO->setCustomerShpAddressUrbanization($fila['customer_shpaddress_urbanization']);
                        $invoicesDTO->setCustomerShpAddressDistrict($fila['customer_shpaddress_district']);
                        $invoicesDTO->setCustomerShpAddressCity($fila['customer_shpaddress_city']);
                        $invoicesDTO->setCustomerShpAddressState($fila['customer_shpaddress_state']);
                        $invoicesDTO->setCustomerShpAddressCountry($fila['customer_shpaddress_country']);
                        $invoicesDTO->setCustomerShpAddressZipcode($fila['customer_shpaddress_zipcode']);
                        
                        $invoicesDTO->setXmlCFD($fila['xml_cfd']);
                        $invoicesDTO->setXmlCFDI($fila['xml_cfdi']);
                        $invoicesDTO->setXmlAddenda($fila['xml_addenda']);
                        $invoicesDTO->setUuid($fila['uuid']);
                        $invoicesDTO->setOriginalString($fila['original_string']);
                        $invoicesDTO->setRelatedID_invoice($fila['related_ID_invoices']);
                        
                        $invoicesDTO->setID_orders_alias($fila['ID_orders_alias']);
                        $invoicesDTO->setID_orders_alias_date($fila['ID_orders_alias_date']);
                        $invoicesDTO->setExchangeReceipt($fila['exchange_receipt']);
                        $invoicesDTO->setExchangeReceiptDate($fila['exchange_receipt_date']);
                        $invoicesDTO->setCreditDays($fila['credit_days']);
                        $invoicesDTO->setConditions($fila['conditions']);
                        $invoicesDTO->setBatchNum($fila['batch_num']);
                        $invoicesDTO->setImr_code($fila['imr_code']);
                        
                        $invoicesDTO->setStatus($fila['Status']);
                        $invoicesDTO->setVendorID($fila['VendorID']);
                        $invoicesDTO->setCustomerShpaddressContact($fila['customer_shpaddress_contact']);
                        $invoicesDTO->setCustomerShpaddressCode($fila['customer_shpaddress_code']);
                        $invoicesDTO->setCustomerShpaddressAlias($fila['customer_shpaddress_alias']);
                        $invoicesDTO->setCustomerAddressGln($fila['customer_address_gln']);
                        $invoicesDTO->setCustomerShpaddressGln($fila['customer_shpaddress_gln']);
                        $invoicesDTO->setViewed($fila['viewed']);

                        $invoicesDTO->setDate($fila['Date']);
                        $invoicesDTO->setTime($fila['Time']);
                        $invoicesDTO->setID_admin_users($fila['ID_admin_users']);

                        $array_result[] = $invoicesDTO;
                    }
                }
            }
        }
        return $array_result;
    }

    public function selectAllRecords(&$objectDTO) {
        $array_result = array();
        $cadena = "";
        if ($objectDTO instanceof InvoicesDTO) {
            if ($this->connectDB()) {
                $cadena_sql = "SET SESSION group_concat_max_len = 1000000;";
                $this->selectSQLcommand($cadena_sql);
                $cadena_sql = "SELECT group_concat(concat(doc_serial,'_',doc_num) separator '|') lista FROM " . $objectDTO->getTableSource() . " WHERE  1 ";

                if (!is_null($objectDTO->getID_invoices()) && $objectDTO->getID_invoices() > 0) {
                    $cadena_sql .="AND ID_invoices = " . $this->cleanSqlValue($objectDTO->getID_invoices());
                }

                /*
                if (!is_null($objectDTO->getID_orders()) && $objectDTO->getID_orders() > 0) {
                    $cadena_sql .="AND ID_orders = " . $this->cleanSqlValue($objectDTO->getID_orders());
                }
                 * 
                 */

                if (!is_null($objectDTO->getID_customers()) && $objectDTO->getID_customers() > 0) {
                    $cadena_sql .="AND ID_customers = " . $this->cleanSqlValue($objectDTO->getID_customers());
                }

                if (!is_null($objectDTO->getCustomerName()) && $objectDTO->getCustomerName() != "") {
                    $cadena_sql .="AND customer_fname LIKE '%" . $this->cleanSqlValue($objectDTO->getCustomerName(), false) . "%'";
                }

                if (!is_null($objectDTO->getCustomerFiscalCode()) && $objectDTO->getCustomerFiscalCode() != "") {
                    $cadena_sql .="AND customer_fcode LIKE '" . $this->cleanSqlValue($objectDTO->getCustomerFiscalCode(), false) . "%'";
                }
                
                if (!is_null($objectDTO->getDocSerial()) && $objectDTO->getDocSerial() != "") {
                    $cadena_sql .="AND doc_serial LIKE '" . $this->cleanSqlValue($objectDTO->getDocSerial(), false) . "%'";
                }

                if (!is_null($objectDTO->getDocNum()) && $objectDTO->getDocNum() != "") {
                    $cadena_sql .="AND doc_num = " . $this->cleanSqlValue($objectDTO->getDocNum());
                }

                if((is_null($objectDTO->getDocDate()) && !is_null($objectDTO->getExtraField())) || ($objectDTO->getDocDate() == "" && $objectDTO->getExtraField() != "")) {
                    $cadena_sql .="AND doc_date<= " . $this->cleanSqlValue($objectDTO->getExtraField());
                }
                elseif ((!is_null($objectDTO->getDocDate()) && !is_null($objectDTO->getExtraField())) && ($objectDTO->getDocDate() != "" && $objectDTO->getExtraField() != "")) {
                    $cadena_sql .="AND doc_date BETWEEN " . $this->cleanSqlValue($objectDTO->getDocDate()) . " AND " . $this->cleanSqlValue($objectDTO->getExtraField());
                }

                if (!is_null($objectDTO->getInvoiceType()) && $objectDTO->getInvoiceType() != "") {
                    $cadena_sql .="AND invoice_type = " . $this->cleanSqlValue($objectDTO->getInvoiceType());
                }

                if (!is_null($objectDTO->getStatus()) && $objectDTO->getStatus() != "") {
                    $cadena_sql .="AND Status = " . $this->cleanSqlValue($objectDTO->getStatus());
                }

                if (!is_null($objectDTO->getUuid()) && $objectDTO->getUuid() != "") {
                    $cadena_sql .="AND uuid = " . $this->cleanSqlValue($objectDTO->getInvoiceType());
                }

                if (!is_null($objectDTO->getViewed()) && $objectDTO->getViewed() != "") {
                    $cadena_sql .="AND viewed = " . $this->cleanSqlValue($objectDTO->getViewed());
                }

                if ($this->orderBy == "ID_invoices_asc") {
                    $cadena_sql .= " ORDER BY ID_invoices ASC";
                } elseif ($this->orderBy == "ID_invoices_desc") {
                    $cadena_sql .= " ORDER BY ID_invoices DESC";
                } elseif ($this->orderBy == "docdate_asc") {
                    $cadena_sql .= " ORDER BY ID_invoices ASC";
                } elseif ($this->orderBy == "docdate_desc") {
                    $cadena_sql .= " ORDER BY ID_invoices DESC";
                } else if (trim($this->orderBy) != "") {
                    $cadena_sql .= " ORDER BY " . $this->cleanSqlValue($this->orderBy) . ";";
                }
                #echo $cadena_sql;exit();
                $this->selectSQLcommand($cadena_sql);
                $fila = $this->fetchAssocNextRow();
                $cadena = $fila['lista'];
                $this->disconnectDB();
            }
        }
        return $cadena;
    }

    public function updateRecord(&$objectDTO) {
        $this->operationSuccess = FALSE;
        if ($objectDTO instanceof InvoicesDTO) {
            if ($this->connectDB()) {

                $needAnd = FALSE;

                $cadena_sql = "UPDATE " . $objectDTO->getTableSource() . " SET ";
                /*
                if (!is_null($objectDTO->getID_customers())) {
                    $cadena_sql .= "ID_customers" . $this->cleanSqlValue($objectDTO->getID_customers());
                    $needAnd = TRUE;
                }

                if (!is_null($objectDTO->getDocDate())) {
                    if ($needAnd) {
                        $cadena_sql .= ", ";
                    }                    
                    $cadena_sql .= "doc_date = " . $this->cleanSqlValue($objectDTO->getDocDate());
                    $needAnd = TRUE;
                }
                */
                if (!is_null($objectDTO->getDocSerial())) {
                    /*if ($needAnd) {
                        $cadena_sql .= ", ";
                    }*/
                    $cadena_sql .= "doc_serial = " . $this->cleanSqlValue($objectDTO->getDocSerial());
                    $needAnd = TRUE;
                }

                if (!is_null($objectDTO->getDocNum())) {
                    if ($needAnd) {
                        $cadena_sql .= ", ";
                    }                    
                    $cadena_sql .= "doc_num = " . $this->cleanSqlValue($objectDTO->getDocNum());
                    $needAnd = TRUE;
                }

                if (!is_null($objectDTO->getDocDate())) {
                    if ($needAnd) {
                        $cadena_sql .= ", ";
                    }                    
                    $cadena_sql .= "doc_date = " . $this->cleanSqlValue($objectDTO->getDocDate());
                    $needAnd = TRUE;
                }
                
                if (!is_null($objectDTO->getPaymentDigits())) {
                    if ($needAnd) {
                        $cadena_sql .= ", ";
                    }                    
                    $cadena_sql .= "payment_digits = " . $this->cleanSqlValue($objectDTO->getPaymentDigits());
                    $needAnd = TRUE;
                }

                if (!is_null($objectDTO->getInvoiceType())) {
                    if ($needAnd) {
                        $cadena_sql .= ", ";
                    }                    
                    $cadena_sql .= "invoice_type = " . $this->cleanSqlValue($objectDTO->getInvoiceType());
                    $needAnd = TRUE;
                }
                
                if (trim($objectDTO->getExpediterFiscalCode()) != '') {
                    if ($needAnd) {
                        $cadena_sql .= ", ";
                    }                    
                    $cadena_sql .= "expediter_fcode = " . $this->cleanSqlValue($objectDTO->getExpediterFiscalCode());
                    $needAnd = TRUE;
                }

                if (trim($objectDTO->getExpediterName()) != '') {
                    if ($needAnd) {
                        $cadena_sql .= ", ";
                    }

                    $cadena_sql .= "expediter_fname = " . $this->cleanSqlValue($objectDTO->getExpediterName());
                    $needAnd = TRUE;
                }

                if (trim($objectDTO->getExpediterRegimen()) != '') {
                    if ($needAnd) {
                        $cadena_sql .= ", ";
                    }

                    $cadena_sql .= "expediter_fregimen = " . $this->cleanSqlValue($objectDTO->getExpediterRegimen());
                    $needAnd = TRUE;
                }

                if (trim($objectDTO->getExpediterFAddressStreet()) != '') {
                    if ($needAnd) {
                        $cadena_sql .= ", ";
                    }

                    $cadena_sql .= "expediter_faddress_street = " . $this->cleanSqlValue($objectDTO->getExpediterFAddressStreet());
                    $needAnd = TRUE;
                }

                if (trim($objectDTO->getExpediterFAddressNum()) != '') {
                    if ($needAnd) {
                        $cadena_sql .= ", ";
                    }

                    $cadena_sql .= "expediter_faddress_num = " . $this->cleanSqlValue($objectDTO->getExpediterFAddressNum());
                    $needAnd = TRUE;
                }


                if (trim($objectDTO->getExpediterFAddressNum2()) != '') {
                    if ($needAnd) {
                        $cadena_sql .= ", ";
                    }

                    $cadena_sql .= "expediter_faddress_num2 = " . $this->cleanSqlValue($objectDTO->getExpediterFAddressNum2());
                    $needAnd = TRUE;
                }

                if (trim($objectDTO->getExpediterFAddressUrbanization()) != '') {
                    if ($needAnd) {
                        $cadena_sql .= ", ";
                    }

                    $cadena_sql .= "expediter_faddress_urbanization = " . $this->cleanSqlValue($objectDTO->getExpediterFAddressUrbanization());
                    $needAnd = TRUE;
                }

                if (trim($objectDTO->getExpediterFAddressDistrict()) != '') {
                    if ($needAnd) {
                        $cadena_sql .= ", ";
                    }

                    $cadena_sql .= "expediter_faddress_district = " . $this->cleanSqlValue($objectDTO->getExpediterFAddressDistrict());
                    $needAnd = TRUE;
                }

                if (trim($objectDTO->getExpediterFAddressCity()) != '') {
                    if ($needAnd) {
                        $cadena_sql .= ", ";
                    }

                    $cadena_sql .= "expediter_faddress_city = " . $this->cleanSqlValue($objectDTO->getExpediterFAddressCity());
                    $needAnd = TRUE;
                }

                if (trim($objectDTO->getExpediterFAddressState()) != '') {
                    if ($needAnd) {
                        $cadena_sql .= ", ";
                    }

                    $cadena_sql .= "expediter_faddress_state = " . $this->cleanSqlValue($objectDTO->getExpediterFAddressState());
                    $needAnd = TRUE;
                }

                if (trim($objectDTO->getExpediterFAddressCountry()) != '') {
                    if ($needAnd) {
                        $cadena_sql .= ", ";
                    }

                    $cadena_sql .= "expediter_faddress_country = " . $this->cleanSqlValue($objectDTO->getExpediterFAddressCountry());
                    $needAnd = TRUE;
                }


                if (trim($objectDTO->getExpediterFAddressZipcode()) != '') {
                    if ($needAnd) {
                        $cadena_sql .= ", ";
                    }

                    $cadena_sql .= "expediter_faddress_zipcode = " . $this->cleanSqlValue($objectDTO->getExpediterFAddressZipcode());
                    $needAnd = TRUE;
                }


                if (!is_null($objectDTO->getExpediterAddressStreet())) {
                    if ($needAnd) {
                        $cadena_sql .= ", ";
                    }

                    $cadena_sql .= "expediter_address_street = " . $this->cleanSqlValue($objectDTO->getExpediterAddressStreet());
                    $needAnd = TRUE;
                }

                if (!is_null($objectDTO->getExpediterAddressNum())) {
                    if ($needAnd) {
                        $cadena_sql .= ", ";
                    }

                    $cadena_sql .= "expediter_address_num = " . $this->cleanSqlValue($objectDTO->getExpediterAddressNum());
                    $needAnd = TRUE;
                }


                if (!is_null($objectDTO->getExpediterAddressNum2())) {
                    if ($needAnd) {
                        $cadena_sql .= ", ";
                    }

                    $cadena_sql .= "expediter_address_num2 = " . $this->cleanSqlValue($objectDTO->getExpediterAddressNum2());
                    $needAnd = TRUE;
                }

                if (!is_null($objectDTO->getExpediterAddressUrbanization())) {
                    if ($needAnd) {
                        $cadena_sql .= ", ";
                    }

                    $cadena_sql .= "expediter_address_urbanization = " . $this->cleanSqlValue($objectDTO->getExpediterAddressUrbanization());
                    $needAnd = TRUE;
                }

                if (!is_null($objectDTO->getExpediterAddressDistrict())) {
                    if ($needAnd) {
                        $cadena_sql .= ", ";
                    }

                    $cadena_sql .= "expediter_address_district = " . $this->cleanSqlValue($objectDTO->getExpediterAddressDistrict());
                    $needAnd = TRUE;
                }

                if (!is_null($objectDTO->getExpediterAddressCity())) {
                    if ($needAnd) {
                        $cadena_sql .= ", ";
                    }

                    $cadena_sql .= "expediter_address_city = " . $this->cleanSqlValue($objectDTO->getExpediterAddressCity());
                    $needAnd = TRUE;
                }

                if (!is_null($objectDTO->getExpediterAddressState())) {
                    if ($needAnd) {
                        $cadena_sql .= ", ";
                    }

                    $cadena_sql .= "expediter_address_state = " . $this->cleanSqlValue($objectDTO->getExpediterAddressState());
                    $needAnd = TRUE;
                }

                if (!is_null($objectDTO->getExpediterAddressCountry())) {
                    if ($needAnd) {
                        $cadena_sql .= ", ";
                    }

                    $cadena_sql .= "expediter_address_country = " . $this->cleanSqlValue($objectDTO->getExpediterAddressCountry());
                    $needAnd = TRUE;
                }


                if (!is_null($objectDTO->getExpediterAddressZipcode())) {
                    if ($needAnd) {
                        $cadena_sql .= ", ";
                    }

                    $cadena_sql .= "expediter_address_zipcode = " . $this->cleanSqlValue($objectDTO->getExpediterAddressZipcode());
                    $needAnd = TRUE;
                }

                if (trim($objectDTO->getCustomerFiscalCode()) != '') {
                    if ($needAnd) {
                        $cadena_sql .= ", ";
                    }

                    $cadena_sql .= "customer_fcode = " . $this->cleanSqlValue($objectDTO->getCustomerFiscalCode());
                    $needAnd = TRUE;
                }

                if (trim($objectDTO->getCustomerName()) != '') {
                    if ($needAnd) {
                        $cadena_sql .= ", ";
                    }

                    $cadena_sql .= "customer_fname = " . $this->cleanSqlValue($objectDTO->getCustomerName());
                    $needAnd = TRUE;
                }

                if (!is_null($objectDTO->getCustomerFAddressStreet())) {
                    if ($needAnd) {
                        $cadena_sql .= ", ";
                    }

                    $cadena_sql .= "customer_address_street = " . $this->cleanSqlValue($objectDTO->getCustomerFAddressStreet());
                    $needAnd = TRUE;
                }

                if (!is_null($objectDTO->getCustomerFAddressNum())) {
                    if ($needAnd) {
                        $cadena_sql .= ", ";
                    }

                    $cadena_sql .= "customer_address_num = " . $this->cleanSqlValue($objectDTO->getCustomerFAddressNum());
                    $needAnd = TRUE;
                }

                if (!is_null($objectDTO->getCustomerFAddressNum2())) {
                    if ($needAnd) {
                        $cadena_sql .= ", ";
                    }

                    $cadena_sql .= "customer_address_num2 = " . $this->cleanSqlValue($objectDTO->getCustomerFAddressNum2());
                    $needAnd = TRUE;
                }

                if (!is_null($objectDTO->getCustomerFAddressUrbanization())) {
                    if ($needAnd) {
                        $cadena_sql .= ", ";
                    }

                    $cadena_sql .= "customer_address_urbanization = " . $this->cleanSqlValue($objectDTO->getCustomerFAddressUrbanization());
                    $needAnd = TRUE;
                }

                if (!is_null($objectDTO->getCustomerFAddressDistrict())) {
                    if ($needAnd) {
                        $cadena_sql .= ", ";
                    }

                    $cadena_sql .= "customer_address_district = " . $this->cleanSqlValue($objectDTO->getCustomerFAddressDistrict());
                    $needAnd = TRUE;
                }

                if (!is_null($objectDTO->getCustomerFAddressCity())) {
                    if ($needAnd) {
                        $cadena_sql .= ", ";
                    }

                    $cadena_sql .= "customer_address_city = " . $this->cleanSqlValue($objectDTO->getCustomerFAddressCity());
                    $needAnd = TRUE;
                }

                if (!is_null($objectDTO->getCustomerFAddressState())) {
                    if ($needAnd) {
                        $cadena_sql .= ", ";
                    }

                    $cadena_sql .= "customer_address_state = " . $this->cleanSqlValue($objectDTO->getCustomerFAddressState());
                    $needAnd = TRUE;
                }

                if (!is_null($objectDTO->getCustomerFAddressCountry())) {
                    if ($needAnd) {
                        $cadena_sql .= ", ";
                    }

                    $cadena_sql .= "customer_address_country = " . $this->cleanSqlValue($objectDTO->getCustomerFAddressCountry());
                    $needAnd = TRUE;
                }

                if (!is_null($objectDTO->getCustomerFAddressZipcode())) {
                    if ($needAnd) {
                        $cadena_sql .= ", ";
                    }

                    $cadena_sql .= "customer_address_zipcode = " . $this->cleanSqlValue($objectDTO->getCustomerFAddressZipcode());
                    $needAnd = TRUE;
                }

                if (!is_null($objectDTO->getCustomerShpAddressStreet())) {
                    if ($needAnd) {
                        $cadena_sql .= ", ";
                    }

                    $cadena_sql .= "customer_shpaddress_street = " . $this->cleanSqlValue($objectDTO->getCustomerShpAddressStreet());
                    $needAnd = TRUE;
                }                

                if (!is_null($objectDTO->getCustomerShpAddressNum())) {
                    if ($needAnd) {
                        $cadena_sql .= ", ";
                    }

                    $cadena_sql .= "customer_shpaddress_num = " . $this->cleanSqlValue($objectDTO->getCustomerShpAddressNum());
                    $needAnd = TRUE;
                }                
                
                if (!is_null($objectDTO->getCustomerShpAddressNum2())) {
                    if ($needAnd) {
                        $cadena_sql .= ", ";
                    }

                    $cadena_sql .= "customer_shpaddress_num2 = " . $this->cleanSqlValue($objectDTO->getCustomerShpAddressNum2());
                    $needAnd = TRUE;
                } 

                if (!is_null($objectDTO->getCustomerShpAddressUrbanization())) {
                    if ($needAnd) {
                        $cadena_sql .= ", ";
                    }

                    $cadena_sql .= "customer_shpaddress_urbanization = " . $this->cleanSqlValue($objectDTO->getCustomerShpAddressUrbanization());
                    $needAnd = TRUE;
                }                 

                if (!is_null($objectDTO->getCustomerShpAddressDistrict())) {
                    if ($needAnd) {
                        $cadena_sql .= ", ";
                    }

                    $cadena_sql .= "customer_shpaddress_district = " . $this->cleanSqlValue($objectDTO->getCustomerShpAddressDistrict());
                    $needAnd = TRUE;
                }                

                if (!is_null($objectDTO->getCustomerShpAddressCity())) {
                    if ($needAnd) {
                        $cadena_sql .= ", ";
                    }

                    $cadena_sql .= "customer_shpaddress_city = " . $this->cleanSqlValue($objectDTO->getCustomerShpAddressCity());
                    $needAnd = TRUE;
                }                 

                if (!is_null($objectDTO->getCustomerShpAddressState())) {
                    if ($needAnd) {
                        $cadena_sql .= ", ";
                    }

                    $cadena_sql .= "customer_shpaddress_state = " . $this->cleanSqlValue($objectDTO->getCustomerShpAddressState());
                    $needAnd = TRUE;
                }                

                if (!is_null($objectDTO->getCustomerShpAddressCountry())) {
                    if ($needAnd) {
                        $cadena_sql .= ", ";
                    }

                    $cadena_sql .= "customer_shpaddress_country = " . $this->cleanSqlValue($objectDTO->getCustomerShpAddressCountry());
                    $needAnd = TRUE;
                }   

                if (!is_null($objectDTO->getCustomerShpAddressZipcode())) {
                    if ($needAnd) {
                        $cadena_sql .= ", ";
                    }

                    $cadena_sql .= "customer_shpaddress_zipcode = " . $this->cleanSqlValue($objectDTO->getCustomerShpAddressZipcode());
                    $needAnd = TRUE;
                }                 
                
                if (trim($objectDTO->getXmlCFD()) != '') {
                    if ($needAnd) {
                        $cadena_sql .= ", ";
                    }

                    $cadena_sql .= "xml_cfd = " . $this->cleanSqlValue($objectDTO->getXmlCFD());
                    $needAnd = TRUE;
                }

                if (trim($objectDTO->getXmlCFDI()) != '') {
                    if ($needAnd) {
                        $cadena_sql .= ", ";
                    }

                    $cadena_sql .= "xml_cfdi = " . $this->cleanSqlValue($objectDTO->getXmlCFDI());
                    $needAnd = TRUE;
                }

                if (trim($objectDTO->getXmlAddenda()) != '') {
                    if ($needAnd) {
                        $cadena_sql .= ", ";
                    }

                    $cadena_sql .= "xml_addenda = " . $this->cleanSqlValue($objectDTO->getXmlAddenda());
                    $needAnd = TRUE;
                }

                if (trim($objectDTO->getUuid()) != '') {
                    if ($needAnd) {
                        $cadena_sql .= ", ";
                    }

                    $cadena_sql .= "uuid = " . $this->cleanSqlValue($objectDTO->getUuid());
                    $needAnd = TRUE;
                }

                if (trim($objectDTO->getOriginalString()) != '') {
                    if ($needAnd) {
                        $cadena_sql .= ", ";
                    }

                    $cadena_sql .= "original_string = " . $this->cleanSqlValue($objectDTO->getOriginalString());
                    $needAnd = TRUE;
                }

                if (!is_null($objectDTO->getRelatedID_invoice()) && $objectDTO->getRelatedID_invoice() > 0) {
                    if ($needAnd) {
                        $cadena_sql .= ", ";
                    }

                    $cadena_sql .= "related_ID_invoices = " . $this->cleanSqlValue($objectDTO->getRelatedID_invoice());
                    $needAnd = TRUE;
                }

                if (!is_null($objectDTO->getID_orders_alias())) {
                    if ($needAnd) {
                        $cadena_sql .= ", ";
                    }

                    $cadena_sql .= "ID_orders_alias = " . $this->cleanSqlValue($objectDTO->getID_orders_alias());
                    $needAnd = TRUE;
                }

                if (!is_null($objectDTO->getID_orders_alias_date())) {
                    if ($needAnd) {
                        $cadena_sql .= ", ";
                    }

                    $cadena_sql .= "ID_orders_alias_date = " . $this->cleanSqlValue($objectDTO->getID_orders_alias_date());
                    $needAnd = TRUE;
                }

                if (!is_null($objectDTO->getExchangeReceipt())) {
                    if ($needAnd) {
                        $cadena_sql .= ", ";
                    }

                    $cadena_sql .= "exchange_receipt = " . $this->cleanSqlValue($objectDTO->getExchangeReceipt());
                    $needAnd = TRUE;
                }

                if (!is_null($objectDTO->getExchangeReceiptDate())) {
                    if ($needAnd) {
                        $cadena_sql .= ", ";
                    }

                    $cadena_sql .= "exchange_receipt_date = " . $this->cleanSqlValue($objectDTO->getExchangeReceiptDate());
                    $needAnd = TRUE;
                }

                if (!is_null($objectDTO->getCreditDays())) {
                    if ($needAnd) {
                        $cadena_sql .= ", ";
                    }

                    $cadena_sql .= "credit_days = " . $this->cleanSqlValue($objectDTO->getCreditDays());
                    $needAnd = TRUE;
                }                

                if (!is_null($objectDTO->getConditions())) {
                    if ($needAnd) {
                        $cadena_sql .= ", ";
                    }

                    $cadena_sql .= "conditions = " . $this->cleanSqlValue($objectDTO->getConditions());
                    $needAnd = TRUE;
                }                
                
                if (!is_null($objectDTO->getBatchNum())) {
                    if ($needAnd) {
                        $cadena_sql .= ", ";
                    }

                    $cadena_sql .= "batch_num = " . $this->cleanSqlValue($objectDTO->getBatchNum());
                    $needAnd = TRUE;
                }                 
                
                if (!is_null($objectDTO->getImr_code())) {
                    if ($needAnd) {
                        $cadena_sql .= ", ";
                    }

                    $cadena_sql .= "imr_code = " . $this->cleanSqlValue($objectDTO->getImr_code());
                    $needAnd = TRUE;
                }                
                
                if (!is_null($objectDTO->getViewed())) {
                    if ($needAnd) {
                        $cadena_sql .= ", ";
                    }

                    $cadena_sql .= "viewed = " . $this->cleanSqlValue($objectDTO->getViewed());
                    $needAnd = TRUE;
                } 

                if (!is_null($objectDTO->getVendorID())) {
                    if ($needAnd) {
                        $cadena_sql .= ", ";
                    }

                    $cadena_sql .= "VendorID = " . $this->cleanSqlValue($objectDTO->getVendorID());
                    $needAnd = TRUE;
                }              

                if (!is_null($objectDTO->getCustomerShpaddressContact())) {
                    if ($needAnd) {
                        $cadena_sql .= ", ";
                    }

                    $cadena_sql .= "customer_shpaddress_contact = " . $this->cleanSqlValue($objectDTO->getCustomerShpaddressContact());
                    $needAnd = TRUE;
                }

                if (!is_null($objectDTO->getCustomerShpaddressCode())) {
                    if ($needAnd) {
                        $cadena_sql .= ", ";
                    }

                    $cadena_sql .= "customer_shpaddress_code = " . $this->cleanSqlValue($objectDTO->getCustomerShpaddressCode());
                    $needAnd = TRUE;
                }

                if (!is_null($objectDTO->getCustomerShpaddressAlias())) {
                    if ($needAnd) {
                        $cadena_sql .= ", ";
                    }

                    $cadena_sql .= "customer_shpaddress_alias = " . $this->cleanSqlValue($objectDTO->getCustomerShpaddressAlias());
                    $needAnd = TRUE;
                }

                if (!is_null($objectDTO->getCustomerAddressGln())) {
                    if ($needAnd) {
                        $cadena_sql .= ", ";
                    }

                    $cadena_sql .= "customer_address_gln = " . $this->cleanSqlValue($objectDTO->getCustomerAddressGln());
                    $needAnd = TRUE;
                }

                if (!is_null($objectDTO->getCustomerShpaddressGln())) {
                    if ($needAnd) {
                        $cadena_sql .= ", ";
                    }

                    $cadena_sql .= "customer_shpaddress_gln = " . $this->cleanSqlValue($objectDTO->getCustomerShpaddressGln());
                    $needAnd = TRUE;
                }
                
                if (trim($objectDTO->getStatus()) != '') {
                    if ($needAnd) {
                        $cadena_sql .= ", ";
                    }

                    $cadena_sql .= "Status = " . $this->cleanSqlValue($objectDTO->getStatus());
                    $needAnd = TRUE;
                }
                if (trim($objectDTO->getDate()) != '') {
                    if ($needAnd) {
                        $cadena_sql .= ", ";
                    }

                    $cadena_sql .= "Date = " . $this->cleanSqlValue($objectDTO->getDate());
                    $needAnd = TRUE;
                }
                if (trim($objectDTO->getTime()) != '') {
                    if ($needAnd) {
                        $cadena_sql .= ", ";
                    }

                    $cadena_sql .= "Time = " . $this->cleanSqlValue($objectDTO->getTime());
                    $needAnd = TRUE;
                }
            #Datos de XML (@ivan.miranda)
                if (trim($objectDTO->getXml_uuid()) != '') {
                    if ($needAnd) {
                        $cadena_sql .= ", ";
                    }

                    $cadena_sql .= "xml_uuid = '" . $this->cleanSqlValue($objectDTO->getXML_uuid())."'";
                    $needAnd = TRUE;
                }
                if (trim($objectDTO->getXml_fecha_emision()) != '') {
                    if ($needAnd) {
                        $cadena_sql .= ", ";
                    }

                    $cadena_sql .= "xml_fecha_emision = " . $this->cleanSqlValue($objectDTO->getXml_fecha_emision());
                    $needAnd = TRUE;
                }
                if (trim($objectDTO->getXml_fecha_certificacion()) != '') {
                    if ($needAnd) {
                        $cadena_sql .= ", ";
                    }

                    $cadena_sql .= "xml_fecha_certificacion = " . $this->cleanSqlValue($objectDTO->getXml_fecha_certificacion());
                    $needAnd = TRUE;
                }
                /*
                if ($needAnd) {
                    $cadena_sql .= ", ";
                }
                */
                #$cadena_sql .= " Date = CURDATE(), Time = CURTIME(), ID_admin_users = " . $this->cleanSqlValue($objectDTO->getID_admin_users());
                $cadena_sql .= " WHERE ";
                if ($objectDTO->getID_invoices() > 0) {
                    $cadena_sql .= "ID_invoices = " . $this->cleanSqlValue($objectDTO->getID_invoices());
                }
                if ($this->executeSQLcommand($cadena_sql) >= 0) {
                    $this->operationSuccess = TRUE;
                }
            }
            $this->disconnectDB();
        }
        return $this->operationSuccess;
    }

    public function duplicateRecord(&$objectDTO) {
        $this->operationSuccess = FALSE;

        if ($objectDTO instanceof InvoicesDTO) {
            if ($this->connectDB()) {

                if (!is_null($objectDTO->getID_invoices()) && $objectDTO->getID_invoices() > 0) {

                    $cadena_sql = "INSERT INTO " . $objectDTO->getTableSource() . " (" . $objectDTO->getStringTableMetadata(TRUE) . ") 
                    SELECT " . $objectDTO->getStringTableMetadata(TRUE) . " FROM " . $objectDTO->getTableSource() . " WHERE ";

                    if (!is_null($objectDTO->getID_invoices()) && $objectDTO->getID_invoices() > 0) {
                        $cadena_sql .= "ID_invoices = " . $this->cleanSqlValue($objectDTO->getID_invoices());
                    }

                    if ($this->executeSQLcommand($cadena_sql) > 0) {
                        $this->operationSuccess = TRUE;
                        $this->lastInsertId = $this->getInsertId();
                    }
                }
            }
        }

        return $this->operationSuccess;
    }

    #@ivanmiranda
    public function movementsReInvocing($id_invoices) {
        $this->operationSuccess = FALSE;
        if ($this->connectDB()) {
            $this->selectSQLcommand("select doc_serial from cu_invoices where id_invoices=$id_invoices;");
            while ($fila = $this->fetchAssocNextRow()) {
                $doc_serial = $fila['doc_serial'];
            }
            if($doc_serial == 'TLOD' or $doc_serial == 'MOWF'){

                $this->selectSQLcommand("select distinct id_orders from cu_invoices_lines where id_invoices=$id_invoices;");
                while ($fila = $this->fetchAssocNextRow()) {
                    $id_orders = $fila['id_orders'];
                }
            #*************************************************************
            #   CON LA NOTA DE CREDITO CREADA SE DISPARA LA CONTABILIDAD
            #*************************************************************
                $Query = "insert into sl_movements (id_accounts,amount,Reference,effdate,tableused,ID_tableused,tablerelated,ID_tablerelated,category,Credebit,ID_segments,ID_journalentries,Status,Date,Time,ID_admin_users)
                    select id_accounts,amount,reference,curdate(),tableused,ID_tableused,tablerelated,ID_tablerelated,category,'Debit',id_segments,null,'Active',curdate(),curtime(),666
                    from sl_movements
                    where ID_tableused=$id_orders and id_accounts in (354,265,355,610) and Credebit='Credit'
                    union all
                    select 238,sum(amount),'',curdate(),tableused,ID_tableused,tablerelated,ID_tablerelated,category,'Credit',0,null,'Active',curdate(),curtime(),666
                    from sl_movements
                    where ID_tableused=$id_orders and id_accounts in (354,265,355,610) and Credebit='Credit'
                    union all
                    select id_accounts,amount,reference,curdate(),tableused,ID_tableused,tablerelated,ID_tablerelated,category,'Credit',id_segments,null,'Active',curdate(),curtime(),666
                    from sl_movements
                    where ID_tableused=$id_orders and id_accounts in (354,265,355,610) and Credebit='Credit'
                    union all
                    select 238,sum(amount),'',curdate(),tableused,ID_tableused,tablerelated,ID_tablerelated,category,'Debit',0,null,'Active',curdate(),curtime(),666
                    from sl_movements
                    where ID_tableused=$id_orders and id_accounts in (354,265,355,610) and Credebit='Credit';";
                if ($this->executeSQLcommand($Query) > 0) {
                    $this->operationSuccess = TRUE;
                    $this->lastInsertId = $this->getInsertId();
                }
            }
            
        }
        return $this->operationSuccess;
    }

}

?>
