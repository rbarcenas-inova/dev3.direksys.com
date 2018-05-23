#####################################################################
########                   APARTS	        		           		#########
#####################################################################



sub mer_po {
# --------------------------------------------------------
	$in{'tab'}=1 if (!$in{'tab'});
	$in{'id_purchaseorders'} = int($in{'id'});

	if ($in{'tab'} eq 1){
		if ($in{'action'}){
			my ($err);
			foreach $key (keys %in){
				if ($key =~ /line(\d+)/){
					$in{$key} = int($in{$key});
					++$err if (!$in{$key});
					my ($sth) = &Do_SQL("SELECT COUNT(*) FROM sl_purchaseorders_items WHERE ID_purchaseorders_items='$1' AND ID_purchaseorders='$in{'id_purchaseorders'}' AND Qty>='$in{$key}'");
					++$err if ($sth->fetchrow eq 0);
				}
			}
			if (!$err){
				foreach $key (keys %in){
					if ($key =~ /line(\d+)/ and $1>0 and $in{'id_purchaseorders'}>0){
						$in{$key} = int($in{$key});
						my ($sth) = &Do_SQL("UPDATE sl_purchaseorders_items SET Received='$in{$key}' WHERE ID_purchaseorders_items='$1' AND ID_purchaseorders='$in{'id_purchaseorders'}' AND Qty>='$in{$key}'");
					}
				}			
				$va{'message'} = &trans_txt('record_updated');
				&auth_logging('record_updated',$in{'id_purchaseorders'});
			}else{
				$va{'message'} = &trans_txt('reqfields');
			}

			
		}
		
		my ($line);
		## ITEMS LIST
		my ($choices_on,$tot_qty,$tot_po,$tax_po,$subtot_po,$vendor_sku,$name);
		my (@c) = split(/,/,$cfg{'srcolors'});
		my ($sth) = &Do_SQL("SELECT COUNT(*) FROM sl_purchaseorders_items WHERE ID_purchaseorders='$in{'id_purchaseorders'}' $query");
		$va{'matches'} = $sth->fetchrow();
		if ($va{'matches'}>0){
			my ($sth) = &Do_SQL("SELECT *, (Qty - Received) as quantity FROM sl_purchaseorders_items WHERE ID_purchaseorders='$in{'id_purchaseorders'}' ORDER BY ID_purchaseorders_items DESC ;");
			while ($rec = $sth->fetchrow_hashref){
				$d = 1 - $d;
				++$line;
				$id_products = $rec->{'ID_products'};
				## Name Model
				if ($rec->{'ID_products'} =~/^4/){
					## Part
					$name = &load_db_names('sl_parts','ID_parts',($rec->{'ID_products'}-400000000),'[Model]<br>[Name]');
					$id_products = ( $rec->{'ID_products'} - 400000000 );
				}elsif($rec->{'ID_products'} =~/^5/){
					## Non Inventory
					$name = &load_db_names('sl_noninventory','ID_noninventory',($rec->{'ID_products'}-500000000),'[Name]');
					$id_products = ( $rec->{'ID_products'} - 500000000 );
				}	
				$va{'searchresults'} .= "<tr bgcolor='$c[$d]'>\n";
				$va{'searchresults'} .= "   <td class='smalltext' valign='top' nowrap>$line</td>\n";	
				$va{'searchresults'} .= "   <td class='smalltext' valign='top'>".&format_sltvid($rec->{'ID_products'})."</td>\n";
				$va{'searchresults'} .= "   <td class='smalltext'>$name </td>\n";
				$va{'searchresults'} .= "   <td class='smalltext' align='right' valign='top'>$rec->{'Qty'}</td>\n";
				$va{'searchresults'} .= "   <td class='smalltext' align='right' valign='top'>".&format_price($rec->{'Price'})."</td>\n";
				$va{'searchresults'} .= "   <td class='smalltext' align='right' valign='top'><input type='text' name='line$rec->{'ID_purchaseorders_items'}'  onfocus='focusOn( this )' onblur='focusOff( this )' size='10' value='$rec->{'Received'}'</td>\n";
				$va{'searchresults'} .= "   <td class='smalltext' align='right' valign='top'> ".&format_price($rec->{'Total'})."</td>\n";
				
				$va{'searchresults'} .= "</tr>\n";
			}
		}else{
			$va{'matches'} = 0;
			$va{'pageslist'} = 1;
			$va{'searchresults'} = qq|
				<tr>
					<td colspan='7' align="center">|.&trans_txt('search_nomatches').qq|</td>
				</tr>\n|;
		}
		print "Content-type: text/html\n\n";
		print &build_page('customapps:po_home.html');
	}else{
		print "Content-type: text/html\n\n";
		print &build_page('customapps:po_payments.html');
	}
}

sub opr_orders {
# --------------------------------------------------------
	#cgierr("This is the module to cancel");
	$in{'tab'}=1 if (!$in{'tab'});
	$in{'id_orders'} = int($in{'id'});

	if ($in{'tab'} eq 1){
		################################################################
		####### PRE SHIPPED (1) 
		################################################################
		if ($in{'action'}){
			my ($err);
			foreach my $key (keys %in){
				if ($key =~ /shpdate(\d+)/){
					$in{'cost'.$1} = $in{'cost'.$1}*1;
					++$err if (!$in{'cost'.$1});
					++$err if (!$in{'shpprovider'.$1});
					++$err if (!$in{'shpdate'.$1});
				}
			}
			if (!$err){
				foreach my $key (keys %in){
					if ($key =~ /shpdate(\d+)/ and $in{'cost'.$1}>0 and $in{'shpprovider'.$1} and $1>0 and $in{'id_orders'}>0){
						$in{'cost'.$1} = $in{'cost'.$1}*1;
						my ($sth) = &Do_SQL("UPDATE sl_orders_products SET 
							ShpDate='$in{'shpdate'.$1}',Cost='$in{'cost'.$1}',ShpProvider='$in{'shpprovider'.$1}',Tracking='$in{'tracking'.$1}', PostedDate = CURDATE()
						 WHERE ID_orders_products='$1' AND ID_orders='$in{'id_orders'}'");
						my ($sth) = &Do_SQL("SELECT ID_orders_parts FROM sl_orders_parts WHERE ID_orders_products='$1'");
						if($sth->fetchrow>0){
							my ($sth) = &Do_SQL("UPDATE sl_orders_parts SET 
							Cost='$in{'cost'.$1}',ShpDate='$in{'shpdate'.$1}',ShpProvider='$in{'shpprovider'.$1}',Tracking='$in{'tracking'.$1}',Status='Shipped'
							WHERE ID_orders_products=$1");
						}else{
							my ($sth) = &Do_SQL("SELECT * FROM sl_orders_products WHERE ID_orders_products='$1'");
							$rec = $sth->fetchrow_hashref;
							my ($sth) = &Do_SQL("INSERT INTO sl_orders_parts SET 
							ID_parts=$rec->{'Related_ID_products'}-400000000, ID_orders_products='$rec->{'ID_orders_products'}',
							Quantity='$rec->{'Quantity'}',Cost='$in{'cost'.$1}',ShpDate='$in{'shpdate'.$1}',ShpProvider='$in{'shpprovider'.$1}',Tracking='$in{'tracking'.$1}',Status='Shipped',
							Date=CURDATE(), Time=CURTIME(), ID_admin_users='$usr{'id_admin_users'}';");
						}
					}
				}
				$va{'message'} = &trans_txt('record_updated');
				&auth_logging('record_updated',$in{'id_orders'});
			}else{
				$va{'message'} = &trans_txt('reqfields');
			}
		}
		
		my ($line);
		my ($shpprovider) = &build_select_from_enum('ShpProvider','sl_orders_products');
		## ITEMS LIST
		my ($choices_on,$tot_qty,$tot_po,$tax_po,$subtot_po,$vendor_sku,$name);
		my (@c) = split(/,/,$cfg{'srcolors'});
		my ($sth) = &Do_SQL("SELECT COUNT(*) FROM sl_orders_products WHERE ID_orders='$in{'id_orders'}' AND Related_ID_products>0");
		$va{'matches'} = $sth->fetchrow();
		if ($va{'matches'}>0){
			my ($sth) = &Do_SQL("SELECT * FROM sl_orders_products WHERE ID_orders='$in{'id_orders'}' AND Related_ID_products>0 ORDER BY ID_orders_products DESC ;");
			while ($rec = $sth->fetchrow_hashref){
				#my ($sth_int) = &Do_SQL("SELECT *,
				#				(IF(sl_orders_products.Related_ID_products is null,
				#					sl_orders_products.ID_products,
				#					sl_orders_products.Related_ID_products)) as idproduct,
				#				sl_orders_products.Date as slop_date
				#				FROM sl_orders_products 
				#				INNER JOIN sl_orders using(ID_orders)
				#				WHERE
				#				sl_orders_products.Related_ID_products='$rec->{'Related_ID_products'}'
				#				AND Related_ID_products>0 
				#				AND sl_orders_products.Cost>0
				#				ORDER BY sl_orders_products.Date DESC LIMIT 1;");
				my ($sth_int) = &Do_SQL("SELECT * FROM `sl_skus_cost` WHERE `ID_products`='$rec->{'Related_ID_products'}'
											ORDER BY Date DESC,Time DESC LIMIT 1;");
				my $rec_int = $sth_int->fetchrow_hashref();
				
				$d = 1 - $d;
				++$line;
				$va{'date_list'} = "#shpdate$rec->{'ID_orders_products'},";
				## Name Model
				$name = &load_db_names('sl_parts','ID_parts',($rec->{'Related_ID_products'}-400000000),'[Model]<br>[Name]');

				$va{'searchresults'} .= "<tr bgcolor='$c[$d]'>\n";
				$va{'searchresults'} .= "   <td class='smalltext' valign='top' nowrap>$line</td>\n";	
				$va{'searchresults'} .= "   <td class='smalltext' valign='top'>".&format_sltvid($rec->{'Related_ID_products'})."</td>\n";
				$va{'searchresults'} .= "   <td class='smalltext'>$name </td>\n";
				$va{'searchresults'} .= "   <td class='smalltext' align='right' valign='top'>$rec->{'Quantity'}</td>\n";
				$va{'searchresults'} .= "   <td class='smalltext' align='right' valign='top' nowrap>".&format_price($rec->{'SalePrice'} / $rec->{'Quantity'})."</td>\n";
				$va{'searchresults'} .= "   <td class='smalltext' align='right' valign='top' nowrap>".&format_price($rec->{'Shipping'})."</td>\n";

				if($in{'tab'} eq 4){
					$va{'searchresults'} .= "   <td class='smalltext' align='right' valign='top'>$rec->{'Cost'}</td>\n";
					$va{'searchresults'} .= "   <td class='smalltext' valign='top'>$rec->{'ShpDate'}<br>\n";
					$va{'searchresults'} .= "   $rec->{'Tracking'}<br>\n";
					$va{'searchresults'} .= "   $rec->{'ShpProvider'}\n";
				}else{
					$rec->{'Cost'} = ($rec_int->{'Cost'})?$rec_int->{'Cost'}:$rec->{'Cost'};
					$va{'searchresults'} .= "   <td class='smalltext' align='right' valign='top'><input type='text' name='cost$rec->{'ID_orders_products'}'  onfocus='focusOn( this )' onblur='focusOff( this )' size='10' value='$rec->{'Cost'}'></td>\n";
					$va{'searchresults'} .= "   <td class='smalltext' valign='top'><input type='text' id='shpdate$rec->{'ID_orders_products'}' name='shpdate$rec->{'ID_orders_products'}'  onfocus='focusOn( this )' onblur='focusOff( this )' size='10' value='$rec->{'ShpDate'}'><br>\n";
					$va{'searchresults'} .= "   <input type='text' name='tracking$rec->{'ID_orders_products'}'  onfocus='focusOn( this )' onblur='focusOff( this )' size='20' value='$rec->{'Tracking'}'><br>\n";
					$va{'searchresults'} .= "   <select name='shpprovider$rec->{'ID_orders_products'}' onFocus='focusOn( this )' onBlur='focusOff( this )'>
														<option value=''>---</option>
														$shpprovider
													</select>\n";
				}
				$va{'searchresults'} .= "</tr>\n";
			}
			chop($va{'date_list'});
		}else{
			$va{'matches'} = 0;
			$va{'pageslist'} = 1;
			$va{'searchresults'} = qq|
				<tr>
					<td colspan='7' align="center">|.&trans_txt('search_nomatches').qq|</td>
				</tr>\n|;
		}
		print "Content-type: text/html\n\n";
		print &build_page('customapps:orders_home.html');

	}elsif($in{'tab'} eq 3){
		################################
		####### (3)TO SHIPPED TAB
		################################
		if ($in{'action'}){
			if (!$in{'orderdate'}){
				++$err;
				$error{'orderdate'} = &trans_txt('required');
			}
			delete($in{'shpdate'});
			
			if (!$err){

				# Inicializa la transaccion
				&Do_SQL("START TRANSACTION;");

				my ($sth) = &Do_SQL("UPDATE sl_orders SET PostedDate='".$cfg{'date_transition'}."', Status='Shipped', Date='".$cfg{'date_transition'}."' WHERE ID_orders='$in{'id'}'");

				###----------------------------------------------------------
				### Se agregan los registros en sl_orders_parts
				###----------------------------------------------------------
				my $sth_pp = &Do_SQL("SELECT 
										op.ID_orders_products, sp.ID_sku_products, sp.ID_parts, sp.Qty AS Qty, 
										IF( op.Cost != 0, 
											op.Cost,
										    (SELECT Cost_Avg FROM cu_skus_trans WHERE id_products = 400000000 + sp.ID_parts ORDER BY DATE DESC LIMIT 1)
										) AS Cost
										FROM sl_orders_products op
											INNER JOIN sl_skus_parts sp ON op.ID_products=sp.ID_sku_products
										WHERE op.ID_orders=".$in{'id_orders'}." AND op.Status='Active';");
				while (my $rec = $sth_pp->fetchrow_hashref()) {
					if( $rec->{'Cost'} eq '' ){
						++$err;
						$va{'message'} = &trans_txt('no_cost').' '.$rec->{'ID_parts'};
						&Do_SQL("ROLLBACK;");
					}else{
						&Do_SQL("INSERT INTO sl_orders_parts(ID_parts, ID_orders_products, Quantity, Cost, ShpDate, Tracking, ShpProvider, PostedDate, Status, Date, Time, ID_admin_users) 
								 VALUES(".$rec->{'ID_parts'}.", ".$rec->{'ID_orders_products'}.", ".$rec->{'Qty'}.", ".$rec->{'Cost'}.", '".$cfg{'date_transition'}."', 'DRIVER', 'DRIVER', '".$cfg{'date_transition'}."', 'Shipped', CURDATE(), CURTIME(), 1);");
					}
				}

				if (!$err){
					###----------------------------------------------------------
					sleep(1);
					
					###----------------------------------------------------------
					### Se genera la contabilidad por cada producto de la orden
					###----------------------------------------------------------
					my $sth_prod = &Do_SQL("SELECT ID_orders_products FROM sl_orders_products WHERE ID_orders=".$in{'id_orders'}." AND `Status`='Active';");
					
					# Movimientos de contabilidad
					my ($order_type, $ctype, $ptype,@params);
					my ($sth) = &Do_SQL("SELECT Ptype, Type FROM sl_orders INNER JOIN sl_customers USING(ID_customers) WHERE ID_orders = '".$in{'id_orders'}."';");
					($order_type, $ctype) = $sth->fetchrow();

					while ($id_ord_prod = $sth_prod->fetchrow_array()) {
						&Do_SQL("UPDATE sl_orders_products
									INNER JOIN 
									(
									 	SELECT 
											ID_orders_products
											, SUM(sl_orders_parts.Cost * sl_orders_parts.Quantity) As ct
											, sl_orders_parts.Date AS sd
											, sl_orders_parts.Tracking tr
											, sl_orders_parts.ShpProvider pr
										FROM sl_orders_parts INNER JOIN sl_orders_products
										USING(ID_orders_products)
										WHERE ID_orders_products = '".$id_ord_prod."'
										GROUP BY ID_orders_products
									)tmp
									USING(ID_orders_products) 
									SET Cost = ct, ShpDate = sd, Tracking = tr, ShpProvider = pr, PostedDate = sd
								WHERE ID_orders_products = '$id_ord_prod';");	
						&Do_SQL("UPDATE `sl_orders_products` 
									SET `ShpDate`='".$cfg{'date_transition'}."', `PostedDate`='".$cfg{'date_transition'}."' 
								WHERE `ID_orders_products`=".$id_ord_prod.";");

						@params = ($in{'id_orders'}, $id_ord_prod);
						&accounting_keypoints('order_products_inventoryout_'. $ctype .'_'. $order_type, \@params );

						&Do_SQL("UPDATE sl_movements 
									SET EffDate = '".$cfg{'date_transition'}."', ID_journalentries='-1' 
								 WHERE ID_tableused = '".$in{'id_orders'}."' AND tableused = 'sl_orders' AND TIMESTAMPDIFF(SECOND,CONCAT(Date,' ',Time) , NOW()) BETWEEN 0 AND 20;");
					}
					###----------------------------------------------------------

					###----------------------------------------------------------
					### Aplica la contabilidad final
					###----------------------------------------------------------				
					my @params = ($in{'id_orders'});
					my $this_keypoint = 'order_products_scanned_'. $ctype .'_'. $order_type;
					&accounting_keypoints($this_keypoint, \@params );
					&Do_SQL("UPDATE sl_movements 
								SET EffDate = '".$cfg{'date_transition'}."', ID_journalentries='-1' 
							 WHERE ID_tableused = '".$in{'id_orders'}."' AND tableused = 'sl_orders' AND TIMESTAMPDIFF(SECOND,CONCAT(Date,' ',Time) , NOW()) BETWEEN 0 AND 20;");
					&Do_SQL("UPDATE cu_invoices INNER JOIN cu_invoices_lines USING(ID_invoices) 
								SET doc_date = '2010-01-01', `Status`='Void' 
							 WHERE cu_invoices_lines.ID_orders=".$in{'id_orders'}." AND cu_invoices.`Status`='New' AND cu_invoices.ID_admin_users='".$usr{'id_admin_users'}."' AND TIMESTAMPDIFF(SECOND,CONCAT(cu_invoices.Date,' ',cu_invoices.Time) , NOW()) BETWEEN 0 AND 25;");
					###----------------------------------------------------------

					# Logs & msj
					&auth_logging('opr_orders_stShipped',$in{'id'});
					&status_logging($in{'id'},'Shipped');
					$va{'message'} = &trans_txt('record_updated');

					# Confirma la transaccion
					&Do_SQL("COMMIT;");
				}
			}else{
				$va{'message'} = &trans_txt('reqfields');
			}
		}
		my ($sth) = &Do_SQL("SELECT Date,PostedDate FROM sl_orders WHERE ID_orders='$in{'id'}'");
		($in{'orderdate'},$in{'shpdate'}) = $sth->fetchrow_array();
		print "Content-type: text/html\n\n";
		print &build_page('customapps:orders_toshipped.html');	
	}elsif($in{'tab'} eq 4){
		################################
		####### (4)FULL RETURN
		################################
		my ($sth) = &Do_SQL("SELECT COUNT(*) FROM sl_orders_products WHERE ID_orders='$in{'id_orders'}' AND Related_ID_products>0 AND (ShpDate IS NULL OR ShpDate='')");
		if($sth->fetchrow>0){
			++$err;
			$va{'message'} = &trans_txt('trans_order_not_fullshipped');
		}
		if ($in{'action'}){
			if (!$in{'orderdate'}){
				++$err;
				$error{'orderdate'} = &trans_txt('required');
			}
			if (!$in{'shpdate'}){
				++$err;
				$error{'shpdate'} = &trans_txt('required');
			}
			if (!$in{'retdate'}){
				++$err;
				$error{'retdate'} = &trans_txt('required');
			}
			if (!$err){
				#my ($sth) = &Do_SQL("UPDATE sl_orders SET PostedDate='$in{'shpdate'}', Status='Shipped',Date='$in{'orderdate'}' WHERE ID_orders='$in{'id'}'");
				#$va{'message'} = &trans_txt('record_updated');
			}else{
				$va{'message'} = &trans_txt('reqfields');
			}
		}
		my ($sth) = &Do_SQL("SELECT Date,PostedDate FROM sl_orders WHERE ID_orders='$in{'id'}'");
		($in{'orderdate'},$in{'shpdate'}) = $sth->fetchrow_array();
		print "Content-type: text/html\n\n";
		print &build_page('customapps:orders_fullreturn.html');	
	}else{
		################################
		####### (2)TO PRE-PAYMENT
		################################
		if ($in{'action'}){			
			my ($err);
			foreach $key (keys %in){
				if ($key =~ /capdate(\d+)/ ){
					++$err if (!$in{$key});
				}
			}
			
			if (!$err){
				# Inicializa la transaccion
				&Do_SQL("START TRANSACTION;");
				foreach $key (keys %in){
					if ($key =~ /capdate(\d+)/ and $1>0 and $in{'id_orders'}>0){
						if ($in{$key}){							
							my ($sth) = &Do_SQL("UPDATE sl_orders_payments 
													SET Captured='Yes', CapDate='".$cfg{'date_transition'}."', PostedDate='".$cfg{'date_transition'}."', Status='Approved'
						 						 WHERE ID_orders_payments='$1' AND ID_orders='$in{'id_orders'}'");
							#CapDate='$in{$key}'

							#######
							####### Movimientos de contabilidad
							#######
							my ($order_type, $ctype, $ptype,@params);
							my ($sth) = &Do_SQL("SELECT Ptype, Type FROM sl_orders INNER JOIN sl_customers USING(ID_customers) WHERE ID_orders = '$in{'id_orders'}';");
							($order_type, $ctype) = $sth->fetchrow();
							#@params = (!$ida_banks) ? ($in{'id_orders'}, $idpp) : ($in{'id_orders'}, $idpp, $ida_banks);
							@params = ($in{'id_orders'}, $1, 1);
							$ptype = 'Credit-Card';
							&accounting_keypoints('order_deposit_'. $ctype .'_'. $order_type .'_'. $ptype, \@params );
							
							&Do_SQL("UPDATE sl_movements 
										SET EffDate = '".$cfg{'date_transition'}."', ID_journalentries='-1' 
									 WHERE ID_tableused = '".$in{'id_orders'}."' AND tableused = 'sl_orders' AND TIMESTAMPDIFF(SECOND,CONCAT(Date,' ',Time) , NOW()) BETWEEN 0 AND 20;");
						}
					}
				}

				$va{'message'} = &trans_txt('record_updated');

				# Confirma la transaccion
				&Do_SQL("COMMIT;");
			}else{
				$va{'message'} = &trans_txt('reqfields');
			}
		}
		
		my ($line);
		## ITEMS LIST
		my ($choices_on,$tot_qty,$tot_po,$tax_po,$subtot_po,$vendor_sku,$name);
		my (@c) = split(/,/,$cfg{'srcolors'});
		my ($sth) = &Do_SQL("SELECT COUNT(*) FROM sl_orders_payments WHERE ID_orders='$in{'id_orders'}' AND Amount>0");
		$va{'matches'} = $sth->fetchrow();
		if ($va{'matches'}>0){
			my ($sth) = &Do_SQL("SELECT * FROM sl_orders_payments WHERE ID_orders='$in{'id_orders'}' AND Amount>0 AND Status != 'Cancelled' ORDER BY ID_orders_payments DESC;");
			while ($rec = $sth->fetchrow_hashref){
				$d = 1 - $d;
				++$line;
				$va{'date_list'} = "#capdate$rec->{'ID_orders_payments'},";
				## Name Model
				$name = &load_db_names('sl_parts','ID_parts',($rec->{'Related_ID_products'}-400000000),'[Model]<br>[Name]');

				$va{'searchresults'} .= "<tr bgcolor='$c[$d]'>\n";
				$va{'searchresults'} .= "   <td class='smalltext' valign='top' nowrap>$line</td>\n";	
				$va{'searchresults'} .= "   <td class='smalltext' valign='top'>$rec->{'Type'}</td>\n";
				$va{'searchresults'} .= "   <td class='smalltext' align='right' valign='top' nowrap>".&format_price($rec->{'Amount'})."</td>\n";
				$va{'searchresults'} .= "   <td class='smalltext' align='right' valign='top' nowrap>$rec->{'Status'}</td>\n";
				$va{'searchresults'} .= "   <td class='smalltext' align='right' valign='top'>$rec->{'Paymentdate'}</td>\n";
				$va{'searchresults'} .= "   <td class='smalltext' align='right' valign='top'><input type='text' id='capdate$rec->{'ID_orders_payments'}' name='capdate$rec->{'ID_orders_payments'}'  onfocus='focusOn( this )' onblur='focusOff( this )' size='10' value='$rec->{'CapDate'}'></td>\n";
				$va{'searchresults'} .= "</tr>\n";
			}
			chop($va{'date_list'});
		}else{
			$va{'matches'} = 0;
			$va{'pageslist'} = 1;
			$va{'searchresults'} = qq|
				<tr>
					<td colspan='7' align="center">|.&trans_txt('search_nomatches').qq|</td>
				</tr>\n|;
		}
		print "Content-type: text/html\n\n";
		print &build_page('customapps:orders_payment.html');
	}
	if ($in{'action'}) {
		
		&add_order_notes_by_type($in{'id_orders'},'[Transition]',"High");
	}
}

sub mer_bills {
# --------------------------------------------------------
	$in{'tab'}=1 if (!$in{'tab'});
	$in{'id_bills'} = int($in{'id'});
	my ($sth) = &Do_SQL("SELECT * FROM sl_bills WHERE ID_bills='$in{'id_bills'}';");
	my ($rec) = $sth->fetchrow_hashref;
	if($in{'action'}){
		my ($err);
		$in{'amount'} = $in{'amount'}*1;
		$in{'exchange_rate'} = $in{'exchange_rate'}*1;
		if(!$in{'exchange_rate'} and $rec->{'Currency'} ne $cfg{'acc_default_currency'}){
			++$err;
			$error{'exchange_rate'} = &trans_txt('required');
		}
		
		if(!$in{'amount'}){
			++$err;
			$error{'amount'} = &trans_txt('required');
		}elsif ($in{'amount'} > load_bill_balance($rec->{'Type'},$rec->{'Currency'},$in{'id_bills'})){
			++$err;
			$error{'amount'} = &trans_txt('invalid');
		}
		if(!$in{'paydate'}){
			++$err;
			$error{'paydate'} = &trans_txt('required');
		}
		if (!$err){
			if ($rec->{'Currency'} eq $cfg{'acc_default_currency'}) {
				$in{'amountcurrency'} = 'NULL'
			}else{
				$in{'amountcurrency'} = $in{'amount'};
				$in{'amount'} = $in{'amount'}*$in{'exchange_rate'};
			}
			$id_bank = &load_name('sl_banks','Name','Internal Use','ID_banks');
			if (!$id_bank){
				my ($sth) = &Do_SQL("INSERT INTO sl_banks SET Name='Internal Use',BankName='Internal Use',Status='Inactive',Date=CURDATE(),Time=CURTIME(),ID_admin_users=1");
				$id_bank = $sth->{'mysql_insertid'};
			}
			
			
			my ($sth) = &Do_SQL("INSERT INTO sl_banks_movements SET
						Type='Debits',ID_banks=$id_bank,BankDate='$in{'paydate'}',Amount=$in{'amount'},
						AmountCurrency=$in{'amountcurrency'},
						RefNum='".&filter_values($in{'refnum'})."', Memo='".&filter_values($in{'memo'})."',
						Date=CURDATE(),Time=CURTIME(),ID_admin_users='$usr{'id_admin_users'}'");
			my ($new_id) = $sth->{'mysql_insertid'};
			my ($sth) = &Do_SQL("INSERT INTO sl_banks_movrel SET
						ID_banks_movements=$new_id,
						tablename='bills', tableid=$in{'id_bills'},
						Date=CURDATE(),Time=CURTIME(),ID_admin_users='$usr{'id_admin_users'}'");
			if (load_bill_balance($rec->{'Type'},$rec->{'Currency'},$in{'id_bills'})>0){
				my ($sth) = &Do_SQL("UPDATE sl_bills SET Status='Partly Paid' WHERE ID_bills=$in{'id_bills'}");
				$rec->{'Status'} = 'Partly Paid';
			}else{
				my ($sth) = &Do_SQL("UPDATE sl_bills SET Status='Paid' WHERE ID_bills=$in{'id_bills'}");
				$rec->{'Status'} = 'Paid';
			}
			$va{'message'} = &trans_txt('record_updated');
			&auth_logging('record_updated',$in{'id_bills'});
		}else{
			$va{'message'} = &trans_txt('reqfields');
		}
		
	}
	
	
	
	$in{'billamount'} = &format_price($rec->{'Amount'});
	$in{'billstatus'} = $rec->{'Status'};
	$in{'billcurrency'} = $rec->{'Currency'};
	$in{'maincurrency'} = $cfg{'acc_default_currency'};
	$in{'billbalance'} = &format_price(load_bill_balance($rec->{'Type'},$rec->{'Currency'},$in{'id_bills'}));
	if ($rec->{'Currency'} eq $cfg{'acc_default_currency'}) {
		$va{'style'} = 'display:none';
	}
	print "Content-type: text/html\n\n";
	print &build_page('customapps:bills_home.html');
}

sub load_bill_balance {
# --------------------------------------------------------
	my ($type,$currency,$id_bills) = @_;
	if ($type eq 'Bill') {
		$sql_string = "
			SELECT ifnull(Amount - (
				SELECT ifnull(SUM(Amount),0)as Amount 
				FROM sl_banks_movrel 
				INNER JOIN sl_banks_movements USING(ID_banks_movements) 
				WHERE tablename='bills' 
				AND tableid=bills.ID_bills AND Type='Credits'
			) + (
				SELECT ifnull(SUM(Amount),0)as Amount 
				FROM sl_banks_movrel 
				INNER JOIN sl_banks_movements USING(ID_banks_movements) 
				WHERE tablename='bills' 
				AND tableid=bills.ID_bills AND Type='Debits'
			) - (
				SELECT ifnull(SUM(sl_bills_applies.Amount),0)as Amount 
				FROM sl_bills_applies 
				INNER JOIN sl_bills USING(ID_bills)
				WHERE ID_bills_applied = bills.ID_bills
				AND sl_bills.Type IN ('Deposit','Credit')
			), 0)as Amount
			FROM sl_bills as bills
			WHERE ID_bills = '".$id_bills."';";
		if ($currency ne $cfg{'acc_default_currency'}) {
			$sql_string = "
				SELECT ifnull(Amount - (
					SELECT TRUNCATE(ifnull(SUM(AmountCurrency),0),4)as Amount 
					FROM sl_banks_movrel 
					INNER JOIN sl_banks_movements USING(ID_banks_movements) 
					WHERE tablename='bills' 
					AND tableid=bills.ID_bills AND Type='Credits'
				) + (
					SELECT TRUNCATE(ifnull(SUM(AmountCurrency),0),4)as Amount 
					FROM sl_banks_movrel 
					INNER JOIN sl_banks_movements USING(ID_banks_movements) 
					WHERE tablename='bills' 
					AND tableid=bills.ID_bills AND Type='Debits'
				) - (
					SELECT ifnull(SUM(sl_bills_applies.Amount),0)as Amount 
					FROM sl_bills_applies 
					INNER JOIN sl_bills USING(ID_bills)
					WHERE ID_bills_applied = bills.ID_bills
					AND sl_bills.Type IN ('Deposit','Credit')
				), 0)as Amount
				FROM sl_bills as bills
				WHERE ID_bills = '".$id_bills."';";
		}
		my ($sth) = &Do_SQL($sql_string);
		return $sth->fetchrow();
	}
	return 0;
}

1;
