<?php

require_once 'dto.common.NotesDTO.php';

/**
 * Description of dto
 *
 * @author ccedillo
 */
class InvoicesNotesDTO extends NotesDTO {

    private $iD_invoices_notes;
    private $iD_invoices;

    function __construct() {
        parent::__construct();
        $this->table_source = 'cu_invoices_notes';
        $this->field_list = array(
            'ID_invoices_notes',
            'ID_invoices',
            'Notes',
            'Type',
            'Date',
            'Time',
            'ID_admin_users'
        );
    }

    public function getID_invoices_notes() {
        return $this->iD_invoices_notes;
    }

    public function setID_invoices_notes($iD_invoices_notes) {
        $this->iD_invoices_notes = $iD_invoices_notes;
    }

    public function getID_invoices() {
        return $this->iD_invoices;
    }

    public function setID_invoices($iD_invoices) {
        $this->iD_invoices = $iD_invoices;
    }

}

?>