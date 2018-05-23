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
local ($in{'e'}) = 2;
local ($usr{'id_admin_users'}) = 1;
local ($in{'batch_forced'}) = 1;
local ($cfg{'ida_banks'}) = '19,24,26,30';
local ($cfg{'ida_bankscd'}) = '207,211,613,215';
local ($cfg{'ida_inventory'}) = '137,367';
local ($cfg{'ida_bankfees'}) = '127,571';
local ($cfg{'ida_sales'}) = '354,355';
local ($cfg{'ida_bank_default'}) = 24; 
local ($cfg{'ida_customer_ar'}) = '76,79';
local ($cfg{'ida_tax_payable'}) = '264';
local ($cfg{'ida_tax_paid'}) = '265';
local ($cfg{'ida_diff'}) = '610';
local ($cfg{'tax_pct'}) = .16;
local ($cfg{'tax_shp'}) = 20.68;
local ($cfg{'bad_movs'}) = '';
#local ($cfg{'ida_specific_deposit'}) = '99:207';
local ($cfg{'reset'}) = 1;


chdir($dir);

# Required Libraries
# --------------------------------------------------------
eval {
	require ('../subs/auth.cgi');
	require ('../subs/sub.base.html.cgi');
	require ('../subs/sub.func.html.cgi');
	require ("../subs/sub.acc_movements.html.cgi");
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
	&Do_SQL("UPDATE `sl_movements` SET ID_accounts = 211 WHERE ID_accounts = 210;");
	&Do_SQL("UPDATE `sl_movements` SET Credebit = 'Debit' WHERE ID_accounts = 610 AND Credebit = '';");
	&Do_SQL("DELETE FROM `sl_movements` WHERE Amount < 0.01;");
	my $modquery;

	if($cfg{'bad_movs'} ne ''){

		###
		### Borramos todo menos el inventario
		###
		&Do_SQL("DELETE FROM sl_movements WHERE ID_tableused IN (".$cfg{'bad_movs'}.") AND tableused = 'sl_orders' AND ID_accounts NOT IN(".$cfg{'ida_inventory'}.");");
		$modquery = " AND ID_tableused IN (".$cfg{'bad_movs'}.") ";

		###
		### Resolucion de problemas
		###
		&fix_payments();
		print "\n\n";


	}

	my ($query_f) = "SELECT
					ID_tableused,
					IF(COUNT(*) IS NULL,0,COUNT(*)) AS QtyMovs,
					SUM(Amount) AS AmtMovs,
					SUM(IF(Credebit = 'Debit',1,0))AS QtyDebits,
					SUM(IF(Credebit = 'Debit',sl_movements.Amount,0))AS AmtDebits,
					SUM(IF(Credebit = 'Credit',1,0))AS QtyCredits,
					SUM(IF(Credebit = 'Credit',sl_movements.Amount,0))AS AmtCredits,
					SUM(IF(Credebit = 'Debit' AND ID_accounts IN(".$cfg{'ida_banks'}."),1,0))AS BankDebits,
					SUM(IF(Credebit = 'Credit' AND ID_accounts IN(".$cfg{'ida_bankscd'}."),1,0))AS BankCredits,
					SUM(IF(Credebit = 'Debit' AND ID_accounts IN(".$cfg{'ida_bankscd'}."),1,0))AS BankCDA,
					SUM(IF(Credebit = 'Credit' AND ID_accounts IN(".$cfg{'ida_sales'}."),1,0))AS SaleMovs,
					SUM(IF(Amount < 0,1,0)) AS NegMovs,
					SUM(IF(Credebit = 'Debit' AND ID_accounts IN(".$cfg{'ida_customer_ar'}."),sl_movements.Amount,0))AS AR,
					SUM(IF(ID_accounts = 610 AND Credebit IN ('Debit',''),sl_movements.Amount,0))AS DiffDebits,
					SUM(IF(ID_accounts = 610 AND Credebit IN ('Credit'),sl_movements.Amount,0))AS DiffCredits,
					SUM(IF(ID_accounts = 613 AND Credebit = 'Debit',sl_movements.Amount,0))AS BkProblemDebits,
					SUM(IF(ID_accounts = 613 AND Credebit = 'Credit',sl_movements.Amount,0))AS BkProblemCredits,
					ID_admin_users
					FROM sl_movements 
					WHERE
					1
					$modquery
					AND ID_tableused IN (9355616,9354374,9355612,9359818,9336380,9360919,9360921)
					AND tableused = 'sl_orders'
					GROUP BY ID_tableused
					/*HAVING BankDebits = 1 AND SaleMovs = 0*/
					/*HAVING BankDebits = 0 OR NegMovs > 0*/
					/*HAVING DiffDebits > 0*/
					ORDER BY ID_tableused /*DESC*/
					/*LIMIT 10*/;";

	($cfg{'bad_movs'} ne '') and ($query_f = "SELECT ID_orders FROM sl_orders WHERE 1 AND ID_orders IN (".$cfg{'bad_movs'}.") ;");


	print "/*Query Inicial */ \n$query_f\n\n"; #9041969,9041999,9042214,9043892,9049288
	my ($sth) = &Do_SQL($query_f);

	my $i=0;
	SALE: while (my ( $id_orders, $nmovs, $amt_movs, $qty_debs, $amt_debs, $qty_creds, $amt_creds, $bank_debs, $bank_creds, $bank_cda, $sale_movs, $neg_movs, $ar, $diff_debs, $diff_creds, $b3226_debs, $b3226_creds, $id_admin_users ) = $sth->fetchrow() ) {
		
		my $str;
		my $flag = 0;
		my ($t1,$t2);
		my $rt1 = '';
		my ($id_payments, $amount, $deposit_date, $id_admin_users);

		++$i;	

		######
		###### EffDate
		######
		my $mod_this = $cfg{'bad_movs'} ? "AND ID_accounts IN (".$cfg{'ida_inventory'}.")" : " AND Credebit = 'Credit' AND ID_accounts IN (".$cfg{'ida_sales'}.")";
		my ($sthsd) = &Do_SQL("SELECT EffDate,ID_admin_users FROM sl_movements WHERE ID_tableused = '$id_orders' AND tableused = 'sl_orders' $mod_this ORDER BY EffDate LIMIT 1;");
		my ($sale_date, $id_admin_users) = $sthsd->fetchrow();

		######
		###### Sale vs CDA
		######
		my ($sthsd2) = &Do_SQL("SELECT COUNT(DISTINCT EffDate) FROM sl_movements WHERE ID_tableused = '$id_orders' AND tableused = 'sl_orders';");
		my ($is_sale) = $sthsd2->fetchrow() == 1 ? 1 : 0;		


		my $iquery = "SELECT
						Ptype,
						Status, 
						Date,
						Products, Payments,
						IF(SumProd IS NULL,0,SumProd)AS SumProd, 
						IF(SumPay IS NULL,0,SumPay) AS SumPay,
						SumProd - SumPay AS Diferencia 
						FROM sl_orders 
						LEFT JOIN
						(
							SELECT ID_orders,
							COUNT(*)AS Products,
							SUM(SalePrice + Shipping + Tax + ShpTax - Discount) AS SumProd
							FROM sl_orders_products
							WHERE ID_orders = '$id_orders' 
							AND Status = 'Active'
							GROUP BY ID_orders
						)tmp USING(ID_orders)
						LEFT JOIN 
						(
							SELECT ID_orders,
							COUNT(*) AS Payments,
							SUM(Amount) AS SumPay
							FROM sl_orders_payments 
							WHERE ID_orders = '$id_orders'
							AND Status NOT IN('Void','Order Cancelled','Cancelled')
							GROUP BY ID_orders
						)tmp3 USING (ID_orders)
						WHERE 1 AND sl_orders.ID_orders = '$id_orders'
						/*AND sl_orders.Status  = 'Shipped'*/
						GROUP BY sl_orders.ID_orders;";
		my ($sthi) = &Do_SQL($iquery)				;
		my ( $ptype, $st, $date, $prods, $pays, $sum_prods, $sum_pays, $dif) = $sthi->fetchrow();
		
		$str = qq|"$i",$id_orders","$ptype","$date","$st","$prods","$sum_prods","$payments","$sum_pays","$dif",$amt_debs","$amt_creds","$bank_debs", "$bank_creds", "$neg_movs"|;


		###########################
		###########################
		######
		###### 1) SECCION SOLO BAD MOVEMENTS TO REPAIR
		######
		###########################
		###########################


		if($cfg{'bad_movs'}){

			###
			### Order Deposit
			###
			my ($sth2) = &Do_SQL("SELECT ID_orders_payments, Amount, CapDate FROM sl_orders_payments WHERE ID_orders = '$id_orders' AND CapDate IS NOT NULL AND CapDate <> '' AND CapDate <> '0000-00-00' AND Amount > 0 AND Status = 'Approved' AND Reason = 'Sale' ORDER BY CapDate;");
			while (($id_payments, $amount, $deposit_date) = $sth2->fetchrow()) {

				($cfg{'bad_movs'} and $ptype eq 'COD' and $sale_date) and ($deposit_date = $sale_date);

				&general_deposits($id_payments,$id_orders,'orders','Customer Deposit','Anticipo Clientes','','','CURDATE',$amount);

				#########
                ######### Cuentas contables especificas
                #########
                if($cfg{'ida_specific_deposit'}){

                	my ($ida_bank_debit, $ida_bank_credit) = split(/:/,$cfg{'ida_specific_deposit'});

					$ida_bank_debit = int($ida_bank_debit); $ida_bank_credit = int($ida_bank_credit);
					($ida_bank_debit > 0) and (&Do_SQL("UPDATE sl_movements SET ID_accounts = '$ida_bank_debit' WHERE ID_tableused = '$id_orders' AND tableused = 'sl_orders' AND Credebit = 'Debit' AND Amount = '$amount' AND TIMESTAMPDIFF(SECOND,CONCAT(Date,' ',Time) , NOW()) BETWEEN 0 AND 5 ;") );
					($ida_bank_credit > 0) and (&Do_SQL("UPDATE sl_movements SET ID_accounts = '$ida_bank_credit' WHERE ID_tableused = '$id_orders' AND tableused = 'sl_orders' AND Credebit = 'Credit' AND Amount = '$amount' AND TIMESTAMPDIFF(SECOND,CONCAT(Date,' ',Time) , NOW()) BETWEEN 0 AND 5 ;") );


                }

                my $queryu = "UPDATE sl_movements SET EffDate = '$deposit_date', Date = '$deposit_date', ID_journalentries = 0, ID_admin_users = '$id_admin_users' WHERE ID_tableused = '$id_orders' AND tableused = 'sl_orders' AND TIMESTAMPDIFF(SECOND,CONCAT(Date,' ',Time) , NOW()) BETWEEN 0 AND 5 AND ID_admin_users = '$usr{'id_admin_users'}';";
				#print "$queryu\n";
				&Do_SQL($queryu);

			}



			#### Acounting Movements
			my ($sth) = &Do_SQL("SELECT Ptype, Type FROM sl_orders INNER JOIN sl_customers USING(ID_customers) WHERE ID_orders = '$id_orders';");
			($order_type, $ctype) = $sth->fetchrow();

			my @params = ($id_orders);
			&accounting_keypoints('order_products_scanned_'. $ctype .'_credit-card', \@params );

			$str .= qq|,"BAD MOVS"|;
			$str .= qq|\n|;
			print $str;

			next SALE;


		}



		#####
		##### Cambiar cuenta de banco?
		#####
		if($ptype eq 'Credit-Card'){

			########
			######## CC  Debit/Credit must be 26/613
			########
			my ($sth1) = &Do_SQL("UPDATE sl_movements SET ID_accounts = '26' WHERE ID_tableused = '$id_orders' AND tableused = 'sl_orders' AND ID_accounts = '24';");
			$t1 = $sth1->rows();
			my ($sth2) = &Do_SQL("UPDATE sl_movements SET ID_accounts = '613' WHERE ID_tableused = '$id_orders' AND tableused = 'sl_orders' AND ID_accounts = '211';");
			$t2 = $sth2->rows();

			$rt1 = "CC Bank Repair + " if ($t1+$t2) > 0;

		}


		####
		#### 2) Movs de la nueva cuenta 3226 que no se tomaron en cuenta
		####
		if($diff_debs > 0 and $b3226_creds > 0 and $st eq 'Shipped'){


			if( ($diff_debs >= $b3226_creds or $b3226_creds - $diff_debs < 50) and abs($diff_debs - $b3226_creds) < 50 ){

				($is_sale) and (&Do_SQL("DELETE FROM sl_movements WHERE ID_tableused = '$id_orders' AND tableused = 'sl_orders' AND ID_accounts = '613' AND Credebit IN('Credit');") );

				if(abs($diff_debs - $b3226_creds) < 1) {		
					&Do_SQL("DELETE FROM sl_movements WHERE ID_tableused = '$id_orders' AND tableused = 'sl_orders' AND ID_accounts = '610' AND Credebit IN('Debit','');");
				}else{
					&Do_SQL("UPDATE sl_movements SET Amount = $diff_debs - $b3226_creds WHERE ID_tableused = '$id_orders' AND tableused = 'sl_orders' AND ID_accounts = '610' AND Credebit IN('Debit','');");
				}
				
				$rt1 .= "3226 Repair OK+";

				$diff_debs = 0;
				$b3226_creds = 0;
			}

		}


		if($is_sale and $b3226_creds > 0 and $st eq 'Shipped'){

			&Do_SQL("DELETE FROM sl_movements WHERE ID_tableused = '$id_orders' AND tableused = 'sl_orders' AND ID_accounts = '613' AND Credebit IN('Credit');");
			$rt1 .= "3226 Repair2 OK+";

			$b3226_creds = 0;
		}


		#####
		##### Tiene AR Registrado?
		#####
		if($ar > 0){

			&Do_SQL("DELETE FROM sl_movements WHERE ID_tableused = '$id_orders' AND tableused = 'sl_orders' AND ID_accounts IN (".$cfg{'ida_customer_ar'}.") AND Credebit IN('Debit');");
			$rt1 .= "AR Repair OK +";

			$ar = 0;

		}


		#####
		##### Mas de 1 movimiento de banco?
		#####
		if($bank_debs > 1 or $bank_creds > 1 or $bank_cda > 1){

			($bank_debs > 1) and ( &Do_SQL("DELETE FROM sl_movements WHERE ID_tableused = '$id_orders' AND tableused = 'sl_orders' AND ID_accounts IN(".$cfg{'ida_banks'}.")  AND Credebit IN('Debit') ORDER BY ID_movements DESC LIMIT ".($bank_debs - ($bank_debs - 1) ).";") );
			($bank_creds > 1) and ( &Do_SQL("DELETE FROM sl_movements WHERE ID_tableused = '$id_orders' AND tableused = 'sl_orders' AND ID_accounts IN(".$cfg{'ida_bankscd'}.")  AND Credebit IN('Credit') ORDER BY ID_movements DESC LIMIT ".($bank_creds - ($bank_creds - 1) ).";") );
			($bank_cda > 1) and ( &Do_SQL("DELETE FROM sl_movements WHERE ID_tableused = '$id_orders' AND tableused = 'sl_orders' AND ID_accounts IN(".$cfg{'ida_bankscd'}.")  AND Credebit IN('Debit') ORDER BY ID_movements DESC LIMIT ".($bank_cda - ($bank_cda - 1) ).";") );
			&Do_SQL("DELETE FROM sl_movements WHERE ID_tableused = '$id_orders' AND tableused = 'sl_orders' AND ID_accounts = '610' AND Credebit IN('Debit','');");

			$rt1 .= "3226 + 610 OK +";

			$b3226_creds = 0;
			$bank_cda = 1;

		}


		#####
		##### Borrar Redondeo de Cifras?
		#####
		if($diff_debs  > 0){

			&Do_SQL("DELETE FROM sl_movements WHERE ID_tableused = '$id_orders' AND tableused = 'sl_orders' AND ID_accounts = '610' AND Credebit IN('Debit','');");
			$diff_debs = 0;

			$rt1 .= "610 OK +";

		}


		#####
		##### Falta Aplicar Deposito?
		#####
		if(!$bank_cda and !$is_sale){

			my $sth_ad = &Do_SQL("INSERT INTO sl_movements (ID_movements,ID_accounts,Amount,Reference,EffDate,tableused,ID_tableused,Category,Credebit,Status,Date,Time,ID_admin_users)
								SELECT
								0,ID_accounts,Amount,Reference,'$sale_date',tableused,ID_tableused,'Ventas','Debit',Status,CURDATE(),CURTIME(),1
								FROM sl_movements 
								WHERE ID_tableused='$id_orders' AND tableused = 'sl_orders' 
								AND ID_accounts IN(".$cfg{'ida_bankscd'}.") AND Credebit='Credit';");
			my ($ad) = $sth_ad->rows();

			if($ad){

				$rt1 .= "CDA OK +";

			}

		}


		if($diff_debs > 5){
			$rt1 .= "3226 Debit Error +";
		}elsif($diff_creds > 5){
			$rt1 .= "3226 Credit Error +";
		}


		if($bank_debs and !$neg_movs and $dif == 0){

			$rt1 = "Skipped" if $rt1 eq '';
			$str = qq|"OK","$rt1",$str|;

			if($sale_movs and abs($bank_cda - $bank_creds) > 0){
				$str .= qq|,"ERROR2"|;

			}elsif(!$sale_movs and $ptype ne 'Credit-Card'){
				

				my @params = ($id_orders);

				######
				###### EffDate
				######
				my ($sthsd) = &Do_SQL("SELECT EffDate,ID_admin_users FROM sl_movements WHERE ID_tableused = '$id_orders' AND tableused = 'sl_orders' AND Credebit = 'Credit' AND ID_accounts IN (137) ORDER BY EffDate LIMIT 1;");
				my ($sale_date, $id_admin_users) = $sthsd->fetchrow();

				if(!$sale_date){
					my ($sthsd) = &Do_SQL("SELECT EffDate,ID_admin_users FROM sl_movements WHERE ID_tableused = '$id_orders' AND tableused = 'sl_orders' AND Credebit = 'Debit' AND ID_accounts IN (".$cfg{'ida_banks'}.") ORDER BY EffDate LIMIT 1;");
					($sale_date, $id_admin_users) = $sthsd->fetchrow();
				}

				&Do_SQL("DELETE FROM sl_movements WHERE ID_tableused = '$id_orders' AND tableused = 'sl_orders' AND ID_accounts IN(".$cfg{'ida_inventory'}.") AND EffDate = '$sale_date';");

				### Sale
				&accounting_keypoints('order_cod_delivered', \@params );

				my $querys = "UPDATE sl_movements SET EffDate = '$sale_date', Date = '$sale_date', ID_journalentries = 0, ID_admin_users = '$id_admin_users' WHERE ID_tableused = '$id_orders' AND tableused = 'sl_orders' AND TIMESTAMPDIFF(SECOND,CONCAT(Date,' ',Time) , NOW()) BETWEEN 0 AND 5 AND ID_admin_users = '$usr{'id_admin_users'}';";
				#print "$queryu\n";
				&Do_SQL($querys);


				$str .= qq|,"TOSALEINVOICE"|;


			}
			$str .= qq|\n|;

			print $str;
			next SALE;

		} #9000349


		if(!$bank_debs){

			#####
			##### 1) No hay deposito del banco. 
			#####


			my ($sth2) = &Do_SQL("SELECT ID_orders_payments, Amount, CapDate FROM sl_orders_payments WHERE ID_orders = '$id_orders' AND CapDate IS NOT NULL AND CapDate <> '' AND CapDate <> '0000-00-00' AND Amount > 0 AND Status = 'Approved' AND Reason = 'Sale' ORDER BY CapDate;");
			while (($id_payments, $amount, $deposit_date) = $sth2->fetchrow()) {


				&general_deposits($id_payments,$id_orders,'orders','Customer Deposit','Anticipo Clientes','','','CURDATE',$amount);
				my $queryu = "UPDATE sl_movements SET EffDate = '$deposit_date', Date = '$deposit_date', ID_journalentries = 0, ID_admin_users = '$id_admin_users' WHERE ID_tableused = '$id_orders' AND tableused = 'sl_orders' AND TIMESTAMPDIFF(SECOND,CONCAT(Date,' ',Time) , NOW()) BETWEEN 0 AND 5 AND ID_admin_users = '$usr{'id_admin_users'}';";
				#print "$queryu\n";
				&Do_SQL($queryu);

				#####
				##### 1.1) Fecha igual a la venta?
				#####

				if($sale_date) {

					$flag = 1;
					#### Eliminamos los Customer Deposit que tenga la orden
					my ($sth) = &Do_SQL("DELETE FROM sl_movements WHERE ID_tableused = '$id_orders' AND ID_accounts IN(".$cfg{'ida_bankscd'}.") AND Credebit='Credit' AND tableused='sl_orders' AND EffDate = '$sale_date';");
					#### Cambiamos el primer registro a categoria 'Sale'
					my ($sth) = &Do_SQL("UPDATE sl_movements SET Category='Ventas' WHERE ID_tableused = '$id_orders' AND Category='Anticipo Clientes' AND Credebit='Debit' AND tableused='sl_orders' AND EffDate = '$sale_date';");


					#####
					##### 1.2) No hay Decremento de anticipo 
					#####
					my $sth_ad = &Do_SQL("INSERT INTO sl_movements (ID_movements,ID_accounts,Amount,Reference,EffDate,tableused,ID_tableused,Category,Credebit,Status,Date,Time,ID_admin_users)
						SELECT
						0,ID_accounts,Amount,Reference,'$sale_date',tableused,ID_tableused,'Ventas','Debit',Status,CURDATE(),CURTIME(),1
						FROM sl_movements 
						WHERE ID_tableused='$id_orders' AND tableused = 'sl_orders' 
						AND ID_accounts IN(".$cfg{'ida_bankscd'}.") AND Credebit='Credit';");
					my ($ad) = $sth_ad->rows();

					if($ad > 0){

						if($diff_debs > 0){
							&Do_SQL("DELETE FROM sl_movements WHERE ID_tableused = '$id_orders' AND tableused = 'sl_orders' AND ID_accounts = '610' AND Credebit IN('Debit','');");
							$rt1 .= "Round Deleted +";

							$diff_debs = 0;

						}

						$str = qq|"$rt1 DEPOSIT APPLIED",$str|;

					}else{

						$str = qq|"$rt1 NO BANK",$str|;
					}


				}else{

					$str = qq|"ok","NO SALE DATE",$str|;

					if($sale_movs and abs($bank_cda - $bank_creds) > 0){
						$str .= qq|,"$rt1ERROR2"|;
					}
					$str .= qq|\n|;

					print $str;
					next SALE;

				}


			}

		}

		if($neg_movs){

			my ($sth3) = &Do_SQL("DELETE FROM sl_movements WHERE ID_tableused = '$id_orders' AND tableused = 'sl_orders' 
								AND ID_accounts IN(".$cfg{'ida_tax_payable'}.",".$cfg{'ida_tax_paid'}.",".$cfg{'ida_customer_ar'}.");");

			my ($stht) = &Do_SQL("SELECT SUM(Tax+ShpTax) FROM sl_orders_products WHERE ID_orders = '$id_orders' AND Status = 'Active' AND SalePrice > 0 AND Date <= '$sale_date';");
			my ($tax) = $stht->fetchrow();


			if($tax > 0) {

				## Tax must be separated
				&accounting_sale_separate_tax($id_orders,$cfg{'ida_banks'},$cfg{'ida_sales'},$sale_date,$tax);
				#### Cambiamos la fecha
				my ($sth) = &Do_SQL("UPDATE sl_movements SET EffDate = '$sale_date', Date = '$sale_date', ID_journalentries = 0, ID_admin_users = '$id_admin_users' WHERE ID_tableused = '$id_orders' AND tableused = 'sl_orders' AND TIMESTAMPDIFF(SECOND,CONCAT(Date,' ',Time) , NOW()) BETWEEN 0 AND 5 AND ID_admin_users = '$usr{'id_admin_users'}';");
				$str = qq|"TAX REPAIRED",$str|;

			}

		}else{
			$str = qq|"ok",$str|;			
		}

		(!$flag) and ($str = qq|"ERROR",$str|);
		if($sale_movs and abs($bank_cda - $bank_creds) > 0){
			$str .= qq|,"ERROR2"|;
		}
		$str .= qq|\n|;


		## ToDo: Agregar Nuevamente AR + CR? (9001038) 


		#### La orden tiene Flexipagos?
		&accounting_set_ar($id_orders,$cfg{'ida_bankfees'});
		#### La orden tiene Refunds?
		&accounting_sale_refund($id_orders,$cfg{'ida_banks'});
		

		####
		#### Suma Final, diferencia que aplicar?
		####
		&accounting_sale_difference($id_orders, 610,'Ventas');


		#### Cambiamos la fecha de la aplicacion
		my ($sth) = &Do_SQL("UPDATE sl_movements SET EffDate = (SELECT PostedDate FROM sl_orders WHERE ID_orders = '$id_orders') WHERE tableused='sl_orders' 
							AND ID_tableused = '$id_orders' AND 
							TIMESTAMPDIFF(MINUTE,CONCAT(Date,' ',Time) , NOW()) = 0 ;");


		print $str;


	}


}


#############################################################################
############################################################################# 
sub fix_payments{
#############################################################################
#############################################################################

	if($cfg{'bad_movs'} ne ''){

		my @ary = split(/,/, $cfg{'bad_movs'});
		my $i=0;

		for (0..$#ary){

			my $id_orders = int($ary[$_]);

			if($id_orders > 0){

				++$i;
				my ($sths) = &Do_SQL("SELECT SumProd, SumPay, TPay, IF(ABS(SumProd - SumPay) > 1,1,0) FROM
									(
										SELECT ID_orders, SUM(SalePrice + Shipping + Tax + ShpTax - Discount) AS SumProd
										FROM sl_orders_products WHERE ID_orders = '$id_orders'
										AND Status IN ('Active','Reship','Exchange','Undeliverable')
										AND SalePrice >= 0
										GROUP BY ID_orders
									)tmp
									INNER JOIN
									(
										SELECT ID_orders, SUM(Amount) AS SumPay, COUNT(*) AS TPay
										FROM sl_orders_payments WHERE ID_orders = '$id_orders'
										AND Status NOT IN('Credit','Void','Order Cancelled','Cancelled','Pending')
										AND Amount >= 0
										GROUP BY ID_orders
									)tmp2
									USING (ID_orders);");
				my ($sumprod, $sumpay, $tpay, $to_fix) = $sths->fetchrow();

				if($to_fix){

					#######
					####### Hay diferencia entre lo pagado y los productos
					#######

					if($sumpay > $sumprod and ($sumpay - $sumprod) > 10 and $tpay == 1){

						my $query = "/*Old Amount = $sumpay */UPDATE sl_orders_payments SET Amount = '$sumprod' WHERE ID_orders = '$id_orders' 
								AND Status NOT IN('Credit','Void','Order Cancelled','Cancelled') AND Amount > $sumprod LIMIT 1;";
						&Do_SQL($query);

						print "$i - $query\n";

					}else{
						print "$i,$id_orders,$sumpay,$sumprod,$tpay,$to_fix\n";
					}


				}else{
					print "$i,$id_orders,$sumprod,$sumpay,$tpay,$to_fix\n";
				}


			}

		}

	}


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
