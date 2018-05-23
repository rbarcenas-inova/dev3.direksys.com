<?php


/**
 * Description of com
 *
 * @author ccedillo
 */
class ReceptorDatos {
    private $RFCRecep;
    private $NmbRecep;
    private $CdgGLNRecep;
    private $TpoCdgIntRecep1;
    private $CdgIntRecep1;
    private $CdgSucursal;
    private $Sucursal;
    private $Contacto;
    
    function __construct() {
        $this->RFCRecep = "";
        $this->NmbRecep = "";
        $this->CdgGLNRecep = "";
        $this->TpoCdgIntRecep1 = "";
        $this->CdgIntRecep1 = "";
        $this->CdgSucursal = "";
        $this->Sucursal = "";
        $this->Contacto = "";
    }
    
    public function getRFCRecep() {
        return $this->RFCRecep;
    }

    public function setRFCRecep($RFCRecep) {
        $this->RFCRecep = $RFCRecep;
    }

    public function getNmbRecep() {
        return $this->NmbRecep;
    }

    public function setNmbRecep($NmbRecep) {
        $this->NmbRecep = $NmbRecep;
    }

    public function getCdgGLNRecep() {
        return $this->CdgGLNRecep;
    }

    public function setCdgGLNRecep($CdgGLNRecep) {
        $this->CdgGLNRecep = $CdgGLNRecep;
    }

    public function getTpoCdgIntRecep1() {
        return $this->TpoCdgIntRecep1;
    }

    public function setTpoCdgIntRecep1($TpoCdgIntRecep1) {
        $this->TpoCdgIntRecep1 = $TpoCdgIntRecep1;
    }

    public function getCdgIntRecep1() {
        return $this->CdgIntRecep1;
    }

    public function setCdgIntRecep1($CdgIntRecep1) {
        $this->CdgIntRecep1 = $CdgIntRecep1;
    }

    public function getCdgSucursal() {
        return $this->CdgSucursal;
    }

    public function setCdgSucursal($CdgSucursal) {
        $this->CdgSucursal = $CdgSucursal;
    }

    public function getSucursal() {
        return $this->Sucursal;
    }

    public function setSucursal($Sucursal) {
        $this->Sucursal = $Sucursal;
    }

    public function getContacto() {
        return $this->Contacto;
    }

    public function setContacto($Contacto) {
        $this->Contacto = $Contacto;
    }


}

?>