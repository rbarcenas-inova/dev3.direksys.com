<?php

/**
 * Description of com
 *
 * @author ccedillo
 */
class Servicio {

    private $TipoSrv;
    private $Numero;
    private $NroExp;
    private $Mandante;
    private $Ejecutor;
    private $Frecuencia;
    private $Duracion;
    private $Origen;
    private $Destino;
    private $PeriodoDesde;
    private $PeriodoHasta;
    private $RazonServ;

    function __construct() {
        $this->TipoSrv = "";
        $this->Numero = "";
        $this->NroExp = "";
        $this->Mandante = "";
        $this->Ejecutor = "";
        $this->Frecuencia = "";
        $this->Duracion = "";
        $this->Origen = "";
        $this->Destino = "";
        $this->PeriodoDesde = "";
        $this->PeriodoHasta = "";
        $this->RazonServ = "";
    }

    public function getTipoSrv() {
        return $this->TipoSrv;
    }

    public function setTipoSrv($TipoSrv) {
        $this->TipoSrv = $TipoSrv;
    }

    public function getNumero() {
        return $this->Numero;
    }

    public function setNumero($Numero) {
        $this->Numero = $Numero;
    }

    public function getNroExp() {
        return $this->NroExp;
    }

    public function setNroExp($NroExp) {
        $this->NroExp = $NroExp;
    }

    public function getMandante() {
        return $this->Mandante;
    }

    public function setMandante($Mandante) {
        $this->Mandante = $Mandante;
    }

    public function getEjecutor() {
        return $this->Ejecutor;
    }

    public function setEjecutor($Ejecutor) {
        $this->Ejecutor = $Ejecutor;
    }

    public function getFrecuencia() {
        return $this->Frecuencia;
    }

    public function setFrecuencia($Frecuencia) {
        $this->Frecuencia = $Frecuencia;
    }

    public function getDuracion() {
        return $this->Duracion;
    }

    public function setDuracion($Duracion) {
        $this->Duracion = $Duracion;
    }

    public function getOrigen() {
        return $this->Origen;
    }

    public function setOrigen($Origen) {
        $this->Origen = $Origen;
    }

    public function getDestino() {
        return $this->Destino;
    }

    public function setDestino($Destino) {
        $this->Destino = $Destino;
    }

    public function getPeriodoDesde() {
        return $this->PeriodoDesde;
    }

    public function setPeriodoDesde($PeriodoDesde) {
        $this->PeriodoDesde = $PeriodoDesde;
    }

    public function getPeriodoHasta() {
        return $this->PeriodoHasta;
    }

    public function setPeriodoHasta($PeriodoHasta) {
        $this->PeriodoHasta = $PeriodoHasta;
    }

    public function getRazonServ() {
        return $this->RazonServ;
    }

    public function setRazonServ($RazonServ) {
        $this->RazonServ = $RazonServ;
    }

}

?>