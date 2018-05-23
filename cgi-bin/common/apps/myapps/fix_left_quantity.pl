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
# use File::Copy;

# local ($dir) = getcwd;
# Default la 2 porque este proceso fue diseñado para TMK
#local(%in) = &parse_form;
# local ($in{'e'}) = 2 if (!$in{'e'});
# chdir($dir);
local ($in{'e'}) = 3;
local ($in{'cmd'}) = 'rep_fin_kardex';
local ($in{'action'}) = 1;
local ($in{'id_products'}) = '5710';
local ($in{'from_date'}) = '2015-06-30';
local ($in{'fix'}) = 1;
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
	&analysis_creditmemos;
	&disconnect_db;

}


#################################################################
#################################################################
#	Function: analysus_creditmemos
#
#   		Analysis CM
#
#	Created by: ISC Alejandro Diaz
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
sub analysis_creditmemos{
#################################################################
#################################################################

# Ninguna tabla es correcta
# lo mas realista es la tabla de sl_warehouses_location y se caia sl_skus_cost
# lo que se ve en pantalla es de sl_warehouses_location por lo que debemos basrnos en Estado
# debemos agrupar por almacen y producto

# registros en 0 de sl_warehouses_location se borran

# no contar lo de los almacenes vistuales AAA quien sabe que

# debe ser basado en lo real

# ID_warehouses=0 se va a la basura
	my $process = ($in{'process'} ne 'commit')? qq|<span style="color:#000;background-color:gray;padding:5px;">ANALYZING</span>|:qq|<span style="color:#FFF;background-color:red;padding:5px;">EXECUTING</span>|;
	my $log_email;
	my $easy_fix=0;
	my $hard_fix=0;
	my $hard_fix_quantity=0;

	&load_settings;
	# print "Content-type: text/html\n\n";
	# print qq|<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN"   "http://www.w3.org/TR/html4/loose.dtd">
	# 		 <meta http-equiv="content-type" content="text/html; charset=utf-8" />\n\n|;
	print qq|<title>Warehouses Manager :: Kardex</title>\n\n|;

# 	print qq|

# <STYLE TYPE="text/css">
# h1 {
# 	font-family: century gothic;
#     display: block;
#     font-size: 45px;
#     margin: 0px;
#     font-weight: normal;
#     line-height:45px;
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
 

# 	</STYLE>
# </head>
# <body>
# |;	

# 	print qq|<div align="center">|;
# 	print qq|<h1>K A R D E X</h1>|;
# 	print qq|<h2>|.uc($cfg{'app_title'}).qq|</h2>|;
# 	print qq|</div>|;
	
	if(!&check_permissions('rep_fin_kardex','','')) {
		print qq|<span style="color:red;">|.&trans_txt('unauth_action').qq|</span>|;
		return
	}
	
	if (!$in{'e'}){
		print qq|<span style="color:red;">ID de empresa es requerido</span>|;
		return;
	}

### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### 
### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### 
my $sth_productos = &Do_SQL("SELECT (ID_products-400000000)ID_products FROM cu_inventory GROUP BY ID_products ORDER BY ID_products");
my $total_updates_por_producto=0;
while (($in{'id_products'}) = $sth_productos->fetchrow_array()){
	my $updates_por_producto=0;
	
	print "<h2>PROCESANDO PRODUCTO $in{'id_products'}</h2>";

	### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### 
	### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### 
	my $add_sql_sku;
	my $add_sql;
	my $add_sql_wh;
	my $add_sql_parts;

	if ((!$in{'id_products'} or length(int($in{'id_products'}))!=4) and (!$in{'upc'} or $in{'upc'} eq '')){
		print qq|<span style="color:red;">SKU Invalido: $in{'id_products'}</span>|;
		return;
	}else{
		$add_sql_sku = ($in{'id_products'})? " AND sl_parts.ID_parts = '".int($in{'id_products'})."' ":"";
		$add_sql_sku .= ($in{'upc'})? " AND sl_skus.UPC = TRIM('".$in{'upc'}."') ":"";
		$in{'id_products'} = 400000000 + int($in{'id_products'}) if ($in{'id_products'});
	}

	$add_sql .= ($in{'id_products'})? " AND sl_skus_trans.ID_products = '".int($in{'id_products'})."' ":"";
	$add_sql_skus .= ($in{'upc'})? " AND sl_skus.UPC = TRIM('".$in{'upc'}."') ":"";
	$add_sql_wh .= ($in{'id_products'})? " AND sl_skus_trans.ID_products = '".int($in{'id_products'})."' ":"";
	$add_sql .= ($in{'id_warehouses'})? " AND sl_skus_trans.ID_warehouses = '".int($in{'id_warehouses'})."' ":"";
	$add_sql_wh .= ($in{'id_warehouses'})? " AND sl_skus_trans.ID_warehouses = '".int($in{'id_warehouses'})."' ":"";
	
	$add_sql_parts .= ($in{'id_products'})? " AND sl_skus_trans.ID_products = '".int($in{'id_products'})."' ":"";
	$add_sql_parts .= ($in{'id_warehouses'})? " AND sl_skus_trans.ID_warehouses = '".int($in{'id_warehouses'})."' ":"";

	my $id_products_trans = 0;
	# Ultimos ID registrados en sl_skus_trans al momento de sacar la fotografia del inventario
	$id_products_trans = 4916812 if ($in{'e'} == 2);
	$id_products_trans = 114263 if ($in{'e'} == 3);
	$id_products_trans = 211068 if ($in{'e'} == 4);
	$id_products_trans = 108872 if ($in{'e'} == 11);
	$sql_restriction = ($id_products_trans > 0)? " AND sl_skus_trans.ID_products_trans >  $id_products_trans":"";

	## Filtro type
	my ($string_tmp);
	if ($in{'type'}){
		if ($in{'type'} =~ m/\|/){
			my @arr_tmp = split /\|/ , $in{'type'};
			for (0..$#arr_tmp) {
				$string_tmp .= "'".$arr_tmp[$_]."',";
			}
			chop $string_tmp;
			$add_sql .= " AND sl_skus_trans.type IN($string_tmp) ";
			$add_sql_wh .= " AND sl_skus_trans.type IN($string_tmp) ";
		}else{
			$add_sql .= " AND sl_skus_trans.type IN('$in{'type'}') ";
			$add_sql_wh .= " AND sl_skus_trans.type IN('$in{'type'}') ";
		}
	}

	## Filtro por Date
	if ($in{'from_date'} ne '' and  $in{'to_date'} ne '' and $in{'from_date'} eq $in{'to_date'}){
		$add_sql .= " AND sl_skus_trans.Date = '$in{'from_date'}' ";
		$add_sql_wh .= " AND sl_skus_trans.Date = '$in{'from_date'}' ";
	}else{
		if ($in{'from_date'}){
			$add_sql .= " AND sl_skus_trans.Date >= '$in{'from_date'}' ";
			$add_sql_wh .= " AND sl_skus_trans.Date >= '$in{'from_date'}' ";
		}

		if ($in{'to_date'}){
			# $add_sql .= " AND sl_skus_trans.Date <= '$in{'to_date'}' ";
			# $add_sql_wh .= " AND sl_skus_trans.Date <= '$in{'to_date'}' ";
		}
	}

	if ($in{'from_date'} eq '' and  $in{'to_date'} eq ''){
		$add_sql .= " AND sl_skus_trans.Date = CURDATE() ";
		$add_sql_wh .= " AND sl_skus_trans.Date = CURDATE() ";
	}

	$sql = "SELECT sl_parts.*, (400000000+sl_parts.ID_parts)SKU, sl_skus.UPC
	FROM sl_parts 
	INNER JOIN sl_skus ON sl_parts.ID_parts=sl_skus.ID_products AND (400000000+sl_parts.ID_parts)=sl_skus.ID_sku_products
	LEFT JOIN sl_skus_trans ON (400000000+sl_parts.ID_parts)=sl_skus_trans.ID_products $add_sql_parts $add_sql_skus
	WHERE sl_parts.Status='Active' $add_sql_sku
	GROUP BY sl_skus_trans.ID_products LIMIT 1;";
	# print "$sql <br />";
	my $sth = &Do_SQL($sql);
	my $recs_found = 0;
	my $str_out = '';
	while (my $rec = $sth->fetchrow_hashref()){

		if (!$in{'id_products'}){
			$add_sql .= " AND sl_skus_trans.ID_products = '".$rec->{'SKU'}."' ";
			$add_sql_wh .= " AND sl_skus_trans.ID_products = '".$rec->{'SKU'}."' ";
		}

		###->print qq|<table border="0"  cellpadding="7" cellspacing="0" width="100%" style="font-size:12px; font-family:verdana; font-weight:normal; border: 1px solid #222222;">
				# 	<tr height=35px>
				# 		<th width="10%" bgcolor=#003674><font face="century gothic, arial" color="#ffffff" size="3">SKU</th>
				# 		<th width="10%" bgcolor=#003674><font face="century gothic, arial" color="#ffffff" size="3">UPC</th>
				# 		<th width="40%" bgcolor=#003674><font face="century gothic, arial" color="#ffffff" size="3">Nombre</th>
				# 		<th width="40%" bgcolor=#003674><font face="century gothic, arial" color="#ffffff" size="3">Modelo</th>
				# 		<th width="10%" bgcolor=#003674><font face="century gothic, arial" color="#ffffff" size="3">Estatus</th>
				# 	</tr>
				# 	<tr>
				# 		<td width="" align="center"><h3>$rec->{'SKU'}</h3></td>
				# 		<td width="" align="center"><h3>$rec->{'UPC'}</h3></td>
				# 		<td width="" align="center"><h3>$rec->{'Name'}</h3></td>
				# 		<td width="" align="center"><h3>$rec->{'Model'}</h3></td>
				# 		<td width="" align="center"><h3>$rec->{'Status'}</h3></td>
				# 	</tr>
				# </table><br />|;
		
				$sql = "SELECT sl_warehouses.* 
				FROM sl_warehouses 
				INNER JOIN sl_skus_trans ON sl_skus_trans.ID_warehouses=sl_warehouses.ID_warehouses
				WHERE 1 $add_sql_wh 
				$sql_restriction
				GROUP BY sl_skus_trans.ID_warehouses
				ORDER BY sl_warehouses.ID_warehouses;";
				# print "$sql <br /><br />";
				my $sth2 = &Do_SQL($sql);
				my $str_wh = '';
				my $total_entradas_qty = 0;
				my $total_entradas_cost = 0;
				my $total_salidas_qty = 0;
				my $total_salidas_cost = 0;
				my $total_saldos_qty = 0;
				my $total_saldos_cost = 0;
				while (my $rec2 = $sth2->fetchrow_hashref()){
				
					$add_por_usuario = ($usr{'id_admin_users'} <= 3000)? "":" AND sl_skus_trans.Quantity < 400000000 ";
					$sql ="SELECT 
						ID_products_trans
						, sl_skus_trans.Date
						, sl_skus_trans.Time
						, sl_skus_trans.ID_products
						, sl_skus_trans.Location
						, sl_skus_trans.Type
						, sl_skus_trans.Type_trans
						, sl_skus_trans.ID_trs
						, sl_skus_trans.tbl_name
						, sl_skus_trans.Quantity
						, sl_skus_trans.Cost
						, sl_skus_trans.Cost_Adj
						, sl_skus_trans.left_quantity
						/*, IF(Type_trans = 'IN',(left_quantity-Quantity),(left_quantity+Quantity))AS 'InvInicial'*/
					FROM sl_skus_trans 
					WHERE 1 $add_sql 
					$add_por_usuario
					AND sl_skus_trans.ID_warehouses='$rec2->{'ID_warehouses'}'
					/* AND sl_skus_trans.Type NOT IN ('Production') */
					$sql_restriction
					ORDER BY sl_skus_trans.ID_products_trans ASC;";
					# print "$sql <br /><br />";
					my $sth3 = &Do_SQL($sql);
					
					## Inventario Inicial
					my $inv_inicial = 0;
					$sql = "SELECT cu_inventory.Quantity, cu_inventory.Cost FROM cu_inventory WHERE cu_inventory.ID_products='$in{'id_products'}' AND cu_inventory.ID_warehouses='$rec2->{'ID_warehouses'}';";
					# print "$sql <br /><br />";
					my $sth5 = &Do_SQL($sql);
					my ($inv_inicial_qty, $inv_inicial_cost) = $sth5->fetchrow_array();

					$inv_inicial = ($inv_inicial_qty)?$inv_inicial_qty:$inv_inicial;
					# print "inv_inicial=$inv_inicial <br />ID_warehouses=$rec2->{'ID_warehouses'}<br />";
					## Sino hay Inventario Inicial y es una entrada
					# if ($inv_inicial_qty == 0 and )

					my $inv_total = $inv_inicial;
					my $cost_inicial = ($inv_inicial_cost)? $inv_inicial_cost : 'Unknow';
					my $cost_total_inicial = ($inv_inicial * $cost_inicial);
					my $cost_promedio = $cost_inicial;

					if ($sth3->rows() > 0){
						$str_out .= qq|<div style="background-color: ; padding-top:10px; padding-bottom:10px; display:block; border:0px; border-bottom:1px solid silver;">
								<img src="/sitimages/user$rec2->{'Status'}.png" align=left style="margin: 7px 15px 0px 7px;">
								<font size=4 face="century gothic, verdana">$rec2->{'Name'} </font> <br>
								<font size=1 face=verdana>ID: $rec2->{'ID_warehouses'} &nbsp;&nbsp;&nbsp; Type: $rec2->{'Type'} &nbsp;&nbsp;&nbsp; Status: $rec2->{'Status'} </font>
								</div>|;

						$str_out .= qq|<table border="0" id="cuadros" cellpadding="7" cellspacing="0" width="100%" style="font-size:12px; font-family:verdana; font-weight:normal; border: 1px solid #777777; border-right:0px;">
								<tr style="background-color:#003674 ;color:#ffffff;">
									<th colspan="3"></th>
									<th colspan="3">Entradas</th>
									<th colspan="3">Salidas</th>
									<th colspan="3">Saldo</th>
								</tr>
								<tr style="background-color:##e2e2e2;">
									<th style="border-right: 1px solid #777777; border-bottom: 1px solid #777777;">Fecha</th>
									<th style="border-right: 1px solid #777777; border-bottom: 1px solid #777777;">Gaveta</th>
									<th style="border-right: 1px solid #777777; border-bottom: 1px solid #777777;">Concepto</th>
									<th style="border-right: 1px solid #777777; border-bottom: 1px solid #777777;">Cantidad</th>
									<th style="border-right: 1px solid #777777; border-bottom: 1px solid #777777;">Costo Unitario</th>
									<th style="border-right: 1px solid #777777; border-bottom: 1px solid #777777;">Costo Total</th>
									<th style="border-right: 1px solid #777777; border-bottom: 1px solid #777777;">Cantidad</th>
									<th style="border-right: 1px solid #777777; border-bottom: 1px solid #777777;">Costo Unitario</th>
									<th style="border-right: 1px solid #777777; border-bottom: 1px solid #777777;">Costo Total</th>
									<th style="border-right: 1px solid #777777; border-bottom: 1px solid #777777;">Cantidad</th>
									<!-- th style="border-right: 1px solid #777777; border-bottom: 1px solid #777777;">Cantidad Grabada</th -->
									<th style="border-right: 1px solid #777777; border-bottom: 1px solid #777777;">Costo Unitario</th>
									<th style="border-right: 1px solid #777777; border-bottom: 1px solid #777777;">Costo Total</th>
								</tr>|;
							# $str_out .= qq|<tr style="background-color:#fafa7b;">
							# 		<td  width="">$rec3->{'Date'} $rec3->{'Time'}</td>
							# 		<td  width="">$rec3->{'Location'}</td>
							# 		<td  width="">SALDO INICIAL</td>
							# 		<td  align=right width="" ></td>
							# 		<td  align=right width="" ></td>
							# 		<td  align=right width="" ></td>
							# 		<td  align=right width="" ></td>
							# 		<td  align=right width="" ></td>
							# 		<td  align=right width="" ></td>|;
							
							# ## Saldos
							# $str_out .= qq|
							# 			<td align=right width="">$inv_inicial</td>
							# 			<!-- td align=right width=""></td -->
							# 			<td align=right width="">$cost_promedio</td>
							# 			<td align=right width="">|.&format_number($cost_total_inicial,2).qq|</td>|;

							# $str_out .= qq|
							# 		</tr>|;
						my $recs=0;
						my ($last_date);
						while (my $rec3 = $sth3->fetchrow_hashref()){

							## - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
							## - - - - - - - - - - - - - - -LINEA DE SALDO INICIAL - - - - - - - - - - - - - -
							if ($recs == 0 or $last_date ne $rec3->{'Date'}){
								$str_out .= qq|
								<tr style="background-color:#fafa7b;">
									<td  width="">$rec3->{'Date'} $rec3->{'Time'}</td>
									<td  width="" align="center">---</td>
									<td  width="">INVENTARIO INICIAL</td>
									<td  align=right width="" ></td>
									<td  align=right width="" ></td>
									<td  align=right width="" ></td>
									<td  align=right width="" ></td>
									<td  align=right width="" ></td>
									<td  align=right width="" ></td>
									
									<td align=right width="">|.$rec3->{'InvInicial'}.qq|</td>
									<!-- td align=right width=""></td -->
									<td align=right width="">|.&format_price($cost_promedio,2).qq|</td>
									<td align=right width="">|.&format_number($cost_total_inicial,2).qq|</td>
								</tr>
								|;

							}

							$last_date = $rec3->{'Date'};

							## - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
							$recs_found++;
							$recs++;
							my $trans_type = $rec3->{'Type'};

							$trans_type = ($rec3->{'Type'} eq 'Purchase')? "ENTRADA":$trans_type; #IN
							$trans_type = ($rec3->{'Type'} eq 'Sale')? "SALIDA":$trans_type; #IN
							$trans_type = ($rec3->{'Type'} eq 'Return')? "ENTRADA":$trans_type; #IN
							$trans_type = ($rec3->{'Type'} eq 'Return to Vendor')? "SALIDA":$trans_type; #IN

							$trans_type = "ENTRADA" if ($rec3->{'Type'} eq 'Production' and $rec3->{'Type_trans'} eq 'IN');
							$trans_type = "SALIDA" if ($rec3->{'Type'} eq 'Production' and $rec3->{'Type_trans'} eq 'OUT');

							$trans_type = "ENTRADA" if ($rec3->{'Type'} eq 'Adjustment' and $rec3->{'Type_trans'} eq 'IN');
							$trans_type = "SALIDA" if ($rec3->{'Type'} eq 'Adjustment' and $rec3->{'Type_trans'} eq 'OUT');

							$trans_type = ($rec3->{'Type'} eq 'Transfer Out')? "SALIDA":$trans_type; #IN
							$trans_type = ($rec3->{'Type'} eq 'Transfer In')? "ENTRADA":$trans_type; #IN
							

							my %cmds = (
							"sl_orders", '/cgi-bin/mod/admin/dbman?cmd=opr_orders&view='.$rec3->{'ID_trs'}
							,"sl_returns", '/cgi-bin/mod/admin/dbman?cmd=opr_returns&view='.$rec3->{'ID_trs'}
							,"sl_purchases", '/cgi-bin/mod/admin/dbman?cmd=mer_po&view='.$rec3->{'ID_trs'}
							,"sl_adjustments", '/cgi-bin/mod/admin/dbman?cmd=opr_adjustments&view='.$rec3->{'ID_trs'}
							,"sl_wreceipts", '/cgi-bin/mod/admin/dbman?cmd=mer_wreceipts&view='.$rec3->{'ID_trs'}
							,"sl_manifests", '/cgi-bin/mod/admin/dbman?cmd=opr_manifests&view='.$rec3->{'ID_trs'}
							,"sl_parts_productions", ''
							,"sl_skustransfers", '/cgi-bin/mod/admin/dbman?cmd=opr_skustransfers&view='.$rec3->{'ID_trs'}
							,"sl_purchaseorders", '/cgi-bin/mod/admin/dbman?cmd=mer_po&view='.$rec3->{'ID_trs'}
							,"sl_creditmemos", '/cgi-bin/mod/admin/dbman?cmd=opr_creditmemos&view='.$rec3->{'ID_trs'});

							## Este costo va variar cada que haya una entrada
							
							if ($trans_type eq 'ENTRADA'){
								$inv_total += $rec3->{'Quantity'};
								$total_cost = $rec3->{'Quantity'} * $rec3->{'Cost'};
								$cost_promedio = ($inv_total > 0)?($cost_total_inicial + $total_cost) / $inv_total:0;
								$cost_total_inicial = $inv_total * $cost_promedio;
							}elsif($trans_type eq 'SALIDA'){
								$inv_total -= $rec3->{'Quantity'};
								$total_cost = $rec3->{'Quantity'} * $cost_promedio;
								$cost_total_inicial = $inv_total * $cost_promedio;
							}

							# if ($recs == 1 and $inv_inicial == 0){
								# $sql_tmp = "UPDATE sl_skus_trans SET left_quantity='$inv_inicial' WHERE ID_products_trans='$rec3->{'ID_products_trans'}';";
							# }else{
								$sql_tmp = "UPDATE sl_skus_trans SET left_quantity='$inv_total' WHERE ID_products_trans='$rec3->{'ID_products_trans'}';";
							# }
							if ($in{'fix'}){
								&Do_SQL($sql_tmp);
								$updates_por_producto++;
							}

							$str_out .= qq|
									<tr>
										<td width="">$rec3->{'Date'} $rec3->{'Time'}</td>
										<td width="">$rec3->{'Location'}</td>
										<td width=""><a href="$cmds{$rec3->{'tbl_name'}}" target="_blank">$rec3->{'Type'} $rec3->{'ID_trs'}</a></td>|;
							
							## Entradas
							$str_out_left = qq|
										<td align=right width="" style="background-color:#cce769;">$rec3->{'Quantity'}</td>
										<td align=right width="" style="background-color:#cce769;">|.&format_number($cost_promedio,3).qq|</td>
										<td align=right width="" style="background-color:#cce769;">|.&format_number($total_cost,2).qq|</td>|;
							
							## Vacuum
							$str_out_vacuum = qq|
										<td align=right width="" ></td>
										<td align=right width="" ></td>
										<td align=right width="" ></td>|;

							## Salidas
							$str_out_rigth = qq|
										<td align=right width="" style="background-color:#cce769;">$rec3->{'Quantity'}</td>
										<td align=right width="" style="background-color:#cce769;">|.&format_number($cost_promedio,3).qq|</td>
										<td align=right width="" style="background-color:#cce769;">|.&format_number($total_cost,2).qq|</td>|;

							if ($trans_type eq 'SALIDA'){
								$str_out .= $str_out_vacuum.$str_out_rigth;
								$total_salidas_qty += $rec3->{'Quantity'};
								$total_salidas_cost += $total_cost;
							}else{
								$str_out .= $str_out_left.$str_out_vacuum;
								$total_entradas_qty += $rec3->{'Quantity'};
								$total_entradas_cost += $total_cost;
							}

							## Saldos
							$str_out .= qq|
										<td align=right width="" >$inv_total</td>
										<!-- td align=right width="" style="background-color:#26A8FF;">$rec3->{'left_quantity'}</td -->
										<td align=right width="" >|.&format_number($cost_promedio,3).qq|</td>
										<td align=right width="" >|.&format_number($cost_total_inicial,2).qq|</td>|;

							$str_out .= qq|
									</tr>|;

						}
						$str_out .= qq|
								<tr>
									<th width="" colspan="3" align="right">Totales</th>
									<th width="">|.&format_number($total_entradas_qty).qq|</th>
									<th width=""></th>
									<th width="">|.&format_price($total_entradas_cost,2).qq|</th>
									<th width="">|.&format_number($total_salidas_qty).qq|</th>
									<th width=""></th>
									<th width="">|.&format_price($total_salidas_cost,2).qq|</th>
									<th width="">|.&format_number($inv_total).qq|</th>
									<th width=""></th>
									<th width="" style="border-right: 1px solid #777777;">|.&format_price($cost_total_inicial,2).qq|</th>
								</tr>
							</table>|;
					}
				}

				if ($recs_found){
					###-> print $str_out;
				}else{
					###-> print qq|<div align="center"><span style="color:red;">No se encontro información en el Sistema.</span></div>|;
				}
	}

	###->print "<center><br><FONT face=verdana size=2 color=#666666>MÉTODO DE VALUACIÓN DE INVENTARIO: $cfg{'acc_inventoryout_method'}</font></center>";

	### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### 
	### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### 
	print "<h2>UPDATES EJECUTADOS PARA ESTE PRODUCTO $in{'id_products'} -> $updates_por_producto</h2>";

	$total_updates_por_producto = $total_updates_por_producto + $updates_por_producto;
}
### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### 
### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### 

	print "<h1>COMPLETADO</h1>";
	print "<h2>UPDATES EJECUTADOS PARA ESTE PROCESO -> $total_updates_por_producto</h2>";
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