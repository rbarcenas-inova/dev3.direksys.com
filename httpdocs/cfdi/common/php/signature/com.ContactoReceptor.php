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
class ContactoReceptor {

    private $Tipo1;
    private $Nombre1;
    private $Descripcion1;
    private $eMail1;
    private $Telefono1;
    private $Extension1;
    private $Fax1;

    function __construct() {
        $this->Tipo1 = "";
        $this->Nombre1 = "";
        $this->Descripcion1 = "";
        $this->eMail1 = "";
        $this->Telefono1 = "";
        $this->Extension1 = "";
        $this->Fax1;
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

}

?>