<?php
/**
 * Description
 *
 * @author L.C.I Cesar Cedillo
 */
function getMaxOrderInRange($lowerLimit, $upperLimit) {
    $max_order = 0;
    $dbh = new DbHandler();
    $dbh->connect();
    
    $cadena_sql = "SELECT IFNULL(MAX(ID_orders),0) AS max_order FROM sl_orders WHERE ID_orders BETWEEN $lowerLimit AND $upperLimit ;";
    $dbh->selectSQLcommand($cadena_sql);
    
    if($result = $dbh->fetchAssocNextRow()){        
        $max_order = $result['max_order'];        
    }    
    $dbh->disconnect();
    
    return $max_order;
}


function calculatePercentValue($percent){
    return floatval($percent / 100);
}

?>