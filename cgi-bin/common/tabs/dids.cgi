#!/usr/bin/perl
####################################################################
########                  Purchase Orders                   ########
####################################################################

sub load_tabsconf {
# --------------------------------------------------------
	if ($in{'tab'} eq 6){
		## Notes Tab
		$va{'tab_type'}  = 'notes';
		$va{'tab_title'} = &trans_txt('notes');
		$va{'tab_table'} = 'sl_mediadids_notes';
	}elsif($in{'tab'} eq 7){
		## Notes Tab
		$va{'tab_type'}  = 'logs';
		$va{'tab_title'} = &trans_txt('logs');
		$va{'tab_table'} = 'sl_mediadids';
	}
}

sub load_tabs1 {
# --------------------------------------------------------
##############################################
## tab1 : ITEMS
##############################################
# Falta Codigo
	#&cgierr();
	## ADD
	if ($in{'action'}){
		#&cgierr("INSERT INTO sl_mediadids_notes SET id_mediadids='$in{'id_mediadids'}',Notes='".&filter_values($in{'notestxt'})."',Type='$in{'notestype'}',Date=Curdate(),Time=NOW(),ID_admin_users='$usr{'id_admin_users'}'");
		if (!$in{'fromdate'} or !$in{'todate'} or !$in{'fromtime'} or !$in{'totime'}){
			$va{'message'} = &trans_txt('reqfields');
		}else{

			my ($sth) = &Do_SQL("SELECT IF(TIMESTAMPDIFF(SECOND,'$in{'fromdate'} $in{'fromtime'}','$in{'todate'} $in{'totime'}') < 600
						OR TIMESTAMPDIFF(MINUTE,NOW(),'$in{'fromdate'} $in{'fromtime'}') < 5,1,0);");
			if($sth->fetchrow()){
				$va{'message'} = &trans_txt('invalid') . 'The exception can\'t be less than 5 mins away fron now.';
			}else{
				&connect_db_w($cfg{'dbi_db_pbx'},$cfg{'dbi_host_pbx'},$cfg{'dbi_user_pbx'},$cfg{'dbi_pw_pbx'});
				$va{'message'} = &trans_txt('mm_dids_exceptionadded');
				my ($sth) = &Do_SQL("SELECT destination FROM sl_numbers WHERE didmx='$in{'didmx'}';",1);
				my($this_destination) = $sth->fetchrow();
				my ($sth) = &Do_SQL("INSERT INTO sl_cron_scripts VALUES(0,\"UPDATE `sl_numbers` SET destination='$in{'todestination'}' WHERE `didmx` = '$in{'didmx'}'\",'s7','sql',0,'$in{'fromdate'}','$in{'fromtime'}','','Active',1);");
				my ($sth) = &Do_SQL("INSERT INTO sl_cron_scripts VALUES(0,\"UPDATE `sl_numbers` SET destination='$this_destination' WHERE `didmx` = '$in{'didmx'}';\",'s7','sql',0,'$in{'todate'}','$in{'totime'}','','Active',1);");
				my ($sth) = &Do_SQL("INSERT INTO sl_mediadids_notes SET id_mediadids='$in{'id_mediadids'}',Notes='DIDMx:$in{'didmx'}\nFrom CC:$this_destination\nTo CC:$in{'todestination'}\nFrom:$in{'fromdate'} $in{'todate'}\nTo:$in{'todate'} $in{'totime'}',Type='Low',Date=CURDATE(),Time=CURTIME(),ID_admin_users='$usr{'id_admin_users'}';");
				delete($in{'action'});
				&auth_logging('mm_dids_exceptionadded',$in{'id_mediadids'});
			}
		}

	}


	if($in{'delete'}){
		my ($sth) = &Do_SQL("UPDATE sl_cron_scripts SET Status='Inactive' WHERE ID_cron_scripts='$in{'delete'}';");
		if($sth->rows() > 0){
			delete($in{'action'});
			&auth_logging('mm_dids_exceptiondeleted',$in{'id_mediadids'});
		}
	}

	## NOTES
	my ($query);
	if ($in{'filter'}){
		$query = "AND Status='".&filter_values($in{'filter'})."' ";
		$va{'query'} = $in{'filter'};
		$in{'tabs'} = 1;
	}
	my (@c) = split(/,/,$cfg{'srcolors'});
	my ($sth) = &Do_SQL("SELECT COUNT(*) FROM sl_cron_scripts WHERE server='s7' AND type='sql' AND script LIKE '%$in{'didmx'}%' $query");
	$va{'matches'} = $sth->fetchrow;
	if ($va{'matches'}>0){
		if ($in{'print'}){
			$sth = &Do_SQL("SELECT sl_cron_scripts.*,FirstName,LastName FROM sl_cron_scripts,admin_users WHERE server='s7' AND type='sql' AND script LIKE '%$in{'didmx'}%' AND sl_cron_scripts.ID_admin_users=admin_users.ID_admin_users $query ORDER BY ID_cron_scripts DESC;");
		}else{
			(!$in{'nh'}) and ($in{'nh'}=1);
			$first = ($in{'nh'} - 1) * $usr{'pref_maxh'};
			($va{'pageslist'},$qs) = &pages_list($in{'nh'},"/cgi-bin/mod/$usr{'application'}/dbman",$va{'matches'},$usr{'pref_maxh'});
			$sth = &Do_SQL("SELECT sl_cron_scripts.*,FirstName,LastName FROM sl_cron_scripts,admin_users WHERE server='s7' AND type='sql' AND script LIKE '%$in{'didmx'}%' AND sl_cron_scripts.ID_admin_users=admin_users.ID_admin_users $query ORDER BY ID_cron_scripts DESC LIMIT $first,$usr{'pref_maxh'};");
		}

		while ($rec = $sth->fetchrow_hashref){
			$d = 1 - $d;
			if($rec->{'script'} =~ /destination='(\w*)'/){
				$rec->{'Destination'} = $1;
			}
			my $delete_this = $rec->{'Status'} eq 'Active' ? "<a href='javascript:trjump(\"[va_script_url]?cmd=[in_cmd]&view=[in_id_mediadids]&tab=[va_activetab]&delete=$rec->{'ID_cron_scripts'}&tabs=1\")'><img src='[va_imgurl]/[ur_pref_style]/b_drop.png' title='Delete' alt='' border='0'></a>" : '';
			my $this_style = $rec->{'Status'} eq 'Inactive' ? "style='text-decoration:line-through;'" : '';

			$va{'searchresults'} .= "<tr bgcolor='$c[$d]' $this_style>\n";
			$va{'searchresults'} .= "  <td class='smalltext' valign='top'>$delete_this</td>\n";
			$va{'searchresults'} .= "  <td class='smalltext' valign='top'>$rec->{'Destination'}</td>\n";
			$va{'searchresults'} .= "  <td class='smalltext' valign='top'>$rec->{'scheduledate'} $rec->{'scheduletime'}</td>\n";
			$va{'searchresults'} .= "  <td class='smalltext' valign='top'>$rec->{'applieddate'}</td>\n";
			$va{'searchresults'} .= "  <td class='smalltext' valign='top'>$rec->{'Status'}</td>\n";
			$va{'searchresults'} .= "  <td class='smalltext' valign='top'>($rec->{'ID_admin_users'}) $rec->{'FirstName'} $rec->{'LastName'}</td>\n";
			$va{'searchresults'} .= "</tr>\n";
		}
	}else{
		$va{'pageslist'} = 1;
		$va{'searchresults'} = qq|
			<tr>
				<td colspan='3' align="center">|.&trans_txt('search_nomatches').qq|</td>
			</tr>\n|;
	}


}


sub load_tabs2 {
# --------------------------------------------------------
##############################################
## tab2 : CONTRACTS
###########&cgierr;###################################

	my (@c) = split(/,/,$cfg{'srcolors'});
	my ($sth) = &Do_SQL("SELECT COUNT(*) FROM sl_mediacontracts WHERE DestinationDID='$in{'didmx'}'");
	$va{'matches'} = $sth->fetchrow;
	if ($va{'matches'}>0){
		(!$in{'nh'}) and ($in{'nh'}=1);
		$first = ($in{'nh'} - 1) * $usr{'pref_maxh'};			
		#&cgierr;
		($va{'pageslist'},$qs) = &pages_list($in{'nh'},"/cgi-bin/mod/$usr{'application'}/dbman",$va{'matches'},$usr{'pref_maxh'});
		my ($sth) = &Do_SQL("SELECT * FROM sl_mediacontracts WHERE DestinationDID='$in{'didmx'}' LIMIT $first,$usr{'pref_maxh'};");
		while ($rec = $sth->fetchrow_hashref){
			$d = 1 - $d;
			$va{'searchresults'} .= "<tr bgcolor='$c[$d]'>\n";
			$va{'searchresults'} .= "  <td class='smalltext'><a href='/cgi-bin/mod/admin/dbman?cmd=mm_contracts&view=$rec->{'ID_mediacontracts'}'>$rec->{'ID_mediacontracts'}</a></td>\n";
			$va{'searchresults'} .= "  <td class='smalltext'>$rec->{'ESTDay'}</td>\n";
			$va{'searchresults'} .= "  <td class='smalltext'>$rec->{'ESTTime'}</td>\n";
			$va{'searchresults'} .= "  <td class='smalltext'>$rec->{'Station'}</td>\n";
			$va{'searchresults'} .= "  <td class='smalltext'>$rec->{'DMA'}</td>\n";
			$va{'searchresults'} .= "  <td class='smalltext'>$rec->{'Status'}</td>\n";
			$va{'searchresults'} .= "</tr>\n";
		}
	}else{
		$va{'pageslist'} = 1;
		$va{'searchresults'} = qq|
			<tr>
				<td colspan='3' align="center">|.&trans_txt('search_nomatches').qq|</td>
			</tr>\n|;
	}

	$va{'keyname'} = 'medialogs';

}



sub load_tabs3{
# --------------------------------------------------------
##############################################
## tab5 : Histoty
##############################################
# Forms Involved: 
# Created on: 12/8/2011 1:18:09 PM
# Author: Carlos Haas
# Description :   
# Parameters :

	my (@c) = split(/,/,$cfg{'srcolors'});
	my ($sth) = &Do_SQL("SELECT COUNT(*) FROM sl_mediadids_logs WHERE id_mediadids='$in{'id_mediadids'}'");
	$va{'matches'} = $sth->fetchrow;
	if ($va{'matches'}>0){
		(!$in{'nh'}) and ($in{'nh'}=1);
		$first = ($in{'nh'} - 1) * $usr{'pref_maxh'};			
		($va{'pageslist'},$qs) = &pages_list($in{'nh'},"/cgi-bin/mod/$usr{'application'}/dbman",$va{'matches'},$usr{'pref_maxh'});
		my ($sth) = &Do_SQL("SELECT * FROM sl_mediadids_logs WHERE id_mediadids='$in{'id_mediadids'}' LIMIT $first,$usr{'pref_maxh'};");
		while ($rec = $sth->fetchrow_hashref){
			$d = 1 - $d;
			$va{'searchresults'} .= "<tr bgcolor='$c[$d]'>\n";
			$va{'searchresults'} .= "  <td class='smalltext'><a href='/cgi-bin/mod/admin/dbman?cmd=mm_dids&view=$rec->{'id_mediadids'}'>$rec->{'id_mediadids'}</a></td>\n";
			$va{'searchresults'} .= "  <td class='smalltext'>$rec->{'DateTime'}</td>\n";
			$va{'searchresults'} .= "  <td class='smalltext'>$rec->{'Changes'}</td>\n";
			$va{'searchresults'} .= "</tr>\n";
		}
	}else{
		$va{'pageslist'} = 1;
		$va{'searchresults'} = qq|
			<tr>
				<td colspan='3' align="center">|.&trans_txt('search_nomatches').qq|</td>
			</tr>\n|;
	}

	$va{'keyname'} = 'medialogs';
}

sub load_tabs4{
# --------------------------------------------------------
##############################################
## tab5 : Orders
##############################################
# Forms Involved: 
# Created on: 12/8/2011 1:33:33 PM
# Author: Carlos Haas.
# Description :   
# Parameters :


}

sub load_tabs5{
# --------------------------------------------------------
##############################################
## tab5 : Orders
##############################################
# Forms Involved: 
# Created on: 09/15/09 11:49:50
# Author: Carlos Haas.
# Description :   
# Parameters :

	my (@c) = split(/,/,$cfg{'srcolors'});
	my ($sth) = &Do_SQL("SELECT COUNT(*) FROM sl_orders WHERE dnis='$in{'didmx'}'");
	$va{'matches'} = $sth->fetchrow;
	if ($va{'matches'}>0){
		(!$in{'nh'}) and ($in{'nh'}=1);
		$first = ($in{'nh'} - 1) * $usr{'pref_maxh'};			
		($va{'pageslist'},$qs) = &pages_list($in{'nh'},"/cgi-bin/mod/$usr{'application'}/dbman",$va{'matches'},$usr{'pref_maxh'});
		my ($sth) = &Do_SQL("SELECT * FROM sl_orders WHERE dnis='$in{'didmx'}' LIMIT $first,$usr{'pref_maxh'};");
		while ($rec = $sth->fetchrow_hashref){
			$d = 1 - $d;
			$va{'searchresults'} .= "<tr bgcolor='$c[$d]'>\n";
			$va{'searchresults'} .= "  <td class='smalltext'><a href='/cgi-bin/mod/admin/dbman?cmd=opr_orders&view=$rec->{'ID_orders'}'>$rec->{'ID_orders'}</a></td>\n";
			$va{'searchresults'} .= "  <td class='smalltext'>$rec->{'Date'}</td>\n";
			$va{'searchresults'} .= "  <td class='smalltext'>$rec->{'Status'}</td>\n";
			$va{'searchresults'} .= "</tr>\n";
		}
	}else{
		$va{'pageslist'} = 1;
		$va{'searchresults'} = qq|
			<tr>
				<td colspan='3' align="center">|.&trans_txt('search_nomatches').qq|</td>
			</tr>\n|;
	}

	$va{'keyname'} = 'Orders';
}

1;