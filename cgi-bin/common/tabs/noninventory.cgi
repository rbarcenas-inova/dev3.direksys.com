#!/usr/bin/perl
#####################################################################
########                   Anoninventory	        		           		#########
#####################################################################
sub load_tabsconf {
# --------------------------------------------------------
	if ($in{'tab'} eq 1){
		## Notes Tab
		$va{'tab_type'}  = 'notes';
		$va{'tab_title'} = &trans_txt('notes');
		$va{'tab_table'} = 'sl_noninventory_notes';
	}elsif($in{'tab'} eq 5){
		## Notes Tab
		$va{'tab_type'}  = 'logs';
		$va{'tab_title'} = &trans_txt('logs');
		$va{'tab_table'} = 'sl_noninventory';
	}
}
 



sub load_tabs2 {
# --------------------------------------------------------
##############################################
## tab2 : VENDORS
##############################################

	## DROP
	if ($in{'vdrop'}){
		my ($sth) = &Do_SQL("DELETE FROM sl_noninventory_vendors WHERE ID_noninventory='$in{'id_noninventory'}' AND ID_noninventory_vendors='$in{'vdrop'}'");
		&auth_logging('mer_noninventory_delvend',$in{'id_noninventory'});
		$va{'tabmessage'} = &trans_txt('mer_noninventory_delvend');
	## ADD
	}elsif ($in{'addvendor'}){
		my ($sth) = &Do_SQL("INSERT INTO sl_noninventory_vendors SET ID_noninventory='$in{'id_noninventory'}', ID_vendors='$in{'addvendor'}',Date=Curdate(),Time=NOW(),ID_admin_users='$usr{'id_admin_users'}'");
		$va{'tabmessage'} = &trans_txt('mer_noninventory_addvend');
		&auth_logging('mer_noninventory_addvend',$in{'id_noninventory'});
	}
	
	## VENDOR LIST
	my (@c) = split(/,/,$cfg{'srcolors'});
	my ($sth) = &Do_SQL("SELECT COUNT(*) FROM sl_noninventory_vendors WHERE id_noninventory='$in{'id_noninventory'}'");
	$va{'matches'} = $sth->fetchrow;
	if ($va{'matches'}>0){
		(!$in{'nh'}) and ($in{'nh'}=1);
		$first = ($in{'nh'} - 1) * $usr{'pref_maxh'};			
		($va{'pageslist'},$qs) = &pages_list($in{'nh'},"/cgi-bin/mod/$usr{'application'}/dbman",$va{'matches'},$usr{'pref_maxh'});
		my ($sth) = &Do_SQL("SELECT * FROM sl_noninventory_vendors,sl_vendors WHERE ID_noninventory='$in{'id_noninventory'}' AND sl_noninventory_vendors.ID_vendors=sl_vendors.ID_vendors ORDER BY ID_noninventory_vendors DESC LIMIT $first,$usr{'pref_maxh'};");
		while ($rec = $sth->fetchrow_hashref){
			$d = 1 - $d;
			$rec->{'Notes'} =~ s/\n/<br>/g;
			$va{'searchresults'} .= "<tr bgcolor='$c[$d]'>\n";
			$va{'searchresults'} .= "   <td class='smalltext'>";
			$va{'searchresults'} .= qq| <a href="$script_url?cmd=mer_noninventory&view=$in{'id_noninventory'}&tab=2&vdrop=$rec->{'ID_noninventory_vendors'}"><img src='$va{'imgurl'}/$usr{'pref_style'}/b_drop.png' title='Drop' alt='' border='0'></a>|;
			$va{'searchresults'} .= "</td>\n";
			$va{'searchresults'} .= "   <td class='smalltext'>($rec->{'ID_vendors'}) $rec->{'CompanyName'}</td>\n";
			my ($sth2) = &Do_SQL("SELECT PODate FROM sl_purchaseorders_items,sl_purchaseorders WHERE sl_purchaseorders_items.ID_purchaseorders=sl_purchaseorders.ID_purchaseorders AND RIGHT(ID_products,4)='$in{'id_noninventory'}' AND ID_vendors=$rec->{'ID_vendors'} ORDER BY PODate DESC;");
			$va{'searchresults'} .= "   <td class='smalltext'>".$sth2->fetchrow."</td>\n";
			my ($sth2) = &Do_SQL("SELECT SUM(Qty*Price) FROM sl_purchaseorders_items,sl_purchaseorders WHERE sl_purchaseorders_items.ID_purchaseorders=sl_purchaseorders.ID_purchaseorders AND RIGHT(ID_products,4)='$in{'id_noninventory'}' AND ID_vendors=$rec->{'ID_vendors'} ORDER BY PODate DESC;");
			$va{'searchresults'} .= "   <td class='smalltext' align='right'>".&format_price($sth2->fetchrow)."</td>\n";
			$va{'searchresults'} .= "   <td class='smalltext' align='right'>$rec->{'Status'}</td>\n";
			$va{'searchresults'} .= "</tr>\n";
		}
	}else{
		$va{'pageslist'} = 1;
		$va{'matches'} = 0;
		$va{'searchresults'} = qq|
			<tr>
				<td colspan='5' align="center">|.&trans_txt('search_nomatches').qq|</td>
			</tr>\n|;
	}

}


sub load_tabs3 {
# --------------------------------------------------------
##############################################
## tab3 : POs
##############################################
	$va{'tab_headers'} = qq|
					<tr>
						<td class="menu_bar_title">PO ID</td>
						<td class="menu_bar_title">Date</td>
						<td class="menu_bar_title">Vendor</td>
						<td class="menu_bar_title">Qty</td>
						<td class="menu_bar_title">Received</td>
						<td class="menu_bar_title">Price</td>
					</tr>\n|;
	my (@c) = split(/,/,$cfg{'srcolors'});
	my ($sth) = &Do_SQL("SELECT COUNT(*) FROM sl_purchaseorders_items WHERE ID_products='".(500000000+$in{'id_noninventory'})."' $query");
	$va{'matches'} = $sth->fetchrow;
	if ($va{'matches'}>0){
		(!$in{'nh'}) and ($in{'nh'}=1);
		$first = ($in{'nh'} - 1) * $usr{'pref_maxh'};			
		($va{'pageslist'},$qs) = &pages_list($in{'nh'},"/cgi-bin/mod/$usr{'application'}/dbman",$va{'matches'},$usr{'pref_maxh'});
		my ($sth) = &Do_SQL("SELECT * FROM sl_purchaseorders_items WHERE ID_products='".(500000000+$in{'id_noninventory'})."'  $query LIMIT $first,$usr{'pref_maxh'};");
		while ($rec = $sth->fetchrow_hashref){
			$d = 1 - $d;
			$rec->{'ID_vendors'} = &load_name('sl_purchaseorders','ID_purchaseorders',$rec->{'ID_purchaseorders'},'ID_vendors');
			$va{'searchresults'} .= "<tr bgcolor='$c[$d]'>\n";
			$va{'searchresults'} .= "  <td class='smalltext'><a href='$script_url?cmd=mer_po&view=$rec->{'ID_purchaseorders'}'>$rec->{'ID_purchaseorders'}</a></td>\n";
			$va{'searchresults'} .= "  <td class='smalltext'>$rec->{'Date'}</td>\n";
			$va{'searchresults'} .= "  <td class='smalltext'><a href='$script_url?cmd=mer_vendors&view=$rec->{'ID_vendors'}'>".&load_db_names('sl_vendors','ID_vendors',$rec->{'ID_vendors'},"([ID_vendors]) [CompanyName]")."</a></td>\n";
			$va{'searchresults'} .= "  <td class='smalltext' align='right'>".&format_number($rec->{'Qty'})."</td>\n";
			$va{'searchresults'} .= "  <td class='smalltext' align='right'>".&format_number($rec->{'Received'})."</td>\n";
			$va{'searchresults'} .= "  <td class='smalltext' align='right'>".&format_price($rec->{'Price'})."</td>\n";
			$va{'searchresults'} .= "</tr>\n";
		}	
	}else{
		$va{'pageslist'} = 1;
		$va{'matches'} = 0;
		$va{'searchresults'} = qq|
			<tr>
				<td colspan='6' align="center">|.&trans_txt('search_nomatches').qq|</td>
			</tr>\n|;
	}
}


sub load_tabs4 {
# --------------------------------------------------------
##############################################
## tab4 : Accounting
##############################################
	my ($sth) = &Do_SQL("SELECT * FROM sl_noninventory WHERE id_noninventory='$in{'id_noninventory'}'");
	my ($rec) = $sth->fetchrow_hashref;
	$in{'purchaseid_accounts'} =  $rec->{'PurchaseID_accounts'};
	$in{'assetid_accounts'} =  $rec->{'AssetID_accounts'};
	$in{'tax'} =  $rec->{'Tax'};
	$va{'paccount_name'} = &load_name('sl_accounts','ID_accounts',$in{'purchaseid_accounts'},'Name');
	$va{'aaccount_name'} = &load_name('sl_accounts','ID_accounts',$in{'assetid_accounts'},'Name');
	
}

1;