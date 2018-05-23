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
use Switch;
# use File::Copy;

# local ($dir) = getcwd;
# Default la 2 porque este proceso fue diseñado para TMK
# local(%in) = &parse_form;
local ($in{'e'}) = 2 if (!$in{'e'});
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
	&kardex;
	&disconnect_db;

}


#################################################################
#################################################################
#	Function: kardex
#
#	Created by: ISC Alejandro Diaz
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
sub kardex{
#################################################################
#################################################################

	&load_settings;

	print "Content-type: text/html\n\n";
	# print qq|<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN"   "http://www.w3.org/TR/html4/loose.dtd">
	# 		 <meta http-equiv="content-type" content="text/html; charset=utf-8" />\n\n|;
	# print qq|<title>Warehouses Manager :: Kardex</title>\n\n|;

	# print qq|
	# <STYLE TYPE="text/css">
	# h1 {
	# 	font-family: century gothic;
	#     display: block;
	#     font-size: 45px;
	#     margin: 0px;
	#     font-weight: normal;
	#     line-heigth:45px;
	# }
	# h2 {
	# 	font-family: century gothic;
	#     display: block;
	#     font-size: 25px;
	#     margin: 0px;
	#     margin-bottom:15px;
	#     font-weight: normal;
	# }
	# .hoverTable tr:hover 
	# {
	#           background-color: #dddddd;
	#         }



	# #cuadros td {
	#      border-right: 1px solid #777777; border-bottom: 1px solid #777777;
	#         }
	# a:link {
	# 	text-decoration:none;
	# 	color: #666;
	# }
	# a:hover {
	# 	text-decoration:underline;
	# 	color: #409CD8;
	# }    
	 

	# 	</STYLE>
	# </head>
	# <body>
	# |;	

	print qq|<div align="center">|;
	print qq|<h2>e$in{'e'} - |.uc($cfg{'app_title'}).qq| $cfg{'dbi_db'}|.qq| $cfg{'dbi_host'}</h2>|;
	print qq|<h2>K A R D E X</h2>|;
	print qq|</div>|;
	
	if (!&check_permissions('rep_fin_kardex','','')) {
		print qq|<span style="color:red;">|.&trans_txt('unauth_action').qq|</span>|;
		return;
	}

	# if (!$cfg{'acc_inventoryout_method_cost'} or $cfg{'acc_inventoryout_method_cost'} ne 'average') {
	# 	print qq|<span style="color:red;">Feature not available</span>|;
	# 	return;
	# }
	
	if (!$in{'e'}){
		print qq|<span style="color:red;">ID de empresa es requerido</span>|;
		return;
	}

	### Config. para el guardado del csv
	my $file_path = $cfg{'path_upfiles'}. 'e'.$in{'e'} . '/fix_inventory/';
	### Encabezado para los archivos
	# my $result_csv = qq|"SKU","UPC","PRODUCTO","INV. AL CIERRE DE OCT 2015","INV. AL CORTE EN SISTEMA","INV. AL CORTE POR ANALSIS"|."\n";
	my $result_csv = "SKU,UPC,Inv. Inicial,Entradas,Total Entradas,Salidas,Total Salidas,Inv. Calculado,Inv. Direksys,Observaciones\n";
	my $result_csv_details = "SKU,ALMACEN,GAVETA,FECHA,ID TRANS.,TRANSACION,TIPO,EXIST. INICIAL,CANTIDAD,EXIST. FINAL\n";

	## Revisando inventarios al cierre de Octubre 2015
	## 400005673 -> BODY CRUNCH EVOLS
	my $sql = "SELECT
					Product AS ID_products
					, UPC
					, SUM(Quantity) AS Quantity
					, Avg_Cost AS Cost
				FROM warehouse_20151031
				WHERE 1
					AND Product IN (400001178)
				GROUP BY Product 
				ORDER BY Product 
				-- LIMIT 50";
	my $sth = &Do_SQL($sql);
	while(my $rec_inv_oct = $sth->fetchrow_hashref()){
		
		my $inv_original = $rec_inv_oct->{'Quantity'};
		my $id_products = $rec_inv_oct->{'ID_products'};
		my $upc_products = $rec_inv_oct->{'UPC'};

		my $notes = '';
		$result_csv .= $id_products.','.$upc_products.','.$inv_original.',';

		my $count_in = 0;
		my $count_out = 0;
		my $qty_in = 0;
		my $qty_out = 0;


		## Recorrido de productos
		print qq|$rec_inv_oct->{'ID_products'} ***  $rec_inv_oct->{'Quantity'} *** $rec_inv_oct->{'Cost'} -+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+<br>|;

		$sql = "SELECT 
					sl_skus_trans.tbl_name
					, sl_skus_trans.ID_trs
					, sl_skus_trans.Type
					, sl_skus_trans.Date
					, sl_skus_trans.ID_warehouses
					, sl_skus_trans.Location
				FROM sl_skus_trans 
				WHERE Date >= '2015-11-01' /*AND Date < '2015-12-01'*/ AND ID_products = ".$id_products."
				GROUP BY sl_skus_trans.tbl_name,sl_skus_trans.ID_trs
				ORDER BY sl_skus_trans.ID_products_trans;";
		my $sth_skus_trans = &Do_SQL($sql);
		while(my $rec_skus_trans = $sth_skus_trans->fetchrow_hashref()){
			my $count_sl_orders=0;
			my $count_sl_wreceipts=0;
			my $count_sl_skustransfers=0;
			my $count_sl_parts_productions=0;

			# print qq|$rec_skus_trans->{'tbl_name'}<----<br>|;
			switch($rec_skus_trans->{'tbl_name'}){
				##############################################
				## sl_orders
				##############################################
				case 'sl_orders' {
					my $inv_sl_orders = 0;

					if ($rec_skus_trans->{'Type'} eq 'Sale'){
						$sql = "SELECT IFNULL(SUM(sl_orders_parts.Quantity),0)Quantity
						FROM sl_orders
						INNER JOIN sl_orders_products ON sl_orders.ID_orders=sl_orders_products.ID_orders
						INNER JOIN sl_orders_parts ON sl_orders_products.ID_orders_products=sl_orders_parts.ID_orders_products
						WHERE sl_orders.ID_orders='".$rec_skus_trans->{'ID_trs'}."'
						AND (400000000+sl_orders_parts.ID_parts)='".$rec_inv_oct->{'ID_products'}."'
						GROUP BY sl_orders_parts.ID_orders_products, sl_orders_parts.ID_parts";
						my $sth_scan = &Do_SQL($sql);
						$inv_sl_orders = $sth_scan->fetchrow_array();

						### Se genera la linea de detalles del movimiento
						$result_csv_details .= $id_products.',';
						$result_csv_details .= $rec_skus_trans->{'ID_warehouses'}.',';
						$result_csv_details .= $rec_skus_trans->{'Location'}.',';
						$result_csv_details .= $rec_skus_trans->{'Date'}.',';
						$result_csv_details .= $rec_skus_trans->{'ID_trs'}.',';
						### Linea de detalle
						$result_csv_details .= 'Sale,Out,'.$inv_original.','.$inv_sl_orders.','.($inv_original - $inv_sl_orders)."\n";

						## Como es una salida se resta
						my $inv_temp = $inv_original;
						$inv_original -= $inv_sl_orders;
						++$count_out if ($inv_sl_orders > 0);
						$qty_out += $inv_sl_orders;

						print qq|sl_orders[$rec_skus_trans->{'ID_trs'}] -> <strong>$inv_original</strong> = $inv_temp - $inv_sl_orders :: $count_out<br>| if ($inv_sl_orders > 0);

					}
					# else{
						## Type = Transfer Out
						## Es una asignacion solamente (Transferecia), realmente no debe afectar inventario
					# }
				}
				
				##############################################
				## sl_manifests - COMO SOLO GENERA MOVIMIENTOS ENTRE ALMACENES NO AFECTA EL INVENTARIO
				##############################################

				##############################################
				## sl_skustransfers
				##############################################
				case 'sl_skustransfers' {
					$sql = "SELECT
					sl_skustransfers_items.From_Warehouse
					, sl_skustransfers_items.From_Warehouse_Location
					, sl_skustransfers_items.FromSku
					, sl_skustransfers_items.To_Warehouse
					, sl_skustransfers_items.To_Warehouse_Location
					, sl_skustransfers_items.ToSku
					, sl_skustransfers_items.Qty
					, sl_skustransfers.Status
					, sl_skustransfers.Date
					FROM sl_skustransfers
					INNER JOIN sl_skustransfers_items ON sl_skustransfers_items.ID_skustransfers=sl_skustransfers.ID_skustransfers
					WHERE sl_skustransfers.ID_skustransfers='".$rec_skus_trans->{'ID_trs'}."';
					";
					my $sth_skustransfers = &Do_SQL($sql);
					my $log2;
					while (my $rec_skustransfers = $sth_skustransfers->fetchrow_hashref()){
						if ($rec_skustransfers->{'Status'} ne 'Completed'){
							#&cgierr("Problema detectado en sl_skustransfers $rec_skus_trans->{'ID_trs'} no tiene estatus Completed");
							$notes .= "Problema detectado en sl_skustransfers $rec_skus_trans->{'ID_trs'} no tiene estatus Completed<br>";
						}

						### Se genera la linea de detalles del movimiento
						$result_csv_details .= $id_products.',';
						$result_csv_details .= $rec_skus_trans->{'ID_warehouses'}.',';
						$result_csv_details .= $rec_skus_trans->{'Location'}.',';
						$result_csv_details .= $rec_skus_trans->{'Date'}.',';
						$result_csv_details .= $rec_skus_trans->{'ID_trs'}.',';

						my $inv_temp = $inv_original;
						if ($rec_skustransfers->{'FromSku'} eq $rec_inv_oct->{'ID_products'}){
							
							### Linea de detalle
							$result_csv_details .= 'Sku Transfer,Out,'.$inv_original.','.$rec_skustransfers->{'Qty'}.','.($inv_original - $rec_skustransfers->{'Qty'})."\n";

							## Como es una SALIDA se RESTA
							$inv_original -= $rec_skustransfers->{'Qty'};
							++$count_out;							
							$qty_out += $rec_skustransfers->{'Qty'};

							print qq|sl_skustransfers[$rec_skus_trans->{'ID_trs'}] -> <strong>$inv_original</strong> = $inv_temp - $rec_skustransfers->{'Qty'} :: $count_out<br>|;
							

						}elsif ($rec_skustransfers->{'ToSku'} eq $rec_inv_oct->{'ID_products'}){
							
							### Linea de detalle
							$result_csv_details .= 'Sku Transfer,In,'.$inv_original.','.$rec_skustransfers->{'Qty'}.','.($inv_original + $rec_skustransfers->{'Qty'})."\n";

							## Como es una ENTRADA se SUMA
							$inv_original += $rec_skustransfers->{'Qty'};
							++$count_in;
							$qty_in += $rec_skustransfers->{'Qty'};

							print qq|sl_skustransfers[$rec_skus_trans->{'ID_trs'}] -> <strong>$inv_original</strong> = $inv_temp + $rec_skustransfers->{'Qty'}<br>|;

						}else{
							# print qq|sl_skustransfers[$rec_skus_trans->{'ID_trs'}] -> Product Not Found<br>|;

						}
					}
				}

				##############################################
				## sl_wreceipts
				##############################################
				case 'sl_wreceipts' {

					$sql = "SELECT sl_wreceipts_items.Qty AS Quantity, sl_wreceipts.Status, sl_wreceipts.Date AS sl_wreceipts_date
					FROM sl_wreceipts 
					INNER JOIN sl_wreceipts_items ON sl_wreceipts.ID_wreceipts=sl_wreceipts_items.ID_wreceipts
					WHERE sl_wreceipts.ID_wreceipts='".$rec_skus_trans->{'ID_trs'}."' 
					AND sl_wreceipts_items.ID_products='".$rec_inv_oct->{'ID_products'}."';
					";
					my $sth_wreceipts = &Do_SQL($sql);
					while (my $rec_wreceipts = $sth_wreceipts->fetchrow_hashref()){
						if ($rec_wreceipts->{'Status'} ne 'Processed'){
							#&cgierr("Problema detectado en sl_wreceipts $rec_skus_trans->{'ID_trs'} no tiene estatus Processed");
							$notes .= "Problema detectado en sl_wreceipts $rec_skus_trans->{'ID_trs'} no tiene estatus Processed<br>";
						}

						### Se genera la linea de detalles del movimiento
						$result_csv_details .= $id_products.',';
						$result_csv_details .= $rec_skus_trans->{'ID_warehouses'}.',';
						$result_csv_details .= $rec_skus_trans->{'Location'}.',';
						$result_csv_details .= $rec_skus_trans->{'Date'}.',';
						$result_csv_details .= $rec_skus_trans->{'ID_trs'}.',';
						### Linea de detalle
						$result_csv_details .= 'W. Receipts,In,'.$inv_original.','.$rec_wreceipts->{'Quantity'}.','.($inv_original + $rec_wreceipts->{'Quantity'})."\n";

						## Como es una ENTRADA se SUMA
						my $inv_temp = $inv_original;
						$inv_original += $rec_wreceipts->{'Quantity'};
						++$count_in;
						$qty_in += $rec_wreceipts->{'Quantity'};

						print qq|sl_wreceipts[$rec_skus_trans->{'ID_trs'}] -> <strong>$inv_original</strong> = $inv_temp + $rec_wreceipts->{'Quantity'}<br>|;

					}
				}

				##############################################
				## sl_parts_productions
				##############################################
				case 'sl_parts_productions' {

					$sql = "SELECT 
					sl_parts_productions_items.Qty AS Quantity
					, sl_parts_productions_items.In_out
					, sl_parts_productions.Status
					, sl_parts_productions.Date
					FROM sl_parts_productions
					INNER JOIN sl_parts_productions_items ON sl_parts_productions.ID_parts_productions=sl_parts_productions_items.ID_parts_productions
					WHERE sl_parts_productions.ID_parts_productions='".$rec_skus_trans->{'ID_trs'}."'
					AND sl_parts_productions_items.ID_products='".$rec_inv_oct->{'ID_products'}."'
					;";
					my $sth_parts_productions = &Do_SQL($sql);
					while (my $rec_parts_productions = $sth_parts_productions->fetchrow_hashref()){
						if ($rec_parts_productions->{'Status'} ne 'Processed'){
							#&cgierr("Problema detectado en sl_parts_productions $rec_skus_trans->{'ID_trs'} no tiene estatus Processed");
							$notes .= "Problema detectado en sl_parts_productions $rec_skus_trans->{'ID_trs'} no tiene estatus Processed<br>";
						}

						### Se genera la linea de detalles del movimiento
						$result_csv_details .= $id_products.',';
						$result_csv_details .= $rec_skus_trans->{'ID_warehouses'}.',';
						$result_csv_details .= $rec_skus_trans->{'Location'}.',';
						$result_csv_details .= $rec_skus_trans->{'Date'}.',';
						$result_csv_details .= $rec_skus_trans->{'ID_trs'}.',';

						if ($rec_parts_productions->{'In_out'} eq 'in'){
							## Salida de Inventario

							### Linea de detalle
							$result_csv_details .= 'Parts Production,Out,'.$inv_original.','.$rec_parts_productions->{'Quantity'}.','.($inv_original - $rec_parts_productions->{'Quantity'})."\n";

							## Como es una SALIDA se RESTA
							my $inv_temp = $inv_original;
							$inv_original -= $rec_parts_productions->{'Quantity'};
							++$count_out;
							$qty_out += $rec_parts_productions->{'Quantity'};

							print qq|sl_parts_productions[$rec_skus_trans->{'ID_trs'}][$rec_parts_productions->{'In_out'}] -> <strong>$inv_original</strong> = $inv_temp - $rec_parts_productions->{'Quantity'} :: $count_out<br>|;

						}elsif ($rec_parts_productions->{'In_out'} eq 'out'){
							## Entrada de Inventario

							### Linea de detalle
							$result_csv_details .= 'Parts Production,In,'.$inv_original.','.$rec_parts_productions->{'Quantity'}.','.($inv_original + $rec_parts_productions->{'Quantity'})."\n";

							## Como es una ENTRADA se SUMA
							my $inv_temp = $inv_original;
							$inv_original += $rec_parts_productions->{'Quantity'};
							++$count_in;
							$qty_in += $rec_parts_productions->{'Quantity'};

							print qq|sl_parts_productions[$rec_skus_trans->{'ID_trs'}][$rec_parts_productions->{'In_out'}] -> <strong>$inv_original</strong> = $inv_temp + $rec_parts_productions->{'Quantity'}<br>|;

						}else{
							#&cgierr("Problema detectado en sl_parts_productions $rec_skus_trans->{'ID_trs'} no es In ni Out");
							$notes .= "Problema detectado en sl_parts_productions $rec_skus_trans->{'ID_trs'} no es In ni Out<br>";
						}


					}
				}

				##############################################
				## sl_purchaseorders -> Return to Vendor
				##############################################
				case 'sl_purchaseorders' {

					$sql = "SELECT IFNULL(SUM(sl_purchaseorders_items.Qty),0) AS Quantity, sl_purchaseorders.Status
					FROM sl_purchaseorders
					INNER JOIN sl_purchaseorders_items ON sl_purchaseorders_items.ID_purchaseorders=sl_purchaseorders.ID_purchaseorders
					WHERE sl_purchaseorders.Type='Return to Vendor'
					AND sl_purchaseorders.ID_purchaseorders='".$rec_skus_trans->{'ID_trs'}."'
					AND sl_purchaseorders_items.ID_products='".$rec_inv_oct->{'ID_products'}."'
					GROUP BY sl_purchaseorders_items.ID_products
					";
					my $sth_purchaseorders = &Do_SQL($sql);
					while (my $rec_purchaseorders = $sth_purchaseorders->fetchrow_hashref()){
						if ($rec_purchaseorders->{'Status'} eq 'New' or $rec_purchaseorders->{'Status'} eq 'Cancelled'){
							#&cgierr("Problema detectado en sl_purchaseorders $rec_skus_trans->{'ID_trs'} Status=$rec_purchaseorders->{'Status'}");
							$notes .= "Problema detectado en sl_purchaseorders $rec_skus_trans->{'ID_trs'} Status=$rec_purchaseorders->{'Status'}<br>";
						}

						### Se genera la linea de detalles del movimiento
						$result_csv_details .= $id_products.',';
						$result_csv_details .= $rec_skus_trans->{'ID_warehouses'}.',';
						$result_csv_details .= $rec_skus_trans->{'Location'}.',';
						$result_csv_details .= $rec_skus_trans->{'Date'}.',';
						$result_csv_details .= $rec_skus_trans->{'ID_trs'}.',';
						### Linea de detalle
						$result_csv_details .= 'Return to Vendor,Out,'.$inv_original.','.$rec_purchaseorders->{'Quantity'}.','.($inv_original - $rec_purchaseorders->{'Quantity'})."\n";

						## Como es una SALIDA se RESTA
						my $inv_temp = $inv_original;
						$inv_original -= $rec_purchaseorders->{'Quantity'};
						++$count_out;
						$qty_out += $rec_purchaseorders->{'Quantity'};

						print qq|sl_purchaseorders[$rec_skus_trans->{'ID_trs'}] -> <strong>$inv_original</strong> = $inv_temp - $rec_purchaseorders->{'Quantity'} :: $count_out<br>|;

					}
				}

				##############################################
				## sl_creditmemos
				##############################################
				case 'sl_creditmemos' {

					$sql = "SELECT IFNULL(SUM(sl_creditmemos_products.Quantity),0) AS Quantity
					FROM sl_creditmemos
					INNER JOIN sl_creditmemos_products ON sl_creditmemos.ID_creditmemos=sl_creditmemos_products.ID_creditmemos
					WHERE sl_creditmemos.ID_creditmemos='".$rec_skus_trans->{'ID_trs'}."'
					AND sl_creditmemos_products.ID_products='".$rec_inv_oct->{'ID_products'}."'
					GROUP BY sl_creditmemos_products.ID_products
					";
					my $sth_creditmemos = &Do_SQL($sql);
					while (my $rec_creditmemos = $sth_creditmemos->fetchrow_hashref()){
						# if ($rec_creditmemos->{'Status'} eq 'New' or $rec_creditmemos->{'Status'} eq 'Cancelled'){
						# 	&cgierr("Problema detectado en sl_creditmemos $rec_skus_trans->{'ID_trs'} Status=$rec_creditmemos->{'Status'}");
						# }

						### Se genera la linea de detalles del movimiento
						$result_csv_details .= $id_products.',';
						$result_csv_details .= $rec_skus_trans->{'ID_warehouses'}.',';
						$result_csv_details .= $rec_skus_trans->{'Location'}.',';
						$result_csv_details .= $rec_skus_trans->{'Date'}.',';
						$result_csv_details .= $rec_skus_trans->{'ID_trs'}.',';
						### Linea de detalle
						$result_csv_details .= 'Credit Memos,In,'.$inv_original.','.$rec_creditmemos->{'Quantity'}.','.($inv_original + $rec_creditmemos->{'Quantity'})."\n";

						## Como es una ENTRADA se SUMA
						my $inv_temp = $inv_original;
						$inv_original += $rec_creditmemos->{'Quantity'};
						++$count_in;
						$qty_in += $rec_creditmemos->{'Quantity'};

						print qq|sl_creditmemos[$rec_skus_trans->{'ID_trs'}] -> <strong>$inv_original</strong> = $inv_temp + $rec_creditmemos->{'Quantity'}<br>|;

					}
				}

				##############################################
				## sl_adjustments
				##############################################
				case 'sl_adjustments' {

					$sql = "SELECT IFNULL(SUM(sl_adjustments_items.Qty),0) AS Quantity
					FROM sl_adjustments
					INNER JOIN sl_adjustments_items ON sl_adjustments_items.ID_adjustments=sl_adjustments.ID_adjustments
					WHERE sl_adjustments.ID_adjustments='".$rec_skus_trans->{'ID_trs'}."'
					AND sl_adjustments_items.ID_products='".$rec_inv_oct->{'ID_products'}."'
					GROUP BY sl_adjustments_items.ID_products
					";
					my $sth_adjustments = &Do_SQL($sql);
					while (my $rec_adjustments = $sth_adjustments->fetchrow_hashref()){
						# if ($rec_adjustments->{'Status'} eq 'New' or $rec_adjustments->{'Status'} eq 'Cancelled'){
						# 	&cgierr("Problema detectado en sl_adjustments $rec_skus_trans->{'ID_trs'} Status=$rec_adjustments->{'Status'}");
						# }

						### Se genera la linea de detalles del movimiento
						$result_csv_details .= $id_products.',';
						$result_csv_details .= $rec_skus_trans->{'ID_warehouses'}.',';
						$result_csv_details .= $rec_skus_trans->{'Location'}.',';
						$result_csv_details .= $rec_skus_trans->{'Date'}.',';
						$result_csv_details .= $rec_skus_trans->{'ID_trs'}.',';

						if ($rec_adjustments->{'Quantity'} > 0){

							### Linea de detalle
							$result_csv_details .= 'Adjustments,In,'.$inv_original.','.$rec_adjustments->{'Quantity'}.','.($inv_original + $rec_adjustments->{'Quantity'})."\n";

							## Como es una ENTRADA se SUMA
							my $inv_temp = $inv_original;
							$inv_original += $rec_adjustments->{'Quantity'};
							++$count_in;
							$qty_in += $rec_adjustments->{'Quantity'};

							print qq|sl_adjustments[$rec_skus_trans->{'ID_trs'}] -> <strong>$inv_original</strong> = $inv_temp + |.abs($rec_adjustments->{'Quantity'}).qq|<br>|;
						
						}elsif ($rec_adjustments->{'Quantity'} < 0){
							
							### Linea de detalle
							$result_csv_details .= 'Adjustments,Out,'.$inv_original.','.$rec_adjustments->{'Quantity'}.','.($inv_original - abs($rec_adjustments->{'Quantity'}))."\n";

							## Como es una SALIDA se RESTA
							my $inv_temp = $inv_original;
							$inv_original -= abs($rec_adjustments->{'Quantity'});
							++$count_out;
							$qty_out += abs($rec_adjustments->{'Quantity'});

							print qq|sl_adjustments[$rec_skus_trans->{'ID_trs'}] -> <strong>$inv_original</strong> = $inv_temp - |.abs($rec_adjustments->{'Quantity'}).qq| :: $count_out<br>|;

						}
					}
				}

				##############################################
				## sl_returns
				##############################################
				case 'sl_returns' {

					$sql = "SELECT sl_returns_upcs.Quantity, sl_returns.Status
					FROM sl_returns
					INNER JOIN sl_returns_upcs ON sl_returns_upcs.ID_returns=sl_returns.ID_returns
					WHERE sl_returns.ID_returns='".$rec_skus_trans->{'ID_trs'}."'
					AND (400000000 + sl_returns_upcs.ID_parts)='".$rec_inv_oct->{'ID_products'}."'
					GROUP BY sl_returns_upcs.ID_parts
					ORDER BY sl_returns.ID_returns DESC
					";
					my $sth_returns = &Do_SQL($sql);
					while (my $rec_returns = $sth_returns->fetchrow_hashref()){
						if ($rec_returns->{'Status'} ne 'Resolved'){
							#&cgierr("Problema detectado en sl_returns $rec_skus_trans->{'ID_trs'} Status=$rec_returns->{'Status'}");
							$notes .= "Problema detectado en sl_returns $rec_skus_trans->{'ID_trs'} Status=$rec_returns->{'Status'}<br>";
						}

						### Se genera la linea de detalles del movimiento
						$result_csv_details .= $id_products.',';
						$result_csv_details .= $rec_skus_trans->{'ID_warehouses'}.',';
						$result_csv_details .= $rec_skus_trans->{'Location'}.',';
						$result_csv_details .= $rec_skus_trans->{'Date'}.',';
						$result_csv_details .= $rec_skus_trans->{'ID_trs'}.',';
						### Linea de detalle
						$result_csv_details .= 'Returns,In,'.$inv_original.','.$rec_returns->{'Quantity'}.','.($inv_original + $rec_returns->{'Quantity'})."\n";

						## Como es una ENTRADA se SUMA
						my $inv_temp = $inv_original;
						$inv_original += $rec_returns->{'Quantity'};
						++$count_in;
						$qty_in += $rec_returns->{'Quantity'};

						print qq|sl_returns[$rec_skus_trans->{'ID_trs'}] -> <strong>$inv_original</strong> = $inv_temp + $rec_returns->{'Quantity'}<br>|;

					}
				}
			}#switch
		}#while

		### Inventario actual en Direksys
		my $sql_inv_dks = "SELECT SUM(Quantity) FROM sl_warehouses_location WHERE ID_products = ".$id_products." GROUP BY ID_products;";
		my $sth_inv_dks = &Do_SQL($sql_inv_dks);
		my $inv_dks = $sth_inv_dks->fetchrow();

		$inv_dks = int($inv_dks);

		## Inventario resultante
		print qq|inv final $id_products -> <strong>$inv_original</strong><br><br>|;

		$result_csv .= $count_in.','.$qty_in.','.$count_out.','.$qty_out.','.$inv_original.','.$inv_dks.','.$notes."\n";


	}
	
	# Archivo con resultados generales
	if( open(my ($file),">", $file_path."fix_inventory_".$in{'e'}.".csv") ){
		print $file $result_csv;
		close($file);
	}else{
		print "No se pudo guardar el archivo: fix_inventory_".$in{'e'}.".csv\n";
	}
	# Archivo con resultados detallados
	if( open(my ($file),">", $file_path."fix_inventory_details_".$in{'e'}.".csv") ){
		print $file $result_csv_details;
		close($file);
	}else{
		print "No se pudo guardar el archivo: fix_inventory_details_.csv\n";
	}

	print "\n\n";
	
return;

###----------------------------------------------------------------------------------------------------------

	my $add_sql = '';
	if ($in{'id_products'}){
		$in{'id_parts'} = int($in{'id_products'});
		$in{'id_products'} = 400000000 + int($in{'id_products'});
	}
	$add_sql .= ($in{'id_products'})? " AND sl_skus_trans.ID_products = ".int($in{'id_products'})." ":"";
	$add_sql .= ($in{'id_warehouses'})? " AND sl_skus_trans.ID_warehouses = ".int($in{'id_warehouses'})." ":"";
	$add_sql .= ($in{'id_locations'})? " AND sl_locations.ID_locations = ".int($in{'id_locations'})." ":"";

	if ($in{'id_trs'} and $in{'tbl_name'}){
		
		my ($add_sql_returns);
		if ($in{'tbl_name'} eq 'sl_orders'){
			$sql = "SELECT GROUP_CONCAT(ID_returns)ID_returns FROM sl_returns WHERE ID_orders='$in{'id_trs'}';";
			my $sth = &Do_SQL($sql);
			my ($id_returns) = $sth->fetchrow_array();
			if ($id_returns){
				$add_sql_returns = " OR (sl_skus_trans.tbl_name = 'sl_returns' AND sl_skus_trans.ID_trs IN(".$id_returns."))";
			}
		}
		$add_sql .= " AND ((sl_skus_trans.tbl_name = '".$in{'tbl_name'}."' AND sl_skus_trans.ID_trs = '".int($in{'id_trs'})."') $add_sql_returns) ";
	}
	# elsif ($in{'from_date'} eq '' and  $in{'to_date'} eq ''){
	# 	$add_sql .= " AND sl_skus_trans.Date = CURDATE() ";
	# }
	
	# ## Filtro por Date
	if ($in{'from_date'} ne '' and  $in{'to_date'} ne '' and $in{'from_date'} eq $in{'to_date'}){
		$add_sql .= " AND sl_skus_trans.Date = '$in{'from_date'}' ";
	}else{
		if ($in{'from_date'}){
			$add_sql .= " AND sl_skus_trans.Date >= '$in{'from_date'}' ";
		}

		if ($in{'to_date'}){
			$add_sql .= " AND sl_skus_trans.Date <= '$in{'to_date'}' ";
		}
	}
	my $id_products_trans = 0;
	# Ultimos ID registrados en sl_skus_trans al momento de sacar la fotografia del inventario
	$id_products_trans = 4916812 if ($in{'e'} == 2 or $in{'e'} == 10);
	$id_products_trans = 114263 if ($in{'e'} == 3 or $in{'e'} == 7);
	$id_products_trans = 211068 if ($in{'e'} == 4 or $in{'e'} == 12);
	$id_products_trans = 108872 if ($in{'e'} == 11 or $in{'e'} == 13);
	# $sql_restriction = ($id_products_trans > 0)? " AND sl_skus_trans.ID_products_trans > $id_products_trans":"";

	# ## Filtro type
	my ($string_tmp);
	if ($in{'type'}){
		if ($in{'type'} =~ m/\|/){
			my @arr_tmp = split /\|/ , $in{'type'};
			for (0..$#arr_tmp) {
				$string_tmp .= "'".$arr_tmp[$_]."',";
			}
			chop $string_tmp;
			$add_sql .= " AND sl_skus_trans.type IN($string_tmp) ";
		}else{
			$add_sql .= " AND sl_skus_trans.type IN('$in{'type'}') ";
		}
	}

	my $total_entradas_qty = 0;
	my $total_entradas_cost = 0;
	my $total_salidas_qty = 0;
	my $total_salidas_cost = 0;
	my $total_saldos_qty = 0;
	my $total_saldos_cost = 0;
	my $total_existencias_cost = 0;
	my $title_custom_info = '';
	my $id_custom_info = '';
	my $title_colspan_existencias = 6;
	my $extra_cell_initial = '';
	my $extra_cell_total = '';

	if ($in{'custom_info'}){
		$title_custom_info = '<th style="border-right: 1px solid #777777; border-bottom: 1px solid #777777;">ID Custom Info</th>';
		$title_colspan_existencias += 1;
	}
	
	$add_sql .= ($in{'ID_warehouses'})? "AND sl_skus_trans.ID_warehouses='$in{'ID_warehouses'}'" : "";

	print qq|
	<table border="0" id="cuadros" cellpadding="7" cellspacing="0" width="100%" style="font-size:10px; font-family:verdana; font-weight:normal; border: 1px solid #777777; border-right:0px;">
		<tr style="background-color:#003674;color:#ffffff;">
			<th colspan="6"></th>
			<th colspan="3">Entradas</th>
			<th colspan="3">Salidas</th>
			<th colspan="$title_colspan_existencias">Existencias</th>
		</tr>
		<tr style="background-color:#CAE1FF;">
			<th style="border-right: 1px solid #777777; border-bottom: 1px solid #777777;">Fecha</th>
			<th style="border-right: 1px solid #777777; border-bottom: 1px solid #777777;">SKU</th>
			<th style="border-right: 1px solid #777777; border-bottom: 1px solid #777777;">Descipcion</th>
			<th style="border-right: 1px solid #777777; border-bottom: 1px solid #777777;">Almacen</th>
			<th style="border-right: 1px solid #777777; border-bottom: 1px solid #777777;">Gaveta</th>
			<th style="border-right: 1px solid #777777; border-bottom: 1px solid #777777;">Concepto</th>
			<th style="border-right: 1px solid #777777; border-bottom: 1px solid #777777;">Cantidad</th>
			<th style="border-right: 1px solid #777777; border-bottom: 1px solid #777777;">Costo Unitario</th>
			<th style="border-right: 1px solid #777777; border-bottom: 1px solid #777777;">Total</th>
			<th style="border-right: 1px solid #777777; border-bottom: 1px solid #777777;">Cantidad</th>
			<th style="border-right: 1px solid #777777; border-bottom: 1px solid #777777;">Costo Unitario</th>
			<th style="border-right: 1px solid #777777; border-bottom: 1px solid #777777;">Total</th>
			<th style="border-right: 1px solid #777777; border-bottom: 1px solid #777777;">Cantidad Almacen</th>
			<th style="border-right: 1px solid #777777; border-bottom: 1px solid #777777;">Cantidad Total</th>
			<th style="border-right: 1px solid #777777; border-bottom: 1px solid #777777;">Costo Promedio</th>
			<th style="border-right: 1px solid #777777; border-bottom: 1px solid #777777;">CA</th>
			<th style="border-right: 1px solid #777777; border-bottom: 1px solid #777777;">CC</th>
			|.$title_custom_info.qq|					
			<th style="border-right: 1px solid #777777; border-bottom: 1px solid #777777;">Total</th>
		</tr>|;

	$sql ="SELECT 
			ID_products_trans
			, sl_skus_trans.Date
			, sl_skus_trans.Time
			, sl_skus_trans.ID_products
			, sl_skus_trans.ID_warehouses
			, sl_warehouses.Name AS Warehouses
			, sl_skus_trans.Location
			, sl_skus_trans.Type AS 'TypeOrig'
			, sl_skus_trans.Type_trans
			, sl_skus_trans.tbl_name
			, sl_skus_trans.ID_trs
			, sl_skus_trans.Quantity
			, sl_skus_trans.left_quantity
			, IF(sl_skus_trans.Type_trans='IN',(CAST(sl_skus_trans.left_quantity AS CHAR)-sl_skus_trans.Quantity),(sl_skus_trans.left_quantity+sl_skus_trans.Quantity))AS 'InvInicial'
			, IF(sl_skus_trans.Type_trans='IN','ENTRADA','SALIDA') AS 'TipoMov'
			, sl_skus_trans.Cost
			, sl_skus_trans.Cost_Avg
			, sl_skus_trans.Cost_Adj
			, sl_skus_trans.Cost_Add
			, CASE sl_skus_trans.Type 
				WHEN 'Purchase' THEN 'Recepcion'
				WHEN 'Sale' THEN 'Venta'
				WHEN 'Adjustment' THEN 'Ajuste de Inventario'
				WHEN 'Return' THEN 'Devolucion'
				WHEN 'Return to Vendor' THEN 'Devolucion a Proveedor'
				WHEN 'Production' THEN 'Produccion'
				WHEN 'Transfer In' THEN 'Tranferencia'
				WHEN 'Transfer Out' THEN 'Tranferencia'
				ELSE '- - -'
			END As Type
			, sl_skus_trans.left_quantity_total
			, sl_skus_trans.id_customs_info
			, sl_parts.Name
			, sl_parts.Model AS Products
		FROM sl_skus_trans 
			INNER JOIN sl_warehouses ON sl_warehouses.ID_warehouses=sl_skus_trans.ID_warehouses
			/*LEFT JOIN sl_locations ON sl_skus_trans.Location=sl_locations.Code AND sl_skus_trans.ID_warehouses=sl_locations.ID_warehouses*/
			INNER JOIN sl_parts ON 400000000+(sl_parts.ID_parts)=sl_skus_trans.ID_products
		WHERE 1 
			$add_sql
			$sql_restriction
		ORDER BY sl_skus_trans.Date DESC, sl_skus_trans.Time DESC, sl_skus_trans.ID_products_trans DESC
		LIMIT 250;";
	# print "$sql <br /><br />";
	my $sth3 = &Do_SQL($sql);
	my ($last_date);
	my $total_recs=$sth3->rows();
	my $str_out = '';
	my $recs;
	while (my $rec3 = $sth3->fetchrow_hashref()){
		$rec3->{'Type'} = ($rec3->{'tbl_name'} eq 'sl_orders' and $rec3->{'Type'} eq 'Tranferencia')? 'Tranferencia COD':$rec3->{'Type'};

		$recs_found++;
		$recs++;
		my $trans_type = $rec3->{'TipoMov'};

		# Marcar si lleva o no contabilidad
		my $skip_accounting = '';
		if ($rec3->{'Type'} eq 'Adjustment'){
			my $sth_skip = &Do_SQL("SELECT COUNT(*) FROM sl_movements WHERE tableused='sl_adjustments' AND Status='Active' AND ID_tableused='$rec3->{'ID_trs'}';");
			my $rec_skip = $sth_skip->fetchrow_array();
			$skip_accounting = ($rec_skip > 0)?"":"<span style='background-color:#FF934C;font-size:8px;padding:3px;'>SKIP ACC</span>";
		}

		my %cmds = (
		"sl_orders", '/cgi-bin/mod/admin/dbman?cmd=opr_orders&view='.$rec3->{'ID_trs'}
		,"sl_returns", '/cgi-bin/mod/admin/dbman?cmd=opr_returns&view='.$rec3->{'ID_trs'}
		,"sl_purchases", '/cgi-bin/mod/admin/dbman?cmd=mer_po&view='.$rec3->{'ID_trs'}
		,"sl_adjustments", '/cgi-bin/mod/admin/dbman?cmd=opr_adjustments&view='.$rec3->{'ID_trs'}
		,"sl_wreceipts", '/cgi-bin/mod/admin/dbman?cmd=mer_wreceipts&view='.$rec3->{'ID_trs'}
		,"sl_manifests", '/cgi-bin/mod/admin/dbman?cmd=opr_manifests&view='.$rec3->{'ID_trs'}
		,"sl_parts_productions", '/cgi-bin/mod/admin/dbman?cmd=mer_parts_productions&view='.$rec3->{'ID_trs'}
		,"sl_skustransfers", '/cgi-bin/mod/admin/dbman?cmd=opr_skustransfers&view='.$rec3->{'ID_trs'}
		,"sl_purchaseorders", '/cgi-bin/mod/admin/dbman?cmd=mer_po&view='.$rec3->{'ID_trs'}
		,"sl_creditmemos", '/cgi-bin/mod/admin/dbman?cmd=opr_creditmemos&view='.$rec3->{'ID_trs'});
		
		if ($trans_type eq 'ENTRADA'){
			$inv_total += $rec3->{'Quantity'};
			$cost_total_inicial = $inv_total * $cost_promedio;
		}elsif($trans_type eq 'SALIDA'){
			$inv_total -= $rec3->{'Quantity'};
		}

		$total_cost_avg = $rec3->{'Cost_Avg'}*$rec3->{'Quantity'};
		$total_cost = $rec3->{'Cost'}*$rec3->{'Quantity'};


		$str_out .= qq|
				<tr>
					<td width="" nowrap>$rec3->{'Date'} $rec3->{'Time'}</td>
					<td width="">$rec3->{'ID_products'}</td>
					<td width="" nowrap>$rec3->{'Products'}</td>
					<td width="" nowrap>$rec3->{'Warehouses'}</td>
					<td width="" nowrap>$rec3->{'Location'}</td>
					<td width="" nowrap><a href="$cmds{$rec3->{'tbl_name'}}" target="_blank">$rec3->{'Type'} $rec3->{'ID_trs'}</a> $skip_accounting</td>|;
		
		## Entradas
		$str_out_left = qq|
					<td align=right width="" style="background-color:#cce769;">|.&format_number($rec3->{'Quantity'}).qq|</td>
					<td align=right width="" style="background-color:#cce769;">|.&format_number($rec3->{'Cost'},3).qq|</td>
					<td align=right width="" style="background-color:#cce769;">|.&format_number($total_cost,2).qq|</td>|;
		
		## Vacuum
		$str_out_vacuum = qq|
					<td align=right width="" ></td>
					<td align=right width="" ></td>
					<td align=right width="" ></td>|;

		## Salidas
		$str_out_rigth = qq|
					<td align=right width="" style="background-color:#FFAA72;">|.&format_number($rec3->{'Quantity'}).qq|</td>
					<td align=right width="" style="background-color:#FFAA72;">|.&format_number($rec3->{'Cost'},3).qq|</td>
					<td align=right width="" style="background-color:#FFAA72;">|.&format_number($total_cost,2).qq|</td>|;

		my $css_cost;
		if ($trans_type eq 'SALIDA'){
			$str_out .= $str_out_vacuum.$str_out_rigth;
			$total_salidas_qty += $rec3->{'Quantity'};
			$total_salidas_cost += $total_cost;
		}else{
			$str_out .= $str_out_left.$str_out_vacuum;
			$total_entradas_qty += $rec3->{'Quantity'};
			$total_entradas_cost += $total_cost;
			$css_cost = qq|background-color:#2963FA;|;
		}


		if($in{'custom_info'}){
			$id_custom_info = qq|<td align=right width="" >$rec3->{'id_customs_info'}</td>|;
			$extra_cell_initial = '<td  align=right width="" ></td>';
			$extra_cell_total = '<th width=""></th>';
		}

		## Existencias
		$str_out .= qq|
					<td align=right width="" >|.&format_number($rec3->{'left_quantity'}).qq|</td>
					<td align=right width="" >|.&format_number($rec3->{'left_quantity_total'}).qq|</td>
					<td align=right width="" style="$css_cost">|.&format_number($rec3->{'Cost_Avg'},3).qq|</td>
					<td align=right width="" >|.&format_number($rec3->{'Cost_Adj'},3).qq|</td>
					<td align=right width="" >|.&format_number($rec3->{'Cost_Add'},3).qq|</td>
					$id_custom_info
					<td align=right width="" >|.&format_number($rec3->{'Cost_Avg'}*$rec3->{'left_quantity'},2).qq|</td>
				</tr>|;

		$total_existencias_cost += $rec3->{'Cost_Avg'}*$rec3->{'left_quantity'};

		# or $last_date ne $rec3->{'Date'}
		# if ($recs == $total_recs){
		# 	$str_out .= qq|
		# 	<tr style="background-color:#fafa7b;">
		# 		<td  width="">$rec3->{'Date'}</td>
		# 		<td  width="" align="center">---</td>
		# 		<td  width="" align="center">---</td>
		# 		<td  width="" align="center">---</td>
		# 		<td  width="">INVENTARIO INICIAL</td>
		# 		<td  align=right width="" ></td>
		# 		<td  align=right width="" ></td>
		# 		<td  align=right width="" ></td>
		# 		<td  align=right width="" ></td>
		# 		<td  align=right width="" ></td>
		# 		<td  align=right width="" ></td>
		# 		<td align=right width="">|.&format_number($rec3->{'InvInicial'}).qq|</td>
		# 		<td  align=right width="" ></td>
		# 		<td align=right width="">|.&format_price($rec3->{'Cost_Avg'},2).qq|</td>
		# 		<td  align=right width="" ></td>
		# 		<td  align=right width="" ></td>
		# 		$extra_cell_initial
		# 		<td align=right width="">|.&format_number(($rec3->{'Cost_Avg'} * $rec3->{'InvInicial'}),2).qq|</td>
		# 	</tr>|;

		# }
		$last_date = $rec3->{'Date'};

	}
	
	$str_out .= qq|
			<tr>
				<th nowrap width="" colspan="6" align="right">Totales</th>
				<th nowrap width="" align="right">|.&format_number($total_entradas_qty).qq|</th>
				<th nowrap width=""></th>
				<th nowrap width="" align="right">|.&format_price($total_entradas_cost,2).qq|</th>
				<th nowrap width="" align="right">|.&format_number($total_salidas_qty).qq|</th>
				<th nowrap width=""></th>
				<th nowrap width="" align="right">|.&format_price($total_salidas_cost,2).qq|</th>
				<th nowrap width=""><!-- |.&format_number($inv_total).qq| --></th>
				<th nowrap width=""></th>
				<th nowrap width=""></th>
				<th nowrap width=""></th>
				<th nowrap width=""></th>
				$extra_cell_total
				<th nowrap width="" style="border-right: 1px solid #777777;">|.&format_price($total_existencias_cost,2).qq|</th>
			</tr>
		</table><br><br>|;
	print $str_out;



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
	$sql = "SELECT ZipCode, StateFullName FROM sl_zipcodes WHERE Status='Active' AND zipcode='$orig_zipcode' AND StateFullName='$orig_state' GROUP BY ZipCode, StateFullName";
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