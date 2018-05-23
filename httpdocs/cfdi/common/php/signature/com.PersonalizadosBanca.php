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
class PersonalizadosBanca {
    private $EmRefBanBanca;
    private $EmRefBanTitular;
    private $EmRefBanCuenta;
    private $EmRefBanCLABE;
    private $EmRefBanConvenio;
    private $EmRepLegNombre;
    private $EmRepLegRFC;
    private $RecRepLegNombre;
    private $RecRepLegRFC;
    private $RecRefBanRef;
    private $RecEmailDist;
    
    function __construct() {
        $this->EmRefBanBanca = "";
        $this->EmRefBanTitular = "";
        $this->EmRefBanCuenta = "";
        $this->EmRefBanCLABE = "";
        $this->EmRefBanConvenio = "";
        $this->EmRepLegNombre = "";
        $this->EmRepLegRFC = "";
        $this->RecRepLegNombre = "";
        $this->RecRepLegRFC = "";
        $this->RecRefBanRef = "";
        $this->RecEmailDist = "";
    }
    
    public function getEmRefBanBanca() {
        return $this->EmRefBanBanca;
    }

    public function setEmRefBanBanca($EmRefBanBanca) {
        $this->EmRefBanBanca = $EmRefBanBanca;
    }

    public function getEmRefBanTitular() {
        return $this->EmRefBanTitular;
    }

    public function setEmRefBanTitular($EmRefBanTitular) {
        $this->EmRefBanTitular = $EmRefBanTitular;
    }

    public function getEmRefBanCuenta() {
        return $this->EmRefBanCuenta;
    }

    public function setEmRefBanCuenta($EmRefBanCuenta) {
        $this->EmRefBanCuenta = $EmRefBanCuenta;
    }

    public function getEmRefBanCLABE() {
        return $this->EmRefBanCLABE;
    }

    public function setEmRefBanCLABE($EmRefBanCLABE) {
        $this->EmRefBanCLABE = $EmRefBanCLABE;
    }

    public function getEmRefBanConvenio() {
        return $this->EmRefBanConvenio;
    }

    public function setEmRefBanConvenio($EmRefBanConvenio) {
        $this->EmRefBanConvenio = $EmRefBanConvenio;
    }

    public function getEmRepLegNombre() {
        return $this->EmRepLegNombre;
    }

    public function setEmRepLegNombre($EmRepLegNombre) {
        $this->EmRepLegNombre = $EmRepLegNombre;
    }

    public function getEmRepLegRFC() {
        return $this->EmRepLegRFC;
    }

    public function setEmRepLegRFC($EmRepLegRFC) {
        $this->EmRepLegRFC = $EmRepLegRFC;
    }

    public function getRecRepLegNombre() {
        return $this->RecRepLegNombre;
    }

    public function setRecRepLegNombre($RecRepLegNombre) {
        $this->RecRepLegNombre = $RecRepLegNombre;
    }

    public function getRecRepLegRFC() {
        return $this->RecRepLegRFC;
    }

    public function setRecRepLegRFC($RecRepLegRFC) {
        $this->RecRepLegRFC = $RecRepLegRFC;
    }

    public function getRecRefBanRef() {
        return $this->RecRefBanRef;
    }

    public function setRecRefBanRef($RecRefBanRef) {
        $this->RecRefBanRef = $RecRefBanRef;
    }

    public function getRecEmailDist() {
        return $this->RecEmailDist;
    }

    public function setRecEmailDist($RecEmailDist) {
        $this->RecEmailDist = $RecEmailDist;
    }


}

?>