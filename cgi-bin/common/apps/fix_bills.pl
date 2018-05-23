#!/usr/bin/perl
#######################################################################
#######################################################################
#######################################################################

# 10208
# 10218
# 10272
# 10347
# 10370
# 10385
# 10390


#use strict;
#use Perl::Critic;
use DBI;
use DBIx::Connector;
use DBD::mysql;
use Cwd;


local ($dir) = getcwd;
local ($in{'e'}) = 11;
local ($cfg{'starting_date_e2'}) = '2013-08-01';
local ($cfg{'starting_date_e3'}) = '2013-05-15';
local ($usr{'id_admin_users'}) = 1;
local ($in{'batch_forced'}) = 1;
local ($cfg{'ida_banks'}) = '19,23,30,31,35,36,37,38,40,48';
local ($cfg{'ida_tax_payable'}) = '124';
local ($cfg{'ida_tax_paid'}) = '127';
local ($cfg{'tax_pct'}) = .16;
local ($cfg{'reset'}) = 1;

chdir($dir);

# Required Libraries
# --------------------------------------------------------
eval {
	require ('../subs/auth.cgi');
	require ('../subs/sub.base.html.cgi');
	require ('../subs/sub.func.html.cgi');
	#require ('../../mod/wms/admin.html.cgi');
	#require ('../../mod/wms/admin.cod.cgi');
	#require ('../../mod/wms/sub.base.html.cgi');
	#require ('../../mod/wms/sub.func.html.cgi');
};
if ($@) { &cgierr ("Error loading required Libraries",300,$@); }

eval { &main; };
if ($@) { &cgierr("Fatal error,301,$@"); }

exit;

#################################################################
#################################################################
#	Function: main
#
#   		Main function: Calls execution scripts. Script called from cron task
#
#	Created by: _Roberto Barcenas_
#
#
#	Modified By:
#
#
#   	Parameters:
#
#
#   	Returns:
#
#
#
#   	See Also:
#
sub main {
#################################################################
#################################################################

	$|++;
	&connect_db;
	&process_bills;
	&disconnect_db;

}


#############################################################################
#############################################################################
#   Function: process_bills
#
#       Es: Procesa archivo de bills para transicion
#       En: 
#
#    Created on: 07/10/2008  16:21:10
#
#    Author: _RB_
#
#    Modifications:
#
#   Parameters:
#
#
#  Returns:
#
#
#   See Also:
#
#
sub process_bills {
############################################################################# 
#############################################################################
	
	
	##################################################################
	##################################################################
	##################################################################
	##############
	############## NOTA. No olvidar indicar la empresa en la linea 23
	##############
	##################################################################
	##################################################################
	##################################################################


	# ,
	my $this_type = "Bill"; my $these_bills = '4145'; my $str_bills = " AND ID_tableused IN (4145) ";

	my $str_journal_locked = 'AND ID_journalentries NOT IN (39)';
	$str_journal_locked .= $str_deposits if $this_type eq 'Deposit';
	$str_journal_locked .= $str_bills  if $this_type eq 'Bill';


	($cfg{'reset'}) and (&Do_SQL("UPDATE sl_movements SET ID_journalentries = 0 WHERE ID_journalentries > 0 $str_journal_locked AND Category IN('Gastos','Anticipo Clientes','Pagos','Aplicacion Anticipos AP');") );
	($cfg{'reset'} and $this_type =~ /Deposit/) and (print "/*Reseting Deposit*/\n") and (&Do_SQL("/*Reseting Deposit*/ DELETE FROM sl_movements WHERE tableused = 'sl_vendors' AND Category = 'Pagos' AND (ID_journalentries IS NULL OR ID_journalentries >= 0) $str_journal_locked;"));

	#print "Content-type: text/html\n\n";
	my ($query_f) = "SELECT ID_bills,tmp.Type,tmp.Date,ID_vendors,tmp.Category,CompanyName,
					Memo,Currency,currency_exchange,tmp.Status,tmp.Amount, tmp.SubType,Deductible,
					IF(COUNT(*) IS NULL,0,COUNT(*)) AS QtyMovs,
					IF(SUM(IF(tableused = 'sl_bills',sl_movements.Amount,0)) IS NULL,0,SUM(IF(tableused = 'sl_bills',sl_movements.Amount,0))) AS AmtMovs,
					SUM(IF(tableused = 'sl_bills' AND Credebit = 'Debit',1,0))AS QtyDebits,
					SUM(IF(tableused = 'sl_bills' AND Credebit = 'Debit',sl_movements.Amount,0))AS AmtDebits,
					SUM(IF(tableused = 'sl_bills' AND Credebit = 'Credit',1,0))AS QtyCredits,
					SUM(IF(tableused = 'sl_bills' AND Credebit = 'Credit',sl_movements.Amount,0))AS AmtCredits,
					SUM(IF(tableused = 'sl_bills' AND Credebit = 'Debit' AND ID_accounts IN(197,198,201,202),1,0))AS VendorDebits,
					SUM(IF(tableused = 'sl_bills' AND Credebit = 'Credit' AND ID_accounts IN(197,198,201,202),1,0))AS VendorCredits,
					SUM(IF(tableused = 'sl_bills' AND sl_movements.Amount < 0,1,0)) AS NegMovs
					FROM
					(
						SELECT 
						sl_bills.ID_bills,sl_bills.Type,sl_bills.Date,
						sl_vendors.ID_vendors,sl_vendors.Category,CompanyName,Memo,sl_bills.Currency,
						sl_bills.currency_exchange,sl_bills.Status,
						ROUND(IF(
							SUM(sl_bills_expenses.Amount * IF(currency_exchange > 0,currency_exchange,1)) > 0,
							SUM(sl_bills_expenses.Amount * IF(currency_exchange > 0,currency_exchange,1)),
							IF(
								SUM(sl_bills_pos.Amount * IF(currency_exchange > 0,currency_exchange,1)) > 0,
								SUM(sl_bills_pos.Amount * IF(currency_exchange > 0,currency_exchange,1)), 
								sl_bills.Amount * IF(currency_exchange > 0,currency_exchange,1)
							)
						),2)AS Amount,
						IF(
							SUM(sl_bills_expenses.Amount * IF(currency_exchange > 0,currency_exchange,1)) > 0,
							'Expenses',
							IF(
								SUM(sl_bills_pos.Amount * IF(currency_exchange > 0,currency_exchange,1)) > 0,
								'PO', 
								'Bill'
							)
						)AS SubType,
						Deductible
						FROM sl_bills 
						LEFT JOIN sl_bills_expenses USING(ID_bills)
						LEFT JOIN sl_bills_pos USING(ID_bills)
						INNER JOIN sl_vendors USING(ID_vendors)
						WHERE 1
						AND BillDate >= '2013-05-15'
						/*AND BillDate <= '2013-12-10' */
						AND IF('$this_type' <> '', sl_bills.Type = '$this_type',1)
						AND sl_bills.ID_bills IN ($these_bills)  /*  Bills / Deposits */
						/*AND sl_bills.Status = 'Pending'*/
						GROUP BY sl_bills.ID_bills
						ORDER BY sl_bills.ID_bills
					)tmp
					LEFT JOIN sl_movements ON ID_bills = ID_tableused
					WHERE 1 
					GROUP BY ID_bills
					ORDER BY ID_bills;";

	my ($sth) = &Do_SQL($query_f);
	print "$query_f\n\n";

	my $i=0;
	BILL: while (my ($id_bills, $type, $date, $id_vendors, $vendor_category, $company, $memo, $currency, $currency_exchange, $status, $amount, $subtype, $deductible, $qty_movs, $amt_movs, $qty_debits, $amt_debits, $qty_credits, $amt_credits, $vendors_debits_qty, $vendors_credits_qty, $neg_movs) = $sth->fetchrow() ) {
		
		++$i;	
		my $vendor_deposits = 0;my $ok = 'OK';my $ok_pr = 'OK';my $ok_pa = 'OK';my $ok_mo = 'OK';my $x;
		my $this_style = abs($amt_debits - $amt_credits) > 0 ? 'style="color:red"' : '';
		($this_style ne '' and $in{'export'}) and ($ok = 'Error');

		print "Row $i - $id_bills\n";
		#print "ID: $id_bills, T: $type, D: $date, IDV: $id_vendors, C: $company, M: $memo, C: $currency, CE: $currency_exchange, ST: $status, AM: $amount, DED: $deductible, QTY: $qty_movs, AMM: $amt_movs, QD: $qty_debits, AD: $amt_debits, QC: $qty_credits, AC: $amt_credits, VD: $vendors_debits_qty, VC: $vendors_credits_qty, NM: $neg_movs, VD: $vendor_deposits\n";
		
		###############################
		###############################
		###############################  Borrado de Contabilidad para reasignacion (solo aplica expenses)
		###############################
		###############################
		if($cfg{'reset'} and $type eq 'Bill' and $subtype ne 'PO') {

			my ($sth) = &Do_SQL("SELECT COUNT(*) FROM sl_movements WHERE ID_tableused = '$id_bills' AND tableused = 'sl_bills' AND (ID_journalentries > 0 OR ID_journalentries = '-1');");
			my ($posted) = $sth->fetchrow();

			print "Entering Expenses Bill\n";

			if(!$posted) {

				my $rquery = "/*Reseting Bill*/ DELETE FROM sl_movements WHERE ID_tableused = '$id_bills' AND tableused = 'sl_bills' AND (ID_journalentries IS NULL OR ID_journalentries = 0);";
				#  AND ( (ID_tablerelated = '$id_bills' AND tablerelated = 'sl_bills') OR Reference = 'Deposit: $id_bills')
				my ($sth) = &Do_SQL($rquery);
				my ($td) = $sth->rows();
				print "$rquery\nDeleted: $td\n";
				$vendors_debits_qty = 0;
				$vendors_credits_qty = 0;

			}else{
				print "Movements Posted Found, Skipping Reset\n";
			}

		}
		#exit;
		#########
		######### Proceso de Busqueda Pre Proceso General
		#########
		if($status =~ /Processed|Pending/){
			$status = &bill_upd($id_bills,$amount);
		}elsif($type eq 'Deposit' and $status =~ /Paid/){
			&deposit_upd($id_bills, $id_vendors, $amount);
		}elsif($type eq 'Bill' and $subtype eq 'PO'){
			print "TP0 ID: $id_bills\n";
			($x,$status,$vendors_credits_qty,$vendors_debits_qty) = &po_noninventory_upd($id_bills,$status,$vendors_credits_qty,$vendors_debits_qty);
		}

		if($type eq 'Deposit' and $status =~ /Paid/){

			#########
			######### Proceso de Busqueda para Deposits
			#########

			my ($sth) = &Do_SQL("SELECT BankDate FROM sl_bills INNER JOIN sl_banks_movrel ON ID_bills = tableid INNER JOIN sl_banks_movements USING(ID_banks_movements)  WHERE tableid = '$id_bills' AND tablename = 'bills';");
			my ($pdate) = $sth->fetchrow();

			if($pdate) {

				my ($sth) = &Do_SQL("SELECT ID_movements, Reference FROM sl_movements WHERE ID_tableused = '$id_vendors' AND tableused = 'sl_vendors' AND EffDate = '$pdate' AND Credebit = 'Credit' AND (Reference IS NULL OR Reference = '' OR Reference = 'Deposit: $id_bills') AND ABS(Amount - $amount) BETWEEN 0 AND 0.009 LIMIT 1;");
				my ($id_movements, $reference) = $sth->fetchrow();
				($id_movements) and ($vendor_deposits = 1);
				print "TPD ID: $id_bills\nMov: $id_movements\n";

			}

		}



		($status =~ /Processed|Paid/ and $type !~ /Deposit|Credit/ and  !$vendors_credits_qty) and ($ok = 'Error') and ($ok_pr = 'Error');
		($status eq 'Paid' and $type eq 'Deposit' and !$vendor_deposits)  and ($ok = 'Error') and ($ok_pa = 'Error');
		($status eq 'Paid' and $type !~ /Deposit|Credit/ and !$vendors_debits_qty )  and ($ok = 'Error') and ($ok_pa = 'Error');
		($neg_movs) and ($ok = 'Error') and ($ok_mo = 'Error');

		#print "aqui sigo\n";


		if($status =~ /Processed|Paid/){

			my ($amount, $bill_date, $id_admin_users);

			if($type !~ /Deposit|Credit/ and $subtype ne 'PO' and !$vendors_credits_qty) {

				print "TP1 ID: $id_bills\n";
				########################################################
				########################################################
				## BILLS PO/EXPENSES TO PROCESSED
				########################################################
				########################################################
			
				print "Bill To Process\n";	
				print "Searching Date in Log Processed\n";
				my ($sth) = &Do_SQL("SELECT LogDate,ID_admin_users FROM admin_logs WHERE Action = '$id_bills' AND tbl_name = 'sl_bills' AND (Message = 'mer_bills_toprocessed' OR Message = 'bills_processed') LIMIT 1;");
				($bill_date, $id_admin_users) = $sth->fetchrow();

				if(!$bill_date and $status eq 'Paid') {
					print "Searching Date in Log Paid\n";
					my ($sth) = &Do_SQL("SELECT LogDate,ID_admin_users FROM admin_logs WHERE Action = '$id_bills' AND tbl_name = 'sl_bills' and Message = 'bills_paid' LIMIT 1;");
					($bill_date, $id_admin_users) = $sth->fetchrow();

					if(!$bill_date){

						print "Extracting Date Same as BankDate\n";
						my ($sth) = &Do_SQL("SELECT BankDate, sl_bills.ID_admin_users FROM sl_bills INNER JOIN sl_banks_movrel ON ID_bills = tableid INNER JOIN sl_banks_movements USING(ID_banks_movements)  WHERE tableid = '$id_bills' AND tablename = 'bills';");
						($bill_date, $id_admin_users) = $sth->fetchrow();						

					}


				}

				if($bill_date) {
			
					### Llamamos a la funcion existente
					&bills_to_processed($id_bills,$currency_exchange);
					my $query_to_processed = "UPDATE sl_movements SET EffDate = '$bill_date', Date = '$bill_date', ID_journalentries = 0, ID_admin_users = '$id_admin_users' WHERE ID_tableused = '$id_bills' AND tableused = 'sl_bills' AND TIMESTAMPDIFF(SECOND,CONCAT(Date,' ',Time) , NOW()) BETWEEN 0 AND 5 AND ID_admin_users = '$usr{'id_admin_users'}';";
					&Do_SQL($query_to_processed);
					print "$query_to_processed\n";
				
				}else{
					print "Error: No date\n";	
				}
			}

			
			if($status =~ /Paid/ and $type !~ /Deposit|Credit/ and !$vendors_debits_qty) {

				print "TP2 ID: $id_bills\n";
				########################################################
				########################################################
				## BILLS PO/EXPENSES TO PAID
				########################################################
				########################################################

				print "Bill To Paid\n";
				#&cgierr($id_bills);
				#exit;
				&bills_to_paid($id_bills,$currency_exchange);
				#exit;
				
			}

			if($status =~ /Paid/ and $type eq 'Deposit' and !$vendor_deposits) {

				print "TPD ID: $id_bills\n";
				#exit;
				#next BILL;
				########################################################
				########################################################
				## BILLS DEPOSITS TO PAID
				########################################################
				########################################################

				print "Deposit To Paid\n";
				#&cgierr($id_bills);
				&deposits_to_paid($id_bills,$currency_exchange);
				sleep(2);
				#exit;
				
			}

			if($type eq 'Bill' and $subtype ne 'PO' and $currency ne $cfg{'acc_default_currency'}){

				########################################################
				########################################################
				## BILL EXPENSES PROFIT/LOST
				########################################################
				########################################################	
				print "$currency vs $cfg{'acc_default_currency'} - Check Paid\n";
				my @params = ($id_bills);
				&accounting_keypoints('bills_expenses_paid_' . lc($vendor_category), \@params );

			}


		}
		#exit if $x;
	}

	my $this_emp = $in{'e'} == 2 ? $cfg{'starting_date_e2'} : $cfg{'starting_date_e3'};
	my $fquery1 = "DELETE FROM sl_movements WHERE Amount = 0 AND (ID_journalentries IS NULL OR ID_journalentries = 0);";
	#my $fquery2 = "UPDATE sl_movements SET ID_journalentries = -1 WHERE EffDate < '". $this_emp ."' AND (ID_journalentries IS NULL OR ID_journalentries = 0);";
	print "\n\nBorrado Final de Datos en cero\n$fquery1\nMarcado de Movimientos pasados\n$fquery2\n\n";
	&Do_SQL($fquery1);
	#sleep(5);
	#&Do_SQL($fquery2);
	my ($sth) = &Do_SQL("UPDATE sl_movements INNER JOIN sl_accounts USING(ID_accounts) SET ID_segments = 0 WHERE Segment = 'No';");

}


#############################################################################
#############################################################################
#   Function: bills_to_paid
#
#       Es: Procesa un Bill (PO | Expenses) que ya esta pagado y no tiene Mov Contables
#       En: 
#
#    Created on: 07/10/2008  16:21:10
#
#    Author: _RB_
#
#    Modifications:
#
#   Parameters:
#
#
#  Returns:
#
#
#   See Also:
#
#
sub bills_to_paid {
#############################################################################
#############################################################################

	### Nota
	### this_pct si se debe usar sobre todo por los bills con valores negativos, 
	### en esos casos el positivo de la iteracion final da un porcentaje > 1
	### Si esto no funciona, entonces hay que sumar los negativos y restarlos al Amount de la ultima iteracion
	###

	### Nota 2
	### No funciona dejar el this_pct debido a que cada cobro toma en cuenta el 100% de los taxes como pagados
	### Es decir. Si el bill se liquida en varios pagos|depositos, el IVA se duplicara
	### 

	### Nota 3
	### La solucion fue quitar el this_pct y en la ultima iteracion sacar la suma del monto negativo
	### De tal manera que al monto mayor se le resta el negativo que es el que se pago a abono
	### 3528, 3301 (Negativos), 3488, 3634, 3635, 3636 (Varios Pagos Positivo)
	###


	my ($id_bills, $currency_exchange) = @_;
	my $x = 0; my $str;my $deposits = 0;
	my ($amount, $ida_banks, $bill_date, $id_admin_users,$str,$id_segments);
	my ($this_bill_type, $this_bill_vendor_category);


	########
	######## 1) Obtenemos el monto pagado
	########
	my $dquery = "/*Deposit Application*/ SELECT sl_bills_applies.ID_bills, sl_bills_applies.Amount AS Payment, sl_bills_applies.Amount / sl_bills.Amount AS Pct, sl_bills_applies.Date, sl_bills_applies.ID_admin_users FROM sl_bills INNER JOIN sl_bills_applies ON sl_bills.ID_bills = ID_bills_applied WHERE ID_bills_applied = '$id_bills' ORDER BY sl_bills_applies.Date,sl_bills_applies.Time,ID_bills_applies;";
	print "$dquery\n";
	my ($sth) = &Do_SQL($dquery);
	
	LINES: while( ($id_bills_original, $amount, $paid_pct, $bill_date, $id_admin_users) = $sth->fetchrow() ) {

		my $bill_type = &load_name('sl_bills','ID_bills',$id_bills_original,'Type');

		if($bill_type eq 'Credit'){
			print "Skipping Credit\n";
			return;
		}

		## Bill Deposit Data
		my ($sth) = &Do_SQL("SELECT Category,IF(sl_bills_expenses.ID_accounts > 0 ,sl_bills_expenses.ID_accounts,sl_bills.ID_accounts) AS ID_accounts,sl_banks_movements.currency_exchange FROM sl_bills LEFT JOIN sl_bills_expenses USING(ID_bills) INNER JOIN sl_vendors USING(ID_vendors) INNER JOIN sl_banks_movrel ON tableid = sl_bills.ID_bills AND tablename = 'bills' INNER JOIN sl_banks_movements USING(ID_banks_movements) WHERE ID_bills = '".$id_bills_original."';");
		my($vendor_category,$ida_deposit,$currency_exchange) = $sth->fetchrow();
		$currency_exchange = 1 if !$currency_exchange;
		$ida_deposit = 0 if !$ida_deposit;

		(!$this_bill_type) and ($this_bill_type = $bill_type) ;
		(!$this_bill_vendor_category) and ($this_bill_vendor_category = $vendor_category);

		my $str_pos;my $str_bills;my $str;
		my $amount_derived = $amount;
		my $amt_negative = 0;

		#my ($sth) = &Do_SQL("SELECT IF(ID_purchaseorders IS NULL,0,ID_purchaseorders) AS ID_po, IF(ID_bills_expenses IS NULL,0,ID_bills_expenses) AS ID_expense,IF(ID_segments IS NULL,0,ID_segments)AS ID_segments FROM sl_bills  LEFT JOIN sl_bills_pos USING(ID_bills) LEFT JOIN sl_bills_expenses USING(ID_bills) WHERE sl_bills.ID_bills = '".$id_bills."'HAVING ID_po > 0 OR ID_expense > 0 ORDER BY sl_bills_pos.Amount, sl_bills_expenses.Amount;");
		my ($sth) = &Do_SQL("SELECT IF(ID_purchaseorders > 0 AND sl_bills_pos.Amount > 0,ID_purchaseorders,0) AS ID_po, IF(ID_bills_expenses > 0 AND sl_bills_expenses.Amount > 0,ID_bills_expenses,0) AS ID_expense,IF(ID_segments IS NULL,0,ID_segments)AS ID_segments FROM sl_bills  LEFT JOIN sl_bills_pos USING(ID_bills) LEFT JOIN sl_bills_expenses USING(ID_bills) WHERE sl_bills.ID_bills = '".$id_bills."' HAVING ID_po > 0 OR ID_expense > 0 ORDER BY sl_bills_pos.Amount, sl_bills_expenses.Amount;");

		my $rows = $sth->rows();
		print "Rows - $rows\n";
		my $this_type; my $j=0;

		while(my($id_po, $id_expenses, $ids) = $sth->fetchrow()) {

			++$j;
			++$deposits;

			$id_segments = $ids;
			######
			###### No hay Bill Date?
			######
			if(!$bill_date or !$id_admin_users) {

				my ($sth) = &Do_SQL("SELECT LogDate,ID_admin_users FROM admin_logs WHERE Action = '$id_bills' AND tbl_name = 'sl_bills' and Message = 'bills_paid' LIMIT 1;");
				($bill_date, $id_admin_users) = $sth->fetchrow();
				($id_admin_users) and ( $usr{'id_admin_users'} = $id_admin_users);
			}


			if($id_po) {

				(!$this_type) and ($this_type = 'po');
				($j == $rows ) and ($amt_negative = &load_bill_amt_negative($id_bills,'sl_bills_pos'));

				### Pago de PO
				my ($sth) = &Do_SQL("SELECT  
									SUM(IF(ID_purchaseorders = '$id_po',Amount,0)) / SUM(Amount) AS PctPaid , 
									( (SUM(IF(ID_purchaseorders = '$id_po',Amount,0)) - $amt_negative ) / SUM(Amount)) * $paid_pct
									FROM sl_bills_pos WHERE ID_bills = '". $id_bills ."';");
				my($pct , $this_pct) = $sth->fetchrow();
				#$this_pct = round($this_pct,3);
				

				my $this_amount = $j < $rows ? round($this_pct * $amount ,3) : $amount_derived;
				$amount_derived -= $this_amount;
				$str .= "$j - $rows -- $amount : $pct ($pct * $paid_pct = $this_pct) = $this_amount - $amount_derived\n";

				my @params = ($id_po,$id_bills_original,0,$this_amount,$currency_exchange);
				#&cgierr('po_apply_' . lc($bill_type) . '_'. lc($vendor_category) . " --- $id_po,0,$this_amount,$currency_exchange");
				&accounting_keypoints('po_apply_' . lc($bill_type) . '_'. lc($vendor_category), \@params );
				&Do_SQL("INSERT INTO sl_purchaseorders_notes SET ID_purchaseorders = '$id_po', Notes='Deposit Applied\nOriginal Amount: $this_amount\nCurrency Exchange: $currency_exchange\nTotal Paid: ".round($this_amount *  $currency_exchange,3)." ',Type='Low', Date = '$bill_date', Time = CURTIME(), ID_admin_users='$usr{'id_admin_users'}' ");
				$str_pos .= "$id_po,";

			}else{

				(!$this_type) and ($this_type = 'expenses');
				($j == $rows ) and ($amt_negative = &load_bill_amt_negative($id_bills,'sl_bills_expenses'));

				##################
				### Pago de Expense
				##################
				##################
				my ($sth) = &Do_SQL("SELECT 
									SUM(IF(ID_bills_expenses = '$id_expenses',Amount,0)) / SUM(Amount) AS PctPaid,
									( (SUM(IF(ID_bills_expenses = '$id_expenses',Amount,0)) - $amt_negative ) / SUM(Amount)) * $paid_pct
									FROM sl_bills_expenses WHERE ID_bills = '". $id_bills ."';");
				my($pct, $this_pct) = $sth->fetchrow();
				#$this_pct = round($this_pct,3);
				

				my $this_amount = $j < $rows ? round($this_pct * $amount ,3) : $amount_derived;
				$amount_derived -= $this_amount;
				$str .= "$amount : $pct ($pct * $paid_pct = $this_pct) = $this_amount - $amount_derived\n";

				my @params = ($id_bills,$id_bills_original,0,$ida_deposit,$this_amount,$currency_exchange,$this_pct);
				#&cgierr('bills_expenses_apply_' . lc($bill_type) . '_'. lc($vendor_category) . " -- $id_expenses,$id_bills_original,0,$ida_deposit,$this_amount,$currency_exchange,$pct");
				&accounting_keypoints('bills_expenses_apply_' . lc($bill_type) . '_'. lc($vendor_category), \@params );
				my $exchange_rate = $currency_exchange > 0 ? $currency_exchange : 1;
				&Do_SQL("INSERT INTO sl_bills_notes SET ID_bills = '$id_bills_original', Notes='Deposit Applied\nTo Bill: $id_bills\nOriginal Amount: $this_amount\nCurrency Exchange: currency_exchange\nTotal Paid: ".round($this_amount * $exchange_rate,3)." ',Type='Low', Date = '$bill_date', Time = CURTIME(), ID_admin_users='$usr{'id_admin_users'}' ");
				&Do_SQL("INSERT INTO sl_bills_notes SET ID_bills = '$id_bills', Notes='Deposit Applied\nFrom Bill: $id_bills_original\nOriginal Amount: $this_amount\nCurrency Exchange: currency_exchange\nTotal Paid: ".round($this_amount * $exchange_rate,3)." ',Type='Low', Date = '$bill_date', Time = CURTIME(), ID_admin_users='$usr{'id_admin_users'}' ");
				$str_bills .= "$id_bills,";

			} ## IF date/amount

		}
		chop($str_pos);
		chop($str_bills);
		print "String: $str\n";

		my $modquery = $str_pos ne '' ? "ID_tableused IN ($str_pos) AND tableused = 'sl_purchaseorders'" : "ID_tableused IN ($str_bills)  AND tableused = 'sl_bills'";
		my $query_to_paid = "UPDATE sl_movements SET EffDate = '$bill_date', ID_segments = '$id_segments', Date = '$bill_date', ID_journalentries = 0, tablerelated = 'sl_bills', ID_tablerelated = '$id_bills_original', ID_admin_users = '$id_admin_users' WHERE $modquery AND TIMESTAMPDIFF(SECOND,CONCAT(Date,' ',Time) , NOW()) BETWEEN 0 AND 5 AND ID_admin_users = '$usr{'id_admin_users'}';";
		&Do_SQL($query_to_paid);
		print "$j -- /* AA */ $query_to_paid\n";	
		#exit;

	}	

	if ($deposits) {

		&accounting_group_amounts('sl_bills',$id_bills);
		print "Deposits Applied\n";
		#exit;
		#return;
	}


	$str='';
	my $bquery = "/*Bank Payment*/SELECT ID_banks_movrel,AmountPaid, AmountPaid / sl_bills.Amount AS Pct, sl_accounts.ID_accounts, sl_banks_movements.currency_exchange, sl_banks_movrel.Date, sl_banks_movements.BankDate, sl_banks_movrel.ID_admin_users FROM sl_bills INNER JOIN sl_banks_movrel ON ID_bills = tableid INNER JOIN sl_banks_movements USING(ID_banks_movements) INNER JOIN sl_banks USING(ID_banks) INNER JOIN sl_accounts ON sl_accounts.`Description` = `ABA-ACH` WHERE tableid = '$id_bills' AND tablename = 'bills' AND ID_accategories = '1';";
	print "$bquery\n";
	my ($sth) = &Do_SQL($bquery);
	while( ($idbm, $amount, $paid_pct, $ida_banks, $currency_exchange, $bill_date_m, $bill_date, $id_admin_users) = $sth->fetchrow() ) {

		$currency_exchange = 1 if !$currency_exchange;
		my $str_pos;my $str_bills;
		my $amount_derived = $amount;
		my $amt_negative = 0;

		my $epo_query = "SELECT ID_vendors,Category,IF(ID_purchaseorders > 0 AND sl_bills_pos.Amount > 0,ID_purchaseorders,0) AS ID_po, IF(ID_bills_expenses > 0 AND sl_bills_expenses.Amount > 0,ID_bills_expenses,0) AS ID_expense,IF(ID_segments IS NULL,0,ID_segments)AS ID_segments FROM sl_bills INNER JOIN sl_vendors USING(ID_vendors) LEFT JOIN sl_bills_pos USING(ID_bills) LEFT JOIN sl_bills_expenses USING(ID_bills) WHERE sl_bills.ID_bills = '".$id_bills."' HAVING ID_po > 0 OR ID_expense > 0 ORDER BY sl_bills_pos.Amount, sl_bills_expenses.Amount;";
		print "$epo_query\n";
		my ($sth) = &Do_SQL($epo_query);
		my $rows = $sth->rows();
		my $this_type;
		print "BankDate: $bill_date : RegDate: $bill_date_m\n";

		while(my($id_vendors,$vendor_category,$id_po, $id_expenses, $ids) = $sth->fetchrow()) {

			++$x;

			$id_segments = $ids;
			(!$this_bill_vendor_category) and ($this_bill_vendor_category = $vendor_category);
			if(!$bill_date or !$id_admin_users) {

				my ($sth) = &Do_SQL("SELECT LogDate,ID_admin_users FROM admin_logs WHERE Action = '$id_bills' AND tbl_name = 'sl_bills' and Message = 'bills_paid' LIMIT 1;");
				($bill_date, $id_admin_users) = $sth->fetchrow();
				($id_admin_users) and ( $usr{'id_admin_users'} = $id_admin_users);

			}

			if($bill_date and $amount and $ida_banks) {

				if($id_po) {

					(!$this_type) and ($this_type = 'po');
					(!$this_bill_type) and ($this_bill_type = $this_type) ;
					($x == $rows ) and ($amt_negative = &load_bill_amt_negative($id_bills,'sl_bills_pos'));

					##################
					##################
					### Pago de PO
					##################
					##################
					my ($sth) = &Do_SQL("SELECT  
									SUM(IF(ID_purchaseorders = '$id_po',Amount,0)) / SUM(Amount) AS PctPaid , 
									( (SUM(IF(ID_purchaseorders = '$id_po',Amount,0)) - $amt_negative ) / SUM(Amount)) * $paid_pct
									FROM sl_bills_pos WHERE ID_bills = '". $id_bills ."';");
					my($pct , $this_pct) = $sth->fetchrow();
					#$this_pct = round($this_pct,3);
					
					my $this_amount = $x < $rows ? round($this_pct * $amount ,3) : $amount_derived;
					$amount_derived -= $this_amount;
					$str .= "$x - $rows -- $amount : $pct ($pct * $paid_pct = $this_pct) = $this_amount - $amount_derived\n";

					my @params = ($id_po,$id_bills,$ida_banks,$this_amount,$currency_exchange);
					&accounting_keypoints('po_payment_'. lc($vendor_category), \@params );
					my $exchange_rate = $currency_exchange > 0 ? $currency_exchange : 1;
					&Do_SQL("INSERT INTO sl_purchaseorders_notes SET ID_purchaseorders = '$id_po', Notes='Payment Posted\nOriginal Amount: $this_amount\nCurrency Exchange: $currency_exchange\nTotal Paid: ".round($this_amount * $exchange_rate,3)." ',Type='Low', Date = CURDATE(), Time = CURTIME(), ID_admin_users='$usr{'id_admin_users'}' ");
					$str_pos .= "$id_po,";

				}elsif($id_expenses){

					(!$this_type) and ($this_type = 'expenses');
					(!$this_bill_type) and ($this_bill_type = $this_type) ;
					($x == $rows ) and ($amt_negative = &load_bill_amt_negative($id_bills,'sl_bills_expenses'));

					##################
					##################
					### Pago de Expense
					##################
					##################

					my $pct_query = "SELECT 
									SUM(IF(ID_bills_expenses = '$id_expenses',Amount,0)) / SUM(Amount) AS PctPaid,
									( (SUM(IF(ID_bills_expenses = '$id_expenses',Amount,0)) - $amt_negative ) / SUM(Amount)) * $paid_pct
									FROM sl_bills_expenses WHERE ID_bills = '". $id_bills ."';";
					print "$pct_query\n";
					my ($sth) = &Do_SQL($pct_query);
					my($pct, $this_pct) = $sth->fetchrow();
					#$this_pct = round($this_pct,3);
					
					my $this_amount = $x < $rows ? round($this_pct * $amount ,3) : $amount_derived;
					$amount_derived -= $this_amount;
					$str .= "$amount : $pct ($pct * $paid_pct = $this_pct) = $this_amount - $amount_derived\n";


					my @params = ($id_bills,$ida_banks,$this_amount,$this_pct,$currency_exchange);
					&accounting_keypoints('bills_expenses_payment_'. lc($vendor_category), \@params );
					my $exchange_rate = $currency_exchange > 0 ? $currency_exchange : 1;
					&Do_SQL("INSERT INTO sl_bills_notes SET ID_bills = '$id_bills', Notes='Payment Posted\nOriginal Amount: $this_amount\nCurrency Exchange: $currency_exchange\nTotal Paid: ".round($this_amount * $exchange_rate,3)." ',Type='Low', Date = CURDATE(), Time = CURTIME(), ID_admin_users='$usr{'id_admin_users'}' ");
					$str_bills .= "$id_bills,";
					
				}


			} ## IF date/amount

			print "String: $str\n";

		} ## While PO/Expense
		chop($str_pos);
		chop($str_bills);

		my $modquery = $str_pos ne '' ? "ID_tableused IN ($str_pos) AND tableused = 'sl_purchaseorders'" : "ID_tableused IN ($str_bills)  AND tableused = 'sl_bills'";
		my $query_to_paid = "UPDATE sl_movements SET EffDate = '$bill_date', ID_segments = '$id_segments', Date = '$bill_date', ID_journalentries = 0, ID_admin_users = '$id_admin_users' WHERE $modquery AND TIMESTAMPDIFF(SECOND,CONCAT(Date,' ',Time) , NOW()) BETWEEN 0 AND 5 AND ID_admin_users = '$usr{'id_admin_users'}';";
		&Do_SQL($query_to_paid);
		print "$query_to_paid\n";

	} ## While Amount


	if($this_type eq 'expenses'){

		##########
		########## Revision de Expense Pagado
		##########

		my @params = ($id_bills);
		#&cgierr('bills_'. $this_type .'_paid_' . lc($vendor_category) . " -- $id_expenses,0,$ida_deposit,$this_amount,$currency_exchange,$pct");
		&accounting_keypoints('bills_'. $this_bill_type .'_paid_' . lc($vc), \@params );

		#my $query_to_paid = "UPDATE sl_movements SET EffDate = '$bill_date', Date = '$bill_date', ID_journalentries = 0, ID_admin_users = '$id_admin_users' WHERE ID_tableused = '$id_bills' AND tableused = 'sl_bills' AND TIMESTAMPDIFF(SECOND,CONCAT(Date,' ',Time) , NOW()) BETWEEN 0 AND 5 AND ID_admin_users = '$usr{'id_admin_users'}';";
		#&Do_SQL($query_to_paid);
		#print "$query_to_paid\n";

	}


}


#############################################################################
#############################################################################
#   Function: deposits_to_paid
#
#       Es: Procesa un Bill (Deposit) que ya esta pagado y no tiene Mov Contables
#       En: 
#
#    Created on: 07/10/2008  16:21:10
#
#    Author: _RB_
#
#    Modifications:
#
#   Parameters:
#
#
#  Returns:
#
#
#   See Also:
#
#
sub deposits_to_paid {
#############################################################################
#############################################################################

	my ($id_bills, $currency_exchange) = @_;

	my ($sth) = &Do_SQL("SELECT AmountPaid, sl_accounts.ID_accounts, sl_banks_movements.BankDate, sl_banks_movrel.ID_admin_users FROM sl_bills INNER JOIN sl_banks_movrel ON ID_bills = tableid INNER JOIN sl_banks_movements USING(ID_banks_movements) INNER JOIN sl_banks USING(ID_banks) INNER JOIN sl_accounts ON sl_accounts.`Description` = `ABA-ACH` WHERE tableid = '$id_bills' AND tablename = 'bills' AND ID_accategories = '1';");
	my($amount, $ida_banks, $bill_date, $id_admin_users) = $sth->fetchrow();

	if(!$bill_date or !$id_admin_users) {

		print "No Date/User Found in Bank Movement.\n";
		my ($sth) = &Do_SQL("SELECT LogDate,ID_admin_users FROM admin_logs WHERE Action = '$id_bills' AND tbl_name = 'sl_bills' and Message = 'bills_paid' LIMIT 1;");
		($bill_date, $id_admin_users) = $sth->fetchrow();

	}

	if($bill_date and $amount and $ida_banks) {

		########################################################
		########################################################
		## Movimientos de contabilidad
		########################################################
		########################################################
		my $id_vendors = &load_name('sl_bills','ID_bills', $id_bills, 'ID_vendors');
		my $vendor_category = &load_name('sl_vendors','ID_vendors', $id_vendors,'Category');
		$currency_exchange = 0 if !$currency_exchange;
		my @params = ($id_vendors,$id_bills,$ida_banks,$bill_date,$amount,$currency_exchange);
		#&cgierr('vendor_deposit_' . lc($vendor_category) . " $id_vendors,$ida_banks,$amount,$currency_exchange");
		&accounting_keypoints('vendor_deposit_' . lc($vendor_category), \@params );

		my $query_to_paid = "UPDATE sl_movements SET EffDate = '$bill_date', Date = '$bill_date', ID_journalentries = 0, ID_admin_users = '$id_admin_users' WHERE ID_tableused = '$id_vendors' AND tableused = 'sl_vendors' AND TIMESTAMPDIFF(SECOND,CONCAT(Date,' ',Time) , NOW()) BETWEEN 0 AND 5 AND ID_admin_users = '$usr{'id_admin_users'}';";
		&Do_SQL($query_to_paid);
		print "$query_to_paid\n";

	}

}



#############################################################################
#############################################################################
#   Function: bills_upd
#
#       Es: Revisa y actualiza de ser necesario, un Bill Processed a Partly Paid o Paid
#       En: 
#
#    Created on: 07/09/2013  16:21:10
#
#    Author: _RB_
#
#    Modifications:
#
#   Parameters:
#
#
#  Returns:
#
#
#   See Also:
#
#
sub bill_upd {
#############################################################################
#############################################################################

	my ($id_bills, $amount) = @_;
	my $status = 'Processed';

	my ($sth) = &Do_SQL("SELECT SUM(AmountPaid) FROM sl_banks_movrel WHERE tableid = '$id_bills' AND tablename = 'bills';");
	my ($total_paid) = $sth->fetchrow();

	if($total_paid > 0){
		if($total_paid == $amount){
			$status = 'Paid';
		}elsif($total_paid > 0){
			$status = 'Partly Paid';
		}

		my $query = "UPDATE sl_bills SET Status = '$status' WHERE ID_bills = '$id_bills';";
		print "$query\n";
		&Do_SQL($query);
	}


	return $status;



}



#############################################################################
#############################################################################
#   Function: deposits_upd
#
#       Es: Revisa si en sl_movements hay registros para sl_vendors que no esten referenciados a un Bill
#       En: 
#
#    Created on: 07/09/2013  16:21:10
#
#    Author: _RB_
#
#    Modifications:
#
#   Parameters:
#
#
#  Returns:
#
#
#   See Also:
#
#
sub deposit_upd {
#############################################################################
#############################################################################


	my ($id_bills, $id_vendors, $amount) = @_;

	($cfg{'reset'}) and (print "/*Reseting Deposit Application*/\n") and (&Do_SQL("/*Reseting Deposit*/ DELETE FROM sl_movements WHERE ID_tablerelated = '$id_bills' AND tablerelated = 'sl_bills' AND Category = 'Expense' AND (ID_journalentries IS NULL OR ID_journalentries = 0) ;"));
	my ($sth) = &Do_SQL("SELECT sl_banks_movrel.Date FROM sl_bills INNER JOIN sl_banks_movrel ON ID_bills = tableid INNER JOIN sl_banks_movements USING(ID_banks_movements)  WHERE tableid = '$id_bills' AND tablename = 'bills';");
	my ($pdate) = $sth->fetchrow();

	if($pdate) {

		my ($sth) = &Do_SQL("SELECT ID_movements, Reference FROM sl_movements WHERE ID_tableused = '$id_vendors' AND tableused = 'sl_vendors' AND EffDate = '$pdate' AND Credebit = 'Credit' AND (Reference IS NULL OR Reference = '' OR Reference = 'Deposit: $id_bills') AND ABS(Amount - $amount) BETWEEN 0 AND 0.009 LIMIT 1;");
		my ($id_movements, $reference) = $sth->fetchrow();
		($id_movements) and ($vendor_deposits = 1);

		if($id_movements){ #and !$reference


			my $id_segments = 0;
			my ($sth) = &Do_SQL("SELECT ID_accounts FROM sl_bills WHERE ID_bills = '$id_bills' AND Type = 'Deposit';");
			my ($this_ida_deposit) = $sth->fetchrow();
			if(!$this_ida_deposit) {
				my ($sth) = &Do_SQL("SELECT sl_bills_expenses.ID_accounts, sl_bills_expenses.ID_segments FROM sl_bills INNER JOIN sl_bills_expenses USING(ID_bills) WHERE sl_bills.ID_bills = '$id_bills' AND Type = 'Deposit';");
				($this_ida_deposit, $id_segments) = $sth->fetchrow();
			}
			(!$id_segments) and ($id_segments = 0);
			(!$this_ida_deposit) and ($this_ida_deposit = 0);

			############
			############ Actualizacion sl_movements
			############
			$queryupd1 = "UPDATE sl_movements SET Reference = '', ID_tablerelated = '$id_bills', tablerelated = 'sl_bills', ID_accounts = IF($this_ida_deposit > 0, $this_ida_deposit, ID_accounts) WHERE ID_tableused = '$id_vendors' AND tableused = 'sl_vendors' AND EffDate = '$pdate' AND Credebit = 'Debit' AND (Reference IS NULL OR Reference = '' OR Reference = 'Deposit: $id_bills') AND (ID_tablerelated = 0 OR ID_tablerelated IS NULL OR ID_tablerelated = '$id_bills') AND ABS(Amount - $amount) BETWEEN 0 AND 0.009 LIMIT 1;";
			$queryupd2 = "UPDATE sl_movements SET Reference = '', ID_tablerelated = '$id_bills', tablerelated = 'sl_bills' WHERE ID_tableused = '$id_vendors' AND tableused = 'sl_vendors' AND EffDate = '$pdate' AND Credebit = 'Credit' AND (Reference IS NULL OR Reference = '' OR Reference = 'Deposit: $id_bills') AND (ID_tablerelated = 0 OR ID_tablerelated IS NULL OR ID_tablerelated = '$id_bills') AND ABS(Amount - $amount) BETWEEN 0 AND 0.009 LIMIT 1;";
			print "Actualizando Deposito\n$queryupd1\n$queryupd2\n";
			&Do_SQL($queryupd1);
			&Do_SQL($queryupd2);
			
		}

	}

}


#############################################################################
#############################################################################
#   Function: po_noninventory_upd
#
#       Es: Revisa si en sl_movements hay registros para sl_vendors que no esten referenciados a un Bill
#       En: 
#
#    Created on: 07/09/2013  16:21:10
#
#    Author: _RB_
#
#    Modifications:
#
#   Parameters:
#
#
#  Returns:
#
#
#   See Also:
#
#
sub po_noninventory_upd {
#############################################################################
#############################################################################

	my ($id_bills,$status,$vendors_credits_qty,$vendors_debits_qty) = @_;
	my $x=0;

	my ($sth) = &Do_SQL("SELECT ID_purchaseorders FROM sl_bills_pos WHERE ID_bills = '$id_bills' AND Amount > 0;");
	PO: while (my($id_po) = $sth->fetchrow()) {

		my ($sth) = &Do_SQL("SELECT COUNT(*) FROM sl_purchaseorders_items WHERE ID_purchaseorders = '$id_po' AND ID_products > 500000000;");
		my ($total) = $sth->fetchrow();

		if (!$total){
			print "Merchandise PO: $id_po \n";
			&po_inventory_upd($id_po);
			($status = 'Paid') and ($vendors_credits_qty = 1) and ($vendors_debits_qty = 1);
			next PO;
		}

		++$x;


		my ($sth) = &Do_SQL("SELECT Category FROM sl_vendors INNER JOIN sl_purchaseorders USING(ID_vendors) WHERE ID_purchaseorders = '$id_po';");
		my ($vendor_category) = $sth->fetchrow();

		##########
		########## Buscamos registros de Pago
		##########
		my ($sth) = &Do_SQL("SELECT COUNT(*) FROM sl_banks_movrel WHERE tablename = 'bills' AND tableid = '$id_bills';");
		my ($billp) = $sth->fetchrow();
		($billp > 0) and ($status = 'Paid') and ($vendors_credits_qty = 1) and ($vendors_debits_qty = 0);

		##########
		########## Eliminamos registros contables previos
		##########
		my $queryd = "/*Non Inventory Delete $id_po*/ DELETE FROM sl_movements WHERE tableused = 'sl_purchaseorders' AND ID_tableused = '$id_po' AND (ID_journalentries IS NULL OR ID_journalentries = 0);";
		print "$queryd\n";
		&Do_SQL($queryd);

		my $rec = 0;
		my ($sth) = &Do_SQL("SELECT ID_purchaseorders_items, ID_products, PurchaseID_accounts,Received, Name, Price, Tax_percent FROM sl_purchaseorders_items INNER JOIN sl_noninventory ON ID_noninventory = ID_products - 500000000 WHERE ID_purchaseorders = '$id_po' AND Status = 'Active' AND Received > 0 AND PurchaseID_accounts ORDER BY ID_purchaseorders_items;");
		LINE: while(my ($idpoi,$id_products,$ida_debit,$to_receive,$pname,$price,$tax_pct) = $sth->fetchrow()) {

			my ($sth) = &Do_SQL("SELECT Date,ID_admin_users FROM sl_purchaseorders_notes WHERE ID_purchaseorders = '$id_po' AND Type = 'High' AND Notes LIKE '%Received%' LIMIT 1");
			my ($effdate,$id_admin_users) = $sth->fetchrow();
			########################################################
			########################################################
			##  Movimientos de contabilidad
			########################################################
			########################################################
			my $this_price = round($to_receive * $price,2);
			my $this_tax = $tax_pct > 0 ? round($to_receive * $price * $tax_pct,2) : 0;
			#&cgierr('po_noninventory_in_'. lc($vendor_category) . " --- $id_po,$idpoi,$id_products,$ida_debit,$this_price,$this_tax");
			my @params = ($id_po,$idpoi,$id_products,$ida_debit,$this_price,$this_tax);
			&accounting_keypoints('po_noninventory_in_'. lc($vendor_category), \@params );

			my $query_non = "/*Non Inventory PO $id_po*/ UPDATE sl_movements SET EffDate = '$effdate', Date = '$effdate', ID_journalentries = 0, ID_admin_users = '$id_admin_users' WHERE ID_tableused = '$id_po' AND tableused = 'sl_purchaseorders' AND TIMESTAMPDIFF(SECOND,CONCAT(Date,' ',Time) , NOW()) BETWEEN 0 AND 5 AND ID_admin_users = '$usr{'id_admin_users'}';";
			print "$query_non\n";
			&Do_SQL($query_non);

		}

	}

	if($x > 0) {
		return ($x,$status,$vendors_credits_qty,$vendors_debits_qty);
	}else{
		return ($x,$status,$vendors_credits_qty,$vendors_debits_qty);
	}

}


#############################################################################
#############################################################################
#   Function: po_inventory_upd
#
#       Es: Revisa si en sl_movements hay registros para sl_vendors que no esten referenciados a un Bill
#       En: 
#
#    Created on: 07/09/2013  16:21:10
#
#    Author: _RB_
#
#    Modifications:
#
#   Parameters:
#
#
#  Returns:
#
#
#   See Also:
#
#
sub po_inventory_upd {
#############################################################################
#############################################################################

	my ($id_po) = @_;
	my $x=0;


	###############
	############### 1) Buscamos Creditos con cuenta de banco
	###############
	my ($sth) = &Do_SQL("SELECT Amount,EffDate,ID_admin_users FROM sl_movements WHERE ID_tableused = '$id_po' AND tableused = 'sl_purchaseorders' AND ID_accounts IN($cfg{'ida_banks'}) AND Credebit = 'Credit' ORDER BY EffDate,ID_movements;");
	while( my($amount, $effdate, $id_admin_users) = $sth->fetchrow()) {

		++$x;
		##################
		################## 2) Borramos Debitos(IVA Pagado) y Creditos(IVA Pendiente) del mismo monto/fecha
		##################
		my $queryd1 = "DELETE FROM sl_movements WHERE ID_tableused = '$id_po' AND tableused = 'sl_purchaseorders' AND ID_accounts = '$cfg{'ida_tax_paid'}' AND Credebit = 'Debit' AND EffDate = '$effdate';";
		my $queryd2 = "DELETE FROM sl_movements WHERE ID_tableused = '$id_po' AND tableused = 'sl_purchaseorders' AND ID_accounts = '$cfg{'ida_tax_payable'}' AND Credebit = 'Credit' AND EffDate = '$effdate';";
		print "$queryd1\n$queryd2\n";
		my ($sth1) = &Do_SQL($queryd1); my ($d1) = $sth1->rows();
		my ($sth2) = &Do_SQL($queryd2); my ($d2) = $sth2->rows();
		my $del = $d1 + $d2;

		##################
		################## 3) Aplicamos el IVA nuevamente
		##################
		if($del > 0) {

			my ($tax) = round($amount - ($amount / (1 + $cfg{'tax_pct'}) ),2);
			&Do_SQL("INSERT INTO sl_movements (ID_accounts,Amount,Reference,EffDate,tableused,ID_tableused,Category,Credebit,Status,Date,Time  ,ID_admin_users )
				VALUES ($cfg{'ida_tax_paid'},'".$tax."', '', '$effdate', 'sl_purchaseorders', $id_po, 'Compras', 'Debit','Active','$effdate', CURTIME(), '$id_admin_users');");
			&Do_SQL("INSERT INTO sl_movements (ID_accounts,Amount,Reference,EffDate,tableused,ID_tableused,Category,Credebit,Status,Date,Time  ,ID_admin_users )
				VALUES ($cfg{'ida_tax_payable'},'".$tax."', '', '$effdate', 'sl_purchaseorders', $id_po, 'Compras', 'credit','Active','$effdate', CURTIME(), '$id_admin_users');");

		}

	}
	print "PO Updated OK\n" if $x > 0;

	return;
}


#############################################################################
#############################################################################
#   Function: accounting_group_amounts
#
#       Es: Agrupa montos por cuenta contable
#       En: 
#
#
#    Created on: 06/01/2013
#
#    Author: _Roberto Barcenas_
#
#    Modifications:
#
#   Parameters:
#
#       - tableused: 
#		- id_tableused
#
#
#  Returns:
#
#      - 
#
#   See Also:
#
#
sub accounting_group_amounts{
#############################################################################
#############################################################################

	my ($tableused, $id_tableused) = @_;

	my ($sth) = &Do_SQL("SELECT ID_accounts,Credebit,Amount,movs,ID_movs FROM
						(
							SELECT ID_accounts,Credebit,COUNT(*)AS movs,SUM(Amount)AS Amount, GROUP_CONCAT(ID_movements)AS ID_movs FROM sl_movements WHERE tableused = '$tableused' AND ID_tableused = '$id_tableused' AND Status = 'Active' AND (ID_journalentries IS NULL OR ID_journalentries = 0) GROUP BY ID_accounts,Credebit,EffDate
						)tmp
						HAVING movs > 1 ORDER BY Credebit,ID_accounts;");
	while(my ($id_accounts, $credebit, $amount, $movs, $ids) = $sth->fetchrow() ){

		my @ary = split(/,/, $ids);
		my $i=0;

		for (0..$#ary){

			my $id_movements = int($ary[$i]);
			if($i == 0){
				&Do_SQL("UPDATE sl_movements SET Amount = '$amount' WHERE ID_movements = '$id_movements';");
			}else{
				&Do_SQL("DELETE FROM sl_movements WHERE ID_movements = '$id_movements';");
			}

			$i++;
		}

	}

	return;
}

##################################################################
#     CGIERR   	#
##################################################################
sub cgierr {
# --------------------------------------------------------
	my (@sys_err) = @_;

	print "\nCGI ERROR\n==========================================\n";
	$sys_err[0]	and print "Error Message       : $sys_err[0]\n";
	$sys_err[1]	and print "Error Code          : $sys_err[1]\n";
	$sys_err[2]	and print "System Message      : $sys_err[2]\n";
	$0			and print "Script Location     : $0\n";
	$]			and print "Perl Version        : $]\n";
	$sid		and print "Session ID          : $sid\n";
	
	exit -1;
}
