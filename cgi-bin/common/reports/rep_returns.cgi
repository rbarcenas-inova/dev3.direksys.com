##################################################################
#    OPERATIONS : ORDERS   	#
##################################################################
sub	rep_ret_prod{
#-----------------------------------------
# Created on: 03/04/09  17:24:21 By  Roberto Barcenas
# Forms Involved: 
# Description :
# Parameters : 
# Last Modified RB: 05/01/09  10:37:59 -- Cambia byuser por user_type basado en la tabla admin_users

	##TODO: Todos los textos deben estar fuera del codigo y/o a traves de transtxt
	
	my ($sb,$query,$report_name,$query_sum);
	if ($in{'action'}){
		my ($runcmd) = 'results_ret_prod';
		$runcmd = 'results_ret_prod' if !$in{'report_type'};
		my ($query_tot,$query_list);
		
		## Date Type
		if ($in{'dtype'} eq 'sl_orders.Date'){
			$va{'report_tbl'} .= "<tr><td width='100' class='smalltext'>Date : </td><td class='smalltext'>Order Date</td></tr>\n";						
		}else{
			$in{'dtype'} = 'sl_returns.Date';
			$va{'report_tbl'} .= "<tr><td width='100' class='smalltext'>Date : </td><td class='smalltext'>Return Date</td></tr>\n";						
		}
		
				
		if ($in{'sortby'}){
			$sb = "ORDER BY $in{'sortby'} $in{'sortorder'}";
		}
		$query = "WHERE sl_returns.ID_orders=sl_orders.ID_orders AND sl_returns.ID_orders_products = sl_orders_products.ID_orders_products  AND sl_orders.ID_orders = sl_orders_products.ID_orders AND sl_returns.Status != 'Void'";

		## Filter by User
		if ($in{'user_type'}){
			$in{'user_type'} =~ s/\|/','/g;
			$va{'report_tbl'} .= "<tr><td width='100' class='smalltext'>By User : </td><td class='smalltext'>$in{'user_type'}</td></tr>\n";
			$query .= " AND 0 < (SELECT IF(user_type IN ('$in{'user_type'}'),1,0) FROM admin_users WHERE ID_admin_users = sl_orders.ID_admin_users) ";
		}$in{'user_type'} =~ s/','/\|/g;
		
		## Filter by Date
		if ($in{'from_date'}){
			$va{'report_tbl'} .= "<tr><td width='100' class='smalltext'>From Date : </td><td class='smalltext'>$in{'from_date'}</td></tr>\n";
			$query .= " AND $in{'dtype'}>='$in{'from_date'}' ";
		}
		if ($in{'to_date'}){
			$va{'report_tbl'} .= "<tr><td width='100' class='smalltext'>To Date : </td><td class='smalltext'>$in{'to_date'}</td></tr>\n";
			$query .= " AND $in{'dtype'}<='$in{'to_date'}' ";
		}
		
		## Filter by Type
		if ($in{'type'}){
			$in{'type'} =~ s/\|/','/g;
			$va{'report_tbl'} .= "<tr><td width='100' class='smalltext'>Type : </td><td class='smalltext'>$in{'type'}</td></tr>\n";			
			$query .= " AND sl_returns.Type IN ('$in{'type'}') ";
		}
	
		## Filter by Status
		if ($in{'status'}){
			$in{'status'} =~ s/\|/','/g;
			$va{'report_tbl'} .= "<tr><td width='100' class='smalltext'>Status : </td><td class='smalltext'>$in{'status'}</td></tr>\n";			
			$query .= " AND sl_returns.Status IN ('$in{'status'}') ";
		}elsif ($in{'excludevoid'}){
			$va{'report_tbl'} .= "<tr><td width='100' class='smalltext'>Status : </td><td class='smalltext'>Void and System Error Excluded</td></tr>\n";			
			$query .= " AND sl_orders.Status NOT IN ('Void','System Error') ";
		}
		
		## Filter by MerAction
		if ($in{'meraction'}){
			$in{'statusprd'} =~ s/\|/','/g;
			$va{'report_tbl'} .= "<tr><td width='100' class='smalltext'>Action : </td><td class='smalltext'>$in{'meraction'}</td></tr>\n";			
			$query .= " AND sl_returns.merAction IN ('$in{'meraction'}') ";
		}

		## Filter by pricelevelss
		if ($in{'id_pricelevels'}){
			$va{'report_tbl'} .= "<tr><td width='100' class='smalltext'>Price Levels : </td><td class='smalltext'>".&load_pricelevels_name()."</td></tr>\n";									
			$query .= " AND sl_orders.ID_pricelevels='$in{'id_pricelevels'}'";
		}
		## Filter by Products
		if ($in{'id_products'}){
			$in{'id_products'} = int($in{'id_products'});
			$va{'report_tbl'} .= "<tr><td width='100' class='smalltext'>Product : </td><td class='smalltext'>(".&format_sltvid($in{'id_products'}).") ".&load_name('sl_products','ID_products',$in{'id_products'},'Name')."</td></tr>\n";
			$query .= " AND RIGHT(sl_orders_products.ID_products,6)='$in{'id_products'}' ";
		}else{
			$query .= " AND ID_products > 100000 ";
		}
		## Filter by category
		if ($in{'id_categories'} and $in{'groupby'} ne 'category'){
			$va{'report_tbl'} .= "<tr><td width='100' class='smalltext'>Category : </td><td class='smalltext'>".&load_name('sl_categories','ID_categories',$in{'id_categories'},'Title')."</td></tr>\n";			
			$query .= " AND RIGHT(sl_orders_products.ID_products,6) IN (SELECT ID_products FROM sl_products_categories WHERE ID_top='$in{'id_categories'}') ";
		}
		
		## Filter by State
		if ($in{'state'}){
			$va{'report_tbl'} .= "<tr><td width='100' class='smalltext'>State : </td><td class='smalltext'>$in{'state'}</td></tr>\n";						
			$query .= " AND sl_orders.State='$in{'state'}' ";
		}
		
		## Filter by history
		if ($in{'history'}){
			$va{'report_tbl'} .= "<tr><td width='100' class='smalltext'>History : </td><td class='smalltext'>$in{'history'}</td></tr>\n";						

		}

		### Exclude Discount
		if ($in{'excludedisc'}){
			$query_sum = "SUM(SalePrice-Discount)*-1";
		}else{
			$va{'report_tbl'} .= "<tr><td width='100' class='smalltext'>Discounts : </td><td class='smalltext'>NOT included</td></tr>\n";			
			$query_sum = "SUM(SalePrice*Quantity)*-1";
		}

		if ($in{'groupby'} eq 'hour'){
			$report_name = "Product ID / Hour";			
			$group = 'sl_orders.Time' if $in{'dtype'}	eq	'sl_orders.Date';
			$group = 'sl_returns.Time' if $in{'dtype'}	eq	'sl_returns.Date';
			$usr{'pref_maxh'} = 30;
			$query_tot  = "SELECT COUNT(*),$query_sum FROM sl_returns,sl_orders_products,sl_orders $query";
			$query_list = "SELECT HOUR($group),COUNT(*) AS nums,$query_sum AS amounts FROM sl_returns,sl_orders_products,sl_orders $query GROUP BY HOUR($group) $sb ";
		}elsif($in{'groupby'} eq 'month'){
			$report_name = "Month";	
			$query_tot  = "SELECT COUNT(*),$query_sum FROM sl_returns,sl_orders,sl_orders_products $query";
			$query_list = "SELECT CONCAT(MONTH($in{'dtype'}),'-',YEAR($in{'dtype'})),COUNT(*) AS nums,$query_sum AS amounts FROM sl_returns,sl_orders_products,sl_orders $query GROUP BY CONCAT(MONTH($in{'dtype'}),'-',YEAR($in{'dtype'})) $sb ";
		}elsif($in{'groupby'} eq 'state'){
			$report_name = "State";	
			$query_tot  = "SELECT COUNT(*),$query_sum FROM sl_returns,sl_orders_products, sl_orders $query";
			$query_list = "SELECT State,COUNT(*) AS nums,$query_sum AS amounts FROM sl_returns,sl_orders_products, sl_orders  $query GROUP BY State $sb ";
		}elsif($in{'groupby'} eq 'category'){
			$report_name = "Categories";
			$query_tot = $query;
			$query_list = $query_sum;
			$runcmd = 'results_ret_categ';
		}elsif($in{'groupby'} eq 'type'){
			$report_name = "Type";	
			$query_tot  = "SELECT COUNT(*),$query_sum FROM sl_returns,sl_orders_products, sl_orders $query";
			$query_list = "SELECT sl_returns.Type,COUNT(*)AS nums,$query_sum AS amounts FROM sl_returns,sl_orders_products, sl_orders $query GROUP BY sl_returns.Type $sb ";
		}elsif($in{'groupby'} eq 'status'){
			$report_name = "Status";	
			$query_tot  = "SELECT COUNT(*),$query_sum FROM sl_returns,sl_orders_products, sl_orders $query";
			$query_list = "SELECT sl_returns.Status,COUNT(*)AS nums,$query_sum AS amounts FROM sl_returns,sl_orders_products, sl_orders $query GROUP BY sl_returns.Status $sb ";
		}elsif($in{'groupby'} eq 'meraction'){
			$report_name = "Action";	
			$query_tot  = "SELECT COUNT(*),$query_sum FROM sl_returns,sl_orders_products, sl_orders $query";
			$query_list = "SELECT sl_returns.merAction,COUNT(*)AS nums,$query_sum AS amounts FROM sl_returns,sl_orders_products, sl_orders $query GROUP BY sl_returns.merAction $sb ";
		}elsif($in{'groupby'} eq 'id_products'){
			$report_name = "Product ID";	
			$query_tot  = "SELECT COUNT(*),$query_sum FROM sl_returns,sl_orders_products,sl_orders $query";
			#(SELECT CONCAT(LEFT(ID_products,3),'-',RIGHT(ID_products,3),' &nbsp; ',Model,'<br>',Name) FROM sl_products WHERE ID_products=RIGHT(sl_orders_products.ID_products,6))
			$query_list = "SELECT 
			IF (ID_products>200000000,
				(SELECT CONCAT(LEFT(ID_services,3),'-',RIGHT(ID_services,3),' &nbsp; ',Name) FROM sl_services WHERE ID_services=RIGHT(sl_orders_products.ID_products,6))
				,
				(SELECT CONCAT(LEFT(ID_products,3),'-',RIGHT(ID_products,3),' &nbsp; ',Model,'<br>',Name) FROM sl_products WHERE ID_products=RIGHT(sl_orders_products.ID_products,6))
			)
			
			,COUNT(*) AS nums,$query_sum AS amounts FROM sl_returns,sl_orders_products,sl_orders $query GROUP BY RIGHT(ID_products,6) $sb ";			
		}else{
			$report_name = "Date";	
			$query_tot  = "SELECT COUNT(*),$query_sum FROM sl_returns,sl_orders,sl_orders_products $query";
			$query_list = "SELECT $in{'dtype'},COUNT(*) AS nums,$query_sum AS amounts FROM sl_returns,sl_orders_products,sl_orders $query GROUP BY $in{'dtype'} $sb ";
		}
		foreach $key (keys %in){
			$in{'qs'} .= "$key=$in{$key}&" unless ($key eq 'cmd');
		}
		
		#&cgierr("$query_list,$runcmd");
	
		### Tabs
		($va{'rep1'},$va{'rep2'}) = ('on','off');

		### Report Headet
		$va{'report_tbl'} = qq |
					<center>
						<table border="0" cellspacing="0" cellpadding="4" width="70%" class="formtable">
							<tr>
						   		 <td class="menu_bar_title" colspan="2">Report Name : $report_name</td>  
							</tr>
						 <tr>
					    	<td class="smalltext">Report Units</td>  
					    	<td class="smalltext">Products / Order Net (Shipping & Taxes not Included)</td>  
						</tr>
					$va{'report_tbl'}
						<tr>
					   		 <td class="smalltext" colspan="2">Created by : ($usr{'id_admin_users'}) $usr{'firstname'} $usr{'lastname'} \@ |.&get_sql_date ." &nbsp;" . &get_time() .qq|</td>  
						</tr> 
					</table></center>\n\n\n\n\n <!--\n $query_tot \n\n $query_list\n\n-->|; 
		&auth_logging('report_view','');
		&$runcmd($query_tot,$query_list);
		return;
	}
		

	print "Content-type: text/html\n\n";
	print &build_page('rep_ret_prod.html');

}


sub rep_ret_orders{
#-----------------------------------------
# Created on: 12/09/08  13:26:41 By  Roberto Barcenas
# Forms Involved: rep_orders_return.html
# Description : Shows return  by status expressed in money group by Categorie and order date
# Parameters : from_date , to_date
	##TODO: Todos los textos deben estar fuera del codigo y/o a traves de transtxt
	##TODO:  El total deberia ser el total de la columna

	
	
	
	if($in{'action'}){
		my ($filter,$tcols,@totalR,$query);
		if(!$in{'filter'}){
			$in{'filter'} = "Active";
		}
		if ($in{'filter'} ne 'All'){
			$query = " AND sl_orders_products.Status = '$in{'filter'}'";
		}
		$tcols = 2;
		($va{'cell1'},$va{'cell2'},$va{'cell3'},$va{'cell4'},$va{'cell5'},$va{'cell6'},$va{'cell7'}) = ('off','off','off','off','off','off','off');
		($in{'filter'} eq 'Active') and ($va{'cell1'}='on');
		($in{'filter'} eq 'Exchange') and ($va{'cell2'}='on');
		($in{'filter'} eq 'Returned') and ($va{'cell3'}='on');
		($in{'filter'} eq 'Undeliverable') and ($va{'cell4'}='on');
		($in{'filter'} eq 'Lost') and ($va{'cell5'}='on');
		($in{'filter'} eq 'ReShip') and ($va{'cell6'}='on');
		($in{'filter'} eq 'All') and ($va{'cell7'}='on');
	  
	  
		$va{'searchresults'} .= '<tr class="menu_bar_title"><td align="left" width="10%">Categorie</td>';
		my ($stm) = &Do_SQL("SELECT DATE_FORMAT(Date, '%c/%y' ) AS MONTHS FROM sl_orders WHERE Date BETWEEN '$in{'from_date'}' AND '$in{'to_date'}' GROUP BY MONTHS ORDER BY date"); 
		while($dformat = $stm->fetchrow()){
				$cols .= "SUM(IF(DATE_FORMAT(sl_orders.Date,'%c/%y') = '$dformat' $query,SalePrice,0)) AS '$dformat', ";
				$va{'searchresults'} .= qq|<td align="center">$dformat</td>|;
				$tcols++;
		}
		$va{'searchresults'} .= '<td align="center">Total</td></tr>';
		
		my ($sth) = &Do_SQL("SELECT $cols
				SUM(SalePrice) AS TotalReturn, Title 
				FROM `sl_orders_products` INNER JOIN sl_orders 
				ON sl_orders.ID_orders = sl_orders_products.ID_orders
				AND `SalePrice` < 0 AND sl_orders.Date BETWEEN '$in{'from_date'}' AND '$in{'to_date'}'
				AND sl_orders.Date < sl_orders_products.Date
				AND LEFT( ID_products, 1 ) <> '6' AND sl_orders.Status NOT IN ('Cancelled', 'Void', 'System Error')
				AND sl_orders_products.Status NOT IN ('Order Cancelled', 'Inactive')
				INNER JOIN sl_products_categories 
				ON RIGHT( sl_orders_products.ID_products, 6 ) = sl_products_categories.ID_products
				INNER JOIN sl_categories 
				ON sl_products_categories.ID_categories = sl_categories.ID_categories
				GROUP BY Title" );
				
				my (@c) = split(/,/,$cfg{'srcolors'});
				while (@rec = $sth->fetchrow_array){
					$d = 1 - $d;
					$va{'searchresults'} .= qq|<tr bgcolor="$c[$d]"><td align="left">$rec[$#rec]</td>|;
					for (0..$#rec-1){
						$va{'searchresults'} .= qq|<td align="right" nowrap>|.&format_price($rec[$_]).qq|</td>|;
						$totalR[$_] += $rec[$_];
					}
					$va{'searchresults'} .= qq|</tr>|;
				}
				$va{'searchresults'} .= qq|<tr class="menu_bar_title"><td align="left">Total M/s</td>|;
				for (0..$#totalR){
					$va{'searchresults'} .= qq|<td align="right" nowrap>|.&format_price($totalR[$_]).qq|</td>|;
				}
				$va{'searchresults'} .= qq|</tr>|;
				$va{'searchresults'} = "<tr><td colspan='$tcols' class='gcell_on' align='center' style='font-size:13px;font-weight:bold;'>Showing $in{'filter'} Status</td></tr>".$va{'searchresults'};
				if($in{'print'}){
					print "Content-type: text/html\n\n";
		        	print &build_page('results_ret_orders_print.html');
		        	return;
				}
			&auth_logging('report_view','');
			print "Content-type: text/html\n\n";
			print &build_page('results_ret_orders.html');
       }else{
			print "Content-type: text/html\n\n";
			print &build_page('rep_ret_orders.html');
	}
}	


sub results_ret_prod {
#-----------------------------------------
# Created on: 03/05/09  13:25:47 By  Roberto Barcenas
# Forms Involved: results_ret_prod
# Description :
# Parameters : 

	my ($query_tot,$query_list) = @_;
	my ($sth) = &Do_SQL($query_tot);
	my ($tot_cant,$tot_amount) = $sth->fetchrow_array();
	my ($c_link);
	
	if ($tot_cant>0 and $tot_amount < 0){
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
		while (@ary = $sth->fetchrow_array){
			$d = 1 - $d;
			$id_product = substr($ary[0],0,7);
			$id_product =~ s/-//g;
			if ($in{'groupby'} eq 'id_products'){
				$c_link = " onmouseover='m_over(this)' onmouseout='m_out(this)' onClick=\"trjump('dbman?cmd=mer_products&view=$id_product')\"";
			}else{
				$c_link = '';
			}
			$va{'searchresults'} .= qq|
				<tr bgcolor='$c[$d]' $c_link>
					<td>$ary[0]</td>
					<td align="right">|.&format_number($ary[1]).qq|</td>
					<td nowrap class="help_on">&nbsp; (|.&format_number($ary[1]/$tot_cant*100).qq| %)</td>
					<td align="right" nowrap>|.&format_price($ary[2]).qq|</td>
					<td nowrap class="help_on">&nbsp; (|.&format_number($ary[2]/$tot_amount*100).qq| %)</td>
				</tr>\n|;
		}
		$va{'tot_cant'} = $tot_cant;
		$va{'tot_amount'} = &format_price($tot_amount);
	}else{
		$va{'tot_cant'} = 0;
		$va{'tot_amount'} = &format_price(0);
		$va{'matches'} = 0;
		$va{'pageslist'} = 1;
		$va{'searchresults'} .= qq|
			<tr>
				<td colspan="5" align="center">|.&trans_txt('search_nomatches').qq|</td>
			</tr>\n|;
	}
	
	if ($in{'print'}){
		print "Content-type: text/html\n\n";
		print &build_page('header_print.html');
		print &build_page('results_ret_report_print.html');
	}else{
		print "Content-type: text/html\n\n";
		print &build_page('results_ret_report.html');
	}
}

sub results_ret_categ {
#-----------------------------------------
# Created on: 03/06/09  16:31:03 By  Roberto Barcenas
# Forms Involved: 
# Description :
# Parameters :  
 			   
	my ($query,$query_sum) = @_;
	my ($choices,%tmp,$sb,$stot_cant,$stot_amount);
	my (@c) = split(/,/,$cfg{'srcolors'});
	my ($sth) = &Do_SQL("SELECT COUNT(*),$query_sum FROM sl_orders,sl_orders_products,sl_returns $query");
	my ($tot_cant,$tot_amount) = $sth->fetchrow_array();
	
	my ($sth) = &Do_SQL("SELECT ID_categories,Title FROM sl_categories WHERE Status='Active' AND ID_parent='0' ORDER BY Title;");
	while (($id_cat,$cat_name) = $sth->fetchrow_array()){
		$d = 1 - $d;
		$nquery = "$query AND RIGHT(sl_orders_products.ID_products,6) IN (SELECT ID_products FROM sl_products_categories WHERE ID_top='$id_cat') ";

		my ($sth) = &Do_SQL("SELECT COUNT(*),$query_sum FROM sl_orders,sl_orders_products,sl_returns $nquery");
		my ($cant,$amount) = $sth->fetchrow_array();
		$stot_cant   += $cant;
		$stot_amount += $amount;
		$va{'searchresults'} .= qq|
			<tr bgcolor='$c[$d]'>
				<td>$cat_name</td>
				<td align="right">|.&format_number($cant).qq|</td>
				<td nowrap class="help_on">&nbsp; (|.&format_number($cant/$tot_cant*100).qq| %)</td>
				<td align="right" nowrap>|.&format_price($amount).qq|</td>
				<td nowrap class="help_on">&nbsp; (|.&format_number($amount/$tot_amount*100).qq| %)</td>
			</tr>\n|;
		$va{'matches'}++;
	}
	$va{'matches'}++;
	$va{'pageslist'}++;
	$va{'searchresults'} .= qq|
		<tr bgcolor='$c[$d]'>
			<td>Others</td>
			<td align="right">|.&format_number($tot_cant-$stot_cant).qq|</td>
			<td nowrap class="help_on">&nbsp; (|.&format_number(($tot_cant-$stot_cant)/$tot_cant*100).qq| %)</td>
			<td align="right" nowrap>|.&format_price($tot_amount-$stot_amount).qq|</td>
			<td nowrap class="help_on">&nbsp; (|.&format_number(($tot_amount-$stot_amount)/$tot_amount*100).qq| %)</td>
		</tr>\n|;	
	$va{'tot_cant'} = $tot_cant;
	$va{'tot_amount'} = &format_price($tot_amount);

	
	if ($in{'print'}){
		print "Content-type: text/html\n\n";
		print &build_page('header_print.html');
		print &build_page('results_ret_report_print.html');
	}else{
		print "Content-type: text/html\n\n";

		print &build_page('results_ret_report.html');
	}
}

#############################################################################
#############################################################################
#   Function: rep_ret_orders_invoices
#
#       Es: Reporte que presenta las ordenes, sus facturas y devoluciones
#       En: 
#
#
#    Created on: 23/07/2013
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
sub rep_ret_orders_invoices {
#############################################################################
#############################################################################
	if($in{'action'}) {
		
		my ($query_list);
		my $maxprod=1;
		my $info_user =	'';
		my $info_pprod = '';
		my $info_oprod = '';
		my $info_time = '';
		my $sql_between = '';
		my $sql_ship_between = '';
		my $sql_idcustomers = '';
		my $sql_idorders = '';
		my $add_filters='';
		
		###### Busqueda por rango de fecha
		#$in{'from_date'} = &get_sql_date() if !$in{'from_date'};
		$in{'from_date'} = &filter_values($in{'from_date'});
		$in{'to_date'} = &filter_values($in{'to_date'});
		$in{'id_customers'} = &filter_values($in{'id_customers'});
		$in{'id_orders'} = &filter_values($in{'id_orders'});
		if ($in{'to_date'} and $in{'from_date'}) {
			$sql_between = "AND sl_orders.Date BETWEEN '$in{'from_date'}' AND '$in{'to_date'}'";
		} elsif ($in{'from_date'}) {
			$sql_between =  "AND sl_orders.Date >= '$in{'from_date'}'";
		} elsif ($in{'to_date'}) {
			$sql_between =  "AND sl_orders.Date <= '$in{'to_date'}'";
		}
		
		
		
		if ($in{'id_customers'}) {
			$sql_idcustomers = "AND sl_orders.ID_customers='$in{'id_customers'}'";
		}
		
		if ($in{'id_orders'}) {
			$sql_idorders = "AND sl_orders.ID_orders='$in{'id_orders'}'";
		}
		
		my $fname   = 'rep_ret_orders_inv_'.$cfg{'app_title'}.'.csv';
		$fname =~ s/\s/_/g;
		
		my $strHeader = "Cliente, ID Cliente,  Sucursal, Num. Orden, Estatus Orden, Fecha Orden, Devoluciones, Facturas";
		
		my ($sth) = &Do_SQL("SELECT
									count(*)
								FROM
									sl_returns_upcs
								INNER JOIN
									sl_skus ON (sl_returns_upcs.ID_parts=sl_skus.ID_sku_products )
								INNER JOIN 
									sl_parts ON ((sl_parts.ID_parts + 400000000) = sl_skus.ID_sku_products)
								INNER JOIN 
									sl_returns ON (sl_returns.ID_returns = sl_returns_upcs.ID_returns)
								INNER JOIN 
									sl_orders ON (sl_returns.ID_orders = sl_orders.ID_orders)
								INNER JOIN 
									sl_orders_products ON (sl_orders_products.ID_orders = sl_orders.ID_orders AND sl_orders_products.Related_ID_products = sl_returns_upcs.ID_parts)
								INNER JOIN 
									sl_customers ON(sl_returns.ID_customers = sl_customers.ID_customers)
								WHERE 1 $sql_idorders $sql_idcustomers $sql_between;");
		my ($total) = $sth->fetchrow();
		
		if($total) {
			print "Content-type: application/octetstream\n";
			print "Content-disposition: attachment; filename=$fname\n\n";
			print "$strHeader\r\n";
			
my $sth2 = &Do_SQL(			
	"SELECT
		(
			SELECT
			GROUP_CONCAT(
				DISTINCT CONCAT_WS(
				' , ',
				CONCAT(doc_serial, '', doc_num),
				imr_code,
				currency,
				invoice_total,
				CONCAT(STATUS, '/', invoice_type)
				) SEPARATOR ' | '
			)
			FROM
				cu_invoices_lines
			LEFT JOIN cu_invoices ON cu_invoices_lines.ID_invoices = cu_invoices.ID_invoices
			WHERE
				cu_invoices_lines.ID_orders = sl_orders.ID_orders
			AND cu_invoices. STATUS <> 'Cancelled'
			AND cu_invoices. STATUS <> 'Void'
			ORDER BY
				cu_invoices.invoice_type ASC
		) as invoices,
		sl_orders.Date,
		CONCAT_WS(', 
		',sl_orders.shp_Address1,sl_orders.shp_Address2,sl_orders.shp_Urbanization,sl_orders.shp_Zip,sl_orders.shp_City,sl_orders.shp_State,sl_orders.shp_Country) as branch,
		sl_orders.ID_orders,
		sl_orders.`Status` as order_status,
		sl_customers.company_name,
		sl_customers.ID_customers,
		(
			SELECT 
				GROUP_CONCAT(
				DISTINCT
				CONCAT_WS(
				'  ',
				CONCAT('ID Dev: ' ,sl_returns.ID_returns), CONCAT('Piezas: ' ,sl_returns_upcs.Quantity), CONCAT('ID Dev. Prod: ' ,sl_returns_upcs.ID_returns_upcs),
				CONCAT('Producto: ' ,sl_parts.`Name`), sl_parts.Model,CONCAT('UPC: ' ,sl_skus.UPC),CONCAT('ID Prod: ' ,sl_skus.ID_sku_products),
				CONCAT('Monto: ' ,(((sl_orders_products.SalePrice / sl_orders_products.Quantity) + (sl_orders_products.Tax / sl_orders_products.Quantity)) * sl_returns_upcs.Quantity))
				) SEPARATOR ' | '
				)
			FROM sl_returns_upcs
			INNER JOIN
				sl_returns ON (sl_returns.ID_returns = sl_returns_upcs.ID_returns)
			INNER JOIN
				sl_skus ON (sl_returns_upcs.ID_parts=sl_skus.ID_sku_products)
			INNER JOIN 
				sl_parts ON ((sl_parts.ID_parts + 400000000) = sl_skus.ID_sku_products)
			LEFT JOIN
				sl_orders_products ON (sl_orders_products.ID_orders = sl_returns.ID_orders AND sl_orders_products.Related_ID_products = sl_returns_upcs.ID_parts)
			WHERE sl_returns.ID_orders = sl_orders.ID_orders
		) as products_info
	FROM
		sl_orders
	INNER JOIN 
		sl_customers ON(sl_orders.ID_customers = sl_customers.ID_customers)
	WHERE 1 AND (SELECT count(*) FROM sl_returns WHERE sl_returns.ID_orders = sl_orders.ID_orders) $sql_idorders $sql_idcustomers $sql_between
	group by sl_orders.ID_orders
	/*order by sl_orders.ID_orders*/
UNION
SELECT
	
		((
			SELECT
			GROUP_CONCAT(
				DISTINCT CONCAT_WS(
				' , ',
				CONCAT(doc_serial, '', doc_num),
				imr_code,
				currency,
				invoice_total,
				CONCAT(STATUS, '/', invoice_type)
				) SEPARATOR ' | '
			)
			FROM
				cu_invoices_lines
			LEFT JOIN cu_invoices ON cu_invoices_lines.ID_invoices = cu_invoices.ID_invoices
			WHERE
				cu_invoices_lines.ID_orders = sl_orders.ID_orders
			AND cu_invoices. STATUS <> 'Cancelled'
			AND cu_invoices. STATUS <> 'Void'
			ORDER BY
				cu_invoices.invoice_type ASC
		)) as invoices,
	
		sl_orders.Date,
		CONCAT_WS(', 
		',sl_orders.shp_Address1,sl_orders.shp_Address2,sl_orders.shp_Urbanization,sl_orders.shp_Zip,sl_orders.shp_City,sl_orders.shp_State,sl_orders.shp_Country) as branch,
		sl_orders.ID_orders,
		sl_orders.`Status` as order_status,
		sl_customers.company_name,
		sl_customers.ID_customers,
		(SELECT 
				GROUP_CONCAT(
					DISTINCT CONCAT_WS('  ',
						CONCAT('ID Dev: ' ,sl_creditmemos.ID_creditmemos),
						CONCAT('Piezas: ' ,sl_creditmemos_products.Quantity),
						CONCAT('ID Dev. Prod: ' ,sl_creditmemos_products.ID_creditmemos_products),
						CONCAT('Prod: ' ,sl_parts.`Name`),
						sl_parts.Model,
						CONCAT('UPC: ' ,sl_skus.UPC),
						CONCAT('ID Prod: ' ,sl_skus.ID_sku_products),
						CONCAT('Monto: ' ,(((sl_creditmemos_products.SalePrice) + (sl_creditmemos_products.Tax)) * sl_creditmemos_products.Quantity))
					) SEPARATOR ' | '
				)
			FROM 
				sl_creditmemos_products
			INNER JOIN
				sl_creditmemos ON (sl_creditmemos_products.ID_creditmemos = sl_creditmemos.ID_creditmemos)
			INNER JOIN
				sl_creditmemos_payments ON (sl_creditmemos.ID_creditmemos = sl_creditmemos_payments.ID_creditmemos)
			INNER JOIN
				sl_skus ON (sl_creditmemos_products.ID_products = sl_skus.ID_sku_products)
			INNER JOIN 
				sl_parts ON ((sl_parts.ID_parts + 400000000) = sl_skus.ID_sku_products)
			WHERE 
				sl_creditmemos_payments.ID_orders = sl_orders.ID_orders
		) as products_info

	FROM
		sl_orders /*ON (sl_creditmemos_payments.ID_orders = sl_orders.ID_orders)*/
	INNER JOIN 
		sl_customers ON(sl_customers.ID_customers = sl_orders.ID_customers)
	WHERE 1 AND (SELECT count(*) FROM `sl_creditmemos_payments`,sl_creditmemos,sl_creditmemos_products
								WHERE 
									sl_creditmemos_payments.ID_orders=sl_orders.ID_orders
								AND sl_creditmemos.ID_creditmemos=sl_creditmemos_payments.ID_creditmemos
								AND sl_creditmemos.ID_creditmemos=sl_creditmemos_products.ID_creditmemos
								AND IF(LEFT(sl_creditmemos_products.ID_products, 1)=4,1,0)) $sql_idorders $sql_idcustomers $sql_between
order by ID_orders
");

#$sql_idorders $sql_idcustomers $sql_between

			my $records = 0;
			my $csv_string = '';
			while ($rec = $sth2->fetchrow_hashref()) {
				#############################################################################
				
				
				$csv_string .= qq|"$rec->{'company_name'}","$rec->{'ID_customers'}","$rec->{'branch'}","$rec->{'ID_orders'}","$rec->{'order_status'}","$rec->{'Date'}","$rec->{'products_info'}"|;
				#############################################################################
				
				
				my @invoices = split /\|/, $rec->{'invoices'};
				foreach my $ext_key (keys @invoices) {
					my @invoice_data = split /,/, $invoices[$ext_key];
					foreach my $int_key (keys @invoice_data) {
						$csv_string .= qq|,"$invoice_data[$int_key]"|;
					}
				}
				
				
				
				$csv_string .="\r\n";
				$records++;
				exit if($records > 5000);
			}
			
			#my @period_to_position = (',"0"',',"0"',',"0"',',"0"',',"0"',',"0"',',"0"',',"0"',',"0"');
			
			print $csv_string;
			$csv_string = '';
			
			return;
		} else {
			$va{'message'} = &trans_txt('search_nomatches');
		}
	}
	print "Content-type: text/html\n\n";
	print &build_page('rep_ret_orders_invoices.html');

}

1;
