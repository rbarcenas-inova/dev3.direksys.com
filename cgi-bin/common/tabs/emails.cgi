#####################################################################
########                   DEVELOPER JOBS                    ########
#####################################################################


sub build_tabs {
# --------------------------------------------------------
	$in{'tab'} = int($in{'tab'});
	if(!&check_permissions($in{'cmd'},'',$in{'tab'})){ return &html_unauth_tab; };

	my ($tab_jump);
	if (!$in{'tab'}) {
		$in{'tab'}=1;
	}else{
		$tab_jump = "<script language='JavaScript'>\n  self.document.location.href = '#tabs';\n</script>";
	}
	
	if ($in{'tab'}>0 and $in{'tab'}<3){
		if ($in{'tab'} eq '1'){

				## Comments
				if ($in{'action'}){
					if ((!$in{'notes'} or !$in{'notestype'}) and !$in{'edit'}){
						$va{'tabmessages'} = &trans_txt('reqfields');
					}else{
						$va{'tabmessages'} = &trans_txt('eco_emails_noteadded');
						my ($sth) = &Do_SQL("INSERT INTO sl_bugs_notes SET id_bugs='$in{'id_bugs'}',Notes='".&filter_values($in{'notes'})."',Type='$in{'notestype'}',Date=Curdate(),Time=NOW(),ID_admin_users='$usr{'id_admin_users'}'");
						delete($in{'notes'});
						delete($in{'notestype'});
						&auth_logging('eco_emails_noteadded',$in{'id_bugs'});
					}
				}
				## VRM
				my ($query);
				if ($in{'filter'}){
					$query = "AND Type='".&filter_values($in{'filter'})."' ";
				}
				my (@c) = split(/,/,$cfg{'srcolors'});
				my ($sth) = &Do_SQL("SELECT COUNT(*) FROM sl_bugs_notes WHERE id_bugs='$in{'id_bugs'}' $query");
				$va{'matches'} = $sth->fetchrow;
				if ($va{'matches'}>0){
					(!$in{'nh'}) and ($in{'nh'}=1);
					$first = ($in{'nh'} - 1) * $usr{'pref_maxh'};			
					($va{'pageslist'},$qs) = &pages_list($in{'nh'},"/cgi-bin/mod/$usr{'application'}/dbman",$va{'matches'},$usr{'pref_maxh'});
					my ($sth) = &Do_SQL("SELECT sl_bugs_notes.ID_admin_users,sl_bugs_notes.Date as mDate,sl_bugs_notes.Time as mTime,FirstName,LastName,Type,Notes FROM sl_bugs_notes,admin_users WHERE ID_bugs='$in{'id_bugs'}' AND sl_bugs_notes.ID_admin_users=admin_users.ID_admin_users $query ORDER BY ID_bugs_notes DESC LIMIT $first,$usr{'pref_maxh'};");
					while ($rec = $sth->fetchrow_hashref){
						$d = 1 - $d;
						$rec->{'Notes'} =~ s/\n/<br>/g;
						$va{'searchresults'} .= "<tr bgcolor='$c[$d]'>\n";
						$va{'searchresults'} .= "  <td class='smalltext'>$rec->{'mDate'} &nbsp; $rec->{'mTime'}<br>($rec->{'ID_admin_users'}) $rec->{'FirstName'} $rec->{'LastName'}</td>\n";
						$va{'searchresults'} .= "  <td class='smalltext'>$rec->{'Type'}</td>\n";
						$va{'searchresults'} .= "  <td class='smalltext'>$rec->{'Notes'}</td>\n";
						$va{'searchresults'} .= "</tr>\n";
					}	
				}else{
					$va{'pageslist'} = 1;
					$va{'searchresults'} = qq|
						<tr>
							<td colspan='3' align="center">|.&trans_txt('search_nomatches').qq|</td>
						</tr>\n|;
				}
			
		}elsif($in{'tab'} eq '2'){
	
				## Logs
				my (@c) = split(/,/,$cfg{'srcolors'});
				my ($sth) = &Do_SQL("SELECT COUNT(*) FROM admin_logs WHERE tbl_name='sl_bugs' AND Action='$in{'id_bugs'}'");
				$va{'matches'} = $sth->fetchrow;
				if ($va{'matches'}>0){
					(!$in{'nh'}) and ($in{'nh'}=1);
					$first = ($in{'nh'} - 1) * $usr{'pref_maxh'};			
					($va{'pageslist'},$qs) = &pages_list($in{'nh'},"/cgi-bin/mod/$usr{'application'}/dbman",$va{'matches'},$usr{'pref_maxh'});
					my ($sth) = &Do_SQL("SELECT * FROM admin_logs,admin_users WHERE tbl_name='sl_bugs' AND Action='$in{'id_bugs'}' AND admin_logs.ID_admin_users=admin_users.ID_admin_users ORDER BY ID_admin_logs DESC LIMIT $first,$usr{'pref_maxh'};");
					while ($rec = $sth->fetchrow_hashref){
						$d = 1 - $d;
						$va{'searchresults'} .= "<tr bgcolor='$c[$d]'>\n";
						$va{'searchresults'} .= "   <td class='smalltext'>$rec->{'LogDate'}</td>\n";
						$va{'searchresults'} .= "   <td class='smalltext'>$rec->{'LogTime'}</td>\n";
						$va{'searchresults'} .= "   <td class='smalltext'>".&trans_txt($rec->{'Message'})."</td>\n";
						$va{'searchresults'} .= "   <td class='smalltext'>($rec->{'ID_admin_users'}) $rec->{'FirstName'} $rec->{'LastName'}</td>\n";
						$va{'searchresults'} .= "   <td class='smalltext'>$rec->{'IP'}</td>\n";
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
		return "<a name='tabs' id='tabs'>&nbsp;</a>" . &build_page('bugs_tab'.$in{'tab'}.'.html') .$tab_jump;
	}
}

sub print_tabs {
# --------------------------------------------------------
# Last Modification by JRG : 03/04/2009 : se quita paginacion para imprimir
	$in{'tab'} = int($in{'tab'});
	my ($tab_jump);
	if (!$in{'tab'}) {
		$in{'tab'}=1;
	}else{
		$tab_jump = "<script language='JavaScript'>\n  self.document.location.href = '#tabs';\n</script>";
	}
	
	if ($in{'tab'}>0 and $in{'tab'}<3){
		if ($in{'tab'} eq '1'){
				## Comments
				if ($in{'action'}){
					if ((!$in{'notes'} or !$in{'notestype'}) and !$in{'edit'}){
						$va{'tabmessages'} = &trans_txt('reqfields');
					}else{
						$va{'tabmessages'} = &trans_txt('eco_emails_noteadded');
						my ($sth) = &Do_SQL("INSERT INTO sl_bugs_notes SET id_bugs='$in{'id_bugs'}',Notes='".&filter_values($in{'notes'})."',Type='$in{'notestype'}',Date=Curdate(),Time=NOW(),ID_admin_users='$usr{'id_admin_users'}'");
						delete($in{'notes'});
						delete($in{'notestype'});
						&auth_logging('eco_emails_noteadded',$in{'id_bugs'});
					}
				}
				## VRM
				my ($query);
				if ($in{'filter'}){
					$query = "AND Type='".&filter_values($in{'filter'})."' ";
				}
				my (@c) = split(/,/,$cfg{'srcolors'});
				my ($sth) = &Do_SQL("SELECT COUNT(*) FROM sl_bugs_notes WHERE id_bugs='$in{'id_bugs'}' $query");
				$va{'matches'} = $sth->fetchrow;
				if ($va{'matches'}>0){
					(!$in{'nh'}) and ($in{'nh'}=1);
					$first = ($in{'nh'} - 1) * $usr{'pref_maxh'};			
					($va{'pageslist'},$qs) = &pages_list($in{'nh'},"/cgi-bin/mod/$usr{'application'}/dbman",$va{'matches'},$usr{'pref_maxh'});
					my ($sth) = &Do_SQL("SELECT sl_bugs_notes.ID_admin_users,sl_bugs_notes.Date as mDate,sl_bugs_notes.Time as mTime,FirstName,LastName,Type,Notes FROM sl_bugs_notes,admin_users WHERE ID_bugs='$in{'id_bugs'}' AND sl_bugs_notes.ID_admin_users=admin_users.ID_admin_users $query ORDER BY ID_bugs_notes DESC ;");
					while ($rec = $sth->fetchrow_hashref){
						$d = 1 - $d;
						$rec->{'Notes'} =~ s/\n/<br>/g;
						$va{'searchresults'} .= "<tr bgcolor='$c[$d]'>\n";
						$va{'searchresults'} .= "  <td class='smalltext'>$rec->{'mDate'} &nbsp; $rec->{'mTime'}<br>($rec->{'ID_admin_users'}) $rec->{'FirstName'} $rec->{'LastName'}</td>\n";
						$va{'searchresults'} .= "  <td class='smalltext'>$rec->{'Type'}</td>\n";
						$va{'searchresults'} .= "  <td class='smalltext'>$rec->{'Notes'}</td>\n";
						$va{'searchresults'} .= "</tr>\n";
					}	
				}else{
					$va{'pageslist'} = 1;
					$va{'searchresults'} = qq|
						<tr>
							<td colspan='3' align="center">|.&trans_txt('search_nomatches').qq|</td>
						</tr>\n|;
				}
			
		}elsif($in{'tab'} eq '2'){
		
				## Logs
				my (@c) = split(/,/,$cfg{'srcolors'});
				my ($sth) = &Do_SQL("SELECT COUNT(*) FROM admin_logs WHERE tbl_name='sl_bugs' AND Action='$in{'id_bugs'}'");
				$va{'matches'} = $sth->fetchrow;
				if ($va{'matches'}>0){
					my ($sth) = &Do_SQL("SELECT * FROM admin_logs,admin_users WHERE tbl_name='sl_bugs' AND Action='$in{'id_bugs'}' AND admin_logs.ID_admin_users=admin_users.ID_admin_users ORDER BY ID_admin_logs DESC ;");
					while ($rec = $sth->fetchrow_hashref){
						$d = 1 - $d;
						$va{'searchresults'} .= "<tr bgcolor='$c[$d]'>\n";
						$va{'searchresults'} .= "   <td class='smalltext'>$rec->{'LogDate'}</td>\n";
						$va{'searchresults'} .= "   <td class='smalltext'>$rec->{'LogTime'}</td>\n";
						$va{'searchresults'} .= "   <td class='smalltext'>".&trans_txt($rec->{'Message'})."</td>\n";
						$va{'searchresults'} .= "   <td class='smalltext'>($rec->{'ID_admin_users'}) $rec->{'FirstName'} $rec->{'LastName'}</td>\n";
						$va{'searchresults'} .= "   <td class='smalltext'>$rec->{'IP'}</td>\n";
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
		return  &build_page('bugs_print_tab'.$in{'tab'}.'.html');
	}
}
1;