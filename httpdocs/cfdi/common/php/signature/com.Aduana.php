<?php

/**
 * Description
 *
 * @author fcanaveral
 */
class Aduana {
    private $data;
    private $db;
    function __construct($db) {
        $this->data = array();
        $this->db = $db;
    }
    public function __set($name,$value){
        $this->data[$name] = $value;
    }
    public function __get($name){
        return isset($this->data[$name]) ? $this->data[$name] : '';
    }
    public function getCabecera(){
        return "================ DatosAduanales";
    }
    public function getAduana($id){
        if($this->db instanceof DbHandler){
            $query = "SELECT 
                sl_skus_trans.ID_products_trans,
                cu_customs_info.import_declaration_number
                , cu_customs_info.import_declaration_date
                , cu_customs_info.customs
                , sl_vendors.CompanyName
            FROM 
                sl_skus_trans 
            INNER JOIN cu_customs_info ON sl_skus_trans.ID_customs_info=cu_customs_info.ID_customs_info
            LEFT JOIN sl_vendors ON sl_vendors.ID_vendors=cu_customs_info.ID_vendors
            WHERE 
                ID_trs=$id AND
                tbl_name='sl_orders' 
            ORDER BY 
                sl_skus_trans.ID_products_trans;";
            $result = $this->db->selectSQLcommand($query);
            $response = '';
            if ($result) {
                while($row = mysql_fetch_array($result)) {
                    $response.= "$row[0]  $row[1]     $row[2]     $row[3]     $row[4]";
                }
            }
            return $response;
        }
        return '';
    }
}
?>

-