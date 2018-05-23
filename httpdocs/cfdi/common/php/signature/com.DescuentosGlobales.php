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
class DescuentosGlobales {

    private $TpoMov1;
    private $CodigoDR1;
    private $GlosaDR1;
    private $TpoValor1;
    private $ValorDR1;
    private $TpoMov2;
    private $CodigoDR2;
    private $GlosaDR2;
    private $TpoValor2;
    private $ValorDR2;

    function __construct() {
        $this->TpoMov1 = "";
        $this->CodigoDR1 = "";
        $this->GlosaDR1 = "";
        $this->TpoValor1 = "";
        $this->ValorDR1 = "";
        $this->TpoMov2 = "";
        $this->CodigoDR2 = "";
        $this->GlosaDR2 = "";
        $this->TpoValor2 = "";
        $this->ValorDR2 = "";
    }

    public function getTpoMov1() {
        return $this->TpoMov1;
    }

    public function setTpoMov1($TpoMov1) {
        $this->TpoMov1 = $TpoMov1;
    }

    public function getCodigoDR1() {
        return $this->CodigoDR1;
    }

    public function setCodigoDR1($CodigoDR1) {
        $this->CodigoDR1 = $CodigoDR1;
    }

    public function getGlosaDR1() {
        return $this->GlosaDR1;
    }

    public function setGlosaDR1($GlosaDR1) {
        $this->GlosaDR1 = $GlosaDR1;
    }

    public function getTpoValor1() {
        return $this->TpoValor1;
    }

    public function setTpoValor1($TpoValor1) {
        $this->TpoValor1 = $TpoValor1;
    }

    public function getValorDR1() {
        return $this->ValorDR1;
    }

    public function setValorDR1($ValorDR1) {
        $this->ValorDR1 = $ValorDR1;
    }

    public function getTpoMov2() {
        return $this->TpoMov2;
    }

    public function setTpoMov2($TpoMov2) {
        $this->TpoMov2 = $TpoMov2;
    }

    public function getCodigoDR2() {
        return $this->CodigoDR2;
    }

    public function setCodigoDR2($CodigoDR2) {
        $this->CodigoDR2 = $CodigoDR2;
    }

    public function getGlosaDR2() {
        return $this->GlosaDR2;
    }

    public function setGlosaDR2($GlosaDR2) {
        $this->GlosaDR2 = $GlosaDR2;
    }

    public function getTpoValor2() {
        return $this->TpoValor2;
    }

    public function setTpoValor2($TpoValor2) {
        $this->TpoValor2 = $TpoValor2;
    }

    public function getValorDR2() {
        return $this->ValorDR2;
    }

    public function setValorDR2($ValorDR2) {
        $this->ValorDR2 = $ValorDR2;
    }

}

?>