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
	&fix_cost_products;
	&disconnect_db;

}


#################################################################
#################################################################
#	Function: fix_cost_products
#
#	Created by: Arturo Hernandez
#
#   	Parameters:
#
#   	Returns:
#
#   	See Also:
#

sub fix_cost_products{
#################################################################
#################################################################
	&load_settings;
	print "Content-type: text/html\n\n";
	print qq|<meta http-equiv="content-type" content="text/html; charset=utf-8" />\n\n|;
	print qq|<title>FIX :: sl_skus_cost & sl_warehouses_locations</title>\n\n|;
	my $process = ($in{'process'} ne 'commit') ? qq|<span style="color: gray;">ANALYZING</span>| : qq|<span style="color: red;">EXECUTING</span>|;
	print "<h4>DIREKSYS $cfg{'app_title'} (e$in{'e'}) - FIX :: sl_skus_cost & sl_warehouses_locations .:: $process ::.</h5>";

	if (!$in{'e'}){
		print qq|<span style="color:red;">ID de empresa es requerido</span>|;
		return;
	}
	$dir = 'cost.csv';
	if(-e $dir) {
		if(-r $dir  and open (FILE, $dir)){
			print "abriendo: ".$dir." <br>";
			print qq|<table border="1" cellpadding="0" cellspacing="1" style="font-size: 11pt; max-width: 1000px;">|;
			while ($record = <FILE>) {
				chomp $record;
				$registers1++;
				my @fields = split "," , $record;

				#Valida el costo...
				my $cost_csv = $fields[2];				
				if( $#fields > 2 ){
					$cost_csv .= $fields[3];
				}
				$cost_csv =~ s/[" ]//g;

				print qq|<tr><td colspan="8" style="text-align:center;font-weight:bold;">$fields[0]</td></tr>
						<tr style="background-color:#848484;">
							<td>ID Warehouses</td>
							<td>Quantity</td>
							<td>Quantity skus</td>
							<td>Diff</td>
							<td>Cost</td>
							<td>Cost CSV</td>
							<td>Delete</td>
							<td>Insert</td>
						</tr>|;
				my ($sth) = &Do_SQL("SELECT ID_warehouses, ID_products, SUM(Quantity) AS xQuantity 
									 FROM sl_warehouses_location 
									 WHERE ID_products = $fields[0] 
									 GROUP BY ID_warehouses, ID_products
									 ORDER by ID_warehouses_location DESC");
				while(my ($ID_warehouses, $ID_products, $Quantity) = $sth->fetchrow_array ){
					if($Quantity > 0){
						my ($sth2) = &Do_SQL("SELECT ID_skus_cost, ID_products, Quantity, Cost, ID_warehouses 
											  FROM sl_skus_cost 
											  WHERE ID_products = $ID_products 
											  	AND ID_warehouses = $ID_warehouses 
											  ORDER BY ID_warehouses ASC");
						my ($sku_id_skus_cost, $sku_id_products, $sku_quantity, $sku_cost, $sku_id_warehouses) = $sth2->fetchrow;
						my ($dif) = $sku_quantity - $Quantity;
						$color = ($dif == 0) ? 'green' : 'red';
						$colorCost = ($sku_cost == $fields[2]) ? 'green' : 'red';				
						
						my $rslt_dlt = "---";
						my $rslt_ins = "---";
						if( $in{'process'} ){
							&Do_SQL("BEGIN;");

							$delete =  "DELETE 
										FROM sl_skus_cost 
										WHERE ID_products = $ID_products 
											AND ID_warehouses = $ID_warehouses;";
							eval{
								my $dth_dlt = &Do_SQL($delete);
								$rslt_dlt = '<span style="color: green;">OK[ '.$dth_dlt->rows." ]</span>";
							};
							if( $@ ){
								&Do_SQL("ROLLBACK;");
								$rslt_dlt = '<span style="color: red;">ERROR</span>';
								print $rslt_dlt;
							} else {								
								$insert = "INSERT INTO sl_skus_cost (ID_products, ID_purchaseorders, ID_warehouses, Tblname, Quantity, Cost, Cost_Adj, Date, Time, ID_admin_users) 	
											VALUES 	($ID_products, 0, $ID_warehouses, 'sl_adjustments', $Quantity, $cost_csv, 0, CURDATE(), CURTIME(), 1)";
								eval{
									&Do_SQL($insert);
									if( $@ ){
										&Do_SQL("ROLLBACK;");
										$rslt_ins = '<span style="color: red;">ERROR</span>';
										print $rslt_ins;
									} else {
										if( $in{'process'} eq "commit" ){
											&Do_SQL("COMMIT;");
										} else {
											&Do_SQL("ROLLBACK;");
										}
										$rslt_ins = '<span style="color: green;">OK</span>';
									}
								};
							}							
						}
						print qq|
							<tr>
								<td>$sku_id_warehouses</td>
								<td>$Quantity</td>
								<td>$sku_quantity</td>
								<td style="background-color:$color;color:white;text-align:right;">$dif</td>
								<td style="background-color:$colorCost;color:white;text-align:right;">$sku_cost</td>
								<td style="text-align:right;">$cost_csv</td>
								<td style="text-align: center;">$rslt_dlt</td>
								<td style="text-align: center;">$rslt_ins</td>
							</tr>							
							|;
					}
				}
			}
			print '</table><br>';
		}
	}else{
		print "No existe el archivo";
	}

}


#################################################################
#################################################################
#	Function: fix_inventory_cost
#
#   		Corrige las tablas sl_skus_cost y sl_warehouses_locations
#
#	Created by: ISC Alejandro Diaz
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