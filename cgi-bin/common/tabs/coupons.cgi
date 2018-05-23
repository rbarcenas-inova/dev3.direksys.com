####################################################################
########                   DEVELOPER JOBS                   ########
####################################################################
sub load_tabsconf {
# --------------------------------------------------------
	if($in{'tab'} eq 4){
		## Notes Tab
		$va{'tab_type'}  = 'logs';
		$va{'tab_title'} = &trans_txt('logs');
		$va{'tab_table'} = 'sl_coupons';
	}
}

sub load_tabs1{
				if ($in{'action'}){
					if (!$in{'id_categories'}){
						$error{'id_categories'} = &trans_txt('required');
						$va{'tabmessages'} = &trans_txt('reqfields');
					}else{
						my ($sth) = &Do_SQL("SELECT COUNT(*) FROM sl_coupons_inccat WHERE id_categories='$in{'id_categories'}' $query");
						$va{'matches'} = $sth->fetchrow;
						if($va{'matches'}>0){
							$error{'id_categories'} = &trans_txt('repeated');
							$va{'messages'} = &trans_txt('repeated');
						}
						else {
							my ($sth) = &Do_SQL("INSERT INTO sl_coupons_inccat SET ID_coupons='$in{'id_coupons'}',ID_categories='$in{'id_categories'}',Date=Curdate(),Time=NOW(),ID_admin_users='$usr{'id_admin_users'}'");
							delete($in{'id_categories'});
							&auth_logging('mkt_coupons_incatadded',$in{'id_coupons'});
							$va{'tabmessages'} = &trans_txt('mkt_coupons_incatadded');
						}
					}
				}elsif ($in{'drop'}){
					my ($sth) = &Do_SQL("DELETE FROM sl_coupons_inccat WHERE ID_coupons_inccat='$in{'drop'}'");
					$va{'tabmessages'} = &trans_txt('mkt_coupons_incatdel');
					&auth_logging('mkt_coupons_incatdel',$in{'id_coupons'});
				}
				## VRM
				my ($query);
				if ($in{'filter'}){
					$query = "AND Type='".&filter_values($in{'filter'})."' ";
				}
				my (@c) = split(/,/,$cfg{'srcolors'});
				my ($sth) = &Do_SQL("SELECT COUNT(*) FROM sl_coupons_inccat WHERE id_coupons='$in{'id_coupons'}' $query");
				$va{'matches'} = $sth->fetchrow;
				if ($va{'matches'}>0){
					(!$in{'nh'}) and ($in{'nh'}=1);
					$first = ($in{'nh'} - 1) * $usr{'pref_maxh'};			
					($va{'pageslist'},$qs) = &pages_list($in{'nh'},"/cgi-bin/mod/$usr{'application'}/dbman",$va{'matches'},$usr{'pref_maxh'});
					my ($sth) = &Do_SQL("SELECT sl_coupons_inccat.ID_categories,sl_coupons_inccat.Date,sl_coupons_inccat.ID_coupons_inccat,admin_users.FirstName,admin_users.LastName,sl_coupons_inccat.Time,sl_coupons_inccat.ID_admin_users,sl_categories.Title FROM sl_coupons_inccat,sl_categories,admin_users WHERE id_coupons='$in{'id_coupons'}' AND sl_coupons_inccat.ID_admin_users=admin_users.ID_admin_users AND sl_categories.ID_categories=sl_coupons_inccat.ID_categories $query ORDER BY id_coupons_inccat DESC LIMIT $first,$usr{'pref_maxh'};");
					while ($rec = $sth->fetchrow_hashref){
						$d = 1 - $d;
						$rec->{'Notes'} =~ s/\n/<br>/g;
						$va{'searchresults'} .= "<tr bgcolor='$c[$d]'>\n";
						$va{'searchresults'} .= "  <td class='smalltext'><a href='$script_url?cmd=mkt_coupons&view=$in{'id_coupons'}&tab=1&drop=$rec->{'ID_coupons_inccat'}'><img src='$va{'imgurl'}/$usr{'pref_style'}/b_drop.png' title='Drop' alt='' border='0'></a></td>\n";
						$va{'searchresults'} .= "  <td class='smalltext'>$rec->{'Date'} $rec->{'Time'}<br>($rec->{'ID_admin_users'}) $rec->{'FirstName'} $rec->{'LastName'}</td>\n";
						$va{'searchresults'} .= "  <td class='smalltext'>($rec->{'ID_categories'}) $rec->{'Title'}</td>\n";
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

sub load_tabs2{
if ($in{'action'}){
					if (!$in{'id_categories'}){
						$error{'id_categories'} = &trans_txt('required');
						$va{'tabmessages'} = &trans_txt('reqfields');
					}else{
						my ($sth) = &Do_SQL("SELECT COUNT(*) FROM sl_coupons_exccat WHERE id_categories='$in{'id_categories'}' $query");
						$va{'matches'} = $sth->fetchrow;
						if($va{'matches'}>0){
							$error{'id_categories'} = &trans_txt('repeated');
							$va{'messages'} = &trans_txt('repeated');
						}
						else {					
							$va{'tabmessages'} = &trans_txt('mkt_coupons_excatadded');
							my ($sth) = &Do_SQL("INSERT INTO sl_coupons_exccat SET ID_coupons='$in{'id_coupons'}',ID_categories='$in{'id_categories'}',Date=Curdate(),Time=NOW(),ID_admin_users='$usr{'id_admin_users'}'");
							delete($in{'id_categories'});
							&auth_logging('mkt_coupons_excatadded',$in{'id_coupons'});
						}
					}
				}elsif ($in{'drop'}){
					my ($sth) = &Do_SQL("DELETE FROM sl_coupons_exccat WHERE ID_coupons_exccat='$in{'drop'}'");
					$va{'tabmessages'} = &trans_txt('mkt_coupons_excatdel');
					&auth_logging('mkt_coupons_excatdel',$in{'id_coupons'});
				}
				## VRM
				my ($query);
				if ($in{'filter'}){
					$query = "AND Type='".&filter_values($in{'filter'})."' ";
				}			
				## Included Categories
				my (@c) = split(/,/,$cfg{'srcolors'});
				my ($sth) = &Do_SQL("SELECT COUNT(*) FROM sl_coupons_exccat WHERE id_coupons='$in{'id_coupons'}' $query");
				$va{'matches'} = $sth->fetchrow;
				if ($va{'matches'}>0){
					(!$in{'nh'}) and ($in{'nh'}=1);
					$first = ($in{'nh'} - 1) * $usr{'pref_maxh'};
					($va{'pageslist'},$qs) = &pages_list($in{'nh'},"/cgi-bin/mod/$usr{'application'}/dbman",$va{'matches'},$usr{'pref_maxh'});					
					my ($sth) = &Do_SQL("SELECT sl_coupons_exccat.ID_categories,sl_coupons_exccat.Date,sl_coupons_exccat.ID_coupons_exccat,admin_users.FirstName,admin_users.LastName,sl_coupons_exccat.Time,sl_coupons_exccat.ID_admin_users,sl_categories.Title FROM sl_coupons_exccat,sl_categories,admin_users WHERE id_coupons='$in{'id_coupons'}' AND sl_coupons_exccat.ID_admin_users=admin_users.ID_admin_users AND sl_categories.ID_categories=sl_coupons_exccat.ID_categories $query ORDER BY id_coupons_exccat DESC LIMIT $first,$usr{'pref_maxh'};");
					while ($rec = $sth->fetchrow_hashref){
						$d = 1 - $d;
						$rec->{'Notes'} =~ s/\n/<br>/g;
						$va{'searchresults'} .= "<tr bgcolor='$c[$d]'>\n";
						$va{'searchresults'} .= "  <td class='smalltext'><a href='$script_url?cmd=mkt_coupons&view=$in{'id_coupons'}&tab=2&drop=$rec->{'ID_coupons_exccat'}'><img src='$va{'imgurl'}/$usr{'pref_style'}/b_drop.png' title='Drop' alt='' border='0'></a></td>\n";
						$va{'searchresults'} .= "  <td class='smalltext'>$rec->{'Date'} $rec->{'Time'}<br>($rec->{'ID_admin_users'}) $rec->{'FirstName'} $rec->{'LastName'}</td>\n";
						$va{'searchresults'} .= "  <td class='smalltext'>($rec->{'ID_categories'}) $rec->{'Title'}</td>\n";
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

sub load_tabs3{
	## Excluded Categories
				my (@c) = split(/,/,$cfg{'srcolors'});
				my ($sth) = &Do_SQL("SELECT COUNT(*) FROM sl_coupons_trans WHERE id_coupons='$in{'id_coupons'}' $query");
				$va{'matches'} = $sth->fetchrow;
				if ($va{'matches'}>0){
					(!$in{'nh'}) and ($in{'nh'}=1);
					$first = ($in{'nh'} - 1) * $usr{'pref_maxh'};			
					($va{'pageslist'},$qs) = &pages_list($in{'nh'},"/cgi-bin/mod/$usr{'application'}/dbman",$va{'matches'},$usr{'pref_maxh'});
					my ($sth) = &Do_SQL("SELECT * FROM sl_coupons_trans,admin_users WHERE id_coupons='$in{'id_coupons'}' AND sl_coupons_trans.ID_admin_users=admin_users.ID_admin_users $query LIMIT $first,$usr{'pref_maxh'};");
					while ($rec = $sth->fetchrow_hashref){
						$d = 1 - $d;
						$rec->{'Notes'} =~ s/\n/<br>/g;
						$va{'searchresults'} .= "<tr bgcolor='$c[$d]'>\n";
						$va{'searchresults'} .= "   <td class='smalltext'>$rec->{'ID_coupons_trans'}</td>\n";					
						$va{'searchresults'} .= "   <td class='smalltext'>($rec->{'ID_customers'}) $rec->{'FirstName'} $rec->{'LastName'}</td>\n";
						$va{'searchresults'} .= "   <td class='smalltext'>$rec->{'State'}</td>\n";
						$va{'searchresults'} .= "   <td class='smalltext'>$rec->{'Zip'}</td>\n";				
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

1;
