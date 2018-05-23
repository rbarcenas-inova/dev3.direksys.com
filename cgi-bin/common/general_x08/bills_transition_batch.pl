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
use File::Copy;


local ($dir) = getcwd;
local ($in{'e'}) = 4;
local ($usr{'id_admin_users'}) = 1;
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
	&process_transition_file;
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
sub process_transition_file {
#############################################################################
#############################################################################
	
	#print "Content-type: text/html\n\n";

	my $inbound_file_path = $cfg{'path_upfiles'}. 'e'.$in{'e'} . '/transition_files/';
	my $executed_file_path = $inbound_file_path . 'done/';
	my @cols = ('id_vendors','type','currency','date','amount','memo','currency_exchange','tax');

	
	opendir (LUEDIR, $inbound_file_path) || &cgierr('Unable to open directory ' . $inbound_file_path ,704,$!);
	@files = readdir(LUEDIR);# Read in list of files in directory..
	closedir (LUEDIR);


	##### Looping files
	FILE: foreach my $file_name (sort @files) {

		next if ($file_name =~ /^\./);		# Skip "." and ".." entries..
		next if ($file_name =~ /^index/);		# Skip index.htm type files..
		next if ($file_name !~ /csv$/);		# Skip not cvs type files..

		print "Intentando abrir el archivo " . $inbound_file_path . $file_name  . "\n";

		##### Opening File
		if (-e  $inbound_file_path . $file_name) {

			open(my $this_file, "<", $inbound_file_path . $file_name) or &cgierr('Unable to open file: '. $inbound_file_path . $file_name, 601,$!);

			my $bills_ok;
			my $bills_failed;

			print "Ejecutando lineas en el archivo $file_name...\n\n";

			LINE: while (<$this_file>) {
				$line = $_;
				$line =~ s/\r|\n|//g;
				#print "$i - $line\n\n";

				my %this_data;
				my @line_data = split(/\t/, $line);
				for (0..$#line_data) {

					$line_data[$_] =~ s/\r|\n//g;
					$line_data[$_] =~ s/^\s+//;
					$line_data[$_] =~ s/\s+$//;
					$line_data[$_] =~ s/"//g;

					$this_data{$cols[$_]} = $line_data[$_];
				}

				$this_data{'id_vendors'} = int($this_data{'id_vendors'});
				$this_data{'amount'} =~ s/,//g; 
				$this_data{'id_banks'} = 2; ## Banorte
				$this_data{'ida_banks'} = 24; ## Banorte
				#$this_data{'deposit_id_accounts'} = 106; # 106 AG. ADNAL Cuenta contable del debito (, )
				#$this_data{'deposit_id_accounts'} = 104; # 105 PROV MER NAL
				#$this_data{'deposit_id_accounts'} = 105; # 105 PROV SER NAL
				#$this_data{'deposit_id_accounts'} = 109; # 109 PROV SER EXT
				#$this_data{'deposit_id_accounts'} = 108; # 108 ANT PROV EXT 
				#$this_data{'deposit_id_accounts'} = 91; # 91 GXC 
				$this_data{'bill_id_accounts'} = 600; # Cuenta contable del debito
				$this_data{'bill_id_tax_accounts'} = 124; # Cuenta contable del debito


				#$this_data{'memo'} = &filter_values($this_data{'memo'});


				##### Processing Data
				if($this_data{'id_vendors'} > 0 and $this_data{'type'} and $this_data{'date'} and $this_data{'amount'}){

					$this_data{'id_bills'} = &generate_new_bill(%this_data);

					if($this_data{'id_bills'}) {


						if($this_data{'type'} eq 'Deposit') {
							

							###################################################################
							###################################################################
							###################################################################
							###################################################################
							#
							#						TYPE Deposit
							#
							###################################################################
							###################################################################
							###################################################################
							###################################################################

							$this_data{'id_banks_movs'} = &generate_new_banks_movements(%this_data);

							########################################################
							########################################################
							## Movimientos de contabilidad
							########################################################
							########################################################
							my $vendor_category = &load_name('sl_vendors','ID_vendors', $this_data{'id_vendors'},'Category');
							my @params = ($this_data{'id_vendors'},$this_data{'id_bills'},$this_data{'ida_banks'},$this_data{'date'},$this_data{'amount'},$this_data{'currency_exchange'});
							&accounting_keypoints('vendor_deposit_'. lc($vendor_category), \@params );
							&Do_SQL("UPDATE sl_movements SET EffDate = '$this_data{'date'}', Date = '$this_data{'date'}', Reference = 'Deposit: $this_data{'id_bills'}', ID_journalentries = -1 WHERE ID_tableused = '$this_data{'id_vendors'}' AND tableused = 'sl_vendors' AND (ID_journalentries = 0 OR ID_journalentries IS NULL) AND TIMESTAMPDIFF(SECOND,CONCAT(Date,' ',Time) , NOW()) BETWEEN 0 AND 5 AND ID_admin_users = '$usr{'id_admin_users'}';");
							

							####
							#### Bill Update
							####
							&Do_SQL("UPDATE sl_bills SET Status = 'Paid' WHERE ID_bills = '$this_data{'id_bills'}';");


							
							++$bills_ok;

						}elsif($this_data{'type'} eq 'Bill') {

							###################################################################
							###################################################################
							###################################################################
							###################################################################
							#
							#						TYPE Bill
							#
							###################################################################
							###################################################################
							###################################################################
							###################################################################

							$this_data{'id_bills_expenses'} = &generate_new_bills_expenses(%this_data);

							########################################################
							########################################################
							## Movimientos de contabilidad
							########################################################
							########################################################
							&bills_to_processed($this_data{'id_bills'},$this_data{'currency_exchange'});
							&Do_SQL("UPDATE sl_movements SET EffDate = '$this_data{'date'}', Date = '$this_data{'date'}', ID_journalentries = -1 WHERE ID_tableused = '$this_data{'id_bills'}' AND tableused = 'sl_bills' AND (ID_journalentries = 0 OR ID_journalentries IS NULL) AND TIMESTAMPDIFF(SECOND,CONCAT(Date,' ',Time) , NOW()) BETWEEN 0 AND 5 AND ID_admin_users = '$usr{'id_admin_users'}';");

							
							++$bills_ok;

						}

					}else{

						++$bills_failed;

					}

				}else{

					++$bills_failed;
					print "No encontre datos para " . join(', ', @line_data) . "\n";
					push(@orders_data_error, join(', ', @line_data) . "\n" );

				}
				
			} ## End Line

			print "Total Bills Generated: $bills_ok\nTotal Bills Failed: $bills_failed\n\n";
			
		} ## End File


        ### Moving the file to Backup
		print "Moving $inbound_file_path$file_name to $executed_file_path$file_name\n\n";
		move($inbound_file_path . $file_name, $executed_file_path . $file_name);
		print "Sleeping 3 seconds\n\n";
		sleep(3);
        print "\n\n\n\n";
        #last FILE;

    } ## Each File

}


#############################################################################
#############################################################################
#   Function: set_error_note
#
#       Es: Genera una nota de error de escaneo en la orden
#       En: 
#
#    Created on: 12/21/2012  11:20:10
#
#    Author: _Roberto Barcenas_
#
#    Modifications:
#
#   Parameters:
#
#       - id_orders : ID_orders
#		- shpdate/from_wh : shpdate in SH type / from_wh in RT type
#		- tracking: Tracking info passed to entershipment / cod_receipt functions
#		- type : SH for Shipp / RT for Return
#
#  Returns:
#
#   See Also:
#
#
#
sub set_error_note {
#############################################################################
#############################################################################

	my($id_orders, $d, $tracking, $type) = @_;
	my ($mod) = $type eq 'SH' ? "ShpDate: $d\n" : "Driver: ".&load_name('sl_warehouses','ID_warehouses',$d,'Name'). " ($d)\n"; 

	## Nota entershipment/cod_receipt error
	
	&add_order_notes_by_type_admin($in{'id_orders'},"$mod".&filter_values($tracking),$type);
}


#############################################################################
#############################################################################
#   Function: generate_new_bill
#
#       Es: Crea un nuevo registro en sl_bills con los datos recibidos
#       En: 
#
#    Created on: 06/25/2013 17:56:10
#
#    Author: _Roberto Barcenas_
#
#    Modifications:
#
#   Parameters:
#
#     - this_data : Hash data
#
#  Returns:
#
#   See Also:
#
#
#
sub generate_new_bill {
#############################################################################
#############################################################################

	my (%bill_data) = @_;
	#&cgierr("Recibi $bill_data{'id_vendors'} + $bill_data{'type'} + $bill_data{'currency'} + $bill_data{'date'} + $bill_data{'amount'} + $bill_data{'memo'} + $bill_data{'currency_exchange'}");

	my $mod_currency = $bill_data{'currency_exchange'} ? "currency_exchange = '$bill_data{'currency_exchange'}', " : '';
	$mod_currency .= $bill_data{'type'} eq 'Deposit' ? "ID_accounts = '$bill_data{'deposit_id_accounts'}', " : "ID_accounts = '$bill_data{'bill_id_accounts'}', ";
	my ($sth) = &Do_SQL("/*$cfg{'dbi_db'}*/ INSERT INTO sl_bills SET ID_vendors = '$bill_data{'id_vendors'}', Type = '$bill_data{'type'}', Currency = '$bill_data{'currency'}', Amount = '$bill_data{'amount'}', Memo = '$bill_data{'memo'}', $mod_currency BillDate = '$bill_data{'date'}', DueDate = '$bill_data{'date'}', AuthBy = '1', PaymentMethod = 'Wire Transfer', Status = 'New', Date = '$bill_data{'date'}', Time = CURTIME(), ID_admin_users = '1';");
	my ($id_bills) = $sth->{'mysql_insertid'};

	if($id_bills){
		&Do_SQL("INSERT INTO sl_bills_notes SET ID_bills = '$id_bills', Notes = 'Bill From Transition File', Type = 'Low', Date = CURDATE(), Time = CURTIME(), ID_admin_users = '1';");
	}

	return $id_bills;

}


#############################################################################
#############################################################################
#   Function: generate_new_bank_movements
#
#       Es: Crea un nuevo registro en sl_bank_movements
#       En: 
#
#    Created on: 06/25/2013 17:56:10
#
#    Author: _Roberto Barcenas_
#
#    Modifications:
#
#   Parameters:
#
#     - this_data : Hash data
#
#  Returns:
#
#   See Also:
#
#
#
sub generate_new_banks_movements {
#############################################################################
#############################################################################

	my (%bill_data) = @_;
	#&cgierr("Recibi $bill_data{'id_vendors'} + $bill_data{'type'} + $bill_data{'currency'} + $bill_data{'date'} + $bill_data{'amount'} + $bill_data{'memo'} + $bill_data{'currency_exchange'}");

	
	my $mod_currency = $bill_data{'currency_exchange'} ?
						"Amount = $bill_data{'amount'} * $bill_data{'currency_exchange'}, AmountCurrency = '$bill_data{'amount'}', currency_exchange = '$bill_data{'currency_exchange'}', " :
						"Amount = $bill_data{'amount'}, AmountCurrency = '$bill_data{'amount'}', currency_exchange = '$bill_data{'currency_exchange'}', ";

	my ($sth) = &Do_SQL("/*$cfg{'dbi_db'}*/ INSERT INTO sl_banks_movements SET ID_banks = '$bill_data{'id_banks'}', Type = 'Credits', BankDate = '$bill_data{'date'}', $mod_currency RefNum = '00000', doc_type = 'Wire Transfer', Memo = '$bill_data{'memo'}', Date = '$bill_data{'date'}', Time = CURTIME(), ID_admin_users = '1';");
	my ($id_banks_movs) = $sth->{'mysql_insertid'};

	if($id_banks_movs){

		&Do_SQL("INSERT INTO sl_banks_movrel SET ID_banks_movements = '$id_banks_movs', tablename = 'bills', tableid = '$bill_data{'id_bills'}', AmountPaid = '$bill_data{'amount'}', Date = '$bill_data{'date'}', Time = CURTIME(), ID_admin_users = '1';");
		&Do_SQL("INSERT INTO sl_banks_movements_notes SET ID_banks_movements = '$id_banks_movs', Notes = 'Bill From Transition File: ($bill_data{'id_bills'})', Type = 'Low', Date = CURDATE(), Time = CURTIME(), ID_admin_users = '1';");

	}

	return $id_banks_movs;

}


#############################################################################
#############################################################################
#   Function: generate_new_bills_expenses
#
#       Es: Genera registros en sl_bills_expenses para soportar las cuentas del Bill
#       En: 
#
#    Created on: 06/28/2013 14:45:10
#
#    Author: _Roberto Barcenas_
#
#    Modifications:
#
#   Parameters:
#
#     - this_data : Hash data
#
#  Returns:
#
#   See Also:
#
#
#
sub generate_new_bills_expenses {
#############################################################################
#############################################################################

	my (%bill_data) = @_;
	my $str = "Recibi $bill_data{'id_vendors'} + $bill_data{'type'} + $bill_data{'currency'} + $bill_data{'date'} + $bill_data{'amount'} + $bill_data{'memo'} + $bill_data{'currency_exchange'} + $bill_data{'tax'}";
	my $lines = $bill_data{'tax'} ? 2 : 1;
	my $last_id = 0;
	
	for(1..$lines){

		####################################
		####################################
		##########
		########## Generacion de registro en 
		##########
		####################################
		####################################

		my $amount = $bill_data{'amount'};
		my $id_accounts = $bill_data{'bill_id_accounts'};
		my $mod_related = '';
		
		if($bill_data{'tax'}){
			$amount = $_ == 1 ? round($bill_data{'amount'} / 1.16,2) : $bill_data{'amount'} - round($bill_data{'amount'} / 1.16,2);
			($_> 1) and ($id_accounts = $bill_data{'bill_id_tax_accounts'});
		}

		my $query = "/*  */ INSERT INTO sl_bills_expenses SET ID_bills = '$bill_data{'id_bills'}', Amount = '$amount', ID_accounts = '$id_accounts', ID_segments = 0, Related_ID_bills_expenses = '$last_id', Deductible = 'No', Date = '$bill_data{'date'}', Time = CURTIME(), ID_admin_users = '1';";
		my ($sth) = &Do_SQL($query);
		$last_id = $sth->{'mysql_insertid'};
		print "$str\n$query\n" if $bill_data{'id_bills'} eq '2049';

		$lines++;

	}

	return $last_id;

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
