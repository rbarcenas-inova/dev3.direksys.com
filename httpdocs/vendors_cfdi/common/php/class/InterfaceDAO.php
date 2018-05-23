<?php

interface InterfaceDAO{
    public function selectRecords(&$objectDTO);
    public function insertRecord(&$objectDTO);
    public function updateRecord(&$objectDTO);
    public function deleteRecord(&$objectDTO);
}
?>