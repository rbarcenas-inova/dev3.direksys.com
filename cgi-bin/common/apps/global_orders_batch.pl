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
	require ('../../mod/wms/admin.html.cgi');
	require ('../../mod/wms/admin.cod.cgi');
	require ('../../mod/wms/sub.base.html.cgi');
	require ('../../mod/wms/sub.func.html.cgi');
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
	&processed_file_global;
	&disconnect_db;

}


#############################################################################
#############################################################################
#   Function: batches_upload_file
#
#       Es: Procesa archivos de ordenes enviadas por Global
#       En: 
#
#    Created on: 07/10/2008  16:21:10
#
#    Author: _Pablo Hdez_
#
#    Modifications:
#
#   Parameters:
#
#     - id_warehouses : ID_warehouses
#
#  Returns:
#
#      - id_ : ID_
#
#   See Also:
#
#      - apps/ajaxbuild.cgi: chg_warehouse_batch
#
sub processed_file_global {
#############################################################################
#############################################################################
	
	#print "Content-type: text/html\n\n";

	my $inbound_file_path = $cfg{'path_upfiles'}.'batches/e'.$in{'e'}.'/ARCHIVE/';
	my $executed_file_path = $inbound_file_path . 'processed/';

	$usr{'id_admin_users'} = 1;
	$in{'action'} = 1; #
	$in{'fc_dropshipp_return'} = 1; ## Indica a entershipment proceso externo
	$in{'id_warehouses'} = 1050; ## Warehouse Global
	my $id_warehouses_damage = 1052; ## Warehouse Damage Global
	my @cols = ('id_global2','qty','global_status','id_skus','sku_name','id_orders','con','id_global1','global_customer','last_name','firts_name',
						'shp_address1','shp_address2','shp_city','shp_state','shp_zipcode','order_date','phone1','company_name','global_userid',
						'invoice_date','invoice_part','paid','tracking_number','shp_date','shp_method','serial','serial_id');

	## Tracking numbers de ordenes repetidas
	my $tracking_skipped = '1Z877V547200011964||1Z877V547200011973||1Z877V547200011982||1Z877V547200011991||1Z877V547200012007||1Z877V547200012016||1Z877V547200012025||1Z877V547200012034||1Z877V547200012043||1Z877V547200012061||1Z877V547200012070||1Z877V547200012089||1Z877V547200012098||1Z877V547200012105||1Z877V547200012123||1Z877V547200012132||1Z877V547200012141||1Z877V547200012169||1Z877V547200012187||1Z877V547200012203||1Z877V547200012212||1Z877V547200012230||1Z877V547200012258||1Z877V547200012267||1Z877V547200012285||1Z877V547200012294||1Z877V547200012310||1Z877V547200012338||1Z877V547200012356||1Z877V547200012365||1Z877V547200012383||1Z877V547200012392||1Z877V547200012409||1Z877V547200012418||1Z877V547200012436||1Z877V547200012454||1Z877V547200012463||1Z877V547200012481||1Z877V547200012490||1Z877V547200012516||1Z877V547200012525||1Z877V547200012543||1Z877V547200012552||1Z877V547200012561||1Z877V547200012598||1Z877V547200011697||1Z877V547200011777||1Z877V547200015157||1Z877V547200013604||1Z877V547200013631||1Z877V547200013711||1Z877V547200013784||1Z877V547200017422||1Z877V547200017520||1Z877V547200017771||1Z877V547200017806||1Z877V547200017815||1Z877V547200017824||1Z877V547200017922||1Z877V547200017931||1Z877V547200017968||1Z877V547200019199||1Z877V547200017977||1Z877V547200019180||1Z877V540300018051||1Z877V547200018083||1Z877V547200018092||1Z877V547200018118||1Z877V547200019162||1Z877V547200018127||1Z877V547200018216||1Z877V547200018225||1Z877V547200018243||1Z877V547200019546||1Z877V547200018252||1Z877V547200018314||1Z877V547200018323||1Z877V540300018426||1Z877V547200018430||1Z877V547200018458||1Z877V547200018467||1Z877V540300018480||1Z877V547200018494||1Z877V540300018515||1Z877V547200018529||1Z877V547200018814||1Z877V547200018823||1Z877V547200018832||1Z877V547200018896||1Z877V547200018903||1Z877V547200018912||1Z877V547200018930||1Z877V547200018949||1Z877V547200018958||1Z877V547200018967||1Z877V547200018976||1Z877V547200018985||1Z877V547200018994||1Z877V540300019014||1Z877V547200019037||1Z877V547200019046||1Z877V540300019050||1Z877V547200019064||1Z877V547200019073';

	my @orders_ok;
	my @orders_error;
	my @orders_ws;

	my @orders_rt_ok;
	my @orders_rt_error;
	my @orders_rt_returns;

	my @orders_data_error;
	
	opendir (LUEDIR, $inbound_file_path) || &cgierr('Unable to open directory ' . $inbound_file_path ,704,$!);
	@files = readdir(LUEDIR);# Read in list of files in directory..
	closedir (LUEDIR);


	##### Looping files
	FILE: foreach my $file_name (sort @files) {

		next if ($file_name =~ /^\./);		# Skip "." and ".." entries..
		next if ($file_name =~ /^index/);		# Skip index.htm type files..

		#my $nfname = $file_name !~ /^NEW_/ ? 'NEW_' : $file_name;
		if (-e  $inbound_file_path . 'NEW_' . $file_name and $file_name !~ /^NEW_GRInvoice-\d{2}-\d{2}-\d{2}/) {
			print "Saltando $file_name por existencia de NEW_$file_name ...\n";

			### Moving the file to Backup
			print "Moving $inbound_file_path$file_name to $executed_file_path$file_name\n\n";
			move($inbound_file_path . $file_name, $executed_file_path . $file_name);

			next;# Skip if not # NEW_GRInvoice files
		
		}else{
			next if ($file_name !~ /GRInvoice-\d{2}-\d{2}-\d{2}/);# Skip if not # GRInvoice files
		}

		print "Intentando abrir el archivo " . $inbound_file_path . $file_name  . "\n";

		##### Open File
		my $i=0;
		my $id_orders_flag;
		my $is_wholesale;
		my $order_type;
		my $cod_driver;
		my $this_msg;


		if (-e  $inbound_file_path . $file_name) {

			if(open(my $wfile, ">>", $inbound_file_path . $file_name) ){
				print $wfile "END OF FILE\n";
				close($wfile);
			}

			open(my $this_file, "<", $inbound_file_path . $file_name) or &cgierr('Unable to open file: '. $inbound_file_path . $file_name, 601,$!);

			print "Ejecutando ordenes en el archivo...\n\n";

			LINE: while (<$this_file>) {
				$line = $_;
				$line =~ s/\r|\n|//g;
				#print "$i - $line\n\n";

				my %this_data;
				my ($item_status);
				my @line_data = split(/";"|","/);
				for (0..$#line_data) {

					$line_data[$_] =~ s/\r|\n|\t|\"//g;
					$line_data[$_] =~ s/^\s+//;
					$line_data[$_] =~ s/\s+$//;

					$this_data{$cols[$_]} = $line_data[$_];
				}
				$this_data{'id_orders'} = int($this_data{'id_orders'});
				$this_data{'qty'} = int($this_data{'qty'});


				##### Tracking Numbers repeated / Must Skip 
				if( $tracking_skipped =~ /$this_data{'tracking_number'}/ and $this_data{'tracking_number'} ne ''){
					print "$this_data{'id_orders'} - $this_data{'tracking_number'} - Skipped \n\n";
					next LINE;
				}

				
				if($this_data{'global_status'} !~ /SH|RT/){

					## TODO: Procesar Status PB, BO, PS,''
					print "$this_data{'id_orders'} - $this_data{'global_status'} - Skipped NO SH|RT\n\n";
					next LINE;

				}


				##### ID_orders
				if(!$this_data{'id_orders'}){

					## Buscar ID_orders de acuerdo a datos del cliente
				}


				##### Processing Data
				if($this_data{'id_orders'} > 0){

					## Shp Method
					($this_data{'shp_method'} eq 'PM') and ($this_data{'shp_method'} = 'USPS');
					($this_data{'shp_method'} eq 'FEG') and ($this_data{'shp_method'} = 'Fedex');


					###################################################################
					###################################################################
					###################################################################
					###################################################################
					#
					#						STATUS : SH
					#
					###################################################################
					###################################################################
					###################################################################
					###################################################################

					if($this_data{'global_status'} eq 'SH') {
						
						## Tracking usado
						## ToDo: No se puede usar el tracking porque muchas se marcaron enviadas sin trackin como Local
						my $modquery = $this_data{'tracking_number'} ne '' ? " AND sl_orders_parts.Tracking = '".&filter_values($this_data{'tracking_number'})."' " : '';
						my ($sth) = &Do_SQL("SELECT COUNT(*) FROM sl_orders_products INNER JOIN sl_orders_parts USING(ID_orders_products) 
						                    WHERE ID_orders = '".int($this_data{'id_orders'})."' $modquery  GROUP BY ID_orders;");
						my ($tracking_used) = $sth->fetchrow();

						if($tracking_used) {

							print "$this_data{'id_orders'} - $this_data{'tracking_number'} - Used\n";
							next LINE;
						}

						###################################################################
						###################################################################
						###################################################################
						###################################################################
						#
						#						ORDER entershipment()
						#
						###################################################################
						###################################################################
						###################################################################
						###################################################################

						if($id_orders_flag and $this_data{'id_orders'} != $id_orders_flag){

							++$i;

							$is_wholesale = &is_exportation_order($id_orders_flag);
							

							if($is_wholesale){

								## Wholesale Order
							
								push(@orders_ws,"File:$file_name\nID:$id_orders_flag");
								print "ID:$id_orders_flag\nType:$order_type\nWS ORDER Skipped\n\n";

							}else{

								$in{'tracking'} =~ s/\n$//;
								$in{'authcode'} = &authnumber;

								## Regular / COD Order
								print "ID:$id_orders_flag\nType:$order_type\nShpDate:$in{'shpdate'}\nTracking:$in{'tracking'}\nAuth:$in{'authcode'}\n";
								&entershipment();

								#my $data = "Bulk:$in{'bulk'}\nLocal:$in{'localdelivery'}\nShp Date:$in{'shpdate'}\nInfo:\n$in{'tracking'}\n$in{'shpdate'}";
								#print "Sending $data";

								$va{'message'} =~ s/<li>//g;
								$va{'message'} =~ s/<\/li>/\n/g;			
								print $va{'message'} . "\n\n";

								## Scan Message
								if($va{'message'} =~ /\d+ pieces scanned/) {
									
									push(@orders_ok, "Order:$id_orders_flag\n$va{'message'}");
									my ($sth) = &Do_SQL("UPDATE sl_orders SET StatusPrd='None' WHERE ID_orders = '".int($this_data{'id_orders'})."';");

								}else{

									my ($sth) = &Do_SQL("SELECT COUNT(*) FROM sl_orders_products WHERE ID_orders = '$id_orders_flag' AND SalePrice >= 0 
														AND Status NOT IN('Order Cancelled','Inactive','Returned')
														AND ID_products NOT LIKE '6%' 
														AND (ISNULL(ShpDate) or ShpDate='0000-00-00' or ShpDate='') 
														AND (ISNULL(Tracking) or Tracking='')
														AND sl_orders_products.SalePrice>0;");
									my ($tosent) = $sth->fetchrow();

									if($tosent) {
										&set_error_note($id_orders_flag,$in{'shpdate'},$in{'tracking'},'SH');
										push(@orders_error, "Order:$id_orders_flag\nType:$order_type\nShpDate:$in{'shpdate'}\nTracking:$in{'tracking'}\n$va{'message'}");
									}

									
								}

							}

							delete($va{'message'});
							delete($in{'shpdate'});
							delete($in{'tracking'});
							delete($in{'bulk'});
							delete($in{'localdelivery'});
							delete($in{'authcode'});
							$id_orders_flag = 0;
							$order_type = '';
							$cod_driver = 0;
							$is_wholesale = 0;
						}

						
						###################################################################
						###################################################################
						###################################################################
						###################################################################
						#
						#				ORDER INFO (Tracking, Type, ID_orders)
						#
						###################################################################
						###################################################################
						###################################################################
						###################################################################

						if(!$id_orders_flag) {

							$id_orders_flag = $this_data{'id_orders'};
							$order_type = &load_name('sl_orders','ID_orders',int($this_data{'id_orders'}),'Ptype');

							($order_type eq 'COD' or !$this_data{'tracking_number'}) and ($in{'localdelivery'} = 1);
							($order_type ne 'COD') and ($in{'bulk'} = 1);

							if($order_type eq 'COD') {

								## Ship Via
								if($this_data{'shp_method'} eq 'UPS'){
									$cod_driver = 1038;
								}elsif($this_data{'shp_method'} eq 'USPS'){
									$cod_driver = 1048;
								}elsif($this_data{'shp_method'} eq 'Fedex'){
									$cod_driver = 1046;
								}

								if($cod_driver){
									my ($sth) = &Do_SQL("UPDATE sl_orders SET ID_warehouses = '$cod_driver' WHERE ID_orders = '".int($this_data{'id_orders'})."';");
								}

							}

							$in{'shpdate'} = substr($this_data{'shp_date'},0,10);
							$in{'tracking'} = $cfg{'prefixentershipment'} . int($this_data{'id_orders'}) . "\n";
							$in{'tracking'} .= $this_data{'shp_method'} .'-'.$this_data{'tracking_number'} . "\n" if $this_data{'tracking_number'};
							
						}

						###################################################################
						###################################################################
						###################################################################
						###################################################################
						#
						#						ITEM STATUS SORTING
						#
						###################################################################
						###################################################################
						###################################################################
						###################################################################

						my $upc = &load_name('sl_skus','ID_sku_products',int($this_data{'id_skus'}),'upc');

						if($upc) {
							for (1..$this_data{'qty'}) {
								$in{'tracking'} .= $upc ."\n";
							}
						}else{
							## TODO: Enviar notif (Item sin UPC)
						}

					}elsif($this_data{'global_status'} eq 'RT') {

					###################################################################
					###################################################################
					###################################################################
					###################################################################
					#
					#						STATUS : RT
					#
					###################################################################
					###################################################################
					###################################################################
					###################################################################
					
						## Has Returns?
						my ($sthr) = &Do_SQL("SELECT COUNT(*) FROM sl_returns WHERE ID_orders = '".int($this_data{'id_orders'})."';");
						my ($ret) = $sthr->fetchrow();
						if ($ret) {
							push(@orders_rt_returns, "File:$file_name\nOrder:$id_orders_flag\nType:$order_type\nSkipped with Return");
							next LINE;
						}

						if($id_orders_flag and $this_data{'id_orders'} != $id_orders_flag){

							++$i;							
							
							if( $order_type eq 'COD' ) {

								## COD Orders
								if($in{'tracking'} and $in{'from_wh'} and $in{'id_warehouses'}) {


									&cod_wreceipt();

									if($va{'message'} =~ /\d+ pieces entered/) {
										
										push(@orders_rt_ok, "File:$file_name\nOrder:$id_orders_flag\nType:$order_type\n$va{'message'}");
										my ($sth) = &Do_SQL("UPDATE sl_orders SET StatusPrd='None' WHERE ID_orders = '".int($this_data{'id_orders'})."';");

									}else{
										&set_error_note($id_orders_flag,$in{'from_wh'},$in{'tracking'},'RT');
										push(@orders_rt_error, "Order:$id_orders_flag\nType:$order_type\nTracking:$in{'tracking'}\n$va{'message'}");
									}
								}
								print "ID:$id_orders_flag\nType:$order_type\nTracking:$in{'tracking'}\nFrom:$in{'from_wh'}\nTo:$in{'id_warehouses'}\nShpDate:$in{'shpdate'}\nMsg:$va{'message'}\n\n";

							} else {

								print "ID:$id_orders_flag\nType:$order_type\nSkipped\n\n";
								## 

							}

							$order_type = '';
							$id_orders_flag = 0;
							delete($in{'tracking'});
							delete($in{'bulk'});
							delete($va{'message'});

						}

						###
						### ORDER INFO (Type, ID_orders)
						###
						
						if(!$id_orders_flag) {

							$id_orders_flag = $this_data{'id_orders'};
							$order_type = &load_name('sl_orders','ID_orders',int($this_data{'id_orders'}),'Ptype');

							$in{'shpdate'} = &get_sql_date() if !$in{'shpdate'};
							$in{'note'} = 'Undeliverable from Global Response' if !$in{'note'};
							
							$in{'tracking'} = $cfg{'prefixentershipment'} . int($this_data{'id_orders'}) . "\n";

							my ($sth) = &Do_SQL("SELECT IF(sl_orders.ID_warehouses > 0,sl_orders.ID_warehouses, sl_orders_datecod.ID_warehouses)
							                    FROM sl_orders INNER JOIN sl_orders_datecod USING(ID_orders)
							                    WHERE sl_orders_datecod.ID_orders = '".int($this_data{'id_orders'})."'
							                    ORDER BY ID_orders_datecod DESC LIMIT 1;");

							$in{'from_wh'} = $sth->fetchrow();

						}

						my $upc = &load_name('sl_skus','ID_sku_products',int($this_data{'id_skus'}),'upc');
						if($upc) {
							for (1..$this_data{'qty'}) {
								$in{'tracking'} .= $upc ."\n";
							}
						}else{
							## TODO: Enviar notif (Item sin UPC)
						}
				

					}elsif($this_data{'global_status'} eq 'PB') {

						## Partial Backorder

					}elsif($this_data{'global_status'} eq 'BO') {

						## Back Order

					}elsif($this_data{'global_status'} eq 'PS') {

						## In fulfillment

					}elsif(!$this_data{'global_status'}) {

						## Not Shipped

					}

				}else{

					print "No encontre datos para " . join(', ', @line_data) . "\n";
					push(@orders_data_error, join(', ', @line_data) . "\n" );

				}
				
			}
			
		}

        ### Moving the file to Backup
		print "Moving $inbound_file_path$file_name to $executed_file_path$file_name\n\n";
		move($inbound_file_path . $file_name, $executed_file_path . $file_name);
		print "Sleeping 15 seconds\n\n";
		sleep(15);

		print "Enviando correo desde ". $executed_file_path . $file_name ."\n\n";
		if(-e $executed_file_path . $file_name) {

			## Email Config
			my $from_mail = "rbarcenas\@inovaus.com";
			my $to_mail_atc1 = "cjmendoza\@inovaus.com";
			my $to_mail_atc2 = "rgomezm\@inovaus.com";
			my $to_mail_atc3 = "nsanchez\@inovaus.com";
			my $to_mail_wh1 = "ajimenez\@inovaus.com";
			my $to_mail_wh2 = "htercero\@inovaus.com";
			my $to_mail_wh3 = "rolascoaga\@inovaus.com";
			my $to_mail_dev1 = "rbarcenas\@inovaus.com";
			my $subject_mail = 'Global Tracking Numbers File';
			my $body_mail = 'Enviando archivo ' . $file_name;

	    	#From,To,CC,BCC,Subject,Body,Attachment
			my $this_msg1 = &send_lite_mail($from_mail,$to_mail_atc1,'','',$subject_mail, $body_mail, $executed_file_path . $file_name);
			my $this_msg2 = &send_lite_mail($from_mail,$to_mail_atc2,'','',$subject_mail, $body_mail, $executed_file_path . $file_name);
			my $this_msg3 = &send_lite_mail($from_mail,$to_mail_atc3,'','',$subject_mail, $body_mail, $executed_file_path . $file_name);
			my $this_msg4 = &send_lite_mail($from_mail,$to_mail_wh1,'','',$subject_mail, $body_mail, $executed_file_path . $file_name);
			my $this_msg5 = &send_lite_mail($from_mail,$to_mail_wh2,'','',$subject_mail, $body_mail, $executed_file_path . $file_name);
			my $this_msg5 = &send_lite_mail($from_mail,$to_mail_wh3,'','',$subject_mail, $body_mail, $executed_file_path . $file_name);
			my $this_msg6 = &send_lite_mail($from_mail,$to_mail_dev1,'','',$subject_mail, $body_mail, $executed_file_path . $file_name);

	    	print "Sending File $file_name to $to_mail_atc1, $to_mail_atc2, $to_mail_wh1, $to_mail_wh2, $to_mail_dev1...";
	    }

        print "\n\n\n\n";
        #last FILE;
    }

    my ($str_ok, $str_error);
    $str_ok .= "Ordenes Procesadas: " . scalar @orders_ok . "\n";
    $str_ok .= "Ordenes WS: " . scalar @orders_ws . "\n";
    $str_ok .= "Ordenes RT OK: " . scalar @orders_rt_ok . "\n";


	$str_error .= "Ordenes No OK: " . scalar @orders_error . "\n";
    $str_error .= "Ordenes RT Returns: " . scalar @orders_rt_returns . "\n";
	$str_error .= "Ordenes RT No OK: " . scalar @orders_rt_error . "\n";
	$str_error .= "Ordenes No Data: " . scalar @orders_data_error . "\n";	

	print $str_ok . "\n\n" . $str_error;


	#### Sending Emails
	if( scalar @orders_ok or scalar @orders_ws or scalar @orders_rt_ok ){
		&send_text_mail("rbarcenas\@inovaus.com","rbarcenas\@inovaus.com","Tracking Numbers Global ","\n#############\nOrdenes OK\n#############\n\n" . join("\n\n",@orders_ok) . "\n\n\n#############\nOrdenes Wholesale (No procesadas)\n#############\n\n" . join("\n\n",@orders_ws) . "\n\n\n#############\nOrdenes RT\n#############\n\n" . join("\n\n",@orders_rt_ok) . "\n\n\n#############\nResume\n#############\n\n ". $str_ok );
		&send_text_mail("rbarcenas\@inovaus.com","jestrada\@inovaus.com","Tracking Numbers Global ","\n#############\nOrdenes OK\n#############\n\n" . join("\n\n",@orders_ok) . "\n\n\n#############\nOrdenes Wholesale (No procesadas)\n#############\n\n" . join("\n\n",@orders_ws) . "\n\n\n#############\nOrdenes RT\n#############\n\n" . join("\n\n",@orders_rt_ok) . "\n\n\n#############\nResume\n#############\n\n ". $str_ok );
	}

	if(scalar @orders_error or scalar @orders_rt_returns or scalar @orders_error) {
		&send_text_mail("rbarcenas\@inovaus.com","cjmendoza\@inovaus.com","Errores File Global Response","\r\n\nOrdenes con Errores en Datos:\n" . join("\n\n",@orders_error) . "\n\n\n#############\nOrdenes RT Error\n#############\n\n" . join("\n\n",@orders_rt_error) . "\n\n\n#############\nOrdenes RT Returns\n#############\n\n" . join("\n\n",@orders_rt_returns) . "\n\n\n#############\nLineas sin Order\n#############\n\n" . join("\n\n",@orders_data_error) ." \n\n\n#############\nResume\n#############\n\n ". $str_ok . "\n\n ". $str_error );
		&send_text_mail("rbarcenas\@inovaus.com","rgomezm\@inovaus.com","Errores File Global Response","\r\n\nOrdenes con Errores en Datos:\n" . join("\n\n",@orders_error) . "\n\n\n#############\nOrdenes RT Error\n#############\n\n" . join("\n\n",@orders_rt_error) . "\n\n\n#############\nOrdenes RT Returns\n#############\n\n" . join("\n\n",@orders_rt_returns) . "\n\n\n#############\nLineas sin Order\n#############\n\n" . join("\n\n",@orders_data_error) ." \n\n\n#############\nResume\n#############\n\n ". $str_ok . "\n\n ". $str_error );
		&send_text_mail("rbarcenas\@inovaus.com","htercero\@inovaus.com","Errores File Global Response","\r\n\nOrdenes con Errores en Datos:\n" . join("\n\n",@orders_error) . "\n\n\n#############\nOrdenes RT Error\n#############\n\n" . join("\n\n",@orders_rt_error) . "\n\n\n#############\nOrdenes RT Returns\n#############\n\n" . join("\n\n",@orders_rt_returns) . "\n\n\n#############\nLineas sin Order\n#############\n\n" . join("\n\n",@orders_data_error) ." \n\n\n#############\nResume\n#############\n\n ". $str_ok . "\n\n ". $str_error );
		&send_text_mail("rbarcenas\@inovaus.com","rolascoaga\@inovaus.com","Errores File Global Response","\r\n\nOrdenes con Errores en Datos:\n" . join("\n\n",@orders_error) . "\n\n\n#############\nOrdenes RT Error\n#############\n\n" . join("\n\n",@orders_rt_error) . "\n\n\n#############\nOrdenes RT Returns\n#############\n\n" . join("\n\n",@orders_rt_returns) . "\n\n\n#############\nLineas sin Order\n#############\n\n" . join("\n\n",@orders_data_error) ." \n\n\n#############\nResume\n#############\n\n ". $str_ok . "\n\n ". $str_error );
		&send_text_mail("rbarcenas\@inovaus.com","jestrada\@inovaus.com","Errores File Global Response","\r\n\nOrdenes con Errores en Datos:\n" . join("\n\n",@orders_error) . "\n\n\n#############\nOrdenes RT Error\n#############\n\n" . join("\n\n",@orders_rt_error) . "\n\n\n#############\nOrdenes RT Returns\n#############\n\n" . join("\n\n",@orders_rt_returns) . "\n\n\n#############\nLineas sin Order\n#############\n\n" . join("\n\n",@orders_data_error) ." \n\n\n#############\nResume\n#############\n\n ". $str_ok . "\n\n ". $str_error );
		&send_text_mail("rbarcenas\@inovaus.com","rbarcenas\@inovaus.com","Errores File Global Response","\r\n\nOrdenes con Errores en Datos:\n" . join("\n\n",@orders_error) . "\n\n\n#############\nOrdenes RT Error\n#############\n\n" . join("\n\n",@orders_rt_error) . "\n\n\n#############\nOrdenes RT Returns\n#############\n\n" . join("\n\n",@orders_rt_returns) . "\n\n\n#############\nLineas sin Order\n#############\n\n" . join("\n\n",@orders_data_error) ." \n\n\n#############\nResume\n#############\n\n ". $str_ok . "\n\n ". $str_error );
		&send_text_mail("rbarcenas\@inovaus.com","chaas\@inovaus.com","Errores File Global Response","\r\n\nOrdenes con Errores en Datos:\n" . join("\n\n",@orders_error) . "\n\n\n#############\nOrdenes RT Error\n#############\n\n" . join("\n\n",@orders_rt_error) . "\n\n\n#############\nOrdenes RT Returns\n#############\n\n" . join("\n\n",@orders_rt_returns) . "\n\n\n#############\nLineas sin Order\n#############\n\n" . join("\n\n",@orders_data_error) ." \n\n\n#############\nResume\n#############\n\n ". $str_ok . "\n\n ". $str_error );
	}

}


#############################################################################
#############################################################################
#   Function: set_error_note
#
#       Es: Genera una nota de error de escaneo en la orden
#       En: 
#
#    Created on: 12/21/2012  11:20:10
#
#    Author: _Roberto Barcenas_
#
#    Modifications:
#
#   Parameters:
#
#       - id_orders : ID_orders
#		- shpdate/from_wh : shpdate in SH type / from_wh in RT type
#		- tracking: Tracking info passed to entershipment / cod_receipt functions
#		- type : SH for Shipp / RT for Return
#
#  Returns:
#
#   See Also:
#
#
#
sub set_error_note {
#############################################################################
#############################################################################

	my($id_orders, $d, $tracking, $type) = @_;
	my ($mod) = $type eq 'SH' ? "ShpDate: $d\n" : "Driver: ".&load_name('sl_warehouses','ID_warehouses',$d,'Name'). " ($d)\n"; 

	## Nota entershipment/cod_receipt error
	my ($sth) = &Do_SQL("INSERT INTO sl_orders_notes SET Notes='$mod".&filter_values($tracking)."',Type='$type',Date=CURDATE(),Time=CURTIME(),ID_admin_users='1', ID_orders='$id_orders';");
	&add_order_notes_by_type($id_orders,'$mod".&filter_values($tracking)."',"$type");
}


#############################################################################
#############################################################################
#   Function: authnumber
#
#       Es: Genera un numero de autorizacion para procesar ordenes
#       En: 
#
#    Created on: 07/10/2008  16:21:10
#
#    Author: _Roberto Barcenas_
#
#    Modifications:
#
#   Parameters:
#
#     - id_orders : ID_orders
#
#  Returns:
#
#   See Also:
#
#
#
sub authnumber {
#############################################################################
#############################################################################

	$usr{'id_admin_users'} = 1;
	my $num=int(rand 10000);
	my $cad=sprintf ("%.04d",$num);
	&Do_SQL("UPDATE sl_vars SET VValue= ('".$usr{'id_admin_users'}.",".$cad."') where VNAME='Authorization Code'");
	&auth_logging('var_updated',"");
	return $cad;

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