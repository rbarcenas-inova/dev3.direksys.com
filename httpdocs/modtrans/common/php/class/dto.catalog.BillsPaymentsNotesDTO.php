<?php
require_once 'dto.common.NotesDTO.php';


/**
 * Description
 *
 * @author L.C.I Cesar Cedillo
 */
class BillsPaymentsNotesDTO extends NotesDTO {
  private $iD_billspayments_notes;
  private $iD_billspayments;
  
  function __construct() {
      parent::__construct();
      
      $this->table_source = 'sl_billspayments_notes';
      $this->field_list = array(
          'ID_billspayments_notes',  
          'ID_billspayments',  
          'Notes',  
          'Type',  
          'Date',  
          'Time',  
          'ID_admin_users'
      );
      
      $this->type = 'High';
  }
    
  public function getID_billspayments_notes() {
      return $this->iD_billspayments_notes;
  }

  public function setID_billspayments_notes($iD_billspayments_notes) {
      $this->iD_billspayments_notes = $iD_billspayments_notes;
  }

  public function getID_billspayments() {
      return $this->iD_billspayments;
  }

  public function setID_billspayments($iD_billspayments) {
      $this->iD_billspayments = $iD_billspayments;
  }

}

?>