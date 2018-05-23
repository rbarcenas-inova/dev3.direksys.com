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

local(%in) = &parse_form;

# Required Libraries
# --------------------------------------------------------
eval {
	require ('../subs/auth.cgi');
	require ('../subs/sub.base.html.cgi');
	require ('../subs/sub.func.html.cgi');
	require ('../subs/libs/lib.to_sort1.pl');
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
	&execute_get_cc_data;
	&disconnect_db;
}


#################################################################
#################################################################
#	Function: execute_get_cc_data
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
sub execute_get_cc_data{
	my $process = ($in{'process'} ne 'commit')? qq|<span style="color: gray; padding:5px;">TESTING</span>|:qq|<span style="color: red; font-weight: bold; padding:5px;">EXECUTING</span>|;
	#my $log_email;

	&load_settings;
	print "Content-type: text/html\n\n";
	print qq|<meta http-equiv="content-type" content="text/html; charset=utf-8" />\n\n|;
	print '<h4 style="border-bottom: 3px double gray;">DIREKSYS '.$cfg{'app_title'}.' e('.$in{'e'}.') :: Se obtienen los datos de la CC  <span style="position: relative; float: right;">Process: '.$process.'</span></h4>';
	
	
	if (!$in{'e'}){
		print qq|<span style="color:red;">ID de empresa es requerido</span>|;
		return;
	}

	my $inbound_file_path = $cfg{'path_upfiles'}. 'e'.$in{'e'} . '/';
	#my $executed_file_path = $inbound_file_path . 'done/';
	my @cols = ('id_orders','card','month','year');

	
	opendir (LUEDIR, $inbound_file_path) || &cgierr('Unable to open directory ' . $inbound_file_path ,704,$!);
	@files = readdir(LUEDIR);# Read in list of files in directory..
	closedir (LUEDIR);


	##### Looping files
	FILE: foreach my $file_name (sort @files) {

		next if ($file_name =~ /^\./);		# Skip "." and ".." entries..
		next if ($file_name =~ /^index/);	# Skip index.htm type files..
		next if ($file_name !~ /csv$/);		# Skip not cvs type files..
		next if ($file_name ne 'orders_cards.csv');

		print "<br />Intentando abrir el archivo " . $inbound_file_path . $file_name  . "\n";

		##### Opening File
		if (-e  $inbound_file_path . $file_name) {

			open(my $this_file, "<", $inbound_file_path . $file_name) or &cgierr('Unable to open file: '. $inbound_file_path . $file_name, 601,$!);

			my $ids_ok;
			my $ids_failed;
			my $str_to_file = '';

			print "<br />Ejecutando lineas en el archivo $file_name...\n\n";

			### Inicializa la transacción para los datos del archivo actual
			&Do_SQL("START TRANSACTION;");

			print '<table style="min-width: 800px;" border="1">';
			print '<tr>';
			print '<th>ID Order</th>';
			print '<th>ID Order Payment</th>';			
			print '<th>Card</th>';
			print '<th>Exp. Date</th>';
			print '<th>CVN</th>';
			print '</tr>';
			LINE: while (<$this_file>) {
				$line = $_;
				$line =~ s/\r|\n| |//g;
				#print "$i - $line\n\n";

				my %this_data;				
				my @line_data = split(/,/, $line);
				for (0..$#line_data) {

					$line_data[$_] =~ s/\r|\n//g;
					$line_data[$_] =~ s/^\s+//;
					$line_data[$_] =~ s/\s+$//;
					$line_data[$_] =~ s/"//g;
					$line_data[$_] =~ s/\-//g;
					$line_data[$_] =~ s/\ //g;

					$this_data{$cols[$_]} = $line_data[$_];
				}				

				print '<tr>';
				print '<td>'.$this_data{'id_orders'}.'</td>';				

				##### Processing Data
				if($this_data{'id_orders'} ne ''){

					###-----------------------------------------------
					### Se obtienen los datos encriptados
					###-----------------------------------------------
					my $sql = "SELECT sl_orders_cardsdata.ID_orders_payments, sl_orders_cardsdata.card_number, sl_orders_cardsdata.card_date, sl_orders_cardsdata.card_cvn 
								FROM sl_orders_cardsdata 
									INNER JOIN sl_orders_payments USING(ID_orders_payments)
								WHERE sl_orders_cardsdata.ID_orders=".$this_data{'id_orders'}." 
									AND sl_orders_payments.Status NOT IN('Financed','Denied','ChargeBack','Void','On Collection','Claim','Order Cancelled','Cancelled')
								ORDER BY sl_orders_cardsdata.ID_orders_payments DESC LIMIT 1;";
					my $sth = &Do_SQL($sql);
					my ($id_order_payments, $card_number, $card_date, $card_cvn) = $sth->fetchrow_array();

					if( !$id_order_payments ){
						print '<td style="color: red;" colspan="3">No existen registros en cardsdata...</td>';
						++$ids_failed;
					}else{
						$card_number = &LeoDecrypt($card_number);
						$card_date = &LeoDecrypt($card_date);
						$card_cvn = &LeoDecrypt($card_cvn);
						$month = substr($card_date, 0, 2);
						$year = '20'.substr($card_date, -2);

						if( $card_number ne $this_data{'card'} and $this_data{'card'} ne '' ){
							$month = '';
							$year = '';
							$card_cvn = '';
							$card_number = $this_data{'card'} if( $this_data{'card'} ne '' );
						}

						print '<td>'.$id_order_payments.'</td>';
						print '<td>'.$card_number.'</td>';
						print '<td>'.$month.' / '.$year.'</td>';
						print '<td>'.$card_cvn.'</td>';

						$str_to_file .= $this_data{'id_orders'}.','.$card_number.','.$month.','.$year.','.$card_cvn."\n";

						++$ids_ok;
					}
					###-----------------------------------------------

				}else{

					++$ids_failed;
					print '<td style="color: red;" colspan="3">No encontre datos para ' . join(', ', @line_data) . '</td>';
					push(@orders_data_error, join(', ', @line_data) . "\n" );

				}
				
				print '</tr>';

			} ## End Line
			print '</table>';
			
			print "<br />Total OK: $ids_ok\nTotal Failed: $ids_failed\n\n";

			### Se genera el archivo con los datos obtenidos de la CC
			if( open(my ($file),">", $inbound_file_path."get_cc_data.csv") ){

				print $file $str_to_file;
				close($file);

			}else{

				&cgierr("Unable to open $fname");

			}
			
		} ## End File

    } ## Each File
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