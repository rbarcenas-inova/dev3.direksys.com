<?php
require_once 'dto.common.NotesDTO.php';

/**
 * Description
 *
 * @author L.C.I Cesar Cedillo
 */
class ReturnsNotesDTO extends NotesDTO {
    private $iD_returns_notes;
    private $iD_returns;

    
    function __construct() {
        parent::__construct();
        
        $this->table_source = 'sl_returns_notes';
        $this->field_list = array('ID_returns_notes',  'ID_returns',  'Notes',  'Type',  'Date',  'Time',  'ID_admin_users');
        
        $this->type = "Reception";
        
    }
    
    public function getID_returns_notes() {
        return $this->iD_returns_notes;
    }

    public function setID_returns_notes($iD_returns_notes) {
        $this->iD_returns_notes = $iD_returns_notes;
    }

    public function getID_returns() {
        return $this->iD_returns;
    }

    public function setID_returns($iD_returns) {
        $this->iD_returns = $iD_returns;
    }


}

?>