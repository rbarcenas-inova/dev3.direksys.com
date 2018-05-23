#####################################################################
########                   Zones               		    #########
#####################################################################
sub load_tabsconf {
# --------------------------------------------------------
	if ($in{'tab'} eq 2){
		## Notes Tab
		$va{'tab_type'}  = 'logs';
		$va{'tab_title'} = &trans_txt('logs');
		$va{'tab_table'} = 'sl_zones';
	}
}


#############################################################################
#############################################################################
#   Function: load_tabs1
#
#       Es: Muestra listado de los choferes asociados a esta zona
#       En: English description if possible
#
#
#    Created on: 26/10/2012  13:20:10
#
#    Author: Carlos Haas
#
#    Modifications:
#
#        - Modified on *01/11/2012* by _Enrique Peña_ : Se agrego el formulario para procesar batch de zipCodes
#
#   Parameters:
#
#  Returns:
#
#   See Also:
#
#
#
sub load_tabs1 {
#############################################################################
#############################################################################
	$va{'messages'} = "";

	my (@c)   = split(/,/,$cfg{'srcolors'});
	my ($sth) = &Do_SQL("SELECT COUNT(*) FROM admin_notifs_actions WHERE ID_admin_notifs = $in{'id_admin_notifs'}");
	$va{'matches'} = $sth->fetchrow;
	if ($va{'matches'}>0){
		my ($sth) = &Do_SQL("SELECT * FROM admin_notifs_actions
					WHERE ID_admin_notifs = $in{'id_admin_notifs'} ");					
		while ($rec = $sth->fetchrow_hashref){
			$va{'searchresults'} .= "<tr bgcolor='$c[$d]' onmouseover='m_over(this)' onmouseout='m_out(this)'>\n";
			$va{'searchresults'} .= " <td class='smalltext'><a href='/cgi-bin/mod/$usr{'application'}/dbman?cmd=notifs&tab=1&view=$in{'id_admin_notifs'}&drop=$rec->{'ID_admin_notifs_actions'}'><img src='$va{'imgurl'}/$usr{'pref_style'}/b_drop.png' title='Drop' alt='' border='0'></a></td>\n";
			$va{'searchresults'} .= " <td class='smalltext' >$rec->{'Type'} </td>\n";
			$va{'searchresults'} .= " <td class='smalltext' >$rec->{'From'} </td>\n";
			$va{'searchresults'} .= " <td class='smalltext' >$rec->{'Destination'} </td>\n";
			$va{'searchresults'} .= "</tr>\n";
		 }
		
	}else{
		$va{'searchresults'} = qq|
			<tr>
				<td colspan='4' align="center">|.&trans_txt('search_nomatches').qq|</td>
			</tr>\n|;
	}

}



1;