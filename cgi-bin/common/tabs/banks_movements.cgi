#####################################################################
########                   banks movements                  #########
#####################################################################
sub load_tabsconf {
# --------------------------------------------------------
	if ($in{'tab'} eq 2){
		## Notes Tab
		$va{'tab_type'}  = 'notes';
		$va{'tab_title'} = &trans_txt('notes');
		$va{'tab_table'} = 'sl_banks_movements_notes';
	}elsif($in{'tab'} eq 3){
		## Notes Tab
		$va{'tab_type'}  = 'logs';
		$va{'tab_title'} = &trans_txt('logs');
		$va{'tab_table'} = 'sl_banks_movements';
	}elsif($in{'tab'} eq 4){
		## Movements 
		$va{'tab_type'}  = 'movs';
		$va{'tab_title'} = &trans_txt('movs');
		$va{'tab_table'} = 'sl_banks_movements';
		$va{'tab_idvalue'} = $in{'view'};
		$va{'edit_movements'} = '0';
	}
}


# tab Related
sub load_tabs1 {
# --------------------------------------------------------
	my $flag=0;
	$sl_banks_movements_amount = &load_name('sl_banks_movements','ID_banks_movements',$in{'view'},'Amount');
	$va{'button'} = '<p align="center"><input type="submit" value="Apply" class="button"></p>';
	my $invoice_status = ($cfg{'invoice_status'} ne '')?$cfg{'invoice_status'}:'Certified';
	
	## Validamos si este movimiento es editable
	my $sth=&Do_SQL("SELECT COUNT(*)movs, tablename FROM sl_banks_movrel WHERE ID_banks_movements=".$in{'id_banks_movements'}.";");
	my ($movs, $tablename) = $sth->fetchrow_array;
	## Si este Banks Movements aun no esta aplicado
	$va{'display_add_aux'} = ($tablename ne 'accounts')?'':($movs == 0)?'':'display: none;';
	$va{'display_add'} = ($movs == 0)?'':'display: none;';
	$va{'display_accounts'} = (($movs > 0) and ($tablename ne 'accounts'))?'display: none;':'';
	
	if ($tablename eq 'accounts') {
		## List records  from  tablename = accounts
		$va{'detail_searchresults'}='';
		my $recs=0;
		my $sth=&Do_SQL("SELECT sl_accounts.Name, sl_accounts.ID_accounts, sl_accounts.ID_accounting, sl_banks_movrel.AmountPaid, sl_banks_movrel.ID_banks_movrel
			FROM sl_banks_movrel 
			INNER JOIN sl_accounts ON sl_accounts.ID_accounts=sl_banks_movrel.tableid
			WHERE 1 
			AND tablename='accounts' 
			AND ID_banks_movements='".$in{'id_banks_movements'}."';");
		while (my $rec = $sth->fetchrow_hashref) {
			$recs++;
			$va{'detail_searchresults'} .= qq|
					<tr>
						<td align='center'><!--<a href="/cgi-bin/mod/[ur_application]/dbman?cmd=[in_cmd]&view=[in_view]&action=1&tab=2&delete_line=$rec->{'ID_banks_movrel'}"><img src="$va{'imgurl'}/$usr{'pref_style'}/b_drop.png" title="Drop" alt="" border="0"></a>--></td>
						<td align='left'>$rec->{'ID_accounts'} $rec->{'ID_accounting'}</td>
						<td align='left'>$rec->{'Name'}</td>
						<td align='right'>|.&format_price($rec->{'AmountPaid'}).qq|</td>
					</tr>\n|;
		}

		if (!$recs){
			$va{'detail_searchresults'} .= qq|
					<tr>
						<td align='center' colspan='3'>|.&trans_txt('search_nomatches').qq|</td>
					</tr>\n|;
		}
	}else{

	}

	if ($movs == 0) {

			## Validamos el tipo de Movimiento
			if (lc($in{'type'}) eq 'credits' and 1 ) {
				
				## Primero verificamos si se va pagar algun bill
				if ($in{'bills'}) {
					
					$string_bills = $in{'bills'};
					if($in{'bills'} =~ m/\|/ ) {
						$string_bills = '';
						my @bills = split /\|/ , $in{'bills'};
						my ($sl_bills_amount, $sl_bills_applies_amount);
						for my $i (0..$#bills) {
							$string_bills .= $bills[$i].',';
						}			
						chop($string_bills);
					}
					
					$sth = &Do_SQL("SELECT SUM(Amount) FROM sl_bills WHERE ID_bills IN (".$string_bills.")");
					$sl_bills_amount += $sth->fetchrow_array;
					$sl_bills_amount += 0 if(!$sl_bills_applies_amount);

					$sth = &Do_SQL("SELECT SUM(Amount) FROM sl_bills_applies WHERE ID_bills IN (".$string_bills.")");
					$sl_bills_applies_amount += $sth->fetchrow_array;
					$sl_bills_applies_amount += 0 if(!$sl_bills_applies_amount);
					if($sl_banks_movements_amount == ($sl_bills_amount - $sl_bills_applies_amount)) {

						## Aqui vamos a cerrar este movimiento bancario
						my @id_bills = split /\|/ , $in{'bills'};
						for my $i (0..$#id_bills) {
							if($id_bills[$i] > 0) {
								&Do_SQL("INSERT INTO sl_banks_movrel SET ID_banks_movements='".&filter_values($in{'id_banks_movements'})."', tablename='bills', tableid=".&filter_values($id_bills[$i]).", Date=CURDATE(), Time=CURTIME(), ID_admin_users=".&filter_values($in{'id_admin_users'}).";");
								$flag=1;

								# actualizar Y se actualizaria el status de sl_bills.Status=’Paid’
								$sth = &Do_SQL("UPDATE sl_bills SET Status='Paid' WHERE ID_bills = '".&filter_values($id_bills[$i])."'");
								$va{'tab_message'} .= &trans_txt(banks_mv_paid_bill)." ".$string_bills."<br>";

								#log
								$in{'db'} = "sl_banks_movements";
								&auth_logging('banks_mv_apply',$in{'id_banks_movements'});

								#log
								$in{'db'} = "sl_bills";
								&auth_logging('bills_paid',$id_bills[$i]);
							}
						}


					}else {
						$va{'tab_message'} .= &trans_txt('banks_mv_amount_no_equals')."<br>";
					}

				}

				if ($in{'id_vendors'} and int($in{'id_vendors'}) > 0) {
					$va{'list_banks_movements'} = '';
					$vendor_name = &load_name('sl_vendors','ID_vendors',$in{'id_vendors'},'CompanyName');

					# se muestran todos los Bills que no esten pagados Status NOT IN (‘Paid’, ‘Void’)
					$va{'list_bills'} .= qq|Bills from Vendor (|.$in{'id_vendors'}.qq|) |.$vendor_name.qq|:
					<input type="hidden" name="id_vendors" id="id_vendors" value="[in_id_customers]">
					<table border="0" cellspacing="0" cellpadding="4" width="[ur_table_width]" class="container_white">
						<tr>
							<td class="menu_bar_title"><input type="checkbox" name="" id="all_checkboxes" value="" onclick="checkall(this)"></td>
							<td class="menu_bar_title">Bill ID</td>
							<td class="menu_bar_title">DueDate</td>
							<td class="menu_bar_title">PO</td>
							<td class="menu_bar_title">Terms</td>
							<td class="menu_bar_title">Amount</td>
						</tr>|;
					$sth = &Do_SQL("SELECT SUM(sl_bills_pos.Amount)Amount, sl_bills.Terms, sl_bills.ID_bills, sl_bills.DueDate, sl_purchaseorders.ID_purchaseorders, sl_purchaseorders.POTerms
						FROM sl_bills 
						INNER JOIN sl_bills_pos USING(ID_bills) 
						INNER JOIN sl_purchaseorders USING(ID_purchaseorders)
						WHERE sl_bills.Type NOT IN('Credit') 
						AND sl_bills.Status NOT IN ('Paid', 'Void') 
						AND sl_purchaseorders.id_vendors='$in{'id_vendors'}'
						GROUP BY ID_bills ORDER BY sl_bills.Date DESC");
					$regs = 0;
					while($rec=$sth->fetchrow_hashref) {
						$regs++;
						$va{'list_bills'} .= qq|
						<tr>
							<td><input type="checkbox" name="bills" value="|.$rec->{'ID_bills'}.qq|" class="chb_bills"></td>
							<td><a href="/cgi-bin/mod/[ur_application]/dbman?cmd=mer_bills&view=|.$rec->{'ID_bills'}.qq|&second_conn=0">|.$rec->{'ID_bills'}.qq|</a></td>
							<td>|.$rec->{'DueDate'}.qq|</td>
							<td>|.$rec->{'ID_purchaseorders'}.qq|</td>
							<td>|.$rec->{'Terms'}.qq|</td>
							<td>|.&format_price($rec->{'Amount'}).qq|</td>
						</tr>|;
					}
					
					if ($regs == 0) {
						$va{'list_bills'} .= qq|
						<tr>
							<td colspan='5' align="center">|.&trans_txt('search_nomatches').qq|</td>
						</tr>|;
					}

					$va{'list_bills'} .= qq|
					</table>|;

					$va{'display_accounts'} = 'display:none';
				}else {
					# se pregunta por el Vendor
					$va{'searchresults'} = qq|
					<tr>
						<td colspan='6' align='left'>Vendor :
						<input type="text" name="id_vendors" id="id_vendors" value="[in_id_customers]" size="20" onFocus='focusOn( this )' onBlur='focusOff( this )'>
						<a class="scroll" href="#tabs" id="customers" onClick="popup_show('search_vendors', 'item_drag1', 'popup_exit1', 'element-right', -1, -1,'tabs');"><img src="/sitimages//default/icsearchsmall.gif" border="0"></a> |.$vendor_name.qq|
						<input type="submit" value="Continue" class="button">
						</td>
					</tr>\n|;
				}

			}elsif (lc($in{'type'}) eq 'debits') {		
				if ($in{'id_customers'} and int($in{'id_customers'}) > 0) {

					## Antes que todo hay que agregar una validacion. La suma de los Montos Assigned tiene que ser la misma del Amount del movimiento
					my $validation = 0;
					my $total_assigned = $in{'payments'};

					if ($in{'payments'} =~ m/\|/) {
						$total_assigned = 0;
						my @amount = split /\|/, $in{'payments'};
						for my $i (0..$#amount) {
							if ($amount[$i] > 0) {
								$total_assigned += $amount[$i];
							}
						}
					}
					#cgierr("Cantidad movimientos: $sl_banks_movements_amount, Total asignado: $total_assigned");
					if ($sl_banks_movements_amount == $total_assigned) {
						my $credit_validation = 1;
						
						my @add_amounts = split('\|', $in{'add_amount'});
						my @add_type = split('\|', $in{'add_type'});
						my @add_id_services = split('\|', $in{'add_id_services'});
						my @add_id_orders = split('\|', $in{'add_id_orders'});
						
						for my $i (0..$#add_amounts) {
									my $in_add_type = $add_type[$i];
									my $in_add_id_orders = $add_id_orders[$i];
									my $in_add_id_services = $add_id_services[$i];
									my $in_add_amount = $add_amounts[$i];
						
							## En caso que existan Cargos/Abonos, estos deben de considerarse para el monto del pago.					
							if ($in_add_type ne '' and $in_add_id_orders ne '' and $in_add_id_services ne '' and $in_add_amount ne '' and $in{'add_amount'} >= 0) {
		
								my $id_services = 600000000 + int($in_add_id_services);
								my $id_orders = int($in_add_id_orders);
								$in{'add_amount'} = &filter_values($in_add_amount);
								my $saleprice = $in{'add_amount'};
		
								$saleprice = $saleprice * -1 if(lc($in_add_type) eq 'credit');
								$tax_percent = &load_name('sl_services','ID_services',$id_services,'Tax');
								$tax_percent = 0 if(!$tax_percent);
								$tax = $saleprice * $tax_percent;
								$tax = 0 if(!$tax);
								$sth = &Do_SQL("SELECT MAX(ID_products) FROM sl_orders_products WHERE ID_orders='$id_orders' AND ID_products > 600000000");
								$next = $sth->fetchrow;
								$next = (!$next)? 601000000: $next + 1;
								$total_saleprice = $saleprice + $tax;
								$total_saleprice_payment = $in{'add_amount'} + $tax;
		
								if (lc($in_add_type) eq 'credit') {
									# Obtengo el total de la orden
									$total_order = &get_order_amountdue($id_orders);
									$credit_validation = (($total_order - $in{'add_amount'}) >= 0)? 1:0;
								}
		
								## Validar que no se aplique un credit donde el Amount de la orden quede negativo
								if ($credit_validation) {
									# Agrego el servicio a la orden
									my ($sth) = &Do_SQL("INSERT INTO `sl_orders_products` (`ID_orders_products`, `ID_products`, `ID_orders`, `ID_packinglist`, `Related_ID_products`, `Quantity`, `SalePrice`, `Shipping`, `Cost`, `Tax`, `Tax_percent`, `Discount`, `FP`, `SerialNumber`, `ShpDate`, `Tracking`, `ShpProvider`, `ShpTax`, `ShpTax_percent`, `PostedDate`, `Upsell`, `Status`, `Date`, `Time`, `ID_admin_users`)
									VALUES (NULL, $next, $id_orders, 0, $id_services, 1, $saleprice, 0.0, 0.0, $tax, $tax_percent , 0.00, 1, NULL, NULL, NULL, NULL, 0.000, 0.0000, NULL, 'Yes', 'Active', CURDATE(), CURTIME(), ".$usr{'id_admin_users'}.")");
									$id_orders_products_new = $sth->{'mysql_insertid'};
		
									#log
									$in{'db'} = "sl_orders";
									&auth_logging('orders_products_added',$id_orders);
		
									## Recalculo el total de la orden
									my ($sth) = &Do_SQL("SELECT * FROM sl_orders_products WHERE ID_orders='$id_orders' AND (Status='Active');");
									while ($tmp = $sth->fetchrow_hashref){
										$in{'orderqty'} += $tmp->{'Quantity'};
										$in{'ordernet'} += $tmp->{'SalePrice'};
										$in{'ordershp'} += $tmp->{'Shipping'};
									}
									$in{'shp_zip'} = &load_name('sl_orders','ID_orders',$id_orders,'shp_Zip') if(!$in{'shp_zip'});
									$in{'shp_state'} = &load_name('sl_orders','ID_orders',$id_orders,'shp_State') if(!$in{'shp_state'});
									$in{'ordertax'} = &calculate_taxes($in{'shp_zip'},$in{'shp_state'},$in{'shp_city'},$id_orders);
									$in{'orderdisc'} = &load_name('sl_orders','ID_orders',$id_orders,'OrderDisc') if(!$in{'orderdisc'});
									
									my ($sth) = &Do_SQL("SELECT ifnull((SELECT SUM(Amount) FROM sl_orders_payments WHERE ID_orders='$id_orders' AND Status<>'Cancelled' AND (captured !='Yes' OR captured IS NULL )),0)as Total;");							
									$total_order = $sth->fetchrow();
									$in{'ordershp'} = $total_order-$in{'ordernet'}+$in{'orderdisc'}-$in{'ordertax'}*($in{'ordernet'}-$in{'orderdisc'});
		
									my ($sth) = &Do_SQL("UPDATE sl_orders SET OrderQty='$in{'orderqty'}',OrderShp='$in{'ordershp'}',OrderTax='$in{'ordertax'}',OrderNet='$in{'ordernet'}' WHERE ID_orders='$id_orders'");
									
									#log
									$in{'db'} = "sl_orders";
									&auth_logging('opr_orders_totals',$id_orders);
									# &cgierr(.'<-Total orden');
									$total = $total_order + $total_saleprice;
									&Do_SQL("UPDATE sl_orders_payments SET Amount=$total WHERE ID_orders=$id_orders AND Status NOT IN ('Cancelled') LIMIT 1");
		
									#log
									$in{'db'} = "sl_orders";
									&auth_logging('orders_payments_updated',$id_orders);
		
									$va{'tab_message'} .= &trans_txt('banks_mv_service_added_order').' '.$id_orders."<br>";
									
								}else{
									$va{'tab_message'} .= &trans_txt('banks_mv_service_notadded_order').' '.$id_orders."<br>";
								}
		
							}
						
						
						}
						
						
						
						
						## Tenemos que recorrer todos los valores posibles de $in{'payments'}
						$id_orders_payments = $in{'id_orders_payments'};
						$id_orders = $in{'id_orders'};
						$payments = &clean_number($in{'payments'});
						if($in{'id_orders_payments'} ne '' and $in{'id_orders'} ne '' and $in{'payments'} ne '' and $credit_validation) {

							my @id_orders_payments = split /\|/, $in{'id_orders_payments'};
							my @id_orders = split /\|/, $in{'id_orders'};
							my @payments = split /\|/, $in{'payments'};
							for my $i (0..$#payments) {
								if (&clean_number($payments[$i]) > 0) {
									$id_orders_payments = $id_orders_payments[$i];
									$id_orders = $id_orders[$i];
									$payments = &clean_number($payments[$i]);

									my ($sth) = &Do_SQL("SELECT SUM(Amount) FROM sl_orders_payments WHERE ID_orders_payments=$id_orders_payments AND ID_orders=$id_orders AND Status<>'Cancelled';");
									$total = $sth->fetchrow();

									if ($payments == $total) {
										
										&Do_SQL("UPDATE sl_orders_payments SET Amount=$total, captured='Yes', CapDate=CURDATE(), Status='Approved' WHERE ID_orders_payments=$id_orders_payments AND ID_orders=$id_orders AND Status NOT IN ('Cancelled') LIMIT 1");

										#log
										$in{'db'} = "sl_orders";
										&auth_logging('orders_payments_updated',$id_orders);

										$va{'tab_message'} .= &trans_txt('banks_mv_paid_order').' '.$id_orders."<br>";

										## Aqui vamos a cerrar este movimiento bancario
										&Do_SQL("INSERT INTO sl_banks_movrel SET ID_banks_movements=".$in{'id_banks_movements'}.", tablename='orders_payments', tableid=".$id_orders_payments.", Date=CURDATE(), Time=CURTIME(), ID_admin_users=".$in{'id_admin_users'}.";");

										#log
										$in{'db'} = "sl_banks_movements";
										&auth_logging('banks_mv_apply',$in{'id_banks_movements'});
										
										$flag=1;

									}elsif($payments < $total) {

										# &cgierr($sl_banks_movements_amount.'='.$total.'++'.$total_saleprice.'---'.$total_saleprice_payment.'--->'.$total_order.'<-->');

										my $tmp_sth = &Do_SQL("SELECT ID_orders, Type, PmtField1, PmtField2, PmtField3, PmtField4, PmtField5, PmtField6, PmtField7, PmtField8, PmtField9, Reason FROM sl_orders_payments WHERE ID_orders=$id_orders AND (Captured != 'Yes' OR Captured IS NULL) AND Status NOT IN ('Cancelled') ORDER BY Date DESC LIMIT 1");
										my ($tmp_id_orders,$tmp_type,$tmp_pmtfield1,$tmp_pmtfield2,$tmp_pmtfield3,$tmp_pmtfield4,$tmp_pmtfield5,$tmp_pmtfield6,$tmp_pmtfield7,$tmp_pmtfield8,$tmp_pmtfield9,$tmp_reason) = $tmp_sth->fetchrow_array();


										my $sth = &Do_SQL("INSERT INTO sl_orders_payments (ID_orders_payments, ID_orders, Type, PmtField1, PmtField2, PmtField3, PmtField4, PmtField5, PmtField6, PmtField7, PmtField8, PmtField9, Amount, Reason, Paymentdate,  Captured, CapDate, PostedDate, Status, Date, Time, ID_admin_users) VALUES
										(NULL, '$tmp_id_orders', '$tmp_type', '$tmp_pmtfield1', '$tmp_pmtfield2', '$tmp_pmtfield3', '$tmp_pmtfield4', '$tmp_pmtfield5', '$tmp_pmtfield6', '$tmp_pmtfield7', '$tmp_pmtfield8', '$tmp_pmtfield9',  ".$payments.", '$tmp_reason', curdate(), 'Yes', curdate(),  NULL, 'Approved', curdate(), curtime(), ".$usr{'id_admin_users'}.");");
										$id_orders_payments_new = $sth->{'mysql_insertid'};

										$va{'tab_message'} .= &trans_txt('banks_mv_payment_added_order').' '.$id_orders."<br>";

										#log
										$in{'db'} = "sl_orders";
										&auth_logging('orders_payments_added',$id_orders);

										# Revisar esta parte 
										$banks_movements_amount = 0;
										my $diference = $total - $payments;
										# el estatus cambia a Credit
										&Do_SQL("UPDATE sl_orders_payments SET Amount=$diference WHERE ID_orders_payments=$id_orders_payments AND ID_orders=$id_orders AND (Captured != 'Yes' OR Captured IS NULL) AND Status NOT IN ('Cancelled') LIMIT 1");

										#log
										$in{'db'} = "sl_orders";
										&auth_logging('orders_payments_updated',$id_orders);

										## Aqui vamos a cerrar este movimiento bancario
										&Do_SQL("INSERT INTO sl_banks_movrel SET ID_banks_movements=".$in{'id_banks_movements'}.", tablename='orders_payments', tableid=".$id_orders_payments_new.", Date=CURDATE(), Time=CURTIME(), ID_admin_users=".$in{'id_admin_users'}.";");
										
										#log
										$in{'db'} = "sl_banks_movements";
										&auth_logging('banks_movements_apply',$in{'id_banks_movements'});
										
										$flag=1;
									}
								}
							}
						}

					}elsif($in{'payments'} ne '') {
						$va{'tab_message'} .= &trans_txt('banks_mv_amount_no_equals')."<br>";
					}

					my $sth_customer = &Do_SQL("SELECT * FROM sl_customers WHERE ID_customers=".$in{'id_customers'});
					$rec_customer=$sth_customer->fetchrow_hashref;

					$customer_name = $rec_customer->{'company_name'};
					$customer_name = $rec_customer->{'FirstName'}.' '.$rec_customer->{'LastName1'}.' '.$rec_customer->{'LastName2'} if($customer_name eq '');

					$va{'list_banks_movements'} = '';
					# se listan todos los pagos (sl_orders_payments) que no esten pagados (Captured = ‘No’)
					# Order ID | Paymentdate | Amount | Assigned (input text)

					$va{'list_payments'} .= qq|Pending Payments from Customer (|.$in{'id_customers'}.qq|) |.$customer_name.qq|:
					<input type="hidden" name="id_customers" value="[in_id_customers]">
					<table border="0" cellspacing="0" cellpadding="4" width="[ur_table_width]" class="container_white">
						<tr>
							<td class="menu_bar_title">Order ID</td>
							<td class="menu_bar_title">Paymentdate</td>
							<td class="menu_bar_title">Amount Due</td>
							<td class="menu_bar_title">Assigned</td>
						</tr>|;

					$sth = &Do_SQL("SELECT DISTINCT cu_invoices.ID_invoices, cu_invoices_lines.ID_orders, sl_orders_payments.Paymentdate
						/* , (sl_orders_payments.Amount)Amount */
						, sl_orders_payments.ID_orders_payments
						, (SELECT ifnull(SUM(Amount),0)Amount FROM sl_orders_payments WHERE ID_orders=sl_orders.ID_orders AND (sl_orders_payments.Captured != 'Yes' OR sl_orders_payments.Captured IS NULL) AND sl_orders_payments.Status IN ('Approved'))Amount
						FROM sl_orders
						INNER JOIN sl_orders_payments USING(ID_orders)
						INNER JOIN cu_invoices_lines USING(ID_orders) 
						INNER JOIN cu_invoices USING(ID_invoices) 
						WHERE (sl_orders_payments.Captured != 'Yes' OR sl_orders_payments.Captured IS NULL)
						AND sl_orders.ID_customers=$in{'id_customers'}
						AND sl_orders_payments.Status IN ('Approved')
						AND sl_orders.Status NOT IN ('Shipped','Cancelled','Void','System Error')
						AND cu_invoices.Status = '$invoice_status'
						ORDER BY sl_orders_payments.Date DESC");
					$select_orders = '';
					
					$regs=0;
					my @paymentsval = split /\|/, $in{'payments'};			
					while($rec=$sth->fetchrow_hashref) {
						$select_orders .= qq|<option value="|.$rec->{'ID_orders'}.qq|">|.$rec->{'ID_orders'}.qq| - |.$rec->{'ID_invoices'}.qq|</option>|;

						if ($in{'payments'} =~ m/\|/) {
							$va{'list_payments'} .= qq|
						<tr>
							<td><a href="/cgi-bin/mod/[ur_application]/dbman?cmd=opr_orders&view=|.$rec->{'ID_orders'}.qq|&second_conn=0">|.$rec->{'ID_orders'}.qq|</a></td>
							<td>|.$rec->{'Paymentdate'}.qq|</td>
							<td>|.&format_price($rec->{'Amount'}).qq|</td>
							<td>
								<input type="hidden" name="id_orders_payments" value="|.$rec->{'ID_orders_payments'}.qq|"> 
								<input type="hidden" name="id_orders" value="|.$rec->{'ID_orders'}.qq|" id="id_orders">
								<input type="text" name="payments" value="|.$paymentsval[$regs].qq|">|;
							$va{'list_payments'} .= qq|<span class="smallfieldterr">|.&trans_txt('invalid').qq|</span>| if($paymentsval[$regs] ne '');
							$va{'list_payments'} .= qq|
							</td>
						</tr>|;
						}else {
							$va{'list_payments'} .= qq|
						<tr>
							<td><a href="/cgi-bin/mod/[ur_application]/dbman?cmd=opr_orders&view=|.$rec->{'ID_orders'}.qq|&second_conn=0">|.$rec->{'ID_orders'}.qq|</a></td>
							<td>|.$rec->{'Paymentdate'}.qq|</td>
							<td>|.&format_price($rec->{'Amount'}).qq|</td>
							<td>
								<input type="hidden" name="id_orders_payments" value="|.$rec->{'ID_orders_payments'}.qq|"> 
								<input type="hidden" name="id_orders" value="|.$rec->{'ID_orders'}.qq|" id="id_orders">
								<input type="text" name="payments" value="[in_payments]">
							</td>
						</tr>|;
						}
						$regs++;
					}

					if ($regs == 0) {
						$va{'list_payments'} .= qq|
						<tr>
							<td colspan='5' align="center">|.&trans_txt('search_nomatches').qq|</td>
						</tr>|;
					}

					$va{'list_payments'} .= qq|
					</table>|;

					## Select de servicios
					my $select_services = &build_select_services;
					## Agregar cargos y abonos
					$va{'form_add'} .= qq|Add Services :
					<table border="0" cellspacing="0" cellpadding="4" width="[ur_table_width]" class="container_white" id="services_table" name="services_table">
						<tr>
							<td class="menu_bar_title">Type</td>
							<td class="menu_bar_title">Order ID-Invoice ID</td>
							<td class="menu_bar_title">Services</td>
							<td class="menu_bar_title">Amount</td>
						</tr>
						<tr>
							<td>
								<select name="add_type" id="add_type">
									<option value="Debit">Debit</option>
									<option value="Credit">Credit</option>
								</select>
							</td>
							<td>
								<select name="add_id_orders" id="add_id_orders">
									<option value="">---</option>
									|.$select_orders.qq|
								</select>
							</td>
							<td>
								<select name="add_id_services" id="add_id_services">
									<option value="">---</option>
									|.$select_services.qq|
								</select>
							</td>
							<td>
								<input type="text" name="add_amount" value="" id="add_amount">
							</td>
						</tr>|;

					## si vienen valores en el submit los recorremos
					$va{'form_add'} .= qq|
						<tr>
							<td>
								<input type="hidden" name="type" value="">
							</td>
							<td>
								<input type="hidden" name="id_orders" value="">
							</td>
							<td>
								<input type="hidden" name="id_services" value="">
							</td>
							<td>
								<input type="hidden" name="amount" value="">
							</td>
						</tr>|;

					$va{'form_add'} .= qq|
					</table>|;
					$va{'form_add'} .= qq|<input type="button" value="Add Service" id="button_replicate" name="button_replicate" onclick="add_service();" style="margin-top: 10px;" />
			<input type="button" value="Delete Service" id="button_delete" name="button_delete" onclick="delete_service();" style="margin-top: 10px;"/>|;
					$va{'display_accounts'} = 'display:none';
				}else {
					# se pregunta por el Customer
					$va{'searchresults'} = qq|
					<tr>
						<td colspan='6' align='left'>Customer :
						<input type="text" name="id_customers" value="$in{'id_customers'}" size="20" onFocus='focusOn( this )' onBlur='focusOff( this )'>
						<a href="#tabs" id="id_customers" onClick="popup_show('search_cust', 'item_drag', 'popup_exiti', 'element-right', -1, -1,'tabs');"><img src="/sitimages//default/icsearchsmall.gif" border="0"></a> |.$customer_name.qq|
						<input type="submit" value="Continue" class="button">
						</td>
					</tr>\n|;
				}
			}
	}
	
	## Despues de procesar Validamos nuevamente si este movimiento esta aplicado
	my $sth=&Do_SQL("SELECT COUNT(*)movs FROM sl_banks_movrel WHERE ID_banks_movements='".$in{'id_banks_movements'}."';");
	my $movs = $sth->fetchrow_array;
	if ($movs > 0) {
		######################################################################################################################################
		my $sth=&Do_SQL("SELECT tablename, tableid FROM sl_banks_movrel WHERE ID_banks_movements=".$in{'id_banks_movements'}." GROUP BY tablename, tableid;");
		$va{'list_banks_movements'} = qq|<table border="0" cellspacing="0" cellpadding="4" width="[ur_table_width]" class="container_white" id="services_table" name="services_table">|;
		$va{'list_banks_movements'} .= '[table_titles]';
		my %header = ();
		
		while($recs_bm=$sth->fetchrow_hashref) {

			if (lc($recs_bm->{'tablename'}) eq 'bills') {
				$header{ 'type' } = 'bills';
				my $sth_bills=&Do_SQL("SELECT * FROM sl_bills INNER JOIN sl_banks_movrel ON sl_banks_movrel.tablename='bills' AND sl_banks_movrel.tableid=ID_bills WHERE ID_bills='".$recs_bm->{'tableid'}."' AND ID_banks_movements='".$in{'id_banks_movements'}."';");
				while($recs_bills=$sth_bills->fetchrow_hashref) {
					my $vendor_name = &load_name('sl_vendors','ID_vendors',$recs_bills->{'ID_vendors'},'CompanyName');
					$va{'list_banks_movements'}.= qq|
					<tr>
						<td align="left"><a href="/cgi-bin/mod/[ur_application]/dbman?cmd=mer_bills&view=|.$recs_bills->{'ID_bills'}.qq|">$recs_bills->{'ID_bills'}</a></td>
						<td align="left"><a href="/cgi-bin/mod/[ur_application]/dbman?cmd=mer_vendors&view=|.$recs_bills->{'ID_vendors'}.qq|">($recs_bills->{'ID_vendors'}) $vendor_name</a></td>
						<td align="left">$recs_bills->{'Type'}</td>
						<td align="left">$recs_bills->{'BillDate'}</td>
						<td align="left">$recs_bills->{'DueDate'}</td>
						<td align="left">$recs_bills->{'Currency'}</td>
						<!--td align="right">|.&format_price($recs_bills->{'Amount'}).qq|</td-->
						<td align="right">|.&format_price($recs_bills->{'AmountPaid'}).qq|</td>
						<td align="left">$recs_bills->{'Status'}</td>
					</tr>|;
				}
				#my $sth_deb_bills=&Do_SQL("SELECT COUNT(*) FROM sl_bills WHERE ID_bills=".$rec_movs->{'tableid'}." AND type='Debit';");
					
				
			} elsif (lc($recs_bm->{'tablename'}) eq 'orders_payments') {

				$header{ 'type' } = 'orders_payments';
				my $sth_pay=&Do_SQL("SELECT * FROM sl_orders INNER JOIN sl_orders_payments USING(ID_orders) WHERE ID_orders_payments=".$recs_bm->{'tableid'}.";");

				
				while($rec_pay=$sth_pay->fetchrow_hashref) {
					my $sth_customer = &Do_SQL("SELECT * FROM sl_customers WHERE ID_customers=".$rec_pay->{'ID_customers'});
					$rec_customer=$sth_customer->fetchrow_hashref;

					$customer_name = $rec_customer->{'company_name'};
					$customer_name = $rec_customer->{'FirstName'}.' '.$rec_customer->{'LastName1'}.' '.$rec_customer->{'LastName2'} if($customer_name eq '');

					$va{'list_banks_movements'} .= qq|
					<tr>
						<td><a href="/cgi-bin/mod/[ur_application]/dbman?cmd=opr_orders&view=|.$rec_pay->{'ID_orders'}.qq|">|.$rec_pay->{'ID_orders'}.qq|</a></td>
						<td><a href="/cgi-bin/mod/[ur_application]/dbman?cmd=opr_customers&view=|.$rec_pay->{'ID_customers'}.qq|">(|.$rec_pay->{'ID_customers'}.qq|) $customer_name</a></td>				
						<td>|.$rec_pay->{'Ptype'}.qq|</td>
						<td>|.$rec_pay->{'CapDate'}.qq|</td>
						<td align="right">|.&format_price($rec_pay->{'Amount'}).qq|</td>
					</tr>|;
				}

			}elsif (lc($recs_bm->{'tablename'}) eq 'customers_advances') {

				$header{ 'type' } = 'orders_payments';
				my $sth_pay=&Do_SQL("SELECT * FROM sl_customers_advances WHERE ID_customers_advances = ".$recs_bm->{'tableid'}.";");
				my $rec_pay=$sth_pay->fetchrow_hashref();

				my $sth_customer = &Do_SQL("SELECT * FROM sl_customers WHERE ID_customers=".$rec_pay->{'ID_customers'});
				$rec_customer = $sth_customer->fetchrow_hashref;

				$customer_name = $rec_customer->{'company_name'};
				$customer_name = $rec_customer->{'FirstName'}.' '.$rec_customer->{'LastName1'}.' '.$rec_customer->{'LastName2'} if($customer_name eq '');

				$va{'list_banks_movements'} .= qq|
				<tr>
					<td><a href="/cgi-bin/mod/[ur_application]/dbman?cmd=opr_customers_advances&view=|.$rec_pay->{'ID_customers_advances'}.qq|">|.$rec_pay->{'ID_customers_advances'}.qq|</a></td>
					<td><a href="/cgi-bin/mod/[ur_application]/dbman?cmd=opr_customers&view=|.$rec_pay->{'ID_customers'}.qq|">(|.$rec_pay->{'ID_customers'}.qq|) $customer_name</a></td>				
					<td>N/A</td>
					<td>|.$rec_pay->{'Date'}.qq|</td>
					<td align="right">|.&format_price($rec_pay->{'Amount'}).qq|</td>
				</tr>|;

			} else {
				
				$header{ 'type' } = 'other';
				my $sth_pay=&Do_SQL("SELECT sl_bills.ID_bills, sl_purchaseorders.ID_vendors, ID_purchaseorders, sl_bills_pos.Amount POAmount, sl_bills_pos.Amount BAmount, sl_bills.Type
						, ifnull((SELECT SUM(Total) FROM sl_purchaseorders_items WHERE ID_purchaseorders = sl_purchaseorders.ID_purchaseorders),0)as Total
						, ifnull((SELECT SUM(sl_bills_pos.Amount) FROM sl_bills INNER JOIN sl_bills_pos USING(ID_bills) WHERE ID_purchaseorders = sl_purchaseorders.ID_purchaseorders AND sl_bills.Status = 'Paid'),0)as TotalPaid
						, ifnull((SELECT SUM(Total) FROM sl_purchaseorders_adj WHERE ID_purchaseorders = sl_purchaseorders.ID_purchaseorders),0)as TotalAdj
						FROM sl_bills INNER JOIN sl_bills_pos USING(ID_bills) 
						INNER JOIN sl_purchaseorders USING(ID_purchaseorders) 
						WHERE ID_bills=".$recs_bm->{'tableid'}.";");
						
					my $rec_pay;
					while($rec_pay=$sth_pay->fetchrow_hashref) {
						# monto total del PO.
						($in{'amount_po'}) = $rec_pay->{'Total'};
						
						# monto total de adjustments.
						($in{'amount_po_adj'}) = $rec_pay->{'TotalAdj'};
						
						# monto total del PO apliacando ajustes
						$in{'amount_po'} = $in{'amount_po'} + $in{'amount_po_adj'};
	
						# monto total pagado}
						($in{'amount_billsp'}) = $rec_pay->{'TotalPaid'};
	
						# Monto total del PO - El monto que se ha pagado
						$va{'total_due'} = ($in{'amount_po'} - $in{'amount_billsp'});
	
						$regs++;
						my $vendor_name = &load_name('sl_vendors','ID_vendors',$rec_pay->{'ID_vendors'},'CompanyName');
						my $amount_due = ($rec_pay->{'Total'}-$rec_pay->{'BAmount'});
						$va{'list_banks_movements'} .= qq|
						<tr>
							<td><a href="/cgi-bin/mod/[ur_application]/dbman?cmd=mer_vendors&view=|.$rec_pay->{'ID_vendors'}.qq|">(|.$rec_pay->{'ID_vendors'}.qq|) |.$vendor_name.qq|</a></td>
							<td><a href="/cgi-bin/mod/[ur_application]/dbman?cmd=mer_po&view=|.$rec_pay->{'ID_purchaseorders'}.qq|">|.$rec_pay->{'ID_purchaseorders'}.qq|</a></td>				
							<td align="center"><a href="/cgi-bin/mod/[ur_application]/dbman?cmd=mer_bills&view=|.$rec_pay->{'ID_bills'}.qq|">(|.$rec_pay->{'ID_bills'}.qq|) |.$rec_pay->{'Type'}.qq|</td>
							<td align="right">|.&format_price($rec_pay->{'BAmount'}).qq|</td>
							<td align="right">|.&format_price($rec_pay->{'Total'}).qq|</td>
							<td align="right">|.&format_price($va{'total_due'}).qq|</td>
						</tr>|;
					}
			}
			
		}
		
		my $table_titles = '';
		if ($header{ 'type' } eq 'bills') {
			$table_titles = qq|
			<tr>
				<td class="menu_bar_title" align="left">Bill ID</td>
				<td class="menu_bar_title" align="left">Vendor</td>
				<td class="menu_bar_title" align="left">Bill Type</td>
				<td class="menu_bar_title" align="left">Bill Date</td>
				<td class="menu_bar_title" align="left">Due Date</td>
				<td class="menu_bar_title" align="left">Currency</td>
				<td class="menu_bar_title" align="left">Amount Paid</td>
				<td class="menu_bar_title" align="left">Status</td>
			</tr>|;
			$va{'display_accounts'} = 'display:none';
		} elsif ($header{ 'type' } eq 'orders_payments'){
			$table_titles = qq|
					<tr>
						<td class="menu_bar_title">ID Order</td>
						<td class="menu_bar_title">Customer</td>
						<td class="menu_bar_title">Type Order</td>
						<td class="menu_bar_title">Cap Date</td>
						<td class="menu_bar_title">Amount</td>
					</tr>|;
			$va{'display_accounts'} = 'display:none';
		} else {
			$table_titles = qq|
						<tr>
							<td class="menu_bar_title" align="center">Vendor</td>
							<td class="menu_bar_title" align="center">PO</td>
							<td class="menu_bar_title" align="center">Bill Type</td>
							<td class="menu_bar_title" align="center">Bill Amount</td>
							<td class="menu_bar_title" align="center">PO Amount</td>
							<td class="menu_bar_title" align="center">Amount Due</td>
						</tr>|;
		}
		my $str_to_replace = '\[table_titles\]';
		$va{'list_banks_movements'} =~ s/$str_to_replace/$table_titles/g;
		
		if ($movs == 0) {
			$va{'list_banks_movements'} .= qq|
			<tr>
				<td colspan='5' align="center">|.&trans_txt('search_nomatches').qq|</td>
			</tr>|;
		}
		
		$va{'list_banks_movements'} .= '</table>';
		######################################################################################################################################
		
		
		

	}

	if ($flag) {
		$va{'searchresults'} = '';
		$va{'form_add'} = '';
		$va{'list_payments'} = '';
		$va{'list_bills'} = '';		
	}

	$va{'button'} = '' if($flag or !$in{'id_customers'} and !$in{'id_vendors'});
}

sub clean_number {
	my ($number) = @_;
	$number =~ s/\$//g;
	$number =~ s/,//g;
	$number =~ s/ //g;
	$number =~ s/^(\d\.)//g;

	return $number;
}

1;