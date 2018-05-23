##################################################################
#    OPERATIONS : ORDERS   	#
##################################################################

sub opq_products {
# --------------------------------------------------------
# Created :  Carlos Haas 01/01/2007 6:47:28 PM
# Last Update : 
# Locked by : 
# Description :
#
#
	my ($sth) = &Do_SQL("SELECT COUNT(*) FROM sl_products WHERE Status='Testing';");
	$va{'matches'} = $sth->fetchrow();
	my (@c) = split(/,/,$cfg{'srcolors'});
	if ($va{'matches'}>0){
		$id_products = substr($in{'id_sku_products'},3,6);
		(!$in{'nh'}) and ($in{'nh'}=1);
		$first = ($in{'nh'} - 1) * $usr{'pref_maxh'};			
		($va{'pageslist'},$qs) = &pages_list($in{'nh'},"/cgi-bin/mod/$usr{'application'}/admin",$va{'matches'},$usr{'pref_maxh'});
		
		my ($sth) = &Do_SQL("SELECT * FROM sl_products WHERE Status='testing' ORDER BY Date ASC LIMIT $first,$usr{'pref_maxh'};");
		while ($rec = $sth->fetchrow_hashref){
			$d = 1 - $d;
			$va{'searchresults'} .= qq|
			<tr bgcolor='$c[$d]' onmouseover='m_over(this)' onmouseout='m_out(this)' onclick="trjump('/cgi-bin/mod/admin/admin?cmd=opq_products_view&view=$rec->{'ID_products'}&tab=6#tabs')">
				<td class="smalltext" nowrap valign="top">|. &format_sltvid($rec->{'ID_products'}) . qq|</td>
				<td class="smalltext">$rec->{'Model'}<br>$rec->{'Name'}</td>
				<td class="smalltext" nowrap valign="top">|. &format_price($rec->{'SPrice'}) . qq|</td>
				<td class="smalltext" nowrap valign="top">$rec->{'Date'}</td>
			</tr>\n|;
		}
	}else{
		$va{'pageslist'} = 1;
		$va{'searchresults'} = qq|
			<tr>
				<td colspan='5' align="center">|.&trans_txt('search_nomatches').qq|</td>
			</tr>\n|;
	}
	print "Content-type: text/html\n\n";
	print &build_page('opq_products_list.html');
}

sub opq_products_view {
# --------------------------------------------------------
# Created :  Carlos Haas 01/01/2007 6:47:28 PM
# Last Update : 
# Locked by : 
# Description :
#
#
# Last Modified on: 10/28/08 10:05:47
# Last Modified by: MCC C. Gabriel Varela S: Se corrige error que producía cgierrors, se cambia returns por return
	require "dbman.html.cgi";
	$in{'db'} = 'sl_products';
	&load_cfg('sl_products');
	my (%rec) = &get_record($db_cols[0],$in{'view'},$in{'db'}) if ($in{'view'}ne'' and $in{'view'}!=0);
	if (!$rec{'id_products'}){
		&opq_products;
		return;
	}
	foreach $key (sort keys %rec) {
		$in{lc($key)} = $rec{$key};
		($db_valid_types{lc($key)} ne 'html') and ($in{lc($key)} =~ s/\n/<br>/g);
	}	
	&view_mer_products;
	&get_db_extrainfo('admin_users',$in{'id_admin_users'});
	
	print "Content-type: text/html\n\n";
	print &build_page('opq_products_view.html');
}



1;

