#####################################################################
########                  REPLACEMENT MEMOS                 #########
#####################################################################

sub load_tabsconf {	
	# --------------------------------------------------------
	if ($in{'tab'} eq 1){
		$in{'db'} = "sl_returns";
		## Notes Tab
		$va{'tab_type'}  = 'notes';
		$va{'tab_title'} = &trans_txt('notes');
		$va{'tab_table'} = 'sl_returns_notes';
	}elsif($in{'tab'} eq 3){
		$in{'db'} = "sl_returns";
		## Notes Tab
		$va{'tab_type'}  = 'logs';
		$va{'tab_title'} = &trans_txt('logs');
		$va{'tab_table'} = 'sl_returns';
	}
}
 
sub load_tabs2 {
# --------------------------------------------------------
##############################################
## tab2 : Parts
##############################################

	## ITEMS LIST
	my (@c) = split(/,/,$cfg{'srcolors'});
	my ($name,$stlink);
	my ($sth) = &Do_SQL("SELECT COUNT(*) FROM sl_returns_upcs WHERE id_returns='$in{'id_returns'}'");
	$va{'matches'} = $sth->fetchrow;
	if ($va{'matches'}>0){
		if ($in{'print'}){
			$sth = &Do_SQL("SELECT * FROM sl_returns_upcs WHERE id_returns='$in{'id_returns'}' ORDER BY ID_returns_upcs");
		}else{
			(!$in{'nh'}) and ($in{'nh'}=1);
			$first = ($in{'nh'} - 1) * $usr{'pref_maxh'};			
			($va{'pageslist'},$qs) = &pages_list($in{'nh'},"/cgi-bin/mod/$usr{'application'}/dbman",$va{'matches'},$usr{'pref_maxh'});
			$sth = &Do_SQL("SELECT * FROM sl_returns_upcs WHERE id_returns='$in{'id_returns'}' ORDER BY ID_returns_upcs LIMIT $first,$usr{'pref_maxh'};");			
		}
	
	  my $status = &load_name('sl_returns','ID_returns',$in{'id_returns'},'Status');
	
		while ($rec = $sth->fetchrow_hashref){
			$d = 1 - $d;
			$rec->{'ID_products'}=&load_name('sl_skus','UPC',$rec->{'UPC'},'ID_sku_products');
			my ($sth2) = &Do_SQL("SELECT SUM(Quantity) FROM sl_returns INNER JOIN sl_orders_products ON sl_returns.ID_orders = sl_orders_products.ID_orders WHERE ID_returns='$rec->{'ID_returns'}' AND Related_ID_products='$rec->{'ID_products'}' GROUP BY Related_ID_products;");
			$rec->{'QtySent'} =$sth2->fetchrow();
			## Name Model
		  $name = &load_db_names('sl_parts','ID_parts',($rec->{'ID_products'}-400000000),'[Model]<br>[Name]');

			$va{'searchresults'} .= "<tr bgcolor='$c[$d]'>\n";
			$va{'searchresults'} .= "   <td class='smalltext' valign='top'>";
			$va{'searchresults'} .= qq| <a href="$script_url?cmd=$in{'cmd'}&view=$in{'id_returns'}&tab=2&drop_item=$rec->{'ID_returns_upcs'}"><img src='$va{'imgurl'}/$usr{'pref_style'}/b_drop.png' title='Drop' alt='' border='0'></a>| if $status eq 'In Process';
			$va{'searchresults'} .= "  <td class='smalltext' valign='top'>".&format_sltvid($rec->{'ID_products'})."</td>\n";
			$va{'searchresults'} .= "  <td class='smalltext'>$name</td>\n";
			$va{'searchresults'} .= "  <td class='smalltext' valign='top' align='left'>$rec->{'QtySent'}</td>\n";
			$va{'searchresults'} .= "  <td class='smalltext' valign='top' align='left'>$rec->{'Quantity'}</td>\n";
			$va{'searchresults'} .= "  <td class='smalltext' valign='top' align='left'><a href=\"/cgi-bin/mod/admin/admin?cmd=warehouses&id_warehouses=$rec->{'ID_warehouses'}\">".&load_name('sl_warehouses','ID_warehouses',$rec->{'ID_warehouses'},'Name')." ($rec->{'ID_warehouses'})</a></td>\n";
			$va{'searchresults'} .= "</tr>\n";
		}	
	}else{
		$va{'pageslist'} = 1;
		$va{'searchresults'} = qq|
			<tr>

				<td colspan='5' align="center">|.&trans_txt('search_nomatches').qq|</td>
			</tr>\n|;
	}
	## Tables Header/Titles
	#$va{'keyname'} = 'Items';
	#&load_db_fields_values($in{'db'},'ID_returns',$in{'id_returns'},'*');
}

1;
