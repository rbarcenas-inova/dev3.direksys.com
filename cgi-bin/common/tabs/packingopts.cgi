#####################################################################
########                   DEVELOPER JOBS                    ########
#####################################################################

sub load_tabsconf {
# --------------------------------------------------------

	if($in{'tab'} eq 2){
		## Notes Tab
		$va{'tab_type'}  = 'logs';
		$va{'tab_title'} = &trans_txt('logs');
		$va{'tab_table'} = 'sl_packingopts';
	}
	
}

sub load_tabs1{
				my (@c) = split(/,/,$cfg{'srcolors'});
				my ($sth) = &Do_SQL("SELECT COUNT(*) FROM sl_products WHERE ID_packingopts = '$in{'ID_packingopts'}' AND sl_products.Status<>'Inactive'");
				$va{'matches'} = $sth->fetchrow;
				if ($va{'matches'}>0){
					(!$in{'nh'}) and ($in{'nh'}=1);
					$first = ($in{'nh'} - 1) * $usr{'pref_maxh'};			
					($va{'pageslist'},$qs) = &pages_list($in{'nh'},"/cgi-bin/mod/$usr{'application'}/dbman",$va{'matches'},$usr{'pref_maxh'});
					my ($sth) = &Do_SQL("SELECT * FROM sl_products WHERE ID_packingopts = '$in{'ID_packingopts'}' AND sl_products.Status<>'Inactive' ORDER BY sl_products.Name DESC LIMIT $first,$usr{'pref_maxh'};");
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


1;