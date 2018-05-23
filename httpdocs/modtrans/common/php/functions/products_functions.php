<?php
/**
 * Description
 *
 * @author L.C.I Cesar Cedillo
 */
/**
 * Requiere la carga de archivos de la base de datos;
 * @param type $idProduct
 */

function load_sltvcost($idProduct){
    $dbh = new DbHandler();
    $dbh->connect();
    
    $cadena_sql = "SELECT SUM(Quantity*Cost)/ SUM(Quantity) AS prod_cost FROM sl_skus_cost WHERE ID_products = $idProduct";
    
    $dbh->selectSQLcommand($cadena_sql);
    $result_cost = $dbh->fetchAssocNextRow();
    
    $prod_cost = $result_cost['prod_cost'];  
    
    if(!$prod_cost || $prod_cost == '' || $prod_cost <= 0){
        $cadena_sql = "SELECT AVG(Price) AS avg_price FROM sl_purchaseorders_items WHERE ID_products = '$idProduct' AND Received > 0";
        $dbh->selectSQLcommand($cadena_sql);
        $result_cost = $dbh->fetchAssocNextRow();
        
        $prod_cost = $result_cost['avg_price'];    
        
        if( (preg_match('/^1/', $idProduct) != 1) && (!$prod_cost || $prod_cost == '' || $prod_cost <= 0)){
             $cadena_sql = "SELECT SLTV_NetCost FROM sl_products WHERE ID_products = '" . substr($idProduct, 3, 6) . "'";
             $dbh->selectSQLcommand($cadena_sql);
             $result_cost = $dbh->fetchAssocNextRow();
             
             $prod_cost = $result_cost['SLTV_NetCost'];
        }
    }    
    $dbh->disconnect();
    
    $prod_cost = !$prod_cost ? 0 : $prod_cost;
    
    return $prod_cost;
}
?>