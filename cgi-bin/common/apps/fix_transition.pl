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
	&process_transition;
	&disconnect_db;

}


#############################################################################
#############################################################################
#   Function: process_transition_file
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
sub process_transition {
#############################################################################
#############################################################################
	
	#print "Content-type: text/html\n\n";

	my $query = "SELECT
ID_tableused AS ID_orders,
SUM(IF(Credebit = 'Debit',Amount,0)) AS Debits,
SUM(IF(Credebit = 'Credit',Amount,0)) AS Credits,
EffDate,
SUM(IF(Category = 'Ventas',1,0)) AS MovSale,
SUM(IF(Category = 'Cambios Fisicos',1,0)) AS MovEx,
SUM(IF(Category = 'Devoluciones',1,0)) AS MovRet,
SUM(IF(Category = 'Pagos',1,0)) AS MovRef,
SUM(IF(Credebit = 'Debit' AND ID_accounts IN(137),Amount,0)) AS AmoutInv,
SUM(IF(Credebit = 'Debit' AND ID_accounts IN(76),Amount,0)) AS AmoutSale,
SUM(IF(Credebit = 'Debit' AND ID_accounts IN(137),Amount,0)) / SUM(IF(Credebit = 'Debit' AND ID_accounts IN(359),Amount,0)) AS Pct
FROM sl_movements
WHERE tableused = 'sl_orders'
AND Status = 'Active'
GROUP BY ID_tableused
HAVING AmoutInv > 0 /*AND Pct * 100 < 30
HAVING MovSale = 0 AND MovEx = 0 AND MovRet = 0 AND MovRef = 0*/
ORDER BY 
SUM(IF(Credebit = 'Debit' AND ID_accounts IN(137),Amount,0)) / SUM(IF(Credebit = 'Debit' AND ID_accounts IN(359),Amount,0)) DESC,
SUM(IF(Credebit = 'Debit' AND ID_accounts IN(137),Amount,0)),
EffDate DESC,
ID_tableused";

	my $i=0;
	my ($sth) = &Do_SQL($query);
	while( $rec = $sth->fetchrow_hashref() ){

		++$i;

		print "\n\nNo:$i\nID: $rec->{'ID_orders'}\n";
		my ($sth) = &Do_SQL("SELECT Ptype, Type FROM sl_orders INNER JOIN sl_customers USING(ID_customers) WHERE ID_orders = '$rec->{'ID_orders'}';");
		my ($order_type, $ctype) = $sth->fetchrow();


		&Do_SQL("DELETE FROM sl_movements WHERE ID_tableused = '$rec->{'ID_orders'}' AND Category = 'Devoluciones' AND ID_accounts IN(137,367);");
		my ($sth) = &Do_SQL("SELECT ABS(Cost),Related_ID_products,PostedDate FROM sl_orders_products WHERE ID_orders = '$rec->{'ID_orders'}' AND Status = 'Returned' AND Cost < 0;");
		while(my ($cost,$relid,$effdate) = $sth->fetchrow()){

			print "Sku: $relid\nCost: $cost\nDate: $effdate\n";
			## Movimientos Contables
			my @params = ($rec->{'ID_orders'},$relid,$cost);
			&accounting_keypoints('order_skus_backtoinventory_'. $ctype .'_'. $order_type, \@params );
			&Do_SQL("UPDATE sl_movements SET EffDate = '$effdate' WHERE ID_tableused = '$rec->{'ID_orders'}' AND tableused = 'sl_orders' AND TIMESTAMPDIFF(SECOND,CONCAT(Date,' ',Time) , NOW()) BETWEEN 0 AND 5 ;");

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
