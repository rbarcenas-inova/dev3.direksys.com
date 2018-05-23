#####################################################################
########                   DEVELOPER JOBS                    ########
#####################################################################


sub build_tabs {
# --------------------------------------------------------
	$in{'tab'} = int($in{'tab'});
	my ($tab_jump);
	if (!$in{'tab'}) {
		$in{'tab'}=1;
	}else{
		$tab_jump = "<script language='JavaScript'>\n  self.document.location.href = '#tabs';\n</script>";
	}
	if ($in{'tab'}>0 and $in{'tab'}<3){
		if ($in{'tab'} eq '1'){
			if (!$perm{'mer_manufacturers_tab1'}) { 
				$va{'pageslist'} = 1;
				$va{'searchresults'} = qq|
					<tr>
						<td colspan='3' align="center">|.&trans_txt('not_auth').qq|</td>
					</tr>\n|;
			}else{			
				## Logs
				my (@c) = split(/,/,$cfg{'srcolors'});
				my ($sth) = &Do_SQL("SELECT COUNT(*) FROM sl_products WHERE ID_manufacters='$in{'id_manufacters'}' AND Status<>'Inactive'");
				$va{'matches'} = $sth->fetchrow;
				if ($va{'matches'}>0){
					(!$in{'nh'}) and ($in{'nh'}=1);
					$first = ($in{'nh'} - 1) * $usr{'pref_maxh'};			
					($va{'pageslist'},$qs) = &pages_list($in{'nh'},"/cgi-bin/mod/$usr{'application'}/dbman",$va{'matches'},$usr{'pref_maxh'});
					my ($sth) = &Do_SQL("SELECT * FROM sl_products WHERE ID_manufacters='$in{'id_manufacters'}' AND Status<>'Inactive' ORDER BY sl_products.Name DESC LIMIT $first,$usr{'pref_maxh'};");
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
		}elsif($in{'tab'} eq '2'){
			if (!$perm{'mer_manufacturers_tab2'}) { 
				$va{'pageslist'} = 1;
				$va{'searchresults'} = qq|
					<tr>
						<td colspan='3' align="center">|.&trans_txt('not_auth').qq|</td>
					</tr>\n|;
			}else{			
				## Logs
				my (@c) = split(/,/,$cfg{'srcolors'});
				my ($sth) = &Do_SQL("SELECT COUNT(*) FROM admin_logs WHERE tbl_name='sl_manufacters' AND Action='$in{'view'}'");
				$va{'matches'} = $sth->fetchrow;
				if ($va{'matches'}>0){
					(!$in{'nh'}) and ($in{'nh'}=1);
					$first = ($in{'nh'} - 1) * $usr{'pref_maxh'};			
					($va{'pageslist'},$qs) = &pages_list($in{'nh'},"/cgi-bin/mod/$usr{'application'}/dbman",$va{'matches'},$usr{'pref_maxh'});
					my ($sth) = &Do_SQL("SELECT * FROM admin_logs,admin_users WHERE tbl_name='sl_manufacters' AND Action='$in{'view'}' AND admin_logs.ID_admin_users=admin_users.ID_admin_users ORDER BY ID_logs DESC LIMIT $first,$usr{'pref_maxh'};");
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
		return "<a name='tabs' id='tabs'>&nbsp;</a>" . &build_page('manufacturers_tab'.$in{'tab'}.'.html') .$tab_jump;
	}
}

sub print_tabs {
# --------------------------------------------------------
	$in{'tab'} = int($in{'tab'});
	my ($tab_jump);
	if (!$in{'tab'}) {
		$in{'tab'}=1;
	}else{
		$tab_jump = "<script language='JavaScript'>\n  self.document.location.href = '#tabs';\n</script>";
	}
	if ($in{'tab'}>0 and $in{'tab'}<3){
		if ($in{'tab'} eq '1'){
			if (!$perm{'mer_manufacturers_tab1'}) { 
				$va{'pageslist'} = 1;
				$va{'searchresults'} = qq|
					<tr>
						<td colspan='3' align="center">|.&trans_txt('not_auth').qq|</td>
					</tr>\n|;
			}else{			
				## Logs
				my (@c) = split(/,/,$cfg{'srcolors'});
				my ($sth) = &Do_SQL("SELECT COUNT(*) FROM sl_products WHERE ID_manufacters='$in{'id_manufacters'}' AND Status<>'Inactive'");
				$va{'matches'} = $sth->fetchrow;
				if ($va{'matches'}>0){
					(!$in{'nh'}) and ($in{'nh'}=1);
					$first = ($in{'nh'} - 1) * $usr{'pref_maxh'};			
					($va{'pageslist'},$qs) = &pages_list($in{'nh'},"/cgi-bin/mod/$usr{'application'}/dbman",$va{'matches'},$usr{'pref_maxh'});
					my ($sth) = &Do_SQL("SELECT * FROM sl_products WHERE ID_manufacters='$in{'id_manufacters'}' AND Status<>'Inactive' ORDER BY sl_products.Name DESC LIMIT $first,$usr{'pref_maxh'};");
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
		}elsif($in{'tab'} eq '2'){
			if (!$perm{'mer_manufacturers_tab2'}) { 
				$va{'pageslist'} = 1;
				$va{'searchresults'} = qq|
					<tr>
						<td colspan='3' align="center">|.&trans_txt('not_auth').qq|</td>
					</tr>\n|;
			}else{			
				## Logs
				my (@c) = split(/,/,$cfg{'srcolors'});
				my ($sth) = &Do_SQL("SELECT COUNT(*) FROM admin_logs WHERE tbl_name='sl_manufacters' AND Action='$in{'id_manufacters'}'");
				$va{'matches'} = $sth->fetchrow;
				if ($va{'matches'}>0){
					(!$in{'nh'}) and ($in{'nh'}=1);
					$first = ($in{'nh'} - 1) * $usr{'pref_maxh'};			
					($va{'pageslist'},$qs) = &pages_list($in{'nh'},"/cgi-bin/mod/$usr{'application'}/dbman",$va{'matches'},$usr{'pref_maxh'});
					my ($sth) = &Do_SQL("SELECT * FROM admin_logs,admin_users WHERE tbl_name='sl_manufacters' AND Action='$in{'id_manufacters'}' AND admin_logs.ID_admin_users=admin_users.ID_admin_users ORDER BY ID_logs DESC LIMIT $first,$usr{'pref_maxh'};");
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
		return "<a name='tabs' id='tabs'>&nbsp;</a>" . &build_page('manufacturers_print_tab'.$in{'tab'}.'.html') .$tab_jump;
	}
}

1;