<?php

/**
 * Description of com
 *
 * @author ccedillo
 */
class Local {
    private $Tipo;
    private $SecTipo;
    private $SecNro;
    
    function __construct() {
        $this->Tipo = "";
        $this->SecTipo = "";
        $this->SecNro = "";
    }
    
    public function getTipo() {
        return $this->Tipo;
    }

    public function setTipo($Tipo) {
        $this->Tipo = $Tipo;
    }

    public function getSecTipo() {
        return $this->SecTipo;
    }

    public function setSecTipo($SecTipo) {
        $this->SecTipo = $SecTipo;
    }

    public function getSecNro() {
        return $this->SecNro;
    }

    public function setSecNro($SecNro) {
        $this->SecNro = $SecNro;
    }


}

?>