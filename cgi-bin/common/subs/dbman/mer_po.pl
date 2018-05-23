#########################################################
##		MERCHANDISING : PURCHASE ORDER
##########################################################

#############################################################################
#############################################################################
#   Function: loaddefault_mer_po
#
#       Es: Carga valores por defecto para mer_po
#       En: 
#
#
#    Created on: 04/18/2013
#
#    Author: _Roberto Barcenas_
#
#    Modifications:
#
#        - Modified on ** by _Roberto Barcenas_ : 
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
#      <>
#
sub loaddefault_mer_po{
#############################################################################
#############################################################################

	$in{'podate'} = &get_sql_date();
	$in{'type'} = 'purchase order';
	#&cgierr;

}


#############################################################################
#############################################################################
#   Function: loading_mer_po
#
#       Es: Carga valores por defecto para mer_po en la edicion
#       En: 
#
#
#    Created on: 04/22/2013
#
#    Author: _Roberto Barcenas_
#
#    Modifications:
#
#        - Modified on ** by _Roberto Barcenas_ : 
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
#      <>
#
sub loading_mer_po{
#############################################################################
#############################################################################

#	$va{'currency_style'};
#	if($in{'currency_exchange'} > 0) {
#
#		## Si existe el currency rate, determinar si se debe permitir editar
#		my ($sth) = &Do_SQL("SELECT SUM(Received) FROM sl_purchaseorders_items WHERE ID_purchaseorders = '$in{'id_purchaseorders'}';");
#		my ($total) = $sth->fetchrow();
#		$va{'currency_dis'} = qq|disabled="disabled"| if $total; 
#	}


} 


#############################################################################
#############################################################################
#   Function: view_mer_po
#
#       Es: Genera el listado de PO Items/Adjustments
#       En: Build PO Items/Adjustments List 
#
#
#    Created on: 
#
#    Author: _Carlos Haas_
#
#    Modifications:
#
#        - Modified on *2013/03/07* by _Roberto Barcenas_ : El listado de elementos se genera en una funcion
#		 - Modified on *2014/08/22* by _Roberto Barcenas_ : Se corrige el problema con el IVA. Probado en POs de varios items
#		 - Modified on *2015/05/18* by _Roberto Barcenas_ : Se corrige el problema con el IVA en RV. Probado en POs de varios items
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
#      <build_po_list>
#
sub view_mer_po {
#############################################################################
#############################################################################
	## Notify
	my ($sth) = &Do_SQL("SELECT Notes FROM sl_purchaseorders_notes WHERE ID_purchaseorders = '$in{'id_purchaseorders'}' AND Type='Notify' ORDER BY Date,Time DESC LIMIT 1;");
	$va{'notify'} = $sth->fetchrow_array();

	if($in{'amazon_process'})
	{
		&amazon_receipts_process( $in{'id_purchaseorders'}, $in{'id_orders'}, $in{'id_exchangerates'}, $in{'number_tracking'}, $in{'shpdate'} );
		return;
	}


	## Reopen PO
	if($in{'ro'}) {

		if(&check_permissions('mer_po_reopen','','')) {

			my ($sth) = &Do_SQL("SELECT SUM(Received) FROM sl_purchaseorders_items WHERE ID_purchaseorders = '$in{'id_purchaseorders'}';");
			my ($trec) = $sth->fetchrow();

			if(!$trec) {

				my ($sth) = &Do_SQL("UPDATE sl_purchaseorders SET Status='New', Auth='In Process', AuthBy = 0 WHERE ID_purchaseorders = '$in{'id_purchaseorders'}';");
				my ($sth) = &Do_SQL("SELECT AuthBy, Auth, Status FROM sl_purchaseorders WHERE ID_purchaseorders = '$in{'id_purchaseorders'}';");
				($in{'authby'}, $in{'auth'},$in{'status'}) = $sth->fetchrow();
				&auth_logging('mer_po_reopened',$in{'id_purchaseorders'});
			
			}else{
				$va{'message'} = &trans_txt('mer_po_itemsreceived');
			}

		}else {
			$va{'message'} = &trans_txt('perms_insufficient_perms');
		}
	}	

	## Authorization
	if($in{'action'}) { 
		
		### Metodo usado para la salida de inventario. FIFO: Primer entradas primeras salidas | LIFO: Ultimas entradas primeras salidas
		my $acc_method = $cfg{'acc_inventoryout_method'} ? $cfg{'acc_inventoryout_method'} : 'fifo';
		my $invout_order = $acc_method eq 'fifo' ? '' : 'DESC';

		if ($in{'tab'} eq '1') {


			#######################
			#######################
			##### Tab2: SKUs / Supplies
			#######################
			#######################

			$in{'add_row_segment'} = int($in{'add_row_segment'});
			if ($in{'add_row_segment'}){

				if($in{'status'} ne 'New'){
					$va{'message'} = &trans_txt('mer_po_items_segment_blocked');
				}else{

					$in{'id_po_segments'} = int($in{'id_po_segments'});
					($in{'id_po_segments'}) and ($in{'id_segments'} = $in{'id_po_segments'});


					if (!$in{'id_segments'}){
						$va{'message'} = &trans_txt('mer_po_items_segment_null');	
					}else{

						#######
						####### Se Procesa la actualizacion de Segmento
						#######
						&Do_SQL("UPDATE sl_purchaseorders_items SET ID_segments = '$in{'id_segments'}' WHERE ID_purchaseorders_items = '$in{'add_row_segment'}';");
						&auth_logging('mer_po_segment_added',$in{'id_purchaseorders'});
						$va{'message'} = &trans_txt('done');

					}

				}

			}

		}elsif ($in{'tab'} eq '2' and ($in{'status'} eq 'New' or $in{'status'} eq 'In Process')) {

			#######################
			#######################
			##### Tab2: Adjustments
			#######################
			#######################

			$in{'id_extracharges'} = int($in{'id_extracharges'});
			if (!$in{'description'}){
				$error{'description'} = &trans_txt('required');
				++$err;
			}
			if (!$in{'amount'}){
				$error{'amount'} = &trans_txt('required');
				++$err;
			}
			if (!$in{'amount_original'}){
				$error{'amount_original'} = &trans_txt('required');
				++$err;
			}
			if (!$in{'id_extracharges'}){
				$error{'id_extracharges'} = &trans_txt('required');
				++$err;
			}else{
				my ($sth) = &Do_SQL("SELECT Name,ID_accounts FROM sl_extracharges WHERE ID_extracharges = '$in{'id_extracharges'}';");
				($in{'type'}, $in{'id_accounts'}) = $sth->fetchrow_array();
				if (!$in{'id_accounts'}){
					$error{'id_extracharges'} = &trans_txt('required');
					++$err;
				}
				my ($sth) = &Do_SQL("SELECT sl_extracharges.Tax_percent FROM sl_extracharges WHERE sl_extracharges.ID_extracharges = ".$in{'id_extracharges'}.";");
				($in{'tax_percent'}) = $sth->fetchrow_array();
				if ($in{'tax_percent'} eq '') {
					$error{'id_extracharges'} = &trans_txt('notfound')." Tax Percent";
					++$err;
				}

			}
			(!$in{'id_extvendors'}) and ($in{'id_extvendors'} = $in{'id_vendors'});

			##--------------------------------------------------
			## Se validan los montos dependiendo del Currency
			## del Vendor-PO y del Vendor-Adj.
			##--------------------------------------------------
			$currency_vendor_adj	= &load_name('sl_vendors','ID_vendors',$in{'id_extvendors'},'Currency');
			$currency_vendor_po		= &load_name('sl_vendors','ID_vendors',$in{'id_vendors'},'Currency');			
			if (($currency_vendor_adj eq $currency_vendor_po) and ($in{'amount_original'} != $in{'amount'})){
				$error{'amount'} = &trans_txt('invalid');
				$error{'amount_original'} = &trans_txt('invalid');
				++$err;
			}
			##--------------------------------------------------

			if ($err>0){
				$va{'tabmessages'} = &trans_txt('reqfields');
			}else{				
				($in{'tax_percent'} > 1) ? ($in{'tax_percent'} = $in{'tax_percent'} / 100) : ($in{'tax_percent'});
				#($in{'incogs'}) ? ($query = ",InCOGS='Yes'"):($query = ",InCOGS='No'");
				my $InCogs = load_name('sl_extracharges', 'ID_extracharges', $in{'id_extracharges'}, 'InCOGS');
				$query = ",InCOGS='".$InCogs."'";
				my $tax = $in{'amount'} * $in{'tax_percent'};
				my $total = $in{'amount'} + $tax;
				$va{'tabmessages'} = &trans_txt('mer_po_adj_added');
				my $total_original = ( $in{'tax_percent'} > 0 and $in{'amount_original'} > 0 ) ? $in{'amount_original'} * ($in{'tax_percent'} + 1) : 0;
				my ($sth) = &Do_SQL("INSERT INTO sl_purchaseorders_adj SET ID_purchaseorders = '$in{'id_purchaseorders'}', ID_vendors = '$in{'id_extvendors'}', ID_accounts = '$in{'id_accounts'}' $query  , Description = '$in{'description'}', Amount = '$in{'amount'}',  Amount_original = '$in{'amount_original'}', Tax_percent = '$in{'tax_percent'}', Tax = '$tax', Total = '$total', TotalOriginal = '$total_original', Type = '$in{'type'}', Status = 'Active', Date = CURDATE(), Time = CURTIME(), ID_admin_users = '$usr{'id_admin_users'}';");
				delete($in{'description'});
				delete($in{'amount'});
				delete($in{'amount_original'});
				delete($in{'tax_percent'});
				$va{'searchresults'} .= "<script language=\"JavaScript1.2\">\ntrjump('/cgi-bin/mod/$usr{'application'}/dbman?cmd=mer_po&view=$in{'id_purchaseorders'}&tab=2&tabmessages=$va{'tabmessages'}')\n</script>";
				&auth_logging('mer_po_adj_added',$in{'id_purchaseorders'});
			}

		}elsif ($in{'tab'} eq '4') {

			#######################
			#######################
			##### Tab4: Authorization
			#######################
			#######################

			if ((!$in{'notes'} or !$in{'notestype'}) and !$in{'edit'}){

				$va{'message'} = &trans_txt('reqfields_short');
				$va{'tabmessages'} = &trans_txt('reqfields_short');

			}else{

				###
				### Valida los segmentos de cada item para los POs de Servicios
				###
				my $valid_segments = 1;
				if ($in{'type'} eq 'PO Services'){
					my $sth = &Do_SQL("SELECT COUNT(*) Invalid
										FROM sl_purchaseorders_items
										WHERE ID_purchaseorders = ".int($in{'id_purchaseorders'})." 
											AND (ID_segments = 0 OR ID_segments IS NULL);");
					my $result = $sth->fetchrow();
					if( $result > 0 ){
						$valid_segments = 0;
						$va{'message'} = &trans_txt('mer_po_items_segment_null');
					}
				}

				#########################
				#########################
				##### Note Insert
				#########################
				#########################

				my($sth) = &Do_SQL("SELECT Status FROM sl_purchaseorders WHERE id_purchaseorders='$in{'id_purchaseorders'}'");
				$status = $sth->fetchrow;						
				if ($status eq "New" and $valid_segments == 1){
					my ($sth) = &Do_SQL("INSERT INTO sl_purchaseorders_auth SET id_purchaseorders='$in{'id_purchaseorders'}',Notes='".&filter_values($in{'notes'})."',Type='$in{'notestype'}',Date=CURDATE(),Time=CURTIME(),ID_admin_users='$usr{'id_admin_users'}'");
					&auth_logging('mer_purchaseorder_auth_noteadded',$in{'id_purchaseorders'});
				}


				if ($in{'finaldec'} and $status eq "New" and $valid_segments == 1){

					#########################
					#########################
					##### Declined / Approved
					#########################
					#########################

					if ($in{'notestype'} eq 'Approved'){

						my (@id_products, %ids, $num);
						if ($in{'type'} eq 'Return to Vendor'){

							#####################
							#####################
							##### RVendor Validation
							#####################
							#####################

							if (!$in{'id_warehouses_rvendor'}) {
								$va{'tabmessages'} = &trans_txt('mer_po_idwh_missing');
							}elsif (!$in{'id_purchaseorders_rvendor'}) {
								$va{'tabmessages'} = &trans_txt('mer_po_idpo_missing');
							}elsif (!$in{'currency_exchange'}) {
								$va{'tabmessages'} = &trans_txt('mer_po_currency_missing');	
							}else{

								my $currency_exchange = $in{'currency_exchange'};
								my $acc_method = $cfg{'acc_inventoryout_method'} ? $cfg{'acc_inventoryout_method'} : 'fifo';
								my $invout_order = $acc_method eq 'fifo' ? '' : 'DESC';

								my ($sth) = &Do_SQL("SELECT 
									ID_purchaseorders_items
									, sl_purchaseorders_items.ID_products
									, sl_purchaseorders_items.Qty
									, Total - Tax AS Price
									, Tax
								FROM sl_purchaseorders 
								INNER JOIN sl_purchaseorders_items USING(ID_purchaseorders)
								WHERE sl_purchaseorders.ID_purchaseorders = '$in{'id_purchaseorders'}'
								ORDER BY ID_purchaseorders_items;");

								$debug = '';
								while (my($id_purchaseorders_items, $id_products, $qty, $total, $tax) = $sth->fetchrow() ) {
								# , $idwl, $wlqty

									# if ($id_purchaseorders_items) {

									# 	++$num;
									# 	push(@id_products,$id_purchaseorders_items);
									# 	$ids{$num}[0] = $id_purchaseorders_items;
									# 	$ids{$num}[1] = $id_products;

									# 	if (!$idwl) { 
									# 		$ids{$num}[2] = 'ERROR';
									# 		$ids{$num}[3] = qq|<li>|. &trans_txt('mer_po_rvendor_wlnoitem') .qq| $id_products</li>|;
									# 	}elsif ($wlqty < $qty){
									# 		$ids{$num}[2] = 'ERROR';
									# 		$ids{$num}[3] = qq|<li>|. &trans_txt('mer_po_rvendor_wlinsufficient') .qq| $id_products</li>|;
									# 	}else{
									# 		$ids{$num}[2] = $idwl;
									# 		$ids{$num}[3] = $qty;
									# 		$ids{$num}[4] = $total;
									# 		$ids{$num}[5] = $tax;
									# 		$ids{$num}[6] = $currency_exchange;
									# 	}


									# }

									++$num;
									push(@id_products,$id_purchaseorders_items);
									$ids{$num}[0] = $id_purchaseorders_items;
									$ids{$num}[1] = $id_products;
									$ids{$num}[4] = $total;
									$ids{$num}[5] = $tax;
									$ids{$num}[6] = $currency_exchange;
									$ids{$num}[3] = $qty;

									my ($sth_wl) = &Do_SQL("SELECT ID_warehouses_location, Quantity
									FROM sl_warehouses_location 
									WHERE sl_warehouses_location.ID_products = '$id_products'
									AND sl_warehouses_location.ID_warehouses = '$in{'id_warehouses_rvendor'}' 
									AND sl_warehouses_location.Location = 'pack'
									ORDER BY sl_warehouses_location.Date $invout_order, sl_warehouses_location.Time $invout_order;");
									my $i=0;
									while ($rec_wl = $sth_wl->fetchrow_hashref()) {

										if ($left_qty > 0){											
											if ($left_qty <= $rec_wl->{'Quantity'}){
												$left_qty = 0;
											}else{
												$left_qty = $left_qty - $rec_wl->{'Quantity'};
											}
										}
									}
									
									if ($left_qty > 0){
										$ids{$num}[2] = 'ERROR';
										$ids{$num}[3] = qq|<li>|. &trans_txt('mer_po_rvendor_wlinsufficient') .qq| $id_products</li>|;
									}
								}

								##############################
								##############################
								####### After Lines validation
								##############################
								##############################

								if (!$num){
									$va{'message'} = &trans_txt('mer_po_rvendor_nolines');
								}else{

									################################
									################################
									## Check for Errors in Lines
									################################
									################################

									my $okskus = 0;
									my $nookskus = 0;
									my $line_errors;
									for my $i(1..$num) {

									    if ($ids{$i}[2] eq 'ERROR'){
										    $line_errors .=  $ids{$i}[3];
										    $nookskus++;
									    }else{
									    	$okskus++;
									    } 

									}
									($nookskus) and ($va{'message'} .= qq|<ul>$line_errors</ul>|);

								}#### Else After Validation
							}
						}


						if (!$va{'tabmessages'} and (!$va{'message'} or ($okskus and $cfg{'wreturn_partial_errors'})) ) {

							my $errors_found = 0;
							my $message_errors_found = '';
							my $modstatus = "'In Process'";
							my $log ="DEBUG Return to Vendor\n\n";
							if ($in{'type'} eq 'Return to Vendor'){
								&Do_SQL("START TRANSACTION");

								########################
								########################
								####### RVendor SKUs out
								########################
								########################

								my $sum_price = 0;
								for my $i(1..$num) {
							
									my $sum_tax = 0; 
					    			my $sum_cost = 0;

					    			if ($ids{$i}[2] ne 'ERROR'){

					    				my $id_purchaseorders_items = $ids{$i}[0];
					    				my $id_products = $ids{$i}[1];
					    				my $id_warehouses = $in{'id_warehouses_rvendor'};
					    				my $currency_exchange = $ids{$i}[6] > 0 ? $ids{$i}[6] : 1;
					    				my $idwl = $ids{$i}[2];
								    	my $qty = $ids{$i}[3];
								    	my $price = round($ids{$i}[4] * $currency_exchange,2);
								    	my $tax = round($ids{$i}[5] * $currency_exchange,2);
								    	my $cost = round($price,2);


								    	$sum_price += round($ids{$i}[4] + $ids{$i}[5],2);

								    	##########
								    	########## Product Tax PCT
								    	##########
								    	$sql = "SELECT Tax_percent FROM sl_purchaseorders_items WHERE ID_purchaseorders = '$in{'id_purchaseorders_rvendor'}' AND ID_products = '$id_products' AND Received >= '$qty';";
								    	$log .= $sql."\n\n";
								    	my ($sth) = &Do_SQL($sql);
								    	my ($tax_percent) = $sth->fetchrow();

								    	##########
								    	########## Nota acerca del ID_purchaseorders del que se devuelve
								    	##########
								    	$sql = "INSERT INTO sl_purchaseorders_notes SET ID_purchaseorders = '$in{'id_purchaseorders'}', Notes ='Return to Vendor of Purchase Order: $in{'id_purchaseorders_rvendor'}', Type = 'High', Date = CURDATE(), Time = CURTIME(), ID_admin_users = '$usr{'id_admin_users'}';";
								    	$log .= $sql."\n\n";
								    	&Do_SQL($sql);


								    	###########################
										### sl_warehouses_location
										###########################
										$diff_wh = $qty;
										$sql = "SELECT 
										ID_warehouses_location
										, Quantity
										, ID_customs_info
										FROM sl_warehouses_location 
										WHERE sl_warehouses_location.ID_products = '$id_products'
										AND sl_warehouses_location.ID_warehouses = '$id_warehouses' 
										AND sl_warehouses_location.Location = 'pack'
										ORDER BY sl_warehouses_location.Date $invout_order, sl_warehouses_location.Time $invout_order;";
								    	$log .= $sql."\n\n";
								    	my ($sth_wl) = &Do_SQL($sql);
										my $i=0;
										while ($rec_wl = $sth_wl->fetchrow_hashref()) {

											if ($diff_wh > 0){
												my $qty_processed=0;

												if ($rec_wl->{'Quantity'} > $diff_wh){
													$sql = "/* return to vendor */UPDATE sl_warehouses_location SET Quantity = Quantity - $diff_wh WHERE ID_warehouses_location = '$rec_wl->{'ID_warehouses_location'}';";
													$log .= $sql."\n\n";
													&Do_SQL($sql);
													$qty_processed = $rec_wl->{'Quantity'} - ($rec_wl->{'Quantity'} - $diff_wh);
												}else{
													$sql = "/* return to vendor */DELETE FROM sl_warehouses_location WHERE ID_warehouses_location = '$rec_wl->{'ID_warehouses_location'}';";
													$log .= $sql."\n\n";
													&Do_SQL($sql);
													$qty_processed = $rec_wl->{'Quantity'};
												}
												$diff_wh -= $rec_wl->{'Quantity'};
												$diff_cost = $qty_processed;

												###########################
												### sl_skus_cost
												###########################
												$sql = "SELECT 
												ID_skus_cost, Quantity, Cost, Cost_Adj, Cost_Add
												FROM sl_skus_cost
												WHERE ID_warehouses = '$id_warehouses' 
												AND ID_products = '$id_products' 
												AND Quantity > 0 
												AND Cost > 0 
												ORDER BY Date $invout_order, Time $invout_order;";
												$log .= $sql."\n\n";
												my ($sth3) = &Do_SQL($sql);
												while (my $rec_cost = $sth3->fetchrow_hashref){

													if ($diff_cost > 0){
														###########################
														### Costo Promedio
														###########################
														if ($cfg{'acc_inventoryout_method_cost'} and lc($cfg{'acc_inventoryout_method_cost'}) eq 'average'){
															($rec_cost->{'Cost'}, $rec_cost->{'Cost_Adj'}, $rec_cost->{'Cost_Add'}) = &load_last_purchase_cost($id_products, $in{'id_purchaseorders_rvendor'});
															$log .= "cost_avg=".$rec_cost->{'Cost'}."<br>\n";
															$log .= "cost_adj=".$rec_cost->{'Cost_Adj'}."<br>\n";
															$log .= "cost_add=".$rec_cost->{'Cost_Add'}."<br>\n";
														}

														if (!$rec_cost->{'Cost'}) {
															$errors_found++;
															$message_errors_found .= &trans_txt('mer_po_cost_cero')."<br>";
															$log .= "$id_warehouses->$id_products ".($qty - $diff_wh)." < $qty"."\n\n";
														}

														$pcost += $rec_cost->{'Cost'};
														$qty_processed = 0;

														if ($rec_cost->{'Quantity'} > $diff_cost){
															$sql = "UPDATE sl_skus_cost SET Quantity = Quantity - $diff_cost WHERE ID_skus_cost = '$rec_cost->{'ID_skus_cost'}' LIMIT 1;";
															$log .= $sql."\n\n";
															&Do_SQL($sql);
															$qty_processed = $rec_cost->{'Quantity'} - ($rec_cost->{'Quantity'} - $diff_cost);
														}else{
															$sql = "DELETE FROM sl_skus_cost WHERE ID_skus_cost = '$rec_cost->{'ID_skus_cost'}' LIMIT 1;";
															$log .= $sql."\n\n";
															&Do_SQL($sql);
															$qty_processed = $rec_cost->{'Quantity'};
														}
														$diff_cost -= $rec_cost->{'Quantity'};

														$skcost *= $qty_processed;
														$sum_cost += $skcost;
														
														###########################
														### sl_skus_trans
														###########################
														&sku_logging($id_products, $id_warehouses, 'pack', 'Return to Vendor', $in{'id_purchaseorders'}, 'sl_purchaseorders', $qty_processed, $rec_cost->{'Cost'}, $rec_cost->{'Cost_Adj'}, "OUT", $rec_wl->{'ID_customs_info'}, $rec_cost->{'Cost_Add'});
														$log .= qq|sku_logging($id_products, $id_warehouses, 'pack', 'Return to Vendor', $in{'id_purchaseorders'}, 'sl_purchaseorders', $qty_processed, $rec_cost->{'Cost'}, $rec_cost->{'Cost_Adj'}, "OUT", $rec_wl->{'ID_customs_info'}, $rec_cost->{'Cost_Add'})|."<br>\n\n";

													}
												}
											}
										}

										if ($diff_wh > 0 or $diff_cost > 0){
											$errors_found++;
											$message_errors_found .= "$id_warehouses->$id_products ".($qty - $diff_wh)." < $qty<br>";
											$log .= "$id_warehouses->$id_products ".($qty - $diff_wh)." < $qty"."\n\n";
										}
										
										####
										#### 3) Calculamos el Tax
										####
										( $tax_percent > 0 ) and ( $sum_tax = round($sum_cost * $tax_percent,3) );
										
										#########################
								    	#########################
								    	###### 4) Accounting Movements
								    	#########################
								    	#########################
								    	my $ptype = &load_name('sl_vendors','ID_vendors',$in{'id_vendors'},'Category');
								    	$ptype = 'nacional' if !$ptype;
								    	### Se comenta linea siguiente para enviar $price y $tax extraidos del PO Nuevo
								    	#my @params = ($in{'id_purchaseorders_rvendor'},$in{'id_purchaseorders'},$sum_cost,$sum_tax);
								    	my @params = ($in{'id_purchaseorders_rvendor'},$in{'id_purchaseorders'},$price,$tax);
										&accounting_keypoints('po_rvendor_'. lc($ptype), \@params );
										$log .= "accounting_keypoints('po_rvendor_'. lc($ptype), [$in{'id_purchaseorders_rvendor'},$in{'id_purchaseorders'},$price,$tax] )\n\n";

										# $sql = "/*  $skcost */INSERT INTO sl_purchaseorders_notes SET ID_purchaseorders = '$in{'id_purchaseorders'}', Notes ='T1\nWarehouse: ".&load_name('sl_warehouses','ID_warehouses',$in{'id_warehouses'},'Name')."($in{'id_warehouses'})\nID: $id_products\nQty: $qty\nCurrency:$currency_exchange\nCost:".$price."\nTotal Cost:".round($price * $qty,2)."\nTax:". ( ($price * $qty) * $tax_percent) ."', Type = 'Low', Date = CURDATE(), Time = CURTIME(), ID_admin_users = '$usr{'id_admin_users'}';";
										$sql = "/*  $skcost */INSERT INTO sl_purchaseorders_notes SET ID_purchaseorders = '$in{'id_purchaseorders'}', Notes ='T1\nWarehouse: ".&load_name('sl_warehouses','ID_warehouses',$in{'id_warehouses'},'Name')."($in{'id_warehouses'})\nID: $id_products\nQty: $qty\nCurrency:$currency_exchange\nTotal:$price\nTax:". ( ($price * $qty) * $tax_percent) ."', Type = 'Low', Date = CURDATE(), Time = CURTIME(), ID_admin_users = '$usr{'id_admin_users'}';";
										$log .= $sql."\n\n";
										&Do_SQL($sql);
										
										$modstatus = "'Paid'";
										$in{'status'} = 'Paid';

					    			}

					    		}### For each item 		

					    		#########################
						    	#########################
						    	###### 5) Bill Credit
						    	#########################
						    	#########################
						    	my $currency = &load_name('sl_vendors','ID_vendors',$in{'id_vendors'},'Currency');
						    	my ($sth) = &Do_SQL("INSERT INTO sl_bills SET ID_vendors = '$in{'id_vendors'}', Type = 'Credit', Currency = '$currency', currency_exchange = '". filter_values($in{'currency_exchange'}) ."', Amount = '$sum_price', BillDate = CURDATE(), DueDate = CURDATE(), AuthBy = '$usr{'id_admin_users'}', PaymentMethod = 'Wire Transfer', Memo = 'PO Original: ". int($in{'id_purchaseorders_rvendor'}) ."', Status = 'New', Date = CURDATE(), Time = CURTIME(), ID_admin_users = '$usr{'id_admin_users'}';");
						    	my $new_bill = $sth->{'mysql_insertid'};

						    	if($new_bill){
						   
						    		###
						    		### 5.1) ligamos el Bill a un expense y a un PO
						    		###
						    		my ($sth) = &Do_SQL("SELECT ID_accounts FROM sl_movements WHERE tableused = 'sl_purchaseorders' AND ID_tableused = '". int($in{'id_purchaseorders_rvendor'}) ."' AND tablerelated = 'sl_purchaseorders' AND ID_tablerelated = '". int($in{'id_purchaseorders'}) ."' AND Credebit = 'Debit' AND Status = 'Active' AND TIMESTAMPDIFF(SECOND, CONCAT(Date,' ',Time) , NOW()) BETWEEN 0 AND 30;");
						    		my ($ida_expenses) = $sth->fetchrow();
						    		&Do_SQL("INSERT INTO sl_bills_expenses SET ID_bills = '$new_bill', ID_accounts = '$ida_expenses', Amount = '". $sum_price ."', ID_segments = '0', Related_ID_bills_expenses = '0', Deductible = 'No', Date = CURDATE(), Time = CURTIME(), ID_admin_users = '$usr{'id_admin_users'}';");
						    		&Do_SQL("INSERT INTO sl_bills_pos SET ID_bills = '$new_bill', ID_purchaseorders = '". $in{'id_purchaseorders'} ."', Amount = '". $sum_price ."', Date = CURDATE(), Time = CURTIME(), ID_admin_users = '$usr{'id_admin_users'}';");

						    		###
						    		### 5.2) Nota en Bill y PO
						    		###
						    		&Do_SQL("INSERT INTO sl_bills_notes SET ID_bills = '$new_bill', Notes = 'Automatic Credit Originated From RVendor: $in{'id_purchaseorders'}', Type = 'Low', Date = CURDATE(), Time = CURTIME(), ID_admin_users = '$usr{'id_admin_users'}';");
						    		&Do_SQL("INSERT INTO sl_purchaseorders_notes SET ID_purchaseorders = '$in{'id_purchaseorders'}', Notes ='New Credit Bill Created: $new_bill', Type = 'Low', Date = CURDATE(), Time = CURTIME(), ID_admin_users = '$usr{'id_admin_users'}';");

						    		###
						    		### 5.3) Ligamos el nuevo Bill con el PO contablemente
						    		###
						    		&Do_SQL("UPDATE sl_movements SET tablerelated = 'sl_bills', ID_tablerelated = '$new_bill' WHERE ID_tableused = '". $in{'id_purchaseorders'} ."' AND tableused = 'sl_purchaseorders' AND (tablerelated IS NULL OR tablerelated = '') AND (ID_tablerelated IS NULL OR ID_tablerelated = 0) AND TIMESTAMPDIFF(SECOND, CONCAT(Date,' ',Time) , NOW()) BETWEEN 0 AND 20;");

						    	}
						    	
						    	### Nota en Purchase Order
						    	my($sth) = &Do_SQL("INSERT INTO sl_purchaseorders_notes SET ID_purchaseorders = '$in{'id_purchaseorders'}', Notes ='$in{'id_purchaseorders_rvendor'}', Type = 'RVendor', Date = CURDATE(), Time = CURTIME(), ID_admin_users = '$usr{'id_admin_users'}';");

							} ### Return to Vendor


							########################
							########################
							####### Authorization Aplication
							########################
							########################
							my ($sth) = &Do_SQL("UPDATE sl_purchaseorders SET Auth='Approved',Status = $modstatus ,AuthBy='$usr{'id_admin_users'}' WHERE id_purchaseorders='$in{'id_purchaseorders'}'");

					    	if ($errors_found){
					    		&Do_SQL("ROLLBACK");
					    		$va{'message'} = $message_errors_found;
					    	}else{
					    		# &Do_SQL("ROLLBACK"); ## Debug only
					    		&Do_SQL("COMMIT");
								$in{'auth'} = 'Approved';
								$in{'status'} = 'In Process';
								$va{'message'} = &trans_txt('mer_po_auth_processed');
					    	}

					    	&Do_SQL("INSERT INTO sl_debug (cmd, id, log, Date, Time, ID_admin_users) VALUES ('Return to Vendor', '$in{'id_purchaseorders'}', '".$va{'message'}."\n\n".&filter_values($log)."', CURDATE(), CURTIME(), '$usr{'id_admin_users'}');");

						}

					}else{

						my ($sth) = &Do_SQL("UPDATE sl_purchaseorders SET Auth='Declined',Status='Cancelled',AuthBy='$usr{'id_admin_users'}' WHERE id_purchaseorders='$in{'id_purchaseorders'}'");
						$in{'auth'} = 'Declined';
						$in{'status'} = 'Cancelled';

					} ### Else Approved


					$in{'authby'} = $usr{'id_admin_users'};
					&auth_logging('mer_purchaseorder_auth_final',$in{'id_purchaseorders'});

				} ## Final Decision	

				delete($in{'notes'});
				delete($in{'notestype'});
			}

		}elsif($in{'tab'} eq '6') {

			#######################
			#######################
			##### Tab6: W.Receipt - Only for Non Inventory Merchandise
			#######################
			#######################
			my $rate = 1;
			my ($sth) = &Do_SQL("SELECT Category FROM sl_vendors INNER JOIN sl_purchaseorders USING(ID_vendors) WHERE ID_purchaseorders = '$in{'id_purchaseorders'}';");
			my ($vendor_category) = $sth->fetchrow();

			if($in{'wreceipt_noninventory'}) {
			
				my $exchange = 1;
				my $currency = &load_name('sl_vendors', 'ID_vendors', $in{'id_vendors'}, 'Currency');

				if ($in{'dateexchange'} eq '' and $cfg{'acc_default_currency'} ne $currency){
					$va{'message'} = &trans_txt('mer_po_currency_required');				
					
				}elsif ($cfg{'acc_default_currency'} ne $currency){
					my ($sth) = &Do_SQL("SELECT * FROM sl_exchangerates WHERE Date_exchange_rate = '".&filter_values($in{'dateexchange'})."'"); 
					my ($rec) = $sth->fetchrow_hashref;
					$exchange = $rec->{'exchange_rate'};
					$rate = $rec->{'exchange_rate'};					
				}

				if ($exchange > 0 and !$va{'message'}){
				
					my $rec = 0;
					my ($sth) = &Do_SQL("SELECT ID_purchaseorders_items, ID_products, PurchaseID_accounts, (Qty - Received) AS MaxRec, Name, Price, Tax_percent FROM sl_purchaseorders_items INNER JOIN sl_noninventory ON ID_noninventory = ID_products - 500000000 WHERE ID_purchaseorders = '$in{'id_purchaseorders'}' AND Status = 'Active' AND Qty - Received > 0 ORDER BY ID_purchaseorders_items;");
					LINE: while(my ($idpoi,$id_products,$ida_debit,$maxrec,$pname,$price,$tax_pct) = $sth->fetchrow()) {
						my $originalPrice = $price;
						$price = $price * $rate;
						if( $in{'id_purchaseorders_items_' . $idpoi } ) {

							my $to_receive = int($in{'id_purchaseorders_items_' . $idpoi });

							if( $to_receive <= $maxrec ) {

								if(!$ida_debit) { 
									$va{'message'} .= "ID: $id_products " . &trans_txt('mer_po_noninventory_accouting_missing') . "<br>";
									next LINE;
								}

								&Do_SQL("UPDATE sl_purchaseorders_items SET Received = Received + $to_receive WHERE ID_purchaseorders_items = '$idpoi';");
								&Do_SQL("INSERT INTO sl_purchaseorders_notes SET ID_purchaseorders = '$in{'id_purchaseorders'}', Notes = 'Warehouse Receipt\nProduct: ". &filter_values($pname) ." (". &format_sltvid($id_products) .")\nReceived: $to_receive\nPrice: ".&format_price($originalPrice)."\nPayment Date: ".&filter_values($in{'dateexchange'})."\nExchange Rate: ".&format_price($rate)."', Type = 'High', Date = CURDATE(), Time = CURTIME(), ID_admin_users = '$usr{'id_admin_users'}';");
								&auth_logging('mer_po_noninventory_received',$in{'id_purchaseorders'});
								$rec++;

								########################################################
								########################################################
								##  Movimientos de contabilidad
								########################################################
								########################################################
								my $this_price = round($to_receive * $price,2);
								my $this_tax = $tax_pct > 0 ? round($to_receive * $price * $tax_pct,2) : 0;
								my @params = ($in{'id_purchaseorders'},$idpoi,$id_products,$ida_debit,$this_price,$this_tax);
								&accounting_keypoints('po_noninventory_in_'. lc($vendor_category), \@params );

							}

						}

					}
					my ($sth) = &Do_SQL("SELECT IF(SUM(Qty) - SUM(Received) = 0 ,1,0)AS ToRec FROM sl_purchaseorders_items WHERE ID_purchaseorders = '$in{'id_purchaseorders'}';");
					my ($full_received) = $sth->fetchrow();

					if($full_received){
						&Do_SQL("UPDATE sl_purchaseorders SET Status = 'Received' WHERE ID_purchaseorders = '$in{'id_purchaseorders'}';");
						&auth_logging('mer_po_received',$in{'id_purchaseorders'});
					}

					($rec) and ($va{'tabmessages'} .= &trans_txt('done'));
				}else{
					$va{'tabmessages'} .= 'There is no exchange rate for the selected date';
				}
			}			
		} #### Tab 6

		if( int($in{'chgto_authrequest'}) == 1 ){
			
			### Si el PO está con los status correctos, se procede con el cambio
			if( ($in{'status'} eq 'New' and $in{'auth'} eq 'In Process') or (int($in{'authreceipt'}) == 0 and int($in{'final_auth'}) == 1) ){

				###
				### Valida los segmentos de cada item para los POs de Servicios
				###
				my $valid_segments = 1;
				if ($in{'type'} eq 'PO Services' and !$in{'final_auth'}){
					my $sth = &Do_SQL("SELECT COUNT(*) Invalid
										FROM sl_purchaseorders_items
										WHERE ID_purchaseorders = ".int($in{'id_purchaseorders'})." 
											AND (ID_segments = 0 OR ID_segments IS NULL);");
					my $result = $sth->fetchrow();
					if( $result > 0 ){
						$valid_segments = 0;
						$va{'message'} = &trans_txt('mer_po_items_segment_null');
					}
				}

				if( int($valid_segments) > 0 ){
					### Se obtienen los datos del autorizador
					my $sth = &Do_SQL("SELECT admin_users.ID_admin_users, admin_users.FirstName, admin_users.LastName, admin_users.MiddleName, admin_users.Email
										FROM cu_admin_users_rel 
											INNER JOIN admin_users ON cu_admin_users_rel.ID_admin_users_rel1 = admin_users.ID_admin_users 
										WHERE cu_admin_users_rel.ID_admin_users_main = ".$usr{'id_admin_users'}." 
											AND Type_rel = 'Authorization'
										LIMIT 1;");
					my ($id_admin_auth, $firstname, $lastname, $middlename, $email) = $sth->fetchrow_array();
					if( int($id_admin_auth) and $email ne '' ){
						use utf8;
						binmode(STDOUT, ":utf8");

						my $authorizer = $id_admin_auth.' - '.$lastname.' '.$middlename.' '.$firstname;

						#### Se genera el hash para la validación de la autorización
						my $vars_def_en = ''; 
						$va{'auth_phase'} = '<span style="display: block; font-size: 11pt;">(Primera Revisi&oacute;n)</span>';
						if(int($in{'final_auth'}) == 1){
							$vars_def_en = ", Definition_En = 'FinalAuth'";
							$va{'auth_phase'} = '<span style="display: block; font-size: 11pt;">(Autorizaci&oacute;n Final)</span>';
							### Se solicita la segunda autorización para recepcion al creador del PO
							my $usr = &Do_SQL("SELECT ID_admin_users, FirstName, LastName, MiddleName, Email FROM admin_users WHERE ID_admin_users = ".$in{'id_admin_users'}.";");
							my $usr_dat = $usr->fetchrow_hashref();

							$email = $usr_dat->{'Email'};
							$authorizer = $usr_dat->{'ID_admin_users'}.' - '.$usr_dat->{'LastName'}.' '.$usr_dat->{'MiddleName'}.' '.$usr_dat->{'FirstName'};
						}
						my $sth_hsh = &Do_SQL("SELECT UPPER(SHA1('".$in{'id_purchaseorders'}.int($in{'final_auth'})."'));");
						$in{'hash'} = $sth_hsh->fetchrow();
						&Do_SQL("INSERT INTO sl_vars SET 
									VName = 'po_services_auth'
									, VValue='".$in{'hash'}."'
									, Subcode='".$in{'id_purchaseorders'}."|".$usr{'id_admin_users'}."|".$id_admin_auth."'
									, Expiration = DATE_ADD(NOW(), INTERVAL 3 DAY)
									$vars_def_en
								 ;");

						#### Datos para el template del email						
						$va{'vendor_name'} = &load_db_names('sl_vendors','ID_vendors',$in{'id_vendors'},'[CompanyName]<br>[address] [city] <br>[state] [zip]');
						$va{'segment_name'} = load_name('sl_accounts_segments','ID_accounts_segments',$in{'id_segments'},'Name');

						my $sth_items = &Do_SQL("SELECT sl_services.ID_services
													, sl_services.Name AS ServiceName
													, sl_accounts_segments.Name AS SegmentName
													, sl_purchaseorders_items.Qty
													, sl_purchaseorders_items.Price
													, sl_purchaseorders_items.Tax_percent
													, sl_purchaseorders_items.Tax
													, (sl_purchaseorders_items.Qty * sl_purchaseorders_items.Price) AS STotal
													, sl_purchaseorders_items.Total
												FROM sl_purchaseorders_items
													INNER JOIN sl_services ON RIGHT(sl_purchaseorders_items.ID_products, 4) = sl_services.ID_services
													INNER JOIN sl_accounts_segments ON sl_purchaseorders_items.ID_segments = sl_accounts_segments.ID_accounts_segments
												WHERE sl_purchaseorders_items.ID_purchaseorders = ".int($in{'id_purchaseorders'}).";");
						$va{'po_items_list'} = '';
						while( my $rec = $sth_items->fetchrow_hashref() ){
							$va{'po_items_list'} .= '<tr>';
							$va{'po_items_list'} .= '<td style="font-weight: normal; padding: 3px 5px;">'.&format_sltvid(600000000+$rec->{'ID_services'}).'  '.$rec->{'ServiceName'}.'</td>';
							$va{'po_items_list'} .= '<td style="font-weight: normal; padding: 3px 5px;">'.$rec->{'SegmentName'}.'</td>';
							$va{'po_items_list'} .= '<td style="font-weight: normal; padding: 3px 5px; text-align: right;">'.$rec->{'Qty'}.'</td>';
							$va{'po_items_list'} .= '<td style="font-weight: normal; padding: 3px 5px; text-align: right;">'.&format_price($rec->{'Price'}).'</td>';
							$va{'po_items_list'} .= '<td style="font-weight: normal; padding: 3px 5px; text-align: right;">'.round($rec->{'Tax_percent'} * 100, 2).'</td>';
							$va{'po_items_list'} .= '<td style="font-weight: normal; padding: 3px 5px; text-align: right;">'.&format_price($rec->{'STotal'}).'</td>';
							$va{'po_items_list'} .= '<td style="font-weight: normal; padding: 3px 5px; text-align: right;">'.&format_price($rec->{'Tax'}).'</td>';
							$va{'po_items_list'} .= '<td style="font-weight: normal; padding: 3px 5px; text-align: right;">'.&format_price($rec->{'Total'}).'</td>';
							$va{'po_items_list'} .= '</tr>';

							$va{'posubtot'} += $rec->{'STotal'};
							$va{'potottax'} += $rec->{'Tax'};
							$va{'pototal'} += $rec->{'Total'};
						}
						$va{'posubtot'} = &format_price($va{'posubtot'});
						$va{'potottax'} = &format_price($va{'potottax'});
						$va{'pototal'} = &format_price($va{'pototal'});

						### Se envia el correo de solicitud para la autorización
						my $from_email = $cfg{'from_email_info'};
						my $to_email = $email;
						my $subject = $cfg{'app_title'}.' - Autorización para Orden de Compra';
						$va{'maindomain'} = $cfg{'maindomain'};
						my $html_body = &build_page('emails/po_auth_request.html');

						#### Se envia el email...
						$rslt_mail = &send_mandrillapp_email_attachment($from_email, $to_email, $subject, $html_body, 'none', 'none');

						#if( $rslt_mail ){

							### Se crea la nota
							&Do_SQL("INSERT INTO sl_purchaseorders_notes SET ID_purchaseorders = ".$in{'id_purchaseorders'}.", Notes='Status updated: Send  auth request for $authorizer', `Type`='High', Date=CURDATE(), Time=CURTIME(), ID_admin_users=".$usr{'id_admin_users'}.";");

							### Se modifica el Status del PO
							&Do_SQL("UPDATE sl_purchaseorders SET Status = 'Auth Request' WHERE id_purchaseorders='$in{'id_purchaseorders'}'");
							$in{'status'} = 'Auth Request';

							&auth_logging('mer_po_auth_request',$in{'id_purchaseorders'});

							$va{'message'} .= &trans_txt('Send auth request');
						#}
					} else {
						$va{'message'} .= &trans_txt('usrman_authorizer_unassigned');
					}
				}

			} else {
				$va{'message'} .= &trans_txt('mer_po_blocked_rs');
			}

		}

	} #### Action
	
	my ($sth) = &Do_SQL("select concat(firstname,' ',lastname)as name,homephone,homefax,email from sl_purchaseorders inner join admin_users USING(ID_admin_users) where sl_purchaseorders.ID_purchaseorders='$in{'id_purchaseorders'}';");
	($va{'ctc'},$va{'ctc_tel'},$va{'ctc_fax'},$va{'ctc_email'}) = $sth->fetchrow_array();

	my ($sth) = &Do_SQL("SELECT CONCAT(Firstname, ' ',LastName1, ' ', LastName2)Name,Phone,Fax,Email FROM sl_vendors_contacts WHERE id_vendors='$in{'id_vendors'}';");
	($va{'vcontact'},$va{'vcontact_tel'},$va{'vcontact_fax'},$va{'vcontact_email'}) = $sth->fetchrow_array();

	## Status
	## Reopen PO Link
	my ($sth) = &Do_SQL("SELECT SUM(Received) FROM sl_purchaseorders_items WHERE ID_purchaseorders = '$in{'id_purchaseorders'}';");
	my ($trec) = $sth->fetchrow();
	my $authby = &load_name('sl_purchaseorders','ID_purchaseorders',$in{'id_purchaseorders'},'AuthBy');
	
	if( ($authby and $in{'type'} eq 'Purchase Order' and &check_permissions('mer_po_reopen','','') and !$trec) or
		($in{'type'} eq 'Purchase Order' and $in{'status'} eq 'Received' or ($in{'type'} eq 'Purchase Order' and $in{'status'} eq 'New' and $in{'closepo'} == 1)) or
		($authby and $in{'type'} eq 'PO Services' and &check_permissions('mer_po_reopen','','') and !$trec)
	 ){
		$va{'reopen'} .= '&nbsp;  <a href="/cgi-bin/mod/'.$usr{'application'}.'/dbman?cmd=mer_po&view='.$in{'id_purchaseorders'}.'&ro=1"><img src="/sitimages/default/reload.png" title="'.trans_txt('mer_po_reopen').'"></a>';
		if( $in{'id_vendors'} eq $cfg{'amazon_vendor'} and  &check_permissions('amazon_receipt','','')){

			my ($sth) = &Do_SQL("	SELECT sl_orders.id_orders, sl_orders.date, sl_orders.time FROM sl_orders inner join sl_orders_products on sl_orders.ID_orders= sl_orders_products.ID_orders
									WHERE sl_orders.status in ('New','Processed','Pending') AND NOT ISNULL(sl_orders_products.Amazon_ID_products)
									GROUP BY sl_orders.id_orders ORDER BY sl_orders.id_orders DESC;");
			while ($rec = $sth->fetchrow_hashref)
			{
				$va{'orders_options'} .= "<option value=\"$rec->{'id_orders'}\">$rec->{'id_orders'} - $rec->{'date'} $rec->{'time'} </option>\n";
			}
			$va{'currency_options'} = &build_select_exchangerate($in{'id_exchangerates'},'US$');
			$va{'amazon_process'} = "Receipt Amazon's Products <a href='javascript:return false();' class='scroll' onclick='amazon_receipts_process();'><img src='/sitimages/default/amazon.jpg' title='".trans_txt('mer_wreceipts_amazon_process')."' style='width:30px; position: relative; top:7px;'></a>";
		}
	}

	if($in{'closepo'}){
		if($in{'status'} ne 'Received'){
			if(&check_permissions('mer_po_close','','')){ 
				### Se obtiene la cantidad de items recibidos
				my $sql = "SELECT SUM(Received) TotalReceived FROM sl_purchaseorders_items WHERE ID_purchaseorders=".$in{'id_purchaseorders'}.";";
				my $sth = &Do_SQL($sql);
				my ($total_received) = $sth->fetchrow();

				### Inicializa la transaccion
				&Do_SQL("START TRANSACTION;");

				if( int($total_received) > 0 ){
					&Do_SQL("UPDATE sl_purchaseorders_items SET Qty=Received WHERE ID_purchaseorders='$in{'id_purchaseorders'}';");
					&auth_logging('mer_po_itemsclosed',$in{'id_purchaseorders'});
					&Do_SQL("UPDATE sl_purchaseorders SET Status='Received' WHERE ID_purchaseorders='$in{'id_purchaseorders'}' AND Status IN('New','In Process');");
					&auth_logging('mer_po_poclosed',$in{'id_purchaseorders'});
					$in{'status'} = 'Received';
				}else{
					&Do_SQL("UPDATE sl_purchaseorders SET Status='Cancelled' WHERE ID_purchaseorders='$in{'id_purchaseorders'}' AND Status IN('New','In Process');");
					&auth_logging('mer_po_poclosed',$in{'id_purchaseorders'});
					&Do_SQL("INSERT INTO sl_purchaseorders_notes SET ID_purchaseorders='$in{'id_purchaseorders'}', Notes='The order was Closed with a Cancelled status', Type='High', Date=CURDATE(), Time=CURTIME(), ID_admin_users='$usr{'id_admin_users'}';");
					$in{'status'} = 'Cancelled';
				}				

				### Confirma la transaccion
				&Do_SQL("COMMIT;");
			}else{
				$va{'tabmessages'} = &trans_txt('unauth_action');
			}
		}
	}elsif ($in{'additem'}){
		if(&check_permissions('mer_po','_edit','')){ 

			## Last Price for this Item/Vendor
			my ($sth) = Do_SQL("SELECT Qty,Price,Tax,Tax_percent,Total FROM sl_purchaseorders_items INNER JOIN sl_purchaseorders USING(ID_purchaseorders)
								WHERE ID_products = '$in{'additem'}' AND ID_vendors='$in{'id_vendors'}' 
								ORDER BY ID_purchaseorders_items DESC LIMIT 1;");
			my($qty,$price,$tax,$taxp,$total) = $sth->fetchrow();
			$price = 1 if !$price;
			$qty = 1 if !$qty;
			$taxp = 0 if !$taxp ;
			$tax = $qty * $price * $taxp;
			$total = $qty * $price + $tax;

			## Tax calculation.
			## For MX companies, refer to cgi-bin\common\subs\e\e[company_number].dbman.pl

			# Multiple / Single items
			@arr_items = split /\|/, $in{'additem'};
			for my $i (0..$#arr_items) {

				if($arr_items[$i] =~ /^700/){
					my ($sth) = &Do_SQL("INSERT INTO sl_purchaseorders_items SET ID_purchaseorders='$in{'id_purchaseorders'}',ID_products='$arr_items[$i]',Qty='$qty',Price='$price',Tax_percent='$taxp',Tax='$tax',Total='$total',Date=CURDATE(),Time=CURTIME(),ID_admin_users='$usr{'id_admin_users'}'");
				}
				elsif($arr_items[$i] =~ /^400/){
					my ($sth) = &Do_SQL("INSERT INTO sl_purchaseorders_items SET ID_purchaseorders='$in{'id_purchaseorders'}',ID_products='$arr_items[$i]',Qty='$qty',Price='$price',Tax_percent='$taxp',Tax='$tax',Total='$total',Date=CURDATE(),Time=CURTIME(),ID_admin_users='$usr{'id_admin_users'}'");
				}else{
					$arr_items[$i] +=100000000  if length($arr_items[$i]) == 6;
					my ($sth) = &Do_SQL("SELECT IsSet FROM sl_skus WHERE ID_sku_products='$arr_items[$i]'");
					if ($sth->fetchrow eq 'Y'){
						my ($sth) = &Do_SQL("SELECT sl_skus_parts.ID_parts FROM sl_skus_parts,sl_parts_vendors WHERE sl_skus_parts.ID_parts=sl_parts_vendors.ID_parts AND ID_vendors='$in{'id_vendors'}' AND ID_sku_products='$arr_items[$i]';");
						while ($id = $sth->fetchrow){
							$id += 400000000;
							my ($sth2) = &Do_SQL("INSERT INTO sl_purchaseorders_items SET ID_purchaseorders='$in{'id_purchaseorders'}',ID_products='$id',Qty='$qty',Price='$price',Tax_percent='$taxp',Tax='$tax',Total='$total',Date=CURDATE(),Time=CURTIME(),ID_admin_users='$usr{'id_admin_users'}'");
						}
					}else{
						my ($sth) = &Do_SQL("INSERT INTO sl_purchaseorders_items SET ID_purchaseorders='$in{'id_purchaseorders'}',ID_products='$arr_items[$i]',Qty='$qty',Price='$price',Tax_percent='$taxp',Tax='$tax',Total='$total',Date=CURDATE(),Time=CURTIME(),ID_admin_users='$usr{'id_admin_users'}'");
					}
				}
				$va{'tabmessages'} = &trans_txt('mer_po_itemadded');
				&auth_logging('mer_po_itemadded',$in{'id_purchaseorders'});

				########
				######## Segmento
				########
				( int($in{'id_segments'}) ) and ( &Do_SQL("UPDATE sl_purchaseorders_items SET ID_segments = '".int($in{'id_segments'})."' WHERE ID_purchaseorders = '$in{'id_purchaseorders'}' ORDER BY ID_purchaseorders_items DESC LIMIT 1;") );

				
			}
		}else{
			$va{'tabmessages'} = &trans_txt('unauth_action');
		}
	
	}elsif ($in{'addservice'} and int($in{'addservice'})>600000000){
 
 		if (&check_permissions('mer_po','_edit','')){
 			$in{'addservice'} = int($in{'addservice'});
 			$sql = "SELECT 
 						(SELECT Tax FROM sl_services WHERE ID_services = RIGHT('$in{'addservice'}', 4))Tax
 						, (SELECT sl_vendors.Currency FROM sl_purchaseorders INNER JOIN sl_vendors ON sl_purchaseorders.ID_vendors=sl_vendors.ID_vendors WHERE sl_purchaseorders.ID_purchaseorders='$in{'id_purchaseorders'}')Currency";
 			my $sth = &Do_SQL($sql);
 			my ($tax, $currency) = $sth->fetchrow_array;
 			$tax = ($currency ne $cfg{'acc_default_currency'}) ? 0 : $tax;
 			my $taxp = ($tax / 100) if( int($tax) > 0 );

 			$sql = "INSERT INTO sl_purchaseorders_items SET ID_purchaseorders='$in{'id_purchaseorders'}',ID_products='$in{'addservice'}',Qty='1',Price='0.00',Tax_percent='$taxp',Tax='0.00',Total='0.00',Date=CURDATE(),Time=CURTIME(),ID_admin_users='$usr{'id_admin_users'}'";
 			&Do_SQL($sql); 
 
 			$va{'messages'} = &trans_txt('mer_po_itemadded');
 
 		}else{
 			$va{'tabmessages'} = &trans_txt('unauth_action');
 		}

	## DROP
	}elsif($in{'vdrop'}){
		if(&check_permissions('mer_po_dropitem','','')){ 
			$va{'tabmessages'} .= &trans_txt('mer_po_itemdel');					
			my ($sth) = &Do_SQL("DELETE FROM sl_purchaseorders_items WHERE id_purchaseorders_items='$in{'vdrop'}'");
			&auth_logging('mer_po_itemdel',$in{'id_purchaseorders'});
		}else{
			$va{'tabmessages'} = &trans_txt('unauth_action');
		}
	}

	if ($in{'id_vendors'}){
		$va{'vendor_name'} = &load_db_names('sl_vendors','ID_vendors',$in{'id_vendors'},'[CompanyName]<br>[address] [city] <br>[state] [zip]');
		$va{'vendor_currency'} = &load_db_names('sl_vendors','ID_vendors',$in{'id_vendors'},'[currency]');
		$va{'vendor_currency'} = ($va{'vendor_currency'} eq 'MX$')?'MXP':($va{'vendor_currency'} eq 'US$')?'USD':$va{'vendor_currency'};
	}
	if ($in{'authby'}){
		$in{'authby_name'} = &load_db_names('admin_users','ID_admin_users',$in{'authby'},'[Firstname] [Lastname]');
	}else{
		$in{'authby'} = ($in{'status'} eq 'Auth Request') ? &trans_txt('auth_in_process') : &trans_txt('not_auth');
		$in{'auth'}   = 'In Process';
		delete($in{'authby_name'});
	}
	if ($in{'id_warehouses'}){
		$va{'warehouseinfo'} = &load_db_names('sl_warehouses','ID_warehouses',$in{'id_warehouses'},'[Name]<br>[address1] [address2] [address3]<br>[city] [state] [zip]');
	}

	$va{'shiptoaddress'} = $va{'warehouseinfo'};
	$in{'currency_exchange'} = &format_price($in{'currency_exchange'}) if $in{'currency_exchange'};
	$va{'currency'} = $in{'currency_exchange'} ? $cfg{'acc_default_currency'} . " * 1 " . &load_name('sl_vendors','ID_vendors',$in{'id_vendors'},'Currency') : '';
	$va{'curstyle'} = $va{'currency'} ne '' ? '' : qq|style="display:none;"|;
	$va{'segment_name'} = load_name('sl_accounts_segments','ID_accounts_segments',$in{'id_segments'},'Name');
	

	## Show or hide icons "Add Sku" & "Add Supply" 
	my ($authby);
	$authby = &load_name('sl_purchaseorders','ID_purchaseorders',$in{'id_purchaseorders'},'AuthBy');
	if ($authby >0){

		$va{'linkadd'} = '';
		if( $in{'type'} eq 'PO Services' and $in{'status'} eq 'In Process' and int($in{'authreceipt'}) == 1 ){
			$va{'linkadd'} = '<a href="/cgi-bin/common/apps/ajaxbuild?ajaxbuild=po_receipts_services&view=[in_id_purchaseorders]&po_receipt_services=1&second_conn=0" title="PO - Receipt Services" class="fancy_modal_iframe"><img src="/sitimages/default/bill_doc.png" alt="wreceipt" border="0" width="24px"></a>';
		}

	}else{
		$va{'linkadd'} = qq|
			<a href="/cgi-bin/common/apps/schid?cmd=po_addparts&id_purchaseorders=[in_id_purchaseorders]&rndnumber=[va_rndnumber]" title="Add Sku" class="fancy_modal_iframe"><img src="/sitimages/default/b_addsku.gif" title="Add Sku" border=0 width="24px"></a>
			<a href="/cgi-bin/common/apps/schid?cmd=po_addnoinv&id_purchaseorders=[in_id_purchaseorders]&rndnumber=[va_rndnumber]" title="Add Supply" class="fancy_modal_iframe"><img src="/sitimages/default/b_addsupply.gif" title="Add Supply" border=0 width="24px"></a>
			<a href="/cgi-bin/common/apps/schid?cmd=po_addservices&id_purchaseorders=[in_id_purchaseorders]" title="Add Services" class="fancy_modal_iframe"><img src="/sitimages/default/b_addservice.png" title="Add Services" border="0" width="24px"></a>|;
	}

	if( ($in{'status'} eq 'New' or $in{'status'} eq 'In Process' or $in{'status'} eq 'Auth Request') and &check_permissions('mer_po','_edit','') ){
		$va{'edit_deductible'} = '<a id="lnk_deductible_edit" href="#deductible_form" data-id="'.$in{'id_purchaseorders'}.'" data-value="'.$in{'deductible'}.'"><img src="/sitimages/default/b_edit.png" title="Edit Deductible" border="0" width="16px"></a>';
	}	

	### Link para solicitar autorizacion
	if( $in{'status'} eq 'New' and $in{'auth'} eq 'In Process' and $in{'type'} eq 'PO Services' ){
		my $sth = &Do_SQL("SELECT COUNT(*) FROM sl_purchaseorders_items WHERE ID_purchaseorders = ".$in{'id_purchaseorders'}." AND ID_segments != 0 AND ID_segments IS NOT NULL;");
		my $ct_items = $sth->fetchrow();
		if( int($ct_items) > 0 ){
			$va{'lnk_get_auth'} = '&nbsp;&nbsp;&nbsp; <span style="font-weight: normal;">Change to:</span> <a href="/cgi-bin/mod/[ur_application]/dbman?cmd=[in_cmd]&view='.$in{'id_purchaseorders'}.'&action=1&chgto_authrequest=1" id="lnk_get_auth">Auth Request</a>';
		}
	} elsif( $in{'type'} eq 'PO Services' and $in{'auth'} eq 'Approved' and int($in{'authreceipt'}) == 0 ){
		$va{'final_auth'} = '<tr>';
		$va{'final_auth'} .= '<td>Authorized Status Final:</td>';
		### Verifica si existe una autorización final pendiente
		my $sth = &Do_SQL("SELECT VValue FROM sl_vars WHERE VName = 'po_services_auth' AND Subcode LIKE '".$in{'id_purchaseorders'}."%' AND Definition_En = 'FinalAuth' LIMIT 1;");
		my $in_final_auth = $sth->fetchrow();
		### Si existe una autorización final pendiente, entonces muestra el status, de otra forma muestra el link para solicitarla
		my $final_auth_status = ($in_final_auth) ? &trans_txt('auth_in_process') : '<a href="/cgi-bin/mod/[ur_application]/dbman?cmd=[in_cmd]&view='.$in{'id_purchaseorders'}.'&action=1&chgto_authrequest=1&final_auth=1" id="lnk_get_auth">Request Final Auth</a>';
		$va{'final_auth'} .= '<td>'.$final_auth_status.'</td>';
		$va{'final_auth'} .= '</tr>';
	}

	## Build PO List
	## Converted to function because needs to be called from:
	## 
	&build_po_list();
	
	
	## Build Shipping Instructions
	my ($sth) = &Do_SQL("SELECT COUNT(*) FROM sl_purchaseorders_shipping WHERE ID_purchaseorders='$in{'id_purchaseorders'}' AND Type='Add to the PO'");
	if ($sth->fetchrow>0){
		my ($sth) = &Do_SQL("SELECT Notes FROM sl_purchaseorders_shipping WHERE ID_purchaseorders='$in{'id_purchaseorders'}' AND Type='Add to the PO'");
		while ($note = $sth->fetchrow){
			$note =~ s/\n/<br>/g;
			$va{'shipping_inst'} = "<li>$note</li>\n";
		}
	}else{
		$va{'shipping_inst'} = "---";
	}

	&get_company_info();

	### Auth Bill to Pay
	if( int($in{'id_bills'}) and int($in{'bill_auth_topay'}) == 1 ){
		if( &check_permissions('mer_bills_auth_topay','','') ){

			my $val = &Do_SQL("SELECT ID_vars FROM sl_vars WHERE VName = 'po_bills_auth' AND VValue = UPPER(SHA1('".int($in{'id_bills'})."'));");
			my $id_vars_exists = $val->fetchrow();

			if( !$id_vars_exists ){
				use utf8;
				binmode(STDOUT, ":utf8");
				### Se solicita la autorizacion al creador del PO
				my $usr = &Do_SQL("SELECT ID_admin_users, FirstName, LastName, MiddleName, Email FROM admin_users WHERE ID_admin_users = ".int($cfg{'user_auth_bill'}).";");
				my $usr_dat = $usr->fetchrow_hashref();

				my $id_admin_auth = $usr_dat->{'ID_admin_users'};
				my $authorizer = $usr_dat->{'ID_admin_users'}.' - '.$usr_dat->{'LastName'}.' '.$usr_dat->{'MiddleName'}.' '.$usr_dat->{'FirstName'};

				### Se obtienen los datos del Bill para la plantilla del correo
				my $sth_bills = &Do_SQL("SELECT * FROM sl_bills WHERE ID_bills = ".int($in{'id_bills'}).";");
				my $bills = $sth_bills->fetchrow_hashref();
				my @fields = ('BillDate','DueDate','Type','Invoice','Memo','Currency','Status','Amount');
				foreach $field (@fields){
					$va{'bills_'.lc($field)} = $bills->{$field};
				}
				$va{'bills_amount'} = &format_price($va{'bills_amount'});

				&Do_SQL("START TRANSACTION;");

				my $sth_hsh = &Do_SQL("SELECT UPPER(SHA1('".int($in{'id_bills'})."'));");
				$in{'hash'} = $sth_hsh->fetchrow();
				&Do_SQL("INSERT INTO sl_vars SET 
							VName = 'po_bills_auth'
							, VValue='".$in{'hash'}."'
							, Subcode='".$in{'id_bills'}."|".$usr{'id_admin_users'}."|".$id_admin_auth."'
							, Expiration = DATE_ADD(NOW(), INTERVAL 3 DAY)
						 ;");

				#### Datos para el template del email						
				$va{'vendor_name'} = &load_db_names('sl_vendors','ID_vendors',$in{'id_vendors'},'[CompanyName]<br>[address] [city] <br>[state] [zip]');
				
				### Se envia el correo de solicitud para la autorización
				my $from_email = $cfg{'from_email_info'};
				my $to_email = $usr_dat->{'Email'};
				my $subject = $cfg{'app_title'}.' - Autorización de Bill para Pago';
				$va{'maindomain'} = $cfg{'maindomain'};
				my $html_body = &build_page('emails/bills_auth_request.html');

				#### Se envia el email...
				$rslt_mail = &send_mandrillapp_email_attachment($from_email, $to_email, $subject, $html_body, 'none', 'none');

				#if( $rslt_mail ){

					### Se crea la nota
					&Do_SQL("INSERT INTO sl_bills_notes SET ID_bills = ".$in{'id_bills'}.", Notes='Send auth request for $authorizer', `Type`='High', Date=CURDATE(), Time=CURTIME(), ID_admin_users=".$usr{'id_admin_users'}.";");

					$in{'cmd'} = 'mer_bills';
					$in{'db'} = 'sl_bills';
					&auth_logging('mer_bills_auth_request',$in{'id_bills'});
					$in{'cmd'} = 'mer_po';
					$in{'db'} = 'sl_purchaseorders';

					$va{'message'} .= &trans_txt('Send auth request');
				#}

				&Do_SQL("COMMIT;");

				#&Do_SQL("UPDATE sl_bills SET AuthToPay = 1, AuthBy = ".int($usr{'id_admin_users'})." WHERE ID_bills = ".int($in{'id_bills'}).";");

				# $va{'message_good'} = "<span class='good'>".&trans_txt('mer_bills_auth_to_pay')." - ".$in{'id_bills'}."</span>";
				# $in{'cmd'} = 'mer_bills';
				# $in{'db'} = 'sl_bills';
				# &auth_logging('mer_bills_auth_to_pay',$in{'id_bills'});
				# $in{'db'} = 'sl_purchaseorders';
				# $in{'cmd'} = 'mer_po';
				# &auth_logging('mer_bills_auth_to_pay',$in{'id_purchaseorders'});
			}

		} else {
			$va{'message_error'} = &trans_txt('unauth_action');
		}
	}

	if ($in{'toprint'}){

        # Movements
        $va{'tab_type'}  = 'movs';
        $va{'tab_title'} = &trans_txt('logs');
        $va{'tab_table'} = 'sl_purchaseorders';
        $va{'tab_idvalue'} = $in{'id_purchaseorders'};
        $va{'mov_searchresults'} = &load_tabs_movs();

        my ($sth) = &Do_SQL("SELECT COUNT(*) FROM sl_bills_pos LEFT JOIN sl_bills ON sl_bills.ID_bills=sl_bills_pos.ID_bills WHERE ID_purchaseorders='$in{'id_purchaseorders'}' ORDER BY ID_bills_pos DESC;");
		$va{'matches'} = $sth->fetchrow();
		if ($va{'matches'}>0){
			$va{'searchresults_bills_print'} .= qq|
			<table border="0" cellspacing="0" cellpadding="4" width="100%" class="formtable">
      			<tr>         	
					<td class="menu_bar_title" width="10%" align="center">ID BIll</td>
					<td class="menu_bar_title" width="35%" align="center">Bill Date</td>
					<td class="menu_bar_title" width="14%" align="center">Due Date</td>
					<td class="menu_bar_title" width="14%" align="center">Status</td>
					<td class="menu_bar_title" width="15%" align="center">Amount</td>
			 	</tr>|;

			my ($sth) = &Do_SQL("SELECT * FROM sl_bills_pos LEFT JOIN sl_bills ON sl_bills.ID_bills=sl_bills_pos.ID_bills WHERE ID_purchaseorders='$in{'id_purchaseorders'}' ORDER BY ID_bills_pos DESC;");
			while ($rec = $sth->fetchrow_hashref){
				$d = 1 - $d;
				$va{'searchresults_bills_print'} .= "<tr bgcolor='$c[$d]'>\n";
				$va{'searchresults_bills_print'} .= qq| <td class='smalltext' valign='top'>$rec->{'ID_bills'}</td> |;
				$va{'searchresults_bills_print'} .= "   <td class='smalltext' valign='top'>$rec->{'BillDate'}</td>\n";
				$va{'searchresults_bills_print'} .= "   <td class='smalltext' valign='top'>$rec->{'DueDate'}</td>\n";
				$va{'searchresults_bills_print'} .= "   <td class='smalltext' valign='top'>$rec->{'Status'}</td>\n";
				$va{'searchresults_bills_print'} .= "   <td class='smalltext' align='right' valign='top'>".&format_price($rec->{'Amount'})."</td>\n";			
				$va{'searchresults_bills_print'} .= "</tr>\n";
				$tot_po += $rec->{'Amount'};
			}

			$va{'searchresults_bills_print'} .= qq|
				<tr>
					<td colspan="5"><hr class=""></td>
				</tr>						
				<tr>
					<td colspan='4' class='smalltext' align="right">|.&trans_txt('mer_po_total').qq|</td>
					<td align="right" class='smalltext' nowrap>|.&format_price($tot_po).qq|</td>
				</tr>\n|;
		}
	}
}


#############################################################################
#############################################################################
#   Function: build_po_list
#
#       Es: Genera el listado de PO Items/Adjustments
#       En: Build PO Items/Adjustments List 
#
#
#    Created on: 2013-03-07
#
#    Author: _Roberto Barcenas_
#
#    Modifications:
#
#        - Modified on ** by _Roberto Barcenas_ : 
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
#      <view_mer_po>
#
sub build_po_list {
#############################################################################
#############################################################################

	# Legend for noauth POs print
	$va{'display_noauth'} = ($in{'auth'} eq 'Approved')?'display:none;':'';

	delete($va{'polist'}); delete($va{'pototal'});
	my $authby = &load_name('sl_purchaseorders','ID_purchaseorders',$in{'id_purchaseorders'},'AuthBy');
	my ($choices,$tot_qty,$tot_po,$tax_po,$subtot_po,$vendor_sku,$line,$name,$cmdlink,$unit);
	my (@c) = split(/,/,$cfg{'srcolors'});
	my ($sth) = &Do_SQL("SELECT COUNT(*) FROM sl_purchaseorders_items WHERE ID_purchaseorders='$in{'id_purchaseorders'}'");
	if ($sth->fetchrow>0){
		my ($sth) = &Do_SQL("SELECT *, (Qty - Received) as quantity FROM sl_purchaseorders_items WHERE ID_purchaseorders='$in{'id_purchaseorders'}' ORDER BY ID_purchaseorders_items DESC;");
		while ($rec = $sth->fetchrow_hashref){
			$d = 1 - $d;
			++$line;

			# Color in Received
			$color = ($rec->{'quantity'}==0)? ' style="color:#73AB00"' : ' style="color:#FF0000"';
			
			## Choices
			my ($sth2) = &Do_SQL("SELECT * FROM sl_skus WHERE ID_sku_products='$rec->{ID_products}' and Status='Active'");
			$tmp = $sth2->fetchrow_hashref;
			$choices = &load_choices('-',$rec->{'choice1'},$rec->{'choice2'},$rec->{'choice3'},$rec->{'choice4'});
			
			my $upc = ($tmp->{'UPC'} ne '')? "<br>".$tmp->{'UPC'}:"";

			## Name Model
			if ($rec->{'ID_products'} =~ /^5/){
				## Non Inventory
				$cmdlink = 'mer_noninventory';
				my $sth = &Do_SQL("SELECT Units, Name FROM sl_noninventory WHERE ID_noninventory = ".int($rec->{'ID_products'}-500000000).";");
				($unit, $name) = $sth->fetchrow_array();				
				$va{'inv_type'} = 'supplys';
			}elsif ($rec->{'ID_products'}  =~ /^4/){
				## Part
				$unit  = "Unit";
				$cmdlink = 'mer_parts';
				$name = &load_db_names('sl_parts','ID_parts',($rec->{'ID_products'}-400000000),'[Model]<br>[Name]');
				$va{'inv_type'} = 'skus';
			}elsif ($rec->{'ID_products'}  =~ /^6/){
 				## Services
 				$unit  = "Unit";
 				$cmdlink = 'mer_services';
 				$name = &load_db_names('sl_services','ID_services',($rec->{'ID_products'}-600000000),'[Name]');
 				$va{'inv_type'} = 'services';

 				$segment_name = &load_db_names('sl_accounts_segments', 'ID_accounts_segments', ($rec->{'ID_segments'}), '[Name]');
 				$segment_name = 'N/A' if( !$segment_name or $segment_name eq '' );
 				my $edit_segment = '';
 				if( !$authby and $rec->{'Received'} eq 0 and !$in{'toprint'} and $in{'status'} ne 'Auth Request' ){
 					$edit_segment = '&nbsp;<a href="#segment_form" class="segment_edit" data-id="'.$rec->{'ID_purchaseorders_items'}.'"><img src="/sitimages/default/b_edit.png" title="Edit PO Area" border="0" width="16px"></a>';
 				}
 				$tmp->{'VendorSKU'} = '--- / <span id="segment_'.$rec->{'ID_purchaseorders_items'}.'">'.$segment_name.'</span>'.$edit_segment;
			}
			
			if( !$authby and $rec->{'Received'} eq 0 and !$in{'toprint'} and $in{'status'} ne 'Auth Request' ){
				$va{'po_blocked'} = "";
				$va{'qyt'}   = "   <td class='smalltext' valign='top'><span id='span_qty_$rec->{'ID_purchaseorders_items'}' class='editable'>".&format_number($rec->{'Qty'})."</span> $unit <span id='span_chg_qty_$rec->{'ID_purchaseorders_items'}'><img id='btn_chg_qty_$rec->{'ID_purchaseorders_items'}' class='triggers_editable' src='$va{'imgurl'}/$usr{'pref_style'}/b_edit.png' title='".&trans_txt('clicktoedit')."' style='cursor:pointer;'></span></td>\n";
				$va{'price'} = "   <td class='smalltext' align='right' valign='top' nowrap>";
				if(&check_permissions('mer_po_edit_price','','')) {
					if( $in{'type'} eq 'PO Services' ){

						$va{'total'} = "<span id='span_total_$rec->{'ID_purchaseorders_items'}'  class='editable'> ".&format_price($rec->{'Total'})."</span> <span id='span_chg_price_$rec->{'ID_purchaseorders_items'}'><img id='btn_chg_total_$rec->{'ID_purchaseorders_items'}' class='triggers_editable' src='$va{'imgurl'}/$usr{'pref_style'}/b_edit.png' title='".&trans_txt('clicktoedit')."' style='cursor:pointer;'></span>";
						$va{'price'} .= &format_price($rec->{'Price'});

					} else {

						$va{'price'} .= "<span id='span_price_$rec->{'ID_purchaseorders_items'}'  class='editable'> ".&format_price($rec->{'Price'})."</span> <span id='span_chg_price_$rec->{'ID_purchaseorders_items'}'><img id='btn_chg_price_$rec->{'ID_purchaseorders_items'}' class='triggers_editable' src='$va{'imgurl'}/$usr{'pref_style'}/b_edit.png' title='".&trans_txt('clicktoedit')."' style='cursor:pointer;'></span>";
						$va{'total'} = &format_price($rec->{'Total'});

					}
				}else{
					$va{'price'} .= &format_price($rec->{'Price'});
					$va{'total'} = &format_price($rec->{'Total'});
				}
				
				$va{'price'} .= "</td>\n";
				$va{'taxp'} = "   <td class='smalltext' valign='top' nowrap><span id='span_taxp_$rec->{'ID_purchaseorders_items'}'  class='editable'> ".($rec->{'Tax_percent'}*100)."</span> <span id='span_chg_taxp_$rec->{'ID_purchaseorders_items'}'><img id='btn_chg_taxp_$rec->{'ID_purchaseorders_items'}' class='triggers_editable' src='$va{'imgurl'}/$usr{'pref_style'}/b_edit.png' title='".&trans_txt('clicktoedit')."' style='cursor:pointer;'></span></td>\n";
			}else{
				$va{'po_blocked'} = "alert('No es posible editar el campo requerido');\nreturn;\n";
				$va{'qyt'}   = "   <td class='smalltext'  valign='top'>".&format_number($rec->{'Qty'})."</td>\n";
				$va{'price'} = "   <td class='smalltext' align='right' valign='top'>".&format_price($rec->{'Price'})."</td>\n";
				$va{'taxp'} = "   <td class='smalltext' valign='top'>".($rec->{'Tax_percent'}*100)."</td>\n";
				$va{'total'} = &format_price($rec->{'Total'});
			}

			$va{'polist'} .= "<tr bgcolor='$c[$d]'>\n";
			$va{'polist'} .= "   <td class='smalltext' valign='top'>$line </td>\n";
			$va{'polist'} .= "   <td class='smalltext' valign='top' nowrap><a href='/cgi-bin/mod/$usr{'application'}/dbman?cmd=$cmdlink&view=".substr($rec->{'ID_products'},3,6)."'>".&format_sltvid($rec->{'ID_products'})."</a>$upc</td>\n";
			$va{'polist'} .= "   <td class='smalltext' valign='top'>$tmp->{'VendorSKU'}</td>\n";
			$va{'polist'} .= "   <td class='smalltext' valign='top'>$name </td>\n";
			$va{'polist'} .= $va{'qyt'};
			$va{'polist'} .= $va{'price'};
			$va{'polist'} .= $va{'taxp'};
			$va{'polist'} .= "   <td class='smalltext' align='center' valign='top' $color>".&format_number($rec->{'Received'})."</td>\n";
			$va{'polist'} .= "   <td class='smalltext' align='right' valign='top' nowrap> ".&format_price($rec->{'Qty'} * $rec->{'Price'})."</td>\n";
			$va{'polist'} .= "   <td class='smalltext' align='right' valign='top'>\$ ".&format_number($rec->{'Tax'},2)."</td>\n";
			$va{'polist'} .= "   <td class='smalltext' align='right' valign='top'>\$ ".&format_number($rec->{'Tax_withholding'},2)."</td>\n";
			$va{'polist'} .= "   <td class='smalltext' align='right' valign='top'>\$ ".&format_number($rec->{'Tax_other'},2)."</td>\n";
			$va{'polist'} .= "   <td class='smalltext' align='right' valign='top' nowrap> ".$va{'total'}."</td>\n";
			$va{'polist'} .= "</tr>\n";
			$tot_qty += $rec->{'Qty'};
			$tot_po += $rec->{'Total'};
			$tax_po += $rec->{'Tax'};
			$tax_hold_po += $rec->{'Tax_withholding'};
			$tax_other_po += $rec->{'Tax_other'};
			$subtot_po += ($rec->{'Price'}*$rec->{'Qty'});
			#&cgierr("$rec->{'Price'}*$rec->{'Qty'}*$rec->{'Tax_percent'}") if $rec->{'Tax_percent'} > 0 ;
		}
	}else{
		$va{'polist'} = qq|
			<tr>
				<td colspan='12' align="center">|.&trans_txt('search_nomatches').qq|</td>
			</tr>\n|;
	}
	
	##---------------------------------------------------------
	## Controla la opción para validar el gasto de aterrizaje
	##---------------------------------------------------------
	my $perm_validate = &check_permissions('mer_po_validate_adj','','');
	
	my ($sth) = &Do_SQL("SELECT sl_purchaseorders.Auth, sl_purchaseorders.`Status`
						FROM sl_purchaseorders						
						WHERE sl_purchaseorders.ID_purchaseorders = '".$in{'id_purchaseorders'}."';");
	my($po_auth, $po_status) = $sth->fetchrow();
	if( $po_auth eq 'Approved' and $po_status eq 'In Process' ){
		$to_validate = 'Yes';
	}
	##---------------------------------------------------------

	my ($sth) = &Do_SQL("SELECT COUNT(*) FROM sl_purchaseorders_adj WHERE ID_purchaseorders='$in{'id_purchaseorders'}'");
	if ($sth->fetchrow>0){
		my ($sth) = &Do_SQL("	select sl_purchaseorders_adj.Validate, sl_purchaseorders_adj.`Status`, 
								sl_purchaseorders_adj.ID_purchaseorders_adj,sl_vendors.CompanyName, sl_purchaseorders_adj.Amount, 
								sl_purchaseorders_adj.Tax, sl_purchaseorders_adj.Total, sl_vendors.ID_vendors, sl_purchaseorders_adj.`Type`, 
								sl_purchaseorders_adj.Description, sl_purchaseorders_adj.InCOGS
								from sl_purchaseorders_adj 
								join sl_vendors on sl_vendors.ID_vendors=sl_purchaseorders_adj.ID_vendors
								where sl_purchaseorders_adj.id_purchaseorders='$in{'id_purchaseorders'}'");
		while ($rec = $sth->fetchrow_hashref){
			$d = 1 - $d;
			++$line;
			$rec->{'Qty'} = 1;
			$va{'polist'} .= "<tr bgcolor='$c[$d]'>\n";
			$va{'polist'} .= "   <td class='smalltext'>$line</td>\n";
			if( $to_validate eq 'Yes' and $rec->{'Validate'} == 0 and $rec->{'Status'} eq 'Active' and $perm_validate ){
				$va{'polist'} .= "   <td class='smalltext' align='center'><a href='#' id='btn_validate_$rec->{'ID_purchaseorders_adj'}' class='btn_validate' data-to-val='1' data-id-adj='$rec->{'ID_purchaseorders_adj'}'><img src='$va{'imgurl'}/$usr{'pref_style'}/b_ok.png' alt='Validate' title='Validar el monto de este gasto...' /></a></td>\n";
			}elsif( $to_validate eq 'Yes' and $rec->{'Validate'} == 1 and $rec->{'Status'} eq 'Active' and $perm_validate ){
				$va{'polist'} .= "   <td class='smalltext' align='center'><a href='#' id='btn_validate_$rec->{'ID_purchaseorders_adj'}' class='btn_validate' data-to-val='0' data-id-adj='$rec->{'ID_purchaseorders_adj'}'><img src='$va{'imgurl'}/$usr{'pref_style'}/b_drop.png' alt='NoValidate' title='Quitar la validaci&oacute;n de este gasto...' /></a></td>\n";
			}elsif( $rec->{'Validate'} == 1 ){
				$va{'polist'} .= "   <td class='smalltext' align='center'><img src='$va{'imgurl'}/$usr{'pref_style'}/approved.gif' alt='Validado' title='Validado' style='height: 16px; width: 16px;' /></td>\n";
			}else{
				$va{'polist'} .= "   <td class='smalltext' align='center'>---</td>\n";
			}
			$va{'polist'} .= "   <td class='smalltext' align='center'>---</td>\n";
			$va{'polist'} .= "   <td class='smalltext'>Vendors: <a href=\"/cgi-bin/mod/$usr{'application'}/dbman?cmd=mer_vendors&view=$rec->{'ID_vendors'}\">$rec->{'CompanyName'}($rec->{'ID_vendors'})</a> / $rec->{'Type'}: $rec->{'Description'} / InCogs : $rec->{'InCOGS'}</td>\n";
			$va{'polist'} .= "   <td class='smalltext' align='center'>---</td>\n";
			$va{'polist'} .= "   <td class='smalltext' align='center'>---</td>\n";
			$va{'polist'} .= "   <td class='smalltext' align='center'>---</td>\n";
			$va{'polist'} .= "   <td class='smalltext' align='center'>---</td>\n";
			$va{'polist'} .= "   <td class='smalltext' align='right'> ".&format_price($rec->{'Amount'})."</td>\n";
			$va{'polist'} .= "   <td class='smalltext' align='right' valign='top'>\$ ".&format_number($rec->{'Tax'},2)."</td>\n";
			$va{'polist'} .= "   <td class='smalltext' align='center'>---</td>\n";
			$va{'polist'} .= "   <td class='smalltext' align='center'>---</td>\n";
			$va{'polist'} .= "   <td class='smalltext' align='right'> ".&format_price($rec->{'Total'})."</td>\n";
			$va{'polist'} .= "</tr>\n";
			$tot_po += $rec->{'Total'};
			$tax_po += $rec->{'Tax'};
			$subtot_po += ($rec->{'Amount'});
		}
	}
	$va{'posubtot'} = &format_price($subtot_po);
	$va{'potottax'} = &format_price($tax_po);
	$va{'potottax_hold'} = &format_price($tax_hold_po);
	$va{'potottax_other'} = &format_price($tax_other_po);
	$va{'pototal'} = &format_price($tot_po);

}



sub del_mer_po {
# --------------------------------------------------------
# Last Modification by JRG : 06/11/2009 : Se agrega el log
	my ($sth) = &Do_SQL("DELETE FROM sl_purchaseorders_adj WHERE ID_purchaseorders='$in{'delete'}';");
	&auth_logging('mer_po_adj_del',$in{'delete'});
	my ($sth) = &Do_SQL("DELETE FROM sl_purchaseorders_auth WHERE ID_purchaseorders='$in{'delete'}';");
	&auth_logging('mer_po_auth_del',$in{'delete'});
	my ($sth) = &Do_SQL("DELETE FROM sl_purchaseorders_items WHERE ID_purchaseorders='$in{'delete'}';");
	&auth_logging('mer_po_itemdel',$in{'delete'});
	my ($sth) = &Do_SQL("DELETE FROM sl_purchaseorders_notes WHERE ID_purchaseorders='$in{'delete'}';");
	&auth_logging('mer_po_note_del',$in{'delete'});
	my ($sth) = &Do_SQL("DELETE FROM sl_purchaseorders_shipping WHERE ID_purchaseorders='$in{'delete'}';");
	&auth_logging('mer_po_ship_del',$in{'delete'});
}

sub validate_mer_po{
# --------------------------------------------------------
# Created on: 1/1/2007 9:43AM
# Last Modified on:
# Last Modified by:

	
	my $err;
	$in{'id_vendors'} = int($in{'id_vendors'});
	if ($in{'add'}){
		$in{'auth'} = 'In Process';
		$in{'status'} = 'New';
		$in{'deductible'} = 'Yes' if( $in{'type'} eq 'PO Services' );
	}
	
	if ($in{'id_vendors'}>0){
		my ($sth) = &Do_SQL("SELECT COUNT(*) FROM sl_vendors WHERE ID_vendors='$in{'id_vendors'}';");
		#$rec = $sth->fetchrow_hashref){
		if ($sth->fetchrow==0){
			$error{'id_vendors'} = &trans_txt('notmatch');
			++$err;
		}else{
			$va{'vendor_name'} = "<br>".&load_name('sl_vendors','ID_vendors',$in{'id_vendors'},'CompanyName');
		}
	}else{
		$error{'id_vendors'} = &trans_txt('required');
	}
	

	if ($in{'edit'}){
		if ($in{'authby'}){
			$in{'authby_name'} = &load_db_names('admin_users','ID_admin_users',$in{'authby'},'[Firstname] [Lastname]');
		}

		if (&load_name('sl_purchaseorders','ID_purchaseorders',$in{'id_purchaseorders'},'AuthBy') >0) {

			## No se permite editar Vendor,Terms
			my $id_vendors = &load_name('sl_purchaseorders','ID_purchaseorders', $in{'id_purchaseorders'},'ID_vendors');

			## No se permite editar Terms si yua se recibio mercancia
			my ($sth) = &Do_SQL("SELECT SUM(Received) FROM sl_purchaseorders_items WHERE ID_purchaseorders = '$in{'id_purchaseorders'}';");
			my ($total) = $sth->fetchrow();

			if($id_vendors ne $in{'id_vendors'} or $total){
				$va{'message'} = &trans_txt('mer_po_blocked');
				++$err;
			}
			
		}
	}

	if ($in{'add'}){
		$in{'poterms'} = &load_name('sl_vendors','ID_vendors',$in{'id_vendors'},'POTerms');
	}

	if( $in{'type'} eq 'PO Services' ){
		$in{'shipvia'} = 'OTRO';
		$in{'id_warehouses'} = '1001';
	}

	if( int($in{'id_segments'}) == 0 ){
		$error{'id_segments'} = &trans_txt('required');
	}

	return $err;
}

#############################################################################
#############################################################################
#   Function: js_clear_form
#
#       Es: Se ejecuta en el formulario de busqueda de Purchase Order, para limpiar el formulario 
#       En: Runs on search form Purchase Order, for clean form
#
#
#    Created on: 2013-03-20
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
#      <>
#
sub js_clear_form {
#############################################################################
#############################################################################
	$va{'clear_form'} = ($in{'search'} eq 'form')? 'document.forms["sitform"].reset();' : '';

	return $va{'clear_form'};
}



sub amazon_receipts_process
{
	use Scalar::Util qw(looks_like_number);

	my $dir = getcwd;
	my($b_cgibin,$a_cgibin) = split(/cgi-bin/,$dir);
	my $home_dir = $b_cgibin.'cgi-bin/common';
	require "$home_dir/subs/sub.wms.html.cgi";

	my( $id_purchaseorders, $id_orders, $id_exchangerates, $number_tracking, $shpdate) = @_;

	## Creación / Inserción de la recepción
	&Do_SQL("BEGIN;");

	my ($sth) = &Do_SQL("INSERT INTO sl_wreceipts SET  ID_vendors ='".$cfg{'amazon_vendor'}."' , ID_purchaseorders ='$id_purchaseorders' , Description ='Recepcion de la orden ".$id_orders."' , Type ='Warehouse Receipt' , Pieces ='', ID_exchangerates ='".$id_exchangerates."', Status ='In Process' ,Date=Curdate(),Time=NOW(), ID_admin_users='".$usr{'id_admin_users'}."';");
	my ($id_wreceipts) = $sth->{'mysql_insertid'};

	if( !looks_like_number($id_wreceipts) ){
		$va{'message'} = "<li>Can´t create Warehouse Receipt</li>";
		&Do_SQL("ROLLBACK;");
		return;
	}

	## ¿Cuantos items tiene la Orden de Compra?
	my ($sth) = &Do_SQL("	SELECT COUNT(*) 
							FROM sl_purchaseorders_items INNER JOIN sl_skus ON sl_purchaseorders_items.ID_products=ID_sku_products 
							WHERE ID_purchaseorders = '".$id_purchaseorders."' AND Qty - Received > 0;");
	my ($qty_products) = $sth->fetchrow();

	if($qty_products>0)
	{
		## Datos de los items
		$sth = &Do_SQL("SELECT *
						FROM sl_purchaseorders_items 
						WHERE ID_purchaseorders = '".$id_purchaseorders."' AND Qty - Received > 0 ;");


		while ($rec = $sth->fetchrow_hashref)
		{
			## Inserción de los item petenecientes a la orden de compra
			my ($sth) = &Do_SQL("	INSERT INTO sl_wreceipts_items 
								 	SET ID_wreceipts='".$id_wreceipts."',
								 	ID_products='".$rec->{'ID_products'}."',
								 	Serial='',
								 	Qty=ifnull( (
								 					SELECT sum(if((Qty - Received) > 0, (Qty - Received), 1)) as quantity 
								 					FROM sl_purchaseorders_items 
								 					WHERE ID_purchaseorders_items = '".$rec->{'ID_purchaseorders_items'}."' AND ID_products = '".$rec->{'ID_products'}."' 
								 				), 0
											  ),
									Date=CURDATE(),
									Time=CURTIME(),
									ID_admin_users='$usr{'id_admin_users'}'");

			&auth_logging('wreceipt_itemadded',$rec->{'ID_prod'});
		}
	}

	### Loading IDs
	my ($rec,@ids,@qty,@wrs,$cant);

	my ($sth) = &Do_SQL("SELECT ID_products, SUM(Qty) FROM sl_wreceipts_items WHERE ID_wreceipts='".$id_wreceipts."' GROUP BY ID_products;");
	my ($id_products, $qty) = $sth->fetchrow(); 
	$qty = int($qty);
		 
	$sth = &Do_SQL("INSERT INTO sl_manifests 
					SET RequestedBy='$usr{'id_admin_users'}', Comments='Recepcion de productos Amazon para la Orden de Compra: ".$id_purchaseorders."', 
					AuthorizedBy='$usr{'id_admin_users'}',	ProcessedBy='$usr{'id_admin_users'}',Status='In Progress',Date=CURDATE(),Time=CURTIME(),
					ID_admin_users='$usr{'id_admin_users'}'");
	$id_manifests = $sth->{'mysql_insertid'};

	if( !looks_like_number($id_manifests) ){
		$va{'message'} = "<li>Can´t create Warehouse Receipt</li>";
		&Do_SQL("ROLLBACK;");
		return;
	}


	&auth_logging('manifests_added', $id_manifests);

	#Verifica si el producto es set
	$isset=&load_name('sl_skus','ID_sku_products',$ids[$i],'IsSet');


	if($isset ne'Y'){
		my ($sth) = &Do_SQL("INSERT INTO sl_manifests_items SET ID_manifests='$id_manifests', ID_products='$id_products'
			,From_Warehouse='".$sys{'receiving_warehouse'}."'
			,From_Warehouse_Location=''
			,To_Warehouse='".&filter_values($cfg{'amazon_id_warehouse'})."'
			,To_Warehouse_Location='".&filter_values($cfg{'amazon_id_location'})."'
			,Qty='$qty',Date=CURDATE(),Time=CURTIME(),ID_admin_users='$usr{'id_admin_users'}'");
		
		$in{'db'} = 'sl_manifests';
		&auth_logging('manifest_itemadded',$id_manifests);
		
		#$items{$ids[$i]} += $qty[$i];

		########################
		######################## Entrada en sl_warehouses_location

		my ($sth) = &Do_SQL("SELECT ID_warehouses_location FROM sl_warehouses_location WHERE ID_warehouses = '".$cfg{'amazon_id_warehouse'}."' AND ID_products = '$id_products' AND Location = '".&filter_values($cfg{'amazon_id_location'})."';");
		my ($idwl) = $sth->fetchrow();

		if($idwl) {
			## Update Inventory
			my ($sth) = &Do_SQL("UPDATE sl_warehouses_location SET Quantity = Quantity + $qty WHERE ID_warehouses_location = '$idwl';");
		}else{
			## Insert Inventory
			my ($sth) = &Do_SQL("INSERT INTO sl_warehouses_location SET ID_warehouses = '$cfg{'amazon_id_warehouse'}', ID_products = '$id_products', Location = '".&filter_values($cfg{'amazon_id_location'})."', Quantity = '$qty', Date = CURDATE(), Time = CURTIME(), ID_admin_users = '$usr{'id_admin_users'}'");
		}
		$in{'db'} = 'sl_warehouses_location';
		&auth_logging('warehouses_location_added',$sth->{'mysql_insertid'});
		
		$in{'db'} = 'sl_skus_trans';
		&auth_logging('sku_trans_added',$sth->{'mysql_insertid'});
		&sku_logging($id_products, $cfg{'amazon_id_warehouse'}, $cfg{'amazon_id_location'}, 'Purchase', $id_wreceipts, 'sl_wreceipts',$qty);
	}
	

	########################
	######################## Entrada en sl_skus_cost
	
	### Calculo de ajuste en el PO
	my ($totalwr);

	##### Suma de la recepcion
	my $amt_po = 0;
	

	my ($sth) = &Do_SQL("SELECT sum(Qty * Price) FROM sl_purchaseorders_items WHERE ID_purchaseorders = $id_purchaseorders;");
	$amt_po = $sth->fetchrow();

	### Separamos el Monto General, Monto del mismo Vendor y Tax del mismo vendor
	my ($sth) = &Do_SQL("SELECT SUM(Total-Tax), 
		SUM(IF(ID_vendors = '$cfg{'amazon_vendor'}',Total-Tax,0))AS AmtSV, 
		SUM(IF(ID_vendors = '$cfg{'amazon_vendor'}',Tax,0))AS TaxSV  
		FROM sl_purchaseorders_adj 
		WHERE ID_purchaseorders = '$id_purchaseorders;' 
		AND InCOGS = 'Yes' AND Status = 'Active';");

	my ($amt_adj, $amt_adjsv, $tax_adjsv) = $sth->fetchrow();
	
	$amt_adj = 0 if !$amt_adj; 
	$amt_adjsv = 0 if !$amt_adjsv; 
	$tax_adjsv = 0 if !$tax_adjsv;  

	### Metodo usado para la salida de inventario. FIFO: Primer entradas primeras salidas | LIFO: Ultimas entradas primeras salidas
	my $acc_method = $cfg{'acc_inventoryout_method'} ? $cfg{'acc_inventoryout_method'} : 'fifo';
	my $invout_order = $acc_method eq 'fifo' ? '' : 'DESC';

	my ($exchange_rate) = &load_name('sl_exchangerates', 'ID_exchangerates',$id_exchangerates,'exchange_rate');
	my ($vendor_category) = &load_name('sl_vendors', 'ID_vendors', $cfg{'amazon_vendor'}, 'Category');


	#### Datos de la linea del producto
	my ($sth) = &Do_SQL("SELECT Qty,Price, (Qty*Price) as total, ID_purchaseorders_items FROM sl_purchaseorders_items WHERE ID_purchaseorders = '$id_purchaseorders';");
	while ($rec = $sth->fetchrow_hashref)
	{
		my $line_qty		= $rec->{'Qty'};
		my $line_price 		= $rec->{'Price'};
		my $line_total 		= $rec->{'total'};
		my $line_idpo_items = $rec->{'ID_purchaseorders_items'};
		
		my $cost = round($exchange_rate * $line_price,3);
		my $proportional = 0; my $proportionalsv = 0; my $proportionalsvt = 0; my $str_adj;

		$totalwr += ( $cost * $line_qty );

		### Calculo proporcional de Ajuste
		if($amt_adj) {
			my $pct = 1;
			$pct = ($line_total / $amt_po) if  $amt_po > 0;
			$proportional = round($amt_adj * $pct * $exchange_rate / $line_qty,3);
			$proportionalsv = $amt_adjsv ? round($amt_adjsv * $pct * $exchange_rate / $line_qty,3) : 0;
			$proportionalsvt = $tax_adjsv ? round($tax_adjsv * $pct * $exchange_rate / $line_qty,3) : 0;
			$str_adj = qq|\nAdj. Value: $proportional  $pct = ($line_total / $amt_po)     $proportional = $amt_adj * $pct / $in{$key}   |;
		} 

		## Costo + Proporcional Ajuste
		my $sumcost = $cost + $proportional;

		########################################################
		########################################################
		## 1 ) sl_skus_cost
		########################################################
		########################################################
		my ($sth) = &Do_SQL("SELECT ID_skus_cost FROM sl_skus_cost WHERE ID_warehouses = '".$cfg{'amazon_id_warehouse'}."' AND ID_products = '$id_products' AND Cost = '$sumcost' AND Cost_Adj = '$proportional' ORDER BY Date $invout_order LIMIT 1");
		my ($idsc) = $sth->fetchrow();

		if($idsc) {
			my ($sth) = &Do_SQL("UPDATE sl_skus_cost SET Quantity = Quantity + $line_qty WHERE ID_skus_cost = '$idsc';");
		}else{
			my ($sth) = &Do_SQL("INSERT INTO sl_skus_cost SET ID_warehouses = '".$cfg{'amazon_id_warehouse'}."' ,ID_products = '$id_products', ID_purchaseorders = '$id_purchaseorders', Quantity = '$line_qty', Cost = '$sumcost', Cost_Adj = '$proportional', Date = CURDATE(), Time = CURTIME(), ID_admin_users = '$usr{'id_admin_users'}'");	
		}
		$in{'db'} = 'sl_skus_cost';
		&auth_logging('sku_cost_added',$sth->{'mysql_insertid'});


		########################################################
		########################################################
		## 2) Movimientos de contabilidad
		########################################################
		########################################################

		my @params = ($id_purchaseorders,$line_idpo_items,$line_qty,$cost,$proportionalsv,$proportionalsvt,$id_products,$exchange_rate);
		&accounting_keypoints('po_wreceipt_in_'. lc($vendor_category), \@params );

												

		########################################################
		########################################################
		## 3) Actualizacion de W. Receipt y PO
		########################################################
		########################################################

		## Update POs
		my ($sth) = &Do_SQL("UPDATE sl_purchaseorders_items SET Received=Received+$line_qty WHERE ID_products='$id_products' AND ID_purchaseorders_items='$line_idpo_items'");
		$in{'db'} = 'sl_purchaseorders';
		&auth_logging('purchaseorder_item_updated',$id_purchaseorders);
		&Do_SQL("INSERT INTO sl_purchaseorders_notes SET ID_purchaseorders='$id_purchaseorders', Notes='W. Receipt: $id_wreceipts\nProduct: ($id_products) ". &load_name('sl_parts','ID_parts',($id_products - 400000000),'Name') ."\nWarehouse: ($cfg{'amazon_id_warehouse'}) ". &load_name('sl_warehouses','ID_warehouses',$cfg{'amazon_id_warehouse'},'Name') ."\nLocation: $cfg{'amazon_id_location'}\nQuantity: $line_qty\nCurrency Exchange: $exchange_rate\nUnit Cost: ". &format_price($cost)  ."/". &format_price($sumcost). "$str_adj',Type='Low', Date = CURDATE(), Time = CURTIME(), ID_admin_users='$usr{'id_admin_users'}' ");
		&Do_SQL("INSERT INTO sl_wreceipts_notes SET ID_wreceipts='$cfg{'amazon_id_warehouse'}', Notes='Product: ($id_products) ". &load_name('sl_parts','ID_parts',($id_products - 400000000),'Name') ."\nWarehouse: ($cfg{'amazon_id_warehouse'}) ". &load_name('sl_warehouses','ID_warehouses',$cfg{'amazon_id_warehouse'},'Name') ."\nLocation: $cfg{'amazon_id_location'}\nQuantity: $line_qty\nCurrency Exchange: $exchange_rate\nUnit Cost: ". &format_price($cost) ."/". &format_price($sumcost)."$str_adj',Type='Low', Date = CURDATE(), Time = CURTIME(), ID_admin_users='$usr{'id_admin_users'}' ");

		## Update Status WR
		my ($sth) = &Do_SQL("UPDATE sl_wreceipts SET Status='Processed' WHERE ID_wreceipts='$cfg{'amazon_id_warehouse'}'");
		$in{'db'} = 'sl_wreceipts';
		&auth_logging('wreceipt_updated',$cfg{'amazon_id_warehouse'});
		my ($sth) = &Do_SQL("INSERT INTO sl_purchaseorders_wreceipts SET ID_purchaseorders_items='$line_idpo_items',ID_wreceipts_items = '$2', Quantity = '$line_qty', ID_products = '$id_products', ID_warehouses = '$cfg{'amazon_id_warehouse'}', Date = CURDATE(), Time = CURTIME(),ID_admin_users='$usr{'id_admin_users'}'");
		$in{'db'} = 'sl_purchaseorders';
		&auth_logging('purchaseorder_wreceipts_added',$sth->{'mysql_insertid'});
	}


	$in{'action'} = '1';
	$in{'cmd'} = "entershipment";
	$in{'tracking'} = "MO$id_orders\nESTAFETA\@$number_tracking";
	$in{'shpdate'} = "$shpdate";
	$in{'id_warehouses'} = $cfg{'amazon_id_warehouse'};
	$in{'skip_batch'} = "1";
	$in{'bulk'} = "1";
	$in{'authcode'} = "";	
	$in{'ajax'} = "1";
	


	# require "$home_dir/reports/rep_parts.cgi" if ($in{'cmd'} =~ /^rep_parts/);
	&entershipment;

	if( $va{'message'} =~ 'Invalid')
	{
		&Do_SQL("ROLLBACK;");
		return;	
	}else{
		&Do_SQL("COMMIT;");
	}

	$va{'message'} .= "<li>Warehouse created: $id_wreceipts</li>";
	$va{'message'} .= "<li>Manifest created: $id_manifests</li>";
}


1;