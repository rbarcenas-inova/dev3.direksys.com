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
	require ('../subs/libs/lib.inventory.pl');
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
	&execute_fix_inventory;
	&disconnect_db;
}


#################################################################
#################################################################
#	Function: execute_fix_inventory
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
sub execute_fix_inventory{
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
	
	
	my ($sthMain) = &Do_SQL("SELECT ID_warehouses, ID_products, SUM(Quantity) AS WLQty
							FROM sl_warehouses_location
							WHERE 1
							GROUP BY ID_warehouses, ID_products;");

	print '<table style="border-collapse: collapse; border-spacing: none; width: 90%;">';
	print '<tr style="background-color: #cccccc;">';
	print '		<th>ID_warehouses</th>';
	print '		<th>ID_products</th>';
	print '		<th>Qty. WL.</th>';
	print '		<th> -> </th>';
	print '		<th>Qty. SC</th>';
	print '		<th> -> </th>';
	print '		<th>Diff</th>';	
	print '		<th>Log</th>';
	print '</tr>';

	my $i = 0;
	my $log = '';
	&Do_SQL("BEGIN;");
	ITEM: while ( my $refMain = $sthMain->fetchrow_hashref() ) {
		++$i;
		$this_log = "";
		my $id_warehouses	= $refMain->{'ID_warehouses'};
		my $id_products		= $refMain->{'ID_products'};
		my $qty_wl			= $refMain->{'WLQty'};

		$sql = "SELECT left_quantity 
				FROM sl_skus_trans 
				WHERE ID_warehouses = ".$id_warehouses." 
					AND ID_products = ".$id_products." 
					AND Cost_Avg > 0
				ORDER BY Date DESC, TIME DESC, ID_products_trans DESC
				LIMIT 1;";
		my $sth = &Do_SQL($sql);
		my $qty_st = $sth->fetchrow();

		next ITEM if( !$qty_st );

		my $diff = $qty_wl - $qty_st;

		if( abs($diff) > 0 ){
			$this_log .= "------------------------------------------------------------------ <br />\n";
			$this_log .= "ID_warehouses: $id_warehouses :: ID_products: $id_products <br />\n";
			$this_log .= "------------------------------------------------------------------ <br />\n";
			$this_log .= "Existencia en sl_warehouses_location: $qty_wl <br />\n";
			$this_log .= "Existencia en sl_skus_trans: $qty_st <br />\n";
			$this_log .= "Diferencia: $diff <br />\n";


			$sql = "SELECT COUNT(*) 
					FROM sl_skus_trans 
					WHERE ID_warehouses = ".$id_warehouses." 
						AND ID_products = ".$id_products." 
						AND Date >= '2015-06-30';";
			$this_log .= $sql."<br />\n";
			my $sth_count = &Do_SQL($sql);
			my $trs_count = $sth_count->fetchrow();

			if( $trs_count <= 1000 ){

				$sql = "SELECT ID_products_trans, Type_trans, Quantity, left_quantity, left_quantity_total, Cost_Avg, Cost
						FROM sl_skus_trans 
						WHERE ID_warehouses = ".$id_warehouses." 
							AND ID_products = ".$id_products." 
							AND Date >= '2015-06-30' 
						ORDER BY Date, Time, ID_products_trans;";
				$this_log .= $sql." <br />\n";
				my $sth_trs = &Do_SQL($sql);
				my $left_qty = 0;
				my $cont = 1;
				my $first_left_qty = 0;
				TRANS: while( my $ftrs = $sth_trs->fetchrow_hashref() ){
					if( $cont == 1 ){
						$left_qty = $ftrs->{'left_quantity'}; 
						$this_log .= "First left_quantity: ".$left_qty." <br />\n";

						$cont++;
						$first_left_qty = $ftrs->{'left_quantity'}

						next TRANS;
					}

					if( $ftrs->{'Type_trans'} eq 'IN' ){
						$left_qty += $ftrs->{'Quantity'};
					}else{
						$left_qty -= $ftrs->{'Quantity'};
					}

					$left_qty = 0 if( $left_qty < 0 );

					if( $left_qty != $ftrs->{'left_quantity'} ){
						$this_log .= "Left Qty diferente!!! => ".$ftrs->{'ID_products_trans'}.": ".$left_qty." vs ".$ftrs->{'left_quantity'}."<br />\n";
						last;
					}
					$cont++;
				}

			}else{
				$this_log .= "Demasiadas transacciones...<br /> \n";
			}

			#$this_log .= "Left Qty. en sl_skus_trans: $left_qty_w <br />\n";

			##------------------------------------------------
			## 
			##------------------------------------------------
			# if( $qty_sc > $qty_wl ){
			# 	$this_log .= "----- Se corrige sl_warehouses_location ------ <br />\n";
			# 	## Se obtiene la gaveta en la que se insertarÃ¡ la diferencia
			# 	$sql = "SELECT Location
			# 			FROM sl_warehouses_location
			# 			WHERE sl_warehouses_location.ID_warehouses=".$id_warehouses." 
			# 				AND ID_products=".$id_products."
			# 			ORDER BY Location
			# 			LIMIT 1;";
			# 	$this_log .= $sql." <br />\n";
			# 	my $sth = &Do_SQL($sql);
			# 	my $location = $sth->fetchrow();

			# 	$this_log .= "Gaveta seleccionada: $location <br />\n";

			# 	$sql = "INSERT INTO sl_warehouses_location SET 
			# 				ID_warehouses = ".$id_warehouses."
			# 				, ID_products = ".$id_products."
			# 				, Location = '".$location."'
			# 				, Quantity = ".abs($diff)."
			# 				, ID_customs_info = NULL
			# 				, Date = CURDATE()
			# 				, Time = CURTIME()
			# 				, ID_admin_users = 9999;";
			# 	$this_log .= $sql." <br />\n";
			# 	my $sth_ins = &Do_SQL($sql);
			# 	$this_log .= "Registro insertado: ".$sth_ins->{'mysql_insertid'}." <br />\n";

			# 	## Se inserta inventario en sl_warehouses_location
			# } else {
			# 	$this_log .= "----- Se corrige sl_skus_cost ------ <br />\n";
			# 	## Se obtiene el ID a modificar
			# 	$sql = "SELECT ID_skus_cost, Quantity 
			# 			FROM sl_skus_cost 
			# 			WHERE ID_warehouses = ".int($id_warehouses)." 
			# 				AND ID_products = ".int($id_products)." 
			# 			ORDER BY Date DESC, Time DESC
			# 			LIMIT 1;";
			# 	$this_log .= $sql." <br />\n";
			# 	my $sth = &Do_SQL($sql);
			# 	my ($id_skus_cost, $this_qty) = $sth->fetchrow();

			# 	$this_log .= "Existencia actual en el ID_skus_cost $id_skus_cost: $this_qty<br />\n";

			# 	## Se inserta inventario en sl_skus_cost
			# 	$sql = "UPDATE sl_skus_cost SET Quantity = Quantity + ".int($diff)." 
			# 			WHERE ID_skus_cost = ".$id_skus_cost.";";
			# 	$this_log .= $sql." <br />\n";
			# 	&Do_SQL($sql);
			# }
			##------------------------------------------------
			
			print '<tr style="">';
			print '		<td style="border-bottom: 1px dotted gray; text-align: center;">'.$id_warehouses.'</td>';
			print '		<td style="border-bottom: 1px dotted gray; text-align: center;">'.$id_products.'</td>';
			print '		<td style="border-bottom: 1px dotted gray; text-align: right;">'.$qty_wl.'</td>';
			print '		<td style="border-bottom: 1px dotted gray; text-align: center;"> -> </td>';
			print '		<td style="border-bottom: 1px dotted gray; text-align: center;">'.$qty_st.'</td>';
			print '		<td style="border-bottom: 1px dotted gray; text-align: center;"> -> </td>';
			print '		<td style="border-bottom: 1px dotted gray; text-align: right;">'.$diff.'</td>';
			print '		<td style="border-bottom: 1px dotted gray; text-align: left;">'.$this_log.'</td>';
			print '</tr>';

			$this_log .= "------------------------------------------------------------------ <br />\n";
			$log .= $this_log;

			$total_process++;
		}
	}
	&Do_SQL($finish_trans);

	#if( $in{'process'} eq 'commit' ){
		# Date
		my ($y, $m, $d) = Date::Calc::Today();
		my ($h, $n, $s) = Date::Calc::Now();
		my $date = sprintf('%02d%02d%02d%02d%02d', $y, $m, $d, $h, $n);
		# File
		my $file_path = '../../../files/e'.$in{'e'}.'/';
		my $file_name = 'fix_inventory_'.$date.'.txt';

		open(logs_fix,"> ".$file_path . $file_name) || die "No se puede abrir el archivo\n";
		print logs_fix $log;
		close(logs_fix);
	#}

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