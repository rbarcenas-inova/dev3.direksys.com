##########################################################
##		FINANCE	 		  ##
##########################################################
sub validate_fin_arman {
# --------------------------------------------------------
	my $err;
		
	if($in{'add'}){
		$in{'status'} = 'New';
	}
	return $err;
}

sub view_fin_arman {
# --------------------------------------------------------
	if($in{'action'} eq 'uploadorders' and $in{'upload_orders'}){
		$in{'upload_orders'} =~ s/\r//g;
		my (@ary) = split(/\n|,/,$in{'upload_orders'});
		$in{'upload_orders'} = '';
		for my $i (0..$#ary){
			if ($ary[$i]>0){
				my ($sth) = &Do_SQL("SELECT MIN(Paymentdate), SUM(Amount),COUNT(*) FROM sl_orders_payments WHERE ID_orders=$ary[$i] AND Captured<>'Yes' AND CapDate='0000-00-00'");
				my ($duesince, $tot, $qty) = $sth->fetchrow_array;
				my ($retid) = &load_name('sl_returns','ID_orders',$ary[$i],'ID_returns');
				if ($tot>1 and !$retid){
					++$q;
					my ($sth) = &Do_SQL("REPLACE INTO sl_arman_payments SET ID_arman=$in{'id_arman'}, ID_orders=$ary[$i], DueSince='$duesince',OrigAmount='$tot',Qty='$qty',Status='New',Date=CURDATE(), Time=CURTIME(),ID_admin_users=$usr{'id_admin_users'}");
					$in{'upload_orders'} .= $ary[$i] . " ".&trans_txt('updated')." ".$sth->rows . "\n";
				}elsif ($tot<1 and $tot>0 and !$retid){
					$in{'upload_orders'} .= $ary[$i] . " ".&trans_txt('invalid')."/".&trans_txt('amount')."\n";
				}elsif($tot>0 and $retid>0){
					$in{'upload_orders'} .= $ary[$i] . " ".&trans_txt('invalid')."/".&trans_txt('returns')."\n";
				}else{
					$in{'upload_orders'} .= $ary[$i] . " ".&trans_txt('invalid')."\n";
				}
			}else{
				$in{'upload_orders'} .= $ary[$i] . " ".&trans_txt('invalid')."\n";
			}
		}
		$va{'tabmessages'} = &trans_txt('uploaded') . " : $q";
		#SELECT SUM(Amount),COUNT(*) FROM sl_orders_payments WHERE ID_orders=310055 AND Captured<>'Yes' AND CapDate='0000-00-00'
	}elsif($in{'action'} eq 'uploadorders' and !$in{'upload_orders'}){
		$va{'tabmessages'} = &trans_txt('required');
	}elsif ($in{'drop'}>0){
		&auth_logging('paymen_droped',$in{'id_arman'});
		my ($sth) = &Do_SQL("DELETE FROM sl_arman_payments WHERE ID_arman_payments=$in{'drop'} AND ID_arman=$in{'id_arman'} AND Status='New'");
		$va{'tabmessages'} = &trans_txt('order_dropped');
	}
	## Basic
	$va{'aragencyname'} = &load_name('sl_aragencies','ID_aragencies',$in{'id_aragencies'},'Name');
	
	## Status
	if ($in{'status'} eq 'New' and $in{'action'} eq 'processed'){
		&auth_logging('status_updated',$in{'id_arman'});
		$in{'status'} = 'Processed';
		my ($sth) = &Do_SQL("UPDATE sl_arman SET Status='Processed' WHERE ID_arman=$in{'id_arman'} AND Status='New'");
	}elsif($in{'status'} ne 'New' and $in{'action'} eq 'download'){
		$end_date = &sqldate_plus(&get_sql_date(),15);
		$end_date_num = &date_to_unixtime($end_date);
		
		$np_date = &sqldate_plus(&get_sql_date(),35);
		$np_date_num = &date_to_unixtime($np_date);
		#print "Content-type: text/html\n\n";
		print "Content-type: application/vnd.ms-excel\n";
		print "Content-disposition: attachment; filename=arman$in{'id_arman'}.csv\n\n";
		my (@cols) = ("Contract ID","Sale Source","Last Name","First Name","Middle Name","Address 1","Address 2","City","State","ZipCode","Country","Phone Number1","Phone Number2","Email","Original Amount","Current Amount Balance","Order Date","Shipping Date","ID Product","Product Name","Credit-Card","# Installments","Carrier (UPS FED EX etc.)","Tracking Number","Date of first payment","Date of last payment", "First Payment Expired ");
		print '"'.join('","',@cols) . "\"\n";
		my ($sth) = &Do_SQL("SELECT sl_orders.* FROM sl_orders LEFT JOIN sl_arman_payments ON sl_arman_payments.ID_orders=sl_orders.ID_orders  WHERE ID_arman=$in{'id_arman'}");
		while ($order = $sth->fetchrow_hashref()){
			$line = &col_sko_order($end_date_num,$np_date_num,$order);
			if ($line){
				print "$line\n";
			}else{
				#print "$order->{'ID_orders'} ERR\n";
			}
		}
		exit 1;
	}
	
	if ($in{'status'} eq 'New'){
		$va{'status'} = qq|&nbsp;&nbsp;&nbsp;&nbsp; <a href="/cgi-bin/mod/$usr{'application'}/dbman?cmd=fin_arman&view=$in{'id_arman'}&action=processed">|. &trans_txt('changeto')." Processed</a>";
	}else{
		$va{'status'} = qq|&nbsp;&nbsp;&nbsp;&nbsp; <a href="/cgi-bin/mod/$usr{'application'}/dbman?cmd=fin_arman&view=$in{'id_arman'}&action=download">|. &trans_txt('download')."</a>";
	}
	
	
	## Totals
	my ($sth) = &Do_SQL("SELECT count(*), SUM(OrigAmount), SUM(IF(PaidAmount>0,1,0)) , SUM(PaidAmount)FROM `sl_arman_payments` WHERE ID_arman=$in{'id_arman'}");
	($va{'qorders'}, $va{'totorders'}, $va{'qpaid'}, $va{'tpaid'}) = $sth->fetchrow_array;
	
	$va{'pqpaid'} = &round($va{'qpaid'}/$va{'qorders'}) if ($va{'qorders'}>0);
	$va{'tqpaid'} = &round($va{'tpaid'}/$va{'totorders'}) if ($va{'totorders'}>0);
	$va{'totorders'} = &format_price($va{'totorders'});
	$va{'tpaid'} = &format_price($va{'tpaid'});
	
}



##########################################################
##		FINANCE	 		  ##
##########################################################
sub validate_fin_deposits {
# --------------------------------------------------------
	my $err;
		
	if($in{'add'}){
		$in{'status'} = 'New';
	}
	return $err;
}

sub loaddefault_fin_deposits {
# --------------------------------------------------------
	my $err;
	$in{'status'} = 'New';
	return $err;
}


##########################################################
##		FINANCE	 		  ##
##########################################################
sub validate_fin_taxcounty {
# --------------------------------------------------------
	my $err;
		
	if (date_to_unixtime($in{'fromdate'}) > date_to_unixtime($in{'todate'})) {
		$error{'fromdate'} = &trans_txt('invalid');
	}	
	return $err;
}


#############################################################################
#############################################################################
#   Function: loaddefault_fin_bills
#
#       Es: Carega valores por defecto para el formulario bills
#       En: 
#
#
#    Created on: 
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
#
#   See Also:
#
#      <view_fin_bills>
#
sub loaddefault_fin_bills {
#############################################################################
#############################################################################

	$in{'type'} = 'Bill';
	$in{'status'} = 'New';

}


#############################################################################
#############################################################################
#   Function: view_fin_bills
#
#       Es: Procesa datos de sl_bills antes de ser cargados por la accion view
#       En: 
#
#
#    Created on: 
#
#    Author: _Roberto Barcenas_
#
#    Modifications:
#
#        - Modified on ** by _Roberto Barcenas_ : 
#
#   Parameters:
#
#      - x  
#      - y  
#
#  Returns:
#
#   See Also:
#
#      <loaddefault_fin_bills>
#
sub view_fin_bills {
#############################################################################
#############################################################################

	$in{'amount'} = &format_price($in{'amount'});
}

#############################################################################
#############################################################################
#   Function: view_fin_banks_movements
#
#       Es: Procesa datos de sl_banks_movements antes de ser cargados por la accion view
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
sub view_fin_banks_movements {
#############################################################################
#############################################################################

	$in{'custom_print_header'}=1;
	my $amount_without_format = $in{'amount'};
	$in{'amount'} = &format_price($in{'amount'});

	if ($in{'action'} and $in{'add_acc_amounts'}) {

		my @acc_amounts=split(/\|/,$in{'acc_amount'});
		my @acc_id_accounts = split(/\|/,$in{'acc_id_accounts'});
		my $total_acc_amount = 0;
		my %amount_by_account = ();
		for(0..$#acc_amounts) {
			$total_acc_amount += $acc_amounts[$_];
			$amount_by_account{$acc_id_accounts[$_]}{$_} = $acc_amounts[$_];
		}

		if ($in{'amount'} == $total_acc_amount) {
			foreach my $account (keys %amount_by_account) {
				foreach my $nl (keys %{$amount_by_account{$account}}) {
					my ($sth) = &Do_SQL("INSERT INTO sl_banks_movrel
										SET
											ID_banks_movrel=NULL
											, ID_banks_movements='$in{'id_banks_movements'}'
											, tablename='accounts'
											, tableid='$account'
											, AmountPaid='$amount_by_account{$account}{$nl}'
											, Date=CURDATE()
											, Time=CURTIME()
											, ID_admin_users='$in{'id_admin_users'}';");
				}
			}
		}
	}
	
	# ABA-ACH :: Clabe Interbancaria
	# SubAccountOf :: No de Cuenta
	my ($sth) =&Do_SQL("SELECT  `Name`,  `ShortName`,  `Description`,  `BankName`, `Currency`, `ABA-ACH`,  `SubAccountOf` FROM `sl_banks` WHERE ID_banks =".$in{'id_banks'}." ;");
	$rec=$sth->fetchrow_hashref;

	$in{'banks_name'} = ($rec->{'BankName'})?$rec->{'BankName'}:'';
	$in{'currency'} = ($rec->{'Currency'})?$rec->{'Currency'}:'';
	$in{'aba-ach'} = ($rec->{'ABA-ACH'})?$rec->{'ABA-ACH'}:'';
	$in{'subaccountof'} = ($rec->{'SubAccountOf'})?$rec->{'SubAccountOf'}:'';


	# $in{'refnum'} = $in{'refnumcustom'} if (!$in{'refnum'});
	$va{'show_currency_exchange'} = ($in{'amountcurrency'} and $in{'currency_exchange'} > 1)? '':'display:none';

	# Info for check print
	if ($in{'type'} eq 'Credits' and $in{'toprint'}){
		my ($sth) = &Do_SQL("SELECT DATE_FORMAT(BankDate,'%c')month, DATE_FORMAT(BankDate,'%e')day, DATE_FORMAT(BankDate,'%Y')year, amount, amountcurrency, currency_exchange FROM sl_banks_movements WHERE ID_banks_movements = ".$in{'id_banks_movements'}." ;");
		my ($month_number, $day, $year, $amount_bankmovements, $amountcurrency, $currency_exchange) = $sth->fetchrow_array();
		my @months = ('','Enero','Febrero','Marzo','Abril','Mayo','Junio','Julio','Agosto','Septiembre','Octubre','Noviembre','Diciembre');
		$va{'date_check'} = $months[$month_number].' '.$day.', '.$year;
		$va{'amount_check'}  = &format_number($amount_without_format,2); 
		
		# ADiaz:Imprimir el nombre del proveedor en caso de que "memo" este vacio
		$va{'beneficiary_check'} = $in{'memo'};
		if ($in{'memo'} eq ''){
			my $sth_bills=&Do_SQL("SELECT * FROM sl_bills INNER JOIN sl_banks_movrel ON sl_banks_movrel.tablename='bills' AND sl_banks_movrel.tableid=ID_bills WHERE ID_banks_movements='".$in{'id_banks_movements'}."' LIMIT 1;");
			while ($recs_bills=$sth_bills->fetchrow_hashref) {
				$va{'beneficiary_check'} = &load_name('sl_vendors','ID_vendors',$recs_bills->{'ID_vendors'},'CompanyName');
			}
		}
		
		$va{'amount_letter_check'} = &amount_in_words($amount_without_format);
		my $spaces_between  = 85-(length($va{'beneficiary_check'}));


		#Se verifica que la cuenta bancaria este registrada en Dolares;
		if( $amountcurrency ne '' and $currency_exchange > 1 and $in{'currency'} eq 'US$' and $in{'f'} eq 3 ){
			$va{'amount_check'}  = &format_number($amountcurrency,2); 
			$va{'amount_letter_check'} = &amount_in_words($amountcurrency, 'USD');
		}

		my $txt_banorte  = "\n\n\n";
		$txt_banorte .= "                                                $va{'date_check'}\n";
		$txt_banorte .= "                                                                                              $va{'amount_check'}\n";
		$txt_banorte .= "                         $va{'beneficiary_check'}\n\n";
		$txt_banorte .= "  $va{'amount_letter_check'}\n";

		my $txt_santander  = "                                                                           $va{'date_check'}\n\n\n";
		$txt_santander .= "     $va{'beneficiary_check'}".(" "x$spaces_between)."$va{'amount_check'}\n\n";
		$txt_santander .= "     $va{'amount_letter_check'}\n";


		$va{'txt_banorte'} = string_to_hexadecimal_ascii($txt_banorte); 
		$va{'txt_santander'} = string_to_hexadecimal_ascii($txt_santander);

	}






	##################################
	##################################
	##################################
	### 
	###	Cancel Payment
	###
	##################################
	##################################
	##################################
	if (!&payment_is_canceled($in{'view'}) and &check_permissions('fin_banks_movements_cancel','','')){

		&Do_SQL("DELETE FROM sl_vars WHERE VName = 'Bank_Movements_Applied' AND STR_TO_DATE(Comment_En, '%Y-%m-%d') < CURDATE();");
		
		my $tvars = 0;
		my $tmovs = 0;
		my @posted_bills;

		my ($sth) = &Do_SQL("SELECT COUNT(*) FROM sl_vars WHERE VName = 'Bank_Movements_Applied' AND VValue = '".$in{'id_banks_movements'}."';");
		my ($tvars) = $sth->fetchrow();

		#########
		######### 2. Boton para cancelar
		#########
		if ($in{'type'} eq 'Credits'){ 
			## Solamente se puede poner boton si la validacion fue correcta
			
			my $dimage = $tvars ? 'cancel.png' : 'rejected.gif';
			$tmovs = $tvars ? 0 : 1;
			
			$va{'cancel_btn'} = qq|<a href="/cgi-bin/mod/$usr{'application'}/dbman?cmd=$in{'cmd'}&view=$in{'view'}&cancel=1&action=1" onclick="return Confirm_to_continue()"><img src='$va{'imgurl'}/$usr{'pref_style'}/|.$dimage.qq|' title='Cancel' alt='Cancel' border='0'></a>|; 

		}


		if ($in{'action'} and $in{'cancel'}) {

			&Do_SQL("START TRANSACTION;");

			#########
			######### 3. Cancelacion
			#########
							

			my (%overwrite_movs) = ('effdate' => '0000-00-00', 'id_journalentries' => 0, 'id_admin_users' => $usr{'id_admin_users'});
			my $movrel_amount = 0;

			#########
			######### 3.1) Cancelar sl_banks_movements
			#########
			my (%overwrite_bank) = ('type' => 'Debits','consdate' => '0000-00-00','bankdate' => '0000-00-00', 'memo' => 'Cancellation Payment: ' . $in{'id_banks_movements'}, 'id_admin_users' => $usr{'id_admin_users'});
			my $new_id_banks_movements = &Do_selectinsert('sl_banks_movements', "ID_banks_movements = '$in{'id_banks_movements'}'", "", "", %overwrite_bank);
			&Do_SQL("UPDATE sl_banks_movements SET BankDate = CURDATE(), RefNum = NULL, RefNumCustom = NULL, doc_type = 'NA' WHERE ID_banks_movements = '$new_id_banks_movements';");

			if ($new_id_banks_movements){

				my (%overwrite_movrel) = ('id_banks_movements' => $new_id_banks_movements, 'id_admin_users' => $usr{'id_admin_users'});
				my ($sth3) = &Do_SQL("SELECT ID_banks_movrel, tableid, AmountPaid FROM sl_banks_movrel WHERE tablename = 'bills' AND ID_banks_movements = '".$in{'id_banks_movements'}."';");
				while (my ($id_banks_movrel, $id_bills, $rel_amount) = $sth3->fetchrow() ){

					if($tvars > 0) {

						#########
						######### 3.2) Cancelacion sl_movements
						#########
						my ($sth) = &Do_SQL("SELECT ID_vars, Definition_En FROM sl_vars WHERE VName = 'Bank_Movements_Applied' AND VValue = '".$in{'id_banks_movements'}."' AND SubCode = '". $id_bills ."';");
						while (my ($id_vars, $id_movements) = $sth->fetchrow()) {

							#########
							######### 3.2.1 Movimientos contables, Se debe hacer reversa
							#########
							my @ary_movs = split(/,/, $id_movements);
							for (0..$#ary_movs){

								my $this_id_movements = int($ary_movs[$_]);
								if($this_id_movements){

									#########
									######### 3.2.1.1 Movimientos contables ya posteados, Se debe hacer reversa
									#########
									my $applied_movement = &Do_selectinsert('sl_movements', "ID_movements = '$this_id_movements'", "", "", %overwrite_movs);
									&Do_SQL("UPDATE sl_movements SET Effdate = CURDATE(), Credebit = IF(Credebit = 'Debit','Credit','Debit'), tablerelated = 'sl_banks_movements', ID_tablerelated = '$new_id_banks_movements', Date = CURDATE(), Time = CURTIME(), ID_admin_users = '$usr{'id_admin_users'}' WHERE ID_movements = '$applied_movement';");
									$tmovs++;

								}

							}
							&Do_SQL("INSERT INTO sl_banks_movements_notes SET ID_banks_movements = '$new_id_banks_movements', Notes = 'Bill: $id_bills\nMovs:\n". $id_movements ."', Type = 'Low', Date = CURDATE(), Time = CURTIME(), ID_admin_users = '$usr{'id_admin_users'}';");
							&Do_SQL("DELETE FROM sl_vars WHERE ID_vars = '$id_vars';");

						} ## while sl_movements

					}

					#########
					######### 3.3) Cancelacion sl_movrel
					#########
					if($tmovs){

						my $new_id_banks_movrel = &Do_selectinsert('sl_banks_movrel', "ID_banks_movrel = '$id_banks_movrel'", "", "", %overwrite_movrel);
						&Do_SQL("UPDATE sl_banks_movrel SET Date = CURDATE(), Time = CURTIME() WHERE ID_banks_movrel = '$new_id_banks_movrel';");
						$movrel_amount += $rel_amount;

						#########
						######### 3.4 Bill
						#########
						my ($sth_bills) = &Do_SQL("SELECT amount FROM sl_bills WHERE ID_bills = '". $id_bills ."';");
						my ($amount_bill)= $sth_bills->fetchrow();

						if ( $rel_amount == $amount_bill ){

							#########
							######### 3.4.1 Bill Processed
							#########
							&Do_SQL("UPDATE sl_bills SET Status = 'Processed' WHERE ID_bills = '". $id_bills ."' LIMIT 1;");

						}elsif( $rel_amount < $amount_bill ){

							#########
							######### 3.4.2 Bill Partly Paid
							#########
							&Do_SQL("UPDATE sl_bills SET Status = 'Partly Paid' WHERE ID_bills = '". $id_bills ."' LIMIT 1;");
						}

					}else{

						&Do_SQL("UPDATE sl_banks_movements SET Status =  'Cancelled' WHERE ID_banks_movements = '$new_id_banks_movements';");

					} ## tmovs > 0
					
				} ## while movrel


				#########
				######### 4) Movimiento bancario
				#########
				if ($movrel_amount > 0){

					if( abs($movrel_amount - $in{'amount'}) > 1){

						## 4.1) Update Amount
						&Do_SQL("UPDATE sl_banks_movements SET Amount = $movrel_amount WHERE ID_banks_movements = '". $new_id_banks_movements ."';");

					}

					#########
					######### 5) Notas
					#########
					&Do_SQL("INSERT INTO sl_banks_movements_notes SET ID_banks_movements = '". $in{'id_banks_movements'}."', Notes = '". &trans_txt('fin_banks_movements_payment_cancelled') ."', Type = 'Cancel', Date = CURDATE(), Time = CURTIME(), ID_admin_users = '$usr{'id_admin_users'}';");
					$va{'message'} = &trans_txt('fin_banks_movements_payment_cancelled') . qq|<a href=/cgi-bin/mod/admin/dbman?cmd=fin_banks_movements&view=$new_id_banks_movements"> $new_id_banks_movements </a>|;
					$in{'db'} = "sl_banks_movements";
					&auth_logging('fin_banks_movements_payment_cancelled', $in{'id_banks_movements'});
					delete($va{'cancel_btn'});
					$in{'status'} = 'Cancelled';

				}

				&Do_SQL("COMMIT;");

			}else{
				$va{'message'} = &trans_txt('fin_banks_movements_payment_not_cancelled');
				&Do_SQL("ROLLBACK;");
			}

		} ## action cancel

	} ## !&payment_is_canceled
	
	##################################
	##################################
	##################################
	### 
	###	Delete Banks Movements
	###
	##################################
	##################################
	##################################
	if ($in{'action'} and $in{'delete'} and $in{'id_banks_movements'}) {
		if (!&check_permissions('fin_banks_movements_delete','','')){
			$va{'message'} = &trans_txt('unauth_action');
		}else{
			&Do_SQL("START TRANSACTION;");
			&Do_SQL("DELETE FROM sl_banks_movements WHERE ID_banks_movements = '".$in{'id_banks_movements'}."';");
			&Do_SQL("DELETE FROM sl_banks_movrel WHERE ID_banks_movements = '".$in{'id_banks_movements'}."';");
			&Do_SQL("DELETE FROM sl_banks_movements_notes WHERE ID_banks_movements = '".$in{'id_banks_movements'}."';");
			&Do_SQL("DELETE FROM sl_movements WHERE tableused = 'sl_banks_movements' AND ID_tableused ='".$in{'id_banks_movements'}."';");
			&Do_SQL("COMMIT;");
			
			$va{'message'} = &trans_txt('fin_banks_movements_deleted');
		}

	}

	$in{'id_invoices'} = &Do_SQL("SELECT ID_invoices FROM cu_customers_payments_trans INNER JOIN cu_invoices using(ID_invoices)  WHERE ID_banks_movements = $in{'id_banks_movements'} AND cu_invoices.`Status` = 'Certified' LIMIT 1")->fetchrow();
	if($in{'id_invoices'} > 0){
		$va{'invoices_link'} = qq|<a href="/finkok/Facturas/?action=showPDF&id_invoices=$in{'id_invoices'}&e=$in{'e'}" target="_blank"><img src="/finkok/common/img/pdf.gif" title="Payment Invoice PDF" alt="PDF" border="0"></a>|;
		$va{'invoices_link'} .= qq|<a href="/finkok/Facturas/?action=showXML&id_invoices=$in{'id_invoices'}&e=$in{'e'}" target="_blank"><img src="/finkok/common/img/xml.gif" title="Payment Invoice XML" alt="XML" border="0"></a>|;
	}
	
	

}


#############################################################################
#############################################################################
#   Function: loading_fin_banks_movements
#
#       Es: Procesa datos de sl_banks_movements antes de ser cargados por la accion view
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
sub loading_fin_banks_movements {
#############################################################################
#############################################################################
	## Validamos si este movimiento es editable
	if ($in{'id_banks_movements'}) {
		my $sth=&Do_SQL("SELECT COUNT(*)movs FROM sl_banks_movrel WHERE ID_banks_movements=".$in{'id_banks_movements'}.";");
		my $movs = $sth->fetchrow_array;
		if ($movs > 0) {		
			$va{'restrict_type'} = 'disabled="disabled"';
			$va{'restrict_amount'} = 'disabled="disabled"';

			if($in{'consdate'} ne '') {
				$va{'restrict_id_banks'} = 'disabled="disabled"';
				$va{'restrict_bankdate'} = 'disabled="disabled"';
				$va{'restrict_consdate'} = 'disabled="disabled"';
			}
		}
	}
}

#############################################################################
#############################################################################
#   Function: validate_fin_banks_movements
#
#       Es: Procesa datos de sl_banks_movements antes de ser cargados para su edicion
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
sub validate_fin_banks_movements {
#############################################################################
#############################################################################	
	## Validamos si este movimiento es editable
	if ($in{'id_banks_movements'}) {
		my $sth=&Do_SQL("SELECT COUNT(*)movs FROM sl_banks_movrel WHERE ID_banks_movements=".$in{'id_banks_movements'}.";");
		my $movs = $sth->fetchrow_array;
		if ($movs > 0) {
			my $sth2=&Do_SQL("SELECT * FROM sl_banks_movements WHERE ID_banks_movements=".$in{'id_banks_movements'}.";");
			my $rec=$sth2->fetchrow_hashref;
			$in{'type'}=$rec->{'Type'};
			$in{'amount'}=$rec->{'Amount'};

			if($rec->{'ConsDate'} ne '' and $rec->{'ConsDate'} ne '0000-00-00') {

				$in{'id_banks'}=$rec->{'ID_banks'};
				$in{'bankdate'}=$rec->{'BankDate'};
				$in{'consdate'}=$rec->{'ConsDate'};

			}
		}
	}
}
#############################################################################
#############################################################################
#   Function: view_fin_banks
#
#       Es: View de Banks
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
sub view_fin_banks {
#############################################################################
#############################################################################

	
}

#############################################################################
#############################################################################
#   Function: validate_fin_xcharges
#
#       Es: Modifica el porcentaje del impuesto en caso de ser mayor a 1
#       En: Modifies the tax percentage, if this is greater than 1
#
#    Created on: 
#
#    Author: Jonathan Alcantara
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
#
sub validate_fin_xcharges {
	my $err;
	if($in{'tax_percent'} > 1){
		$in{'tax_percent'} = $in{'tax_percent'}/100;
	}
	return $err;
}

1;
