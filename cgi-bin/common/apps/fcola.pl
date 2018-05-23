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
local (%in);

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
	$in{'e'} = 1;
	&connect_db;
	&process_file;
	&disconnect_db;

}


#############################################################################
#############################################################################
#   Function: process_file
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
sub process_file {
#############################################################################
#############################################################################
	
	#print "Content-type: text/html\n\n";

	my $inbound_file_path = $cfg{'path_upfiles'};

	$usr{'id_admin_users'} = 1;
	$in{'action'} = 1; #
	$in{'e'} = 1;
	$in{'fc_dropshipp_return'} = 1; ## Indica a entershipment proceso externo
	$in{'id_warehouses'} = 1050; ## Warehouse Global
	my $id_warehouses_damage = 1052; ## Warehouse Damage Global
	my @cols = ('id_orders','shp_date','tracking_number');

	my @orders_ok;
	my @orders_error;

	opendir (my $fdir, $inbound_file_path) || &cgierr('Unable to open directory ' . $inbound_file_path ,704,$!);
	@files = readdir($fdir);# Read in list of files in directory..
	closedir ($fdir);


	##### Looping files
	FILE: foreach my $file_name (sort @files) {

		next if ($file_name !~ /^fcola.txt$/);		# Skip no "." and ".." entries..

		print "Intentando abrir el archivo " . $inbound_file_path . $file_name  . "\n";

		##### Open File
		my $i=0;
		my $is_wholesale;
		my $order_type;
		my $cod_driver;
		my $this_msg;


		if (-e  $inbound_file_path . $file_name) {

			open(my $this_file, "<", $inbound_file_path . $file_name) or &cgierr('Unable to open file: '. $inbound_file_path . $file_name, 601,$!);

			print "Ejecutando ordenes en el archivo...\n\n";

			LINE: while (<$this_file>) {
				++$i;
				$line = $_;
				next LINE if $line =~ /^#/;
				$line =~ s/\r|\n|//g;
				#print "$i - $line\n\n";

				my %this_data;
				my ($item_status);
				my @line_data = split(/,/);
				for (0..$#line_data) {

					$line_data[$_] =~ s/\r|\n|\"//g;
					$line_data[$_] =~ s/^\s+//;
					$line_data[$_] =~ s/\s+$//;

					$this_data{$cols[$_]} = $line_data[$_];
				}
				$this_data{'id_orders'} = int($this_data{'id_orders'});

				if($this_data{'id_orders'} and $this_data{'shp_date'} and $this_data{'tracking_number'}) {

					$this_data{'shp_method'} = $this_data{'tracking_number'} =~ /^1Z/ ? 'UPS' : 'USPS';
					$in{'tracking'} = 'IU' . $this_data{'id_orders'} . "\n" . $this_data{'shp_method'} . "-" . $this_data{'tracking_number'} . "\n";
					my $status = &load_name('sl_orders','ID_orders',$this_data{'id_orders'},'Status');

					if($status eq 'Processed') {

						my ($sth) = &Do_SQL("SELECT UPC,SUM(Qty)
										FROM sl_orders_products 
										INNER JOIN sl_skus_parts 
										ON sl_orders_products.ID_products = sl_skus_parts.ID_sku_products 
										INNER JOIN sl_skus ON sl_skus.ID_products = ID_parts
										WHERE ID_orders = '$this_data{'id_orders'}'
										AND sl_orders_products.Status IN('Active','Exchange','Reship') AND SalePrice >= 0
										GROUP BY ID_parts ORDER BY ID_parts ;");

						while(my($upc,$qty) = $sth->fetchrow()) {

							for(1..$qty) {
								$in{'tracking'} .= $upc . "\n";
							}

						}
						$in{'authcode'} = &authnumber;
						$in{'shpdate'} = substr($this_data{'shp_date'},0,10);
						my $order_type = &load_name('sl_orders','ID_orders',int($this_data{'id_orders'}),'Ptype');
						($order_type eq 'COD' or !$this_data{'tracking_number'}) and ($in{'localdelivery'} = 1);
						#($order_type ne 'COD') and ($in{'bulk'} = 1);

						if($order_type eq 'COD') {
							my ($cod_driver);
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


						print "ID:$this_data{'id_orders'}\nType:$order_type\nTracking:$in{'tracking'}\nShpDate:$in{'shpdate'}\nAuth:$in{'authcode'}\n";
						&entershipment();

						$va{'message'} =~ s/<li>//g;
						$va{'message'} =~ s/<\/li>/\n/g;			
						print $va{'message'} . "\n\n";

						## Scan Message
						if($va{'message'} =~ /\d+ pieces scanned/) {
							
							push(@orders_ok, "Order:$this_data{'id_orders'}\n$va{'message'}");
							my ($sth) = &Do_SQL("UPDATE sl_orders SET StatusPrd='None' WHERE ID_orders = '".int($this_data{'id_orders'})."';");

						}else{

							my ($sth) = &Do_SQL("SELECT COUNT(*) FROM sl_orders_products WHERE ID_orders = '$this_data{'id_orders'}' AND SalePrice >= 0 
												AND Status NOT IN('Order Cancelled','Inactive','Returned')
												AND ID_products NOT LIKE '6%' 
												AND (ISNULL(ShpDate) or ShpDate='0000-00-00' or ShpDate='') 
												AND (ISNULL(Tracking) or Tracking='')
												AND sl_orders_products.SalePrice>0;");
							my ($tosent) = $sth->fetchrow();

							if($tosent) {
								&set_error_note($this_data{'id_orders'},$in{'shpdate'},$in{'tracking'},'SH');
								push(@orders_error, "Order:$this_data{'id_orders'}\nType:$order_type\nShpDate:$in{'shpdate'}\nTracking:$in{'tracking'}\n$va{'message'}");
							}

						}

						delete($va{'message'});
						delete($in{'shpdate'});
						delete($in{'tracking'});
						delete($in{'bulk'});
						delete($in{'localdelivery'});
						delete($in{'authcode'});
						$order_type = '';
						$cod_driver = 0;

					} ## Order Proccesed
					else{
						push(@orders_error, "Order:$this_data{'id_orders'}\nStatus Not Proccesed");
					}	

				} ## data wright
				
			}## each line}


			### Moving the file to Backup
			print "Moving $inbound_file_path$file_name to $inbound_file_path$file_name.ini\n\n";
			move($inbound_file_path . $file_name, $executed_file_path . $file_name . '.ini');
			print "Sleeping 5 seconds\n\n";
			sleep(5);

			my ($str_ok, $str_error);
    		$str_ok .= "Ordenes Procesadas: " . scalar @orders_ok . "\n";
    		$str_error .= "Ordenes No OK: " . scalar @orders_error . "\n";
			
    		&send_text_mail("rbarcenas\@inovaus.com","rbarcenas\@inovaus.com","File Colageina Results ","\n#############\nOrdenes OK\n#############\n\n" . join("\n\n",@orders_ok) . "Ordenes con Errores en Datos:\n" . join("\n\n",@orders_error) . "\n\n\n############\nResume\n#############\n\n ". $str_ok . "\n" . $str_error );


		} ## file exists

    } ## each file

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
	&add_order_notes_by_type($id_orders,'$mod".&filter_values($tracking)."',$type);
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