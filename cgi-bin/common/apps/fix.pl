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

local (%in) = &parse_form;
local ($dir) = getcwd;
local ($usr{'id_admin_users'}) = 1;
local ($cfg{'id_warehouses'}) = 1001;
local ($cfg{'reset'}) = 1;


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

sub main {

	$|++;
	&load_settings;
	&connect_db;
	&fix_by_operations;
	&disconnect_db;

}


sub fix_by_operations{
	
	print "Content-type: text/html\n\n";
	print "repartir";
}



sub help_fix {
	use Data::Dumper;
	my $date = "2015-10-31";
	my $desde = "129532";
	&Do_SQL("set \@fecha='$date';");
	&Do_SQL("set \@desde=$desde;");
	my $q = "select * from sl_skus_trans where date > \@fecha and ID_products_trans >= \@desde;";
	my $sth = &Do_SQL($q);
	print "Content-type: text/html\n\n";
	print q|<table border="1" style="border-collapse:collapse;font-size:12px;font-family:consolas">
	<thead>
		<tr>
			<th>ID products</th>
			<th>Warehouses</th>
			<th>Location</th>
			<th>Type Trans</th>
			<th>Quantity</th>
			<th>Left Quantity</th>
			<th>Left Quantity Total</th>
			<th>Avg</th>
			<th>Operation</th>
		</tr>
	</thead>
	<tbody>|;
	while(my $row = $sth->fetchrow_hashref){
		print '<tr>';
		print "<td>$row->{'ID_products'}</td>";
		print "<td>$row->{'ID_warehouses'}</td>";
		print "<td>$row->{'Location'}</td>";
		print "<td>$row->{'Type_trans'}</td>";
		print "<td>$row->{'Quantity'}</td>";
		print "<td>$row->{'left_quantity'}</td>";
		print "<td>$row->{'left_quantity_total'}</td>";
		print "<td>$row->{'Cost_Avg'}</td>";
		print "<td>$row->{'tbl_name'}</td>";
		my %conversor = {
			"sl_manifests", "sl_manifests_items",
			"sl_purchaseorders", "sl_purchaseorders_items",
			"sl_orders", "sl_orders_products",
			"sl_skustransfers", "sl_skustransfers_items"
		};
		$row->{'tbl_name'} eq 'sl_manifests' and $table = 'sl_manifests_items';
		$row->{'tbl_name'} eq 'sl_purchaseorders' and $table = 'sl_purchaseorders_items';
		$row->{'tbl_name'} eq 'sl_skustransfers' and $table = 'sl_skustransfers_items';
		$row->{'tbl_name'} eq 'sl_orders' and $table = 'sl_orders_products';
		$field = $row->{'tbl_name'};
		$field =~ s/sl_/ID_/;
		$query2 = "select * from $table where $field=$row->{'ID_trs'}";
		my $rs = &Do_SQL($query2);
		print 	q|<td><table border="1" style="border-collapse:collapse"><thead></thead><tbody>|;
		while( my $r = $rs->fetchrow_hashref){
			print '<tr>';
			print "<td>$r->{'ID_products'}</td>";
			print "<td>$r->{'Qty'}</td>";
			print '</tr>';
		}
		print '</tbody></table></td>';
		print '</tr>';
	}
	print "</tbody></table>";
}
sub fix_by_product{
	use Data::Dumper;
	my $date = "2015-10-31";
	my $desde = "129532";
	&Do_SQL("set \@fecha='$date';");
	&Do_SQL("set \@desde=$desde;");
	my $q = "select distinct ID_products from sl_skus_trans where date > \@fecha and ID_products_trans >= \@desde;";
	my ($listProducts) = &Do_SQL($q);
	print "Content-type: text/html\n\n";
	my $br = "<br>";
	while( my $product = $listProducts->fetchrow_hashref ){
		print '<hr>';
		print "<h3>Producto $product->{'ID_products'}</h3>";
		&Do_SQL("set \@producto = $product->{'ID_products'};");
		$queryGetLinesTrans ="
		select 
			a.ID_warehouses,
			a.Location,
			a.`Type`,
			a.Quantity,
			a.left_quantity,
			a.left_quantity_total,
			a.Cost_Avg,
			a.tbl_name,
			a.ID_products,
			a.ID_products_trans,
			a.ID_trs,
			a.date,
			a.Type_trans
		from 
			sl_skus_trans a 
		where 
			a.date > \@fecha and
 			ID_products = \@producto and
 			ID_products_trans > \@desde
		order by a.ID_products_trans asc;";
		my ($rs) = &Do_SQL($queryGetLinesTrans);
		print q|<table border="1" style="border-collapse:collapse;font-size:12px;font-family:consolas">
			<thead>
				<tr>
					<th>ID Skus Trans</th>
					<th>Warehouses</th>
					<th>Location</th>
					<th>Type Trans</th>
					<th>Type</th>
					<th>Quantity</th>
					<th>Left Quantity</th>
					<th>Left Quantity Total</th>
					<th>Avg</th>
					<th>Date</th>
				</tr>
			</thead>
			<tbody>|;

		my $totalUltimo = 0;
		my $id_products_trans = 0;
		while (my $r = $rs->fetchrow_hashref ) {
			print "<tr>";
			print "<td>$r->{'ID_products_trans'}</td>";
			print "<td>$r->{'ID_warehouses'}</td>";
			print "<td>$r->{'Location'}</td>";
			print "<td>$r->{'tbl_name'}</td>";
			print "<td>$r->{'Type'}</td>";
			print "<td>$r->{'Quantity'}</td>";
			print "<td>$r->{'left_quantity'}</td>";
			print "<td>$r->{'left_quantity_total'}</td>";
			print "<td>$r->{'Cost_Avg'}</td>";
			print "<td>$r->{'date'}</td>";
			print "</tr>";
			$totalUltimo = $r->{'left_quantity_total'};
			$id_products_trans = $r->{'ID_products_trans'};
		}
		print q|</tbody></table>|;
		print $br;
		print q|<table border="1" style="border-collapse:collapse;font-size:12px;font-family:consolas; float:left;">|;
		print "<tr>";
		print "<th>Warehouse</th>";
		print "<th>Quantity (Warehouses Location)</th>";
		print "<th>Quantity (Skus_trans)</th>";
		print "</tr>";
		$queryWH = "select 
			ID_warehouses,
			Location,
			sum(Quantity) Quantity
		from 
			sl_warehouses_location 
		where 
			ID_products=\@producto
		group by ID_warehouses";
		my ($r) = &Do_SQL($queryWH);
		my $total = 0;
		while ( my $f = $r->fetchrow_hashref) {
			$qq = &Do_SQL("select left_quantity 
			from 
				sl_skus_trans 
			where 
			--	date> \@fecha and
				ID_products = \@producto and 
				ID_warehouses = $f->{'ID_warehouses'}
			order by ID_products_trans desc
			limit 1;")->fetchrow;
			print "<tr>";
			print "<td>$f->{'ID_warehouses'}</td>";
			$as = abs($f->{'Quantity'} - $qq) > 0 ? q|style="background:red;color:white;"| : '';
			print "<td $as>$f->{'Quantity'}</td>";
			print "<td>$qq</td>";
			print "</tr>";
			$total+=$f->{'Quantity'};
		}
		print "<tr>";
		print "<td>Quantity Total (sl_warehouses_location)</td>";
		print "<td>$total</td>";
		print "</tr>";
		print "</table>";


		print q|<table border="1" style="border-collapse:collapse;font-size:12px;font-family:consolas; float:left; margin-left : 10%">|;
		print "<tr>";
		print "<th>Warehouse</th>";
		print "<th>Quantity</th>";
		print "<th>Cost</th>";
		print "<th>Date</th>";
		print "</tr>";
		$queryWH = "select * from sl_skus_cost where id_products = \@producto and Date >\@fecha order by ID_skus_cost desc;";
		my ($r) = &Do_SQL($queryWH);
		my $total2 = 0;
		while ( my $f = $r->fetchrow_hashref) {
			print "<tr>";
			print "<td>$f->{'ID_warehouses'}</td>";
			print "<td>$f->{'Quantity'}</td>";
			print "<td>$f->{'Cost'}</td>";
			print "<td>$f->{'Date'}</td>";
			print "</tr>";
			$total2+=$f->{'Quantity'};
		}
		print "</table>";
		print $br;
		print q|<div style="clear:both"|;
		print $br;
		print $br;
		my $inf = 0;
		if( abs($totalUltimo - $total) > 0){
			print q|<span style="color:red">Left Quantity Total Diferencia: |.($total - $totalUltimo).q|</span>|.$br;
			$inf = 1;
		}
		if($inf == 1){
			&Do_SQL('START TRANSACTION');
			print "Querys para Corregir Left Quantity Total y left_quantity:".$br;
			print q|<ul style="font-family: consolas;font-size: 15px;margin-left: 4px;list-style:none">|;
			$_query = "update sl_skus_trans set left_quantity_total = $total where id_products_trans = $id_products_trans";
			print "<li>$q</li>";
			&Do_SQL($_query);
			$queryLeftCorrect = "select ID_warehouses,(select ID_products_trans from sl_skus_trans where id_products = \@producto and id_warehouses =a.ID_warehouses order by ID_products_trans desc limit 1) ID_products_trans from sl_skus_trans a where id_products = \@producto and date > \@fecha and id_products_trans > \@desde group by ID_warehouses;";
			$sth = &Do_SQL($queryLeftCorrect);
			my %warehouses_quantity = ();

			while($r = $sth->fetchrow_hashref){
				$whq = &Do_SQL("select 
					sum(Quantity)
				from 
					sl_warehouses_location 
				where 
					ID_products=\@producto and 
					ID_warehouses=$r->{'ID_warehouses'} 
				group by ID_warehouses")->fetchrow;
				$whq = $whq ? $whq : 0;
				print "<li>update sl_skus_trans set left_quantity = $whq where id_products_trans = $r->{'ID_products_trans'}</li>";
				$_query = "update sl_skus_trans set left_quantity = $whq where id_products_trans = $r->{'ID_products_trans'}";
				&Do_SQL($_query);
				$warehouses_quantity{ $r->{'ID_warehouses'} } = $whq;
				# push @warehouses_quantity, \%warehouse_quantity;
			}
			print "<li>-------------------------------------------------</li>";
			$queryGetLinesTrans =~ s/asc/desc/g;
			my ($rs) = &Do_SQL($queryGetLinesTrans);
			my $total_tmp = $total;
			$warehouses_quantity;
			$tmp = $rs->fetchrow_hashref;
			$operation = $tmp->{'Type_trans'};
			$id_warehouse_anterior = $tmp->{'ID_warehouses'};
			while ($r1 = $rs->fetchrow_hashref) {
				if($operation eq 'OUT'){
					$total_tmp += $r1->{'Quantity'};
					$warehouses_quantity{$id_warehouse_anterior} += $r1->{'Quantity'};
					$id_warehouse_anterior = $r1->{'ID_warehouses'};
					$operation = $r1->{'Type_trans'};
					$_query = "update sl_skus_trans set left_quantity=$warehouses_quantity{$r1->{'ID_warehouses'}}, left_quantity_total=$total_tmp where ID_products_trans = $r1->{'ID_products_trans'}";
					print "<li>update sl_skus_trans set left_quantity=$warehouses_quantity{$r1->{'ID_warehouses'}}, left_quantity_total=$total_tmp where ID_products_trans = $r1->{'ID_products_trans'}</li>";
				}elsif($operation eq 'IN'){
					$total_tmp -= $r1->{'Quantity'};
					$warehouses_quantity{$id_warehouse_anterior} -= $r1->{'Quantity'};
					$id_warehouse_anterior = $r1->{'ID_warehouses'};
					$operation = $r1->{'Type_trans'};
					$_query = "update sl_skus_trans set left_quantity=$warehouses_quantity{$r1->{'ID_warehouses'}}, left_quantity_total=$total_tmp where ID_products_trans = $r1->{'ID_products_trans'}";
					print "<li>update sl_skus_trans set left_quantity=$warehouses_quantity{$r1->{'ID_warehouses'}}, left_quantity_total=$total_tmp where ID_products_trans = $r1->{'ID_products_trans'}</li>";
				}
				&Do_SQL($_query);
			}
			# $total Left quantity Total final obtenido de whl
			# @warehouses_quatity left_quantity final por warehouse obtenido de whl

			print "</ul>";

			$queryGetLinesTrans ="
			select 
				a.ID_warehouses,
				a.Location,
				a.`Type`,
				a.Quantity,
				a.left_quantity,
				a.left_quantity_total,
				a.Cost_Avg,
				a.tbl_name,
				a.ID_products,
				a.ID_products_trans,
				a.ID_trs,
				a.date,
				a.Type_trans
			from 
				sl_skus_trans a 
			where 
				a.date > \@fecha and
	 			ID_products = \@producto and
	 			ID_products_trans > \@desde
			order by a.ID_products_trans asc;";
			my ($rs) = &Do_SQL($queryGetLinesTrans);
			print q|<table border="1" style="border-collapse:collapse;font-size:12px;font-family:consolas">
				<thead>
					<tr>
						<th>ID Skus Trans</th>
						<th>Warehouses</th>
						<th>Location</th>
						<th>Type Trans</th>
						<th>Type</th>
						<th>Quantity</th>
						<th>Left Quantity</th>
						<th>Left Quantity Total</th>
						<th>Avg</th>
						<th>Date</th>
					</tr>
				</thead>
				<tbody>|;

			my $totalUltimo = 0;
			my $id_products_trans = 0;
			while (my $r = $rs->fetchrow_hashref ) {
				print "<tr>";
				print "<td>$r->{'ID_products_trans'}</td>";
				print "<td>$r->{'ID_warehouses'}</td>";
				print "<td>$r->{'Location'}</td>";
				print "<td>$r->{'tbl_name'}</td>";
				print "<td>$r->{'Type'}</td>";
				print "<td>$r->{'Quantity'}</td>";
				print "<td>$r->{'left_quantity'}</td>";
				print "<td>$r->{'left_quantity_total'}</td>";
				print "<td>$r->{'Cost_Avg'}</td>";
				print "<td>$r->{'date'}</td>";
				print "</tr>";
				$totalUltimo = $r->{'left_quantity_total'};
				$id_products_trans = $r->{'ID_products_trans'};
			}
			print q|</tbody></table>|;
			print $br;
			if($in{'db'} and $in{'db'} eq 'commit'){
				&Do_SQL('COMMIT;');
			}else{
				&Do_SQL('ROLLBACK;');
			}
		}





		# print q|<span style="color:red">Left Quantity Total Diferencia: |.($total - $totalUltimo).q|</span>|;
	}
}

# 'Quantity' => '5',
# 'Type_trans' => undef,
# 'left_quantity' => '0',
# 'Type' => 'Sale',
# 'tbl_name' => 'sl_orders',
# 'Location' => 'PACK',
# 'ID_warehouses' => '1076',
# 'Time' => '10:47:10',
# 'Date' => '2013-05-17',
# 'Cost_Add' => '0.00',
# 'ID_trs' => '100008',
# 'ID_customs_info' => undef,
# 'Cost_Adj' => '0.000',
# 'left_quantity_total' => '0',
# 'ID_products' => '400001181',
# 'Cost_Avg' => '0.000',
# 'ID_admin_users' => '3020',
# 'Cost' => '0.000',
# 'SerialNum' => undef,
# 'ID_products_trans' => '17'

# sub fix_inventory {

# 	use Data::Dumper;
# 	my $date = '2015-11-02';
# 	my $query = "select * from sl_skus_trans where tbl_name ='sl_orders' and date = '$date' order by ID_products_trans asc";
# 	my ($sth) = &Do_SQL($query);

# 	my $aux =0;
# 	print "Content-type: text/html\n\n";
# 	print '<pre>';
# 	while (my ($row) = $sth->fetchrow_hashref() ) {
# 		my $field = 'ID_orders';
# 		$q = "select count(*) t from sl_orders_products where ID_products not like '6%' and ID_orders =$row->{'ID_trs'}";
# 		my ($prod_by_order) = &Do_SQL($q)->fetchrow();
# 		$q = "select count(*) t from sl_skus_trans where ID_trs = $row->{'ID_trs'} and tbl_name='sl_orders'";
# 		my ($lines_by_order) = &Do_SQL($q)->fetchrow();
# 		$q2 = "select Type from sl_warehouses where ID_warehouses=$row->{'ID_warehouses'}";
# 		$rs = &Do_SQL($q2)->fetchrow();
# 		print ' Productos por Order: ' .$prod_by_order. '<br>';
# 		print ' lineas de sku_trans: ' .$lines_by_order. '<br>';
# 		print "..............................<br>";
# 		print 'ID Product: '.$row->{'ID_products'}.'<br>';
# 		print 'Warehouse: '.$row->{'ID_warehouses'}.'<br>';
# 		print 'Type Warehouse: '.$rs.'<br>';
# 		print 'Location: '.$row->{'Location'}.'<br>';
# 		print 'Qty: '.$row->{'Quantity'}.'<br>';
# 		print 'Type: '.$row->{'Type_trans'}.'<br>';
# 		print 'Qty Total: '.$row->{'left_quantity_total'}.'<br>';
# 		print 'Costo Promedio: '.$row->{'Cost_Avg'}.'<br>';
# 		print "..............................<br>";
# 		if($row->{'Status'} == 'Processed'){
# 			print  $row->{'Ptype'}.'<br>';
# 			if( ($prod_by_order * 2) !=  $lines_by_order){
# 				$query = "select StatusPrd from sl_orders where ID_orders=$row->{'ID_trs'}";
# 				$rr = &Do_SQL($query)->fetchrow();
# 				if($rr ne 'For Re-Ship'){
# 					print '<p style="color:red">'.$row->{'ID_trs'}.'</p>';
# 					$aux++;
# 				}
# 			}
# 		}else{
# 			print  $row->{'Ptype'}.'<br>';
# 			if( ($prod_by_order * 3) !=  $lines_by_order){
# 				$query = "select StatusPrd from sl_orders where ID_orders=$row->{'ID_trs'}";
# 				$rr = &Do_SQL($query)->fetchrow();
# 				print $rr. '<br>';
# 				if($rr ne 'For Re-Ship'){
# 					print '<p style="color:red">'.$row->{'ID_trs'}.'</p>';
# 					$aux++;
# 				}
# 			}
# 		}
# 		print '----------------------------'.'<br>';

# 	}
# 	print '</pre>';
# }



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