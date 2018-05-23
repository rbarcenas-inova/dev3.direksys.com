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
	&execute_fix_last_cost;
	&disconnect_db;
}


#################################################################
#################################################################
#	Function: execute_fix_last_cost
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
sub execute_fix_last_cost{
	my $process = ($in{'process'} ne 'commit')? qq|<span style="color: gray; padding:5px;">TESTING</span>|:qq|<span style="color: red; font-weight: bold; padding:5px;">EXECUTING</span>|;
	#my $log_email;

	&load_settings;
	print "Content-type: text/html\n\n";
	print qq|<meta http-equiv="content-type" content="text/html; charset=utf-8" />\n\n|;
	print '<h4 style="border-bottom: 3px double gray;">DIREKSYS '.$cfg{'app_title'}.' e('.$in{'e'}.') :: Extraccion del ultimo costo de un sku desde un PO <span style="position: relative; float: right;">Process: '.$process.'</span></h4>';
	
	
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
	
	# $id_products_trans = 4916812 if ($in{'e'} == 2);
 #    $id_products_trans = 114263 if ($in{'e'} == 3);
 #    $id_products_trans = 211068 if ($in{'e'} == 4);
 #    $id_products_trans = 108872 if ($in{'e'} == 11);


	print '<table border=1 style="border-spacing: 0; width: 90%;">';	
	
	my ($sthMain) = &Do_SQL("Select ID_products From sl_skus_trans Where Date>='2015-06-30' And ID_products>0 Group by ID_products;");

	&Do_SQL("BEGIN;");	
	while ( $refMain = $sthMain->fetchrow_hashref() ) {
		my $id_products = $refMain->{'ID_products'};
		#my $id_warehouses = $refMain->{'ID_warehouses'};
				
		print '<tr>';
		print '	<td style="font-size: 14pt; font-weight: bold;">ID_products: '.$id_products.' </td>';
		print '</tr>';
		print '<tr><td>';

		$logs .= "----------------------------------------------------------------------------\n";
		$logs .= "--- Inicia el proceso para: ID_products: $id_products\n";
		$logs .= "----------------------------------------------------------------------------\n";		

		### Se obtiene el ultimo precio de compra(Costo)
		# my $sql = "SELECT Price AS Cost
		# 			FROM sl_purchaseorders_items 
		# 				INNER JOIN sl_purchaseorders USING(ID_purchaseorders)
		# 			WHERE ID_products=$id_products
		# 				AND Received > 0 
		# 			ORDER BY sl_purchaseorders_items.ID_purchaseorders DESC 
		# 			LIMIT 1;";
		my $sql = "SELECT if(sl_skus_trans.Cost_Avg=0,sl_skus_trans.Cost,sl_skus_trans.Cost_Avg)Cost
					FROM sl_skus_trans
						INNER JOIN sl_wreceipts_items ON sl_wreceipts_items.ID_wreceipts=sl_skus_trans.ID_trs AND sl_wreceipts_items.ID_products=sl_skus_trans.ID_products
						INNER JOIN sl_wreceipts ON sl_wreceipts.ID_wreceipts=sl_wreceipts_items.ID_wreceipts
					WHERE sl_skus_trans.tbl_name = 'sl_wreceipts'
						AND sl_skus_trans.ID_products = '$id_products'
						AND sl_skus_trans.Type = 'Purchase'
					ORDER BY sl_skus_trans.ID_products_trans DESC
					LIMIT 1;";
		my $sth = &Do_SQL($sql);
		my $last_cost = $sth->fetchrow();
		if( $last_cost == 0 ){
			my $sql = "SELECT Price AS Cost
			 			FROM sl_purchaseorders_items 
			 				INNER JOIN sl_purchaseorders USING(ID_purchaseorders)
			 			WHERE ID_products=$id_products
			 				AND Received > 0 
			 			ORDER BY sl_purchaseorders_items.ID_purchaseorders DESC 
			 			LIMIT 1;";
			my $sth = &Do_SQL($sql);
			$last_cost = $sth->fetchrow();
		}
		
		my $sql_left_qty_total = '';
		if( int($in{'leftqty'}) == 1 ){
			###----------------------------------------------------
			### Se obtiene el left_quantity_total
			###----------------------------------------------------
			my $sql = "SELECT MAX(ID_products_trans) ID_last_trans, ID_warehouses
						FROM sl_skus_trans
						WHERE Date >= '2015-06-30'
							AND ID_products='$id_products' 
							AND ID_warehouses>0
						GROUP BY ID_warehouses;";
			my $sthW = &Do_SQL($sql);
			my $left_qty_total = 0;		
			while( my $rec = $sthW->fetchrow_hashref() ){
				my $sthQty = &Do_SQL("SELECT left_quantity FROM sl_skus_trans WHERE ID_products_trans=".$rec->{'ID_last_trans'}.";");
				my $left_qty = $sthQty->fetchrow();
				$left_qty = 0 if( !$left_qty );

				$left_qty_total += $left_qty;
			}
			$sql_left_qty_total = ", LeftQtyTotal = $left_qty_total";
		}

		if( $last_cost and $last_cost > 0 ){
			
			my $sth = Do_SQL("SELECT GROUP_CONCAT(ID_inventory) IDs
								FROM cu_inventory
								WHERE ID_products=$id_products;");
			my $ids = $sth->fetchrow();

			### Actualiza el costo para este SKU
			my $sql = "UPDATE cu_inventory SET Cost = $last_cost $sql_left_qty_total WHERE ID_products=$id_products;";
			&Do_SQL($sql);
			$logs .= $sql."\n";
			$logs .= "IDs editados :: $ids\n";
			print $sql."<br>";
			print "IDs editados :: $ids<br>";

			++$total_process;
		}		
			
		print '</td></tr>';

	}
	&Do_SQL($finish_trans);
	if( $in{'process'} ne 'commit' ){
		# Date
		my ($y, $m, $d) = Date::Calc::Today();
		my ($h, $n, $s) = Date::Calc::Now();
		my $date = sprintf('%02d%02d%02d%02d%02d', $y, $m, $d, $h, $n);
		# File
		my $file_path = '../../../files/e'.$in{'e'}.'/';
		my $file_name = 'fix_last_cost_sku_'.$date.'.txt';

		open(logs_fix,"> ".$file_path . $file_name) || die "No se puede abrir el archivo\n";
		print logs_fix $logs;
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