#!/usr/bin/perl
#######################################################################
#######################################################################
#######################################################################

#use strict;
#use Perl::Critic;
##use DBI;
##use DBIx::Connector;
##use DBD::mysql;
use Cwd;
use File::Copy;


use DBI;
use DBD::mysql;

# local ($dir) = getcwd;
# Default la 2 porque este proceso fue diseñado para TMK
#local(%in) = &parse_form;
local ($in{'e'}) = 4 if (!$in{'e'});
# chdir($dir);

$in{'process'} = 'commit';

# Required Libraries
# --------------------------------------------------------
eval {
	require ('../subs/auth.cgi');
	require ('../subs/sub.base.html.cgi');
	require ('../subs/sub.func.html.cgi');
	require ('cybersubs.cgi');
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
#	Modified By: Alejandro Diaz
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
	&accounting;
	&disconnect_db;

}


#################################################################
#################################################################
#	Function: execute_outsourcing_batch
#
#   		This functions reads from several outsourcing callcenters /home/ccname/orders paths. The file inside contains orders created by Listen Up Callcenter to be processed in Direksys. The script validate and create every order and send them to authorize if necessary
#
#	Created by: _Roberto Barcenas_
#
#
#	Modified By:Alejandro Diaz
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
sub accounting{
#################################################################
#################################################################
	my $process = ($in{'process'} ne 'commit')? qq|<span style="color:#000;background-color:gray;padding:5px;">ANALYZING</span>|:qq|<span style="color:#FFF;background-color:red;padding:5px;">EXECUTING</span>|;
	my $log_email;

	&load_settings;
	print "Content-type: text/html\n\n";
	print qq|<meta http-equiv="content-type" content="text/html; charset=utf-8" />\n\n|;
	print "<h4>DIREKSYS $cfg{'app_title'} (e$in{'e'}) - CONTABILIDAD $process</h5>";
	
	if (!$in{'e'}){
		print qq|<span style="color:red;">ID de empresa es requerido</span>|;
		return;
	}
	
	## Definicion de rango de fechas
	$in{'date_from'} = '2014-01-01';
	$in{'date_to'} = '2014-11-11'; # Solo cambiar el mes, para no buscar dia de fin de mes

	$sys{'fmt_curr_decimal_digits'} = 2 if(!$sys{'fmt_curr_decimal_digits'});

	#my ($sth2) = &Do_SQL("DELETE FROM `sl_movements` WHERE `ID_movements` >=4740347");


	# NOTAS DE CREDITO
	print qq|<H2 style="color:red;">N O T A S   DE   C R E D I T O -- ORDERS</H2>|;

	$sql = "
	SELECT 
		cu_invoices.invoice_type
		,cu_invoices_lines.ID_invoices_lines
		,cu_invoices_lines.ID_invoices
		,cu_invoices_lines.ID_orders
		,cu_invoices_lines.ID_creditmemos
		,cu_invoices_lines.ID_debitmemos
		,cu_invoices_lines.ID_orders_products
		,cu_invoices_lines.description
		,cu_invoices.doc_date
		,cu_invoices.invoice_net
		,cu_invoices.total_taxes_transfered
		,cu_invoices.invoice_total
		,(cu_invoices.invoice_net+cu_invoices.total_taxes_transfered)TOTAL_SQL
		, SUM(sl_orders_products.Cost) Cost
		, SUM(sl_orders_products.Shipping) Shipping
		, SUM(sl_orders_products.SalePrice-sl_orders_products.Discount) SalePrice
	FROM cu_invoices INNER JOIN cu_invoices_lines ON cu_invoices.ID_invoices=cu_invoices_lines.ID_invoices
	LEFT JOIN sl_orders_products ON sl_orders_products.ID_orders_products=cu_invoices_lines.ID_orders_products
	WHERE cu_invoices.Status='Certified'
	AND cu_invoices.invoice_type='egreso'
	AND cu_invoices_lines.ID_orders>0
	AND DATE(cu_invoices.doc_date) >= '$in{'date_from'}'
	AND DATE(cu_invoices.doc_date) < '$in{'date_to'}'
	GROUP BY cu_invoices_lines.ID_invoices
	ORDER BY cu_invoices_lines.ID_invoices";
	($sth) = &Do_SQL($sql);
	&print_query($sql);
	print qq|<table border="1" style="font-size:10px;" padding="2">
	<tr>
		<td>invoice_type</td>
		<td>ID_invoices_lines</td>
		<td>ID_invoices</td>
		<td>ID_orders</td>
		<td>ID_creditmemos</td>
		<td>ID_debitmemos</td>
		<td>ID_orders_products</td>
		<td>description</td>
		<td>doc_date</td>
		<td>invoice_net</td>
		<td>Shipping</td>
		<td>total_taxes_transfered</td>
		<td>invoice_total</td>
		<td>TOTAL_SQL</td>
		<td>Cost</td>
	</tr>|;
	while ( $rec = $sth->fetchrow_hashref()){
		my ($id_orders) = $rec->{'ID_orders'};
		print qq|
		<tr>
			<td>&nbsp;$rec->{'invoice_type'}</td>
			<td>&nbsp;$rec->{'ID_invoices_lines'}</td>
			<td>&nbsp;$rec->{'ID_invoices'}</td>
			<td>&nbsp;$rec->{'ID_orders'}</td>
			<td>&nbsp;$rec->{'ID_creditmemos'}</td>
			<td>&nbsp;$rec->{'ID_debitmemos'}</td>
			<td>&nbsp;$rec->{'ID_orders_products'}</td>
			<td>&nbsp;$rec->{'description'}</td>
			<td>&nbsp;$rec->{'doc_date'}</td>
			<td>&nbsp;$rec->{'invoice_net'}</td>
			<td>&nbsp;$rec->{'total_taxes_transfered'}</td>
			<td>&nbsp;$rec->{'invoice_total'}</td>
			<td>&nbsp;$rec->{'TOTAL_SQL'}</td>
		</tr>|;

		# Se modifican Status a sl_movements
		$sql = "UPDATE sl_movements SET Status='Direksys_Active' WHERE tableused='sl_orders' AND ID_tableused='$id_orders' AND Status='Active' AND DATE <= '2014-11-12' AND DATE >= '2014-01-01'";
		&print_query($sql);
		my ($sth2) = &Do_SQL($sql) if ($in{'process'} eq 'commit');
		
		$sql = "UPDATE sl_movements SET Status='Direksys_Pending' WHERE tableused='sl_orders' AND ID_tableused='$id_orders' AND Status='Pending' AND DATE <= '2014-11-12' AND DATE >= '2014-01-01'";
		&print_query($sql);
		my ($sth2) = &Do_SQL($sql) if ($in{'process'} eq 'commit');
		
		# Se genera nueva contabilidad para esta factura / orden
		# Se inserta 1 por cada cuenta contable

		$sql = "SELECT ID_salesorigins, Ptype FROM sl_orders WHERE ID_orders='$id_orders';";
		&print_query($sql);
		my ($sth2) = &Do_SQL($sql);
		my ($id_salesorigins, $ptype) = $sth2->fetchrow();
		
		# Cuentas contables
		my $cta_ventas = 359;
		my $cta_envio = 355;
		my $cta_iva = 265;
		my $cta_costo = 367;
		my $cta_inventario = 137;
		my $cta_reembolso = 238;
		my $cta_banco = 32;

		if ($in{'e'} == 4){
			$cta_banco = 25;
		}

		## Se insertan Mov Contables
		$sql = "INSERT INTO sl_movements (ID_movements, ID_accounts, Amount, Reference, EffDate, tableused, ID_tableused, tablerelated, ID_tablerelated, Category, Credebit, ID_segments, ID_journalentries, Status, Date, Time, ID_admin_users) 
		VALUES (NULL, '$cta_ventas', '$rec->{'SalePrice'}', '', '$rec->{'doc_date'}', 'sl_orders', '$id_orders', NULL, 0, 'Devoluciones', 'Debit', 0, 0, 'Active', CURDATE(), CURTIME(), 1);";
		&print_query($sql);
		my ($sth2) = &Do_SQL($sql) if ($in{'process'} eq 'commit');

		$sql = "INSERT INTO sl_movements (ID_movements, ID_accounts, Amount, Reference, EffDate, tableused, ID_tableused, tablerelated, ID_tablerelated, Category, Credebit, ID_segments, ID_journalentries, Status, Date, Time, ID_admin_users) 
		VALUES (NULL, '$cta_envio', '$rec->{'Shipping'}', '', '$rec->{'doc_date'}', 'sl_orders', '$id_orders', NULL, 0, 'Devoluciones', 'Debit', 0, 0, 'Active', CURDATE(), CURTIME(), 1);";
		&print_query($sql);
		my ($sth2) = &Do_SQL($sql) if ($rec->{'Shipping'} > 0 and $in{'process'} eq 'commit');
		
		$sql = "INSERT INTO sl_movements (ID_movements, ID_accounts, Amount, Reference, EffDate, tableused, ID_tableused, tablerelated, ID_tablerelated, Category, Credebit, ID_segments, ID_journalentries, Status, Date, Time, ID_admin_users) 
		VALUES (NULL, '$cta_iva', '$rec->{'total_taxes_transfered'}', '', '$rec->{'doc_date'}', 'sl_orders', '$id_orders', NULL, 0, 'Devoluciones', 'Debit', 0, 0, 'Active', CURDATE(), CURTIME(), 1);";
		&print_query($sql);
		my ($sth2) = &Do_SQL($sql) if ($rec->{'total_taxes_transfered'} > 0 and $in{'process'} eq 'commit');

		$sql = "INSERT INTO sl_movements (ID_movements, ID_accounts, Amount, Reference, EffDate, tableused, ID_tableused, tablerelated, ID_tablerelated, Category, Credebit, ID_segments, ID_journalentries, Status, Date, Time, ID_admin_users) 
		VALUES (NULL, '$cta_costo', '$rec->{'Cost'}', '', '$rec->{'doc_date'}', 'sl_orders', '$id_orders', NULL, 0, 'Devoluciones', 'Credit', 0, 0, 'Active', CURDATE(), CURTIME(), 1);";
		&print_query($sql);
		my ($sth2) = &Do_SQL($sql) if ($in{'process'} eq 'commit');

		$sql = "INSERT INTO sl_movements (ID_movements, ID_accounts, Amount, Reference, EffDate, tableused, ID_tableused, tablerelated, ID_tablerelated, Category, Credebit, ID_segments, ID_journalentries, Status, Date, Time, ID_admin_users) 
		VALUES (NULL, '$cta_inventario', '$rec->{'Cost'}', '', '$rec->{'doc_date'}', 'sl_orders', '$id_orders', NULL, 0, 'Devoluciones', 'Debit', 0, 0, 'Active', CURDATE(), CURTIME(), 1);";
		&print_query($sql);
		my ($sth2) = &Do_SQL($sql) if ($in{'process'} eq 'commit');
		
		$sql = "INSERT INTO sl_movements (ID_movements, ID_accounts, Amount, Reference, EffDate, tableused, ID_tableused, tablerelated, ID_tablerelated, Category, Credebit, ID_segments, ID_journalentries, Status, Date, Time, ID_admin_users) 
		VALUES (NULL, '$cta_reembolso', '$rec->{'invoice_total'}', '', '$rec->{'doc_date'}', 'sl_orders', '$id_orders', NULL, 0, 'Devoluciones', 'Credit', 0, 0, 'Active', CURDATE(), CURTIME(), 1);";
		&print_query($sql);
		my ($sth2) = &Do_SQL($sql) if ($in{'process'} eq 'commit');
		
		$sql = "INSERT INTO sl_movements (ID_movements, ID_accounts, Amount, Reference, EffDate, tableused, ID_tableused, tablerelated, ID_tablerelated, Category, Credebit, ID_segments, ID_journalentries, Status, Date, Time, ID_admin_users) 
		VALUES (NULL, '$cta_banco', '$rec->{'invoice_total'}', '', '$rec->{'doc_date'}', 'sl_orders', '$id_orders', NULL, 0, 'Reembolsos', 'Credit', 0, 0, 'Active', CURDATE(), CURTIME(), 1);";
		&print_query($sql);
		my ($sth2) = &Do_SQL($sql) if ($in{'process'} eq 'commit');

		$sql = "INSERT INTO sl_movements (ID_movements, ID_accounts, Amount, Reference, EffDate, tableused, ID_tableused, tablerelated, ID_tablerelated, Category, Credebit, ID_segments, ID_journalentries, Status, Date, Time, ID_admin_users) 
		VALUES (NULL, '$cta_reembolso', '$rec->{'invoice_total'}', '', '$rec->{'doc_date'}', 'sl_orders', '$id_orders', NULL, 0, 'Reembolsos', 'Debit', 0, 0, 'Active', CURDATE(), CURTIME(), 1);";
		&print_query($sql);
		my ($sth2) = &Do_SQL($sql) if ($in{'process'} eq 'commit');


		##
		## Al final se debe mandar ejecutar &accounting_set_segment($id_orders, $id_salesorigins)
		&accounting_set_segment($id_orders, $id_salesorigins);		
	}
	print qq|</table>|;

	print "hasta aqui llegamos...";


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

sub load_settings {
	my ($fname);
	
	if ($in{'e'}) {
		$fname = "../general.e".$in{'e'}.".cfg";
	}else {
		$fname = "../general.ex.cfg";
	}

	## general
	open (CFG, "<$fname") or &cgierr ("Unable to open: $fname,160,$!");
	LINE: while (<CFG>) {
		(/^#/)      and next LINE;
		(/^\s*$/)   and next LINE;
		$line = $_;
		$line =~ s/\n|\r//g;
		my ($td,$name,$value) = split (/\||\=/, $line,3);
		if ($td eq "conf") {
			$cfg{$name} = $value;
			next LINE;
		}elsif ($td eq "sys"){
			$sys{$name} = $value;
			next LINE;
		}
	}
	close CFG;

}

sub parse_form {
# --------------------------------------------------------
	my (@pairs, %in);
	my ($buffer, $pair, $name, $value);

	if ($ENV{'REQUEST_METHOD'} eq 'GET') {
		@pairs = split(/&/, $ENV{'QUERY_STRING'});
	}elsif ($ENV{'REQUEST_METHOD'} eq 'POST') {
		read(STDIN, $buffer, $ENV{'CONTENT_LENGTH'});
 		@pairs = split(/&/, $buffer);
	}else {
		&cgierr ("This script must be called from the Web\nusing either GET or POST requests\n\n");
	}
	PAIR: foreach $pair (@pairs) {
		($name, $value) = split(/=/, $pair);

		$name =~ tr/+/ /;
		$name =~ s/%([a-fA-F0-9][a-fA-F0-9])/pack("C", hex($1))/eg;
		$name = lc($name);

		$value =~ tr/+/ /;
		$value =~ s/%([a-fA-F0-9][a-fA-F0-9])/pack("C", hex($1))/eg;

		$value =~ s/^\s+//g;
		$value =~ s/\s+$//g;

		#$value =~ s/\r//g;
		$value =~ s/<!--(.|\n)*-->//g;			# Remove SSI.
		if ($value eq "---") { next PAIR; }		# This is used as a default choice for select lists and is ignored.
		(exists $in{$name}) ?
			($in{$name} .= "|$value") :		# If we have multiple select, then we tack on
			($in{$name}  = $value);			# using the ~~ as a seperator.
	}
	return %in;
}

sub print_query{
	my ($sql) = @_;
	print qq|\n\n\n$sql\n\n\n|;
}

sub accounting_set_segment{
#############################################################################
#############################################################################

	my ($id_orders, $id_salesorigins) = @_;

	if($cfg{'accounting_use_segments'}) {
		my ($id_segments);
			(!$id_salesorigins) and ($id_salesorigins = $cfg{'default_origin'});
			my ($sth2) = &Do_SQL("SELECT ID_accounts_segments FROM sl_salesorigins WHERE ID_salesorigins = '$id_salesorigins' LIMIT 1;");
			$id_segments = $sth2->fetchrow();
		
		if($id_segments) {

			&Do_SQL("SET group_concat_max_len = 204800;");
			my ($stha) = &Do_SQL("SELECT GROUP_CONCAT(ID_accounts) FROM sl_accounts WHERE Segment =  'Yes';");
			my ($id_accounts_grouped) = $stha->fetchrow();

			if($id_accounts_grouped){
				my ($sth2) = &Do_SQL("UPDATE sl_movements SET ID_segments = '$id_segments' WHERE ID_tableused = '$id_orders' AND ID_segments = 0 AND ID_accounts IN($id_accounts_grouped) AND TIMESTAMPDIFF(MINUTE,CONCAT(Date,' ',Time) , NOW()) = 0 ;");
			}

		}

	}

}
