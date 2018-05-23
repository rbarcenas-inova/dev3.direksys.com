##########################################################
##              OPERATIONS : WAREHOUSE TRANSFER           ##
##########################################################

#############################################################################
#############################################################################
#   Function: view_opr_skustransfers
#
#       Es: 
#       En: 
#
#
#    Created on: 2015-08-25
#
#    Author: ISC Alejandro Diaz
#
#    Modifications:
#
#
#   Parameters:
#
#   Returns:
#
#   See Also:
#
sub view_opr_skustransfers {
#############################################################################
#############################################################################

    my $rec,$sth;
    my ($err,$item);

    if ($in{'done'}) {

        my $acc_method = $cfg{'acc_inventoryout_method'} ? $cfg{'acc_inventoryout_method'} : 'fifo';
        my $invout_order = $acc_method eq 'fifo' ? '' : 'DESC';

        ### Se valida que no exista una transaccion activa sobre el mismo proceso
        if( !&transaction_validate($in{'cmd'}, $in{'id_skustransfers'}, 'check') ){

            ### Se bloquea la transaccion para evitar duplicidad
            my $id_transaction = &transaction_validate($in{'cmd'}, $in{'id_skustransfers'}, 'insert');

            my ($sth) = &Do_SQL("SELECT COUNT(*) FROM  sl_skustransfers WHERE ID_skustransfers ='$in{'id_skustransfers'}' AND Status != 'Completed';");
            
            if ($sth->fetchrow() > 0){

                my ($err,$query,$idw,$act_cost);
                my ($sth) = &Do_SQL("SELECT * FROM  sl_skustransfers_items WHERE ID_skustransfers = '$in{'id_skustransfers'}' AND Status = 'New'");
                my $rows = 0;
                my $errors = 0;


                ### Inicializa la transaccion
                &Do_SQL("START TRANSACTION;");

                LINES:while ($rec = $sth->fetchrow_hashref){
                    my ($status, $message) = &warehouse_skutransfers($rec->{'From_Warehouse'}, $rec->{'From_Warehouse_Location'}, $rec->{'To_Warehouse'}, $rec->{'To_Warehouse_Location'}, $rec->{'FromSku'}, $rec->{'Qty'}, $rec->{'ToSku'}, $in{'id_skustransfers'});

                    if ($status =~ /ERROR/i){
                        $errors++;
                        $va{'message'} .= $message;
                    }else{             
                        &Do_SQL("UPDATE sl_skustransfers_items SET Status = 'Done' WHERE ID_skustransfers_items = '".$rec->{'ID_skustransfers_items'}."' LIMIT 1" );
                    }

                    $rows++;

                }

                if (!$rows){
                    $va{'message'} .= &trans_txt('manifest_error');
                    &Do_SQL("ROLLBACK;");
                }elsif($errors){
                    $va{'message'} = "ERROR<br>".$va{'message'};
                    &Do_SQL("ROLLBACK;");
                }else{
                    &Do_SQL("UPDATE sl_skustransfers SET Status='Completed', ProcessedBy='$usr{'id_admin_users'}', ProcessedDate = CURDATE() WHERE ID_skustransfers = '$in{'id_skustransfers'}';");
                    
                    &auth_logging('manifest_done',$in{'id_skustransfers'});
                    $va{'message'} .= &trans_txt('manifest_done');

                    $in{'status'} = 'Completed';
                    $in{'processedby'} = $usr{'id_admin_users'};

                    &Do_SQL("COMMIT;");
                    #&Do_SQL("ROLLBACK;"); ## Only Debug
                }

            }

            ### Elimina el registro de la transaccion activa de este proceso
            &transaction_validate($in{'cmd'}, $in{'id_skustransfers'}, 'delete');

        }else{
            $va{'message'} = &trans_txt('transaction_duplicate');
        }
    }

    if ($in{'requestedby'}){
        $va{'reqname'} = &load_db_names('admin_users','ID_admin_users',$in{'requestedby'},'[LastName], [FirstName]');
    }else{
        $va{'reqname'} = '---';
    }

    if ($in{'authorizedby'}){
        $va{'reqauth'} = &load_db_names('admin_users','ID_admin_users',$in{'authorizedby'},'[LastName], [FirstName]');
    }else{
        $va{'reqauth'} = '---';
    }

    if ($in{'status'} eq 'Completed'){
        $va{'statusmsg'} = " &nbsp;&nbsp; ($in{'processedby'}) ";
        if ($in{'processedby'}){
            $va{'statusmsg'} .= &load_db_names('admin_users','ID_admin_users',$in{'processedby'},'[LastName], [FirstName]') . " &nbsp; $in{'processeddate'}";
        }
    }elsif ($in{'search'} ne 'Print'){
        $va{'status'} = "&nbsp;&nbsp; ".&trans_txt('change_to'). " : <a href='/cgi-bin/mod/$usr{'application'}/dbman?cmd=opr_skustransfers&view=$in{'id_skustransfers'}&done=1'>Completed</a>";
    }

    $va{'this_style'} = $in{'status'} ne 'In Progress' ? qq|style = "display:none"| : "";
    if ( $in{'status'} eq 'In Progress' ) {

        $va{'div_height'} = 50;
        my ($sth) =  &Do_SQL("SELECT ID_skustransfers_items, FromSku, sl_parts.Name, From_warehouse, From_warehouse_Location,To_warehouse, To_Warehouse_Location,Qty
                                FROM sl_parts 
                                    INNER JOIN sl_skustransfers_items ON ID_parts = RIGHT(FromSku,4) 
                                WHERE ID_skustransfers = '$in{'id_skustransfers'}'
                                ORDER BY ID_skustransfers_items;");
        while (my($idmi, $id_parts, $name, $fwh, $from_location, $twh, $to_location, $qty) = $sth->fetchrow()){

            my $fwhname = &load_name('sl_warehouses', 'ID_warehouses', $fwh, 'Name');
            my $twhname = &load_name('sl_warehouses', 'ID_warehouses', $twh, 'Name');

            $va{'div_height'} += 22;
            $va{'ids_in'} .= qq|<tr id="row-$idai">\n
                                    <td><img src="/sitimages/default/b_drop.png" class="rdrop" id="drop-$idmi" style="cursor:pointer" title="Drop $id_parts"></td>\n
                                    <td>|.&format_sltvid($id_parts).qq|</td>\n
                                    <td>$name</td>\n 
                                    <td><a href="/cgi-bin/mod/$usr{'application'}/dbman?cmd=opr_warehouses&view=$fwh" title="View $fwh">($fwh) $fwhname / $from_location</a></td>\n 
                                    <td><a href="/cgi-bin/mod/$usr{'application'}/dbman?cmd=opr_warehouses&view=$twh" title="View $twh">($twh) $twhname / $to_location</a></td>\n
                                    <td  align="right">$qty</td>\n 
                                </tr>|;
        }

        if ($va{'ids_in'}) {
            $va{'ids_in'} = qq|<table id="tbl-id-in" width="98%" align="center" cellspacing="2" cellpadding="2" class="formtable">\n 
                                    <tr>\n 
                                        <td align="center" class="menu_bar_title">&nbsp;</td>\n 
                                        <td align="center" class="menu_bar_title">ID</td>\n 
                                        <td align="center" class="menu_bar_title">Name</td>\n 
                                        <td align="center" class="menu_bar_title">From Warehouse / Location</td>\n 
                                        <td align="center" class="menu_bar_title">To Warehouse / Location</td>\n 
                                        <td align="center" class="menu_bar_title">Quantity</td>\n 
                                    </tr>\n
                                    $va{'ids_in'}
                                </table>\n|;
        }
    }
}

1;