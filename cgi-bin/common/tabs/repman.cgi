#!/usr/bin/perl
#####################################################################
########                   APARTS	        		           		#########
#####################################################################
sub load_tabsconf {
# --------------------------------------------------------
	if ($in{'tab'} eq 2){
		## Notes Tab
		$va{'tab_type'}  = 'logs';
		$va{'tab_title'} = &trans_txt('logs');
		$va{'tab_table'} = 'sl_aragencies';
	}
}

sub load_tabs1 {
# --------------------------------------------------------
##############################################
## tab1 : FIELDS
##############################################
	
	## ITEMS LIST
	my (@c) = split(/,/,$cfg{'srcolors'});
	my ($name,$stlink);
	my ($sth) = &Do_SQL("SELECT COUNT(*) FROM admin_reports_fields WHERE ID_admin_reports='$in{'id_admin_reports'}'");
	$va{'matches'} = $sth->fetchrow;
	if ($va{'matches'}>0){
		if ($in{'print'}){
			$sth = &Do_SQL("SELECT * FROM admin_reports_fields WHERE ID_admin_reports='$in{'id_admin_reports'}' ORDER BY ListOrder ASC ");
		}else{
			(!$in{'nh'}) and ($in{'nh'}=1);
			$first = ($in{'nh'} - 1) * $usr{'pref_maxh'};			
			($va{'pageslist'},$qs) = &pages_list($in{'nh'},"/cgi-bin/mod/$usr{'application'}/dbman",$va{'matches'},$usr{'pref_maxh'});
			$sth = &Do_SQL("SELECT * FROM admin_reports_fields WHERE ID_admin_reports='$in{'id_admin_reports'}' ORDER BY ListOrder ASC LIMIT $first,$usr{'pref_maxh'};");			
		}
	
		
		while ($rec = $sth->fetchrow_hashref){
			$d = 1 - $d;
			$va{'searchresults'} .= "<tr bgcolor='$c[$d]'>\n";
			$va{'searchresults'} .= "  <td class='smalltext'><a href='/cgi-bin/mod/$usr{'application'}/dbman?cmd=repman&view=".$in{'id_admin_reports'}."&drop=".$rec->{'ID_admin_reports_fields'}."&tab=1#tabs'><img src='$va{'imgurl'}/$usr{'pref_style'}/b_drop.png' title='Drop' alt='' border='0'></a>\n";
			$va{'searchresults'} .= "  $rec->{'PrintName'}</td>\n";
			$va{'searchresults'} .= "  <td class='smalltext'' valign='top'>$rec->{'Field'}</td>\n";
			$va{'searchresults'} .= "  <td class='smalltext'' valign='top'>$rec->{'FieldType'}</td>\n";
			$va{'searchresults'} .= "  <td class='smalltext'' valign='top'>$rec->{'Filter'}</td>\n";
			$va{'searchresults'} .= "  <td class='smalltext'' valign='top'>$rec->{'FormatType'}</td>\n";
			$va{'searchresults'} .= "  <td class='smalltext'' valign='top'>$rec->{'Visibility'}</td>\n";
			$va{'searchresults'} .= "  <td class='smalltext'' valign='top'>$rec->{'ListOrder'}";
			$va{'searchresults'} .= " <a href='/cgi-bin/mod/$usr{'application'}/dbman?cmd=repman&view=".$in{'id_admin_reports'}."&order_up=".$rec->{'ID_admin_reports_fields'}."&tab=1&[va_rndnumber]#tabs'><img src='$va{'imgurl'}/$usr{'pref_style'}/arr.up.gif' title='Up' alt='' border='0'></a>\n";
			$va{'searchresults'} .= " <a href='/cgi-bin/mod/$usr{'application'}/dbman?cmd=repman&view=".$in{'id_admin_reports'}."&order_down=".$rec->{'ID_admin_reports_fields'}."&tab=1&[va_rndnumber]#tabs'><img src='$va{'imgurl'}/$usr{'pref_style'}/arr.down.gif' title='Down' alt='' border='0'></a>\n";
			
			$va{'searchresults'} .= " </td>\n";
			$va{'searchresults'} .= "</tr>\n";
		}	
	}else{
		$va{'pageslist'} = 1;
		$va{'searchresults'} = qq|
			<tr>
				<td colspan='6' align="center">|.&trans_txt('search_nomatches').qq|</td>
			</tr>\n|;
	}

}

1;