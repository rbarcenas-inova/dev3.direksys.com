<?php

require_once 'BaseDTO.php';

/**
 * Description of dto
 *
 * @author ccedillo
 */
class AdminLogsDTO extends BaseDTO {
    
    private $iD_admin_logs;
    private $logDate;
    private $logTime;
    private $message;
    private $action;
    private $type;
    private $tblName;
    private $logCmd;
    private $iD_admin_users;
    private $iP;
    
    function __construct() {
        parent::__construct();
        
        $this->table_source = 'admin_logs';
        $this->field_list = array('ID_admin_logs',  'LogDate',  'LogTime',  'Message',  'Action',  'Type',  'tbl_name',  'Logcmd',  'ID_admin_users',  'IP');
        
        $this->type = 'Application';
    }
    
    public function getID_admin_logs() {
        return $this->iD_admin_logs;
    }

    public function setID_admin_logs($iD_admin_logs) {
        $this->iD_admin_logs = $iD_admin_logs;
    }

    public function getLogDate() {
        return $this->logDate;
    }

    public function setLogDate($logDate) {
        $this->logDate = $logDate;
    }

    public function getLogTime() {
        return $this->logTime;
    }

    public function setLogTime($logTime) {
        $this->logTime = $logTime;
    }

    public function getMessage() {
        return $this->message;
    }

    public function setMessage($message) {
        $this->message = $message;
    }

    public function getAction() {
        return $this->action;
    }

    public function setAction($action) {
        $this->action = $action;
    }

    public function getType() {
        return $this->type;
    }

    public function setType($type) {
        $this->type = $type;
    }

    public function getTblName() {
        return $this->tblName;
    }

    public function setTblName($tblName) {
        $this->tblName = $tblName;
    }

    public function getLogCmd() {
        return $this->logCmd;
    }

    public function setLogCmd($logCmd) {
        $this->logCmd = $logCmd;
    }

    public function getID_admin_users() {
        return $this->iD_admin_users;
    }

    public function setID_admin_users($iD_admin_users) {
        $this->iD_admin_users = $iD_admin_users;
    }

    public function getIP() {
        return $this->iP;
    }

    public function setIP($iP) {
        $this->iP = $iP;
    }


   
}

?>