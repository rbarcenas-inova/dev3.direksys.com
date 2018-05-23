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
class ImpuestosTraslados {

    private $TipoImp1;
    private $TasaImp1;
    private $MontoImp1;
    private $TipoImp2;
    private $TasaImp2;
    private $MontoImp2;

    function __construct() {
        $this->TipoImp1 = "";
        $this->TasaImp1 = "";
        $this->MontoImp1 = "";
        $this->TipoImp2 = "";
        $this->TasaImp2 = "";
        $this->MontoImp2 = "";
    }

    public function getTipoImp1() {
        return $this->TipoImp1;
    }

    public function setTipoImp1($TipoImp1) {
        $this->TipoImp1 = $TipoImp1;
    }

    public function getTasaImp1() {
        return $this->TasaImp1;
    }

    public function setTasaImp1($TasaImp1) {
        $this->TasaImp1 = $TasaImp1;
    }

    public function getMontoImp1() {
        return $this->MontoImp1;
    }

    public function setMontoImp1($MontoImp1) {
        $this->MontoImp1 = $MontoImp1;
    }

    public function getTipoImp2() {
        return $this->TipoImp2;
    }

    public function setTipoImp2($TipoImp2) {
        $this->TipoImp2 = $TipoImp2;
    }

    public function getTasaImp2() {
        return $this->TasaImp2;
    }

    public function setTasaImp2($TasaImp2) {
        $this->TasaImp2 = $TasaImp2;
    }

    public function getMontoImp2() {
        return $this->MontoImp2;
    }

    public function setMontoImp2($MontoImp2) {
        $this->MontoImp2 = $MontoImp2;
    }
   
}

?>