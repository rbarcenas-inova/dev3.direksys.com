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
class ContactoEmisor {

    private $Tipo1;
    private $Nombre1;
    private $Descripcion1;
    private $eMail1;
    private $Telefono1;
    private $Extension1;
    private $Fax1;
    private $Tipo2;
    private $Nombre2;
    private $Descripcion2;
    private $eMail2;
    private $Telefono2;
    private $Extension2;
    private $Fax2;

    function __construct() {
        $this->Tipo1 = "";
        $this->Nombre1 = "";
        $this->Descripcion1 = "";
        $this->eMail1 = "";
        $this->Telefono1 = "";
        $this->Extension1 = "";
        $this->Fax1;
        $this->Tipo2 = "";
        $this->Nombre2 = "";
        $this->Descripcion2 = "";
        $this->eMail2 = "";
        $this->Telefono2 = "";
        $this->Extension2 = "";
        $this->Fax2;
    }

    public function getTipo1() {
        return $this->Tipo1;
    }

    public function setTipo1($Tipo1) {
        $this->Tipo1 = $Tipo1;
    }

    public function getNombre1() {
        return $this->Nombre1;
    }

    public function setNombre1($Nombre1) {
        $this->Nombre1 = $Nombre1;
    }

    public function getDescripcion1() {
        return $this->Descripcion1;
    }

    public function setDescripcion1($Descripcion1) {
        $this->Descripcion1 = $Descripcion1;
    }

    public function getEMail1() {
        return $this->eMail1;
    }

    public function setEMail1($eMail1) {
        $this->eMail1 = $eMail1;
    }

    public function getTelefono1() {
        return $this->Telefono1;
    }

    public function setTelefono1($Telefono1) {
        $this->Telefono1 = $Telefono1;
    }

    public function getExtension1() {
        return $this->Extension1;
    }

    public function setExtension1($Extension1) {
        $this->Extension1 = $Extension1;
    }

    public function getFax1() {
        return $this->Fax1;
    }

    public function setFax1($Fax1) {
        $this->Fax1 = $Fax1;
    }

    public function getTipo2() {
        return $this->Tipo2;
    }

    public function setTipo2($Tipo2) {
        $this->Tipo2 = $Tipo2;
    }

    public function getNombre2() {
        return $this->Nombre2;
    }

    public function setNombre2($Nombre2) {
        $this->Nombre2 = $Nombre2;
    }

    public function getDescripcion2() {
        return $this->Descripcion2;
    }

    public function setDescripcion2($Descripcion2) {
        $this->Descripcion2 = $Descripcion2;
    }

    public function getEMail2() {
        return $this->eMail2;
    }

    public function setEMail2($eMail2) {
        $this->eMail2 = $eMail2;
    }

    public function getTelefono2() {
        return $this->Telefono2;
    }

    public function setTelefono2($Telefono2) {
        $this->Telefono2 = $Telefono2;
    }

    public function getExtension2() {
        return $this->Extension2;
    }

    public function setExtension2($Extension2) {
        $this->Extension2 = $Extension2;
    }

    public function getFax2() {
        return $this->Fax2;
    }

    public function setFax2($Fax2) {
        $this->Fax2 = $Fax2;
    }

}

?>