<?php

require_once 'dto.common.NotesDTO.php';

/**
 * Description
 *
 * @author L.C.I Cesar Cedillo
 */
class BillsNotesDTO extends NotesDTO {

    private $iD_bills_notes;
    private $iD_bills;

    function __construct() {
        parent::__construct();
        $this->table_source = 'sl_bills_notes';
        $this->field_list = array(
            'ID_bills_notes',
            'ID_bills',
            'Notes',
            'Type',
            'Date',
            'Time',
            'ID_admin_users'
        );
        
        $this->type = 'High';
    }

    public function getID_bills_notes() {
        return $this->iD_bills_notes;
    }

    public function setID_bills_notes($iD_bills_notes) {
        $this->iD_bills_notes = $iD_bills_notes;
    }

    public function getID_bills() {
        return $this->iD_bills;
    }

    public function setID_bills($iD_bills) {
        $this->iD_bills = $iD_bills;
    }


}

?>