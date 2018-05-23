

#############################################################################
#############################################################################
#   Function: sku_logging
#
#       Es: Registra movimientos de sku de todo tipo entradas/salidas
#       En: 
#
#
#    Created on: 2013-06-18
#
#    Author: _RB_
#
#    Modifications:
#
#    19-02-2015::AD::Se agrega columna Cost_Adj para el costo de Aterrizaje
#
#   Parameters:
#
#      - $sku, $id_warehouses, $location, $type, $id_table, $tbl, $quantity, $cost
#      
#
#  Returns:
#
#      - None
#
#   See Also:
#
#      <move_inventory>
#
sub sku_logging {
#############################################################################
#############################################################################
    my ($sku, $id_warehouses, $location, $type, $id_table, $tbl, $quantity, $cost, $cost_adj, $type_trans, $id_customs_info, $cost_add) = @_;
    my $log = qq|($sku, $id_warehouses, $location, $type, $id_table, $tbl, $quantity, $cost, $cost_adj, $type_trans, $id_customs_info)\n|;
    (!$usr{'id_admin_users'}) and ($usr{'id_admin_users'} = 0);
    (!$cost) and ($cost = 0);

    my $add_sql = '';
    ### Datos aduanales
    $add_sql .= ($id_customs_info and $id_customs_info ne '')? ", ID_customs_info='$id_customs_info' ":"";
    ### Costo complementario
    $add_sql .= ($cost_add)? ", Cost_Add='$cost_add' ":"";
    
    ####################################
    ### Se calculan los Left quantity
    ####################################
    my ($this_sku, $left_qty, $left_qty_total, $cost_avg, $total_cost_avg, $cost_adj_avg, $total_cost_adj_avg);
    if ($cfg{'acc_inventoryout_method_cost'} and lc($cfg{'acc_inventoryout_method_cost'}) eq 'average'){

        my $sql = "SELECT 
                        ID_products
                        , left_quantity
                        , left_quantity_total 
                        , Cost_Avg
                        , (cu_skus_trans.left_quantity_total * cu_skus_trans.Cost_Avg)AS total_cost_avg
                        , Cost_Adj_Avg
                        , (cu_skus_trans.left_quantity_total * cu_skus_trans.Cost_Adj_Avg)AS total_cost_adj_avg
                    FROM cu_skus_trans 
                    WHERE ID_products = ".int($sku)." AND ID_warehouses = ".int($id_warehouses)."
                    FOR UPDATE;";
        $log .= $sql."<br>\n";
        my $sth_qty = &Do_SQL($sql);
        ($this_sku, $left_qty, $left_qty_total, $cost_avg, $total_cost_avg, $cost_adj_avg, $total_cost_adj_avg) = $sth_qty->fetchrow_array();
        $log .= qq|Cost Data ==>> ($this_sku, $left_qty, $left_qty_total, $cost_avg, $total_cost_avg, $cost_adj_avg, $total_cost_adj_avg)|."<br>\n";
        if( !$this_sku ){
            my $sql = "SELECT 
                            ID_products
                            , 0
                            , left_quantity_total 
                            , Cost_Avg
                            , (cu_skus_trans.left_quantity_total * cu_skus_trans.Cost_Avg)AS total_cost_avg
                            , Cost_Adj_Avg
                            , (cu_skus_trans.left_quantity_total * cu_skus_trans.Cost_Adj_Avg)AS total_cost_adj_avg
                        FROM cu_skus_trans 
                        WHERE ID_products = ".int($sku)." 
                        ORDER BY Date DESC, Time DESC
                        LIMIT 1
                        FOR UPDATE;";
            $log .= $sql."<br>\n";
            my $sth_qty = &Do_SQL($sql);
            ($this_sku, $left_qty, $left_qty_total, $cost_avg, $total_cost_avg, $cost_adj_avg, $total_cost_adj_avg) = $sth_qty->fetchrow_array();
            if( !$this_sku ){
                # &Do_SQL('ROLLBACK;');
                # &cgierr($sku.' ['.$id_warehouses.'] : Cost average not found !!!');
                if( $cost > 0 ){
                    $left_qty = 0;
                    $left_qty_total = 0;
                    $cost_avg = $cost;
                    $cost_adj_avg = $cost_adj;
                    $total_cost_avg = 0;
                    $total_cost_adj_avg = 0;
                } else {
                    &Do_SQL('ROLLBACK;');
                    &cgierr($sku.' ['.$id_warehouses.'] : Cost('.$cost.') average invalid !!!');
                }
            }
        }

    } else {

        $sql = "SELECT left_quantity, left_quantity_total FROM sl_skus_trans WHERE ID_products=".int($sku)." AND ID_warehouses = ".int($id_warehouses)." ORDER BY Date DESC, Time DESC, ID_products_trans DESC LIMIT 1;";
        $log .= $sql."<br>\n";
        my $sth_qty = &Do_SQL($sql);
        ($left_qty, $left_qty_total) = $sth_qty->fetchrow_array();

    }
    $left_qty_total = 0 if(!$left_qty_total);
    $log .= "left_qty_total=".$left_qty_total."<br>\n";

    ### Formatea Type_trans si existe
    $type_trans = uc(&filter_values($type_trans));
    $log .= "type_trans=".$type_trans."<br>\n";
    
    my $sql_left_qty = "";
    if ( $type_trans eq 'IN' ){

        $left_qty += $quantity;
        $left_qty_total += $quantity if(($type ne 'Transfer Out' and $type ne 'Transfer In' and $type ne 'Transfer') or $tbl eq 'sl_skustransfers');

    }elsif ( $type_trans eq 'OUT' ){

        $left_qty -= $quantity if( $left_qty > 0 );
        $left_qty_total -= $quantity if( $left_qty_total > 0 and (($type ne 'Transfer Out' and $type ne 'Transfer In' and $type ne 'Transfer') or $tbl eq 'sl_skustransfers') );

    }else{

        if ( $type eq 'Purchase' or $type eq 'Return' or $type eq 'Transfer In' ){
            $type_trans = 'IN';
            $left_qty += $quantity;
            $left_qty_total += $quantity if(($type ne 'Transfer Out' and $type ne 'Transfer In' and $type ne 'Transfer') or $tbl eq 'sl_skustransfers');
        }elsif ( $type eq 'Return to Vendor' or $type eq 'Sale' or $type eq 'Transfer Out' ){
            $type_trans = 'OUT';
            $left_qty -= $quantity if( $left_qty > 0 );
            $left_qty_total -= $quantity if( $left_qty_total > 0 and (($type ne 'Transfer Out' and $type ne 'Transfer In' and $type ne 'Transfer') or $tbl eq 'sl_skustransfers') );
        }

    }
    $sql_left_qty = "left_quantity = ".int($left_qty).", ";

    my $sql_type_trans = ( $type_trans eq 'IN' or $type_trans eq 'OUT' ) ? " Type_trans = '$type_trans'," : "";
    $log .= "sql_type_trans=".$sql_type_trans."<br>\n";

    ####################################
    ### Costo Promedio
    ####################################
    if ($cfg{'acc_inventoryout_method_cost'} and lc($cfg{'acc_inventoryout_method_cost'}) eq 'average'){
        #my ($cost_avg, $total_cost_avg) = &get_average_cost($sku);
        # my $sql = "
        #         SELECT Cost_Avg
        #             , (cu_skus_trans.left_quantity_total * cu_skus_trans.Cost_Avg)AS total_cost_avg
        #             , Cost_Adj_Avg
        #             , (cu_skus_trans.left_quantity_total * cu_skus_trans.Cost_Adj_Avg)AS total_cost_adj_avg
        #         FROM cu_skus_trans
        #         WHERE cu_skus_trans.ID_products = ".$sku." 
        #         LOCK IN SHARE MODE;";
        # $log .= $sql."<br>\n";
        # my $qty_last =  &Do_SQL($sql);
        # my ($cost_avg, $total_cost_avg, $cost_adj_avg, $total_cost_adj_avg) = $qty_last->fetchrow_array();
        # $log .= qq|($cost_avg, $total_cost_avg, $cost_adj_avg, $total_cost_adj_avg) = get_average_cost($sku)|."<br>\n";

        if ($type_trans eq 'IN'){

            if( ($type ne 'Transfer Out' and $type ne 'Transfer In' and $type ne 'Transfer') or $tbl eq 'sl_skustransfers' ){
                ## Recalcular el Costo Promedio
                $total_cost = $quantity * $cost;
                $cost_avg  = ($total_cost + $total_cost_avg) / $left_qty_total;

                $log .= qq|total_cost[$total_cost] =$quantity * $cost|."<br>\n";
                $log .= qq|cost_avg[$cost_avg]=($total_cost + $total_cost_avg) / $left_qty_total|."<br>\n";

                ## Recalcular el Costo de Aterrizaje Promedio 
                $cost_adj_avg = 0 if( !$cost_adj_avg );
                $total_cost_adj_avg = 0 if( !$total_cost_adj_avg );

                my $total_cost_adj = $quantity * $cost_adj;
                $cost_adj_avg  = ($total_cost_adj + $total_cost_adj_avg) / $left_qty_total;

                $log .= qq|total_cost_adj[$total_cost_adj] = $quantity * $cost_adj|."<br>\n";
                $log .= qq|cost_adj_avg[$cost_adj_avg]=($total_cost_adj + $total_cost_adj_avg) / $left_qty_total|."<br>\n";
            }

            $add_sql .= ", Cost_Avg = '". $cost_avg ."', Cost_Adj_Avg = '".$cost_adj_avg."' ";

        }elsif ($type_trans eq 'OUT'){
            #$log .= qq|($cost_avg, $total_cost_avg) = get_average_cost($sku)|."<br>\n";
            ## Para salidas enviamos siempre el costo normal como promedio
            $add_sql .= ", Cost_Avg = '". $cost_avg ."', Cost_Adj_Avg = '".$cost_adj_avg."' ";
        }

        ### Inserta/Reemplaza en la tabla 
        #if( &table_exists('cu_skus_trans') and (($type ne 'Transfer Out' and $type ne 'Transfer In' and $type ne 'Transfer') or $tbl eq 'sl_skustransfers') ){
            my $sql_add_cus_info = ($id_customs_info and $id_customs_info ne '') ? ", ID_customs_info = '$id_customs_info'" : "";
            my $sql_ins = "INSERT INTO cu_skus_trans SET 
                                ID_products = ".$sku."
                                , ID_warehouses = '".$id_warehouses."'
                                , left_quantity = '".$left_qty."'
                                , left_quantity_total = '".$left_qty_total."'
                                , Cost_Avg = '".$cost_avg."'
                                , Cost = '".$cost."'
                                , Cost_Adj = '".$cost_adj."'
                                , Cost_Adj_Avg = '".$cost_adj_avg."'
                                , Cost_Add = '".$cost_add."'
                                $sql_add_cus_info 
                                , Date = CURDATE()
                                , Time = CURTIME()
                            ON DUPLICATE KEY UPDATE
                                left_quantity = '".$left_qty."'
                                , left_quantity_total = '".$left_qty_total."'
                                , Cost_Avg = '".$cost_avg."'
                                , Cost = '".$cost."'
                                , Cost_Adj = '".$cost_adj."'
                                , Cost_Adj_Avg = '".$cost_adj_avg."'
                                , Cost_Add = '".$cost_add."'
                                $sql_add_cus_info 
                                , Date = CURDATE()
                                , Time = CURTIME();";
            $log .= $sql_ins."<br>\n";
            &Do_SQL($sql_ins);
            ### Actualiza los costos y lef_qty_total en todos los registros del SKU
            my $sql_upd = "UPDATE cu_skus_trans SET 
                                left_quantity_total = '".$left_qty_total."'
                                , Cost_Avg = '".$cost_avg."'
                                , Cost = '".$cost."'
                                , Cost_Adj = '".$cost_adj."'
                                , Cost_Adj_Avg = '".$cost_adj_avg."'
                                , Cost_Add = '".$cost_add."'
                                $sql_add_cus_info
                            WHERE ID_products = '".$sku."';";
            $log .= $sql_upd."<br>\n";
            &Do_SQL($sql_upd);
        #}
    }

    ####################################
    ### Se insertan los datos generados
    ####################################
    $value = " ID_products = ".int($sku).", ID_warehouses = ".int($id_warehouses).", Location = '".&filter_values($location)."', Type = '".&filter_values($type)."', $sql_type_trans ID_trs = '".int($id_table)."', tbl_name = '".&filter_values($tbl)."', Quantity = ".int($quantity).", $sql_left_qty left_quantity_total = $left_qty_total, Cost = '". &filter_values($cost) ."', Cost_Adj = '". &filter_values($cost_adj) ."' $add_sql, Date = CURDATE(), Time = CURTIME(), ID_admin_users = '$usr{'id_admin_users'}';";
    $sql = "INSERT INTO sl_skus_trans SET $value";
    $log .= $sql."<br>\n";
    &Do_SQL($sql);

    if ($cfg{'debug_costo_promedio'} and $cfg{'debug_costo_promedio'} == 1){
        &Do_SQL("INSERT INTO sl_debug (cmd, id, log, Date, Time, ID_admin_users) VALUES ('sku_logging', '".int($id_table)."', '".&filter_values($log)."', CURDATE(), CURTIME(), '$usr{'id_admin_users'}');") if ($cfg{'acc_inventoryout_method_cost'} and lc($cfg{'acc_inventoryout_method_cost'}) eq 'average');
    }
}

#############################################################################
#############################################################################
#   Function: loc_logging
#
#       Es: Registra movimientos de sku entre gavetas
#       En: 
#
#
#    Created on: 2013-06-18
#
#    Author: _RB_
#
#    Modifications:
#
#
#   Parameters:
#
#      - $sku, $id_warehouses, $location, $type, $id_table, $tbl, $quantity, $cost
#      
#
#  Returns:
#
#      - None
#
#   See Also:
#
#      <view_mer_bills>
#
sub loc_logging {
#############################################################################
#############################################################################

    my ($id, $sku, $idw_from, $loc_from, $idw_to, $loc_to, $qty) = @_;
    (!$usr{'id_admin_users'}) and ($usr{'id_admin_users'} = 0);

    my ($sth);
    $value = " ID_manifests = '".int($id)."', ID_products = '".int($sku)."', ID_warehouses_From = '".$idw_from."', Location_From = '".&filter_values($loc_from)."', ID_warehouses_To = '".$idw_to."', Location_To = '".&filter_values($loc_to)."', Quantity = '".int($qty)."', Date = CURDATE(), Time = CURTIME(), ID_admin_users = '$usr{'id_admin_users'}'";

    &connect_db;
    $sth = &Do_SQL("INSERT INTO sl_locations_trans SET $value");
}


#############################################################################
#############################################################################
#   Function: move_inventory
#
#       Es: Mueve inventario entre almacenes
#       En: 
#
#
#    Created on: 2013-06-18
#
#    Author: _RB_
#
#    Modifications:
#
#
#   Parameters:
#
#      - $from_wh,$from_loc,$to_wh,$to_loc,$sku,$qty
#      
#
#  Returns:
#
#      - None
#
#   See Also:
#
#      <view_mer_bills>
#
sub move_inventory {
#############################################################################
#############################################################################
    my ($from_wh,$from_loc,$to_wh,$to_loc,$sku,$qty)= @_;


    #################################
    #################################
    ######
    ###### x) Comprobacion de Inventario
    ######
    #################################
    #################################
    my $tblname = 'transfer';
    my $mod1 = $from_loc ne '' ? " AND Location = '$from_loc' " : "";
    (!$to_loc) and ( $to_loc = &load_name('sl_locations', 'ID_warehouses', 'Code') );

    my ($sth) = &Do_SQL("SELECT IF(SUM(Quantity) IS NULL, 0, SUM(Quantity)) FROM sl_warehouses_location WHERE ID_warehouses = '$from_wh' AND ID_products = '$sku' $mod1 AND Quantity > 0;");
    my ($total) = $sth->fetchrow();
    my ($sth2) = &Do_SQL("SELECT IF(SUM(Quantity) IS NULL, 0, SUM(Quantity)) FROM sl_skus_cost LEFT JOIN sl_warehouses ON sl_skus_cost.ID_warehouses=sl_warehouses.ID_warehouses  WHERE ID_products='$sku' AND sl_skus_cost.ID_warehouses = '$from_wh'  AND Cost > 0");
    #my ($total2) = $sth2->fetchrow();
    my ($total2) = 1;
    if ($total < $qty or !$total2){

        return "error:$qty";

    }else{

        ### Habilitar cuando entre en operacion la opcion de transacciones
        #&Do_SQL("START TRANSACTION;");

        ### Metodo usado para la salida de inventario. FIFO: Primer entradas primeras salidas | LIFO: Ultimas entradas primeras salidas
        my $acc_method = $cfg{'acc_inventoryout_method'} ? $cfg{'acc_inventoryout_method'} : 'fifo';
        my $invout_order = $acc_method eq 'fifo' ? '' : 'DESC';

        ### Copy
        my $qty_derived = $qty;


        ####################################################
        ####################################################
        ####################################################
        ####################################################
        #################
        #################  WAREHOUSE LOCATION
        #################
        ####################################################
        ####################################################
        ####################################################
        ####################################################



        ###################################
        ################# FROM Warehouse Location
        ###################################
        do{

            my ($sth2) = &Do_SQL("SELECT ID_warehouses_location, Quantity FROM sl_warehouses_location WHERE ID_warehouses = '$from_wh' AND ID_products = '$sku' AND Location = '$from_loc' AND Quantity > 0 ORDER BY Date $invout_order, Time $invout_order;");
            my ($idwl,$this_qty) = $sth2->fetchrow();

            if($idwl){

                if($this_qty > $qty_derived){

                    my ($sth) = &Do_SQL("UPDATE sl_warehouses_location SET Quantity = Quantity - $qty WHERE ID_warehouses_location = '$idwl';");
                    &loc_logging(0,$sku,$from_wh,$from_loc,$to_wh,$to_loc,$qty);
                    $qty_derived = 0;

                }else{

                    my ($sth) = &Do_SQL("DELETE FROM sl_warehouses_location WHERE ID_warehouses_location = '$idwl';");
                    &loc_logging(0,$sku,$from_wh,$from_loc,$to_wh,$to_loc,$this_qty);
                    $qty_derived -= $this_qty;

                }

            }else{

                    ### Habilitar cuando entre en operacion la opcion de transacciones
                    #&Do_SQL("ROLLBACK");
                    #return ('ERROR', 'WL;;' . $sku . ';;' . $$from_wh .';;'. $from_loc);

            }


        } while ( $qty_derived > 0 );

        ###################################
        ################# TO Warehouse Location
        ###################################

        my ($sth) = &Do_SQL("SELECT ID_warehouses_location FROM sl_warehouses_location WHERE ID_warehouses = '$to_wh' AND ID_products = '$sku' AND Location = '$to_loc' ORDER BY Date $invout_order, Time $invout_order LIMIT 1;");
        my ($tidwl) = $sth->fetchrow();

        my $sthwl;
        if($tidwl) {
            $sthwl = &Do_SQL("UPDATE sl_warehouses_location SET Quantity = Quantity + $qty WHERE ID_warehouses_location='$tidwl';");
        }else{
            $sthwl = &Do_SQL("INSERT INTO sl_warehouses_location SET ID_warehouses = '$to_wh', ID_products = '$sku', Location = '$to_loc' , Quantity = '$qty', Date = CURDATE(), Time = CURTIME(), ID_admin_users = '$usr{'id_admin_users'}' ;");
        }
        my $t = $sthwl->rows();


        ####################################################
        ####################################################
        ####################################################
        ####################################################
        #################
        #################  SKUS COST
        #################
        ####################################################
        ####################################################
        ####################################################
        ####################################################

        if($from_wh ne $to_wh) {

            ### Copy
            my $qty_derived = $qty;

            ###################################
            ################# FROM Skus Cost
            ###################################
            my $qty_to = $qty;
            my $fcost = 0;

            do {

                my ($sth) = &Do_SQL("SELECT ID_skus_cost, Quantity, Cost FROM sl_skus_cost WHERE ID_warehouses = '$from_wh' AND ID_products = '$sku' AND Quantity > 0 ORDER BY Date $invout_order, Time $invout_order LIMIT 1;");
                my ($idsc, $this_qty, $cost) = $sth->fetchrow();
               
                if($idsc) {

                    if($this_qty > $qty_derived) {

                        my ($sth) = &Do_SQL("UPDATE sl_skus_cost SET Quantity = Quantity - $qty_derived WHERE ID_skus_cost='$idsc';");

                        ###################################
                        ################# TO Skus Cost
                        ###################################

                        my ($sth) = &Do_SQL("SELECT ID_skus_cost FROM sl_skus_cost WHERE ID_warehouses = '$to_wh' AND ID_products = '$sku' AND Cost = '$cost' ORDER BY Date $invout_order, Time $invout_order LIMIT 1;");
                        my ($tidsc2) = $sth->fetchrow();

                        if($tidsc2) {
                            $sthsc = &Do_SQL("UPDATE sl_skus_cost SET Quantity = Quantity + $qty_derived WHERE ID_skus_cost = '$tidsc2' ;");
                        }else{
                            $sthsc = &Do_SQL("INSERT INTO sl_skus_cost SET ID_warehouses = '$to_wh', ID_products = '$sku', ID_purchaseorders = '$in{'id_manifests'}' , Tblname = '$tblname', Quantity = '$qty', Cost = '$cost', Date = CURDATE(), Time = CURTIME(), ID_admin_users = '$usr{'id_admin_users'}' ;");
                        }
                        
                        $qty_derived = 0;
                        $t2 += $sthsc->rows();

                    }else{
                       
                        my ($sth) = &Do_SQL("DELETE FROM sl_skus_cost WHERE ID_skus_cost = '$idsc';");
                        $qty_derived -= $this_qty;

                        ###################################
                        ################# TO Skus Cost
                        ###################################

                        my ($sth) = &Do_SQL("SELECT ID_skus_cost FROM sl_skus_cost WHERE ID_warehouses = '$to_wh' AND ID_products = '$sku' AND Cost = 'Cost' ORDER BY Date $invout_order, Time $invout_order LIMIT 1;");
                        my ($tidsc2) = $sth->fetchrow();

                        if($tidsc2) {
                            $sthsc = &Do_SQL("UPDATE sl_skus_cost SET Quantity = Quantity + $this_qty WHERE ID_skus_cost = '$tidsc2' ;");
                        }else{
                            $sthsc = &Do_SQL("INSERT INTO sl_skus_cost SET ID_warehouses = '$to_wh', ID_products = '$sku', ID_purchaseorders = '$in{'id_manifests'}' , Tblname = '$tblname', Quantity = '$this_qty', Cost = '$cost', Date = CURDATE(), Time = CURTIME(), ID_admin_users = '$usr{'id_admin_users'}' ;");
                        }
                        $t2 += $sthsc->rows();

                    }


                }else{
                    
                    my $cost_adj = 0;
                    ($cost, $cost_adj) = &load_sltvcost($sku);
                    
                    ###################################
                    ################# TO Skus Cost
                    ###################################

                    my ($sth) = &Do_SQL("SELECT ID_skus_cost FROM sl_skus_cost WHERE ID_warehouses = '$to_wh' AND ID_products = '$sku' AND Cost = '$cost' ORDER BY Date $invout_order, Time $invout_order LIMIT 1;");
                    my ($tidsc2) = $sth->fetchrow();

                    if($tidwl) {
                        $sthsc = &Do_SQL("UPDATE sl_skus_cost SET Quantity = Quantity + $qty_derived WHERE ID_skus_cost = '$tidsc2' ;");
                    }else{
                        $sthsc = &Do_SQL("INSERT INTO sl_skus_cost SET ID_warehouses = '$to_wh', ID_products = '$sku', ID_purchaseorders = 0 , Tblname = '$tblname', Quantity = '$qty_derived', Cost='$cost', Cost_Adj='$cost_adj' Date = CURDATE(), Time = CURTIME(), ID_admin_users = '$usr{'id_admin_users'}' ;");
                    }

                    $qty_derived = 0;
                    $t2 += $sthsc->rows();

                    ### Habilitar cuando entre en operacion la opcion de transacciones
                    ### Y deshabilitar todo lo de esta seccion arriba
                    #&Do_SQL("ROLLBACK");
                    #return ('ERROR', 'SC;;' . $sku . ';;' . $from_wh .';;'. $from_loc);

                }

            } while ( $qty_derived > 0 );

        }

        my ($sth) = &Do_SQL("SELECT ID_locations FROM sl_locations WHERE ID_warehouses = '$from_wh' AND Code = '$from_loc';");
        my ($idlf) = $sth->fetchrow();
        my ($sth) = &Do_SQL("SELECT ID_locations FROM sl_locations WHERE ID_warehouses = '$to_wh' AND Code = '$to_loc';");
        my ($idlt) = $sth->fetchrow();

        my ($pname) = &load_name('sl_parts', 'ID_parts', $sku-400000000, 'Name');
        my ($whname) = &load_name('sl_warehouses', 'ID_warehouses', $to_wh, 'Name');
        my ($whnamef) = &load_name('sl_warehouses', 'ID_warehouses', $from_wh, 'Name');

        my ($sth) = &Do_SQL("INSERT INTO sl_locations_notes SET ID_locations = '$idlf', Notes = 'Transfer $qty items of ($sku) ". &filter_values($pname) ." to -> ($to_wh) ". &filter_values($whname) ." / $to_loc', Type = 'Low', Date = CURDATE(), Time = CURTIME(), ID_admin_users = '$usr{'id_admin_users'}' ;");
        my ($sth) = &Do_SQL("INSERT INTO sl_locations_notes SET ID_locations = '$idlt', Notes = 'Received $qty items of ($sku) ". &filter_values($pname) ." from -> ($from_wh) ". &filter_values($whnamef) ." / $from_loc', Type = 'Low', Date = CURDATE(), Time = CURTIME(), ID_admin_users = '$usr{'id_admin_users'}' ;");

        ### Habilitar cuando entre en operacion la opcion de transacciones
        #&Do_SQL("COMMIT");
        return ("ok", "ok");

    }

}

sub check_pack_loc {
# --------------------------------------------------------
    my ($id_wh) = @_;
    if ($id_wh>0){
        my ($sth) = &Do_SQL("SELECT COUNT(*) FROM sl_locations WHERE ID_warehouses='$id_wh' AND Code='PACK'");
        if ($sth->fetchrow eq 0){
            my ($sth) = &Do_SQL("INSERT INTO sl_locations SET ID_warehouses='$id_wh', Code='PACK', UPC='temp_upc', Status='Active', Date=CURDATE(), Time=CURTIME(), ID_admin_users='1'");
            my ($sth) = &Do_SQL("UPDATE sl_locations SET UPC=CONCAT('PACK',ID_locations) WHERE ID_warehouses='$id_wh' AND Code='PACK' AND UPC='temp_upc' AND Status='Active'");
        }
    }
}

#############################################################################
#############################################################################
#   Function: default_warehouses_location
#
#       Es: Get default location in warehouses
#       En: 
#
#
#    Created on: 2015-02-25
#
#    Author: ISC Alejandro Diaz
#
#    Modifications:
#
#
#
#   Parameters:
#
#      - $id_warehouses, $id_products
#      
#
#  Returns:
#
#      - None
#
#   See Also:
#
#
sub default_warehouses_location {
#############################################################################
#############################################################################
    my ($id_warehouses, $id_products) = @_;
    my ($location);
    if ($id_warehouses) {
        $add_sql = ($id_products)? " AND sl_warehouses_location.ID_products = '$id_products' ":"";

        $sql ="SELECT DISTINCT sl_warehouses_location.Location, sl_locations.ID_locations
        FROM sl_warehouses_location
        INNER JOIN sl_locations ON sl_warehouses_location.Location=sl_locations.Code AND sl_warehouses_location.ID_warehouses=sl_locations.ID_warehouses
        WHERE sl_locations.Status='Active'    
        AND sl_warehouses_location.ID_warehouses = '$id_warehouses'
        AND sl_warehouses_location.Quantity >= 0
        $add_sql
        ORDER BY sl_locations.ID_locations
        LIMIT 1;";
        my ($sth) = &Do_SQL($sql);
        my $rec = $sth->fetchrow_hashref();

        if (!$rec->{'Location'}){
            $sql ="SELECT sl_locations.ID_locations, sl_locations.Code AS Location
            FROM sl_locations
            WHERE sl_locations.Status='Active'    
            AND sl_locations.ID_warehouses = '$id_warehouses'
            ORDER BY sl_locations.ID_locations
            LIMIT 1;";
            $sth = &Do_SQL($sql);
            $rec = $sth->fetchrow_hashref();
            $location = $rec->{'Location'};
        }else{
            $location = $rec->{'Location'};
        }
    }

    return $location;
}

#############################################################################
#############################################################################
#   Function: warehouse_transfers
#
#       Es: Realiza transferencias entre almacenes y gavetas
#       En: Make transfers between warehouses and locations
#
#
#    Created on: 2015-02-26
#
#    Author: ISC Alejandro Diaz
#
#    Modifications:
#
#
#   Parameters:
#
#       - from_warehouse: Origin Warehous
#       - from_location: Origin Location
#       - to_location: Target Location
#       - id_products: SKU to transfer
#       - quantity: Quantity to transfer
#       - optional: $tracking, $shpdate, $trktype, $id_orders_products
#
#  Returns:
#
#      - OK if sucess
#      - ERROR if fail
#
#   See Also:
#
#      >>> MUY IMPORTANTE >>> SI SE MODIFICA DEBES MODIFICAR LA FUNCION EN HANDHELD main.functions.pl 
#      >>> MUY IMPORTANTE >>> SI SE MODIFICA DEBES MODIFICAR LA FUNCION EN cgi-bin\mod\admin.fin2.cgi
#
sub warehouse_transfers {
#############################################################################
#############################################################################
    my ($from_warehouse, $from_location, $to_warehouse, $to_location, $id_products, $quantity, $transaction_id, $transaction_table, $tracking, $shpdate, $trktype, $id_orders_products) = @_;
    
    # Warehouse Origin Validation
    if ($from_warehouse){
        $sql = "SELECT COUNT(*) FROM sl_warehouses WHERE ID_warehouses=$from_warehouse AND Status='Active';";
        $log .= $sql."<br>\n\n";
        my ($sth) = &Do_SQL($sql);
        my $is_valid = $sth->fetchrow_array();
        
        if (!$is_valid){
            return ("ERROR", "Warehouse Origin Invalid $from_warehouse");
        }
    }

    # Location Origin Validation
    if ($from_location){
        $add_sql = ($from_warehouse)? " AND ID_warehouses='$from_warehouse' ":"";
        $sql = "SELECT COUNT(*) FROM sl_locations WHERE 1 $add_sql AND Code='$from_location' AND Status='Active';";
        $log .= $sql."<br>\n\n";
        my ($sth) = &Do_SQL($sql);
        my $is_valid = $sth->fetchrow_array();
        
        if (!$is_valid){
            return ("ERROR", "Location Origin Invalid $from_location");
        }
    }

    # Warehouse Target Validation
    if ($to_warehouse){
        $sql = "SELECT COUNT(*) FROM sl_warehouses WHERE ID_warehouses=$to_warehouse AND Status='Active';";
        $log .= $sql."<br>\n\n";
        my ($sth) = &Do_SQL($sql);
        my $is_valid = $sth->fetchrow_array();
        
        if (!$is_valid){
            return ("ERROR", "Warehouse Target Invalid $to_warehouse");
        }
    }

    # Location Target Validation
    if ($to_location){
        $add_sql = ($to_warehouse)? " AND ID_warehouses=$to_warehouse ":"";
        $sql = "SELECT COUNT(*) FROM sl_locations WHERE 1 $add_sql AND Code='$to_location' AND Status='Active';";
        $log .= $sql."<br>\n\n";
        my ($sth) = &Do_SQL($sql);
        my $is_valid = $sth->fetchrow_array();
        
        if (!$is_valid){
            return ("ERROR", "Location Target Invalid $to_location");
        }
    }

    my $acc_method = $cfg{'acc_inventoryout_method'} ? $cfg{'acc_inventoryout_method'} : 'fifo';
    my $invout_order = $acc_method eq 'fifo' ? '' : 'DESC';

    my $add_sql = ($from_location)? " AND UPPER(sl_warehouses_location.Location) = UPPER('$from_location') ":"";
    my $pname = &load_name('sl_parts','ID_parts',($id_products - 400000000),'Name');

    if (!$to_location and $to_warehouse){
        $to_location = &default_warehouses_location($to_warehouse, $id_products);
    }

    if (!$to_warehouse and $to_location){
        $to_warehouse = &load_name('sl_warehouses_location', 'Location', $to_location, 'ID_warehouses');
    }

    my $log = "DEBUG: warehouse_transfers <br>\n\n";
    $log .= "from_warehouse=$from_warehouse <br>\n";
    $log .= "from_location=$from_location <br>\n";
    $log .= "to_warehouse=$to_warehouse <br>\n";
    $log .= "to_location=$to_location <br>\n";
    $log .= "id_products=$id_products <br>\n";
    $log .= "quantity=$quantity <br>\n";
    $log .= "transaction_id=$transaction_id <br>\n";
    $log .= "transaction_table=$transaction_table <br>\n";
    $log .= "id_orders_products=$id_orders_products <br>\n";
    $log .= "trktype=$trktype <br>\n";
    $log .= "shpdate=$shpdate <br>\n";
    $log .= "tracking=$tracking <br>\n\n";
    
    $log .= "acc_inventoryout_method=$acc_method <br>\n";
    $log .= "invout_order=$invout_order <br>\n\n";

    #########################################
    ### Validation
    #########################################
    if (!$from_warehouse){
        return ("ERROR", "Warehouses Origin Invalid");
    }
    
    if (!$to_warehouse){
        return ("ERROR", "Warehouses Target Invalid");
    }

    if (!$to_location){
        return ("ERROR", "Warehouses Location Target Invalid");
    }

    if (!$quantity or $quantity < 1){
        return ("ERROR", "Quantity Invalid");
    }
    

    #########################################
    ### sl_warehouses_location - Salida 
    #########################################
    $diff_wh = $quantity;
    $sql = "SELECT 
                sl_warehouses_location.ID_warehouses_location
                , sl_warehouses_location.Location
                , sl_warehouses_location.Quantity 
                , sl_locations.ID_locations
                , sl_warehouses_location.ID_customs_info
            FROM sl_warehouses_location
                INNER JOIN sl_locations ON sl_warehouses_location.Location=sl_locations.Code AND sl_warehouses_location.ID_warehouses=sl_locations.ID_warehouses
                INNER JOIN sl_warehouses ON sl_warehouses.ID_warehouses=sl_locations.ID_warehouses
            WHERE sl_warehouses_location.ID_warehouses = $from_warehouse $add_sql
                AND sl_warehouses_location.ID_products = $id_products 
                AND sl_warehouses_location.Quantity > 0 
                AND sl_locations.Status='Active'
                AND sl_warehouses.Status='Active'
            ORDER BY sl_warehouses_location.Date $invout_order, sl_warehouses_location.Time $invout_order 
            ;";
    $log .= $sql."<br>\n\n";
    my ($sth2) = &Do_SQL($sql);
    $cont = 0;
    while (my $rec = $sth2->fetchrow_hashref){
        if ($diff_wh > 0){
            my $qty_processed=0;

            if ($rec->{'Quantity'} > $diff_wh){
                $sql = "UPDATE sl_warehouses_location SET Quantity = Quantity - $diff_wh WHERE ID_warehouses_location = $rec->{'ID_warehouses_location'} LIMIT 1;";
                $log .= $sql."<br>\n\n";
                &Do_SQL($sql);
                $qty_processed = $rec->{'Quantity'} - ($rec->{'Quantity'} - $diff_wh);
            }else{
                $sql = "DELETE FROM sl_warehouses_location WHERE ID_warehouses_location = $rec->{'ID_warehouses_location'} LIMIT 1;";
                $log .= $sql."<br>\n\n";
                &Do_SQL($sql);
                $qty_processed = $rec->{'Quantity'};
            }

            ######################################################
            ### sl_warehouses_location - Entrada 
            ######################################################
            my $add_sql_custom_info='';
            $add_sql_custom_info .= ($rec->{'ID_customs_info'} and $rec->{'ID_customs_info'} ne '')? ", ID_customs_info='$rec->{'ID_customs_info'}' ":"";

            $sql = "SELECT sl_locations.ID_locations FROM sl_locations WHERE UPPER(sl_locations.Code)=UPPER('$to_location') AND sl_locations.ID_warehouses=$to_warehouse;";
            $log .= $sql."<br>\n\n";
            my $sth = &Do_SQL($sql);

            $id_locations = $sth->fetchrow_array();

            ### Se valida si ya existe un registro en sl_warehouses_location
            my $sel_sql_custom_info = (!$rec->{'ID_customs_info'}) ? "AND ID_customs_info IS NULL" : "AND ID_customs_info = $rec->{'ID_customs_info'}";
            $sql = "SELECT ID_warehouses_location FROM sl_warehouses_location WHERE ID_warehouses = $to_warehouse AND ID_products = $id_products AND Location = '$to_location' $sel_sql_custom_info ORDER BY Date DESC LIMIT 1;";
            my $sth_exist = &Do_SQL($sql);
            my $id_wl = $sth_exist->fetchrow();
            if( int($id_wl) > 0 ){
                $sql = "UPDATE sl_warehouses_location SET Quantity = Quantity + $qty_processed WHERE ID_warehouses_location = $id_wl;";
            }else{
                $sql = "INSERT INTO sl_warehouses_location SET ID_warehouses = '$to_warehouse', ID_products = $id_products, Location = '$to_location' , Quantity = $qty_processed $add_sql_custom_info , Date = CURDATE(), Time = CURTIME(), ID_admin_users = $usr{'id_admin_users'} ;";
            }
            $log .= $sql."<br>\n\n";
            &Do_SQL($sql);

            $sql = "INSERT INTO sl_locations_notes SET ID_locations = '$id_locations', Notes = 'Type: Transfer In\nItem: ($id_products) ". &filter_values($pname) ."\nQuantity: $qty_processed', Type = 'Low', Date = CURDATE(), Time = CURTIME(), ID_admin_users = $usr{'id_admin_users'};";
            $log .= $sql."<br>\n\n";
            &Do_SQL($sql);

            $diff_wh -= $rec->{'Quantity'};

            my ($id_manifests) = ($transaction_table eq 'sl_manifests' and $transaction_id)? $transaction_id : 0 ;
            &loc_logging($id_manifests, $id_products, $from_warehouse, $rec->{'Location'}, $to_warehouse , $to_location, $qty_processed);
            $log .= qq|loc_logging($id_manifests, $id_products, $from_warehouse, $rec->{'Location'}, $to_warehouse , $to_location, $qty_processed)|."<br>\n\n";

            $sql = "INSERT INTO sl_locations_notes SET ID_locations = $rec->{'ID_locations'}, Notes = 'Type: Transfer Out\nItem: ($id_products) ". &filter_values($pname) ."\nQuantity: $qty_processed', Type = 'Low', Date = CURDATE(), Time = CURTIME(), ID_admin_users = $usr{'id_admin_users'};";
            $log .= $sql."<br>\n\n";
            &Do_SQL($sql);

            $diff_cost = $qty_processed;

            ###########################
            ### sl_skus_cost - Salida 
            ###########################
            $sql = "SELECT 
                        ID_skus_cost, Quantity, Cost, Cost_Adj, Cost_Add
                    FROM sl_skus_cost
                    WHERE ID_warehouses = $from_warehouse 
                        AND ID_products = $id_products 
                        AND Quantity > 0 
                        AND Cost > 0 
                    ORDER BY Date $invout_order, Time $invout_order 
                    ;";
            $log .= $sql."<br>\n\n";
            my ($sth3) = &Do_SQL($sql);
            while (my $rec_cost = $sth3->fetchrow_hashref){

                if ($diff_cost > 0){

                    ###########################
                    ### Costo Promedio
                    ###########################
                    if ($cfg{'acc_inventoryout_method_cost'} and lc($cfg{'acc_inventoryout_method_cost'}) eq 'average'){
                        my ($cost_avg, $total_cost_avg, $id_custom_info, $cost_adj, $cost_add) = &get_average_cost($id_products);
                        
                        if ($cost_avg <= 0) {
                        
                            return ("ERROR", "AVG Cost Not Found");
                            
                        }

                        $rec_cost->{'Cost'} = $cost_avg;
                        $rec_cost->{'Cost_Adj'} = $cost_adj;
                        $rec_cost->{'Cost_Add'} = $cost_add;
                        $rec->{'ID_customs_info'} = $id_custom_info;
                        
                        $log .= "cost_avg=".$cost_avg."<br>\n";
                        $log .= "cost_adj=".$cost_adj."<br>\n";
                        $log .= "cost_add=".$cost_add."<br>\n";
                        $log .= "id_custom_info=".$id_custom_info."<br>\n";
                        $log .= "total_cost_avg=".$total_cost_avg."<br>\n";
                    }

                    $pcost += $rec_cost->{'Cost'};
                    $qty_processed = 0;
                    $log .= "pcost=".$pcost."<br>\n\n";
                    $log .= "qty_processed=".$qty_processed."<br>\n\n";

                    if ($rec_cost->{'Quantity'} > $diff_cost){
                        $sql = "UPDATE sl_skus_cost SET Quantity = Quantity - $diff_cost WHERE ID_skus_cost = $rec_cost->{'ID_skus_cost'} LIMIT 1;";
                        $log .= $sql."<br>\n\n";
                        &Do_SQL($sql) if ($from_warehouse ne $to_warehouse);
                        $qty_processed = $rec_cost->{'Quantity'} - ($rec_cost->{'Quantity'} - $diff_cost);
                        $log .= "qty_processed=$rec_cost->{'Quantity'} - ($rec_cost->{'Quantity'} - $diff_cost)<br>\n\n";
                    }else{
                        $sql = "DELETE FROM sl_skus_cost WHERE ID_skus_cost = $rec_cost->{'ID_skus_cost'} LIMIT 1;";
                        $log .= $sql."<br>\n\n";
                        &Do_SQL($sql) if ($from_warehouse ne $to_warehouse);
                        $qty_processed = $rec_cost->{'Quantity'};
                        $log .= "qty_processed=".$rec_cost->{'Quantity'}."<br>\n\n";
                    }
                    $diff_cost -= $rec_cost->{'Quantity'};
                    $log .= "diff_cost=".$diff_cost."<br>\n\n";

                    ###########################
                    ### sl_orders_parts
                    ###########################
                    if ($id_orders_products){

                        $sql = "insert into sl_orders_parts (Tracking, Cost, Cost_Adj, Cost_Add, ShpDate, ShpProvider, ID_orders_products, ID_parts, Status, Quantity, Date, Time, ID_admin_users) values ";
                        @id_orders_p = split(/,/, $id_orders_products);
                        for my $el (@id_orders_p){
                            $sql.=" ('$tracking', $rec_cost->{'Cost'}, $rec_cost->{'Cost_Adj'}, $rec_cost->{'Cost_Add'}, '$shpdate', '$trktype', $el, ($id_products - 400000000), 'Shipped', 1, curdate(), curtime(), $usr{'id_admin_users'}),";
                        }
                        chop($sql);
                        # $sql = "INSERT INTO sl_orders_parts SET Tracking='$tracking', Cost=$rec_cost->{'Cost'}, Cost_Adj=$rec_cost->{'Cost_Adj'}, Cost_Add=$rec_cost->{'Cost_Add'}, ShpDate='$shpdate', ShpProvider='$trktype', ID_orders_products=$id_orders_products, ID_parts=($id_products - 400000000), Status='Shipped', Quantity=$qty_processed, Date=CURDATE(), Time=CURTIME(), ID_admin_users=$usr{'id_admin_users'};";
                        $log .= $sql."<br>\n\n";
                        &Do_SQL($sql);

                        $id_orders_products = 0;
                    }
                    
                    ###########################
                    ### sl_skus_trans
                    ###########################
                    &sku_logging($id_products, $from_warehouse, $rec->{'Location'}, 'Transfer Out', $transaction_id, $transaction_table, $qty_processed, $rec_cost->{'Cost'}, $rec_cost->{'Cost_Adj'}, "OUT", $rec->{'ID_customs_info'}, $rec_cost->{'Cost_Add'});
                    $log .= qq|sku_logging($id_products, $from_warehouse, $rec->{'Location'}, 'Transfer Out', $transaction_id, $transaction_table, $qty_processed, $rec_cost->{'Cost'}, $rec_cost->{'Cost_Adj'}, "OUT", $rec->{'ID_customs_info'}, $rec_cost->{'Cost_Add'})|."<br>\n\n";

                    ###########################
                    ### sl_skus_cost - Entrada 
                    ###########################
                    $sql = "SELECT 
                                ID_skus_cost, Quantity, Cost, Cost_Adj, Cost_Add
                            FROM sl_skus_cost
                            WHERE ID_warehouses = $to_warehouse 
                                AND ID_products = $id_products 
                                AND Quantity >= 0 
                                AND Cost =$rec_cost->{'Cost'}
                                AND Cost_Adj =$rec_cost->{'Cost_Adj'}
                            ORDER BY Date $invout_order, Time $invout_order                             
                            LIMIT 1 
                            ;";
                    $log .= $sql."<br>\n\n";
                    $sth = &Do_SQL($sql);
                    my $rec_cost_to = $sth->fetchrow_hashref();
                    if ($rec_cost_to->{'ID_skus_cost'}){
                        
                        $sql = "UPDATE sl_skus_cost SET Quantity = Quantity + $qty_processed WHERE ID_skus_cost = $rec_cost_to->{'ID_skus_cost'} LIMIT 1;";
                        $log .= $sql."<br>\n\n";
                        &Do_SQL($sql) if ($from_warehouse ne $to_warehouse);

                    }else{
                        
                        $sql = "INSERT INTO sl_skus_cost SET ID_products=$id_products, ID_warehouses=$to_warehouse, Tblname='transfer', Quantity=$qty_processed, Cost=$rec_cost->{'Cost'}, Cost_Adj=$rec_cost->{'Cost_Adj'}, Date = CURDATE(), Time = CURTIME(), ID_admin_users = $usr{'id_admin_users'};";
                        $log .= $sql."<br>\n\n";
                        &Do_SQL($sql) if ($from_warehouse ne $to_warehouse);

                    }

                    ###########################
                    ### sl_skus_trans
                    ###########################
                    &sku_logging($id_products, $to_warehouse, $to_location, 'Transfer In', $transaction_id, $transaction_table, $qty_processed, $rec_cost->{'Cost'}, $rec_cost->{'Cost_Adj'}, "IN", $rec->{'ID_customs_info'}, $rec_cost->{'Cost_Add'});
                    $log .= qq|sku_logging($id_products, $to_warehouse, $to_location, 'Transfer In', $transaction_id, $transaction_table, $qty_processed, $rec_cost->{'Cost'}, $rec_cost->{'Cost_Adj'}, "IN", $rec->{'ID_customs_info'}, $rec_cost->{'Cost_Add'})|."<br>\n\n";

                }else{
                    last;
                }
            }            
        }else{
            last;
        }

    }

    if ($cfg{'debug_costo_promedio'} and $cfg{'debug_costo_promedio'} == 1){
        &Do_SQL("INSERT INTO sl_debug (cmd, id, log, Date, Time, ID_admin_users) VALUES ('warehouse_transfers', '$transaction_id', '".&filter_values($log)."', CURDATE(), CURTIME(), '$usr{'id_admin_users'}');") if ($cfg{'acc_inventoryout_method_cost'} and lc($cfg{'acc_inventoryout_method_cost'}) eq 'average');
    }

    if ($diff_wh > 0 or $diff_cost > 0){
        
        $log .= "diff_wh=".$diff_wh."<br>\n\n";
        $log .= "diff_cost=".$diff_cost."<br>\n\n";

        return ("ERROR", "$from_warehouse->$id_products ".($quantity - $diff_wh)."<$quantity");

    }

    return ("ok","ok");

}

#############################################################################
#############################################################################
#   Function: set_wlocation_grouped
#
#       Es: Agrupa registros de inventario
#       En: 
#
#
#    Created on: 2015-07-27
#
#    Author: _RB_
#
#    Modifications:
#
#
#
#   Parameters:
#
#      - $id_warehouses, $location, $id_products
#      
#
#  Returns:
#
#      - None
#
#   See Also:
#
#
sub set_wlocation_grouped {
#############################################################################
#############################################################################

    my ($id_warehouses, $location, $id_products) = @_;

    return if (!$id_warehouses or !$location or !$id_products);

    ### Metodo usado para la salida de inventario. FIFO: Primer entradas primeras salidas | LIFO: Ultimas entradas primeras salidas
    my $acc_method = $cfg{'acc_inventoryout_method'} ? $cfg{'acc_inventoryout_method'} : 'fifo';
    my $invout_order = $acc_method eq 'fifo' ? '' : 'DESC';


    my ($sth) = &Do_SQL("SELECT ID_warehouses_location, Quantity FROM sl_warehouses_location WHERE ID_warehouses = '". int($id_warehouses) ."' AND ID_products = '". int($id_products)."' AND Location = '". &filter_values($location)."' ORDER BY Date $invout_order;");
    my ($tlines) = $sth->rows();

    if($tlines > 1){

        my $idwl_base = 0;
        while(my ($idwl,$this_qty) = $sth->fetchrow()){

            if($idwl_base){

                ####
                #### Sumamos la cantidad al registro principal y la deducimos del actual
                ####
                &Do_SQL("UPDATE sl_warehouses_location SET Quantity = Quantity + $this_qty WHERE ID_warehouses_location = '$idwl_base';");
                &Do_SQL("DELETE FROM sl_warehouses_location WHERE ID_warehouses_location = '$idwl';");               

            } 

            $idwl_base = $idwl if !$idwl_base;

        }

    }

    return;
}

#############################################################################
#############################################################################
#   Function: warehouse_skutransfers
#
#       Es: Realiza transferencias entre almacenes y gavetas de un SKU para suplantar a otro
#       En: Make transfers between warehouses and locations
#
#
#    Created on: 2015-08-25
#
#    Author: ISC Alejandro Diaz
#
#    Modifications:
#       - Last Time Modification by _RB_ on 2015/11/23: Se busca registro para $id_products_new en la entrada de wlocation y el if que hace update/insert de sl_skus_cost se agrega tambien si el producto de entrada es diferente al de salida
#
#
#   Parameters:
#
#       - from_warehouse: Origin Warehous
#       - from_location: Origin Location
#       - to_location: Target Location
#       - id_products: SKU to transfer
#       - id_products_new: New SKU
#       - quantity: Quantity to transfer
#       - optional: $tracking, $shpdate, $trktype, $id_orders_products
#
#  Returns:
#
#      - OK if sucess
#      - ERROR if fail
#
#   See Also:
#
#      >>> MUY IMPORTANTE >>> SI SE MODIFICA DEBES MODIFICAR LA FUNCION EN HANDHELD main.functions.pl 
#      >>> MUY IMPORTANTE >>> SI SE MODIFICA DEBES MODIFICAR LA FUNCION EN cgi-bin\mod\admin.fin2.cgi
#
sub warehouse_skutransfers {
#############################################################################
#############################################################################
    my ($from_warehouse, $from_location, $to_warehouse, $to_location, $id_products, $quantity, $id_products_new, $transaction_id) = @_;
    my ($transaction_table) = 'sl_skustransfers';

    # Warehouse Origin Validation
    if ($from_warehouse){
        $sql = "SELECT COUNT(*) FROM sl_warehouses WHERE ID_warehouses=$from_warehouse AND Status='Active';";
        $log .= $sql."<br>\n\n";
        my ($sth) = &Do_SQL($sql);
        my $is_valid = $sth->fetchrow_array();
        
        if (!$is_valid){
            return ("ERROR", "Warehouse Origin Invalid $from_warehouse");
        }
    }

    # Location Origin Validation
    if ($from_location){
        $add_sql = ($from_warehouse)? " AND ID_warehouses=$from_warehouse ":"";
        $sql = "SELECT COUNT(*) FROM sl_locations WHERE 1 $add_sql AND Code='$from_location' AND Status='Active';";
        $log .= $sql."<br>\n\n";
        my ($sth) = &Do_SQL($sql);
        my $is_valid = $sth->fetchrow_array();
        
        if (!$is_valid){
            return ("ERROR", "Location Origin Invalid $from_location");
        }
    }

    # Warehouse Target Validation
    if ($to_warehouse){
        $sql = "SELECT COUNT(*) FROM sl_warehouses WHERE ID_warehouses=$to_warehouse AND Status='Active';";
        $log .= $sql."<br>\n\n";
        my ($sth) = &Do_SQL($sql);
        my $is_valid = $sth->fetchrow_array();
        
        if (!$is_valid){
            return ("ERROR", "Warehouse Target Invalid $to_warehouse");
        }
    }

    # Location Target Validation
    if ($to_location){
        $add_sql = ($to_warehouse)? " AND ID_warehouses=$to_warehouse ":"";
        $sql = "SELECT COUNT(*) FROM sl_locations WHERE 1 $add_sql AND Code='$to_location' AND Status='Active';";
        $log .= $sql."<br>\n\n";
        my ($sth) = &Do_SQL($sql);
        my $is_valid = $sth->fetchrow_array();
        
        if (!$is_valid){
            return ("ERROR", "Location Target Invalid $to_location");
        }
    }

    my $acc_method = $cfg{'acc_inventoryout_method'} ? $cfg{'acc_inventoryout_method'} : 'fifo';
    my $invout_order = $acc_method eq 'fifo' ? '' : 'DESC';

    my $add_sql = ($from_location)? " AND UPPER(sl_warehouses_location.Location) = UPPER('$from_location') ":"";
    my $pname = &load_name('sl_parts','ID_parts',($id_products - 400000000),'Name');

    if (!$to_location and $to_warehouse){
        $to_location = &default_warehouses_location($to_warehouse, $id_products);
    }

    if (!$to_warehouse and $to_location){
        $to_warehouse = &load_name('sl_warehouses_location', 'Location', $to_location, 'ID_warehouses');
    }

    my $log = "DEBUG: warehouse_transfers <br>\n\n";
    $log .= "from_warehouse=$from_warehouse <br>\n";
    $log .= "from_location=$from_location <br>\n";
    $log .= "to_warehouse=$to_warehouse <br>\n";
    $log .= "to_location=$to_location <br>\n";
    $log .= "id_products=$id_products <br>\n";
    $log .= "id_products_new=$id_products_new <br>\n";
    $log .= "quantity=$quantity <br>\n";
    $log .= "transaction_id=$transaction_id <br>\n";
    $log .= "transaction_table=$transaction_table <br>\n";
    
    $log .= "acc_inventoryout_method=$acc_method <br>\n";
    $log .= "invout_order=$invout_order <br>\n\n";

    #########################################
    ### Validation
    #########################################
    if (!$from_warehouse){
        return ("ERROR", "Warehouses Origin Invalid");
    }
    
    if (!$to_warehouse){
        return ("ERROR", "Warehouses Target Invalid");
    }

    if (!$to_location){
        return ("ERROR", "Warehouses Location Target Invalid");
    }

    if (!$quantity or $quantity < 1){
        return ("ERROR", "Quantity Invalid");
    }

    #########################################
    ### sl_warehouses_location - Salida 
    #########################################
    $diff_wh = $quantity;
    $sql = "SELECT 
                sl_warehouses_location.ID_warehouses_location
                , sl_warehouses_location.Location
                , sl_warehouses_location.Quantity 
                , sl_locations.ID_locations
                , sl_warehouses_location.ID_customs_info
            FROM sl_warehouses_location
            INNER JOIN sl_locations ON sl_warehouses_location.Location=sl_locations.Code AND sl_warehouses_location.ID_warehouses=sl_locations.ID_warehouses
            INNER JOIN sl_warehouses ON sl_warehouses.ID_warehouses=sl_locations.ID_warehouses
            WHERE 
                sl_warehouses_location.ID_warehouses = ". $from_warehouse ." $add_sql
                AND sl_warehouses_location.ID_products = ". $id_products ."
                AND sl_warehouses_location.Quantity > 0 
                AND sl_locations.Status='Active'
                AND sl_warehouses.Status='Active'
            ORDER BY 
                sl_warehouses_location.Date $invout_order, sl_warehouses_location.Time $invout_order 
            ;";
    $log .= $sql."<br>\n\n";

    my ($sth2) = &Do_SQL($sql);
    while (my $rec = $sth2->fetchrow_hashref){

        if ($diff_wh > 0){
            my $qty_processed=0;

            if ($rec->{'Quantity'} > $diff_wh){
                $sql = "UPDATE sl_warehouses_location SET Quantity = Quantity - $diff_wh WHERE ID_warehouses_location = '". $rec->{'ID_warehouses_location'} ."' LIMIT 1;";
                $log .= $sql."<br>\n\n";
                &Do_SQL($sql);
                $qty_processed = $rec->{'Quantity'} - ($rec->{'Quantity'} - $diff_wh);
            }else{
                $sql = "DELETE FROM sl_warehouses_location WHERE ID_warehouses_location = '". $rec->{'ID_warehouses_location'} ."' LIMIT 1;";
                $log .= $sql."<br>\n\n";
                &Do_SQL($sql);
                $qty_processed = $rec->{'Quantity'};
            }

            ######################################################
            ### sl_warehouses_location - Entrada 
            ######################################################
            $sql = "SELECT 
                        sl_locations.ID_locations 
                    FROM sl_locations 
                    WHERE 
                        UPPER(sl_locations.Code) = UPPER('". $to_location ."') 
                        AND sl_locations.ID_warehouses = '". $to_warehouse ."';";
            $log .= $sql."<br>\n\n";
            my $sth = &Do_SQL($sql);

            $id_locations = $sth->fetchrow_array();

            ### Se valida si ya existe un registro en sl_warehouses_location
            my $sel_sql_custom_info = (!$rec->{'ID_customs_info'}) ? "AND ID_customs_info IS NULL" : "AND ID_customs_info = $rec->{'ID_customs_info'}";
            $sql = "SELECT 
                        ID_warehouses_location 
                    FROM sl_warehouses_location 
                    WHERE 
                        ID_warehouses = '". $to_warehouse ."' 
                        AND ID_products = '". $id_products_new ."' 
                        AND Location = '". $to_location ."' 
                        $sel_sql_custom_info 
                    ORDER BY 
                        Date DESC 
                    LIMIT 1 
                    ;";
            $log .= $sql."<br>\n\n";
            my $sth_exist = &Do_SQL($sql);
            my $id_wl = $sth_exist->fetchrow();
            if( int($id_wl) > 0 ){
                $sql = "UPDATE sl_warehouses_location SET Quantity = Quantity + $qty_processed WHERE ID_warehouses_location = '". $id_wl ."';";
            }else{
                $sql = "INSERT INTO sl_warehouses_location SET ID_warehouses = $to_warehouse, ID_products = '". $id_products_new ."', Location = '". $to_location ."' , Quantity = '". $qty_processed ."', Date = CURDATE(), Time = CURTIME(), ID_admin_users = $usr{'id_admin_users'};";
            }
            $log .= $sql."<br>\n\n";
            &Do_SQL($sql);                

            $sql = "INSERT INTO sl_locations_notes SET ID_locations = '". $id_locations ."', Notes = 'Type: Transfer In\nItem: ($id_products_new) ". &filter_values($pname) ."\nQuantity: $qty_processed', Type = 'Low', Date = CURDATE(), Time = CURTIME(), ID_admin_users = $usr{'id_admin_users'};";
            $log .= $sql."<br>\n\n";
            &Do_SQL($sql);

            $diff_wh -= $rec->{'Quantity'};

            my ($id_manifests) = ($transaction_id)? $transaction_id : 0 ;
            &loc_logging($id_manifests, $id_products, $from_warehouse, $rec->{'Location'}, $to_warehouse , $to_location, $qty_processed);
            $log .= qq|loc_logging($id_manifests, $id_products, $from_warehouse, $rec->{'Location'}, $to_warehouse , $to_location, $qty_processed)|."<br>\n\n";

            $sql = "INSERT INTO sl_locations_notes SET ID_locations = '". $rec->{'ID_locations'} ."', Notes = 'Type: Transfer Out\nItem: ($id_products_new) ". &filter_values($pname) ."\nQuantity: $qty_processed', Type = 'Low', Date = CURDATE(), Time = CURTIME(), ID_admin_users = $usr{'id_admin_users'};";
            $log .= $sql."<br>\n\n";
            &Do_SQL($sql);


            $diff_cost = $qty_processed;
            ###########################
            ### sl_skus_cost - Salida 
            ###########################
            $sql = "SELECT 
                        ID_skus_cost
                        , Quantity
                        , Cost
                        , Cost_Adj
                        , Cost_Add
                    FROM sl_skus_cost
                    WHERE 
                        ID_warehouses = '". $from_warehouse ."' 
                        AND ID_products = '". $id_products ."'
                        AND Quantity > 0 
                        AND Cost > 0 
                    ORDER BY 
                        Date $invout_order, Time $invout_order 
                    ;";
            $log .= $sql."<br>\n\n";
            my ($sth3) = &Do_SQL($sql);
            while (my $rec_cost = $sth3->fetchrow_hashref){

                if ($diff_cost > 0){

                    ###########################
                    ### Costo Promedio
                    ###########################
                    if ($cfg{'acc_inventoryout_method_cost'} and lc($cfg{'acc_inventoryout_method_cost'}) eq 'average'){
                        my ($cost_avg, $total_cost_avg, $id_custom_info, $cost_adj, $cost_add) = &get_average_cost($id_products);

                        if ($cost_avg <= 0) {
                                                
                            return ("ERROR", "AVG Cost Not Found");
                            
                        }

                        $rec_cost->{'Cost'} = $cost_avg;
                        $rec_cost->{'Cost_Adj'} = $cost_adj;
                        $rec_cost->{'Cost_Add'} = $cost_add;
                        $rec->{'ID_customs_info'} = $id_custom_info;
                        
                        $log .= "cost_avg=".$cost_avg."<br>\n";
                        $log .= "cost_adj=".$cost_adj."<br>\n";
                        $log .= "cost_add=".$cost_add."<br>\n";
                        $log .= "id_custom_info=".$id_custom_info."<br>\n";
                        $log .= "total_cost_avg=".$total_cost_avg."<br>\n";
                    }

                    $pcost += $rec_cost->{'Cost'};
                    $log .= "pcost=".$pcost."<br>\n\n";
                    $qty_processed = 0;

                    if ($rec_cost->{'Quantity'} > $diff_cost){
                        $sql = "UPDATE sl_skus_cost SET Quantity = Quantity - $diff_cost WHERE ID_skus_cost = $rec_cost->{'ID_skus_cost'} LIMIT 1;";
                        $log .= $sql."<br>\n\n";
                        &Do_SQL($sql) if ($from_warehouse ne $to_warehouse or $id_products ne $id_products_new);
                        $qty_processed = $rec_cost->{'Quantity'} - ($rec_cost->{'Quantity'} - $diff_cost);
                    }else{
                        $sql = "DELETE FROM sl_skus_cost WHERE ID_skus_cost = $rec_cost->{'ID_skus_cost'} LIMIT 1;";
                        $log .= $sql."<br>\n\n";
                        &Do_SQL($sql) if ($from_warehouse ne $to_warehouse or $id_products ne $id_products_new);
                        $qty_processed = $rec_cost->{'Quantity'};
                    }
                    $diff_cost -= $rec_cost->{'Quantity'};
                    
                    ###########################
                    ### sl_skus_trans
                    ###########################
                    &sku_logging($id_products, $from_warehouse, $rec->{'Location'}, 'Transfer Out', $transaction_id, $transaction_table, $qty_processed, $rec_cost->{'Cost'}, $rec_cost->{'Cost_Adj'}, "OUT", $rec->{'ID_customs_info'}, $rec_cost->{'Cost_Add'});
                    $log .= qq|sku_logging($id_products, $from_warehouse, $rec->{'Location'}, 'Transfer Out', $transaction_id, $transaction_table, $qty_processed, $rec_cost->{'Cost'}, $rec_cost->{'Cost_Adj'}, "OUT", $rec->{'ID_customs_info'}, $rec_cost->{'Cost_Add'})|."<br>\n\n";

                    ###########################
                    ### sl_skus_cost - Entrada 
                    ###########################
                    $sql = "SELECT 
                                ID_skus_cost
                                , Quantity
                                , Cost
                                , Cost_Adj 
                            FROM sl_skus_cost
                            WHERE 
                                ID_warehouses = '". $to_warehouse ."'
                                AND ID_products = '". $id_products_new ."'
                                AND Quantity >= 0 
                                AND Cost = '". $rec_cost->{'Cost'} ."'
                                AND Cost_Adj = '". $rec_cost->{'Cost_Adj'} ."'
                            ORDER BY 
                                Date $invout_order, Time $invout_order 
                            LIMIT 1 
                            ;";
                    $log .= $sql."<br>\n\n";
                    $sth = &Do_SQL($sql);
                    my $rec_cost_to = $sth->fetchrow_hashref();
                    if ($rec_cost_to->{'ID_skus_cost'}){
                        
                        $sql = "UPDATE sl_skus_cost SET Quantity = Quantity + $qty_processed WHERE ID_skus_cost = $rec_cost_to->{'ID_skus_cost'} LIMIT 1;";
                        $log .= $sql."<br>\n\n";
                        &Do_SQL($sql) if ($from_warehouse ne $to_warehouse or $id_products ne $id_products_new);

                    }else{
                        
                        $sql = "INSERT INTO sl_skus_cost SET ID_products=$id_products_new, ID_warehouses=$to_warehouse, Tblname='transfer', Quantity=$qty_processed, Cost=$rec_cost->{'Cost'}, Cost_Adj=$rec_cost->{'Cost_Adj'}, Date = CURDATE(), Time = CURTIME(), ID_admin_users = $usr{'id_admin_users'};";
                        $log .= $sql."<br>\n\n";
                        &Do_SQL($sql) if ($from_warehouse ne $to_warehouse or $id_products ne $id_products_new);

                    }

                    ###########################
                    ### sl_skus_trans
                    ###########################
                    &sku_logging($id_products_new, $to_warehouse, $to_location, 'Transfer In', $transaction_id, $transaction_table, $qty_processed, $rec_cost->{'Cost'}, $rec_cost->{'Cost_Adj'}, "IN", $rec->{'ID_customs_info'}, $rec_cost->{'Cost_Add'});
                    $log .= qq|sku_logging($id_products_new, $to_warehouse, $to_location, 'Transfer In', $transaction_id, $transaction_table, $qty_processed, $rec_cost->{'Cost'}, $rec_cost->{'Cost_Adj'}, "IN", $rec->{'ID_customs_info'}, $rec_cost->{'Cost_Add'})|."<br>\n\n";

                }else{
                    last;
                }
            }
        }else{
            last;
        }
    }

    if ($cfg{'debug_costo_promedio'} and $cfg{'debug_costo_promedio'} == 1){
        &Do_SQL("INSERT INTO sl_debug (cmd, id, log, Date, Time, ID_admin_users) VALUES ('opr_skustranfer', '$transaction_id', '".&filter_values($log)."', CURDATE(), CURTIME(), '$usr{'id_admin_users'}');");
    }

    if ($diff_wh > 0 or $diff_cost > 0){
        
        $log .= "diff_wh=".$diff_wh."<br>\n\n";
        $log .= "diff_cost=".$diff_cost."<br>\n\n";

        return ("ERROR", "$from_warehouse->$id_products ".($quantity - $diff_wh)."<$quantity");

    }

    return ("ok","ok");

}

#############################################################################
#############################################################################
#   Function: get_average_cost
#
#       Es: Obtiene el ultimo registro de costo promedio
#       En: Get last register of average cost
#
#
#    Created on: 2015-09-09
#
#    Author: Jonathan Alcantara
#
#    Modifications:
#
#
#   Parameters:
#       -sku : producto
#
#  Returns:
#
#      - Cost_Avg : costo promedio
#      - total_cost_avg : Costo total promedio
#
#   See Also:
#
sub get_average_cost{
#############################################################################
#############################################################################    

    my ($sku) = @_;

    my ($total_cost_avg, $cost_average, $id_custom_info, $cost_adj, $cost_add);
    $total_cost_avg = 0;

    if( &table_exists('cu_skus_trans') ){
        my $sql = "SELECT Cost_Avg, Cost_Adj_Avg, Cost_Add, ID_customs_info 
                    FROM cu_skus_trans 
                    WHERE ID_products = ".$sku."
                    ORDER BY Date DESC, Time DESC
                    LIMIT 1;";
        my $sth = &Do_SQL($sql);
        ($cost_average, $cost_adj, $cost_add, $id_custom_info) = $sth->fetchrow_array();
    }

    if( !$cost_average or $cost_average == 0 ){

        ### Se crea la tabla temporal y se insertan los registros traidos de sl_skus_trans
        my $sql = " CREATE TEMPORARY TABLE tmp_skus_trans
                    SELECT   
                         sl_skus_trans.ID_products_trans
                        , sl_skus_trans.ID_products
                        , sl_skus_trans.ID_warehouses
                        , sl_skus_trans.Type_trans  
                        , sl_skus_trans.left_quantity
                        , sl_skus_trans.left_quantity_total
                        , sl_skus_trans.Cost_Avg
                        , sl_skus_trans.Cost
                        , sl_skus_trans.Cost_Adj
                        , sl_skus_trans.Cost_Adj_Avg
                        , sl_skus_trans.Cost_Add
                        , sl_skus_trans.ID_customs_info
                        , sl_skus_trans.Date
                        , sl_skus_trans.Time
                    FROM sl_skus_trans
                    WHERE sl_skus_trans.ID_products = ".$sku." AND sl_skus_trans.Cost_Avg > 0
                    ORDER BY sl_skus_trans.Date DESC, sl_skus_trans.Time DESC, sl_skus_trans.ID_products_trans DESC
                    LIMIT 1000;";
        &Do_SQL($sql);

        my $sql = "
            SELECT tmp_skus_trans.Cost_Avg
                , tmp_skus_trans.ID_customs_info
                #, tmp_skus_trans.Cost_Adj
                , tmp_skus_trans.Cost_Adj_Avg
                , tmp_skus_trans.Cost_Add
            FROM tmp_skus_trans
            WHERE tmp_skus_trans.ID_products = ".$sku."
            AND tmp_skus_trans.Type_trans='IN'
            ORDER BY tmp_skus_trans.Date DESC, tmp_skus_trans.Time DESC, tmp_skus_trans.ID_products_trans DESC
            LIMIT 1 LOCK IN SHARE MODE;";
        my $qty_last =  &Do_SQL($sql);
        ($cost_average, $id_custom_info, $cost_adj, $cost_add) = $qty_last->fetchrow_array();

        # my $sql = "
        #     SELECT (tmp_skus_trans.left_quantity_total * tmp_skus_trans.Cost_Avg)AS total_cost_avg
        #     FROM tmp_skus_trans
        #     WHERE tmp_skus_trans.ID_products = ".$sku."
        #     ORDER BY tmp_skus_trans.Date DESC, tmp_skus_trans.Time DESC, tmp_skus_trans.ID_products_trans DESC
        #     LIMIT 1 LOCK IN SHARE MODE;";
        #     my $qty_last =  &Do_SQL($sql);
        # my ($total_cost_avg) = $qty_last->fetchrow_array();

        &Do_SQL("DROP TEMPORARY TABLE tmp_skus_trans;");
    }
    return ($cost_average, $total_cost_avg, $id_custom_info, $cost_adj, $cost_add);
}

1;