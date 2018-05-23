#####################################################################
########                   Coverages               		    #########
#####################################################################
sub load_tabsconf {
# --------------------------------------------------------
	if ($in{'tab'} eq 2){
		## Notes Tab
		$va{'tab_type'}  = 'notes';
		$va{'tab_title'} = &trans_txt('notes');
		$va{'tab_table'} = 'sl_warehouses_coverages_notes';
	}elsif($in{'tab'} eq 3){
		## Notes Tab
		$va{'tab_type'}  = 'logs';
		$va{'tab_title'} = &trans_txt('logs');
		$va{'tab_table'} = 'sl_warehouses_coverages';
	}
}

#############################################################################
#############################################################################
#   Function: load_tabs1
#
#       Es: Muestra los Warehouses con la misma cobertura
#       En: Displays the same coverage Warehouses
#
#
#    Created on: 09/01/2013  11:29:10
#
#    Author: Alejandro Diaz
#
#    Modifications:
#
#        - 
#
#   Parameters:
#
#      - 
#
#  Returns:
#
#      - 
#
#   See Also:
#
#
#
sub load_tabs1 {
#############################################################################
#############################################################################		
	$va{'messages'} = "";
	
	$in{'view'} = int($in{'view'});
	my (@c)   = split(/,/,$cfg{'srcolors'});

	my ($sth_cov) = &Do_SQL("SELECT sl_warehouses_coverages.country, sl_warehouses_coverages.state, sl_warehouses_coverages.city, ID_warehouses
				FROM `sl_warehouses_coverages` 
				WHERE `ID_warehouses_coverages` = '$in{'id_warehouses_coverages'}'");
	$rec_cov = $sth_cov->fetchrow_hashref;

	my ($sth_c) = &Do_SQL("SELECT COUNT(*) FROM(
				SELECT sl_warehouses.ID_warehouses, sl_warehouses.Name, sl_warehouses.Type, COUNT(*) Recs
				FROM `sl_warehouses_coverages`
				INNER JOIN sl_warehouses USING(ID_warehouses)
				WHERE `ID_warehouses` != ".$rec_cov->{'ID_warehouses'}."
				AND sl_warehouses_coverages.country = '".$rec_cov->{'country'}."'
				AND sl_warehouses_coverages.state = '".$rec_cov->{'state'}."'
				AND sl_warehouses_coverages.city = '".$rec_cov->{'city'}."'
				AND sl_warehouses_coverages.Covered = 'Covered'
				GROUP BY ID_warehouses, Name, Type
				ORDER BY Name) as tmp");
	$va{'matches'} = $sth_c->fetchrow;
	if ($va{'matches'}>0){
		my ($sth) = &Do_SQL("SELECT sl_warehouses.ID_warehouses, sl_warehouses.Name, sl_warehouses.Type, COUNT(*) Recs
				FROM `sl_warehouses_coverages`
				INNER JOIN sl_warehouses USING(ID_warehouses)
				WHERE `ID_warehouses` != ".$rec_cov->{'ID_warehouses'}."
				AND sl_warehouses_coverages.country = '".$rec_cov->{'country'}."'
				AND sl_warehouses_coverages.state = '".$rec_cov->{'state'}."'
				AND sl_warehouses_coverages.city = '".$rec_cov->{'city'}."'
				AND sl_warehouses_coverages.Covered = 'Covered'
				GROUP BY ID_warehouses, Name, Type
				ORDER BY Name");		

		$d = 1 - $d;
		(!$in{'nh'}) and ($in{'nh'}=1);
		$first = ($in{'nh'} - 1) * $usr{'pref_maxh'};
		($va{'pageslist'}, $qs) = &pages_list($in{'nh'},$script_url,$rec_wh->{'Recs'}, $usr{'pref_maxh'});
		while($rec_wh = $sth->fetchrow_hashref) {
				$va{'searchresults'} .= "<tr bgcolor='$c[$d]' onmouseover='m_over(this)' onmouseout='m_out(this)'>\n";
				$va{'searchresults'} .= qq| <td class='smalltext' ><a href="/cgi-bin/mod/$usr{'application'}/dbman?cmd=opr_warehouses&view=$rec_wh->{'ID_warehouses'}">$rec_wh->{'ID_warehouses'}</a>| ;
				$va{'searchresults'} .= "   <td class='smalltext' >$rec_wh->{'Name'}</td>\n";
				$va{'searchresults'} .= "   <td class='smalltext' >$rec_wh->{'Type'}</td>\n";				
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