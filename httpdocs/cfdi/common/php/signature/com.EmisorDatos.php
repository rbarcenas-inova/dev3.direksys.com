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
class EmisorDatos {
    private $RFCEmisor;
    private $NmbEmisor;
    private $CdgGLNEmisor;
    private $TpoCdgIntEmisor1;
    private $CdgIntEmisor1;
    private $TpoCdgIntEmisor2;
    private $CdgIntEmisor2;
    private $CdgSucursal;
    private $Sucursal;
    private $CdgVendedor;
    
    function __construct() {
        $this->RFCEmisor = "";
        $this->NmbEmisor = "";
        $this->CdgGLNEmisor = "";
        $this->TpoCdgIntEmisor1 = "";
        $this->CdgIntEmisor1 = "";
        $this->TpoCdgIntEmisor2 = "";
        $this->CdgIntEmisor2 = "";
        $this->CdgSucursal = "";
        $this->Sucursal = "";
        $this->CdgVendedor = "";
    }
    
    public function getRFCEmisor() {
        return $this->RFCEmisor;
    }

    public function setRFCEmisor($RFCEmisor) {
        $this->RFCEmisor = $RFCEmisor;
    }

    public function getNmbEmisor() {
        return $this->NmbEmisor;
    }

    public function setNmbEmisor($NmbEmisor) {
        $this->NmbEmisor = $NmbEmisor;
    }

    public function getCdgGLNEmisor() {
        return $this->CdgGLNEmisor;
    }

    public function setCdgGLNEmisor($CdgGLNEmisor) {
        $this->CdgGLNEmisor = $CdgGLNEmisor;
    }

    public function getTpoCdgIntEmisor1() {
        return $this->TpoCdgIntEmisor1;
    }

    public function setTpoCdgIntEmisor1($TpoCdgIntEmisor1) {
        $this->TpoCdgIntEmisor1 = $TpoCdgIntEmisor1;
    }

    public function getCdgIntEmisor1() {
        return $this->CdgIntEmisor1;
    }

    public function setCdgIntEmisor1($CdgIntEmisor1) {
        $this->CdgIntEmisor1 = $CdgIntEmisor1;
    }

    public function getTpoCdgIntEmisor2() {
        return $this->TpoCdgIntEmisor2;
    }

    public function setTpoCdgIntEmisor2($TpoCdgIntEmisor2) {
        $this->TpoCdgIntEmisor2 = $TpoCdgIntEmisor2;
    }

    public function getCdgIntEmisor2() {
        return $this->CdgIntEmisor2;
    }

    public function setCdgIntEmisor2($CdgIntEmisor2) {
        $this->CdgIntEmisor2 = $CdgIntEmisor2;
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

    public function getCdgVendedor() {
        return $this->CdgVendedor;
    }

    public function setCdgVendedor($CdgVendedor) {
        $this->CdgVendedor = $CdgVendedor;
    }

}

?>