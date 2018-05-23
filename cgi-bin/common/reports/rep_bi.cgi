#!/usr/bin/perl
##################################################################
#   REPORTS : BUSINESS INTELIGENCE
##################################################################

sub rep_bi_prodbyagent{
# --------------------------------------------------------
	## TODO: Parametrizar que no existan textos que no pasen por transtxt

	if($in{'action'}){
		my ($query_tot,$query_list);

		$in{'rtype'} = 'Orders'	if !$in{'rtype'} ;
		
		$prefix = 'orders';
		
		my @hours = ("00:00:00","00:31:00","01:01:00","01:31:00","02:01:00","02:31:00","03:01:00","03:31:00","04:01:00","04:31:00"
								,"05:01:00","05:31:00","06:01:00","06:31:00","07:01:00","07:31:00","08:01:00","08:31:00","09:01:00","09:31:00"
								,"10:01:00","10:31:00","11:01:00","11:31:00","12:01:00","12:31:00","13:01:00","13:31:00","14:01:00","14:31:00"
								,"15:01:00","15:31:00","16:01:00","16:31:00","17:01:00","17:31:00","18:01:00","18:31:00","19:01:00","19:31:00"
								,"20:01:00","20:31:00","21:01:00","21:31:00","22:01:00","22:31:00","23:01:00","23:31:00");
	

		$query ="WHERE sl_".$prefix."_products.Status = 'Active' ";
		
		
		## Filter by Date
		if ($in{'from_date'}){
			$va{'report_tbl'} .= "<tr><td width='100' class='smalltext'>From Date : </td><td class='smalltext'>$in{'from_date'}</td></tr>\n";
			$query .= " AND sl_".$prefix."_products.Date >= '$in{'from_date'}' ";
		}
		
		$in{'to_date'}	= &get_sql_date()	if !$in{'to_date'};
		if ($in{'to_date'}){
			$va{'report_tbl'} .= "<tr><td width='100' class='smalltext'>To Date : </td><td class='smalltext'>$in{'to_date'}</td></tr>\n";
			$query .= " AND sl_".$prefix."_products.Date <= '$in{'to_date'}' ";
		}
		
		## Filter by Admin User
		my $by_admin_user = '';
		if ($in{'id_admin_users'}){
			$in{'id_admin_users'} = int($in{'id_admin_users'});
			$by_admin_user = "WHERE ID_admin_users = $in{'id_admin_users'} ";
		}
		
		
		## Filter By Time
		$in{'time'} = int($in{'time'});
		if($in{'time'}){
			$query .= " AND Time >= '$hours[$in{'time'}-1]' AND Time < '$hours[$in{'time'}]' "	if $in{'time'} < 48;
			$query .= " AND Time BETWEEN '$hours[$in{'time'}]' AND '23:59:59' "	if $in{'time'} == 48;
		}
		
		## Filter by User Type
		if ($in{'user_type'}){
			$in{'user_type'} =~ s/\|/','/g;
			$va{'report_tbl'} .= "<tr><td width='100' class='smalltext'>By User : </td><td class='smalltext'>$in{'user_type'}</td></tr>\n";
			$query .= " AND 0 < (SELECT IF(user_type IN('$in{'user_type'}'),1,0) FROM admin_users WHERE ID_admin_users = sl_orders.ID_admin_users) ";
		}$in{'user_type'} =~ s/','/\|/g;
		
		
		##### SOrt By
		$in{'sortby'}	=	" Time "	if !$in{'sortby'};
		$in{'sortorder'}	=	'' if	!$in{'sortorder'};
		$sb = "ORDER BY $in{'sortby'} $in{'sortorder'}";
		
		$query = "FROM sl_".$prefix."_products LEFT JOIN 
				(
					SELECT ID_products AS IDProduct, Name AS ProductName
					FROM sl_products
				) AS tmpprod
				ON IDProduct = RIGHT( sl_".$prefix."_products.ID_products, 6 )
				LEFT JOIN
				(
					SELECT ID_services AS IDService, Name AS ServiceName
					FROM sl_services
				) AS tmpser
				ON IDService = RIGHT( sl_".$prefix."_products.ID_products, 4 )
				INNER JOIN
				(
					SELECT ID_admin_users AS IDAgent,CONCAT(LastName,',',FirstName) AS AgentName
					FROM admin_users $by_admin_user
				)AS tmpagent
				ON IDAgent = sl_".$prefix."_products.ID_admin_users
				$query ";
		
		
		$report_name = "Product ID / Half Hour";			
		$usr{'pref_maxh'} = 30;
		$query_tot  = "SELECT COUNT(*),SUM(SalePrice) $query";
		$query_list = "SELECT 
					IF( MINUTE( Time ) <=30, CONCAT( HOUR( Time ) , ':01 to ', HOUR( Time ) , ':30' ) , CONCAT( HOUR( Time ) , ':31 to ', HOUR( Time ) +1, ':00' ) ) AS RANGO ,
					IF(IDProduct IS NULL,IDService,IDProduct)AS IDProduct,
					IF(ProductName IS NULL,ServiceName,ProductName)AS ProductName,
					AgentName,
					COUNT(sl_".$prefix."_products.ID_products) AS Hits,
					SUM(SalePrice)AS SaleNet
					$query
					GROUP BY HOUR( Time ) , MINUTE( Time ) <=30, MINUTE( Time ) >30,IDAgent,IDProduct
					$sb";
		
		foreach $key (keys %in){
			$in{'qs'} .= "$key=$in{$key}&" unless ($key eq 'cmd');
		}
		
		my ($sth) = &Do_SQL($query_tot);
		my ($tot_cant,$tot_amount) = $sth->fetchrow_array();
		
		if ($tot_cant > 0 and  $tot_amount > 0){
			(!$in{'nh'}) and ($in{'nh'}=1);
			$first = ($in{'nh'} - 1) * $usr{'pref_maxh'};	
			my ($sth) = &Do_SQL($query_list);
			$va{'matches'} = $sth->rows;
			($va{'pageslist'},$qs) = &pages_list($in{'nh'},"/cgi-bin/mod/$usr{'application'}/admin",$va{'matches'},$usr{'pref_maxh'});
			if ($in{'print'}){
				$sth = &Do_SQL($query_list);
			}else{
				$sth = &Do_SQL($query_list ." LIMIT $first,$usr{'pref_maxh'}");
			}
			my (@c) = split(/,/,$cfg{'srcolors'});
			while (my ($range,$id_products,$pname,$agent,$hits,$amount) = $sth->fetchrow_array){
				$id_products = 600000000+$id_products	if length($id_products) < 6;
				$d = 1 - $d;
				$va{'searchresults'} .= qq|
								<tr bgcolor='$c[$d]'>
									<td align="left" class="smalltext" nowrap>$range</td>
									<td align="left" class="smalltext">(|.&format_sltvid($id_products).qq|) $pname</td>
									<td align="left" class="smalltext">$agent</td>
									<td align="right" class="smalltext">$hits</td>
									<td nowrap align="right" class="smalltext">|.&format_price($amount).qq|</td>
								</tr>\n|;

			}
			$va{'tot_cant'} = $tot_cant;
			$va{'tot_amount'} = &format_price($tot_amount);
			&auth_logging('report_view',1);

		}else{
			$va{'matches'} = 0;
			$va{'pageslist'} = 1;
			$va{'searchresults'} .= qq|<tr><td align="center" colspan="11">|.&trans_txt('search_nomatches').qq|</td></tr>|;
		}
		
		### Report Headet
		$va{'report_tbl'} = qq |
								<center>
									<table border="0" cellspacing="0" cellpadding="4" width="70%" class="formtable">
										<tr>
									   		 <td class="menu_bar_title" colspan="2">Report Name : $report_name</td>  
										</tr>
									 <tr>
								    	<td class="smalltext">Report Units</td>  
								    	<td class="smalltext">Products / Sale Price</td>  
									</tr>
								$va{'report_tbl'}
									<tr>
								   		 <td class="smalltext" colspan="2">Created by : ($usr{'id_admin_users'}) $usr{'firstname'} $usr{'lastname'} \@ |.&get_sql_date ." &nbsp;" . &get_time() .qq|</td>  
									</tr> 
								</table></center>|;
								
		$va{'totinfo'}	=	qq|<table border="0" cellspacing="0" cellpadding="2" width="40%" align="center" class="formtable">
									<tr>
										<td class="menu_bar_title" colspan="3" align="center">Totals</td>
									</tr>
									<tr>
										<td>Totals Count:</td>
										<td align="right">$va{'tot_cant'}</td>
										<td></td>
									</tr>
									<tr>
										<td>Total Amount:</td>
										<td align="right">$va{'tot_amount'}</td>
										<td align="right">(100 %)</td>
									</tr>
								</table>|;												
														
		&auth_logging('report_view','');
		if ($in{'print'}){
			print "Content-type: text/html\n\n";
			print &build_page('header_print.html');
			print &build_page('results_bi_prodbyagent_print.html');
		}else{
			print "Content-type: text/html\n\n";
			print &build_page('results_bi_prodbyagent.html');
		}
	}else{
		print "Content-type: text/html\n\n";
		print &build_page('rep_bi_prodbyagent.html');
	}
}

sub rep_bi_allorders {
#-----------------------------------------
# Created on: 08/04/09  15:28:39 By  Roberto Barcenas
# Forms Involved: 
# Description : Extrae la informacion de ordenes 
# Parameters :
# Last Modified by RB: Se habilita el filtrado por productos y la presentacion del reporte mostrando por linea orden o producto.
# Last Modified on: 08/27/09 13:20:40
# Last Modified by: MCC C. Gabriel Varela S: Se cambia ID_dids por DNIS en sl_orders/
# Last Modified by RB on: 03/22/10 15:59:40 : Se modifica query para no mostrar preordenes en Status Converted
# Last Modified by RB on: 03/31/10 12:05:40 : Se modifica query para mostrar Ordenes con Preorden Converted con fecha de la Preorden	
# Last Modified by RB on: 07/06/10 12:00:40 : Dos modificaciones. 1. Se cambia inner join con sl_zipcodes por left join. 2. Se modifica cuando es orden de exportacion para traer el ID_products desde el Products_Related 
# Last modified on 19 Jul 2010 11:46:41
# Last modified by: MCC C. Gabriel Varela S. :Se corrige la consulta que obtiene el id y el nombre del producto, haciendo que no tome en cuenta el relacionado si es un servicio
# Last modified on 27 Jul 2010 13:14:09
# Last modified by: MCC C. Gabriel Varela S. :Se hace que se tome el relacionado para ??rdenes de exportaci??n s??lo si comienza con 400
# Last Modified by RB on 08/23/2010 12:03:40: Se agrega el user_type 
# Last Modified by RB on 10/05/2010 11:47:40: Se agrega first_call 
# Last Modified by RB on 03/23/2011 13:10:05: Se agrega DMA_DESC	
# Last modified on 08/11/2012 18:00:00
# Last modified by: EP : Se tomo el nombre de la empresa para el nombre del archivo a generar
	my $log_query;
	if($in{'action'}){
		
		my ($query_list);
		my $maxprod=1;
		my $info_user =	'';
		my $info_pprod = '';
		my $info_oprod = '';
		my $info_time = '';
		my $strout = '';
		
		## Si type eq 'order' 1 linea por orden
		$maxprod = 10	if $in{'type'} eq 'order';
		
		###### Busqueda por rango de fecha de order
		if ($in{'from_date'} and $in{'to_date'}){
			$where_date = " AND sl_orders.Date BETWEEN '$in{'from_date'}' AND '$in{'to_date'}' ";
		}else{
			$where_date = "";
		}

		
		### Busqueda por rango de tiempo
		if($in{'from_time'} or $in{'to_time'}){
			$in{'from_time'} 	= "00:00:00"	if !$in{'from_time'};
			$in{'to_time'} 		= "23:59:59"	if !$in{'to_time'};
			$info_time = " AND Time BETWEEN '$in{'from_time'}' AND '$in{'to_time'}'";
		}

		###### Busqueda por rango de fecha de venta
		if ($in{'from_sales_date'} and $in{'to_sales_date'}){
			$where_posteddate = "WHERE PostedDate BETWEEN '$in{'from_sales_date'}' AND '$in{'to_sales_date'}'";
		}else{
			$where_posteddate = "";
		}
		
		### Si es busqueda por id_admin_user 
		$info_user = "WHERE ID_admin_users = ".int($in{'id_admin_users'})." "	if $in{'id_admin_users'};
		
		
		### Si es busqueda por id_products
		if($in{'id_products'}){			
			$info_oprod = " AND 0 < (SELECT COUNT(DISTINCT ID_orders) FROM sl_orders_products WHERE ID_orders = sl_orders.ID_orders AND RIGHT(ID_products,6) = '".int($in{'id_products'})."' AND Status = 'Active') ";
		}

		my $fname   = 'all_orders_'.$cfg{'app_title'}.'.csv';
		$fname =~ s/\s/_/g;
		
		my $strHeader = "Channel,TPago,DID,Orden,Status,Primer Llamada,Fecha,Hora,Fecha de Venta,Fecha de Factura,Fecha de Envio,Fecha de Ingreso,Estado,Municipio,CP,Id Zona,Nombre Zona,DMA";
		for(1..$maxprod){
				$strHeader .=",Cant$_,Cod$_,Prod$_,Cost$_,Prec$_,Desc$_,Tax$_,Envio$_,Tax Envio$_";
			}
		## Si type eq 'order' 1 linea por orden	
		$strHeader .= ",Total Cost,Total Products,Total Descuento,Total Taxes,Total Envio,Total Orden"	if $in{'type'} eq 'order';
		
		$strHeader .= ",Familia de Producto,Usuario,Grupo,Rush Shipping,ID Usuario,Usuario Direksys,CID,PHONE1,PHONE2,CELLPHONE";

		if($cfg{'use_admin_users_tree'} and $cfg{'use_admin_users_tree'}==1){
			$strHeader .= ",Supervisor,Coordinador";
		} 

		$strHeader .= ",Facturacion InovaClub";
		$strHeader .= ",ID Cliente";

		## Busqueda por consolas
		my $add_sql;
		if ($in{'id_salesorigins'}){
			my @arr_salesorigins = split /\|/ , $in{'id_salesorigins'};
			$add_sql .= " AND sl_orders.ID_salesorigins IN(". join(',', @arr_salesorigins) .")";
		}
		
		$query_list = "SELECT 
				   IDAgent,
				   AgentName,
				   IF(user_type IS NOT NULL AND user_type != '',user_type,'N/A') AS user_type,
				   IF(Orders IS NOT NULL,Orders,0)AS Orders,
				   ID_user,
				   UsernameDireksys
				FROM
				(
				   SELECT 
				      ID_admin_users AS IDAgent,
				      (CONCAT(UPPER(admin_users.FirstName),' ',UPPER(admin_users.MiddleName),' ',UPPER(admin_users.LastName))) AS AgentName,
				      user_type, admin_users.ID_admin_users as ID_user, admin_users.Username as UsernameDireksys
				   FROM admin_users $info_user
				)AS tmp_agent
				
				LEFT JOIN
				(
				   SELECT
				      ID_admin_users AS IDA,
				      COUNT(ID_Orders) AS Orders
				   FROM sl_orders
				      WHERE 1
				      $where_date
				      $info_time 

				      $info_oprod 

				      $add_sql

				      AND Status != 'System Error' 
				      GROUP BY ID_admin_users
				)AS tmp_order
				ON tmp_order.IDA = tmp_agent.IDAgent
				HAVING Orders > 0
				ORDER BY AgentName ";
		$log_query = $query_list . "\n\n ================================== \n\n";
		
		my ($sth) = &Do_SQL($query_list);
		if($sth->rows() > 0){

			print "Content-type: application/octetstream\n";
			print "Content-disposition: attachment; filename=$fname\n\n";
			print "$strHeader\r\n";
			
			while(my($idagent,$agentname,$user_type,$orders,$iduser_direksys,$user_direksys) = $sth->fetchrow()){

				if($in{'from_time'} or $in{'to_time'}) {
					$in{'from_time'} 	= "00:00:00"	if !$in{'from_time'};
					$in{'to_time'} 		= "23:59:59"	if !$in{'to_time'};
					$info_timep = " AND sl_orders.Time BETWEEN '$in{'from_time'}' AND '$in{'to_time'}'";
				}
				
				my $supervisor, $coordinador;

				# /* Se añade los datos del supervisor y del Coordinador */
				if ($cfg{'use_admin_users_tree'} and $cfg{'use_admin_users_tree'}==1 and $idagent and $idagent ne ''){
					$sql_sup = "SELECT
								(
									SELECT UPPER(CONCAT (Firstname,' ',LastName,' ',MiddleName))
									FROM admin_users
									WHERE ID_admin_users=cu_admin_users_tree.ID_admin_users2
								) supervisor, 
								(
									SELECT UPPER(CONCAT (Firstname,' ',LastName,' ',MiddleName))
									FROM admin_users
									WHERE ID_admin_users=cu_admin_users_tree.ID_admin_users3
								) coordinador
							FROM cu_admin_users_tree
							WHERE ID_admin_users = '$idagent';";
					$sth_sup = &Do_SQL($sql_sup);
					($supervisor, $coordinador) = $sth_sup->fetchrow();
				}


				# /*, IFNULL(CountyName,'N/A') AS County*/
				$query = "SELECT * FROM (
								SELECT DISTINCT ID_orders
									, IF(DNIS IS NULL,0,DNIS) AS DNIS
									, sl_orders.Date
									, sl_orders.Time
									, (shp_State)AS State, shp_City AS County
									, sl_orders.Status,Channel,IF(DMA_DESC IS NULL OR DMA_DESC = '','N/A',DMA_DESC) AS DMA_DESC, IF(shp_type = 2, 'Yes','No')AS Rush
									, sl_orders.shp_Zip, sl_orders.ID_zones, (SELECT Name FROM sl_zones WHERE sl_zones.ID_zones=sl_orders.ID_zones) as zone_name
									, if(sl_orders.Ptype<>'COD',(SELECT CapDate FROM sl_orders_payments WHERE sl_orders_payments.ID_orders=sl_orders.ID_orders AND Captured='Yes' LIMIT 1),sl_orders.PostedDate)PostedDate
									, (SELECT GROUP_CONCAT(DISTINCT ShpDate) FROM sl_orders_products  WHERE sl_orders_products.ID_orders=sl_orders.ID_orders AND ShpDate > '1900-01-01' GROUP BY ID_orders) as ShpDate
									, if(sl_orders.Ptype='COD',(SELECT CapDate FROM sl_orders_payments WHERE sl_orders_payments.ID_orders=sl_orders.ID_orders AND Captured='Yes' LIMIT 1),'')CapDate
									, (SELECT IF( COUNT(id_products)>0 , 1, 0) FROM sl_orders_products WHERE sl_orders_products.ID_orders=sl_orders.ID_orders AND id_products IN (600001005,600001035) )ClubInova
									, sl_orders.ID_customers
									, sl_orders.PType
									, sl_orders.first_call
								FROM sl_orders LEFT JOIN sl_zipcodes ON sl_orders.shp_Zip = sl_zipcodes.ZipCode
									LEFT JOIN sl_zipdma ON sl_zipdma.ZipCode = sl_zipcodes.ZipCode 
									LEFT join sl_salesorigins on (sl_orders.ID_salesorigins=sl_salesorigins.ID_salesorigins)
								WHERE sl_orders.ID_admin_users = $idagent 
									$info_oprod
									$add_sql 
									$query_converted 
									$where_date 
									$info_timep $nopreorder  
									AND sl_orders.Status NOT IN('System Error','Converted')
							)orders
							$where_posteddate
							ORDER BY Date,Status,Time,ID_orders";
				my $sth = &Do_SQL($query);
				#$log_query .= $query . "\n\n ================================== \n\n";
				                   
				while(my($id_orders,$id_dids,$date,$time_order,$state,$county,$status,$salesorigins,$dma_name,$rush_shipping,$shp_zip,$id_zones,$zone_name,$posteddate,$shpdate,$capdate,$clubinova,$id_customers,$tpago,$first_call) = $sth->fetchrow()){
					my $items=0;
					my $total = 0;
					my $tcost = 0;
					my $tdisc = 0;
					my $ttax = 0;
					my $tshp = 0;
					my $torder = 0;
					my $strprod = '';
					my $strout='';
					my $first_call = 'N/A';
					my $catname;
					$first_call = 'Unknown' if $first_call eq '';
					$tpago = 'Money Order'	if $tpago eq '';

					my $sth_cust = &Do_SQL("SELECT sl_customers.ID_customers
												, sl_customers.CID
												, sl_customers.Phone1
												, sl_customers.Phone2
												, sl_customers.Cellphone
											FROM sl_customers 
											WHERE sl_customers.ID_customers = ".$id_customers.";");
					my $customer = $sth_cust->fetchrow_hashref();
					my $cid = $customer->{'CID'};
					my $phone1 = $customer->{'Phone1'};
					my $phone2 = $customer->{'Phone2'};
					my $cellphone = $customer->{'Cellphone'};

					my $invoice = &Do_SQL("SELECT Date(cu_invoices.doc_date)doc_date
							FROM cu_invoices_lines
							INNER JOIN cu_invoices ON cu_invoices.ID_invoices=cu_invoices_lines.ID_invoices AND cu_invoices.Status='Certified' AND cu_invoices.invoice_type='ingreso'
							WHERE cu_invoices_lines.ID_orders=$id_orders
							ORDER BY cu_invoices.ID_invoices
							LIMIT 1");
					my ($date_invoice) = $invoice->fetchrow();			

					# Se ocultan datos temporalmente
					$state = &temp_hide_data($state);
					$county = &temp_hide_data($county);
					# $shp_zip = &temp_hide_data($shp_zip);

					## Si type eq 'order' 1 linea por order
					$strout .= qq|"$salesorigins","$tpago","$id_dids","$id_orders","$status","$first_call","$date","$time_order","$posteddate","$date_invoice","$shpdate","$capdate","$state","$county","$shp_zip","$id_zones","$zone_name","$dma_name"| if $in{'type'} eq 'order';
					$query = "SELECT IF(LEFT(sl_orders_products.ID_products,3) = 100 AND LENGTH(Related_ID_products) = 9 and left(Related_ID_products,3)=400,Related_ID_products,sl_orders_products.ID_products) AS ID_products,
						IF(sl_parts.Name IS NOT NULL,sl_parts.Name,IF(sl_services.Name IS NOT NULL,sl_services.Name,sl_products.Name)) AS Pname,
						Quantity,SalePrice,sl_orders_products.Discount,sl_orders_products.Tax,sl_orders_products.Shipping,sl_orders_products.ShpTax
						,IF(sl_orders_products.Cost > 0,sl_orders_products.Cost,IF(SLTV_NetCost >=0,SLTV_NetCost,0))AS SLTV_NetCost,
						Channel, ID_categories
					FROM sl_orders_products 
					INNER JOIN sl_orders on (sl_orders_products.ID_orders = sl_orders.ID_orders)
					LEFT JOIN sl_salesorigins on (sl_orders.ID_salesorigins=sl_salesorigins.ID_salesorigins)
					LEFT JOIN sl_products ON sl_products.ID_products = RIGHT(sl_orders_products.ID_products,6)
					LEFT JOIN sl_services ON sl_services.ID_services = RIGHT(sl_orders_products.ID_products,4)
					LEFT JOIN sl_parts ON (ID_parts = RIGHT(Related_ID_products,4) and left(Related_ID_products,3)=400 )
					WHERE sl_orders_products.ID_orders = $id_orders 
					AND sl_orders_products.Status NOT IN('Order Cancelled', 'Inactive')
					ORDER BY  ID_orders_products ;";
					my $sthi = &Do_SQL($query);
					#$log_query .= $query . "\n\n ================================== \n\n";
					$prodline = 0;
					while(my($id_products,$pname,$qty,$sprice,$pdisc,$tax,$shp,$shptax,$netcost,$salesorigins,$idcat) = $sthi->fetchrow()){
						++$prodline;

						$rush_shipping = 'Yes' if $id_products eq '600001046';

						###
						### Product Family
						###
						if($prodline == 1 or $in{'type'} ne 'order') {

							if(!$idcat){

								my ($sthc) = Do_SQL("SELECT ID_categories FROM sl_products_categories WHERE ID_products = RIGHT($id_products,6) LIMIT 1;");
								$idcat = $sthc->fetchrow();

							}

							$catname = $idcat ? &load_name('sl_categories','ID_categories', $idcat, 'Title') : 'N/A';

						}

						## Si type eq 'order' 1 linea por orden
						if($in{'type'} eq 'order'){
							$strprod .= qq|,"$qty","|.&format_sltvid($id_products).qq|","$pname","$netcost","$sprice","$pdisc","$tax","$shp","$shptax"| if ($prodline<=$maxprod);
							$items++;
							$total+= $sprice;
							$tdisc+=$pdisc;

							$ttax+=$tax;
							$ttax+=$shptax;

							$tshp+=$shp;
							$tcost+=$netcost;
							$torder+=$sprice-$pdisc+$tax+$shp+$shptax;
						}else{
							$strout .= qq|"$salesorigins","$tpago","$id_dids","$id_orders","$status","$first_call","$date","$time_order","$posteddate","$shpdate","$state","$county","$dma_name","$qty","|.&format_sltvid($id_products).qq|","$pname","$netcost","$sprice","$pdisc","$tax","$shp","$catname","$agentname","$user_type","$rush_shipping"|;
							if($cfg{'use_admin_users_tree'} and $cfg{'use_admin_users_tree'}==1){
								$strout .= qq|,"$supervisor","$coordinador"|;
							}
						}
					}
					
					## Si type eq 'order' 1 linea por orden
					if($in{'type'} eq 'order'){
						for ($items..$maxprod-1){
							$strprod .= ",,,,,,,,,";
						}
						
						# Se ocultan datos temporalmente
						$cid = &temp_hide_data($cid,'phone');
						$phone1 = &temp_hide_data($phone1,'phone');
						$phone2 = &temp_hide_data($phone2,'phone');
						$cellphone = &temp_hide_data($cellphone,'phone');

						$strout .= qq|$strprod,"$tcost","$total","$tdisc","$ttax","$tshp","$torder","$catname","$agentname","$user_type","$rush_shipping","$iduser_direksys","$user_direksys","$cid","$phone1","$phone2","$cellphone"|;
						if($cfg{'use_admin_users_tree'} and $cfg{'use_admin_users_tree'}==1){
							$strout .= qq|,"$supervisor","$coordinador"|;
						}
					}

					$strout .= qq|,"$clubinova"|;
					$strout .= qq|,"$id_customers"|;
					$strout .= "\r\n";

					print $strout;
				}
			}
			&auth_logging('report_view','');
			&log_reports($log_query, 'rep_bi_allorders');

			return;
		}else{
			$va{'message'} = &trans_txt('search_nomatches');
		}
	}
	&log_reports($log_query, 'rep_bi_allorders');
	print "Content-type: text/html\n\n";
	print &build_page('rep_bi_allorders.html');
}


sub rep_bi_allorders_v2 {
#-----------------------------------------
# Created on: 08/04/09  15:28:39 By  Roberto Barcenas
# Forms Involved: 
# Description : Extrae la informacion de ordenes 
# Parameters :
# Last Modified by RB: Se habilita el filtrado por productos y la presentacion del reporte mostrando por linea orden o producto.
# Last Modified on: 08/27/09 13:20:40
# Last Modified by: MCC C. Gabriel Varela S: Se cambia ID_dids por DNIS en sl_orders/
# Last Modified by RB on: 03/22/10 15:59:40 : Se modifica query para no mostrar preordenes en Status Converted
# Last Modified by RB on: 03/31/10 12:05:40 : Se modifica query para mostrar Ordenes con Preorden Converted con fecha de la Preorden	
# Last Modified by RB on: 07/06/10 12:00:40 : Dos modificaciones. 1. Se cambia inner join con sl_zipcodes por left join. 2. Se modifica cuando es orden de exportacion para traer el ID_products desde el Products_Related 
# Last modified on 19 Jul 2010 11:46:41
# Last modified by: MCC C. Gabriel Varela S. :Se corrige la consulta que obtiene el id y el nombre del producto, haciendo que no tome en cuenta el relacionado si es un servicio
# Last modified on 27 Jul 2010 13:14:09
# Last modified by: MCC C. Gabriel Varela S. :Se hace que se tome el relacionado para ??rdenes de exportaci??n s??lo si comienza con 400
# Last Modified by RB on 08/23/2010 12:03:40: Se agrega el user_type 
# Last Modified by RB on 10/05/2010 11:47:40: Se agrega first_call 
# Last Modified by RB on 03/23/2011 13:10:05: Se agrega DMA_DESC	
# Last modified on 08/11/2012 18:00:00
# Last modified by: EP : Se tomo el nombre de la empresa para el nombre del archivo a generar

	if($in{'action'}){
		
		my ($query_list);
		my $maxprod=1;
		my $info_user =	'';
		my $info_pprod = '';
		my $info_oprod = '';
		my $info_time = '';
		my $strout = '';
		
		## Si type eq 'order' 1 linea por orden
		$maxprod = 10	if $in{'type'} eq 'order';
		
		###### Busqueda por rango de fecha de order
		if ($in{'from_date'} and $in{'to_date'}){
			$where_date = " AND sl_orders.Date BETWEEN '$in{'from_date'}' AND '$in{'to_date'}' ";
		}else{
			$where_date = "";
		}

		
		### Busqueda por rango de tiempo
		if($in{'from_time'} or $in{'to_time'}){
			$in{'from_time'} 	= "00:00:00"	if !$in{'from_time'};
			$in{'to_time'} 		= "23:59:59"	if !$in{'to_time'};
			$info_time = " AND Time BETWEEN '$in{'from_time'}' AND '$in{'to_time'}'";
		}

		###### Busqueda por rango de fecha de venta
		if ($in{'from_sales_date'} and $in{'to_sales_date'}){
			$where_posteddate = "WHERE PostedDate BETWEEN '$in{'from_sales_date'}' AND '$in{'to_sales_date'}'";
		}else{
			$where_posteddate = "";
		}
		
		### Si es busqueda por id_admin_user 
		$info_user = "WHERE ID_admin_users = ".int($in{'id_admin_users'})." "	if $in{'id_admin_users'};
		
		
		### Si es busqueda por id_products
		if($in{'id_products'}){			
			$info_oprod = " AND 0 < (SELECT COUNT(DISTINCT ID_orders) FROM sl_orders_products WHERE ID_orders = sl_orders.ID_orders AND RIGHT(ID_products,6) = '".int($in{'id_products'})."' AND Status = 'Active') ";
		}

		my $fname   = 'all_orders_'.$cfg{'app_title'}.'.csv';
		$fname =~ s/\s/_/g;
		
		my $strHeader = "Channel,TPago,Orden,Status,Fecha,Hora";
		
		$strHeader .= ",Total Cost,Total Products,Total Descuento,Total Taxes,Total Envio,Total Orden"	if $in{'type'} eq 'order';
		
		$strHeader .= ",Familia de Producto,Usuario,Grupo,ID Usuario,Usuario Direksys,CID,PHONE1,PHONE2,CELLPHONE";

		$strHeader .= ",Supervisor,Coordinador";
		## Busqueda por consolas
		my $add_sql;
		if ($in{'id_salesorigins'}){
			my @arr_salesorigins = split /\|/ , $in{'id_salesorigins'};
			$add_sql .= " AND sl_orders.ID_salesorigins IN(". join(',', @arr_salesorigins) .")";
		}
		
		$query_list = "SELECT 
				   IDAgent,
				   AgentName,
				   IF(user_type IS NOT NULL AND user_type != '',user_type,'N/A') AS user_type,
				   IF(Orders IS NOT NULL,Orders,0)AS Orders,
				   ID_user,
				   UsernameDireksys
				FROM
				(
				   SELECT 
				      ID_admin_users AS IDAgent,
				      (CONCAT(UPPER(admin_users.FirstName),' ',UPPER(admin_users.MiddleName),' ',UPPER(admin_users.LastName))) AS AgentName,
				      user_type, admin_users.ID_admin_users as ID_user, admin_users.Username as UsernameDireksys
				   FROM admin_users $info_user
				)AS tmp_agent
				
				LEFT JOIN
				(
				   SELECT
				      ID_admin_users AS IDA,
				      COUNT(ID_Orders) AS Orders
				   FROM sl_orders
				      WHERE 1
				      $where_date
				      $info_time 

				      $info_oprod 

				      $add_sql

				      AND Status != 'System Error' 
				      GROUP BY ID_admin_users
				)AS tmp_order
				ON tmp_order.IDA = tmp_agent.IDAgent
				HAVING Orders > 0
				ORDER BY AgentName ";

		my ($sth) = &Do_SQL($query_list);
		if($sth->rows() > 0){

			print "Content-type: application/octetstream\n";
			print "Content-disposition: attachment; filename=$fname\n\n";
			print "$strHeader\r\n";
			
			while(my($idagent,$agentname,$user_type,$orders,$iduser_direksys,$user_direksys) = $sth->fetchrow()){

				if($in{'from_time'} or $in{'to_time'}) {
					$in{'from_time'} 	= "00:00:00"	if !$in{'from_time'};
					$in{'to_time'} 		= "23:59:59"	if !$in{'to_time'};
					$info_timep = " AND sl_orders.Time BETWEEN '$in{'from_time'}' AND '$in{'to_time'}'";
				}
				
				my $supervisor, $coordinador;

				$sql_sup = "SELECT
								(
									SELECT UPPER(CONCAT (Firstname,' ',LastName,' ',MiddleName))
									FROM admin_users
									WHERE ID_admin_users=cu_admin_users_tree.ID_admin_users2
								) supervisor, 
								(
									SELECT UPPER(CONCAT (Firstname,' ',LastName,' ',MiddleName))
									FROM admin_users
									WHERE ID_admin_users=cu_admin_users_tree.ID_admin_users3
								) coordinador
							FROM cu_admin_users_tree
							WHERE ID_admin_users = '$idagent';";
					$sth_sup = &Do_SQL($sql_sup);
					($supervisor, $coordinador) = $sth_sup->fetchrow();

				# /*, IFNULL(CountyName,'N/A') AS County*/

				my $sth = &Do_SQL("SELECT * FROM (
										SELECT DISTINCT ID_orders
											, IF(DNIS IS NULL,0,DNIS) AS DNIS
											, sl_orders.Date
											, sl_orders.Time
											, (shp_State)AS State, shp_City AS County
											, sl_orders.Status,Channel,IF(DMA_DESC IS NULL OR DMA_DESC = '','N/A',DMA_DESC) AS DMA_DESC, IF(shp_type = 2, 'Yes','No')AS Rush
											, sl_orders.shp_Zip, sl_orders.ID_zones, (SELECT Name FROM sl_zones WHERE sl_zones.ID_zones=sl_orders.ID_zones) as zone_name
											, if(sl_orders.Ptype<>'COD',(SELECT CapDate FROM sl_orders_payments WHERE sl_orders_payments.ID_orders=sl_orders.ID_orders AND Captured='Yes' LIMIT 1),sl_orders.PostedDate)PostedDate
											, (SELECT GROUP_CONCAT(DISTINCT ShpDate) FROM sl_orders_products  WHERE sl_orders_products.ID_orders=sl_orders.ID_orders AND ShpDate > '1900-01-01' GROUP BY ID_orders) as ShpDate
											, if(sl_orders.Ptype='COD',(SELECT CapDate FROM sl_orders_payments WHERE sl_orders_payments.ID_orders=sl_orders.ID_orders AND Captured='Yes' LIMIT 1),'')CapDate
											, (SELECT IF( COUNT(id_products)>0 , 1, 0) FROM sl_orders_products WHERE sl_orders_products.ID_orders=sl_orders.ID_orders AND id_products IN (600001005,600001035) )ClubInova
											, sl_orders.ID_customers
											, sl_orders.PType
											, sl_orders.first_call
										FROM sl_orders 
											LEFT JOIN sl_zipcodes ON sl_orders.shp_Zip = sl_zipcodes.ZipCode
											LEFT JOIN sl_zipdma ON sl_zipdma.ZipCode = sl_zipcodes.ZipCode 
											LEFT join sl_salesorigins on (sl_orders.ID_salesorigins=sl_salesorigins.ID_salesorigins)
										WHERE sl_orders.ID_admin_users = $idagent 
											$info_oprod
											$add_sql 
											$query_converted 
											$where_date 
											$info_timep $nopreorder  
											AND sl_orders.Status NOT IN('System Error','Converted')
									)orders
									$where_posteddate
									ORDER BY Date,Status,Time,ID_orders");
				                   
				while(my($id_orders,$id_dids,$date,$time_order,$state,$county,$status,$salesorigins,$dma_name,$rush_shipping,$shp_zip,$id_zones,$zone_name,$posteddate,$shpdate,$capdate,$clubinova,$id_customers,$tpago,$first_call) = $sth->fetchrow()){

					my $items=0;
					my $total = 0;
					my $tcost = 0;
					my $tdisc = 0;
					my $ttax = 0;
					my $tshp = 0;
					my $torder = 0;
					my $strprod = '';
					my $strout='';
					my $first_call = 'N/A';
					my $catname;
					$first_call = 'Unknown' if $first_call eq '';
					$tpago = 'Money Order'	if $tpago eq '';

					my $sth_cust = &Do_SQL("SELECT sl_customers.ID_customers
												, sl_customers.CID
												, sl_customers.Phone1
												, sl_customers.Phone2
												, sl_customers.Cellphone
											FROM sl_customers 
											WHERE sl_customers.ID_customers = ".$id_customers.";");
					my $customer = $sth_cust->fetchrow_hashref();
					my $cid = $customer->{'CID'};
					my $phone1 = $customer->{'Phone1'};
					my $phone2 = $customer->{'Phone2'};
					my $cellphone = $customer->{'Cellphone'};

					my $invoice = &Do_SQL("SELECT Date(cu_invoices.doc_date)doc_date
							FROM cu_invoices_lines
							INNER JOIN cu_invoices ON cu_invoices.ID_invoices=cu_invoices_lines.ID_invoices AND cu_invoices.Status='Certified' AND cu_invoices.invoice_type='ingreso'
							WHERE cu_invoices_lines.ID_orders=$id_orders
							ORDER BY cu_invoices.ID_invoices
							LIMIT 1");
					my ($date_invoice) = $invoice->fetchrow();			

					# Se ocultan datos temporalmente
					$state = &temp_hide_data($state);
					$county = &temp_hide_data($county);
					$shp_zip = &temp_hide_data($shp_zip);

					## Si type eq 'order' 1 linea por order
					$strout .= qq|"$salesorigins","$tpago","$id_orders","$status","$date","$time_order"| if $in{'type'} eq 'order';

					my $sthi = &Do_SQL("SELECT IF(LEFT(sl_orders_products.ID_products,3) = 100 AND LENGTH(Related_ID_products) = 9 and left(Related_ID_products,3)=400,Related_ID_products,sl_orders_products.ID_products) AS ID_products,
						IF(sl_parts.Name IS NOT NULL,sl_parts.Name,IF(sl_services.Name IS NOT NULL,sl_services.Name,sl_products.Name)) AS Pname,
						Quantity,SalePrice,sl_orders_products.Discount,sl_orders_products.Tax,sl_orders_products.Shipping,sl_orders_products.ShpTax
						,IF(sl_orders_products.Cost > 0,sl_orders_products.Cost,IF(SLTV_NetCost >=0,SLTV_NetCost,0))AS SLTV_NetCost,
						Channel, ID_categories
					FROM sl_orders_products 
					INNER JOIN sl_orders on (sl_orders_products.ID_orders = sl_orders.ID_orders)
					LEFT JOIN sl_salesorigins on (sl_orders.ID_salesorigins=sl_salesorigins.ID_salesorigins)
					LEFT JOIN sl_products ON sl_products.ID_products = RIGHT(sl_orders_products.ID_products,6)
					LEFT JOIN sl_services ON sl_services.ID_services = RIGHT(sl_orders_products.ID_products,4)
					LEFT JOIN sl_parts ON (ID_parts = RIGHT(Related_ID_products,4) and left(Related_ID_products,3)=400 )
					WHERE sl_orders_products.ID_orders = $id_orders 
					AND sl_orders_products.Status NOT IN('Order Cancelled', 'Inactive')
					ORDER BY  ID_orders_products ;");
					$prodline = 0;
					while(my($id_products,$pname,$qty,$sprice,$pdisc,$tax,$shp,$shptax,$netcost,$salesorigins,$idcat) = $sthi->fetchrow()){
						++$prodline;

						$rush_shipping = 'Yes' if $id_products eq '600001046';

						###
						### Product Family
						###
						if($prodline == 1 or $in{'type'} ne 'order') {

							if(!$idcat){

								my ($sthc) = Do_SQL("SELECT ID_categories FROM sl_products_categories WHERE ID_products = RIGHT($id_products,6) LIMIT 1;");
								$idcat = $sthc->fetchrow();

							}

							$catname = $idcat ? &load_name('sl_categories','ID_categories', $idcat, 'Title') : 'N/A';

						}

						## Si type eq 'order' 1 linea por orden
						if($in{'type'} eq 'order'){
						$items++;
							$total+= $sprice;
							$tdisc+=$pdisc;

							$ttax+=$tax;
							$ttax+=$shptax;

							$tshp+=$shp;
							$tcost+=$netcost;
							$torder+=$sprice-$pdisc+$tax+$shp+$shptax;
						}else{
							$strout .= qq|"$salesorigins","$tpago","$id_orders","$status","$date","$time_order","$qty","|.&format_sltvid($id_products).qq|","$pname","$netcost","$sprice","$pdisc","$tax","$shp","$catname","$agentname","$user_type"|;
							$strout .= qq|,"$supervisor","$coordinador"|;
							$strout .= qq|,"$id_customers"|;
						}
					}
					
					## Si type eq 'order' 1 linea por orden
					if($in{'type'} eq 'order'){											
					
						$strout .= qq|$strprod,"$tcost","$total","$tdisc","$ttax","$tshp","$torder","$catname","$agentname","$user_type","$iduser_direksys","$user_direksys","$cid","$phone1","$phone2","$cellphone"|;
						$strout .= qq|,"$supervisor","$coordinador"|;
						$strout .= qq|,"$id_customers"|;
					}

					$strout .= "\r\n";

					print $strout;
				}
			}
			&auth_logging('report_view','');
			return;
		}else{
			$va{'message'} = &trans_txt('search_nomatches');
		}

	}
	
	print "Content-type: text/html\n\n";
	print &build_page('rep_bi_allorders_v2.html');
}

sub rep_bi_capture{
#-----------------------------------------
# Created on: 08/04/09  15:28:39 By  Roberto Barcenas
# Forms Involved: 
# Description : Extra la informacion de ordenes/preordenes 
# Parameters :
# Last Modified by RB: Se habilita el filtrado por productos y la presentacion del reporte mostrando por linea orden o producto.
# Last Modified on: 08/27/09 13:20:40
# Last Modified by: MCC C. Gabriel Varela S: Se cambia ID_dids por DNIS en sl_orders/preorders
# Last modified on 08/11/2012 18:00:00
# Last modified by: EP : Se tomo el nombre de la empresa para el nombre del archivo a generar	
# Last modified by: EP : Se parametrizaron los textos a trans_txt
## TODO: Verificar que no este usando sl_preorders

	if($in{'action'}){
		my ($query_list);
		my $maxprod=1;
		my $info_user =	'';
		my $info_time = '';
		my $strout = '';
		
		###### Busqueda por rango de fecha
		$in{'from_date'} = &get_sql_date() if !$in{'from_date'};
		$in{'to_date'} = &get_sql_date() if !$in{'to_date'};
		
		
		### Busqueda por rango de tiempo
		if($in{'from_time'} or $in{'to_time'}){
			$in{'from_time'} 	= "00:00:00"	if !$in{'from_time'};
			$in{'to_time'} 		= "23:59:59"	if !$in{'to_time'};
			$info_time = " AND Time BETWEEN '$in{'from_time'}' AND '$in{'to_time'}'";
		}
		
		### Si es busqueda por id_admin_user 
		$info_user = "WHERE ID_admin_users = ".int($in{'id_admin_users'})." "	if $in{'id_admin_users'};
		
		my $fname   = 'capture_orders_sosl_'.$cfg{'app_title'}.'.csv';
		$fname =~ s/\s/_/g;
		
		my $strHeader = &trans_txt('rep_bi_capture_headers');
		
		$query_list = "SELECT 
				   IDAgent,
				   AgentName,
				   0 AS Preorders,
				   IF(Orders IS NOT NULL,Orders,0)AS Orders
				FROM
				(
				   SELECT 
				      ID_admin_users AS IDAgent,
				      CONCAT(FirstName,' ',LastName) AS AgentName
				   FROM admin_users $info_user
				)AS tmp_agent
				LEFT JOIN
				(
				   SELECT
				      ID_admin_users AS IDA,
				      COUNT(DISTINCT ID_Orders) AS Orders
				   FROM sl_orders_payments
				      WHERE CapDate BETWEEN  '$in{'from_date'}' AND '$in{'to_date'}'
				      $info_time 
				      AND Amount > 0 				      
				      GROUP BY ID_admin_users
				)AS tmp_order
				ON tmp_order.IDA = tmp_agent.IDAgent
				HAVING Orders > 0
				ORDER BY AgentName";
		
		my ($sth) = &Do_SQL($query_list);
		if($sth->rows() > 0){
			$txt_needle = "AND Time";
			##$txt_replace= "AND sl_preorders_payments.Time";
			$info_time =~	s/$txt_needle/$txt_replace/; 
			print "Content-type: application/octetstream\n";
			print "Content-disposition: attachment; filename=$fname\n\n";
			print "$strHeader\r\n";
			
			while(my($idagent,$agentname,$preorders,$orders) = $sth->fetchrow()){
				
				my $prefix = 'orders';
				if($orders){
					                   
					my $sth = &Do_SQL("SELECT DISTINCT sl_".$prefix.".ID_".$prefix.",IF(DNIS IS NULL,0,DNIS) AS DNIS,sl_".$prefix.".Date,sl_".$prefix.".Time,SUBSTR(shp_State,4)AS State,IF(CountyName IS NULL,'N/A',CountyName) AS County,sl_".$prefix.".Status
					                   FROM sl_".$prefix." INNER JOIN sl_zipcodes ON sl_".$prefix.".shp_Zip = sl_zipcodes.ZipCode
					                   INNER JOIN sl_".$prefix."_payments ON sl_".$prefix.".ID_".$prefix." = sl_".$prefix."_payments.ID_".$prefix."
					                   WHERE sl_".$prefix.".ID_admin_users = $idagent AND CapDate BETWEEN  '$in{'from_date'}' AND '$in{'to_date'}' $info_time AND sl_".$prefix.".Status != 'System Error'  ORDER BY Date,Status,Time,ID_".$prefix." ");
					                   
					while(my($id_orders,$id_dids,$date,$time_order,$state,$county,$status) = $sth->fetchrow()){
						my $strout='';
						my $tpago = &load_name('sl_'.$prefix.'_payments','ID_'.$prefix,$id_orders,'Type');
						$tpago = 'Money Order'	if $tpago eq '';
						
						my $sthp = &Do_SQL("SELECT 
												SUM(SalePrice+Tax+Shipping-Discount) AS OrderTotal
												FROM sl_".$prefix."_products 
												WHERE ID_".$prefix." = $id_orders AND sl_".$prefix."_products.Status != 'Inactive';");
						
						my ($orderTotal) = $sthp->fetchrow();
						
						my $sthi = &Do_SQL("SELECT Amount,CapDate FROM sl_".$prefix."_payments
												WHERE ID_".$prefix." = $id_orders AND Amount > 0
												AND CapDate BETWEEN  '$in{'from_date'}' AND '$in{'to_date'}' $info_time 
												ORDER BY CapDate;"); 
																
						while(my($amount,$capdate) = $sthi->fetchrow()){
							$strout .= "$tpago,$id_dids,$id_orders,$status,$date,$time_order,$state,$county,$orderTotal,$amount,$capdate,$agentname\r\n";
						}
						print $strout;
					}
				}                  
			}
			&auth_logging('report_view','');
			return;
		}else{
			$va{'message'} = &trans_txt('search_nomatches');
		}
	}
	
	print "Content-type: text/html\n\n";
	print &build_page('rep_bi_capture.html');
}



sub rep_bi_orders_customers_info{
# --------------------------------------------------------
	## TODO: Parametrizar que no existan textos que no pasen por transtxt
	## TODO: Verificar que no este usando sl_preorders
	## TODO: Los emails deben configurarse con setup


	if($in{'action'}){
		my ($query,$orders,$data, $cadinner);
		my $link_order = '';
		my $link_customer = '';

		if(!$in{'order_list'}){
			$error{'order_list'} = trans_txt('required');
			$err++;
			delete($in{'action'});
			&rep_bi_orders_customers_info;
			return;
		}

		@ary = split(/\n|\s|,/,$in{'order_list'});
		
		for (0..$#ary){
			$orders .= "$ary[$_],"	if length($ary[$_]) > 0;
		}
		chop($orders);
		$in{'order_list'} = $orders;
		
		$data = " ID_orders, sl_orders.Date,sl_orders.Status,sl_customers.ID_customers,CONCAT(FirstName,' ',LastName1),sl_customers.City,sl_customers.State,Phone1,Phone2,Cellphone ";		
		$cadinner = 'INNER JOIN  sl_customers ON sl_orders.ID_customers = sl_customers.ID_customers';
		
		my ($sth) = &Do_SQL("SELECT COUNT(*) FROM sl_orders $cadinner WHERE ID_orders IN($orders)");
		my ($tot_cant) = $sth->fetchrow();
		
		if ($tot_cant > 0){
			(!$in{'nh'}) and ($in{'nh'}=1);
			$first = ($in{'nh'} - 1) * $usr{'pref_maxh'};	
			$va{'matches'} = $tot_cant;
			($va{'pageslist'},$qs) = &pages_list($in{'nh'},"/cgi-bin/mod/$usr{'application'}/admin",$va{'matches'},$usr{'pref_maxh'});
			$in{'qs'} = $qs;
			if ($in{'print'}){
				$sth = &Do_SQL("SELECT $data FROM sl_orders $cadinner WHERE ID_orders IN($orders) ORDER BY ID_orders");
			}else{
				$sth = &Do_SQL("SELECT $data FROM sl_orders $cadinner WHERE ID_orders IN($orders) ORDER BY ID_orders LIMIT $first,$usr{'pref_maxh'}");
			}
			my (@c) = split(/,/,$cfg{'srcolors'});
			while (my ($id_orders,$date,$status,$id_customers,$customer,$city,$state,$phone1,$phone2,$cellphone) = $sth->fetchrow_array){
				$d = 1 - $d;
				my $phones;

				# Se ocultan datos temporalmente
				$city = &temp_hide_data($city);
				$state = &temp_hide_data($state);
				$phone1 = &temp_hide_data($phone1,'phone');
				$phone2 = &temp_hide_data($phone2,'phone');
				$cellphone = &temp_hide_data($cellphone,'phone');

				($phone1 ne '') and ($phones .= $phone1 . "  / ");
				($phone2 ne '') and ($phones .= $phone2 . "  /  ");
				($cellphone ne '') and ($phones .= $cellphone . "  /  ");
				chop($phones);
				chop($phones);
				chop($phones);
				
				if(!$in{'print'}){
						$link_order = qq|<a href="/cgi-bin/mod/$usr{'application'}/dbman?cmd=opr_orders&view=$id_orders">$id_orders</a>|;
						$link_customer = qq|<a href="/cgi-bin/mod/$usr{'application'}/dbman?cmd=opr_customers&view=$id_customers">$id_customers</a>|;
				}else{
						$link_order = $id_orders;
						$link_customer = $id_customers;
				}
				
				$va{'searchresults'} .= qq|
								<tr bgcolor='$c[$d]'>
									<td align="left" class="smalltext">$link_order</td>
									<td align="left" class="smalltext">$date </td>
									<td align="left" class="smalltext">$status </td>
									<td align="left" class="smalltext">$customer ($link_customer)</td>
									<td align="left" class="smalltext">$state ($city)</td>
									<td nowrap align="left" class="smalltext">$phones</td>
								</tr>\n|;						
			}
			&auth_logging('report_view',1);
			&send_text_mail($cfg{'from_email'},'chaas@innovagroupusa.com','CDR Info Report',"Reporte Generado por:$usr{'id_admin_users'}\n<br>Ordenes Ingresadas:$in{'order_list'}");
		}else{
			$va{'matches'} = 0;
			$va{'pageslist'} = 1;
			$va{'searchresults'} .= qq|<tr><td align="center" colspan="11">|.&trans_txt('search_nomatches').qq|</td></tr>|;
		}
		
		### Report Header
		$va{'report_tbl'} = qq |
								<center>
									<table border="0" cellspacing="0" cellpadding="4" width="70%" class="formtable">
										<tr>
									   		 <td class="menu_bar_title" colspan="2">Report Name : Orders/Customers Info</td>  
										</tr>
									 <tr>
								    	<td class="smalltext" colspan="2">Order List: $orders</td>   
									</tr>
								$va{'report_tbl'}
									<tr>
								   		 <td class="smalltext" colspan="2">Created by : ($usr{'id_admin_users'}) $usr{'firstname'} $usr{'lastname'} \@ |.&get_sql_date ." &nbsp;" . &get_time() .qq|</td>  
									</tr> 
								</table></center>\n\n\n\n\n|;
		&auth_logging('report_view','');
		if ($in{'print'}){
			print "Content-type: text/html\n\n";
			print &build_page('header_print.html');
			print &build_page('results_bi_orders_customers_info_print.html');
		}else{
			print "Content-type: text/html\n\n";
			print &build_page('results_bi_orders_customers_info_list.html');
		}
	}else{
		print "Content-type: text/html\n\n";
		print &build_page('rep_bi_orders_customers_info.html');
	}
}


sub rep_bi_orders_filter{
#-----------------------------------------
# Created on: 03/30/10  15:28:39 By  MCC C Gabriel Varela S
# Forms Involved: 
# Description : 
# Parameters :	
#Last modified on 13 Oct 2010 16:44:40
#Last modified by: MCC C. Gabriel Varela S. :Se agrega left join a sl_numbers_assign
	
	## TODO: Parametrizar que no existan textos que no pasen por transtxt, incluye los HEaders de los files
	## TODO: Los emails de aviso deben ser por configuración
	## TODO: Verificar que no este usando sl_preorders
	## TODO: Remover referencias a nombres de compañia por la "e" debe estar parametrizado
	## TODO: no usar sl_numbers debe usarse sl_mediadids
	## TODO: no usar sl_cdr debe usarse sl_leads_call

	if($in{'action'}){
		###### Busqueda por rango de fecha
		$in{'from_date'} = &get_sql_date() if !$in{'from_date'};
		$in{'to_date'} = &get_sql_date() if !$in{'to_date'};
		my $query="";
		if($in{'from_date'} or $in{'to_date'}){
			$query = " AND sl_orders.Date BETWEEN '$in{'from_date'}' AND '$in{'to_date'}'";
		}
		
		## Filter by Status
		if ($in{'status'} !~ /-1/){
			my $status=$in{'status'};
			$status =~ s/\|/','/g;
			$query .= " AND sl_orders.Status IN ('$status') ";
		}
		
		## Filter by Ptype
		if ($in{'ptype'} ne ''){
			#my $ptype=$in{'status'};
			my $ptype=$in{'ptype'};  
			$ptype =~ s/\|/','/g;
			$query .= " AND sl_orders.Ptype IN ('$ptype') ";
		}
		
		## Filter by DID
		if ($in{'did'} ne ''){
			my $did=$in{'did'};
			$did=~ s/\|/','/g;
			$query .= " AND sl_mediadids.didusa IN ('$did') ";
		}
		
		## Filter by Return
		if ($in{'withreturns'} eq 'on'){
			$query .= " Having not isnull(ID_returns)";
		}
		
		my $fname   =	'orders_filters_sosl'.$in{'date'}.'.csv';
		
		($in{'e'} eq '1') and ($fname =~	s/sosl/usa/);
		($in{'e'} eq '2') and ($fname =~	s/sosl/pr/);
		($in{'e'} eq '3') and ($fname =~	s/sosl/training/);
		($in{'e'} eq '4') and ($fname =~	s/sosl/gts/);
		$fname =~	s/\///g;
		if($cfg{'product_assign'}==1){
			$query_list = "sELECT 
							sl_orders.ID_orders, 
							concat(sl_customers.FirstName,' ',sl_customers.Lastname1)as CustomerName,
							sl_customers.Phone1,
							sl_customers.Phone2,
							sl_customers.Cellphone,
							sl_customers.CID,
							sl_orders.Date,
							sl_orders.Time,
							product as Product,
							PType,
							sl_orders.Status,
							ID_returns
						FROM sl_orders
						INNER join sl_customers ON(sl_orders.ID_customers=sl_customers.ID_customers)
						/*left join sl_numbers ON(sl_orders.Dids7=sl_numbers.didusa)
						LEFT JOIN sl_numbers_assign ON sl_numbers.ID_numbers=sl_numbers_assign.ID_numbers*/
						LEFT JOIN sl_mediadids ON (sl_orders.DIDS7=sl_mediadids.didusa)
						LEFT JOIN sl_returns ON(sl_orders.ID_orders=sl_returns.ID_orders)
						WHERE 1 $query";
		}else{
			$query_list = "SELECT 
						sl_orders.ID_orders, 
						concat(sl_customers.FirstName,' ',sl_customers.Lastname1)as CustomerName,
						sl_customers.Phone1,
						sl_customers.Phone2,
						sl_customers.Cellphone,
						sl_customers.CID,
						sl_orders.Date,
						sl_orders.Time,
						Product,
						PType,
						sl_orders.Status,
						ID_returns
					FROM sl_orders
					INNER join sl_customers on(sl_orders.ID_customers=sl_customers.ID_customers)
					/*left join sl_numbers on(sl_orders.Dids7=sl_numbers.didusa)*/
					LEFT JOIN sl_mediadids ON (sl_orders.DIDS7=sl_mediadids.didusa)
					LEFT JOIN sl_returns on(sl_orders.ID_orders=sl_returns.ID_orders)
					WHERE 1 $query";
		}
		&auth_logging('report_view','');
		my ($sth) = &Do_SQL($query_list);
		if($sth->rows() > 0){
			print "Content-type: application/octetstream\n";
			print "Content-disposition: attachment; filename=$fname\n\n";
			print "Order ID,Customer Name,Phone1,Phone2,Cellphone,CID,Order Date,Order Time,Product (DID),Order Type,Order Status\r\n";
			
			while($rec=$sth->fetchrow_hashref){
				print "$rec->{'ID_orders'},$rec->{'CustomerName'},$rec->{'Phone1'},$rec->{'Phone2'},$rec->{'Cellphone'},$rec->{'CID'},$rec->{'Date'},$rec->{'Time'},$rec->{'Product'},$rec->{'PType'},$rec->{'Status'}\r\n";
			}
			&auth_logging('report_view',1);
			my $sth=&Do_SQL("Select now(),FirstName,LastName from admin_users where id_admin_users=$usr{'id_admin_users'};");
			($nowd,$first,$last)=$sth->fetchrow_array;
			$status = &send_text_mail($cfg{'from_email'},'chaas@innovagroupusa.com','Calls without orders',"$usr{'id_admin_users'},$nowd,$first,$last\n<br>$query_list");
			return;
		}else{
			$va{'message'} = &trans_txt('not_records_found');
		}
	}
	
	print "Content-type: text/html\n\n";
	print &build_page('rep_bi_orders_filter.html');
}


sub rep_bi_noorder{
#-----------------------------------------
# Created on: 03/30/2010  10:05:39 By  Roberto Barcenas
# Forms Involved: 
# Description : Extrae reporte de llamadas en S7 que no estan asignadas a una orden.
# Parameters :
# Last Modified by RB on: 	
# Last modified on 13 Oct 2010 16:45:16
# Last modified by: MCC C. Gabriel Varela S. :Se cambia right por left
# Last Modified by RB on 06/06/2011 11:15:54 AM : Se agrega vixicom a la busqueda
# Last Modified by RB on 06/07/2011 06:11:19 PM : Se agrega textbox para poder pegar los dids 
# Last Modified by RB on 03/06/2012 02:12:27 PM : Se agrega campo Destination
# Last Modified by RB on 03/26/2012 04:57:09 PM : Se agrega S8
	
	## TODO: Parametrizar que no existan textos que no pasen por transtxt
	## TODO: Verificar que no este usando sl_preorders
	## TODO: Remover referencias a nombres de compañia por la "e" debe estar parametrizado
	## TODO: no usar sl_numbers debe usarse sl_mediadids
	## TODO: no usar sl_cdr debe usarse sl_leads_call

	if($in{'action'}){
		my $query = '';
		my $strout = '';
		my $founds=0;
		my $notfounds=0;
		my $total=0;
			
		###### Busqueda por rango de fecha
		if ($in{'from_date'}){
			$in{'from_date'}=~s/\//-/g;
			$query .= " AND DATE(sl_leads_calls.Date) >= '$in{'from_date'}' ";
		}

		$in{'to_date'} = &get_sql_date() if !$in{'to_date'};
		$query .= " AND DATE(sl_leads_calls.Date) <= '$in{'to_date'}' ";
		
		if($in{'from_time'}){
			$in{'from_time'}=&filter_values($in{'from_time'});
			$query.=" and time(sl_leads_calls.Date)>='$in{'from_time'}' ";
		}
		
		if($in{'to_time'}){
			$in{'to_time'}=&filter_values($in{'to_time'});
			$query.=" and time(sl_leads_calls.Date)<='$in{'to_time'}' ";
		}
		
		### Busqueda por Callcenter
		if($in{'destination'}){
			$in{'destination'}=&filter_values($in{'destination'});
			($in{'destination'} eq 'Vixicom') and ($query.= " AND Destination LIKE '%vixicom%'");
			($in{'destination'} eq 'S8') and ($query.= " AND Destination LIKE '%s8%'");
			($in{'destination'} !~ 'S8|Vixicom') and ($query.= " AND Destination NOT LIKE ('%s8%','%vixicom%') ");
		}
		

		###  Busqueda por DID
		$in{'didusa'} = $in{'dnis'} if $in{'dnis'};
		if($in{'didusa'}){
			$in{'didusa'}  =~ s/\||\n/','/g;
			$query .= " AND didusa IN ('$in{'didusa'}')";
		}
		$in{'didusa'} =~ s/','/\|/g;

		## Busqueda del Grupo
		$query .=" AND grupo IN('','US')	"	if $in{'e'}	==	1;
		$query .=" AND grupo = 'GTS'	"		if $in{'e'}	==	4;

		my $name_c  = $cfg{'app_title'};
		$name_c =~ s/\s//g;
		my $fname   =	'calls_withoutorder_direksys_'.$name_c.'_'.$in{'to_date'}.'.csv';

		$fname =~	s/\///g;
		
		my ($sth) = &Do_SQL("SELECT COUNT(*)
							FROM sl_leads_calls
							LEFT JOIN sl_mediadids ON sl_mediadids.didusa=sl_leads_calls.DIDUS
							WHERE 1=1 $query");	
		if($sth->rows() > 0){
			#print "Content-type: text/html\n\n";
			print "Content-type: application/octetstream\n";
			print "Content-disposition: attachment; filename=$fname\n\n";
			print "Fecha,Hora,DID,Producto,Caller ID,Destination\r\n";
			
			my ($sth) = &Do_SQL("SELECT DISTINCT 
									sl_leads_calls.Date,
									sl_leads_calls.Time,
									didusa,
									product,
									ID_leads,
									Destination 
								FROM sl_leads_calls
								LEFT JOIN sl_mediadids ON sl_mediadids.didusa=sl_leads_calls.DIDUS
								WHERE 1=1 $query");				
			$total = $sth->rows();
			
			while(my($date,$time,$didusa,$product,$src,$destination) = $sth->fetchrow()){
			    
				#my $destination = $lastdata =~ /vixicom/ ? 'Vixicom' : 'Mixcoac';
				    
			    my $query ='';
	           	$strout = '';
	           	$query = "	$src='".substr($rec->{'Phone1'},-10)."' OR ";
	        	my $sth = &Do_SQL("SELECT ID_customers FROM sl_customers
			      					WHERE '$src' = RIGHT(Phone1,10) OR '$src' = RIGHT(Phone2,10) OR '$src' = RIGHT(Cellphone,10) OR '$src' = RIGHT(CID,10)");

	        	if($sth->rows() > 0){
		      		my($id_customers) = $sth->fetchrow();
		      		my $sth_orders = &Do_SQL("SELECT COUNT(*) FROM sl_orders WHERE ID_customers = $id_customers AND Date BETWEEN DATE_SUB('$date',INTERVAL 3 DAY) AND DATE_ADD('$date',INTERVAL 3 DAY) ");
		      		my ($orders) = $sth_orders->fetchrow();

		      		if($orders == 0){

			        	$strout .= "$date,$time,$didusa,$product,$src,$destination\r\n";
			        	$notfounds++;
			    		
		      		}else{
			    		$strin .="ID_customers: $id_customers,DID:$didusa,Caller ID: $src, Destination:$destination \r\n";
			    		$founds++;
		      		}

		        }else{
			      	$strout .= "$date,$time,$didusa,$product,$src,$destination\r\n";
			      	$notfounds++;
		        }
	    		print $strout;
			}				
			#$va{'message'} = "Total llamadas: ".$total." -  No Encontrados:".$notfounds;
			&auth_logging('report_view','');
			#Se manda correo
			my $sth=&Do_SQL("Select now(),FirstName,LastName from admin_users where id_admin_users=$usr{'id_admin_users'};");
			($nowd,$first,$last)=$sth->fetchrow_array;
			$status = &send_mail($cfg{'from_email'},'chaas@inovaus.com','Calls without orders',"$usr{'id_admin_users'},$nowd,$first,$last\n<br>SELECT DISTINCT sl_leads_calls.Date,sl_leads_calls.Time,didusa,product,didmx,Destination FROM sl_leads_calls LEFT JOIN sl_mediadids ON sl_mediadids.didusa=sl_leads_calls.DIDUS WHERE 1=1 $query");
			return;			
		}else{
			$va{'message'} = &trans_txt('not_records_found');
		}
	}
	
	print "Content-type: text/html\n\n";
	print &build_page('rep_bi_noorder.html');
}


sub rep_bi_salesbysku{
# --------------------------------------------------------
# Created on: 05/12/2011 05:13:45 PM  
# Author: Roberto Barcenas
# Description : 
# Parameters : From_Date | To_Date | ID_parts

	## TODO: Parametrizar que no existan textos que no pasen por transtxt
	## TODO: Verificar que no este usando sl_preorders
	## TODO: Remover referencias a nombres de compañia por la "e" debe estar parametrizado
	## TODO: no usar sl_numbers debe usarse sl_mediadids
	## TODO: no usar sl_cdr debe usarse sl_leads_call
	## TODO: No deberian haber IDs, deben estar en configuracion
	
	if($in{'action'}){
		my ($query_list);
		my $strout = '';
		my $flag=0;
		
		if(!$in{'id_parts'}){
			$err++;
			$error{'id_parts'} = &trans_txt('required');
			$va{'message'} = &trans_txt('reqfields_short');
		  
			print "Content-type: text/html\n\n";
			print &build_page('rep_bi_salesbysku.html');
		  return;
		}
		
		$in{'id_parts'} =~ s/-| //g;
		#$in{'id_parts'} = substr($in{'id_parts'},-4) if length($in{'id_parts'}) > 4;
		$in{'id_parts'} -= 400000000 if $in{'id_parts'} > 400000000;
		
		###### Busqueda por rango de fecha
		$in{'from_date'} = &get_sql_date() if !$in{'from_date'};
		$in{'to_date'} = &get_sql_date() if !$in{'to_date'};
		
		###### Excluir Ordenes de Prueba?
		my $exclude_free = $in{'exclude_freeorders'} ? 1 : 0;
		
		
		my $date_from = $in{'from_date'};
		my $date_to = $in{'to_date'};
		my $id_parts = int($in{'id_parts'});
		my $date_type = $in{'type'} eq 'o' ? 'Date' : 'PostedDate';
		my $these_id_admin_users = '4122,4322,4688,4689,5020,5021,5022,5023,5024,5025,5026,5027,5028,5029,5030,5031,5032,5033,5201,5202,5283,5284,5285,5286,5288,5289';
		my %all_data;
		
		########################################
		########################################
		########                          ######
		########      Inbound + Web       ######
		########                          ######
		########################################
		########################################
		
		my $sku_name = &load_name('sl_parts','ID_parts',$id_parts,'Name');
		### Buscando productos para la parte ##
		my($sth) = &Do_SQL("SELECT ID_products,Name,SUM(Qty) FROM sl_skus_parts INNER JOIN sl_products ON ID_products = RIGHT(ID_sku_products,6) WHERE ID_parts = '$id_parts' GROUP BY ID_products ORDER BY ID_products;");
		my($total_products) = $sth->rows();
		
		## Hay productos asignados?
		if($total_products > 0){
		
		
			if($in{'export'}){

				$flag=1;
				my $fname   =	'salesbysku_sosl'.$in{'date'}.'.csv';
		
				($in{'e'} eq '1') and ($fname =~	s/sosl/usa/);
				($in{'e'} eq '2') and ($fname =~	s/sosl/pr/);

				($in{'e'} eq '3') and ($fname =~	s/sosl/training/);
				($in{'e'} eq '4') and ($fname =~	s/sosl/gts/);
				$fname =~	s/\///g;
		    
				print "Content-type: application/octetstream\n";
				print "Content-disposition: attachment; filename=$fname\n\n";
		    
				print "Product ID,Product Name,Orders NeT,TV SalePrice,Web SalePrice,Cost,SKUs,Orders Quantity,Return SalePrice,Return SKUs,Return Orders\n";
		
			}
		
			my $total_matches=0;
			my (@c) = split(/,/,$cfg{'srcolors'});
			## Revisamos cada producto
			PRODUCTS:while(my($id_products,$product_name,$this_qty) = $sth->fetchrow()){
			
				my $actual_order;
				my $total_sprice_orders=0;
				my $total_sprice_phone=0;
				my $total_sprice_web=0;
				my $total_cost_orders=0;
				my $total_cost_phone=0;
				my $total_cost_web=0;
				my $total_qty_orders=0;
				my $total_qty_phone=0;
				my $total_qty_web=0;
				my $total_sku_orders=0;
				my $total_sku_phone=0;
				my $total_sku_web=0;
				my $str_order_price='';
				my $str_order_cost='';
				my $str_web_price='';
				my $str_phone_price='';
		  
				## Vendido en el rango de fecha Web + Inbound
				my($sth_sales) = Do_SQL("SELECT sl_orders.ID_orders,sl_orders.Status,ID_orders_products,sl_orders.ID_admin_users,SalePrice-Discount AS Sprice FROM sl_orders INNER JOIN sl_orders_products
				ON sl_orders.ID_orders = sl_orders_products.ID_orders WHERE RIGHT(ID_products,6) = '$id_products' 
				AND sl_orders.$date_type BETWEEN '$date_from' AND '$date_to' AND sl_orders.Status NOT IN('Cancelled','Void','System Error') 
				AND sl_orders_products.Status IN('Active','ReShip','Undeliverable','') AND SalePrice >= '$exclude_free';");
		    
				next PRODUCTS if $sth_sales->rows() == 0;
				$d = 1 - $d;
		    
				while(my($id_orders,$order_status,$id_orders_products,$id_admin_users,$sale_price) = $sth_sales->fetchrow()){
			
					my ($this_price,$this_cost);
					## Cuantos skus en total por producto?
					my ($sth_parts) = Do_SQL("SELECT SUM(Qty)AS total_parts FROM sl_skus_parts WHERE RIGHT(ID_sku_products,6) = '$id_products'; ");
					my($total_parts) = $sth_parts->fetchrow();
					## Costo del sku
					my ($cost,$cost_adj);
					my ($sth_cost) =  Do_SQL("SELECT Cost from sl_orders_parts WHERE ID_orders_products = '$id_orders_products' AND ID_parts = '$id_parts';");
					if($sth_cost->rows() > 0){
						$cost = $sth_cost->fetchrow();
					}else{
						($cost, $cost_adj) = &load_sltvcost('40000'.$id_parts);
					}
          
					## Calcular Price
					if($total_parts > $this_qty){
					
						## Buscamos costo en sl_orders_products
						my($sth_tcost) = Do_SQL("SELECT Cost from sl_orders_products WHERE ID_orders_products = '$id_orders_products';");
						my($total_cost) = $sth_tcost->fetchrow();
						
						## Orden no enviada o costo no presente
						if(! int($total_cost)){
              
							## Costo en sl_orders_parts?
							my ($sth_tcost2) =  Do_SQL("SELECT IF(SUM(Cost) IS NULL,0,SUM(Cost))AS Cost from sl_orders_parts WHERE ID_orders_products = '$id_orders_products' AND ID_parts != '$id_parts';");
							$total_cost = $sth_tcost2->fetchrow();
					
							## Orden no enviada
							if(! int($total_cost)){
                
								## Buscamos el costo de las partes restantes
								my($sth_tparts) = &Do_SQL("SELECT ID_parts,Qty FROM sl_skus_parts WHERE RIGHT(ID_sku_products,6) = '$id_products' AND ID_parts != '$id_parts' ORDER BY ID_parts;");
								if($sth_tparts->rows() > 0){
									while(my($other_id_parts,$other_qty) = $sth_tparts->fetchrow()){
                    
										## Sacamos costo
										my ($xcost,$xcost_adj) = &load_sltvcost('40000'.$other_id_parts);
										$total_cost += ($xcost * $other_qty);
				
									}
                  
								}else{
									$total_cost -= round($cost * $this_qty,2); 
								}
                  
							}
              
						}else{
							#&cgierr("SELECT Cost from sl_orders_products WHERE ID_orders_products = '$id_orders_products';");
							$total_cost -= round($cost * $this_qty,2);
						}

						$total_cost += round($cost * $this_qty,2);
						$this_price = $sale_price * $cost / $total_cost * $this_qty;
						#&cgierr("$this_price = $sale_price * $cost / $total_cost * $this_qty;") if $order_status eq 'Shipped';
            
              
					}else{
						$this_price = $sale_price;
					}
					$this_price = round($this_price,2);
					$this_cost = round($cost * $this_qty,2);

					## Total global por producto
					$total_sprice_orders += $this_price;
					$total_cost_orders += $this_cost;
					$total_sku_orders += $this_qty;
					$str_order_price .= "$this_price +"; # Cadena con los precios de cada linea (para imprimir en debug)
					$str_order_cost .= "$this_cost +";# Cadena con los precios de cada linea (para imprimir en debug)
          
					## Total Qty
					if($actual_order ne $id_orders){
						$total_qty_orders++;
						($order_status eq 'Shipped' and $these_id_admin_users !~ /$id_admin_users/) and ($total_qty_phone++);
						($order_status eq 'Shipped' and $these_id_admin_users =~ /$id_admin_users/) and ($total_qty_web++);
						$actual_order = $id_orders;
					}
          
					## Order Telefonica / Orden Web
					($order_status eq 'Shipped' and $these_id_admin_users !~ /$id_admin_users/) and ($total_sku_phone += $this_qty) and ($total_sprice_phone += round($this_price,2)) and ($str_phone_price .= "$this_price +") and ($total_cost_phone += round($this_cost,2)) and ($str_phone_cost .= "$this_cost +");
					($order_status eq 'Shipped' and $these_id_admin_users =~ /$id_admin_users/) and ($total_sku_web += $this_qty) and ($total_sprice_web += round($this_price,2)) and ($str_web_price .= "$this_price +") and ($total_cost_web += round($this_cost,2)) and ($str_web_cost .= "$this_cost +");
			
					#&cgierr("$this_price = $sale_price * $cost / $total_cost * $this_qty; $total_sprice_phone") if $order_status eq 'Shipped';
				
				} # Linea en sl_orders_products
		    
				#&cgierr("Product ID: $id_products\nProduct Name: $product_name\nTotal SPrice($total_qty_orders - $total_sku_orders): $total_sprice_orders --- $str_order_price\nTotal SPrice TV($total_qty_phone - $total_sku_phone): $total_sprice_phone  --- $str_phone_price\nTotal Cost TV: $total_cost_phone\nTotal SPrice Web($total_qty_web - $total_sku_web): $total_sprice_web\nTotal Cost Web: $total_cost_web");
		  
		  
				##############################
				######                ########
				######  Devoluciones  ########
				######                ########
				##############################
		    
		    
				$actual_order=0;
				my $total_dev_sprice_orders=0;
				my $total_dev_sprice_phone=0;
				my $total_dev_sprice_web=0;
				my $total_dev_cost_orders=0;
				my $total_dev_cost_phone=0;
				my $total_dev_cost_web=0;
				my $total_dev_sku_orders=0;
				my $total_dev_sku_phone=0;
				my $total_dev_sku_web=0;
				my $total_dev_qty_orders=0;
				my $total_dev_qty_phone=0;
				my $total_dev_qty_web=0;
				my $str_dev_order_price='';
				my $str_dev_phone_price='';
				my $str_dev_web_price='';
				my $str_dev_order_cost='';
				my $str_dev_phone_cost='';
				my $str_dev_web_cost='';
		    
				## Devuelto en el rango de fecha Web + Inbound
				my($sth_dev) = Do_SQL("SELECT sl_orders.ID_orders,sl_orders.ID_admin_users,ABS(SalePrice-Discount) AS Sprice FROM sl_orders INNER JOIN sl_orders_products
				ON sl_orders.ID_orders = sl_orders_products.ID_orders WHERE RIGHT(ID_products,6) = '$id_products'
				AND sl_orders_products.$date_type BETWEEN '$date_from' AND '$date_to' AND sl_orders.Status NOT IN('Cancelled','Void','System Error')
				AND sl_orders_products.Status IN('Returned','Exchange','Undeliverable','') AND ABS(SalePrice) >= '$exclude_free' AND SalePrice < 0;");

				if($sth_dev->rows() > 0){
		      
		      
					while(my($id_orders,$id_admin_users,$sale_price) = $sth_dev->fetchrow()){
		      
						## Buscamos el costo inicial
						my ($sth_pdev) =Do_SQL("SELECT SUM(IF(ID_parts = '$id_parts',Cost,0))as s1, SUM(IF(ID_parts = '$id_parts',Quantity,0))as s2,
						SUM(IF(ID_parts != '$id_parts',Cost,0))as s3, SUM(IF(ID_parts != '$id_parts',Quantity,0))as s4
						FROM sl_orders_parts
						INNER JOIN
						(
						SELECT sl_orders_products.ID_orders_products FROM sl_orders_parts INNER JOIN sl_orders_products
						ON sl_orders_parts.ID_orders_products = sl_orders_products.ID_orders_products
						WHERE ID_orders = '$id_orders' AND RIGHT(ID_products,6) = '$id_products'
						AND ID_parts = '$id_parts' ORDER BY sl_orders_parts.Date DESC LIMIT 1
						)AS tmp
						ON tmp.ID_orders_products = sl_orders_parts.ID_orders_products GROUP BY tmp.ID_orders_products;");
						my ($this_dev_cost,$this_dev_qty,$all_dev_cost,$all_dev_qty) = $sth_pdev->fetchrow();

						## Revisar la manera de agrupar todos los de la parte y todos los de la no parte para no tener que iterar
						my $this_dev_price = round($sale_price * ($this_dev_cost/$this_dev_qty) / ($this_dev_cost + $all_dev_cost) * $this_dev_qty,2);
						#&cgierr("Order:$id_orders\nProduct:$product_name\nSPrice:$sale_price\n$this_dev_price = $sale_price * ($this_dev_cost/$this_dev_qty) / ($this_dev_cost + $all_dev_cost) * $this_dev_qty");

            
						## Total global por producto
						$total_dev_sprice_orders += $this_dev_price;
						$total_dev_cost_orders += round($this_dev_cost + $all_dev_cost,2);
						$total_dev_sku_orders += $this_dev_qty;
						$str_dev_order_price .= "$this_dev_price +"; # Cadena con los precios de cada linea (para imprimir en debug)
						$str_dev_order_cost .= round($this_dev_cost,2)." +";# Cadena con los precios de cada linea (para imprimir en debug)

						## Total Qty
						if($actual_order ne $id_orders){
							$total_dev_qty_orders++;
							($these_id_admin_users !~ /$id_admin_users/) and ($total_dev_qty_phone++);
							($these_id_admin_users =~ /$id_admin_users/) and ($total_dev_qty_web++);
							$actual_order = $id_orders;
						}
          
						## Order Telefonica / Orden Web
						($these_id_admin_users !~ /$id_admin_users/) and ($total_dev_sku_phone += $this_dev_qty) and ($total_dev_sprice_phone += $this_dev_price) and ($str_dev_phone_price .= "$this_dev_price +") and ($total_dev_cost_phone += round($this_dev_cost,2)) and ($str_phone_cost .= round($this_dev_cost,2)." +");
						($these_id_admin_users =~ /$id_admin_users/) and ($total_dev_sku_web += $this_dev_qty) and ($total_dev_sprice_web += $this_dev_price) and ($str_dev_web_price .= "$this_dev_price +") and ($total_dev_cost_web += round($this_dev_cost,2)) and ($str_web_cost .= round($this_dev_cost,2)." +");

					}
				}
		    
		    
				if($in{'export'}){
					print &format_sltvid(100000000+$id_products).",$product_name,".($total_sprice_orders).",$total_sprice_phone,$total_sprice_web,".($total_cost_phone+$total_cost_web).",".($total_sku_phone+$total_sku_web).",".($total_qty_phone+$total_qty_web).",$total_dev_sprice_orders,$total_dev_sku_orders,$total_dev_qty_orders\n";
				}else{

					#&cgierr("Total SPrice=$str_order_price\nTotal Phone= ");
					$va{'searchresults'} .= '<tr bgcolor='.$c[$d].' style="height:40px">
									<td align="left" width="80" nowrap>'.&format_sltvid(100000000+$id_products).'</td>
									<td align="left" width="350">'.$product_name.'</td>
									<td align="right" width="80" nowrap>'.&format_price($total_sprice_orders).'</td>
									<td align="right" width="80" nowrap>'.&format_price($total_sprice_phone).'</td>
									<td align="right" width="80" nowrap>'.&format_price($total_sprice_web).'</td>
									<td align="right" width="80" nowrap>'.&format_price($total_cost_phone+$total_cost_web).'</td>
									<td align="center" width="80" nowrap>'.($total_sku_phone + $total_sku_web).'</td>
									<td align="center" width="80" nowrap>'.($total_qty_phone + $total_qty_web).'</td>
									<td align="right" width="80" nowrap>'.&format_price($total_dev_sprice_orders).'</td>
									<td align="center" width="80" nowrap>'.$total_dev_sku_orders.'</td>
									<td align="center" width="90" nowrap>'.$total_dev_qty_orders.'</td>
									</tr>';
				}

				$all_data{'sprice_orders'} += $total_sprice_orders;
				$all_data{'sprice_phone'} += $total_sprice_phone;
				$all_data{'sprice_web'} += $total_sprice_web;
				$all_data{'cost_orders'} += ($total_cost_phone+$total_cost_web);
				$all_data{'skus_orders'} += ($total_sku_phone + $total_sku_web);
				$all_data{'qty_orders'} += ($total_qty_phone + $total_qty_web);
				$all_data{'sprice_dev'} += $total_dev_sprice_orders;
				$all_data{'skus_dev'} += $total_dev_sku_orders;
				$all_data{'qty_dev'} += $total_dev_qty_orders;

				$total_matches++;


			} # Productos

		} # Retail
		  
		########################################
		########################################
		########                          ######
		########      Exportacion         ######
		########                          ######
		########################################
		########################################

		$actual_order=0;
		my $total_exp_sprice_orders=0;
		my $total_exp_cost_orders=0;
		my $total_exp_qty_orders=0;
		my $total_exp_sku_orders=0;

		my($sth_exp) = Do_SQL("SELECT sl_orders.ID_orders,Quantity,sl_orders.ID_admin_users,SalePrice,Cost FROM sl_orders INNER JOIN sl_orders_products
		ON sl_orders.ID_orders = sl_orders_products.ID_orders WHERE RIGHT(Related_ID_products,4) = '$id_parts'
		AND sl_orders_products.$date_type BETWEEN '$date_from' AND '$date_to' AND sl_orders.Status = 'Shipped' /*NOT('Cancelled','Void','System Error') */
		AND sl_orders_products.Status IN('Active','ReShip','Undeliverable','') AND SalePrice > '$exclude_free';");

		if($sth_exp->rows() > 0){
	    
			while(my($id_orders,$this_exp_qty,$id_admin_users,$this_exp_sprice,$this_exp_cost) = $sth_exp->fetchrow()){
	      
				$total_exp_sprice_orders += $this_exp_sprice;
				$total_exp_cost_orders += $this_exp_cost;
				$total_exp_sku_orders += $this_exp_qty;
	        
				## Total Qty
				if($actual_order ne $id_orders){
					$total_exp_qty_orders++;
					$actual_order = $id_orders;
				}
	      
			}
		}
		  
		if($total_exp_sprice_orders > 0){
			
			if($in{'export'}){
				if(!$flag){
					my $fname   =	'salesbysku_sosl'.$in{'date'}.'.csv';

					($in{'e'} eq '1') and ($fname =~	s/sosl/usa/);
					($in{'e'} eq '2') and ($fname =~	s/sosl/pr/);

					($in{'e'} eq '3') and ($fname =~	s/sosl/training/);
					($in{'e'} eq '4') and ($fname =~	s/sosl/gts/);
					$fname =~	s/\///g;

					print "Content-type: application/octetstream\n";
					print "Content-disposition: attachment; filename=$fname\n\n";
				}
		    
				print "Exportation\nTotal Orders, Order Net,Total Cost,Total SKUs\n";
				print "$total_exp_qty_orders,$total_exp_sprice_orders,$total_exp_cost_orders,$total_exp_sku_orders\n";
				return;
		      
			}else{
		      
				$total_exp_sprice_orders = round($total_exp_sprice_orders,2);
				$total_exp_cost_orders = round($total_exp_cost_orders,2);
          
				$va{'searchresults2'} .= '<tr bgcolor="'.$c[$d].'" style="height:40px;">
									<td colspan="2" align="center" nowrap>'.$total_exp_qty_orders.'</td>
									<td colspan="3" align="right" nowrap>'.&format_price($total_exp_sprice_orders).'</td>
									<td colspan="3" align="right" nowrap>'.&format_price($total_exp_cost_orders).'</td>
									<td colspan="3" align="right" nowrap>'.$total_exp_sku_orders.'</td>
								</tr>';
                                 
				#$all_data{'sprice_orders'} += $total_exp_sprice_orders;
				#$all_data{'sprice_wholesale'} += $total_exp_sprice_orders;
				#$all_data{'cost_orders'} += $total_exp_cost_orders;
				#$all_data{'skus_orders'} += $total_exp_sku_orders;
				#$all_data{'qty_orders'} += $total_exp_qty_orders;
                                  
			}
       
		}else{
			$va{'searchresults2'} .= '<tr bgcolor="'.$c[$d].'" style="height:40px">
								<td colspan="11" align="center">'.&trans_txt('notmatch').'</td>
							</tr>';
		}
		  
	  
		$va{'matches'} = $total_matches;
		$va{'pageslist'} = 1;

		$va{'sprice_orders'}= &format_price($all_data{'sprice_orders'});
		$va{'sprice_phone'}= &format_price($all_data{'sprice_phone'});
		$va{'sprice_web'}= &format_price($all_data{'sprice_web'});
		$va{'cost_orders'}= &format_price($all_data{'cost_orders'});
		$va{'skus_orders'}= $all_data{'skus_orders'};
		$va{'qty_orders'}= $all_data{'qty_orders'};

		$va{'ret_orders'}= &format_price($all_data{'sprice_dev'});
		$va{'ret_skus'}= $all_data{'skus_dev'};
		$va{'ret_qty'}= $all_data{'qty_dev'};

		#&cgierr($str_idp);
		
		
		if($va{'searchresults'} ne '' or $va{'searchresults2'} ne ''){

			if($va{'searchresults'} eq ''){
				$va{'searchresults'} .= '<tr bgcolor="'.$c[$d].'" style="height:40px">
								<td colspan="11" align="center">'.&trans_txt('notmatch').'</td>
							</tr>';
			}

			my $exclude_string = $in{'exclude_freeorders'} ? '<tr><td class="smalltext" align="left">Free Orders</td><td class="smalltext">Excluded</td></tr>' : '';
		
			$va{'report_tbl'} = qq |
						<center>
							<table border="0" cellspacing="0" cellpadding="4" width="70%" class="formtable">
								<tr>
										<td class="menu_bar_title" colspan="2">Report Name : Sales by SKU</td>
								</tr>
								<tr>
							<td class="smalltext">SKU</td>
							<td class="smalltext">$sku_name (|.&format_sltvid(400000000+$id_parts).qq|)</td>
							</tr>
							<tr>
							<td class="smalltext">From Date</td>
							<td class="smalltext">$date_from</td>
							</tr>
							<tr>
							<td class="smalltext">To Date</td>
							<td class="smalltext">$date_to</td>
							</tr>
							$exclude_string
							<tr>
							<td class="smalltext" colspan="2">&nbsp;</td>
							</tr>
							<tr>
									<td class="smalltext" colspan="2">Created by : ($usr{'id_admin_users'}) $usr{'firstname'} $usr{'lastname'} \@ |.&get_sql_date ." &nbsp;" . &get_time() .qq|</td>
							</tr>
						</table></center>\n\n\n\n\n <!--\n $query_tot \n\n $query_list\n\n-->|;
			&auth_logging('report_view','');			
			if ($in{'print'}){
				print "Content-type: text/html\n\n";
				print &build_page('header_print.html');
				print &build_page('results_bi_salesbysku_print.html');
			}elsif($in{'export'}){
				return;
			}else{
				foreach $key (keys %in){
					$in{'qs'} .= "$key=$in{$key}&" unless ($key eq 'cmd');
				}
				
				print "Content-type: text/html\n\n";
				print &build_page('results_bi_salesbysku_list.html');

			}
	    
		}else{
			
			&auth_logging('report_view','');
			$va{'message'} = &trans_txt('notmatch');
			print "Content-type: text/html\n\n";
			print &build_page('results_bi_salesbysku_list.html');
		}
		
	}else{
  
		print "Content-type: text/html\n\n";
		print &build_page('rep_bi_salesbysku.html');
	}

}


#########################################################
#########################################################	
#	Function: 
#   		rep_bi_prodfam
#
#	Created by:
#		_Roberto Barcenas_
#
#	Modified By:
#
#   	Parameters:
#
#   	Returns:
# 			- Excel File
#
#   	See Also:
#
sub rep_bi_prodfam{
########################################################
########################################################


	
 	#print "Content-type: text/html\n\n";
 
	if($in{'action'}){
		my ($query_list);
		my $maxprod=1;
		my $info_user =	'';
		my $strout = '';
		
		## Si type eq 'order' 1 linea por orden
		$maxprod = 10	if $in{'type'} eq 'order';
		
		###### Busqueda por rango de fecha
		$in{'from_date'} = &get_sql_date() if !$in{'from_date'};
		$in{'to_date'} = &get_sql_date() if !$in{'to_date'};

#		## Busqueda por Familia
#		my $cad_inner;
#		my $prodfam_name;
#		if($in{'prodfam'}){
#			@these_patterns;
#			my $q1 = "SELECT pattern FROM sl_media_prodfam WHERE Name = '$in{'prodfam'}';";
#			my $sth = &Do_SQL($q1);
#			my $prodfam_str;
#			while(my($this_pattern) = $sth->fetchrow()){
#				$prodfam_str .= " Name LIKE '%$this_pattern%' OR Model LIKE '%$this_pattern%' OR";
#				push(@these_patterns,$this_pattern);
#			}
#			$prodfam_str= substr($prodfam_str,0,-3);
#
#			$cad_inner = " INNER JOIN (SELECT ID_orders FROM sl_orders_products INNER JOIN (SELECT DISTINCT ID_products FROM sl_products WHERE $prodfam_str)tmp
#							ON tmp.ID_products = RIGHT(sl_orders_products.ID_products,6)
#							WHERE Date BETWEEN '$in{'from_date'}' AND DATE_ADD('$in{'to_date'}', INTERVAL 5 DAY))tmp2
#							ON sl_orders.ID_orders = tmp2.ID_orders ";
#
#			&cgierr($cad_inner);
#		}
		
		local (%fampattern);
		
		my $fname   =	'prodfam_'.$in{'date'}.'.csv';
		$fname =~	s/\///g;
		
		my $cadp = $in{'type'} eq 'order' ? 'OrdenNet' : 'ProductTot';
		my $strHeader = "Origin,Pay Type,DID,Order,Status,Date,Time,Week,State,County,DMA,ProdFam,$cadp,Tax,S&H,Orden Total,COGS,User,Group,Paid,Denied,All,Returns";
		
		
		$query_list = "SELECT
							sl_orders.ID_orders,
							admin_users.ID_admin_users,
							CONCAT(FirstName,' ',LastName) AS AgentName,
							IF(user_type IS NOT NULL AND user_type != '',user_type,'N/A') AS user_type,
							IF(DNIS IS NULL,0,DNIS) AS DNIS,
							sl_orders.Date,sl_orders.Time,
							WEEK(sl_orders.Date,1)+1 AS week,
							SUBSTR(shp_State,4)AS State,
							IF(CountyName IS NULL,'N/A',CountyName) AS County,
							sl_orders.Status,
							Channel,
							IF(DMA_DESC IS NULL OR DMA_DESC = '','N/A',DMA_DESC) AS DMA_DESC
						FROM sl_orders
						$cad_inner
						INNER JOIN admin_users
						USING(ID_admin_users)
						LEFT JOIN sl_zipcodes ON sl_orders.shp_Zip = sl_zipcodes.ZipCode
		                LEFT JOIN sl_zipdma USING(ZipCode)
		                LEFT JOIN sl_salesorigins USING(ID_salesorigins)
		                WHERE 
		                	sl_orders.Date BETWEEN '$in{'from_date'}' AND '$in{'to_date'}' 
		                	AND sl_orders.Status NOT IN('System Error') 
		                GROUP BY sl_orders.ID_orders	 
		                ORDER BY 
		                	Date,Status,Time,ID_orders";													

		
		my ($sth) = &Do_SQL($query_list);
		if($sth->rows() > 0){
			print "Content-type: application/octetstream\n";
			print "Content-disposition: attachment; filename=$fname\n\n";
			print "$strHeader\r\n";
			
			while(my($id_orders,$idagent,$agentname,$user_type,$didmx,$d,$t,$week,$state,$county,$status,$salesorigins,$dma_name) = $sth->fetchrow()){
				
				my $items=0;
				my $total = 0;
				my $tcost = 0;
				my $tdisc = 0;
				my $ttax = 0;
				my $tshp = 0;
				my $torder = 0;
				my $strprod = '';
				my $strout='';
				my $tpago = &load_name('sl_orders_payments','ID_orders',$id_orders,'Type');
				$tpago = &load_name('sl_orders','ID_orders',$id_orders,'Ptype');
				$tpago = 'Money Order'	if $tpago eq '';
				$week = &weeknum($d);
				
				$order_str = "$salesorigins,$tpago,$didmx,$id_orders,$status,$d,$t,$week,$state,$county,$dma_name";  
				my $q2 = "SELECT
							ID_orders_products, 
							IF(LEFT(sl_orders_products.ID_products,3) = 100 AND LENGTH(Related_ID_products) = 9 AND LEFT(Related_ID_products,3)=400,Related_ID_products,sl_orders_products.ID_products) AS ID_products,
							IF(sl_parts.Name IS NOT NULL,sl_parts.Name,IF(sl_services.Name IS NOT NULL,sl_services.Name,sl_products.Name)) AS Pname,
							Quantity,
							SalePrice,
							sl_orders_products.Discount,
							sl_orders_products.Tax,
							Shipping,
							IF(sl_orders_products.Cost > 0,sl_orders_products.Cost,IF(SLTV_NetCost >=0,SLTV_NetCost,0))AS ProductCost
						FROM 
							sl_orders_products 
						INNER JOIN 
							sl_orders USING(ID_orders)
						LEFT JOIN 
							sl_products
						ON sl_products.ID_products = RIGHT(sl_orders_products.ID_products,6)
						LEFT JOIN sl_services
						ON sl_services.ID_services = RIGHT(sl_orders_products.ID_products,4)
						LEFT JOIN sl_parts 
						ON (ID_parts = RIGHT(Related_ID_products,4) AND left(Related_ID_products,3)=400 )
						WHERE sl_orders.ID_orders = '$id_orders' AND sl_orders_products.Status = 'Active'
						ORDER BY  ID_orders_products;";
				my $sth2 = &Do_SQL($q2);
				my $items=0;
				my $tprice=0;
				my $tdisc=0;
				my $ttax=0;
				my $ttax=0;
				my $tcost=0;
				my $tshp=0;
				my $torder=0;
				my %prod;

				while(my($id_op,$id_products,$pname,$qty,$sprice,$pdisc,$tax,$shp,$netcost) = $sth2->fetchrow()){
					my $qc = "SELECT SUM(Cost) FROM sl_orders_parts WHERE ID_orders_products = '$id_op';";
					my $sthc = &Do_SQL($qc);
					if($sthc->rows > 0){
						$netcost = $sthc->fetchrow();
					}
					$prod{$pname} += $sprice*$qty;


					## Si type eq 'order' 1 linea por orden
					if($in{'type'} eq 'order'){
						$items++;
						$tprice+= $sprice*$qty;
						$tdisc+=$pdisc;
						$ttax+=$tax;
						$tshp+=$shp;
						$tcost+=$netcost;
						$torder+=$sprice-$pdisc+$tax+$shp;
					}else{
						$prodfam_name = &load_prodfam(%prod) ;
						delete($prod{$pname});
						if(($in{'prodfam'} and $prodfam_name eq $in{'prodfam'}) or !$in{'prodfam'}){
							print  "$order_str,$prodfam_name,".($sprice*$qty).",".($sprice-$pdisc).",$tax,$shp, ".($sprice-$pdisc+$tax+$shp).",$netcost,$agentname,$user_type\r\n";
						}
					}
				}
				if ($in{'type'} eq 'order'){
					my ($paid,$denied,$all,$ret);
					if ($tpago eq 'Credit-Card' and $status='Shipped'){
						my $sth2 = &Do_SQL("SELECT SUM( IF( Captured = 'Yes', Amount, 0 ) ) AS Paid, 
												SUM( IF(STATUS = 'Denied', Amount, 0 ) ) AS Denied,
												SUM( IF(STATUS NOT IN ('Void','Cancelled'), Amount, 0 ) ) AS total
									FROM `sl_orders_payments`
									WHERE id_orders =$id_orders");
						($paid,$denied,$all) = $sth2->fetchrow();
						if ($all<($tprice-$tdisc)){
							$ret = $tprice-$tdisc-$all;
						}
					}
					#print "prod : $prodfam_name <> $in{'prodfam'}<br>";
					$prodfam_name = &load_prodfam(%prod) ;
					if(($in{'prodfam'} and $prodfam_name eq $in{'prodfam'}) or !$in{'prodfam'}){
						print "$order_str,$prodfam_name,".($tprice-$tdisc).",$ttax,$tshp,$torder,$tcost,$agentname,$user_type,$paid,$denied,$all,$ret\r\n";
					}
				}
			}
			
			&auth_logging('report_view','');
			return;
		}else{
			$va{'message'} = &trans_txt('not_records_found');
		}
	}

	print "Content-type: text/html\n\n";
	print &build_page('rep_bi_prodfam.html');
}


#########################################################
#########################################################	
#	Function: 
#   		load_prodfam
#
#	Created by:
#		_Carlos Haas_
#
#	Modified By:
#
#   	Parameters:
#
#   	Returns:
# 			- Excel File
#
#   	See Also:
#
sub load_prodfam{
########################################################
########################################################
	my (%rec) = @_;
	my ($value,$key,$nofam);
	if (!$fampattern{'loaded'}){
		my $q1 = "SELECT pattern FROM sl_media_prodfam WHERE Name = '$in{'prodfam'}';";
		my $sth = &Do_SQL("SELECT pattern,Name FROM sl_media_prodfam WHERE Status='Active'");
		while (my($p,$n) = $sth->fetchrow_array()){
			$fampattern{$p} = $n;
		}
	}
	foreach $value (sort {$rec{$b} <=> $rec{$a} } keys %rec){
		$nofam = $value if (!$nofam);
		foreach $key (keys %fampattern){
			
			if ($value =~ /$key/i){
				return $fampattern{$key};
			}
		}
	}
	if ($nofam){
		return $nofam;
	}else{
		return "N/A";
	}
}

#########################################################
#########################################################	
#	Function: 
#   		rep_bi_frec
#
#	Created by:
#		_Carlos Haas_
#
#	Modified By:
#
#   	Parameters:
#
#   	Returns:
# 		- Report on screen
#
#   	See Also:
#
sub rep_bi_frec{
########################################################
########################################################
# Last Modified on: 12/11/09 18:00:59
# Last modified by: EP. : Se agregaron textos a trans_txt	
	if($in{'action'}){
		my ($query_tot,$query_list,$data, $cadinner);
		
		$data = 'SUM(IF(Times=1,1,0))AS FirstTime, SUM( IF( Times =1, 1, 0 ) ) / COUNT( * ) AS Pct1T, SUM(IF(Times BETWEEN 2 AND 5,1,0))AS FiveTimes, SUM( IF( Times BETWEEN 2 AND 5, 1, 0 ) ) / COUNT( * ) AS Pct5T, SUM(IF(Times BETWEEN 6 AND 10,1,0))AS TenTimes, SUM( IF( Times BETWEEN 6 AND 10, 1, 0 ) ) / COUNT( * ) AS PctTT, SUM(IF(Times > 10,1,0))AS ManyTimes, SUM( IF( Times > 10, 1, 0 ) ) / COUNT( * ) AS PctMT, ';		
		$cadinner = 'INNER JOIN (SELECT ID_customers, COUNT( * ) AS Times FROM sl_orders GROUP BY ID_customers) AS tmp ON sl_orders.ID_customers = tmp.ID_customers';
				
		if ($in{'sortby'}){
			$sb = "ORDER BY $in{'sortby'} $in{'sortorder'}";
		}
		
		## Filter by Date
		if ($in{'from_date'}){
			$va{'report_tbl'} .= "<tr><td width='100' class='smalltext'>".&trans_txt('to_date')." : </td><td class='smalltext'>$in{'from_date'}</td></tr>\n";
			$query .= " AND sl_orders.Date >= '$in{'from_date'}' ";
		}
		if ($in{'to_date'}){
			$va{'report_tbl'} .= "<tr><td width='100' class='smalltext'>".&trans_txt('from_date')." : </td><td class='smalltext'>$in{'to_date'}</td></tr>\n";
			$query .= " AND sl_orders.Date <= '$in{'to_date'}' ";
		}
	
		if ($in{'excludevoid'}){
			$va{'report_tbl'} .= "<tr><td width='100' class='smalltext'>".&trans_txt('status')." : </td><td class='smalltext'>".&trans_txt('void_system_error_excluded')."</td></tr>\n";			
			$query .= " AND sl_orders.Status NOT IN ('Void','System Error') ";
		}	
		
		## Filter by State
		if ($in{'state'}){
			$va{'report_tbl'} .= "<tr><td width='100' class='smalltext'>".&trans_txt('state')." : </td><td class='smalltext'>$in{'state'}</td></tr>\n";									
			$query .= " AND sl_orders.State='$in{'state'}' ";
		}
		
		## Filter by pricelevels
		if ($in{'id_pricelevels'} > 0){
			my $pricelevels = $in{'id_pricelevels'};
			$pricelevels =~ s/\|/','/g;
			
			my @ary = split(/\|/,$in{'id_pricelevels'});
			for (0..$#ary){
				$sname .= &load_name('sl_pricelevels','ID_pricelevels',$ary[$_],'Name').',';
			}
			chop($sname);
			
			$va{'report_tbl'} .= "<tr><td width='100' class='smalltext'>".&trans_txt('reports_price_levels')." : </td><td class='smalltext'> $sname </td></tr>\n";									
			$query .= " AND sl_orders.ID_pricelevels IN ('$pricelevels') ";
		}
		
		## Filter by User
		if ($in{'user_type'}){
			$in{'user_type'} =~ s/\|/','/g;
			$va{'report_tbl'} .= "<tr><td width='100' class='smalltext'>".&trans_txt('reports_by_user')." : </td><td class='smalltext'>$in{'user_type'}</td></tr>\n";
			$query .= " AND 0 < (SELECT IF(user_type IN('$in{'user_type'}'),1,0) FROM admin_users WHERE ID_admin_users = sl_orders.ID_admin_users) ";
		}$in{'user_type'} =~ s/','/\|/g;
		
		$query =~	s/and/WHERE/i;
		
		
		if($in{'groupby'} eq 'halfhour'){
			$report_name = &trans_txt('rep_orders_p_id_half');			
			$usr{'pref_maxh'} = 30;
			$query_tot  = "SELECT COUNT(*),SUM(OrderNet) FROM sl_orders $query";
			$query_list = "SELECT IF( MINUTE(Time ) <=30, CONCAT( HOUR(Time ) , ':01 to ', HOUR(Time ) , ':30' ) , CONCAT( HOUR( sl_orders.Time ) , ':31 to ', HOUR(Time ) +1, ':00' ) ) AS RANGO , COUNT( * ) AS nums,$data SUM(OrderNet) AS amounts FROM sl_orders $cadinner $query GROUP BY HOUR(Time ) , MINUTE(Time ) <=30, MINUTE(Time ) >30 ORDER BY HOUR(Time ) ,RANGO";
		}elsif ($in{'groupby'} eq 'hour'){
			$report_name = &trans_txt('rep_orders_p_id_hour');
			$usr{'pref_maxh'} = 30;
			$query_tot  = "SELECT COUNT(*),SUM(OrderNet) FROM sl_orders $query";
			$query_list = "SELECT HOUR(Time),COUNT(*) AS nums, $data SUM(OrderNet) AS amounts FROM sl_orders $cadinner $query GROUP BY HOUR(sl_orders.Time) $sb ";
		}elsif($in{'groupby'} eq 'month'){
			$report_name = &trans_txt('month');	
			$query_tot  = "SELECT COUNT(*),SUM(OrderNet) FROM sl_orders $query";
			$query_list = "SELECT CONCAT(MONTH(Date),'-',YEAR(Date)),COUNT(*) AS nums, $data SUM(OrderNet) AS amounts FROM sl_orders $cadinner $query GROUP BY CONCAT(MONTH(Date),'-',YEAR(Date)) $sb ";
		}elsif($in{'groupby'} eq 'state'){
			$report_name = &trans_txt('state');	
			$query_tot  = "SELECT COUNT(*),SUM(OrderNet) FROM sl_orders $query";
			$query_list = "SELECT State,COUNT(*) AS nums, $data SUM(OrderNet) AS amounts FROM sl_orders $cadinner  $query GROUP BY State $sb ";
		}elsif($in{'groupby'} eq 'station'){
			$report_name = &trans_txt('reports_station');
			$cadinner .=" LEFT JOIN (SELECT ID_pricelevels,Name AS PriceLavel FROM sl_pricelevels) AS tmp2 ON tmp2.ID_pricelevels = sl_orders.ID_pricelevels ";	
			$query_tot  = "SELECT COUNT(*),SUM(OrderNet) FROM sl_orders $query";
			$query_list = "SELECT IF(PriceLavel IS NULL,'N/A',PriceLavel) AS Station,COUNT(*) AS nums, $data SUM(OrderNet) AS amounts FROM sl_orders $cadinner  $query GROUP BY sl_orders.ID_pricelevels $sb ";
		}else{
			$report_name = &trans_txt('date');
			$query_tot  = "SELECT COUNT(*),SUM(OrderNet) FROM sl_orders $query";
			$query_list = "SELECT Date,COUNT(*) AS nums, $data SUM(OrderNet) AS amounts FROM sl_orders $cadinner $query GROUP BY Date $sb ";
		}
		foreach $key (keys %in){
			$in{'qs'} .= "$key=$in{$key}&" unless ($key eq 'cmd');
		}
		
		my ($sth) = &Do_SQL("$query_tot");
		my ($tot_cant,$tot_amount) = $sth->fetchrow_array();
		
		if ($tot_cant>0 and $tot_amount>0){
			(!$in{'nh'}) and ($in{'nh'}=1);
			$first = ($in{'nh'} - 1) * $usr{'pref_maxh'};	
			my ($sth) = &Do_SQL($query_list);
			$va{'matches'} = $sth->rows;
			($va{'pageslist'},$qs) = &pages_list($in{'nh'},"/cgi-bin/mod/$usr{'application'}/admin",$va{'matches'},$usr{'pref_maxh'});
			if ($in{'print'}){
				$sth = &Do_SQL($query_list);
			}else{
				$sth = &Do_SQL($query_list ." LIMIT $first,$usr{'pref_maxh'}");
			}
			my (@c) = split(/,/,$cfg{'srcolors'});
			while (my ($desc,$orders,$first_time,$pct1,$five_times,$pct2,$ten_times,$pct3,$many_times,$pct4,$amount) = $sth->fetchrow_array){
				$d = 1 - $d;
				$va{'searchresults'} .= qq|
								<tr bgcolor='$c[$d]'>
									<td align="left" class="smalltext">$desc</td>
									<td align="center" class="smalltext">$orders</td>
									<td align="right" class="smalltext">$first_time</td>
									<td align="left" class="smalltext">(|.(&round($pct1,2)*100).qq|%)</td>
									<td align="right" class="smalltext">$five_times</td>
									<td align="left" class="smalltext">(|.(&round($pct2,2)*100).qq|%)</td>
									<td align="right" class="smalltext">$ten_times</td>
									<td align="left" class="smalltext">(|.(&round($pct3,2)*100).qq|%)</td>
									<td align="right" class="smalltext">$many_times</td>
									<td align="left" class="smalltext">(|.(&round($pct4,2)*100).qq|%)</td>
									<td nowrap align="right" class="smalltext">|.&format_price($amount).qq|</td>
								</tr>\n|;						
				$tot_1time += $first_time;
				$tot_5time += $five_times;
				$tot_ttime += $ten_times;
				$tot_mtime += $many_times;
			}
			$va{'tot_cant'} = $tot_cant;
			$va{'tot_amount'} = &format_price($tot_amount);
#			$va{'tot_1time'} = $tot_1time;
#			$va{'tot_5time'} = $tot_5time;
#			$va{'tot_ttime'} = $tot_ttime;
#			$va{'tot_mtime'} = $tot_mtime;

		}else{
			$va{'matches'} = 0;
			$va{'pageslist'} = 1;
			$va{'searchresults'} .= qq|<tr><td align="center" colspan="11">|.&trans_txt('search_nomatches').qq|</td></tr>|;
		}
		
		### Report Headet
		$va{'report_tbl'} = qq |
								<center>
									<table border="0" cellspacing="0" cellpadding="4" width="70%" class="formtable">
										<tr>
									   		 <td class="menu_bar_title" colspan="2">|.&trans_txt('report_name').qq| : $report_name</td>  
										</tr>
									 <tr>
								    	<td class="smalltext">|.&trans_txt('reports_units').qq|</td>  
								    	<td class="smalltext">|.&trans_txt('reports_customer_freq').qq|</td>  
									</tr>
								$va{'report_tbl'}
									<tr>
								   		 <td class="smalltext" colspan="2">|.&trans_txt('reports_created_by').qq|: ($usr{'id_admin_users'}) $usr{'firstname'} $usr{'lastname'} \@ |.&get_sql_date ." &nbsp;" . &get_time() .qq|</td>  
									</tr> 
								</table></center>\n\n\n\n\n <!--\n $query_tot \n\n $query_list\n\n-->|;
		&auth_logging('report_view','');
		if ($in{'print'}){
			print "Content-type: text/html\n\n";
			print &build_page('header_print.html');
			print &build_page('results_bi_frec_print.html');
		}else{
			print "Content-type: text/html\n\n";
			print &build_page('results_bi_frec.html');
					  
		}
	}else{
		print "Content-type: text/html\n\n";
		print &build_page('rep_bi_frec.html');
	}
}

#########################################################
#########################################################	
#	Function: 
#   		rep_bi_sex
#
#	Created by:
#		_Carlos Haas_
#
#	Modified By:
#
#   	Parameters:
#
#   	Returns:
# 		- Report on screen
#
#   	See Also:
#
sub rep_bi_sex{
########################################################
########################################################
# Last Modified on: 12/11/09 18:00:59
# Last modified by: EP. : Se agregaron textos a trans_txt

	if($in{'action'}){
		my ($query_tot,$query_list,$data, $cadinner);
		
		$data = "SUM(IF(Sex='Female',1,0))AS Female, SUM( IF( Sex = 'Female', 1, 0 ) ) / COUNT( * ) AS PctF, SUM(IF(Sex='Male',1,0))AS Male, SUM( IF(Sex='Male', 1, 0 ) ) / COUNT( * ) AS PctM, SUM(IF(Sex NOT IN('Female','Male'),1,0))AS Unknown, SUM( IF(Sex NOT IN('Female','Male'), 1, 0 ) ) / COUNT( * ) AS PctU, ";		
		$cadinner = 'INNER JOIN (SELECT ID_customers, Sex FROM sl_customers ) AS tmp ON sl_orders.ID_customers = tmp.ID_customers';
				
		if ($in{'sortby'}){
			$sb = "ORDER BY $in{'sortby'} $in{'sortorder'}";
		}
		
		## Filter by Date
		if ($in{'from_date'}){
			$va{'report_tbl'} .= "<tr><td width='100' class='smalltext'>".&trans_txt('from_date')." : </td><td class='smalltext'>$in{'from_date'}</td></tr>\n";
			$query .= " AND sl_orders.Date >= '$in{'from_date'}' ";
		}
		if ($in{'to_date'}){
			$va{'report_tbl'} .= "<tr><td width='100' class='smalltext'>".&trans_txt('to_date')." : </td><td class='smalltext'>$in{'to_date'}</td></tr>\n";
			$query .= " AND sl_orders.Date <= '$in{'to_date'}' ";
		}
	
		## Filter by State
		if ($in{'state'}){
			$va{'report_tbl'} .= "<tr><td width='100' class='smalltext'>".&trans_txt('state')." : </td><td class='smalltext'>$in{'state'}</td></tr>\n";									
			$query .= " AND sl_orders.State='$in{'state'}' ";
		}
		
		## Filter by pricelevels
		if ($in{'id_pricelevels'} !~ /-1/){
			my $pricelevels = $in{'id_pricelevels'};
			$pricelevels =~ s/\|/','/g;
			
			my @ary = split(/\|/,$in{'id_pricelevels'});
			for (0..$#ary){
				$sname .= &load_name('sl_pricelevels','ID_pricelevels',$ary[$_],'Name').',';
			}
			chop($sname);
			
			$va{'report_tbl'} .= "<tr><td width='100' class='smalltext'>".&trans_txt('reports_price_levels').": </td><td class='smalltext'> $sname </td></tr>\n";									
			$query .= " AND sl_orders.ID_pricelevels IN ('$pricelevels') ";
		}
		## Filter by status
		if ($in{'status'} !~ /-1/){
			my $status = $in{'status'};
			$status =~ s/\|/','/g;
			
			$va{'report_tbl'} .= "<tr><td width='100' class='smalltext'>".&trans_txt('status')." : </td><td class='smalltext'> $status </td></tr>\n";									
			$query .= " AND sl_orders.Status IN ('$status') ";
		}elsif ($in{'excludevoid'}){
			$va{'report_tbl'} .= "<tr><td width='100' class='smalltext'>".&trans_txt('status')." : </td><td class='smalltext'>".&trans_txt('void_system_error_excluded')."</td></tr>\n";			
			$query .= " AND sl_orders.Status NOT IN ('Void','System Error') ";
		}	
		
		## Filter by User
		if ($in{'user_type'}){
			$in{'user_type'} =~ s/\|/','/g;
			$va{'report_tbl'} .= "<tr><td width='100' class='smalltext'>".&trans_txt('reports_by_user')." : </td><td class='smalltext'>$in{'user_type'}</td></tr>\n";
			$query .= " AND 0 < (SELECT IF(user_type IN('$in{'user_type'}'),1,0) FROM admin_users WHERE ID_admin_users = sl_orders.ID_admin_users) ";
		}$in{'user_type'} =~ s/','/\|/g;
		
		$query =~	s/and/WHERE/i;
		
		
		if($in{'groupby'} eq 'halfhour'){
			$report_name = &trans_txt('rep_orders_p_id_half');			
			$usr{'pref_maxh'} = 30;
			$query_tot  = "SELECT COUNT(*),SUM(OrderNet) FROM sl_orders $query";
			$query_list = "SELECT IF( MINUTE(Time ) <=30, CONCAT( HOUR(Time ) , ':01 to ', HOUR(Time ) , ':30' ) , CONCAT( HOUR( sl_orders.Time ) , ':31 to ', HOUR(Time ) +1, ':00' ) ) AS RANGO , COUNT( * ) AS nums,$data SUM(OrderNet) AS amounts FROM sl_orders $cadinner $query GROUP BY HOUR(Time ) , MINUTE(Time ) <=30, MINUTE(Time ) >30 ORDER BY HOUR(Time ) ,RANGE";
		}elsif ($in{'groupby'} eq 'hour'){
			$report_name = &trans_txt('rep_orders_p_id_hour');			
			$usr{'pref_maxh'} = 30;
			$query_tot  = "SELECT COUNT(*),SUM(OrderNet) FROM sl_orders $query";
			$query_list = "SELECT HOUR(Time),COUNT(*) AS nums, $data SUM(OrderNet) AS amounts FROM sl_orders $cadinner $query GROUP BY HOUR(sl_orders.Time) $sb ";
		}elsif($in{'groupby'} eq 'month'){
			$report_name = &trans_txt('month');	
			$query_tot  = "SELECT COUNT(*),SUM(OrderNet) FROM sl_orders $query";
			$query_list = "SELECT CONCAT(MONTH(Date),'-',YEAR(Date)),COUNT(*) AS nums, $data SUM(OrderNet) AS amounts FROM sl_orders $cadinner $query GROUP BY CONCAT(MONTH(Date),'-',YEAR(Date)) $sb ";
		}elsif($in{'groupby'} eq 'state'){
			$report_name = &trans_txt('state');	
			$query_tot  = "SELECT COUNT(*),SUM(OrderNet) FROM sl_orders $query";
			$query_list = "SELECT State,COUNT(*) AS nums, $data SUM(OrderNet) AS amounts FROM sl_orders $cadinner  $query GROUP BY State $sb ";
		}elsif($in{'groupby'} eq 'station'){
			$report_name = &trans_txt('reports_station');
			$cadinner .=" LEFT JOIN (SELECT ID_pricelevels,Name AS Station FROM sl_pricelevels) AS tmp2 ON tmp2.ID_pricelevels = sl_orders.ID_pricelevels ";	
			$query_tot  = "SELECT COUNT(*),SUM(OrderNet) FROM sl_orders $query";
			$query_list = "SELECT IF(Station IS NULL,'N/A',Station) AS Station,COUNT(*) AS nums, $data SUM(OrderNet) AS amounts FROM sl_orders $cadinner  $query GROUP BY sl_orders.ID_pricelevels $sb ";
		}else{
			$report_name = &trans_txt('date');
			$query_tot  = "SELECT COUNT(*),SUM(OrderNet) FROM sl_orders $query";
			$query_list = "SELECT Date,COUNT(*) AS nums, $data SUM(OrderNet) AS amounts FROM sl_orders $cadinner $query GROUP BY Date $sb ";
		}
		foreach $key (keys %in){
			$in{'qs'} .= "$key=$in{$key}&" unless ($key eq 'cmd');
		}
		
		my ($sth) = &Do_SQL($query_tot);
		my ($tot_cant,$tot_amount) = $sth->fetchrow_array();
		
		if ($tot_cant>0 and $tot_amount>0){
			(!$in{'nh'}) and ($in{'nh'}=1);
			$first = ($in{'nh'} - 1) * $usr{'pref_maxh'};	
			my ($sth) = &Do_SQL($query_list);
			$va{'matches'} = $sth->rows;
			($va{'pageslist'},$qs) = &pages_list($in{'nh'},"/cgi-bin/mod/$usr{'application'}/admin",$va{'matches'},$usr{'pref_maxh'});
			if ($in{'print'}){
				$sth = &Do_SQL($query_list);
			}else{
				$sth = &Do_SQL($query_list ." LIMIT $first,$usr{'pref_maxh'}");
			}
			my (@c) = split(/,/,$cfg{'srcolors'});
			while (my ($desc,$orders,$female,$pct_female,$male,$pct_male,$unknown,$pct_unknown,$amount) = $sth->fetchrow_array){
				$d = 1 - $d;
				$va{'searchresults'} .= qq|
									<tr bgcolor='$c[$d]'>
										<td align="left" class="smalltext">$desc</td>
										<td align="center" class="smalltext">$orders</td>
										<td align="right" class="smalltext">$female</td>
										<td align="left" class="smalltext">(|.(&round($pct_female,2)*100).qq|%)</td>
										<td align="right" class="smalltext">$male</td>
										<td align="left" class="smalltext">(|.(&round($pct_male,2)*100).qq|%)</td>
										<td align="right" class="smalltext">$unknown</td>
										<td align="left" class="smalltext">(|.(&round($pct_unknown,2)*100).qq|%)</td>
										<td nowrap align="right" class="smalltext">|.&format_price($amount).qq|</td>
									</tr>\n|;						
#				$tot_1time += $first_time;
#				$tot_5time += $five_times;
#				$tot_ttime += $ten_times;
#				$tot_mtime += $many_times;
			}
			$va{'tot_cant'} = $tot_cant;
			$va{'tot_amount'} = &format_price($tot_amount);
#			$va{'tot_1time'} = $tot_1time;
#			$va{'tot_5time'} = $tot_5time;
#			$va{'tot_ttime'} = $tot_ttime;
#			$va{'tot_mtime'} = $tot_mtime;

		}else{
			$va{'matches'} = 0;
			$va{'pageslist'} = 1;
			$va{'searchresults'} .= qq|<tr><td align="center" colspan="11">|.&trans_txt('search_nomatches').qq|</td></tr>|;
		}
		
		### Report Headet
		$va{'report_tbl'} = qq |
								<center>
									<table border="0" cellspacing="0" cellpadding="4" width="70%" class="formtable">
										<tr>
									   		 <td class="menu_bar_title" colspan="2">|.&trans_txt('report_name').qq| : $report_name</td>  
										</tr>
									 <tr>
								    	<td class="smalltext">|.&trans_txt('reports_units').qq|</td>  
								    	<td class="smalltext">|.&trans_txt('reports_customer_sex').qq| </td>  
									</tr>
								$va{'report_tbl'}
									<tr>
								   		 <td class="smalltext" colspan="2">|.&trans_txt('reports_created_by').qq| : ($usr{'id_admin_users'}) $usr{'firstname'} $usr{'lastname'} \@ |.&get_sql_date ." &nbsp;" . &get_time() .qq|</td>  
									</tr> 
								</table></center>\n\n\n\n\n <!--\n $query_tot \n\n $query_list\n\n-->|;
		&auth_logging('report_view','');
		if ($in{'print'}){
			print "Content-type: text/html\n\n";
			print &build_page('header_print.html');
			print &build_page('results_bi_sex_print.html');
		}else{
			print "Content-type: text/html\n\n";
			print &build_page('results_bi_sex.html');
		}
	}else{
		print "Content-type: text/html\n\n";
		print &build_page('rep_bi_sex.html');
	}
}

sub rep_bi_sales_behavior{
# Last modified on 08/11/2012 18:00:00
# Last modified by: EP : Se agrego a todo el texto la funcion trans_txt
	if($in{'action'}){
		my (%query,%serie,$query,$err);
		
		if(!$in{'from_date_base'}){
			$error{'from_date_base'} = trans_txt('required');
			$err++;
		}
		
		if(!$in{'from_date_compare'}){
			$error{'from_date_compare'} = trans_txt('required');
			$err++;
		}
		
		if(!$in{'to_date_base'}){
			$error{'to_date_base'} = trans_txt('required');
			$err++;
		}
		
		if(!$in{'to_date_compare'}){
			$error{'to_date_compare'} = trans_txt('required');
			$err++;
		}
		
		if(!$err){
			
				$query = "";
				
				## Filter by Date
				$query{'base'} = "sl_orders.Date BETWEEN '$in{'from_date_base'}' AND '$in{'to_date_base'}' ";
				$query{'compare'} = "sl_orders.Date BETWEEN '$in{'from_date_compare'}' AND '$in{'to_date_compare'}' ";
				
				## Filter by category
				if ($in{'id_categories'}){
					if($in{'id_categories'} > 0){
						$va{'report_tbl'} .= "<tr><td width='100' class='smalltext'>".&trans_txt('category')." : </td><td class='smalltext'>".&load_name('sl_categories','ID_categories',$in{'id_categories'},'Title')."</td></tr>\n";			
						$query .= " AND RIGHT(sl_orders_products.ID_products,6) IN (SELECT ID_products FROM sl_products_categories WHERE ID_top='$in{'id_categories'}') ";
					}else{
						$va{'report_tbl'} .= "<tr><td width='100' class='smalltext'>".&trans_txt('category')." : </td><td class='smalltext'>N/A (Others)</td></tr>\n";
						$query .= " AND RIGHT(sl_orders_products.ID_products,6) NOT IN (SELECT DISTINCT ID_products FROM sl_products_categories) ";
					}
				}

				## Filter by User
				if ($in{'user_type'}){
					$in{'user_type'} =~ s/\|/','/g;
					$va{'report_tbl'} .= "<tr><td width='100' class='smalltext'>".&trans_txt('by_user')." : </td><td class='smalltext'>$in{'user_type'}</td></tr>\n";
					$query .= " AND 0 < (SELECT IF(user_type IN ('$in{'user_type'}'),1,0) FROM admin_users WHERE ID_admin_users = sl_orders.ID_admin_users) ";
				}$in{'user_type'} =~ s/','/\|/g;
				
				
				## Filter by Order Type
				if ($in{'ptype'}){
					$in{'ptype'} =~ s/\|/','/g;	
					$va{'report_tbl'} .= "<tr><td width='100' class='smalltext'".&trans_txt('reports_order_type')." : </td><td class='smalltext'>$in{'ptype'}</td></tr>\n";						
					$query .= " AND sl_orders.Ptype IN('$in{'ptype'}') ";
				}$in{'ptype'} =~ s/','/\|/g;
					
					
				## Filter by Products
				if ($in{'id_products'}){
					$in{'id_products'} = int($in{'id_products'});
					$va{'report_tbl'} .= "<tr><td width='100' class='smalltext'>".&trans_txt('reports_product')." : </td><td class='smalltext'>(".&format_sltvid($in{'id_products'}).") ".&load_name('sl_products','ID_products',$in{'id_products'},'Name')."</td></tr>\n";
					$query .= " AND RIGHT(sl_orders_products.ID_products,6)='$in{'id_products'}' ";
				}else{
					$query .= " AND ID_products > 100000 ";
				}
				
				
				foreach $key (keys %in){
					$in{'qs'} .= "$key=$in{$key}&" unless ($key eq 'cmd');
				}
				
				my $serietxt = 'base';
				for (1..2){

					($_ == 2) and ($serietxt = 'compare');
					##  New / Pending / Process/ Shipped / Void  / Cancelled Query
					$query_orders = "SELECT
							COUNT(DISTINCT sl_orders.ID_orders) AS Total,SUM(SalePrice-Discount+Shipping+Tax)AS OrderTotal,sl_orders.Status
							FROM sl_orders INNER JOIN sl_orders_products
							ON sl_orders.ID_orders = sl_orders_products.ID_orders
							WHERE $query{$serietxt} $query
							AND (sl_orders.ID_orders_related = 0 OR sl_orders.ID_orders_related IS NULL)
							AND sl_orders.Status != 'System Error'
							AND sl_orders_products.Status = 'Active'
							AND SalePrice > 0
							GROUP BY sl_orders.Status
							ORDER BY sl_orders.Status ASC;";

					## Orders Data
					my ($sth_orders) = &Do_SQL($query_orders);
					while(my ($tot_qty,$tot_amount,$status) = $sth_orders->fetchrow()){
						
						if($status =~ /New|Processed|Pending/){
							$serie{'orders_qty_npp_'. $serietxt} += $tot_qty; 
							$serie{'orders_amount_npp_'. $serietxt} += $tot_amount;
						}else{
							$serie{'orders_qty_'. lc($status) .'_'. $serietxt} = $tot_qty; 
							$serie{'orders_amount_'. lc($status) .'_'. $serietxt} = $tot_amount;
						}
						$serie{'orders_qty_total_'. $serietxt} += $tot_qty;
						$serie{'orders_amount_total_'. $serietxt} += $tot_amount;
					}

		    
					## Refunds Query
					$query_refunds = "SELECT COUNT(DISTINCT sl_orders.ID_orders) AS Orders, ABS(SUM(SalePrice-Discount+Shipping+Tax)) AS Refund
						        FROM sl_orders INNER JOIN sl_orders_products
						        ON sl_orders.ID_orders = sl_orders_products.ID_orders 
						        WHERE $query{$serietxt} $query
						        AND (sl_orders.ID_orders_related = 0 OR sl_orders.ID_orders_related IS NULL)
						        AND sl_orders.Status = 'Shipped'
						        AND sl_orders_products.Status = 'Returned' 
						        AND SalePrice < 0
						        AND 0 < ( SELECT COUNT(*) FROM sl_returns WHERE ID_orders = sl_orders.ID_orders AND merAction = 'Refund');";

					## Refunds Data
					my ($sth_refunds) = &Do_SQL($query_refunds);
					my ($tot_qty,$tot_amount) = $sth_refunds->fetchrow();
					$serie{'refunds_qty_'. $serietxt} = $tot_qty;
					$serie{'refunds_amount_'. $serietxt} = $tot_amount;



					## Refills Query
					$query_refills = "SELECT
							COUNT(DISTINCT sl_orders.ID_orders) AS Total,SUM(SalePrice-Discount+Shipping+Tax)AS OrderTotal
						        FROM sl_orders INNER JOIN sl_orders_products
						        ON sl_orders.ID_orders = sl_orders_products.ID_orders
						        INNER JOIN
						        (
							    SELECT sl_orders.ID_orders FROM sl_orders INNER JOIN sl_orders_products
							    ON sl_orders.ID_orders = sl_orders_products.ID_orders
							    WHERE $query{$serietxt} $query
							    AND (sl_orders.ID_orders_related = 0 OR sl_orders.ID_orders_related IS NULL)
							    AND sl_orders.Status = 'Shipped' AND sl_orders_products.Status = 'Active'
							    AND SalePrice > 0 GROUP BY sl_orders.ID_orders
						        ) AS tmp
						        ON ID_orders_related = tmp.ID_orders
						        WHERE sl_orders.Status = 'Shipped' 
						        AND sl_orders_products.Status = 'Active'
						        AND SalePrice > 0;";
						        
					## Refills Data
					my ($sth_refills) = &Do_SQL($query_refills);
					my ($tot_qty,$tot_amount) = $sth_refills->fetchrow();
					$serie{'refills_qty_'. $serietxt} = $tot_qty;
					$serie{'refills_amount_'. $serietxt} = $tot_amount;


					## Percentages
					$serie{'sales_perc_'. $serietxt} = ($serie{'orders_amount_total_'. $serietxt} == 0) ? 0 : round(($serie{'orders_amount_shipped_'. $serietxt} / $serie{'orders_amount_total_'. $serietxt}) * 100,2);
					$serie{'void_perc_'. $serietxt} = ($serie{'orders_amount_total_'. $serietxt} == 0) ? 0 :  round(($serie{'orders_amount_void_'. $serietxt} / $serie{'orders_amount_total_'. $serietxt}) * 100,2);
					$serie{'cancelled_perc_'. $serietxt} = ($serie{'orders_amount_total_'. $serietxt} == 0) ? 0 :  round(($serie{'orders_amount_cancelled_'. $serietxt} / $serie{'orders_amount_total_'. $serietxt}) * 100,2);
					$serie{'npp_perc_'. $serietxt} = ($serie{'orders_amount_total_'. $serietxt} == 0) ? 0 :  round(($serie{'orders_amount_npp_'. $serietxt} / $serie{'orders_amount_total_'. $serietxt}) * 100,2);
					$serie{'refund_perc_'. $serietxt} = ($serie{'orders_amount_total_'. $serietxt} == 0) ? 0 :  round(($serie{'refunds_amount_'. $serietxt} / $serie{'orders_amount_total_'. $serietxt}) * 100,2);
					$serie{'refill_perc_'. $serietxt} = ($serie{'orders_amount_total_'. $serietxt} == 0) ? 0 :  round(($serie{'refills_amount_'. $serietxt} / $serie{'orders_amount_total_'. $serietxt}) * 100,2);

					## So Far Percentages					
					$serie{'cancelled_perc_sofar_'. $serietxt} = round($serie{'void_perc_'. $serietxt} + $serie{'cancelled_perc_'. $serietxt},2);
					$serie{'npp_perc_sofar_'. $serietxt} = round($serie{'cancelled_perc_sofar_'. $serietxt} + $serie{'npp_perc_'. $serietxt},2);
					$serie{'refund_perc_sofar_'. $serietxt} = round($serie{'npp_perc_sofar_'. $serietxt} + $serie{'refund_perc_'. $serietxt},2);
					$serie{'refill_perc_sofar_'. $serietxt} = round($serie{'refund_perc_sofar_'. $serietxt} - $serie{'refill_perc_'. $serietxt},2);


					if($_ == 1 and $serie{'orders_amount_total_base'} > 0){
							### Series
							$serie{'serie_amount_void_'. $serietxt} = $serie{'orders_amount_total_'. $serietxt} - $serie{'orders_amount_void_'. $serietxt};
							$serie{'serie_amount_cancelled_'. $serietxt} = $serie{'serie_amount_void_'. $serietxt} - $serie{'orders_amount_cancelled_'. $serietxt};
							$serie{'serie_amount_npp_'. $serietxt} = $serie{'serie_amount_cancelled_'. $serietxt} - $serie{'orders_amount_npp_'. $serietxt};
							#$serie{'serie_amount_shipped_'. $serietxt} = $serie{'serie_amount_npp_'. $serietxt} - $serie{'orders_amount_shipped_'. $serietxt};
							$serie{'serie_amount_refund_'. $serietxt} = $serie{'serie_amount_npp_'. $serietxt} - $serie{'refunds_amount_'. $serietxt};
							$serie{'serie_amount_refill_'. $serietxt} = ($serie{'refills_amount_'. $serietxt} > 0) ? $serie{'serie_amount_refund_'. $serietxt} + $serie{'refills_amount_'. $serietxt} : $serie{'serie_amount_refund_'. $serietxt};
			
							## Tooltips
							$va{'funnel_orders_'. $serietxt} = '<b>Orders</b><br><font color="blue">Total:</font> '.format_price($serie{'orders_amount_total_'. $serietxt});
							$va{'funnel_void_'. $serietxt} = '<b>Void</b><br><font color="blue">Total:</font> '.format_price($serie{'orders_amount_void_'. $serietxt}).'<br><font color="blue">Variation:</font> '.$serie{'void_perc_'. $serietxt}.'%<br><font color="blue">So far:</font> '.$serie{'void_perc_'. $serietxt}.'%';
							$va{'funnel_cancelled_'. $serietxt} = '<b>Cancelled</b><br><font color="blue">Total:</font> '.format_price($serie{'orders_amount_cancelled_'. $serietxt}).'<br><font color="blue">Variation:</font> '.$serie{'cancelled_perc_'. $serietxt}.'%<br><font color="blue">So far:</font> '.$serie{'cancelled_perc_sofar_'. $serietxt}.'%';
							$va{'funnel_npp_'. $serietxt} = '<b>New/Pending/Processed</b><br><font color="blue">Total:</font> '.format_price($serie{'orders_amount_npp_'. $serietxt}).'<br><font color="blue">Variation:</font> '.$serie{'npp_perc_'. $serietxt}.'%<br><font color="blue">So far:</font> '.$serie{'npp_perc_sofar_'. $serietxt}.'%';
							#$va{'funnel_shipped_'. $serietxt} = '<b>Shipped</b><br>Total: '.format_price($serie{'orders_amount_shipped_'. $serietxt});
							$va{'funnel_refund_'. $serietxt} = '<b>Refunds</b><br><font color="blue">Total:</font> '.format_price($serie{'refunds_amount_'. $serietxt}).'<br><font color="blue">Variation:</font> '.$serie{'refund_perc_'. $serietxt} .'%<br><font color="blue">So far:</font> '.$serie{'refund_perc_sofar_'. $serietxt}.'%';
							$va{'funnel_refill_'. $serietxt} = '<b>Continuity</b><br><font color="blue">Total:</font> '.format_price($serie{'refills_amount_'. $serietxt}).'<br><font color="blue">Variation:</font> '.$serie{'refill_perc_'. $serietxt} .'%<br><font color="blue">So far:</font> '.$serie{'refill_perc_sofar_'. $serietxt}.'%';
			
							#$serie{'serie_amount_shipped_'. $serietxt},'id:tooltip_shipped','". format_price($serie{'serie_amount_shipped_'. $serietxt}) ."',
							$va{'funnel_options'} = "'funnel".$_."', [$serie{'orders_amount_total_'. $serietxt},$serie{'serie_amount_void_'. $serietxt},$serie{'serie_amount_cancelled_'. $serietxt},$serie{'serie_amount_npp_'. $serietxt},$serie{'serie_amount_refund_'. $serietxt},$serie{'serie_amount_refill_'. $serietxt},$serie{'serie_amount_refill_'. $serietxt}]";
							$va{'funnel_title'} = "'".&trans_txt('reports_sales_behavior')."'";
							$va{'funnel_tooltips'} = "'id:tooltip_orders_$serietxt','id:tooltip_void_$serietxt','id:tooltip_cancelled_$serietxt','id:tooltip_npp_$serietxt','id:tooltip_refund_$serietxt','id:tooltip_refill_$serietxt',";
							$va{'funnel_labels'} = "'". format_price($serie{'orders_amount_total_'. $serietxt}) ."', '". format_price($serie{'serie_amount_void_'. $serietxt}) ."', '". format_price($serie{'serie_amount_cancelled_'. $serietxt}) ."','". format_price($serie{'serie_amount_npp_'. $serietxt}) ."','". format_price($serie{'serie_amount_refund_'. $serietxt}) ."','". format_price($serie{'serie_amount_refill_'. $serietxt}) ."',''";
							$va{'funnelchart'.$_} = &build_page('func/construct_rgraph_funnel.html');
							
					}
				}

				## Gauges Meter
				
				## Sales Base
				$va{'meter_options'} = "'meter1', 0, 100, $serie{'sales_perc_base'}";
				$va{'meter_title'} = 'Shipped Base ('. $serie{'sales_perc_base'}. '%)';
				$va{'meter_red_start'} = 0;
				$va{'meter_red_end'} = 60;
				$va{'meter_yellow_start'} = 60;
				$va{'meter_yellow_end'} = 80;
				$va{'meter_green_start'} = 80;
				$va{'meter_green_end'} = 100;
				$va{'meterchart1'} = &build_page('func/construct_rgraph_meter.html');
				
				## Sales Compare
				$va{'meter_options'} = "'meter2', 0, 100, $serie{'sales_perc_compare'}";
				$va{'meter_title'} = 'Shipped Compare ('. $serie{'sales_perc_compare'}. '%)';
				$va{'meterchart2'} = &build_page('func/construct_rgraph_meter.html');

				## Void Base
				$va{'meter_options'} = "'meter3', 0, 100, $serie{'void_perc_base'}";
				$va{'meter_title'} = 'Void Base ('. $serie{'void_perc_base'}. '%)';		
				$va{'meter_red_start'} = 40;
				$va{'meter_red_end'} = 100;
				$va{'meter_yellow_start'} = 20;
				$va{'meter_yellow_end'} = 40;
				$va{'meter_green_start'} = 0;
				$va{'meter_green_end'} = 40;
				$va{'meterchart3'} = &build_page('func/construct_rgraph_meter.html'); 
	
				## Void Compare
				$va{'meter_options'} = "'meter4', 0, 100, $serie{'void_perc_compare'}";
				$va{'meter_title'} = 'Void Compare ('. $serie{'void_perc_compare'}. '%)';
				$va{'meterchart4'} = &build_page('func/construct_rgraph_meter.html');

				## Cancelled Base
				$va{'meter_options'} = "'meter5', 0, 100, $serie{'cancelled_perc_base'}";
				$va{'meter_title'} = 'Cancelled Base ('. $serie{'cancelled_perc_base'}. '%)';
				$va{'meterchart5'} = &build_page('func/construct_rgraph_meter.html');
				
				## Cancelled Compare
				$va{'meter_options'} = "'meter6', 0, 100, $serie{'cancelled_perc_compare'}";
				$va{'meter_title'} = 'Cancelled Compare ('. $serie{'cancelled_perc_compare'}. '%)';
				$va{'meterchart6'} = &build_page('func/construct_rgraph_meter.html');
				
				## Refund Base
				$va{'meter_options'} = "'meter7', 0, 4, $serie{'refund_perc_base'}";
				$va{'meter_title'} = 'Refund Base ('. $serie{'refund_perc_base'}. '%)';
				$va{'meter_red_start'} = 2.5;
				$va{'meter_red_end'} = 4;
				$va{'meter_yellow_start'} = 1.5;
				$va{'meter_yellow_end'} = 2.5;
				$va{'meter_green_start'} = 0;
				$va{'meter_green_end'} = 1.5;
				$va{'meterchart7'} = &build_page('func/construct_rgraph_meter.html');
				
				## Refund Compare
				$va{'meter_options'} = "'meter8', 0, 4, $serie{'refund_perc_compare'}";
				$va{'meter_title'} = 'Refund Compare ('. $serie{'refund_perc_compare'}. '%)';
				$va{'meterchart8'} = &build_page('func/construct_rgraph_meter.html');

				###### Charge the js scripts if not charged
				if(!$va{'rgraph_js'}){
					$va{'rgraph_js'} = &build_page('func/rgraph_js.html');
				}
				$va{'rgraph_js'} .='<script src="/RGraph/libraries/RGraph.funnel.js" ></script>'."\n";
				$va{'rgraph_js'} .='<script src="/RGraph/libraries/RGraph.meter.js" ></script>'."\n"; 


				### Report Header
				$va{'report_tbl'} = qq |
							<center>
								<table border="0" cellspacing="0" cellpadding="4" width="70%" class="formtable">
									<tr>
								   		 <td class="menu_bar_title" colspan="2">|.&trans_txt('report_name').qq| : |.&trans_txt('reports_sales_behavior').qq|</td>  
									</tr>
								 <tr>
							    	<td class="smalltext">|.&trans_txt('rep_bi_sales_behavior_period').qq|</td>  
							    	<td class="smalltext">|.&trans_txt('from_date').qq|: [in_from_date_base] |.&trans_txt('to_date').qq| [in_to_date_base]</td>  
								</tr>
								<tr>
							    	<td class="smalltext">|.&trans_txt('rep_bi_sales_behavior_comparison').qq|</td>  
							    	<td class="smalltext">|.&trans_txt('from_date').qq|: [in_from_date_compare] |.&trans_txt('to_date').qq| [in_to_date_compare]</td>  
								</tr>
								$va{'report_tbl'}
								<tr>
							   		 <td class="smalltext" colspan="2">|.&trans_txt('reports_created_by').qq| : ($usr{'id_admin_users'}) $usr{'firstname'} $usr{'lastname'} \@ |.&get_sql_date ." &nbsp;" . &get_time() .qq|</td>  
								</tr> 
							</table></center>\n\n\n|; 


				&auth_logging('report_view','');
				if ($in{'print'}){
					print "Content-type: text/html\n\n";
					print &build_page('header_print.html');
					print &build_page('results_bi_sales_behavior_print.html');
				}else{
					print "Content-type: text/html\n\n";
					print &build_page('results_bi_sales_behavior.html');
				}
		}else{
			print "Content-type: text/html\n\n";
			print &build_page('rep_bi_sales_behavior.html');	
		}
	}else{
		print "Content-type: text/html\n\n";
		print &build_page('rep_bi_sales_behavior.html');
	}
}


sub rep_bi_twilio_messages{
#-----------------------------------------
# Created on: 08/04/09  15:28:39 By  Roberto Barcenas
# Forms Involved:
# Description : Extrae la informacion de ordenes/preordenes
# Parameters :
# Last modified on 08/11/2012 18:00:00
# Last modified by: EP : Se tomo el nombre de la empresa para el nombre del archivo a generar
# Last modified by: EP : Se agrego la funcion transtxt a los textos
#TODO : Revisar la exportacion a excel
	if($in{'action'}){
		my ($query_tot,$query_list);

		$query = " FROM  `sl_twilio_sms` WHERE 1 ";

		## Filter by Date
		#$in{'from_date'}	= &get_sql_date()	if !$in{'from_date'};
		if ($in{'from_date'}){
			$va{'report_tbl'} .= "<tr><td width='100' class='smalltext'>".&trans_txt('from_date')." : </td><td class='smalltext'>$in{'from_date'}</td></tr>\n";
			$query .= " AND DATE(Date_sent) >= '$in{'from_date'}' ";
		}

		$in{'to_date'}	= &get_sql_date()	if !$in{'to_date'};
		if ($in{'to_date'}){
			$va{'report_tbl'} .= "<tr><td width='100' class='smalltext'>".&trans_txt('to_date')." : </td><td class='smalltext'>$in{'to_date'}</td></tr>\n";
			$query .= " AND DATE(Date_sent) <= '$in{'to_date'}' ";
		}

		if($in{'from_number'}){
			$va{'report_tbl'} .= "<tr><td width='100' class='smalltext'>".&trans_txt('from_number')." : </td><td class='smalltext'>$in{'from_number'}</td></tr>\n";
			$query .= " AND `From` = '$in{'from_number'}' ";
		}

		$in{'sortorder'}	=	'' if	!$in{'sortorder'};
		$sb = "ORDER BY Date_sent $in{'sortorder'}";

		$usr{'pref_maxh'} = 30;
		$query_tot  = "SELECT COUNT(*) FROM (SELECT DATE(`Date_sent`),`To`,`From`,Status,Price $query GROUP BY `To`,DATE(`Date_sent`))AS tmp ";
		$query_list = "SELECT DATE(`Date_sent`),`To`,`From`,Status,Price $query GROUP BY `To`,DATE(`Date_sent`)  $sb ";

		foreach $key (keys %in){
			$in{'qs'} .= "$key=$in{$key}&" unless ($key eq 'cmd');
		}

		my ($sth) = &Do_SQL($query_tot);
		$va{'matches'} = $sth->fetchrow();

		if ($va{'matches'} > 0){

			my $workbook,$worksheet;
			my $url = $va{'script_url'};
			$url =~ s/admin/dbman/;

			(!$in{'nh'}) and ($in{'nh'}=1);
			$first = ($in{'nh'} - 1) * $usr{'pref_maxh'};
			my ($sth) = &Do_SQL($query_list);
			($va{'pageslist'},$qs) = &pages_list($in{'nh'},"/cgi-bin/mod/$usr{'application'}/admin",$va{'matches'},$usr{'pref_maxh'});

			if ($in{'print'} or $in{'export'}){

				if($in{'export'}){
					
					my $fname   = $cfg{'app_title'}.'_twilio_messages-'.$in{'from_date'}.'-'.$in{'to_date'}.'.xls';				
					$fname =~ s/\s/_/g;
					use Spreadsheet::WriteExcel;

					# Send the content type
					print "Content-type: application/octetstream\n";
					print "Content-disposition: attachment; filename=$fname\n\n";

					# Redirect the output to STDOUT
					$workbook  = Spreadsheet::WriteExcel->new("-");
					$worksheet = $workbook->add_worksheet();

					# Write some text.
					$worksheet->write(0, 0,'Date Sent');
					$worksheet->write(0, 1,'Cellphone');
					$worksheet->write(0, 2,'Order ID');
					$worksheet->write(0, 3,'Customer Name');
					$worksheet->write(0, 4,'Order Date');
					$worksheet->write(0, 5,'Orde Satatus');
					$worksheet->write(0, 6,'Order Net');

					$date_format = $workbook->add_format(num_format => 'mm/dd/yy');
					$price_format = $workbook->add_format(align => 'right', num_format => '$0.00');

				}

				$sth = &Do_SQL($query_list);
			}else{
				$sth = &Do_SQL($query_list ." LIMIT $first,$usr{'pref_maxh'}");
			}
			my (@c) = split(/,/,$cfg{'srcolors'});
			my $row=1;


			LINE:while(my($date_sent,$to,$from,$status,$price) = $sth->fetchrow()){
				$d = 1 - $d;

				my($id_customers,$cname,$id_orders,$order_date,$order_net,$order_status);
				my ($sth) = &Do_SQL("SELECT sl_customers.ID_customers,CONCAT(FirstName,' ',LastName1)AS cname,ID_orders,sl_orders.Date,OrderNet,sl_orders.Status
							FROM sl_customers INNER JOIN sl_orders
							ON sl_orders.ID_customers = sl_customers.ID_customers
							WHERE (RIGHT('$to',10) = RIGHT(Phone1,10) OR RIGHT('$to',10) = RIGHT(Phone2,10) OR RIGHT('$to',10) = RIGHT(Cellphone,10))
							AND sl_orders.Date >= DATE_SUB('$date_sent',INTERVAL 1 DAY)
							ORDER BY sl_orders.Date DESC LIMIT 1;");

				if($sth->rows() > 0){

					($id_customers,$cname,$id_orders,$order_date,$order_net,$order_status) = $sth->fetchrow();

					if(!$in{'print'} and !$in{'export'}){
						$link_order = qq|<a href="/cgi-bin/mod/admin/dbman?cmd=opr_orders&view=$id_orders">$id_orders</a>|;
						$link_customer = qq|<a href="/cgi-bin/mod/admin/dbman?cmd=opr_customers&view=$id_customers">$cname ($id_customers)</a>|;
					}else{
						$link_order = $id_orders;
						$link_customer = $id_customers;
					}
				
				}else{
					$link_order='';
					$link_customer='';
					$order_date='';
					$order_net='';
					$order_status='';
				}

				if(!$in{'export'}){
					$va{'searchresults'} .= qq|
									<tr bgcolor='$c[$d]'>
										<td align="left">$date_sent</td>
										<td align="left">|.&format_phone($to).qq|</td>
										<td align="left">$link_order</td>
										<td align="left">$link_customer</td>
										<td align="left">$order_date</td>
										<td align="left">$order_status</td>
										<td align="right">|.&format_price($order_net).qq|</td>
									</tr>|;
				}else{
					$worksheet->write_date_time($row,0,$date_sent,$date_format);
					$worksheet->write_number($row,1,substr($to,-10));
					$worksheet->write_number($row,2,$link_order);
					$worksheet->write($row,3,$link_customer);
					$worksheet->write_date_time($row,4,$order_date,$date_format);
					$worksheet->write($row,5,$order_status);
					$worksheet->write_number($row,6,$order_net,$price_format);
					$row++;
				}
			}
		}else{
			$va{'matches'} = 0;
			$va{'pageslist'} = 1;
			$va{'searchresults'} .= qq|<tr><td align="center" colspan="7">|.&trans_txt('search_nomatches').qq|</td></tr>|;
		}

		### Report Headet
		$va{'report_tbl'} = qq |
						<center>
							<table border="0" cellspacing="0" cellpadding="4" width="70%" class="formtable">
								<tr>
										<td class="menu_bar_title" colspan="2">|.&trans_txt('report_name').qq|: |.&trans_txt('rep_bi_twilio_messages_rname').qq|</td>
								</tr>
								<tr>
								$va{'report_tbl'}
								<tr>
									<td class="smalltext" colspan="2">|.&trans_txt('reports_created_by').qq|: ($usr{'id_admin_users'}) $usr{'firstname'} $usr{'lastname'} \@ |.&get_sql_date ." &nbsp;" . &get_time() .qq|</td>
								</tr>
						</table></center>|;

		&auth_logging('report_view','');
		if(!$in{'export'}){
			if ($in{'print'}){
				print "Content-type: text/html\n\n";
				print &build_page('header_print.html');
				print &build_page('results_bi_twilio_messages_print.html');
			}else{
				print "Content-type: text/html\n\n";
				print &build_page('results_bi_twilio_messages.html');
			}
		}
	}else{
		print "Content-type: text/html\n\n";
		print &build_page('rep_bi_twilio_messages.html');
	}

}




sub build_report_ordquery{
# --------------------------------------------------------
# Last Modified RB: 05/01/09  10:43:03 -- Cambia byuser por user_type basado en la tabla admin_users
# Last Modified on: 05/12/09 10:13:45
# Last Modified by: MCC C. Gabriel Varela S: Se arregla mostrar la hora igual que agrupada por, anteriormente mostraba horas repetidas.

	## TODO: Parametrizar que no existan textos que no pasen por transtxt, incluye los HEaders de los files


	my ($sb) =  'ORDER BY sl_orders.Date';
	my ($cadinner) = " inner join sl_orders_products on (sl_orders.ID_orders=sl_orders_products.ID_orders and right(ID_products,6)=".int($in{'id_products'}).") " if($in{'id_products'}ne"");
	my ($query_tot,$query_list,$query,$report_name,$units);
	
	## Date Type
	$va{'report_tbl'} .= "<tr><td width='100' class='smalltext'>Date : </td><td class='smalltext'>Order Date</td></tr>\n";						

	if ($in{'groupby'} ne 'fpmnt' and $in{'groupby'} ne 'amtrange' and $in{'groupby'} ne 'fppaid'){
		$query = "WHERE  sl_orders_payments.Status NOT IN ('Cancelled','Order Cancelled','Void') and Amount>0";# if($in{'groupby'}eq"fpst");
	}

	## Filter by User
		if ($in{'user_type'}){
			$in{'user_type'} =~ s/\|/','/g;
			$va{'report_tbl'} .= "<tr><td width='100' class='smalltext'>By User : </td><td class='smalltext'>$in{'user_type'}</td></tr>\n";
			$query .= " AND 0 < (SELECT IF(user_type IN('$in{'user_type'}'),1,0) FROM admin_users WHERE ID_admin_users = sl_orders.ID_admin_users) ";
		}$in{'user_type'} =~ s/','/\|/g;
			
	## Filter by Date
	if ($in{'from_date'}){
		$va{'report_tbl'} .= "<tr><td width='100' class='smalltext'>From Date : </td><td class='smalltext'>$in{'from_date'}</td></tr>\n";
		$query .= " AND sl_orders.Date>='$in{'from_date'}' ";
	}
	if ($in{'to_date'}){
		$va{'report_tbl'} .= "<tr><td width='100' class='smalltext'>To Date : </td><td class='smalltext'>$in{'to_date'}</td></tr>\n";
		$query .= " AND sl_orders.Date<='$in{'to_date'}' ";
	}		
	
	## Filter by Status
	if ($in{'status'}){
		$in{'status'} =~ s/\|/','/g;
		$va{'report_tbl'} .= "<tr><td width='100' class='smalltext'>Status : </td><td class='smalltext'>$in{'status'}</td></tr>\n";						
		$query .= " AND sl_orders.Status IN ('$in{'status'}') ";
	}elsif ($in{'excludevoid'}){
		$va{'report_tbl'} .= "<tr><td width='100' class='smalltext'>Status : </td><td class='smalltext'>Void and System Error Excluded</td></tr>\n";			
		$query .= " AND sl_orders.Status NOT IN ('Void','System Error') ";
	}

	## Filter by pricelevels
	if ($in{'id_pricelevels'} !~ /-1/){
		my $pricelevels = $in{'id_pricelevels'};
			$pricelevels =~ s/\|/','/g;
			
			my @ary = split(/\|/,$in{'id_pricelevels'});
			for (0..$#ary){
				$sname .= &load_name('sl_pricelevels','ID_pricelevels',$ary[$_],'Name').',';
			}
			chop($sname);
			
			$va{'report_tbl'} .= "<tr><td width='100' class='smalltext'>Price Lavel : </td><td class='smalltext'> $sname </td></tr>\n";									
			$query .= " AND sl_orders.ID_pricelevels IN ('$pricelevels') ";
	}
	
	## Filter by Payment Type
	($in{'groupby'} eq 'paytype_form') and ($in{'paytype'} eq 'Credit-Card');
	if ($in{'paytype'}){
		$va{'report_tbl'} .= "<tr><td width='100' class='smalltext'>Payment Type : </td><td class='smalltext'>$in{'paytype'}</td></tr>\n";
		$query .= " AND sl_orders_payments.Type='$in{'paytype'}'";
	}else{
		$va{'report_tbl'} .= "<tr><td width='100' class='smalltext'>Payment Type : </td><td class='smalltext'>All</td></tr>\n";
	}
	## Filter by State
	if ($in{'state'}){
		$va{'report_tbl'} .= "<tr><td width='100' class='smalltext'>State : </td><td class='smalltext'>$in{'state'}</td></tr>\n";									
		$query .= " AND sl_orders.State='$in{'state'}' ";
	}
	## Filter by payments.Status.
	if ($in{'history'}){
		$va{'report_tbl'} .= "<tr><td width='100' class='smalltext'>History : </td><td class='smalltext'>$in{'history'}</td></tr>\n";						
	}
	
	
	## Group records by
	my ($cadinner);
	$cadinner =" inner join sl_orders_products on (sl_orders.ID_orders=sl_orders_products.ID_orders and right(ID_products,6)=".int($in{'id_products'}).") " if($in{'id_products'}ne"");
	
	if ($in{'groupby'} eq 'day'){
		$report_name = "Day";	
		$units       = "Payments / Amounts (Shipping & Taxes Included)";
		
		$query_tot  = "SELECT COUNT(*),SUM(amount) FROM sl_orders inner join sl_orders_payments on (sl_orders.ID_orders=sl_orders_payments.ID_orders) $cadinner $query";
		$query_list = "SELECT sl_orders.date,COUNT(*) AS nums,SUM(amount) AS amounts FROM sl_orders inner join sl_orders_payments on (sl_orders.ID_orders=sl_orders_payments.ID_orders) $cadinner $query GROUP BY sl_orders.date $sb ";
	}elsif($in{'groupby'} eq 'month'){
		$report_name = "Month";	
		$units       = "Payments / Amounts (Shipping & Taxes Included)";
		
		$query_tot  = "SELECT COUNT(*),SUM(amount) FROM sl_orders inner join sl_orders_payments on (sl_orders.ID_orders=sl_orders_payments.ID_orders) $cadinner $query";
		$query_list = "SELECT CONCAT(MONTH(sl_orders.date),'-',YEAR(sl_orders.date)),COUNT(*) AS nums,SUM(amount) AS amounts FROM sl_orders inner join sl_orders_payments on (sl_orders.ID_orders=sl_orders_payments.ID_orders) $cadinner $query GROUP BY CONCAT(MONTH(sl_orders.date),'-',YEAR(sl_orders.date)) $sb ";
	}elsif($in{'groupby'} eq 'halfhour'){
		$report_name = "Half an Hour";
		$units       = "Payments / Amounts (Shipping & Taxes Included)";
		$usr{'pref_maxh'} = 30;

		$query_tot  = "SELECT COUNT(*),SUM(amount) FROM sl_orders inner join sl_orders_payments on (sl_orders.ID_orders=sl_orders_payments.ID_orders) $cadinner $query";
		$query_list = "SELECT IF( MINUTE( sl_orders_payments.Time ) <=30, CONCAT( HOUR( sl_orders_payments.Time ) , ':01 to ', HOUR( sl_orders_payments.Time ) , ':30' ) , CONCAT( HOUR( sl_orders_payments.Time ) , ':31 to ', HOUR( sl_orders_payments.Time ) +1, ':00' ) ) AS RANGO,COUNT(*) AS nums,SUM(amount) AS amounts FROM sl_orders inner join sl_orders_payments on (sl_orders.ID_orders=sl_orders_payments.ID_orders) $cadinner $query GROUP BY HOUR( sl_orders_payments.Time ) , MINUTE( sl_orders_payments.Time ) <=30, MINUTE( sl_orders_payments.Time ) >30 ORDER BY HOUR( sl_orders_payments.Time ) ,RANGE ";
	
	}elsif($in{'groupby'} eq 'hour'){
		$report_name = "Hour";
		$units       = "Payments / Amounts (Shipping & Taxes Included)";
		$usr{'pref_maxh'} = 30;

		$query_tot  = "SELECT COUNT(*),SUM(amount) FROM sl_orders inner join sl_orders_payments on (sl_orders.ID_orders=sl_orders_payments.ID_orders) $cadinner $query";
		$query_list = "SELECT HOUR(sl_orders_payments.Time),COUNT(*) AS nums,SUM(amount) AS amounts FROM sl_orders inner join sl_orders_payments on (sl_orders.ID_orders=sl_orders_payments.ID_orders) $cadinner $query GROUP BY HOUR(sl_orders_payments.Time) $sb ";
	}elsif($in{'groupby'} eq 'state'){
		$report_name = "State";
		$units       = "Payments / Amounts (Shipping & Taxes Included)";
		
		$query_tot  = "SELECT COUNT(*),SUM(amount) FROM sl_orders inner join sl_orders_payments on (sl_orders.ID_orders=sl_orders_payments.ID_orders) $cadinner $query";
		$query_list = "SELECT State,COUNT(*) AS nums,SUM(amount) AS amounts FROM sl_orders inner join sl_orders_payments on (sl_orders.ID_orders=sl_orders_payments.ID_orders) $cadinner $query GROUP BY State $sb ";
	}	
				
	return ($query_tot, $query_list);
}

sub build_report_pordquery{
# --------------------------------------------------------
# Last Modified RB: 05/01/09  10:44:57 -- Cambia byuser por user_type basado en la tabla admin_users
# Last Modified on: 05/12/09 10:15:03
# Last Modified by: MCC C. Gabriel Varela S: Se arregla para que no muestre horas repetidas.
	## TODO: Parametrizar que no existan textos que no pasen por transtxt, incluye los HEaders de los files


	my ($sb) =  'ORDER BY sl_orders.Date';
	my ($cadinner) = " inner join sl_orders_products on (sl_orders.ID_orders=sl_orders_products.ID_orders and right(ID_products,6)=".int($in{'id_products'}).") " if($in{'id_products'}ne"");
	my ($query_tot,$query_list,$query,$report_name,$units);

	
	## Date Type
	$va{'report_tbl'} .= "<tr><td width='100' class='smalltext'>Date : </td><td class='smalltext'>Order Date</td></tr>\n";						

	$sb = "ORDER BY sl_orders.Date";
	$query="";
	
	if ($in{'groupby'} ne 'fpmnt' and $in{'groupby'} ne 'amtrange' and $in{'groupby'} ne 'fppaid'){
		$query = "WHERE  sl_orders.ID_orders = sl_orders_payments.ID_orders AND sl_orders_payments.Status<>'Cancelled'";
	}
	
	$query.=" and Ptype!='Credit-Card' ";
	
	## Filter by User
		if ($in{'user_type'}){
			$in{'user_type'} =~ s/\|/','/g;
			$va{'report_tbl'} .= "<tr><td width='100' class='smalltext'>By User : </td><td class='smalltext'>$in{'user_type'}</td></tr>\n";
			$query .= " AND 0 < (SELECT IF(user_type IN('$in{'user_type'}'),1,0) FROM admin_users WHERE ID_admin_users = sl_orders.ID_admin_users) ";
		}$in{'user_type'} =~ s/','/\|/g;
			
	## Filter by Date
	if ($in{'from_date'}){
		++$rows;
		$va{'report_tbl'} .= "<tr><td width='100' class='smalltext'>From Date : </td><td class='smalltext'>$in{'from_date'}</td></tr>\n";
		$query .= " AND sl_orders.date>='$in{'from_date'}' ";
	}
	if ($in{'to_date'}){
		++$rows;
		$va{'report_tbl'} .= "<tr><td width='100' class='smalltext'>To Date : </td><td class='smalltext'>$in{'to_date'}</td></tr>\n";
		$query .= " AND sl_orders.date<='$in{'to_date'}' ";
	}		
	
	## Filter by Status
	if ($in{'status'}){
		$in{'status'} =~ s/\|/','/g;
		$va{'report_tbl'} .= "<tr><td width='100' class='smalltext'>Status : </td><td class='smalltext'>$in{'status'}</td></tr>\n";						
		$query .= " AND sl_orders.Status IN ('$in{'status'}') ";
	}elsif ($in{'excludevoid'}){
		$va{'report_tbl'} .= "<tr><td width='100' class='smalltext'>Status : </td><td class='smalltext'>Void and System Error Excluded</td></tr>\n";			
		$query .= " AND sl_orders.Status NOT IN ('Void','System Error') ";
	}

	## Filter by Payment Exception
	if ($in{'statuspay'}){
		$in{'statuspay'} =~ s/\|/','/g;
		++$rows;			
		$va{'report_tbl'} .= "<tr><td width='100' class='smalltext'>Payment Exeption : </td><td class='smalltext'>$in{'statuspay'}</td></tr>\n";			
		$query .= " AND sl_orders.StatusPay IN ('$in{'statuspay'}') ";
	}
	## Filter by pricelevels
	if ($in{'id_pricelevels'} !~ /-1/){
		my $pricelevels = $in{'id_pricelevels'};
			$pricelevels =~ s/\|/','/g;
			
			my @ary = split(/\|/,$in{'id_pricelevels'});
			for (0..$#ary){
				$sname .= &load_name('sl_pricelevels','ID_pricelevels',$ary[$_],'Name').',';
			}
			chop($sname);
			
			$va{'report_tbl'} .= "<tr><td width='100' class='smalltext'>Price Lavel : </td><td class='smalltext'> $sname </td></tr>\n";									
			$query .= " AND sl_orders.ID_pricelevels IN ('$pricelevels') ";
	}
	
	## Filter by Payment Type
	if ($in{'paytype'} and $in{'groupby'} ne 'fpmnt' and $in{'groupby'} ne 'amtrange' and $in{'groupby'} ne 'fppaid'){
		++$rows;
		$va{'report_tbl'} .= "<tr><td width='100' class='smalltext'>Payment Type : </td><td class='smalltext'>$in{'paytype'}</td></tr>\n";
		($in{'paytype'} eq 'all') and ($query .= " AND sl_orders_payments.Type IN ('WesternUnion','Money Order','Layaway','COD')");
		($in{'paytype'} ne 'all' and $in{'paytype'} ne 'LayawayMO' and $in{'paytype'} ne 'LayawayCC') and ($query .= " AND sl_orders_payments.Type='$in{'paytype'}'");
		#Por tipo de Layaway
		($in{'paytype'} eq 'LayawayMO') and ($query .= " AND sl_orders_payments.Type='layaway' and Pmtfield3='' ");
		($in{'paytype'} eq 'LayawayCC') and ($query .= " AND sl_orders_payments.Type='layaway' and Pmtfield3!='' ");
		
	}
	## Filter by State
	if ($in{'state'}){
		++$rows;
		$va{'report_tbl'} .= "<tr><td width='100' class='smalltext'>State : </td><td class='smalltext'>$in{'state'}</td></tr>\n";									
		$query .= " AND sl_orders.State='$in{'state'}' ";
	}

	
	## Group records by
	if ($in{'groupby'} eq 'day'){
		$report_name = "Day";	
		$query_tot  = "SELECT COUNT(*),SUM(amount) FROM sl_orders_payments,sl_orders $query";
		$query_list = "SELECT sl_orders.date,COUNT(*) AS nums,SUM(amount) AS amounts FROM sl_orders_payments,sl_orders $query GROUP BY sl_orders.date $sb ";
	}elsif($in{'groupby'} eq 'month'){
		$report_name = "Month";	
		$units       = "Payments / Amounts (Shipping & Taxes Included)";
		$query_tot  = "SELECT COUNT(*),SUM(amount) FROM sl_orders_payments,sl_orders $query";
		$query_list = "SELECT CONCAT(MONTH(sl_orders.date),'-',YEAR(sl_orders.date)),COUNT(*) AS nums,SUM(amount) AS amounts FROM sl_orders_payments,sl_orders $query GROUP BY CONCAT(MONTH(sl_orders.date),'-',YEAR(sl_orders.date)) $sb ";
	}elsif($in{'groupby'} eq 'halfhour'){
		$report_name = "Half an Hour";
		$units       = "Payments / Amounts (Shipping & Taxes Included)";
		$usr{'pref_maxh'} = 30;

		$query_tot  = "SELECT COUNT(*),SUM(amount) FROM sl_orders_payments,sl_orders $query";
		$query_list = "SELECT IF( MINUTE( sl_orders_payments.Time ) <=30, CONCAT( HOUR( sl_orders_payments.Time ) , ':01 to ', HOUR( sl_orders_payments.Time ) , ':30' ) , CONCAT( HOUR( sl_orders_payments.Time ) , ':31 to ', HOUR( sl_orders_payments.Time ) +1, ':00' ) ) AS RANGO,COUNT(*) AS nums,SUM(amount) AS amounts FROM  sl_orders_payments,sl_orders $query GROUP BY HOUR( sl_orders_payments.Time ) , MINUTE( sl_orders_payments.Time ) <=30, MINUTE( sl_orders_payments.Time ) >30 ORDER BY HOUR( sl_orders_payments.Time ) ,RANGE ";
	
	}elsif($in{'groupby'} eq 'hour'){
		$report_name = "Hour";
		$usr{'pref_maxh'} = 30;
		$query_tot  = "SELECT COUNT(*),SUM(amount) FROM sl_orders_payments,sl_orders $query";
		$query_list = "SELECT HOUR(sl_orders_payments.Time),COUNT(*) AS nums,SUM(amount) AS amounts FROM sl_orders_payments,sl_orders $query GROUP BY HOUR(sl_orders_payments.Time) $sb ";
	}elsif($in{'groupby'} eq 'state'){
		$report_name = "State";
		$query_tot  = "SELECT COUNT(*),SUM(amount) FROM sl_orders_payments, sl_orders $query";
		$query_list = "SELECT State,COUNT(*) AS nums,SUM(amount) AS amounts FROM sl_orders_payments, sl_orders  $query GROUP BY State $sb ";

	}
	
	return ($query_tot, $query_list);
}


#############################################################################
#############################################################################
#   Function: rep_bi_allorders_custom2
#
#       Es: Reporte de ordenes de ventas por rango de fechas
#       En: Report sales orders by date range
#
#
#    Created on: 17/05/2013
#
#    Author: Alejandro Diaz
#
#    Modifications:
#
#        - Modified on ** by *** : 
#
#   Parameters:
#
#      - id_orders
#
#  Returns:
#
#      Devuelve 1 si la ordern se puede editar o 0 si  no se puede
#
#   See Also:
#
#      <>
#
sub rep_bi_salesday{
#############################################################################
#############################################################################

	if($in{'action'}) {

		my ($query_list);
		my $maxprod=1;
		my $info_user =	'';
		my $info_pprod = '';
		my $info_oprod = '';
		my $info_time = '';
		my $strout = '';

		my $add_filters='';
		
		## Si type eq 'order' 1 linea por orden
		$maxprod = 10	if $in{'type'} eq 'order';
		
		###### Busqueda por rango de fecha
		$in{'from_date'} = &get_sql_date() if !$in{'from_date'};
		$in{'to_date'} = &get_sql_date() if !$in{'to_date'};
		
		
		### Busqueda por rango de tiempo
		if($in{'from_time'} or $in{'to_time'}){
			$in{'from_time'} 	= "00:00:00"	if !$in{'from_time'};
			$in{'to_time'} 		= "23:59:59"	if !$in{'to_time'};
			
			$add_filters .= " AND sl_orders.Time BETWEEN '$in{'from_time'}' AND '$in{'to_time'}'";
		}
		
		### Si es busqueda por id_admin_user 
		$add_filters .= "AND sl_orders.ID_admin_users = ".int($in{'id_admin_users'})." "	if $in{'id_admin_users'};
		
		
		### Si es busqueda por id_products
		if($in{'id_products'}){			
			$info_oprod = " AND 0 < (SELECT COUNT(DISTINCT ID_orders) FROM sl_orders_products WHERE ID_orders = sl_orders.ID_orders AND RIGHT(ID_products,6) = '".int($in{'id_products'})."' AND Status = 'Active') ";
		}
		
		my $fname   = 'sales_by_day'.$cfg{'app_title'}.'.csv';
		$fname =~ s/\s/_/g;
		
		my $strHeader = "No Ped,F Pedido,Estado,Clnt Venta,Cliente,Moneda,Linea,Estado,ID Prod,Descr,Cant Program,Precio,UM Envío,Importe Tns,Tipo de documento";
		my $join = ($in{'winvoice'})?'INNER ':'LEFT ';

		my ($sth) = &Do_SQL("SELECT COUNT(*) FROM( 
			SELECT COUNT(*) FROM sl_orders 
			$join JOIN cu_invoices_lines USING(ID_orders)
			$join JOIN cu_invoices USING(ID_invoices)
			WHERE 1 AND cu_invoices.Status='Certified' AND sl_orders.Date BETWEEN  '$in{'from_date'}' AND '$in{'to_date'}' $add_filters 
			GROUP BY ID_orders)orders;");
		my ($total) = $sth->fetchrow();


		if($total) {

			print "Content-type: application/octetstream\n";
			print "Content-disposition: attachment; filename=$fname\n\n";
			print "$strHeader\r\n";


			my $sth2 = &Do_SQL("SELECT DISTINCT
								ID_orders
								,sl_orders.Date
								,sl_orders.ID_admin_users
								,sl_orders.Status
								,sl_orders.ID_customers
								,IF(sl_customers.company_name IS NOT NULL,company_name,CONCAT(sl_customers.FirstName,' ',sl_customers.Lastname1)) AS CompanyName
								,sl_customers.Currency
								,sl_orders_products.Status as LineStatus
								,if(sl_orders_products.Related_ID_products is null,sl_orders_products.ID_products,sl_orders_products.Related_ID_products) as ID_products
								,sl_skus.UPC
								,sl_orders_products.Quantity
								,sl_orders_products.SalePrice / sl_orders_products.Quantity AS SalePrice
								,sl_orders_products.Tax
								,'PZA' as UM
								,SalePrice as Total
								,cu_invoices.invoice_type
								FROM sl_orders
								$join JOIN cu_invoices_lines USING(ID_orders)
								$join JOIN cu_invoices USING(ID_invoices)
								LEFT JOIN sl_zipcodes ON sl_orders.shp_Zip = sl_zipcodes.ZipCode
								LEFT JOIN sl_zipdma ON sl_zipdma.ZipCode = sl_zipcodes.ZipCode
								LEFT JOIN sl_salesorigins on (sl_orders.ID_salesorigins=sl_salesorigins.ID_salesorigins)
								LEFT JOIN sl_customers ON sl_customers.ID_customers=sl_orders.ID_customers
								INNER JOIN sl_orders_products USING(ID_orders)
								INNER JOIN sl_skus ON Related_ID_products = ID_sku_products
								WHERE 1 AND cu_invoices.Status='Certified'
								AND sl_orders.Date BETWEEN '$in{'from_date'}' AND '$in{'to_date'}'
								AND sl_orders.Status NOT IN('System Error','Converted') $add_filters
								GROUP BY ID_orders
								ORDER BY sl_orders.Date,sl_orders.Time,ID_orders, sl_orders_products.ID_orders_products;");

			my $records = 0;
			my $actual = 0;
			my $line = 1;
			while ($rec = $sth2->fetchrow_hashref()) {

				if($rec->{'ID_orders'} == $actual) {
					$linea++;
				}else{
					$linea = 1;
					$actual = $rec->{'ID_orders'}; 
				}
				
				my $pname;
				if (int($rec->{'ID_products'}) >= 400000000 and int($rec->{'ID_products'}) < 500000000){
					$pname = load_name('sl_parts','ID_parts',($rec->{'ID_products'} - 400000000),'Name');
				}elsif (int($rec->{'ID_products'}) >= 500000000 and int($rec->{'ID_products'}) < 600000000){
					$pname = load_name('sl_noninventory','ID_noninventory',($rec->{'ID_products'} - 500000000),'Name');
				}elsif (int($rec->{'ID_products'}) >= 600000000){
					$pname = load_name('sl_services','ID_services',($rec->{'ID_products'} - 600000000),'Name');
				}else{
					$pname = load_name('sl_products','ID_products',($rec->{'ID_products'} - 100000000),'Name');
				}

				$records++;

				if (lc($rec->{'invoice_type'}) eq 'ingreso'){
					$t_docto = 'Factura';
				}elsif (lc($rec->{'invoice_type'}) eq 'egreso'){
					$t_docto = 'Nota de credito';
				}
				my $strout = qq|"$rec->{'ID_orders'}","$rec->{'Date'}","$rec->{'Status'}","$rec->{'ID_customers'}","$rec->{'CompanyName'}","$rec->{'Currency'}","$linea","$rec->{'LineStatus'}","$rec->{'UPC'}","$pname","$rec->{'Quantity'}","$rec->{'SalePrice'}","$rec->{'UM'}","$rec->{'Total'}","$t_docto"\r\n|;

				print $strout;
			}
			&auth_logging('report_view','');
			return;

		}
	}
	
	print "Content-type: text/html\n\n";
	print &build_page('rep_bi_salesday.html');

}


#############################################################################
#############################################################################
#   Function: rep_bi_wholesale
#
#       Es: Reporte Excel para Ordenes Wholesale
#       En: 
#
#
#    Created on: 2013/06/17
#
#    Author: _Roberto Barcenas_
#
#    Modifications:
#
#        - Modified on ** by _Roberto Barcenas_ : 
#
#   Parameters:
#
#      - 
#      -   
#
#  Returns:
#
#      - 
#
#   See Also:
#
#
sub rep_bi_wholesale {
#############################################################################
#############################################################################

	if($in{'action'}) {

		############################################
		############################################
		############################################
		#######
		####### Export File
		#######
		############################################
		############################################
		############################################

		my ($query);
		my $moddate = $in{'posteddate'} ? 'PostedDate' : 'Date';

		## Filter by Date
		if ($in{'from_date'}){
			$query .= " AND sl_orders." .$moddate." >= '$in{'from_date'}' ";
		}
		
		$in{'to_date'}	= &get_sql_date() if !$in{'to_date'};
		if ($in{'to_date'}){
			$query .= " AND sl_orders.Date <= '$in{'to_date'}' ";
		}

		## Filter by User
		if ($in{'type'}){
			$in{'type'} =~ s/\|/','/g;		
			$query .= " AND sl_customers.type IN ('$in{'type'}') ";
		}
		$in{'user_type'} =~ s/','/\|/g;

		my ($sth) = &Do_SQL("SELECT COUNT(*) FROM sl_orders INNER JOIN sl_customers USING(ID_customers) WHERE 1 $query AND sl_orders.Status != 'System Error';");
		$va{'matches'} = $sth->rows();

		if ($va{'matches'}>0) {

			my $cname = lc($cfg{'company_name'});
			$cname =~ s/\s/_/g;
			my $fname =  $cname. '_wholesale_' . &get_date();
			chop($fname);

			#print "Content-type: text/html\n\n";
			print "Content-type: application/octet-stream\n";
			print "Content-disposition: attachment; filename=$fname.csv\n\n";
			print "ID Orden,OrderDate,Posted Date,Product,Price,Quantity,Total,Customer\n";

			my ($sth) = &Do_SQL("SELECT ID_orders,sl_orders.ID_customers,sl_orders.Date,PostedDate,CONCAT(FirstName,' ',Lastname1)AS CName FROM sl_orders INNER JOIN sl_customers USING(ID_customers) WHERE 1 $query AND sl_orders.Status != 'System Error' ORDER BY ID_orders;");
			while( my($id_orders, $id_customers, $date, $posteddate, $cname) = $sth->fetchrow()) {

				my ($sth) = &Do_SQL("SELECT ID_products,Related_ID_Products,SalePrice/Quantity,Quantity,SalePrice FROM sl_orders_products WHERE ID_orders = '$id_orders' AND Status NOT IN('Order Cancelled','Inactive') ORDER BY ID_orders_products");
				while(my ($idp, $id_related, $unit_price, $qty, $saleprice) = $sth->fetchrow()) {

					my $pname;
					if(!$id_related){

						if(substr($idp,0,1) == 6){

							$idp  = $idp - 600000000;
							$pname = &load_name('sl_services','ID_services',$idp,'Name');

						}else{

							$idp = substr($idp,-6);
							$pname = &load_name('sl_products','ID_products',$idp,'Name');

						}

						
					}elsif(substr($id_related,0,1) == 4){
						$idp = $id_related - 400000000;
						$pname = &load_name('sl_parts','ID_parts',$idp,'Name');
					}else{
						$idp  = $id_related - 600000000;
						$pname = &load_name('sl_services','ID_services',$idp,'Name');
					}

					print " \"$id_orders\",\"$date\",\"$posteddate\",\"$pname ($idp)\",\"$unit_price\",\"$qty\",\"$saleprice\",\"$cname ($id_customers)\"\n";

				}

			}

			return;
		}

	}
	
	print "Content-type: text/html\n\n";
	print &build_page('rep_bi_wholesale.html');

}


#############################################################################
#############################################################################
#   Function: rep_bi_indicators
#
#       Es: Reporte Excel Indicadores 
#       En: 
#
#
#    Created on: 2013/09/23
#
#    Author: __
#
#    Modifications:
#
#        - Modified on ** by __ : 
#
#   Parameters:
#
#      - 
#      -   
#
#  Returns:
#
#      - 
#
#   See Also:
#
#
sub rep_bi_indicators {
#############################################################################
#############################################################################

	if($in{'action'}) {

		my ($query_list);
		my $maxprod=1;
		my $info_user =	'';
		my $info_pprod = '';
		my $info_oprod = '';
		my $info_time = '';
		my $strout = '';
				
		my $sql_between = '';
		
		my $add_filters='';
		
		###### Busqueda por rango de fecha
		#$in{'from_date'} = &get_sql_date() if !$in{'from_date'};
		$in{'from_date'} = &filter_values($in{'from_date'});
		$in{'to_date'} = &filter_values($in{'to_date'});
		
		my @from_date_array = split /-/,$in{'from_date'};
		my @to_date_array = split /-/,$in{'to_date'};
		if ($in{'to_date'} and $in{'from_date'}) {
			#$sql_between = "AND aux_table.invoices_date BETWEEN '$in{'from_date'}' AND '$in{'to_date'}'";
			$sql_between = "AND YEAR(aux_table.invoices_date)=$from_date_array[0] AND MONTH(aux_table.invoices_date) BETWEEN $from_date_array[1] AND $to_date_array[1]";
			
		} elsif ($in{'from_date'}) {
			$sql_between =  "AND YEAR(aux_table.invoices_date)=$from_date_array[0] AND MONTH(aux_table.invoices_date) >= '$from_date_array[1]'";
		} elsif ($in{'to_date'}) {
			$sql_between =  "AND YEAR(aux_table.invoices_date)=$to_date_array[0] AND MONTH(aux_table.invoices_date) <= '$to_date_array[1]'";
		}
		
		
		my $fname   = 'rep_bi_indicators_'.$cfg{'app_title'}.'.csv';
		$fname =~ s/\s/_/g;
		
		
		
		my $strHeader = "Mes,PLevantados,\$,COD,\$COD,TDC,\$TDC,PSurtidos,\$,COD,\$COD,TDC,\$TDC,PEntregados,\$,COD,\$COD,TDC,\$TDC";
		
		# *********************************************************************************************************
		# *********************************************************************************************************

		
		
		# *********************************************************************************************************
		# *********************************************************************************************************
		
		my ($total) = 1;
		
		if($total) {
			#print "Content-type: text/html\n\n";
			print "Content-type: application/octetstream\n";
			print "Content-disposition: attachment; filename=$fname\n\n";
			print "$strHeader\r\n";
			
			my $records = 0;
			
			
			
			my ($sth) = &Do_SQL("SELECT *
						FROM (
							-- 9024180
							select 
								count(*), 
								invoices_date,
								ID_orders,
								payment_type,
							-- sum(quantity), 
							-- (SUM((unit_price * quantity)) + sum(tax) - sum(discount)) total , 
							-- sum(discount),
								IF(payment_type = 'Credit-Card',(SUM((unit_price * quantity)) + sum(tax) - sum(discount)),0.00) cc_amount, 
								IF(payment_type = 'COD',(SUM((unit_price * quantity)) + sum(tax) - sum(discount)),0.00) cod_amount, 
								IF(payment_type = 'Referenced Deposit',(SUM((unit_price * quantity)) + sum(tax) - sum(discount)),0.00)  rd_amount,
								IF(payment_type = '' AND ID_orders < 9000000,(SUM((unit_price * quantity)) + sum(tax) - sum(discount)),0.00) cm_amount,
								'invoices' source
							from(
						
									SELECT 
										`sl_orders`.`ID_orders`
										,`sl_orders`.`Date` orders_date
										,`cu_invoices`.`doc_date` invoices_date
										
										,`cu_invoices_lines`.`quantity`
										,`cu_invoices_lines`.`unit_price`
										,`cu_invoices_lines`.`discount`
										,`cu_invoices_lines`.`tax_rate`
										,`cu_invoices_lines`.`tax`
										,`invoice_type`
										,`cu_invoices`.`Currency`
										,`sl_orders_products`.`Cost`
										,`cu_invoices`.`Status`
										,
										sl_orders.Ptype payment_type
									FROM
										cu_invoices_lines
										INNER JOIN
										cu_invoices USING(ID_invoices)
										INNER JOIN
										sl_orders ON(sl_orders.ID_orders = cu_invoices_lines.ID_orders)
										LEFT JOIN
										sl_orders_products ON (sl_orders_products.ID_orders_products = cu_invoices_lines.ID_orders_products 
										AND
										cu_invoices_lines.ID_creditmemos
										IS NULL)
										INNER JOIN
										sl_customers
										ON
										sl_customers.ID_customers=sl_orders.ID_customers
										WHERE 1
										AND
										cu_invoices.Status='Certified'
										AND
										sl_orders.Status
										NOT IN
										('System Error','Converted')
								UNION ALL
									SELECT 
										
													sl_creditmemos.ID_creditmemos
										ID_orders
										,
										sl_creditmemos.Date
										orders_date
										,
										`cu_invoices`.`doc_date`
										invoices_date
										,
										
										`cu_invoices_lines`.`quantity`
										,
										`cu_invoices_lines`.`unit_price` * (-1)
										,
										`cu_invoices_lines`.`discount` * (-1)
										,
										`cu_invoices_lines`.`tax_rate`
										,
										`cu_invoices_lines`.`tax` * (-1)
										,
										`invoice_type`
										,
										`cu_invoices`.`Currency`
										,
										sl_creditmemos_products.Cost
										,
										`cu_invoices`.`Status`
										
										,
										'' payment_type
									FROM
											sl_creditmemos
										INNER
										JOIN
											sl_creditmemos_products
										USING(ID_creditmemos)
										INNER
										JOIN
											cu_invoices_lines
										ON
											cu_invoices_lines.ID_orders_products=sl_creditmemos_products.ID_creditmemos_products
										AND
											cu_invoices_lines.ID_orders=0
										INNER
										JOIN
											cu_invoices USING(ID_invoices)
										INNER
										JOIN
											sl_customers
										ON
											sl_customers.ID_customers=sl_creditmemos.ID_customers
									WHERE 1
									AND
										cu_invoices.Status='Certified'
							) invoices 
							WHERE
							1
							-- AND ID_orders = 9024180
							 GROUP BY ID_orders
						
							UNION ALL
						
							SELECT 
							COUNT(*),
							`sl_orders`.`Date`,
							`sl_orders`.`ID_orders`, 
							`sl_orders`.`PType`,
						
						
							-- ((OrderNet-OrderDisc)*OrderTax), 
							-- `sl_orders_products`.`Quantity`, 
							-- (sl_orders_products.SalePrice / sl_orders_products.Quantity), 
							-- ((OrderNet + SUM(sl_orders_products.Tax)) - SUM(sl_orders_products.Discount)) total,
								IF(sl_orders.PType = 'Credit-Card',((OrderNet + SUM(sl_orders_products.Tax)) - SUM(sl_orders_products.Discount) + SUM(sl_orders_products.Shipping) + SUM(sl_orders_products.ShpTax)),0.00) cc_amount, 
								IF(sl_orders.PType = 'COD',((OrderNet + SUM(sl_orders_products.Tax)) - SUM(sl_orders_products.Discount) + SUM(sl_orders_products.Shipping) + SUM(sl_orders_products.ShpTax)),0.00) cod_amount, 
								IF(sl_orders.PType = 'Referenced Deposit',((OrderNet + SUM(sl_orders_products.Tax)) - SUM(sl_orders_products.Discount) + SUM(sl_orders_products.Shipping) + SUM(sl_orders_products.ShpTax)),0.00)  rd_amount,
								 0.00 cm_amount,
								'requisitions' source
						
							FROM sl_orders
							INNER JOIN
							sl_orders_products
							USING(ID_orders)
							INNER JOIN
							sl_customers
							ON
							sl_customers.ID_customers=sl_orders.ID_customers
							LEFT JOIN
							sl_salesorigins
							USING(ID_salesorigins) WHERE 1
							AND
							sl_orders.Status
							NOT
							IN('System
							Error','Converted')
							AND
							sl_orders_products.Status='Active' 
							-- AND 
							--  sl_orders.ID_orders = 9000006
							GROUP BY sl_orders.ID_orders
						
							UNION ALL
						
							SELECT
								COUNT(*),
								sl_warehouses_batches_orders.Date,
								`sl_orders`.`ID_orders`,
							-- `sl_warehouses_batches`.`ID_warehouses_batches`, 
							-- `sl_warehouses_batches`.`Date`, 
								`sl_orders`.`Ptype`, 
								 
								
							-- `sl_orders`.`Date`, 
							-- `sl_orders`.`Status`, 
							-- `sl_warehouses_batches`.`Status`,
							-- `sl_orders_products`.`ID_products`, 
							-- `sl_orders_parts`.`ShpDate`, 
							-- (SUM(sl_orders_products.SalePrice) - SUM(sl_orders_products.Discount) + SUM(sl_orders_products.Shipping) + SUM(sl_orders_products.Tax) + SUM(sl_orders_products.ShpTax)) total,
								IF(sl_orders.PType = 'Credit-Card',(SUM(sl_orders_products.SalePrice) - SUM(sl_orders_products.Discount) + SUM(sl_orders_products.Shipping) + SUM(sl_orders_products.Tax) + SUM(sl_orders_products.ShpTax)),0.00) cc_amount, 
								IF(sl_orders.PType = 'COD',(SUM(sl_orders_products.SalePrice) - SUM(sl_orders_products.Discount) + SUM(sl_orders_products.Shipping) + SUM(sl_orders_products.Tax) + SUM(sl_orders_products.ShpTax)),0.00) cod_amount, 
								IF(sl_orders.PType = 'Referenced Deposit',(SUM(sl_orders_products.SalePrice) - SUM(sl_orders_products.Discount) + SUM(sl_orders_products.Shipping) + SUM(sl_orders_products.Tax) + SUM(sl_orders_products.ShpTax)),0.00)  rd_amount,
								0.00 cm_amount,
								'consignments' source
						
							FROM sl_orders
								INNER JOIN
									sl_orders_products
								ON
									sl_orders.ID_orders=sl_orders_products.ID_orders
								LEFT JOIN
									sl_skus_parts
								ON
									sl_skus_parts.ID_sku_products=sl_orders_products.ID_products
								INNER JOIN
									sl_parts
								ON
									sl_parts.ID_parts=sl_skus_parts.ID_parts
								LEFT JOIN
									sl_orders_parts
								ON
									sl_skus_parts.ID_parts=sl_orders_parts.ID_parts
								AND
								sl_orders_parts.ID_orders_products=sl_orders_products.ID_orders_products
								INNER JOIN
								sl_warehouses_batches_orders
								ON
									sl_orders_products.ID_orders_products=sl_warehouses_batches_orders.ID_orders_products
								INNER JOIN
									sl_warehouses_batches
								ON
									sl_warehouses_batches.ID_warehouses_batches=sl_warehouses_batches_orders.ID_warehouses_batches
							 WHERE 1 
							-- AND
							-- sl_orders.ID_orders = 9038842
							GROUP BY sl_orders.ID_orders
							) aux_table
						WHERE 1
						$sql_between
						;");
			
			#my ($req_cntr, $csign_cntr, $inv_cntr) = (0) x 3;
			#
			#my ($req_cod_cntr,$csign_cod_cntr,$inv_cod_cntr) = (0) x 3;
			#my ($req_tdc_cntr,$csign_tdc_cntr,$inv_tdc_cntr) = (0) x 3;
			#
			#my ($req_cod_mny,$csign_cod_mny,$inv_cod_mny) = (0) x 3;
			#my ($req_tdc_mny,$csign_tdc_mny,$inv_tdc_mny) = (0) x 3;
			
			my (%req_cod_cntr,%csign_cod_cntr,%inv_cod_cntr) = () x 3;
			my (%req_tdc_cntr,%csign_tdc_cntr,%inv_tdc_cntr) = () x 3;
			my (%req_codtdc_cntr,%csign_codtdc_cntr,%inv_codtdc_cntr) = () x 3;
			
			my (%req_cod_mny,%csign_cod_mny,%inv_cod_mny) = () x 3;
			my (%req_tdc_mny,%csign_tdc_mny,%inv_tdc_mny) = () x 3;
			my (%req_codtdc_mny,%csign_codtdc_mny,%inv_codtdc_mny) = () x 3;
			
			while ($rec = $sth->fetchrow_hashref()) {
				
				my $year_month = substr ($rec->{'invoices_date'}, 0, 7);
				
				if ($rec->{'source'} eq 'requisitions') {
					$req_cod_cntr{"$year_month"} += ($rec->{'cod_amount'} != 0)?$rec->{'count(*)'}:0;
					$req_tdc_cntr{"$year_month"} += ($rec->{'cc_amount'} != 0)?$rec->{'count(*)'}:0;
					$req_codtdc_cntr{"$year_month"} += $rec->{'count(*)'};
					
					$req_cod_mny{"$year_month"} += ($rec->{'cod_amount'} != 0)?$rec->{'cod_amount'}:0;
					$req_tdc_mny{"$year_month"} += ($rec->{'cc_amount'} != 0)?$rec->{'cc_amount'}:0;
					$req_codtdc_mny{"$year_month"} += ($rec->{'cod_amount'} + $rec->{'cc_amount'});
					
				} elsif ($rec->{'source'} eq 'consignments') {
					$csign_cod_cntr{"$year_month"} += ($rec->{'cod_amount'} != 0)?$rec->{'count(*)'}:0;
					$csign_tdc_cntr{"$year_month"} += ($rec->{'cc_amount'} != 0)?$rec->{'count(*)'}:0;
					$csign_codtdc_cntr{"$year_month"} += $rec->{'count(*)'};
					
					$csign_cod_mny{"$year_month"} += ($rec->{'cod_amount'} != 0)?$rec->{'cod_amount'}:0;
					$csign_tdc_mny{"$year_month"} += ($rec->{'cc_amount'} != 0)?$rec->{'cc_amount'}:0;
					$csign_codtdc_mny{"$year_month"} += ($rec->{'cod_amount'} + $rec->{'cc_amount'});
				} elsif ($rec->{'source'} eq 'invoices') {
					#print qq|$rec->{'ID_orders'}, $rec->{'source'}, $rec->{'cm_amount'}, $rec->{'rd_amount'}, $rec->{'cod_amount'}, $rec->{'cc_amount'}|."\r\n";
					#print $rec->{'cc_amount'}."\r\n";
					
					$inv_cod_cntr{"$year_month"} += ($rec->{'cod_amount'} != 0)?$rec->{'count(*)'}:0;
					$inv_tdc_cntr{"$year_month"} += ($rec->{'cc_amount'} != 0)?$rec->{'count(*)'}:0;
					$inv_codtdc_cntr{"$year_month"} += $rec->{'count(*)'};
					
					$inv_cod_mny{"$year_month"} += ($rec->{'cod_amount'} != 0)?$rec->{'cod_amount'}:0;
					$inv_tdc_mny{"$year_month"} += ($rec->{'cc_amount'} != 0)?$rec->{'cc_amount'}:0;
					$inv_codtdc_mny{"$year_month"} += ($rec->{'cod_amount'} + $rec->{'cc_amount'});
					
				}
				
			}

			my %aux_hash = ((scalar keys %req_codtdc_cntr) > 0)?%req_codtdc_cntr:((scalar keys %csign_codtdc_cntr) > 0)?%csign_codtdc_cntr:((scalar keys %inv_codtdc_cntr) > 0)?%inv_codtdc_cntr:();
			
			foreach my $key (sort keys %aux_hash) {
				$strout .= qq|"$key","$req_codtdc_cntr{"$key"}","$req_codtdc_mny{"$key"}","$req_cod_cntr{"$key"}","$req_cod_mny{"$key"}","$req_tdc_cntr{"$key"}","$req_tdc_mny{"$key"}","$csign_codtdc_cntr{"$key"}","$csign_codtdc_mny{"$key"}","$csign_cod_cntr{"$key"}","$csign_cod_mny{"$key"}","$csign_tdc_cntr{"$key"}","$csign_tdc_mny{"$key"}","$inv_codtdc_cntr{"$key"}","$inv_codtdc_mny{"$key"}","$inv_cod_cntr{"$key"}","$inv_cod_mny{"$key"}","$inv_tdc_cntr{"$key"}","$inv_tdc_mny{"$key"}"\r\n|;
			}
			print $strout;
			return;
		} else {
			$va{'message'} = &trans_txt('search_nomatches');
		}
	}
	
	print "Content-type: text/html\n\n";
	print &build_page('rep_bi_indicators.html');
}

#############################################################################
#############################################################################
#   Function: rep_bi_invoicing
#
#       Es: Reporte de Detalle de Facturacion
#       En: Invoicing Detail Report
#
#
#    Created on: 30/09/2013
#
#    Author: Alejandro Diaz
#
#    Modifications:
#
#        - Modified on ** by *** : 
#
#   Parameters:
#
#      - 
#
#  Returns:
#
#
#   See Also:
#
#      <>
#
sub rep_bi_invoicing{
#############################################################################
#############################################################################

	if($in{'action'}){
		my ($query_list);
		my $maxprod=1;
		my $info_user =	'';
		my $info_time = '';
		my $strout = '';
		
		###### Busqueda por rango de fecha
		$in{'from_date'} = &get_sql_date() if !$in{'from_date'};
		$in{'to_date'} = &get_sql_date() if !$in{'to_date'};
		
	#@ivanmiranda
		$add_sql = " AND cu_invoices.doc_date >= '$in{'from_date'} 00:00:00'";
		$add_sql .= " AND cu_invoices.doc_date <= '$in{'to_date'} 23:59:59'";

		#$add_sql = " AND cu_invoices.Date >= DATE('$in{'from_date'}')";
		#$add_sql .= " AND cu_invoices.Date <= DATE('$in{'to_date'}')";
		

		
		### Si es busqueda por id_admin_user 
		# $info_user = "WHERE ID_admin_users = ".int($in{'id_admin_users'})." "	if $in{'id_admin_users'};
		
		my $fname   = 'invoicing_'.$cfg{'app_title'}.'.csv';
		$fname =~ s/\s/_/g;
		
		# my $strHeader = "Invoice,ID_orders,OrderDate,InvoiceDate,Expediter,ID_customers,CustomerName,CustomerType,Grouping,SKU,Name,Category,UPC,Qty,UnitPrice,Discount,TaxRate,TotalNet,Tax,Amount,InvoiceType,Currency,Cost,StatusPrd,status,Origin";
		#my $strHeader = "FACTURA,ID_PEDIDO,FECHA FINALIZACION,FECHA DE FACTURA,UNIDAD NEGOCIO VENTAS,ID CLIENTE,CLIENTE,TIPO CLIENTE,ID PRODUCTO,UPC,SKU,DESCRIPCION,FAMILIA,TIPO DE DOCUMENTO,CANTIDAD,PRECIO UNITARIO,MONTO SIN IVA,MONTO DESCUENTO,SUBTOTAL,% IVA,MONTO IVA,TOTAL,DOCTO,MONEDA,COSTO TOTAL,TASA CAMBIO,COSTO UNITARIO,STATUS PRD,FACTURA ESTATUS,ORIGEN DE VENTA";
		my $strHeader = "UNIDAD NEGOCIO VENTAS,FACTURA,ID_PEDIDO,FECHA DE PEDIDO,FECHA DE FACTURA,FECHA CONTABLE,ID CLIENTE,CLIENTE,FAMILIA,TIPO,ORIGEN DE VENTA,PROPIEDAD,ID PRODUCTO,UPC,SKU,DESCRIPCION,DOCTO,CANTIDAD,PRECIO UNITARIO,MONTO SIN IVA,MONTO DESCUENTO,SUBTOTAL,% IVA,MONTO IVA,TOTAL,C.A.,C.C.,COSTO UNITARIO,COSTO TOTAL,MONEDA,TASA CAMBIO,FACTURA ESTATUS,TIPO CLIENTE,TIPO DE DOCUMENTO,STATUS PRD";

		## Debug only
		 #my $tmp_id_orders = 9544315;
		 #$add_sql = ($tmp_id_orders)? " AND sl_orders.ID_orders IN($tmp_id_orders)":"";

		my ($sth) = &Do_SQL("SELECT
				(concat(doc_serial,doc_num))Invoice
				, ID_orders
				, orders_date
				, invoices_date
				, expediter_fname
				, ID_customers
				, (((IF(company_name!='',company_name,CONCAT(FirstName,' ',Lastname1)))))
				, Type, grouping
				, SKU
				, (if(UPC='',ID_products_out,UPC))
				, quantity
				, (IF(invoice_type='egreso',unit_price*-1,unit_price)) unit_price
				, ((IF(invoice_type='egreso' AND discount>0,discount*-1,discount)))
				, tax_rate
				, ((IF(invoice_type='egreso' AND TotalNet>0,TotalNet*-1,TotalNet)))
				, ((IF(invoice_type='egreso' AND tax>0,tax*-1,tax)))
				, ((IF(invoice_type='egreso' AND Amount>0,Amount*-1,Amount)))
				, invoice_type
				, Currency
				, Cost
				, Cost_Adj
				, StatusPrd
				, Status
				, salesorigin
				, currency_exchange
				, description
				, ID_orders_products
				, ID_products
				, ID_skus_parts
			FROM (
				SELECT
					doc_serial
					, doc_num
					, sl_orders.ID_orders
					, sl_orders.Date orders_date
					, cu_invoices.doc_date invoices_date
					, cu_invoices.expediter_fname
					, sl_orders.ID_customers
					, sl_customers.company_name
					, sl_customers.FirstName
					, sl_customers.Lastname1
					, sl_customers.Lastname2
					, sl_customers.Type
					, sl_orders_products.ID_products as ID_products_out
					, 'Principal' as grouping
					, '' as SKU
					, '' as UPC
					, cu_invoices_lines.quantity
					, cu_invoices_lines.unit_price
					, cu_invoices_lines.discount
					, cu_invoices_lines.tax_rate
					, cu_invoices_lines.tax
					, (cu_invoices_lines.quantity*cu_invoices_lines.unit_price) as TotalNet
					, ((cu_invoices_lines.quantity*cu_invoices_lines.unit_price)+cu_invoices_lines.tax) as Amount
					, invoice_type
					, cu_invoices.Currency
					, '' as Cost
					, '' as Cost_Adj
					, sl_orders.StatusPrd
					, cu_invoices.Status
					, (SELECT Channel FROM sl_salesorigins WHERE sl_salesorigins.ID_salesorigins=sl_orders.ID_salesorigins LIMIT 1) as salesorigin
					, cu_invoices.currency_exchange
					, cu_invoices_lines.description
					, sl_orders_products.ID_orders_products
					, '' AS ID_products
					, '' AS ID_skus_parts
				FROM cu_invoices_lines
				INNER JOIN cu_invoices USING(ID_invoices)
				INNER JOIN sl_orders ON(sl_orders.ID_orders = cu_invoices_lines.ID_orders)
				LEFT JOIN sl_orders_products ON (sl_orders_products.ID_orders_products = cu_invoices_lines.ID_orders_products AND cu_invoices_lines.ID_creditmemos IS NULL)
				INNER JOIN sl_customers ON sl_customers.ID_customers=sl_orders.ID_customers
				WHERE 1
				AND cu_invoices.Status='Certified'
				AND cu_invoices.invoice_type IN('ingreso','egreso')
				AND sl_orders.Status NOT IN ('System Error','Converted')
				$add_sql

				UNION ALL

				SELECT
					doc_serial
					, doc_num
					, sl_orders.ID_orders
					, sl_orders.Date orders_date
					, cu_invoices.doc_date invoices_date
					, cu_invoices.expediter_fname
					, sl_orders.ID_customers
					, sl_customers.company_name
					, sl_customers.FirstName
					, sl_customers.Lastname1
					, sl_customers.Lastname2
					, '' t1
					, sl_orders_products.ID_products as ID_products_out
					, 'Secundario' as grouping
					, if(qry_products.SKU is null, cu_invoices_lines.ID_sku,qry_products.SKU) as SKU
					, if(qry_products.UPC is null, cu_invoices_lines.UPC,qry_products.UPC) as UPC
					, if(qry_products.Qty is null, sl_orders_products.Quantity, qry_products.Qty )
					, cu_invoices_lines.unit_price t3
					, cu_invoices_lines.discount
					, cu_invoices_lines.tax_rate
					, cu_invoices_lines.tax
					, (cu_invoices_lines.quantity*cu_invoices_lines.unit_price) as TotalNet
					, ((cu_invoices_lines.quantity*cu_invoices_lines.unit_price)+cu_invoices_lines.tax) as Amount
					, invoice_type
					, cu_invoices.Currency
					, (
						SELECT sl_orders_parts.Cost
						FROM sl_orders_parts 
						WHERE sl_orders_parts.ID_orders_products = sl_orders_products.ID_orders_products AND sl_orders_parts.ID_parts=qry_products.ID_parts
						GROUP BY sl_orders_parts.ID_orders_products, sl_orders_parts.ID_parts
					)Cost
					, (
						SELECT sl_orders_parts.Cost_Adj
						FROM sl_orders_parts 
						WHERE sl_orders_parts.ID_orders_products = sl_orders_products.ID_orders_products AND sl_orders_parts.ID_parts=qry_products.ID_parts
						GROUP BY sl_orders_parts.ID_orders_products, sl_orders_parts.ID_parts
					)Cost_Adj
					, sl_orders.StatusPrd
					, cu_invoices.Status
					, (SELECT Channel FROM sl_salesorigins WHERE sl_salesorigins.ID_salesorigins=sl_orders.ID_salesorigins LIMIT 1) as salesorigin
					, cu_invoices.currency_exchange
					, cu_invoices_lines.description
					, sl_orders_products.ID_orders_products
					, qry_products.ID_products
					, qry_products.ID_skus_parts
				FROM cu_invoices_lines
				INNER JOIN cu_invoices USING(ID_invoices)
				INNER JOIN sl_orders ON (sl_orders.ID_orders = cu_invoices_lines.ID_orders)
				LEFT JOIN sl_orders_products ON (sl_orders_products.ID_orders_products = cu_invoices_lines.ID_orders_products)
				INNER JOIN sl_customers ON sl_customers.ID_customers=sl_orders.ID_customers
				LEFT JOIN (
					SELECT a.ID_sku_products as ID_products, a.ID_parts, (a.ID_parts+400000000) as SKU, b.UPC, a.Qty, a.ID_skus_parts
					FROM sl_skus_parts a
					LEFT JOIN sl_skus b ON a.ID_parts=b.ID_products
					GROUP BY a.ID_skus_parts
					ORDER BY a.ID_sku_products asc
				) qry_products ON sl_orders_products.ID_products=qry_products.ID_products
				
				WHERE 1
				AND cu_invoices.Status='Certified'
				AND cu_invoices.invoice_type IN('ingreso','egreso')
				AND sl_orders.Status NOT IN ('System Error','Converted')
				AND sl_orders_products.ID_products<=600000000
				$add_sql

				UNION ALL
				
				-- Credit memos 
				SELECT
					doc_serial
					, doc_num
					,`sl_creditmemos`.`ID_creditmemos` as ID_orders
					,`sl_creditmemos`.`Date` as orders_date
					,`cu_invoices`.`doc_date` invoices_date
					,`cu_invoices`.`expediter_fname`
					,`sl_creditmemos`.`ID_customers`
					,sl_customers.company_name
					,sl_customers.FirstName
					,sl_customers.Lastname1
					,sl_customers.Lastname2
					,`sl_customers`.`Type`
					,sl_creditmemos_products.ID_products as ID_products_out
					,'Principal' as grouping
					,if(qry_products.SKU is null, cu_invoices_lines.ID_sku,qry_products.SKU) as SKU
					,if(qry_products.UPC is null, cu_invoices_lines.UPC,qry_products.UPC) as UPC
					,`cu_invoices_lines`.`quantity`
					,`cu_invoices_lines`.`unit_price`
					,`cu_invoices_lines`.`discount`
					,`cu_invoices_lines`.`tax_rate`
					,`cu_invoices_lines`.`tax`
					,(`cu_invoices_lines`.`quantity`*`cu_invoices_lines`.`unit_price`)+sl_creditmemos_products.Shipping as TotalNet
					,((`cu_invoices_lines`.`quantity`*`cu_invoices_lines`.`unit_price`)+`cu_invoices_lines`.`tax`+sl_creditmemos_products.Shipping)-`cu_invoices_lines`.`discount` as Amount
					,`invoice_type`
					,`cu_invoices`.`Currency`
					, sl_creditmemos_products.Cost
					, '' asCost_Adj
					,'' as StatusPrd
					,`cu_invoices`.`Status`
					,(SELECT channel FROM sl_salesorigins WHERE sl_salesorigins.ID_salesorigins=sl_orders.ID_salesorigins LIMIT 1) AS salesorigin
					, cu_invoices.currency_exchange
					, cu_invoices_lines.description
					, sl_creditmemos_products.ID_creditmemos_products as ID_orders_products
					, '' AS ID_products
					, qry_products.ID_skus_parts
				FROM cu_invoices_lines
				INNER JOIN cu_invoices USING(ID_invoices)
				INNER JOIN sl_creditmemos ON(sl_creditmemos.ID_creditmemos = cu_invoices_lines.ID_creditmemos)
				INNER JOIN sl_creditmemos_products ON (sl_creditmemos.ID_creditmemos = sl_creditmemos_products.ID_creditmemos and sl_creditmemos_products.id_creditmemos_products=cu_invoices_lines.id_orders_products)
				INNER JOIN sl_customers ON sl_customers.ID_customers=sl_creditmemos.ID_customers
				left join (
					SELECT a.ID_sku_products as ID_products, a.ID_parts, (a.ID_parts+400000000) as SKU, b.UPC, a.Qty, a.ID_skus_parts
					FROM sl_skus_parts a
					LEFT JOIN sl_skus b ON a.ID_parts=b.ID_products
					GROUP BY a.ID_skus_parts
					ORDER BY a.ID_sku_products asc
				) qry_products on sl_creditmemos_products.ID_products=qry_products.ID_products
				LEFT JOIN sl_creditmemos_payments ON (sl_creditmemos.ID_creditmemos = sl_creditmemos_payments.ID_creditmemos)
				LEFT JOIN sl_orders ON (sl_orders.ID_orders = sl_creditmemos_payments.ID_orders)
				WHERE 1
				AND cu_invoices.Status='Certified'
				AND cu_invoices.invoice_type IN('ingreso','egreso')
				$add_sql
			) c 
			WHERE 1 
			ORDER BY ID_orders, invoices_date ASC, Invoice ASC, ID_orders_products, ID_skus_parts
			");
	#@ivanmiranda
	#ORDER BY ID_orders, Invoice ASC, ID_orders_products, ID_skus_parts
		if ($sth->rows() > 0){
			
		# 	$info_time =~	s/$txt_needle/$txt_replace/; 
			#print "Content-type: text/html\n";
			print "Content-type: application/octetstream\n";
			print "Content-disposition: attachment; filename=$fname\n\n";
			print "$strHeader\r\n";

			my $gtempo = '';
			my $last_product=0;

			$docto_anterior = '';
		
			while(my ($Invoice,$ID_orders,$OrderDate,$InvoiceDate,$Expediter,$ID_customers,$CustomerName,$CustomerType,$Grouping,$SKU,$UPC,$Qty,$UnitPrice,$Discount,$TaxRate,$TotalNet,$Tax,$Amount,$InvoiceType,$Currency,$Cost,$Cost_Adj,$StatusPrd,$status,$Origin,$currency_exchange,$description, $id_orders_products, $id_products, $id_skus_parts) = $sth->fetchrow){

				my $strout = '';
				my $sku_name = '';
				
				my ($part_name, $part_model);
				$description =~ s/^\s*(.*?)\s*$/$1/;
				$UPC =~ s/^\s*(.*?)\s*$/$1/;
				$part_name = $description;
				
				$categories='';
				if ($SKU >= 400000000) {
					my ($sth) = &Do_SQL("SELECT Name, (SELECT Title FROM sl_categories WHERE ID_categories=(SELECT ID_categories FROM sl_parts WHERE ID_parts='".($SKU-400000000)."')) FROM sl_parts WHERE ID_parts='".($SKU-400000000)."';");
					($part_name, $categories) = $sth->fetchrow_array;
				}
				if ($SKU >= 600000000) {					
					my ($sth) = &Do_SQL("SELECT Name FROM sl_services WHERE ID_services='".($SKU-600000000)."';");
					($part_name) = $sth->fetchrow_array;
				}

				#@ivanmiranda
				#Nueva columna: Categoria
				$_category = '';
				if(length($id_products) > 0) {
					$_temp = substr($id_products,length($id_products)-6);
					$_query ="select cat.Title
						from sl_products_properties pct
						inner join sl_properties cat using(ID_properties)
						where pct.id_products='$_temp';";
					#&cgierr($_query);
					my ($sth) = &Do_SQL($_query);
					($_category) = $sth->fetchrow_array;
				}



				if ($Grouping eq 'Principal' and $UPC < 600000000 and substr($UPC,0,1) ne 'P' and substr($UPC,0,1) ne 'S' and substr($UPC,0,1) ne '0' and uc($part_name) ne 'ENVIO Y MANEJO' and $UPC ne '4203727' and $UPC ne '4203766' and $UPC ne '4203721' and $UPC ne '502149' and $UPC ne '502208' and $UPC ne 'P13323'  and $UPC ne '14015626' and $UPC ne '785697-07' and $UPC ne '12471342' and $UPC ne '307090002' and $UPC ne '307090003' and $UPC ne '308010006' and $UPC ne '309010005' and $UPC ne '309010008' and $UPC ne '400002005') {
					$UnitPrice = '0';
					$Discount = '0';
					$TaxRate = '';
					$TotalNet = '0';
					$Tax = '0';
					$Amount = '0';
					$last_product = '';
				}else{
					# $UnitPrice = $last_product.'<-'.$id_orders_products;

					# Secundario
					if ($last_product == $id_orders_products){
						if($docto_anterior eq $Invoice){
							$UnitPrice = '0';
							$Discount = '0';
							$TaxRate = '';
							$TotalNet = '0';
							$Tax = '0';
							$Amount = '0';
						}else{
							# Linea con precios
							$UnitPrice = ($Qty > 0)? $UnitPrice / $Qty : '';
							$docto_anterior = $Invoice;
						}
					}else{
						# Linea con precios
						$docto_anterior = $Invoice;
						$UnitPrice = ($Qty > 0)? $UnitPrice / $Qty : '';
					}
				}

				if (lc($InvoiceType) eq 'ingreso'){
					$docto = 'Factura';
				}elsif (lc($InvoiceType) eq 'egreso'){
					$docto = 'Nota de credito';
					$Cost *= (-1);
				}
				#Blank Vars
				my ($Tipo,$cu,$ca,$cc);
				$cu = $Cost;
				$ca = $Cost_Adj;
				$cc = 0; # ADG->Aun no se conoce este dato en el Sistema

				#$strout .= qq|"$Invoice","$ID_orders","$OrderDate","$InvoiceDate","$Expediter","$ID_customers","$CustomerName","$CustomerType","$Grouping","$UPC","$SKU","$part_name","$categories","$InvoiceType","$Qty","$UnitPrice","$TotalNet","$Discount","|.($TotalNet-$Discount).qq|","$TaxRate","$Tax","$Amount","$docto","$Currency","|.($Cost*$Qty).qq|","$currency_exchange","$Cost","$StatusPrd","$status","$Origin"\r\n|;
				if($InvoiceType eq 'egreso'){
					$strout .= qq|"$Expediter","$Invoice","$ID_orders","$OrderDate","$InvoiceDate","$InvoiceDate","$ID_customers","$CustomerName","$categories","$Tipo","$Origin","$_category","$Grouping","$UPC","$SKU","$part_name","$docto","$Qty","$UnitPrice","$TotalNet","$Discount","|.($TotalNet-$Discount).qq|","$TaxRate","$Tax","|.$Amount.qq|","$ca","$cc","$Cost","|.($Cost*$Qty).qq|","$Currency","$currency_exchange","$status","$CustomerType","$InvoiceType","$StatusPrd"\r\n|;
				}else {
					$strout .= qq|"$Expediter","$Invoice","$ID_orders","$OrderDate","$InvoiceDate","$InvoiceDate","$ID_customers","$CustomerName","$categories","$Tipo","$Origin","$_category","$Grouping","$UPC","$SKU","$part_name","$docto","$Qty","$UnitPrice","$TotalNet","$Discount","|.($TotalNet-$Discount).qq|","$TaxRate","$Tax","|.(($TotalNet-$Discount)+$Tax).qq|","$ca","$cc","$Cost","|.($Cost*$Qty).qq|","$Currency","$currency_exchange","$status","$CustomerType","$InvoiceType","$StatusPrd"\r\n|;
				}
				
				print $strout;

				# Grouping Temporal
				$gtempo = $Grouping;

				$last_product = $id_orders_products if ($Grouping ne 'Principal');
			}
			# 	&auth_logging('report_view','');
			return;
		}else{
			$va{'message'} = &trans_txt('search_nomatches');
		}
	}
	
	print "Content-type: text/html\n\n";
	print &build_page('rep_bi_invoicing.html');
}

#############################################################################
#############################################################################
#   Function: rep_bi_invoicing_v2
#
#       Es: Reporte de Detalle de Facturacion
#       En: Invoicing Detail Report
#
#
#    Created on: 30/09/2013
#
#    Author: Alejandro Diaz
#
#    Modifications:
#
#        - Modified on ** by *** : Gilberto QC 
#
#   Parameters:
#
#      - 
#
#  Returns:
#
#
#   See Also:
#
#      <>
#
sub rep_bi_invoicing_v2{
#############################################################################
#############################################################################

	if($in{'action'}){
		my ($query_list);
		my $maxprod=1;
		my $info_user =	'';
		my $info_time = '';
		my $strout = '';
		
		###### Busqueda por rango de fecha
		$in{'from_date'} = &get_sql_date() if !$in{'from_date'};
		$in{'to_date'} = &get_sql_date() if !$in{'to_date'};
		
		$add_sql = " AND cu_invoices.doc_date >= '$in{'from_date'} 00:00:00'";
		$add_sql .= " AND cu_invoices.doc_date <= '$in{'to_date'} 23:59:59'";

		#$add_sql = " AND cu_invoices.Date >= DATE('$in{'from_date'}')";
		#$add_sql .= " AND cu_invoices.Date <= DATE('$in{'to_date'}')";
				
		### Si es busqueda por id_admin_user 
		# $info_user = "WHERE ID_admin_users = ".int($in{'id_admin_users'})." "	if $in{'id_admin_users'};
		
		my $fname   = 'invoicing_'.$cfg{'app_title'}.'.csv';
		$fname =~ s/\s/_/g;
		
		# my $strHeader = "Invoice,ID_orders,OrderDate,InvoiceDate,Expediter,ID_customers,CustomerName,CustomerType,Grouping,SKU,Name,Category,UPC,Qty,UnitPrice,Discount,TaxRate,TotalNet,Tax,Amount,InvoiceType,Currency,Cost,StatusPrd,status,Origin";
		#my $strHeader = "FACTURA,ID_PEDIDO,FECHA FINALIZACION,FECHA DE FACTURA,UNIDAD NEGOCIO VENTAS,ID CLIENTE,CLIENTE,TIPO CLIENTE,ID PRODUCTO,UPC,SKU,DESCRIPCION,FAMILIA,TIPO DE DOCUMENTO,CANTIDAD,PRECIO UNITARIO,MONTO SIN IVA,MONTO DESCUENTO,SUBTOTAL,% IVA,MONTO IVA,TOTAL,DOCTO,MONEDA,COSTO TOTAL,TASA CAMBIO,COSTO UNITARIO,STATUS PRD,FACTURA ESTATUS,ORIGEN DE VENTA";
		my $strHeader = "UNIDAD NEGOCIO VENTAS,FACTURA,ID_PEDIDO,FECHA DE PEDIDO,FECHA DE FACTURA,FECHA CONTABLE,ID CLIENTE,CLIENTE,FAMILIA,TIPO,ORIGEN DE VENTA,ID PRODUCTO,UPC,SKU,DESCRIPCION,DOCTO,CANTIDAD,PRECIO UNITARIO,MONTO SIN IVA,MONTO DESCUENTO,SUBTOTAL,% IVA,MONTO IVA,TOTAL,C.A.,COSTO UNITARIO,COSTO TOTAL,MONEDA,TASA CAMBIO,FACTURA ESTATUS,TIPO CLIENTE,METODO DE PAGO";

		## Debug only
		#my $tmp_id_orders = 9544315;
		#$add_sql = ($tmp_id_orders)? " AND sl_orders.ID_orders IN($tmp_id_orders)":"";

		my ($sth) = &Do_SQL("SELECT
				(concat(doc_serial,doc_num))Invoice
				, ID_orders
				, orders_date
				, invoices_date
				, expediter_fname
				, ID_customers
				, (((IF(company_name!='',company_name,CONCAT(FirstName,' ',Lastname1)))))
				, Type, grouping
				, SKU
				, (if(UPC='',ID_products_out,UPC))
				, quantity
				, (IF(invoice_type='egreso',unit_price*-1,unit_price)) unit_price
				, ((IF(invoice_type='egreso' AND discount>0,discount*-1,discount)))
				, tax_rate
				, ((IF(invoice_type='egreso' AND TotalNet>0,TotalNet*-1,TotalNet)))
				, ((IF(invoice_type='egreso' AND tax>0,tax*-1,tax)))
				, ((IF(invoice_type='egreso' AND Amount>0,Amount*-1,Amount)))
				, invoice_type
				, Currency
				, Cost
				, Cost_Adj
				, StatusPrd
				, Status
				, salesorigin
				, currency_exchange
				, description
				, ID_orders_products
				, ID_products
				, ID_skus_parts
				, Ptype
			FROM (

				SELECT
					doc_serial
					, doc_num
					, sl_orders.ID_orders
					, sl_orders.Date orders_date
					, cu_invoices.doc_date invoices_date
					, cu_invoices.expediter_fname
					, sl_orders.ID_customers
					, sl_customers.company_name
					, sl_customers.FirstName
					, sl_customers.Lastname1
					, sl_customers.Lastname2
					, sl_customers.Type
					, sl_orders.Ptype
					, sl_orders_products.ID_products as ID_products_out
					, 'Principal' as grouping
					, '' as SKU
					, '' as UPC
					, cu_invoices_lines.quantity
					, cu_invoices_lines.unit_price
					, cu_invoices_lines.discount
					, cu_invoices_lines.tax_rate
					, cu_invoices_lines.tax
					, (cu_invoices_lines.quantity*cu_invoices_lines.unit_price) as TotalNet
					, ((cu_invoices_lines.quantity*cu_invoices_lines.unit_price)+cu_invoices_lines.tax) as Amount
					, invoice_type
					, cu_invoices.Currency
					, '' as Cost
					, '' as Cost_Adj
					, sl_orders.StatusPrd
					, cu_invoices.Status
					, (SELECT Channel FROM sl_salesorigins WHERE sl_salesorigins.ID_salesorigins=sl_orders.ID_salesorigins LIMIT 1) as salesorigin
					, cu_invoices.currency_exchange
					, cu_invoices_lines.description
					, sl_orders_products.ID_orders_products
					, '' AS ID_products
					, '' AS ID_skus_parts
				FROM cu_invoices_lines
				INNER JOIN cu_invoices USING(ID_invoices)
				INNER JOIN sl_orders ON(sl_orders.ID_orders = cu_invoices_lines.ID_orders)
				LEFT JOIN sl_orders_products ON (sl_orders_products.ID_orders_products = cu_invoices_lines.ID_orders_products AND cu_invoices_lines.ID_creditmemos IS NULL)
				INNER JOIN sl_customers ON sl_customers.ID_customers=sl_orders.ID_customers
				WHERE 1
				AND cu_invoices.Status='Certified'
				AND cu_invoices.invoice_type IN('ingreso','egreso')
				AND sl_orders.Status NOT IN ('System Error','Converted')
				AND (sl_orders_products.ShpDate > '2010-12-31' OR LEFT(sl_orders_products.ID_products,1) = '6' OR sl_orders_products.ID_orders_products IS NULL)
				$add_sql

				UNION ALL

				SELECT
					doc_serial
					, doc_num
					, sl_orders.ID_orders
					, sl_orders.Date orders_date
					, cu_invoices.doc_date invoices_date
					, cu_invoices.expediter_fname
					, sl_orders.ID_customers
					, sl_customers.company_name
					, sl_customers.FirstName
					, sl_customers.Lastname1
					, sl_customers.Lastname2
					, '' t1
					, sl_orders.Ptype
					, sl_orders_products.ID_products as ID_products_out
					, 'Secundario' as grouping
					, sl_skus.ID_sku_products
					, sl_skus.UPC
					, sl_orders_parts.Quantity
					, cu_invoices_lines.unit_price t3
					, cu_invoices_lines.discount
					, cu_invoices_lines.tax_rate
					, cu_invoices_lines.tax
					, (cu_invoices_lines.quantity*cu_invoices_lines.unit_price) as TotalNet
					, ((cu_invoices_lines.quantity*cu_invoices_lines.unit_price)+cu_invoices_lines.tax) as Amount
					, invoice_type
					, cu_invoices.Currency
					-- , sl_orders_parts.Cost
					, IF((cu_invoices_lines.ID_admin_users=0 OR cu_invoices_lines.ID_admin_users=100), 0, sl_orders_parts.Cost)Cost
					, sl_orders_parts.Cost_Adj
					, sl_orders.StatusPrd
					, cu_invoices.Status
					, (SELECT Channel FROM sl_salesorigins WHERE sl_salesorigins.ID_salesorigins=sl_orders.ID_salesorigins LIMIT 1) as salesorigin
					, cu_invoices.currency_exchange
					, cu_invoices_lines.description
					, sl_orders_products.ID_orders_products
					, sl_orders_products.ID_products
					, sl_orders_parts.ID_orders_parts ID_skus_parts
				FROM cu_invoices_lines
				INNER JOIN cu_invoices USING(ID_invoices)
				INNER JOIN sl_orders ON (sl_orders.ID_orders = cu_invoices_lines.ID_orders)
				LEFT JOIN sl_orders_products ON (sl_orders_products.ID_orders_products = cu_invoices_lines.ID_orders_products)
				LEFT JOIN sl_orders_parts ON sl_orders_parts.ID_orders_products=sl_orders_products.ID_orders_products 
				LEFT JOIN sl_skus ON sl_skus.ID_products=sl_orders_parts.ID_parts AND sl_skus.ID_sku_products=(400000000+sl_orders_parts.ID_parts)
				INNER JOIN sl_customers ON sl_customers.ID_customers=sl_orders.ID_customers
				WHERE 1
				AND cu_invoices.Status='Certified'
				AND cu_invoices.invoice_type IN('ingreso','egreso')
				AND sl_orders.Status NOT IN ('System Error','Converted')
				AND sl_orders_products.ID_products<=600000000
				AND sl_orders_products.ShpDate > '2010-12-31'
				$add_sql

				UNION ALL
				
				-- Credit memos 
				SELECT
					doc_serial
					, doc_num
					,`sl_creditmemos`.`ID_creditmemos` as ID_orders
					,`sl_creditmemos`.`Date` as orders_date
					,`cu_invoices`.`doc_date` invoices_date
					,`cu_invoices`.`expediter_fname`
					,`sl_creditmemos`.`ID_customers`
					,sl_customers.company_name
					,sl_customers.FirstName
					,sl_customers.Lastname1
					,sl_customers.Lastname2
					,`sl_customers`.`Type`
					, sl_orders.Ptype
					,sl_creditmemos_products.ID_products as ID_products_out
					,'Principal' as grouping
					,if(qry_products.SKU is null, cu_invoices_lines.ID_sku,qry_products.SKU) as SKU
					,if(qry_products.UPC is null, cu_invoices_lines.UPC,qry_products.UPC) as UPC
					,`cu_invoices_lines`.`quantity`
					,`cu_invoices_lines`.`unit_price`
					,`cu_invoices_lines`.`discount`
					,`cu_invoices_lines`.`tax_rate`
					,`cu_invoices_lines`.`tax` + sl_creditmemos_products.Shptax AS tax
					,(`cu_invoices_lines`.`quantity`*`cu_invoices_lines`.`unit_price`)+sl_creditmemos_products.Shipping as TotalNet
					,((`cu_invoices_lines`.`quantity`*`cu_invoices_lines`.`unit_price`)+`cu_invoices_lines`.`tax`+sl_creditmemos_products.Shipping)-`cu_invoices_lines`.`discount` as Amount
					,`invoice_type`
					,`cu_invoices`.`Currency`
					, sl_creditmemos_products.Cost
					, '' asCost_Adj
					,'' as StatusPrd
					,`cu_invoices`.`Status`
					,(SELECT channel FROM sl_salesorigins WHERE sl_salesorigins.ID_salesorigins=sl_orders.ID_salesorigins LIMIT 1) AS salesorigin
					, cu_invoices.currency_exchange
					, cu_invoices_lines.description
					, sl_creditmemos_products.ID_creditmemos_products as ID_orders_products
					, '' AS ID_products
					, qry_products.ID_skus_parts
				FROM cu_invoices_lines
				INNER JOIN cu_invoices USING(ID_invoices)
				INNER JOIN sl_creditmemos ON(sl_creditmemos.ID_creditmemos = cu_invoices_lines.ID_creditmemos)
				INNER JOIN sl_creditmemos_products ON (sl_creditmemos.ID_creditmemos = sl_creditmemos_products.ID_creditmemos and sl_creditmemos_products.id_creditmemos_products=cu_invoices_lines.id_orders_products)
				INNER JOIN sl_customers ON sl_customers.ID_customers=sl_creditmemos.ID_customers
				left join (
					SELECT a.ID_sku_products as ID_products, a.ID_parts, (a.ID_parts+400000000) as SKU, b.UPC, a.Qty, a.ID_skus_parts
					FROM sl_skus_parts a
					LEFT JOIN sl_skus b ON a.ID_parts=b.ID_products
					GROUP BY a.ID_skus_parts
					ORDER BY a.ID_sku_products asc
				) qry_products on sl_creditmemos_products.ID_products=qry_products.ID_products
				LEFT JOIN sl_creditmemos_payments ON (sl_creditmemos.ID_creditmemos = sl_creditmemos_payments.ID_creditmemos)
				LEFT JOIN sl_orders ON (sl_orders.ID_orders = sl_creditmemos_payments.ID_orders)
				WHERE 1
				AND cu_invoices.Status='Certified'
				AND cu_invoices.invoice_type IN('ingreso','egreso')				
				$add_sql
			) c 
			WHERE 1 
			ORDER BY ID_orders, invoices_date ASC, Invoice ASC, ID_orders_products
			");
			#ORDER BY ID_orders, Invoice ASC, ID_orders_products, ID_skus_parts

		if ($sth->rows() > 0){
			
			#$info_time =~	s/$txt_needle/$txt_replace/; 
			#print "Content-type: text/html\n";
			print "Content-type: application/octetstream\n";
			print "Content-disposition: attachment; filename=$fname\n\n";
			print "$strHeader\r\n";

			my $gtempo = '';
			my $last_product=0;

			$docto_anterior = '';
		
			while(my ($Invoice,$ID_orders,$OrderDate,$InvoiceDate,$Expediter,$ID_customers,$CustomerName,$CustomerType,$Grouping,$SKU,$UPC,$Qty,$UnitPrice,$Discount,$TaxRate,$TotalNet,$Tax,$Amount,$InvoiceType,$Currency,$Cost,$Cost_Adj,$StatusPrd,$status,$Origin,$currency_exchange,$description, $id_orders_products, $id_products, $id_skus_parts, $ptype) = $sth->fetchrow){

				my $strout = '';
				my $sku_name = '';
				
				my ($part_name, $part_model);
				$description =~ s/^\s*(.*?)\s*$/$1/;
				$UPC =~ s/^\s*(.*?)\s*$/$1/;
				$part_name = $description;
				
				$categories='';
				if ($SKU >= 400000000) {
					my ($sth) = &Do_SQL("SELECT Name, (SELECT Title FROM sl_categories WHERE ID_categories=(SELECT ID_categories FROM sl_parts WHERE ID_parts='".($SKU-400000000)."')) FROM sl_parts WHERE ID_parts='".($SKU-400000000)."';");
					($part_name, $categories) = $sth->fetchrow_array;
				}
				if ($SKU >= 600000000) {					
					my ($sth) = &Do_SQL("SELECT Name FROM sl_services WHERE ID_services='".($SKU-600000000)."';");
					($part_name) = $sth->fetchrow_array;
				}

				#Nueva columna: Categoria
				$_category = '';
				if(length($id_products) > 0) {
					$_temp = substr($id_products,length($id_products)-6);
					$_query ="select cat.Title
						from sl_products_properties pct
						inner join sl_properties cat using(ID_properties)
						where pct.id_products='$_temp';";
					#&cgierr($_query);
					my ($sth) = &Do_SQL($_query);
					($_category) = $sth->fetchrow_array;
				}

				if ($Grouping eq 'Principal' and $UPC < 600000000 and substr($UPC,0,1) ne 'P' and substr($UPC,0,1) ne 'S' and substr($UPC,0,1) ne '0' and uc($part_name) ne 'ENVIO Y MANEJO' and $UPC ne '4203727' and $UPC ne '4203766' and $UPC ne '4203721' and $UPC ne '502149' and $UPC ne '502208' and $UPC ne 'P13323'  and $UPC ne '14015626' and $UPC ne '785697-07' and $UPC ne '12471342' and $UPC ne '307090002' and $UPC ne '307090003' and $UPC ne '308010006' and $UPC ne '309010005' and $UPC ne '309010008' and $UPC ne '400002005' and $UPC ne '171191') {
					$UnitPrice = '0';
					$Discount = '0';
					$TaxRate = '';
					$TotalNet = '0';
					$Tax = '0';
					$Amount = '0';
					$last_product = '';
				}else{
					# $UnitPrice = $last_product.'<-'.$id_orders_products;

					# Secundario
					if ($last_product == $id_orders_products){
						if($docto_anterior eq $Invoice){
							$UnitPrice = '0';
							$Discount = '0';
							$TaxRate = '';
							$TotalNet = '0';
							$Tax = '0';
							$Amount = '0';
						}else{
							# Linea con precios
							$UnitPrice = ($Qty > 0)? $UnitPrice / $Qty : '';
							$docto_anterior = $Invoice;
						}
					}else{
						# Linea con precios
						$docto_anterior = $Invoice;
						$UnitPrice = ($Qty > 0)? $UnitPrice / $Qty : '';
					}
				}

				if (lc($InvoiceType) eq 'ingreso'){
					$docto = 'Factura';
				}elsif (lc($InvoiceType) eq 'egreso'){
					$docto = 'Nota de credito';
					$Cost *= (-1);
				}
				#Blank Vars
				my ($Tipo,$cu,$ca,$cc);
				$cu = $Cost;
				$ca = $Cost_Adj;
				$cc = 0; # ADG->Aun no se conoce este dato en el Sistema

				#$strout .= qq|"$Invoice","$ID_orders","$OrderDate","$InvoiceDate","$Expediter","$ID_customers","$CustomerName","$CustomerType","$Grouping","$UPC","$SKU","$part_name","$categories","$InvoiceType","$Qty","$UnitPrice","$TotalNet","$Discount","|.($TotalNet-$Discount).qq|","$TaxRate","$Tax","$Amount","$docto","$Currency","|.($Cost*$Qty).qq|","$currency_exchange","$Cost","$StatusPrd","$status","$Origin"\r\n|;
				$strout .= qq|"$Expediter","$Invoice","$ID_orders","$OrderDate","$InvoiceDate","$InvoiceDate","$ID_customers","$CustomerName","$categories","$Tipo","$Origin","$Grouping","$UPC","$SKU","$part_name","$docto","$Qty","$UnitPrice","$TotalNet","$Discount","|.($TotalNet-$Discount).qq|","$TaxRate","$Tax","|.(($TotalNet-$Discount)+$Tax).qq|","$ca","$Cost","|.($Cost*$Qty).qq|","$Currency","$currency_exchange","$status","$CustomerType","$ptype"\r\n|;
								
				print $strout;

				# Grouping Temporal
				$gtempo = $Grouping;

				$last_product = $id_orders_products if ($Grouping ne 'Principal');
			}
			# 	&auth_logging('report_view','');
			return;
		}else{
			$va{'message'} = &trans_txt('search_nomatches');
		}
	}
	
	print "Content-type: text/html\n\n";
	print &build_page('rep_bi_invoicing.html');
}

#############################################################################
#############################################################################
#   Function: rep_bi_media_sales
#
#       Es: Reporte de Ventas para Medios
#       En: Sales Report
#
#
#    Created on: 30/09/2013
#
#    Author: Alejandro Diaz
#
#    Modifications:
#
#        - Modified on ** by *** : 
#
#   Parameters:
#
#      - 
#
#  Returns:
#
#
#   See Also:
#
#      <>
#
sub rep_bi_media_sales{
#############################################################################
#############################################################################

	if($in{'action'}){
		my ($query_list);
		my $maxprod=1;
		my $info_user =	'';
		my $info_time = '';
		my $strout = '';
		
		## Busqueda por rango de fecha
		$in{'from_date'} = &get_sql_date() if !$in{'from_date'};
		$in{'to_date'} = &get_sql_date() if !$in{'to_date'};
		
		$add_sql  = " AND sl_orders.Date >= DATE('$in{'from_date'}')";
		$add_sql .= " AND sl_orders.Date <= DATE('$in{'to_date'}')";
		
		## GQ: Filtro por Status
		if( $in{'status'} and $in{'status'} ne '' ){
			$in{'status'} =~ s/\|/','/g;
			$add_sql .= " AND sl_orders.Status IN('".$in{'status'}."')";
		}
		
		my $fname   = 'ventas_medios'.$cfg{'app_title'}.'.csv';
		$fname =~ s/\s/_/g;
		

		my $titles_sup_coord, $fields_sup_coord, $where_sup_coord;

		if($cfg{'use_admin_users_tree'} and $cfg{'use_admin_users_tree'}==1){
			$titles_sup_coord = ',SUPERVISOR,COORDINADOR';
			$fields_sup_coord = ",(SELECT UPPER(CONCAT (Firstname,' ',LastName,' ',MiddleName)) FROM admin_users WHERE ID_admin_users=cu_admin_users_tree.ID_admin_users2 ) supervisor ";
			$fields_sup_coord .= ",(SELECT UPPER(CONCAT (Firstname,' ',LastName,' ',MiddleName)) FROM admin_users WHERE ID_admin_users=cu_admin_users_tree.ID_admin_users3 ) coordinador ";
			$where_sup_coord .= " LEFT JOIN cu_admin_users_tree ON admin_users.ID_admin_users=cu_admin_users_tree.ID_admin_users ";
		}



		my $strHeader = "DID,FORMA DE PAGO,ID_PEDIDO,ORIGEN DE VENTA,ESTATUS DEL PEDIDO,ESTATUS DEL PRODUCTO,ESTATUS DEL PAGO,FECHA DE PEDIDO,HORA DE PEDIDO,CLIENTE,EMAIL,GENERO,FECHA DE NACIMIENTO,CALLER ID,TEL CASA,TEL OFICINA,CELULAR,CALLE Y NO,COLONIA,DELEGACION/ MUNICIPIO,ESTADO,CODIGO POSTAL,CLAVE DE PRODUCTO,PRODUCTO,MODELO,CANTIDAD,SKU,UPC,DESCRIPCION,MODELO,FAMILIA,PRECIO UNITARIO,PRECIO VENTA,DESCUENTO,IVA,ENVIO,IVA ENVIO,PRECIO TOTAL,ID USUARIO,USUARIO".$titles_sup_coord.",ID ZONA,ZONA";
		$query = "SELECT '0'
			,sl_zones.ID_zones
			,sl_zones.Name
			, sl_orders.Ptype
			, sl_orders.ID_orders
			, sl_salesorigins.Channel
			, sl_orders.Status
			, sl_orders.StatusPrd
			, sl_orders.StatusPay
			, sl_orders.Date
			, sl_orders.Time
			, (CONCAT(sl_customers.FirstName,' ',sl_customers.LastName1 ,' ',sl_customers.Lastname2))
			, sl_customers.Email, sl_customers.Sex
			, sl_customers.Birthday
			, sl_customers.CID
			, sl_customers.Phone1
			, sl_customers.Phone2
			, sl_customers.Cellphone
			, sl_orders.shp_Address1
			, sl_orders.shp_Urbanization
			, sl_orders.shp_City
			, sl_orders.shp_State
			, sl_orders.shp_Zip
			, sl_orders_products.ID_products
			, sl_products.Name
			, sl_products.Model
			, qry_products.Qty
			, qry_products.SKU
			, qry_products.UPC
			, qry_products.Name
			, qry_products.Model
			, qry_products.Category
			, ((sl_orders_products.SalePrice / sl_orders_products.Quantity)) UnitPrice
			, ifnull(sl_orders_products.SalePrice,0)
			, ifnull(sl_orders_products.Discount,0)
			, ifnull(sl_orders_products.Tax,0)
			, ifnull(sl_orders_products.Shipping,0)
			, ifnull(sl_orders_products.ShpTax,0)
			, ((ifnull(sl_orders_products.SalePrice,0) - ifnull(sl_orders_products.Discount,0) + ifnull(sl_orders_products.Tax,0) + ifnull(sl_orders_products.Shipping,0) + ifnull(sl_orders_products.ShpTax,0)))
			, admin_users.ID_admin_users
			, UPPER((CONCAT(IFNULL(admin_users.FirstName,''),' ',IFNULL(admin_users.MiddleName,''),' ',IFNULL(admin_users.LastName,''))))
			,sl_orders_products.ID_orders_products			
			". $fields_sup_coord ."
			, qry_products.ID_skus_parts			
			FROM sl_orders
			INNER JOIN sl_zones on sl_zones.ID_zones=sl_orders.ID_zones
			INNER JOIN sl_orders_products ON sl_orders_products.ID_orders=sl_orders.ID_orders
			LEFT JOIN sl_products ON RIGHT(sl_orders_products.ID_products,6) = sl_products.ID_products
			LEFT JOIN sl_salesorigins USING(ID_salesorigins)
			LEFT JOIN sl_customers ON sl_customers.ID_customers=sl_orders.ID_customers
			LEFT JOIN admin_users ON admin_users.ID_admin_users=sl_orders.ID_admin_users
			". $where_sup_coord ."
			LEFT JOIN (
				SELECT 
					a.ID_sku_products AS ID_products
					, a.ID_parts
					, (a.ID_parts+400000000) AS SKU
					, b.UPC
					, a.Qty
					, sl_parts.Model
					, sl_parts.Name
					, sl_categories.Title as Category
					, a.ID_skus_parts
				FROM sl_skus_parts a
				INNER JOIN sl_skus b ON a.ID_parts=b.ID_products
				INNER JOIN sl_parts ON sl_parts.ID_parts=a.ID_parts
				LEFT JOIN sl_categories ON sl_categories.ID_categories=sl_parts.ID_categories
				GROUP BY a.ID_skus_parts
				ORDER BY a.ID_skus_parts ASC
			) qry_products ON sl_orders_products.ID_products=qry_products.ID_products
			WHERE 1 
			AND sl_orders_products.Status NOT IN('Order Cancelled', 'Inactive')
			AND sl_orders.Status NOT IN ('System Error')
			$add_sql
			ORDER BY sl_orders.ID_orders DESC, sl_orders_products.ID_orders_products,qry_products.ID_skus_parts
			";
		my ($sth) = &Do_SQL($query);
		&log_reports($query, 'rep_bi_media_sales');
		if ($sth->rows() > 0){
			
		# 	$info_time =~	s/$txt_needle/$txt_replace/; 
			print "Content-type: application/octetstream\n";
			print "Content-disposition: attachment; filename=$fname\n\n";
			print "$strHeader\r\n";

			my $last_product=0;
			my($did,$forma_de_pago,$id_pedido,$origen_de_venta,$estatus_del_pedido,$estatus_del_producto,$estatus_del_pago,$fecha_de_pedido,$hora_de_pedido,$cliente,$email,$genero,$fecha_de_nacimiento,$caller_id,$tel_casa,$tel_oficina,$celular,$calle_y_no,$colonia,$delegacion_municipio,$estado,$codigo_postal,$clave_de_producto,$producto,$modelo,$cantidad,$sku,$upc,$descripcion,$modelo,$familia,$precio_unitario,$precio_venta,$descuento,$iva,$envio,$iva_envio,$precio_total,$id_admin_users,$username,$id_orders_products,$supervisor,$coordinador,$id_zones,$zone_name);
			while(($did,$id_zones,$zone_name,$forma_de_pago,$id_pedido,$origen_de_venta,$estatus_del_pedido,$estatus_del_producto,$estatus_del_pago,$fecha_de_pedido,$hora_de_pedido,$cliente,$email,$genero,$fecha_de_nacimiento,$caller_id,$tel_casa,$tel_oficina,$celular,$calle_y_no,$colonia,$delegacion_municipio,$estado,$codigo_postal,$clave_de_producto,$producto,$modelo,$cantidad,$sku,$upc,$descripcion,$modelo,$familia,$precio_unitario,$precio_venta,$descuento,$iva,$envio,$iva_envio,$precio_total,$id_admin_users,$username,$id_orders_products,$supervisor,$coordinador) = $sth->fetchrow){

				$calle_y_no =~ s/\\//gi;
				$calle_y_no =~ s/"//gi;

				# Secundario
				if ($last_product == $id_orders_products){
					$precio_unitario = '0';
					$precio_venta = '0';
					$iva = '0';
					$envio = '0';
					$iva_envio = '0';
					$precio_total = '0';
				}
				
				if ($clave_de_producto > 600000000){
					my $id_services  = $clave_de_producto - 600000000;
					my $service = &load_name('sl_services','ID_services',$id_services,'Name');
					$producto = $service;
					$modelo = '';
				}

				$last_product = $id_orders_products;

				## Se ocultan datos temporalmente
				$caller_id = &temp_hide_data($caller_id,'phone');
				$tel_casa = &temp_hide_data($tel_casa,'phone');
				$tel_oficina = &temp_hide_data($tel_oficina,'phone');
				$celular = &temp_hide_data($celular,'phone');
				$calle_y_no = &temp_hide_data($calle_y_no);
				$colonia = &temp_hide_data($colonia);
				$delegacion_municipio = &temp_hide_data($delegacion_municipio);
				$estado = &temp_hide_data($estado);
				$codigo_postal = &temp_hide_data($codigo_postal);

				$strout .= qq|"$did","$forma_de_pago","$id_pedido","$origen_de_venta","$estatus_del_pedido","$estatus_del_producto","$estatus_del_pago","$fecha_de_pedido","$hora_de_pedido","$cliente","$email","$genero","$fecha_de_nacimiento","$caller_id","$tel_casa","$tel_oficina","$celular","$calle_y_no","$colonia","$delegacion_municipio","$estado","$codigo_postal","$clave_de_producto","$producto","$modelo","$cantidad","$sku","$upc","$descripcion","$modelo","$familia","$precio_unitario","$precio_venta","$descuento","$iva","$envio","$iva_envio","$precio_total","$id_admin_users","$username"|;
				if($cfg{'use_admin_users_tree'} and $cfg{'use_admin_users_tree'}==1){
					$strout .= qq|,"$supervisor","$coordinador"|;
				}

				$strout .= qq|,"$id_zones","$zone_name"|;
				$strout .= qq|\r\n|;

			}
			print $strout;
			# 	&auth_logging('report_view','');
			return;
		}else{
			$va{'message'} = &trans_txt('search_nomatches');
		}
	}
	
	print "Content-type: text/html\n\n";
	print &build_page('rep_bi_media_sales.html');
}


#############################################################################
#############################################################################
#   Function: rep_bi_media_sales_2
#
#       Es: Reporte de Ventas para Medios
#       En: Sales Report
#
#
#    Created on: 20/01/2017
#
#    Author: Fabian Cañaveral
#
#    Modifications:
#
#        - Modified on ** by *** : 
#
#   Parameters:
#
#      - 
#
#  Returns:
#
#
#   See Also:
#
#      <>
#
sub rep_bi_media_sales_v2{
#############################################################################
#############################################################################

	if($in{'action'}){
		my ($query_list);
		my $maxprod=1;
		my $info_user =	'';
		my $info_time = '';
		my $strout = '';
		
		## Busqueda por rango de fecha
		$in{'from_date'} = &get_sql_date() if !$in{'from_date'};
		$in{'to_date'} = &get_sql_date() if !$in{'to_date'};
		
		$add_sql  = " AND sl_orders.Date >= DATE('$in{'from_date'}')";
		$add_sql .= " AND sl_orders.Date <= DATE('$in{'to_date'}')";
		
		## GQ: Filtro por Status
		if( $in{'status'} and $in{'status'} ne '' ){
			$in{'status'} =~ s/\|/','/g;
			$add_sql .= " AND sl_orders.Status IN('".$in{'status'}."')";
		}
		
		my $fname   = 'ventas_medios'.$cfg{'app_title'}.'.csv';
		$fname =~ s/\s/_/g;
		

		my $titles_sup_coord, $fields_sup_coord, $where_sup_coord;

		if($cfg{'use_admin_users_tree'} and $cfg{'use_admin_users_tree'}==1){
			$titles_sup_coord = ',SUPERVISOR,COORDINADOR';
			$fields_sup_coord = ",(SELECT UPPER(CONCAT (Firstname,' ',LastName,' ',MiddleName)) FROM admin_users WHERE ID_admin_users=cu_admin_users_tree.ID_admin_users2 ) supervisor ";
			$fields_sup_coord .= ",(SELECT UPPER(CONCAT (Firstname,' ',LastName,' ',MiddleName)) FROM admin_users WHERE ID_admin_users=cu_admin_users_tree.ID_admin_users3 ) coordinador ";
			$where_sup_coord .= " LEFT JOIN cu_admin_users_tree ON admin_users.ID_admin_users=cu_admin_users_tree.ID_admin_users ";
		}



		my $strHeader = qq|FORMA DE PAGO,ID_PEDIDO,ORIGEN DE VENTA,ESTATUS DEL PEDIDO,ESTATUS DEL PRODUCTO,ESTATUS DEL PAGO,FECHA DE PEDIDO,HORA DE PEDIDO,CALLER ID,TEL CASA,TEL OFICINA,CELULAR,MODELO,FAMILIA,PRECIO VENTA,PRECIO TOTAL,ID USUARIO,USUARIO,SUPERVISOR,COORDINADOR|;

		my ($sth) = &Do_SQL("SELECT '0'
			,sl_zones.ID_zones
			,sl_zones.Name
			, sl_orders.Ptype
			, sl_orders.ID_orders
			, sl_salesorigins.Channel
			, sl_orders.Status
			, sl_orders.StatusPrd
			, sl_orders.StatusPay
			, sl_orders.Date
			, sl_orders.Time
			, (CONCAT(sl_customers.FirstName,' ',sl_customers.LastName1 ,' ',sl_customers.Lastname2))
			, sl_customers.Email, sl_customers.Sex
			, sl_customers.Birthday
			, sl_customers.CID
			, sl_customers.Phone1
			, sl_customers.Phone2
			, sl_customers.Cellphone
			, sl_orders.shp_Address1
			, sl_orders.shp_Urbanization
			, sl_orders.shp_City
			, sl_orders.shp_State
			, sl_orders.shp_Zip
			, sl_orders_products.ID_products
			, sl_products.Name
			, sl_products.Model
			, qry_products.Qty
			, qry_products.SKU
			, qry_products.UPC
			, qry_products.Name
			, qry_products.Model
			, qry_products.Category
			, ((sl_orders_products.SalePrice / sl_orders_products.Quantity)) UnitPrice
			, ifnull(sl_orders_products.SalePrice,0)
			, ifnull(sl_orders_products.Discount,0)
			, ifnull(sl_orders_products.Tax,0)
			, ifnull(sl_orders_products.Shipping,0)
			, ifnull(sl_orders_products.ShpTax,0)
			, ((ifnull(sl_orders_products.SalePrice,0) - ifnull(sl_orders_products.Discount,0) + ifnull(sl_orders_products.Tax,0) + ifnull(sl_orders_products.Shipping,0) + ifnull(sl_orders_products.ShpTax,0)))
			, admin_users.ID_admin_users
			, UPPER((CONCAT(admin_users.FirstName,' ',admin_users.MiddleName,' ',admin_users.LastName)))
			,sl_orders_products.ID_orders_products			
			". $fields_sup_coord ."
			, qry_products.ID_skus_parts			
			FROM sl_orders
			INNER JOIN sl_zones on sl_zones.ID_zones=sl_orders.ID_zones
			INNER JOIN sl_orders_products ON sl_orders_products.ID_orders=sl_orders.ID_orders
			LEFT JOIN sl_products ON RIGHT(sl_orders_products.ID_products,6) = sl_products.ID_products
			LEFT JOIN sl_salesorigins USING(ID_salesorigins)
			LEFT JOIN sl_customers ON sl_customers.ID_customers=sl_orders.ID_customers
			LEFT JOIN admin_users ON admin_users.ID_admin_users=sl_orders.ID_admin_users
			". $where_sup_coord ."
			LEFT JOIN (
				SELECT 
					a.ID_sku_products AS ID_products
					, a.ID_parts
					, (a.ID_parts+400000000) AS SKU
					, b.UPC
					, a.Qty
					, sl_parts.Model
					, sl_parts.Name
					, sl_categories.Title as Category
					, a.ID_skus_parts
				FROM sl_skus_parts a
				INNER JOIN sl_skus b ON a.ID_parts=b.ID_products
				INNER JOIN sl_parts ON sl_parts.ID_parts=a.ID_parts
				LEFT JOIN sl_categories ON sl_categories.ID_categories=sl_parts.ID_categories
				GROUP BY a.ID_skus_parts
				ORDER BY a.ID_skus_parts ASC
			) qry_products ON sl_orders_products.ID_products=qry_products.ID_products
			WHERE 1 
			AND sl_orders_products.Status NOT IN('Order Cancelled', 'Inactive')
			AND sl_orders.Status NOT IN ('System Error')
			$add_sql
			ORDER BY sl_orders.ID_orders DESC, sl_orders_products.ID_orders_products,qry_products.ID_skus_parts
			");
		
		if ($sth->rows() > 0){
			
		# 	$info_time =~	s/$txt_needle/$txt_replace/; 
			print "Content-type: application/octetstream\n";
			print "Content-disposition: attachment; filename=$fname\n\n";
			print "$strHeader\r\n";

			my $last_product=0;
			my($did,$forma_de_pago,$id_pedido,$origen_de_venta,$estatus_del_pedido,$estatus_del_producto,$estatus_del_pago,$fecha_de_pedido,$hora_de_pedido,$cliente,$email,$genero,$fecha_de_nacimiento,$caller_id,$tel_casa,$tel_oficina,$celular,$calle_y_no,$colonia,$delegacion_municipio,$estado,$codigo_postal,$clave_de_producto,$producto,$modelo,$cantidad,$sku,$upc,$descripcion,$modelo,$familia,$precio_unitario,$precio_venta,$descuento,$iva,$envio,$iva_envio,$precio_total,$id_admin_users,$username,$id_orders_products,$supervisor,$coordinador,$id_zones,$zone_name);
			while(($did,$id_zones,$zone_name,$forma_de_pago,$id_pedido,$origen_de_venta,$estatus_del_pedido,$estatus_del_producto,$estatus_del_pago,$fecha_de_pedido,$hora_de_pedido,$cliente,$email,$genero,$fecha_de_nacimiento,$caller_id,$tel_casa,$tel_oficina,$celular,$calle_y_no,$colonia,$delegacion_municipio,$estado,$codigo_postal,$clave_de_producto,$producto,$modelo,$cantidad,$sku,$upc,$descripcion,$modelo,$familia,$precio_unitario,$precio_venta,$descuento,$iva,$envio,$iva_envio,$precio_total,$id_admin_users,$username,$id_orders_products,$supervisor,$coordinador) = $sth->fetchrow){

				$calle_y_no =~ s/\\//gi;
				$calle_y_no =~ s/"//gi;

				# Secundario
				if ($last_product == $id_orders_products){
					$precio_unitario = '0';
					$precio_venta = '0';
					$iva = '0';
					$envio = '0';
					$iva_envio = '0';
					$precio_total = '0';
				}
				
				if ($clave_de_producto > 600000000){
					my $id_services  = $clave_de_producto - 600000000;
					my $service = &load_name('sl_services','ID_services',$id_services,'Name');
					$producto = $service;
					$modelo = '';
				}

				$last_product = $id_orders_products;
				

				## Se ocultan datos temporalmente
				$caller_id = &temp_hide_data($caller_id,'phone');
				$tel_casa = &temp_hide_data($tel_casa,'phone');
				$tel_oficina = &temp_hide_data($tel_oficina,'phone');
				$celular = &temp_hide_data($celular,'phone');
				$calle_y_no = &temp_hide_data($calle_y_no);
				$colonia = &temp_hide_data($colonia);
				$delegacion_municipio = &temp_hide_data($delegacion_municipio);
				$estado = &temp_hide_data($estado);
				$codigo_postal = &temp_hide_data($codigo_postal);

				$strout .= qq|"$forma_de_pago","$id_pedido","$origen_de_venta","$estatus_del_pedido","$estatus_del_producto","$estatus_del_pago","$fecha_de_pedido","$hora_de_pedido","$caller_id","$tel_casa","$tel_oficina","$celular","$modelo","$familia","$precio_venta","$precio_total","$id_admin_users","$username","$supervisor","$coordinador"|;

				$strout .= qq|\r\n|;

			}
			print $strout;
			# 	&auth_logging('report_view','');
			return;
		}else{
			$va{'message'} = &trans_txt('search_nomatches');
		}
	}
	
	print "Content-type: text/html\n\n";
	print &build_page('rep_bi_media_sales_v2.html');
}


#############################################################################
#############################################################################
#   Function: rep_bi_media_sales
#
#       Es: Reporte de Ventas para Medios DARIO
#       En: Sales Report
#
#
#    Created on: 30/09/2013
#
#    Author: JS
#
#    Modifications:
#
#        - Modified on ** by *** : 
#
#   Parameters:
#
#      - 
#
#  Returns:
#
#
#   See Also:
#
#      <>
#
sub rep_bi_media_sales_v3{
#############################################################################
#############################################################################

	if($in{'action'}){
		my ($query_list);
		my $maxprod=1;
		my $info_user =	'';
		my $info_time = '';
		my $strout = '';
		
		## Busqueda por rango de fecha
		$in{'from_date'} = &get_sql_date() if !$in{'from_date'};
		$in{'to_date'} = &get_sql_date() if !$in{'to_date'};
		
		$add_sql  = " AND sl_orders.Date >= DATE('$in{'from_date'}')";
		$add_sql .= " AND sl_orders.Date <= DATE('$in{'to_date'}')";
		
		## GQ: Filtro por Status
		if( $in{'status'} and $in{'status'} ne '' ){
			$in{'status'} =~ s/\|/','/g;
			$add_sql .= " AND sl_orders.Status IN('".$in{'status'}."')";
		}
		
		my $fname   = 'ventas_medios'.$cfg{'app_title'}.'.csv';
		$fname =~ s/\s/_/g;
		

		my $titles_sup_coord, $fields_sup_coord, $where_sup_coord;

		if($cfg{'use_admin_users_tree'} and $cfg{'use_admin_users_tree'}==1){
			$titles_sup_coord = ',SUPERVISOR,COORDINADOR';
			$fields_sup_coord = ",(SELECT UPPER(CONCAT (Firstname,' ',LastName,' ',MiddleName)) FROM admin_users WHERE ID_admin_users=cu_admin_users_tree.ID_admin_users2 ) supervisor ";
			$fields_sup_coord .= ",(SELECT UPPER(CONCAT (Firstname,' ',LastName,' ',MiddleName)) FROM admin_users WHERE ID_admin_users=cu_admin_users_tree.ID_admin_users3 ) coordinador ";
			$where_sup_coord .= " LEFT JOIN cu_admin_users_tree ON admin_users.ID_admin_users=cu_admin_users_tree.ID_admin_users ";
		}



		my $strHeader = "DID,FORMA DE PAGO,ID_PEDIDO,ORIGEN DE VENTA,FECHA DE PEDIDO,HORA DE PEDIDO,CLIENTE,GENERO,FECHA DE NACIMIENTO,CALLER ID,TEL CASA,TEL OFICINA,CELULAR,ESTADO,CLAVE DE PRODUCTO,PRODUCTO,MODELO,CANTIDAD,SKU,UPC,FAMILIA,PRECIO VENTA,DESCUENTO,IVA,ENVIO,IVA ENVIO,PRECIO TOTAL,ID USUARIO,USUARIO".$titles_sup_coord;
		
		my ($sth) = &Do_SQL("SELECT '0'
			,sl_zones.ID_zones
			,sl_zones.Name
			, sl_orders.Ptype
			, sl_orders.ID_orders
			, sl_salesorigins.Channel
			, sl_orders.Status
			, sl_orders.StatusPrd
			, sl_orders.StatusPay
			, sl_orders.Date
			, sl_orders.Time
			, (CONCAT(sl_customers.FirstName,' ',sl_customers.LastName1 ,' ',sl_customers.Lastname2))
			, sl_customers.Email, sl_customers.Sex
			, sl_customers.Birthday
			, sl_customers.CID
			, sl_customers.Phone1
			, sl_customers.Phone2
			, sl_customers.Cellphone
			, sl_orders.shp_Address1
			, sl_orders.shp_Urbanization
			, sl_orders.shp_City
			, sl_orders.shp_State
			, sl_orders.shp_Zip
			, sl_orders_products.ID_products
			, sl_products.Name
			, sl_products.Model
			, qry_products.Qty
			, qry_products.SKU
			, qry_products.UPC
			, qry_products.Name
			, qry_products.Model
			, qry_products.Category
			, ((sl_orders_products.SalePrice / sl_orders_products.Quantity)) UnitPrice
			, ifnull(sl_orders_products.SalePrice,0)
			, ifnull(sl_orders_products.Discount,0)
			, ifnull(sl_orders_products.Tax,0)
			, ifnull(sl_orders_products.Shipping,0)
			, ifnull(sl_orders_products.ShpTax,0)
			, ((ifnull(sl_orders_products.SalePrice,0) - ifnull(sl_orders_products.Discount,0) + ifnull(sl_orders_products.Tax,0) + ifnull(sl_orders_products.Shipping,0) + ifnull(sl_orders_products.ShpTax,0)))
			, admin_users.ID_admin_users
			, UPPER((CONCAT(admin_users.FirstName,' ',admin_users.MiddleName,' ',admin_users.LastName)))
			,sl_orders_products.ID_orders_products			
			". $fields_sup_coord ."
			, qry_products.ID_skus_parts			
			FROM sl_orders
			INNER JOIN sl_zones on sl_zones.ID_zones=sl_orders.ID_zones
			INNER JOIN sl_orders_products ON sl_orders_products.ID_orders=sl_orders.ID_orders
			LEFT JOIN sl_products ON RIGHT(sl_orders_products.ID_products,6) = sl_products.ID_products
			LEFT JOIN sl_salesorigins USING(ID_salesorigins)
			LEFT JOIN sl_customers ON sl_customers.ID_customers=sl_orders.ID_customers
			LEFT JOIN admin_users ON admin_users.ID_admin_users=sl_orders.ID_admin_users
			". $where_sup_coord ."
			LEFT JOIN (
				SELECT 
					a.ID_sku_products AS ID_products
					, a.ID_parts
					, (a.ID_parts+400000000) AS SKU
					, b.UPC
					, a.Qty
					, sl_parts.Model
					, sl_parts.Name
					, sl_categories.Title as Category
					, a.ID_skus_parts
				FROM sl_skus_parts a
				INNER JOIN sl_skus b ON a.ID_parts=b.ID_products
				INNER JOIN sl_parts ON sl_parts.ID_parts=a.ID_parts
				LEFT JOIN sl_categories ON sl_categories.ID_categories=sl_parts.ID_categories
				GROUP BY a.ID_skus_parts
				ORDER BY a.ID_skus_parts ASC
			) qry_products ON sl_orders_products.ID_products=qry_products.ID_products
			WHERE 1 
			AND sl_orders_products.Status NOT IN('Order Cancelled', 'Inactive')
			AND sl_orders.Status NOT IN ('System Error')
			$add_sql
			ORDER BY sl_orders.ID_orders DESC, sl_orders_products.ID_orders_products,qry_products.ID_skus_parts
			");
		
		if ($sth->rows() > 0){
			
		# 	$info_time =~	s/$txt_needle/$txt_replace/; 
			print "Content-type: application/octetstream\n";
			print "Content-disposition: attachment; filename=$fname\n\n";
			print "$strHeader\r\n";

			my $last_product=0;
			my($did,$forma_de_pago,$id_pedido,$origen_de_venta,$estatus_del_pedido,$estatus_del_producto,$estatus_del_pago,$fecha_de_pedido,$hora_de_pedido,$cliente,$email,$genero,$fecha_de_nacimiento,$caller_id,$tel_casa,$tel_oficina,$celular,$calle_y_no,$colonia,$delegacion_municipio,$estado,$codigo_postal,$clave_de_producto,$producto,$modelo,$cantidad,$sku,$upc,$descripcion,$modelo,$familia,$precio_unitario,$precio_venta,$descuento,$iva,$envio,$iva_envio,$precio_total,$id_admin_users,$username,$id_orders_products,$supervisor,$coordinador,$id_zones,$zone_name);
			while(($did,$id_zones,$zone_name,$forma_de_pago,$id_pedido,$origen_de_venta,$estatus_del_pedido,$estatus_del_producto,$estatus_del_pago,$fecha_de_pedido,$hora_de_pedido,$cliente,$email,$genero,$fecha_de_nacimiento,$caller_id,$tel_casa,$tel_oficina,$celular,$calle_y_no,$colonia,$delegacion_municipio,$estado,$codigo_postal,$clave_de_producto,$producto,$modelo,$cantidad,$sku,$upc,$descripcion,$modelo,$familia,$precio_unitario,$precio_venta,$descuento,$iva,$envio,$iva_envio,$precio_total,$id_admin_users,$username,$id_orders_products,$supervisor,$coordinador) = $sth->fetchrow){

				$calle_y_no =~ s/\\//gi;
				$calle_y_no =~ s/"//gi;

				# Secundario
				if ($last_product == $id_orders_products){
					$precio_unitario = '0';
					$precio_venta = '0';
					$iva = '0';
					$envio = '0';
					$iva_envio = '0';
					$precio_total = '0';
				}
				
				if ($clave_de_producto > 600000000){
					my $id_services  = $clave_de_producto - 600000000;
					my $service = &load_name('sl_services','ID_services',$id_services,'Name');
					$producto = $service;
					$modelo = '';
				}

				$last_product = $id_orders_products;

				## Se ocultan datos temporalmente
				# $caller_id = &temp_hide_data($caller_id,'phone');
				# $tel_casa = &temp_hide_data($tel_casa,'phone');
				# $tel_oficina = &temp_hide_data($tel_oficina,'phone');
				# $celular = &temp_hide_data($celular,'phone');
				# $calle_y_no = &temp_hide_data($calle_y_no);
				# $colonia = &temp_hide_data($colonia);
				# $delegacion_municipio = &temp_hide_data($delegacion_municipio);
				# $estado = &temp_hide_data($estado);
				# $codigo_postal = &temp_hide_data($codigo_postal); 

				$strout .= qq|"$did","$forma_de_pago","$id_pedido","$origen_de_venta","$fecha_de_pedido","$hora_de_pedido","$cliente","$genero","$fecha_de_nacimiento","$caller_id","$tel_casa","$tel_oficina","$celular"|;
				
				if( $in{'external_requirement'} eq '1' )
				{ 
					$strout .= qq|,"$email"|; 
				}

				$strout .= qq|,"$estado","$clave_de_producto","$producto","$modelo","$cantidad","$sku","$upc","$familia","$precio_venta","$descuento","$iva","$envio","$iva_envio","$precio_total","$id_admin_users","$username"|;				
				$strout .= qq|,"$supervisor","$coordinador"|;				
				$strout .= qq|\r\n|;

			}

			if( $in{'external_requirement'} eq '1' )
			{
				return $strout;
			}
			else
			{
				print $strout;			
				return;
			}
		}else{
			$va{'message'} = &trans_txt('search_nomatches');
		}
	}
	
	print "Content-type: text/html\n\n";
	print &build_page('rep_bi_media_sales_v3.html');
}


#############################################################################
#############################################################################
#   Function: rep_bi_media_sales_plus
#
#       Es: Reporte de Ventas para Medios DARIO + Mail
#       En: Sales Report
#
#
#    Created on: 30/09/2013
#
#    Author: HC
#
#    Modifications:
#
#        - Modified on ** by *** : 
#
#   Parameters:
#
#      - 
#
#  Returns:
#
#
#   See Also:
#
#      <>
#
sub rep_bi_media_sales_plus{
#############################################################################
#############################################################################

	if($in{'action'}){
		
		$in{'external_requirement'} = 1;
		$data = &rep_bi_media_sales_v3();

		if( $data ne '')
		{
			print $data;
			return;
		}else{
			$va{'message'} = &trans_txt('search_nomatches');
		}
	}
	
	print "Content-type: text/html\n\n";
	print &build_page('rep_bi_media_sales_plus.html');
}


#############################################################################
#############################################################################
#   Function: rep_bills_banks
#
#       Es: Reporte de Detalle de Pagos
#       En: 
#
#
#    Created on: 03/06/2013
#
#    Author: EO
#
#    Modifications:
#
#        - Modified on ** by *** : 
#
#   Parameters:
#
#      - 
#
#  Returns:
#
#
#   See Also:
#
#      <>
#
sub rep_bi_prices{
#############################################################################
#############################################################################

	if($in{'action'}) {

		my ($query_list);
		my $maxprod=1;
		my $info_user =	'';
		my $info_pprod = '';
		my $info_oprod = '';
		my $info_time = '';
		my $strout = '';
		my $add_filters = '';

		# $add_filters = " AND ID_banks='$in{'id_banks'}'" if ($in{'id_banks'});

		my $fname   = 'products_prices_'.$cfg{'app_title'}.'.csv';
		$fname =~ s/\s/_/g;
		
		my $strHeader = qq|"ID PRODUCTO","NOMBRE","MODELO","DESCRIPCION DE PRECIO","PRECIO","MENSUALIDADES","FORMA DE PAGO","ESTATUS","CATEGORIA","% IVA","CONSOLAS"|;
		my ($sth_ext) = &Do_SQL("SELECT 
			c.ID_products
			, e.Name
			, e.Model
			, c.Name PriceName
			, c.Price
			, c.FP
			, c.PayType
			, e.Status
			, g.title
			, e.TaxAux 
			, REPLACE((TRIM('|' FROM c.Origins)), '|', ',') ID_salesorigins
		FROM sl_products_prices c
		left join sl_products e on e.ID_products=c.ID_products
		left join sl_products_categories f on c.ID_products=f.ID_products
		left join sl_categories g on g.ID_categories=f.ID_categories 
		WHERE c.Price is not null 
		ORDER BY c.ID_products ,c.FP, c.Price ASC");
									
		print "Content-type: application/octetstream\n";
		print "Content-disposition: attachment; filename=$fname\n\n";
		print "$strHeader\r\n";
		
		
		while ($rec_ext = $sth_ext->fetchrow_hashref()) {
				my $sql_filters = '';
				# $sql_filters .= " AND BankDate >= '".&filter_values($in{'from_date'})."'" if ($in{'to_date'});
				# $sql_filters .= " AND BankDate <= '".&filter_values($in{'to_date'})."'" if ($in{'to_date'});
				
				my ($ids) = $in_data[9];
				$query = "SELECT group_concat(sl_salesorigins.Channel )Channels FROM sl_salesorigins WHERE sl_salesorigins.Status='Active'";
	
				if ($rec_ext->{'ID_salesorigins'} ne ''){
					$query .= " AND sl_salesorigins.ID_salesorigins IN (".$rec_ext->{'ID_salesorigins'}.")";
				}
	
				my ($sth) = &Do_SQL($query);

				$rec_int = $sth->fetchrow_hashref();
				$channels = $rec_int->{'Channels'};
				
				
				my $strout;
				$strout .= qq|"$rec_ext->{'ID_products'}"|;
				$strout .= qq|,"$rec_ext->{'Name'}"|;
				$strout .= qq|,"$rec_ext->{'Model'}"|;
				$strout .= qq|,"$rec_ext->{'PriceName'}"|;
				$strout .= qq|,"$rec_ext->{'Price'}"|;
				$strout .= qq|,"$rec_ext->{'FP'}"|;
				$strout .= qq|,"$rec_ext->{'PayType'}"|;
				$strout .= qq|,"$rec_ext->{'Status'}"|;
				$strout .= qq|,"$rec_ext->{'title'}"|;
				$strout .= qq|,"$rec_ext->{'TaxAux'}"|;
				$strout .= qq|,"$channels"\r\n|;
				
				print $strout;
		}

		&auth_logging('report_view','');
		return;
		
	}
	
	print "Content-type: text/html\n\n";
	print &build_page('rep_bi_prices.html');

}


sub rep_bi_inbound {

	if($in{'action'}){
		my ($add_sql,$add_sql2);
		my ($string_status);

		### Si es busqueda por id_admin_user 
		$add_sql .= (int($in{'id_admin_users'}) > 0)? " AND ID_admin_users = ".int($in{'id_admin_users'}):"";

		### Si es busqueda por id_admin_user 
		if ($in{'status'} =~ m/\|/){
			my @arr_status = split /\|/ , $in{'status'};
			for (0..$#arr_status) {
				$string_status .= "'".$arr_status[$_]."',";
			}
			chop $string_status;
			$add_sql .= " AND Status IN($string_status)";
		}else{
			$add_sql .= ($in{'status'})? " AND Status IN('$in{'status'}')":"";
		}


		if ($in{'ptype'} =~ m/\|/){
			my @arr_ptype = split /\|/ , $in{'ptype'};
			for (0..$#arr_ptype) {
				$string_ptype .= "'".$arr_ptype[$_]."',";
			}
			chop $string_ptype;
			$add_sql .= " AND sl_orders.Ptype IN($string_ptype)";
		}else{
			$add_sql .= ($in{'ptype'})? " AND sl_orders.Ptype IN('$in{'ptype'}')":"";
		}


		if ($in{'id_salesorigins'} =~ m/\|/){
			my @arr_salesorigins = split /\|/ , $in{'id_salesorigins'};
			for (0..$#arr_salesorigins) {
				$string_salesorigins .= "'".$arr_salesorigins[$_]."',";
			}
			chop $string_salesorigins;
			$add_sql .= " AND sl_orders.ID_salesorigins IN($string_salesorigins)";
		}else{
			$add_sql .= ($in{'id_salesorigins'})? " AND sl_orders.ID_salesorigins IN('$in{'id_salesorigins'}')":"";
		}



		###### Busqueda por rango de fecha de order
		if ($in{'from_date'} and $in{'to_date'}){
			$add_sql .= " AND sl_orders.Date BETWEEN '$in{'from_date'}' AND '$in{'to_date'}'";
		}else{
			if ($in{'from_date'}){
				$add_sql .= " AND sl_orders.Date >= '$in{'from_date'}' ";
			}
			if ($in{'to_date'}){
				$add_sql .= " AND sl_orders.Date <= '$in{'to_date'}' ";
			}
		}

		###### Busqueda por rango de fecha de venta
		if ($in{'from_sales_date'} and $in{'to_sales_date'}){
			$add_sql .= " AND IF(sl_orders.Ptype <> 'COD', (SELECT CapDate FROM sl_orders_payments WHERE sl_orders_payments.ID_orders=sl_orders.ID_orders AND Captured='Yes' LIMIT 1), PostedDate) BETWEEN '$in{'from_sales_date'}' AND '$in{'to_sales_date'}'";
		}else{
			if ($in{'from_sales_date'}){
				$add_sql .= " AND IF(sl_orders.Ptype <> 'COD', (SELECT CapDate FROM sl_orders_payments WHERE sl_orders_payments.ID_orders=sl_orders.ID_orders AND Captured='Yes' LIMIT 1), PostedDate) >= '$in{'from_sales_date'}' ";
			}
			if ($in{'to_sales_date'}){
				$add_sql .= " AND IF(sl_orders.Ptype <> 'COD', (SELECT CapDate FROM sl_orders_payments WHERE sl_orders_payments.ID_orders=sl_orders.ID_orders AND Captured='Yes' LIMIT 1), PostedDate) <= '$in{'to_sales_date'}' ";
			}
		}
		
		my $fname   = 'sales_summary_'.$cfg{'app_title'}.'.csv';
		$fname =~ s/\s/_/g;
		
		my $strHeader = qq|"ID USUARIO","USUARIO","FORMA DE PAGO","CANTIDAD DE ORDENES","CANTIDAD DE PRODUCTOS","SUBTOTAL","DESCUENTO","IVA","ENVIO","TOTAL"|;
		
		$query_list = "
			SELECT 
				sl_orders.ID_admin_users, 
				(select CONCAT (UPPER(FirstName),' ',UPPER(MiddleName),' ',UPPER(LastName)) as nombre from admin_users where sl_orders.ID_admin_users=ID_admin_users) Name ,
				sl_orders.Ptype, 
				COUNT(sl_orders.ID_orders), 
				SUM(sl_orders_products.Quantity), 
				( SUM(sl_orders_products.SalePrice)), 
				SUM(sl_orders_products.Discount), 
				( SUM(sl_orders_products.Tax)+SUM(sl_orders_products.ShpTax) ), 
				SUM(sl_orders_products.Shipping), 
				( (SUM(sl_orders_products.SalePrice) + SUM(sl_orders_products.Shipping) + SUM(sl_orders_products.Tax) + SUM(sl_orders_products.ShpTax))-SUM(sl_orders_products.Discount) ), 
				sl_orders.ID_salesorigins, 
				IF(	sl_orders.Ptype <> 'COD', PostedDate, (SELECT CapDate FROM sl_orders_payments WHERE sl_orders_payments.ID_orders=sl_orders.ID_orders AND Captured='Yes' LIMIT 1)) PostedDate,
				sl_orders.Date 
			FROM 
				sl_orders 
				INNER JOIN
				(
					SELECT
						sl_orders_products.ID_orders,
						SUM(sl_orders_products.Quantity)Quantity,
						SUM(sl_orders_products.SalePrice)SalePrice,
						SUM(sl_orders_products.Shipping)Shipping,
						SUM(sl_orders_products.Discount)Discount,
						SUM(sl_orders_products.Tax)Tax,
						SUM(sl_orders_products.ShpTax)ShpTax
					FROM
						sl_orders_products
					WHERE 1 
						AND sl_orders_products.Status NOT IN('Order Cancelled', 'Inactive')
					GROUP BY
						sl_orders_products.ID_orders
				)sl_orders_products ON sl_orders_products.ID_orders=sl_orders.ID_orders
			WHERE 1 
				$add_sql
			GROUP BY 
				sl_orders.ID_admin_users, 
				sl_orders.Ptype
			ORDER BY Name ASC";
		
		my($sth) = &Do_SQL($query_list);
		
		if ($sth->rows() > 0){
			print "Content-type: application/octetstream\n";
			print "Content-disposition: attachment; filename=$fname\n\n";
			print "$strHeader\r\n";
			
			while( my($id_admin_users,$name_user,$ptype,$num_orders,$num_products,$subtotal,$discount,$tax,$shipping,$total) = $sth->fetchrow() )
			{
				$strout .= qq|"$id_admin_users","$name_user","$ptype","$num_orders","$num_products","$subtotal","$discount","$tax","$shipping","$total"|."\r\n";
			}

			print $strout;
			
			&auth_logging('report_view','');
			return;
		}else{
			$va{'message'} = &trans_txt('search_nomatches');
		}
	}
	
	print "Content-type: text/html\n\n";
	print &build_page('rep_bi_inbound.html');
}


sub rep_bi_allorders_by_capdate {
#-----------------------------------------
# Created on: 06/02/15  11:01:39 By  HC
# Forms Involved: 
# Description : Extrae la informacion de ordenes ( Con del reporte rep_bi_allorders ) 
# Parameters :

	if($in{'action'}){
		
		my ($query_list);
		my $maxprod=1;
		my $info_user =	'';
		my $info_pprod = '';
		my $info_oprod = '';
		my $info_time = '';
		my $modshipped = '';
		my $strout = '';
		
		## Si type eq 'order' 1 linea por orden
		$maxprod = 10 if $in{'type'} eq 'order';
		
		###### Busqueda por rango de fecha de order
		my $where_date = ($in{'from_date'} and $in{'to_date'}) ? " AND sl_orders.Date BETWEEN '$in{'from_date'}' AND '$in{'to_date'}'" : '';

		###### Busqueda por rango de fecha de venta
		my $where_posteddate = ($in{'from_sales_date'} and $in{'to_sales_date'}) ? "AND sl_orders.PostedDate BETWEEN '$in{'from_sales_date'}' AND '$in{'to_sales_date'}'" : '';


		### Filtro por usuarios LISTENUP
		my $where_listenup = '';
		if( $usr{'id_salesorigins_view'} == 22 ){
			$where_listenup = " AND sl_orders.ID_salesorigins = 22";
		}


		### Busqueda por rango de tiempo
		if($in{'from_time'} or $in{'to_time'}){

			$in{'from_time'} 	= "00:00:00"	if !$in{'from_time'};
			$in{'to_time'} 		= "23:59:59"	if !$in{'to_time'};
			$info_time = " AND Time BETWEEN '$in{'from_time'}' AND '$in{'to_time'}'";

		}

		### Si es busqueda por id_admin_user 
		$info_user = "WHERE ID_admin_users = ".int($in{'id_admin_users'})." "	if $in{'id_admin_users'};
		

		### Si es busqueda por id_products
		if($in{'id_products'}){			
			$info_oprod = " AND 0 < (SELECT COUNT(DISTINCT ID_orders) FROM sl_orders_products WHERE ID_orders = sl_orders.ID_orders AND RIGHT(ID_products,6) = '".int($in{'id_products'})."' AND Status = 'Active') ";
		}

		### Busqueda Shipped o no
		$modshipped = $in{'status'} ? " AND sl_orders.Status = 'Shipped'" : " AND sl_orders.Status NOT IN('System Error')";

		my $fname   = 'all_orders_'.$cfg{'app_title'}.'.csv';
		$fname =~ s/\s/_/g;
		
		my $strHeader = "Channel,TPago,DID,Orden,Status,Primer Llamada,Fecha,Hora,Fecha de Venta,Fecha de Envio,Fecha de Ingreso,Estado,Municipio,CP,Id Zona,Nombre Zona,DMA";
		for(1..$maxprod){
				$strHeader .=",Cant$_,Cod$_,Prod$_,Cost$_,Prec$_,Desc$_,Tax$_,Envio$_,Tax Envio$_";
			}
		## Si type eq 'order' 1 linea por orden	
		$strHeader .= ",Total Cost,Total Products,Total Descuento,Total Taxes,Total Envio,Total Orden"	if $in{'type'} eq 'order';
		
		$strHeader .= ",Familia de Producto,Usuario,Grupo,Rush Shipping,ID Usuario,Usuario Direksys,CID,PHONE1,PHONE2,CELLPHONE,ID Cliente";
		
		&auth_logging('report_view','');
			
		#print "Content-type: text/html\n\n";
		print "Content-type: application/octetstream\n";
		print "Content-disposition: attachment; filename=$fname\n\n";
		print "$strHeader\r\n";

		$query_list = "SELECT 
				   IDAgent,
				   AgentName,
				   IF(user_type IS NOT NULL AND user_type != '',user_type,'N/A') AS user_type,
				   IF(Orders IS NOT NULL,Orders,0)AS Orders,
				   ID_user,
				   UsernameDireksys
				FROM
				(
				   SELECT 
				      ID_admin_users AS IDAgent,
				      (CONCAT(UPPER(admin_users.FirstName),' ',UPPER(admin_users.MiddleName),' ',UPPER(admin_users.LastName))) AS AgentName,
				      user_type, admin_users.ID_admin_users as ID_user, admin_users.Username as UsernameDireksys
				   FROM admin_users 
				   	". $info_user ."
				)AS tmp_agent
				
				LEFT JOIN
				(
				   SELECT
				      ID_admin_users AS IDA,
				      COUNT(ID_Orders) AS Orders
				   FROM sl_orders
				      WHERE 1
				      ". $modshipped ."
				      ". $where_date ."
				      ". $where_posteddate ."
				      ". $info_time ." 
				      ". $where_listenup ."
				      ". $info_oprod ."
				      GROUP BY ID_admin_users
				)AS tmp_order
				ON tmp_order.IDA = tmp_agent.IDAgent
				HAVING Orders > 0
				ORDER BY AgentName;";
		
		my ($sth) = &Do_SQL($query_list);
		if($sth->rows() > 0){
			
			while(my($idagent,$agentname,$user_type,$orders,$iduser_direksys,$user_direksys) = $sth->fetchrow()){

				if($in{'from_time'} or $in{'to_time'}) {
					$in{'from_time'} 	= "00:00:00"	if !$in{'from_time'};
					$in{'to_time'} 		= "23:59:59"	if !$in{'to_time'};
					$info_timep = " AND sl_orders.Time BETWEEN '$in{'from_time'}' AND '$in{'to_time'}'";
				}
				
				# /*, IFNULL(CountyName,'N/A') AS County*/
				# /*, if(sl_orders.Ptype<>'COD',(SELECT CapDate FROM sl_orders_payments WHERE sl_orders_payments.ID_orders=sl_orders.ID_orders AND Captured='Yes' LIMIT 1),sl_orders.PostedDate)PostedDate*/
				my $sth = &Do_SQL("SELECT 
									* 
								FROM (
										SELECT 
											DISTINCT ID_orders
											, IF(DNIS IS NULL,0,DNIS) AS DNIS
											, sl_orders.Date
											, sl_orders.Time
											, (shp_State)AS State, shp_City AS County
											, sl_orders.Status,Channel,IF(DMA_DESC IS NULL OR DMA_DESC = '','N/A',DMA_DESC) AS DMA_DESC, IF(shp_type = 2, 'Yes','No')AS Rush
											, sl_orders.shp_Zip, sl_orders.ID_zones, (SELECT Name FROM sl_zones WHERE sl_zones.ID_zones=sl_orders.ID_zones) as zone_name
											, (SELECT CapDate FROM sl_orders_payments WHERE sl_orders_payments.ID_orders=sl_orders.ID_orders AND Captured='Yes' LIMIT 1)CapDate
											, sl_orders.PostedDate
											, (SELECT GROUP_CONCAT(DISTINCT ShpDate) FROM sl_orders_products  WHERE sl_orders_products.ID_orders=sl_orders.ID_orders AND ShpDate > '1900-01-01' GROUP BY ID_orders) as ShpDate
											, IF(sl_orders.Ptype='COD',(SELECT CapDate FROM sl_orders_payments WHERE sl_orders_payments.ID_orders=sl_orders.ID_orders AND Captured='Yes' LIMIT 1),'')CapDateCOD
											, sl_orders.ID_customers
											, sl_orders.PType
											, sl_orders.first_call
										FROM sl_orders 
											LEFT JOIN sl_zipcodes ON sl_orders.shp_Zip = sl_zipcodes.ZipCode
											LEFT JOIN sl_zipdma ON sl_zipdma.ZipCode = sl_zipcodes.ZipCode 
											LEFT join sl_salesorigins on (sl_orders.ID_salesorigins=sl_salesorigins.ID_salesorigins)
										WHERE 
											sl_orders.ID_admin_users = ". $idagent ."
											". $modshipped ."
											". $where_date ."
											". $where_posteddate ."
											". $info_oprod ."
											". $query_converted ."
											". $where_date ."
											". $info_timep ." 
											". $nopreorder ."
											". $where_listenup ."
									)orders
								WHERE 
									1
								ORDER BY 
									Date,Status,Time,ID_orders");
				                   
				while(my($id_orders,$id_dids,$date,$time_order,$state,$county,$status,$salesorigins,$dma_name,$rush_shipping,$shp_zip,$id_zones,$zone_name,$capdate,$posteddate,$shpdate,$capdatecod,$id_customers,$tpago,$first_call) = $sth->fetchrow()){
					my $items=0;
					my $total = 0;
					my $tcost = 0;
					my $tdisc = 0;
					my $ttax = 0;
					my $tshp = 0;
					my $torder = 0;
					my $strprod = '';
					my $strout='';
					my $first_call = 'N/A';
					my $catname;
					$first_call = 'Unknown' if $first_call eq '';
					$tpago = 'Money Order'	if $tpago eq '';

					my $sth_cust = &Do_SQL("SELECT sl_customers.ID_customers
												, sl_customers.CID
												, sl_customers.Phone1
												, sl_customers.Phone2
												, sl_customers.Cellphone
											FROM sl_customers 
											WHERE sl_customers.ID_customers = ".$id_customers.";");
					my $customer = $sth_cust->fetchrow_hashref();
					my $cid = $customer->{'CID'};
					my $phone1 = $customer->{'Phone1'};
					my $phone2 = $customer->{'Phone2'};
					my $cellphone = $customer->{'Cellphone'};
	
					# Se ocultan datos temporalmente
					$state = &temp_hide_data($state);
					$county = &temp_hide_data($county);
					$shp_zip = &temp_hide_data($shp_zip);

					## Si type eq 'order' 1 linea por order
					$strout .= qq|"$salesorigins","$tpago","$id_dids","$id_orders","$status","$first_call","$date","$time_order","$posteddate","$shpdate","$capdate","$state","$county","$shp_zip","$id_zones","$zone_name","$dma_name"| if $in{'type'} eq 'order';
					
					my $sthi = &Do_SQL("SELECT IF(LEFT(sl_orders_products.ID_products,3) = 100 AND LENGTH(Related_ID_products) = 9 and left(Related_ID_products,3)=400,Related_ID_products,sl_orders_products.ID_products) AS ID_products,
						IF(sl_parts.Name IS NOT NULL,sl_parts.Name,IF(sl_services.Name IS NOT NULL,sl_services.Name,sl_products.Name)) AS Pname,
						Quantity,SalePrice,sl_orders_products.Discount,sl_orders_products.Tax,sl_orders_products.Shipping,sl_orders_products.ShpTax
						,IF(sl_orders_products.Cost > 0,sl_orders_products.Cost,IF(SLTV_NetCost >=0,SLTV_NetCost,0))AS SLTV_NetCost,
						Channel, ID_categories
					FROM sl_orders_products 
					INNER JOIN sl_orders on (sl_orders_products.ID_orders = sl_orders.ID_orders)
					LEFT JOIN sl_salesorigins on (sl_orders.ID_salesorigins=sl_salesorigins.ID_salesorigins)
					LEFT JOIN sl_products ON sl_products.ID_products = RIGHT(sl_orders_products.ID_products,6)
					LEFT JOIN sl_services ON sl_services.ID_services = RIGHT(sl_orders_products.ID_products,4)
					LEFT JOIN sl_parts ON (ID_parts = RIGHT(Related_ID_products,4) and left(Related_ID_products,3)=400 )
					WHERE 
						sl_orders_products.ID_orders = ". $id_orders ."
						AND sl_orders_products.Status NOT IN('Order Cancelled', 'Inactive')
						$where_listenup 
					ORDER BY  
						ID_orders_products ;");
					
					$prodline = 0;
					while(my($id_products,$pname,$qty,$sprice,$pdisc,$tax,$shp,$shptax,$netcost,$salesorigins,$idcat) = $sthi->fetchrow()){

						++$prodline;
						$rush_shipping = 'Yes' if $id_products eq '600001046';

						###
						### Product Family
						###
						if($prodline == 1 or $in{'type'} ne 'order') {

							if(!$idcat){

								my ($sthc) = Do_SQL("SELECT ID_categories FROM sl_products_categories WHERE ID_products = RIGHT($id_products,6) LIMIT 1;");
								$idcat = $sthc->fetchrow();

							}

							$catname = $idcat ? &load_name('sl_categories','ID_categories', $idcat, 'Title') : 'N/A';

						}

						## Si type eq 'order' 1 linea por orden
						if($in{'type'} eq 'order'){

							$strprod .= qq|,"$qty","|.&format_sltvid($id_products).qq|","$pname","$netcost","$sprice","$pdisc","$tax","$shp","$shptax"| if ($prodline<=$maxprod);
							$items++;
							$total+= $sprice;
							$tdisc+=$pdisc;

							$ttax+=$tax;
							$ttax+=$shptax;

							$tshp+=$shp;
							$tcost+=$netcost;
							$torder+=$sprice-$pdisc+$tax+$shp+$shptax;

						}else{
							$strout .= qq|"$salesorigins","$tpago","$id_dids","$id_orders","$status","$first_call","$date","$time_order","$posteddate","$shpdate","$capdate","$state","$county","$dma_name","$qty","|.&format_sltvid($id_products).qq|","$pname","$netcost","$sprice","$pdisc","$tax","$shp","$catname",$agentname","$user_type","$rush_shipping"|;
						}

					}
					
					## Si type eq 'order' 1 linea por orden
					if($in{'type'} eq 'order'){
						for ($items..$maxprod-1){
							$strprod .= ",,,,,,,,,";
						}
						
						# Se ocultan datos temporalmente
						$cid = &temp_hide_data($cid,'phone');
						$phone1 = &temp_hide_data($phone1,'phone');
						$phone2 = &temp_hide_data($phone2,'phone');
						$cellphone = &temp_hide_data($cellphone,'phone');

						$strout .= qq|$strprod,"$tcost","$total","$tdisc","$ttax","$tshp","$torder","$catname","$agentname","$user_type","$rush_shipping","$iduser_direksys","$user_direksys","$cid","$phone1","$phone2","$cellphone"|;
					}
					$strout .= qq|,"$id_customers"|;
					$strout .= "\r\n";

					print $strout;
				}
			}

			return;

		}else{
			$va{'message'} = &trans_txt('search_nomatches');
		}
	}
	
	print "Content-type: text/html\n\n";
	print &build_page('rep_bi_allorders_by_capdate.html');
}

sub rep_bi_allorders_by_capdate_v2 {
#-----------------------------------------
# Created on: 06/02/15  11:01:39 By  HC
# Forms Involved: 
# Description : Extrae la informacion de ordenes ( Con del reporte rep_bi_allorders ) 
# Parameters :
	my $log_query;
	if($in{'action'}){
		
		my ($query_list);
		my $maxprod=1;
		my $info_user =	'';
		my $info_pprod = '';
		my $info_oprod = '';
		my $info_time = '';
		my $modshipped = '';
		my $strout = '';
		
		## Si type eq 'order' 1 linea por orden
		$maxprod = 10 if $in{'type'} eq 'order';
		
		###### Busqueda por rango de fecha de order
		my $where_date = ($in{'from_date'} and $in{'to_date'}) ? " AND sl_orders.Date BETWEEN '$in{'from_date'}' AND '$in{'to_date'}'" : '';

		###### Busqueda por rango de fecha de venta
		my $where_posteddate = ($in{'from_sales_date'} and $in{'to_sales_date'}) ? "AND sl_orders.PostedDate BETWEEN '$in{'from_sales_date'}' AND '$in{'to_sales_date'}'" : '';


		### Filtro por usuarios LISTENUP
		my $where_listenup = '';
		if( $usr{'id_salesorigins_view'} == 22 ){
			$where_listenup = " AND sl_orders.ID_salesorigins = 22";
		}


		### Busqueda por rango de tiempo
		if($in{'from_time'} or $in{'to_time'}){

			$in{'from_time'} 	= "00:00:00"	if !$in{'from_time'};
			$in{'to_time'} 		= "23:59:59"	if !$in{'to_time'};
			$info_time = " AND Time BETWEEN '$in{'from_time'}' AND '$in{'to_time'}'";

		}

		### Si es busqueda por id_admin_user 
		$info_user = "WHERE ID_admin_users = ".int($in{'id_admin_users'})." "	if $in{'id_admin_users'};
		

		### Si es busqueda por id_products
		if($in{'id_products'}){			
			$info_oprod = " AND 0 < (SELECT COUNT(DISTINCT ID_orders) FROM sl_orders_products WHERE ID_orders = sl_orders.ID_orders AND RIGHT(ID_products,6) = '".int($in{'id_products'})."' AND Status = 'Active') ";
		}

		### Busqueda Shipped o no
		$modshipped = $in{'status'} ? " AND sl_orders.Status = 'Shipped'" : " AND sl_orders.Status NOT IN('System Error')";

		my $fname   = 'all_orders_'.$cfg{'app_title'}.'.csv';
		$fname =~ s/\s/_/g;
		
		my $strHeader = "Channel,TPago,Orden,Status,Fecha,Hora,Fecha de Venta,Fecha de Envio,Fecha de Ingreso";
		for(1..$maxprod){
				#$strHeader .=",Cant$_,Cod$_,Prod$_,Cost$_,Prec$_,Desc$_,Tax$_,Envio$_,Tax Envio$_";
			}
		## Si type eq 'order' 1 linea por orden	
		$strHeader .= ",Total Products,Total Descuento,Total Taxes,Total Envio,Total Orden"	if $in{'type'} eq 'order';
		
		$strHeader .= ",Familia de Producto,Usuario,Grupo,ID Usuario,Usuario Direksys,CID,PHONE1,PHONE2,CELLPHONE";
		
		&auth_logging('report_view','');
			
		

		$query_list = "SELECT 
				   IDAgent,
				   AgentName,
				   IF(user_type IS NOT NULL AND user_type != '',user_type,'N/A') AS user_type,
				   IF(Orders IS NOT NULL,Orders,0)AS Orders,
				   ID_user,
				   UsernameDireksys
				FROM
				(
				   SELECT 
				      ID_admin_users AS IDAgent,
				      (CONCAT(UPPER(admin_users.FirstName),' ',UPPER(admin_users.MiddleName),' ',UPPER(admin_users.LastName))) AS AgentName,
				      user_type, admin_users.ID_admin_users as ID_user, admin_users.Username as UsernameDireksys
				   FROM admin_users 
				   	". $info_user ."
				)AS tmp_agent
				
				LEFT JOIN
				(
				   SELECT
				      ID_admin_users AS IDA,
				      COUNT(ID_Orders) AS Orders
				   FROM sl_orders
				      WHERE 1
				      ". $modshipped ."
				      ". $where_date ."
				      ". $where_posteddate ."
				      ". $info_time ." 
				      ". $where_listenup ."
				      ". $info_oprod ."
				      GROUP BY ID_admin_users
				)AS tmp_order
				ON tmp_order.IDA = tmp_agent.IDAgent
				HAVING Orders > 0
				ORDER BY AgentName;";
		$log_query = $query_list . "\n\n ================================== \n\n";
		my ($sth) = &Do_SQL($query_list);
		if($sth->rows() > 0){
				#print "Content-type: text/html\n\n";
			print "Content-type: application/octetstream\n";
			print "Content-disposition: attachment; filename=$fname\n\n";
			print "$strHeader\r\n";
			while(my($idagent,$agentname,$user_type,$orders,$iduser_direksys,$user_direksys) = $sth->fetchrow()){

				if($in{'from_time'} or $in{'to_time'}) {
					$in{'from_time'} 	= "00:00:00"	if !$in{'from_time'};
					$in{'to_time'} 		= "23:59:59"	if !$in{'to_time'};
					$info_timep = " AND sl_orders.Time BETWEEN '$in{'from_time'}' AND '$in{'to_time'}'";
				}
				
				# /*, IFNULL(CountyName,'N/A') AS County*/
				# /*, if(sl_orders.Ptype<>'COD',(SELECT CapDate FROM sl_orders_payments WHERE sl_orders_payments.ID_orders=sl_orders.ID_orders AND Captured='Yes' LIMIT 1),sl_orders.PostedDate)PostedDate*/
				my $query = "SELECT 
									* 
								FROM (
										SELECT 
											DISTINCT ID_orders
											, IF(DNIS IS NULL,0,DNIS) AS DNIS
											, sl_orders.Date
											, sl_orders.Time
											, (shp_State)AS State, shp_City AS County
											, sl_orders.Status,Channel,IF(DMA_DESC IS NULL OR DMA_DESC = '','N/A',DMA_DESC) AS DMA_DESC, IF(shp_type = 2, 'Yes','No')AS Rush
											, sl_orders.shp_Zip, sl_orders.ID_zones, (SELECT Name FROM sl_zones WHERE sl_zones.ID_zones=sl_orders.ID_zones) as zone_name
											, (SELECT CapDate FROM sl_orders_payments WHERE sl_orders_payments.ID_orders=sl_orders.ID_orders AND Captured='Yes' LIMIT 1)CapDate
											, sl_orders.PostedDate
											, (SELECT GROUP_CONCAT(DISTINCT ShpDate) FROM sl_orders_products  WHERE sl_orders_products.ID_orders=sl_orders.ID_orders AND ShpDate > '1900-01-01' GROUP BY ID_orders) as ShpDate
											, IF(sl_orders.Ptype='COD',(SELECT CapDate FROM sl_orders_payments WHERE sl_orders_payments.ID_orders=sl_orders.ID_orders AND Captured='Yes' LIMIT 1),'')CapDateCOD
											, sl_orders.ID_customers
											, sl_orders.PType
											, sl_orders.first_call
										FROM sl_orders 
											LEFT JOIN sl_zipcodes ON sl_orders.shp_Zip = sl_zipcodes.ZipCode
											LEFT JOIN sl_zipdma ON sl_zipdma.ZipCode = sl_zipcodes.ZipCode 
											LEFT join sl_salesorigins on (sl_orders.ID_salesorigins=sl_salesorigins.ID_salesorigins)
										WHERE 
											sl_orders.ID_admin_users = ". $idagent ."
											". $modshipped ."
											". $where_date ."
											". $where_posteddate ."
											". $info_oprod ."
											". $query_converted ."
											". $where_date ."
											". $info_timep ." 
											". $nopreorder ."
											". $where_listenup ."
									)orders
								WHERE 
									1
								ORDER BY 
									Date,Status,Time,ID_orders";
				my $sth = &Do_SQL($query);
				#$log_query .= $query . "\n\n ================================== \n\n";         
				while(my($id_orders,$id_dids,$date,$time_order,$state,$county,$status,$salesorigins,$dma_name,$rush_shipping,$shp_zip,$id_zones,$zone_name,$capdate,$posteddate,$shpdate,$capdatecod,$id_customers,$tpago,$first_call) = $sth->fetchrow()){
					my $items=0;
					my $total = 0;
					my $tcost = 0;
					my $tdisc = 0;
					my $ttax = 0;
					my $tshp = 0;
					my $torder = 0;
					my $strprod = '';
					my $strout='';
					my $catname;
					$first_call = 'Unknown' if $first_call eq '';					
					$tpago = 'Money Order'	if $tpago eq '';

					my $sth_cust = &Do_SQL("SELECT sl_customers.ID_customers
												, sl_customers.CID
												, sl_customers.Phone1
												, sl_customers.Phone2
												, sl_customers.Cellphone
											FROM sl_customers 
											WHERE sl_customers.ID_customers = ".$id_customers.";");
					my $customer = $sth_cust->fetchrow_hashref();
					my $cid = $customer->{'CID'};
					my $phone1 = $customer->{'Phone1'};
					my $phone2 = $customer->{'Phone2'};
					my $cellphone = $customer->{'Cellphone'};
					
					## Si type eq 'order' 1 linea por order
					$strout .= qq|"$salesorigins","$tpago","$id_orders","$status","$date","$time_order","$posteddate","$shpdate","$capdate"| if $in{'type'} eq 'order';
					$query = "SELECT IF(LEFT(sl_orders_products.ID_products,3) = 100 AND LENGTH(Related_ID_products) = 9 and left(Related_ID_products,3)=400,Related_ID_products,sl_orders_products.ID_products) AS ID_products,
						IF(sl_parts.Name IS NOT NULL,sl_parts.Name,IF(sl_services.Name IS NOT NULL,sl_services.Name,sl_products.Name)) AS Pname,
						Quantity,SalePrice,sl_orders_products.Discount,sl_orders_products.Tax,sl_orders_products.Shipping,sl_orders_products.ShpTax
						,IF(sl_orders_products.Cost > 0,sl_orders_products.Cost,IF(SLTV_NetCost >=0,SLTV_NetCost,0))AS SLTV_NetCost,
						Channel, ID_categories
					FROM sl_orders_products 
					INNER JOIN sl_orders on (sl_orders_products.ID_orders = sl_orders.ID_orders)
					LEFT JOIN sl_salesorigins on (sl_orders.ID_salesorigins=sl_salesorigins.ID_salesorigins)
					LEFT JOIN sl_products ON sl_products.ID_products = RIGHT(sl_orders_products.ID_products,6)
					LEFT JOIN sl_services ON sl_services.ID_services = RIGHT(sl_orders_products.ID_products,4)
					LEFT JOIN sl_parts ON (ID_parts = RIGHT(Related_ID_products,4) and left(Related_ID_products,3)=400 )
					WHERE 
						sl_orders_products.ID_orders = ". $id_orders ."
						AND sl_orders_products.Status NOT IN('Order Cancelled', 'Inactive')
						$where_listenup 
					ORDER BY  
						ID_orders_products ;";
					my $sthi = &Do_SQL($query);
					#$log_query .= $query . "\n\n ================================== \n\n";     
					$prodline = 0;
					while(my($id_products,$pname,$qty,$sprice,$pdisc,$tax,$shp,$shptax,$netcost,$salesorigins,$idcat) = $sthi->fetchrow()){

						++$prodline;
						$rush_shipping = 'Yes' if $id_products eq '600001046';

						###
						### Product Family
						###
						if($prodline == 1 or $in{'type'} ne 'order') {

							if(!$idcat){

								my ($sthc) = Do_SQL("SELECT ID_categories FROM sl_products_categories WHERE ID_products = RIGHT($id_products,6) LIMIT 1;");
								$idcat = $sthc->fetchrow();

							}

							$catname = $idcat ? &load_name('sl_categories','ID_categories', $idcat, 'Title') : 'N/A';

						}

						## Si type eq 'order' 1 linea por orden
						if($in{'type'} eq 'order'){

							$strprod .= qq|,"$sprice","$pdisc","$tax","$shp"| if ($prodline<=$maxprod);
							$items++;
							$total+= $sprice;
							$tdisc+=$pdisc;

							$ttax+=$tax;
							$ttax+=$shptax;

							$tshp+=$shp;
							$tcost+=$netcost;
							$torder+=$sprice-$pdisc+$tax+$shp+$shptax;

						}else{
							$strout .= qq|"$salesorigins","$tpago","$id_orders","$status","$date","$time_order","$posteddate","$shpdate","$capdate","$sprice","$pdisc","$tax","$shp"|;
						}

					}
					
					## Si type eq 'order' 1 linea por orden
					if($in{'type'} eq 'order'){
						for ($items..$maxprod-1){
							$strprod .= ",,,,,,,,,";
						}
						
						$strout .= qq|,"$total","$tdisc","$ttax","$tshp","$torder","$catname","$agentname","$user_type","$iduser_direksys","$user_direksys","$cid","$phone1","$phone2","$cellphone"|;
					}
					$strout .= qq|,"$id_customers"|;
					$strout .= "\r\n";

					print $strout;
				}
			}
			log_reports($log_query, 'rep_bi_allorders_by_capdate_v2');
			return;

		}else{
			$va{'message'} = &trans_txt('search_nomatches');
		}
	}
	log_reports($log_query, 'rep_bi_allorders_by_capdate_v2');
	print "Content-type: text/html\n\n";
	print &build_page('rep_bi_allorders_by_capdate_v2.html');
}

#############################################################################
#############################################################################
#   Function: rep_bi_orders_statistics
#
#       Es: Reporte de Detalle de Pagos
#       En: 
#
#
#    Created on: 07/05/2015
#
#    Author: ISC Alejandro Diaz
#
#    Modifications:
#
#        - Modified on ** by *** : 
#
#   Parameters:
#
#      - 
#
#  Returns:
#
#
#   See Also:
#
#      <>
#
sub rep_bi_orders_statistics {
#############################################################################
#############################################################################

	if ($in{'action'}){
		
		my $output = '';
		
		my $fname   = 'orders_statistics '.$cfg{'app_title'}.'.csv';
		$fname =~ s/\s/_/g;
		
		my $strHeader = qq|"Total Cost","Total Products","Margen %","Total Envio","Channel","TPago","Orden","Status","Fecha de Pedido","Fecha de Factura"|;
		
		## Busqueda por consolas
		my $add_sql;
		if ($in{'id_salesorigins'}){
			my @arr_salesorigins = split /\|/ , $in{'id_salesorigins'};
			$add_sql .= " AND sl_orders.ID_salesorigins IN(". join(',', @arr_salesorigins) .")";
		}

		my ($string_status);
		if ($in{'status'}){
			if ($in{'status'} =~ m/\|/){
				my @arr_status = split /\|/ , $in{'status'};
				for (0..$#arr_status) {
					$string_status .= "'".$arr_status[$_]."',";
				}
				chop $string_status;
				$add_sql .= " AND sl_orders.Status IN($string_status) ";
			}else{
				$add_sql .= ($in{'status'})? " AND sl_orders.Status IN('$in{'status'}') ":"";
			}
		}

		if ($in{'from_date'} ne '' and  $in{'to_date'} ne '' and $in{'from_date'} eq $in{'to_date'}){
			$add_sql .= " AND sl_orders.Date = '$in{'from_date'}'";
		}else{
			if ($in{'from_date'}){
				$add_sql .= " AND sl_orders.Date >= '$in{'from_date'}' ";
			}

			if ($in{'to_date'}){
				$add_sql .= " AND sl_orders.Date <= '$in{'to_date'}' ";
			}
		}
		
		$sql = "SELECT
			sl_salesorigins.Channel
			, sl_orders.Ptype
			, sl_orders.ID_orders
			, sl_orders.Status
			, sl_orders.Date
			, (SELECT Date(cu_invoices.doc_date) FROM cu_invoices_lines LEFT JOIN cu_invoices ON cu_invoices.ID_invoices=cu_invoices_lines.ID_invoices AND cu_invoices.Status='Certified' WHERE cu_invoices_lines.ID_orders=sl_orders.ID_orders GROUP BY cu_invoices_lines.ID_invoices ORDER BY cu_invoices.doc_date ASC LIMIT 1)doc_date
		FROM sl_orders
		LEFT JOIN sl_salesorigins ON sl_orders.ID_salesorigins=sl_salesorigins.ID_salesorigins
		WHERE 1
		AND sl_orders.Status <> 'System Error'
		$add_sql";
		
		my ($sth) = &Do_SQL($sql);
		
			my $out='';
			my $norders=0;
			my $max_len=0;
			while (my $rec = $sth->fetchrow_hashref()){
				my $output='';
				my $output2='';
				my $output3='';
				$norders++;
				$output .= qq|,"$rec->{'Channel'}","$rec->{'Ptype'}","$rec->{'ID_orders'}","$rec->{'Status'}","$rec->{'Date'}","$rec->{'doc_date'}"|;

				$sql = "SELECT 
				(400000000 + sl_parts.ID_parts)SKU
				, sl_skus_parts.Qty
				, sl_parts.Model
				, sl_parts.Name
				,(
					SELECT Price
					FROM sl_purchaseorders_items 
					INNER JOIN sl_purchaseorders USING(ID_purchaseorders) 
					WHERE ID_products=(400000000 + sl_parts.ID_parts)
					AND sl_purchaseorders_items.Received>0
					AND sl_purchaseorders.Status NOT IN ('Cancelled')
					ORDER BY sl_purchaseorders_items.ID_purchaseorders DESC 
					LIMIT 1
				)AS Cost
				, sl_orders_products.ID_orders_products
				, sl_orders_products.SalePrice
				, sl_orders_products.Shipping
				FROM sl_orders_products
				INNER JOIN sl_products ON RIGHT(sl_orders_products.ID_products,6)=sl_products.ID_products
				INNER JOIN sl_skus_parts ON sl_skus_parts.ID_sku_products=sl_orders_products.ID_products
				INNER JOIN sl_parts ON sl_parts.ID_parts=sl_skus_parts.ID_parts
				WHERE sl_orders_products.ID_orders='$rec->{'ID_orders'}'
				AND (sl_orders_products.ID_products >= 100000000 AND sl_orders_products.ID_products < 200000000)
				AND sl_orders_products.Status NOT IN ('Order Cancelled','Inactive')
				ORDER BY sl_orders_products.ID_orders_products, sl_skus_parts.ID_skus_parts;";
				my $sth2 = &Do_SQL($sql);
				                   
				my $id_last=0;
				my $lines_prd=0;
				my $recs=0;
				my $total_cost=0;
				my $total_products=0;
				my $margen=0; # (Total Products - Total Cost / Total products)
				my $total_shipping=0;
				while (my $rec2 = $sth2->fetchrow_hashref()){
					my $saleprice = ($id_last != $rec2->{'ID_orders_products'})? $rec2->{'SalePrice'} : 0;

					$recs++;
					
					if ($id_last != $rec2->{'ID_orders_products'}){
						$total_products += $rec2->{'SalePrice'};
						$total_shipping += $rec2->{'Shipping'};
					}

					$total_cost += $rec2->{'Cost'};

					$output2 .= qq|,"$rec2->{'Qty'}","$rec2->{'SKU'}","$rec2->{'Name'}/$rec2->{'Model'}","$rec2->{'Cost'}","$saleprice"|;

					$id_last = $rec2->{'ID_orders_products'};
				}

				$max_len = ($max_len < $recs)? $recs : $max_len;

				$margen = ($total_products > 0)? ((($total_products-$total_cost)/$total_products)*100) : 0;
				$margen = &format_number($margen,2);
				$output3 = qq|"$total_cost","$total_products","$margen","$total_shipping"|;

				$out .= $output3.$output.$output2."\r\n";
				
			}
			&auth_logging('report_view','');

			for (1..$max_len){
				$strHeader .= qq|,"Cant $_","SKU $_","Prod $_","Cost $_","Prec $_"|;
			}

			$strHeader .= "\r\n";
			
			if ($norders){				
				print "Content-type: application/octetstream\n";
				print "Content-disposition: attachment; filename=$fname\n\n";
				print $strHeader;
				print $out;
				
				return;
			}else{
				$va{'message'} = &trans_txt('search_nomatches');
			}
	}
	
	print "Content-type: text/html\n\n";
	print &build_page('rep_bi_orders_statistics.html');
}

#############################################################################
#############################################################################
#   Function: rep_bi_sales_journal_v1
#
#       Es: Reporte de Diario de Ventas version TMK y Mas Ofertas
#       En: 
#
#
#    Created on: 11/05/2015
#
#    Author: ISC Alejandro Diaz
#
#    Modifications:
#
#        - Modified on ** by *** : 
#
#   Parameters:
#
#      - 
#
#  Returns:
#
#
#   See Also:
#
#      <>
#
sub rep_bi_sales_journal_v1 {
#############################################################################
#############################################################################

	if ($in{'action'}){
		
		my $output = '';
		
		my $fname   = 'sales_journal_v1 '.$cfg{'app_title'}.'.csv';
		$fname =~ s/\s/_/g;

		my ($add_sql, $add_sql_cm);

		$add_sql .= ($in{'doc_serial'})? " AND cu_invoices.doc_serial = TRIM('$in{'doc_serial'}') ":"";
		$add_sql .= ($in{'doc_num'})? " AND cu_invoices.doc_num = TRIM('$in{'doc_num'}') ":"";
		$add_sql .= ($in{'id_invoices'})? " AND cu_invoices.ID_invoices = TRIM('$in{'id_invoices'}') ":"";
		$add_sql .= ($in{'id_orders'})? " AND sl_orders.ID_orders = '$in{'id_orders'}' ":"";
		
		$add_sql_cm .= ($in{'doc_serial'})? " AND cu_invoices.doc_serial = TRIM('$in{'doc_serial'}') ":"";
		$add_sql_cm .= ($in{'doc_num'})? " AND cu_invoices.doc_num = TRIM('$in{'doc_num'}') ":"";
		$add_sql_cm .= ($in{'id_invoices'})? " AND cu_invoices.ID_invoices = TRIM('$in{'id_invoices'}') ":"";
		$add_sql_cm .= ($in{'id_creditmemos'})? " AND sl_creditmemos.ID_creditmemos = '$in{'id_creditmemos'}' ":"";

		$add_sql .= ($in{'id_customers'})? " AND cu_invoices.ID_customers = '$in{'id_customers'}' ":"";
		$add_sql_cm .= ($in{'id_customers'})? " AND cu_invoices.ID_customers = '$in{'id_customers'}' ":"";
		
		$add_sql_cm .= ($in{'firstname'})? " AND sl_customers.FirstName LIKE (CONCAT('%',TRIM('$in{'firstname'}'),'%')) ":"";
		$add_sql_cm .= ($in{'lastname1'})? " AND sl_customers.Lastname1 LIKE (CONCAT('%',TRIM('$in{'lastname1'}'),'%')) ":"";
		$add_sql_cm .= ($in{'lastname2'})? " AND sl_customers.Lastname2 LIKE (CONCAT('%',TRIM('$in{'lastname2'}'),'%')) ":"";

		$add_sql .= ($in{'firstname'})? " AND sl_customers.FirstName LIKE (CONCAT('%',TRIM('$in{'firstname'}'),'%')) ":"";
		$add_sql .= ($in{'lastname1'})? " AND sl_customers.Lastname1 LIKE (CONCAT('%',TRIM('$in{'lastname1'}'),'%')) ":"";
		$add_sql .= ($in{'lastname2'})? " AND sl_customers.Lastname2 LIKE (CONCAT('%',TRIM('$in{'lastname2'}'),'%')) ":"";
		
		$add_sql .= ($in{'customer_fcode'})? " AND cu_invoices.customer_fcode LIKE (CONCAT('%',TRIM('$in{'customer_fcode'}'),'%')) ":"";
		$add_sql_cm .= ($in{'customer_fcode'})? " AND cu_invoices.customer_fcode LIKE (CONCAT('%',TRIM('$in{'customer_fcode'}'),'%')) ":"";

		## Filtro por Inovices invoice_type
		# my ($string_tmp);
		# if ($in{'invoice_type'}){
		# 	if ($in{'invoice_type'} =~ m/\|/){
		# 		my @arr_tmp = split /\|/ , $in{'invoice_type'};
		# 		for (0..$#arr_tmp) {
		# 			$string_tmp .= "'".$arr_tmp[$_]."',";
		# 		}
		# 		chop $string_tmp;
		# 		$add_sql .= " AND cu_invoices.invoice_type IN($string_tmp) ";
		# 		$add_sql_cm .= " AND cu_invoices.invoice_type IN($string_tmp) ";
		# 	}else{
		# 		$add_sql .= " AND cu_invoices.invoice_type IN('$in{'invoice_type'}') ";
		# 		$add_sql_cm .= " AND cu_invoices.invoice_type IN('$in{'invoice_type'}') ";
		# 	}
		# }
		$add_sql .= " AND cu_invoices.invoice_type IN('ingreso','egreso') ";
		$add_sql_cm .= " AND cu_invoices.invoice_type IN('ingreso','egreso') ";

		## Filtro por Orders Ptype
		my ($string_tmp);
		if ($in{'ptype'}){
			if ($in{'ptype'} =~ m/\|/){
				my @arr_tmp = split /\|/ , $in{'ptype'};
				for (0..$#arr_tmp) {
					$string_tmp .= "'".$arr_tmp[$_]."',";
				}
				chop $string_tmp;
				$add_sql .= " AND sl_orders.ptype IN($string_tmp) ";
				$add_sql_cm .= "";
			}else{
				$add_sql .= " AND sl_orders.ptype IN('$in{'ptype'}') ";
				$add_sql_cm .= "";
			}
		}

		## Filtro por Orders Date
		if ($in{'from_date'} ne '' and  $in{'to_date'} ne '' and $in{'from_date'} eq $in{'to_date'}){
			$add_sql .= " AND sl_orders.Date = '$in{'from_date'}' ";
		}else{
			if ($in{'from_date'}){
				$add_sql .= " AND sl_orders.Date >= '$in{'from_date'}' ";
			}

			if ($in{'to_date'}){
				$add_sql .= " AND sl_orders.Date <= '$in{'to_date'}' ";
			}
		}

		## Filtro por Invoices doc_date
		if ($in{'from_doc_date'} ne '' and  $in{'to_doc_date'} ne '' and $in{'from_doc_date'} eq $in{'to_doc_date'}){
			$add_sql .= " AND Date(cu_invoices.doc_date) = '$in{'from_doc_date'}' ";
			$add_sql_cm .= " AND Date(cu_invoices.doc_date) = '$in{'from_doc_date'}' ";
		}else{
			if ($in{'from_doc_date'}){
				$add_sql .= " AND Date(cu_invoices.doc_date) >= '$in{'from_doc_date'}' ";
				$add_sql_cm .= " AND Date(cu_invoices.doc_date) >= '$in{'from_doc_date'}' ";
			}

			if ($in{'to_doc_date'}){
				$add_sql .= " AND Date(cu_invoices.doc_date) <= '$in{'to_doc_date'}' ";
				$add_sql_cm .= " AND Date(cu_invoices.doc_date) <= '$in{'to_doc_date'}' ";
			}
		}

		## Filtro por Credit Memos Date
		if ($in{'from_doc_date_cm'} ne '' and  $in{'to_doc_date_cm'} ne '' and $in{'from_doc_date_cm'} eq $in{'to_doc_date_cm'}){
			$add_sql_cm .= " AND sl_creditmemos_payments.Date = '$in{'from_doc_date_cm'}' ";
		}else{
			if ($in{'from_doc_date_cm'}){
				$add_sql_cm .= " AND sl_creditmemos_payments.Date >= '$in{'from_doc_date_cm'}' ";
			}

			if ($in{'to_doc_date_cm'}){
				$add_sql_cm .= " AND sl_creditmemos_payments.Date <= '$in{'to_doc_date_cm'}' ";
			}
		}
		
		$sql = "SELECT 
				expediter_fname
				, Femision
				, ID_orders
				, ID_creditmemos
				, orders_date
				, `orders_status`
				, (CONCAT(doc_serial,doc_num))folio
				, doc_date
				, ID_customers
				, customer_fcode
				, ((CONCAT(FirstName,' ',Lastname1,' ',Lastname2)))Cliente
				, Type
				, ((IF(invoice_type='egreso' AND invoice_net>0,invoice_net*-1,invoice_net)))net
				, ((IF(invoice_type='egreso' AND total_taxes_transfered>0,total_taxes_transfered*-1,total_taxes_transfered)))tax
				, ((IF(invoice_type='egreso' AND discount>0,discount*-1,discount)))discount
				, ((IF(invoice_type='egreso' AND invoice_total>0,invoice_total*-1,invoice_total)))total
				
				-- , ((CASE WHEN Status='Certified' THEN 'Emitida' WHEN Status='Cancelled' THEN 'Cancelada' ELSE '' END))emitida
				, 'Emitida' emitida
				
				, invoice_type
				, IF(Currency='MXP' OR Currency='MX\$','MXP','USD')Currency
				, IF(Currency='MXP' OR Currency='MX\$','1',currency_exchange)exchange_rate
				, notes
				, Ptype
				, sales_origins
				, IF(invoice_type='egreso',COSTO*-1,COSTO)COSTO
				, xml_uuid 
				, REFACTURACION
			FROM ( 

				SELECT 
					cu_invoices.expediter_fname 
					, cu_invoices.Date 'Femision'
					, doc_serial 
					, doc_num 
					, sl_orders.Date orders_date 
					, sl_orders.Status orders_status
					, Date(cu_invoices.doc_date)doc_date
					, sl_orders.ID_customers 
					, cu_invoices.customer_fcode
					, sl_customers.FirstName
					, sl_customers.Lastname1 
					, sl_customers.Lastname2 
					, sl_customers.Type 
					, cu_invoices.invoice_net 
					, cu_invoices.total_taxes_transfered 
					, cu_invoices.invoice_total 
					, cu_invoices.discount 
					, cu_invoices.Status 
					, sl_orders.ID_orders 
					, '' AS ID_creditmemos
					, cu_invoices.invoice_type 
					, cu_invoices.Currency 
					, cu_invoices.currency_exchange
					, cu_invoices.ID_invoices 
					, cu_invoices.xml_uuid 
					, ((SELECT GROUP_CONCAT(NOTES SEPARATOR ' ') FROM cu_invoices_notes WHERE 1 AND Type='ToPrint' AND cu_invoices_notes.ID_invoices=cu_invoices.ID_invoices))notes 
					, sl_orders.Ptype
					, sl_salesorigins.channel sales_origins
					, IF((cu_invoices_lines.ID_admin_users=0 OR cu_invoices_lines.ID_admin_users=100),0,SUM(sl_orders_products.Cost))COSTO
					, IF((cu_invoices_lines.ID_admin_users=0 OR cu_invoices_lines.ID_admin_users=100),'REFACTURACION','')REFACTURACION
				FROM sl_orders 
				INNER JOIN sl_orders_products USING(ID_orders) 
				INNER JOIN cu_invoices_lines ON cu_invoices_lines.ID_orders_products=sl_orders_products.ID_orders_products AND cu_invoices_lines.ID_creditmemos IS NULL 
				INNER JOIN cu_invoices USING(ID_invoices) 
				INNER JOIN sl_customers ON sl_customers.ID_customers=sl_orders.ID_customers
				LEFT JOIN sl_salesorigins ON sl_salesorigins.ID_salesorigins=sl_orders.ID_salesorigins
				WHERE 1 $add_sql
				AND cu_invoices.Status = 'Certified'
				AND sl_orders.Status NOT IN('System Error','Converted') 
				AND sl_orders_products.ShpDate > '2010-12-31'
				GROUP BY ID_invoices 

			UNION 

				SELECT 
					cu_invoices.expediter_fname 
					, cu_invoices.Date 'Femision'
					, doc_serial 
					, doc_num 
					, sl_creditmemos.Date orders_date 
					
					-- , sl_creditmemos_payments.Status orders_status
					, ''orders_status

					, Date(cu_invoices.doc_date)doc_date
					, sl_creditmemos.ID_customers 
					, cu_invoices.customer_fcode
					, sl_customers.FirstName
					, sl_customers.Lastname1 
					, sl_customers.Lastname2 
					, sl_customers.Type 
					, cu_invoices.invoice_net 
					, cu_invoices.total_taxes_transfered 
					, cu_invoices.invoice_total 
					, cu_invoices.discount 
					, cu_invoices.Status 
					
					-- , sl_creditmemos_payments.ID_orders
					, '' ID_orders
					
					, sl_creditmemos.ID_creditmemos 
					, cu_invoices.invoice_type 
					, cu_invoices.Currency 
					, cu_invoices.currency_exchange
					, cu_invoices.ID_invoices 
					, cu_invoices.xml_uuid 
					, ((SELECT GROUP_CONCAT(NOTES SEPARATOR ' ') FROM cu_invoices_notes WHERE 1 AND Type='ToPrint' AND cu_invoices_notes.ID_invoices=cu_invoices.ID_invoices))notes 
					
					-- , sl_creditmemos_payments.Ptype
					, '' Ptype

					-- , sl_creditmemos_payments.Channel sales_origins
					, '' sales_origins

					, SUM(sl_creditmemos_products.Cost * sl_creditmemos_products.Quantity) COSTO
					, '' REFACTURACION
				FROM sl_creditmemos 
				INNER JOIN sl_creditmemos_products USING(ID_creditmemos) 
				INNER JOIN cu_invoices_lines ON cu_invoices_lines.ID_orders_products=sl_creditmemos_products.ID_creditmemos_products AND cu_invoices_lines.ID_orders=0 
				INNER JOIN cu_invoices USING(ID_invoices) 
				INNER JOIN sl_customers ON sl_customers.ID_customers=sl_creditmemos.ID_customers 
				WHERE 1 $add_sql_cm
				AND cu_invoices.Status = 'Certified'
				AND sl_creditmemos_products.ShpDate > '2010-12-31'
				GROUP BY ID_invoices 
			)invoices 
			ORDER BY doc_serial,doc_num ASC;";
		my ($sth) = &Do_SQL($sql);
		
		my $out='';
		my $recs=0;
		while (my $rec = $sth->fetchrow_hashref()){
			$recs++;

			## Datos del pedido cuando es de CreditMemo
			if ($rec->{'ID_creditmemos'} > 0){
				
				$sql = "SELECT 
					sl_orders.Ptype
					, sl_orders.Status
					, sl_creditmemos_payments.ID_orders
					, sl_salesorigins.Channel
				FROM sl_creditmemos_payments
				INNER JOIN sl_orders ON sl_creditmemos_payments.ID_orders=sl_orders.ID_orders
				INNER JOIN sl_salesorigins ON sl_salesorigins.ID_salesorigins=sl_orders.ID_salesorigins
				WHERE sl_creditmemos_payments.ID_creditmemos='$rec->{'ID_creditmemos'}'
				GROUP BY sl_creditmemos_payments.ID_creditmemos";
				my ($sth_info) = &Do_SQL($sql);
				my $rec_info = $sth_info->fetchrow_hashref();

				## Sobreescribo valores
				$rec->{'orders_status'} = $rec_info->{'Status'};
				$rec->{'ID_orders'} = $rec_info->{'ID_orders'};
				$rec->{'Ptype'} = $rec_info->{'Ptype'};
				$rec->{'sales_origins'} = $rec_info->{'Channel'};


			}

			$rec->{'COSTO'} = '0' if(!$rec->{'COSTO'});			
			$rec->{'COSTO'} = ($rec->{'COSTO'} > 0) ? &format_price($rec->{'COSTO'}) : '-'.&format_price(($rec->{'COSTO'}*-1));
			$rec->{'net'} = ($rec->{'net'} > 0) ? &format_price($rec->{'net'}) : '-'.&format_price(($rec->{'net'}*-1));
			$rec->{'tax'} = ($rec->{'tax'} > 0) ? &format_price($rec->{'tax'}) : '-'.&format_price(($rec->{'tax'}*-1));
			$rec->{'discount'} = ($rec->{'discount'} > 0) ? &format_price($rec->{'discount'}) : '-'.&format_price(($rec->{'discount'}*-1));
			$rec->{'total'} = ($rec->{'total'} > 0) ? format_price($rec->{'total'}) : '-'.&format_price(($rec->{'total'}*-1));

			$out .= qq|"$rec->{'expediter_fname'}","$rec->{'ID_orders'}","$rec->{'ID_creditmemos'}","$rec->{'orders_date'}","$rec->{'orders_status'}","$rec->{'folio'}","$rec->{'Femision'}","$rec->{'doc_date'}","$rec->{'ID_customers'}","$rec->{'customer_fcode'}","$rec->{'Cliente'}","$rec->{'Type'}","$rec->{'net'}","$rec->{'tax'}","$rec->{'discount'}","$rec->{'total'}","$rec->{'emitida'}","$rec->{'invoice_type'}","$rec->{'Currency'}","$rec->{'exchange_rate'}","$rec->{'notes'}","$rec->{'Ptype'}","$rec->{'sales_origins'}","$rec->{'COSTO'}","$rec->{'xml_uuid'}","$rec->{'REFACTURACION'}"|."\r\n";
			
		}
		
		&auth_logging('report_view','');
		
		if ($recs){				
			my $strHeader = qq|"UNIDAD DE NEGOCIO","ID PEDIDO","ID CREDITMEMO","FECHA DE PEDIDO","STATUS DE PEDIDO","FACTURA","FECHA DE EMISION","FECHA DE FACTURA","ID CLIENTE","RFC RECEPTOR","NOMBRE CLIENTE","TIPO CLIENTE","SUB-TOTAL","IVA","DESCUENTO","TOTAL","ESTADO","TIPO FACTURA","MONEDA","TIPO DE CAMBIO","OBSERVACIONES","FORMA DE PAGO","ORIGEN VENTA","COSTO DE VENTA","UUID","REFACTURACION"|."\r\n";

			print "Content-type: application/octetstream\n";
			print "Content-disposition: attachment; filename=$fname\n\n";
			print $strHeader;
			print $out;
			
			return;
		}else{
			$va{'message'} = &trans_txt('search_nomatches');
		}
	}
	
	print "Content-type: text/html\n\n";
	print &build_page('rep_bi_sales_journal_v1.html');
}

#############################################################################
#############################################################################
#   Function: rep_bi_sales_journal_v2
#
#       Es: Reporte de Diario de Ventas version Importaciones y Mufar
#       En: 
#
#
#    Created on: 11/05/2015
#
#    Author: ISC Alejandro Diaz
#
#    Modifications:
#
#        - Modified on ** by *** : 
#
#   Parameters:
#
#      - 
#
#  Returns:
#
#
#   See Also:
#
#      <>
#
sub rep_bi_sales_journal_v2 {
#############################################################################
#############################################################################

	if ($in{'action'}){
		
		my $output = '';
		
		my $fname   = 'sales_journal_v2 '.$cfg{'app_title'}.'.csv';
		$fname =~ s/\s/_/g;

		my ($add_sql, $add_sql_cm);

		$add_sql .= ($in{'doc_serial'})? " AND cu_invoices.doc_serial = TRIM('$in{'doc_serial'}') ":"";
		$add_sql .= ($in{'doc_num'})? " AND cu_invoices.doc_num = TRIM('$in{'doc_num'}') ":"";
		$add_sql .= ($in{'id_invoices'})? " AND cu_invoices.ID_invoices = TRIM('$in{'id_invoices'}') ":"";
		$add_sql .= ($in{'id_orders'})? " AND sl_orders.ID_orders = '$in{'id_orders'}' ":"";
		
		$add_sql_cm .= ($in{'doc_serial'})? " AND cu_invoices.doc_serial = TRIM('$in{'doc_serial'}') ":"";
		$add_sql_cm .= ($in{'doc_num'})? " AND cu_invoices.doc_num = TRIM('$in{'doc_num'}') ":"";
		$add_sql_cm .= ($in{'id_invoices'})? " AND cu_invoices.ID_invoices = TRIM('$in{'id_invoices'}') ":"";
		$add_sql_cm .= ($in{'id_creditmemos'})? " AND sl_creditmemos.ID_creditmemos = '$in{'id_creditmemos'}' ":"";

		$add_sql .= ($in{'id_customers'})? " AND cu_invoices.ID_customers = '$in{'id_customers'}' ":"";
		$add_sql_cm .= ($in{'id_customers'})? " AND cu_invoices.ID_customers = '$in{'id_customers'}' ":"";
		
		$add_sql_cm .= ($in{'firstname'})? " AND sl_customers.FirstName LIKE (CONCAT('%',TRIM('$in{'firstname'}'),'%')) ":"";
		$add_sql_cm .= ($in{'lastname1'})? " AND sl_customers.Lastname1 LIKE (CONCAT('%',TRIM('$in{'lastname1'}'),'%')) ":"";
		$add_sql_cm .= ($in{'lastname2'})? " AND sl_customers.Lastname2 LIKE (CONCAT('%',TRIM('$in{'lastname2'}'),'%')) ":"";

		$add_sql .= ($in{'firstname'})? " AND sl_customers.FirstName LIKE (CONCAT('%',TRIM('$in{'firstname'}'),'%')) ":"";
		$add_sql .= ($in{'lastname1'})? " AND sl_customers.Lastname1 LIKE (CONCAT('%',TRIM('$in{'lastname1'}'),'%')) ":"";
		$add_sql .= ($in{'lastname2'})? " AND sl_customers.Lastname2 LIKE (CONCAT('%',TRIM('$in{'lastname2'}'),'%')) ":"";
		
		$add_sql .= ($in{'customer_fcode'})? " AND cu_invoices.customer_fcode LIKE (CONCAT('%',TRIM('$in{'customer_fcode'}'),'%')) ":"";
		$add_sql_cm .= ($in{'customer_fcode'})? " AND cu_invoices.customer_fcode LIKE (CONCAT('%',TRIM('$in{'customer_fcode'}'),'%')) ":"";

		## Filtro por Inovices invoice_type
		# my ($string_tmp);
		# if ($in{'invoice_type'}){
		# 	if ($in{'invoice_type'} =~ m/\|/){
		# 		my @arr_tmp = split /\|/ , $in{'invoice_type'};
		# 		for (0..$#arr_tmp) {
		# 			$string_tmp .= "'".$arr_tmp[$_]."',";
		# 		}
		# 		chop $string_tmp;
		# 		$add_sql .= " AND cu_invoices.invoice_type IN($string_tmp) ";
		# 		$add_sql_cm .= " AND cu_invoices.invoice_type IN($string_tmp) ";
		# 	}else{
		# 		$add_sql .= " AND cu_invoices.invoice_type IN('$in{'invoice_type'}') ";
		# 		$add_sql_cm .= " AND cu_invoices.invoice_type IN('$in{'invoice_type'}') ";
		# 	}
		# }
		$add_sql .= " AND cu_invoices.invoice_type IN('ingreso','egreso') ";
		$add_sql_cm .= " AND cu_invoices.invoice_type IN('ingreso','egreso') ";

		## Filtro por Orders Ptype
		my ($string_tmp);
		if ($in{'ptype'}){
			if ($in{'ptype'} =~ m/\|/){
				my @arr_tmp = split /\|/ , $in{'ptype'};
				for (0..$#arr_tmp) {
					$string_tmp .= "'".$arr_tmp[$_]."',";
				}
				chop $string_tmp;
				$add_sql .= " AND sl_orders.ptype IN($string_tmp) ";
				$add_sql_cm .= " AND sl_creditmemos_payments.ptype IN($string_tmp) ";
			}else{
				$add_sql .= " AND sl_orders.ptype IN('$in{'ptype'}') ";
				$add_sql_cm .= " AND sl_creditmemos_payments.ptype IN('$in{'ptype'}') ";
			}
		}

		## Filtro por Orders Date
		if ($in{'from_date'} ne '' and  $in{'to_date'} ne '' and $in{'from_date'} eq $in{'to_date'}){
			$add_sql .= " AND sl_orders.Date = '$in{'from_date'}' ";
		}else{
			if ($in{'from_date'}){
				$add_sql .= " AND sl_orders.Date >= '$in{'from_date'}' ";
			}

			if ($in{'to_date'}){
				$add_sql .= " AND sl_orders.Date <= '$in{'to_date'}' ";
			}
		}

		## Filtro por Invoices doc_date
		if ($in{'from_doc_date'} ne '' and  $in{'to_doc_date'} ne '' and $in{'from_doc_date'} eq $in{'to_doc_date'}){
			$add_sql .= " AND Date(cu_invoices.doc_date) = '$in{'from_doc_date'}' ";
			$add_sql_cm .= " AND Date(cu_invoices.doc_date) = '$in{'from_doc_date'}' ";
		}else{
			if ($in{'from_doc_date'}){
				$add_sql .= " AND Date(cu_invoices.doc_date) >= '$in{'from_doc_date'}' ";
				$add_sql_cm .= " AND Date(cu_invoices.doc_date) >= '$in{'from_doc_date'}' ";
			}

			if ($in{'to_doc_date'}){
				$add_sql .= " AND Date(cu_invoices.doc_date) <= '$in{'to_doc_date'}' ";
				$add_sql_cm .= " AND Date(cu_invoices.doc_date) <= '$in{'to_doc_date'}' ";
			}
		}

		## Filtro por Credit Memos Date
		if ($in{'from_doc_date_cm'} ne '' and  $in{'to_doc_date_cm'} ne '' and $in{'from_doc_date_cm'} eq $in{'to_doc_date_cm'}){
			$add_sql_cm .= " AND sl_creditmemos_payments.Date = '$in{'from_doc_date_cm'}' ";
		}else{
			if ($in{'from_doc_date_cm'}){
				$add_sql_cm .= " AND sl_creditmemos_payments.Date >= '$in{'from_doc_date_cm'}' ";
			}

			if ($in{'to_doc_date_cm'}){
				$add_sql_cm .= " AND sl_creditmemos_payments.Date <= '$in{'to_doc_date_cm'}' ";
			}
		}

		my $ida_inventory_sales = ($cfg{'ida_inventory_sales'}) ? $cfg{'ida_inventory_sales'} : '0';
		
		$sql = "SELECT 
					`expediter_fname`
					, (CONCAT(doc_serial,doc_num)) folio
					, `orders_date`
					, `orders_status`
					, `doc_date`
					, `ID_customers`
					, customer_fcode
					, ((IF(company_name IS NOT NULL,company_name,CONCAT(FirstName,' ',Lastname1))))Cliente
					, `Type`
					, ((IF(invoice_type='egreso' AND invoice_net>0,invoice_net*-1,invoice_net)))net
					, ((IF(invoice_type='egreso' AND total_taxes_transfered>0,total_taxes_transfered*-1,total_taxes_transfered)))tax
					, ((IF(invoice_type='egreso' AND invoice_total>0,invoice_total*-1,invoice_total)))total
					, ((IF(invoice_type='egreso' AND discount>0,discount*-1,discount)))discount
					, ((CASE WHEN Status='Certified' THEN 'Emitida' WHEN Status='Cancelled' THEN 'Cancelada' ELSE '' END))emitida
					, `ID_orders`
					, `invoice_type`
					, `Currency`
					, ((IF(Currency != 'MXP',currency_exchange,'')))currency_exchange
					, ((IF(Currency != 'MXP',(currency_exchange * invoice_net),invoice_net)) * (IF(invoice_type='egreso', -1, 1 ))) AS 'monto_en_pesos'
					, `notes`
					, Ptype
					, sales_origins
					, `COSTO`
					, `xml_uuid`
					, date_invoice 
				FROM ( 
					SELECT 
						cu_invoices.expediter_fname 
						, doc_serial 
						, doc_num 
						, sl_orders.Date orders_date 
						, Date(cu_invoices.doc_date)doc_date
						, sl_orders.ID_customers 
						, cu_invoices.customer_fcode
						, sl_customers.company_name
						, sl_customers.FirstName
						, sl_customers.Lastname1 
						, sl_customers.Type 
						, cu_invoices.invoice_net 
						, cu_invoices.total_taxes_transfered 
						, cu_invoices.invoice_total 
						, cu_invoices.discount 
						, cu_invoices.Status 
						, sl_orders.ID_orders 
						, cu_invoices.invoice_type 
						, cu_invoices.Currency 
						, cu_invoices.ID_invoices 
						, cu_invoices.xml_uuid 
						, ((SELECT GROUP_CONCAT(NOTES SEPARATOR ' ') FROM cu_invoices_notes WHERE 1 AND Type='ToPrint' AND cu_invoices_notes.ID_invoices=cu_invoices.ID_invoices))notes
						, SUM(sl_orders_products.Cost) COSTO
						/*
						, (select sum(amount) from sl_movements where id_accounts=$ida_inventory_sales and Credebit = 'Credit' and Status='Active' and ID_tableused=sl_orders.ID_orders) COSTO
						*/
						/*
						, (select sum(amount) from sl_movements where id_accounts=264 and Credebit = 'Credit' and Status='Active' and ID_tableused=sl_orders.ID_orders) IVA
						, (select sum(amount) from sl_movements where id_accounts in (363) and Credebit = 'Debit' and Status='Active' and ID_tableused=sl_orders.ID_orders) DESCUENTO
						, (select sum(amount) from sl_movements where id_accounts in (354,360) and Credebit = 'Credit' and Status='Active' and ID_tableused=sl_orders.ID_orders) VENTAS 
						*/
						, cu_invoices.currency_exchange 
						, sl_orders.Ptype
						, sl_salesorigins.channel sales_origins	
						, sl_orders.Status orders_status	
						, cu_invoices.Date AS date_invoice			
					FROM sl_orders 
						INNER JOIN sl_orders_products USING(ID_orders) 
						INNER JOIN cu_invoices_lines ON cu_invoices_lines.ID_orders_products=sl_orders_products.ID_orders_products AND cu_invoices_lines.ID_creditmemos IS NULL 
						INNER JOIN cu_invoices USING(ID_invoices) 
						INNER JOIN sl_customers ON sl_customers.ID_customers=sl_orders.ID_customers 
						LEFT JOIN sl_salesorigins ON sl_salesorigins.ID_salesorigins=sl_orders.ID_salesorigins
					WHERE 1 
						$add_sql 
						AND cu_invoices.Status IN ('Certified') 
						AND sl_orders.Status NOT IN('System Error','Converted') 
					GROUP BY ID_invoices 
					
					UNION 
					
					SELECT cu_invoices.expediter_fname 
						, doc_serial 
						, doc_num 
						, sl_creditmemos.Date orders_date 
						, Date(cu_invoices.doc_date)doc_date 
						, sl_creditmemos.ID_customers 
						, cu_invoices.customer_fcode
						, sl_customers.company_name
						, sl_customers.FirstName
						, sl_customers.Lastname1 
						, sl_customers.Type 
						, cu_invoices.invoice_net 
						, cu_invoices.total_taxes_transfered 
						, cu_invoices.invoice_total 
						, cu_invoices.discount 
						, cu_invoices.Status 
						, sl_creditmemos.ID_creditmemos 
						, cu_invoices.invoice_type 
						, cu_invoices.Currency 
						, cu_invoices.ID_invoices 
						, cu_invoices.xml_uuid 
						, ((SELECT GROUP_CONCAT(NOTES SEPARATOR ' ') FROM cu_invoices_notes WHERE 1 AND Type='ToPrint' AND cu_invoices_notes.ID_invoices=cu_invoices.ID_invoices))notes
						, SUM(sl_creditmemos_products.Cost * sl_creditmemos_products.Quantity) COSTO
						/*, 0 COSTO*/
						/*
						, 0 IVA
						, 0 DESCUENTO
						, 0 VENTAS 
						*/
						, cu_invoices.currency_exchange 
						, sl_creditmemos_payments.Ptype
						, sl_creditmemos_payments.Channel sales_origins
						, sl_creditmemos_payments.Status orders_status
						, cu_invoices.Date AS date_invoice
					FROM sl_creditmemos 
						INNER JOIN sl_creditmemos_products USING(ID_creditmemos) 
						INNER JOIN cu_invoices_lines ON cu_invoices_lines.ID_orders_products=sl_creditmemos_products.ID_creditmemos_products AND cu_invoices_lines.ID_orders=0 
						INNER JOIN cu_invoices USING(ID_invoices) 
						INNER JOIN sl_customers ON sl_customers.ID_customers=sl_creditmemos.ID_customers
						LEFT JOIN(
							SELECT 
								sl_creditmemos_payments.ID_creditmemos
								, sl_salesorigins.Channel
								, sl_orders.Ptype
								, sl_orders.Status
							FROM sl_creditmemos_payments
								INNER JOIN sl_orders ON sl_creditmemos_payments.ID_orders=sl_orders.ID_orders
								INNER JOIN sl_salesorigins ON sl_salesorigins.ID_salesorigins=sl_orders.ID_salesorigins
							WHERE 1
							GROUP BY sl_creditmemos_payments.ID_creditmemos
							ORDER BY sl_creditmemos_payments.ID_creditmemos_applied
						)sl_creditmemos_payments ON sl_creditmemos_payments.ID_creditmemos=sl_creditmemos.ID_creditmemos
					WHERE 1 
						$add_sql_cm
						AND cu_invoices.Status IN ('Certified') 
					GROUP BY ID_invoices 
				)invoices 
				WHERE 1 
				ORDER BY doc_serial,doc_num ASC;";
		my ($sth) = &Do_SQL($sql);
		
		my $out='';
		my $recs=0;
		while (my $rec = $sth->fetchrow_hashref()){
			$recs++;

			$rec->{'COSTO'} = '0' if(!$rec->{'COSTO'});
			$rec->{'COSTO'} = ($rec->{'COSTO'} > 0) ? &format_price($rec->{'COSTO'}) : '-'.&format_price(($rec->{'COSTO'}*-1));
			$rec->{'net'} = ($rec->{'net'} > 0) ? &format_price($rec->{'net'}) : '-'.&format_price(($rec->{'net'}*-1));
			$rec->{'tax'} = ($rec->{'tax'} > 0) ? &format_price($rec->{'tax'}) : '-'.&format_price(($rec->{'tax'}*-1));
			$rec->{'discount'} = ($rec->{'discount'} > 0) ? &format_price($rec->{'discount'}) : '-'.&format_price(($rec->{'discount'}*-1));
			$rec->{'total'} = ($rec->{'total'} > 0) ? format_price($rec->{'total'}) : '-'.&format_price(($rec->{'total'}*-1));

			my $id_orders = ($rec->{'invoice_type'} eq 'ingreso') ? $rec->{'ID_orders'} : '';
			my $id_creditmemos = ($rec->{'invoice_type'} eq 'egreso') ? $rec->{'ID_orders'} : '';

			$out .= qq|"$rec->{'expediter_fname'}","$id_orders","$id_creditmemos","$rec->{'orders_date'}","$rec->{'orders_status'}","$rec->{'folio'}","$rec->{'date_invoice'}","$rec->{'doc_date'}","$rec->{'ID_customers'}","$rec->{'customer_fcode'}","$rec->{'Cliente'}","$rec->{'Type'}","$rec->{'net'}","$rec->{'tax'}","$rec->{'discount'}","$rec->{'total'}","$rec->{'emitida'}","$rec->{'invoice_type'}","$rec->{'Currency'}","$rec->{'currency_exchange'}","$rec->{'monto_en_pesos'}","$rec->{'notes'}","$rec->{'Ptype'}","$rec->{'sales_origins'}","$rec->{'COSTO'}","$rec->{'xml_uuid'}"|."\r\n";

		}
		&auth_logging('report_view','');
		
		if ($recs){				

			my $strHeader = qq|"UNIDAD DE NEGOCIO","ID PEDIDO","ID CREDITMEMO","FECHA DE PEDIDO","ESTATUS DE PEDIDO","FACTURA","FECHA DE EMISION","FECHA DE FACTURA","ID CLIENTE","RFC RECEPTOR","NOMBRE CLIENTE","TIPO CLIENTE","SUB-TOTAL","IVA","DESCUENTO","TOTAL","ESTADO","TIPO FACTURA","MONEDA","TIPO DE CAMBIO","SUB-TOTAL EN PESOS","OBSERVACIONES","FORMA DE PAGO","ORIGEN VENTA","COSTO DE VENTA","UUID"|."\r\n";

			print "Content-type: application/octetstream\n";
			print "Content-disposition: attachment; filename=$fname\n\n";
			print $strHeader;
			print $out;
			
			return;
		}else{
			$va{'message'} = &trans_txt('search_nomatches');
		}
	}
	
	print "Content-type: text/html\n\n";
	print &build_page('rep_bi_sales_journal_v2.html');
}

#############################################################################
#############################################################################
#   Function: rep_bi_shipping_costs
#
#       Es: Reporte de Gastos de Envio
#       En: 
#
#
#    Created on: 22/07/2016
#
#    Author: ISC Alejandro Diaz
#
#    Modifications:
#
#        - Modified on ** by *** : 
#
#   Parameters:
#
#      - 
#
#  Returns:
#
#
#   See Also:
#
#      <>
#
sub rep_bi_shipping_costs {
#############################################################################
#############################################################################

	my $add_sql;
	
	## Headers Print
	my $str_to_print = qq|"MENSAJERIA","EN REMESA","REMESA","FALTA","FSALIDA ENV","ORIGVTA","TPAGO","FACTURA (INVOICING)","FECHA EN QUE SE EMITIO LA FACTURA (INVOICING)","ESTATUS","ORDVTA","GENVIO","TOTAL","FECHA DE REMESA","HORA DE REMESA","FAMILIA"\n|;

	if ($in{'action'}){

		if ($in{'history'}){
			(!$in{'from_date'}) and ($in{'from_date'} = &get_sql_date());
			(!$in{'to_date'}) and ($in{'to_date'} = &get_sql_date());		
		}

		$add_sql = ($in{'from_date'} ne '')? " AND sl_warehouses_batches.Date >= '".$in{'from_date'}."'":"";
		$add_sql .= ($in{'to_date'} ne '')? " AND sl_warehouses_batches.Date <= '".$in{'to_date'}."'":"";
		$add_sql .= ($in{'id_warehouses'} ne '')? " AND sl_warehouses_batches.ID_warehouses=".$in{'id_warehouses'}:"";


		my ($sth) = &Do_SQL("SELECT COUNT(*)
		FROM sl_warehouses_batches_orders
		INNER JOIN sl_warehouses_batches ON sl_warehouses_batches.ID_warehouses_batches=sl_warehouses_batches_orders.ID_warehouses_batches
		INNER JOIN sl_orders_products ON sl_orders_products.ID_orders_products=sl_warehouses_batches_orders.ID_orders_products
		WHERE 1 $add_sql
		GROUP BY sl_orders_products.ID_orders");
		$va{'matches'} = $sth->fetchrow;

		if (int($va{'matches'}) > 0) {

			my $query  =  "SELECT 
				sl_orders_products.ID_orders
				,sl_orders_products.ID_products
				,(sl_orders_products.SalePrice + sl_orders_products.Shipping + sl_orders_products.Tax) as cost
				, sl_warehouses_batches_orders.ID_warehouses_batches
				, sl_warehouses_batches.ID_warehouses
				, sl_warehouses_batches.Date
				, sl_warehouses_batches.Time
				, sl_warehouses_batches.Status
				, sl_warehouses_batches_orders.ScanDate
				, sl_warehouses.Name AS Warehouse
			FROM sl_warehouses_batches_orders
			INNER JOIN sl_warehouses_batches ON sl_warehouses_batches.ID_warehouses_batches=sl_warehouses_batches_orders.ID_warehouses_batches
			INNER JOIN sl_warehouses ON sl_warehouses.ID_warehouses=sl_warehouses_batches.ID_warehouses
			INNER JOIN sl_orders_products ON sl_orders_products.ID_orders_products=sl_warehouses_batches_orders.ID_orders_products
			WHERE 1 $add_sql
			GROUP BY sl_orders_products.ID_orders,sl_warehouses_batches_orders.ID_warehouses_batches 
			ORDER BY sl_warehouses_batches.ID_warehouses_batches,sl_orders_products.ID_orders;";

			my ($sth2) = &Do_SQL($query);
			ORDERS: while ($rec = $sth2->fetchrow_hashref()){

				my $intransit=0; my $cancelled=0; my $returned=0;

				$query = "SELECT 
				sl_salesorigins.Channel
				, sl_orders.Ptype
				, sl_orders.Date
				, sl_orders.ID_orders
				, sl_orders.Status
				FROM sl_orders
				INNER JOIN sl_customers ON sl_orders.ID_customers=sl_customers.ID_customers
				INNER JOIN sl_salesorigins ON sl_salesorigins.ID_salesorigins=sl_orders.ID_salesorigins
				WHERE sl_orders.ID_orders = $rec->{'ID_orders'}";

				my ($sth_order) = &Do_SQL($query);
				my ($rec_order) = $sth_order->fetchrow_hashref();

				## Datos de Factura
				my ($id_invoices, $doc_date, $invoice);
				if ($rec->{'ID_orders'}>0 and $rec->{'ScanDate'} ne ''){
					$query = "SELECT 
					cu_invoices.ID_invoices
					, Date(cu_invoices.doc_date) AS doc_date
					, CONCAT(cu_invoices.doc_serial,cu_invoices.doc_num) AS invoice
					FROM cu_invoices_lines
					INNER JOIN cu_invoices ON cu_invoices.ID_invoices=cu_invoices_lines.ID_invoices
					WHERE cu_invoices_lines.ID_orders = $rec->{'ID_orders'}
					AND Date(cu_invoices.doc_date) >= '$rec->{'ScanDate'}'
					GROUP BY cu_invoices_lines.ID_invoices
					ORDER BY cu_invoices_lines.ID_invoices
					LIMIT 1";
					my ($sth_invoice) = &Do_SQL($query);
					($id_invoices, $doc_date, $invoice) = $sth_invoice->fetchrow_array();
				}


				my $sumprod = 0; my $sumser = 0; my $sumtax = 0; my $sumdisc = 0; my $sumshipp = 0;
				my $catname;

				$sth3 = &Do_SQL("SELECT IsSet,sl_orders_products.*,
				IF(sl_warehouses_batches_orders.Status IN('Cancelled','Error') AND ID_warehouses_batches = $rec->{'ID_warehouses_batches'},1,0)AS Cancelled,
				IF(sl_warehouses_batches_orders.Status = 'Returned' AND ID_warehouses_batches = $rec->{'ID_warehouses_batches'},1,0)AS Returned,
				IF(sl_warehouses_batches_orders.Status IN('In Fulfillment','Shipped','In Transit') AND ID_warehouses_batches = $rec->{'ID_warehouses_batches'},1,0)AS Transit 
				FROM sl_orders_products 
				LEFT JOIN sl_warehouses_batches_orders USING(ID_orders_products)
				LEFT JOIN sl_skus ON sl_orders_products.ID_products = sl_skus.ID_sku_products
				WHERE ID_orders = $rec->{'ID_orders'}
				AND sl_orders_products.Status IN('Active','ReShip','Exchange')
				AND IF( LEFT(sl_orders_products.ID_products,1) = 6,1, sl_warehouses_batches_orders.ID_orders_products = sl_orders_products.ID_orders_products AND ID_warehouses_batches = $rec->{'ID_warehouses_batches'})
				GROUP BY sl_orders_products.ID_orders_products;");

				$prodline = 0;
				while($rprod = $sth3->fetchrow_hashref()){
					++$prodline;
							
					###
					### Product Family
					###
					if($prodline == 1) {
						
						if(!$idcat){
							
							my ($sthc) = Do_SQL("SELECT ID_categories FROM sl_products_categories WHERE ID_products = RIGHT($rprod->{'ID_products'},6) LIMIT 1;");
							$idcat = $sthc->fetchrow();

						}

						$catname = $idcat ? &load_name('sl_categories','ID_categories', $idcat, 'Title') : 'N/A';

					}

					$sumprod += $rprod->{'SalePrice'} if substr($rprod->{'ID_products'},0,1)!= 6;
					$sumser += $rprod->{'SalePrice'} if substr($rprod->{'ID_products'},0,1)== 6;
					$sumtax += $rprod->{'Tax'} if abs($rprod->{'SalePrice'}) > 0.05;
					$sumdisc += $rprod->{'Discount'};
					$sumshipp += $rprod->{'Shipping'};
					$sumshipp += $rprod->{'ShpTax'} if abs($rprod->{'Shipping'}) > 0.05;

					undef $idcat;

				}
				
				$sumshipp = round($sumshipp,2);
				my $sumtot = round($sumprod + $sumser + $sumtax + $sumshipp - $sumdisc,2);

				my $res_batch = 'OK';

				($intransit > 0 and ($cancelled > 0 or $returned > 0)) and ($res_batch = 'Partial');
				($cancelled > 0) and ($res_batch = 'Cancelled');
				($returned > 0) and ($res_batch = 'Returned');
				($rec->{'Status'} eq 'Void') and ($res_batch = 'Void');

				## Cadena que se va imprimir
				$str_to_print .= ($res_batch eq 'OK')? qq|"$rec->{'Warehouse'}","$res_batch","$rec->{'ID_warehouses_batches'}","$rec->{'Date'}","$rec->{'ScanDate'}","$rec_order->{'Channel'}","$rec_order->{'Ptype'}","$invoice","$doc_date","$rec->{'Status'}","$rec->{'ID_orders'}","$sumshipp","$sumtot","$rec->{'Date'}","$rec->{'Time'}","$catname"\n| : ""; 

			}

		}
		
		## Impresion de archivo CSV
		my $f = lc($cfg{"app_title"}."-Gastos-de-envio");
		$f =~ s/ /_/g;

		print "Content-Type: text/csv\n";
		print "Content-disposition: attachment; filename=".$f.".csv\n\n";
		print $str_to_print;

		return;
	}

	print "Content-type: text/html\n\n";
	print &build_page('rep_bi_shipping_costs.html');
}


#############################################################################
#############################################################################
#   Function: rep_bi_manual_calls
#
#       Es: Reporte de Llamadas Manuales
#       En: 
#
#
#    Created on: 26/01/2017
#
#    Author: Fabian Cañaveral
#
#    Modifications:
#
#        - Modified on ** by *** : 
#
#   Parameters:
#
#      - 
#
#  Returns:
#
#
#   See Also:
#
#      <>
#
sub rep_bi_manual_calls{
#############################################################################
#############################################################################
	use Data::Dumper;
	if ($in{'action'}){
		$csvHeader = qq|"number","name","start_date","end_date","duration","duration_wait","queue","type","telefono","transfer","status","idx","res"\r\n|;
		$query = qq|SELECT 
			sl_call_schedules.phone
			, sl_call_schedules.tipificacion
			, sl_call_schedules.tipificacion_des
			, sl_call_schedules.status
			, sl_call_schedules.date
			, sl_call_schedules.time
			, sl_call_schedules.ID_admin_users
			, admin_users.Username_ref
			, UPPER(CONCAT(admin_users.FirstName,' ', admin_users.LastName)) name
		FROM sl_call_schedules
		INNER JOIN admin_users on sl_call_schedules.ID_admin_users = admin_users.ID_admin_users
		WHERE 1
			AND sl_call_schedules.status = 'Called'
			-- AND admin_users.Username_ref > 0
			AND sl_call_schedules.date BETWEEN '$in{'from_date'}' AND '$in{'to_date'}';|;
		$calls = &Do_SQL($query);
		$csv = $csvHeader;
		$in{'from_date'} =~ s/-//g;
		$in{'to_date'} =~ s/-//g;
		$f = "calls_details_manual_$in{'from_date'}_$in{'to_date'}";
		print "Content-Type: text/csv\n";
		print "Content-disposition: attachment; filename=".$f.".csv\n\n";
		print $csv;
		### Conexion BD Asterisk Fidelizacion
		while($call = $calls->fetchrow_hashref()){
			$phone = &getPhoneNumber($call->{'phone'});
			&connect_db_w($cfg{'dbi_db_fide'},$cfg{'dbi_host_fide'},$cfg{'dbi_user_fide'},$cfg{'dbi_pw_fide'});
			$ext = $call->{'Username_ref'};
			$dateTime = qq|$call->{'date'} $call->{'time'}|;
			### diffTime on seconds
			$diffTime = 60;
			$query = qq|SELECT
				src
				, SEC_TO_TIME(duration) duration
				, uniqueid
				, disposition
				, calldate start_date
				, (calldate + INTERVAL duration SECOND) end_date
				, SEC_TO_TIME((duration - billsec)) espera
			FROM asteriskcdrdb.cdr
			WHERE 1
				AND src = '_ext|. qq|$ext| . qq|_$phone'
				AND ABS(UNIX_TIMESTAMP(calldate)-UNIX_TIMESTAMP('$dateTime')) <= $diffTime
			ORDER BY calldate desc 
			LIMIT 1;|;

			$call_asterisk = &Do_SQL($query, 1)->fetchrow_hashref();
			if($call_asterisk->{'uniqueid'}){
				$csvRow = qq|$call->{'Username_ref'}, $call->{'name'}, $call_asterisk->{'start_date'},$call_asterisk->{'end_date'}, $call_asterisk->{'duration'},$call_asterisk->{'espera'},,"manual",|.$call->{'phone'}. qq|,,$call_asterisk->{'disposition'},$call_asterisk->{'uniqueid'},$call->{'tipificacion'}\r\n|;
				print $csvRow;
			}

		}

	}else{
		print "Content-type: text/html\n\n";
		print &build_page('rep_bi_manual_calls.html');
	}
}


sub rep_bi_allorders_logistics {
#-----------------------------------------
# Created on: 2017/05/23  18:54:00 By  HCJ
# Forms Involved: 
# Description : Extrae la informacion de ordenes 
# Parameters :

	my $log_query;
	if($in{'action'}){
		
		my ($query_list);
		my $maxprod=1;
		my $info_user =	'';
		my $info_pprod = '';
		my $info_oprod = '';
		my $strout = '';
		
		## Si type eq 'order' 1 linea por orden
		$maxprod = 10	if $in{'type'} eq 'order';
		
		###### Busqueda por rango de fecha de order
		if ($in{'from_date'} and $in{'to_date'}){
			$where_date = " AND sl_orders.Date BETWEEN '$in{'from_date'}' AND '$in{'to_date'}' ";
		}else{
			$where_date = "";
		}

		###### Busqueda por rango de fecha de venta
		if ($in{'from_sales_date'} and $in{'to_sales_date'}){
			$where_posteddate = " WHERE PostedDate BETWEEN '$in{'from_sales_date'}' AND '$in{'to_sales_date'}'";
		}else{
			$where_posteddate = "";
		}
		
		### Si es busqueda por id_products
		if($in{'id_products'}){			
			$info_oprod = " AND 0 < (SELECT COUNT(DISTINCT ID_orders) FROM sl_orders_products WHERE ID_orders = sl_orders.ID_orders AND RIGHT(ID_products,6) = '".int($in{'id_products'})."' AND Status = 'Active') ";
		}

		my $fname   = 'Logistics_all_orders_'.$cfg{'app_title'}.'.csv';
		$fname =~ s/\s/_/g;
		
		my $strHeader = '';
		if ($in{'type'} eq 'order'){
			$strHeader = "Channel,TPago,Orden,Status,Fecha,Fecha de Venta,Fecha de Factura,Fecha de Envio,Fecha de Ingreso,Estado,Municipio,CP,Id Zona,Nombre Zona";
		}else{
			$strHeader = "Channel,TPago,Orden,Status,Fecha,Fecha de Venta,Fecha de Envio,Estado,Municipio";	
		}

		for(1..$maxprod){
			$strHeader .=",Cant$_,Cod$_,Prod$_,Prec$_";
		}

		## Si type eq 'order' 1 linea por orden	
		$strHeader .= "Total Envio,Total Orden"	if $in{'type'} eq 'order';
		
		$strHeader .= ",Familia de Producto,Usuario,Grupo,Gastos de Envio";

		## Busqueda por consolas
		my $add_sql;
		if ($in{'id_salesorigins'}){
			my @arr_salesorigins = split /\|/ , $in{'id_salesorigins'};
			$add_sql .= " AND sl_orders.ID_salesorigins IN(". join(',', @arr_salesorigins) .")";
		}
		
		$query_list = "SELECT 
						   IDAgent,
						   AgentName,
						   IF(user_type IS NOT NULL AND user_type != '',user_type,'N/A') AS user_type,
						   IF(Orders IS NOT NULL,Orders,0)AS Orders,
						   ID_user,
						   UsernameDireksys
						FROM
						(
						   SELECT 
						      ID_admin_users AS IDAgent,
						      (CONCAT(UPPER(admin_users.FirstName),' ',UPPER(admin_users.MiddleName),' ',UPPER(admin_users.LastName))) AS AgentName,
						      user_type, admin_users.ID_admin_users as ID_user, admin_users.Username as UsernameDireksys
						   FROM admin_users $info_user
						)AS tmp_agent
						LEFT JOIN
						(
						   SELECT
						      ID_admin_users AS IDA,
						      COUNT(ID_Orders) AS Orders
						   FROM sl_orders
						      WHERE 1
						      $where_date
						      $info_oprod 
						      $add_sql
						      AND Status != 'System Error' 
						      GROUP BY ID_admin_users
						)AS tmp_order
						ON tmp_order.IDA = tmp_agent.IDAgent
						HAVING Orders > 0
						ORDER BY AgentName ";
		$log_query = $query_list . "\n\n ================================== \n\n";
		
		my ($sth) = &Do_SQL($query_list);
		if($sth->rows() > 0){

			print "Content-type: application/octetstream\n";
			print "Content-disposition: attachment; filename=$fname\n\n";
			print "$strHeader\r\n";
			
			while(my($idagent,$agentname,$user_type,$orders,$iduser_direksys,$user_direksys) = $sth->fetchrow()){

				# /*, IFNULL(CountyName,'N/A') AS County*/
				$query = "	SELECT * 
							FROM (
								SELECT 
									  DISTINCT ID_orders
									, sl_orders.Date
									, (shp_State)AS State
									, shp_City AS County
									, sl_orders.Status
									, Channel
									, IF(shp_type = 2, 'Yes','No')AS Rush
									, sl_orders.shp_Zip
									, sl_orders.ID_zones
									, (SELECT Name FROM sl_zones WHERE sl_zones.ID_zones=sl_orders.ID_zones) as zone_name
									, if(	sl_orders.Ptype<>'COD',
											(SELECT CapDate FROM sl_orders_payments WHERE sl_orders_payments.ID_orders=sl_orders.ID_orders AND Captured='Yes' LIMIT 1),
											sl_orders.PostedDate
										)PostedDate
									, (SELECT GROUP_CONCAT(DISTINCT ShpDate) FROM sl_orders_products  WHERE sl_orders_products.ID_orders=sl_orders.ID_orders AND ShpDate > '1900-01-01' GROUP BY ID_orders) as ShpDate
									, if(sl_orders.Ptype='COD',(SELECT CapDate FROM sl_orders_payments WHERE sl_orders_payments.ID_orders=sl_orders.ID_orders AND Captured='Yes' LIMIT 1),'')CapDate
								FROM sl_orders LEFT JOIN sl_zipcodes ON sl_orders.shp_Zip = sl_zipcodes.ZipCode
									LEFT JOIN sl_zipdma ON sl_zipdma.ZipCode = sl_zipcodes.ZipCode 
									LEFT join sl_salesorigins on (sl_orders.ID_salesorigins=sl_salesorigins.ID_salesorigins)
								WHERE 
									sl_orders.ID_admin_users = $idagent 
									$info_oprod
									$add_sql 
									$query_converted 
									$where_date 
									$nopreorder  
									AND sl_orders.Status NOT IN('System Error','Converted'))orders
									$where_posteddate
								ORDER BY Date,Status,ID_orders";
				my $sth = &Do_SQL($query);
				#$log_query .= $query . "\n\n ================================== \n\n";
				                   
				while(my($id_orders,$date,$state,$county,$status,$salesorigins,$rush_shipping,$shp_zip,$id_zones,$zone_name,$posteddate,$shpdate,$capdate) = $sth->fetchrow()){
					my $items 	= 0;
					my $total 	= 0;
					my $tcost 	= 0;
					my $tdisc 	= 0;
					my $ttax 	= 0;
					my $tshp 	= 0;
					my $torder 	= 0;
					my $strprod = '';
					my $strout 	= '';
					my $catname;
					my $id_customers = &load_name('sl_orders','ID_orders',$id_orders,'ID_customers');
					my $tpago = &load_name('sl_orders_payments','ID_orders',$id_orders,'Type');
					$tpago = &load_name('sl_orders','ID_orders',$id_orders,'Ptype');
					$tpago = 'Money Order'	if $tpago eq '';

					my $invoice = &Do_SQL("SELECT Date(cu_invoices.doc_date)doc_date
							FROM cu_invoices_lines
							INNER JOIN cu_invoices ON cu_invoices.ID_invoices=cu_invoices_lines.ID_invoices AND cu_invoices.Status='Certified' AND cu_invoices.invoice_type='ingreso'
							WHERE cu_invoices_lines.ID_orders=$id_orders
							ORDER BY cu_invoices.ID_invoices
							LIMIT 1");
					my ($date_invoice) = $invoice->fetchrow();			

					# Se ocultan datos temporalmente
					$state = &temp_hide_data($state);
					$county = &temp_hide_data($county);
					# $shp_zip = &temp_hide_data($shp_zip);

					## Si type eq 'order' 1 linea por order
					$strout .= qq|"$salesorigins","$tpago","$id_orders","$status","$date","$posteddate","$date_invoice","$shpdate","$capdate","$state","$county","$shp_zip","$id_zones","$zone_name"| if $in{'type'} eq 'order';
					$query = "SELECT 
								IF(LEFT(sl_orders_products.ID_products,3) = 100 AND LENGTH(Related_ID_products) = 9 and left(Related_ID_products,3)=400,
									Related_ID_products,
									sl_orders_products.ID_products
								) AS ID_products,
								IF(sl_parts.Name IS NOT NULL,
									sl_parts.Name,
									IF(sl_services.Name IS NOT NULL,sl_services.Name,sl_products.Name)
								) AS Pname,
								Quantity,
								SalePrice,
								sl_orders_products.Discount,
								sl_orders_products.Tax,
								sl_orders_products.Shipping,
								sl_orders_products.ShpTax,
								IF(sl_orders_products.Cost > 0,
									sl_orders_products.Cost,
									IF(SLTV_NetCost >=0,SLTV_NetCost,0)
								)AS SLTV_NetCost,
								Channel, 
								ID_categories
							FROM 
								sl_orders_products 
								INNER JOIN sl_orders on (sl_orders_products.ID_orders = sl_orders.ID_orders)
								LEFT JOIN sl_salesorigins on (sl_orders.ID_salesorigins=sl_salesorigins.ID_salesorigins)
								LEFT JOIN sl_products ON sl_products.ID_products = RIGHT(sl_orders_products.ID_products,6)
								LEFT JOIN sl_services ON sl_services.ID_services = RIGHT(sl_orders_products.ID_products,4)
								LEFT JOIN sl_parts ON (ID_parts = RIGHT(Related_ID_products,4) and left(Related_ID_products,3)=400 )
							WHERE 
								sl_orders_products.ID_orders = $id_orders 
								AND sl_orders_products.Status NOT IN('Order Cancelled', 'Inactive')
							ORDER BY  ID_orders_products ;";
					my $sthi = &Do_SQL($query);
					#$log_query .= $query . "\n\n ================================== \n\n";
					$prodline = 0;
					while(my($id_products,$pname,$qty,$sprice,$pdisc,$tax,$shp,$shptax,$netcost,$salesorigins,$idcat) = $sthi->fetchrow())
					{

						++$prodline;
						$rush_shipping = 'Yes' if $id_products eq '600001046';

						###
						### Product Family
						###
						if($prodline == 1 or $in{'type'} ne 'order') {

							if(!$idcat){

								my ($sthc) = Do_SQL("SELECT ID_categories FROM sl_products_categories WHERE ID_products = RIGHT($id_products,6) LIMIT 1;");
								$idcat = $sthc->fetchrow();

							}

							$catname = $idcat ? &load_name('sl_categories','ID_categories', $idcat, 'Title') : 'N/A';

						}


						## Si type eq 'order' 1 linea por orden
						if($in{'type'} eq 'order'){
							$strprod .= qq|,"$qty","|.&format_sltvid($id_products).qq|","$pname","$sprice"| if ($prodline<=$maxprod);

							$items++;
							$total	+=	$sprice;
							$tdisc	+=	$pdisc;

							$ttax	+=	$tax;
							$ttax	+=	$shptax;

							$tot_ship += $shptax + $shp;

							$tshp	+=	$shp;
							$tcost	+=	$netcost;
							$torder	+=	$sprice-$pdisc+$tax+$shp+$shptax;
						}else{
							$tot_ship_prod = $shptax +$shp;
							$strout .= qq|"$salesorigins","$tpago","$id_orders","$status","$date","$posteddate","$shpdate", "$state","$county","$qty","|.&format_sltvid($id_products).qq|","$pname","$shp","$catname","$agentname","$user_type","$tot_ship_prod"|;
							$strout .= "\r\n"
						}
					}
					
					## Si type eq 'order' 1 linea por orden
					if($in{'type'} eq 'order'){
						for ($items..$maxprod-1){
							$strprod .= ",,,,";
						}
						
						$strout .= qq|$strprod,"$torder","$catname","$agentname","$user_type","$tot_ship"|;
						$strout .= "\r\n";

						$tot_ship=0;
					}


					print $strout;
				}
			}
			&auth_logging('report_view','');
			&log_reports($log_query, 'rep_bi_allorders_logistics');

			return;
		}else{
			$va{'message'} = &trans_txt('search_nomatches');
		}
	}
	&log_reports($log_query, 'rep_bi_allorders_logistics');
	print "Content-type: text/html\n\n";
	print &build_page('rep_bi_allorders_logistics.html');
}

1;
