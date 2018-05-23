<?php
require_once 'BaseDTO.php';
/*
 * To change this template, choose Tools | Templates
 * and open the template in the editor.
 */

/**
 * Description of dto
 *
 * @author ccedillo
 */
class NotesDTO extends BaseDTO {
    protected $notes;
    protected $type;
    protected $date;
    protected $time;
    protected $iD_admin_users;
    
    function __construct() {
        parent::__construct();
        $this->notes = "";        
        $this->date = "";
        $this->time ="";
        $this->iD_admin_users = 0;
    }
    
    public function getNotes() {
        return $this->notes;
    }

    public function setNotes($notes) {
        $this->notes = $notes;
    }

    public function getType() {
        return $this->type;
    }

    public function setType($type) {
        $this->type = $type;
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
        return $this->iD_admin_users;
    }

    public function setID_admin_users($iD_admin_users) {
        $this->iD_admin_users = $iD_admin_users;
    }

}

?>