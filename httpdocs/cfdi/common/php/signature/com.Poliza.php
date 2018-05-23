<?php


/**
 * Description of com
 *
 * @author ccedillo
 */
class Poliza {
    private $TipoPol;
    private $Numero;
    private $INC;
    private $TpoCliente;
    private $NroReporte;
    private $NroSint;
    private $Tramitador;
    private $NroExp;
    private $NmbCont;
    private $CdgCont;
    private $DireccionCont;
    private $NmbAseg;
    private $CdgAseg;
    private $DireccionAseg;
    private $NmbAfect;
    private $CdgAfect;
    private $DireccionAfect;
    private $VigDesde;
    private $VigHasta;
    
    function __construct() {
        $this->TipoPol = "";
        $this->Numero = "";
        $this->INC = "";
        $this->TpoCliente = "";
        $this->NroReporte = "";
        $this->NroSint = "";
        $this->Tramitador = "";
        $this->NroExp = "";
        $this->NmbCont = "";
        $this->CdgCont = "";
        $this->DireccionCont = "";
        $this->NmbAseg = "";
        $this->CdgAseg = "";
        $this->DireccionAseg = "";
        $this->NmbAfect = "";
        $this->CdgAfect ="";
        $this->DireccionAfect = "";
        $this->VigDesde  ="";
        $this->VigHasta = "";
    }
    
    public function getTipoPol() {
        return $this->TipoPol;
    }

    public function setTipoPol($TipoPol) {
        $this->TipoPol = $TipoPol;
    }

    public function getNumero() {
        return $this->Numero;
    }

    public function setNumero($Numero) {
        $this->Numero = $Numero;
    }

    public function getINC() {
        return $this->INC;
    }

    public function setINC($INC) {
        $this->INC = $INC;
    }

    public function getTpoCliente() {
        return $this->TpoCliente;
    }

    public function setTpoCliente($TpoCliente) {
        $this->TpoCliente = $TpoCliente;
    }

    public function getNroReporte() {
        return $this->NroReporte;
    }

    public function setNroReporte($NroReporte) {
        $this->NroReporte = $NroReporte;
    }

    public function getNroSint() {
        return $this->NroSint;
    }

    public function setNroSint($NroSint) {
        $this->NroSint = $NroSint;
    }

    public function getTramitador() {
        return $this->Tramitador;
    }

    public function setTramitador($Tramitador) {
        $this->Tramitador = $Tramitador;
    }

    public function getNroExp() {
        return $this->NroExp;
    }

    public function setNroExp($NroExp) {
        $this->NroExp = $NroExp;
    }

    public function getNmbCont() {
        return $this->NmbCont;
    }

    public function setNmbCont($NmbCont) {
        $this->NmbCont = $NmbCont;
    }

    public function getCdgCont() {
        return $this->CdgCont;
    }

    public function setCdgCont($CdgCont) {
        $this->CdgCont = $CdgCont;
    }

    public function getDireccionCont() {
        return $this->DireccionCont;
    }

    public function setDireccionCont($DireccionCont) {
        $this->DireccionCont = $DireccionCont;
    }

    public function getNmbAseg() {
        return $this->NmbAseg;
    }

    public function setNmbAseg($NmbAseg) {
        $this->NmbAseg = $NmbAseg;
    }

    public function getCdgAseg() {
        return $this->CdgAseg;
    }

    public function setCdgAseg($CdgAseg) {
        $this->CdgAseg = $CdgAseg;
    }

    public function getDireccionAseg() {
        return $this->DireccionAseg;
    }

    public function setDireccionAseg($DireccionAseg) {
        $this->DireccionAseg = $DireccionAseg;
    }

    public function getNmbAfect() {
        return $this->NmbAfect;
    }

    public function setNmbAfect($NmbAfect) {
        $this->NmbAfect = $NmbAfect;
    }

    public function getCdgAfect() {
        return $this->CdgAfect;
    }

    public function setCdgAfect($CdgAfect) {
        $this->CdgAfect = $CdgAfect;
    }

    public function getDireccionAfect() {
        return $this->DireccionAfect;
    }

    public function setDireccionAfect($DireccionAfect) {
        $this->DireccionAfect = $DireccionAfect;
    }

    public function getVigDesde() {
        return $this->VigDesde;
    }

    public function setVigDesde($VigDesde) {
        $this->VigDesde = $VigDesde;
    }

    public function getVigHasta() {
        return $this->VigHasta;
    }

    public function setVigHasta($VigHasta) {
        $this->VigHasta = $VigHasta;
    }

}

?>