<?php
class Tabla {
    private $datos;
    private $val;
    function __construct($datos=array()) {
        $this -> datos = $datos;
        $this->val=false;
    }
    public function __set($varnom, $valor) {
        if($valor!=''){
            $this->datos[$varnom] = $valor;
            $this->val=true;
        }
    }
    public function __get($varnom) {
        return $this->datos[$varnom];
    }
    public function __call($funcion, $params = array()){
        if($funcion=='get'){
            if(isset($this->datos[$params[0]]))
                return new Tabla($this->datos[$params[0]]);
            else 
                return false;
        }
        if($funcion=='num')
            return count($this->datos);
        if($funcion=='vacio')
            return (count($this->datos)==0) ? true: false;
        if($funcion=='valido')
            return $this->val;
   }
    public function getDatos(){
        return $this->datos;
    }
    public function setDatos($datos){
        $this->datos=$datos;
    }
}
?>
