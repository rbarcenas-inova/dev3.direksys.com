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
	print '<h4 style="border-bottom: 3px double gray;">DIREKSYS '.$cfg{'app_title'}.' e('.$in{'e'}.') :: Fix del Left Quantity Total <span style="position: relative; float: right;">Process: '.$process.'</span></h4>';
	
	
	if (!$in{'e'}){
		print qq|<span style="color:red;">ID de empresa es requerido</span>|;
		return;
	}

	# Max rows process
	my $max_rows_process = 'LIMIT '.$in{'limit'} if( $in{'limit'} and int($in{'limit'}) > 0 ); #? $in{'rows'} : 5000;
	# To Date
	my $sql_filter = " AND op.Date <= '".$in{'todate'}."'" if( $in{'todate'} and $in{'todate'} ne '' );
	# Start ID
	my $sql_start = " AND op.ID_orders_payments >= ".$in{'start'} if( $in{'start'} and int($in{'start'}) > 0 );

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
	
	my ($sthMain) = &Do_SQL("SELECT 
								op.ID_orders
								, op.ID_orders_payments
								, op.PmtField3
								, op.PmtField4
								, op.PmtField5
								, op.Date 
							FROM sl_orders_payments op 
							WHERE 1 
								/*AND op.ID_orders_payments >= $fisrt_id_op*/
								AND op.`Type` = 'Credit-Card' 
								AND op.PmtField3 != '' 
								AND op.PmtField3 IS NOT NULL
								/*AND op.PmtField1 = 'American Express'*/
								/*AND op.PmtField3 NOT LIKE '%xx%'*/
								/*AND op.ID_orders_payments Not In(Select ID_orders_payments From sl_orders_cardsdata)*/
								$sql_filter
								$sql_start
							ORDER BY op.ID_orders_payments 
							$max_rows_process;");

	print '<table style="border-collapse: collapse; border-spacing: none; width: 90%;">';
	print '<tr style="background-color: #cccccc;">';
	print '		<th>N.P.</th>';
	print '		<th>ID_orders</th>';
	print '		<th>ID_orders_payments</th>';
	print '		<th>Credit-Card</th>';
	print '		<th>CVN</th>';
	print '		<th>Date</th>';
	print '		<th>PayLogs Found</th>';
	print '		<th>PayLogs Process</th>';
	print '</tr>';

	my $i = 0;
	my $log = '';
	&Do_SQL("BEGIN;");
	while ( $refMain = $sthMain->fetchrow_hashref() ) {
		++$i;
		my $id_order	= $refMain->{'ID_orders'};
		my $id_payment	= $refMain->{'ID_orders_payments'};
		my $card_num	= $refMain->{'PmtField3'};
		my $card_date	= $refMain->{'PmtField4'};
		my $cvn			= $refMain->{'PmtField5'};
				

		##------------------------------------------------
		## Se procesa la info. de plogs
		##------------------------------------------------
		my $total_process_plogs = 0;		
		my $list_card_num_plogs = '';
		$qPlogs = "SELECT ID_orders_plogs, Data 
					FROM sl_orders_plogs 
					WHERE ID_orders = ".$id_order." 
						AND ID_orders_payments = ".$id_payment.";";
		my $sthPlogs = &Do_SQL($qPlogs);
		my $num_plogs = $sthPlogs->rows();
		while ($fPlogs = $sthPlogs->fetchrow_hashref()) {
			my $data_plogs = $fPlogs->{'Data'};
			if( $data_plogs =~ /Number=\d{12,18}/ ){
				## Se extrae el num. de tarjeta
				my $idx_cc_ini = index($data_plogs, 'Number=');
				my $idx_cc_fin = index($data_plogs, 'Expires=', $idx_cc_ini+7);				
				my $cc_plogs = substr($data_plogs, $idx_cc_ini+7, (($idx_cc_fin-8) - $idx_cc_ini));				
				## Se enmascara el num. de tarjeta
				my $cc_plogs_mask = substr($cc_plogs, 0, 6).'xxxxxx'.substr($cc_plogs, -4);

				## Se extra el cvn
				my $idx_cvn_ini = index($data_plogs, 'Cvv2Val=');
				#my $idx_cvn_fin = index($data_plogs, 'Total=', $idx_cvn_ini+8);
				my $cvn_plogs = substr($data_plogs, $idx_cvn_ini+8, 3);
				## Se enmascara el cvn
				my $cvn_plogs_mask = 'xxx';

				$list_card_num_plogs .= '<br />'.$cc_plogs.'['.$cvn_plogs.']';
				$list_card_num_plogs .= ' -> '.$cc_plogs_mask.'['.$cvn_plogs_mask.']';

				## Se sustituyen los valores enmascarados
				$data_plogs =~ s/Number=\d{12,18}/Number=$cc_plogs_mask/g;
				$data_plogs =~ s/Expires=\d{2}\/\d{2}/Expires=xx\/xx/g;
				$data_plogs =~ s/Cvv2Val=\d{3}/Cvv2Val=xxx/g;
				## Se actualiza el campo en la tabla plogs
				&Do_SQL("UPDATE sl_orders_plogs SET Data='".$data_plogs."' WHERE ID_orders_plogs=".$fPlogs->{'ID_orders_plogs'});

				$total_process_plogs++;
			}elsif( $data_plogs =~ /number: \d{12,15}/ ){
				## Se extrae el num. de tarjeta
				my $idx_cc_ini = index($data_plogs, 'number: ');
				my $idx_cc_fin = index($data_plogs, 'month:', $idx_cc_ini+8);				
				my $cc_plogs = substr($data_plogs, $idx_cc_ini+8, (($idx_cc_fin-9) - $idx_cc_ini));				
				## Se enmascara el num. de tarjeta
				my $cc_plogs_mask = substr($cc_plogs, 0, 6).'xxxxx'.substr($cc_plogs, -4);

				## Se extra el cvn
				my $idx_cvn_ini = index($data_plogs, 'securityCode: ');
				#my $idx_cvn_fin = index($data_plogs, 'Total=', $idx_cvn_ini+8);
				my $cvn_plogs = substr($data_plogs, $idx_cvn_ini+8, 3);
				## Se enmascara el cvn
				my $cvn_plogs_mask = 'xxxx';

				$list_card_num_plogs .= '<br />'.$cc_plogs.'['.$cvn_plogs.']';
				$list_card_num_plogs .= ' -> '.$cc_plogs_mask.'['.$cvn_plogs_mask.']';

				## Se sustituyen los valores enmascarados
				$data_plogs =~ s/number: \d{12,18}/number: $cc_plogs_mask/g;
				$data_plogs =~ s/month: \d{3}/month: xx/g;
				$data_plogs =~ s/year: \d{3}/year: xx/g;
				$data_plogs =~ s/securityCode: \d{4}/securityCode: xxxx/g;
				## Se actualiza el campo en la tabla plogs
				&Do_SQL("UPDATE sl_orders_plogs SET Data='".&filter_values($data_plogs)."' WHERE ID_orders_plogs=".$fPlogs->{'ID_orders_plogs'});

				$total_process_plogs++;
			}
		}
		##------------------------------------------------

		##------------------------------------------------
		## Se actualiza el valor en la tabla orders_payments		
		##------------------------------------------------
		# my $cc_mask = substr($card_num,0,6)."xxxxxx".substr($card_num,-4);
		# my $cvn_mask = (length($cvn) == 4) ? 'xxxx' : 'xxx';
		# my $sql = "UPDATE sl_orders_payments SET PmtField3='".$cc_mask."', PmtField4='xxxx', PmtField5='".$cvn_mask."' WHERE ID_orders_payments=".$id_payment.";";
		# $log .= $sql."\n";
		# &Do_SQL($sql);
		# $log .= "UPDATE sl_orders_payments SET PmtField3='".$card_num."', PmtField4='".$card_date."', PmtField5='".$cvn."' WHERE ID_orders_payments=".$id_payment.";\n";
		##------------------------------------------------
		
		##------------------------------------------------
		## Se guardan los datos encriptados en la tabla
		## correspondiente
		##------------------------------------------------
		## Encrypt card_num
		# my $card_num_crypt = '';
		# my $date_crypt = '';
		# my $cvn_crypt = '';
		# if( $card_num ){			
		# 	## Encrypt CC
		# 	$card_num_crypt = &LeoEncrypt($card_num);
		# 	## Encrypt Date CC
		# 	$date_crypt = &LeoEncrypt($card_date) if($card_date);
		# 	## Encrypt CVN		
		# 	$cvn_crypt = &LeoEncrypt($cvn) if($cvn);	

		# 	# Valida que aún no exista el registro correspondiente al pago actual...
		# 	my $sthVal = &Do_SQL("SELECT ID_orders_payments FROM sl_orders_cardsdata WHERE ID_orders_payments=$id_payment;");
		# 	my $fval = $sthVal->fetchrow();
		# 	if( !$fval ){
		# 		&Do_SQL("INSERT INTO sl_orders_cardsdata(ID_orders, ID_orders_payments, card_number, card_date, card_cvn, Date, Time, ID_admin_users)
		# 				 VALUES($id_order, $id_payment, '$card_num_crypt', '$date_crypt', '$cvn_crypt', CURDATE(), CURTIME(), 1);");
		# 	}
		# }
		##------------------------------------------------
		print '<tr style="">';
		print '		<td style="border-bottom: 1px dotted gray; text-align: right;">'.$i.'</td>';
		print '		<td style="border-bottom: 1px dotted gray; text-align: right;">'.$id_order.'</td>';
		print '		<td style="border-bottom: 1px dotted gray; text-align: right;">'.$id_payment.'</td>';
		print '		<td style="border-bottom: 1px dotted gray; text-align: center;">'.$card_num.'<br /><span style="color: gray; display: block; float: right; position: relative;">'.$card_num_crypt.'</span>'.'</td>';
		print '		<td style="border-bottom: 1px dotted gray; text-align: right;">'.$cvn.'<span style="color: gray; display: block;">'.$cvn_crypt.'</span>'.'</td>';
		print '		<td style="border-bottom: 1px dotted gray; text-align: center;">'.$refMain->{'Date'}.'</td>';
		print '		<td style="border-bottom: 1px dotted gray; text-align: center;">'.$num_plogs.'</td>';
		print '		<td style="border-bottom: 1px dotted gray; text-align: center;">'.$list_card_num_plogs.'<br />Total rows: '.$num_plogs.', &nbsp;&nbsp; Total Processed:'.$total_process_plogs.'</td>';
		print '</tr>';
		print '<tr>';
		print '<td colspan="9">'.$sql.'</td>';
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
		my $file_name = 'fix_cc_payments_'.$date.'.txt';

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