<?php

/*
 * To change this template, choose Tools | Templates
 * and open the template in the editor.
 */

/**
 * Description of com
 *
 * @author ccedillo
 */
class TotalesDoc {
    private $TotalLotes;
    private $Moneda;
    private $FctConv;
    private $IndLista;
    private $TipoLista;
    private $SubTotal;
    private $MntDcto;
    private $PctDcto;
    private $MntRcgo;
    private $PctRcgo;
    private $MntBase;
    private $MntImp;
    private $MntRet;
    private $VlrPagar;
    private $VlrPalabras;
    
    function __construct() {
        $this->TotalLotes = "";
        $this->Moneda = "";
        $this->FctConv = "";
        $this->IndLista = "";
        $this->TipoLista = "";
        $this->SubTotal = "";
        $this->MntDcto = "";
        $this->PctDcto ="";
        $this->MntRcgo = "";
        $this->PctRcgo = "";
        $this->MntBase = "";
        $this->MntImp ="";
        $this->MntRet = "";
        $this->VlrPagar = "";
        $this->VlrPalabras = "";
    }
    
    public function getTotalLotes() {
        return $this->TotalLotes;
    }

    public function setTotalLotes($TotalLotes) {
        $this->TotalLotes = $TotalLotes;
    }

    public function getMoneda() {
        return $this->Moneda;
    }

    public function setMoneda($Moneda) {
        $this->Moneda = $Moneda;
    }

    public function getFctConv() {
        return $this->FctConv;
    }

    public function setFctConv($FctConv) {
        $this->FctConv = $FctConv;
    }

    public function getIndLista() {
        return $this->IndLista;
    }

    public function setIndLista($IndLista) {
        $this->IndLista = $IndLista;
    }

    public function getTipoLista() {
        return $this->TipoLista;
    }

    public function setTipoLista($TipoLista) {
        $this->TipoLista = $TipoLista;
    }

    public function getSubTotal() {
        return $this->SubTotal;
    }

    public function setSubTotal($SubTotal) {
        $this->SubTotal = $SubTotal;
    }

    public function getMntDcto() {
        return $this->MntDcto;
    }

    public function setMntDcto($MntDcto) {
        $this->MntDcto = $MntDcto;
    }

    public function getPctDcto() {
        return $this->PctDcto;
    }

    public function setPctDcto($PctDcto) {
        $this->PctDcto = $PctDcto;
    }

    public function getMntRcgo() {
        return $this->MntRcgo;
    }

    public function setMntRcgo($MntRcgo) {
        $this->MntRcgo = $MntRcgo;
    }

    public function getPctRcgo() {
        return $this->PctRcgo;
    }

    public function setPctRcgo($PctRcgo) {
        $this->PctRcgo = $PctRcgo;
    }

    public function getMntBase() {
        return $this->MntBase;
    }

    public function setMntBase($MntBase) {
        $this->MntBase = $MntBase;
    }

    public function getMntImp() {
        return $this->MntImp;
    }

    public function setMntImp($MntImp) {
        $this->MntImp = $MntImp;
    }

    public function getMntRet() {
        return $this->MntRet;
    }

    public function setMntRet($MntRet) {
        $this->MntRet = $MntRet;
    }

    public function getVlrPagar() {
        return $this->VlrPagar;
    }

    public function setVlrPagar($VlrPagar) {
        $this->VlrPagar = $VlrPagar;
    }

    public function getVlrPalabras() {
        return $this->VlrPalabras;
    }

    public function setVlrPalabras($VlrPalabras) {
        $this->VlrPalabras = $VlrPalabras;
    }


}

?>