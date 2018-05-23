#####################################################################
########                   DEVELOPER JOBS                    ########
#####################################################################

sub load_tabsconf {
# --------------------------------------------------------

	if($in{'tab'} eq 3){
		## Notes Tab
		$va{'tab_type'}  = 'logs';
		$va{'tab_title'} = &trans_txt('logs');
		$va{'tab_table'} = 'sl_categories';
	}
	
}

sub load_tabs1{
# --------------------------------------------------------
##############################################
## tab1 : Categories
##############################################
		my (@c) = split(/,/,$cfg{'srcolors'});
		my ($sth) = &Do_SQL("SELECT COUNT(*) FROM sl_products,sl_products_categories WHERE ID_categories='$in{'id_categories'}' AND sl_products.ID_products=sl_products_categories.ID_products  AND sl_products.Status<>'Inactive'");
		$va{'matches'} = $sth->fetchrow;
		if ($va{'matches'}>0){
			(!$in{'nh'}) and ($in{'nh'}=1);
			$first = ($in{'nh'} - 1) * $usr{'pref_maxh'};			
			($va{'pageslist'},$qs) = &pages_list($in{'nh'},"/cgi-bin/mod/$usr{'application'}/dbman",$va{'matches'},$usr{'pref_maxh'});
			my ($sth) = &Do_SQL("SELECT * FROM sl_products,sl_products_categories WHERE ID_categories='$in{'id_categories'}' AND sl_products.ID_products=sl_products_categories.ID_products AND sl_products.Status<>'Inactive' ORDER BY sl_products.Name DESC LIMIT $first,$usr{'pref_maxh'};");
			while ($rec = $sth->fetchrow_hashref){
				$d = 1 - $d;
				$va{'searchresults'} .= "<tr bgcolor='$c[$d]' onmouseover='m_over(this)' onmouseout='m_out(this)' onClick=\"trjump('$script_url?cmd=mer_products&view=$rec->{'ID_products'}')\">\n";
				$va{'searchresults'} .= "   <td class='smalltext'>".&format_sltvid($rec->{'ID_products'})."</td>\n";
				$va{'searchresults'} .= "   <td class='smalltext'>$rec->{'Model'}</td>\n";
				$va{'searchresults'} .= "   <td class='smalltext'>$rec->{'Name'}</td>\n";
				$va{'searchresults'} .= "   <td class='smalltext' align='right'>".&format_price($rec->{'SPrice'})."</td>\n";
				$va{'searchresults'} .= "</tr>\n";
			}
		}else{
			$va{'pageslist'} = 1;
			$va{'searchresults'} = qq|
				<tr>
					<td colspan='6' align='center'>|.&trans_txt('search_nomatches').qq|</td>
				</tr>\n|;
		}
}

sub load_tabs2 {
# --------------------------------------------------------
##############################################
## tab2 : VENDORS
##############################################

	### TODO Permisos
	## DROP
	if ($in{'vdrop'}){
		my ($sth) = &Do_SQL("DELETE FROM sl_vendors_categories WHERE ID_categories='$in{'id_categories'}' AND ID_vendors_categories='$in{'vdrop'}'");
		&auth_logging('mer_parts_delvend',$in{'id_categories'});
		$va{'tabmessage'} = &trans_txt('mer_parts_delvend');
	## ADD
	}elsif ($in{'addvendor'}){
		my ($sth) = &Do_SQL("INSERT INTO sl_vendors_categories SET ID_categories='$in{'id_categories'}', ID_vendors='$in{'addvendor'}',Date=Curdate(),Time=NOW(),ID_admin_users='$usr{'id_admin_users'}'");
		$va{'tabmessage'} = &trans_txt('mer_parts_addvend');
		&auth_logging('mer_parts_addvend',$in{'id_categories'});
	}
	
	## VENDOR LIST
	my (@c) = split(/,/,$cfg{'srcolors'});
	my ($sth) = &Do_SQL("SELECT COUNT(*) FROM sl_vendors_categories WHERE ID_categories='$in{'id_categories'}'");
	$va{'matches'} = $sth->fetchrow;
	if ($va{'matches'}>0){
		(!$in{'nh'}) and ($in{'nh'}=1);
		$first = ($in{'nh'} - 1) * $usr{'pref_maxh'};			
		($va{'pageslist'},$qs) = &pages_list($in{'nh'},"/cgi-bin/mod/$usr{'application'}/dbman",$va{'matches'},$usr{'pref_maxh'});
		my ($sth) = &Do_SQL("SELECT * FROM sl_vendors_categories,sl_vendors WHERE ID_categories='$in{'id_categories'}' AND sl_vendors_categories.ID_vendors=sl_vendors.ID_vendors ORDER BY ID_vendors_categories DESC LIMIT $first,$usr{'pref_maxh'};");
		while ($rec = $sth->fetchrow_hashref){
			$d = 1 - $d;
			$rec->{'Notes'} =~ s/\n/<br>/g;
			$va{'searchresults'} .= "<tr bgcolor='$c[$d]'>\n";
			$va{'searchresults'} .= "   <td class='smalltext'>";
			$va{'searchresults'} .= qq| <a href="$script_url?cmd=mer_categories&view=$in{'id_categories'}&tab=2&vdrop=$rec->{'ID_vendors_categories'}"><img src='$va{'imgurl'}/$usr{'pref_style'}/b_drop.png' title='Drop' alt='' border='0'></a>|;
			$va{'searchresults'} .= "</td>\n";
			$va{'searchresults'} .= "   <td class='smalltext'>($rec->{'ID_vendors'}) $rec->{'CompanyName'}</td>\n";
			my ($sth2) = &Do_SQL("SELECT PODate FROM sl_purchaseorders_items,sl_purchaseorders WHERE sl_purchaseorders_items.ID_purchaseorders=sl_purchaseorders.ID_purchaseorders AND RIGHT(ID_products,4)='$in{'id_categories'}' AND ID_vendors=$rec->{'ID_vendors'} ORDER BY PODate DESC;");
			$va{'searchresults'} .= "   <td class='smalltext'>".$sth2->fetchrow."</td>\n";
			my ($sth2) = &Do_SQL("SELECT SUM(Qty*Price) FROM sl_purchaseorders_items,sl_purchaseorders WHERE sl_purchaseorders_items.ID_purchaseorders=sl_purchaseorders.ID_purchaseorders AND RIGHT(ID_products,4)='$in{'id_categories'}' AND ID_vendors=$rec->{'ID_vendors'} ORDER BY PODate DESC;");
			$va{'searchresults'} .= "   <td class='smalltext' align='right'>".&format_price($sth2->fetchrow)."</td>\n";
			$va{'searchresults'} .= "   <td class='smalltext' align='right'>$rec->{'Status'}</td>\n";
			$va{'searchresults'} .= "</tr>\n";
		}
	}else{
		$va{'pageslist'} = 1;
		$va{'searchresults'} = qq|
			<tr>
				<td colspan='5' align="center">|.&trans_txt('search_nomatches').qq|</td>
			</tr>\n|;
	}

}
1;