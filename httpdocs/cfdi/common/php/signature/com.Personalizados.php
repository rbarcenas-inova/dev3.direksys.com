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
class Personalizados {

    private $TpoDocRefON;
    private $FolioRefON;
    private $FechaRefON;
    private $TpoDocRefDQ;
    private $FolioRefDQ;
    private $FechaRefDQ;
    private $FolioPedido;
    private $FechaPedido;
    private $ElaboradoPor;
    private $ViaEmbarque;
    private $NumEmbarque;
    private $NumEmbarqueInt;
    private $EmURL;
    private $EmMarca;

    function __construct() {
        $this->TpoDocRefON = "";
        $this->FolioRefON = "";
        $this->FechaRefON = "";
        $this->TpoDocRefDQ = "";
        $this->FolioRefDQ = "";
        $this->FechaRefDQ = "";
        $this->FolioPedido = "";
        $this->FechaPedido = "";
        $this->ElaboradoPor = "";
        $this->ViaEmbarque = "";
        $this->NumEmbarque = "";
        $this->NumEmbarqueInt = "";
        $this->EmURL = "";
        $this->EmMarca = "";
    }

    public function getTpoDocRefON() {
        return $this->TpoDocRefON;
    }

    public function setTpoDocRefON($TpoDocRefON) {
        $this->TpoDocRefON = $TpoDocRefON;
    }

    public function getFolioRefON() {
        return $this->FolioRefON;
    }

    public function setFolioRefON($FolioRefON) {
        $this->FolioRefON = $FolioRefON;
    }

    public function getFechaRefON() {
        return $this->FechaRefON;
    }

    public function setFechaRefON($FechaRefON) {
        $this->FechaRefON = $FechaRefON;
    }

    public function getTpoDocRefDQ() {
        return $this->TpoDocRefDQ;
    }

    public function setTpoDocRefDQ($TpoDocRefDQ) {
        $this->TpoDocRefDQ = $TpoDocRefDQ;
    }

    public function getFolioRefDQ() {
        return $this->FolioRefDQ;
    }

    public function setFolioRefDQ($FolioRefDQ) {
        $this->FolioRefDQ = $FolioRefDQ;
    }

    public function getFechaRefDQ() {
        return $this->FechaRefDQ;
    }

    public function setFechaRefDQ($FechaRefDQ) {
        $this->FechaRefDQ = $FechaRefDQ;
    }

    public function getFolioPedido() {
        return $this->FolioPedido;
    }

    public function setFolioPedido($FolioPedido) {
        $this->FolioPedido = $FolioPedido;
    }

    public function getFechaPedido() {
        return $this->FechaPedido;
    }

    public function setFechaPedido($FechaPedido) {
        $this->FechaPedido = $FechaPedido;
    }

    public function getElaboradoPor() {
        return $this->ElaboradoPor;
    }

    public function setElaboradoPor($ElaboradoPor) {
        $this->ElaboradoPor = $ElaboradoPor;
    }

    public function getViaEmbarque() {
        return $this->ViaEmbarque;
    }

    public function setViaEmbarque($ViaEmbarque) {
        $this->ViaEmbarque = $ViaEmbarque;
    }

    public function getNumEmbarque() {
        return $this->NumEmbarque;
    }

    public function setNumEmbarque($NumEmbarque) {
        $this->NumEmbarque = $NumEmbarque;
    }

    public function getNumEmbarqueInt() {
        return $this->NumEmbarqueInt;
    }

    public function setNumEmbarqueInt($NumEmbarqueInt) {
        $this->NumEmbarqueInt = $NumEmbarqueInt;
    }

    public function getEmURL() {
        return $this->EmURL;
    }

    public function setEmURL($EmURL) {
        $this->EmURL = $EmURL;
    }

    public function getEmMarca() {
        return $this->EmMarca;
    }

    public function setEmMarca($EmMarca) {
        $this->EmMarca = $EmMarca;
    }

}

?>