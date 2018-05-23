####################################################################
########                WAREHOUSE RECEIPT                ########
####################################################################

sub load_tabsconf {
# --------------------------------------------------------
	if ($in{'tab'} eq 2){
		## Notes Tab
		$va{'tab_type'}  = 'notes';
		$va{'tab_title'} = &trans_txt('notes');
		$va{'tab_table'} = 'sl_skustransfers_notes';
	}elsif($in{'tab'} eq 3){
		## Notes Tab
		$va{'tab_type'}  = 'logs';
		$va{'tab_title'} = &trans_txt('logs');
		$va{'tab_table'} = 'sl_skustransfers';
	}
}

sub load_tabs1 {
# --------------------------------------------------------
# Last Modified on: 06/08/09 16:25:23
# Last Modified by: MCC C. Gabriel Varela S: Se hace que no se permitan sets.
##############################################
## tab1 : ITEMS
##############################################

	$in{'id_from_sku'} = $in{'id_from_sku'};
		## Items List
		my ($err,$item);
		if ($in{'add_item'} and $in{'status'} ne 'Completed'){
		
		  if($in{'id_warehouses'}){
		    $query = " AND ID_warehouses = '$in{'id_warehouses'}' ";
		  }
		
			#$in{'qty'} = int($in{'qty'});
			if (!$in{'id_fromsku'} or !$in{'id_tosku'}){
				$error{'id_sku'} = &trans_txt('required');
				++$err;
			}else{
				$in{'id_fromsku'}	=~	s/-//g;
				$in{'id_tosku'}	=~	s/-//g;
				
				$in{'id_fromsku'} = int($in{'id_fromsku'});
				$in{'id_tosku'} = int($in{'id_tosku'});
				($in{'id_fromsku'} < 400000000) and ($in{'id_fromsku'} += 400000000);	
				($in{'id_tosku'} < 400000000) and ($in{'id_tosku'} += 400000000);
				
#				my ($sth) = &Do_SQL("SELECT COUNT(*) FROM sl_skus WHERE ID_sku_products = '$in{'id_fromsku'}'");
				my ($sth) = &Do_SQL("SELECT COUNT(*),sum(if(Isset='Y',1,0)) as SumY
									FROM sl_skus 
									WHERE ID_sku_products = '$in{'id_fromsku'}'");
				($count,$sumy)=$sth->fetchrow_array();
				if($count == 0){
					#&cgierr("no from");
					$error{'id_fromsku'} = &trans_txt('invalid');
					++$err;
				}
				if($sumy > 0){
					#&cgierr("no from");
					$error{'id_fromsku'} = "The ID is a set.";
					++$err;
				}
				
#				my ($sth) = &Do_SQL("SELECT COUNT(*) FROM sl_skus WHERE ID_sku_products = '$in{'id_tosku'}'");
				my ($sth) = &Do_SQL("SELECT COUNT(*),sum(if(Isset='Y',1,0)) as SumY
									FROM sl_skus 
									WHERE ID_sku_products = '$in{'id_tosku'}'");
				($count,$sumy)=$sth->fetchrow_array();
				if($count == 0){
					#&cgierr("no to");
					$error{'id_tosku'} = &trans_txt('invalid');
					++$err;
				}
				if($sumy> 0){
					#&cgierr("no to");
					$error{'id_tosku'} = "The ID is a set.";
					++$err;
				}
				
				($sth) = &Do_SQL("SELECT COUNT(*) FROM sl_warehouses_location WHERE ID_products = '$in{id_fromsku}' $query ;");
				$total = $sth->fetchrow;
				if ($total <= 0){
					#&cgierr("no inventory");
					$error{'id_fromsku'} .= &trans_txt('invalid');
					++$err;
				}
			}

			if ($err>0){
				$va{'autorun_js'} = "add_item();";
				$va{'message'} = &trans_txt('reqfields') ."$error{'id_sku'}<br>$error{'id_fromsku'}<br>$error{'id_tosku'}";
			}else{
				$va{'message'} = &trans_txt('skustransfers_itemadded');
				my ($sth) = &Do_SQL("INSERT INTO sl_skustransfers_items SET id_skustransfers='$in{'id_skustransfers'}',FromSku='$in{'id_fromsku'}',ToSku='$in{'id_tosku'}',Date=CURDATE(),Time=CURTIME(),ID_admin_users='$usr{'id_admin_users'}'");
				&auth_logging('opr_skuitemtransfers_added',$in{'id_skustransfers'});
				$va{'tabmessages'} = &trans_txt('opr_itemtransfers_added');
				$in{'tabs'} = 1;
			}
		}elsif($in{'drop'}){
			my ($sth) = &Do_SQL("DELETE FROM sl_skustransfers_items WHERE ID_skustransfers_items='$in{'drop'}'");
			&auth_logging('opr_itemskutransfers_deleted',$in{'id_skustransfers'});
			$va{'tabmessages'} = &trans_txt('opr_itemskutransfers_deleted');
			$in{'tabs'} = 1;
		}
		## ITEMS
		my ($choices_on,$tot_qty,$vendor_sku);
		my (@c) = split(/,/,$cfg{'srcolors'});
		my ($sth) = &Do_SQL("SELECT COUNT(*) FROM sl_skustransfers_items WHERE ID_skustransfers='$in{'id_skustransfers'}'");
		$va{'matches'} = $sth->fetchrow;
		if ($va{'matches'}>0){
			my ($sth) = &Do_SQL("SELECT * FROM sl_skustransfers_items WHERE ID_skustransfers='$in{'id_skustransfers'}' ORDER BY ID_skustransfers_items DESC;");
			while ($rec = $sth->fetchrow_hashref){
				
				my $fwhname = &load_name('sl_warehouses', 'ID_warehouses', $rec->{'From_Warehouse'}, 'Name');
				my $twhname = &load_name('sl_warehouses', 'ID_warehouses', $rec->{'To_Warehouse'}, 'Name');
				
				if(substr($rec->{'FromSku'},0,1)ne'4'){
					$rec->{'FromModel'}	= &load_name('sl_products','ID_products',substr($rec->{'FromSku'},3),'Model');
					$rec->{'FromName'}	= &load_name('sl_products','ID_products',substr($rec->{'FromSku'},3),'Name');
					$linkprodfrom = 'mer_products';
				}else{
					$rec->{'FromModel'} = &load_name('sl_parts','ID_parts',substr($rec->{'FromSku'},5),'Model');
					$rec->{'FromName'} = &load_name('sl_parts','ID_parts',substr($rec->{'FromSku'},5),'Name');
					$linkprodfrom = 'mer_parts';
				}
				
				if(substr($rec->{'ToSku'},0,1)ne'4'){
					$rec->{'ToModel'}	= &load_name('sl_products','ID_products',substr($rec->{'ToSku'},3),'Model');
					$rec->{'ToName'}	= &load_name('sl_products','ID_products',substr($rec->{'ToSku'},3),'Name');
					$linkprodto = 'mer_products';
				}else{
					$rec->{'ToModel'} = &load_name('sl_parts','ID_parts',substr($rec->{'ToSku'},5),'Model');
					$rec->{'ToName'} = &load_name('sl_parts','ID_parts',substr($rec->{'ToSku'},5),'Name');
					$linkprodto = 'mer_parts';
				}
				
				$in{'status'} = &load_name('sl_skustransfers','ID_skustransfers',$in{'id_skustransfers'},'Status');
				$d = 1 - $d;
				$va{'searchresults'} .= "<tr bgcolor='$c[$d]'>\n";
				
				$va{'searchresults'} .= "   <td class='smalltext' valign='top'>";
				$va{'searchresults'} .= qq|<a href="/cgi-bin/mod/[ur_application]/dbman?cmd=opr_warehouses&view=$rec->{'From_Warehouse'}" title="View $rec->{'From_Warehouse'}">($rec->{'From_Warehouse'})</a> $fwhname / <a href="/cgi-bin/mod/[ur_application]/dbman?cmd=opr_locations&search=Search&id_warehouses=$rec->{'From_Warehouse'}&code=$rec->{'From_Warehouse_Location'}" title="View $rec->{'From_Warehouse'}">$rec->{'From_Warehouse_Location'}</a>|;
				$va{'searchresults'} .= "   </td>\n";
				
				$va{'searchresults'} .= "   <td class='smalltext' valign='top'>";
				$va{'searchresults'} .= qq| <a href="$script_url?cmd=opr_skustransfers&view=$rec->{'ID_skustransfers'}&tab=1&drop=$rec->{'ID_skustransfers_items'}"><img src='$va{'imgurl'}/$usr{'pref_style'}/b_drop.png' title='Drop' alt='' border='0'></a>| if $in{'status'} ne 'Completed';
				$va{'searchresults'} .= "   </td>\n";
				$va{'searchresults'} .= qq|  <td class='smalltext' valign='top'><a href="$script_url?cmd=$linkprodto&view=|.substr($rec->{'FromSku'},3).qq|">|.&format_sltvid($rec->{'FromSku'}).qq|</a></td>|;
				$va{'searchresults'} .= qq| <td  class='smalltext' valign='top'>$rec->{'FromModel'}<br>$rec->{'FromName'}|;
				
				$va{'searchresults'} .= "   <td class='smalltext' valign='top'>";
				$va{'searchresults'} .= qq|<a href="/cgi-bin/mod/[ur_application]/dbman?cmd=opr_warehouses&view=$rec->{'To_Warehouse'}" title="View $rec->{'To_Warehouse'}">($rec->{'To_Warehouse'})</a> $twhname / <a href="/cgi-bin/mod/[ur_application]/dbman?cmd=opr_locations&search=Search&id_warehouses=$rec->{'To_Warehouse'}&code=$rec->{'To_Warehouse_Location'}" title="View $rec->{'To_Warehouse'}">$rec->{'To_Warehouse_Location'}</a>|;
				$va{'searchresults'} .= "   </td>\n";
				
				$va{'searchresults'} .= "   <td class='smalltext' valign='top'>&nbsp;</td>";
				$va{'searchresults'} .= qq| <td class='smalltext' valign='top'><a href="$script_url?cmd=$linkprodto&view=|.substr($rec->{'ToSku'},3).qq|">|.&format_sltvid($rec->{'ToSku'}).qq|</a></td>|;
				$va{'searchresults'} .= qq| <td class='smalltext' valign='top'>$rec->{'ToModel'}<br>$rec->{'ToName'}|;
				
				$va{'searchresults'} .= "   <td class='smalltext' valign='top' align='right'>";
				$va{'searchresults'} .= qq|$rec->{'Qty'}|;
				$va{'searchresults'} .= "   </td>\n";
				
				$va{'searchresults'} .= "</tr>\n";
			}
		}else{
			$va{'pageslist'} = 1;
			$va{'searchresults'} = qq|
				<tr>
					<td colspan='7' align="center">|.&trans_txt('search_nomatches').qq|</td>
				</tr>\n|;
		}
		## Tables Header/Titles
		$va{'keyname'} = 'Items';
		&load_db_fields_values($in{'db'},'ID_skustransfers',$in{'id_skustransfers'},'*');
}

1;
