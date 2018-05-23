##################################################################
#    OPERATIONS : ORDERS   	#
##################################################################

sub rep_cod{
# --------------------------------------------------------
# Forms Involved: 
# Created on: 03/12/09 10:22:57
# Author: MCC C. Gabriel Varela S.
# Description :   
# Parameters :
# Last Modified on: 03/17/09 13:18:11
# Last Modified by: MCC C. Gabriel Varela S: Se pone resultado de not found
# Last Modified on: 03/19/09 12:44:25
# Last Modified by: MCC C. Gabriel Varela S: Se toma en cuenta codshptype
	$va{'matches'} = 1;
	$va{'pageslist'} = 1;
	my $sth=&Do_SQL("SELECT count(ID_warehouses)
from (SELECT ID_warehouses,count(sl_orders.ID_orders) as NOrders,sum(NItems)as NItems
FROM `sl_orders` 
inner join (Select ID_orders,sum(if(isset!='Y',1,0))+if(not isnull(parts),parts,0) as NItems,Isset
            from sl_orders_products 
            inner join sl_skus on (sl_orders_products.ID_products=sl_skus.ID_sku_products)
            left join (select ID_sku_products,count(ID_skus_parts)as parts 
                       from sl_skus_parts 
                       group by ID_sku_products)as tampa on (sl_orders_products.ID_products=tampa.ID_sku_products)
            where sl_orders_products.Status='Active'
            and sl_orders_products.SalePrice>0
            and sl_orders_products.Quantity>0
            and sl_orders_products.ID_products not like '6%'
            group by ID_orders)as tmp on (sl_orders.ID_orders=tmp.ID_orders)
WHERE Ptype!='Credit-Card' 
and Status='Shipped' 
and shp_type=$cfg{'codshptype'}
group by ID_warehouses)as tempo");
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

		my $sth=&Do_SQL("SELECT ID_warehouses,count(sl_orders.ID_orders) as NOrders,sum(NItems)as NItems
FROM `sl_orders` 
inner join (Select ID_orders,sum(if(isset!='Y',1,0))+if(not isnull(parts),parts,0) as NItems,Isset
            from sl_orders_products 
            inner join sl_skus on (sl_orders_products.ID_products=sl_skus.ID_sku_products)
            left join (select ID_sku_products,count(ID_skus_parts)as parts 
                       from sl_skus_parts 
                       group by ID_sku_products)as tampa on (sl_orders_products.ID_products=tampa.ID_sku_products)
            WHERE sl_orders_products.Status='Active'
            AND sl_orders_products.SalePrice>0
            AND sl_orders_products.Quantity>0
            AND sl_orders_products.ID_products not like '6%'
            GROUP BY ID_orders)as tmp ON (sl_orders.ID_orders=tmp.ID_orders)
				WHERE Ptype!='Credit-Card' 
				AND Status='Shipped' 
				AND shp_type=$cfg{'codshptype'}
				GROUP BY ID_warehouses $page_limit");

		$va{'searchresults'}="";
		while(my $rec=$sth->fetchrow_hashref){
			$d = 1 - $d;
			$va{'searchresults'} .= "<tr bgcolor='$c[$d]' onmouseover='m_over(this)' onmouseout='m_out(this)' >\n";
			$va{'searchresults'} .= "  <td class='smalltext' valign='top' align='center'>$rec->{'ID_warehouses'}</td>";
			$va{'searchresults'} .= "  <td class='smalltext' valign='top'>".&load_name('sl_warehouses','ID_warehouses',$rec->{'ID_warehouses'},'Name')." </td>\n";
			$va{'searchresults'} .= "  <td class='smalltext' valign='top'>$rec->{'NOrders'}</td>\n";
			$va{'searchresults'} .= "  <td class='smalltext' valign='top'>$rec->{'NItems'}</td>\n";
			$va{'searchresults'} .= "</tr>\n";
		}
	}else{
		$va{'pageslist'} = 1;
		$va{'searchresults'} = qq|
		<tr>
			<td colspan='7' align="center">|.&trans_txt('search_nomatches').qq|</td>
		</tr>\n|;
	}
	&auth_logging('report_view','');
	if ($in{'print'}){
		print "Content-type: text/html\n\n";
		print &build_page('header_print.html');
		print &build_page('rep_cod_print.html');
	}else{
		print "Content-type: text/html\n\n";
		print &build_page('rep_cod.html');
	}
}

sub rep_cod_by_orders{
# --------------------------------------------------------
# Forms Involved: 
# Created on: 03/13/09 17:23:17
# Author: MCC C. Gabriel Varela S.
# Description :   
# Parameters :
# Last Modified on: 03/17/09 13:18:11
# Last Modified by: MCC C. Gabriel Varela S: Se pone resultado de not found
# Last Modified on: 03/19/09 12:45:01
# Last Modified by: MCC C. Gabriel Varela S: Se toma en cuenta codshptype
# Last Modified on: 08/11/09 11:00:59
# Last modified by: EP. : Se Eliminan las referencias a preordenes

	$va{'matches'} = 1;
	$va{'pageslist'} = 1;
	my $cadinn = " INNER JOIN sl_orders_datecod ON sl_orders.ID_orders = sl_orders_datecod.ID_orders ";
	my $sth=&Do_SQL("SELECT count(ID_warehouses)
			FROM (SELECT sl_orders.ID_orders,sl_orders_datecod.DateCOD,sl_orders.ID_warehouses,count(sl_orders.ID_orders) as NOrders,sum(NItems)as NItems,sl_orders.Status
			FROM `sl_orders` 
			INNER JOIN (Select ID_orders,sum(if(isset!='Y',1,0))+if(not isnull(parts),parts,0) as NItems,Isset
			            FROM sl_orders_products 
			            INNER JOIN sl_skus on (sl_orders_products.ID_products=sl_skus.ID_sku_products)
			            LEFT JOIN (SELECT ID_sku_products,count(ID_skus_parts)as parts 
			                       FROM sl_skus_parts 
			                       GROUP by ID_sku_products)as tampa on (sl_orders_products.ID_products=tampa.ID_sku_products)
			            WHERE sl_orders_products.Status='Active'
			            AND sl_orders_products.SalePrice>0
			            AND sl_orders_products.Quantity>0
			            AND sl_orders_products.ID_products not like '6%'
			            GROUP BY ID_orders)as tmp ON (sl_orders.ID_orders=tmp.ID_orders)
			$cadinn
			WHERE Ptype!='Credit-Card'
			AND sl_orders.Status='Shipped' 
			AND sl_orders.shp_type=$cfg{'codshptype'}
			AND sl_orders_datecod.Status='Active'
			GROUP BY sl_orders.ID_orders)as tempo");
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

		my $sth=&Do_SQL("SELECT sl_orders.ID_orders,sl_orders_datecod.DateCOD,sl_orders.ID_warehouses,count(sl_orders.ID_orders) as NOrders,sum(NItems)as NItems,sl_orders.Status
			FROM `sl_orders` 
			inner join (Select ID_orders,sum(if(isset!='Y',1,0))+if(not isnull(parts),parts,0) as NItems,Isset
			            FROM sl_orders_products 
			            INNER JOIN sl_skus on (sl_orders_products.ID_products=sl_skus.ID_sku_products)
			            LEFT JOIN (select ID_sku_products,count(ID_skus_parts)as parts 
			                       from sl_skus_parts 
			                       group by ID_sku_products)as tampa ON (sl_orders_products.ID_products=tampa.ID_sku_products)
			            WHERE sl_orders_products.Status='Active'
			            AND sl_orders_products.SalePrice>0
			            AND sl_orders_products.Quantity>0
			            AND sl_orders_products.ID_products not like '6%'
			            GROUP BY ID_orders)as tmp ON (sl_orders.ID_orders=tmp.ID_orders) 
			$cadinn
			WHERE Ptype!='Credit-Card'
			AND sl_orders.Status='Shipped' 
			AND shp_type=$cfg{'codshptype'}
			AND sl_orders_datecod.Status='Active'
			GROUP BY sl_orders.ID_orders $page_limit");

		$va{'searchresults'}="";
		while(my $rec=$sth->fetchrow_hashref){
			$d = 1 - $d;
			$va{'searchresults'} .= "<tr bgcolor='$c[$d]' onmouseover='m_over(this)' onmouseout='m_out(this)' >\n";
			$va{'searchresults'} .= "  <td class='smalltext' valign='top' align='center'>$rec->{'ID_orders'}</td>";
			$va{'searchresults'} .= "  <td class='smalltext' valign='top' align='center'>$rec->{'DateCOD'}</td>";
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
	&auth_logging('report_view','');
	if ($in{'print'}){
		print "Content-type: text/html\n\n";
		print &build_page('header_print.html');
		print &build_page('rep_cod_by_orders_print.html');
	}else{
		print "Content-type: text/html\n\n";
		print &build_page('rep_cod_by_orders.html');
	}
}

sub rep_cod_by_items{
# --------------------------------------------------------
# Forms Involved: 
# Created on: 03/13/09 17:41:36
# Author: MCC C. Gabriel Varela S.
# Description :   
# Parameters :
# Last Modified on: 03/17/09 13:18:11
# Last Modified by: MCC C. Gabriel Varela S: Se pone resultado de not found
# Last Modified on: 03/19/09 12:45:49
# Last Modified by: MCC C. Gabriel Varela S: Se toma en cuenta codshptype
# Last Modified on: 08/11/09 11:00:59
# Last modified by: EP. : Se Eliminan las referencias a preordenes
	$va{'matches'} = 1;
	$va{'pageslist'} = 1;
	my $cadinn = " INNER JOIN sl_orders_datecod ON sl_orders.ID_orders = sl_orders_datecod.ID_orders ";
	my $sth=&Do_SQL("SELECT count(sl_orders_products.ID_products)
					FROM sl_orders_products
					INNER JOIN sl_skus ON ( sl_orders_products.ID_products = sl_skus.ID_sku_products ) 
					LEFT JOIN (SELECT ID_sku_products, ID_parts
					           FROM sl_skus_parts) AS tampa ON ( sl_orders_products.ID_products = tampa.ID_sku_products ) 
					INNER JOIN sl_orders ON ( sl_orders_products.ID_orders = sl_orders.ID_orders ) 
					$cadinn
					WHERE sl_orders_products.Status = 'Active'
					AND sl_orders_products.SalePrice >0
					AND sl_orders_products.Quantity >0
					AND sl_orders_products.ID_products NOT LIKE '6%'
					AND Ptype!='Credit-Card'
					AND sl_orders.Status = 'Shipped'
					AND sl_orders_datecod.Status='Active'
					AND shp_type =$cfg{'codshptype'};");
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

		my $sth=&Do_SQL("SELECT if(Isset='Y',400000000+ID_parts,sl_orders_products.ID_products)as ID_items,DateCOD,sl_orders.ID_warehouses,Isset
						FROM sl_orders_products
						INNER JOIN sl_skus ON ( sl_orders_products.ID_products = sl_skus.ID_sku_products ) 
						LEFT JOIN (SELECT ID_sku_products, ID_parts
						           FROM sl_skus_parts) AS tampa ON ( sl_orders_products.ID_products = tampa.ID_sku_products ) 
						INNER JOIN sl_orders ON ( sl_orders_products.ID_orders = sl_orders.ID_orders ) 
						$cadinn
						WHERE sl_orders_products.Status = 'Active'
						AND sl_orders_products.SalePrice >0
						AND sl_orders_products.Quantity >0
						AND sl_orders_products.ID_products NOT LIKE '6%'
						AND Ptype!='Credit-Card'
						AND sl_orders.Status = 'Shipped'
						AND shp_type =$cfg{'codshptype'}
						AND sl_orders_datecod.Status='Active' $page_limit");

		$va{'searchresults'}="";
		my $cadnamemodel;
		$cadnamemodel="";
		while(my $rec=$sth->fetchrow_hashref){
			$d = 1 - $d;
			if($rec->{'Isset'}eq'Y'){
				$cadnamemodel=&load_db_names('sl_parts','ID_parts',substr($rec->{'ID_items'},5,4),"[Model]<br>[Name]");
			}else{
				$cadnamemodel=&load_db_names('sl_products','ID_products',substr($rec->{'ID_items'},3,6),"[Model]<br>[Name]");
			}
			$va{'searchresults'} .= "<tr bgcolor='$c[$d]' onmouseover='m_over(this)' onmouseout='m_out(this)' >\n";
			$va{'searchresults'} .= "  <td class='smalltext' valign='top'>".&format_sltvid($rec->{'ID_items'})."</td>";
			$va{'searchresults'} .= "  <td class='smalltext' valign='top'>$cadnamemodel</td>";
			$va{'searchresults'} .= "  <td class='smalltext' valign='top'>$rec->{'DateCOD'}</td>\n";
			$va{'searchresults'} .= "  <td class='smalltext' valign='top'>".&load_name('sl_warehouses','ID_warehouses',$rec->{'ID_warehouses'},'Name')." </td>\n";
			$va{'searchresults'} .= "</tr>\n";
		}
	}else{
		$va{'pageslist'} = 1;
		$va{'searchresults'} = qq|
		<tr>
			<td colspan='7' align="center">|.&trans_txt('search_nomatches').qq|</td>
		</tr>\n|;
	}
	&auth_logging('report_view','');
	if ($in{'print'}){
		print "Content-type: text/html\n\n";
		print &build_page('header_print.html');
		print &build_page('rep_cod_by_items_print.html');
	}else{
		print "Content-type: text/html\n\n";
		print &build_page('rep_cod_by_items.html');
	}
}

###############################################################################
#   Function: rep_cod_by_posteddated
#
#       Muestra informacion de ordenes COD
#
#   Created by:
#       _Pablo Hernandez_
#
#   Modified By:
#
#       Parameters:
#
#       from_date, to_date
#
#       Returns:
#
#
sub rep_cod_by_posteddated {
###############################################################################
    if($in{'action'}){
        
        use Spreadsheet::WriteExcel;
        my ($fname) = 'rep_cod_by_posteddated-'.$in{'from_date'}.'-'.$in{'to_date'}.'.xls';
        my $row=1;

        ###### Busqueda por rango de fecha
        $in{'from_date'} = &get_sql_date() if !$in{'from_date'};
        $in{'to_date'} = &get_sql_date() if !$in{'to_date'};
  
        my $Sql = "SELECT sl_orders.ID_orders, sl_orders.PostedDate, 
                       SUM(sl_orders_products.SalePrice) AS SalePrice, 
                       SUM(sl_orders_products.Discount) AS Discount, 
                       SUM(sl_orders_products.Tax) AS Tax, 
                       SUM(sl_orders_products.Shipping) AS Shipping
                 FROM sl_orders
                INNER JOIN sl_orders_products 
                   ON sl_orders.ID_orders=sl_orders_products.ID_orders
                WHERE sl_orders_products.Status='Active'
                AND sl_orders.Ptype='COD'
                AND sl_orders.Status='Shipped'    
                AND sl_orders.PostedDate BETWEEN '$in{'from_date'}' AND '$in{'to_date'}' 
                GROUP BY sl_orders.ID_orders, sl_orders_products.ID_orders";

        my ($sth) = &Do_SQL($Sql);
		&auth_logging('report_view',''); 
        print "Content-type: application/octetstream\n";
        print "Content-disposition: attachment; filename=$fname\n\n";
                           
        my $workbook  = Spreadsheet::WriteExcel->new("-");
        my $worksheet = $workbook->add_worksheet();
        $worksheet->write(0, 1,'ID');
        $worksheet->write(0, 2,'Amount');
        $worksheet->write(0, 3,'Paid');
        $worksheet->write(0, 4,'Date');        
        while ($rec = $sth->fetchrow_hashref()){
        	if($rec->{'ID_orders'} > 0){             
        		my $sth_payments = &Do_SQL("SELECT  SUM(sl_orders_payments.Amount) as Amount FROM sl_orders_payments WHERE sl_orders_payments.Status NOT IN('Cancelled', 'Void') AND ID_orders=$rec->{'ID_orders'}");
                my($Amount) = $sth_payments->fetchrow();
                my $order_net = $rec->{'SalePrice'} + $rec->{'Discount'} + $rec->{'Tax'} + $rec->{'Shipping'};
                $worksheet->write($row,1,$rec->{'ID_orders'});
                $worksheet->write($row,2,round($order_net,2));
                $worksheet->write($row,3,$Amount);
                $worksheet->write($row,4,$rec->{'PostedDate'}); 
                $row++;
            }
        }
    }
    print "Content-type: text/html\n\n";
    print &build_page('rep_cod_by_posteddated.html');
    
}


###############################################################################
#   Function: rep_cod_intransit
#
#       Muestra informacion de ordenes COD en transito, por almacen
#
#   Created by:
#       _RB_
#
#   Modified By:
#
#       Parameters:
#
#       ID_warehouses
#
#       Returns:
#
#
sub rep_cod_intransit {
###############################################################################


	if($in{'action'}){

		my $id_warehouses;

		####
		#### Export
		####

		if($in{'id_warehouses'}){

			###
			### 1. Validamos que el WH sea Virtual
			###

			$id_warehouses = int($in{'id_warehouses'});
			my $this_type = &load_name('sl_warehouses','ID_warehouses', $id_warehouses, 'Type');

			if( lc($this_type) ne 'virtual'){

				###
				### 1.1. WH No es Virtual, se agrega error
				###
				$error++;
				$error{'id_warehouses'} = &trans_txt('invalid');

			}

		}else{

			###
			### 2. No se busco WH, extraemos todos los WH Virtuales Activos
			###
			my ($sth) = &Do_SQL("SELECT GROUP_CONCAT(ID_warehouses) FROM sl_warehouses WHERE Type = 'Virtual' AND Status='Active';");
			$id_warehouses = $sth->fetchrow();

		}


		if(!$error and $id_warehouses){

			###
			### 3. No hay errores, extraer reporte
			###
			my $this_sql = "SELECT
						sl_orders.ID_orders 
						, sl_warehouses_batches.ID_warehouses
						, sl_warehouses.Name AS warehouses
						, (400000000 + sl_orders_parts.ID_parts)SKU
						, sl_parts.Name
						, SUM(sl_orders_parts.Quantity)Quantity
						FROM sl_orders_products
							INNER JOIN sl_orders USING(ID_orders)
							INNER JOIN sl_warehouses_batches_orders USING(ID_orders_products)
							INNER JOIN sl_warehouses_batches USING(ID_warehouses_batches) 
							INNER JOIN sl_warehouses ON sl_warehouses.ID_warehouses = sl_warehouses_batches.ID_warehouses
							INNER JOIN sl_orders_parts USING(ID_orders_products)
							INNER JOIN sl_parts USING(ID_parts)
						WHERE
							sl_warehouses.ID_warehouses IN($id_warehouses)
						AND sl_orders.Ptype='COD'
						AND sl_orders.Status = 'Processed' 
						AND sl_orders_products.ID_products < 600000000
						AND sl_orders_products.Status = 'Active' 
						AND sl_warehouses_batches_orders.Status IN ('In Transit', 'Shipped')
						GROUP BY
							sl_orders.ID_orders 
							, sl_orders_parts.ID_parts
						ORDER BY 
							sl_warehouses.ID_warehouses
							, sl_orders.ID_orders
							, sl_parts.ID_parts";
			
			my ($sth) = &Do_SQL($this_sql);
			my ($tlines) = $sth->rows();

			if($tlines){

				&auth_logging('report_cod_intransit_view','');
				my $fname = 'cod_intransit_e' . $in{'e'} . '_' . &get_sql_date() . '.csv';
		        print "Content-type: application/octetstream\n";
		        print "Content-disposition: attachment; filename=$fname\n\n";
		        print qq|"ID Warehouse","Warehouse Name","ID Orders","ID SKU","SKU Name","UPC","Quantity In Transit","Quantity In Order","Difference"\r\n|;


				while(my ($this_id_orders, $this_idwh, $this_nmwh, $this_sku, $this_sku_name, $this_qty) = $sth->fetchrow()){

					###
					### 3.1. Buscamos la cantidad que deberia tener de acuerdo a la orden
					###
					my ($sth2) = &Do_SQL("SELECT 
											SUM(Qty * Quantity) 
										FROM
											sl_orders_products
										INNER JOIN 
											sl_skus_parts
										ON 
											ID_sku_products = ID_products
										WHERE
											ID_orders = '$this_id_orders'
											AND sl_skus_parts.ID_parts + 400000000 = '$this_sku'
											AND sl_orders_products.Status='Active';");
					my ($this_qty_byorder) = $sth2->fetchrow();

					###
					### 3.2. Impresion de resultado
					###
					print qq|"$this_idwh","$this_nmwh","$this_id_orders","$this_sku","$this_sku_name","|.&load_name('sl_skus','ID_sku_products',$this_sku,'UPC').qq|","$this_qty","$this_qty_byorder","|.($this_qty - $this_qty_byorder).qq|"\r\n|;

				}

			}
			
			return;

		}elsif(!$id_warehouses){

			###
			### 4. Se devuelve Error al no encontrar almacen para trabajar
			###

			$va{'message'} = &trans_txt('rep_cod_intransit_nowarehouse');

		}



	}


	print "Content-type: text/html\n\n";
    print &build_page('rep_cod_intransit.html');

}

1;