<?php

/**
 * Description of BaseDTO
 *
 * @author Eduardo Cesar Cedillo Jimenez
 */
class BaseDTO {

    protected $table_source;
    protected $field_list;
    protected $date;
    protected $time;
    protected $ID_admin_users;

    function __construct() {
        $this->table_source = "";
        $this->field_list = array();
    }

    public function getDate() {
        return $this->date;
    }

    public function setDate($date) {
        $this->date = $date;
    }

    public function getTime() {
        return $this->time;
    }

    public function setTime($time) {
        $this->time = $time;
    }

    public function getID_admin_users() {
        return $this->ID_admin_users;
    }

    public function setID_admin_users($ID_admin_users) {
        $this->ID_admin_users = $ID_admin_users;
    }

        
    /**
     * Regresa el nombre de la tabla a la que apunta el objeto
     * @return <string> 
     */
    public function getTableSource() {
        return $this->table_source;
    }

    /**
     * Obtiene la lista del nombre de los campos en forma de Array
     * @return <array>
     */
    public function getFieldList() {
        return (array) $this->field_list;
    }

    /**
     * Regresa la lista del nombre de las columnas en forma de String
     * @return string   Nombre de las columnas en forma de string separado por comas
     */
    public function getStringTableMetadata($useAutoIncrement = FALSE) {
        $string_metadata = "";
        if ($useAutoIncrement) {
            $indice_inicial = 1;
        } else {
            $indice_inicial = 0;
        }

        if (is_array($this->field_list)) {
            $array_size = sizeof($this->field_list);
            for ($i = $indice_inicial; $i < $array_size; $i++) {
                if ($i == ($array_size - 1)) {
                    $string_metadata .= $this->field_list[$i];
                } else {
                    $string_metadata .= $this->field_list[$i] . ",";
                }
            }
        }
        return $string_metadata;
    }

}

?>