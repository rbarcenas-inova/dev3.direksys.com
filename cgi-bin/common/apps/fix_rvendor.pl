#!/usr/bin/perl
#######################################################################
#######################################################################
#######################################################################

use DBI;
use DBIx::Connector;
use DBD::mysql;
use Cwd;


local ($dir) = getcwd;
local ($in{'e'}) = 3;
local($in{'process'}) = 'commit';

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
	&fix_rvendor;
	&disconnect_db;

}


#############################################################################
#############################################################################
#   Function: process_bills
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
sub fix_rvendor {
############################################################################# 
#############################################################################
	
	my $strmovs;
	my $q1 = "SELECT 
					ID_tableused
					, tableused
					, EffDate
					, ID_tablerelated
					, IF(tablerelated IS NULL,'NULL', tablerelated)
					, Category
					, CONCAT(Date, ' ', Time)
				FROM sl_movements m 
				WHERE 
					m.ID_accounts = 137 
					AND m.Credebit = 'Credit'
					AND m.tableused = 'sl_purchaseorders' 
					AND Status = 'Active'
					AND YEAR(EffDate) >= 2014 
				GROUP BY m.ID_tableused, CONCAT(m.Date,' ',m.Time)
				ORDER BY m.EffDate, m.ID_tableused /*LIMIT 50*/;";

	print "Q1 : $q1\n\n";
				
	my $x = 0;			
	my ($sth) = &Do_SQL($q1);
	while(my ($id_tu, $tu, $effdate, $id_tr, $tr, $cat, $reg_date) = $sth->fetchrow()){

		++$x;
		my $touched = 0;
		my $q2 = "SELECT 
						ID_movements
						, Name
						, Amount
						, Credebit
						, ID_journalentries
						, sl_journalentries.Status
					FROM sl_movements INNER JOIN sl_accounts USING(ID_accounts)
					LEFT JOIN sl_journalentries USING(ID_journalentries)
					WHERE
						ID_tableused = '$id_tu'
						AND tableused = '$tu'
						AND EffDate = '$effdate'
						AND ID_tablerelated = '$id_tr'
						AND IF('$tr' = 'NULL', tablerelated IS NULL, tablerelated = '$tr')
						AND Category = '$cat'
						AND sl_movements.Status = 'Active'
						AND ABS(TIMESTAMPDIFF(SECOND, '$reg_date', CONCAT(sl_movements.Date,' ',sl_movements.Time))) <= 2 
						ORDER BY ID_movements;";

		print "($x) - PO: $id_tu\n$q2\n";

		$sth_prod = &Do_SQL($q2);

		while( my($id_movements, $acc, $amt, $credebit, $id_journal, $journal_status) = $sth_prod->fetchrow()){

			print "ID: $id_movements | Acc: $acc | Amt: $amt | CR: $credebit | JOU: $id_journal | JS: $journal_status\n";

			if(!$id_journal or lc($journal_status) ne 'posted'){

				###
				### Solo se pasan a Inactive
				###
				my $qi = "UPDATE sl_movements SET Status = 'Inactive' WHERE ID_movements = '$id_movements';";
				print "$qi ";
				
				if ($in{'process'} eq 'commit'){

					&Do_SQL($qi); 
					print " - Done";

				}
				print "\n";

			}else{

				###
				### Se duplica mov. en fecha de hoy
				###
				$touched = 1;

				if($strmovs !~ /$id_movements/){
					print "Cancelacion de Movimiento ";	
				}else{
					print "Skipped ";	
				}
				


				if ($in{'process'} eq 'commit'){

					my $modcredebit = $credebit eq 'Debit' ? 'Credit' : 'Debit';
					my (%overwrite) = ('credebit' => $modcredebit, 'id_journalentries' => '0', 'category' => 'Compras');
					my $applied_movement = &Do_selectinsert('sl_movements', "ID_movements = '$id_movements'", "", "", %overwrite);
					&Do_SQL("UPDATE sl_movements SET Date = '2014-12-31'/*CURDATE()*/, EffDate = '2014-12-31'/*CURDATE()*/ WHERE ID_movements = '$applied_movement';");

					print " ID_nuevo: $applied_movement";

				}

				print "\n";

			}
			$strmovs .= "$id_movements|";

		}

		print "\n";
		#return if $touched;

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
