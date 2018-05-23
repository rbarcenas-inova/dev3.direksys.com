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
	print "Content-type: text/html\n\n";
	print qq|<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN"   "http://www.w3.org/TR/html4/loose.dtd">
			 <meta http-equiv="content-type" content="text/html; charset=utf-8" />\n\n|;
	print qq|<title>Warehouses Manager :: Kardex</title>\n\n|;

	print qq|

<STYLE TYPE="text/css">
h1 {
	font-family: century gothic;
    display: block;
    font-size: 45px;
    margin: 0px;
    font-weight: normal;
    line-height:45px;
}
h2 {
	font-family: century gothic;
    display: block;
    font-size: 25px;
    margin: 0px;
    margin-bottom:15px;
    font-weight: normal;
}
.hoverTable tr:hover 
{
          background-color: #dddddd;
        }

	</STYLE>


</head>
<body>
|;	

	print qq|<div align="center">|;
	print qq|<h1>K A R D E X</h1>|;
	print qq|<h2>|.uc($cfg{'app_title'}).qq|</h2>|;
	print qq|</div>|;
	
	if(!&check_permissions('rep_fin_kardex','','')) {
		print qq|<span style="color:red;">|.&trans_txt('unauth_action').qq|</span>|;
		return
	}
	
	if (!$in{'e'}){
		print qq|<span style="color:red;">ID de empresa es requerido</span>|;
		return;
	}

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
			$add_sql .= " AND sl_skus_trans.Date <= '$in{'to_date'}' ";
			$add_sql_wh .= " AND sl_skus_trans.Date <= '$in{'to_date'}' ";
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

		print qq|<table border="0" cellpadding="7" cellspacing="0" width="100%" style="font-size:12px; font-family:verdana; font-weight:normal; border: 1px solid #222222;">
					<tr height=35px>
						<th width="10%" bgcolor=#003674><font face="century gothic, arial" color="#ffffff" size="3">SKU</th>
						<th width="10%" bgcolor=#003674><font face="century gothic, arial" color="#ffffff" size="3">UPC</th>
						<th width="40%" bgcolor=#003674><font face="century gothic, arial" color="#ffffff" size="3">Nombre</th>
						<th width="40%" bgcolor=#003674><font face="century gothic, arial" color="#ffffff" size="3">Modelo</th>
						<th width="10%" bgcolor=#003674><font face="century gothic, arial" color="#ffffff" size="3">Estatus</th>
					</tr>
					<tr>
						<td width="" align="center"><h3>$rec->{'SKU'}</h3></td>
						<td width="" align="center"><h3>$rec->{'UPC'}</h3></td>
						<td width="" align="center"><h3>$rec->{'Name'}</h3></td>
						<td width="" align="center"><h3>$rec->{'Model'}</h3></td>
						<td width="" align="center"><h3>$rec->{'Status'}</h3></td>
					</tr>
				</table><br />|;
		
				$sql = "SELECT * 
				FROM sl_warehouses 
				INNER JOIN sl_skus_trans ON sl_skus_trans.ID_warehouses=sl_warehouses.ID_warehouses
				WHERE 1 $add_sql_wh 
				GROUP BY sl_skus_trans.ID_warehouses
				ORDER BY sl_warehouses.ID_warehouses;";
				print "$sql <br /><br />";
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
						sl_skus_trans.Date
						, sl_skus_trans.Time
						, sl_skus_trans.ID_products
						, sl_skus_trans.Location
						, sl_skus_trans.Type
						, sl_skus_trans.ID_trs
						, sl_skus_trans.tbl_name
						, sl_skus_trans.Quantity
						, sl_skus_trans.Cost
						, sl_skus_trans.Cost_Adj
					FROM sl_skus_trans 
					WHERE 1 $add_sql 
					$add_por_usuario
					/* AND sl_skus_trans.Type NOT IN ('Production') */
					ORDER BY sl_skus_trans.ID_products_trans ASC;";
					print "$sql <br /><br />";
					my $sth3 = &Do_SQL($sql);
					
					## Inventario Inicial
					my $inv_inicial = 1000;
					my $inv_total = $inv_inicial;
					my $cost_inicial = 845.00;
					my $cost_total_inicial = ($inv_inicial * $cost_inicial);
					my $cost_promedio = $cost_inicial;

					if ($sth3->rows() > 0){
						$str_out .= qq|<div style="background-color: ; padding-top:10px; padding-bottom:10px; display:block; border:0px; border-bottom:1px solid silver;">
								<img src="/sitimages/user$rec2->{'Status'}.png" align=left style="margin: 7px 15px 0px 7px;">
								<font size=4 face="century gothic, verdana">$rec2->{'Name'} </font> <br>
								<font size=1 face=verdana>ID: $rec2->{'ID_warehouses'} &nbsp;&nbsp;&nbsp; Type: $rec2->{'Type'} &nbsp;&nbsp;&nbsp; Status: $rec2->{'Status'} </font>
								</div>|;

						$str_out .= qq|<table border="1" cellpadding="7" cellspacing="0" width="100%" style="font-size:12px; font-family:verdana; font-weight:normal; border: 1px solid #222222;">
								<tr>
									<th width="" colspan="3"></th>
									<th width="" colspan="3">Entradas</th>
									<th width="" colspan="3">Salidas</th>
									<th width="" colspan="3">Saldo</th>
								</tr>
								<tr>
									<th width="">Fecha</th>
									<th width="">Gaveta</th>
									<th width="">Concepto</th>
									<th width="">Cantidad</th>
									<th width="">Costo Unitario</th>
									<th width="">Costo Total</th>
									<th width="">Cantidad</th>
									<th width="">Costo Unitario</th>
									<th width="">Costo Total</th>
									<th width="">Cantidad</th>
									<th width="">Costo Unitario</th>
									<th width="">Costo Total</th>
								</tr>
								<tr style="background-color:#FFFF26;">
									<td width="">$rec3->{'Date'} $rec3->{'Time'}</td>
									<td width="">$rec3->{'Location'}</td>
									<td width="">SALDO INICIAL</td>
									<td align=right width="" ></td>
									<td align=right width="" ></td>
									<td align=right width="" ></td>
									<td align=right width="" ></td>
									<td align=right width="" ></td>
									<td align=right width="" ></td>|;
							
							## Saldos
							$str_out .= qq|
										<td align=right width="">$inv_inicial</td>
										<td align=right width="">$cost_promedio</td>
										<td align=right width="">|.&format_number($cost_total_inicial,2).qq|</td>|;

							$str_out .= qq|
									</tr>|;
						my $recs=0;
						while (my $rec3 = $sth3->fetchrow_hashref()){
							$recs_found++;
							$recs++;
							my $trans_type = $rec3->{'Type'};
							# $trans_type = $rec3->{'Type'} = 'Purchase'; #IN
							# $rec3->{'Type'} = 'Sale'; #OUT
							# $rec3->{'Type'} = 'Return'; #IN
							# $rec3->{'Type'} = 'Return to Vendor'; #OUT
							# $rec3->{'Type'} = 'Production'; # ??
							# $rec3->{'Type'} = 'Transfer Out'; #OUT
							# $rec3->{'Type'} = 'Transfer In'; #IN
							# $rec3->{'Type'} = 'Transfer'; # ?? sl_skustransfers es entrada o salida
							# $rec3->{'Type'} = 'Adjustment'; # ?? sl_adjustments es entrada o salida

							$trans_type = ($rec3->{'Type'} eq 'Purchase')? "ENTRADA":$trans_type; #IN
							$trans_type = ($rec3->{'Type'} eq 'Sale')? "SALIDA":$trans_type; #IN
							$trans_type = ($rec3->{'Type'} eq 'Return')? "ENTRADA":$trans_type; #IN
							$trans_type = ($rec3->{'Type'} eq 'Return to Vendor')? "SALIDA":$trans_type; #IN
							$trans_type = ($rec3->{'Type'} eq 'Return to Vendor')? "SALIDA":$trans_type; #IN
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
							}else{
								$inv_total -= $rec3->{'Quantity'};
								$total_cost = $rec3->{'Quantity'} * $cost_promedio;
								$cost_total_inicial = $inv_total * $cost_promedio;
							}

							$str_out .= qq|
									<tr>
										<td width="">$rec3->{'Date'} $rec3->{'Time'}</td>
										<td width="">$rec3->{'Location'}</td>
										<td width=""><a href="$cmds{$rec3->{'tbl_name'}}" target="_blank">$rec3->{'Type'} $rec3->{'ID_trs'}</a></td>|;
							
							## Entradas
							$str_out_left = qq|
										<td align=right width="" style="background-color:#99FF00;">$rec3->{'Quantity'}</td>
										<td align=right width="" style="background-color:#99FF00;">|.&format_number($rec3->{'Cost'},3).qq|</td>
										<td align=right width="" style="background-color:#99FF00;">|.&format_number($total_cost,2).qq|</td>|;
							
							## Vacuum
							$str_out_vacuum = qq|
										<td align=right width="" ></td>
										<td align=right width="" ></td>
										<td align=right width="" ></td>|;

							## Salidas
							$str_out_rigth = qq|
										<td align=right width="" style="background-color:#99FF00;">$rec3->{'Quantity'}</td>
										<td align=right width="" style="background-color:#99FF00;">|.&format_number($cost_promedio,3).qq|</td>
										<td align=right width="" style="background-color:#99FF00;">|.&format_number($total_cost,2).qq|</td>|;

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
									<th width="">|.&format_price($cost_total_inicial,2).qq|</th>
								</tr>
							</table>|;
					}
				}

				if ($recs_found){
					print $str_out;
				}else{
					print qq|<div align="center"><span style="color:red;">No se encontro información en el Sistema.</span></div>|;
				}
	}

	print "<center><br><FONT face=verdana size=2 color=#666666>MÉTODO DE VALUACIÓN DE INVENTARIO: $cfg{'acc_inventoryout_method'}</font></center>";


return;

	# print qq|<table border="1" cellpadding="8" cellspacing="0" width="90%" style="font-size:12px; border: 1px solid #222222;">|;
	# print qq|	<tr>
	# 				<th width="" colspan="2"></th>
	# 				<th width="" colspan="3">Movimientos</th>
	# 			</tr>|;
	# print qq|	<tr>
	# 				<th width="">Fecha</th>
	# 				<th width="">Concepto</th>
	# 				<th width="">Q</th>
	# 				<th width="">VU</th>
	# 				<th width="">VT</th>
	# 			</tr>|;


	my ($initial_inventory, $current_inventory, $vu_inventory, $vt_inventory);
	my $sth = &Do_SQL("SELECT ID_products, ID_warehouses, Location, Type, ID_trs, tbl_name, Quantity, Cost, Cost_Adj, Date, Time
	FROM sl_skus_trans 
	WHERE 1
	AND ID_products='$in{'id_products'}'
	AND ID_warehouses='$in{'id_warehouses'}'
	AND Quantity > 0
	ORDER BY ID_products_trans limit 1000;");
	$initial_inventory = 500;
	$rows = 0;
	while (my $rec = $sth->fetchrow_hashref()){
		$rows++;

		if ($rows == 1){
			$current_inventory = $initial_inventory;
		}
		
		# Depende si es + o -
		my $left = 0;
		my $right = 0;
		if ($rec->{'Type'} eq 'Sale' or $rec->{'Type'} eq 'Return to Vendor'){
			$current_inventory = $current_inventory - $rec->{'Quantity'};
			$right=1;
			$style = qq|style="color:red;font-weight:bold;"|
		}elsif ($rec->{'Type'} eq 'Purchase' or $rec->{'Type'} eq 'Production' or $rec->{'Type'} eq 'Adjustment' or $rec->{'Type'} eq 'Return'){
			$current_inventory = $current_inventory + $rec->{'Quantity'};
			$left=1;
			$style = qq|style="color:green;font-weight:bold;"|
		}
		$vu_inventory = $rec->{'Cost'};
		$vt_inventory = $current_inventory * $rec->{'Cost'};
		my $vt = ($rec->{'Quantity'} * $rec->{'Cost'});

		print qq|<tr>
					<td align="left">$rec->{'Date'}</td>
					<td align="left">$rec->{'Type'}</td>|;
		if ($left == 1){
			print qq|
					<td align="right" $style>$rec->{'Quantity'}</td>
					<td align="right" $style>$rec->{'Cost'}</td>
					<td align="left" $style>$vt</td>|;
		}else{
			print qq|
					<td align="right">&nbsp;</td>
					<td align="right">&nbsp;</td>
					<td align="left">&nbsp;</td>|;
			
		}

		if ($right == 1){
			print qq|
					<td align="right" $style>$rec->{'Quantity'}</td>
					<td align="right" $style>$rec->{'Cost'}</td>
					<td align="left" $style>$vt</td>|;
		}else{
			print qq|
					<td align="right">&nbsp;</td>
					<td align="right">&nbsp;</td>
					<td align="left">&nbsp;</td>|;
			
		}

		print qq|
					<td align="right">$current_inventory</td>
					<td align="right">$vu_inventory</td>
					<td align="left">$vt_inventory</td>|;
		print qq|
				</tr>|;

	}
	
	print qq|</table><br>|;
return;
	#  - - - - - - - - - - - - - - - - - - - - - - - - - - -
	## Analizando Almacenes en sl_warehouses_location
	#  - - - - - - - - - - - - - - - - - - - - - - - - - - -
	print qq|<table border="1" cellpadding="8" cellspacing="0" width="50%" style="font-size:12px; border: 1px solid #222222;">|;
	print qq|	<tr>
					<th width="35%">sl_warehouses_location.ID_warehouses</th>
					<th>Accion</th>
				</tr>|;
	
	my $sth = &Do_SQL("SELECT sl_warehouses_location.ID_warehouses
	FROM sl_warehouses_location
	LEFT JOIN sl_warehouses ON sl_warehouses_location.ID_warehouses=sl_warehouses.ID_warehouses
	WHERE sl_warehouses.Name IS NULL
	GROUP BY sl_warehouses_location.ID_warehouses
	ORDER BY sl_warehouses_location.ID_warehouses;");
	while (my $rec = $sth->fetchrow_hashref()){
		$sql = "DELETE FROM sl_warehouses_location WHERE ID_warehouses = '$rec->{'ID_warehouses'}';";
		print qq|<tr>
					<td align="right">$rec->{'ID_warehouses'}</td>
					<td>$sql</td>
				</tr>|;
		&Do_SQL($sql) if ($in{'process'} eq 'commit');
	}
	
	print qq|</table><br>|;

	#  - - - - - - - - - - - - - - - - - - - - - - - - - - -
	## Buscando diferencias entre tablas
	#  - - - - - - - - - - - - - - - - - - - - - - - - - - -
	print qq|<table border="1" cellpadding="5" cellspacing="0" width="100%" style="font-size:12px; border: 1px solid #222222;">|;
	print qq|	<tr>
					<th colspan="4">sl_warehouses_location</th>
					<th colspan="4">sl_skus_cost</th>
					<th></th>
				</tr>|;

	print qq|	<tr>
					<th>#</th>
					<th>ID_warehouses</th>
					<th>ID_products</th>
					<th>Quantity</th>
					<th></th>
					<th>ID_warehouses</th>
					<th>ID_products</th>
					<th>Quantity</th>
					<th></th>
					<th>Diference</th>
				</tr>|;
	my $sth = &Do_SQL("
	SELECT 
		sl_warehouses_location.ID_warehouses, sl_warehouses_location.ID_products, SUM(sl_warehouses_location.Quantity)Quantity
		, sl_skus_cost.ID_warehouses sc_ID_warehouses, sl_skus_cost.ID_products sc_ID_products, SUM(sl_skus_cost.Quantity)sc_Quantity
		, (SUM(sl_warehouses_location.Quantity) - ifnull(SUM(sl_skus_cost.Quantity),0))Diference

	FROM (
		SELECT
			sl_warehouses_location.ID_warehouses
			, sl_warehouses_location.ID_products
			, SUM(sl_warehouses_location.Quantity)Quantity
		FROM sl_warehouses_location 
		GROUP BY sl_warehouses_location.ID_warehouses, sl_warehouses_location.ID_products
	)sl_warehouses_location 
	INNER JOIN sl_warehouses ON sl_warehouses_location.ID_warehouses=sl_warehouses.ID_warehouses
	LEFT JOIN (
		SELECT 
			sl_skus_cost.ID_warehouses
			, sl_skus_cost.ID_products
			, SUM(sl_skus_cost.Quantity)Quantity
		FROM sl_skus_cost
		WHERE 1
		AND sl_skus_cost.Cost IS NOT NULL
		AND sl_skus_cost.Cost > 0
		AND sl_skus_cost.Quantity > 0
		GROUP BY sl_skus_cost.ID_warehouses, sl_skus_cost.ID_products
	)sl_skus_cost ON sl_skus_cost.ID_warehouses=sl_warehouses_location.ID_warehouses AND sl_skus_cost.ID_products=sl_warehouses_location.ID_products
	WHERE 1
	GROUP BY sl_warehouses_location.ID_warehouses, sl_warehouses_location.ID_products
	ORDER BY sl_warehouses_location.ID_warehouses, sl_warehouses_location.ID_products");
	my $recs = 0;
	my $recs_dif = 0;
	my $neg_fix=0;
	while (my $rec = $sth->fetchrow_hashref()){
		$recs++;
		$recs_dif++ if ($rec->{'Diference'} != 0);
		my $style = ($rec->{'Diference'} == 0)? qq|style="display:none;background-color:#C1F325;color:#000"|:'';
		$style = ($rec->{'Diference'} < 0)? qq|style="background-color:#FF26A8;color:#000"|:$style;
		$style = (!$rec->{'sc_ID_warehouses'})? qq|style="background-color:#FF784D;color:#000"|:$style;
		print qq|<tr $style >
					<td align="right">$recs</td>
					<td align="right">$rec->{'ID_warehouses'}</td>
					<td align="right">$rec->{'ID_products'}</td>
					<td align="right">$rec->{'Quantity'}</td>
					<td>--</td>
					<td align="right">$rec->{'sc_ID_warehouses'}</td>
					<td align="right">$rec->{'sc_ID_products'}</td>
					<td align="right">$rec->{'sc_Quantity'}</td>
					<td>--</td>
					<td align="right">$rec->{'Diference'}</td>
				</tr>|;
		
		#  - - - - - - - - - - - - - - - - - - - - - - - - - - -
		#  - - - - - - - - - - - - - - - - - - - - - - - - - - -
		# 					ANALISIS DE COSTOS
		#  - - - - - - - - - - - - - - - - - - - - - - - - - - -
		#  - - - - - - - - - - - - - - - - - - - - - - - - - - -
		if ($rec->{'Diference'} != 0 and $rec->{'Quantity'} > 0) {

			print qq|<tr>
						<td colspan="10">
							<table border="1" cellpadding="5" cellspacing="0" width="100%" style="font-size:12px; border: 1px solid #222222;">|;

			my $sth2 = &Do_SQL("SELECT 
				sl_skus_cost.ID_skus_cost
				, sl_skus_cost.Tblname
				, sl_skus_cost.ID_warehouses
				, sl_skus_cost.ID_products
				, sl_skus_cost.Quantity
				, sl_skus_cost.Cost
				, sl_skus_cost.Date
				, sl_skus_cost.Time
			FROM sl_skus_cost 
			WHERE 1
			AND sl_skus_cost.ID_warehouses='$rec->{'ID_warehouses'}'
			AND sl_skus_cost.ID_products='$rec->{'ID_products'}'
			AND sl_skus_cost.Cost IS NOT NULL
			AND sl_skus_cost.Cost > 0
			AND sl_skus_cost.Quantity > 0
			ORDER BY sl_skus_cost.ID_warehouses, sl_skus_cost.ID_products, sl_skus_cost.Date DESC, sl_skus_cost.Time DESC");
			my $recs2 = 0;
			my $last_id;
			my $first_id;
			while (my $rec2 = $sth2->fetchrow_hashref()){
				$recs2++;
				$last_id = $rec2->{'ID_skus_cost'};
				$first_id = $rec2->{'ID_skus_cost'} if ($recs2 == 1);
				print qq|
					<tr>
						<td align="right" style="background-color:#0098FF">$recs2</td>
						<td align="right">$rec2->{'ID_skus_cost'}</td>
						<td align="right">$rec2->{'Tblname'}</td>
						<td align="right">$rec2->{'ID_warehouses'}</td>
						<td align="right">$rec2->{'ID_products'}</td>
						<td align="right">$rec2->{'Quantity'}</td>
						<td align="right">$rec2->{'Cost'}</td>
						<td align="right">$rec2->{'Date'}</td>
						<td align="right">$rec2->{'Time'}</td>
					</tr>|;
			}
			
			if ($recs2 == 1 and $rec->{'Diference'} > 0){
				$easy_fix++;
				$sql_fix = "UPDATE sl_skus_cost SET Quantity=(Quantity+ABS($rec->{'Diference'})) WHERE ID_skus_cost='$last_id' LIMIT 1;";
				print qq|
					<tr>
						<td align="right" colspan="9" style="background-color:#FFFF00">$sql_fix</td>
					</tr>|;
				&Do_SQL($sql_fix) if ($in{'process'} eq 'commit');
			}

			if($recs2 > 1 and $rec->{'Diference'} > 0){
				$easy_fix++;
				$sql_fix = "UPDATE sl_skus_cost SET Quantity=(Quantity+ABS($rec->{'Diference'})) WHERE ID_skus_cost='$first_id' LIMIT 1;";
				print qq|
					<tr>
						<td align="right" colspan="9" style="background-color:#26FF26">$sql_fix</td>
					</tr>|;
				&Do_SQL($sql_fix) if ($in{'process'} eq 'commit');

			}

			## Diferencias Negativas
			if ($recs2 == 1 and $rec->{'Diference'} < 0){
				$easy_fix++;
				$sql_fix = "UPDATE sl_skus_cost SET Quantity=(Quantity-ABS($rec->{'Diference'})) WHERE ID_skus_cost='$last_id' LIMIT 1;";
				print qq|
					<tr>
						<td align="right" colspan="9" style="background-color:#26FFFF">$sql_fix</td>
					</tr>|;
				&Do_SQL($sql_fix) if ($in{'process'} eq 'commit');
			}

			if ($recs2 > 1 and $rec->{'Diference'} < 0){
				my $sth3 = &Do_SQL("SELECT 
					sl_skus_cost.ID_skus_cost
					, sl_skus_cost.Tblname
					, sl_skus_cost.ID_warehouses
					, sl_skus_cost.ID_products
					, sl_skus_cost.Quantity
					, sl_skus_cost.Cost
					, sl_skus_cost.Date
					, sl_skus_cost.Time
				FROM sl_skus_cost 
				WHERE 1
				AND sl_skus_cost.ID_warehouses='$rec->{'ID_warehouses'}'
				AND sl_skus_cost.ID_products='$rec->{'ID_products'}'
				AND sl_skus_cost.Cost IS NOT NULL
				AND sl_skus_cost.Cost > 0
				ORDER BY sl_skus_cost.Quantity DESC");
				my $jumper=0;
				my $dif=abs($rec->{'Diference'});
				# Buscar si hay uno con la cantidad >= a la diferencia
				while (my $rec3 = $sth3->fetchrow_hashref()){
					if (!$jumper){
						if ($rec3->{'Quantity'} == abs($rec->{'Diference'}) ){
							# Si hay y es igual se elimina el registro
							$jumper=1;
							$easy_fix++;
							$sql_fix = "DELETE FROM sl_skus_cost WHERE ID_skus_cost='$rec3->{'ID_skus_cost'}' LIMIT 1;";
							print qq|
								<tr>
									<td align="right" colspan="9" style="background-color:#26FFFF">$sql_fix</td>
								</tr>|;
							&Do_SQL($sql_fix) if ($in{'process'} eq 'commit');
						}elsif ($rec3->{'Quantity'} > abs($rec->{'Diference'}) ){
							# Si hay y es mayor a ese se le descuenta la diferecia
							$jumper=1;
							$easy_fix++;
							$sql_fix = "UPDATE sl_skus_cost SET Quantity=(Quantity-ABS($rec->{'Diference'})) WHERE ID_skus_cost='$rec3->{'ID_skus_cost'}' LIMIT 1;";
							print qq|
								<tr>
									<td align="right" colspan="9" style="background-color:#26FFFF">$sql_fix</td>
								</tr>|;
							&Do_SQL($sql_fix) if ($in{'process'} eq 'commit');
						}
					}

				}
				
				#  - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
				#  - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
				# Si aun con el de arriba no se corrigio se procede a hacer un descuento a la malagueña
				# Se iran descontando en cada registro recorrido hasta lograr descontar el total
				#  - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
				#  - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

				if (!$jumper){
					$sql_fix = "NEXT";
					print qq|
						<tr>
							<td align="right" colspan="9" style="background-color:#26FFFF">$sql_fix</td>
						</tr>|;

					my $sth3 = &Do_SQL("SELECT 
						sl_skus_cost.ID_skus_cost
						, sl_skus_cost.Tblname
						, sl_skus_cost.ID_warehouses
						, sl_skus_cost.ID_products
						, sl_skus_cost.Quantity
						, sl_skus_cost.Cost
						, sl_skus_cost.Date
						, sl_skus_cost.Time
					FROM sl_skus_cost 
					WHERE 1
					AND sl_skus_cost.ID_warehouses='$rec->{'ID_warehouses'}'
					AND sl_skus_cost.ID_products='$rec->{'ID_products'}'
					AND sl_skus_cost.Cost IS NOT NULL
					AND sl_skus_cost.Cost > 0
					ORDER BY sl_skus_cost.Quantity DESC");
					my $dif=abs($rec->{'Diference'});
					# Buscar si hay uno con la cantidad >= a la diferencia
					while (my $rec3 = $sth3->fetchrow_hashref()){
						if ($dif > 0){
							if ($rec3->{'Quantity'} >  $dif){
								# Si hay y es mayor a ese se le descuenta la diferecia
								$sql_fix = "/*$dif MAGIC $rec3->{'Quantity'}*/ UPDATE sl_skus_cost SET Quantity=(Quantity-$dif) WHERE ID_skus_cost='$rec3->{'ID_skus_cost'}' LIMIT 1;";
								print qq|
									<tr>
										<td align="right" colspan="9" style="background-color:#26FFFF">$sql_fix</td>
									</tr>|;
								&Do_SQL($sql_fix) if ($in{'process'} eq 'commit');
							}else{
								# Si hay y es igual se elimina el registro
								$sql_fix = "/*$dif MAGIC $rec3->{'Quantity'}*/ DELETE FROM sl_skus_cost WHERE ID_skus_cost='$rec3->{'ID_skus_cost'}' LIMIT 1;";
								print qq|
									<tr>
										<td align="right" colspan="9" style="background-color:#26FFFF">$sql_fix</td>
									</tr>|;
								&Do_SQL($sql_fix) if ($in{'process'} eq 'commit');
							}

							$easy_fix++;
							$dif -= $rec3->{'Quantity'};
						}
					}
				}
			}

			## Con costo Calculado
			if (!$rec->{'sc_ID_warehouses'}){
				my $cost = &load_sltvcost($rec->{'ID_products'});
				if ($cost > 0){
					$easy_fix++;
					$sql_fix = "INSERT INTO sl_skus_cost SET ID_products='$rec->{'ID_products'}', ID_warehouses='$rec->{'ID_warehouses'}', Tblname='sl_manifests', Quantity=ABS($rec->{'Diference'}), Cost='$cost', Date=CURDATE(), Time=CURTIME(), ID_admin_users='1';";
					print qq|
						<tr>
							<td align="right" colspan="9" style="background-color:#9BE6BB">$sql_fix</td>
						</tr>|;
					&Do_SQL($sql_fix) if ($in{'process'} eq 'commit');
				}else{
					$sql_fix = "DIFICIL";
					$hard_fix++;
					print qq|
						<tr>
							<td align="right" colspan="9" style="background-color:#9BE6BB">$sql_fix</td>
						</tr>|;
				}
			}

			print qq|
						</table>
					</td>
				</tr>|;
		}

		# No tenemos porque tener Qty Negativos en sl_warehouses_location
		# Negativo encontrado, Negativo eliminado
		if ($rec->{'Quantity'} <= 0) {
			$neg_fix++;
				print qq|<tr><td colspan="10"><table border="1" cellpadding="5" cellspacing="0" width="100%" style="font-size:12px; border: 1px solid #222222;">|;
				
				$sql_fix = "/*CLEAN*/ DELETE FROM sl_warehouses_location WHERE ID_warehouses='$rec->{'ID_warehouses'}' AND ID_products='$rec->{'ID_products'}';";
				print qq|	<tr>
								<td>$sql_fix</td>
							</tr>|;
				&Do_SQL($sql_fix) if ($in{'process'} eq 'commit');
				
				$sql_fix = "/*CLEAN*/ DELETE FROM sl_skus_cost WHERE ID_warehouses='$rec->{'ID_warehouses'}' AND ID_products='$rec->{'ID_products'}';";
				print qq|	<tr>
								<td>$sql_fix</td>
							</tr>|;
				&Do_SQL($sql_fix) if ($in{'process'} eq 'commit');

				print qq|</td></tr></table>|;
		}
	}
	
	print qq|</table>|;
	print qq|<br>Registros encontrados: $recs|;
	print qq|<br>Diferencias detectadas: $recs_dif|;
	print qq|<br>Facilmente corregidos: $easy_fix|;
	print qq|<br>Casos donde se requiere el costo: $hard_fix|;
	print qq|<br>Casos de cantidad negativas: $hard_fix_quantity|;
	print qq|<br>Casos de cantidad negativas y en cero eliminados: $neg_fix|;

	#|<----------------------------------------------------------------------------------------
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