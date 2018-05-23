#!/usr/bin/perl
#######################################################################
#######################################################################
#######################################################################

# $in{'e'}
# $in{'id_warehouses'}
# $in{'list_orders'}
# $in{'st_shpdate'}
# $in{'process'} eq 'commit' ejecuta el proceso 
# $in{'mc'} = 1 ejecuta contabilidad del inventario
# $in{'mc'} = 2 ejecuta contabilidad completa (inventario + venta)
# $in{'mc'} = 3 ejecuta contabilidad de la venta

use DBI;
use DBIx::Connector;
use DBD::mysql;

# Load the form information and set the config file and userid.
local(%in) = &parse_form;
local(%config, %cfg, %usr);

# Required Libraries
# --------------------------------------------------------
eval {
	require ("../subs/auth.cgi");
	require ("../subs/sub.base.html.cgi");
};

if ($@) { &cgierr ("Error loading required Libraries",300,$@); }

eval { &main; };
if ($@) { &cgierr("Fatal error, 301, $@"); }

exit;

sub main {	
	$|++;
	print "Content-type: text/html\n\n";
	
	&load_settings;

	$sys{'fmt_curr_decimal_digits'} = 2 if(!$sys{'fmt_curr_decimal_digits'});

	print "<h3 align=center>DIREKSYS($in{'e'}) $cfg{'app_title'}</h3>";
	print "<h4 align=center>CORRECCION DE PEDIDOS CON ESCANEO INCOMPLETO EN PRODUCTO</h4>";
	print "<h4 align=center>Process: <strong>$in{'process'}</strong></h4>";

	# Numero de orden de cliente
	if (!$in{'e'}){
		print "<span style='color:red;'>NO SE ENVIO EL ID DE EMPRESA.</span><br>";
	}else{

		&connect_db;
		$in{'list_orders'} = int($in{'id_orders'}) if !$in{'list_orders'};

		my $touched = 0;
		my ($sth) = &Do_SQL("SELECT Ptype, Type, PostedDate FROM sl_orders INNER JOIN sl_customers USING(ID_customers) WHERE ID_orders = '$in{'list_orders'}';");
		my ($order_type, $ctype, $pdate) = $sth->fetchrow();

		
		print "<br><table width='100%' cellpadding='3' border='1' style='font-family:verdana;font-size:10px'>";
		print "<tr>";
		print "		<th>ID_orders</th>";
		print "		<th>ID_orders_products</th>";
		print "		<th>ID_products</th>";
		print "		<th>Cost</th>";
		print "		<th>New Cost</th>";
		print "		<th>ShpDate</th>";
		print "		<th>ID_parts</th>";
		print "		<th>Comments</th>";
		print "</tr>";

		my ($sth_prod);
		my $wholesale_order = &is_exportation_order($in{'list_orders'});

		if($wholesale_order){

			$sth_prod = &Do_SQL("SELECT 
									ID_orders
									, ID_orders_products
									, ID_products
									, Cost prod_cost
									, ShpDate AS prod_shpdate
									, Quantity AS prod_quantity
									,'->'
									, ID_parts AS ID_parts
									, (ID_parts + 400000000)AS SKU
									, SUM(Quantity)AS sku_quantity
									FROM sl_orders_products
									INNER JOIN sl_parts 
									ON (Related_ID_products - 400000000) = ID_parts
									WHERE ID_orders IN ($in{'list_orders'})
									AND sl_orders_products.ID_products < 600000000
									AND sl_orders_products.Status NOT IN('Order Cancelled','Inactive')
									GROUP BY ID_orders_products,ID_parts
									ORDER BY ID_orders_products, ID_parts;");


		}else{

			$sth_prod = &Do_SQL("SELECT 
									ID_orders
									, ID_orders_products
									, ID_products
									, Cost prod_cost
									, ShpDate AS prod_shpdate
									, Quantity AS prod_quantity
									,'->'
									, sl_skus_parts.ID_parts AS ID_parts
									, (sl_skus_parts.ID_parts + 400000000)AS SKU
									, SUM(sl_skus_parts.Qty)AS sku_quantity
									FROM sl_orders_products
									INNER JOIN sl_skus_parts ON ID_products = ID_sku_products
									WHERE ID_orders IN ($in{'list_orders'})
									AND sl_orders_products.ID_products < 600000000
									AND sl_orders_products.Status NOT IN('Order Cancelled','Inactive')
									GROUP BY ID_orders_products,ID_parts
									ORDER BY ID_orders_products, ID_parts;");

		}

		my $registros = 0;
		while($rec = $sth_prod->fetchrow_hashref()) {

			my $comments = '';
			my $id_orders = $rec->{'ID_orders'};
			my $id_orders_products = $rec->{'ID_orders_products'};
			my $id_products = $rec->{'ID_products'};
			my $sku = $rec->{'SKU'};
			my $id_parts = $rec->{'ID_parts'};			
			my $id_orders_parts = 0;
			my $prod_shpdate = $rec->{'prod_shpdate'};
			my $prod_cost = $rec->{'prod_cost'};
			my $sku_quantity = $rec->{'sku_quantity'};
			my $tracking = 'Local COD';
			my $trktype = '';
			my $cost_zero = ($prod_cost <= 0)? 1 : 0;
			my $new_cost = 0;
			my $this_record_touched = 0;

			$comments .= 'La linea NO tiene Cost='.$prod_cost.'<br>' if ($cost_zero);

			my ($sthc) = &Do_SQL("SELECT SUM(Quantity) FROM sl_orders_parts WHERE ID_orders_products = '$id_orders_products' AND ID_parts = '$id_parts';");
			my ($total_parts_sent) = $sthc->fetchrow();
			(!$total_parts_sent) and ($total_parts_sent = 0);

			$comments .= "SKU: $sku - A Enviar: $sku_quantity - Enviadas: $total_parts_sent<br>";

			while($total_parts_sent < $sku_quantity){

				$touched = 1;
				$this_record_touched = 1;
				my $this_quantity; my $this_cost;
				# Prioritario obtener el Costo
				my $new_cost = round(&load_sltvcost($sku),3);

				if($wholesale_order){

					$this_quantity = ($sku_quantity - $total_parts_sent);
					$total_parts_sent = $sku_quantity;
					#$this_cost = round($new_cost * $this_quantity,3);

				}else{

					++$total_parts_sent;
					$this_quantity = 1;
					#$this_cost = $new_cost;

				}
				
				# Si la linea tiene fecha de escaneo solo se crea el sl_orders_parts
				my $new_id_orders_parts;
				my $last_shpdate;

				my $sql = "/*UCost: $new_cost */ INSERT INTO sl_orders_parts SET
				ID_parts = '$id_parts'
				,  ID_orders_products = '$id_orders_products'
				,  Quantity = '$this_quantity'
				,  Cost = '$new_cost'
				,  ShpDate = '".$in{'set_shpdate'}."'
				,  Tracking = '$tracking'
				,  ShpProvider = ''
				,  Status = 'Shipped'
				,  Date = CURDATE()
				,  Time = CURTIME()
				,  ID_admin_users = 1";

				if ($in{'process'} eq 'commit'){

					my $sth2 = &Do_SQL($sql);
					$new_id_orders_parts = $sth2->{'mysql_insertid'};

				}

				$comments .= 'New ID_orders_parts = '.$new_id_orders_parts.'<br>';
				$comments .= $sql.'<br>';

			}

			if($this_record_touched){

				########
				######## Actualizacion campo Costo en sl_orders_products
				########
				my ($sthc) = &Do_SQL("SELECT SUM(Cost * Quantity), IF(ShpDate IS NULL,Date,ShpDate) FROM sl_orders_parts WHERE ID_orders_products = '$id_orders_products';");
				my ($new_pcost, $shpdate) = $sthc->fetchrow();

				$sql = "UPDATE sl_orders_products SET Cost = '$new_pcost', ShpDate = '$shpdate' WHERE ID_orders_products = '$id_orders_products';";
				&Do_SQL($sql) if ($in{'process'} eq 'commit' and $cost_zero);
				$comments .= 'Se actualiza Linea Cost ='.$new_pcost.' y ShpDate='.$shpdate.' de sl_orders_products'.'<br>';
				$comments .= $sql.'<br>';
				$new_cost = $new_pcost;


				if($in{'process'} eq 'commit' and $in{'mc'} =~ /1|2/){

					#########
					######### Contabilidad de Inventario?
					#########

					my $this_keypoint = $wholesale_order ? 'order_skus_inventoryout_' : 'order_products_inventoryout_';
					$this_keypoint .= $ctype .'_'. $order_type;
					@params = ($id_orders, $id_orders_products);
					&accounting_keypoints($this_keypoint, \@params );
					my $sqlf = "UPDATE sl_orders_products INNER JOIN sl_orders_parts USING(ID_orders_products) SET sl_orders_parts.Date = '".$in{'set_shpdate'}."' WHERE ID_orders = '$id_orders' AND TIMESTAMPDIFF(SECOND,CONCAT(sl_orders_parts.Date,' ',sl_orders_parts.TIME),NOW()) BETWEEN 0 AND 50;";
					&Do_SQL($sqlf);
					$comments .= $sqlf.'<br>';

					$comments .= 'Se inserta contabilidad de inventario con el keypoint = '. $this_keypoint .'<br>';

				}

			}

			print "<tr>";
			print "		<td>$id_orders &nbsp;</td>";
			print "		<td>$id_orders_products &nbsp;</td>";
			print "		<td>$id_products &nbsp;</td>";
			print "		<td>$prod_cost &nbsp;</td>";
			print "		<td>$new_cost &nbsp;</td>";
			print "		<td>$prod_shpdate &nbsp;</td>";
			print "		<td>$id_parts &nbsp;</td>";
			print "		<td>$comments &nbsp;</td>";
			print "</tr>";

		}

		print "</table><br>";
		# print "SE CREARON $registros PRODUCTOS<br>";
			
		my $fc;
		if($touched and $in{'process'} eq 'commit' and $in{'mc'} =~ /2|3/){

			#### Acounting Movements
			(!$pdate and $shpdate) and ($pdate = $shpdate) ;

			my @params = ($in{'list_orders'});
			my $this_keypoint = $wholesale_order ? 'order_skus_scanned_' : 'order_products_scanned_';
			$this_keypoint .= $ctype .'_'. $order_type;
			&accounting_keypoints($this_keypoint , \@params);
			$fc = 'Se inserta contabilidad de venta con el keypoint = '. $this_keypoint .'<br>';

		}
		&Do_SQL("UPDATE sl_movements SET EffDate = '$pdate' WHERE ID_tableused = '$in{'list_orders'}' AND EffDate = CURDATE();");

		my ($sthf) = &Do_SQL("SELECT SUM(Cost), ShpDate FROM sl_orders_products WHERE ID_orders = '$in{'list_orders'}' AND Status IN('Active','Returned');");
		my ($sumcost, $shpdate) = $sthf->fetchrow();
		print "<center><h1>Costo Final: $sumcost</h1><br><h2>$fc</h2></center>";

		&disconnect_db;

	}

}

######################################################### &process=commit&mc=2
##			Query				##
##########################################################
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

##################################################################
#     CGIERR   	#
##################################################################
sub cgierr {
# --------------------------------------------------------
# Last Modified on: 11/10/08 11:58:21
# Last Modified by: MCC C. Gabriel Varela S: Se corrige la forma de mostrar la fecha
	my (@sys_err) = @_;
	print "Content-type: text/html\n\n";

	my ($key,$env,$out_in,$out_env);
	if (!$cfg{'cd'}){
		print qq|
						<head>
										<title>CGI - ERROR</title>
						</head>					
						<body BGCOLOR="#FFFFFF" LINK="#FF0000" VLINK="#FF0000" ALINK="#FF0000">
					
							<table BORDER="0" WIDTH="500" CELLPADDING="10" CELLSPACING="10">
							  <tr>
							    <td BGCOLOR="#FF0000" colspan="2"><font size="5" color="#FFFFFF" face="Arial"><b>CGI-Error</b></font></td>
							  </tr>
							</table>
							<table BORDER="0" WIDTH="550" CELLPADDING="2" CELLSPACING="0">|;
								$sys_err[0]	and print "\n<tr>\n  <td valign='top' width='200'><font face='Arial' size='3'>Error Message</font></td>\n  <td><font face='Arial' size='3' color='#FF0000'><b>$sys_err[0]</b></font></td>\n</tr>\n";
								$sys_err[1]	and print "<tr>\n  <td width='200'><font face='Arial' size='2'>Error Code</font></td>\n  <td><font face='Arial' size='2'>$sys_err[1]</font></td>\n";
								$sys_err[2]	and print "<tr>\n  <td valign='top' width='200'><font face='Arial' size='2'>System Message</font></td>\n  <td><font face='Arial' size='2'>$sys_err[2]</font></td>\n";
								print qq|
							<tr>
							  <td colspan="2"><p>&nbsp</p><font face='Arial' size='2'>If the problem percist, please contact us with the above Information.</font><br>
									<font face='Arial' size='2'><a href="mailto:$systememail">$systememail</a></font></td>
							</tr>
							  </table>
						</body>
						</html>|;
		######################################
		### Save CGI ERR			
		##############################
		my ($ip);
		my (@outmsg) = @sys_err;
		my ($sec, $min, $hour, $day, $mon, $year, $dweek, $dyear, $daylight) = localtime(time());
		$year+=1900;
		$mon++;
		my ($time,$date) = ("$hour:$min:$sec","$mon-$day-$year");
		
		foreach $key (sort keys %in) {
			$outmsg[3] .= "$key=$in{$key},";
		}
		
		foreach $env (sort keys %ENV) {
			$outmsg[4] .= "$env=$ENV{$env},";
		}
		
		for (0..4){
			$outmsg[$_] =~ s/\n|\r/ /g;
			$outmsg[$_] =~ s/\|/ /g;
		}
		
		if ($ENV{'REMOTE_ADDR'}){
			$ip = $ENV{'REMOTE_ADDR'};
		}elsif ($ENV{'REMOTE_HOST'}){
			$ip = $ENV{'REMOTE_HOST'};
		}elsif ($ENV{'HTTP_CLIENT_IP'}){
			$ip = $ENV{'HTTP_CLIENT_IP'};
		}else{
			$ip = "Unknow";
		}
	
		(!$cfg{'cgierr_log_file'}) and ($cfg{'cgierr_log_file'} = './logs/cgierr.log');
		if (open (LOG, ">>$cfg{'cgierr_log_file'}")){;
			print LOG "$usr{'username'}|$outmsg[0]|$outmsg[1]|$outmsg[2]|$outmsg[3]|$outmsg[4]|$time|$date|$ip\n";
			close AUTH;
		}
	

	}else{
		print "<PRE>\n\nCGI ERROR\n==========================================\n";
					$sys_err[0]	and print "Error Message       : $sys_err[0]\n";
					$sys_err[1]	and print "Error Code          : $sys_err[1]\n";
					$sys_err[2]	and print "System Message      : $sys_err[2]\n";
					$0			and print "Script Location     : $0\n";
					$]			and print "Perl Version        : $]\n";
					$sid		and print "Session ID          : $sid\n";


		print "\nForm Variables IN\n-------------------------------------------\n";
		
		foreach $key (sort keys %in) {
			my $space = " " x (20 - length($key));
			$out_in .= "$key=$in{$key},";
			print "$key$space: $in{$key}\n";
		}
		
		print "\nForm Variables ERROR\n-------------------------------------------\n";
		foreach $key (sort keys %error) {
			my $space = " " x (20 - length($key));
			print "$key$space: $error{$key}\n";
		}
		
		print "\nEnvironment Variables\n-------------------------------------------\n";
		foreach $env (sort keys %ENV) {
			my $space = " " x (20 - length($env));
			$out_env .= "$env=$ENV{$env},";
			print "$env$space: $ENV{$env}\n";
		}
		
		print "\n</PRE>";

	}

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

sub check_ip {
# --------------------------------------------------------
	my ($ip, $ipfilter) = @_;
	
	my (@ip) = split(/\./,$ip,4);
	my (@allowip) = split(/\,/,$ipfilter,4);
	
	for my $i(0..$#allowip){
		$allowip[$i] =~ s/\n|\r//g;
		$ok = 1;
		my (@ipfilter) = split(/\./,$allowip[$i],4);
		for my $x(0..3){
			if ($ip[$x] ne $ipfilter[$x] and $ipfilter[$x] ne 'x'){
				$ok = 0;
			}
		}
	}
	return $ok;
}


1;