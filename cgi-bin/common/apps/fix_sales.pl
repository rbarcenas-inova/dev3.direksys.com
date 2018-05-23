#!/usr/bin/perl
#######################################################################
#######################################################################
#######################################################################

#use strict;
#use Perl::Critic;
use DBI;
use DBIx::Connector;
use DBD::mysql;
use Cwd;


local ($dir) = getcwd;
local ($in{'e'}) = 3;
local ($usr{'id_admin_users'}) = 1;
local ($in{'batch_forced'}) = 1;
local ($cfg{'ida_banks'}) = '19,23,24,26,30,31,35,36,37,38,40,48';
local ($cfg{'ida_bank_default'}) = 36; 
local ($cfg{'ida_customer_ar'}) = '76,79';
local ($cfg{'ida_tax_payable'}) = '264';
local ($cfg{'ida_tax_paid'}) = '265';
local ($cfg{'tax_pct'}) = .16;
local ($cfg{'reset'}) = 1;

chdir($dir);

# Required Libraries
# --------------------------------------------------------
eval {
	require ('../subs/auth.cgi');
	require ('../subs/sub.base.html.cgi');
	require ('../subs/sub.func.html.cgi');
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
	&process_sales;
	&disconnect_db;

}


#############################################################################
#############################################################################
#   Function: process_sales
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
sub process_sales {
#############################################################################
#############################################################################
	
	#print "Content-type: text/html\n\n";
	my ($query_f) = "SELECT
					 ID_tableused,
					 SUM(IF(ID_accounts IN ($cfg{'ida_customer_ar'}) AND Credebit = 'Debit',Amount, 0))AS AR,
					 SUM(IF(ID_accounts IN ($cfg{'ida_tax_payable'}) AND Credebit = 'Credit',Amount, 0))AS Tax_Payable,
					 SUM(IF(ID_accounts IN ($cfg{'ida_tax_paid'}) AND Credebit = 'Debit',Amount, 0))AS Tax_Paid
					 FROM sl_movements INNER JOIN
					(
						SELECT DISTINCT ID_orders FROM sl_orders_payments 
						WHERE ID_orders = '9154845' AND Captured= 'Yes' AND Amount > 0 AND Status = 'Approved' ORDER BY ID_orders
					)tmp ON ID_tableused = ID_orders
					WHERE Status = 'Active' AND tableused = 'sl_orders'
					GROUP BY ID_tableused
					HAVING Tax_Payable > 0
					ORDER BY ID_tableused;";


	print "/*Query Inicial */ \n$query_f\n\n";
	my ($sth) = &Do_SQL($query_f);

	my $i=0;
	SALE: while (my ($id_orders, $ar_amount, $tax_payable, $tax_paid) = $sth->fetchrow() ) {
		
		++$i;	
		
		print "Row $i - $id_orders - $tax_payable : $tax_paid\n";
		#print "ID: $id_bills, T: $type, D: $date, IDV: $id_vendors, C: $company, M: $memo, C: $currency, CE: $currency_exchange, ST: $status, AM: $amount, DED: $deductible, QTY: $qty_movs, AMM: $amt_movs, QD: $qty_debits, AD: $amt_debits, QC: $qty_credits, AC: $amt_credits, VD: $vendors_debits_qty, VC: $vendors_credits_qty, NM: $neg_movs, VD: $vendor_deposits\n";
		
		if($tax_payable == $tax_paid){

			###########
			########### Tax Pagado
			###########
			print "Skipping ($tax_payable == $tax_paid)\n\n";
			next SALE;
		}

		###############################
		###############################
		###############################  Borrado de Contabilidad para reasignacion (solo aplica expenses)
		###############################
		###############################
		if($cfg{'reset'}) {

			

		}
		
		#########
		######### Proceso de Busqueda Pre Proceso General
		#########
		my $q1 = "SELECT ID_orders_payments, tmp.Amount,IDA_banks, tmp.Date, tmp.Time, tmp.ID_admin_users, tmp.Amount / $ar_amount 
				FROM
				(
					SELECT ID_orders,ID_orders_payments, sl_orders_payments.Amount, 
					sl_banks_movrel.Date, sl_banks_movrel.Time,
					sl_banks_movrel.ID_admin_users,
					IF(ID_accounts IS NULL, $cfg{'ida_bank_default'},ID_accounts)AS IDA_banks 
					FROM sl_orders_payments INNER JOIN sl_banks_movrel
					ON ID_orders_payments = tableid
					INNER JOIN sl_banks_movements USING(ID_banks_movements)
					INNER JOIN sl_banks USING(ID_banks)
					LEFT JOIN sl_accounts ON sl_accounts.`Description` = `ABA-ACH`
					WHERE ID_orders = '$id_orders'
					AND Captured= 'Yes' AND sl_orders_payments.Amount > 0 
					AND sl_orders_payments.Amount = AmountPaid
					AND sl_orders_payments.Status = 'Approved' 
					ORDER BY ID_orders_payments
				)tmp
				WHERE tmp.Amount > 0 ORDER BY tmp.Date, tmp.Time;";

		print "/*Buscando Monto y Pct*/\n$q1\n";
		my ($sth1) = &Do_SQL($q1);
		my $i = 0;
		my $accumulated = 0;
		PAY: while (my ($id_orders_payments, $amount, $ida_banks, $effdate, $ttime, $id_admin_users, $pct) = $sth1->fetchrow() ) {

			++$i;
			$pct = round($pct,3);

			if($pct > 0){
				

				my $q2 = "SELECT ID_movements FROM sl_movements WHERE ID_tableused = '$id_orders' 
				 			AND tableused = 'sl_orders' 
							AND ID_accounts IN($cfg{'ida_banks'}) AND Credebit = 'Debit'
							AND Amount = '$amount' 
							AND Effdate = '$effdate' AND Time = '$ttime'
							AND Status = 'Active' AND ID_admin_users = '$id_admin_users';";
				my ($sth2) = &Do_SQL($q2);
				my $id_movs = $sth2->fetchrow();

				if(!$id_movs){

					#######
					####### Pago sin movimientos. Mandar a pagar.
					#######
					print "/*Pago sin Contabilidad*/\n$q2\n";

					my ($order_type, $ctype, $ptype,@params);
					my ($sth) = &Do_SQL("SELECT Ptype, Type FROM sl_orders INNER JOIN sl_customers USING(ID_customers) WHERE ID_orders = '$id_orders';");
					($order_type, $ctype) = $sth->fetchrow();
					$ptype = get_deposit_type($id_orders_payments,'');
					@params = ($id_orders, $id_orders_payments, $ida_banks, 1);
					&accounting_keypoints('order_deposit_'. $ctype .'_'. $order_type .'_'. $ptype, \@params);

					my $query_upd = "/*Payment Movement $id_orders_payments*/ UPDATE sl_movements SET EffDate = '$effdate', Date = '$effdate', Time = '$ttime', ID_journalentries = 0, ID_admin_users = '$id_admin_users' WHERE ID_tableused = '$id_orders' AND tableused = 'sl_orders' AND TIMESTAMPDIFF(SECOND,CONCAT(Date,' ',Time) , NOW()) BETWEEN 0 AND 5 AND ID_admin_users = '$usr{'id_admin_users'}';";
					print "$query_upd\n";
					&Do_SQL($query_upd);

					next PAY;

				}

				my $this_tax = round( $tax_payable * $pct,3 );
				$this_tax = ($tax_paid + $accumulated + $this_tax > $tax_payable) ? ($tax_payable - $accumulated - $tax_paid) : $this_tax;

				my $q3 = "SELECT ID_movements, Amount,Date FROM sl_movements 
				WHERE ID_tableused = '$id_orders' AND tableused = 'sl_orders' 
				AND ID_accounts IN($cfg{'ida_tax_paid'}) AND Credebit = 'Credit'
				AND Amount = '$this_tax' AND Status = 'Active' AND Time = '$ttime' 
				ORDER BY Effdate, Time;";

				print "/* Searching Tax Already*/\n$q2\n";
				my ($sth3) = &Do_SQL($q3);
				if($sth3->rows() > 0){

					my ($id_mov, $amt, $date) = $sth3->fetchrow();
					print "Movement Found - $id_mov - $amt - $date ... Skipping\n";

				}else{

					print "Generating Tax Movements\nPayment: $i - $amount - $pct - $effdate - $this_tax\n";
					&Do_SQL("INSERT INTO sl_movements (ID_accounts,Amount,Reference,EffDate,tableused,ID_tableused,Category,Credebit,Status,Date,Time  ,ID_admin_users )
							VALUES ($cfg{'ida_tax_payable'},'".$this_tax."', '', '$effdate', 'sl_orders', '$id_orders', 'Cobranza', 'Debit','Active','$effdate', CURTIME(), '$id_admin_users');");			
					&Do_SQL("INSERT INTO sl_movements (ID_accounts,Amount,Reference,EffDate,tableused,ID_tableused,Category,Credebit,Status,Date,Time  ,ID_admin_users )
							VALUES ($cfg{'ida_tax_paid'},'".$this_tax."', '', '$effdate', 'sl_orders', '$id_orders', 'Cobranza', 'Credit','Active','$effdate', CURTIME(), '$id_admin_users');");

				}

				$accumulated += $this_tax;
			}


		}

		if(!$i){
			print "No Payment Found\n";
		}


		print "\n";
		&accounting_group_amounts('sl_orders', $id_orders);


	}



	#my $fquery1 = "DELETE FROM sl_movements WHERE Amount = 0 AND (ID_journalentries IS NULL OR ID_journalentries = 0);";
	#my $fquery2 = "UPDATE sl_movements SET ID_journalentries = -1 WHERE EffDate < '2013-05-16' AND (ID_journalentries IS NULL OR ID_journalentries = 0);";
	#print "\n\nBorrado Final de Datos en cero\n$fquery1\nMarcado de Movimientos pasados\n$fquery2\n\n";
	#&Do_SQL($fquery1);
	#sleep(5);
	#&Do_SQL($fquery2);

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
