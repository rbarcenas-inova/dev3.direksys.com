<?php

/**
 * Description of com
 *
 * @author ccedillo
 */
class Referencia {
    
    private $TpoDocRef;
    private $FolioRef;
    private $FechaRef;
    private $RazonRef;
    private $MontoRef1;
    private $MontoRef2;

    function __construct() {
        $this->TpoDocRef = "";
        $this->FolioRef = "";
        $this->FechaRef = "";
        $this->RazonRef = "";
        $this->MontoRef1 = "";
        $this->MontoRef2 = "";
                 
    }
    
    public function getTpoDocRef() {
        return $this->TpoDocRef;
    }

    public function setTpoDocRef($TpoDocRef) {
        $this->TpoDocRef = $TpoDocRef;
    }

    public function getFolioRef() {
        return $this->FolioRef;
    }

    public function setFolioRef($FolioRef) {
        $this->FolioRef = $FolioRef;
    }

    public function getFechaRef() {
        return $this->FechaRef;
    }

    public function setFechaRef($FechaRef) {
        $this->FechaRef = $FechaRef;
    }

    public function getRazonRef() {
        return $this->RazonRef;
    }

    public function setRazonRef($RazonRef) {
        $this->RazonRef = $RazonRef;
    }

    public function getMontoRef1() {
        return $this->MontoRef1;
    }

    public function setMontoRef1($MontoRef1) {
        $this->MontoRef1 = $MontoRef1;
    }

    public function getMontoRef2() {
        return $this->MontoRef2;
    }

    public function setMontoRef2($MontoRef2) {
        $this->MontoRef2 = $MontoRef2;
    }


}

?>