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
use Encode;

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
sub execute_outsourcing_batch{
#################################################################
#################################################################
	my $process = ($in{'process'} ne 'commit')? qq|<span style="color:#000;background-color:gray;padding:5px;">ANALYZING</span>|:qq|<span style="color:#FFF;background-color:red;padding:5px;">EXECUTING</span>|;
	my $log_email;

	&load_settings;
	print "Content-type: text/html\n\n";
	print qq|<meta http-equiv="content-type" content="text/html; charset=utf-8" />\n\n|;
	print "<h4>DIREKSYS $cfg{'app_title'} (e$in{'e'}) - CARGA MASIVA DE ORDENES DE VENTA $process</h5>";
	
	if (!$in{'e'}){
		print qq|<span style="color:red;">ID de empresa es requerido</span>|;
		return;
	}

	$sys{'fmt_curr_decimal_digits'} = 2 if(!$sys{'fmt_curr_decimal_digits'});
	$dir = $cfg{'path_sanborns_layouts'};

	# my @req_fields_cod = ('','Date','Time','CALLERID','LastName1','LastName2','FirstName','','Phone1','','','','Cmode','','Address1','','','','City','State','Zip','shp_Name','shp_Address1','','','','shp_City','shp_State','shp_Zip','','shp_type','','','','','','','NumProds');
	my @req_fields_cod = ('ALTORDID','Date','Time','CALLERID','LastName1','LastName2','FirstName','','Phone1','','','','','','','','','','','','','shp_Name','shp_Address1','shp_Address2','','shp_Urbanization','shp_City','shp_State','shp_Zip','','shp_type','PayMethod','','','','','','NumProds','NumPayments');
	my @req_fields_cc = ('ALTORDID','Date','Time','CALLERID','LastName1','LastName2','FirstName','','Phone1','','','','','','Address1','Address2','','Urbanization','City','State','Zip','shp_Name','shp_Address1','shp_Address2','','shp_Urbanization','shp_City','shp_State','shp_Zip','','shp_type','PayMethod','CardHolder','CardType','CardNum','CardCVN','CardExpiration','NumProds','NumPayments');
	# my @req_fields_cc = ('ALTORDID','Date','Time','CALLERID','LastName1','LastName2','FirstName','SEX','Phone1','Phone2','CELLPHONE','ATIME','Cmode','email','Address1','Address2','Address3','Urbanization','City','State','Zip','shp_Name','shp_Address1','shp_Address2','shp_Address3','shp_Urbanization','shp_City','shp_State','shp_Zip','shp_Notes','shp_type','PayMethod','CardHolder','CardType','CardNum','CardCVN','CardExpiration','NumProds','NumPayments');

	my (@contact_modes) = (1=>'sms',2=>'email',3=>'phone_call');

	my $default_price = 0.01;
	my $id_special = 100919525;
	my $rush_shipping = 4.95;#

	my $i=0;
	my @orders_not_ok_det;
	my @orders_ok_processed;

	### Callcenters Array
	my @ccnames = ('external_source');#'listenup','softbox','allegro'
	my @ccusers = (6118);#6045,'6096', 6116
	my @ccrwtax = (0);#,'6096'    ## 0=Normal | >0 = max tax percent
	CC:for (0..$#ccnames) {

		my $ccname = $ccnames[$_];
		my $ccrwtax = $ccrwtax[$_];
		my $inbound_file_path = $dir.$ccname.'/orders/';
		my $executed_file_path = $dir.$ccname.'/orders_executed/';

		if (!-e $inbound_file_path){
			print "Folder no encontrado para <b>$ccname: </b> " . $inbound_file_path  . "<br>\n";
			
			if (!-e $executed_file_path){
				print "Folder no encontrado para <b>$ccname: </b> " . $executed_file_path  . "<br>\n";
			}
			
			next CC
		};

		$usr{'id_admin_users'} = ($cfg{'ext_source_id_admin_users'})? $cfg{'ext_source_id_admin_users'} : 1;

		##### Open File
		opendir (CCDIR, $inbound_file_path) or &cgierr('Unable to open directory ' . $inbound_file_path ,704,$!);
		@files = readdir(CCDIR);# Read in list of files in directory..
		closedir (CCDIR);

		if($ccname eq 'ignitemedia' and scalar (@files) > 3){
			&send_text_mail("rbarcenas\@inovaus.com","rbarcenas\@inovaus.com","Ordenes Softbox","Ya hay " . (scalar (@files) - 3) . "archivos" );
			next CC;
		}

		my $files_founds=0;
		##### Looping files
		FILE: foreach my $file_name (@files) {
			next if ($file_name =~ /^\./);		# Skip "." and ".." entries..
			next if ($file_name =~ /^index/);		# Skip index.htm type files..

			print "Intentando abrir el archivo " . $inbound_file_path . $file_name  . "<br>\n";

			next if ($file_name !~ /^\d{8}_\d{1,2}\.csv$/);		# Skip not #_date type files

			##### Open File
			if (-e  $inbound_file_path . $file_name) {
			
				if (-e $executed_file_path . $file_name){
					print qq|<span style="color:red">El archivo "$file_name" ya fue procesado anteriormente.</span><br>\n|;
					next;
				}

				$files_founds++;

				my $test_file = &validate_file($inbound_file_path, $file_name);
				if( $test_file and ($in{'process'} eq 'commit')){
					open(my $this_file, "<", $inbound_file_path . $file_name) or &cgierr('Unable to open file: '. $inbound_file_path . $file_name, 601,$!);

					print "Procesando el archivo...<br>\n\n";

					LINE: while (<$this_file>) {
						++$i;
						$line = $_;
						$line =~ s/\r|\n|//g;
						$line =~ s/",,,,"/","","","","/g;
						$line =~ s/",,,"/","","","/g;
						$line =~ s/",,"/","","/g;


						@this_order_data = split(/","/, $line);

						######################################################################
						######################################################################
						###################### Orders OK. Processing!!!!! ####################
						######################################################################
						######################################################################
						print "Procesando Linea $i ...\n<br>Status: $general_status<br>\n";
						my %data;
						######
						###### Customer Data
						######
						$data{'CID'} = $this_order_data[3];
						# $data{'DNIS'} = $this_order_data[4];
						$data{'Phone1'} = $this_order_data[8];
						$data{'Phone2'} = $this_order_data[9];
						$data{'Cellphone'} = $this_order_data[10];

						$data{'CID'} =~ s/-|\(|\)|\+|\.|\s//g;
						$data{'Phone1'} =~  s/-|\(|\)|\+|\.|\s//g;
						$data{'Phone2'} =~  s/-|\(|\)|\+|\.|\s//g;
						$data{'Cellphone'} =~  s/-|\(|\)|\+|\.|\s//g;

						$data{'CID'} = int($data{'CID'});
						$data{'Phone1'} = ($data{'Phone1'});
						$data{'Phone2'} = ($data{'Phone2'});
						$data{'Cellphone'} = ($data{'Cellphone'});

						$data{'LastName1'} = $this_order_data[4];
						$data{'LastName2'} = $this_order_data[5];
						$data{'FirstName'} = $this_order_data[6];
						$data{'Sex'} = (int($this_order_data[7]) == 1)? 'Male' : 'Female';

						$data{'atime'} = $this_order_data[11];
						$data{'contact_mode'} = $contact_modes[int($this_order_data[12])];
						$data{'Email'} = lc($this_order_data[13]);

						$data{'Address1'} = $this_order_data[14];
						$data{'Address2'} = $this_order_data[15];
						$data{'Address3'} = $this_order_data[16];
						$data{'Urbanization'} = $this_order_data[17];
						$data{'City'} = $this_order_data[18];
						## Get Name State
						$this_order_data[19] = &get_state($this_order_data[19]);
						$data{'State'} = ($cfg{'acc_default_country'} ne 'mexico')? $this_order_data[19] . '-' . &load_name('sl_zipcodes','State',$this_order_data[19],'StateFullName'):$this_order_data[19];
						$data{'Zip'} = $this_order_data[20];
						$data{'Country'} = ($cfg{'acc_default_country'} ne 'mexico')? 'USA':'MEXICO';

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

						# if(!$data{'ID_customers'}){
						# Se forza a crear el cliente siempre
						if(1){

							###########
							########### New Customer
							###########
							my (@dbcols_customer) = ('CID','FirstName','LastName1','LastName2','Sex','Phone1','Phone2','Cellphone','atime','Email','Address1','Address2','Address3','Urbanization','City','State','Zip','Country','contact_mode');

							my $query_customer;
							for(0..$#dbcols_customer){
								if($data{$dbcols_customer[$_]}){
									$query_customer .= "$dbcols_customer[$_]= '". &filter_values($data{$dbcols_customer[$_]}) ."',";
								}
							}

							$sql = "INSERT INTO sl_customers SET Status = 'Active', Type = '$cfg{'ext_source_customers_type'}', $query_customer Date = CURDATE(), Time = CURTIME(), ID_admin_users = $usr{'id_admin_users'};";
							my ($sth_nc) = &Do_SQL($sql) if ($in{'process'} eq 'commit');
							# print "\n\n$sql<br>\n\n" if ($in{'debug'} ==1);
							print_query($sql) if ($in{'debug'} == 1);

							$data{'ID_customers'} = $sth_nc->{'mysql_insertid'};
							$data{'repeatedcustomer'} = 'No';
							print "\n\nID_customers: $data{'ID_customers'}<br>\n\n";

							$in{'db'}="sl_customers";
							&auth_logging('customer_added', $data{'ID_orders'});

						}

						#########################################################################
						#########################################################################
						############################ Order Process ##############################
						#########################################################################
						#########################################################################



						my $o_id_lup = $this_order_data[0];
						$o_id_lup =~ s/"//g;
						$data{'Date'} = $this_order_data[1];
						$data{'Time'} = $this_order_data[2];

						$data{'shp_name'} = $this_order_data[21];
						$data{'shp_Address1'} = $this_order_data[22];
						$data{'shp_Address2'} = $this_order_data[23];
						$data{'shp_Address3'} = $this_order_data[24];
						$data{'shp_Urbanization'} = $this_order_data[25];
						$data{'shp_City'} = $this_order_data[26];
						## Get Name State
						$this_order_data[27] = &get_state($this_order_data[27]);
						$data{'shp_State'} = ($cfg{'acc_default_country'} ne 'mexico')? $this_order_data[27] . '-' . &load_name('sl_zipcodes','State',$this_order_data[27],'StateFullName'):$this_order_data[27];
						$data{'shp_Zip'} = $this_order_data[28];
						$data{'shp_Country'} = ($cfg{'acc_default_country'} ne 'mexico')? 'USA':'MEXICO';
						$data{'shp_Notes'} = $this_order_data[29];
						$data{'Ptype'} = ($this_order_data[31] eq 'CC')? 'Credit-Card' : (($this_order_data[31] eq 'COD')?'COD':'Referenced Deposit');
						$data{'shp_type'} = $data{'Ptype'} eq 'COD' ? 3 : $this_order_data[30];

						my $this_tax = &calculate_taxes($data{'shp_Zip'},$data{'shp_State'},$data{'shp_City'},0);

						my (@dbcols_order) = ('ID_customers','Address1','Address2','Address3','Urbanization','City','State','Zip','Country','shp_type','shp_name','shp_Address1','shp_Address2','shp_Address3','shp_Urbanization','shp_City','shp_State','shp_Zip','shp_Country','shp_Notes','Ptype','repeatedcustomer');

						my $query_order;
						for(0..$#dbcols_order){
							if($data{$dbcols_order[$_]}){
								$query_order .= "$dbcols_order[$_]= '". &filter_values($data{$dbcols_order[$_]}) ."',";
							}
						}

						$query_order .= ($this_order_data[0] ne '')? "ID_orders_alias='$o_id_lup',":"";
						$query_order .= ($cfg{'ext_source_orders_ptype'} and $cfg{'ext_source_orders_ptype'} ne '')? "Pterms='$cfg{'ext_source_orders_ptype'}',":"";
						$query_order .= ($cfg{'ext_source_orders_id_salesorigins'} and $cfg{'ext_source_orders_id_salesorigins'} ne '')? "ID_salesorigins='$cfg{'ext_source_orders_id_salesorigins'}',":"";
						

						$add_sql = "";
						$add_sql .= ($cfg{'ext_source_datetime'} eq 'layout')?" Date = '$this_order_data[1]', Time = '$this_order_data[2]',":" Date = CURDATE(), Time = CURTIME(),";

						$sql="INSERT INTO sl_orders SET Status = IF('$data{'Ptype'}' = 'Credit-Card','Void','New'), $query_order first_call = 'Yes', StatusPrd = 'None', StatusPay = IF('$data{'Ptype'}' = 'Referenced Deposit','Pending Payment','None'), $add_sql ID_admin_users = $usr{'id_admin_users'};";
						# print "\n\n$sql<br>\n\n" if ($in{'debug'} ==1);
						print_query($sql) if ($in{'debug'} == 1);
						my ($sth_no) = &Do_SQL($sql) if ($in{'process'} eq 'commit');
						$data{'ID_orders'} = $sth_no->{'mysql_insertid'};
						
						$log_email .= "Order Type: ". $this_order_data[31]."<br>\n";
						$log_email .= "ID Order: $data{'ID_orders'}<br>\n";
						
						# print $log_email;

						$in{'db'}="sl_orders";
						&auth_logging('orders_added', $data{'ID_orders'});

						## Se asigna la zona al pedido nuevo
						&update_order_zone($data{'ID_orders'}) if ($data{'ID_orders'});

						$sql="INSERT INTO sl_orders_notes SET ID_orders='$data{'ID_orders'}',Notes = 'Este pedido fue cargado al sistema, mediante un procedimiento masivo. Archivo $file_name', Type = 'Low',Date = CURDATE(), Time = CURTIME(), ID_admin_users='$usr{'id_admin_users'}';";
						
						# print "\n\n$sql<br>\n\n" if ($in{'debug'} ==1);
						print_query($sql) if ($in{'debug'} == 1);
						if ($in{'process'} eq 'commit'){
								&Do_SQL(&add_order_notes_by_type($data{'ID_orders'},"Este pedido fue cargado al sistema, mediante un procedimiento masivo. Archivo $file_name","Low");
							}



						#########################################################################
						#########################################################################
						########################## Products Process #############################
						#########################################################################
						#########################################################################




						my $prods = $this_order_data[37];
						my $ini = 39;

						do{
							$data{'ID_products'} = $this_order_data[$ini];
							$data{'Shipping'} = $this_order_data[$ini+1];
							$data{'SalePrice'} = $this_order_data[$ini+2];
							$data{'SalePrice'} = $default_price if $data{'SalePrice'} <= 0;
							$data{'Tax_percent'} = ($this_order_data[$ini+3] == 2)? 0 : $cfg{'taxp_default'};
							$data{'ShpTax'}  = 0; #Inicializado requerido;

							$data{'ID_products'} =~ s/-|\s//g;
							$data{'ID_products'} = int($data{'ID_products'});
							(length($data{'ID_products'}) == 6) and ($data{'ID_products'} += 100000000);

							if($data{'ID_products'} and $data{'SalePrice'} and $data{'SalePrice'} > 0){
								
								print 		  qq|$data{'ID_products'}<---<br><div style="background-color:#FFF;border:solid 2px #D8208F;padding:10px;font-size:12px;margin:0 0 10px 0;">|;

								#########################################################################
								## P R O M O ## P R O M O ## P R O M O ## P R O M O ## P R O M O ## P R O
								#########################################################################
								## Validacion de productos
								$sql = "SELECT sl_products.Status, RIGHT($data{'ID_products'},6) ID_products FROM sl_skus INNER JOIN sl_products ON sl_skus.ID_products=sl_products.ID_products WHERE sl_skus.Status='Active' AND sl_skus.id_sku_products='$data{'ID_products'}' AND sl_skus.ID_products=RIGHT('$data{'ID_products'}',6);"; 
								print_query($sql) if ($in{'debug'} == 1);
								my $sth = &Do_SQL($sql);
								my (my $status_product, $id_promo) = $sth->fetchrow_array();
								if (!$status_product){
									$log_email .= qq|<span style="color:red;">El producto NO existe: $data{'ID_products'}</span><br>|;
									print 		  qq|<span style="color:red;">El producto NO existe: $data{'ID_products'}</span><br>|;
									$err++;
								}elsif ($status_product ne 'On-Air'){
									$log_email .= qq|<span style="color:red;">El producto no tiene estatus On-Air: $status_product</span><br>|;
									print 		  qq|<span style="color:red;">El producto no tiene estatus On-Air: $status_product</span><br>|;
									$err++;
								}else{
									$log_email .= qq|<span style="color:green;">El producto <strong>$data{'ID_products'}</strong> tiene Status: <strong>$status_product</strong></span><br>|;
									print 		  qq|<span style="color:green;">El producto <strong>$data{'ID_products'}</strong> tiene Status: <strong>$status_product</strong></span><br>|;
								}

								$sql ="SELECT (SELECT TRIM( BOTH '|' FROM VValue ) FROM sl_vars WHERE sl_vars.VName LIKE ('promo".$id_promo."'))ID_products, (SELECT TRIM( BOTH '|' FROM VValue ) FROM sl_vars WHERE sl_vars.VName LIKE ('percent_promo".$id_promo."'))Percents";
								my $sth = &Do_SQL($sql);
								print_query($sql) if ($in{'debug'} == 1);
								my ($promo,$percents) = $sth->fetchrow;
								my (@products) = split(/\|/,$promo);
								my $products = @products;
								my (@percents);
								if ($percents){
									@percents = split(/\|/,$percents);
								}
								if ($promo){
									$log_email .= qq|<span style="color:blue;">El producto es un PROMO: $id_promo</span><br>|;
									print 		  qq|<span style="color:blue;">El producto es un PROMO: $id_promo</span><br>|;
								}else{
									$products[0] = $data{'ID_products'};
								}

								for(0..$#products){
									

									$data{'ID_products'} = ($promo)?$id_promo:$data{'ID_products'};

									if($products[$_]>0){
										print 		  qq|<div style="background-color:#FFF;border:solid 2px #FF784D;padding:10px;font-size:12px;margin:0 0 10px 0;">|;

										$log_email .= qq|<span style="color:red;">Procesando el producto[$_]: $data{'ID_products'}</span><br>|;
										print 		  qq|<span style="color:red;">Procesando el producto[$_]: $data{'ID_products'}</span><br>|;

										if ($in{'debug'}){

											print "## Debug: datos de entrada<br>";
											print "ID_products=$data{'ID_products'}<br>";
											print "SalePrice=$data{'SalePrice'}<br>";
											print "Shipping=$data{'Shipping'}<br>";
											print "Tax_percent=$data{'Tax_percent'}<br><br>";
										}

										### Product Insertion
										$data{'Shipping'} = 0 if !$data{'Shipping'};
										# $data{'Shipping'} += $rush_shipping if ($data{'shp_type'} == 2 and $ini < 40); #$ccname eq 'softbox' and 
										my $this_product_tax = round($this_tax * $data{'SalePrice'},2);
										my ($this_tax_rw) = $ccrwtax ? $ccrwtax /100 : $this_tax;

										#### SalePrice Rewrite if tax rewrite
										if($this_tax > $this_tax_rw and $data{'SalePrice'} > 1) {

											my $new_total = round($data{'SalePrice'} * ( 1 + $this_tax_rw),2);
											$data{'SalePrice'} = round($new_total / (1 + $this_tax),2);
											$this_product_tax = $new_total - $data{'SalePrice'};
											#&cgierr(" ($this_tax_rw vs $this_tax) $data{'SalePrice'} = $new_total - $this_product_tax");

										}

										# print "====>SalePrice=$data{'SalePrice'} $products<br>";
										## Precio calculado por porcentaje
										if ($percents){
											$data{'SalePrice'} = ($percents[$_] == 0)? 0 : ($percents[$_] * $data{'SalePrice'}) / 100;
										}elsif($products){
											$data{'SalePrice'} = $data{'SalePrice'} / $products;
										}

										# Tax de producto :: Se calcula solo si envian un 2 
										if ($data{'Tax_percent'} > 0){
											$data{'SalePriceTmp'} = round($data{'SalePrice'}/(1+$data{'Tax_percent'}),2);
											$data{'Tax'} = round($data{'SalePrice'}-$data{'SalePriceTmp'},2);
											$data{'SalePrice'} = $data{'SalePriceTmp'};

										}
										
										# Tax de envio :: Se calcula siempre
										if ($data{'Shipping'} > 0 and $cfg{'shptax_percent_default'} > 0){
											$data{'ShippingTmp'}= round($data{'Shipping'}/(1+$cfg{'shptax_percent_default'}),2);
											$data{'ShpTax'} = round($data{'Shipping'}-$data{'ShippingTmp'},2);
											$data{'Shipping'} = $data{'ShippingTmp'};
										}
										
										if ($in{'debug'}){
											print "## Debug: datos de salida<br>";
											print "Tax=$data{'Tax'}<br>";
											print "Tax_percent=$data{'Tax_percent'}<br>";
											print "SalePrice=$data{'SalePrice'}<br><br>";
											print "Shipping=$data{'Shipping'}<br>";
											print "ShpTax=$data{'ShpTax'}<br><br>";
										}

										$sql = "INSERT INTO sl_orders_products SET ID_products = '$data{'ID_products'}', ID_orders='$data{'ID_orders'}', ID_packinglist = 0, Quantity = 1
										, SalePrice = '$data{'SalePrice'}'
										, Shipping = '$data{'Shipping'}'
										, Tax = '$data{'Tax'}'
										, Tax_percent = '$data{'Tax_percent'}'
										, ShpTax = '$data{'ShpTax'}'
										, ShpTax_percent = '$cfg{'shptax_percent_default'}'
										, FP = 1, Upsell = IF($ini = 38,'No','Yes'), Status = 'Active', Date = CURDATE(), Time = CURTIME(), ID_admin_users = $usr{'id_admin_users'};";
										# print "\n\n$sql<br>\n\n" if ($in{'debug'} ==1);
										print_query($sql) if ($in{'debug'} == 1);
										my ($sth_prod) = &Do_SQL($sql) if ($in{'process'} eq 'commit');
										&auth_logging('orders_product_added', $data{'ID_orders'});

										print 		  qq|</div>|;

									}
								}
								# < - - -- - - - -- - - - - - -- - -- - - - - - -- - - -- 	
								print 		  qq|</div>|;

							}
							$ini +=4;

						}while($data{'ID_products'} and $data{'SalePrice'});


						#########################################################################
						#########################################################################
						############################ Final Process ##############################
						#########################################################################
						#########################################################################


						# Update sl_orders totals
						my $sth = &Do_SQL("SELECT 
							count(*) AS OrderQty
							, SUM(SalePrice - Discount + Shipping + Tax + ShpTax) AS OrderTotal 
							, SUM(SalePrice) AS OrderNet
							, SUM(Shipping)OrderShp
							, SUM(Discount)OrderDisc
							, SUM(Tax + ShpTax) AS Tax
							FROM sl_orders_products WHERE ID_orders = '$data{'ID_orders'}' AND Status NOT IN ('Inactive','Order Cancelled');
							");
						my ($orderqty,$ordertotal,$ordernet,$ordershp,$orderdisc,$ordertax) = $sth->fetchrow_array();

						$sql = "UPDATE sl_orders SET OrderQty='$orderqty', OrderShp='$ordershp', OrderDisc='$orderdisc', OrderNet='$ordernet' WHERE ID_orders='$data{'ID_orders'}';";
						# print "\n\n$sql<br>\n\n" if ($in{'debug'} ==1);
						print_query($sql) if ($in{'debug'} == 1);
						&Do_SQL($sql) if ($in{'process'} eq 'commit');


						#########################################################################
						#########################################################################
						############################ Payment Data ###############################
						#########################################################################
						#########################################################################


						$data{'PmtField2'} = $this_order_data[32];# CardHolder 
						
						if ($this_order_data[33] eq "VI"){
							$data{'PmtField1'} = 'Visa';
						}elsif ($this_order_data[33] eq "MC"){
							$data{'PmtField1'} = 'MasterCard';
						}elsif ($this_order_data[33] eq "AE"){
							$data{'PmtField1'} = 'American Express';
						}

						$data{'PmtField3'} = $this_order_data[34];# CardNum 
						$data{'PmtField5'} = $this_order_data[35];# CardCVN 
						$data{'PmtField4'} = $this_order_data[36];# CardExpiration 

						$data{'PmtField6'} = $data{'Phone1'};
						$data{'PmtField7'} = 'CreditCard';
						$data{'PmtField8'} = int($this_order_data[38]);#  NumPayments 

						my $query_p;
						for my $i(1..8){
							$column = "PmtField".$i;
							$query_p .= $column."='". &filter_values($data{$column}) ."', ";
						}

						# Solo cuando es TDC a MSI
						$query_p .= ($this_order_data[38] > 1)? "PmtField10='03',":"";

						### Insercion de Pagos basado en arreglo generado en el proceso de Insercion de Productos
						# for(1..$#these_payments){
							# $ordertotal = &round($ordertotal,2);
							$sql="INSERT INTO sl_orders_payments SET ID_orders='$data{'ID_orders'}',Type='$data{'Ptype'}', $query_p Amount='".$ordertotal."', Reason = 'Sale', Paymentdate = CURDATE(), AuthCode = '', AuthDateTime = '', Status = 'Approved', Date = CURDATE(), Time = CURTIME(), ID_admin_users = $usr{'id_admin_users'}";
							# print "\n\n$sql<br>\n\n" if ($in{'debug'} ==1);
							print_query($sql) if ($in{'debug'} == 1);
							my ($sth_pay) = &Do_SQL($sql) if ($in{'process'} eq 'commit');

							&auth_logging('orders_payment_added', $data{'ID_orders'});
							## Solo guardamos el ID del primer pago
							$data{'ID_orders_payments'} = $sth_pay->{'mysql_insertid'};

							# print "Payment ".($_).': $ '. $these_payments[$_]."<br>\n";

						# }


						### Payment Processing
						if($data{'Ptype'} eq 'Credit-Card' and (!$data{'PmtField3'} or !$data{'PmtField4'} or !$data{'PmtField5'}) ) {
							$cc_toprocess = 0;
						}

						# my ($status,$msg,$code);
						# my $str_p;
						# if($data{'Ptype'} eq 'Credit-Card' and $cc_toprocess and $in{'process'} eq 'commit'){

						# 	my $x=1;
						# 	do{	
						# 		($status,$msg,$code) = &sltvcyb_auth($data{'ID_orders'}, $data{'ID_orders_payments'});
						# 		$str_p .= "$status,$msg,$code\n";
						# 		print "Try $x ($data{'ID_orders'}, $data{'ID_orders_payments'}): $msg\n<br>";
						# 		$x++;
						# 	}while($x <= 3 and $status ne 'OK');

						# }

						$o_status = load_name('sl_orders', 'ID_orders', $data{'ID_orders'}, 'Status');
						push(@orders_ok_processed,"Linea: $i<br>\nCallcenter:$ccname<br>\nID Orden: $data{'ID_orders'}<br>\nStatus: $o_status<br>\nPayment Logs:<br>\n$str_p");

						print "Resume: Qty: $orderqty, Net: $ordernet, Shp: $ordershp, Tax(%): $ordertax<br><br>\n\n";
					}

					###############################################################################
					# Enviando correo y moviendo el archivo procesado...
					###############################################################################3
					my $from_mail = ($cfg{'default_email_sender'})?$cfg{'default_email_sender'}:'info@inova.com.mx';
				 	my $to_mail = 'ltorres@inova.com.mx,adiaz@inovaus.com,rbarcenas@inovaus.com,gquirino@inovaus.com,achagoya@inova.com.mx';
				 	#my $to_mail = 'gquirino@inovaus.com';
				 	my $subject_mail = "Carga de pedidos por Layout $file_name";
				 	my $body_mail = '<h3>Resumen</h3>'.$log_email;
				 	my $text_mail = 'Testing Text';
				 	my $res = send_mandrillapp_email($from_mail,$to_mail,$subject_mail,$body_mail,$text_mail,'none');

				 	print "Enviando correo: $res->{'status'}<br>";

				 	print "Moving file ".$inbound_file_path . $file_name.", ".$executed_file_path . $file_name."<br><br>\n\n";
				 	move($inbound_file_path . $file_name, $executed_file_path . $file_name);
				}

				## NO FUNCIONA
				### Moving the file to Backup
				# print "Moving $inbound_file_path$file_name to $executed_file_path$file_name<br><br>\n\n";
				# move($inbound_file_path . $file_name, $executed_file_path . $file_name);

				# if ($in{'process'} eq 'commit'){
				# 	my $from_mail = ($cfg{'default_email_sender'})?$cfg{'default_email_sender'}:'info@inova.com.mx';
				# 	my $to_mail = 'ltorres@inova.com.mx,adiaz@inovaus.com,rbarcenas@inovaus.com';
				# 	# my $to_mail = 'adiaz@inovaus.com';
				# 	my $subject_mail = "Carga de pedidos por Layout $file_name";
				# 	my $body_mail = '<h3>Resumen</h3>'.$log_email;
				# 	my $text_mail = 'Testing Text';
				# 	my $res = send_mandrillapp_email($from_mail,$to_mail,$subject_mail,$body_mail,$text_mail,'none');

				# 	print "Enviando correo: $res->{'status'}<br>";

				# 	print "Moving file ".$inbound_file_path . $file_name.", ".$executed_file_path . $file_name."<br><br>\n\n";
				# 	move($inbound_file_path . $file_name, $executed_file_path . $file_name);
				# }

			}

		}

		print "No hay archivos que procesar para <b>$ccname: </b> " . $inbound_file_path  . "<br>\n" if (!$files_founds);

	} ## End Callcenters Loop
	

	print "Ordenes Procesadas: " . scalar @orders_ok_processed . "<br>\n";
	print "Ordenes No OK: " . scalar @orders_not_ok_det . "<br>\n";

	#### Sending Emails
	if( scalar @orders_ok_processed or scalar @orders_not_ok_det){

		# &send_text_mail("rbarcenas\@inovaus.com","cjmendoza\@inovaus.com","Ordenes Callcenters","\r\nOrdenes Procesadas:\n" . join("\n",@orders_ok_processed) . "\n\nOrdenes con Errores en Datos:\n" . join("\n",@orders_not_ok_det) );

		# &send_text_mail("rbarcenas\@inovaus.com","rgomezm\@inovaus.com","Ordenes Callcenters","\r\nOrdenes Procesadas:\n" . join("\n",@orders_ok_processed) . "\n\nOrdenes con Errores en Datos:\n" . join("\n",@orders_not_ok_det) );

		&send_text_mail("adiaz\@inovaus.com","rbarcenas\@inovaus.com","Ordenes Callcenters ","\r\nOrdenes Procesadas:\n" . join("\n",@orders_ok_processed) . "\n\nOrdenes con Errores en Datos\n" . join("\n",@orders_not_ok_det) );

	}

}

#----------------------------------------------------------------
sub validate_file {
	#-- Recepción de parámetros
	my ($inbound_file_path, $file_name) = @_;

	open(my $this_file, "<", $inbound_file_path . $file_name) or &cgierr('Unable to open file: '. $inbound_file_path . $file_name, 601,$!);

	print "Ejecutando archivo...<br>\n\n";

	#--------------------------------------------------------------------------------------------------------------------
	# Recorrido del archivo....
	#--------------------------------------------------------------------------------------------------------------------
	$i = 0;
	$errors_file = 0;
	my $result = 1;
	LINE: while (<$this_file>) {
		++$i;
		$line = $_;
		$line =~ s/\r|\n|//g;
		$line =~ s/",,,,"/","","","","/g;
		$line =~ s/",,,"/","","","/g;
		$line =~ s/",,"/","","/g;
		
		#-- Se valida por la cantidad de valores que contiene la fila actual (43 ó 43+(4*n))
		@this_order_data = split(/","/, $line);
		$total_fields = scalar(@this_order_data);
		
		print qq|<table style="border: none; border-collapse: collapse; border-spacing: 0; empty-cells: show; font-family: arial, sans-serif; font-size: 8pt; margin-bottom: 7px;">|;
		print qq|<tr>
					<td colspan="$total_fields">
						<span style="font-size: 11pt; font-weight: bold;">Fila $i --> </span>
						<span style="color: black; font-size: 11pt;">Total de columnas encontradas: $total_fields</span>
					</td>
				</tr>|;

		#-- Se imprimen los valores
		my $html_cols_row1 = "<tr>";
		my $html_cols_row2 = "<tr>";
		foreach (0 .. $#this_order_data) {
			$this_order_data[$_] =~ s/"//g;
			my $val = $this_order_data[$_];
			$html_cols_row1 .= qq|<td style="background-color: #e6e6e6; border: 1px solid gray; min-width: 15px; padding: 1px 3px 1px 3px; text-align: center; white-space: nowrap;">[$_] $req_fields_cc[$_]</td>|;
			$html_cols_row2 .= qq|<td style="border: 1px solid gray; min-width: 15px; padding: 1px 3px 1px 3px; text-align: center; white-space: nowrap;">$val</td>|;
		}
		$html_cols_row1 .= "</tr>";
		$html_cols_row2 .= "</tr>";
		print $html_cols_row1 . $html_cols_row2;

		#-- Se obtiene la cantidad de valores adicionales por cada producto
		if ($total_fields > 43){
			$dif = $total_fields - 43;
		} else {
			$dif = 4;
		}

		#-- Si la estructura de los valores es correcta
		if ($total_fields == 43 or ($total_fields > 43 and ($dif % 4) == 0) ) {
			#-------------------------------------------------------------------------------------------#
			#-- Validación de valores
			#-------------------------------------------------------------------------------------------#
			# Si no mandan el no de tel se asigna el de donde llamo
			# print qq|$this_order_data[8]->$this_order_data[3]<br>|;
			(!$this_order_data[8]) and ($this_order_data[8] = $this_order_data[3]);

			# print qq|$this_order_data[34]<br>|;
			# Si no trae datos de TDC
			(!$this_order_data[34]) and ($this_order_data[31] = 'COD');

			$this_order_data[27] = &get_state($this_order_data[27]);
			print $this_order_data[27].'<br />';
			## COD Data Completion
			if($this_order_data[31] eq 'COD'){
				$this_order_data[14] = $this_order_data[22];
				$this_order_data[18] = $this_order_data[26];
				$this_order_data[19] = $this_order_data[27];
				$this_order_data[20] = $this_order_data[28];
				$this_order_data[38] = 1;
			}else{
				$this_order_data[19] = &get_state($this_order_data[19]);
			}

			my $general_status = 'ok';
			#my $j = 1; No se utiliza
			my $err=0;
			my $list_errors = '';
			my $str_error='';
			my $this_order_str = "$i - $ccname<br>\n";
			my $cc_toprocess = 1;
			my @these_payments;
			
			### Si es un pago con TDC a MSI(solo aplica para banorte payworks)
			if($this_order_data[31] eq 'CC' and $this_order_data[31] > 1){
				# " PmtField10='03' ";# Cuando es TDC a MSI
				$add_sql = ", PmtField10='03'";
			}

			if($this_order_data[31] eq 'CC'){
				print qq|<span>Validando Pedido de tipo <span style="color:blue;">Tarjeta de Credito</span></span>|;
			}elsif($this_order_data[31] eq 'COD'){
				print qq|<span>Validando Pedido de tipo <span style="color:blue;">COD</span></span>|;
			}elsif($this_order_data[31] eq 'DR'){
				print qq|<span>Validando Pedido de tipo <span style="color:blue;">Deposito Referenciado</span></span>|;
			}
			
			#######################
			####################### Validaciones especificas sobre campos
			#######################
			## Validacion de Pedido repetido
			$this_order_data[0] =~ s/"//g;
			if ($this_order_data[0]){
				$sql ="SELECT ID_orders FROM sl_orders WHERE ID_orders_alias='$this_order_data[0]' LIMIT 1;";
				#print "\n\n$sql\n\n";
				my ($sth5) = &Do_SQL($sql);
				$repeated_order = $sth5->fetchrow();

				if ($repeated_order){
					$log_email .= qq|<span style="color:red;">El pedido $this_order_data[0] ya existe en el sistema con el ID: $repeated_order</span><br>|;
					$list_errors .= qq|<span style="color:red;">El pedido $this_order_data[0] ya existe en el sistema con el ID: $repeated_order</span><br>|;
					$err++;
					$str_error .= $req_fields_cod[$_] ."|";
				}
			}

			## Validacion de Codigo Postal y Estado
			my $tmp_state = $this_order_data[27]; # shp_State
			my $tmp_zip = $this_order_data[28]; # shp_Zip
			my $test = &validate_state_zipcode($tmp_zip,$tmp_state);
			if ($test){
				$log_email .= qq|<span style="color:red;">CP no corresponde al Estado: $test</span><br>|;
				$list_errors .= qq|<span style="color:red;">CP no corresponde al Estado: $test</span><br>|;
				$err++;
				$str_error .= $req_fields_cod[$_] ."|";
			}

			## Validacion de datos de TDC
			if($this_order_data[31] eq 'CC'){
				$this_order_data[38] = int($this_order_data[38]);
				$this_order_data[34] = int($this_order_data[34]);

				if (!$this_order_data[36] or length($this_order_data[36]) != 4){
					$log_email .= qq|<span style="color:red;">Formato de columna 36 incorrecto MMYY: $this_order_data[36]</span><br>|;
					$list_errors .= qq|<span style="color:red;">Formato de columna 36 incorrecto MMYY: $this_order_data[36]</span><br>|;
					$err++;

				}else{

					my $month = int(substr $this_order_data[36], 0 , 2);
					if ($month < 1 or $month > 12){
						$log_email .= qq|<span style="color:red;">Formato de columna 36 incorrecto MMYY: $this_order_data[36]</span><br>|;
						$list_errors .= qq|<span style="color:red;">Formato de columna 36 incorrecto MMYY: $this_order_data[36]</span><br>|;
						$err++;
					}					
				}
				if (!$this_order_data[34] or length($this_order_data[34]) < 15){
					$log_email .= qq|<span style="color:red;">Formato de columna 34 incorrecto 9999 9999 9999 9999: $this_order_data[34]</span><br>|;
					$list_errors .= qq|<span style="color:red;">Formato de columna 34 incorrecto 9999 9999 9999 9999: $this_order_data[34]</span><br>|;
					$err++;
				}
				if (!$this_order_data[35] or length($this_order_data[35]) < 3 or $this_order_data[35] =~ /\D/){
					$log_email .= qq|<span style="color:red;">Formato de columna 35 incorrecto int(3-4): $this_order_data[35]</span><br>|;
					$list_errors .= qq|<span style="color:red;">Formato de columna 35 incorrecto int(3-4): $this_order_data[35]</span><br>|;
					$err++;
				}
				if (!$this_order_data[38] or (length($this_order_data[38]) != 1 and ($this_order_data[38]) != 3 and ($this_order_data[38]) !=6 and ($this_order_data[38]) != 9 and ($this_order_data[38]) != 12) ){
					$log_email .= qq|<span style="color:red;">Formato de columna 38 incorrecto (1,3,6,9,12): $this_order_data[38]</span><br>|;
					$list_errors .= qq|<span style="color:red;">Formato de columna 38 incorrecto (1,3,6,9,12): $this_order_data[38]</span><br>|;
					$err++;
				}
			}

			my $column = $this_order_data[$_];
			my $valid = '<span style="color:blue;">ok</span>';


			if($this_order_data[31] eq 'CC'){

				#######################
				####################### CC Order Validation
				#######################

				if($req_fields_cc[$_] and (!$this_order_data[$_] or $this_order_data[$_] eq '') ){
					$valid = '<span style="color:red;">REQUIRED</span>';

					$err++;
					$str_error .= $req_fields_cc[$_] ."|n";

				}
				
				$column = 'xxxx xxxx xxxx ' . substr($column , -4) if $req_fields_cc[$_] eq 'CardNum';
				$this_order_str .= "$i - [$_]  ". $req_fields_cc[$_] ."  : $column ($valid)<br>\n";

			}elsif($this_order_data[31] eq 'COD' or $this_order_data[31] eq 'DR'){

				#######################
				####################### COD Order Validation
				#######################

				if($req_fields_cod[$_] and (!$this_order_data[$_]  or $this_order_data[$_] eq '') ){
					$valid = '<span style="color:red;">REQUIRED</span>';
					$err++;
					$str_error .= $req_fields_cod[$_] ."|";
				}

				$this_order_str .= "$i - [$_] ". $req_fields_cc[$_] ."  : $column ($valid)<br>\n";

			}
			#$j++;
			#-------------------------------------------------------------------------------------------#	

			#-- Impresión del resultado del análisis de la fila actual		
			if (!$err) {							
				print qq|<tr>
							<td colspan="$total_fields" style="border: none; font-size: 11pt;">
								<span style="font-weight: normal;">Status General: </span><span style="color: green;">OK:</span>
							</td>
						</tr>|;				
			} else {
				print qq|<tr>
							<td colspan="$total_fields" style="border: none; font-size: 11pt;">
								$list_errors
							</td>
						</tr>|;
				print qq|<tr>
						<td colspan="$total_fields" style="border: none; font-size: 11pt;">
							<span style="font-weight: normal;">Status General: </span><span style="color: red;">ERROR:</span><span style="color: gray; font-size: 11pt;">Por favor corrija los errores e int&eacute;ntelo de nuevo...</span>
						</td>
					</tr>|;
				$result = 0;
			}
			$errors_file += $err;
		} 
		#-- Si la estructura es INCORRECTA
		else {
			print qq|<tr>
						<td colspan="$total_fields" style="border: none; font-size: 11pt;">
							<span style="font-weight: normal;">Status General: </span><span style="color: red;">ERROR:</span><span style="color: gray; font-size: 11pt;">La estructura de los valores es incorrecta...</span>
						</td>
					</tr>|;
			$errors_file++;
			$result = 0;
		}		

		print "</table>";		
	}
	print '<br /><hr />';
	print qq|<span>Errores econtratos: $errors_file</span>|;
	if( $errors_file == 0 ){
		print qq|<br /><span style="color: green;">El archivo $file_name, est&aacute; listo para ser procesado</span>|;
	}
	print '<hr /><br />';
	return ($result);
}
#----------------------------------------------------------------


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
	#$orig_state_utf8 = encode('utf-8', $orig_state);
	$sql = decode_utf8("SELECT ZipCode, StateFullName FROM sl_zipcodes WHERE Status='Active' AND zipcode='$orig_zipcode' AND StateFullName = '$orig_state' GROUP BY ZipCode, StateFullName");
	print "<br />".$sql."<br />";
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


sub get_state{
	my ($id_state) = @_;

	my @aryStates = ('Aguascalientes','Baja California','Baja California Sur','Campeche','Chiapas','Chihuahua','Coahuila de Zaragoza','Colima','Distrito Federal','Durango','Guanajuato','Guerrero','Hidalgo','Jalisco','México','Michoacán de Ocampo','Morelos','Nayarit','Nuevo León','Oaxaca','Puebla','Querétaro','Quintana Roo','San Luis Potosí','Sinaloa','Sonora','Tabasco','Tamaulipas','Tlaxcala','Veracruz de Ignacio de la Llave','Yucatán','Zacatecas','XX-Otro');
	my $name_state = '';
	if( $id_state > 0 and $id_state < 33 ){
		foreach my $i (0 .. $#aryStates) {
  			if( $id_state == ($i+1) ){
  				$name_state = $aryStates[$i];
  				break;
  			}
		}
		return $name_state;
	}else{
		return "No existe el estado con ese ID";
	}
}