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
class ImpuestosRetenciones {
    private $TipoRet1;
    private $TasaRet1;
    private $MontoRet1;    
    private $TipoRet2;
    private $TasaRet2;
    private $MontoRet2;    
    
    function __construct() {
        $this->TipoRet1 = "";
        $this->TasaRet2 = "";
        $this->MontoRet1 = "";
        $this->TipoRet2 = "";
        $this->TasaRet2 = "";
        $this->MontoRet2 = "";        
    }
    
    public function getTipoRet1() {
        return $this->TipoRet1;
    }

    public function setTipoRet1($TipoRet1) {
        $this->TipoRet1 = $TipoRet1;
    }

    public function getTasaRet1() {
        return $this->TasaRet1;
    }

    public function setTasaRet1($TasaRet1) {
        $this->TasaRet1 = $TasaRet1;
    }

    public function getMontoRet1() {
        return $this->MontoRet1;
    }

    public function setMontoRet1($MontoRet1) {
        $this->MontoRet1 = $MontoRet1;
    }

    public function getTipoRet2() {
        return $this->TipoRet2;
    }

    public function setTipoRet2($TipoRet2) {
        $this->TipoRet2 = $TipoRet2;
    }

    public function getTasaRet2() {
        return $this->TasaRet2;
    }

    public function setTasaRet2($TasaRet2) {
        $this->TasaRet2 = $TasaRet2;
    }

    public function getMontoRet2() {
        return $this->MontoRet2;
    }

    public function setMontoRet2($MontoRet2) {
        $this->MontoRet2 = $MontoRet2;
    }


}

?>