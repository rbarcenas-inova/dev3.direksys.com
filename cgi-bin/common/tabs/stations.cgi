#!/usr/bin/perl
####################################################################
########                  Purchase Orders                   ########
####################################################################

sub load_tabsconf {

}

sub load_tabs1 {
# --------------------------------------------------------
##############################################
## tab1 : STATS
##############################################

	### Calls
	$sth = &Do_SQL("SELECT COUNT(*),
				SUM(IF(DATEDIFF(NOW(),CONCAT(ESTDay, ' ', ESTTime))<=7,1,0)) AS T7,
				SUM(IF(DATEDIFF(NOW(),CONCAT(ESTDay, ' ', ESTTime))<=30,1,0)) AS T30,
				SUM(IF(DATEDIFF(NOW(),CONCAT(ESTDay, ' ', ESTTime))<=60,1,0)) AS T60
			FROM sl_leads_calls 
			LEFT JOIN sl_mediacontracts ON sl_leads_calls.ID_mediacontracts=sl_mediacontracts.ID_mediacontracts
			WHERE Station='$in{'stationname'}'");
	($va{'cal_qty'},$va{'cal_q7'},$va{'cal_q30'},$va{'cal_q60'})=$sth->fetchrow();
	
	### Contracts
	$sth = &Do_SQL("SELECT 
						SUM(Cost) AS Tt, COUNT(*) AS tq, 
						SUM(IF(DATEDIFF(NOW(),CONCAT(ESTDay, ' ', ESTTime))<=7,Cost,0)) AS T7,
						SUM(IF(DATEDIFF(NOW(),CONCAT(ESTDay, ' ', ESTTime))<=7,1,0)) AS q7,
						SUM(IF(DATEDIFF(NOW(),CONCAT(ESTDay, ' ', ESTTime))<=30,Cost,0)) AS T30,
						SUM(IF(DATEDIFF(NOW(),CONCAT(ESTDay, ' ', ESTTime))<=30,1,0)) AS q30,
						SUM(IF(DATEDIFF(NOW(),CONCAT(ESTDay, ' ', ESTTime))<=60,Cost,0)) AS T60,
						SUM(IF(DATEDIFF(NOW(),CONCAT(ESTDay, ' ', ESTTime))<=60,1,0)) AS q60
				FROM sl_mediacontracts WHERE Station='$in{'stationname'}'");
	($va{'inv_tot'},$va{'inv_qty'},$va{'inv_t7'},$va{'inv_q7'},$va{'inv_t30'},$va{'inv_q30'},$va{'inv_t60'},$va{'inv_q60'} )=$sth->fetchrow();

	### Orders
	$sth = &Do_SQL("SELECT 
						SUM(OrderNet) AS Tt, COUNT(*) AS tq, 
						SUM(IF(DATEDIFF(NOW(),CONCAT(Date, ' ', Time))<=7,OrderNet,0)) AS T7,
						SUM(IF(DATEDIFF(NOW(),CONCAT(Date, ' ', Time))<=7,1,0)) AS q7,
						SUM(IF(DATEDIFF(NOW(),CONCAT(Date, ' ', Time))<=30,OrderNet,0)) AS T30,
						SUM(IF(DATEDIFF(NOW(),CONCAT(Date, ' ', Time))<=30,1,0)) AS q30,
						SUM(IF(DATEDIFF(NOW(),CONCAT(Date, ' ', Time))<=60,OrderNet,0)) AS T60,
						SUM(IF(DATEDIFF(NOW(),CONCAT(Date, ' ', Time))<=60,1,0)) AS q60
				FROM sl_orders WHERE ID_mediacontracts IN 
						(SELECT ID_mediacontracts FROM sl_mediacontracts WHERE Station='$in{'stationname'}')  ");
	($va{'ord_tot'},$va{'ord_qty'},$va{'ord_t7'},$va{'ord_q7'},$va{'ord_t30'},$va{'ord_q30'},$va{'ord_t60'},$va{'ord_q60'} )=$sth->fetchrow();
	#### Ratio Orders
	$va{'ror_t7'} = &round($va{'ord_t7'}/$va{'inv_t7'},2) if ($va{'inv_t7'}>0);
	$va{'ror_t30'} = &round($va{'ord_t30'}/$va{'inv_t30'},2) if ($va{'inv_t30'}>0);
	$va{'ror_t60'} = &round($va{'ord_t60'}/$va{'inv_t60'},2) if $va{'inv_t60'}>0;
	$va{'ror_tot'} = &round($va{'ord_tot'}/$va{'inv_tot'},2) if $va{'inv_tot'}>0;
	
	### Sales
	$sth = &Do_SQL("SELECT 
						SUM(OrderNet) AS Tt, COUNT(*) AS tq, 
						SUM(IF(DATEDIFF(NOW(),CONCAT(Date, ' ', Time))<=7,OrderNet,0)) AS T7,
						SUM(IF(DATEDIFF(NOW(),CONCAT(Date, ' ', Time))<=7,1,0)) AS q7,
						SUM(IF(DATEDIFF(NOW(),CONCAT(Date, ' ', Time))<=30,OrderNet,0)) AS T30,
						SUM(IF(DATEDIFF(NOW(),CONCAT(Date, ' ', Time))<=30,1,0)) AS q30,
						SUM(IF(DATEDIFF(NOW(),CONCAT(Date, ' ', Time))<=60,OrderNet,0)) AS T60,
						SUM(IF(DATEDIFF(NOW(),CONCAT(Date, ' ', Time))<=60,1,0)) AS q60
				FROM sl_orders WHERE ID_mediacontracts IN 
						(SELECT ID_mediacontracts FROM sl_mediacontracts WHERE Station='$in{'stationname'}') AND Status='Shipped' ");
	($va{'sal_tot'},$va{'sal_qty'},$va{'sal_t7'},$va{'sal_q7'},$va{'sal_t30'},$va{'sal_q30'},$va{'sal_t60'},$va{'sal_q60'} )=$sth->fetchrow();
	### Ratio Sales
	$va{'rsa_t7'} = &round($va{'sal_t7'}/$va{'inv_t7'},2) if ($va{'inv_t7'}>0);
	$va{'rsa_t30'} = &round($va{'sal_t30'}/$va{'inv_t30'},2) if ($va{'inv_t30'}>0);
	$va{'rsa_t60'} = &round($va{'sal_t60'}/$va{'inv_t60'},2) if $va{'inv_t60'}>0;
	$va{'rsa_tot'} = &round($va{'sal_tot'}/$va{'inv_tot'},2) if $va{'inv_tot'}>0;

	### % Sales vs Orders
	$va{'ros_t7'} = &round($va{'sal_t7'}/$va{'ord_t7'}*100,2) if ($va{'ord_t7'}>0);
	$va{'ros_t30'} = &round($va{'sal_t30'}/$va{'ord_t30'}*100,2) if ($va{'ord_t30'}>0);
	$va{'ros_t60'} = &round($va{'sal_t60'}/$va{'ord_t60'}*100,2)  if $va{'ord_t60'}>0;
	$va{'ros_tot'} = &round($va{'sal_tot'}/$va{'ord_tot'}*100,2) if $va{'ord_tot'}>0;
	
	foreach $key (keys %va){
		if ($key =~ /inv_t|ord_t|sal_t/){
			$va{$key} = &format_price($va{$key});
		}
	}
	&load_db_fields_values($in{'db'},'ID_mediastations',$in{'id_mediastations'},'*');
}

sub load_tabs2 {
# --------------------------------------------------------
##############################################
## tab2 : Agencies
##############################################
	$in{'stationname'} = &load_db_names('sl_mediaagencies','ID_mediaagencies',$in{'id_mediastations'},'[Name]');
	my (@c) = split(/,/,$cfg{'srcolors'});
	my ($sth) = &Do_SQL("SELECT COUNT(DISTINCT(Agency)) FROM sl_mediadids WHERE channel='$in{'stationname'}'");
	$va{'matches'} = $sth->fetchrow;
	if ($va{'matches'}>0){
		if ($in{'print'}){
			$sth = &Do_SQL("SELECT * FROM  sl_mediadids LEFT JOIN sl_mediaagencies ON Agency=Name WHERE channel='$in{'stationname'}' GROUP BY Agency;");
		}else{
			(!$in{'nh'}) and ($in{'nh'}=1);
			$first = ($in{'nh'} - 1) * $usr{'pref_maxh'};
			($va{'pageslist'},$qs) = &pages_list($in{'nh'},"/cgi-bin/mod/$usr{'application'}/dbman",$va{'matches'},$usr{'pref_maxh'});
			$sth = &Do_SQL("SELECT sl_mediaagencies.* FROM  sl_mediadids LEFT JOIN sl_mediaagencies ON Agency=Name WHERE channel='$in{'stationname'}'  GROUP BY Agency LIMIT $first,$usr{'pref_maxh'};");
		}

		while ($rec = $sth->fetchrow_hashref){
			$d = 1 - $d;
			$va{'searchresults'} .= "<tr bgcolor='$c[$d]'>\n";
			$va{'searchresults'} .= "  <td class='smalltext'><a href='/cgi-bin/mod/admin/dbman?cmd=mm_agencies&view=$rec->{'ID_mediaagencies'}'>$rec->{'ID_mediaagencies'}</a></td>\n";
			$va{'searchresults'} .= "  <td class='smalltext'>$rec->{'Name'}</td>\n";
			$va{'searchresults'} .= "  <td class='smalltext'>".&format_phone($rec->{'Phone'})."</td>\n";
			$va{'searchresults'} .= "  <td class='smalltext'>$rec->{'Contact'}</td>\n";
			$va{'searchresults'} .= "  <td class='smalltext'>$rec->{'PaymentType'}</td>\n";
			$va{'searchresults'} .= "  <td class='smalltext'>$rec->{'TimeZone'}</td>\n";
			$va{'searchresults'} .= "</tr>\n";
		}
	}else{
		$va{'pageslist'} = 1;
		$va{'searchresults'} = qq|
			<tr>
				<td colspan='6' align='center'>|.&trans_txt('search_nomatches').qq|</td>
			</tr>\n|;
	}
	## Tables Header/Titles
	#$va{'keyname'} = 'Agencies';
    #&load_db_fields_values($in{'db'},'ID_mediastations',$in{'id_mediastations'},'*');
}


sub load_tabs3{
# --------------------------------------------------------
##############################################
## tab2 : DIDs
##############################################
	my (@c) = split(/,/,$cfg{'srcolors'});
	my ($sth) = &Do_SQL("SELECT COUNT(*) FROM sl_mediadids WHERE channel='$in{'stationname'}' ");
	$va{'matches'} = $sth->fetchrow;
	if ($va{'matches'}>0){
		if ($in{'print'}){
			$sth = &Do_SQL("SELECT * FROM  sl_mediadids WHERE channel='$in{'stationname'}';");
		}else{
			(!$in{'nh'}) and ($in{'nh'}=1);
			$first = ($in{'nh'} - 1) * $usr{'pref_maxh'};
			($va{'pageslist'},$qs) = &pages_list($in{'nh'},"/cgi-bin/mod/$usr{'application'}/dbman",$va{'matches'},$usr{'pref_maxh'});
			$sth = &Do_SQL("SELECT * FROM  sl_mediadids  WHERE channel='$in{'stationname'}' LIMIT $first,$usr{'pref_maxh'};");
		}

		while ($rec = $sth->fetchrow_hashref){
			$d = 1 - $d;
			$va{'searchresults'} .= "<tr bgcolor='$c[$d]'>\n";
			$va{'searchresults'} .= "  <td class='smalltext'><a href='/cgi-bin/mod/admin/dbman?cmd=mm_dids&view=$rec->{'ID_mediadids'}'>$rec->{'didmx'}</a></td>\n";
			$va{'searchresults'} .= "  <td class='smalltext'>".&format_phone($rec->{'num800'})."</td>\n";
			$va{'searchresults'} .= "  <td class='smalltext'>$rec->{'product'}</td>\n";
			$va{'searchresults'} .= "  <td class='smalltext'>$rec->{'Promocion'}</td>\n";
			$va{'searchresults'} .= "  <td class='smalltext'>$rec->{'ISCI'}</td>\n";
			$va{'searchresults'} .= "  <td class='smalltext'>$rec->{'DMA'}</td>\n";
			$va{'searchresults'} .= "</tr>\n";
		}
	}else{
		$va{'pageslist'} = 1;
		$va{'searchresults'} = qq|
			<tr>
				<td colspan='6' align='center'>|.&trans_txt('search_nomatches').qq|</td>
			</tr>\n|;
	}
	## Tables Header/Titles
	$va{'keyname'} = 'DIDs';
	&load_db_fields_values($in{'db'},'ID_mediastations',$in{'id_mediastations'},'*');
}

sub load_tabs4{
# --------------------------------------------------------
##############################################
## tab4 : SAME DMA
##############################################
	my (@c) = split(/,/,$cfg{'srcolors'});
	my ($sth) = &Do_SQL("SELECT COUNT(*) FROM sl_mediadids WHERE DMA IN (SELECT DMA FROM sl_mediadids WHERE channel='$in{'stationname'}') ");
	$va{'matches'} = $sth->fetchrow;
	if ($va{'matches'}>0){
		if ($in{'print'}){
			$sth = &Do_SQL("SELECT * FROM sl_mediadids WHERE DMA IN (SELECT DMA FROM sl_mediadids WHERE channel='$in{'stationname'}');");
		}else{
			(!$in{'nh'}) and ($in{'nh'}=1);
			$first = ($in{'nh'} - 1) * $usr{'pref_maxh'};
			($va{'pageslist'},$qs) = &pages_list($in{'nh'},"/cgi-bin/mod/$usr{'application'}/dbman",$va{'matches'},$usr{'pref_maxh'});
			$sth = &Do_SQL("SELECT * FROM sl_mediadids WHERE DMA IN (SELECT DMA FROM sl_mediadids WHERE channel='$in{'stationname'}') LIMIT $first,$usr{'pref_maxh'};");
		}

		while ($rec = $sth->fetchrow_hashref){
			$d = 1 - $d;
			$va{'searchresults'} .= "<tr bgcolor='$c[$d]'>\n";
			$va{'searchresults'} .= "  <td class='smalltext'><a href='/cgi-bin/mod/admin/dbman?cmd=mm_dids&view=$rec->{'ID_mediadids'}'>$rec->{'didmx'}</a></td>\n";
			$va{'searchresults'} .= "  <td class='smalltext'>".&format_phone($rec->{'num800'})."</td>\n";
			$va{'searchresults'} .= "  <td class='smalltext'>$rec->{'product'}</td>\n";
			$va{'searchresults'} .= "  <td class='smalltext'>$rec->{'Promocion'}</td>\n";
			$va{'searchresults'} .= "  <td class='smalltext'>$rec->{'ISCI'}</td>\n";
			$va{'searchresults'} .= "  <td class='smalltext'>$rec->{'DMA'}</td>\n";
			$va{'searchresults'} .= "</tr>\n";
		}
	}else{
		$va{'pageslist'} = 1;
		$va{'searchresults'} = qq|SELECT COUNT(*) FROM sl_mediadids WHERE DMA='$in{'dma'}'
			<tr>
				<td colspan='6' align='center'>|.&trans_txt('search_nomatches').qq|</td>
			</tr>\n|;
	}
	## Tables Header/Titles
	$va{'keyname'} = 'SameDMA';
	&load_db_fields_values($in{'db'},'ID_mediastations',$in{'id_mediastations'},'*');
}

sub load_tabs5{
# --------------------------------------------------------
##############################################
## tab5 : Contracts
##############################################
	my (@c) = split(/,/,$cfg{'srcolors'});
	my ($sth) = &Do_SQL("SELECT COUNT(*) FROM sl_mediacontracts WHERE Station='$in{'stationname'}' ");
	$va{'matches'} = $sth->fetchrow;
	if ($va{'matches'}>0){
		if ($in{'print'}){
			$sth = &Do_SQL("SELECT * FROM  sl_mediacontracts WHERE Station='$in{'stationname'}';");
		}else{
			(!$in{'nh'}) and ($in{'nh'}=1);
			$first = ($in{'nh'} - 1) * $usr{'pref_maxh'};
			($va{'pageslist'},$qs) = &pages_list($in{'nh'},"/cgi-bin/mod/$usr{'application'}/dbman",$va{'matches'},$usr{'pref_maxh'});
			$sth = &Do_SQL("SELECT * FROM  sl_mediacontracts WHERE Station='$in{'stationname'}' ORDER BY ESTDay DESC LIMIT $first,$usr{'pref_maxh'};");
		}

		while ($rec = $sth->fetchrow_hashref){
			$d = 1 - $d;
			$va{'searchresults'} .= "<tr bgcolor='$c[$d]'>\n";
			$va{'searchresults'} .= "  <td class='smalltext'><a href='/cgi-bin/mod/admin/dbman?cmd=mm_contracts&view=$rec->{'ID_mediacontracts'}'>$rec->{'ID_mediacontracts'}</a></td>\n";
			$va{'searchresults'} .= "  <td class='smalltext'>$rec->{'Format'}</td>\n";
			$va{'searchresults'} .= "  <td class='smalltext'>$rec->{'ESTDay'}</td>\n";
			$va{'searchresults'} .= "  <td class='smalltext'>$rec->{'ESTTime'}</td>\n";
			$va{'searchresults'} .= "  <td class='smalltext'>$rec->{'Destination'}</td>\n";
			$va{'searchresults'} .= "  <td class='smalltext'>$rec->{'Offer'}</td>\n";
			$va{'searchresults'} .= "  <td class='smalltext'>".&format_price($rec->{'Cost'})."</td>\n";
			$va{'searchresults'} .= "  <td class='smalltext'>$rec->{'Status'}</td>\n";
			$va{'searchresults'} .= "</tr>\n";
		}
	}else{
		$va{'pageslist'} = 1;
		$va{'searchresults'} = qq|
			<tr>
				<td colspan='6' align='center'>|.&trans_txt('search_nomatches').qq|</td>
			</tr>\n|;
	}
	## Tables Header/Titles
	$va{'keyname'} = 'DIDs';
	&load_db_fields_values($in{'db'},'ID_mediastations',$in{'id_mediastations'},'*');
}


1;