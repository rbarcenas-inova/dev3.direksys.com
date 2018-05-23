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
class Vehiculo {

    private $TipoVeh;
    private $Marca;
    private $Modelo;
    private $Ano;
    private $Color;
    private $NroChasis;
    private $NroSerie;
    private $Placa;

    function __construct() {
        $this->TipoVeh = "";
        $this->Marca = "";
        $this->Modelo = "";
        $this->Ano = "";
        $this->Color = "";
        $this->NroChasis = "";
        $this->NroSerie = "";
        $this->Placa = "";
    }
    
    public function getTipoVeh() {
        return $this->TipoVeh;
    }

    public function setTipoVeh($TipoVeh) {
        $this->TipoVeh = $TipoVeh;
    }

    public function getMarca() {
        return $this->Marca;
    }

    public function setMarca($Marca) {
        $this->Marca = $Marca;
    }

    public function getModelo() {
        return $this->Modelo;
    }

    public function setModelo($Modelo) {
        $this->Modelo = $Modelo;
    }

    public function getAno() {
        return $this->Ano;
    }

    public function setAno($Ano) {
        $this->Ano = $Ano;
    }

    public function getColor() {
        return $this->Color;
    }

    public function setColor($Color) {
        $this->Color = $Color;
    }

    public function getNroChasis() {
        return $this->NroChasis;
    }

    public function setNroChasis($NroChasis) {
        $this->NroChasis = $NroChasis;
    }

    public function getNroSerie() {
        return $this->NroSerie;
    }

    public function setNroSerie($NroSerie) {
        $this->NroSerie = $NroSerie;
    }

    public function getPlaca() {
        return $this->Placa;
    }

    public function setPlaca($Placa) {
        $this->Placa = $Placa;
    }

}

?>