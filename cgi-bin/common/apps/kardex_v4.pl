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
	    line-heigth:45px;
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



	#cuadros td {
	     border-right: 1px solid #777777; border-bottom: 1px solid #777777;
	        }
	a:link {
		text-decoration:none;
		color: #666;
	}
	a:hover {
		text-decoration:underline;
		color: #409CD8;
	}    
	 

		</STYLE>
	</head>
	<body>
	|;	

	print qq|<div align="center">|;
	print qq|<h2>|.uc($cfg{'app_title'}).qq|</h2>|;
	print qq|<h2>K A R D E X - MOVIMIENTOS DE ALMACEN</h2>|;
	print qq|</div>|;
	
	if(!&check_permissions('rep_fin_kardex','','')) {
		print qq|<span style="color:red;">|.&trans_txt('unauth_action').qq|</span>|;
		return
	}
	
	if (!$in{'e'}){
		print qq|<span style="color:red;">ID de empresa es requerido</span>|;
		return;
	}

	my $add_sql_sku = '';

	if ((!$in{'id_products'} or length(int($in{'id_products'}))!=4) and (!$in{'upc'} or $in{'upc'} eq '')){
		print qq|<span style="color:red;">SKU o UPC Invalido: $in{'id_products'}</span>|;
		return;
	}else{
		$add_sql_sku = ($in{'id_products'})? " AND sl_parts.ID_parts = '".int($in{'id_products'})."' ":"";
		$add_sql_sku .= ($in{'upc'})? " AND sl_skus.UPC = TRIM('".$in{'upc'}."') ":"";
		if ($in{'id_products'}){
			$in{'id_parts'} = int($in{'id_products'});
			$in{'id_products'} = 400000000 + int($in{'id_products'});
		}
	}

	$in{'id_warehouses'} =~ s/\|/\,/g;

	my ($add_sql_wh, $add_sql_wh2);
	$add_sql .= ($in{'id_products'})? " AND sl_skus_trans.ID_products = ".int($in{'id_products'})." ":"";
	$add_sql_skus .= ($in{'upc'})? " AND sl_skus.UPC = TRIM('".$in{'upc'}."') ":"";
	$add_sql_wh .= ($in{'id_products'})? " AND sl_skus_trans.ID_products = ".int($in{'id_products'})." ":"";
	$add_sql .= ($in{'id_warehouses'})? " AND sl_skus_trans.ID_warehouses = ".int($in{'id_warehouses'})." ":"";
	$add_sql_wh .= ($in{'id_warehouses'})? " AND sl_skus_trans.ID_warehouses = (".$in{'id_warehouses'}.") ":"";
	$add_sql_wh2 = ($in{'id_warehouses'})? " AND ID_warehouses IN(".$in{'id_warehouses'}.") ":"";
	
	$add_sql_parts .= ($in{'id_products'})? " AND sl_skus_trans.ID_products = ".int($in{'id_products'})." ":"";
	$add_sql_parts .= ($in{'id_warehouses'})? " AND sl_skus_trans.ID_warehouses = ".int($in{'id_warehouses'})." ":"";

	my $id_products_trans = 0;
	# Ultimos ID registrados en sl_skus_trans al momento de sacar la fotografia del inventario
	$id_products_trans = 4916812 if ($in{'e'} == 2 or $in{'e'} == 10);
	$id_products_trans = 114263 if ($in{'e'} == 3 or $in{'e'} == 7);
	$id_products_trans = 211068 if ($in{'e'} == 4 or $in{'e'} == 12);
	$id_products_trans = 108872 if ($in{'e'} == 11 or $in{'e'} == 13);
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
			$add_sql .= " AND sl_skus_trans.Date <= '$in{'to_date'}' ";
			$add_sql_wh .= " AND sl_skus_trans.Date <= '$in{'to_date'}' ";
		}
	}

	if ($in{'from_date'} eq '' and  $in{'to_date'} eq ''){
		$add_sql .= " AND sl_skus_trans.Date = CURDATE() ";
		$add_sql_wh .= " AND sl_skus_trans.Date = CURDATE() ";
	}

	### Mostrar siempre la info. de aduana
	$in{'custom_info'} = 1;

	#### Total decimales
	$decimal = 2;

	$sql = "SELECT sl_parts.*, sl_skus.ID_sku_products SKU, sl_skus.UPC, (SELECT left_quantity_total FROM sl_skus_trans WHERE sl_skus_trans.ID_products = sl_skus.ID_sku_products ORDER BY sl_skus_trans.Date DESC, sl_skus_trans.Time DESC, sl_skus_trans.ID_products_trans DESC LIMIT 1) left_quantity_total 
	FROM sl_parts 
	INNER JOIN sl_skus ON sl_parts.ID_parts=sl_skus.ID_products AND (400000000+sl_parts.ID_parts)=sl_skus.ID_sku_products
	WHERE sl_parts.ID_parts = '$in{'id_parts'}';";
	# print "$sql <br />";
	my $sth = &Do_SQL($sql);
	my $recs_found = 0;
	#my $str_out = '';
	while (my $rec = $sth->fetchrow_hashref()){
		my ($cost_avg) = &get_average_cost($rec->{'SKU'});
		if ($cost_avg == ''){ $cost_avg = '0.00'; }

		print qq|
		<table border="0"  cellpadding="3" cellspacing="0" width="100%" style="font-size:12px; font-family:verdana; font-weight:normal; border: 1px solid #222222;">
			<tr heigth=35px>
				<th width="10%" bgcolor="#003674"><font face="century gothic, arial" color="#ffffff" size="3">SKU</th>
				<th width="10%" bgcolor="#003674"><font face="century gothic, arial" color="#ffffff" size="3">UPC</th>
				<th width="40%" bgcolor="#003674"><font face="century gothic, arial" color="#ffffff" size="3">Nombre</th>
				<th width="10%" bgcolor="#003674"><font face="century gothic, arial" color="#ffffff" size="3">Inventario</th>
				<th width="10%" bgcolor="#003674"><font face="century gothic, arial" color="#ffffff" size="3">Costo \$</th>
				<th width="10%" bgcolor="#003674"><font face="century gothic, arial" color="#ffffff" size="3">Estatus</th>
			</tr>
			<tr>
				<td width="" align="center"><h3>$rec->{'SKU'}</h3></td>
				<td width="" align="center"><h3>$rec->{'UPC'}</h3></td>
				<td width="" align="center"><h3>$rec->{'Name'}</h3></td>
				<td width="" align="center"><h3>$rec->{'left_quantity_total'}</h3></td>
				<td width="" align="center"><h3>$cost_avg</h3></td>
				<td width="" align="center"><h3>$rec->{'Status'}</h3></td>
			</tr>
		</table><br />|;

		if (!$in{'id_products'}){
			$add_sql .= " AND sl_skus_trans.ID_products = '".$rec->{'SKU'}."' ";
			$add_sql_wh .= " AND sl_skus_trans.ID_products = '".$rec->{'SKU'}."' ";
		}
		
		$sql = "SELECT sl_warehouses.* 
		FROM sl_warehouses 
		WHERE 1 $add_sql_wh2
		ORDER BY sl_warehouses.ID_warehouses;";
		# print "$sql <br /><br />";
		my $sth2 = &Do_SQL($sql);
		my $str_wh = '';
		while (my $rec2 = $sth2->fetchrow_hashref()){
			my $total_entradas_qty = 0;
			my $total_entradas_cost = 0;
			my $total_salidas_qty = 0;
			my $total_salidas_cost = 0;
			my $total_saldos_qty = 0;
			my $total_saldos_cost = 0;
			my $total_existencias_cost = 0;
			my $title_custom_info = '';
			my $id_custom_info = '';
			my $title_colspan_existencias = 7;
			my $extra_cell_initial = '';
			my $extra_cell_total = '';

			# $add_por_usuario = ($usr{'id_admin_users'} <= 3000)? "":" AND sl_skus_trans.Quantity < 400000000 ";

			if($in{'custom_info'}){
				$title_custom_info = '<th style="border-right: 1px solid #777777; border-bottom: 1px solid #777777;">Info Aduana</th>';
				$title_colspan_existencias += 1;
			}

			print qq|
			<div style="background-color: ; padding-top:10px; padding-bottom:10px; display:block; border:0px; border-bottom:1px solid silver;">
				<img src="/sitimages/user$rec2->{'Status'}.png" align=left style="margin: 7px 15px 0px 7px;">
				<font size=4 face="century gothic, verdana">$rec2->{'Name'} </font><br>
				<font size=1 face=verdana>ID: $rec2->{'ID_warehouses'} &nbsp;&nbsp;&nbsp; Type: $rec2->{'Type'} &nbsp;&nbsp;&nbsp; Status: $rec2->{'Status'} </font>
			</div>
			<table border="0" id="cuadros" cellpadding="7" cellspacing="0" width="100%" style="font-size:10px; font-family:verdana; font-weight:normal; border: 1px solid #777777; border-right:0px;">
				<tr style="background-color:#003674 ;color:#ffffff;">
					<th colspan="3"></th>
					<th colspan="3">Entradas</th>
					<th colspan="3">Salidas</th>
					<th colspan="$title_colspan_existencias">Existencias</th>
				</tr>
				<tr style="background-color:#CAE1FF;">
					<th style="border-right: 1px solid #777777; border-bottom: 1px solid #777777;">Fecha</th>
					<th style="border-right: 1px solid #777777; border-bottom: 1px solid #777777;">Gaveta</th>
					<th style="border-right: 1px solid #777777; border-bottom: 1px solid #777777;">Concepto</th>
					<th style="border-right: 1px solid #777777; border-bottom: 1px solid #777777;">Cantidad</th>
					<th style="border-right: 1px solid #777777; border-bottom: 1px solid #777777;">Costo Unitario</th>
					<th style="border-right: 1px solid #777777; border-bottom: 1px solid #777777;">Total</th>
					<th style="border-right: 1px solid #777777; border-bottom: 1px solid #777777;">Cantidad</th>
					<th style="border-right: 1px solid #777777; border-bottom: 1px solid #777777;">Costo Unitario</th>
					<th style="border-right: 1px solid #777777; border-bottom: 1px solid #777777;">Total</th>
					<th style="border-right: 1px solid #777777; border-bottom: 1px solid #777777;">Cantidad</th>
					<th style="border-right: 1px solid #777777; border-bottom: 1px solid #777777;">Cantidad Total</th>
					<th style="border-right: 1px solid #777777; border-bottom: 1px solid #777777;">Costo Promedio</th>
					<th style="border-right: 1px solid #777777; border-bottom: 1px solid #777777;">CA</th>
					<th style="border-right: 1px solid #777777; border-bottom: 1px solid #777777;">CA Promedio</th>
					<th style="border-right: 1px solid #777777; border-bottom: 1px solid #777777;">CC</th>
					|.$title_custom_info.qq|					
					<th style="border-right: 1px solid #777777; border-bottom: 1px solid #777777;">Total</th>
				</tr>|;

				$sql ="SELECT 
					ID_products_trans
					, sl_skus_trans.Date
					, sl_skus_trans.Time
					, sl_skus_trans.ID_products
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
					, sl_skus_trans.Cost_Adj_Avg
					, sl_skus_trans.Cost_Add
					, CASE Type 
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
				FROM sl_skus_trans 
				WHERE 1 
				$add_sql 
				AND sl_skus_trans.ID_warehouses=$rec2->{'ID_warehouses'}
				/*$sql_restriction*/
				ORDER BY sl_skus_trans.Date DESC, sl_skus_trans.Time DESC, sl_skus_trans.ID_products_trans DESC;";
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

					## Este costo va variar cada que haya una entrada
					
					if ($trans_type eq 'ENTRADA'){
						$inv_total += $rec3->{'Quantity'};
						#$cost_promedio = ($inv_total > 0)?($cost_total_inicial + $total_cost) / $inv_total:0;
						$cost_total_inicial = $inv_total * $cost_promedio;
					}elsif($trans_type eq 'SALIDA'){
						$inv_total -= $rec3->{'Quantity'};
						# $cost_total_inicial = $inv_total * $cost_promedio;
					}

					$total_cost_avg = $rec3->{'Cost_Avg'}*$rec3->{'Quantity'};
					$total_cost = $rec3->{'Cost'}*$rec3->{'Quantity'};


					$str_out .= qq|
							<tr>
								<td width="">$rec3->{'Date'} $rec3->{'Time'}</td>
								<td width="">$rec3->{'Location'}</td>
								<td width=""><a href="$cmds{$rec3->{'tbl_name'}}" target="_blank">$rec3->{'Type'} $rec3->{'ID_trs'}</a> $skip_accounting</td>|;
					
					## Entradas
					$str_out_left = qq|
								<td align=right width="" style="background-color:#cce769;">$rec3->{'Quantity'}</td>
								<td align=right width="" style="background-color:#cce769;">|.&format_number($rec3->{'Cost'},$decimal).qq|</td>
								<td align=right width="" style="background-color:#cce769;">|.&format_number($total_cost,$decimal).qq|</td>|;
					
					## Vacuum
					$str_out_vacuum = qq|
								<td align=right width="" ></td>
								<td align=right width="" ></td>
								<td align=right width="" ></td>|;

					## Salidas
					$str_out_rigth = qq|
								<td align=right width="" style="background-color:#FFAA72;">$rec3->{'Quantity'}</td>
								<td align=right width="" style="background-color:#FFAA72;">|.&format_number($rec3->{'Cost'},$decimal).qq|</td>
								<td align=right width="" style="background-color:#FFAA72;">|.&format_number($total_cost,$decimal).qq|</td>|;

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
						if(int($rec3->{'id_customs_info'}) > 0){
							my $cinfo = &Do_SQL("SELECT import_declaration_number, import_declaration_date, customs, CompanyName
												 FROM cu_customs_info 
												 	LEFT JOIN sl_vendors ON cu_customs_info.ID_vendors = sl_vendors.ID_vendors
												 WHERE cu_customs_info.ID_customs_info = ".$rec3->{'id_customs_info'}.";");
							$cust_info = $cinfo->fetchrow_hashref();

							$id_custom_info = qq|<td align="left" width="" nowrap>$cust_info->{'import_declaration_number'} - $cust_info->{'import_declaration_date'}<br />$cust_info->{'customs'}</td>|;
						} else {
							$id_custom_info = qq|<td align="left" width="" nowrap>&nbsp;</td>|;
						}
						$extra_cell_initial = '<td  align=right width="" ></td>';
						$extra_cell_total = '<th width=""></th>';
					}


					## Existencias
					$str_out .= qq|
								<td align=right width="" >|.$rec3->{'left_quantity'}.qq|</td>
								<td align=right width="" >|.$rec3->{'left_quantity_total'}.qq|</td>
								<td align=right width="" style="$css_cost">|.&format_number($rec3->{'Cost_Avg'},$decimal).qq|</td>
								<td align=right width="" >|.&format_number($rec3->{'Cost_Adj'},$decimal).qq|</td>
								<td align=right width="" >|.&format_number($rec3->{'Cost_Adj_Avg'},$decimal).qq|</td>
								<td align=right width="" >|.&format_number($rec3->{'Cost_Add'},$decimal).qq|</td>
								$id_custom_info
								<td align=right width="" >|.&format_number($rec3->{'Cost_Avg'}*$rec3->{'left_quantity'},$decimal).qq|</td>
							</tr>|;

					$total_existencias_cost += $rec3->{'Cost_Avg'}*$rec3->{'left_quantity'};


					# or $last_date ne $rec3->{'Date'}
					if ($recs == $total_recs){
						my $sql = "SELECT sl_skus_trans.Cost, sl_skus_trans.Cost_Avg, sl_skus_trans.left_quantity, sl_skus_trans.left_quantity_total
									FROM sl_skus_trans
									WHERE 1 
										AND sl_skus_trans.ID_products='".$in{'id_products'}."' 
										AND sl_skus_trans.Date >= '".$in{'from_date'}."' 
									ORDER BY DATE, TIME, ID_products_trans
									LIMIT 1;";
						my $sth = &Do_SQL($sql);
						my ($this_cost, $this_cost_avg, $this_left_qty, $this_left_qty_total) = $sth->fetchrow_array();

						$str_out .= qq|
						<tr style="background-color:#fafa7b;">
							<td  width="">$rec3->{'Date'}</td>
							<td  width="" align="center">---</td>
							<td  width="">INVENTARIO INICIAL</td>
							<td  align=right width="" ></td>
							<td  align=right width="" ></td>
							<td  align=right width="" ></td>
							<td  align=right width="" ></td>
							<td  align=right width="" ></td>
							<td  align=right width="" ></td>
							<td align=right width="">|.$rec3->{'InvInicial'}.qq|</td>
							<td  align=right width="" ></td>
							<td align=right width="">|.&format_price($this_cost_avg,2).qq|</td>
							<td  align=right width="" ></td>
							<td  align=right width="" ></td>
							<td  align=right width="" ></td>
							$extra_cell_initial
							<td align=right width="">|.&format_number(($this_cost_avg * $rec3->{'InvInicial'}),$decimal).qq|</td>
						</tr>|;

					}
					$last_date = $rec3->{'Date'};

				}

				if( int($recs) == 0 ){
					my $sql = "SELECT sl_skus_trans.Cost_Avg
								FROM sl_skus_trans
								WHERE 1 
									AND sl_skus_trans.ID_products='".$in{'id_products'}."' 
									AND sl_skus_trans.Date >= '".$in{'from_date'}."' 
								ORDER BY DATE, TIME, ID_products_trans
								LIMIT 1;";
					my $sth = &Do_SQL($sql);
					my ($this_cost_avg) = $sth->fetchrow_array();

					my $sql = "SELECT SUM(Quantity) FROM sl_warehouses_location WHERE ID_products='".$in{'id_products'}."' AND ID_warehouses='".$rec2->{'ID_warehouses'}."' GROUP BY ID_warehouses;";
					my $sth = &Do_SQL($sql);
					my $this_left_qty = $sth->fetchrow();
					$this_left_qty = 0 if(!$this_left_qty);					

					$str_out .= qq|
					<tr style="background-color:#fafa7b;">
						<td  width="">$rec3->{'Date'}</td>
						<td  width="" align="center">---</td>
						<td  width="">INVENTARIO INICIAL</td>
						<td  align=right width="" ></td>
						<td  align=right width="" ></td>
						<td  align=right width="" ></td>
						<td  align=right width="" ></td>
						<td  align=right width="" ></td>
						<td  align=right width="" ></td>
						<td align=right width="">|.$this_left_qty.qq|</td>
						<td  align=right width="" ></td>
						<td align=right width="">|.&format_price($this_cost_avg,2).qq|</td>
						<td  align=right width="" ></td>
						<td  align=right width="" ></td>
						<td  align=right width="" ></td>
						$extra_cell_initial
						<td align=right width="">|.&format_number(($this_cost_avg * $this_left_qty),$decimal).qq|</td>
					</tr>|;
				}
				
				$str_out .= qq|
						<tr>
							<th width="" colspan="3" align="right">Totales</th>
							<th width="" align="right">|.&format_number($total_entradas_qty).qq|</th>
							<th width=""></th>
							<th width="" align="right">|.&format_price($total_entradas_cost,$decimal).qq|</th>
							<th width="" align="right">|.&format_number($total_salidas_qty).qq|</th>
							<th width=""></th>
							<th width="" align="right">|.&format_price($total_salidas_cost,$decimal).qq|</th>
							<th width=""><!-- |.&format_number($inv_total).qq| --></th>
							<th width=""></th>
							<th width=""></th>
							<th width=""></th>
							<th width=""></th>
							<th width=""></th>
							$extra_cell_total
							<th width="" style="border-right: 1px solid #777777;">|.&format_price($total_existencias_cost,$decimal).qq|</th>
						</tr>
					</table><br><br>|;
				print $str_out;
		}
	}

	# print "<center><br><FONT face=verdana size=2 color=#666666>MÉTODO DE VALUACIÓN DE INVENTARIO: $cfg{'acc_inventoryout_method'}</font></center>";
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