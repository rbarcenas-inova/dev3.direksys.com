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
# use File::Copy;

# local ($dir) = getcwd;
# Default la 2 porque este proceso fue diseñado para TMK
local(%in) = &parse_form;
# local ($in{'e'}) = 2 if (!$in{'e'});
# chdir($dir);

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
#	Created by: _Roberto Barcenas_
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
	&fix_inventory_cost;
	&disconnect_db;

}


#################################################################
#################################################################
#	Function: fix_inventory_cost
#
#   		Corrige las tablas sl_skus_cost y sl_warehouses_locations
#
#	Created by: ISC Alejandro Diaz
#
#
#	Modified By:Alejandro Diaz
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
sub fix_inventory_cost{
#################################################################
#################################################################

# Ninguna tabla es correcta
# lo mas realista es la tabla de sl_warehouses_location y se caia sl_skus_cost
# lo que se ve en pantalla es de sl_warehouses_location por lo que debemos basrnos en Estado
# debemos agrupar por almacen y producto

# registros en 0 de sl_warehouses_location se borran

# no contar lo de los almacenes vistuales AAA quien sabe que

# debe ser basado en lo real

# ID_warehouses=0 se va a la basura
	my $process = ($in{'process'} ne 'commit')? qq|<span style="color:#000;background-color:gray;padding:5px;">ANALYZING</span>|:qq|<span style="color:#FFF;background-color:red;padding:5px;">EXECUTING</span>|;
	my $log_email;
	my $easy_fix=0;
	my $hard_fix=0;
	my $hard_fix_quantity=0;

	&load_settings;
	print "Content-type: text/html\n\n";
	print qq|<meta http-equiv="content-type" content="text/html; charset=utf-8" />\n\n|;
	print qq|<title>FIX :: sl_skus_cost & sl_warehouses_locations</title>\n\n|;
	print "<h4>DIREKSYS $cfg{'app_title'} (e$in{'e'}) - Fix sl_skus_cost & sl_warehouses_location</h5>";
	
	if (!$in{'e'}){
		print qq|<span style="color:red;">ID de empresa es requerido</span>|;
		return;
	}

	## Analizando Almacenes en sl_skus_cost
	print qq|<table border="1" cellpadding="8" cellspacing="0" width="50%" style="font-size:12px; border: 1px solid #222222;">|;
	print qq|	<tr>
					<th width="35%">sl_skus_cost.ID_warehouses</th>
					<th>Accion</th>
				</tr>|;
	
	my $sth = &Do_SQL("SELECT sl_skus_cost.ID_warehouses
	FROM sl_skus_cost
	LEFT JOIN sl_warehouses ON sl_skus_cost.ID_warehouses=sl_warehouses.ID_warehouses
	WHERE sl_warehouses.Name IS NULL
	GROUP BY sl_skus_cost.ID_warehouses
	ORDER BY sl_skus_cost.ID_warehouses;");
	while (my $rec = $sth->fetchrow_hashref()){
		$sql = "DELETE FROM sl_skus_cost WHERE ID_warehouses = '$rec->{'ID_warehouses'}';";
		print qq|<tr>
					<td align="right">$rec->{'ID_warehouses'}</td>
					<td>$sql</td>
				</tr>|;
		&Do_SQL($sql) if ($in{'process'} eq 'commit');
	}
	
	print qq|</table><br>|;

	#  - - - - - - - - - - - - - - - - - - - - - - - - - - -
	## Analizando Almacenes en sl_warehouses_location
	#  - - - - - - - - - - - - - - - - - - - - - - - - - - -
	print qq|<table border="1" cellpadding="8" cellspacing="0" width="50%" style="font-size:12px; border: 1px solid #222222;">|;
	print qq|	<tr>
					<th width="35%">sl_warehouses_location.ID_warehouses</th>
					<th>Accion</th>
				</tr>|;
	
	my $sth = &Do_SQL("SELECT sl_warehouses_location.ID_warehouses
	FROM sl_warehouses_location
	LEFT JOIN sl_warehouses ON sl_warehouses_location.ID_warehouses=sl_warehouses.ID_warehouses
	WHERE sl_warehouses.Name IS NULL
	GROUP BY sl_warehouses_location.ID_warehouses
	ORDER BY sl_warehouses_location.ID_warehouses;");
	while (my $rec = $sth->fetchrow_hashref()){
		$sql = "DELETE FROM sl_warehouses_location WHERE ID_warehouses = '$rec->{'ID_warehouses'}';";
		print qq|<tr>
					<td align="right">$rec->{'ID_warehouses'}</td>
					<td>$sql</td>
				</tr>|;
		&Do_SQL($sql) if ($in{'process'} eq 'commit');
	}
	
	print qq|</table><br>|;

	#  - - - - - - - - - - - - - - - - - - - - - - - - - - -
	## Buscando diferencias entre tablas
	#  - - - - - - - - - - - - - - - - - - - - - - - - - - -
	print qq|<table border="1" cellpadding="5" cellspacing="0" width="100%" style="font-size:12px; border: 1px solid #222222;">|;
	print qq|	<tr>
					<th colspan="4">sl_warehouses_location</th>
					<th colspan="4">sl_skus_cost</th>
					<th></th>
				</tr>|;

	print qq|	<tr>
					<th>#</th>
					<th>ID_warehouses</th>
					<th>ID_products</th>
					<th>Quantity</th>
					<th></th>
					<th>ID_warehouses</th>
					<th>ID_products</th>
					<th>Quantity</th>
					<th></th>
					<th>Diference</th>
				</tr>|;
	my $sth = &Do_SQL("
	SELECT 
		sl_warehouses_location.ID_warehouses, sl_warehouses_location.ID_products, SUM(sl_warehouses_location.Quantity)Quantity
		, sl_skus_cost.ID_warehouses sc_ID_warehouses, sl_skus_cost.ID_products sc_ID_products, SUM(sl_skus_cost.Quantity)sc_Quantity
		, (SUM(sl_warehouses_location.Quantity) - ifnull(SUM(sl_skus_cost.Quantity),0))Diference

	FROM (
		SELECT
			sl_warehouses_location.ID_warehouses
			, sl_warehouses_location.ID_products
			, SUM(sl_warehouses_location.Quantity)Quantity
		FROM sl_warehouses_location 
		GROUP BY sl_warehouses_location.ID_warehouses, sl_warehouses_location.ID_products
	)sl_warehouses_location 
	INNER JOIN sl_warehouses ON sl_warehouses_location.ID_warehouses=sl_warehouses.ID_warehouses
	LEFT JOIN (
		SELECT 
			sl_skus_cost.ID_warehouses
			, sl_skus_cost.ID_products
			, SUM(sl_skus_cost.Quantity)Quantity
		FROM sl_skus_cost
		WHERE 1
		AND sl_skus_cost.Cost IS NOT NULL
		AND sl_skus_cost.Cost > 0
		AND sl_skus_cost.Quantity > 0
		GROUP BY sl_skus_cost.ID_warehouses, sl_skus_cost.ID_products
	)sl_skus_cost ON sl_skus_cost.ID_warehouses=sl_warehouses_location.ID_warehouses AND sl_skus_cost.ID_products=sl_warehouses_location.ID_products
	WHERE 1
	GROUP BY sl_warehouses_location.ID_warehouses, sl_warehouses_location.ID_products
	ORDER BY sl_warehouses_location.ID_warehouses, sl_warehouses_location.ID_products");
	my $recs = 0;
	my $recs_dif = 0;
	my $neg_fix=0;
	while (my $rec = $sth->fetchrow_hashref()){
		$recs++;
		$recs_dif++ if ($rec->{'Diference'} != 0);
		my $style = ($rec->{'Diference'} == 0)? qq|style="display:none;background-color:#C1F325;color:#000"|:'';
		$style = ($rec->{'Diference'} < 0)? qq|style="background-color:#FF26A8;color:#000"|:$style;
		$style = (!$rec->{'sc_ID_warehouses'})? qq|style="background-color:#FF784D;color:#000"|:$style;
		print qq|<tr $style >
					<td align="right">$recs</td>
					<td align="right">$rec->{'ID_warehouses'}</td>
					<td align="right">$rec->{'ID_products'}</td>
					<td align="right">$rec->{'Quantity'}</td>
					<td>--</td>
					<td align="right">$rec->{'sc_ID_warehouses'}</td>
					<td align="right">$rec->{'sc_ID_products'}</td>
					<td align="right">$rec->{'sc_Quantity'}</td>
					<td>--</td>
					<td align="right">$rec->{'Diference'}</td>
				</tr>|;
		
		#  - - - - - - - - - - - - - - - - - - - - - - - - - - -
		#  - - - - - - - - - - - - - - - - - - - - - - - - - - -
		# 					ANALISIS DE COSTOS
		#  - - - - - - - - - - - - - - - - - - - - - - - - - - -
		#  - - - - - - - - - - - - - - - - - - - - - - - - - - -
		if ($rec->{'Diference'} != 0 and $rec->{'Quantity'} > 0) {

			print qq|<tr>
						<td colspan="10">
							<table border="1" cellpadding="5" cellspacing="0" width="100%" style="font-size:12px; border: 1px solid #222222;">|;

			my $sth2 = &Do_SQL("SELECT 
				sl_skus_cost.ID_skus_cost
				, sl_skus_cost.Tblname
				, sl_skus_cost.ID_warehouses
				, sl_skus_cost.ID_products
				, sl_skus_cost.Quantity
				, sl_skus_cost.Cost
				, sl_skus_cost.Date
				, sl_skus_cost.Time
			FROM sl_skus_cost 
			WHERE 1
			AND sl_skus_cost.ID_warehouses='$rec->{'ID_warehouses'}'
			AND sl_skus_cost.ID_products='$rec->{'ID_products'}'
			AND sl_skus_cost.Cost IS NOT NULL
			AND sl_skus_cost.Cost > 0
			AND sl_skus_cost.Quantity > 0
			ORDER BY sl_skus_cost.ID_warehouses, sl_skus_cost.ID_products, sl_skus_cost.Date DESC, sl_skus_cost.Time DESC");
			my $recs2 = 0;
			my $last_id;
			my $first_id;
			while (my $rec2 = $sth2->fetchrow_hashref()){
				$recs2++;
				$last_id = $rec2->{'ID_skus_cost'};
				$first_id = $rec2->{'ID_skus_cost'} if ($recs2 == 1);
				print qq|
					<tr>
						<td align="right" style="background-color:#0098FF">$recs2</td>
						<td align="right">$rec2->{'ID_skus_cost'}</td>
						<td align="right">$rec2->{'Tblname'}</td>
						<td align="right">$rec2->{'ID_warehouses'}</td>
						<td align="right">$rec2->{'ID_products'}</td>
						<td align="right">$rec2->{'Quantity'}</td>
						<td align="right">$rec2->{'Cost'}</td>
						<td align="right">$rec2->{'Date'}</td>
						<td align="right">$rec2->{'Time'}</td>
					</tr>|;
			}
			
			if ($recs2 == 1 and $rec->{'Diference'} > 0){
				$easy_fix++;
				$sql_fix = "UPDATE sl_skus_cost SET Quantity=(Quantity+ABS($rec->{'Diference'})) WHERE ID_skus_cost='$last_id' LIMIT 1;";
				print qq|
					<tr>
						<td align="right" colspan="9" style="background-color:#FFFF00">$sql_fix</td>
					</tr>|;
				&Do_SQL($sql_fix) if ($in{'process'} eq 'commit');
			}

			if($recs2 > 1 and $rec->{'Diference'} > 0){
				$easy_fix++;
				$sql_fix = "UPDATE sl_skus_cost SET Quantity=(Quantity+ABS($rec->{'Diference'})) WHERE ID_skus_cost='$first_id' LIMIT 1;";
				print qq|
					<tr>
						<td align="right" colspan="9" style="background-color:#26FF26">$sql_fix</td>
					</tr>|;
				&Do_SQL($sql_fix) if ($in{'process'} eq 'commit');

			}

			## Diferencias Negativas
			if ($recs2 == 1 and $rec->{'Diference'} < 0){
				$easy_fix++;
				$sql_fix = "UPDATE sl_skus_cost SET Quantity=(Quantity-ABS($rec->{'Diference'})) WHERE ID_skus_cost='$last_id' LIMIT 1;";
				print qq|
					<tr>
						<td align="right" colspan="9" style="background-color:#26FFFF">$sql_fix</td>
					</tr>|;
				&Do_SQL($sql_fix) if ($in{'process'} eq 'commit');
			}

			if ($recs2 > 1 and $rec->{'Diference'} < 0){
				my $sth3 = &Do_SQL("SELECT 
					sl_skus_cost.ID_skus_cost
					, sl_skus_cost.Tblname
					, sl_skus_cost.ID_warehouses
					, sl_skus_cost.ID_products
					, sl_skus_cost.Quantity
					, sl_skus_cost.Cost
					, sl_skus_cost.Date
					, sl_skus_cost.Time
				FROM sl_skus_cost 
				WHERE 1
				AND sl_skus_cost.ID_warehouses='$rec->{'ID_warehouses'}'
				AND sl_skus_cost.ID_products='$rec->{'ID_products'}'
				AND sl_skus_cost.Cost IS NOT NULL
				AND sl_skus_cost.Cost > 0
				ORDER BY sl_skus_cost.Quantity DESC");
				my $jumper=0;
				my $dif=abs($rec->{'Diference'});
				# Buscar si hay uno con la cantidad >= a la diferencia
				while (my $rec3 = $sth3->fetchrow_hashref()){
					if (!$jumper){
						if ($rec3->{'Quantity'} == abs($rec->{'Diference'}) ){
							# Si hay y es igual se elimina el registro
							$jumper=1;
							$easy_fix++;
							$sql_fix = "DELETE FROM sl_skus_cost WHERE ID_skus_cost='$rec3->{'ID_skus_cost'}' LIMIT 1;";
							print qq|
								<tr>
									<td align="right" colspan="9" style="background-color:#26FFFF">$sql_fix</td>
								</tr>|;
							&Do_SQL($sql_fix) if ($in{'process'} eq 'commit');
						}elsif ($rec3->{'Quantity'} > abs($rec->{'Diference'}) ){
							# Si hay y es mayor a ese se le descuenta la diferecia
							$jumper=1;
							$easy_fix++;
							$sql_fix = "UPDATE sl_skus_cost SET Quantity=(Quantity-ABS($rec->{'Diference'})) WHERE ID_skus_cost='$rec3->{'ID_skus_cost'}' LIMIT 1;";
							print qq|
								<tr>
									<td align="right" colspan="9" style="background-color:#26FFFF">$sql_fix</td>
								</tr>|;
							&Do_SQL($sql_fix) if ($in{'process'} eq 'commit');
						}
					}

				}
				
				#  - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
				#  - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
				# Si aun con el de arriba no se corrigio se procede a hacer un descuento a la malagueña
				# Se iran descontando en cada registro recorrido hasta lograr descontar el total
				#  - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
				#  - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

				if (!$jumper){
					$sql_fix = "NEXT";
					print qq|
						<tr>
							<td align="right" colspan="9" style="background-color:#26FFFF">$sql_fix</td>
						</tr>|;

					my $sth3 = &Do_SQL("SELECT 
						sl_skus_cost.ID_skus_cost
						, sl_skus_cost.Tblname
						, sl_skus_cost.ID_warehouses
						, sl_skus_cost.ID_products
						, sl_skus_cost.Quantity
						, sl_skus_cost.Cost
						, sl_skus_cost.Date
						, sl_skus_cost.Time
					FROM sl_skus_cost 
					WHERE 1
					AND sl_skus_cost.ID_warehouses='$rec->{'ID_warehouses'}'
					AND sl_skus_cost.ID_products='$rec->{'ID_products'}'
					AND sl_skus_cost.Cost IS NOT NULL
					AND sl_skus_cost.Cost > 0
					ORDER BY sl_skus_cost.Quantity DESC");
					my $dif=abs($rec->{'Diference'});
					# Buscar si hay uno con la cantidad >= a la diferencia
					while (my $rec3 = $sth3->fetchrow_hashref()){
						if ($dif > 0){
							if ($rec3->{'Quantity'} >  $dif){
								# Si hay y es mayor a ese se le descuenta la diferecia
								$sql_fix = "/*$dif MAGIC $rec3->{'Quantity'}*/ UPDATE sl_skus_cost SET Quantity=(Quantity-$dif) WHERE ID_skus_cost='$rec3->{'ID_skus_cost'}' LIMIT 1;";
								print qq|
									<tr>
										<td align="right" colspan="9" style="background-color:#26FFFF">$sql_fix</td>
									</tr>|;
								&Do_SQL($sql_fix) if ($in{'process'} eq 'commit');
							}else{
								# Si hay y es igual se elimina el registro
								$sql_fix = "/*$dif MAGIC $rec3->{'Quantity'}*/ DELETE FROM sl_skus_cost WHERE ID_skus_cost='$rec3->{'ID_skus_cost'}' LIMIT 1;";
								print qq|
									<tr>
										<td align="right" colspan="9" style="background-color:#26FFFF">$sql_fix</td>
									</tr>|;
								&Do_SQL($sql_fix) if ($in{'process'} eq 'commit');
							}

							$easy_fix++;
							$dif -= $rec3->{'Quantity'};
						}
					}
				}
			}

			## Con costo Calculado
			if (!$rec->{'sc_ID_warehouses'}){
				my $cost = &load_sltvcost($rec->{'ID_products'});
				if ($cost > 0){
					$easy_fix++;
					$sql_fix = "INSERT INTO sl_skus_cost SET ID_products='$rec->{'ID_products'}', ID_warehouses='$rec->{'ID_warehouses'}', Tblname='sl_manifests', Quantity=ABS($rec->{'Diference'}), Cost='$cost', Date=CURDATE(), Time=CURTIME(), ID_admin_users='1';";
					print qq|
						<tr>
							<td align="right" colspan="9" style="background-color:#9BE6BB">$sql_fix</td>
						</tr>|;
					&Do_SQL($sql_fix) if ($in{'process'} eq 'commit');
				}else{
					$sql_fix = "DIFICIL";
					$hard_fix++;
					print qq|
						<tr>
							<td align="right" colspan="9" style="background-color:#9BE6BB">$sql_fix</td>
						</tr>|;
				}
			}

			print qq|
						</table>
					</td>
				</tr>|;
		}

		# No tenemos porque tener Qty Negativos en sl_warehouses_location
		# Negativo encontrado, Negativo eliminado
		if ($rec->{'Quantity'} <= 0) {
			$neg_fix++;
				print qq|<tr><td colspan="10"><table border="1" cellpadding="5" cellspacing="0" width="100%" style="font-size:12px; border: 1px solid #222222;">|;
				
				$sql_fix = "/*CLEAN*/ DELETE FROM sl_warehouses_location WHERE ID_warehouses='$rec->{'ID_warehouses'}' AND ID_products='$rec->{'ID_products'}';";
				print qq|	<tr>
								<td>$sql_fix</td>
							</tr>|;
				&Do_SQL($sql_fix) if ($in{'process'} eq 'commit');
				
				$sql_fix = "/*CLEAN*/ DELETE FROM sl_skus_cost WHERE ID_warehouses='$rec->{'ID_warehouses'}' AND ID_products='$rec->{'ID_products'}';";
				print qq|	<tr>
								<td>$sql_fix</td>
							</tr>|;
				&Do_SQL($sql_fix) if ($in{'process'} eq 'commit');

				print qq|</td></tr></table>|;
		}
	}
	
	print qq|</table>|;
	print qq|<br>Registros encontrados: $recs|;
	print qq|<br>Diferencias detectadas: $recs_dif|;
	print qq|<br>Facilmente corregidos: $easy_fix|;
	print qq|<br>Casos donde se requiere el costo: $hard_fix|;
	print qq|<br>Casos de cantidad negativas: $hard_fix_quantity|;
	print qq|<br>Casos de cantidad negativas y en cero eliminados: $neg_fix|;

	#|<----------------------------------------------------------------------------------------
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

sub validate_state_zipcode{
	my ($orig_zipcode,$orig_state) = @_;
	&Do_SQL("SET NAMES utf8");
	$sql = "SELECT ZipCode, StateFullName FROM sl_zipcodes WHERE Status='Active' AND zipcode='$orig_zipcode' AND StateFullName='$orig_state' GROUP BY ZipCode, StateFullName";
	my $sth = &Do_SQL($sql);
	my ($zipcode,$state) = $sth->fetchrow_array();

	if ( lc($state) eq lc($orig_state) ){
		return 0;
	}else{
		return "BD=$state != LO=$orig_state";
	}
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

sub print_query{
	my ($sql) = @_;
	print qq|<div style="border:solid 1px #666;padding:3px;"><span style="font-size:10px;color:#0099FF;">$sql</span></div>|;
}