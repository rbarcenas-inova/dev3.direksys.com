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
local ($in{'e'}) = 1;
chdir($dir);

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
	&execute_outsourcing_batch;
	&disconnect_db;

}


#################################################################
#################################################################
#	Function: execute_outsourcing_batch
#
#   		This functions reads from several outsourcing callcenters /home/ccname/orders paths. The file inside contains orders created by Listen Up Callcenter to be processed in Direksys. The script validate and create every order and send them to authorize if necessary
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
sub execute_outsourcing_batch{
#################################################################
#################################################################

	my ($sth) = Do_SQL("SELECT DATE_FORMAT(CURDATE(), '%d%m%y') FROM sl_orders;");
	my ($this_date) = $sth->fetchrow();
	#my $file_name = '1_'. $this_date .'.csv';

	my @req_fields_cod = ('','Date','Time','CALLERID','DNIS','LastName1','FirstName','','Phone1','','','','Cmode','','Address1','','','','City','State','Zip','shp_Name','shp_Address1','','','','shp_City','shp_State','shp_Zip','','shp_type','','','','','','','NumProds');

	my @req_fields_cc = ('','Date','Time','CALLERID','DNIS','LastName1','FirstName','','Phone1','','','','Cmode','','Address1','','','','City','State','Zip','shp_Name','shp_Address1','','','','shp_City','shp_State','shp_Zip','','shp_type','PayMethod','CardHolder','CardType','CardNum','','CardExpiration','NumProds');

	my (@contact_modes) = (1=>'sms',2=>'email',3=>'phone_call');
	my $default_price = 0.01;
	my $id_special = 100919525;
	my $rush_shipping = 4.95;#

	my $i=0;
	my @orders_not_ok_det;
	my @orders_ok_processed;
	# 416

	### Callcenters Array
	my @ccnames = (ignitemedia);#'listenup','softbox','allegro'
	my @ccusers = (6118);#6045,'6096', 6116
	my @ccrwtax = (0);#,'6096'    ## 0=Normal | >0 = max tax percent

	CC:for (0..$#ccnames) {

		$usr{'id_admin_users'} = $ccusers[$_];
		my $ccname = $ccnames[$_];
		my $ccrwtax = $ccrwtax[$_];
		my $inbound_file_path = '/home/'.$ccname.'/orders/';
		my $executed_file_path = '/home/'.$ccname.'/orders_executed/';

		next CC if !-e $inbound_file_path;

		##### Open File
		opendir (CCDIR, $inbound_file_path) || &cgierr('Unable to open directory ' . $inbound_file_path ,704,$!);
		@files = readdir(CCDIR);# Read in list of files in directory..
		closedir (CCDIR);

		if($ccname eq 'ignitemedia' and scalar (@files) > 3){
			&send_text_mail("rbarcenas\@inovaus.com","rbarcenas\@inovaus.com","Ordenes Softbox","Ya hay " . (scalar (@files) - 3) . "archivos" );
			next CC;
		}


		##### Looping files
		FILE: foreach my $file_name (@files) {

			next if ($file_name =~ /^\./);		# Skip "." and ".." entries..
			next if ($file_name =~ /^index/);		# Skip index.htm type files..

			print "Intentando abrir el archivo " . $file_name  . "\n";

			next if ($file_name !~ /^\d{1,2}_\d{6}\.csv$/);		# Skip not #_date type files

			##### Open File
			if (-e  $inbound_file_path . $file_name) {
				open(my $this_file, "<", $inbound_file_path . $file_name) or &cgierr('Unable to open file: '. $inbound_file_path . $file_name, 601,$!);

				print "Ejecutando ordenes en el archivo...\n\n";

				LINE: while (<$this_file>) {
					++$i;
					$line = $_;
					$line =~ s/\r|\n|//g;
					$line =~ s/",,,,"/","","","","/g;
					$line =~ s/",,,"/","","","/g;
					$line =~ s/",,"/","","/g;
					#print "$i - $line\n\n";

					@this_order_data = split(/","/, $line);
					(!$this_order_data[8]) and ($this_order_data[8] = $this_order_data[3]);
					(!$this_order_data[31]) and ($this_order_data[31] = 'CO');

					## COD Data Completion
					if($this_order_data[31]){
						$this_order_data[14] = $this_order_data[22];
						$this_order_data[18] = $this_order_data[26];
						$this_order_data[19] = $this_order_data[27];
						$this_order_data[20] = $this_order_data[28];
					}

					my $general_status = 'ok';
					my $j = 1;
					my $err=0;
					my $str_error='';
					my $this_order_str = "$i - $ccname\n";
					my $cc_toprocess = 1;
					my @these_payments;

					### Validamos tipo pago para producto a Flexipagos
					if($this_order_data[31] ne 'CC'){
						my $p_ini = 38;
						for($p_ini..$#this_order_data){
							my $column = $this_order_data[$_];
							$column =~ s/"|'//g;

							if($column =~ /$id_special/){
								$this_order_data[31] = 'CC';
								print "TO CC by Special Product Detection...\n";
							}
						}
					}


					for(0..$#this_order_data){

						my $column = $this_order_data[$_];
						$column =~ s/"//g;
						my $valid = 'ok';


						if($this_order_data[31] eq 'CC'){

							#######################
							####################### CC Order Validation
							#######################

							if($req_fields_cc[$_] and (!$this_order_data[$_] or $this_order_data[$_] eq '') ){
								$valid = 'REQUIRED';
								$err++;
								$str_error .= $req_fields_cc[$_] ."|n";

							}
							$column = 'xxxx xxxx xxxx ' . substr($column , -4) if $req_fields_cc[$_] eq 'CardNum';
							$this_order_str .= "$i - ". $req_fields_cc[$_] ."  : $column ($valid)\n";

						}else{

							#######################
							####################### COD Order Validation
							#######################

							if($req_fields_cod[$_] and (!$this_order_data[$_]  or $this_order_data[$_] eq '') ){
								$valid = 'REQUIRED';
								$err++;
								$str_error .= $req_fields_cod[$_] ."|";
							}
							$this_order_str .= "$i - ". $req_fields_cc[$_] ."  : $column ($valid)\n";

						}
						$j++;
					}

					#######################################################
					#######################################################
					### Validation Results
					#######################################################
					#######################################################


					if($err){
						######################
						###################### Orders Not OK
						######################
						push(@orders_not_ok_det, $this_order_str);
						$general_status = 'error';
						#next LINE;
					}

					print "\n\n$this_order_str\n\n";
					######################################################################
					######################################################################
					###################### Orders OK. Processing!!!!! ####################
					######################################################################
					######################################################################

					print "Procesando Linea $i ...\nStatus: $general_status\n";
					my %data;
					######
					###### Customer Data
					######
					$data{'CID'} = $this_order_data[3];
					$data{'DNIS'} = $this_order_data[4];
					$data{'Phone1'} = $this_order_data[8];
					$data{'Phone2'} = $this_order_data[9];
					$data{'Cellphone'} = $this_order_data[10];

					$data{'CID'} =~ s/-|\(|\)|\+|\.|\s//g;
					$data{'Phone1'} =~  s/-|\(|\)|\+|\.|\s//g;
					$data{'Phone2'} =~  s/-|\(|\)|\+|\.|\s//g;
					$data{'Cellphone'} =~  s/-|\(|\)|\+|\.|\s//g;

					$data{'CID'} = int($data{'CID'});
					$data{'Phone1'} = int($data{'Phone1'});
					$data{'Phone2'} = int($data{'Phone2'});
					$data{'Cellphone'} = int($data{'Cellphone'});

					$data{'LastName1'} = $this_order_data[5];
					$data{'FirstName'} = $this_order_data[6];
					$data{'Sex'} = $this_order_data[7];

					$data{'atime'} = $this_order_data[11];
					$data{'contact_mode'} = $contact_modes[$this_order_data[12]];
					$data{'Email'} = $this_order_data[13];

					$data{'Address1'} = $this_order_data[14];
					$data{'Address2'} = $this_order_data[15];
					$data{'Address3'} = $this_order_data[16];
					$data{'Urbanization'} = $this_order_data[17];
					$data{'City'} = $this_order_data[18];
					$data{'State'} = $this_order_data[19] . '-' . &load_name('sl_zipcodes','State',$this_order_data[19],'StateFullName');
					$data{'Zip'} = $this_order_data[20];
					$data{'Country'} = 'USA';

					### Customer Repeated?
					my $qc;
					($data{'Phone1'}) and ($qc .= " Phone1 = '$data{'Phone1'}' OR");
					($data{'Phone2'}) and ($qc .= " Phone2 = '$data{'Phone2'}' OR");
					($data{'Phone3'}) and ($qc .= " Phone3 = '$data{'Phone3'}' OR");
					($data{'CID'}) and ($qc .= " CID = '$data{'CID'}' OR");
					$qc = substr($qc, 0, -2);
					my ($sthc) = &Do_SQL("SELECT ID_customers FROM sl_customers WHERE 1 AND ($qc);");
					$data{'ID_customers'} = $sthc->fetchrow();
					$data{'repeatedcustomer'} = 'Yes';

					if(!$data{'ID_customers'}){

						###########
						########### New Customer
						###########
						my (@dbcols_customer) = ('CID','FirstName','LastName1','Sex','Phone1','Phone2','Cellphone','atime','Email','Address1','Address2','Address3','Urbanization','City','State','Zip','contact_mode');

						my $query_customer;
						for(0..$#dbcols_customer){
							if($data{$dbcols_customer[$_]}){
								$query_customer .= "$dbcols_customer[$_]= '". &filter_values($data{$dbcols_customer[$_]}) ."',";
							}
						}

						my ($sth_nc) = &Do_SQL("INSERT INTO sl_customers SET Status = 'Active', Type = 'Retail', $query_customer Date = CURDATE(), Time = CURTIME(), ID_admin_users = $usr{'id_admin_users'};");

						$data{'ID_customers'} = $sth_nc->{'mysql_insertid'};
						$data{'repeatedcustomer'} = 'No';

					}



					#########################################################################
					#########################################################################
					############################ Order Process ##############################
					#########################################################################
					#########################################################################



					my $o_id_lup = $this_order_data[0];
					$data{'Date'} = $this_order_data[1];
					$data{'Time'} = $this_order_data[2];

					$data{'shp_name'} = $this_order_data[21];
					$data{'shp_Address1'} = $this_order_data[22];
					$data{'shp_Address2'} = $this_order_data[23];
					$data{'shp_Address3'} = $this_order_data[24];
					$data{'shp_Urbanization'} = $this_order_data[25];
					$data{'shp_City'} = $this_order_data[26];
					$data{'shp_State'} = $this_order_data[27] . '-' . &load_name('sl_zipcodes','State',$this_order_data[27],'StateFullName');
					$data{'shp_Zip'} = $this_order_data[28];
					$data{'shp_Country'} = 'USA';
					$data{'shp_Notes'} = $this_order_data[29];
					$data{'Ptype'} = $this_order_data[31] eq 'CC' ? 'Credit-Card' : 'COD';
					$data{'shp_type'} = $data{'Ptype'} eq 'COD' ? 3 : $this_order_data[30];


					my $this_tax = &calculate_taxes($data{'shp_Zip'},$data{'shp_State'},$data{'shp_City'},0);

					my (@dbcols_order) = ('ID_customers','Address1','Address2','Address3','Urbanization','City','State','Zip','Country','shp_type','shp_name','shp_Address1','shp_Address2','shp_Address3','shp_Urbanization','shp_City','shp_State','shp_Zip','shp_Country','shp_Notes','Ptype','repeatedcustomer');

					my $query_order;
					for(0..$#dbcols_order){
						if($data{$dbcols_order[$_]}){
							$query_order .= "$dbcols_order[$_]= '". &filter_values($data{$dbcols_order[$_]}) ."',";
						}
					}

					my ($sth_no) = &Do_SQL("INSERT INTO sl_orders SET Status = IF('$data{'Ptype'}' = 'COD','New','Void'), $query_order first_call = 'Yes', StatusPrd = 'None', StatusPay = 'None', Date = CURDATE(), Time = CURTIME(), ID_admin_users = $usr{'id_admin_users'};");
					$data{'ID_orders'} = $sth_no->{'mysql_insertid'};
					print "Order Type: ". $this_order_data[31]."\n";
					print "ID Order: $data{'ID_orders'}\n";

					
					&add_order_notes_by_type($data{'ID_orders'},"$ccname Order\nALTORDID: ".&filter_values($o_id_lup)."\nDNIS: ".&filter_values($data{'DNIS'})."\nDate: $data{'Date'}\nTime: $data{'Time'}","Low");
					$in{'db'}="sl_orders";
					&auth_logging('orders_added', $data{'ID_orders'});




					#########################################################################
					#########################################################################
					########################## Products Process #############################
					#########################################################################
					#########################################################################



					my $prods = $this_order_data[37];
					my $ini = 38;

					do{
						$data{'ID_products'} = $this_order_data[$ini];
						$data{'Shipping'} = $this_order_data[$ini+1];
						$data{'SalePrice'} = $this_order_data[$ini+2];
						$data{'SalePrice'} = $default_price if $data{'SalePrice'} <= 0;
						$data{'Flexpayments'} = $this_order_data[$ini+3] > 1 ? $this_order_data[$ini+3] : 1;

						$data{'ID_products'} =~ s/-|\s//g;
						$data{'ID_products'} = int($data{'ID_products'});
						(length($data{'ID_products'}) == 6) and ($data{'ID_products'} += 100000000);

						if($data{'ID_products'} and $data{'SalePrice'}){

							### Product Insertion
							$data{'Shipping'} = 0 if !$data{'Shipping'};
							$data{'Shipping'} += $rush_shipping if ($data{'shp_type'} == 2 and $ini < 40); #$ccname eq 'softbox' and 
							my $this_product_tax = round($this_tax * $data{'SalePrice'},2);
							my ($this_tax_rw) = $ccrwtax ? $ccrwtax /100 : $this_tax;

							#### SalePrice Rewrite if tax rewrite
							if($this_tax > $this_tax_rw and $data{'SalePrice'} > 1) {

								my $new_total = round($data{'SalePrice'} * ( 1 + $this_tax_rw),2);
								$data{'SalePrice'} = round($new_total / (1 + $this_tax),2);
								$this_product_tax = $new_total - $data{'SalePrice'};
								#&cgierr(" ($this_tax_rw vs $this_tax) $data{'SalePrice'} = $new_total - $this_product_tax");

							}

							my ($sth_prod) = &Do_SQL("INSERT INTO sl_orders_products SET ID_products = '$data{'ID_products'}', ID_orders='$data{'ID_orders'}', ID_packinglist = 0, Quantity = 1, SalePrice = '$data{'SalePrice'}', Shipping = '$data{'Shipping'}', Tax = '$this_product_tax', FP = 1, Upsell = IF($ini = 38,'No','Yes'), Status = 'Active', Date = CURDATE(), Time = CURTIME(), ID_admin_users = $usr{'id_admin_users'};");
							&auth_logging('orders_product_added', $data{'ID_orders'});

							###
							### Payments
							###

							if($data{'ID_products'} == $id_special) {
								## 2 payments Product
								$these_payments[1] += $data{'Shipping'};
								$these_payments[2] += ($data{'SalePrice'} + $this_product_tax);
							}elsif($data{'Flexpayments'} > 1) {	
								## Flexpayments
								my $fppayment = round($data{'SalePrice'} / $data{'Flexpayments'},2);
								my $firstpayment = $data{'SalePrice'} - ($fppayment * ($data{'Flexpayments'} -1) );

								for (1..$data{'Flexpayments'}) {
									$these_payments[$_] = $_ == 1 ? 
										round($firstpayment + $data{'Shipping'} + $this_product_tax,2) :
										$fppayment;
								}

							}else{
								## 1payment Product
								$these_payments[1] += ($data{'SalePrice'} + $this_product_tax + $data{'Shipping'});
							}

							print "Product: $data{'ID_products'} - $data{'SalePrice'} - $data{'Shipping'} - $this_product_tax\n";

						}
						$ini +=4;

					}while($data{'ID_products'} and $data{'SalePrice'});




					#########################################################################
					#########################################################################
					############################ Payment Data ###############################
					#########################################################################
					#########################################################################



					$data{'PmtField2'} = $this_order_data[32];
					$data{'PmtField1'} = $this_order_data[33];
					$data{'PmtField3'} = $this_order_data[34];
					$data{'PmtField5'} = $this_order_data[35];
					$data{'PmtField4'} = $this_order_data[36];

					$data{'PmtField6'} = $data{'Phone1'};
					$data{'PmtField7'} = $data{'Ptype'} eq 'COD' ? '' : 'CreditCard';

					my $query_p;
					for my $i(1..7){
						$column = "PmtField".$i;
						$query_p .= $column."='". &filter_values($data{$column}) ."', ";
					}

					### Insercion de Pagos basado en arreglo generado en el proceso de Insercion de Productos
					for(1..$#these_payments){
						my ($sth_pay) = &Do_SQL("INSERT INTO sl_orders_payments SET ID_orders='$data{'ID_orders'}',Type='$data{'Ptype'}', $query_p Amount='".$these_payments[$_]."', Reason = 'Sale', Paymentdate = DATE_ADD(CURDATE(), INTERVAL ".$_." MONTH), AuthCode = '', AuthDateTime = '', Status = 'Approved', Date = CURDATE(), Time = CURTIME(), ID_admin_users = $usr{'id_admin_users'}");

						&auth_logging('orders_payment_added', $data{'ID_orders'});

						## Solo guardamos el ID del primer pago
						$data{'ID_orders_payments'} = $sth_pay->{'mysql_insertid'} if $_ == 1;

						print "Payment ".($_).': $ '. $these_payments[$_]."\n";

					}


					### Payment Processing
					if($data{'Ptype'} eq 'Credit-Card' and (!$data{'PmtField3'} or !$data{'PmtField4'}) ) {
						$cc_toprocess = 0;
					}

					my ($status,$msg,$code);
					my $str_p;
					if($data{'Ptype'} eq 'Credit-Card' and $cc_toprocess){

						my $x=1;
						do{	
							($status,$msg,$code) = &sltvcyb_auth($data{'ID_orders'}, $data{'ID_orders_payments'});
							$str_p .= "$status,$msg,$code\n";
							print "Try $x: $msg\n";
							$x++;
						}while($x <= 3 and $status ne 'OK');

					}




					#########################################################################
					#########################################################################
					############################ Final Process ##############################
					#########################################################################
					#########################################################################



					#### Updating Order Totals
					my $sth_total = Do_SQL("SELECT COUNT(*),SUM(SalePrice), SUM(Shipping), SUM(SalePrice + Shipping + Tax - Discount) FROM sl_orders_products WHERE ID_orders = '$data{'ID_orders'}';");
					my($o_qty, $o_net, $o_shp, $o_total) = $sth_total->fetchrow();

					Do_SQL("UPDATE sl_orders SET OrderQty = '$o_qty', OrderNet = '$o_net', OrderShp = '$o_shp', OrderTax = '$this_tax' WHERE ID_orders = '$data{'ID_orders'}';");
					&recalc_totals($data{'ID_orders'});




					$o_status = load_name('sl_orders', 'ID_orders', $data{'ID_orders'}, 'Status');
					push(@orders_ok_processed,"Linea: $i\nCallcenter:$ccname\nID Orden: $data{'ID_orders'}\nStatus: $o_status\nPayment Logs:\n$str_p");

					print "Resume: Qty: $o_qty, Net: $o_net, Shp: $o_shp, Tax(%): $this_tax\n\n";
				}

				### Moving the file to Backup
				print "Moving $inbound_file_path$file_name to $executed_file_path$file_name\n\n";
				move($inbound_file_path . $file_name, $executed_file_path . $file_name);

			}

		}

	} ## End Callcenters Loop
	

	print "Ordenes Procesadas: " . scalar @orders_ok_processed . "\n";
	print "Ordenes No OK: " . scalar @orders_not_ok_det . "\n";

	#### Sending Emails
	if( scalar @orders_ok_processed or scalar @orders_not_ok_det){

		&send_text_mail("rbarcenas\@inovaus.com","cjmendoza\@inovaus.com","Ordenes Callcenters","\r\nOrdenes Procesadas:\n" . join("\n",@orders_ok_processed) . "\n\nOrdenes con Errores en Datos:\n" . join("\n",@orders_not_ok_det) );

		&send_text_mail("rbarcenas\@inovaus.com","rgomezm\@inovaus.com","Ordenes Callcenters","\r\nOrdenes Procesadas:\n" . join("\n",@orders_ok_processed) . "\n\nOrdenes con Errores en Datos:\n" . join("\n",@orders_not_ok_det) );

		&send_text_mail("rbarcenas\@inovaus.com","rbarcenas\@inovaus.com","Ordenes Callcenters ","\r\nOrdenes Procesadas:\n" . join("\n",@orders_ok_processed) . "\n\nOrdenes con Errores en Datos\n" . join("\n",@orders_not_ok_det) );

	}


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


