
#############################################################################
#############################################################################
#   Function: bills_to_processed
#
#       Es: Revisa y en su caso pasa un Bill de Expenses a Processed
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
#      - id_bills: ID_bills
#      - currency_exchange: Currency Exchange
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
sub bills_to_processed {
#############################################################################
#############################################################################

	my ($id_bills,$currency_exchange) = @_;

	# Bills Expenses && Credit -- and $in{'type'} ne 'Credit'
	if ($in{'type'} ne 'Deposit' and $in{'type'} ne 'Debit' and !&bills_pos_detection($id_bills)) {

		($in{'id_segments'}) and (delete($in{'id_segments'}));
		my ($sth) = &Do_SQL("SELECT sl_bills.Amount BillAmount, SUM(sl_bills_expenses.Amount)Amount, COUNT(*) AS nlines, IF(ID_segments IS NULL,0,ID_segments) AS ID_segments FROM sl_bills INNER JOIN sl_bills_expenses USING(ID_bills) WHERE ID_bills='$id_bills';");
		my ($amount_bill, $amount_lines, $no_lines, $ids) = $sth->fetchrow_array();
		
		$in{'id_segments'} = $ids;
		if ($no_lines > 0 and $amount_lines > 0 and ($amount_bill==$amount_lines or $in{'batch_forced'}) ){

			my $movs = 0;
			if($cfg{'acc_accural_based'}) {
				my ($sth) = &Do_SQL("SELECT COUNT(*) FROM sl_movements WHERE ID_tableused = '$id_bills' AND tableused = 'sl_bills' AND Status NOT IN ('Inactive');");
				$movs = $sth->fetchrow();
			}

			if(!$movs or $in{'batch_forced'}){

				my $upd = 0;
				if(!$in{'batch_forced'}) {
					my ($sth) = &Do_SQL("UPDATE sl_bills SET Status = 'Processed',AuthBy = '$usr{'id_admin_users'}' WHERE ID_bills = '$id_bills' LIMIT 1;");
					$upd = $sth->rows();
				}

				if ( $upd == 1 or $in{'batch_forced'}) {

					# grabar en el log
					&auth_logging('mer_bills_toprocessed',$id_bills);
					$va{'message'} = &trans_txt('mer_bills_toprocessed');
					$in{'status'} = 'Processed';

					if($cfg{'acc_accural_based'}) {

						###############################
						###############################
						### Mov Contables al reconocer la deuda y el credito
						###############################
						###############################
						my ($sth) = &Do_SQL("SELECT Category FROM sl_bills INNER JOIN sl_vendors USING(ID_vendors) WHERE ID_bills = '$id_bills';");
						my ($vtype) = $sth->fetchrow();

						my $sum_amount = 0;
						#### Si es tipo credit, se voltean cargo y abono
						my $flip_this_bill = $in{'type'} ne 'Credit' ? 0 : 1;
						my ($sth) = &Do_SQL("SELECT ID_accounts, Amount, IF(ID_segments > 0, ID_segments,0), LOWER(Deductible) FROM sl_bills_expenses WHERE ID_bills = '$id_bills' /*AND Amount > 0*/ ORDER BY Amount DESC,ID_bills_expenses, Related_ID_bills_expenses");
						while(my ($id_accounts, $amount, $id_segments, $deductible) = $sth->fetchrow() ) {

							$sum_amount += $amount;
							my @params = ($id_bills,$id_segments,$deductible,$id_accounts,$amount,$currency_exchange,$flip_this_bill);
							&accounting_keypoints('bills_expenses_record_'. $vtype, \@params );

						}
						
					} ## if acc_accural_based
				}
			} else {	
				$va{'message'} = &trans_txt('mer_bills_movsalready');
			}
		
		} else {

			#########################
			#########################
			###
			### No cumple con los requisitos, pasar a Pending
			###
			#########################
			#########################

			my ($sth) = &Do_SQL("UPDATE sl_bills SET Status = 'Pending', AuthBy = NULL WHERE ID_bills = '$id_bills' LIMIT 1;");
			$va{'message'} = &trans_txt('bills_amounts_not_match');
		}
	}else {
		#########################
		#########################
		###
		### Pasa a Processed no contabiliza
		###
		#########################
		#########################

		my ($sth) = &Do_SQL("UPDATE sl_bills SET Status = 'Processed',AuthBy = '$usr{'id_admin_users'}' WHERE ID_bills = '$id_bills' LIMIT 1;");
		if ($sth->rows() == 1) {
			$in{'status'} = 'Processed';

			# grabar en el log
			&auth_logging('mer_bills_toprocessed',$id_bills);
			$va{'message'} = &trans_txt('mer_bills_toprocessed');
		}
	}
}


#############################################################################
#############################################################################
#   Function: get_layout_load_bank_payments
#
#       Es: Devuelve cadena con layout para pago en Banorte
#       En: 
#
#
#    Created on: 2017-03-31
#
#    Author: _RB_
#
#    Modifications:
#
#
#   Parameters:
#
#      - Date: Date
#      - currency: Currency 
#      
#
#  Returns:
#
#      - None
#
#   See Also:
#
#      <>
#
sub get_layout_load_bank_payments {
#############################################################################
#############################################################################

	my ($id_vendors, $this_amount, $this_operation_type) = @_;

	my $txt_data; 
	$this_amount = 0 if !$this_amount;
	my $bankdate = $in{'bankdate'} ? $in{'bankdate'} : &get_sql_date();
	&load_cfg('sl_banks');
	my (%bankinfo) = &get_record('ID_banks', $in{'id_banks'},'sl_banks');
	$bankinfo{'bankname'} = lc($bankinfo{'bankname'});
	
	my $currency_from = $bankinfo{'currency'} eq 'MX$' ? 1 : 2;
	my $currency_to = $currency_from;

	my $modquery = $id_vendors ? "AND sl_vendors.ID_vendors = ".$id_vendors ." " : '';
	my ($sth) = &Do_SQL("SELECT 
							COUNT(*) 
						FROM 
							sl_bills INNER JOIN sl_vendors ON sl_bills.ID_vendors = sl_vendors.ID_vendors 
						WHERE 
							1
							". $modquery ." 
							AND sl_bills.Status = 'To Pay'
							AND sl_bills.Amount > 0
							AND sl_vendors.PaymentMethod = 'Wire Transfer'
							AND '". $bankinfo{'currency'} ."' = sl_bills.Currency;");
	my ($total) = $sth->fetchrow();

	if($total) {

		#$csv_data = qq|"Oper","Clave ID","Cuenta Origen","Cuenta/CLABE destino","Importe","Referencia","Descripción","RFC Ordenante","IVA","Fecha aplicación","Instrucción de pago","Clave tipo cambio"\n|;
		my $sth2 = &Do_SQL("SELECT 
								cu_company_legalinfo.Name AS CompanyName
								, cu_company_legalinfo.RFC AS CompanyRFC
								, sl_vendors.BankName
								, sl_vendors.BankID
								, sl_vendors.BankAccount
								, sl_vendors.BankWT
								, IF(". $this_amount ." > 0, ". $this_amount .", SUM(sl_bills.Amount) )AS Amount
								, DATE_FORMAT(CURDATE(), '%d%m%Y')AS Reference
								, LEFT(GROUP_CONCAT(sl_bills.Invoice), 40) AS Invoice 
								, LEFT(GROUP_CONCAT(sl_bills.Memo), 100) AS Memo
								, sl_vendors.ID_vendors
								, sl_vendors.CompanyName AS VendorName
								, sl_vendors.RFC AS VendorRFC
								, '0' AS Tax
								, ' ' AS VendorMail
								, DATE_FORMAT('". $bankdate ."', '%d%m%Y')AS BankDate
							FROM 
								sl_bills
							LEFT JOIN 
								cu_company_legalinfo ON PrimaryRecord = 'YES'
							INNER JOIN 
								sl_vendors ON sl_bills.ID_vendors = sl_vendors.ID_vendors
							WHERE 
								1
								". $modquery ." 
								AND sl_bills.Status = 'To Pay'
								AND sl_bills.Amount > 0
								AND sl_vendors.PaymentMethod = 'Wire Transfer'
								AND '". $bankinfo{'currency'} ."' = sl_bills.Currency
							GROUP BY
								sl_vendors.ID_vendors
							ORDER BY 
								sl_vendors.ID_vendors;");

		my $records = 0;
		RECORDS: while ($rec = $sth2->fetchrow_hashref()) {

			#01 = Trasp propias, 02 = Terceros ó Pago proveedores, 04 = SPEI, 05 = TEFs
			my $operation_type = '04';

			#$str .= qq|$rec->{'BankName'} =~ $bankinfo{'bankname'}\n|;
			if(lc($rec->{'BankName'}) =~ /$bankinfo{'bankname'}/){

				$rec->{'BankWT'} = $rec->{'BankAccount'};
				$operation_type = '02'; 

			}


			###
			## Only records same type
			###
			next RECORDS if $this_operation_type ne $operation_type;


			if(!$bankinfo{'subaccountof'}){

				## Bank Account Not Found
				$va{'message'} .= qq|1 (<a href="/cgi-bin/mod/[ur_application]/dbman?cmd=fin_banks&view=$in{'id_banks'}">$bankinfo{'bankname'} - $in{'id_banks'}</a>) : Bank Account Missing<br>|;
				last RECORDS;

			}if(!$rec->{'BankID'} or !$rec->{'Amount'}){

				## Required Data not found
				$va{'message'} .= qq|2 $rec->{'VendorName'} ($rec->{'VendorRFC'} - <a href="/cgi-bin/mod/[ur_application]/dbman?cmd=mer_vendors&view=$rec->{'ID_vendors'}">$rec->{'ID_vendors'}</a>) : ID $rec->{'BankID'} - WT $rec->{'BankWT'} - AM $rec->{'Amount'}<br>|;
				next RECORDS; 

			}elsif($operation_type =~ /^04/ and length($rec->{'BankWT'}) < 18){

				## SPEI value length invalid
				$va{'message'} .= qq|3 $rec->{'VendorName'} ($rec->{'VendorRFC'} - <a href="/cgi-bin/mod/[ur_application]/dbman?cmd=mer_vendors&view=$rec->{'ID_vendors'}">$rec->{'ID_vendors'}</a>) : $rec->{'BankWT'} Not CLABE Value<br>|; 
				next RECORDS;
				
			}

			$rec->{'Invoice'} =~ s/\t|,|-/ /g; $rec->{'Invoice'} =~  s/"|'|\\//g; $rec->{'Invoice'} = substr($rec->{'Invoice'},0,25);
			$rec->{'Memo'} =~ s/\t|,|-/ /g; $rec->{'Memo'} =~  s/"|\\//g; $rec->{'Memo'} = substr($rec->{'Memo'},0,65);

			## BankID to 13 chars must add trailing spaces
			$rec->{'BankID'} = sprintf("%-13s",$rec->{'BankID'});
			## BankID to 13 chars must add trailing spaces
			$rec->{'Invoice'} = sprintf("%-30s",$rec->{'Invoice'});
			## BankID to 70 chars must add trailing spaces
			$rec->{'Memo'} = sprintf("%-70s",$rec->{'Memo'});
			## CompanyRFC to 13 chars must add trailing spaces
			$rec->{'CompanyRFC'} = sprintf("%-13s",$rec->{'CompanyRFC'});
			## VendorMail to 39 chars must add trailing spaces
			$rec->{'VendorMail'} = sprintf("%-39s",$rec->{'VendorMail'});

			## Bank Accounts to 20 digits must add leading zeros
			$rec->{'BankWT'} = sprintf("%020s",$rec->{'BankWT'});
			$bankinfo{'subaccountof'} = sprintf("%020s",$bankinfo{'subaccountof'});
			## Amount to 14 digits must add leading zeros. Decimals must be last two
			$rec->{'Amount'} = &round($rec->{'Amount'}, 2);
			my @tmp_amt = split(/\./, $rec->{'Amount'}); 
			$tmp_amt[1] = '00' if !$tmp_amt[1]; $tmp_amt[1] .= '0' if length($tmp_amt[1]) == 1;
			$rec->{'Amount'} = sprintf("%014s", join('',@tmp_amt));
			## Reference to 10 digits must add leading zeros
			$rec->{'Reference'} = sprintf("%010s",$rec->{'Reference'});
			## Tax to 14 digits must add leading zeros
			$rec->{'Tax'} = &round($rec->{'Tax'}, 2);
			my @tmp_tax = split('.', $rec->{'Tax'});
			$tmp_tax[1] = '00' if !$tmp_tax[1]; $tmp_tax[1] = sprintf("%-02s", $tmp_tax[1]);
			$rec->{'Tax'} = sprintf("%014s", join('',@tmp_tax));
			## Bank Date to 8 digits must add leading zeros
			$rec->{'BankDate'} = sprintf("%08s",$rec->{'BankDate'});

			$records++;

			# 				  Operación			Clave ID		  Cuenta Destino		Importe			  Referencia(10)	  Descripcion(30)	    MOrigen	MDes	RFC				IVA	Mail  Fecha aplica instruccion de pago(70)
			#$csv_data .= qq|"$operation_type","$rec->{'BankID'}","$bankinfo{'subaccountof'}","$rec->{'BankWT'}","$rec->{'Amount'}","$rec->{'Reference'}","$rec->{'Invoice'}","$currency_from","$currency_to","$rec->{'CompanyRFC'}","$rec->{'Tax'}","$rec->{'VendorMail'}","$rec->{'BankDate'}","$rec->{'Memo'}"\n|;
			#$csv_data .= qq|"$operation_type","$rec->{'BankID'}","$bankinfo{'subaccountof'}","$rec->{'BankWT'}","$rec->{'Amount'}","$rec->{'Reference'}","$rec->{'Invoice'}","$rec->{'CompanyRFC'}","0","$bankdate","$rec->{'Memo'}","0"\n|;
			$txt_data .= $operation_type . $rec->{'BankID'} . $bankinfo{'subaccountof'} . $rec->{'BankWT'} . $rec->{'Amount'} . $rec->{'Reference'} . $rec->{'Invoice'} . $currency_from . $currency_to . $rec->{'CompanyRFC'} . $rec->{'Tax'} . $rec->{'VendorMail'} . $rec->{'BankDate'} . $rec->{'Memo'} . "\n";

		}

	}else{

		$va{'message'} .= trans_txt('nodata');

	}

	## Impresion de archivo CSV
	my $f = lc($cfg{"app_title"}) . '_' . lc($bankinfo{'shortname'}) . '_' . &get_sql_date();		
	$f =~ s/ /_/g;

	if(!$va{'message'}){
		
		return $txt_data;

	}else{

		return "ERROR<br>";

	}

}


#############################################################################
#############################################################################
#   Function: get_exchangerate
#
#       Es: Devuelve el tipo de cambio para una fecha determinada
#       En: 
#
#
#    Created on: 2015-06-11
#
#    Author: _RB_
#
#    Modifications:
#
#
#   Parameters:
#
#      - Date: Date
#      - currency: Currency 
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
sub get_exchangerate {
#############################################################################
#############################################################################

	my ($this_currency, $this_date) = @_;

	my $modsql = $this_date == 1 ? " Date = CURDATE()" : " Date = '". &filter_values($this_date) ."' ";

	##
	## Intentamos sacar el tipo de cambio
	my ($sth) = &Do_SQL("SELECT exchange_rate FROM sl_exchangerates WHERE Currency = '$this_currency' AND ". $modsql ." LIMIT 1;");
	my ($this_exchange_rate) = $sth->fetchrow();
	$this_exchange_rate = 0 if !$this_exchange_rate;

	return $this_exchange_rate;

}

1;