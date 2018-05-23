#!/usr/bin/perl


##################################################################
##########   PACKING LIST     	######################
##################################################################

sub pklist {
# --------------------------------------------------------
# Last Modified on: 10/07/08 13:00:49
# Last Modified by: MCC C. Gabriel Varela S: Se toma en cuenta para cuando se habla de partial shipment
# Last Modified on: 02/09/09 17:07:08
# Last Modified by: MCC C. Gabriel Varela S: Se arregla que en la consulta por defecto no se cuenten servicios dentro de la condici�n 1= (select count ....
# Last Modified on: 02/10/09 10:46:11
# Last Modified by: MCC C. Gabriel Varela S: Se consideran pre�rdenes COD
# Last Modified on: 02/23/09 16:49:18
# Last Modified by: MCC C. Gabriel Varela S: Se agregan validaciones a las consultas de CODs
# Last Modified on: 03/19/09 12:40:55
# Last Modified by: MCC C. Gabriel Varela S: Se toma en cuenta $cfg{'codshptype'}
# Last Time Modified By RB on 2/18/10 12:26 PM : Se modifica para coincidir con el manejo de Ordernes COD, las Preordenes estan en desuso.


	if(!$cfg{'wms_skip_pklist'}){

		my ($sth) = &Do_SQL("SELECT 
								COUNT(DISTINCT sl_orders.ID_orders)
								, COUNT(DISTINCT IF(LENGTH(Related_ID_products) = 9, Related_ID_products, sl_orders_products.ID_products))
							FROM sl_orders 
						    INNER JOIN sl_orders_products on(sl_orders.ID_orders=sl_orders_products.ID_orders )
						    LEFT JOIN  sl_warehouses_batches_orders
								ON sl_warehouses_batches_orders.ID_orders_products = sl_orders_products.ID_orders_products 
								AND sl_warehouses_batches_orders.Status IN ('In Fulfillment','Shipped','In Transit')  
						    WHERE sl_warehouses_batches_orders.ID_orders_products IS NULL
							AND sl_orders.Ptype	!= 'COD' 
							AND sl_orders.Status  = 'Processed' 
							AND sl_orders.StatusPrd	 = 'In Fulfillment'
							AND sl_orders_products.Status IN ('Active','Exchange','Undeliverable','ReShip') 
							AND sl_orders_products.SalePrice >= 0
							AND sl_orders_products.ID_products NOT LIKE '6%';");
		($va{'toff'}, $va{'items'})  = $sth->fetchrow();	
		
		# my ($sth) = &Do_SQL("SELECT IF(LENGTH(Related_ID_products) = 9, Related_ID_products, sl_orders_products.ID_products) AS ID_products
		# 		FROM sl_orders 
		# 		INNER JOIN sl_orders_products
		# 			USING(ID_orders)
		# 		LEFT JOIN sl_warehouses_batches_orders
		# 			ON sl_orders_products.ID_orders_products=sl_warehouses_batches_orders.ID_orders_products
		# 			AND sl_warehouses_batches_orders.Status IN ('In Fulfillment','Shipped','In Transit')  
		# 		WHERE sl_warehouses_batches_orders.ID_orders_products IS NULL
		# 		AND sl_orders.Ptype	!= 'COD' 
		# 		AND sl_orders.Status = 'Processed' 
		# 		AND sl_orders.StatusPrd	 = 'In Fulfillment'
		# 		AND sl_orders_products.Status IN ('Active','Exchange','Undeliverable','ReShip') 
		# 		AND sl_orders_products.SalePrice >= 0
		# 		AND sl_orders_products.ID_products NOT LIKE '6%' 
		# 		GROUP BY IF(LENGTH(Related_ID_products) = 9, Related_ID_products, sl_orders_products.ID_products)");
		# $va{'items'} = $sth->rows;	
		
		my ($sth) = &Do_SQL("SELECT 
								COUNT(DISTINCT sl_orders.ID_orders)
								, COUNT(DISTINCT IF(LENGTH(Related_ID_products) = 9, Related_ID_products, sl_orders_products.ID_products))
							FROM sl_orders
							INNER JOIN sl_orders_products
								ON sl_orders_products.ID_orders=sl_orders.ID_orders
							LEFT JOIN sl_warehouses_batches_orders
								ON sl_orders_products.ID_orders_products=sl_warehouses_batches_orders.ID_orders_products
								AND sl_warehouses_batches_orders.Status IN ('In Fulfillment','Shipped','In Transit')  
							WHERE sl_warehouses_batches_orders.ID_orders_products IS NULL
							AND sl_orders.Ptype != 'COD' AND sl_orders.Status='Processed' 
							AND sl_orders.StatusPrd='In Dropshipment'");							
		($va{'tods'}, $va{'itemsds'}) = $sth->fetchrow();	
		
		# my ($sth) = &Do_SQL("SELECT IF(LENGTH(Related_ID_products) = 9, Related_ID_products, sl_orders_products.ID_products) AS ID_products 
		# 			FROM sl_orders 
		# 			INNER JOIN sl_orders_products 
		# 				ON sl_orders.ID_orders=sl_orders_products.ID_orders 
		# 			LEFT JOIN sl_warehouses_batches_orders
		# 				ON sl_orders_products.ID_orders_products=sl_warehouses_batches_orders.ID_orders_products
		# 				AND sl_warehouses_batches_orders.Status IN ('In Fulfillment','Shipped','In Transit')  
		# 			WHERE sl_warehouses_batches_orders.ID_orders_products IS NULL
		# 			AND sl_orders.Ptype !='COD' AND sl_orders.Status='Processed' 
		# 			AND StatusPrd='In Dropshipment'
		# 			AND sl_orders_products.Status='Active' 
		# 			GROUP BY IF(LENGTH(Related_ID_products) = 9, Related_ID_products, sl_orders_products.ID_products);");						
		# $va{'itemsds'} = $sth->rows;		
		
		my ($sth) = &Do_SQL("SELECT 
								COUNT(DISTINCT sl_orders.ID_orders)
								, COUNT(DISTINCT IF(LENGTH(Related_ID_products) = 9, Related_ID_products, sl_orders_products.ID_products))
							FROM sl_orders 
							INNER JOIN sl_orders_products 
								ON sl_orders.ID_orders=sl_orders_products.ID_orders 
							LEFT JOIN sl_warehouses_batches_orders
								ON sl_orders_products.ID_orders_products=sl_warehouses_batches_orders.ID_orders_products
								AND sl_warehouses_batches_orders.Status IN ('In Fulfillment','Shipped','In Transit')  
							WHERE sl_warehouses_batches_orders.ID_orders_products IS NULL
							AND sl_orders.Ptype != 'COD' 
							AND sl_orders.Status='Shipped'
							AND sl_orders.StatusPrd='In Fulfillment';");						
		($va{'toffps'}, $va{'itemsps'}) = $sth->fetchrow();	
		
		# my ($sth) = &Do_SQL("SELECT IF(LENGTH(Related_ID_products) = 9, Related_ID_products, sl_orders_products.ID_products) AS ID_products 
		# 			FROM sl_orders 
		# 			INNER JOIN sl_orders_products 
		# 				ON sl_orders.ID_orders=sl_orders_products.ID_orders 
		# 			LEFT JOIN sl_warehouses_batches_orders
		# 				ON sl_orders_products.ID_orders_products=sl_warehouses_batches_orders.ID_orders_products
		# 				AND sl_warehouses_batches_orders.Status IN ('In Fulfillment','Shipped','In Transit')  
		# 			WHERE sl_warehouses_batches_orders.ID_orders_products IS NULL
		# 			AND Ptype !='COD'
		# 			AND sl_orders.Status='Shipped' 
		# 			AND StatusPrd='In Fulfillment' 
		# 			AND sl_orders_products.Status='Active' 
		# 			GROUP BY IF(LENGTH(Related_ID_products) = 9, Related_ID_products, sl_orders_products.ID_products);");		 				 
		# $va{'itemsps'} = $sth->rows;	
		
		my ($sth) = &Do_SQL("SELECT 
								COUNT(DISTINCT sl_orders.ID_orders)
								, COUNT(DISTINCT IF(LENGTH(Related_ID_products) = 9, Related_ID_products, sl_orders_products.ID_products))
							FROM sl_orders 
							INNER JOIN sl_orders_products 
								ON sl_orders.ID_orders=sl_orders_products.ID_orders 
							LEFT JOIN sl_warehouses_batches_orders
								ON sl_orders_products.ID_orders_products=sl_warehouses_batches_orders.ID_orders_products
								AND sl_warehouses_batches_orders.Status IN ('In Fulfillment','Shipped','In Transit')  
							WHERE sl_warehouses_batches_orders.ID_orders_products IS NULL
							AND Ptype != 'COD' 
							AND sl_orders.Status='Shipped' 
							AND StatusPrd='In Dropshipment'");
		($va{'todsps'}, $va{'itemsdsps'}) = $sth->fetchrow();	

		# my ($sth) = &Do_SQL("SELECT IF(LENGTH(Related_ID_products) = 9, Related_ID_products, sl_orders_products.ID_products) AS ID_products
		# 			FROM sl_orders 
		# 			INNER JOIN sl_orders_products 
		# 				ON sl_orders.ID_orders=sl_orders_products.ID_orders
		# 			LEFT JOIN sl_warehouses_batches_orders
		# 				ON sl_orders_products.ID_orders_products=sl_warehouses_batches_orders.ID_orders_products
		# 				AND sl_warehouses_batches_orders.Status IN ('In Fulfillment','Shipped','In Transit')  
		# 			WHERE sl_warehouses_batches_orders.ID_orders_products IS NULL
		# 			AND Ptype !='COD'
		# 			AND sl_orders.Status='Shipped' 
		# 			AND StatusPrd='In Dropshipment' 
		# 			AND sl_orders_products.Status='Active' 
		# 			GROUP BY IF(LENGTH(Related_ID_products) = 9, Related_ID_products, sl_orders_products.ID_products);");	
		# $va{'itemsdsps'} = $sth->rows;		
		
		$sth=&Do_SQL("SELECT 
						COUNT(DISTINCT NPreorders)
						, COUNT(DISTINCT ID_products) 
					from 
						(
							SELECT 
								sl_orders_products.ID_products
								, sl_orders_products.ID_orders as NPreorders
							FROM 
								sl_orders_products
							INNER JOIN 
								sl_orders 
							USING 
								(ID_Orders)	
							LEFT JOIN 
								sl_warehouses_batches_orders
							ON 
								sl_orders_products.ID_orders_products = sl_warehouses_batches_orders.ID_orders_products
								AND sl_warehouses_batches_orders.Status IN ('In Fulfillment','Shipped','In Transit')  
							WHERE 
								sl_warehouses_batches_orders.ID_orders_products IS NULL
								and ID_products NOT LIKE  '6%' 
								and (isnull(ShpDate) or ShpDate='0000-00-00') 
								and (isnull(Tracking) or Tracking='')
								and (isnull(ShpProvider) or ShpProvider='')
								and shp_type = '". $cfg{'codshptype'} ."'
								and Ptype = 'COD'
								and sl_orders.Status='Processed'
								and StatusPrd = 'In Fulfillment'
								and sl_orders_products.Status = 'Active'
								and sl_orders_products.SalePrice > 0
								and sl_orders_products.Quantity > 0
								and 0 < (SELECT COUNT(*) FROM sl_orders_payments WHERE ID_orders = sl_orders.ID_orders AND Type='COD' AND Status IN('Approved','Denied','Pending','Insufficient Funds') )
							GROUP BY 
								sl_orders_products.ID_orders
						)as tempo;");

		($va{'tpcodff'}, $va{'itemscodff'}) = $sth->fetchrow;
		
		# $sth=&Do_SQL("SELECT COUNT(NPreorders) FROM (
		# 			SELECT sl_orders_products.ID_products,sl_orders_products.ID_orders as NPreorders,PaymentsCOD,PaymentsNotCOD
		# 			FROM   sl_orders_products
		# 			INNER JOIN sl_orders on(sl_orders_products.ID_orders=sl_orders.ID_orders)
		# 			LEFT JOIN sl_warehouses_batches_orders
		# 				ON sl_orders_products.ID_orders_products=sl_warehouses_batches_orders.ID_orders_products
		# 				AND sl_warehouses_batches_orders.Status IN ('In Fulfillment','Shipped','In Transit')  
		# 			INNER JOIN (
		# 				SELECT ID_orders,sum(if(Type='COD',1,0))as PaymentsCOD,sum(if(Type!='COD',1,0))as PaymentsNotCOD
		# 				FROM sl_orders_payments
		# 				GROUP BY ID_orders
		# 				having PaymentsCOD>0)as tempo on (tempo.ID_orders=sl_orders.ID_orders)
		# 				WHERE sl_warehouses_batches_orders.ID_orders_products IS NULL
		# 			and ID_products NOT LIKE '6%' 
		# 			and (isnull(ShpDate) or ShpDate='0000-00-00' or ShpDate='') 
		# 			and (isnull(Tracking) or Tracking='')
		# 			and (isnull(ShpProvider) or ShpProvider='')
		# 			/*and shp_type=$cfg{'codshptype'}*/
		# 			and Ptype='COD'
		# 			and sl_orders.Status='Processed'
		# 			and StatusPrd='In Fulfillment'
		# 			and sl_orders_products.Status='Active'
		# 			and sl_orders_products.SalePrice>0
		# 			and sl_orders_products.Quantity>0
		# 			and sl_orders.Status not in ('Void', 'Cancelled')
		# 			GROUP BY sl_orders_products.ID_orders
		# 		)as tempo");			
		# ($va{'tpcodff'})=$sth->fetchrow;

	}

	
	print "Content-type: text/html\n\n";
	$va{'page_title'} = trans_txt("pageadmin");
	print &build_page('pklist.html');
}

##################################################################
##########   ORDERS READY TO FULFILL
##################################################################


sub packing_toff {
# --------------------------------------------------------	
# Created on: Unknown
# Last Modified on: 07/07/2008
# Last Modified by: Jose Ramirez Garcia
# Author: Unknown
# Description : Modified to show only products (no services) without links
# Parameters :
# Fulfillment Type
# Last Modified on: 10/07/08 13:13:05
# Last Modified by: MCC C. Gabriel Varela S: Se toma en cuenta partial shipment
# Last Modified on: 02/09/09 17:07:08
# Last Modified by: MCC C. Gabriel Varela S: Se arregla que en la consulta por defecto no se cuenten servicios dentro de la condición 1= (select count ....
# Last Modified on: 05/15/09 17:42:54
# Last Modified by: MCC C. Gabriel Varela S: Se modifica para mostrar la parte en caso de que corresponda.
# Last Modified on: 05/18/09 11:38:50
# Last Modified by: MCC C. Gabriel Varela S: Se modifica para mostrar las partes sin quitar el producto.
# Last Modified on: 07/15/09 16:51:10
# Last Modified by: MCC C. Gabriel Varela S: Se hace que se pueda mostrar el inventario de las partes cuando corresponda.
# Last Modified RB: 09/11/09  13:46:09 -- Se agrego llamada a la funcion &build_export_setup(sub.base_sltv) que genera un archivo de exportacion basado en configuracion setup.cfg|general.cfg
# Last Modified RB: 03/31/2010  18:28:09 -- Se elimina el telefono del cliente por peticion de Alma Hubbe
# Last Modified by RB on 03/31/2011 05:40:48 PM : Se agrega validacion para ordenes Allnatpro
# Last Modified by RB on 10/11/2011: Se agrega idioma de invoice


	if ($in{'dropship'}){
		$va{'fftype'} = 'Dropship';
		$prdstatus = 'In Dropshipment';
	}else{
		$va{'fftype'} = 'Fullfill';
		$prdstatus = 'In Fulfillment';
	}

	my $ordstatus;
	if($in{'partialshipment'}){
		$ordstatus="'Shipped'";
	}else{
		$ordstatus="'Processed'";
	}

	## All
	my ($sth) = &Do_SQL("SELECT COUNT(DISTINCT sl_orders.ID_orders)
				FROM sl_orders 
			    INNER JOIN sl_orders_products on(sl_orders.ID_orders=sl_orders_products.ID_orders )
			    LEFT JOIN  sl_warehouses_batches_orders
					ON sl_warehouses_batches_orders.ID_orders_products = sl_orders_products.ID_orders_products 
					AND sl_warehouses_batches_orders.Status IN ('In Fulfillment','Shipped','In Transit')  
			    WHERE sl_warehouses_batches_orders.ID_orders_products IS NULL
				AND sl_orders.Ptype	!= 'COD' 
				AND sl_orders.Status	 = 'Processed' 
				AND sl_orders.StatusPrd	 = 'In Fulfillment'
				AND sl_orders_products.Status IN ('Active','Exchange','Undeliverable','ReShip') 
				AND sl_orders_products.SalePrice >= 0");
	$va{'tot_orders'} = $sth->fetchrow();		
	my ($sth) = &Do_SQL("SELECT GROUP_CONCAT(DISTINCT sl_orders.ID_orders) AS ORDERS
				FROM sl_orders 
			    INNER JOIN sl_orders_products on(sl_orders.ID_orders=sl_orders_products.ID_orders )
			    LEFT JOIN  sl_warehouses_batches_orders
					ON sl_warehouses_batches_orders.ID_orders_products = sl_orders_products.ID_orders_products 
					AND sl_warehouses_batches_orders.Status IN ('In Fulfillment','Shipped','In Transit')  
			    WHERE sl_warehouses_batches_orders.ID_orders_products IS NULL
				AND sl_orders.Ptype	!= 'COD' 
				AND sl_orders.Status = 'Processed' 
				AND sl_orders.StatusPrd	 = 'In Fulfillment'
				AND sl_orders_products.Status IN ('Active','Exchange','Undeliverable','ReShip') 
				AND sl_orders_products.SalePrice >= 0;");
	($va{'orders'}) = $sth->fetchrow_array();
	my ($sth) = &Do_SQL("SELECT IF(LENGTH(Related_ID_products) = 9, Related_ID_products, sl_orders_products.ID_products) AS ID_products
			FROM sl_orders 
			INNER JOIN sl_orders_products
				ON sl_orders_products.ID_orders=sl_orders.ID_orders
				AND sl_orders_products.Status='Active' 
				AND sl_orders_products.ID_products NOT LIKE '6%' 
			LEFT JOIN sl_warehouses_batches_orders
				ON sl_orders_products.ID_orders_products=sl_warehouses_batches_orders.ID_orders_products
				AND sl_warehouses_batches_orders.Status IN ('In Fulfillment','Shipped','In Transit')  
			WHERE sl_warehouses_batches_orders.ID_orders_products IS NULL
			AND sl_orders.Ptype	!= 'COD' 
			AND sl_orders.Status=$ordstatus 
			AND StatusPrd='$prdstatus' 
						    AND sl_orders_products.Status IN ('Active','Exchange','Undeliverable','ReShip') 
				AND sl_orders_products.SalePrice >= 0
			GROUP BY IF(LENGTH(Related_ID_products) = 9, Related_ID_products, sl_orders_products.ID_products);");				
	$va{'tot_skus'} = $sth->rows;

	## Last Month
	my ($sth) = &Do_SQL("SELECT COUNT(*) FROM sl_orders WHERE Ptype != 'COD' AND Status=$ordstatus AND StatusPrd='$prdstatus' AND DATEDIFF(Date,CURDATE())>30;");
	$va{'tot_orders_lm'} = $sth->fetchrow();	
	my ($sth) = &Do_SQL("SELECT IF(LENGTH(Related_ID_products) = 9, Related_ID_products, sl_orders_products.ID_products) AS ID_products FROM sl_orders,sl_orders_products WHERE sl_orders.ID_orders=sl_orders_products.ID_orders AND Ptype !='COD' AND sl_orders.Status=$ordstatus AND StatusPrd='$prdstatus' AND sl_orders_products.Status='Active' AND DATEDIFF(sl_orders.Date,CURDATE())>30  AND sl_orders_products.ID_products NOT LIKE '6%' GROUP BY IF(LENGTH(Related_ID_products) = 9, Related_ID_products, sl_orders_products.ID_products);");
	$va{'tot_skus_lm'} = $sth->rows;	


	## This Month
	my ($sth) = &Do_SQL("SELECT COUNT(*) FROM sl_orders WHERE Ptype != 'COD' AND Status=$ordstatus AND StatusPrd='$prdstatus' AND MONTH(Date)=MONTH(NOW()) AND YEAR(Date)=YEAR(NOW())");
	$va{'tot_orders_tm'} = $sth->fetchrow();	
	my ($sth) = &Do_SQL("SELECT IF(LENGTH(Related_ID_products) = 9, Related_ID_products, sl_orders_products.ID_products) AS ID_products FROM sl_orders,sl_orders_products WHERE sl_orders.ID_orders=sl_orders_products.ID_orders AND Ptype !='COD' AND sl_orders.Status=$ordstatus AND StatusPrd='$prdstatus' AND sl_orders_products.Status='Active'  AND MONTH(sl_orders.Date)=MONTH(NOW())  AND YEAR(sl_orders.Date)=YEAR(NOW())  AND sl_orders_products.ID_products NOT LIKE '6%' GROUP BY IF(LENGTH(Related_ID_products) = 9, Related_ID_products, sl_orders_products.ID_products);");
	$va{'tot_skus_tm'} = $sth->rows;	


	## This Week
	my ($sth) = &Do_SQL("SELECT COUNT(*) FROM sl_orders WHERE Ptype != 'COD' AND Status=$ordstatus AND StatusPrd='$prdstatus' AND WEEK(Date)=WEEK(NOW()) AND YEAR(Date)=YEAR(NOW())");
	$va{'tot_orders_tw'} = $sth->fetchrow();	
	my ($sth) = &Do_SQL("SELECT IF(LENGTH(Related_ID_products) = 9, Related_ID_products, sl_orders_products.ID_products) AS ID_products FROM sl_orders,sl_orders_products WHERE sl_orders.ID_orders=sl_orders_products.ID_orders AND Ptype !='COD' AND sl_orders.Status=$ordstatus AND StatusPrd='$prdstatus' AND sl_orders_products.Status='Active'  AND WEEK(sl_orders.Date)=WEEK(NOW()) AND YEAR(sl_orders.Date)=YEAR(NOW()) AND sl_orders_products.ID_products NOT LIKE '6%' GROUP BY IF(LENGTH(Related_ID_products) = 9, Related_ID_products, sl_orders_products.ID_products);");
	$va{'tot_skus_tw'} = $sth->rows;	

	## This Week
	my ($sth) = &Do_SQL("SELECT COUNT(*) FROM sl_orders WHERE Ptype != 'COD' AND Status=$ordstatus AND StatusPrd='$prdstatus' AND DATEDIFF(Date,CURDATE())=1");
	$va{'tot_orders_y'} = $sth->fetchrow();	
	my ($sth) = &Do_SQL("SELECT IF(LENGTH(Related_ID_products) = 9, Related_ID_products, sl_orders_products.ID_products) AS ID_products FROM sl_orders,sl_orders_products WHERE sl_orders.ID_orders=sl_orders_products.ID_orders AND Ptype !='COD' AND sl_orders.Status=$ordstatus AND StatusPrd='$prdstatus' AND sl_orders_products.Status='Active'  AND DATEDIFF(sl_orders.Date,CURDATE())=1  AND sl_orders_products.ID_products NOT LIKE '6%' GROUP BY IF(LENGTH(Related_ID_products) = 9, Related_ID_products, sl_orders_products.ID_products);");
	$va{'tot_skus_y'} = $sth->rows;	

	## This Week
	my ($sth) = &Do_SQL("SELECT COUNT(*) FROM sl_orders WHERE Ptype != 'COD' AND Status=$ordstatus AND StatusPrd='$prdstatus' AND Date = CURDATE()");
	$va{'tot_orders_t'} = $sth->fetchrow();	
	my ($sth) = &Do_SQL("SELECT IF(LENGTH(Related_ID_products) = 9, Related_ID_products, sl_orders_products.ID_products) AS ID_products FROM sl_orders,sl_orders_products WHERE sl_orders.ID_orders=sl_orders_products.ID_orders AND Ptype !='COD' AND sl_orders.Status=$ordstatus AND StatusPrd='$prdstatus' AND sl_orders_products.Status='Active'  AND sl_orders.Date=CURDATE() AND sl_orders_products.ID_products NOT LIKE '6%' GROUP BY IF(LENGTH(Related_ID_products) = 9, Related_ID_products, sl_orders_products.ID_products);");
	$va{'tot_skus_t'} = $sth->rows;	

	## ToDo: Work in progress
	#######################################
	###### Printing 
	#######################################
	if ($in{'print'} and $in{'manifest'}){
		my ($sth) = &Do_SQL("SELECT sl_orders_products.ID_products,Isset,ID_parts, if(NOT ISNULL(ID_parts),400000000+ID_parts,sl_orders_products.ID_products)as ID_products_p
							FROM sl_orders 
							INNER JOIN sl_orders_products on(sl_orders.ID_orders=sl_orders_products.ID_orders)
							INNER JOIN sl_skus on (sl_orders_products.ID_products=ID_sku_products)
							left JOIN (Select ID_sku_products,group_concat(concat(Qty,'|',ID_parts))as ID_parts from sl_skus_parts GROUP BY ID_sku_products)as temp on (sl_skus.ID_sku_products=temp.ID_sku_products)
							WHERE sl_orders_products.Status='Active' 
							AND (ISNULL(ShpDate) OR ShpDate='' OR ShpDate='0000-00-00')
							AND Ptype !='COD'  
							AND sl_orders_products.ID_products>1000000 
							AND sl_orders.Status=$ordstatus 
							AND StatusPrd='$prdstatus' 
							AND LEFT(sl_orders_products.ID_products,1)<>'6' 
							GROUP BY ID_products");
		$va{'matches'} = $sth->rows;
		if ($va{'matches'}>0){
			my (@c) = split(/,/,$cfg{'srcolors'});
			$sth = &Do_SQL("SELECT SUM(Quantity) AS Total,sl_orders_products.ID_products,Isset,ID_parts, if(NOT ISNULL(ID_parts),400000000+ID_parts,sl_orders_products.ID_products)as ID_products_p
							FROM sl_orders 
							INNER JOIN sl_orders_products on(sl_orders.ID_orders=sl_orders_products.ID_orders)
							INNER JOIN sl_skus on (sl_orders_products.ID_products=ID_sku_products)
							LEFT JOIN (Select ID_sku_products,group_concat(concat(Qty,'|',ID_parts))as ID_parts from sl_skus_parts GROUP BY ID_sku_products)as temp on (sl_skus.ID_sku_products=temp.ID_sku_products)
							WHERE Ptype != 'COD' 
							AND sl_orders_products.Status='Active' 
							AND sl_orders_products.ID_products>1000000  
							AND sl_orders.Status=$ordstatus 
							AND StatusPrd='$prdstatus' 
							AND LEFT(sl_orders_products.ID_products,1)<>'6' 
							GROUP BY ID_products 
							ORDER BY SUM(Quantity) DESC");
			while ($rec = $sth->fetchrow_hashref){
				$d = 1 - $d;
				$cadparts="";
				if($rec->{'ID_parts'} ne '')
				{
					#$cadparts.= "<table border='0' cellspacing='0' cellpadding='4' width='100%' class='formtable'>\n";
					@partsin=split(/,/,$rec->{'ID_parts'});
					for(0..$#partsin)
					{
						@qtyid=split(/\|/,$partsin[$_]);
						$cadparts.= "<tr bgcolor='$c[$d]'>\n";
						$cadparts.= "	<td class='smalltext' valign='top' align='center'></td>\n
													<td class='smalltext' valign='top' align='center'>".$rec->{'Total'}*$qtyid[0]."</td>\n
											    <td class='smalltext' valign='top'>".&format_sltvid(400000000+$qtyid[1]). "<br>".&load_db_names('sl_parts','ID_parts',$qtyid[1],'[Name]')."</td>\n
											    <td class='smalltext' valign='top'>".&calc_parts_inventory(400000000+$qtyid[1])." Units</td>\n
											  </tr>\n";
					}
					#$cadparts.= "</table>\n";
				}
				
				$va{'searchresults'} .= "<tr bgcolor='$c[$d]'>\n";
				$va{'searchresults'} .= "  <td class='smalltext' valign='top' align='center'>$rec->{'Total'}</td>";
				$va{'searchresults'} .= "  <td class='smalltext' valign='top'>".&format_sltvid($rec->{'ID_products'}). "</td>\n";
				$va{'searchresults'} .= "  <td class='smalltext' valign='top'>".&load_db_names('sl_products','ID_products',substr($rec->{'ID_products'},3,6),'[Name]<br>[Model]').&load_choices($rec->{'ID_products'})."</td>\n";
				$va{'searchresults'} .= "  <td class='smalltext' valign='top'>".&inventory_by_id($rec->{'ID_products'})."</td>\n";
				$va{'searchresults'} .= "</tr>$cadparts\n";
			}
		}else{
			$va{'searchresults'} = qq|
			<tr>
				<td colspan='3' align="center">|.&trans_txt('search_nomatches').qq|</td>
			</tr>\n|;
		}
		### Print Manifest
		print "Content-type: text/html\n\n";
		print &build_page('header_print.html');
		print &build_page('packing_toff_man.html');
		return
	}elsif($in{'print'} and $in{'page'}=~/^exportfile.*/){
	
		my ($sth) = &Do_SQL("SELECT COUNT(*) FROM sl_orders WHERE Ptype != 'COD' AND sl_orders.Status=$ordstatus AND StatusPrd='$prdstatus'");
		if ($sth->fetchrow>0){	
			my (@ids);
			my ($sth) = &Do_SQL("SELECT sl_orders.ID_orders FROM sl_orders WHERE Ptype != 'COD' AND sl_orders.Status=$ordstatus AND StatusPrd='$prdstatus' ORDER BY ID_orders");
			while ($id_orders = $sth->fetchrow()){
				push(@ids, $id_orders);
			}
			#### Nueva funcion basada en setup.cfg de wms
			&build_export_setup('orders',@ids);
		}
		return;
		
	}elsif ($in{'print'} and $in{'page'} eq 'warehouses_batches'){	
		#### Assign to warehouses_batches
		my ($err);

		my $sth = &Do_SQL("SELECT COUNT(*) FROM sl_warehouses WHERE ID_warehouses=".int($in{'id_warehouses'})." AND ID_warehouses > 0 ");    
	    if ($sth->fetchrow == 0){	
			$error{'id_warehouses'} = &trans_txt('invalid');
	    	++$err;
	    }

		if($in{'id_warehouses'} and !$err) {
									
			if ($in{'action'}){
				 					
				$va{'id_warehouses_batches'}='';
				my $status_warehouses_batches = 0;				
				my $new = $in{'id_warehouses'};
				$va{'id_warehouses_batches'} = &create_warehouse_batch_file($new);
				
				if($va{'id_warehouses_batches'}){
				
				####TDC by warehouse
				my $query= "SELECT sl_orders.ID_orders  
				            FROM sl_orders 
						INNER JOIN sl_orders_products 
							ON sl_orders.ID_orders=sl_orders_products.ID_orders 
						LEFT JOIN  sl_warehouses_batches_orders
							ON sl_warehouses_batches_orders.ID_orders_products = sl_orders_products.ID_orders_products 
							AND sl_warehouses_batches_orders.Status IN ('In Fulfillment','Shipped','In Transit')  
						WHERE sl_warehouses_batches_orders.ID_orders_products IS NULL
				            AND sl_orders.Ptype != 'COD' 
				            AND sl_orders.Status='Processed'
				            AND sl_orders.StatusPrd='In Fulfillment'
						AND sl_orders_products.Status IN ('Active','Exchange','Undeliverable','ReShip') 
						AND sl_orders_products.SalePrice >= 0
				            ORDER BY sl_orders.ID_orders ";
				my ($sth) = &Do_SQL($query);
				my ($total_prod_ord);
			    if ($sth->rows>0){	
					my $sth = &Do_SQL($query);					
					while ($rec = $sth->fetchrow_hashref){
						$total_prod_ord = 0;
						### Insert Remesas Orders 
						my $Query = "SELECT ID_orders_products FROM sl_orders_products 
									WHERE ID_orders = '$rec->{'ID_orders'}' 
									AND Status IN ('Active','Exchange','Undeliverable','ReShip') 
									AND SalePrice >= 0;";
						my ($sth_op) = &Do_SQL($Query);
						while ($rec_op = $sth_op->fetchrow_hashref){
							$Query = "SELECT COUNT(*) FROM sl_warehouses_batches_orders WHERE ID_orders_products = '$rec_op->{'ID_orders_products'}'  AND Status IN ('In Fulfillment','Shipped','In Transit');";
							($sth2) = &Do_SQL($Query);
							($count)=$sth2->fetchrow_array();
							if($count == 0 ){
								$Query = "INSERT INTO sl_warehouses_batches_orders SET ID_warehouses_batches = '".$va{'id_warehouses_batches'}."', ID_orders_products = '".int($rec_op->{'ID_orders_products'})."', Status='In Fulfillment', Date=CURDATE(),Time=CURTIME(),ID_admin_users='$usr{'id_admin_users'}'; ";
								($sth3) = &Do_SQL($Query);
								$status_warehouses_batches =1;
								$total_prod_ord++;
							}					
						}						
						if($total_prod_ord>0){
							$in{'db'} = 'sl_orders';
							## Nota orden enviada en batch		

							&add_order_notes_by_type($rec->{'ID_orders'},&trans_txt('order_batchadded')." $va{'id_warehouses_batches'}","High");
							&auth_logging('order_batchadded', $rec->{'ID_orders'});
						}
					} 

				 	if($status_warehouses_batches){
				 		my $Query = "UPDATE sl_warehouses_batches SET Status='Assigned' WHERE ID_warehouses_batches=$va{'id_warehouses_batches'};";
						my ($sth) = &Do_SQL($Query);
						$in{'db'}='sl_warehouses_batches';
						&auth_logging('warehouses_batches_items_add',$va{'id_warehouses_batches'});
						delete($in{'db'});
				 	}

					delete($in{'page'});
					delete($in{'action'});
					delete($in{'id_warehouses'});
					$va{'message'}=&trans_txt("warehouses_batches_assigned") . ": $va{'id_warehouses_batches'}";
					 
				}
				
			  }
							 
			}
 
		}else{
			++$err;
			$error{'id_warehouses'}=&trans_txt('required');
		}

	}elsif ($in{'print'} and $in{'page'}){
		my ($sth) = &Do_SQL("SELECT COUNT(*) FROM sl_orders WHERE Ptype != 'COD' AND sl_orders.Status=$ordstatus AND StatusPrd='$prdstatus'");
		if ($sth->fetchrow>0){
			print "Content-type: text/html\n\n";
			print &build_page('header_print.html');
			### Print Manifest
			if ($in{'page'} eq 'invoiceblank'){
				$cmd = 'invoices';
			}else{
				$cmd = 'pinvoices';
			}				
			my ($num);
			$in{'db'} = 'sl_orders';
			$in{'toprint'}=1;		
			my ($sth) = &Do_SQL("SELECT sl_orders.ID_orders FROM sl_orders WHERE Ptype != 'COD' AND sl_orders.Status=$ordstatus AND StatusPrd='$prdstatus' ORDER BY ID_orders");
			while ($in{'id_orders'} = $sth->fetchrow){
				if ($num>0){
					print "<DIV STYLE='page-break-before:always'></DIV>";
				}					
				&load_cfg('sl_orders');
				$in{'toprint'}  = $in{'id_orders'};
				my (%rec) = &get_record($db_cols[0],$in{'id_orders'},$in{'db'});
				if ($rec{lc($db_cols[0])}){
					foreach my $key (sort keys %rec) {
						$in{lc($key)} = $rec{$key};
						($db_valid_types{lc($key)} ne 'html') and ($in{lc($key)} =~ s/\n/<br>/g);
					}
					$in{'shpdate'} = $shpdate;
					#$va{'shp_phone'} = &load_customer_phone($in{'id_customers'});
					$va{'shp_phone'} = "";
					## User Info
					&get_db_extrainfo('admin_users',$in{'id_admin_users'});
					
					## Regular or Allnatpro Invoice?
					my $customer_type=&load_name('sl_customers','ID_customers',$in{'id_customers'},'Type');
					my $xcmd = $customer_type eq 'Allnatpro' ? '_allnatpro' : '';
					$xcmd = '_whole' if $customer_type =~ /wholesale/i;

					# Extraemos el idioma del invoice
					$xcmd .= &load_name('sl_orders','ID_orders',$in{'id_orders'},'language') eq 'english' ? '_en' : '';
					
					my ($func) = 'view_' . $cmd . $xcmd;
					if (defined &$func){
						&$func;
					}
					
					print &build_page($cmd . $xcmd .'_print.html');
					#print &html_print_record(%rec);
				}
				++$num;				
			}
			return
		}else{
			&trans_txt('noprint');
			print "Content-type: text/html\n\n";
			print &build_page('toprint_msg.html');
			return;
			
		}
	}

	print "Content-type: text/html\n\n";
	print &build_page('packing_toff.html');
}


sub packing_toff_orders {
# --------------------------------------------------------	
# Created on: Unknown
# Last Modified on: 07/07/2008
# Last Modified by: Jose Ramirez Garcia
# Author: Unknown
# Description : Modified to select the orders will be modified
# Parameters :
## Fulfillment Type
# Last Modified on: 10/07/08 11:11:39
# Last Modified by: MCC C. Gabriel Varela S: Se agrega columna de número de pagos para la orden y se toma en cuenta partial shipment
# Last Modified on: 10/08/08 11:59:45
# Last Modified by: MCC C. Gabriel Varela S: Se hace que se muestren los productos de la orden
# Last Modified on: 05/22/09 12:19:36
# Last Modified by: MCC C. Gabriel Varela S: Se cambia consulta para optimizar. Saludos.

	if ($in{'dropship'}){
		$va{'fftype'} = 'Dropship';
		$prdstatus = 'In Dropshipment';
	}else{
		$va{'fftype'} = 'Fullfill';
		$prdstatus = 'In Fulfillment';
	}
	my $ordstatus;
	if($in{'partialshipment'}){
		$ordstatus="'Shipped'";
	}else{
		$ordstatus="'Processed'";
	}
	
	print "Content-type: text/html\n\n";


	if($in{'remove'} eq 'alls'){
		my ($sth)	= &Do_SQL("UPDATE sl_orders SET StatusPrd='None' WHERE Ptype != 'COD' AND sl_orders.Status=$ordstatus AND StatusPrd='$prdstatus';");
		&auth_logging('orders_updated',"");
		$va{'message'} = &trans_txt('done');	
	}elsif($in{'remove'} eq '1s'){
		if($in{'ordersselected'} && $in{'ordersselected'} !~ m/,,.*/){
			chop($in{'ordersselected'});
			my ($sth)	= &Do_SQL("UPDATE sl_orders SET StatusPrd='None' WHERE Ptype != 'COD' AND sl_orders.Status=$ordstatus AND StatusPrd='$prdstatus' AND sl_orders.ID_orders IN($in{'ordersselected'});");
			&auth_logging('orders_updated',"");
			$va{'message'} = &trans_txt('done');			
		}
	}elsif ($in{'id_warehouses'}){	
		#### Assign to warehouses_batches
		my ($err);

		my $sth = &Do_SQL("SELECT COUNT(*) FROM sl_warehouses WHERE ID_warehouses=".int($in{'id_warehouses'})." AND ID_warehouses > 0 ");    
	    if ($sth->fetchrow == 0){	
			$error{'id_warehouses'} = &trans_txt('invalid');
	    	++$err;
	    }

		if($in{'id_warehouses'} and !$err) {
									
			if ($in{'action'}){
				 					
				$va{'id_warehouses_batches'}='';
				my $status_warehouses_batches = 0;				
				my $new = $in{'id_warehouses'};
				$va{'id_warehouses_batches'} = &create_warehouse_batch_file($new);
				
				if($va{'id_warehouses_batches'}){
				
					if($in{'ordersselected'} && $in{'ordersselected'} !~ m/,,.*/){
						chop($in{'ordersselected'});
					}

					####TDC by warehouse
					my $query= "SELECT sl_orders.ID_orders  
					            FROM sl_orders 
							INNER JOIN sl_orders_products 
								ON sl_orders.ID_orders=sl_orders_products.ID_orders 
							LEFT JOIN  sl_warehouses_batches_orders
								ON sl_warehouses_batches_orders.ID_orders_products = sl_orders_products.ID_orders_products 
								AND sl_warehouses_batches_orders.Status IN ('In Fulfillment','Shipped','In Transit')  
							WHERE sl_warehouses_batches_orders.ID_orders_products IS NULL
								AND sl_orders.ID_orders IN($in{'ordersselected'})
					            AND sl_orders.Ptype != 'COD' 
					            AND sl_orders.Status='Processed'
					            AND sl_orders.StatusPrd='In Fulfillment'
							AND sl_orders_products.Status IN ('Active','Exchange','Undeliverable','ReShip') 
							AND sl_orders_products.SalePrice >= 0
					            ORDER BY sl_orders.ID_orders ";
					my ($sth) = &Do_SQL($query);
					my ($total_prod_ord);
				    if ($sth->rows>0){	
						my $sth = &Do_SQL($query);					
						while ($rec = $sth->fetchrow_hashref){
							$total_prod_ord = 0;
							### Insert Remesas Orders 
							my $Query = "SELECT ID_orders_products FROM sl_orders_products 
										WHERE ID_orders = '$rec->{'ID_orders'}' 
										AND Status IN ('Active','Exchange','Undeliverable','ReShip') 
										AND SalePrice >= 0;";
							my ($sth_op) = &Do_SQL($Query);
							while ($rec_op = $sth_op->fetchrow_hashref){
								$Query = "SELECT COUNT(*) FROM sl_warehouses_batches_orders WHERE ID_orders_products = '$rec_op->{'ID_orders_products'}'  AND Status IN ('In Fulfillment','Shipped','In Transit');";
								($sth2) = &Do_SQL($Query);
								($count)=$sth2->fetchrow_array();
								if($count == 0 ){
									$Query = "INSERT INTO sl_warehouses_batches_orders SET ID_warehouses_batches = '".$va{'id_warehouses_batches'}."', ID_orders_products = '".int($rec_op->{'ID_orders_products'})."', Status='In Fulfillment', Date=CURDATE(),Time=CURTIME(),ID_admin_users='$usr{'id_admin_users'}'; ";
									($sth3) = &Do_SQL($Query);
									$status_warehouses_batches =1;
									$total_prod_ord++;
								}					
							}						
							if($total_prod_ord>0){
								$in{'db'} = 'sl_orders';
								## Nota orden enviada en batch		

								&add_order_notes_by_type($rec->{'ID_orders'},&trans_txt('order_batchadded')." $va{'id_warehouses_batches'}","High");
								&auth_logging('order_batchadded', $rec->{'ID_orders'});
							}
						} 

					 	if($status_warehouses_batches){
					 		my $Query = "UPDATE sl_warehouses_batches SET Status='Assigned' WHERE ID_warehouses_batches=$va{'id_warehouses_batches'};";
							my ($sth) = &Do_SQL($Query);
							$in{'db'}='sl_warehouses_batches';
							&auth_logging('warehouses_batches_items_add',$va{'id_warehouses_batches'});
							delete($in{'db'});
					 	}

						delete($in{'action'});
						delete($in{'id_warehouses'});
						delete($in{'ordersselected'});
						$va{'message'}=&trans_txt("warehouses_batches_assigned") . ": $va{'id_warehouses_batches'}";
						 
					}
								 
				}else{
					++$err;
					$error{'id_warehouses'}=&trans_txt('warehouses_batches_invalid');	
				}

			}
 
		}else{
			++$err;
			$error{'id_warehouses'}=&trans_txt('required');
		}

	}

		
	$va{'matches'} = 1;
	$va{'pageslist'} = 1;
	
	my ($sth) = &Do_SQL("SELECT COUNT(DISTINCT sl_orders.ID_orders) FROM sl_orders 
			    INNER JOIN sl_orders_products on(sl_orders.ID_orders=sl_orders_products.ID_orders )
			    LEFT JOIN  sl_warehouses_batches_orders
					ON sl_warehouses_batches_orders.ID_orders_products = sl_orders_products.ID_orders_products 
					AND sl_warehouses_batches_orders.Status IN ('In Fulfillment','Shipped','In Transit')  
			    WHERE sl_warehouses_batches_orders.ID_orders_products IS NULL
						AND Ptype != 'COD'
						AND sl_orders.Status=$ordstatus 
						AND StatusPrd='$prdstatus'
				AND sl_orders_products.Status IN ('Active','Exchange','Undeliverable','ReShip') 
				AND sl_orders_products.SalePrice >= 0;");
	$va{'matches'} = $sth->fetchrow;
	
	if ($va{'matches'}>0){
		(!$in{'nh'}) and ($in{'nh'}=1);
		$first = ($in{'nh'} - 1) * $usr{'pref_maxh'};			
		($va{'pageslist'},$qs) = &pages_list($in{'nh'},"/cgi-bin/mod/$usr{'application'}/admin",$va{'matches'},$usr{'pref_maxh'});
		my (@c) = split(/,/,$cfg{'srcolors'});

		$sth = &Do_SQL("SELECT sl_orders.*, COUNT(ID_orders_payments) AS NumPay 
				FROM sl_orders_payments 
				INNER JOIN sl_orders on(sl_orders_payments.ID_orders=sl_orders.ID_orders)
				INNER JOIN sl_orders_products on(sl_orders.ID_orders=sl_orders_products.ID_orders )
				LEFT JOIN sl_products on(sl_products.ID_products=RIGHT(sl_orders_products.ID_products,6)) 
			    LEFT JOIN sl_parts ON(sl_parts.ID_parts=RIGHT(sl_orders_products.ID_products,4)) 
				LEFT JOIN  sl_warehouses_batches_orders
					ON sl_warehouses_batches_orders.ID_orders_products = sl_orders_products.ID_orders_products 
					AND sl_warehouses_batches_orders.Status IN ('In Fulfillment','Shipped','In Transit')  
				WHERE sl_warehouses_batches_orders.ID_orders_products IS NULL
				AND Ptype != 'COD'
				AND sl_orders.Status=$ordstatus
				AND StatusPrd='$prdstatus' 
				AND sl_orders_products.Status IN ('Active','Exchange','Undeliverable','ReShip') 
				AND sl_orders_products.SalePrice >= 0
				GROUP BY sl_orders_payments .ID_orders
				ORDER BY sl_orders.ID_orders DESC 
				LIMIT $first,$usr{'pref_maxh'}");

		my $sth1,$rec1,$cont,$prodcad;
		while ($rec = $sth->fetchrow_hashref){
			$d = 1 - $d;
			$cont=0;
			$va{'searchresults'} .= "<tr bgcolor='$c[$d]' onmouseover='m_over(this)' onmouseout='m_out(this)'>\n";
			$va{'searchresults'} .= "  <td class='smalltext' valign='top' align='center'><input type='checkbox' class='checkbox' id='chkor_$rec->{'ID_orders'}' name='id_ordersttia' value='$rec->{'ID_orders'}' onclick='chk_ord($rec->{'ID_orders'})'>&nbsp;</td>\n";
			$va{'searchresults'} .= "  <td class='smalltext' valign='top' align='center'><a href='#' onClick=\"trjump('/cgi-bin/mod/wms/dbman?cmd=opr_orders&view=$rec->{'ID_orders'}&check_status=1')\">$rec->{'ID_orders'}</a></td>\n";
			$va{'searchresults'} .= "  <td class='smalltext' valign='top'>$rec->{'Date'}</td>\n";
			$va{'searchresults'} .= "  <td class='smalltext' valign='top'>$rec->{'CompanyName'} ".&load_db_names('sl_customers','ID_customers',$rec->{'ID_customers'},"[FirstName] [LastName1]")."</td>\n";
			$va{'searchresults'} .= "  <td class='smalltext' valign='top'>$rec->{'NumPay'}</td>\n";
			$va{'searchresults'} .= "</tr>\n";
			$sth1=&Do_SQL("Select ID_orders,sl_orders_products.ID_products, Name, Model
						from sl_orders_products
						INNER JOIN sl_products on (right(sl_orders_products.ID_products,6)=sl_products.ID_products)
						where id_orders=$rec->{'ID_orders'} and sl_products.status not in('Inactive','Order Cancelled')");
			while($rec1=$sth1->fetchrow_hashref) {
				$va{'searchresults'} .= "<tr bgcolor='$c[$d]' onmouseover='m_over(this)' onmouseout='m_out(this)'>\n";
				$cont++;
				$va{'searchresults'} .= "  <td class='smalltext' valign='top'></td>\n";
				if($cont==1){
					$prodcad="Products: ";
				}else{
					$prodcad="";
				}
				$va{'searchresults'} .= "  <td class='smalltext' valign='top'>$prodcad</td>\n";
				$va{'searchresults'} .= "  <td class='smalltext' valign='top' colspan='3'>".&format_sltvid($rec1->{'ID_products'}).": $rec1->{'Name'}/$rec1->{'Model'}</td>\n";
				$va{'searchresults'} .= "</tr>\n";
			}
			$va{'searchresults'} .= "</tr>\n";
		}
	}else{
		$va{'pageslist'} = 1;
		$va{'searchresults'} = qq|
		<tr>
			<td colspan='3' align="center">|.&trans_txt('search_nomatches').qq|</td>
		</tr>\n|;
	}
	print &build_page('packing_toff_orders.html');
}

sub packing_partialship{
# --------------------------------------------------------
# Forms Involved: 
# Created on: 10/06/08 12:12:49
# Author: MCC C. Gabriel Varela S.
# Description :   
# Parameters :
# Last Modified on: 10/09/08 16:04:30
# Last Modified by: MCC C. Gabriel Varela S: Se excluyen los productos que no sean Active
	require ("../common/subs/sub.search.html.cgi");
	my($numhits,$first,$nh,$sth);
	if($in{'view'})
	{
		@db_cols = ('ID_orders','Date','ID_customers','StatusPay','StatusPrd','Status');
		$in{'db'}="sl_orders";
		$in{'cmd'}='orders';
		$in{'id_orders'}=$in{'view'};
		$in{'search'}="Search";
		$in{'sx'}=1;
		$script_url="/cgi-bin/mod/wms/dbman";
		$perm{'suf'}="orders";
		return &html_search_select;
		#return &html_view_record; 
		
	}
	$sth = &Do_SQL("SELECT sl_orders.ID_orders,sl_orders.Date,ID_customers,StatusPay,StatusPrd,sl_orders.Status,sum(if(ID_products NOT LIKE '6%' and ((isnull(ShpDate)or ShpDate='0000-00-00')),1,0))as NotSended,sum(if(ID_products NOT LIKE '6%' and ((NOT ISNULL(ShpDate)and ShpDate!='0000-00-00')),1,0))as Sended
			FROM `sl_orders` 
			INNER JOIN sl_orders_products on (sl_orders.ID_orders=sl_orders_products.ID_orders) 
			where Ptype != 'COD' AND sl_orders.Status='Shipped' and sl_orders_products.Status in('Active','Exchange') and SalePrice>=0
			GROUP BY sl_orders.ID_orders
			having NotSended>0 and Sended>0");
	$numhits=$sth->rows;
	$in{'nh'} ? ($nh = $in{'nh'}) : ($nh = 1);
	$first = ($usr{'pref_maxh'} * ($nh - 1));
	
	$sth = &Do_SQL("SELECT sl_orders.ID_orders,sl_orders.Date,ID_customers,StatusPay,StatusPrd,sl_orders.Status,sum(if(ID_products NOT LIKE '6%' and ((isnull(ShpDate)or ShpDate='0000-00-00')),1,0))as NotSended,sum(if(ID_products NOT LIKE '6%' and ((NOT ISNULL(ShpDate)and ShpDate!='0000-00-00')),1,0))as Sended
			FROM `sl_orders` 
			INNER JOIN sl_orders_products on (sl_orders.ID_orders=sl_orders_products.ID_orders) 
			where Ptype != 'COD' AND sl_orders.Status='Shipped' and sl_orders_products.Status in('Active','Exchange') and SalePrice>=0
			GROUP BY sl_orders.ID_orders
			having NotSended>0 and Sended>0 limit $first,$usr{'pref_maxh'}");
	my $rec,@hits,$column;
	#my (@c) = split(/,/,$cfg{'srcolors'});
	@db_cols = ('ID_orders','Date','ID_customers','StatusPay','StatusPrd','Status');
	@headerfields = split(/,/, "ID_orders,Date,sl_customers:ID_customers.FirstName,sl_customers:ID_customers.LastName1,StatusPay,StatusPrd,Status");
	while ($rec = $sth->fetchrow_hashref) {
		foreach my $column (@db_cols) {
			push(@hits, $rec->{$column});
		}
#		$d = 1 - $d;
#		$va{'searchresults'} .= "<tr onmouseover='m_over(this)' onmouseout='m_out(this)' bgcolor='$c[$d]' OnClick=\"trjump('/cgi-bin/mod/wms/dbman?cmd=orders&view=$rec->{'ID_orders'}')\">
#															
#														 </tr>";
	}
	$in{'show_only_list'}=1;
	#$in{'cmd'}='orders';
	#$script_url="/cgi-bin/mod/wms/dbman";
	return &html_view_success($numhits,@hits);
#	print "Content-type: text/html\n\n";
#	print &build_page('packing_partialship.html');
}



sub packing_toff_items {
# --------------------------------------------------------	
# Created on: Unknown
# Last Modified on: 08/26/2008
# Last Modified by: Jose Ramirez Garcia
# Author: Unknown
# Description : 
# Parameters :
# Notes: Modified to select the orders will be modified
# 08/25/2008 the headers for excel were modified and the format to print in file
# 08/26/2008 the headers for excel were modified to take old/new format	

# Last Modified on: 10/06/08  13:33:13
# Last Modified by: Roberto Barcenas
# Last Modified Desc: Added Model Data For Export General Report
# Last Modified on: 10/07/08 13:16:57
# Last Modified by: MCC C. Gabriel Varela S: Se toma en cuenta partial shipment
# Last Modified on: 10/08/08 11:35:38
# Last Modified by: MCC C. Gabriel Varela S: Se pone partial shipment cuando exista dropship

# Last Modified on: 10/24/08  11:34:32
# Last Modified by: Roberto Barcenas
# Last Modified Desc: Model Data for Fedex Report
# Last Modified on: 02/09/09 17:07:08
# Last Modified by: MCC C. Gabriel Varela S: Se arregla que en la consulta por defecto no se cuenten servicios dentro de la condición 1= (select count ....
## Last Modification by JRG : 03/12/2009 : Se agrega log
# Last Modified on: 05/15/09 17:42:54
# Last Modified by: MCC C. Gabriel Varela S: Se modifica para mostrar la parte en caso de que corresponda.
# Last Modified on: 05/18/09 11:38:50
# Last Modified by: MCC C. Gabriel Varela S: Se modifica para mostrar las partes sin quitar el producto.
# Last Modified on: 07/15/09 16:51:10
# Last Modified by: MCC C. Gabriel Varela S: Se hace que se pueda mostrar el inventario de las partes cuando corresponda.
# Last Modified by RB on 03/31/2011 05:40:21 PM  : Se agrega validacion para ordenes Allnatpro 

	
	## Fulfillment Type
	if ($in{'dropship'}){
		$va{'fftype'} = 'Dropship';
		$prdstatus = 'In Dropshipment';
	}else{
		$va{'fftype'} = 'Fullfill';
		$prdstatus = 'In Fulfillment';
	}
	
	my $ordstatus;
	if($in{'partialshipment'}) {
		$ordstatus="'Shipped'";
	}else{
		$ordstatus="'Processed'";
	}
	
	if ($in{'print'} and $in{'page'} eq 'tooutofstock'){
		my ($sth) = &Do_SQL("SELECT COUNT(DISTINCT(sl_orders.ID_orders)) FROM sl_orders,sl_orders_products WHERE sl_orders.ID_orders=sl_orders_products.ID_orders AND Ptype !='COD' AND sl_orders_products.Status='Active' AND IF(LENGTH(Related_ID_products) = 9, Related_ID_products, sl_orders_products.ID_products)='$in{'id_products'}' AND sl_orders.Status=$ordstatus AND StatusPrd='$prdstatus' AND sl_orders_products.ID_products NOT LIKE '6%'");
		if ($sth->fetchrow>0){
			my ($sth) = &Do_SQL("SELECT sl_orders.ID_orders FROM sl_orders,sl_orders_products WHERE sl_orders.ID_orders=sl_orders_products.ID_orders AND Ptype !='COD' AND sl_orders_products.Status='Active' AND IF(LENGTH(Related_ID_products) = 9, Related_ID_products, sl_orders_products.ID_products)='$in{'id_products'}' AND sl_orders.Status=$ordstatus AND StatusPrd='$prdstatus' AND sl_orders_products.ID_products NOT LIKE '6%'");
			while ($rec = $sth->fetchrow){
				my ($sth2)	= &Do_SQL("UPDATE sl_orders SET StatusPrd='Out of Stock' WHERE ID_orders='$rec'");
				&auth_logging('orders_updated',$rec);
			}
			$va{'message'} = &trans_txt('done');
		}else{
			$va{'message'} = &trans_txt('noprint');
		}
		print "Content-type: text/html\n\n";
		print &build_page('toprint_msg.html');
		return;
	}elsif($in{'print'} and $in{'page'} eq 'todssent'){
		my ($sth) = &Do_SQL("SELECT COUNT(DISTINCT(sl_orders.ID_orders)) FROM sl_orders,sl_orders_products WHERE sl_orders.ID_orders=sl_orders_products.ID_orders AND Ptype !='COD' AND sl_orders_products.Status='Active' AND IF(LENGTH(Related_ID_products) = 9, Related_ID_products, sl_orders_products.ID_products)='$in{'id_products'}' AND sl_orders.Status=$ordstatus AND StatusPrd='$prdstatus' AND sl_orders_products.ID_products NOT LIKE '6%'");
		if ($sth->fetchrow>0){
			my ($sth) = &Do_SQL("SELECT sl_orders.ID_orders FROM sl_orders,sl_orders_products WHERE sl_orders.ID_orders=sl_orders_products.ID_orders AND Ptype !='COD' AND sl_orders_products.Status='Active' AND IF(LENGTH(Related_ID_products) = 9, Related_ID_products, sl_orders_products.ID_products)='$in{'id_products'}' AND sl_orders.Status=$ordstatus AND StatusPrd='$prdstatus' AND sl_orders_products.ID_products NOT LIKE '6%'");
			while ($rec = $sth->fetchrow){
				my ($sth2)	= &Do_SQL("UPDATE sl_orders SET StatusPrd='Dropship Sent' WHERE ID_orders='$rec'");
				&auth_logging('orders_updated',$rec);
			}
			$va{'message'} = &trans_txt('done');
		}else{
			$va{'message'} = &trans_txt('noprint');
		}
		print "Content-type: text/html\n\n";
		print &build_page('toprint_msg.html');
		return;
	}elsif($in{'print'} and ($in{'page'} eq 'exports_general' or $in{'page'} eq 'exports_fedex')){	#new format
		my ($sth) = &Do_SQL("SELECT COUNT(DISTINCT(sl_orders.ID_orders)) FROM sl_orders,sl_orders_products WHERE sl_orders.ID_orders=sl_orders_products.ID_orders AND Ptype !='COD' AND sl_orders_products.Status='Active' AND IF(LENGTH(Related_ID_products) = 9, Related_ID_products, sl_orders_products.ID_products)='$in{'id_products'}' AND sl_orders.Status=$ordstatus AND StatusPrd='$prdstatus' AND sl_orders_products.ID_products NOT LIKE '6%'");
		if ($sth->fetchrow>0){	
			my (%lines);	
			print "Content-type: application/vnd.ms-excel\n";
			print "Content-disposition: attachment; filename=shoplatinotv_".&format_sltvid($in{'id_products'})."_".&get_date().".csv\n\n";
			if($in{'page'} eq 'exports_general'){
				print " Order , ID , Model , Ship Date , First Name , Last Name , Contact Number1 , Contact Number2 , Zip code , City , State , Street , Tracking Information , Comment ";
			}elsif($in{'page'} eq 'exports_fedex'){
				print " Order , ID , Model , Ship Date , Name, Contact Number1 , Contact Number2 , Zip code , City , State , Street , Tracking Information , Comment ";
			}
			print "\r\n";

			my ($sth) = &Do_SQL("SELECT * FROM sl_orders,sl_orders_products WHERE sl_orders.ID_orders=sl_orders_products.ID_orders AND Ptype !='COD' AND sl_orders.Status=$ordstatus AND StatusPrd='$prdstatus' AND IF(LENGTH(Related_ID_products) = 9, Related_ID_products, sl_orders_products.ID_products)='$in{'id_products'}' ORDER BY sl_orders.ID_orders");
			while ($rec = $sth->fetchrow_hashref()){
				my (@cols);
				$cols[0] = $rec->{'ID_orders'};
				$cols[1] = &format_sltvid($rec->{'ID_products'});
				$cols[2] = &load_name('sl_products','ID_products',substr($rec->{'ID_products'},3),'Model');
				$cols[3] = $rec->{'ShpDate'};
				my ($sth2) = &Do_SQL("SELECT * FROM sl_customers WHERE ID_customers='$rec->{'ID_customers'}';");
				my ($tmp) = $sth2->fetchrow_hashref();
				if($in{'page'} eq 'exports_general'){
					$cols[4] = $tmp->{'FirstName'};
					$cols[5] = $tmp->{'LastName1'};
					$cols[6] = $tmp->{'Phone1'};
					$cols[7] = $tmp->{'Phone2'};
					$cols[8] = $rec->{'shp_Zip'};
					$cols[9] = $rec->{'shp_City'};
					$cols[10] = substr($rec->{'shp_State'},0,2);
					$cols[11] = $rec->{'shp_Address1'} . ' ' . $rec->{'shp_Address2'} . ' ' . $rec->{'shp_Address3'};
					$cols[12] = $rec->{'Tracking'} . ' ' . $rec->{'ShpProvider'};
					$cols[13] = $rec->{'shp_Notes'};
					$lines{"$cols[5],$cols[4]"} = '"'.join('","', @cols)."\"\r\n";
				}else{
					$cols[4] = "$tmp->{'LastName1'} $tmp->{'FirstName'}";
					$cols[5] = $tmp->{'Phone1'};
					$cols[6] = $tmp->{'Phone2'};
					$cols[7] = $rec->{'shp_Zip'};
					$cols[8] = $rec->{'shp_City'};
					$cols[9] = substr($rec->{'shp_State'},0,2);
					$cols[10] = $rec->{'shp_Address1'} . ' ' . $rec->{'shp_Address2'} . ' ' . $rec->{'shp_Address3'};
					$cols[11] = $rec->{'Tracking'} . ' ' . $rec->{'ShpProvider'};
					$cols[12] = $rec->{'shp_Notes'};
					$lines{"$cols[4]"} = '"'.join('","', @cols)."\"\r\n";
				}
			}
		
			if ($in{'sort'}){
				foreach my $key (sort { lc($a) cmp lc($b) } keys %lines){
					print $lines{$key};
				}
			}else{
				foreach my $key (keys %lines){
					print $lines{$key};
				}
			}
		}else{
			$va{'message'} = &trans_txt('noprint');
			print "Content-type: text/html\n\n";
			print &build_page('toprint_msg.html');
			return;
		}
		return;
	}elsif($in{'print'} and $in{'page'} eq 'exports_inova'){	#old_format
		my ($sth) = &Do_SQL("SELECT COUNT(DISTINCT(sl_orders.ID_orders)) FROM sl_orders,sl_orders_products WHERE sl_orders.ID_orders=sl_orders_products.ID_orders AND Ptype !='COD' AND sl_orders_products.Status='Active' AND IF(LENGTH(Related_ID_products) = 9, Related_ID_products, sl_orders_products.ID_products)='$in{'id_products'}' AND sl_orders.Status=$ordstatus AND StatusPrd='$prdstatus'");
		if ($sth->fetchrow>0){	
			my (%lines);	
			my (@xcols) = ('REMESA','TPAGO','ORDVTA','CANT1','CLAV1','PROD1','PREC1','CANT2','CLAV2','PROD2','PREC2','CANT3','CLAV3','PROD3','PREC3','CANT4','CLAV4','PROD4','PREC4','CANT5','CLAV5','PROD5','PREC5','CANT6','CLAV6','PROD6','PREC6','MTOTAL','NOMBRE','APATERNO','AMATERNO','TELCASA','TELOFICINA','CP','COLONIA','CIUDAD','ESTADO','CALLE','ENTRECALLES','INDICACIONES','OBSERVACIONES');
			print "Content-type: application/vnd.ms-excel\n";
			print "Content-disposition: attachment; filename=shoplatinotv_".&format_sltvid($in{'id_products'})."_".&get_date().".csv\n\n";
			print '"'.join('","', @xcols)."\"\n";
			my ($sth) = &Do_SQL("SELECT * FROM sl_orders,sl_orders_products WHERE sl_orders.ID_orders=sl_orders_products.ID_orders AND Ptype !='COD' AND sl_orders.Status=$ordstatus AND StatusPrd='$prdstatus' AND IF(LENGTH(Related_ID_products) = 9, Related_ID_products, sl_orders_products.ID_products)='$in{'id_products'}' ORDER BY sl_orders.ID_orders");
			while ($rec = $sth->fetchrow_hashref()){
				my (@cols);
				##$cols[2] = "$rec->{'ID_orders'}-$rec->{'ID_orders_products'}";
				$cols[2] = "$rec->{'ID_orders'}";
				my ($sth2) = &Do_SQL("SELECT * FROM sl_customers WHERE ID_customers='$rec->{'ID_customers'}';");
				my ($tmp) = $sth2->fetchrow_hashref();
				$cols[28] = $tmp->{'FirstName'};
				$cols[29] = $tmp->{'LastName1'};
				$cols[30] = $tmp->{'LastName2'};
				$cols[31] = $tmp->{'Phone1'};
				$cols[32] = $tmp->{'Phone2'};
				
				$cols[33] = $rec->{'shp_Zip'};
				$cols[35] = $rec->{'shp_City'};
				$cols[36] = substr($rec->{'shp_State'},0,2);
				$cols[37] = $rec->{'shp_Address1'} . ' ' . $rec->{'shp_Address2'} . ' ' . $rec->{'shp_Address3'};
				$cols[39] = $rec->{'shp_Notes'};
				$lines{"$cols[3],$cols[2]"} = '"'.join('","', @cols)."\"\n";
			}
			if ($in{'sort'}){
				foreach my $key (sort { lc($a) cmp lc($b) } keys %lines){
					print $lines{$key};
				}
			}else{
				foreach my $key (keys %lines){
					print $lines{$key};
				}
			}
		}else{
			$va{'message'} = &trans_txt('noprint');
			print "Content-type: text/html\n\n";
			print &build_page('toprint_msg.html');
			return;
		}
		return;
	}elsif($in{'print'} and $in{'page'}){
		my ($sth) = &Do_SQL("SELECT COUNT(DISTINCT(sl_orders.ID_orders)) FROM sl_orders,sl_orders_products WHERE sl_orders.ID_orders=sl_orders_products.ID_orders AND Ptype !='COD' AND sl_orders_products.Status='Active' AND IF(LENGTH(Related_ID_products) = 9, Related_ID_products, sl_orders_products.ID_products)='$in{'id_products'}' AND sl_orders.Status=$ordstatus AND StatusPrd='$prdstatus'");
		if ($sth->fetchrow>0){
			print "Content-type: text/html\n\n";
			print &build_page('header_print.html');
			### Print Manifest
			if ($in{'page'} eq 'invoiceblank'){
				$cmd = 'invoices';
			}else{
				$cmd = 'pinvoices';
			}				
			my ($num);
			$in{'db'} = 'sl_orders';
			$in{'toprint'}=1;		
			my ($sth) = &Do_SQL("SELECT sl_orders.ID_orders FROM sl_orders,sl_orders_products WHERE sl_orders.ID_orders=sl_orders_products.ID_orders AND Ptype !='COD' AND sl_orders.Status=$ordstatus AND StatusPrd='$prdstatus' AND IF(LENGTH(Related_ID_products) = 9, Related_ID_products, sl_orders_products.ID_products)='$in{'id_products'}' ORDER BY sl_orders.ID_orders");
			while ($in{'id_orders'} = $sth->fetchrow){
				if ($num>0){
					print "<DIV STYLE='page-break-before:always'>&nbsp;</DIV>";
				}					
				&load_cfg('sl_orders');
				$in{'toprint'}  = $in{'id_orders'};
				my (%rec) = &get_record($db_cols[0],$in{'id_orders'},$in{'db'});
				if ($rec{lc($db_cols[0])}){
					foreach my $key (sort keys %rec) {
						$in{lc($key)} = $rec{$key};
						($db_valid_types{lc($key)} ne 'html') and ($in{lc($key)} =~ s/\n/<br>/g);
					}
					$in{'shpdate'} = $shpdate;
					## User Info
					&get_db_extrainfo('admin_users',$in{'id_admin_users'});
					
					## Regular or Allnatpro Invoice?
					my $customer_type=&load_name('sl_customers','ID_customers',$in{'id_customers'},'Type');
					my $xcmd = $customer_type eq 'Allnatpro' ? '_allnatpro' : '';
					
					my ($func) = 'view_' . $cmd . $xcmd;
					if (defined &$func){
						&$func;
					}
					
					print &build_page($cmd . $xcmd .'_print.html');
					
				}
				++$num;				
			}
			return;
		}else{
			$va{'message'} = &trans_txt('noprint');
			print "Content-type: text/html\n\n";
			print &build_page('toprint_msg.html');
			return;
		}
	
	}elsif($in{'id_products'} and $in{'remove'}){
		my ($sth) = &Do_SQL("SELECT sl_orders.ID_orders FROM sl_orders,sl_orders_products WHERE sl_orders.ID_orders=sl_orders_products.ID_orders AND Ptype !='COD' AND sl_orders_products.Status='Active' AND IF(LENGTH(Related_ID_products) = 9, Related_ID_products, sl_orders_products.ID_products)='$in{'id_products'}' AND sl_orders.Status=$ordstatus AND StatusPrd='$prdstatus'");
		while ($rec = $sth->fetchrow){
			my ($sth2)	= &Do_SQL("UPDATE sl_orders SET StatusPrd='None' WHERE ID_orders='$rec'");
			&auth_logging('orders_updated',$rec);
		}
		$va{'message'} = &trans_txt('done');
		print "Content-type: text/html\n\n";
		print &build_page('toprint_msg.html');
		return;
	}elsif($in{'remove'} eq 'all'){
		my ($sth)	= &Do_SQL("UPDATE sl_orders SET StatusPrd='None' WHERE Ptype != 'COD' AND sl_orders.Status=$ordstatus AND StatusPrd='$prdstatus'");
		&auth_logging('orders_updated',"");
		$va{'message'} = &trans_txt('done');
		print "Content-type: text/html\n\n";
		print &build_page('toprint_msg.html');
		return;	
	}elsif($in{'remove'} eq 'selected'){
		if($in{'ordersselected'} && $in{'ordersselected'} !~ m/,,.*/){
			chop($in{'ordersselected'});
			my ($sth)	= &Do_SQL("UPDATE sl_orders SET StatusPrd='None' WHERE Ptype != 'COD' AND sl_orders.Status=$ordstatus AND StatusPrd='$prdstatus' AND sl_orders.ID_orders IN($in{'ordersselected'})");
			&auth_logging('orders_updated',"");
			$va{'message'} = &trans_txt('done');
			print "Content-type: text/html\n\n";
			print &build_page('toprint_msg.html');
			return;			
		}
	}elsif($in{'id_products'}){
		$sth = &Do_SQL("SELECT COUNT(DISTINCT(sl_orders.ID_orders)) FROM sl_orders,sl_orders_products 
						WHERE sl_orders.ID_orders=sl_orders_products.ID_orders AND Ptype !='COD' 
						AND sl_orders_products.Status='Active' 
						AND IF(LENGTH(Related_ID_products) = 9, Related_ID_products, sl_orders_products.ID_products)='$in{'id_products'}' 
						AND sl_orders.Status=$ordstatus AND StatusPrd='$prdstatus'");
		$va{'orders'} = $sth->fetchrow;

		my ($sth) = substr($in{'id_products'},0,1) == 4 ? &Do_SQL("SELECT Name, Model FROM sl_parts WHERE ID_parts = '".substr($in{'id_products'},-4)."'") : &Do_SQL("SELECT Name, Model FROM sl_products WHERE ID_products='".substr($in{'id_products'},-6)."'");
		my($rec) = $sth->fetchrow_hashref;
		$va{'id_products'} = &format_sltvid($in{'id_products'});
		$va{'name'} = $rec->{'Name'};
		$va{'model'} = $rec->{'Model'};
		$va{'choices'} = &load_choices($in{'id_products'});
		
		print "Content-type: text/html\n\n";
		print &build_page('packing_toff_iteminfo.html');	
		return;
	}
	
	$va{'matches'} = 1;
	$va{'pageslist'} = 1;
	my ($sth);

	$sth = &Do_SQL("SELECT sl_orders_products.ID_products,IF(LENGTH(Related_ID_products) = 9, Related_ID_products,'') AS ID2,Isset,temp.ID_parts, if(NOT ISNULL(temp.ID_parts),temp.ID_parts,sl_orders_products.ID_products)as ID_products_p
					FROM sl_orders INNER JOIN sl_orders_products USING(ID_orders)
					INNER JOIN sl_skus on (IF(LENGTH(Related_ID_products) = 9, Related_ID_products, sl_orders_products.ID_products)=ID_sku_products)
					LEFT JOIN (Select ID_sku_products,group_concat(concat(Qty,'|',ID_parts))as ID_parts from sl_skus_parts GROUP BY ID_sku_products)as temp USING(ID_sku_products)
					LEFT JOIN  sl_warehouses_batches_orders
						ON sl_warehouses_batches_orders.ID_orders_products = sl_orders_products.ID_orders_products 
						AND sl_warehouses_batches_orders.Status IN ('In Fulfillment','Shipped','In Transit')  
					WHERE sl_warehouses_batches_orders.ID_orders_products IS NULL
					and Ptype != 'COD' 
					AND sl_orders_products.Status='Active' 
					AND sl_orders_products.ID_products>1000000 
					AND sl_orders.Status=$ordstatus 
					AND StatusPrd='$prdstatus' 
					AND sl_orders_products.ID_products NOT LIKE '6%' 
					GROUP BY IF(LENGTH(Related_ID_products) = 9, Related_ID_products, sl_orders_products.ID_products);");
	$va{'matches'} = $sth->rows;
	
	if ($va{'matches'}>0){

		(!$in{'nh'}) and ($in{'nh'}=1);
		$first = ($in{'nh'} - 1) * $usr{'pref_maxh'};			
		($va{'pageslist'},$qs) = &pages_list($in{'nh'},"/cgi-bin/mod/$usr{'application'}/admin",$va{'matches'},$usr{'pref_maxh'});
		my (@c) = split(/,/,$cfg{'srcolors'});

		$sth = &Do_SQL("SELECT COUNT(DISTINCT(sl_orders.ID_orders)) AS Total,sl_orders_products.ID_products,IF(LENGTH(Related_ID_products) = 9, Related_ID_products,'') AS ID2, Isset,temp.ID_parts, if(NOT ISNULL(temp.ID_parts),temp.ID_parts,sl_orders_products.ID_products)as ID_products_p
						FROM sl_orders INNER JOIN sl_orders_products USING(ID_orders)
						INNER JOIN sl_skus on (IF(LENGTH(Related_ID_products) = 9, Related_ID_products, sl_orders_products.ID_products)=ID_sku_products)
						LEFT JOIN (Select ID_sku_products,group_concat(concat(Qty,'|',ID_parts))as ID_parts from sl_skus_parts GROUP BY ID_sku_products)as temp USING(ID_sku_products)
						LEFT JOIN  sl_warehouses_batches_orders
							ON sl_warehouses_batches_orders.ID_orders_products = sl_orders_products.ID_orders_products 
							AND sl_warehouses_batches_orders.Status IN ('In Fulfillment','Shipped','In Transit')  
						WHERE sl_warehouses_batches_orders.ID_orders_products IS NULL
						AND Ptype != 'COD' 
						AND sl_orders_products.Status='Active' 
						AND sl_orders_products.ID_products>1000000 
						AND sl_orders.Status=$ordstatus 
						AND StatusPrd='$prdstatus' 
						AND sl_orders_products.ID_products NOT LIKE '6%' 
						GROUP BY IF(LENGTH(Related_ID_products) = 9, Related_ID_products, sl_orders_products.ID_products) 
						ORDER BY SUM(Quantity) 
						DESC LIMIT $first,$usr{'pref_maxh'}");

		while ($rec = $sth->fetchrow_hashref){
			$d = 1 - $d;
			$cadparts="";

			my $pname = $rec->{'ID2'} ? &load_db_names('sl_parts','ID_parts',substr($rec->{'ID2'},-4),'[Name]<br>[Model]') : &load_db_names('sl_products','ID_products',substr($rec->{'ID_products'},-6),'[Name]<br>[Model]');
			my $id = $rec->{'ID2'} ? $rec->{'ID2'}: $rec->{'ID_products'};
			my $choices = &load_choices($id);

			if($rec->{'ID_parts'} ne ''){
				#$cadparts.= "<table border='0' cellspacing='0' cellpadding='4' width='100%' class='formtable'>\n";
				@partsin=split(/,/,$rec->{'ID_parts'});
				for(0..$#partsin){
					@qtyid=split(/\|/,$partsin[$_]);
					$cadparts.= "<tr bgcolor='$c[$d]'>\n";
					$cadparts.= "	<td class='smalltext' valign='top' align='center'></td>\n
												<td class='smalltext' valign='top' align='center'>".$rec->{'Total'}*$qtyid[0]."</td>\n
										    <td class='smalltext' valign='top'>".&format_sltvid(400000000+$qtyid[1]). "<br>".&load_db_names('sl_parts','ID_parts',$qtyid[1],'[Name]')."</td>\n
										    <td class='smalltext' valign='top'>".&calc_parts_inventory(400000000+$qtyid[1])." Units</td>\n
										  </tr>\n";
				}
				#$cadparts.= "</table>\n";
			}

			$va{'searchresults'} .= "<tr bgcolor='$c[$d]' >\n";
			$va{'searchresults'} .= "  <td class='smalltext' valign='top' align='center'>
										<input class='checkbox' type='checkbox' name='rem_$id' value='$rec->{'Total'}'>\n
										<input type='button' name='btnid_$rec->{'ID_products'}' value='S' onClick=\"trjump('/cgi-bin/mod/wms/admin?cmd=packing_toff_items&dropship=$in{'dropship'}&id_products=$id&partialshipment=[in_partialshipment]')\">\n
										</td>\n";
			$va{'searchresults'} .= "  <td class='smalltext' valign='top' align='center'>$rec->{'Total'}</td>";
			$va{'searchresults'} .= "  <td class='smalltext' valign='top'>".&format_sltvid($id)."</td>\n";
			$va{'searchresults'} .= "  <td class='smalltext' valign='top'>".$pname." $choices</td>\n";
			$va{'searchresults'} .= "  <td class='smalltext' valign='top'>".&inventory_by_id($id)."</td>\n";
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
	print &build_page('packing_toff_items.html');
}

sub packing_toff_zones {
# --------------------------------------------------------	
# Created on: Carlos Haas
# Last Modified on: 7/30/2013 12:13:41 PM
# Author: Unknown
# Description : 
# Parameters :
	$in{'id_zones'}=int($in{'id_zones'});

	if ($in{'id_zones'}>0){
		&packing_toff_zones_to_batch;
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
						AND Ptype != 'COD'
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
								AND Ptype != 'COD'
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
			my $ed = $rec->{'Express_Delivery'}	? qq|<img src="/sitimages/delivery_2_on.jpg" title="Express Delivery">| : '';

			$va{'searchresults'} .= "<tr bgcolor='$c[$d]' onmouseover='m_over(this)' onmouseout='m_out(this)'>\n";
			$va{'searchresults'} .= "  <td class='smalltext' valign='top' align='center'><a href='#' onClick=\"trjump('/cgi-bin/mod/wms/admin?cmd=packing_toff_zones&id_zones=$rec->{'ID_zones'}')\"><img src='[va_imgurl]/[ur_pref_style]/icsearchsmall.gif' title='Next' alt='' border='0'></a></td>\n";
			$va{'searchresults'} .= "  <td class='smalltext' valign='top' align='center'><a href='#' onClick=\"trjump('/cgi-bin/mod/wms/dbman?cmd=opr_zones&view=$rec->{'ID_zones'}')\">$rec->{'ID_zones'}</a></td>\n";
			$va{'searchresults'} .= "  <td class='smalltext' valign='top'><a href='#' onClick=\"trjump('/cgi-bin/mod/wms/admin?cmd=packing_toff_zones&id_zones=$rec->{'ID_zones'}')\">$rec->{'Name'} &nbsp; $ed</a></td>\n";
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
	print &build_page('packing_toff_zones.html');
}

sub packing_toff_zones_to_batch {
# --------------------------------------------------------

	if ($in{'action'}){

		if ($in{'id_warehouses'} and $in{'id_orders'}){

			#my ($sth) = &Do_SQL("SELECT ID_warehouses_batches FROM sl_warehouses_batches WHERE ID_warehouses=$in{'id_warehouses'} AND Status IN ('New','Assigned')");
			#my ($id_batch) = $sth->fetchrow;
			#if (!$id_batch){
			#	my ($sth) = &Do_SQL("INSERT INTO sl_warehouses_batches SET ID_warehouses=$in{'id_warehouses'}, Status='Assigned', Date = CURDATE(), Time = CURTIME(), ID_admin_users = '$usr{'id_admin_users'}';");
			#	$id_batch = $sth->{'mysql_insertid'};
			#}else{
			#	my ($sth) = &Do_SQL("UPDATE sl_warehouses_batches SET Status='Assigned' WHERE ID_warehouses=$in{'id_warehouses'} AND Status = 'New'");
			#}

			delete($va{'message'}); delete($va{'message_zip_excluded'});
			my ($id_batch) = &create_warehouse_batch_file($in{'id_warehouses'});
			my ($sth) = &Do_SQL("UPDATE sl_warehouses_batches SET Status='Assigned' WHERE ID_warehouses=$in{'id_warehouses'} AND Status = 'New'");

			$in{'id_orders'} =~ s/\|/,/g;
			
			## Excluded Zips
			my ($excluded_zips, $mod_excluded_zip, $orders_excluded);
			my ($sth) = &Do_SQL("SELECT ZipCode FROM sl_warehouses_zipcodes_excludes WHERE ID_warehouses = '$in{'id_warehouses'}' AND Status='Active';");
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
								FROM sl_orders 
								INNER JOIN sl_orders_products USING(ID_orders )
								LEFT JOIN sl_products on(sl_products.ID_products=RIGHT(sl_orders_products.ID_products,6)) 
								LEFT JOIN sl_warehouses_batches_orders
									ON sl_warehouses_batches_orders.ID_orders_products = sl_orders_products.ID_orders_products 
									AND sl_warehouses_batches_orders.Status IN ('In Fulfillment','Shipped','In Transit')  
								WHERE sl_warehouses_batches_orders.ID_orders_products IS NULL
								AND Ptype != 'COD'
								AND sl_orders_products.ID_products BETWEEN 100000000 AND 399999999
								AND sl_orders.Status IN ('Processed','Shipped')
								AND StatusPrd='In Fulfillment' 
								AND sl_orders_products.Status IN ('Active','Exchange','Undeliverable','ReShip') 
								AND sl_orders_products.SalePrice >= 0
								$mod_excluded_zip 
								AND sl_orders.ID_orders IN ($in{'id_orders'})
								AND ID_zones='$in{'id_zones'}';");
			
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
			$va{'message'} = &trans_txt('tobatch_err');
		}
	}

	$va{'zonename'} = &load_name('sl_zones','ID_zones',$in{'id_zones'},'Name');
	
	my ($sth) = &Do_SQL("SELECT COUNT(*) FROM sl_zones_warehouses INNER JOIN sl_warehouses ON sl_zones_warehouses.ID_warehouses=sl_warehouses.ID_warehouses AND sl_warehouses.Status='Active' WHERE ID_zones='$in{'id_zones'}';");
	if ($sth->fetchrow>0){
		my (@c) = split(/,/,$cfg{'srcolors'});
		#############################
		### List of Warehouse
		#############################
		my ($sth) = &Do_SQL("SELECT * FROM sl_zones_warehouses INNER JOIN sl_warehouses ON sl_zones_warehouses.ID_warehouses=sl_warehouses.ID_warehouses AND sl_warehouses.Status='Active' WHERE ID_zones='$in{'id_zones'}';");
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
								   sl_warehouses_batches.ID_warehouses = '". $rec->{'ID_warehouses'} ."'
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
		my ($modquery, $modquery2, $condition_amazon);
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

		$condition_amazon = ($cfg{'amazon_vendor'}) ? " AND (sl_orders_products.Amazon_ID_products='' OR sl_orders_products.Amazon_ID_products IS NULL) " : "";

		my ($sth) = &Do_SQL("SELECT 
								sl_orders.ID_orders
								, sl_orders.Date
								, SUM( ( (SalePrice - sl_orders_products.Discount) * Quantity ) + Shipping + ShpTax + Tax ) AS TotProd
								, SUM(Quantity) AS TotItems
								, ID_customers
								, IF(shp_type = 2,1,0) AS Express_Delivery
								, shp_Zip,shp_City
								, shp_Urbanization
							FROM sl_orders 
							INNER JOIN sl_orders_products USING(ID_orders)
							LEFT JOIN sl_products on(sl_products.ID_products=RIGHT(sl_orders_products.ID_products,6)) 
							LEFT JOIN sl_warehouses_batches_orders
								ON sl_warehouses_batches_orders.ID_orders_products = sl_orders_products.ID_orders_products 
								AND sl_warehouses_batches_orders.Status IN ('In Fulfillment','Shipped','In Transit')  
							WHERE sl_warehouses_batches_orders.ID_orders_products IS NULL
							$modquery
							AND Ptype != 'COD'
							AND sl_orders_products.ID_products BETWEEN 100000000 AND 399999999
							AND sl_orders.Status IN ('Processed','Shipped')
							AND StatusPrd='In Fulfillment' 
							AND sl_orders_products.Status IN ('Active','Exchange','Undeliverable','ReShip') 
							AND sl_orders_products.SalePrice >= 0
							AND ID_zones = $in{'id_zones'}
							$condition_amazon
							GROUP BY sl_orders.ID_orders
							$modquery2 
							ORDER BY shp_Zip,shp_City,shp_Urbanization,sl_orders.ID_orders DESC");

		$va{'matches'} = $sth->rows;
		
		if ($va{'matches'}>0){

			while ($rec = $sth->fetchrow_hashref){

				$d = 1 - $d;
				$cont=0;
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
				$va{'ordsearchresults'} .= "  <td class='smalltext' valign='top'>$rec->{'shp_City'}<br>$rec->{'shp_Urbanization'}</td>\n";
				$va{'ordsearchresults'} .= "  <td class='smalltext' valign='top'>$rec->{'Date'}</td>\n";
				$va{'ordsearchresults'} .= "  <td class='smalltext' valign='top'>".&load_db_names('sl_customers','ID_customers',$rec->{'ID_customers'},"[company_name] [FirstName] [LastName1]")."</td>\n";
				$va{'ordsearchresults'} .= "  <td class='smalltext' valign='top'>$rec->{'TotItems'}</td>\n";
				$va{'ordsearchresults'} .= "  <td class='smalltext' valign='top' align='right'>".&format_price($rec->{'TotProd'})."</td>\n";
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
					$va{'ordsearchresults'} .= "  <td class='smalltext' valign='top' colspan='4'></td>\n";
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
				<td colspan='7' align="center">|.&trans_txt('search_nomatches').qq|</td>
			</tr>\n|;
		}
	}else{
		$va{'message'} = &trans_txt('nozones_err');
		$va{'matches'} = 0;
		$va{'pageslist'} = 1;
		$va{'searchresults'} = qq|
		<tr>
			<td colspan='6' align="center">|.&trans_txt('search_nomatches').qq|</td>
		</tr>\n|;
		$va{'ordsearchresults'} = qq|
			<tr>
				<td colspan='7' align="center">|.&trans_txt('search_nomatches').qq|</td>
			</tr>\n|;
	}

	print "Content-type: text/html\n\n";
	print &build_page('packing_toff_zonesbatch.html');
}

##################################################################
##########   SELECTING ORDERS
##################################################################

sub packing_addform {
# --------------------------------------------------------
	print "Content-type: text/html\n\n";
	print &build_page('packing_addform.html');
}

sub packing_fadd {
# --------------------------------------------------------
# Created on: unknown
# Last Modified on:07/07/2008 09:56:33 PM
# Last Modified by: MCC C Gabriel Varela S
# Author: unknown
# Description : Se modifica la forma de hacer las consultas SQL, estaba mal. Se cambia la forma de ver los multi-items, no se cuentan los servicios
# Parameters : 
# Last Modified on: 10/06/08 17:57:51
# Last Modified by: MCC C. Gabriel Varela S: Se agrega pestaña Partial Ship
# Last Modified on: 10/07/08 09:30:31
# Last Modified by: MCC C. Gabriel Varela S: Se excluyen los servicios para partial Ship, se toma en cuenta DropShip al llamar a las consultas de Partial Ship, y se toma en cuenta partial shipment para todas las consultas
# Last Modified on: 10/09/08 17:05:00
# Last Modified by: MCC C. Gabriel Varela S: Se incluye condición de Saleprice>=0
# Last Modified on: 02/09/09 17:07:08
# Last Modified by: MCC C. Gabriel Varela S: Se arregla que en la consulta por defecto no se cuenten servicios dentro de la condición 1= (select count ....
# Last Modified on: 04/28/09 17:52:07
# Last Modified by: MCC C. Gabriel Varela S: Se deshabilita partialshipped

	$va{'matches'} = 1;
	$va{'pageslist'} = 1;
	my ($sth,$dsquery,$page_limit,$psquery,$ordstatus,$basequery);
	
	$dsquery = ($in{'dropship'})? " 'Yes' " : " 'No' ";
	$ordstatus = ($in{'partialshipment'})? "'Shipped'" : "'Processed'";

	###
	### Base Query
	###
	$basequery = "SELECT
						COUNT(DISTINCT(sl_orders.ID_orders)) AS Total,
						GROUP_CONCAT(DISTINCT sl_orders.ID_orders),
						sl_orders_products.ID_products AS ID, 
						IF(LENGTH(Related_ID_products) = 9, Related_ID_products,'') AS ID2,
						sl_orders_products.ID_products,
						SUM(Quantity), 
						Isset, 
						temp.ID_parts, 
						IF(NOT ISNULL(temp.ID_parts), temp.ID_parts, sl_orders_products.ID_products)AS ID_products_p  
			      FROM 
			      sl_orders INNER JOIN sl_orders_products ON(sl_orders.ID_orders=sl_orders_products.ID_orders )
			      LEFT JOIN sl_products ON(sl_products.ID_products=RIGHT(sl_orders_products.ID_products,6)) 
			      LEFT JOIN sl_parts ON(sl_parts.ID_parts=RIGHT(sl_orders_products.ID_products,4)) 
			      LEFT JOIN sl_skus ON (sl_orders_products.ID_products=ID_sku_products)
				  LEFT JOIN ( 
					  	SELECT ID_sku_products,GROUP_CONCAT(CONCAT(Qty,'|',ID_parts))AS ID_parts 
					  	FROM sl_skus_parts 
					  	GROUP BY ID_sku_products
				  )temp ON (sl_skus.ID_sku_products=temp.ID_sku_products)
			      LEFT JOIN  
			      		sl_warehouses_batches_orders 
			      		ON sl_warehouses_batches_orders.ID_orders_products = sl_orders_products.ID_orders_products 
			      		AND sl_warehouses_batches_orders.Status IN ('In Fulfillment','Shipped','In Transit')
			      WHERE sl_warehouses_batches_orders.ID_orders_products IS NULL
				  AND IF(LENGTH(Related_ID_products) = 9 AND LEFT(Related_ID_products,1) < 6 AND RIGHT(sl_orders_products.ID_products,6) = '000000',1,sl_products.DropShipment =$dsquery) $psquery
			      AND (ISNULL(ShpDate) OR ShpDate='' OR ShpDate='0000-00-00')
			      AND Ptype !='COD' 
			      AND sl_orders.Status=$ordstatus 
			      AND sl_orders_products.Status='Active' 
			      AND sl_orders_products.ID_products > 1000000
			      AND LEFT(sl_orders_products.ID_products,1) < 6";


	## Top Bar
	if ($in{'mult'}){

		$sth = &Do_SQL("$basequery
					    AND (StatusPrd='None' OR StatusPrd='') 
					    AND sl_orders.shp_type<>2
					    AND 1<(SELECT COUNT(*) FROM sl_orders_products WHERE Status='Active' AND ID_orders=sl_orders.ID_orders AND sl_orders_products.ID_products NOT LIKE '6%')  
					    GROUP BY IF(LENGTH(Related_ID_products) = 9 AND RIGHT(sl_orders_products.ID_products,6) = '000000', Related_ID_products, sl_orders_products.ID_products)");

	}elsif($in{'xd'}){

		$sth = &Do_SQL("$basequery 
						AND (StatusPrd = 'None' OR StatusPrd = '') 
						AND sl_orders.shp_type = 2 
						GROUP BY IF(LENGTH(Related_ID_products) = 9 AND RIGHT(sl_orders_products.ID_products,6) = '000000', Related_ID_products, sl_orders_products.ID_products);");

	}elsif($in{'ostock'}){

		$sth = &Do_SQL("$basequery 
						AND StatusPrd='Out of Stock' 
						AND sl_orders.shp_type <> 2 
						GROUP BY IF(LENGTH(Related_ID_products) = 9 AND RIGHT(sl_orders_products.ID_products,6) = '000000', Related_ID_products, sl_orders_products.ID_products);");

	}else{
		$sth = &Do_SQL("$basequery
						AND (StatusPrd='None' OR StatusPrd='') 
						AND 1=(SELECT COUNT(*) FROM sl_orders_products WHERE Status='Active' AND ID_orders=sl_orders.ID_orders AND ID_products NOT LIKE '6%')  
						AND sl_orders.shp_type <> 2 
						GROUP BY IF(LENGTH(Related_ID_products) = 9 AND RIGHT(sl_orders_products.ID_products,6) = '000000', Related_ID_products, sl_orders_products.ID_products);");
	}

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

		$va{'report_header'}='<td class="menu_bar_title">Inventory</td>';		
		my (@c) = split(/,/,$cfg{'srcolors'});

		if ($in{'mult'}){

			$sth = &Do_SQL("$basequery
						    AND (StatusPrd='None' OR StatusPrd='') 
						    AND sl_orders.shp_type<>2
						    AND 1<(SELECT COUNT(*) FROM sl_orders_products WHERE Status='Active' AND ID_orders=sl_orders.ID_orders AND sl_orders_products.ID_products NOT LIKE '6%')  
						    GROUP BY IF(LENGTH(Related_ID_products) = 9 AND RIGHT(sl_orders_products.ID_products,6) = '000000', Related_ID_products, sl_orders_products.ID_products)
							ORDER BY COUNT(DISTINCT(sl_orders.ID_orders)) DESC ,SUM(Quantity) DESC
							$page_limit");

		}elsif($in{'xd'}){

			$sth = &Do_SQL("$basequery
							AND (StatusPrd = 'None' OR StatusPrd = '') 
							AND sl_orders.shp_type=2 
							GROUP BY IF(LENGTH(Related_ID_products) = 9 AND RIGHT(sl_orders_products.ID_products,6) = '000000', Related_ID_products, sl_orders_products.ID_products) 
							ORDER BY COUNT(DISTINCT(sl_orders.ID_orders)) DESC ,SUM(Quantity) DESC
							$page_limit");

		}elsif($in{'ostock'}){

			$sth = &Do_SQL("$basequery
							AND StatusPrd='Out of Stock' 
							AND sl_orders.shp_type<>2 
							GROUP BY IF(LENGTH(Related_ID_products) = 9 AND RIGHT(sl_orders_products.ID_products,6) = '000000', Related_ID_products, sl_orders_products.ID_products) 
							ORDER BY COUNT(DISTINCT(sl_orders.ID_orders)) DESC ,SUM(Quantity) DESC
							$page_limit");

		}else{

			$va{'report_header'}='<td class="menu_bar_title">Inventory</td>';
			$sth = &Do_SQL("$basequery
							AND (StatusPrd='None' OR StatusPrd='') 
							AND 1=(SELECT COUNT(*) FROM sl_orders_products WHERE Status='Active' AND ID_orders=sl_orders.ID_orders AND ID_products NOT LIKE '6%')  
							AND sl_orders.shp_type<>2 
							GROUP BY IF(LENGTH(Related_ID_products) = 9 AND RIGHT(sl_orders_products.ID_products,6) = '000000', Related_ID_products, sl_orders_products.ID_products)
							ORDER BY COUNT(DISTINCT(sl_orders.ID_orders)) DESC ,SUM(Quantity) DESC
							$page_limit");
		}

		## Cambios CH?
		while (my $rec = $sth->fetchrow_hashref){

			my $pname = $rec->{'ID2'} ? &load_db_names('sl_parts','ID_parts',substr($rec->{'ID2'},-4),'[Name]<br>[Model]') : &load_db_names('sl_products','ID_products',substr($rec->{'ID'},-6),'[Name]<br>[Model]');
			my $id = $rec->{'ID2'} ? $rec->{'ID2'}: $rec->{'ID'};
			my $this_id = $rec->{'ID2'} ? $rec->{'ID2'} : $rec->{'ID'};
			$d = 1 - $d;
			
			$cadparts="";
			if($rec->{'ID_parts'} ne ''){

				@partsin=split(/,/,$rec->{'ID_parts'});
				for(0..$#partsin){

					@qtyid=split(/\|/,$partsin[$_]);
					my $id_products = 400000000+$qtyid[1];

					my $this_link = ($all_inventory{$id_products}{'inventory'} > 0 and !$in{'print'}) ? 
						"<a class=\"scroll\" href=\"#ajax_inv$id\" onClick=\"popup_show('ajax_windows', 'ajax_drag', 'ajax_exit', 'screen-center', -1, -1,'ajax_inv$id');loadDoc('/cgi-bin/common/apps/ajaxbuild?ajaxbuild=inventory&id_products=".$id_products."&cols=ID,Warehouse,In Batch,Qty&extradata=".$id_warehouses.":".$nopack.":".$include_all."');\">
			  				<img id='idajax_inv".$id_products."' src='[va_imgurl]/[ur_pref_style]/b_view.png' title='More Info' alt='More Info' border='0'>
			  			</a>" : '';

					#my ($link_inv, $qty_inv, $qty_batch) = &inventory_by_id(400000000+$qtyid[1]);
					$cadparts.= "<tr bgcolor='$c[$d]'>\n";
					$cadparts.= "	<td class='smalltext' valign='top' align='center'></td>\n
											<td class='smalltext' valign='top' align='center'></td>\n
											<td class='smalltext' valign='top' align='center'>".$rec->{'Total'}*$qtyid[0]." x ".&format_sltvid(400000000+$qtyid[1]). "</td>\n
										    <td class='smalltext' valign='top'>".&load_db_names('sl_parts','ID_parts',$qtyid[1],'[Name]')."</td>\n
										    <td class='smalltext' valign='top'>".format_number($all_inventory{$id_products}{'inbatch'})."</td>\n
											<td class='smalltext' valign='top'>".format_number($all_inventory{$id_products}{'inventory'})."</td>\n
										    <td class='smalltext' valign='top'>".$this_link."</td>\n
										  </tr>\n";
				}
			}

			$va{'searchresults'} .= "<tr bgcolor='$c[$d]' >\n";
			$va{'searchresults'} .= "  <td class='smalltext' valign='top' align='center'>";
			
			if (!$in{'print'}){
				$va{'searchresults'} .= "
										<input class='checkbox' type='checkbox' name='pid_$this_id' value='$rec->{'Total'}'>\n
										<input type='button' name='btnid_$this_id' value='S' onClick=\"trjump('/cgi-bin/mod/wms/admin?cmd=packing_fadd_form&id_products=$this_id&mult=$in{'mult'}&xd=$in{'xd'}&ostock=$in{'ostock'}&dropship=$in{'dropship'}&partialshipped=$in{'partialshipped'}&partialshipment=$in{'partialshipment'}')\">\n";
			}

			$va{'searchresults'} .= "	</td>\n";
			$va{'searchresults'} .= "  <td class='smalltext' valign='top' align='center'>$rec->{'Total'}</td>";
			$va{'searchresults'} .= "  <td class='smalltext' valign='top'>".&format_sltvid($id)."</td>\n";
			$va{'searchresults'} .= "  <td class='smalltext' valign='top'>".$pname." $choices</td>\n";
			$va{'searchresults'} .= "  <td class='smalltext' valign='top' align='right' colspan='3'><span name='ajax_inv$id' id='ajax_inv$id'>&nbsp;</span></td>\n";
			$va{'searchresults'} .= "</tr>$cadparts\n";
			
		}

	}else{
		$va{'pageslist'} = 1;
		$va{'searchresults'} = qq|
		<tr>
			<td colspan='5' align="center">|.&trans_txt('search_nomatches').qq|</td>
		</tr>\n|;
	}

	($va{'sitems'},$va{'ditems'},$va{'xitems'},$va{'mitems'},$va{'pitems'},$va{'titems'},$va{'oitems'},$va{'paship'}) = ('on','off','off','off','off','off','off','off');
	if ($in{'mult'}){
		($va{'sitems'},$va{'ditems'},$va{'xitems'},$va{'mitems'},$va{'pitems'},$va{'titems'},$va{'oitems'},$va{'paship'}) = ('off','off','off','on','off','off','off','off');
	}elsif($in{'ds'}){	
		($va{'sitems'},$va{'ditems'},$va{'xitems'},$va{'mitems'},$va{'pitems'},$va{'titems'},$va{'oitems'},$va{'paship'}) = ('off','on','off','off','off','off','off','off');
	}elsif($in{'pend'}){
		($va{'sitems'},$va{'ditems'},$va{'xitems'},$va{'mitems'},$va{'pitems'},$va{'titems'},$va{'oitems'},$va{'paship'}) = ('off','off','off','off','on','off','off','off');
	}elsif($in{'intran'}){
		($va{'sitems'},$va{'ditems'},$va{'xitems'},$va{'mitems'},$va{'pitems'},$va{'titems'},$va{'oitems'},$va{'paship'}) = ('off','off','off','off','off','on','off','off');	
	}elsif($in{'ostock'}){
		($va{'sitems'},$va{'ditems'},$va{'xitems'},$va{'mitems'},$va{'pitems'},$va{'titems'},$va{'oitems'},$va{'paship'}) = ('off','off','off','off','off','off','on','off');
		$va{'sty_bo'} = qq|style="display:none"|;
	}elsif($in{'xd'}){
		($va{'sitems'},$va{'ditems'},$va{'xitems'},$va{'mitems'},$va{'pitems'},$va{'titems'},$va{'oitems'},$va{'paship'}) = ('off','off','on','off','off','off','off','off');
	}

	
	(!$in{'page'}) and ($in{'page'} = 'home');
	if ($in{'print'}){
		print "Content-type: text/html\n\n";
		print &build_page('header_print.html');
		print &build_page('packing_fadd_prt.html');
	}else{
		print "Content-type: text/html\n\n";
		print &build_page('packing_fadd.html');
	}
}


############################################################################################
############################################################################################
#	Function: packing_fadd_auto
#
#   		Set StatusPrd of order automatically based in inventory - In Fulfillment
#
#	Created by:
#		_Roberto Barcenas_
#
#	Modified By:
#
#   	Parameters:
#		- id_warehouses : Warehouse to look for inventory
#		- order : Oldest or Newest
#
#   	Returns:
#		- 
#
#   	See Also:
#   	
#   		/cgi-bin/common/apps/ajaxbuild.wms.cgi [For all functionality]
#
sub packing_fadd_auto {
############################################################################################
############################################################################################

	
	my $modsql_ptype;
	if($in{'cod'}){

		$va{'string_ptype'} = 'COD';
		$modsql_ptype = q| AND Ptype = 'COD' |;

	}else{

		$va{'string_ptype'} = 'Prepay';
		$modsql_ptype = q| AND Ptype <> 'COD' |;

	}

	##
	## In Fulfillment
	my ($sth) = Do_SQL("SELECT COUNT(DISTINCT sl_orders.ID_orders)
						FROM sl_orders INNER JOIN sl_orders_products USING(ID_orders)
						LEFT JOIN sl_warehouses_batches_orders
						ON sl_warehouses_batches_orders.ID_orders_products = sl_orders_products.ID_orders_products AND sl_warehouses_batches_orders.Status IN ('In Fulfillment','Shipped','In Transit')
						WHERE 1 AND sl_orders.Status = 'Processed' AND StatusPrd = 'In Fulfillment' AND sl_orders_products.Status = 'Active' AND sl_warehouses_batches_orders.ID_orders_products IS NULL 
						AND (ISNULL(ShpDate) OR ShpDate='0000-00-00') AND sl_orders_products.ID_products > 1000000 AND LEFT(sl_orders_products.ID_products,1) < 4 $modsql_ptype
						AND 1 > (SELECT COUNT(*) FROM sl_orders_products INNER JOIN sl_products ON sl_products.ID_products = RIGHT(sl_orders_products.ID_products,6)	
								WHERE sl_orders_products.ID_orders = sl_orders.ID_orders AND sl_products.DropShipment = 'Yes');"); 
	$va{'infulfillment_orders'} = $sth->fetchrow();
	$va{'infulfillment_image'} = $va{'infulfillment_orders'} ? qq|<img id="img-infulfillment_on" src="/sitimages/packing_list/infullfilment_on.png" title="Clean \| None" style="cursor:pointer">| : qq|<img id="img-infulfillment_off" src="/sitimages/packing_list/infullfilment_off.png" title="All Clean">|;

	##
	## Out of Stock
	my ($sth) = Do_SQL("SELECT COUNT(*) FROM sl_orders WHERE Status = 'Processed' AND StatusPrd = 'Out of Stock' $modsql_ptype;");
	$va{'ostock_orders'} = $sth->fetchrow();
	$va{'ostock_image'} = $va{'ostock_orders'} ? qq|<img id="img-ostock_on" src="/sitimages/packing_list/outofstock_on.png" title="Clean \| None" style="cursor:pointer">| : qq|<img id="img-ostock_off" src="/sitimages/packing_list/outofstock_off.png" title="All Clean">|;




	print "Content-type: text/html\n\n";
	print &build_page('packing_fadd_auto.html');


}


sub packing_orders {
# --------------------------------------------------------
	my ($pname);
	$in{'db'} = $sys{"db_opr_orders"};
	@headerfields = split(/,/, $sys{"db_opr_orders_list"});
	&load_cfg($in{'db'});
	$in{lc($db_cols[0])} =~ s/\D//g;  	#$in{lc($db_cols[0])} = int($in{lc($db_cols[0])});
	$va{'id_cmd_value'} = $in{lc($db_cols[0])};
	
	if ($in{lc($db_cols[0])}==0){
		delete($in{lc($db_cols[0])});
		$va{'id_cmd_value'} = int($in{'view'});
		if ($va{'id_cmd_value'}==0){
			$va{'id_cmd_value'} = int($in{'modify'});
			if ($va{'id_cmd_value'}==0){
				delete($va{'id_cmd_value'});
			}
		}
	}
	print "Content-type: text/html\n\n";
	
	if ($in{'action'} eq 'orders_toadd'){
		
		my $ids;
		$va{'message'} = &trans_txt('nomatches');

		foreach my $key (keys %in){
		
			if ($key =~ /(\d{3,})/ and $in{$key} eq 'create_pklist'){
				my $id_orders = int($1);
				my ($sth) = &Do_SQL("UPDATE sl_orders SET StatusPrd = 'In Fulfillment' WHERE ID_orders = '$id_orders'");
				&auth_logging('orders_updated',$id_orders);

				&add_order_notes_by_type($id_orders,"The order has been marked to Fulfill","Low");
				&auth_logging('orders_note_added',$id_orders);
				$ids++;
			}

		}

		if($ids) {
			$va{'message'} = &trans_txt('done');
		}
			
		print &build_page('toprint_msg.html');
		return;

	}


	if ($in{'action'}) {

		$in{'status'} = 'Processed';
		$in{'statusprd'} = 'None';
		
		my ($numhits, @hits) = &query($in{'db'});



		if ($numhits>0){
			($va{'pageslist'},$va{'qs'})  = &pages_list($in{'nh'},"$script_url",$numhits,$usr{'pref_maxh'});
			$va{'matches'} = $numhits;
			my ($rows) = ($#hits+1)/($#db_cols+1);
			my $rowsviewed=&GetCookies("$in{'db'}$in{'e'}");
			my (@c) = split(/,/,$cfg{'srcolors'});
			
			for (0 .. $rows-1) {

				$d = 1 - $d;
				%tmp = &array_to_hash($_, @hits);

				my ($sth) = &Do_SQL("SELECT sl_orders_products.*,sl_orders_products.Quantity AS pqty,
										IF(ID_warehouses_batches IS NOT NULL,ID_warehouses_batches, 0),
										IF(sl_warehouses_batches_orders.Status IS NOT NULL, sl_warehouses_batches_orders.Status, 'N/A') AS BatchStatus
										FROM sl_orders_products 
										LEFT JOIN  
			      						sl_warehouses_batches_orders 
			      						ON sl_warehouses_batches_orders.ID_orders_products = sl_orders_products.ID_orders_products 
			      						AND sl_warehouses_batches_orders.Status IN ('In Fulfillment','Shipped','In Transit')
			      						WHERE sl_warehouses_batches_orders.ID_orders_products IS NULL
										AND sl_orders_products.ID_orders = '$tmp{'ID_orders'}'
										AND sl_orders_products.Status = 'Active'
										AND LEFT(ID_products,1) = 1;");

				if($sth->rows > 0){

					$va{'searchresults'} .= "<tr bgcolor='$c[$d]'>\n";
					$va{'searchresults'} .= "  <td class='smalltext' valign='top' align='center'><input type='checkbox' name='$tmp{'ID_orders'}' value='create_pklist'></td>";
					$va{'searchresults'} .= "  <td class='smalltext' valign='top' align='center'>$tmp{'ID_orders'}</td>\n";
					$va{'searchresults'} .= "  <td class='smalltext' valign='top'></td>\n";
					$va{'searchresults'} .= "  <td class='smalltext' valign='top'>".&load_db_names('sl_customers','ID_customers',$tmp{'ID_customers'},'[FirstName] [LastName1] @ [company_name]')." $tmp{'Date'} / $tmp{'Status'}</td>\n";
					$va{'searchresults'} .= "  <td class='smalltext' valign='top'></td>\n";
					$va{'searchresults'} .= "</tr>\n";


					while ($rec = $sth->fetchrow_hashref){

						if (length($rec->{'Related_ID_products'}) == 9){

							$rec->{'ID_products'} = $rec->{'Related_ID_products'};
							$pname = &load_db_names('sl_parts','ID_parts',$rec->{'ID_products'}-400000000,'[Name]<br>[Model]')

						}elsif($rec->{'ID_products'} > 100000000 and $rec->{'ID_products'} < 400000000){

							$pname = &load_db_names('sl_products','ID_products',substr($rec->{'ID_products'},3,6),'[Name]<br>[Model]');

						}
						
						my($qty,$inv) = &load_inventory($rec->{'ID_products'});
						$va{'searchresults'} .= "<tr bgcolor='$c[$d]'>\n";
						$va{'searchresults'} .= "  <td class='smalltext' valign='top' align='center'>&nbsp; </td>";
						$va{'searchresults'} .= "  <td class='smalltext' valign='top'></td>\n";
						$va{'searchresults'} .= "  <td class='smalltext' valign='top'>$rec->{'pqty'} x ".&format_sltvid($rec->{'ID_products'}). "</td>\n";
						$va{'searchresults'} .= "  <td class='smalltext' valign='top'>$pname</td>\n";
						$va{'searchresults'} .= "  <td class='smalltext' valign='top'>".&inventory_by_id($rec->{'ID_products'})."</td>\n";
						$va{'searchresults'} .= "</tr>\n";
					}

				}else{

					$va{'searchresults'} .= "<tr bgcolor='$c[$d]'>\n";
					$va{'searchresults'} .= "  <td class='smalltext' valign='top' colspan='2' align='center'>$tmp{'ID_orders'}</td>\n";
					$va{'searchresults'} .= "  <td class='smalltext' valign='top' colspan='4' >Already Sent</td>\n";
					$va{'searchresults'} .= "</tr>\n";

				}
				
			}
			print &build_page('packing_orders_list.html');
		}else{
			$va{'message'} = &trans_txt('nomatches');
			print &build_page('packing_orders.html');
		}
	}else{
		print &build_page('packing_orders.html');
	}
}

sub packing_fadd_form {
# --------------------------------------------------------
# Last Modified on: 10/06/08 18:18:44
# Last Modified by: MCC C. Gabriel Varela S: Se agrega pestaña Partial Shipped
# Last Modified on: 10/07/08 13:31:13
# Last Modified by: MCC C. Gabriel Varela S: Se toma en cuenta partial shipment
# Last Modified on: 10/09/08 17:17:33
# Last Modified by: MCC C. Gabriel Varela S: Se pone la condición SalePrice>=0 y también se pone partialshipment en todos lados donde esté mult
# Last Modified on: 02/09/09 17:07:08
# Last Modified by: MCC C. Gabriel Varela S: Se arregla que en la consulta por defecto no se cuenten servicios dentro de la condición 1= (select count ....
# Last Modification by JRG : 06/12/2009 : Se agrega log
# Last Modified on: 04/28/09 17:58:30
# Last Modified by: MCC C. Gabriel Varela S: Se deshabilita partialshipped
	
	my ($prdstatus);

	## Fulfillment Type / Back Order
	if($in{'tobackorder'}){
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

	my $ordstatus;
	if($in{'partialshipment'}){
		$ordstatus="'Shipped'";
	}else{
		$ordstatus="'Processed'";
	}

	## Top Bar
	if ($in{'mult'}){			
		($va{'sitems'},$va{'ditems'},$va{'xitems'},$va{'mitems'},$va{'pitems'},$va{'titems'},$va{'oitems'},$va{'paship'}) = ('off','off','off','on','off','off','off','off');
	}elsif($in{'ds'}){	
		($va{'sitems'},$va{'ditems'},$va{'xitems'},$va{'mitems'},$va{'pitems'},$va{'titems'},$va{'oitems'},$va{'paship'}) = ('off','on','off','off','off','off','off','off');
	}elsif($in{'pend'}){
		($va{'sitems'},$va{'ditems'},$va{'xitems'},$va{'mitems'},$va{'pitems'},$va{'titems'},$va{'oitems'},$va{'paship'}) = ('off','off','off','off','on','off','off','off');
	}elsif($in{'intran'}){
		($va{'sitems'},$va{'ditems'},$va{'xitems'},$va{'mitems'},$va{'pitems'},$va{'titems'},$va{'oitems'},$va{'paship'}) = ('off','off','off','off','off','on','off','off');	
	}elsif($in{'ostock'}){
		($va{'sitems'},$va{'ditems'},$va{'xitems'},$va{'mitems'},$va{'pitems'},$va{'titems'},$va{'oitems'},$va{'paship'}) = ('off','off','off','off','off','off','on','off');	
	}elsif($in{'xd'}){
		($va{'sitems'},$va{'ditems'},$va{'xitems'},$va{'mitems'},$va{'pitems'},$va{'titems'},$va{'oitems'},$va{'paship'}) = ('off','off','on','off','off','off','off','off');
	}
#	elsif($in{'partialshipped'}){
#		($va{'sitems'},$va{'ditems'},$va{'xitems'},$va{'mitems'},$va{'pitems'},$va{'titems'},$va{'oitems'},$va{'paship'}) = ('off','off','off','off','off','off','off','on');
#	}
	else{
		($va{'sitems'},$va{'ditems'},$va{'xitems'},$va{'mitems'},$va{'pitems'},$va{'titems'},$va{'oitems'},$va{'paship'}) = ('on','off','off','off','off','off','off','off');
	}

	$in{'orders'} = int($in{'orders'});

	###
	### Base Query
	###
	$basequery = "FROM 
			      sl_orders INNER JOIN sl_orders_products ON(sl_orders.ID_orders=sl_orders_products.ID_orders )
			      LEFT JOIN sl_products ON(sl_products.ID_products=RIGHT(sl_orders_products.ID_products,6)) 
			      LEFT JOIN sl_parts ON(sl_parts.ID_parts=RIGHT(sl_orders_products.ID_products,4)) 
			      LEFT JOIN sl_skus ON (sl_orders_products.ID_products=ID_sku_products)
				  LEFT JOIN ( 
					  	SELECT ID_sku_products,GROUP_CONCAT(CONCAT(Qty,'|',ID_parts))AS ID_parts 
					  	FROM sl_skus_parts 
					  	GROUP BY ID_sku_products
				  )temp ON (sl_skus.ID_sku_products=temp.ID_sku_products)
			      LEFT JOIN  
			      		sl_warehouses_batches_orders 
			      		ON sl_warehouses_batches_orders.ID_orders_products = sl_orders_products.ID_orders_products 
			      		AND sl_warehouses_batches_orders.Status IN ('In Fulfillment','Shipped','In Transit')
			      WHERE sl_warehouses_batches_orders.ID_orders_products IS NULL   
			      AND (ISNULL(ShpDate) OR ShpDate='' OR ShpDate='0000-00-00')
			      AND Ptype !='COD' 
			      AND sl_orders.Status=$ordstatus 
			      AND sl_orders_products.Status='Active' 
			      AND sl_orders_products.ID_products > 1000000
			      AND LEFT(sl_orders_products.ID_products,1) < 6";

	if($in{'action'} eq 'full'){

		foreach my $key (keys %in){

			if ($key =~ /pid_(\d+)/){

				$in{'id_products'} = $1;
				$in{'orders'} = $in{$key};

				if ($in{'mult'}){
					$sth = &Do_SQL("SELECT sl_orders.ID_orders,sl_orders_products.ID_orders_products 
									$basequery
									AND IF(LENGTH(Related_ID_products) = 9 AND RIGHT(sl_orders_products.ID_products,6) = '000000',Related_ID_products,sl_orders_products.ID_products)='$in{'id_products'}'
									AND (StatusPrd='None' OR StatusPrd='') 
									AND sl_orders.shp_type<>2
									AND 1<(SELECT COUNT(*) FROM sl_orders_products WHERE Status='Active' AND ID_orders=sl_orders.ID_orders AND sl_orders_products.ID_products NOT LIKE '6%') 
									GROUP BY sl_orders.ID_orders ORDER BY sl_orders.ID_orders $in{'so'} LIMIT 0,$in{'orders'};");
				}elsif($in{'xd'}){
					$sth = &Do_SQL("SELECT sl_orders.ID_orders,sl_orders_products.ID_orders_products
					 				$basequery
					 				AND IF(LENGTH(Related_ID_products) = 9 AND RIGHT(sl_orders_products.ID_products,6) = '000000',Related_ID_products,sl_orders_products.ID_products)='$in{'id_products'}'
									AND (StatusPrd='None' OR StatusPrd='') 
									AND sl_orders.shp_type=2 
									GROUP BY sl_orders.ID_orders ORDER BY sl_orders.ID_orders $in{'so'} LIMIT 0,$in{'orders'}");
				}elsif($in{'ostock'}){
					$sth = &Do_SQL("SELECT sl_orders.ID_orders,sl_orders_products.ID_orders_products 
									$basequery
									AND IF(LENGTH(Related_ID_products) = 9 AND RIGHT(sl_orders_products.ID_products,6) = '000000',Related_ID_products,sl_orders_products.ID_products)='$in{'id_products'}'
									AND StatusPrd='Out of Stock' 
									AND sl_orders.shp_type<>2 
									GROUP BY sl_orders.ID_orders ORDER BY sl_orders.ID_orders $in{'so'} LIMIT 0,$in{'orders'}");
				}else{
					$sth = &Do_SQL("SELECT sl_orders.ID_orders,sl_orders_products.ID_orders_products 
									$basequery
									AND IF(LENGTH(Related_ID_products) = 9 AND RIGHT(sl_orders_products.ID_products,6) = '000000',Related_ID_products,sl_orders_products.ID_products)='$in{'id_products'}'
									AND (StatusPrd='None' OR StatusPrd='') 
									AND 1=(SELECT COUNT(*) FROM sl_orders_products WHERE Status='Active' AND ID_orders=sl_orders.ID_orders AND sl_orders_products.ID_products NOT LIKE '6%') 
									AND sl_orders.shp_type<>2 
									ORDER BY sl_orders.ID_orders $in{'so'} LIMIT 0,$in{'orders'}");
				}
				$va{'message'} = &trans_txt('status_updated');
				while (($id_orders,$id_orders_products) = $sth->fetchrow_array()){
					my ($sth2) = &Do_SQL("UPDATE sl_orders SET StatusPrd='$prdstatus' WHERE ID_orders='$id_orders'");
					&auth_logging('orders_updated',$id_orders);

					&add_order_notes_by_type($id_orders,"The order has been marked to : $va{'fftype'}","Low");
					&auth_logging('orders_note_added',$id_orders);
				}
			}
		}
		$va{'message'} = &trans_txt('done');
		print "Content-type: text/html\n\n";
		print &build_page('toprint_msg.html');
		return;

	}elsif ($in{'action'}){

		$basequery .= " AND IF(LENGTH(Related_ID_products) = 9 AND RIGHT(sl_orders_products.ID_products,6) = '000000',Related_ID_products,sl_orders_products.ID_products)='$in{'id_products'}' ";

		if (!$in{'id_products'}){
			$va{'message'} = &trans_txt('noprint');
		}elsif(!$in{'orders'}){
			$va{'message'} = &trans_txt('noprint');
		}else{
			my ($tot_rec,$sth);
			if ($in{'mult'}){
			 	$sth = &Do_SQL("SELECT COUNT(DISTINCT(sl_orders.ID_orders)) $basequery AND (StatusPrd='None' OR StatusPrd='') AND sl_orders.shp_type <> 2 AND 1<(SELECT COUNT(*) FROM sl_orders_products WHERE Status='Active' AND ID_orders=sl_orders.ID_orders AND sl_orders_products.ID_products NOT LIKE '6%')");
			}elsif($in{'xd'}){
				$sth = &Do_SQL("SELECT COUNT(DISTINCT(sl_orders.ID_orders)) $basequery AND (StatusPrd='None' OR StatusPrd='') AND sl_orders.shp_type = 2");
			}elsif($in{'ostock'}){
				$sth = &Do_SQL("SELECT COUNT(DISTINCT(sl_orders.ID_orders)) $basequery AND StatusPrd = 'Out of Stock' AND sl_orders.shp_type <> 2");
			}
#			elsif($in{'partialshipped'}){
#				$sth = &Do_SQL("SELECT SUM(Quantity) FROM sl_orders,sl_orders_products WHERE sl_orders.ID_orders=sl_orders_products.ID_orders AND sl_orders.Status='Shipped' and (isnull(ShpDate)or ShpDate='0000-00-00') AND Ptype !='COD' AND sl_orders_products.ID_products='$in{'id_products'}'");
#			}
			else{
				$sth = &Do_SQL("SELECT COUNT(DISTINCT(sl_orders.ID_orders)) $basequery AND (StatusPrd='None' OR StatusPrd='') AND sl_orders.shp_type <> 2 AND 1=(SELECT COUNT(*) FROM sl_orders_products WHERE Status='Active' AND ID_orders=sl_orders.ID_orders AND sl_orders_products.ID_products NOT LIKE '6%')");
			}
			$tot_rec = $sth->fetchrow();
			if ($tot_rec==0){
				$va{'message'} = &trans_txt('noprint');
			}elsif ($tot_rec < $in{'orders'}){
				$in{'orders'} = $tot_rec;
			}
		}
		
		if ($va{'message'}){
			print "Content-type: text/html\n\n";
			print &build_page('toprint_msg.html');
			return;
		}else{
			if ($in{'mult'}){
				$sth = &Do_SQL("SELECT sl_orders.ID_orders,sl_orders_products.ID_orders_products $basequery AND (StatusPrd='None' OR StatusPrd='') AND sl_orders.shp_type <> 2 AND 1<(SELECT COUNT(*) FROM sl_orders_products WHERE Status='Active' AND ID_orders=sl_orders.ID_orders AND sl_orders_products.ID_products NOT LIKE '6%') GROUP BY sl_orders.ID_orders ORDER BY sl_orders.ID_orders $in{'so'} LIMIT 0,$in{'orders'};");
			}elsif($in{'xd'}){
				$sth = &Do_SQL("SELECT sl_orders.ID_orders,sl_orders_products.ID_orders_products $basequery AND (StatusPrd='None' OR StatusPrd='') AND sl_orders.shp_type = 2 GROUP BY sl_orders.ID_orders ORDER BY sl_orders.ID_orders $in{'so'} LIMIT 0,$in{'orders'}");
			}elsif($in{'ostock'}){
				$sth = &Do_SQL("SELECT sl_orders.ID_orders,sl_orders_products.ID_orders_products $basequery AND StatusPrd = 'Out of Stock' AND sl_orders.shp_type <> 2 ORDER BY sl_orders.ID_orders $in{'so'} LIMIT 0,$in{'orders'}");
			}else{
				$sth = &Do_SQL("SELECT sl_orders.ID_orders,sl_orders_products.ID_orders_products $basequery AND (StatusPrd='None' OR StatusPrd='') AND sl_orders.shp_type <> 2 AND 1=(SELECT COUNT(*) FROM sl_orders_products WHERE Status='Active' AND ID_orders=sl_orders.ID_orders AND sl_orders_products.ID_products NOT LIKE '6%') ORDER BY sl_orders.ID_orders $in{'so'} LIMIT 0,$in{'orders'}");
			}
			$va{'message'} = &trans_txt('status_updated');
			while (($id_orders,$id_orders_products) = $sth->fetchrow_array()){
				my ($sth2) = &Do_SQL("UPDATE sl_orders SET StatusPrd='$prdstatus' WHERE ID_orders='$id_orders'");
				&auth_logging('orders_updated',$id_orders);

				&add_order_notes_by_type($id_orders,"The order has been marked to : $va{'fftype'}","Low");
				&auth_logging('orders_note_added',$id_orders);
			}
		
			print "Content-type: text/html\n\n";
			print &build_page('toprint_msg.html');
			return;
		}
		print qq|</body>\n</html>\n|;
		return;
	}
	
	if($in{'id_products'}){

		$basequery .= " AND IF(LENGTH(Related_ID_products) = 9 AND RIGHT(sl_orders_products.ID_products,6) = '000000',Related_ID_products,sl_orders_products.ID_products)='$in{'id_products'}' ";
		my ($sth) = substr($in{'id_products'},0,1) == 4 ? &Do_SQL("SELECT Name, Model FROM sl_parts WHERE ID_parts = '".substr($in{'id_products'},-4)."'") : &Do_SQL("SELECT Name, Model FROM sl_products WHERE ID_products='".substr($in{'id_products'},-6)."'");
		my $rec = $sth->fetchrow_hashref;
		$va{'id_products'} = &format_sltvid($in{'id_products'});
		$va{'name'} = $rec->{'Name'};
		$va{'model'} = $rec->{'Model'};
		$va{'choices'} = &load_choices($in{'id_products'});
		my ($sth) = &Do_SQL("SET group_concat_max_len = 204800;");
		if ($in{'mult'}){
		 	$sth = &Do_SQL("SELECT COUNT(DISTINCT(sl_orders.ID_orders)), GROUP_CONCAT(DISTINCT sl_orders.ID_orders) $basequery AND (StatusPrd='None' OR StatusPrd='') AND sl_orders.shp_type <> 2 AND 1<(SELECT COUNT(*) FROM sl_orders_products WHERE Status='Active' AND ID_orders=sl_orders.ID_orders AND sl_orders_products.ID_products NOT LIKE '6%')");
		}elsif($in{'xd'}){
			$sth = &Do_SQL("SELECT COUNT(DISTINCT(sl_orders.ID_orders)), GROUP_CONCAT(DISTINCT sl_orders.ID_orders) $basequery AND (StatusPrd='None' OR StatusPrd='') AND sl_orders.shp_type = 2");
		}elsif($in{'ostock'}){
			$sth = &Do_SQL("SELECT COUNT(DISTINCT(sl_orders.ID_orders)), GROUP_CONCAT(DISTINCT sl_orders.ID_orders) $basequery AND StatusPrd = 'Out of Stock' AND sl_orders.shp_type <> 2");
		}else{
			$sth = &Do_SQL("SELECT COUNT(DISTINCT(sl_orders.ID_orders)), GROUP_CONCAT(DISTINCT sl_orders.ID_orders) $basequery AND (StatusPrd='None' OR StatusPrd='') AND sl_orders.shp_type <> 2 AND 1=(SELECT COUNT(*) FROM sl_orders_products WHERE Status='Active' AND ID_orders=sl_orders.ID_orders AND sl_orders_products.ID_products NOT LIKE '6%');");
		}
		my ($orders, $id_group_orders) = $sth->fetchrow();

		#####
		##### Other Products / SKUS in the order
		#####
		my ($sth) = substr($in{'id_products'},0,1) == 4 ? 
					&Do_SQL("SELECT Related_ID_products, Name, SUM(Quantity), temp.ID_parts 
							FROM sl_orders_products INNER JOIN sl_parts 
							ON ID_parts = Related_ID_products - 400000000
							LEFT JOIN ( 
							  			SELECT ID_parts + 400000000 AS ID_sku_products ,GROUP_CONCAT(CONCAT(Qty,'|',ID_parts))AS ID_parts 
							  			FROM sl_skus_parts 
							  			GROUP BY ID_sku_products
						  				)temp ON Related_ID_products=ID_sku_products 
							WHERE ID_orders IN($id_group_orders) 
							AND Related_ID_products != '$in{'id_products'}' 
							GROUP BY ID_parts ORDER BY ID_parts;") :

					&Do_SQL("SELECT sl_orders_products.ID_products, Name, SUM(Quantity), temp.ID_parts 
							FROM sl_orders_products INNER JOIN sl_products 
							ON sl_products.ID_products = RIGHT(sl_orders_products.ID_products,6) 
							LEFT JOIN ( 
							  			SELECT ID_sku_products,GROUP_CONCAT(CONCAT(Qty,'|',ID_parts))AS ID_parts 
							  			FROM sl_skus_parts 
							  			GROUP BY ID_sku_products
						  				)temp ON sl_orders_products.ID_products=ID_sku_products 
							WHERE ID_orders IN($id_group_orders) 
							AND sl_orders_products.ID_products != '$in{'id_products'}' 
							GROUP BY sl_orders_products.ID_products 
							ORDER BY sl_orders_products.ID_products;");

		my (@c) = split(/,/,$cfg{'srcolors'});
		while(my($id_products,$name,$qty,$grouped_parts) = $sth->fetchrow() ) {			

			$d = 1 - $d;
			$cadparts="";
			if($grouped_parts ne ''){
				my @partsin=split(/,/,$grouped_parts);
				for(0..$#partsin){
					my @qtyid=split(/\|/,$partsin[$_]);
					my ($link_inv, $qty_inv, $qty_batch) = &inventory_by_id(400000000+$qtyid[1]);
					$cadparts.= "<tr bgcolor='$c[$d]'>\n";
					$cadparts.= "<td valign='top' align='center'>".$qty*$qtyid[0]." x ".&format_sltvid(400000000+$qtyid[1]). "</td>\n
								    <td valign='top'>".&load_db_names('sl_parts','ID_parts',$qtyid[1],'[Name]')."</td>\n
								    <td valign='top' align='right'>".format_number($qty_batch)."</td>\n
									<td valign='top' align='right'>".format_number($qty_inv)."</td>\n
								    <td valign='top' align='right'>".$link_inv." </td>\n
								  </tr>\n";
				}
			}

			$va{'skuslog'} .= qq|<tr bgcolor='$c[$d]'>\n
									<td class='smalltext'>$qty x |.&format_sltvid($id_products).qq|</td>\n
									<td class='smalltext'>|.$name.qq|</td>\n
									<td align="right" colspan="3"></td>\n
								<tr>\n
								$cadparts\n|;
		}
		(!$va{'skuslog'}) and ($va{'skuslog'} = qq|<tr>\n<td colspan="5">|.&trans_txt('nomatches').qq|</td>\n<tr>\n|);

		#my ($sth) = &Do_SQL("SELECT COUNT(*) FROM sl_orders,sl_orders_products WHERE sl_orders.ID_orders=sl_orders_products.ID_orders AND sl_orders.Status=$ordstatus AND sl_orders_products.ID_products='$in{'id_products'}';");
		$va{'orders'} = $orders;
		my ($sth) = &Do_SQL("SELECT * FROM sl_prnmanifest_log WHERE Date=CURDATE() AND ID_products='$in{'id_products'}' ORDER BY ID_prnmanifest_log DESC;");
		while ($rec = $sth->fetchrow_hashref()){
			$va{'printlog'} .= qq|
					<tr>
						<td class="smalltext">($rec->{'ID_admin_users'}) |. &load_db_names('admin_users','ID_admin_users',$rec->{'ID_admin_users'},"[FirstName] [LastName]").qq| : $rec->{'Qty'} x $rec->{'PType'} \@ $rec->{'Time'}</td>
					</tr>
			|;
		}
	}

	print "Content-type: text/html\n\n";
	$va{'page_title'} = trans_txt("pageadmin");
	print &build_page('packing_fadd_form.html');
}



##################################################################
##########   PACKING LIST     	######################
##################################################################

sub packing_add {
# --------------------------------------------------------
# Last Modification by JRG : 06/12/2009 : Se agrega log
	if ($in{'createpl'}){
		my ($id,@ary);
		#&cgierr;
		foreach my $key (keys %in){
			if ($in{$key} eq 'create_pklist'){
				my ($sth) = &Do_SQL("INSERT INTO sl_packinglist SET ID_orders_products='$key', Status='New',Date=CURDATE(),Time=CURTIME(),ID_admin_users='$usr{'id_admin_users'}'");
				$id = $sth->{'mysql_insertid'};
				&auth_logging('packinglist_added',$id);
				$id_products = &load_name('sl_orders_products','ID_orders_products',$key,'ID_products');
			}
			my ($sth) = &Do_SQL("UPDATE sl_orders_products SET ID_packinglist='$id' WHERE ID_orders_products='$key'");
			$id_ordupdlog = &load_name('sl_orders_products','ID_orders_products',$key,'ID_orders');
			&auth_logging('orders_products_updated',$id_ordupdlog);
		}
	}
	my ($query) = "sl_orders_products.ID_packinglist=0  AND Ptype !='COD' AND sl_orders.Status='Processed' AND sl_warehouses_location.Quantity>0";
	if ($in{'id_warehouses'}){
		$query .= " AND sl_warehouses_location.ID_warehouses='$in{'id_warehouses'}'";
	}else{
		&packing_addform;
		return;
	}

	$va{'matches'} = 1;
	$va{'pageslist'} = 1;
	#my ($sth) = &Do_SQL("SELECT COUNT(*) FROM sl_orders,sl_orders_products WHERE sl_orders.ID_orders=sl_orders_products.ID_orders AND sl_orders.Status='Processed' AND sl_orders_products.ID_packinglist=0");
	my ($sth) = &Do_SQL("SELECT COUNT(*) FROM sl_orders LEFT JOIN sl_orders_products ON sl_orders.ID_orders=sl_orders_products.ID_orders LEFT JOIN sl_warehouses_location ON sl_orders_products.ID_products=sl_warehouses_location.ID_products 	WHERE $query");
	
	$va{'matches'} = $sth->fetchrow();
	if ($va{'matches'}>0){
		(!$in{'nh'}) and ($in{'nh'}=1);
		$first = ($in{'nh'} - 1) * $usr{'pref_maxh'};			
		($va{'pageslist'},$qs) = &pages_list($in{'nh'},"/cgi-bin/mod/$usr{'application'}/admin",$va{'matches'},$usr{'pref_maxh'});
		my (@c) = split(/,/,$cfg{'srcolors'});
		#my ($sth) = &Do_SQL("SELECT * FROM sl_orders,sl_orders_products WHERE sl_orders.ID_orders=sl_orders_products.ID_orders AND sl_orders.Status='Processed' AND sl_orders_products.ID_packinglist=0 ORDER BY sl_orders.ID_orders DESC LIMIT $first,$usr{'pref_maxh'};");
		my ($sth) = &Do_SQL("SELECT DISTINCT(sl_orders.ID_orders),sl_orders_products.ID_products as ID_products,sl_orders.ID_orders as ID_orders,sl_orders.Date as Date,ID_orders_products FROM sl_orders LEFT JOIN sl_orders_products ON sl_orders.ID_orders=sl_orders_products.ID_orders LEFT JOIN sl_warehouses_location ON sl_orders_products.ID_products=sl_warehouses_location.ID_products WHERE $query ORDER BY sl_orders.ID_orders DESC LIMIT $first,$usr{'pref_maxh'};");
		while ($rec = $sth->fetchrow_hashref){
			$d = 1 - $d;
			my($qty,$inv) = &load_inventory($rec->{'ID_products'});
			$va{'searchresults'} .= "<tr bgcolor='$c[$d]'>\n";
			$va{'searchresults'} .= "  <td class='smalltext' valign='top' align='center'>";
			($qty>0) and ($va{'searchresults'} .= "<input type='checkbox' name='$rec->{'ID_orders_products'}' value='create_pklist'>\n");
			$va{'searchresults'} .= " </td>";
			$va{'searchresults'} .= "  <td class='smalltext' valign='top' align='center'>$rec->{'ID_orders'}</td>\n";
			$va{'searchresults'} .= "  <td class='smalltext' valign='top'>$rec->{'Date'}</td>\n";
			$va{'searchresults'} .= "  <td class='smalltext' valign='top'>".&format_sltvid($rec->{'ID_products'}). "</td>\n";
			$va{'searchresults'} .= "  <td class='smalltext' valign='top'>".&load_db_names('sl_products','ID_products',substr($rec->{'ID_products'},3,6),'[Name]<br>[Model]')."</td>\n";
			$va{'searchresults'} .= "  <td class='smalltext' valign='top'>$inv</td>\n";
			$va{'searchresults'} .= "</tr>\n";
		}
	}else{
		$va{'pageslist'} = 1;
		$va{'searchresults'} = qq|
		<tr>
			<td colspan='6' align="center">|.&trans_txt('search_nomatches').qq|</td>
		</tr>\n|;
	}
	print "Content-type: text/html\n\n";
	print &build_page('packing_add.html');
}

sub packing_list {
# --------------------------------------------------------
	my ($query);
	if ($in{'action'}){
		foreach my $key (keys %in) {
			if ($in{$key} eq &trans_txt('btn_order')){
				&packing_list_order(substr($key,4));
				return;
			}elsif ($in{$key} eq &trans_txt('btn_inv')){
				&packing_list_inv(substr($key,4));
				return;
			}elsif ($in{$key} eq &trans_txt('btn_plist')){
				&packing_list_pl(substr($key,4));
				return;
			}
		}
	}
	if ($in{'status'}){
		$query = "AND sl_packinglist.Status='$in{'status'}'";
	}
	
	$va{'matches'} = 1;
	$va{'pageslist'} = 1;
	my ($sth) = &Do_SQL("SELECT COUNT(*) FROM sl_packinglist,sl_orders_products WHERE sl_packinglist.ID_orders_products=sl_orders_products.ID_orders_products $query");
	$va{'matches'} = $sth->fetchrow();
	if ($va{'matches'}>0){
		(!$in{'nh'}) and ($in{'nh'}=1);
		$first = ($in{'nh'} - 1) * $usr{'pref_maxh'};			
		($va{'pageslist'},$qs) = &pages_list($in{'nh'},"/cgi-bin/mod/$usr{'application'}/admin",$va{'matches'},$usr{'pref_maxh'});
		my (@c) = split(/,/,$cfg{'srcolors'});
		my ($sth) = &Do_SQL("SELECT *,sl_packinglist.Status AS PLStatus,sl_orders_products.Date as ODate FROM sl_packinglist,sl_orders_products WHERE sl_packinglist.ID_orders_products=sl_orders_products.ID_orders_products ORDER BY sl_packinglist.ID_packinglist DESC LIMIT $first,$usr{'pref_maxh'};");
		while ($rec = $sth->fetchrow_hashref){
			$d = 1 - $d;
			$va{'searchresults'} .= "<tr bgcolor='$c[$d]' onmouseover='m_over(this)' onmouseout='m_out(this)'>\n";
			$va{'searchresults'} .= "  <td class='smalltext' valign='top' align='center'>";
			$va{'searchresults'} .= qq|<input type="submit" name="ord_$rec->{'ID_orders'}" value="|.&trans_txt('btn_order').qq|" class="button">
										<input type="submit" name="inv_$rec->{'ID_orders'}" value="|.&trans_txt('btn_inv').qq|" class="button">
										<input type="submit" name="pls_$rec->{'ID_packinglist'}" value="|.&trans_txt('btn_plist').qq|" class="button">|;
			$va{'searchresults'} .= "</td>\n";
			$va{'searchresults'} .= "  <td class='smalltext' valign='top' align='center'>$rec->{'ID_orders'}</td>\n";
			$va{'searchresults'} .= "  <td class='smalltext' valign='top'>$rec->{'ODate'}</td>\n";
			$va{'searchresults'} .= "  <td class='smalltext' valign='top'>$rec->{'PLStatus'}</td>\n";
			$va{'searchresults'} .= "  <td class='smalltext'>".&format_sltvid($rec->{'ID_products'})."<BR>".&load_db_names('sl_products','ID_products',substr($rec->{'ID_products'},3,6),'[Model]<br>[Name]')."</td>\n";
			$va{'searchresults'} .= "</tr>\n";
		}
	}else{
		$va{'pageslist'} = 1;
		$va{'searchresults'} = qq|
		<tr>
			<td colspan='5' align="center">|.&trans_txt('search_nomatches').qq|</td>
		</tr>\n|;
	}

	print "Content-type: text/html\n\n";
	print &build_page('packing_list.html');
}

sub packing_list_order {
# --------------------------------------------------------

# Author: Unknown
# Created on: Unknown
# Last Modified on: 08/27/2008
# Last Modified by: Jose Ramirez Garcia
# Description : 
# Forms Involved: 
# Parameters : 
# Notes : the orderdisc was added to ordertax

	my ($id) = @_;
	if ($in{'id_orders'}){
		$id = $in{'id_orders'};
	}
	
	&load_cfg('sl_orders');
	my (%rec) = &get_record('ID_orders',$id,'sl_orders');
	foreach $key (sort keys %rec) {
		$in{lc($key)} = uc($rec{$key});
		($db_valid_types{lc($key)} ne 'html') and ($in{lc($key)} =~ s/\n/<br>/g);
	}
	### Load Customer Info
	if ($in{'id_customers'}){
		my ($sth) = &Do_SQL("SELECT * FROM sl_customers WHERE ID_customers='$in{'id_customers'}';");
		$rec = $sth->fetchrow_hashref;
		foreach $key (keys %{$rec}){
			$in{'customers.'.lc($key)} = uc($rec->{$key});
		}
	}
	
	#### Shipping
	my (@types) = split(/,/,$cfg{'shp_types'});
	foreach $type (@types) {
		if ($in{'shp_type'} eq 1) {
			$in{'shp_type'} = "$types[0]";
		}
		elsif ($in{'shp_type'} eq 2) {
			$in{'shp_type'} = "$types[1]";		
		}
		elsif ($in{'shp_type'} eq 3){
			$in{'shp_type'} = "$types[2]"; 
		}
	}

	### User Info
	&get_db_extrainfo('admin_users',$in{'id_admin_users'});

	### Totals
	### Orders Totals
	$va{'total_taxes'} = &format_price((&taxables_in_order($in{'id_orders'})-$in{'orderdisc'})*$in{'ordertax'});
	$va{'total_order'} = &format_price($in{'ordernet'}+$in{'ordershp'}+$in{'ordernet'}*$in{'ordertax'});
	$va{'total_order'} = &format_price(int(($in{'ordernet'}+$in{'ordershp'}+$in{'ordernet'}*$in{'ordertax'})*100+0.9)/100);
	$va{'ordernet'} = &format_price($in{'ordernet'});
	$va{'ordershp'} = &format_price($in{'ordershp'});
	$va{'tax'} = $in{'ordertax'}*100;
	$va{'ordertax'} = &format_number($in{'ordertax'}*100);
	
	if ($in{'print'}){
		print "Content-type: text/html\n\n";
		print &build_page('header_print.html');
		print &build_page('packing_list_prorder.html');
	}else{
		print "Content-type: text/html\n\n";
		print &build_page('packing_list_order.html');
	}
}

sub packing_list_inv {
# --------------------------------------------------------

# Author: Unknown
# Created on: Unknown
# Last Modified on: 08/27/2008
# Last Modified by: Jose Ramirez Garcia
# Description : 
# Forms Involved: 
# Parameters : 
# Notes : the orderdisc was added to ordertax
	my ($id) = @_;
	if ($in{'id_orders'}){
		$id = $in{'id_orders'};
	}
	
	&load_cfg('sl_orders');
	my (%rec) = &get_record('ID_orders',$id,'sl_orders');
	foreach $key (sort keys %rec) {
		$in{lc($key)} = uc($rec{$key});
		($db_valid_types{lc($key)} ne 'html') and ($in{lc($key)} =~ s/\n/<br>/g);
	}
	### Load Customer Info
	if ($in{'id_customers'}){
		my ($sth) = &Do_SQL("SELECT * FROM sl_customers WHERE ID_customers='$in{'id_customers'}';");
		$rec = $sth->fetchrow_hashref;
		foreach $key (keys %{$rec}){
			$in{'customers.'.lc($key)} = uc($rec->{$key});
		}
	}
	
	#### Shipping
	my (@types) = split(/,/,$cfg{'shp_types'});
	foreach $type (@types) {
		if ($in{'shp_type'} eq 1) {
			$in{'shp_type'} = "$types[0]";
		}
		elsif ($in{'shp_type'} eq 2) {
			$in{'shp_type'} = "$types[1]";		
		}
		elsif ($in{'shp_type'} eq 3){
			$in{'shp_type'} = "$types[2]"; 
		}
	}

	### User Info
	&get_db_extrainfo('admin_users',$in{'id_admin_users'});

	### Totals
	### Orders Totals
	$va{'total_taxes'} = &format_price((&taxables_in_order($in{'id_orders'})-$in{'orderdisc'})*$in{'ordertax'});
	$va{'total_order'} = &format_price($in{'ordernet'}+$in{'ordershp'}+$in{'ordernet'}*$in{'ordertax'});
	$va{'total_order'} = int(($in{'ordernet'}+$in{'ordershp'}+$in{'ordernet'}*$in{'ordertax'})*100+0.9)/100;
	$va{'ordernet'} = &format_price($in{'ordernet'});
	$va{'ordershp'} = &format_price($in{'ordershp'});
	$va{'tax'} = $in{'ordertax'}*100;
	$va{'ordertax'} = &format_number($in{'ordertax'}*100);
	$va{'total_discounts'} = &format_price($in{'order_discounts'});

	if ($in{'print'}){
		print "Content-type: text/html\n\n";
		print &build_page('header_print.html');
		print &build_page('packing_list_prinv.html');
	}else{
		print "Content-type: text/html\n\n";
		print &build_page('packing_list_inv.html');
	}
}

sub packing_list_pl {
# --------------------------------------------------------

# Author: Unknown
# Created on: Unknown
# Last Modified on: 08/27/2008
# Last Modified by: Jose Ramirez Garcia
# Description : 
# Forms Involved: 
# Parameters : 
# Notes : the orderdisc was added to ordertax
	my ($id) = @_;
	if ($in{'id_packinglist'}){
		$id = $in{'id_packinglist'};
	}else{
		$in{'id_packinglist'} = $id;
	}

	$in{'id_orders'} = &load_name('sl_orders_products','ID_packinglist',$in{'id_packinglist'},'ID_orders');

	&load_cfg('sl_orders');
	
	my (%rec) = &get_record('ID_orders',$in{'id_orders'},'sl_orders');
	
	foreach $key (sort keys %rec) {
		$in{lc($key)} = uc($rec{$key});
		($db_valid_types{lc($key)} ne 'html') and ($in{lc($key)} =~ s/\n/<br>/g);
	}
	### Load Customer Info
	if ($in{'id_customers'}){
		my ($sth) = &Do_SQL("SELECT * FROM sl_customers WHERE ID_customers='$in{'id_customers'}';");
		$rec = $sth->fetchrow_hashref;
		foreach $key (keys %{$rec}){
			$in{'customers.'.lc($key)} = uc($rec->{$key});
		}
	}
	
	#### Shipping
	my (@types) = split(/,/,$cfg{'shp_types'});
	foreach $type (@types) {
		if ($in{'shp_type'} eq 1) {
			$in{'shp_type'} = "$types[0]";
		}
		elsif ($in{'shp_type'} eq 2) {
			$in{'shp_type'} = "$types[1]";		
		}
		elsif ($in{'shp_type'} eq 3){
			$in{'shp_type'} = "$types[2]"; 
		}
	}

	### User Info
	&get_db_extrainfo('admin_users',$in{'id_admin_users'});

	### Totals
	### Orders Totals
	$va{'total_taxes'} = &format_price((&taxables_in_order($in{'id_orders'})-$in{'orderdisc'})*$in{'ordertax'});
	$va{'total_order'} = &format_price($in{'ordernet'}+$in{'ordershp'}+$in{'ordernet'}*$in{'ordertax'});
	$va{'total_order'} = int(($in{'ordernet'}+$in{'ordershp'}+$in{'ordernet'}*$in{'ordertax'})*100+0.9)/100;
	$va{'ordernet'} = &format_price($va{'ordernet'});
	$va{'ordershp'} = &format_price($va{'ordershp'});
	$va{'tax'} = $in{'ordertax'}*100;
	$va{'ordertax'} = &format_number($in{'ordertax'}*100);
	
	if ($in{'print'}){
		print "Content-type: text/html\n\n";
		print &build_page('header_print.html');
		print &build_page('packing_list_prpl.html');
	}else{
		print "Content-type: text/html\n\n";
		print &build_page('packing_list_pl.html');
	}
}

##################################################################
##########    SORT WRECEIPTS     	######################
##################################################################

#############################################################################
#############################################################################
#   Function: swreceipt
#
#       Es: Genera el listado de W. Receipts listos para procesamiento
#       En: Build W Receipts List ready to process
#
#
#    Created on: 2013-03-07
#
#    Author: _Roberto Barcenas_
#
#    Modifications:
#
#        - Modified on *2013-03-21* by _Roberto Barcenas_ : Se muestran unicamente registros que contengan items
#
#   Parameters:
#
#
#  Returns:
#
#      - 
#
#   See Also:
#
#      <swreceipt_process>
#
sub swreceipt {
#############################################################################
#############################################################################


	## TO-DO: Agregar Permisos
	my (@c) = split(/,/,$cfg{'srcolors'});
	my ($sth) = &Do_SQL("SELECT COUNT(*) FROM sl_wreceipts INNER JOIN sl_wreceipts_items USING(ID_wreceipts) WHERE sl_wreceipts.Status='In Process' GROUP BY sl_wreceipts.ID_wreceipts;");
	$va{'matches'} = $sth->fetchrow;
	if ($va{'matches'}>0){
		(!$in{'nh'}) and ($in{'nh'}=1);
		$first = ($in{'nh'} - 1) * $usr{'pref_maxh'};			
		($va{'pageslist'},$qs) = &pages_list($in{'nh'},"/cgi-bin/mod/$usr{'application'}/admin",$va{'matches'},$usr{'pref_maxh'});
		my ($sth) = &Do_SQL("SELECT sl_wreceipts.*, COUNT(ID_wreceipts_items) AS TLines,SUM(Qty) AS TQty FROM sl_wreceipts INNER JOIN sl_wreceipts_items USING(ID_wreceipts) WHERE sl_wreceipts.Status='In Process' GROUP BY sl_wreceipts.ID_wreceipts  ORDER BY ID_wreceipts DESC LIMIT $first,$usr{'pref_maxh'};");
		while ($rec = $sth->fetchrow_hashref){
			$d = 1 - $d;

			##----------------------------------------------
			## Valida que ya esten validados sus gastos
			##----------------------------------------------
			my $sthAdj = &Do_SQL("SELECT COUNT(*) AS NoVal FROM sl_purchaseorders_adj WHERE ID_purchaseorders='".$rec->{'ID_purchaseorders'}."' AND Validate=0;");
			my $no_val = $sthAdj->fetchrow();
			##----------------------------------------------
			my $sty_no_valid = "";
			if( $no_val == 0 ){
				$va{'searchresults'} .= "<tr bgcolor='$c[$d]' onmouseover='m_over(this)' onmouseout='m_out(this)' onClick=\"trjump('/cgi-bin/mod/wms/admin?cmd=swreceipt_process&id_wreceipts=$rec->{'ID_wreceipts'}')\">\n";
			}else{
				$sty_no_valid = "style='color: gray;'";
				$va{'searchresults'} .= "<tr bgcolor='$c[$d]' onmouseover='m_over(this)' onmouseout='m_out(this)'>\n"; 
			}
			$va{'searchresults'} .= "   <td class='smalltext' $sty_no_valid>$rec->{'ID_wreceipts'}</td>\n";
			$va{'searchresults'} .= "   <td class='smalltext' $sty_no_valid nowrap>$rec->{'Date'}</td>\n";
			$va{'searchresults'} .= "   <td class='smalltext' $sty_no_valid>($rec->{'ID_vendors'}) ".&load_name('sl_vendors','ID_vendors',$rec->{'ID_vendors'},'CompanyName')."</td>\n";
			$va{'searchresults'} .= "   <td class='smalltext' $sty_no_valid>$rec->{'Description'}</td>\n";
			$va{'searchresults'} .= "   <td class='smalltext' $sty_no_valid>$rec->{'TLines'}</td>\n";
			$va{'searchresults'} .= "   <td class='smalltext' $sty_no_valid align='right'>".&format_number($rec->{'TQty'})."</td>\n";
			$va{'searchresults'} .= "</tr>\n";
		}
	}else{
		$va{'pageslist'} = 1;
		$va{'searchresults'} = qq|
			<tr>
				<td colspan='6' align='center'>|.&trans_txt('search_nomatches').qq|</td>
			</tr>\n|;
	}

	print "Content-type: text/html\n\n";
	print &build_page('swreceipt.html');
}


sub swreceipt_process {
# --------------------------------------------------------
# Last Modification by JRG : 03/11/2009 : Se agrega log
# Last Modified on: 06/08/09 12:15:29
# Last Modified by: MCC C. Gabriel Varela S: Se valida para no afectar a sets.
# Last Modified RB: 06/25/09  16:53:06 -- Se envian los datos para movimientos de contabilidad en sub.finance_2.html
# Last Modified RB: 09/29/2011  19:11:00 -- Se agrega el ID_warehouses a la tabla sl_purchaseorders_wreceipts y se agrega una nota en po_items_notes
# Last Modified RB: 07/03/2013  14:43:00 -- Se aplican los ajustes por recepcion.


	$in{'id_wreceipts'} = int($in{'id_wreceipts'});
	if ($in{'id_wreceipts'}>0){
		
		## Load Info
		&load_cfg('sl_wreceipts');
		%tmp = &get_record('ID_wreceipts',$in{'id_wreceipts'},'sl_wreceipts');
		
		for (0..$#db_cols){
			$in{lc($db_cols[$_])} = $tmp{lc($db_cols[$_])} if ($db_cols[$_] ne 'ID_exchangerates');
		}
		## Load Vendor Info
		my ($sth) = &Do_SQL("SELECT CompanyName, Currency, Category FROM sl_vendors WHERE ID_vendors = '$in{'id_vendors'}';");
		($in{'vendor_name'},$in{'vendor_currency'},$in{'vendor_category'}) = $sth->fetchrow_array();

		### Loading IDs
		my ($rec,@ids,@qty,@wrs,@poitems,@cusinfo,$cant);
		my $log = '<br>';	
		my $f=0;
		#my ($sth) = &Do_SQL("SELECT * FROM sl_wreceipts_items WHERE ID_wreceipts='$in{'id_wreceipts'}'");
		my ($sth) = &Do_SQL("SELECT sl_wreceipts_items.ID_wreceipts_items 
								, sl_wreceipts_items.ID_products
								, sl_wreceipts_items.Qty
								, sl_wreceipts_items.ID_customs_info
								, (SELECT sl_purchaseorders_items.ID_purchaseorders_items FROM sl_purchaseorders_items WHERE sl_purchaseorders_items.ID_purchaseorders=sl_wreceipts.ID_purchaseorders AND sl_purchaseorders_items.ID_products=sl_wreceipts_items.ID_products LIMIT 1) ID_po_item
							FROM sl_wreceipts_items
								INNER JOIN sl_wreceipts ON sl_wreceipts.ID_wreceipts=sl_wreceipts_items.ID_wreceipts
							WHERE sl_wreceipts_items.ID_wreceipts=".$in{'id_wreceipts'}."
							GROUP BY sl_wreceipts_items.ID_wreceipts_items;");
		while ($rec = $sth->fetchrow_hashref()){

			push(@ids, $rec->{'ID_products'}); 
			push(@idspo, $in{'id_purchaseorders'}); 
			push(@wrs, $rec->{'ID_wreceipts_items'}); 
			push(@poitems, $rec->{'ID_po_item'}); 
			push(@qty, $rec->{'Qty'}); 
			push(@cusinfo, $rec->{'ID_customs_info'});

			$log .= "ids[f=$f] $rec->{'ID_products'}\n<br>";
			$log .= "idspo[f=$f] $rec->{'id_purchaseorders'}\n<br>";
			$log .= "wrs[f=$f] $rec->{'ID_wreceipts_items'}\n<br>";
			$log .= "poitems[f=$f] $rec->{'ID_po_item'}\n<br>";			
			$log .= "qty[f=$f] $rec->{'Qty'}\n<br>";
			$log .= "cusinfo[f=$f] $rec->{'ID_customs_info'}\n<br>";
			
			$f++;
		}

		### Currency Check
		my $manual_exchange = 0;	
		if ($in{'vendor_currency'} ne $cfg{'acc_default_currency'} and $cfg{'acc_default_currency'}){

			$va{'currency'} = '';
			$in{'id_exchangerates'} =~ s/\$|,//g;
			$va{'currency'} = &build_select_exchangerate($in{'id_exchangerates'},$in{'vendor_currency'});
			(!$va{'currency'}) and ($manual_exchange = 1) and ($va{'currency'} = qq|<input type='text' name='id_exchangerates' value='$in{'id_exchangerates'}' size='10' onFocus='focusOn( this )' onBlur='focusOff( this )'>|);

			$va{'curstyle'} = '';
			if ($in{'id_exchangerates'} > 0){
				$exchange_rate = $manual_exchange ? $in{'id_exchangerates'} : &load_name('sl_exchangerates','ID_exchangerates',$in{'id_exchangerates'},'exchange_rate');
			}else{
				$exchange_rate = 1;
			}

		}else{
			$exchange_rate = 1;  #no Exchange Rate
			$va{'currency'} = '';
			$va{'curstyle'} = qq|style="display:none;"|;
		}		

		###########################################
		###########################################
		###########################################
		#######		Valida W. Receipt
		###########################################
		###########################################
		###########################################

		if ($in{'action'}){

			###
			### Se agrega validación del Status de la recepción
			###
			if( $in{'status'} ne 'In Process' ){
				use CGI qw(:standard);
				print redirect('/cgi-bin/mod/wms/admin?cmd=swreceipt');
			}
			
			my (%wr,$key);			
			foreach my $key (keys %in){
				if ($key =~ /(\d+)-(\d+)-(\d+)/){
					$in{$key} = int($in{$key});
					$wr{$1} += $in{$key};
					#my ($sth) = &Do_SQL("SELECT (Qty-Received) FROM sl_purchaseorders_items WHERE ID_products='$1' AND ID_purchaseorders_items='$3'");
					my ($sth) = &Do_SQL("SELECT Qty FROM sl_wreceipts_items WHERE ID_products='$1' AND ID_wreceipts_items='$2';");
					if ($sth->fetchrow() != $in{$key}){
						$error{$key} = &trans_txt('invalid');
						++$err;
					}
				}
			}

			### Validar cantidades totales a recepcionar por cada SKU
			my $rPOItems = &Do_SQL("SELECT ID_products, SUM(Qty-Received) Qty FROM sl_purchaseorders_items WHERE ID_purchaseorders=".$in{'id_purchaseorders'}." GROUP BY ID_products;");
			while( my $rec = $rPOItems->fetchrow_hashref() ){
				my $rWRItems = &Do_SQL("SELECT ID_products, SUM(Qty) Qty FROM sl_wreceipts_items WHERE ID_wreceipts=".$in{'id_wreceipts'}." AND ID_products=".$rec->{'ID_products'}." GROUP BY ID_products;");
				my $wr_item = $rWRItems->fetchrow_hashref();
				if( int($rec->{'Qty'}) < int($wr_item->{'Qty'}) ){
					++$err;
					$va{'message'} = &trans_txt("mer_wreceipts_nomatch_items").": SKU ".$rec->{'ID_products'}." ".$rec->{'Qty'}." vs ".$wr_item->{'Qty'}."<br />";
				}
			}

			for my $i(0..$#qty){

				###--------------------------------------------------
				### Valida el Costo del SKU
				###--------------------------------------------------				
				my $sth = &Do_SQL("SELECT Price FROM sl_purchaseorders_items WHERE ID_purchaseorders='".$in{'id_purchaseorders'}."' AND ID_products='".$ids[$i]."';");
				my $cost_po = $sth->fetchrow_array();
				## Si no es un producto de regalo, entonces aplica la validación de su costo
				if( $cost_po > 0.01 ){

					if( &valid_refcost($ids[$i], $cost_po) eq 'No' ){
						$error{$ids[$i].'-'.$wrs[$i].'-'.$poitems[$i]} .= &trans_txt('skus_invalid_cost');
						++$err;
					}
				}
				###--------------------------------------------------

				### Validacion de cantidades
				if( ($qty[$i]) < int($in{$ids[$i].'-'.$wrs[$i].'-'.$poitems[$i]}) ){
					$error{$ids[$i].'-'.$wrs[$i].'-'.$poitems[$i]} .= &trans_txt('invalid');
					++$err;
				}

				if (!$in{'tw'.$wrs[$i]}){
					$error{'tw'.$wrs[$i]} = &trans_txt('required');
					++$err;
				}elsif ($in{'tw'.$wrs[$i]} eq $sys{'receiving_warehouse'}){
					$error{'tw'.$wrs[$i]} = &trans_txt('invalid');
					++$err;
				}

				my ($sth) = &Do_SQL("SELECT COUNT(*) FROM sl_locations WHERE ID_warehouses = '$in{'tw'.$wrs[$i]}' AND Code = '$in{'loc'.$wrs[$i]}';");
				my ($valid_loc) = $sth->fetchrow();
				if (!$in{'loc'.$wrs[$i]}){
					$error{'loc'.$wrs[$i]} = &trans_txt('required');
					++$err;
				}elsif (!$valid_loc){
					$error{'loc'.$wrs[$i]} = &trans_txt('invalid');
					++$err;
				}else{
					$in{'loc'.$wrs[$i]} = uc($in{'loc'.$wrs[$i]});
				}

				## Valida la Informacion de Aduana
				if ($in{'currency_vendor'} ne $cfg{'acc_default_currency'} and ($cfg{'customs_info_required'} and $cfg{'customs_info_required'} == 1) and !$cusinfo[$i] and ($cfg{'use_customs_info'} and $cfg{'use_customs_info'} == 1)){
					$error{$ids[$i].'-'.$wrs[$i].'-'.$poitems[$i]} .= &trans_txt('mer_wreceipts_no_customs');
					++$err;
				}
			}

			## check for valid Exchange rate
			if (!$exchange_rate){
				$error{'id_exchangerates'} = &trans_txt('invalid');
				++$err;
			}
			if( $in{'currency_vendor'} ne $cfg{'acc_default_currency'} and !$in{'id_exchangerates'} ){
				$error{'id_exchangerates'} = &trans_txt('required');
				++$err;
			}			

			if ($err > 0){
				$va{'message'} .= &trans_txt('reqfields_short');
			}else{

				my $rslt_val = &transaction_validate($in{'cmd'}, $in{'id_wreceipts'}, 'check');
				
				if( !$rslt_val ){
					### Se bloquea la transaccion para evitar duplicidad
		        	my $id_transaction = &transaction_validate($in{'cmd'}, $in{'id_wreceipts'}, 'insert');

					## Start transaction
					&Do_SQL("START TRANSACTION;");

					##UPDATE ID_exchangerates EN sl_wreceipts
					my ($sth) = &Do_SQL("UPDATE sl_wreceipts SET ID_exchangerates = '$in{'id_exchangerates'}' WHERE ID_wreceipts = '$in{'id_wreceipts'}';") if ($in{'id_exchangerates'}>0);
					
					my ($totalwr, $id_manifests, %items);
					##my ($sth) = &Do_SQL("INSERT INTO sl_financial SET Type='wreceipt',ID_trs='$in{'id_wreceipts'}',tb_name='sl_wreceipts',Date=NOW(),Time=CURTIME(),ID_admin_users='$usr{'id_admin_users'}'");
					##$id_finance = $sth->{'mysql_insertid'};
					
					$va{'message'} = &trans_txt('wreceipt_processed');


					###########################################
					###########################################
					######### Recepcion de Mercancia al Almacen
					###########################################
					###########################################

					## Create Manifest
					my ($sth) = &Do_SQL("INSERT INTO sl_manifests SET RequestedBy='$usr{'id_admin_users'}',AuthorizedBy='$usr{'id_admin_users'}',ProcessedBy='$usr{'id_admin_users'}',Status='In Progress',Date=CURDATE(),Time=CURTIME(),ID_admin_users='$usr{'id_admin_users'}'");
					$id_manifests = $sth->{'mysql_insertid'};
					$in{'db'} = 'sl_manifests';
					&auth_logging('manifests_added',$id_manifests);
					for my $i(0..$#qty){
						
						#Verifica si el producto es set
						$isset=&load_name('sl_skus','ID_sku_products',$ids[$i],'IsSet');

						if($isset ne'Y'){
							my ($sth) = &Do_SQL("INSERT INTO sl_manifests_items SET 
													ID_manifests='$id_manifests'
													,ID_products='$ids[$i]'
													,From_Warehouse='".$sys{'receiving_warehouse'}."'
													,From_Warehouse_Location=''
													,To_Warehouse='".&filter_values($in{'tw'.$wrs[$i]})."'
													,To_Warehouse_Location='".&filter_values($in{'loc'.$wrs[$i]})."'
													,Qty='$qty[$i]'
													,Date=CURDATE(),Time=CURTIME(),ID_admin_users='$usr{'id_admin_users'}' 
												ON DUPLICATE KEY UPDATE Qty=(Qty+$qty[$i]);");
							$in{'db'} = 'sl_manifests';
							&auth_logging('manifest_itemadded',$id_manifests);
							$items{$ids[$i]} += $qty[$i];

							########################
							######################## Entrada en sl_warehouses_location

							my $sql = "SELECT ID_warehouses_location FROM sl_warehouses_location WHERE ID_warehouses = '$in{'tw'.$wrs[$i]}' AND ID_products = '$ids[$i]' AND Location = '".&filter_values($in{'loc'.$wrs[$i]})."';";
							$log .= $sql."\n<br>";
							my ($sth) = &Do_SQL($sql);
							my ($idwl) = $sth->fetchrow();

							if($idwl and !$cusinfo[$i]) {
								## Update Inventory
								my $sql = "UPDATE sl_warehouses_location SET Quantity = Quantity + $qty[$i] WHERE ID_warehouses_location = '$idwl';";
								$log .= $sql."\n<br>";
								my ($sth) = &Do_SQL($sql);
							}else{
								my $sql_cus_info = "ID_customs_info='$cusinfo[$i]'," if(int($cusinfo[$i]) > 0);
								# Insert Inventory
								my $sql = "INSERT INTO sl_warehouses_location SET ID_warehouses = '$in{'tw'.$wrs[$i]}', ID_products = '$ids[$i]', Location = '".&filter_values($in{'loc'.$wrs[$i]})."', Quantity = '$qty[$i]', $sql_cus_info Date = CURDATE(), Time = CURTIME(), ID_admin_users = '$usr{'id_admin_users'}'";
								$log .= $sql."\n<br>";
								my ($sth) = &Do_SQL($sql);
							}

							$in{'db'} = 'sl_warehouses_location';
							&auth_logging('warehouses_location_added',$sth->{'mysql_insertid'});
						}

					} 

					########################
					######################## Entrada en sl_skus_cost
					my ($totalwr);
					### Calculo de ajuste en el PO

					##### Suma de la recepcion
					my $amt_po = 0;
					foreach my $key (keys %in) {

						if ($key =~ /(\d+)-(\d+)-(\d+)/ and $in{$key}>0){
							my ($sth) = &Do_SQL("SELECT  $in{$key} * Price FROM sl_purchaseorders_items WHERE ID_purchaseorders_items = '$3';");
							my ($this_line) = $sth->fetchrow();
							$amt_po += $this_line;
							#$str .= "($3)$amt_po += " . $this_line . "\n";
						}
					}
					

					### Separamos el Monto General, Monto del mismo Vendor y Tax del mismo vendor
					my ($sth) = &Do_SQL("SELECT SUM(Total-Tax), SUM(IF(ID_vendors = '$in{'id_vendors'}',Total-Tax,0))AS AmtSV, SUM(IF(ID_vendors = '$in{'id_vendors'}',Tax,0))AS TaxSV  FROM sl_purchaseorders_adj WHERE ID_purchaseorders = '$in{'id_purchaseorders'}' AND InCOGS = 'Yes' AND Status = 'Active';");
					my ($amt_adj, $amt_adjsv, $tax_adjsv) = $sth->fetchrow();
					$amt_adj = 0 if !$amt_adj; $amt_adjsv = 0 if !$amt_adjsv; $tax_adjsv = 0 if !$tax_adjsv;  

					### Metodo usado para la salida de inventario. FIFO: Primer entradas primeras salidas | LIFO: Ultimas entradas primeras salidas
					my $acc_method = $cfg{'acc_inventoryout_method'} ? $cfg{'acc_inventoryout_method'} : 'fifo';
					my $invout_order = $acc_method eq 'fifo' ? '' : 'DESC';

					my $id_po = $in{'id_purchaseorders'};
					my $i = 0;
					$va{'this_accounting_time'} = time();
					
					foreach my $key (keys %in) {

						if ($key =~ /(\d+)-(\d+)-(\d+)/ and $in{$key}>0){

							#### Datos de la linea del producto
							my ($sth) =  &Do_SQL("SELECT Qty,Price,$in{$key} * Price /*Total*/ FROM sl_purchaseorders_items WHERE ID_purchaseorders_items = '$3';");
							my ($line_qty,$line_price,$line_total) = $sth->fetchrow();
							my $cost = round($exchange_rate * $line_price,3);
							my $proportional = 0; my $proportionalsv = 0; my $proportionalsvt = 0; my $str_adj;
							$totalwr += ($cost * $items{$1});

							### Calculo proporcional de Ajuste
							if($amt_adj) {

								my $pct = 1;
								$pct = ($line_total / $amt_po) if  $amt_po > 0;
								$proportional = round($amt_adj * $pct * $exchange_rate / $in{$key},3);
								$proportionalsv = $amt_adjsv ? round($amt_adjsv * $pct * $exchange_rate / $in{$key},3) : 0;
								$proportionalsvt = $tax_adjsv ? round($tax_adjsv * $pct * $exchange_rate / $in{$key},3) : 0;
								$str_adj = qq|\nAdj. Value: $proportional  $pct = ($line_total / $amt_po)     $proportional = $amt_adj * $pct * $exchange_rate / $in{$key}   |;

							}
							## Costo + Proporcional Ajuste
							my $sumcost = $cost + $proportional;

							########################################################
							########################################################
							## 1 ) sl_skus_cost
							########################################################
							########################################################
							my $sql = "INSERT INTO sl_skus_cost SET ID_warehouses = '".$in{'tw'.$wrs[$i]}."' ,ID_products = '$1', ID_purchaseorders = '$id_po', Quantity = '$in{$key}', Cost = '$sumcost', Cost_Adj = '$proportional', Date = CURDATE(), Time = CURTIME(), ID_admin_users = '$usr{'id_admin_users'}'";
							$log .= $sql."\n<br>";
							my ($sth) = &Do_SQL($sql);
							my $new_id_sku_cost = $sth->{'mysql_insertid'};	
							$log .= "New ID_skus_cost: ".$new_id_sku_cost."\n<br>";
							$in{'db'} = 'sl_skus_cost';
							&auth_logging('sku_cost_added',$new_id_sku_cost);
							
							## AD::190202015 Se graban lineas en sl_sku_trans con costo
							&sku_logging($1, $in{'tw'.$wrs[$i]}, $in{'loc'.$wrs[$i]},'Purchase', $in{'id_wreceipts'}, 'sl_wreceipts', $in{$key}, $sumcost, $proportional, 'IN', $cusinfo[$i]);
							$log .= "sku_logging($1, $in{'tw'.$wrs[$i]}, $in{'loc'.$wrs[$i]},'Purchase', $in{'id_wreceipts'}, 'sl_wreceipts', $in{$key}, $sumcost, $proportional, 'IN', $cusinfo[$i])";
							
							$in{'db'} = 'sl_skus_trans';
							&auth_logging('sku_trans_added',$sth->{'mysql_insertid'});

							########################################################
							########################################################
							## 2) Movimientos de contabilidad
							########################################################
							########################################################
							my @params = ($id_po,$3,$in{$key},$cost,$proportionalsv,$proportionalsvt,$1,$exchange_rate);
							&accounting_keypoints('po_wreceipt_in_'. lc($in{'vendor_category'}), \@params );

							########################################################
							########################################################
							## 3) Actualizacion de W. Receipt y PO
							########################################################
							########################################################
				
							## Update POs
							my ($sth) = &Do_SQL("UPDATE sl_purchaseorders_items SET Received=Received+$in{$key} WHERE ID_products='$1' AND ID_purchaseorders_items='$3'");
							$in{'db'} = 'sl_purchaseorders';
							&auth_logging('purchaseorder_item_updated',$in{'id_purchaseorders'});
							my $sql_cus_info_note = "";
							if( int($cusinfo[$i]) > 0 ){
								my $rCusInf = &Do_SQL("SELECT import_declaration_number, import_declaration_date, customs FROM cu_customs_info WHERE ID_customs_info=".$cusinfo[$i].";");
								my $cusinf = $rCusInf->fetchrow_hashref();
								$sql_cus_info_note = "\nCustoms Data: ".$cusinf->{'import_declaration_number'}."  ||  ".$cusinf->{'import_declaration_date'}."  ||  ".$cusinf->{'customs'};
							}
							&Do_SQL("INSERT INTO sl_purchaseorders_notes SET ID_purchaseorders='$in{'id_purchaseorders'}', Notes='W. Receipt: $in{'id_wreceipts'}\nProduct: ($1) ". &load_name('sl_parts','ID_parts',($1 - 400000000),'Name') ."\nWarehouse: ($in{'tw'.$wrs[$i]}) ". &load_name('sl_warehouses','ID_warehouses',$in{'tw'.$wrs[$i]},'Name') ."\nLocation: $in{'loc'.$wrs[$i]}\nQuantity: $in{$key}\nCurrency Exchange: $exchange_rate\nUnit Cost: ". &format_price($cost)  ."/". &format_price($sumcost). "$str_adj $sql_cus_info_note',Type='Low', Date = CURDATE(), Time = CURTIME(), ID_admin_users='$usr{'id_admin_users'}' ");
							&Do_SQL("INSERT INTO sl_wreceipts_notes SET ID_wreceipts='$in{'id_wreceipts'}', Notes='Product: ($1) ". &load_name('sl_parts','ID_parts',($1 - 400000000),'Name') ."\nWarehouse: ($in{'tw'.$wrs[$i]}) ". &load_name('sl_warehouses','ID_warehouses',$in{'tw'.$wrs[$i]},'Name') ."\nLocation: $in{'loc'.$wrs[$i]}\nQuantity: $in{$key}\nCurrency Exchange: $exchange_rate\nUnit Cost: ". &format_price($cost) ."/". &format_price($sumcost)."$str_adj $sql_cus_info_note',Type='Low', Date = CURDATE(), Time = CURTIME(), ID_admin_users='$usr{'id_admin_users'}' ");

							## Update Status WR
							my ($sth) = &Do_SQL("UPDATE sl_wreceipts SET Status='Processed' WHERE ID_wreceipts='$in{'id_wreceipts'}'");
							$in{'db'} = 'sl_wreceipts';
							&auth_logging('wreceipt_updated',$in{'id_wreceipts'});
							my ($sth) = &Do_SQL("INSERT INTO sl_purchaseorders_wreceipts SET ID_purchaseorders_items='$3',ID_wreceipts_items = '$2', Quantity = '$in{$key}', Cost='$sumcost', Cost_Adj='$proportional', exchange_rate='$exchange_rate', ID_products = '$1', ID_warehouses = '$in{'tw'.$wrs[$i]}', Date = CURDATE(), Time = CURTIME(),ID_admin_users='$usr{'id_admin_users'}'");
							$in{'db'} = 'sl_purchaseorders';
							&auth_logging('purchaseorder_wreceipts_added',$sth->{'mysql_insertid'});

							++$i;
						}

					} 


					############################################################
					############################################################
					############################################################
					################
					################ Procesamiento Ajuste Otros Vendors
					################
					############################################################
					############################################################
					############################################################
					&wreceipt_proccess_adjustments($in{'id_purchaseorders'}, $in{'id_vendors'},$exchange_rate);


					## Valida si el po esta completo y se marca como Received
					my ($sth) = &Do_SQL("SELECT (SUM(Qty) - SUM(Received)) as quantity FROM sl_purchaseorders_items WHERE ID_purchaseorders='$in{'id_purchaseorders'}';");
					my $quantity = $rec = $sth->fetchrow_array;
					if ($quantity == 0) {
						my ($sth) = &Do_SQL("UPDATE sl_purchaseorders SET Status='Received' WHERE ID_purchaseorders='$in{'id_purchaseorders'}' LIMIT 1;");
						$in{'db'} = 'sl_purchaseorders';
						&auth_logging('mer_po_received', $in{'id_purchaseorders'});
					}

					&Do_SQL("UPDATE sl_manifests SET Comments='".&trans_txt('opr_reception_of_merchandise').": $in{'id_purchaseorders'}', Status='Completed', ProcessedDate=CURDATE() WHERE ID_manifests = '$id_manifests';");
					&Do_SQL("UPDATE sl_manifests_items SET Status='Done' WHERE ID_manifests = '$id_manifests';");
					$in{'db'} = 'sl_manifests';
					&auth_logging('opr_manifests_completed',$id_manifests);

					## Finish transaction
					$in{'db'} = 'sl_purchaseorders';
					&Do_SQL("COMMIT;");
					# &Do_SQL("ROLLBACK;"); #Only debug

					## UPDATE Finantial Transac /* Buscar sacar el reporte con sl_purchaseorders_wreceipts
					##my ($sth) = &Do_SQL("UPDATE sl_financial SET Amount='$totalwr' WHERE ID_financial='$id_finance'");
					&swreceipt();

					&Do_SQL("INSERT INTO sl_debug (cmd, id, log, Date, Time, ID_admin_users) VALUES ('wreceipt_process', '$in{'id_wreceipts'}', '".&filter_values($log)."', CURDATE(), CURTIME(), '$usr{'id_admin_users'}');");

					### Elimina el registro de la transaccion activa de este proceso
		            &transaction_validate($in{'cmd'}, $in{'id_wreceipts'}, 'delete');

					return;
				}else{
					$va{'message'} .= &trans_txt('transaction_duplicate');
				}
			}
		}		

		my (@c) = split(/,/,$cfg{'srcolors'});
		for my $i(0..$#ids){
			$d = 1 - $d;
			$aux = "<tr bgcolor='$c[$d]' onmouseover='m_over(this)' onmouseout='m_out(this)'>\n";
			if ($ids[$i] =~ /^400/){
				$aux .= "   <td class='smalltext' colspan='5'>".&format_sltvid($ids[$i])." : ".&load_db_names('sl_parts','ID_parts',int(substr($ids[$i],3,6)),'[Model]<br>[Name]')."</td>\n";
				$aux .= "	<td class='smallfieldterr' colspan='2'>".$error{$ids[$i].'-'.$wrs[$i].'-'.$poitems[$i]}."</td>";
			}else{
				$aux .= "   <td class='smalltext' colspan='5'>".&format_sltvid($ids[$i])." : ".&load_db_names('sl_products','ID_products',substr($ids[$i],3,6),'[Model]<br>[Name]')." ".&load_choices($ids[$i])."</td>\n";
				$aux .= "	<td class='smallfieldterr' colspan='2'>".$error{$ids[$i].'-'.$wrs[$i].'-'.$poitems[$i]}."</td>";
			}
			$aux .= "</tr>\n";
			++$cant;			
			$va{'searchresults'} .= $aux;
			$va{'tomanifest'} .= $aux;
			$query = ($idspo[$i]>0)?"AND sl_purchaseorders.ID_purchaseorders='$idspo[$i]'":"";
			my ($sth) = &Do_SQL("SELECT COUNT(*) FROM sl_purchaseorders_items,sl_purchaseorders WHERE ID_products='$ids[$i]' $query AND sl_purchaseorders.ID_purchaseorders=sl_purchaseorders_items.ID_purchaseorders AND ID_vendors='$in{'id_vendors'}' AND (Qty>Received OR isNull(Received))");
			if ($sth->fetchrow >0){
				my ($sth) = &Do_SQL("SELECT * FROM sl_purchaseorders_items,sl_purchaseorders WHERE ID_products='$ids[$i]' $query AND sl_purchaseorders.ID_purchaseorders=sl_purchaseorders_items.ID_purchaseorders AND ID_vendors='$in{'id_vendors'}' AND (Qty>Received OR isNull(Received))");
				while ($rec = $sth->fetchrow_hashref){

					#$d = 1 - $d;
					$va{'searchresults'} .= "<tr bgcolor='$c[$d]' onmouseover='m_over(this)' onmouseout='m_out(this)'>\n";
					$va{'searchresults'} .= "   <td class='smalltext'>&nbsp;&nbsp;&nbsp;&nbsp;</td>\n";
					$va{'searchresults'} .= "   <td class='smalltext' align='center'>$rec->{'ID_purchaseorders'}</td>\n";
					$va{'searchresults'} .= "   <td class='smalltext' align='center'>".&load_name('sl_purchaseorders','ID_purchaseorders',$rec->{'ID_purchaseorders'},'PODate')."</td>\n";
					$va{'searchresults'} .= "   <td class='smalltext' align='right'>$rec->{'Qty'}</td>\n";
					$va{'searchresults'} .= "   <td class='smalltext' align='right'>$rec->{'Received'}</td>\n";
					$va{'searchresults'} .= "   <td class='smalltext' align='right'><input type='text' name='$ids[$i]-$wrs[$i]-$rec->{'ID_purchaseorders_items'}' value='$in{$ids[$i].'-'.$wrs[$i].'-'.$rec->{'ID_purchaseorders_items'}}'size='5' onFocus='focusOn( this )' onBlur='focusOff( this )'></td>\n";
					$va{'searchresults'} .= "   <td class='smalltext' align='right'>".&format_price($rec->{'Price'})."</td>\n";
					$va{'searchresults'} .= "</tr>\n";
					++$cant;
				}
			}else{
				#$d = 1 - $d;
				$va{'searchresults'} .= "<tr bgcolor='$c[$d]' onmouseover='m_over(this)' onmouseout='m_out(this)'>\n";
				$va{'searchresults'} .= "   <td class='smalltext' colspan='7' align='center'>".&trans_txt('nopo_available')."</td>\n";
				$va{'searchresults'} .= "</tr>\n";
				++$cant;
			}
			#$d = 1 - $d;
			$va{'searchresults'} .= "<tr bgcolor='$c[$d]' onmouseover='m_over(this)' onmouseout='m_out(this)'>\n";
			$va{'searchresults'} .= "   <td class='smalltext'></td>\n";
			$va{'searchresults'} .= "   <td class='smalltext'></td>\n";
			$va{'searchresults'} .= "   <td class='smalltext'></td>\n";
			$va{'searchresults'} .= "   <td class='smalltext'></td>\n";
			$va{'searchresults'} .= "   <td class='smalltext'></td>\n";
			$va{'searchresults'} .= "   <td class='smalltext' align='right' style='border-top: thin solid #000000'>$qty[$i]</td>\n";
			$va{'searchresults'} .= "   <td class='smalltext'>&nbsp;</td>\n";
			$va{'searchresults'} .= "</tr>\n";
			++$cant;
	
			### To Manifest
			$va{'tomanifest'} .= "<tr bgcolor='$c[$d]' onmouseover='m_over(this)' onmouseout='m_out(this)'>\n";
			$va{'tomanifest'} .= "   <td class='smalltext'></td>\n";
			$va{'tomanifest'} .= "   <td class='smalltext'>From</td>\n";
			$va{'tomanifest'} .= "   <td class='smalltext' colspan='5'> ($sys{'receiving_warehouse'}) ".&load_name('sl_warehouses','ID_warehouses',$sys{'receiving_warehouse'},'Name')."</td>\n";
			$va{'tomanifest'} .= "</tr>\n";
			$va{'tomanifest'} .= "<tr bgcolor='$c[$d]' onmouseover='m_over(this)' onmouseout='m_out(this)'>\n";
			$va{'tomanifest'} .= "   <td class='smalltext'></td>\n";
			$va{'tomanifest'} .= "   <td class='smalltext'>To</td>\n";
			$va{'tomanifest'} .= "   <td class='smalltext' colspan='5'><select onchange='loadLocations(this.value,\"divload_$wrs[$i]\",\"loc$wrs[$i]\")' name='tw$wrs[$i]' onFocus='focusOn( this )' onBlur='focusOff( this )'>	<option value=''>---</option>".&build_select_regular_warehouses()."</select><script language='javascript'>\nchg_select('tw$wrs[$i]','$in{'tw'.$wrs[$i]}');\n</script>\n <span class='smallfieldterr'>$error{'tw'.$wrs[$i]}</span></td>\n";
			$va{'tomanifest'} .= "</tr>\n";
			$va{'tomanifest'} .= "<tr bgcolor='$c[$d]' onmouseover='m_over(this)' onmouseout='m_out(this)'>\n";
			$va{'tomanifest'} .= "   <td class='smalltext'></td>\n";
			$va{'tomanifest'} .= "   <td class='smalltext'>Location</td>\n";
			$va{'tomanifest'} .= "   <td class='smalltext' colspan='5'>
			<span id='divload_$wrs[$i]'></span>
			<span class='smallfieldterr'>$error{'loc'.$wrs[$i]}</span> &nbsp;&nbsp; <span class='help_on'>XYYYZ (X : Section(a-z) / YYY : Position(0-999) / Z : Level(a-z))</span></td>\n";
			$va{'tomanifest'} .= "</tr>\n";					
		}

		if (!$cant){
			$va{'matches'} = 0;
			$va{'pageslist'} = 1;
			$va{'searchresults'} = qq|
				<tr>
					<td colspan='6' align='center'>|.&trans_txt('search_nomatches').qq|</td>
				</tr>\n|;
		}

		#$in{'po_currency'} = &load_name('sl_vendors', 'ID_vendors', $in{'id_vendors'}, 'Currency');

		print "Content-type: text/html\n\n";
		print &build_page('swreceipt_process.html');
	}else{
		&swreceipt;
	}
}


##################################################################
##########    SORT WRECEIPTS     	######################
##################################################################
sub warehouses_list {
# --------------------------------------------------------

	## TO-DO: Agregar Permisos
	
	my (@c) = split(/,/,$cfg{'srcolors'});
	my ($sth) = &Do_SQL("SELECT COUNT(*) FROM sl_warehouses WHERE Status='Active'");
	$va{'matches'} = $sth->fetchrow;
	if ($va{'matches'}>0){
		(!$in{'nh'}) and ($in{'nh'}=1);
		$first = ($in{'nh'} - 1) * $usr{'pref_maxh'};			
		($va{'pageslist'},$qs) = &pages_list($in{'nh'},"/cgi-bin/mod/$usr{'application'}/admin",$va{'matches'},$usr{'pref_maxh'});
		my ($sth) = &Do_SQL("SELECT * FROM sl_warehouses WHERE Status='Active' ORDER BY ID_warehouses DESC LIMIT $first,$usr{'pref_maxh'};");
		while ($rec = $sth->fetchrow_hashref){
			$d = 1 - $d;
			$va{'searchresults'} .= "<tr bgcolor='$c[$d]' onmouseover='m_over(this)' onmouseout='m_out(this)' onClick=\"trjump('/cgi-bin/mod/wms/admin?cmd=warehouses&id_warehouses=$rec->{'ID_warehouses'}')\">\n";
			$va{'searchresults'} .= "   <td class='smalltext'>$rec->{'ID_warehouses'}</td>\n";
			$va{'searchresults'} .= "   <td class='smalltext'>$rec->{'Name'}</td>\n";
			$va{'searchresults'} .= "   <td class='smalltext'>$rec->{'City'}</td>\n";
			$va{'searchresults'} .= "   <td class='smalltext'>$rec->{'State'}</td>\n";
			$va{'searchresults'} .= "</tr>\n";
		}
	}else{
		$va{'pageslist'} = 1;
		$va{'searchresults'} = qq|
			<tr>
				<td colspan='4' align='center'>|.&trans_txt('search_nomatches').qq|</td>
			</tr>\n|;
	}

	print "Content-type: text/html\n\n";
	print &build_page('warehouses_list.html');
}

sub print_label {
# --------------------------------------------------------
# Created by: Rafael Sobrino
# Created on: 12/19/2007
# Description : 
# Notes : (Modified on : Modified by :)

	my ($query,$id,$upc);
	if (($in{'id_products'} or $in{'upc'} or $in{'xupc'}) and $in{'action'}){
		if ($in{'id_products'} and $in{'upc'} and $in{'action'}){
			$query = "SELECT ID_sku_products,UPC FROM sl_skus WHERE ID_sku_products='$in{'id_products'}' AND UPC='$in{'upc'}'";
		}elsif ($in{'id_products'} and $in{'action'}){
			$query = "SELECT ID_sku_products,UPC FROM sl_skus WHERE ID_sku_products='$in{'id_products'}'";
		}elsif ($in{'upc'} and $in{'action'}){
			$query = "SELECT ID_sku_products,UPC FROM sl_skus WHERE UPC='$in{'upc'}'";			
		}
		if ($query){		
			my ($sth) = &Do_SQL($query);
			($id,$upc) = $sth->fetchrow_array;
		}
		if ($id){
			$va{'searchresults'} .= qq|
				<tr>
					<td align='center' height='0'>ID: |.&format_sltvid($id).qq|</td>
				</tr>
				<tr>
					<td valign='top' align='center' height="69">
						<img src="/cgi-bin/common/apps/barcode?code=$upc" border="0">
					</td>
				</tr> |;
				
				&html_print_jstop;
				print &build_page('print_label_print.html');
		}elsif ($in{'xupc'}){
			$va{'searchresults'} .= qq|
				<tr>
					<td valign='top' align='center' height="69">
						<img src="/cgi-bin/common/apps/barcode?code=$in{'xupc'}" border="0">
					</td>
				</tr> |;
				
				&html_print_jstop;
				print &build_page('create_label_print.html');
		}else{
			$va{'message'} = &trans_txt('search_nomatches').$va{'matches'};	
			print "Content-type: text/html\n\n";
			print &build_page('toprint_msg.html');
		}
	}elsif (!$in{'action'}){
		print "Content-type: text/html\n\n";
		print "a";
		print &build_page('create_label.html');	
		print "b";
	}else{
		$va{'message'} = &trans_txt('noprint');
		print "Content-type: text/html\n\n";
		print &build_page('toprint_msg.html');				
	}
	
}


sub inventory {
# --------------------------------------------------------

	my ($sth) = &Do_SQL("SELECT COUNT(*) FROM sl_warehouses WHERE Status='Active';");
	$va{'matches'} = $sth->fetchrow();
	if ($va{'matches'}>0){
		($va{'pageslist'},$qs) = &pages_list($in{'nh'},"/cgi-bin/mod/$usr{'application'}/admin",$va{'matches'},$usr{'pref_maxh'});
		my (@c) = split(/,/,$cfg{'srcolors'});
		(!$in{'nh'}) and ($in{'nh'}=1);
		$first = ($in{'nh'} - 1) * $usr{'pref_maxh'};	
		my ($sth) = &Do_SQL("SELECT * FROM sl_warehouses WHERE Status='Active' ORDER BY ID_warehouses DESC ;");
		while ($rec = $sth->fetchrow_hashref){
			$d = 1 - $d;
			my ($sth2) = &Do_SQL("SELECT SUM(Quantity) FROM sl_warehouses_location WHERE ID_warehouses='$rec->{'ID_warehouses'}';");	
			$tot_items = &format_number($sth2->fetchrow());
			my ($sth2) = &Do_SQL("SELECT COUNT(*) FROM sl_warehouses_location WHERE ID_warehouses='$rec->{'ID_warehouses'}' GROUP BY ID_products;");	
			$tot_warehouse = &format_number($sth2->rows());
			## TO-DO: Agregar Cantidad de SKUS e Items en el Warehouse

	
			$va{'searchresults'} .= qq|
				<tr bgcolor='$c[$d]' onmouseover='m_over(this)' onmouseout='m_out(this)' onClick=\"trjump('/cgi-bin/mod/wms/admin?cmd=inventory_wlist&seacrh=1&ID_warehouses=$rec->{'ID_warehouses'}')\">
					<td class='smalltext'>$rec->{'ID_warehouses'}</td>
					<td class='smalltext'>$rec->{'Name'}</td>
					<td class='smalltext'>$tot_warehouse</td>
					<td class='smalltext'>$tot_items</td>
				</tr>\n|;
		}
	}else{
		$va{'pageslist'} = 1;
		$va{'searchresults'} = qq|
			<tr>
				<td colspan='4' align='center'>|.&trans_txt('search_nomatches').qq|</td>
			</tr>\n|;
	}
	print "Content-type: text/html\n\n";
	print &build_page('inventory.html');
}

sub inventory_wlist {
# --------------------------------------------------------
# Forms Involved: 
# Created on: unknown
# Last Modified on: 07/01/2008
# Last Modified by: MCC C Gabriel Varela S.
# Author: unknown
# Description : Se agrega parte para mostrar información de partes
# Parameters : 

	if ($in{'id_warehouses'}){

		if($in{'export'}) {
			inventory_file();
			return;
		}

		my ($sth) = &Do_SQL("SELECT COUNT(*) FROM sl_warehouses_location WHERE ID_warehouses='$in{'id_warehouses'}' AND Quantity>0;");
		$va{'matches'} = $sth->fetchrow();
		if ($va{'matches'}>0){
			($va{'pageslist'},$qs) = &pages_list($in{'nh'},"/cgi-bin/mod/$usr{'application'}/admin",$va{'matches'},$usr{'pref_maxh'});
			my (@c) = split(/,/,$cfg{'srcolors'});
			(!$in{'nh'}) and ($in{'nh'}=1);
			$first = ($in{'nh'} - 1) * $usr{'pref_maxh'};	
			my ($sth) = &Do_SQL("SELECT *,SUM(Quantity) AS Qty FROM sl_warehouses_location WHERE ID_warehouses='$in{'id_warehouses'}' GROUP BY ID_products HAVING Qty > 0 LIMIT $first,$usr{'pref_maxh'};");
			while ($rec = $sth->fetchrow_hashref){
				$d = 1 - $d;
				$namemodel=&load_db_names('sl_products','ID_products',substr($rec->{'ID_products'},3,6),'[Model]<br>[Name]') if length($rec->{'ID_products'}) == 9;
				if($namemodel eq "")
				{
					$namemodel=&load_db_names('sl_parts','ID_parts',substr($rec->{'ID_products'},5,4),'[Model]<br>[Name]')	if length($rec->{'ID_products'}) == 9;
					$namemodel = 'N/A' if (!$namemodel);;
				}
				
				$va{'searchresults'} .= qq|
					<tr bgcolor='$c[$d]' onmouseover='m_over(this)' onmouseout='m_out(this)' onClick=\"trjump('/cgi-bin/mod/wms/dbman?cmd=mer_parts&view=|.substr($rec->{'ID_products'},3,6).qq|')\">
						<td class='smalltext' valign='top'>$rec->{'Location'}</td>
						<td class='smalltext' valign='top'>|.&format_sltvid($rec->{'ID_products'}).qq|</td>
						<td class='smalltext'>|.$namemodel.qq|</td>
						<td class='smalltext' valign='top' align='right'>|.&format_number($rec->{'Qty'}).qq|</td>
					</tr>\n|;
			}
		}else{
			$va{'pageslist'} = 1;
			$va{'searchresults'} = qq|
				<tr>
					<td colspan='4' align='center'>|.&trans_txt('search_nomatches').qq|</td>
				</tr>\n|;
		}
		print "Content-type: text/html\n\n";
		print &build_page('inventory_det.html');	
	}else{
		&inventory;
	}
}

sub inventory_file {
# --------------------------------------------------------
# Export master File 
#print "Content-type: text/html\n\n";
#print "<pre>";
# Last Modified on: 11/10/08 17:27:50
# Last Modified by: MCC C. Gabriel Varela S: Se hace que sea una suma por ID_warehouse en lugar de sólo un quantity
	
	print "Content-type: application/vnd.ms-excel\n";
	print "Content-disposition: attachment; filename=masterinventory$in{'id_warehouses'}.csv\n\n";

	my (@cols) = ('ID','Name','Choices','Status','Warehouse','In Stock');
	print '"'.join('","', @cols)."\"\n";

	my $modquery = $in{'id_warehouses'} ? " AND ID_warehouses = '$in{'id_warehouses'}' " : ''; 

	my ($rec,$skus,$warehouse,$qty,$line_prn);
	my ($sth) = &Do_SQL("SELECT * FROM sl_products ORDER BY ID_products;");
	while ($rec = $sth->fetchrow_hashref){
		$cols[1] = $rec->{'Model'} . ' ' . $rec->{'Name'};
		$cols[1] =~ s/"//g; #"
		$cols[3] = $rec->{'Status'};
		
		my ($sth2) = &Do_SQL("SELECT COUNT(*) FROM sl_skus WHERE ID_products=$rec->{'ID_products'} ORDER BY ID_skus;");
		$skus = $sth2->fetchrow;
		
		if($skus > 0){
			my ($sth2) = &Do_SQL("SELECT * FROM sl_skus WHERE ID_products=$rec->{'ID_products'} ORDER BY ID_skus;");
			while ($skus = $sth2->fetchrow_hashref){
				$cols[0] = &format_sltvid($skus->{'ID_sku_products'});
	
				$cols[2] = "$skus->{'choice1'},$skus->{'choice2'},$skus->{'choice3'},$skus->{'choice4'}";
				$cols[2] =~ s/,,|,$|"|'//g; #";
				(!$cols[2]) and ($cols[2] = '---'); 
				my ($sth3) = &Do_SQL("SELECT ID_warehouses,sum(Quantity) FROM sl_warehouses_location WHERE ID_products=$skus->{'ID_sku_products'} $modquery GROUP BY ID_warehouses;");
				while (($warehouse,$qty) = $sth3->fetchrow_array()){
					$cols[4] = $warehouse; 
					$cols[5] = $qty;
					print '"'.join('","', @cols)."\"\n";
					$line_prn = 1;
				}
				if (!$line_prn and !$in{'id_warehouses'}){
					$cols[4] = '---';
					$cols[5] = 0;
					print '"'.join('","', @cols)."\"\n";
				}
				$line_prn = 0;
			}
		}else{
			$cols[0] = &format_sltvid(100000000+$rec->{'ID_products'});
			$cols[2] = '---';
			$cols[4] = '---';
			$cols[5] = 0;
			print '"'.join('","', @cols)."\"\n" if !$in{'id_warehouses'};
		}
	}
	
	
	################
	################ PARTS
	################
	my ($sth) = &Do_SQL("SELECT * FROM sl_parts ORDER BY ID_parts;");
	while ($rec = $sth->fetchrow_hashref){	
		$cols[1] = $rec->{'Model'} . ' ' . $rec->{'Name'};
		$cols[1] =~ s/"//g; #"
		$cols[3] = $rec->{'Status'};

		my ($sth2) = &Do_SQL("SELECT COUNT(*) FROM sl_skus WHERE ID_products=$rec->{'ID_parts'} ORDER BY ID_skus;");
		$skus = $sth2->fetchrow;
		
		if($skus > 0){
			my ($sth2) = &Do_SQL("SELECT * FROM sl_skus WHERE ID_products=$rec->{'ID_parts'} ORDER BY ID_skus;");
			while ($skus = $sth2->fetchrow_hashref){
				$cols[0] = &format_sltvid($skus->{'ID_sku_products'});
	
				$cols[2] = "$skus->{'choice1'},$skus->{'choice2'},$skus->{'choice3'},$skus->{'choice4'}";
				$cols[2] =~ s/,,|,$|"|'//g; #";
				(!$cols[2]) and ($cols[2] = '---'); 
				my ($sth3) = &Do_SQL("SELECT ID_warehouses,sum(Quantity) FROM sl_warehouses_location WHERE ID_products=$skus->{'ID_sku_products'} $modquery GROUP BY ID_warehouses;");
				while (($warehouse,$qty) = $sth3->fetchrow_array()){
					$cols[4] = $warehouse; 
					$cols[5] = $qty;
					print '"'.join('","', @cols)."\"\n";
					$line_prn = 1;
				}
				if (!$line_prn and !$in{'id_warehouses'}){
					$cols[4] = '---';
					$cols[5] = 0;
					print '"'.join('","', @cols)."\"\n";
				}
				$line_prn = 0;
			}
		}else{
			$cols[0] = &format_sltvid(400000000+$rec->{'ID_parts'});
			$cols[2] = '---';
			$cols[4] = '---';
			$cols[5] = 0;
			print '"'.join('","', @cols)."\"\n" if !$in{'id_warehouses'};
		}	
	}
	
}


###################################################################
#######################       OUTBOUND       ######################
###################################################################
sub updtracking {
# --------------------------------------------------------
# Last Modification by JRG : 03/12/2009 : Se agrega log
# Last Modified on: 05/13/09 16:53:38
# Last Modified by: MCC C. Gabriel Varela S: Se cambia SL por variable de sistema

	if ($in{'action'}){
		if (!$in{'shpdate'} or !$in{'tracking'}){
			$va{'message'} = &trans_txt('reqfields');
			++$err;
		}

		if($in{'id_packinglist'}){

			my ($sth) = &Do_SQL("SELECT COUNT(*) FROM sl_orders_products WHERE ID_packinglist='$in{'id_packinglist'}' AND ISNULL(Tracking);");
			if ($sth->fetchrow() == 0){
				$va{'message'} = &trans_txt('packinglist_updinvfld');
				++$err;
			}

		}

		if (!$err){
			my ($id_orders, $tracking,$trktype,@id_products);
			@ary = split(/\n|\s/,$in{'tracking'});
			for (0..$#ary){
				if ($ary[$_] =~ /^$cfg{'prefixentershipment'}(\d+)/i and !$id_orders){
					$id_orders = $1;
					$ary[$_] = '';
					my ($sth) = &Do_SQL("SELECT COUNT(*) FROM sl_orders WHERE ID_orders='$id_orders';");
					if ($sth->fetchrow==0){
						$id_orders = 0;
					}
				}elsif(($ary[$_] =~ /^91\d+/ or $ary[$_] =~ /^E\w+/) and !$tracking){
					$tracking = $ary[$_];
					$ary[$_] = '';
					$trktype = 'USPS';
				}elsif($ary[$_] =~ /^1Z\d+/i and !$tracking){
					$tracking = $ary[$_];
					$ary[$_] = '';
					$trktype = 'UPS';
				}else{
					my ($sth) = &Do_SQL("SELECT ID_sku_products FROM sl_skus WHERE UPC='$ary[$_]';");
					$id = $sth->fetchrow;
					if ($id >0){
						push(@id_products,$id);
						push(@upcs,$ary[$_]);
					}
				}
			}
			if (!$id_orders){
				$va{'message'} .= "<li>Invalid, Missing or Unknow Order</li>";
			}
			if (!$tracking){
				$va{'message'} .= "<li>Invalid, Missing or Unknow Tracking Number</li>";
			}
			if ($#id_products <0){
				$va{'message'} .= "<li>Invalid, Missing or Unknow UPC codes. MSG2</li>";
			}
			
			if (!$va{'message'}){
				for (0..$#id_products){
					my ($sth) = &Do_SQL("SELECT * FROM sl_orders_products WHERE ID_orders='$id_orders' AND ID_products='$id_products[$_]' AND Status='Active';");
					$rec = $sth->fetchrow_hashref;
					if ($rec->{'ID_products'}>0 and $rec->{'ShpDate'}){
						$va{'message'} .= "<li>The UPC $upcs[$_] ID ".&format_sltvid($id_products[$_])." has been shipped on $rec->{'ShpDate'}</li>";
					}elsif(!$rec->{'ID_products'}){
						$va{'message'} .= "<li>The UPC $upcs[$_] ID ".&format_sltvid($id_products[$_])." is not in the Order $id_orders</li>";
					}
				}
			}
			
			if ($va{'message'}){
				$va{'error'} = 'ERROR';
			}else{
				for (0..$#id_products){
					#RB Start - Adding PostedDate - jun/22/08
					my ($sth)  = &Do_SQL("UPDATE sl_orders_products SET Tracking='$tracking',ShpDate='$in{'shpdate'}',ShpProvider='$trktype',PostedDate = CURDATE() WHERE ID_orders='$id_orders' AND ID_products='$id_products[$_]' AND Status='Active' AND (ShpDate<>'' OR ISNULL(ShpDate) ) LIMIT 1;");
					&auth_logging('orders_products_updated',$id_orders);
					my ($sth2) = &Do_SQL("UPDATE sl_orders_payments SET PostedDate = CURDATE() WHERE ID_orders='$id_orders' AND (PostedDate IS NULL OR PostedDate = '0000-00-00') ");
					&auth_logging('orders_payments_updated',$id_orders);
					#RB End
				}
				$va{'message'} = &trans_txt('done');
				$va{'message'} = "UPDATE sl_orders_products SET Tracking='$tracking',ShpDate='$in{'shpdate'}',ShpProvider='$trktype' WHERE ID_orders='$id_orders' AND ID_products='$id_products[$_]' AND Status='Active' AND (ShpDate<>'' OR ISNULL(ShpDate) ) LIMIT 1;";
				$va{'message'} = "UPDATE sl_orders SET Status='Shipped' WHERE ID_orders='$id_orders';";
				$in{'tracking'} = '';
			}
		}
	}else{
		$in{'shpdate'} = &get_sql_date(0);
	}
	print "Content-type: text/html\n\n";
	#GV Inicia modificación 02jun2008
	$va{'message1'}="Note: The correct format for uploading a file is in accordance with the following columns (the column separator is a tab. Verify not include commas):<br>
			1.-Date<br>
			2.-Number of order<br>
			3.-Customer Name<br>
			4.-Shipping way (DHL, UPS, etc.)<br>
			5.-Tracking<br>
			6.-Product Id (9 digits)";	
	# $va{'message1'}="Nota: El formato correcto para subir un archivo es de acuerdo a las siguientes columnas (el separador de columnas es un tabulador. Verificar que no se incluyan comas):<br>
										# 1.-Fecha<br>
										# 2.-Número de orden<br>
										# 3.-Nombre del cliente<br>
										# 4.-Forma de Envío(DHL,UPS, etc.)<br>
										# 5.-Tracking<br>
										# 6.-Id de producto de 9 dígitos";
	#GV Termina modificación 02jun2008
	print &build_page('outbound_updtrk.html');
}


sub updtracking_list {
# --------------------------------------------------------
# Created by: 
# Created on: 
# Description : 
# Modified : Rafael Sobrino on 01/02/2008
# Reason : To be able to delete the files (one at a time) when the user clicks the Delete button
# Modified : Rafael Sobrino on 01/04/2008
# Reason : Number of files $#files in if statement must be > 1 since by default, when empty size is 1
	if ($in{'action'}){
		my ($filename,$key);
		foreach $key (keys %in){
			if ($key =~ /^run(.*)/){
				#GV Inicia modificación 02jun2008: Se agrega parámetro vacío a la función
				&updtracking_run($1,"$in{'Todo'}");
				#GV Termina modificación 02jun2008: Se agrega parámetro vacío a la función
				return;
			}elsif($key =~ /^del(.*)/){
				$filename = $1;
				$in{'action'} = 'del';
				$file = "$cfg{'path_shpfiles'}$filename";
				unlink ($file);
			}
		}
	}
	
	opendir (AUTHDIR, "$cfg{'path_shpfiles'}") || &cgierr("Unable to open directory $cfg{'path_shpfiles'}",604,$!);
		@files = readdir(AUTHDIR);		# Read in list of files in directory..
	closedir (AUTHDIR);

	if ($#files >1){
		for (0..$#files){
			next if ($files[$_] =~ /^\./);		# Skip "." and ".." entries..
			$va{'searchresults'} .= qq|
			<tr>
				<td width="20%"><input type="submit" class="button" name="run$files[$_]" value="Run">
					<input type="submit" class="button" name="del$files[$_]" value="Del"></td>
				<td>$files[$_]</td>
			</tr>\n|;
		}
	}else{
		$va{'searchresults'} = qq|
			<tr>
				<td colspan='2' align='center'>|.&trans_txt('search_nomatches').qq|</td>
			</tr>\n|;
	}
	print "Content-type: text/html\n\n";

	print &build_page('outbound_upflist.html');
}

sub updtracking_run {
# --------------------------------------------------------
	#GV Inicia modificación 02jun2008: Se agrega parámetro $Todo y documentación de función
	# Created on: unknown
	# Last Modified on:02/june/2008 03:47:29 PM
	# Last Modified by: MCC C. Gabriel Varela S.
	# Author: unknown
	# Description : Mejoras para un sólo tipo de archivo a analizar, y se incluye la llamada a la función cost_inventory para hacer los ajustes que se requieran.
	# Parameters : Nombre de archivo, y tipo de acción a realizar. Cuando $Todo es igual a vacío, se verifica la integridad el archivo
	#Modifications:
	#			-Se agrega parámetro $Todo
	#			-Se quita opción multi items
	#			Dependiendo del parámetro $Todo se hará la acción. Cuando $Todo es igual a vacío, se verifica la integridad el archivo
	# Last Modified on: 10/15/08 09:49:38
	# Last Modified by: MCC C. Gabriel Varela S: Se arregla expresión regular para procesar fechas del tipo MMM.DD y para poner una fecha actual válida y se agrega tipo de envío "EXPRESS" y "L.A.DRIVER"
	# Last Modified on: 10/23/08 10:46:23
# Last Modified by: MCC C. Gabriel Varela S: Se descomentan líneas que hacen los updates y los insert al mostrar el mensaje Ship Date Updated and Tracking Number Added
# Last Modified on: 10/24/08 10:22:09
# Last Modified by: MCC C. Gabriel Varela S: Se hace que se cree una variable de fecha para que sea posible aplicarla en cost_inventory en lugar de la fecha actual (datetoapplygv)
# Last Modified on: 10/27/08 13:33:00
# Last Modified by: MCC C. Gabriel Varela S: Se hace que al mandar a llamar a cost_inventory se haga con la fecha apropiada
# Last Modified on: 11/06/08 12:25:59
# Last Modified by: MCC C. Gabriel Varela S: Modificaciones menores para procesar archivos
# Last Modified on: 11/07/08 16:13:36
# Last Modified by: MCC C. Gabriel Varela S: Se modifica el error que existía de que se actualizaran 2 productos para una misma orden
# Last Modified on: 11/17/08 10:35:22
# Last Modified by: MCC C. Gabriel Varela S: Se agrega tipo de envío GRND
# Last Modification by JRG : 03/12/2009 : Se agrega log
# Last Modified on: 06/08/09 13:04:52
# Last Modified by: MCC C. Gabriel Varela S: Se valida si el producto es set, de serlo regresa un error.

	my ($fname,$Todo) = @_;
	#GV Termina modificación 02jun2008
	#GV Inicia modificación 04jun2008
	my $vamsg="";
	#GV Termina modificación 04jun2008
	# Find shipping provider based on the filename
	#GV Inicia modificación 02jun2008: Quitar el tipo de archivo filetype, ya no se utilizará

	$columnsnerr=0;
	$numline=0;
	$datenerr=0;
	$daterows="---";
	#GV Inicia 03jun2008
	$columnsrows="---";
	$datatypeerr=0;
	$datatyperows="---";
	#GV Termina 03jun2008
	#GV Termina modificación 02jun2008: Quitar el tipo de archivo filetype, ya no se utilizará
	my ($dhl_err,$usps_err) = (0,0);
	if (open (TXT, "<$cfg{'path_shpfiles'}$fname")){
		my ($line,%rec,@ary,$num,$d);
		my (@c) = split(/,/,$cfg{'srcolors'});
		LINE: while (<TXT>){
			$line = $_;
			$line =~ s/\r|\n//g;
			@ary = split(/[\t]/,$line);
			#GV Inicia modificación 02jun2008: El número de columnas será fijo, siempre 6: Fecha, #Orden, Nombre del cliente, Forma de envío, Tracking, 9 digit ID products
			#GV Inicia 02jun2008
			$rec{'shpdate'}=$ary[0];
			$rec{'ID_orders'}=$ary[1];
			$rec{'customername'}=$ary[2];
			$rec{'ShpProvider'}=$ary[3];
			$rec{'trankingnum'}=$ary[4];
			$rec{'productid'}=$ary[5];
			$rec{'productid'} =~ s/\s//g;
			$done=$ary[3];
			#GV Termina 02jun2008
			$numline++;
			
			#################################################################################################
			#Comienzan validaciones##########################################################################
			#################################################################################################
			#################################################################################################
			#GV Inicia 09jun2008
			$bandidproductvalidation=0;
			#GV Termina 09jun2008
			
			if($Todo eq '')
			{
				#################################################################################################
				#Validación de número de columnas
				#Verifica que el número de columnas sea siempre 6
				#################################################################################################
				if($#ary ne 5){
					$columnsnerr++;
					$columnsrows.=", $numline";
				}
				
				#################################################################################################
				#Validación de fechas
				#Verifica de acuerdo a los tipo de formatos dados para fecha.
				#El año siempre tendrá que ser el presente o el anterior, y no puede ser la fecha superior a la de hoy
				#################################################################################################
				if($in{'datetype'}eq'american')#MM/DD/YYYY, ej. 06/02/2008 2 de junio de 2008 
				{
					#GV Inicia 03jun2008
					@tmpdate=split(/-|\/|:|\//, &get_sql_date(0),3);
					#GV Termina 03jun2008
					#GV Inicia modificación 09jun2008 Se hace válido también el año de dos cifras
					$rec{'shpdate'}=~ /(\d{1,2})[-|\/](\d{1,2})[-|\/](\d{2,4})$/;
					if($3<100){
						$ano3=2000+$3;
						$rec{'shpdate'}="$1-$2-$ano3";
					}else{
						$ano3=$3;
					}
					#GV Termina modificación 09jun2008
					#&cgierr("2094: $rec{'shpdate'}, $3/$2/$1, &date_to_unixtime('$3/$2/$1'), &date_to_unixtime(&get_sql_date)");
					#GV Inicia 03jun2008
					#GV Inicia modificación 09jun2008 Se cambia $3 por $ano3
					if($ano3<$tmpdate[2]-1)
					#GV Termina modificación 09jun2008
					{
						$datenerr++;
						$daterows.=", $numline";
					}
					#GV Inicia modificación 09jun2008 Se cambia $3 por $ano3
					$tmp0=&date_to_unixtime('$ano3/$1/$2');
					#GV Termina modificación 09jun2008 Se cambia $3 por $ano3
					$tmp1=&date_to_unixtime(&get_sql_date(0));
					#GV Inicia modificación 09jun2008 Se cambia $3 por $ano3
					$tmp2=&valid_date_sql("$ano3/$1/$2");
					if(&valid_date_sql("$ano3/$1/$2")eq 0 or $tmp0>$tmp1)
					#GV Termina modificación 09jun2008 Se cambia $3 por $ano3
					#GV Termina 03jun2008
					{
						#&cgierr("2094: $rec{'shpdate'}, $3/$1/$2, $tmp0, $tmp1, $tmp2");
						$datenerr++;
						$daterows.=", $numline";
					}
				}
				elsif($in{'datetype'}eq'latin')#DD/MM/YYYY, ej. 02/06/2008 2 de junio de 2008 
				{
					#GV Inicia 03jun2008
					@tmpdate=split(/-|\/|:|\//, &get_sql_date(0),3);
					#GV Termina 03jun2008
					#GV Inicia modificación 09jun2008 Se hace válido también el año de dos cifras
					$rec{'shpdate'}=~ /(\d{1,2})[-|\/](\d{1,2})[-|\/](\d{2,4})$/;
					if($3<100){
						$ano3=2000+$3;
						$rec{'shpdate'}="$1-$2-$ano3";
					}else{
						$ano3=$3;
					}
					#GV Termina modificación 09jun2008
					#GV Inicia 03jun2008
					#GV Inicia modificación 09jun2008 Se cambia $3 por $ano3
					if($ano3<$tmpdate[2]-1)
					#GV Termina modificación 09jun2008 Se cambia $3 por $ano3
					{
						$datenerr++;
						$daterows.=", $numline";
					}
					#GV Inicia modificación 09jun2008 Se cambia $3 por $ano3
					$tmp0=&date_to_unixtime('$ano3/$2/$1');
					#GV Termina modificación 09jun2008 Se cambia $3 por $ano3
					$tmp1=&date_to_unixtime(&get_sql_date(0));
					#GV Inicia modificación 09jun2008 Se cambia $3 por $ano3
					$tmp2=&valid_date_sql("$ano3/$2/$1");
					#GV Termina 03jun2008
					if(&valid_date_sql("$ano3/$2/$1")eq 0 or $tmp0>$tmp1)
					#GV Termina modificación 09jun2008 Se cambia $3 por $ano3
					{
						$datenerr++;
						$daterows.=", $numline";
					}
				}
				elsif($in{'datetype'} eq 'nothingtosee')
				{
					@tmpdate=split(/-|\/|:|\//, &get_sql_date(0),3);
					$rec{'shpdate'}=~ /(\w{3})\.(\d{1,2})/;
					if(lc($1) eq "jan" or lc($1) eq "ene"){
						$mm = "01";
					} elsif(lc($1) eq "feb"){
						$mm = "02";
					} elsif(lc($1) eq "mar"){
						$mm = "03";
					} elsif(lc($1) eq "apr" or lc($1) eq "abr"){
						$mm = "04";
					} elsif(lc($1) eq "may"){
						$mm = "05";
					} elsif(lc($1) eq "jun"){
						$mm = "06";
					} elsif(lc($1) eq "jul"){
						$mm = "07";
					} elsif(lc($1) eq "aug" or lc($1) eq "ago"){
						$mm = "08";
					} elsif(lc($1) eq "sep"){
						$mm = "09";
					} elsif(lc($1) eq "oct"){
						$mm = "10";
					} elsif(lc($1) eq "nov"){
						$mm = "11";
					} elsif(lc($1) eq "dec" or lc($1) eq "dic"){
						$mm = "12";
					}
					if(&valid_date_sql("$tmpdate[0]/$mm/$2")eq 0 or &date_to_unixtime("$tmpdate[0]/$mm/$2")>&date_to_unixtime(&get_sql_date(0)))
					{
#						$var=&valid_date_sql("$tmpdate[0]/$mm/$2");
#						$var1=&date_to_unixtime("$tmpdate[0]/$mm/$2");
#						$var2=&get_sql_date(0);
#						&cgierr("$var,$var1,$var2:$tmpdate[0]/$mm/$2");
						$datenerr++;
						$daterows.=", $numline";
					}
					else
					{
						#$in{'datetoapplygv'}="$tmpdate[0]/$mm/$2";
					}
				}
				
				#GV Inicia 03jun2008
				#################################################################################################
				#Validaciones de tipo de datos
				#################################################################################################
				#GV Inicia modificación 09jun2008 Se modifica la regexp para evaluar ID de productos
				if($rec{'productid'}!~/^\d{9}$/)
				{
					if($rec{'productid'}!~/^\d{3}-\d{3}-\d{3}$/)
					{
						$bandidproductvalidation=1;
					}
					else
					{
						$rec{'productid'}=~/^(\d{3})-(\d{3})-(\d{3})$/;
						$rec{'productid'}="$1$2$3";
					}
				}
				if($rec{'ID_orders'}!~/^\d\d+\d$/ or $rec{'ShpProvider'} !~ /GRND|L\.?A\.? ?DRIVER|express|ups|usps|fedex|dhl ground|dhl|local/i or length($rec{'trankingnum'})<1 or $bandidproductvalidation)#$rec{'productid'}!~/^\d{9}$/)#$rec{'productid'}!~/^\d\d+\d$/) $rec{'customername'}!~/^\w+\s\w+.$/ or 
				#GV Termina modificación 09jun2008
				{
					$datatypeerr++;
					$datatyperows.=", $numline";
				}
				#GV Termina 03jun2008
				next LINE;
			}
		}
		
		
		#GV Inicia 03jun2008
		if($Todo eq '')
		{
			$va{'message1'}.="Existieron errores al procesar el archivo. Se listan a continuación:<br>";
			if($columnsnerr>0 or $datenerr>0 or $datatypeerr>0)#Si existe un error de cualquier tipo
			{
				$in{'action'}='';
				#print "Content-type: text/html\n\n";
				$va{'message1'}.="Existen $columnsnerr errores relacionados con número de columnas incorrecto en las líneas: $columnsrows<br>" if($columnsnerr>0);
				$va{'message1'}.="Existen $datenerr errores relacionados con formato de fechas incorrecto en las líneas: $daterows<br>" if($datenerr>0);
				$va{'message1'}.="Existen $datatypeerr errores relacionados con tipo de datos incorrecto en las líneas: $datatyperows<br>" if($datatypeerr>0);
				#print &build_page('outbound_upflist.html');
				&updtracking_list;
				return;
			}else{
				print "Content-type: application/vnd.ms-excel\n";
				print "Content-disposition: attachment; filename=exportreport.csv\n\n";
				require "../../common/apps/cybersubs.cgi";
				if (open (TXT, "<$cfg{'path_shpfiles'}$fname")){
					XLINE: while (<TXT>){
						my ($line) = $_;
						$line =~ s/\r|\n//g;
						my (@ary) = split(/[\t]/,$line);
						#GV Inicia 02jun2008
						$rec{'shpdate'}=$ary[0];
						$rec{'ID_orders'}=$ary[1];
						$rec{'customername'}=$ary[2];
						$rec{'ShpProvider'}=$ary[3];
						$rec{'trankingnum'}=$ary[4];
						$rec{'productid'}=$ary[5];
						$rec{'productid'} =~ s/\s//g;
						$done=$ary[3];
			
						#################################################################################################
						#Validación de número de columnas
						#Verifica que el número de columnas sea siempre 6
						#################################################################################################
						if($#ary ne 5){
							print "$rec{'ID_orders'},$rec{'shpdate'},$rec{'trankingnum'},Invalid Rows Count\n";
							next XLINE;
						}
						
						#################################################################################################
						#Validación de fechas
						#Verifica de acuerdo a los tipo de formatos dados para fecha.
						#El año siempre tendrá que ser el presente o el anterior, y no puede ser la fecha superior a la de hoy
						#################################################################################################
						if($in{'datetype'} eq 'american'){
							@tmpdate=split(/-|\/|:|\//, &get_sql_date(0),3);
							$rec{'shpdate'}=~ /(\d{1,2})[-|\/](\d{1,2})[-|\/](\d{2,4})$/;
							if($3<100){
								$ano3=2000+$3;
								$rec{'shpdate'}="$1-$2-$ano3";
							}else{
								$ano3=$3;
							}
							if($ano3<$tmpdate[2]-1){
								print "$rec{'ID_orders'},$rec{'shpdate'},$rec{'trankingnum'},Invalid Date\n";
								next XLINE;
							}
							$tmp0=&date_to_unixtime('$ano3/$1/$2');
							$tmp1=&date_to_unixtime(&get_sql_date(0));
							$tmp2=&valid_date_sql("$ano3/$1/$2");
							if(&valid_date_sql("$ano3/$1/$2")eq 0 or $tmp0>$tmp1){
								print "$rec{'ID_orders'},$rec{'shpdate'},$rec{'trankingnum'},Invalid Date\n";
								next XLINE;
							}
							else
							{
								$in{'datetoapplygv'}="$ano3/$1/$2";
							}
						}elsif($in{'datetype'} eq 'latin'){
							@tmpdate=split(/-|\/|:|\//, &get_sql_date(0),3);
							$rec{'shpdate'}=~ /(\d{1,2})[-|\/](\d{1,2})[-|\/](\d{2,4})$/;
							if($3<100){
								$ano3=2000+$3;
								$rec{'shpdate'}="$1-$2-$ano3";
							}else{
								$ano3=$3;
							}
							if($ano3<$tmpdate[2]-1){
								print "$rec{'ID_orders'},$rec{'shpdate'},$rec{'trankingnum'},Invalid Date\n";
								next XLINE;
							}
							$tmp0=&date_to_unixtime('$ano3/$2/$1');
							$tmp1=&date_to_unixtime(&get_sql_date(0));
							$tmp2=&valid_date_sql("$ano3/$2/$1");
							if(&valid_date_sql("$ano3/$2/$1")eq 0 or $tmp0>$tmp1){
								print "$rec{'ID_orders'},$rec{'shpdate'},$rec{'trankingnum'},Invalid Date\n";
								next XLINE;
							}
							else
							{
								$in{'datetoapplygv'}="$ano3/$2/$1";
							}
						}elsif($in{'datetype'} eq 'nothingtosee'){
							@tmpdate=split(/-|\/|:|\//, &get_sql_date(0),3);
							$rec{'shpdate'} =~ /(\w{3})\.(\d{1,2})/;
							if(lc($1) eq "jan" or lc($1) eq "ene"){
								$mm = "01";
							} elsif(lc($1) eq "feb"){
								$mm = "02";
							} elsif(lc($1) eq "mar"){
								$mm = "03";
							} elsif(lc($1) eq "apr" or lc($1) eq "abr"){
								$mm = "04";
							} elsif(lc($1) eq "may"){
								$mm = "05";
							} elsif(lc($1) eq "jun"){
								$mm = "06";
							} elsif(lc($1) eq "jul"){
								$mm = "07";
							} elsif(lc($1) eq "aug" or lc($1) eq "ago"){
								$mm = "08";
							} elsif(lc($1) eq "sep"){
								$mm = "09";
							} elsif(lc($1) eq "oct"){
								$mm = "10";
							} elsif(lc($1) eq "nov"){
								$mm = "11";
							} elsif(lc($1) eq "dec" or lc($1) eq "dic"){
								$mm = "12";
							}
							if(&valid_date_sql("$tmpdate[0]/$mm/$2") eq 0 or &date_to_unixtime("$tmpdate[0]/$mm/$2")>&date_to_unixtime(&get_sql_date(0))){
								print "$rec{'ID_orders'},$rec{'shpdate'},$rec{'trankingnum'},Invalid Date\n";
								next XLINE;
							}
							else
							{
								$in{'datetoapplygv'}="$tmpdate[0]/$mm/$2";
							}
						}
						
						#################################################################################################
						#Validaciones de tipo de datos
						#################################################################################################
						if($rec{'ID_orders'}!~/^\d\d+\d$/ or $rec{'ShpProvider'} !~ /GRND|L\.?A\.? ?DRIVER|express|ups|usps|fedex|dhl ground|dhl|local/i or length($rec{'trankingnum'})<1){
							print "$rec{'ID_orders'},$rec{'shpdate'},$rec{'trankingnum'},Missing Info\n";
							next XLINE;
						}
			
			
						#################################################################################################
						##########          UPDATE 
						#################################################################################################
						($in{'rtest'}) and (next XLINE);
						my ($sth) = &Do_SQL("SELECT COUNT(*) FROM sl_import_log WHERE ID_import_log='$rec{'trankingnum'}' AND Type='$done';");
						if ($sth->fetchrow()>0){
							print "$rec{'ID_orders'},$rec{'shpdate'},$rec{'trankingnum'},Transaction Already been Imported\n";
							next XLINE;
						}else{
							if($rec{'productid'}!~/^\d{9}$/){
								if($rec{'productid'} =~ /^(\d{3})-(\d{3})-(\d{3})$/){
									$rec{'productid'}="$1$2$3";
								}else{
									print "$rec{'ID_orders'},$rec{'shpdate'},$rec{'trankingnum'},Invalid Product ID\n";
									next XLINE;
								}
							}
							$ids{1}[0] = $rec{'productid'};
							
							#Verifica si es set
							$isset=&load_name('sl_skus','ID_sku_products',$ids{1}[0],'IsSet');
							if($isset eq'Y')
							{
								print "$rec{'ID_orders'},$rec{'shpdate'},$rec{'trankingnum'},Invalid Product ID (it's a set)\n";
								next XLINE;
							}
							
							my $gvsth3 = &Do_SQL("SELECT Id_orders_products FROM sl_orders_products where ID_orders=$rec{'ID_orders'} and ID_products=$rec{'productid'}");
							$ids{1}[3] = $gvsth3->fetchrow;
							if ($ids{1}[3]){
								#print "$rec{'ID_orders'},,,run cost_inventory\n";
								$vamsg = &cost_inventory($in{'datetoapplygv'},$rec{'trankingnum'},$rec{'ShpProvider'},$rec{'ID_orders'},$in{'id_warehouses'},1,1,1,1,0,%ids);
								my $sth3;
								$sth3 = &Do_SQL("UPDATE sl_orders SET Status='Shipped' WHERE ID_orders='$rec{'ID_orders'}';");
								#&auth_logging('orders_updated',$rec{'ID_orders'});
								&auth_logging('opr_orders_stShipped',$rec{'ID_orders'});
								&status_logging($rec{'ID_orders'},'Shipped');

								$sth3 = &Do_SQL("UPDATE sl_orders_products SET Tracking='$rec{'trankingnum'}',ShpProvider='$rec{'ShpProvider'}',ShpDate='$in{'datetoapplygv'}' WHERE ID_orders='$rec{'ID_orders'}' AND Status='Active' and (isnull(Tracking)or Tracking='') and (isnull(ShpProvider)or ShpProvider='') and (isnull(ShpDate) or ShpDate='' or ShpDate='0000-00-00') limit 1;");
								&auth_logging('orders_products_updated',$rec{'ID_orders'});
								$sth3 = &Do_SQL("INSERT INTO sl_import_log SET ID_import_log='$rec{'trankingnum'}',Type='$rec{'ShpProvider'}',ID_orders='$rec{'ID_orders'}',IData='---',Date=CURDATE(),Time=CURTIME(),ID_admin_users='$usr{'id_admin_users'}';");
								&auth_logging('import_log_added',$rec{'trankingnum'});
								print "$rec{'ID_orders'},$rec{'shpdate'},$rec{'trankingnum'},Ship Date Updated and Tracking Number Added\n";
								next XLINE;
							}else{
								print "$rec{'ID_orders'},$rec{'shpdate'},$rec{'trankingnum'},Unable to Find the Product ID: $ids{1}[0]\n";
								next XLINE;
							}
						}
						print "last line\n";
					}
				}
				return;
			}
		}
		#GV Termina 03jun2008
		
		if (!$done or !$va{'searchresults'}){
			$err = &trans_txt("unknfiletype");
			$va{'searchresults'} .= qq|
			<tr>
				<td colspan='5' align='center'>$err $#ary</td>
			</tr>\n|;			
		}
	}else{
		$err = &trans_txt("err_openfile");
		$va{'searchresults'} .= qq|
			<tr>
				<td colspan='5' align='center'>$err $fname: $!</td>
			</tr>\n|;
	}
	if ($dhl_err > 0){
		$va{'message'} = trans_txt("invdhl").": $dhl_err";
	}elsif ($usps_err > 0){
		$va{'message'} = trans_txt("invusps").": $usps_err";
	}	
	print "Content-type: text/html\n\n";
	print &build_page('outbound_upflist_run.html');
}

sub outbound_uploaded {
# --------------------------------------------------------

	print "Content-type: text/html\n\n";
	print &build_page('outbound_uploaded.html');
}

sub report_order_day {
# --------------------------------------------------------

	print "Content-type: text/html\n\n";
	print &build_page('report_order_day.html');
}

sub report_order_day_list {
# --------------------------------------------------------
	$in{'reportdate'}=substr($in{'reportdate'},1,11);
	if(!$in{'reportdate'}){
		my ($sth) = &Do_SQL("SELECT CURDATE()as date");
		$rec = $sth->fetchrow_hashref();
		$in{'reportdate'}=$rec->{'date'};
	}
  
	my ($sth) = &Do_SQL("SELECT COUNT(*) FROM sl_orders WHERE Date = '$in{'reportdate'}' and Status='Shipped'");
	$cont_l=$sth->fetchrow;
	if ($cont_l>0){	
		my (@c) = split(/,/,$cfg{'srcolors'});
		(!$in{'nh'}) and ($in{'nh'}=1);
		$first = ($in{'nh'} - 1) * $usr{'pref_maxh'};	
		$va{'matches'} = $cont_l;			
		my($cont)=10;
		($va{'pageslist'},$qs) = &pages_list($in{'nh'},"/cgi-bin/mod/$usr{'application'}/admin",$va{'matches'},$usr{'pref_maxh'});
		$sth = &Do_SQL("SELECT * FROM sl_orders WHERE  Date = '$in{'reportdate'}' and  Status='Shipped' ORDER BY ID_orders DESC LIMIT $first,$usr{'pref_maxh'};");
		while ($rec = $sth->fetchrow_hashref){
		  $d = 1 - $d; $cont++;		  
		  $amount_price=$rec->{'OrderNet'}+$rec->{'OrderShp'}+$rec->{'OrderTax'};
		  
		  my ($sth1) = &Do_SQL("SELECT MIN(ShpDate) FROM `sl_orders_products` WHERE  id_orders = '$rec->{'ID_orders'}'");
		  $min_prod_ship=$sth1->fetchrow;		  		  
		  
		  my ($sth2) = &Do_SQL("SELECT SUM(Amount) FROM sl_orders_payments WHERE ID_orders = '$rec->{'ID_orders'}' and Status='Approved'");
		  $pay_amount=$sth2->fetchrow;
		  
		  my ($sth2) = &Do_SQL("SELECT SUM(SLTV_NetCost) FROM sl_orders_products,sl_products WHERE sl_orders_products.ID_orders = '$rec->{'ID_orders'}' and  RIGHT(sl_orders_products.id_products,6) = sl_products.id_products");
		  $sltv_cost=$sth2->fetchrow;
		  
		  my ($sth3) = &Do_SQL("SELECT COUNT(*) FROM sl_orders_payments WHERE ID_orders = '$rec->{'ID_orders'}'");
		  $number_pay=$sth3->fetchrow;
		if($number_pay==1){
			$pay_type="Regular";
		  }else{
		  	$pay_type="Flex. Pay";
		  }		  
			$page  .= qq|				
				<tr  bgcolor='$c[$d]'>
				  <td valign='top' nowrap>$min_prod_ship</td>										
					<td valign='top' nowrap>$rec->{'ID_orders'}</td>					  
				  <td nowrap valign='top'>|.&format_price($rec->{'OrderNet'}) .qq| </td>					  							  
				  <td nowrap valign='top'>|.&format_price($rec->{'OrderShp'}) .qq| </td>					  							  
				  <td nowrap valign='top'>|.&format_price($rec->{'OrderTax'}) .qq| </td>					  							  							  
				  <td nowrap valign='top'>|.&format_price($amount_price) .qq| </td>					  							  
				  <td nowrap valign='top'>|.&format_price($pay_amount) .qq| </td>					  							  
				  <td nowrap valign='top'>|.&format_price($sltv_cost) .qq| </td>					  							  
				  <td nowrap valign='top'>$pay_type </td>					  							  
				  <td align="right" nowrap valign='top' >$number_pay</td>							  
				</tr>\n|;
		}
	}else{
		$page = "<tr><td colspan='3' align='center'>".&trans_txt('egw_nomsgs')."</td></tr>";
	}
	$va{'searchresults'}=$page;
	
	print "Content-type: text/html\n\n";
	print &build_page('report_order_day_list.html');
}

sub load_ups_invdata {
# --------------------------------------------------------
# Created on: 11/14/2007 12:15PM
# Author: Rafael Sobrino
# Description : 
# Notes: 

	$filename = "../common/apps/uploads/temperr.csv";
	my ($count) = 0;
	my (@c) = split(/,/,$cfg{'srcolors'});

	if (open (FILE, "$filename")){
		while ($record = <FILE>){
			$d = 1 - $d;
			## add record to array
			my (@ary) = split(',', $record);
			$out .= "<tr bgcolor='$c[$d] 'onmouseover='m_over(this)' onmouseout='m_out(this)' onClick=\"trjump('/cgi-bin/mod/wms/admin?cmd=upsinv_record&view=$count')\">\n";
			## columns to be displayed
			$columns = "<td>$ary[9]</td><td>$ary[10]</td><td>$ary[16]</td><td>$ary[15]</td>\n";
			if ($ary[1] eq 0){
				$out .= "<td>$ary[0]</td><td>$ary[1]</td>$columns";
				$count++;
			}elsif ($ary[1] == ""){
				$out .= "<td>$ary[0]</td><td>---</td>$columns";
				$count++;
			}elsif ($ary[1] < 1000){
				$out .= "<td>$ary[0]</td><td>$ary[1]</td>$columns";
				$count++;
			}else{
				$out .= "<td>$ary[0]</td><td>$ary[1]</td>$columns";
				$count++;
			}
			$out .= "</tr>";
	 	}
		close(FILE);		
	}else{
		$va{'searchresults'} = "<tr><td colspan='6' align='center' class='stdtxterr'>".&trans_txt("upfile_err")."</td></tr>";
	}
	
	$va{'matches'} = $count;
	#($va{'pageslist'},$qs) = &pages_list($in{'nh'},"/cgi-bin/mod/$usr{'application'}/admin",$va{'matches'},$usr{'pref_maxh'});			
	$va{'searchresults'} = $out;
	
	print "Content-type: text/html\n\n";
	print &build_page('outbound_uploaded.html');	
}

sub upsinv_record {
# --------------------------------------------------------
# Created on: 11/15/2007 6:30PM
# Author: Rafael Sobrino
# Description : 
# Notes: 

	my ($count) = 0;	
	$filename = "../common/apps/uploads/temperr.csv";
	$va{'record_num'} = $in{'view'} + 1;
	if (open (FILE, "$filename")){
		while ($record = <FILE>){
			if ($count eq $in{'view'}){
				## add record to array				
				my (@ary) = split(',', $record);
				## display a --- when the field is empty
				foreach $value (@ary){
					if ($value eq ""){
						$value = "---";
					}
				}
				$va{'general'} = "<tr><td>$ary[0]</td><td>$ary[1]&nbsp;</td></tr>";
				$va{'shipto_contact'} = "<tr><td>$ary[2]&nbsp;</td><td>$ary[3]&nbsp;</td><td>$ary[8]&nbsp;</td></tr>";
				$va{'shipto_address'} = "<tr><td>$ary[4]</td><td>$ary[5]</td><td>$ary[6]</td><td>$ary[7]</td></tr>\n";
				$va{'ship_date'} = "<tr><td>$ary[9]</td><td>$ary[10]</td><td>$ary[11]</td><td>$ary[12]</td></tr>";
				$va{'ship_info'} = "<tr><td>$ary[13]</td><td>$ary[14]</td><td>$ary[15]</td><td>$ary[16]</td><td>$ary[17]</td></tr>";
				$va{'ship_other'} = "<tr><td colspan='2' valign='top'>$ary[18]</td><td valign='top'>$ary[19]</td><td valign='top'>$ary[20]</td><td valign='top'>$ary[21]</td></tr>";
				break;
			}
			$count++;
	 	}
		close(FILE);		
	}else{
		$va{'searchresults'} = "<tr><td colspan='6' align='center' class='stdtxterr'>".&trans_txt("upfile_err")."</td></tr>";
	}
	
	print "Content-type: text/html\n\n";
	print &build_page('upsinv_record.html');	
}


sub report_multi_order {
# --------------------------------------------------------
#
	if ($in{'action'}){
		my ($first_pay,$amount_price,$query,$k);		
		my (@xcols) = ('ID-ORDERS','ID-PRODUCT','Name','LAST','LAST2','PHONE1','PHONE2','ZIP','URB','CITY','STATE','ADDRES');
		$cont_l=0;
		my($tgr) = &Do_SQL("SELECT COUNT(*)
												FROM sl_orders,sl_orders_products 
												WHERE sl_orders.ID_orders=sl_orders_products.ID_orders AND
												      	1<(SELECT COUNT(*) 
												        	 FROM sl_orders_products 
												         	 WHERE Status='Active' AND                 
												                 sl_orders_products.ID_orders=sl_orders.ID_orders) AND
												      sl_orders_products.Status='Active' AND 
												      sl_orders_products.ID_products>1000000 AND 
												      sl_orders.Status='Processed' AND
												      sl_orders.shp_type<>2       
												      ORDER BY sl_orders.id_orders,sl_orders_products.ID_products");	  
		$cont_l=$tgr->fetchrow;				
    
		if ($cont_l>0){	               
			my ($mdate) = &get_date();
			$mdate =~ s/-//g;
			print "Content-type: application/vnd.ms-excel\n";
			print "Content-disposition: attachment; filename=multi_order_$cont_l.csv\n\n";			      
			my ($sthd) = &Do_SQL("SELECT sl_orders.ID_orders,
		         								sl_orders_products.ID_products,
		         								sl_orders.Shp_name,
		         								sl_orders.Shp_Zip,
		         								sl_orders.Shp_Urbanization,
		         								sl_orders.Shp_City,
		         								sl_orders.Shp_State,
		         								sl_orders.Shp_Address1,
		         								sl_orders.Shp_Address2,
		         								sl_orders.Shp_Address3,
		         								sl_orders.ID_customers
														FROM sl_orders,sl_orders_products 
														WHERE sl_orders.ID_orders=sl_orders_products.ID_orders AND
														      	1<(SELECT COUNT(*) 
														        	 FROM sl_orders_products 
														         	 WHERE Status='Active' AND                 
														                 sl_orders_products.ID_orders=sl_orders.ID_orders) AND
														      sl_orders_products.Status='Active' AND 
														      sl_orders_products.ID_products>1000000 AND 
														      sl_orders.Status='Processed' AND
														      sl_orders.shp_type<>2       
														      ORDER BY sl_orders.ID_orders,sl_orders_products.ID_products");				
			while ($rec = $sthd->fetchrow_hashref()){		
				my (@cols);
				my ($prod_cost);				
				$cols[0] = $rec->{'ID_orders'};										
				$cols[1] = &format_sltvid($rec->{'ID_products'});
				my ($sth1) = &Do_SQL("SELECT FirstName,LastName1,LastName2,Phone1,Phone2 FROM sl_customers WHERE ID_customers='$rec->{'ID_customers'}';");
				my ($tmp) = $sth1->fetchrow_hashref();
				if ($rec->{'shp_name'}){
					($cols[2],$cols[3]) = split(/\s+/,$rec->{'shp_name'},2);
				}else{
					$cols[2] = $tmp->{'FirstName'};
					$cols[3] = $tmp->{'LastName1'};
				}				
				$cols[4] = $tmp->{'LastName2'};
				$cols[5] = $tmp->{'Phone1'};
				$cols[6] = $tmp->{'Phone2'};
				
				$cols[7] = $rec->{'Shp_Zip'};
				$cols[9] = $rec->{'Shp_Urbanization'};
				$cols[9] = $rec->{'Shp_City'};
				$cols[10] = substr($rec->{'Shp_State'},0,2);
				$cols[11] = $rec->{'Shp_Address1'} . ' ' . $rec->{'Shp_Address2'} . ' ' . $rec->{'Shp_Address3'};				
				
				print '"'.join('","', @cols)."\"\n";;
			}		
			return;
		}else{
			$va{'message'} = &trans_txt('novalues');	
			print "Content-type: text/html\n\n";
			print &build_page('toprint_msg.html');
			return;	
		}
	}	
}

sub upc {
# --------------------------------------------------------
	if ($in{'action'}){
		$in{'upc'} =~ s/\n|\r|//g;
		my ($odd, $even);
		if ($in{'sltv_id'}){
			$in{'upc'} = '44'.$in{'id_products'};
			for (0..4){
				$odd += substr($in{'upc'},$_*2,1);
				$even += substr($in{'upc'},$_*2+1,1);
			}
			$odd += substr($in{'upc'},10,1);
			if (($odd*3+$even)%10 == 0){
				$in{'upc'} .= '0';
			}else{
				$in{'upc'} .= (10-($odd*3+$even)%10);
			}
		}
		if (!$in{'upc'}){
			$error{'upc'} = &trans_txt('required');	
			++$err;
		}elsif(length($in{'upc'}) ne 12){
			$error{'upc'} = &trans_txt('invalid');	
			++$err;
		}else{
			my ($odd, $even);
			my ($sth) = &Do_SQL("SELECT COUNT(*) FROM sl_skus WHERE UPC='$in{'upc'}' AND ID_sku_products<>'$in{'id_products'}'");
			if ($sth->fetchrow ne 0){
				$error{'upc'} = &trans_txt('repeated');	
				++$err;
			}else{
				# ---- &cgierr("rafa:$in{'sltv_id'}");
				#In the UPC-A system, the check digit is calculated as follows:
				#1. Add the digits in the odd-numbered positions (first, third, fifth, etc.) together and multiply by three.
				#2. Add the digits in the even-numbered positions (second, fourth, sixth, etc.) to the result.
				#3. Subtract the result modulo 10 from ten.
				for (0..4){
					$odd += substr($in{'upc'},$_*2,1);
					$even += substr($in{'upc'},$_*2+1,1);
				}
				$odd += substr($in{'upc'},10,1);
				if (($odd*3+$even)%10 == 0 and substr($in{'upc'},11,1) ne 0){
					$error{'upc'} = &trans_txt('invalid');
					++$err;
				}elsif((10-($odd*3+$even)%10) ne substr($in{'upc'},11,1) and ($odd*3+$even)%10 ne 0){
					$error{'upc'} = &trans_txt('invalid');
					++$err;
				}
			}
		}
		if (!$in{'id_products'}){
			$error{'id_products'} = &trans_txt('required');	
			++$err;
		}else{
			my ($sth) = &Do_SQL("SELECT COUNT(*) FROM sl_skus WHERE ID_sku_products='$in{'id_products'}'");
			if ($sth->fetchrow ne 1){
				$error{'id_products'} = &trans_txt('invalid');	
				++$err;
			}
		}
		if ($err>0){
			$va{'message'} = &trans_txt('reqfields');
		}else{
			$in{'db'} = 'sl_products';
			my ($sth) = &Do_SQL("SELECT UPC FROM sl_skus WHERE ID_sku_products='$in{'id_products'}'");
			my ($matches) = $sth->fetchrow;
			if ($in{'confirm'}){
				my ($sth) = &Do_SQL("UPDATE sl_skus SET UPC='$in{'upc'}' WHERE ID_sku_products='$in{'id_products'}'");
				$va{'message'} = &trans_txt('upc_updated').': '.$in{'upc'};
				&auth_logging("upc_updated",substr($in{'id_products'},3,6));
				delete($in{'id_products'});
				delete($in{'upc'});
				
			}elsif($matches>0){
				$va{'message'} = &trans_txt('confirm');
				$va{'confirm'} = qq|<input type="checkbox" class="checkbox" name="confirm" value="on">| . $va{'message'} . "<br><br>";
			}else{
				my ($sth) = &Do_SQL("UPDATE sl_skus SET UPC='$in{'upc'}' WHERE ID_sku_products='$in{'id_products'}'");
				$va{'message'} = &trans_txt('upc_added').': '.$in{'upc'};
				&auth_logging("upc_added",substr($in{'id_products'},3,6));
				delete($in{'id_products'});
				delete($in{'upc'});
			}
		}
	}
	print "Content-type: text/html\n\n";
	print &build_page('upc.html');
}

sub bulkprint {
# --------------------------------------------------------

# Author: Unknown
# Created on: Unknown
# Last Modified on: 08/26/2008
# Last Modified by: Jose Ramirez Garcia
# Description : 
# Forms Involved: 
# Parameters : 
# Notes:
# 08/21/2008 the headers for excel were modified and the format to print in file
# 08/26/2008 the headers for excel were modified to take old/new format
# 10/24/2008 added fedex format in ds general report (RB)
# Last Modified RB: 09/11/09  13:46:09 -- Se agrego llamada a la funcion &build_export_setup(sub.base_sltv) que genera un archivo de exportacion basado en configuracion setup.cfg|general.cfg
# Last Modified on: 09/11/09 17:35:10
# Last Modified by: MCC C. Gabriel Varela S: Se habilita para preorders
# Last Modified by RB on 03/31/2011 05:38:41 PM : Se agrega validacion para ordenes Allnatpro. 


	my (@ids);
	my $prefix="orders";
	$prefix=$in{'prefix'}if $in{'prefix'};
	if ($in{'action'}){
		if ($in{'id_orders_bulk'}){
			$in{'db'} = "sl_$prefix";
			my (@ary) = split(/\s+|,|\n|\t/,$in{'id_orders_bulk'});
			for my $i(0..$#ary){
				my ($sth) = &Do_SQL("SELECT COUNT(*) FROM sl_$prefix WHERE ID_$prefix='".&filter_values($ary[$i])."';");
				if ($sth->fetchrow()>0){
					if ($in{'type'} eq 'opr_packinglist' or $in{'type'} eq 'opr_ppackinglist'){
						my ($sth) = &Do_SQL("SELECT ID_".$prefix."_products FROM sl_".$prefix."_products WHERE ID_$prefix='".&filter_values($ary[$i])."' AND Status='Active' AND (ISNULL(Tracking) OR Tracking ='');");
						while ($id = $sth->fetchrow()){
							push(@ids,"$ary[$i],$id");
						}
					}else{
						push(@ids,$ary[$i]);
					}
				}
			}
			if ($#ids==-1){
				$va{'message'} = &trans_txt('toprn_none');
			}
		}else{
			$va{'message'} = &trans_txt('toprn_none');
		}
	}
	
	if ($in{'action'} and $va{'message'}){
		print "Content-type: text/html\n\n";
		print &build_page('toprint_msg.html');
	
	
	}elsif($in{'action'} and $in{'page'}=~/^exportfile.*/){
		$in{'prefix'} ='orders'	if !$in{'prefix'};
		#### Nueva funcion basada en setup.cfg de wms
		&build_export_setup($in{'prefix'},@ids);
		
	}elsif($in{'action'} and ($in{'page'}eq 'exports_general' or $in{'page'} eq 'exports_fedex')){	#new format
		my (%lines);	
		print "Content-type: application/vnd.ms-excel\n";
		print "Content-disposition: attachment; filename=shoplatinotv".&get_date().".csv\n\n";
		
		if($in{'page'} eq 'exports_general'){
				print " Order , ID , Model , Ship Date , First Name , Last Name , Contact Number1 , Contact Number2 , Zip code , City , State , Street , Tracking Information , Comment ";
			}elsif($in{'page'} eq 'exports_fedex'){
				print " Order , ID , Model , Ship Date , Name, Contact Number1 , Contact Number2 , Zip code , City , State , Street , Tracking Information , Comment ";
			}
		print "\r\n";
		
		for my $i(0..$#ids){
			my ($sth) = &Do_SQL("SELECT * FROM sl_orders,sl_orders_products WHERE sl_orders.ID_orders=sl_orders_products.ID_orders AND sl_orders.ID_orders='$ids[$i]' AND LEFT(ID_products,1) <> '6' ");
			while ($rec = $sth->fetchrow_hashref()){
				my (@cols);
				$cols[0] = $rec->{'ID_orders'};
				$cols[1] = &format_sltvid($rec->{'ID_products'});
				$cols[2] = &load_name('sl_products','ID_products',substr($rec->{'ID_products'},3),'Model');
				$cols[3] = $rec->{'ShpDate'};
				my ($sth2) = &Do_SQL("SELECT * FROM sl_customers WHERE ID_customers='$rec->{'ID_customers'}';");
				my ($tmp) = $sth2->fetchrow_hashref();
				if($in{'page'} eq 'exports_general'){
					$cols[4] = $tmp->{'FirstName'};
					$cols[5] = $tmp->{'LastName1'};
					$cols[6] = $tmp->{'Phone1'};
					$cols[7] = $tmp->{'Phone2'};
					$cols[8] = $rec->{'shp_Zip'};
					$cols[9] = $rec->{'shp_City'};
					$cols[10] = substr($rec->{'shp_State'},0,2);
					$cols[11] = $rec->{'shp_Address1'} . ' ' . $rec->{'shp_Address2'} . ' ' . $rec->{'shp_Address3'};
					$cols[12] = $rec->{'Tracking'} . ' ' . $rec->{'ShpProvider'};
					$cols[13] = $rec->{'shp_Notes'};
					$lines{"$cols[5],$cols[4]"} = '"'.join('","', @cols)."\"\r\n";
				}else{
					$cols[4] = "$tmp->{'LastName1'} $tmp->{'FirstName'}";
					$cols[5] = $tmp->{'Phone1'};
					$cols[6] = $tmp->{'Phone2'};
					$cols[7] = $rec->{'shp_Zip'};
					$cols[8] = $rec->{'shp_City'};
					$cols[9] = substr($rec->{'shp_State'},0,2);
					$cols[10] = $rec->{'shp_Address1'} . ' ' . $rec->{'shp_Address2'} . ' ' . $rec->{'shp_Address3'};
					$cols[11] = $rec->{'Tracking'} . ' ' . $rec->{'ShpProvider'};
					$cols[12] = $rec->{'shp_Notes'};
					$lines{"$cols[4]"} = '"'.join('","', @cols)."\"\r\n";
				}
			}
		}


		if ($in{'sort'}){
			foreach $key (sort { lc($a) cmp lc($b) } keys %lines){
				print $lines{$key};
			}
		}else{
			foreach $key (keys %lines){
				print $lines{$key};
			}
		}
	}elsif($in{'action'} and $in{'page'}eq 'exports_inova'){	#old format
		my (%lines);	
		my (@xcols) = ('Order','Ship Date','First Name','Last Name','Contact Number1','Contact Number2','Zip code','City','State','Street','Tracking Information','Comment');
		print "Content-type: application/vnd.ms-excel\n";
		print "Content-disposition: attachment; filename=shoplatinotv".&get_date().".csv\n\n";
		
		for my $i(0..$#ids){
			my ($sth) = &Do_SQL("SELECT * FROM sl_orders,sl_orders_products WHERE sl_orders.ID_orders=sl_orders_products.ID_orders AND sl_orders.ID_orders='$ids[$i]' ");
			while ($rec = $sth->fetchrow_hashref()){
				my (@cols);
				$cols[2] = "$rec->{'ID_orders'}-$rec->{'ID_orders_products'}";
				my ($sth2) = &Do_SQL("SELECT * FROM sl_customers WHERE ID_customers='$rec->{'ID_customers'}';");
				my ($tmp) = $sth2->fetchrow_hashref();
				$cols[28] = $tmp->{'FirstName'};
				$cols[29] = $tmp->{'LastName1'};
				$cols[30] = $tmp->{'LastName2'};
				$cols[31] = $tmp->{'Phone1'};
				$cols[32] = $tmp->{'Phone2'};
				
				$cols[33] = $rec->{'shp_Zip'};
				$cols[35] = $rec->{'shp_City'};
				$cols[36] = substr($rec->{'shp_State'},0,2);
				$cols[37] = $rec->{'shp_Address1'} . ' ' . $rec->{'shp_Address2'} . ' ' . $rec->{'shp_Address3'};
				$cols[39] = $rec->{'shp_Notes'};
				$lines{"$cols[3],$cols[2]"} = '"'.join('","', @cols)."\"\n";
			}
		}

		if ($in{'sort'}){
			foreach $key (sort { lc($a) cmp lc($b) } keys %lines){
				print $lines{$key};
			}
		}else{
			foreach $key (keys %lines){
				print $lines{$key};
			}
		}
	}elsif($in{'action'}){
		my ($page,%rec);
		&html_print_headers ('Printing.....');
		print qq|
	<body onload="prn()" style="background-color:#FFFFFF">
<!--
<object id=factory viewastext style="display:none"
classid="clsid:1663ed61-23eb-11d2-b92f-008048fdd814"
  codebase="/ScriptX.cab#Version=5,60,0,375">
</object>
-->
<script defer>
function prn() {
	window.print()
	return false;
}

</script>\n|;
		$in{'db'} = 'sl_orders';
		$in{'toprint'}=1;
		$cmd = $in{'type'};
		#opr_finance
		for my $i(0..$#ids){
			&load_cfg('sl_orders');
			if ($ids[$i]){
				if ($in{'page'} eq 'invoiceblank'){
					$cmd = 'invoices';
				}else{
					$cmd = 'pinvoices';
				}			
				$in{'id_orders'} = $ids[$i];
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
					
					my ($func) = 'view_' . $cmd . $xcmd;
					if (defined &$func){
						&$func;
					}
					
					print &build_page($cmd . $xcmd .'_print.html');
					#print &html_print_record(%rec);
				}
			}
			if ($ids[$i+1]>0){
				print "<DIV STYLE='page-break-before:always'></DIV>";
			}
		}
		print qq|</body>\n</html>\n|;

	}else{
		print "Content-type: text/html\n\n";
		print &build_page('bulkprint.html');		
	}
}


sub retpackinglist_orders {
# --------------------------------------------------------	
# Created on: Unknown
# Last Modified on: 07/07/2008
# Last Modified by: Jose Ramirez Garcia
# Author: Unknown
# Description : Modified to select the orders will be modified
# Parameters :
## Fulfillment Type
# Last Modified on: 10/07/08 11:11:39
# Last Modified by: MCC C. Gabriel Varela S: Se agrega columna de número de pagos para la orden y se toma en cuenta partial shipment
# Last Modified on: 10/08/08 11:59:45
# Last Modified by: MCC C. Gabriel Varela S: Se hace que se muestren los productos de la orden
# Last Modified on: 05/22/09 12:19:36
# Last Modified by: MCC C. Gabriel Varela S: Se cambia consulta para optimizar. Saludos.


	$ordstatus="'Shipped'";
	$prdstatus = 'For ReShip';

	if ($in{'id_warehouses'}){	
		#### Assign to warehouses_batches
		my ($err);

		my $sth = &Do_SQL("SELECT COUNT(*) FROM sl_warehouses WHERE ID_warehouses=".int($in{'id_warehouses'})." AND ID_warehouses > 0 ");    
	    if ($sth->fetchrow == 0){	
			$error{'id_warehouses'} = &trans_txt('invalid');
	    	++$err;
	    }

		if($in{'id_warehouses'} and !$err) {
									
			if ($in{'action'}){
				 					
				$va{'id_warehouses_batches'}='';
				my $status_warehouses_batches = 0;				
				my $new = $in{'id_warehouses'};
				$va{'id_warehouses_batches'} = &create_warehouse_batch_file($new);
				
				if($va{'id_warehouses_batches'}){
				
					if($in{'ordersselected'} && $in{'ordersselected'} !~ m/,,.*/){
						chop($in{'ordersselected'});
					}

					####TDC by warehouse
					my $query = "SELECT 
									sl_orders.ID_orders
									, sl_orders_products.ID_orders_products
								FROM sl_orders INNER JOIN sl_returns USING(ID_orders) 
							    INNER JOIN sl_orders_products USING(ID_orders)
							    LEFT JOIN  sl_warehouses_batches_orders
									ON sl_warehouses_batches_orders.ID_orders_products = sl_orders_products.ID_orders_products 
									AND sl_warehouses_batches_orders.Status IN ('In Fulfillment','Shipped','In Transit'/*,'Returned'*/)
							    WHERE 1
							    	/*AND Ptype != 'COD'*/
									AND sl_orders.Status = 'Shipped'
									AND StatusPrd IN('For Exchange','For Re-Ship')
									AND sl_orders_products.Status IN ('Exchange','Undeliverable','ReShip') 
									AND sl_orders_products.SalePrice >= 0
									AND (PackingListStatus != 'Done' OR ISNULL(PackingListStatus))
									AND sl_returns.Status IN ('Resolved','Pending Payments','Pending Refunds')
									AND sl_orders_products.SalePrice >= 0
									AND sl_orders_products.ID_products BETWEEN 100000000 AND 399999999
									AND sl_warehouses_batches_orders.ID_orders_products IS NULL
									AND IF(
										merAction = 'Exchange'
											, (
												1 > (SELECT COUNT(*) FROM sl_orders_payments WHERE ID_orders = sl_returns.ID_orders AND Status NOT IN ('Financed','Credit','Void','Order Cancelled','Cancelled') AND Captured <> 'Yes' AND (CapDate IS NULL OR CapDate = '0000-00-00') )
												OR 1 <= (SELECT COUNT(*) FROM sl_orders_notes WHERE ID_orders = sl_returns.ID_orders AND sl_orders_notes.Date > sl_returns.Date AND Type = 'Exchange Paid')
											)
											, 1
									)
								GROUP BY sl_orders_products.ID_orders_products";


					my ($sth) = &Do_SQL($query);
				    if ($sth->rows() > 0){

				    	my $id_orders_base = 0;
						
						while (my ($this_id_orders, $this_id_orders_products) = $sth->fetchrow() ){
							
							### Insert Batch Orders Products Lines
							$Query = "SELECT COUNT(*) FROM sl_warehouses_batches_orders WHERE ID_orders_products = '$this_id_orders_products' AND Status IN ('In Fulfillment','Shipped','In Transit');";
							($sth2) = &Do_SQL($Query);
							my ($count) = $sth2->fetchrow();
							
							if(!$count){

								$Query = "INSERT INTO sl_warehouses_batches_orders SET ID_warehouses_batches = '".$va{'id_warehouses_batches'}."', ID_orders_products = '$this_id_orders_products', Status='In Fulfillment', Date=CURDATE(),Time=CURTIME(),ID_admin_users='$usr{'id_admin_users'}'; ";
								($sth3) = &Do_SQL($Query);
								$status_warehouses_batches =1;
								
								if($this_id_orders ne $id_orders_base){

									$in{'db'} = 'sl_orders';
									## Nota orden enviada en batch		

									&add_order_notes_by_type($this_id_orders,&trans_txt('order_batchadded')." $va{'id_warehouses_batches'}","High");
									&auth_logging('order_batchadded', $this_id_orders);
									$id_orders_base = $this_id_orders;

								}

							}					
							
						} 

					 	if($status_warehouses_batches){

					 		my $Query = "UPDATE sl_warehouses_batches SET Status='Assigned' WHERE ID_warehouses_batches=$va{'id_warehouses_batches'};";
							my ($sth) = &Do_SQL($Query);
							$in{'db'}='sl_warehouses_batches';
							&auth_logging('warehouses_batches_items_add',$va{'id_warehouses_batches'});
							delete($in{'db'});

							delete($in{'action'});
							delete($in{'id_warehouses'});
							delete($in{'ordersselected'});
							$va{'message'}=&trans_txt("warehouses_batches_assigned") . ": $va{'id_warehouses_batches'}";

					 	}
						 
					}
								 
				}else{
					++$err;
					$error{'id_warehouses'}=&trans_txt('warehouses_batches_invalid');	
				}

			}
 
		}else{
			++$err;
			$error{'id_warehouses'}=&trans_txt('required');
		}

	}

		
	$va{'matches'} = 1;
	$va{'pageslist'} = 1;
	
	my ($sth) = &Do_SQL("SELECT COUNT(DISTINCT sl_orders.ID_orders) 
						FROM sl_orders INNER JOIN sl_returns USING(ID_orders) 
					    INNER JOIN sl_orders_products USING(ID_orders)
					    LEFT JOIN  sl_warehouses_batches_orders
							ON sl_warehouses_batches_orders.ID_orders_products = sl_orders_products.ID_orders_products 
							AND sl_warehouses_batches_orders.Status IN ('In Fulfillment','Shipped','In Transit'/*,'Returned'*/)
					    WHERE 1
					    	/*AND Ptype != 'COD'*/
							AND sl_orders.Status = 'Shipped'
							AND StatusPrd IN('For Exchange','For Re-Ship')
							AND sl_orders_products.Status IN ('Exchange','Undeliverable','ReShip') 
							AND sl_orders_products.SalePrice >= 0
							AND (PackingListStatus != 'Done' OR ISNULL(PackingListStatus))
							AND sl_returns.Status IN ('Resolved','Pending Payments','Pending Refunds')
							AND sl_orders_products.SalePrice >= 0
							AND sl_orders_products.ID_products BETWEEN 100000000 AND 399999999
							AND sl_warehouses_batches_orders.ID_orders_products IS NULL
							AND IF(
									merAction = 'Exchange'
										, (
											1 > (SELECT COUNT(*) FROM sl_orders_payments WHERE ID_orders = sl_returns.ID_orders AND Status NOT IN ('Financed','Credit','Void','Order Cancelled','Cancelled') AND Captured <> 'Yes' AND (CapDate IS NULL OR CapDate = '0000-00-00') )
											OR 1 <= (SELECT COUNT(*) FROM sl_orders_notes WHERE ID_orders = sl_returns.ID_orders AND sl_orders_notes.Date > sl_returns.Date AND Type = 'Exchange Paid')
										)
										, 1
								);");
	$va{'matches'} = $sth->fetchrow;
	
	if ($va{'matches'}>0){
		(!$in{'nh'}) and ($in{'nh'}=1);
		$first = ($in{'nh'} - 1) * $usr{'pref_maxh'};			
		($va{'pageslist'},$qs) = &pages_list($in{'nh'},"/cgi-bin/mod/$usr{'application'}/admin",$va{'matches'},$usr{'pref_maxh'});
		my (@c) = split(/,/,$cfg{'srcolors'});

		$sth = &Do_SQL("SELECT sl_orders.*, meraction
						FROM sl_orders INNER JOIN sl_returns USING(ID_orders) 
					    INNER JOIN sl_orders_products USING(ID_orders)
					    LEFT JOIN  sl_warehouses_batches_orders
							ON sl_warehouses_batches_orders.ID_orders_products = sl_orders_products.ID_orders_products 
							AND sl_warehouses_batches_orders.Status IN ('In Fulfillment','Shipped','In Transit'/*,'Returned'*/)
					    WHERE 1
					    	/*AND Ptype != 'COD'*/
							AND sl_orders.Status = 'Shipped'
							AND StatusPrd IN('For Exchange','For Re-Ship')
							AND sl_orders_products.Status IN ('Exchange','Undeliverable','ReShip') 
							AND sl_orders_products.SalePrice >= 0
							AND (PackingListStatus != 'Done' OR ISNULL(PackingListStatus))
							AND sl_returns.Status IN ('Resolved','Archived','Pending Payments','Pending Refunds')
							AND sl_orders_products.SalePrice >= 0
							AND sl_orders_products.ID_products BETWEEN 100000000 AND 399999999
							AND sl_warehouses_batches_orders.ID_orders_products IS NULL
							AND IF(
									merAction = 'Exchange'
										, (
											1 > (SELECT COUNT(*) FROM sl_orders_payments WHERE ID_orders = sl_returns.ID_orders AND Status NOT IN ('Financed','Credit','Void','Order Cancelled','Cancelled') AND Captured <> 'Yes' AND (CapDate IS NULL OR CapDate = '0000-00-00') )
											OR 1 <= (SELECT COUNT(*) FROM sl_orders_notes WHERE ID_orders = sl_returns.ID_orders AND sl_orders_notes.Date > sl_returns.Date AND Type = 'Exchange Paid')
										)
										, 1
								)
						GROUP BY sl_orders.ID_orders
						ORDER BY meraction, sl_orders.ID_orders DESC 
						LIMIT $first,$usr{'pref_maxh'}");

		my $sth1,$rec1,$cont,$prodcad;
		while ($rec = $sth->fetchrow_hashref){

			$d = 1 - $d;
			$cont=0;
			my $id_orders_string = $rec->{'ID_orders'};
			$id_orders_string .= 'R' if $rec->{'meraction'} eq 'ReShip';
			$id_orders_string .= 'CF' if $rec->{'meraction'} eq 'Exchange';


			$va{'searchresults'} .= "<tr bgcolor='$c[$d]' onmouseover='m_over(this)' onmouseout='m_out(this)'>\n";
			$va{'searchresults'} .= "  <td class='smalltext' valign='top' align='center'><input type='checkbox' class='checkbox' id='chkor_$rec->{'ID_orders'}' name='id_ordersttia' value='$rec->{'ID_orders'}' onclick='chk_ord($rec->{'ID_orders'})'>&nbsp;</td>\n";
			$va{'searchresults'} .= "  <td class='smalltext' valign='top' align='center'><a href='#' onClick=\"trjump('/cgi-bin/mod/wms/dbman?cmd=opr_orders&view=$rec->{'ID_orders'}&check_status=1')\">$id_orders_string</a></td>\n";
			$va{'searchresults'} .= "  <td class='smalltext' valign='top'>$rec->{'Date'}</td>\n";
			$va{'searchresults'} .= "  <td class='smalltext' valign='top'>$rec->{'CompanyName'} ".&load_db_names('sl_customers','ID_customers',$rec->{'ID_customers'},"[FirstName] [LastName1]")."</td>\n";
			$va{'searchresults'} .= "  <td class='smalltext' valign='top'>$rec->{'NumPay'}</td>\n";
			$va{'searchresults'} .= "</tr>\n";

			$sth1=&Do_SQL("SELECT ID_orders,sl_orders_products.ID_products, Name, Model
						FROM sl_orders_products
						INNER JOIN sl_products ON (right(sl_orders_products.ID_products,6)=sl_products.ID_products)
						WHERE ID_orders = '$rec->{'ID_orders'}' AND sl_orders_products.status IN ('ReShip','Exchange')");

			while($rec1=$sth1->fetchrow_hashref) {

				$va{'searchresults'} .= "<tr bgcolor='$c[$d]' onmouseover='m_over(this)' onmouseout='m_out(this)'>\n";
				$cont++;
				$va{'searchresults'} .= "  <td class='smalltext' valign='top'></td>\n";
				
				if($cont==1){
					$prodcad="Products: ";
				}else{
					$prodcad="";
				}

				$va{'searchresults'} .= "  <td class='smalltext' valign='top'>$prodcad</td>\n";
				$va{'searchresults'} .= "  <td class='smalltext' valign='top' colspan='3'>".&format_sltvid($rec1->{'ID_products'}).": $rec1->{'Name'}/$rec1->{'Model'}</td>\n";
				$va{'searchresults'} .= "</tr>\n";

			}
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
	print &build_page('retpackinglist_orders.html');
}



sub retpackinglist_zones {
# --------------------------------------------------------	
# Created on: Carlos Haas
# Last Modified on: 7/30/2013 12:13:41 PM
# Author: Unknown
# Description : 
# Parameters :

	$in{'id_zones'}=int($in{'id_zones'});

	if ($in{'id_zones'}>0){
		&retpackinglist_zones_to_batch;
		return;
	}

	$va{'matches'} = 1;
	$va{'pageslist'} = 1;
	
	my ($sth) = &Do_SQL("SELECT COUNT(DISTINCT sl_orders.ID_orders) FROM 
				sl_orders INNER JOIN sl_returns USING(ID_orders) 
			    INNER JOIN sl_orders_products USING(ID_orders)
			    LEFT JOIN  sl_warehouses_batches_orders
					ON sl_warehouses_batches_orders.ID_orders_products = sl_orders_products.ID_orders_products 
					AND sl_warehouses_batches_orders.Status IN ('In Fulfillment','Shipped','In Transit'/*,'Returned'*/)
			    WHERE 1
			    	/*AND Ptype != 'COD'*/
					AND sl_orders.Status = 'Shipped'
					AND StatusPrd IN('For Exchange','For Re-Ship')
					AND sl_orders_products.Status IN ('Exchange','Undeliverable','ReShip') 
					AND sl_orders_products.SalePrice >= 0
					AND (PackingListStatus != 'Done' OR ISNULL(PackingListStatus))
					AND sl_returns.Status IN ('Resolved','Pending Payments','Pending Refunds')
					AND sl_returns.merAction IN('Exchange','ReShip')
					AND sl_orders_products.SalePrice >= 0
					AND sl_orders_products.ID_products BETWEEN 100000000 AND 399999999
					AND sl_warehouses_batches_orders.ID_orders_products IS NULL
					AND IF(
							merAction = 'Exchange'
								, (
									1 > (SELECT COUNT(*) FROM sl_orders_payments WHERE ID_orders = sl_returns.ID_orders AND Status NOT IN ('Financed','Credit','Void','Order Cancelled','Cancelled') AND Captured <> 'Yes' AND (CapDate IS NULL OR CapDate = '0000-00-00') )
									OR 1 <= (SELECT COUNT(*) FROM sl_orders_notes WHERE ID_orders = sl_returns.ID_orders AND sl_orders_notes.Date > sl_returns.Date AND Type = 'Exchange Paid')
								)
								, 1
						)
		    		/*AND IF(
	    				sl_orders_products.Status = 'Exchange', 
	    					sl_warehouses_batches_orders.ID_orders_products IS NULL,
	    					0 < (SELECT SUM(IF(Status = 'Returned',1,0)) FROM sl_warehouses_batches_orders WHERE ID_orders_products = ID_orders_products ORDER BY ID_warehouses_batches_orders DESC LIMIT 1)
	    			)*/
				");
	$va{'matches'} = $sth->fetchrow;
	
	if ($va{'matches'}>0){

		my (@c) = split(/,/,$cfg{'srcolors'});
		my ($sth) = &Do_SQL("SELECT 
								SUM(SumNet) AS TotNet
								, SUM(SumTot) AS TotOrd
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
									, (Saleprice - sl_orders_products.Discount + Shipping + Tax + ShpTax) AS SumTot
									, ID_zones
								FROM sl_orders INNER JOIN sl_returns USING(ID_orders) 
								INNER JOIN sl_orders_products USING(ID_orders)
								LEFT JOIN sl_products on(sl_products.ID_products=RIGHT(sl_orders_products.ID_products,6)) 
							    LEFT JOIN sl_parts ON(sl_parts.ID_parts=RIGHT(sl_orders_products.ID_products,4)) 
								LEFT JOIN  sl_warehouses_batches_orders
									ON sl_warehouses_batches_orders.ID_orders_products = sl_orders_products.ID_orders_products 
									AND sl_warehouses_batches_orders.Status IN ('In Fulfillment','Shipped','In Transit'/*,'Returned'*/)  
								WHERE 1
						    	/*AND Ptype != 'COD'*/
								AND sl_orders.Status = 'Shipped'
								AND StatusPrd IN('For Exchange','For Re-Ship')
								AND sl_orders_products.Status IN ('Exchange','Undeliverable','ReShip') 
								AND sl_orders_products.SalePrice >= 0
								AND (PackingListStatus != 'Done' OR ISNULL(PackingListStatus))
								AND sl_returns.Status IN ('Resolved','Archived','Pending Payments','Pending Refunds')
								AND sl_returns.merAction IN('Exchange','ReShip')
								AND sl_orders_products.SalePrice >= 0
								AND sl_orders_products.ID_products BETWEEN 100000000 AND 399999999
								AND sl_warehouses_batches_orders.ID_orders_products IS NULL
								AND IF(
										merAction = 'Exchange'
											, (
												1 > (SELECT COUNT(*) FROM sl_orders_payments WHERE ID_orders = sl_returns.ID_orders AND Status NOT IN ('Financed','Credit','Void','Order Cancelled','Cancelled') AND Captured <> 'Yes' AND (CapDate IS NULL OR CapDate = '0000-00-00') )
												OR 1 <= (SELECT COUNT(*) FROM sl_orders_notes WHERE ID_orders = sl_returns.ID_orders AND sl_orders_notes.Date > sl_returns.Date AND Type = 'Exchange Paid')
											)
											, 1
									)
					    		/*AND IF(
					    				sl_orders_products.Status = 'Exchange', 
					    					sl_warehouses_batches_orders.ID_orders_products IS NULL,
					    					0 < (SELECT SUM(IF(Status = 'Returned',1,0)) FROM sl_warehouses_batches_orders WHERE ID_orders_products = ID_orders_products ORDER BY ID_warehouses_batches_orders DESC LIMIT 1)
					    			)*/
								GROUP BY sl_orders_products.ID_orders_products
								ORDER BY sl_orders.ID_orders DESC 
							) AS tmp
							LEFT JOIN sl_zones ON tmp.ID_zones=sl_zones.ID_zones
							WHERE 1
							GROUP BY ID_zones");

		while (my $rec = $sth->fetchrow_hashref){

			$d = 1 - $d;
			my $ed = $rec->{'Express_Delivery'}	? qq|<img src="/sitimages/delivery_2_on.jpg" title="Express Delivery">| : '';

			$va{'searchresults'} .= "<tr bgcolor='$c[$d]' onmouseover='m_over(this)' onmouseout='m_out(this)'>\n";
			$va{'searchresults'} .= "  <td class='smalltext' valign='top' align='center'><a href='#' onClick=\"trjump('/cgi-bin/mod/wms/admin?cmd=retpackinglist_zones&id_zones=$rec->{'ID_zones'}')\"><img src='[va_imgurl]/[ur_pref_style]/icsearchsmall.gif' title='Next' alt='' border='0'></a></td>\n";
			$va{'searchresults'} .= "  <td class='smalltext' valign='top' align='center'><a href='#' onClick=\"trjump('/cgi-bin/mod/wms/dbman?cmd=opr_zones&view=$rec->{'ID_zones'}')\">$rec->{'ID_zones'}</a></td>\n";
			$va{'searchresults'} .= "  <td class='smalltext' valign='top'><a href='#' onClick=\"trjump('/cgi-bin/mod/wms/admin?cmd=retpackinglist_zones&id_zones=$rec->{'ID_zones'}')\">$rec->{'Name'} &nbsp; $ed</a></td>\n";
			$va{'searchresults'} .= "  <td class='smalltext' valign='top' align='right'>".&format_number($rec->{'TotZone'})."</td>\n";
			$va{'searchresults'} .= "  <td class='smalltext' valign='top' align='right'>".&format_price($rec->{'TotOrd'})."</td>\n";
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
	print &build_page('retpackinglist_zones.html');
}

sub retpackinglist_zones_to_batch {
# --------------------------------------------------------

	if ($in{'action'}){

		if ($in{'id_warehouses'} and $in{'id_orders'}){

			delete($va{'message'}); delete($va{'message_zip_excluded'});
			my ($id_batch) = &create_warehouse_batch_file($in{'id_warehouses'});
			my ($sth) = &Do_SQL("UPDATE sl_warehouses_batches SET Status='Assigned' WHERE ID_warehouses=$in{'id_warehouses'} AND Status = 'New'");

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
								FROM sl_orders INNER JOIN sl_returns USING(ID_orders) 
								INNER JOIN sl_orders_products USING(ID_orders )
								LEFT JOIN sl_products on(sl_products.ID_products=RIGHT(sl_orders_products.ID_products,6)) 
								LEFT JOIN sl_warehouses_batches_orders
									ON sl_warehouses_batches_orders.ID_orders_products = sl_orders_products.ID_orders_products 
									AND sl_warehouses_batches_orders.Status IN ('In Fulfillment','Shipped','In Transit'/*,'Returned'*/)  
								WHERE 1
						    	/*AND Ptype != 'COD'*/
								AND sl_orders.Status = 'Shipped'
								AND StatusPrd IN('For Exchange','For Re-Ship')
								AND sl_orders_products.Status IN ('Exchange','Undeliverable','ReShip') 
								AND sl_orders_products.SalePrice >= 0
								AND (PackingListStatus != 'Done' OR ISNULL(PackingListStatus))
								AND sl_returns.Status IN ('Resolved','Pending Payments','Pending Refunds')
								AND sl_orders_products.SalePrice >= 0
								AND sl_orders_products.ID_products BETWEEN 100000000 AND 399999999
								AND sl_warehouses_batches_orders.ID_orders_products IS NULL
								AND IF(
										merAction = 'Exchange'
											, (
												1 > (SELECT COUNT(*) FROM sl_orders_payments WHERE ID_orders = sl_returns.ID_orders AND Status NOT IN ('Financed','Credit','Void','Order Cancelled','Cancelled') AND Captured <> 'Yes' AND (CapDate IS NULL OR CapDate = '0000-00-00') )
												OR 1 <= (SELECT COUNT(*) FROM sl_orders_notes WHERE ID_orders = sl_returns.ID_orders AND sl_orders_notes.Date > sl_returns.Date AND Type = 'Exchange Paid')
											)
											, 1
									)
					    		/*AND IF(
					    				sl_orders_products.Status = 'Exchange', 
					    					sl_warehouses_batches_orders.ID_orders_products IS NULL,
					    					sl_warehouses_batches_orders.Status = 'Returned'
					    			)*/
								$mod_excluded_zip 
								AND sl_orders.ID_orders IN ($in{'id_orders'})
								AND ID_zones='$in{'id_zones'}';");

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
					SET ID_warehouses_batches = '$id_batch', ID_orders_products = '$idp', Status='In Fulfillment', Date = CURDATE(), Time = CURTIME(), ID_admin_users = '$usr{'id_admin_users'}'");

				($ido ne $this_order) and ( $x += 1) and ($this_order = $ido);
				
			}
			$va{'message'} = &trans_txt('order_batchadded') . ": $id_batch x $x";
			($excluded_zips) and ($va{'message'} .= qq|<br><br>|. &trans_txt('order_batch_zip_excluded') . qq| ( $excluded_zips ): <br>|. $va{'message_zip_excluded'});

		}else{
			$va{'message'} = &trans_txt('tobatch_err');
		}
	}

	$va{'zonename'} = &load_name('sl_zones','ID_zones',$in{'id_zones'},'Name');
	
	my ($sth) = &Do_SQL("SELECT COUNT(*) FROM sl_zones_warehouses INNER JOIN sl_warehouses ON sl_zones_warehouses.ID_warehouses=sl_warehouses.ID_warehouses AND sl_warehouses.Status='Active' WHERE ID_zones='$in{'id_zones'}';");
	if ($sth->fetchrow>0){
		my (@c) = split(/,/,$cfg{'srcolors'});
		#############################
		### List of Warehouse
		#############################
		my ($sth) = &Do_SQL("SELECT * FROM sl_zones_warehouses INNER JOIN sl_warehouses ON sl_zones_warehouses.ID_warehouses=sl_warehouses.ID_warehouses AND sl_warehouses.Status='Active' WHERE ID_zones='$in{'id_zones'}';");
		while (my $rec = $sth->fetchrow_hashref){
			$d = 1 - $d;

			#####
			##### Ordenes en Remesa Actual
			#####
			my ($sthw) = &Do_SQL("SELECT COUNT(DISTINCT sl_orders.ID_orders)
			FROM sl_orders 
			INNER JOIN sl_orders_products USING(ID_orders)
			INNER JOIN sl_warehouses_batches_orders USING(ID_orders_products)
			INNER JOIN sl_warehouses_batches USING(ID_warehouses_batches)
			WHERE sl_warehouses_batches.ID_warehouses=$rec->{'ID_warehouses'}
			AND sl_warehouses_batches.Status IN ('New','Assigned')");
			my ($this_warehouse_batch) = $sthw->fetchrow();

			# my ($sth2) = &Do_SQL("SELECT COUNT(*) tot_intransit, SUM(OrderNet) AS amt_intransit, SUM(OrderQty) AS qty_intransit
			# FROM sl_warehouses_batches_orders
			# LEFT JOIN sl_warehouses_batches ON sl_warehouses_batches.ID_warehouses_batches=sl_warehouses_batches_orders.ID_warehouses_batches
			# LEFT JOIN sl_orders_products ON sl_warehouses_batches_orders.ID_orders_products=sl_orders_products.ID_orders_products
			# LEFT JOIN sl_orders ON sl_orders_products.ID_orders=sl_orders.ID_orders
			# WHERE sl_warehouses_batches_orders.status='In Transit'
			# AND sl_warehouses_batches.ID_warehouses=$rec->{'ID_warehouses'}");
			# $rec_tot = $sth2->fetchrow_hashref();

			$va{'searchresults'} .= "<tr bgcolor='$c[$d]' onmouseover='m_over(this)' onmouseout='m_out(this)'>\n";
			$va{'searchresults'} .= "  <td class='smalltext' valign='top' align='center'><input type='radio' class='radio' name='id_warehouses' value='$rec->{'ID_warehouses'}'</td>\n";
			$va{'searchresults'} .= "  <td class='smalltext' valign='top' align='center'><a href='#' onClick=\"trjump('/cgi-bin/mod/wms/dbman?cmd=opr_warehouses&view=$rec->{'ID_warehouses'}')\">$rec->{'ID_warehouses'}</a></td>\n";
			$va{'searchresults'} .= "  <td class='smalltext' valign='top'>$rec->{'Name'}</td>\n";
			$va{'searchresults'} .= "  <td class='smalltext' valign='top' align='right'>".&format_number($this_warehouse_batch)."</td>\n";
			$va{'searchresults'} .= "  <td class='smalltext' valign='top' align='right'>".&format_number($rec_tot->{'Tot_intransit'})."</td>\n";
			$va{'searchresults'} .= "  <td class='smalltext' valign='top' align='right'>".&format_price($rec_tot->{'Amt_intransit'})."</td>\n";
			$va{'searchresults'} .= "  <td class='smalltext' valign='top' align='right'>".&format_number($rec_tot->{'Qty_intransit'})."</td>\n";
			$va{'searchresults'} .= "</tr>\n";
		}
		#############################
		### List of Orders
		#############################
		my ($modquery, $modquery2);
		($in{'from_date'}) and ($modquery .= "AND sl_orders.Date >= '$in{'from_date'}' ");
		($in{'to_date'}) and ($modquery .= "AND sl_orders.Date <= '$in{'to_date'}' ");
		($in{'sid_products'}) and ($modquery .= "AND sl_orders_products.ID_products = '$in{'sid_products'}' ");
		($in{'shp_city'}) and ($modquery .= "AND shp_City = '$in{'shp_city'}' ");
		($in{'shp_type'}) and ($modquery .= "AND shp_type = '$in{'shp_type'}' ");
		if($in{'from_amount'}){ $in{'from_amount'} =~ s/\$|,//g; $modquery2 .= "HAVING TotProd >= '$in{'from_amount'}' "; }
		if($in{'to_amount'}){
			$in{'to_amount'} =~ s/\$|,//g;
			$modquery2 .= ($in{'from_amount'})? "AND TotProd <= '$in{'to_amount'}' " : "HAVING TotProd <= '$in{'to_amount'}' "; 
		}

		my ($sth) = &Do_SQL("SELECT 
								sl_orders.ID_orders
								, sl_orders.Date
								, SUM( ( (SalePrice - sl_orders_products.Discount) * Quantity ) + Shipping + ShpTax + Tax ) AS TotProd
								, SUM(Quantity) AS TotItems
								, sl_orders.ID_customers
								, IF(shp_type = 2,1,0) AS Express_Delivery
								, shp_Zip,shp_City
								, shp_Urbanization
								, ID_warehouses_batches_orders
								, meraction
							FROM sl_orders INNER JOIN sl_returns USING(ID_orders)
							INNER JOIN sl_orders_products USING(ID_orders)
							LEFT JOIN sl_products on(sl_products.ID_products=RIGHT(sl_orders_products.ID_products,6)) 
							LEFT JOIN sl_warehouses_batches_orders
								ON sl_warehouses_batches_orders.ID_orders_products = sl_orders_products.ID_orders_products 
								AND sl_warehouses_batches_orders.Status IN ('In Fulfillment','Shipped','In Transit'/*,'Returned'*/)
							WHERE 1
						    	/*AND Ptype != 'COD'*/
								AND sl_orders.Status = 'Shipped'
								AND StatusPrd IN('For Exchange','For Re-Ship')
								AND sl_orders_products.Status IN ('Exchange','Undeliverable','ReShip') 
								AND sl_orders_products.SalePrice >= 0
								AND (PackingListStatus != 'Done' OR ISNULL(PackingListStatus))
								AND sl_returns.Status IN ('Resolved','Pending Payments','Pending Refunds')
								AND sl_orders_products.SalePrice >= 0
								AND sl_orders_products.ID_products BETWEEN 100000000 AND 399999999
								AND sl_warehouses_batches_orders.ID_orders_products IS NULL
								AND IF(
										merAction = 'Exchange'
											, (
												1 > (SELECT COUNT(*) FROM sl_orders_payments WHERE ID_orders = sl_returns.ID_orders AND Status NOT IN ('Financed','Credit','Void','Order Cancelled','Cancelled') AND Captured <> 'Yes' AND (CapDate IS NULL OR CapDate = '0000-00-00') )
												OR 1 <= (SELECT COUNT(*) FROM sl_orders_notes WHERE ID_orders = sl_returns.ID_orders AND sl_orders_notes.Date > sl_returns.Date AND Type = 'Exchange Paid')
											)
											, 1
									)
					    		/*AND IF(
					    				sl_orders_products.Status = 'Exchange', 
					    					sl_warehouses_batches_orders.ID_orders_products IS NULL,
					    					0 < (SELECT SUM(IF(Status = 'Returned',1,0)) FROM sl_warehouses_batches_orders WHERE ID_orders_products = ID_orders_products ORDER BY ID_warehouses_batches_orders DESC LIMIT 1)
					    			)*/
							$modquery
							AND ID_zones = $in{'id_zones'}
							GROUP BY sl_orders.ID_orders
							$modquery2 
							ORDER BY meraction,shp_Zip,shp_City,shp_Urbanization,sl_orders.ID_orders DESC");

		$va{'matches'} = $sth->rows;
		
		if ($va{'matches'}>0){

			while ($rec = $sth->fetchrow_hashref){

				$d = 1 - $d;
				$cont=0;
				my $id_orders_string = $rec->{'ID_orders'};
				$id_orders_string .= 'R' if $rec->{'meraction'} eq 'ReShip';
				$id_orders_string .= 'CF' if $rec->{'meraction'} eq 'Exchange';

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
				$va{'ordsearchresults'} .= "  <td class='smalltext' valign='top' align='center'><a href='#' onClick=\"trjump('/cgi-bin/mod/wms/dbman?cmd=opr_orders&view=$rec->{'ID_orders'}&check_status=1')\">$id_orders_string</a></td>\n";
				$va{'ordsearchresults'} .= "  <td class='smalltext' valign='top' align='center'> $ed </td>\n";
				$va{'ordsearchresults'} .= "  <td class='smalltext' valign='top'>$rec->{'shp_City'}<br>$rec->{'shp_Urbanization'}</td>\n";
				$va{'ordsearchresults'} .= "  <td class='smalltext' valign='top'>$rec->{'Date'}</td>\n";
				$va{'ordsearchresults'} .= "  <td class='smalltext' valign='top'>".&load_db_names('sl_customers','ID_customers',$rec->{'ID_customers'},"[company_name] [FirstName] [LastName1]")."</td>\n";
				$va{'ordsearchresults'} .= "  <td class='smalltext' valign='top'>$rec->{'TotItems'}</td>\n";
				$va{'ordsearchresults'} .= "  <td class='smalltext' valign='top' align='right'>".&format_price($rec->{'TotProd'})."</td>\n";
				$va{'ordsearchresults'} .= "</tr>\n";

				$sth1=&Do_SQL("SELECT 
								ID_orders,sl_orders_products.ID_products, Name, Model
							FROM sl_orders_products
							INNER JOIN sl_products on (right(sl_orders_products.ID_products,6)=sl_products.ID_products)
							WHERE ID_orders = '$rec->{'ID_orders'}' AND sl_products.status IN('Exchange','ReShip')
							AND IF(
			    				sl_orders_products.Status = 'Exchange', 
			    					(sl_orders_products.Shpdate IS NULL OR sl_orders_products.Shpdate = '0000-00-00'),
			    					(sl_orders_products.Shpdate IS NOT NULL AND sl_orders_products.Shpdate <> '0000-00-00' AND sl_orders_products.Shpdate <= CURDATE())
			    			);");

				while($rec1=$sth1->fetchrow_hashref) {

					if($va{'filterby_ids'} !~ /$rec1->{'ID_products'}/){

						#####
						##### Used to filter by Product
						#####
						my $en = "$in{'sid_products'}" eq "$rec1->{'ID_products'}" ? 'selected="selected"' : '';
						$va{'filterby_ids'} .= qq|<option value="$rec1->{'ID_products'}" $en>$rec1->{'ID_products'} - $rec1->{'Name'}</option>\n|;

					}

					$va{'ordsearchresults'} .= "<tr bgcolor='$c[$d]'>\n";
					$va{'ordsearchresults'} .= "  <td class='smalltext' valign='top' colspan='4'></td>\n";
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
				<td colspan='7' align="center">|.&trans_txt('search_nomatches').qq|</td>
			</tr>\n|;
		}
	}else{
		$va{'message'} = &trans_txt('nozones_err');
		$va{'matches'} = 0;
		$va{'pageslist'} = 1;
		$va{'searchresults'} = qq|
		<tr>
			<td colspan='6' align="center">|.&trans_txt('search_nomatches').qq|</td>
		</tr>\n|;
		$va{'ordsearchresults'} = qq|
			<tr>
				<td colspan='7' align="center">|.&trans_txt('search_nomatches').qq|</td>
			</tr>\n|;
	}

	print "Content-type: text/html\n\n";
	print &build_page('retpackinglist_zonesbatch.html');
}


sub _retpackinglist_{
# --------------------------------------------------------
# Forms Involved: 
# Created on: 12/15/08 13:57:22
# Author: MCC C. Gabriel Varela S.
# Description :   
# Parameters :
# Last Modified on: 12/18/08 17:22:03
# Last Modified by: MCC C. Gabriel Varela S: Se cambia consulta. Se habilita print.
# Last Modified on: 12/19/08 12:51:48
# Last Modified by: MCC C. Gabriel Varela S: Se modifica proceso de printing
# Last Modified on: 01/08/09 13:40:08
# Last Modified by: MCC C. Gabriel Varela S: Se modifica la consulta que muestra los resultados y la lista que muestra los choices.
# Last Modified on: 01/09/09 17:32:05
# Last Modified by: MCC C. Gabriel Varela S: Se modifica consulta para no tomar en cuenta registros de sl_orders_products con status diferente a Active
# Last Modification by JRG : 03/12/2009 : Se agrega log


	if($in{'tobatch'} eq 'selected'){

		if($in{'ordersselected'} and $in{'id_warehouses'}){

			chop($in{'ordersselected'});

			## Old batch records to Return
			my ($sth) = &Do_SQL("UPDATE sl_warehouses_batches_orders
			                    SET Status = 'Returned'
								WHERE ID_orders_products
								IN(
								   SELECT ID_orders_products FROM sl_orders_products 
								   WHERE ID_orders IN ($in{'ordersselected'})
								   );");

			my $id_warehouses_batches = create_warehouse_batch_file($in{'id_warehouses'});
			my $id_str;
			my @ids = split(/,/,$in{'ordersselected'});

			for (0..$#ids) {
				my $id_orders = int($ids[$_]);

				if($id_str !~ /$id_orders/) {

					my $i;
					my $order_type = &load_name('sl_orders','ID_orders',$id_orders,'Ptype');
					$id_str .= "$id_orders,";			

					## COD Orders driver's assign
					if($order_type) {
						&Do_SQL("UPDATE sl_orders SET ID_warehouses = '$in{'id_warehouses'}' WHERE ID_orders = '$id_orders';");
					}

					## COD/TDC Batch Assign
					my ($sth) = Do_SQL("SELECT ID_orders_products FROM sl_orders_products 
										WHERE ID_orders = '$id_orders' 
										AND Status IN ('Exchange','Undeliverable','ReShip') 
										AND SalePrice >= 0
										AND 1 > (SELECT COUNT(*) FROM sl_warehouses_batches_orders WHERE ID_orders_products = sl_orders_products.ID_orders_products AND Status IN ('In Fulfillment','Shipped','In Transit'));");
					while(my($id_orders_products) = $sth->fetchrow() ) {
						++$i;
						&Do_SQL("INSERT INTO sl_warehouses_batches_orders SET ID_warehouses_batches = '".$id_warehouses_batches."', ID_orders_products = '".$id_orders_products."', Status='In Fulfillment', Date = CURDATE(),Time = CURTIME(),ID_admin_users='$usr{'id_admin_users'}';");
					}

					if($i > 0) {

						&Do_SQL("UPDATE sl_returns SET PackingListStatus = 'Done' WHERE ID_orders = '$id_orders';"); 
						&Do_SQL("UPDATE sl_orders SET StatusPrd='In Fulfillment' WHERE ID_orders = '$id_orders';");

						## Nota y Log para orden asignada
						$in{'db'} = 'sl_orders';

						&add_order_notes_by_type($id_orders,&trans_txt('order_batchadded')." $id_warehouses_batches ","High");

						&auth_logging('order_batchadded', $id_orders);

					}
				}

			}

			if($id_str) {

				&Do_SQL("UPDATE sl_warehouses_batches SET Status='Assigned' WHERE ID_warehouses_batches = '$id_warehouses_batches';");
				$va{'message'} = &trans_txt('done') . "<br>". &trans_txt('order_batchadded')." $id_warehouses_batches ";				

			}else{
				$va{'message'} = &trans_txt('invalid');
			}	
			
			print "Content-type: text/html\n\n";
			print &build_page('toprint_msg.html');
			return;			
		}
	}

	if($in{'showpackinglist'} or $in{'search'} eq "Print") {

		#Muestra el packing list
		$in{'view'}=$in{'toprint'} if(!$in{'view'});
		#Cargar ines
		my $i=0,@fieldss;
		$sth=&Do_SQL("describe sl_orders");

		while($rec=$sth->fetchrow_hashref){
			$fieldss[$i]=lc($rec->{'Field'});
			$i++;
		}

		$fieldss[$i]="Firstname";
		$i++;
		$fieldss[$i]="LastName1";
		
		$sth=&Do_SQL("SELECT sl_orders.*,sl_customers.Firstname,sl_customers.LastName1 FROM `sl_orders` INNER JOIN sl_customers on (sl_orders.ID_customers=sl_customers.ID_customers) WHERE `ID_orders`=$in{'view'}");
		@rec=$sth->fetchrow_array;
		
		for(0..$#rec){
			$in{$fieldss[$_]}=$rec[$_];
		}
		
		if($in{'search'} eq "Print"){

			&html_forprint_headers ('Printing.....');
			print &build_page('retpackinglist_print.html');
		
		}else{

			print "Content-type: text/html\n\n";
			print &build_page('retpackinglistsp.html');

		}

	}else{

		if($in{'action'}) {

			$sth=&Do_SQL("update sl_returns set PackingListStatus='$in{'packingliststatus'}' where ID_returns=$in{'id_returns'}");
			&auth_logging('returns_updated',$in{'id_returns'});
		
		}
		
		my ($sthw) = &Do_SQL("SELECT * FROM sl_warehouses WHERE Type in('Virtual','Outsource') AND Status='Active'");
		while ($war = $sthw->fetchrow_hashref){
			$va{'selectwh'} .= "<option value='".$war->{'ID_warehouses'}."'>".$war->{'Name'}."</option>";
		}

		my $sth,$rec;
		my (@c) = split(/,/,$cfg{'srcolors'});
		$sth=&Do_SQL("SELECT count(distinct(ID_returns))
					FROM sl_returns
					INNER JOIN sl_orders USING(ID_orders)
					INNER JOIN(
						SELECT * from sl_orders_products where Status IN ('Reship','Exchange')
						AND (ShpDate=''or isnull(Shpdate) or ShpDate='0000-00-00') 
						AND (Tracking=''or isnull(Tracking)) 
						AND SalePrice>=0 AND Quantity>=0 AND Shipping>=0 
					)as tempo 
					USING(ID_orders)
					WHERE (PackingListStatus != 'Done' OR ISNULL(PackingListStatus))
					AND sl_returns.Status IN ('Resolved','Archived','Pending Payments','Pending Refunds') ;");
		$va{'matches'} = $sth->fetchrow;
	
		if ($va{'matches'}>0) {

			(!$in{'nh'}) and ($in{'nh'}=1);
			$first = ($in{'nh'} - 1) * $usr{'pref_maxh'};			
			($va{'pageslist'},$qs) = &pages_list($in{'nh'},"/cgi-bin/mod/wms/amdin?cmd=retpackinglist",$va{'matches'},$usr{'pref_maxh'});
			$sth=&Do_SQL("SELECT distinct(ID_returns), sl_returns.ID_orders, sl_returns.ID_orders_products, Amount, merAction, sl_returns.Status AS StatusRet, StatusPrd, StatusPay, sl_orders.Status AS StatusOrd, ID_products_exchange,tempo.ID_orders_products
						FROM sl_returns
						INNER JOIN sl_orders USING(ID_orders)
						INNER JOIN(
							SELECT * from sl_orders_products where Status IN ('Reship','Exchange')
							AND (ShpDate=''or isnull(Shpdate) or ShpDate='0000-00-00') 
							AND (Tracking=''or isnull(Tracking)) 
							AND SalePrice>=0 AND Quantity>=0 AND Shipping>=0 
						)as tempo 
						USING(ID_orders)
						WHERE (PackingListStatus != 'Done' OR ISNULL(PackingListStatus))
						AND sl_returns.Status IN ('Resolved','Archived','Pending Payments','Pending Refunds') 
						GROUP BY ID_returns LIMIT $first,$usr{'pref_maxh'};");
			
			while($rec=$sth->fetchrow_hashref) {
				$d = 1 - $d;
				
				$id_products=&load_name('sl_orders_products','ID_orders_products',$rec->{'ID_orders_products'},'ID_products');
				my ($sthk) = &Do_SQL("SELECT * FROM sl_skus WHERE ID_sku_products='$id_products' and Status='Active'");
				$reck = $sthk->fetchrow_hashref;
				$choices = &load_choices('-',$reck->{'choice1'},$reck->{'choice2'},$reck->{'choice3'},$reck->{'choice4'});
				
				$va{'searchresults'} .= "<tr bgcolor='$c[$d]' onmouseover='m_over(this)' onmouseout='m_out(this)'>\n";
				$va{'searchresults'} .= "   <td class='smalltext'><input type='checkbox' class='checkbox' id='chkor_$rec->{'ID_orders'}' name='chkor_$rec->{'ID_orders'}' value='$rec->{'ID_orders'}' onclick='chk_ord($rec->{'ID_orders'})'>&nbsp;&nbsp;";
				$va{'searchresults'} .= "   <a href='$script_url?cmd=retpackinglist&view=$rec->{'ID_orders'}&ID_orders_products=$rec->{'ID_orders_products'}&choices=$choice&showpackinglist=1&packingliststatus=Pending&id_returns=$rec->{'ID_returns'}')'>V</a></td>\n";
				$va{'searchresults'} .= "   <td class='smalltext'>$rec->{'ID_returns'}</td>\n";
				$va{'searchresults'} .= "   <td class='smalltext'>$rec->{'ID_orders'}</td>\n";
				$va{'searchresults'} .= "   <td class='smalltext'>$rec->{'Amount'}</td>\n";
				$va{'searchresults'} .= "   <td class='smalltext'>$rec->{'merAction'}</td>\n";
				$va{'searchresults'} .= "   <td class='smalltext'>$rec->{'StatusRet'}</td>\n";
				$va{'searchresults'} .= "	<td class='smalltext'>$rec->{'StatusPrd'}</td>\n";							
				$va{'searchresults'} .= "	<td class='smalltext'>$rec->{'StatusPay'}</td>\n";
				$va{'searchresults'} .= "	<td class='smalltext'>$rec->{'StatusOrd'}</td>\n";
				$va{'searchresults'} .= "</tr>\n";
			
			}
		
		}else{

			$va{'pageslist'} = 1;
			$va{'searchresults'} = qq|
				<tr>
					<td colspan='7' align="center">|.&trans_txt('search_nomatches').qq|</td>
				</tr>\n|;
		}

		print "Content-type: text/html\n\n";
		print &build_page('retpackinglist.html');

	}

}



sub retpackinglistbyprod{
# --------------------------------------------------------
# Forms Involved: 
# Created on: 01/08/09 12:35:36
# Author: MCC C. Gabriel Varela S.
# Description :   
# Parameters :
	if($in{'showpackinglist'} or $in{'search'}eq"Print")
	{
		my @id_orders=split(/,/,$in{'id_orders'});
		my @id_orders_products=split(/,/,$in{'id_orders_products'});
		my @id_returns=split(/,/,$in{'id_returns'});
		my %dones;
		for(0..$#id_orders)
		{
			#Muestra el packing list
			if(!$dones{"$id_orders[$_]$id_orders_products[$_]"})
			{
				#$in{'view'}=$in{'toprint'} if(!$in{'view'});
				$in{'view'}=$id_orders[$_];
				$in{'id_orders_products'}=$id_orders_products[$_];
				$in{'id_returns'}=$id_returns[$_];
				
				#Cargar ines
				my $i=0,@fieldss;
				$sth=&Do_SQL("describe sl_orders");
				while($rec=$sth->fetchrow_hashref)
				{
					$fieldss[$i]=lc($rec->{'Field'});
					$i++;
				}
				$fieldss[$i]="Firstname";
				$i++;
				$fieldss[$i]="LastName1";
				
				$sth=&Do_SQL("SELECT sl_orders.*,sl_customers.Firstname,sl_customers.LastName1 FROM `sl_orders` INNER JOIN sl_customers on (sl_orders.ID_customers=sl_customers.ID_customers) WHERE `ID_orders`=$in{'view'}");
				@rec=$sth->fetchrow_array;
				for(0..$#rec)
				{
					$in{$fieldss[$_]}=$rec[$_];
				}
				$va{'packinglist_view'}.=&build_page('forms:packinglist_view.html')."<DIV STYLE='page-break-before:always'></DIV>";
				#$dones{"$id_orders[$_]$id_orders_products[$_]"}=1;
			}
		}
		

		
		if($in{'search'}eq"Print")	{
			print "Content-type: text/html\n\n";
			print &build_page('header_print.html');
			print &build_page('retpackinglistbyproduct_print.html');
		}		else	{
			print "Content-type: text/html\n\n";
			print &build_page('retpackinglistspbyproduct.html');
		}
	}else{
		
		my $sth,$rec;
		my (@c) = split(/,/,$cfg{'srcolors'});
		$sth=&Do_SQL("SELECT count( qty ) FROM (
				SELECT count( DISTINCT (ID_returns) ) AS Qty
				FROM sl_returns
				INNER JOIN sl_orders ON ( sl_returns.ID_orders = sl_orders.ID_orders ) 
				INNER JOIN (
	
					SELECT * 
					FROM sl_orders_products
					WHERE (
						ShpDate = ''
						OR isnull( Shpdate ) 
						OR ShpDate = '0000-00-00')
					AND (
						Tracking = ''
						OR isnull( Tracking ) )
					AND SalePrice >=0
					AND Quantity >=0
					AND Shipping >=0
					AND Status!='Inactive') AS tempo ON ( tempo.ID_orders = sl_orders.ID_orders
										AND tempo.ID_products = ID_products_exchange ) 
					INNER JOIN sl_products ON ( right( ID_products_exchange, 6 ) = sl_products.ID_products ) 
					WHERE PackingListStatus != 'Done' AND ((sl_returns.Status = 'Resolved' AND Amount=0) OR (sl_returns.Status = 'Archived' AND Amount !=0))
				GROUP BY ID_products_exchange
				) AS tabtemp");
		$va{'matches'} = $sth->fetchrow;
	
		if ($va{'matches'}>0)
		{
			(!$in{'nh'}) and ($in{'nh'}=1);
			$first = ($in{'nh'} - 1) * $usr{'pref_maxh'};			
			($va{'pageslist'},$qs) = &pages_list($in{'nh'},"/cgi-bin/mod/$usr{'application'}/admin",$va{'matches'},$usr{'pref_maxh'});
			$sth=&Do_SQL("SELECT count(distinct(ID_returns)) as Qty, group_concat(ID_returns separator ',')as ID_returns, group_concat(sl_returns.ID_orders separator ',')as ID_orders, group_concat(sl_returns.ID_orders_products separator ',') as ID_orders_products, group_concat(Amount separator ',') as Amount, group_concat(merAction separator ',') as merAction, group_concat(sl_returns.Status separator ',') AS StatusRet, group_concat(StatusPrd separator ',')as StatusPrd, group_concat(StatusPay separator ',')as StatusPay, group_concat(sl_orders.Status separator ',') AS StatusOrd, ID_products_exchange,group_concat(tempo.ID_orders_products separator ',')as ID_orders_products,sl_products.ID_products,Name,Model
					FROM sl_returns
					INNER JOIN sl_orders ON ( sl_returns.ID_orders = sl_orders.ID_orders ) 
					INNER JOIN(select * 
							from sl_orders_products 
							where (ShpDate=''or isnull(Shpdate) or ShpDate='0000-00-00') and (Tracking=''or isnull(Tracking)) and SalePrice>=0 and Quantity>=0 and Shipping>=0 and Status!='Inactive')as tempo on(tempo.ID_orders=sl_orders.ID_orders and tempo.ID_products=ID_products_exchange)
					INNER JOIN sl_products on (right(ID_products_exchange,6)=sl_products.ID_products)
					WHERE PackingListStatus != 'Done' AND ((sl_returns.Status = 'Resolved' AND Amount=0) OR (sl_returns.Status = 'Archived' AND Amount !=0))
					GROUP BY ID_products_exchange
					order by Qty desc LIMIT $first,$usr{'pref_maxh'};");
			while($rec=$sth->fetchrow_hashref)
			{
				$d = 1 - $d;
				
	#			$id_products=&load_name('sl_orders_products','ID_orders_products',$rec->{'ID_orders_products'},'ID_products');
	#			my ($sthk) = &Do_SQL("SELECT * FROM sl_skus WHERE ID_sku_products='$id_products'");
	#			$reck = $sthk->fetchrow_hashref;
	#			$choices = &load_choices('-',$reck->{'choice1'},$reck->{'choice2'},$reck->{'choice3'},$reck->{'choice4'});
				
				$va{'searchresults'} .= "<tr bgcolor='$c[$d]' onmouseover='m_over(this)' onmouseout='m_out(this)' onClick=\"prnwin('$script_url?cmd=retpackinglistbyprod&id_orders=$rec->{'ID_orders'}&ID_orders_products=$rec->{'ID_orders_products'}&showpackinglist=1&packingliststatus=Pending&id_returns=$rec->{'ID_returns'}&search=Print')\">\n";
				$va{'searchresults'} .= "   <td class='smalltext'>$rec->{'Qty'}</td>\n";
				$va{'searchresults'} .= "   <td class='smalltext'>".&format_sltvid($rec->{'ID_products_exchange'})."</td>\n";
				$va{'searchresults'} .= "   <td class='smalltext'>$rec->{'Name'}<br>$rec->{'Model'}</td>\n";
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
		#$va{'searchresults'} .=	"</table>";
		print "Content-type: text/html\n\n";
		print &build_page('retpackinglistbyproducts.html');
	}
}

sub mo_coupons{
# --------------------------------------------------------

# Author: Jose Ramirez Garcia
# Created on: 01/14/2009
# Last Modified on: 
# Last Modified by: 
# Description : 
# Forms Involved: 
# Parameters : 

	my ($sth) = &Do_SQL("SELECT sl_orders.* FROM sl_orders, sl_orders_payments WHERE sl_orders.ID_orders = sl_orders_payments.ID_orders AND sl_orders.Coupon IS NULL AND sl_orders_payments.Type='Money Order' AND sl_orders.Status NOT IN('Cancelled','Void','System Error') GROUP BY sl_orders.ID_orders");
	$va{'matches'} = $sth->rows;
	my (@c) = split(/,/,$cfg{'srcolors'});
	if ($va{'matches'}>0){
		(!$in{'nh'}) and ($in{'nh'}=1);
		$first = ($in{'nh'} - 1) * $usr{'pref_maxh'};			
		($va{'pageslist'},$qs) = &pages_list($in{'nh'},"/cgi-bin/mod/$usr{'application'}/admin",$va{'matches'},$usr{'pref_maxh'});
		
		my ($sth) = &Do_SQL("SELECT sl_orders.* FROM sl_orders, sl_orders_payments WHERE sl_orders.ID_orders = sl_orders_payments.ID_orders AND sl_orders.Coupon IS NULL AND sl_orders_payments.Type='Money Order' AND sl_orders.Status NOT IN('Cancelled','Void','System Error') GROUP BY sl_orders.ID_orders LIMIT $first,$usr{'pref_maxh'};");
		while ($rec = $sth->fetchrow_hashref){
			$d = 1 - $d;
			$va{'searchresults'} .= qq|
			<tr bgcolor='$c[$d]' onmouseover='m_over(this)' onmouseout='m_out(this)' onclick="prnwin('/cgi-bin/mod/wms/admin?cmd=print_mo_coupons&id_orders=$rec->{'ID_orders'}')">
				<td class="smalltext">$rec->{'ID_orders'}</td>
				<td class="smalltext">$rec->{'Date'}</td>
				<td class="smalltext">|.&load_name("sl_customers","ID_customers",$rec->{'ID_customers'},"FirstName").qq|</td>
				<td class="smalltext">|.&load_name("sl_customers","ID_customers",$rec->{'ID_customers'},"LastName1").qq| |.&load_name("sl_customers","ID_customers",$rec->{'ID_customers'},"LastName2").qq|</td>
				<td class="smalltext">$rec->{'Status'}</td>
			</tr>\n|;
		}
	}else{	
		$va{'pageslist'} = 1;
		$va{'searchresults'} = qq|
		<tr>
				<td colspan='1' align="center">|.&trans_txt('search_nomatches').qq|</td>
			</tr>\n|;
	}
	print "Content-type: text/html\n\n";
	print &build_page('mo_coupons.html')	

}

sub print_mo_coupons{
# --------------------------------------------------------

# Author: Jose Ramirez Garcia
# Created on: 12/08/2008
# Last Modified on: 
# Last Modified by: 
# Description : 
# Forms Involved: 
# Parameters : 
# Last Modification by JRG : 03/12/2009 : Se agrega log

	if($in{'printall'}){
		print "Content-type: text/html\n\n";
		print &build_page('header_print.html');
		my ($sth) = &Do_SQL("SELECT sl_orders.* FROM sl_orders, sl_orders_payments WHERE sl_orders.ID_orders = sl_orders_payments.ID_orders AND sl_orders.Coupon IS NULL AND sl_orders_payments.Type='Money Order' AND sl_orders.Status NOT IN('Cancelled','Void','System Error') GROUP BY sl_orders.ID_orders");
		while ($rec = $sth->fetchrow_hashref){
				my ($sth) = &Do_SQL("SELECT * FROM sl_orders WHERE ID_orders='$rec->{'ID_orders'}';");
				my ($ins) = $sth->fetchrow_hashref();
				foreach $key (keys %{$ins}){ #informacion de la orden
					$in{lc($key)} = $ins->{$key};
				}
				$va{'pay_info'} = "";
				my ($cnt) = 0;
				my ($sth) = &Do_SQL("SELECT * FROM sl_orders_payments WHERE ID_orders='$rec->{'ID_orders'}'");
				while($row = $sth->fetchrow_hashref){ #informacion de pago que sea necesaria
					$cnt++;
					$va{'pay_info'} = $row->{'ID_orders_payments'};
					print &build_page('print_mo_coupons.html');
					if($cnt%$cfg{'coupons_pp'} == 0){
						print "<DIV STYLE='page-break-before:always'></DIV>";
					}
				}
				my ($sth) = &Do_SQL("SELECT COUNT(*) FROM sl_orders_notes WHERE ID_orders='$rec->{'id_orders'}' AND Notes='MO coupon printed'");
				if($sth->fetchrow_array < 1){
					

					&add_order_notes_by_type($rec->{'ID_orders'},"MO coupon printed","Low");

					&auth_logging('orders_note_added',$rec->{'ID_orders'});
				}
				my ($sth) = &Do_SQL("UPDATE sl_orders SET Coupon=1 WHERE ID_orders='$rec->{'ID_orders'}'");
				&auth_logging('orders_updated',$rec->{'ID_orders'});
				print "<DIV STYLE='page-break-before:always'></DIV>";
		}
	} elsif($in{'id_orders'}){
		my ($sth) = &Do_SQL("SELECT * FROM sl_orders WHERE ID_orders='$in{'id_orders'}';");
		my ($rec) = $sth->fetchrow_hashref();
		foreach $key (keys %{$rec}){ #informacion de la orden
			$in{lc($key)} = $rec->{$key};
		}
		my ($cnt) = 0;
		print "Content-type: text/html\n\n";
		print &build_page('header_print.html');
		my ($sth) = &Do_SQL("SELECT * FROM sl_orders_payments WHERE ID_orders='$in{'id_orders'}'");
		while($row = $sth->fetchrow_hashref){#informacion de pago que sea necesaria
			$cnt++;
			$va{'pay_info'} = $row->{'ID_orders_payments'};
			if($cnt%$cfg{'coupons_pp'} == 0){
				print &build_page('print_mo_coupons.html')				
			}
		}

		my ($sth) = &Do_SQL("SELECT COUNT(*) FROM sl_orders_notes WHERE ID_orders='$in{'id_orders'}' AND Notes='MO coupon printed'");
		if($sth->fetchrow_array < 1){

			&add_order_notes_by_type($in{'id_orders'},"MO coupon printed","Low");
			&auth_logging('orders_note_added',$in{'ID_orders'});
		}
		my ($sth) = &Do_SQL("UPDATE sl_orders SET Coupon=1 WHERE ID_orders='$in{'id_orders'}'");
		&auth_logging('orders_updated',$rec->{'ID_orders'});

	}
}


sub returns_home{
#-----------------------------------------
# Created on: 03/02/09  12:53:31 By  Roberto Barcenas
# Forms Involved: returns_home
# Description : Shows the returns dashboard
# Parameters : 
	
	#####Dates
	my ($sth) = &Do_SQL("SELECT CURDATE() AS d1,
											DATE_SUB(CURDATE(),INTERVAL 7 DAY) AS d7,
											DATE_SUB(CURDATE(),INTERVAL 8 DAY) AS d8,
											DATE_SUB(CURDATE(),INTERVAL 14 DAY) AS d14,
											DATE_SUB(CURDATE(),INTERVAL 15 DAY) AS d15,
											DATE_SUB(CURDATE(),INTERVAL 22 DAY) AS d22,
											DATE_SUB(CURDATE(),INTERVAL 23 DAY) AS d23,
											DATE_SUB(CURDATE(),INTERVAL 30 DAY) AS d30;");
											
	($va{'d1'},$va{'d7'},$va{'d8'},$va{'d14'},$va{'d15'},$va{'d22'},$va{'d23'},$va{'d30'})	=	$sth->fetchrow();
											
	
	######### Sorting
	my ($sth) = &Do_SQL("SELECT SUM(IF(Status = 'In process' AND Date BETWEEN '$va{'d7'}' AND '$va{'d1'}',1,0)) AS s7,
											  SUM(IF(Status = 'In process' AND Date BETWEEN '$va{'d14'}' AND '$va{'d8'}',1,0)) AS s14,
											  SUM(IF(Status = 'In process' AND Date BETWEEN '$va{'d22'}' AND '$va{'d15'}',1,0)) AS s22,
											  SUM(IF(Status = 'In process' AND Date BETWEEN '$va{'d30'}' AND '$va{'d23'}',1,0)) AS s30,
											  
											  SUM(IF(Status = 'Repair' AND Date BETWEEN '$va{'d7'}' AND '$va{'d1'}',1,0)) AS r7,
											  SUM(IF(Status = 'Repair' AND Date BETWEEN '$va{'d14'}' AND '$va{'d8'}',1,0)) AS r14,
											  SUM(IF(Status = 'Repair' AND Date BETWEEN '$va{'d22'}' AND '$va{'d15'}',1,0)) AS r22,
											  SUM(IF(Status = 'Repair' AND Date BETWEEN '$va{'d30'}' AND '$va{'d23'}',1,0)) AS r30,
											  
											  SUM(IF(Status = 'QC/IT' AND Date BETWEEN '$va{'d7'}' AND '$va{'d1'}',1,0)) AS q7,
											  SUM(IF(Status = 'QC/IT' AND Date BETWEEN '$va{'d14'}' AND '$va{'d8'}',1,0)) AS q14,
											  SUM(IF(Status = 'QC/IT' AND Date BETWEEN '$va{'d22'}' AND '$va{'d15'}',1,0)) AS q22,
											  SUM(IF(Status = 'QC/IT' AND Date BETWEEN '$va{'d30'}' AND '$va{'d23'}',1,0)) AS q30,
											  
											  SUM(IF(Status = 'ATC' AND Date BETWEEN '$va{'d7'}' AND '$va{'d1'}',1,0)) AS a7,
											  SUM(IF(Status = 'ATC' AND Date BETWEEN '$va{'d14'}' AND '$va{'d8'}',1,0)) AS a14,
											  SUM(IF(Status = 'ATC' AND Date BETWEEN '$va{'d22'}' AND '$va{'d15'}',1,0)) AS a22,
											  SUM(IF(Status = 'ATC' AND Date BETWEEN '$va{'d30'}' AND '$va{'d23'}',1,0)) AS a30,
											  
											  SUM(IF(Status = 'Processed' AND Date BETWEEN '$va{'d7'}' AND '$va{'d1'}',1,0)) AS p7,
											  SUM(IF(Status = 'Processed' AND Date BETWEEN '$va{'d14'}' AND '$va{'d8'}',1,0)) AS p14,
											  SUM(IF(Status = 'Processed' AND Date BETWEEN '$va{'d22'}' AND '$va{'d15'}',1,0)) AS p22,
											  SUM(IF(Status = 'Processed' AND Date BETWEEN '$va{'d30'}' AND '$va{'d23'}',1,0)) AS p30,
											  
											  SUM(IF(Status = 'Back to inventory' AND Date BETWEEN '$va{'d7'}' AND '$va{'d1'}',1,0)) AS b7,
											  SUM(IF(Status = 'Back to inventory' AND Date BETWEEN '$va{'d14'}' AND '$va{'d8'}',1,0)) AS b14,
											  SUM(IF(Status = 'Back to inventory' AND Date BETWEEN '$va{'d22'}' AND '$va{'d15'}',1,0)) AS b22,
											  SUM(IF(Status = 'Back to inventory' AND Date BETWEEN '$va{'d30'}' AND '$va{'d23'}',1,0)) AS b30
											  
											  FROM sl_returns WHERE Date BETWEEN '$va{'d30'}' AND '$va{'d1'}' 
											  AND Status IN('In process','Repair','QC/IT','ATC','Processed','Back to inventory')");
	
	($va{'sor_7'},$va{'sor_14'},$va{'sor_22'},$va{'sor_30'},$va{'rep_7'},$va{'rep_14'},$va{'rep_22'},$va{'rep_30'},$va{'qc_7'},$va{'qc_14'},$va{'qc_22'},$va{'qc_30'},$va{'mx_7'},$va{'mx_14'},$va{'mx_22'},$va{'mx_30'},$va{'mia_7'},$va{'mia_14'},$va{'mia_22'},$va{'mia_30'},$va{'bti_7'},$va{'bti_14'},$va{'bti_22'},$va{'bti_30'})	=	$sth->fetchrow();
	
	### Status
	$va{'tot_sorting'}	=	$va{'sor_7'}+$va{'sor_14'}+$va{'sor_22'}+$va{'sor_30'};
	$va{'tot_repair'}	=	$va{'rep_7'}+$va{'rep_14'}+$va{'rep_22'}+$va{'rep_30'};
	$va{'tot_qcit'}	=	$va{'qc_7'}+$va{'qc_14'}+$va{'qc_22'}+$va{'qc_30'};
	$va{'tot_atc'}	=	$va{'mx_7'}+$va{'mx_14'}+$va{'mx_22'}+$va{'mx_30'};
	$va{'tot_processed'}	=	$va{'mia_7'}+$va{'mia_14'}+$va{'mia_22'}+$va{'mia_30'};
	$va{'tot_bti'}	=	$va{'bti_7'}+$va{'bti_14'}+$va{'bti_22'}+$va{'bti_30'};
	
	#### Range
	$va{'tot_30'}	=	$va{'sor_30'} + $va{'rep_30'} + $va{'qc_30'} + $va{'mx_30'} + $va{'mia_30'} + $va{'bti_30'};
	$va{'tot_22'}	=	$va{'sor_22'} + $va{'rep_22'} + $va{'qc_22'} + $va{'mx_22'} + $va{'mia_22'} + $va{'bti_22'};
	$va{'tot_14'}	=	$va{'sor_14'} + $va{'rep_14'} + $va{'qc_14'} + $va{'mx_14'} + $va{'mia_14'} + $va{'bti_14'};
	$va{'tot_7'}	=	$va{'sor_7'} + $va{'rep_7'} + $va{'qc_7'} + $va{'mx_7'} + $va{'mia_7'} + $va{'bti_7'};
	$va{'tot_returns'}	=	$va{'tot_30'} + $va{'tot_22'} + $va{'tot_14'} + $va{'tot_7'};
	
	
	print "Content-type: text/html\n\n";
	print &build_page('returns_home.html');
}


sub rvendor_list {
# --------------------------------------------------------

	## TO-DO: Agregar Permisos
	
	my (@c) = split(/,/,$cfg{'srcolors'});
	my ($sth) = &Do_SQL("SELECT COUNT(*) FROM sl_purchaseorders WHERE Type='Return to Vendor'  AND Status !='Cancelled'");
	$va{'matches'} = $sth->fetchrow;
	if ($va{'matches'}>0){
		(!$in{'nh'}) and ($in{'nh'}=1);
		$first = ($in{'nh'} - 1) * $usr{'pref_maxh'};			
		($va{'pageslist'},$qs) = &pages_list($in{'nh'},"/cgi-bin/mod/$usr{'application'}/admin",$va{'matches'},$usr{'pref_maxh'});
		my ($sth) = &Do_SQL("SELECT * FROM sl_purchaseorders WHERE Type='Return to Vendor'  AND Status !='Cancelled' ORDER BY ID_purchaseorders DESC LIMIT $first,$usr{'pref_maxh'};");
		while ($rec = $sth->fetchrow_hashref){
			$d = 1 - $d;
			$va{'searchresults'} .= "<tr bgcolor='$c[$d]' onmouseover='m_over(this)' onmouseout='m_out(this)' onClick=\"trjump('/cgi-bin/mod/wms/admin?cmd=rvendor&id_purchaseorders=$rec->{'ID_purchaseorders'}')\">\n";
			$va{'searchresults'} .= "   <td class='smalltext'>$rec->{'ID_purchaseorders'}</td>\n";
			$va{'searchresults'} .= "   <td class='smalltext'>".&load_name('sl_vendors','ID_vendors',$rec->{'ID_vendors'},'CompanyName')."</td>\n";
			$va{'searchresults'} .= "   <td class='smalltext'>".&load_name('sl_warehouses','ID_warehouses',$rec->{'ID_warehouses'},'Name')."</td>\n";
			$va{'searchresults'} .= "   <td class='smalltext'>$rec->{'Date'}</td>\n";
			$va{'searchresults'} .= "   <td class='smalltext'>$rec->{'Status'}</td>\n";
			$va{'searchresults'} .= "</tr>\n";
		}
	}else{
		$va{'pageslist'} = 1;
		$va{'searchresults'} = qq|
			<tr>
				<td colspan='4' align='center'>|.&trans_txt('search_nomatches').qq|</td>
			</tr>\n|;
	}

	print "Content-type: text/html\n\n";
	print &build_page('rvendor_list.html');
}



sub rvendor {
# --------------------------------------------------------

	## TO-DO: Agregar Permisos
	($in{'view'}) and ($in{'id_purchaseorders'} = $in{'view'});
		
	$in{'id_purchaseorders'} = int($in{'id_purchaseorders'});
	if ($in{'id_purchaseorders'}>0){
		
		############### Se cambia el Status a Sent 
		my $type = &load_name('sl_purchaseorders','ID_purchaseorders',$in{'id_purchaseorders'},'Type'); 
		my $status = &load_name('sl_purchaseorders','ID_purchaseorders',$in{'id_purchaseorders'},'Status');

		if($in{'sent'} and $status ne 'Sent' and $type eq 'Return to Vendor') { 

			my ($sth) = &Do_SQL("UPDATE sl_purchaseorders SET Status='Sent' WHERE ID_purchaseorders = $in{'id_purchaseorders'};");
			my ($sth2) = &Do_SQL("INSERT INTO sl_purchaseorders_notes SET Notes='The Orders has been returned to Vendor',Type='Low',ID_purchaseorders='$in{'id_purchaseorders'}' ,Date=CURDATE(),Time=CURTIME(),ID_admin_users='$usr{'id_admin_users'}';");		

			## Movimientos de contabilidad
			if($tot_accounting > 0) {
				my @params = ($in{'id_purchaseorders'});
				&accounting_keypoints('returntovendor', \@params ); 
		 	}


		}
		
		
		&load_cfg('sl_purchaseorders');
		%tmp = &get_record('ID_purchaseorders',$in{'id_purchaseorders'},'sl_purchaseorders');

		for (0..$#db_cols){
			$in{lc($db_cols[$_])} = $tmp{lc($db_cols[$_])};
		}
		$in{'authby_name'} = &load_db_names('admin_users','ID_admin_users',$in{'authby'},'[Firstname] [Lastname]');	
		$va{'vendorinfo'}= &load_name('sl_vendors','ID_vendors',$in{'id_vendors'},'CompanyName');
		$va{'warehouseinfo'} = &load_name('sl_warehouses','ID_warehouses',$in{'id_warehouses'},'Name');
		$va{'sentinfo'} = '';
		
		if ($in{'status'}ne'Sent'){
			$va{'sentinfo'} = qq|<a href="/cgi-bin/mod/wms/admin?cmd=rvendor&id_purchaseorders=$in{'id_purchaseorders'}&sent=1">Change to Sent|;
		}
		## Build PO
		my ($choices,$tot_qty,$tot_po,$vendor_sku,$line,$name);
		my (@c) = split(/,/,$cfg{'srcolors'});
		my ($sth) = &Do_SQL("SELECT COUNT(*) FROM sl_purchaseorders_items WHERE ID_purchaseorders='$in{'id_purchaseorders'}'");
		if ($sth->fetchrow>0){
			my ($sth) = &Do_SQL("SELECT * FROM sl_purchaseorders_items WHERE ID_purchaseorders='$in{'id_purchaseorders'}' ORDER BY ID_purchaseorders_items DESC;");
			while ($rec = $sth->fetchrow_hashref){
				$d = 1 - $d;
				++$line;
				
				## Choices
				my ($sth2) = &Do_SQL("SELECT * FROM sl_skus WHERE ID_sku_products='$rec->{ID_products}' and Status='Active'");
				$tmp = $sth2->fetchrow_hashref;
				$choices = &load_choices('-',$rec->{'choice1'},$rec->{'choice2'},$rec->{'choice3'},$rec->{'choice4'});
				
				## Name Model
				if ($rec->{'ID_products'} > 400000000){
					## Part
					$name = &load_db_names('sl_parts','ID_parts',($rec->{ID_products}-400000000),'[Model]<br>[Name]');
				}else{
					## Regular Item
					$name = &load_db_names('sl_products','ID_products',substr($rec->{ID_products},3,6),'[Model]<br>[Name]');
				}
				
				$va{'polist'} .= "<tr bgcolor='$c[$d]'>\n";
				$va{'polist'} .= "   <td class='smalltext' valign='top'>$line</td>\n";
				$va{'polist'} .= "   <td class='smalltext' valign='top' nowrap><a href='/cgi-bin/mod/$usr{'application'}/dbman?cmd=mer_parts&view=".substr($rec->{'ID_products'},3,6)."'>".&format_sltvid($rec->{'ID_products'})."</a></td>\n";
				$va{'polist'} .= "   <td class='smalltext' valign='top'>$tmp->{'VendorSKU'}</td>\n";
				$va{'polist'} .= "   <td class='smalltext' valign='top'>$name $choices</td>\n";
				$va{'polist'} .= "   <td class='smalltext' align='right' valign='top'>".&format_number($rec->{'Qty'})."</td>\n";
				$va{'polist'} .= "   <td class='smalltext' align='right' valign='top'>".&format_number($rec->{'Received'})."</td>\n";
				$va{'polist'} .= "   <td class='smalltext' align='right' valign='top' nowrap> ".&format_price($rec->{'Price'})."</td>\n";
				$va{'polist'} .= "   <td class='smalltext' align='right' valign='top' nowrap> ".&format_price($rec->{'Price'}*$rec->{'Qty'})."</td>\n";
				$va{'polist'} .= "</tr>\n";
				$tot_qty += $rec->{'Qty'};
				$tot_po +=$rec->{'Price'}*$rec->{'Qty'};				
	
			}
		}else{
			$va{'polist'} = qq|
				<tr>
					<td colspan='7' align="center">|.&trans_txt('search_nomatches').qq|</td>
				</tr>\n|;
		}
		
		my ($sth) = &Do_SQL("SELECT COUNT(*) FROM sl_purchaseorders_adj WHERE ID_purchaseorders='$in{'id_purchaseorders'}'");
		if ($sth->fetchrow>0){
			my ($sth) = &Do_SQL("SELECT * FROM sl_purchaseorders_adj WHERE ID_purchaseorders='$in{'id_purchaseorders'}'");
			while ($rec = $sth->fetchrow_hashref){
				$d = 1 - $d;
				++$line;
				$va{'polist'} .= "<tr bgcolor='$c[$d]'>\n";
				$va{'polist'} .= "   <td class='smalltext'>$line</td>\n";
				$va{'polist'} .= "   <td class='smalltext'>---</td>\n";
				$va{'polist'} .= "   <td class='smalltext'>---</td>\n";
				$va{'polist'} .= "   <td class='smalltext'>$rec->{'Type'}: $rec->{'Description'}</td>\n";
				$va{'polist'} .= "   <td class='smalltext' align='right'>---</td>\n";
				$va{'polist'} .= "   <td class='smalltext' align='right'>---</td>\n";
				$va{'polist'} .= "   <td class='smalltext' align='right'> ".&format_price($rec->{'Amount'})."</td>\n";
				$va{'polist'} .= "   <td class='smalltext' align='right'> ".&format_price($rec->{'Amount'})."</td>\n";
				$va{'polist'} .= "</tr>\n";
				$tot_po += $rec->{'Amount'};
			}
		}
		$va{'vendor_name'} = &load_db_names('sl_vendors','ID_vendors',$in{'id_vendors'},	'[CompanyName]<br>[address] [city] <br>[city] [zip]');
		$va{'shiptoaddress'} = &load_db_names('sl_warehouses','ID_warehouses',$in{'id_warehouses'},'[Name]<br>[address1] [address2] [address3]<br>[city] [state] [zip]');
		$va{'pototal'} = &format_price($tot_po);		
		print "Content-type: text/html\n\n";
		print &build_page('rvendor.html');
	}else{
		&rvendor_list;
	}
}


sub orders_dropshipp{
# --------------------------------------------------------
# Forms Involved: 
# Created on: 02 Sep 2010 13:45:37
# Author: R.B.
# Description :   
# Parameters :

	my ($x,$err,$query);

	if($in{'action'}){

		#Valida los datos para la creación de cliente
		$err = &validate_orders_dropshipp();
		if ($err==0){

			my $id_warehouses = &load_name('sl_warehouses','Name','LA Main','ID_warehouses');
			my $id_wreceipt = 0;
			my ($products)='';
			$in{'id_purchaseorders'} = int($in{'id_purchaseorders'});

			if(!$in{'id_purchaseorders'}){
					#Inserta PO

					for(1..5){
						if(int($in{'id_products'.$_}) > 0){
								$products.= int($in{'id_products'.$_}) . ',';
						}
					}

					chop($products);
					my ($sth) = &Do_SQL("INSERT INTO sl_purchaseorders SET ID_vendors = '$in{'id_vendors'}' , PODate = CURDATE() , CancelDate = DATE_ADD(CURDATE(), INTERVAL 1 MONTH) , POTerms = '30 Days' , Type='Purchase Order' , Shipvia='USPS' , ID_warehouses = '$id_warehouses' , AuthBy = '$usr{'id_admin_users'}' , Auth='Approved' , Status='In Process' , Date= CURDATE() , Time = CURTIME()  , ID_admin_users = '$usr{'id_admin_users'}';");
					$in{'id_purchaseorders'} = $sth->{'mysql_insertid'};
					
					if(!$in{'id_purchaseorders'}){
						$va{'message'} = 'Error: Impossible to create te PO.';
						return;
					
					}else{
							&auth_logging('purchaseorder_created',$in{'id_purchaseorders'});
							$va{'message_dp'} = "OK: PO $in{'id_purchaseorders'} Created ";
							my $query ='';
							my ($sthk) = &Do_SQL("SELECT ID_sku_products,sl_skus.ID_products,SUM(Quantity) AS Quantity,isSet FROM sl_orders_products INNER JOIN sl_skus ON ID_sku_products = sl_orders_products.ID_products WHERE ID_orders = '$in{'id_orders'}' AND sl_orders_products.Status='Active' AND (ShpDate IS NULL OR ShpDate='' OR ShpDate = '0000-00-00') GROUP BY ID_sku_products;");
							while($rec = $sthk->fetchrow_hashref()){
									my $cost=0;
									if ($rec->{'isSet'} eq 'Y'){
						  				### SETS / Kits
											my ($sth2) = &Do_SQL("SELECT * FROM sl_skus_parts WHERE ID_sku_products = '$rec->{'ID_sku_products'}';");
											while ($tmp = $sth2->fetchrow_hashref){
													my $idp = 400000000 + $tmp->{'ID_parts'}; 
													my $qty = $tmp->{'Qty'} * $rec->{'Quantity'};
													$cost = load_sltvcost($idp); 
													$query .="INSERT INTO sl_purchaseorders_items SET ID_purchaseorders = '$in{'id_purchaseorders'}' , ID_products = '$idp' , Qty = '$qty' , Received = 0 , Price = '$cost', Date = CURDATE(), Time = CURTIME(),ID_admin_users = $usr{'id_admin_users'};";
											}
									}else{
											$cost = load_sltvcost($rec->{'ID_sku_products'});
											$query .="INSERT INTO sl_purchaseorders_items SET ID_purchaseorders = '$in{'id_purchaseorders'}' , ID_products = '$rec->{'ID_sku_products'}' , Qty = '$rec->{'Quantity'}' , Received = 0 , Price = '$cost', Date = CURDATE(), Time = CURTIME(),ID_admin_users = $usr{'id_admin_users'};";
									}
							}
							
							my ($stp_pi) = Do_mSQL("$query");
							
							## Verificamos que se hayan creado los Items
							my ($sthc) = &Do_SQL("SELECT COUNT(*) FROM sl_purchaseorders_items WHERE ID_purchaseorders = '$in{'id_purchaseorders'}';");
							if($sthc->fetchrow <= 0){
									$va{'message_dp'} .= "<br>Error: Impossible to create the items for PO $in{'id_purchaseorders'}";
									return;
							}else{
									&auth_logging('purchaseorder_items_created',$in{'id_purchaseorders'});
									$va{'message_dp'} .= "<br>OK: Items for PO $in{'id_purchaseorders'} Created ";
							}
					}	
			}
			
			## Recepcion de PO
			my ($sth5) = &Do_SQL("SELECT ID_wreceipts FROM sl_wreceipts WHERE ID_purchaseorders = '$in{'id_purchaseorders'}' AND Status = 'Processed';");
			$id_wreceipt = $sth5->fetchrow();

			## Esta recibida la mercancia?
			if(int($id_wreceipt) == 0){

				$in{'id_vendors'} = &load_name('sl_purchaseorders','ID_purchaseorders',$in{'id_purchaseorders'},'ID_vendors') if!$in{'id_vendors'};
				my ($sthwr) = &Do_SQL("INSERT INTO sl_wreceipts SET ID_vendors = '$in{'id_vendors'}', ID_purchaseorders = '$in{'id_purchaseorders'}',ReceivedFrom='Dropshipper', Description='Dropshipper Shipment', Type='Warehouse Receipt', Status='In Process', Date=CURDATE(), Time=CURTIME(), ID_admin_users = '$usr{'id_admin_users'}';");
				$id_wreceipt = $sthwr->{'mysql_insertid'};
				
				if(int($id_wreceipt) == 0){
						$va{'message_dp'} .= "<br>Error: Impossible to create Warehouse Receipt";
						return;
				
				}else{
						&auth_logging('wreceipt_created',$id_wreceipt);
						$va{'message_dp'} .= "<br>OK: WReceipt $id_wreceipt Created ";

						my ($tmp_sthwi) = &Do_SQL("SELECT ID_products, Qty FROM sl_purchaseorders_items WHERE ID_purchaseorders = '$in{'id_purchaseorders'}';"); 
						
						while( my( $tmp_id_products, $tmp_qty ) = $tmp_sthwi->fetchrow_array() )
						{
							my ($sthwi) = &Do_SQL("INSERT INTO sl_wreceipts_items VALUES (0, $id_wreceipt, '$tmp_id_products', '', '$tmp_qty', CURDATE(), CURTIME(), $usr{'id_admin_users'} );"); 
						}

						my ($sthwic) = &Do_SQL("SELECT COUNT(*) FROM sl_wreceipts_items WHERE ID_wreceipts = '$id_wreceipt';");
						if($sthwic->fetchrow <= 0){
								$va{'message_dp'} .= "<br>Error: Impossible to create the items for Warehose Receipt #$id_wreceipt";
								return;
						}else{
								my $wquery = '';


								my ( $tmp_sth_wquery ) = &Do_SQL("SELECT ID_products, Qty FROM sl_wreceipts_items WHERE ID_wreceipts = '$id_wreceipt';");
								while( my ( $tmp_id_products, $tmp_qty ) = $tmp_sth_wquery->fetchrow_array() )
								{
									$wquery .= "INSERT INTO sl_warehouses_location VALUES( 0,'$id_warehouses','$tmp_id_products','A100A','$tmp_qty',CURDATE(),CURTIME(),'$usr{'id_admin_users'}' );";
									$wquery .= "INSERT INTO sl_skus_trans VALUES( 0,$tmp_id_products,'Purchase','$id_wreceipt','sl_wreceipts',$tmp_qty,'',CURDATE(),CURTIME(),'$usr{'id_admin_users'}');";
								}

								my ( $tmp_sth_wquery ) = &Do_SQL("SELECT ID_products, Qty, Price FROM sl_purchaseorders_items WHERE ID_purchaseorders = '$in{'id_purchaseorders'}';");
								while( my ( $tmp_id_products, $tmp_qty, $tmp_price ) = $tmp_sth_wquery->fetchrow_array() )
								{
									$wquery .= "INSERT INTO sl_skus_cost VALUES ( 0, '$tmp_id_products', '$in{'id_purchaseorders'}','$id_warehouses','sl_purchaseorders', '$tmp_qty', '$tmp_price', CURDATE(), CURTIME(), '$usr{'id_admin_users'}' );";
								}

								$wquery .= "UPDATE sl_purchaseorders_items SET Received=Qty WHERE ID_purchaseorders = '$in{'id_purchaseorders'}';";
								$wquery .= "UPDATE sl_wreceipts SET Status='Processed' WHERE ID_wreceipts = '$id_wreceipt';";
								$wquery .= "UPDATE sl_purchaseorders SET Status = 'Received' WHERE ID_purchaseorders = '$in{'id_purchaseorders'}';";
								
								my ($stw) = Do_mSQL("$wquery");
								

								if($stw){
									$va{'message_dp'} .= "<br>OK: PO  and WReceipt Received ";

							      
									&auth_logging('warehouses_location_added',$id_wreceipt);
									&auth_logging('sku_trans_added',$id_wreceipt);
									&auth_logging('sku_cost_added',$id_wreceipt);
									&auth_logging('purchaseorder_item_updated',$in{'id_purchaseorders'});
									&auth_logging('wreceipt_updated',$id_wreceipt);
									&auth_logging('purchaseorder_received',$in{'id_purchaseorders'});

									my ($sthf) = &Do_SQL("SELECT Price,Qty FROM sl_purchaseorders_items WHERE ID_purchaseorders = '$in{'id_purchaseorders'}';");
									while(my($cost,$qty) = $sthf->fetchrow()){
										## Movimientos de contabilidad
										my @params = ($in{'id_purchaseorders'},$qty,$cost);
										&accounting_keypoints('po_wreceipt_dropship', \@params );
									}

								}else{
									$va{'message_dp'} .= "<br>Error: Impossible to receive the merchandise";
								}
						}
				}
			}


			## Scan de la orden
			$in{'shpdate'} = &get_sql_date(0);
			$in{'id_warehouses'} = $id_warehouses;

			my $upcs = &get_bulk_products('orders',$in{'id_orders'});
			  
			if($upcs ne ''){
  
				if($in{'tracking'} ne ''){
					$in{'tracking'} =  $cfg{'prefixentershipment'} . $in{'id_orders'} . "\r\n" . $in{'tracking'} . &get_bulk_products('orders',$in{'id_orders'});
				}else{
					$in{'tracking'} =  $cfg{'prefixentershipment'} . $in{'id_orders'} . "\r\n" . $upcs;
				}


				$in{'fc_dropshipp_return'} = 1;
				$status = &entershipment();
			

				$script_url =~ s/admin\.cgi/dbman\.cgi/;
				$va{'message'} = "$va{'message_dp'}<br>$va{'message'}<br><br> Wanna check the order <a href=\"$script_url?cmd=orders&view=$in{'id_orders'}\">$in{'id_orders'}</a> ?";
				foreach $key (keys %in)
				{
					if($key !~ /^[cmd|e]$/){
						delete($in{$key});
					}
				}
			}else{
				$va{'message'} = "$va{'message'}<br> Missing UPCS";
			}

		}
		
	}
	print "Content-type: text/html\n\n";
	print &build_page('orders_dropshipp.html');

}

sub validate_orders_dropshipp{
# --------------------------------------------------------
# Forms Involved: 
# Created on: 25 Aug 2010 18:32:09
# Author: MCC C. Gabriel Varela S.
# Description :   
# Parameters :
	my $err=0;
	
	
	if (!$in{'id_orders'} or int($in{'id_orders'}) <= 0){
		$error{'id_orders'} = &trans_txt('required');
		++$err;
	}else{
		my ($sth) = &Do_SQL("SELECT COUNT(*) FROM sl_orders_products WHERE ID_orders = '$in{'id_orders'}' AND Status='Active' AND (ShpDate IS NULL OR Shpdate = '' OR Shpdate = '0000-00-00');");
		if($sth->fetchrow() == 0){
			$error{'id_orders'} = &trans_txt('invalid');
			++$err;
		}
	}

	if(!$in{'id_products1'} and !$in{'id_products2'} and !$in{'id_products3'} and !$in{'id_products4'} and !$in{'id_products5'}){
		$error{'id_products1'} = &trans_txt('invalid');
		++$err;
	}
	
	$in{'id_purchaseorders'} = int($in{'id_purchaseorders'});
	$in{'id_vendors'} = int($in{'id_vendors'});
	if(!$in{'id_purchaseorders'} and !$in{'id_vendors'}){
			$error{'id_purchaseorders'} = &trans_txt('invalid');
			$error{'id_vendors'} = &trans_txt('invalid');
			++$err;
			$va{'message'} = 'You have to choose a PO or a Vendor to create the PO for this Shipp';
	}
	
	if($in{'id_products1'} and length($in{'id_products1'})<9){
		$error{'id_products1'} = "12312321".&trans_txt('invalid');
		++$err;
	}
	if($in{'id_products2'} and length($in{'id_products2'})<9){
		$error{'id_products2'} = &trans_txt('invalid');
		++$err;
	}
	if($in{'id_products5'} and length($in{'id_products5'})<9){
		$error{'id_products5'} = &trans_txt('invalid');
		++$err;
	}
	if($in{'id_products3'} and length($in{'id_products3'})<9){
		$error{'id_products3'} = &trans_txt('invalid');
		++$err;
	}
	if($in{'id_products4'} and length($in{'id_products4'})<9){
		$error{'id_products4'} = &trans_txt('invalid');
		++$err;
	}
	
	if($in{'id_products5'}and length($in{'id_products5'})<9){
		$error{'id_products5'} = &trans_txt('required');
		++$err;
	}

#	if($in{'id_purchaseorders'}){
#			my ($sth) = &Do_SQL("SELECT COUNT(*) FROM sl_purchaseorders WHERE ID_purchaseorders = '$in{'id_purchaseorders'}' AND Status != 'Received';");
#
#			if($sth->fetchrow() == 0){
#				$error{'id_purchaseorders'} = &trans_txt('invalid');
#				++$err;
#			}
#	}

	return $err;
}


sub wholesale{
# --------------------------------------------------------
# Created on: 
# Author: Roberto Barcenas
# Description : 
# Parameters : 
#


  my $page=$in{'cmd'};
  my $cmd=$in{'cmd'};

  if($in{'view'}){
    $cmd .= '_view';
  }elsif($in{'modify'}){
  
  }elsif($in{'search'}){
    $cmd .= '_search';
  }
  
  if($cmd ne $in{'cmd'} and defined &$cmd){
    $flag=1;
    &$cmd;
  }


  if($in{'action'})
	{
	
	  ## Add return
	  if($in{'add'}){	 
	    if(!$in{'id_orders'}){
	      $error{'id_orders'} = &trans_txt('required');
	      $err++;
	    }else{
	    
		my ($sth) = &Do_SQL("SELECT COUNT(*) FROM sl_orders,sl_orders_products WHERE sl_orders.ID_orders=sl_orders_products.ID_orders AND sl_orders.ID_orders='$in{'id_orders'}' AND sl_orders_products.Status IN ('Active','Exchange','ReShip') AND SalePrice >= 0 AND sl_orders.Status = 'Shipped' AND LEFT(sl_orders_products.ID_products,1)<>'6' AND (Related_ID_products IS NULL OR LEFT(Related_ID_products,1)=4);");	    
		if($sth->fetchrow() == 0){
			$error{'id_orders'} = &trans_txt('invalid');
			$err++;
		}        
	}
	    $in{'generalpckgcondition'} = 'Opened/Customer Box' if !$in{'generalpckgcondition'};
      	
      if(!$err){
        $in{'type'}='Returned for Refund';
        $in{'prodcondition'}='New';
        $in{'meraction'}='Refund';
        $in{'status'}='In Process';
        my $id_customers = &load_name('sl_orders','ID_orders',$in{'id_orders'},'ID_customers');
        my ($str) =  &Do_SQL("INSERT INTO sl_returns SET ID_customers='$id_customers' , ID_orders='$in{'id_orders'}', Type='$in{'type'}', generalpckgcondition='$in{'generalpckgcondition'}', receptionnotes='".&filter_values($in{'receptionnotes'})."', ProdCondition='$in{'prodcondition'}', merAction='$in{'meraction'}', Status='$in{'status'}', Date=CURDATE(), Time=CURTIME(), ID_admin_users = $usr{'id_admin_users'}");
        
        if($str->rows() > 0){
          delete($in{'action'});
          delete($in{'add'});
          my $lastid = $str->{'mysql_insertid'};
          
          my ($sth) = &Do_SQL("INSERT INTO sl_returns_notes(ID_returns, Notes, Type, Date, Time, ID_admin_users) VALUES('$lastid','New Return for Exportation Order Added','Reception',CURDATE(),CURTIME(),'$usr{'id_admin_users'}');");
				  &auth_logging('returns_exportation_added',$lastid);
          
          $in{'view'}=$lastid; 
          $page=$in{'cmd'}.'_view';
          $flag=1;
          &$page;
        }else{
          $va{'message'}=&trans_txt('opr_orders_caperror');
        }
        
      }else{
        $va{'message'}=&trans_txt('reqfields_short');
      }	
      	  
	  
	  }
		
	}
  
  if(!$flag){
	  print "Content-type: text/html\n\n";
	  print &build_page($in{'cmd'}.'.html');
  }
}


sub wholesale_view{
# --------------------------------------------------------
# Created on: 
# Author: Roberto Barcenas
# Description : 
# Parameters : 
#  

	$in{'db'} = 'sl_returns';
	&load_cfg('sl_returns');
	my (%rec) = &get_record($db_cols[0],$in{'view'},$in{'db'});
	if ($rec{lc($db_cols[0])}){
		foreach $key (sort keys %rec) {
			$in{lc($key)} = $rec{$key};
		}
	}

  	## Add Part
  	if($in{'add_item'} and $in{'total_items'} > 0 ){
  
    	$status='Conforming';
    	
    	##Check each part
    	for $i(1..$in{'total_items'}){
    
      		## Item returned
      		if($in{'qtyreturned_'.$i} > 0 and $in{'id_warehouses_'.$i} > 0){

        		##Check againts previous?
        		my $sent=int($in{'qtysent_'.$i});
        		my $returned=int($in{'qtyreturned_'.$i});
        		my $id_parts=$in{'idp_'.$i};
        		my $upc=&load_name('sl_skus','ID_sku_products',$id_parts,'UPC');
        
        		if($upc){
        
	        		my ($sth) = &Do_SQL("SELECT IF(SUM(sl_returns_upcs.Quantity) + $returned > SUM(sl_orders_products.Quantity) ,1,0)AS invalid FROM sl_orders_products INNER JOIN sl_returns ON sl_orders_products.ID_orders = sl_returns.ID_orders LEFT JOIN sl_returns_upcs ON sl_returns.ID_returns = sl_returns_upcs.ID_returns WHERE sl_returns.ID_returns='$in{id_returns}' AND UPC='$upc' AND ID_products='$id_parts'; ");;
	        		my ($invalid) = $sth->fetchrow();
	        
	        		## Adding New Part
	        		if(!$invalid){
	          			my ($sth2) = &Do_SQL("INSERT INTO sl_returns_upcs SET ID_returns='$in{id_returns}', UPC='$upc', ID_warehouses='$in{'id_warehouses_'.$i}', Status='$status', Location='', Quantity='$returned', Date=CURDATE(), Time=CURTIME(), ID_admin_users='$usr{'id_admin_users'}';");  
	          			&auth_logging('upc_added',$in{'id_returns'});
	        		}
	  
	  			}else{
	  				$va{'message'} .= $id_parts . " - Invalid UPC<br>";	
	  			}
        
      		}		
    
    	}
  
  	}	
  
	## Drop Return Item
	if($in{'drop_item'} and int($in{'drop_item'}) > 0 and int($in{'view'}) > 0){
	 	my ($sth) = &Do_SQL("DELETE FROM sl_returns_upcs WHERE ID_returns_upcs='$in{'drop_item'}';");
	 	&auth_logging('upc_deleted',$in{'id_view'});
	}
  

	## Process Returned
	if($in{'done'} and int($in{'view'}) > 0){

		if($in{'status'} eq 'In Process'){

    		$in{'meraction'}='Refund';
        	my $id_returns = int($in{'view'});
        	my $id_orders = &load_name('sl_returns','ID_returns',$id_returns,'ID_orders');
        	my ($sth) = &Do_SQL("SELECT ID_returns_upcs, UPC, ID_warehouses, Quantity FROM sl_returns_upcs WHERE ID_returns = '$id_returns'");

			my ($order_type, $ctype);
			my ($sth) = &Do_SQL("SELECT Ptype, Type FROM sl_orders INNER JOIN sl_customers USING(ID_customers) WHERE ID_orders = '$id_orders';");
			($order_type, $ctype) = $sth->fetchrow();


        	while(my($id_upc,$upc,$id_warehouses,$quantity) = $sth->fetchrow()){
          
        		my $id_product=&load_name('sl_skus','UPC',$upc,'ID_sku_products');
        							#("SELECT SalePrice/Quantity AS SalePrice, Cost/Quantity AS Cost, Cost AS TCost FROM sl_orders_products WHERE ID_orders = '$id_orders' AND Related_ID_products='$id_product' AND Quantity >= '$quantity' AND Status IN ('Active','Exchange','ReShip') AND ShpDate IS NOT NULL AND ShpDate <> '' AND ShpDate <> '0000-00-00' LIMIT 1;"); 
        		my ($sthd) = &Do_SQL("SELECT sl_orders_products.SalePrice/sl_orders_products.Quantity AS SalePrice, IF(sl_orders_parts.Cost IS NOT NULL AND sl_orders_parts.Cost > 0, sl_orders_parts.Cost, IF( sl_orders_products.Cost IS NULL, 0, sl_orders_products.Cost/sl_orders_products.Quantity)) AS Cost, sl_orders_products.Cost AS TCost, sl_orders_parts.Cost_Adj FROM sl_orders_parts INNER JOIN sl_orders_products USING(ID_orders_products) WHERE ID_orders = '$id_orders' AND Related_ID_products='$id_product' AND 	Quantity >= '$quantity' AND Status IN ('Active','Exchange','ReShip') AND ShpDate IS NOT NULL AND ShpDate <> '' AND 	ShpDate <> '0000-00-00' LIMIT 1;");
         		my ($saleprice,$cost,$pcost, $cost_adj) = $sthd->fetchrow();
          
          	#	#Determine product Cost
			#	if(!$cost or $cost < 0){
			#		$sthcost=&Do_SQL("SELECT IF(sl_orders_parts.Cost IS NOT NULL AND sl_orders_parts.Cost > 0,sl_orders_parts.Cost,IF(sl_orders_products.Cost IS NULL,0,sl_orders_products.Cost)) FROM sl_orders_parts INNER JOIN sl_orders_products ON sl_orders_products.ID_orders_products = sl_orders_parts.ID_orders_products WHERE ID_orders = $id_orders AND ID_parts='".substr($id_product,5,4)."';");
            #		$cost = $sthcost->fetchrow();
            #		$pcost = $cost * $quantity;
          	#	}
          		$cost=0 if !$cost;
          		$cost_adj=0 if !$cost_adj;
						
				## warehouses_location
				my($sthinv);
				my ($sthwl) = &Do_SQL("/* returns_exportartion */ SELECT COUNT(*) FROM sl_warehouses_location WHERE ID_warehouses='$id_warehouses' AND ID_products='$id_product' AND Quantity > 0;");

				if($sthwl->fetchrow() > 0){
					$sthinv=&Do_SQL("UPDATE sl_warehouses_location SET Quantity = Quantity + $quantity WHERE ID_warehouses='$id_warehouses' AND ID_products='$id_product' AND Quantity > 0 ORDER BY Date LIMIT 1;");
				}else{
					$sthinv=&Do_SQL("/* returns_exportartion */ INSERT INTO sl_warehouses_location set ID_warehouses=$id_warehouses,ID_products=$id_product,Location='A00A',Quantity='$quantity',Date=CURDATE(),Time=CURTIME(),ID_admin_users='$usr{'id_admin_users'}'");
					&auth_logging('warehouses_location_added',$sthinv->{'mysql_insertid'});
				}

				## skus_cost	
				my ($sths1) = &Do_SQL("SELECT ID_skus_cost FROM sl_skus_cost WHERE ID_warehouses = $id_warehouses AND ID_products=$id_product AND Quantity > 0 AND Cost='$cost' AND Date=CURDATE() LIMIT 1;");
				if($sths1->rows() > 0){
					## Is there a record same day / same cost ?
					my($idscost1) = $sths1->fetchrow();
					&Do_SQL("/* 1 returns_exportartion */ UPDATE sl_skus_cost SET Quantity = Quantity + $quantity WHERE ID_skus_cost = $idscost1;");
				}else{
					## 
					my ($sths) = &Do_SQL("SELECT ID_skus_cost, Cost, Cost_Adj FROM sl_skus_cost WHERE ID_warehouses=$id_warehouses AND ID_products=$id_product AND Quantity > 0 ORDER BY Date DESC LIMIT 1;");
					my($idscost,$scost,$scost_adj) = $sths->fetchrow();

					if( ($scost == $cost) && ($scost_adj == $cost_adj) ){
			  			&Do_SQL("/* 2 returns_exportartion */ UPDATE sl_skus_cost SET Quantity = Quantity + $quantity WHERE ID_skus_cost = $idscost;");
					}else{
						my $sthsku=&Do_SQL("/* returns_exportartion */ INSERT INTO sl_skus_cost set ID_products=$id_product,ID_purchaseorders=$in{'id_returns'},Tblname='sl_returns',Cost=$cost, Cost_Adj=$cost_adj ,ID_warehouses=$id_warehouses,Quantity='$quantity',Date=CURDATE(),Time=CURTIME(),ID_admin_users='$usr{'id_admin_users'}'");
				 	 	&auth_logging('sku_cost_added',$sthsku->{'mysql_insertid'});
					}

				}
					
				## Add negative orders_products
				my $tprice=$saleprice*$quantity*-1;
				my $tcost=$cost*$quantity*-1;
				my $tquantity=$quantity*-1;
				
				my ($tmp_sthn) = &Do_SQL("SELECT CONCAT(LEFT(ID_products,3)+1,'000000'), ID_orders, ID_packinglist, FP, SerialNumber FROM sl_orders_products WHERE ID_orders='$id_orders' ORDER BY ID_orders_products DESC LIMIT 1;");
				my ( $tmp_id_products, $tmp_id_orders, $tmp_id_packinglist, $tmp_fp, $tmp_serialnumber ) = $tmp_sthn->fetchrow_array();
				
				my ($sthn) = &Do_SQL("INSERT INTO sl_orders_products VALUES( 0,'$tmp_id_products', '$tmp_id_orders', '$tmp_id_packinglist','$id_product','$tquantity','$tprice','0.00','$tcost','0.00','0.00', '$tmp_fp', '$tmp_serialnumber', CURDATE(),'','',CURDATE(),'No','Returned',CURDATE(),CURTIME(),'$usr{'id_admin_users'}');");
				my $lastidp = $sthn->{'mysql_insertid'};
				&auth_logging('return_product_added',$lastidp);

				## Movimientos Contables
				my @params = ($id_orders,$id_product,$pcost);
				&accounting_keypoints('order_skus_backtoinventory_'. $ctype .'_'. $order_type, \@params );
				  
				my($sth)=&Do_SQL("INSERT INTO sl_returns_notes SET ID_returns='$id_returns', Notes='Return Processed: $quantity pieces of $idproduct Returned to ".&load_name('sl_warehouses','ID_warehouses',$id_warehouses,'Name')."($id_warehouses) Warehouse ',Type='ATC',Date=CURDATE(),Time=CURTIME(),ID_admin_users='$usr{'id_admin_users'}';");

				&add_order_notes_by_type($id_orders,"Return Processed: $quantity pieces of $idproduct Returned to ".&load_name('sl_warehouses','ID_warehouses',$id_warehouses,'Name')."($id_warehouses) Warehouse","Low");
				  
			} ## end while
	
			## Movimientos Contables
			my @params = ($id_orders,$in{'meraction'},0);
			&accounting_keypoints('order_skus_returnsolved_'. $ctype .'_'. $order_type, \@params );


	    	&Do_SQL("UPDATE sl_orders_payments SET Status = 'Cancelled' WHERE ID_orders =  $id_orders AND (Captured='No' OR Captured IS NULL) AND (CapDate IS NULL OR CapDate='0000-00-00'); ");

        	my ($sth2) = &Do_SQL("SELECT * FROM sl_orders_payments WHERE ID_orders = $id_orders AND Status = 'Approved' 
        	AND (Captured='Yes' OR (AuthCode IS NOT NULL AND AuthCode != '' AND AuthCode != '0000'))
		    ORDER BY ID_orders_payments DESC LIMIT 1;");
        	my ($rec2) = $sth2->fetchrow_hashref;

        	$queryPmt = '';
        	for my $i(1..9){
	        	$queryPmt .= ",PmtField$i = '".$rec2->{'PmtField'.$i.''}."' ";
       	 	}	

        	## Products + Tax + Shipping vs Payments already done
        	$sumatoria = &orderbalance($id_orders);
        	my $posteddate = "";
        	my $statuspayments='Approved';
        	$statuspayments='Credit' if($sumatoria<0);

        	if($sumatoria < 0.99*-1 or $sumatoria > 0.99){

	        	my ($sthpy) = &Do_SQL("INSERT INTO sl_orders_payments SET ID_orders = '$id_orders', Reason='$in{'meraction'}',
						Type= '$rec2->{'Type'}' $queryPmt , Amount = '$sumatoria' , PaymentDate = CURDATE(), PostedDate=CURDATE(),Status='$statuspayments',
						Date = CURDATE(),Time=CURTIME(),ID_admin_users='$usr{'id_admin_users'}';");
			    &auth_logging('orders_payments_added',$rec2->{'ID_orders'});
			    $lastidp = $sthpy->{'mysql_insertid'};
			    $in{'amount'}=$sumatoria;
			    &proccessamount($sumatoria,$id_orders,$lastid);	

        	}else{
	        	$sumatoria=0;
       	 	}
      		&recalc_totals($id_orders);
			my($sthrt)=&Do_SQL("UPDATE sl_returns SET Amount='$sumatoria',Status='Resolved' WHERE ID_returns = '$id_returns'");			  
			delete($in{'done'});
			$va{'message'} .= "\n Return Resolved."; 

      	}else{
     		$va{'message'} = 'The Status of the return is not correct';
      	}	
  	}


######
######
######
######
######
  
  ## List of Parts Sent
  my ($sth) = &Do_SQL("SELECT COUNT(*) FROM sl_returns,sl_orders_products WHERE sl_returns.ID_orders=sl_orders_products.ID_orders AND ID_returns='$in{'id_returns'}' AND sl_orders_products.Status IN ('Active','Exchange','ReShip') AND LEFT(sl_orders_products.ID_products,1)<>'6' AND LEFT(Related_ID_products,1)=4 ;");	    
  if($sth->fetchrow() > 0){
    my (@c) = split(/,/,$cfg{'srcolors'});
    my $i=1;
    my ($sth) = &Do_SQL("SELECT sl_orders_products.ID_orders_products,Related_ID_products,Quantity FROM sl_returns,sl_orders_products WHERE sl_returns.ID_orders=sl_orders_products.ID_orders AND ID_returns='$in{'id_returns'}' AND sl_orders_products.Status IN ('Active','Exchange','ReShip') AND LEFT(sl_orders_products.ID_products,1)<>'6' AND LEFT(Related_ID_products,1)=4 ORDER BY sl_orders_products.ID_orders_products;");
    while(my($idop,$id_parts,$qtysent) = $sth->fetchrow()){
 
        $d = 1 - $d;   
        my $pname = &load_name('sl_parts','ID_parts',substr($id_parts,5),'Name');
        
        $va{'partresults'} .= qq|<tr bgcolor='$c[$d]'>
  <td nowrap="nowrap">&nbsp;</td>      
  <td nowrap="nowrap">|.&format_sltvid($id_parts).qq|</td>
  <td nowrap="nowrap">$pname</td>
  <td nowrap="nowrap">$qtysent</td>
  <td nowrap="nowrap">
    <input name="qtyreturned_$i" id="qtyreturned_$i" type="text" size="5" value="[in_qtyreturned_$i]" onFocus='focusOn( this )' onBlur='focusOff( this )'>
    <input name="idp_$i" id="idp_$i" type="hidden" value="$id_parts">
    <input name="qtysent_$i" id="qtysent_$i" type="hidden" value="$qtysent">
  </td>
  <td nowrap="nowrap"><select name="ID_warehouses_$i" id="ID_warehouses_$i" onFocus='focusOn( this )' onBlur='focusOff( this )'>
			<option value="">---</option>
			[fc_build_select_warehouses]
		</select>
  </td>
</tr>|;
        $i++;
    }
   $va{'total_items'}=qq|<input name="total_items" id="total_items" type="hidden" value="$i">|; 
  }else{    
    $va{'partresults'} .= qq|<tr><td colspan="5" align="center">|.&trans_txt('not_match').qq|</td></tr>|;
  }
  
  $va{'statusmsg'} =  $in{'status'} ne 'In Process' ? '' : '<strong>'.&trans_txt('change_to'). "</strong> : <a href='$script_url?cmd=$in{'cmd'}&view=$in{'id_returns'}&done=1'>Resolved</a>";
  
  print "Content-type: text/html\n\n";
  print &build_page($in{'cmd'}.'_view.html');

}


sub wholesale_search{
# --------------------------------------------------------
# Created on: 07/26/2011 11:33:22 AM 
# Author: Roberto Barcenas
# Description : 
# Parameters : 
#

  if($in{'search'} eq 'form'){
    print "Content-type: text/html\n\n";
    print &build_page($in{'cmd'}.'_search.html');
  }else{
  
    if($in{'id_returns'}){
      
      $in{'view'}=$in{'id_returns'};
      &wholesale_view();
      return;
    }
    
    $in{'so'}='' if !$in{'so'};
    my $query = '';

    if($in{'search'} eq 'listall'){
      $query = "";
    }
    
    if($in{'id_orders'}){
      $query .= " AND ID_orders='$in{'id_orders'}' ";
    }
    
    if($in{'from_date'} and $in{'to_date'}){
      $query .= " AND sl_returns.Date BETWEEN '$in{'from_date'}' AND '$in{'to_date'}' ";
    
    }elsif($in{'from_date'}){
      $query .= " AND sl_returns.Date >= '$in{'from_date'}' ";
    
    }elsif($in{'to_date'}){
      $query .= " AND sl_returns.Date <= '$in{'to_date'}' ";
    
    }


    my ($sth) = &Do_SQL("SELECT COUNT(*) FROM sl_returns INNER JOIN sl_returns_notes ON sl_returns.ID_returns = sl_returns_notes.ID_returns WHERE Notes='New Return for Exportation Order Added' $query ;");
	  $va{'matches'} = $sth->fetchrow();
	  if ($va{'matches'}>0){
		  (!$in{'nh'}) and ($in{'nh'}=1);
		  $first = ($in{'nh'} - 1) * $usr{'pref_maxh'};			
		  ($va{'pageslist'},$qs) = &pages_list($in{'nh'},"/cgi-bin/mod/$usr{'application'}/admin",$va{'matches'},$usr{'pref_maxh'});
		  my (@c) = split(/,/,$cfg{'srcolors'});

      my ($sth) = &Do_SQL("SELECT sl_returns.ID_returns,ID_orders,receptionnotes,sl_returns.Status,sl_returns.Date FROM sl_returns INNER JOIN sl_returns_notes ON sl_returns.ID_returns = sl_returns_notes.ID_returns WHERE Notes='New Return for Exportation Order Added' $query ORDER BY ID_returns $in{'so'} LIMIT $first,$usr{'pref_maxh'};");
      while(my($id_returns,$id_orders,$receptionnotes,$status,$date) = $sth->fetchrow()){ 
        $d = 1 - $d;
			  $choices = &load_choices($rec->{'ID'});
			  $va{'searchresults'} .= "<tr bgcolor='$c[$d]' onmouseover='m_over(this)' onmouseout='m_out(this)'>\n";
			  $va{'searchresults'} .= "<td>&nbsp;</td>\n";
			  $va{'searchresults'} .= "<td align='left' nowrap='nowrap'><a href='/cgi-bin/mod/wms/admin?cmd=$in{'cmd'}&view=$id_returns' title='View Return'>$id_returns</td>\n";
			  $va{'searchresults'} .= "<td align='left' nowrap='nowrap'><a href='/cgi-bin/mod/wms/dbman?cmd=opr_orders&view=$id_orders' title='View Order'>$id_orders</td>\n";
			  $va{'searchresults'} .= "<td align='left'>$receptionnotes</td>\n";
			  $va{'searchresults'} .= "<td align='left' nowrap='nowrap'>$date</td>\n";
			  $va{'searchresults'} .= "<td align='left' nowrap='nowrap'>$status</td>\n";
			  $va{'searchresults'} .= "</tr>\n";
      }
    }else{
      $va{'searchresults'} .= "<tr bgcolor='$c[$d]' onmouseover='m_over(this)' onmouseout='m_out(this)'>\n";
      $va{'searchresults'} .= "<td colspan='6' align='center'>".&trans_txt('search_nomatches')."</td>\n";
      $va{'searchresults'} .= "</tr>\n";
    }
    
    print "Content-type: text/html\n\n";
    print &build_page($in{'cmd'}.'_list.html');
    
    
  }

}

##################################################################
##########     RMAS     	######################
##################################################################
sub customer_search {
# --------------------------------------------------------
# Created on: 5/30/2008 10:34:29 AM
# Last Modified on: 7/8/2008 4:25 PM
# Last Modified by: Jose Ramirez
# Author: Jose
# Description : Search Customer
# Parameters : None
# Last Modified RB: 01/07/09  16:47:08 -- Fixed search by customer data


	my ($query,$tquery,$tbl_name);
	$in{'id_customers'} = int($in{'id_customers'});
	$in{'id_orders'} = int($in{'id_orders'});
	$query = "";
	if ($in{'id_customers'}>0){
		my ($sth) = &Do_SQL("SELECT COUNT(*) FROM sl_customers LEFT JOIN sl_orders ON sl_customers.ID_customers=sl_orders.ID_orders WHERE sl_customers.ID_customers='$in{'id_customers'}' AND sl_orders.Status = 'Shipped'");
		if ($sth->fetchrow()>0){
			print "Location: /cgi-bin/mod/wms/dbman?cmd=opr_returns&add=1&id_customers=$in{'id_customers'}\n\n";
			return;
		}
	}elsif($in{'id_orders'}>0){
		my ($sth) = &Do_SQL("SELECT sl_customers.ID_customers FROM sl_customers LEFT JOIN sl_orders ON sl_customers.ID_customers=sl_orders.ID_orders WHERE ID_orders='$in{'id_orders'}' AND sl_orders.Status = 'Shipped'");
		$in{'id_customers'} = $sth->fetchrow();
		if ($in{'id_customers'}>0){
			print "Location: /cgi-bin/mod/wms/dbman?cmd=opr_returns&add=1&id_customers=$in{'id_customers'}&id_corders=$in{'id_orders'}\n\n";
			return;
		}
	}else{
		#GV Inicia modificaci?n 06jun2008
		if($in{'lastname'}){
			$in{'lastname1'}= &filter_values($in{'lastname'});
		}
		if($in{'phone'}){
			$in{'phone1'}= &filter_values($in{'phone'});
			$in{'phone2'}= &filter_values($in{'phone'});
			$in{'cellphone'}= &filter_values($in{'phone'});
		}
		#GV Termina modificaci?n 06jun2008
		delete($in{'id_customers'});
		&load_cfg('sl_customers');
		$tquery = &query('sl_customers',1);
		($tquery) and ($query .= " AND ($tquery)");
	}
#&cgierr;
	#GV Inicia 22may2008
	if($in{'rmanum'}){
		$query.=" and ID_orders in (SELECT sl_orders.ID_orders
							FROM sl_rma
							left JOIN sl_orders_products ON ( sl_rma.ID_orders_products = sl_orders_products.ID_orders_products ) 
							left JOIN sl_orders ON ( sl_orders_products.ID_orders = sl_orders.ID_orders ) 
							WHERE num_rma =$in{'rmanum'}) ";
	}
	#GV Termina 22may2008
	
	$va{'matches'} = 1;
	$va{'pageslist'} = 1;	
	(!$in{'nh'}) and ($in{'nh'}=1);
	$first = ($in{'nh'} - 1) * $usr{'pref_maxh'};
	my (@c) = split(/,/,$cfg{'srcolors'});
	my ($sth) = &Do_SQL("SELECT * FROM sl_customers LEFT JOIN sl_orders ON sl_customers.ID_customers=sl_orders.ID_orders WHERE sl_orders.Status = 'Shipped' GROUP BY sl_customers.ID_customers");
	$va{'matches'} = $sth->rows();
	
	if ($va{'matches'} == 1){
		$in{'id_customers'} = $rec->{'ID_customers'};
		print "Location: /cgi-bin/mod/wms/dbman?cmd=opr_returns&add=1&id_customers=$in{'id_customers'}&id_corders=$in{'id_orders'}\n\n";
		return;
	}elsif ($va{'matches'}>0){
		my ($sth) = &Do_SQL("SELECT * FROM sl_customers LEFT JOIN sl_orders ON sl_customers.ID_customers=sl_orders.ID_orders WHERE sl_orders.Status = 'Shipped' GROUP BY sl_customers.ID_customers $in{'so'} LIMIT $first,$usr{'pref_maxh'};");
		($va{'pageslist'},$qs) = &pages_list($in{'nh'},"/cgi-bin/mod/$usr{'application'}/admin",$va{'matches'},$usr{'pref_maxh'});
		while ($rec = $sth->fetchrow_hashref){
			$d = 1 - $d;
			#GV Inicia Modificaci?n 26may2008 Se incluye al final &genrmanum=$in{'rmanum'}
			$cadrma="";
			if($in{'rmanum'}){
				my $sthin=&Do_SQL("Select ID_orders_products from sl_rma where num_rma=$in{'rmanum'}");
				my $recin=$sthin->fetchrow();
				#$cadrma="&genrmanum=$in{'rmanum'}";
				$cadrma="&id_orders_products=$recin";
			}
			$va{'searchresults'} .= "<tr bgcolor='$c[$d]' onmouseover='m_over(this)' onmouseout='m_out(this)' onClick=\"trjump('/cgi-bin/mod/wms/dbman?cmd=opr_returns&add=1&id_customers=$rec->{'ID_customers'}$cadrma')\">\n";
			#GV Termina Modificaci?n 26may2008
			$va{'searchresults'} .= "  <td class='smalltext' valign='top' align='center'>$rec->{'ID_customers'}</td>\n";
			$va{'searchresults'} .= "  <td class='smalltext' valign='top'>$rec->{'FirstName'} $rec->{'LastName1'} $rec->{'LastName2'}</td>\n";
			$va{'searchresults'} .= "  <td class='smalltext' valign='top'>$rec->{'State'}</td>\n";
			$tel = "";
			if($rec->{'Phone1'}){
				$tel .= "$rec->{'Phone1'}<br>";
			}
			if($rec->{'Phone2'}){
				$tel .= "$rec->{'Phone2'}<br>";
			}
			if($rec->{'Cellphone'}){
				$tel .= "$rec->{'Cellphone'}<br>";
			}										
			$va{'searchresults'} .= "  <td class='smalltext' valign='top'>$tel</td>\n";
			$va{'searchresults'} .= "  <td class='smalltext' valign='top'>$rec->{'Status'}</td>\n";
			my ($sth2) = &Do_SQL("SELECT COUNT(*) FROM sl_orders WHERE ID_customers='$rec->{'ID_customers'}' AND Status NOT IN ('Cancelled','System Error')");
			$va{'searchresults'} .= "  <td class='smalltext' valign='top' align='center'>".&format_number($sth2->fetchrow)."</td>\n";
			$va{'searchresults'} .= "</tr>\n";
		}
	}else{
		$va{'pageslist'} = 1;
		$va{'searchresults'} = qq|
		<tr>
			<td colspan='5' align="center">|.&trans_txt('search_nomatches').qq|</td>
		</tr>\n|;
	}
	$va{'page_title'} = trans_txt("pageadmin");
	print "Content-type: text/html\n\n";
	print &build_page('opr_returns_custlist.html');
}

##################################################################
##########     RMAS     	######################
##################################################################
sub opr_returns_add {
# --------------------------------------------------------
# Created on: 5/30/2008 10:34:29 AM
	&load_cfg('sl_customers');
	$in{'sb'} = 'Date';
	$in{'so'} = 'DESC';
	print "Content-type: text/html\n\n";
	print &build_page('opr_returns_add.html');

}

sub packing_search {
# --------------------------------------------------------
	&cgierr;
}

sub packing_topack {
# --------------------------------------------------------
	my (@oids,$err);
	if ($in{'search'} and !$in{'oids'}){
		foreach my $key (keys %in){
			if ($key =~ /oid_(\d+)/){
				push(@oids,$1);
			}
		}
	}elsif ($in{'search'} and $in{'oids'}){
		@oids =  split(/,/, $in{'oids'});
	}
	my (@c) = split(/,/,$cfg{'srcolors'});
	#&cgierr
	if ($#oids>=0){
		$in{'oids'} = join(',',@oids);
		if (!$in{'id_warehouses'}){
			my($sth) = &Do_SQL("SELECT `ID_warehouses` FROM `sl_skus_trans` WHERE 1 GROUP BY `ID_warehouses` ORDER BY COUNT(*) DESC LIMIT 0,1");
			$in{'id_warehouses'} = $sth->fetchrow();
		}
		my ($i,$err,%transfer);
		my($sth) = &Do_SQL("SELECT idp, qty, Name, Model, UPC
							FROM 
							(
								SELECT related_ID_products AS idp, SUM(Quantity) AS qty
								FROM sl_orders_products 
								WHERE (Shpdate IS NULL OR Shpdate = '0000-00-00' AND Shpdate = '') AND (Tracking IS NULL OR Tracking = '') AND (ShpProvider IS NULL OR ShpProvider = '') 
								AND sl_orders_products.Status IN ('Active','ReShip','Exchange') AND ID_orders IN ($in{'oids'})
								AND LEFT(related_ID_products,1)=4
								GROUP BY related_ID_products
								
								 UNION
								 
							    SELECT 400000000 + ID_parts AS idp,SUM(pqty * Qty) AS qty
							    FROM sl_skus_parts INNER JOIN
							        (
							        SELECT GROUP_CONCAT(ID_orders)AS ido,sl_orders_products.ID_products AS idp,SUM(Quantity) AS pqty
							
							        FROM sl_orders_products
							        WHERE (Shpdate IS NULL OR Shpdate = '0000-00-00' AND Shpdate = '') AND (Tracking IS NULL OR Tracking = '') AND (ShpProvider IS NULL OR ShpProvider = '') 
							        AND sl_orders_products.Status IN ('Active','ReShip','Exchange') AND ID_orders IN ($in{'oids'})
							        AND (Related_ID_products IS NULL OR Related_ID_products = '') AND LENGTH(ID_products) = 9 AND LEFT(ID_products,1) < 4
							        GROUP BY ID_products
							    	  )tmp1
							    ON idp = ID_sku_products    
							    INNER JOIN sl_parts USING(ID_parts)
							    GROUP BY ID_parts
							) AS tmp2
							LEFT JOIN sl_parts ON idp=ID_parts+400000000
							LEFT JOIN sl_skus ON idp=ID_sku_products
							WHERE 1
							GROUP BY idp");
		while ( my $rec = $sth->fetchrow_hashref()){
			++$i;
			$d = 1 - $d;
			my($sth2) = &Do_SQL("SELECT Quantity, UPC, Location  FROM sl_warehouses_location
									LEFT JOIN sl_locations ON Location=Code
									WHERE sl_warehouses_location.ID_warehouses = $in{'id_warehouses'} AND ID_products = $rec->{'idp'} 
									AND Status='Active'
									ORDER BY sl_warehouses_location.Date ASC");
			my ($locations) = '';
			my ($to_pack) = $rec->{'qty'};
			$transfer{$rec->{'idp'}} = $to_pack;
			LOC: while ( my ($q,$upc,$loc) = $sth2->fetchrow_array()){
				if ($to_pack<=$q){
					$locations .= "$to_pack \@ $upc";
					$transfer{$rec->{'idp'}.'@'.$loc} = $to_pack;
					last LOC;
				}else{
					$locations .= "$q \@ $upc<br>";
					$transfer{$rec->{'idp'}.'@'.$loc} = $q;
					$to_pack -= $q;
				}
			}
			if (!$locations){
				$locations = "<span style='color:red;'>".&trans_txt('notavailable')."</span>";
				++$err;
			}
			$va{'searchresults'} .= "<tr bgcolor='$c[$d]' onmouseover='m_over(this)' onmouseout='m_out(this)'>\n";
			$va{'searchresults'} .= "  <td class='smalltext' valign='top'>$i</td>\n";
			$va{'searchresults'} .= "  <td class='smalltext' valign='top'>".&format_sltvid($rec->{'idp'})."</td>\n";
			$va{'searchresults'} .= "  <td class='smalltext' valign='top'>$rec->{'UPC'}</td>\n";
			$va{'searchresults'} .= "  <td class='smalltext' valign='top'>$rec->{'Name'}<br>$rec->{'Model'}</td>\n";
			$va{'searchresults'} .= "  <td class='smalltext' valign='top'>$rec->{'qty'}</td>\n";
			$va{'searchresults'} .= "  <td class='smalltext' valign='top'>$locations</td>\n";
			$va{'searchresults'} .= "</tr>\n";
		}
		if ($in{'finished'} and !$err and !$in{'id_manifests'}){
			#%error = %transfer;
			#&cgierr;
			## Creating The Manifest
			($sth) = &Do_SQL("INSERT INTO sl_manifests SET RequestedBy=$usr{'id_admin_users'}, AuthorizedBy=$usr{'id_admin_users'}, ProcessedBy=$usr{'id_admin_users'}, Comments='".&trans_txt('pack_comment').' '.$in{'oids'}."', Status='Completed', Date=CURDATE(), Time=CURTIME(), ID_admin_users='$usr{'id_admin_users'}'");
			$in{'id_manifests'} = $sth->{'mysql_insertid'};
			&check_pack_loc($in{'id_warehouses'});
			foreach $key (keys %transfer){
				if ($key =~ /(\d+)\@(.*)/){
					my ($status) = &move_inventory($in{'id_warehouses'},$2,$in{'id_warehouses'},'PACK',$1,$transfer{$key});
					if ($status eq 'ok'){
						$status = 'Done';
					}else{
						$status = 'Failed';
					}
					($sth) = &Do_SQL("INSERT INTO sl_manifests_items SET ID_manifests=$in{'id_manifests'}, ID_products=$1, 
									From_Warehouse=$in{'id_warehouses'}, From_Warehouse_Location='$2', 
									To_Warehouse=$in{'id_warehouses'}, To_Warehouse_Location='PACK',
									Qty=$transfer{$key}, Status='$status', Date=CURDATE(), Time=CURTIME(), ID_admin_users='$usr{'id_admin_users'}'");
					#&cgierr("$status $in{'id_warehouses'},$2,$in{'id_warehouses'},'PACK',$1,$transfer{$key}");
				}
			}
			$va{'message'}	= &trans_txt('pack_done');
		}elsif($in{'finished'} and !$err and $in{'id_manifests'}){
			$in{'cmd'} = 'opr_manifests'; $db_cols[0] = 'ID_manifests';
			$va{'prnbutton'} = &template_prnbutton;
			$va{'message'}	= &trans_txt('pack_already');
			#$in{'cmd'} = 'packing_topack';
			#http://dev2.direksys.com/cgi-bin/mod/wms/dbman?cmd=opr_manifests&search=Print&toprint=1304
			#http://dev2.direksys.com/cgi-bin/mod/wms/dbman?cmd=packing_topack&search=Print&toprint=1304
		}elsif($err){
			$va{'message'}	= &trans_txt('pack_error');
		}
		print "Content-type: text/html\n\n";
		print &build_page('packing_topack_stats.html');		
	}else{
		###########################################
		######### ORDERS LIST
		###########################################
		$va{'div_height'} = 60;
		my($sth) = &Do_SQL("SELECT sl_orders.ID_orders,COUNT(*) AS TLines,SUM(Quantity) AS Qty,sl_orders.Date, FirstName, LastName1, company_name, StatusPay,StatusPrd, sl_orders.Status
						FROM sl_orders LEFT JOIN sl_customers USING(ID_customers)
						INNER JOIN sl_orders_products USING(ID_orders) 
						LEFT JOIN  sl_warehouses_batches_orders
						ON sl_warehouses_batches_orders.ID_orders_products = sl_orders_products.ID_orders_products 
						AND sl_warehouses_batches_orders.Status IN ('In Fulfillment','Shipped','In Transit')  
						WHERE sl_orders.Status IN ('Shipped','Processed')
						AND sl_warehouses_batches_orders.ID_orders_products IS NULL
						AND StatusPrd = 'In Fulfillment' 
						AND sl_orders_products.Status IN ('Active','ReShip','Exchange')
						AND Saleprice >= 0
						AND (Shpdate IS NULL OR Shpdate = '0000-00-00' AND Shpdate = '') AND (Tracking IS NULL OR Tracking = '') AND (ShpProvider IS NULL OR ShpProvider = '')
						AND (Cost IS NULL OR Cost = '')
						GROUP BY sl_orders.ID_orders 
						ORDER BY sl_orders.ID_orders;");
		$va{'matches'} = $sth->rows();	
		if ($va{'matches'}>0){
			while (my($id_orders, $tlines, $qty, $order_date, $firsrname, $lastname, $companyname, $statuspay, $statusprd, $status ) = $sth->fetchrow()) {
				$d = 1 - $d;
				$va{'div_height'} += 20;
				
				$va{'searchresults'} .= "<tr bgcolor='$c[$d]' onmouseover='m_over(this)' onmouseout='m_out(this)'>\n";
				$va{'searchresults'} .= "  <td class='smalltext' width='5%' align='center' valign='top'><input class='checkbox' type='checkbox' name='oid_$id_orders' value='1'></td>\n";
				$va{'searchresults'} .= "  <td class='smalltext' width='10%' valign='top'>$id_orders</td>\n";
				$va{'searchresults'} .= "  <td class='smalltext' width='10%' valign='top'>$order_date </td>\n";
				$va{'searchresults'} .= "  <td class='smalltext' width='25%' valign='top'>$firstname $lastname</td>\n";
				$va{'searchresults'} .= "  <td class='smalltext' width='25%' valign='top'>$companyname</td>\n";
				$va{'searchresults'} .= "  <td class='smalltext' width='15%' align='center' valign='top' nowrap>$tlines / $qty</td>\n";
				$va{'searchresults'} .= "  <td class='smalltext' width='10%' valign='top'>$status</td>\n";
				$va{'searchresults'} .= "</tr>\n";
			}
			$va{'pageslist'} = 1;
		}else{
			$va{'matches'} = 1;
			$va{'pageslist'} = 1;
			$va{'searchresults'} = qq|
			<tr>
				<td colspan='5' align="center">|.&trans_txt('search_nomatches').qq|</td>
			</tr>\n|;
		}
		print "Content-type: text/html\n\n";
		print &build_page('packing_topack.html');
	}

}



############################################################################################
############################################################################################
#	Function: warehouses_batches_export_layout
#
#   		Exports batches info in layout format of any shipping company
#
#	Created by:
#		_Roberto Barcenas_
#
#	Modified By:
#
#   	Parameters:
#		- from_date : from date
#		- to_date : to date		
#		- f : f
#
#   	Returns:
#		- $id_new_batch
#
#   	See Also:
#   	- apps/ajaxbuild.cgi: chg_warehouse_batch
#   	- op-wman/admin_cod.html.cgi: cod_preorderstobatch
#
sub warehouses_batches_export_layout {
############################################################################################
############################################################################################


	#if(){
	$va{'export_perm'} = &check_permissions('warehouses_batches','_export','');

		################################################
		################################################
		################################################
		################################################
		###########
		########### Exportacion
		###########
		################################################
		################################################
		################################################
		################################################
		if($in{'export'} and $in{'action'}){ # and &check_permissions('warehouses_batches','_export','')

			my $fn = 'warehouses_batches_export';
			#&cgierr($fn);
			if( defined &$fn ) {
				&$fn();
				exit;
			}

		}


		my (@ary) = split(/,/,$sys{'db_warehouses_batches_export'});

		if ($#ary >= 1){

			for my $i(0..$#ary){
				++$x;

				if ($ary[$i]){
				
					$va{'layout_list'} .= qq|<input type="radio" id="f_$x" name="f" value="$x" onFocus="focusOn( this )" onBlur="focusOff( this )">$ary[$i]&nbsp;&nbsp;&nbsp;&nbsp;\n|;
					
				}
			}

		}

		print "Content-type: text/html\n\n";
		print &build_page('warehouses_batches_export_layout.html');

	#}
	

}


############################################################################################
############################################################################################
#	Function: warehouses_batches_conciliate
#
#   		Shows all orders in the batch and allows to pay from here
#
#	Created by:
#		_Roberto Barcenas_
#
#	Modified By:
#
#   	Parameters:
#
#
#   	Returns:
#
#
#   	See Also:
#
#
sub warehouses_batches_conciliate {
############################################################################################
############################################################################################


	$in{'id_warehouses'} = &load_name('sl_warehouses_batches','ID_warehouses_batches',$in{'view'},'ID_warehouses');
	$in{'date'} = &load_name('sl_warehouses_batches','ID_warehouses_batches',$in{'view'},'Date');
	$in{'status'} = &load_name('sl_warehouses_batches','ID_warehouses_batches',$in{'view'},'Status');

		#############################################
		#############################################
		############### Batch Actions
		#############################################
		#############################################

	if($in{'action'}) {

		if($in{'addpayment'}) {

			#############################################
			#############################################
			############### 1 )  Batch Payment 
			#############################################
			#############################################
			#&cgierr();

			$va{'message'} = &trans_txt('reqfields');		
			if(!$in{'view'}) {
				++$err;
			}

			if(!$in{'amount'}) {
				$error{'amount'} = &trans_txt('required');		
				++$err;
			}

			if(!$in{'id_banks'}) {
				$error{'id_banks'} = &trans_txt('required');		
				++$err;
			}

			if(!$in{'bankdate'}) {
				$error{'bankdate'} = &trans_txt('required');		
				++$err;
			}

			if(!$in{'refid'}) {
				$error{'refid'} = &trans_txt('required');		
				++$err;
			}


			if(!$error) {

				$in{'id_banks'} = int($in{'id_banks'});
				$in{'amount'} = &filter_values($in{'amount'});
				$in{'amount'} =~ s/\$|,|\s//g;
				$in{'bankdate'} = &filter_values($in{'bankdate'});
				$in{'refid'} = &filter_values($in{'refid'});

				####
				#### Agregamos pago
				####
				my ($sth) = &Do_SQL("INSERT INTO sl_warehouses_batches_payments SET ID_warehouses_batches = '$in{'view'}', ID_banks = '$in{'id_banks'}', 
									BankDate = '$in{'bankdate'}', Amount = '$in{'amount'}', RefID = '$in{'refid'}', Notes = '". &filter_values($in{'notes'})."',
									Status = 'New', Date = CURDATE(), Time = CURTIME(), ID_admin_users = '$usr{'id_admin_users'}';");
				my ($ok) = $sth->rows();

				if($ok) {

					my ($sth) = &Do_SQL("INSERT INTO sl_warehouses_batches_notes SET Notes='".&trans_txt('warehouses_batches_payment_added')."',Type='Low',Date=CURDATE(),Time=CURTIME(),ID_admin_users='$usr{'id_admin_users'}', ID_warehouses_batches='$in{'view'}';");
				    &auth_logging('batches_payment_added',$in{'view'});
				    $va{'message'} = &trans_txt('warehouses_batches_payment_added');

				    ###
				    ### ToDo: KeyPoint Contable
				    ###
					$ptype = 'COD';
					@params = ($in{'view'}, $in{'amount'},$in{'id_banks'}, 1);
					#&cgierr('order_deposit_'. $ctype .'_'. $order_type .'_'. $ptype);
					&accounting_keypoints('batch_deposit_' . $ptype, \@params );		


				}		


			}


		}

	}


	#############################################
	#############################################
	############### List 
	#############################################
	#############################################

	my $batch_free = 0;
	my ($sth) = &Do_SQL("SELECT COUNT(*)AS Payments, IF(SUM(Amount) IS NULL,0,SUM(Amount)) AS Paid, ToPay FROM sl_warehouses_batches_payments
						RIGHT JOIN
						(
							SELECT COUNT(*) AS TOrders, ID_warehouses_batches, SUM(Amount) AS ToPay 
							FROM sl_orders_payments INNER JOIN
							(
								SELECT ID_warehouses_batches, sl_orders.ID_orders
								FROM sl_warehouses_batches_orders INNER JOIN sl_orders_products USING(ID_orders_products)
								INNER JOIN sl_orders USING(ID_orders)
								WHERE ID_warehouses_batches = '$in{'view'}'
								AND sl_orders.Status = 'Processed'
								AND sl_warehouses_batches_orders.Status IN ('In Fulfillment', 'Shipped', 'In Transit')
								AND sl_orders_products.Status IN ('Active', 'Reship', 'Exchange')
								GROUP BY sl_orders.ID_orders
							)tmp2
							USING(ID_orders)	
							WHERE Status IN ('Approved','Denied','Pending','Credit')
							AND (Captured IS NULL OR Captured = 'No') 
							AND (CapDate IS NULL OR CapDate = '0000-00-00')
						)tmp 
	  					USING (ID_warehouses_batches)
	  					WHERE Status = 'New';");
	my ($tpay, $paid, $topay) = $sth->fetchrow();

	$va{'payments'} = $tpay;
	$va{'topay'} = &format_price($topay,2);
	$va{'paid'} = &format_price($paid,2);
	$va{'pay_batch'} = 'none';

	my $amt_error = $topay * ($cfg{'porcerror'}/100);
	#&cgierr("$paid >= $topaid or ($topaid - $paid) <= $amt_error");
	if($topay > 0 and ($paid >= $topay or ($topay - $paid) <= $amt_error) ) {

		####
		#### Aqui se desbloquea la posibilidad de pagar
		####
		$batch_free = 1;
		$va{'pay_batch'} = 'block';

	}


	my $x = 0;
	my ($sth) = &Do_SQL("SELECT sl_orders.ID_orders,Ptype,InBatch,sl_orders.Status,SUM(IF( (Captured = 'No' OR Captured IS NULL) AND (CapDate IS NULL OR CapDate = '0000-00-00'),Amount,0)), sl_customers.ID_customers, CONCAT(Firstname,' ', LastName1)AS Customer 
					FROM sl_orders INNER JOIN
			 			(
			 				SELECT ID_orders, SUM(IF(sl_warehouses_batches_orders.Status IN ('In Fulfillment', 'Shipped', 'In Transit'),1,0))AS InBatch
			 				 FROM sl_warehouses_batches_orders INNER JOIN sl_orders_products USING(ID_orders_products)
			 				WHERE ID_warehouses_batches = '$in{'view'}'
			 				GROUP BY ID_orders
			 			)tmp USING(ID_orders)
						INNER JOIN sl_orders_payments USING(ID_orders)
						INNER JOIN sl_customers USING(ID_customers)
						WHERE sl_orders_payments.Status NOT IN('Void','Order Cancelled','Cancelled')
						AND (Captured IS NULL OR Captured = 'No') 
						AND (CapDate IS NULL OR CapDate = '0000-00-00')
						GROUP BY sl_orders.ID_orders ORDER BY Ptype,sl_orders.ID_orders;");
	ORDERS:while(my ($id_orders, $ptype, $inbatch, $status, $amount, $id_customers, $customer_name) = $sth->fetchrow()){

		next ORDERS if (!$inbatch and $status ne 'Cancelled');

		++$x;
		$va{'searchresults'} .= "<tr bgcolor='$c[$d]' onmouseover='m_over(this)' onmouseout='m_out(this)'>\n";
		$va{'searchresults'} .= "  <td class='smalltext' valign='top' align='center'>";
		
		my $style_order = 'black';
		if ($status eq 'Processed' and $inbatch){

			++$va{'orders'};
			$va{'searchresults'} .= qq|<img src="[va_imgurl][ur_pref_style]/checkmark.gif">\n|;
			$style_order = "green";
	
		}
		$va{'searchresults'} .= "	</td>\n";
		$va{'searchresults'} .= "  <td class='smalltext' valign='top' align='center'><a href='/cgi-bin/mod/$usr{'application'}/dbman?cmd=opr_orders&view=$id_orders'>$id_orders</a></td>";
		$va{'searchresults'} .= "  <td class='smalltext' valign='top' align='left'>$ptype</td>";
		$va{'searchresults'} .= "  <td class='smalltext' valign='top' align='left'><a href='/cgi-bin/mod/$usr{'application'}/dbman?cmd=opr_customrs&view=$id_customers'>$customer_name</a></td>";
		$va{'searchresults'} .= "  <td class='smalltext' valign='top' align='left'>$status</td>";
		$va{'searchresults'} .= "  <td class='smalltext' valign='top' align='right' id='p_$id_orders'><span style='color:$style_order'>".&format_price($amount)."</span></td>";
		$va{'searchresults'} .= "  <input type='hidden' value='$amount' id='v_$id_orders'></td>";

		$va{'searchresults'} .= "</tr>\n";

	}
	$va{'matches'} = $x;
	$va{'pageslist'} = 1;

	(!$va{'orders'}) and ($va{'tbl_payments_style'} = 'style="display:none;"');

	print "Content-type: text/html\n\n";
	print &build_page('warehouses_batches_conciliate.html');

}

sub false_delivery{
		if(&check_permissions('false_delivery','','')){
			print "Content-type: text/html\n\n";
			print &build_page('false_delivery.html');
		}else{
			&html_unauth;
		}
}

sub zipcodes_border_zones{
	$in{'setup_zones'} =~ s/^\s+|\s+$//g if ($in{'setup_zones'});
	$va{'summary'} = '';

	if ($in{'action'}) {
		$zones = '';
		$add_sql = '';
		&Do_SQL("START TRANSACTION;");

		my (@ary) = split(/\s+|,|\n|\t|\|/,$in{'setup_zones'});
		
		for my $i(0..$#ary){
			my $zone = $ary[$i];
		
			if (int($zone) > 0){
				$add_sql .= "'$zone',";
			}else{
				$va{'summary'} .= $zone.": ".&trans_txt('zipcode_format_invalid')."<br>";
			}
		}
		chop($add_sql);

		if ($add_sql ne ''){
			my ($sth) = &Do_SQL("SELECT ID_zones, Name FROM sl_zones WHERE ID_zones IN (".$add_sql.") AND Status='Active';");
			while (my $rec = $sth->fetchrow_hashref()) {
				$zones .= "'$rec->{'ID_zones'}',";
				$va{'summary'} .= $rec->{'ID_zones'}.' - '.$rec->{'Name'}.": ".&trans_txt('zipcodes_border_zones_updated')."<br>";

			}
			chop($zones);

			## Logs
			my ($sth) = &Do_SQL("SELECT ID_zones, Name FROM sl_zones WHERE ID_zones IN (".$add_sql.") AND Status='Active';");
			while (my $rec = $sth->fetchrow_hashref()) {
				$in{'db'} = 'sl_zones';
				&auth_logging('zipcode_border_zone_added',$rec->{'ID_zones'});
			}

			&Do_SQL("UPDATE sl_zones SET BorderZone='No' WHERE BorderZone='Yes';");
			&Do_SQL("UPDATE sl_zones SET BorderZone='Yes' WHERE ID_zones IN (".$zones.");");
			&Do_SQL("COMMIT;");
			delete($in{'setup_zones'});
			$va{'message'} = &trans_txt('zipcodes_border_zones_successfull');
		}

	}

	my ($sth) = &Do_SQL("SELECT ID_zones FROM sl_zones WHERE BorderZone='Yes' AND Status='Active';");
	while (my $rec = $sth->fetchrow_hashref()) {
		$in{'setup_zones'} .= "$rec->{'ID_zones'},";
	}
	chop($in{'setup_zones'});

	print "Content-type: text/html\n\n";
	print &build_page('zipcodes_border_zones.html');
}

1;
