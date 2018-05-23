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


local ($dir) = getcwd;
local(%in) = &parse_form;
# local ($in{'e'}) = 2;
local ($usr{'id_admin_users'}) = 1;


chdir($dir);

# Required Libraries
# --------------------------------------------------------
eval {
	require ('../subs/auth.cgi');
	require ('../subs/sub.base.html.cgi');
	require ('../subs/sub.func.html.cgi');
	require ("../subs/sub.acc_movements.html.cgi");
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
	&fix_inventory;
	&disconnect_db;

}


#############################################################################
#############################################################################
#   Function: fix_inventory
#
#       Es: Procesa archivo de bills para transicion
#       En: 
#
#    Created on: 29/07/2015  16:21:10
#
#    Author: Alejandro Diaz
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
sub fix_inventory {
#############################################################################
#############################################################################
	
	use File::Slurp;
	use MIME::Base64;

	print "Content-type: text/html\n\n";

	my $process = ($in{'process'} ne 'commit')? qq|<span style="color:#000;background-color:gray;padding:5px;">ANALYZING</span>|:qq|<span style="color:#FFF;background-color:red;padding:5px;">EXECUTING</span>|;
	$in{'id_adjustments'} = int($in{'id_adjustments'});
	$in{'id_warehouses'} = int($in{'id_warehouses'});
	$in{'e'} = int($in{'e'});

	if (!$in{'e'}){
		print "<h5>e requerido</h5>";
		return;
	}else{
		print qq|<h2>|.uc($cfg{'app_title'}).qq|<br>$process</h2>|;		
	}

	if (!$in{'id_adjustments'}){
		print "<h5>id_adjustments requerido</h5>";
		return;
	}else{
		print qq|<h4>ID_adjustments=$in{'id_adjustments'}</h4>|;		
	}

	if (!$in{'id_warehouses'}){
		print "<h5>id_warehouses requerido</h5>";
		return;
	}else{
		print qq|<h4>ID_warehouses=$in{'id_warehouses'}</h4>|;		
	}

	$sql = "SELECT
	sl_adjustments_items.ID_adjustments_items
	, sl_adjustments_items.ID_adjustments
	, sl_adjustments_items.ID_products
	, sl_adjustments_items.ID_warehouses AS Location
	-- , sl_adjustments_items.Location
	, ABS(sl_adjustments_items.Adj) AS Qty
	, ROUND(sl_adjustments_items.Price/ABS(sl_adjustments_items.Adj),2)Cost
	, sl_adjustments_items.Date
	, sl_adjustments_items.Time
	, sl_adjustments_items.ID_admin_users
	FROM sl_adjustments_items WHERE sl_adjustments_items.ID_adjustments='$in{'id_adjustments'}' AND sl_adjustments_items.Adj<0";
	my ($sth) = &Do_SQL($sql);
	# print $sql."<br>";
	# my $id_adjustments = $sth->{'mysql_insertid'};
	my $recs=0;
	while (my $rec = $sth->fetchrow_hashref()){
		$recs++;

		# Se graga con el usuario 9999 los datos sobrantes
		$sql = "INSERT INTO sl_warehouses_location (ID_warehouses, ID_products, Location, Quantity, Date, Time, ID_admin_users) 
		VALUES ('$in{'id_warehouses'}', '$rec->{'ID_products'}', '$rec->{'Location'}', '$rec->{'Qty'}', CURDATE(), CURTIME(), 9999);";

		print qq|<span style="font-size:12;color:#FF7A24;">$sql</span><br>|;
		&Do_SQL($sql) if ($in{'process'} eq "commit");

		$sql = "INSERT INTO sl_skus_cost (ID_products, ID_purchaseorders, ID_warehouses, Tblname, Quantity, Cost, Date, Time, ID_admin_users) 
		VALUES ('$rec->{'ID_products'}', '$rec->{'ID_adjustments'}', '$in{'id_warehouses'}', 'sl_adjustments', '$rec->{'Qty'}', '$rec->{'Cost'}', CURDATE(), CURTIME(), 9999);";

		print qq|<span style="font-size:12;color:#924BFF;">$sql</span><br>|;
		&Do_SQL($sql) if ($in{'process'} eq "commit");

	}

	print qq|<h4>$recs Registros agregados.</h4>|;		



### - AD - AD - AD - AD - AD - AD - AD - AD - AD - AD - AD - AD - AD - AD - AD
return;

	my $inbound_file_path = $cfg{'path_upfiles'} . 'e'.$in{'e'} . '/';
	my $executed_file_path = $inbound_file_path;

	print "Leyendo archivos en ruta: " . $inbound_file_path . "\n";
	opendir (CMDIR, $inbound_file_path) || &cgierr('Unable to open directory ' . $inbound_file_path ,704,$!);
	@files = readdir(CMDIR);# Read in list of files in directory..
	closedir (CMDIR);


	##### Looping files A2BF_Shipments_20150515120126.txt
	FILE: foreach my $file_name (sort @files) {

		next if ($file_name =~ /^\./);		# Skip "." and ".." entries..
		next if ($file_name =~ /^index/);		# Skip index.htm type files..

		next if ($file_name !~ /^ajuste_e2_\d{8}.csv$/);# Skip
		print "Archivo encontrado: " . $file_name  . "\n";
		print "Intentando abrir el archivo " . $inbound_file_path . $file_name  . "\n";

		if (-e  $inbound_file_path . $file_name) {

			open(my $this_file, "<", $inbound_file_path . $file_name) or &cgierr('Unable to open file: '. $inbound_file_path . $file_name, 601,$!);
			print "Ejecutando ordenes en el archivo...\n\n";
			my @ary_warehouses;
			my %these_wh;
			##### Open File
			my $i=0;

			LINE: while (<$this_file>) {

				$line = $_;
				$line =~ s/\r|\n|//g;
				#print "$i - $line\n";

				my @line_data = split(/,/);
				#print "Linea tiene " . scalar @line_data . " Elementos\n\n";

				for (0..$#line_data) {

					my $j = $_;
					$line_data[$j] =~ s/\r|\n|\t|\"//g;
					$line_data[$j] =~ s/^\s+//;
					$line_data[$j] =~ s/\s+$//;

			
					#####
					##### 1er Linea (ID de Almacen)
					#####
					if($i == 0 ){

						#####
						##### Existe almacen y es virtual?
						#####
						my ($sth) = &Do_SQL("SELECT COUNT(*) FROM sl_warehouses WHERE ID_warehouses = '". $line_data[$j] ."' AND Type = 'Virtual' AND Status  = 'Active';");
						my ($is_virtual) = $sth->fetchrow();

						### Si no es virtual, no se puede procesar su informacion?
						#$line_data[$_] = 0 if $!is_virtual;

						push(@ary_warehouses, $line_data[$j]);

					}else{

						#####
						##### Lineas consecutivas
						#####
						my $id_orders = int($line_data[$j]);
						$these_wh{$ary_warehouses[$j]} .= $id_orders . ',' if $id_orders;

					}

				} ## for line

				++$i;

			} ## while line

			print "Finalizado leida de elementos en el archivo...\nSe encontraron ". scalar @ary_warehouses ." Almacenes en el archivo\n\n";
			print "Ordenes en cada Almacen:\n";

			&Do_SQL("START TRANSACTION");

			my @ary_sorted = sort {$a <=> $b} @ary_warehouses;
			my $recs=0;
			for(0..$#ary_sorted){
				$recs++;

				#######
				####### Iteracion Elementos del arreglo
				#######
				my $this_line = $_ + 1;
				chop($these_wh{$ary_sorted[$_]});
				
				# print $this_line . '. Almacen ' . $ary_sorted[$_] . ' = ' . $these_wh{$ary_sorted[$_]} . "\n\n" ;

				### Genera Ajuste
				$sql = "INSERT INTO sl_adjustments (Title, Comments, AuthBy, AuthDate, Status, Date, Time, ID_admin_users) VALUES ('Ajuste de Almacen COD $ary_sorted[$_]', 'Ajuste de Inventario para corregir mercancia en transito.', 0, '0000-00-00', 'New', CURDATE(), CURTIME(), 1);";
				my ($sth) = &Do_SQL($sql);
				my $id_adjustments = $sth->{'mysql_insertid'};
				
				print "\n".$this_line . '. ID warehouses->' . $ary_sorted[$_]." ID adjustments->".$id_adjustments."\n";

				$sql = "SELECT
				(400000000+sl_parts.ID_parts)SKU 
				/*(400000000+sl_orders_parts.ID_parts)SKU*/
				, sl_parts.Model
				, sl_parts.Name
				, SUM(Qty * Quantity) AS Quantity
				 /*, sum(sl_orders_parts.Quantity)Quantity*/
				, '$ary_sorted[$_]'ID_warehouses
				, (SELECT sl_locations.Code FROM sl_locations WHERE sl_locations.ID_warehouses='$ary_sorted[$_]' AND sl_locations.Status='Active' LIMIT 1)Location
				FROM sl_orders_products
				INNER JOIN sl_orders ON sl_orders_products.ID_orders=sl_orders.ID_orders
				INNER JOIN sl_skus_parts ON ID_sku_products = ID_products
				INNER JOIN sl_parts USING(ID_parts)
				/*INNER JOIN sl_orders_parts ON sl_orders_products.ID_orders_products=sl_orders_parts.ID_orders_products*/
				/*INNER JOIN sl_parts ON sl_parts.ID_parts=sl_orders_parts.ID_parts*/
				WHERE sl_orders_products.ID_orders IN ($these_wh{$ary_sorted[$_]})
				AND sl_orders.Ptype='COD'
				AND sl_orders.status='Processed' 
				AND sl_orders_products.ID_products < 600000000
				AND sl_orders_products.Status='Active'
				GROUP BY sl_parts.ID_parts
				/*GROUP BY sl_orders_parts.ID_parts*/
				";
				my ($sth) = &Do_SQL($sql);
				my $id_products_adj='';
				while(my $rec = $sth->fetchrow_hashref()){
					$id_products_adj .= $rec->{'SKU'}.',';
					# print " WH->".$rec->{'ID_warehouses'}." SKU->".$rec->{'SKU'}." Qty->".$rec->{'Quantity'}."\n";


					# Se graba con el usuario 1 los datos proporcionados
					$sql = "INSERT INTO sl_adjustments_items (ID_adjustments, ID_products, ID_warehouses, Location, Qty, Adj, Price, Date, Time, ID_admin_users) 
					VALUES ('$id_adjustments', '$rec->{'SKU'}', '$rec->{'ID_warehouses'}', '$rec->{'Location'}', '$rec->{'Quantity'}', 0, 0, CURDATE(), CURTIME(), 1);";
					&Do_SQL($sql);

					if ($rec->{'Location'} eq ''){
						print "\n>>>>FAIL Not location found in warehouse $rec->{'ID_warehouses'}.<<<<\n"
					}


				}
				chop($id_products_adj);

				### Buscar productos que no envien para ajustar pero que si existan en el almacen
				# Se graga con el usuario 9999 los datos sobrantes
				$sql = "SELECT ID_warehouses, Location, ID_products SKU, SUM(Quantity)Quantity FROM sl_warehouses_location WHERE sl_warehouses_location.ID_warehouses='$ary_sorted[$_]' AND ID_products NOT IN ($id_products_adj) GROUP BY ID_warehouses, Location, ID_products";
				$sth = &Do_SQL($sql);
				while(my $rec = $sth->fetchrow_hashref()){
					$sql = "INSERT INTO sl_adjustments_items (ID_adjustments, ID_products, ID_warehouses, Location, Qty, Adj, Price, Date, Time, ID_admin_users) 
					VALUES ('$id_adjustments', '$rec->{'SKU'}', '$rec->{'ID_warehouses'}', '$rec->{'Location'}', '0', 0, 0, CURDATE(), CURTIME(), 9999);";
					&Do_SQL($sql);

				}

			}

			&Do_SQL("COMMIT");
			print "\nDone...\n";


		} ## existe el archivo

	} ## each file

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