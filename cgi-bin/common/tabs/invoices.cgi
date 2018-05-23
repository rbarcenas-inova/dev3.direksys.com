#!/usr/bin/perl
####################################################################
########                  INVOICES                          ########
####################################################################
sub load_tabsconf {
# --------------------------------------------------------
	if ($in{'tab'} eq 2){
		## Notes Tab
		$va{'tab_type'}  = 'notes';
		$va{'tab_title'} = &trans_txt('notes');
		$va{'tab_table'} = 'cu_invoices_notes';
	}elsif($in{'tab'} eq 3){
		## Notes Tab
		$va{'tab_type'}  = 'logs';
		$va{'tab_title'} = &trans_txt('logs');
		$va{'tab_table'} = 'cu_invoices';
	}
}

#############################################################################
#############################################################################
#   Function: load_tabs1
#
#       Es: Muestra los Invoices relacionados.
#
#
#    Created on: 30/01/2013 18:00:00
#
#    Author: Enrique Peña
#
#    Modifications:
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
	my (@c) = split(/,/,$cfg{'srcolors'});
	my ($sth) = &Do_SQL("SELECT COUNT(*) FROM cu_invoices WHERE related_ID_invoices = $in{'id_invoices'}");
	$va{'matches'} = $sth->fetchrow;
	if ($va{'matches'}>0){
		(!$in{'nh'}) and ($in{'nh'}=1);
		$first = ($in{'nh'} - 1) * $usr{'pref_maxh'};			
		($va{'pageslist'},$qs) = &pages_list($in{'nh'},"/cgi-bin/mod/$usr{'application'}/dbman",$va{'matches'},$usr{'pref_maxh'});
		$sth = &Do_SQL("SELECT cu_invoices.ID_invoices,cu_invoices.ID_customers,ID_orders,CONCAT('(',cu_invoices.customer_fcode,') ',cu_invoices.customer_fname) AS NAME, cu_invoices.Status,DATE(cu_invoices.doc_date)doc_date
				FROM cu_invoices
				INNER JOIN cu_invoices_lines ON cu_invoices.ID_invoices=cu_invoices_lines.ID_invoices
				WHERE cu_invoices.related_ID_invoices = $in{'id_invoices'}
				ORDER BY cu_invoices.ID_invoices DESC LIMIT $first,$usr{'pref_maxh'};");
		while ($rec = $sth->fetchrow_hashref){
			$d = 1 - $d;
			$va{'searchresults'} .= "<tr bgcolor='$c[$d]'>\n";
			$va{'searchresults'} .= "   <td class='smalltext'><a href=\"/cgi-bin/mod/$usr{'application'}/dbman?cmd=opr_invoices&view=$rec->{'ID_invoices'}\">$rec->{'ID_invoices'}</a></td>\n";
			$va{'searchresults'} .= "   <td class='smalltext'><a href=\"/cgi-bin/mod/$usr{'application'}/dbman?cmd=opr_orders&view=$rec->{'ID_orders'}\">$rec->{'ID_orders'}</a></td>\n";
			$va{'searchresults'} .= "   <td class='smalltext'><a href=\"/cgi-bin/mod/$usr{'application'}/dbman?cmd=opr_customers&view=$rec->{'ID_customers'}\">($rec->{'ID_customers'}) $rec->{'NAME'}</a></td>\n";			
			$va{'searchresults'} .= "   <td class='smalltext'>$rec->{'Status'}</td>\n";
			$va{'searchresults'} .= "   <td class='smalltext'>$rec->{'doc_date'}</td>\n";
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