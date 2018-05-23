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
# use File::Copy;

# local ($dir) = getcwd;
# Default la 2 porque este proceso fue diseñado para TMK
local(%in) = &parse_form;
# local ($in{'e'}) = 2 if (!$in{'e'});
# chdir($dir);

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
	&fix_accounting;
	&disconnect_db;

}


#################################################################
#################################################################
#	Function: fix_accounting
#
#   Inserta movimientos faltantes de costo de ventas
#
#	Created by: Jonathan Alcantara
#
#
#	Modified By:Jonathan Alcantara
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
sub fix_accounting{
#################################################################
#################################################################
	my $process = ($in{'process'} ne 'commit')? qq|<span style="color:#000;background-color:gray;padding:5px;">ANALYZING</span>|:qq|<span style="color:#FFF;background-color:red;padding:5px;">EXECUTING</span>|;
	my $log_email;
	my $easy_fix=0;
	my $hard_fix=0;
	my $hard_fix_quantity=0;

	&load_settings;
	print "Content-type: text/html\n\n";
	print qq|<meta http-equiv="content-type" content="text/html; charset=utf-8" />\n\n|;
	print qq|<title>FIX :: sl_skus_cost & sl_warehouses_locations</title>\n\n|;
	print "<h4>DIREKSYS $cfg{'app_title'} (e$in{'e'}) - Fix sl_skus_cost & sl_warehouses_location</h5>";
	
	if (!$in{'e'}){
		print qq|<span style="color:red;">ID de empresa es requerido</span>|;
		return;
	}

	my $sql ="
		SELECT *
		FROM (
			SELECT
			sl_orders.ID_orders
			, sl_orders.Ptype
			, sl_orders.Status
			, SUM(sl_orders_parts.Cost*sl_orders_parts.Quantity)TotalCostParts
			FROM sl_orders
			INNER JOIN sl_orders_products ON sl_orders.ID_orders=sl_orders_products.ID_orders
			INNER JOIN sl_orders_parts ON sl_orders_parts.ID_orders_products=sl_orders_products.ID_orders_products
			WHERE sl_orders.Date>='2015-11-01'
			AND sl_orders.Status !='Cancelled'
			AND sl_orders_products.ID_products<=600000000
			GROUP BY sl_orders.ID_orders
		)products
		INNER JOIN (
			SELECT
			sl_movements.ID_tableused ID_orders
			, SUM(sl_movements.Amount) Amount
			FROM sl_movements
			WHERE sl_movements.Date>='2015-11-01'
			AND sl_movements.tableused = 'sl_orders'
			AND sl_movements.ID_accounts = 1253
			AND sl_movements.Credebit = 'Debit'
			AND sl_movements.Status = 'Active'
			GROUP BY sl_movements.tableused, sl_movements.ID_tableused
		)movements ON movements.ID_orders=products.ID_orders
		WHERE ROUND(movements.Amount,2)!=products.TotalCostParts
	";

	my $sth = &Do_SQL($sql);
	print qq
	|
	<table border=1>
	|;

	while (my $rec = $sth->fetchrow_hashref()){
		$sql2 = "SELECT sl_orders_products.*
				FROM sl_orders_parts
				INNER JOIN sl_orders_products ON sl_orders_products.ID_orders_products = sl_orders_parts.ID_orders_products
				WHERE sl_orders_products.ID_orders=$rec->{'ID_orders'};
		";
		print qq
		|<tr>
			<td width="20%">
					$sql2
			</td>
		|;
		my $sth2 = &Do_SQL($sql2);
		print qq
		|
			<td width="80%">
			<table border=1>
				<tr>
				<td>
		|;
		my @prods_costs;
		while (my $rec2 = $sth2->fetchrow_hashref()){
			push @prods_costs, $rec2->{'Cost'};
		}
		print "prods_costs = <br>";
		foreach my $prods_costs(@prods_costs) {
		    print "<strong>".$prods_costs."</strong><br>";
		}
		my @movs_costs;
		$sql3 = "SELECT sl_movements.ID_movements,
				sl_movements.ID_tableused ID_orders
				, SUM(sl_movements.Amount) Amount
				FROM sl_movements
				WHERE sl_movements.Date>='2015-11-01'
				AND sl_movements.tableused = 'sl_orders'
				AND sl_movements.ID_tableused = ".$rec->{'ID_orders'}."
				AND sl_movements.ID_accounts = 1253
				AND sl_movements.Credebit = 'Debit'
				AND sl_movements.Status = 'Active'
				GROUP BY sl_movements.ID_movements, sl_movements.tableused, sl_movements.ID_tableused
		";
		my $sth3 = &Do_SQL($sql3);
		my $primerMov = 0;
		while (my $rec3 = $sth3->fetchrow_hashref()){
			if ($primerMov == 0) {
				$primerMov = $rec3->{'ID_movements'};
			}
			push @movs_costs, $rec3->{'Amount'};
		}
		print "movs_costs = <br>";
		foreach my $movs_costs(@movs_costs) {
		    print "<strong>".$movs_costs."</strong><br>";
		}
		OUTER: for my $i(0..$#movs_costs){
			INNER: for my $j(0..$#prods_costs){
				if (round($movs_costs[$i], 2) == round($prods_costs[$j], 2)) {
					splice @prods_costs, $j, 1;
					last INNER ;
				}
			}
		}
		print "faltantes = <br>";
		foreach my $prods_costs(@prods_costs) {
		    print "<strong>".$prods_costs."</strong><br>";
		}
		#print "PrimerMov = ". $primerMov."<br>";
		$sql4 = "SELECT ID_accounts, Amount, Reference, EffDate, tableused, ID_tableused, 
				tablerelated, ID_tablerelated, Category, Credebit, ID_segments, ID_journalentries, Status, Date, 
				Time, ID_admin_users
				FROM sl_movements
				WHERE sl_movements.ID_movements = $primerMov;
		";
		my $sth4 = &Do_SQL($sql4);
		while (my $rec4 = $sth4->fetchrow_hashref()){
			foreach my $prods_costs(@prods_costs) {
		    	print $sql5 = "INSERT INTO sl_movements(ID_accounts, Amount, Reference, EffDate, tableused, ID_tableused, 
						tablerelated, ID_tablerelated, Category, Credebit, ID_segments, ID_journalentries, Status, Date, 
						Time, ID_admin_users) 
						VALUES('1253', '".$prods_costs."', '".$rec4->{'Reference'}."', '".$rec4->{'EffDate'}."', '".$rec4->{'tableused'}."', '".$rec4->{'ID_tableused'}."', 
						'".$rec4->{'tablerelated'}."', '".$rec4->{'ID_tablerelated'}."', '".$rec4->{'Category'}."', 'Debit', '".$rec4->{'ID_segments'}."', NULL, '".$rec4->{'Status'}."', '".$rec4->{'Date'}."', 
						'".$rec4->{'Time'}."', '6');";
				my $sth5 = &Do_SQL($sql5);
				print "<br>"; 
				print $sql6 = "INSERT INTO sl_movements(ID_accounts, Amount, Reference, EffDate, tableused, ID_tableused, 
						tablerelated, ID_tablerelated, Category, Credebit, ID_segments, ID_journalentries, Status, Date, 
						Time, ID_admin_users) 
						VALUES('1106', '".$prods_costs."', '".$rec4->{'Reference'}."', '".$rec4->{'EffDate'}."', '".$rec4->{'tableused'}."', '".$rec4->{'ID_tableused'}."', 
						'".$rec4->{'tablerelated'}."', '".$rec4->{'ID_tablerelated'}."', '".$rec4->{'Category'}."', 'Credit', '0', NULL, '".$rec4->{'Status'}."', '".$rec4->{'Date'}."', 
						'".$rec4->{'Time'}."', '6');";
				my $sth6 = &Do_SQL($sql6);
				print "<br>"; 
				print "<br>"; 
			}
		}
		print qq
		|
			</td>
			<td>
		|;
		print qq
		|
		</td>
		</tr>
		</table>
		</td>
		</tr>
		|;
		#&Do_SQL($sql) if ($in{'process'} eq 'commit');
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

sub validate_state_zipcode{
	my ($orig_zipcode,$orig_state) = @_;
	&Do_SQL("SET NAMES utf8");
	$sql = "SELECT ZipCode, StateFullName FROM sl_zipcodes WHERE Status='Active' AND zipcode='$orig_zipcode' AND StateFullName='$orig_state' GROUP BY ZipCode, StateFullName";
	my $sth = &Do_SQL($sql);
	my ($zipcode,$state) = $sth->fetchrow_array();

	if ( lc($state) eq lc($orig_state) ){
		return 0;
	}else{
		return "BD=$state != LO=$orig_state";
	}
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
	print qq|<div style="border:solid 1px #666;padding:3px;"><span style="font-size:10px;color:#0099FF;">$sql</span></div>|;
}