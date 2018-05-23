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
	&execute_fix_groups_perms;
	&disconnect_db;
}


#################################################################
#################################################################
#	Function: execute_fix_groups_perms
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
sub execute_fix_groups_perms{
	my $process = ($in{'process'} ne 'commit')? qq|<span style="color: gray; padding:5px;">TESTING</span>|:qq|<span style="color: red; font-weight: bold; padding:5px;">EXECUTING</span>|;
	#my $log_email;

	&load_settings;
	print "Content-type: text/html\n\n";
	print qq|<meta http-equiv="content-type" content="text/html; charset=utf-8" />\n\n|;
	print '<h4 style="border-bottom: 3px double gray;">DIREKSYS '.$cfg{'app_title'}.' e('.$in{'e'}.') :: Fix de Left Qty <span style="position: relative; float: right;">Process: '.$process.'</span></h4>';
	
	
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
	
	$id_products_trans = 4916812 if ($in{'e'} == 2);
    $id_products_trans = 114263 if ($in{'e'} == 3);
    $id_products_trans = 211068 if ($in{'e'} == 4);
    $id_products_trans = 108872 if ($in{'e'} == 11);


	print '<table border=1 style="border-spacing: 0; width: 90%;">';	
	
	my ($sthMain) = &Do_SQL("SELECT ID_products_trans, ID_products, ID_warehouses
								FROM sl_skus_trans
								WHERE Type_trans='IN' 
									AND left_quantity=0 
									AND ID_products_trans>$id_products_trans								
								GROUP BY ID_products, ID_warehouses
								ORDER BY ID_products, ID_warehouses, ID_products_trans DESC;");

	&Do_SQL("BEGIN;");	
	while ( $refMain = $sthMain->fetchrow_hashref() ) {
		my $id_products = $refMain->{'ID_products'};
		my $id_warehouses = $refMain->{'ID_warehouses'};
		my $this_id_products_trans = $refMain->{'ID_products_trans'};
		
		print '<tr>';
		print '	<td style="font-size: 14pt; font-weight: bold;">ID_products: '.$id_products.' :: ID_warehouses: '.$id_warehouses.'</td>';
		print '</tr>';
		print '<tr><td>';

		$logs .= "----------------------------------------------------------------------------\n";
		$logs .= "--- Inicia el proceso para: ID_products: $id_products :: ID_warehouses: $id_warehouses\n";
		$logs .= "----------------------------------------------------------------------------\n";		

		### Se obtiene el ultimo left_quantity correcto
		my $sql = "SELECT left_quantity
					FROM sl_skus_trans
					WHERE ID_products=$id_products 
						AND ID_warehouses=$id_warehouses 
						AND ID_products_trans>$id_products_trans
						AND ID_products_trans < $this_id_products_trans
					ORDER BY ID_products_trans DESC
					LIMIT 1;";
		my $sth = &Do_SQL($sql);
		my $last_left_qty_ok = $sth->fetchrow();
		$last_left_qty_ok = 0 if( !$last_left_qty_ok );

		### Se recorren y corrigen los registros de transacciones posteriores al IN con left_quantity=0
		my $sql = "SELECT ID_products_trans, Type_trans, Quantity, left_quantity
					FROM sl_skus_trans
					WHERE ID_products=$id_products
						AND ID_warehouses=$id_warehouses 						
						AND ID_products_trans>$id_products_trans
					ORDER BY ID_warehouses, ID_products_trans ASC;";
		my $sth = &Do_SQL($sql);
		my $last_left_qty = 0;
		while( $rec = $sth->fetchrow_hashref() ){
			my $this_left_qty = 0;
			if( $rec->{'Type_trans'} eq 'IN' ){
				$this_left_qty = ($last_left_qty + $rec->{'Quantity'});
			}elsif($last_left_qty > $rec->{'Quantity'}){
				$this_left_qty = ($last_left_qty - $rec->{'Quantity'});
			}
			$last_left_qty = $this_left_qty;

			### Actualiza el left_quantity de este registro
			my $sql = "UPDATE sl_skus_trans SET left_quantity=$this_left_qty WHERE ID_products_trans=".$rec->{'ID_products_trans'}.";";
			&Do_SQL($sql);
			$logs .= $sql."\n";
			$logs .= "Registro editado :: ".$rec->{'ID_products_trans'}." TypeTrans: ".$rec->{'Type_trans'}." Qty: ".$rec->{'Quantity'}.", LeftQty: ".$rec->{'left_quantity'}." -> ".$this_left_qty."\n";
			print $sql."<br>";
			print "Registro editado :: ".$rec->{'ID_products_trans'}." TypeTrans: ".$rec->{'Type_trans'}." Qty: ".$rec->{'Quantity'}.", LeftQty: ".$rec->{'left_quantity'}." -> ".$this_left_qty."<br>";
		}		
			
		print '</td></tr>';

		++$total_process;

	}
	&Do_SQL($finish_trans);
	if( $in{'process'} ne 'commit' ){
		# Date
		my ($y, $m, $d) = Date::Calc::Today();
		my ($h, $n, $s) = Date::Calc::Now();
		my $date = sprintf('%02d%02d%02d%02d%02d', $y, $m, $d, $h, $n);
		# File
		my $file_path = '../../../files/e'.$in{'e'}.'/';
		my $file_name = 'fix_left_qty_'.$date.'.txt';

		open(logs_fix,"> ".$file_path . $file_name) || die "No se puede abrir el archivo\n";
		print logs_fix $logs;
		close(logs_fix);
	}

	print '</table>';

	print '<br /><br /><hr /><hr />';
	print '<span style="font-weight: bold;">Custom Reports procesados: </span> <span style="color: #209001;">'.$total_process.'</span><br />';
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