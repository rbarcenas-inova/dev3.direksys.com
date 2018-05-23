#!/usr/bin/perl
#####################################################################
########                   APARTS	        		           		#########
#####################################################################
sub load_tabsconf {
# --------------------------------------------------------
	if ($in{'tab'} eq 3){
		## Notes Tab
		$va{'tab_type'}  = 'notes';
		$va{'tab_title'} = &trans_txt('notes');
		$va{'tab_table'} = 'sl_arman_notes';
	}elsif($in{'tab'} eq 4){
		## Notes Tab
		$va{'tab_type'}  = 'logs';
		$va{'tab_title'} = &trans_txt('logs');
		$va{'tab_table'} = 'sl_arman';
	}
}

sub load_tabs1 {
# --------------------------------------------------------
##############################################
## tab1 : Orders
##############################################
	$in{'status'} = &load_name('sl_arman','ID_arman',$in{'id_arman'},'Status');
	my (@c) = split(/,/,$cfg{'srcolors'});
	my ($sth) = &Do_SQL("SELECT COUNT(*) FROM sl_arman_payments WHERE ID_arman='$in{'id_arman'}'");
	$va{'matches'} = $sth->fetchrow;
	if ($va{'matches'}>0){
		if ($in{'print'}){
			$sth = &Do_SQL("SELECT * FROM sl_arman_payments WHERE ID_arman='$in{'id_arman'}';");
		}else{
			(!$in{'nh'}) and ($in{'nh'}=1);
			$first = ($in{'nh'} - 1) * $usr{'pref_maxh'};
			($va{'pageslist'},$qs) = &pages_list($in{'nh'},"/cgi-bin/mod/$usr{'application'}/dbman",$va{'matches'},$usr{'pref_maxh'});
			$sth = &Do_SQL("SELECT * FROM sl_arman_payments WHERE ID_arman='$in{'id_arman'}' LIMIT $first,$usr{'pref_maxh'};");
		}
		while ($rec = $sth->fetchrow_hashref){
			$d = 1 - $d;
			$va{'searchresults'} .= "<tr bgcolor='$c[$d]'>\n";
			if ($in{'status'} eq 'New'){
				$va{'searchresults'} .= qq| <td class='smalltext'><a href="/cgi-bin/mod/$usr{'application'}/dbman?cmd=$in{'cmd'}&view=$in{'id_arman'}&tab=1&drop=$rec->{'ID_arman_payments'}"><img src='$va{'imgurl'}/$usr{'pref_style'}/b_drop.png' title='Drop' alt='' border='0'></a></td>\n|;
			}else{
				$va{'searchresults'} .= "  <td class='smalltext'>&nbsp;</td>\n";
			}
			$va{'searchresults'} .= "  <td class='smalltext'><a href='/cgi-bin/mod/$usr{'application'}/dbman?cmd=opr_orders&view=$rec->{'ID_orders'}'>$rec->{'ID_orders'}</a></td>\n";
			$va{'searchresults'} .= "  <td class='smalltext'>$rec->{'DueSince'}</td>\n";
			$va{'searchresults'} .= "  <td class='smalltext'>$rec->{'Qty'}</td>\n";
			$va{'searchresults'} .= "  <td class='smalltext'>".&format_price($rec->{'OrigAmount'})."</td>\n";
			$va{'searchresults'} .= "  <td class='smalltext'>".&format_price($rec->{'PaidAmount'})."</td>\n";
			$va{'searchresults'} .= "  <td class='smalltext'>$rec->{'Status'}</td>\n";
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
## tab2 : Upload
##############################################


}

 1;