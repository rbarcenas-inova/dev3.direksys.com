####################################################################
########                  SUPPLIERS                  ########
####################################################################

sub build_tabs {
# --------------------------------------------------------
	$in{'tab'} = int($in{'tab'});
	my ($tab_jump);
	if (!$in{'tab'}) {
		$in{'tab'}=1;
	}else{
		$tab_jump = "<script language='JavaScript'>\n  self.document.location.href = '#tabs';\n</script>";
	}
	if ($in{'tab'}>0 and $in{'tab'}<6){
		if ($in{'tab'} eq '1'){
			if (!$perm{'mer_suppliers_tab1'}) { 
				$va{'pageslist'} = 1;
				$va{'searchresults'} = qq|
					<tr>
						<td colspan='3' align="center">|.&trans_txt('not_auth').qq|</td>
					</tr>\n|;
			}else{				
				## VRM
				if ($in{'action'}){
					if ((!$in{'notes'} or !$in{'notestype'}) and !$in{'edit'}){
						$va{'tabmessages'} = &trans_txt('reqfields_short');
					}else{
						$va{'tabmessages'} = &trans_txt('mer_suppliers_noteadded');
						my ($sth) = &Do_SQL("INSERT INTO sl_suppliers_notes SET id_suppliers='$in{'id_suppliers'}',Notes='".&filter_values($in{'notes'})."',Type='$in{'notestype'}',Date=Curdate(),Time=NOW(),ID_admin_users='$usr{'id_admin_users'}'");
						delete($in{'notes'});
						delete($in{'notestype'});
						&auth_logging('mer_suppliers_noteadded',$in{'id_suppliers'});
					}
				}
				## VRM
				my ($query);
				if ($in{'filter'}){
					$query = "AND Type='".&filter_values($in{'filter'})."' ";
				}
				my (@c) = split(/,/,$cfg{'srcolors'});
				my ($sth) = &Do_SQL("SELECT COUNT(*) FROM sl_suppliers_notes WHERE id_suppliers='$in{'id_suppliers'}' $query");
				$va{'matches'} = $sth->fetchrow;
				if ($va{'matches'}>0){
					(!$in{'nh'}) and ($in{'nh'}=1);
					$first = ($in{'nh'} - 1) * $usr{'pref_maxh'};			
					($va{'pageslist'},$qs) = &pages_list($in{'nh'},"/cgi-bin/mod/$usr{'application'}/dbman",$va{'matches'},$usr{'pref_maxh'});
					my ($sth) = &Do_SQL("SELECT * FROM sl_suppliers_notes,admin_users WHERE id_suppliers='$in{'id_suppliers'}' AND sl_suppliers_notes.ID_admin_users=admin_users.ID_admin_users $query ORDER BY ID_suppliers_notes DESC LIMIT $first,$usr{'pref_maxh'};");
					while ($rec = $sth->fetchrow_hashref){
						$d = 1 - $d;
						$rec->{'Notes'} =~ s/\n/<br>/g;
						$va{'searchresults'} .= "<tr bgcolor='$c[$d]'>\n";
						$va{'searchresults'} .= "  <td class='smalltext'>$rec->{'Date'} $rec->{'Time'}<br>($rec->{'ID_admin_users'}) $rec->{'FirstName'} $rec->{'LastName'}</td>\n";
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
		}elsif($in{'tab'} eq '2'){
			if (!$perm{'mer_suppliers_tab2'}) { 
				$va{'pageslist'} = 1;
				$va{'searchresults'} = qq|
					<tr>
						<td colspan='6' align="center">|.&trans_txt('not_auth').qq|</td>
					</tr>\n|;
			}else{				
				## Logs
				my (@c) = split(/,/,$cfg{'srcolors'});
				my ($sth) = &Do_SQL("SELECT COUNT(*) FROM sl_supplies_suppliers WHERE id_suppliers='$in{id_suppliers}'");
				$va{'matches'} = $sth->fetchrow;
				if ($va{'matches'}>0){
					(!$in{'nh'}) and ($in{'nh'}=1);
					$first = ($in{'nh'} - 1) * $usr{'pref_maxh'};			
					($va{'pageslist'},$qs) = &pages_list($in{'nh'},"/cgi-bin/mod/$usr{'application'}/dbman",$va{'matches'},$usr{'pref_maxh'});
					my ($sth) = &Do_SQL("SELECT * FROM sl_supplies_suppliers,sl_supplies WHERE sl_supplies_suppliers.id_suppliers='$in{id_suppliers}' AND sl_supplies.ID_supplies=sl_supplies_suppliers.ID_supplies ORDER BY sl_supplies.ID_supplies DESC LIMIT $first,$usr{'pref_maxh'};");
					while ($rec = $sth->fetchrow_hashref){
						$d = 1 - $d;
						$va{'searchresults'} .= "<tr bgcolor='$c[$d]'>\n";
						$va{'searchresults'} .= "   <td class='smalltext'><a href='$script_url?cmd=mer_supplies&view=$rec->{'ID_supplies'}'>$rec->{'ID_supplies'}</td>\n";
						$va{'searchresults'} .= "   <td class='smalltext'>$rec->{'Name'}</td>\n";						
						$va{'searchresults'} .= "   <td class='smalltext'>".&format_price($rec->{'SPrice'})."</td>\n";
						$va{'searchresults'} .= "   <td class='smalltext'>$rec->{'Status'}</td>\n";						
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
		}elsif($in{'tab'} eq '3'){
			if (!$perm{'mer_suppliers_tab3'}) { 
				$va{'pageslist'} = 1;
				$va{'searchresults'} = qq|
					<tr>
						<td colspan='6' align="center">|.&trans_txt('not_auth').qq|</td>
					</tr>\n|;
			}else{
				$va{'searchresults'} = qq|
					<tr>
						<td colspan='6' align='center'>|.&trans_txt('na').qq|</td>
					</tr>\n|;
			}
		}elsif($in{'tab'} eq '4'){
			if (!$perm{'mer_suppliers_tab4'}) { 
				$va{'pageslist'} = 1;
				$va{'searchresults'} = qq|
					<tr>
						<td colspan='6' align="center">|.&trans_txt('not_auth').qq|</td>
					</tr>\n|;
			}else{
				## Logs
				my (@c) = split(/,/,$cfg{'srcolors'});
				my ($sth) = &Do_SQL("SELECT COUNT(*) FROM sl_supplies_suppliers WHERE id_suppliers='$in{id_suppliers}'");
				$va{'matches'} = $sth->fetchrow;
				if ($va{'matches'}>0){
					$va{'searchresults'} = qq|
						<tr>
							<td colspan='6' align="center">|.&trans_txt('na').qq|</td>
						</tr>\n|;
				}else{
					$va{'pageslist'} = 1;
					$va{'searchresults'} = qq|
						<tr>
							<td colspan='6' align='center'>|.&trans_txt('search_nomatches').qq|</td>
						</tr>\n|;
				}
			}								
		}elsif($in{'tab'} eq '5'){
			if (!$perm{'mer_suppliers_tab5'}) { 
				$va{'pageslist'} = 1;
				$va{'searchresults'} = qq|
					<tr>
						<td colspan='6' align="center">|.&trans_txt('not_auth').qq|</td>
					</tr>\n|;
			}else{				
				## Logs
				my (@c) = split(/,/,$cfg{'srcolors'});
				my ($sth) = &Do_SQL("SELECT COUNT(*) FROM admin_logs WHERE tbl_name='sl_suppliers' AND Action='$in{'view'}'");
				$va{'matches'} = $sth->fetchrow;
				if ($va{'matches'}>0){
					(!$in{'nh'}) and ($in{'nh'}=1);
					$first = ($in{'nh'} - 1) * $usr{'pref_maxh'};			
					($va{'pageslist'},$qs) = &pages_list($in{'nh'},"/cgi-bin/mod/$usr{'application'}/dbman",$va{'matches'},$usr{'pref_maxh'});
					my ($sth) = &Do_SQL("SELECT * FROM admin_logs,admin_users WHERE tbl_name='sl_suppliers' AND Action='$in{'view'}' AND admin_logs.ID_admin_users=admin_users.ID_admin_users ORDER BY ID_logs DESC LIMIT $first,$usr{'pref_maxh'};");
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
		return "<a name='tabs' id='tabs'>&nbsp;</a>" . &build_page('suppliers_tab'.$in{'tab'}.'.html') .$tab_jump;
	}
}

sub print_tabs {
# --------------------------------------------------------
# Last Modification by JRG : 03/06/2009 : Se elimina paginacion para imprimir
	$in{'tab'} = int($in{'tab'});
	my ($tab_jump);
	if (!$in{'tab'}) {
		$in{'tab'}=1;
	}else{
		$tab_jump = "<script language='JavaScript'>\n  self.document.location.href = '#tabs';\n</script>";
	}
	if ($in{'tab'}>0 and $in{'tab'}<6){
		if ($in{'tab'} eq '1'){
			if (!$perm{'mer_suppliers_tab1'}) { 
				$va{'pageslist'} = 1;
				$va{'searchresults'} = qq|
					<tr>
						<td colspan='3' align="center">|.&trans_txt('not_auth').qq|</td>
					</tr>\n|;
			}else{				
				## VRM
				if ($in{'action'}){
					if ((!$in{'notes'} or !$in{'notestype'}) and !$in{'edit'}){
						$va{'tabmessages'} = &trans_txt('reqfields_short');
					}else{
						$va{'tabmessages'} = &trans_txt('mer_suppliers_noteadded');
						my ($sth) = &Do_SQL("INSERT INTO sl_suppliers_notes SET id_suppliers='$in{'id_suppliers'}',Notes='".&filter_values($in{'notes'})."',Type='$in{'notestype'}',Date=Curdate(),Time=NOW(),ID_admin_users='$usr{'id_admin_users'}'");
						delete($in{'notes'});
						delete($in{'notestype'});
						&auth_logging('mer_suppliers_noteadded',$in{'id_suppliers'});
					}
				}
				## VRM
				my ($query);
				if ($in{'filter'}){
					$query = "AND Type='".&filter_values($in{'filter'})."' ";
				}
				my (@c) = split(/,/,$cfg{'srcolors'});
				my ($sth) = &Do_SQL("SELECT COUNT(*) FROM sl_suppliers_notes WHERE id_suppliers='$in{'id_suppliers'}' $query");
				$va{'matches'} = $sth->fetchrow;
				if ($va{'matches'}>0){
					(!$in{'nh'}) and ($in{'nh'}=1);
					$first = ($in{'nh'} - 1) * $usr{'pref_maxh'};			
					($va{'pageslist'},$qs) = &pages_list($in{'nh'},"/cgi-bin/mod/$usr{'application'}/dbman",$va{'matches'},$usr{'pref_maxh'});
					my ($sth) = &Do_SQL("SELECT * FROM sl_suppliers_notes,admin_users WHERE id_suppliers='$in{'id_suppliers'}' AND sl_suppliers_notes.ID_admin_users=admin_users.ID_admin_users $query ORDER BY ID_suppliers_notes DESC ;");
					while ($rec = $sth->fetchrow_hashref){
						$d = 1 - $d;
						$rec->{'Notes'} =~ s/\n/<br>/g;
						$va{'searchresults'} .= "<tr bgcolor='$c[$d]'>\n";
						$va{'searchresults'} .= "  <td class='smalltext'>$rec->{'Date'} $rec->{'Time'}<br>($rec->{'ID_admin_users'}) $rec->{'FirstName'} $rec->{'LastName'}</td>\n";
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
		}elsif($in{'tab'} eq '2'){
			if (!$perm{'mer_suppliers_tab2'}) { 
				$va{'pageslist'} = 1;
				$va{'searchresults'} = qq|
					<tr>
						<td colspan='6' align="center">|.&trans_txt('not_auth').qq|</td>
					</tr>\n|;
			}else{				
				## Logs
				my (@c) = split(/,/,$cfg{'srcolors'});
				my ($sth) = &Do_SQL("SELECT COUNT(*) FROM sl_supplies_suppliers WHERE id_suppliers='$in{id_suppliers}'");
				$va{'matches'} = $sth->fetchrow;
				if ($va{'matches'}>0){
					(!$in{'nh'}) and ($in{'nh'}=1);
					$first = ($in{'nh'} - 1) * $usr{'pref_maxh'};			
					($va{'pageslist'},$qs) = &pages_list($in{'nh'},"/cgi-bin/mod/$usr{'application'}/dbman",$va{'matches'},$usr{'pref_maxh'});
					my ($sth) = &Do_SQL("SELECT * FROM sl_supplies_suppliers,sl_supplies WHERE sl_supplies_suppliers.id_suppliers='$in{id_suppliers}' AND sl_supplies.ID_supplies=sl_supplies_suppliers.ID_supplies ORDER BY sl_supplies.ID_supplies DESC ;");
					while ($rec = $sth->fetchrow_hashref){
						$d = 1 - $d;
						$va{'searchresults'} .= "<tr bgcolor='$c[$d]'>\n";
						$va{'searchresults'} .= "   <td class='smalltext'><a href='$script_url?cmd=mer_supplies&view=$rec->{'ID_supplies'}'>$rec->{'ID_supplies'}</td>\n";
						$va{'searchresults'} .= "   <td class='smalltext'>$rec->{'Name'}</td>\n";						
						$va{'searchresults'} .= "   <td class='smalltext'>".&format_price($rec->{'SPrice'})."</td>\n";
						$va{'searchresults'} .= "   <td class='smalltext'>$rec->{'Status'}</td>\n";						
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
		}elsif($in{'tab'} eq '3'){
			if (!$perm{'mer_suppliers_tab3'}) { 
				$va{'pageslist'} = 1;
				$va{'searchresults'} = qq|
					<tr>
						<td colspan='6' align="center">|.&trans_txt('not_auth').qq|</td>
					</tr>\n|;
			}else{
				$va{'searchresults'} = qq|
					<tr>
						<td colspan='6' align='center'>|.&trans_txt('na').qq|</td>
					</tr>\n|;
			}
		}elsif($in{'tab'} eq '4'){
			if (!$perm{'mer_suppliers_tab4'}) { 
				$va{'pageslist'} = 1;
				$va{'searchresults'} = qq|
					<tr>
						<td colspan='6' align="center">|.&trans_txt('not_auth').qq|</td>
					</tr>\n|;
			}else{
				## Logs
				my (@c) = split(/,/,$cfg{'srcolors'});
				my ($sth) = &Do_SQL("SELECT COUNT(*) FROM sl_supplies_suppliers WHERE id_suppliers='$in{id_suppliers}'");
				$va{'matches'} = $sth->fetchrow;
				if ($va{'matches'}>0){
					$va{'searchresults'} = qq|
						<tr>
							<td colspan='6' align="center">|.&trans_txt('na').qq|</td>
						</tr>\n|;
				}else{
					$va{'pageslist'} = 1;
					$va{'searchresults'} = qq|
						<tr>
							<td colspan='6' align='center'>|.&trans_txt('search_nomatches').qq|</td>
						</tr>\n|;
				}
			}								
		}elsif($in{'tab'} eq '5'){
			if (!$perm{'mer_suppliers_tab5'}) { 
				$va{'pageslist'} = 1;
				$va{'searchresults'} = qq|
					<tr>
						<td colspan='6' align="center">|.&trans_txt('not_auth').qq|</td>
					</tr>\n|;
			}else{				
				## Logs
				my (@c) = split(/,/,$cfg{'srcolors'});
				my ($sth) = &Do_SQL("SELECT COUNT(*) FROM admin_logs WHERE tbl_name='sl_suppliers' AND Action='$in{'id_suppliers'}'");
				$va{'matches'} = $sth->fetchrow;
				if ($va{'matches'}>0){
					(!$in{'nh'}) and ($in{'nh'}=1);
					$first = ($in{'nh'} - 1) * $usr{'pref_maxh'};			
					($va{'pageslist'},$qs) = &pages_list($in{'nh'},"/cgi-bin/mod/$usr{'application'}/dbman",$va{'matches'},$usr{'pref_maxh'});
					my ($sth) = &Do_SQL("SELECT * FROM admin_logs,admin_users WHERE tbl_name='sl_suppliers' AND Action='$in{'id_suppliers'}' AND admin_logs.ID_admin_users=admin_users.ID_admin_users ORDER BY ID_logs DESC ;");
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
		return "<a name='tabs' id='tabs'>&nbsp;</a>" . &build_page('suppliers_print_tab'.$in{'tab'}.'.html') .$tab_jump;
	}
}


1;