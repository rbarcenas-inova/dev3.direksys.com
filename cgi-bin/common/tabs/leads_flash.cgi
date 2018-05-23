#!/usr/bin/perl
####################################################################
########                  Flash Leads                   ########
####################################################################

sub load_tabsconf {
# --------------------------------------------------------
	if ($in{'tab'} eq 2){
		## Notes Tab
		$va{'tab_type'}  = 'notes';
		$va{'tab_title'} = &trans_txt('notes');
		$va{'tab_table'} = 'sl_leads_flash_notes';
	}elsif($in{'tab'} eq 3){
		## Notes Tab
		$va{'tab_type'}  = 'logs';
		$va{'tab_title'} = &trans_txt('logs');
		$va{'tab_table'} = 'sl_leads_flash';
	}
}


sub load_tabs1 {
# --------------------------------------------------------
##############################################
## tab1 : Leads
##############################################
# Last Modified RB: 05/15/09  16:35:25 -- Si el producsto es un Set, se cargan sus partes


	## Get Calls 
	my (@c) = split(/,/,$cfg{'srcolors'});
	$lead = $in{'id_leads'};
	$lead =~ s/-|\(|\)|\+|\.|\s//g;
	$lead = int($lead);
	my ($sth) = &Do_SQL("SELECT COUNT(*) FROM sl_leads_calls  WHERE ID_leads = '$lead';");
	$va{'matches'} = $sth->fetchrow;
	if ($va{'matches'}>0){
		(!$in{'nh'}) and ($in{'nh'}=1);
		$first = ($in{'nh'} - 1) * $usr{'pref_maxh'};			
		($va{'pageslist'},$qs) = &pages_list($in{'nh'},$script_url,$va{'matches2'},$usr{'pref_maxh'});
		my ($sth) = &Do_SQL("SELECT * FROM sl_leads_calls  WHERE ID_leads = '$lead' ORDER BY ID_leads_calls DESC LIMIT $first,$usr{'pref_maxh'};");
		while ($rec = $sth->fetchrow_hashref){
			$d = 1 - $d;
			(!$rec->{'Duration'}) and ($rec->{'Duration'} = 'N/A');
			$va{'searchresults'} .= "<tr bgcolor='$c[$d]'>\n";
			$va{'searchresults'} .= "  <td class='smalltext'>".&format_phone($rec->{'ID_leads'})."</td>\n";
			$va{'searchresults'} .= "  <td class='smalltext'>$rec->{'IO'}</td>\n";
			$va{'searchresults'} .= "  <td class='smalltext'>".&load_name("admin_users","ID_admin_users",$rec->{'ID_admin_users'},"CONCAT(FirstName,' ',LastName)")." ($rec->{'ID_admin_users'})</td>\n";
			$va{'searchresults'} .= "  <td class='smalltext'>$rec->{'Calif'}</td>\n";
			$va{'searchresults'} .= "  <td class='smalltext'>$rec->{'Duration'}</td>\n";
			
			$va{'searchresults'} .= "  <td class='smalltext'>$rec->{'Date'}</td>\n";
			$va{'searchresults'} .= "  <td class='smalltext'>$rec->{'Time'}</td>\n";
			$va{'searchresults'} .= "</tr>\n";
			&auth_logging('opr_orders_outcall_viewed',$in{'id_orders'});
		}
	}else{
		$va{'pageslist'} = 1;
		$va{'searchresults'} = qq|
			<tr>
				<td colspan='5' align='center'>|.&trans_txt('search_nomatches').qq|</td>
			</tr>\n|;
	}

	$va{'keyname'} = 'Leads';
	&load_db_fields_values($in{'db'},'ID_leads_flash',$in{'id_leads_flash'},'*');
}

1;