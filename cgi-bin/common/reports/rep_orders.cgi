#!/usr/bin/perl
##################################################################
#    OPERATIONS : ORDERS   	#
##################################################################
sub rep_orders_prod {
# --------------------------------------------------------
# Created :  Carlos Haas 01/01/2007 6:47:28 PM
# Last Update : 
# Locked by : 
# Description :
##TODO: Todos los textos deben estar fuera del codigo y/o a traves de transtxt OK
# Last Modified EP: 06/11/12  12:22:54 -- Se agrega la funcion transtxt
## Checking Permission
	
	my ($sb,$query,$report_name,$query_sum);
	if ($in{'action'}){
		my ($runcmd) = 'results_orders_prod';
		my ($query_tot,$query_list);
		
		## Date Type
		if ($in{'dtype'} eq 'sl_orders.Date'){
			$va{'report_tbl'} .= "<tr><td width='100' class='smalltext'>".&trans_txt('date')." : </td><td class='smalltext'>".&trans_txt('report_order_date')."</td></tr>\n";
		}else{
			$in{'dtype'} = 'sl_orders_products.ShpDate';
			$va{'report_tbl'} .= "<tr><td width='100' class='smalltext'>".&trans_txt('date').": </td><td class='smalltext'>".&trans_txt('rep_orders_p_sdate')."</td></tr>\n";
		}
	
		if ($in{'sortby'}){
			$sb = "ORDER BY $in{'sortby'} $in{'sortorder'}";
		}
		$query = "WHERE sl_orders_products.ID_orders=sl_orders.ID_orders ";


		### Busqueda por rango de tiempo
		if($in{'from_time'} or $in{'to_time'}){
			$in{'from_time'} 	= "00:00:00"	if !$in{'from_time'};
			$in{'to_time'} 		= "23:59:59"	if !$in{'to_time'};
			$query .= " AND sl_orders.Time BETWEEN '$in{'from_time'}' AND '$in{'to_time'}'";
		}
		if(!&check_permissions($in{'cmd'}.'_onlymytype','','')){ 
			$in{'user_type'} = $usr{'user_type'};
		}
		## Filter by User
		if ($in{'user_type'}){
			$in{'user_type'} =~ s/\|/','/g;
			$va{'report_tbl'} .= "<tr><td width='100' class='smalltext'>'>".&trans_txt('by_user')." : </td><td class='smalltext'>$in{'user_type'}</td></tr>\n";
			$query .= " AND 0 < (SELECT IF(user_type IN ('$in{'user_type'}'),1,0) FROM admin_users WHERE ID_admin_users = sl_orders.ID_admin_users) ";
		}
		$in{'user_type'} =~ s/','/\|/g;
		
		## Filter by Date
		if ($in{'from_date'}){
			$va{'report_tbl'} .= "<tr><td width='100' class='smalltext'>".&trans_txt('from_date')." : </td><td class='smalltext'>$in{'from_date'}</td></tr>\n";
			$query .= " AND $in{'dtype'}>='$in{'from_date'}' ";
		}
		if ($in{'to_date'}){
			$va{'report_tbl'} .= "<tr><td width='100' class='smalltext'>".&trans_txt('to_date')." : </td><td class='smalltext'>$in{'to_date'}</td></tr>\n";
			$query .= " AND $in{'dtype'}<='$in{'to_date'}' ";
		}
		## Filter by Status
		if ($in{'status'} !~ /-1/){
			my $status=$in{'status'};
			$status =~ s/\|/','/g;
			$va{'report_tbl'} .= "<tr><td width='100' class='smalltext'>".&trans_txt('status')." : </td><td class='smalltext'>'$status'</td></tr>\n";			
			$query .= " AND sl_orders.Status IN ('$status') ";
		}elsif ($in{'excludevoid'}){
			$va{'report_tbl'} .= "<tr><td width='100' class='smalltext'>".&trans_txt('status')." : </td><td class='smalltext'>".&trans_txt('void_system_error_excluded')."</td></tr>\n";			
			$query .= " AND sl_orders.Status NOT IN ('Void','System Error') ";
		}
		
		##Filter by Free Shipping
		if($in{'freeshipping'}){
			$va{'report_tbl'} .= "<tr><td width='100' class='smalltext'>".&trans_txt('status')." : </td><td class='smalltext'>".&trans_txt('rep_orders_p_shippingt')."</td></tr>\n";			
			$query .= " AND sl_orders_products.Shipping=0 ";
		}
		
		## Filter by DID
		if ($in{'dids'} !~ /-1/){
			my $dids=$in{'dids'};
			$dids =~ s/\|/','/g;
			
			my @ary = split(/\|/,$in{'dids'});
			for (0..$#ary){
				$dname .= &load_name('sl_mediadids','didmx',$ary[$_],'num800').',';
			}
			chop($dname);
			
			$va{'report_tbl'} .= "<tr><td width='100' class='smalltext'>".&trans_txt('report_dids')." : </td><td class='smalltext'>$dname</td></tr>\n";			
			$query .= " AND sl_orders.DNIS IN ('$dids') ";  #DNIS-NUMBER
		}
		
		## Filter by Payment Exception
		if ($in{'statuspay'} !~ /-1/){
			$in{'statuspay'} =~ s/\|/','/g;
			$va{'report_tbl'} .= "<tr><td width='100' class='smalltext'>".&trans_txt('rep_orders_p_pexception')." : </td><td class='smalltext'>$in{'statuspay'}</td></tr>\n";			
			$query .= " AND sl_orders.StatusPay IN ('$in{'statuspay'}') ";
		}
		## Filter by Products Exception
		if ($in{'statusprd'} !~ /-1/){
			$in{'statusprd'} =~ s/\|/','/g;
			$va{'report_tbl'} .= "<tr><td width='100' class='smalltext'>".&trans_txt('reports_products_exception')." : </td><td class='smalltext'>$in{'statusprd'}</td></tr>\n";			
			$query .= " AND sl_orders.StatusPrd IN ('$in{'statusprd'}') ";
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
			
			$va{'report_tbl'} .= "<tr><td width='100' class='smalltext'>".&trans_txt('rep_orders_p_levels')." : </td><td class='smalltext'> $sname </td></tr>\n";									
			$query .= " AND sl_orders.ID_pricelevels IN ('$pricelevels') ";
		}
		
		## Filter by Products
		if ($in{'id_products'}){
			$in{'id_products'} = int($in{'id_products'});
			$va{'report_tbl'} .= "<tr><td width='100' class='smalltext'>".&trans_txt('product')." : </td><td class='smalltext'>(".&format_sltvid($in{'id_products'}).") ".&load_name('sl_products','ID_products',$in{'id_products'},'Name')."</td></tr>\n";
			$query .= " AND RIGHT(sl_orders_products.ID_products,6)='$in{'id_products'}' ";
		}else{
			$query .= " AND ID_products > 100000 ";
		}
		$query .= " AND sl_orders_products.Status != 'Inactive' ";
		
		
		## Filter by category
		if ($in{'id_categories'} and $in{'groupby'} ne 'category'){
			if($in{'id_categories'} > 0){
				$va{'report_tbl'} .= "<tr><td width='100' class='smalltext'>".&trans_txt('category')." : </td><td class='smalltext'>".&load_name('sl_categories','ID_categories',$in{'id_categories'},'Title')."</td></tr>\n";			
				$query .= " AND RIGHT(sl_orders_products.ID_products,6) IN (SELECT ID_products FROM sl_products_categories WHERE ID_top='$in{'id_categories'}') ";
			}else{
				$va{'report_tbl'} .= "<tr><td width='100' class='smalltext'>".&trans_txt('category')." : </td><td class='smalltext'>N/A (Others)</td></tr>\n";
				$query .= " AND RIGHT(sl_orders_products.ID_products,6) NOT IN (SELECT DISTINCT ID_products FROM sl_products_categories) ";
			}
		}
		
		## Filter by State
		if ($in{'state'}){
			$va{'report_tbl'} .= "<tr><td width='100' class='smalltext'>".&trans_txt('state')." : </td><td class='smalltext'>$in{'state'}</td></tr>\n";						
			$query .= " AND sl_orders.State='$in{'state'}' ";
		}
		
		## Filter by history
		if ($in{'history'}){
			$va{'report_tbl'} .= "<tr><td width='100' class='smalltext'>".&trans_txt('history')." : </td><td class='smalltext'>$in{'history'}</td></tr>\n";						

		}
		
		## Filter by Order Type
		if ($in{'ptype'}){
			$in{'ptype'} =~ s/\|/','/g;	
			$va{'report_tbl'} .= "<tr><td width='100' class='smalltext'>".&trans_txt('reports_order_type')." : </td><td class='smalltext'>$in{'ptype'}</td></tr>\n";						
			$query .= " AND sl_orders.Ptype IN('$in{'ptype'}') ";
		}$in{'ptype'} =~ s/','/\|/g;
			
			
		## Filter by First Call
		if ($in{'first_call'}){
			$in{'first_call'} =~ s/\|/','/g;	
			$va{'report_tbl'} .= "<tr><td width='100' class='smalltext'>".&trans_txt('reports_first_call')." : </td><td class='smalltext'>$in{'first_call'}</td></tr>\n";						
			$query .= " AND sl_orders.first_call IN('$in{'first_call'}') ";
		}$in{'first_call'} =~ s/','/\|/g;	


		## Filter by Sale Origins
		if ($in{'id_salesorigins'} !~ /-1/){
			$in{'id_salesorigins'} =~ s/-2/0/g;
			my @ary = split(/\|/,$in{'id_salesorigins'});
			$in{'id_salesorigins'} =~ s/\|/','/g;
			
			my $sname='';
			for (0..$#ary){
				if($ary[$_] == 0){
						$sname .= &trans_txt('rep_orders_p_unassigned').",";
				}else{
						$sname .= &load_name('sl_salesorigins','id_salesorigins',$ary[$_],'Channel').',';
				}
			}
			chop($sname);
			$va{'report_tbl'} .= "<tr><td width='100' class='smalltext'>".&trans_txt('reports_sales_origins')." : </td><td class='smalltext'>$sname</td></tr>\n";						
			$query .= " AND sl_orders.ID_salesorigins IN ('$in{'id_salesorigins'}') ";
		}

		### Exclude Discount
		if ($in{'excludedisc'}){
			$query_sum = "SUM(SalePrice-IF (OrderNet>0,SalePrice*OrderDisc/OrderNet,0))";
		}else{
			$va{'report_tbl'} .= "<tr><td width='100' class='smalltext'>".&trans_txt('rep_orders_p_discounts')." : </td><td class='smalltext'>NOT included</td></tr>\n";			
			$query_sum = "SUM(SalePrice*Quantity)";
		}

	    
		if($in{'groupby'} eq 'ptype'){
			$report_name = &trans_txt('reports_price_levels');
			$query_tot  = "SELECT COUNT(*),$query_sum FROM sl_orders,sl_orders_products $query";
			$query_list = "SELECT Ptype,COUNT(*) AS nums,$query_sum AS amounts FROM sl_orders_products,sl_orders $query GROUP BY Ptype $sb ";
		}elsif($in{'groupby'} eq 'dnis_usa'){
			$report_name = &trans_txt('rep_orders_p_dids_usa');
			$query_tot  = "SELECT COUNT(*),$query_sum FROM sl_orders,sl_orders_products $query";
			$query_list = "SELECT DIDS7,COUNT(*) AS nums,$query_sum AS amounts FROM sl_orders_products,sl_orders $query GROUP BY DIDS7 $sb ";
		}elsif($in{'groupby'} eq 'dnis'){
			$report_name = &trans_txt('rep_orders_p_dids_mex');
			$query_tot  = "SELECT COUNT(*),$query_sum FROM sl_orders,sl_orders_products $query";
			$query_list = "SELECT DNIS,COUNT(*) AS nums,$query_sum AS amounts FROM sl_orders_products,sl_orders $query GROUP BY DNIS $sb ";
		}elsif($in{'groupby'} eq 'halfhour'){
			$report_name = &trans_txt('rep_orders_p_id_half');
			$usr{'pref_maxh'} = 30;
			$query_tot  = "SELECT COUNT(*),$query_sum FROM sl_orders_products,sl_orders $query";
			$query_list = "SELECT IF( MINUTE( sl_orders.Time ) <=30, CONCAT( HOUR( sl_orders.Time ) , ':01 to ', HOUR( sl_orders.Time ) , ':30' ) , CONCAT( HOUR( sl_orders.Time ) , ':31 to ', HOUR( sl_orders.Time ) +1, ':00' ) ), COUNT( * ) AS hits, SUM( SalePrice - IF( OrderNet >0, SalePrice * OrderDisc / OrderNet, 0 ) ) AS amounts FROM sl_orders_products, sl_orders $query GROUP BY HOUR( sl_orders.Time ) , MINUTE( sl_orders.Time ) <=30, MINUTE( sl_orders.Time ) >30 ORDER BY HOUR( sl_orders.Time ) ";
		}elsif ($in{'groupby'} eq 'hour'){
			$report_name = &trans_txt('rep_orders_p_id_hour');
			$usr{'pref_maxh'} = 30;
			$query_tot  = "SELECT COUNT(*),$query_sum FROM sl_orders_products,sl_orders $query";
			$query_list = "SELECT HOUR(sl_orders.Time),COUNT(*) AS nums,$query_sum AS amounts FROM sl_orders_products,sl_orders $query GROUP BY HOUR(sl_orders.Time) $sb ";
		}elsif($in{'groupby'} eq 'month'){
			$report_name = &trans_txt('month');
			$query_tot  = "SELECT COUNT(*),$query_sum FROM sl_orders,sl_orders_products $query";
			$query_list = "SELECT CONCAT(MONTH($in{'dtype'}),'-',YEAR($in{'dtype'})),COUNT(*) AS nums,$query_sum AS amounts FROM sl_orders_products,sl_orders $query GROUP BY CONCAT(MONTH($in{'dtype'}),'-',YEAR($in{'dtype'})) $sb ";
		}elsif($in{'groupby'} eq 'state'){
			$report_name = &trans_txt('state');
			$query_tot  = "SELECT COUNT(*),$query_sum FROM sl_orders_products, sl_orders $query";
			$query_list = "SELECT State,COUNT(*) AS nums,$query_sum AS amounts FROM sl_orders_products, sl_orders  $query GROUP BY State $sb ";
		}elsif($in{'groupby'} eq 'category'){
			$report_name = &trans_txt('categories');
			$query_tot = $query;
			$query_list = $query_sum;
			$runcmd = 'results_orders_categ';
		}elsif($in{'groupby'} eq 'status'){
			$report_name = &trans_txt('status');
			$query_tot  = "SELECT COUNT(*),$query_sum FROM sl_orders_products, sl_orders $query";
			$query_list = "SELECT sl_orders.Status,COUNT(*)AS nums,$query_sum AS amounts FROM sl_orders_products, sl_orders $query GROUP BY sl_orders.Status $sb ";
		}elsif($in{'groupby'} eq 'statuspay'){
			$report_name = &trans_txt('rep_orders_p_pexception');
			$query_tot  = "SELECT COUNT(*),$query_sum FROM sl_orders_products, sl_orders $query";
			$query_list = "SELECT sl_orders.StatusPay,COUNT(*)AS nums,$query_sum AS amounts FROM sl_orders_products, sl_orders $query GROUP BY sl_orders.StatusPay $sb ";
		}elsif($in{'groupby'} eq 'statusprd'){
			$report_name = &trans_txt('rep_orders_p_exception');
			$query_tot  = "SELECT COUNT(*),$query_sum FROM sl_orders_products, sl_orders $query";
			$query_list = "SELECT sl_orders.StatusPrd,COUNT(*)AS nums,$query_sum AS amounts FROM sl_orders_products, sl_orders $query GROUP BY sl_orders.StatusPrd $sb ";

		}elsif($in{'groupby'} eq 'id_products'){
			$report_name = &trans_txt('rep_orders_p_idproduct');
			$query_tot  = "SELECT COUNT(*),$query_sum AS amounts FROM sl_orders_products,sl_orders $query ";
			$query_list = "SELECT 
				IF(ID_products>500000000,
				(SELECT CONCAT(LEFT(ID_services,3),'-',RIGHT(ID_services,3),'   ',Name) FROM sl_services WHERE ID_services=RIGHT(sl_orders_products.ID_products,6))
				,IF(ID_products>200000000,
				(SELECT CONCAT('00',LEFT(ID_parts,1),'-',RIGHT(ID_parts,3),'   ',Name) FROM sl_parts WHERE ID_parts=RIGHT(sl_orders_products.ID_products,6))
				,(SELECT CONCAT(LEFT(ID_products,3),'-',RIGHT(ID_products,3),'   ',Model,'',Name) FROM sl_products WHERE ID_products=RIGHT(sl_orders_products.ID_products,6)))
				)
			,COUNT(*) AS nums,$query_sum AS amounts FROM sl_orders_products,sl_orders $query GROUP BY RIGHT(ID_products,6) $sb ";			
			#$query_tot  = "SELECT COUNT(*),$query_sum FROM sl_orders_products,sl_products WHERE RIGHT(sl_orders_products.ID_products,6)=sl_products.ID_products $query";
			#$query_list = "SELECT CONCAT(LEFT(sl_products.ID_products,3),'-',RIGHT(sl_products.ID_products,3),' &nbsp; ',sl_products.Model,'<br>',sl_products.Name),COUNT(*) AS nums,$query_sum AS amounts FROM sl_orders_products,sl_products WHERE RIGHT(sl_orders_products.ID_products,6)=sl_products.ID_products $query GROUP BY sl_products.ID_products $sb ";
		}elsif($in{'groupby'} eq 'shpchg'){
			my ($sth) = &Do_SQL("SELECT ID_orders_products,ID_products,Shipping FROM sl_orders_products WHERE Shipping=0;");
			while (($id_orders_products,$id_products,$shipping) = $sth->fetchrow_array() ) {
				if (!$shipping and $id_products and $id_products =~ /^1/){
					$shipping = &load_regular_shipping(substr($id_products,3,6));
					my ($sth) = &Do_SQL("UPDATE sl_orders_products SET Shipping='$shipping' WHERE ID_orders_products='$id_orders_products';");
				}
			}
			$report_name = &trans_txt('rep_orders_p_shipping_c');
			$query_tot  = "SELECT COUNT(*),SUM(sl_orders_products.Shipping) FROM sl_orders_products, sl_orders $query";
			$query_list = "SELECT Shipping,COUNT(*)AS nums,SUM(sl_orders_products.Shipping) AS amounts FROM sl_orders_products, sl_orders $query AND LEFT(ID_products,1) <> '6' GROUP BY $in{'dtype'} $sb ";
		
		}elsif($in{'groupby'} eq 'plevels'){
			$report_name = &trans_txt('rep_orders_p_levels');
			$query_tot = $query;
			$query_list = $query_sum;
			$runcmd = 'results_orders_plevels';
		}elsif($in{'groupby'} eq 'prod-hour'){
			$report_name = &trans_txt('rep_orders_p_per_hour');
			$query_tot = $query;
			$query_list = $query_sum;
			$runcmd = 'results_orders_prodhrs';
		}elsif($in{'groupby'} eq 'analisis1'){
			$report_name = &trans_txt('rep_orders_p_order_status');
			$query_tot = $query;
			$runcmd = 'results_orders_ana1';			
		}elsif($in{'groupby'} eq 'id_skus'){
			$report_name = &trans_txt('rep_orders_p_skus');	
			$query_tot = $query;
			$query_list = $query_sum;
			$runcmd = 'results_orders_skus';
		}elsif($in{'groupby'} eq 'prod-util'){
			$report_name = &trans_txt('rep_orders_p_profit');	
			$query_tot = $query;
			$query_list = $query_sum;
			$runcmd = 'results_orders_produt';
		}else{
			$report_name = &trans_txt('date');	
			$query_tot  = "SELECT COUNT(*),$query_sum FROM sl_orders,sl_orders_products $query";
			$query_list = "SELECT $in{'dtype'},COUNT(*) AS nums,$query_sum AS amounts FROM sl_orders_products,sl_orders $query GROUP BY $in{'dtype'} $sb ";
		}
		foreach $key (keys %in){
			$in{'qs'} .= "$key=$in{$key}&" unless ($key eq 'cmd');
		}

		$va{'report_name'} = $report_name;
		### Tabs
		($va{'rep1'},$va{'rep2'},$va{'rep3'},$va{'rep4'},$va{'rep5'},$va{'rep6'},$va{'rep7'}) = ('on','off','off','off','off','off','off');

		#&cgierr("$runcmd");
		### Report Headet
		$va{'report_tbl'} = qq |
					<center>
						<table border="0" cellspacing="0" cellpadding="4" width="70%" class="formtable">
							<tr>
						   		 <td class="menu_bar_title" colspan="2">|.&trans_txt('report_name').qq|: $report_name</td>  
							</tr>
						 <tr>
					    	<td class="smalltext">|.&trans_txt('reports_units').qq|</td>  
					    	<td class="smalltext">|.&trans_txt('reports_ordernet').qq|</td>  
						</tr>
						$va{'report_tbl'}
						<tr>
					   		 <td class="smalltext" colspan="2">|.&trans_txt('reports_created_by').qq| : ($usr{'id_admin_users'}) $usr{'firstname'} $usr{'lastname'} \@ |.&get_sql_date ." &nbsp;" . &get_time() .qq|</td>  
						</tr> 
					</table></center>\n\n\n\n\n <!--\n $query_tot \n\n $query_list\n\n-->|; 
		&$runcmd($query_tot,$query_list);
		&auth_logging('report_view','');
		return;
	}

	print "Content-type: text/html\n\n";
	print &build_page('rep_orders_prod.html');
}

sub rep_orders_mm {
# --------------------------------------------------------
# Created :  Carlos Haas 01/01/2007 6:47:28 PM
# Last Update : 
# Locked by : 
# Description :
# Last Modified EP: 06/11/12  12:22:54 -- Se agrega la funcion transtxt
##TODO: Revisar el if donde se toma By DMA NO ya que marcar error al no encontrar el campo RANK

	my ($sb,$query);
	if ($in{'action'}){
		my ($runcmd) = 'results_orders_prod';
		my ($query_tot,$query_list);
				
		if ($in{'sortby'}){
			$sb = "ORDER BY $in{'sortby'} $in{'sortorder'}";
		}
		$query = "WHERE sl_zipdma.ZipCode=sl_orders.Zip";

		my ($rows) = 0;
		
		## Filter by User
		if ($in{'user_type'}){
			$in{'user_type'} =~ s/\|/','/g;
			$va{'report_tbl'} .= "<tr><td width='100' class='smalltext'>".&trans_txt('by_user')." : </td><td class='smalltext'>$in{'user_type'}</td></tr>\n";
			$query .= " AND 0 < (SELECT IF(user_type IN ('$in{'user_type'}'),1,0) FROM admin_users WHERE ID_admin_users = sl_orders.ID_admin_users) ";
		}$in{'user_type'} =~ s/','/\|/g;
		
		## Filter by Date
		if ($in{'from_date'}){
			$va{'report_tbl'} .= "<tr><td width='100' class='smalltext'>".&trans_txt('from_date')." : </td><td class='smalltext'>$in{'from_date'}</td></tr>\n";
			$query .= " AND sl_orders.Date>='$in{'from_date'}' ";
		}
		if ($in{'to_date'}){
			$va{'report_tbl'} .= "<tr><td width='100' class='smalltext'>".&trans_txt('to_date')." : </td><td class='smalltext'>$in{'to_date'}</td></tr>\n";
			$query .= " AND sl_orders.Date<='$in{'to_date'}' ";
		}
		
		### Busqueda por rango de tiempo
		if($in{'from_time'} or $in{'to_time'}){
			$in{'from_time'} 	= "00:00:00"	if !$in{'from_time'};
			$in{'to_time'} 		= "23:59:59"	if !$in{'to_time'};
			$query .= " AND sl_orders.Time BETWEEN '$in{'from_time'}' AND '$in{'to_time'}'";
		}
		## By DMA NO
		if ($in{'dma_no'}){
			$query .= " AND RANK='$in{'dma_no'}' ";
			$va{'report_tbl'} .= "<tr><td width='100' class='smalltext'>".&trans_txt('rep_orders_mm_dmas')." : </td><td class='smalltext'>($in{'dma_no'}) ".&load_name('sl_zipdma','RANK',$in{'dma_no'},'DMA_DESC')."</td></tr>\n";
		}
		## Filter by Status
		if ($in{'status'} !~ /-1/){
			$in{'status'} =~ s/\|/','/g;
			$va{'report_tbl'} .= "<tr><td width='100' class='smalltext'>".&trans_txt('status').": </td><td class='smalltext'>$in{'status'}</td></tr>\n";			
			$query .= " AND sl_orders.Status IN ('$in{'status'}') ";
		}elsif ($in{'excludevoid'}){
			$va{'report_tbl'} .= "<tr><td width='100' class='smalltext'>".&trans_txt('status')." : </td><td class='smalltext'>".&trans_txt('void_system_error_excluded')."</td></tr>\n";
			$query .= " AND sl_orders.Status NOT IN ('Void','System Error') ";
		}
		
		## Filter by DID
		if ($in{'dids'} !~ /-1/){
			my $dids=$in{'dids'};
			$dids =~ s/\|/','/g;
			
			my @ary = split(/\|/,$in{'dids'});
			for (0..$#ary){
				$dname .= &load_name('sl_mediadids','didmx',$ary[$_],'num800').',';
			}
			chop($dname);
			
			$va{'report_tbl'} .= "<tr><td width='100' class='smalltext'>".&trans_txt('report_dids')." : </td><td class='smalltext'>$dname</td></tr>\n";			
			$query .= " AND sl_orders.DNIS IN ('$dids') "; #DNIS-NUMBER
		}
		
		## Filter by Payment Exception
		if ($in{'statuspay'} !~ /-1/){
			$in{'statuspay'} =~ s/\|/','/g;
			$va{'report_tbl'} .= "<tr><td width='100' class='smalltext'>".&trans_txt('report_dids')." : </td><td class='smalltext'>$in{'statuspay'}</td></tr>\n";			
			$query .= " AND sl_orders.StatusPay IN ('$in{'statuspay'}') ";
		}
		## Filter by Products Exception
		if ($in{'statusprd'} !~ /-1/){
			$in{'statusprd'} =~ s/\|/','/g;
			$va{'report_tbl'} .= "<tr><td width='100' class='smalltext'>".&trans_txt('reports_products_exception')." : </td><td class='smalltext'>$in{'statusprd'}</td></tr>\n";			
			$query .= " AND sl_orders.StatusPrd IN ('$in{'statusprd'}') ";
		}

		## Filter by Order Type
		if ($in{'ptype'}){
			$in{'ptype'} =~ s/\|/','/g;	
			$va{'report_tbl'} .= "<tr><td width='100' class='smalltext'>".&trans_txt('reports_order_type')." : </td><td class='smalltext'>'$in{'ptype'}'</td></tr>\n";						
			$query .= " AND sl_orders.Ptype IN('$in{'ptype'}') ";
		}$in{'ptype'} =~ s/','/\|/g;

		## Filter by First Call
		if ($in{'first_call'}){
			$in{'first_call'} =~ s/\|/','/g;	
			$va{'report_tbl'} .= "<tr><td width='100' class='smalltext'>".&trans_txt('reports_first_call')." : </td><td class='smalltext'>$in{'first_call'}</td></tr>\n";						
			$query .= " AND sl_orders.first_call IN('$in{'first_call'}') ";
		}$in{'first_call'} =~ s/','/\|/g;

		## Filter by pricelevels
		if ($in{'id_pricelevels'} !~ /-1/){
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
		
		## Filter by State
		if ($in{'state'}){
			$va{'report_tbl'} .= "<tr><td width='100' class='smalltext'>".&trans_txt('state')." : </td><td class='smalltext'>$in{'state'}</td></tr>\n";						
			$query .= " AND sl_orders.State='$in{'state'}' ";
		}
		## Filter by history
		if ($in{'history'}){
			$va{'report_tbl'} .= "<tr><td width='100' class='smalltext'>".&trans_txt('history')." : </td><td class='smalltext'>$in{'history'}</td></tr>\n";						

		}
		
		## Filter by Products
		if ($in{'id_products'}){
			$in{'id_products'} = int($in{'id_products'});
			$va{'report_tbl'} .= "<tr><td width='100' class='smalltext'>".&trans_txt('product')." : </td><td class='smalltext'>(".&format_sltvid($in{'id_products'}).") ".&load_name('sl_products','ID_products',$in{'id_products'},'Name')."</td></tr>\n";
		
			if(!$in{'id_categories'}){
				my $querytmp = $query;
				$querytmp =~	s/sl_zipdma.ZipCode=sl_orders.Zip AND //;
				
				&Do_SQL("SET group_concat_max_len = 10240;");
				my $sth = &Do_SQL("SELECT IF(GROUP_CONCAT(DISTINCT sl_orders.ID_orders) IS NOT NULL,GROUP_CONCAT(DISTINCT sl_orders.ID_orders),0) FROM sl_orders INNER JOIN sl_orders_products ON sl_orders.ID_orders = sl_orders_products.ID_orders $querytmp AND RIGHT(sl_orders_products.ID_products,6)='$in{'id_products'}' ");
				my $tmp_id_orders = $sth->fetchrow();
				#&cgierr("$tmp_id_orders");
				$query .= " AND ID_orders IN($tmp_id_orders) ";
			}
		}
		
		## Filter by category
		if ($in{'id_categories'} and $in{'groupby'} ne 'category'){
			my $incat = 'IN ';
			my $cat = '';
			$incat = 'NOT '.$incat	if $in{'id_categories'} <= 0;
			$cat = " WHERE ID_top='$in{'id_categories'}'"	if $in{'id_categories'} > 0;
			my $querytmp = $query;
			$querytmp =~	s/sl_zipdma.ZipCode=sl_orders.Zip AND //;
			$querytmp .= " AND RIGHT(sl_orders_products.ID_products,6)='$in{'id_products'}' "	if $in{'id_products'};

			if($in{'id_categories'} > 0){
				$va{'report_tbl'} .= "<tr><td width='100' class='smalltext'>".&trans_txt('category')." : </td><td class='smalltext'>".&load_name('sl_categories','ID_categories',$in{'id_categories'},'Title')."</td></tr>\n";
			}else{
				$va{'report_tbl'} .= "<tr><td width='100' class='smalltext'>".&trans_txt('category')." : </td><td class='smalltext'>N/A (Others)</td></tr>\n";
			}
			
			&Do_SQL("SET group_concat_max_len = 10240;");
			my $sth = &Do_SQL("SELECT IF(GROUP_CONCAT(DISTINCT sl_orders.ID_orders) IS NOT NULL,GROUP_CONCAT(DISTINCT sl_orders.ID_orders),0) FROM sl_orders INNER JOIN sl_orders_products ON sl_orders.ID_orders = sl_orders_products.ID_orders $querytmp AND RIGHT(sl_orders_products.ID_products,6) $incat (SELECT DISTINCT ID_products FROM sl_products_categories $cat) ");
			my $tmp_id_orders = $sth->fetchrow();
			$query .= " AND ID_orders IN($tmp_id_orders) ";
		}
		
		## Filter by Sale Origins
		if ($in{'id_salesorigins'} !~ /-1/){
			$in{'id_salesorigins'} =~ s/-2/0/g;
			my @ary = split(/\|/,$in{'id_salesorigins'});
			$in{'id_salesorigins'} =~ s/\|/','/g;
			
			my $sname='';
			for (0..$#ary){
				if($ary[$_] == 0){
						$sname .= &trans_txt('rep_orders_p_unassigned').",";
				}else{
						$sname .= &load_name('sl_salesorigins','id_salesorigins',$ary[$_],'Channel').',';
				}
			}
			chop($sname);
			$va{'report_tbl'} .= "<tr><td width='100' class='smalltext'>".&trans_txt('reports_sales_origins')." : </td><td class='smalltext'>$sname</td></tr>\n";						
			$query .= " AND sl_orders.ID_salesorigins IN ('$in{'id_salesorigins'}') ";
		}
		
		
		## build report table
    	$tbl_info = $va{'report_tbl'};
		$va{'report_tbl'} = qq |
				<center>
					<table border="0" cellspacing="0" cellpadding="4" width="70%" class="formtable">
						<tr>
					    	<td class="menu_bar_title" colspan="2">Report : Selected fields</td>  
						</tr>
						<tr>
					    	<td class="smalltext">|.&trans_txt('reports_units').qq| </td>  
					    	<td class="smalltext">|.&trans_txt('reports_ordernet').qq| </td>  
						</tr>|;  
			$va{'report_tbl'} .= "$tbl_info</table></center>\n";		
						 	
		if($in{'groupby'} eq 'ptype'){
			$report_name = &trans_txt('reports_order_type');	
			$query_tot  = "SELECT COUNT(*),SUM(OrderNet) FROM sl_zipdma,sl_orders $query";
			$query_list = "SELECT Ptype,COUNT(*) AS nums,SUM(OrderNet) AS amounts FROM sl_zipdma,sl_orders $query GROUP BY Ptype $sb ";
		}elsif ($in{'groupby'} eq 'dnis_usa'){
			$query_tot  = "SELECT COUNT(*),SUM(OrderNet) FROM sl_zipdma,sl_orders $query";
			$query_list = "SELECT DIDS7,COUNT(*) AS nums,SUM(OrderNet) AS amounts FROM sl_zipdma,sl_orders $query GROUP BY DIDS7 $sb ";
		}
		elsif ($in{'groupby'} eq 'dnis'){
			$query_tot  = "SELECT COUNT(*),SUM(OrderNet) FROM sl_zipdma,sl_orders $query";
			$query_list = "SELECT DNIS,COUNT(*) AS nums,SUM(OrderNet) AS amounts FROM sl_zipdma,sl_orders $query GROUP BY DNIS $sb ";
		}else{
			$query_tot  = "SELECT COUNT(*),SUM(OrderNet) FROM sl_zipdma,sl_orders $query";
			$query_list = "SELECT CONCAT(RANK,' ',DMA_DESC),COUNT(*) AS nums,SUM(OrderNet) AS amounts FROM sl_zipdma,sl_orders $query GROUP BY DMA_NO $sb ";
		}
		#}else{
		#	$query_tot  = "SELECT COUNT(*),SUM(OrderNet) FROM sl_zipdma,sl_orders $query";
		#	$query_list = "SELECT CONCAT(RANK,' ',DMA_DESC),SUM(*) AS nums,SUM(OrderNet) AS amounts FROM sl_zipdma,sl_orders $query GROUP BY DMA_NO $sb ";
		#}
		foreach $key (keys %in){
			$in{'qs'} .= "$key=$in{$key}&" unless ($key eq 'cmd');
		}

		$va{'report_tbl'} .= "\n\n\n\n <!--\n $query_tot \n\n $query_list\n\n-->";	
		($va{'rep1'},$va{'rep2'},$va{'rep3'},$va{'rep4'},$va{'rep5'},$va{'rep6'},$va{'rep7'}) = ('off','on','off','off','off','off','off');
		&$runcmd($query_tot,$query_list);
		&auth_logging('report_view','');
		return;
	}
	
	print "Content-type: text/html\n\n";
	print &build_page('rep_orders_mm.html');
}



######################################################
#### PAYMENTS
######################################################

sub rep_orders_pay {
# --------------------------------------------------------
# Created :  Carlos Haas 01/01/2007 6:47:28 PM
# Last Update : 
# Locked by : 
# Description :
# Last Modified EP: 07/11/12  09:48:54 -- Se agrega la funcion transtxt

	my ($sb,$query);	
	if ($in{'action'}){
		my ($runcmd) = 'results_orders_pay';
		my ($query_tot,$query_list);
		
		## Date Type
		if ($in{'dtype'} eq 'sl_orders.Date'){
			$va{'report_tbl'} .= "<tr><td width='100' class='smalltext'>".&trans_txt('date')." : </td><td class='smalltext'>".&trans_txt('report_order_date')."</td></tr>\n";						
		}elsif ($in{'dtype'} eq 'sl_orders_payments.Paymentdate'){
			$va{'report_tbl'} .= "<tr><td width='100' class='smalltext'>".&trans_txt('date')." : </td><td class='smalltext'>".&trans_txt('rep_orders_pay_date')."</td></tr>\n";
		}else{
			$in{'dtype'} = 'sl_orders_payments.CapDate';
			$va{'report_tbl'} .= "<tr><td width='100' class='smalltext'>".&trans_txt('date')." : </td><td class='smalltext'>".&trans_txt('report_captured_date')."</td></tr>\n";
		}

		if ($in{'sortby'}){
			$sb = "ORDER BY $in{'sortby'} $in{'sortorder'}";
		}
		if ($in{'groupby'} ne 'fpmnt' and $in{'groupby'} ne 'amtrange' and $in{'groupby'} ne 'fppaid'){
			#$query = "WHERE  sl_orders.id_orders = sl_orders_payments.id_orders AND sl_orders_payments.Status NOT IN ('Cancelled','Order Cancelled','Void')";
			$query = "WHERE  sl_orders_payments.Status NOT IN ('Cancelled','Order Cancelled','Void') and Amount>0";# if($in{'groupby'}eq"fpst");
		}
	
		### Busqueda por rango de tiempo
		if($in{'from_time'} or $in{'to_time'}){
			$in{'from_time'} 	= "00:00:00"	if !$in{'from_time'};
			$in{'to_time'} 		= "23:59:59"	if !$in{'to_time'};
			$query .= " AND sl_orders.Time BETWEEN '$in{'from_time'}' AND '$in{'to_time'}'
									AND sl_orders_payments.Time BETWEEN '$in{'from_time'}' AND '$in{'to_time'}'";
		}

		## Filter by User
		if ($in{'user_type'}){
			$in{'user_type'} =~ s/\|/','/g;
			$va{'report_tbl'} .= "<tr><td width='100' class='smalltext'>".&trans_txt('by_user')." : </td><td class='smalltext'>$in{'user_type'}</td></tr>\n";
			$query .= " AND 0 < (SELECT IF(user_type IN ('$in{'user_type'}'),1,0) FROM admin_users WHERE ID_admin_users = sl_orders.ID_admin_users) ";
		}$in{'user_type'} =~ s/','/\|/g;
				
		## Filter by Date
		if ($in{'from_date'}){
			$va{'report_tbl'} .= "<tr><td width='100' class='smalltext'>".&trans_txt('from_date')."  : </td><td class='smalltext'>$in{'from_date'}</td></tr>\n";
			$query .= " AND $in{'dtype'}>='$in{'from_date'}' ";
		}
		if ($in{'to_date'}){
			$va{'report_tbl'} .= "<tr><td width='100' class='smalltext'>".&trans_txt('to_date')."  : </td><td class='smalltext'>$in{'to_date'}</td></tr>\n";
			$query .= " AND $in{'dtype'}<='$in{'to_date'}' ";
		}		
		
		$query .= " AND $in{'dtype'} IS NOT NULL AND $in{'dtype'} != '' AND $in{'dtype'} !='0000-00-00' "	if (!$in{'from_date'} and !$in{'to_date'} and $in{'dtype'} !~	/Paymentdate/i);
		
		## Filter by Status
		if ($in{'status'} !~ /-1/){
			$in{'status'} =~ s/\|/','/g;
			$va{'report_tbl'} .= "<tr><td width='100' class='smalltext'>".&trans_txt('status')." : </td><td class='smalltext'>$in{'status'}</td></tr>\n";						
			$query .= " AND sl_orders.Status IN ('$in{'status'}') ";
		}elsif ($in{'excludevoid'}){
			$va{'report_tbl'} .= "<tr><td width='100' class='smalltext'>".&trans_txt('status')." : </td><td class='smalltext'>".&trans_txt('void_system_error_excluded')."</td></tr>\n";			
			$query .= " AND sl_orders.Status NOT IN ('Void','System Error') ";
		}
		
		## Filter by DID
		if ($in{'dids'} !~ /-1/){
			my $dids=$in{'dids'};
			$dids =~ s/\|/','/g;
			
			my @ary = split(/\|/,$in{'dids'});
			for (0..$#ary){
				$dname .= &load_name('sl_mediadids','didmx',$ary[$_],'num800').',';
			}
			chop($dname);
			
			$va{'report_tbl'} .= "<tr><td width='100' class='smalltext'>".&trans_txt('report_dids')." : </td><td class='smalltext'>$dname</td></tr>\n";			
			$query .= " AND sl_orders.DNIS IN ('$dids') "; #DNIS-NUMBER
		}
		
		## Filter by Payment Exception
		if ($in{'statuspay'} !~ /-1/){
			$in{'statuspay'} =~ s/\|/','/g;
			$va{'report_tbl'} .= "<tr><td width='100' class='smalltext'>".&trans_txt('rep_orders_p_pexception')." : </td><td class='smalltext'>$in{'statuspay'}</td></tr>\n";			
			$query .= " AND sl_orders.StatusPay IN ('$in{'statuspay'}') ";
		}
		## Filter by Products Exception
		if ($in{'statusprd'} !~ /-1/){
			$in{'statusprd'} =~ s/\|/','/g;
			$va{'report_tbl'} .= "<tr><td width='100' class='smalltext'>".&trans_txt('reports_products_exception')." : </td><td class='smalltext'>$in{'statusprd'}</td></tr>\n";			
			$query .= " AND sl_orders.StatusPrd IN ('$in{'statusprd'}') ";
		}
		
		## Filter by Order Type
		if ($in{'ptype'}){
			$in{'ptype'} =~ s/\|/','/g;	
			$va{'report_tbl'} .= "<tr><td width='100' class='smalltext'>".&trans_txt('reports_order_type')." : </td><td class='smalltext'>'$in{'ptype'}'</td></tr>\n";						
			$query .= " AND sl_orders.Ptype IN('$in{'ptype'}') ";
		}$in{'ptype'} =~ s/','/\|/g;

		## Filter by First Call
		if ($in{'first_call'}){
			$in{'first_call'} =~ s/\|/','/g;	
			$va{'report_tbl'} .= "<tr><td width='100' class='smalltext'>".&trans_txt('reports_first_call')." : </td><td class='smalltext'>$in{'first_call'}</td></tr>\n";						
			$query .= " AND sl_orders.first_call IN('$in{'first_call'}') ";
		}$in{'first_call'} =~ s/','/\|/g;

		## Filter by pricelevels
		if ($in{'id_pricelevels'} !~ /-1/){
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
		## Filter by Payment Type
		($in{'groupby'} eq 'paytype_form') and ($in{'paytype'} eq 'Credit-Card');
		if ($in{'paytype'}){
			$va{'report_tbl'} .= "<tr><td width='100' class='smalltext'>".&trans_txt('reports_price_levels')."  : </td><td class='smalltext'>$in{'paytype'}</td></tr>\n";
			$query .= " AND sl_orders_payments.Type='$in{'paytype'}'";
		}else{
			$va{'report_tbl'} .= "<tr><td width='100' class='smalltext'>".&trans_txt('report_payment_type')." : </td><td class='smalltext'>All</td></tr>\n";
		}
		## Filter by State
		if ($in{'state'}){
			$va{'report_tbl'} .= "<tr><td width='100' class='smalltext'>".&trans_txt('state')." : </td><td class='smalltext'>$in{'state'}</td></tr>\n";									
			$query .= " AND sl_orders.State='$in{'state'}' ";
		}
		## Filter by payments.Status.
		if ($in{'pstatus'}){
		}
		## Filter by history
		if ($in{'history'}){
			$va{'report_tbl'} .= "<tr><td width='100' class='smalltext'>".&trans_txt('history')." : </td><td class='smalltext'>$in{'history'}</td></tr>\n";						
		}

		## Filter by Sale Origins
		if ($in{'id_salesorigins'} !~ /-1/){
			$in{'id_salesorigins'} =~ s/-2/0/g;
			my @ary = split(/\|/,$in{'id_salesorigins'});
			$in{'id_salesorigins'} =~ s/\|/','/g;
			
			my $sname='';
			for (0..$#ary){
				if($ary[$_] == 0){
						$sname .= &trans_txt('rep_orders_p_unassigned').",";
				}else{
						$sname .= &load_name('sl_salesorigins','id_salesorigins',$ary[$_],'Channel').',';
				}
			}
			chop($sname);
			
			
			$va{'report_tbl'} .= "<tr><td width='100' class='smalltext'>".&trans_txt('reports_sales_origins')." : </td><td class='smalltext'>$sname</td></tr>\n";						
			$query .= " AND sl_orders.ID_salesorigins IN ('$in{'id_salesorigins'}') ";
		}
		
		
		my ($cadinner);
		if ($in{'id_products'}){
			$cadinner="";
			$va{'report_tbl'} .= "<tr><td width='100' class='smalltext'>".&trans_txt('rep_orders_p_idproduct')." : </td><td class='smalltext'>(".&format_sltvid($in{'id_products'}).") ". &load_db_names('sl_products','ID_products',$in{'id_products'},'[Name] [Model]'). "</td></tr>\n";
			$cadinner=" inner join sl_orders_products on (sl_orders.ID_orders=sl_orders_products.ID_orders and right(ID_products,6)=".int($in{'id_products'}).") ";
		}
		
		## Group records by
		if($in{'groupby'} eq 'ptype')
		{
			$report_name = &trans_txt('reports_order_type');	
			$units       = &trans_txt('rep_orders_pay_payments_amounts_taxes');
			$query_tot  = "SELECT COUNT(*),SUM(amount) FROM sl_orders inner join sl_orders_payments on (sl_orders.ID_orders=sl_orders_payments.ID_orders) $cadinner $query";
			$query_list = "SELECT Ptype,COUNT(*) AS nums,SUM(amount) AS amounts FROM sl_orders inner join sl_orders_payments on (sl_orders.ID_orders=sl_orders_payments.ID_orders) $cadinner $query GROUP BY Ptype $sb ";
		}elsif ($in{'groupby'} eq 'dnis_usa'){
			$report_name = &trans_txt('rep_orders_p_dids_usa');	
			$units       = &trans_txt('rep_orders_pay_payments_amounts_taxes');
			
			$query_tot  = "SELECT COUNT(*),SUM(amount) FROM sl_orders inner join sl_orders_payments on (sl_orders.ID_orders=sl_orders_payments.ID_orders) $cadinner $query";
			$query_list = "SELECT DIDS7,COUNT(*) AS nums,SUM(amount) AS amounts FROM sl_orders inner join sl_orders_payments on (sl_orders.ID_orders=sl_orders_payments.ID_orders) $cadinner $query GROUP BY DIDS7 $sb ";
		}elsif ($in{'groupby'} eq 'dnis'){
			$report_name = &trans_txt('rep_orders_p_dids_mex');	
			$units       = &trans_txt('rep_orders_pay_payments_amounts_taxes');
			
			$query_tot  = "SELECT COUNT(*),SUM(amount) FROM sl_orders inner join sl_orders_payments on (sl_orders.ID_orders=sl_orders_payments.ID_orders) $cadinner $query";
			$query_list = "SELECT DNIS,COUNT(*) AS nums,SUM(amount) AS amounts FROM sl_orders inner join sl_orders_payments on (sl_orders.ID_orders=sl_orders_payments.ID_orders) $cadinner $query GROUP BY DNIS $sb ";
		}elsif ($in{'groupby'} eq 'day'){
			$report_name = &trans_txt('reports_day');	
			$units       = &trans_txt('rep_orders_pay_payments_amounts_taxes');
			
			$query_tot  = "SELECT COUNT(*),SUM(amount) FROM sl_orders inner join sl_orders_payments on (sl_orders.ID_orders=sl_orders_payments.ID_orders) $cadinner $query";
			$query_list = "SELECT $in{'dtype'},COUNT(*) AS nums,SUM(amount) AS amounts FROM sl_orders inner join sl_orders_payments on (sl_orders.ID_orders=sl_orders_payments.ID_orders) $cadinner $query GROUP BY $in{'dtype'} $sb ";
		}elsif($in{'groupby'} eq 'month'){
			$report_name = &trans_txt('month');	
			$units       = &trans_txt('rep_orders_pay_payments_amounts_taxes');
			
			$query_tot  = "SELECT COUNT(*),SUM(amount) FROM sl_orders inner join sl_orders_payments on (sl_orders.ID_orders=sl_orders_payments.ID_orders) $cadinner $query";
			$query_list = "SELECT CONCAT(MONTH($in{'dtype'}),'-',YEAR($in{'dtype'})),COUNT(*) AS nums,SUM(amount) AS amounts FROM sl_orders inner join sl_orders_payments on (sl_orders.ID_orders=sl_orders_payments.ID_orders) $cadinner $query GROUP BY CONCAT(MONTH($in{'dtype'}),'-',YEAR($in{'dtype'})) $sb ";
		}elsif($in{'groupby'} eq 'halfhour'){
			$report_name = &trans_txt('reports_half_hour');
			$units       = &trans_txt('rep_orders_pay_payments_amounts_taxes');			
			$usr{'pref_maxh'} = 30;
			
			$query_tot  = "SELECT COUNT(*),SUM(amount) FROM sl_orders inner join sl_orders_payments on (sl_orders.ID_orders=sl_orders_payments.ID_orders) $cadinner $query";
			$query_list = "SELECT IF( MINUTE( sl_orders_payments.Time ) <=30, CONCAT( HOUR( sl_orders_payments.Time ) , ':01 to ', HOUR( sl_orders_payments.Time ) , ':30' ) , CONCAT( HOUR( sl_orders_payments.Time ) , ':31 to ', HOUR( sl_orders_payments.Time ) +1, ':00' ) ), COUNT( * ) AS hits, SUM(Amount) AS amounts FROM sl_orders inner join sl_orders_payments on (sl_orders.ID_orders=sl_orders_payments.ID_orders) $cadinner $query GROUP BY HOUR( sl_orders_payments.Time ) , MINUTE( sl_orders_payments.Time ) <=30, MINUTE( sl_orders_payments.Time ) >30 ORDER BY HOUR( sl_orders_payments.Time ) ";
		
		}elsif($in{'groupby'} eq 'hour'){
			$report_name = &trans_txt('reports_hour');
			$units       = &trans_txt('rep_orders_pay_payments_amounts_taxes');
			$usr{'pref_maxh'} = 30;

			$query_tot  = "SELECT COUNT(*),SUM(amount) FROM sl_orders inner join sl_orders_payments on (sl_orders.ID_orders=sl_orders_payments.ID_orders) $cadinner $query";
			$query_list = "SELECT HOUR(sl_orders_payments.Time),COUNT(*) AS nums,SUM(amount) AS amounts FROM sl_orders inner join sl_orders_payments on (sl_orders.ID_orders=sl_orders_payments.ID_orders) $cadinner $query GROUP BY HOUR(sl_orders_payments.Time) $sb ";
		}elsif($in{'groupby'} eq 'state'){
			$report_name = &trans_txt('state');
			$units       = &trans_txt('rep_orders_pay_payments_amounts_taxes');			
			$query_tot  = "SELECT COUNT(*),SUM(amount) FROM sl_orders inner join sl_orders_payments on (sl_orders.ID_orders=sl_orders_payments.ID_orders) $cadinner $query";
			$query_list = "SELECT State,COUNT(*) AS nums,SUM(amount) AS amounts FROM sl_orders inner join sl_orders_payments on (sl_orders.ID_orders=sl_orders_payments.ID_orders) $cadinner $query GROUP BY State $sb ";
		}elsif($in{'groupby'} eq 'status'){
			$report_name = &trans_txt('status');
			$units       = &trans_txt('rep_orders_pay_payments_amounts_taxes');
			$query_tot  = "SELECT COUNT(*),SUM(amount) FROM sl_orders inner join sl_orders_payments on (sl_orders.ID_orders=sl_orders_payments.ID_orders) $cadinner $query";
			$query_list = "SELECT sl_orders.Status,COUNT(*)AS nums,SUM(amount) AS amounts FROM sl_orders inner join sl_orders_payments on (sl_orders.ID_orders=sl_orders_payments.ID_orders) $cadinner $query GROUP BY sl_orders.Status $sb ";
		}elsif($in{'groupby'} eq 'paytype'){
			$report_name = &trans_txt('rep_orders_pay_type_pay');
			$units       = &trans_txt('rep_orders_pay_payments_amounts_taxes');
			$query_tot  = "SELECT COUNT(*),SUM(amount) FROM sl_orders inner join sl_orders_payments on (sl_orders.ID_orders=sl_orders_payments.ID_orders) $cadinner $query";
			$query_list = "SELECT sl_orders_payments.Type,COUNT(*) AS nums,SUM(amount) AS amounts FROM sl_orders inner join sl_orders_payments on (sl_orders.ID_orders=sl_orders_payments.ID_orders) $cadinner $query GROUP BY sl_orders_payments.Type $sb ";
		}elsif($in{'groupby'} eq 'paytype_form'){
			$report_name = &trans_txt('rep_orders_pay_type_pay_type');
			$units       = &trans_txt('rep_orders_pay_payments_amounts_taxes');
			$query_tot  = "SELECT COUNT(*),SUM(amount) FROM sl_orders inner join sl_orders_payments on (sl_orders.ID_orders=sl_orders_payments.ID_orders) $cadinner $query";
			$query_list = "SELECT sl_orders_payments.PmtField1,COUNT(*) AS nums,SUM(amount) AS amounts FROM sl_orders inner join sl_orders_payments on (sl_orders.ID_orders=sl_orders_payments.ID_orders) $cadinner $query GROUP BY sl_orders_payments.PmtField1 $sb ";
		}elsif($in{'groupby'} eq 'fp'){
			$report_name = &trans_txt('rep_orders_pay_flexipago');
			$units       = &trans_txt('rep_orders_pay_orders_amounts_taxes');
			$query_tot = $query;
			$runcmd = 'results_orders_fpago';
		}elsif($in{'groupby'} eq 'fpst'){
			$report_name = &trans_txt('rep_orders_pay_flexipago_aging');
			$units       = &trans_txt('rep_orders_pay_payments_amounts_taxes');
			$query_tot = $query;
			$runcmd = 'results_orders_fpago_st';
		}elsif($in{'groupby'} eq 'fcol'){
			$report_name = &trans_txt('rep_orders_pay_flexipago_coll');
			$units       = &trans_txt('rep_orders_pay_payments_amounts_taxes');
			$query_tot = $query;
			$runcmd = 'results_orders_fpago_col';
		}elsif($in{'groupby'} eq 'fpmnt'){
			$report_name = &trans_txt('rep_orders_pay_account_receivable');
			$units       = &trans_txt('rep_orders_pay_payments_amounts_taxes');
			$query_tot = $query;
			$runcmd = 'results_orders_fpmnt';
		}elsif($in{'groupby'} eq 'amtrange'){
			$report_name = &trans_txt('rep_orders_pay_flexipago_amount_range');
			$units       = &trans_txt('rep_orders_pay_payments_amounts_taxes');
			$query_tot = $query;
			$runcmd = 'results_orders_amtrange';
		}elsif($in{'groupby'} eq 'fppaid'){
			$report_name = &trans_txt('rep_orders_pay_flexipago__payments');
			$units       = &trans_txt('rep_orders_pay_payments_amounts_taxes');
			$query_tot = $query;
			$runcmd = 'results_orders_fppaid';
		}	
					
		foreach $key (keys %in){
			$in{'qs'} .= "$key=$in{$key}&" unless ($key eq 'cmd');
		}
		## Tabs
		($va{'rep1'},$va{'rep2'},$va{'rep3'},$va{'rep4'},$va{'rep5'},$va{'rep6'},$va{'rep7'}) = ('off','off','on','off','off','off','off');
		
		### Report Headet
		$va{'report_tbl'} = qq |
					<center>
						<table border="0" cellspacing="0" cellpadding="4" width="70%" class="formtable">
							<tr>
						   		 <td class="menu_bar_title" colspan="2">|.&trans_txt('report_name').qq| : $report_name</td>  
							</tr> 
							<tr>
						    	<td class="smalltext">|.&trans_txt('reports_units').qq|</td>  
						    	<td class="smalltext">$units</td>  
							</tr>
					$va{'report_tbl'}
						<tr>
					   		 <td class="smalltext" colspan="2">|.&trans_txt('reports_created_by').qq| : ($usr{'id_admin_users'}) $usr{'firstname'} $usr{'lastname'} \@ |.&get_sql_date ." &nbsp;" . &get_time() .qq|</td>  
						</tr> 
					</table></center>\n\n\n\n\n <!--\n $query_tot \n\n $query_list\n\n-->|; 
		
		&$runcmd($query_tot,$query_list);
		&auth_logging('report_view','');
		return;
	}
	
	print "Content-type: text/html\n\n";
	print &build_page('rep_orders_pay.html');
}





###################################################################
#########  USERS
###################################################################

sub rep_orders_usr {
# --------------------------------------------------------
# Created :  Carlos Haas 01/01/2007 6:47:28 PM
# Last Update : 
# Locked by : 
# Description :
# Last Modified EP: 07/11/12  10:10:54 -- Se agrega la funcion transtxt

	my ($sb,$query);
	
	if ($in{'action'}){
		my ($runcmd) = 'results_orders_usr';
		my ($query_tot,$query_list);
		
		if ($in{'sortby'}){
			$sb = "ORDER BY $in{'sortby'} $in{'sortorder'}";
		}
		$query = 'WHERE sl_orders_products.ID_orders=sl_orders.ID_orders and sl_orders.ID_admin_users=admin_users.ID_admin_users';
		
		my ($rows) = 0;
		## Filter by Date
		if ($in{'from_date'}){
			$va{'report_tbl'} .= "<tr><td width='100' class='smalltext'>".&trans_txt('from_date')." : </td><td class='smalltext'>$in{'from_date'}</td></tr>\n";
			$query .= " AND sl_orders.Date>='$in{'from_date'}' ";
		}
		if ($in{'to_date'}){
			$va{'report_tbl'} .= "<tr><td width='100' class='smalltext'>".&trans_txt('to_date')." : </td><td class='smalltext'>$in{'to_date'}</td></tr>\n";				
			$query .= " AND sl_orders.Date<='$in{'to_date'}' ";
		}
		
		### Busqueda por rango de tiempo
		if($in{'from_time'} or $in{'to_time'}){
			$in{'from_time'} 	= "00:00:00"	if !$in{'from_time'};
			$in{'to_time'} 		= "23:59:59"	if !$in{'to_time'};
			$query .= " AND sl_orders.Time BETWEEN '$in{'from_time'}' AND '$in{'to_time'}' ";
		}
		
		## Filter by Status
		if ($in{'status'} !~ /-1/){
			$in{'status'} =~ s/\|/','/g;
			$va{'report_tbl'} .= "<tr><td width='100' class='smalltext'>".&trans_txt('status')." : </td><td class='smalltext'>$in{'status'}</td></tr>\n";						
			$query .= " AND sl_orders.Status IN ('$in{'status'}') ";
		}
		
		## Filter by DID
		if ($in{'dids'} !~ /-1/){
			my $dids=$in{'dids'};
			$dids =~ s/\|/','/g;
			
			my @ary = split(/\|/,$in{'dids'});
			for (0..$#ary){
				$dname .= &load_name('sl_mediadids','didmx',$ary[$_],'num800').',';
			}
			chop($dname);
			
			$va{'report_tbl'} .= "<tr><td width='100' class='smalltext'>".&trans_txt('report_dids')." : </td><td class='smalltext'>$dname</td></tr>\n";			
			$query .= " AND sl_orders.DNIS IN ('$dids') "; #DNIS-NUMBER
		}
		
		
		## Filter by Payment Exception
		if ($in{'statuspay'} !~ /-1/){
			$in{'statuspay'} =~ s/\|/','/g;
			$va{'report_tbl'} .= "<tr><td width='100' class='smalltext'>".&trans_txt('rep_orders_p_pexception')." : </td><td class='smalltext'>$in{'statuspay'}</td></tr>\n";			
			$query .= " AND sl_orders.StatusPay IN ('$in{'statuspay'}') ";
		}
		## Filter by Products Exception
		if ($in{'statusprd'} !~ /-1/){
			$in{'statusprd'} =~ s/\|/','/g;
			$va{'report_tbl'} .= "<tr><td width='100' class='smalltext'>".&trans_txt('reports_products_exception')." : </td><td class='smalltext'>$in{'statusprd'}</td></tr>\n";			
			$query .= " AND sl_orders.StatusPrd IN ('$in{'statusprd'}') ";
		}

		## Filter by Order Type
		if ($in{'ptype'}){
			$in{'ptype'} =~ s/\|/','/g;	
			$va{'report_tbl'} .= "<tr><td width='100' class='smalltext'>".&trans_txt('reports_order_type')." : </td><td class='smalltext'>'$in{'ptype'}'</td></tr>\n";						
			$query .= " AND sl_orders.Ptype IN('$in{'ptype'}') ";
		}$in{'ptype'} =~ s/','/\|/g;

		## Filter by First Call
		if ($in{'first_call'}){
			$in{'first_call'} =~ s/\|/','/g;	
			$va{'report_tbl'} .= "<tr><td width='100' class='smalltext'>".&trans_txt('reports_first_call')." : </td><td class='smalltext'>$in{'first_call'}</td></tr>\n";						
			$query .= " AND sl_orders.first_call IN('$in{'first_call'}') ";
		}$in{'first_call'} =~ s/','/\|/g;


		## Filter by pricelevels
		if ($in{'id_pricelevels'} !~ /-1/){
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
		if ($in{'id_admin_users'}){
			$username = &load_db_names('admin_users','ID_admin_users',$in{'id_admin_users'},'[FirstName] [MiddleName] [LastName]');
			if ($username eq ""){
				$username = "---";
			}
			$va{'report_tbl'} .= "<tr><td width='100' class='smalltext'>".&trans_txt('reports_user_name')." : </td><td class='smalltext'>($in{'id_admin_users'}) $username</td></tr>\n";			
			$query .= " AND sl_orders_products.ID_admin_users='$in{'id_admin_users'}' ";
		}else{
			$query .= " AND admin_users.ID_admin_users > 0 ";
		}
		## Filter by category
		if ($in{'id_categories'} and $in{'groupby'} ne 'category'){
			if($in{'id_categories'} > 0){
				$va{'report_tbl'} .= "<tr><td width='100' class='smalltext'>".&trans_txt('category')." : </td><td class='smalltext'>".&load_name('sl_categories','ID_categories',$in{'id_categories'},'Title')."</td></tr>\n";			
				$query .= " AND RIGHT(sl_orders_products.ID_products,6) IN (SELECT ID_products FROM sl_products_categories WHERE ID_top='$in{'id_categories'}') ";
			}else{
				$va{'report_tbl'} .= "<tr><td width='100' class='smalltext'>".&trans_txt('category')." : </td><td class='smalltext'>N/A (Others)</td></tr>\n";
				$query .= " AND RIGHT(sl_orders_products.ID_products,6) NOT IN (SELECT DISTINCT ID_products FROM sl_products_categories) ";
			}
		}
		## Filter by State
		if ($in{'state'}){
			$va{'report_tbl'} .= "<tr><td width='100' class='smalltext'>".&trans_txt('state')." : </td><td class='smalltext'>$in{'state'}</td></tr>\n";									
			$query .= " AND sl_orders.State='$in{'state'}' ";
		}
		
		## Filter by Sale Origins
		if ($in{'id_salesorigins'} !~ /-1/){
			$in{'id_salesorigins'} =~ s/-2/0/g;
			my @ary = split(/\|/,$in{'id_salesorigins'});
			$in{'id_salesorigins'} =~ s/\|/','/g;
			
			my $sname='';
			for (0..$#ary){
				if($ary[$_] == 0){
						$sname .= &trans_txt('rep_orders_p_unassigned').",";
				}else{
						$sname .= &load_name('sl_salesorigins','id_salesorigins',$ary[$_],'Channel').',';
				}
			}
			chop($sname);
			$va{'report_tbl'} .= "<tr><td width='100' class='smalltext'>".&trans_txt('reports_sales_origins')." : </td><td class='smalltext'>$sname</td></tr>\n";						
			$query .= " AND sl_orders.ID_salesorigins IN ('$in{'id_salesorigins'}') ";
		}
		
		if(!&check_permissions($in{'cmd'}.'_onlymyutype','','')){ 
			$in{'user_type'} = $usr{'user_type'};
		}
		## Filter by User
		if ($in{'user_type'}){
			$in{'user_type'} =~ s/\|/','/g;
			$va{'report_tbl'} .= "<tr><td width='100' class='smalltext'>'>".&trans_txt('by_user')." : </td><td class='smalltext'>$in{'user_type'}</td></tr>\n";
			$query .= " AND 0 < (SELECT IF(user_type IN ('$in{'user_type'}'),1,0) FROM admin_users WHERE ID_admin_users = sl_orders.ID_admin_users) ";
		}
		$in{'user_type'} =~ s/','/\|/g;		
		
		#&cgierr("$query");	
		
		if($in{'groupby'} eq 'ptype'){
			$report_name = &trans_txt('reports_order_type');
			$query_tot  = "SELECT COUNT(*),SUM(SalePrice*Quantity) FROM admin_users,sl_orders_products,sl_orders $query";
			$query_list = "SELECT Ptype,COUNT(*) AS nums,SUM(SalePrice*Quantity) AS amounts FROM  admin_users,sl_orders_products,sl_orders $query GROUP BY Ptype $sb ";
		}elsif ($in{'groupby'} eq 'dnis_usa'){
			$report_name = &trans_txt('rep_orders_p_dids_usa');
			$query_tot  = "SELECT COUNT(*),SUM(SalePrice*Quantity) FROM admin_users,sl_orders_products,sl_orders $query";
			$query_list = "SELECT DIDS7,COUNT(*) AS nums,SUM(SalePrice*Quantity) AS amounts FROM  admin_users,sl_orders_products,sl_orders $query GROUP BY DIDS7 $sb ";
		}elsif ($in{'groupby'} eq 'dnis'){
			$report_name = &trans_txt('rep_orders_p_dids_mex');
			$query_tot  = "SELECT COUNT(*),SUM(SalePrice*Quantity) FROM admin_users,sl_orders_products,sl_orders $query";
			$query_list = "SELECT DNIS,COUNT(*) AS nums,SUM(SalePrice*Quantity) AS amounts FROM  admin_users,sl_orders_products,sl_orders $query GROUP BY DNIS $sb ";
		}elsif ($in{'groupby'} eq 'day'){
			$report_name = &trans_txt('reports_day');
			$query_tot  = "SELECT COUNT(*),SUM(SalePrice*Quantity) FROM admin_users,sl_orders_products,sl_orders $query";
			$query_list = "SELECT sl_orders.Date,COUNT(*) AS nums,SUM(SalePrice*Quantity) AS amounts FROM  admin_users,sl_orders_products,sl_orders $query GROUP BY sl_orders.Date $sb ";
		}elsif($in{'groupby'} eq 'month'){
			$report_name = &trans_txt('month');
			$query_tot  = "SELECT COUNT(*),SUM(SalePrice*Quantity) FROM admin_users,sl_orders_products,sl_orders $query";
			$query_list = "SELECT CONCAT(MONTH(sl_orders.Date),'-',YEAR(sl_orders.Date)),COUNT(*) AS nums,SUM(SalePrice*Quantity) AS amounts FROM  admin_users,sl_orders_products,sl_orders $query GROUP BY CONCAT(MONTH(sl_orders.Date),'-',YEAR(sl_orders.Date)) $sb ";
		}elsif($in{'groupby'} eq 'halfhour'){
			$report_name = &trans_txt('reports_half_hour');			
			$usr{'pref_maxh'} = 30;
			$query_tot  = "SELECT COUNT(*),SUM(SalePrice*Quantity) FROM  admin_users,sl_orders_products,sl_orders $query";
			$query_list = "SELECT IF( MINUTE( sl_orders.Time ) <=30, CONCAT( HOUR( sl_orders.Time ) , ':01 to ', HOUR( sl_orders.Time ) , ':30' ) , CONCAT( HOUR( sl_orders.Time ) , ':31 to ', HOUR( sl_orders.Time ) +1, ':00' ) ), COUNT( * ) AS hits, SUM(SalePrice*Quantity) AS amounts FROM  admin_users,sl_orders_products,sl_orders $query GROUP BY HOUR( sl_orders.Time ) , MINUTE( sl_orders.Time ) <=30, MINUTE( sl_orders.Time ) >30 ORDER BY HOUR( sl_orders.Time ) ";
		}elsif($in{'groupby'} eq 'hour'){
			$report_name = &trans_txt('reports_hour');
			$usr{'pref_maxh'} = 30;
			$query_tot  = "SELECT COUNT(*),SUM(SalePrice*Quantity) FROM  admin_users,sl_orders_products,sl_orders $query";
			$query_list = "SELECT HOUR(sl_orders.Time),COUNT(*) AS nums,SUM(SalePrice*Quantity) AS amounts FROM  admin_users,sl_orders_products,sl_orders $query GROUP BY HOUR(sl_orders.Time) $sb ";
		}elsif($in{'groupby'} eq 'state'){
			$report_name = &trans_txt('state');
			$query_tot  = "SELECT COUNT(*),SUM(SalePrice*Quantity) FROM  admin_users,sl_orders_products, sl_orders $query";
			$query_list = "SELECT State,COUNT(*) AS nums,SUM(SalePrice*Quantity) AS amounts FROM  admin_users,sl_orders_products, sl_orders  $query GROUP BY State $sb ";
		}elsif($in{'groupby'} eq 'category'){
			$report_name = &trans_txt('category');
			$report_name = &trans_txt('categories');
			$query_tot  = ",admin_users $query" ;
			$query_list = " SUM(SalePrice*Quantity) ";		
			$runcmd = 'results_orders_categ';
			$in{'extra_table'} = '';
		}elsif($in{'groupby'} eq 'status'){
			$report_name = &trans_txt('status');
			$query_tot  = "SELECT COUNT(*),SUM(SalePrice*Quantity) FROM  admin_users,sl_orders_products, sl_orders $query";
			$query_list = "SELECT sl_orders.Status,COUNT(*)AS nums,SUM(SalePrice*Quantity) AS amounts FROM  admin_users,sl_orders_products, sl_orders $query GROUP BY sl_orders.Status $sb ";
		}elsif($in{'groupby'} eq 'id_admin_users'){
			$report_name = &trans_txt('reports_user_admin');
			$query_tot  = "SELECT COUNT(*),SUM(SalePrice*Quantity) FROM  admin_users,sl_orders_products,sl_orders $query";
			$query_list = "SELECT (SELECT CONCAT(admin_users.ID_admin_users,' &nbsp; ',FirstName,' &nbsp; ',LastName) FROM  admin_users,sl_orders WHERE admin_users.ID_admin_users=sl_orders.ID_admin_users and sl_orders.ID_orders=sl_orders_products.ID_orders),COUNT(*) AS nums,SUM(SalePrice*Quantity) AS amounts FROM admin_users,sl_orders_products,sl_orders $query GROUP BY admin_users.ID_admin_users $sb ";
		}
		foreach $key (keys %in){
			$in{'qs'} .= "$key=$in{$key}&" unless ($key eq 'cmd');
		}
		
		## build report table
	    $tbl_info = $va{'report_tbl'};
		$va{'report_tbl'} = qq |
			<center>
					<table border="0" cellspacing="0" cellpadding="4" width="70%" class="formtable">
						<tr>
						    <td class="menu_bar_title" colspan="2">|.&trans_txt('report_name').qq| : $report_name</td>  
						</tr>
						<tr>
					    	<td class="smalltext">|.&trans_txt('reports_units').qq| </td>  
					    	<td class="smalltext">|.&trans_txt('reports_ordernet').qq|</td>  
						</tr>|;  
			$va{'report_tbl'} .= "$tbl_info</table></center>\n";						
		
		
		($va{'rep1'},$va{'rep2'},$va{'rep3'},$va{'rep4'},$va{'rep5'},$va{'rep6'},$va{'rep7'}) = ('off','off','off','on','off','off','off');
		&$runcmd($query_tot,$query_list);
		&auth_logging('report_view','');
		return;
	}
	
	print "Content-type: text/html\n\n";
	print &build_page('rep_orders_usr.html');
}




###################################################################
#########  CUSTOMERS
###################################################################

sub rep_orders_cust {
# --------------------------------------------------------
# Created :  Carlos Haas 01/01/2007 6:47:28 PM
# Last Update : 
# Locked by : 
# Description :
# Last Modified EP: 07/11/12  10:30:54 -- Se agrega la funcion transtxt
	my ($sb,$query);
	
	if ($in{'action'}){
		my ($runcmd) = 'results_orders_cust';
		my ($query_tot,$query_list);
		
		if ($in{'sortby'}){
			$sb = "ORDER BY $in{'sortby'} $in{'sortorder'}";
		}
		
		## Group by Admin User	
		if ($in{'groupby'} eq 'id_admin_users'){
			$query .= ",admin_users WHERE sl_orders.ID_customers=sl_customers.ID_customers AND sl_orders.ID_admin_users = admin_users.ID_admin_users ";
		}else{
			$query = 'WHERE sl_orders.ID_customers=sl_customers.ID_customers';
		}
		
		my ($rows) = 0;
		
		## Filter by User Type
		if ($in{'user_type'}){
			$in{'user_type'} =~ s/\|/','/g;
			$va{'report_tbl'} .= "<tr><td width='100' class='smalltext'>".&trans_txt('by_user')." : </td><td class='smalltext'>$in{'user_type'}</td></tr>\n";
			$query .= " AND 0 < (SELECT IF(user_type IN ('$in{'user_type'}'),1,0) FROM admin_users WHERE ID_admin_users = sl_orders.ID_admin_users) ";
		}$in{'user_type'} =~ s/','/\|/g;
		
		## Filter by Date
		if ($in{'from_date'}){
			$va{'report_tbl'} .= "<tr><td width='100' class='smalltext'>".&trans_txt('from_date')." : </td><td class='smalltext'>$in{'from_date'}</td></tr>\n";
			$query .= " AND sl_orders.Date>='$in{'from_date'}' ";
		}
		if ($in{'to_date'}){
			$va{'report_tbl'} .= "<tr><td width='100' class='smalltext'>".&trans_txt('to_date')." : </td><td class='smalltext'>$in{'to_date'}</td></tr>\n";
			$query .= " AND sl_orders.Date<='$in{'to_date'}' ";
		}
		
		### Busqueda por rango de tiempo
		if($in{'from_time'} or $in{'to_time'}){
			$in{'from_time'} 	= "00:00:00"	if !$in{'from_time'};
			$in{'to_time'} 		= "23:59:59"	if !$in{'to_time'};
			$query .= " AND sl_orders.Time BETWEEN '$in{'from_time'}' AND '$in{'to_time'}' ";
		}
		
		
		## Filter by Status
		if ($in{'status'} !~ /-1/){
			$in{'status'} =~ s/\|/','/g;
			$va{'report_tbl'} .= "<tr><td width='100' class='smalltext'>".&trans_txt('status')." : </td><td class='smalltext'>$in{'status'}</td></tr>\n";						
			$query .= " AND sl_orders.Status IN ('$in{'status'}') ";
		}elsif ($in{'excludevoid'}){
			$va{'report_tbl'} .= "<tr><td width='100' class='smalltext'>".&trans_txt('status')." : </td><td class='smalltext'>".&trans_txt('void_system_error_excluded')."</td></tr>\n";			
			$query .= " AND sl_orders.Status NOT IN ('Void','System Error') ";
		}
		
		## Filter by DID
		if ($in{'dids'} !~ /-1/){
			my $dids=$in{'dids'};
			$dids =~ s/\|/','/g;
			
			my @ary = split(/\|/,$in{'dids'});
			for (0..$#ary){
				$dname .= &load_name('sl_mediadids','didmx',$ary[$_],'num800').',';
			}
			chop($dname);
			
			$va{'report_tbl'} .= "<tr><td width='100' class='smalltext'>".&trans_txt('report_dids')." : </td><td class='smalltext'>$dname</td></tr>\n";			
			$query .= " AND sl_orders.DNIS IN ('$dids') "; #DNIS-NUMBER
		}
		
		## Filter by Payment Exception
		if ($in{'statuspay'} !~ /-1/){
			$in{'statuspay'} =~ s/\|/','/g;
			$va{'report_tbl'} .= "<tr><td width='100' class='smalltext'>".&trans_txt('rep_orders_p_pexception')." : </td><td class='smalltext'>$in{'statuspay'}</td></tr>\n";			
			$query .= " AND sl_orders.StatusPay IN ('$in{'statuspay'}') ";
		}
		## Filter by Products Exception
		if ($in{'statusprd'} !~ /-1/){
			$in{'statusprd'} =~ s/\|/','/g;
			$va{'report_tbl'} .= "<tr><td width='100' class='smalltext'>".&trans_txt('reports_products_exception')." : </td><td class='smalltext'>$in{'statusprd'}</td></tr>\n";			
			$query .= " AND sl_orders.StatusPrd IN ('$in{'statusprd'}') ";
		}

		## Filter by Order Type
		if ($in{'ptype'}){
			$in{'ptype'} =~ s/\|/','/g;	
			$va{'report_tbl'} .= "<tr><td width='100' class='smalltext'>".&trans_txt('reports_order_type')." : </td><td class='smalltext'>'$in{'ptype'}'</td></tr>\n";						
			$query .= " AND sl_orders.Ptype IN('$in{'ptype'}') ";
		}$in{'ptype'} =~ s/','/\|/g;

		## Filter by First Call
		if ($in{'first_call'}){
			$in{'first_call'} =~ s/\|/','/g;	
			$va{'report_tbl'} .= "<tr><td width='100' class='smalltext'>".&trans_txt('reports_first_call')." : </td><td class='smalltext'>$in{'first_call'}</td></tr>\n";						
			$query .= " AND sl_orders.first_call IN('$in{'first_call'}') ";
		}$in{'first_call'} =~ s/','/\|/g;

		## Filter by Order Type
		if ($in{'type'}){
			$in{'type'} =~ s/\|/','/g;	
			$va{'report_tbl'} .= "<tr><td width='100' class='smalltext'>".&trans_txt('reports_type')." : </td><td class='smalltext'>'$in{'type'}'</td></tr>\n";						
			$query .= " AND sl_customers.Type IN('$in{'type'}') ";
		}$in{'type'} =~ s/','/\|/g;
			
			
		## Filter by pricelevels
		if ($in{'id_pricelevels'} !~ /-1/){
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
		
		## Filter by Admin User	
		if ($in{'id_admin_users'}){
			$username = &load_db_names('admin_users','ID_admin_users',$in{'id_admin_users'},'[FirstName] [MiddleName] [LastName]');
			if ($username eq ""){
				$username = "---";
			}
			$va{'report_tbl'} .= "<tr><td width='100' class='smalltext'>".&trans_txt('reports_user_name')." : </td><td class='smalltext'>($in{'id_admin_users'}) $username</td></tr>\n";			
			$query .= " AND sl_orders.ID_admin_users='$in{'id_admin_users'}' ";
		}else{
			$query .= " AND sl_orders.ID_admin_users > 0 ";
		}
		
		## Filter by Customer	
		if ($in{'id_customers'}){
			$custname = &load_db_names('sl_customers','ID_customers',$in{'id_customers'},'[FirstName] [MiddleName] [LastName]');
			if ($username eq ""){
				$custname = "---";
			}
			$va{'report_tbl'} .= "<tr><td width='100' class='smalltext'>".&trans_txt('reports_customer')." : </td><td class='smalltext'>($in{'id_customers'}) $custname</td></tr>\n";			
			$query .= " AND sl_orders.ID_customers='$in{'id_customers'}' ";
		}else{
			$query .= " AND sl_orders.ID_customers > 0 ";
		}
		
		## Filter by State
		if ($in{'state'}){
			$va{'report_tbl'} .= "<tr><td width='100' class='smalltext'>".&trans_txt('state')." : </td><td class='smalltext'>$in{'state'}</td></tr>\n";									
			$query .= " AND sl_orders.State='$in{'state'}' ";
		}
		
		## Filter by history
		if ($in{'history'}){
			$va{'report_tbl'} .= "<tr><td width='100' class='smalltext'>".&trans_txt('history')." : </td><td class='smalltext'>$in{'history'}</td></tr>\n";						

		}

		## Filter by Sale Origins
		if ($in{'id_salesorigins'} !~ /-1/){
			$in{'id_salesorigins'} =~ s/-2/0/g;
			my @ary = split(/\|/,$in{'id_salesorigins'});
			$in{'id_salesorigins'} =~ s/\|/','/g;
			
			my $sname='';
			for (0..$#ary){
				if($ary[$_] == 0){
						$sname .= &trans_txt('rep_orders_p_unassigned').",";
				}else{
						$sname .= &load_name('sl_salesorigins','id_salesorigins',$ary[$_],'Channel').',';
				}
			}
			chop($sname);
			
			
			$va{'report_tbl'} .= "<tr><td width='100' class='smalltext'>".&trans_txt('reports_sales_origins').": </td><td class='smalltext'>$sname</td></tr>\n";						
			$query .= " AND sl_orders.ID_salesorigins IN ('$in{'id_salesorigins'}') ";
		}
							 	
					 	
		if($in{'groupby'} eq 'ptype'){
			$report_name = &trans_txt('reports_order_type');	
			$query_tot  = "SELECT COUNT(*),SUM(OrderNet) FROM sl_customers,sl_orders $query";
			$query_list = "SELECT Ptype,COUNT(*) AS nums,SUM(OrderNet) AS amounts FROM  sl_customers,sl_orders $query GROUP BY Ptype $sb ";
		}elsif($in{'groupby'} eq 'dnis_usa'){
			$report_name = &trans_txt('rep_orders_p_dids_usa');
			$query_tot  = "SELECT COUNT(*),SUM(OrderNet) FROM sl_customers,sl_orders $query";
			$query_list = "SELECT DIDS7,COUNT(*) AS nums,SUM(OrderNet) AS amounts FROM  sl_customers,sl_orders $query GROUP BY DIDS7 $sb ";
		}elsif($in{'groupby'} eq 'dnis'){
			$report_name = &trans_txt('rep_orders_p_dids_mex');
			$query_tot  = "SELECT COUNT(*),SUM(OrderNet) FROM sl_customers,sl_orders $query";
			$query_list = "SELECT DNIS,COUNT(*) AS nums,SUM(OrderNet) AS amounts FROM  sl_customers,sl_orders $query GROUP BY DNIS $sb ";
		}elsif ($in{'groupby'} eq 'day-util'){
			$report_name = &trans_txt('rep_orders_cust_daily_sales');	
			$query_tot = $query;
			$runcmd = 'results_orders_dayut';
		}elsif($in{'groupby'} eq 'month'){
			$report_name = &trans_txt('month');
			$query_tot  = "SELECT COUNT(*),SUM(OrderNet) FROM sl_customers,sl_orders $query";
			$query_list = "SELECT CONCAT(MONTH(sl_orders.Date),'-',YEAR(sl_orders.Date)),COUNT(*) AS nums,SUM(OrderNet) AS amounts FROM  sl_customers,sl_orders $query GROUP BY CONCAT(MONTH(sl_orders.Date),'-',YEAR(sl_orders.Date)) $sb ";
		}elsif($in{'groupby'} eq 'halfhour'){
			$report_name = &trans_txt('reports_half_hour');
			$usr{'pref_maxh'} = 30;
			$query_tot  = "SELECT COUNT(*),SUM(OrderNet) FROM  sl_customers,sl_orders $query";
			$query_list = "SELECT IF( MINUTE( sl_orders.Time ) <=30, CONCAT( HOUR( sl_orders.Time ) , ':01 to ', HOUR( sl_orders.Time ) , ':30' ) , CONCAT( HOUR( sl_orders.Time ) , ':31 to ', HOUR( sl_orders.Time ) +1, ':00' ) ), COUNT( * ) AS hits, SUM(OrderNet) AS amounts FROM  sl_customers,sl_orders $query GROUP BY HOUR( sl_orders.Time ) , MINUTE( sl_orders.Time ) <=30, MINUTE( sl_orders.Time ) >30 ORDER BY HOUR( sl_orders.Time ) ";
		}elsif($in{'groupby'} eq 'hour'){
			$report_name = &trans_txt('hour');
			$usr{'pref_maxh'} = 30;
			$query_tot  = "SELECT COUNT(*),SUM(OrderNet) FROM  sl_customers,sl_orders $query";
			$query_list = "SELECT HOUR(sl_orders.Time),COUNT(*) AS nums,SUM(OrderNet) AS amounts FROM  sl_customers,sl_orders $query GROUP BY HOUR(sl_orders.Time) $sb ";
		}elsif($in{'groupby'} eq 'state'){
			$report_name = &trans_txt('state');
			$query_tot  = "SELECT COUNT(*),SUM(OrderNet) FROM  sl_customers,sl_orders $query";
			$query_list = "SELECT sl_orders.State,COUNT(*) AS nums,SUM(OrderNet) AS amounts FROM  sl_customers,sl_orders  $query GROUP BY State $sb ";
		#}elsif($in{'groupby'} eq 'sex'){
		#	$query_tot  = "SELECT COUNT(*),SUM(OrderNet) FROM  sl_customers,sl_orders $query";
		#	$query_list = "SELECT Sex,COUNT(*) AS nums,SUM(OrderNet) AS amounts FROM  sl_customers,sl_orders $query GROUP BY Sex $sb ";		
		}elsif($in{'groupby'} eq 'status'){
			$report_name = &trans_txt('status');
			$query_tot  = "SELECT COUNT(*),SUM(OrderNet) FROM  sl_customers,sl_orders $query";
			$query_list = "SELECT sl_orders.Status,COUNT(*)AS nums,SUM(OrderNet) AS amounts FROM  sl_customers,sl_orders $query GROUP BY sl_orders.Status $sb ";
		}elsif($in{'groupby'} eq 'id_admin_users'){
			$report_name = &trans_txt('reports_user_admin');
			$query_tot  = "SELECT COUNT(*),SUM(OrderNet) FROM  sl_customers,sl_orders $query";
			$query_list = "SELECT CONCAT(admin_users.ID_admin_users,' &nbsp; ',admin_users.FirstName,' &nbsp; ',admin_users.LastName),COUNT(*) AS nums,SUM(OrderNet) AS amounts FROM sl_customers,sl_orders $query GROUP BY admin_users.ID_admin_users $sb ";
		}else{
			$query_tot  = "SELECT COUNT(*),SUM(OrderNet) FROM sl_customers,sl_orders $query";
			$query_list = "SELECT sl_orders.Date,COUNT(*) AS nums,SUM(OrderNet) AS amounts FROM  sl_customers,sl_orders $query GROUP BY sl_orders.Date $sb ";	
		}
		foreach $key (keys %in){
			$in{'qs'} .= "$key=$in{$key}&" unless ($key eq 'cmd');
		}
		
		## build report table
	   	$tbl_info = $va{'report_tbl'};
			$va{'report_tbl'} = qq |
				<center>
					<table border="0" cellspacing="0" cellpadding="4" width="70%" class="formtable">
						<tr>
					    	<td class="menu_bar_title" colspan="2">|.&trans_txt('report_name').qq|: |.&trans_txt('reports_selected_fields').qq| </td>  
						</tr>
						<tr>
					    	<td class="smalltext">|.&trans_txt('reports_units').qq|</td>  
					    	<td class="smalltext">|.&trans_txt('reports_ordernet').qq| </td>  
						</tr>\n|;  
		$va{'report_tbl'} .= "$tbl_info</table></center>\n";	
		
		($va{'rep1'},$va{'rep2'},$va{'rep3'},$va{'rep4'},$va{'rep5'},$va{'rep6'},$va{'rep7'}) = ('off','off','off','off','on','off','off');
		&$runcmd($query_tot,$query_list);
		&auth_logging('report_view','');
		return;
	}
	
	print "Content-type: text/html\n\n";
	print &build_page('rep_orders_cust.html');
}




#####################################################
#######   CANCELED 
#####################################################
sub rep_orders_araging {
# --------------------------------------------------------
# Created :  Roberto Barcenas
# Last Update : 
# Locked by : 
# Description : Show A/R aging for a specfic range of dates
# Last Modified RB: 08/19/2010 : Added FP  not due.
# Last Modified EP: 07/11/12  10:45:54 -- Se agrega la funcion transtxt

	my ($sb,$query);	
	if ($in{'action'}){

		$tot_amount = 0;
		$tot_qty    = 0;
		$report_name = &trans_txt('rep_orders_araging_report_name');
		$units       = &trans_txt('rep_orders_pay_payments_amounts_taxes');

		## Filter by Date
		$date = &get_sql_date if !$in{'date'};
		$va{'report_tbl'} .= "<tr><td width='100' class='smalltext'>".&trans_txt('rep_orders_araging_as_off')." : </td><td class='smalltext'>$in{'date'}</td></tr>\n";

		## Filter by User
		if ($in{'user_type'}){
			$in{'user_type'} =~ s/\|/','/g;
			$va{'report_tbl'} .= "<tr><td width='100' class='smalltext'>".&trans_txt('reports_by_user')." : </td><td class='smalltext'>$in{'user_type'}</td></tr>\n";
			$query .= " AND 0 < (SELECT IF(user_type IN ('$in{'user_type'}'),1,0) FROM admin_users WHERE ID_admin_users = sl_orders.ID_admin_users) ";
		}$in{'user_type'} =~ s/','/\|/g;

		## Filter by Status
		if ($in{'status'} !~ /-1/){
			$in{'status'} =~ s/\|/','/g;
			$va{'report_tbl'} .= "<tr><td width='100' class='smalltext'>".&trans_txt('status')." : </td><td class='smalltext'>$in{'status'}</td></tr>\n";						
			$query .= " AND sl_orders.Status IN ('$in{'status'}') ";
		}elsif ($in{'excludevoid'}){
			$va{'report_tbl'} .= "<tr><td width='100' class='smalltext'>".&trans_txt('status')." : </td><td class='smalltext'>".&trans_txt('void_system_error_excluded')."</td></tr>\n";			
			$query .= " AND sl_orders.Status NOT IN ('Void','System Error') ";
		}


		$query = " WHERE  sl_orders.Date <= '$in{'date'}' AND
				  sl_orders_payments.Status NOT IN ('Cancelled','Order Cancelled','Void') 
				  and Amount>0 
				  $query  
				  AND sl_orders.Date IS NOT NULL 
				  AND sl_orders.Date != '' 
				  AND sl_orders.Date !='0000-00-00'  
				  AND Type='Credit-Card'";


		if ($in{'export'}){
			@cols = ('ID Order','Order Date','Payment Date','Days Due','Captured Date','Amount','Status');
			print "Content-type: application/vnd.ms-excel\n";
			print "Content-disposition: attachment; filename=ar_aging_analisis.csv\n\n";
			print '"'.join('","', @cols)."\"\n";

			my ($sth) = &Do_SQL("SELECT sl_orders.ID_orders,sl_orders.Date, Paymentdate,DATEDIFF('$in{'date'}',Paymentdate),CapDate,Amount ,sl_orders.Status FROM sl_orders inner join sl_orders_payments on (sl_orders.ID_orders=sl_orders_payments.ID_orders) $query  AND DATEDIFF('$in{'date'}',Paymentdate) >= 0 AND (Captured='No' OR CapDate > '$in{'date'}') ORDER BY DATEDIFF('$in{'date'}',Paymentdate) DESC;");
			while (@ary = $sth->fetchrow_array){
				print '"'.join('","', @ary)."\"\n";
			}
			return;
		}

		### AR DUE
		## FP Due (90 days)
		my ($sth) = &Do_SQL("SELECT SUM(Amount) FROM sl_orders inner join sl_orders_payments on (sl_orders.ID_orders=sl_orders_payments.ID_orders) $query  AND DATEDIFF('$in{'date'}',Paymentdate) > 90  AND (Captured='No' OR CapDate > '$in{'date'}')");
		my ($amount) = $sth->fetchrow;
		my ($sth) = &Do_SQL("SELECT COUNT(DISTINCT(sl_orders.ID_orders)) FROM sl_orders inner join sl_orders_payments on (sl_orders.ID_orders=sl_orders_payments.ID_orders) $query  AND DATEDIFF('$in{'date'}',Paymentdate) > 90 AND (Captured='No' OR CapDate > '$in{'date'}')");
		my ($qty) = $sth->fetchrow;
		$tot_amount += $amount;
		$tot_qty    += $qty;
		$report{'due_90'}[0] = $qty;
		$report{'due_90'}[1] = $amount;
		
		## FP Due (60-90 days)
		my ($sth) = &Do_SQL("SELECT SUM(Amount) FROM sl_orders inner join sl_orders_payments on (sl_orders.ID_orders=sl_orders_payments.ID_orders) $query  AND DATEDIFF('$in{'date'}',Paymentdate) BETWEEN 61 AND 90 AND (Captured='No' OR CapDate > '$in{'date'}')");
		my ($amount) = $sth->fetchrow;
		my ($sth) = &Do_SQL("SELECT COUNT(DISTINCT(sl_orders.ID_orders)) FROM sl_orders inner join sl_orders_payments on (sl_orders.ID_orders=sl_orders_payments.ID_orders) $query  AND DATEDIFF('$in{'date'}',Paymentdate) BETWEEN 61 AND 90 AND (Captured='No' OR CapDate > '$in{'date'}')");
		my ($qty) = $sth->fetchrow;
		$tot_amount += $amount;
		$tot_qty    += $qty;
		$report{'due_60'}[0] = $qty;
		$report{'due_60'}[1] = $amount;

		## FP Due (31-60 days)
		my ($sth) = &Do_SQL("SELECT SUM(Amount) FROM sl_orders inner join sl_orders_payments on (sl_orders.ID_orders=sl_orders_payments.ID_orders) $query  AND DATEDIFF('$in{'date'}',Paymentdate) BETWEEN 31 AND 60 AND (Captured='No' OR CapDate > '$in{'date'}')");
		my ($amount) = $sth->fetchrow;
		my ($sth) = &Do_SQL("SELECT COUNT(DISTINCT(sl_orders.ID_orders)) FROM sl_orders inner join sl_orders_payments on (sl_orders.ID_orders=sl_orders_payments.ID_orders) $query  AND DATEDIFF('$in{'date'}',Paymentdate) BETWEEN 31 AND 60 AND (Captured='No' OR CapDate > '$in{'date'}')");
		my ($qty) = $sth->fetchrow;
		$tot_amount += $amount;
		$tot_qty    += $qty;
		$report{'due_30'}[0] = $qty;
		$report{'due_30'}[1] = $amount;
		

		## FP Due (1-30 days)
		my ($sth) = &Do_SQL("SELECT SUM(Amount) FROM sl_orders inner join sl_orders_payments on (sl_orders.ID_orders=sl_orders_payments.ID_orders) $query  AND DATEDIFF('$in{'date'}',Paymentdate) BETWEEN 1 AND 30 AND (Captured='No' OR CapDate > '$in{'date'}')");
		my ($amount) = $sth->fetchrow;
		my ($sth) = &Do_SQL("SELECT COUNT(DISTINCT(sl_orders.ID_orders)) FROM sl_orders inner join sl_orders_payments on (sl_orders.ID_orders=sl_orders_payments.ID_orders) $query  AND DATEDIFF('$in{'date'}',Paymentdate) BETWEEN 1 AND 30 AND (Captured='No' OR CapDate > '$in{'date'}')");
		my ($qty) = $sth->fetchrow;
		$tot_amount += $amount;
		$tot_qty    += $qty;
		$report{'due'}[0] = $qty;
		$report{'due'}[1] = $amount;

		## FP Due (Today)
		my ($sth) = &Do_SQL("SELECT SUM(Amount) FROM sl_orders inner join sl_orders_payments on (sl_orders.ID_orders=sl_orders_payments.ID_orders) $query AND Paymentdate='$in{'date'}' AND (Captured='No' OR CapDate > '$in{'date'}')");
		my ($amount) = $sth->fetchrow;
		my ($sth) = &Do_SQL("SELECT COUNT(DISTINCT(sl_orders.ID_orders)) FROM sl_orders inner join sl_orders_payments on (sl_orders.ID_orders=sl_orders_payments.ID_orders) $query  AND Paymentdate='$in{'date'}' AND (Captured='No' OR CapDate > '$in{'date'}')");
		my ($qty) = $sth->fetchrow;
		$tot_amount += $amount;
		$tot_qty    += $qty;
		$report{'due_now'}[0] = $qty;
		$report{'due_now'}[1] = $amount;

		### FP ALIVE

		## FP (90 days)
		my ($sth) = &Do_SQL("SELECT SUM(Amount) FROM sl_orders inner join sl_orders_payments on (sl_orders.ID_orders=sl_orders_payments.ID_orders) $query  AND DATEDIFF(Paymentdate , '$in{'date'}') > 90;");
		my ($amount) = $sth->fetchrow;
		my ($sth) = &Do_SQL("SELECT COUNT(DISTINCT(sl_orders.ID_orders)) FROM sl_orders inner join sl_orders_payments on (sl_orders.ID_orders=sl_orders_payments.ID_orders) $query  AND DATEDIFF(Paymentdate , '$in{'date'}') > 90;");
		my ($qty) = $sth->fetchrow;
		$tot_amount += $amount;
		$tot_qty    += $qty;
		$report{'fp_90'}[0] = $qty;
		$report{'fp_90'}[1] = $amount;
		
		## FP (60-90 days)
		my ($sth) = &Do_SQL("SELECT SUM(Amount) FROM sl_orders inner join sl_orders_payments on (sl_orders.ID_orders=sl_orders_payments.ID_orders) $query  AND DATEDIFF(Paymentdate , '$in{'date'}') BETWEEN 61 AND 90;");
		my ($amount) = $sth->fetchrow;
		my ($sth) = &Do_SQL("SELECT COUNT(DISTINCT(sl_orders.ID_orders)) FROM sl_orders inner join sl_orders_payments on (sl_orders.ID_orders=sl_orders_payments.ID_orders) $query  AND DATEDIFF(Paymentdate , '$in{'date'}') BETWEEN 61 AND 90;");
		my ($qty) = $sth->fetchrow;
		$tot_amount += $amount;
		$tot_qty    += $qty;
		$report{'fp_60'}[0] = $qty;
		$report{'fp_60'}[1] = $amount;

		## FP (31-60 days)
		my ($sth) = &Do_SQL("SELECT SUM(Amount) FROM sl_orders inner join sl_orders_payments on (sl_orders.ID_orders=sl_orders_payments.ID_orders) $query  AND DATEDIFF(Paymentdate , '$in{'date'}') BETWEEN 31 AND 60;");
		my ($amount) = $sth->fetchrow;
		my ($sth) = &Do_SQL("SELECT COUNT(DISTINCT(sl_orders.ID_orders)) FROM sl_orders inner join sl_orders_payments on (sl_orders.ID_orders=sl_orders_payments.ID_orders) $query  AND DATEDIFF(Paymentdate , '$in{'date'}') BETWEEN 31 AND 60;");
		my ($qty) = $sth->fetchrow;
		$tot_amount += $amount;
		$tot_qty    += $qty;
		$report{'fp_30'}[0] = $qty;
		$report{'fp_30'}[1] = $amount;
		

		## FP (1-30 days)
		my ($sth) = &Do_SQL("SELECT SUM(Amount) FROM sl_orders inner join sl_orders_payments on (sl_orders.ID_orders=sl_orders_payments.ID_orders) $query  AND DATEDIFF(Paymentdate , '$in{'date'}') BETWEEN 1 AND 30;");
		my ($amount) = $sth->fetchrow;
		my ($sth) = &Do_SQL("SELECT COUNT(DISTINCT(sl_orders.ID_orders)) FROM sl_orders inner join sl_orders_payments on (sl_orders.ID_orders=sl_orders_payments.ID_orders) $query  AND DATEDIFF(Paymentdate , '$in{'date'}') BETWEEN 1 AND 30;");
		my ($qty) = $sth->fetchrow;
		$tot_amount += $amount;
		$tot_qty    += $qty;
		$report{'fp'}[0] = $qty;
		$report{'fp'}[1] = $amount;



		if($tot_amount > 0 ){
			## FP Due (90 days)
			$va{'searchresults'} .= qq|	
				<tr onmouseover='m_over(this)' onmouseout='m_out(this)' bgcolor='$c[$d]'>
					<td valign="top" class='smalltext'>&nbsp;&nbsp;&nbsp; |.&trans_txt('rep_orders_araging_pd_91_more').qq|</td>
					<td align="right" valign="top" class='smalltext'><span class='help_on'>|.&format_number($report{'due_90'}[0]).qq|</span></td>
					<td nowrap class="help_on" valign="top" class='smalltext'>&nbsp; (|.&format_number($report{'due_90'}[0]/$tot_qty*100).qq|%)</td>
					<td align="right" valign="top" nowrap class='smalltext'>|.&format_price($report{'due_90'}[1]).qq|</td>
					<td nowrap class="help_on" valign="top" class='smalltext'>&nbsp;  (|.&format_number($report{'due_90'}[1]/$tot_amount*100).qq|%)</td>
				</tr>\n|;

			## FP Due (61-90 days)
			$va{'searchresults'} .= qq|	
				<tr onmouseover='m_over(this)' onmouseout='m_out(this)' bgcolor='$c[$d]'>
					<td valign="top" class='smalltext'>&nbsp;&nbsp;&nbsp; |.&trans_txt('rep_orders_araging_pd_61_90').qq|</td>
					<td align="right" valign="top" class='smalltext'><span class='help_on'>|.&format_number($report{'due_60'}[0]).qq|</span></td>
					<td nowrap class="help_on" valign="top" class='smalltext'>&nbsp; (|.&format_number($report{'due_60'}[0]/$tot_qty*100).qq|%)</td>
					<td align="right" valign="top" nowrap class='smalltext'>|.&format_price($report{'due_60'}[1]).qq|</td>
					<td nowrap class="help_on" valign="top" class='smalltext'>&nbsp;  (|.&format_number($report{'due_60'}[1]/$tot_amount*100).qq|%)</td>
				</tr>\n|;	

			## FP Due (31-60 days)
			$va{'searchresults'} .= qq|	
				<tr onmouseover='m_over(this)' onmouseout='m_out(this)' bgcolor='$c[$d]'>
					<td valign="top" class='smalltext'>&nbsp;&nbsp;&nbsp; |.&trans_txt('rep_orders_araging_pd_31_60').qq|</td>
					<td align="right" valign="top" class='smalltext'><span class='help_on'>|.&format_number($report{'due_30'}[0]).qq|</span></td>
					<td nowrap class="help_on" valign="top" class='smalltext'>&nbsp; (|.&format_number($report{'due_30'}[0]/$tot_qty*100).qq|%)</td>
					<td align="right" valign="top" nowrap class='smalltext'>|.&format_price($report{'due_30'}[1]).qq|</td>
					<td nowrap class="help_on" valign="top" class='smalltext'>&nbsp;  (|.&format_number($report{'due_30'}[1]/$tot_amount*100).qq|%)</td>
				</tr>\n|;	
	
			## FP Due (1-30 days)
			$va{'searchresults'} .= qq|	
				<tr onmouseover='m_over(this)' onmouseout='m_out(this)' bgcolor='$c[$d]'>
					<td valign="top" class='smalltext'>&nbsp;&nbsp;&nbsp; |.&trans_txt('rep_orders_araging_pd_1_30').qq|</td>
					<td align="right" valign="top" class='smalltext'><span class='help_on'>|.&format_number($report{'due'}[0]).qq|</span></td>
					<td nowrap class="help_on" valign="top" class='smalltext'>&nbsp; (|.&format_number($report{'due'}[0]/$tot_qty*100).qq|%)</td>
					<td align="right" valign="top" nowrap class='smalltext'>|.&format_price($report{'due'}[1]).qq|</td>
					<td nowrap class="help_on" valign="top" class='smalltext'>&nbsp;  (|.&format_number($report{'due'}[1]/$tot_amount*100).qq|%)</td>
				</tr>\n|;
	
			$va{'searchresults'} .= qq|
				<tr onmouseover='m_over(this)' onmouseout='m_out(this)' bgcolor='$c[$d]'>
					<td colspan="5">&nbsp;</td>
				</tr>\n|;	
	
			## FP Due (Today)
			$va{'searchresults'} .= qq|	
				<tr onmouseover='m_over(this)' onmouseout='m_out(this)' bgcolor='$c[$d]'>
					<td valign="top" class='smalltext'>&nbsp;&nbsp;&nbsp; |.&trans_txt('rep_orders_araging_fp_due').qq| ($in{'date'})</td>
					<td align="right" valign="top" class='smalltext'><span class='help_on'>|.&format_number($report{'due_now'}[0]).qq|</span></td>
					<td nowrap class="help_on" valign="top" class='smalltext'>&nbsp; (|.&format_number($report{'due_now'}[0]/$tot_qty*100).qq|%)</td>
					<td align="right" valign="top" nowrap class='smalltext'>|.&format_price($report{'due_now'}[1]).qq|</td>
					<td nowrap class="help_on" valign="top" class='smalltext'>&nbsp;  (|.&format_number($report{'due_now'}[1]/$tot_amount*100).qq|%)</td>
				</tr>\n|;				
		
			$va{'searchresults'} .= qq|
				<tr onmouseover='m_over(this)' onmouseout='m_out(this)' bgcolor='$c[$d]'>
					<td colspan="5">&nbsp;</td>
				</tr>\n|;	

			## FP (1-30 days)
			$va{'searchresults'} .= qq|	
				<tr onmouseover='m_over(this)' onmouseout='m_out(this)' bgcolor='$c[$d]'>
					<td valign="top" class='smalltext'>&nbsp;&nbsp;&nbsp; |.&trans_txt('rep_orders_araging_fp_1_30').qq|</td>
					<td align="right" valign="top" class='smalltext'><span class='help_on'>|.&format_number($report{'fp'}[0]).qq|</span></td>
					<td nowrap class="help_on" valign="top" class='smalltext'>&nbsp; (|.&format_number($report{'fp'}[0]/$tot_qty*100).qq|%)</td>
					<td align="right" valign="top" nowrap class='smalltext'>|.&format_price($report{'fp'}[1]).qq|</td>
					<td nowrap class="help_on" valign="top" class='smalltext'>&nbsp;  (|.&format_number($report{'fp'}[1]/$tot_amount*100).qq|%)</td>
				</tr>\n|;

			## FP (31-60 days)
			$va{'searchresults'} .= qq|	
				<tr onmouseover='m_over(this)' onmouseout='m_out(this)' bgcolor='$c[$d]'>
					<td valign="top" class='smalltext'>&nbsp;&nbsp;&nbsp; |.&trans_txt('rep_orders_araging_fp_31_60').qq|</td>
					<td align="right" valign="top" class='smalltext'><span class='help_on'>|.&format_number($report{'fp_30'}[0]).qq|</span></td>
					<td nowrap class="help_on" valign="top" class='smalltext'>&nbsp; (|.&format_number($report{'fp_30'}[0]/$tot_qty*100).qq|%)</td>
					<td align="right" valign="top" nowrap class='smalltext'>|.&format_price($report{'fp_30'}[1]).qq|</td>
					<td nowrap class="help_on" valign="top" class='smalltext'>&nbsp;  (|.&format_number($report{'fp_30'}[1]/$tot_amount*100).qq|%)</td>
				</tr>\n|;

			## FP (61-90 days)
			$va{'searchresults'} .= qq|	
				<tr onmouseover='m_over(this)' onmouseout='m_out(this)' bgcolor='$c[$d]'>
					<td valign="top" class='smalltext'>&nbsp;&nbsp;&nbsp; |.&trans_txt('rep_orders_araging_fp_61_90').qq|</td>
					<td align="right" valign="top" class='smalltext'><span class='help_on'>|.&format_number($report{'fp_60'}[0]).qq|</span></td>
					<td nowrap class="help_on" valign="top" class='smalltext'>&nbsp; (|.&format_number($report{'fp_60'}[0]/$tot_qty*100).qq|%)</td>
					<td align="right" valign="top" nowrap class='smalltext'>|.&format_price($report{'fp_60'}[1]).qq|</td>
					<td nowrap class="help_on" valign="top" class='smalltext'>&nbsp;  (|.&format_number($report{'fp_60'}[1]/$tot_amount*100).qq|%)</td>
				</tr>\n|;

			## FP (90 > days)
			$va{'searchresults'} .= qq|	
				<tr onmouseover='m_over(this)' onmouseout='m_out(this)' bgcolor='$c[$d]'>
					<td valign="top" class='smalltext'>&nbsp;&nbsp;&nbsp; |.&trans_txt('rep_orders_araging_fp_91_more').qq|</td>
					<td align="right" valign="top" class='smalltext'><span class='help_on'>|.&format_number($report{'fp_90'}[0]).qq|</span></td>
					<td nowrap class="help_on" valign="top" class='smalltext'>&nbsp; (|.&format_number($report{'fp_90'}[0]/$tot_qty*100).qq|%)</td>
					<td align="right" valign="top" nowrap class='smalltext'>|.&format_price($report{'fp_90'}[1]).qq|</td>
					<td nowrap class="help_on" valign="top" class='smalltext'>&nbsp;  (|.&format_number($report{'fp_90'}[1]/$tot_amount*100).qq|%)</td>
				</tr>\n|;
		
		}else{
			##No Data Found
			$va{'searchresults'} .= qq|
				<tr onmouseover='m_over(this)' onmouseout='m_out(this)' bgcolor='$c[$d]'>
					<td valign="top" class='smalltext' colspan='5' align='center'>|.&trans_txt('notmatch').qq|</td>
				</tr>\n|;
		}
		
		$va{'tot_cant'} = &format_number($tot_qty);
		$va{'tot_amount'} = &format_price($tot_amount);
		$va{'matches'} = $va{'tot_cant'};
		$va{'pageslist'} = 1;

		### Report Headet
		$va{'report_tbl'} = qq |
					<center>
						<table border="0" cellspacing="0" cellpadding="4" width="70%" class="formtable">
							<tr>
						   		 <td class="menu_bar_title" colspan="2">|.&trans_txt('report_name').qq| : $report_name</td>  
							</tr> 
							<tr>
						    	<td class="smalltext">|.&trans_txt('reports_units').qq|</td>  
						    	<td class="smalltext">$units</td>  
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
			print &build_page('rep_orders_araginglist_print.html');
		}else{
			($nul,$qs) = &pages_list($in{'nh'},$script_url,1,1);
			$va{'extabtns'} = qq|<a href="javascript:prnwin('/cgi-bin/mod/[ur_application]/admin?print=1&$qs')"><img src='[va_imgurl]/[ur_pref_style]/b_print.png' title='Print' alt='' border='0'></a>
					  &nbsp;&nbsp;
					  <a href="javascript:prnwin('/cgi-bin/mod/[ur_application]/admin?export=1&$qs')"><img src='[va_imgurl]/[ur_pref_style]/b_xls.gif' title='Export' alt='' border='0'></a>|;
			print "Content-type: text/html\n\n";
			print &build_page('results_orders_araging.html');
		}
	}else{
		print "Content-type: text/html\n\n";
		print &build_page('rep_orders_araging.html');
	}
}

sub rep_orders_good_bad_l{
# --------------------------------------------------------
# Forms Involved: 
# Created on: 03/23/09 16:06:02
# Author: MCC C. Gabriel Varela S.
# Description :   
# Parameters :
# Last Modified EP: 07/11/12  11:00:54 -- Se agrega la funcion transtxt


	my ($sb,$query,$bandinnerpreorders,$select_date,$cadinner,$gb,$sb);	
	$bandinnerpreorders=1;
	if ($in{'action'}){
		## Date Type
		if ($in{'dtype'} eq 'sl_orders.Date'){
			$bandinnerpreorders=1;
			$select_date="sl_orders.Date as day,date_format(sl_orders.Date,'%b%y')as Month";
			$va{'report_tbl'} .= "<tr><td width='100' class='smalltext'>".&trans_txt('date')." : </td><td class='smalltext'>".&trans_txt('reports_order_type')."</td></tr>\n";
		}elsif ($in{'dtype'} eq 'sl_orders_payments.Paymentdate'){
			$select_date="sl_orders_payments.Paymentdate as day,date_format(sl_orders_payments.Paymentdate,'%b%y')as Month";
			$va{'report_tbl'} .= "<tr><td width='100' class='smalltext'>".&trans_txt('date')." : </td><td class='smalltext'>".&trans_txt('rep_orders_pay_date')."</td></tr>\n";
		}else{
			$select_date="sl_orders_payments.CapDate as day,date_format(sl_orders_payments.CapDate,'%b%y')as Month";
			$in{'dtype'} = 'sl_orders_payments.CapDate';
			$va{'report_tbl'} .= "<tr><td width='100' class='smalltext'>".&trans_txt('date')." : </td><td class='smalltext'>".&trans_txt('reports_captured_date')."</td></tr>\n";
		}

		if ($in{'sortby'}){
			$sb = "ORDER BY $in{'sortby'} $in{'sortorder'}";
			my $cadsort=$in{'sortby'};
			$cadsort=~s/sl_orders_payments\.ID_orders/NO Orders/g;
			$va{'report_tbl'} .= "<tr><td width='100' class='smalltext'>".&trans_txt('reports_sort_by')." : </td><td class='smalltext'>$cadsort $in{'sortorder'}</td></tr>\n";
		}
		
	
		## Filter by User
		if ($in{'user_type'}){
			$in{'user_type'} =~ s/\|/','/g;
			$va{'report_tbl'} .= "<tr><td width='100' class='smalltext'>".&trans_txt('reports_by_user')."</td><td class='smalltext'>$in{'user_type'}</td></tr>\n";
			$query .= " AND 0 < (SELECT IF(user_type IN ('$in{'user_type'}'),1,0) FROM admin_users WHERE ID_admin_users = sl_orders_payments.ID_admin_users) ";
		}$in{'user_type'} =~ s/','/\|/g;
				
		## Filter by Date
		if ($in{'from_date'}){
			$va{'report_tbl'} .= "<tr><td width='100' class='smalltext'>".&trans_txt('from_date')." : </td><td class='smalltext'>$in{'from_date'}</td></tr>\n";
			$query .= " AND $in{'dtype'}>='$in{'from_date'}' ";
		}
		if ($in{'to_date'}){
			$va{'report_tbl'} .= "<tr><td width='100' class='smalltext'>".&trans_txt('to_date')." : </td><td class='smalltext'>$in{'to_date'}</td></tr>\n";
			$query .= " AND $in{'dtype'}<='$in{'to_date'}' ";
		}		
		
		### Busqueda por rango de tiempo
		if($in{'from_time'} or $in{'to_time'}){
			$in{'from_time'} 	= "00:00:00"	if !$in{'from_time'};
			$in{'to_time'} 		= "23:59:59"	if !$in{'to_time'};
			$query .= " AND sl_orders.Time BETWEEN '$in{'from_time'}' AND '$in{'to_time'}' ";
		}
		
		## Filter by Status
		if ($in{'status'} !~ /-1/){
			$in{'status'} =~ s/\|/','/g;
			$va{'report_tbl'} .= "<tr><td width='100' class='smalltext'>".&trans_txt('status')." : </td><td class='smalltext'>$in{'status'}</td></tr>\n";						
			$bandinnerpreorders=1;
			$query .= " AND sl_orders.Status IN ('$in{'status'}') ";
		}elsif ($in{'excludevoid'}){
			$va{'report_tbl'} .= "<tr><td width='100' class='smalltext'>".&trans_txt('status')." : </td><td class='smalltext'>".&trans_txt('void_system_error_excluded')."</td></tr>\n";			
			$bandinnerpreorders=1;
			$query .= " AND sl_orders.Status NOT IN ('Void','System Error') ";
		}
		
		## Filter by DID
		if ($in{'dids'} !~ /-1/){
			my $dids=$in{'dids'};
			$dids =~ s/\|/','/g;
			
			my @ary = split(/\|/,$in{'dids'});
			for (0..$#ary){
				$dname .= &load_name('sl_mediadids','didmx',$ary[$_],'product').',';
			}
			chop($dname);
			$bandinnerpreorders=1;
			$va{'report_tbl'} .= "<tr><td width='100' class='smalltext'>".&trans_txt('report_dids')." : </td><td class='smalltext'>$dname</td></tr>\n";			
			$query .= " AND sl_orders.DNIS IN ('$dids') ";#DNIS-NUMBER
		}
		

		## Filter by Payment Exception
		if ($in{'statuspay'} !~ /-1/){
			$in{'statuspay'} =~ s/\|/','/g;
			$bandinnerpreorders=1;
			$va{'report_tbl'} .= "<tr><td width='100' class='smalltext'>".&trans_txt('rep_orders_p_pexception')." : </td><td class='smalltext'>$in{'statuspay'}</td></tr>\n";
			$query .= " AND sl_orders.StatusPay IN ('$in{'statuspay'}') ";
		}
	
		## Filter by pricelevels
		if ($in{'id_pricelevels'} !~ /-1/){
			
			++$rows;
			$bandinnerpreorders=1;
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
		
		## Filter by Payment Type
		$va{'report_tbl'} .= "<tr><td width='100' class='smalltext'>".&trans_txt('report_payment_type')." : </td><td class='smalltext'>$in{'paytype'}</td></tr>\n";
		#($in{'paytype'} eq 'all') and ($query .= " AND sl_preorders_payments.Type IN ('Layaway')");
		#Por tipo de Layaway
		($in{'paytype'} eq 'LayawayMO') and ($query .= " AND Pmtfield3='' ");
		($in{'paytype'} eq 'LayawayCC') and ($query .= " AND Pmtfield3!='' ");
			

		## Filter by State
		if ($in{'state'}){
			$bandinnerpreorders=1;
			$va{'report_tbl'} .= "<tr><td width='100' class='smalltext'>".&trans_txt('state')." : </td><td class='smalltext'>$in{'state'}</td></tr>\n";									
			$query .= " AND sl_orders.State='$in{'state'}' ";
		}
		
		## Group records by
		$gb=$in{'groupby'};
		my $groupcad=$in{'groupby'};
		$groupcad=~s/sl_orders_payments\.id_orders/Order ID/g;
		$groupcad=~s/sl_orders\.status/Order Status/g;
		$va{'report_tbl'} .= "<tr><td width='100' class='smalltext'>".&trans_txt('reports_group_by')." : </td><td class='smalltext'>$groupcad</td></tr>\n";
		
		##TODO: porque tanto elsif sin nada?
		if ($in{'groupby'} eq 'day'){
		}elsif($in{'groupby'} eq 'month'){
		}elsif($in{'groupby'} eq 'state'){
			$bandinnerpreorders=1;
		}elsif($in{'groupby'} eq 'sl_orders.status'){
			$bandinnerpreorders=1;
		}elsif($in{'groupby'} eq 'paytype'){
		}elsif($in{'groupby'} eq 'fp'){
		}
		$select_date.=",sl_orders.State";
		$select_date.=",sl_orders.Status";
		foreach $key (keys %in){
			$in{'qs'} .= "$key=$in{$key}&" unless ($key eq 'cmd');
		}
				
		### Report Headet
		$va{'report_tbl'} = qq |
					<center>
						<table border="0" cellspacing="0" cellpadding="4" width="70%" class="formtable">
							<tr>
						   		 <td class="menu_bar_title" colspan="2">|.&trans_txt('reports_created_by').qq|: |.&trans_txt('rep_orders_good_bad_name').qq|</td>  
							</tr> 
					$va{'report_tbl'}
						<tr>
					   		 <td class="smalltext" colspan="2"> |.&trans_txt('report_name').qq| : ($usr{'id_admin_users'}) $usr{'firstname'} $usr{'lastname'} \@ |.&get_sql_date ." &nbsp;" . &get_time() .qq|</td>  
						</tr> 
					</table></center>\n\n\n\n\n <!--\n $query_tot \n\n $query_list\n\n-->|; 
		
		$va{'matches'} = 1;
		$va{'pageslist'} = 1;
		
		if($bandinnerpreorders){
			$cadinner=" inner join sl_orders on (sl_orders_payments.ID_orders=sl_orders.ID_orders and Ptype!='Credit-Card') "
		}
		
		my $querytoapp="SELECT 1 as groupfl,sl_orders_payments.ID_orders,
						sum(if((Captured='No') and PaymentDate < Curdate(),1,0))as Vencidos,
						sum(if((Captured='No') and PaymentDate < Curdate(),Amount,0))as SVencidos,
						sum(if(Captured='Yes',1,0))as Pagados,
						sum(if(Captured='Yes',Amount,0))as SPagados,
						sum(if((Captured='No') and PaymentDate >= Curdate(),1,0))as Por_pagar,
						sum(if((Captured='No') and PaymentDate >= Curdate(),Amount,0))as SPor_pagar,
						count(sl_orders_payments.ID_orders) as TotalPayments,
						sum(Amount) as STotalPayments,
						if(sum(if((Captured='No') and PaymentDate < Curdate(),1,0))=0,'Good','Bad')as Good,
						$select_date,
						if(Type='Layaway' and PmtField3='','LayawayMO','LayawayCC')as Paytype
						FROM `sl_orders_payments` 
						$cadinner
						WHERE Type='Layaway' and sl_orders_payments.ID_orders!=0 $query
						group by sl_orders_payments.ID_orders
						$sb";

		$sth=&Do_SQL("Select Good,
						sum(Vencidos)as Vencidos,
						sum(SVencidos)as SVencidos,
						sum(Pagados)as Pagados,
						sum(SPagados)as SPagados,
						sum(Por_pagar)as Por_pagar,
						sum(SPor_pagar)as SPor_pagar,
						sum(TotalPayments)as TotalPayments,
						sum(STotalPayments)as STotalPayments,
						day,
						Month,
						Paytype,State,Status,
						count(groupfl)
						from
						($querytoapp)as tmp group by Good order by Good");
		$va{'matches'}=$sth->rows;
		($va{'paytypebad'},$va{'tvencidosbad'},$va{'tsvencidosbad'},$va{'tpagadosbad'},$va{'tspagadosbad'},$va{'tpor_pagarbad'},$va{'tspor_pagarbad'},$va{'ttotalpaymentsbad'},$va{'tstotalpaymentsbad'},$va{'matchesbad'}) = $sth->fetchrow;
		($va{'paytypegood'},$va{'tvencidosgood'},$va{'tsvencidosgood'},$va{'tpagadosgood'},$va{'tspagadosgood'},$va{'tpor_pagargood'},$va{'tspor_pagargood'},$va{'ttotalpaymentsgood'},$va{'tstotalpaymentsgood'},$va{'matchesgood'}) = $sth->fetchrow;

		$sth=&Do_SQL("Select Good,
						sum(Vencidos)as Vencidos,
						sum(SVencidos)as SVencidos,
						sum(Pagados)as Pagados,
						sum(SPagados)as SPagados,
						sum(Por_pagar)as Por_pagar,
						sum(SPor_pagar)as SPor_pagar,
						sum(TotalPayments)as TotalPayments,
						sum(STotalPayments)as STotalPayments,
						day,
						Month,
						Paytype,State,Status,
						count(groupfl)
						from
						($querytoapp)as tmp group by $gb");
		$va{'matches'}=$sth->rows;
		
		$va{'tsvencidosbad'}=&format_price($va{'tsvencidosbad'});
		$va{'tspagadosbad'}=&format_price($va{'tspagadosbad'});
		$va{'tspor_pagarbad'}=&format_price($va{'tspor_pagarbad'});
		$va{'tstotalpaymentsbad'}=&format_price($va{'tstotalpaymentsbad'});
		
		$va{'tsvencidosgood'}=&format_price($va{'tsvencidosgood'});
		$va{'tspagadosgood'}=&format_price($va{'tspagadosgood'});
		$va{'tspor_pagargood'}=&format_price($va{'tspor_pagargood'});
		$va{'tstotalpaymentsgood'}=&format_price($va{'tstotalpaymentsgood'});
		
		my $caddate=$in{'dtype'};
		$caddate=~s/sl_orders\.Date/Date/g;
		
		##TODO: Estos Headers deberan estar en el template
		$va{'headersresult'} .= qq|<tr>|;
		$va{'headersresult'} .= qq|<td class="menu_bar_title">|.&trans_txt('reports_id_orders').qq|</td>| if($in{'groupby'}=~/id_orders/);
		$va{'headersresult'} .= qq|<td class="menu_bar_title">$caddate</td>| if($in{'groupby'}=~/day/);
		$va{'headersresult'} .= qq|<td class="menu_bar_title">|.&trans_txt('month').qq| </td>| if($in{'groupby'}=~/month/);
		$va{'headersresult'} .= qq|<td class="menu_bar_title">|.&trans_txt('state').qq|</td>| if($in{'groupby'}=~/state/);
		$va{'headersresult'} .= qq|<td class="menu_bar_title">|.&trans_txt('rep_orders_p_order_status').qq|</td>| if($in{'groupby'}=~/status/);
		$va{'headersresult'} .= qq|<td class="menu_bar_title">|.&trans_txt('report_payment_type').qq|</td>| if($in{'groupby'}=~/paytype/);
		$va{'headersresult'} .= qq|<td class="menu_bar_title">|.&trans_txt('report_payment_due').qq|</td>| if(1);#$in{'groupby'}=~/id_preorders|day/);
		$va{'headersresult'} .= qq|<td class="menu_bar_title">|.&trans_txt('report_payment_paid').qq|</td>| if(1);#$in{'groupby'}=~/id_preorders|day/);
	    $va{'headersresult'} .= qq|<td class="menu_bar_title">|.&trans_txt('report_payment_payable').qq|</td>| if(1);#$in{'groupby'}=~/id_preorders|day/);
	    $va{'headersresult'} .= qq|<td class="menu_bar_title">|.&trans_txt('report_payment_total').qq|</td>| if(1);#$in{'groupby'}=~/id_preorders|day/);
	    #$va{'headersresult'} .= qq|<td class="menu_bar_title">Good/Bad</td>|;
		$va{'headersresult'} .= qq|</tr>\n|;
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
			
			my $sth=&Do_SQL("Select groupfl,ID_orders,Good,
							sum(Vencidos)as Vencidos,
							sum(SVencidos)as SVencidos,
							sum(Pagados)as Pagados,
							sum(SPagados)as SPagados,
							sum(Por_pagar)as Por_pagar,
							sum(SPor_pagar)as SPor_pagar,
							sum(TotalPayments)as TotalPayments,
							sum(STotalPayments)as STotalPayments,
							day,
							Month,
							Paytype,State,Status,
							count(groupfl)
							from
							($querytoapp)as tmp group by $gb
							$page_limit");
		
			$va{'searchresults'}="";
			my $cadnamemodel;
			$cadnamemodel="";
			while(my $rec=$sth->fetchrow_hashref){
				$d = 1 - $d;
				$va{'searchresults'} .= "<tr bgcolor='$c[$d]' onmouseover='m_over(this)' onmouseout='m_out(this)' >\n";
				$va{'searchresults'} .= "  <td class='smalltext' valign='top'>$rec->{'ID_orders'}</td>" if($in{'groupby'}=~/id_orders/);
				$va{'searchresults'} .= "  <td class='smalltext' valign='top'>$rec->{'day'}</td>" if($in{'groupby'}=~/day/);
				$va{'searchresults'} .= "  <td class='smalltext' valign='top'>$rec->{'Month'}</td>" if($in{'groupby'}=~/month/);
				$va{'searchresults'} .= "  <td class='smalltext' valign='top'>$rec->{'State'}</td>" if($in{'groupby'}=~/state/);
				$va{'searchresults'} .= "  <td class='smalltext' valign='top'>$rec->{'Status'}</td>" if($in{'groupby'}=~/status/);
				$va{'searchresults'} .= "  <td class='smalltext' valign='top'>$rec->{'Paytype'}</td>" if($in{'groupby'}=~/paytype/);
				$va{'searchresults'} .= "  <td class='smalltext' valign='top' align='right'>".&format_price($rec->{'SVencidos'})."</td>" if(1);#$in{'groupby'}=~/id_preorders|day/);
				$va{'searchresults'} .= "  <td class='smalltext' valign='top' align='right'>".&format_price($rec->{'SPagados'})."</td>\n" if(1);#$in{'groupby'}=~/id_preorders|day/);
				$va{'searchresults'} .= "  <td class='smalltext' valign='top' align='right'>".&format_price($rec->{'SPor_pagar'})." </td>\n" if(1);#$in{'groupby'}=~/id_preorders|day/);
				$va{'searchresults'} .= "  <td class='smalltext' valign='top' align='right'>".&format_price($rec->{'STotalPayments'})." </td>\n" if(1);#$in{'groupby'}=~/id_preorders|day/);
				#$va{'searchresults'} .= "  <td class='smalltext' valign='top' align='center'>$rec->{'Good'} </td>\n";
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
			print &build_page('results_orders_good_bad_l_print.html');
		}else{
			print "Content-type: text/html\n\n";
			print &build_page('results_orders_good_bad_l.html');
		}
		return;
	}
	print "Content-type: text/html\n\n";
	print &build_page('rep_orders_good_bad_l.html');
}


##########################################################################################
#######                      RESULTADO REPORTES                               ############
##########################################################################################

sub results_orders_prod {
# --------------------------------------------------------
# Created :  Carlos Haas 01/01/2007 6:47:28 PM
# Last Update : 
# Locked by : 
# Description :
# Last Time Modified by RB on 10/05/2010 : Se agregan charts
##TODO: Todos los textos deben estar fuera del codigo y/o a traves de transtxt. Inclytendo los mensajes/titulos en los graficos


	my ($query_tot,$query_list) = @_;
	my ($sth) = &Do_SQL($query_tot);
	my ($tot_cant,$tot_amount) = $sth->fetchrow_array();
	my ($c_link);
	
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
				
				###### Amount / Quantity Bar
				if($in{'groupby'} eq 'id_products'){
					$va{'xaxis_categories'} .= "'". substr($ary[0],8,15) ."',";
				}else{
					$va{'xaxis_categories'} .= "'$ary[0]',";
				}
				$series_quantity .= $ary[1] . ',';
				$series_amount .= round($ary[2],2) .',';
				
				($in{'groupby'} eq 'id_products') and ($ary[0] = &load_name('sl_products','ID_products',$id_product,'LEFT(Name,12)'));
				($in{'groupby'} eq 'id_products' and $ary[0] eq '') and ($ary[0] = &load_name('sl_services','ID_services',$id_product - 100000,'LEFT(Name,10)'));
				($in{'groupby'} eq 'id_products' and $ary[0] eq '') and ($ary[0] = &load_name('sl_services','ID_services',$id_product - 99000,'LEFT(Name,10)'));
				###### Amount / Quantity Pie		
				$series_quantityp .= "['$ary[0]', ". round($ary[1]/$tot_cant,2) * 100 ."],";
				$series_amountp .= "['$ary[0]', ". round($ary[2]/$tot_amount,2) * 100 ."],";
				
		}
		$va{'tot_cant'} = $tot_cant;
		$va{'tot_amount'} = &format_price($tot_amount);
		
		(!$in{'chart_theme'}) and ($in{'chart_theme'} = 'gray');
		$va{'highchart_theme'} = ($in{'chart_theme'} eq 'blank') ? '' : &build_page('func/highcharts_theme_'. $in{'chart_theme'} .'.html');
		##### Amount / Quantity Bar
		chop($va{'xaxis_categories'});
		chop($series_quantity);
		chop($series_amount);

		my $xaxis_mod = ",title: { text: '$in{'groupby'}' } ";
		my $chart_mod= '';
		if($sth->rows() > 5){
			$xaxis_mod = ",labels: {rotation: -45, align: 'right', style: { font: 'normal 13px Verdana, sans-serif'}} ";
			$chart_mod = ',height: 450, margin: [ 50, 50, 150, 100]';
		}
		
		$va{'chart_options'} = "renderTo: 'container1', defaultSeriesType: 'areaspline' $chart_mod ";
		$va{'chart_title'} = 'Report By Products';
		$va{'chart_subtitle'} = $va{'report_name'};
		$va{'chart_xaxis'} = "categories: [$va{'xaxis_categories'}] $xaxis_mod ";
		$va{'chart_yaxis'} = "title: { text: 'Quantity / Amount', margin: 75 }";
		$va{'chart_tooltip'} = "enabled: true,formatter: function() {return '<b>'+ this.series.name +'</b><br/>'+this.x +': '+ this.y;}";
		$va{'series_data'} = "{ name: 'Quantity', data: [$series_quantity]}, { name: 'Amount', data: [$series_amount] }";
		$va{'highchart1'} = &build_page('func/construct_highcharts.html');
		
		
		###### Amount / Quantity Pie
		chop($series_quantityp);
		chop($series_amountp);


		## Pie Quantity
		$va{'chart_options'} = "renderTo: 'container2', margin: [50, 150, 10, 5], width: 400";
		$va{'chart_title'} = 'Quantity';
		$va{'chart_subtitle'} = 'Percentages';
		$va{'chart_plotarea'} = 'shadow: null, borderWidth: null, backgroundColor: null';
		$va{'chart_tooltip'} = "enabled: true,formatter: function() { return '<b>'+ this.point.name +'</b>: '+ this.y +' %';}";
		$va{'chart_plotoptions'} = "pie: {
							allowPointSelect: true,
							cursor: 'pointer',
							dataLabels: {
								enabled: true,
								formatter: function() {
									if (this.y > 50) return this.point.name;
								},
								color: 'white',
								style: {
									font: '13px Trebuchet MS, Verdana, sans-serif'
								}
							}
						}";
		$va{'chart_legend'} = "layout: 'vertical', style: { left: 'auto', bottom: 'auto', right: '10px', top: '50px' }";
		$va{'series_data'} = "{ type: 'pie', name: 'Quantity Percentages ', data: [$series_quantityp] }";
		$va{'highchart2'} = &build_page('func/construct_highcharts.html');
		

		## Pie Amount
		$va{'chart_options'} = "renderTo: 'container3', margin: [50, 150, 10, 5], width: 400";
		$va{'chart_title'} = 'Amount';
		$va{'series_data'} = "{ type: 'pie', name: 'Quantity Percentages ', data: [$series_amountp] }";
		$va{'highchart3'} = &build_page('func/construct_highcharts.html');

		
		###### Charge the js scripts if not charged
		if(!$va{'highcharts_js'}){
			$va{'highcharts_js'} = &build_page('func/highcharts_js.html');
		}
		
		
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
		print &build_page('results_orders_base_print.html');
	}else{
		print "Content-type: text/html\n\n";
		print &build_page('results_orders_base.html');
	}
}

sub results_orders_prodhrs {
# --------------------------------------------------------
# Created on: 07/14/08 @ 13:02:37
# Author: Carlos Haas
# Last Modified on: 07/14/08 @ 13:02:37
# Last Modified by: Carlos Haas
# Description : 
# Parameters : 
#			   
##TODO: Agregar Graficos al resultado

	my ($query,$query_sum) = @_;
	my ($sth) = &Do_SQL("SELECT COUNT(*),$query_sum FROM sl_orders_products,sl_orders $query");
	my ($tot_cant,$tot_amount) = $sth->fetchrow_array();
	my ($choices);
	if ($tot_cant>0 and $tot_amount>0){
		(!$in{'nh'}) and ($in{'nh'}=1);
		my (@c) = split(/,/,$cfg{'srcolors'});
		my ($sth) = &Do_SQL("SELECT HOUR(sl_orders.Time),COUNT(*) AS nums,$query_sum AS amounts FROM sl_orders_products,sl_orders $query GROUP BY HOUR(sl_orders.Time) $sb ");
		$va{'matches'} = $sth->rows;
		$sth = &Do_SQL("SELECT HOUR(sl_orders.Time),COUNT(*) AS nums,$query_sum AS amounts FROM sl_orders_products,sl_orders $query GROUP BY HOUR(sl_orders.Time) $sb ");
		while (@ary = $sth->fetchrow_array){
			$d = 1 - $d;
			$va{'searchresults'} .= qq|
				<tr bgcolor='$c[$d]'>
					<td>$ary[0].00 - $ary[0].59</td>
					<td align="right" valign="top" nowrap>|.&format_number($ary[1]).qq|</td>
					<td nowrap class="help_on" valign="top" nowrap>&nbsp; (|.&format_number($ary[1]/$tot_cant*100).qq| %)</td>
					<td align="right" valign="top" nowrap>|.&format_price($ary[2]).qq|</td>
					<td nowrap class="help_on" valign="top" nowrap>&nbsp; (|.&format_number($ary[2]/$tot_amount*100).qq| %)</td>
				</tr>\n|;
			$sth2 = &Do_SQL("SELECT RIGHT(sl_orders_products.ID_products,6),COUNT(*) AS nums,$query_sum AS amounts,sl_orders_products.ID_products FROM sl_orders_products,sl_orders $query AND HOUR(sl_orders.Time)=$ary[0] GROUP BY RIGHT(sl_orders_products.ID_products,6) $sb ");
			while (@ary2 = $sth2->fetchrow_array){
				$va{'searchresults'} .= qq|
				<tr bgcolor='$c[$d]'>
					<td class="smalltext">&nbsp;&nbsp;&nbsp;|.&format_sltvid($ary2[0])." " . &load_product_name($ary2[3]) . qq|</td>
					<td class="smalltext" align="right" valign="top" nowrap>|.&format_number($ary2[1]).qq|</td>
					<td class="smalltext" nowrap class="help_on" valign="top" nowrap>&nbsp; (|.&format_number($ary2[1]/($ary[1]+.001)*100).qq| %)</td>
					<td class="smalltext" align="right" valign="top" nowrap>|.&format_price($ary2[2]).qq|</td>
					<td class="smalltext" nowrap class="help_on" valign="top" nowrap>&nbsp; (|.&format_number($ary2[2]/($ary[2]+.001)*100).qq| %)</td>
				</tr>\n|;
			}
		}
		$va{'tot_cant'} = $tot_cant;
		$va{'tot_amount'} = &format_price($tot_amount);
		&auth_logging('report_view',1);
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
		print &build_page('results_orders_base_print.html');
	}else{
		($va{'rep1'},$va{'rep2'},$va{'rep3'},$va{'rep4'},$va{'rep5'},$va{'rep6'}) = ('on','off','off','off','off','off');
		print "Content-type: text/html\n\n";
		print &build_page('results_orders_base.html');
	}
}


sub results_orders_produt {
# --------------------------------------------------------
# Created on: 07/14/08 @ 14:25:19
# Author: Carlos Haas
# Last Modified on: 07/14/08 @ 14:25:19
# Last Modified by: Carlos Haas
# Description : 
# Parameters : 
#			   
##TODO: Todos los textos deben estar fuera del codigo y/o a traves de transtxt
##TODO: Agregar Graficos al Resultado

	my ($query,$query_sum) = @_;
	my ($choices,%tmp,$sb);
	if ($in{'sortby'}){
		$sb = "ORDER BY $in{'sortby'} $in{'sortorder'}";
	}


	my ($sth) = &Do_SQL("SELECT COUNT(*),$query_sum FROM sl_orders_products,sl_orders $query");
	my ($tot_cant,$tot_amount) = $sth->fetchrow_array();
	
	###,(SELECT SLTV_NetCost FROM sl_products WHERE ID_products=RIGHT(sl_orders_products.ID_products,6))
	$sth = &Do_SQL("SELECT SUM((SELECT SLTV_NetCost FROM sl_products WHERE ID_products=RIGHT(sl_orders_products.ID_products,6))*Quantity) FROM sl_orders_products,sl_orders $query ");
	$tot_cost = $sth->fetchrow;
	
	if ($tot_cant>0 and $tot_amount>0){
		(!$in{'nh'}) and ($in{'nh'}=1);
		$first = ($in{'nh'} - 1) * $usr{'pref_maxh'};	
		my ($sth) = &Do_SQL("SELECT RIGHT(sl_orders_products.ID_products,6),COUNT(*) AS nums,$query_sum AS amounts FROM sl_orders_products,sl_orders $query GROUP BY RIGHT(sl_orders_products.ID_products,6) $sb ");
		$va{'matches'} = $sth->rows;
		($va{'pageslist'},$qs) = &pages_list($in{'nh'},"/cgi-bin/mod/$usr{'application'}/admin",$va{'matches'},$usr{'pref_maxh'});
		if ($in{'print'}){
			$sth = &Do_SQL("SELECT RIGHT(sl_orders_products.ID_products,6),COUNT(*) AS nums,$query_sum AS amounts FROM sl_orders_products,sl_orders $query GROUP BY RIGHT(sl_orders_products.ID_products,6) $sb ");
		}else{
			$sth = &Do_SQL("SELECT RIGHT(sl_orders_products.ID_products,6),COUNT(*) AS nums,$query_sum AS amounts FROM sl_orders_products,sl_orders $query GROUP BY RIGHT(sl_orders_products.ID_products,6) $sb  LIMIT $first,$usr{'pref_maxh'}");
		}
		my($status,%tmp,$fulldesc);
		my (@c) = split(/,/,$cfg{'srcolors'});
		while (@ary = $sth->fetchrow_array){
			$d = 1 - $d;
			($status,%tmp) = &load_product_info($ary[0]);
			if ($tmp{'id_products'} ne $ary[0]){
				$linkprod = "mer_services";
				$fulldesc = &format_sltvid(600000000+$ary[0]) . "<br>".&load_name('sl_services','ID_services',int($ary[0]),'Name');
			}else{
				$linkprod = "mer_products";
				$choices = &load_choices($ary[0]);	
				$fulldesc= &format_sltvid($ary[0]) . "<br>$tmp{'name'}<br>$tmp{'model'} $choices";	
			}
			

			$va{'searchresults'} .= qq|
				<tr onmouseover='m_over(this)' onmouseout='m_out(this)' bgcolor='$c[$d]' onclick="trjump('$cfg{'pathcgi_adm_dbman'}?cmd=$linkprod&view=$ary[0]')">
					<td class='lnk_spec'>$fulldesc</td>
					<td align="right" valign="top">|.&format_number($ary[1]).qq|</td>
					<td nowrap class="help_on" valign="top">&nbsp; (|.&format_number($ary[1]/$tot_cant*100).qq| %)</td>
					<td align="right" valign="top" nowrap>|.&format_price($ary[2]).qq|<br>
								<u>|.&format_price(-$tmp{'sltv_netcost'}*$ary[1]).qq|</u><br>
								|.&format_price($ary[2]-$tmp{'sltv_netcost'}*$ary[1]).qq|</td>
					<td nowrap class="help_on" valign="top">&nbsp; (|.&format_number($ary[2]/$tot_amount*100).qq| %)</td>
				</tr>\n|;
			#$tot_cost       += $tmp{'sltv_netcost'}*$ary[1];	
		}
		$va{'tot_cant'} = $tot_cant;
		$va{'tot_amount'} = &format_price($tot_amount);
		
		
		$part = ($tot_cost * 100)/ $tot_amount;
		$part = sprintf("%.0f", $part);	
		$part2 =(($tot_amount-$tot_cost) * 100)/ $tot_amount;
		$part2 = sprintf("%.0f", $part2);	
		$va{'totinfo'} = qq|
					<tr>
						<td>Total Cost:</td>
						<td align="right" nowrap><u>|. &format_price(-$tot_cost).qq|</u></td>
						<td align="right" nowrap>(|. $part.qq| %)</td>
					</tr>
						<tr>
						<td>Total Utility:</td>
						<td align="right" nowrap>|. &format_price($tot_amount-$tot_cost).qq|</td>
						<td align="right" nowrap>(|. $part2.qq| %)</td>
					</tr>\n|;
		
		
		
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
		print &build_page('results_orders_base_print.html');
	}else{
		print "Content-type: text/html\n\n";
		print &build_page('results_orders_base.html');
	}
}

sub results_orders_categ {
# --------------------------------------------------------
# Created on: 07/14/08 @ 12:57:20
# Author: Carlos Haas
# Last Modified on: 07/14/08 @ 12:57:20
# Last Modified by: Carlos Haas
# Description : 
# Parameters : 
#		
##TODO: Agregar Graficos al resultado	   
	my ($query,$query_sum) = @_;
	my ($choices,%tmp,$sb,$stot_cant,$stot_amount);
	my (@c) = split(/,/,$cfg{'srcolors'});
	my ($sth) = &Do_SQL("SELECT COUNT(*),$query_sum FROM sl_orders_products,sl_orders  $query");
	my ($tot_cant,$tot_amount) = $sth->fetchrow_array();
	
	my ($sth) = &Do_SQL("SELECT ID_categories,Title FROM sl_categories WHERE Status='Active' AND ID_parent='0' ORDER BY Title;");
	while (($id_cat,$cat_name) = $sth->fetchrow_array()){
		$d = 1 - $d;
		$nquery = "$query AND RIGHT(sl_orders_products.ID_products,6) IN (SELECT ID_products FROM sl_products_categories WHERE ID_top='$id_cat') ";
		my ($sth) = &Do_SQL("SELECT COUNT(*),$query_sum FROM sl_orders_products,sl_orders $nquery");
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
		
	}
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
	&auth_logging('report_view',1);
	
	if ($in{'print'}){
		print "Content-type: text/html\n\n";
		print &build_page('header_print.html');
		print &build_page('results_orders_base_print.html');
	}else{
		print "Content-type: text/html\n\n";
		print &build_page('results_orders_base.html');
	}
}

sub results_orders_plevels {
# --------------------------------------------------------
# Created on: 07/14/08 @ 13:01:50
# Author: Carlos Haas
# Last Modified on: 07/14/08 @ 13:01:50
# Last Modified by: Carlos Haas
# Description : 
# Parameters : 
#			
##TODO: Agregar Graficos al Resultado
   
	my ($query,$query_sum) = @_;
	my ($choices,%tmp,$sb);
	if ($in{'sortby'}){
		$sb = "ORDER BY $in{'sortby'} $in{'sortorder'}";
	}
	my ($sth) = &Do_SQL("SELECT COUNT(*),$query_sum FROM sl_orders_products,sl_orders $query");
	my ($tot_cant,$tot_amount) = $sth->fetchrow_array();
	if ($tot_cant>0 and $tot_amount>0){
		(!$in{'nh'}) and ($in{'nh'}=1);
		$first = ($in{'nh'} - 1) * $usr{'pref_maxh'};	
		my ($sth) = &Do_SQL("SELECT ID_pricelevels,COUNT(*) AS nums,$query_sum AS amounts FROM sl_orders_products,sl_orders $query GROUP BY ID_pricelevels $sb ");
		$va{'matches'} = $sth->rows;
		($va{'pageslist'},$qs) = &pages_list($in{'nh'},"/cgi-bin/mod/$usr{'application'}/admin",$va{'matches'},$usr{'pref_maxh'});
		if ($in{'print'}){
			$sth = &Do_SQL("SELECT ID_pricelevels,COUNT(*) AS nums,$query_sum AS amounts FROM sl_orders_products,sl_orders $query GROUP BY ID_pricelevels $sb ");
		}else{
			$sth = &Do_SQL("SELECT ID_pricelevels,COUNT(*) AS nums,$query_sum AS amounts FROM sl_orders_products,sl_orders $query GROUP BY ID_pricelevels $sb  LIMIT $first,$usr{'pref_maxh'}");
		}
		my (@c) = split(/,/,$cfg{'srcolors'});
		while (@ary = $sth->fetchrow_array){
			$d = 1 - $d;
			$in{'id_pricelevels'} = $ary[0];
			$pricelevels = &load_pricelevels_name;
			if(!$pricelevels or $pricelevels eq '---'){
				$pricelevels = "($ary[0]) Unknow";
			}
			$va{'searchresults'} .= qq|
				<tr onmouseover='m_over(this)' onmouseout='m_out(this)' bgcolor='$c[$d]'>
					<td>$pricelevels</td>
					<td align="right" valign="top">|.&format_number($ary[1]).qq|</td>
					<td nowrap class="help_on" valign="top">&nbsp; (|.&format_number($ary[1]/$tot_cant*100).qq| %)</td>
					<td align="right" valign="top" nowrap>|.&format_price($ary[2]).qq|</td>
					<td nowrap class="help_on" valign="top">&nbsp; (|.&format_number($ary[2]/$tot_amount*100).qq| %)</td>
				</tr>\n|;
			#$tot_cost       += $tmp{'sltv_netcost'}*$ary[1];	
		}
		$va{'tot_cant'} = $tot_cant;
		$va{'tot_amount'} = &format_price($tot_amount);
		&auth_logging('report_view',1);
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
		print &build_page('results_orders_base_print.html');
	}else{
		($va{'rep1'},$va{'rep2'},$va{'rep3'},$va{'rep4'},$va{'rep5'},$va{'rep6'}) = ('on','off','off','off','off','off');
		print "Content-type: text/html\n\n";
		print &build_page('results_orders_base.html');
	}
}

sub results_orders_ana1 {
# --------------------------------------------------------
# Created :  Carlos Haas 01/01/2007 6:47:28 PM
# Last Update : 
# Locked by : 
# Description :
#
#
##TODO: Faltan Graficos

	my ($query,$null) = @_;
	my ($choices,%tmp,$sb);
	if ($in{'sortby'}){
		$sb = "ORDER BY $in{'sortby'} $in{'sortorder'}";
	}
	my ($sth) = &Do_SQL("SELECT COUNT(*),SUM(SalePrice*Quantity) FROM sl_orders_products,sl_orders $query");
	my ($tot_cant,$tot_amount) = $sth->fetchrow_array();
	if ($tot_cant>0 and $tot_amount>0){
		(!$in{'nh'}) and ($in{'nh'}=1);
		$first = ($in{'nh'} - 1) * $usr{'pref_maxh'};	
		my ($sth) = &Do_SQL("SELECT sl_orders.Date,COUNT(*) AS nums,SUM(SalePrice*Quantity) AS amounts FROM sl_orders_products,sl_orders $query GROUP BY sl_orders.Date $sb ");
		$va{'matches'} = $sth->rows;
		($va{'pageslist'},$qs) = &pages_list($in{'nh'},"/cgi-bin/mod/$usr{'application'}/admin",$va{'matches'},$usr{'pref_maxh'});
		if ($in{'print'}){
			$sth = &Do_SQL("SELECT sl_orders.Date,COUNT(*) AS nums,SUM(SalePrice*Quantity) AS amounts FROM sl_orders_products,sl_orders $query GROUP BY sl_orders.Date $sb ");
		}else{
			$sth = &Do_SQL("SELECT sl_orders.Date,COUNT(*) AS nums,SUM(SalePrice*Quantity) AS amounts FROM sl_orders_products,sl_orders $query GROUP BY sl_orders.Date $sb  LIMIT $first,$usr{'pref_maxh'}");
		}
		my (@c) = split(/,/,$cfg{'srcolors'});
		my ($col1,$col2,$col3);
		while (@ary = $sth->fetchrow_array){
			$d = 1 - $d;
			$sth1 = &Do_SQL("SELECT sl_orders.Status,COUNT(*) FROM sl_orders_products,sl_orders $query AND sl_orders.Date='$ary[0]' GROUP BY sl_orders.Status");
			my ($col1,$col2,$col3);
			while (@ary1 = $sth1->fetchrow_array){
				$col1 .= "<br>$ary1[0]";
				#$col2 .= "<br>(".&format_number($ary1[1]/$ary[1]*100)." %)";
				$width1 = int($ary1[1]/$ary[1]*200);
				$col2 .=  qq|<br><img src="$va{'imgurl'}/$usr{'pref_style'}/bluepixel.gif" height="8" width="$width1">&nbsp; (|.&format_number($ary1[1]/$ary[1]*100). " %)";
			}	
			
			$va{'searchresults'} .= qq|
				<tr onmouseover='m_over(this)' onmouseout='m_out(this)' bgcolor='$c[$d]'>
					<td valign="top">$ary[0]</td>
					<td align="right" valign="top">|.&format_number($ary[1]) . qq|<span class='help_on'>$col1</span></td>
					<td nowrap class="help_on" valign="top">&nbsp; (|.&format_number($ary[1]/$tot_cant*100).qq|%) $col2</td>
					<td align="right" valign="top" nowrap>|.&format_price($ary[2]).qq|</td>
					<td nowrap class="help_on" valign="top">&nbsp; (|.&format_number($ary[2]/$tot_amount*100).qq| %) $col3</td>
				</tr>\n|;
			#$tot_cost       += $tmp{'sltv_netcost'}*$ary[1];	
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
		print &build_page('results_orders_base_print.html');
	}else{
		($va{'rep1'},$va{'rep2'},$va{'rep3'},$va{'rep4'},$va{'rep5'},$va{'rep6'}) = ('on','off','off','off','off','off');
		print "Content-type: text/html\n\n";
		print &build_page('results_orders_base.html');
	}
}


sub results_orders_skus {
# --------------------------------------------------------
# Created :  Carlos Haas 01/01/2007 6:47:28 PM
# Last Update : 
# Locked by : 
# Description :
#
#
##TODO: Faltan Graficos

	my ($query,$query_sum) = @_;

	my ($sth) = &Do_SQL("SELECT COUNT(*),$query_sum FROM sl_orders_products,sl_orders $query");
	my ($tot_cant,$tot_amount) = $sth->fetchrow_array();
	my ($choices);
	if ($tot_cant>0 and $tot_amount>0){
		(!$in{'nh'}) and ($in{'nh'}=1);
		$first = ($in{'nh'} - 1) * $usr{'pref_maxh'};	
		my ($sth) = &Do_SQL("SELECT sl_orders_products.ID_products,COUNT(*) AS nums,$query_sum AS amounts FROM sl_orders_products,sl_orders $query GROUP BY ID_products $sb ");
		$va{'matches'} = $sth->rows;
		($va{'pageslist'},$qs) = &pages_list($in{'nh'},"/cgi-bin/mod/$usr{'application'}/admin",$va{'matches'},$usr{'pref_maxh'});
		if ($in{'print'}){
			$sth = &Do_SQL("SELECT sl_orders_products.ID_products,COUNT(*) AS nums,$query_sum AS amounts FROM sl_orders_products,sl_orders $query GROUP BY ID_products $sb ");
		}else{
			$sth = &Do_SQL("SELECT  sl_orders_products.ID_products,COUNT(*) AS nums,$query_sum AS amounts FROM sl_orders_products,sl_orders $query GROUP BY ID_products $sb  LIMIT $first,$usr{'pref_maxh'}");
		}
		my (@c) = split(/,/,$cfg{'srcolors'});
		while (@ary = $sth->fetchrow_array){
			$d = 1 - $d;
			$id_product = substr($ary[0],3,6);
			$choices = &load_choices($ary[0]);
			
			$va{'searchresults'} .= qq|
				<tr onmouseover='m_over(this)' onmouseout='m_out(this)' bgcolor='$c[$d]'>
					<td class='lnk_spec'><a href='dbman?cmd=mer_products&view=$id_product'>|.&format_sltvid($ary[0])."<br>".&load_db_names('sl_products','ID_products',substr($ary[0],3,6),'[Name]<br>[Model]').$choices.qq|</a></td>
					<td align="right" valign="top">|.&format_number($ary[1]).qq|</td>
					<td nowrap class="help_on" valign="top">&nbsp; (|.&format_number($ary[1]/$tot_cant*100).qq| %)</td>
					<td align="right" valign="top">|.&format_price($ary[2]).qq|</td>
					<td nowrap class="help_on" valign="top">&nbsp; (|.&format_number($ary[2]/$tot_amount*100).qq| %)</td>
				</tr>\n|;
		}
		$va{'tot_cant'} = $tot_cant;
		$va{'tot_amount'} = &format_price($tot_amount);
		&auth_logging('report_view',1);
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
		print &build_page('results_orders_base_print.html');
	}else{
		($va{'rep1'},$va{'rep2'},$va{'rep3'},$va{'rep4'},$va{'rep5'},$va{'rep6'}) = ('on','off','off','off','off','off');
		print "Content-type: text/html\n\n";
		print &build_page('results_orders_base.html');
	}
}

sub results_orders_pay {
# --------------------------------------------------------
# Created :  Carlos Haas 01/01/2007 6:47:28 PM
# Last Update : 
# Locked by : 
# Description :
# Last Time Modified by RB on 10/05/2010 : Se agregan charts
##TODO: Todos los textos deben estar fuera del codigo y/o a traves de transtxt, iblyendo las legendas en los graficos


	my ($query_tot,$query_list) = @_;
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
		while (@ary = $sth->fetchrow_array){
			$va{'searchresults'} .= qq|
				<tr>
					<td>$ary[0]</td>
					<td align="right">|.&format_number($ary[1]).qq|</td>
					<td nowrap class="help_on">&nbsp; (|.&format_number($ary[1]/$tot_cant*100).qq| %)</td>
					<td align="right">|.&format_price($ary[2]).qq|</td>
					<td nowrap class="help_on">&nbsp; (|.&format_number($ary[2]/$tot_amount*100).qq| %)</td>
				</tr>\n|;

			###### Amount / Quantity Bar
			if($in{'groupby'} eq 'id_products'){
				$va{'xaxis_categories'} .= "'". substr($ary[0],8,15) ."',";
			}else{
				$va{'xaxis_categories'} .= "'$ary[0]',";
			}
			$series_quantity .= $ary[1] . ',';
			$series_amount .= round($ary[2],2) .',';
			
			($in{'groupby'} eq 'id_products') and ($ary[0] = &load_name('sl_products','ID_products',$id_product,'LEFT(Name,12)'));
			($in{'groupby'} eq 'id_products' and $ary[0] eq '') and ($ary[0] = &load_name('sl_services','ID_services',$id_product - 100000,'LEFT(Name,10)'));
			($in{'groupby'} eq 'id_products' and $ary[0] eq '') and ($ary[0] = &load_name('sl_services','ID_services',$id_product - 99000,'LEFT(Name,10)'));
			###### Amount / Quantity Pie		
			$series_quantityp .= "['$ary[0]', ". round($ary[1]/$tot_cant,2) * 100 ."],";
			$series_amountp .= "['$ary[0]', ". round($ary[2]/$tot_amount,2) * 100 ."],";

		}
		$va{'tot_cant'} = $tot_cant;
		$va{'tot_amount'} = &format_price($tot_amount);


		(!$in{'chart_theme'}) and ($in{'chart_theme'} = 'gray');
		$va{'highchart_theme'} = ($in{'chart_theme'} eq 'blank') ? '' : &build_page('func/highcharts_theme_'. $in{'chart_theme'} .'.html');
		##### Amount / Quantity Bar
		chop($va{'xaxis_categories'});
		chop($series_quantity);
		chop($series_amount);

		my $xaxis_mod = ",title: { text: '$in{'groupby'}' } ";
		my $chart_mod= '';
		if($sth->rows() > 5){
			$xaxis_mod = ",labels: {rotation: -45, align: 'right', style: { font: 'normal 13px Verdana, sans-serif'}} ";
			$chart_mod = ',height: 450, margin: [ 50, 50, 150, 100]';
		}
		
		$va{'chart_options'} = "renderTo: 'container1', defaultSeriesType: 'column' $chart_mod ";
		$va{'chart_title'} = 'Report By Products';
		$va{'chart_subtitle'} = $va{'report_name'};
		$va{'chart_xaxis'} = "categories: [$va{'xaxis_categories'}] $xaxis_mod ";
		$va{'chart_yaxis'} = "title: { text: 'Quantity / Amount', margin: 75 }";
		$va{'chart_tooltip'} = "enabled: true,formatter: function() {return '<b>'+ this.series.name +'</b><br/>'+this.x +': '+ this.y;}";
		$va{'series_data'} = "{ name: 'Quantity', data: [$series_quantity]}, { name: 'Amount', data: [$series_amount] }";
		$va{'highchart1'} = &build_page('func/construct_highcharts.html');
		
		
		###### Amount / Quantity Pie
		chop($series_quantityp);
		chop($series_amountp);


		## Pie Quantity
		$va{'chart_options'} = "renderTo: 'container2', margin: [50, 150, 10, 5], width: 400";
		$va{'chart_title'} = 'Quantity';
		$va{'chart_subtitle'} = 'Percentages';
		$va{'chart_plotarea'} = 'shadow: null, borderWidth: null, backgroundColor: null';
		$va{'chart_tooltip'} = "enabled: true,formatter: function() { return '<b>'+ this.point.name +'</b>: '+ this.y +' %';}";
		$va{'chart_plotoptions'} = "pie: {
							allowPointSelect: true,
							cursor: 'pointer',
							dataLabels: {
								enabled: true,
								formatter: function() {
									if (this.y > 50) return this.point.name;
								},
								color: 'white',
								style: {
									font: '13px Trebuchet MS, Verdana, sans-serif'
								}
							}
						}";
		$va{'chart_legend'} = "layout: 'vertical', style: { left: 'auto', bottom: 'auto', right: '10px', top: '50px' }";
		$va{'series_data'} = "{ type: 'pie', name: 'Quantity Percentages ', data: [$series_quantityp] }";
		$va{'highchart2'} = &build_page('func/construct_highcharts.html');
		

		## Pie Amount
		$va{'chart_options'} = "renderTo: 'container3', margin: [50, 150, 10, 5], width: 400";
		$va{'chart_title'} = 'Amount';
		$va{'series_data'} = "{ type: 'pie', name: 'Quantity Percentages ', data: [$series_amountp] }";
		$va{'highchart3'} = &build_page('func/construct_highcharts.html');

		
		###### Charge the js scripts if not charged
		if(!$va{'highcharts_js'}){
			$va{'highcharts_js'} = &build_page('func/highcharts_js.html');
		}

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
		print &build_page('results_orders_base_print.html');
	}else{
		print "Content-type: text/html\n\n";
		print &build_page('results_orders_base.html');
	}
}

sub results_orders_fpago_col {
# --------------------------------------------------------
# Created :  Carlos Haas 01/01/2007 6:47:28 PM
# Last Update : 
# Locked by : 
# Description :
#
#
# Last Modified on: 01/12/09 11:56:59
# Last Modified by: MCC C. Gabriel Varela S: Se habilita filtro por producto
# Last Modified on: 01/13/09 16:27:29
# Last Modified by: MCC C. Gabriel Varela S: Se valida que la cantidad sea mayor a 0. Falta optimizar
##TODO: Todos los textos deben estar fuera del codigo y/o a traves de transtxt
##TODO: Faltan Graficos

	my ($query,$null) = @_;
	my ($d,%report,$tot_qty,$tot_amount,$qty,$amount,@cols,$unpaid);

	my ($cadinner);
	$cadinner="";
	$cadinner=" inner join sl_orders_products on (sl_orders.ID_orders=sl_orders_products.ID_orders and right(ID_products,6)=".int($in{'id_products'}).") " if($in{'id_products'}ne"");

	## All Orders
	my ($sth) = &Do_SQL("SELECT DISTINCT(sl_orders.ID_orders) FROM sl_orders inner join sl_orders_payments on (sl_orders.ID_orders=sl_orders_payments.ID_orders) $cadinner $query AND Type='Credit-Card' /*LIMIT 0,10000*/");
	$va{'searchresults'}="<tr>
			<td class='stdtxterr' colspan='2'>There are more than 10,000 records</td>
		</tr>"if($sth->rows==10000);
	IDORDEN: while ($id = $sth->fetchrow){
		$status = &check_ord_totals($id);
		if ($status eq 'OK'){
			my ($sth2) = &Do_SQL("SELECT COUNT(*),SUM(Amount) FROM sl_orders_payments WHERE ID_orders='$id' AND Type='Credit-Card' AND Status IN ('Approved','Denied') And Amount>0");
			($payments,$tot_ord) = $sth2->fetchrow_array();		
			($payments>1) or (next IDORDEN);
			$tot_amount += $tot_ord;
			++$tot_qty;
			my ($sth2) = &Do_SQL("SELECT COUNT(*) FROM sl_orders_payments WHERE ID_orders='$id' AND Type='Credit-Card' AND(DATEDIFF(Paymentdate,Curdate())<=-5 AND Paymentdate<>'0000-00-00') AND (Captured='No' OR CapDate='0000-00-00') AND (AuthCode<>'' OR AuthCode IS NOT NULL OR AuthCode<>'0000') AND Status IN ('Approved','Denied') And Amount>0");
			if ($sth2->fetchrow_array()>0){
				$report{'fpd_tot'.$payments} += $tot_ord;
				++$report{'fpd'.$payments};
				my ($sth2) = &Do_SQL("SELECT SUM(Amount) FROM sl_orders_payments WHERE ID_orders='$id' AND Type='Credit-Card' AND (AuthCode='' OR AuthCode IS NULL or AuthCode='0000') AND Status IN ('Approved','Denied') And Amount>0");
				$unpaid =  $sth2->fetchrow;
				$report{'fpd_unpaid'.$payments} += $unpaid ;	
				
				## Sub Totals
				++$report{'fpd'};	
				$report{'fpd_tot'} += $tot_ord;
				$report{'fpd_unpaid'} += $unpaid ;		
				if ($in{'export'}){
					$cols[0] = "$payments payments";
					$cols[1] = $id;
					$cols[2] = $tot_ord;
					$cols[3] = $tot_ord-$unpaid ;
					$cols[4] = $unpaid ;
					$report{'exportp'.$payments} .= '"'.join('","', @cols)."\"\n";
				}
			}else{
				$report{'fp_tot'.$payments} += $tot_ord;
				++$report{'fp'.$payments};
				my ($sth2) = &Do_SQL("SELECT SUM(Amount) FROM sl_orders_payments WHERE ID_orders='$id' AND Type='Credit-Card' AND (AuthCode='' OR AuthCode IS NULL or AuthCode='0000') AND Status IN ('Approved','Denied') And Amount>0");
				$unpaid = $sth2->fetchrow();
				$report{'fp_unpaid'.$payments} += $unpaid ;
				
				## Sub Totals
				++$report{'fp'};
				$report{'fp_unpaid'} += $unpaid;
				$report{'fp_tot'} += $tot_ord;
				if ($in{'export'}){
					$cols[0] = "$payments payments";
					$cols[1] = $id;
					$cols[2] = $tot_ord;
					$cols[3] = $tot_ord-$unpaid ;
					$cols[4] = $unpaid ;
					$report{'export'.$payments} .= '"'.join('","', @cols)."\"\n";
				}
			}
			
		}else{
			++$report{'error'.$status};
		}
	}
	(!$tot_qty) and ($tot_qty=1);
	(!$tot_amount) and ($tot_amount=1);	
	(!$report{'fp_tot'}) and ($report{'fp_tot'}=1);	
	(!$report{'fpd_tot'}) and ($report{'fpd_tot'}=1);	
	####################################################
	## NOT DUE
	####################################################
	$va{'searchresults'} .= qq|
		<tr onmouseover='m_over(this)' onmouseout='m_out(this)' bgcolor='$c[$d]'>
			<td colspan="9">Sales without Overdue Payments</td>
		</tr>\n|;
	for my $p(2..12){
		if ($report{'fp'.$p}>0){
			(!$report{'fp_tot'.$p}) and ($report{'fp_tot'.$p}=1);
			$va{'searchresults'} .= qq|	
			<tr onmouseover='m_over(this)' onmouseout='m_out(this)' bgcolor='$c[$d]'>
				<td valign="top" class='smalltext'>&nbsp;&nbsp;&nbsp; Payment : $p</td>
				<td align="right" valign="top" class='smalltext'><span class='help_on'>|.&format_number($report{'fp'.$p}).qq|</span></td>
				<td nowrap class="help_on" valign="top" class='smalltext'>&nbsp; (|.&format_number($report{'fp'.$p}/$tot_qty*100).qq|%)</td>
				<td align="right" valign="top" nowrap class='smalltext'>|.&format_price($report{'fp_tot'.$p}) . qq|</td>
				<td nowrap class="help_on" valign="top" class='smalltext'>&nbsp;  (|.&format_number($report{'fp_tot'.$p}/$tot_amount*100).qq|%)</td>
				<td align="right" valign="top" nowrap class='smalltext'>|. &format_price($report{'fp_tot'.$p}-$report{'fp_unpaid'.$p}) . qq|</td>
				<td nowrap class="help_on" valign="top" class='smalltext'>&nbsp;  (|.&format_number(($report{'fp_tot'.$p}-$report{'fp_unpaid'.$p})/$report{'fp_tot'.$p}*100).qq|%)</td>
				<td align="right" valign="top" nowrap class='smalltext'>|. &format_price($report{'fp_unpaid'.$p}) .qq|</td>
				<td nowrap class="help_on" valign="top" class='smalltext'>&nbsp;  (|.&format_number($report{'fp_unpaid'.$p}/$report{'fp_tot'.$p}*100).qq|%)</td>
			</tr>\n|;
		}
	}

	$va{'searchresults'} .= qq|	
			<tr onmouseover='m_over(this)' onmouseout='m_out(this)' bgcolor='$c[$d]'>
				<td valign="top" class='smalltext' align="right">&nbsp;&nbsp;&nbsp; Total</td>
				<td align="right" valign="top" class='smalltext'><span class='help_on'>|.&format_number($report{'fp'}).qq|</span></td>
				<td nowrap class="help_on" valign="top" class='smalltext'>&nbsp; (|.&format_number($report{'fp'}/$tot_qty*100).qq|%)</td>
				<td align="right" valign="top" nowrap class='smalltext'>|.&format_price($report{'fp_tot'}) .qq|</td>
				<td nowrap class="help_on" valign="top" class='smalltext'>&nbsp;  (|.&format_number($report{'fp_tot'}/$tot_amount*100).qq|%)</td>
				<td align="right" valign="top" nowrap class='smalltext'>|.&format_price($report{'fp_tot'}-$report{'fp_unpaid'})  . qq|
				<td nowrap class="help_on" valign="top" class='smalltext'>&nbsp;  (|.&format_number(($report{'fp_tot'}-$report{'fp_unpaid'})/$report{'fp_tot'}*100).qq|%)</td>
				<td align="right" valign="top" nowrap class='smalltext'>|.&format_price($report{'fp_unpaid'}).qq|</td>
				<td nowrap class="help_on" valign="top" class='smalltext'>&nbsp;  (|.&format_number($report{'fp_unpaid'}/$report{'fp_tot'}*100).qq|%)</td>
			</tr>\n|;

	####################################################
	### OVER DUE
	####################################################
	$va{'searchresults'} .= qq|
		<tr bgcolor='$c[$d]'>
			<td colspan="5">Sales with Overdue Payments</td>
		</tr>\n|;
	for my $p(2..12){
		if ($report{'fpd'.$p}>0){
			(!$report{'fpd_tot'.$p}) and ($report{'fpd_tot'.$p}=1);
			$va{'searchresults'} .= qq|	
			<tr onmouseover='m_over(this)' onmouseout='m_out(this)' bgcolor='$c[$d]'>
				<td valign="top" class='smalltext'>&nbsp;&nbsp;&nbsp; Payment : $p</td>
				<td align="right" valign="top" class='smalltext'><span class='help_on'>|.&format_number($report{'fpd'.$p}).qq|</span></td>
				<td nowrap class="help_on" valign="top" class='smalltext'>&nbsp; (|.&format_number($report{'fpd'.$p}/$tot_qty*100).qq|%)</td>
				<td align="right" valign="top" nowrap class='smalltext'>|.&format_price($report{'fpd_tot'.$p}) .qq|</td>
				<td nowrap class="help_on" valign="top" class='smalltext'>&nbsp;  (|.&format_number($report{'fpd_tot'.$p}/$tot_amount*100).qq|%)</td>
				<td align="right" valign="top" nowrap class='smalltext'>|. &format_price($report{'fpd_tot'.$p}-$report{'fpd_unpaid'.$p})  .qq|</td>
				<td nowrap class="help_on" valign="top" class='smalltext'>&nbsp;  (|.&format_number(($report{'fpd_tot'.$p}-$report{'fpd_unpaid'.$p})/$report{'fpd_tot'.$p}*100).qq|%)</td>
				<td align="right" valign="top" nowrap class='smalltext'>|. &format_price($report{'fpd_unpaid'.$p}) .qq|</td>
				<td nowrap class="help_on" valign="top" class='smalltext'>&nbsp;  (|.&format_number($report{'fpd_unpaid'.$p}/$report{'fpd_tot'.$p}*100).qq|%)</td>
			</tr>\n|;
		}
	}
	$va{'searchresults'} .= qq|	
			<tr onmouseover='m_over(this)' onmouseout='m_out(this)' bgcolor='$c[$d]'>
				<td valign="top" class='smalltext' align="right">&nbsp;&nbsp;&nbsp; Total</td>
				<td align="right" valign="top" class='smalltext'><span class='help_on'>|.&format_number($report{'fpd'}).qq|</span></td>
				<td nowrap class="help_on" valign="top" class='smalltext'>&nbsp; (|.&format_number($report{'fpd'}/$tot_qty*100).qq|%)</td>
				<td align="right" valign="top" nowrap class='smalltext'>|. &format_price($report{'fpd_tot'}) .qq|</td>
				<td nowrap class="help_on" valign="top" class='smalltext'>&nbsp;  (|.&format_number($report{'fpd_tot'}/$tot_amount*100).qq|%)</td>
				<td align="right" valign="top" nowrap class='smalltext'>|. &format_price($report{'fpd_tot'.$p}-$report{'fpd_unpaid'}) .qq|</td> 
				<td nowrap class="help_on" valign="top" class='smalltext'>&nbsp;  (|.&format_number(($report{'fpd_tot'.$p}-$report{'fpd_unpaid'})/$report{'fpd_tot'}*100).qq|%)</td>
				<td align="right" valign="top" nowrap class='smalltext'>|. &format_price($report{'fpd_unpaid'})  .qq|</td>
				<td nowrap class="help_on" valign="top" class='smalltext'>&nbsp;  (|.&format_number($report{'fpd_unpaid'}/$report{'fpd_tot'}*100).qq|%)</td>
			</tr>\n|;
	
	
	$va{'searchresults'} .= qq|
		<tr onmouseover='m_over(this)' onmouseout='m_out(this)' bgcolor='$c[$d]'>
			<td colspan="9" class="smalltext" align="center">
				Skipped Sales due to error in 'Payments' : |. &format_number($report{'errorPayments Error'}). qq| &nbsp;&nbsp;&nbsp;
				Skipped Sales due to error in 'Products' : |. &format_number($report{'errorProducts Error'}). qq|</td>
		</tr>\n|;	

	$va{'tot_cant'} = &format_number($tot_qty);
	$va{'tot_amount'} = &format_price($tot_amount);
	$va{'matches'} = $va{'tot_cant'};
	$va{'pageslist'} = 1;

	if ($in{'print'}){
		print "Content-type: text/html\n\n";
		print &build_page('header_print.html');
		print &build_page('results_orders_repan_print.html');
	}elsif ($in{'export'}){
		@cols = (' ','ID Order','Total','Paid','UnPaid');
		print "Content-type: application/vnd.ms-excel\n";
		print "Content-disposition: attachment; filename=fp_analytic.csv\n\n";
		print "Sales without Overdue Payments\n";
		print '"'.join('","', @cols)."\"\n";
		for my $p(2..12){
			if ($report{'fp'.$p}>0){
				print $report{'export'.$p};
			}
		}
		print "Sales with Overdue Payments\n";
		print '"'.join('","', @cols)."\"\n";
		for my $p(2..12){
			if ($report{'fp'.$p}>0){
				print $report{'exportp'.$p};
			}
		}
	}else{
		($nul,$qs) = &pages_list($in{'nh'},"/cgi-bin/mod/$usr{'application'}/admin",$va{'matches'},$usr{'pref_maxh'});
		$va{'extabtns'} = qq|<a href="javascript:prnwin('/cgi-bin/mod/[ur_application]/admin?export=1&$qs')"><img src='[va_imgurl]/[ur_pref_style]/b_xls.gif' title='Export' alt='' border='0'></a>|;
		($va{'rep1'},$va{'rep2'},$va{'rep3'},$va{'rep4'},$va{'rep5'},$va{'rep6'}) = ('off','off','on','off','off','off');
		print "Content-type: text/html\n\n";
		print &build_page('results_orders_repan.html');
	}
}

sub results_orders_fpago_st {
# --------------------------------------------------------
# Created :  Carlos Haas 01/01/2007 6:47:28 PM
# Last Update : 
# Locked by : 
# Description :
#
#
# Last Modified on: 01/06/09 18:13:10
# Last Modified by: MCC C. Gabriel Varela S: Se modifica para poder filtrar por producto
# Last Modified on: 03/30/09 18:10:46
# Last Modified by: MCC C. Gabriel Varela S: Se cambia leyenda por not payment date defined
# Last Modified on: 05/27/09 15:30:33
# Last Modified by: MCC C. Gabriel Varela S: Se optimiza tomando en cuenta captured
##TODO: Todos los textos deben estar fuera del codigo y/o a traves de transtxt
##TODO: Faltan Graficos


	my ($query,$null) = @_;
	my ($d,%report);
	my ($cadinner);
	$cadinner="";
	($in{'id_products'}ne"") and ($cadinner=" AND 0 < (SELECT COUNT(*) FROM sl_orders_products WHERE ID_orders = sl_orders.ID_orders AND RIGHT(ID_products,6)=967763 AND Status NOT IN('Order Cancelled', 'Inactive')) ");
	if ($in{'export'}){
		@cols = ('ID Order','Order Date','Payment Date','Amount','Status','ProdStatus','PayStatus','Class');
		print "Content-type: application/vnd.ms-excel\n";
		print "Content-disposition: attachment; filename=ARanalisis.csv\n\n";
		print '"'.join('","', @cols)."\"\n";

		my ($sth) = &Do_SQL("SELECT sl_orders.ID_orders,sl_orders.Date, Paymentdate,Amount ,sl_orders.Status, StatusPrd, StatusPay FROM sl_orders inner join sl_orders_payments on (sl_orders.ID_orders=sl_orders_payments.ID_orders) $query  AND (DATEDIFF(Paymentdate,Curdate())>0 AND Paymentdate<>'0000-00-00')  AND (Captured='No' OR CapDate='0000-00-00')");
		while (@ary = $sth->fetchrow_array){
			$status = &check_ord_totals($ary[0]);
			if ($status eq 'OK'){
				my ($sth2) = &Do_SQL("SELECT COUNT(*) FROM sl_orders_payments WHERE ID_orders='$ary[0]' AND DATEDIFF(Paymentdate,Curdate())<-5 AND Amount>0 AND (Captured='No' OR CapDate='0000-00-00')");
				if ($sth2->fetchrow>0){
					push(@ary,'C');
				}else{
					push(@ary,'A');
				}	
			}else{
				push(@ary,'B');
			}
			print '"'.join('","', @ary)."\"\n";
		}
		return;
	}
	


	## FP Due (90 days)
	#my ($sth) = &Do_SQL("SELECT SUM(Amount) FROM sl_orders,sl_orders_payments $query AND Type='Credit-Card' AND (DATEDIFF(Paymentdate,NOW())<-90 AND Paymentdate<>'0000-00-00') AND (Captured<>'Yes' OR ISNULL(Captured) OR ISNULL(CapDate) OR CapDate='0000-00-00')");
	my ($sth) = &Do_SQL("SELECT SUM(Amount) FROM sl_orders inner join sl_orders_payments on (sl_orders.ID_orders=sl_orders_payments.ID_orders) $query  $cadinner AND Type='Credit-Card' AND (DATEDIFF(Paymentdate,Curdate())<-90 AND Paymentdate<>'0000-00-00') AND (Captured='No' OR CapDate='0000-00-00')");
	my ($amount) = $sth->fetchrow;
	my ($sth) = &Do_SQL("SELECT COUNT(DISTINCT(sl_orders.ID_orders)) FROM sl_orders inner join sl_orders_payments on (sl_orders.ID_orders=sl_orders_payments.ID_orders) $query  $cadinner AND Type='Credit-Card' AND (DATEDIFF(Paymentdate,Curdate())<-90 AND Paymentdate<>'0000-00-00')  AND (Captured='No' OR CapDate='0000-00-00')");
	my ($qty) = $sth->fetchrow;
	$tot_amount += $amount;
	$tot_qty    += $qty;
	$report{'due_90'}[0] = $qty;
	$report{'due_90'}[1] = $amount;
	
	## FP Due (60-90 days)
	my ($sth) = &Do_SQL("SELECT SUM(Amount) FROM sl_orders inner join sl_orders_payments on (sl_orders.ID_orders=sl_orders_payments.ID_orders) $query  $cadinner AND Type='Credit-Card' AND (DATEDIFF(Paymentdate,Curdate())<-60 AND DATEDIFF(Paymentdate,Curdate())>=-90 AND Paymentdate<>'0000-00-00') AND (Captured='No' OR CapDate='0000-00-00')");
	my ($amount) = $sth->fetchrow;
	my ($sth) = &Do_SQL("SELECT COUNT(DISTINCT(sl_orders.ID_orders)) FROM sl_orders inner join sl_orders_payments on (sl_orders.ID_orders=sl_orders_payments.ID_orders) $query  $cadinner AND Type='Credit-Card' AND (DATEDIFF(Paymentdate,Curdate())<-60 AND DATEDIFF(Paymentdate,Curdate())>=-90 AND Paymentdate<>'0000-00-00')  AND (Captured='No' OR CapDate='0000-00-00')");
	my ($qty) = $sth->fetchrow;
	$tot_amount += $amount;
	$tot_qty    += $qty;
	$report{'due_60'}[0] = $qty;
	$report{'due_60'}[1] = $amount;

	## FP Due (31-60 days)
	my ($sth) = &Do_SQL("SELECT SUM(Amount) FROM sl_orders inner join sl_orders_payments on (sl_orders.ID_orders=sl_orders_payments.ID_orders) $query  $cadinner AND Type='Credit-Card' AND (DATEDIFF(Paymentdate,Curdate())<-30 AND DATEDIFF(Paymentdate,Curdate())>=-60 AND Paymentdate<>'0000-00-00') AND (Captured='No' OR CapDate='0000-00-00')");
	my ($amount) = $sth->fetchrow;
	my ($sth) = &Do_SQL("SELECT COUNT(DISTINCT(sl_orders.ID_orders)) FROM sl_orders inner join sl_orders_payments on (sl_orders.ID_orders=sl_orders_payments.ID_orders) $query  $cadinner AND Type='Credit-Card' AND (DATEDIFF(Paymentdate,Curdate())<-30 AND DATEDIFF(Paymentdate,Curdate())>=-60 AND Paymentdate<>'0000-00-00')  AND (Captured='No' OR CapDate='0000-00-00')");
	my ($qty) = $sth->fetchrow;
	$tot_amount += $amount;
	$tot_qty    += $qty;
	$report{'due_30'}[0] = $qty;
	$report{'due_30'}[1] = $amount;
	

	## FP Due (1-30 days)
	my ($sth) = &Do_SQL("SELECT SUM(Amount) FROM sl_orders inner join sl_orders_payments on (sl_orders.ID_orders=sl_orders_payments.ID_orders) $query  $cadinner AND Type='Credit-Card' AND (DATEDIFF(Paymentdate,Curdate())<0 AND DATEDIFF(Paymentdate,Curdate())>=-30 AND Paymentdate<>'0000-00-00') AND (Captured='No' OR CapDate='0000-00-00')");
	my ($amount) = $sth->fetchrow;
	my ($sth) = &Do_SQL("SELECT COUNT(DISTINCT(sl_orders.ID_orders)) FROM sl_orders inner join sl_orders_payments on (sl_orders.ID_orders=sl_orders_payments.ID_orders) $query  $cadinner AND Type='Credit-Card' AND (DATEDIFF(Paymentdate,Curdate())<0 AND DATEDIFF(Paymentdate,Curdate())>=-30 AND Paymentdate<>'0000-00-00')  AND (Captured='No' OR CapDate='0000-00-00')");
	my ($qty) = $sth->fetchrow;
	$tot_amount += $amount;
	$tot_qty    += $qty;
	$report{'due'}[0] = $qty;
	$report{'due'}[1] = $amount;

	## FP Due (Today)
	my ($sth) = &Do_SQL("SELECT SUM(Amount) FROM sl_orders inner join sl_orders_payments on (sl_orders.ID_orders=sl_orders_payments.ID_orders) $cadinner $query AND Type='Credit-Card' AND (Paymentdate=Curdate() AND Paymentdate<>'0000-00-00') AND (Captured='No' OR CapDate='0000-00-00')");
	my ($amount) = $sth->fetchrow;
	my ($sth) = &Do_SQL("SELECT COUNT(DISTINCT(sl_orders.ID_orders)) FROM sl_orders inner join sl_orders_payments on (sl_orders.ID_orders=sl_orders_payments.ID_orders) $query   $cadinner AND Type='Credit-Card' AND (Paymentdate=Curdate() AND Paymentdate<>'0000-00-00')  AND (Captured='No' OR CapDate='0000-00-00')");
	my ($qty) = $sth->fetchrow;
	$tot_amount += $amount;
	$tot_qty    += $qty;
	$report{'due_now'}[0] = $qty;
	$report{'due_now'}[1] = $amount;
	
	
	## FP AR (1-30 days)
	my ($sth) = &Do_SQL("SELECT SUM(Amount) FROM sl_orders inner join sl_orders_payments on (sl_orders.ID_orders=sl_orders_payments.ID_orders) $query  $cadinner AND Type='Credit-Card' AND (DATEDIFF(Paymentdate,Curdate())>0 AND DATEDIFF(Paymentdate,Curdate())<=30 AND Paymentdate<>'0000-00-00') AND (Captured='No' OR CapDate='0000-00-00')");
	my ($amount) = $sth->fetchrow;
	my ($sth) = &Do_SQL("SELECT COUNT(DISTINCT(sl_orders.ID_orders)) FROM sl_orders inner join sl_orders_payments on (sl_orders.ID_orders=sl_orders_payments.ID_orders) $query  $cadinner AND Type='Credit-Card' AND (DATEDIFF(Paymentdate,Curdate())>0 AND DATEDIFF(Paymentdate,Curdate())<=30 AND Paymentdate<>'0000-00-00')  AND (Captured='No' OR CapDate='0000-00-00')");
	my ($qty) = $sth->fetchrow;
	$tot_amount += $amount;
	$tot_qty    += $qty;
	$report{'ar_30'}[0] = $qty;
	$report{'ar_30'}[1] = $amount;
	
	## FP AR (30-60 days)
	my ($sth) = &Do_SQL("SELECT SUM(Amount) FROM sl_orders inner join sl_orders_payments on (sl_orders.ID_orders=sl_orders_payments.ID_orders) $query  $cadinner AND Type='Credit-Card' AND (DATEDIFF(Paymentdate,Curdate())>30 AND DATEDIFF(Paymentdate,Curdate())<=60 AND Paymentdate<>'0000-00-00') AND (Captured='No' OR CapDate='0000-00-00')");
	my ($amount) = $sth->fetchrow;
	my ($sth) = &Do_SQL("SELECT COUNT(DISTINCT(sl_orders.ID_orders)) FROM sl_orders inner join sl_orders_payments on (sl_orders.ID_orders=sl_orders_payments.ID_orders) $query  $cadinner AND Type='Credit-Card' AND (DATEDIFF(Paymentdate,Curdate())>30 AND DATEDIFF(Paymentdate,Curdate())<=60 AND Paymentdate<>'0000-00-00')  AND (Captured='No' OR CapDate='0000-00-00')");
	my ($qty) = $sth->fetchrow;
	$tot_amount += $amount;
	$tot_qty    += $qty;
	$report{'ar_60'}[0] = $qty;
	$report{'ar_60'}[1] = $amount;


	## FP AR (61-90 days)
	my ($sth) = &Do_SQL("SELECT SUM(Amount) FROM sl_orders inner join sl_orders_payments on (sl_orders.ID_orders=sl_orders_payments.ID_orders) $query  $cadinner AND Type='Credit-Card' AND (DATEDIFF(Paymentdate,Curdate())>60 AND DATEDIFF(Paymentdate,Curdate())<=90 AND Paymentdate<>'0000-00-00') AND (Captured='No' OR CapDate='0000-00-00')");
	my ($amount) = $sth->fetchrow;
	my ($sth) = &Do_SQL("SELECT COUNT(DISTINCT(sl_orders.ID_orders)) FROM sl_orders inner join sl_orders_payments on (sl_orders.ID_orders=sl_orders_payments.ID_orders) $query  $cadinner AND Type='Credit-Card' AND (DATEDIFF(Paymentdate,Curdate())>60 AND DATEDIFF(Paymentdate,Curdate())<=90 AND Paymentdate<>'0000-00-00')  AND (Captured='No' OR CapDate='0000-00-00')");
	my ($qty) = $sth->fetchrow;
	$tot_amount += $amount;
	$tot_qty    += $qty;
	$report{'ar_90'}[0] = $qty;
	$report{'ar_90'}[1] = $amount;


	## FP AR (91 days)
	my ($sth) = &Do_SQL("SELECT SUM(Amount) FROM sl_orders inner join sl_orders_payments on (sl_orders.ID_orders=sl_orders_payments.ID_orders) $query   $cadinner AND Type='Credit-Card' AND (DATEDIFF(Paymentdate,Curdate())>90 AND Paymentdate<>'0000-00-00') AND (Captured='No' OR CapDate='0000-00-00')");
	my ($amount) = $sth->fetchrow;
	my ($sth) = &Do_SQL("SELECT COUNT(DISTINCT(sl_orders.ID_orders)) FROM sl_orders inner join sl_orders_payments on (sl_orders.ID_orders=sl_orders_payments.ID_orders) $query $cadinner  AND Type='Credit-Card' AND (DATEDIFF(Paymentdate,Curdate())>90 AND Paymentdate<>'0000-00-00')  AND (Captured='No' OR CapDate='0000-00-00')");
	my ($qty) = $sth->fetchrow;
	$tot_amount += $amount;
	$tot_qty    += $qty;
	$report{'ar_91'}[0] = $qty;
	$report{'ar_91'}[1] = $amount;

	## PAID
	my ($sth) = &Do_SQL("SELECT SUM(Amount) FROM sl_orders inner join sl_orders_payments on (sl_orders.ID_orders=sl_orders_payments.ID_orders) $cadinner $query  AND Type='Credit-Card' AND Captured='Yes'");
	my ($amount) = $sth->fetchrow;
	my ($sth) = &Do_SQL("SELECT COUNT(DISTINCT(sl_orders.ID_orders)) FROM sl_orders inner join sl_orders_payments on (sl_orders.ID_orders=sl_orders_payments.ID_orders) $query $cadinner  AND Type='Credit-Card' AND Captured='Yes' ");
	my ($qty) = $sth->fetchrow;
	$tot_amount += $amount;
	$tot_qty    += $qty;
	$report{'paid'}[0] = $qty;
	$report{'paid'}[1] = $amount;


	## NOT FLEXIPAGO
	my ($sth) = &Do_SQL("SELECT SUM(Amount) FROM sl_orders inner join sl_orders_payments on (sl_orders.ID_orders=sl_orders_payments.ID_orders) $cadinner $query  AND Type='Credit-Card' AND (Paymentdate='0000-00-00') AND (Captured='No' OR CapDate='0000-00-00')");
	my ($amount) = $sth->fetchrow;
	my ($sth) = &Do_SQL("SELECT COUNT(DISTINCT(sl_orders.ID_orders)) FROM sl_orders inner join sl_orders_payments on (sl_orders.ID_orders=sl_orders_payments.ID_orders) $query $cadinner  AND Type='Credit-Card' AND (Paymentdate='0000-00-00') AND (Captured='No' OR CapDate='0000-00-00')");
	my ($qty) = $sth->fetchrow;
	$tot_amount += $amount;
	$tot_qty    += $qty;
	$report{'nofp'}[0] = $qty;
	$report{'nofp'}[1] = $amount;

	
	if($tot_amount > 0 ){
			## PAID
			$va{'searchresults'} .= qq|	
				<tr onmouseover='m_over(this)' onmouseout='m_out(this)' bgcolor='$c[$d]'>
					<td valign="top" class='smalltext'>&nbsp;&nbsp;&nbsp; Paid</td>
					<td align="right" valign="top" class='smalltext'><span class='help_on'>|.&format_number($report{'paid'}[0]).qq|</span></td>
					<td nowrap class="help_on" valign="top" class='smalltext'>&nbsp; (|.&format_number($report{'paid'}[0]/$tot_qty*100).qq|%)</td>
					<td align="right" valign="top" nowrap class='smalltext'>|.&format_price($report{'paid'}[1]).qq|</td>
					<td nowrap class="help_on" valign="top" class='smalltext'>&nbsp;  (|.&format_number($report{'paid'}[1]/$tot_amount*100).qq|%)</td>
				</tr>\n|;	
			## NOT FLEXIPAGOS / NOT PAID
			$va{'searchresults'} .= qq|	
				<tr onmouseover='m_over(this)' onmouseout='m_out(this)' bgcolor='$c[$d]'>
					<td valign="top" class='smalltext'>&nbsp;&nbsp;&nbsp; not Paid/ not Payment Date defined</td>
					<td align="right" valign="top" class='smalltext'><span class='help_on'>|.&format_number($report{'nofp'}[0]).qq|</span></td>
					<td nowrap class="help_on" valign="top" class='smalltext'>&nbsp; (|.&format_number($report{'nofp'}[0]/$tot_qty*100).qq|%)</td>
					<td align="right" valign="top" nowrap class='smalltext'>|.&format_price($report{'nofp'}[1]).qq|</td>
					<td nowrap class="help_on" valign="top" class='smalltext'>&nbsp;  (|.&format_number($report{'nofp'}[1]/$tot_amount*100).qq|%)</td>
				</tr>\n|;
		
			$va{'searchresults'} .= qq|
				<tr onmouseover='m_over(this)' onmouseout='m_out(this)' bgcolor='$c[$d]'>
					<td colspan="5">&nbsp;</td>
				</tr>\n|;		
			## FP Due (90 days)
			$va{'searchresults'} .= qq|	
				<tr onmouseover='m_over(this)' onmouseout='m_out(this)' bgcolor='$c[$d]'>
					<td valign="top" class='smalltext'>&nbsp;&nbsp;&nbsp; FP Past Due (91 or more days)</td>
					<td align="right" valign="top" class='smalltext'><span class='help_on'>|.&format_number($report{'due_90'}[0]).qq|</span></td>
					<td nowrap class="help_on" valign="top" class='smalltext'>&nbsp; (|.&format_number($report{'due_90'}[0]/$tot_qty*100).qq|%)</td>
					<td align="right" valign="top" nowrap class='smalltext'>|.&format_price($report{'due_90'}[1]).qq|</td>
					<td nowrap class="help_on" valign="top" class='smalltext'>&nbsp;  (|.&format_number($report{'due_90'}[1]/$tot_amount*100).qq|%)</td>
				</tr>\n|;

			## FP Due (61-90 days)
			$va{'searchresults'} .= qq|	
				<tr onmouseover='m_over(this)' onmouseout='m_out(this)' bgcolor='$c[$d]'>
					<td valign="top" class='smalltext'>&nbsp;&nbsp;&nbsp; FP Past Due (61-90 days)</td>
					<td align="right" valign="top" class='smalltext'><span class='help_on'>|.&format_number($report{'due_60'}[0]).qq|</span></td>
					<td nowrap class="help_on" valign="top" class='smalltext'>&nbsp; (|.&format_number($report{'due_60'}[0]/$tot_qty*100).qq|%)</td>
					<td align="right" valign="top" nowrap class='smalltext'>|.&format_price($report{'due_60'}[1]).qq|</td>
					<td nowrap class="help_on" valign="top" class='smalltext'>&nbsp;  (|.&format_number($report{'due_60'}[1]/$tot_amount*100).qq|%)</td>
				</tr>\n|;	

			## FP Due (31-60 days)
			$va{'searchresults'} .= qq|	
				<tr onmouseover='m_over(this)' onmouseout='m_out(this)' bgcolor='$c[$d]'>
					<td valign="top" class='smalltext'>&nbsp;&nbsp;&nbsp; FP Past Due (31-60 days)</td>
					<td align="right" valign="top" class='smalltext'><span class='help_on'>|.&format_number($report{'due_30'}[0]).qq|</span></td>
					<td nowrap class="help_on" valign="top" class='smalltext'>&nbsp; (|.&format_number($report{'due_30'}[0]/$tot_qty*100).qq|%)</td>
					<td align="right" valign="top" nowrap class='smalltext'>|.&format_price($report{'due_30'}[1]).qq|</td>
					<td nowrap class="help_on" valign="top" class='smalltext'>&nbsp;  (|.&format_number($report{'due_30'}[1]/$tot_amount*100).qq|%)</td>
				</tr>\n|;	
	
			## FP Due (1-30 days)
			$va{'searchresults'} .= qq|	
				<tr onmouseover='m_over(this)' onmouseout='m_out(this)' bgcolor='$c[$d]'>
					<td valign="top" class='smalltext'>&nbsp;&nbsp;&nbsp; FP Past Due (1-30 days)</td>
					<td align="right" valign="top" class='smalltext'><span class='help_on'>|.&format_number($report{'due'}[0]).qq|</span></td>
					<td nowrap class="help_on" valign="top" class='smalltext'>&nbsp; (|.&format_number($report{'due'}[0]/$tot_qty*100).qq|%)</td>
					<td align="right" valign="top" nowrap class='smalltext'>|.&format_price($report{'due'}[1]).qq|</td>
					<td nowrap class="help_on" valign="top" class='smalltext'>&nbsp;  (|.&format_number($report{'due'}[1]/$tot_amount*100).qq|%)</td>
				</tr>\n|;
	
			$va{'searchresults'} .= qq|
				<tr onmouseover='m_over(this)' onmouseout='m_out(this)' bgcolor='$c[$d]'>
					<td colspan="5">&nbsp;</td>
				</tr>\n|;	
	
			## FP Due (Today)
			$va{'searchresults'} .= qq|	
				<tr onmouseover='m_over(this)' onmouseout='m_out(this)' bgcolor='$c[$d]'>
					<td valign="top" class='smalltext'>&nbsp;&nbsp;&nbsp; FP Due (Today)</td>
					<td align="right" valign="top" class='smalltext'><span class='help_on'>|.&format_number($report{'due_now'}[0]).qq|</span></td>
					<td nowrap class="help_on" valign="top" class='smalltext'>&nbsp; (|.&format_number($report{'due_now'}[0]/$tot_qty*100).qq|%)</td>
					<td align="right" valign="top" nowrap class='smalltext'>|.&format_price($report{'due_now'}[1]).qq|</td>
					<td nowrap class="help_on" valign="top" class='smalltext'>&nbsp;  (|.&format_number($report{'due_now'}[1]/$tot_amount*100).qq|%)</td>
				</tr>\n|;				
		
			$va{'searchresults'} .= qq|
				<tr onmouseover='m_over(this)' onmouseout='m_out(this)' bgcolor='$c[$d]'>
					<td colspan="5">&nbsp;</td>
				</tr>\n|;	
	
			## FP AR (1-30 days)
			$va{'searchresults'} .= qq|	
				<tr onmouseover='m_over(this)' onmouseout='m_out(this)' bgcolor='$c[$d]'>
					<td valign="top" class='smalltext'>&nbsp;&nbsp;&nbsp; FP Future Payments (1-30 days)</td>
					<td align="right" valign="top" class='smalltext'><span class='help_on'>|.&format_number($report{'ar_30'}[0]).qq|</span></td>
					<td nowrap class="help_on" valign="top" class='smalltext'>&nbsp; (|.&format_number($report{'ar_30'}[0]/$tot_qty*100).qq|%)</td>
					<td align="right" valign="top" nowrap class='smalltext'>|.&format_price($report{'ar_30'}[1]).qq|</td>
					<td nowrap class="help_on" valign="top" class='smalltext'>&nbsp;  (|.&format_number($report{'ar_30'}[1]/$tot_amount*100).qq|%)</td>
				</tr>\n|;	


			## FP AR (30-60 days)
			$va{'searchresults'} .= qq|	
				<tr onmouseover='m_over(this)' onmouseout='m_out(this)' bgcolor='$c[$d]'>
					<td valign="top" class='smalltext'>&nbsp;&nbsp;&nbsp; FP Future Payments (30-60 days)</td>
					<td align="right" valign="top" class='smalltext'><span class='help_on'>|.&format_number($report{'ar_60'}[0]).qq|</span></td>
					<td nowrap class="help_on" valign="top" class='smalltext'>&nbsp; (|.&format_number($report{'ar_60'}[0]/$tot_qty*100).qq|%)</td>
					<td align="right" valign="top" nowrap class='smalltext'>|.&format_price($report{'ar_60'}[1]).qq|</td>
					<td nowrap class="help_on" valign="top" class='smalltext'>&nbsp;  (|.&format_number($report{'ar_60'}[1]/$tot_amount*100).qq|%)</td>
				</tr>\n|;	


			## FP AR (61-90 days)
			$va{'searchresults'} .= qq|	
				<tr onmouseover='m_over(this)' onmouseout='m_out(this)' bgcolor='$c[$d]'>
					<td valign="top" class='smalltext'>&nbsp;&nbsp;&nbsp; FP Future Payments (61-90 days)</td>
					<td align="right" valign="top" class='smalltext'><span class='help_on'>|.&format_number($report{'ar_90'}[0]).qq|</span></td>
					<td nowrap class="help_on" valign="top" class='smalltext'>&nbsp; (|.&format_number($report{'ar_90'}[0]/$tot_qty*100).qq|%)</td>
					<td align="right" valign="top" nowrap class='smalltext'>|.&format_price($report{'ar_90'}[1]).qq|</td>
					<td nowrap class="help_on" valign="top" class='smalltext'>&nbsp;  (|.&format_number($report{'ar_90'}[1]/$tot_amount*100).qq|%)</td>
				</tr>\n|;



			## FP AR (91 days)
			$va{'searchresults'} .= qq|	
				<tr onmouseover='m_over(this)' onmouseout='m_out(this)' bgcolor='$c[$d]'>
					<td valign="top" class='smalltext'>&nbsp;&nbsp;&nbsp; FP Future Payments (91 or more days)</td>
					<td align="right" valign="top" class='smalltext'><span class='help_on'>|.&format_number($report{'ar_91'}[0]).qq|</span></td>
					<td nowrap class="help_on" valign="top" class='smalltext'>&nbsp; (|.&format_number($report{'ar_91'}[0]/$tot_qty*100).qq|%)</td>
					<td align="right" valign="top" nowrap class='smalltext'>|.&format_price($report{'ar_91'}[1]).qq|</td>
					<td nowrap class="help_on" valign="top" class='smalltext'>&nbsp;  (|.&format_number($report{'ar_91'}[1]/$tot_amount*100).qq|%)</td>
				</tr>\n|;
		
		$va{'debugquery'} = qq|
						## FP Due (90 days)
						SELECT SUM(Amount) FROM sl_orders inner join sl_orders_payments on (sl_orders.ID_orders=sl_orders_payments.ID_orders) $cadinner $query AND Type='Credit-Card' AND (DATEDIFF(Paymentdate,Curdate())<-90 AND Paymentdate<>'0000-00-00') AND (Captured='No' OR CapDate='0000-00-00')
						## FP Due (60-90 days)
						SELECT SUM(Amount) FROM sl_orders inner join sl_orders_payments on (sl_orders.ID_orders=sl_orders_payments.ID_orders) $cadinner $query AND Type='Credit-Card' AND (DATEDIFF(Paymentdate,Curdate())<-60 AND DATEDIFF(Paymentdate,Curdate())>=-90 AND Paymentdate<>'0000-00-00') AND (Captured='No' OR CapDate='0000-00-00')
						## FP Due (31-60 days)
						SELECT SUM(Amount) FROM sl_orders inner join sl_orders_payments on (sl_orders.ID_orders=sl_orders_payments.ID_orders) $cadinner $query AND Type='Credit-Card' AND (DATEDIFF(Paymentdate,Curdate())<-30 AND DATEDIFF(Paymentdate,Curdate())>=-60 AND Paymentdate<>'0000-00-00') AND (Captured='No' OR CapDate='0000-00-00')
						## FP Due (1-30 days)
						SELECT SUM(Amount) FROM sl_orders inner join sl_orders_payments on (sl_orders.ID_orders=sl_orders_payments.ID_orders) $cadinner $query AND Type='Credit-Card' AND (DATEDIFF(Paymentdate,Curdate())<0 AND DATEDIFF(Paymentdate,Curdate())>=-30 AND Paymentdate<>'0000-00-00') AND (Captured='No' OR CapDate='0000-00-00')
						## FP Due (Today)
						SELECT SUM(Amount) FROM sl_orders inner join sl_orders_payments on (sl_orders.ID_orders=sl_orders_payments.ID_orders) $cadinner $query AND Type='Credit-Card' AND (Paymentdate=Curdate() AND Paymentdate<>'0000-00-00') AND (Captured='No' OR CapDate='0000-00-00')
						## FP AR (1-30 days)
						SELECT SUM(Amount) FROM sl_orders inner join sl_orders_payments on (sl_orders.ID_orders=sl_orders_payments.ID_orders) $cadinner $query AND Type='Credit-Card' AND (DATEDIFF(Paymentdate,Curdate())>0 AND DATEDIFF(Paymentdate,Curdate())<=30 AND Paymentdate<>'0000-00-00') AND (Captured='No' OR CapDate='0000-00-00')
						## FP AR (30-60 days)
						SELECT SUM(Amount) FROM sl_orders inner join sl_orders_payments on (sl_orders.ID_orders=sl_orders_payments.ID_orders) $cadinner $query AND Type='Credit-Card' AND (DATEDIFF(Paymentdate,Curdate())>30 AND DATEDIFF(Paymentdate,Curdate())<=60 AND Paymentdate<>'0000-00-00') AND (Captured='No' OR CapDate='0000-00-00')
						## FP AR (61-90 days)
						SELECT SUM(Amount) FROM sl_orders inner join sl_orders_payments on (sl_orders.ID_orders=sl_orders_payments.ID_orders) $cadinner $query AND Type='Credit-Card' AND (DATEDIFF(Paymentdate,Curdate())>60 AND DATEDIFF(Paymentdate,Curdate())<=90 AND Paymentdate<>'0000-00-00') AND (Captured='No' OR CapDate='0000-00-00')
						## FP AR (91 days)
						SELECT SUM(Amount) FROM sl_orders inner join sl_orders_payments on (sl_orders.ID_orders=sl_orders_payments.ID_orders) $cadinner $query  AND Type='Credit-Card' AND (DATEDIFF(Paymentdate,Curdate())>90 AND Paymentdate<>'0000-00-00') AND (Captured='No' OR CapDate='0000-00-00')
						## PAID
						SELECT SUM(Amount) FROM sl_orders inner join sl_orders_payments on (sl_orders.ID_orders=sl_orders_payments.ID_orders) $cadinner $query  AND Type='Credit-Card' AND Captured='Yes'
						## NOT FLEXIPAGO
						SELECT SUM(Amount) FROM sl_orders inner join sl_orders_payments on (sl_orders.ID_orders=sl_orders_payments.ID_orders) $cadinner $query  AND Type='Credit-Card' AND (Paymentdate='0000-00-00') AND (Captured='No' OR CapDate='0000-00-00')
						|;		
		
		
	}else{
			##No Data Found
			$va{'searchresults'} .= qq|
				<tr onmouseover='m_over(this)' onmouseout='m_out(this)' bgcolor='$c[$d]'>
					<td valign="top" class='smalltext' colspan='5' align='center'>No records Found</td>
				</tr>\n|;
	}
		
	$va{'tot_cant'} = &format_number($tot_qty);
	$va{'tot_amount'} = &format_price($tot_amount);
	$va{'matches'} = $va{'tot_cant'};
	$va{'pageslist'} = 1;

	if ($in{'print'}){
		print "Content-type: text/html\n\n";
		print &build_page('header_print.html');
		print &build_page('results_orders_base_print.html');
	}else{
		($nul,$qs) = &pages_list($in{'nh'},$script_url,1,1);
		$va{'extabtns'} = qq|<a href="javascript:prnwin('/cgi-bin/mod/[ur_application]/admin?export=1&$qs')"><img src='[va_imgurl]/[ur_pref_style]/b_xls.gif' title='Export' alt='' border='0'></a>|;
		($va{'rep1'},$va{'rep2'},$va{'rep3'},$va{'rep4'},$va{'rep5'},$va{'rep6'}) = ('off','off','on','off','off','off');
		print "Content-type: text/html\n\n";
		print &build_page('results_orders_base.html');
	}
}

sub results_orders_fpago {
# --------------------------------------------------------
# Created :  Carlos Haas 01/01/2007 6:47:28 PM
# Last Update : 
# Locked by : 
# Description :
#
#
# Last Modified on: 01/12/09 11:54:00
# Last Modified by: MCC C. Gabriel Varela S: Se filtra opcionalmente por producto.
# Last Modified RB: 10/02/09  13:11:03 -- Se modifica $cadinner por un subquery

##TODO: Todos los textos deben estar fuera del codigo y/o a traves de transtxt
##TODO: Faltan Graficos

	my ($query,$null) = @_;
	my ($d,$tot_qtyfp,$tot_fp);
	my ($cadinner);
	$cadinner="";
	($in{'id_products'}ne"") and ($cadinner=" AND 0 < (SELECT COUNT(*) FROM sl_orders_products WHERE ID_orders = sl_orders.ID_orders AND RIGHT(ID_products,6)=967763 AND Status NOT IN('Order Cancelled', 'Inactive')) ");
	my ($sth) = &Do_SQL("SELECT IF(SUM(Amount) > 0,SUM(Amount),0) FROM sl_orders inner join sl_orders_payments on (sl_orders.ID_orders=sl_orders_payments.ID_orders) $cadinner $query AND Type = 'Credit-Card' AND Amount>0");
	my ($tot_amount) = $sth->fetchrow_array;

	my ($sth) = &Do_SQL("SELECT COUNT(distinct(sl_orders.ID_orders)) FROM sl_orders inner join sl_orders_payments on (sl_orders.ID_orders=sl_orders_payments.ID_orders) $cadinner $query AND Type = 'Credit-Card' AND Amount>0");
	my ($tot_qty) = $sth->fetchrow_array;
		
	my ($sth) = &Do_SQL("SELECT num,count(num), sum(total)
					FROM (
					SELECT COUNT(*) AS num, SUM(Amount) as total FROM sl_orders inner join sl_orders_payments on (sl_orders.ID_orders=sl_orders_payments.ID_orders)
					$query AND Type = 'Credit-Card' $cadinner
					GROUP BY (sl_orders_payments.ID_orders)) as fp
					GROUP BY num");
					
	if($tot_amount == 0 and $tot_qty == 0){
			$va{'searchresults'} .= qq|
				<tr onmouseover='m_over(this)' onmouseout='m_out(this)' bgcolor='$c[$d]'>
					<td valign="top" colspan="5" align="center">Not Records Found</td>
				</tr>\n|;				
	}else{				
					
	while (@ary = $sth->fetchrow_array){
		$d = 1 - $d;
		$va{'searchresults'} .= qq|
			<tr onmouseover='m_over(this)' onmouseout='m_out(this)' bgcolor='$c[$d]'>
				<td valign="top">Orders with $ary[0] payments</td>
				<td align="right" valign="top"><span class='help_on'>|.&format_number($ary[1]).qq|</span></td>
				<td nowrap class="help_on" valign="top">&nbsp; (|.&format_number($ary[1]/$tot_qty*100).qq|%)</td>
				<td align="right" valign="top" nowrap>|.&format_price($ary[2]).qq|</td>
				<td nowrap class="help_on" valign="top">&nbsp;  (|.&format_number($ary[2]/$tot_amount*100).qq|%)</td>
			</tr>\n|;
		++$va{'matches'};
		if ($ary[0]>1){
			$tot_qtyfp += $ary[1];
			$tot_fp    += $ary[2];
		}
	}
	$va{'searchresults'} .= qq|
			<tr>
				<td colspan="4"></td>
			</tr>
			<tr onmouseover='m_over(this)' onmouseout='m_out(this)' bgcolor='$c[$d]'>
				<td valign="top">Orders with Flexipago</td>
				<td align="right" valign="top"><span class='help_on'>|.&format_number($tot_qtyfp).qq|</span></td>
				<td nowrap class="help_on" valign="top">&nbsp; (|.&format_number($tot_qtyfp/$tot_qty*100).qq|%)</td>
				<td align="right" valign="top" nowrap>|.&format_price($tot_fp).qq|</td>
				<td nowrap class="help_on" valign="top">&nbsp;  (|.&format_number($tot_fp/$tot_amount*100).qq|%)</td>
			</tr>\n|;	
	
	}
	
	$va{'tot_cant'} = &format_number($tot_qty);
	$va{'tot_amount'} = &format_price($tot_amount);
	$va{'pageslist'} = 1;
	if ($in{'print'}){
		print "Content-type: text/html\n\n";
		print &build_page('header_print.html');
		print &build_page('results_orders_base_print.html');
	}else{
		($va{'rep1'},$va{'rep2'},$va{'rep3'},$va{'rep4'},$va{'rep5'},$va{'rep6'}) = ('off','off','on','off','off','off');
		print "Content-type: text/html\n\n";
		print &build_page('results_orders_base.html');
	}
}

sub results_orders_fpmnt {
# --------------------------------------------------------
# Created :  Carlos Haas 01/01/2007 6:47:28 PM
# Last Update : 
# Locked by : 
# Description :
#
#
# Last Modified on: 01/12/09 12:12:40
# Last Modified by: MCC C. Gabriel Varela S: Se adapta para que se pueda filtrar por producto
##TODO: Todos los textos deben estar fuera del codigo y/o a traves de transtxt
##TODO: Faltan Graficos


	my ($query,$null) = @_;
	my ($d,%report,$tot_qty,$tot_amount,$qty,$amount,@cols,$unpaid);
	
	my ($cadinner);
	$cadinner="";
	$cadinner=" inner join sl_orders_products on (sl_orders.ID_orders=sl_orders_products.ID_orders and right(ID_products,6)=".int($in{'id_products'}).") " if($in{'id_products'}ne"");
	
	## Totals
	my ($sth) = &Do_SQL("SELECT SUM(OrderNet),COUNT(*) FROM sl_orders $cadinner WHERE 1<(SELECT COUNT(*) FROM sl_orders_payments WHERE ID_orders=sl_orders.ID_orders AND Type='Credit-Card') $query");
	($tot_amount,$tot_qty) = $sth->fetchrow_array();	

	####################################################
	### 20% Higher Orders
	####################################################
	my ($sth) = &Do_SQL("SELECT DISTINCT(sl_orders.ID_orders) FROM sl_orders $cadinner WHERE 1<(SELECT COUNT(*) FROM sl_orders_payments WHERE ID_orders=sl_orders.ID_orders AND Type='Credit-Card') $query ORDER BY OrderNet DESC");
	IDORDEN: while ($id = $sth->fetchrow){
		my ($sth2) = &Do_SQL("SELECT COUNT(*),SUM(Amount) FROM sl_orders_payments WHERE ID_orders='$id' AND Type='Credit-Card' AND Status IN ('Approved','Denied')");
		($payments,$tot_ord) = $sth2->fetchrow_array();		
		($payments>1) or (next IDORDEN);
		($report{'fp'}>int($tot_qty*.20)) and (last IDORDEN);
		$report{'fp_tot'.$payments} += $tot_ord;
		++$report{'fp'.$payments};
		my ($sth2) = &Do_SQL("SELECT Amount FROM sl_orders_payments WHERE ID_orders='$id' AND Type='Credit-Card' AND Status IN ('Approved','Denied') ORDER BY Paymentdate ASC LIMIT 0,1");
		$unpaid = $sth2->fetchrow();
		$report{'fp_down'.$payments} += $unpaid ;
		
		## Sub Totals
		++$report{'fp'};
		$report{'fp_down'} += $unpaid;
		$report{'fp_tot'} += $tot_ord;
	}
	(!$tot_qty) and ($tot_qty=1);
	(!$tot_amount) and ($tot_amount=1);
	(!$report{'fp_tot'}) and ($report{'fp_tot'}=1);

	$va{'searchresults'} .= qq|
		<tr bgcolor='$c[$d]'>
			<td colspan="5">20% Higher Ticket Price</td>
		</tr>\n|;
	for my $p(2..12){
		if ($report{'fp'.$p}>0){
			$va{'searchresults'} .= qq|	
			<tr onmouseover='m_over(this)' onmouseout='m_out(this)' bgcolor='$c[$d]'>
				<td valign="top" class='smalltext'>&nbsp;&nbsp;&nbsp; Payment : $p</td>
				<td align="right" valign="top" class='smalltext'><span class='help_on'>|.&format_number($report{'fp'.$p}).qq|</span></td>
				<td nowrap class="help_on" valign="top" class='smalltext'>&nbsp; (|.&format_number($report{'fp'.$p}/$tot_qty*100).qq|%)</td>
				<td align="right" valign="top" nowrap class='smalltext'>|.&format_price($report{'fp_tot'.$p}) . qq|</td>
				<td nowrap class="help_on" valign="top" class='smalltext'>&nbsp;  (|.&format_number($report{'fp_tot'.$p}/$tot_amount*100).qq|%)</td>
				<td align="right" valign="top" nowrap class='smalltext'>|. &format_price($report{'fp_down'.$p}) . qq|</td>
				<td nowrap class="help_on" valign="top" class='smalltext'>&nbsp;  (|.&format_number($report{'fp_down'.$p}/$report{'fp_tot'.$p}*100).qq|%)</td>
				<td align="right" valign="top" nowrap class='smalltext'>|. &format_price($report{'fp_tot'.$p}-$report{'fp_down'.$p}) .qq|</td>
				<td nowrap class="help_on" valign="top" class='smalltext'>&nbsp;  (|.&format_number(($report{'fp_tot'.$p}-$report{'fp_down'.$p})/$report{'fp_tot'.$p}*100).qq|%)</td>
			</tr>\n|;
		}
	}
	$va{'searchresults'} .= qq|	
			<tr onmouseover='m_over(this)' onmouseout='m_out(this)' bgcolor='$c[$d]'>
				<td valign="top" class='smalltext' align="right">&nbsp;&nbsp;&nbsp; Total</td>
				<td align="right" valign="top" class='smalltext'><span class='help_on'>|.&format_number($report{'fp'}).qq|</span></td>
				<td nowrap class="help_on" valign="top" class='smalltext'>&nbsp; (|.&format_number($report{'fp'}/$tot_qty*100).qq|%)</td>
				<td align="right" valign="top" nowrap class='smalltext'>|.&format_price($report{'fp_tot'}) .qq|</td>
				<td nowrap class="help_on" valign="top" class='smalltext'>&nbsp;  (|.&format_number($report{'fp_tot'}/$tot_amount*100).qq|%)</td>
				<td align="right" valign="top" nowrap class='smalltext'>|.&format_price($report{'fp_down'})  . qq|
				<td nowrap class="help_on" valign="top" class='smalltext'>&nbsp;  (|.&format_number($report{'fp_down'}/$report{'fp_tot'}*100).qq|%)</td>
				<td align="right" valign="top" nowrap class='smalltext'>|.&format_price($report{'fp_tot'}-$report{'fp_down'}).qq|</td>
				<td nowrap class="help_on" valign="top" class='smalltext'>&nbsp;  (|.&format_number(($report{'fp_tot'}-$report{'fp_down'})/$report{'fp_tot'}*100).qq|%)</td>
			</tr>\n|;
	

	####################################################
	### 20% Lower Orders
	####################################################
	my (%report);
	my ($sth) = &Do_SQL("SELECT DISTINCT(sl_orders.ID_orders) FROM sl_orders $cadinner WHERE 1<(SELECT COUNT(*) FROM sl_orders_payments WHERE ID_orders=sl_orders.ID_orders AND Type='Credit-Card') $query ORDER BY OrderNet ASC");
	IDORDEN: while ($id = $sth->fetchrow){
		my ($sth2) = &Do_SQL("SELECT COUNT(*),SUM(Amount) FROM sl_orders_payments WHERE ID_orders='$id' AND Type='Credit-Card' AND Status IN ('Approved','Denied')");
		($payments,$tot_ord) = $sth2->fetchrow_array();		
		($payments>1) or (next IDORDEN);
		($report{'fp'}>int($tot_qty*.20)) and (last IDORDEN);
		$report{'fp_tot'.$payments} += $tot_ord;
		++$report{'fp'.$payments};
		my ($sth2) = &Do_SQL("SELECT Amount FROM sl_orders_payments WHERE ID_orders='$id' AND Type='Credit-Card' AND Status IN ('Approved','Denied') ORDER BY Paymentdate ASC LIMIT 0,1");
		$unpaid = $sth2->fetchrow();
		$report{'fp_down'.$payments} += $unpaid ;
		
		## Sub Totals
		++$report{'fp'};
		$report{'fp_down'} += $unpaid;
		$report{'fp_tot'} += $tot_ord;
	}
	$va{'searchresults'} .= qq|
		<tr bgcolor='$c[$d]'>
			<td colspan="5">20% Lower Ticket Price</td>
		</tr>\n|;
	(!$report{'fp_tot'}) and ($report{'fp_tot'}=1);
	(!$tot_qty) and ($tot_qty=1);
	(!$tot_amount) and ($tot_amount=1);
	
	for my $p(2..12){
		if ($report{'fp'.$p}>0){
			(!$report{'fp_tot'.$p}) and ($report{'fp_tot'.$p}=1);
			$va{'searchresults'} .= qq|	
			<tr onmouseover='m_over(this)' onmouseout='m_out(this)' bgcolor='$c[$d]'>
				<td valign="top" class='smalltext'>&nbsp;&nbsp;&nbsp; Payment : $p</td>
				<td align="right" valign="top" class='smalltext'><span class='help_on'>|.&format_number($report{'fp'.$p}).qq|</span></td>
				<td nowrap class="help_on" valign="top" class='smalltext'>&nbsp; (|.&format_number($report{'fp'.$p}/$tot_qty*100).qq|%)</td>
				<td align="right" valign="top" nowrap class='smalltext'>|.&format_price($report{'fp_tot'.$p}) . qq|</td>
				<td nowrap class="help_on" valign="top" class='smalltext'>&nbsp;  (|.&format_number($report{'fp_tot'.$p}/$tot_amount*100).qq|%)</td>
				<td align="right" valign="top" nowrap class='smalltext'>|. &format_price($report{'fp_tot'.$p}-$report{'fp_down'.$p}) . qq|</td>
				<td nowrap class="help_on" valign="top" class='smalltext'>&nbsp;  (|.&format_number(($report{'fp_tot'.$p}-$report{'fp_down'.$p})/$report{'fp_tot'.$p}*100).qq|%)</td>
				<td align="right" valign="top" nowrap class='smalltext'>|. &format_price($report{'fp_down'.$p}) .qq|</td>
				<td nowrap class="help_on" valign="top" class='smalltext'>&nbsp;  (|.&format_number($report{'fp_down'.$p}/$report{'fp_tot'.$p}*100).qq|%)</td>
			</tr>\n|;
		}
	}
	$va{'searchresults'} .= qq|	
			<tr onmouseover='m_over(this)' onmouseout='m_out(this)' bgcolor='$c[$d]'>
				<td valign="top" class='smalltext' align="right">&nbsp;&nbsp;&nbsp; Total</td>
				<td align="right" valign="top" class='smalltext'><span class='help_on'>|.&format_number($report{'fp'}).qq|</span></td>
				<td nowrap class="help_on" valign="top" class='smalltext'>&nbsp; (|.&format_number($report{'fp'}/$tot_qty*100).qq|%)</td>
				<td align="right" valign="top" nowrap class='smalltext'>|.&format_price($report{'fp_tot'}) .qq|</td>
				<td nowrap class="help_on" valign="top" class='smalltext'>&nbsp;  (|.&format_number($report{'fp_tot'}/$tot_amount*100).qq|%)</td>
				<td align="right" valign="top" nowrap class='smalltext'>|.&format_price($report{'fp_tot'}-$report{'fp_down'})  . qq|
				<td nowrap class="help_on" valign="top" class='smalltext'>&nbsp;  (|.&format_number(($report{'fp_tot'}-$report{'fp_down'})/$report{'fp_tot'}*100).qq|%)</td>
				<td align="right" valign="top" nowrap class='smalltext'>|.&format_price($report{'fp_down'}).qq|</td>
				<td nowrap class="help_on" valign="top" class='smalltext'>&nbsp;  (|.&format_number($report{'fp_down'}/$report{'fp_tot'}*100).qq|%)</td>
			</tr>\n|;
		
	$va{'tot_cant'} = &format_number($tot_qty);
	$va{'tot_amount'} = &format_price($tot_amount);
	$va{'matches'} = $va{'tot_cant'};
	$va{'pageslist'} = 1;

	if ($in{'print'}){
		print "Content-type: text/html\n\n";
		print &build_page('header_print.html');
		print &build_page('results_orders_amns_print.html');
	}else{
		($va{'rep1'},$va{'rep2'},$va{'rep3'},$va{'rep4'},$va{'rep5'},$va{'rep6'}) = ('off','off','on','off','off','off');
		print "Content-type: text/html\n\n";
		print &build_page('results_orders_amns.html');
	}
}

sub results_orders_cust {
# --------------------------------------------------------
# Created :  Carlos Haas 01/01/2007 6:47:28 PM
# Last Update : 
# Locked by : 
# Description :
# Last Time Modified by RB on 10/05/2010 : Se agregan charts
##TODO: Todos los textos deben estar fuera del codigo y/o a traves de transtxt


	my ($query_tot,$query_list) = @_;
	my ($sth) = &Do_SQL($query_tot);
	my ($tot_cant,$tot_amount) = $sth->fetchrow_array();
	
	if ($tot_cant>0 and $tot_amount>0){
		(!$in{'nh'}) and ($in{'nh'}=1);
		$first = ($in{'nh'} - 1) * $usr{'pref_maxh'};	
		my ($sth) = &Do_SQL("$query_list");
		$va{'matches'} = $sth->rows;
		($va{'pageslist'},$qs) = &pages_list($in{'nh'},"/cgi-bin/mod/$usr{'application'}/admin",$va{'matches'},$usr{'pref_maxh'});
		my ($sth) = &Do_SQL($query_list ." LIMIT $first,$usr{'pref_maxh'}");
		while (@ary = $sth->fetchrow_array){
			$va{'searchresults'} .= qq|
				<tr>
					<td>$ary[0]</td>
					<td align="right">|.&format_number($ary[1]).qq|</td>
					<td nowrap class="help_on">&nbsp; (|.&format_number($ary[1]/$tot_cant*100).qq| %)</td>
					<td align="right">|.&format_price($ary[2]).qq|</td>
					<td nowrap class="help_on">&nbsp; (|.&format_number($ary[2]/$tot_amount*100).qq| %)</td>
				</tr>\n|;

			###### Amount / Quantity Bar
			if($in{'groupby'} eq 'id_products'){
				$va{'xaxis_categories'} .= "'". substr($ary[0],8,15) ."',";
			}else{
				$va{'xaxis_categories'} .= "'$ary[0]',";
			}
			$series_quantity .= $ary[1] . ',';
			$series_amount .= round($ary[2],2) .',';
			
			($in{'groupby'} eq 'id_admin_users') and ($ary[0] = &load_name('admin_users','ID_admin_users',substr($ary[0],0,4),"CONCAT(FirstName,' ',LEFT(LastName,1))"));
			###### Amount / Quantity Pie		
			$series_quantityp .= "['$ary[0]', ". round($ary[1]/$tot_cant,2) * 100 ."],";
			$series_amountp .= "['$ary[0]', ". round($ary[2]/$tot_amount,2) * 100 ."],";

		}
		$va{'tot_cant'} = $tot_cant;
		$va{'tot_amount'} = &format_price($tot_amount);

		(!$in{'chart_theme'}) and ($in{'chart_theme'} = 'gray');
		$va{'highchart_theme'} = ($in{'chart_theme'} eq 'blank') ? '' : &build_page('func/highcharts_theme_'. $in{'chart_theme'} .'.html');
		##### Amount / Quantity Bar
		chop($va{'xaxis_categories'});
		chop($series_quantity);
		chop($series_amount);

		my $xaxis_mod = ",title: { text: '$in{'groupby'}' } ";
		my $chart_mod= '';
		if($sth->rows() > 5){
			$xaxis_mod = ",labels: {rotation: -45, align: 'right', style: { font: 'normal 13px Verdana, sans-serif'}} ";
			$chart_mod = ',height: 450, margin: [ 50, 50, 150, 100]';
		}
		
		$va{'chart_options'} = "renderTo: 'container1', defaultSeriesType: 'line' $chart_mod ";
		$va{'chart_title'} = 'Report By Products';
		$va{'chart_subtitle'} = $va{'report_name'};
		$va{'chart_xaxis'} = "categories: [$va{'xaxis_categories'}] $xaxis_mod ";
		$va{'chart_yaxis'} = "title: { text: 'Quantity / Amount', margin: 70 }";
		$va{'chart_tooltip'} = "enabled: true,formatter: function() {return '<b>'+ this.series.name +'</b><br/>'+this.x +': '+ this.y;}";
		$va{'series_data'} = "{ name: 'Quantity', data: [$series_quantity]}, { name: 'Amount', data: [$series_amount] }";
		$va{'highchart1'} = &build_page('func/construct_highcharts.html');
		
		
		###### Amount / Quantity Pie
		chop($series_quantityp);
		chop($series_amountp);


		## Pie Quantity
		$va{'chart_options'} = "renderTo: 'container2', margin: [50, 150, 10, 5], width: 400";
		$va{'chart_title'} = 'Quantity';
		$va{'chart_subtitle'} = 'Percentages';
		$va{'chart_plotarea'} = 'shadow: null, borderWidth: null, backgroundColor: null';
		$va{'chart_tooltip'} = "enabled: true,formatter: function() { return '<b>'+ this.point.name +'</b>: '+ this.y +' %';}";
		$va{'chart_plotoptions'} = "pie: {
							allowPointSelect: true,
							cursor: 'pointer',
							dataLabels: {
								enabled: true,
								formatter: function() {
									if (this.y > 50) return this.point.name;
								},
								color: 'white',
								style: {
									font: '13px Trebuchet MS, Verdana, sans-serif'
								}
							}
						}";
		$va{'chart_legend'} = "layout: 'vertical', style: { left: 'auto', bottom: 'auto', right: '10px', top: '50px' }";
		$va{'series_data'} = "{ type: 'pie', name: 'Quantity Percentages ', data: [$series_quantityp] }";
		$va{'highchart2'} = &build_page('func/construct_highcharts.html');
		

		## Pie Amount
		$va{'chart_options'} = "renderTo: 'container3', margin: [50, 150, 10, 5], width: 400";
		$va{'chart_title'} = 'Amount';
		$va{'series_data'} = "{ type: 'pie', name: 'Quantity Percentages ', data: [$series_amountp] }";
		$va{'highchart3'} = &build_page('func/construct_highcharts.html');

		
		###### Charge the js scripts if not charged
		if(!$va{'highcharts_js'}){
			$va{'highcharts_js'} = &build_page('func/highcharts_js.html');
		}

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
		print &build_page('results_orders_base_print.html');
	}else{
		print "Content-type: text/html\n\n";
		print &build_page('results_orders_base.html');
	}
}

sub results_orders_usr {
# --------------------------------------------------------
# Created :  Carlos Haas 01/01/2007 6:47:28 PM
# Last Update : 
# Locked by : 
# Description :
#
#
	my ($query_tot,$query_list) = @_;
	my ($sth) = &Do_SQL($query_tot);
	my ($tot_cant,$tot_amount) = $sth->fetchrow_array();
	
	if ($tot_cant>0 and $tot_amount>0){
		(!$in{'nh'}) and ($in{'nh'}=1);
		$first = ($in{'nh'} - 1) * $usr{'pref_maxh'};	
		my ($sth) = &Do_SQL($query_list);
		$va{'matches'} = $sth->rows;
		($va{'pageslist'},$qs) = &pages_list($in{'nh'},"/cgi-bin/mod/$usr{'application'}/admin",$va{'matches'},$usr{'pref_maxh'});
		my ($sth) = &Do_SQL($query_list ." LIMIT $first,$usr{'pref_maxh'}");
		while (@ary = $sth->fetchrow_array){
			$va{'searchresults'} .= qq|
				<tr>
					<td>$ary[0]</td>
					<td align="right">|.&format_number($ary[1]).qq|</td>
					<td nowrap class="help_on">&nbsp; (|.&format_number($ary[1]/$tot_cant*100).qq| %)</td>
					<td align="right">|.&format_price($ary[2]).qq|</td>
					<td nowrap class="help_on">&nbsp; (|.&format_number($ary[2]/$tot_amount*100).qq| %)</td>
				</tr>\n|;

			###### Amount / Quantity Bar
			if($in{'groupby'} eq 'id_products'){
				$va{'xaxis_categories'} .= "'". substr($ary[0],8,15) ."',";
			}else{
				$va{'xaxis_categories'} .= "'$ary[0]',";
			}
			$series_quantity .= $ary[1] . ',';
			$series_amount .= round($ary[2],2) .',';
			
			($in{'groupby'} eq 'id_products') and ($ary[0] = $id_product);
			###### Amount / Quantity Pie		
			$series_quantityp .= "['$ary[0]', ". round($ary[1]/$tot_cant,2) * 100 ."],";
			$series_amountp .= "['$ary[0]', ". round($ary[2]/$tot_amount,2) * 100 ."],";

		}
		$va{'tot_cant'} = $tot_cant;
		$va{'tot_amount'} = &format_price($tot_amount);

		(!$in{'chart_theme'}) and ($in{'chart_theme'} = 'gray');
		$va{'highchart_theme'} = ($in{'chart_theme'} eq 'blank') ? '' : &build_page('func/highcharts_theme_'. $in{'chart_theme'} .'.html');
		##### Amount / Quantity Bar
		chop($va{'xaxis_categories'});
		chop($series_quantity);
		chop($series_amount);

		my $xaxis_mod = ",title: { text: '$in{'groupby'}' } ";
		my $chart_mod= '';
		if($sth->rows() > 5){
			$xaxis_mod = ",labels: {rotation: -45, align: 'right', style: { font: 'normal 13px Verdana, sans-serif'}} ";
			$chart_mod = ',height: 450, margin: [ 50, 50, 150, 100]';
		}
		
		$va{'chart_options'} = "renderTo: 'container1', defaultSeriesType: 'bar' $chart_mod ";
		$va{'chart_title'} = 'Report By Products';
		$va{'chart_subtitle'} = $va{'report_name'};
		$va{'chart_xaxis'} = "categories: [$va{'xaxis_categories'}] $xaxis_mod ";
		$va{'chart_yaxis'} = "title: { text: 'Quantity / Amount', margin: 75 }";
		$va{'chart_tooltip'} = "enabled: true,formatter: function() {return '<b>'+ this.series.name +'</b><br/>'+this.x +': '+ this.y;}";
		$va{'series_data'} = "{ name: 'Quantity', data: [$series_quantity]}, { name: 'Amount', data: [$series_amount] }";
		$va{'highchart1'} = &build_page('func/construct_highcharts.html');
		
		
		###### Amount / Quantity Pie
		chop($series_quantityp);
		chop($series_amountp);


		## Pie Quantity
		$va{'chart_options'} = "renderTo: 'container2', margin: [50, 150, 10, 5], width: 400";
		$va{'chart_title'} = 'Quantity';
		$va{'chart_subtitle'} = 'Percentages';
		$va{'chart_plotarea'} = 'shadow: null, borderWidth: null, backgroundColor: null';
		$va{'chart_tooltip'} = "enabled: true,formatter: function() { return '<b>'+ this.point.name +'</b>: '+ this.y +' %';}";
		$va{'chart_plotoptions'} = "pie: {
							allowPointSelect: true,
							cursor: 'pointer',
							dataLabels: {
								enabled: true,
								formatter: function() {
									if (this.y > 50) return this.point.name;
								},
								color: 'white',
								style: {
									font: '13px Trebuchet MS, Verdana, sans-serif'
								}
							}
						}";
		$va{'chart_legend'} = "layout: 'vertical', style: { left: 'auto', bottom: 'auto', right: '10px', top: '50px' }";
		$va{'series_data'} = "{ type: 'pie', name: 'Quantity Percentages ', data: [$series_quantityp] }";
		$va{'highchart2'} = &build_page('func/construct_highcharts.html');
		

		## Pie Amount
		$va{'chart_options'} = "renderTo: 'container3', margin: [50, 150, 10, 5], width: 400";
		$va{'chart_title'} = 'Amount';
		$va{'series_data'} = "{ type: 'pie', name: 'Quantity Percentages ', data: [$series_amountp] }";
		$va{'highchart3'} = &build_page('func/construct_highcharts.html');

		
		###### Charge the js scripts if not charged
		if(!$va{'highcharts_js'}){
			$va{'highcharts_js'} = &build_page('func/highcharts_js.html');
		}

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
		print &build_page('results_orders_base_print.html');
	}else{
		print "Content-type: text/html\n\n";
		print &build_page('results_orders_base.html');
	}
}

sub results_orders_amtrange{
#-----------------------------------------
# Forms Involved: 
# Created on: 07/24/08  14:36:28
# Last Modified on: 07/24/08  14:36:28
# Last Modified by: Roberto Barcenas
# Last Modified Desc:
# Author: Roberto Barcenas based on CH fpmnt
# Description : Split into ranges the current order fp balance 
# Parameters : $query previously made and sended by rep_orders_pay
# Last Modified on: 01/12/09 12:13:58
# Last Modified by: MCC C. Gabriel Varela S: Se adapta para filtrar por producto
##TODO: Todos los textos deben estar fuera del codigo y/o a traves de transtxt
##TODO: Faltan Graficos

	my ($query,$null) = @_;
	my ($flag,$amtorder,$amtpaid,$amtfinanced,$amtoncollection,$amtupaid,%orders,$tot_qty,$tot_amt,$str);
	$flag=0;
	
	my ($cadinner);
	$cadinner="";
	$cadinner=" inner join sl_orders_products on (sl_orders.ID_orders=sl_orders_products.ID_orders and right(ID_products,6)=".int($in{'id_products'}).") " if($in{'id_products'}ne"");
	
	## Totals
	my ($sth) = &Do_SQL("SELECT sl_orders.ID_orders,sl_orders.Date FROM sl_orders $cadinner WHERE 1<(SELECT COUNT(*) FROM sl_orders_payments WHERE ID_orders=sl_orders.ID_orders AND Type='Credit-Card') $query");
	while($rec = $sth->fetchrow_hashref){

			$amtorder = 0;
			$amtpaid  = 0;
			$amtfinanced = 0;
			$amtoncollection = 0;
			$amtupaid = 0;

			my ($sth2) = 	&Do_SQL("SELECT * FROM sl_orders_payments WHERE ID_orders = '$rec->{'ID_orders'}' AND Status NOT IN ('Credit','ChargeBack','Void','Order Cancelled','Cancelled') ORDER BY PaymentDate");
			while($paym = $sth2->fetchrow_hashref){
			
					### Order total
					$amtorder += $paym->{'Amount'};
									
					## Paid
					if($paym->{'AuthCode'} and $paym->{'AuthCode'} ne '0000' and $paym->{'Captured'} ne 'Yes'){
							$amtpaid += $paym->{'Amount'};
					## Financed
					}elsif($paym->{'Status'} eq 'Financed'){
							$amtfinanced += $paym->{'Amount'};
					## On Colection
					}elsif($paym->{'Status'} eq 'On Collection'){
							$amtoncollection += $paym->{'Amount'};
					## Unpaid
					}else{
							$amtupaid += $paym->{'Amount'};
					}
			}
	
				
			$str .="$rec->{'ID_orders'},$rec->{'Date'},$amtorder,$amtpaid,$amtfinanced,$amtoncollection,$amtupaid\n";
			
			## Range 01 - 500 USD
			if($amtorder <= 500){
					$orders{'range1_count'}++;
					$orders{'range1'}[0] += $amtpaid;
					$orders{'range1'}[1] += $amtfinanced;
					$orders{'range1'}[2] += $amtoncollection;
					$orders{'range1'}[3] += $amtupaid;
			## Range 501 - 1000	
			}elsif($amtorder > 500 and $amtorder <= 1000){
					
					$orders{'range2_count'}++;
					$orders{'range2'}[0] += $amtpaid;
					$orders{'range2'}[1] += $amtfinanced;
					$orders{'range2'}[2] += $amtoncollection;
					$orders{'range2'}[3] += $amtupaid;
					## Range 1001 - 1500	
			}elsif($amtorder > 1000 and $amtorder <= 1500){
						
					$orders{'range3_count'}++;
					$orders{'range3'}[0] += $amtpaid;
					$orders{'range3'}[1] += $amtfinanced;
					$orders{'range3'}[2] += $amtoncollection;
					$orders{'range3'}[3] += $amtupaid;
			## Range 1501 - 2500	
			}elsif($amtorder > 1501 and $amtorder <= 2500){
					
					$orders{'range4_count'}++;
					$orders{'range4'}[0] += $amtpaid;
					$orders{'range4'}[1] += $amtfinanced;
					$orders{'range4'}[2] += $amtoncollection;
					$orders{'range4'}[3] += $amtupaid;
			## Range > 2500	
			}elsif($amtorder > 2500 ){
						
					$orders{'range5_count'}++;
					$orders{'range5'}[0] += $amtpaid;
					$orders{'range5'}[1] += $amtfinanced;
					$orders{'range5'}[2] += $amtoncollection;
					$orders{'range5'}[3] += $amtupaid;		
			}
			$orders{'total_amt'} += $amtorder;
			$orders{'total_qty'}++;
	}
	
	$orders{'range1_header'} = 'Less than 500';		
	$orders{'range2_header'} = '501 to 1000';		
	$orders{'range3_header'} = '1001 to 1500';
	$orders{'range4_header'} = '1501 to 2500';
	$orders{'range5_header'} = 'More than 2500';
		
		
	for(1..5){
		
		if($orders{'total_amt'} > 0){
			$flag = 1;
			
			$va{'searchresults'} .= qq|	
					<tr onmouseover='m_over(this)' onmouseout='m_out(this)' bgcolor='$c[$d]'>
						<td valign="top" class='smalltext' align="right">&nbsp;&nbsp;&nbsp; $orders{'range'.$_.'_header'}</td>
						<td align="right" valign="top" class='smalltext'><span class='help_on'>|.&format_number($orders{'range'.$_.'_count'}).qq|</span></td>
						<td nowrap class="help_on" valign="top" class='smalltext'>&nbsp; (|.&format_number($orders{'range'.$_.'_count'}/$orders{'total_qty'}*100).qq|%)</td>
						<td align="right" valign="top" nowrap class='smalltext'>|.&format_price($orders{'range'.$_.''}[0]) .qq| </td>
						<td nowrap class="help_on" valign="top" class='smalltext'>&nbsp;  (|.&format_number($orders{'range'.$_.''}[0]/$orders{'total_amt'}*100).qq|%)</td>
						<td align="right" valign="top" nowrap class='smalltext'>|.&format_price($orders{'range'.$_.''}[1]) .qq| </td>
						<td nowrap class="help_on" valign="top" class='smalltext'>&nbsp;  (|.&format_number($orders{'range'.$_.''}[1]/$orders{'total_amt'}*100).qq|%)</td>
						<td align="right" valign="top" nowrap class='smalltext'>|.&format_price($orders{'range'.$_.''}[2]) .qq| </td>
						<td nowrap class="help_on" valign="top" class='smalltext'>&nbsp;  (|.&format_number($orders{'range'.$_.''}[2]/$orders{'total_amt'}*100).qq|%)</td>
						<td align="right" valign="top" nowrap class='smalltext'>|.&format_price($orders{'range'.$_.''}[3]) .qq| </td>
						<td nowrap class="help_on" valign="top" class='smalltext'>&nbsp;  (|.&format_number($orders{'range'.$_.''}[3]/$orders{'total_amt'}*100).qq|%)</td>
					</tr>\n|;
		
		}else{
			$va{'searchresults'} .= qq|
				<tr onmouseover='m_over(this)' onmouseout='m_out(this)' bgcolor='$c[$d]'>
					<td valign="top" colspan="12">No data found</td>
				</tr>|;	
		}
	}
	
	if($flag == 1){
	
			$va{'searchresults'} .= qq|	
					<tr onmouseover='m_over(this)' onmouseout='m_out(this)' bgcolor='$c[$d]'>
						<td valign="top" class='smalltext' align="right">&nbsp;&nbsp;&nbsp; Total</td>
						<td align="right" valign="top" class='smalltext'><span class='help_on'>|.&format_number($orders{'total_qty'}).qq|</span></td>
						<td nowrap class="help_on" valign="top" class='smalltext'>&nbsp; (|.&format_number($orders{'total_qty'}/$orders{'total_qty'}*100).qq|%)</td>
						<td align="right" valign="top" nowrap class='smalltext'>|.&format_price($orders{'range1'}[0]+$orders{'range2'}[0]+$orders{'range3'}[0]+$orders{'range4'}[0]+$orders{'range5'}[0]) .qq| </td>
						<td nowrap class="help_on" valign="top" class='smalltext'>&nbsp;  (|.&format_number(($orders{'range1'}[0]+$orders{'range2'}[0]+$orders{'range3'}[0]+$orders{'range4'}[0]+$orders{'range5'}[0])/$orders{'total_amt'}*100).qq|%)</td>
						<td align="right" valign="top" nowrap class='smalltext'>|.&format_price($orders{'range1'}[1]+$orders{'range2'}[1]+$orders{'range3'}[1]+$orders{'range4'}[1]+$orders{'range5'}[1]) .qq| </td>
						<td nowrap class="help_on" valign="top" class='smalltext'>&nbsp;  (|.&format_number(($orders{'range1'}[1]+$orders{'range2'}[1]+$orders{'range3'}[1]+$orders{'range4'}[1]+$orders{'range5'}[1])/$orders{'total_amt'}*100).qq|%)</td>
						<td align="right" valign="top" nowrap class='smalltext'>|.&format_price($orders{'range1'}[2]+$orders{'range2'}[2]+$orders{'range3'}[2]+$orders{'range4'}[2]+$orders{'range5'}[2]) .qq| </td>
						<td nowrap class="help_on" valign="top" class='smalltext'>&nbsp;  (|.&format_number(($orders{'range1'}[2]+$orders{'range2'}[2]+$orders{'range3'}[2]+$orders{'range4'}[2]+$orders{'range5'}[2])/$orders{'total_amt'}*100).qq|%)</td>
						<td align="right" valign="top" nowrap class='smalltext'>|.&format_price($orders{'range1'}[3]+$orders{'range2'}[3]+$orders{'range3'}[3]+$orders{'range4'}[3]+$orders{'range5'}[3]) .qq| </td>
						<td nowrap class="help_on" valign="top" class='smalltext'>&nbsp;  (|.&format_number(($orders{'range1'}[3]+$orders{'range2'}[3]+$orders{'range3'}[3]+$orders{'range4'}[3]+$orders{'range5'}[3])/$orders{'total_amt'}*100).qq|%)</td>
					</tr>\n|;
		}
	
	$va{'tot_cant'} = $orders{'total_qty'};
	$va{'tot_amount'} = &format_price($orders{'total_amt'});
	$va{'matches'} = $va{'tot_cant'};
	$va{'pageslist'} = 1;

	if ($in{'print'}){
			print "Content-type: application/vnd.ms-excel\n";
			print "Content-disposition: attachment; filename=fpranges_$in{'from_date'}.csv\n\n";
			my (@cols) = ("ID Order","Date","Initial Balance","Paid","Financed","On Collection","Unpaid");
			print '"'.join('","',@cols) . "\"\n";
			print "$str";
	}else{
		($va{'rep1'},$va{'rep2'},$va{'rep3'},$va{'rep4'},$va{'rep5'},$va{'rep6'}) = ('off','off','on','off','off','off');
		print "Content-type: text/html\n\n";
		print &build_page('results_orders_amtrange.html');
	}
}

###################################################################
#########  ????
###################################################################

sub results_orders_dayut {
# --------------------------------------------------------
# Created :  Carlos Haas 01/01/2007 6:47:28 PM
# Last Update : 
# Locked by : 
# Description :
#
#
##TODO: Todos los textos deben estar fuera del codigo y/o a traves de transtxt
##TODO: Faltan Graficos

	my ($query,$null) = @_;
	my ($choices,%tmp,$sb);
	if ($in{'sortby'}){
		$sb = "ORDER BY $in{'sortby'} $in{'sortorder'}";
	}
	$va{'col1'} = "Orders";
	$va{'col2'} = "Sales";
	$va{'col3'} = "Profit";

	my ($sth) = &Do_SQL("SELECT COUNT(*),SUM(OrderNet+OrderShp-OrderDisc+OrderNet*OrderTax) FROM  sl_customers,sl_orders $query");
	my ($tot_cant,$tot_amount) = $sth->fetchrow_array();


	
	if ($tot_cant>0 and $tot_amount>0){
		(!$in{'nh'}) and ($in{'nh'}=1);
		$first = ($in{'nh'} - 1) * $usr{'pref_maxh'};	
		my ($sth) = &Do_SQL("SELECT sl_orders.Date,COUNT(DISTINCT(sl_orders.ID_orders)) AS nums,SUM(OrderNet+OrderShp-OrderDisc+OrderNet*OrderTax) AS amounts FROM  sl_customers,sl_orders $query GROUP BY sl_orders.Date $sb ");
		$va{'matches'} = $sth->rows;
		($va{'pageslist'},$qs) = &pages_list($in{'nh'},"/cgi-bin/mod/$usr{'application'}/admin",$va{'matches'},$usr{'pref_maxh'});
		if ($in{'print'}){
			$sth = &Do_SQL("SELECT sl_orders.Date,COUNT(DISTINCT(sl_orders.ID_orders)) AS nums,SUM(OrderNet+OrderShp-OrderDisc+OrderNet*OrderTax) AS amounts FROM  sl_customers,sl_orders $query GROUP BY sl_orders.Date $sb ");
		}else{
			$sth = &Do_SQL("SELECT sl_orders.Date,COUNT(DISTINCT(sl_orders.ID_orders)) AS nums,SUM(OrderNet+OrderShp-OrderDisc+OrderNet*OrderTax) AS amounts FROM  sl_customers,sl_orders $query GROUP BY sl_orders.Date $sb  LIMIT $first,$usr{'pref_maxh'}");
		}
		my (@c) = split(/,/,$cfg{'srcolors'});
		while (@ary = $sth->fetchrow_array){
			$d = 1 - $d;
			$sth2 = &Do_SQL("SELECT SUM((SELECT SLTV_NetCost*Quantity FROM sl_products WHERE ID_products=RIGHT(sl_orders_products.ID_products,6))*Quantity) FROM sl_orders,sl_orders_products WHERE sl_orders.ID_orders=sl_orders_products.ID_orders AND sl_orders.Date='$ary[0]'");
			$sltv_netcost = $sth2->fetchrow;
			$tot_cost += $sltv_netcost;
			$va{'searchresults'} .= qq|
				<tr onmouseover='m_over(this)' onmouseout='m_out(this)' bgcolor='$c[$d]'>
					<td class='lnk_spec'>$ary[0]</td>
					<td align="right" valign="top">|.&format_number($ary[1]).qq|</td>
					<td nowrap class="help_on" valign="top">&nbsp; (|.&format_number($ary[1]/$tot_cant*100).qq| %)</td>
					<td align="right" valign="top" nowrap>|.&format_price($ary[2]).qq|</td>
					<td nowrap class="help_on" valign="top">&nbsp; (|.&format_number($ary[1]/$tot_cant*100).qq| %)</td>
					<td align="right" valign="top" nowrap>|.&format_price($ary[2]-$sltv_netcost).qq|</td>
					<td nowrap class="help_on" valign="top">&nbsp; (|.&format_number($ary[2]/$tot_amount*100).qq| %)</td>
				</tr>\n|;
			#$tot_cost       += $tmp{'sltv_netcost'}*$ary[1];	
		}
		$va{'tot_cant'} = $tot_cant;
		$va{'tot_amount'} = &format_price($tot_amount);
		
		
		$part = ($tot_cost * 100)/ $tot_amount;
		$part = sprintf("%.0f", $part);	
		$part2 =(($tot_amount-$tot_cost) * 100)/ $tot_amount;
		$part2 = sprintf("%.0f", $part2);	
		$va{'totinfo'} = qq|
					<tr>
						<td>Total Cost:</td>
						<td align="right" nowrap><u>|. &format_price(-$tot_cost).qq|</u></td>
						<td align="right" nowrap>(|. $part.qq| %)</td>
					</tr>
						<tr>
						<td>Total Utility:</td>
						<td align="right" nowrap>|. &format_price($tot_amount-$tot_cost).qq|</td>
						<td align="right" nowrap>(|. $part2.qq| %)</td>
					</tr>\n|;
		
		
		
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
		print &build_page('results_orders_dbl_print.html');
	}else{
		print "Content-type: text/html\n\n";
		print &build_page('results_orders_dbl.html');
	}
}

sub results_orders_fppaid{
#-----------------------------------------
# Forms Involved: 
# Created on: 07/25/08  10:39:03
# Last Modified on: 07/30/08  17:47:15
# Last Modified by: Roberto Barcenas
# Last Modified Desc: The report was changed to present now a table
# Author: Roberto Barcenas
# Description : Graphics the payments
# Parameters : 
# Last Modified on: 01/12/09 12:15:31
# Last Modified by: MCC C. Gabriel Varela S: Se adapta para filtrar por producto
# Last Modified on: 02/03/09 17:51:40
# Last Modified by: MCC C. Gabriel Varela S: Se corrige para contar de forma correcta los pagos pagados.
##TODO: Todos los textos deben estar fuera del codigo y/o a traves de transtxt
##TODO: Faltan Graficos

	my ($query,$null) = @_;
	my ($today,$amtpaid,$amtfinanced,$amtoncollection,$amtar,$amtupaid,%payments,$tot_qty,$tot_amt,$str,$fppaid,$fpupaid,$fp,$maxfp);
	$maxfp = 0;
	
	my ($sth) = &Do_SQL("SELECT UNIX_TIMESTAMP( CURDATE( ) )");
	($today) = $sth->fetchrow;
	
	my ($cadinner);
	$cadinner="";
	$cadinner=" inner join sl_orders_products on (sl_orders.ID_orders=sl_orders_products.ID_orders and right(ID_products,6)=".int($in{'id_products'}).") " if($in{'id_products'}ne"");
	
	## Totals
	my ($sth) = &Do_SQL("SELECT sl_orders.ID_orders,sl_orders.Date FROM sl_orders $cadinner WHERE 1<(SELECT COUNT(*) FROM sl_orders_payments WHERE ID_orders=sl_orders.ID_orders AND Type='Credit-Card') $query");
	while($rec = $sth->fetchrow_hashref){

			my (@order);
			$amtorder = 0;
			$amtpaid  = 0;
			$amtfinanced = 0;
			$amtoncollection = 0;
			$amtar = 0;
			$amtupaid = 0;
			$fp=0;
			my ($sth2) = 	&Do_SQL("SELECT *,UNIX_TIMESTAMP(Paymentdate)as pdate FROM sl_orders_payments WHERE ID_orders = '$rec->{'ID_orders'}' AND Status NOT IN ('Credit','ChargeBack','Void','Order Cancelled','Cancelled') ORDER BY PaymentDate");
			while($paym = $sth2->fetchrow_hashref){
			
					### Felxpays in order
					$fp++;
					### Order total
					$amtorder += $paym->{'Amount'};
									
					## Paid
					if($paym->{'AuthCode'}ne"" and $paym->{'AuthCode'} ne '0000' and $paym->{'Captured'} eq 'Yes' and $paym->{'Status'}eq"Approved"){
							push (@order, 'fppaid');
							#$order[$fp-1] = 'fppaid';
							$amtpaid += $paym->{'Amount'};
							$payments{'file_'.$rec->{'ID_orders'}.'_'.$fp} = $paym->{'Amount'} * -1;
							$payments{'id_'.$rec->{'ID_orders'}.'_'.$fp} = $paym->{'Amount'} * -1;
					## Financed
					}elsif($paym->{'Status'} eq 'Financed'){
							push (@order, 'fpfinanced');
							$amtfinanced += $paym->{'Amount'};
							if($paym->{'pdate'} < $today){
									$payments{'file_'.$rec->{'ID_orders'}.'_'.$fp} = $paym->{'Amount'};
									$payments{'id_'.$rec->{'ID_orders'}.'_'.$fp} = $paym->{'Amount'};	
							}else{
									$payments{'file_'.$rec->{'ID_orders'}.'_'.$fp} = "";
									$payments{'id_'.$rec->{'ID_orders'}.'_'.$fp} = $paym->{'Amount'};
							}
					## On Colection
					}elsif($paym->{'Status'} eq 'On Collection'){
							push (@order, 'fponcollection');
							$amtoncollection += $paym->{'Amount'};
							$payments{'file_'.$rec->{'ID_orders'}.'_'.$fp} = $paym->{'Amount'};
							$payments{'id_'.$rec->{'ID_orders'}.'_'.$fp} = $paym->{'Amount'};
					## A/R
					}elsif($paym->{'pdate'} > $today){
							push (@order, 'fpar');
							$amtar += $paym->{'Amount'};
							$payments{'file_'.$rec->{'ID_orders'}.'_'.$fp} = "";
							$payments{'id_'.$rec->{'ID_orders'}.'_'.$fp} = $paym->{'Amount'};	
					## Unpaid
					}else{
							push (@order, 'fpunpaid');
							$amunpaid += $paym->{'Amount'};
							$payments{'file_'.$rec->{'ID_orders'}.'_'.$fp} = $paym->{'Amount'};
							$payments{'id_'.$rec->{'ID_orders'}.'_'.$fp} = $paym->{'Amount'};

					}
			}
			
			($fp > $maxfp) and ($maxfp = $fp);	
			## String for the file				
			$str .="\n$rec->{'ID_orders'},$rec->{'Date'},$amtorder,FP:$fp";
			for(1..$fp){
					$str .= ",".$payments{'file_'.$rec->{'ID_orders'}.'_'.$_};
			}
			####
								
			
			## Range 01 - 500 USD
			if($amtorder <= 500){
					$payments{'range1_count'}++;
					$payments{'range1'}[0] += $amtpaid;
					$payments{'range1'}[1] += $amtfinanced;
					$payments{'range1'}[2] += $amtoncollection;
					$payments{'range1'}[3] += $amtupaid;
					$payments{'range1'}[4] += $amtar;
							
					for(1..$fp){
							$payments{'range1_fp_'.$_}++;
							$payments{'id_'.$rec->{'ID_orders'}.'_'.$_} = abs($payments{'id_'.$rec->{'ID_orders'}.'_'.$_});
							
							## Asign payment to the correct status
							$payments{'range1_'.$order[$_-1].'_'.$_} += $payments{'id_'.$rec->{'ID_orders'}.'_'.$_};		
					}
							
			## Range 501 - 1000	
			}elsif($amtorder > 500 and $amtorder <= 1000){
					$payments{'range2_count'}++;
					$payments{'range2'}[0] += $amtpaid;
					$payments{'range2'}[1] += $amtfinanced;
					$payments{'range2'}[2] += $amtoncollection;
					$payments{'range2'}[3] += $amtupaid;
					$payments{'range2'}[4] += $amtar;
							
					for(1..$fp){
							$payments{'range2_fp_'.$_}++;
							$payments{'id_'.$rec->{'ID_orders'}.'_'.$_} = abs($payments{'id_'.$rec->{'ID_orders'}.'_'.$_});
							
							## Asign payment to the correct status
							$payments{'range2_'.$order[$_-1 ].'_'.$_} += $payments{'id_'.$rec->{'ID_orders'}.'_'.$_};		
					}
					
			## Range 1001 - 1500	
			}elsif($amtorder > 1000 and $amtorder <= 1500){	
					$payments{'range3_count'}++;
					$payments{'range3'}[0] += $amtpaid;
					$payments{'range3'}[1] += $amtfinanced;
					$payments{'range3'}[2] += $amtoncollection;
					$payments{'range3'}[3] += $amtupaid;
					$payments{'range3'}[4] += $amtar;
							
					for(1..$fp){
							$payments{'range3_fp_'.$_}++;
							$payments{'id_'.$rec->{'ID_orders'}.'_'.$_} = abs($payments{'id_'.$rec->{'ID_orders'}.'_'.$_});
							
							## Asign payment to the correct status
							$payments{'range3_'.$order[$_-1].'_'.$_} += $payments{'id_'.$rec->{'ID_orders'}.'_'.$_};		
					}
									
			## Range 1501 - 2500	
			}elsif($amtorder > 1501 and $amtorder <= 2500){
					$payments{'range4_count'}++;
					$payments{'range4'}[0] += $amtpaid;
					$payments{'range4'}[1] += $amtfinanced;
					$payments{'range4'}[2] += $amtoncollection;
					$payments{'range4'}[3] += $amtupaid;
					$payments{'range4'}[4] += $amtar;
							
					for(1..$fp){
							$payments{'range4_fp_'.$_}++;
							$payments{'id_'.$rec->{'ID_orders'}.'_'.$_} = abs($payments{'id_'.$rec->{'ID_orders'}.'_'.$_});
							
							## Asign payment to the correct status
							$payments{'range4_'.$order[$_-1].'_'.$_} += $payments{'id_'.$rec->{'ID_orders'}.'_'.$_};		
					}
							
			## Range > 2500	
			}elsif($amtorder > 2500 ){	
					$payments{'range5_count'}++;
					$payments{'range5'}[0] += $amtpaid;
					$payments{'range5'}[1] += $amtfinanced;
					$payments{'range5'}[2] += $amtoncollection;
					$payments{'range5'}[3] += $amtupaid;
					$payments{'range5'}[4] += $amtar;
							
					for(1..$fp){
							$payments{'range5_fp_'.$_}++;
							$payments{'id_'.$rec->{'ID_orders'}.'_'.$_} = abs($payments{'id_'.$rec->{'ID_orders'}.'_'.$_});
							
							## Asign payment to the correct status
							$payments{'range5_'.$order[$_-1].'_'.$_} += $payments{'id_'.$rec->{'ID_orders'}.'_'.$_};		
					}
			}
			$payments{'total_amt'} += $amtorder;
			$payments{'total_qty'}++;
	}
		
		
	for $i(1..$maxfp){
			$payments{'range1_total_'.$i} = $payments{'range1_fppaid_'.$i} + $payments{'range1_fpfinanced_'.$i} + $payments{'range1_fponcollection_'.$i} + $payments{'range1_fpar_'.$i} + $payments{'range1_fpunpaid_'.$i};
			$payments{'range2_total_'.$i}= $payments{'range2_fppaid_'.$i} + $payments{'range2_fpfinanced_'.$i} + $payments{'range2_fponcollection_'.$i} + $payments{'range2_fpar_'.$i} + $payments{'range2_fpunpaid_'.$i};
			$payments{'range3_total_'.$i} = $payments{'range3_fppaid_'.$i} + $payments{'range3_fpfinanced_'.$i} + $payments{'range3_fponcollection_'.$i} + $payments{'range3_fpar_'.$i} + $payments{'range3_fpunpaid_'.$i};
			$payments{'range4_total_'.$i} = $payments{'range4_fppaid_'.$i} + $payments{'range4_fpfinanced_'.$i} + $payments{'range4_fponcollection_'.$i} + $payments{'range4_fpar_'.$i} + $payments{'range4_fpunpaid_'.$i};
			$payments{'range5_total_'.$i} = $payments{'range5_fppaid_'.$i} + $payments{'range5_fpfinanced_'.$i} + $payments{'range5_fponcollection_'.$i} + $payments{'range5_fpar_'.$i} + $payments{'range5_fpunpaid_'.$i};
			
			$va{'searchresults'} .= qq|	
					<tr onmouseover='m_over(this)' onmouseout='m_out(this)' bgcolor='$c[$d]'>
						<td align="right" valign="top" nowrap class='smalltext'>FP $i </td>|;
						
			
			for $j(1..5){
					
					if($payments{'range'.$j.'_total_'.$i} > 0)
					{
									
							$va{'searchresults'} .= qq|	
										<td align="right" valign="top" nowrap class='smalltext'>
											<table border="0" cellspacing="0" cellpadding="2" width="100%" class="formtable">
												<tr>
													<td align="right" valign="top">P</td>
													<td align="right" valign="top" nowrap class='smalltext'>|.&format_price($payments{'range'.$j.'_fppaid_'.$i}).qq|</td>
													<td align="right" valign="top">(|.&format_number($payments{'range'.$j.'_fppaid_'.$i}/$payments{'range'.$j.'_total_'.$i}*100).qq|%)</td>
												</tr>
												<tr>
													<td align="right" valign="top">F</td>
													<td align="right" valign="top" nowrap class='smalltext'>|.&format_price($payments{'range'.$j.'_fpfinanced_'.$i}).qq|</td>
													<td align="right" valign="top">(|.&format_number($payments{'range'.$j.'_fpfinanced_'.$i}/$payments{'range'.$j.'_total_'.$i}*100).qq|%)</td>
												</tr>
												<tr>
													<td align="right" valign="top" class='smalltext'>OC</td>
													<td align="right" valign="top" nowrap class='smalltext'>|.&format_price($payments{'range'.$j.'_fponcollection_'.$i}).qq|</td>
													<td align="right" valign="top">(|.&format_number($payments{'range'.$j.'_fponcollection_'.$i}/$payments{'range'.$j.'_total_'.$i}*100).qq|%)</td>
												</tr>
												<tr>
													<td align="right" valign="top" class='smalltext'>A/R</td>
													<td align="right" valign="top" nowrap class='smalltext'>|.&format_price($payments{'range'.$j.'_fpar_'.$i}).qq|</td>
													<td align="right" valign="top">(|.&format_number($payments{'range'.$j.'_fpar_'.$i}/$payments{'range'.$j.'_total_'.$i}*100).qq|%)</td>
												</tr>
												<tr>
													<td align="right" valign="top" class='smalltext'>U</td>
													<td align="right" valign="top" nowrap class='smalltext'>|.&format_price($payments{'range'.$j.'_fpunpaid_'.$i}).qq|</td>
													<td align="right" valign="top">(|.&format_number($payments{'range'.$j.'_fpunpaid_'.$i}/$payments{'range'.$j.'_total_'.$i}*100).qq|%)</td>
												</tr>
											</table>
										</td>|;
					}else{
							$va{'searchresults'} .= qq|	
										<td align="right" valign="top" nowrap class='smalltext'>
										<table border="0" cellspacing="0" cellpadding="2" width="100%" class="formtable">
										<tr><td colspan="3" align="center" h>No Flexpays Founded</td></tr>
										</table>|;
					}
			}
			
			$va{'searchresults'} .= qq|</td></tr>\n|;				
						
	}

	$va{'tot_cant'} = $payments{'total_qty'};
	$va{'tot_amount'} = &format_price($payments{'total_amt'});
	$va{'matches'} = $va{'tot_cant'};
	$va{'pageslist'} = 1;

	if ($in{'export'}){
			print "Content-type: application/vnd.ms-excel\n";
			print "Content-disposition: attachment; filename=fppaid_$in{'from_date'}.csv\n\n";
			my (@cols) = ("ID Order","Date","Initial Balance","# FP","FP1","FP2","FP3","FP4","FP5","FP6","FP7","FP8","FP9","FP10","FP11","FP12");
			print '"'.join('","',@cols) . "\"\n";
			print "$str";
	}else{
		($va{'rep1'},$va{'rep2'},$va{'rep3'},$va{'rep4'},$va{'rep5'},$va{'rep6'}) = ('off','off','on','off','off','off');
		print "Content-type: text/html\n\n";
		print &build_page('results_orders_fppaid.html');
	}
}


sub rep_orders_shipinfo{
#-----------------------------------------

	if($in{'action'} and &check_permissions('reports_orders','','')){
		
		my $fname   =	'shipinfo.e'.$in{'e'}.'.'.$in{'date'}.'.csv';
		
		###### Busqueda por rango de fecha
		$in{'from_date'} = &get_sql_date() if !$in{'from_date'};
		$in{'to_date'} = &get_sql_date() if !$in{'to_date'};
		
		my $strHeader = "ID Order,Type,Date,ShpDate,Amount,Status,Provider,Tracking";
		
		$query_tot = "SELECT COUNT(*) FROM sl_orders INNER JOIN
					(
						SELECT ID_orders FROM sl_orders_products INNER JOIN sl_orders_parts
						USING(ID_orders_products) WHERE  sl_orders_parts.Date BETWEEN '$in{'from_date'}' AND '$in{'to_date'}'
						GROUP BY ID_orders					
					)tmp USING (ID_orders);";

		$query_list = "SELECT sl_orders.ID_orders,Ptype,sl_orders.Date,Shp_Date,Amt,sl_orders.Status,ShpProvider,Tracking 
						FROM sl_orders INNER JOIN
					(
						SELECT ID_orders,sl_orders_parts.ShpProvider,sl_orders_parts.Tracking,sl_orders_parts.Date AS Shp_Date 
						FROM sl_orders_products INNER JOIN sl_orders_parts
						USING(ID_orders_products) WHERE  sl_orders_parts.Date BETWEEN '$in{'from_date'}' AND '$in{'to_date'}'
						GROUP BY ID_orders					
					)tmp USING (ID_orders)
					INNER JOIN 
					(
						SELECT ID_orders, SUM(Amount)AS Amt FROM sl_orders_payments
						WHERE Date BETWEEN '$in{'from_date'}' AND DATE_ADD('$in{'to_date'}', INTERVAL 10 DAY)
						AND Status NOT IN('Void','Cancelled')
						GROUP BY ID_orders 
					)tmp2
					 USING (ID_orders);";

		my ($sth) = &Do_SQL($query_tot);
		my ($tot) = $sth->fetchrow();

		if($tot) {

			my ($sth) = &Do_SQL($query_list);
			print "Content-type: application/octetstream\n";
			print "Content-disposition: attachment; filename=$fname\n\n";
			print "$strHeader\r\n";
			
			
			while(my($id_orders, $ptype, $date, $shpdate, $amount, $status, $provider, $tracking) = $sth->fetchrow()){
				
				print "$id_orders,$ptype,$date,$shpdate,$amount,$status,$provider,$tracking\n";
				
			}

			&auth_logging('report_view',1);
			return;

		}else{
			$va{'message'} = &trans_txt('not_records_found');
		}
	}
	
	print "Content-type: text/html\n\n";
	$va{'page_title'} = trans_txt("pageopr_orders");
	(!$in{'page'}) and ($in{'page'} = 'home');
	print &build_page('rep_orders_shipinfo.html');
}

#############################################################################
#############################################################################
#   Function: rep_orders_balance
#
#       Es: Reporte de Detalle Pagos Cuentas por Cobrar
#       En: 
#
#
#    Created on: 10/06/2013
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
sub rep_orders_balance {
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
		
		###### Busqueda por rango de fecha
		$in{'from_date'} = &get_sql_date() if !$in{'from_date'};

		
		my $fname   = 'customer_payments_'.$cfg{'app_title'}.'.csv';
		$fname =~ s/\s/_/g;
		
		
		
		my $strHeader = "UN, CLIENTE, NOMBRE, ID_FACTURA, MONEDA, FECHA FACTURA, FECHA VENCIMIENTO, IMPORTE ITEM ORIGINAL, SALDO ITEM, MORA";
		my ($sth) = &Do_SQL("
							SELECT 
								COUNT(*) 
							FROM sl_orders
							INNER JOIN
								sl_orders_products
							USING(ID_orders)
							INNER JOIN
								cu_invoices_lines
							USING(ID_orders_products)
							INNER JOIN
								cu_invoices USING(ID_invoices)
							INNER JOIN
								sl_customers
							ON
								sl_customers.ID_customers=sl_orders.ID_customers WHERE 1
							AND
								cu_invoices.Status IN('Certified','Cancelled');");
		my ($total) = $sth->fetchrow();
		
		if($total) {
			print "Content-type: application/octetstream\n";
			print "Content-disposition: attachment; filename=$fname\n\n";
			print "$strHeader\r\n";
			
			
			my $sth2 = &Do_SQL("SELECT 
								`cu_invoices`.`expediter_fname`, 
								(CONCAT(doc_serial,doc_num)), 
								`sl_orders`.`Date`, 
								`cu_invoices`.`Date`, 
								`cu_invoices`.`Date`, 
								`sl_orders`.`ID_customers`,
								cu_invoices.ID_invoices,
								(IF(sl_customers.company_name IS NOT NULL,company_name,CONCAT(sl_customers.FirstName,' ',sl_customers.Lastname1))) as cust_name, 
								`sl_customers`.`Type`, 
								`cu_invoices`.`invoice_net`, 
								`cu_invoices`.`total_taxes_transfered`, 
								`cu_invoices`.`invoice_total`, 
								`cu_invoices`.`discount`, 
								(CASE WHEN cu_invoices.Status='Certified' THEN 'Emitida' WHEN cu_invoices.Status='Cancelled' THEN 'Cancelada' ELSE '' END), 
								`sl_orders`.`ID_orders` 
							FROM sl_orders
							INNER JOIN
								sl_orders_products
							USING(ID_orders)
							INNER JOIN
								cu_invoices_lines
							USING(ID_orders_products)
							INNER JOIN
								cu_invoices USING(ID_invoices)
							INNER JOIN
								sl_customers
							ON
								sl_customers.ID_customers=sl_orders.ID_customers WHERE 1
							AND
								cu_invoices.Status IN ('Certified','Cancelled')
							GROUP BY ID_invoices ORDER BY doc_serial,doc_num;");
			
			
			my $records = 0;
			while ($rec = $sth2->fetchrow_hashref()) {
				
				my ($sth) = &Do_SQL("SELECT
										sum(sl_banks_movements.Amount) as total_paid,
										cu_invoices.ID_invoices, sl_orders.ID_orders,cu_company_legalinfo.Name,cu_invoices.Currency,
										cu_invoices.doc_serial, cu_invoices.doc_num,cu_invoices.invoice_total,
										cu_invoices.doc_date, date_add(cu_invoices.doc_date, INTERVAL sl_terms.CreditDays DAY) as DueDate,
										IF(DATEDIFF('$in{'from_date'}', date_add(cu_invoices.doc_date, INTERVAL sl_terms.CreditDays DAY))>0,
											DATEDIFF('$in{'from_date'}', date_add(cu_invoices.doc_date, INTERVAL sl_terms.CreditDays DAY)),
											0) as delay
									FROM 
										sl_banks_movements
									INNER JOIN sl_banks_movrel USING(ID_banks_movements)
									INNER JOIN sl_orders_payments ON ID_orders_payments=tableid AND tablename='orders_payments'
									INNER JOIN sl_orders USING(ID_orders)
									INNER JOIN cu_invoices_lines USING(ID_orders)
									INNER JOIN cu_invoices USING(ID_invoices)
									LEFT JOIN cu_company_legalinfo ON PrimaryRecord='YES'
									LEFT JOIN sl_terms ON (sl_orders.Pterms=sl_terms.Name AND sl_terms.Type='Sales')
									WHERE 1 AND sl_orders.ID_customers = '$rec->{'ID_customers'}'
									AND sl_orders_payments.Status IN ('Approved')
									AND sl_orders_payments.Captured = 'Yes'
									AND cu_invoices.ID_invoices = $rec->{'ID_invoices'}
									/*AND sl_orders.Status NOT IN ('Cancelled','Void','System Error')*/
									/*GROUP BY sl_orders.ID_orders;*/
									/*GROUP BY cu_invoices.ID_invoices*/;
									/*AND cu_invoices.Status = '$invoice_status'*/;");
				
				my ($rec_amounts) = $sth->fetchrow_hashref();
				my $pay_diff = $rec_amounts->{'invoice_total'} - $rec_amounts->{'total_paid'};
				my $delay = 0;
				if ($pay_diff > 0) {
					$delay = 1;
				}
				if ($rec_amounts->{'total_paid'} eq '') {
					my ($sth_aux) = &Do_SQL("SELECT
						cu_company_legalinfo.Name,
						cu_invoices.invoice_total,
						sl_terms.CreditDays DAY,
						cu_invoices.doc_date,
						date_add(cu_invoices.doc_date, INTERVAL sl_terms.CreditDays DAY) as DueDate,
						IF(DATEDIFF('$in{'from_date'}', date_add(cu_invoices.doc_date, INTERVAL sl_terms.CreditDays DAY))>0,
																DATEDIFF('$in{'from_date'}', date_add(cu_invoices.doc_date, INTERVAL sl_terms.CreditDays DAY)),
																0) as delay
					FROM cu_invoices
					INNER JOIN cu_invoices_lines USING(ID_invoices)
					INNER JOIN sl_orders USING(ID_orders)
					LEFT JOIN sl_terms ON(sl_orders.Pterms=sl_terms.Name AND sl_terms.Type='Sales')
					LEFT JOIN cu_company_legalinfo ON PrimaryRecord='YES'
					WHERE cu_invoices.ID_invoices = '$rec->{'ID_invoices'}' LIMIT 1;");
					
					my ($rec_aux) = $sth_aux->fetchrow_hashref();
					
					$rec_amounts->{'Name'} = $rec_aux->{'Name'};
					$rec_amounts->{'DueDate'} = $rec_aux->{'DueDate'};
					$rec_amounts->{'delay'} = $rec_aux->{'delay'};
				}
				
				my $strout = qq|"$rec_amounts->{'Name'}","$rec->{'ID_customers'}","$rec->{'cust_name'}","$rec_amounts->{'doc_serial'}$rec_amounts->{'doc_num'}","$rec_amounts->{'Currency'}","$rec_amounts->{'doc_date'}","$rec_amounts->{'DueDate'}","$rec_amounts->{'invoice_total'}","$pay_diff","$rec_amounts->{'delay'}"\r\n|;
				print $strout;
			}
			return;
		} else {
			$va{'message'} = &trans_txt('search_nomatches');
		}
	}
	
	print "Content-type: text/html\n\n";
	print &build_page('rep_orders_balance.html');

}

#############################################################################
#############################################################################
#   Function: rep_orders_ar_aging
#
#       Es: Reporte de Detalle de Saldos de Cuentas por Cobrar
#       En: 
#
#
#    Created on: 13/06/2013
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
sub rep_orders_ar_aging {
#############################################################################
#############################################################################

	if($in{'action'}) {
		if ($in{'cons_customer'} and $in{'cons_customer'} eq 'yes') {
			&rep_orders_ar_grouped_aging_periods();
			return;
		}
		$in{'export'}=1;
		my ($query_list);
		my $maxprod=1;
		my $info_user =	'';
		my $info_pprod = '';
		my $info_oprod = '';
		my $info_time = '';
		my $sql_between = '';
		my $sql_ship_between = '';
		my $sql_idcustomers = '';
		my $add_filters='';
		
		###### Busqueda por rango de fecha
		#$in{'from_date'} = &get_sql_date() if !$in{'from_date'};
		$in{'from_date'} = &filter_values($in{'from_date'});
		$in{'to_date'} = &filter_values($in{'to_date'});
		$in{'from_ship_date'} = &filter_values($in{'from_ship_date'});
		$in{'to_ship_date'} = &filter_values($in{'to_ship_date'});
		$in{'id_customers'} = &filter_values($in{'id_customers'});
		if ($in{'to_date'} and $in{'from_date'}) {
			$sql_between = "AND date_add(sl_orders.PostedDate, INTERVAL sl_terms.CreditDays DAY) BETWEEN '$in{'from_date'}' AND '$in{'to_date'}'";
		} elsif ($in{'from_date'}) {
			$sql_between =  "AND date_add(sl_orders.PostedDate, INTERVAL sl_terms.CreditDays DAY) >= '$in{'from_date'}'";
		} elsif ($in{'to_date'}) {
			$sql_between =  "AND date_add(sl_orders.PostedDate, INTERVAL sl_terms.CreditDays DAY) <= '$in{'to_date'}'";
		}
		
		if ($in{'to_ship_date'} and $in{'from_ship_date'}) {
			$sql_ship_between = "AND sl_orders.PostedDate BETWEEN '$in{'from_ship_date'}' AND '$in{'to_ship_date'}'";
		} elsif ($in{'from_ship_date'}) {
			$sql_ship_between =  "AND sl_orders.PostedDate >= '$in{'from_ship_date'}'";
		} elsif ($in{'to_ship_date'}) {
			$sql_ship_between =  "AND sl_orders.PostedDate <= '$in{'to_ship_date'}'";
		}
		
		if ($in{'id_customers'}) {
			$sql_idcustomers = "AND sl_orders.ID_customers='$in{'id_customers'}'";
		}
		
		my $fname   = 'rep_ar_aging_'.$cfg{'app_title'}.'.csv';
		$fname =~ s/\s/_/g;
		
		# my $strHeader = "ID Cliente, Cliente,  No Vencido 30, No Vencido 60, No Vencido 90, No Vencido > 90, Vencido 30, Vencido 60, Vencido 90, Vencido 120, Vencido > 120, No Vencido Total, Vencido Total, Saldo";
		#my $strHeader = qq|"ID Cliente","ID Pedido","Num. Factura","Cliente","Tipo","Plazo","Fecha Factura","Fecha Vencimiento","Dias Mora","Importe Orig Factura","Moneda","Saldo","Tipo Documento","Numero Orden de Compra","Estatus Orden","Piezas Facturadas","No Vencido Total","Vencido 30","Vencido 60","Vencido 90","Vencido 120","Vencido > 120"|;
		my $strHeader = qq|"ID Cliente","ID Pedido","Num. Factura","Cliente","Tipo","Plazo","Fecha Factura","Fecha Vencimiento","Dias Mora","Importe Orig Factura","Moneda","Saldo","Tipo Documento","Numero Orden de Compra","Estatus Orden","Piezas Facturadas","No Vencido Total"|;
		
		print "Content-type: application/octetstream\n";
		print "Content-disposition: attachment; filename=$fname\n\n";
		print "$strHeader\r\n";
		
		
		my $sth2 = &Do_SQL("SELECT
			sl_orders.ID_orders
			, sl_customers.ID_customers
			, sl_customers.company_name
			, sl_customers.Type customer_type
			, sl_terms.Name cretid_days

			-- , (IFNULL(payments_paid.AmountPaid,0))payments_paid
			-- , (IFNULL(payments_pending.AmountPending,0)) payments_pending

			, payments_totals.AmountTotal

			, IFNULL(payments_pending.AmountPending,0) + IFNULL(credits_pending.AmountPending,0) as TotalPending

			, IFNULL(credits_pending.AmountPending,0) credits_pending

			, (IF(DATEDIFF(CURDATE(), date_add(sl_orders.PostedDate, INTERVAL sl_terms.CreditDays DAY))<0,IFNULL(payments_pending.AmountPending,0) + IFNULL(credits_pending.AmountPending,0),0))NOVENCIDO

			, (IF(DATEDIFF(CURDATE(), date_add(sl_orders.PostedDate, INTERVAL sl_terms.CreditDays DAY))>=0 AND DATEDIFF(CURDATE(), date_add(sl_orders.PostedDate, INTERVAL sl_terms.CreditDays DAY))<=30,IFNULL(payments_pending.AmountPending,0) + IFNULL(credits_pending.AmountPending,0),0))VENCIDO30
			, (IF(DATEDIFF(CURDATE(), date_add(sl_orders.PostedDate, INTERVAL sl_terms.CreditDays DAY))>=31 AND DATEDIFF(CURDATE(), date_add(sl_orders.PostedDate, INTERVAL sl_terms.CreditDays DAY))<=60,IFNULL(payments_pending.AmountPending,0) + IFNULL(credits_pending.AmountPending,0),0))VENCIDO60
			, (IF(DATEDIFF(CURDATE(), date_add(sl_orders.PostedDate, INTERVAL sl_terms.CreditDays DAY))>=61 AND DATEDIFF(CURDATE(), date_add(sl_orders.PostedDate, INTERVAL sl_terms.CreditDays DAY))<=90,IFNULL(payments_pending.AmountPending,0) + IFNULL(credits_pending.AmountPending,0),0))VENCIDO90
			, (IF(DATEDIFF(CURDATE(), date_add(sl_orders.PostedDate, INTERVAL sl_terms.CreditDays DAY))>=91 AND DATEDIFF(CURDATE(), date_add(sl_orders.PostedDate, INTERVAL sl_terms.CreditDays DAY))<=120,IFNULL(payments_pending.AmountPending,0) + IFNULL(credits_pending.AmountPending,0),0))VENCIDO120
			, (IF(DATEDIFF(CURDATE(), date_add(sl_orders.PostedDate, INTERVAL sl_terms.CreditDays DAY))>=121,IFNULL(payments_pending.AmountPending,0) + IFNULL(credits_pending.AmountPending,0),0))VENCIDOMT120

			, DATEDIFF(CURDATE(), date_add(sl_orders.PostedDate, INTERVAL sl_terms.CreditDays DAY))days
			
			, sl_orders.PostedDate
			, sl_orders.Status
			, inovices.ID_invoices
			, inovices.invoice
			, inovices.doc_date
			, inovices.pzs
			, inovices.invoice_type
			, inovices.invoice_total
			, inovices.currency_exchange
			, inovices.currency
			, inovices.ID_orders_alias
			FROM sl_orders

			LEFT JOIN (
				SELECT SUM(sl_orders_payments.Amount)AmountPaid, COUNT(*)Payments, ID_orders
				FROM sl_orders_payments
				WHERE sl_orders_payments.Status IN ('Approved','Credit')
				AND sl_orders_payments.Captured='Yes'
				AND sl_orders_payments.CapDate > '1900-01-01'
				AND sl_orders_payments.Amount > 0
				GROUP BY sl_orders_payments.ID_orders
			)payments_paid ON payments_paid.ID_orders=sl_orders.ID_orders

			LEFT JOIN (
				SELECT SUM(sl_orders_payments.Amount)AmountPending, COUNT(*)Payments, ID_orders
				FROM sl_orders_payments
				WHERE sl_orders_payments.Status IN ('Approved','Credit')
				AND (sl_orders_payments.Captured<>'Yes' OR sl_orders_payments.Captured IS NULL)
				AND (sl_orders_payments.CapDate IS NULL OR sl_orders_payments.CapDate<'1900-01-01' OR sl_orders_payments.CapDate ='')
				AND sl_orders_payments.Amount > 0
				GROUP BY sl_orders_payments.ID_orders
			)payments_pending ON payments_pending.ID_orders=sl_orders.ID_orders

			LEFT JOIN (
				SELECT SUM(sl_orders_payments.Amount)AmountPending, COUNT(*)Payments, ID_orders
				FROM sl_orders_payments
				WHERE sl_orders_payments.Status IN ('Credit')
				AND (sl_orders_payments.Captured<>'Yes' OR sl_orders_payments.Captured IS NULL)
				AND (sl_orders_payments.CapDate IS NULL OR sl_orders_payments.CapDate<'1900-01-01' OR sl_orders_payments.CapDate ='')
				AND sl_orders_payments.Amount < 0
				GROUP BY sl_orders_payments.ID_orders
			)credits_pending ON credits_pending.ID_orders=sl_orders.ID_orders

			LEFT JOIN (
				SELECT SUM(sl_orders_payments.Amount)AmountTotal, COUNT(*)Payments, ID_orders
				FROM sl_orders_payments
				WHERE sl_orders_payments.Status NOT IN ('Cancelled')
				GROUP BY sl_orders_payments.ID_orders
			)payments_totals ON payments_totals.ID_orders=sl_orders.ID_orders
			
			LEFT JOIN (
				SELECT 
					ID_invoices
					, cu_invoices_lines.ID_orders
					, concat(cu_invoices.doc_serial
					, cu_invoices.doc_num)invoice
					, DATE(cu_invoices.doc_date)doc_date
					, COUNT(*)pzs
					, cu_invoices.invoice_type
					, cu_invoices.invoice_total
					, IF(cu_invoices.currency='MXP','',cu_invoices.currency_exchange)currency_exchange
					, cu_invoices.currency
					, cu_invoices.ID_orders_alias
				FROM cu_invoices_lines
				LEFT JOIN cu_invoices USING(ID_invoices)
				WHERE cu_invoices.Status='Certified'
				GROUP BY ID_invoices
				
				UNION 

				SELECT  
					ID_invoices
					, cu_invoices_lines.ID_orders
					, concat(cu_invoices.doc_serial
					, cu_invoices.doc_num)invoice
					, DATE(cu_invoices.doc_date)doc_date
					, COUNT(*)pzs
					, cu_invoices.invoice_type
					, cu_invoices.invoice_total
					, IF(cu_invoices.currency='MXP','',cu_invoices.currency_exchange)currency_exchange
					, cu_invoices.currency
					, cu_invoices.ID_orders_alias
				FROM sl_creditmemos_payments
				LEFT JOIN cu_invoices_lines ON cu_invoices_lines.ID_creditmemos=sl_creditmemos_payments.ID_creditmemos
				LEFT JOIN cu_invoices USING(ID_invoices)
				WHERE cu_invoices.Status='Certified'
				GROUP BY ID_invoices
			)inovices ON inovices.ID_orders = sl_orders.ID_orders

			INNER JOIN sl_customers ON sl_customers.ID_customers=sl_orders.ID_customers
			LEFT JOIN sl_terms ON sl_terms.Name=sl_customers.Pterms

			WHERE sl_orders.Status='Shipped'

			-- AND sl_customers.ID_customers = 100065

			$sql_between
			$sql_ship_between
			$sql_idcustomers
						
			GROUP BY sl_orders.ID_orders
			HAVING TotalPending <> 0
			ORDER BY sl_customers.company_name, sl_orders.ID_orders, inovices.ID_invoices;");
			
		while ($rec = $sth2->fetchrow_hashref()) {
			
			$cust_lines = qq|"$rec->{'ID_customers'}","$rec->{'ID_orders'}","$rec->{'invoice'}","$rec->{'company_name'}","$rec->{'customer_type'}","$rec->{'cretid_days'}","$rec->{'doc_date'}","$rec->{'PostedDate'}","$rec->{'days'}","$rec->{'invoice_total'}","$rec->{'currency'}"|;
			
			$cust_lines .= qq|,"|.&format_price(($rec->{'TotalPending'})).qq|","$rec->{'invoice_type'}","$rec->{'ID_orders_alias'}","$rec->{'Status'}","$rec->{'pzs'}","|.&format_price(($rec->{'NOVENCIDO'})).qq|"\r\n|;

			if($rec->{'TotalPending'} > 0){
				print $cust_lines;
			}
		}
		return;
	}
	print "Content-type: text/html\n\n";
	print &build_page('rep_orders_ar_aging.html');

}



#############################################################################
#############################################################################
#   Function: rep_orders_ar_aging_periods
#
#       Es: Reporte de Atigüedad de Saldos de CxC
#       En: 
#
#
#    Created on: 27/06/2013
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
sub rep_orders_ar_aging_periods {
#############################################################################
#############################################################################

	if($in{'action'}) {
		#if ($in{'cons_customer'} and $in{'cons_customer'} eq 'yes') {
		#	&rep_orders_ar_grouped_aging_periods();
		#	return;
		#}

		$in{'export'}=1;
		my $add_sql = '';
		my $add_sql_cms = '';
		my $add_sql_cus_ad = '';
		
		$in{'from_todate'} = &filter_values($in{'from_todate'});
		$in{'to_todate'} = &filter_values($in{'to_todate'});
		$in{'from_date'} = &filter_values($in{'from_date'});
		$in{'to_date'} = &filter_values($in{'to_date'});
		$in{'from_ship_date'} = &filter_values($in{'from_ship_date'});
		$in{'to_ship_date'} = &filter_values($in{'to_ship_date'});
		$in{'id_customers'} = &filter_values($in{'id_customers'});


		## Document Date
		if ($in{'to_docdate'} and $in{'from_docdate'}) {
			$add_sql .= "AND sl_orders.Date BETWEEN '". $in{'from_docdate'} ."' AND '". $in{'to_docdate'} ."'";
			$add_sql_cms .= "AND sl_creditmemos.Date BETWEEN '". $in{'from_docdate'} ."' AND '". $in{'to_docdate'} ."'";
			$add_sql_cus_ad .= "AND sl_customers_advances.Date BETWEEN '". $in{'from_docdate'} ."' AND '". $in{'to_docdate'} ."'";
		} elsif ($in{'from_docdate'}) {
			$add_sql .=  "AND sl_orders.Date >= '". $in{'from_docdate'} ."'";
			$add_sql_cms .= "AND sl_creditmemos.Date >= '". $in{'from_docdate'} ."'";
			$add_sql_cus_ad .= "AND sl_customers_advances.Date >= '". $in{'from_docdate'} ."'";
		} elsif ($in{'to_docdate'}) {
			$add_sql .=  "AND sl_orders.Date <= '". $in{'to_docdate'} ."'";
			$add_sql_cms .= "AND sl_creditmemos.Date <= '". $in{'to_docdate'} ."'";
			$add_sql_cus_ad .= "AND sl_customers_advances.Date <= '". $in{'to_docdate'} ."'";
		}

		## Due Date
		if ($in{'to_date'} and $in{'from_date'}) {
			$add_sql .= "AND date_add(sl_orders.PostedDate, INTERVAL sl_terms.CreditDays DAY) BETWEEN '". $in{'from_date'} ."' AND '". $in{'to_date'} ."'";
		} elsif ($in{'from_date'}) {
			$add_sql .=  "AND date_add(sl_orders.PostedDate, INTERVAL sl_terms.CreditDays DAY) >= '". $in{'from_date'} ."'";
		} elsif ($in{'to_date'}) {
			$add_sql .=  "AND date_add(sl_orders.PostedDate, INTERVAL sl_terms.CreditDays DAY) <= '". $in{'to_date'} ."'";
		}
		
		## ShipDate
		if ($in{'to_ship_date'} and $in{'from_ship_date'}) {
			$add_sql .= "AND sl_orders.PostedDate BETWEEN '". $in{'from_ship_date'} ."' AND '". $in{'to_ship_date'} ."'";
		} elsif ($in{'from_ship_date'}) {
			$add_sql .=  "AND sl_orders.PostedDate >= '". $in{'from_ship_date'} ."'";
		} elsif ($in{'to_ship_date'}) {
			$add_sql .=  "AND sl_orders.PostedDate <= '". $in{'to_ship_date'} ."'";
		}
		
		if ($in{'id_customers'}) {

			$add_sql .= "AND sl_orders.ID_customers='$in{'id_customers'}'";
			$add_sql_cms .= "AND sl_creditmemos.ID_customers='$in{'id_customers'}'";
			$add_sql_cus_ad .= "AND sl_customers_advances.ID_customers='$in{'id_customers'}'";

		}

		if($in{'id_customers_bulk'}){

			## Seeveral Customers
			my (@ary_customers) = split(/\s+|,|\n|\t/,$in{'id_customers_bulk'});
			$add_sql .= "AND sl_orders.ID_customers IN (". join(',', @ary_customers) .") ";
			$add_sql_cms .= "AND sl_creditmemos.ID_customers IN (". join(',', @ary_customers) .") ";
			$add_sql_cus_ad .= "AND sl_customers_advances.ID_customers IN (". join(',', @ary_customers) .") ";			

		}

		## Filter by invoice_type
		if ($in{'invoice_type'} and $in{'invoice_type'} ne ''){

			my @ary = split(/\|/,$in{'invoice_type'});
			my $invoice_type='';
			for (0..$#ary){
					$invoice_type .= ($ary[$_] ne '')? "'$ary[$_]',":"";
			}

			chop($invoice_type);
			$add_sql .= "AND invoices.invoice_type IN($invoice_type) ";

		}

		my $fname   = 'rep_ar_aging_periods_'.$cfg{'app_title'}.'.csv';
		$fname =~ s/\s/_/g;


		## Se unen los parametros del reporte para formar un json con dichos datos, el cual es pasado a 
		## ax_set_report_background para que sea almacenado en los registros de reportes pendientes
		my $json_parameters = '{"export":"'.$in{'export'}.'","from_todate":"'.$in{'from_todate'}.'","to_todate":"'.$in{'to_todate'}.'",';
			$json_parameters .= '"from_date":"'.$in{'from_date'}.'","to_date":"'.$in{'to_date'}.'","from_ship_date":"'.$in{'from_ship_date'}.'",';
			$json_parameters .= '"to_ship_date":"'.$in{'to_ship_date'}.'","id_customers":"'.$in{'id_customers'}.'","to_docdate":"'.$in{'to_docdate'}.'",';
			$json_parameters .= '"from_docdate":"'.$in{'from_docdate'}.'","id_customers_bulk":"'.$in{'id_customers_bulk'}.'","invoice_type":"'.$in{'invoice_type'}.'"}';

		$result = &ax_set_report_background( 'rep_orders_ar_aging_periods', $json_parameters );
		if( $result->{'status'} ne 'Fail' )
		{

			if( $result->{'status'} =~ m/Finished/ ){
				$va{'message'} = &trans_txt('report_in_background_existing').'<a href="/cgi-bin/mod/admin/admin?cmd=extracted_reports&report='.$result->{'status'}.'"><img src="/sitimages/file.png" style="height:32px; vertical-align: middle;" /></a>';
			}else{
				$va{'message'} = &trans_txt('report_in_background_processing');
			}
			
			print "Content-type: text/html\n\n";
			print &build_page('rep_orders_ar_aging_periods.html');
			return null;
		}
		


		my $strHeader = qq|"ID Cliente","Nombre","Tipo","Plazo","ID Pedido","Estatus","Numero Orden de Compra","Tipo Documento","ID Documento","Fecha Documento","Moneda","Importe Orignal Documento","Tipo de Cambio","Importe Original MXN","Fecha Vencimiento","Dias Mora","Saldo Moneda Original","Saldo MXN","No Vencido Total","Vencido 30","Vencido 60","Vencido 90","Vencido 120","Vencido > 120"|;#"Piezas","Tipo Factura",		
		
		my $sth2 = &Do_SQL("
			SELECT
				sl_customers.ID_customers
				, sl_customers.company_name
				, sl_customers.`Type` customer_type
				, sl_terms.Name cretid_days
				, sl_orders.ID_orders
				, sl_orders.`Status`
				, invoices.ID_invoices
				, invoices.invoice
				#, invoices.pzs
				#, invoices.invoice_type
				, invoices.doc_date
				, invoices.ID_orders_alias
				, 'Factura' AS TipoDocumento
				, DATE_ADD(sl_orders.PostedDate, INTERVAL sl_terms.CreditDays DAY)PostedDate
				, DATEDIFF(CURDATE(), DATE_ADD(sl_orders.PostedDate, INTERVAL sl_terms.CreditDays DAY))days
				, invoices.invoice_total TotalFactura
				, invoices.currency
				, IF(invoices.currency_exchange != '' AND invoices.currency_exchange IS NOT NULL, invoices.currency_exchange, 1) AS currency_exchange
				, IFNULL(sl_orders_products.TotalProducts,0) - IFNULL(payments_paid.AmountPaid,0) as SaldoAlDia
				, (IF(DATEDIFF(CURDATE(), DATE_ADD(sl_orders.PostedDate, INTERVAL sl_terms.CreditDays DAY))<0,IFNULL(sl_orders_products.TotalProducts,0) - IFNULL(payments_paid.AmountPaid,0),0))NOVENCIDO
				, (IF(DATEDIFF(CURDATE(), DATE_ADD(sl_orders.PostedDate, INTERVAL sl_terms.CreditDays DAY))>=0 AND DATEDIFF(CURDATE(), DATE_ADD(sl_orders.PostedDate, INTERVAL sl_terms.CreditDays DAY))<=30,IFNULL(sl_orders_products.TotalProducts,0) - IFNULL(payments_paid.AmountPaid,0),0))VENCIDO30
				, (IF(DATEDIFF(CURDATE(), DATE_ADD(sl_orders.PostedDate, INTERVAL sl_terms.CreditDays DAY))>=31 AND DATEDIFF(CURDATE(), DATE_ADD(sl_orders.PostedDate, INTERVAL sl_terms.CreditDays DAY))<=60,IFNULL(sl_orders_products.TotalProducts,0) - IFNULL(payments_paid.AmountPaid,0),0))VENCIDO60
				, (IF(DATEDIFF(CURDATE(), DATE_ADD(sl_orders.PostedDate, INTERVAL sl_terms.CreditDays DAY))>=61 AND DATEDIFF(CURDATE(), DATE_ADD(sl_orders.PostedDate, INTERVAL sl_terms.CreditDays DAY))<=90,IFNULL(sl_orders_products.TotalProducts,0) - IFNULL(payments_paid.AmountPaid,0),0))VENCIDO90
				, (IF(DATEDIFF(CURDATE(), DATE_ADD(sl_orders.PostedDate, INTERVAL sl_terms.CreditDays DAY))>=91 AND DATEDIFF(CURDATE(), DATE_ADD(sl_orders.PostedDate, INTERVAL sl_terms.CreditDays DAY))<=120,IFNULL(sl_orders_products.TotalProducts,0) - IFNULL(payments_paid.AmountPaid,0),0))VENCIDO120
				, (IF(DATEDIFF(CURDATE(), DATE_ADD(sl_orders.PostedDate, INTERVAL sl_terms.CreditDays DAY))>=121,IFNULL(sl_orders_products.TotalProducts,0) - IFNULL(payments_paid.AmountPaid,0),0))VENCIDOMT120
				, 1 AS Orden
			FROM sl_orders
				LEFT JOIN (
					SELECT SUM(sl_orders_payments.Amount)AmountPaid, COUNT(*)Payments, ID_orders
					FROM sl_orders_payments
					WHERE sl_orders_payments.`Status` IN ('Approved','Credit')
						AND sl_orders_payments.Captured='Yes'
						AND sl_orders_payments.CapDate > '1900-01-01'
						#AND sl_orders_payments.Amount > 0
					GROUP BY sl_orders_payments.ID_orders
				)payments_paid ON payments_paid.ID_orders=sl_orders.ID_orders
				LEFT JOIN (
					SELECT SUM(sl_orders_payments.Amount)AmountPending, COUNT(*)Payments, ID_orders
					FROM sl_orders_payments
					WHERE sl_orders_payments.`Status` IN ('Approved','Credit')
						AND (sl_orders_payments.Captured<>'Yes' OR sl_orders_payments.Captured IS NULL)
						AND (sl_orders_payments.CapDate IS NULL OR sl_orders_payments.CapDate<'1900-01-01' OR sl_orders_payments.CapDate ='')
						#AND sl_orders_payments.Amount > 0
					GROUP BY sl_orders_payments.ID_orders
				)payments_pending ON payments_pending.ID_orders=sl_orders.ID_orders
				LEFT JOIN (
					SELECT SUM(sl_orders_payments.Amount)AmountPending, COUNT(*)Payments, ID_orders
					FROM sl_orders_payments
					WHERE sl_orders_payments.`Status` IN ('Credit')
						AND (sl_orders_payments.Captured<>'Yes' OR sl_orders_payments.Captured IS NULL)
						AND (sl_orders_payments.CapDate IS NULL OR sl_orders_payments.CapDate<'1900-01-01' OR sl_orders_payments.CapDate ='')
						AND sl_orders_payments.Amount < 0
					GROUP BY sl_orders_payments.ID_orders
				)credits_pending ON credits_pending.ID_orders=sl_orders.ID_orders
				LEFT JOIN (
					SELECT SUM(sl_orders_payments.Amount)AmountTotal, COUNT(*)Payments, ID_orders
					FROM sl_orders_payments
					WHERE sl_orders_payments.`Status` NOT IN ('Cancelled')
					GROUP BY sl_orders_payments.ID_orders
				)payments_totals ON payments_totals.ID_orders=sl_orders.ID_orders
				INNER JOIN (
					SELECT
						sl_orders_products.ID_orders
						, (SUM(sl_orders_products.SalePrice) + SUM(sl_orders_products.Shipping) + SUM(sl_orders_products.Tax) + SUM(sl_orders_products.ShpTax))- SUM(sl_orders_products.Discount)TotalProducts
					FROM sl_orders_products
					WHERE sl_orders_products.`Status` NOT IN ('Inactive')
					GROUP BY sl_orders_products.ID_orders
				)sl_orders_products ON sl_orders_products.ID_orders=sl_orders.ID_orders
				LEFT JOIN (
					SELECT 
						ID_invoices
						, cu_invoices_lines.ID_orders
						, concat(cu_invoices.doc_serial
						, cu_invoices.doc_num)invoice
						, DATE(cu_invoices.doc_date)doc_date
						#, COUNT(*)pzs
						, cu_invoices.invoice_type
						, cu_invoices.invoice_total
						, IF(cu_invoices.currency='MXP','',cu_invoices.currency_exchange)currency_exchange
						, cu_invoices.currency
						, cu_invoices.ID_orders_alias
					FROM cu_invoices_lines
					LEFT JOIN cu_invoices USING(ID_invoices)
					WHERE cu_invoices.`Status`='Certified'
					GROUP BY ID_invoices
					
					UNION 
					
					SELECT  
						ID_invoices
						, cu_invoices_lines.ID_orders
						, CONCAT(cu_invoices.doc_serial, cu_invoices.doc_num)invoice
						, DATE(cu_invoices.doc_date)doc_date
						#, COUNT(*)pzs
						, cu_invoices.invoice_type
						, cu_invoices.invoice_total
						, IF(cu_invoices.currency='MXP','',cu_invoices.currency_exchange)currency_exchange
						, cu_invoices.currency
						, cu_invoices.ID_orders_alias
					FROM sl_creditmemos_payments
					LEFT JOIN cu_invoices_lines ON cu_invoices_lines.ID_creditmemos=sl_creditmemos_payments.ID_creditmemos
					LEFT JOIN cu_invoices USING(ID_invoices)
					WHERE cu_invoices.Status='Certified'
					GROUP BY ID_invoices
					ORDER BY ID_invoices DESC
				)invoices ON invoices.ID_orders = sl_orders.ID_orders
				INNER JOIN sl_customers ON sl_customers.ID_customers=sl_orders.ID_customers
				LEFT JOIN sl_terms ON sl_terms.Name=sl_customers.Pterms
			WHERE sl_orders.Status='Shipped' 
				#AND sl_orders.ID_customers= 100107
				$add_sql
				AND ABS(IFNULL(sl_orders_products.TotalProducts,0) - IFNULL(payments_paid.AmountPaid,0)) > 0.01
				AND invoices.invoice_type='ingreso' 
			GROUP BY sl_orders.ID_orders

			# ----------------------------------------------------------------
			# Se agregan los CMs que aun no tienen ligada una orden
			# ----------------------------------------------------------------
			UNION 

			SELECT
				sl_customers.ID_customers
				, sl_customers.company_name
				, sl_customers.`Type` customer_type
				, sl_terms.Name cretid_days
				, sl_creditmemos.ID_creditmemos AS ID_orders
				, sl_creditmemos.`Status` AS `Status`
				, invoices.ID_invoices
				, invoices.invoice
				#, invoices.pzs
				#, invoices.invoice_type
				, invoices.doc_date
				, invoices.ID_orders_alias
				, 'Nota de Credito' AS TipoDocumento
				, DATE_ADD(sl_creditmemos.Date, INTERVAL sl_terms.CreditDays DAY)PostedDate
				, DATEDIFF(CURDATE(), DATE_ADD(sl_creditmemos.Date, INTERVAL sl_terms.CreditDays DAY))days
				, invoices.invoice_total TotalFactura
				, invoices.currency
				, IF(invoices.currency_exchange != '' AND invoices.currency_exchange IS NOT NULL, invoices.currency_exchange, 1) AS currency_exchange
				, sl_creditmemos_products.TotalProducts AS SaldoAlDia
				, 0 AS NOVENCIDO
				, 0 AS VENCIDO30
				, 0 AS VENCIDO60
				, 0 AS VENCIDO90
				, 0 AS VENCIDO120
				, 0 AS VENCIDOMT120
				, 2 AS Orden
			FROM sl_creditmemos
				INNER JOIN (
					SELECT
						sl_creditmemos_products.ID_creditmemos
						, (SUM(sl_creditmemos_products.SalePrice * sl_creditmemos_products.Quantity) + SUM(sl_creditmemos_products.Shipping) + SUM(sl_creditmemos_products.Tax) + SUM(sl_creditmemos_products.ShpTax) - SUM(sl_creditmemos_products.Discount)) TotalProducts
					FROM sl_creditmemos_products
					WHERE sl_creditmemos_products.`Status` = 'Active'
					GROUP BY sl_creditmemos_products.ID_creditmemos
				)sl_creditmemos_products ON sl_creditmemos_products.ID_creditmemos=sl_creditmemos.ID_creditmemos
				INNER JOIN (
					SELECT  
						ID_invoices
						, cu_invoices_lines.ID_creditmemos
						, concat(cu_invoices.doc_serial
						, cu_invoices.doc_num)invoice
						, DATE(cu_invoices.doc_date)doc_date
						#, COUNT(*)pzs
						#, cu_invoices.invoice_type
						, cu_invoices.invoice_total
						, IF(cu_invoices.currency='MXP','',cu_invoices.currency_exchange)currency_exchange
						, cu_invoices.currency
						, cu_invoices.ID_orders_alias
					FROM sl_creditmemos
						INNER JOIN cu_invoices_lines USING(ID_creditmemos)
						INNER JOIN cu_invoices USING(ID_invoices)
					WHERE cu_invoices.`Status`='Certified' 
					GROUP BY cu_invoices_lines.ID_invoices
					ORDER BY cu_invoices.ID_invoices DESC
				)invoices ON invoices.ID_creditmemos = sl_creditmemos.ID_creditmemos
				INNER JOIN sl_customers ON sl_customers.ID_customers=sl_creditmemos.ID_customers
				LEFT JOIN sl_terms ON sl_terms.Name=sl_customers.Pterms
			WHERE sl_creditmemos.`Status`='Approved' 
				$add_sql_cms
			GROUP BY sl_creditmemos.ID_creditmemos

			# ----------------------------------------------------------------
			# Se agregan los Anticipos(Customers-Advances) del Cliente
			# ----------------------------------------------------------------
			UNION

			SELECT
				sl_customers.ID_customers
				, sl_customers.company_name
				, sl_customers.`Type` customer_type
				, sl_terms.Name cretid_days
				, sl_customers_advances.ID_customers_advances AS ID_orders
				, sl_customers_advances.`Status` AS `Status`
				, 0 AS ID_invoices
				, '' AS invoice
				#, invoices.pzs
				#, invoices.invoice_type
				, sl_customers_advances.Date AS doc_date
				, '' AS ID_orders_alias
				, 'Anticipos' AS TipoDocumento
				, DATE_ADD(sl_customers_advances.Date, INTERVAL sl_terms.CreditDays DAY)PostedDate
				, DATEDIFF(CURDATE(), DATE_ADD(sl_customers_advances.Date, INTERVAL sl_terms.CreditDays DAY))days
				, sl_customers_advances.Amount TotalFactura
				, sl_customers.Currency AS currency
				, IF(sl_customers_advances.Exchangerates != '' AND sl_customers_advances.Exchangerates IS NOT NULL, sl_customers_advances.Exchangerates, 1) AS currency_exchange
				, (sl_customers_advances.Amount - IFNULL(sl_customers_advances_payments.AmountPay, 0)) AS SaldoAlDia
				, 0 AS NOVENCIDO
				, 0 AS VENCIDO30
				, 0 AS VENCIDO60
				, 0 AS VENCIDO90
				, 0 AS VENCIDO120
				, 0 AS VENCIDOMT120
				, 3 AS Orden
			FROM sl_customers_advances
				LEFT JOIN (
					SELECT sl_customers_advances_payments.ID_customers_advances
						, GROUP_CONCAT(sl_customers_advances_payments.ID_orders)
						, SUM(sl_customers_advances_payments.Amount) AmountPay
					FROM sl_customers_advances_payments
					GROUP BY sl_customers_advances_payments.ID_customers_advances
				)sl_customers_advances_payments ON sl_customers_advances.ID_customers_advances = sl_customers_advances_payments.ID_customers_advances
				INNER JOIN sl_customers ON sl_customers.ID_customers=sl_customers_advances.ID_customers
				LEFT JOIN sl_terms ON sl_terms.Name=sl_customers.Pterms
			WHERE (sl_customers_advances.Amount - IFNULL(sl_customers_advances_payments.AmountPay, 0)) > 0 
				AND sl_customers_advances.`Status` != 'Cancelled'
				$add_sql_cus_ad
				
			# Orden General
			ORDER BY company_name, Orden, TipoDocumento, ID_orders, ID_invoices
			;");

			print "Content-type: application/octetstream\n";
			print "Content-disposition: attachment; filename=$fname\n\n";
			print "$strHeader\r\n";
			
		while ($rec = $sth2->fetchrow_hashref()) {	
			if( $rec->{'TipoDocumento'} ne 'Factura' ){
				$rec->{'SaldoAlDia'} = ($rec->{'SaldoAlDia'} * (-1));
				$rec->{'TotalFactura'} = ($rec->{'TotalFactura'} * (-1));
			}
			#					qq|"ID Cliente","Nombre",		"Tipo", 	"Plazo",	"ID orden",															"Status",				"Factura","Piezas",		"Tipo Factura",		"Fecha Factura",		"Importe Orig Factura",				"Fecha Vencimiento", 		"Dias Mora",		"Moneda",			"Tipo de Cambio",	"Saldo al Dia","No Vencido Total","Vencido 30","Vencido 60","Vencido 90","Vencido 120","Vencido > 120"|;		
			#my $strHeader = qq|"ID Cliente",				"Nombre",					"Tipo",					"Plazo",			"ID Pedido",			"Estatus",		"Numero Orden de Compra",	"Tipo Documento",			"ID Documento",	"Fecha Documento",			"Moneda",			"Importe Orignal Documento",							"Tipo de Cambio",												"Importe Original MXN",									"Fecha Vencimiento",	"Dias Mora",	
			$cust_lines = qq|"$rec->{'ID_customers'}","$rec->{'company_name'}","$rec->{'customer_type'}","$rec->{'cretid_days'}","$rec->{'ID_orders'}","$rec->{'Status'}","$rec->{'ID_orders_alias'}","$rec->{'TipoDocumento'}","$rec->{'invoice'}","$rec->{'doc_date'}","$rec->{'currency'}","|.&format_price(($rec->{'TotalFactura'})).qq|","|.$rec->{'currency_exchange'}.qq|","|.&format_price(($rec->{'TotalFactura'} * $rec->{'currency_exchange'})).qq|","$rec->{'PostedDate'}","$rec->{'days'}",|;#"$rec->{'pzs'}","$rec->{'invoice_type'}",
			$cust_lines .= qq|"|.&format_price(($rec->{'SaldoAlDia'})).qq|","|.&format_price(($rec->{'SaldoAlDia'} * $rec->{'currency_exchange'})).qq|","|.&format_price(($rec->{'NOVENCIDO'})).qq|","|.&format_price(($rec->{'VENCIDO30'})).qq|","|.&format_price(($rec->{'VENCIDO60'})).qq|","|.&format_price(($rec->{'VENCIDO90'})).qq|","|.&format_price(($rec->{'VENCIDO120'})).qq|","|.&format_price(($rec->{'VENCIDOMT120'})).qq|"\r\n|;

			print $cust_lines;
		}
		return;
	}

	print "Content-type: text/html\n\n";
	print &build_page('rep_orders_ar_aging_periods.html');
}

#############################################################################
#############################################################################
#   Function: rep_orders_ar_aging_periods2
#
#       Es: Reporte de Atigüedad de Saldos de CxC
#       En: 
#
#
#    Created on: 27/06/2013
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
sub rep_orders_ar_aging_periods2 {
#############################################################################
#############################################################################
	if($in{'action'}) {
		if ($in{'cons_customer'} and $in{'cons_customer'} eq 'yes') {
			&rep_orders_ar_grouped_aging_periods();
			return;
		}
		$in{'export'}=1;
		my $add_sql = '';
		
		$customer = '';
		$in{'id_customers'} = &filter_values($in{'id_customers'});
		if ($in{'id_customers'}) {
			$add_sql .= "AND sl_orders.ID_customers='$in{'id_customers'}'";
			$customer = "(".$in{'id_customers'}.")";
		}
	
		my $fname   = 'rep_ar_aging_customer'.$customer.'_'.$cfg{'app_title'}.'.csv';
		$fname =~ s/\s/_/g;
		
		my $strHeader = qq|"ID Cliente","Nombre","Tipo","Plazo","ID orden","Status","ID_orders_alias","Factura","Piezas","Tipo Factura","Fecha Factura","Importe Orig Factura","Fecha Vencimiento","Dias Mora","Moneda","Tipo de Cambio","Saldo al Dia","No Vencido Total","Vencido 30","Vencido 60","Vencido 90","Vencido 120","Vencido > 120"|;
		
		print "Content-type: application/octetstream\n";
		print "Content-disposition: attachment; filename=$fname\n\n";
		print "$strHeader\r\n";
		
		
		my $sth2 = &Do_SQL("
			SELECT
				sl_customers.ID_customers
				, sl_customers.company_name
				, sl_customers.Type customer_type
				, sl_terms.Name cretid_days
				, sl_orders.ID_orders
				, sl_orders.Status
				, inovices.invoice
				, inovices.pzs
				, inovices.invoice_type
				, inovices.doc_date
				, inovices.ID_orders_alias
				, date_add(sl_orders.PostedDate, INTERVAL sl_terms.CreditDays DAY)PostedDate
				, DATEDIFF(CURDATE(), date_add(sl_orders.PostedDate, INTERVAL sl_terms.CreditDays DAY))days
				, inovices.invoice_total TotalFactura
				, inovices.currency
				, inovices.currency_exchange
				, IFNULL(sl_orders_products.TotalProducts,0) - IFNULL(payments_paid.AmountPaid,0) as SaldoAlDia
				, (IF(DATEDIFF(CURDATE(), date_add(sl_orders.PostedDate, INTERVAL sl_terms.CreditDays DAY))<0,IFNULL(sl_orders_products.TotalProducts,0) - IFNULL(payments_paid.AmountPaid,0),0))NOVENCIDO
				, (IF(DATEDIFF(CURDATE(), date_add(sl_orders.PostedDate, INTERVAL sl_terms.CreditDays DAY))>=0 AND DATEDIFF(CURDATE(), date_add(sl_orders.PostedDate, INTERVAL sl_terms.CreditDays DAY))<=30,IFNULL(sl_orders_products.TotalProducts,0) - IFNULL(payments_paid.AmountPaid,0),0))VENCIDO30
				, (IF(DATEDIFF(CURDATE(), date_add(sl_orders.PostedDate, INTERVAL sl_terms.CreditDays DAY))>=31 AND DATEDIFF(CURDATE(), date_add(sl_orders.PostedDate, INTERVAL sl_terms.CreditDays DAY))<=60,IFNULL(sl_orders_products.TotalProducts,0) - IFNULL(payments_paid.AmountPaid,0),0))VENCIDO60
				, (IF(DATEDIFF(CURDATE(), date_add(sl_orders.PostedDate, INTERVAL sl_terms.CreditDays DAY))>=61 AND DATEDIFF(CURDATE(), date_add(sl_orders.PostedDate, INTERVAL sl_terms.CreditDays DAY))<=90,IFNULL(sl_orders_products.TotalProducts,0) - IFNULL(payments_paid.AmountPaid,0),0))VENCIDO90
				, (IF(DATEDIFF(CURDATE(), date_add(sl_orders.PostedDate, INTERVAL sl_terms.CreditDays DAY))>=91 AND DATEDIFF(CURDATE(), date_add(sl_orders.PostedDate, INTERVAL sl_terms.CreditDays DAY))<=120,IFNULL(sl_orders_products.TotalProducts,0) - IFNULL(payments_paid.AmountPaid,0),0))VENCIDO120
				, (IF(DATEDIFF(CURDATE(), date_add(sl_orders.PostedDate, INTERVAL sl_terms.CreditDays DAY))>=121,IFNULL(sl_orders_products.TotalProducts,0) - IFNULL(payments_paid.AmountPaid,0),0))VENCIDOMT120
			FROM sl_orders
				LEFT JOIN (
					SELECT SUM(sl_orders_payments.Amount)AmountPaid, COUNT(*)Payments, ID_orders
					FROM sl_orders_payments
					WHERE sl_orders_payments.Status IN ('Approved','Credit')
					AND sl_orders_payments.Captured='Yes'
					AND sl_orders_payments.CapDate > '1900-01-01'
					AND sl_orders_payments.Amount > 0
					GROUP BY sl_orders_payments.ID_orders
				)payments_paid ON payments_paid.ID_orders=sl_orders.ID_orders
				LEFT JOIN (
					SELECT SUM(sl_orders_payments.Amount)AmountPending, COUNT(*)Payments, ID_orders
					FROM sl_orders_payments
					WHERE sl_orders_payments.Status IN ('Approved','Credit')
					AND (sl_orders_payments.Captured<>'Yes' OR sl_orders_payments.Captured IS NULL)
					AND (sl_orders_payments.CapDate IS NULL OR sl_orders_payments.CapDate<'1900-01-01' OR sl_orders_payments.CapDate ='')
					AND sl_orders_payments.Amount > 0
					GROUP BY sl_orders_payments.ID_orders
				)payments_pending ON payments_pending.ID_orders=sl_orders.ID_orders
				LEFT JOIN (
					SELECT SUM(sl_orders_payments.Amount)AmountPending, COUNT(*)Payments, ID_orders
					FROM sl_orders_payments
					WHERE sl_orders_payments.Status IN ('Credit')
					AND (sl_orders_payments.Captured<>'Yes' OR sl_orders_payments.Captured IS NULL)
					AND (sl_orders_payments.CapDate IS NULL OR sl_orders_payments.CapDate<'1900-01-01' OR sl_orders_payments.CapDate ='')
					AND sl_orders_payments.Amount < 0
					GROUP BY sl_orders_payments.ID_orders
				)credits_pending ON credits_pending.ID_orders=sl_orders.ID_orders
				LEFT JOIN (
					SELECT SUM(sl_orders_payments.Amount)AmountTotal, COUNT(*)Payments, ID_orders
					FROM sl_orders_payments
					WHERE sl_orders_payments.Status NOT IN ('Cancelled')
					GROUP BY sl_orders_payments.ID_orders
				)payments_totals ON payments_totals.ID_orders=sl_orders.ID_orders
				INNER JOIN (
					SELECT
						sl_orders_products.ID_orders
						, (SUM(sl_orders_products.SalePrice) + SUM(sl_orders_products.Shipping) + SUM(sl_orders_products.Tax) + SUM(sl_orders_products.ShpTax))- SUM(sl_orders_products.Discount)TotalProducts
					FROM sl_orders_products
					WHERE sl_orders_products.Status NOT IN ('Inactive')
					GROUP BY sl_orders_products.ID_orders
				)sl_orders_products ON sl_orders_products.ID_orders=sl_orders.ID_orders
				LEFT JOIN (
					SELECT 
						ID_invoices
						, cu_invoices_lines.ID_orders
						, concat(cu_invoices.doc_serial
						, cu_invoices.doc_num)invoice
						, DATE(cu_invoices.doc_date)doc_date
						, COUNT(*)pzs
						, cu_invoices.invoice_type
						, cu_invoices.invoice_total
						, IF(cu_invoices.currency='MXP','',cu_invoices.currency_exchange)currency_exchange
						, cu_invoices.currency
						, cu_invoices.ID_orders_alias
					FROM cu_invoices_lines
					LEFT JOIN cu_invoices USING(ID_invoices)
					WHERE cu_invoices.Status='Certified'
					GROUP BY ID_invoices
					
					UNION 
					
					SELECT  
						ID_invoices
						, cu_invoices_lines.ID_orders
						, concat(cu_invoices.doc_serial
						, cu_invoices.doc_num)invoice
						, DATE(cu_invoices.doc_date)doc_date
						, COUNT(*)pzs
						, cu_invoices.invoice_type
						, cu_invoices.invoice_total
						, IF(cu_invoices.currency='MXP','',cu_invoices.currency_exchange)currency_exchange
						, cu_invoices.currency
						, cu_invoices.ID_orders_alias
					FROM sl_creditmemos_payments
					LEFT JOIN cu_invoices_lines ON cu_invoices_lines.ID_creditmemos=sl_creditmemos_payments.ID_creditmemos
					LEFT JOIN cu_invoices USING(ID_invoices)
					WHERE cu_invoices.Status='Certified'
					GROUP BY ID_invoices
					ORDER BY ID_invoices DESC
				)inovices ON inovices.ID_orders = sl_orders.ID_orders
				INNER JOIN sl_customers ON sl_customers.ID_customers=sl_orders.ID_customers
				LEFT JOIN sl_terms ON sl_terms.Name=sl_customers.Pterms
			WHERE sl_orders.Status='Shipped' 
				$add_sql 
				AND ABS(IFNULL(sl_orders_products.TotalProducts,0) - IFNULL(payments_paid.AmountPaid,0)) > 0.01
				AND inovices.invoice_type='ingreso' 
			GROUP BY sl_orders.ID_orders
			ORDER BY sl_customers.company_name, sl_orders.ID_orders, inovices.ID_invoices;");
			
		while ($rec = $sth2->fetchrow_hashref()) {	
			#					qq|"ID Cliente","Nombre",		"Tipo", 	"Plazo",	"ID orden",															"Status",				"Factura","Piezas",		"Tipo Factura",		"Fecha Factura",		"Importe Orig Factura",				"Fecha Vencimiento", 		"Dias Mora",		"Moneda",			"Tipo de Cambio",	"Saldo al Dia","No Vencido Total","Vencido 30","Vencido 60","Vencido 90","Vencido 120","Vencido > 120"|;		
			$cust_lines = qq|"$rec->{'ID_customers'}","$rec->{'company_name'}","$rec->{'customer_type'}","$rec->{'cretid_days'}","$rec->{'ID_orders'}","$rec->{'Status'}","$rec->{'ID_orders_alias'}","$rec->{'invoice'}","$rec->{'pzs'}","$rec->{'invoice_type'}","$rec->{'doc_date'}","|.&format_price(($rec->{'TotalFactura'})).qq|","$rec->{'PostedDate'}","$rec->{'days'}","$rec->{'currency'}","|.&format_price($rec->{'currency_exchange'}).qq|"|;
			$cust_lines .= qq|,"|.&format_price(($rec->{'SaldoAlDia'})).qq|","|.&format_price(($rec->{'NOVENCIDO'})).qq|","|.&format_price(($rec->{'VENCIDO30'})).qq|","|.&format_price(($rec->{'VENCIDO60'})).qq|","|.&format_price(($rec->{'VENCIDO90'})).qq|","|.&format_price(($rec->{'VENCIDO120'})).qq|","|.&format_price(($rec->{'VENCIDOMT120'})).qq|"\r\n|;

			print $cust_lines;
		}
		return;
	}

	print "Content-type: text/html\n\n";
	print &build_page('rep_orders_ar_aging_periods2.html');

}

#############################################################################
#############################################################################
#   Function: rep_orders_ar_grouped_aging_periods
#
#       Es: Reporte de Atigüedad de Saldos de CxC
#       En: 
#
#
#    Created on: 27/06/2013
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
sub rep_orders_ar_grouped_aging_periods {
#############################################################################
#############################################################################
	if($in{'action'}) {
		
		$in{'export'}=1;
		my ($query_list);
		my $maxprod=1;
		my $info_user =	'';
		my $info_pprod = '';
		my $info_oprod = '';
		my $info_time = '';
		my $sql_between = '';
		my $sql_ship_between = '';
		my $sql_idcustomers = '';
		my $add_filters='';
		
		###### Busqueda por rango de fecha
		#$in{'from_date'} = &get_sql_date() if !$in{'from_date'};
		$in{'from_date'} = &filter_values($in{'from_date'});
		$in{'to_date'} = &filter_values($in{'to_date'});
		$in{'from_ship_date'} = &filter_values($in{'from_ship_date'});
		$in{'to_ship_date'} = &filter_values($in{'to_ship_date'});
		$in{'id_customers'} = &filter_values($in{'id_customers'});
		if ($in{'to_date'} and $in{'from_date'}) {
			$sql_between = "AND date_add(sl_orders.PostedDate, INTERVAL sl_terms.CreditDays DAY) BETWEEN '$in{'from_date'}' AND '$in{'to_date'}'";
		} elsif ($in{'from_date'}) {
			$sql_between =  "AND date_add(sl_orders.PostedDate, INTERVAL sl_terms.CreditDays DAY) >= '$in{'from_date'}'";
		} elsif ($in{'to_date'}) {
			$sql_between =  "AND date_add(sl_orders.PostedDate, INTERVAL sl_terms.CreditDays DAY) <= '$in{'to_date'}'";
		}
		
		if ($in{'to_ship_date'} and $in{'from_ship_date'}) {
			$sql_ship_between = "AND sl_orders.PostedDate BETWEEN '$in{'from_ship_date'}' AND '$in{'to_ship_date'}'";
		} elsif ($in{'from_ship_date'}) {
			$sql_ship_between =  "AND sl_orders.PostedDate >= '$in{'from_ship_date'}'";
		} elsif ($in{'to_ship_date'}) {
			$sql_ship_between =  "AND sl_orders.PostedDate <= '$in{'to_ship_date'}'";
		}
		
		if ($in{'id_customers'}) {
			$sql_idcustomers = "AND sl_orders.ID_customers='$in{'id_customers'}'";
		}
		
		my $fname   = 'rep_ar_aging_'.$cfg{'app_title'}.'.csv';
		$fname =~ s/\s/_/g;
		
		# my $strHeader = "ID Cliente, Cliente,  No Vencido 30, No Vencido 60, No Vencido 90, No Vencido > 90, Vencido 30, Vencido 60, Vencido 90, Vencido 120, Vencido > 120, No Vencido Total, Vencido Total, Saldo";
		my $strHeader = qq|"ID Cliente","Cliente","Tipo","Plazo","Saldo","No Vencido Total","Vencido 30","Vencido 60","Vencido 90","Vencido 120","Vencido > 120"|;
		
		print "Content-type: application/octetstream\n";
		print "Content-disposition: attachment; filename=$fname\n\n";
		print "$strHeader\r\n";
		
		
		# my $sth2 = &Do_SQL("SELECT
		# 	sl_orders.ID_orders
		# 	, sl_customers.ID_customers
		# 	, sl_customers.company_name
		# 	, sl_customers.Type customer_type
		# 	, sl_terms.Name cretid_days

		# 	-- , (IFNULL(payments_paid.AmountPaid,0))payments_paid
		# 	-- , (IFNULL(payments_pending.AmountPending,0)) payments_pending

		# 	, SUM(payments_totals.AmountTotal)AmountTotal
		# 	, SUM(IFNULL(payments_pending.AmountPending,0) + IFNULL(credits_pending.AmountPending,0)) as TotalPending
		# 	, SUM(IFNULL(credits_pending.AmountPending,0)) credits_pending
			
		# 	, (IF(DATEDIFF(CURDATE(), date_add(sl_orders.PostedDate, INTERVAL sl_terms.CreditDays DAY))<0,SUM(IFNULL(payments_pending.AmountPending,0) + IFNULL(credits_pending.AmountPending,0)),0))NOVENCIDO
		# 	, (IF(DATEDIFF(CURDATE(), date_add(sl_orders.PostedDate, INTERVAL sl_terms.CreditDays DAY))>=0 AND DATEDIFF(CURDATE(), date_add(sl_orders.PostedDate, INTERVAL sl_terms.CreditDays DAY))<=30,SUM(IFNULL(payments_pending.AmountPending,0) + IFNULL(credits_pending.AmountPending,0)),0))VENCIDO30
		# 	, (IF(DATEDIFF(CURDATE(), date_add(sl_orders.PostedDate, INTERVAL sl_terms.CreditDays DAY))>=31 AND DATEDIFF(CURDATE(), date_add(sl_orders.PostedDate, INTERVAL sl_terms.CreditDays DAY))<=60,SUM(IFNULL(payments_pending.AmountPending,0) + IFNULL(credits_pending.AmountPending,0)),0))VENCIDO60
		# 	, (IF(DATEDIFF(CURDATE(), date_add(sl_orders.PostedDate, INTERVAL sl_terms.CreditDays DAY))>=61 AND DATEDIFF(CURDATE(), date_add(sl_orders.PostedDate, INTERVAL sl_terms.CreditDays DAY))<=90,SUM(IFNULL(payments_pending.AmountPending,0) + IFNULL(credits_pending.AmountPending,0)),0))VENCIDO90
		# 	, (IF(DATEDIFF(CURDATE(), date_add(sl_orders.PostedDate, INTERVAL sl_terms.CreditDays DAY))>=91 AND DATEDIFF(CURDATE(), date_add(sl_orders.PostedDate, INTERVAL sl_terms.CreditDays DAY))<=120,SUM(IFNULL(payments_pending.AmountPending,0) + IFNULL(credits_pending.AmountPending,0)),0))VENCIDO120
		# 	, (IF(DATEDIFF(CURDATE(), date_add(sl_orders.PostedDate, INTERVAL sl_terms.CreditDays DAY))>=121,SUM(IFNULL(payments_pending.AmountPending,0) + IFNULL(credits_pending.AmountPending,0)),0))VENCIDOMT120

		# 	FROM sl_orders

		# 	LEFT JOIN (
		# 		SELECT SUM(sl_orders_payments.Amount)AmountPaid, COUNT(*)Payments, ID_orders
		# 		FROM sl_orders_payments
		# 		WHERE sl_orders_payments.Status IN ('Approved','Credit')
		# 		AND sl_orders_payments.Captured='Yes'
		# 		AND sl_orders_payments.CapDate > '1900-01-01'
		# 		AND sl_orders_payments.Amount > 0
		# 		GROUP BY sl_orders_payments.ID_orders
		# 	)payments_paid ON payments_paid.ID_orders=sl_orders.ID_orders

		# 	LEFT JOIN (
		# 		SELECT SUM(sl_orders_payments.Amount)AmountPending, COUNT(*)Payments, ID_orders
		# 		FROM sl_orders_payments
		# 		WHERE sl_orders_payments.Status IN ('Approved','Credit')
		# 		AND (sl_orders_payments.Captured<>'Yes' OR sl_orders_payments.Captured IS NULL)
		# 		AND (sl_orders_payments.CapDate IS NULL OR sl_orders_payments.CapDate<'1900-01-01' OR sl_orders_payments.CapDate ='')
		# 		AND sl_orders_payments.Amount > 0
		# 		GROUP BY sl_orders_payments.ID_orders
		# 	)payments_pending ON payments_pending.ID_orders=sl_orders.ID_orders

		# 	LEFT JOIN (
		# 		SELECT SUM(sl_orders_payments.Amount)AmountPending, COUNT(*)Payments, ID_orders
		# 		FROM sl_orders_payments
		# 		WHERE sl_orders_payments.Status IN ('Credit')
		# 		AND (sl_orders_payments.Captured<>'Yes' OR sl_orders_payments.Captured IS NULL)
		# 		AND (sl_orders_payments.CapDate IS NULL OR sl_orders_payments.CapDate<'1900-01-01' OR sl_orders_payments.CapDate ='')
		# 		AND sl_orders_payments.Amount < 0
		# 		GROUP BY sl_orders_payments.ID_orders
		# 	)credits_pending ON credits_pending.ID_orders=sl_orders.ID_orders

		# 	LEFT JOIN (
		# 		SELECT SUM(sl_orders_payments.Amount)AmountTotal, COUNT(*)Payments, ID_orders
		# 		FROM sl_orders_payments
		# 		WHERE sl_orders_payments.Status NOT IN ('Cancelled')
		# 		GROUP BY sl_orders_payments.ID_orders
		# 	)payments_totals ON payments_totals.ID_orders=sl_orders.ID_orders
		# 	INNER JOIN sl_customers ON sl_customers.ID_customers=sl_orders.ID_customers
		# 	LEFT JOIN sl_terms ON sl_terms.Name=sl_customers.Pterms

		# 	WHERE sl_orders.Status='Shipped'
		# 	AND (
		# 		SELECT COUNT(*)
		# 		FROM cu_invoices_lines
		# 		LEFT JOIN cu_invoices USING(ID_invoices)
		# 		WHERE cu_invoices.Status='Certified'
		# 		AND cu_invoices_lines.ID_orders = sl_orders.ID_orders
		# 	)>0

		# 	-- AND sl_customers.ID_customers = 100040
			
		# 	-- > > > > > > 
		# 	 AND ((IFNULL(payments_pending.AmountPending,0) + IFNULL(credits_pending.AmountPending,0))) > 0
		# 	-- < < < < < <

		# 	$sql_between
		# 	$sql_ship_between
		# 	$sql_idcustomers
			
		# 	GROUP BY sl_orders.ID_customers
		# 	ORDER BY sl_customers.company_name");

		my $sth2 = &Do_SQL("SELECT
			sl_orders.ID_orders
			, sl_customers.ID_customers
			, sl_customers.company_name
			, sl_customers.Type customer_type
			, sl_terms.Name cretid_days

			-- , (IFNULL(payments_paid.AmountPaid,0))payments_paid
			-- , (IFNULL(payments_pending.AmountPending,0)) payments_pending

			, SUM(payments_totals.AmountTotal)AmountTotal
			, SUM(IFNULL(payments_pending.AmountPending,0) + IFNULL(credits_pending.AmountPending,0)) as TotalPending
			, SUM(IFNULL(credits_pending.AmountPending,0)) credits_pending
			/*
			, (IF(DATEDIFF(CURDATE(), date_add(sl_orders.PostedDate, INTERVAL sl_terms.CreditDays DAY))<0,SUM(IFNULL(payments_pending.AmountPending,0) + IFNULL(credits_pending.AmountPending,0)),0))NOVENCIDO
			, (IF(DATEDIFF(CURDATE(), date_add(sl_orders.PostedDate, INTERVAL sl_terms.CreditDays DAY))>=0 AND DATEDIFF(CURDATE(), date_add(sl_orders.PostedDate, INTERVAL sl_terms.CreditDays DAY))<=30,SUM(IFNULL(payments_pending.AmountPending,0) + IFNULL(credits_pending.AmountPending,0)),0))VENCIDO30
			, (IF(DATEDIFF(CURDATE(), date_add(sl_orders.PostedDate, INTERVAL sl_terms.CreditDays DAY))>=31 AND DATEDIFF(CURDATE(), date_add(sl_orders.PostedDate, INTERVAL sl_terms.CreditDays DAY))<=60,SUM(IFNULL(payments_pending.AmountPending,0) + IFNULL(credits_pending.AmountPending,0)),0))VENCIDO60
			, (IF(DATEDIFF(CURDATE(), date_add(sl_orders.PostedDate, INTERVAL sl_terms.CreditDays DAY))>=61 AND DATEDIFF(CURDATE(), date_add(sl_orders.PostedDate, INTERVAL sl_terms.CreditDays DAY))<=90,SUM(IFNULL(payments_pending.AmountPending,0) + IFNULL(credits_pending.AmountPending,0)),0))VENCIDO90
			, (IF(DATEDIFF(CURDATE(), date_add(sl_orders.PostedDate, INTERVAL sl_terms.CreditDays DAY))>=91 AND DATEDIFF(CURDATE(), date_add(sl_orders.PostedDate, INTERVAL sl_terms.CreditDays DAY))<=120,SUM(IFNULL(payments_pending.AmountPending,0) + IFNULL(credits_pending.AmountPending,0)),0))VENCIDO120
			, (IF(DATEDIFF(CURDATE(), date_add(sl_orders.PostedDate, INTERVAL sl_terms.CreditDays DAY))>=121,SUM(IFNULL(payments_pending.AmountPending,0) + IFNULL(credits_pending.AmountPending,0)),0))VENCIDOMT120
			*/
			, SUM(IF(DATEDIFF(CURDATE(), date_add(sl_orders.PostedDate, INTERVAL sl_terms.CreditDays DAY))<0,IFNULL(payments_pending.AmountPending,0) + IFNULL(credits_pending.AmountPending,0),0))NOVENCIDO
			, SUM(IF(DATEDIFF(CURDATE(), date_add(sl_orders.PostedDate, INTERVAL sl_terms.CreditDays DAY))>=0 AND DATEDIFF(CURDATE(), date_add(sl_orders.PostedDate, INTERVAL sl_terms.CreditDays DAY))<=30,IFNULL(payments_pending.AmountPending,0) + IFNULL(credits_pending.AmountPending,0),0))VENCIDO30
			, SUM(IF(DATEDIFF(CURDATE(), date_add(sl_orders.PostedDate, INTERVAL sl_terms.CreditDays DAY))>=31 AND DATEDIFF(CURDATE(), date_add(sl_orders.PostedDate, INTERVAL sl_terms.CreditDays DAY))<=60,IFNULL(payments_pending.AmountPending,0) + IFNULL(credits_pending.AmountPending,0),0))VENCIDO60
			, SUM(IF(DATEDIFF(CURDATE(), date_add(sl_orders.PostedDate, INTERVAL sl_terms.CreditDays DAY))>=61 AND DATEDIFF(CURDATE(), date_add(sl_orders.PostedDate, INTERVAL sl_terms.CreditDays DAY))<=90,IFNULL(payments_pending.AmountPending,0) + IFNULL(credits_pending.AmountPending,0),0))VENCIDO90
			, SUM(IF(DATEDIFF(CURDATE(), date_add(sl_orders.PostedDate, INTERVAL sl_terms.CreditDays DAY))>=91 AND DATEDIFF(CURDATE(), date_add(sl_orders.PostedDate, INTERVAL sl_terms.CreditDays DAY))<=120,IFNULL(payments_pending.AmountPending,0) + IFNULL(credits_pending.AmountPending,0),0))VENCIDO120
			, SUM(IF(DATEDIFF(CURDATE(), date_add(sl_orders.PostedDate, INTERVAL sl_terms.CreditDays DAY))>=121,IFNULL(payments_pending.AmountPending,0) + IFNULL(credits_pending.AmountPending,0),0))VENCIDOMT120
			
			FROM sl_orders

			LEFT JOIN (
				SELECT SUM(sl_orders_payments.Amount)AmountPaid, COUNT(*)Payments, ID_orders
				FROM sl_orders_payments
				WHERE sl_orders_payments.Status IN ('Approved','Credit')
				AND sl_orders_payments.Captured='Yes'
				AND sl_orders_payments.CapDate > '1900-01-01'
				AND sl_orders_payments.Amount > 0
				GROUP BY sl_orders_payments.ID_orders
			)payments_paid ON payments_paid.ID_orders=sl_orders.ID_orders

			LEFT JOIN (
				SELECT SUM(sl_orders_payments.Amount)AmountPending, COUNT(*)Payments, ID_orders
				FROM sl_orders_payments
				WHERE sl_orders_payments.Status IN ('Approved','Credit')
				AND (sl_orders_payments.Captured<>'Yes' OR sl_orders_payments.Captured IS NULL)
				AND (sl_orders_payments.CapDate IS NULL OR sl_orders_payments.CapDate<'1900-01-01' OR sl_orders_payments.CapDate ='')
				AND sl_orders_payments.Amount > 0
				GROUP BY sl_orders_payments.ID_orders
			)payments_pending ON payments_pending.ID_orders=sl_orders.ID_orders

			LEFT JOIN (
				SELECT SUM(sl_orders_payments.Amount)AmountPending, COUNT(*)Payments, ID_orders
				FROM sl_orders_payments
				WHERE sl_orders_payments.Status IN ('Credit')
				AND (sl_orders_payments.Captured<>'Yes' OR sl_orders_payments.Captured IS NULL)
				AND (sl_orders_payments.CapDate IS NULL OR sl_orders_payments.CapDate<'1900-01-01' OR sl_orders_payments.CapDate ='')
				AND sl_orders_payments.Amount < 0
				GROUP BY sl_orders_payments.ID_orders
			)credits_pending ON credits_pending.ID_orders=sl_orders.ID_orders

			LEFT JOIN (
				SELECT SUM(sl_orders_payments.Amount)AmountTotal, COUNT(*)Payments, ID_orders
				FROM sl_orders_payments
				WHERE sl_orders_payments.Status NOT IN ('Cancelled')
				GROUP BY sl_orders_payments.ID_orders
			)payments_totals ON payments_totals.ID_orders=sl_orders.ID_orders
			
			LEFT JOIN (
				SELECT 
					ID_invoices
					, cu_invoices_lines.ID_orders
					, concat(cu_invoices.doc_serial
					, cu_invoices.doc_num)invoice
					, DATE(cu_invoices.doc_date)doc_date
					, COUNT(*)pzs
					, cu_invoices.invoice_type
					, cu_invoices.invoice_total
					, IF(cu_invoices.currency='MXP','',cu_invoices.currency_exchange)currency_exchange
					, cu_invoices.currency
					, cu_invoices.ID_orders_alias
				FROM cu_invoices_lines
				LEFT JOIN cu_invoices USING(ID_invoices)
				WHERE cu_invoices.Status='Certified'
				GROUP BY ID_invoices
				
				UNION 

				SELECT  
					ID_invoices
					, cu_invoices_lines.ID_orders
					, concat(cu_invoices.doc_serial
					, cu_invoices.doc_num)invoice
					, DATE(cu_invoices.doc_date)doc_date
					, COUNT(*)pzs
					, cu_invoices.invoice_type
					, cu_invoices.invoice_total
					, IF(cu_invoices.currency='MXP','',cu_invoices.currency_exchange)currency_exchange
					, cu_invoices.currency
					, cu_invoices.ID_orders_alias
				FROM sl_creditmemos_payments
				LEFT JOIN cu_invoices_lines ON cu_invoices_lines.ID_creditmemos=sl_creditmemos_payments.ID_creditmemos
				LEFT JOIN cu_invoices USING(ID_invoices)
				WHERE cu_invoices.Status='Certified'
				GROUP BY ID_invoices
			)inovices ON inovices.ID_orders = sl_orders.ID_orders

			INNER JOIN sl_customers ON sl_customers.ID_customers=sl_orders.ID_customers
			LEFT JOIN sl_terms ON sl_terms.Name=sl_customers.Pterms

			WHERE sl_orders.Status='Shipped'

			-- AND sl_customers.ID_customers = 100040
			
			-- > > > > > > 
			 AND ((IFNULL(payments_pending.AmountPending,0) + IFNULL(credits_pending.AmountPending,0))) > 0
			-- < < < < < <

			$sql_between
			$sql_ship_between
			$sql_idcustomers
			
			GROUP BY sl_orders.ID_customers
			ORDER BY sl_customers.company_name");
			
		while ($rec = $sth2->fetchrow_hashref()) {
			
			$cust_lines = qq|"$rec->{'ID_customers'}","$rec->{'company_name'}","$rec->{'customer_type'}","$rec->{'cretid_days'}","|.&format_price(abs($rec->{'TotalPending'})).qq|","|.&format_price(abs($rec->{'NOVENCIDO'})).qq|"|;
			
			$cust_lines .= qq|,"|.&format_price(abs($rec->{'VENCIDO30'})).qq|"|;

			$cust_lines .= qq|,"|.&format_price(abs($rec->{'VENCIDO60'})).qq|"|;

			$cust_lines .= qq|,"|.&format_price(abs($rec->{'VENCIDO90'})).qq|"|;

			$cust_lines .= qq|,"|.&format_price(abs($rec->{'VENCIDO120'})).qq|"|;
			
			$cust_lines .= qq|,"|.&format_price(abs($rec->{'VENCIDOMT120'})).qq|"\r\n|;
			
			print $cust_lines;
			
		}
		return;
	}
	print "Content-type: text/html\n\n";
	print &build_page('rep_orders_ar_aging_periods.html');

}

#############################################################################
#############################################################################
#   Function: rep_orders_ar_order_payments
#
#       Es: Reporte de Cobros por Orden para CxC
#       En: 
#
#
#    Created on: 02/07/2013
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
sub rep_orders_ar_order_payments {
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
		my $sql_idcustomers = '';
		my $add_filters='';
		
		###### Busqueda por rango de fecha
		#$in{'from_date'} = &get_sql_date() if !$in{'from_date'};
		$in{'from_date'} = &filter_values($in{'from_date'});
		$in{'to_date'} = &filter_values($in{'to_date'});
		$in{'id_customers'} = &filter_values($in{'id_customers'});
		if ($in{'to_date'} and $in{'from_date'}) {
			$sql_between = "AND sl_orders_payments.CapDate BETWEEN '$in{'from_date'}' AND '$in{'to_date'}'";
		} elsif ($in{'from_date'}) {
			$sql_between =  "AND sl_orders_payments.CapDate >= '$in{'from_date'}'";
		} elsif ($in{'to_date'}) {
			$sql_between =  "AND sl_orders_payments.CapDate <= '$in{'to_date'}'";
		}
		
		if ($in{'id_customers'}) {
			$sql_idcustomers = "AND sl_orders.ID_customers='$in{'id_customers'}'";
		}
		
		my $fname   = 'rep_ar_payments_'.$cfg{'app_title'}.'.csv';
		$fname =~ s/\s/_/g;
		
		
		my $strHeader = "UN, ID Orden, ID Cliente, Cliente, Fecha Orden, Monto Pagado, Factura, Orden Compra, Nota Orden";
		my ($sth) = &Do_SQL("SELECT COUNT(*) FROM sl_orders 
		LEFT JOIN sl_orders_payments ON sl_orders.ID_orders=sl_orders_payments.ID_orders
		LEFT JOIN sl_terms ON (sl_orders.Pterms=sl_terms.Name AND sl_terms.Type='Sales')
		INNER JOIN sl_customers ON (sl_orders.ID_customers=sl_customers.ID_customers)
		LEFT JOIN cu_company_legalinfo ON cu_company_legalinfo.PrimaryRecord='Yes' WHERE 1 
		AND sl_orders.Status='Shipped'
		$sql_between
		$sql_idcustomers
		AND sl_orders_payments.Status='Approved'
		AND sl_orders_payments.Captured='Yes'
		AND sl_orders_payments.CapDate IS NOT NULL
		AND sl_orders_payments.CapDate != '0000-00-00' HAVING (SUM(IF(Captured='Yes',Amount,0)) > 0);");
		my ($total) = $sth->fetchrow();
		
		
		
		
		if($total) {
			print "Content-type: application/octetstream\n";
			print "Content-disposition: attachment; filename=$fname\n\n";
			print "$strHeader\r\n";
			
			
			
			my $sth2 = &Do_SQL("SELECT
								`cu_company_legalinfo`.`Name`,
								`sl_orders`.`ID_orders`,
								`sl_orders`.`ID_customers`,
								`sl_customers`.`company_name`,
								`sl_orders`.`Date`,
								(SUM(IF (Captured = 'Yes', Amount, 0))) as paid,
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
												) SEPARATOR ' / '
											)
										FROM
											cu_invoices_lines
										LEFT JOIN cu_invoices ON cu_invoices_lines.ID_invoices = cu_invoices.ID_invoices
										WHERE
											cu_invoices_lines.ID_orders = sl_orders.ID_orders
										AND cu_invoices. STATUS <> 'Cancelled'
										AND cu_invoices. STATUS <> 'Void' /*GROUP BY cu_invoices.ID_invoices*/
										ORDER BY
											cu_invoices.invoice_type ASC
									)) as invoices,
								`sl_orders`.`ID_orders_alias`,
								`sl_orders`.`OrderNotes`,
								`sl_orders_payments`.`CapDate`
							FROM
								sl_orders
							LEFT JOIN sl_orders_payments ON sl_orders.ID_orders = sl_orders_payments.ID_orders
							LEFT JOIN sl_terms ON (
								sl_orders.Pterms = sl_terms. NAME
								AND sl_terms.Type = 'Sales'
							)
							INNER JOIN sl_customers ON (
								sl_orders.ID_customers = sl_customers.ID_customers
							)
							LEFT JOIN cu_company_legalinfo ON cu_company_legalinfo.PrimaryRecord = 'Yes'
							WHERE
								1
							AND sl_orders. STATUS = 'Shipped'
							$sql_between
							$sql_idcustomers
							AND sl_orders_payments. STATUS = 'Approved'
							AND sl_orders_payments.Captured = 'Yes'
							AND sl_orders_payments.CapDate IS NOT NULL
							AND sl_orders_payments.CapDate != '0000-00-00'
							GROUP BY
								sl_orders.ID_orders
							HAVING
								(SUM(IF (Captured = 'Yes', Amount, 0)) > 0);");
			
			
			my $records = 0;
			while ($rec = $sth2->fetchrow_hashref()) {
				$records++;
				#############################################################################
				$strout = qq|"$rec->{'Name'}","$rec->{'ID_orders'}","$rec->{'ID_customers'}","$rec->{'company_name'}","$rec->{'Date'}","$rec->{'paid'}","$rec->{'invoices'}","$rec->{'ID_orders_alias'}","$rec->{'OrderNotes'}"|;
				
				#########################################################################################################
				
				$strout .= qq|\r\n|;	
				print $strout;
				return if ($records > 1300);
			}
			return;
		} else {
			$va{'message'} = &trans_txt('search_nomatches');
		}
	}
	
	print "Content-type: text/html\n\n";
	print &build_page('rep_orders_ar_order_payments.html');

}

#############################################################################
#############################################################################
#   Function: rep_orders_ar_customer_payments
#
#       Es: Reporte de Pagos por Cliente
#       En: 
#
#
#    Created on: 14/06/2013
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
sub rep_orders_ar_customer_payments {
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
		if ($in{'to_date'} and $in{'from_date'}) {
			$sql_between = "AND sl_banks_movements.BankDate BETWEEN '$in{'from_date'}' AND '$in{'to_date'}'";
		} elsif ($in{'from_date'}) {
			$sql_between =  "AND sl_banks_movements.BankDate >= '$in{'from_date'}'";
		} elsif ($in{'to_date'}) {
			$sql_between =  "AND sl_banks_movements.BankDate <= '$in{'to_date'}'";
		}
		
		
		my $fname   = 'rep_ar_cust_payments_'.$cfg{'app_title'}.'.csv';
		$fname =~ s/\s/_/g;
		
		
		my $strHeader = "ID Cliente, Razon Social, Pago";
		my ($sth) = &Do_SQL("SELECT
								COUNT(*)
								FROM sl_orders 
								LEFT JOIN sl_orders_payments ON sl_orders.ID_orders=sl_orders_payments.ID_orders
								LEFT JOIN sl_terms ON (sl_orders.Pterms=sl_terms.Name AND sl_terms.Type='Sales')
								INNER JOIN sl_customers ON (sl_customers.ID_customers=sl_orders.ID_customers)
								left join sl_banks_movrel ON (sl_banks_movrel.tablename='orders_payments' AND sl_banks_movrel.tableid=sl_orders_payments.ID_orders_payments)
								inner join sl_banks_movements using (ID_banks_movements)
								WHERE 1
									AND sl_orders.Status='Shipped'
									AND sl_orders_payments.Status='Approved'
									AND sl_orders_payments.Captured='Yes'
									AND sl_orders_payments.CapDate IS NOT NULL
									AND sl_orders_payments.CapDate != '0000-00-00'
								$sql_between;");	
		my ($total) = $sth->fetchrow();
		
		if($total) {
			print "Content-type: application/octetstream\n";
			print "Content-disposition: attachment; filename=$fname\n\n";
			print "$strHeader\r\n";
			
			
			my $sth2 = &Do_SQL("SELECT
									sl_banks_movements.BankDate,
									sl_customers.ID_customers,
									sl_customers.company_name,
									/*sl_orders.ID_orders,*/
									/*sl_orders.ID_orders_alias,*/
									DATEDIFF(CURDATE(),sl_orders.PostedDate) AS df1,
									SUM(IF(Captured='Yes',sl_orders_payments.Amount,0)) AS Paid
									
									FROM sl_orders 
									LEFT JOIN sl_orders_payments ON sl_orders.ID_orders=sl_orders_payments.ID_orders
									LEFT JOIN sl_terms ON (sl_orders.Pterms=sl_terms.Name AND sl_terms.Type='Sales')
									INNER JOIN sl_customers ON (sl_customers.ID_customers=sl_orders.ID_customers)
									left join sl_banks_movrel ON (sl_banks_movrel.tablename='orders_payments' AND sl_banks_movrel.tableid=sl_orders_payments.ID_orders_payments)
									inner join sl_banks_movements using (ID_banks_movements)
									WHERE 1
									AND sl_orders.Status='Shipped'
									AND sl_orders_payments.Status='Approved'
									AND sl_orders_payments.Captured='Yes'
									AND sl_orders_payments.CapDate IS NOT NULL
									AND sl_orders_payments.CapDate != '0000-00-00'
									$sql_between
								GROUP BY sl_customers.ID_customers
								HAVING (Paid > 0)
								ORDER BY sl_customers.company_name DESC;");
			
			my $records = 0;
			while ($rec = $sth2->fetchrow_hashref()) {
				
				my $strout = qq|"$rec->{'ID_customers'}","$rec->{'company_name'}","$rec->{'Paid'}"\r\n|;
				print $strout;
			}
			return;
		} else {
			$va{'message'} = &trans_txt('search_nomatches');
		}
	}
	
	print "Content-type: text/html\n\n";
	print &build_page('rep_orders_ar_cust_payments.html');

}

#############################################################################
#############################################################################
#   Function: rep_orders_logistics
#
#       Es: Reporte de logistica de ordenes de ventas 
#       En: Report logistics sales orders
#
#
#    Created on: 20/05/2013
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
#
#   See Also:
#
#      <>
#
sub rep_orders_logistics{
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
		
		my $fname   = 'orders_logistics_'.$cfg{'app_title'}.'.csv';
		$fname =~ s/\s/_/g;
		
		my $strHeader = "Fecha de pedido,No de pedido Direksys,Orden compra,Id cliente,Nombre cliente,No de factura,Fecha de factura,Importe sin IVA,Importe con IVA,Status factura,Status orden";

		my ($sth) = &Do_SQL("SELECT COUNT(*) FROM sl_orders WHERE 1 AND Date BETWEEN  '$in{'from_date'}' AND '$in{'to_date'}' $add_filters;");
		my ($total) = $sth->fetchrow();


		if($total) {

			print "Content-type: application/octetstream\n";
			print "Content-disposition: attachment; filename=$fname\n\n";
			print "$strHeader\r\n";
			my $join = ($in{'winvoice'})?'INNER ':'LEFT ';
			$add_filters .= " AND sl_orders.Status='".&filter_values($in{'status'})."'" if ($in{'status'} ne '');

			my $sth2 = &Do_SQL("SELECT 
								sl_orders.Date,ID_orders, sl_orders.ID_orders_alias,sl_orders.ID_customers,company_name
								,cu_invoices.ID_invoices
								,concat(cu_invoices.doc_serial,'-',cu_invoices.doc_num)factura
								,cu_invoices.doc_date fecha_factura
								,cu_invoices.invoice_net as total_siva
								,cu_invoices.invoice_total as total_civa
								,cu_invoices.Status as invoice_status
								,sl_orders.Status as order_status
								FROM sl_orders
								INNER JOIN sl_customers USING(ID_customers)
								$join JOIN cu_invoices_lines USING(ID_orders)
								$join JOIN cu_invoices ON cu_invoices.ID_invoices=cu_invoices_lines.ID_invoices AND cu_invoices.Status IN ('Certified', 'Cancelled')
								WHERE 1
								AND sl_orders.Date BETWEEN '$in{'from_date'}' AND '$in{'to_date'}'
								AND sl_orders.Status NOT IN('System Error','Converted') $add_filters
								GROUP BY ID_orders, ID_invoices
								ORDER BY ID_orders,sl_orders.Date;");

			my $records = 0;
			while ($rec = $sth2->fetchrow_hashref()) {
				$records++;

				
				my $strout = qq|"$rec->{'Date'}","$rec->{'ID_orders'}","$rec->{'ID_orders_alias'}","$rec->{'ID_customers'}","$rec->{'company_name'}","$rec->{'factura'}","$rec->{'fecha_factura'}","$rec->{'total_siva'}","$rec->{'total_civa'}","$rec->{'invoice_status'}","$rec->{'order_status'}"\r\n|;

				print $strout;
			}
			&auth_logging('report_view','');
			return;

		}
	}
	
	print "Content-type: text/html\n\n";
	print &build_page('rep_orders_logistics.html');

}

sub rep_orders_new_costs {
#############################################################################
#############################################################################
	
	if($in{'action'}) {
		my $fname   = 'rep_costs'.$cfg{'app_title'}.'.csv';
		$fname =~ s/\s/_/g;

		my $strHeader = qq|"UPC","SKU","DESCRIPCION","FECHA DE ULTIMA RECEPCION Y/O COSTO HISTORICO","MONEDA","COSTO DE RECEPCION","TIPO DE CAMBIO","COSTO DE RECEPCION EN PESOS","GASTO DE ATERRIZAJE","COSTO TOTAL"|;
		
		print "Content-type: application/octetstream\n";
		print "Content-disposition: attachment; filename=$fname\n\n";
		print "$strHeader\r\n";
		
		
		my $sth1 = &Do_SQL("SELECT 
			sl_parts.ID_parts
			-- sl_skus.ID_products
			, sl_skus.ID_sku_products
			, sl_parts.Model
			, sl_parts.Name
			, sl_skus.UPC
			FROM sl_parts
			INNER JOIN sl_skus ON sl_parts.ID_parts=sl_skus.ID_products 
			AND (sl_skus.ID_sku_products>=400000000 AND sl_skus.ID_sku_products<500000000)
			AND sl_skus.Status='Active' ORDER BY Model,Name");
			
		while ($rec = $sth1->fetchrow_hashref()) {
			my $sku = $rec->{'ID_sku_products'};
			my $upc = $rec->{'UPC'};
			# my $description = $rec->{'Model'}.'/'.$rec->{'Name'};
			my $description = $rec->{'Name'};

			# Ultimo costo de compra/recepcion
			my $sth2 = &Do_SQL("SELECT 
				sl_wreceipts.Date
				, sl_purchaseorders_items.ID_products
				, sl_purchaseorders_items.Price
				, sl_vendors.Currency
				, sl_exchangerates.exchange_rate 
				, sl_wreceipts.ID_wreceipts
				,sl_purchaseorders.ID_purchaseorders
				FROM sl_purchaseorders
				INNER JOIN sl_purchaseorders_items USING(ID_purchaseorders)
				INNER JOIN sl_wreceipts ON sl_wreceipts.ID_purchaseorders=sl_purchaseorders.ID_purchaseorders
				INNER JOIN sl_wreceipts_items ON sl_wreceipts_items.ID_products=sl_purchaseorders_items.ID_products AND sl_wreceipts_items.ID_wreceipts=sl_wreceipts.ID_wreceipts
				INNER JOIN sl_vendors ON sl_purchaseorders.ID_vendors=sl_vendors.ID_vendors
				LEFT JOIN sl_exchangerates ON (sl_wreceipts.ID_exchangerates=sl_exchangerates.ID_exchangerates)
				WHERE sl_purchaseorders_items.ID_products = '".$rec->{'ID_sku_products'}."'
				ORDER BY sl_wreceipts.Date DESC, sl_wreceipts.Time DESC LIMIT 1");
			$rec2 = $sth2->fetchrow_hashref();

			my $id_wreceipts = $rec2->{'ID_wreceipts'};
			my $id_purchaseorders = $rec2->{'ID_purchaseorders'};
			my $date_wreceipts = $rec2->{'Date'};
			my $cost = $rec2->{'Price'};
			my $currency = $rec2->{'Currency'};
			my $exchange_rate = $rec2->{'exchange_rate'};

			# Nota de la recepcion
			my $sth3 = &Do_SQL("SELECT Notes
				FROM sl_purchaseorders_notes 
				WHERE sl_purchaseorders_notes.ID_purchaseorders = '".$id_purchaseorders."'
				AND sl_purchaseorders_notes.Notes LIKE('W. Receipt: ".$id_wreceipts."\nProduct: (".$rec->{'ID_sku_products'}.")%Adj. Value%')");
			my $notes;
			while ($rec3 = $sth3->fetchrow_hashref()) {
				$notes .= $rec3->{'Notes'}.'';
			}

			# Si no hay recepcion (nunca se ha comprado)
			# Intentar obtener el dato del HISTORICO
			if (!$id_wreceipts and !$cost){
				my $sth4 = &Do_SQL("SELECT Cost, Date FROM sl_skus_cost WHERE 1 AND sl_skus_cost.ID_products='".$rec->{'ID_sku_products'}."' AND (Cost IS NOT NULL AND Cost>0) ORDER BY Date DESC, Time DESC LIMIT 1");
				$rec4 = $sth4->fetchrow_hashref();
				if ($rec4->{'Cost'}){					
					$cost = $rec4->{'Cost'};
					$notes = 'Extraido del ultimo registro encontrado en inventarios';
					$date_wreceipts = $rec4->{'Date'};
					$currency = 'MX$';
				}

			}

			my $cost_mx = ($exchange_rate > 0)? ( $cost * $exchange_rate ) : $cost;

			$cust_lines = qq|"$upc","$sku","$description","$date_wreceipts","$currency","$cost","$exchange_rate","$cost_mx","$notes",""\r\n|;

			print $cust_lines;
			
		}
		return;
	}
	# $va{'message'}='asdasdasd';
	print "Content-type: text/html\n\n";
	print &build_page('rep_costs.html');

}


sub rep_orders_file {
#############################################################################
#############################################################################

	#my($invalid_character) = $in{'list_id_orders'} =~ /([^\d])/g;
	
	if($in{'action'} and $invalid_character eq '') {

		## To Array for formating
		my (@ary) = split(/\s+|,|\n|\t/,$in{'list_id_orders'});

		$va{'message'} = '';

		my $strHeader = qq|"ACTION","DATE","MESSAGE","IP","USER","APPLICATION","MULTIAPP"|;
		my $query = "	SELECT
							Action 
							, CONCAT(LogDate, ' ', LogTime)As LogDateTime
							, Message
							, IP
							, CONCAT(FirstName, ' ', LastName)AS User
							, admin_users.Application
							, MultiApp 
						FROM 
							admin_vlogs INNER JOIN admin_users USING(ID_admin_users) 
						WHERE 
							tbl_name='sl_orders' 
							AND Action IN('". join("','", @ary) . "')
					UNION
	
						SELECT
							`Action` 
							, CONCAT(LogDate, ' ', LogTime)As LogDateTime
							, Message
							, IP
							, CONCAT(FirstName, ' ', LastName)AS User
							, admin_users.Application
							, MultiApp 
						FROM 
							admin_logs INNER JOIN admin_users USING(ID_admin_users) 
						WHERE 
							tbl_name='sl_orders' 
							AND Action IN('". join("','", @ary) . "')

					UNION

						SELECT
							sl_orders_notes.ID_orders AS `Action` 
							, CONCAT(sl_orders_notes.Date, ' ', sl_orders_notes.Time)As LogDateTime
							, sl_orders_notes.Notes AS Message
							, '' AS IP
							, CONCAT(FirstName, ' ', LastName)AS User
							, admin_users.Application
							, MultiApp 
						FROM 
							sl_orders_notes INNER JOIN admin_users USING(ID_admin_users) 
						WHERE 
							sl_orders_notes.ID_orders IN(". join(",", @ary) . ")

					ORDER BY
					LogDateTime DESC;";

		my ($sth) = &Do_SQL($query);
		my ($this_records) = $sth->rows();

		if($this_records){

			my $fname   = 'rep_order_file_'.$cfg{'app_title'}.'_'. &get_sql_date() . '.csv';
			$fname =~ s/\s/_/g;

			#print "Content-type: text/html\n\n"; # debug
			print "Content-type: application/octetstream\n";
			print "Content-disposition: attachment; filename=$fname\n\n";
			print "$strHeader\r\n";

			while (my ($action, $date, $message, $ip, $user, $app, $multiapp) = $sth->fetchrow()) {

				$cust_lines = qq|"$action","$date","$message","$ip","$user","$app","$multiapp"\r\n|;
				print $cust_lines;
				
			}
			return;

		}else{

			$va{'message'} = trans_txt('search_nomatches');

		}

	}elsif($invalid_character ne ''){
		$va{'message'} = trans_txt('rep_orders_files_invalid_character')."  [ $invalid_character ]";
	}
 
 	print "Content-type: text/html\n\n";
	print &build_page('rep_orders_file.html');

}

#############################################################################
#############################################################################
#   Function: rep_orders_entry_apply
#
#       Es: Reporte de aplicacion ingresos
#       En: 
#
#
#    Created on: 14/10/2016
#
#    Author: ISC Gilberto Q. C.
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
sub rep_orders_entry_apply {
#############################################################################
#############################################################################
	
	if($in{'action'}) {

		my $sql_where = '';	
		### ID Orders	
		if( $in{'id_orders_equal'} ){
			$sql_where = " AND sl_orders.ID_orders = ".int($in{'id_orders'});
		} else {
			if( $in{'id_orders_from'} ){
				$sql_where .= " AND sl_orders.ID_orders >= ".int($in{'id_orders_from'});
			}
			if( $in{'id_orders_to'} ){
				$sql_where .= " AND sl_orders.ID_orders <= ".int($in{'id_orders_to'});
			}
		}
		### Channel
		if( $in{'channel'} ){
			$sql_where .= " AND sl_orders.ID_salesorigins = ".int($in{'channel'});
		}
		### PType
		if( $in{'ptype'} ){
			$sql_where .= " AND sl_orders.Ptype = '".$in{'ptype'}."'";
		}
		### Order Status
		if( $in{'order_status'} ){
			$sql_where .= " AND sl_orders.`Status` = '".$in{'channel'}."'";
		}
		### Order Date
		if( $in{'orderdate_equal'} ){
			$sql_where .= " AND sl_orders.Date = '".$in{'orderdate_equal'}."'";
		} else {
			if( $in{'orderdate_from'} ){
				$sql_where .= " AND sl_orders.Date >= '".$in{'orderdate_from'}."'";
			}
			if( $in{'orderdate_to'} ){
				$sql_where .= " AND sl_orders.Date <= '".$in{'orderdate_to'}."'";
			}
		}
		### Bank Date
		if( $in{'bankdate_equal'} ){
			$sql_where .= " AND sl_orders_payments.CapDate = '".$in{'bankdate_equal'}."'";
		} else {
			if( $in{'bankdate_from'} ){
				$sql_where .= " AND sl_orders_payments.CapDate >= '".$in{'bankdate_from'}."'";
			}
			if( $in{'bankdate_to'} ){
				$sql_where .= " AND sl_orders_payments.CapDate <= '".$in{'bankdate_to'}."'";
			}
		}
		### Bank Name
		if( $in{'bankname'} ){
			$sql_where .= " AND sl_banks.Name LIKE '%".$in{'bankname'}."%'";
		}
		### Facturado
		my $sql_having = '';
		if( $in{'facturado'} ){
			$sql_having = " HAVING Facturado = '".$in{'facturado'}."'";
		}

		my $fname   = 'Aplicacion_ingresos-'.$cfg{'app_title'}.'.csv';
		$fname =~ s/\s/_/g;

		my $strHeader = qq|"ID PEDIDO","CANAL","TIPO DE PEDIDO","TIPO DE TARJETA","ESTATUS DE PEDIDO","FECHA PEDIDO","FECHA DE BANCO","MONTO","FACTURA","FECHA FACTURA","MONTO NETO","IVA","TOTAL","ID BANCO","BANCO","FACTURADO","JOURNAL"|;
		
		print "Content-type: application/octetstream\n";
		print "Content-disposition: attachment; filename=$fname\n\n";
		print "$strHeader\r\n";
		
		my $sql = "SELECT sl_orders.ID_orders
						, sl_salesorigins.Channel
						, sl_orders.Ptype
						, sl_orders_payments.PmtField1
						, sl_orders.`Status`
						, sl_orders.Date
						, sl_orders_payments.CapDate
						, sl_orders_payments.Amount
						, CONCAT(cu_invoices.doc_serial, cu_invoices.doc_num) Invoice
						, CONCAT(cu_invoices.doc_serial, cu_invoices.doc_num) Invoice
						, cu_invoices.invoice_net AS InvoiceNet
						, cu_invoices.total_taxes_transfered AS InvoiceTax
						, cu_invoices.invoice_total AS InvoiceTotal
						, DATE(cu_invoices.doc_date) AS InvoiceDate
						, sl_banks.ID_banks
						, sl_banks.Name
						, IF(cu_invoices.ID_invoices IS NULL, 'NO', 'SI') Facturado
						, sl_movements.ID_journalentries
					FROM sl_orders 
						INNER JOIN sl_salesorigins USING(ID_salesorigins) 
						INNER JOIN sl_orders_payments ON sl_orders.ID_orders=sl_orders_payments.ID_orders 
						LEFT JOIN cu_invoices_lines ON cu_invoices_lines.ID_orders=sl_orders.ID_orders 
						LEFT JOIN cu_invoices ON cu_invoices_lines.ID_invoices=cu_invoices.ID_invoices 
						INNER JOIN sl_movements ON sl_orders_payments.ID_orders_payments = sl_movements.ID_tablerelated 
							AND sl_movements.tablerelated = 'sl_orders_payments' 
							AND sl_movements.Category = 'Anticipo Clientes' 
							AND sl_movements.Credebit = 'Debit' 
						INNER JOIN sl_banks ON sl_movements.ID_accounts = sl_banks.ID_accounts 
					WHERE 1 
						AND sl_orders_payments.Captured = 'Yes' 
						AND sl_orders_payments.Capdate IS NOT NULL 
						AND sl_orders_payments.Capdate != '0000-00-00' 
						AND sl_orders_payments.Capdate != '' 
						AND sl_orders_payments.Amount >= 0 
						AND sl_orders_payments.Reason != 'Refund' 
						$sql_where
					GROUP BY sl_orders_payments.ID_orders_payments 
					$sql_having
					ORDER BY sl_orders.ID_orders DESC;";
		my $sth = &Do_SQL($sql);
			
		while ($rec = $sth->fetchrow_hashref()) {
			
			$rec->{'InvoiceNet'} = &format_price($rec->{'InvoiceNet'}) if($rec->{'InvoiceNet'} > 0);
			$rec->{'InvoiceTax'} = &format_price($rec->{'InvoiceTax'}) if($rec->{'InvoiceTax'} > 0);
			$rec->{'InvoiceTotal'} = &format_price($rec->{'InvoiceTotal'}) if($rec->{'InvoiceTotal'} > 0);

			$cust_lines = qq|"$rec->{'ID_orders'}","$rec->{'Channel'}","$rec->{'Ptype'}","$rec->{'PmtField1'}","$rec->{'Status'}","$rec->{'Date'}","$rec->{'CapDate'}","$rec->{'Amount'}","$rec->{'Invoice'}","$rec->{'InvoiceDate'}","$rec->{'InvoiceNet'}","$rec->{'InvoiceTax'}","$rec->{'InvoiceTotal'}","$rec->{'ID_banks'}","$rec->{'Name'}","$rec->{'Facturado'}","$rec->{'ID_journalentries'}"\r\n|;

			print $cust_lines;
			
		}
		return;
	}

	print "Content-type: text/html\n\n";
	print &build_page('rep_orders_entry_apply.html');

}

1;