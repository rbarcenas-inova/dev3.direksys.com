##########################################################
##		OPERATIONS : WAREHOUSE TRANSFER		  ##
##########################################################

#############################################################################
#############################################################################
#   Function: loaddefault_opr_manifests
#
#       Es: Carga el Status Inicial de un Manifiesto
#       En: 
#
#
#    Created on: 2013-03-19
#
#    Author: Alejandro Diaz
#
#    Modifications:
#
#        - Modified on **: 
#
#   Parameters:
#
#
#  Returns:
#
#      - 
#
#   See Also:
#
#
sub loaddefault_opr_manifests {
#############################################################################
#############################################################################
	
	$in{'status'} = 'In Progress';
		
}


sub view_opr_manifests {
# --------------------------------------------------------
# Created on: unknown
# Author: unknown
# Last Modified on:09/07/2008 PM
# Last Modified by: Jose Ramirez Garcia
# Description : Se cambia el status de processed a completed
# Last Modified on: 04/08/09 13:53:46
# Last Modified by: MCC C. Gabriel Varela S: Se manda a llamar a transfer_warehouses
# Last Modified on: 04/09/09 12:50:57
# Last Modified by: MCC C. Gabriel Varela S: Se contin�a.
# Last Modified on: 05/29/09 17:58:13
# Last Modified by: MCC C. Gabriel Varela S: Se quita validaci�n de query err�neo
# Last Modified by RB on 08/30/2010: Se valida que el manifiesto no este completo y se actualiza antes de iterar
# Last Modified by ISC Alejandro Diaz on 03/03/2015: Se reemplaza funcion move_inventory->warehouse_transfers ademas se aplica uso de Transacciones MySQL

	my $rec,$sth;
	my ($err,$item);

	if ($in{'done'}) {

        ### Se valida que no exista una transaccion activa sobre el mismo proceso
        if( !&transaction_validate($in{'cmd'}, $in{'id_manifests'}, 'check') ){

        	### Se bloquea la transaccion para evitar duplicidad
        	my $id_transaction = &transaction_validate($in{'cmd'}, $in{'id_manifests'}, 'insert');
            

			&Do_SQL("START TRANSACTION;");
				
			my ($sth) = &Do_SQL("SELECT COUNT(*) FROM  sl_manifests WHERE ID_manifests ='$in{'id_manifests'}' AND Status != 'Completed';");
			if ($sth->fetchrow() > 0){
			
				my ($err, $query, $idw, $act_cost);
				my ($sth) = &Do_SQL("SELECT * FROM  sl_manifests_items WHERE ID_manifests = '$in{'id_manifests'}' AND Status = 'New';");
				my $rows = 0;

				LINES:while ($rec = $sth->fetchrow_hashref){
					
					my ($status, $message) = &warehouse_transfers($rec->{'From_Warehouse'}, $rec->{'From_Warehouse_Location'}, $rec->{'To_Warehouse'}, $rec->{'To_Warehouse_Location'}, $rec->{'ID_products'}, $rec->{'Qty'}, $in{'id_manifests'}, 'sl_manifests');

					if ($status =~ /ok/i){

						++$rows
						&Do_SQL("UPDATE sl_manifests_items SET Status = 'Done' WHERE ID_manifests_items = '$rec->{'ID_manifests_items'}';");
						&auth_logging('manifest_item_done',$in{'id_manifests'});

					}else{

						&Do_SQL("UPDATE sl_manifests_items SET Status = 'Failed' WHERE ID_manifests_items = '$rec->{'ID_manifests_items'}';");
						my ($st, $qty) = split(/:/, $status);
						$va{'message'} .= qq|$rec->{'ID_products'} $rec->{'Qty'} < $qty\n|;
						$va{'message'} .= qq|<br />$message\n|;
						
					}
		
				}
				
				if (!$rows or $va{'message'}){

					$va{'message'} = &trans_txt('manifest_error') . qq|\n $va{'message'}|;
					($rows) and ($in{'status'} = 'Completed') and ($in{'processedby'} = $usr{'id_admin_users'}) and ( &Do_SQL("UPDATE sl_manifests SET Status='Completed', ProcessedBy='$usr{'id_admin_users'}', ProcessedDate = CURDATE() WHERE ID_manifests = '$in{'id_manifests'}';") );

					&Do_SQL("ROLLBACK;");

					$in{'db'} = "sl_manifests";
					&auth_logging('manifest_item_failed',$in{'id_manifests'});

					### Elimina el registro de la transaccion activa de este proceso
	            	&transaction_validate($in{'cmd'}, $in{'id_manifests'}, 'delete');
	            	
				}else{

					&Do_SQL("UPDATE sl_manifests SET Status='Completed', ProcessedBy='$usr{'id_admin_users'}', ProcessedDate=CURDATE() WHERE ID_manifests='$in{'id_manifests'}';");
					#&Do_SQL("DELETE FROM sl_warehouses_location WHERE Quantity=0;");

					&auth_logging('manifest_done',$in{'id_manifests'});
					$va{'message'}=&trans_txt('manifest_done');

					$in{'status'} = 'Completed';
					$in{'processedby'} = $usr{'id_admin_users'};

					&Do_SQL("COMMIT;");
					#&Do_SQL("ROLLBACK;"); #Only debug

				}

				### Elimina el registro de la transaccion activa de este proceso
	            &transaction_validate($in{'cmd'}, $in{'id_manifests'}, 'delete');
	      
			}

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
		$va{'statusmsg'} = "($in{'processedby'}) ";
		if ($in{'processedby'}){
			$va{'statusmsg'} .= &load_db_names('admin_users','ID_admin_users',$in{'processedby'},'[LastName], [FirstName]') . " &nbsp; $in{'processeddate'}";
		}
	}elsif ($in{'search'} ne 'Print'){
		$va{'status'} = "&nbsp;&nbsp; ".&trans_txt('change_to'). " : <a href='/cgi-bin/mod/$usr{'application'}/dbman?cmd=opr_manifests&view=$in{'id_manifests'}&done=1' onclick='return ConfirmLink();' id='lnkCompleted'>Completed</a>";
	}

	$va{'this_style'} = $in{'status'} ne 'In Progress' ? qq|style = "display:none"| : "";
	if( $in{'status'} eq 'In Progress' ) {

		$va{'div_height'} = 50;
		my ($sth) =  &Do_SQL("SELECT ID_manifests_items, ID_products, sl_parts.Name, From_warehouse, From_warehouse_Location,To_warehouse, To_Warehouse_Location,Qty
                    FROM sl_parts INNER JOIN sl_manifests_items 
                    ON ID_parts = RIGHT(ID_products,4) 
                    WHERE ID_manifests = '$in{'id_manifests'}'
                    ORDER BY ID_manifests_items;");
		while(my($idmi, $id_parts, $name, $fwh, $from_location, $twh, $to_location, $qty) = $sth->fetchrow()){

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

		if($va{'ids_in'}) {
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

	if ($in{'toprint'}) {
		&detail_manifests();
	}
}

#############################################################################
#############################################################################
#   Function: detail_manifests
#
#       Es: Obtiene el detalle de SKUs transferidos
#       En: SKUs transfered detail
#
#
#    Created on: 20/06/2013
#
#    Author: Alejandro Diaz
#
#    Modifications:
#
#        - Modified on ** by *** : 
#
#   Parameters:
#
#      - ID_manifests
#
#  Returns:
#
#      --
#
#   See Also:
#
#      <>
#
sub detail_manifests{
#############################################################################
#############################################################################

	my ($sth) =  &Do_SQL("SELECT ID_manifests_items, ID_products, sl_parts.Name, From_warehouse, From_warehouse_Location,To_warehouse, To_warehouse_Location,Qty, sl_manifests_items.Status
                    FROM sl_parts INNER JOIN sl_manifests_items 
                    ON ID_parts = RIGHT(ID_products,4) 
                    WHERE ID_manifests = '$in{'id_manifests'}'
                    ORDER BY ID_manifests_items;");
	while(my($idmi, $id_parts, $name, $fwh, $from_location, $twh, $to_location, $qty, $status) = $sth->fetchrow()){

		my $fwhname = &load_name('sl_warehouses', 'ID_warehouses', $fwh, 'Name');
		my $twhname = &load_name('sl_warehouses', 'ID_warehouses', $twh, 'Name');
		my $this_style = $status eq 'Failed' ? 'style="color:red"' : '';

		$va{'searchresults'} .= qq|<tr id="row-$idai" >\n
									<td style="border-left:1px solid #555555;border-bottom:1px solid #555555;" align="left" $this_style>$status</td>\n 
									<td style="border-left:1px solid #555555;border-bottom:1px solid #555555;">|.&format_sltvid($id_parts).qq|</td>\n
									<td style="border-left:1px solid #555555;border-bottom:1px solid #555555;">$name</td>\n 
									<td style="border-left:1px solid #555555;border-bottom:1px solid #555555;"><a href="/cgi-bin/mod/[ur_application]/dbman?cmd=opr_warehouses&view=$fwh" title="View $fwh">($fwh)</a> $fwhname / <a href="/cgi-bin/mod/[ur_application]/dbman?cmd=opr_locations&search=Search&id_warehouses=$fwh&code=$from_location" title="View $from_location">$from_location</a></td>\n 
									<td style="border-left:1px solid #555555;border-bottom:1px solid #555555;"><a href="/cgi-bin/mod/[ur_application]/dbman?cmd=opr_warehouses&view=$twh" title="View $twh">($twh)</a> $twhname / <a href="/cgi-bin/mod/[ur_application]/dbman?cmd=opr_locations&search=Search&id_warehouses=$twh&code=$to_location" title="View $to_location">$to_location</a></td>\n
									<td style="border-left:1px solid #555555;border-bottom:1px solid #555555;" align="right">$qty</td>\n 
								</tr>|;	
	}

}

1;