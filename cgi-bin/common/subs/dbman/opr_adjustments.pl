
sub view_opr_adjustments {
# --------------------------------------------------------
# Created on: 07/17/08 @ 14:31:22
# Author: Roberto Barcenas
# Last Modified on: 07/17/08 @ 14:31:22
# Last Modified by: Carlos Haas
# Description : 
# Parameters : 
# Last Modified RB: 11/10/08  18:02:47  -- Drop rows insted balance			   
# Last Modified on: 03/11/09 15:18:06
# Last Modified by: MCC C. Gabriel Varela S: Se pone WHERE ID_adjustments='$in{'id_adjustments'}'; en el update de status Denied. Observación hecha por José.
# Last Modification by JRG : 03/11/2009 : Se agrega el log
# Last Modified on: 06/08/09 15:52:18
# Last Modified by: MCC C. Gabriel Varela S: Se valida que no existan sets.
# Last Modified RB: 06/26/09  11:31:24 -- Se agregan los movimientos contables.


	my ($diff,$diffgral,$err);

	if ($in{'chg_status'} eq 'Denied'){ 

		if(!&check_permissions('opr_adjustments','_edit','')){ return 'error'; };
		
		my ($sth) = &Do_SQL("UPDATE sl_adjustments SET Status='Denied' WHERE ID_adjustments='$in{'id_adjustments'}';");
		&auth_logging('adjustments_denied',$in{'id_adjustments'});
		$in{'status'} = 'Denied';

	}elsif ($in{'status'} eq 'New' and $in{'chg_status'} eq 'Approved' ){

		if(!&check_permissions('opr_adjustments','_edit','')){ return 'error'; };

		#Verifica si hay sets en la lista:
		my ($sth) = &Do_SQL("SELECT COUNT(*),SUM(IF(Isset='Y',1,0)) AS SumY
							FROM sl_adjustments_items 
							INNER JOIN sl_skus ON(sl_adjustments_items.ID_products=ID_sku_products)
							WHERE ID_adjustments='$in{'id_adjustments'}';");
		($count,$sumy)=$sth->fetchrow_array();

		$err = 0;
		if($count > 0 and !$sumy){

			### Valida si no se generara contabilidad y si tiene el permiso para esta opcion
			my $skip_accounting = ($in{'skip_acc'} and int($in{'skip_acc'}) == 1) ? 'Yes' : 'No';
			if( $skip_accounting eq 'Yes' and !&check_permissions('opr_adjustments_skip_accounting','','') ){
				$va{'message'} = &trans_txt('unauth_action');
				return;
			}

			### Se valida que no exista una transaccion activa sobre el mismo proceso
	        if( !&transaction_validate($in{'cmd'}, $in{'id_adjustments'}, 'check') ){

	        	### Se bloquea la transaccion para evitar duplicidad
	        	my $id_transaction = &transaction_validate($in{'cmd'}, $in{'id_adjustments'}, 'insert');

				### Metodo usado para la salida de inventario. FIFO: Primer entradas primeras salidas | LIFO: Ultimas entradas primeras salidas
				my $acc_method = $cfg{'acc_inventoryout_method'} ? $cfg{'acc_inventoryout_method'} : 'fifo';
				my $invout_order = $acc_method eq 'fifo' ? '' : 'DESC';
			
				my ($sth) = &Do_SQL("SELECT * FROM sl_adjustments_items WHERE ID_adjustments='$in{'id_adjustments'}';");

				&Do_SQL("START TRANSACTION;");
				my $notes = ( $skip_accounting eq 'Yes' ) ? "Skip accounting\n" : "Adjustment\n";

				AITEMS:while (my $rec = $sth->fetchrow_hashref){

					my $cost = 0;
					my $cost_adj = 0;
					my $id_custom_info;
					my $cost_add = 0;
					my $tot_accounting = 0;
					my($idsc,$items_qty);

					&Do_SQL("DELETE FROM sl_warehouses_location WHERE ID_warehouses = '$rec->{'ID_warehouses'}' AND ID_products = '$rec->{'ID_products'}' AND Location = '$rec->{'Location'}' AND `Quantity` = 0;");
					&set_wlocation_grouped($rec->{'ID_warehouses'}, $rec->{'Location'}, $rec->{'ID_products'});

					##################
					################## Difference
					################## 				
					my ($sth) = &Do_SQL("SELECT ID_warehouses_location, Location, Quantity FROM sl_warehouses_location WHERE ID_warehouses='$rec->{'ID_warehouses'}' AND ID_products='$rec->{'ID_products'}' AND Location='$rec->{'Location'}' AND Quantity > 0 ORDER BY Date $invout_order LIMIT 1;");
					#my ($idwl,$act_qty) = $sth->fetchrow();				
					my ($idwl,$location,$act_qty) = $sth->fetchrow();
					my $diffgral =  $rec->{'Qty'} - $act_qty;
					my $diff = abs($diffgral);

					### Valida si realmente hay un ajuste que aplicar
					if( $diff > 0 ){

						### Se valida el ID_warehouses - Location
						my $sql_loc = "SELECT UPC FROM sl_locations WHERE ID_warehouses = ".$rec->{'ID_warehouses'}." AND Code = '".$rec->{'Location'}."' LIMIT 1;";
						my $sth_loc = &Do_SQL($sql_loc);
						my $upc_loc = $sth_loc->fetchrow();
						if( !$upc_loc or $upc_loc eq '' ){
							++$err;
							$va{'message'} .= &trans_txt('warehouse_not_location').': '.$rec->{'ID_products'}.' -> '.$rec->{'ID_warehouses'}.' -> '.$rec->{'Location'}."<br />";
						}

						my $oper = ( $diffgral > 0 ) ? '+' : '-';
						$act_qty = 0 if(!$act_qty);
						$notes .= "SKU: ".$rec->{'ID_products'}." :: Movement: $act_qty $oper $diff = $rec->{'Qty'}\n";
						

						##################
						################## warehouse location
						################## 
						if($rec->{'Qty'} > 0){
							if( $idwl ){
								$sthin = &Do_SQL("/* FROM Adjustment $in{'id_adjustments'} */ UPDATE sl_warehouses_location SET Quantity = '$rec->{'Qty'}' WHERE ID_warehouses_location = '$idwl';");			
							}else{
								$sthin = &Do_SQL("/* FROM Adjustment $in{'id_adjustments'} */ INSERT INTO sl_warehouses_location SET ID_warehouses='$rec->{'ID_warehouses'}', Location='$rec->{'Location'}', ID_products='$rec->{'ID_products'}', Quantity='$rec->{'Qty'}', Date=CURDATE(), Time=CURTIME(), ID_admin_users='$usr{'id_admin_users'}';");
							}
						}else{
							my ($sthd) = &Do_SQL("/* FROM Adjustment $in{'id_adjustments'} */ DELETE FROM sl_warehouses_location WHERE ID_warehouses_location = '$idwl';"); 
						}
						&auth_logging('warehouses_location_added',$sthin->{'mysql_insertid'});

						##################
						################## skus cost
						################## 
						do{

							my ($sth) = &Do_SQL("SELECT ID_skus_cost, Quantity, Cost FROM sl_skus_cost WHERE ID_warehouses = '". $rec->{'ID_warehouses'} ."' AND ID_products = '". $rec->{'ID_products'} ."' AND Quantity > 0 ORDER BY Date $invout_order LIMIT 1;");
							($idsc,$items_qty,$cost) = $sth->fetchrow;

							###
							### Costo Promedio
							###
							if( $cfg{'acc_inventoryout_method_cost'} and $cfg{'acc_inventoryout_method_cost'} eq 'average' ){
								($cost, $total_cost_avg, $id_custom_info, $cost_adj, $cost_add) = &get_average_cost($rec->{'ID_products'});
							}
							
							if($diffgral > 0){
								## Add Items to DB

								if($idsc){
									my ($sth2) = &Do_SQL("/* FROM Adjustment $in{'id_adjustments'} */ UPDATE sl_skus_cost SET Quantity = $items_qty + $diff  WHERE ID_skus_cost = '$idsc' ;");
									$tot_accounting = $diff * $cost;
								}else{	
									($cost, $cost_adj, $id_custom_info, $cost_add) = &load_sltvcost($rec->{'ID_products'}) if( int($cost) == 0 );
									if( $cost == 0 ){
										$va{'message'} .= &trans_txt('opr_adjustments_error_cost').' for Add-SKU: '.$rec->{'ID_products'} . qq|<br>|;
										++$err;
									}
									my ($sth2) = &Do_SQL("/* FROM Adjustment $in{'id_adjustments'} */ INSERT INTO sl_skus_cost SET ID_warehouses='$rec->{'ID_warehouses'}' ,ID_products='$rec->{'ID_products'}',ID_purchaseorders='$rec->{'ID_adjustments'}',Tblname='sl_adjustments',Quantity=$diff,Cost='$cost',Cost_Adj='$cost_adj',Date=CURDATE(),Time=CURTIME(),ID_admin_users='$usr{'id_admin_users'}' ;");
									&auth_logging('sku_cost_added',$sth2->{'mysql_insertid'});
									$tot_accounting = $diff * $cost;
								}
								$diff = 0;
							
							}else{
								## Remove Items From DB

								if($idsc) {
									if ($items_qty >= $diff){
								
										my ($sth2) = &Do_SQL("UPDATE sl_skus_cost SET Quantity = $items_qty - $diff  WHERE ID_skus_cost = '$idsc' ;");
										$tot_accounting += ($diff * $cost);
										$diff = 0;
										&auth_logging('sku_cost_updated',$idsc);

									}else{

										my ($sth) = &Do_SQL("/* FROM Adjustment $in{'id_adjustments'} */ DELETE FROM sl_skus_cost WHERE ID_skus_cost = '$idsc';");
										$tot_accounting += ($items_qty * $cost);
										$diff -= $items_qty;
										
									}

								}else{

									## 
									($cost, $cost_adj, $id_custom_info, $cost_add) = &load_sltvcost($rec->{'ID_products'}) if( int($cost) == 0 );
									if( $cost == 0 ){
										$va{'message'} .= &trans_txt('opr_adjustments_error_cost').' for Remove-SKU: '.$rec->{'ID_products'} . qq|<br>|;
										++$err;
									}
									$tot_accounting = $diff * $cost;
									my ($sth2) = &Do_SQL("/* FROM Adjustment $in{'id_adjustments'} */ INSERT INTO sl_skus_cost SET ID_warehouses='$rec->{'ID_warehouses'}' ,ID_products='$rec->{'ID_products'}',ID_purchaseorders='$rec->{'ID_adjustments'}',Tblname='sl_adjustments',Quantity=$diff,Cost='$cost',Cost_Adj='$cost_adj',Date=CURDATE(),Time=CURTIME(),ID_admin_users='$usr{'id_admin_users'}' ;");
									&auth_logging('sku_cost_added',$sth2->{'mysql_insertid'});

								}
							
							}

						}while($diff);
					}else{
						#++$err;
						#$va{'message'} = "Not adjustment for ".$rec->{'ID_products'}.", Current quantity=$act_qty, Difference=$diff";
						$notes .= "SKU: ".$rec->{'ID_products'}." - ".$rec->{'Location'}." not adjustment, Difference=0\n";
						next AITEMS;
					}

					if( $err == 0 ){
						my ($sth2) = &Do_SQL("UPDATE sl_adjustments_items SET Price = '$tot_accounting', Adj = $diffgral WHERE  ID_adjustments_items = '$rec->{'ID_adjustments_items'}'");

						### Registra la transaccion
						my $type_trans = ( $diffgral > 0 ) ? "IN" : "OUT";
						### Se sustituye $rec->{'Qty'} por abs($diffgral);
						&sku_logging($rec->{'ID_products'},$rec->{'ID_warehouses'},$rec->{'Location'},'Adjustment',$in{'id_adjustments'},'sl_adjustments',abs($diffgral),$cost,$cost_adj,$type_trans,$id_custom_info,$cost_add);

						## ToDo: Movimientos de contabilidad Positivos/Negativos basado en $difgral
						## Movimientos de contabilidad
						if($tot_accounting > 0 and $skip_accounting eq 'No') {
							my $wht = &load_name('sl_warehouses', 'ID_warehouses',$rec->{'ID_warehouses'},'Type'); 
							my @params = ($in{'id_adjustments'},$diffgral,$tot_accounting);
		 					&accounting_keypoints('warehouse_adjustment_'. $wht, \@params); 
					 	}
					}

				}

				if( $err == 0 ){
					### Nota
					&Do_SQL("INSERT INTO sl_adjustments_notes SET ID_adjustments = $in{'id_adjustments'}, Notes = '$notes', Type = 'Low', Date = CURDATE(), Time = CURTIME(), ID_admin_users = '$usr{'id_admin_users'}';");

					my ($sth) = &Do_SQL("UPDATE sl_adjustments SET AuthBy='$usr{'id_admin_users'}',AuthDate=CURDATE(),Status='Approved' WHERE ID_adjustments='$in{'id_adjustments'}'");
					&auth_logging('adjustments_updated',$in{'id_adjustments'});
					$in{'status'} = 'Approved';
					$in{'authby'} = $usr{'id_admin_users'};
					$va{'message'} = &trans_txt('opr_adjustments_approved');

					&auth_logging('opr_adjustments_approved',$in{'id_adjustments'});

					&Do_SQL("COMMIT;");
					#&Do_SQL("ROLLBACK;"); #Only debug
				}else{
					&Do_SQL("ROLLBACK;");
				}

				### Elimina el registro de la transaccion activa de este proceso
	            &transaction_validate($in{'cmd'}, $in{'id_adjustments'}, 'delete');

			}else{
				$va{'message'} = &trans_txt('transaction_duplicate');
			}

		}else{
			$va{'message'} = &trans_txt('opr_adjustments_cant_approved');
		}		
	}
	
	$va{'accounts_positive'} = $in{'id_accounts_positive'} ? qq|( <a href="/cgi-bin/mod/[ur_application]/dbman?cmd=fin_accounts&view=[in_id_accounts_positive]" title="View [in_id_accounts_positive]">[in_id_accounts_positive]</a> ) |.&load_name('sl_accounts','ID_accounts',$in{'id_accounts_positive'},'Name') : qq|---|;
	$va{'accounts_negative'} = $in{'id_accounts_negative'} ? qq|( <a href="/cgi-bin/mod/[ur_application]/dbman?cmd=fin_accounts&view=[in_id_accounts_negative]" title="View [in_id_accounts_negative]">[in_id_accounts_negative]</a> ) |.&load_name('sl_accounts','ID_accounts',$in{'id_accounts_negative'},'Name') : qq|---|;

	$va{'authby'} = $in{'authby'} ? &load_db_names('admin_users','ID_admin_users', $in{'authby'},"[FirstName] [LastName]") : '---';
	($va{'authby'} ne '---') and ($va{'authby'} = qq|(<a href="/cgi-bin/mod/[ur_application]/dbman?cmd=usrman&view=[in_authby]" title="View [in_authby]">[in_authby]</a>)&nbsp;$va{'authby'}|);
	$va{'this_style'} = $in{'status'} ne 'New' ? qq|style = "display:none"| : "";
	if ($in{'status'} eq 'New'){

		$va{'div_height'} = 50;		
		my ($sth) =  &Do_SQL("SELECT ID_adjustments_items, ID_products, sl_warehouses.Name, 
						sl_warehouses.ID_warehouses, sl_parts.Name, Location,Qty
	                    FROM sl_parts INNER JOIN sl_adjustments_items 
	                    ON ID_parts = RIGHT(ID_products,4) 
	                    INNER JOIN sl_warehouses USING(ID_warehouses)
	                    WHERE ID_adjustments = '$in{'id_adjustments'}'
	                    ORDER BY ID_adjustments_items;");
		while(my($idai, $id_parts, $whname, $id_warehouses, $name, $location, $qty) = $sth->fetchrow()){

			$va{'div_height'} += 22;
			$va{'ids_in'} .= qq|<tr id="row-$idai">\n
								<td><img src="/sitimages/default/b_drop.png" class="rdrop" id="drop-$idai" style="cursor:pointer" title="Drop $id_parts"></td>\n
								<td>|.&format_sltvid($id_parts).qq|</td>\n
								<td>$name</td>\n 
								<td><a href="/cgi-bin/mod/$usr{'application'}/dbman?cmd=opr_warehouses&view=$id_warehouses" title="View $id_warehouses">($id_warehouses) $whname</a></td>\n 
								<td align="center">$location</td>\n 
								<td  align="right">$qty</td>\n 
							</tr>|;	
		}

		if($va{'ids_in'}) {
			$va{'ids_in'} = qq|<table id="tbl-id-in" width="98%" align="center" cellspacing="2" cellpadding="2" class="formtable">\n 
							<tr>\n 
								<td align="center" class="menu_bar_title">&nbsp;</td>\n 
								<td align="center" class="menu_bar_title">ID</td>\n 
								<td align="center" class="menu_bar_title">Name</td>\n 
								<td align="center" class="menu_bar_title">Warehouse</td>\n 
								<td align="center" class="menu_bar_title">Location</td>\n 
								<td align="center" class="menu_bar_title">Quantity</td>\n 
							</tr>\n
							$va{'ids_in'}
						</table>\n|;
		}

		#$va{'linkedit'} = qq|<a href="/cgi-bin/mod/$usr{'application'}/dbman?cmd=[in_cmd]&modify=[in_id_adjustments]"><img src='[va_imgurl]/[ur_pref_style]/b_edit.gif' title='View' alt='' border='0'></a>|;
		$va{'status'} .= qq|&nbsp;&nbsp;
								<a href="#">
									<img src='[va_imgurl]/[ur_pref_style]/capt-fu.png' title='Approve' alt='' border='0' onClick='if(confirm("WAIT!! Do you really want to APPROVE this adjustment?")){trjump("/cgi-bin/mod/[ur_application]/dbman?cmd=[in_cmd]&view=[in_id_adjustments]&tab=1&chg_status=Approved")}'>
								</a>
							&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
								<a href="#">
									<img src='[va_imgurl]/[ur_pref_style]/b_drop.png' title='Deny' alt='' border='0' onClick='if(confirm("Do you want to DENY this adjustment?")){trjump("/cgi-bin/mod/[ur_application]/dbman?cmd=[in_cmd]&view=[in_id_adjustments]&tab=1&chg_status=Denied")}'>
								</a>|;
		if( &check_permissions('opr_adjustments_skip_accounting','','') ){
			$va{'status'} .= qq|&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; \|\| &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
								<a href="#">
									<img src='[va_imgurl]/[ur_pref_style]/auth-fu.png' title='Approve Skip Accounting' alt='' border='0' onClick='if(confirm("ALERT Do you want to APPROVE this adjustment without accounting?")){trjump("/cgi-bin/mod/[ur_application]/dbman?cmd=[in_cmd]&view=[in_id_adjustments]&tab=1&chg_status=Approved&skip_acc=1")}'>
								</a>|;
		}

	}else{
		$va{'start_notes'} = "<!--";
		$va{'end_notes'} = "-->";		
	}
}


#########################################################################################
#########################################################################################
#   Function: edit_bills_applies
#
#   Es: Carga datos para autocomplete
#
#   Created on: 20/03/2013  19:11
#
#   Author: Alejandro Diaz
#
#   Modifications:
#
#      - Modified on 
#
#   Parameters:
#
#   Returns:
#
sub data_parts_adjustments {
#########################################################################################
#########################################################################################
	my $output='';
	if(int($in{'id_adjustments'})>0) {

		my ($sth) = &Do_SQL("SELECT 
			ID_warehouses, sl_warehouses.Name wname,
			sl_warehouses_location.ID_products as ID,
			IF(NOT ISNULL(sl_products.Model),sl_products.Model,sl_parts.Model)as Model,
			IF((NOT ISNULL(sl_products.Name) and sl_products.Name!=''),sl_products.Name,sl_parts.Name)as Name,
			SUM(Quantity) Quantity,
			sl_warehouses_location.Location
			FROM sl_warehouses_location 
			INNER JOIN sl_warehouses USING(ID_warehouses)
			INNER JOIN sl_skus on(sl_warehouses_location.ID_products=sl_skus.ID_sku_products)
			LEFT JOIN sl_products on(RIGHT(sl_warehouses_location.ID_products,6)=sl_products.ID_products and sl_warehouses_location.ID_products like '1%')
			LEFT JOIN sl_parts on(RIGHT(sl_warehouses_location.ID_products,4)=sl_parts.ID_parts and sl_warehouses_location.ID_products like '4%' )
			AND Isset!='Y'
			AND sl_warehouses_location.Quantity>0 
			GROUP BY ID_warehouses, Model, Name, Location
			ORDER BY Quantity DESC ");
		while (my $rec = $sth->fetchrow_hashref()){
			$output .= '"'.$rec->{'ID'}.'   '.$rec->{'Name'}.' x '.$rec->{'Quantity'}.'   '.$rec->{'wname'}.'   '.$rec->{'ID_warehouses'}.'   '.$rec->{'Location'}.'",';

		}
	}
	chop($output);

	return $output;
}

1;