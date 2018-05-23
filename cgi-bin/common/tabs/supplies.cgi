#!/usr/bin/perl
####################################################################
########                  Supplies                   ########
####################################################################
sub load_tabsconf {
# --------------------------------------------------------
	if ($in{'tab'} eq 3){
		## Notes Tab
		$va{'tab_type'}  = 'notes';
		$va{'tab_title'} = &trans_txt('notes');
		$va{'tab_table'} = 'sl_supplies_notes';
	}elsif($in{'tab'} eq 4){
		## Notes Tab
		$va{'tab_type'}  = 'logs';
		$va{'tab_title'} = &trans_txt('logs');
		$va{'tab_table'} = 'sl_supplies';
	}
}

sub load_tabs1 {
# --------------------------------------------------------
##############################################
## tab1 :  Vendors
##############################################

	if ($in{'vdrop'}){
	
		## Revisar si el vendor no ha surtido suppplies

		my ($sth) = &Do_SQL("DELETE FROM sl_supplies_vendors WHERE ID_supplies='$in{'id_supplies'}' AND ID_supplies_vendors='$in{'vdrop'}'");
		&auth_logging('mer_supplies_delvend',$in{'id_supplies'});
		$va{'tabmessage'} = &trans_txt('mer_supplies_delvend');
		$in{'tabs'} = 1;
	}
	my (@c) = split(/,/,$cfg{'srcolors'});
	my ($sth) = &Do_SQL("SELECT COUNT(*) FROM sl_supplies_vendors WHERE id_supplies='$in{'id_supplies'}'");
	$va{'matches'} = $sth->fetchrow;
	if ($va{'matches'}>0){
		(!$in{'nh'}) and ($in{'nh'}=1);
		$first = ($in{'nh'} - 1) * $usr{'pref_maxh'};			
		($va{'pageslist'},$qs) = &pages_list($in{'nh'},"/cgi-bin/mod/$usr{'application'}/dbman",$va{'matches'},$usr{'pref_maxh'});
		my ($sth) = &Do_SQL("SELECT * FROM sl_supplies_vendors,sl_vendors WHERE ID_supplies='$in{'id_supplies'}' AND sl_supplies_vendors.ID_vendors=sl_vendors.ID_vendors ORDER BY ID_supplies_vendors DESC LIMIT $first,$usr{'pref_maxh'};");
		while ($rec = $sth->fetchrow_hashref){
			$d = 1 - $d;
			$rec->{'Notes'} =~ s/\n/<br>/g;
			$va{'searchresults'} .= "<tr bgcolor='$c[$d]'>\n";
			$va{'searchresults'} .= "   <td class='smalltext'>";
			$va{'searchresults'} .= qq| <a href="$script_url?cmd=mer_vendors&view=$rec->{'ID_vendors'}"><img src='$va{'imgurl'}/$usr{'pref_style'}/b_view.png' title='View' alt='' border='0'></a>|;
			$va{'searchresults'} .= qq| <a href="$script_url?cmd=$in{'cmd'}&view=$in{'id_supplies'}&tab=2&vdrop=$rec->{'ID_supplies_vendors'}"><img src='$va{'imgurl'}/$usr{'pref_style'}/b_drop.png' title='Drop' alt='' border='0'></a>|;
			$va{'searchresults'} .= "</td>\n";
			$va{'searchresults'} .= "   <td class='smalltext'>($rec->{'ID_vendors'}) $rec->{'CompanyName'}</td>\n";
			my ($sth2) = &Do_SQL("SELECT PODate FROM sl_purchaseorders_items,sl_purchaseorders WHERE sl_purchaseorders_items.ID_purchaseorders=sl_purchaseorders.ID_purchaseorders AND ID_products - 700000000 ='$in{'id_supplies'}' AND ID_vendors=$rec->{'ID_vendors'} ORDER BY PODate DESC;");
			$va{'searchresults'} .= "   <td class='smalltext'>".$sth2->fetchrow."</td>\n";
			my ($sth2) = &Do_SQL("SELECT SUM(Qty*Price) FROM sl_purchaseorders_items,sl_purchaseorders WHERE sl_purchaseorders_items.ID_purchaseorders=sl_purchaseorders.ID_purchaseorders AND ID_products - 700000000 ='$in{'id_supplies'}' AND ID_vendors=$rec->{'ID_vendors'} ORDER BY PODate DESC;");
			$va{'searchresults'} .= "   <td class='smalltext' align='right'>".&format_price($sth2->fetchrow)."</td>\n";
			$va{'searchresults'} .= "   <td class='smalltext'>$rec->{'Status'}</td>\n";
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
	#$va{'keyname'} = 'Vendors';
	#&load_db_fields_values($in{'db'},'ID_supplies',$in{'id_supplies'},'*');
}

sub load_tabs2 {	
# --------------------------------------------------------
##############################################
## tab8 : POs
##############################################
	
	my (@c) = split(/,/,$cfg{'srcolors'});
	my ($sth) = &Do_SQL("SELECT COUNT(*) FROM sl_purchaseorders_items 
			WHERE ID_products - 700000000 = '$in{'id_supplies'}';"); 
	$va{'matches'} = $sth->fetchrow;
	if ($va{'matches'}>0){
		if ($in{'print'}){
			$sth = &Do_SQL("SELECT * FROM sl_purchaseorders_items 
				      WHERE ID_products - 700000000 = '$in{'id_supplies'}'
				      ORDER BY ID_purchaseorders DESC;");
		}else{
			(!$in{'nh'}) and ($in{'nh'}=1);
			$first = ($in{'nh'} - 1) * $usr{'pref_maxh'};			
			($va{'pageslist'},$qs) = &pages_list($in{'nh'},"/cgi-bin/mod/$usr{'application'}/dbman",$va{'matches'},$usr{'pref_maxh'});
			$sth = &Do_SQL("SELECT * FROM sl_purchaseorders_items 
				      WHERE ID_products - 700000000 = '$in{'id_supplies'}'
				      ORDER BY ID_purchaseorders DESC LIMIT $first,$usr{'pref_maxh'};");			
		}

		while ($rec = $sth->fetchrow_hashref){
			$d = 1 - $d;
			$va{'searchresults'} .= "<tr bgcolor='$c[$d]'>\n";
			$va{'searchresults'} .= "   <td class='smalltext' valign='top'><a href='$script_url?cmd=mer_po&view=$rec->{'ID_purchaseorders'}'>$rec->{'ID_purchaseorders'}</a></td>\n";						
			$va{'searchresults'} .= "   <td class='smalltext'>$rec->{'Qty'}</td>\n";
			$va{'searchresults'} .= "   <td class='smalltext'>$rec->{'Received'}</td>\n";
			$va{'searchresults'} .= "   <td class='smalltext'>$rec->{'Price'}</td>\n";
			$va{'searchresults'} .= "   <td class='smalltext'>$rec->{'Date'}</td>\n";
			$va{'searchresults'} .= "</tr>\n";
		}
	}else{
		$va{'pageslist'} = 1;
		$va{'searchresults'} = qq|
			<tr>
				<td colspan='6' align='center'>|.&trans_txt('search_nomatches').qq|</td>
			</tr>\n|;
	}
	#$va{'keyname'} = 'POs';
	#&load_db_fields_values($in{'db'},'ID_supplies',$in{'id_supplies'},'*');
}

1;