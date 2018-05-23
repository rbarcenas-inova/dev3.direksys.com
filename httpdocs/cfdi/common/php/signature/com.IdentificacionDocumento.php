<?php

/**
 * Description of com
 *
 * @author ccedillo
 */
class IdentificacionDocumento {
    private $NumeroInterno;
    private $NroAprob;
    private $AnoAprob;
    private $Tipo;
    private $Serie;
    private $Folio;
    private $Estado;
    private $FechaEmis;
    private $FormaPago;
    private $MedioPago;
    private $CondPago;
    private $TermPagoCdg;
    private $TermPagoDias;
    private $FechaVenc;
    
    function __construct() {
        $this->NumeroInterno = "";
        $this->NroAprob = "";
        $this->AnoAprob = "";
        $this->Tipo = "";
        $this->Serie = "";
        $this->Folio = "";
        $this->Estado = "";
        $this->FechaEmis = "";
        $this->FormaPago = "";
        $this->MedioPago = "";
        $this->CondPago = "";
        $this->TermPagoCdg = "";
        $this->TermPagoDias = "";
        $this->FechaVenc = "";
        
    }
    
    
    public function getNumeroInterno() {
        return $this->NumeroInterno;
    }

    public function setNumeroInterno($NumeroInterno) {
        $this->NumeroInterno = $NumeroInterno;
    }

    public function getNroAprob() {
        return $this->NroAprob;
    }

    public function setNroAprob($NroAprob) {
        $this->NroAprob = $NroAprob;
    }

    public function getAnoAprob() {
        return $this->AnoAprob;
    }

    public function setAnoAprob($AnoAprob) {
        $this->AnoAprob = $AnoAprob;
    }

    public function getTipo() {
        return $this->Tipo;
    }

    public function setTipo($Tipo) {
        $this->Tipo = $Tipo;
    }

    public function getSerie() {
        return $this->Serie;
    }

    public function setSerie($Serie) {
        $this->Serie = $Serie;
    }

    public function getFolio() {
        return $this->Folio;
    }

    public function setFolio($Folio) {
        $this->Folio = $Folio;
    }

    public function getEstado() {
        return $this->Estado;
    }

    public function setEstado($Estado) {
        $this->Estado = $Estado;
    }

    public function getFechaEmis() {
        return $this->FechaEmis;
    }

    public function setFechaEmis($FechaEmis) {
        $this->FechaEmis = $FechaEmis;
    }

    public function getFormaPago() {
        return $this->FormaPago;
    }

    public function setFormaPago($FormaPago) {
        $this->FormaPago = $FormaPago;
    }

    public function getMedioPago() {
        return $this->MedioPago;
    }

    public function setMedioPago($MedioPago) {
        $this->MedioPago = $MedioPago;
    }

    public function getCondPago() {
        return $this->CondPago;
    }

    public function setCondPago($CondPago) {
        $this->CondPago = $CondPago;
    }

    public function getTermPagoCdg() {
        return $this->TermPagoCdg;
    }

    public function setTermPagoCdg($TermPagoCdg) {
        $this->TermPagoCdg = $TermPagoCdg;
    }

    public function getTermPagoDias() {
        return $this->TermPagoDias;
    }

    public function setTermPagoDias($TermPagoDias) {
        $this->TermPagoDias = $TermPagoDias;
    }

    public function getFechaVenc() {
        return $this->FechaVenc;
    }

    public function setFechaVenc($FechaVenc) {
        $this->FechaVenc = $FechaVenc;
    }

}

?>
