#!/usr/bin/perl



#############################################################################
#############################################################################
#   Function: cod_tovirtual
#
#       Es: Traspasa inventario de un WH fisico a un WH virtual para asignar productos a choferes para ordenes COD
#       En: 
#
#
#    Created on: 02/10/09
#
#    Author: _Roberto Barcenas_
#
#    Modifications:
#
#        - Modified on *06/14/2010* by _Roberto Barcenas_ : Se modifica por completo la funcion. Los productos son procesados por la funcion transfer_warehouses, al igual que lo hace el cod_receipt. La Funcion transfer_warehouses se transformo por completo el mismo dia
#        - Modified on *11/12/2012* by _Roberto Barcenas_ : Se agrega llamada a funcion de movimientos de inventario, los movimientos dependerar de si existe una funcion a correr declarada en la tabla sl_keypoints_functions para este tipo de orden
#        - Modified on 17/12/2015 by Fabian Cañaveral : Se modifica la forma de procesar las lineas de productos de traking, se hace proceso por producto.
#
#   Parameters:
#
#      - x  
#      - y  
#
#  Returns:
#
#      - 
#
#   See Also:
#
#      <entershipment>
#
sub cod_tovirtual {
#############################################################################
#############################################################################
	
	my ($shpdate, $tracking, $trktype, $id_orders, $id_warehouses, $num, $doinventory, $idvirtual, %ids)=@_;
	
	$tracking = ($tracking)? $tracking:'N/A';
	$trktype = ($trktype)? $trktype:'By Parts';

	### Metodo usado para la salida de inventario. FIFO: Primer entradas primeras salidas | LIFO: Ultimas entradas primeras salidas
	my $acc_method = $cfg{'acc_inventoryout_method'} ? $cfg{'acc_inventoryout_method'} : 'fifo';
	my $invout_order = $acc_method eq 'fifo' ? '' : 'DESC';

	### Escanear orden del location Pack?
	my $mod_pack = $in{'scan_from_pack'} ? " AND UPPER(Location) = 'PACK' " : '';

	if($doinventory){
		

		######################################
		######################################
		###############
		############### 1) Revision de Inventario
		###############
		######################################
		######################################

		my ($valid, $vmsg);

		$sql = "SELECT 400000000 + ID_parts, SUM(sl_orders_products.Quantity * Qty)
		FROM sl_orders_products INNER JOIN sl_skus ON ID_sku_products = sl_orders_products.ID_products
		INNER JOIN sl_skus_parts USING(ID_sku_products) 
		WHERE ID_orders = '$id_orders' 
		AND sl_orders_products.Status = 'Active'
		AND (sl_orders_products.Cost IS NULL OR sl_orders_products.Cost = '' OR sl_orders_products.Cost = 0)
		AND 1 > (SELECT COUNT(*) FROM sl_orders_parts WHERE ID_orders_products = sl_orders_products.ID_orders_products)
		GROUP BY ID_parts
		ORDER BY ID_parts;";
		$log .= $sql."<br>";
		my ($sthv) = &Do_SQL($sql);

		while(my ($id, $qty) = $sthv->fetchrow()){

			$sql = "SELECT IF(SUM(Quantity)>0,SUM(Quantity),0)AS Stock, IF(SUM(Quantity) < $qty,0,1)AS ToSend FROM sl_warehouses_location WHERE ID_products = '$id' AND ID_warehouses = '".$id_warehouses."' $mod_pack;";
			$log .= $sql."<br>";
			$sthinv = &Do_SQL($sql);
			my ($stock, $recinv) = $sthinv->fetchrow();

			if($stock == 0 or !$recinv){
				my $upc = &load_name('sl_skus', 'ID_sku_products', $id, 'UPC');
				$vmsg .= "<li>".trans_txt('scan_no_stock')."$upc ($id) ($stock < $qty) ".trans_txt('warehouse')." $in{'id_warehouses'}</li>";
				&auth_logging('cod_order_no_stock',$id_orders);
			}

		}
		
		if (length($vmsg) > 0){
			return ('error', $vmsg) 
		}

		######################################
		######################################
		###############
		############### 2) Movimientos de almacen
		###############
		######################################
		######################################
		my ($query);
		%skus_products = fix_hash_for_entershipment(\%ids);
		while( my($sku, $value) = each %skus_products ){
			my $id_orders_products = $value->{'id_orders_products'};
			my ($status_transfer, $message) = &warehouse_transfers(
				$id_warehouses,
				0,
				$idvirtual,
				0,
				$sku,
				$value->{'qty'},
				$id_orders,
				'sl_orders',
				$tracking,
				$shpdate,
				$trktype,
				$id_orders_products
			);
			$log .= "status_transfer=".$status_transfer."<br>\n\n";
			$log .= "message=".$message."<br>\n\n";
			if ($status_transfer =~ /ok/i){
				$sql = "SELECT sl_orders_products.ID_orders_products
				FROM sl_orders_products 
				INNER JOIN sl_orders_parts ON sl_orders_products.ID_orders_products=sl_orders_parts.ID_orders_products
				WHERE sl_orders_products.ID_orders='$id_orders'
				GROUP BY sl_orders_products.ID_orders_products;";
				my $sth_orders_products = &Do_SQL($sql);
				while (my $rec_orders_products = $sth_orders_products->fetchrow_hashref()){
					$sql = "UPDATE sl_orders_products
					INNER JOIN 
					(
					 	SELECT 
							ID_orders_products
							, SUM(sl_orders_parts.Cost * sl_orders_parts.Quantity) As ct
							, sl_orders_parts.Date AS sd
							, sl_orders_parts.Tracking tr
							, sl_orders_parts.ShpProvider pr
					 FROM sl_orders_parts INNER JOIN sl_orders_products
					 USING(ID_orders_products)
					 WHERE ID_orders_products = $rec_orders_products->{'ID_orders_products'}
					 GROUP BY ID_orders_products
					)tmp
					USING(ID_orders_products)
					SET Cost = ct, ShpDate = sd, Tracking = tr, ShpProvider = pr, PostedDate = sd
					WHERE ID_orders_products = $rec_orders_products->{'ID_orders_products'};";
					$log .= $sql."<br>\n\n";
					&Do_SQL($sql);
				}

				####### Movimientos de contabilidad
				#######
				my ($order_type, $ctype, $ptype,@params);
				$sql = "SELECT Ptype, Type FROM sl_orders INNER JOIN sl_customers USING(ID_customers) WHERE ID_orders = '$id_orders';";
				$log .= $sql."<br>";
				my ($sth) = &Do_SQL($sql);
				($order_type, $ctype) = $sth->fetchrow();
				my @params = ($id_orders);
				&accounting_keypoints('order_products_inventoryout_'. $ctype .'_'. $order_type, \@params );	
				$log .= qq|accounting_keypoints('order_products_inventoryout_'. $ctype .'_'. $order_type, [$id_orders] )|."<br>";
			
			}else{

				$log .= "ERROR DETECTADO"."<br>";
				&send_text_mail($cfg{'to_email_debug'},$cfg{'to_email_debug'},'DEBUG cod_tovirtual',"$log") if ($cfg{'sales_debug'} and $cfg{'sales_debug'}==1);
				
				return ($status_transfer, $message);
			}
		}
		
		## Update Order Status & Add Note
		my ($shp_place) = &load_name('sl_orders','ID_orders',$id_orders,"CONCAT(shp_City,' , ',shp_State)");
		my $cod_driver  = &load_name('sl_warehouses','ID_warehouses',$idvirtual,'Name');
		$sql = "UPDATE sl_orders SET Status='Processed',StatusPrd='None' WHERE ID_orders='$id_orders';";
		$log .= $sql."<br>";
		my ($sth) = &Do_SQL($sql);

		$sql = "SELECT ID_warehouses FROM sl_orders WHERE ID_orders='$id_orders' ;";
		$log .= $sql."<br>";
		my ($tmp_sthv) = &Do_SQL($sql);
		my ( $tmp_id_warehouses ) = $tmp_sthv->fetchrow_array();

		$sql = "INSERT INTO sl_orders_datecod VALUES(0, '$id_orders', '$tmp_id_warehouses','$shpdate','0000-00-00','Active',CURTIME(),$usr{'id_admin_users'} );";
		$log .= $sql."<br>";
		my ($sthv) = &Do_SQL($sql);
		&auth_logging('opr_orders_stProcessed',$id_orders);
		&status_logging($id_orders,'Processed');

		$datetoapply="'$in{'datetoapplygv'}'" if($in{'datetoapplygv'}=~/(\d{4})[-|\/](\d{1,2})[-|\/](\d{1,2})$/);
		$sql = "INSERT INTO sl_orders_notes SET Notes='COD ".&trans_txt('order_shipped')." to:$shp_place\nAssigned to: $cod_driver',Type='Low',ID_orders_notes_types='1',Date=CURDATE(),Time=NOW(),ID_admin_users='$usr{'id_admin_users'}', ID_orders='$id_orders';";
		$log .= $sql."<br>";
		my ($sth) = &Do_SQL($sql);
		$in{'db'} = "sl_orders";
		&auth_logging('cod_order_shipped',$id_orders);
		
		&send_text_mail($cfg{'to_email_debug'},$cfg{'to_email_debug'},'DEBUG cod_tovirtual',"$log") if ($cfg{'sales_debug'} and $cfg{'sales_debug'}==1);

		##########################
		##########################
		# Si se utilizo authcode, desocupamos el valor en DB
		##########################
		##########################
		if($in{'auth_finance'} or $in{'auth_admin'}){
			my ($sth) = &Do_SQL("INSERT INTO cleanup_temp SET ID_orders='$id_orders',Message='Order Shipped W/Authorization Code'");
			## Reinitialize the Value
			my ($sth) = &Do_SQL("UPDATE sl_vars SET VValue = '' WHERE VName = 'Authorization Code'");
			my ($sth) = &Do_SQL("UPDATE sl_vars SET VValue = '' WHERE VName = 'Auth Order' AND RIGHT(VValue,4)='$in{'authcode'}';");
			delete($in{'auth_finance'})		if	$in{'auth_finance'};
			delete($in{'authcode_admin'})	if	$in{'authcode_admin'};
		}

		## Clean Tracking Info
		$in{'tracking'} = '';

	}

	return ("ok","ok");
}


sub assigntovirtual{
#-----------------------------------------
# Created on: 02/10/09  16:20:07 By  Roberto Barcenas
# Forms Involved:  cod_tovirtual
# Description : Assign a product to a virtual warehouse
# Parameters : $id_orders,$id_products,$id_warehouses, $cost

	my ($id_orders,$id_products,$id_warehouses,$cost)	=	@_;
	my $str = '';
	my ($sth) = &Do_SQL("DELETE FROM sl_warehouses_location WHERE ID_warehouses = $id_warehouses AND ID_products = '$id_products' AND Quantity <= 0");
	my ($sth) = &Do_SQL("DELETE FROM sl_skus_cost WHERE ID_warehouses = $id_warehouses AND ID_products = '$id_products'  AND Quantity <= 0");
	
	###### sl_warehouses_location
	my ($sth) = &Do_SQL("SELECT COUNT(*) FROM sl_warehouses_location WHERE ID_warehouses = $id_warehouses AND ID_products = '$id_products'");
	if($sth->fetchrow > 0){
		$str .="UPDATE sl_warehouses_location SET Quantity = Quantity+1,Date=CURDATE(),Time=CURTIME(),ID_admin_users='$usr{'id_admin_users'}' WHERE ID_warehouses = $id_warehouses AND ID_products = '$id_products' ORDER BY Date LIMIT 1;";
	}else{
		$str .="INSERT INTO sl_warehouses_location SET ID_products='$id_products',ID_warehouses=$id_warehouses,Location='a999a',Quantity=1,Date=CURDATE(),Time=CURTIME(),ID_admin_users='$usr{'id_admin_users'}';";
	}
	
	
	###### sl_skus_cost
	my ($sth) = &Do_SQL("SELECT COUNT(*) FROM sl_skus_cost WHERE ID_warehouses = $id_warehouses AND ID_products = '$id_products' AND Cost='$cost'");
	if($sth->fetchrow > 0){
		$str .="UPDATE sl_skus_cost SET Quantity = Quantity+1 WHERE ID_warehouses = $id_warehouses AND ID_products = '$id_products' AND Cost='$cost' ORDER BY Date LIMIT 1;";
	}else{
		$str .="INSERT INTO sl_skus_cost SET ID_products='$id_products',ID_purchaseorders='$id_orders',ID_warehouses=$id_warehouses,Tblname='sl_adjustments',Quantity=1,Cost='$cost',Date=CURDATE(),Time=NOW(),ID_admin_users='$usr{'id_admin_users'}';";
	}
	return $str;
}


sub manifest_cod{
#-----------------------------------------
# Created on: 02/11/09  15:53:12 By  Roberto Barcenas
# Forms Involved: 
# Description :
# Parameters : 	
# Last Modified on: 07/17/09 13:45:09
# Last Modified by: MCC C. Gabriel Varela S: Se modifica para mostrar por Status en History.
# Last Modified RB: 08/04/09  12:14:22 -- Se habilita busqueda por Preorden y busqueda de Status='Cancelled'
# Last Modified RB: 09/15/09  13:41:34 -- Se habilita busqueda por cualquier Status de la preorden

	
	my $query = '';
	my $mod1='';
	my $mod2='';
	my $extcond .=" Status = 'Active' ";

	my $datecod = 'DateCOD';
	$in{'basedate'} = "In Transit Date"	if (!$in{'basedate'} or $in{'basedate'} eq '');
	
	if($in{'history'}){
		$va{'history'}="History";
	}elsif($in{'basedate'}	eq 'Any Time'){
		$va{'history'}="";
		$extcond ="1";
	}elsif($in{'basedate'}	eq 'Cancell Date'){
		$va{'history'}="";
		$mod1 = " AND Status='Cancelled' ";
		$mod2 = " AND Status='Cancelled' ";
		$extcond ="  Status = 'Inactive' ";
		$datecod = 'DateCancelled';
	}elsif($in{'id_preorders'}){
	  ($in{'id_preorders'} > 500000000) and ($mod1 .=" AND ID_preorders = ".int($in{'id_preorders'})." ");
	  ($in{'id_preorders'} < 500000000) and ($mod2 .=" AND ID_orders = ".int($in{'id_preorders'})." ");
	}else{
		$va{'history'}="";
		$mod1 = " AND Status='In Process' ";
		$mod2 = " AND Status='Processed'";
	}
	
	if($in{'search'}eq'form'){
		&manifests_cod_search;
		return;
	}
	
	if($in{'date'} and $in{'idwh'}){
		$in{'date'} = &filter_values($in{'date'});
		$in{'idwh'}	=	int($in{'idwh'});
		&manifest_cod_date;
		return;
	}
	
	if($in{'id_warehouses'}){
		$query .= " AND sl_orders_datecod.ID_warehouses = '$in{'id_warehouses'}' ";
	}
	
	if($in{'from_date'} and $in{'to_date'}){
		$query .= " AND sl_orders_datecod.".$datecod." BETWEEN '$in{'from_date'}' AND '$in{'to_date'}' ";
	}elsif($in{'from_date'}){
		$query .= " AND sl_orders_datecod.".$datecod." >= '$in{'from_date'}' ";
	}elsif($in{'to_date'}){
		$query .= " AND sl_orders_datecod.".$datecod." <= '$in{'to_date'}' ";
	}
	
	
	my $cadinn = " INNER JOIN 
			(
			SELECT ID_orders
			FROM sl_orders 
			WHERE Ptype='COD'
			AND ID_warehouses > 0
			$mod2)as tmp
			ON tmp.ID_orders = sl_orders_datecod.ID_orders ";
	
	my ($sth) = &Do_SQL("SELECT sl_orders_datecod.".$datecod." FROM sl_orders_datecod $cadinn  WHERE $extcond $query  GROUP BY DateCOD,ID_warehouses");
	$va{'matches'} = $sth->rows;
	if($va{'matches'} > 0){
		my (@c) = split(/,/,$cfg{'srcolors'});
		
		if(!$in{'print'}){
			(!$in{'nh'}) and ($in{'nh'}=1);
			$first = ($in{'nh'} - 1) * $usr{'pref_maxh'};			
			($va{'pageslist'},$qs) = &pages_list($in{'nh'},"/cgi-bin/mod/$usr{'application'}/admin",$va{'matches'},$usr{'pref_maxh'});
			$limit = " LIMIT $first,$usr{'pref_maxh'}";
		}else{

			$limit = "";
			$va{'pageslist'}=1	
		}
		
		if($in{'print'} ne '2'){
			
			$va{'header'} = qq|<td class="menu_bar_title">Date</td>
									   <td class="menu_bar_title">Orders</td>
									   <td class="menu_bar_title">Coverage</td>|;
			
			my ($sth) = &Do_SQL("SELECT sl_orders_datecod.".$datecod." AS DateCOD,DATE_FORMAT(sl_orders_datecod.".$datecod.",'%W, %M %d %Y')AS Date,COUNT(DISTINCT tmp.ID_orders)AS Orders,sl_orders_datecod.ID_warehouses FROM sl_orders_datecod $cadinn WHERE  $extcond $query  GROUP BY $datecod,ID_warehouses ORDER BY $datecod DESC $limit ;");
			while($rec = $sth->fetchrow_hashref()){
				$d = 1 - $d;
				my $coverage = load_name('sl_warehouses','ID_warehouses',$rec->{'ID_warehouses'},'Name') ; 
				$va{'searchresults'} .= "<tr bgcolor='$c[$d]' onmouseover='m_over(this)' onmouseout='m_out(this)' onClick='trjump(\"/cgi-bin/mod/wms/admin?cmd=manifest_cod&date=$rec->{'DateCOD'}&idwh=$rec->{'ID_warehouses'}&basedate=$in{'basedate'}&id_preorders=$in{'id_preorders'}&history=$in{'history'}\")'>
																			<td class='smalltext' valign='top'>$rec->{'Date'}</td>
																			<td class='smalltext' valign='top' align='center'>$rec->{'Orders'}</td>
																			<td class='smalltext' valign='top' align='left'>$coverage</td>
																		</tr>";
			}
		### Impresion detallada de ordenes(no manifiesto)	
		}else{
			###
			$va{'header'} = qq|<td class="menu_bar_title">ID Order</td>
									   			<td class="menu_bar_title">Date</td>
									   			<td class="menu_bar_title">Status</td>
									   			<td class="menu_bar_title">State</td>
									   			<td class="menu_bar_title">Order Net</td>
									   			<td class="menu_bar_title">Shipping</td>
									   			<td class="menu_bar_title">Tax</td>
									   			<td class="menu_bar_title">In Transit</td>
									   			<td class="menu_bar_title">Ship Via</td>|;
			
			my $cadwhinn = " INNER JOIN sl_warehouses ON sl_warehouses.ID_warehouses = sl_orders_datecod.ID_warehouses ";
			my ($sth) = &Do_SQL("SELECT DISTINCT sl_orders.ID_orders,sl_orders.Date,sl_orders.Status,SUBSTR(sl_orders.shp_State,4)AS State,OrderNet,OrderShp,ROUND(IF(OrderTax >0,OrderNet*OrderTax,0),2)AS OrderTax,sl_orders_datecod.".$datecod." AS DateCOD,Name AS ShipVia FROM sl_orders_datecod $cadinn AND $extcond INNER JOIN sl_orders ON sl_orders.ID_orders = sl_orders_datecod.ID_orders  $cadwhinn WHERE sl_orders_datecod.ID_warehouses > 0   $query ORDER BY sl_orders_datecod.".$datecod." DESC,Name");
			$va{'matches'} = $sth->rows();
			while(my($id_preorders,$date,$status,$state,$net,$shp,$tax,$datecod,$coverage) = $sth->fetchrow()){
				$d = 1 - $d;
				$va{'searchresults'} .= "<tr bgcolor='$c[$d]' onmouseover='m_over(this)' onmouseout='m_out(this)'>
																		<td class='smalltext' valign='top'>$id_preorders</td>
																		<td class='smalltext' valign='top' align='left'>$date</td>
																		<td class='smalltext' valign='top' align='left'>$status</td>
																		<td class='smalltext' valign='top' align='left'>$state</td>
																		<td class='smalltext' valign='top' align='left'>".&format_price($net)."</td>
																		<td class='smalltext' valign='top' align='left'>".&format_price($shp)."</td>
																		<td class='smalltext' valign='top' align='left'>".&format_price($tax)."</td>
																		<td class='smalltext' valign='top' align='left'>$datecod</td>
																		<td class='smalltext' valign='top' align='left'>$coverage</td>
																	</tr>";
			}
		}
		
#		$va{'cod_print'} = qq|<a href="javascript:prnwin('[va_script_url]?cmd=manifest_cod&from_date=[in_from_date]&to_date=[in_to_date]&basedate=[in_basedate]&id_preorders=[in_id_preorders]&idwh=[in_id_warehouses]&print=1&history=[in_history]');"><img src='[va_imgurl]/[ur_pref_style]/b_print.gif' title='Print' alt='' border='0' width="16" height="16"></a>&nbsp;&nbsp;
#													<a href="javascript:prnwin('[va_script_url]?cmd=manifest_cod&from_date=[in_from_date]&to_date=[in_to_date]&basedate=[in_basedate]&id_preorders=[in_id_preorders]&idwh=[in_id_warehouses]&print=2&history=[in_history]');"><img src='[va_imgurl]/[ur_pref_style]/b_print.png' title='Print Detail' alt='' border='0' width="16" height="16"></a>|;
		
		$va{'cod_print_list'} = qq|
		<a href="javascript:prnwin('[va_script_url]?cmd=manifest_cod&from_date=[in_from_date]&to_date=[in_to_date]&basedate=[in_basedate]&id_preorders=[in_id_preorders]&idwh=[in_id_warehouses]&print=1&history=[in_history]');" class="menu">|.&trans_txt('manifest_print').qq|</a>&nbsp;&nbsp;
		<a href="javascript:prnwin('[va_script_url]?cmd=manifest_cod&from_date=[in_from_date]&to_date=[in_to_date]&basedate=[in_basedate]&id_preorders=[in_id_preorders]&idwh=[in_id_warehouses]&print=2&history=[in_history]');" class="menu">|.&trans_txt('manifest_print_detail').qq|</a>|;
 	
	}else{
		$va{'searchresults'} = &trans_txt('search_nomatches');
	}
	

	if(!$in{'print'}){
		print "Content-type: text/html\n\n";
		print &build_page('manifests_cod_list.html');
	}else{
		print "Content-type: text/html\n\n";
		print &build_page('manifests_cod.html');
	}
}


sub manifest_cod_date{
#-----------------------------------------
# Created on: 02/11/09  16:52:45 By  Roberto Barcenas
# Forms Involved: manifest_cod_list
# Description : Build  manifests for coverage and date
# Parameters : 	$in{'date'}, $in{idwh'}
# Last Modified on: 03/09/09 11:47:05
# Last Modified by: MCC C. Gabriel Varela S: Se hace que la ventana de impresi�n tenga los encabezados de impresi�n.
# Last Modified RB: 06/08/09  12:31:51 -- Se hace que se pueda agregar cada preorden a una lista para su verificaci�n.
# Last Modified on: 07/17/09 14:05:57
# Last Modified by: MCC C. Gabriel Varela S: Se adapta para history
# Last Modified RB: 08/04/09  12:14:22 -- Se habilita busqueda por Preorden y busqueda de Status='Cancelled'



	my (%tmpord);
	my $maxres 			= 5;
	$maxres 			= 20 if($in{'history'});
	my $linesxpage 	= 80; #Quantity of lines per page 
	my $baselines 	=	9; #Based on an average lines per order
	my $count = 1; #The actual counter of orders printed by page
	my $i=0;
	my $datecod = 'DateCOD';
	
	my $query = '';
	my $mod1='';
	my $mod2='';
	my $extcond .=" Status = 'Active' ";
	
	if($in{'history'}){
		$va{'history'}="History";
	}elsif($in{'basedate'}	eq 'Any Time'){
		$va{'history'}="";
		$extcond .="  ";
	}elsif($in{'basedate'}	eq 'Cancell Date'){
		$va{'history'}="";
		$mod1 = " AND Status='Cancelled' ";
		$mod2 = " AND Status='Cancelled' ";
		$extcond ="  Status = 'Inactive' ";
		$datecod = 'DateCancelled';
	}elsif($in{'id_preorders'}){
	  ($in{'id_preorders'} > 500000000) and ($mod1 .=" AND ID_preorders = ".int($in{'id_preorders'})." ");
		($in{'id_preorders'} < 500000000) and ($mod2 .=" AND ID_orders = ".int($in{'id_preorders'})." ");
	}else{
		$va{'history'}="";
		$mod1 = " AND Status='In Process' ";
		$mod2 = " AND Status='Processed'";
	}
	
	$va{'info'} = "<br>".&load_name('sl_warehouses','ID_warehouses',$in{'idwh'},"Name")."<br>($in{'date'})";
	$va{'cod_driver'} = &load_name('sl_warehouses','ID_warehouses',$in{'idwh'},"Name");
	
	
	my $cadinn = " INNER JOIN 
			(
			SELECT ID_orders
			from   sl_orders 
			where 
			Ptype='COD'
			AND ID_warehouses > 0
			$mod2)as sl_orders ON   sl_orders.ID_orders = sl_orders_datecod.ID_orders ";
	
	
	my ($sth) = &Do_SQL("SELECT COUNT(DISTINCT sl_orders.ID_orders) FROM sl_orders_datecod $cadinn WHERE $extcond AND ID_warehouses = $in{'idwh'} AND $datecod = '$in{'date'}';");
	$va{'matches'} = $sth->fetchrow;
	if($va{'matches'} > 0){
		###### Print
		if($in{'print'}){
			$sth = &Do_SQL("SELECT * FROM sl_orders_datecod $cadinn  WHERE $extcond AND ID_warehouses = $in{'idwh'} AND $datecod = '$in{'date'}' ORDER BY sl_orders.ID_orders");
		###### Print Screen
		}else{
			$va{'cod_print_list'} = qq|
		<a href="javascript:prnwin(\'$va{'script_url'}?cmd=manifest_cod&date=$in{'date'}&basedate=$in{'basedate'}&id_preorders=$in{'id_preorders'}&idwh=$in{'idwh'}&print=1&history=$in{'history'}\');" class="menu">|.&trans_txt('manifest_print').qq|</a>|;
			$va{'cod_print_list'} .= qq|<a href="javascript:prnwin(\'$va{'script_url'}?cmd=manifest_cod&date=$in{'date'}&basedate=$in{'basedate'}&id_preorders=$in{'id_preorders'}&idwh=$in{'idwh'}&print=2&history=$in{'history'}\');" class="menu">|.&trans_txt('manifest_print_detail').qq|</a> |	if $in{'history'};
			
			#$va{'cod_print'}  = qq|<a href="javascript:prnwin(\'$va{'script_url'}?cmd=manifest_cod&date=$in{'date'}&basedate=$in{'basedate'}&id_preorders=$in{'id_preorders'}&idwh=$in{'idwh'}&print=1&history=$in{'history'}\');"><img src='[va_imgurl]/[ur_pref_style]/b_print.gif' title='Print' alt='' border='0' width="16" height="16"></a> |;
			#$va{'cod_print'} .= qq|<a href="javascript:prnwin(\'$va{'script_url'}?cmd=manifest_cod&date=$in{'date'}&basedate=$in{'basedate'}&id_preorders=$in{'id_preorders'}&idwh=$in{'idwh'}&print=2&history=$in{'history'}\');"><img src='[va_imgurl]/[ur_pref_style]/b_print.png' title='Print Detail' alt='' border='0' width="16" height="16"></a> |	if $in{'history'};
			(!$in{'nh'}) and ($in{'nh'}=1);
			$first = ($in{'nh'} - 1) * $maxres;			
			($va{'pageslist'},$qs) = &pages_list($in{'nh'},"/cgi-bin/mod/$usr{'application'}/admin",$va{'matches'},$maxres);
			$sth = &Do_SQL("SELECT *  FROM sl_orders_datecod $cadinn WHERE $extcond AND ID_warehouses = $in{'idwh'} AND $datecod = '$in{'date'}' ORDER BY sl_orders.ID_orders LIMIT $first,$maxres;");
		}
		
		while($rec = $sth->fetchrow_hashref){
			$id_preorders=$rec->{'ID_orders'};
			#$j=0;
			$str_prod = '';
			my $sumprod=0;$sumser=0;$sumtax=0;$sumdisc=0;$sumshipp=0;$sumorder=0;$item=0;$subtotal=0;
			$d = 1 - $d;
			
			$prefix ='';
			$prefix = 'pre'  if $id_preorders > 500000;
			
			######## Lists
			if (!$in{'print'}){
				$va{'cod_to_list'} = qq|<a href="#top_$id_preorders" id="ajax_btn" onclick="popup_show('lists_windows_$id_preorders', 'lists_drag_$id_preorders', 'lists_exit_$id_preorders', 'element-right', -1, -1,'top_$id_preorders');"><img src="/sitimages//default/reminders.png" title=" Manage lists. " alt=" Manage lists. " width="24" border="0" height="24"></a>&nbsp;<a name="top_$id_preorders" id="top_$id_preorders">|;
				$va{'lists_iframes'} .= qq|<div id="lists_windows_$id_preorders" style="visibility: hidden; display: none; background-color: #ffffff;">\r\n
																	<div class="menu_bar_title" id="lists_drag_$id_preorders">\r\n
																		<img id="lists_exit_$id_preorders" src="/sitimages/default/popupclose.gif">\r\n
																		&nbsp;&nbsp;&nbsp;List Manager\r\n
																	</div>\r\n
																	<div class="formtable">\r\n
																		<IFRAME SRC="/cgi-bin/common/apps/ajaxbuild?ajaxbuild=manage_lists&id=$id_preorders&db=sl_|.$prefix.qq|orders&table=sl_|.$prefix.qq|orders&path=$script_url&cmdo=|.$prefix.qq|orders&id_admin_users=$usr{'id_admin_users'}" name="rcmd" TITLE="Recieve Commands" width="446" height="320" FRAMEBORDER="0" MARGINWIDTH="0" MARGINHEIGHT="0" SCROLLING="auto">\r\n
																			<H2>Unable to do the script</H2>\r\n
																			<H3>Please update your Browser</H3>\r\n
																		</IFRAME>\r\n
																	</div>\r\n
																</div>\r\n|;
			}
			
			
			my ($sth2) = &Do_SQL("SELECT IsSet,sl_".$prefix."orders_products.* FROM sl_".$prefix."orders_products LEFT JOIN sl_skus 
														ON sl_".$prefix."orders_products.ID_products = sl_skus.ID_sku_products
														WHERE ID_".$prefix."orders = $id_preorders AND sl_".$prefix."orders_products.Status='Active';");
				
			&load_cfg('sl_orders');											
			while($rprod = $sth2->fetchrow_hashref()){
				
				%tmpord = &get_record('ID_orders',$id_preorders,'sl_orders');
				$add = 
				$customer = &load_db_names('sl_customers','ID_customers',$tmpord{'id_customers'},"[Lastname1] [FirstName]");
				#$cphone = &load_db_names('sl_customers','ID_customers',$tmpord{'id_customers'},"[Phone1] / [Cellphone]");
				$cphone='';
			
				$sumprod+=$rprod->{'SalePrice'} if substr($rprod->{'ID_products'},0,1)!= 6;
				$sumser+=$rprod->{'SalePrice'} if substr($rprod->{'ID_products'},0,1)== 6;
				$sumtax+=$rprod->{'Tax'};
				$sumdisc+= $rprod->{'Discount'}*-1;
				$sumshipp+= $rprod->{'Shipping'};
			
				$items++ if (substr($rprod->{'ID_products'},0,1) != 6 and $rprod->{'IsSet'}ne'Y');
				$item = load_name('sl_products','ID_products',substr($rprod->{'ID_products'},3),"Name") if substr($rprod->{'ID_products'},0,1)!= 6;
				$str_prod .= "<tr>
												<td class='smalltext' valign='top' align='left' colspan='3' style='font-size:10px;font-weight:bold;'>$item</td>
												<td class='smalltext' valign='top' align='right' colspan='3' style='font-size:10px;font-weight:bold;'>".&format_price($rprod->{'SalePrice'})."</td>
											</tr>" if substr($rprod->{'ID_products'},0,1) != 6;
			
				if($rprod->{'IsSet'}eq'Y'){
					my ($sth3) = &Do_SQL("SELECT * FROM sl_".$prefix."orders_parts WHERE ID_".$prefix."orders_products = '$rprod->{'ID_orders_products'}' ");
					while($rpart = $sth3->fetchrow_hashref()){
						$items++;
						$item = load_db_names('sl_parts','ID_parts',$rpart->{'ID_parts'},"[Model]/[Name]");
						
						$str_prod .= "<tr>
														<td class='smalltext' valign='top' align='left' colspan='3' style='font-size:9px;'>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;$item</td>
													</tr>"; 
						$i++;
					}
				}
				$i++;
			}
			$total+=$sumprod+$sumser+$sumtax+$sumshipp+$sumdisc;
			
			if(($count*$baselines+$i > $linesxpage or !$flag) and $in{'print'}){
				$va{'searchresults'} .= "</td></tr></table><div style='page-break-before:always'></div>" if $flag==1 and !$in{'history'};
				$va{'searchresults'} .= "<table align='center' style='background:#fff;' width='100%'><tr><td>"if(!$in{'history'}or !$flag);
				$va{'searchresults'} .= "</td></tr>"if($in{'history'}and $flag);
				$va{'searchresults'} .= "<tr class='menu_bar_title'>
		   <td>Order ID</td>
		   <td>Total</td>
		   <td>Status</td>
		</tr>"if($in{'history'} and !$flag);
				
				($flag) and ($i=int($i/$count+1)) and ($count=1) ;
				$flag=1;
			}
			
			if($in{'history'} and (!$in{'print'} or $in{'print'} ==1))
			{
				$va{'searchresults'} .= "<tr>
																   <td>$id_preorders</td>
																   <td>".&format_price($sumprod+$sumtax+$sumser+$sumshipp+$sumdisc)."</td>
																   <td>$rec->{'Status'}</td>
																</tr>";
			}
			else
			{
				$va{'searchresults'} .= "<table width='100%' algin='center' style='border:1px solid;font-size:9px;'>
																	<tr>
																		<td align='left' style='font-size:10px;'><strong>Order</strong></td><td style='font-size:10px;'>$id_preorders</td>
																			<td align='right' colspan='4'>$va{'cod_to_list'}</td>
																	</tr>
																	<tr>
																		<td align='left' style='font-size:10px;'><strong>Customer</strong></td>
																		<td style='font-size:10px;'>$customer</td>
																		<td align='center' valign='top' style='font-size:10px;'><strong> &nbsp; </strong> $cphone</td>
																		<td align='left' valign='top' style='font-size:10px;'><strong>Address</strong></td>
																		<td style='font-size:10px;' width='30%'>$tmpord{'address1'}<br>$tmpord{'address2'}</td>
																		<td align='right' valign='top' style='font-size:10px;'><strong>City</strong> $tmpord{'shp_city'}, $tmpord{'shp_zip'}</td>
																	</tr>
																	<tr class='menu_bar_title'>
																		<td align='center' colspan='3'>Item</td><td align='center' colspan='3'>Sale Price</td>
																	</tr>
																	$str_prod
																	<tr>
																		<td align='right' colspan='2'>&nbsp;</td>
																		<td align='right' colspan='4'>
																			<table width=100% align='right' border='0'>
																				<tr>
																					<td align='right' style='font-size:10px;font-weight:bold;'>Subtotal: </td>
																					<td align='left' style='font-size:10px;'>".&format_price($sumprod)."</td>
																					<td align='right' style='font-size:10px;font-weight:bold;'>Discounts: </td>
																					<td align='left' style='font-size:10px;'>".&format_price($sumdisc)."</td>
																					<td align='right' style='font-size:10px;font-weight:bold;'>Tax: </td>
																					<td align='left' style='font-size:10px;'>".&format_price($sumtax)."</td>
																					<td align='right' style='font-size:10px;font-weight:bold;'>Services: </td>
																					<td align='left' style='font-size:10px;'>".&format_price($sumser)."</td>
																					<td align='right' style='font-size:10px;font-weight:bold;'>S&H: </td>
																					<td align='left' style='font-size:10px;'>".&format_price($sumshipp)."</td>
																					<td align='right' style='font-size:12px;font-weight:bold;color:red'>Total: </td>
																					<td align='right' style='font-size:12px;font-weight:bold;'>".&format_price($sumprod+$sumtax+$sumser+$sumshipp+$sumdisc)."</td>
																				</tr>
																			</table>
																		</td>
																	</tr>
																</table>
																&nbsp;";
			}
			$count++;																									 
		}
		$count-- if $count>1;
#		if($count*$baselines+$i+4 > $linesxpage and $in{'print'}){
#				$va{'searchresults'} .= "</td></tr></table><div style='page-break-before:always'></div>
#																	<table align='center' style='background:#fff;' width='100%'><tr><td>
#																	[ip_forms:sltv_header]<br>"if(!$in{'history'});
#		}
		
		$va{'searchresults'} .= "<table align='center' class='formtable' style='background:#fff;' width='50%'>
																<tr class='menu_bar_title'><td align='center' colspan='2' style='border-bottom:1px solid;'>Resume</td</tr>
																<tr>
																	<td align='right'><strong>Total Items</strong></td><td>$items</td>
																</tr>
																<tr>
																	<td align='right'><strong>Total Money</strong></td><td>".format_price($total)."</td>
																</tr>
															</table>"if(!$in{'history'});
	
		
	}else{
		$va{'searchresults'} = &trans_txt('search_nomatches');
	}
	
	
	if($in{'print'}){
		print "Content-type: text/html\n\n";
		print &build_page('header_print.html');
		print &build_page("manifests_cod$in{'history'}.html");
	}else{
		print "Content-type: text/html\n\n";
		print &build_page("manifests_cod_list$in{'history'}.html");
	}
	
}


sub manifests_cod_search{
#-----------------------------------------
# Created on: 02/12/09  15:40:13 By  Roberto Barcenas
# Forms Involved: manifests_cod_search.html
# Description :
# Parameters : 	

	
	if($in{'action'}){
	 $in{'to_date'} = &get_sql_date()	if 	!$in{'to_date'};
		&manifest_cod;
		return;
	}
	
	print "Content-type: text/html\n\n";
	print &build_page('manifests_cod_search.html');	
}


sub cod_products{
# --------------------------------------------------------

# Author: Jose Ramirez Garcia
# Created on: 
# Last Modified on: 
# Last Modified by: 
# Description : 
# Forms Involved: 
# Parameters : 
	my ($sth) = &Do_SQL("SELECT sl_orders_products.ID_products, COUNT(sl_orders_products.ID_products) AS Qty 
				FROM 	sl_orders, sl_orders_products, sl_orders_payments 
				WHERE 	sl_orders.ID_orders=sl_orders_payments.ID_orders 
				AND 	sl_orders.ID_orders=sl_orders_products.ID_orders 
				AND 	sl_orders_payments.Type='COD' 
				AND sl_orders.Status='Processed' 
				AND sl_orders.StatusPrd<>'In Fulfillment' 
				AND LEFT(sl_orders_products.ID_products,1) <> '6' 
				GROUP BY sl_orders_products.ID_products");
	$va{'matches'} = $sth->rows;
	if ($va{'matches'}>0){
		(!$in{'nh'}) and ($in{'nh'}=1);
		$first = ($in{'nh'} - 1) * $usr{'pref_maxh'};			
		($va{'pageslist'},$qs) = &pages_list($in{'nh'},"/cgi-bin/mod/$usr{'application'}/admin",$va{'matches'},$usr{'pref_maxh'});
		my ($sth) = &Do_SQL("SELECT sl_orders_products.ID_products, COUNT(sl_orders_products.ID_products) AS Qty FROM sl_orders, sl_orders_products, sl_orders_payments WHERE sl_orders.ID_orders=sl_orders_payments.ID_orders AND sl_orders.ID_orders=sl_orders_products.ID_orders AND sl_orders_payments.Type='COD' AND sl_orders.Status='Processed' AND sl_orders.StatusPrd<>'In Fulfillment' AND LEFT(sl_orders_products.ID_products,1) <> '6' GROUP BY sl_orders_products.ID_products LIMIT $first,$usr{'pref_maxh'}");
		my (@c) = split(/,/,$cfg{'srcolors'});
		while ($rec = $sth->fetchrow_hashref){
			$d = 1 - $d;
			$va{'searchresults'} .= "<tr bgcolor='$c[$d]' onmouseover='m_over(this)' onmouseout='m_out(this)' onClick=\"trjump('/cgi-bin/mod/wms/admin?cmd=cod_zip&id_products=$rec->{'ID_products'}')\">\n";
			$va{'searchresults'} .= "  <td class='smalltext' valign='top' >".&format_sltvid($rec->{'ID_products'})."</td>";
			my ($choices) = "";
			for my $i(1..4){
				$choices .= &load_name('sl_skus','ID_sku_products',$rec->{'ID_products'},'choice'.$i)." ";
			}
			$va{'searchresults'} .= "  <td class='smalltext' valign='top' >".&load_name('sl_products','ID_products',substr($rec->{'ID_products'},3,9),'Name')." ".$choices."</td>";
			$va{'searchresults'} .= "  <td class='smalltext' valign='top' >$rec->{'Qty'}</td>";
			$va{'searchresults'} .= "</tr>\n";
		}
	}else{
		$va{'pageslist'} = 1;
		$va{'searchresults'} = qq|
		<tr>
			<td colspan='3' align="center">|.&trans_txt('search_nomatches').qq|</td>
		</tr>\n|;
	}
	print "Content-type: text/html\n\n";
	print &build_page('cod_products.html');

}



sub cod_zip{
# --------------------------------------------------------

# Author: Jose Ramirez Garcia
# Created on: 
# Last Modified on: 
# Last Modified by: 
# Description : 
# Forms Involved: 
# Parameters : 
#last modified: 02/03/2009 : JRG : se cambia la forma de definir zonas

	if($in{'id_products'}){
		my ($sth) = &Do_SQL("SELECT sl_orders.shp_Zip, sl_orders.shp_City, sl_orders.shp_State, sl_orders.shp_Country, COUNT(sl_orders_products.ID_products) as Qty 
					FROM sl_orders, sl_orders_payments, sl_orders_products 
					WHERE sl_orders.ID_orders=sl_orders_payments.ID_orders 
					AND sl_orders.ID_orders=sl_orders_products.ID_orders 
					AND sl_orders_payments.Type='COD' 
					AND sl_orders.Status='Processed' 
					AND sl_orders.StatusPrd<>'In Fulfillment' 
					AND sl_orders_products.ID_products='".$in{'id_products'}."' 
					GROUP BY sl_orders.shp_Zip ");
		$va{'matches'} = $sth->rows;
		if($va{'matches'} == 1){
			while ($rec = $sth->fetchrow_hashref){
				$in{'zip'} = $rec->{'shp_Zip'};
				$in{'state'} = $rec->{'shp_State'};
				$in{'city'} = $rec->{'shp_City'};
				$in{'country'} = $rec->{'shp_Country'};
			}
			&cod_warehouse;
			exit;
		} elsif ($va{'matches'}>0){
			(!$in{'nh'}) and ($in{'nh'}=1);
			$first = ($in{'nh'} - 1) * $usr{'pref_maxh'};
			($va{'pageslist'},$qs) = &pages_list($in{'nh'},"/cgi-bin/mod/$usr{'application'}/admin",$va{'matches'},$usr{'pref_maxh'});
			my ($sth) = &Do_SQL("SELECT sl_orders.shp_Zip, sl_orders.shp_City, sl_orders.shp_State, sl_orders.shp_Country, COUNT(sl_orders_products.ID_products) as Qty FROM sl_orders, sl_orders_payments, sl_orders_products WHERE sl_orders.ID_orders=sl_orders_payments.ID_orders AND sl_orders.ID_orders=sl_orders_products.ID_orders AND sl_orders_payments.Type='COD' AND sl_orders.Status='Processed' AND sl_orders.StatusPrd<>'In Fulfillment' AND sl_orders_products.ID_products='".$in{'id_products'}."' GROUP BY sl_orders.Zip LIMIT $first,$usr{'pref_maxh'}");
			my (@c) = split(/,/,$cfg{'srcolors'});
			while ($rec = $sth->fetchrow_hashref){
				$d = 1 - $d;
				$va{'searchresults'} .= "<tr bgcolor='$c[$d]' onmouseover='m_over(this)' onmouseout='m_out(this)' onClick=\"trjump('/cgi-bin/mod/wms/admin?cmd=cod_warehouse&zip=$rec->{'shp_Zip'}&state=$rec->{'shp_State'}&city=$rec->{'shp_City'}&country=$rec->{'shp_Country'}&id_products=".$in{'id_products'}."')\">\n";
				$va{'searchresults'} .= "  <td class='smalltext' valign='top' align='center'>$rec->{'Qty'}</td>";
				$va{'searchresults'} .= "  <td class='smalltext' valign='top' >".&format_sltvid($in{'id_products'})."</td>";
				my ($choices) = "";
				for my $i(1..4){
					$choices .= &load_name('sl_skus','ID_sku_products',$in{'id_products'},'choice'.$i)." ";
				}
				$va{'searchresults'} .= "  <td class='smalltext' valign='top' >".&load_name('sl_products','ID_products',substr($in{'id_products'},3,9),'Name')." ".$choices."</td>";
				$va{'searchresults'} .= "  <td class='smalltext' valign='top' >$rec->{'shp_Zip'}</td>";
				$va{'searchresults'} .= "  <td class='smalltext' valign='top' >$rec->{'shp_City'}</td>";
				$va{'searchresults'} .= "  <td class='smalltext' valign='top' >$rec->{'shp_State'}</td>";
				$va{'searchresults'} .= "</tr>\n";
			}
		}else{
			$va{'pageslist'} = 1;
			$va{'searchresults'} = qq|
			<tr>
				<td colspan='4' align="center">|.&trans_txt('search_nomatches').qq|</td>
			</tr>\n|;
		}
	} else {
		$va{'pageslist'} = 1;
		$va{'searchresults'} = qq|
		<tr>
			<td colspan='4' align="center">|.&trans_txt('search_nomatches').qq|</td>
		</tr>\n|;		
	}
	print "Content-type: text/html\n\n";
	print &build_page('cod_zip.html');
}

sub cod_warehouse{
# --------------------------------------------------------

# Author: Jose Ramirez Garcia
# Created on: 
# Last Modified on: 
# Last Modified by: 
# Description : 
# Forms Involved: 
# Parameters : 
# Last Modification: JRG 01/21/2009 : e agrego formato sltv id
	$va{'id_products'} = $in{'id_products'};
	$va{'format_id_products'} = &format_sltvid($in{'id_products'});
	$va{'model'} = &load_name('sl_products','ID_products',substr($in{'id_products'},3,9),'Model');
	$in{'name'} = &load_name('sl_products','ID_products',substr($in{'id_products'},3,9),'Name');
	for my $i(1..4){
		$va{'choices'} .= &load_name('sl_products','ID_products',substr($in{'id_products'},3,9),'ChoiceName'.$i)." ";
	}
	my ($sth) = &Do_SQL("SELECT sl_orders.ID_orders 
				FROM sl_orders, sl_orders_products, sl_orders_payments 
				WHERE sl_orders.ID_orders=sl_orders_payments.ID_orders 
				AND sl_orders.ID_orders=sl_orders_products.ID_orders 
				AND sl_orders_payments.Type='COD' 
				AND sl_orders.Status='Processed' 
				AND sl_orders.StatusPrd<>'In Fulfillment' 
				AND sl_orders_products.ID_products='".$va{'id_products'}."' 
				AND LOWER(sl_orders.shp_City)='".lc($in{'city'})."' 
				AND sl_orders.shp_State='".$in{'state'}."' ");
	$va{'orders'} = $sth->rows;
	print "Content-type: text/html\n\n";
	print &build_page('cod_warehouse.html');
}

sub cod_process{
# --------------------------------------------------------

# Author: Jose Ramirez Garcia
# Created on: 
# Last Modified on: 
# Last Modified by: 
# Description : 
# Forms Involved: 
# Parameters : 
#last modification: JRG : 02/13/2009 se agrega id_warehouses a sl_orders
# Last Modification by JRG : 03/13/2009 : Se agrega log
	if($in{'virtual_warehouse'}){
		my $cadinn = " INNER JOIN sl_orders_datecod ON sl_orders.ID_orders = sl_orders_datecod.ID_orders ";
		my ($sth) = &Do_SQL("SELECT sl_orders.ID_orders FROM sl_orders, sl_orders_products, sl_orders_payments WHERE sl_orders.ID_orders=sl_orders_payments.ID_orders AND sl_orders.ID_orders=sl_orders_products.ID_orders AND sl_orders_payments.Type='COD' AND sl_orders.Status='Processed' AND sl_orders.StatusPrd<>'In Fulfillment' AND sl_orders_products.ID_products='".$in{'id_products'}."' AND LOWER(sl_orders.shp_City)='".$in{'city'}."' AND sl_orders.shp_State='".$in{'state'}."' ORDER BY sl_orders.ID_orders ".$in{'so'}." LIMIT 0,".$in{'orders'}." ");
		while ($row = $sth->fetchrow_hashref){
			my ($sth_uo) = &Do_SQL("UPDATE sl_orders SET StatusPrd='In Fulfillment' WHERE ID_orders='".$row->{'ID_orders'}."'");
			&auth_logging('orders_updated',$row->{'ID_orders'});
			my ($sth_dc) = &Do_SQL("SELECT IF(sl_orders_datecod.DateCOD IS NULL),0,1) FROM sl_orders_datecod WHERE ID_orders='".$row->{'ID_orders'}."' AND DateCOD = CURDATE()");
			$datecod = $sth_dc->fetchrow_array();
			if($datecod == 0){
				my ($tmp_sth_uo) = &Do_SQL("SELECT ID_admin_users FROM sl_orders WHERE ID_orders='".$row->{'ID_orders'}."' ;");
				my ( $tmp_id_admin_users ) = $tmp_sth_uo->fetchrow_array();		
				my ($sth_uo) = &Do_SQL("INSERT INTO sl_orders_datecod VALUES( 0, '$row->{'ID_orders'}','".$in{'virtual_warehouse'}."',CURDATE(),'0000-00-00','Active',CURTIME(),'$tmp_id_admin_users' );");			
			}
			my ($sth_up) = &Do_SQL("UPDATE sl_orders SET ID_warehouses='".$in{'virtual_warehouse'}."' WHERE ID_orders='".$row->{'ID_orders'}."'");
		}
	}
		&cod_products;
}

sub cod_man_wh {
# --------------------------------------------------------

# Author: Jose Ramirez Garcia
# Created on: 
# Last Modified on: 
# Last Modified by: 
# Description : 
# Forms Involved: 
# Parameters :
# last modification: JRG : 02/13/2009 se agrega id_warehouses a sl_orders 
# last modification: JRG : 02/19/2009 se cambia id_warehouses de preorders a orders
# Last Modified by RB on 03/31/2011 05:54:47 PM  : Se agrega validacion para ordenes Allnatpro 
	
	if($in{'p_products'}){
		if($in{'id_warehouses'}){
			$va{'searchresults'} = "";
			$qry = "";
			if($in{'from_date'} =~ /^(\d{4})(\/)(\d{1,2})\2(\d{1,2})$/){
				$qry .= " AND sl_orders.Date >= '".$in{'from_date'}."' ";
			}
			if($in{'to_date'} =~ /^(\d{4})(\/)(\d{1,2})\2(\d{1,2})$/){
				$qry .= " AND sl_orders.Date <= '".$in{'to_date'}."' ";
			}
			if($in{'from_date'} =~ /^(\d{4})(\/)(\d{1,2})\2(\d{1,2})$/ && $in{'to_date'} =~ /^(\d{4})(\/)(\d{1,2})\2(\d{1,2})$/){
				my ($sth) = &Do_SQL("SELECT DATEDIFF('".$in{'to_date'}."','".$in{'from_date'}."')");
				$days = $sth->fetchrow_array();
				if($days > 0 || $in{'from_date'} eq $in{'to_date'}){
					#ok
				} else {
					$qry = "";
				}
			}
			my ($sth) = &Do_SQL("SELECT sl_orders_products.ID_orders, sl_orders_products.ID_products, COUNT(sl_orders_products.ID_products) AS Qty 
						FROM sl_orders, sl_orders_payments, sl_orders_products 
						WHERE sl_orders.ID_orders=sl_orders_payments.ID_orders 
						AND sl_orders.ID_orders=sl_orders_products.ID_orders 
						AND sl_orders_payments.Type='COD' 
						AND LEFT(sl_orders_products.ID_products,1) <> '6' 
						AND sl_orders.ID_warehouses='".$in{'id_warehouses'}."' 
						AND sl_orders.ID_orders='0' $qry 
						GROUP BY sl_orders_products.ID_products");
			$va{'wh_name'} = &load_name("sl_warehouses","ID_warehouses",$in{'id_warehouses'},"Name");
			while ($row = $sth->fetchrow_hashref){
				$not_assigned = 0;
				my ($sth_o) = &Do_SQL("SELECT count(*) FROM sl_orders WHERE ID_orders=".$row->{'ID_orders'}." AND ID_warehouses IS NULL");
				$not_assigned = $sth_o->fetchrow_array();
				if($not_assigned == 0){
					$name = "";
					$choices = "";
					for my $i(1..4){
						$choices .= &load_name('sl_skus','ID_sku_products',$row->{'ID_products'},'choice'.$i)." ";
					}
					$name .= &load_name("sl_products","ID_products",substr($row->{'ID_products'},3,9),"Name")." ".&load_name("sl_products","ID_products",substr($row->{'ID_products'},3,9),"Model")." ".$choices;
					$va{'searchresults'} .= "<tr><td>".&format_sltvid($row->{'ID_products'})."</td><td>$name</td><td>".$row->{'Qty'}."</td></tr>";				
				}
			}
			&html_print_jstop;
			print &build_page('cod_print_man_products.html');
		}else{
			$va{'message'} = &trans_txt('search_nomatches');	
			print "Content-type: text/html\n\n";
			print &build_page('toprint_msg.html');
		}
	}elsif($in{'p_money'}){
		if($in{'id_warehouses'}){		
			$va{'searchresults'} = "";
			$qry = "";
			if($in{'from_date'} =~ /^(\d{4})(\/)(\d{1,2})\2(\d{1,2})$/){
				$qry .= " AND sl_orders.Date >= '".$in{'from_date'}."' ";
			}
			if($in{'to_date'} =~ /^(\d{4})(\/)(\d{1,2})\2(\d{1,2})$/){
				$qry .= " AND sl_orders.Date <= '".$in{'to_date'}."' ";
			}
			if($in{'from_date'} =~ /^(\d{4})(\/)(\d{1,2})\2(\d{1,2})$/ && $in{'to_date'} =~ /^(\d{4})(\/)(\d{1,2})\2(\d{1,2})$/){
				my ($sth) = &Do_SQL("SELECT DATEDIFF('".$in{'to_date'}."','".$in{'from_date'}."')");
				$days = $sth->fetchrow_array();
				if($days > 0 || $in{'from_date'} eq $in{'to_date'}){
					#ok
				} else {
					$qry = "";
				}
			}
			my ($sth) = &Do_SQL("SELECT sl_orders_products.ID_orders, sl_orders_products.SalePrice, sl_orders_products.ID_products, COUNT(sl_orders_products.ID_products) AS Qty FROM sl_orders, sl_orders_payments, sl_orders_products WHERE sl_orders.ID_orders=sl_orders_payments.ID_orders AND sl_orders.ID_orders=sl_orders_products.ID_orders AND sl_orders_payments.Type='COD' AND LEFT(sl_orders_products.ID_products,1) <> '6' AND sl_orders.ID_warehouses='".$in{'id_warehouses'}."' AND sl_orders.ID_orders='0' $qry GROUP BY sl_orders_products.ID_products");
			$va{'wh_name'} = &load_name("sl_warehouses","ID_warehouses",$in{'id_warehouses'},"Name");
			while ($row = $sth->fetchrow_hashref){
				$not_assigned = 0;
				my ($sth_o) = &Do_SQL("SELECT count(*) FROM sl_orders WHERE ID_orders=".$row->{'ID_orders'}." AND ID_warehouses IS NULL");
				$not_assigned = $sth_o->fetchrow_array();
				if($not_assigned == 0){
					$name = "";
					$choices = "";
					for my $i(1..4){
						$choices .= &load_name('sl_skus','ID_sku_products',$row->{'ID_products'},'choice'.$i)." ";
					}
					$name .= &load_name("sl_products","ID_products",substr($row->{'ID_products'},3,9),"Name")." ".&load_name("sl_products","ID_products",substr($row->{'ID_products'},3,9),"Model")." ".$choices;
					$product_total = $row->{'SalePrice'}*$row->{'Qty'};
					$va{'searchresults'} .= "<tr><td>".&format_sltvid($row->{'ID_products'})."</td><td>".$name."</td><td align='right'>".&format_price($row->{'SalePrice'})."</td><td align='right'>".$row->{'Qty'}."</td><td align='right'>".&format_price($product_total)."</td></tr>";				
					$total += $product_total;
				}
			}
			if($total){
				$va{'searchresults'} .= "<tr><td colspan='4' align='center'>TOTAL </td><td align ='right'>".&format_price($total)."</td></tr>";
			}
			&html_print_jstop;
			print &build_page('cod_print_man_money.html');
		}else{
			$va{'message'} = &trans_txt('search_nomatches');	
			print "Content-type: text/html\n\n";
			print &build_page('toprint_msg.html');
		}
	} elsif($in{'p_invoices'}){
		
		if($in{'id_warehouses'}){
			$va{'searchresults'} = "";
			$qry = "";
			if($in{'from_date'} =~ /^(\d{4})(\/)(\d{1,2})\2(\d{1,2})$/){
				$qry .= " AND sl_orders.Date >= '".$in{'from_date'}."' ";
			}
			if($in{'to_date'} =~ /^(\d{4})(\/)(\d{1,2})\2(\d{1,2})$/){
				$qry .= " AND sl_orders.Date <= '".$in{'to_date'}."' ";
			}
			if($in{'from_date'} =~ /^(\d{4})(\/)(\d{1,2})\2(\d{1,2})$/ && $in{'to_date'} =~ /^(\d{4})(\/)(\d{1,2})\2(\d{1,2})$/){
				my ($sth) = &Do_SQL("SELECT DATEDIFF('".$in{'to_date'}."','".$in{'from_date'}."')");
				$days = $sth->fetchrow_array();
				if($days > 0 || $in{'from_date'} eq $in{'to_date'}){
					#ok
				} else {
					$qry = "";
				}
			}
			my ($sth) = &Do_SQL("SELECT sl_orders_products.ID_orders, sl_orders_products.SalePrice, sl_orders_products.ID_products, COUNT(sl_orders_products.ID_products) AS Qty FROM sl_orders, sl_orders_payments, sl_orders_products WHERE sl_orders.ID_orders=sl_orders_payments.ID_orders AND sl_orders.ID_orders=sl_orders_products.ID_orders AND sl_orders_payments.Type='COD' AND LEFT(sl_orders_products.ID_products,1) <> '6' AND sl_orders.ID_warehouses='".$in{'id_warehouses'}."' AND sl_orders.ID_orders='0' $qry GROUP BY sl_orders_products.ID_products");
			$va{'wh_name'} = &load_name("sl_warehouses","ID_warehouses",$in{'id_warehouses'},"Name");
			$con_ids=0;
			while ($row = $sth->fetchrow_hashref){
				$not_assigned = 0;
				my ($sth_o) = &Do_SQL("SELECT count(*) FROM sl_orders WHERE ID_orders=".$row->{'ID_orders'}." AND ID_warehouses IS NULL");
				$not_assigned = $sth_o->fetchrow_array();
				if($not_assigned == 0){
					$ids[$con_ids] = $row->{'ID_orders'};
					$con_ids++;
				}
			}
			if($con_ids){
				chop($orders);
				my ($page,%rec);
				print "Content-type: text/html\n\n";
				print &build_page('header_print.html');
				$in{'db'} = 'sl_orders';
				$in{'toprint'}=1;
				for my $i(0..$#ids){
					&load_cfg('sl_orders');
					
					if ($ids[$i]){
						$in{'id_preorders'} = $ids[$i];
						$in{'toprint'}  = $ids[$i];
						my (%rec) = &get_record($db_cols[0],$ids[$i],$in{'db'});
						if ($rec{lc($db_cols[0])}){
							foreach $key (sort keys %rec) {
								$in{lc($key)} = $rec{$key};
								($db_valid_types{lc($key)} ne 'html') and ($in{lc($key)} =~ s/\n/<br>/g);
							}
						
							## User Info
							&get_db_extrainfo('admin_users',$in{'id_admin_users'});
							
							## Regular or Allnatpro Invoice?
					        my $customer_type=&load_name('sl_customers','ID_customers',$in{'id_customers'},'Type');
					        my $xcmd = $customer_type eq 'Allnatpro' ? '_allnatpro' : '';
							
							print &build_page('cod_invoice' . $xcmd .'.html');
							#print &html_print_record(%rec);
						}
					}
					
					if ($ids[$i+1]>0){
						print "<DIV STYLE='page-break-before:always'></DIV>";
					}
				}
				print qq|</body>\n</html>\n|;
				
			} else {
				$va{'message'} = &trans_txt('search_nomatches');	
				print "Content-type: text/html\n\n";
				print &build_page('toprint_msg.html');
			}
			
		}else{
			$va{'message'} = &trans_txt('search_nomatches');	
			print "Content-type: text/html\n\n";
			print &build_page('toprint_msg.html');
		}

	} else {
		$va{'message'} = &trans_txt('search_nomatches');	
		print "Content-type: text/html\n\n";
		print &build_page('toprint_msg.html');
	}
}


sub cod_orderstofulfill{
# --------------------------------------------------------
# Forms Involved: 
# Created on: 02/09/09 10:33:51
# Author: MCC C. Gabriel Varela S.
# Description :   
# Parameters :
# Last Modified on: 02/10/09 09:45:31
# Last Modified by: MCC C. Gabriel Varela S: Se continua. Se filtra por substatus de producto and StatusPrd='None'
# Last Modified on: 02/11/09 11:04:59
# Last Modified by: MCC C. Gabriel Varela S: Se continua.
# Last Modified on: 03/19/09 12:47:08
# Last Modified by: MCC C. Gabriel Varela S: Se toma en cuenta codshptype y se pone condici�n and sl_orders.Status='Processed'
# Last Time Modified by RB on 11/30/2011: Se agrego opcion para exportar file endicia

	my $selectv,$gb,$query,$querycount;	
	my $shp_type = '';
	my $query = '';
	my $my_ip = &get_ip;

	if ($in{'mult'}){

		($va{'sitems'},$va{'mitems'},$va{'xitems'},$va{'oitems'}) = ('off','on','off','off');
		$querycount = " AND 1 < (SELECT COUNT(*) FROM sl_orders_products WHERE Status='Active' AND ID_orders=sl_orders.ID_orders AND sl_orders_products.ID_products NOT LIKE '6%')";
		$query .= " AND shp_type = '". $cfg{'codshptype'} ."' ";
		$query .= " AND sl_orders.StatusPrd = 'None'";

	}elsif($in{'xd'}){

		($va{'sitems'},$mitems{'va'},$va{'xitems'},$va{'oitems'}) = ('off','off','on','off');
		$querycount = "";
		$query .= " AND sl_orders.shp_type = 2 ";
		$query .= " AND sl_orders.StatusPrd = 'None'";
		
	}elsif($in{'ostock'}){

		($va{'sitems'},$va{'mitems'},$va{'xitems'},$va{'oitems'}) = ('off','off','off','on');
		$querycount = "";
		$query .= " AND sl_orders.StatusPrd = 'Out of Stock' ";

	}else{

		($va{'sitems'},$va{'mitems'},$va{'xitems'},$va{'oitems'}) = ('on','off','off','off');
		$querycount = "AND 1 = (SELECT COUNT(*) FROM sl_orders_products  WHERE Status='Active' AND ID_orders=sl_orders.ID_orders AND sl_orders_products.ID_products NOT LIKE '6%')";
		$query .= " AND shp_type = '". $cfg{'codshptype'} ."' ";
		$query .= " AND sl_orders.StatusPrd = 'None'";
	}
	
	$selectv = "SELECT 
		sl_orders_products.ID_products
		, COUNT(sl_orders_products.ID_orders)as NPreorders
		, GROUP_CONCAT(sl_orders_products.ID_orders separator ',') AS Preorders
		, '' PaymentsCOD
		, '' PaymentsNotCOD
		, '' ID_parts
	FROM (
		SELECT *
		FROM sl_orders
		WHERE sl_orders.Status='Processed'
		AND sl_orders.Ptype = 'COD'
		$query
	)sl_orders
	INNER JOIN  sl_orders_products ON sl_orders_products.ID_orders=sl_orders.ID_orders
	INNER JOIN sl_skus ON (sl_orders_products.ID_products=ID_sku_products)
	LEFT JOIN  sl_warehouses_batches_orders ON sl_warehouses_batches_orders.ID_orders_products = sl_orders_products.ID_orders_products AND sl_warehouses_batches_orders.Status IN ('In Fulfillment','Shipped','In Transit')
	WHERE sl_warehouses_batches_orders.ID_orders_products IS NULL
	AND sl_orders_products.ID_products NOT LIKE '6%' 
	AND (ISNULL(sl_orders_products.ShpDate)  OR sl_orders_products.ShpDate='0000-00-00') 
	AND (ISNULL(sl_orders_products.Tracking) OR sl_orders_products.Tracking='')
	AND (ISNULL(sl_orders_products.ShpProvider) OR sl_orders_products.ShpProvider='')
	AND sl_orders_products.Status = 'Active'
	AND sl_orders_products.SalePrice > 0
	AND sl_orders_products.Quantity > 0";
	$gb = "GROUP BY sl_orders_products.ID_products";

	if ($in{'action'} eq 'full'){

		if ($in{'tobackorder'}){
			$va{'fftype'} = 'Back Order';
			$prdstatus = 'Out of Stock';
		}elsif ($in{'dropship'}){
			$va{'fftype'} = 'Dropship';
			$prdstatus = 'In Dropshipment';
		}else{
			$va{'fftype'} = 'Fullfill';
			$prdstatus = 'In Fulfillment';
			&auth_logging('tofulfill',1);
		}
		
		$in{'db'}='sl_orders';
		my $notes_message = "The order has been marked to : $va{'fftype'}";
		my $str_id_products = '';
		foreach my $key (keys %in){
			if ($key =~ /pid_(\d+)/){
				$str_id_products .= "$1,";
			}
		}
		chop($str_id_products);
		
		## Operacion encapsulada en TRANSACTION
		&Do_SQL("START TRANSACTION");

		my $query2 = " AND sl_orders_products.ID_products IN ($str_id_products) ";
		my $selectv2 = "$selectv $querycount $query2 $gb";
		
		## Para prevenir problemas con GROUP_CONCAT
		&Do_SQL("SET group_concat_max_len = 204800;");

		my $sth = &Do_SQL("SELECT GROUP_CONCAT(Preorders separator ',')Preorders FROM( $selectv2 ) tmp");
		while (my $rec = $sth->fetchrow_hashref) {

			$in{'orders'} = int($in{'orders'});
			$in{'orders'} = $rec->{'NPreorders'} if($in{'orders'}>$rec->{'NPreorders'});
			
			if ($rec->{'Preorders'}){
			
				&Do_SQL("UPDATE sl_orders SET StatusPrd = '$prdstatus' WHERE ID_orders IN($rec->{'Preorders'});");

				my @ary = split(/,/, $rec->{'Preorders'});
				my $i = 0;
				my $values_sl_orders_notes = '';
				my $values_logging_orders_updated = '';
				my $values_logging_orders_note_added = '';
				my $message_to_print = qq|<br><br><table border="1" cellspacing="0" cellpadding="5" class="formtable" width="50%">
				<tr>
					<th class="menu_bar_title">#</th>
					<th class="menu_bar_title">ID order</th>
					<th class="menu_bar_title">Message</th>
				</tr>|;
				for (0..$#ary){

					my $id_orders = $ary[$_];
					$i = ($_ + 1);

					$values_sl_orders_notes .= "($id_orders, '$notes_message', 'Low', CURDATE(), CURTIME(), $usr{'id_admin_users'},'1'),";
					$values_logging_orders_updated .= "(CURDATE(), CURTIME(), 'orders_updated', '$id_orders', 'Application', '$in{'db'}', '$in{'cmd'}', $usr{'id_admin_users'}, '$my_ip'),";
					$values_logging_orders_note_added .= "(CURDATE(), CURTIME(), 'orders_note_added', '$id_orders', 'Application', '$in{'db'}', '$in{'cmd'}', $usr{'id_admin_users'}, '$my_ip'),";
					$message_to_print .= qq|
					<tr>
						<td align="right">$i</td>
						<td align="right">$id_orders</td>
						<td>$notes_message</td>
					</tr>|;

				}
				chop($values_sl_orders_notes);
				chop($values_logging_orders_updated);
				chop($values_logging_orders_note_added);
				$message_to_print .= qq|</table><br>$i |.&trans_txt("search_matches");

				&Do_SQL("INSERT INTO admin_logs (LogDate, LogTime, Message, Action, Type, tbl_name, Logcmd, ID_admin_users, IP) VALUES $values_logging_orders_updated;");				
				&Do_SQL("INSERT INTO sl_orders_notes (ID_orders, Notes, Type, Date, Time, ID_admin_users,ID_orders_notes_types) VALUES $values_sl_orders_notes;");
				&Do_SQL("INSERT INTO admin_logs (LogDate, LogTime, Message, Action, Type, tbl_name, Logcmd, ID_admin_users, IP) VALUES $values_logging_orders_note_added;");				
				
				$va{'message_good'} = &trans_txt('actionapplied');
				$va{'message'} .= $message_to_print;
			}else{
				$va{'message_error'} = &trans_txt('search_nomatches');				
			}
		}
		
		&Do_SQL("COMMIT");
		# &Do_SQL("ROLLBACK"); # Debug only
		
		print "Content-type: text/html\n\n";
		print &build_page('toprint_msg.html');
		return;

	}elsif($in{'id_products'}){
		
		$query .= " and sl_orders_products.ID_products = '". $in{'id_products'} ."' ";
		$selectv .= " $querycount $query $gb";

		if ($in{'action'}==1){

			&auth_logging('tofulfill',1);
			$va{'fftype'} = 'Fullfill';
			my ($sth) = &Do_SQL("SET group_concat_max_len = 204800;");
			my $sth=&Do_SQL("$selectv");
			my $update_id_orders;
			while(my $rec=$sth->fetchrow_hashref){
				
				$update_id_orders = $rec->{'Preorders'};			

			}

			## Notas y Logs
			if ($update_id_orders ne ''){
				my $sth = &Do_SQL("SELECT ID_orders FROM sl_orders WHERE ID_orders IN ($update_id_orders)");
				while (my $rec=$sth->fetchrow_hashref){
					my $sth2 = &Do_SQL("UPDATE sl_orders SET StatusPrd = 'In Fulfillment' WHERE ID_orders='$rec->{'ID_orders'}';");
					if ($sth2->rows()) {

						$in{'db'}='sl_orders';
						&auth_logging('orders_updated',$rec->{'ID_orders'});
						#my ($sth2) = &Do_SQL("INSERT INTO sl_orders_notes SET Notes='The order has been marked to : $va{'fftype'}',Type='Low',ID_orders='$rec->{'ID_orders'}' ,Date=CURDATE(),Time=CURTIME(),ID_admin_users='$usr{'id_admin_users'}';");
						&add_order_notes_by_type($rec->{'ID_orders'},"The order has been marked to : $va{'fftype'}","Low");
						&auth_logging('orders_note_added',$rec->{'ID_orders'});

					}
				}
			}

			$va{'message'}="<script language='JavaScript'>alert('The orders have been updated.')</script>";
			&cod_orderstofulfillstart($selectv);
			
			(!$in{'page'}) and ($in{'page'} = 'home');
			
			if ($in{'print'}){
			
				print "Content-type: text/html\n\n";
				print &build_page('header_print.html');
				print &build_page('cod_orderstofulfill_print.html');
			
			}else{
			
				print "Content-type: text/html\n\n";
				print &build_page('cod_orderstofulfill.html');
			
			}
		
		}else{
		
			my $sth=&Do_SQL("$selectv");
			my $rec=$sth->fetchrow_hashref;
			$va{'choices'} = &load_choices($rec->{'ID_products'});
			$va{'model'} = &load_name('sl_products','ID_products',substr($rec->{'ID_products'},3,6),'Model');
			$va{'name'} = &load_name('sl_products','ID_products',substr($rec->{'ID_products'},3,6),'Name');
			$va{'orders'}=$rec->{'NPreorders'};
			
			print "Content-type: text/html\n\n";			
			print &build_page('cod_orderstofulfill_form.html');
		}
	}elsif(!$in{'id_products'}){
		$selectv .= " $querycount $query $gb";
		&cod_orderstofulfillstart($selectv);
		
		(!$in{'page'}) and ($in{'page'} = 'home');
		if ($in{'print'}){
			print "Content-type: text/html\n\n";
			print &build_page('header_print.html');
			print &build_page('cod_orderstofulfill_print.html');
		}else{
			print "Content-type: text/html\n\n";
			print &build_page('cod_orderstofulfill.html');
		}
	}
}

sub cod_orderstofulfillstart{
# --------------------------------------------------------
# Forms Involved: 
# Created on: 02/09/09 18:10:30
# Author: MCC C. Gabriel Varela S.
# Description :   
# Parameters :
# Last Modified on: 02/10/09 09:45:31
# Last Modified by: MCC C. Gabriel Varela S: Se contin�a
# Last Modified on: 07/16/09 13:17:32
# Last Modified by: MCC C. Gabriel Varela S: Se hace que incorpore las partes si es el caso.
# Last Modified RB: 08/13/09  13:52:45 -- Se separa el link para ver el item to fulfill del link para ver el inventory del item. El primero estaba sobre el <tr>  y no permitia desplegar el ajax del inventory


	my ($selectv)=@_;
	my $page_limit;
	
	$va{'matches'} = 1;
	$va{'pageslist'} = 1;
	my $sth=&Do_SQL("$selectv");
	$va{'matches'} = $sth->rows;

	if ($va{'matches'}>0){

		my %all_inventory = &inventory_all(0);

		(!$in{'nh'}) and ($in{'nh'}=1);
		$first = ($in{'nh'} - 1) * $usr{'pref_maxh'};			
		($va{'pageslist'},$qs) = &pages_list($in{'nh'},"/cgi-bin/mod/$usr{'application'}/admin",$va{'matches'},$usr{'pref_maxh'});
		
		if ($in{'print'}){
			$page_limit = '';
		}else{
			$page_limit = " LIMIT $first,$usr{'pref_maxh'}";
		}

		my (@c) = split(/,/,$cfg{'srcolors'});

		my $sth=&Do_SQL("$selectv $page_limit");
		while(my $rec=$sth->fetchrow_hashref){

			$d = 1 - $d;
			
			$cadparts="";
			if ($rec->{'ID_products'} ne ''){

				my $sth_parts = &Do_SQL("SELECT ID_parts, (400000000+ID_parts)SKU, Qty FROM sl_skus_parts WHERE ID_sku_products='".$rec->{'ID_products'}."'");
				while (my $rec_parts = $sth_parts->fetchrow_hashref()){

					my $this_link = ($all_inventory{$rec_parts->{'SKU'}}{'inventory'} > 0 and !$in{'print'}) ? 
						"<a class=\"scroll\" href=\"#ajax_inv$rec->{'ID_products'}\" onClick=\"popup_show('ajax_windows', 'ajax_drag', 'ajax_exit', 'screen-center', -1, -1,'ajax_inv$rec->{'ID_products'}');loadDoc('/cgi-bin/common/apps/ajaxbuild?ajaxbuild=inventory&id_products=".$rec_parts->{'SKU'}."&cols=ID,Warehouse,In Batch,Qty&extradata=".$id_warehouses.":".$nopack.":".$include_all."');\">
			  				<img id='idajax_inv".$rec_parts->{'SKU'}."' src='[va_imgurl]/[ur_pref_style]/b_view.png' title='More Info' alt='More Info' border='0'>
			  			</a>" : '';

					$cadparts.= "<tr bgcolor='$c[$d]'>\n";
					$cadparts.= "	<td class='smalltext' valign='top' align='center' colspan='2'></td>\n
									<td class='smalltext' valign='top' align='center'>".$rec->{'NPreorders'}*$rec_parts->{'Qty'}." x ".&format_sltvid($rec_parts->{'SKU'}). "</td>\n
									<td class='smalltext' valign='top'>".&load_db_names('sl_parts','ID_parts',$rec_parts->{'ID_parts'},'[Name]')."</td>\n
									<td class='smalltext' valign='top'>".format_number($all_inventory{$rec_parts->{'SKU'}}{'inbatch'})."</td>\n
									<td class='smalltext' valign='top'>".format_number($all_inventory{$rec_parts->{'SKU'}}{'inventory'})."</td>\n
									<td class='smalltext' valign='top'>".$this_link."</td>\n
								</tr>\n";
				}

				#$cadparts.= "<table border='0' cellspacing='0' cellpadding='4' width='100%' class='formtable'>\n";
				# @partsin=split(/,/,$rec->{'ID_parts'});
				# for(0..$#partsin){
				# 	@qtyid=split(/\|/,$partsin[$_]);
				# 	my $part9digit = 400000000+$qtyid[1];
				# 	my ($link_inv, $qty_inv, $qty_batch) = &inventory_by_id($part9digit);
				# 	$cadparts.= "<tr bgcolor='$c[$d]'>\n";
				# 	$cadparts.= "	<td class='smalltext' valign='top' align='center' colspan='2'></td>\n
				# 					<td class='smalltext' valign='top' align='center'>".$rec->{'NPreorders'}*$qtyid[0]." x ".&format_sltvid($part9digit). "</td>\n
				# 					<td class='smalltext' valign='top'>".&load_db_names('sl_parts','ID_parts',$qtyid[1],'[Name]')."</td>\n
				# 					<td class='smalltext' valign='top'>".format_number($qty_batch)."</td>\n
				# 					<td class='smalltext' valign='top'>".format_number($qty_inv)."</td>\n
				# 					<td class='smalltext' valign='top'>".$link_inv."</td>\n
				# 				</tr>\n";
				# }
				#$cadparts.= "</table>\n";
			}
			
			my $choices = &load_choices($rec->{'ID_products'});
			$va{'searchresults'} .= "<tr bgcolor='$c[$d]' onmouseover='m_over(this)' onmouseout='m_out(this)'>\n";
			$va{'searchresults'} .= "  <td class='smalltext' valign='top' align='center'>";
			if (!$in{'print'}){
				$va{'searchresults'} .= "
										<input class='checkbox' type='checkbox' name='pid_$rec->{'ID_products'}' value='$rec->{'NPreorders'}'>\n
										<input type='button' name='btnid_$rec->{'ID_products'}' value='S' onClick=\"trjump('/cgi-bin/mod/wms/admin?cmd=$in{'cmd'}&id_products=$rec->{'ID_products'}&mult=$in{'mult'}&ostock=$in{'ostock'}')\">\n";
			}
			$va{'searchresults'} .= "	</td>\n";
			$va{'searchresults'} .= "  <td class='smalltext' valign='top' align='center'>$rec->{'NPreorders'} </td>";
			$va{'searchresults'} .= "  <td class='smalltext' valign='top' onClick=\"trjump('/cgi-bin/mod/wms/admin?cmd=$in{'cmd'}&id_products=$rec->{'ID_products'}&mult=$in{'mult'}&ostock=$in{'ostock'}')\">".&format_sltvid($rec->{'ID_products'}). "</td>\n";
			$va{'searchresults'} .= "  <td class='smalltext' valign='top' onClick=\"trjump('/cgi-bin/mod/wms/admin?cmd=$in{'cmd'}&id_products=$rec->{'ID_products'}&mult=$in{'mult'}&ostock=$in{'ostock'}')\">".&load_db_names('sl_products','ID_products',substr($rec->{'ID_products'},3,6),'[Name]<br>[Model]')." $choices </td>\n";
			$va{'searchresults'} .= "  <td class='smalltext' valign='top' colspan='3'><span name='ajax_inv$rec->{'ID_products'}' id='ajax_inv$rec->{'ID_products'}'>&nbsp;</span></td>\n";
			$va{'searchresults'} .= "</tr>$cadparts\n";

		}
	}else{
		$va{'pageslist'} = 1;
		$va{'searchresults'} = qq|
		<tr>
			<td colspan='3' align="center">|.&trans_txt('search_nomatches').qq|</td>
		</tr>\n|;
	}
}

sub cod_orderstobefulfilled {
# --------------------------------------------------------
# Forms Involved: 
# Created on: 02/10/09 11:48:51
# Author: MCC C. Gabriel Varela S.
# Description :   
# Parameters :
# Last Modified on: 02/11/09 10:38:58
# Last Modified by: MCC C. Gabriel Varela S: Se continua
# Last Modified on: 02/12/09 16:57:08
# Last Modified by: MCC C. Gabriel Varela S: Se agrega by warehouses
# Last Modified on: 02/13/09 09:00:33
# Last Modified by: MCC C. Gabriel Varela S: Se continua
# Last Modified on: 02/16/09 10:05:43
# Last Modified by: MCC C. Gabriel Varela S: Se hace que se considere ID_warehouses como nulo o cero. Se agregan validaciones para n�meros de pre�rdenes by warehouses.
# Last Modified on: 02/18/09 16:29:12
# Last Modified by: MCC C. Gabriel Varela S: Se cambia consulta para contemplar covertura por paises
# Last Modified on: 03/06/09 12:14:14
# Last Modified by: MCC C. Gabriel Varela S: Cuando se remueven del manifiesto, se pone ID_warehouses=0 instead of Null. Tambi�n se hace la validaci�n de null o cero aplicada para todo.
# Last Modified on: 03/19/09 12:47:41
# Last Modified by: MCC C. Gabriel Varela S: Se toma en cuenta codshptype y se pone condicion and sl_orders.Status='Processed'. Se integra impresi�n de invoices.
# Last Modified on: 05/22/09 17:21:37
# Last Modified by: MCC C. Gabriel Varela S: Se reemplazan consultas de agrupado por warehouses.
# Last Modified RB: 06/29/09  17:45:26 Se agrega el llamado a cod_confirmation_list_add y cod_confirmation_list_delete para asignar las ordenes COD a una lista de confirmacion que depende de los ids que se hayan ingresado en el modulo administration para el warehouses virtual. Si no existiesen usuarios, por el momento se estarian asignando a Rigoberto, Crystian e Ilene en Mexico.
# Last Modified on: 07/14/09 16:09:38
# Last Modified by: MCC C. Gabriel Varela S: Se cambia la consulta para cuando se presenta el caso que la vista es por warehouses y se selecciona un warehouse. Tambi�n para su action correspondiente.
# Last Modified on: 07/15/09 13:04:51
# Last Modified by: MCC C. Gabriel Varela S: Se cambian consultas para vista de warehouses para calcular de forma diferente las no cubiertas
# Last Modified on: 07/16/09 10:25:58
# Last Modified by: MCC C. Gabriel Varela S: Se hace que se puedan imprimir los invoices por warehouse o por id de preorden.
# Last Modified by RB on 03/31/2010: Se elimina el telefono del cliente por peticion de Alma Hubbe
# Last Modified by RB on 03/31/2011 05:55:33 PM : Se agrega validacion para ordenes Allnatpro
# Last Modified by RB on 05/22/2011 17:10:33 PM : Se agrega paso de ordenes COD a metodo PostPay basado en parametros de configuracion. Tambien se elimina la nota si se desasigna la orden del driver
	my $selectv,$gb,$selectvbp,$selectvbw,$query,$querycount;
	
	my $id_zones = $in{'id_zones'};
	$id_zones =~ s/\|/\,/g;	
	my ($idzone) = "AND sl_orders.ID_zones IN (".$id_zones.") " if($in{'id_zones'} and $in{'id_zones'}!="");	
		
	if($in{'action'}==1){

		if($in{'setwarehouses'}==1){

				(!$in{'page'}) and ($in{'page'} = 'home');
				my $err;
				if($in{'id_warehouses'}eq"" and $in{'remove'}eq'0'){
					++$err;
					$error{'id_warehouses'} = &trans_txt('required');
				}
				if($in{'id_ordersttia'} eq "" and ($in{'remove'} eq '0' or $in{'remove'} eq '1')){
					++$err;
					$error{'id_ordersttia'} = &trans_txt('required');
				}

				if($err==0){

					if($in{'remove'}eq'0'){

						my $cadorders=$in{'id_ordersttia'};
						$in{'id_ordersttia'}=~s/\|/\,/g;

						if($in{'id_ordersttia'} ne ""){
							$selectvx = "SELECT 1,ID_orders,1,1,1 FROM sl_orders WHERE ID_orders IN($in{'id_ordersttia'})";
						}else{
							$query.= ($in{'remove'}eq'0' and $in{'id_ordersttia'} ne "") ? " AND sl_orders.ID_orders in ($in{'id_ordersttia'})" : '';
							$gb="group by sl_orders_products.ID_orders";
							$selectvx ="$selectvbp $querycount $query $gb";	
						}

						my ($sth) = &Do_SQL("SET group_concat_max_len = 204800;");
						my $sth=&Do_SQL("$selectvx");

						while(my ($a,$id_orders,$c,$d,$e) = $sth->fetchrow()){

							&Do_SQL("UPDATE sl_orders SET ID_warehouses=0 WHERE ID_orders IN ($id_orders)");
							&Do_SQL("DELETE FROM sl_orders_notes WHERE ID_orders IN ($id_orders) and Type='PP Order';");
							&cod_confirmation_list_delete($id_orders);

							## Release From Batch
							my ($sth) = &Do_SQL("SELECT GROUP_CONCAT(ID_warehouses_batches) FROM sl_warehouses_batches_orders
												INNER JOIN sl_orders_products USING(ID_orders_products)
												WHERE ID_orders IN ($id_orders) 
												AND sl_warehouses_batches_orders.Status IN ('In Fulfillment','Error');");
							my ($id_warehouses_batches) = $sth->fetchrow;

							if($id_warehouses_batches) { 
								my $query = "UPDATE sl_warehouses_batches_orders INNER JOIN sl_orders_products 
											USING(ID_orders_products) SET sl_warehouses_batches_orders.Status = 'Cancelled' 
											WHERE ID_orders IN ($id_orders)
											AND sl_warehouses_batches_orders.Status IN ('In Fulfillment','Error');";
								my ($sth) = &Do_SQL($query);
							}
						}
						
						my $cadorders=$in{'id_ordersttia'};				
						$cadorders=~s/\|/\,/g;
						
						&Do_SQL("UPDATE sl_orders SET ID_warehouses = $in{'id_warehouses'} WHERE ID_orders IN ($cadorders)");

						$va{'message'}="<script language='JavaScript'>
							alert('The order(s) have been updated');
							</script>";

						##Assign to batch
						$this_type = &load_name('sl_warehouses','ID_warehouses',$in{'id_warehouses'},'Type');
						#if($this_type =~ /Drop Ship|Outsource/) {
						my $this_order = 0;
						my $id_warehouses_batches = &create_warehouse_batch_file($in{'id_warehouses'});
						
						my $Query = "SELECT ID_orders,ID_orders_products FROM sl_orders_products WHERE ID_orders IN ($cadorders) AND Status IN ('Active','Exchange','Undeliverable','ReShip') AND SalePrice >= 0 ORDER BY ID_orders;";
						my ($sth_op) = &Do_SQL($Query);
						my $a =0;

						while ($rec_op = $sth_op->fetchrow_hashref){
												
							my $Query_w = "SELECT COUNT(*), ID_warehouses_batches
											FROM sl_warehouses_batches_orders
											WHERE ID_orders_products    = ".int($rec_op->{'ID_orders_products'})." 
									 		AND Status IN ('In Fulfillment','Shipped','In Transit'));";
							($sth2) = &Do_SQL($Query_w);		  
							my ($countw, $idw) = $sth2->fetchrow();

							if($countw == 0){

								++$a;
								my $query = "INSERT INTO sl_warehouses_batches_orders SET ID_warehouses_batches=".$id_warehouses_batches.", ID_orders_products=".int($rec_op->{'ID_orders_products'}).", Status='In Fulfillment', Date=CURDATE(),Time=CURTIME(),ID_admin_users='$usr{'id_admin_users'}'; ";
								($sth3) = &Do_SQL($query);

								if($this_order ne $rec_op->{'ID_orders'}) {
									## Order Assigned
									$this_order = $rec_op->{'ID_orders'};
									if($this_order > 0) {
										#my ($sth) = &Do_SQL("INSERT INTO sl_orders_notes SET Notes='".&trans_txt('order_batchadded')." $id_warehouses_batches',Type='High',Date=CURDATE(),Time=CURTIME(),ID_admin_users='$usr{'id_admin_users'}', ID_orders = '$rec_op->{'ID_orders'}';");
										&add_order_notes_by_type($rec_op->{'ID_orders'},&trans_txt('order_batchadded')." $id_warehouses_batches","High");
										&auth_logging('order_batchadded', $rec_op->{'ID_orders'});
									}
								}

							}
												
						}

						if($a){
						
							&Do_SQL("UPDATE sl_warehouses_batches SET Status = 'Assigned' WHERE ID_warehouses_batches = $id_warehouses_batches;"); 
							
							#&cod_orderstofulfillstart_bypreorders($selectvbp);
							&cod_confirmation_list_add($in{'id_warehouses'},$cadorders);
							$va{'message'}="<script language='JavaScript'>
							alert('The orders have been updated and assigned to batch $id_warehouses_batches.');
							</script>";

						}else{

							$va{'message'}="<script language='JavaScript'>
							alert('Impossible to Assign to batch $id_warehouses_batches.');
							</script>";

						}
						
					}elsif($in{'remove'}eq'allw' or $in{'remove'}eq'1w'){					
						$in{'id_ordersttia'}=~s/\|/\,/g;

						if($in{'id_ordersttia'} ne ""){
							$selectvx = "SELECT 1,ID_orders,1,1,1 FROM sl_orders WHERE ID_orders IN($in{'id_ordersttia'})";
						}else{
							$query.= ($in{'remove'}eq'1w' and $in{'id_ordersttia'} ne "") ? " AND sl_orders.ID_orders in ($in{'id_ordersttia'})" : '';
							$gb="group by sl_orders_products.ID_orders";
							$selectvx ="$selectvbp $querycount $query $gb";	
						}

						my ($sth) = &Do_SQL("SET group_concat_max_len = 204800;");
						my $sth=&Do_SQL("$selectvx");
						while(my ($a,$id_orders,$c,$d,$e) = $sth->fetchrow()){
							&Do_SQL("UPDATE sl_orders SET ID_warehouses=0 WHERE ID_orders IN ($id_orders)");
							&Do_SQL("DELETE FROM sl_orders_notes WHERE ID_orders IN ($id_orders) and Type='PP Order';");
							&cod_confirmation_list_delete($id_orders);

							## Release From Batch
							my ($sth) = &Do_SQL("SELECT GROUP_CONCAT(ID_warehouses_batches) FROM sl_warehouses_batches_orders
												INNER JOIN sl_orders_products USING(ID_orders_products)
												WHERE ID_orders IN ($id_orders) 
												AND sl_warehouses_batches_orders.Status IN ('In Fulfillment','Error');");
							my ($id_warehouses_batches) = $sth->fetchrow;

							if($id_warehouses_batches) { 
								my $query = "UPDATE sl_warehouses_batches_orders INNER JOIN sl_orders_products 
											USING(ID_orders_products) SET sl_warehouses_batches_orders.Status = 'Cancelled' 
											WHERE ID_orders IN ($id_orders)
											AND sl_warehouses_batches_orders.Status IN ('In Fulfillment','Error');";
								my ($sth) = &Do_SQL($query);
							}
							
						}
						$va{'message'}="<script language='JavaScript'>alert('The orders have been updated.')</script>";
						#&cod_orderstofulfillstart($selectv);
						#(!$in{'page'}) and ($in{'page'} = 'home');
						
						
					}elsif($in{'remove'}eq'alls' or $in{'remove'}eq'1s'){
						my $id_zones = $in{'id_zones'};
						$id_zones =~ s/\|/\,/g;
						my ($idzone) = "AND sl_orders.ID_zones IN (".$id_zones.") " if($in{'id_zones'} and $in{'id_zones'}!="");
						$products    =" and sl_orders_products.ID_products=$in{'id_products'}" if($in{'id_products'}ne"");
						
						if($in{'id_ordersttia'} ne "" and $in{'remove'}eq'1s'){
							$selectvx = " AND sl_orders.ID_orders IN ($in{'id_ordersttia'})";
						}
						
						if($in{'batches'}){
							$selectvbp="SELECT sl_orders_products.ID_products,sl_orders_products.ID_orders,	( select sum(if(Type='COD',1,0)) from sl_orders_payments where sl_orders_payments.id_orders = sl_orders.ID_orders) PaymentsCOD,
	( select sum(if(Type!='COD',1,0)) from sl_orders_payments where sl_orders_payments.id_orders = sl_orders.ID_orders) PaymentsNotCOD,sl_orders.Date,sl_orders.shp_Zip,sl_orders.shp_City,sl_orders.shp_State,sl_orders.shp_Country,sl_orders.ID_warehouses,sl_orders.ID_zones,
									sl_warehouses_batches.ID_warehouses AS ON_BATCH, sl_warehouses_batches.ID_warehouses_batches, sl_warehouses_batches.Status AS bStatus
									FROM sl_orders_products
									INNER JOIN sl_orders ON (sl_orders_products.ID_orders=sl_orders.ID_orders)
									
									LEFT JOIN  sl_warehouses_batches_orders
										ON sl_warehouses_batches_orders.ID_orders_products = sl_orders_products.ID_orders_products 
										AND sl_warehouses_batches_orders.Status IN ('In Fulfillment')
									LEFT JOIN sl_warehouses_batches 
										ON sl_warehouses_batches.ID_warehouses_batches = sl_warehouses_batches_orders.ID_warehouses_batches
									WHERE (sl_warehouses_batches_orders.ID_orders_products IS NULL OR sl_warehouses_batches.Status IN ('New','Assigned') )
									AND sl_orders_products.ID_products NOT LIKE '6%' 
									AND (ISNULL(ShpDate) OR ShpDate='0000-00-00' OR ShpDate='') 
									AND (ISNULL(Tracking) OR Tracking='')
									AND (ISNULL(ShpProvider) OR ShpProvider='')
									AND shp_type=$cfg{'codshptype'}
									AND sl_orders.Status='Processed'
									AND Ptype='COD' 
									AND StatusPrd='In Fulfillment'
									AND sl_orders_products.Status='Active'
									AND sl_orders_products.SalePrice>0
									AND sl_orders_products.Quantity>0
									AND sl_orders.Status NOT IN ('Shipped','Void', 'Cancelled','System Error')
									$idzone $selectvx";		
						}else{
							$selectvbp="SELECT sl_orders_products.ID_products,sl_orders_products.ID_orders,( select sum(if(Type='COD',1,0)) from sl_orders_payments where sl_orders_payments.id_orders = sl_orders.ID_orders) PaymentsCOD,( select sum(if(Type!='COD',1,0)) from sl_orders_payments where sl_orders_payments.id_orders = sl_orders.ID_orders) PaymentsNotCOD,sl_orders.Date,sl_orders.shp_Zip,sl_orders.shp_City,sl_orders.shp_State,sl_orders.shp_Country,sl_orders.ID_warehouses,sl_orders.ID_zones
								FROM sl_orders_products
								INNER JOIN sl_orders ON (sl_orders_products.ID_orders=sl_orders.ID_orders)
								
								LEFT JOIN  sl_warehouses_batches_orders
									ON sl_warehouses_batches_orders.ID_orders_products = sl_orders_products.ID_orders_products 
									AND sl_warehouses_batches_orders.Status IN ('In Fulfillment','Shipped','In Transit')
								WHERE sl_warehouses_batches_orders.ID_orders_products IS NULL			
								AND sl_orders_products.ID_products not like '6%' 
								AND (isnull(ShpDate) or ShpDate='0000-00-00' or ShpDate='') 
								AND (isnull(Tracking) or Tracking='')
								AND (isnull(ShpProvider) or ShpProvider='')
								AND shp_type=$cfg{'codshptype'}
								AND sl_orders.Status='Processed'
								AND Ptype='COD' 
								AND StatusPrd='In Fulfillment'
								AND sl_orders_products.Status='Active'
								AND sl_orders_products.SalePrice>0
								AND sl_orders_products.Quantity>0
								AND sl_orders.Status not in ('Shipped','Void', 'Cancelled','System Error')
								$idzone $selectvx";
						}

						my ($sth) = &Do_SQL("SET group_concat_max_len = 204800;");
						my $sth=&Do_SQL("$selectvbp");
						while(my $rec=$sth->fetchrow_hashref){
							if($rec->{'ON_BATCH'} and $rec->{'bStatus'}){
								my $query = "UPDATE sl_warehouses_batches_orders INNER JOIN sl_orders_products 
										USING(ID_orders_products) SET sl_warehouses_batches_orders.Status = 'Cancelled' 
										WHERE ID_orders IN ($rec->{'ID_orders'})
										AND sl_warehouses_batches_orders.Status IN ('In Fulfillment','Error');";
								my ($sth) = &Do_SQL($query);							
							}
							
							&Do_SQL("Update sl_orders set StatusPrd='None',ID_warehouses=0 where ID_orders in ($rec->{'ID_orders'})");
						}
						$va{'message'}="<script language='JavaScript'>alert('The orders have been updated.')</script>";
					}
				}
				
		}
	}	

	if($in{'orders'}==1){
		($va{'sitems'},$va{'oitems'},$va{'zones'})=('off','on','off');
		&cod_orderstobefulfilled_orders;
	}elsif($in{'items'}==1){
		($va{'sitems'},$va{'oitems'},$va{'zones'})=('on','off','off');
		&cod_orderstobefulfilled_items;
	}else{
		($va{'sitems'},$va{'oitems'},$va{'zones'})=('off','off','on');
		&cod_orderstobefulfilled_zones;
	}
}

sub cod_orderstobefulfilled_orders {
# --------------------------------------------------------
	if($in{'batches'}){
		$selectvbp="SELECT sl_orders_products.ID_products,sl_orders_products.ID_orders,( select sum(if(Type='COD',1,0)) from sl_orders_payments where sl_orders_payments.id_orders = sl_orders.ID_orders) PaymentsCOD,( select sum(if(Type!='COD',1,0)) from sl_orders_payments where sl_orders_payments.id_orders = sl_orders.ID_orders) PaymentsNotCOD,sl_orders.Date,sl_orders.shp_Zip,sl_orders.shp_City,sl_orders.shp_State,sl_orders.shp_Country,sl_orders.ID_warehouses,sl_orders.ID_zones,
				sl_warehouses_batches.ID_warehouses AS ON_BATCH, sl_warehouses_batches.ID_warehouses_batches, sl_warehouses_batches.Status AS bStatus
			FROM sl_orders_products
			INNER JOIN sl_orders ON (sl_orders_products.ID_orders=sl_orders.ID_orders)
			
			LEFT JOIN  sl_warehouses_batches_orders
				ON sl_warehouses_batches_orders.ID_orders_products = sl_orders_products.ID_orders_products 
				AND sl_warehouses_batches_orders.Status IN ('In Fulfillment','Shipped','In Transit')  
			LEFT JOIN sl_warehouses_batches 
					ON sl_warehouses_batches.ID_warehouses_batches = sl_warehouses_batches_orders.ID_warehouses_batches	
			WHERE (sl_warehouses_batches_orders.ID_orders_products IS NULL OR sl_warehouses_batches.Status IN ('New','Assigned') )		
			AND sl_orders_products.ID_products not like '6%' 
			AND (isnull(ShpDate) or ShpDate='0000-00-00' or ShpDate='') 
			AND (isnull(Tracking) or Tracking='')
			AND (isnull(ShpProvider) or ShpProvider='')
			AND shp_type=$cfg{'codshptype'}
			AND sl_orders.Status='Processed'
			AND Ptype='COD' 
			AND StatusPrd='In Fulfillment'
			AND sl_orders_products.Status='Active'
			AND sl_orders_products.SalePrice>0
			AND sl_orders_products.Quantity>0
			AND sl_orders.Status not in ('Shipped','Void', 'Cancelled','System Error')";
	}else{
		$selectvbp="SELECT sl_orders_products.ID_products,sl_orders_products.ID_orders,( select sum(if(Type='COD',1,0)) from sl_orders_payments where sl_orders_payments.id_orders = sl_orders.ID_orders) PaymentsCOD,( select sum(if(Type!='COD',1,0)) from sl_orders_payments where sl_orders_payments.id_orders = sl_orders.ID_orders) PaymentsNotCOD,sl_orders.Date,sl_orders.shp_Zip,sl_orders.shp_City,sl_orders.shp_State,sl_orders.shp_Country,sl_orders.ID_warehouses
			FROM sl_orders_products
			INNER JOIN sl_orders ON (sl_orders_products.ID_orders=sl_orders.ID_orders)
			
			LEFT JOIN  sl_warehouses_batches_orders
				ON sl_warehouses_batches_orders.ID_orders_products = sl_orders_products.ID_orders_products 
				AND sl_warehouses_batches_orders.Status  IN ('In Fulfillment')
			WHERE sl_warehouses_batches_orders.ID_orders_products IS NULL			
			AND sl_orders_products.ID_products not like '6%' 
			AND (isnull(ShpDate) or ShpDate='0000-00-00' or ShpDate='') 
			AND (isnull(Tracking) or Tracking='')
			AND (isnull(ShpProvider) or ShpProvider='')
			AND shp_type=$cfg{'codshptype'}
			AND sl_orders.Status='Processed'
			AND Ptype='COD' 
			AND StatusPrd='In Fulfillment'
			AND sl_orders_products.Status='Active'
			AND sl_orders_products.SalePrice>0
			AND sl_orders_products.Quantity>0
			AND sl_orders.Status not in ('Shipped','Void', 'Cancelled','System Error')";		
	}
		
	$gb="group by sl_orders_products.ID_orders";
	#Comienza Si es vista por Ordenes
	$selectvbp.=" $querycount $query $gb";
	&cod_orderstofulfillstart_bypreorders($selectvbp);
	(!$in{'page'}) and ($in{'page'} = 'home');
		print "Content-type: text/html\n\n";
		print &build_page('cod_orderstobefulfilled_orders.html');
}

sub cod_orderstobefulfilled_items {
# --------------------------------------------------------
	$selectv="SELECT sl_orders_products.ID_products,COUNT(sl_orders_products.ID_orders)AS NPreorders,GROUP_CONCAT(sl_orders_products.ID_orders SEPARATOR ',')AS Preorders,( select sum(if(Type='COD',1,0)) from sl_orders_payments where sl_orders_payments.id_orders = sl_orders.ID_orders) PaymentsCOD,( select sum(if(Type!='COD',1,0)) from sl_orders_payments where sl_orders_payments.id_orders = sl_orders.ID_orders) PaymentsNotCOD, ID_parts
		FROM sl_orders_products
		LEFT JOIN  sl_warehouses_batches_orders
			ON sl_warehouses_batches_orders.ID_orders_products = sl_orders_products.ID_orders_products 
			AND sl_warehouses_batches_orders.Status  IN ('In Fulfillment')
		INNER JOIN  sl_orders ON (sl_orders_products.ID_orders=sl_orders.ID_orders)
		
		INNER JOIN sl_skus ON (sl_orders_products.ID_products=ID_sku_products)
		LEFT JOIN (SELECT ID_sku_products,GROUP_CONCAT(CONCAT(Qty,'|',ID_parts))AS ID_parts 
				FROM sl_skus_parts GROUP BY ID_sku_products)AS temp ON (sl_skus.ID_sku_products=temp.ID_sku_products)
		WHERE sl_warehouses_batches_orders.ID_orders_products IS NULL
		AND sl_orders_products.ID_products NOT LIKE '6%' 
		AND 1=(SELECT COUNT(*) 
					      FROM sl_orders_products 
					      WHERE STATUS='Active' 
					      AND ID_orders=sl_orders.ID_orders AND ID_products NOT LIKE '6%') 
		AND (ISNULL(ShpDate)  OR ShpDate='0000-00-00' OR ShpDate='') 
		AND (ISNULL(Tracking) OR Tracking='')
		AND (ISNULL(ShpProvider) OR ShpProvider='')
		AND shp_type=$cfg{'codshptype'}
		AND sl_orders.Status='Processed'
		AND Ptype='COD'
		AND StatusPrd='In Fulfillment'
		AND sl_orders_products.Status='Active'
		AND sl_orders_products.SalePrice>0
		AND sl_orders_products.Quantity>0
		AND sl_orders.Status NOT IN ('Shipped','Void', 'Cancelled','System Error')
		GROUP BY sl_orders_products.ID_products ";
	# #Si es vista por items
	
	
	$selectv.=" $querycount $query $gb";
	#&cod_orderstofulfillstart($selectv);
	(!$in{'page'}) and ($in{'page'} = 'home');

	
	$va{'matches'} = 1;
	$va{'pageslist'} = 1;
	my $sth=&Do_SQL("$selectv");
	$va{'matches'} = $sth->rows;
	if ($va{'matches'}>0){
		(!$in{'nh'}) and ($in{'nh'}=1);
		$first = ($in{'nh'} - 1) * $usr{'pref_maxh'};			
		($va{'pageslist'},$qs) = &pages_list($in{'nh'},"/cgi-bin/mod/$usr{'application'}/admin",$va{'matches'},$usr{'pref_maxh'});
		if ($in{'print'}){
			$page_limit = '';
		}else{
			$page_limit = " LIMIT $first,$usr{'pref_maxh'}";
		}		
		my (@c) = split(/,/,$cfg{'srcolors'});
		my $sth=&Do_SQL("$selectv $page_limit");
		while(my $rec=$sth->fetchrow_hashref){
			$d = 1 - $d;
			
			$cadparts="";
			if($rec->{'ID_parts'} ne ''){
				@partsin=split(/,/,$rec->{'ID_parts'});
				for(0..$#partsin){
					@qtyid=split(/\|/,$partsin[$_]);
					my $part9digit = 400000000+$qtyid[1];
					$cadparts.= "<tr bgcolor='$c[$d]'>\n";
					$cadparts.= "	<td class='smalltext' valign='top' align='center'></td>\n
									<td class='smalltext' valign='top' align='center'>".$rec->{'NPreorders'}*$qtyid[0]."</td>\n
									<td class='smalltext' valign='top'>".&format_sltvid($part9digit). "<br>".&load_db_names('sl_parts','ID_parts',$qtyid[1],'[Name]')."</td>\n
									<td class='smalltext' valign='top'>".&format_number( &calc_parts_inventory($part9digit) )." Units</td>\n
								</tr>\n";
				}
			}
			
			my $choices = &load_choices($rec->{'ID_products'});
			$va{'searchresults'} .= "<tr bgcolor='$c[$d]' onmouseover='m_over(this)' onmouseout='m_out(this)'>\n";
			$va{'searchresults'} .= "<td class='smalltext' valign='top' align='center'>
						<input type='checkbox' name='id_ordersttia' class='id_ordersttia' value='$rec->{'Preorders'}' class='checkbox'>
						$rec->{'NPreorders'}</td>";
						
			$va{'searchresults'} .= "  <td class='smalltext' valign='top' >".&format_sltvid($rec->{'ID_products'}). "</td>\n";
			$va{'searchresults'} .= "  <td class='smalltext' valign='top' >".&load_db_names('sl_products','ID_products',substr($rec->{'ID_products'},3,6),'[Name]<br>[Model]')." $choices</td>\n";
			$va{'searchresults'} .= "  <td class='smalltext' valign='top'>".&inventory_by_id($rec->{'ID_products'})."</td>\n";
			$va{'searchresults'} .= "</tr>$cadparts\n";

		}
	}else{
		$va{'pageslist'} = 1;
		$va{'searchresults'} = qq|
		<tr>
			<td colspan='3' align="center">|.&trans_txt('search_nomatches').qq|</td>
		</tr>\n|;
	}	
	print "Content-type: text/html\n\n";
	print &build_page('cod_orderstobefulfilled_items.html');
}

#sub cod_orderstobefulfilled_zones {
## --------------------------------------------------------
#	my ($selectvbp);
#	if($in{'batches'}){
#		$selectvbp="SELECT sl_orders_products.ID_products,sl_orders_products.ID_orders,( select sum(if(Type='COD',1,0)) from sl_orders_payments where sl_orders_payments.id_orders = sl_orders.ID_orders) PaymentsCOD,( select sum(if(Type!='COD',1,0)) from sl_orders_payments where sl_orders_payments.id_orders = sl_orders.ID_orders) PaymentsNotCOD,sl_orders.Date,sl_orders.shp_Zip,sl_orders.shp_City,sl_orders.shp_State,sl_orders.shp_Country,sl_orders.ID_warehouses,sl_orders.ID_zones,
#				sl_warehouses_batches.ID_warehouses AS ON_BATCH, sl_warehouses_batches.ID_warehouses_batches, sl_warehouses_batches.Status AS bStatus
#				FROM sl_orders_products
#				INNER JOIN sl_orders ON (sl_orders_products.ID_orders=sl_orders.ID_orders)
#				INNER JOIN (SELECT ID_orders,SUM(IF(TYPE='COD',1,0))AS PaymentsCOD,SUM(IF(TYPE!='COD',1,0))AS PaymentsNotCOD
#					FROM sl_orders_payments
#					GROUP BY ID_orders
#					HAVING PaymentsCOD>0) AS tempo ON (tempo.ID_orders=sl_orders.ID_orders)
#				LEFT JOIN  sl_warehouses_batches_orders
#					ON sl_warehouses_batches_orders.ID_orders_products = sl_orders_products.ID_orders_products 
#					AND sl_warehouses_batches_orders.Status IN ('In Fulfillment')
#				LEFT JOIN sl_warehouses_batches 
#					ON sl_warehouses_batches.ID_warehouses_batches = sl_warehouses_batches_orders.ID_warehouses_batches
#				WHERE (sl_warehouses_batches_orders.ID_orders_products IS NULL OR sl_warehouses_batches.Status IN ('New','Assigned') )
#				AND sl_orders_products.ID_products NOT LIKE '6%' 
#				AND (ISNULL(ShpDate) OR ShpDate='0000-00-00' OR ShpDate='') 
#				AND (ISNULL(Tracking) OR Tracking='')
#				AND (ISNULL(ShpProvider) OR ShpProvider='')
#				AND shp_type=$cfg{'codshptype'}
#				AND sl_orders.Status='Processed'
#				AND Ptype='COD' 
#				AND StatusPrd='In Fulfillment'
#				AND sl_orders_products.Status='Active'
#				AND sl_orders_products.SalePrice>0
#				AND sl_orders_products.Quantity>0
#				AND sl_orders.Status NOT IN ('Shipped','Void', 'Cancelled','System Error')
#				$idzone";		
#	}else{
#		$selectvbp="SELECT sl_orders_products.ID_products,sl_orders_products.ID_orders,( select sum(if(Type='COD',1,0)) from sl_orders_payments where sl_orders_payments.id_orders = sl_orders.ID_orders) PaymentsCOD,( select sum(if(Type!='COD',1,0)) from sl_orders_payments where sl_orders_payments.id_orders = sl_orders.ID_orders) PaymentsNotCOD,sl_orders.Date,sl_orders.shp_Zip,sl_orders.shp_City,sl_orders.shp_State,sl_orders.shp_Country,sl_orders.ID_warehouses,sl_orders.ID_zones
#			FROM sl_orders_products
#			INNER JOIN sl_orders ON (sl_orders_products.ID_orders=sl_orders.ID_orders)
#			INNER JOIN (SELECT ID_orders,sum(if(Type='COD',1,0))as PaymentsCOD,sum(if(Type!='COD',1,0))as PaymentsNotCOD
#				FROM sl_orders_payments
#				GROUP BY ID_orders
#				HAVING PaymentsCOD>0) AS tempo ON (tempo.ID_orders=sl_orders.ID_orders)
#			LEFT JOIN  sl_warehouses_batches_orders
#				ON sl_warehouses_batches_orders.ID_orders_products = sl_orders_products.ID_orders_products 
#				AND sl_warehouses_batches_orders.Status IN ('In Fulfillment','Shipped','In Transit')  
#			WHERE sl_warehouses_batches_orders.ID_orders_products IS NULL			
#			AND sl_orders_products.ID_products not like '6%' 
#			AND (isnull(ShpDate) or ShpDate='0000-00-00' or ShpDate='') 
#			AND (isnull(Tracking) or Tracking='')
#			AND (isnull(ShpProvider) or ShpProvider='')
#			AND shp_type=$cfg{'codshptype'}
#			AND sl_orders.Status='Processed'
#			AND Ptype='COD' 
#			AND StatusPrd='In Fulfillment'
#			AND sl_orders_products.Status='Active'
#			AND sl_orders_products.SalePrice>0
#			AND sl_orders_products.Quantity>0
#			AND sl_orders.Status not in ('Shipped','Void', 'Cancelled','System Error')
#			$idzone";
#	}
#		
#	my $sth=&Do_SQL("$selectvbp");
#	$va{'matches'}	= $sth->rows;	
#	$va{'pageslist'}= $va{'matches'};
#	
#	if($va{'matches'}>0){		
#		(!$in{'nh'}) and ($in{'nh'}=1);
#		$first = ($in{'nh'} - 1) * $usr{'pref_maxh'};			
#		($va{'pageslist'},$qs) = &pages_list($in{'nh'},"/cgi-bin/mod/$usr{'application'}/admin",$va{'matches'},$usr{'pref_maxh'});
#		$va{'searchresults'}="";
#		
#		my $page_limit;
#		$page_limit = " LIMIT $first,$usr{'pref_maxh'}";
#
#		my (@c) = split(/,/,$cfg{'srcolors'});
#		my $sth=&Do_SQL("$selectvbp $page_limit");
#				
#		while(my $rec=$sth->fetchrow_hashref){			
#			my $onwarehouse = "";
#			my $onbatch 	= "";
#			$d = 1 - $d;
#			my $choices	= &load_choices($rec->{'ID_products'});
#			$onwarehouse = "---";
#			$onwarehouse = &load_name('sl_warehouses','ID_warehouses',$rec->{'ID_warehouses'},'Name') if($rec->{'ID_warehouses'}ne"NULL" and $rec->{'ID_warehouses'}ne"");
#			$onbatch     = $rec->{'ID_warehouses_batches'} if($rec->{'ON_BATCH'}ne"NULL" and $rec->{'ON_BATCH'}ne"");
#			$sbatch     = $rec->{'bStatus'} if($rec->{'ON_BATCH'}ne"NULL" and $rec->{'ON_BATCH'}ne"");
#			$va{'searchresults'} .= "<tr bgcolor='$c[$d]' onmouseover='m_over(this)' onmouseout='m_out(this)'>\n";
#			$va{'searchresults'} .= "  <td class='smalltext' valign='top' align='center'>
#							<input type='checkbox' name='id_ordersttia' class='id_ordersttia' value='$rec->{'ID_orders'}' class='checkbox'>
#							$rec->{'ID_orders'}</td>";
#			$va{'searchresults'} .= "  <td class='smalltext' valign='top'>".&load_name('sl_zones','ID_zones',$rec->{'ID_zones'},'Name')."</td>\n";							
#			$va{'searchresults'} .= "  <td class='smalltext' valign='top'>$rec->{'Date'}</td>\n";			
#			$va{'searchresults'} .= "  <td class='smalltext' valign='top'>($rec->{'shp_Zip'}) $rec->{'shp_City'},$rec->{'shp_State'}</td>\n";
#			$va{'searchresults'} .= "  <td class='smalltext' valign='top'>".$onwarehouse."</td>\n";
#			$va{'searchresults'} .= "  <td class='smalltext' valign='top'>".$onbatch."</td>\n";
#			$va{'searchresults'} .= "  <td class='smalltext' valign='top'>".$sbatch."</td>\n";
#			$va{'searchresults'} .= "</tr>\n";			
#			
#		}
#	}else{
#		$va{'pageslist'} = 1;
#		$va{'searchresults'} = qq|
#		<tr>
#			<td colspan='7' align="center">|.&trans_txt('search_nomatches').qq|</td>
#		</tr>\n|;		
#	}	
#	print "Content-type: text/html\n\n";
#	print &build_page('cod_orderstobefulfilled_zones.html');
#}

sub cod_orderstofulfillstart_bypreorders{
# --------------------------------------------------------
# Forms Involved: 
# Created on: 02/11/09 16:08:26
# Author: Carlos Haas
# Description :   
# Parameters :
	my ($selectv)=@_;
	$va{'matches'} = 1;
	$va{'pageslist'} = 1;
	my $sth=&Do_SQL("$selectv");
	$va{'matches'} = $sth->rows;
	if ($va{'matches'}>0){
		(!$in{'nh'}) and ($in{'nh'}=1);
		$first = ($in{'nh'} - 1) * $usr{'pref_maxh'};			
		($va{'pageslist'},$qs) = &pages_list($in{'nh'},"/cgi-bin/mod/$usr{'application'}/admin",$va{'matches'},$usr{'pref_maxh'});
		my $page_limit;
		if ($in{'print'}){
			$page_limit = '';
		}else{
			$page_limit = " LIMIT $first,$usr{'pref_maxh'}";
		}		
		my (@c) = split(/,/,$cfg{'srcolors'});
		my $sth=&Do_SQL("$selectv $page_limit");
		$va{'searchresults'}="";
		while(my $rec=$sth->fetchrow_hashref){
			my $onwarehouse = "";
			my $onbatch 	= "";
			$d = 1 - $d;
			my $choices	= &load_choices($rec->{'ID_products'});
			$onwarehouse = "---";
			$onwarehouse = &load_name('sl_warehouses','ID_warehouses',$rec->{'ID_warehouses'},'Name') if($rec->{'ID_warehouses'}ne"NULL" and $rec->{'ID_warehouses'}ne"");
			$onbatch     = $rec->{'ID_warehouses_batches'} if($rec->{'ON_BATCH'}ne"NULL" and $rec->{'ON_BATCH'}ne"");
			$sbatch     = $rec->{'bStatus'} if($rec->{'ON_BATCH'}ne"NULL" and $rec->{'ON_BATCH'}ne"");
			$va{'searchresults'} .= "<tr bgcolor='$c[$d]' onmouseover='m_over(this)' onmouseout='m_out(this)'>\n";
			$va{'searchresults'} .= "  <td class='smalltext' valign='top' align='center'>
							<input type='checkbox' name='id_ordersttia' class='id_ordersttia' value='$rec->{'ID_orders'}' class='checkbox'>
							$rec->{'ID_orders'}</td>";
			$va{'searchresults'} .= "  <td class='smalltext' valign='top'>".&load_name('sl_zones','ID_zones',$rec->{'ID_zones'},'Name')."</td>\n";							
			$va{'searchresults'} .= "  <td class='smalltext' valign='top'>$rec->{'Date'}</td>\n";			
			$va{'searchresults'} .= "  <td class='smalltext' valign='top'>($rec->{'shp_Zip'}) $rec->{'shp_City'},$rec->{'shp_State'}</td>\n";
			$va{'searchresults'} .= "  <td class='smalltext' valign='top'>".$onwarehouse."</td>\n";
			$va{'searchresults'} .= "  <td class='smalltext' valign='top'>".$onbatch."</td>\n";
			$va{'searchresults'} .= "  <td class='smalltext' valign='top'>".$sbatch."</td>\n";
			$va{'searchresults'} .= "</tr>\n";
		}
	}else{
		$va{'pageslist'} = 1;
		$va{'searchresults'} = qq|
		<tr>
			<td colspan='6' align="center">|.&trans_txt('search_nomatches').qq|</td>
		</tr>\n|;
	}
}

sub cod_in_transit{
# --------------------------------------------------------
# Forms Involved: 
# Created on: 02/20/09 13:01:03
# Author: MCC C. Gabriel Varela S.
# Description :   
# Parameters :
# Last Modified on: 03/19/09 12:48:25
# Last Modified by: MCC C. Gabriel Varela S: Se toma en cuenta codshptype y se pone condici�n and sl_orders.Status='Processed'

## - - - - - - - - - - - - - - - - - - - AD/01092014/ Se cancela rutina por detectar que esta tirando el sistema
	print "Content-type: text/html\n\n";
	print &build_page('unauth.html');
	
	&auth_logging('usuario_con_malas_intenciones_detectado',1);
	return;
## - - - - - - - - - - - - - - - - - - - 

  my $selectvbw;

  $selectvbw="_SELECT NItems,Tobepaid,1 as gball2,sl_orders_products.ID_products,sl_orders_products.ID_orders,( select sum(if(Type='COD',1,0)) from sl_orders_payments where sl_orders_payments.id_orders = sl_orders.ID_orders) PaymentsCOD,( select sum(if(Type!='COD',1,0)) from sl_orders_payments where sl_orders_payments.id_orders = sl_orders.ID_orders) PaymentsNotCOD,sl_orders.Date,sl_orders.shp_Country,sl_orders.shp_Zip,sl_orders.shp_City,sl_orders.shp_State,sl_orders.ID_warehouses,sl_orders.Country
from sl_orders_products
inner join sl_orders on(sl_orders_products.ID_orders=sl_orders.ID_orders)

inner join (SELECT ID_orders,sum(if(isset!='Y',1,0))+if(not isnull(parts),parts,0) as NItems,Isset
            from sl_orders_products 
            inner join sl_skus on (sl_orders_products.ID_products=sl_skus.ID_sku_products)
            left join (SELECT ID_sku_products,count(ID_skus_parts)as parts from sl_skus_parts group by ID_sku_products)as tampa on (sl_orders_products.ID_products=tampa.ID_sku_products)
            where sl_orders_products.Status='Active'
            and sl_orders_products.SalePrice>0
            and sl_orders_products.Quantity>0
            and sl_orders_products.ID_products not like '6%'
            group by ID_orders)as tempor on(tempor.ID_orders=sl_orders.ID_orders)
where (ID_products not like '6%' 
and not(isnull(ShpDate) or ShpDate='0000-00-00' or ShpDate='') 
and not(isnull(Tracking) or Tracking='')
and not(isnull(ShpProvider) or ShpProvider='')
and shp_type=$cfg{'codshptype'})
and sl_orders.Status='Processed'
and Ptype='COD'
/*and StatusPrd='In Fulfillment'*/
and sl_orders_products.Status='Active'
and sl_orders_products.SalePrice>0
and sl_orders_products.Quantity>0
and sl_orders.Status not in ('Shipped','Void', 'Cancelled','System Error')";
	
  $gb="group by sl_orders_products.ID_orders";
	$query.=" and not(isnull(ID_warehouses) or ID_warehouses=0) ";
	$selectvbw.=" $querycount $query $gb";
	$va{'matches'} = 1;
	$va{'pageslist'} = 1;
	
	my $sth=&Do_SQL("SELECT SUM(togb)
				FROM(
					SELECT 1 as togb,Name,sl_warehouses_coverages.ID_warehouses,sum(if(sl_warehouses_coverages.ID_warehouses=tempo2.ID_warehouses,1,0))as NPreorders,group_concat(if(sl_warehouses_coverages.ID_warehouses=tempo2.ID_warehouses,ID_orders,NULL))as cadorders
					FROM sl_warehouses_coverages
					INNER JOIN sl_warehouses on (sl_warehouses_coverages.ID_warehouses=sl_warehouses.ID_warehouses)
					INNER JOIN ($selectvbw)as tempo2 on (1=tempo2.gball2)
					WHERE Covered='Covered'
					AND sl_warehouses.Status='Active'
					AND Type IN ('Virtual','Outsource')
					GROUP BY sl_warehouses_coverages.ID_warehouses
				)as tempo
			GROUP BY togb");

	($va{'matches'}) = $sth->fetchrow;
	if ($va{'matches'}>0){
		(!$in{'nh'}) and ($in{'nh'}=1);
		$first = ($in{'nh'} - 1) * $usr{'pref_maxh'};			
		($va{'pageslist'},$qs) = &pages_list($in{'nh'},"/cgi-bin/mod/$usr{'application'}/admin",$va{'matches'},$usr{'pref_maxh'});
		my $page_limit;
		if ($in{'print'}){
			$page_limit = '';
		}else{
			$page_limit = " LIMIT $first,$usr{'pref_maxh'}";
		}		
		my (@c) = split(/,/,$cfg{'srcolors'});
		
		my $sth=&Do_SQL("SELECT 1 as togb,Name,sl_warehouses_coverages.ID_warehouses,sum(if(sl_warehouses_coverages.ID_warehouses=tempo2.ID_warehouses,1,0))as NPreorders,group_concat(if(sl_warehouses_coverages.ID_warehouses=tempo2.ID_warehouses,ID_orders,NULL))as cadorders,sum(if(sl_warehouses_coverages.ID_warehouses=tempo2.ID_warehouses,Tobepaid,0))as NMoney,sum(if(sl_warehouses_coverages.ID_warehouses=tempo2.ID_warehouses,NItems,0))as NItems
				FROM sl_warehouses_coverages
				INNER JOIN sl_warehouses on (sl_warehouses_coverages.ID_warehouses=sl_warehouses.ID_warehouses)
				INNER JOIN ($selectvbw)as tempo2 on (1=tempo2.gball2)
				WHERE Covered='Covered'
				AND sl_warehouses.Status='Active'
				AND Type='Virtual'
				GROUP BY sl_warehouses_coverages.ID_warehouses $page_limit");

		$va{'searchresults'}="";
		while(my $rec=$sth->fetchrow_hashref){
			$d = 1 - $d;
			$va{'searchresults'} .= "<tr bgcolor='$c[$d]' onmouseover='m_over(this)' onmouseout='m_out(this)' >\n";
			$va{'searchresults'} .= "  <td class='smalltext' valign='top' align='center'>$rec->{'ID_warehouses'}</td>";
			$va{'searchresults'} .= "  <td class='smalltext' valign='top'>$rec->{'Name'}</td>\n";
			$va{'searchresults'} .= "  <td class='smalltext' valign='top'>$rec->{'NPreorders'}</td>\n";
			$va{'searchresults'} .= "  <td class='smalltext' valign='top'>$rec->{'NItems'}</td>\n";
			$va{'searchresults'} .= "  <td class='smalltext' valign='top' align='right'>".format_price($rec->{'NMoney'})."</td>\n";
			$va{'searchresults'} .= "</tr>\n";
		}
	}else{
		$va{'pageslist'} = 1;
		$va{'searchresults'} = qq|
		<tr>
			<td colspan='7' align="center">|.&trans_txt('search_nomatches').qq|</td>
		</tr>\n|;
	}

	(!$in{'page'}) and ($in{'page'} = 'home');
	if ($in{'print'}){
		print "Content-type: text/html\n\n";
		print &build_page('header_print.html');
		print &build_page('cod_orders_in_transit_print.html');
	}else{
		print "Content-type: text/html\n\n";
		print &build_page('cod_orders_in_transit.html');
	}
}


sub cod_in_transit_by_orders{
# --------------------------------------------------------
# Forms Involved: 
# Created on: 03/09/09 16:41:42
# Author: MCC C. Gabriel Varela S.
# Description :   
# Parameters :
# Last Modified on: 03/16/09 16:31:48
# Last Modified by: MCC C. Gabriel Varela S: Se pone else para cuando no encuentra resultados.
# Last Modified on: 03/19/09 12:49:23
# Last Modified by: MCC C. Gabriel Varela S: Se toma en cuenta codshptype

	## - - - - - - - - - - - - - - - - - - - AD/01092014/ Se cancela rutina por detectar que esta tirando el sistema
	print "Content-type: text/html\n\n";
	print &build_page('unauth.html');

	&auth_logging('usuario_con_malas_intenciones_detectado',1);
	return;
	## - - - - - - - - - - - - - - - - - - - 

	$va{'matches'} = 1;
	$va{'pageslist'} = 1;
	my $cadinn = " INNER JOIN (
				SELECT ID_orders,Status
				FROM sl_orders 
				WHERE Ptype='COD'
				AND ID_warehouses > 0
				AND Status='Processed'
				AND shp_type=$cfg{'codshptype'})as sl_orders
			  ON sl_orders.ID_orders = sl_orders_datecod.ID_orders ";
	
	my $sth=&Do_SQL("SELECT count(sl_orders.ID_orders)
			FROM `sl_orders_datecod`
			$cadinn
			WHERE sl_orders_datecod.Status='Active';");
	($va{'matches'}) = $sth->fetchrow;
	if ($va{'matches'}>0){
		(!$in{'nh'}) and ($in{'nh'}=1);
		$first = ($in{'nh'} - 1) * $usr{'pref_maxh'};			
		($va{'pageslist'},$qs) = &pages_list($in{'nh'},"/cgi-bin/mod/$usr{'application'}/admin",$va{'matches'},$usr{'pref_maxh'});
		my $page_limit;
		if ($in{'print'}){
			$page_limit = '';
		}else{
			$page_limit = " LIMIT $first,$usr{'pref_maxh'}";
		}		
		my (@c) = split(/,/,$cfg{'srcolors'});
		
		my $sth=&Do_SQL("SELECT sl_orders.ID_orders,sl_orders_datecod.ID_warehouses,sl_orders.Status,sl_orders_datecod.DateCOD  
				FROM `sl_orders_datecod` 
				$cadinn
				WHERE sl_orders_datecod.Status='Active'
				$page_limit;");
	
		$va{'searchresults'}="";
		while(my $rec=$sth->fetchrow_hashref){
			$d = 1 - $d;
			$va{'searchresults'} .= "<tr bgcolor='$c[$d]' onmouseover='m_over(this)' onmouseout='m_out(this)' >\n";
			$va{'searchresults'} .= "  <td class='smalltext' valign='top' align='center'>$rec->{'ID_orders'}</td>";
			$va{'searchresults'} .= "  <td class='smalltext' valign='top'>$rec->{'DateCOD'}</td>\n";
			$va{'searchresults'} .= "  <td class='smalltext' valign='top'>".&load_name('sl_warehouses','ID_warehouses',$rec->{'ID_warehouses'},'Name')." </td>\n";
			$va{'searchresults'} .= "  <td class='smalltext' valign='top'>$rec->{'Status'}</td>\n";
			$va{'searchresults'} .= "</tr>\n";
		}
	}else{
		$va{'pageslist'} = 1;
		$va{'searchresults'} = qq|
		<tr>
			<td colspan='7' align="center">|.&trans_txt('search_nomatches').qq|</td>
		</tr>\n|;
	}
	
	if ($in{'print'}){
		print "Content-type: text/html\n\n";
		print &build_page('header_print.html');
		print &build_page('cod_orders_in_transit_by_orders_print.html');
	}else{
		print "Content-type: text/html\n\n";
		print &build_page('cod_orders_in_transit_by_orders.html');
	}
}

sub cod_in_transit_by_items{
	# --------------------------------------------------------
	# Forms Involved: 
	# Created on: 03/09/09 17:20:13
	# Author: MCC C. Gabriel Varela S.
	# Description :   
	# Parameters :
	# Last Modified on: 03/10/09 13:11:47
# Last Modified by: MCC C. Gabriel Varela S: Se da formato a vista por items
# Last Modified on: 03/16/09 16:30:53
# Last Modified by: MCC C. Gabriel Varela S: Se pone else para cuando no encuentra resultados.
# Last Modified on: 03/19/09 12:49:56
# Last Modified by: MCC C. Gabriel Varela S: Se toma en cuenta codshptype

## - - - - - - - - - - - - - - - - - - - AD/01092014/ Se cancela rutina por detectar que esta tirando el sistema
	print "Content-type: text/html\n\n";
	print &build_page('unauth.html');

	&auth_logging('usuario_con_malas_intenciones_detectado',1);
	return;
## - - - - - - - - - - - - - - - - - - - 

	$va{'matches'} = 1;
	$va{'pageslist'} = 1;
	my $cadinn = " INNER JOIN sl_orders_datecod ON sl_orders.ID_orders = sl_orders_datecod.ID_orders ";
	
	
	my $sth=&Do_SQL("SELECT count(sl_orders_products.ID_products)
			FROM sl_orders_products
			INNER JOIN sl_skus ON ( sl_orders_products.ID_products = sl_skus.ID_sku_products ) 
			LEFT JOIN (
				SELECT ID_sku_products, ID_parts
				FROM sl_skus_parts) AS tampa ON ( sl_orders_products.ID_products = tampa.ID_sku_products ) 
			INNER JOIN sl_orders ON ( sl_orders_products.ID_orders = sl_orders.ID_orders )
			$cadinn 
			WHERE sl_orders_products.Status = 'Active'
			AND sl_orders_products.SalePrice >0
			AND sl_orders_products.Quantity >0
			AND sl_orders_products.ID_products NOT LIKE '6%'
			AND Ptype='COD'
			AND sl_orders.Status = 'Processed'
			AND sl_orders_datecod.Status = 'Active'
			AND shp_type =$cfg{'codshptype'}; ");
	($va{'matches'}) = $sth->fetchrow;
	if ($va{'matches'}>0)
	{
		(!$in{'nh'}) and ($in{'nh'}=1);
		$first = ($in{'nh'} - 1) * $usr{'pref_maxh'};			
		($va{'pageslist'},$qs) = &pages_list($in{'nh'},"/cgi-bin/mod/$usr{'application'}/admin",$va{'matches'},$usr{'pref_maxh'});
		my $page_limit;
		if ($in{'print'}){
			$page_limit = '';
		}else{
			$page_limit = " LIMIT $first,$usr{'pref_maxh'}";
		}		
		my (@c) = split(/,/,$cfg{'srcolors'});
		
		my $sth=&Do_SQL("SELECT if(Isset='Y',400000000+ID_parts,sl_orders_products.ID_products)as ID_items,sl_orders_datecod.DateCOD,sl_orders.ID_warehouses,Isset
				FROM sl_orders_products
				INNER JOIN sl_skus ON ( sl_orders_products.ID_products = sl_skus.ID_sku_products ) 
				LEFT JOIN (
					SELECT ID_sku_products, ID_parts
					FROM sl_skus_parts) AS tampa ON ( sl_orders_products.ID_products = tampa.ID_sku_products ) 
				INNER JOIN sl_orders ON ( sl_orders_products.ID_orders = sl_orders.ID_orders ) 
				$cadinn 
				WHERE sl_orders_products.Status = 'Active'
				AND sl_orders_products.SalePrice >0
				AND sl_orders_products.Quantity >0
				AND sl_orders_products.ID_products NOT LIKE '6%'
				AND Ptype='COD'
				AND sl_orders.Status = 'Processed'
				AND sl_orders_datecod.Status = 'Active'
				AND shp_type =$cfg{'codshptype'} $page_limit");
	
		$va{'searchresults'}="";
		my $cadnamemodel;
		$cadnamemodel="";
		while(my $rec=$sth->fetchrow_hashref)
		{
			$d = 1 - $d;
			if($rec->{'Isset'}eq'Y')
			{
				$cadnamemodel=&load_db_names('sl_parts','ID_parts',substr($rec->{'ID_items'},5,4),"[Model]<br>[Name]");
			}
			else
			{
				$cadnamemodel=&load_db_names('sl_products','ID_products',substr($rec->{'ID_items'},3,6),"[Model]<br>[Name]");
			}
			$va{'searchresults'} .= "<tr bgcolor='$c[$d]' onmouseover='m_over(this)' onmouseout='m_out(this)' >\n";
			$va{'searchresults'} .= "  <td class='smalltext' valign='top'>".&format_sltvid($rec->{'ID_items'})."</td>";
			$va{'searchresults'} .= "  <td class='smalltext' valign='top'>$cadnamemodel</td>";
			$va{'searchresults'} .= "  <td class='smalltext' valign='top'>$rec->{'DateCOD'}</td>\n";
			$va{'searchresults'} .= "  <td class='smalltext' valign='top'>".&load_name('sl_warehouses','ID_warehouses',$rec->{'ID_warehouses'},'Name')." </td>\n";
			$va{'searchresults'} .= "</tr>\n";
		}
	}
	else
	{
		$va{'pageslist'} = 1;
		$va{'searchresults'} = qq|
		<tr>
			<td colspan='7' align="center">|.&trans_txt('search_nomatches').qq|</td>
		</tr>\n|;
	}
	
	if ($in{'print'}){
		print "Content-type: text/html\n\n";
		print &build_page('header_print.html');
		print &build_page('cod_orders_in_transit_by_items_print.html');
	}else{
		print "Content-type: text/html\n\n";
		print &build_page('cod_orders_in_transit_by_items.html');
	}
}

sub cod_confirmation_list_add{
#-----------------------------------------
# Created on: 06/29/09  17:20:48 By  Roberto Barcenas
# Forms Involved: 
# Description : Asigna a lista de confirmacion una orden COD
# Parameters : 
	
	my ($id_warehouses,$orders) = @_;
	my @list = split(/,/,$orders);
	
	for my $i(0..$#list){
		$users = load_name('sl_warehouses','ID_warehouses',$id_warehouses,'codlist');
		$users = $cfg{'cod_list'} if $users eq 'N/A';
		@userlist = split(/,/,$users);
		for my $j(0..$#list){
			&write_to_list('COD Confirmations','orders',$userlist[$j],0,$list[$i],'sl_orders');
		}
	}
}

sub cod_confirmation_list_delete{
#-----------------------------------------
# Created on: 06/29/09  17:36:10 By  Roberto Barcenas
# Forms Involved: 
# Description : Eliminara los registros de una lista si se ha desasignado la orden
# Parameters : 

	my ($orders) = @_;
	$sth=&Do_SQL("DELETE FROM sl_lists WHERE Name='COD Confirmations' AND ID_table IN($orders);");
}

#############################################################################
#############################################################################
#   Function: cod_wreceipt
#
#       Es: Get default location in warehouses
#       En: 
#
#
#    Created on: 2015-02-25
#
#    Author: Jose Ramirez Garcia
#
#    Modifications:
#
#	 18/03/2015 ISC Alejandro Diaz se optimiza funcion con transacciones MySQL y se sustituye "warehouse_transfers"-> "transfer_warehouses"
#
#    Parameters:
#
#      - $id_warehouses, $id_products
#      
#
#    Returns:
#
#      - None
#
#    See Also:
#
# Last Modified on: 03/05/09 15:54:18
# Last Modified by: MCC C. Gabriel Varela S: Se corrige consulta mal hecha que actualizaba todas las preorders.
# Last Modification by JRG : 03/12/2009 : Se agrega log
# Last Modified on: 04/08/09 12:25:12
# Last Modified by: MCC C. Gabriel Varela S: Se manda llamar a la funcion transfer_warehouses
# Last Modified on: 04/09/09 13:34:02
# Last Modified by: MCC C. Gabriel Varela S: Se continua.
# Last Modified on: 04/15/09 12:37:02
# Last Modified by: MCC C. Gabriel Varela S: Se corrige funcionamiento para items que son sets.
# Last Modified on: 05/13/09 16:53:38
# Last Modified by: MCC C. Gabriel Varela S: Se cambia SL por variable de sistema
# Last Modified on: 05/26/09 12:19:39
# Last Modified by: MCC C. Gabriel Varela S: Se modifica para mostrar los items recibidos1.
# Last Modified RB: 07/24/09  16:21:32 -- Al cancelar se inactiva el registro de sl_orders_datecod y se guarda la fecha de la cancelacion
# Last Modified on: 09/16/09 12:40:20
# Last Modified by: MCC C. Gabriel Varela S: Se habilita cookie multi compania
# Last Time Modified By RB on 07/12/2010 : Se agrega verificacion de warehouse virtual 
# Last Time Modified By RB on 07/12/2010 : Se agrega verificacion de warehouse virtual 
sub cod_wreceipt {
#############################################################################
#############################################################################
	my ($status, $statmsg);

	if ($in{'action'}){
		my ($log);

		#$va{'message'} = 'Temporary Unavailable';
		print "Set-Cookie: ck_warehouses$in{'e'}=$in{'id_warehouses'} ; expires=; path=/;\n";
		my $id_orders;
		if (!$in{'id_warehouses'} or !$in{'shpdate'} or !$in{'tracking'} or !$in{'to_location'} or !$in{'from_wh'}){

			$va{'message'} = &trans_txt('reqfields');
			++$err;

		}else{

			$log .= "in{'id_warehouses'}=".$in{'id_warehouses'}."<br>\n";
			$log .= "in{'to_location'}=".$in{'to_location'}."<br>\n";
			$log .= "in{'tracking'}=".$in{'tracking'}."<br>\n";
			$log .= "in{'shpdate'}=".$in{'shpdate'}."<br>\n";
			$log .= "in{'from_wh'}=".$in{'from_wh'}."<br>\n";
			$log .= "cfg{'prefixentershipment'}=".$cfg{'prefixentershipment'}."<br>\n\n";

			my ($upcs_str,@ary);
			$sumshipp =	0;

			@ary = split(/\n|\s/,$in{'tracking'});
			
			$log .= "Lines tracking:<br>\n";
			my %upcs_list;
			for (0..$#ary){

				$ary[$_] =~ s/\n|\r|\s//g;

				# Clean line
				$log .= "ary[".$_."]=".$ary[$_]."<br>\n";


				if ($ary[$_] =~ /^$cfg{'prefixentershipment'}(\d+)/i and !$id_orders){

					$id_orders = $1;
					$ary[$_] = '';
					$sql = "SELECT COUNT(*) FROM sl_orders WHERE ID_orders='$id_orders' AND Status = 'Processed';";
					$log .= $sql."<br>\n";

					my ($sth) = &Do_SQL($sql);
					if ($sth->fetchrow == 0){
						$id_orders = 0;
						last;
					}
				}elsif($ary[$_] ne ''){
					if(exists($upcs_list{$ary[$_]}) ){
						$upcs_list{$ary[$_]}++;
					}else{
						$upcs_list{$ary[$_]} = 1;
					}
					$upcs_str .= '|'.$ary[$_].'|';
					$log .= "$ary[$_]<br>\n";
					$sumshipp++;
				}
			}
			$log .= "Total Lines: ".$sumshipp."<br>\n\n";

			my $upcs_str1=$upcs_str;

			if (!$id_orders){
				$va{'message'} .= "<li>Invalid, Missing/Unknow/ COD Order OR Order Already Processed </li>";
			}else{

				

			
				$sql = "SELECT ID_sku_products,ShpDate,UPC,IsSet FROM sl_orders_products,sl_skus WHERE sl_orders_products.ID_products=sl_skus.ID_sku_products AND ID_orders='$id_orders' AND LEFT(sl_orders_products.ID_products,1)<= 4 and sl_orders_products.status not in('Inactive') AND ShpDate IS NOT NULL AND ShpDate !='' AND ShpDate !='0000-00-00';";
				$log .= $sql."<br>\n";
				my ($sth) = &Do_SQL($sql);
				while (($id,$shpdate,$upc,$isset) = $sth->fetchrow_array) {	

					if ($isset eq 'Y') {

						$sql = "SELECT UPC,Qty,ID_parts FROM sl_skus,sl_skus_parts WHERE sl_skus_parts.ID_sku_products=$id AND sl_skus.ID_sku_products=400000000+ID_parts;";
						$log .= $sql."<br>\n";my ($sth2) = &Do_SQL($sql);
						while (($upc,$qtyupc,$id) = $sth2->fetchrow_array){
							$log .= "upc=$upc<br>\n";
							$log .= "qtyupc=$qtyupc<br>\n";
							$log .= "id=$id<br>\n";
							
							for(1..$qtyupc){
								if ($upcs_str !~ s/$upc// and $upc){
									my ($varx) = s/$upc//;
									$log .= "$upcs_str !~ $varx and $upc<br>";
									$va{'message'} .= "Missing UPC : $upc<br>";
									$log .= "Missing UPC : $upc<br>";
								}
							}
						}
					
					}else{
						
						if ($upcs_str !~ s/$upc// and $upc){
							$va{'message'} .= "Missing UPC : $upc<br>";
							$log .= "Missing UPC : $upc<br>";
						}

					}

				}
				

			}

			$upcs_str =~ s/\|\|/ /g;

			if ($upcs_str=~/\S+/g){
				$upcs_str =~ s/\|//g; $upcs_str =~ s/^,|,$//g;
				$va{'message'} .= "<li>Unknown UPC code(s):$upcs_str</li>";
			}


			my ($sthw)	= &Do_SQL("SELECT ID_warehouses FROM sl_orders_datecod WHERE ID_orders = '$id_orders' AND Status= 'Active' ORDER BY ID_orders_datecod DESC LIMIT 1;");
			my ($from_wh) = $sthw->fetchrow();
		 	$from_wh = &load_name('sl_orders','ID_orders',$id_orders,'ID_warehouses') if !$from_wh;
			

			if ($from_wh ne $in{'from_wh'}){

				########
				######## Buscamos por ultimo la nota de salida para determinar con que mensajeria salio
				########
				my ($sthn) = &Do_SQL("SELECT Notes FROM sl_orders_notes
									INNER JOIN
									(
										SELECT ID_orders, sl_orders_parts.Date AS sd
										FROM `sl_orders_products` 
										INNER JOIN sl_orders_parts
										USING(ID_orders_products)
										WHERE ID_orders = '$id_orders' LIMIT 1
									)tmp USING(ID_orders)
									WHERE ID_orders = '$id_orders'
									AND Date = sd AND Notes LIKE 'COD Order Shipped%';");
				my ($shpnote) = $sthn->fetchrow();

				if($shpnote){

					my @aryn = split(/Assigned to: /, $shpnote);
					my $this_wh = &load_name('sl_warehouses','Name',$aryn[1],'ID_warehouses');
					($this_wh) and ($from_wh = $this_wh);

				}

			}

			if ($from_wh ne $in{'from_wh'}){			

					my ($original_whname) = &load_name('sl_warehouses', 'ID_warehouses', $from_wh, 'Name');
					my ($new_whname) = &load_name('sl_warehouses', 'ID_warehouses', $in{'from_wh'}, 'Name');

					if ($id_orders and !$from_wh){
						$va{'message'} .= "<li>Looks like Order COD Warehouse Missed</li>";
					}

					$va{'message'} .= "<li>Driver doesn't match. Order was originally assigned to $original_whname not $new_whname</li>";
					# &send_text_mail("rbarcenas\@inovaus.com","rbarcenas\@inovaus.com","Invalid Source Warehouse [COD Receipt]","Tracking: $in{'tracking'} \r\n  Original Warehouse: $original_whname($idwh_assigned)\r\n Trying with: $new_whname($in{'id_warehouses'})");
			}

			#####
			##### Conteo de Partes escaneadas vs partes devueltas
			##### 
			my ($sthp) = &Do_SQL("SELECT COUNT(*) FROM sl_orders_products INNER JOIN sl_orders_parts USING(ID_orders_products) WHERE ID_orders = '$id_orders';");
			my ($tshipp) = $sthp->fetchrow();

			if ( abs($sumshipp - $tshipp) > 0 ){
				$va{'message'} .= "<li>".&trans_txt('scan_cod_receipt_count_notmatch') . " $sumshipp vs $tshipp</li>";
			}

			if ($tshipp == 0){
				$va{'message'} .= "<li>".&trans_txt('scan_cod_receipt_notsent') ."</li>";
			}

			if ($va{'message'}){
				$va{'error'} = 'ERROR';
				$va{'message'} = "<br>$va{'message'}";
				&Do_SQL("INSERT INTO sl_debug (cmd, id, log, Date, Time, ID_admin_users) VALUES ('cod_wreceipt', '$id_orders', '".&filter_values($va{'message'})."\n\n\n".&filter_values($log)."', CURDATE(), CURTIME(), '$usr{'id_admin_users'}');");
			}else{
				## Move Inventory
				$upcs_str1=~s/^\||\|$//g;
				my @upcst=split(/\|\|/,$upcs_str1);
				my $movinv=0,$transferstatus=0;
				my $failedupcs="";

				if(!&transaction_validate($in{'cmd'}, $id_orders, 'check')){
    				my $id_transaction = &transaction_validate($in{'cmd'},  $id_orders, 'insert');
				}else{
		            $va{'error'} = 'ERROR';
		            $va{'message'} = &trans_txt('transaction_duplicate');
		            return;
		        }
				#
				# INICIA TRANSACCION
				#
				&Do_SQL("START TRANSACTION;");
				$log .= "START TRANSACTION<br>\n\n";
				# print "Content-type: text/html\n\n";
				# use Data::Dumper;
				# print '<pre>';
				# print Dumper \%upcs_list;
				# exit;
				while( my($upc,$qty) = each %upcs_list ){
					my $isset = &load_name('sl_skus', 'UPC', $upc, 'IsSet');
					my $id_products = &load_name('sl_skus', 'UPC', $upc, 'ID_sku_products');
					my ($status_transfer, $message) = &warehouse_transfers($from_wh, 0, $in{'id_warehouses'}, $in{'to_location'}, $id_products, $qty, $id_orders, 'sl_orders', "", "", "", 0);
					$log .= qq|warehouse_transfers($from_wh, 0, $in{'id_warehouses'}, $in{'to_location'}, $id_products, 1, $id_orders, 'sl_orders', "", "", "", 0)|."<br>\n";
					$log .= "status_transfer=".$status_transfer."<br>\n";
					$log .= "message=".$message."<br>\n\n";
					if ($status_transfer !~ /ok/i){
						$failedupcs .= "$from_wh -> $upcst[$_] [$id_products] x 1<br>";
					}
				}
				if ($failedupcs ne ""){
					
					$va{'message'} = "Return inventory process failed because of the upcs:<br> $failedupcs";
					&Do_SQL("ROLLBACK");
					$log .= "ROLLBACK<br>\n";

					&Do_SQL("INSERT INTO sl_debug (cmd, id, log, Date, Time, ID_admin_users) VALUES ('cod_wreceipt', '$id_orders', '".$va{'message'}."\n\n\n".&filter_values($log)."', CURDATE(), CURTIME(), '$usr{'id_admin_users'}');");

				}else{

					$sql = "UPDATE sl_orders SET Status='Cancelled' WHERE ID_orders='$id_orders';";
					$log .= $sql."<br>\n";
					&Do_SQL($sql);
					
					$sql = "UPDATE sl_orders_datecod SET Status='Inactive',DateCancelled=CURDATE() WHERE ID_orders='$id_orders' AND Status='Active';";
					$log .= $sql."<br>\n";
					&Do_SQL($sql);
					
					$sql = "UPDATE sl_orders_products SET Cost='0' WHERE ID_orders = '$id_orders';";
					$log .= $sql."<br>\n";
					&Do_SQL($sql);

					$sql = "UPDATE sl_warehouses_batches_orders INNER JOIN sl_orders_products USING(ID_orders_products) SET sl_warehouses_batches_orders.Status = 'Returned' WHERE ID_orders = '$id_orders';";
					$log .= $sql."<br>\n";
					&Do_SQL($sql);

					$in{'db'} = 'sl_orders';
					&auth_logging('opr_orders_stCancelled',$id_orders);
					$log .= qq|auth_logging('opr_orders_stCancelled',$id_orders)|."<br>\n";

					&status_logging($id_orders,'Cancelled');
					$log .= qq|status_logging($id_orders,'Cancelled')|."<br>\n";

					$sql = "INSERT INTO sl_orders_notes SET ID_orders='$id_orders', Notes='Order Cancelled\nCOD failed to deliver the merchandise\n\n".&filter_values($in{'note'})."', Type='High',Date=Curdate(),Time=CURTIME(),ID_admin_users='$usr{'id_admin_users'}';";
					&add_order_notes_by_type($id_orders,"Order Cancelled\nCOD failed to deliver the merchandise\n\n".&filter_values($in{'note'}),"High");
					$log .= $sql."<br>\n"; 
					#my ($sth) = &Do_SQL($sql);

					$va{'message'} .= "<span class='bigerrtext'>".($#upcst+1)." pieces entered.</span>";
					
					my $id_warehouses_batches = &warehouses_batches_by_order($id_orders);
					&Do_SQL("INSERT INTO sl_entershipments (ID_orders, ID_warehouses_batches, Type, Input, Output, Status, Date, Time, ID_admin_users) VALUES ('$id_orders', '$id_warehouses_batches', 'cod return', '".&filter_values($in{'tracking'})."', 'DEVOLUCION COD $cfg{'prefixentershipment'}$id_orders', 'ok', CURDATE(), CURTIME(), '$usr{'id_admin_users'}');");
					
					delete($in{'tracking'});
					delete($in{'note'});

					&Do_SQL("COMMIT");
					# &Do_SQL("ROLLBACK"); # Debug only
					$log .= "COMMIT<br>\n";
				}
				&transaction_validate($in{'cmd'}, $id_orders, 'delete');
			}
		}

		### Return Dropship / Outsource
		if($in{'fc_dropshipp_return'}){
			return;
		}	
		
	}else{		
		$in{'shpdate'} = &get_sql_date(0);
		(!$in{'id_warehouses'}) and ($in{'id_warehouses'} = &GetCookies("ck_warehouses$in{'e'}"));
	}

		
	## Extraemos los Warehouses Virtuales de la DB
	my ($sth) = &Do_SQL("SELECT ID_warehouses,Name FROM sl_warehouses WHERE Type IN ('Virtual','Outsource') AND Status='Active' ORDER BY Name;");
	while(my($idw,$wname) = $sth->fetchrow()){

		if($in{'idw'} eq 	$idw){
			$va{'warehouses_list'} .= qq| <a href='/cgi-bin/mod/$usr{'application'}/admin?cmd=cod_wreceipt&idw=$idw' class="menu">$wname</a>|; 
		}else{
			$va{'warehouses_list'} .= qq| <a href='/cgi-bin/mod/$usr{'application'}/admin?cmd=cod_wreceipt&idw=$idw' class="menu">$wname</a>|; 
		}
	}
	
	my $flagw = 'on';
	($in{'idw'}) and ($flagw = 'off');
					
	$va{'warehouses_list'} .= qq| <a href='/cgi-bin/mod/$usr{'application'}/admin?cmd=cod_wreceipt' class="menu">Cualquier Chofer</a>|; 					
	
	if ($in{'idw'}){			
			&cod_wreceipt_bywarehouse;			
	}else{
			$va{'namew'} = 'Cualquier Chofer';
			($in{'from_wh'} and !$in{'action'}) and ($va{'message'}) = "Orden asignada a: ".&load_name('sl_warehouses','ID_warehouses',$in{'from_wh'},"Name");
			print "Content-type: text/html\n\n";
			$va{'page_title'} = trans_txt("pageadmin");
			print &build_page('cod_wreceipt.html');	
	}

}


sub cod_wreceipt_bywarehouse{
# --------------------------------------------------------
# Created  By  RB on  06/14/2010: 
# Description : Muestra las ordenes que estan ligadas al chofer 
# Forms Involved: cod_wreceipt_bywarehouse.html , cod_wreceipt.html
# Parameters :  $in{'idw'}
# Last Modified By  - - on: 

		$usr{'pref_maxh'} = 10;

		my ($sth) = &Do_SQL("SELECT sl_orders.ID_orders,COUNT(*) AS PartSent 
					FROM sl_orders_products 
					INNER JOIN sl_orders ON sl_orders.ID_orders = sl_orders_products.ID_orders
					INNER JOIN sl_orders_parts ON sl_orders_products.ID_orders_products = sl_orders_parts.ID_orders_products
					WHERE ID_warehouses = '$in{'idw'}' AND sl_orders.Status = 'Processed'
					GROUP BY sl_orders.ID_orders;");

		my $total = $sth->rows();
		
		if($total > 0 ){
				$va{'matches'} = $total;
				my (@c) = split(/,/,$cfg{'srcolors'});
				(!$in{'nh'}) and ($in{'nh'}=1);
				$first = ($in{'nh'} - 1) * $usr{'pref_maxh'};			
				($va{'pageslist'},$qs) = &pages_list($in{'nh'},"/cgi-bin/mod/$usr{'application'}/admin",$va{'matches'},$usr{'pref_maxh'});
	
				my ($sth) = &Do_SQL("SELECT sl_orders.ID_orders,CONCAT(FirstName,' ',LastName1) AS customer, shp_State,shp_City,shp_Zip,GROUP_CONCAT(ID_parts)
							FROM sl_orders
							INNER JOIN sl_customers ON sl_orders.ID_customers = sl_customers.ID_customers 
							INNER JOIN sl_orders_products ON sl_orders.ID_orders = sl_orders_products.ID_orders
							INNER JOIN sl_orders_parts ON sl_orders_products.ID_orders_products = sl_orders_parts.ID_orders_products
							WHERE ID_warehouses = '$in{'idw'}' AND sl_orders.Status = 'Processed'
							GROUP BY sl_orders.ID_orders LIMIT $first,$usr{'pref_maxh'};");
				
				while(my($id_orders,$customer,$state,$city,$zipcode,$idparts) = $sth->fetchrow()){ 
							$d = 1 - $d;
							my @parts = split(/,/,$idparts);
							my $txtparts="";
							for(0..$#parts){
								$txtparts .= &load_name('sl_parts','ID_parts',$parts[$_],"Name") . " (" . (400000000 + $parts[$_]) . ")<br>";
							}

							$va{'searchresults'} .= qq|<tr bgcolor='$c[$d]'>
										        <td class='smalltext' valign='top'>
											        <input name="tracking" value="|. $cfg{'prefixentershipment'} . $id_orders .qq|" class="radio" type="radio">&nbsp;&nbsp;
											        $id_orders
										        </td>
										        <td class='smalltext' valign='top' align='center'>$customer</td>
										        <td class='smalltext' valign='top' align='left'>$state<br>$city,$zipcode</td>
										        <td class='smalltext' valign='top' align='left'>$txtparts</td>
									        </tr>|;
				}
		}else{
			$va{'matches'} = 0;
			$va{'pageslist'} =1;
			$va{'searchresults'} = qq|<tr bgcolor='$c[$d]'><td class='smalltext' valign='top' colspan="4" align="center">|.&trans_txt('search_nomatches').qq|</td></tr>|;
		}		
		$va{'id_warehouses'} = &load_name('sl_warehouses','Name','LA Main',"IF(Status='Active',ID_warehouses,0)");
		$va{'namew'} = &load_name('sl_warehouses','ID_warehouses',$in{'idw'},"Name") if ($in{'idw'});

		print "Content-type: text/html\n\n";
		print &build_page('cod_wreceipt_bywarehouse.html');
}


sub cod_orderstobatch {
# --------------------------------------------------------
# Created  By PH on  06/14/2010: 
# Description : Asigna ordenes COD a la remesa activa del chofer 
# Forms Involved: 
# Parameters :
# Last Modified By  - - on: 
 
	if ($in{'action'}){
		if($in{'id_warehouses'}){
			
			$va{'id_warehouses_batches'}='';
			my $new = $in{'id_warehouses'};
			$va{'id_warehouses_batches'} = &create_warehouse_batch_file($new);
			if($va{'id_warehouses_batches'}){		
			
			####COD by warehouse
			my $status_warehouses_batches = 0;
			my $query= "SELECT sl_orders_products.ID_orders
						FROM sl_orders_products
						INNER JOIN sl_orders on(sl_orders_products.ID_orders=sl_orders.ID_orders)
						INNER JOIN (
							SELECT sl_orders_payments.ID_orders,sum(if(Type='COD',1,0))as PaymentsCOD,sum(if(Type!='COD',1,0))as PaymentsNotCOD
						        FROM sl_orders_payments
						        GROUP BY sl_orders_payments.ID_orders
							having PaymentsCOD>0
						         )as tempo on (tempo.ID_orders=sl_orders.ID_orders)
						LEFT JOIN  sl_warehouses_batches_orders
							ON sl_warehouses_batches_orders.ID_orders_products = sl_orders_products.ID_orders_products 
							AND sl_warehouses_batches_orders.Status IN ('In Fulfillment','Shipped','In Transit')  
						WHERE sl_warehouses_batches_orders.ID_orders_products IS NULL
						AND sl_orders_products.ID_products not like '6%' 
						and (isnull(ShpDate) or ShpDate='0000-00-00' or ShpDate='') 
						and (isnull(Tracking) or Tracking='')
						and (isnull(ShpProvider) or ShpProvider='') 
						and shp_type=3
						and sl_orders.Status='Processed'
						and Ptype='COD' 
						and StatusPrd='In Fulfillment'
						and sl_orders_products.Status='Active'
						and sl_orders_products.SalePrice>0
						and sl_orders_products.Quantity>0
						and sl_orders.Status not in ('Shipped','Void', 'Cancelled','System Error')   
						and sl_orders.ID_warehouses = '$in{'id_warehouses'}'
						group by sl_orders_products.ID_orders
						";
					 
			my ($sth) = &Do_SQL($query);
		    if ($sth->rows>0){	
				my $sth = &Do_SQL($query);
				while ($rec = $sth->fetchrow_hashref){
					### Insert Remesas Orders 
					my $Query = "SELECT ID_orders_products FROM sl_orders_products 
								WHERE ID_orders = $rec->{'ID_orders'} 
								AND Status IN ('Active','Exchange','Undeliverable','ReShip') 
								AND SalePrice >= 0;";
					my ($sth_op) = &Do_SQL($Query);
					my $a = 0;

					while ($rec_op = $sth_op->fetchrow_hashref){

						$Query = "SELECT COUNT(*) FROM sl_warehouses_batches_orders WHERE ID_orders_products = $rec_op->{'ID_orders_products'} AND Status IN('In Fulfillment','Shipped','In Transit');";
						($sth2) = &Do_SQL($Query);
						($count)=$sth2->fetchrow_array();
						
						if($count == 0 ) { 

							++$a;
							my $Query = "INSERT INTO sl_warehouses_batches_orders SET ID_warehouses_batches=".$va{'id_warehouses_batches'}.", ID_orders_products=".int($rec_op->{'ID_orders_products'}).", Status='In Fulfillment', Date=CURDATE(),Time=CURTIME(),ID_admin_users='$usr{'id_admin_users'}'; ";
							($sth3) = &Do_SQL($Query);

						}					

					} 

					if($a){

						## Nota y Log para orden asignada
						$in{'db'} = 'sl_orders';
						## Nota orden enviada en batch		
						#my ($sth) = &Do_SQL("INSERT INTO sl_orders_notes SET Notes='".&trans_txt('order_batchadded')." $va{'id_warehouses_batches'} ',Type='High',Date=CURDATE(),Time=CURTIME(),ID_admin_users='$usr{'id_admin_users'}', ID_orders = '$rec->{'ID_orders'}';");
						&add_order_notes_by_type($rec->{'ID_orders'},&trans_txt('order_batchadded')." $va{'id_warehouses_batches'}","High");
						
						&auth_logging('order_batchadded', $rec->{'ID_orders'});

						my $Query = "UPDATE sl_warehouses_batches SET Status='Assigned' WHERE ID_warehouses_batches=$va{'id_warehouses_batches'};";
						my ($sth) = &Do_SQL($Query);

					}

				} 

				delete($in{'export'});
				delete($in{'action'});
				delete($in{'id_warehouses'});
				$in{'wareho'}=1;
				$va{'message'}=&trans_txt("warehouses_batches_assigned").": $va{'id_warehouses_batches'}".' <a href="/cgi-bin/mod/'.$usr{'application'}.'/dbman?cmd=warehouses_batches&view='.$va{'id_warehouses_batches'}.'">View batch</a>';
				&cod_orderstobefulfilled();
			}else{
								
				delete($in{'export'});
				delete($in{'action'});
				delete($in{'id_warehouses'});
				$in{'wareho'}=1;
				&cod_orderstobefulfilled();
			}
			}			
		}
	}	 
}

sub cod_orderstobefulfilled_zones {
# --------------------------------------------------------	
# Created on: Carlos Haas
# Last Modified on: 7/30/2013 12:13:41 PM
# Author: Unknown
# Description : 
# Parameters :
	$in{'id_zones'}=int($in{'id_zones'});

	if ($in{'id_zones'}>0){
		&cod_orderstobefulfilled_zones_to_batch;
		return;
	}

	$va{'matches'} = 1;
	$va{'pageslist'} = 1;
	
	my ($sth) = &Do_SQL("SELECT COUNT(*) FROM sl_orders 
			    INNER JOIN sl_orders_products on(sl_orders.ID_orders=sl_orders_products.ID_orders )
			    LEFT JOIN  sl_warehouses_batches_orders
					ON sl_warehouses_batches_orders.ID_orders_products = sl_orders_products.ID_orders_products 
					AND sl_warehouses_batches_orders.Status IN ('In Fulfillment','Shipped','In Transit')  
			    WHERE sl_warehouses_batches_orders.ID_orders_products IS NULL
						AND Ptype = 'COD'
						AND sl_orders.Status IN ('Processed','Shipped')
						AND StatusPrd='In Fulfillment'
				AND sl_orders_products.Status IN ('Active','Exchange','Undeliverable','ReShip') 
				AND sl_orders_products.SalePrice >= 0
				GROUP BY ID_zones");
	$va{'matches'} = $sth->fetchrow;
	
	if ($va{'matches'}>0){

		my (@c) = split(/,/,$cfg{'srcolors'});
		my ($sth) = &Do_SQL("SELECT 
								SUM(SumNet) AS TotNet
								, COUNT(DISTINCT tmp.ID_orders)AS TotZone
								, SUM(Express_Delivery)AS Express_Delivery
								, COUNT(DISTINCT ID_orders_products) AS TotQty
								, tmp.ID_zones
								, Name
							FROM(
								SELECT 
									sl_orders.ID_orders
									, SUM(IF(sl_orders.shp_type = 2,1,0))AS Express_Delivery
									, sl_orders_products.ID_orders_products
									, (Saleprice - sl_orders_products.Discount) AS SumNet
									, ID_zones
								FROM /*sl_orders_payments 
								INNER JOIN */ sl_orders /*USING(ID_orders)*/
								INNER JOIN sl_orders_products USING(ID_orders)
								LEFT JOIN sl_products on(sl_products.ID_products=RIGHT(sl_orders_products.ID_products,6)) 
							    LEFT JOIN sl_parts ON(sl_parts.ID_parts=RIGHT(sl_orders_products.ID_products,4)) 
								LEFT JOIN  sl_warehouses_batches_orders
									ON sl_warehouses_batches_orders.ID_orders_products = sl_orders_products.ID_orders_products 
									AND sl_warehouses_batches_orders.Status IN ('In Fulfillment','Shipped','In Transit')  
								WHERE sl_warehouses_batches_orders.ID_orders_products IS NULL
								AND Ptype = 'COD'
								AND sl_orders.Status IN ('Processed','Shipped')
								AND StatusPrd='In Fulfillment' 
								AND sl_orders_products.Status IN ('Active','Exchange','Undeliverable','ReShip') 
								AND sl_orders_products.SalePrice >= 0
								AND sl_orders_products.ID_products BETWEEN 100000000 AND 399999999
								GROUP BY sl_orders_products.ID_orders_products
								ORDER BY sl_orders.ID_orders DESC 
							) AS tmp
							LEFT JOIN sl_zones ON tmp.ID_zones=sl_zones.ID_zones
							WHERE 1
							GROUP BY ID_zones");

		while (my $rec = $sth->fetchrow_hashref){

			$d = 1 - $d;
			my $ed = $rec->{'Express_Delivery'}? qq|<img src="/sitimages/delivery_2_on.jpg" title="Express Delivery">| : '';

			$va{'searchresults'} .= "<tr bgcolor='$c[$d]' onmouseover='m_over(this)' onmouseout='m_out(this)' >\n";
			$va{'searchresults'} .= "  <td class='smalltext' valign='top' align='center'><a href='#' onClick=\"trjump('/cgi-bin/mod/wms/admin?cmd=cod_orderstobefulfilled&zones=1&id_zones=$rec->{'ID_zones'}')\"><img src='[va_imgurl]/[ur_pref_style]/icsearchsmall.gif' title='Next' alt='' border='0'></a></td>\n";
			$va{'searchresults'} .= "  <td class='smalltext' valign='top' align='center'><a href='#' onClick=\"trjump('/cgi-bin/mod/wms/dbman?cmd=opr_zones&view=$rec->{'ID_zones'}')\">$rec->{'ID_zones'}</a></td>\n";
			$va{'searchresults'} .= "  <td class='smalltext' valign='top'><a href='#' onClick=\"trjump('/cgi-bin/mod/wms/admin?cmd=cod_orderstobefulfilled&zones=1&id_zones=$rec->{'ID_zones'}')\">$rec->{'Name'} &nbsp; $ed</a></td>\n";
			$va{'searchresults'} .= "  <td class='smalltext' valign='top' align='right'>".&format_number($rec->{'TotZone'})."</td>\n";
			$va{'searchresults'} .= "  <td class='smalltext' valign='top' align='right'>".&format_price($rec->{'TotNet'})."</td>\n";
			$va{'searchresults'} .= "  <td class='smalltext' valign='top' align='right'>".&format_number($rec->{'TotQty'})."</td>\n";
			$va{'searchresults'} .= "</tr>\n";
		}
	}else{
		$va{'pageslist'} = 1;
		$va{'searchresults'} = qq|
		<tr>
			<td colspan='3' align="center">|.&trans_txt('search_nomatches').qq|</td>
		</tr>\n|;
	}

	print "Content-type: text/html\n\n";
	print &build_page('cod_orderstobefulfilled_zones.html');
}

sub cod_orderstobefulfilled_zones_to_batch {
# --------------------------------------------------------

	if ($in{'action'}){

		if ($in{'id_warehouses'} and $in{'id_orders'}){

			delete($va{'message'}); delete($va{'message_zip_excluded'});
			my ($id_batch) = &create_warehouse_batch_file($in{'id_warehouses'});
			my ($sth) = &Do_SQL("UPDATE sl_warehouses_batches SET Status='Assigned' WHERE ID_warehouses=$in{'id_warehouses'} AND Status = 'New'");


			# my ($sth) = &Do_SQL("SELECT ID_warehouses_batches FROM sl_warehouses_batches WHERE ID_warehouses=$in{'id_warehouses'} AND Status IN ('New','Assigned')");
			# my ($id_batch) = $sth->fetchrow;
			
			# if (!$id_batch){
			# 	my ($sth) = &Do_SQL("INSERT INTO sl_warehouses_batches SET ID_warehouses=$in{'id_warehouses'}, Status='Assigned', Date = CURDATE(), Time = CURTIME(), ID_admin_users = '$usr{'id_admin_users'}';");
			# 	$id_batch = $sth->{'mysql_insertid'};
			# }else{
			# 	my ($sth) = &Do_SQL("UPDATE sl_warehouses_batches SET Status='Assigned' WHERE ID_warehouses=$in{'id_warehouses'} AND Status = 'New'");
			# }
			$in{'id_orders'} =~ s/\|/,/g;
			
			## Excluded Zips
			my ($excluded_zips, $mod_excluded_zip, $orders_excluded);
			my ($sth) = &Do_SQL("SELECT ZipCode FROM sl_warehouses_zipcodes_excludes WHERE ID_warehouses=$in{'id_warehouses'} AND Status='Active';");
			while (my $zip = $sth->fetchrow){
				#$excluded_zips = $zip . ",";
				$excluded_zips = ";" . $zip . ";";
			}
			#chop($excluded_zips);
			#$mod_excluded_zip = "AND shp_Zip NOT IN ($excluded_zips)" if ($excluded_zips);
			
			my $this_order = 0; my $x = 0;
			my ($sth) = &Do_SQL("SELECT 
									sl_orders_products.ID_orders_products
									, sl_orders.ID_orders
									, shp_Zip
								FROM sl_orders 
								INNER JOIN sl_orders_products on(sl_orders.ID_orders=sl_orders_products.ID_orders )
								LEFT JOIN sl_products on(sl_products.ID_products=RIGHT(sl_orders_products.ID_products,6)) 
								LEFT JOIN sl_warehouses_batches_orders
									ON sl_warehouses_batches_orders.ID_orders_products = sl_orders_products.ID_orders_products 
									AND sl_warehouses_batches_orders.Status IN ('In Fulfillment','Shipped','In Transit')  
								WHERE sl_warehouses_batches_orders.ID_orders_products IS NULL
								AND Ptype = 'COD'
								AND sl_orders_products.ID_products BETWEEN 100000000 AND 399999999
								AND sl_orders.Status IN ('Processed','Shipped')
								AND StatusPrd='In Fulfillment' 
								AND sl_orders_products.Status IN ('Active','Exchange','Undeliverable','ReShip') 
								AND sl_orders_products.SalePrice >= 0
								$mod_excluded_zip 
								AND sl_orders.ID_orders IN ($in{'id_orders'})
								AND ID_zones = '$in{'id_zones'}' 
								ORDER BY sl_orders.ID_orders;");
			EZ:while (my ($idp,$ido, $zip) = $sth->fetchrow){

				if($excluded_zips and $orders_excluded !~ /$ido/ and $excluded_zips =~ /;$zip;/){

					##
					## Zip Excluded in Warehouse
					##
					$va{'message_zip_excluded'} .= qq|$ido<br>|;
					$orders_excluded .= qq|;$ido;|;
					next EZ;

				}

				my ($sth2) = &Do_SQL("REPLACE INTO sl_warehouses_batches_orders 
									SET ID_warehouses_batches = '$id_batch', ID_orders_products = '$idp', Status = 'In Fulfillment', 
									Date = CURDATE(), Time = CURTIME(), ID_admin_users = '$usr{'id_admin_users'}';");
				($ido ne $this_order) and ( $x += 1) and ($this_order = $ido);

			}
			$va{'message'} = &trans_txt('order_batchadded') . ": $id_batch x $x";
			($excluded_zips) and ($va{'message'} .= qq|<br><br>|. &trans_txt('order_batch_zip_excluded') . qq| ( $excluded_zips ): <br>|. $va{'message_zip_excluded'});

		}else{
			$va{'messages'} = &trans_txt('tobatch_err');
		}
	}

	$va{'zonename'} = &load_name('sl_zones','ID_zones',$in{'id_zones'},'Name');

	my ($sth) = &Do_SQL("SELECT COUNT(*) FROM sl_zones_warehouses INNER JOIN sl_warehouses ON sl_zones_warehouses.ID_warehouses=sl_warehouses.ID_warehouses AND sl_warehouses.Status='Active' WHERE ID_zones = '$in{'id_zones'}';");
	if ($sth->fetchrow>0){
		my (@c) = split(/,/,$cfg{'srcolors'});
		#############################
		### List of Warehouse
		#############################
		my ($sth) = &Do_SQL("SELECT * FROM sl_zones_warehouses
		INNER JOIN sl_warehouses ON sl_zones_warehouses.ID_warehouses=sl_warehouses.ID_warehouses AND sl_warehouses.Status='Active'
		WHERE ID_zones='$in{'id_zones'}';");
		while (my $rec = $sth->fetchrow_hashref){
			$d = 1 - $d;


			#####
			##### Ordenes en Remesa Actual
			#####
			my ($sthw) = &Do_SQL("SELECT COUNT(DISTINCT sl_orders.ID_orders)
						   FROM sl_orders 
						   INNER JOIN sl_orders_products
						  USING(ID_orders)
						   INNER JOIN sl_warehouses_batches_orders
						  USING(ID_orders_products)
						   INNER JOIN sl_warehouses_batches
						   USING(ID_warehouses_batches)
						  WHERE
						   sl_warehouses_batches.ID_warehouses=$rec->{'ID_warehouses'}
						   AND sl_warehouses_batches.Status IN ('New','Assigned')");
			my ($this_warehouse_batch) = $sthw->fetchrow();

			my $query = "SELECT
							sl_warehouses_batches.ID_warehouses
							, COUNT(*) AS Tot_intransit
							, SUM(OrderNet) AS Amt_intransit
							, SUM(Qty_intransit) AS Qty_intransit
						FROM 
						(
							SELECT
								sl_warehouses_batches.ID_warehouses
								, ID_orders
								, COUNT(*) AS Qty_intransit
							FROM 
								sl_warehouses_batches_orders  
								INNER JOIN sl_warehouses_batches USING(ID_warehouses_batches)
								INNER JOIN sl_zones_warehouses USING(ID_warehouses)
								INNER JOIN sl_orders_products USING(ID_orders_products)
							WHERE	
								sl_zones_warehouses.ID_zones = '". $in{'id_zones'} ."'
								AND sl_warehouses_batches.Status IN ('Processed','In Transit')
								AND sl_warehouses_batches_orders.Status = 'In Transit'
								AND sl_warehouses_batches.ID_warehouses = '". $rec->{'ID_warehouses'} ."'
							GROUP BY 
								sl_warehouses_batches.ID_warehouses, ID_orders
							ORDER BY	
								sl_warehouses_batches.ID_warehouses, ID_orders
						)sl_warehouses_batches
						INNER JOIN sl_orders USING(ID_orders);";
			#my ($sth2) = &Do_SQL($query);

			# my ($sth2) = &Do_SQL("SELECT SUM(IF(sl_warehouses_batches_orders.Status='In Transit',1,0)) AS Tot_intransit,
			# 							SUM(IF(sl_warehouses_batches_orders.Status='In Transit',OrderNet,0)) AS Amt_intransit,
			# 							SUM(IF(sl_warehouses_batches_orders.Status='In Transit',OrderQty,0)) AS Qty_intransit 
			# 							FROM sl_warehouses_batches_orders 
			# 			LEFT JOIN sl_warehouses_batches ON sl_warehouses_batches.ID_warehouses_batches=sl_warehouses_batches_orders.ID_warehouses_batches
			# 			LEFT JOIN sl_orders_products ON sl_warehouses_batches_orders.ID_orders_products=sl_orders_products.ID_orders_products
			# 			LEFT JOIN sl_orders ON sl_orders_products.ID_orders=sl_orders.ID_orders
			# 			WHERE sl_warehouses_batches.ID_warehouses=$rec->{'ID_warehouses'}");
			#$rec_tot = $sth2->fetchrow_hashref();

			$va{'searchresults'} .= "<tr bgcolor='$c[$d]' onmouseover='m_over(this)' onmouseout='m_out(this)'>\n";
			$va{'searchresults'} .= "  <td class='smalltext' valign='top' align='center'><input type='radio' class='radio' name='id_warehouses' value='$rec->{'ID_warehouses'}'</td>\n";
			$va{'searchresults'} .= "  <td class='smalltext' valign='top' align='center'><a href='#' onClick=\"trjump('/cgi-bin/mod/wms/dbman?cmd=opr_warehouses&view=$rec->{'ID_warehouses'}')\">$rec->{'ID_warehouses'}</a></td>\n";
			$va{'searchresults'} .= "  <td class='smalltext' valign='top'>$rec->{'Name'}</td>\n";
			$va{'searchresults'} .= "  <td class='smalltext' valign='top' align='right'>".&format_number($this_warehouse_batch)."</td>\n";
			# $va{'searchresults'} .= "  <td class='smalltext' valign='top' align='right'>".&format_number($rec_tot->{'Tot_intransit'})."</td>\n";
			# $va{'searchresults'} .= "  <td class='smalltext' valign='top' align='right'>".&format_price($rec_tot->{'Amt_intransit'})."</td>\n";
			# $va{'searchresults'} .= "  <td class='smalltext' valign='top' align='right'>".&format_number($rec_tot->{'Qty_intransit'})."</td>\n";
			$va{'searchresults'} .= "</tr>\n";
		}
		#############################
		### List of Orders
		#############################
		my ($modquery, $modquery2);
		($in{'from_date'}) and ($modquery .= "AND sl_orders.Date >= '$in{'from_date'}' ");
		($in{'to_date'}) and ($modquery .= "AND sl_orders.Date <= '$in{'to_date'}' ");
		($in{'sid_products'} ne '---' and $in{'sid_products'} ne '') and ($modquery .= "AND sl_orders_products.ID_products = '$in{'sid_products'}' ");
		($in{'shp_city'} ne '---' and $in{'shp_city'} ne '') and ($modquery .= "AND shp_City = '$in{'shp_city'}' ");
		($in{'shp_type'}) and ($modquery .= "AND shp_type = '$in{'shp_type'}' ");
		if($in{'from_amount'}){ $in{'from_amount'} =~ s/\$|,//g; $modquery2 .= "HAVING TotProd >= '$in{'from_amount'}' "; }
		if($in{'to_amount'}){ 
			$in{'to_amount'} =~ s/\$|,//g;
			$modquery2 .= ($in{'from_amount'})? "AND TotProd <= '$in{'to_amount'}' " : "HAVING TotProd <= '$in{'to_amount'}' "; 
		}

		my ($sth) = &Do_SQL("SELECT 
								sl_orders.ID_orders
								, sl_orders.Date
								, SUM(SalePrice*Quantity) AS TotProd
								, SUM(Quantity) AS TotItems
								, ID_customers
								, IF(shp_type = 2,1,0) AS Express_Delivery
								, shp_Zip
								, shp_City
								, shp_Urbanization
								, shp_State
							FROM sl_orders 
							INNER JOIN sl_orders_products USING(ID_orders)
							LEFT JOIN sl_products on(sl_products.ID_products=RIGHT(sl_orders_products.ID_products,6)) 
							LEFT JOIN sl_warehouses_batches_orders
								ON sl_warehouses_batches_orders.ID_orders_products = sl_orders_products.ID_orders_products 
								AND sl_warehouses_batches_orders.Status IN ('In Fulfillment','Shipped','In Transit')  
							WHERE sl_warehouses_batches_orders.ID_orders_products IS NULL
							$modquery
							AND Ptype = 'COD'
							AND sl_orders_products.ID_products BETWEEN 100000000 AND 399999999
							AND sl_orders.Status IN ('Processed','Shipped')
							AND StatusPrd='In Fulfillment' 
							AND sl_orders_products.Status IN ('Active','Exchange','Undeliverable','ReShip') 
							AND sl_orders_products.SalePrice >= 0
							AND ID_zones = $in{'id_zones'}
							GROUP BY sl_orders.ID_orders
							$modquery2 
							ORDER BY shp_Zip,shp_City,shp_Urbanization,sl_orders.ID_orders DESC");
		$va{'matches'} = $sth->rows;
		
		if ($va{'matches'}>0){

			my ($ids,$cities);
			while ($rec = $sth->fetchrow_hashref){

				$d = 1 - $d;
				$cont = 0;
				my $ed = $rec->{'Express_Delivery'}	? qq|<img src="/sitimages/delivery_2_on.jpg" title="Express Delivery" width="">| : '';

				if($va{'filterby_city'} !~ /$rec->{'shp_City'}/){

					#####
					##### Used to filter by Product
					#####
					my $en = "$in{'shp_city'}" eq "$rec->{'shp_City'}" ? 'selected="selected"' : '';
					$va{'filterby_city'} .= qq|<option value="$rec->{'shp_City'}" $en>$rec->{'shp_City'}</option>\n|;

				}

				$va{'ordsearchresults'} .= "<tr bgcolor='$c[$d]' onmouseover='m_over(this)' onmouseout='m_out(this)'>\n";
				$va{'ordsearchresults'} .= "  <td class='smalltext' valign='top' align='center'><input type='checkbox' class='checkbox' id='chkor_$rec->{'ID_orders'}' name='id_orders' value='$rec->{'ID_orders'}' onclick='chk_ord($rec->{'ID_orders'})'>&nbsp;</td>\n";
				$va{'ordsearchresults'} .= "  <td class='smalltext' valign='top' align='center'><a href='#' onClick=\"trjump('/cgi-bin/mod/wms/dbman?cmd=opr_orders&view=$rec->{'ID_orders'}&check_status=1')\">$rec->{'ID_orders'}</a></td>\n";
				$va{'ordsearchresults'} .= "  <td class='smalltext' valign='top' align='center'> $ed </td>\n";
				$va{'ordsearchresults'} .= "  <td class='smalltext' valign='top'>$rec->{'shp_City'}<br>$rec->{'shp_Urbanization'}<br>$rec->{'shp_State'}</td>\n";
				$va{'ordsearchresults'} .= "  <td class='smalltext' valign='top'>$rec->{'Date'}</td>\n";
				$va{'ordsearchresults'} .= "  <td class='smalltext' valign='top'>".&load_db_names('sl_customers','ID_customers',$rec->{'ID_customers'},"[company_name] [FirstName] [LastName1]")."</td>\n";
				$va{'ordsearchresults'} .= "  <td class='smalltext' valign='top'>$rec->{'TotItems'}</td>\n";
				$va{'ordsearchresults'} .= "  <td class='smalltext' valign='top'>".&format_price($rec->{'TotProd'})."</td>\n";
				$va{'ordsearchresults'} .= "</tr>\n";

				$sth1=&Do_SQL("SELECT ID_orders,sl_orders_products.ID_products, Name, Model
							FROM sl_orders_products
							INNER JOIN sl_products ON RIGHT(sl_orders_products.ID_products,6) = sl_products.ID_products
							WHERE ID_orders = '$rec->{'ID_orders'}' AND sl_orders_products.status NOT IN('Inactive','Order Cancelled')");
				
				while($rec1=$sth1->fetchrow_hashref) {

					if($va{'filterby_ids'} !~ /$rec1->{'ID_products'}/){

						#####
						##### Used to filter by Product
						#####
						my $en = "$in{'sid_products'}" eq "$rec1->{'ID_products'}" ? 'selected="selected"' : '';
						$va{'filterby_ids'} .= qq|<option value="$rec1->{'ID_products'}" $en>$rec1->{'ID_products'} - $rec1->{'Name'}</option>\n|;

					}

					$va{'ordsearchresults'} .= "<tr bgcolor='$c[$d]'>\n";
					$va{'ordsearchresults'} .= "  <td class='smalltext' valign='top' colspan='3'></td>\n";
					$va{'ordsearchresults'} .= "  <td class='smalltext' valign='top'>".&format_sltvid($rec1->{'ID_products'})."</td>\n";
					$va{'ordsearchresults'} .= "  <td class='smalltext' valign='top' colspan='4'>$rec1->{'Name'}/$rec1->{'Model'}</td>\n";
					$va{'ordsearchresults'} .= "</tr>\n";

				}
				$va{'ordsearchresults'} .= "</tr>\n";

			}
	

		}else{
			$va{'pageslist'} = 1;
			$va{'ordsearchresults'} = qq|
			<tr>
				<td colspan='8' align="center">|.&trans_txt('search_nomatches').qq|</td>
			</tr>\n|;
		}
	}else{
		$va{'pageslist'} = 1;
		$va{'ordsearchresults'} = qq|
		<tr>
			<td colspan='8' align="center">|.&trans_txt('zones_notwarehouses').qq|</td>
		</tr>\n|;
	}

	print "Content-type: text/html\n\n";
	print &build_page('cod_orderstobefulfilled_zonesbatch.html');
}



1;
