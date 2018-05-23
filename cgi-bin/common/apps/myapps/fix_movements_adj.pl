#!/usr/bin/perl
#######################################################################
#######################################################################
#######################################################################

use DBI;
use DBIx::Connector;
use DBD::mysql;
use Cwd;
use File::Copy;
use Encode;

# Default la 11 porque este proceso fue diseñado para Importaciones
local(%in) = &parse_form;

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
#	Created by: Ing. Gilberto Quirino
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
	&execute_fix_movements_adj;
	&disconnect_db;
}


#################################################################
#################################################################
#	Function: execute_fix_movements_adj
#
#
#	Created by: Gilberto Quirino
#
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
sub execute_fix_movements_adj{
	my $process = ($in{'process'} ne 'commit')? qq|<span style="color: gray; padding:5px;">TESTING</span>|:qq|<span style="color: red; font-weight: bold; padding:5px;">EXECUTING</span>|;
	my $log_email;

	&load_settings;
	print "Content-type: text/html\n\n";
	print qq|<meta http-equiv="content-type" content="text/html; charset=utf-8" />\n\n|;
	print '<h4 style="border-bottom: 3px double gray;">DIREKSYS '.$cfg{'app_title'}.' e('.$in{'e'}.') :: Fix de movimientos contables de los gastos de aterrizaje <span style="position: relative; float: right;">Process: '.$process.'</span></h4>';
	
	
	if (!$in{'e'}){
		print qq|<span style="color:red;">ID de empresa es requerido</span>|;
		return;
	}
	
	## Id del primer PO que si cuenta con su contabilidad correcta(e11)...	
	my $id_po_ok_ini = 0;#( $in{'e'} == 11 ) ? 2047 : 0;

	my $finish_trans = '';
	my $msj_ok = '';
	my $msj_error = '';

	if( $in{'process'} eq 'commit' ){
		$finish_trans = 'COMMIT'; 
		$msj_ok = '<span style="color: #209001;">Este registro fu&eacute; procesado correctamente</span>';
		$msj_error = '<span style="color: #ff0000;">Este registro NO pudo ser procesado</span>';
	} else {
		$finish_trans = 'ROLLBACK'; 
		$msj_ok = '<span style="color: #209001;">Este registro puede ser procesado</span>';
		$msj_error = '<span style="color: #ff0000;">Este registro NO puede ser procesado</span>';
	}

	print '<table>';
	print '<tr>';
	print '		<th>ID_Mov</th>';
	print '		<th>ID_PO</th>';
	print '		<th>ID_Vendor_PO</th>';
	print '		<th>Amount PO</th>';
	print '		<th>Adjustmens</th>';
	print '</tr>';

	my ($sthMain) = &Do_SQL("SELECT ID_tableused  
							FROM sl_movements 
							WHERE Reference LIKE 'Vendor%' 
								AND Status='Active'
							GROUP BY ID_tableused;");
	my $i = 0;
	&Do_SQL("BEGIN;");	
	while ( $refMain = $sthMain->fetchrow_hashref() ) {
		++$i;
		my $id_po = $refMain->{'ID_tableused'};		
		
		if( $id_po >= $id_po_ok_ini ){
			##--- Se obtiene el ID_vendor del PO
			$sthNotes = &Do_SQL("SELECT ID_movements, MAX(Amount), Reference, SUBSTR(Reference, 8) ID_vendor_po
								FROM sl_movements
								WHERE ID_tableused='$id_po' 
									AND tableused='sl_purchaseorders'
									AND Reference LIKE 'Vendor%';");
			my($id_movements, $amount_po, $reference_po, $id_vendor_po) = $sthNotes->fetchrow_array();

			## Revisa si el PO tiene gastos de aterrizaje
			my $sthCountAdj = &Do_SQL("SELECT COUNT(*) total_adjs FROM sl_purchaseorders_adj WHERE ID_purchaseorders='$id_po';");
			my $count_adj = $sthCountAdj->fetchrow_array();

			if( $id_vendor_po ){
				$id_vendor_po = int($id_vendor_po);

				print '<tr>';		
				print '<td>'.$id_movements.'</td>';
				print '<td>'.$id_po.'</td>';
				print '<td>'.$id_vendor_po.'</td>';
				print '<td>'.$amount_po.'</td>';
				print '<td>'.$count_adj.'</td>';
				print '</tr>';

				print '<tr><td colspan="3">';
				print '<table border="1">';
				$sthAdj = &Do_SQL("SELECT * FROM sl_movements WHERE ID_tableused='$id_po' AND tableused='sl_purchaseorders' AND Reference LIKE 'Vendor%';");
				while ($refAdj = $sthAdj->fetchrow_hashref()){
					if( $refAdj->{'Reference'} !~ /Vendor: $id_vendor_po/ ){
						print '<tr>';
						print '<td>'.$refAdj->{'ID_movements'}.'</td>';
						print '<td>'.$refAdj->{'Reference'}.'</td>';
						print '<td>'.$refAdj->{'Amount'}.'</td>';
						print '<td>'.$refAdj->{'Category'}.'</td>';
						print '<td>'.$refAdj->{'Credebit'}.'</td>';
						print '<td>'.$refAdj->{'EffDate'}.'</td>';
						print '</tr>';
					}
				}
				print '</table>';
				print '</td></tr>';
			}
		}
	}
	&Do_SQL($finish_trans);

	print '</table>';

	#print '<br /><br /><hr /><hr />';
	#print '<span style="font-weight: bold;">Registros Correctos para procesar:</span> <span style="color: #209001;">'.$rows_ok.'</span><br />';
	#print '<span style="font-weight: bold;">Registros Con errores:</span> <span style="color: #ff0000;">'.$rows_no_ok.'</span><br />';
	#print '<span style="font-weight: bold;">Total de Registros:</span> <span style="color: #0000ff;">'.$i.'</span>';
	#print '<hr />';
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