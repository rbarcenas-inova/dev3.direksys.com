#########################################################
##		MERCHANDISING : BILLS
##########################################################

sub view_mer_bills {
# --------------------------------------------------------
		
	if ($in{'chgstatusto'} and &check_permissions('mer_bills_change_status','','')) {
		my ($sth)	= &Do_SQL("UPDATE sl_bills SET Status='".&filter_values($in{'chgstatusto'})."' WHERE ID_bills='$in{'id_bills'}' LIMIT 1;");
		&auth_logging(&trans_txt('bills_change_status').' From: '.$in{'status'}.' To: '.$in{'chgstatusto'},$in{'id_bills'});
		$in{'status'} = $in{'chgstatusto'};
		&bills_to_void($in{'id_bills'}) if ($in{'chgstatusto'} eq 'Void');
	}
	
	if (!&check_permissions('mer_bills_change_status','','')) {
		$va{'chgstatus'} = qq| <span class="smallfieldterr">|.&trans_txt('unauth_action').qq|</span>|;
	} else {
		my (@ary) = &load_enum_toarray('sl_bills','Status');
		for (0..$#ary) {
			if ($ary[$_] ne $in{'status'}){
				$va{'chgstatus'} .= qq| <a href="/cgi-bin/mod/$usr{'application'}/dbman?cmd=mer_bills&view=$in{'id_bills'}&chgstatusto=$ary[$_]">$ary[$_]</a> &nbsp;&nbsp;&nbsp;|;
			}
		}
	}	
	
	
	if ($in{'to_process'}){
		# If it is an expense bill must be validated before
		my ($sth) = &Do_SQL("SELECT sl_bills.Amount BillAmount, SUM(sl_bills_expenses.Amount)Amount, COUNT(*) AS nlines FROM sl_bills INNER JOIN sl_bills_expenses USING(ID_bills) WHERE ID_bills='$in{'id_bills'}';");
		my ($amount_bill, $amount_lines, $no_lines) = $sth->fetchrow_array();
				
		if ($in{'type'} eq 'Bill' and $no_lines > 0 and ($amount_lines <= 0 or $amount_bill != $amount_lines)){
			$va{'message'} = &trans_txt('bills_amounts_not_match');
		}else{

			my ($t_amount) =  $in{'amount'};
			$in{'amount'} = $in{'amount'}*$in{'currency_exchange'} if ($in{'currency'} ne $cfg{'acc_default_currency'} and $in{'currency_exchange'});

			if ($cfg{'bills_autoproc_'.lc($in{'type'})} and $t_amount > $cfg{'bills_autoproc_'.lc($in{'type'})}  and $in{'status'} eq 'New'){
				if (&check_permissions('mer_bills_toprocessed','','')){
					my ($sth) = &Do_SQL("UPDATE sl_bills SET Status='Pending' WHERE ID_bills='$in{'id_bills'}';");
					
					&auth_logging('mer_bills_topending',$in{'id_bills'});
					$va{'message'} = &trans_txt('mer_bills_topending');
					$in{'status'} = 'Pending';
				}else{
					$va{'message'} = &trans_txt('unauth_action');
				}
			}elsif ($cfg{'bills_autoproc_'.lc($in{'type'})} and $t_amount > $cfg{'bills_autoproc_'.lc($in{'type'})}  and $in{'status'} eq 'Pending'){
				if (&check_permissions('mer_bills_pendauth','','')){

					###########################
					###########################
					####
					#### Pasa a Processed
					####
					###########################
					###########################

					&bills_to_processed($in{'id_bills'},$in{'currency_exchange'});
				}else{
					$va{'message'} = &trans_txt('unauth_action');
				}
			}elsif (&check_permissions('mer_bills_toprocessed','','')){

				###########################
				###########################
				####
				#### Pasa a Processed
				####
				###########################
				###########################

				&bills_to_processed($in{'id_bills'},$in{'currency_exchange'});	
			}else{
				$va{'message'} = &trans_txt('unauth_action');
			}
		}
	}

	if ($in{'cancel_payment'} and &check_permissions('mer_bills_partial_cancellation_payments','','')){

			# buscar todos los payments y duplicarlos con montos negativos(Debits)
			my ($sth) = &Do_SQL("SELECT Amount, ID_banks_movements, ID_banks_movrel
			FROM sl_banks_movrel INNER JOIN sl_banks_movements USING(ID_banks_movements) 
			WHERE tablename='bills' AND tableid='".&filter_values($in{'view'})."' AND ID_banks_movements='".$in{'cancel_payment'}."' AND Amount > 0
			AND (SELECT count(*) FROM sl_banks_movements_notes WHERE Type='Cancel' AND ID_banks_movements=sl_banks_movements.ID_banks_movements) = 0;");
			while ($rec = $sth->fetchrow_hashref){
				if (!$rec->{'duplicated'}) {
					my ($sth2) = &Do_SQL("INSERT INTO sl_banks_movements (ID_banks,  Type,  BankDate,  ConsDate,  Amount,  currency_exchange,  RefNum,  Memo,  Date,  Time,  ID_admin_users )
					(SELECT  ID_banks,  'Debits',  curdate(),  ConsDate,  Amount,  currency_exchange,  RefNum,  'Cancel Bank Movement',  CURDATE(),  CURTIME(),  $usr{'id_admin_users'} FROM sl_banks_movements WHERE ID_banks_movements = '".$rec->{'ID_banks_movements'}."');");
					$id_banks_movements = $sth2->{'mysql_insertid'};

					my ($sth) = &Do_SQL("INSERT INTO sl_banks_movrel SET ID_banks_movements = '$id_banks_movements', tablename = 'bills', tableid = '".$in{'id_bills'}."', DATE = CURDATE(), TIME = CURTIME(), ID_admin_users='$usr{'id_admin_users'}'");

					# La nota me indicara si este movimineto esta cancelado
					my ($sth) = &Do_SQL("INSERT INTO sl_banks_movements_notes (ID_banks_movements_notes,  ID_banks_movements,  Notes,  Type,  Date,  Time,  ID_admin_users )
					VALUES(NULL, $in{'cancel_payment'}, 'This movement has been cancelled.', 'Cancel', CURDATE(), CURTIME(),$usr{'id_admin_users'});");
					
					# pasar el status del bill a New o Partly Paid o el que le corresponda
					# calcular el due y sobre eso definirlo

					$sql_string = "SELECT Amount, IFNULL(Amount - (SELECT IFNULL(SUM(Amount),0)as Amount FROM sl_banks_movrel INNER JOIN sl_banks_movements USING(ID_banks_movements) WHERE tablename='bills' AND tableid=bills.ID_bills) - (SELECT IFNULL(SUM(sl_bills_applies.Amount),0)as Amount FROM sl_bills_applies INNER JOIN sl_bills USING(ID_bills) WHERE ID_bills_applied = bills.ID_bills AND sl_bills.Type IN ('Deposit','Credit')), 0)as Amount FROM sl_bills as bills WHERE ID_bills ='".$in{'view'}."';";
					if ($in{'currency'} ne $cfg{'acc_default_currency'}) {
						$sql_string = "SELECT Amount, IFNULL(Amount - (SELECT IFNULL(SUM(AmountCurrency),0)as Amount FROM sl_banks_movrel INNER JOIN sl_banks_movements USING(ID_banks_movements) WHERE tablename='bills' AND tableid=bills.ID_bills) - (SELECT IFNULL(SUM(sl_bills_applies.Amount),0)as Amount FROM sl_bills_applies INNER JOIN sl_bills USING(ID_bills) WHERE ID_bills_applied = bills.ID_bills AND sl_bills.Type IN ('Deposit','Credit')), 0)as Amount FROM sl_bills as bills WHERE ID_bills ='".$in{'view'}."';";
					}
					my ($sth) = &Do_SQL($sql_string);
					my ($bill_amount,$bill_amount_payable) = $sth->fetchrow_array();

					my $status = ($bill_amount==$bill_amount_payable)?'New':'Partly Paid';

					my ($sth) = &Do_SQL("UPDATE sl_bills SET Status='$status' WHERE ID_bills = '".$in{'id_bills'}."' LIMIT 1;");
					$in{'status'} = &load_name("sl_bills","ID_bills",$in{'view'},"Status");

					# grabar en el log estos movimientos
					$in{'db'} = "sl_bills";
					&auth_logging('mer_bills_payment_canceled', $in{'id_bills'});
				}
			}


	}


	## Cancel bill payment
	if ($in{'cancel'} and $in{'status'} eq 'Paid' and &check_permissions('mer_bills_cancel','','')){
		
		# buscar todos los deposits y credits y desligarlos (borrarlos de la tabla sl_bills_applies)
		my ($sth) = &Do_SQL("SELECT sl_bills_applies.ID_bills_applies FROM sl_bills INNER JOIN sl_bills_applies USING(ID_bills) WHERE sl_bills_applies.ID_bills_applied='$in{'id_bills'}' AND sl_bills.Type IN ('Deposit','Credit','Debit') AND sl_bills.ID_vendors = '$in{'id_vendors'}' AND sl_bills.ID_bills NOT IN ('$in{'id_bills'}');");
		while ($rec = $sth->fetchrow_hashref){
			my ($sth2) = &Do_SQL("DELETE FROM sl_bills_applies WHERE ID_bills_applies = '".$rec->{'ID_bills_applies'}."' LIMIT 1;");
		}
		
		# buscar todos los POs (borrarlos de la tabla sl_bills_pos)
		my ($sth) = &Do_SQL("SELECT ID_bills_pos FROM sl_bills INNER JOIN sl_bills_pos USING(ID_bills) INNER JOIN sl_purchaseorders USING(ID_purchaseorders)  WHERE 1 AND ID_bills='$in{'id_bills'}';");
		while ($rec = $sth->fetchrow_hashref){
			my ($sth2) = &Do_SQL("DELETE FROM sl_bills_pos WHERE ID_bills_pos = '".$rec->{'ID_bills_pos'}."' LIMIT 1;");
		}

		# buscar todos los payments y duplicarlos con montos negativos(Debits)
		my ($sth) = &Do_SQL("SELECT ID_banks_movements, ID_banks_movrel FROM sl_banks_movrel INNER JOIN sl_banks_movements USING(ID_banks_movements) WHERE tablename='bills' AND tableid='".&filter_values($in{'view'})."';");
		while ($rec = $sth->fetchrow_hashref){
			my ($sth2) = &Do_SQL("INSERT INTO sl_banks_movements (ID_banks,  Type,  BankDate,  ConsDate,  Amount,  currency_exchange,  RefNum,  Memo,  Date,  Time,  ID_admin_users )
			(SELECT  ID_banks,  'Debits',  curdate(),  ConsDate,  Amount,  currency_exchange,  RefNum,  'Cancel Bank Movement',  curdate(),  curtime(),  $usr{'id_admin_users'} FROM sl_banks_movements WHERE ID_banks_movements = '".$rec->{'ID_banks_movements'}."');");
			$id_banks_movements = $sth2->{'mysql_insertid'};

			my ($sth) = &Do_SQL("INSERT INTO sl_banks_movrel SET ID_banks_movements = $id_banks_movements, tablename = 'bills', tableid = '".$in{'id_bills'}."', DATE = Curdate(), TIME = NOW(), ID_admin_users='$usr{'id_admin_users'}'");
			# le falta agregar el AmountPaid

			# La nota me indicara si este movimineto esta cancelado
			my ($sth) = &Do_SQL("INSERT INTO sl_banks_movements_notes (ID_banks_movements_notes,  ID_banks_movements,  Notes,  Type,  Date,  Time,  ID_admin_users )
			VALUES(NULL, $rec->{'ID_banks_movements'}, 'This movement has been cancelled.', 'Cancel', CURDATE(), CURTIME(),$usr{'id_admin_users'});");
		}		

		# pasar el status del bill a Void
		my ($sth) = &Do_SQL("UPDATE sl_bills SET Status='Void' WHERE ID_bills = '".$in{'id_bills'}."' LIMIT 1;");
		$in{'status'} = &load_name("sl_bills","ID_bills",$in{'view'},"Status") if (!$in{'status'});

		# grabar en el log todos estos movimientos
		$in{'db'} = "sl_bills";
		&auth_logging('mer_bills_canceled', $in{'id_bills'});
	}

	## Button Cancel bill payment
	if ($in{'status'} eq 'Paid' and &check_permissions('mer_bills_cancel','','')){
		$va{'cancel_bill_payment'} .= '&nbsp;  <a href="/cgi-bin/mod/'.$usr{'application'}.'/dbman?cmd=[in_cmd]&view='.$in{'id_bills'}.'&cancel=1"><img src="[va_imgurl]/[ur_pref_style]/delete.png" title="'.trans_txt('mer_bills_cancel').'" onclick="return Confirm_to_continue()"></a>';
	}

	if($in{'action'}){
		## tab 2
		$in{'n_amount'} = &filter_values($in{'n_amount'});
		$in{'n_amount'} = $in{'amount'} if (!$in{'n_amount'} and $in{'amount'} > 0);
		my $val_id_accounts_ml = $in{'id_accounts_ml'};
		$val_id_accounts_ml =~ s/\|//g;
		my $add_sql = ($val_id_accounts_ml eq '')? ",ID_accounts = '".&filter_values($in{'n_id_accounts'})."' ":",ID_accounts = NULL ";

		if (!$in{'n_amount'} or $in{'n_amount'} eq "" or $in{'n_amount'} <= 0 and (!$in{'delete_line'} and !$in{'id_segments'} and !$in{'amount_ml'})){
			$error{'n_amount'} = &trans_txt('required');
			++$err;
		}
		if ((int($in{'n_id_accounts'}) == 0) and !&bills_expenses_detection($in{'id_bills'}) and (!$in{'delete_line'} and !$in{'id_segments'} and !$in{'amount_ml'})){
			$error{'n_id_accounts'} = &trans_txt('required');
			++$err;
		}

		if (!$err) {
			#validar el n_amount como numero y el id accounts
			my ($sth) = &Do_SQL("UPDATE sl_bills  SET Amount = ".$in{'n_amount'}." ".$add_sql." WHERE ID_bills = $in{'id_bills'} LIMIT 1;");
			&auth_logging('mer_bills_amount_edited',$in{'id_bills'});
			$va{'tab_messages'} = &trans_txt("bills_amount_edited");
		}else {
			if (!$in{'delete_line'} and !$in{'id_segments'} and !$in{'amount_ml'}) {
				$va{'tab_messages'} = &trans_txt('reqfields_short');
				delete($in{'action'});
			}
		}

		# Procesamiento de detalle multilinea
		if ($in{'tab'} == 2 and int($in{'view'}) > 0 ) {

			if ($in{'delete_line'}) {

				###########################
				###########################
				## Borrado de lineas
				## ToDo AD: Agregar un boton de Cerrado de Bill expense para guardar en ese momento la contabilidad del expense
				## ToDo AD: Al borrar, revisar si la contabilidad ya fue posteada, como borrar. Preferible borar toda la contabilidad de el expense 
				###########################
				###########################

				$related = &load_name("sl_bills_expenses","id_bills_expenses",$in{'delete_line'},"Related_ID_bills_expenses");

				my ($sth) = &Do_SQL("DELETE FROM sl_bills_expenses WHERE id_bills_expenses = '$in{'delete_line'}' LIMIT 1;");
				# Log
				$in{'db'} = "sl_bills";
				&auth_logging('bills_expenses_line_removed',$in{'view'});
				
				my ($sth) = &Do_SQL("DELETE FROM sl_bills_expenses WHERE Related_ID_bills_expenses = '$in{'delete_line'}' LIMIT 1;");
				# Log
				$in{'db'} = "sl_bills";
				&auth_logging('bills_expenses_line_removed',$in{'view'});
				
			}else {

				my @arr_amount_ml = split /\|/, $in{'amount_ml'};
				my @arr_id_accounts_ml = split /\|/, $in{'id_accounts_ml'};
				my @arr_id_bills_expenses = split /\|/, $in{'id_bills_expenses'};
				my @arr_tax_amount_ml = split /\|/, $in{'tax_amount_ml'};
				my @arr_tax_id_accounts_ml = split /\|/, $in{'tax_id_accounts_ml'};
				my @arr_id_segments = split /\|/, $in{'id_segments'};


				my $total_lines, $lines;
				for my $i (0..$#arr_id_accounts_ml) {
					my $amount_ml = &filter_values($arr_amount_ml[$i]);
					my $id_accounts_ml = $arr_id_accounts_ml[$i];
					my $id_bills_expenses = int($arr_id_bills_expenses[$i]);
					my $tax_amount_ml = &filter_values($arr_tax_amount_ml[$i]);
					my $tax_id_accounts_ml = int($arr_tax_id_accounts_ml[$i]);
					my $id_segments = int($arr_id_segments[$i]);
					
					# Validar si vienen los campos requeridos
					if (int($id_accounts_ml) > 0 and $amount_ml > 0 ) {
						# Obtengo el valor total del Bill, Monto Restante em detalle, Monto Detallado en lineas
						my ($sth) = &Do_SQL("SELECT IFNULL(sl_bills.Amount,0)Amount, IFNULL(sl_bills.Amount - IFNULL(SUM(sl_bills_expenses.Amount),0),0)AmountRemaining, IFNULL(SUM(sl_bills_expenses.Amount),0)AmountLines FROM sl_bills LEFT JOIN sl_bills_expenses USING(ID_bills) WHERE ID_bills = '".$in{'view'}."'");
						my ($bill_amount, $amount_remaining, $amount_lines) = $sth->fetchrow_array();

						# &cgierr($amount_ml.'---'.$amount_remaining);
						# Lo cancelo temporalmente
						# if ($amount_ml <= $amount_remaining){

							my $deductible = ($in{'deductible'})? "Deductible = 'Yes', ": "Deductible = 'No',";
							my $sth = &Do_SQL("INSERT INTO sl_bills_expenses SET $deductible `ID_segments` = '$id_segments', `ID_bills` = '$in{'view'}',  `Amount` = '$amount_ml',  `ID_accounts` = '$id_accounts_ml',  `Date` = CURDATE(),  `Time` = CURTIME(),  `ID_admin_users` = '$usr{'id_admin_users'}';");
							my $id_bills_expenses = $sth->{'mysql_insertid'};
							$in{'id_bills_expenses'} .= $id_bills_expenses.',';
							
							if (int($id_bills_expenses)> 0){

								# Log
								$in{'db'} = "sl_bills";
								&auth_logging('bills_expenses_line_added',$in{'view'});

								## revisamos si se agrega linea Related de tax
								# and $tax_amount_ml > 0
								if (int($tax_id_accounts_ml) > 0) {
									# Obtengo el valor total del Bill, Monto Restante em detalle, Monto Detallado en lineas
									my ($sth) = &Do_SQL("SELECT IFNULL(sl_bills.Amount,0)Amount, IFNULL(sl_bills.Amount - IFNULL(SUM(sl_bills_expenses.Amount),0),0)AmountRemaining, IFNULL(SUM(sl_bills_expenses.Amount),0)AmountLines FROM sl_bills LEFT JOIN sl_bills_expenses USING(ID_bills) WHERE ID_bills = '".$in{'view'}."'");
									my ($bill_amount, $amount_remaining, $amount_lines) = $sth->fetchrow_array();

									# if ($tax_amount_ml <= $amount_remaining) {
										my $sth = &Do_SQL("INSERT INTO sl_bills_expenses SET $deductible `ID_segments` = '$id_segments', `ID_bills` = '$in{'view'}',  `Amount` = '$tax_amount_ml',  `ID_accounts` = '$tax_id_accounts_ml',  `Date` = CURDATE(),  `Time` = CURTIME(),  `ID_admin_users` = '$usr{'id_admin_users'}';");
										my $id_related = $sth->{'mysql_insertid'};
										$in{'id_bills_expenses'} .= $id_related.',';

										my $sth = &Do_SQL("UPDATE sl_bills_expenses SET Related_ID_bills_expenses='$id_bills_expenses' WHERE ID_bills_expenses='$id_related' LIMIT 1;");
										
										if (int($id_related)> 0){

											# Log
											$in{'db'} = "sl_bills";
											&auth_logging('bills_expenses_line_added',$in{'view'});
										}
									# }else {							
									# 	$va{'tab_messages'} = &trans_txt('bills_expenses_line_amount_higher');
									# }
								}
							}

						# }else {							
						# 	$va{'tab_messages'} = &trans_txt('bills_expenses_line_amount_higher');
						# }
					}else {
						# $va{'messages'} .= &trans_txt('required').' : Bill '.$id_creddep.'<br>';
						
					}
				}#for
			}
		}

	}	
	
	if ($in{'addpo'}) {
		my ($sth) = &Do_SQL("INSERT INTO sl_bills_pos SET ID_bills='$in{'id_bills'}', ID_purchaseorders=$in{'addpo'},Date=CURDATE(),Time=CURTIME(),ID_admin_users=$usr{'id_admin_users'}");	
		$va{'tab_messages'} = &trans_txt('po_added');
	}elsif($in{'delpo'}) {		
		my $amount = &load_name("sl_bills_pos","ID_bills_pos",$in{'delpo'},"Amount");
		my ($sth) = &Do_SQL("DELETE FROM sl_bills_pos WHERE ID_bills='$in{'id_bills'}' AND ID_bills_pos=$in{'delpo'} LIMIT 1;");
		&update_amount_bill($in{'id_bills'});
		$va{'tab_messages'} = &trans_txt('po_delete');
	}
		
	if($in{'addbills'}){
		my ($sth) = &Do_SQL("INSERT INTO sl_bills_applies SET ID_bills = $in{'id_bills'}, ID_bills_applied = $in{'addbills'},DATE = CURRENT_DATE(), TIME = CURRENT_TIME(), ID_admin_users=$usr{'id_admin_users'}");	
		$va{'tab_messages'} = &trans_txt('bills_applied');
	}elsif($in{'delbills'}){
		my ($sth) = &Do_SQL("DELETE FROM sl_bills_applies WHERE ID_bills='$in{'id_bills'}' AND ID_bills_applied = $in{'delbills'} LIMIT 1;");	
		$va{'tab_messages'} = &trans_txt('bills_applied_delete');
	}
	
	if ($in{'updateinfo'}) {
		#Se suma el monto total del PO.
		my ($sth2) = &Do_SQL("SELECT IFNULL(ROUND(SUM((Qty*Price)+Tax),2),0) FROM sl_purchaseorders_items WHERE ID_purchaseorders = $in{'id_po'}");
		($in{'amount_po'}) = $sth2->fetchrow_array();
		
		#Se suman los pagos hechos para obtener el due amount
		my ($sthd) = &Do_SQL("SELECT IFNULL(ROUND(SUM(sl_bills_pos.Amount),2),0) - IFNULL((SELECT SUM(Total) FROM sl_purchaseorders_adj WHERE ID_purchaseorders = sl_bills_pos.ID_purchaseorders),0)as Total
					FROM sl_bills_pos 
					INNER JOIN sl_bills ON sl_bills_pos.ID_bills = sl_bills.ID_bills
					WHERE ID_purchaseorders = $in{'id_po'}
					AND sl_bills.Status IN ('Paid')");
		
		($in{'amount_billsp'}) = $sthd->fetchrow_array();
		#Monto total del PO - El monto que se ha pagado
		$va{'total_due'} = ($in{'amount_po'} - $in{'amount_billsp'});
		# &cgierr('ajaxamount='.&filter_values($in{'ajaxamount'}).'<---'.&filter_values($va{'total_due'}).'<-->'.$in{'amount_billsp'});
		if($in{'ajaxamount'} <= $va{'total_due'} and $in{'ajaxamount'} > 0){
			my ($query,@cols);
				@cols = ('Amount');
			for(0..$#cols){
				if ($in{'type'} and $in{'type'} eq 'Bill') {
					$query .= " $cols[$_]='".&filter_values($in{'ajax'.lc($cols[$_])})."',";
				}elsif ($in{'type'} and $in{'type'} eq 'Credit') {
					$query .= " $cols[$_]='".&filter_values($in{'ajax'.lc($cols[$_])})."',";
					# $query .= " $cols[$_]='".(&filter_values($in{'ajax'.lc($cols[$_])}) * -1)."',";
				}
			}
			chop($query);
			my ($sth) = &Do_SQL("UPDATE sl_bills_pos SET $query WHERE ID_bills_pos='$in{'id_bills_pos'}' LIMIT 1;");
			
			&update_amount_bill($in{'id_bills'});
		}else{
			$va{'tab_messages'} = &trans_txt('bills_amount_invalid');
		}
	}
	
	if($in{'up_amount'}){		
		#sE OBTIENEN LOS DATOS DEL BILL tipo DEPOSITO		
		my ($sthb) = &Do_SQL("SELECT Amount
					FROM sl_bills
					WHERE ID_bills = ($in{'id_bills'})");
		($in{'amount_bill'}) = $sthb->fetchrow_array();
		
		#Se obtiene el monto total del Bill
		
		my ($sth2) = &Do_SQL("SELECT Amount FROM sl_bills WHERE ID_bills = $in{'bill_use'}");
		($in{'amount_bill_ap'}) = $sth2->fetchrow_array();
		
		#Se suma el monto total del Bill Deposit.
		my ($sth2) = &Do_SQL("SELECT SUM(Amount) 
					FROM sl_bills_applies 
					WHERE ID_bills_applied = $in{'bill_use'}
					 AND  ID_bills NOT IN($in{'id_bills'})");
		($in{'amount_applied'}) = $sth2->fetchrow_array();		
		$va{'total'}       = ($in{'amount_applied'}+$in{'ajaxamount'});
		$va{'amount_disp'} = $in{'amount_bill_ap'} - ($va{'total'});

		#Se suma el monto total de Depositos del Bill.
		my ($sth2) = &Do_SQL("SELECT SUM(Amount) FROM sl_bills_applies WHERE ID_bills = $in{'id_bills'}");
		($va{'total_bill'}) = $sth2->fetchrow_array();
		$va{'total_real'} = $va{'total_bill'} + $va{'total'};
		
		if($in{'ajaxamount'} <= $va{'amount_disp'} and $va{'total_real'} <= $in{'amount_bill'}){
			my ($query,@cols);
				@cols = ('Amount');
			for(0..$#cols){
				$query .= " $cols[$_]='".&filter_values($in{'ajax'.lc($cols[$_])})."',";
			}
			chop($query);
			my ($sth) = &Do_SQL("UPDATE sl_bills_applies SET $query WHERE ID_bills_applies='$in{'id_bills_apps'}'");			
			$va{'tab_messages'} = &trans_txt('bills_applied');
		}else{
			$va{'tab_messages'} = &trans_txt('bills_amount_invalid');
		}
	}

	if($in{'status'} ne 'Paid'){
		$va{'idbutton'} = &template_idbutton;
	}else {

		if ($in{'type'} ne 'Bill') {
			my ($sth) = &Do_SQL("SELECT sl_banks_movements.ID_banks, sl_banks_movements.RefNum, sl_banks_movements.ID_banks_movements
			FROM sl_banks_movrel INNER JOIN sl_banks_movements ON sl_banks_movrel.ID_banks_movements = sl_banks_movements.ID_banks_movements
			WHERE tablename = 'bills' AND tableid   = $in{'id_bills'}");
			$data = $rec = $sth->fetchrow_hashref;
			if (int($rec->{'ID_banks'}) > 0) {
				$va{'bank'} = &load_name("sl_banks","ID_banks",$rec->{'ID_banks'},"Name");
				$va{'paid_info'} = qq| <tr>
						<td width="30%" valign="top">Paid Info :</span></td>
						<td class="smalltext">
						<a href=\"/cgi-bin/mod/$usr{'application'}/dbman?cmd=fin_banks_movements&view=$rec->{'ID_banks_movements'}\">($rec->{'ID_banks_movements'}) $va{'bank'} Num. Ref: $rec->{'RefNum'}</a>
						</td>
						</tr>|;
			}
		}
	}
	
	$in{'amount'}      = &load_name("sl_bills","ID_bills",$in{'id_bills'},"Amount");
	$va{'id_vendors'} = $in{'id_vendors'};	
	$va{'vendors'} = &load_db_names('sl_vendors','ID_vendors',$in{'id_vendors'},'([ID_vendors]) [CompanyName]');
	$in{'id_vendors'} =  "<a href=\"/cgi-bin/mod/$usr{'application'}/dbman?cmd=mer_vendors&view=$in{'id_vendors'}\">$va{'vendors'}</a>";	
	if($in{'id_accounts'} and $in{'id_accounts'} ne "NULL"){
		$va{'n_accounts'} = &load_name("sl_accounts","ID_accounts",$in{'id_accounts'},"NAME");
		
		my $link_accounts = qq|<a href='javascript:trjump("/cgi-bin/mod/$usr{'application'}/dbman?cmd=fin_accounts&view=$in{'id_accounts'}")'>
		($in{'id_accounts'}) $va{'n_accounts'}</a>|;

		$va{'accounts'} = qq| <tr><td width="30%" valign="top">Account :</span></td>
					  <td class="smalltext">$link_accounts</td> </tr> |;
	}

	if ($in{'type'} eq 'Bill') {
		$va{'bill_amount_due'} = &format_price(&bills_amount_due($in{'id_bills'}));
	}
	$va{'only_nopadided'} = ($in{'type'} eq 'Bill' and $in{'status'} ne 'Paid')?'':'display:none';
	
	$in{'v_amount'} = &format_price($in{'amount'});

	$va{'display_only_internationals'} = ($in{'currency'} ne $cfg{'acc_default_currency'})? '':'display:none;';
	
	if ($in{'authby'}>0){
		$va{'authorization'} = "($in{'authby'}) " . &load_db_names('admin_users','ID_admin_users',$in{'authby'},"[FirstName] [LastName]");
	}else{
		$va{'authorization'} = "---";
	}

}


sub update_amount_bill{
# --------------------------------------------------------
	my ($idbills) = @_;
	
	my ($sth) = &Do_SQL("UPDATE sl_bills  SET Amount = (SELECT IFNULL((SELECT SUM(sl_bills_pos.Amount) FROM sl_bills_pos WHERE ID_bills = '$idbills'),0)) WHERE ID_bills = '$idbills' LIMIT 1;");
}

sub bill_status{
# --------------------------------------------------------
	my ($output);
	if ($in{'type'} eq 'Bill') {
		
		# Detectamos si es un Bill de Expenses
		my ($sth) = &Do_SQL("SELECT SUM(sl_bills_expenses.Amount)Amount, COUNT(*)AS nlines FROM sl_bills INNER JOIN sl_bills_expenses USING(ID_bills) WHERE ID_bills='$in{'id_bills'}';");
		my ($amount_lines, $no_lines) = $sth->fetchrow_array();
		
		if ($no_lines > 0 and $in{'status'} eq 'New' ){
			$output = qq|<a href='/cgi-bin/mod/[ur_application]/dbman?cmd=$in{'cmd'}&view=$in{'view'}&to_process=1' onclick="return Confirm_to_continue()"><img src='[va_imgurl]/[ur_pref_style]/b_ok.png' title='Auth' alt='Process' border='0'></a>|;
		}elsif($no_lines > 0 and $in{'status'} eq 'Pending'){
			$output = qq|<a href='/cgi-bin/mod/[ur_application]/dbman?cmd=$in{'cmd'}&view=$in{'view'}&to_process=1' onclick="return Confirm_to_continue()"><img src='[va_imgurl]/[ur_pref_style]/b_ok.png' title='Auth' alt='Process' border='0'><img src='[va_imgurl]/[ur_pref_style]/b_ok.png' title='Auth' alt='Process' border='0'></a>|;
		}elsif($in{'status'} eq 'New' and $in{'amount'} > 0){
			$output = qq|<a href='/cgi-bin/mod/[ur_application]/dbman?cmd=$in{'cmd'}&view=$in{'view'}&to_process=1' onclick="return Confirm_to_continue()"><img src='[va_imgurl]/[ur_pref_style]/b_ok.png' title='Auth' alt='Process' border='0'></a>|;
		}elsif($in{'status'} eq 'Pending' and $in{'amount'} > 0){
			$output = qq|<a href='/cgi-bin/mod/[ur_application]/dbman?cmd=$in{'cmd'}&view=$in{'view'}&to_process=1' onclick="return Confirm_to_continue()"><img src='[va_imgurl]/[ur_pref_style]/b_ok.png' title='Auth' alt='Process' border='0'><img src='[va_imgurl]/[ur_pref_style]/b_ok.png' title='Auth' alt='Process' border='0'></a>|;
		}elsif($in{'status'} eq 'Processed' and $in{'amount'} > 0){
			$output = qq|<a href='/cgi-bin/mod/[ur_application]/admin?cmd=mer_bills_payments&id_vendors=$va{'id_vendors'}' onclick="return Confirm_to_continue()"><img src='[va_imgurl]/[ur_pref_style]/b_cauth.gif' title='Pay' alt='Pay' border='0'></a>|;
		}
	}elsif (($in{'type'} eq 'Deposit' or $in{'type'} eq 'Debit') and $in{'amount'} > 0) {
		if($in{'status'} eq 'New'){
			$output = qq|<a href='/cgi-bin/mod/[ur_application]/dbman?cmd=$in{'cmd'}&view=$in{'view'}&to_process=1' onclick="return Confirm_to_continue()"><img src='[va_imgurl]/[ur_pref_style]/b_ok.png' title='Auth' alt='Process' border='0'></a>|;
		}elsif($in{'status'} eq 'Pending'){
			$output = qq|<a href='/cgi-bin/mod/[ur_application]/dbman?cmd=$in{'cmd'}&view=$in{'view'}&to_process=1' onclick="return Confirm_to_continue()"><img src='[va_imgurl]/[ur_pref_style]/b_ok.png' title='Auth' alt='Process' border='0'><img src='[va_imgurl]/[ur_pref_style]/b_ok.png' title='Auth' alt='Process' border='0'></a>|;
		}elsif($in{'status'} eq 'Processed'){
			$output = qq|<a href='/cgi-bin/mod/[ur_application]/admin?cmd=mer_bills_dd_payments&id_vendors=$va{'id_vendors'}' onclick="return Confirm_to_continue()"><img src='[va_imgurl]/[ur_pref_style]/b_cauth.gif' title='Pay' alt='Pay' border='0'></a>|;
		}elsif($in{'status'} eq 'Paid'){
			my ($sth) = &Do_SQL("SELECT (Amount - (SELECT IFNULL(SUM(Amount),0)as Amount FROM sl_bills_applies WHERE ID_bills = sl_bills.ID_bills))as AmountAvailable FROM sl_bills WHERE 1 AND ID_bills = '".$in{'view'}."';");
			my ($amount_available) = $sth->fetchrow_array();
			if ($amount_available > 0) {
				$output = qq|<a href='/cgi-bin/mod/[ur_application]/admin?cmd=mer_bills_payments&id_vendors=$va{'id_vendors'}' onclick="return Confirm_to_continue()"><img src='[va_imgurl]/[ur_pref_style]/b_ok.png' title='Apply' alt='Apply' border='0'></a>|;
			}

		}
	}else {
		if($in{'status'} eq 'New' and $in{'amount'} > 0){
			$output = qq|<a href='/cgi-bin/mod/[ur_application]/dbman?cmd=$in{'cmd'}&view=$in{'view'}&to_process=1' onclick="return Confirm_to_continue()"><img src='[va_imgurl]/[ur_pref_style]/b_ok.png' title='Auth' alt='Process' border='0'></a>|;
		}elsif($in{'status'} eq 'Pending' and $in{'amount'} > 0){
			$output = qq|<a href='/cgi-bin/mod/[ur_application]/dbman?cmd=$in{'cmd'}&view=$in{'view'}&to_process=1' onclick="return Confirm_to_continue()"><img src='[va_imgurl]/[ur_pref_style]/b_ok.png' title='Auth' alt='Process' border='0'><img src='[va_imgurl]/[ur_pref_style]/b_ok.png' title='Auth' alt='Process' border='0'></a>|;
		}elsif($in{'status'} eq 'Processed' and $in{'amount'} > 0){
			$output = qq|<a href='/cgi-bin/mod/[ur_application]/admin?cmd=mer_bills_payments&id_vendors=$va{'id_vendors'}' onclick="return Confirm_to_continue()"><img src='[va_imgurl]/[ur_pref_style]/b_ok.png' title='Apply' alt='Apply' border='0'></a>|;
		}
	}

	return $output;
}
#############################################################################
#############################################################################
#   Function: validate_mer_bills
#       Es: Procesa datos de sl_bills antes de ser editados
#       En: 
#
#    Created on: 26/03/2013
#
#    Author: Alejandro Diaz
#
#    Modifications:
#
#
#   Parameters:
#
#  Returns:
#
#   See Also:
#
#
sub validate_mer_bills {
# --------------------------------------------------------
	my ($err);
	
	$in{'currency'} = &load_name("sl_vendors","ID_vendors",$in{'id_vendors'},"Currency");
	$in{'paymentmethod'} = &load_name("sl_vendors","ID_vendors",$in{'id_vendors'},"PaymentMethod");
	delete($in{'currency_exchange'}) if ($cfg{'acc_default_currency'} eq $in{'currency'});
	if (!$in{'currency_exchange'} and $cfg{'acc_default_currency'} ne $in{'currency'}) {
	 	$error{'currency_exchange'} = &trans_txt('required');
	 	++$err;
	}
	my $sth2=&Do_SQL("SELECT * FROM sl_bills WHERE ID_bills='".$in{'id_bills'}."';");
	my $rec=$sth2->fetchrow_hashref;

	## Validamos si este movimiento es editable
	if ($in{'status'} and $in{'status'} eq 'Paid' and $in{'id_bills'}) {

		$in{'amount'}=$rec->{'Amount'};
		$in{'id_accounts'}=$rec->{'ID_accounts'};
		$in{'terms'}=$rec->{'Terms'};
		$in{'status'}=$rec->{'Status'};
		$in{'type'}=$rec->{'Type'};
		$in{'id_vendors'}=$rec->{'ID_vendors'};
		$in{'currency'}=$rec->{'Currency'};

	}elsif ($in{'id_bills'} and ($in{'type'} eq 'Deposit' or $in{'type'} eq 'Credit') ) {
		my ($sth) = &Do_SQL("SELECT ifnull(Amount,0)Amount, ID_accounts, Status
			,(select count(*) from sl_banks_movrel where tablename='bills' and tableid=sl_bills.ID_bills)billsmovrel
			,(select count(*) from sl_bills_pos where ID_bills=sl_bills.ID_bills)billspos
			,(select count(*) from sl_bills_applies where ID_bills=sl_bills.ID_bills)billsapplies
			FROM sl_bills WHERE ID_bills='$in{'id_bills'}'; ");
		my ($amount, $id_accounts, $status, $billsmovrel, $billspos, $billsapplies) = $sth->fetchrow_array();

		if ($billsapplies > 0) {
			$in{'amount'}=$rec->{'Amount'};
			$in{'id_accounts'}=$rec->{'ID_accounts'};
			$in{'terms'}=$rec->{'Terms'};
			$in{'status'}=$rec->{'Status'};
			$in{'type'}=$rec->{'Type'};
			$in{'id_vendors'}=$rec->{'ID_vendors'};
			$in{'currency'}=$rec->{'Currency'};
		}
		
	}else {
		$in{'amount'}=$rec->{'Amount'};
		$in{'id_accounts'}=$rec->{'ID_accounts'};
		$in{'status'}=$rec->{'Status'};
	}

	if ($in{'add'}){
		$in{'status'} = 'New';
	}
	
	return $err;
}

#############################################################################
#############################################################################
#   Function: loading_mer_bills
#
#       Es: Procesa datos de sl_bills antes de ser cargados por la accion view
#       En: 
#
#    Created on: 
#
#    Author: Alejandro Diaz
#
#    Modifications:
#
#
#   Parameters:
#
#  Returns:
#
#   See Also:
#
#
sub loading_mer_bills {
#############################################################################
#############################################################################

	## Validamos si este movimiento es editable
	if ($in{'id_bills'} and $in{'status'} and $in{'status'} eq 'Paid') {
		$va{'restrict_type'} = ' style="display:none;" ';
		$va{'restrict_id_vendors'} = 'disabled="disabled"';
		$va{'restrict_lens_id_vendors'} = ' style="display:none;" ';
		$va{'restrict_currency'} = ' style="display:none;" ';
	}

	if ($in{'id_bills'} and ($in{'type'} eq 'Deposit' or $in{'type'} eq 'Credit') ) {
		my ($sth) = &Do_SQL("SELECT ifnull(Amount,0)Amount, ID_accounts, Status
			,(select count(*) from sl_banks_movrel where tablename='bills' and tableid=sl_bills.ID_bills)billsmovrel
			,(select count(*) from sl_bills_pos where ID_bills=sl_bills.ID_bills)billspos
			,(select count(*) from sl_bills_applies where ID_bills=sl_bills.ID_bills)billsapplies
			FROM sl_bills WHERE ID_bills='$in{'id_bills'}'; ");
		my ($amount, $id_accounts, $status, $billsmovrel, $billspos, $billsapplies) = $sth->fetchrow_array();

		if ($billsapplies > 0) {
			$va{'restrict_type'} = ' style="display:none;" ';
			$va{'restrict_id_vendors'} = 'disabled="disabled"';
			$va{'restrict_lens_id_vendors'} = ' style="display:none;" ';
			$va{'restrict_currency'} = ' style="display:none;" ';
		}
	}
}

sub bills_to_void {
#############################################################################
#############################################################################

	my ($id_bills) = @_;
	my $id_vendors = &load_name('sl_bills','ID_bills',$id_bills,'ID_vendors');
	my $status = &load_name('sl_bills','ID_bills',$id_bills,'Status');

	if ($status eq 'Partly Paid' or $status eq 'Paid'){

	}else{
		my ($sth) = &Do_SQL("SELECT ID_movements, ID_accounts, Amount, Reference, EffDate, tableused, ID_tableused, Category, Credebit, ID_segments, ID_journalentries, Status, Date, Time, ID_admin_users
			FROM sl_movements WHERE tableused='sl_bills' AND ID_tableused='$id_bills';");
		while (my $rec = $sth->fetchrow_hashref){
			if ($rec->{'ID_journalentries'} > 0){

				if ($rec->{'Credebit'} eq 'Credit'){
					# Debit required for reverse
					my ($sthd) = &Do_SQL("INSERT INTO sl_movements SET
						ID_accounts='".$rec->{'ID_accounts'}."'
						, Amount='".$rec->{'Amount'}."'
						, Reference='".$rec->{'Reference'}."'
						, EffDate='".$rec->{'EffDate'}."'
						, tableused='".$rec->{'tableused'}."'
						, ID_tableused='".$rec->{'ID_tableused'}."'
						, Category='".$rec->{'Category'}."'
						, Credebit='Debit'
						, ID_segments='".$rec->{'ID_segments'}."'
						, ID_journalentries=NULL
						, Status='Active'
						, Date=CURDATE()
						, Time=CURTIME()
						, ID_admin_users='$usr{'id_admin_users'}';");
					my ($idm_debit) = $sthd->{'mysql_insertid'};
				}elsif ($rec->{'Credebit'} eq 'Debit'){
					# Credit required for reverse
					my ($sthd) = &Do_SQL("INSERT INTO sl_movements SET
						ID_accounts='".$rec->{'ID_accounts'}."'
						, Amount='".$rec->{'Amount'}."'
						, Reference='".$rec->{'Reference'}."'
						, EffDate='".$rec->{'EffDate'}."'
						, tableused='".$rec->{'tableused'}."'
						, ID_tableused='".$rec->{'ID_tableused'}."'
						, Category='".$rec->{'Category'}."'
						, Credebit='Credit'
						, ID_segments='".$rec->{'ID_segments'}."'
						, ID_journalentries=NULL
						, Status='Active'
						, Date=CURDATE()
						, Time=CURTIME()
						, ID_admin_users='$usr{'id_admin_users'}';");
					my ($idm_credit) = $sthc->{'mysql_insertid'};
				}
			}else{
				# Delete records
				my ($sthd) = &Do_SQL("DELETE FROM sl_movements WHERE ID_movements='".$rec->{'ID_movements'}."' LIMIT 1;");
			}
		}
	}

	return;
}

1;