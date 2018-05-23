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
local ($in{'e'}) = 2;
local ($usr{'id_admin_users'}) = 1;
local ($in{'batch_forced'}) = 1;
local ($cfg{'ida_banks'}) = '19,24,26,30';
local ($cfg{'ida_bankscd'}) = '207,211,613,215';
local ($cfg{'ida_bankfees'}) = '127,571';
local ($cfg{'ida_sales'}) = '354,355';
local ($cfg{'ida_bank_default'}) = 24; 
local ($cfg{'ida_customer_ar'}) = '76,79';
local ($cfg{'ida_tax_payable'}) = '264';
local ($cfg{'ida_tax_paid'}) = '265';
local ($cfg{'ida_diff'}) = '610';
local ($cfg{'tax_pct'}) = .16;
local ($cfg{'tax_shp'}) = 20.68;
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
	&process_scan;
	&disconnect_db;

}


#############################################################################
#############################################################################
#   Function: process_scan
#
#       Es: Procesa archivo de bills para transicion
#       En: 
#
#    Created on: 07/10/2008  16:21:10
#
#    Author: _RB_
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
sub process_scan {
#############################################################################
#############################################################################
	


	my ($query_f) = "SELECT ID_orders,GROUP_CONCAT(ID_orders_products),GROUP_CONCAT(tmp.UPC), Ptype, sl_orders.Status, sl_orders.Date
					FROM sl_orders INNER JOIN sl_orders_products USING(ID_orders)
					INNER JOIN sl_skus ON sl_orders_products.ID_products = ID_sku_products
					INNER JOIN sl_skus_parts USING(ID_sku_products)
					INNER JOIN
					(
						SELECT ID_products, UPC FROM sl_skus WHERE 1
						AND LENGTH(UPC) > 2 /*AND CAST(UPC AS UNSIGNED) = 0*/
					)tmp
					ON sl_skus_parts.ID_parts = tmp.ID_products
					WHERE sl_orders.Status IN('Pending','Processed','Shipped','Cancelled')
					AND sl_orders_products.Status = 'Active'
					AND LEFT(sl_orders_products.ID_products,1) < 4
					GROUP BY sl_orders.ID_orders
					ORDER BY sl_orders.ID_orders;";

	#print "/*Query Inicial */ \n$query_f\n\n"; #9041969,9041999,9042214,9043892,9049288
	my ($sth) = &Do_SQL($query_f);

	my $i=0;
	SCAN: while (my ( $id_orders, $idop, $upcs, $ptype, $st, $d  ) = $sth->fetchrow() ) {
		
		++$i;

		my ($sth2) = &Do_SQL("SELECT COUNT(*) FROM sl_orders_products INNER JOIN sl_orders_parts USING(ID_orders_products) WHERE ID_orders = '$id_orders';");
		my ($ts) = $sth2->fetchrow();

		###########
		########### Determinamos el Batch correcto
		###########
		my ($sthw) = &Do_SQL("/* $id_orders - $st */
							SELECT ID_warehouses_batches, ID_warehouses
							FROM `sl_orders_products` 
							INNER JOIN sl_warehouses_batches_orders 
							USING(ID_orders_products)
							INNER JOIN sl_warehouses_batches
							USING(ID_warehouses_batches)
							WHERE ID_orders = '$id_orders' 
							GROUP BY sl_warehouses_batches.ID_warehouses_batches, sl_warehouses_batches_orders.Status
							ORDER BY 
							FIELD(sl_warehouses_batches_orders.Status, 'Shipped', 'Returned', 'In Fulfillment')
							LIMIT 1;");
		my ($id_whb, $idwh) = $sthw->fetchrow();

		if($ts){
			#print "$id_orders|$upcs|$ptype|$st|$d|Sent\n";

			my @ary = split(/,/, $idop);
			my $ok = 0;
			my $ok2 = 0;
			my $action;

			for(0..$#ary){

				my $this_idop = int($ary[$_]);
				my ($sth3) = &Do_SQL("SELECT COUNT(*) FROM sl_orders_products INNER JOIN sl_orders_parts USING(ID_orders_products) WHERE ID_orders_products = '$this_idop';");
				
				if($sth3->fetchrow > 0){ 
					$ok++; 

				}else{

					
					####################################
					####################################
					####################################
					#########
					######### Producto no enviado
					#########
					####################################
					####################################
					####################################

					if($ptype eq 'COD'){


						if($st eq 'Shipped'){

							########
							######## a) Salida de Mercancia (Mov Contables de inventario?)
							########
							$action = 'out';

						}elsif($st eq 'Cancelled'){

							########
							######## b) Solo marcado de datos en sl_orders_products + sl_orders_parts pero no traspaso
							########
							$action = 'marked';

						}else{

							########
							######## c) Traspaso de Mercancia al almacen del chofer
							########
							$action = 'assigned';

						}

					}else{

						########
						######## a) Salida de Mercancia (Mov Contables de inventario?)
						########
						$action = 'out';

					}

					$ok2 += &scan_this($id_orders,$this_idop,$idwh,$action);

					####
					#### Confirmacion de linea enviada en Batch
					####
					&warehouses_batches_confirm($id_orders, $this_idop, $id_whb);


				}

			}

			print "$id_orders|$ptype|$st|$d|".scalar @ary."|$ok|$ok2|";
			if($ok < scalar @ary){
				print "Partial|$action\n";
				#exit;
			}else{
				print "Sent|Skipped\n";
			}


		}else{
			next SCAN;
			print "Skipped\n";
		}

	}


}



#############################################################################
#############################################################################
#   Function: scan_this
#
#       Es: Hace envio de la mercancia
#       En: 
#
#
#    Created on: 06/01/2013
#
#    Author: _Roberto Barcenas_
#
#    Modifications:
#
#   Parameters:
#
#       - id_orders_products: 
#		- type
#
#
#  Returns:
#
#      - 
#
#   See Also:
#
#
sub scan_this{
#############################################################################
#############################################################################

	my ($id_orders, $id_orders_products, $idvirtual, $this_action) = @_;


		my $id_warehouses = 1001;
		my $ok = 0;

		my ($sth2) = &Do_SQL("SELECT ShpDate, ShpProvider FROM sl_orders_products WHERE ID_orders = '$id_orders' AND ShpDate IS NOT NULL AND ShpDate <> '' AND ShpDate <> '0000-00-00' ORDER BY ShpDate LIMIT 1;");
		my ($shpdate,$shpprovider) = $sth2->fetchrow();

		my ($sthv) = &Do_SQL("/* $id_orders, $id_orders_products, $this_action */ 
							SELECT 400000000 + ID_parts, SUM(sl_orders_products.Quantity * Qty)
							FROM sl_orders_products INNER JOIN sl_skus ON ID_sku_products = sl_orders_products.ID_products
							INNER JOIN sl_skus_parts USING(ID_sku_products) 
							WHERE ID_orders_products = '$id_orders_products' 
							AND sl_orders_products.Status = 'Active'
							AND (sl_orders_products.Cost IS NULL OR sl_orders_products.Cost = '' OR sl_orders_products.Cost = 0)
							AND 1 > (SELECT COUNT(*) FROM sl_orders_parts WHERE ID_orders_products = '$id_orders_products' )
							GROUP BY ID_parts
							ORDER BY ID_parts;");

		while(my($id_parts, $qty) = $sthv->fetchrow()){

				#'out','marked','assigned'
			my $status = 'ok';
			my ($sth,$pcost);
			$sth = &Do_SQL("SELECT Cost FROM sl_skus_cost WHERE ID_products = '".$id_parts."' AND ID_warehouses='".$id_warehouses."' AND Quantity > 0 $mod_pack ORDER BY Date $invout_order LIMIT 1");
			$pcost = $sth->fetchrow();
			$pcost = load_sltvcost($id_parts) if !$pcost;

			if($this_action eq 'assigned') {

				my $status = &transfer_warehouses($id_warehouses,$idvirtual,$id_parts,$qty);
				
			}

			if($status ne 'error'){

				++$ok;
				$sth = &Do_SQL("INSERT INTO sl_orders_parts SET Tracking='12345',Cost='$pcost',ShpDate='$shpdate',ShpProvider='$shpprovider',ID_orders_products='$id_orders_products',ID_parts='$id_parts',Status='Shipped',Quantity='$qty',Date=CURDATE(),Time=CURTIME(),ID_admin_users='$usr{'id_admin_users'}';");

			}

		}

		####### Movimientos de contabilidad
		#######
		my ($order_type, $ctype, $ptype,@params);
		my ($sth) = &Do_SQL("SELECT Ptype, Type FROM sl_orders INNER JOIN sl_customers USING(ID_customers) WHERE ID_orders = '$id_orders';");
		($order_type, $ctype) = $sth->fetchrow();

		my @params = ($id_orders, $id_orders_products);
		&accounting_keypoints('order_products_inventoryout_'. $ctype .'_'. $order_type, \@params );
		&Do_SQL("UPDATE sl_movements INNER JOIN 
				(
					SELECT ID_tableused,EffDate FROM sl_movements WHERE ID_tableused = '$id_orders' AND tableused = 'sl_orders'
					AND EffDate < CURDATE() LIMIT 1
				)tmp
				USING(ID_tableused)
				SET sl_movements.EffDate = tmp.EffDate
				WHERE ID_tableused = '$id_orders' AND sl_movements.EffDate = CURDATE();")	;
			

		#if (&check_kit_shipped($id_orders_products,'orders') eq 'OK'){

			my ($sth) = &Do_SQL("SELECT SUM(Quantity*Cost) FROM sl_orders_parts WHERE ID_orders_products = '$id_orders_products' ");	
			my ($tot_cost) = $sth->fetchrow();
			my ($sth) = &Do_SQL("UPDATE sl_orders_products SET ShpProvider='By Parts',Tracking='N/A',Cost='$tot_cost',ShpDate='$shpdate' WHERE ID_orders_products='$id_orders_products'");
			&auth_logging('orders_products_updated',$id_orders);

		#}


		return 1 if $ok;
		#}else{
		#	&write_to_list('No_Stock','orders',3000,0,$id_orders,'sl_orders');
		#	&Do_SQL("INSERT INTO sl_orders_notes SET Notes='Bad Quantity in From:$id_warehouses To:$idvirtual Product: $id_parts',Type='High',Date=CURDATE(),Time=CURTIME(),ID_admin_users='$usr{'id_admin_users'}', ID_orders='$id_orders';");
		#}



}



#############################################################################
#############################################################################
#   Function: warehouses_batches_confirm
#
#       Es: Hace envio de la mercancia
#       En: 
#
#
#    Created on: 06/01/2013
#
#    Author: _Roberto Barcenas_
#
#    Modifications:
#
#   Parameters:
#
#       - id_orders_products: 
#		- type
#
#
#  Returns:
#
#      - 
#
#   See Also:
#
#
sub warehouses_batches_confirm{
#############################################################################
#############################################################################


	my ($id_orders, $idop, $idwhb) = @_;
	my $total = 0;

	if($id_orders) {

		###
		### 1) Status / Date for this Order
		my ($sth1) = &Do_SQL("SELECT sl_warehouses_batches_orders.Status, sl_warehouses_batches_orders.Date,
							sl_warehouses_batches_orders.Time 
							FROM sl_warehouses_batches_orders INNER JOIN sl_orders_products USING(ID_orders_products) 
							WHERE ID_warehouses_batches = '$idwhb'
							AND ID_orders = '$id_orders' ORDER BY LEFT(ID_products,1) LIMIT 1;");
		my ($r_st, $r_date, $r_time) = $sth1->fetchrow();


		###
		### 2) Deactivate other batch products
		my ($sth2) = &Do_SQL("/* $id_orders, $idop, $idwhb */
							UPDATE `sl_orders_products` 
							INNER JOIN sl_warehouses_batches_orders
							USING ( ID_orders_products ) 
							SET sl_warehouses_batches_orders.Status = 'Cancelled'
							WHERE sl_warehouses_batches_orders.ID_orders_products = '$idop' 
							AND ID_warehouses_batches <> '$idwhb'
							AND sl_warehouses_batches_orders.Status NOT IN('Returned','Error');");

		my ($total) = $sth2->rows();

		###
		### 3) Confirming Products
		my ($sth3) = &Do_SQL("UPDATE sl_warehouses_batches_orders SET Status = '$r_st' WHERE ID_warehouses_batches = '$idwhb' AND ID_orders_products = '$idop';");
		$total = $sth3->rows();

		if(!$total){

			my ($sth4) = &Do_SQL("INSERT IGNORE INTO sl_warehouses_batches_orders
								SELECT 0,$idwhb,ID_orders_products,0,'$r_st','$r_date','$r_time','$usr{'id_admin_users'}'
								FROM sl_orders_products
								WHERE ID_orders_products = '$idop' AND Status NOT IN ('Returned','Order Cancelled','Inactive');");
			$total = $sth4->rows();
		}

		&auth_logging('order_batchreasigned', $idwhb);


	}


}



#############################################################################
#############################################################################
#   Function: accounting_group_amounts
#
#       Es: Agrupa montos por cuenta contable
#       En: 
#
#
#    Created on: 06/01/2013
#
#    Author: _Roberto Barcenas_
#
#    Modifications:
#
#   Parameters:
#
#       - tableused: 
#		- id_tableused
#
#
#  Returns:
#
#      - 
#
#   See Also:
#
#
sub accounting_group_amounts{
#############################################################################
#############################################################################

	my ($tableused, $id_tableused) = @_;

	my ($sth) = &Do_SQL("SELECT ID_accounts,Credebit,Amount,movs,ID_movs FROM
						(
							SELECT ID_accounts,Credebit,COUNT(*)AS movs,SUM(Amount)AS Amount, GROUP_CONCAT(ID_movements)AS ID_movs FROM sl_movements WHERE tableused = '$tableused' AND ID_tableused = '$id_tableused' AND Status = 'Active' AND (ID_journalentries IS NULL OR ID_journalentries = 0) 
							GROUP BY ID_accounts,ID_tablerelated,tablerelated,Credebit,EffDate
						)tmp
						HAVING movs > 1 ORDER BY Credebit,ID_accounts;");
	while(my ($id_accounts, $credebit, $amount, $movs, $ids) = $sth->fetchrow() ){

		my @ary = split(/,/, $ids);
		my $i=0;

		for (0..$#ary){

			my $id_movements = int($ary[$i]);
			if($i == 0){
				&Do_SQL("UPDATE sl_movements SET Amount = '$amount' WHERE ID_movements = '$id_movements';");
			}else{
				&Do_SQL("DELETE FROM sl_movements WHERE ID_movements = '$id_movements';");
			}

			$i++;
		}

	}

	return;
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
