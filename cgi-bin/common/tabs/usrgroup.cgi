####################################################################
########                  DEVELOPER JOBS                  ########
####################################################################

sub load_tabsconf {
# --------------------------------------------------------
	if ($in{'tab'} eq 3){
		## Notes Tab
		$va{'tab_type'}  = 'logs';
		$va{'tab_title'} = &trans_txt('logs');
		$va{'tab_table'} = 'sl_keypoints';
	}
}

sub load_tabs1 {
# --------------------------------------------------------
##############################################
## tab1 : Perms
##############################################
	$in{'drop'} = int($in{'drop'});
	$in{'add_id'} = int($in{'add_id'});
	$va{'addbtn'} = qq|<a href='javascript:trjump("/cgi-bin/mod/[ur_application]/dbman?cmd=[in_cmd]&view=[in_id_admin_groups]&tab=[in_tab]&addusr=1")'><img src='[va_imgurl]/[ur_pref_style]/b_add.gif' title='Add User' alt='' border='0'></a>&nbsp;|;
	if ($in{'addusr'}){
		if(!&check_permissions($in{'cmd'},'_addusr','')){ return &html_unauth_tab; };
		$va{'new_tbname'} = 'usrgroup_tab1_add';
		if($in{'action'}){
			my ($sth) = &Do_SQL("SELECT ID_admin_users FROM admin_users WHERE ID_admin_users='$in{'add_id'}' or Username='".&filter_values($in{'add_username'})."'");
			my ($idu) = $sth->fetchrow;
			if ($idu > 0){
				my ($sth) = &Do_SQL("INSERT IGNORE INTO admin_users_groups SET ID_admin_users=$idu, ID_admin_groups=$in{'id_admin_groups'}");
				$va{'message'} = &trans_txt('record_added');
				&auth_logging('usrgroup_addusr',$in{'id_admin_groups'});
			}else{
				$va{'message'} = &trans_txt('reqfields');
			}
		}

	}elsif ($in{'drop'}){
		if(!&check_permissions($in{'cmd'},'_delusr','')){ return &html_unauth_tab; };
		my ($sth) = &Do_SQL("DELETE FROM admin_users_groups WHERE ID_admin_groups='$in{'id_admin_groups'}' AND ID_admin_users_perms=$in{'drop'}");
		&auth_logging('usrgroup_delusr',$in{'id_admin_groups'});
	}	
	## ITEMS LIST
	my (@c) = split(/,/,$cfg{'srcolors'});
	my ($d);
	my ($sth) = &Do_SQL("SELECT COUNT(*) FROM admin_users_groups LEFT JOIN admin_users ON admin_users.ID_admin_users=admin_users_groups.ID_admin_users WHERE ID_admin_groups='$in{'id_admin_groups'}'");
	$va{'matches'} = $sth->fetchrow;
	if ($va{'matches'}>0){
		if ($in{'print'}){
			$sth = &Do_SQL("SELECT * FROM admin_users_groups LEFT JOIN admin_users ON admin_users.ID_admin_users=admin_users_groups.ID_admin_users WHERE ID_admin_groups='$in{'id_admin_groups'}' ORDER BY LastName DESC ");
		}else{
			(!$in{'nh'}) and ($in{'nh'}=1);
			$first = ($in{'nh'} - 1) * $usr{'pref_maxh'};			
			($va{'pageslist'},$qs) = &pages_list($in{'nh'},"/cgi-bin/mod/$usr{'application'}/dbman",$va{'matches'},$usr{'pref_maxh'});
			$sth = &Do_SQL("SELECT * FROM admin_users_groups LEFT JOIN admin_users ON admin_users.ID_admin_users=admin_users_groups.ID_admin_users WHERE ID_admin_groups='$in{'id_admin_groups'}' ORDER BY LastName DESC LIMIT $first,$usr{'pref_maxh'};");			
		}
	
		
		while ($rec = $sth->fetchrow_hashref){
			$d = 1 - $d;
			$va{'searchresults'} .= "<tr bgcolor='$c[$d]'>\n";
			$va{'searchresults'} .= qq|<td class='smalltext' valign='top' nowrap>
								<a href="/cgi-bin/mod/$usr{'application'}/dbman?cmd=usrgroup&view=$in{'id_admin_groups'}&tab=1&drop=$rec->{'ID_admin_users_perms'}"><img src='$va{'imgurl'}/$usr{'pref_style'}/b_drop.png' title='Drop' alt='' border='0'></a>
								($rec->{'ID_admin_users'}) $rec->{'FirstName'} $rec->{'LastName'}</td>\n|;
			$va{'searchresults'} .= "  <td class='smalltext' valign='top'>$rec->{'Username'}</td>\n";
			$va{'searchresults'} .= "  <td class='smalltext' valign='top' nowrap><a href='mailto:$rec->{'Email'}'>$rec->{'Email'}</a></td>\n";
			$va{'searchresults'} .= "  <td class='smalltext' valign='top'>$rec->{'user_type'}</td>\n";
			$va{'searchresults'} .= "  <td class='smalltext' valign='top'>$rec->{'Status'}</td>\n";
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
## tab2 : Perms
##############################################
	$in{'drop'} = int($in{'drop'});
	$va{'message'} = '';
	$va{'addbtn'} = qq|<a href='javascript:trjump("/cgi-bin/mod/[ur_application]/dbman?cmd=[in_cmd]&view=[in_id_admin_groups]&tab=[in_tab]&addperm=1")'><img src='[va_imgurl]/[ur_pref_style]/b_add.gif' title='Add Perm' alt='' border='0'></a>&nbsp;|;
	if ($in{'addperm'}){
		if(!&check_permissions($in{'cmd'},'_addperm','')){ return &html_unauth_tab; };
		$va{'new_tbname'} = 'usrgroup_tab2_add';
		if($in{'action'}){
			##############################################################################################################
			######## 
			$sth_aux = &Do_SQL("SELECT COUNT(*) FROM admin_perms WHERE application='".&filter_values($in{'application'})."' AND type='".&filter_values($in{'type'})."' AND command='".&filter_values($in{$in{'type'}.'_cmd'})."'");
			if ($sth_aux->fetchrow == 0) {
				$sth = &Do_SQL("REPLACE INTO `admin_perms` (`Name`, `Node`, `application`, `command`, `type`, `tabs`, `ID_parent`, `Path`, `Status`, `Date`, `Time`, `ID_admin_users`) VALUES
(NULL, NULL, '".&filter_values($in{'application'})."', '".&filter_values($in{$in{'type'}.'_cmd'})."', '".&filter_values($in{'type'})."', 0, NULL, NULL, 'New', CURDATE(), CURTIME(), $usr{'id_admin_users'});");
			}
			##############################################################################################################
			$sth = &Do_SQL("SELECT COUNT(*) FROM admin_perms WHERE application='".&filter_values($in{'application'})."' AND type='".&filter_values($in{'type'})."' AND command='".&filter_values($in{$in{'type'}.'_cmd'})."'");
			if ($sth->fetchrow eq 1){
				## OK
				
				if ($in{'type'} eq 'admin'){
					$sth = &Do_SQL("INSERT IGNORE admin_groups_perms SET ID_admin_groups='$in{'id_admin_groups'}', application='".&filter_values($in{'application'})."',  command='".&filter_values($in{'admin_cmd'})."' ");
				}else{
					$sth = &Do_SQL("INSERT IGNORE admin_groups_perms SET ID_admin_groups='$in{'id_admin_groups'}', application='".&filter_values($in{'application'})."',  command='".&filter_values($in{'dbman_cmd'}.'_add'). "'") if ($in{'dbman_add'} eq 'on');
					$sth = &Do_SQL("INSERT INTO admin_groups_perms SET ID_admin_groups='$in{'id_admin_groups'}', application='".&filter_values($in{'application'})."',  command='".&filter_values($in{'dbman_cmd'}.'_view'). "'") if ($in{'dbman_view'} eq 'on');
					$sth = &Do_SQL("INSERT INTO admin_groups_perms SET ID_admin_groups='$in{'id_admin_groups'}', application='".&filter_values($in{'application'})."',  command='".&filter_values($in{'dbman_cmd'}.'_del'). "'") if ($in{'dbman_del'} eq 'on');
					$sth = &Do_SQL("INSERT INTO admin_groups_perms SET ID_admin_groups='$in{'id_admin_groups'}', application='".&filter_values($in{'application'})."',  command='".&filter_values($in{'dbman_cmd'}.'_edit'). "'") if ($in{'dbman_edit'} eq 'on');
					$sth = &Do_SQL("INSERT INTO admin_groups_perms SET ID_admin_groups='$in{'id_admin_groups'}', application='".&filter_values($in{'application'})."',  command='".&filter_values($in{'dbman_cmd'}.'_print'). "'") if ($in{'dbman_print'} eq 'on');
					$sth = &Do_SQL("SELECT tabs FROM admin_perms WHERE application='".&filter_values($in{'application'})."' AND type='dbman' AND command='".&filter_values($in{'dbman_cmd'})."'");		
					my ($tot_tabs) = $sth->fetchrow;
					if ($tot_tabs>0){
						for my $i(1..$tot_tabs){
							$sth = &Do_SQL("INSERT INTO admin_groups_perms SET ID_admin_groups='$in{'id_admin_groups'}', application='".&filter_values($in{'application'})."',  command='".&filter_values($in{'dbman_cmd'}.$i)."' ") if ($in{'dbman_tab'.$i} eq 'on');
						}
					}
				}
				$va{'message'} = &trans_txt('record_added');
				&auth_logging('usrgroup_addperm',$in{'id_admin_groups'});
			}else{
				$va{'message'} = &trans_txt('reqfields');
			}
		}
	}elsif ($in{'drop'}){
		if(!&check_permissions($in{'cmd'},'_delperm','')){ return &html_unauth_tab; };
		my ($sth) = &Do_SQL("DELETE FROM  admin_groups_perms WHERE ID_admin_groups='$in{'id_admin_groups'}' AND ID_admin_groups_perms=$in{'drop'}");
		&auth_logging('usrgroup_delperm',$in{'id_admin_groups'});
	}
	## ITEMS LIST
	my (@c) = split(/,/,$cfg{'srcolors'});
	my ($d);
	my ($sth) = &Do_SQL("SELECT COUNT(*) FROM admin_groups_perms WHERE ID_admin_groups='$in{'id_admin_groups'}'");
	$va{'matches'} = $sth->fetchrow;
	if ($va{'matches'}>0){
		if ($in{'print'}){
			$sth = &Do_SQL("SELECT * FROM admin_groups_perms WHERE ID_admin_groups='$in{'id_admin_groups'}' ORDER BY command DESC ");
		}else{
			(!$in{'nh'}) and ($in{'nh'}=1);
			$first = ($in{'nh'} - 1) * $usr{'pref_maxh'};			
			($va{'pageslist'},$qs) = &pages_list($in{'nh'},"/cgi-bin/mod/$usr{'application'}/dbman",$va{'matches'},$usr{'pref_maxh'});
			$sth = &Do_SQL("SELECT * FROM admin_groups_perms WHERE ID_admin_groups='$in{'id_admin_groups'}' ORDER BY command DESC LIMIT $first,$usr{'pref_maxh'};");			
		}
	
		
		while ($rec = $sth->fetchrow_hashref){
			$d = 1 - $d;
			$va{'searchresults'} .= "<tr bgcolor='$c[$d]'>\n";
			$va{'searchresults'} .= qq|  <td class='smalltext' valign='top'>
						<a href="/cgi-bin/mod/$usr{'application'}/dbman?cmd=usrgroup&nh=$in{'nh'}&tab=2&view=$in{'id_admin_groups'}&drop=$rec->{'ID_admin_groups_perms'}"><img src='$va{'imgurl'}/$usr{'pref_style'}/b_drop.png' title='Drop' alt='' border='0'></a>
							$rec->{'application'}</td>\n|;
			$va{'searchresults'} .= "  <td class='smalltext' valign='top'>$rec->{'command'}</td>\n";
			$va{'searchresults'} .= "</tr>\n";
		}	
	}else{
		$va{'pageslist'} = 1;
		$va{'searchresults'} = qq|
			<tr>
				<td colspan='2' align="center">|.&trans_txt('search_nomatches').qq|</td>
			</tr>\n|;
	}

}

1;