#!/usr/bin/perl

sub build_homepage {
# --------------------------------------------------------
	my ($page,@list);
	if ($vkey{'custom_name'}){
		my ($fname) = $cfg{'path_templates'};
		$fname =~ s/\[lang\]/$usr{'pref_language'}/gi;		
		if (-e "$fname/custpages/$vkey{'custom_name'}/home_top.html"){
			$page = &build_page("/custpages/$vkey{'custom_name'}/home_top.html");
		}
	}
	

	if (!$usr{'pref_wpage'}){
		return $page . &build_page('widgets/home.html');
	}else{
		@list = split(/\|/, $usr{'pref_wpage'});
		return $page;
	}
}


sub wpage_news {
# --------------------------------------------------------
# Last Modified RB: 03/25/09  17:54:22 -- Se discriminarios mensajes de acuerdo a la aplicacion

	my ($page,$d);
	my($tech,$ext) = split(/\//,$usr{'extension'});
	#&cgierr("$va{'script_url'}");
	my @ary = split(/\//,$va{'script_url'});
	my ($sth) = &Do_SQL("SELECT COUNT(*) FROM sl_devnews WHERE Date>=DATE_SUB(CURDATE(),INTERVAL 15 DAY) AND Status='Active' AND application = '$ary[2]'  ORDER BY ID_devnews DESC LIMIT 0,10;");
	if ($sth->fetchrow>0){
		my (@c) = split(/,/,$cfg{'srcolors'});
		my ($sth) = &Do_SQL("SELECT * FROM sl_devnews WHERE Date>=DATE_SUB(CURDATE(),INTERVAL 15 DAY) AND Status='Active' AND application = '$ary[2]' ORDER BY ID_devnews DESC LIMIT 0,10;");
		while ($rec = $sth->fetchrow_hashref()){
			$d = 1 - $d;
			$rec->{'Description'} =~ s/\n/<br>/g;
			$page .= qq|
				<tr onmouseover='m_over(this)' onmouseout='m_out(this)' bgcolor='$c[$d]'>
					<td class='smalltext'>$rec->{'Type'}</td>
					<td class='smalltext'>$rec->{'application'}</td>
					<td class='smalltext'><b>$rec->{'Title'}</b><br>$rec->{'Description'}<br><br></td>
				</tr>\n|;
		}
		if (!$page){
			$page = "<tr><td colspan='3' align='center'>".&trans_txt('news_nomsgs')."</td></tr>";
		}
	}else{
		$page = "<tr><td colspan='3' align='center'>".&trans_txt('news_nomsgs')."</td></tr>";
	}

	return $page;

}

sub build_developerlist {
# --------------------------------------------------------
	my ($output,$ext);
	my ($sth) = &Do_SQL("SELECT ID_admin_users,FirstName,LastName FROM admin_users WHERE usergroup=1 AND Status='Active' GROUP BY LastName, FirstName ORDER BY LastName");
	while ($rec = $sth->fetchrow_hashref){
		($rec->{'extension'}) ? ($ext = "($rec->{'extension'})"):
							($ext = "");
		$output .= "<option value='$rec->{'ID_admin_users'}'>$rec->{'LastName'}, $rec->{'FirstName'} $ext</option>\n";
	}
	(!$output) and ($output .= "<option value='---'>".&trans_txt('none')."</option>\n");
	return $output;
}

sub build_userlist {
# --------------------------------------------------------
	my ($output,$ext);
	my ($sth) = &Do_SQL("SELECT * FROM admin_users WHERE application='admin' AND Status='Active' ORDER BY LastName");
	while ($rec = $sth->fetchrow_hashref){
		($rec->{'extension'}) ? ($ext = "($rec->{'extension'})"):
							($ext = "");
		$output .= "<option value='$rec->{'ID_admin_users'}'>$rec->{'LastName'}, $rec->{'FirstName'} $ext</option>\n";
	}
	(!$output) and ($output .= "<option value='---'>".&trans_txt('none')."</option>\n");
	return $output;
}


sub build_compleuserlist {
# --------------------------------------------------------
	my ($output,$ext);
	my ($sth) = &Do_SQL("SELECT * FROM admin_users ORDER BY LastName");
	while ($rec = $sth->fetchrow_hashref){
		($rec->{'extension'}) ? ($ext = "($rec->{'extension'})"): ($ext = "");
		if ($rec->{'Status'} eq 'Active'){
			$output .= "<option value='$rec->{'ID_admin_users'}'>($rec->{'ID_admin_users'}) $rec->{'LastName'}, $rec->{'FirstName'} $ext</option>\n";
		}else{
			$output .= "<option value='$rec->{'ID_admin_users'}' style='Color:Grey'>($rec->{'ID_admin_users'}) $rec->{'LastName'}, $rec->{'FirstName'} $ext</option>\n";
		}
	}
	(!$output) and ($output .= "<option value='---'>".&trans_txt('none')."</option>\n");
	return $output;
}


sub header_menucompanies {
# --------------------------------------------------------
# Last Modified RB: 04/28/09  11:58:50

	my ($output,%tmp);
	### Load Other Sessions
	$cfg{'max_e'} = 1 if (!$cfg{'max_e'});
	for my $i(1..$cfg{'max_e'}){
		if ($cfg{'gensessiontype'} eq 'mysql'){
			if ($cfg{'app_e'.$i} and GetCookies('app_e'.$i)){
				$output .= qq|<a href='/cgi-bin/mod/$usr{'application'}/admin?cmd=changee&e=$i' class=menu><img src=$va{'imgurl'}app_bar/mod/ico-e$i.png border=0> &nbsp; $cfg{'app_e'.$i}</a>| if ($i ne $in{'e'});
			}
		}else{
			if ($cfg{'app_e'.$i} and -e "$cfg{'genauth_dir'}e$i/$sid"){
				$output .= qq|<a href='/cgi-bin/mod/$usr{'application'}/admin?cmd=changee&e=$i' class=menu><img src=$va{'imgurl'}app_bar/mod/ico-e$i.png border=0> &nbsp; $cfg{'app_e'.$i}</a>| if ($i ne $in{'e'});
			}elsif($cfg{'app_e'.$i}){
				#$output .= qq|<a href='/cgi-bin/mod/$usr{'application'}/admin?cmd=changee&e=$i' class=menu><img src=$va{'imgurl'}app_bar/mod/ico-e$i.png border=0> &nbsp; $cfg{'app_e'.$i}</a>| if ($i ne $in{'e'});
			}
		}
	}
	return $output;
}


sub header_menumod {
# --------------------------------------------------------
	my ($output);
	my (@ary) = split(/\|/, $usr{'multiapp'});
	for (0..$#ary){
		if ($ary[$_] eq 'custom'){
			$output .= " <a href='/cgi-bin/mod/$usr{'application'}/admin?cmd=changemod&to=".$ary[$_]."' class=menu>$cfg{'app_title'}</a>\n" if ($ary[$_] ne $usr{'application'});
		}else{
			$output .= " <a href='/cgi-bin/mod/$usr{'application'}/admin?cmd=changemod&to=".$ary[$_]."' class=menu>".&trans_txt('appname_'.$ary[$_])."</a>\n" if ($ary[$_] ne $usr{'application'});
		}
	}
	return $output;
}

sub permission {
# --------------------------------------------------------
	if ($in{'appperm'}){
		return &build_page("perm/$in{'appperm'}.html");
	}else{
		return &build_page('perm/general.html') . &build_page('perm/applications.html');
	}
}


sub new_messages {
# --------------------------------------------------------
# Last Modified RB: 03/06/09  18:09:15 -- Added Lists for user message
#Last modified on 16 Dec 2010 15:25:21
#Last modified by: MCC C. Gabriel Varela S. : Toma en cuenta el tamaño de la clave para mostrar mensaje de cambio de contraseña
#Last modified on 17 Dec 2010 13:17:37
#Last modified by: MCC C. Gabriel Varela S. :Se cambia para tomar en cuenta $usr{'change_pass'}
#Last modified by: _RB_ :Se inactiva funcion por obsoleta

	my ($output);
	return;


	if ($usr{'pref_newmsg'} eq 'yes' and $usr{'egw_uid'}>0){
		my ($sth) = &Do_SQL("SELECT COUNT(*) FROM phpgw_messenger_messages WHERE message_owner='$usr{'egw_uid'}' AND message_status='N';");
		$va{'msgcount'}  = $sth->fetchrow;
		if ($va{'msgcount'} >0) {
			$output = &build_page('mods/newmsgs.html');
		}
	}
	
	### Lists for the user?
	my ($sth) = &Do_SQL("SELECT COUNT(*) FROM sl_lists WHERE ID_users = $usr{'id_admin_users'} AND Status= 'Active' ");
	$output .= "<br><span class='newmessage'>".&trans_txt('havelist')."</span>" if $sth->fetchrow > 0;
	
	return $output;
}

sub select_language {
# --------------------------------------------------------
	my ($output);
	my (@list) = split(/,/, $cfg{'langs'});
	$output = "<select name='pref_language' onFocus='focusOn( this )' onBlur='focusOff( this )'><option value=''>---</option>";
	for my $i(0..$#list/2) {
		$output .= "<option value='".$list[$i*2+1]."'>".$list[$i*2]."</option>\n";
	}
	$output .= "</select>";
	return $output;
}



sub select_apps {
# --------------------------------------------------------
	my ($output);
	my (@list) = split(/,/, $cfg{'applications'});
	APPS:for my $i(0..$#list/3) {
		($list[$i*3+2] =~ /\/egw\//) and (next APPS);
		$output .= "<span style='white-space:nowrap'><input type='checkbox' name='pref_applications' value='$list[$i*3]' class='checkbox'>".$list[$i*3]."</span>\n ";
	}
	return $output."APPLICATIONS";
}



sub build_ccusertype {
# --------------------------------------------------------
	my ($output);
	my ($sth) = &Do_SQL("DESCRIBE admin_users app");
	my (@ary) = $sth->fetchrow_array();
	$ary[1] = substr($ary[1],6,-2);
	$ary[1] =~ s/','/,/g;
	@ary = split(/,/, $ary[1]);
	for (0..$#ary){
		if ($ary[$_] =~ /^cc-/){
			$output .= "<option value='$ary[$_]'>".&trans_txt('usertype_'.$ary[$_])."</option>\n";
		}
	}
	(!$output) and ($output .= "<option value='---'>".&trans_txt('none')."</option>\n");
	return $output;
}

sub build_sausertype {
# --------------------------------------------------------
	my ($output);
	my ($sth) = &Do_SQL("DESCRIBE admin_users app");
	my (@ary) = $sth->fetchrow_array();
	$ary[1] = substr($ary[1],6,-2);
	$ary[1] =~ s/','/,/g;
	@ary = split(/,/, $ary[1]);
	for (0..$#ary){
		if ($ary[$_] =~ /^sa-/){
			$output .= "<option value='$ary[$_]'>".&trans_txt('usertype_'.$ary[$_])."</option>\n";
		}
	}
	(!$output) and ($output .= "<option value='---'>".&trans_txt('none')."</option>\n");
	return $output;
}


####################################################################################
########      CUSTOMS  PAGES FUNCTIONS                 #############################
####################################################################################
sub menu_list{
#-----------------------------------------
# Created on: 02/23/09  16:46:25 By  Roberto Barcenas
# Forms Involved: menu.html of any app
# Description : Builds a custom lists menu to see any kind of element marked as part of a list where the user is assigned
# Parameters : $usr{'id_admin_users'} . The function uses load_prefixtab in sub.func_sltv.html.cgi to find out the command
# Last Modified RB: 02/27/09  17:29:46 -- Added buildfavslist_returns
# Last Modified on: 09/16/09 11:31:01
# Last Modified by: MCC C. Gabriel Varela S: Se habilitan cookies para multicompañía

	my($output,$userid,$tblactual,$strtbl,$script_url);
	$userid = $usr{'id_admin_users'};
	$script_url = $va{'script_url'};
	$script_url	=~	s/admin/dbman/;
	my ($sth) = &Do_SQL("SELECT DISTINCT(Name) FROM sl_lists WHERE ID_users	=	'$userid' AND Status = 'Active'");
	my($lists) = $sth->rows;
	
	if($lists > 0){
		
		my ($sth) = &Do_SQL("SELECT tbl_name,Name,cmd,GROUP_CONCAT(ID_table SEPARATOR '|') FROM sl_lists WHERE ID_users	=	'$userid' AND Status = 'Active' GROUP BY tbl_name,Name,cmd ORDER BY tbl_name,Name");
		while(my($tbl_name,$list,$cmdlist,$id_orders) = $sth->fetchrow()){
		
			$app = uc(substr($cmdlist,0,1)).substr($cmdlist,1);
			$cmdlist = &load_prefixtab($cmdlist);
		
			if($tbl_name ne $tblactual){
				
				$tblactual = $tbl_name;
				$strtbl .= $tbl_name;
				$output .=qq|<tr><td class="menu_bar">&nbsp;&nbsp; $app</td></tr>|;
				##### Favoritos
				my $favred=&GetCookies($tbl_name.$in{'e'}."red");					$favred		=~	s/,/|/g;			chop($favred);
				my $favblue=&GetCookies($tbl_name.$in{'e'}."blue");				$favblue	=~	s/,/|/g;			chop($favblue);
				my $favgreen=&GetCookies($tbl_name.$in{'e'}."green");			$favgreen	=~	s/,/|/g;			chop($favgreen);
				
				if($favred>0 or $favblue>0 or $favgreen>0){
					if($cmdlist ne 'returns'){
						$output .=qq|<tr><td class="menu_bar" valign="top">&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Favs |;
						$output .=qq|<img width="13" height="11" name="$tbl_name_red" 	src="[va_imgurl]app_bar/small_bookmarksredon.gif" onmouseover='m_over(this)' onmouseout='m_out(this)' onClick="trjump('/cgi-bin/mod/|.$usr{'application'}.qq|/dbman?cmd=$cmdlist&search=advSearch&id_table=$favred&st=AND')">&nbsp;&nbsp;|			if $favred 		> 0;
						$output .=qq|<img width="13" height="11" name="$tbl_name_blue" src="[va_imgurl]app_bar/small_bookmarksblueon.gif" onmouseover='m_over(this)' onmouseout='m_out(this)' onClick="trjump('/cgi-bin/mod/|.$usr{'application'}.qq|/dbman?cmd=$cmdlist&search=advSearch&id_table=$favblue&st=AND')">&nbsp;&nbsp;|		if $favblue 	> 0;
						$output .=qq|<img width="13" height="11" name="$tbl_name_green" src="[va_imgurl]app_bar/small_bookmarksgreenon.gif" onmouseover='m_over(this)' onmouseout='m_out(this)' onClick="trjump('/cgi-bin/mod/|.$usr{'application'}.qq|/dbman?cmd=$cmdlist&search=advSearch&id_table=$favgreen&st=AND')">&nbsp;&nbsp;|	if $favgreen 	> 0;
						$output .=qq|</td></tr>|;
					}else{
						my @ary_colors = ("$favred","$favblue","$favgreen");
						$output .= &buildfavslist_returns(@ary_colors);
					}
				}
			}
			
			$output .=qq|<tr>
										<td class="menu_bar" onmouseover='m_over(this)' onmouseout='m_out(this)' onClick="trjump('/cgi-bin/mod/|.$usr{'application'}.qq|/dbman?cmd=$cmdlist&search=advSearch&id_table=$id_orders&st=AND')">&nbsp;&nbsp;&nbsp;&nbsp; $list </td>
									</tr>|;
		}
	}
	$output2 .=	&buildfavslist($strtbl);
	$output = qq|&nbsp;
								<table border="0" cellspacing="0" width="95%" class="formtable">
									<tr>
										<td class="menu_bar_title">My Lists</td>
									</tr>
									$output
									$output2	
								</table>|	if($lists > 0 or $output2);
	
	return $output;
}

sub buildfavslist{
#-----------------------------------------
# Created on: 02/24/09  09:25:59 By  Roberto Barcenas
# Forms Involved: 
# Description :
# Parameters : The function uses load_prefixtab in sub.func_sltv.html.cgi to find out the command
# Last Modified RB: 02/27/09  17:29:46 -- Added buildfavslist_returns
# Last Modified on: 09/16/09 11:31:56
# Last Modified by: MCC C. Gabriel Varela S: Se habilita cookies multi compañía

	my($tbldone)	=	@_;
	my(@tbls)	= ("sl_orders","sl_products","sl_parts","sl_services","sl_customers","sl_adjustments","admin_users","sl_manifests","sl_brands","sl_purchaseorders","sl_returns","sl_repmemos","sl_skus","sl_vendors","sl_warehouses","sl_wreceipts");
	my(@cmds)	= ("opr_orders","mer_products","mer_parts","mer_services","opr_customers","opr_adjustments","usrman","opr_manifests","mer_brands","mer_po","opr_returns","opr_repmemos","mer_parts","mer_vendors","opr_warehouses","mer_wreceipts");
	my($output,$favred,$favblue,$favgreen,$cmdlist,$script_url);
	$output='';
	$script_url = $va{'script_url'};
	$script_url	=~	s/admin/dbman/;
	
	for (0..$#tbls){
		if($tbldone	!~	/$tbls[$_]/){
			##### Favoritos
			my $favred=&GetCookies($tbls[$_].$in{'e'}."red");					$favred		=~	s/,/|/g;			chop($favred);
			my $favblue=&GetCookies($tbls[$_].$in{'e'}."blue");				$favblue	=~	s/,/|/g;			chop($favblue);
			my $favgreen=&GetCookies($tbls[$_].$in{'e'}."green");			$favgreen	=~	s/,/|/g;			chop($favgreen);
			
			if($favred>0 or $favblue>0 or $favgreen>0){
				if($cmds[$_] ne 'returns'){
					$cmdlist = load_prefixtab($cmds[$_]);
					$output .=qq|<tr><td class="menu_bar">&nbsp;&nbsp; |.uc(substr($tbls[$_],3,1)).substr($tbls[$_],4).qq|</td></tr>|;
					$output .=qq|<tr><td class="menu_bar" valign="top">&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Favs |; 
					
					$output .=qq|<img width="13" height="11" name="$tbls[$_]_red" src="[va_imgurl]app_bar/small_bookmarksredon.gif" onmouseover='m_over(this)' onmouseout='m_out(this)' onClick="trjump('/cgi-bin/mod/|.$usr{'application'}.qq|/dbman?cmd=$cmdlist&search=advSearch&id_table=$favred&st=AND')">&nbsp;&nbsp;|			if $favred 		> 0;
					$output .=qq|<img width="13" height="11" name="$tbls[$_]_blue" src="[va_imgurl]app_bar/small_bookmarksblueon.gif" onmouseover='m_over(this)' onmouseout='m_out(this)' onClick="trjump('/cgi-bin/mod/|.$usr{'application'}.qq|/dbman?cmd=$cmdlist&search=advSearch&id_table=$favblue&st=AND')">&nbsp;&nbsp;|		if $favblue 	> 0;
					$output .=qq|<img width="13" height="11" name="$tbls[$_]_green" src="[va_imgurl]app_bar/small_bookmarksgreenon.gif" onmouseover='m_over(this)' onmouseout='m_out(this)' onClick="trjump('/cgi-bin/mod/|.$usr{'application'}.qq|/dbman?cmd=$cmdlist&search=advSearch&id_table=$favgreen&st=AND')">&nbsp;&nbsp;|	if $favgreen 	> 0;
	
					$output .=qq|</td></tr>|;
				### Returns
				}else{
					my @ary_colors = ("$favred","$favblue","$favgreen");
					$output .= &buildfavslist_returns(@ary_colors);
				}
			}
		}
	}
	return $output;
}


sub buildfavslist_returns{
#-----------------------------------------
# Created on: 02/27/09  15:24:51 By  Roberto Barcenas
# Forms Involved: buildfavslist
# Description : Builds the favs list for returns
# Parameters : array(favsred,favsblue,favsgreen)

	my (@colors)	=	@_;
	my $output = '';
	my $script_url = $va{'script_url'};
	$script_url	=~	s/admin/dbman/;
	
	if($colors[0] ne '' or $colors[1] ne '' or $colors[2] ne ''){
	
		LINES:for (0..$#colors){
			next LINES if $colors[$_] eq '';
			my $id_returns = $colors[$_];
			$id_returns	=~	s/\|/,/g;
			my ($sth) = &Do_SQL("SELECT ID_returns,
													IF(Status = 'In Process','sorting',
													IF(Status =	'Repair','repairret',
													IF(Status	=	'QC/IT','qcreturns',
													IF(Status	=	'ATC','atcreturns',
													IF(Status	=	'Processed','crreturns',
													IF(Status	=	'Back to inventory','retwarehouse','returns')))))) FROM sl_returns WHERE ID_returns IN ($id_returns) ;"); 
			
			while(my($id,$cmd)	=	$sth->fetchrow()){
			
				$sorting[$_] .= "$id|"	if	$cmd	eq	'sorting';
				$repairret[$_] .= "$id|"	if	$cmd	eq	'repairret';
				$qcreturns[$_] .= "$id|"	if	$cmd	eq	'qcreturns';
				$atcreturns[$_] .= "$id|"	if	$cmd	eq	'atcreturns';
				$crreturns[$_] .= "$id|"	if	$cmd	eq	'crreturns';
				$retwarehouse[$_] .= "$id|"	if	$cmd	eq	'retwarehouse';
				$returns[$_] .= "$id|"	if	$cmd	eq	'returns';
			}
		}
		
		$output .=qq|<tr><td class="menu_bar">&nbsp;&nbsp; Returns</td></tr>|;
			
		## Sorting
		if($sorting[0] ne '' or $sorting[1] ne '' or $sorting[2] ne ''){
			
			my $cmdlist = load_prefixtab('sorting'); 
			$output .=qq|<tr><td class="menu_bar" valign="top">&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Favs Sorting |; 
			
			$output .=qq|<img width="13" height="11" name="sorting_red" src="[va_imgurl]app_bar/small_bookmarksredon.gif" onmouseover='m_over(this)' onmouseout='m_out(this)' onClick="trjump('/cgi-bin/mod/|.$usr{'application'}.qq|/dbman?cmd=$cmdlist&search=advSearch&id_table=$sorting[0]&st=AND')">&nbsp;&nbsp;|	if $sorting[0]	ne	'';
			$output .=qq|<img width="13" height="11" name="sorting_blue" src="[va_imgurl]app_bar/small_bookmarksblueon.gif" onmouseover='m_over(this)' onmouseout='m_out(this)' onClick="trjump('/cgi-bin/mod/|.$usr{'application'}.qq|/dbman?cmd=$cmdlist&search=advSearch&id_table=$sorting[1]&st=AND')">&nbsp;&nbsp;|		if $sorting[1]	ne	'';
			$output .=qq|<img width="13" height="11" name="sorting_green" src="[va_imgurl]app_bar/small_bookmarksgreenon.gif" onmouseover='m_over(this)' onmouseout='m_out(this)' onClick="trjump('/cgi-bin/mod/|.$usr{'application'}.qq|/dbman?cmd=$cmdlist&search=advSearch&id_table=$sorting[2]&st=AND')">&nbsp;&nbsp;|	if	$sorting[2]	ne	'';

			$output .=qq|</td></tr>|;
		}
		
		## Repair
		if($repairret[0] ne '' or $repairret[1] ne '' or $repairret[2] ne ''){
			
			my $cmdlist = load_prefixtab('repairret'); 
			$output .=qq|<tr><td class="menu_bar" valign="top">&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; Repair |; 
			
			$output .=qq|<img width="13" height="11" name="repair_red" src="[va_imgurl]app_bar/small_bookmarksredon.gif" onmouseover='m_over(this)' onmouseout='m_out(this)' onClick="trjump('/cgi-bin/mod/|.$usr{'application'}.qq|/dbman?cmd=$cmdlist&search=advSearch&id_table=$repairret[0]&st=AND')">&nbsp;&nbsp;|	if $repairret[0]	ne	'';
			$output .=qq|<img width="13" height="11" name="repair_blue" src="[va_imgurl]app_bar/small_bookmarksblueon.gif" onmouseover='m_over(this)' onmouseout='m_out(this)' onClick="trjump('/cgi-bin/mod/|.$usr{'application'}.qq|/dbman?cmd=$cmdlist&search=advSearch&id_table=$repairret[1]&st=AND')">&nbsp;&nbsp;|		if $repairret[1]	ne	'';
			$output .=qq|<img width="13" height="11" name="repair_green" src="[va_imgurl]app_bar/small_bookmarksgreenon.gif" onmouseover='m_over(this)' onmouseout='m_out(this)' onClick="trjump('/cgi-bin/mod/|.$usr{'application'}.qq|/dbman?cmd=$cmdlist&search=advSearch&id_table=$repairret[2]&st=AND')">&nbsp;&nbsp;|	if	$repairret[2]	ne	'';

			$output .=qq|</td></tr>|;
		}
		
		## QC /IT
		if($qcreturns[0] ne '' or $qcreturns[1] ne '' or$qcreturns[2] ne ''){
			
			my $cmdlist = load_prefixtab('qcreturns'); 
			$output .=qq|<tr><td class="menu_bar" valign="top">&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; QC/IT |; 
			
			$output .=qq|<img width="13" height="11" name="qcreturns_red" src="[va_imgurl]app_bar/small_bookmarksredon.gif" onmouseover='m_over(this)' onmouseout='m_out(this)' onClick="trjump('/cgi-bin/mod/|.$usr{'application'}.qq|/dbman?cmd=$cmdlist&search=advSearch&id_table=$qcreturns[0]&st=AND')">&nbsp;&nbsp;|	if $qcreturns[0]	ne	'';
			$output .=qq|<img width="13" height="11" name="qcreturns_blue" src="[va_imgurl]app_bar/small_bookmarksblueon.gif" onmouseover='m_over(this)' onmouseout='m_out(this)' onClick="trjump('/cgi-bin/mod/|.$usr{'application'}.qq|/dbman?cmd=$cmdlist&search=advSearch&id_table=$qcreturns[1]&st=AND')">&nbsp;&nbsp;|		if $qcreturns[1]	ne	'';
			$output .=qq|<img width="13" height="11" name="qcreturns_green" src="[va_imgurl]app_bar/small_bookmarksgreenon.gif" onmouseover='m_over(this)' onmouseout='m_out(this)' onClick="trjump('/cgi-bin/mod/|.$usr{'application'}.qq|/dbman?cmd=$cmdlist&search=advSearch&id_table=$qcreturns[2]&st=AND')">&nbsp;&nbsp;|	if	$qcreturns[2]	ne	'';

			$output .=qq|</td></tr>|;
		}
		
		## ATC MEX
		if($atcreturns[0] ne '' or $atcreturns[1] ne '' or $atcreturns[2] ne ''){
			
			my $cmdlist = load_prefixtab('atcreturns'); 
			$output .=qq|<tr><td class="menu_bar" valign="top">&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; ATC MX |; 
			
			$output .=qq|<img width="13" height="11" name="atcreturns_red" src="[va_imgurl]app_bar/small_bookmarksredon.gif" onmouseover='m_over(this)' onmouseout='m_out(this)' onClick="trjump('/cgi-bin/mod/|.$usr{'application'}.qq|/dbman?cmd=$cmdlist&search=advSearch&id_table=$atcreturns[0]&st=AND')">&nbsp;&nbsp;|	if $atcreturns[0]	ne	'';
			$output .=qq|<img width="13" height="11" name="atcreturns_blue" src="[va_imgurl]app_bar/small_bookmarksblueon.gif" onmouseover='m_over(this)' onmouseout='m_out(this)' onClick="trjump('/cgi-bin/mod/|.$usr{'application'}.qq|/dbman?cmd=$cmdlist&search=advSearch&id_table=$atcreturns[1]&st=AND')">&nbsp;&nbsp;|		if $atcreturns[1]	ne	'';
			$output .=qq|<img width="13" height="11" name="atcreturns_green" src="[va_imgurl]app_bar/small_bookmarksgreenon.gif" onmouseover='m_over(this)' onmouseout='m_out(this)' onClick="trjump('/cgi-bin/mod/|.$usr{'application'}.qq|/dbman?cmd=$cmdlist&search=advSearch&id_table=$atcreturns[2]&st=AND')">&nbsp;&nbsp;|	if	$atcreturns[2]	ne	'';

			$output .=qq|</td></tr>|;
		}			
		
		## ATC MIA
		if($crreturns[0] ne '' or $crreturns[1] ne '' or $crreturns[2] ne ''){
			
			my $cmdlist = load_prefixtab('crreturns'); 
			$output .=qq|<tr><td class="menu_bar" valign="top">&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; ATC MIA |; 
			
			$output .=qq|<img width="13" height="11" name="crreturns_red" src="[va_imgurl]app_bar/small_bookmarksredon.gif" onmouseover='m_over(this)' onmouseout='m_out(this)' onClick="trjump('/cgi-bin/mod/|.$usr{'application'}.qq|/dbman?cmd=$cmdlist&search=advSearch&id_table=$crreturns[0]&st=AND')">&nbsp;&nbsp;|	if $crreturns[0]	ne	'';
			$output .=qq|<img width="13" height="11" name="crreturns_blue" src="[va_imgurl]app_bar/small_bookmarksblueon.gif" onmouseover='m_over(this)' onmouseout='m_out(this)' onClick="trjump('/cgi-bin/mod/|.$usr{'application'}.qq|/dbman?cmd=$cmdlist&search=advSearch&id_table=$crreturns[1]&st=AND')">&nbsp;&nbsp;|		if $crreturns[1]	ne	'';
			$output .=qq|<img width="13" height="11" name="crreturns_green" src="[va_imgurl]app_bar/small_bookmarksgreenon.gif" onmouseover='m_over(this)' onmouseout='m_out(this)' onClick="trjump('/cgi-bin/mod/|.$usr{'application'}.qq|/dbman?cmd=$cmdlist&search=advSearch&id_table=$crreturns[2]&st=AND')">&nbsp;&nbsp;|	if	$crreturns[2]	ne	'';

			$output .=qq|</td></tr>|;
		}		
		
		## Back To Inventory
		if($retwarehouse[0] ne '' or $retwarehouse[1] ne '' or $retwarehouse[2] ne ''){
			
			my $cmdlist = load_prefixtab('retwarehouse'); 
			$output .=qq|<tr><td class="menu_bar" valign="top">&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; BTI |; 
			
			$output .=qq|<img width="13" height="11" name="retwarehouse_red" src="[va_imgurl]app_bar/small_bookmarksredon.gif" onmouseover='m_over(this)' onmouseout='m_out(this)' onClick="trjump('/cgi-bin/mod/|.$usr{'application'}.qq|/dbman?cmd=$cmdlist&search=advSearch&id_table=$retwarehouse[0]&st=AND')">&nbsp;&nbsp;|	if $retwarehouse[0]	ne	'';
			$output .=qq|<img width="13" height="11" name="retwarehouse_blue" src="[va_imgurl]app_bar/small_bookmarksblueon.gif" onmouseover='m_over(this)' onmouseout='m_out(this)' onClick="trjump('/cgi-bin/mod/|.$usr{'application'}.qq|/dbman?cmd=$cmdlist&search=advSearch&id_table=$retwarehouse[1]&st=AND')">&nbsp;&nbsp;|		if $retwarehouse[1]	ne	'';
			$output .=qq|<img width="13" height="11" name="retwarehouse_green" src="[va_imgurl]app_bar/small_bookmarksgreenon.gif" onmouseover='m_over(this)' onmouseout='m_out(this)' onClick="trjump('/cgi-bin/mod/|.$usr{'application'}.qq|/dbman?cmd=$cmdlist&search=advSearch&id_table=$retwarehouse[2]&st=AND')">&nbsp;&nbsp;|	if	$retwarehouse[2]	ne	'';

			$output .=qq|</td></tr>|;
		}
		
		## Returns
		if($returns[0] ne '' or $returns[1] ne '' or $returns[2] ne ''){
			
			my $cmdlist = load_prefixtab('returns'); 
			$output .=qq|<tr><td class="menu_bar" valign="top">&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Favs Returns |; 
			
			$output .=qq|<img width="13" height="11" name="returns_red" src="[va_imgurl]app_bar/small_bookmarksredon.gif" onmouseover='m_over(this)' onmouseout='m_out(this)' onClick="trjump('/cgi-bin/mod/|.$usr{'application'}.qq|/dbman?cmd=$cmdlist&search=advSearch&id_table=$returns[0]&st=AND')">&nbsp;&nbsp;|	if $returns[0]	ne	'';
			$output .=qq|<img width="13" height="11" name="returns_blue" src="[va_imgurl]app_bar/small_bookmarksblueon.gif" onmouseover='m_over(this)' onmouseout='m_out(this)' onClick="trjump('/cgi-bin/mod/|.$usr{'application'}.qq|/dbman?cmd=$cmdlist&search=advSearch&id_table=$returns[1]&st=AND')">&nbsp;&nbsp;|		if $returns[1]	ne	'';
			$output .=qq|<img width="13" height="11" name="returns_green" src="[va_imgurl]app_bar/small_bookmarksgreenon.gif" onmouseover='m_over(this)' onmouseout='m_out(this)' onClick="trjump('/cgi-bin/mod/|.$usr{'application'}.qq|/dbman?cmd=$cmdlist&search=advSearch&id_table=$returns[2]&st=AND')">&nbsp;&nbsp;|	if	$returns[2]	ne	'';

			$output .=qq|</td></tr>|;
		}
	}
	return $output;
}



sub thisweek {
# --------------------------------------------------------
	my ($sth) = &Do_SQL("SELECT WEEK(CURDATE())");
	return $sth->fetchrow();
}

#GV Inicia
#GV Inicia 14may2008
sub hasreturn{
	#Acción: Creación
	#Comentarios:
	# --------------------------------------------------------
	# Forms Involved: \cgi-bin\templates\en\app\administration\opr_orders_view.html
	# Created on: 14/may/2008 11:48AM GMT -0600
	# Last Modified on: 17 - jun - 2008 11:06 am
	# Last Modified by: Jose Ramirez
	# Author: MCC C. Gabriel Varela S.
	# Description :  Mostrará si una orden tiene un return, se modifica para mostrar una imagen en vez de texto y link
	# Parameters :
	# Last Modified on: 09/05/08 15:09:05
	# Last Modified by: MCC C. Gabriel Varela S: Se establece el campo ID_orders en la consulta para que haga referencia al de sl_orders_products
	# Last Modified on: 10/16/08 16:51:10
	# Last Modified by: MCC C. Gabriel Varela S: Se omiten los status de return Resolved, Archived y Void
	# Last Modified on: 10/21/08 10:51:31
	# Last Modified by: MCC C. Gabriel Varela S: Se modifica para que ya no se cuente status Archived
	
	my ($str, $rec);
	my $sth=&Do_SQL("SELECT COUNT(*) FROM `sl_returns`  WHERE ID_orders = '$in{'id_orders'}' AND Status NOT IN('Resolved','Void')");
	$rec=$sth->fetchrow();
	$str =  qq|<a href='#' onClick='trjump("$va{'script_url'}?cmd=$in{'cmd'}&view=$in{'id_orders'}&tab=7&tabs=1#tabs")'><img src='[va_imgurl]/[ur_pref_style]/return.gif' title='Esta orden tiene registros de returns' alt='returnsinorder' border='0' ></a>| if ($rec);	
	
	my ($sth) = &Do_SQL("SELECT COUNT(*) FROM sl_crmtickets WHERE ID_ref='$in{'id_orders'}' AND ID_type='orders' AND Status IN ('New','In Process')");
	if ($sth->fetchrow >0){
		$str .=  qq|<a href='#' onClick='trjump("$va{'script_url'}?cmd=$in{'cmd'}&view=$in{'id_orders'}&tab=15&tabs=1#tabs")'><img src='[va_imgurl]/[ur_pref_style]/tickets.gif' title='Esta orden tiene registros de Tickets' alt='returnsinorder' border='0' ></a>|;
	}
	
	return $str;
	#return 'Esta orden tiene registros de returns';
}

#GV Termina 14may2008
#GV Inicia 25jun2008
sub checkparts{
	# Created on: 20/jun/2008 01:36:18 PM GMT -06:00
	# Last Modified on: 07/11/2008
	# Last Modified by: MCC C Gabriel Varela S: Se agrega condición de id de return
	# Author: MCC C. Gabriel Varela S.
	# Description : Mostrará un mensaje en caso de que el return contenga un producto que es un set y las partes no coincidan
	# Parameters :
	
	#Verifica si algún UPC es un set
	#return;#Pendiente quitar return al terminar
	my $productsids="";
	my $upcs="",$ret="";
	#GV Inicia modificación 24jun2008
	my($sth0)=&Do_SQL("Select count(*) from sl_returns_upcs inner join sl_skus on (sl_returns_upcs.UPC=sl_skus.UPC) where ID_returns=$in{'id_returns'} and IsSet='Y' and sl_returns_upcs.UPC!=''");
	#GV Termina modificación 24jun2008
	$rec0=$sth0->fetchrow;
	if(!$rec0){
		return;
	}else{
		#GV Inicia modificación 24jun2008
		my($sth0)=&Do_SQL("SELECT sl_returns_upcs.UPC, sl_skus.ID_sku_products from sl_returns_upcs inner join sl_skus on (sl_returns_upcs.UPC=sl_skus.UPC) where ID_returns=$in{'id_returns'} and IsSet='Y' and sl_returns_upcs.UPC!=''");
		#GV Termina modificación 24jun2008
		while($rec0=$sth0->fetchrow_hashref)
		{
			$productsids.=",$rec0->{'ID_sku_products'}";
			$upcs.=",$rec0->{'UPC'}";
		}
	}
	my($sth)=&Do_SQL("SELECT UPC
										FROM `sl_skus_parts` 
										INNER JOIN sl_parts ON ( sl_parts.`ID_parts` = sl_skus_parts.`ID_parts` ) 
										INNER JOIN sl_skus ON ( sl_parts.`ID_parts` = sl_skus.ID_products ) 
										WHERE sl_skus_parts.`ID_sku_products` in (0$productsids)");
	while($rec=$sth->fetchrow()){
		$i++;
		$upcs.=",$rec";
	}
  #GV Inicia modificación 24jun2008
	#GV Inicia modificación 23jun2008
	#GV Termina modificación 24jun2008
	$va{'reti'}= "<script type='text/javascript'>
//<![CDATA[
	onload = function(){
		popup_show('ajax_windows', 'ajax_drag', 'ajax_exit', 'element-right', -1, 35,'wumsg');
		//loadDoc('cgi-bin/templates/en/app/wms/list_parts.html');
		
	}
//]]>
</script>
<div id='ajax_windows' style='visibility: hidden; display: none; background-color: #ffffff;'>
				<div class='menu_bar_title' id='ajax_drag'>
				<table width=100% cellpadding=0 cellspacing=3>
					<td align=left>&nbsp;&nbsp;Showing parts</td>
					<td align=right width=20px><img id='ajax_exit' src='[va_imgurl][ur_pref_style]/popupclose.gif' align=right style='cursor:pointer;'></td>
				</table>		
				</div>
				<div class='formtable'>
				<IFRAME SRC='/cgi-bin/common/apps/ajaxbuild?ajaxbuild=showparts&upcs=$upcs&id_returns=$in{'id_returns'}' name='rcmd' TITLE='Recieve Commands' width='566' height='150' FRAMEBORDER='0' MARGINWIDTH='0' MARGINHEIGHT='0' SCROLLING='auto'>
				<H2>Unable to do the script</H2>
				<H3>Please update your Browser</H3>
				</IFRAME>	
				</div></div>
";
	return $va{'reti'};
}


sub loaddatapayment{
# --------------------------------------------------------
# Forms Involved: common/tabs/orders.cgi 
# Created on: 6/03/2008 11:43PM
# Last Modified on: 6/23/2008 
# Last Modified by: Roberto Barcenas
# Author: Roberto Barcenas
# Description : Load the $in{} variables when tabs AJAX are called
# Parameters : 
# Variables : 

	if($cfg{'dhtmlxtab'} == 0 or $cfg{'dhtmlxtab'} == 2){
		my ($id_orders) = @_;
		my ($sth) = &Do_SQL("SELECT * FROM sl_orders_payments WHERE ID_orders='$id_orders' ORDER BY ID_orders_payments DESC LIMIT 1;");
		$rec = $sth->fetchrow_hashref;
		
		for (1..9){
			$in{'pmtfield'.$_} = $rec->{'PmtField'.$_};
		}
	
		if ($rec->{'Type'} eq "Check"){
			$in{'month'} = substr($rec->{'PmtField5'},0,2);
			$in{'day'} = substr($rec->{'PmtField5'},3,2);
			$in{'year'} = substr($rec->{'PmtField5'},6,4);
		}else{
			$in{'month'} = substr($rec->{'PmtField4'},0,2);
			$in{'year'} = substr($rec->{'PmtField4'},2,2);
		}
		
		$in{'type'} = $rec->{'Type'};	
	}	
}


sub selecttype{
	# --------------------------------------------------------
	# Created by: MCC C Gabriel Varela S
	# Created on: 07/11/2008
	# Description : Muestra el contenido del campo Enum Type de sl_customers
	# Notes : (Modified on : Modified by :)	
	return &build_select_from_enum("Type","sl_customers");
}




sub invoice_link {
# --------------------------------------------------------

# Author: Jose Ramirez Garcia
# Created on:  01/08/2009
# Last Modified on: 
# Last Modified by: 
# Description : 
# Forms Involved: opr_orders_view
# Parameters : 
# Last Modified RB: 03/31/09  16:30:17 -- Se adapto para redirigir a follow-up o administration


	my ($out, $check_order) = "";
	$check_order = &check_ord_totals($in{'id_orders'});
	
	my $cmd = 'opr_invoices';
	@ary = split(/\//,$va{'script_url'});
	$cmd = 'invoices'	if	$ary[2] eq 'follow-up';
	
	if($check_order eq "OK"){
		$out = '<a href="/cgi-bin/mod/[ur_application]/dbman?cmd='.$cmd.'&view=[in_id_orders]"><img src="[va_imgurl]/[ur_pref_style]/b_invoice.gif" title="Invoice" alt="Invoice" border="0"></a>';
	} else {
		$out = '<img src="[va_imgurl]/[ur_pref_style]/inactive.gif" title="Invoice Error" border="0">';
	}
	return $out;
}



sub func_list_manager{
# --------------------------------------------------------
# Forms Involved: 
# Created on: 02/19/09 13:16:27
# Author: MCC C. Gabriel Varela S.
# Description :   
# Parameters :
# Last Modified on: 02/26/09 12:27:05
# Last Modified by: MCC C. Gabriel Varela S: Se incluye referencia top

#	my $user,$order,$type;
#	$user=$usr{'id_admin_users'};
#	$type=$in{'db'};
#	$order=$type;
#	$order=~s/sl_/id_/g;
#	$order=$in{$order};
#	$in{'user'}=$user;
#	$in{'id'}=$order;
#	$in{'table'}=$type;
 
	my ($output);
	$output = qq| <a href=\"/cgi-bin/common/apps/ajaxbuild?ajaxbuild=manage_lists&id=[in_view]&db=[in_db]&table=[in_db]&path=[va_script_url]&cmdo=[in_cmd]&dototemp=YES\" title=\"List Manager\" class=\"fancy_modal_iframe\">
		<img src='$va{'imgurl'}/$usr{'pref_style'}/b_manlist.gif' title=' Manage lists. ' alt=' Manage lists. ' border='0' width='24' height='24'>
	</a><a name='top' id='top'>|;

	return $output;
}


sub set_products_dids{
#-----------------------------------------
# Created on: 04/17/09  09:44:18 By  Roberto Barcenas
# Forms Involved: mer_products
# Description : Inserta relacion id_products,id_dids en la tabla sl_products_dids
# Parameters : 	id_products, string dids

	my($id_products,$strdids) = @_;
	my ($sth)	= &Do_SQL("DELETE FROM sl_products_dids WHERE ID_products = '$id_products' ");
	
	if($strdids ne ''){
		my @dids = split(/\|/,$strdids);
		
		for(0..$#dids){
			my ($sth)	= &Do_SQL("INSERT INTO sl_products_dids VALUES(0,$id_products,$dids[$_],'Active',CURDATE(),NOW(),$usr{'id_admin_users'});");
		}
	}
}


sub multicompany{
#-----------------------------------------
# Created on: 4/24/2009 1:38:15 PM By  Carlos Haas
# Forms Involved:Login
# Description : Inserta nombres del las compañias
# Parameters : 	
# Last Modified on: 06/12/09 11:47:03

	my ($output);
	$cfg{'max_e'} = 1 if (!$cfg{'max_e'});
	for my $i(1..$cfg{'max_e'}){
		my $selected='';
		$selected = 'selected="selected"' if $i==1;
		
		if ($cfg{'app_e'.$i}){
			$output .= "<option value='$i' $selected>".$cfg{'app_e'.$i}."</option>\n";
		}
	}
	if ($output){
		return qq|
		<select name='e' class='input250'>
			<option value=''>---</option>
			<!--<option value='0'>|. $cfg{'app_e'.$i}.qq|</option>-->
			$output
		</select>\n|;
	}else{
		return $cfg{'app_title'};
	}
}

sub show_image_in_page{
# --------------------------------------------------------
# Forms Involved: 
# Created on: 05/11/09 17:19:02
# Author: MCC C. Gabriel Varela S.
# Description :   
# Parameters :
# Last Modified on: 05/12/09 12:21:30
# Last Modified by: MCC C. Gabriel Varela S: Se manda parámetro img
	my ($output,$id);
	($id)=@_;
	## if the product is a set, assign that value to id_products
	if (-e "$cfg{'path_imgman'}/$id"."b1.gif"){
		$output = qq|<IFRAME SRC="/cgi-bin/showimages?id=$id&e=$in{'e'}&img=1" name="rcmd" TITLE="Show Products" width="115" height="115" FRAMEBORDER="0" MARGINWIDTH="0" MARGINHEIGHT="0" SCROLLING="auto">
			<H2>Unable to do the script</H2>
			<H3>Please update your Browser</H3>
		</IFRAME>|;
	}else{
		$output = "<p align='center'>".&trans_txt('no_imgs_available')."</p>";
	}	
	return $output;
}

sub build_closepo_button{
# --------------------------------------------------------

# Author: Jose Ramirez Garcia
# Created on: 07/22/2008
# Last Modified on: 
# Last Modified by: 
# Description : it shows the close po button when status isn't received or cancelled
# Forms Involved: 
# Parameters :
# Last Time Modified by RB: La funcion del botin cambia cuando se trata de un supply 
	
#TODO: Botones en transtxt
	my ($output);
	if(&check_permissions('mer_po_close','','') and $in{'status'} ne 'Received' and $in{'status'} ne 'Cancelled') {
		
		$output = qq|
					<a href="#"  onclick="confcloseup()" title="Close Purchase Order" ><img src="/sitimages/default/b_closeorder.gif" title="Close Purchase Order" border=0 width="24px"></a>
					  <form action="/cgi-bin/mod/admin/dbman" method="post" id="cform">
						<input type="hidden" name="cmd" value="mer_po">
						<input type="hidden" name="view" value="$in{'id_purchaseorders'}">
						<input type="hidden" name="id_purchaseorders" value="$in{'id_purchaseorders'}">
						<input type="hidden" name="closepo" value="1">
							
						<center><!--<input type="buttom" value="Close Purchase Order" class="button" onclick="confcloseup()">--></center>
							<script>
								function confcloseup(){
									if(confirm("Close Purchase Order?")){
										document.getElementById("cform").submit();
									}
								}
							</script>
						</form>
							|;
	}
	return $output;
}


############################################################################################
############################################################################################
#	Function: create_warehouse_batch_file
#   		Cheecks for a batch and creates a new one if none exists
#
#	Created by:
#		_Roberto Barcenas_
#
#	Modified By:
#
#   	Parameters:
#		- id_warehouses : ID_warehouses
#
#   	Returns:
#		- $id_new_batch
#
#   	See Also:
#   	- apps/ajaxbuild.cgi: chg_warehouse_batch
#   	- op-wman/admin_cod.html.cgi: cod_preorderstobatch
#
sub create_warehouse_batch_file{
############################################################################################
############################################################################################

    my ($id_warehouses);
	($id_warehouses)=@_;

	my ($sth) = &Do_SQL("SELECT ID_warehouses_batches FROM sl_warehouses_batches WHERE ID_warehouses = '$id_warehouses' AND Status IN ('New','Assigned'/*,'Processed'*/) ORDER BY ID_warehouses_batches LIMIT 1;");
	my($id_new_batch) = $sth->fetchrow();

	if(!$id_new_batch){
		my ($sth) = &Do_SQL("INSERT INTO sl_warehouses_batches SET ID_warehouses=$id_warehouses, Status='New', Date=CURDATE(),Time=CURTIME(),ID_admin_users='$usr{'id_admin_users'}';");
		$id_new_batch = $sth->{'mysql_insertid'};

		$in{'db'}='sl_warehouses_batches';
		&auth_logging('warehouses_batches_added',$id_new_batch);
	}

	return $id_new_batch;

}


############################################################################################
############################################################################################
#	Function: create_journalentries
#   		
#   	Set and Get New Daily Journal Entry
#
#	Created by:
#		_Roberto Barcenas_
#
#	Modified By:
#
#   	Parameters:
#		- category : category
#
#   	Returns:
#		- $id_journalentries
#
#   	See Also:
#   	- 
#   	- 
#
sub create_journalentries{
############################################################################################
############################################################################################

	my ($category) = @_;
	my ($id_journalentries);

	my ($sth) = &Do_SQL("SELECT ID_journalentries FROM sl_journalentries WHERE Categories LIKE '%category%' AND Date = CURDATE() AND Status  = 'New' ORDER BY ID_journalentries DESC LIMIT 1;");
	($id_journalentries) = $sth->fetchrow();

	if(!$id_journalentries){

		my $this_category;
		my @ary = split(/\s/, $category);
		if(scalar @ary > 1){
			for(0..$#ary){
				$this_category .= uc(substr($ary[$_],0,1));
			}
		}else{
			$this_category = uc(substr($ary[0],0,3));
		}

		my ($sth) = &Do_SQL("INSERT INTO sl_journalentries SET JournalDate = CURDATE(), Categories = '$category', comments = '', Status = 'New', Date = CURDATE(), Time = CURTIME(), ID_admin_users = '1';");
		$id_journalentries = $sth->{'mysql_insertid'};
		&Do_SQL("UPDATE sl_journalentries SET comments = CONCAT('". $this_category . $id_journalentries ."_',DATE_FORMAT(CURDATE(),'%d%m%Y') ) WHERE ID_journalentries = '$id_journalentries';");

	}

	return $id_journalentries;
}


sub opr_warehouses_inventory {
# --------------------------------------------------------
	## Checking Permission

	my ($sth) = &Do_SQL("SELECT COUNT(*) FROM sl_warehouses WHERE Status='Active';");
	$va{'matches'} = $sth->fetchrow();
	if ($va{'matches'}>0){
		($va{'pageslist'},$qs) = &pages_list($in{'nh'},"/cgi-bin/mod/$usr{'application'}/admin",$va{'matches'},$usr{'pref_maxh'});
		my (@c) = split(/,/,$cfg{'srcolors'});
		(!$in{'nh'}) and ($in{'nh'}=1);
		$first = ($in{'nh'} - 1) * $usr{'pref_maxh'};	
		my ($sth) = &Do_SQL("SELECT * FROM sl_warehouses WHERE Status='Active' ORDER BY ID_warehouses DESC ;");
		while ($rec = $sth->fetchrow_hashref){
			$d = 1 - $d;
			my ($sth2) = &Do_SQL("SELECT SUM(Quantity) FROM sl_warehouses_location WHERE ID_warehouses='$rec->{'ID_warehouses'}';");	
			$tot_items = &format_number($sth2->fetchrow());
			my ($sth2) = &Do_SQL("SELECT COUNT(*) FROM sl_warehouses_location WHERE ID_warehouses='$rec->{'ID_warehouses'}' GROUP BY ID_products;");	
			$tot_warehouse = &format_number($sth2->rows());
			
			
	
			$va{'searchresults'} .= qq|
				<tr bgcolor='$c[$d]' onmouseover='m_over(this)' onmouseout='m_out(this)' onClick=\"trjump('/cgi-bin/mod/$usr{'application'}/admin?cmd=opr_warehouses_inv_wlist&seacrh=1&ID_warehouses=$rec->{'ID_warehouses'}')\">
					<td class='smalltext'>$rec->{'ID_warehouses'}</td>
					<td class='smalltext'>$rec->{'Name'}</td>
					<td class='smalltext' align="right">$tot_warehouse</td>
					<td class='smalltext' align="right">$tot_items</td>
				</tr>\n|;
		}
	}else{
		$va{'pageslist'} = 1;
		$va{'searchresults'} = qq|
			<tr>
				<td colspan='4' align='center'>|.&trans_txt('search_nomatches').qq|</td>
			</tr>\n|;
	}
	print "Content-type: text/html\n\n";
	print &build_page('opr_warehouse_inv.html');
}

#############################################################################
#############################################################################
#   Function: opr_warehouses_inventory_available
#
#       Es: Inventario Completo de almacenes por gaveta
#       En: Full inventory in warehouses by locations
#
#    Created on: 2013-04-26
#
#    Author: Alejandro Diaz
#
#    Modifications:
#
#        - Modified on **: 
#
#   Parameters:
#
#
#  Returns:
#
#      - 
#
#   See Also:
#
#      <>
#
sub opr_warehouses_inventory_available {
#############################################################################
#############################################################################
	if($in{'export'}){
		print "Content-type: application/octet-stream\n";
		print "Content-disposition: attachment; filename=inventory_$in{'id_warehouses'}.csv\n\n";
		print  "Warehouse ID,Warehouse,Product ID,UPC,Model/Name,Cost,Total,Assigned,Available\r\n";
	}
		
	if ($in{'onlyphysical'}){
		$addsql = " AND sl_warehouses.Type='Physical' ";
		$va{'addtitle'} .= " (Only Physical) ";
	}

	if (int($in{'id_warehouses'}) > 0){
		$addsql .= " AND sl_warehouses_location.ID_warehouses='$in{'id_warehouses'}' ";
		$va{'addtitle'} .= " ($in{'id_warehouses'}) ";
		$va{'addtitle'} .= &load_db_names('sl_warehouses','ID_warehouses',$in{'id_warehouses'},'[Name]');
	}

	$addsql .= ($in{'notempty'})? ' AND Quantity > 0 ':'';
	
	my $sql = "	SELECT 
	sl_warehouses_location.ID_warehouses
	, sl_warehouses.Name as Warehouse
	, sl_warehouses_location.ID_products
	, sl_parts.Name
	, SUM(Quantity) AS Quantity
	, sl_skus.UPC
	FROM sl_warehouses_location 
	INNER JOIN sl_parts ON ID_parts = RIGHT( ID_products, 4 ) 
	INNER JOIN sl_locations ON sl_locations.ID_warehouses = sl_warehouses_location.ID_warehouses AND sl_locations.Code = sl_warehouses_location.Location 
	INNER JOIN sl_warehouses ON sl_locations.ID_warehouses=sl_warehouses.ID_warehouses
	INNER JOIN sl_skus ON sl_skus.ID_sku_products=sl_warehouses_location.ID_products
	WHERE 1	$addsql
	GROUP BY sl_warehouses_location.ID_warehouses, sl_warehouses_location.ID_products
	ORDER BY sl_warehouses_location.ID_warehouses, sl_warehouses_location.ID_products";
	
	my ($sth) = &Do_SQL("SELECT count(*) FROM ( $sql ) as rows");
	$va{'matches'} = $sth->fetchrow();
	if ($va{'matches'}>0){
		
		$va{'options'} = qq|&nbsp;&nbsp;<a href="javascript:prnwin('[va_script_url]?cmd=[in_cmd]&seacrh=1&id_warehouses=[in_id_warehouses]&print=1')"><img src='[va_imgurl]/[ur_pref_style]/b_print.png' title='Print' alt='' border='0'></a>|;

		if(!$in{'print'} and !$in{'export'}){
			($va{'pageslist'},$qs) = &pages_list($in{'nh'},"/cgi-bin/mod/$usr{'application'}/admin",$va{'matches'},$usr{'pref_maxh'});
			my (@c) = split(/,/,$cfg{'srcolors'});
			(!$in{'nh'}) and ($in{'nh'}=1);
			$first = ($in{'nh'} - 1) * $usr{'pref_maxh'};
			$sth_det = &Do_SQL("$sql LIMIT $first,$usr{'pref_maxh'};");
		}else{
			$sth_det = &Do_SQL("$sql");
		}

		while (my $rec = $sth_det->fetchrow_hashref){
		 	my $location = $rec->{'Location'};
		 	my ($inv_assigned) = 0;

			# SKU en pedidos tipo SKU
			$sql_inv = "SELECT IFNULL(SUM(sl_orders_products.Quantity),0)Quantity
			FROM sl_orders
			INNER JOIN sl_orders_products ON sl_orders.ID_orders=sl_orders_products.ID_orders
			WHERE 1
			AND sl_orders_products.Related_ID_products='$rec->{'ID_products'}'
			AND sl_orders_products.Status IN ('Active','Exchange','ReShip')
			AND sl_orders.StatusPrd='In Fulfillment'
			AND sl_orders.Status='Processed'";
			$sth_inv = &Do_SQL("$sql_inv");
			$inv_assigned = $sth_inv->fetchrow_array();
			
			# SKU en pedidos tipo Producto
			$sql_inv = "SELECT IFNULL(SUM(sl_skus_parts.Qty),0)Qty
			FROM sl_orders
			INNER JOIN sl_orders_products ON sl_orders.ID_orders=sl_orders_products.ID_orders
			INNER JOIN sl_skus_parts ON sl_skus_parts.ID_sku_products=sl_orders_products.ID_products
			WHERE 1
			AND sl_skus_parts.ID_parts=".abs(400000000 - $rec->{'ID_products'})."
			AND sl_orders_products.Status IN ('Active','Exchange','ReShip')
			AND sl_orders.StatusPrd='In Fulfillment'
			AND sl_orders.Status='Processed'";
			$sth_inv = &Do_SQL("$sql_inv");

			$inv_assigned += $sth_inv->fetchrow_array();

			$txtlink = '';

			my $cost_adj = 0;
			($sltvcost, $cost_adj) = &load_sltvcost($rec->{'ID_products'});
			
			$d = 1 - $d;
			if ($rec->{'ID_products'} =~ /^1/){
				$namemodel=&load_db_names('sl_products','ID_products',substr($rec->{'ID_products'},3,6),'[Model]<br>[Name]');
				$prdlink = "/cgi-bin/mod/admin/dbman?cmd=mer_products&view=".substr($rec->{'ID_products'},3,6);
			}else{
				$namemodel=&load_db_names('sl_parts','ID_parts',substr($rec->{'ID_products'},5,4),'[Model]<br>[Name]')	if length($rec->{'ID_products'}) == 9;
				$namemodel = 'N/A' if (!$namemodel);
				$prdlink = "/cgi-bin/mod/".$usr{'application'}."/dbman?cmd=mer_parts&view=".substr($rec->{'ID_products'},5,4);
			}
			$txtlink = qq|onmouseover='m_over(this)' onmouseout='m_out(this)' onClick=\"trjump('$prdlink')\"	| if(!$in{'print'} and !$in{'export'});
			
			if($in{'export'}){
				# Warehouse ID,Warehouse,Product ID,UPC,Model/Name,Cost,Total,Assigned,Available";
				print "$rec->{'ID_warehouses'},$rec->{'Warehouse'},".&format_sltvid($rec->{'ID_products'}).",$rec->{'UPC'},$rec->{'Name'},$sltvcost,$rec->{'Quantity'},$inv_assigned,".($rec->{'Quantity'} - $inv_assigned)."\r\n";	
			}else{
				$va{'searchresults'} .= qq|
					<tr bgcolor='$c[$d]' $txtlink>
						<td class='smalltext'>(|.$rec->{'ID_warehouses'}.qq|) |.$rec->{'Warehouse'}.qq|</td>
						<td class='smalltext' valign='top'>|.&format_sltvid($rec->{'ID_products'}).qq|</td>
						<td class='smalltext' valign='top'>|.$rec->{'UPC'}.qq|</td>
						<td class='smalltext'>|.$rec->{'Name'}.qq|</td>
						<td class='smalltext' valign='top' align='right'>|.&format_price($sltvcost).qq|</td>
						<td class='smalltext' valign='top' align='right'>|.&format_number($rec->{'Quantity'}).qq|</td>
						<td class='smalltext' valign='top' align='right'>|.&format_number($inv_assigned).qq|</td>
						<td class='smalltext' valign='top' align='right'>|.&format_number($rec->{'Quantity'} - $inv_assigned).qq|</td>
					</tr>\n|;
			}
		}
	
	}else{
		$va{'pageslist'} = 1;
		$va{'searchresults'} = qq|
			<tr>
				<td colspan='4' align='center'>|.&trans_txt('search_nomatches').qq|</td>
			</tr>\n|;
	}

	if($in{'print'}){
		print "Content-type: text/html\n\n";
		print &build_page('opr_warehouse_inv_loc.html');
	}elsif($in{'export'}){
		return;
	}else{
		print "Content-type: text/html\n\n";
		print &build_page('opr_warehouse_inv_loc.html');
	}
}

#############################################################################
#############################################################################
#   Function: opr_warehouses_inventory_locations
#
#       Es: Inventario Completo de almacenes por gaveta
#       En: Full inventory in warehouses by locations
#
#    Created on: 2013-04-26
#
#    Author: Alejandro Diaz
#
#    Modifications:
#
#        - Modified on **: 06/08/2015 Alejandro Diaz - Se optimizan consultas
#
#   Parameters:
#
#
#  Returns:
#
#      - 
#
#   See Also:
#
#      <>
#
sub opr_warehouses_inventory_locations {
#############################################################################
#############################################################################
	# Verificamos si se requiere filtrar por Warehouse o Location
		
	if ($in{'onlyphysical'}){
		$addsql = " AND sl_warehouses.Type='Physical' ";
		$va{'addtitle'} .= " (Only Physical) ";
	}
	if (int($in{'id_warehouses'}) > 0){
		$addsql .= " AND sl_warehouses_location.ID_warehouses='$in{'id_warehouses'}' ";
		$va{'addtitle'} .= " ($in{'id_warehouses'}) ";
		$va{'addtitle'} .= &load_db_names('sl_warehouses','ID_warehouses',$in{'id_warehouses'},'[Name]');
	}
	if (int($in{'id_locations'}) > 0){
		$addsql .= " AND sl_locations.ID_locations='$in{'id_locations'}' ";
		$va{'addtitle'} .= ' ' if ($addtitle ne '');
		$va{'addtitle'} .= ':'.&load_db_names('sl_locations','ID_locations',$in{'id_locations'},'[Code]');
	}
	$addsql .= ($in{'notempty'})? ' AND Quantity > 0 ':'';

	$va{'td_cost'} = '';
	my $sql_field_cost = '';
	my $sql_lft_join_cost = '';
	my $sql_group_cost = '';
	if( $cfg{'show_cost_rpt_inv'} and $cfg{'show_cost_rpt_inv'} == 1 ){
		$va{'td_cost'} = '<td class="menu_bar_title">Cost</td>';
		$sql_field_cost = ', sl_skus_cost.Cost';
		$sql_lft_join_cost = 'LEFT JOIN sl_skus_cost ON sl_skus_cost.ID_products=sl_warehouses_location.ID_products';
		$sql_group_cost = ', sl_skus_cost.Cost';
	}

	my $sql = "SELECT 
					sl_warehouses.ID_warehouses
					, sl_warehouses.Name as Warehouse
					, sl_warehouses_location.Location
					, sl_warehouses_location.ID_products
					, sl_skus.UPC
					, CONCAT(sl_parts.Model,'/',sl_parts.Name)Description
					, SUM(sl_warehouses_location.Quantity)Quantity
					, sl_categories.Title AS Category
					, sl_warehouses.Type
					$sql_field_cost
				FROM sl_warehouses_location 
					INNER JOIN sl_parts ON (400000000+sl_parts.ID_parts) = sl_warehouses_location.ID_products
					INNER JOIN sl_skus ON sl_skus.ID_sku_products=sl_warehouses_location.ID_products
					INNER JOIN sl_warehouses ON sl_warehouses_location.ID_warehouses=sl_warehouses.ID_warehouses
					INNER JOIN sl_locations ON sl_locations.Code=sl_warehouses_location.Location and sl_warehouses.ID_warehouses=sl_locations.ID_warehouses
					LEFT JOIN sl_categories ON sl_parts.ID_categories=sl_categories.ID_categories
					$sql_lft_join_cost
				WHERE 1 $addsql
				GROUP BY sl_warehouses_location.ID_warehouses, sl_warehouses_location.ID_products, sl_warehouses_location.Location $sql_group_cost
				ORDER BY sl_warehouses_location.ID_warehouses, sl_warehouses_location.ID_products, sl_warehouses_location.Location";
				my ($sth) = &Do_SQL("SELECT count(*) FROM ($sql) as rows");
	$va{'matches'} = $sth->fetchrow();
	my $output;

	if ($va{'matches'}>0){
		
		$va{'options'} = qq|&nbsp;&nbsp;<a href="javascript:prnwin('[va_script_url]?cmd=[in_cmd]&seacrh=1&id_warehouses=[in_id_warehouses]&print=1')"><img src='[va_imgurl]/[ur_pref_style]/b_print.png' title='Print' alt='' border='0'></a>|;
		
		my $add_limit;
		if(!$in{'print'} and !$in{'export'}){
			($va{'pageslist'},$qs) = &pages_list($in{'nh'},"/cgi-bin/mod/$usr{'application'}/admin",$va{'matches'},$usr{'pref_maxh'});
			my (@c) = split(/,/,$cfg{'srcolors'});
			(!$in{'nh'}) and ($in{'nh'}=1);
			$first = ($in{'nh'} - 1) * $usr{'pref_maxh'};

			$add_limit = "LIMIT $first,$usr{'pref_maxh'};";
		}
		
		$sql .= " ".$add_limit;

		$sth_det = &Do_SQL($sql);
		while ($rec = $sth_det->fetchrow_hashref){

			$txtlink = '';
			# $sltvcost = &load_sltvcost($rec->{'ID_products'});
			$d = 1 - $d;

			$namemodel=$rec->{'Description'};
			$prdlink = "/cgi-bin/mod/".$usr{'application'}."/dbman?cmd=mer_parts&view=".substr($rec->{'ID_products'},5,4);
			$txtlink = qq|onmouseover='m_over(this)' onmouseout='m_out(this)' onClick=\"trjump('$prdlink')\"	| if(!$in{'print'} and !$in{'export'});
			
			if($in{'export'}){
				$namemodel =~	s/<br>|,/ /g;
				$output .= qq|"$rec->{'ID_warehouses'}","$rec->{'Warehouse'}","$rec->{'Type'}","$rec->{'Location'}","$rec->{'ID_products'}","$rec->{'UPC'}","$rec->{'Description'}","$rec->{'Category'}","$rec->{'Quantity'}"|;
				if( $cfg{'show_cost_rpt_inv'} and $cfg{'show_cost_rpt_inv'} == 1 ){
					$output .= qq|,"$rec->{'Cost'}"|;
				}
				$output .= qq|\r\n|;
			}else{
				$va{'searchresults'} .= qq|
					<tr bgcolor='$c[$d]' $txtlink>
						<td class='smalltext'>(|.$rec->{'ID_warehouses'}.qq|) |.$rec->{'Warehouse'}.qq|</td>
						<td class='smalltext'>|.$rec->{'Type'}.qq|</td>
						<td class='smalltext'>|.$rec->{'Location'}.qq|</td>
						<td class='smalltext' valign='top'>|.&format_sltvid($rec->{'ID_products'}).qq|</td>
						<td class='smalltext' valign='top'>|.$rec->{'UPC'}.qq|</td>
						<td class='smalltext'>|.$rec->{'Description'}.qq|</td>
						<td class='smalltext'>|.$rec->{'Category'}.qq|</td>
						<td class='smalltext' valign='top' align='right'>|.&format_number($rec->{'Quantity'}).qq|</td>|;
				if( $cfg{'show_cost_rpt_inv'} and $cfg{'show_cost_rpt_inv'} == 1 ){
					$va{'searchresults'} .= qq|
						<td class='smalltext' style="text-align: right;">|.&format_price($rec->{'Cost'}).qq|</td>|;
				}
				$va{'searchresults'} .= qq|
					</tr>\n|;
			}
		}
	
	}else{
		$va{'pageslist'} = 1;
		$va{'searchresults'} = qq|
			<tr>
				<td colspan='4' align='center'>|.&trans_txt('search_nomatches').qq|</td>
			</tr>\n|;
	}

	if ($in{'export'}){
		$filename = $cfg{'app_title'}."_inventory";
		$filename .= ($in{'id_warehouses'})? "_$in{'id_warehouses'}":"";
		$filename =~ s/\ //g;

		print "Content-type: application/octet-stream\n";
		print "Content-disposition: attachment; filename=$filename.csv\n\n";
		if( $cfg{'show_cost_rpt_inv'} and $cfg{'show_cost_rpt_inv'} == 1 ){
			print qq|"ID WAREHOUSE","WAREHOUSE","TYPE","LOCATION","ID PRODUCT","UPC","MODEL/NAME","CATEGORY","QUANTITY","COST"\r\n|;
		}else{
			print qq|"ID WAREHOUSE","WAREHOUSE","TYPE","LOCATION","ID PRODUCT","UPC","MODEL/NAME","CATEGORY","QUANTITY"\r\n|;
		}
		print $output;
	}else{
		print "Content-type: text/html\n\n";
		print &build_page('opr_warehouse_inv_loc.html');
	}
}

sub opr_warehouses_inv_wlist {
# --------------------------------------------------------
# Forms Involved: 
# Created on: unknown
# Parameters 
# Last Modified on: 07/01/2008
# Last Modified by: MCC C Gabriel Varela S.
# Description : Se agrega parte para mostrar informacion de partes
# Last Modified RB: 12/05/08  12:41:00 - Se agrega opcion de impresion y exportacion de inventario por warehouse
 
	## Checking Permission
	my ($namemodel,$sth,$prdlink,$txtlink);

	if ($in{'id_warehouses'}){
		my ($sth) = &Do_SQL("SELECT COUNT(*) FROM sl_warehouses_location WHERE ID_warehouses='$in{'id_warehouses'}' AND Quantity>0;");
		$va{'matches'} = $sth->fetchrow();
		if ($va{'matches'}>0){
			
			$va{'options'} = qq|&nbsp;&nbsp;<a href="javascript:prnwin('[va_script_url]?cmd=[in_cmd]&seacrh=1&id_warehouses=[in_id_warehouses]&print=1')"><img src='[va_imgurl]/[ur_pref_style]/b_print.png' title='Print' alt='' border='0'></a>|;
			
			if(!$in{'print'} and !$in{'export'}){
				($va{'pageslist'},$qs) = &pages_list($in{'nh'},"/cgi-bin/mod/$usr{'application'}/admin",$va{'matches'},$usr{'pref_maxh'});
				my (@c) = split(/,/,$cfg{'srcolors'});
				(!$in{'nh'}) and ($in{'nh'}=1);
				$first = ($in{'nh'} - 1) * $usr{'pref_maxh'};	
				$sth = &Do_SQL("SELECT *,SUM(Quantity) AS Qty FROM sl_warehouses_location WHERE ID_warehouses='$in{'id_warehouses'}' GROUP BY ID_products HAVING Qty > 0 LIMIT $first,$usr{'pref_maxh'};");
			}else{
				$sth = &Do_SQL("SELECT *,SUM(Quantity) AS Qty FROM sl_warehouses_location WHERE ID_warehouses='$in{'id_warehouses'}' GROUP BY ID_products HAVING Qty > 0;");
			}
			
			if($in{'export'}){
				print "Content-type: application/octet-stream\n";
				print "Content-disposition: attachment; filename=inventory_$in{'id_warehouses'}.csv\n\n";
				print  "Product ID,Model/Name,Quantity,Cost,Total\r\n";
			}
			
			while ($rec = $sth->fetchrow_hashref){
				$txtlink = '';
				my $cost_adj = 0;
				($sltvcost, $cost_adj) = &load_sltvcost($rec->{'ID_products'});
				$d = 1 - $d;
				if ($rec->{'ID_products'} =~ /^1/){
					$namemodel=&load_db_names('sl_products','ID_products',substr($rec->{'ID_products'},3,6),'[Model]<br>[Name]');
					$prdlink = "/cgi-bin/mod/admin/dbman?cmd=mer_products&view=".substr($rec->{'ID_products'},3,6);
				}else{
					$namemodel=&load_db_names('sl_parts','ID_parts',substr($rec->{'ID_products'},5,4),'[Model]<br>[Name]')	if length($rec->{'ID_products'}) == 9;
					$namemodel = 'N/A' if (!$namemodel);
					$prdlink = "/cgi-bin/mod/".$usr{'application'}."/dbman?cmd=mer_parts&view=".substr($rec->{'ID_products'},5,4);
				}
				$txtlink = qq|onmouseover='m_over(this)' onmouseout='m_out(this)' onClick=\"trjump('$prdlink')\"	| if(!$in{'print'} and !$in{'export'});
				
				if($in{'export'}){
					$namemodel =~	s/<br>|,/ /g;
					print &format_sltvid($rec->{'ID_products'}).",$namemodel,$rec->{'Qty'},$sltvcost,".($sltvcost*$rec->{'Qty'})."\r\n";	
				}else{
					$va{'searchresults'} .= qq|
						<tr bgcolor='$c[$d]' $txtlink>
							<td class='smalltext' valign='top'>|.&format_sltvid($rec->{'ID_products'}).qq|</td>
							<td class='smalltext'>|.$namemodel.qq|</td>
							<td class='smalltext' valign='top' align='right'>|.&format_number($rec->{'Qty'}).qq|</td>
							<td class='smalltext' valign='top' align='right'>|.&format_price($sltvcost).qq|</td>
							<td class='smalltext' valign='top' align='right'>|.&format_price($sltvcost*$rec->{'Qty'}).qq|</td>
						</tr>\n|;
				}
			}
		}else{
			$va{'pageslist'} = 1;
			$va{'searchresults'} = qq|
				<tr>
					<td colspan='4' align='center'>|.&trans_txt('search_nomatches').qq|</td>
				</tr>\n|;
		}
		if($in{'print'}){
			print "Content-type: text/html\n\n";
			print &build_page('opr_warehouses_inv_wlist.html');
		}elsif($in{'export'}){
			return;
		}else{
			print "Content-type: text/html\n\n";
			print &build_page('opr_warehouse_invdet.html');
		}	
	}else{
		&opr_inventory;
	}
}

sub opr_warehouses_inv_file {
# --------------------------------------------------------
# Export master File 
#print "Content-type: text/html\n\n";
#print "<pre>";
# Last Modified on: 11/10/08 17:59:54
# Last Modified by: MCC C. Gabriel Varela S: Se corrige para tomar la cantidad como suma
	print "Content-type: application/vnd.ms-excel\n";
	print "Content-disposition: attachment; filename=masterinventory$in{'id_warehouses'}.csv\n\n";
	my (@cols) = ('Item ID','Name','Choices','Status','Warehouse','In Stock','Cost');
	print '"'.join('","', @cols)."\"\n";
	my ($rec,$skus,$warehouse,$qty,$line_prn);

	my $addsql = $in{'id_warehouses'} ? " AND ID_warehouses = '".$in{'id_warehouses'}."' " : ''; 


	
	################################################
	################ PARTS
	################################################
	my ($sth) = &Do_SQL("SELECT * FROM sl_parts ORDER BY ID_parts;");
	while ($rec = $sth->fetchrow_hashref){	
		$cols[1] = $rec->{'Model'} . ' ' . $rec->{'Name'};
		$cols[1] =~ s/"//g; #"
		$cols[3] = $rec->{'Status'};

		my ($sth2) = &Do_SQL("SELECT COUNT(*) FROM sl_skus WHERE ID_products=$rec->{'ID_parts'} ORDER BY ID_skus;");
		$skus = $sth2->fetchrow;
		
		if($skus > 0){
			my ($sth2) = &Do_SQL("SELECT * FROM sl_skus WHERE ID_products=$rec->{'ID_parts'} ORDER BY ID_skus;");
			while ($skus = $sth2->fetchrow_hashref){
				$cols[0] = &format_sltvid($skus->{'ID_sku_products'});
	
				$cols[2] = "$skus->{'choice1'},$skus->{'choice2'},$skus->{'choice3'},$skus->{'choice4'}";
				$cols[2] =~ s/,,|,$|"|'//g; #";
				(!$cols[2]) and ($cols[2] = '---'); 

				my $cost_adj = 0;

				my ($sth3) = &Do_SQL("SELECT ID_warehouses,sum(Quantity) FROM sl_warehouses_location WHERE ID_products=$skus->{'ID_sku_products'} $addsql GROUP BY ID_warehouses;");
				while (($warehouse,$qty) = $sth3->fetchrow_array()){
					$cols[4] = $warehouse; 
					$cols[5] = $qty;
					($cols[6],$cost_adj) = &load_sltvcost($skus->{'ID_sku_products'});
					print '"'.join('","', @cols)."\"\n";
					$line_prn = 1;
				}
				if (!$line_prn and !$in{'id_warehouses'}){
					$cols[4] = '---';
					$cols[5] = 0;
					($cols[6],$cost_adj) = &load_sltvcost($skus->{'ID_sku_products'});
					print '"'.join('","', @cols)."\"\n";
				}
				$line_prn = 0;
			}
		}else{
			$cols[0] = &format_sltvid(400000000+$rec->{'ID_parts'});
			$cols[2] = '---';
			$cols[4] = '---';
			$cols[5] = 0;
			print '"'.join('","', @cols)."\"\n" if !$in{'id_warehouses'};
		}	
	}
	
}

sub show_companyinfo{

	(!$in{'id_warehouses'} and $in{'id_warehouses_batches'}) and ($in{'id_warehouses'} = &load_name('sl_warehouses_batches', 'ID_warehouses_batches',$in{'id_warehouses_batches'},'ID_warehouses'));
	$fname = $tpath."common/company_info.e".$in{'e'}.".html";
	if (-e $fname){
		$page = "company_info.e".$in{'e'}.".html";		
	}else{
		$page = "company_info.html";
	}	
	&build_page($page);	
}

sub show_companyinfo_label{
	
	(!$in{'id_warehouses'} and $in{'id_warehouses_batches'}) and ($in{'id_warehouses'} = &load_name('sl_warehouses_batches', 'ID_warehouses_batches',$in{'id_warehouses_batches'},'ID_warehouses'));
	$fname = $tpath."common/company_info_label.e".$in{'e'}.".html";
	if (-e $fname){
		$page = "company_info_label.e".$in{'e'}.".html";		
	}else{
		$page = "company_info_label.html";
	}	
	&build_page($page);	
}


sub link_to_extramodule{
#-------------------------------------------------------------------------------
# Forms Involved: 
# Created on: 07/14/13 11:45:02
# Author: CC
# Description :  
# Parameters :
	my ($link) = '';
	my ($url) = $cfg{'mod_trans_url'};
	
	$link .= qq|		
			<br>				
			<font class=sub>Custom Links</font>
			<ul>|;
	
	## Modulo de Transición
	my $count_links=0;
	if($url ne ''){
		$link .= qq|<li><a href="|.$url .qq|?e=|. $in{'e'} .qq|&slsid=|.&GetCookies($cfg{'ckname'}).qq|"class=acormenu>Mod. Transici&oacute;n</a></li>\n|;
		$count_links++;
	}

	## Modulo de Facturación
	my ($url) = $cfg{'mod_cfdi_url'};
	if($url ne ''){
		$link .= qq|<li><a href="|.$url .qq|?e=|. $in{'e'} .qq|&slsid=|.&GetCookies($cfg{'ckname'}).qq|"class=acormenu>Mod. CFDI</a></li>\n|;
		$count_links++;
	}

	## Modulo de Facturas Recibidas
	$url = $cfg{'mod_vendors_cfdi_url'};
	if($url ne ''){
		$link .= qq|<li><a href="|.$url .qq|?e=|. $in{'e'} .qq|&slsid=|.&GetCookies($cfg{'ckname'}).qq|"class=acormenu>Buz&oacute;n CFDI</a></li>\n|;
		$count_links++;
	}

	$link .= qq|</ul><br>\n|;
	$link = '' if($count_links == 0);

	return $link;
}


#############################################################################
#############################################################################
#   Function: build_addwreceipt_button
#
#       Es: Permite generar un nuevo WReceipt desde vista de PO
#       En: From PO View screen, allows to generate a new WReceipt
#
#
#    Created on: 2013-03-14
#
#    Author: _Roberto Barcenas_
#
#    Modifications:
#
#        - Modified on ** by  : 
#
#   Parameters:
#
#
#  Returns:
#
#      - 
#
#   See Also:
#
#      <view_po>
#
sub build_addwreceipt_button {
#############################################################################
#############################################################################

	my ($output);
	my ($sth) = &Do_SQL("SELECT IF(SUM(sl_purchaseorders_items.Received) < SUM(Qty) AND Status = 'In Process', 1,0) FROM sl_purchaseorders LEFT JOIN sl_purchaseorders_items USING(ID_purchaseorders) WHERE sl_purchaseorders.ID_purchaseorders = '".$in{'id_purchaseorders'}."' GROUP BY sl_purchaseorders.ID_purchaseorders;");
	my ($po_opened) = $sth->fetchrow();
	$in{'currency_exchange'} =~ s/\$|\s//g if $in{'currency_exchange'};
	my $noninventory_items = &check_non_inventory($in{'id_purchaseorders'});

	if($usr{'application'} eq 'wms' and $po_opened and !$noninventory_items){
		my $date = &get_sql_date();
		$output = qq|
					  <form action="/cgi-bin/mod/$usr{'application'}/dbman" method="post" id="awrform">
						<input type="hidden" name="cmd" value="mer_wreceipts">
						<input type="hidden" name="add" value="1">
						<input type="hidden" name="type" value="Warehouse Receipt">
						<input type="hidden" name="status" value="In Process">
						<input type="hidden" name="id_purchaseorders" value="$in{'id_purchaseorders'}">
						<input type="hidden" name="id_vendors" value="$in{'id_vendors'}">
						<input type="hidden" name="invoicedate" value="$date">
						<input type="hidden" name="currency_exchange" value="$in{'currency_exchange'}">
		
						<center><input type="button" value="|.&trans_txt('mer_po_addwreceipt').qq|" class="button" onclick="confaddwr()"></center>
							<script>
								function confaddwr(){
									if(confirm("|.&trans_txt('mer_po_addwreceipt_question').qq|")){
										document.getElementById("awrform").submit();
									}
								}
							</script>
						</form>|;
	}
	return $output;
}
#############################################################################
#############################################################################
#   Function: get_order_amountdue
#
#       Es: Permite generar un nuevo WReceipt desde vista de PO
#       En: 
#
#
#    Created on: 2013-03-14
#
#    Author: _Erik Osornio_
#
#    Modifications:
#
#        - Modified on ** by  : 
#
#   Parameters: id_order: Valor por el que se realiza la busqueda
#
#
#  Returns: total_order: Cantidad total de la orden
#
#      - 
#
#   See Also:
#
#      <view_po>
#
sub get_order_amountdue {
	my ($id_orders) = @_;

	# Obtengo el total de la orden
	my ($sth) = &Do_SQL("SELECT ifnull((SELECT SUM(Amount) FROM sl_orders_payments WHERE ID_orders='$id_orders' AND Status <> 'Cancelled' AND (captured !='Yes' OR captured IS NULL )),0)as Total;");
	my $total_order = $sth->fetchrow();

	return $total_order;
}

#############################################################################
#############################################################################
#   Function: check_non_inventory
#
#       Es: Verifica si un PO tiene non inventory
#       En: Check if a PO has "non inventory" items
#
#
#    Created on: 2013-05-14
#
#    Author: Alejandro Diaz
#
#    Modifications:
#
#        - Modified on ** by  : 
#
#   Parameters:
#
#
#  Returns:
#
#      - 
#
#   See Also:
#
#
sub check_non_inventory {
#############################################################################
#############################################################################
	my ($id_purchaseorders) = @_;	
	my ($output);
	my ($sth) = &Do_SQL("SELECT COUNT(*) FROM sl_purchaseorders_items WHERE ID_products > 499999999 AND ID_products < 599999999 AND ID_purchaseorders= '".$id_purchaseorders."';");
	my ($items_non_inventory) = $sth->fetchrow_array();

	if ($items_non_inventory > 0){
		$output = 1;
	}else{
		$output = 0;
	}
	return $output;
}

#############################################################################
#############################################################################
#   Function: bills_amount_due
#
#       Es: Obtiene el Amount Due de un bill
#       En: Gets the Amount Due of a bill
#
#
#    Created on: 2013-06-12
#
#    Author: Alejandro Diaz
#
#    Modifications:
#
#        - Modified on ** by  : 
#
#   Parameters:
#
#
#  Returns:
#
#      - 
#
#   See Also:mer_bills
#
#
sub bills_amount_due{
	my ($id_bills) = @_;
	$bill_amount_due = 0;
	
	if ($id_bills){			

		my ($sth) = &Do_SQL("SELECT IFNULL(Amount - (
				SELECT IFNULL(SUM(AmountPaid),0)as Amount 
					FROM sl_banks_movrel 
					INNER JOIN sl_banks_movements USING(ID_banks_movements) 
					WHERE tablename='bills' 
					AND tableid=bills.ID_bills
					AND sl_banks_movements.Type='credits'
				) + (
					SELECT IFNULL(SUM(AmountPaid),0)as Amount 
					FROM sl_banks_movrel 
					INNER JOIN sl_banks_movements USING(ID_banks_movements) 
					WHERE tablename='bills' 
					AND tableid=bills.ID_bills
					AND sl_banks_movements.Type='Debits'
				) - (
					SELECT IFNULL(SUM(sl_bills_applies.Amount),0)as Amount 
					FROM sl_bills_applies 
					INNER JOIN sl_bills USING(ID_bills)
					WHERE ID_bills_applied = bills.ID_bills
					AND sl_bills.Type IN ('Deposit','Credit')
				), 0)as Amount
				FROM sl_bills as bills
				WHERE ID_bills = '".$id_bills."';");
		$bill_amount_due = $sth->fetchrow_array();
	}

	return $bill_amount_due;
}


#############################################################################
#############################################################################
#   Function: credit_amount_due
#
#       Es: Obtiene el Amount Due de un credit
#       En: Gets the Amount Due of a credit
#
#
#    Created on: 2013-06-12
#
#    Author: Alejandro Diaz
#
#    Modifications:
#
#        - Modified on ** by  : Arturo Hernandez
#
#   Parameters:
#
#
#  Returns:
#
#      - 
#
#   See Also:mer_bills
#
#
sub credit_amount_due{
	my ($id_bills) = @_;
	$credit_amount_due = 0;
	
	if ($id_bills){			

		my ($sth) = &Do_SQL("SELECT IFNULL(Amount - (
				SELECT IFNULL(SUM(AmountPaid),0)as Amount 
					FROM sl_banks_movrel 
					INNER JOIN sl_banks_movements USING(ID_banks_movements) 
					WHERE tablename='bills' 
					AND tableid=bills.ID_bills
					AND sl_banks_movements.Type='credits'
				) + (
					SELECT IFNULL(SUM(AmountPaid),0)as Amount 
					FROM sl_banks_movrel 
					INNER JOIN sl_banks_movements USING(ID_banks_movements) 
					WHERE tablename='bills' 
					AND tableid=bills.ID_bills
					AND sl_banks_movements.Type='Debits'
				) - (
					SELECT IFNULL(SUM(sl_bills_applies.Amount),0)as Amount 
					FROM sl_bills_applies 
					INNER JOIN sl_bills USING(ID_bills)
					WHERE ID_bills = bills.ID_bills
					AND sl_bills.Type IN ('Deposit','Credit')
				), 0)as Amount
				FROM sl_bills as bills
				WHERE ID_bills = '".$id_bills."';");
		$credit_amount_due = $sth->fetchrow_array();
	}

	return $credit_amount_due;
}

#############################################################################
#############################################################################
#   Function: bills_pos_detection
#
#       Es: Detecta si el Bill es de POs
#       En: Detect Bills POs
#
#
#    Created on: 2013-06-18
#
#    Author: Alejandro Diaz
#
#    Modifications:
#
#        - Modified on ** by  : 
#
#   Parameters:
#
#
#  Returns:
#
#      - 
#
#   See Also:
#
#
sub bills_pos_detection{
	my ($id_bills) = @_;
	$detect = 0;
	
	if ($id_bills){			

		my ($sth) = &Do_SQL("SELECT COUNT(* ) FROM sl_bills_pos INNER JOIN sl_bills USING(ID_bills) WHERE 1 AND ID_bills='".$id_bills."';");
		$detect = $sth->fetchrow_array();
	}

	return $detect;
}

#############################################################################
#############################################################################
#   Function: bills_expenses_detection
#
#       Es: Detecta si el Bill es de Gastos
#       En: Detect Bills Expenses
#
#
#    Created on: 2013-07-09
#
#    Author: Alejandro Diaz
#
#    Modifications:
#
#        - Modified on ** by  : 
#
#   Parameters:
#
#
#  Returns:
#
#      - 
#
#   See Also:
#
#
sub bills_expenses_detection{
	my ($id_bills) = @_;
	$detect = 0;
	
	if ($id_bills){

		my ($sth) = &Do_SQL("SELECT Type, sl_bills.Amount BillAmount, SUM(sl_bills_expenses.Amount)Amount, COUNT(*) AS nlines FROM sl_bills INNER JOIN sl_bills_expenses USING(ID_bills) WHERE ID_bills='$id_bills';");
		my ($bill_type, $bill_amount, $amount_lines, $no_lines) = $sth->fetchrow_array();
		
		if ($bill_type eq 'Bill' and $no_lines > 0){
			$detect = 1;
		}
	}

	return $detect;
}

#############################################################################
#############################################################################
#   Function: bills_amount_due_by_vendor
#
#       Es: Obtiene el Amount Due de los bills de un vendor
#       En: Gets the Amount Due of a vendor
#
#
#    Created on: 2013-06-17
#
#    Author: Alejandro Diaz
#
#    Modifications:
#
#        - Modified on ** by  : 
#
#   Parameters:
#
#
#  Returns:
#
#      - 
#
#   See Also:mer_bills
#
#
sub bills_amount_due_by_vendor{
	my ($id_vendors) = @_;
	$amount_due = 0;
	
	if ($id_vendors){			

		my ($sth) = &Do_SQL("SELECT IFNULL(SUM(IFNULL(Amount - (
				SELECT IFNULL(SUM(AmountPaid),0)as Amount 
					FROM sl_banks_movrel 
					INNER JOIN sl_banks_movements USING(ID_banks_movements) 
					WHERE tablename='bills' 
					AND tableid=bills.ID_bills
					AND sl_banks_movements.Type='credits'
				) + (
					SELECT IFNULL(SUM(AmountPaid),0)as Amount 
					FROM sl_banks_movrel 
					INNER JOIN sl_banks_movements USING(ID_banks_movements) 
					WHERE tablename='bills' 
					AND tableid=bills.ID_bills
					AND sl_banks_movements.Type='Debits'
				) - (
					SELECT IFNULL(SUM(sl_bills_applies.Amount),0)as Amount 
					FROM sl_bills_applies 
					INNER JOIN sl_bills USING(ID_bills)
					WHERE ID_bills_applied = bills.ID_bills
					AND sl_bills.Type IN ('Deposit','Credit')
				), 0)), 0)as Amount
				FROM sl_bills as bills
				WHERE 1
				AND ID_vendors='".$id_vendors."'
				AND Status IN('Processed','Partly Paid');");
		$amount_due = $sth->fetchrow_array();
	}

	return $amount_due;
}

#############################################################################
#############################################################################
# Function: amount_in_words
#
# Es: Obtiene cantidades en texto para impresion en facturas y cheques
# En: 
#
# Created on: 18/06/2013 012:33:00
#
# Author: Alejandro Diaz
#
# Modifications: EO
#
# Parameters:
#
#
# Returns:Amount in words
#
#
# See Also:
#
#  Todo:
#
sub amount_in_words {
#############################################################################
#############################################################################
	my ($amount,$currency) = @_;

	if($currency eq ''){
		$currency = 'MXP';
	}

	if ($amount){
		$amount = &filter_values($amount);
		my $contents = `php ../../../httpdocs/cfdi/common/php/letras.php $amount $currency`;
		
		return $contents;
	}
	return;
}



#############################################################################
#############################################################################
#   Function: update_paymentdate
#
#       Es: Actualiza el campo Paymentdate de sl_orders_payments para una Orden
#       En: Upgrade Paymentdate of sl_orders_payments field for an Order 
#
#
#    Created on: 2013-06-28
#
#    Author: Alejandro Diaz
#
#    Modifications:
#
#        - Modified on ** by  : 
#
#   Parameters:
#
#
#  Returns:
#
#      - 
#
#   See Also: HH
#
#
sub update_paymentdate{
	my ($id_orders) = @_;
	
	if ($id_orders){
		my ($sth) = &Do_SQL("SELECT (SELECT ifnull(CreditDays,0) FROM sl_terms WHERE Type='Sales' AND Status='Active' AND Name=sl_customers.Pterms)CreditDays FROM sl_orders INNER JOIN sl_customers USING(ID_customers) WHERE 1 AND ID_orders='".$id_orders."';");
		my $creditdays = $sth->fetchrow_array();
		$creditdays = 0 if !$creditdays;

		my ($sth) = &Do_SQL("UPDATE sl_orders_payments SET Paymentdate = DATE_ADD(CURDATE(), INTERVAL ".$creditdays." DAY) WHERE ID_orders = '".$id_orders."' AND (Captured<>'Yes' OR Captured IS NULL);");
	}

	return;
}

#############################################################################
#############################################################################
#   Function: services_tax
#
#       Es: Calcula la informacion de precio e impuestos de un servicio
#       En: Calculate information about price and service tax
#
#
#    Created on: 08/10/2013 11:00
#
#    Author: Alejandro Diaz
#
#    Modifications:
#
#        - Modified on 
#
#   Parameters:
#      - 
#
#  Returns:
#
#      - 
#
#   See Also:
#
#
sub services_tax{
#############################################################################
#############################################################################
	my ($id_services) = @_;
	my $tax_serv = 0;
	my $price = 0;
	my $tax_rate = 0;
	if ($id_services){

		$price = &load_name ('sl_services','ID_services',$id_services,'SPrice');
			    
	    if ($cfg{'calc_tax_in_services'} and $cfg{'calc_tax_in_services'}==1){
	        $tax_rate = &load_name ('sl_services','ID_services',$id_services,'Tax');
	        $tax_rate = ($tax_rate/100);

	        if ($cfg{'servtaxtype'} and $cfg{'servtaxtype'} eq 'net'){
	            $tax_serv = $price * $tax_rate;
	            $price = $price;
	        }else{
	        	$tax_serv = $price - ($price / (1 + $tax_rate));
	        	$tax_serv = &round($tax_serv, $sys{'fmt_curr_decimal_digits'});

	        	$price =  &round($price, $sys{'fmt_curr_decimal_digits'});
	        	$price -= $tax_serv;

	        	### Recalculo de taxes
	        	$tax_serv = $price * $tax_rate;
	        	$tax_serv = &round($tax_serv, $sys{'fmt_curr_decimal_digits'});
	        }
	    }
	}

	# &cgierr('->'.$price.'->'.$tax_serv.'->'.$tax_rate);
	return ($price,$tax_serv,$tax_rate);

}

#############################################################################
#############################################################################
#   Function: ref_banco_azteca
#
#       Es: Calcula la referencia para el pago en Banco Azteca
#       En: Calculates the payment reference for Banco Azteca
#
#
#    Created on: 23/10/2013 11:00
#
#    Author: Alejandro Diaz
#
#    Modifications:
#
#        - Modified on 
#
#   Parameters:
#      - 
#
#  Returns:
#
#      - 
#
#   See Also:
#
#
sub ref_banco_azteca{
#############################################################################
#############################################################################
	my ($id_orders) = @_;
	$id_orders = "$in{'id_orders'}" if (!$id_orders);
	$id_banks = "10";
	my $temp;
	if ($id_orders > 0){
		$temp = $id_banks.$id_orders;

		@string = split //, $temp;
		my $flag=3;
		my $result;
		my $dv;
		my $sum=0;
		for (0..$#string){
			my $mult = $flag * int($string[$_]);
			$sum += $mult;
			$result .= "$mult";
			$flag = ($flag == 1)? 3 : 1 ;
		}

		$dv = (($sum / 10 ) + 1);
		$dv = int($dv) * 10;
		$dv = $dv - $sum;
		$dv = 0 if($dv > 9);

		$temp = $id_banks.$id_orders."$dv";
	}

	return $temp;

}

#############################################################################
#############################################################################
#   Function: get_edit_returns_exchange_lines
#
#       Es: Devuelve las lineas de un exchange de sl_vars o sl_orders_products
#       En: 
#
#
#    Created on: 21/04/2014 15:00
#
#    Author: _RB_
#
#    Modifications:
#
#        - Modified on 
#
#   Parameters:
#      - 
#
#  Returns:
#
#      - 
#
#   See Also:
#
#
sub get_edit_returns_exchange_lines{
#############################################################################
#############################################################################

	my ($id_returns) =@_;
	my ($str_out);
	my $sum_total = 0;
	$va{'div_height'} = 0;

	my ($sth) =  &Do_SQL("SELECT ID_vars, VValue
	                    FROM sl_vars 
	                    WHERE VName = 'Exchange Process'
	                    AND Subcode = '$id_returns'
	                    ORDER BY ID_vars;");
	while(my($idri, $subcode) = $sth->fetchrow()){

		$va{'div_height'} += 50;
		my ($this_offer,$this_price,$this_tax,$this_shp,$this_shptax) = split(/:/, $subcode);

		my $this_total = round($this_price + $this_tax + $this_shp + $this_shptax,2);
		$sum_total += $this_total;
		my $pname = substr($this_offer,0,1) ne '6' ? &load_name('sl_products','ID_products',substr($this_offer,-6),'Name') : &load_name('sl_services','ID_services',substr($this_offer,-4),'Name');
		$str_out .= qq|<tr id="row-$idai">\n
							<td><img src="/sitimages/default/b_drop.png" class="rdrop" id="drop-$idri" style="cursor:pointer" title="Drop $idri"></td>\n
							<td class='smalltext' valign='top' nowrap><b>|. $pname ." </b>&nbsp; (<a href='/cgi-bin/mod/$usr{'application'}/dbman?cmd=mer_products&view=".substr($this_offer,-6)."'>". &format_sltvid($this_offer) .qq|</a>)<br>|;

		my ($sth) = &Do_SQL("SELECT 
						sl_parts.ID_parts
						, Model
						, Name
						, (SELECT UPC FROM sl_skus WHERE ID_sku_products=400000000+sl_parts.ID_parts) AS UPC 
						, SUM(Qty)AS Qty
						FROM sl_skus INNER JOIN sl_skus_parts USING(ID_sku_products)
						INNER JOIN sl_parts USING(ID_parts) 
						WHERE sl_skus.ID_sku_products = '$this_offer';");
		while ($rec = $sth->fetchrow_hashref){

			(!$rec->{'UPC'}) and ($rec->{'UPC'} = '---');
			$str_out .= qq|   &nbsp;&nbsp;&nbsp;&nbsp;$rec->{'Qty'} x $rec->{'Name'}&nbsp;&nbsp;\|&nbsp;&nbsp;ID: <a href='/cgi-bin/mod/$usr{'application'}/dbman?cmd=mer_parts&view=$rec->{'ID_parts'}'>|.&format_sltvid(400000000+$rec->{'ID_parts'}).qq|</a>&nbsp;&nbsp;\|<b>&nbsp;&nbsp;<b>UPC:</b> $rec->{'UPC'}<br>\n|;

		}

		$str_out .= qq|</td>\n 
						<td class='menu_bar' valign='top' align="right" nowrap>|. &format_price($this_price) .qq|</td>\n
						<td class='menu_bar' valign='top' align="right" nowrap>|. &format_price($this_tax) .qq|</td>\n
						<td class='menu_bar' valign='top' align="right" nowrap>|. &format_price($this_shp) .qq|</td>\n
						<td class='menu_bar' valign='top' align="right" nowrap>|. &format_price($this_shptax) .qq|</td>\n
						<td class='menu_bar' valign='top' align="right" nowrap>|. &format_price($this_total) .qq|</td>\n
					</tr>\n|;

	}


	if($str_out) {
		$str_out = qq|<table id="tbl-id-in" width="98%" align="center" cellspacing="2" cellpadding="2" class="formtable">\n 
						<tr>\n 
							<td align="center" class="menu_bar_title">&nbsp;</td>\n 
							<td align="center" class="menu_bar_title">Product Info</td>\n 
							<td align="center" class="menu_bar_title">Price</td>\n 
							<td align="center" class="menu_bar_title">Product Tax</td>\n 
							<td align="center" class="menu_bar_title">S & H</td>\n 
							<td align="center" class="menu_bar_title">S & H Tax</td>\n 
							<td align="center" class="menu_bar_title">Total</td>\n 
						</tr>\n
						$str_out
						<tr>\n 
							<td colspan="6" align="right" class="smalltext">Total</td>\n 
							<td class="smalltext" align="right">|.&format_price($sum_total).qq|</td>\n 
						</tr>\n
					</table>\n|;
	}

	return $str_out;

}		

#############################################################################
#############################################################################
#   Function: check_batches
#
#       Es: Devuelve el estado de las remesas de una orden.
#       En: 
#
#
#    Created on: 21/04/2014 15:00
#
#    Author: Arturo Hernandez
#
#    Modifications:
#
#        - Modified on 
#
#   Parameters:
#      - 
#
#  Returns:
#
#      - 
#
#   See Also:
#
#
sub check_batches{
#############################################################################
#############################################################################
	my ($id_orders) = @_;
	if ($id_orders > 0){
		my ($sth) = &Do_SQL("select 
							SUM(if ( sl_warehouses_batches_orders.ID_warehouses_batches > 0 , 1, 0))inbatch
							, sl_warehouses_batches_orders.ID_warehouses_batches
							from sl_orders_products 
							left join sl_warehouses_batches_orders 
								on sl_orders_products.ID_orders_products=sl_warehouses_batches_orders.ID_orders_products
							WHERE sl_warehouses_batches_orders.Status='In Fulfillment'
							AND sl_orders_products.ID_orders='".$id_orders."';");
		my ($batch_total) = $sth->fetchrow();

		if($batch_total > 0){
			return 1;
		}else{
			return 0;
		}
	}
}

############################################################################################
############################################################################################
#	Function: warehouses_batches_by_order
#   		Get ID_warehouses_batches if exists
#
#	Created by:
#		Ing. Alejandro Diaz
#
#	Modified By:
#
#   	Parameters:
#		- ID_orders
#
#   	Returns:
#		- ID_warehouses_batches
#
#   	See Also:
#
sub warehouses_batches_by_order{
############################################################################################
############################################################################################

    my ($id_orders)=@_;

	my ($sth) = &Do_SQL("SELECT sl_warehouses_batches_orders.ID_warehouses_batches
		FROM sl_warehouses_batches_orders 
		INNER JOIN sl_orders_products ON sl_warehouses_batches_orders.ID_orders_products=sl_orders_products.ID_orders_products
		WHERE sl_orders_products.ID_orders='$id_orders'
		ORDER BY sl_warehouses_batches_orders.ID_warehouses_batches_orders DESC
		LIMIT 1");
	my($id_warehouses_batches) = $sth->fetchrow();

	return $id_warehouses_batches;

}

############################################################################################
############################################################################################
#	Function: repmans_replication
#   	Indica si esta activado el parametro use_ext_host_for_repmans en el general
#
#	Created by:
#		Ing. Alejandro Diaz
#
#	Modified By:
#
#   	Parameters:
#
#   	Returns:
#
#   	See Also:
#
sub repmans_replication{
############################################################################################
############################################################################################
	return ($cfg{'use_ext_host_for_repmans'} and $cfg{'use_ext_host_for_repmans'} == 1)? qq|<span style="padding:0 10px;"><img alt="Reports from replication enabled" title="Reports from replication enabled" src="[va_imgurl]/reprep1.gif" width="9" height="9"></span>|:'';
}

############################################################################################
############################################################################################
#	Function: get_company_info
#   	Indica si esta activado el parametro use_ext_host_for_repmans en el general
#
#	Created by:
#		05-09-2014::Ing. Alejandro Diaz
#
#	Modified By:
#
#   	Parameters:
#
#   	Returns:
#
#   	See Also:
#
sub get_company_info{
############################################################################################
############################################################################################
	$sql = "SELECT RFC,Name,Regime from cu_company_legalinfo where PrimaryRecord='Yes'";
	my ($sth) = &Do_SQL($sql);
	my ($rec) = $sth->fetchrow_hashref();

	$va{'company_name'} = $rec->{'Name'};
	$va{'company_regime'} = $rec->{'Regime'};
	$va{'company_rfc'} = $rec->{'RFC'};

	$sql = "SELECT Street,Num,Num2,Urbanization,District,City,State,Country,Zip from cu_company_addresses where PrimaryRecord='Yes'";
	my ($sth) = &Do_SQL($sql);
	my ($rec) = $sth->fetchrow_hashref();

	$va{'company_street'} = $rec->{'Street'};
	$va{'company_num'} = $rec->{'Num'};
	$va{'company_num2'} = $rec->{'Num2'};
	$va{'company_urbanization'} = $rec->{'Urbanization'};
	$va{'company_district'} = $rec->{'District'};
	$va{'company_city'} = $rec->{'City'};
	$va{'company_state'} = $rec->{'State'};
	$va{'company_country'} = $rec->{'Country'};
	$va{'company_zip'} = $rec->{'Zip'};
	
}

############################################################################################
############################################################################################
#	Function: creditmemos_status
#   	Genera de forma dinamica el selector de estatus para creditmemos
#
#	Created by:
#		24-11-2014::Ing. Alejandro Diaz
#
#	Modified By:
#
#   	Parameters:
#
#   	Returns:
#
#   	See Also:
#
sub creditmemos_status{
############################################################################################
############################################################################################
	return $va{'creditmemos_status'} = ($in{'search'})?'[bc_status@sl_creditmemos]':qq|<input type='hidden' name='status' value='[in_status]'>[in_status]|;
}

sub parts_productions_status{
############################################################################################
############################################################################################
	return $result = ($in{'search'})?'[bc_status@sl_parts_productions]':qq|<input type='hidden' name='status' value='[in_status]'>[in_status]|;
}

############################################################################################
############################################################################################
#	Function: orders_status
#   	Genera de forma dinamica el selector de main estatus para orders
#
#	Created by:
#		24-11-2014::Ing. Alejandro Diaz
#
#	Modified By:
#		24-11-2014::Ing. Gilberto Quirino
#
#   	Parameters:
#
#   	Returns:
#
#   	See Also:
#
sub orders_status{
############################################################################################
############################################################################################
	return $va{'orders_status'} = ($in{'search'})?'[bc_status@sl_orders]<span style="border-top: 1px dotted gray; display: block; min-width: 200px; padding: 1px 0 1px 0;"></span>':qq|<input type='hidden' name='status' value='[in_status]'>[in_status]|;
}


############################################################################################
############################################################################################
#	Function: orders_statuspay
#   	Genera de forma dinamica el selector de payment estatus para orders
#
#	Created by:
#		24-11-2014::Ing. Alejandro Diaz
#
#	Modified By:
#		24-11-2014::Ing. Gilberto Quirino
#
#   	Parameters:
#
#   	Returns:
#
#   	See Also:
#
sub orders_statuspay{
############################################################################################
############################################################################################
	return $va{'orders_statuspay'} = ($in{'search'})?'[bc_statuspay@sl_orders]<span style="border-top: 1px dotted gray; display: block; min-width: 200px; padding: 1px 0 1px 0;"></span>':qq|<input type='hidden' name='statuspay' value='[in_statuspay]'>[in_statuspay]|;
}

############################################################################################
############################################################################################
#	Function: orders_statusprd
#   	Genera de forma dinamica el selector de product estatus para orders
#
#	Created by:
#		24-11-2014::Ing. Alejandro Diaz
#
#	Modified By:
#		24-11-2014::Ing. Gilberto Quirino
#
#   	Parameters:
#
#   	Returns:
#
#   	See Also:
#
sub orders_statusprd{
############################################################################################
############################################################################################
	return $va{'orders_statusprd'} = ($in{'search'})?'[bc_statusprd@sl_orders]':qq|<input type='hidden' name='statusprd' value='[in_statusprd]'>[in_statusprd]|;
}

############################################################################################
############################################################################################
#	Function: customers_status
#   	Genera de forma dinamica el selector de estatus para customers
#
#	Created by:
#		01-05-2015::Ing. Gilberto Quirino
#
#	Modified By:
#
#   	Parameters:
#
#   	Returns:
#
#   	See Also:
#
sub order_postdate_link{
############################################################################################
############################################################################################
	my $sth = &Do_SQL("SELECT Status, StatusPay FROM sl_orders WHERE ID_orders=".$in{'view'}.";");
	my ($st_order, $st_pay) = $sth->fetchrow_array();

	my $link = '';
	if( $st_order eq 'New' or $st_order eq 'Void' ){
		my $sth = &Do_SQL("SELECT COUNT(*) 
							FROM sl_orders_payments 
							WHERE ID_orders=".$in{'view'}." 
								AND (AuthCode='' OR AuthCode IS NULL) 
								AND (Captured='No' OR Captured='' OR Captured IS NULL) 
								AND (CapDate='0000-00-00' OR CapDate IS NULL) 
								AND Status IN('Pending','Approved');");
		my $num_pmts = $sth->fetchrow();
		if( $num_pmts and $num_pmts == 1 ){
			$link = '<a href="/cgi-bin/common/apps/e_orders?cmd=postdate&id_orders='.$in{'id_orders'}.'&ap='.$usr{'application'}.'"  class="fancy_modal_iframe">
							<img src="[va_imgurl]/[ur_pref_style]/postdate.png" title="Post-Dated Order" alt="Post-Dated_Order" border="0">
						</a>';
		}
	}

	return $link;
}

############################################################################################
############################################################################################
#	Function: customers_status
#   	Genera de forma dinamica el selector de estatus para customers
#
#	Created by:
#		24-11-2014::Ing. Alejandro Diaz
#
#	Modified By:
#		24-11-2014::Ing. Gilberto Quirino
#
#   	Parameters:
#
#   	Returns:
#
#   	See Also:
#
sub customers_status{
############################################################################################
############################################################################################
	return $va{'customers_status'} = ($in{'search'})?'[bc_status@sl_customers]':qq|<input type='hidden' name='status' value='[in_status]'>[in_status]|;
}


############################################################################################
############################################################################################
#	Function: crmtickets_status
#   	Genera de forma dinamica el selector de estatus para crmtickets
#
#	Created by:
#		24-11-2014::Ing. Alejandro Diaz
#
#	Modified By:
#		24-11-2014::Ing. Gilberto Quirino
#
#   	Parameters:
#
#   	Returns:
#
#   	See Also:
#
sub crmtickets_status{
############################################################################################
############################################################################################
	return $va{'crmtickets_status'} = ($in{'search'})?'[bc_status@sl_crmtickets]':qq|<input type='hidden' name='status' value='[in_status]'>[in_status]|;
}

############################################################################################
############################################################################################
#	Function: crmtickets_select_type
#   	Genera de forma dinamica el combobox para el tipo de ticket
#
#	Created by:
#		24-11-2014::Ing. Gilberto Quirino
#
#	Modified By:
#
#
#   	Parameters:
#
#   	Returns:
#
#   	See Also:
#
sub crmtickets_select_type{
############################################################################################
############################################################################################
	my $sth = &Do_SQL("SELECT 
							ID_crmtickets_type
							, Type
							, Description
							, GroupType
							, BgColor
							, TextColor
						FROM sl_crmtickets_type 
						WHERE status=1
						ORDER BY GroupType, Description;");
	my $select = '<select name="id_crmtickets_type">';
	$select .= '<option value=""> --- </option>';
	my $group = '';

	## Se obtiene el id_crmtickets_type del ticket actual
	$id_crmtickets_type = 0;
	if( $in{'modify'} ){
		my $sthX = &Do_SQL("SELECT ID_crmtickets_type FROM sl_crmtickets WHERE ID_crmtickets=".$in{'modify'});
		$id_crmtickets_type = $sthX->fetchrow();		
	}
	while ($ref = $sth->fetchrow_hashref()) {
		if( $group ne $ref->{'GroupType'} ){
			$select .= '<optgroup style="background-color: #'.$ref->{'BgColor'}.'; padding: 5px;color: #'.$ref->{'TextColor'}.';" label="'.$ref->{'GroupType'}.'"></optgroup>';
		}

		if( $id_crmtickets_type eq $ref->{'ID_crmtickets_type'} ){
			$select .= '<option value="'.$ref->{'ID_crmtickets_type'}.'" class="ddoption" selected="selected"> '.$ref->{'Description'}.'</option>';

		}else{
			$select .= '<option value="'.$ref->{'ID_crmtickets_type'}.'" class="ddoption"> '.$ref->{'Description'}.'</option>';
		}
	
		$group = $ref->{'GroupType'};
	}
	$select .= '</select>';

	return $select;
}

############################################################################################
############################################################################################
#	Function: journalentries_status
#   	Genera de forma dinamica el selector de estatus para journalentries
#
#	Created by:
#		24-11-2014::Ing. Alejandro Diaz
#
#	Modified By:
#		24-11-2014::Ing. Gilberto Quirino
#
#   	Parameters:
#
#   	Returns:
#
#   	See Also:
#
sub journalentries_status{
############################################################################################
############################################################################################
	return $va{'journalentries_status'} = ($in{'search'})?'[bc_status@sl_journalentries]':qq|<input type='hidden' name='status' value='[in_status]'>[in_status]|;
}


############################################################################################
############################################################################################
#	Function: orders_saleschannel
#   	Genera de forma dinamica el selector para el campo Sales Channel 
#
#	Created by:
#		25-11-2014::Ing. Gilberto Quirino
#
#	Modified By:
#
#   	Parameters:
#
#   	Returns:
#
#   	See Also:
#
sub orders_saleschannel{
############################################################################################
############################################################################################
	if( $in{'search'} ){
		$va{'build_saleschannel'} = '<td class="smalltext" style="border-top: 1px dotted gray; border-bottom: 1px dotted gray;">[fc_build_checkbox_saleorigins]</td>';
	}elsif( $in{'add'} ){
		$va{'build_saleschannel'} = '<td class="smalltext" style="border-top: 1px dotted gray; border-bottom: 1px dotted gray;">[fc_build_radio_saleorigins]</td>';
	}else{
		my $sc = &load_name('sl_salesorigins','ID_salesorigins',$in{'id_salesorigins'},'Channel');
		$va{'build_saleschannel'} = '<td class="smalltext">'.$sc.'</td>';
	}

	return $va{'build_saleschannel'};
}

############################################################################################
############################################################################################
#	Function: bills_status
#   	Genera de forma dinamica del campo Status para el form bills_form
#
#	Created by:
#		25-11-2014::Ing. Gilberto Quirino
#
#	Modified By:
#
#   	Parameters:
#
#   	Returns:
#
#   	See Also:
#
sub bills_status{
############################################################################################
############################################################################################
	if( $in{'search'} ){
		return $va{'bills_status'} = '[bc_status@sl_bills]';	
	} elsif( $in{'add'} ){
		return $va{'bills_status'} = qq|<input type='hidden' name='status' value='New'>New|;
	} else {
		return $va{'bills_status'} = qq|<input type='hidden' name='status' value='[in_status]'>[in_status]|;
	}	
}

############################################################################################
############################################################################################
#	Function: accounts_status
#   	Genera de forma dinamica del campo Status para el form accounts_form
#
#	Created by:
#		20-06-2016 ISC Alejandro Diaz
#
#	Modified By:
#
#   	Parameters:
#
#   	Returns:
#
#   	See Also:
#
sub accounts_status{
############################################################################################
############################################################################################
	if( $in{'search'} ){
		return $va{'accounts_status'} = '[bc_status@sl_accounts]';	
	} elsif( $in{'add'} ){
		return $va{'accounts_status'} = qq|<input type='hidden' name='status' value='Active'>Active|;
	} else {
		return $va{'accounts_status'} = qq|<input type='hidden' name='status' value='[in_status]'>[in_status]|;
	}	
}

############################################################################################
############################################################################################
#	Function: wreceipts_status
#   	Genera de forma dinamica el campo Status para el form wreceipts_form
#
#	Created by:
#		25-11-2014::Ing. Gilberto Quirino
#
#	Modified By:
#
#   	Parameters:
#
#   	Returns:
#
#   	See Also:
#
sub wreceipts_status{
############################################################################################
############################################################################################
	if( $in{'search'} ){
		return $va{'wreceipts_status'} = '[bc_status@sl_wreceipts]';	
	} else {
		return $va{'wreceipts_status'} = qq|<input type="hidden" name="status" value="[in_status]">[in_status]|;
	}	
}

############################################################################################
############################################################################################
#	Function: skustransfers_status
#   	Genera de forma dinamica el campo Status para el form skustransfers_form
#
#	Created by:
#		25-11-2014::Ing. Gilberto Quirino
#
#	Modified By:
#
#   	Parameters:
#
#   	Returns:
#
#   	See Also:
#
sub skustransfers_status{
############################################################################################
############################################################################################
	if( $in{'search'} ){
		return $va{'skustransfers_status'} = '[bc_status@sl_skustransfers]';	
	} elsif( $in{'add'} ){
		return $va{'skustransfers_status'} = qq|<input type='hidden' name='status' value='In Progress'>In Progress|;
	} else {
		return $va{'skustransfers_status'} = qq|<input type="hidden" name="status" value="[in_status]">[in_status]|;
	}	
}

############################################################################################
############################################################################################
#	Function: manifests_status
#   	Genera de forma dinamica el campo Status para el form manifests_form
#
#	Created by:
#		25-11-2014::Ing. Gilberto Quirino
#
#	Modified By:
#
#   	Parameters:
#
#   	Returns:
#
#   	See Also:
#
sub manifests_status{
############################################################################################
############################################################################################
	if( $in{'search'} ){
		return $va{'manifests_status'} = '[bc_status@sl_manifests]';	
	} elsif( $in{'add'} ){
		return $va{'manifests_status'} = qq|<input type='hidden' name='status' value='In Progress'>In Progress|;
	} else {
		return $va{'manifests_status'} = qq|<input type="hidden" name="status" value="[in_status]">[in_status]|;
	}	
}

############################################################################################
############################################################################################
#	Function: adjustments_status
#   	Genera de forma dinamica el campo Status para el form adjustments_form
#
#	Created by:
#		25-11-2014::Ing. Gilberto Quirino
#
#	Modified By:
#
#   	Parameters:
#
#   	Returns:
#
#   	See Also:
#
sub adjustments_status{
############################################################################################
############################################################################################
	if( $in{'search'} ){
		return $va{'adjustments_status'} = '[bc_status@sl_adjustments]';	
	} elsif( $in{'add'} ){
		return $va{'adjustments_status'} = qq|<input type='hidden' name='status' value='New'>New|;
	} else {
		return $va{'adjustments_status'} = qq|<input type="hidden" name="status" value="[in_status]">[in_status]|;
	}	
}

############################################################################################
############################################################################################
#	Function: return_notices_status
#   	Genera de forma dinamica del campo Status para el form return_notices_status
#
#	Created by:
#		13-08-2015::Ing. Gilberto Quirino
#
#	Modified By:
#
#   	Parameters:
#
#   	Returns:
#
#   	See Also:
#
sub return_notices_status{
############################################################################################
############################################################################################
	if( $in{'search'} ){
		return $va{'return_not_status'} = '[bc_status@sl_return_notices]';	
	} elsif( $in{'add'} ){
		return $va{'return_not_status'} = qq|<input type='hidden' name='status' value='New'>New|;
	} else {
		return $va{'return_not_status'} = qq|<input type='hidden' name='status' value='[in_status]'>[in_status]|;
	}	
}

############################################################################################
############################################################################################
#	Function: str_pad
#   	Rellena una cadena con otra subcadena especificada para completar el tamaño 
#		requerido, similar a la función del mismo nombre de PHP
#
#	Created by:
#		25-11-2014::Ing. Gilberto Quirino
#
#	Modified By:
#
#   Parameters:
#		$string:		(obligatorio) Cadena original
#		$pad_length:	(obligatorio) Tamaño requerido para la cadena final	
#		$pad_string:	(obligatorio) Subcadena con la que se rellenará la cadena original
#		$pad_type: 		[opcional] Define de manera se rellenará la cadena original
#			-> STR_PAD_LEFT:	Relleno del lado izquierdo
#			-> STR_PAD_RIGHT:	Relleno del lado derecho - [Default]
#			-> STR_PAD_BOTH:	Relleno en ambos lados
#	
#   Returns:
#
#   See Also:
#
sub str_pad{
############################################################################################
############################################################################################
	my ($string, $pad_length, $pad_string, $pad_type) = @_;

	if( $string ){		
		my $pad_str = '';
		my $pad_str_extra_left = '';
		my $pad_str_extra_right = '';
		$pad_type = ( $pad_type ) ? $pad_type : "STR_PAD_RIGHT";
		## Si el tamaño requerido es mayor que el tamaño original de la cadena
		## entonces se continúa con el proceso.
		if( $pad_length > length($string) ){
			## Si la cadena con la que se rellenará la cadena original, tiene algún valor
			## entonces, se continúa con el proceso.
			if( $pad_string ne "" ){				
				my $num_iterations = 0;
				my $pad_string_length = length($pad_string);
				## Se calcula cuantos caracteres hacen falta para completar 
				## el tamaño requerido por $pad_length
				my $pad_length_need = $pad_length - length($string);
				my $band_ok = 0;
				## Si el relleno debe hacerse en ambos lados
				if( $pad_type eq 'STR_PAD_BOTH' ){
					if( $pad_length_need >= $pad_string_length and $pad_string_length == 1 ){
						$num_iterations = int($pad_length_need / 2);
						my $rmd = ($pad_length_need % 2);
						if( $rmd > 0 ){
							$pad_str_extra_right = substr($pad_string, 0, $rmd);
						}
						$band_ok = 1;
					}elsif( $pad_length_need >= $pad_string_length and $pad_string_length > 1 ){
						my $dif = $pad_length - length($string);
						my $double_length = length($pad_string) * 2;
						if( $double_length > $pad_length_need ){
							my $num_car = int($dif / 2);
							$pad_str_extra_left = substr($pad_string, 0, $num_car);
							if( ($dif % 2) > 0 ){
								$pad_str_extra_right = substr($pad_string, 0, ($num_car + 1));
							}
							$band_ok = 1;
						}else{
							$num_iterations = int($dif / $double_length);
							my $rmd = ($dif % $double_length);
							if( $rmd > 0 ){
								$pad_str_extra_right = substr($pad_string, 0, $rmd);
							}
							$band_ok = 1;
						}
					}
				}else{
				## Si el relleno debe hacerse sólo en alguno de los lados(izquierda o derecha)
					if( $pad_length_need >= $pad_string_length and $pad_string_length == 1 ){
						$num_iterations = $pad_length_need;
						$band_ok = 1;
					}elsif( $pad_length_need >= $pad_string_length and $pad_string_length > 1 ){
						my $dif = $pad_length - length($string);
						$num_iterations = int($dif / $pad_string_length);
						my $rmd = ($dif % $pad_string_length);
						if( $rmd > 0 ){
							$pad_str_extra_left = substr($pad_string, 0, $rmd);
							$pad_str_extra_right = $pad_str_extra_left;
						}
						$band_ok = 1;						
					}
				}

				## Si las condiciones se cumplen para rellenar la cadena con los parámetros
				## especificados, entonces se procede a hacerlo.
				if( $band_ok == 1 ){
					for (my $i=0; $i<$num_iterations; $i++){
					 	$pad_str .= $pad_string;
					}

					if( $pad_type eq "STR_PAD_LEFT" ){
						$string = $pad_str_extra_left.$pad_str.$string;
					}elsif( $pad_type eq "STR_PAD_RIGHT" ){
						$string = $string.$pad_str.$pad_str_extra_right;
					}else{
						$string = $pad_str_extra_left.$pad_str. $string .$pad_str.$pad_str_extra_right;
					}

					return $string;
				}else{
				## En caso de cumplir con las condiciones, sólo se retorna la cadena original sin cambios
					return $string;
				}
			}else{
			## Si la cadena de relleno es vacía, solo se retorna la cadena original sin cambios
				return $string;
			}
		}else{
		## Si el tamaño requerido es menor que el tamaño de la cadena original,
		## solo se retorna la cadena original sin cambios
			return $string;
		}
	}else{
		return;
	}
}

sub home_direksys{

	my $sth = &Do_SQL("SELECT admin_users.LastLogin, admin_users.LastIP, admin_users.Username_ref
		, UPPER(admin_users.application)application
		, UPPER(REPLACE(admin_users.MultiApp, '|',','))AS 'multiapp'
		, REPLACE(admin_users.ID_salesorigins, '|',',')AS 'ID_salesorigins'
		, IF(admin_users.MultiApp LIKE '%sales%',1,0)sales_available
		FROM admin_users  WHERE admin_users.ID_admin_users='$usr{'id_admin_users'}';");
	my ($lastlogin, $lastip, $username_ref, $application, $multiapp, $id_salesorigins, $sales_available) = $sth->fetchrow_array();
	$va{'last_login'} = &date_format_custom($lastlogin);
	$va{'last_ip'} = $lastip;
	$va{'multiapp'} = $multiapp;
	$va{'multiapp'} =~ s/\,/<br \/>/g;
	$va{'username_ref'} = $username_ref;

	my ($channel);
	if ($sales_available){

		my $add_sql = ($id_salesorigins)? " AND ID_salesorigins IN ($id_salesorigins)":"";

		my $sth = &Do_SQL("SELECT GROUP_CONCAT(Channel)Channel FROM sl_salesorigins WHERE Status='Active' $add_sql;");
		$va{'channel'} = $sth->fetchrow_array();
		$va{'channel'} =~ s/\,/<br \/>/g;

		$sth = &Do_SQL("SELECT COUNT(*) FROM sl_orders WHERE DATE=CURDATE() AND ID_admin_users='$usr{'id_admin_users'}';");
		$va{'sales_count'} = $sth->fetchrow_array();

	}
	if ($usr{'application'} ne 'sales'){
		$va{'sales_available'} = 'display:none;';
	}

	## Modulos Sales
	if ($usr{'application'} eq 'sales'){
		$sql = "
			SELECT date_format(sl_orders.Date,'%e')Date,COUNT(*)Orders
			FROM sl_orders
			-- WHERE date_format(sl_orders.Date,'%Y-%m') = date_format(CURDATE(),'%Y-%m')
			 WHERE Date>='2016-01-01' and Date<'2016-02-01'
			-- AND sl_orders.ID_admin_users='$usr{'id_admin_users'}'
			GROUP BY sl_orders.Date DESC
			-- LIMIT 7
		ORDER BY sl_orders.Date;";
		my $sth = &Do_SQL($sql);
		$va{'totals_chart'}='';
		while (my $rec = $sth->fetchrow_hashref()){
			$va{'totals_chart'} .= "['$rec->{'Date'}', $rec->{'Orders'}],";
		}
		chop($va{'totals_chart'});
		# &cgierr($va{'totals_chart'});
	}

	## Mod CRM
	if ($usr{'application'} eq 'crm'){
		# $sql = "
		# SELECT COUNT(*)Ventas
		# , sl_orders.shp_State Estado
		# , (SELECT sl_vars.Definition_En FROM sl_vars WHERE VName = 'estados_fedex' AND VValue=(SELECT State FROM sl_zipcodes WHERE StateFullName=sl_orders.shp_State LIMIT 1))Alias
		# FROM sl_orders
		# WHERE sl_orders.Date>='2016-04-01'
		# GROUP BY sl_orders.shp_State
		# ORDER BY Ventas DESC";
		# my $sth = &Do_SQL($sql);
		# $va{'array_chart'}='';
		# while (my $rec = $sth->fetchrow_hashref()){
		# 	$va{'array_chart'} .= "['$rec->{'Alias'}','$rec->{'Estado'}', $rec->{'Ventas'}]," if($rec->{'Alias'} ne '');
		# }
		# chop($va{'array_chart'});
	}

	if (1){

		my $sth = &Do_SQL("SELECT Date_exchange_rate, exchange_rate, Currency FROM sl_exchangerates WHERE DATE=CURDATE() AND Currency='US\$';");
		my ($date_exchange_rate, $exchange_rate, $currency) = $sth->fetchrow_array();
		if ($exchange_rate){
			$va{'date_exchange_rate'} = $date_exchange_rate;
			$va{'exchange_rate'} = $exchange_rate;
			$va{'currency'} = $currency;
		}
	}

	my $sth = &Do_SQL("SELECT GROUP_CONCAT(Name) AS 'groups' FROM admin_users_groups INNER JOIN admin_groups USING(ID_admin_groups) WHERE admin_users_groups.ID_admin_users='$usr{'id_admin_users'}';");
	$va{'groups'} = $sth->fetchrow_array();

	$va{'admin_vlogs'}='';
	my $sth = &Do_SQL("SELECT
	admin_vlogs.LogDate
	, admin_vlogs.LogTime
	, admin_vlogs.Message
	, admin_vlogs.Action
	, admin_vlogs.IP
	, admin_vlogs.ID_admin_users
	FROM admin_vlogs WHERE admin_vlogs.ID_admin_users='$usr{'id_admin_users'}'
	/* GROUP BY admin_vlogs.Message */
	ORDER BY admin_vlogs.ID_logs DESC 
	LIMIT 30;");
	while (my $rec = $sth->fetchrow_hashref()){
		$va{'admin_vlogs'} .= qq|
		<tr>
			<td colspan="2" class="log_title">|.&trans_txt($rec->{'Message'}).qq| $rec->{'Action'}</td>
		</tr>
		<tr>
			<td class="log_detail">Fecha: $rec->{'LogDate'} $rec->{'LogTime'}  I IP: $rec->{'IP'}</td>
		</tr>|;
	}
	
}

sub date_format_custom{
	my ($date) = @_;

	my $sth = &Do_SQL("SELECT 
		DATE_FORMAT('$date', '%e') AS 'day'
		, DATE_FORMAT('$date', '%W') AS 'day_name'
		, DATE_FORMAT('$date', '%b')AS 'month'
		, DATE_FORMAT('$date', '%Y') AS 'year'
		, DATE_FORMAT('$date', '%H:%i:%s') AS 'hour'
	");
	my ($day, $day_name, $month, $year, $hour) = $sth->fetchrow_array();

	if ($day){

		my %months = (
			"Jan", 'Enero'
			,"Feb", 'Febrero'
			,"Mar", 'Marzo'
			,"Apr", 'Abril'
			,"May", 'Mayo'
			,"Jun", 'Junio'
			,"Jul", 'Julio'
			,"Aug", 'Agosto'
			,"Sep", 'Septiembre'
			,"Oct", 'Octubre'
			,"Nov", 'Noviembre'
			,"Dec", 'Diciembre'
		);

		my %days = (
			"Monday", 'Lunes'
			, "Tuesday", 'Martes'
			, "Wednesday", 'Miercoles'
			, "Thursday", 'Jueves'
			, "Friday", 'Viernes'
			, "Saturday", 'Sabado'
			, "Sunday", 'Domingo'
		);

		return "$days{$day_name}, ".int($day)." de $months{$month} del $year $hour";

	}else{

		return &trans_txt('invalid_params');

	}

}

sub string_to_hexadecimal_ascii()
{
	use Switch;

	my ($text) = @_;
	my $result_text;

	my @characters = split("", $text);
	foreach $char (@characters) {
		$ascii = ord($char);
		
		switch($ascii){

			case 225 {$ascii = 160}
			case 233 {$ascii = 130}
			case 237 {$ascii = 161}
			case 243 {$ascii = 162}
			case 250 {$ascii = 163}
			case 252 {$ascii = 129}
			case 241 {$ascii = 164}
			case 193 {$ascii = 181}
			case 201 {$ascii = 144}
			case 205 {$ascii = 214}
			case 211 {$ascii = 162}
			case 218 {$ascii = 233}
			case 220 {$ascii = 154}
			case 209 {$ascii = 165}
		}

		$result_text .= sprintf("x%x", $ascii); 
	}
	
	return $result_text;

}

############################################################################################
############################################################################################
#	Function: order_service_validation
#   	Genera de forma dinamica el selector de estatus para customers
#
#       Created on: 11/08/15  13:11:25 By Jonathan Alcantara
#
#	Modified By:
#
#   	Parameters:
#
#   	Returns:
#
#   	See Also:
#
sub order_service_validation {
############################################################################################
############################################################################################
    my ($total_products_services) = &order_total_products_services($in{'id_orders'});
    my ($total_services) = &order_total_services($in{'id_orders'});

    my ($order_status) = &load_name('sl_orders','ID_orders', $in{'id_orders'},'Status');

    my $link = '';

    if (($total_products_services == $total_services) and $order_status eq 'Processed') {
    	$link = '<a id="aScanningService" href="#" class="">
                    <img
                        onclick="if(confirm(\'Are you sure to apply service scanning?\')){$(\'#aScanningService\').attr(\'href\',\'/cgi-bin/mod/admin/dbman?cmd=opr_orders&view='.$in{'id_orders'}.'&scanning_services=1\');$(\'#aScanningService\').click();}" 
                        src="[va_imgurl]/[ur_pref_style]/b_packinglist.gif" 
                        title="Scanning Services" 
                        alt="Scanning Services" 
                        border="0">
                </a>';
    }
    return $link;
}

############################################################################################
############################################################################################
#	Function: creditmemos_return_validation
#   	Valida si el Credit Memo tiene una previa devolucion de los productos
#
#	Created by:
#		07-09-2015::Ing. Alejandro Diaz
#
#	Modified By:
#
#   	Parameters:
#
#   	Returns:
#
#   	See Also:
#
sub creditmemos_return_validation{
############################################################################################
############################################################################################
	
	my ($id_creditmemos) = @_;
	$in{'id_creditmemos'} = $id_creditmemos if $in{'id_creditmemos'};
	my $this_res = 'ERROR'; my $this_message;

	## Validation 1
	my ($sth) = &Do_SQL("SELECT COUNT(*) FROM sl_creditmemos_products WHERE Status='Active' AND ID_products LIKE('4%') AND (ShpDate IS NULL OR ShpDate='0000-00-00') AND ID_creditmemos = ". $id_creditmemos .";");
	my ($incomplete_return) = $sth->fetchrow();

	## Validation 2 (Credit Memo already has an invoice)
	########## This is important for transition CM. Some processes could have invoice already. 
	########## This means no inventory return section applies
	my ($sth) = &Do_SQL("SELECT 
							COUNT(*) 
						FROM 
							cu_invoices INNER JOIN cu_invoices_lines 
							ON cu_invoices.ID_invoices = cu_invoices_lines.ID_invoices
						WHERE
							cu_invoices_lines.ID_creditmemos = ". $id_creditmemos ."
							AND cu_invoices.Status NOT IN ('Failed','ToCancel','CancelProcess','Cancelled','Void')
						GROUP BY 
							cu_invoices.ID_invoices;");
	my ($flag_invoice) = $sth->fetchrow(); 
	$flag_invoice = 0 if !$flag_invoice;

	## Validation 3 (Credit Memo already has momvements)
	my ($sth) = &Do_SQL("SELECT COUNT(*) FROM sl_movements WHERE tableused = 'sl_creditmemos' and ID_tableused = ". $id_creditmemos .";");
	my ($flag_movements) = $sth->fetchrow(); 
	$flag_movements = 0 if !$flag_movements; 

	## Validation 4 Returns Pending Intems
	my ($sth) = &Do_SQL("SELECT COUNT(DISTINCT sl_returns_upcs.ID_returns_upcs) ret_pending_items
						FROM sl_creditmemos
						INNER JOIN sl_returns_upcs ON sl_returns_upcs.ID_returns = sl_creditmemos.Reference
							AND sl_returns_upcs.`Status` != 'Processed'
						WHERE sl_creditmemos.ID_creditmemos = ".$id_creditmemos."
						;");
	my ($ret_pending_items) = $sth->fetchrow(); 


	if(!$flag_invoice and !$flag_movements){ #and $ret_pending_items > 0
		

		### Tipo de Cliente
		my ($sth) = &Do_SQL("SELECT ID_customers, `Type` FROM sl_customers WHERE ID_customers=".int($in{'id_customers'}).";");
		my ($id_customers, $ctype) = $sth->fetchrow_array();

		my $sql_cm_prods = "SELECT 
								ID_creditmemos_products
								, ID_products
								, Location
								, SalePrice
								, Quantity
								, Tax
								, Cost
								, Cost_Adj
								, Cost_Add
								, ShpDate
							FROM 
								sl_creditmemos_products 
							WHERE 
								ID_creditmemos = ". $id_creditmemos ." 
								AND `Status` = 'Active'
								AND ID_products > 400000000 
								AND ID_products < 600000000;";
		my $sth_cm_prods = &Do_SQL($sql_cm_prods);
		my $count_prods = 0;

		PRODS : while( my $rec = $sth_cm_prods->fetchrow_hashref() ){

			###------------------------------------------------------
			### Costo de producto
			###------------------------------------------------------
			my ($this_cost,$to_dump, $id_customs_info, $this_cost_adj, $this_cost_add);

			if ($cfg{'acc_inventoryout_method_cost'} and lc($cfg{'acc_inventoryout_method_cost'}) eq 'average'){
				
				($this_cost,$to_dump, $id_customs_info, $this_cost_adj, $cost_add) = &get_average_cost($rec->{'ID_products'});
				$log .= "($this_cost, $to_dump, $id_customs_info, $this_cost_adj, $cost_add)=get_average_cost($rec->{'ID_products'}) \n\n";
				
				if( !$this_cost or $this_cost == 0 or $this_cost eq ''){

					($this_cost, $this_cost_adj, $this_cost_add) = &load_last_purchase_cost($rec->{'ID_products'});

				}

			}else{

				($this_cost, $this_cost_adj, $id_customs_info) = &load_sltvcost($rec->{'ID_products'});
				$log .= "($this_cost, $this_cost_adj, $id_customs_info)=load_sltvcost($rec->{'ID_products'}) \n\n";

			}

			if( $this_cost ){

				$rec->{'Cost'} = $this_cost;
				$rec->{'Cost_Adj'} = ($this_cost_adj) ? $this_cost_adj : 0;
				$rec->{'Cost_Add'} = ($this_cost_add) ? $this_cost_add : 0;

				### Se actualiza el costo de los productos
				my $sql_upd = "UPDATE 
									sl_creditmemos_products 
								SET 
									Cost = ".$rec->{'Cost'}."
									, Cost_Adj = ".$rec->{'Cost_Adj'}."
									, Cost_Add = ".$rec->{'Cost_Add'}."
								WHERE 
									ID_creditmemos_products = ".$rec->{'ID_creditmemos_products'}.";";
				&Do_SQL($sql_upd);

				###------------------------------------------------------
				### Inventario
				###------------------------------------------------------
				
				### Se obtiene el Almacen y la Gaveta
				$sql = "SELECT Code, ID_warehouses FROM sl_locations WHERE UPC = '".&filter_values($rec->{'Location'})."';";
				my ($sthLocation) = &Do_SQL($sql);
				my ($Code, $ID_warehouses) = $sthLocation->fetchrow_array();

				if( !$ID_warehouses or !$Code ){

					$this_message .= "UPC Location Unknown ".$rec->{'Location'}."<br>";
					++$err;
					next PRODS;

				}

				my $add_sql_custom_info='';
				$add_sql_custom_info .= ($id_customs_info and $id_customs_info ne '')? ", ID_customs_info='$id_customs_info' ":"";
				if (!$this_cost or $this_cost == 0 or $this_cost eq ''){

					++$err;
					$this_message .= &trans_txt('enternewcmreturn_cost_not_found')." $rec->{'ID_products'}<br>";

				}else{

					&sku_logging($rec->{'ID_products'},$ID_warehouses, $Code, 'Return', $in{'id_creditmemos'}, 'sl_creditmemos', $rec->{'Quantity'}, $this_cost, $this_cost_adj, 'IN', $id_customs_info, $cost_add);
					$log .= "sku_logging($rec->{'ID_products'},$ID_warehouses, $Code, 'Return', $in{'id_creditmemos'}, 'sl_creditmemos', $rec->{'Quantity'}, $this_cost, $this_cost_adj, 'IN', $id_customs_info, $cost_add) \n\n";

				}

				my ($sthinv) =  &Do_SQL("SELECT ID_warehouses_location FROM sl_warehouses_location WHERE ID_warehouses = ".$ID_warehouses." AND Location = '".$Code."' and ID_products=".$rec->{'ID_products'}.";");
				my ($ID_warehouses_location) = $sthinv->fetchrow();
				
				my $sel_sql_custom_info = (!$id_customs_info) ? "AND ID_customs_info IS NULL" : "AND ID_customs_info = $id_customs_info";
	   			$sql = "SELECT ID_warehouses_location FROM sl_warehouses_location WHERE ID_warehouses = ".$ID_warehouses." AND ID_products = ".$rec->{'ID_products'}." AND Location = '$Code' $sel_sql_custom_info ORDER BY Date DESC LIMIT 1;";
	    		my $sth_exist = &Do_SQL($sql);
	   			my $id_wl = $sth_exist->fetchrow();
	   			
	   			if( int($id_wl) > 0 ){

	   				$sql = "UPDATE sl_warehouses_location SET Quantity = Quantity + ".$rec->{'Quantity'}." WHERE ID_warehouses_location = ".$id_wl.";";

	   			}else{

					$sql = "INSERT INTO sl_warehouses_location SET ID_warehouses=".$ID_warehouses.", ID_products=".$rec->{'ID_products'}.", Location='".$Code."', Quantity=".$rec->{'Quantity'}." $add_sql_custom_info, Date=CURDATE(), Time=CURTIME(), ID_admin_users='".$usr{'id_admin_users'}."';";

				}
				$log .= $sql."\n\n";
				$sthinv = &Do_SQL($sql);
				&auth_logging('warehouses_location_added',$sthinv->{'mysql_insertid'});
				
				$sql = "INSERT INTO sl_skus_cost SET ID_products = '".$rec->{'ID_products'}."',ID_purchaseorders='".$in{'id_creditmemos'}."',ID_warehouses='".$ID_warehouses."',Tblname='sl_creditmemos',Quantity='".$rec->{'Quantity'}."',Cost='".$this_cost."', Cost_Adj='".$this_cost_adj."', Date=CURDATE(), Time=CURTIME(), ID_admin_users='".$usr{'id_admin_users'}."';";
				$log .= $sql."\n\n";
				&Do_SQL($sql);

				###------------------------------------------------------
				### Contabilidad
				###------------------------------------------------------
				my $sku_cost = round($rec->{'Quantity'} * $rec->{'Cost'}, 2);
				my $sku_price = ($rec->{'SalePrice'} * $rec->{'Quantity'});
				my @params = ($in{'id_creditmemos'}, $in{'id_customers'}, $sku_cost, $sku_price, $rec->{'Tax'}, $rec->{'ShpDate'});
				($acc_status, $acc_str) = &accounting_keypoints('skus_backtoinventory_wo_cm_'. $ctype, \@params);
				++$flag_acc if $acc_status; $this_message .= qq|<br>Acc: |. $acc_str;
				$log .= qq|accounting_keypoints'skus_backtoinventory_wo_cm_'. $ctype, [] )|."\nAcc: $acc_status, $acc_str\n\n";	

				++$count_prods;

			}else{

				++$err;
				$this_message .= $rec->{'ID_products'}.": ".&trans_txt('skus_invalid_cost');

			}

		}					

		if( $err <= 0 and !$flag_acc){

			###------------------------------------------------------
			### Se genera la Nota de Credito
			###------------------------------------------------------

			($msg_invoice, $status) = &export_info_for_credits_notes($in{'id_creditmemos'});
			if ($status =~ /OK/i){

				$this_res = 'OK';
				$this_message = "Done: Invoice Response<br> ". $message_invoice;	

			}else{

				$this_message = "Invoice Response :: ". $message_invoice;

			}

		}

	}elsif( $incomplete_return and (($flag_invoice and !$flag_movements) or (!$flag_invoice and $flag_movements)) ){

		##
		### Validations Failed
		##
		$this_message = qq|<br>Incomplete Return Lines: |. $incomplete_return .qq|
							<br>Invoice Created: |. $flag_invoice .qq|
							<br>Accounting Movements: |. $flag_movements;

	}else{

		$this_message = 2 if ($flag_invoice and $flag_movements); ## Old Process record
		$this_res = 'OK';

	}

	return ($this_res, $this_message);
}


############################################################################################
############################################################################################
#	Function: encrypt_cc
#   	Encripta los datos de la tarjeta de credito
#
#	Created by:
#		05-10-2015::Ing. Gilberto Quirino
#
#	Modified By:
#
#   	Parameters:
#
#   	Returns:
#
#   	See Also:
#
sub encrypt_cc{
############################################################################################
############################################################################################

	my($id_orders, $id_payments, $cc_number, $cc_date, $cc_cvn) = @_;
	my $result = 'OK';
	my $message = '';

	if( !$id_orders or !$id_payments or !$cc_number or !$cc_cvn or !$cc_date ){
		$result = 'ERROR';
		$message = 'Alguno de los campos esta vacio, incompleto o invalido';
	}else{
		my $cc_crypt = &filter_values($cc_number);
		$cc_crypt = &LeoEncrypt($cc_crypt);
		my $date_crypt = &filter_values($cc_date);
		$date_crypt = &LeoEncrypt($date_crypt);
		my $cvn_crypt = &filter_values($cc_cvn);
		$cvn_crypt = &LeoEncrypt($cvn_crypt);
		&Do_SQL("INSERT INTO sl_orders_cardsdata(ID_orders, ID_orders_payments, card_number, card_date, card_cvn, Date, Time, ID_admin_users)
				 VALUES('$id_orders', '$id_payments', '$cc_crypt', '$date_crypt', '$cvn_crypt', CURDATE(), CURTIME(), ".$usr{'id_admin_users'}.");");	

	}

	return($result, $message);


}
sub button_notepad{
	my $val ='';
	$va{'test'} = &check_permissions('button_notepad','','');
	if($cfg{'activate_notepad'} and $cfg{'activate_notepad'} == 1 and &check_permissions('button_notepad','','')){
		$val=q|<a href="/cgi-bin/common/apps/ajaxbuild?ajaxbuild=user_notes&type=note" class="fancy_modal_iframe"><img src="/sitimages/notas.png" title="notepad" alt="Logoff" border="0"> </a>|;
	}
	return $val;
}

############################################################################################
############################################################################################
#	Function: transaction_validate
#   	Valida que no se duplique una transaccion
#
#	Created by:
#		01-12-2015::Ing. Gilberto Quirino
#
#	Modified By:
#
#   	Parameters:
#			cmd: Comando
#			ID_transaccion: ID del registro que se esta procesando
#			Type: check, insert, delete
#			
#   	Returns:
#
#   	See Also:
#
sub transaction_validate{
############################################################################################
############################################################################################
	my ($cmd, $id_trs, $type) = @_;

	$cmd = '' if( !$cmd );
	$id_trs = int($id_trs);

	my $result = 0;
	if( $type eq 'check' ){
		my $sth_vars = &Do_SQL("SELECT ID_transaction_controller, TIMESTAMPDIFF(minute, CONCAT(Date,' ',Time), NOW()) min_diff FROM transaction_controller WHERE Command = '".$cmd."' AND ID_transaction = ".$id_trs.";");
	    my ($trans_exist, $min_diff) = $sth_vars->fetchrow();

	    ## Si el lapso del bloqueo es menor a 10 min. entonces no permitirá la segunda transacción
	    if( int($min_diff) < 10 ){
		    $result = $trans_exist;
		## Si el lapso es mayor o igual a 10 min. entonces se desbloquea el ID.
		}else{
			&Do_SQL("DELETE FROM transaction_controller WHERE Command = '".$cmd."' AND ID_transaction = ".$id_trs.";");
		}
	}elsif( $type eq 'insert' ){
		if( $cmd ne '' and $id_trs > 0 ){
			my $sth_vars = &Do_SQL("INSERT INTO transaction_controller SET 
										Command = '".$cmd."'
										, ID_transaction = ".$id_trs."
										, Date = CURDATE()
										, Status = 'Active'
										, Time = CURTIME()
										, ID_admin_users = ".$usr{'id_admin_users'}.";");
		    my $new_id = $sth_vars->{'mysql_insertid'};

		    $result = $new_id;
		}
	}elsif( $type eq 'delete' ){
		if( $cmd ne '' and $id_trs > 0 ){
			my $sth_vars = &Do_SQL("DELETE FROM transaction_controller WHERE Command = '".$cmd."' AND ID_transaction = ".$id_trs.";");

			$result = 1;
		}
	}

	return $result;
}

############################################################################################
############################################################################################
#	Function: fix_hash_for_entershipment
#   	Transaforma el hash de entershipment parar optimizar proceso
#
#	Created on: 01-12-2015 13:46:25 By Fabian Cañaveral
#
#	Modified By:
#
#	Parameters:
#			%ids: hash con skus de escaneo
#
#
#			
#   Returns:
#		hash con skus sin repetir y con qty
#   See Also:
#
sub fix_hash_for_entershipment{
############################################################################################
############################################################################################
	my $hash = shift;
	my %response;
	my %skus;
	while( my($key, $value) = each $hash){

		if(exists($skus{@$value[0]})){

			$skus{@$value[0]}++;
			$response{@$value[0]}{'qty'} = $skus{@$value[0]};
			my $set = @$value[3];
			$set =~ /SET:(\d+),(\d+)/;
			$response{@$value[0]}{'id_orders_products'} .= ",".$1;

		}else{

			$skus{@$value[0]} = 1;
			my $set = @$value[3];
			$set =~ /SET:(\d+),(\d+)/;
			my $cost = @$value[4] ? @$value[4] : 0;
			my $codsale = @$value[5] ? @$value[5] : 0;
			
			$response{@$value[0]} = {
				'upc'=>@$value[1],
				'status'=>@$value[2],
				'id_parts'=>$2,
				'id_orders_products'=>$1,
				'qty'=>1,
				'cost'=>@$value[4],
				'codsale'=>$codsale
			};

		}

	}
	return %response;
}

############################################################################################
############################################################################################
#	Function: acc_periods_status
#   	Genera de forma dinamica del campo Status para el form periods_form
#
#	Created by:
#		09/03/2016 ISC Alejandro Diaz
#
#	Modified By:
#
#   	Parameters:
#
#   	Returns:
#
#   	See Also:
#
sub periods_status{
############################################################################################
############################################################################################
	if( $in{'search'} ){
		return $va{'periods_status'} = '[bc_status@sl_accounting_periods]';
	} elsif( $in{'add'} ){
		return $va{'periods_status'} = '[br_status@sl_accounting_periods]';
	} else {
		return $va{'periods_status'} = qq|<input type='hidden' name='status' value='[in_status]'>[in_status]|;
	}	
}

############################################################################################
############################################################################################
#	Function: segments_status
#   	Genera de forma dinamica del campo Status para el form segments_form
#
#	Created by:
#		10/03/2016 ISC Alejandro Diaz
#
#	Modified By:
#
#   	Parameters:
#
#   	Returns:
#
#   	See Also:
#
sub segments_status{
############################################################################################
############################################################################################
	if( $in{'search'} ){
		return $va{'segments'} = '[bc_status@sl_accounts_segments]';
	} elsif( $in{'add'} ){
		return $va{'segments'} = '[br_status@sl_accounts_segments]';
	} else {
		return $va{'segments'} = qq|<input type='hidden' name='status' value='[in_status]'>[in_status]|;
	}	
}

############################################################################################
############################################################################################
#	Function: segments_select
#   	Genera de forma dinamica un input tipo select
#
#	Created by:
#		10/03/2016 ISC Alejandro Diaz
#
#	Modified By:
#
#
#   	Parameters:
#
#   	Returns:
#
#   	See Also:
#
sub build_select_segments{
############################################################################################
############################################################################################
	my $select = '<option value="0"></option>';

	$select .= &recursive_tree_segments(0);

	return $select;
}

############################################################################################
############################################################################################
#	Function: segments_select
#   	Genera de forma dinamica un input tipo select
#
#	Created by:
#		10/03/2016 ISC Alejandro Diaz
#
#	Modified By:
#
#
#   	Parameters:
#
#   	Returns:
#
#   	See Also:
#
sub recursive_tree_segments{
############################################################################################
############################################################################################
	my ($id_parent, $tab) = @_;
	my $select = '';

	my $sth2 = &Do_SQL("SELECT
	sl_accounts_segments.ID_accounts_segments
	, sl_accounts_segments.Name
	FROM sl_accounts_segments 
	WHERE sl_accounts_segments.ID_parent='$id_parent'
	AND sl_accounts_segments.Status='Active'
	ORDER BY sl_accounts_segments.Name;");

	$tab .= ($id_parent > 0)? "&nbsp;&nbsp;&nbsp;&nbsp;":"";
	while ($rec2 = $sth2->fetchrow_hashref()) {
		$select .= '<option value="'.$rec2->{'ID_accounts_segments'}.'" class="ddoption">'.$tab.$rec2->{'Name'}.'  ('.$rec2->{'ID_accounts_segments'}.')</option>';

		$select .= &recursive_tree_segments($rec2->{'ID_accounts_segments'},$tab);
	}

	return $select;
}


sub add_order_notes {
# --------------------------------------------------------
	&connect_db;
	my ($ID_Orders,$Notes,$ID_orders_notes_types,$type) = @_;
	my ($sth) = &Do_SQL("INSERT INTO sl_orders_notes SET ID_orders='$ID_Orders',Notes='".&filter_values($Notes)."',Type='$type',ID_orders_notes_types=".$ID_orders_notes_types.",Date=Curdate(),Time=NOW(),ID_admin_users='$usr{'id_admin_users'}'");	
}

sub add_order_notes_by_type {
# --------------------------------------------------------
	&connect_db;
	my ($ID_Orders,$Notes,$Type) = @_;
	my ($sth_type) = &Do_SQL("SELECT ID_orders_notes_types,Type FROM sl_orders_notes_types WHERE Type='".$Type."'");	
	my ($type_row) = $sth_type->fetchrow_hashref;
	
	my $idtipo=0;
	
	if ($type_row->{'ID_orders_notes_types'}!=""){
		$idtipo=$type_row->{'ID_orders_notes_types'};
		$Type=$type_row->{'Type'};
	}else{
		$idtipo=1; 
		$Type="Low";
	}

	# if($usr{'id_admin_users'}==13){
	# 	&cgierr("$ID_Orders,$Notes,$Type\nSELECT * FROM sl_orders_notes_types WHERE Type='".$Type."'\nINSERT INTO sl_orders_notes SET ID_orders='$ID_Orders',Notes='".$Notes."',Type='".$Type."',ID_orders_notes_types=".$idtipo.",Date=Curdate(),Time=NOW(),ID_admin_users='$usr{'id_admin_users'}'");
	# }

	my ($sth) = &Do_SQL("INSERT INTO sl_orders_notes SET ID_orders='$ID_Orders',Notes='".$Notes."',Type='".$Type."',ID_orders_notes_types=".$idtipo.",Date=Curdate(),Time=NOW(),ID_admin_users='$usr{'id_admin_users'}'");	
	
}

sub add_order_notes_by_type_admin {
# --------------------------------------------------------
	&connect_db;
	my ($ID_Orders,$Notes,$Type) = @_;
	my ($sth_type) = &Do_SQL("SELECT * FROM sl_orders_notes_types WHERE Type='".$Type."'");	
	my ($type_row) = $sth_type->fetchrow_hashref;
	my $idtipo=0;
	if ($type_row->{'ID_orders_notes_types'}!=""){
		$idtipo=$type_row->{'ID_orders_notes_types'};
		$Type=$type_row->{'Type'};
	}else{
		$idtipo=1; 
		$Type="Low";
	}

	# if($usr{'id_admin_users'}==13){
	# 	&cgierr("$ID_Orders,$Notes,$Type\nSELECT * FROM sl_orders_notes_types WHERE Type='".$Type."'\nINSERT INTO sl_orders_notes SET ID_orders='$ID_Orders',Notes='".$Notes."',Type='".$Type."',ID_orders_notes_types=".$idtipo.",Date=Curdate(),Time=NOW(),ID_admin_users='$usr{'id_admin_users'}'");
	# }
	
	my ($sth) = &Do_SQL("INSERT INTO sl_orders_notes SET ID_orders='$ID_Orders',Notes='".$Notes."',Type='".$Type."',ID_orders_notes_types=".$idtipo.",Date=Curdate(),Time=NOW(),ID_admin_users='1'");		
	
}
sub get_agrupadorsat{
	return &load_name('sl_agrupadorsat', 'id_agrupadorSat', $in{'id_agrupadorsat'}, 'codigoagrupador').' - '.uc(&load_name('sl_agrupadorsat', 'id_agrupadorSat', $in{'id_agrupadorsat'}, 'name'));
}



sub phone_button{
	my $val = '';
	if($cfg{'asterisk_activate_phone'} and $cfg{'asterisk_activate_phone'} == 1 and &check_permissions('phone_button','','')){
		if(index($cfg{'available_modules_phone'}, $usr{'application'}) > -1){
			$val= &build_page("/widgets/call_button.html");
		}
	}
	return $val;
}



sub getSonsAccounts{
	my $id_parent = shift;
	if($id_parent eq ''){
		$id_parent = 0;
	}
	my @results;
	my $query = "SELECT count(*)
	FROM sl_accounts 
	WHERE id_parent = $id_parent
	ORDER BY sl_accounts.ID_accounting asc";
	$n = &Do_SQL($query)->fetchrow();
	# use Encode qw(decode encode);
	use HTML::Entities;
	if($n > 0){
		$query = "
			SELECT 
				sl_accounts.ID_accounts
				, sl_accounts.ID_accounting
				, sl_accounts.Name
				, sl_accounts.Status
				, sl_accounts.Currency
				, sl_accounts.Segment
				, sl_agrupadorsat.codigoAgrupador
				, sl_accounts.isdetailaccount
				, aux.typeAccount
				, sl_accounts.ID_parent
			FROM sl_accounts 
			LEFT JOIN (
				SELECT
					sl_accounts_nature.ID_accounts_nature
					, concat(prefix.Name, ' ', sl_accounts_nature.Name) typeAccount
				FROM 
					sl_accounts_nature
				INNER JOIN (
					SELECT 
						sl_accounts_nature.ID_accounts_nature
						, sl_accounts_nature.Name 
					FROM 
						sl_accounts_nature 
					WHERE sl_accounts_nature.id_parent = 0
				)prefix ON prefix.ID_accounts_nature = sl_accounts_nature.ID_parent
				WHERE 1 
					and ID_parent != 0
			)aux ON sl_accounts.ID_account_nature = aux.ID_accounts_nature
			LEFT JOIN sl_agrupadorsat on sl_agrupadorsat.id_agrupadorSat = sl_accounts.id_agrupadorsat
			WHERE 
				sl_accounts.id_parent = $id_parent 
				and sl_accounts.status != 'Void'
			ORDER BY sl_accounts.ID_accounts asc";
		my $rs = &Do_SQL($query);

		while(my $row = $rs->fetchrow_hashref()){
			my %element;
			$element{'ID_accounting'} 	= $row->{'ID_accounting'};
			$l = encode_entities($row->{'Name'});
			$element{'label'} 	= &format_account($row->{'ID_accounting'}).' - '.$l;
			$element{'ID_accounts'} 	= $row->{'ID_accounts'};
			$element{'Name'} 			= $row->{'Name'};
			$element{'Status'} 			= $row->{'Status'};
			$element{'Tipo'} 			= $row->{'typeAccount'};
			$element{'Moneda'} 			= $row->{'Currency'};
			$element{'Segmento'} 		= $row->{'Segment'};
			$element{'Agrupador'} 		= $row->{'codigoAgrupador'};
			$element{'Detalle'} 		= $row->{'isdetailaccount'};
			$element{'children'}		= &getSonsAccounts($row->{'ID_accounts'});
			push @results, \%element;
		}
		return \@results;
	}
	return 0;
}

sub accountsTree{
	$va{'expanditem'} = 3;
	use JSON;
	print "Content-type: text/html\n\n";
	if($in{'tree'}){
		$va{'data'} = encode_json getSonsAccounts(0);
		print &build_page("treeView.html");
		return;
	}
	$qry = "SELECT 
				sl_accounts.ID_accounts
				, sl_accounts.ID_accounting
				, sl_accounts.Name
				, sl_accounts.Status
				, sl_accounts.Currency
				, sl_accounts.Segment
				, sl_agrupadorsat.codigoAgrupador
				, sl_accounts.isdetailaccount
				, aux.typeAccount
				, sl_accounts.ID_parent
			FROM sl_accounts 
			LEFT JOIN (
				SELECT
					sl_accounts_nature.ID_accounts_nature
					, concat(prefix.Name, ' ', sl_accounts_nature.Name) typeAccount
				FROM 
					sl_accounts_nature
				INNER JOIN (
					SELECT 
						sl_accounts_nature.ID_accounts_nature
						, sl_accounts_nature.Name 
					FROM 
						sl_accounts_nature 
					WHERE sl_accounts_nature.id_parent = 0
				)prefix ON prefix.ID_accounts_nature = sl_accounts_nature.ID_parent
				WHERE 1 
					and ID_parent != 0
			)aux ON sl_accounts.ID_account_nature = aux.ID_accounts_nature
			LEFT JOIN sl_agrupadorsat on sl_agrupadorsat.id_agrupadorSat = sl_accounts.id_agrupadorsat
			WHERE 
				sl_accounts.status != 'Void'
			ORDER BY sl_accounts.ID_accounts asc";
	$rs = &Do_SQL($qry);
	$va{'table_accounts'} = qq|<table id="accounts"><thead><tr>
		<th></th>
		<th>ID Acounts</th>
		<th>ID Accounting</th>
		<th>Name</th>
		<th>Status</th>
	</tr></thead><tbody>|;
	while($row = $rs->fetchrow_hashref()){
		$img = '';
		$style = '';
		if($row->{'isdetailaccount'} eq 'Yes' and $row->{'Status'} eq 'Active'){
			$img = qq|<img src="/sitimages/newstyle/auth-fu.png"   style="width:15px" title="Seleccionar Cuenta" />|;
			$style = qq|data-id_accounts="$row->{'ID_accounts'}" data-name="|.&format_account($row->{'ID_accounting'})." ".$row->{'Name'}.qq|" style="cursor:pointer" onclick="selectAccount(this)"|;
		}
		$va{'table_accounts'} .= qq|
			<tr $style>
				<td width="2">$img</td>
				<td>$row->{'ID_accounts'}</td>
				<td>|.&format_account($row->{'ID_accounting'}).qq|</td>
				<td>$row->{'Name'}</td>
				<td>$row->{'Status'}</td>
			</tr>
		|;
	}
	$va{'table_accounts'}.=qq|</tbody></table>|;
	print &build_page("accountsTree.html");
	return;
}

############################################################################################
############################################################################################
#	Function: banks_status
#   	Genera de forma dinamica el selector de estatus
#
#	Created by:
#		24-11-2014::Ing. Alejandro Diaz
#
sub banks_status{
############################################################################################
############################################################################################
	return $va{'banks_status'} = ($in{'search'})?'[bc_status@sl_banks]':'[br_status@sl_banks]';
}

############################################################################################
############################################################################################
#	Function: banks_currency
#   	Genera de forma dinamica el selector de estatus
#
#	Created by:
#		24-11-2014::Ing. Alejandro Diaz
#
sub banks_currency{
############################################################################################
############################################################################################
	return $va{'banks_currency'} = ($in{'search'})?'[bc_currency@sl_banks]':'[br_currency@sl_banks]';
}

############################################################################################
############################################################################################
#	Function: get_account_name
#   	Obtiene la informacion de la cuenta contable
#
#	Created by:
#		19-07-2016::Ing. Alejandro Diaz
#
sub get_account_name{
############################################################################################
############################################################################################
	my ($sth) = &Do_SQL("SELECT sl_accounts.ID_accounting, UPPER(sl_accounts.Name)Name FROM sl_accounts WHERE sl_accounts.ID_accounts='".$in{'id_accounts'}."';");
	my ($id_accounting, $name) = $sth->fetchrow;
	
	return $va{'account_name'} = &format_account($id_accounting).' - '.$name;
}

#############################################################################
#############################################################################
#   Function: table_to_json
#
#       Es: Devuelve los resultados de un select simple en formateo JSON
#
#
#    Created on: 18/07/2016
#
#    Author: Ing Fabian Cañaveral
#
#    Modifications:
#
#
#   Parameters:
#
#		- tableName obligatorio
#		- fields opcional
#		- where opcional
#
#
#  Returns:
#
#      - 
#
#   See Also:
#
#		<>
#
#
sub table_to_json{
#############################################################################
#############################################################################
	use JSON;
	use Data::Dumper;
	my $tableName = shift;
	my $fields = shift or '*';
	my $where = shift or ' 1 ';
	my @results = ();
	if(!$tableName){
		return "{}";
	}
	$rs = &Do_SQL("SELECT $fields FROM $tableName WHERE 1 AND $where");
	while($rec = $rs->fetchrow_hashref()){
		push @results, $rec;
	}
	return encode_json \@results;
}

#############################################################################
#############################################################################
#   Function: enum_to_json
#
#       Es: Devuelve enum en formateo JSON
#
#
#    Created on: 18/07/2016
#
#    Author: Ing Fabian Cañaveral
#
#    Modifications:
#
#
#   Parameters:
#
#		- tableName obligatorio
#		- field obligatorio
#		- where opcional
#
#
#  Returns:
#
#      - 
#
#   See Also:
#
#		<>
#
#
sub enum_to_json{
#############################################################################
#############################################################################
	use JSON;
	use Data::Dumper;
	my $tableName = shift;
	my $fields = shift;
	my @results = ();
	if(!$tableName or !fields){
		return "{}";
	}
	@rs = &load_enum_toarray($tableName,$fields);
	for my $el (@rs){
		my %r = ('Id'=>$el, 'Name'=>$el);
		push @results, \%r;
	}
	return encode_json \@results;
}

############################################################################################
############################################################################################
#	Function: report_footer
#   	Genera Pie de Pagina para reportes CSV
#
#	Created by:
#		07-10-2016 ISC Alejandro Diaz
#
#   	Parameters:
#
#   	Returns:
#
#   	See Also:
#
#
sub report_footer{
############################################################################################
############################################################################################

	my ($user, $csv, $report_date);

	$report_date = &get_sql_date();
	$user  = $usr{'firstname'};
	$user .= ($usr{'lastname'} ne '')? " ".$usr{'lastname'}:"";
	$user .= ($usr{'middlename'} ne '')? " ".$usr{'middlename'}:"";
	$user  = uc($user);
	
	$csv .= qq|\n"GENERADO POR:","$user"|;
	$csv .= qq|\n"GENERADO EL:","$report_date"|;

	return $csv;

}


#############################################################################
#############################################################################
#       Function: vendor_cfdi_selector
#
#       Es: Muestra un listado de las Facturas emitidas por proveedores
#       En: 
#
#       Created on: 18/10/2016
#
#       Author: ISC Alejandro Diaz
#       
#       
#
sub vendor_cfdi_selector{
#############################################################################
#############################################################################

	# if ($cfg{'repo_db'} and $cfg{'repo_db'} ne ''){
		
		## Reescribe la conexion a Base de Datos
		&connect_db_w($cfg{'repo_db'},$cfg{'repo_host'},$cfg{'repo_user'},$cfg{'repo_pw'});

		if(!$in{'id_vendors'}){
			$va{'msg'} = "DEBE SELECCIONAR PRIMERO UN VENDOR PARA BUSCAR SUS FACTURAS";
			print "Content-type: text/html\n\n";
			print &build_page("vendor_cfdi_selector.html");
			return;
		}	

		### Filtro por tipo de bills		
		my $add_sql = '';
		if( $in{'type_bill'} ){
			my $this_type = ( lc($in{'type_bill'}) eq 'bill' ) ? 'Ingreso' : 'Egreso';
			$add_sql = " AND tipo = '$this_type'";
		}

		$rfc_vendor = &Do_SQL("SELECT RFC from sl_vendors where ID_vendors='$in{'id_vendors'}'  limit 1")->fetchrow();
		$sql = "SELECT 
		xml_info_vendor.ID_xml_info_vendor
		, CONCAT(xml_info_vendor.serie, xml_info_vendor.folio)invoice
		, xml_info_vendor.tipo
		, xml_info_vendor.uuid
		, xml_info_vendor.fecha_certificacion
		, xml_info_vendor.fecha_emision
		, xml_info_vendor.rfc
		, xml_info_vendor.razon_social
		, CONCAT(xml_info_vendor.total,' ',xml_info_vendor.moneda)total
		, xml_info_vendor.`Status`
		FROM direksys2_repo.e".$in{'e'}."_xml_info_vendor xml_info_vendor
		WHERE 1
		AND Status = 'Certified'
		AND rfc = '$rfc_vendor'
		AND id_vendors is null
		AND id_bills is null
		$add_sql
		ORDER BY ID_xml_info_vendor DESC
		";
		$sth = &Do_SQL($sql, 1);
		$va{'table_accounts'} = qq|<table id="invoices_vendor"><thead><tr>
			<th></th>
			<th>ID</th>
			<th>Factura #</th>
			<th>RFC Emisor</th>
			<th>Razon Social</th>
			<th>Fecha</th>
			<th>Tipo</th>
			<th>Total</th>
		</tr></thead><tbody>|
;		while($row = $sth->fetchrow_hashref()){
			$img = qq|<img src="/sitimages/newstyle/auth-fu.png"   style="width:15px" title="Invoice" />|;
			$style = '';
			# $img = ;
			$style = qq|data-id_xml="$row->{'ID_xml_info_vendor'}"  style="cursor:pointer" 
				onclick="selectInvoice(this)" 
				data-id_invoice="$row->{'ID_xml_info_vendor'}"
				data-uuid="$row->{'uuid'}"
			|;
			$va{'table_accounts'} .= qq|
				<tr $style>
					<td width="2">$img</td>
					<td>$row->{'ID_xml_info_vendor'}</td>
					<td>$row->{'invoice'}</td>
					<td>$row->{'rfc'}</td>
					<td>$row->{'razon_social'}</td>
					<td>$row->{'fecha_certificacion'}</td>
					<td>$row->{'tipo'}</td>
					<td>|.&format_price($row->{'total'}).qq|</td>
				</tr>
			|;
		}
		$va{'table_accounts'}.=qq|</tbody></table>|;
	# }

	print "Content-type: text/html\n\n";
	
	# exit;
	print &build_page("vendor_cfdi_selector.html");

}


#############################################################################
#############################################################################
#   Function: validate_date_in_openperiod
#
#       Es: Valida que la fecha se encuentre en un periodo contable abierto
#
#
#    Created on: 25/08/2016
#
#    Author: ISC Alejandro Diaz
#
#    Modifications:
#
#
#   Parameters:
#
#		- date obligatorio
#
#  Returns:
#
#      - true/false
#
#   See Also:
#
#		<>
#
#
sub validate_date_in_openperiod{
#############################################################################
#############################################################################
	my ($date) = @_;
	my ($sth) = &Do_SQL("SELECT IF(COUNT(*)>0,1,0) AS 'Result' FROM sl_accounting_periods WHERE sl_accounting_periods.`Status`='Open' AND '".$date."' BETWEEN sl_accounting_periods.From_Date AND sl_accounting_periods.To_Date;");
	$isvalid = $sth->fetchrow;

	return $isvalid;
	
}

sub getMovementInfo{
	$id_movements = shift;
	if($id_movements){
		$query = qq|SELECT FieldName, FieldValue FROM sl_movements_auxiliary WHERE id_movements = $id_movements|;
		my $sth = &Do_SQL($query);
		my %response = ();
		$response{'id_movements'} = $id_movements;
		while($row = $sth->fetchrow_hashref()){
			$response{$row->{'FieldName'}} = $row->{'FieldValue'};
		}
		return \%response;
		# select FieldName, FieldValue from sl_movements_auxiliary where id_movements = 11469576
	}
}

#############################################################################
#############################################################################
#   Function: getPhoneNumber
#
#       Es: Le pone al número el prefijo de celular 044 / 045 en caso de ser necesario
#
#
#    Created on: 26/01/2017
#    Author: Fabian Cañaveral
#
#    Modifications:
#
#
#   Parameters:
#
#		- phone Numero Telefonico
#
#  Returns:
#
#      - Numero telefonico Completo
#
#   See Also:
#
#		Se require haberse conectado previamente a base de datos de elastisk
#
#
sub getPhoneNumber{


	$phone = shift;
	$in{'phone'} = $phone;
	&connect_db_w($cfg{'dbi_db_cc'},$cfg{'dbi_host_cc'},$cfg{'dbi_user_cc'},$cfg{'dbi_pw_cc'});
	my $path = $cfg{'path_click_to_call'};
	$in{'phone'} =~ s/[^0-9]//g;
	$va{'local'} = 55;
	my $numero = $in{'phone'};
	my $local = substr $in{'phone'}, 2;
	my $area = substr $in{'phone'}, 0, 2;
	my $serie = substr $local, 0, 4; 

	if ( !( (substr $in{'phone'}, 0, 2) =~ /55|81|33/g)) {
		$area = substr $in{'phone'}, 0, 3;
	    $local = substr $in{'phone'}, 3;
		$serie = substr $local, 0, 3; 
	}


	if(length $in{'phone'} == 10){
		$SQL = "SELECT movil FROM elastix_helper.ift WHERE SUBSTRING('$numero',7) BETWEEN inicial AND final AND `area` = $area AND serie = $serie LIMIT 1";
		$sth = &Do_SQL($SQL);
		$res = $sth->fetchrow();
		if($area eq $va{'local'}){
			if($res eq '1'){
				$in{'phone'} = '044'.$in{'phone'};	
			}
		}else{
			if($res eq '1'){
				$in{'phone'} = '045'.$in{'phone'};	
			}else{
				$in{'phone'} = '01'.$in{'phone'};
			}
		}
	}
	return $in{'phone'};
}


#############################################################################
#############################################################################
#   Function: func_customers_ar
#				
#       Es: Muestra icono si un cliente tiene saldo que pueda ser cancelado de acuerdo a parametro de configuracion
#       En: 
#
#
#    Created on: 02/12/2017  12:20:10
#
#    Author: RB
#
#    Modifications:
#
#    Parameters:
#
#		
#  Returns:
#
#      - Icon representing a possible debt cancellation
#
#   See Also:
#
#	</cgi-bin/common/subs/libs/lib.orders.pl -> get_customers_ar_debtcancellation>
#
sub func_customers_ar {
#############################################################################
#############################################################################

	## Customer Invoices
	my $numrows = get_customers_ar_debtcancellation('rows');

	my $output =  $numrows ?
					qq| <a href="/cgi-bin/common/apps/ajaxbuild?ajaxbuild=customer_ar_debtcancellation&id_customers=[in_id_customers]" title="Cancell $numrows Invoice Debt" class="fancy_modal_iframe">
							<img src="[va_imgurl][ur_pref_style]/b_droppayment.png" title="Cancell $numrows Invoice Debt" alt="Cancell $numrows Invoice Debt" height="24" width="24" border="0">
						</a>| : '';

	return $output;

}

#############################################################################
#############################################################################
#   Function: log_debug
#				
#       Es: Guarda información en sl_debut
#       En: 
#
#
#    Created on: 26/04/2017
#
#    Author: Fabian Cañaveral
#
#    Modifications:
#
#    Parameters:
#
#		
#  Returns:
#
#      - ID de sl_debug creado.
#
#   See Also:
#
#	
#
sub log_debug {
#############################################################################
#############################################################################
	my ($cmd,$msg, $id)	= @_;
	if($msg){
		$q_save = $msg;
		$q_save =~ s/\'/\'\'/g;
		$log_query = qq|INSERT INTO `sl_debug` (`cmd`, `id`, `log`, `Date`, `Time`, `ID_admin_users`) 
		VALUES ('$cmd', '$id', '$q_save', curdate(), curtime(), '$usr{'id_admin_users'}');|;
		&Do_SQL($log_query);
		return &Do_SQL("SELECT LAST_INSERT_ID()")->fetchrow();
	}
	return 0;
}

#############################################################################
#############################################################################
#   Function: log_reports
#				
#       Es: Guarda log de los reportes con informacion delicada.
#       En: 
#
#
#    Created on: 26/04/2017
#
#    Author: Fabian Cañaveral
#
#    Modifications:
#
#    Parameters:
#
#		
#  Returns:
#
#      - ID de sl_debug creado.
#
#   See Also:
#
#	
#
sub log_reports {
#############################################################################
#############################################################################
	my ($query, $id) = @_;

	if($cfg{'save_log'} == 1){
		return log_debug('log_query_report', qq|Report : $id \n---------------------------------------\n $query|, $id);
	}
	return 0;
}



#############################################################################
#############################################################################
#   Function: notification
#				
#       Es: Se conecta a a API de Notificaciones de Direksys
#       En: 
#
#
#    Created on: 20/04/2017  13:20:00
#
#    Author: Fabian Cañaveral
#
#    Modifications:
#
#    Parameters:
#
#		
#  Returns:
#
#      - HTML para rederizar el plugin de notificaciones en Direksys
#
#   See Also:
#	conf|display_notification=1
#	conf|display_desktop_notification=1
#	
#
sub notification {
	if($cfg{'display_notification'} and $cfg{'display_notification'} == 1 ){
		$va{'desktop'} = $cfg{'display_desktop_notification'};
		$va{'element_notification'} = $cfg{'notification_element'};
		return &build_page('widgets/notification.html');
	}
}

#############################################################################
#############################################################################
#   Function: notificaction_js
#				
#       Es: Se conecta a a API de Notificaciones de Direksys
#       En: 
#
#
#    Created on: 20/04/2017  13:20:00
#
#    Author: Fabian Cañaveral
#
#    Modifications:
#
#    Parameters:
#
#		
#  Returns:
#
#      - HTML para rederizar el plugin de notificaciones en Direksys
#
#   See Also:
#	conf|display_notification=1
#	conf|display_desktop_notification=1
#	
#
sub notificaction_js {
	if($cfg{'display_notification'} and $cfg{'display_notification'} == 1 ){
		$va{'host'} = $cfg{'notification_host'};
		$va{'port'} = $cfg{'notification_port'};
		$va{'display_icon'} = $cfg{'display_notification_icon'};
		return &build_page('widgets/notification.js');
	}
}

#############################################################################
#############################################################################
#   Function: filter_text_match
#				
#       Es: Se eliminan caracteres especiales para palabras o texto que se utilizan en búsquedas MATCH AGAINST
#       En: 
#
#
#    Created on: 11/12/2017  
#
#    Author: Gilberto Quirino
#
#    Modifications:
#
#    Parameters:
#
#		
#  Returns:
#
#      - 
#
#   See Also:
#	
#
sub filter_text_match {
	my ($text) = @_;

	$text =~ s/[\+|\*|\&|\-|\||\>|\<|\~|\:\@|\\"|\\']//g;

	return $text;
}

1;