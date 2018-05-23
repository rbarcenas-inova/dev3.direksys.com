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
		$va{'tab_table'} = 'sl_keypoints_notes';
	}elsif($in{'tab'} eq 4){
		## Notes Tab
		$va{'tab_type'}  = 'logs';
		$va{'tab_title'} = &trans_txt('logs');
		$va{'tab_table'} = 'sl_keypoints';
	}
}

sub load_tabs1 {
# --------------------------------------------------------
##############################################
## tab1 : Families
##############################################
	$in{'drop'} = int($in{'drop'});
	$in{'new_id_keypoints'} = int($in{'new_id_keypoints'});
	if ($in{'tabaction'} and $in{'new_id_keypoints'}){
		## TODO... Permisos
		my ($sth) = &Do_SQL("REPLACE INTO sl_keypfunctions_keypoints SET 
					ID_keypoints='$in{'new_id_keypoints'}',
					ID_keypfunctions='$in{'id_keypfunctions'}',
					Date=CURDATE(), Time=CURTIME(),ID_admin_users='$usr{'id_admin_users'}'  ");
		delete($in{'new_id_keypoints'});
		&auth_logging('acc_keypfunctions_added',$in{'id_keypfunctions'});
	}elsif ($in{'drop'}){
		## TODO... Permisos
		my ($sth) = &Do_SQL("DELETE FROM sl_keypfunctions_keypoints WHERE ID_keypfunctions='$in{'id_keypfunctions'}' AND ID_keypfunctions_keypoints=$in{'drop'}");
		&auth_logging('acc_keypfunctions_droped',$in{'id_keypoints'});
	}	
	
	## ITEMS LIST
	my (@c) = split(/,/,$cfg{'srcolors'});
	my ($d);
	my ($sth) = &Do_SQL("SELECT COUNT(*) FROM sl_keypfunctions_keypoints LEFT JOIN sl_keypoints ON sl_keypoints.ID_keypoints = sl_keypfunctions_keypoints.ID_keypoints WHERE ID_keypfunctions='$in{'id_keypfunctions'}' AND  sl_keypfunctions_keypoints.ID_keypoints>0");
	$va{'matches'} = $sth->fetchrow;
	if ($va{'matches'}>0){
		if ($in{'print'}){
			$sth = &Do_SQL("SELECT * FROM sl_keypfunctions_keypoints LEFT JOIN sl_keypoints ON sl_keypoints.ID_keypoints = sl_keypfunctions_keypoints.ID_keypoints WHERE ID_keypfunctions='$in{'id_keypfunctions'}' AND  sl_keypfunctions_keypoints.ID_keypoints>0 ORDER BY Name DESC ");
		}else{
			(!$in{'nh'}) and ($in{'nh'}=1);
			$first = ($in{'nh'} - 1) * $usr{'pref_maxh'};			
			($va{'pageslist'},$qs) = &pages_list($in{'nh'},"/cgi-bin/mod/$usr{'application'}/dbman",$va{'matches'},$usr{'pref_maxh'});
			$sth = &Do_SQL("SELECT * FROM sl_keypfunctions_keypoints LEFT JOIN sl_keypoints ON sl_keypoints.ID_keypoints = sl_keypfunctions_keypoints.ID_keypoints WHERE ID_keypfunctions='$in{'id_keypfunctions'}' AND  sl_keypfunctions_keypoints.ID_keypoints>0 ORDER BY Name DESC LIMIT $first,$usr{'pref_maxh'};");			
		}
	
		
		while ($rec = $sth->fetchrow_hashref){
			$d = 1 - $d;
			$va{'searchresults'} .= "<tr bgcolor='$c[$d]'>\n";
			$va{'searchresults'} .= qq|<td class='smalltext' valign='top' nowrap>
								<a href="/cgi-bin/mod/setup/dbman?cmd=acc_keypfunctions&view=$in{'id_keypfunctions'}&tab=1&drop=$rec->{'ID_keypfunctions_keypoints'}"><img src='$va{'imgurl'}/$usr{'pref_style'}/b_drop.png' title='Drop' alt='' border='0'></a>
								$rec->{'Name'}</td>\n|;
			$va{'searchresults'} .= "</tr>\n";
		}	
	}else{
		$va{'pageslist'} = 1;
		my ($sth) = &Do_SQL("SELECT COUNT(*) FROM sl_keypfunctions_keypoints WHERE ID_keypfunctions='$in{'id_keypfunctions'}' AND ID_keypoints IS NULL");
		if ($sth->fetchrow>0){
			$va{'searchresults'} = qq|
				<tr>
					<td align="center">|.&trans_txt('all_keypoints').qq|</td>
				</tr>\n|;
		}else{
			$va{'searchresults'} = qq|
				<tr>
					<td align="center">|.&trans_txt('search_nomatches').qq|</td>
				</tr>\n|;
		}
	}

}

sub load_tabs2 {
# --------------------------------------------------------
##############################################
## tab1 : Params
##############################################
	$in{'drop'} = int($in{'drop'});
	$in{'new_line'} = int($in{'new_line'});
	if ($in{'tabaction'} and $in{'new_name'} and $in{'new_desc'} and $in{'new_line'}){
		## TODO... Permisos
		my ($sth) = &Do_SQL("REPLACE INTO sl_keypfunctions_params SET 
					ID_keypfunctions='$in{'id_keypfunctions'}',
					ParamName='$in{'new_name'}',
					ParamDesc='$in{'new_desc'}',
					Line='$in{'new_line'}',
					Date=CURDATE(), Time=CURTIME(),ID_admin_users='$usr{'id_admin_users'}'  ");
		delete($in{'new_name'});
		delete($in{'new_desc'});
		&auth_logging('acc_keypfunctions_padded',$in{'id_keypfunctions'});
	}elsif ($in{'drop'}){
		## TODO... Permisos
		my ($sth) = &Do_SQL("DELETE FROM sl_keypfunctions_params WHERE ID_keypfunctions='$in{'id_keypfunctions'}' AND ID_keypfunctions_params=$in{'drop'}");
		&auth_logging('acc_keypfunctions_pdroped',$in{'id_keypoints'});
	}
	delete($in{'new_line'});	
	
	## ITEMS LIST
	my (@c) = split(/,/,$cfg{'srcolors'});
	my ($d);
	my ($sth) = &Do_SQL("SELECT COUNT(*) FROM sl_keypfunctions_params  WHERE ID_keypfunctions='$in{'id_keypfunctions'}'");
	$va{'matches'} = $sth->fetchrow;
	if ($va{'matches'}>0){
		if ($in{'print'}){
			$sth = &Do_SQL("SELECT * FROM sl_keypfunctions_params WHERE ID_keypfunctions='$in{'id_keypfunctions'}' ORDER BY Line ASC ");
		}else{
			(!$in{'nh'}) and ($in{'nh'}=1);
			$first = ($in{'nh'} - 1) * $usr{'pref_maxh'};			
			($va{'pageslist'},$qs) = &pages_list($in{'nh'},"/cgi-bin/mod/$usr{'application'}/dbman",$va{'matches'},$usr{'pref_maxh'});
			$sth = &Do_SQL("SELECT * FROM sl_keypfunctions_params WHERE ID_keypfunctions='$in{'id_keypfunctions'}' ORDER BY Line ASC LIMIT $first,$usr{'pref_maxh'};");			
		}
		while ($rec = $sth->fetchrow_hashref){
			$d = 1 - $d;
			$va{'searchresults'} .= "<tr bgcolor='$c[$d]'>\n";
			$va{'searchresults'} .= qq|<td class='smalltext' valign='top' nowrap>
								<a href="/cgi-bin/mod/setup/dbman?cmd=acc_keypfunctions&view=$in{'id_keypfunctions'}&tab=2&drop=$rec->{'ID_keypfunctions_params'}"><img src='$va{'imgurl'}/$usr{'pref_style'}/b_drop.png' title='Drop' alt='' border='0'></a>
								$rec->{'Line'}</td>\n|;
			$va{'searchresults'} .= "  <td class='smalltext'' valign='top' nowrap>$rec->{'ParamName'}</td>\n";
			$va{'searchresults'} .= "  <td class='smalltext'' valign='top'>$rec->{'ParamDesc'}</td>\n";
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



 1;