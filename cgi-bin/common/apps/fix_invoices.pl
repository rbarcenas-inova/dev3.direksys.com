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

local(%in) = &parse_form;
local ($dir) = getcwd;
local ($in{'e'}) = 4;
# local ($usr{'id_admin_users'}) = 1;
# local ($cfg{'id_warehouses'}) = 1001;
# local ($cfg{'reset'}) = 1;


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


sub main {
#################################################################
#################################################################

	$|++;
	&connect_db;
	&fix_invoices;
	&disconnect_db;

}

sub fix_invoices {
#############################################################################
#############################################################################
	# cgierr('HOLA');
	print "Content-type: text/html\n\n";
	# print 'HOLA';
	use Data::Dumper;
	my @arr = (6095188, 6094303, 6095461, 6095459, 6094722, 6094444, 6094877, 6096207, 6095651);
	# # print "Content-type: text/html\n\n";
	# &connect_db_w('direksys2_e4','172.20.27.78','d2mow','jKSu2&&28GjngbKJSWH*(*289HK');
	# print &Do_SQL("SELECT DATABASE()")->fetchrow();
	# exit;
	print '<pre>';
	&Do_SQL('START TRANSACTION');
	&Do_SQL('BEGIN');
	foreach $el (@arr){
		$id_invoices = &Do_SQL("select cu_invoices.ID_invoices from cu_invoices inner join cu_invoices_lines using(id_invoices) where id_orders='$el' and cu_invoices.status = 'Cancelled' and cu_invoices.id_admin_users!=100 group by id_invoices limit 1")->fetchrow();
		$query = "insert into cu_invoices (`ID_customers`, `doc_serial`, `doc_num`, `doc_date`, `payment_type`, `payment_method`, `payment_digits`, `invoice_net`, `invoice_total`, `discount`, `total_taxes_detained`, `total_taxes_transfered`, `Cost`, `currency`, `currency_exchange`, `invoice_type`, `place_consignment`, `expediter_fcode`, `expediter_fname`, `expediter_fregimen`, `expediter_faddress_street`, `expediter_faddress_num`, `expediter_faddress_num2`, `expediter_faddress_urbanization`, `expediter_faddress_district`, `expediter_faddress_city`, `expediter_faddress_state`, `expediter_faddress_country`, `expediter_faddress_zipcode`, `expediter_address_street`, `expediter_address_num`, `expediter_address_num2`, `expediter_address_urbanization`, `expediter_address_district`, `expediter_address_city`, `expediter_address_state`, `expediter_address_country`, `expediter_address_zipcode`, `customer_fcode`, `customer_fname`, `customer_address_street`, `customer_address_num`, `customer_address_num2`, `customer_address_urbanization`, `customer_address_district`, `customer_address_city`, `customer_address_state`, `customer_address_country`, `customer_address_zipcode`, `customer_shpaddress_code`, `customer_shpaddress_alias`, `customer_shpaddress_contact`, `customer_shpaddress_street`, `customer_shpaddress_num`, `customer_shpaddress_num2`, `customer_shpaddress_urbanization`, `customer_shpaddress_district`, `customer_shpaddress_city`, `customer_shpaddress_state`, `customer_shpaddress_country`, `customer_shpaddress_zipcode`, `xml_cfd`, `xml_cfdi`, `xml_addenda`, `uuid`, `xml_uuid`, `xml_fecha_emision`, `xml_fecha_certificacion`, `original_string`, `related_ID_invoices`, `ID_orders_alias`, `ID_orders_alias_date`, `exchange_receipt`, `exchange_receipt_date`, `credit_days`, `conditions`, `batch_num`, `imr_code`, `Status`, `VendorID`, `customer_address_gln`, `customer_shpaddress_gln`, `PurchaseDate`, `viewed`, `Date`, `Time`, `ID_admin_users`)
		SELECT cu_invoices.`ID_customers`,cu_invoices.`doc_serial`,cu_invoices.`doc_num`,cu_invoices.`doc_date`,cu_invoices.`payment_type`,cu_invoices.`payment_method`,cu_invoices.`payment_digits`,cu_invoices.`invoice_net`,cu_invoices.`invoice_total`,cu_invoices.`discount`,cu_invoices.`total_taxes_detained`,cu_invoices.`total_taxes_transfered`,cu_invoices.`Cost`,cu_invoices.`currency`,cu_invoices.`currency_exchange`,cu_invoices.`invoice_type`,cu_invoices.`place_consignment`,cu_invoices.`expediter_fcode`,cu_invoices.`expediter_fname`,cu_invoices.`expediter_fregimen`,cu_invoices.`expediter_faddress_street`,cu_invoices.`expediter_faddress_num`,cu_invoices.`expediter_faddress_num2`,cu_invoices.`expediter_faddress_urbanization`,cu_invoices.`expediter_faddress_district`,cu_invoices.`expediter_faddress_city`,cu_invoices.`expediter_faddress_state`,cu_invoices.`expediter_faddress_country`,cu_invoices.`expediter_faddress_zipcode`,cu_invoices.`expediter_address_street`,cu_invoices.`expediter_address_num`,cu_invoices.`expediter_address_num2`,cu_invoices.`expediter_address_urbanization`,cu_invoices.`expediter_address_district`,cu_invoices.`expediter_address_city`,cu_invoices.`expediter_address_state`,cu_invoices.`expediter_address_country`,cu_invoices.`expediter_address_zipcode`,cu_invoices.`customer_fcode`,cu_invoices.`customer_fname`,cu_invoices.`customer_address_street`,cu_invoices.`customer_address_num`,cu_invoices.`customer_address_num2`,cu_invoices.`customer_address_urbanization`,cu_invoices.`customer_address_district`,cu_invoices.`customer_address_city`,cu_invoices.`customer_address_state`,cu_invoices.`customer_address_country`,cu_invoices.`customer_address_zipcode`,cu_invoices.`customer_shpaddress_code`,cu_invoices.`customer_shpaddress_alias`,cu_invoices.`customer_shpaddress_contact`,cu_invoices.`customer_shpaddress_street`,cu_invoices.`customer_shpaddress_num`,cu_invoices.`customer_shpaddress_num2`,cu_invoices.`customer_shpaddress_urbanization`,cu_invoices.`customer_shpaddress_district`,cu_invoices.`customer_shpaddress_city`,cu_invoices.`customer_shpaddress_state`,cu_invoices.`customer_shpaddress_country`,cu_invoices.`customer_shpaddress_zipcode`,cu_invoices.`xml_cfd`,cu_invoices.`xml_cfdi`,cu_invoices.`xml_addenda`,cu_invoices.`uuid`,cu_invoices.`xml_uuid`,cu_invoices.`xml_fecha_emision`,cu_invoices.`xml_fecha_certificacion`,cu_invoices.`original_string`,cu_invoices.`related_ID_invoices`,cu_invoices.`ID_orders_alias`,cu_invoices.`ID_orders_alias_date`,cu_invoices.`exchange_receipt`,cu_invoices.`exchange_receipt_date`,cu_invoices.`credit_days`,cu_invoices.`conditions`,cu_invoices.`batch_num`,cu_invoices.`imr_code`,cu_invoices.`Status`,cu_invoices.`VendorID`,cu_invoices.`customer_address_gln`,cu_invoices.`customer_shpaddress_gln`,cu_invoices.`PurchaseDate`,cu_invoices.`viewed`,cu_invoices.`Date`,cu_invoices.`Time`,cu_invoices.`ID_admin_users` from cu_invoices inner join cu_invoices_lines using(id_invoices) where id_orders='$el' and cu_invoices.status = 'Cancelled' and cu_invoices.id_admin_users!=100 group by id_invoices limit 1";
		$rs = &Do_SQL($query);
		$new_id_invoices = &Do_SQL("SELECT LAST_INSERT_ID();")->fetchrow();
		$order = &Do_SQL("Select * from sl_orders where id_orders = '$el' limit 1")->fetchrow_hashref();
		$descuento = $order->{'OrderDisc'};
		&Do_SQL("update cu_invoices set doc_date=now(), Date=curdate(), Time=curtime(), discount='$order->{'OrderDisc'}', status='Confirmed', xml_uuid='',total_taxes_transfered =round(".($order->{'OrderNet'}-$order->{'OrderDisc'})*(1 + $order->{'OrderTax'}).",2), doc_serial='', doc_num=0 where cu_invoices.id_invoices=$new_id_invoices ");

		&Do_SQL("insert into cu_invoices_lines(`ID_invoices`, `ID_orders`, `ID_creditmemos`, `ID_debitmemos`, `ID_orders_products`, `line_num`, `quantity`, `measuring_unit`, `reference_id`, `description`, `unit_price`, `Cost`, `amount`, `tax`, `tax_type`, `tax_name`, `tax_rate`, `discount`, `customs_gln`, `customs_name`, `customs_num`, `customs_date`, `ID_sku`, `ID_sku_alias`, `size`, `packing_type`, `packing_unit`, `UPC`, `import_declaration_number`, `import_declaration_date`, `customs`, `customs_broker`, Date, Time, `ID_admin_users`)
			select
			 $new_id_invoices `ID_invoices`, `ID_orders`, `ID_creditmemos`, `ID_debitmemos`, `ID_orders_products`, `line_num`, `quantity`, `measuring_unit`, `reference_id`, `description`, `unit_price`, `Cost`, `amount`, `tax`, `tax_type`, `tax_name`, `tax_rate`, `discount`, `customs_gln`, `customs_name`, `customs_num`, `customs_date`, `ID_sku`, `ID_sku_alias`, `size`, `packing_type`, `packing_unit`, `UPC`, `import_declaration_number`, `import_declaration_date`, `customs`, `customs_broker`, curdate() c1, curtime() c2, `ID_admin_users`
			from cu_invoices_lines where id_invoices=$id_invoices
		");

		$id_invoices_lines = &Do_SQL("SELECT id_invoices_lines from cu_invoices_lines where id_invoices = $new_id_invoices and discount > 0.01 limit 1")->fetchrow();
		&Do_SQL("UPDATE cu_invoices_lines set discount=$descuento where id_invoices_lines= $id_invoices_lines");
		
		&Do_SQL("UPDATE cu_invoices_lines set tax =round( (amount - discount) * (tax_rate ), 2 ) where id_invoices= $new_id_invoices");



		$id_invoices = &Do_SQL("select cu_invoices.ID_invoices from cu_invoices inner join cu_invoices_lines using(id_invoices) where id_orders='$el' and cu_invoices.status = 'Cancelled' and cu_invoices.id_admin_users=100 group by id_invoices limit 1")->fetchrow();
		$query = "insert into cu_invoices (`ID_customers`, `doc_serial`, `doc_num`, `doc_date`, `payment_type`, `payment_method`, `payment_digits`, `invoice_net`, `invoice_total`, `discount`, `total_taxes_detained`, `total_taxes_transfered`, `Cost`, `currency`, `currency_exchange`, `invoice_type`, `place_consignment`, `expediter_fcode`, `expediter_fname`, `expediter_fregimen`, `expediter_faddress_street`, `expediter_faddress_num`, `expediter_faddress_num2`, `expediter_faddress_urbanization`, `expediter_faddress_district`, `expediter_faddress_city`, `expediter_faddress_state`, `expediter_faddress_country`, `expediter_faddress_zipcode`, `expediter_address_street`, `expediter_address_num`, `expediter_address_num2`, `expediter_address_urbanization`, `expediter_address_district`, `expediter_address_city`, `expediter_address_state`, `expediter_address_country`, `expediter_address_zipcode`, `customer_fcode`, `customer_fname`, `customer_address_street`, `customer_address_num`, `customer_address_num2`, `customer_address_urbanization`, `customer_address_district`, `customer_address_city`, `customer_address_state`, `customer_address_country`, `customer_address_zipcode`, `customer_shpaddress_code`, `customer_shpaddress_alias`, `customer_shpaddress_contact`, `customer_shpaddress_street`, `customer_shpaddress_num`, `customer_shpaddress_num2`, `customer_shpaddress_urbanization`, `customer_shpaddress_district`, `customer_shpaddress_city`, `customer_shpaddress_state`, `customer_shpaddress_country`, `customer_shpaddress_zipcode`, `xml_cfd`, `xml_cfdi`, `xml_addenda`, `uuid`, `xml_uuid`, `xml_fecha_emision`, `xml_fecha_certificacion`, `original_string`, `related_ID_invoices`, `ID_orders_alias`, `ID_orders_alias_date`, `exchange_receipt`, `exchange_receipt_date`, `credit_days`, `conditions`, `batch_num`, `imr_code`, `Status`, `VendorID`, `customer_address_gln`, `customer_shpaddress_gln`, `PurchaseDate`, `viewed`, `Date`, `Time`, `ID_admin_users`)
		SELECT cu_invoices.`ID_customers`,cu_invoices.`doc_serial`,cu_invoices.`doc_num`,cu_invoices.`doc_date`,cu_invoices.`payment_type`,cu_invoices.`payment_method`,cu_invoices.`payment_digits`,cu_invoices.`invoice_net`,cu_invoices.`invoice_total`,cu_invoices.`discount`,cu_invoices.`total_taxes_detained`,cu_invoices.`total_taxes_transfered`,cu_invoices.`Cost`,cu_invoices.`currency`,cu_invoices.`currency_exchange`,cu_invoices.`invoice_type`,cu_invoices.`place_consignment`,cu_invoices.`expediter_fcode`,cu_invoices.`expediter_fname`,cu_invoices.`expediter_fregimen`,cu_invoices.`expediter_faddress_street`,cu_invoices.`expediter_faddress_num`,cu_invoices.`expediter_faddress_num2`,cu_invoices.`expediter_faddress_urbanization`,cu_invoices.`expediter_faddress_district`,cu_invoices.`expediter_faddress_city`,cu_invoices.`expediter_faddress_state`,cu_invoices.`expediter_faddress_country`,cu_invoices.`expediter_faddress_zipcode`,cu_invoices.`expediter_address_street`,cu_invoices.`expediter_address_num`,cu_invoices.`expediter_address_num2`,cu_invoices.`expediter_address_urbanization`,cu_invoices.`expediter_address_district`,cu_invoices.`expediter_address_city`,cu_invoices.`expediter_address_state`,cu_invoices.`expediter_address_country`,cu_invoices.`expediter_address_zipcode`,cu_invoices.`customer_fcode`,cu_invoices.`customer_fname`,cu_invoices.`customer_address_street`,cu_invoices.`customer_address_num`,cu_invoices.`customer_address_num2`,cu_invoices.`customer_address_urbanization`,cu_invoices.`customer_address_district`,cu_invoices.`customer_address_city`,cu_invoices.`customer_address_state`,cu_invoices.`customer_address_country`,cu_invoices.`customer_address_zipcode`,cu_invoices.`customer_shpaddress_code`,cu_invoices.`customer_shpaddress_alias`,cu_invoices.`customer_shpaddress_contact`,cu_invoices.`customer_shpaddress_street`,cu_invoices.`customer_shpaddress_num`,cu_invoices.`customer_shpaddress_num2`,cu_invoices.`customer_shpaddress_urbanization`,cu_invoices.`customer_shpaddress_district`,cu_invoices.`customer_shpaddress_city`,cu_invoices.`customer_shpaddress_state`,cu_invoices.`customer_shpaddress_country`,cu_invoices.`customer_shpaddress_zipcode`,cu_invoices.`xml_cfd`,cu_invoices.`xml_cfdi`,cu_invoices.`xml_addenda`,cu_invoices.`uuid`,cu_invoices.`xml_uuid`,cu_invoices.`xml_fecha_emision`,cu_invoices.`xml_fecha_certificacion`,cu_invoices.`original_string`,cu_invoices.`related_ID_invoices`,cu_invoices.`ID_orders_alias`,cu_invoices.`ID_orders_alias_date`,cu_invoices.`exchange_receipt`,cu_invoices.`exchange_receipt_date`,cu_invoices.`credit_days`,cu_invoices.`conditions`,cu_invoices.`batch_num`,cu_invoices.`imr_code`,cu_invoices.`Status`,cu_invoices.`VendorID`,cu_invoices.`customer_address_gln`,cu_invoices.`customer_shpaddress_gln`,cu_invoices.`PurchaseDate`,cu_invoices.`viewed`,cu_invoices.`Date`,cu_invoices.`Time`,cu_invoices.`ID_admin_users` from cu_invoices inner join cu_invoices_lines using(id_invoices) where id_orders='$el' and cu_invoices.status = 'Cancelled' and cu_invoices.id_admin_users=100 group by id_invoices limit 1";
		$rs = &Do_SQL($query);
		$new_id_invoices = &Do_SQL("SELECT LAST_INSERT_ID();")->fetchrow();
		$order = &Do_SQL("Select * from sl_orders where id_orders = '$el' limit 1")->fetchrow_hashref();
		&Do_SQL("update cu_invoices set Date=curdate(), Time=curtime(), discount='$order->{'OrderDisc'}',doc_date=now(), xml_uuid='', status='Confirmed', total_taxes_transfered =round(".($order->{'OrderNet'}-$order->{'OrderDisc'})*(1 + $order->{'OrderTax'}).",2), doc_serial='', doc_num=0 where cu_invoices.id_invoices=$new_id_invoices ");

		&Do_SQL("insert into cu_invoices_lines(`ID_invoices`, `ID_orders`, `ID_creditmemos`, `ID_debitmemos`, `ID_orders_products`, `line_num`, `quantity`, `measuring_unit`, `reference_id`, `description`, `unit_price`, `Cost`, `amount`, `tax`, `tax_type`, `tax_name`, `tax_rate`, `discount`, `customs_gln`, `customs_name`, `customs_num`, `customs_date`, `ID_sku`, `ID_sku_alias`, `size`, `packing_type`, `packing_unit`, `UPC`, `import_declaration_number`, `import_declaration_date`, `customs`, `customs_broker`, Date, Time, `ID_admin_users`)
			select
			 $new_id_invoices `ID_invoices`, `ID_orders`, `ID_creditmemos`, `ID_debitmemos`, `ID_orders_products`, `line_num`, `quantity`, `measuring_unit`, `reference_id`, `description`, `unit_price`, `Cost`, `amount`, `tax`, `tax_type`, `tax_name`, `tax_rate`, `discount`, `customs_gln`, `customs_name`, `customs_num`, `customs_date`, `ID_sku`, `ID_sku_alias`, `size`, `packing_type`, `packing_unit`, `UPC`, `import_declaration_number`, `import_declaration_date`, `customs`, `customs_broker`, curdate() c1, curtime() c2, `ID_admin_users`
			from cu_invoices_lines where id_invoices=$id_invoices
		");

		$id_invoices_lines = &Do_SQL("SELECT id_invoices_lines from cu_invoices_lines where id_invoices = $new_id_invoices and discount > 0.01 limit 1")->fetchrow();
		&Do_SQL("UPDATE cu_invoices_lines set discount=$descuento where id_invoices_lines= $id_invoices_lines");

		&Do_SQL("UPDATE cu_invoices_lines set tax =round( (amount - discount) * (tax_rate ), 2 ) where id_invoices= $new_id_invoices");

		print 'TERMINADO ORDER ->'. $el. '<br>';
		&Do_SQL('COMMIT');
	}
	# return;
	# $q = "select * from cu_invoices inner join cu_invoices_lines where id_orders in(6095414, 6095011, 6095188, 6094303, 6095461, 6095459, 6094722, 6094444, 6094877, 6096207, 6095651)";

}



##################################################################
#     CGIERR   	#
##################################################################
sub cgierr {
# --------------------------------------------------------
# Last Modified on: 11/10/08 12:00:31
# Last Modified by: MCC C. Gabriel Varela S: Se corrige que se muestre la fecha de forma correcta
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