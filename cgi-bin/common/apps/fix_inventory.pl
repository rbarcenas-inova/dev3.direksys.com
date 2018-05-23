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
local ($cfg{'id_warehouses'}) = 1001;
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
	&fix_inventory;
	&disconnect_db;

}


#############################################################################
#############################################################################
#   Function: fix_inventory
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
sub fix_inventory {
#############################################################################
#############################################################################
	


	my ($query_f) = "SELECT 
						`sl_warehouses`.`ID_warehouses`, 
						Name,
						sl_warehouses_location.ID_products,
						sl_warehouses_location.ID_products - 400000000 AS ID_parts,
						SUM(`sl_warehouses_location`.Quantity)AS WLQ,
						IF(SCQ IS NOT NULL, SCQ,0)AS SCQ
					FROM `sl_warehouses` 
					INNER JOIN sl_warehouses_location USING(ID_warehouses)
					LEFT JOIN 
					(
						SELECT ID_warehouses, ID_products, SUM(Quantity)AS SCQ
						FROM sl_skus_cost GROUP BY ID_warehouses, ID_products
						ORDER BY ID_warehouses, ID_products
					)tmp
					USING(ID_warehouses)
					WHERE `Type` = 'Virtual'
					AND `sl_warehouses_location`.ID_products = `tmp`.ID_products
					GROUP BY `sl_warehouses`.ID_warehouses, sl_warehouses_location.ID_products
					HAVING WLQ - SCQ > 0
					ORDER BY sl_warehouses_location.ID_products,`sl_warehouses`.ID_warehouses
					/*LIMIT 10*/;";

	my ($query_f2) = "SELECT 
						`sl_warehouses`.`ID_warehouses`, 
						Name,
						sl_warehouses_location.ID_products,
						sl_warehouses_location.ID_products - 400000000 AS ID_parts,
						SUM(`sl_warehouses_location`.Quantity)AS WLQ,
						0 AS SCQ
					FROM `sl_warehouses` 
					INNER JOIN sl_warehouses_location USING(ID_warehouses)
					WHERE `Type` = 'Virtual'
					AND 1 > (SELECT COUNT(*) FROM sl_skus_cost WHERE ID_warehouses = sl_warehouses_location.ID_warehouses AND ID_products = sl_warehouses_location.ID_products)
					GROUP BY `sl_warehouses`.ID_warehouses, sl_warehouses_location.ID_products
					ORDER BY `sl_warehouses`.ID_warehouses, sl_warehouses_location.ID_products;";				

	#print "/*Query Inicial */ \n$query_f\n\n"; #9041969,9041999,9042214,9043892,9049288


	for(1..2){

		my $query = $_ == 1 ? $query_f : $query_f2;

		print "$query\n\n";

		my ($sth) = &Do_SQL($query);

		my $i=0;
		SCAN: while (my ( $id_warehouses, $wname, $id_skus, $id_parts, $wqty, $sqty  ) = $sth->fetchrow() ) {
			
			++$i;
			my $pname =&load_name('sl_parts', 'ID_parts', $id_parts, 'Name');
			my $quantity_to_fix = $wqty - $sqty;

			print qq|"$id_warehouses","$wname","$id_skus","$pname","$wqty","$sqty","$quantity_to_fix"\n|;

			do{

				#######
				####### Tenemos registro previo?
				#######
				my ($sth) = &Do_SQL("SELECT ID_skus_cost FROM sl_skus_cost WHERE ID_warehouses = '$id_warehouses' AND ID_products = '$id_skus' AND Quantity > 0 ORDER BY Date DESC LIMIT 1;");
				my ($idsc) = $sth->fetchrow();


				if($idsc){

					###
					### 1) Si hay registro
					###
					&Do_SQL("UPDATE sl_skus_cost SET Quantity = Quantity + $quantity_to_fix WHERE ID_skus_cost = '$idsc';");

				}else{

					###
					### 2) No hay registro
					###
					my ($sth) = &Do_SQL("SELECT Cost FROM sl_skus_cost WHERE ID_warehouses = '".$cfg{'id_warehouses'}."' AND ID_products = '$id_skus' AND Quantity > 0 ORDER BY Date DESC LIMIT 1;");
					my ($cost) = $sth->fetchrow();

					$cost = &load_sltvcost($id_skus) if !$cost;

					&Do_SQL("INSERT INTO sl_skus_cost SET ID_products = '$id_skus', ID_warehouses = '$id_warehouses', Tblname = 'transfer', Quantity = $quantity_to_fix, Cost = '$cost', Date = CURDATE(), Time = CURTIME(), ID_admin_users = '".$usr{'id_admin_users'}."';");

				}

				$quantity_to_fix = 0;

			}while ($quantity_to_fix);


		}

	}


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
