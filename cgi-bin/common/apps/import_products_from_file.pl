#!/usr/bin/perl
#######################################################################
#######################################################################
#######################################################################
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

	# aplico la 3 porque este proceso fue diseñado para MUFAR
	if (!$in{'e'})
	{
		print "<h4>Error - No es ha especificado la Empresa </h5>";
		return;
	}

	&load_settings;

	$sys{'fmt_curr_decimal_digits'} = 2 if(!$sys{'fmt_curr_decimal_digits'});

	print "<h4>DIREKSYS($in{'e'}) - CARGA MASIVA DE SKUS</h5>";
	my $email_text = 'Cargado masivo de SKUS -- '.localtime."\n";

	&connect_db;
	# paso 1 - revisar si en el folder configurado existen los 2 archivos y podrian ser del tipo csv | xls | xlsx
	# consultar con robert este detalle
	$dir = $cfg{'path_sanborns_layouts'};
	
	if(-e $dir ) {

		# cambiar a nombre archivo dinamico
		$file1 = 'layout_skus.csv';
		$dir1 = $dir.$file1;

		if(-r $dir1 ) {
			print "abriendo: ".$dir1." <br>";


			# lee archivo 1
			# paso 2 - una vez que se encuentre el archivo hay que recorrer primero el que tiene el resumen
			my ($string) = '';
			my ($registers) = 0;
			my (@product, @cve_product, @product_price, @product_tax);
			my ($id_admin_user) = 1;

			my ($id_sku_products) = 0;
			my ($sql) = "";

			if(-r $dir1 and open (FILE, $dir1)) {
				
				print "<br><table width='100%' cellpadding='3' border='1' style='font-family:verdana;font-size:10px'>";
				print "<tr>";
				print "	    <th>Fila</th>";
				print "		<th>NAME</th>";
				print "		<th>UPC</th>";
				print "		<th>ID_PARTS</th>";
				print "		<th>ID_SKUS</th>";
				print "</tr>";

				my $errors=0;

				while ($record = <FILE>) {
					chomp $record;
					$registers++;
					if($registers == 1)
					{
						next;
					}


					my @fields = split "," , $record;
					

					my $field_name 					= $fields[0];
					my $field_model 				= $fields[1];
					my $field_id_categories 		= $fields[2];
					my $field_lots 					= $fields[3];
					my $field_purchaseid_accounts 	= $fields[4];
					my $field_saleid_accounts 		= $fields[5];
					my $field_assetid_accounts 		= $fields[6];
					my $field_purchase_tax 			= $fields[7];
					my $field_sale_tax 				= $fields[8];
					my $field_vendor_sku 			= $fields[9];
					my $field_upc 					= $fields[10];
					
					
					
					
					# ¿Esto esta bien?????
					$field_name 				=~ s/[\"\$]//g;
					$field_model 				=~ s/[\"\$]//g;
					$field_id_categories 		=~ s/[\" \$]//g;
					$field_lots 				=~ s/[\" \$]//g;
					$field_purchaseid_accounts 	=~ s/[\" \$]//g;
					$field_saleid_accounts 		=~ s/[\" \$]//g;
					$field_assetid_accounts 	=~ s/[\" \$]//g;
					$field_purchase_tax 		=~ s/[\" \$]//g;
					$field_sale_tax 			=~ s/[\" \$]//g;
					$field_vendor_sku 			=~ s/[\" \$]//g;
					$field_upc 					=~ s/[\" \$]//g;
					
					

					if ($field_name ne '' and $field_model ne '' and $field_upc ne '')
					{
						
						#Verifica que el UPC no exista ya en sl_sku
						$sql = "SELECT COUNT(*) FROM sl_skus WHERE UPC='$field_upc';";

						
						#En modo analyze imprime el query 
						if($in{'process'} eq 'analyze')
						{
							print "<tr><td>$registers</td><td>$field_name</td><td>$field_upc</td><td colspan='2'>$sql</td></tr>";
						}
						my ($sth) = &Do_SQL($sql);
						if ($sth->fetchrow > 0){
							print "<tr style='background-color:#F00;'><td>$registers</td><td>$field_name</td><td>$field_upc</td><td colspan='2'>El UPC ya esta escrito en SL_SKU</td></tr>";
							next;
						}
						
						
						
						#Inserta el registro en sl_parts
						$sql = "INSERT INTO sl_parts (Model, Name, ID_categories, Lots, PurchaseID_accounts, SaleID_accounts, AssetID_accounts, Purchase_Tax, Sale_Tax, Status, Date, Time, ID_admin_users) VALUES('$field_model', '$field_name', '$field_id_categories', '$field_lots', '$field_purchaseid_accounts', '$field_saleid_accounts', '$field_assetid_accounts', '$field_purchase_tax', '$field_sale_tax', 'Active', CURDATE(), CURTIME(), '$id_admin_user') ;";
						if( $in{'process'} eq 'commit' )
						{
							my ($sth) = &Do_SQL($sql);
							$id_sl_parts 	= $sth->{'mysql_insertid'};
							if(!$id_sl_parts)
							{
								print "<tr style='background-color:#F00;'><td>$registers</td><td>$field_name</td><td>$field_upc</td><td colspan='2'>No fue posible insertar el registro en sl_parts</td></tr>";
								next;
							}
							else
							{
								print "<tr><td>$registers</td><td>$field_name</td><td>$field_upc</td><td colspan='2'>OK. Registro insertado en sl_parts. </td></tr>";							
							}
						}
						
						if($in{'process'} eq 'analyze')
						{
							print "<tr><td>$registers</td><td>$field_name</td><td>$field_upc</td><td colspan='2'>$sql</td></tr>";
							$id_sl_parts = 0; #Valor solo de relleno en el caso de estar en modo Analyze
						}
						
						
						
						
						#Obtiene el ID_sku_products
						$id_sku_products = 400000000 + $id_sl_parts;
					



					
						#Inserta el registro en sl_skus
						$sql = "INSERT INTO sl_skus SET ID_sku_products='$id_sku_products', ID_products='$id_sl_parts', VendorSKU='$field_vendor_sku',UPC='$field_upc', Status='Active', Date=CURDATE(), Time=CURTIME(), ID_admin_users='$id_admin_user';";
						if( $in{'process'} eq 'commit' )
						{
							my ($sth) = &Do_SQL($sql);
							$id_sl_skus	= $sth->{'mysql_insertid'};
							if(!$id_sl_skus)
							{
								print "<tr style='background-color:#F00;'><td>$registers</td><td>$field_name</td><td>$field_upc</td><td colspan='2'>No fue posible insertar el registro en sl_skus</td></tr>";
								next;
							}
							else
							{
								print "<tr><td>$registers</td><td>$field_name</td><td>$field_upc</td><td colspan='2'>OK. Registro insertado en sl_skus. </td></tr>";							
							}
						}

						if($in{'process'} eq 'analyze')
						{
							print "<tr><td>$registers</td><td>$field_name</td><td>$field_upc</td><td colspan='2'>$sql</td></tr>";
						}

					}

				}

				print "</table><br>";

				close FILE;
				

			}else{
				print "<span style='color:red;'>$dir1 no encontrado </span><br>";
				return;
			}

			&send_text_mail($cfg{'from_email'},'adiaz@inovaus.com',"Resumen de Carga masiva de ordenes.", $email_text) if($in{'process'} eq 'commit');


		}else{
			print "<span style='color:red;'>ERROR AL LEER EL ARCHIVOS FUENTE <strong>$file1</strong> .</span><br>";
			print "$dir1<br>";
		}
	 
	}else{
		print "<span style='color:red;'>dir '$dir' not found </span><br>";
		$email_text .= "El archivo '$dir' no fue encontrado.\n";

	}

	&disconnect_db;


}

#########################################################
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
