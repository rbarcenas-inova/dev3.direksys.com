<?php

require_once 'dto.common.NotesDTO.php';

/**
 * Description
 *
 * @author L.C.I Cesar Cedillo
 */
class PurchaseOrdersNotesDTO extends NotesDTO {
    private $iD_purchaseorders_notes;
    private $iD_purchaseorders;
    
    function __construct() {
        parent::__construct();
        $this->table_source = 'sl_purchaseorders_notes';
        $this->field_list = array(
            'ID_purchaseorders_notes',  
            'ID_purchaseorders',  
            'Notes', 
            'Type',  
            'Date',  
            'Time',  
            'ID_admin_users' 
        );
        
        $this->type = "High";
    }
    
    public function getID_purchaseorders_notes() {
        return $this->iD_purchaseorders_notes;
    }

    public function setID_purchaseorders_notes($iD_purchaseorders_notes) {
        $this->iD_purchaseorders_notes = $iD_purchaseorders_notes;
    }

    public function getID_purchaseorders() {
        return $this->iD_purchaseorders;
    }

    public function setID_purchaseorders($iD_purchaseorders) {
        $this->iD_purchaseorders = $iD_purchaseorders;
    }

}
?>