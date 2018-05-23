#!/usr/bin/perl
#######################################################################
#######################################################################
#######################################################################

use DBI;
use DBIx::Connector;
use DBD::mysql;
use Cwd;
use File::Copy;
use File::Slurp;
use MIME::Base64;
use Encode;
use Date::Calc qw();


local ($dir) = getcwd;
local ($in{'e'}) = 3;
local ($in{'this_ida_debit'}) = 1554;
local ($in{'this_ida_credit'}) = 1074;
local ($in{'this_date'}) = '2015-12-31';

chdir($dir);

# Required Libraries
# --------------------------------------------------------
eval {
	require ('../subs/auth.cgi');
	require ('../subs/sub.base.html.cgi');
	require ('../subs/sub.func.html.cgi');
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
#	Created by: _RB_
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
	&execute_fix_customers_balance;
	&disconnect_db;
}


#################################################################
#################################################################
#	Function: execute_fix_customers_balance
#
#
#	Created by: _RB_
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
sub execute_fix_customers_balance{
#################################################################
#################################################################	

	my $inbound_file_path = $cfg{'path_upfiles'} . 'e' . $in{'e'} . '/';
	my $executed_file_path = $inbound_file_path;
	print "Leyendo archivo en ruta: " . $inbound_file_path . "\n";

	opendir (CMDIR, $inbound_file_path) || &cgierr('Unable to open directory ' . $inbound_file_path ,704,$!);
	@files = readdir(CMDIR);# Read in list of files in directory..
	closedir (CMDIR);

	my @cols = ('id_orders','amount','type');


	##### Looping files A2BF_Shipments_20150515120126.txt
	FILE: foreach my $file_name (sort @files) {

		next if ($file_name =~ /^\./);		# Skip "." and ".." entries..
		next if ($file_name =~ /^index/);		# Skip index.htm type files..

		print "Archivo encontrado: " . $file_name  . "\n";
		next if ($file_name !~ /^depuracionclientes_\d{8}.csv$/);# Skip
		print "Intentando abrir el archivo " . $file_name  . "\n";

		##### Open File
		my $i=0;
		my @orders_res;

		if (-e  $inbound_file_path . $file_name) {

			open(my $this_file, "<", $inbound_file_path . $file_name) or &cgierr('Unable to open file: '. $inbound_file_path . $file_name, 601,$!);

			print "Ejecutando ordenes en el archivo...\n\n";

			LINE: while (<$this_file>) {

				$line = $_;
				$line =~ s/\r|\n|//g;
				#print "$i - $line\n\n";

				my %this_data; my $this_res; my $flag_amount = 0;
				my @line_data = split(/,/, $line);
				#print "Linea tiene " . scalar @line_data . " Elementos\n";
				
				for (0..$#line_data) {

					$line_data[$_] =~ s/\r|\n|\t|\"//g;
					$line_data[$_] =~ s/^\s+//;
					$line_data[$_] =~ s/\s+$//;

					$this_data{$cols[$_]} = $line_data[$_];

				}
				$this_data{'id_orders'} = int($this_data{'id_orders'});


				##### Processing Data
				if($this_data{'id_orders'} > 0){

					## Inicializa la transaccion
					++$i;
					$va{'this_accounting_time'} = time();
					&Do_SQL("START TRANSACTION;");

					if($this_data{'type'}  == 1){

						## 1) Only Mark as Void
						$this_res = 'To Void';
						&Do_SQL("UPDATE sl_orders SET Status = 'Void' WHERE ID_orders = '". $this_data{'id_orders'} ."';");

					}elsif($this_data{'type'} > 1){

						## 2) Capture Payment
						my ($sth_p) = &Do_SQL("SELECT ID_orders_payments FROM sl_orders_payments WHERE ID_orders = '". $this_data{'id_orders'} ."' AND ROUND(Amount, 2) > 0.1 AND Status IN('Approved','Financed','Denied','Pending','Insufficient Funds') ORDER BY Paymentdate, ID_orders_payments ;");
						my ($this_id) = $sth_p->fetchrow();

						if($this_id){

							my (%overwrite) = ('amount' => $this_data{'amount'}, 'pmtfield8' => '1' ,'authcode' => 'BAL-' . $i, 'authdatetime' => 'NOW()', 'captured' => 'Yes', 'paymentdate' => $in{'this_date'}, 'capdate' => $in{'this_date'}, 'status' => 'Approved', 'reason' => 'Sale');
							$new_applied_payment = &Do_selectinsert('sl_orders_payments', "ID_orders_payments = '". $this_id ."'", "", "", %overwrite);
							$this_res .= qq|New Payment: $new_applied_payment|;

						}else{
							
							## Cancelled Payment already Captured?
							my ($sth) = &Do_SQL("SELECT ID_orders_payments FROM sl_orders_payments WHERE ID_orders = '". $this_data{'id_orders'} ."' AND Captured = 'Yes' AND CapDate > '2013-01-01' AND Status = 'Cancelled' AND ABS(Amount - ". $this_data{'amount'} .") < 1 LIMIT 1;");
							my ($this_id) = $sth->fetchrow();

							if($this_id){

								&Do_SQL("UPDATE sl_orders_payments SET Status = 'Approved' WHERE ID_orders_payments = '". $this_id ."';");
								$this_res .= qq|Payment Approved|;

							}else{

								## No se encontro pago, si se quiere dar de alta uno por defecto, aplicar el INSERT, de otra forma, mandar el error con el fla_amount
								#$flag_amount = 1;
								#$this_res .= qq|No Payment|;

								&Do_SQL("INSERT INTO `sl_orders_payments` (`ID_orders_payments`, `ID_orders`, `Type`, `PmtField1`, `PmtField2`, `PmtField3`, `PmtField4`, `PmtField5`, `PmtField6`, `PmtField7`, `PmtField8`, `PmtField9`, `PmtField10`, `PmtField11`, `Amount`, `Reason`, `Paymentdate`, `AuthCode`, `AuthDateTime`, `Captured`, `CapDate`, `PostedDate`, `Status`, `Date`, `Time`, `ID_admin_users`) VALUES (0, ". $this_data{'id_orders'} .", 'Deposit', '', '', '', '', '', '', '', '', '', '', '', ". $this_data{'amount'} .", 'Sale', '". $in{'this_date'} ."', 'CBALANCE-CREATED', '', 'Yes', '". $in{'this_date'} ."', '". $in{'this_date'} ."', 'Approved', CURDATE(), CURTIME(), 1);");
								$this_res .= qq|Payment Created|;

							}

						}
					

						if($this_data{'type'}  == 3 and !$flag_amount){
						
							## 3) Accounting Debit
							&Do_SQL("INSERT INTO sl_movements (ID_accounts, Amount, Reference, EffDate, tableused, ID_tableused, Category, Credebit, MD5Verification, ID_journalentries, Status, Date, Time, ID_admin_users )
									VALUES (". $in{'this_ida_debit'} .", ". $this_data{'amount'} .", 'CBALANCE', '". $in{'this_date'} ."', 'sl_orders', '". $this_data{'id_orders'} ."', 'Cobranza', 'Debit', MD5('". $va{'this_accounting_time'} ."'), -1, 'Active',CURDATE(), CURTIME(), '1');");

							## 3) Accounting Credit
							&Do_SQL("INSERT INTO sl_movements (ID_accounts, Amount, Reference, EffDate, tableused, ID_tableused, Category, Credebit, MD5Verification, ID_journalentries, Status, Date, Time, ID_admin_users )
									VALUES (". $in{'this_ida_credit'} .", ". $this_data{'amount'} .", 'CBALANCE', '". $in{'this_date'} ."', 'sl_orders', '". $this_data{'id_orders'} ."', 'Cobranza', 'Credit',MD5('". $va{'this_accounting_time'} ."'), -1, 'Active',CURDATE(), CURTIME(), '1');");
							
							$this_res .= qq| - Accounting Created|;

						}

					}

					## Order Payments Cancell
					&Do_SQL("UPDATE sl_orders_payments SET Status = 'Cancelled', Paymentdate = CURDATE() WHERE ID_orders = '". $this_data{'id_orders'} ."' AND (Captured IS NULL OR Captured = 'No' OR Captured = '') AND (CapDate IS NULL OR CapDate = '0000-00-00') AND Status IN('Approved','Financed','Denied','Pending','Insufficient Funds');");
					## Order Note
					#&Do_SQL("INSERT INTO sl_orders_notes SET ID_orders = '". $this_data{'id_orders'} ."', Notes = 'Customer Balance\n". $this_res ."', Type = 'Low', Date = CURDATE(), Time = CURTIME(), ID_admin_users = '1';");
					
					push(@orders_res, "$this_data{'id_orders'},$this_data{'amount'},$this_data{'type'},$this_res" );

					## COMMIT / ROLLBACK
					if(!$flag_amount and $this_res){ &Do_SQL("COMMIT;"); }else{ &Do_SQL("ROLLBACK;"); }

					## Printing Res in console
					print $i . ' - ' . qq|$this_data{'id_orders'} , $this_data{'amount'}, $this_data{'type'}, $this_res\n|;


					if($i % 500 == 0){

						print "Sleeping 1 second...";
						sleep(1);

					}
					#print $i . ' - ' . qq|$this_data{'id_orders'} , $this_data{'amount'}, $this_data{'type'}\n|;

				}else{

					print "No encontre datos para " . join(', ', @line_data) . "\n";
					push(@orders_data_error, join(', ', @line_data) . "\n" );

				}
				
			}
			
		}

        ### Moving the file to Backup
		#print "Moving $inbound_file_path$file_name to $executed_file_path$file_name\n\n";
		#move($inbound_file_path . $file_name, $executed_file_path . $file_name);
		#print "Sleeping 5 seconds\n\n";
		#sleep(2);

		### Reading File for Manddrill attachment
		# my $text_file = read_file($executed_file_path . $file_name);
		# my $file_encoded = encode_base64($text_file);
		# my $file_ext = 'csv';

		print "Enviando correo\n\n";
		if(scalar @orders_res) {

			## Email Config
			my $from_mail = 'info@inovaus.com';
			my $to_mail_fin = "ltorres\@inovaus.com";
			my $to_mail_dev1 = "rbarcenas\@inovaus.com";
			
			my $subject_mail = 'Depuracion Clientes - ' . $cfg{'company_name'};
			my $body_mail = join("<br>", @orders_res) . "\n" ;

	    	#From,To,CC,BCC,Subject,Body,Attachment
	    	#&send_mandrillapp_email($from_mail,$to_mail_atc2,$subject_mail,$body_mail,$text_mail,$file_encoded,$file_name, $file_ext);
	    	#&send_mandrillapp_email($from_mail,$to_mail_atc3,$subject_mail,$body_mail,$text_mail,$file_encoded,$file_name, $file_ext);
	    	&send_mandrillapp_email($from_mail,$to_mail_fin,$subject_mail,$body_mail,$body_mail,'','','');
	    	&send_mandrillapp_email($from_mail,$to_mail_dev1,$subject_mail,$body_mail,$body_mail,'','','');

	    	print "Sending File $file_name to $to_mail_dev1...";
	    }

        print "\n\n\n\nDone...\n\n\n\n";
        #last FILE;
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