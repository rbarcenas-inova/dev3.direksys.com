<?php

require_once 'BaseDTO.php';

/**
 * Description
 *
 * @author L.C.I Cesar Cedillo
 */
class ReturnsDTO extends BaseDTO {

            private $iD_returns;
            private $iD_orders_products;
            private $iD_customers;            
            private $iD_orders;
            private $amount;
            private $type;
            private $generalpckgcondition;
            private $itemsqty;
            private $receptionnotes;
            private $prodCondition;
            private $serialNumber;
            private $prodnotes;
            private $merAction;
            private $workdone;
            private $iD_products_exchange;
            private $actnotes;
            private $qcReturnFees;
            private $qcRestockFees;
            private $QcProcessed;
            private $aTCReturnFees;
            private $aTCRestockFees;
            private $aTCProcessed;
            private $oldShpReturn;
            private $newShp;
            private $authBy;
            private $packingListStatus;
            private $status;
            private $date;
            private $time;
            private $iD_admin_users;

    function __construct() {
        parent::__construct();

        $this->table_source = 'sl_returns';
        $this->field_list = array(
            'ID_returns',
            'ID_orders_products',
            'ID_customers',
            'ID_orders',
            'Amount',
            'Type',
            'generalpckgcondition',
            'itemsqty',
            'receptionnotes',
            'ProdCondition',
            'serial_number',
            'prodnotes',
            'merAction',
            'workdone',
            'ID_products_exchange',
            'actnotes',
            'QcReturnFees',
            'QcRestockFees',
            'QcProcessed',
            'ATCReturnFees',
            'ATCRestockFees',
            'ATCProcessed',
            'OldShpReturn',
            'NewShp',
            'AuthBy',
            'PackingListStatus',
            'Status',
            'Date',
            'Time',
            'ID_admin_users'
        );
        
        $this->generalpckgcondition = "New/Undeliverable";
        $this->workdone = "";
        //$this->qcReturnFees = "To Be Determined by ATC";
        //$this->qcRestockFees = "To Be Determined by ATC";
        //$this->QcProcessed = "no";
        $this->aTCReturnFees = "Not Applicable";
        $this->aTCRestockFees = "Not Applicable";
        //$this->aTCProcessed  = "no";
        //$this->oldShpReturn = "Applicable";
        //$this->newShp = "Applicable";
        //$this->packingListStatus = "Not Applicable";
        $this->status = "In Process";
        
    }

    public function getID_returns() {
        return $this->iD_returns;
    }

    public function setID_returns($iD_returns) {
        $this->iD_returns = $iD_returns;
    }

    public function getID_orders_products() {
        return $this->iD_orders_products;
    }

    public function setID_orders_products($iD_orders_products) {
        $this->iD_orders_products = $iD_orders_products;
    }

    public function getID_customers() {
        return $this->iD_customers;
    }

    public function setID_customers($iD_customers) {
        $this->iD_customers = $iD_customers;
    }

    public function getID_orders() {
        return $this->iD_orders;
    }

    public function setID_orders($iD_orders) {
        $this->iD_orders = $iD_orders;
    }

    public function getAmount() {
        return $this->amount;
    }

    public function setAmount($amount) {
        $this->amount = $amount;
    }

    public function getType() {
        return $this->type;
    }

    public function setType($type) {
        $this->type = $type;
    }

    public function getGeneralpckgcondition() {
        return $this->generalpckgcondition;
    }

    public function setGeneralpckgcondition($generalpckgcondition) {
        $this->generalpckgcondition = $generalpckgcondition;
    }

    public function getItemsqty() {
        return $this->itemsqty;
    }

    public function setItemsqty($itemsqty) {
        $this->itemsqty = $itemsqty;
    }

    public function getReceptionnotes() {
        return $this->receptionnotes;
    }

    public function setReceptionnotes($receptionnotes) {
        $this->receptionnotes = $receptionnotes;
    }

    public function getProdCondition() {
        return $this->prodCondition;
    }

    public function setProdCondition($prodCondition) {
        $this->prodCondition = $prodCondition;
    }

    public function getSerialNumber() {
        return $this->serialNumber;
    }

    public function setSerialNumber($serialNumber) {
        $this->serialNumber = $serialNumber;
    }

    public function getProdnotes() {
        return $this->prodnotes;
    }

    public function setProdnotes($prodnotes) {
        $this->prodnotes = $prodnotes;
    }

    public function getMerAction() {
        return $this->merAction;
    }

    public function setMerAction($merAction) {
        $this->merAction = $merAction;
    }

    public function getWorkdone() {
        return $this->workdone;
    }

    public function setWorkdone($workdone) {
        $this->workdone = $workdone;
    }

    public function getID_products_exchange() {
        return $this->iD_products_exchange;
    }

    public function setID_products_exchange($iD_products_exchange) {
        $this->iD_products_exchange = $iD_products_exchange;
    }

    public function getActnotes() {
        return $this->actnotes;
    }

    public function setActnotes($actnotes) {
        $this->actnotes = $actnotes;
    }

    public function getQcReturnFees() {
        return $this->qcReturnFees;
    }

    public function setQcReturnFees($qcReturnFees) {
        $this->qcReturnFees = $qcReturnFees;
    }

    public function getQcRestockFees() {
        return $this->qcRestockFees;
    }

    public function setQcRestockFees($qcRestockFees) {
        $this->qcRestockFees = $qcRestockFees;
    }

    public function getQcProcessed() {
        return $this->QcProcessed;
    }

    public function setQcProcessed($QcProcessed) {
        $this->QcProcessed = $QcProcessed;
    }

    public function getATCReturnFees() {
        return $this->aTCReturnFees;
    }

    public function setATCReturnFees($aTCReturnFees) {
        $this->aTCReturnFees = $aTCReturnFees;
    }

    public function getATCRestockFees() {
        return $this->aTCRestockFees;
    }

    public function setATCRestockFees($aTCRestockFees) {
        $this->aTCRestockFees = $aTCRestockFees;
    }

    public function getATCProcessed() {
        return $this->aTCProcessed;
    }

    public function setATCProcessed($aTCProcessed) {
        $this->aTCProcessed = $aTCProcessed;
    }

    public function getOldShpReturn() {
        return $this->oldShpReturn;
    }

    public function setOldShpReturn($oldShpReturn) {
        $this->oldShpReturn = $oldShpReturn;
    }

    public function getNewShp() {
        return $this->newShp;
    }

    public function setNewShp($newShp) {
        $this->newShp = $newShp;
    }

    public function getAuthBy() {
        return $this->authBy;
    }

    public function setAuthBy($authBy) {
        $this->authBy = $authBy;
    }

    public function getPackingListStatus() {
        return $this->packingListStatus;
    }

    public function setPackingListStatus($packingListStatus) {
        $this->packingListStatus = $packingListStatus;
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