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
use Date::Calc qw();

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
	&execute_fix_left_qty_total;
	&disconnect_db;
}


#################################################################
#################################################################
#	Function: execute_fix_left_qty_total
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
sub execute_fix_left_qty_total{
	my $process = ($in{'process'} ne 'commit')? qq|<span style="color: gray; padding:5px;">TESTING</span>|:qq|<span style="color: red; font-weight: bold; padding:5px;">EXECUTING</span>|;
	#my $log_email;

	&load_settings;
	print "Content-type: text/html\n\n";
	print qq|<meta http-equiv="content-type" content="text/html; charset=utf-8" />\n\n|;
	print '<h4 style="border-bottom: 3px double gray;">DIREKSYS '.$cfg{'app_title'}.' e('.$in{'e'}.') :: Fix Payments - PmtField11 <span style="position: relative; float: right;">Process: '.$process.'</span></h4>';
	
	
	if (!$in{'e'}){
		print qq|<span style="color:red;">ID de empresa es requerido</span>|;
		return;
	}

	my $logs = '';
	my $finish_trans = '';
	my $msj_ok = '';
	my $msj_error = '';
	my $total_process = 0;

	if( $in{'process'} eq 'commit' ){
		$finish_trans = 'COMMIT;'; 
		$msj_ok = '<span style="color: #209001;">Este registro fu&eacute; procesado correctamente</span>';
		$msj_error = '<span style="color: #ff0000;">Este registro NO pudo ser procesado</span>';
	} else {
		$finish_trans = 'ROLLBACK;'; 
		$msj_ok = '<span style="color: #209001;">Este registro puede ser procesado</span>';
		$msj_error = '<span style="color: #ff0000;">Este registro NO puede ser procesado</span>';
	}
	
	my ($sthMain) = &Do_SQL("SELECT ID_orders, ID_orders_payments, PmtField11
							FROM sl_orders_payments
							WHERE DATE >= '2015-12-01' AND (LENGTH(PmtField11)<=10 AND PmtField11 != '');");

	print '<table style="border-collapse: collapse; border-spacing: none; width: 100%;">';
	print '<tr style="background-color: #cccccc;">';
	print '		<th>N.P.</th>';
	print '		<th>ID_orders</th>';
	print '		<th>ID_orders_payments</th>';
	print '		<th>PmtField11</th>';
	print '		<th>ID_Plogs</th>';	
	print '		<th>Reference OK</th>';
	print '		<th>SQL</th>';
	print '</tr>';

	my $i = 0;
	my $log = '';
	my $total_process_plogs = 0;
	&Do_SQL("BEGIN;");
	while ( $refMain = $sthMain->fetchrow_hashref() ) {
		++$i;
		my $id_order	= $refMain->{'ID_orders'};
		my $id_payment	= $refMain->{'ID_orders_payments'};
		my $pmtfield11	= $refMain->{'PmtField11'};
		
		$log .= "ID_orders : ".$id_order."\n";
		$log .= "ID_orders_payments : ".$id_payment."\n";
		$log .= "PmtField11 : ".$pmtfield11."\n";

		##------------------------------------------------
		## Se procesa la info. de plogs
		##------------------------------------------------
		my $ids_plogs = '';
		my $sql_upd = '';
		my $ref_plogs = '';
		$qPlogs = "SELECT ID_orders_plogs, Data 
					FROM sl_orders_plogs 
					WHERE ID_orders = ".$id_order." 
						AND ID_orders_payments = ".$id_payment."
						AND Resp_msg = 'Aprobado'
						AND Resp_code = 'A';";
		my $sthPlogs = &Do_SQL($qPlogs);
		my $num_plogs = $sthPlogs->rows();
		while ($fPlogs = $sthPlogs->fetchrow_hashref()) {
			$ids_plogs .= $fPlogs->{'ID_orders_plogs'}.'<br>';
			$data_plogs = $fPlogs->{'Data'};
			if( $data_plogs =~ /REFERENCIA=\d/ ){
				## Se extrae el num. de tarjeta
				my $idx_cc_ini = index($data_plogs, 'REFERENCIA=');
				$ref_plogs = substr($data_plogs, $idx_cc_ini+11, 12);

				if( $ref_plogs ne '' ){
					$sql_upd = "UPDATE sl_orders_payments SET PmtField11 = '".&filter_values($ref_plogs)."' WHERE ID_orders_payments = ".$id_payment.";";
					$log .= $sql_upd."\n";
					&Do_SQL($sql_upd);
					$total_process++;
				}

			}
		}
		##------------------------------------------------

		$log .= "----------------------------------------------------------------------\n";
		
		print '<tr style="">';
		print '		<td style="border-bottom: 1px dotted gray; text-align: right;">'.$i.'</td>';
		print '		<td style="border-bottom: 1px dotted gray; text-align: right;">'.$id_order.'</td>';
		print '		<td style="border-bottom: 1px dotted gray; text-align: right;">'.$id_payment.'</td>';
		print '		<td style="border-bottom: 1px dotted gray; text-align: center;">'.$pmtfield11.'</td>';
		print '		<td style="border-bottom: 1px dotted gray; text-align: right;">'.$ids_plogs.'</td>';
		print '		<td style="border-bottom: 1px dotted gray; text-align: center;">'.$ref_plogs.'</td>';
		print '		<td style="border-bottom: 1px dotted gray; text-align: center;">'.$sql_upd.'</td>';
		print '</tr>';		
	}
	&Do_SQL($finish_trans);
	if( $in{'process'} eq 'commit' ){
		# Date
		my ($y, $m, $d) = Date::Calc::Today();
		my ($h, $n, $s) = Date::Calc::Now();
		my $date = sprintf('%02d%02d%02d%02d%02d', $y, $m, $d, $h, $n);
		# File
		my $file_path = '../../../files/e'.$in{'e'}.'/';
		my $file_name = 'fix_payments_field11_'.$date.'.txt';

		open(logs_fix,"> ".$file_path . $file_name) || die "No se puede abrir el archivo\n";
		print logs_fix $log;
		close(logs_fix);
	}

	print '</table>';

	print '<br /><br /><hr /><hr />';
	print '<span style="font-weight: bold;">SKUs Procesados: </span> <span style="color: #209001;">'.$total_process.'</span><br />';
	#print '<span style="font-weight: bold;">Registros Con errores:</span> <span style="color: #ff0000;">'.$rows_no_ok.'</span><br />';
	#print '<span style="font-weight: bold;">Total de Registros:</span> <span style="color: #0000ff;">'.$i.'</span>';
	print '<hr />';
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