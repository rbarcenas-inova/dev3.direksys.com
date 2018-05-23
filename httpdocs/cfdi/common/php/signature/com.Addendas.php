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
class Addendas {

    private $IdAreaOld;
    private $IdArea;
    private $IdRevision;
    private $Banderas;
    private $ReceiverIDs;
    private $SenderIDGeneric;
    private $SenderID;
    private $SenderIDCorvi;
    private $EmisorRI;
    private $Addendas1;
    private $Addendas2;
    private $Addendas3;
    private $Addendas4;
    private $Addendas5;
    private $Addendas6;

    function __construct() {
        $this->IdAreaOld = "";
        $this->IdArea = "";
        $this->IdRevision = "";
        $this->Banderas = "";
        $this->ReceiverIDs = "";
        $this->SenderIDGeneric = "";
        $this->SenderID = "";
        $this->SenderIDCorvi = "";
        $this->EmisorRI = "";
        $this->Addendas1 = "";
        $this->Addendas2 = "";
        $this->Addendas3 = "";
        $this->Addendas4 = "";
        $this->Addendas5 = "";
        $this->Addendas6 = "";
    }

    public function getIdAreaOld() {
        return $this->IdAreaOld;
    }

    public function setIdAreaOld($IdAreaOld) {
        $this->IdAreaOld = $IdAreaOld;
    }

    public function getIdArea() {
        return $this->IdArea;
    }

    public function setIdArea($IdArea) {
        $this->IdArea = $IdArea;
    }

    public function getIdRevision() {
        return $this->IdRevision;
    }

    public function setIdRevision($IdRevision) {
        $this->IdRevision = $IdRevision;
    }

    public function getBanderas() {
        return $this->Banderas;
    }

    public function setBanderas($Banderas) {
        $this->Banderas = $Banderas;
    }

    public function getReceiverIDs() {
        return $this->ReceiverIDs;
    }

    public function setReceiverIDs($ReceiverIDs) {
        $this->ReceiverIDs = $ReceiverIDs;
    }

    public function getSenderIDGeneric() {
        return $this->SenderIDGeneric;
    }

    public function setSenderIDGeneric($SenderIDGeneric) {
        $this->SenderIDGeneric = $SenderIDGeneric;
    }

    public function getSenderID() {
        return $this->SenderID;
    }

    public function setSenderID($SenderID) {
        $this->SenderID = $SenderID;
    }

    public function getSenderIDCorvi() {
        return $this->SenderIDCorvi;
    }

    public function setSenderIDCorvi($SenderIDCorvi) {
        $this->SenderIDCorvi = $SenderIDCorvi;
    }

    public function getEmisorRI() {
        return $this->EmisorRI;
    }

    public function setEmisorRI($EmisorRI) {
        $this->EmisorRI = $EmisorRI;
    }

    public function getAddendas1() {
        return $this->Addendas1;
    }

    public function setAddendas1($Addendas1) {
        $this->Addendas1 = $Addendas1;
    }

    public function getAddendas2() {
        return $this->Addendas2;
    }

    public function setAddendas2($Addendas2) {
        $this->Addendas2 = $Addendas2;
    }

    public function getAddendas3() {
        return $this->Addendas3;
    }

    public function setAddendas3($Addendas3) {
        $this->Addendas3 = $Addendas3;
    }

    public function getAddendas4() {
        return $this->Addendas4;
    }

    public function setAddendas4($Addendas4) {
        $this->Addendas4 = $Addendas4;
    }

    public function getAddendas5() {
        return $this->Addendas5;
    }

    public function setAddendas5($Addendas5) {
        $this->Addendas5 = $Addendas5;
    }

    public function getAddendas6() {
        return $this->Addendas6;
    }

    public function setAddendas6($Addendas6) {
        $this->Addendas6 = $Addendas6;
    }

}

?>