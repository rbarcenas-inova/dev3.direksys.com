sub load_tabsconf {
# --------------------------------------------------------
	if ($in{'tab'} eq 2){
		## Notes Tab
		$va{'tab_type'}  = 'notes';
		$va{'tab_title'} = &trans_txt('notes');
		$va{'tab_table'} = 'sl_warehouses_batches_notes';
	}elsif($in{'tab'} eq 3){
		## Notes Tab
		$va{'tab_type'}  = 'logs';
		$va{'tab_title'} = &trans_txt('logs');
		$va{'tab_table'} = 'sl_warehouses_batches';
	}
}


#############################################################################
#############################################################################
#   Function: load_tabs1
#
#       Es: carga el tab uno
#       En: 
#
#   Created on: 07/10/2008  16:21:10
#
#   Author: Pablo Hdez.
#
#   Modifications:
#
#   Parameters:
#
#     - id_warehouses : ID_warehouses
#     - id_warehouses_batches : ID_warehouses_batches
#
#  Returns:
#
#      - searchresults : searchresults
#
#  See Also:
#
#  Todo:
#
sub load_tabs1 {
#############################################################################
#############################################################################

	my (@c) = split(/,/,$cfg{'srcolors'});
	$va{'idcounts'} ='';
	$batch_status = &load_name('sl_warehouses_batches','ID_warehouses_batches',$in{'id_warehouses_batches'},'Status');
  	if($in{'id_warehouses'} eq '' && $in{'id_warehouses_batches'} ){
  		my $sth = &Do_SQL("SELECT ID_warehouses  FROM sl_warehouses_batches WHERE ID_warehouses_batches=".&filter_values($in{'id_warehouses_batches'}));
  		$in{'id_warehouses'} = $sth->fetchrow;
  	}
	
	my $sth = &Do_SQL("SELECT 
							sl_orders.ID_orders
							, COUNT(DISTINCT sl_warehouses_batches_orders.ID_orders_products)AS InBatch
							, SUM(IF(sl_orders_products.Status = 'ReShip',1,0))AS ToReship
							, SUM(IF(sl_orders_products.Status = 'Exchange',1,0))AS ToExchange
							, sl_orders.Ptype, sl_orders.Date
		                    , sl_orders.shp_Zip, sl_orders.shp_City, sl_orders.shp_State
		                    , sl_warehouses_batches.ID_warehouses_batches
		                    , sl_warehouses_batches_orders.Status
		                    , sl_warehouses_batches.Status as Status_wh
					   FROM sl_orders 
					   INNER JOIN sl_orders_products
					   USING(ID_orders)
					   INNER JOIN sl_warehouses_batches_orders
					   USING(ID_orders_products)
					   INNER JOIN sl_warehouses_batches
					   USING(ID_warehouses_batches)
					   WHERE sl_warehouses_batches.ID_warehouses = '$in{'id_warehouses'}'
					   AND sl_warehouses_batches.ID_warehouses_batches = '$in{'id_warehouses_batches'}'
					   GROUP BY sl_orders.ID_orders
					   ORDER BY sl_orders.ID_orders");
 
  	$va{'matches'}=$sth->rows;
  	$va{'pageslist'} = 1;

 	if ($sth->rows>0){	

		while ($rec = $sth->fetchrow_hashref){

			$d = 1 - $d;
			$va{'idcounts'} .= $rec->{'ID_orders'}.",";
			
			my $dynamic_cancel;
			my $dynamic_order_warning;
			my $dynamic_order_reasign;
			my $imgw = '';
			my $id_orders_string = $rec->{'ID_orders'};
			$id_orders_string .= 'R' if $rec->{'ToReship'};
			$id_orders_string .= 'CF' if $rec->{'ToExchange'};

			######
			###### Deteccion Posibles Problemas con los productos de esta orden
			######
			my $queryw = "SELECT 
								SUM(IF(sl_warehouses_batches_orders.Status = 'Shipped',1,0)) AS Shipped,
								SUM(IF(sl_warehouses_batches_orders.Status = 'In Transit',1,0)) ASInTransit,
								SUM(IF(sl_warehouses_batches_orders.Status = 'In Fulfillment',1,0)) ASInFulfillment
								FROM `sl_orders_products` 
								INNER JOIN sl_warehouses_batches_orders 
								USING(ID_orders_products)
								WHERE ID_orders = '$rec->{'ID_orders'}'
								AND ID_warehouses_batches <> '$in{'id_warehouses_batches'}'
								AND sl_warehouses_batches_orders.Status IN ('Shipped','In Transit','In Fulfillment') 
								AND LEFT(sl_orders_products.ID_products,1) <> 6
								ORDER BY sl_orders_products.ID_orders_products, ID_warehouses_batches_orders;";
			my ($sthw) = &Do_SQL($queryw);
			my ($b_shipped, $b_intransit, $b_infulfillment) = $sthw->fetchrow();

			if($rec->{'Status'} !~ /Cancelled|Returned|Error/) {

				($b_shipped > 0 or $b_intransit > 0) and ($imgw = 'b_topending.gif');
				($b_infulfillment > 0) and ($imgw = 'b_warning.png');
				

				if($imgw ne '' ) {

					(&check_permissions('warehouses_batches_orders_reasign','','')) and $dynamic_order_reasign = qq|<a title="" href="javascript:return false;" onclick="to_reasign($rec->{'ID_orders'});" style="text-decoration:none"><img src="$va{'imgurl'}/$usr{'pref_style'}/bt_do.gif"</a>|;
					$dynamic_order_warning = qq|<a title="$b_infulfillment IF\n$b_intransit IT\n$b_shipped S" href="/cgi-bin/common/apps/ajaxbuild?tab=$in{'tab'}&ajaxbuild=overlay_warehouses_batches_products&ido=$rec->{'ID_orders'}&idwb=$in{'id_warehouses_batches'}" title="" rel="#overlay" style="text-decoration:none"><img src="$va{'imgurl'}/$usr{'pref_style'}/$imgw"</a>|;

				}

			}


			if(($rec->{'Status'} eq 'In Fulfillment' or $rec->{'Status'} eq 'Error') and $batch_status eq 'Assigned'){

				$dynamic_cancel = qq|<a href="/cgi-bin/mod/wms/dbman?cmd=$in{'cmd'}&view=$in{'id_warehouses_batches'}&drop=$rec->{'ID_orders'}">
							    		<img src="/sitimages/default/checkmark_off.gif" title="Click to cancel order" style="cursor:pointer;">
							    	</a>|;
			}
			$this_style = $rec->{'Status'} eq 'Cancelled' ? 'text-decoration:line-through;' : '';

			$va{'searchresults'} .=  qq|
			<tr bgcolor='$c[$d]' onmouseout="m_out(this)" onmouseover="m_over(this)" style="$this_style">\n
				<td valign="top" align="left" class="smalltext">\n
				$dynamic_cancel &nbsp;\n
				<a href="/cgi-bin/mod/$usr{'application'}/dbman?cmd=opr_orders&view=$rec->{'ID_orders'}">|. $id_orders_string .qq|</a>\n
				&nbsp;\n
				$dynamic_order_warning &nbsp;$dynamic_order_reasign &nbsp;\n
				</td>  \n
				<td valign="top" class="smalltext">$rec->{'Ptype'}</td>\n
				<td valign="top" class="smalltext">$rec->{'Date'}</td>\n
				<td valign="top" class="smalltext">$rec->{'shp_Zip'}</td>\n
				<td valign="top" class="smalltext">$rec->{'shp_City'}</td>\n
				<td valign="top" class="smalltext">$rec->{'shp_State'}</td>\n 
			</tr>\n|;

		} 
		 
	}else{
		$va{'pageslist'} = 1;
		$va{'searchresults'} .=  qq|
				<tr bgcolor='$c[$d]' onmouseout="m_out(this)" onmouseover="m_over(this)" style="">
			  <td align="center" colspan=6 class="smalltext">|.&trans_txt('search_nomatches').qq|</td>
			</tr>\n|;
	}

}


#############################################################################
#############################################################################
#   Function: load_tabs4
#
#       Es: carga el tab cuatro. Pagos a Remesas
#       En: 
#
#   Created on: 08/26/2013  14:21:10
#
#   Author: _RB_
#
#   Modifications:
#
#   Parameters:
#
#
#  Returns:
#
#      - searchresults : searchresults
#
#  See Also:
#
#  Todo:
#
sub load_tabs4 {
#############################################################################
#############################################################################
########################################

	$va{'chkperm'} = &check_permissions('warehouses_batches_payments','','') ? 'block' : 'none';


	my ($sth3) = &Do_SQL("SELECT SUM(SalePrice - Discount + Tax + Shipping + ShpTax)
						FROM sl_orders_products INNER JOIN
						(
							SELECT ID_orders FROM sl_orders_products INNER JOIN sl_warehouses_batches_orders 
							USING(ID_orders_products) WHERE ID_warehouses_batches = '$in{'id_warehouses_batches'}'
							GROUP BY ID_orders
						)tmp
						USING(ID_orders) 
						LEFT JOIN sl_warehouses_batches_orders 
							USING(ID_orders_products)
						WHERE sl_orders_products.Status='Active'
						AND IF( 
								LEFT(ID_products,1) = 6,1, 
								sl_warehouses_batches_orders.ID_orders_products = sl_orders_products.ID_orders_products 
								AND ID_warehouses_batches = '$in{'id_warehouses_batches'}'
						);");

	### Sale Prices
	my (@c) = split(/,/,$cfg{'srcolors'});
	my ($sth) = &Do_SQL("SELECT COUNT(*) FROM sl_warehouses_batches_payments WHERE ID_warehouses_batches = '$in{'id_warehouses_batches'}';");
	$va{'matches'} = $sth->fetchrow;

	if ($va{'matches'}>0){	

		my ($sth) = &Do_SQL("SELECT * FROM sl_warehouses_batches_payments WHERE ID_warehouses_batches = '$in{'id_warehouses_batches'}' ORDER BY ID_warehouses_batches_payments DESC;");
		while (my ($id, $id2, $id_banks, $amount, $refid, $notes, $st, $d, $t, $id_admin_users)= $sth->fetchrow() ){

			my $moddrop = ($st eq 'New' and $va{'chkperm'} eq 'block') ? 
							qq|<a href='/cgi-bin/mod/".$usr{'application'}."/dbman?cmd=".$in{'cmd'}."&view=".$in{'id_products'}."&tab=4&action=1&drop=".$idpp."'>
								<img src='$va{'imgurl'}/$usr{'pref_style'}/b_drop.png' title='Delete' alt='' border='0'>
								</a>| :
							'';

			$d = 1 - $d;
			$va{'searchresults'} .= "<tr bgcolor='$c[$d]'>\n";
			$va{'searchresults'} .= "  <td class='smalltext'>$moddrop</td>";
			$va{'searchresults'} .= "  <td class='smalltext'>$name</td>\n";
			$va{'searchresults'} .= "  <td class='smalltext'>$fp</td>\n";
			$va{'searchresults'} .= "  <td class='smalltext'>$ptype</td>\n";
			$va{'searchresults'} .= "  <td class='smalltext'>$authcode</td>\n";
			$va{'searchresults'} .= "  <td class='smalltext'align='right'>".&format_price($price)."</td>\n";
			$va{'searchresults'} .= "  <td class='smalltext'align='right'>".&format_price($dp)."</td>\n";
			$va{'searchresults'} .= "</tr>\n";
		
		}
	
	}else{
	
		$va{'searchresults'} = qq|
			<tr>
				<td colspan='6' align="center">|.&trans_txt('search_nomatches').qq|</td>
			</tr>\n|;
	
	}

}

1;