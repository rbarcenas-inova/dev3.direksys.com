####################################################################
########                  Item                  ########
####################################################################

sub build_tabs {
# --------------------------------------------------------
# Forms Involved: specials_tab1.html, specials_tab2.html,specials_tab3.html
# Created on: 
# Last Modified on: 9/14/2007 3:46PM - Items
# Last Modified by: Rafael Sobrino
# Author: Carlos Haas
# Description : 

	$in{'tab'} = int($in{'tab'});
	my ($tab_jump);
	if (!$in{'tab'}) {
		$in{'tab'}=1;
	}else{
		$tab_jump = "<script language='JavaScript'>\n  self.document.location.href = '#tabs';\n</script>";
	}
	if ($in{'tab'}>0 and $in{'tab'}<=3){
		if ($in{'tab'} eq '1'){
			if (!$perm{'specials_tab1'}) { 
				$va{'pageslist'} = 1;
				$va{'searchresults'} = qq|
					<tr>
						<td colspan='7' align="center">|.&trans_txt('not_auth').qq|</td>
					</tr>\n|;
			}else{
				if ($in{'add_special'}){
					#&cgierr;
					$in{'add_special'} = int($in{'add_special'});
					my ($sth) = &Do_SQL("UPDATE sl_specials SET ID_products='$in{'add_special'}' WHERE ID_specials='$in{'id_specials'}'");
					$in{'id_products'} = $in{'add_special'};
					&auth_logging('specials_itemupd',$in{'id_specials'});
				}else{
					## Items List
					my ($err,$item);
					if ($in{'ajax_resp'}){
						my ($sth) = &Do_SQL("UPDATE sl_specials SET ID_products='$in{'ajax_resp'}' WHERE ID_specials='$in{'id_specials'}'");
						&auth_logging('specials_itemupd',$in{'id_specials'});
						$in{'id_products'} = $in{'ajax_resp'};
					}
				}
				if ($in{'id_products'}){
					$va{'products_description'} .= qq|
<IFRAME SRC="$script_url?cmd=products&view=$in{'id_products'}&frameview=1" name="rcmd" TITLE="Recieve Commands" width="540" height="250" FRAMEBORDER="0" MARGINWIDTH="0" MARGINHEIGHT="0" SCROLLING="auto">
<H2>Unable to do the script</H2>
<H3>Please update your Browser</H3>
</IFRAME>\n|;
				}
			}
		}elsif($in{'tab'} eq '2'){
			if (!$perm{'specials_tab2'}) { 
				$va{'pageslist'} = 1;
				$va{'searchresults'} = qq|
					<tr>
						<td colspan='7' align="center">|.&trans_txt('not_auth').qq|</td>
					</tr>\n|;
			}else{	
				## Comments
				if ($in{'action'}){
					if (!$in{'notes'} or !$in{'notestype'}){
						$va{'messages'} = &trans_txt('reqfields');
					}else{
						$va{'messages'} = &trans_txt('shows_noteadded');
						my ($sth) = &Do_SQL("INSERT INTO sl_specials_notes SET id_specials='$in{'id_specials'}',Notes='".&filter_values($in{'notes'})."',Type='$in{'notestype'}',Date=Curdate(),Time=NOW(),ID_admin_users='$usr{'id_admin_users'}'");
						delete($in{'notes'});
						delete($in{'notestype'});
						&auth_logging('shows_noteadded',$in{'id_specials'});
					}
				}
				## VRM
				my ($query);
				if ($in{'filter'}){
					$query = "AND Type='".&filter_values($in{'filter'})."' ";
				}
				my (@c) = split(/,/,$cfg{'srcolors'});
				my ($sth) = &Do_SQL("SELECT COUNT(*) FROM sl_specials_notes WHERE id_specials='$in{'id_specials'}' $query");
				$va{'matches'} = $sth->fetchrow;
				if ($va{'matches'}>0){
					(!$in{'nh'}) and ($in{'nh'}=1);
					$first = ($in{'nh'} - 1) * $usr{'pref_maxh'};			
					($va{'pageslist'},$qs) = &pages_list($in{'nh'},"/cgi-bin/mod/$usr{'application'}/dbman",$va{'matches'},$usr{'pref_maxh'});
					my ($sth) = &Do_SQL("SELECT sl_specials_notes.ID_admin_users,sl_specials_notes.Date as mDate,sl_specials_notes.Time as mTime,FirstName,LastName,Type,Notes FROM sl_specials_notes,admin_users WHERE id_specials='$in{'id_specials'}' AND sl_specials_notes.ID_admin_users=admin_users.ID_admin_users $query ORDER BY id_specials_notes DESC LIMIT $first,$usr{'pref_maxh'};");
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
			}
		}elsif($in{'tab'} eq '3'){
			if (!$perm{'specials_tab3'}) { 
				$va{'pageslist'} = 1;
				$va{'searchresults'} = qq|
					<tr>
						<td colspan='7' align="center">|.&trans_txt('not_auth').qq|</td>
					</tr>\n|;
			}else{	
				## Logs
				my (@c) = split(/,/,$cfg{'srcolors'});
				my ($sth) = &Do_SQL("SELECT COUNT(*) FROM admin_logs WHERE tbl_name='sl_specials' AND Action='$in{'view'}'");
				$va{'matches'} = $sth->fetchrow;
				if ($va{'matches'}>0){
					(!$in{'nh'}) and ($in{'nh'}=1);
					$first = ($in{'nh'} - 1) * $usr{'pref_maxh'};			
					($va{'pageslist'},$qs) = &pages_list($in{'nh'},"/cgi-bin/mod/$usr{'application'}/dbman",$va{'matches'},$usr{'pref_maxh'});
					my ($sth) = &Do_SQL("SELECT * FROM admin_logs,admin_users WHERE tbl_name='sl_specials' AND Action='$in{'view'}' AND admin_logs.ID_admin_users=admin_users.ID_admin_users ORDER BY ID_logs DESC LIMIT $first,$usr{'pref_maxh'};");
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
		}
		return "<a name='tabs' id='tabs'>&nbsp;</a>" . &build_page('specials_tab'.$in{'tab'}.'.html') .$tab_jump;
	}
}

1;