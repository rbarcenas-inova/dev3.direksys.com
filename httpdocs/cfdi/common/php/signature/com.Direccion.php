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
class Direccion {
    protected $Calle;
    protected $NroExterior;
    protected $NroInterior;
    protected $Colonia;
    protected $Localidad;
    protected $Referencia;
    protected $Municipio;
    protected $Estado;
    protected $Pais;
    protected $CodigoPostal;
    protected $GLN;
    
    
    function __construct() {
        $this->Calle = "";
        $this->NroInterior = "";
        $this->NroInterior = "";
        $this->Colonia = "";
        $this->Localidad = "";
        $this->Referencia = "";
        $this->Municipio = "";
        $this->Estado = "";
        $this->Pais = "";
        $this->CodigoPostal = "";
        $this->GLN  = "";
    }
    
    public function getCalle() {
        return $this->Calle;
    }

    public function setCalle($Calle) {
        $this->Calle = $Calle;
    }

    public function getNroExterior() {
        return $this->NroExterior;
    }

    public function setNroExterior($NroExterior) {
        $this->NroExterior = $NroExterior;
    }

    public function getNroInterior() {
        return $this->NroInterior;
    }

    public function setNroInterior($NroInterior) {
        $this->NroInterior = $NroInterior;
    }

    public function getColonia() {
        return $this->Colonia;
    }

    public function setColonia($Colonia) {
        $this->Colonia = $Colonia;
    }

    public function getLocalidad() {
        return $this->Localidad;
    }

    public function setLocalidad($Localidad) {
        $this->Localidad = $Localidad;
    }

    public function getReferencia() {
        return $this->Referencia;
    }

    public function setReferencia($Referencia) {
        $this->Referencia = $Referencia;
    }

    public function getMunicipio() {
        return $this->Municipio;
    }

    public function setMunicipio($Municipio) {
        $this->Municipio = $Municipio;
    }

    public function getEstado() {
        return $this->Estado;
    }

    public function setEstado($Estado) {
        $this->Estado = $Estado;
    }

    public function getPais() {
        return $this->Pais;
    }

    public function setPais($Pais) {
        $this->Pais = $Pais;
    }

    public function getCodigoPostal() {
        return $this->CodigoPostal;
    }

    public function setCodigoPostal($CodigoPostal) {
        $this->CodigoPostal = $CodigoPostal;
    }

    public function getGLN() {
        return $this->GLN;
    }

    public function setGLN($GLN) {
        $this->GLN = $GLN;
    }

    
}

?>