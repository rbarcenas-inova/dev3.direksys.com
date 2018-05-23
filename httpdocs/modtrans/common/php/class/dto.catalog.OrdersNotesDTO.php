<?php

//require_once 'BaseDTO.php';
require_once 'dto.common.NotesDTO.php';

/**
 * Description
 *
 * @author L.C.I Cesar Cedillo
 */
class OrdersNotesDTO extends NotesDTO {
    
    private $iD_orders_notes;
    private $iD_orders;

    
    function __construct() {
        parent::__construct();
        
        $this->table_source = 'sl_orders_notes';
        $this->field_list = array('ID_orders_notes',  'ID_orders', 'Notes',  'Type',  'Date',  'Time',  'ID_admin_users');
        
        $this->iD_orders_notes = 0;
        $this->iD_orders = 0;
        $this->notes = "";
        $this->type = "Low";
        $this->iD_admin_users = 0;
    }
  
    
    public function getID_orders_notes() {
        return $this->iD_orders_notes;
    }

    public function setID_orders_notes($iD_orders_notes) {
        $this->iD_orders_notes = $iD_orders_notes;
    }

    public function getID_orders() {
        return $this->iD_orders;
    }

    public function setID_orders($iD_orders) {
        $this->iD_orders = $iD_orders;
    }

}

?>