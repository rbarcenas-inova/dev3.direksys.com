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
local ($in{'e'}) = 2;
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
#	Created by: _Gilberto Quirino_
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
	&process_costo_promedio_start;
	&disconnect_db;

}


#############################################################################
#############################################################################
#   Function: process_costo_promedio_start
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
sub process_costo_promedio_start {
#############################################################################
#############################################################################

	print "Content-type: text/html\n\n";

	my $inbound_file_path = $cfg{'path_upfiles'}. 'e'.$in{'e'} . '/';
	my $executed_file_path = $inbound_file_path . 'done/';
	my @cols = ('sku','upc','cost_avg','cost_adj','total_cost');

	
	opendir (LUEDIR, $inbound_file_path) || &cgierr('Unable to open directory ' . $inbound_file_path ,704,$!);
	@files = readdir(LUEDIR);# Read in list of files in directory..
	closedir (LUEDIR);


	##### Looping files
	FILE: foreach my $file_name (sort @files) {

		next if ($file_name =~ /^\./);		# Skip "." and ".." entries..
		next if ($file_name =~ /^index/);		# Skip index.htm type files..
		next if ($file_name !~ /csv$/);		# Skip not cvs type files..
		next if ($file_name ne 'costo_promedio_inicial.csv');

		print "<br />Intentando abrir el archivo " . $inbound_file_path . $file_name  . "\n";

		##### Opening File
		if (-e  $inbound_file_path . $file_name) {

			open(my $this_file, "<", $inbound_file_path . $file_name) or &cgierr('Unable to open file: '. $inbound_file_path . $file_name, 601,$!);

			my $sku_ok;
			my $sku_failed;

			print "<br />Ejecutando lineas en el archivo $file_name...\n\n";

			### Inicializa la transacción para los datos del archivo actual
			print '<table style="min-width: 800px;" border="1">';
			print '<tr>';
			print '<th>SKU</th>';
			print '<th>UPC</th>';			
			print '<th>Cost AVG</th>';
			print '<th>Cost Adj.</th>';
			print '<th>Cost Total.</th>';
			print '<th>Notes</th>';
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
				print '<td>'.$this_data{'sku'}.'</td>';
				print '<td>'.$this_data{'upc'}.'</td>';
				print '<td>'.$this_data{'cost_avg'}.'</td>';
				print '<td>'.$this_data{'cost_adj'}.'</td>';
				print '<td>'.$this_data{'total_cost'}.'</td>';

				my $sqlss  = '';
				##### Processing Data
				if($this_data{'sku'} ne '' and $this_data{'cost_avg'} > 0){

					### Actualiza el registro en cu_skus_trans
					if( !$this_data{'cost_adj'} or $this_data{'cost_adj'} eq '' or $this_data{'cost_adj'} eq '0.00' ){
						next LINE;
					}else{

						my $sql = "SELECT ID_products, left_quantity_total 
									FROM cu_skus_trans 
									WHERE ID_products=".$this_data{'sku'}.";";
						$sqlss = $sql.'<br>';
						my $sth = &Do_SQL($sql);
						my ($id_products, $left_qty_total) = $sth->fetchrow_array();

						if( int($id_products) == 0 ){
							my $sql = "SELECT left_quantity_total
										FROM sl_skus_trans WHERE ID_products=".$this_data{'sku'}." 
										ORDER BY ID_products_trans DESC LIMIT 1;";
							$sqlss .= $sql.'<br>';
							my $sth = &Do_SQL($sql);
							$left_qty_total = $sth->fetchrow_array();
						}

						my $sql_ins = "REPLACE INTO cu_skus_trans SET 
											ID_products = '".$this_data{'sku'}."'
											, left_quantity_total = '".$left_qty_total."'
											, Cost_Avg = '".$this_data{'total_cost'}."'
											, Cost = '".$this_data{'cost_avg'}."'
											, Cost_Adj = '".$this_data{'cost_adj'}."'
											, Cost_Add = 0
											/*, ID_customs_info = '".$data_trans{'ID_customs_info'}."'*/
											, Date = CURDATE()
											, Time = CURTIME();";
						$sqlss .= $sql_ins.'<br>';
						&Do_SQL($sql_ins);
					}

					###-----------------------------------------------
					### Actializa el ultimo registro en skus_trans
					###-----------------------------------------------
					# my $sql = "SELECT ID_products_trans, Type_trans, Type, Cost_Adj FROM sl_skus_trans WHERE ID_products=".$this_data{'sku'}." ORDER BY ID_products_trans DESC LIMIT 1;";
					# my $sth = &Do_SQL($sql);
					# my ($id_last_trans, $type_trans, $type, $cost_adj) = $sth->fetchrow_array();
					# if( int($id_last_trans) > 0 ){
					# 	# my $sql_upd = "Cost_Avg = '".$this_data{'cost_avg'}."'";
					# 	# if( !$type_trans ){
					# 	# 	if ( $type eq 'Purchase' or $type eq 'Return' or $type eq 'Transfer In' ){
					# 	# 		$type_trans = 'IN';
					# 	# 	}elsif( $type eq 'Return to Vendor' or $type eq 'Sale' or $type eq 'Transfer Out' ){
					# 	# 		$type_trans = 'OUT';
					# 	# 	}
					# 	# 	$sql_upd .= ", Type_trans = '".$type_trans."'";
					# 	# }

					# 	# $sql_upd .= ", Cost_Adj = '".$this_data{'cost_adj'}."'" if( $cost_adj == 0 );

					# 	# $sql = "UPDATE sl_skus_trans SET $sql_upd WHERE ID_products_trans = '".$id_last_trans."';";
					# 	# &Do_SQL($sql);

					# 	# $notes = 'OK: '.$sql.'<br>';
					# 	$notes = 'OK: SKU Actualizado<br>';
					# }else{
					# 	$notes = "No existe registro en skus trans para este SKU<br>";

					# 	$this_data{'cost_adj'} = 0 if(!$this_data{'cost_adj'});
					# 	&Do_SQL("INSERT INTO `direksys2_e2`.`sl_skus_trans` (`ID_products`, `ID_warehouses`, `Type`, `Type_trans`, `tbl_name`, `Quantity`, `Cost_Avg`, `Cost`, Cost_Adj, `Date`, `Time`, `ID_admin_users`) 
					# 			VALUES (".$this_data{'sku'}.", 1001, 'Adjustment', 'IN', 'sl_adjustments', 0, ".$this_data{'cost_avg'}.", ".$this_data{'cost_avg'}.", ".$this_data{'cost_adj'}.", '2010-01-01', '00:01:00', 11);");

					# 	$notes .= "Se inserta transaccion ficticia de entrada (IN)";

					# 	#next LINE;
					# }
					# ###-----------------------------------------------

					# ###-----------------------------------------------
					# ### Actializa el ultimo registro de entrada (IN) en skus_trans
					# ###-----------------------------------------------
					# my $sql = "SELECT ID_products_trans, left_quantity_total, Cost_Adj FROM sl_skus_trans WHERE ID_products=".$this_data{'sku'}." AND Type_trans='IN' ORDER BY ID_products_trans DESC LIMIT 1;";
					# my $sth = &Do_SQL($sql);
					# my ($id_last_trans_in, $left_qty_total, $cost_adj) = $sth->fetchrow_array();
					# if( int($id_last_trans_in) > 0 ){
					# 	# $sql = "Mismo registro";
					# 	# if( $id_last_trans != $id_last_trans_in ){
					# 	# 	my $sql_upd = "Cost_Avg = '".$this_data{'cost_avg'}."'";

					# 	# 	$sql_upd .= ", Cost_Adj = '".$this_data{'cost_adj'}."'" if( $cost_adj == 0 );

					# 	# 	$sql = "UPDATE sl_skus_trans SET $sql_upd WHERE ID_products_trans = '".$id_last_trans_in."';";
					# 	# 	&Do_SQL($sql);
					# 	# }

					# 	# $notes .= 'OK: '.$sql;
					# 	$notes .= 'OK: SKU Actualizado<br>';
					# }else{
					# 	$notes .= "No existe registro de entrada (IN) en skus trans para este SKU<br>";

					# 	$this_data{'cost_adj'} = 0 if(!$this_data{'cost_adj'});
					# 	&Do_SQL("INSERT INTO `direksys2_e2`.`sl_skus_trans` (`ID_products`, `ID_warehouses`, `Type`, `Type_trans`, `tbl_name`, `Quantity`, `Cost_Avg`, `Cost`, Cost_Adj, `Date`, `Time`, `ID_admin_users`) 
					# 			VALUES (".$this_data{'sku'}.", 1001, 'Adjustment', 'IN', 'sl_adjustments', 0, ".$this_data{'cost_avg'}.", ".$this_data{'cost_avg'}.", ".$this_data{'cost_adj'}.", '2010-01-01', '00:01:00', 11);");

					# 	$notes .= "Se inserta transaccion ficticia de entrada (IN)";
					# }
					###-----------------------------------------------

					print '<td>'.$notes.$sqlss.'</td>';

					++$sku_ok;
				}else{

					++$sku_failed;
					print '<td style="color: red;">No encontre datos para ' . join(', ', @line_data) . '</td>';
					push(@orders_data_error, join(', ', @line_data) . "\n" );

				}
				
				print '</tr>';

			} ## End Line
			print '</table>';
			### Finaliza la transacción
			&Do_SQL("COMMIT;");
			#&Do_SQL("ROLLBACK;");

			print "<br />Total Trans Updated: $sku_ok\nTotal Trans Failed: $sku_failed\n\n";
			
		} ## End File


        ### Moving the file to Backup
		#print "<br />Moving $inbound_file_path$file_name to $executed_file_path$file_name\n\n";
		#move($inbound_file_path . $file_name, $executed_file_path . $file_name);
		#print "<br />Sleeping 3 seconds\n\n";
		#sleep(3);
        #print "<br /><br />\n\n\n\n";
        #last FILE;

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
