#############################################################################
#############################################################################
# Function: presearch_opr_returns
#
# Es: Validacion de Returns
# En: 
#
# Created on: 1/23/2013 6:46:39 PM
#
# Author: Carlos Haas
#
# Modifications:
#
# Parameters:
#
#
# Returns:
#
#
# See Also:
#
#  Todo:
#
sub presearch_opr_returns{
#############################################################################
#############################################################################
	if ($usr{'application'} eq 'crm'){
		$in{'status'} = 'Customer Service';
	}
}

#############################################################################
#############################################################################
# Function: view_opr_returns
#
# Es: Validacion de Returns
# En: 
#
# Created on: 1/23/2013 6:46:39 PM
#
# Author: Carlos Haas
#
# Modifications:
#
# Parameters:
#
#
# Returns:
#
#
# See Also:
#
#  Todo:
#
sub view_opr_returns{
#############################################################################
#############################################################################
	($in{'amount'},%fees) = &calculate_fees($in{'id_orders'},$in{'id_orders_products'});
	$in{'amount'} = &format_price($in{'amount'});
	$in{'sprice'} = &format_price($in{'sprice'});

	$va{'div_exchange'} = $in{'meraction'} eq 'Exchange' ? 'block' : 'none';
	$va{'div_reship'} = $in{'meraction'} eq 'ReShip' ? 'block' : 'none';


	if ($in{'id_products_exchange'}>0){

		$va{'id_products'} = substr($in{'id_products_exchange'},3,9);
		$va{'productsname'} = &load_name('sl_products','ID_products',$va{'id_products'},'Name');
		
	}
	$va{'id_products_exchange'} = &format_sltvid($in{'id_products_exchange'});

	## Se permite modificar el campo merAction bajo las siguientes condiciones
	## Status = 'Resolved'
	## merAction = 'Refund'
	## Permiso especial requerido opr_returns_chgstatus
	if ($in{'chgstatusto'}){
		if (&check_permissions('opr_returns_chgstatus','','') and $in{'status'} eq 'Resolved' and $in{'meraction'} eq 'Refund'){
			my ($sth)	= &Do_SQL("UPDATE sl_returns SET Status='".&filter_values($in{'chgstatusto'})."' WHERE ID_returns='$in{'view'}'");
			&auth_logging('opr_returns_chgstatus',$in{'view'});
			$in{'status'} = $in{'chgstatusto'};
			$va{'message_good'} = &trans_txt('opr_returns_chgstatus')." to ".$in{'status'};
		}else{
			$va{'message_error'} = &trans_txt('unauth_action');
		}
	}

	if (&check_permissions('opr_returns_chgstatus','','') and $in{'status'} eq 'Resolved' and $in{'meraction'} eq 'Refund'){
		my (@ary) = ('Back To Inventory');
		for (0..$#ary){
			if ($ary[$_] ne $in{'status'}){
				$va{'chgstatus'} .= qq| <a href="/cgi-bin/mod/$usr{'application'}/dbman?cmd=opr_returns&view=$in{'view'}&chgstatusto=$ary[$_]">$ary[$_]</a> &nbsp;&nbsp;&nbsp;|;
			}
		}
	}

}


#############################################################################
#############################################################################
# Function: loading_opr_returns
#
# Es: Evalua datos antes de cargar formulario de edicion de Returns
# En: 
#
# Created on: 1/23/2013 6:46:39 PM
#
# Author: Carlos Haas
#
# Modifications:
#
# Parameters:
#
#
# Returns:
#
#
# See Also:
#
#  <return_set_visibility>
#
#  Todo:
#
sub loading_opr_returns{
#############################################################################
#############################################################################

	($va{'id_creditmemos'}, $va{'already_creditmemos'}) = &get_returns_credtimemo($in{'id_returns'});
	&return_set_div_visibility();
	
}


#############################################################################
#############################################################################
# Function: validate_opr_returns
#
# Es: Validacion de Returns
# En: 
#
# Created on: 1/23/2013 6:46:39 PM
#
# Author: Carlos Haas
#
# Modifications:
# 
# 		- Last Time Modified by _RB_ on 2015-12-07: Se toma en cuenta Discount
#
# Parameters:
#
#
# Returns:
#
#
# See Also:
#
#  Todo:
#
sub validate_opr_returns{
#############################################################################
#############################################################################
	my ($err);
	

	if ($in{'add'}){

		$in{'status'} = 'New';
		(!$in{'id_customers'}) and ($in{'id_customers'} = &load_name('sl_orders','ID_orders',$in{'id_orders'},'ID_customers'));

	}elsif($in{'edit'}){
	
		if( !&transaction_validate($in{'cmd'}, $in{'id_returns'}, 'check') ){
			my $id_transaction = &transaction_validate($in{'cmd'},  $in{'id_returns'}, 'insert');
		}else{
			$va{'error'} = 'ERROR';
            $va{'message'} = &trans_txt('transaction_duplicate');
			return;
		}

		&Do_SQL("START TRANSACTION;");


		if ($in{'status'} =~ /Back to inventory|Resolved/){

			$in{'returnfee'} = 'Waived' if !$in{'returnfee'}; 
			$in{'restockfee'} = 'Waived' if !$in{'restockfee'};
			$in{'processingfee'} = 'Waived' if !$in{'processingfee'};
			$in{'oldshpreturn'} = 'Waived' if !$in{'oldshpreturn'};
			$in{'newshp'} = 'Waived' if !$in{'newshp'};

		}

		## Load not in form data
		## Cols = 'ID_returns','ID_orders_products','ID_customers','ID_orders','Amount','Type','generalpckgcondition','itemsqty','receptionnotes','merAction','workdone','ID_products_exchange','SPrice','ReturnFees','RestockFees','Processed','OldShpReturn','NewShp','AuthBy','PackingListStatus','Status','Date','Time','ID_admin_users'
		my (@savedcols);
		my ($sth) = &Do_SQL("SELECT * FROM sl_returns WHERE ID_returns = '$in{'id_returns'}';");
		my $rec_saved = $sth->fetchrow_hashref;

		if ($rec_saved->{'Status'} eq 'Repair'){

			@savedcols = ('ID_orders_products','ID_customers','ID_orders','itemsqty','receptionnotes','ID_products_exchange','ReturnFee','RestockFee','ProcessingFee','Amount','AuthBy','PackingListStatus');	

		}elsif($rec_saved->{'merAction'} eq 'Exchange'){

			@savedcols = ('ID_orders_products','ID_customers','ID_orders','itemsqty','receptionnotes','workdone','AuthBy','PackingListStatus','Amount')

		}else{

			@savedcols = ('ID_orders_products','ID_customers','ID_orders','Amount','itemsqty','receptionnotes','ID_products_exchange','workdone','AuthBy','PackingListStatus','SPrice')

		}

		for my $i(0..$#savedcols){
			$in{lc($savedcols[$i])} = $rec_saved->{$savedcols[$i]};
		}


		if($in{'status'} eq 'Void'){

			#####################
			#####################
			#####################
			###
			### Void only allowed with perms when inventory already returned to warehouse
			###
			#####################
			#####################
			#####################
			my ($sth) = &Do_SQL("SELECT COUNT(*) FROM sl_returns_upcs WHERE ID_returns = '$in{'id_returns'}' AND Status = 'Processed';");
			my ($total) = $sth->fetchrow();

			if ($total and !&check_permissions('returns_void_backtoinventory','','')){
				++$err;
				$va{'message'} = &trans_txt('returns_void_backtoinventory');
			}

		}
		

		##################################################
		##################################################
		##################################################
		##### Changing to Resolved Validation
		##################################################
		##################################################
		##################################################
		if ($rec_saved->{'Status'} eq 'Back to inventory' and ($in{'status'} eq 'Resolved' or $rec_saved->{'merAction'} eq 'To Be Determined by CR') ){
			
			if ($rec_saved->{'merAction'} eq 'Undefined yet'){ #or $rec_saved->{'merAction'} eq 'To Be Determined by CR'){

				#####################################
				#####################################
				#####################################
				### Undefined?
				#####################################
				#####################################
				#####################################
				$error{'meraction'} = &trans_txt('invalid');
				++$err;

			}elsif ($in{'meraction'} eq 'ReShip' or $rec_saved->{'merAction'} eq 'ReShip'){

				#####################################
				#####################################
				#####################################
				### ReShip
				#####################################
				#####################################
				#####################################
				my @ids_reship;
				foreach my $key (keys %in) {
				    
				    #$str .= "$key = " . $in{$key} . "\n";
					if($key =~ /^reship_(\d{1,10})$/ and $in{$key}){
						push(@ids_reship, $1);
					}

				}
			
				if(scalar @ids_reship == 0){

					$error{'status'} = &trans_txt('invalid');
					$error{'div_reship'} = &trans_txt('required');
					++$err;

				}elsif($in{'id_creditmemos'} or $in{'already_creditmemos'}){

					$error{'meraction'} = &trans_txt('invalid');
					++$err;

				}else{
				
					$in{'changed_to_resolved'} = 1;

				}

			}


			if ($rec_saved->{'merAction'} =~ /Refund|Exchange|Chargeback|To Be Determined by CR/){
	
				#####################################
				#####################################
				#####################################
				### Refund / Chargeback
				#####################################
				#####################################
				#####################################
				

				if(!$in{'id_creditmemos'} and !$in{'already_creditmemos'} and $in{'meraction'} ne 'ReShip' and $in{'status'} ne 'Void'){

					###
					### Only validate if not Credit Memo Already
					###

					if(!$in{'return_amount_net'}){

						$error{'return_amount_net'} = &trans_txt('invalid');
						++$err;

					}

					$in{'return_amount_shp'} = 0 if !$in{'return_amount_shp'};
					$in{'return_amount_tax'} = 0 if !$in{'return_amount_tax'};
					my $sumtot = round($in{'return_amount_net'} - $in{'return_amount_dis'} + $in{'return_amount_shp'} + $in{'return_amount_tax'}, 2);

					if(abs($sumtot - $in{'return_amount_total'}) > 1 or $in{'return_amount_total'}  > $in{'return_amount_max'}  or $in{'return_amount_total'} < 0){ #!$in{'return_amount_total'} or !$sumtot or

						#&cgierr("$in{'return_amount_total'} or !$sumtot or  abs($sumtot - $in{'return_amount_total'} or abs($in{'return_amount_total'} - $in{'return_amount_max'}) > 1");
						#########
						######### 1) Bad Data
						#########
						$error{'return_amount_max'} = &trans_txt('invalid');
						++$err;

					}elsif($rec_saved->{'merAction'} eq 'Chargeback'){

						#########
						######### 2) Chargeback Validation
						#########
						if(!&check_permissions('returns_chargeback','','')){

							#########
							######### 2.1) Not allowed
							#########
							++$err;

						}else{

							#########
							######### 2.2) Same amount?
							#########
							my $tot_amount = 0; my $same_amount = 0;
							my ($sth) = &Do_SQL("SELECT Amount FROM sl_orders_payments WHERE ID_orders = '$in{'id_orders'}' AND Type = 'Credit-Card' AND Status = 'Approved' AND Amount > 0 AND Captured = 'Yes' AND CapDate IS NOT NULL AND CapDate <> '' AND CapDate <> '0000-00-00' ORDER BY Amount;");
							AMOUNT:while(my ($this_amount) = $sth->fetchrow()){

								$totamt += $this_amount;
								if( abs($sumtot - $totamt) < 1 ){

									$same_amount = 1;
									last AMOUNT;

								}

							}

							if(!$same_amount){

								$error{'return_amount_max'} = &trans_txt('invalid');
								++$err;

							}

						}


					}else{

						#########
						######### 2) OK Data. Save in sl_vars
						#########
						&Do_SQL("INSERT INTO sl_vars SET VName = 'Return". $in{'id_returns'} ."', VValue = '$in{'return_amount_net'}::$in{'return_amount_dis'}::$in{'return_amount_shp'}::$in{'return_amount_tax'}::$in{'return_amount_total'}';");

					}

				}
				
			}

			if ($rec_saved->{'merAction'} eq 'Exchange'){

				#####################################
				#####################################
				#####################################
				### Exchange
				#####################################
				#####################################
				#####################################
				my ($sth) = &Do_SQL("SELECT COUNT(*) FROM sl_vars WHERE VName = 'Exchange Process' AND SubCode = '$in{'id_returns'}';");
				my ($t) = $sth->fetchrow();

				if(!$t){

					$error{'meraction'} = &trans_txt('invalid');
					$error{'id_products_exchange'} = &trans_txt('required');
					++$err;

				}
				
			}


			#####################################
			#####################################
			#####################################
			### Error validation
			#####################################
			#####################################
			#####################################
			if (!$err){
				$in{'changed_to_resolved'} = 1;
			}else{
				&Do_SQL("ROLLBACK;");
				$in{'status'} = $rec_saved->{'Status'};
				&transaction_validate($in{'cmd'}, $in{'id_returns'}, 'delete');
			}

		}

	}

	if($err) { &return_set_div_visibility(); }
	return $err;
}

#############################################################################
#############################################################################
# Function: updated_opr_returns
#
# Es: After Update
# En: 
#
# Created on: 1/23/2013 6:46:39 PM
#
# Author: Carlos Haas
#
# Modifications:
# 
# 		- Last Time Modified by _RB_ on 2015-12-07: Se toma en cuenta Discount
#
# Parameters:
#
#
# Returns:
#
#
# See Also:
#
#  Todo:
#
sub updated_opr_returns{
#############################################################################
#############################################################################
	my ($rStatus) = &load_name('sl_returns','ID_returns',$in{'id_returns'},'Status');
	my $original_action; my $err = 0;
	$va{'this_accounting_time'} = time();

	($in{'meraction'} eq 'To Be Determined by CR') and ($in{'meraction'} = 'Refund') and ($original_action = 'To Be Determined by CR');
	if ($in{'meraction'} ne 'ReShip' and /id_returns_upc_/ ~~ %in and ( $rStatus eq 'Resolved' or ( $rStatus eq 'Back to inventory' and ($cfg{'fastbackinventory'} or $cfg{'transitioninventory'}) ) ) ){

		
		##########################################
		##########################################
		##########################################
		### Se guardan los datos de los skus si es que existen cambios
		##########################################
		##########################################
		##########################################
		my $fb_done = ($in{'fastbacktoinventory_done'} and &check_permissions('returns_fastbacktoinventory_done','','')) ? 1 : 0;
		my ($status, $status_msg, $total_returned);
		
		foreach my $key (keys %in){

			if ($key =~ /cost_(\d+)/ and $1 > 0){
				my ($sth) = &Do_SQL("UPDATE sl_returns_upcs SET Cost = '".&filter_values($in{$key})."' WHERE ID_returns_upcs = '$1';");
			}elsif ($key =~ /quantity_(\d+)/ and $1 > 0){
				my ($sth) = &Do_SQL("UPDATE sl_returns_upcs SET Quantity = '$in{$key}' WHERE ID_returns_upcs = '$1';");
			}elsif ($key =~ /id_warehouses_(\d+)/ and $1 > 0){
				my ($sth) = &Do_SQL("UPDATE sl_returns_upcs SET ID_warehouses = '$in{$key}' WHERE ID_returns_upcs = '$1';");
			}elsif ($key =~ /location_(\d+)/ and $1 > 0){
				my ($sth) = &Do_SQL("UPDATE sl_returns_upcs SET Location = '". &filter_values($in{$key}) ."' WHERE ID_returns_upcs = '$1';");
			}elsif ($key =~ /inorder_(\d+)/ and $1 > 0){
				my ($sth) = &Do_SQL("UPDATE sl_returns_upcs SET InOrder = '$in{$key}' WHERE ID_returns_upcs = '$1';");
			}

			## Inventory already Returned?
			if ($fb_done){
				&Do_SQL("UPDATE sl_returns_upcs SET Status = 'Processed' WHERE ID_returns_upcs = '$1';");
				$total_returned++;
			}
		}

		##############################################
		##############################################
		##############################################
		############# Back To Inventory
		##############################################
		##############################################
		##############################################
		if (!$fb_done){

			($status, $status_msg, $total_returned) = &return_back_to_inventory($in{'id_returns'}, $in{'id_orders'});
			$va{'message'} .= ($status_msg ne '')? "<br />":"";
			$va{'message'} .= $status_msg;

		}else{
			&auth_logging('fastbacktoinventory_done',$in{'id_returns'});
		}
		
		if ($total_returned > 0){
			&Do_SQL("INSERT INTO sl_returns_notes SET ID_returns = '$in{'id_returns'}', Notes='Back to Inventory\nSkus Processed: $total_returned\n$status_msg', Type = 'Low', Date = CURDATE(), Time = CURTIME(), ID_admin_users='$usr{'id_admin_users'}';");
		}

	}elsif($rStatus eq 'Void' or ($in{'changed_to_resolved'} and $in{'meraction'} eq 'ReShip') ){

		#########
		######### Drop Any sl_vars record
		#########
		&Do_SQL("DELETE FROM sl_vars WHERE VName = 'Exchange Process' AND SubCode = '$in{'id_returns'}';");

		#########
		######### Deactivate sl_returns_upcs records
		#########
		&Do_SQL("UPDATE sl_returns_upcs SET Status = 'Processed' WHERE ID_returns = '$in{'id_returns'}';");

		#########
		######### Note
		#########
		
		&add_order_notes_by_type($in{'id_orders'},"Return Proccess finished as: $rStatus / $in{'meraction'}","Low");
	}


	####
	#### Validacion de Inventario Ingresado
	####
	my ($sth) = &Do_SQL("SELECT COUNT(*) FROM sl_returns_upcs WHERE ID_returns = '". $in{'id_returns'} ."' AND Status  = 'TBD';");
	my ($pending_inventory) = $sth->fetchrow();


	if($in{'changed_to_resolved'} and $rStatus ne 'Void' and !$pending_inventory){

		if($in{'meraction'} =~ /Return to Customer|Repair Center|ReShip|Void/){

			if ($in{'meraction'} eq 'ReShip') { &return_reship(); }
			&Do_SQL("COMMIT;");
			&transaction_validate($in{'cmd'}, $in{'id_returns'}, 'delete');
			
		}else{			

			my $flag_accounting = 0;

			########
			######## 1) CreditMemo
			########
			my ($id_creditmemos, $already_creditmemos) = &return_creditmemo($in{'id_returns'}, $in{'return_amount_net'}, $in{'return_amount_dis'}, $in{'return_amount_shp'}, $in{'return_amount_tax'}, $in{'return_amount_total'}); ## Applies Both Exchange and Refund?

			if($id_creditmemos){

				#&cgierr("$id_creditmemos, $already_creditmemos");
				########
				######## 2) Cambio Fisico
				########
				my $exchange_res = &return_exchange($in{'id_returns'});


				########
				######## 3) Movimientos Contables | Devolucion + CF (si es necesaro)
				########

				#####
				##### 3.1) Sumatoria final
				#####
				$sumatoria = 0;#&orderbalance($id_orders);

				if(!$already_creditmemos){

					#####
		      		##### 3.2) Movimientos Contables
					#####

					my ($order_type, $ctype, $ptype,@params);
					my $id_orders = $in{'id_orders'} ? int($in{'id_orders'}) : &load_name('sl_returns', 'ID_returns', $in{'id_returns'}, 'ID_orders');
					my ($sth) = &Do_SQL("SELECT Ptype, Type FROM sl_orders INNER JOIN sl_customers USING(ID_customers) WHERE ID_orders = '$id_orders';");
					($order_type, $ctype) = $sth->fetchrow();

					########
					######## 3.2.1) Movimientos Contables (Devolucion)
					########
					my @params = ($id_orders);
					my ($this_acc_status, $this_acc_str) = &accounting_keypoints('order_products_returned_'. $ctype .'_'. $order_type, \@params );
					$flag_accounting++ if $this_acc_status;

					########
					######## 3.2.2) Movimientos Contables (Devolucion Finalizada)
					########
					my $amount_toreturn = $sumatoria > 0 ? 0 : $sumatoria;
					@params = ($id_orders,$in{'meraction'},0,$amount_toreturn);
					($this_acc_status, $this_acc_str) = &accounting_keypoints('order_products_returnsolved_'. $ctype .'_'. $order_type, \@params );
					$flag_accounting++ if $this_acc_status;					

					########
					######## 3.2.3) Actualizacion de tablerelated (Devolucion Finalizada)
					########
					&Do_SQL("UPDATE sl_movements SET tablerelated = 'sl_creditmemos', ID_tablerelated = '$id_creditmemos' WHERE ID_tableused = '$id_orders' AND tableused = 'sl_orders' AND ID_tablerelated = 0 AND Status = 'Active' AND TIMESTAMPDIFF(SECOND,CONCAT(Date,' ',TIME),NOW()) BETWEEN 0 AND 50;");

					########
					######## 4) Credit Memo (Fiscal)
					########
					&export_info_for_credits_notes($id_creditmemos);

				}

				########
				######## 5) Recalc Totals
				########
				&recalc_totals($id_orders);

				########
				######## 6) Back to Inventory + $original_action
				########
				if($original_action and $rStatus eq 'Back to inventory'){

					&Do_SQL("UPDATE sl_returns SET merAction = '". $in{'meraction'} ."' WHERE ID_returns = '". $in{'id_returns'} ."';");

				}

				if( lc($in{'meraction'}) eq 'chargeback'){

					if(&check_permissions('opr_orders_chargebacks','','')){

						my ($sth) = &Do_SQL("SELECT ID_orders_payments, ABS(Amount) FROM sl_orders_payments WHERE ID_orders = '". $in{'id_orders'} ."' AND Amount < 0 AND Status = 'Credit' AND (Captured IS NULL OR Captured = 'No') AND (CapDate = '0000-00-00' OR CapDate IS NULL) ORDER BY ID_orders_payments DESC LIMIT 1;");
						my ($id_orders_payments, $amount) = $sth->fetchrow();

						my ($sth) = &Do_SQL("SELECT ID_orders_payments FROM sl_orders_payments WHERE ID_orders = '". $in{'id_orders'} ."' AND ABS(Amount - ". $amount .") < 1 AND Status = 'Approved' AND LENGTH(PmtField3) >= 13 AND Captured = 'Yes' AND CapDate <> '0000-00-00' AND LENGTH(AuthCode) >= 2 AND AuthCode <> '0000' ORDER BY ID_orders_payments DESC LIMIT 1;");
						my ($id_original_payment) = $sth->fetchrow();					

						my ($sth) = &Do_SQL("SELECT ID_movements FROM sl_movements WHERE ID_tableused = '". $in{'id_orders'} ."' AND tableused = 'sl_orders' AND ABS(Amount - ". $amount .") < 1 AND Status = 'Pending' AND Credebit = 'Debit';");

						my ($id_movements) = $sth->fetchrow();

						if($id_orders_payments and $id_movements and $id_original_payment){			

							## 7.3 Contabilidad
							my ($order_type, $ctype,@params);
							my ($sth) = &Do_SQL("SELECT Ptype, Type FROM sl_orders INNER JOIN sl_customers USING(ID_customers) WHERE ID_orders = '". $in{'id_orders'} ."';");
							($order_type, $ctype) = $sth->fetchrow();
							@params = ($in{'id_orders'}, $id_orders_payments, 1, lc($in{'meraction'}),1);
							my ($stacc_open,$msg_open) = &accounting_keypoints('order_chargeback_open_'. $ctype .'_'. $order_type , \@params);
							$flag_accounting += $stacc;
							sleep(1);
							my ($stacc_close,$msg_close) = &accounting_keypoints('order_chargeback_close_'. $ctype .'_'. $order_type , \@params);

							if(!$flag_accounting){

								my $bankdate = $in{'bankdate'} ? $in{'bankdate'} : &get_aql_date();
								## 7.1 Capture Payment
								&Do_SQL("UPDATE sl_orders_payments SET Captured = 'Yes', CapDate = '". $bankdate ."', Paymentdate = '". $bankdate ."' WHERE ID_orders = '". $in{'id_orders'} ."' AND ID_orders_payments = '". $id_orders_payments ."';");
								## 7.2 Order
								&Do_SQL("UPDATE sl_orders SET StatusPrd = 'None', StatusPay = 'None' WHERE ID_orders = '". $in{'id_orders'} ."';");
								## 7.3 Order Note
								
								&add_order_notes_by_type($in{'id_orders'},&trans_txt('opr_returns_resolved_chargeback'),"Low");
							}

						}elsif(!$id_orders_payments){

							$va{'message'} = &trans_txt('returns_chargeback_nocredit');
							&Do_SQL("ROLLBACK;");
							++$err;
							&transaction_validate($in{'cmd'}, $in{'id_returns'}, 'delete');

						}elsif(!$id_movements){

							$va{'message'} = &trans_txt('returns_chargeback_nomovement');
							&Do_SQL("ROLLBACK;");
							++$err;
							&transaction_validate($in{'cmd'}, $in{'id_returns'}, 'delete');

						}elsif(!$id_original_payment){

							$va{'message'} = &trans_txt('returns_chargeback_nooriginal');
							&Do_SQL("ROLLBACK;");
							++$err;
							&transaction_validate($in{'cmd'}, $in{'id_returns'}, 'delete');

						}

					}else{

						## No Permisos de aplicacion
						$va{'message'} = &trans_txt('perms_insufficient_perms');
						&Do_SQL("ROLLBACK;");
						++$err;
						&transaction_validate($in{'cmd'}, $in{'id_returns'}, 'delete');

					}

				}

				if($flag_accounting){

					## Problema contable
					$va{'message'} = &trans_txt('acc_error');
					&Do_SQL("ROLLBACK;");
					&transaction_validate($in{'cmd'}, $in{'id_returns'}, 'delete');

				}elsif(!$err){

					## Todo OK
					&Do_SQL("COMMIT;");
					&transaction_validate($in{'cmd'}, $in{'id_returns'}, 'delete');

				}

			}elsif(!$already_creditmemos){

				&Do_SQL("ROLLBACK;");
				$va{'message'} = &trans_txt('returns_creditmemo_generalerror');
				&transaction_validate($in{'cmd'}, $in{'id_returns'}, 'delete');

			}

		}

	}elsif(!$in{'changed_to_resolved'} ){

		## Simple update sin resolucion
		&Do_SQL("COMMIT;");
		&transaction_validate($in{'cmd'}, $in{'id_returns'}, 'delete');

	}elsif($in{'status'} eq 'Void'){

		## Simple update Void
		&Do_SQL("COMMIT;");
		&transaction_validate($in{'cmd'}, $in{'id_returns'}, 'delete');

	}else{

		## Problema al resolver
		$va{'message'} = &trans_txt('returns_creditmemo_generalerror');
		&Do_SQL("ROLLBACK;");
		&transaction_validate($in{'cmd'}, $in{'id_returns'}, 'delete');

	}

	## Secure Commit
	&Do_SQL("COMMIT;");
	&transaction_validate($in{'cmd'}, $in{'id_returns'}, 'delete');
}


#############################################################################
#############################################################################
# Function: return_set_div_visibility
#
# Es: Carga el Menu form que corresponde al status del return
# En: 
#
# Created on: 1/23/2013 6:46:43 PM
#
# Author: Carlos Haas
#
# Modifications:
#
# Parameters:
#
#
# Returns:
#
#
# See Also:
#
#  <loading_opr_returns>
#
#  Todo:
#
sub return_set_div_visibility{
#############################################################################

	#&cgierr($va{'id_creditmemos'}); !$va{'id_creditmemos'} and 
	#my ($id_creditmemos, $already) = &get_returns_credtimemo($in{'id_returns'});
	$va{'div_return'} = ($in{'meraction'} =~ /Exchange|Refund|Chargeback|To Be Determined by CR/) ? 'block' : 'none'; #activa seccion en Exchange|Refund
	$va{'div_exchange'} = $in{'meraction'} eq 'Exchange' ? 'block' : 'none'; #activa seccion en Exchange
	$va{'div_reship'} = $in{'meraction'} eq 'ReShip' ? 'block' : 'none'; #activa seccion en ReShip
	
	$va{'fc_return_products'} = $in{'meraction'} =~ /Exchange|Refund|Chargeback|To Be Determined by CR/ ? &return_products($va{'id_creditmemos'}) : ''; # Ejecuta funcion en Exchange|Refund
	$va{'fc_reship'} = $in{'meraction'} eq 'ReShip' ? &return_reship_products() : ''; # Ejecuta funcion en ReShip
	$va{'ids_autocomplete'} = $in{'meraction'} eq 'Exchange' ? &return_exchange_products() : ''; # Ejecuta funcion en Exchange
	$va{'ids_in'} = $in{'meraction'} eq 'Exchange' ? &get_edit_returns_exchange_lines($in{'id_returns'}) : '';# Ejecuta funcion en Exchange
	($va{'ids_in'}) and ($va{'div_height'} += 70);
	$va{'style_fastbacktoinventory_done'} = &check_permissions('returns_fastbacktoinventory_done','','') ? 'inline' : 'none';

}


#############################################################################
#############################################################################
# Function: dynamic_returns_form
#
# Es: Carga el Menu form que corresponde al status del return
# En: 
#
# Created on: 1/23/2013 6:46:43 PM
#
# Author: Carlos Haas
#
# Modifications:
#
# Parameters:
#
#
# Returns:
#
#
# See Also:
#
#  Todo:
#
sub dynamic_returns_form{
#############################################################################
#############################################################################
	if($in{'add'}){

		if($in{'id_customers'}){
			$va{'customername'} = &load_db_names('sl_customers','ID_customers',$in{'id_customers'},'[FirstName] [LastName1] [LastName2]');
		}
		
		return &build_page("forms:returns_add_form.html");
	}elsif($in{'search'}){
		return &build_page("forms:returns_search.html");
	}elsif($in{'status'} eq 'Back to inventory'){
		$va{'tax_default'}=$cfg{'taxp_default'};
		return &build_page("forms:returns_binventory_form.html");
	}elsif($in{'status'} eq 'Resolved'){
		return &build_page("forms:returns_resolved.html");
	}else{
		if ($in{'status'} eq 'New'){
			if ($in{'id_orders_products'}){
				$va{'order_prod'} = "p".$in{'id_orders_products'};
			}elsif($in{'id_orders'}){
				$va{'order_prod'} = "o".$in{'id_orders'};
			}
			return &build_page("forms:returns_new_form.html");
		}elsif($in{'status'} eq 'Pending Refunds' or $in{'status'} eq 'Pending Payments'){
			return &build_page("forms:returns_payment_view.html");
		}elsif($in{'meraction'} eq 'Exchange'){
			return &build_page("forms:returns_exchange_form.html");
		}elsif($in{'meraction'} eq 'Repair Center' or $in{'status'} eq 'Repair'){
			return &build_page("forms:returns_repair_form.html");
		}else{
			return &build_page("forms:returns_gen_form.html");
		}
	}
}

#############################################################################
#############################################################################
# Function: dynamic_returns_view
#
# Es: Carga el Menu form que corresponde al status del return
# En: 
#
# Created on: 1/23/2013 6:46:46 PM
#
# Author: Carlos Haas
#
# Modifications:
#
# Parameters:
#
#
# Returns:
#
#
# See Also:
#
#  Todo:
#
sub dynamic_returns_view{
#############################################################################
#############################################################################
	if ($in{'status'} eq 'Pending Refunds' or $in{'status'} eq 'Pending Payments'){
			return &build_page("forms:returns_payment_view.html");
	}elsif($in{'meraction'} eq 'Exchange'){
		return &build_page("forms:returns_exchange_view.html");
	}elsif($in{'meraction'} eq 'Repair Center' or $in{'status'} eq 'Repair'){
			return &build_page("forms:returns_repair_view.html");
	}else{
		return &build_page("forms:returns_gen_view.html");
	}
}

sub returns_itemsordered{
# --------------------------------------------------------

	my $output = return_order_products_info();
	return $output;

	#############
	############# NOTA!!! Esta funcion dejo de ser utilizada en favor de la de la linea arriba
	#############

	my $outputsh,$query; 
	my ($sth) = &Do_SQL("SELECT * FROM sl_orders WHERE ID_customers='$in{'id_customers'}' AND Status='Shipped' $query");
	$va{'matches'} = $sth->fetchrow();
	if ($va{'matches'}>0){
		my ($sth) = &Do_SQL("SELECT * FROM sl_orders WHERE ID_customers='$in{'id_customers'}' AND Status = 'Shipped' ORDER BY Date;");
		while ($rec = $sth->fetchrow_hashref){
			$d = 1 - $d;
			$outputsh .= "<tr bgcolor='$c[$d]'>\n";
			$outputsh .= "  <td class='smalltext' valign='top' align='center' nowrap>";
			$outputsh .= "<input type='radio' class='radio' name='order_prod' value='o$rec->{'ID_orders'}'><br>" if($in{'status'} eq 'New' and $in{'modify'});
			$outputsh .= "<a href='/cgi-bin/mod/$usr{'application'}/dbman?cmd=opr_orders&view=$rec->{'ID_orders'}' name='idorder' id='idorder'>$rec->{'ID_orders'}</a><br>";
			$outputsh .= qq|<a href="#idorder" id='ajax_btn' onClick="popup_show('ajax_windows', 'ajax_drag', 'ajax_exit', 'element-right', -1, -1,'idorder');loadDoc('/cgi-bin/common/apps/ajaxbuild?ajaxbuild=orders_viewnotes&id_orders=$rec->{'ID_orders'}');"><img src='$va{'imgurl'}/$usr{'pref_style'}/b_notes.gif' title='View Notes' alt='' border='0'></a><br>|;
			$outputsh .= "</td>\n";
			$outputsh .= "  <td class='smalltext' valign='top' nowrap>$rec->{'Date'}</td>\n";
			$outputsh .= "  <td class='smalltext' valign='top'>".&return_skusordered($rec->{'ID_orders'})."</td>\n";
			$outputsh .= "</tr>\n";
		}
	}else{
		$va{'pageslist'} = 1;
		$outputsh = qq|
		<tr>
			<td colspan='5' align="center">|.&trans_txt('search_nomatches').qq|</td>
		</tr>\n|;
	}
	return $outputsh;
}

sub return_skusordered {
# --------------------------------------------------------
	my ($id_order) = @_;
	my ($output, $id_orders_products);
	#my ($sth) = &Do_SQL("SELECT * FROM sl_orders_products LEFT JOIN sl_skus ON sl_orders_products.ID_products=sl_skus.ID_sku_products WHERE ID_orders=$id_order;");
	my ($sth) = &Do_SQL("SELECT sl_orders_products.ID_products, sl_orders_parts.ID_orders_products,sl_orders_parts.Tracking, sl_orders_parts.ShpProvider, sl_orders_parts.ShpDate, Model, Name, sl_orders_parts.Quantity, sl_parts.ID_parts, (SELECT UPC FROM sl_skus WHERE ID_sku_products=400000000+sl_parts.ID_parts) AS UPC FROM sl_orders_products LEFT JOIN sl_orders_parts ON sl_orders_products.ID_orders_products=sl_orders_parts.ID_orders_products  LEFT JOIN sl_parts ON sl_parts.ID_parts=sl_orders_parts.ID_parts WHERE ID_orders=$id_order;");
	while ($rec = $sth->fetchrow_hashref){
		(!$rec->{'UPC'}) and ($rec->{'UPC'} = '---');
		if ($id_orders_products ne $rec->{'ID_orders_products'}){
			$output .= "<tr>\n";
			$output .= "   <td class='smalltext' valign='top' nowrap colspan='2'>";
			$output .= "<input type='radio' class='radio' name='order_prod' value='p$rec->{'ID_orders_products'}'> " if($in{'status'} eq 'New' and $in{'modify'});
			$output .= "<b>" if ($in{'id_orders_products'} eq $rec->{'ID_orders_products'});
			$output .=  &load_name('sl_products','ID_products',substr($rec->{'ID_products'},3,8),'Name')." &nbsp; (<a href='/cgi-bin/mod/$usr{'application'}/dbman?cmd=mer_products&view=".substr($rec->{'ID_products'},3,8)."'>". &format_sltvid(substr($rec->{'ID_products'},3,8))."</a>)</td>\n";
			$output .= "</b>" if ($in{'id_orders_products'} eq $rec->{'ID_orders_products'});
			$output .= "</tr>\n";			
		}
		$output .= "<tr>\n";
		$output .= "   <td class='smalltext' valign='top' nowrap>$rec->{'Quantity'} x $rec->{'Name'}<br>&nbsp;&nbsp;&nbsp;&nbsp; ID : <a href='/cgi-bin/mod/$usr{'application'}/dbman?cmd=mer_parts&view=$rec->{'ID_parts'}'>".&format_sltvid(400000000+$rec->{'ID_parts'})."</a><br>&nbsp;&nbsp;&nbsp;&nbsp; <font color='red'>UPC: $rec->{'UPC'}</font></td>\n";
		$output .= "   <td class='smalltext' valign='top'>$rec->{'ShpProvider'}<br>$rec->{'Tracking'}<br>$rec->{'ShpDate'}</td>\n";
		$output .= "</tr>\n";
		$id_orders_products = $rec->{'ID_orders_products'};
	}
	if ($output){
		return qq|<table border="0" cellspacing="0" cellpadding="2" width="100%">\n| . $output . "</table>\n";
	}else{
		return qq|<table border="0" cellspacing="0" cellpadding="2" width="100%">\n<tr>\n<td align="center">|.&trans_txt('search_nomatches')."</td>\n	</tr></table>\n";
	}
}


#########################################################################################################
#########################################################################################################
#
#	Function: return_order_products_info
#   		
#		sp: Recibe items para devolucion wholesale / retail
#
#	Created by:
#		_Roberto Barcenas_
#
#	Modified By:
#
#   	Parameters:
#		id_orders: ID_orders
#
#   	Returns:
#		None
#
#   	See Also:
#
sub return_order_products_info {
#########################################################################################################
#########################################################################################################

	my $id_orders = $in{'id_orders'};
	my $id_orders_products = 0;
	my ($sth) = &Do_SQL("SELECT 
							sl_orders_products.ID_products
							, sl_orders_parts.ID_orders_products
							, sl_parts.ID_parts
							, sl_orders_parts.Tracking
							, sl_orders_parts.ShpProvider
							, sl_orders_parts.ShpDate
							, Model
							, Name
							, sl_orders_parts.Quantity
							, sl_orders_parts.Cost
							, (SELECT UPC FROM sl_skus WHERE ID_sku_products=400000000+sl_parts.ID_parts) AS UPC 
							FROM sl_orders_products LEFT JOIN sl_orders_parts USING(ID_orders_products)  
							LEFT JOIN sl_parts USING(ID_parts) WHERE ID_orders = '$id_orders';");
	while ($rec = $sth->fetchrow_hashref){

		(!$rec->{'UPC'}) and ($rec->{'UPC'} = '---');
		
		if ($id_orders_products ne $rec->{'ID_orders_products'}){

			if($id_orders_products > 0){

				$output .= "</td></tr>\n";

			}

			my $cost_adj = 0;
			($rec->{'Cost'}, $cost_adj) = &load_sltvcost(400000000 + $rec->{'ID_parts'}) if !$rec->{'Cost'};
			my $pname = substr($rec->{'ID_products'},0,1) ne '6' ? &load_name('sl_products','ID_products',substr($rec->{'ID_products'},-6),'Name') : &load_name('sl_services','ID_services',substr($rec->{'ID_products'},-4),'Name');
			$output .= qq|<tr>\n|;
			$output .= qq|   <td class='smalltext' valign='top' nowrap colspan='2'></td>\n|;
			$output .= qq|		<td class='smalltext' valign='top' nowrap><b>|. $pname ." </b>&nbsp; (<a href='/cgi-bin/mod/$usr{'application'}/dbman?cmd=mer_products&view=".substr($rec->{'ID_products'},3,8)."'>". &format_sltvid($rec->{'ID_products'}) .qq|</a>)<br>|;
			$id_orders_products = $rec->{'ID_orders_products'}

		}

		$output .= qq|   &nbsp;&nbsp;&nbsp;&nbsp;$rec->{'Quantity'} x $rec->{'Name'}&nbsp;&nbsp;\|&nbsp;&nbsp;ID: <a href='/cgi-bin/mod/$usr{'application'}/dbman?cmd=mer_parts&view=$rec->{'ID_parts'}'>|.&format_sltvid(400000000+$rec->{'ID_parts'}).qq|</a>&nbsp;&nbsp;\|<b>&nbsp;&nbsp;<b>UPC:</b> $rec->{'UPC'}&nbsp;&nbsp;\|<b>&nbsp;&nbsp;<b>Cost:</b> |. &format_price($rec->{'Cost'}) .qq| &nbsp;&nbsp;\|<b>&nbsp;&nbsp; <b>ShpDate:</b> $rec->{'ShpDate'}<br>\n|;
	
	}

	$output = qq|</td><tr>\n<td class='smalltext' valign='top' nowrap><a href="/cgi-bin/mod/$usr{'application'}/dbman?cmd=opr_orders&view=$id_orders">$id_orders</a></td>\n<td class='smalltext' valign='top' nowrap>|. &load_name('sl_orders','ID_orders',$id_orders,'Date') .qq|</td>\n</tr>| . $output;

	return $output;

}


#########################################################################################################
#########################################################################################################
#
#	Function: return_products
#   		
#		sp: Imprime tabla con productos y servicios enviados disponibles para posible devolucion
#
#	Created by:
#		_Roberto Barcenas_
#
#	Modified By:
#
#   	Parameters:
#		id_orders: ID_orders
#
#   	Returns:
#		None
#
#   	See Also:
#
sub return_products {
#########################################################################################################
#########################################################################################################

	my ($id_creditmemos) = @_;
	
	$id_creditmemos = 0 if !$id_creditmemos;
	my $id_orders = $in{'id_orders'};
	my $modquery = $id_creditmemos ? " AND SalePrice < 0 AND sl_orders_products.Status = 'Returned' AND sl_orders_products.ID_products > 800000000 AND Related_ID_products = '$id_creditmemos' " : " AND SalePrice >= 0 AND sl_orders_products.Status IN('Active','ReShip','Exchange') ";
	my $amount = 0; my $discount = 0; my $tax = 0; my $amount_total = 0;
	my $output;

	my ($sth) = &Do_SQL("SELECT 
							sl_orders_products.ID_orders_products
							, sl_orders_products.ID_products
							, SalePrice
							, sl_orders_products.Discount
							, Shipping
							, sl_orders_products.Tax
							, ShpTax
							, sl_orders_parts.ShpDate
							, IF(sl_products.Name IS NULL, IF(sl_services.Name IS NULL AND $id_creditmemos > 0, 'Credito Memo', sl_services.Name) ,sl_products.Name) AS Name
							, choice1
							, choice2
							, choice3
							, sl_orders_products.Quantity
							FROM sl_orders_products
							LEFT JOIN sl_services ON sl_orders_products.ID_products = 600000000 + sl_services.ID_services
							LEFT JOIN sl_skus ON sl_orders_products.ID_products = ID_sku_products
							LEFT JOIN sl_orders_parts USING(ID_orders_products) 
							LEFT JOIN sl_products ON sl_products.ID_products = RIGHT(sl_orders_products.ID_products,6) 
							WHERE 
								ID_orders = '$id_orders' 
								$modquery
							GROUP BY sl_orders_products.ID_orders_products
							ORDER BY sl_orders_parts.ShpDate <> NULL, sl_orders_products.ID_orders_products;");
	while (my ($id_orders_products, $id_products, $sprice, $this_discount, $this_shipping, $this_tax, $shptax, $shpdate, $pname, $c1, $c2, $c3, $quantity ) = $sth->fetchrow() ){

		$pname .= ' ' . $c1 . ' ' . $c2 . ' ' . $c3;
		$output .= qq|<tr>\n|;

		my $outputsh = (!$id_creditmemos and $this_shipping > 0) ?
						qq|   <td class='smalltext' valign='top' nowrap align="center"><input type="checkbox" class="checkbox" id="id_return_shipping_|. $id_orders_products .qq|" name="return_shipping_|. $id_orders_products .qq|" value="|. $this_shipping.qq|">
								<input type="hidden" id="id_return_shptax_|. $id_orders_products .qq|" name="return_shptax_|. $id_orders_products .qq|" value="|. $shptax .qq|" </td>\n| :
						qq|   <td class='smalltext' valign='top' nowrap align="center">&nbsp;</td>\n|;


		$output .= (!$id_creditmemos) ? 
						qq|   <td class='smalltext' valign='top' nowrap align="center">
								<input type="checkbox" class="checkbox" id="id_return_sprice_|. $id_orders_products .qq|" name="return_sprice_|. $id_orders_products .qq|" value="|. $sprice .qq|">\n
								<input type="hidden" id="id_return_tax_|. $id_orders_products .qq|" name="return_tax_|. $id_orders_products .qq|" value="|. $this_tax .qq|" </td>\n
								<input type="hidden" id="id_return_dis_|. $id_orders_products .qq|" name="return_dis_|. $id_orders_products .qq|" value="|. $this_discount .qq|" </td>\n| :
						qq|   <td class='smalltext' valign='top' nowrap align="center">&nbsp;</td>\n|;							

		$output .= $outputsh;
		$output .= qq|   <td class='smalltext' valign='top' nowrap align="left"><a href="/cgi-bin/mod/$usr{'application'}/dbman?cmd=mer_products&view=|. substr($id_products,-6) .qq|">|. &format_sltvid($id_products) .qq|</a></td>\n|;
		$output .= qq|	 <td class='smalltext' valign='top' nowrap align="left"><b>|. $pname .qq|</b></td>\n|;
		$output .= qq|	 <td class='smalltext' valign='top' nowrap align="left"><b>|. $quantity .qq|</b></td>\n|;
		$output .= qq|	 <td class='smalltext' valign='top' nowrap align="right"><b>|. &format_price($sprice) .qq|</b></td>\n|;
		$output .= qq|	 <td class='smalltext' valign='top' nowrap align="right">|. &format_price($this_discount) .qq|</td>\n|;
		$output .= qq|	 <td class='smalltext' valign='top' nowrap align="right"><b>|. &format_price($this_tax + $shptax) .qq|</b></td>\n|;
		$output .= qq|	 <td class='smalltext' valign='top' nowrap align="right"><b>|. &format_price($this_shipping) .qq|</b></td>\n|;
		$output .= qq|</tr>\n|;
		$amount += round($sprice,2);
		$discount += round($this_discount,2);
		$tax += round($this_tax + $shptax,2);
		$amount_total += round($this_shipping,2);
	
	}
	$amount_total += ($amount - $discount + $tax);


	if(!$output){

		$output .= qq|<tr>\n|;
		$output .= qq|	 <td class='smalltext' valign='top' nowrap align="center" colspan="9"><b>|. &trans_txt('returns_reship_no_products_available') .qq|</b></td>\n|;
		$output .= qq|</tr>\n|;

	}else{

		if(!$id_creditmemos){

			$output .= qq|<tr>
							<td class="menu_bar_title" colspan="7"></td>\n
							<td class="menu_bar_title">Order Net:</td>\n
							<td class="menu_bar_title" align="right"><input type="text" class="text" size="10" id="id_return_amount_net" name="return_amount_net" value="|. 0 .qq|"></td>\n
						</tr>
						<tr>
							<td class="menu_bar_title" colspan="7"></td>\n
							<td class="menu_bar_title">Discount:</td>\n
							<td class="menu_bar_title" align="right"><input type="text" class="text" size="10" id="id_return_amount_dis" name="return_amount_dis" value="|. 0 .qq|" ></td>\n
						</tr>
						<tr>
							<td class="menu_bar_title" colspan="7"><span></td>\n
							<td class="menu_bar_title">S & H:</td>\n
							<td class="menu_bar_title" align="right"><input type="text" class="text" size="10" id="id_return_amount_shp" name="return_amount_shp" value="|. 0 .qq|"></td>\n
						</tr>
						<tr>
							<td class="menu_bar_title" colspan="7"><span style="float:right; text-decoration: underline;padding-right:10px;color:#fff82b;font-weight:bold" id="spn_id_return_amount_tax"><span></td>\n
							<td class="menu_bar_title">Tax:</td>\n
							<td class="menu_bar_title" align="right"><input type="text" class="text" size="10" id="id_return_amount_tax" name="return_amount_tax" value="|. 0 .qq|"></td>\n
						</tr>
						<tr>
							<td class="menu_bar_title" colspan="7"><span style="float:right; text-decoration: underline;padding-right:10px;color:#fff82b;font-weight:bold" id="spn_id_return_amount_total"><span></td>\n
							<td class="menu_bar_title">
								<span class="smallfieldterr">[er_return_amount_max]</span>
								Total:
							</td>\n
							<td class="menu_bar_title" align="right">
								<input type="text" class="text" size="10" id="id_return_amount_total" name="return_amount_total" value="|. 0 .qq|">
								<input type="hidden" id="return_amount_max" name="return_amount_max" value="$amount_total">
							</td>\n
						</tr>|;

		}else{

			$output .= qq|<tr>
							<td class="menu_bar_title" colspan="7">&nbsp;</td>\n
							<td class="menu_bar_title">Total:</td>\n
							<td class="menu_bar_title" align="right">|. &format_price($amount_total) .qq|</td>\n
						</tr>|;

		}

	}

	return $output;
}


#########################################################################################################
#########################################################################################################
#
#	Function: return_reship_products
#   		
#		sp: Imprime tabla con productos habilitados para reenvio
#
#	Created by:
#		_Roberto Barcenas_
#
#	Modified By:
#
#   	Parameters:
#		id_orders: ID_orders
#
#   	Returns:
#		None
#
#   	See Also:
#
sub return_reship_products {
#########################################################################################################
#########################################################################################################


	my $id_orders = $in{'id_orders'};
	my $output;
	my ($sth) = &Do_SQL("SELECT 
							sl_orders_products.ID_orders_products
							, sl_orders_products.ID_products
							, SalePrice
							, sl_orders_parts.ShpDate
							, Name
							, sl_orders_products.Quantity
							FROM sl_orders_products INNER JOIN sl_orders_parts USING(ID_orders_products) 
							INNER JOIN sl_products ON sl_products.ID_products = RIGHT(sl_orders_products.ID_products,6) 
							WHERE ID_orders = '$id_orders' GROUP BY sl_orders_products.ID_orders_products
							ORDER BY sl_orders_parts.ShpDate, sl_orders_products.ID_orders_products;");
	while (my ($id_orders_products, $id_products, $sprice, $shpdate, $pname, $quantity ) = $sth->fetchrow() ){

		$output .= qq|<tr>\n|;
		$output .= qq|   <td class='smalltext' valign='top' nowrap align="center"><input type="checkbox" class="checkbox" name="reship_|. $id_orders_products .qq|" value="1" checked="checked"></td>\n|;
		$output .= qq|   <td class='smalltext' valign='top' nowrap align="left"><a href="/cgi-bin/mod/$usr{'application'}/dbman?cmd=mer_products&view=|. substr($id_products,-6) .qq|">|. &format_sltvid($id_products) .qq|</a></td>\n|;
		$output .= qq|	 <td class='smalltext' valign='top' nowrap align="left"><b>|. $pname .qq|</b></td>\n|;
		$output .= qq|	 <td class='smalltext' valign='top' nowrap align="left"><b>|. $quantity .qq|</b></td>\n|;
		$output .= qq|	 <td class='smalltext' valign='top' nowrap align="right"><b>|. &format_price($sprice) .qq|</b></td>\n|;
		$output .= qq|</tr>\n|;
	
	}

	if(!$output){

		$output .= qq|<tr>\n|;
		$output .= qq|	 <td class='smalltext' valign='top' nowrap align="center" colspan="5"><b>|. &trans_txt('returns_reship_no_products_available') .qq|</b></td>\n|;
		$output .= qq|</tr>\n|;

	}

	return $output;
}


#########################################################################################################
#########################################################################################################
#
#	Function: return_exchange_products
#   		
#		sp: Carga en String todos los productos disponibles para CF
#
#	Created by:
#		_Roberto Barcenas_
#
#	Modified By:
#
#   	Parameters:
#		
#
#   	Returns:
#		None
#
#   	See Also:
#
sub return_exchange_products {
#########################################################################################################
#########################################################################################################

	my $ids_autocomplete;
	my ($sth) = &Do_SQL("SELECT 
							ID_sku_products
							, CONCAT(Name,' ', IF(choice1 IS NOT NULL,choice1,''), ' ', IF(choice2 IS NOT NULL,choice2,''), IF(choice3 IS NOT NULL,choice3,'') )AS Name
							, sl_products.Status 
						FROM sl_products INNER JOIN sl_skus USING(ID_products)
						WHERE sl_products.Status IN ('On-Air','Active','Inactive')	
						ORDER BY Name, ID_sku_products;");
	
	while (my($id_products, $name, $st) = $sth->fetchrow()){
			$ids_autocomplete .= '"'.$id_products.' @@ '.&filter_values($name).' @@ '. $st .'",';			
	}
	chop($ids_autocomplete);
	#&cgierr($va{'ids_autocomplete'});

	return $ids_autocomplete;
}


sub customerdata {
# --------------------------------------------------------
# Created by: Jose Ramirez Garcia
# Created on: 30abr2008
# Description : It shows the customer data
# Notes : (Modified on : Modified by :)

	if(!$in{'id_customers'} && $in{'id_returns'}){
		my ($sth0) = &Do_SQL("SELECT COUNT(*) FROM sl_returns WHERE ID_returns='$in{'id_returns'}'");
		if ($sth0->fetchrow() >0){
			my ($sth0) = &Do_SQL("SELECT ID_orders FROM sl_returns,sl_orders_products WHERE sl_orders_products.ID_orders_products=sl_returns.ID_orders_products AND ID_returns='$in{'id_returns'}'");
			$in{'id_orders'} = $sth0->fetchrow();
			$in{'id_customers'} = &load_name('sl_orders','ID_orders',$in{'id_orders'},'ID_customers');
		}
	}
	
	if ($in{'id_customers'} ){
		my ($sth) = &Do_SQL("SELECT COUNT(*) FROM sl_customers WHERE id_customers='$in{'id_customers'}'");
		if ($sth->fetchrow() >0){
			my ($sth) = &Do_SQL("SELECT * FROM sl_customers WHERE id_customers='$in{'id_customers'}'");
			my ($tmp) = $sth->fetchrow_hashref();
			foreach my $key (keys %{$tmp}){
				$in{"customers.".lc($key)} = $tmp->{$key};
			}
			return &build_page("customerdata.html");
		}
	}
}


#########################################################################################################
#########################################################################################################
#
#	Function: return_upcs
#   		
#		sp: Carga contenido de upcs en el return dependiendo si es modo vista o modo edicion. (Back to Inventory)
#
#	Created by:
#		_Roberto Barcenas_
#
#	Modified By:
#
#   	Parameters:
#		
#
#   	Returns:
#		None
#
#   	See Also:
#
sub return_upcs {
#########################################################################################################
#########################################################################################################


	my ($cadmodel,$output);
	if($in{'id_returns'}){

		my ($sth0) = &Do_SQL("SELECT COUNT(*) FROM sl_returns_upcs WHERE ID_returns='$in{'id_returns'}' and UPC != '';");
		$va{'matches'} = $sth0->fetchrow();
		
		if($va{'matches'} > 0){

			my (@c) = split(/,/,$cfg{'srcolors'});
			$va{'btn_fastbacktoinventory'} = 'none'; ## Display Button in template for Fast Back To Inventory?
			$va{'btn_transitioninventory'} = 'none'; ## Display Button in template for Transition Inventory?
			

			my ($sth1) = &Do_SQL("SELECT * FROM  sl_returns_upcs WHERE ID_returns='$in{'id_returns'}' and UPC!='' order by UPC");
			while ($rec1 = $sth1->fetchrow_hashref){

				$d = 1 - $d;
				$output .= "<tr bgcolor='$c[$d]'>";

				$in{'id_products'} = &load_name('sl_skus','UPC',$upcs,'ID_sku_products');
				$in{'id_products'} = "UPC NOT FOUND" if(!$in{'id_products'});
				$cadmodel = &load_db_names('sl_parts','ID_parts',$rec1->{'ID_parts'},'[Model] / [Name]');

				$output .= '<td class="smalltext" nowrap><a href="/cgi-bin/mod/'.$usr{'application'}.'/dbman?cmd=mer_parts&view='.$rec1->{'ID_parts'}.'">'.&format_sltvid(400000000+$rec1->{'ID_parts'}).'</a></td>';
				$output .= '<td class="smalltext">'.$cadmodel.'</td>';
				$output .= '<td class="smalltext" nowrap>'.$rec1->{'UPC'}.'</td>';

				$css_style = $rec1->{'Cost'} <=0 ? qq|style = "background-color: #FFBABA;color: #D8000C;" | : qq||;

				if ($in{'modify'} and $in{'meraction'} ne 'ReShip' and $rec1->{'Status'} !~ /Processed|New/ and ( $in{'status'} eq 'Back to inventory' or $cfg{'fastbackinventory'}) ){

					$output .= qq|<input type="hidden" name="id_returns_upc_$rec1->{'ID_returns_upcs'}" value="$rec1->{'ID_returns_upcs'}">\n|;
					$output .= qq|<td class='smalltext'><input type="text" size="10" $css_style name="cost_$rec1->{'ID_returns_upcs'}" value="$rec1->{'Cost'}" onFocus='focusOn( this )' onBlur='focusOff( this )'></td>|;
					$output .= qq|<td class='smalltext'><input type="text" size="4" $css_style name="quantity_$rec1->{'ID_returns_upcs'}" value="$rec1->{'Quantity'}" onFocus='focusOn( this )' onBlur='focusOff( this )'></td>|;
					$output .= qq|<td class='smalltext'><select $css_style name="inorder_$rec1->{'ID_returns_upcs'}" onFocus='focusOn( this )' onBlur='focusOff( this )'>
									<option value="">---</option>
									|.&build_select_from_enum('InOrder','sl_returns_upcs')."</select></td>";
					$output .= qq|<td class='smalltext'><select $css_style name="status_$rec1->{'ID_returns_upcs'}" onFocus='focusOn( this )' onBlur='focusOff( this )'>
									<option value="">---</option>
									|.&build_select_from_enum('Status','sl_returns_upcs')."</select></td>";
					$output .= qq|<td class='smalltext' valign='middle' align='center' style='color:green;'>
									<select $css_style name='id_warehouses_$rec1->{'ID_returns_upcs'}' onFocus='focusOn( this )' onBlur='focusOff( this )'>
										<option value='---' selected>--</option>|.&build_select_notdropshippers_warehouses($rec1->{'ID_warehouses'}) . qq|
									</select>[er_id_warehouses_$rec1->{'ID_returns_upcs'}]</td>						
									|;
					$output .= qq|<td class='smalltext'><input type="text" size="10" $css_style name="location_$rec1->{'ID_returns_upcs'}" value="$rec1->{'Location'}" onFocus='focusOn( this )' onBlur='focusOff( this )'></td>|;

					$va{'btn_fastbacktoinventory'} = 'block' if $cfg{'fastbackinventory'};## Only show extra button with $cfg{'fastbackinventory'}
					$va{'btn_transitioninventory'} = 'block' if $cfg{'transitioninventory'};## Only show extra button with $cfg{'fastbackinventory'}

					$va{'jsreturns'} .= "chg_select('inorder_$rec1->{'ID_returns_upcs'}','$rec1->{'InOrder'}');";
					$va{'jsreturns'} .= "chg_select('status_$rec1->{'ID_returns_upcs'}','$rec1->{'Status'}');";
					#$va{'jsreturns'} .= "chg_select('id_warehouses_$rec1->{'ID_returns_upcs'}','$rec1->{'ID_returns_upcs'}');";
				
				}else{

					$output .= "<td class='smalltext' align='right' nowrap>". &format_price($rec1->{'Cost'})."</td>";
					$output .= "<td class='smalltext'>$rec1->{'Quantity'}</td>";
					$output .= "<td class='smalltext'>$rec1->{'InOrder'}</td>";
					$output .= "<td class='smalltext' nowrap>$rec1->{'Status'}</td>";
					$output .= qq|<td class='smalltext' valign='left' align='left' style='color:green;'>|.&load_name('sl_warehouses', ID_warehouses,$rec1->{'ID_warehouses'}, 'Name') .qq|</td>|;
					$output .= qq|<td class='smalltext' valign='right' align='right' style='color:green;'>$rec1->{'Location'}</td>|;

				}

				$output .= '</tr>';
			}
			
		}else{
			$output = qq|
		<tr>
			<td colspan='6' align="center">|.&trans_txt('search_nomatches').qq|</td>
		</tr>\n|;
		}
	}else{
		$output = qq|
		<tr>
			<td colspan='6' align="center">|.&trans_txt('search_nomatches').qq|</td>
		</tr>\n|;
	}
	return $output;
}

sub calculate_fees {
# --------------------------------------------------------
	my ($id_orders,$id_orders_products)=@_;
	my ($amount,%fees);
	my (@ary) = ('returnfee','restockfee','processingfee','oldshpreturn','newshp');

	for my $i(0..5){

		$fees{$ary[$i].'_amount'}=0;
		if ($in{$ary[$i]} eq 'Applicable'){

			my ($sth) = &Do_SQL("SELECT sl_services.*  FROM `sl_vars` LEFT JOIN sl_services ON ID_services=VValue WHERE `VName` = '$ary[$i]' and Status IN ('Active','Hidden')");
			$rec = $sth->fetchrow_hashref();
			
			## TODO Cargar Servicio/valor desde var
			if ($rec->{'ID_services'}>0){

				$fees{$ary[$i].'_id'}=$rec->{'ID_services'};
				if ($rec->{'SalesPrice'} eq 'Fixed'){

					$fees{$ary[$i].'_amount'}=$rec->{'SPrice'};

				}else{

					if ($ary[$i] =~ /oldshpreturn|newshp/){

						## Calculate Shipping for Return Fee
						if ($id_orders_products>0){

							$fees{$ary[$i].'_amount'} = &round(&load_name('sl_orders_products','ID_orders_products',$id_orders_products,'Shipping')*$rec->{'SPrice'}/100,$sys{'fmt_curr_decimal_digits'});
						
						}else{
							$fees{$ary[$i].'_amount'} = &round(&load_name('sl_orders','ID_orders',$id_orders,'OrderShp')*$rec->{'SPrice'}/100,$sys{'fmt_curr_decimal_digits'});

						}

					}else{

						## Calculate Price for Return Fee
						if ($id_orders_products>0){

							$fees{$ary[$i].'_amount'} = &round(&load_name('sl_orders_products','ID_orders_products',$id_orders_products,'SalePrice')*$rec->{'SPrice'}/100,$sys{'fmt_curr_decimal_digits'});

						}else{

							$fees{$ary[$i].'_amount'} = &round(&load_name('sl_orders','ID_orders',$id_orders,'OrderNet')*$rec->{'SPrice'}/100,$sys{'fmt_curr_decimal_digits'});

						}

					}

				}
				$amount += $fees{$ary[$i].'_amount'};
			}

		}
		
	}

	if ($in{'meraction'} eq 'Repair Center'){
		$amount += $in{'sprice'};
	}elsif($in{'meraction'} eq 'Exchange'){
		## CH:TODO
		## Cargar valor de $price_old desde sl_orders_products, que es el producto por el cual se esta cambiando
		my ($price_old);
		$amount += $in{'sprice'} - $price_old; 
	}
	return ($amount,%fees);
}


sub build_radio_return_status {
# --------------------------------------------------------
# Created by: Carlos Haas
# Created on: 
# Description : 
# Notes : (Modified on : Modified by :)
	## All Status : ('New','In Process','Repair','Customer Service','QC/IT','Processed','Back to inventory','Resolved','Void','Pending Payments','Pending Refunds','Archived','Refused','Unable to Resolve');
	my (@fields,$output);
	if ($in{'search'} eq 'form'){
		@fields = ('New','In Process','Repair','Customer Service','QC/IT','Processed','Back to inventory','Resolved','Void','Pending Payments','Pending Refunds','Archived','Refused','Unable to Resolve');
	}elsif($in{'status'} =~ /Repair/ or $in{'meraction'} eq 'Repair Center'){
		@fields = ('Repair','Resolved','Unable to Resolve','Void');
	}elsif($in{'status'} =~ /Void|Archived|New|Resolved/i){
		@fields = ($in{'status'});
	}elsif ($in{'status'} =~ /In Process/){
		@fields = ('In Process','Repair','Customer Service','QC/IT','Refused','Back to inventory','Unable to Resolve','Void');
	}elsif ($in{'status'} =~ /Back to inventory/){
		@fields = ('Back to inventory','Resolved','Void');
	}elsif ($in{'status'} =~ /Customer Service/){
		@fields = ('Customer Service','Back to inventory','Void');
	}elsif ($in{'status'} =~ /Processed/){
		@fields = ('Processed','Repair','Customer Service','QC/IT','Refused','Back to inventory','Unable to Resolve','Void');
	}elsif ($in{'status'} eq 'QC/IT'){
		@fields = ('QC/IT','Repair','Customer Service','Back to inventory','Void');
	}else{
		@fields = ($in{'status'},'Void');
	}
	for (0..$#fields){
		$output .= '<span style="white-space:nowrap"><input type="radio" id="Status_'.lc($fields[$_]).'" name="Status" value="'.$fields[$_].'" class="radio"> <label for="Status_'.lc($fields[$_]).'">'.$fields[$_].'</label></span>'."\n";
	}
	return $output;	
}


#########################################################################################################
#########################################################################################################
#
#	Function: return_back_to_inventory
#   		
#		sp: Devuelve a Inventario la mercancia procedente de una devolucion
#
#	Created by:
#		_Roberto Barcenas_
#
#	Modified By:
#
#   	Parameters:
#		id_returns: ID_returns
#		id_orders: ID_orders
#
#   	Returns:
#		None
#
#   	See Also:
#
sub return_back_to_inventory {
#########################################################################################################
#########################################################################################################
	
	my ($id_returns, $id_orders) = @_;
	my $total_returned = 0;
	my $srts;
	my $log = "Debug cmd=return_back_to_inventory\n\n";

	###############################
	###############################
	### Metodo usado para la salida de inventario. FIFO: Primer entradas primeras salidas | LIFO: Ultimas entradas primeras salidas
	###############################
	###############################
	my $acc_method = $cfg{'acc_inventoryout_method'} ? $cfg{'acc_inventoryout_method'} : 'fifo';
	my $invout_order = $acc_method eq 'fifo' ? '' : 'DESC';
	
	&Do_SQL("START TRANSACTION;");
	$log .= "START TRANSACTION;"."<br>\n\n";

	$sql = "SELECT ID_returns_upcs, ID_parts, 400000000 + ID_parts, UPC, ID_warehouses, Location, Cost, Cost_Adj, Cost_Add, Quantity FROM sl_returns_upcs WHERE ID_returns = '$id_returns' AND ID_parts > 0 AND ID_warehouses > 0 AND Status!='Processed' ORDER BY ID_returns_upcs;";
	$log .= $sql."<br>\n\n";
	my ($sthr) = &Do_SQL($sql);
	my ($qty_processed, $qty_required) = 0;
	my ($err_message) = '';
	while (my ($id, $id_parts, $this_sku, $upc, $id_warehouses, $location, $cost, $cost_adj, $cost_add, $quantity) = $sthr->fetchrow() ){

		$qty_required += $quantity;
		$log .= "id=".$id."<br>\n";
		$log .= "id_parts=".$id_parts."<br>\n";
		$log .= "this_sku=".$this_sku."<br>\n";
		$log .= "upc=".$upc."<br>\n";
		$log .= "id_warehouses=".$id_warehouses."<br>\n";
		$log .= "location=".$location."<br>\n";
		$log .= "cost=".$cost."<br>\n";
		$log .= "cost_adj=".$cost_adj."<br>\n";
		$log .= "qty_required=".$qty_required."<br>\n";
		$log .= "quantity=".$quantity."<br>\n\n";

		###########################
        ### Costo Promedio
        ###########################
        my ($cost_avg, $total_cost_avg, $id_custom_info);        
        # if ($cfg{'acc_inventoryout_method_cost'} and lc($cfg{'acc_inventoryout_method_cost'}) eq 'average'){
        #     ($cost_avg, $total_cost_avg, $id_custom_info, $cost_adj, $cost_add) = &get_average_cost($this_sku);
        #     if ($cost_avg <= 0) {
            
        #         return ("ERROR", "AVG Cost Not Found");
                
        #     }

        #     $cost = $cost_avg;
        #     $log .= "cost_avg=".$cost_avg."<br>\n";
        #     $log .= "total_cost_avg=".$total_cost_avg."<br>\n";
        # }else{
        	###
			### Custom Info
			###
			my $sql_info = "SELECT sl_warehouses_location.ID_customs_info 
							FROM sl_warehouses_location 
							WHERE sl_warehouses_location.ID_warehouses = '$id_warehouses' 
								AND sl_warehouses_location.Location = '$location' 
								AND sl_warehouses_location.ID_products = '$this_sku'
							ORDER BY sl_warehouses_location.Date $invout_order, sl_warehouses_location.Time $invout_order
							LIMIT 1;";
			my $sth_info = &Do_SQL($sql_info);
			$id_custom_info = $sth_info->fetchrow();
        # }

		## Validation 
		if ($cost <= 0){
			$err_message .= "Invalid Cost -> $id_warehouses : $upc [$this_sku] x $quantity"."<br />";
		}
		
		$location = &return_check_location($id, $id_warehouses, $location);
		if (!$location){
			$err_message .= "Invalid Target Location -> $id_warehouses : $upc [$this_sku] x $quantity"."<br />";
		}

		if ($this_sku and $err_message eq ''){
			
			############################################
			############################################
			##########
			##########  1) warehouses_location
			##########
			############################################
			############################################

			$sql = "/* Return: IDR:$id_returns:IDRU:$id:IDWL:0:Q:0 */ ";
			### Se valida si ya existe un registro en sl_warehouses_location
			my $sel_sql_custom_info = (!$id_custom_info) ? "AND ID_customs_info IS NULL" : "AND ID_customs_info = $id_custom_info";
            $sql = "SELECT ID_warehouses_location FROM sl_warehouses_location WHERE ID_warehouses = $id_warehouses AND ID_products = $this_sku AND Location = '$location' $sel_sql_custom_info ORDER BY Date DESC LIMIT 1;";
            my $sth_exist = &Do_SQL($sql);
            my $id_wl = $sth_exist->fetchrow();
            if( int($id_wl) > 0 ){
            	$sql = "UPDATE sl_warehouses_location SET Quantity = Quantity + $quantity WHERE ID_warehouses_location = $id_wl;";
            }else{
				$sql = "INSERT INTO sl_warehouses_location SET ID_warehouses = '$id_warehouses', ID_products = '$this_sku', Location = '$location', Quantity = '$quantity' $add_sql_custom_info, Date = CURDATE(),Time = CURTIME(), ID_admin_users='$usr{'id_admin_users'}';";
			}
			$log .= $sql."<br>\n\n";
			&Do_SQL($sql);

			############################################
			############################################
			##########
			##########  2) sl_skus_cost
			##########
			############################################
			############################################
			$sql = "/* Returns IDR:$id_returns:IDRU:$id:IDSC:0:Q:0 */ ";
			$sql .= "INSERT INTO sl_skus_cost SET ID_products = '$this_sku', ID_purchaseorders = $id_returns, Tblname='sl_returns', Cost = '$cost', ID_warehouses = '$id_warehouses', Quantity = '$quantity', Date = CURDATE(), Time = CURTIME(), ID_admin_users = '$usr{'id_admin_users'}';";
			$log .= $sql."<br>\n\n";
			&Do_SQL($sql);
			
			############################################
			############################################
			##########
			##########  3) Log sl_skus_trans
			##########
			############################################
			############################################
			&sku_logging($this_sku, $id_warehouses, $location, 'Return', $id_returns, 'sl_returns', $quantity, $cost, $cost_adj, 'IN', $id_custom_info, $cost_add);
			$log .= qq|sku_logging($this_sku, $id_warehouses, $location, 'Return', $id_returns, 'sl_returns', $quantity, $cost, $cost_adj, 'IN', $id_custom_info, $cost_add)|."<br>\n\n";

			############################################
			############################################
			##########
			##########  3) Movimientos Contables
			##########
			############################################
			############################################
			my ($order_type, $ctype, $ptype,@params);
			$sql = "SELECT Ptype, Type FROM sl_orders INNER JOIN sl_customers USING(ID_customers) WHERE ID_orders = '$id_orders';";
			$log .= $sql."<br>\n\n";
			my ($sth) = &Do_SQL($sql);
			($order_type, $ctype) = $sth->fetchrow();
			my @params = ($id_orders, $this_sku, round($cost * $quantity,2) );
			&accounting_keypoints('order_skus_backtoinventory_'. $ctype .'_'. $order_type, \@params );
			$log .= qq|accounting_keypoints('order_skus_backtoinventory_'. $ctype .'_'. $order_type, [$id_orders, $this_sku, $cost] )|."<br>\n\n";

			############################################
			############################################
			##########
			##########  4) Actualizacion linea de return para marcar procesado
			##########
			############################################
			############################################
			$sql = "UPDATE sl_returns_upcs SET Status = 'Processed' WHERE ID_returns_upcs = '$id';";
			$log .= $sql."<br>\n\n";
			&Do_SQL($sql);

		}else{
			$err_message .= "Invalid SKU -> $id_warehouses : $upc [$this_sku] x $quantity"."<br />";
		}
	}
	my $sth = &Do_SQL("SELECT SUM(Quantity) FROM sl_skus_trans WHERE tbl_name='sl_returns' AND ID_trs='$id_returns';");
	my ($qty_processed) = $sth->fetchrow();

	$log .= "err_message=".$err_message."\n";
	$log .= "qty_processed=".$qty_processed."\n";
	$log .= "qty_required=".$qty_required."\n\n";

	if ($qty_processed == $qty_required and $err_message eq ''){

		$in{'db'}='sl_returns';
		&auth_logging('back_to_inventory',$id_returns);

		&Do_SQL("COMMIT;");
		$log .= "COMMIT;"."<br>\n\n";
		# &Do_SQL("ROLLBACK;"); ## Only Debug
		&Do_SQL("INSERT INTO sl_debug (cmd, id, log, Date, Time, ID_admin_users) VALUES ('[OK]return_back_to_inventory', '$id_returns', '".&filter_values($log)."', CURDATE(), CURTIME(), '$usr{'id_admin_users'}');");

		return ('OK','', $qty_processed);

	}else{

		&Do_SQL("ROLLBACK;");

		$err_message .="<br>\nQty Required: $qty_required<br>\nQty Processed: $qty_processed<br>\n" if '$qty_processed' ne '$qty_required';
		$log .= $err_message . "\n\n";
		$log .= "ROLLBACK;"."<br>\n\n";

		&Do_SQL("INSERT INTO sl_debug (cmd, id, log, Date, Time, ID_admin_users) VALUES ('[ERROR]return_back_to_inventory', '$id_returns', '".&filter_values($log)."', CURDATE(), CURTIME(), '$usr{'id_admin_users'}');");

		return ('ERROR',"$err_message", 0);

	}

}


#########################################################################################################
#########################################################################################################
#
#	Function: return_check_location
#   		
#		sp:Revisa si el location pertenece al almacen o devuelve un location del almacen 
#
#	Created by:
#		_Roberto Barcenas_
#
#	Modified By:
#
#   	Parameters:
#		id_orders: ID_orders
#
#   	Returns:
#		None
#
#   	See Also:
#
sub return_check_location {
#########################################################################################################
#########################################################################################################


	my ($id, $id_warehouses, $location) = @_;

	my ($sth) = &Do_SQL("SELECT COUNT(*) FROM sl_locations WHERE ID_warehouses = '$id_warehouses' AND Code = '". &filter_values($location) ."' AND status = 'Active';");
	my ($ok) = $sth->fetchrow();

	return $location;
}


#########################################################################################################
#########################################################################################################
#
#	Function: return_reship
#   		
#		sp: Evalua y marca orden y productos para reenvio
#
#	Created by:
#		_Roberto Barcenas_
#
#	Modified By:
#
#   	Parameters:
#		id_returns: ID_returns
#
#   	Returns:
#		None
#
#   	See Also:
#
sub return_reship {
#########################################################################################################
#########################################################################################################

	my $ok = 0; my @ids_reship; my $id_orders = 0; my $merAction = 'ReShip';

	#########
	######### 1) ReShip
	#########
	foreach my $key (keys %in) {
	    
	    #$str .= "$key = " . $in{$key} . "\n";
		if($key =~ /^reship_(\d{1,10})$/ and $in{$key}){

			++$ok;
			my $this_id_orders_products = int($1);
			###
			### 1.1) Lineas en Remesa -> Returned
			###
			&Do_SQL("UPDATE sl_warehouses_batches_orders SET Status = 'Returned' WHERE ID_orders_products = '$this_id_orders_products' AND Status IN ('In Fulfillment','Shipped','In Transit');");


			###
			### 1.2) Lineas en Orden -> ReShip
			###
			&Do_SQL("UPDATE sl_orders_products SET Status = 'ReShip' WHERE ID_orders_products = '$this_id_orders_products';");

			###
			### 1.3) Lineas en Orden -> Array
			###
			push(@ids_reship, $this_id_orders_products);

		}

		$id_orders = int($in{$key}) if $key eq 'id_orders';
	}
	( !$id_orders and $in{'id_orders'} ) and ( $id_orders = int($in{'id_orders'}) );

	###
	### 1.4) Nota en Orden
	###
	if($ok and $id_orders){

		&Do_SQL("UPDATE sl_orders SET StatusPrd = 'For Re-Ship' WHERE ID_orders = '$in{'id_orders'}';");

		my ($sth) = &Do_SQL("SELECT sl_orders_products.ID_products, Name FROM sl_orders_products INNER JOIN sl_products ON RIGHT(sl_orders_products.ID_products,6) = sl_products.ID_products WHERE ID_orders_products IN (".join(',', @ids_reship).");");
		while(my ($id_products, $pname) = $sth->fetchrow() ){
			$va{'returns_note_'. $id_orders} .= &format_sltvid($id_products) .' '. $pname .qq|\n|;
		}
		&add_orders_notes($id_orders, $merAction);

	}

	return;
}


#########################################################################################################
#########################################################################################################
#
#	Function: return_creditmemo
#   		
#		sp: Genera un creditmemo con todos los skus devueltos
#
#	Created by:
#		_Roberto Barcenas_
#
#	Modified By:
#
#		Last Time Modified By _RB_ on 2015-09-23: Se agrega sl_creditmemos_products.ShpDate para estandarizar con proceso devolucion de skus
# 		Last Time Modified by _RB_ on 2015-12-07: Se toma en cuenta Discount
# 		
# 		
#   	Parameters:
#		id_returns: ID_returns
#
#   	Returns:
#		None
#
#   	See Also:
#
sub return_creditmemo {
#########################################################################################################
#########################################################################################################

	my ($id_returns, $return_net, $return_dis, $return_shp, $return_tax, $return_total) = @_;

	my $id_creditmemos = 0; my $fixed_return = 0; my $already_creditmemos = 0;
	if(!$id_returns){ return ($id_creditmemos, $already_creditmemos); }
	my $return_shp_tax = 0; my $return_shp_tax_pct = 0;

	#####
	##### 1) Buscamos ID_creditmemos existente (Para casos donde se requirio la nota de credito sin finalizar el proceso de devolucion)
	#####
	($id_creditmemos, $already_creditmemos) = &get_returns_credtimemo($id_returns);
	return ($id_creditmemos, $already_creditmemos) if $id_creditmemos;


	#####
	##### 2) Si no hay creditmemo previo
	#####

	if(!$return_net){
	
		my ($sth) = &Do_SQL("SELECT VValue FROM sl_vars WHERE VName = 'Return'". $id_returns ."';");
		my $return_data = $sth->fetchrow();

		($return_net, $return_dis, $return_shp, $return_tax, $return_total) = split(/::/, $return_data,4);

	}

	#@ivanmiranda :: Pase de Cost_Adj de sl_returns_upcs a sl_creditmemos_products
	my ($sth) = &Do_SQL("SELECT 400000000 + ID_parts, Quantity, Cost, Cost_Adj FROM sl_returns_upcs WHERE ID_returns = '$id_returns';");
	my ($total_upcs) = $sth->rows();

	if($total_upcs){

		my ($sth_co) = &Do_SQL("SELECT sl_orders.ID_customers, sl_orders.ID_orders FROM sl_returns INNER JOIN sl_orders USING(ID_orders) WHERE ID_returns = '$id_returns';");
		my ($id_customers, $id_orders) = $sth_co->fetchrow();


		#########
		######### 2.1) sl_creditmemos
		#########
		$tries = 0;
		do{

			++$tries;	
			my ($sth_cm) = &Do_SQL("INSERT INTO sl_creditmemos SET ID_customers = '$id_customers', Reference = '$id_returns', Description = '". &trans_txt('returns_creditmemo_new') ."', Status = 'New', Date = CURDATE(), Time = CURTIME(), ID_admin_users = '$usr{'id_admin_users'}';");
			$id_creditmemos = $sth_cm->{'mysql_insertid'};

		}while(!$id_creditmemos or $tries > 2);

		if($id_creditmemos){

			my $i = 0; my $lines = 0; my $total_cost = 0; my $applied_payment = 0; my $total_amt_aux = ($cfg{'arithmetic_zero_amt'} * -1);
			#@ivanmiranda :: Pase de Cost_Adj de sl_returns_upcs a sl_creditmemos_products
			while(my ($sku, $qty, $cost, $cost_adj) = $sth->fetchrow() ){

				#########
				######### 2.2) sl_creditmemos_products
				#########
				++$i;

				for(1..$qty){

					### Cero aritmético
					my $this_sprice = 0; my $this_disc = 0;
					if( int($cfg{'arithmetic_zero'}) == 1 && $cfg{'arithmetic_zero_amt'} ){
						$this_sprice = $cfg{'arithmetic_zero_amt'};
						$this_disc = $cfg{'arithmetic_zero_amt'};
						$total_amt_aux += $this_sprice;
					}

					my ($sth_cmpr) = &Do_SQL("INSERT INTO sl_creditmemos_products SET ID_products = '$sku', ID_creditmemos = '$id_creditmemos', Quantity = 1, SalePrice = '$this_sprice', Shipping = 0, Cost = '$cost', Cost_Adj = '$cost_adj', Tax = 0, Tax_percent = 0, Discount = '$this_disc', ShpDate = CURDATE(), ShpTax = 0, ShpTax_percent = 0, Status = 'Active', Date = CURDATE(), Time = CURTIME(), ID_admin_users = '$usr{'id_admin_users'}';");
					$lines += $sth_cmpr->rows();
					$total_cost += round($cost,2);

				}

			}

			#########
			######### 2.3) sl_creditmemos_notes &log
			#########
			if ($lines){ 

				### Cero aritmético
				my ($this_return_net, $this_return_dis);
				if( int($cfg{'arithmetic_zero'}) == 1 ){
					$this_return_net = ($return_net >= $total_amt_aux and $return_dis < 1) ? ($return_net - $return_dis) : ($return_net - $total_amt_aux);
					$this_return_dis = ($return_dis >= $total_amt_aux) ? $return_dis - $total_amt_aux : 0;

					$this_return_net = $cfg{'arithmetic_zero_amt'} if( $this_return_net == 0 and $cfg{'arithmetic_zero_amt'} );
				} else {
					$this_return_net = $return_net;
					$this_return_dis = $return_dis;
				}

				### Shp-Tax
				if( $return_shp > 0 ){
					$return_shp_tax_pct = ($cfg{'shptax_percent_default'}) ? $cfg{'shptax_percent_default'} : 0.16;
					$return_shp_tax = round($return_shp * $return_shp_tax_pct, 2);

					$return_tax -= $return_shp_tax if( $return_tax > 0 );
				}

				### Recalc-Tax
				my $this_tax_pct = ($cfg{'taxp_default'}) ? $cfg{'taxp_default'} : 0.16;
				if( $return_tax > 0 ){
					$return_tax = round(($this_return_net - $this_return_dis) * $this_tax_pct, 2);
				} else {
					$this_tax_pct = 0;
				}

				&Do_SQL("UPDATE sl_creditmemos_products SET SalePrice = '". $this_return_net ."', Discount = '". $this_return_dis ."', Shipping = '". $return_shp ."', Tax = '". $return_tax ."', Tax_percent = ". ($this_tax_pct * 100) .", ShpTax = '". $return_shp_tax ."', ShpTax_percent = '". ($return_shp_tax_pct * 100) ."' WHERE ID_creditmemos = '". $id_creditmemos ."' ORDER BY ID_creditmemos_products LIMIT 1;");
				&Do_SQL("INSERT INTO sl_creditmemos_notes SET ID_creditmemos = '". $id_creditmemos ."', Notes = '". &trans_txt('returns_creditmemo_new') ."', Type = 'Low', Date = CURDATE(), Time = CURTIME(), ID_admin_users = '$usr{'id_admin_users'}';");
				
				&add_order_notes_by_type($id_orders,&trans_txt('returns_creditmemo_new'),"Low");

			}

			#########
			######### 2.4) sl_orders_products
			#########
			my ($sth_cop) = &Do_SQL("SELECT COUNT(*) + 1 FROM sl_orders_products WHERE ID_orders = '". $id_orders ."' AND RIGHT(ID_products,6) = 800000;");
			my ($new_line) = $sth_cop->fetchrow();

			my ($sth_op) = &Do_SQL("INSERT INTO sl_orders_products SET ID_orders = '". $id_orders ."', ID_products = (800000000 + ". $new_line ."), ID_packinglist = 0, Related_ID_products = '". $id_creditmemos ."', Quantity = 1, SalePrice = (". $return_net ." * -1), Discount = (". $return_dis ." * -1) , Shipping = (". $return_shp ." * -1), Cost = (". $total_cost ." * -1), Tax = (". $return_tax ." * -1), Tax_percent = IF(". $return_tax ." > 0,16/100,0), FP = 1, ShpTax = (". $return_shp_tax ." * -1), ShpTax_percent = IF(". $return_shp_tax ." > 0,16/100,0), PostedDate = CURDATE(), Status = 'Returned', Date = CURDATE(), Time = CURTIME(), ID_admin_users = '$usr{'id_admin_users'}';");
			my ($id_orders_products) = $sth_op->{'mysql_insertid'};

			#########
			######### 2.5) sl_orders_payments
			#########
			my ($sth_copa) = &Do_SQL("SELECT SUM(Amount) FROM sl_orders_payments WHERE ID_orders = '". $id_orders ."' AND (Captured IS NULL OR Captured = 'No' OR Captured = '') AND (PostedDate IS NULL OR PostedDate = '' OR PostedDate = '0000-00-00') AND Status NOT IN('Void','Order Cancelled','Cancelled');");
			my ($total_debt) = $sth_copa->fetchrow();

			if(!$total_debt){

				#########
				######### 2.5.1) No debt | Return all Amount
				#########
				$fixed_return = $return_total;
				my $sth = &Do_SQL("SELECT ID_orders_payments, Type FROM sl_orders_payments WHERE ID_orders = '". $id_orders ."' AND Status NOT IN('Void','Order Cancelled','Cancelled','Credit') ORDER BY FIELD(Type, 'Credit-Card','Referenced Deposit','COD'), Amount DESC, CapDate DESC, Captured = 'Yes', AuthDateTime DESC, LENGTH(AuthCode) DESC, Paymentdate DESC, ID_orders_payments LIMIT 1;");
				my ($id_orders_payments, $type_payment) = $sth->fetchrow();

				my (%overwrite) = ('amount' => ($return_total * -1), 'pmtfield8' => '1' ,'authcode' => '', 'authdatetime' => '', 'captured' => 'No', 'capdate' => '', 'status' => 'Credit', 'reason' => 'Refund', 'posteddate' => '0000-00-00');
				#$applied_payment = &Do_selectinsert('sl_orders_payments', "ID_orders = '$id_orders' AND Status NOT IN('Void','Order Cancelled','Cancelled','Credit')", "ORDER BY CapDate DESC, Captured = 'Yes', AuthDateTime DESC, LENGTH(AuthCode) DESC, Paymentdate DESC, ID_orders_payments ", " LIMIT 1", %overwrite);
				$applied_payment = &Do_selectinsert('sl_orders_payments', "ID_orders_payments = '$id_orders_payments' ", "", "", %overwrite);
				
				if( !$applied_payment ){
					return(0, 0);
				}else{

					&Do_SQL("UPDATE sl_orders_payments SET Amount = ($return_total * -1), Paymentdate = CURDATE(), Date = CURDATE(), Time = CURTIME(), ID_admin_users = '$usr{'id_admin_users'}' WHERE ID_orders_payments = '$applied_payment';");
					
					if($type_payment eq 'Credit-Card' and ($cfg{'encrypt_cc'} and $cfg{'encrypt_cc'} == 1)){

						my $id_payments = $applied_payment;
						my $id_pcd = &load_name("sl_orders_cardsdata", "ID_orders_payments", $id_orders_payments, "ID_orders_cardsdata");	
						if($id_pcd > 0){
							&Do_SQL("INSERT INTO sl_orders_cardsdata(ID_orders,ID_orders_payments,card_number,card_date,card_cvn,Date,Time,ID_admin_users) 
									 SELECT ID_orders, ". $id_payments .", card_number, card_date, card_cvn, Date, Time, ID_admin_users FROM sl_orders_cardsdata WHERE ID_orders_cardsdata = ". $id_pcd .";");
						}
					
					}

				}

			}else{

				#########
				######### 2.5.2) Debt (Could or not cover full return amount)
				#########
				do{

					my ($sth_p) = &Do_SQL("SELECT ID_orders_payments, Amount FROM sl_orders_payments WHERE ID_orders = '$id_orders' AND Amount > 0 AND (Captured IS NULL OR Captured = 'No' OR Captured = '') AND (PostedDate IS NULL OR PostedDate = '' OR PostedDate = '0000-00-00') AND Status NOT IN('Void','Order Cancelled','Cancelled','Credit');");
					my ($this_id, $this_amount) = $sth_p->fetchrow();

					if($this_id){

						#########
						######### 2.5.2.1) Order Has Enough debt
						#########
						if($return_total >= $this_amount){

							#########
							######### 2.5.2.1.1) Return Amount is Greater or equal than debt
							#########
							&Do_SQL("UPDATE sl_orders_payments SET Status = 'Void' WHERE ID_orders_payments = '$this_id';");
							$return_total -= round($this_amount,2);

						}else{

							#########
							######### 2.5.2.1.2) Debt is greater than Return Amount
							#########
							&Do_SQL("UPDATE sl_orders_payments SET Amount = Amount - $return_total WHERE ID_orders_payments = '$this_id';");
							$return_total = 0;

						}

					}else{

						#########
						######### 2.5.2.2) Order Has Not enough debt
						#########
						$fixed_return = $return_total;

						my $sth = &Do_SQL("SELECT ID_orders_payments, Type FROM sl_orders_payments WHERE ID_orders = '$id_orders' AND Status NOT IN('Void','Order Cancelled','Cancelled','Credit') ORDER BY CapDate DESC, Captured = 'Yes', AuthDateTime DESC, LENGTH(AuthCode) DESC, Paymentdate DESC, ID_orders_payments LIMIT 1;");
						my ($id_orders_payments, $type_payment) = $sth->fetchrow();

						my (%overwrite) = ('amount' => ($return_total * -1), 'pmtfield8' => '1' ,'authcode' => '', 'authdatetime' => '', 'captured' => 'No', 'capdate' => '', 'status' => 'Credit', 'reason' => 'Refund', 'posteddate' => '0000-00-00');
						#$applied_payment = &Do_selectinsert('sl_orders_payments', "ID_orders = '$id_orders' AND Status NOT IN('Void','Order Cancelled','Cancelled','Credit')", "ORDER BY CapDate DESC, Captured = 'Yes', AuthDateTime DESC, LENGTH(AuthCode) DESC, Paymentdate DESC, ID_orders_payments ", " LIMIT 1", %overwrite);
						$applied_payment = &Do_selectinsert('sl_orders_payments', "ID_orders_payments = '$id_orders_payments' ", "", "", %overwrite);						
						if( !$applied_payment ){
							return(0, 0);
						}else{
							&Do_SQL("UPDATE sl_orders_payments SET Amount = ($return_total * -1), Paymentdate = CURDATE(), Date = CURDATE(), Time = CURTIME(), ID_admin_users = '$usr{'id_admin_users'}' WHERE ID_orders_payments = '$applied_payment';");
							$return_total = 0;
							if($type_payment eq 'Credit-Card' and ($cfg{'encrypt_cc'} and $cfg{'encrypt_cc'} == 1)){
								my $id_payments = $applied_payment;
								my $id_pcd = &load_name("sl_orders_cardsdata", "ID_orders_payments", $id_orders_payments, "ID_orders_cardsdata");	
								if($id_pcd > 0){
									&Do_SQL("INSERT INTO sl_orders_cardsdata(ID_orders,ID_orders_payments,card_number,card_date,card_cvn,Date,Time,ID_admin_users) 
											 SELECT ID_orders,$id_payments,card_number,card_date,card_cvn,Date,Time,ID_admin_users FROM sl_orders_cardsdata WHERE ID_orders_cardsdata = $id_pcd;");
								}
							}
						}

					}

				}while($return_total);

			} ## else debt


			#########
			######### 2.6) Creditmemos Payments
			#########
			&Do_SQL("INSERT INTO sl_creditmemos_payments SET ID_creditmemos = '$id_creditmemos', ID_orders = '$id_orders', ID_orders_payments = 0, ID_orders_payments_added = '$applied_payment', ID_orders_products_added = '$id_orders_products', Amount = '$return_total', Date = CURDATE(), Time = CURTIME(), ID_admin_users = '$usr{'id_admin_users'}';");
			&Do_SQL("UPDATE sl_creditmemos SET Status = 'Applied' WHERE ID_creditmemos = '$id_creditmemos';");

			#########
			######### 2.7) Pending Refund?
			#########
			if($applied_payment){

				my $mod1 = $in{'meraction'} eq 'Chargeback' ? " StatusPay = 'ChargeBack', StatusPrd = 'In Claim'  " : "StatusPay = 'Pending Refund' ";
				&Do_SQL("UPDATE sl_orders SET $mod1 WHERE ID_orders = '$id_orders';");
				&Do_SQL("UPDATE sl_returns SET Amount = '$fixed_return' WHERE ID_returns = '$id_returns';");

			}

		} ## if creditmemos

	} ## if returns_upcs

	return ($id_creditmemos, $already_creditmemos);

}


#########################################################################################################
#########################################################################################################
#
#	Function: return_exchange
#   		
#		sp: Genera Movimientos de CF en sl_orders_products | sl_orders_payments
#
#	Created by:
#		_Roberto Barcenas_
#
#	Modified By:
#
#   	Parameters:
#		id_returns: ID_returns
#
#   	Returns:
#		None
#
#   	See Also:
#
sub return_exchange {
#########################################################################################################
#########################################################################################################

	my ($id_returns) = @_;
	if(!$id_returns or $in{'meraction'} ne 'Exchange'){ return 0; }

	my ($sth_co) = &Do_SQL("SELECT sl_orders.ID_customers, sl_orders.ID_orders FROM sl_returns INNER JOIN sl_orders USING(ID_orders) WHERE ID_returns = '$id_returns';");
	my ($id_customers, $id_orders) = $sth_co->fetchrow();
	my @ids; my $sum_total = 0;

	##################
	################## 1) INSERT INTO sl_orders_products records
	##################
	my ($sth) = &Do_SQL("SELECT ID_vars, VValue, IF(Definition_Sp IS NULL,0,RIGHT(Definition_Sp,6)) FROM sl_vars WHERE SubCode = '$id_returns' AND VName = 'Exchange Process' ORDER BY ID_vars;");
	while( my ($id_vars, $sc, $id_products_related) = $sth->fetchrow() ){

		my ($this_offer, $this_price, $this_tax, $this_shp, $this_shptax) = split(/:/, $sc);
		my $this_disc = 0;
		if( int($cfg{'arithmetic_zero'}) == 1 && ($this_price == 0) ){
			$this_price = $cfg{'arithmetic_zero_amt'};
			$this_disc = $cfg{'arithmetic_zero_amt'};
		}
		my ($sth_op) = &Do_SQL("INSERT INTO sl_orders_products SET ID_orders = '$id_orders', ID_products = '$this_offer', ID_packinglist = 0, Related_ID_products = '$id_products_related', Quantity = 1, SalePrice = '$this_price', Shipping = '$this_shp', Cost = 0, Tax = '$this_tax', Tax_percent = IF($this_tax > 0,16/100,0), Discount = '$this_disc', FP = 1, ShpTax = '$this_shptax', ShpTax_percent = IF($this_shptax > 0,16/100,0), Upsell = 'Yes', Status = 'Exchange', Date = CURDATE(), Time = CURTIME(), ID_admin_users = '$usr{'id_admin_users'}';");
		my ($id_orders_products) = $sth_op->{'mysql_insertid'};

		if($id_orders_products){

			push(@ids, "$id_orders_products - $this_offer");
			$sum_total += round($this_price + $this_tax + $this_shp + $this_shptax,2);

		}
		
	} 


	if(scalar @ids > 0 and $sum_total){

		##################
		################## 2) sl_orders_payments
		##################
		my $applied_payment = 0;
		my ($sth_copa) = &Do_SQL("SELECT 
									SUM( IF(Status = 'Credit' AND Amount < 0, ABS(Amount),0) ) 
									, SUM( IF(Status NOT IN('Void','Order Cancelled','Cancelled','Credit') AND Amount > 0 AND (PostedDate IS NULL OR PostedDate = '' OR PostedDate = '0000-00-00'), ABS(Amount),0) ) 
								FROM sl_orders_payments 
								WHERE ID_orders = '$id_orders' 
								AND (Captured IS NULL OR Captured = 'No' OR Captured = '') 
								AND (CapDate IS NULL OR CapDate = '0000-00-00');");
		my ($total_credit, $total_debit) = $sth_copa->fetchrow();

		if(!$total_credit){

			##########
			########## 2.1) No credit. All to Debit
			##########
			$fixed_total = $sum_total;

			if($total_debit){

				#########
				######### 2.1.1) Update Amount 
				#########
				&Do_SQL("UPDATE sl_orders_payments 
						SET Amount = Amount + $sum_total 
						WHERE ID_orders = '$id_orders'
						AND (Captured IS NULL OR Captured = 'No' OR Captured = '') 
						AND (CapDate IS NULL OR CapDate = '0000-00-00') 
						AND (PostedDate IS NULL OR PostedDate = '' OR PostedDate = '0000-00-00')
						AND (Status NOT IN('Void','Order Cancelled','Cancelled','Credit')
						ORDER BY Paymentdate, Status, Amount DESC
						LIMIT 1;");

			}else{

				#########
				######### 2.1.2) INSERT Amount 
				#########
				my (%overwrite) = ('amount' => $sum_total, 'pmtfield8' => '1' ,'authcode' => '', 'authdatetime' => '', 'captured' => 'No', 'capdate' => '', 'status' => 'Approved', 'reason' => 'Exchange');
				$applied_payment = &Do_selectinsert('sl_orders_payments', "ID_orders = '$id_orders' AND Status NOT IN('Void','Order Cancelled','Cancelled','Credit')", "ORDER BY CapDate DESC, Captured = 'Yes', AuthDateTime DESC, LENGTH(AuthCode) DESC, Paymentdate DESC, ID_orders_payments ", " LIMIT 1", %overwrite);
				&Do_SQL("UPDATE sl_orders_payments SET Paymentdate = CURDATE(), PostedDate = '0000-00-00', Date = CURDATE(), Time = CURTIME(), ID_admin_users = '$usr{'id_admin_users'}' WHERE ID_orders_payments = '$applied_payment';");

				## 2.1.3) Crypt Card
				my $sth = &Do_SQL("SELECT ID_orders_payments, Type FROM sl_orders_payments WHERE ID_orders = ". $id_orders ." AND Captured = 'Yes' AND Status NOT IN('Void','Order Cancelled','Cancelled','Credit') ORDER BY CapDate DESC, Captured = 'Yes', AuthDateTime DESC, LENGTH(AuthCode) DESC, Paymentdate DESC, ID_orders_payments LIMIT 1;");
				my ($id_orders_payments, $type_payment) = $sth->fetchrow();

				if($type_payment eq 'Credit-Card' and ($cfg{'encrypt_cc'} and $cfg{'encrypt_cc'} == 1)){

					my $id_payments = $applied_payment;
					my $id_pcd = &load_name("sl_orders_cardsdata", "ID_orders_payments", $id_orders_payments, "ID_orders_cardsdata");
					if($id_pcd > 0){
						&Do_SQL("INSERT INTO sl_orders_cardsdata(ID_orders,ID_orders_payments,card_number,card_date,card_cvn,Date,Time,ID_admin_users) 
								 SELECT ID_orders, ". $id_payments ." , card_number, card_date, card_cvn, Date, Time, ID_admin_users FROM sl_orders_cardsdata WHERE ID_orders_cardsdata = ". $id_pcd .";");
					}

				}

			}

		}else{

			#########
			######### 2.2) Credit (Could or not cover full exchange amount)
			#########
			do{

				my ($sth_p) = &Do_SQL("SELECT ID_orders_payments, ABS(Amount) FROM sl_orders_payments WHERE ID_orders = '$id_orders' AND Amount < 0 AND (Captured IS NULL OR Captured = 'No' OR Captured = '') AND (CapDate IS NULL OR CapDate = '0000-00-00') AND Status = 'Credit' ;");
				my ($this_id, $this_amount) = $sth_p->fetchrow();

				if($this_id){

					#########
					######### 2.2.1) Order Has Enough credit
					#########
					if($sum_total >= $this_amount){

						#########
						######### 2.2.1.1) Return Amount is Greater or equal than debt
						#########
						&Do_SQL("UPDATE sl_orders_payments SET Status = 'Cancelled' WHERE ID_orders_payments = '$this_id';");
						$sum_total -= round($this_amount,2);

					}else{

						#########
						######### 2.2.1.2) Credit is greater than Return Amount
						#########
						&Do_SQL("UPDATE sl_orders_payments SET Amount = Amount + $sum_total WHERE ID_orders_payments = '$this_id';");
						$sum_total = 0;

					}

				}else{

					#########
					######### 2.2.2) Order Has Not enough credit
					#########
					$fixed_total = $sum_total;
					my (%overwrite) = ('amount' => $sum_total, 'pmtfield8' => '1' ,'authcode' => '', 'authdatetime' => '', 'captured' => 'No', 'capdate' => '', 'status' => 'Approved', 'reason' => 'Exchange', 'posteddate' => '0000-00-00');
					$applied_payment = &Do_selectinsert('sl_orders_payments', "ID_orders = '$id_orders' AND Status NOT IN('Void','Order Cancelled','Cancelled','Credit')", "ORDER BY CapDate DESC, Captured = 'Yes', AuthDateTime DESC, LENGTH(AuthCode) DESC, Paymentdate DESC, ID_orders_payments ", " LIMIT 1", %overwrite);
					&Do_SQL("UPDATE sl_orders_payments SET Paymentdate = CURDATE(), Date = CURDATE(), Time = CURTIME(), ID_admin_users = '$usr{'id_admin_users'}' WHERE ID_orders_payments = '$applied_payment';");
					$sum_total = 0;

					## 2.2.3) Crypt Card
					my $sth = &Do_SQL("SELECT ID_orders_payments, Type FROM sl_orders_payments WHERE ID_orders = '$id_orders' AND Captured = 'Yes' AND Status NOT IN('Void','Order Cancelled','Cancelled','Credit') ORDER BY CapDate DESC, Captured = 'Yes', AuthDateTime DESC, LENGTH(AuthCode) DESC, Paymentdate DESC, ID_orders_payments LIMIT 1;");
					my ($id_orders_payments, $type_payment) = $sth->fetchrow();

					if($type_payment eq 'Credit-Card' and ($cfg{'encrypt_cc'} and $cfg{'encrypt_cc'} == 1)){
						my $id_payments = $applied_payment;
						my $id_pcd = &load_name("sl_orders_cardsdata", "ID_orders_payments", $id_orders_payments, "ID_orders_cardsdata");
						if($id_pcd > 0){									
							&Do_SQL("INSERT INTO sl_orders_cardsdata(ID_orders,ID_orders_payments,card_number,card_date,card_cvn,Date,Time,ID_admin_users) 
								 SELECT ID_orders, ". $id_payments ." , card_number, card_date, card_cvn, Date, Time, ID_admin_users FROM sl_orders_cardsdata WHERE ID_orders_cardsdata = ". $id_pcd .";");
						}

					}

				}

				if($sum_total > 0 and $sum_total < 1) { $sum_total = 0; }

			}while($sum_total);

		} ## else credit

		
		if($applied_payment){

			#########
			######### 3) Pending Payments?
			#########
			&Do_SQL("UPDATE sl_orders SET StatusPay = 'Pending Payment' WHERE ID_orders = ". $id_orders .";");
			&Do_SQL("UPDATE sl_returns SET Amount = '$fixed_return' WHERE ID_returns = ". $id_returns .";");

		}else{

			my ($sth) = &Do_SQL("SELECT COUNT(*) FROM sl_orders_payments WHERE ID_orders = ". $id_orders ." AND Amount < 0 AND (Captured IS NULL OR Captured = 'No' OR Captured = '') AND (CapDate IS NULL OR CapDate = '0000-00-00') AND Status = 'Credit';");
			my ($tcredits) = $sth->fetchrow();

			if(!$tcredits){

				#########
				######### 4) Nothing Pending
				#########
				&Do_SQL("UPDATE sl_orders SET StatusPay = 'None' WHERE ID_orders = ". $id_orders .";");
				&Do_SQL("UPDATE sl_returns SET Amount = '0' WHERE ID_returns = ". $id_returns .";");

			}

		}

		&Do_SQL("UPDATE sl_orders SET StatusPrd = 'For Exchange' WHERE ID_orders = ". $id_orders .";");
		
		&add_order_notes_by_type($id_orders,&trans_txt('returns_exchange_processed') ."\nProducts Added:\n".join("\n",@ids),"Low");
	}

	return;
}


#########################################################################################################
#########################################################################################################
#
#	Function: get_returns_credtimemo
#   		
#		sp: Devuelve id_creditmemos para un return
#
#	Created by:
#		_Roberto Barcenas_
#
#	Modified By:
#
#   	Parameters:
#		id_returns: ID_returns
#
#   	Returns:
#		None
#
#   	See Also:
#
sub get_returns_credtimemo {
#########################################################################################################
#########################################################################################################

	my ($id_returns) = @_;

	#####
	##### 1) Buscamos ID_creditmemos existente
	#####
	my ($sth) = &Do_SQL("SELECT ID_creditmemos FROM sl_creditmemos WHERE Reference = '$id_returns' AND Status = 'Applied';");
	my ($id_creditmemos) = $sth->fetchrow();
	my $already = $id_creditmemos ? 1 : 0;


	return ($id_creditmemos, $already);

}


sub return_adjust_order {
# --------------------------------------------------------
	### CH:TODO
	## Esta funcion es la reesponsable de ajustar la orden con los cambios preestablecidos.
	## Se debe ajustar la orden agregando los servcios que correspondan y el cargo que sea la diferencia
	## ver funcion &calculate_fees
	## En donde ya se calculan los Fees y se genera nu arreglo con los valores y ID del servicio que se agregaria
	my ($id_returns) = $in{'id_returns'};	
	my ($vlogMysql) = 0; # 1=Activa Logs de querys en archivo .txt $cfg{'path_logtxt'}
	my ($TaxRate_generic) = $cfg{'TaxRate_generic'};
	my ($ID_shipping_service) = $cfg{'ID_shipping_service'};

	sub add_same_products{
	###Inserta lineas negativas/positivas del mismo producto en orden
	###Aguments: ID_return, pos/neg (positive/negative)
		($id_returns, $opt, $merAction, $ReturnFee) = @_;
		if($opt eq 'pos'){$s='1';}
		elsif($opt eq 'neg'){$s='-1';}
		if($id_returns ne '' and $s ne ''){
			my ($sql) = "SELECT 
						c.ID_products
						,b.ID_orders
						,'0' as ID_packinglist
						,c.Related_ID_products
						,c.ID_products_prices
						,c.Quantity
						,(ifnull(c.SalePrice,0)*$s) as SalePrice
						,(ifnull(c.Shipping,0)*$s) as Shipping
						/*,'0' as Shipping*/
						,(ifnull(c.Cost,0)*$s) as Cost
						,(ifnull(c.Tax,0)*$s) as Tax
						,c.Tax_percent
						,(ifnull(c.Discount,0)*$s) as Discount
						,'1' as FP
						,c.SerialNumber
						,NULL as ShpDate
						,NULL as Tracking
						,NULL as ShpProvider
						,(ifnull(c.ShpTax,0)*$s) as ShpTax
						,c.ShpTax_percent
						/*,'0' as ShpTax*/
						/*,'0' as ShpTax_percent*/
						,NULL as PostedDate
						,NULL as Upsell
						,c.Status
						,CURDATE() as Date
						,CURTIME() as Time
						,c.ID_admin_users
						FROM sl_returns_upcs a
						LEFT JOIN sl_returns b USING(ID_returns)
						LEFT JOIN sl_orders_products c ON b.ID_orders=c.ID_orders AND a.ID_orders_products=c.ID_orders_products
						WHERE a.ID_returns='$id_returns'
						GROUP BY c.ID_orders_products ASC";
			my ($sth) = &Do_SQL($sql);	
			&logtxt($sql,$vlogMysql);			
			while($rec=$sth->fetchrow_hashref()){
				$vID_orders=$rec->{'ID_orders'};
				my ($sql) ="INSERT INTO sl_orders_products SET 							
							ID_products='$rec->{ID_products}'
							,ID_orders='$rec->{ID_orders}'
							,ID_packinglist='$rec->{ID_packinglist}'
							,Related_ID_products='$rec->{Related_ID_products}'
							,ID_products_prices='$rec->{ID_products_prices}'
							,Quantity='$rec->{Quantity}'
							,SalePrice='$rec->{SalePrice}'
							,Shipping='$rec->{Shipping}'
							,Cost='$rec->{Cost}'
							,Tax='$rec->{Tax}'
							,Tax_percent='$rec->{Tax_percent}'
							,Discount='$rec->{Discount}'
							,FP='$rec->{FP}'
							,SerialNumber='$rec->{SerialNumber}'
							,ShpDate='$rec->{ShpDate}'
							,Tracking='$rec->{Tracking}'
							,ShpProvider='$rec->{ShpProvider}'
							,ShpTax='$rec->{ShpTax}'
							,ShpTax_percent='$rec->{ShpTax_percent}'
							,PostedDate='$rec->{PostedDate}'
							,Upsell='$rec->{Upsell}'
							,Status='$rec->{Status}'
							,Date=CURDATE(),
							Time=CURTIME(),
							ID_admin_users='$usr{'id_admin_users'}';";
				my ($sth) = &Do_SQL($sql);	
				&logtxt($sql,$vlogMysql);	
			}
			if($ReturnFee eq 'Applicable'){&add_shipping_service($vID_orders,'pos',$merAction);}			
		} 
	}

	sub add_same_payments{
	###Inserta pago negativo/positivo en orden
	###Aguments: ID_return, pos/neg (positive/negative)
		($id_returns, $opt) = @_;
		if($opt eq 'pos'){$s='1'; $vStatus='Approved';}
		elsif($opt eq 'neg'){$s='-1'; $vStatus='Credit';}
		if($id_returns ne '' and $s ne ''){
			my ($sql) ="SELECT 
						b.ID_orders
						,d.Type
						,d.PmtField1
						,d.PmtField2
						,d.PmtField3
						,d.PmtField4
						,d.PmtField5
						,d.PmtField6
						,d.PmtField7
						,d.PmtField8
						,d.PmtField9
						,d.PmtField10
						,d.PmtField11
						/*,sum((((ifnull(c.SalePrice,0)*$s) - (ifnull(c.Discount,0)*$s)) + (ifnull(c.Tax,0)*$s))) as Amount*/
						,sum((((ifnull(c.SalePrice,0)*$s) - (ifnull(c.Discount,0)*$s)) + (ifnull(c.Tax,0)*$s) + (ifnull(c.Shipping,0)*$s) + (ifnull(c.ShpTax,0)*$s))) as Amount
						,b.merAction as Reason
						,CURDATE() as Paymentdate
						,NULL as AuthCode
						,NULL as AuthDateTime
						,NULL as Captured
						,NULL as CapDate
						,NULL as PostedDate
						,'$vStatus' as Status
						,CURDATE() as Date
						,CURTIME() as Time
						,c.ID_admin_users
						FROM sl_returns_upcs a
						LEFT JOIN sl_returns b using(ID_returns)
						LEFT JOIN sl_orders_products c on b.ID_orders=c.ID_orders and a.ID_orders_products=c.ID_orders_products
						LEFT JOIN sl_orders_payments d on b.ID_orders=d.ID_orders
						WHERE a.ID_returns='$id_returns'
						GROUP BY c.ID_orders ASC LIMIT 1";
			my ($sth) = &Do_SQL($sql);
			&logtxt($sql,$vlogMysql);
			while($rec=$sth->fetchrow_hashref()){
				my ($sql) ="INSERT INTO sl_orders_payments SET 							
							ID_orders='$rec->{ID_orders}'
							,Type='$rec->{Type}'
							,PmtField1='$rec->{PmtField1}'
							,PmtField2='$rec->{PmtField2}'
							,PmtField3='$rec->{PmtField3}'
							,PmtField4='$rec->{PmtField4}'
							,PmtField5='$rec->{PmtField5}'
							,PmtField6='$rec->{PmtField6}'
							,PmtField7='$rec->{PmtField7}'
							,PmtField8='$rec->{PmtField8}'
							,PmtField9='$rec->{PmtField9}'
							,PmtField10='$rec->{PmtField10}'
							,PmtField11='$rec->{PmtField11}'
							,Amount='$rec->{Amount}'
							,Reason='$rec->{Reason}'
							,Paymentdate='$rec->{Paymentdate}'
							,AuthCode='$rec->{AuthCode}'
							,AuthDateTime='$rec->{AuthDateTime}'
							,Captured='$rec->{Captured}'
							,CapDate='$rec->{CapDate}'
							,PostedDate='$rec->{PostedDate}'
							,Status='$rec->{Status}'
							,Date=CURDATE(),
							Time=CURTIME(),
							ID_admin_users='$usr{'id_admin_users'}';";
				my ($sth) = &Do_SQL($sql);
				&logtxt($sql,$vlogMysql);
			}		
		}	
	}	

	sub add_new_products{
	###Inserta linea con nuevo producto en la orden
	###Aguments: ID_return, pos/neg (positive/negative)
		($id_returns, $opt, $merAction, $ReturnFee) = @_;
		if($opt eq 'pos'){$s='1';}
		elsif($opt eq 'neg'){$s='-1';}
		if($id_returns ne '' and $s ne ''){
			if($TaxRate_generic eq ''){$TaxRate='0';}else{$TaxRate=$TaxRate_generic;}
			my($loops) = 0;
			my ($sql) ="SELECT
						b.ID_products_exchange as ID_products
						,b.ID_orders
						,'0' as ID_packinglist
						,NULL as Related_ID_products
						,NULL as ID_products_prices
						,'1' as Quantity
						,(ifnull(b.SPrice,0)*$s) as SalePrice
						,(IFNULL((SELECT Shipping FROM sl_packingopts LIMIT 1),0)*$s) as Shipping
						,(ifnull(f.Cost,0)*$s) as Cost
						,((ifnull(b.SPrice,0)*$s)*(e.Sale_Tax/100)) as Tax
						,(e.Sale_Tax/100) as Tax_percent
						,NULL as Discount
						,'1' as FP
						,NULL as SerialNumber
						,NULL as ShpDate
						,NULL as Tracking
						,NULL as ShpProvider
						,ROUND(((IFNULL((SELECT Shipping FROM sl_packingopts LIMIT 1),0)*$TaxRate)*$s),2) as ShpTax
						,'$TaxRate' as ShpTax_percent
						/*,'0' as ShpTax*/
						/*,'0' as ShpTax_percent*/
						,NULL as PostedDate
						,NULL as Upsell
						,'Active' as Status
						,CURDATE() as Date
						,CURTIME() as Time
						,b.ID_admin_users
						FROM sl_returns b 
						LEFT JOIN sl_skus_parts d ON b.ID_products_exchange=d.ID_sku_products
						LEFT JOIN sl_parts e ON e.ID_parts=d.ID_parts
						LEFT JOIN (SELECT ID_products, Cost FROM (SELECT ID_products, Cost FROM sl_skus_cost ORDER BY date DESC, time DESC) a GROUP BY ID_products) f ON f.ID_products=(d.ID_parts+400000000) 
						WHERE b.ID_returns='$id_returns'
						GROUP BY b.ID_orders, b.ID_products_exchange ASC";
			my ($sth) = &Do_SQL($sql);
			&logtxt($sql,$vlogMysql);
			while($rec=$sth->fetchrow_hashref()){
				$loops++;
				if($loops>1){
					$vShipping=0; $vShpTax=0; $vTaxRate=0; 
				}else{
					$vShipping=$rec->{'Shipping'}; 
					$vShpTax=$rec->{'ShpTax'}; 
					$vTaxRate=$rec->{'ShpTax_percent'};
				}
				$vID_orders=$rec->{'ID_orders'};
				my ($sql) ="INSERT INTO sl_orders_products SET 							
							ID_products='$rec->{ID_products}'
							,ID_orders='$rec->{ID_orders}'
							,ID_packinglist='$rec->{ID_packinglist}'
							,Related_ID_products='$rec->{Related_ID_products}'
							,ID_products_prices='$rec->{ID_products_prices}'
							,Quantity='$rec->{Quantity}'
							,SalePrice='$rec->{SalePrice}'
							,Shipping='$vShipping'
							,Cost='$rec->{Cost}'
							,Tax='$rec->{Tax}'
							,Tax_percent='$rec->{Tax_percent}'
							,Discount='$rec->{Discount}'
							,FP='$rec->{FP}'
							,SerialNumber='$rec->{SerialNumber}'
							,ShpDate='$rec->{ShpDate}'
							,Tracking='$rec->{Tracking}'
							,ShpProvider='$rec->{ShpProvider}'
							,ShpTax='$vShpTax'
							,ShpTax_percent='$vTaxRate'
							,PostedDate='$rec->{PostedDate}'
							,Upsell='$rec->{Upsell}'
							,Status='$rec->{Status}'
							,Date=CURDATE(),
							Time=CURTIME(),
							ID_admin_users='$usr{'id_admin_users'}';";
				my ($sth) = &Do_SQL($sql);
				&logtxt($sql,$vlogMysql);
			}
			if($ReturnFee eq 'Applicable'){&add_shipping_service($vID_orders,'pos',$merAction);}
		}
	}

	sub add_new_payments{
	###Inserta pago positivo en orden
	###Aguments: ID_return, pos/neg (positive/negative)
		($id_returns, $opt, $merAction, $ReturnFee) = @_;
		if($opt eq 'pos'){$s='1'; $vStatus='Approved';}
		elsif($opt eq 'neg'){$s='-1'; $vStatus='Credit';}
		if($id_returns ne '' and $s ne ''){
			if($TaxRate_generic eq ''){$TaxRate='0';}else{$TaxRate=$TaxRate_generic;}
			my ($sql) ="SELECT 
						b.ID_orders
						,d.Type
						,NULL as PmtField1
						,NULL as PmtField2
						,NULL as PmtField3
						,NULL as PmtField4
						,NULL as PmtField5
						,NULL as PmtField6
						,NULL as PmtField7
						,NULL as PmtField8
						,NULL as PmtField9
						,NULL as PmtField10
						,NULL as PmtField11
						,(SUM(
							/*SalePrice*/	(IFNULL(b.SPrice,0)*$s) +									
							/*Tax*/			(((IFNULL(b.SPrice,0)*$s)*(f.Sale_Tax/100))) )+
							/*Shipping*/	(IFNULL((SELECT Shipping FROM sl_packingopts LIMIT 1),0)*$s) + 
							/*ShpTax*/		ROUND(((IFNULL((SELECT Shipping FROM sl_packingopts LIMIT 1),0)*$TaxRate)*$s),2)) as Amount
						,b.merAction as Reason
						,CURDATE() as Paymentdate
						,NULL as AuthCode
						,NULL as AuthDateTime
						,NULL as Captured
						,NULL as CapDate
						,NULL as PostedDate
						,'$vStatus' as Status
						,CURDATE() as Date
						,CURTIME() as Time
						,b.ID_admin_users
						FROM sl_returns b
						LEFT JOIN (SELECT ID_orders, Type FROM sl_orders_payments GROUP BY ID_orders DESC) d on b.ID_orders=d.ID_orders 
						LEFT JOIN sl_skus_parts e ON b.ID_products_exchange=e.ID_sku_products
						LEFT JOIN sl_parts f ON f.ID_parts=e.ID_parts
						WHERE b.ID_returns='$id_returns'
						GROUP BY b.ID_orders ASC LIMIT 1";
			my ($sth) = &Do_SQL($sql);
			&logtxt($sql,$vlogMysql);
			while($rec=$sth->fetchrow_hashref()){
				my ($sql) ="INSERT INTO sl_orders_payments SET 							
								ID_orders='$rec->{ID_orders}'
								,Type='$rec->{Type}'
								,PmtField1='$rec->{PmtField1}'
								,PmtField2='$rec->{PmtField2}'
								,PmtField3='$rec->{PmtField3}'
								,PmtField4='$rec->{PmtField4}'
								,PmtField5='$rec->{PmtField5}'
								,PmtField6='$rec->{PmtField6}'
								,PmtField7='$rec->{PmtField7}'
								,PmtField8='$rec->{PmtField8}'
								,PmtField9='$rec->{PmtField9}'
								,PmtField10='$rec->{PmtField10}'
								,PmtField11='$rec->{PmtField11}'
								,Amount='$rec->{Amount}'
								,Reason='$rec->{Reason}'
								,Paymentdate='$rec->{Paymentdate}'
								,AuthCode='$rec->{AuthCode}'
								,AuthDateTime='$rec->{AuthDateTime}'
								,Captured='$rec->{Captured}'
								,CapDate='$rec->{CapDate}'
								,PostedDate='$rec->{PostedDate}'
								,Status='$rec->{Status}'
								,Date=CURDATE(),
								Time=CURTIME(),
								ID_admin_users='$usr{'id_admin_users'}';";
				my ($sth) = &Do_SQL($sql);
				$id_key = $sth->{'mysql_insertid'};
				&logtxt($sql,$vlogMysql);
			}	
			if($ReturnFee eq 'Applicable'){&add_shipping_payment($id_key,'pos');}	
		}	
	}

	sub add_shipping_service{
	###Inserta linea con servicio por shipping en la orden
	###Aguments: id_orders, pos/neg (positive/negative)
		($id_orders, $opt, $merAction) = @_;
		if($opt eq 'pos'){$s='1';}
		elsif($opt eq 'neg'){$s='-1';}
		if($id_orders ne '' and $s ne '' and $ID_shipping_service ne ''){
			if($TaxRate_generic eq ''){$TaxRate='0';}else{$TaxRate=$TaxRate_generic;}
			my ($sql) ="SELECT
						(c.ID_services+600000000) as ID_products
						,'$id_orders' as ID_orders
						,'0' as ID_packinglist
						,NULL as Related_ID_products
						,NULL as ID_products_prices
						,'1' as Quantity
						,(IFNULL(c.SPrice,0)*$s) as SalePrice
						,'0' as Shipping
						,'0' as Cost
						,((ifnull(c.SPrice,0)*$s)*(c.Tax/100)) as Tax
						,(c.Tax/100) as Tax_percent
						,NULL as Discount
						,'1' as FP
						,NULL as SerialNumber
						,NULL as ShpDate
						,NULL as Tracking
						,NULL as ShpProvider
						,'0' as ShpTax
						,'0' as ShpTax_percent
						,NULL as PostedDate
						,NULL as Upsell
						,'Active' as Status
						,CURDATE() as Date
						,CURTIME() as Time
						,'$usr{id_admin_users}' as ID_admin_users
						FROM  sl_services c
						WHERE c.ID_services='$ID_shipping_service'
						GROUP BY c.ID_services ASC LIMIT 1";
			my ($sth) = &Do_SQL($sql);
			&logtxt($sql,$vlogMysql);
			while($rec=$sth->fetchrow_hashref()){
				my ($sql) ="INSERT INTO sl_orders_products SET 							
							ID_products='$rec->{ID_products}'
							,ID_orders='$rec->{ID_orders}'
							,ID_packinglist='$rec->{ID_packinglist}'
							,Related_ID_products='$rec->{Related_ID_products}'
							,ID_products_prices='$rec->{ID_products_prices}'
							,Quantity='$rec->{Quantity}'
							,SalePrice='$rec->{SalePrice}'
							,Shipping='$rec->{Shipping}'
							,Cost='$rec->{Cost}'
							,Tax='$rec->{Tax}'
							,Tax_percent='$rec->{Tax_percent}'
							,Discount='$rec->{Discount}'
							,FP='$rec->{FP}'
							,SerialNumber='$rec->{SerialNumber}'
							,ShpDate='$rec->{ShpDate}'
							,Tracking='$rec->{Tracking}'
							,ShpProvider='$rec->{ShpProvider}'
							,ShpTax='$rec->{ShpTax}'
							,ShpTax_percent='$rec->{ShpTax_percent}'
							,PostedDate='$rec->{PostedDate}'
							,Upsell='$rec->{Upsell}'
							,Status='$rec->{Status}'
							,Date=CURDATE(),
							Time=CURTIME(),
							ID_admin_users='$usr{'id_admin_users'}';";
				my ($sth) = &Do_SQL($sql);	
				&logtxt($sql,$vlogMysql);
			}
			if($merAction eq 'ReShip'){
				my ($sql) ="SELECT ID_orders_payments FROM sl_orders_payments WHERE ID_orders='$id_orders' AND Status='Approved' GROUP BY ID_orders ASC LIMIT 1;";
				my ($sth) = &Do_SQL($sql);
				$rec=$sth->fetchrow_hashref();
				$id_key=$rec->{'ID_orders_payments'};
				&logtxt($sql,$vlogMysql);
				my ($sql) ="SELECT
							(c.ID_services+600000000) as ID_products
							,(IFNULL(c.SPrice,0)*$s) as SalePrice
							,((ifnull(c.SPrice,0)*$s)*(c.Tax/100)) as Tax
							,(c.Tax/100) as Tax_percent	
							,(IFNULL(c.SPrice,0)*$s) + ((ifnull(c.SPrice,0)*$s)*(c.Tax/100)) as Amount
							FROM  sl_services c
							WHERE c.ID_services='$ID_shipping_service'
							GROUP BY c.ID_services ASC LIMIT 1";
				my ($sth) = &Do_SQL($sql);
				&logtxt($sql,$vlogMysql);
				while($rec=$sth->fetchrow_hashref()){
					my ($sql) ="UPDATE sl_orders_payments SET 							
								Amount=Amount+'$rec->{Amount}'
								WHERE ID_orders_payments='$id_key' LIMIT 1;";
					my ($sth) = &Do_SQL($sql);	
					&logtxt($sql,$vlogMysql);
				}
			}		
		}
	}

	sub add_shipping_payment{
	###Actualiza sumando el precio del Shipping al pago de la orden
	###Aguments: id_key, pos/neg (positive/negative)
		($id_key, $opt) = @_;
		if($opt eq 'pos'){$s='1';}elsif($opt eq 'neg'){$s='-1';}
		if($id_key  and $s ne '' and $ID_shipping_service ne ''){
			my ($sql) ="SELECT
						(c.ID_services+600000000) as ID_products
						,(IFNULL(c.SPrice,0)*$s) as SalePrice
						,((ifnull(c.SPrice,0)*$s)*(c.Tax/100)) as Tax
						,(c.Tax/100) as Tax_percent	
						,(IFNULL(c.SPrice,0)*$s) + ((ifnull(c.SPrice,0)*$s)*(c.Tax/100)) as Amount
						FROM  sl_services c
						WHERE c.ID_services='$ID_shipping_service'
						GROUP BY c.ID_services ASC LIMIT 1";
			my ($sth) = &Do_SQL($sql);
			&logtxt($sql,$vlogMysql);
			while($rec=$sth->fetchrow_hashref()){
				my ($sql) ="UPDATE sl_orders_payments SET 							
							Amount=Amount+'$rec->{Amount}'
							WHERE ID_orders_payments='$id_key' LIMIT 1;";
				my ($sth) = &Do_SQL($sql);	
				&logtxt($sql,$vlogMysql);
			}			
		}
	}

	sub add_orders_notes{
	###Agrega nota a la orden
		($id_orders, $merAction) = @_;

		if($id_orders ne ''){

			my $extra_notes = $va{'returns_note_'. $id_orders} ? $va{'returns_note_'. $id_orders} : '';
			
			&add_order_notes_by_type($id_orders,"Return Processed\nID: ".$id_returns."\nAction: ".$merAction."\n".$extra_notes,"Low");
			#my ($sth) = &Do_SQL($sql);
			&logtxt($sql,$vlogMysql);
			delete($va{'returns_note_'. $id_orders}) if($va{'returns_note_'. $id_orders});
		}
	}

	sub logtxt{
	##Graba SQL en txt
		($logquery,$enabled) = @_;
		if($enabled and $cfg{'path_logtxt'} ne ''){
			my $timestamp = localtime(time);
			my ($sec,$min,$hour,$mday,$mon,$year,$wday,$yday,$isdst)=localtime(time);
    		my $file_timestamp = sprintf ( "%04d%02d%02d_%02d%02d%02d",$year+1900,$mon+1,$mday,$hour,$min,$sec);
			my $filename = $cfg{'path_logtxt'}."logtxt_returns_".$file_timestamp.".txt";			
			open(my $fh, '>>', $filename) or die "Could not open file '$filename' $!";
			print $fh $logquery."\n\r";		
			print $fh "\n\r---".$timestamp."---\n\r";
			close $fh;
		}
	}

	my($sth)=&Do_SQL("SELECT * FROM sl_returns WHERE ID_returns='$id_returns'");	
	while($rec=$sth->fetchrow_hashref()){

		my($id_orders)=$rec->{'ID_orders'};
		my($merAction)=$rec->{'merAction'};
		my($ReturnFee)=$rec->{'ReturnFee'};
		
		if ($rec->{'merAction'} eq 'Exchange'){

			&add_same_products($id_returns,'neg');
			&add_same_payments($id_returns,'neg');			
			&add_new_products($id_returns,'pos',$merAction,$ReturnFee);
			&add_new_payments($id_returns,'pos',$merAction,$ReturnFee);
			&add_orders_notes($id_orders, $merAction);

		}elsif($rec->{'merAction'} eq 'ReShip'){

			#&add_same_products($id_returns,'neg');
			#&add_same_products($id_returns,'pos',$merAction,$ReturnFee);
			
		}elsif($rec->{'merAction'} eq 'Refund'){
			&add_same_products($id_returns,'neg');
			&add_same_payments($id_returns,'neg');
			&add_orders_notes($id_orders, $merAction);
		}elsif($rec->{'merAction'} eq 'Repair Center'){
		}elsif($rec->{'merAction'} eq 'Return to Customer'){
			if ($rec->{'NewShp'} eq 'Applicable'){
			}
		}
	}
}


sub fastbacktoinventory {
# --------------------------------------------------------

# Author: Jose Ramirez Garcia
# Created on: 01/14/2009
# Last Modified on: 
# Last Modified by: 
# Description : 
# Forms Involved: 
# Parameters :
# Last Modified RB: 02/17/09  15:55:08 -- Solo requiere id_returns_upc y id_warehouses
# Last Modification by JRG : 03/13/2009 : Se agrega log

	if($in{'id_returns_upcs'} && $in{'id_warehouses'}){

		# Registering product into warehouse
		my $id_warehouses = $in{'id_warehouses'};
		my $upc = &load_name('sl_returns_upcs','ID_returns_upcs',$in{'id_returns_upcs'},'UPC');
		my $id_product = &load_name('sl_skus','UPC',$upc,'ID_sku_products');
		my $sthinv=&Do_SQL("INSERT INTO sl_warehouses_location set ID_warehouses=$id_warehouses,ID_products=$id_product,Location='A00A',Quantity=1,Date=Curdate(),Time=NOW(),ID_admin_users='$usr{'id_admin_users'}'");
		&auth_logging('warehouses_location_added',$sthinv->{'mysql_insertid'});
		my $dateout = &load_name('sl_orders_products','ID_orders_products',$in{'id_orders_products'},'Date');
		my $idorders = &load_name('sl_orders_products','ID_orders_products',$in{'id_orders_products'},'ID_orders');


		#Determine product Cost
		my $sthcost=&Do_SQL("SELECT IF(Cost IS NULL,0,Cost) FROM sl_orders_products WHERE ID_orders_products = $in{'id_orders_products'} AND ID_products='$id_product' and Date = '$dateout'");
		my $cost=$sthcost->fetchrow();
		
		my $cost_adj = 0;
		if($cost == 0){	
   			($cost, $cost_adj) = &load_sltvcost($id_product);
		}

		# Restore product into inventory
		$cost=0 if(!$cost);
		my $sthsku=&Do_SQL("INSERT INTO sl_skus_cost SET ID_products = '$id_product', ID_purchaseorders = '$in{'id_returns'}', Tblname='sl_returns',Cost=$cost,Cost_Adj='$cost_adj',ID_warehouses=$id_warehouses,Quantity=1,Date=Curdate(),Time=NOW(),ID_admin_users='$usr{'id_admin_users'}'");
		&auth_logging('sku_cost_added',$sthsku->{'mysql_insertid'});
		my ($sth) = &Do_SQL("UPDATE sl_returns_upcs SET ID_warehouses='$in{'id_warehouses'}' WHERE ID_returns_upcs='$in{'id_returns_upcs'}'");
		&auth_logging('returns_upcs_updated',$in{'id_returns'});
	
		if($in{'meraction'} ne 'Exchange' and $in{'meraction'} ne 'ReShip' and $in{'meraction'} and 'Refund'){
			my $sthsku=&Do_SQL("INSERT INTO sl_returns_notes SET ID_returns ='$in{'id_returns'}', Notes='Fast Back to Inventory:$in{'id_returns_upcs'}',Type='Sorting',Date=CURDATE(),TIME=NOW(),ID_admin_users='$usr{'id_admin_users'}'");
			&auth_logging('returns_noteadded',$in{'id_returns'});
		}


		## Movimientos Contables
		my ($order_type, $ctype, $ptype,@params);
		my ($sth) = &Do_SQL("SELECT Ptype, Type FROM sl_orders INNER JOIN sl_customers USING(ID_customers) WHERE ID_orders = '$idorders';");
		($order_type, $ctype) = $sth->fetchrow();
		@params = ($idorders,$id_product,$cost);
		&accounting_keypoints('order_fastbacktoinventory_'. $ctype .'_'. $order_type, \@params );

	} 

	&auth_logging('fastbacktoinventory_done',$in{'id_returns'});
	delete($in{'id_returns_upcs'});
	delete($in{'id_warehouses'});
	$in{'modify'}	= 	$in{'view'};
	delete($in{'view'});	
}

1;