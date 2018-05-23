##################################################################
#    USERS : SESSIONS  	#
##################################################################
sub usr_sessions {
# --------------------------------------------------------
# Created :  Carlos Haas 01/01/2007 6:47:28 PM
# Last Update : 
# Locked by : 
# Description :
#
#
	my ($message) = @_;
	if ($in{'action'}){
		foreach $key (keys %in) {
			if ($in{$key} eq &trans_txt('btn_del')){
				$in{lc($db_cols[0])} = $key;
				%tmp = &load_session("$cfg{'auth_dir'}/$key");
				$va{'message'} = &trans_txt("usr_sesdroped") . " ($tmp{'id_admin_users'}) $tmp{'firstname'} $tmp{'lastname'}";
				&auth_logging('usr_sesdroped'," ($tmp{'id_admin_users'}) $tmp{'firstname'} $tmp{'lastname'}");
				unlink ("$cfg{'auth_dir'}/$key");
			}
		}
	}

	my ($colspan,%tmp,$qs,$colors);
	if (opendir (AUTHDIR, "$cfg{'auth_dir'}")){
		my ($play_btn,@files,$name,$comments);
		@files = readdir(AUTHDIR);		# Read in list of files in directory..
		closedir (AUTHDIR);
		@files = grep(/\d+/,@files);
		@files = sort @files;

		my (@c) = split(/,/,$cfg{'srcolors'});
		$va{'matches'} = $#files+1;
		
		(!$in{'nh'}) and ($in{'nh'}=1);
		
		$first = ($in{'nh'} - 1) * $usr{'pref_maxh'};
		$last = $va{'matches'};
		($last-$first > $usr{'pref_maxh'}) and ($last = $first+$usr{'pref_maxh'});
		for ($x = $first; $x < $last; $x++) {
			@ary = stat("$cfg{'auth_dir'}/$files[$x]");
			%tmp = &load_session("$cfg{'auth_dir'}/$files[$x]");
			
			my ($sec, $min, $hour, $day, $mon, $year, $dweek, $dyear, $daylight) = localtime($ary[9]);
			($hour<10) and ($hour = "0$hour");
			($min<10) and ($min = "0$min");
			($sec<10) and ($sec = "0$sec");
			
			($date,$time2) = split(/\s/,$tmp{'lastlogin'},2);
			$date = &sql_to_date($date);
			$time1 = "$hour:$min:$sec";
			$d = 1 - $d;
			
			$va{'searchresults'} .= qq|
				<tr bgcolor='$c[$d]' onmouseover='m_over(this)' onmouseout='m_out(this)'>
				   <td align="center"><input type="submit" name="$files[$x]" value="|.&trans_txt("btn_drop").qq|" class="button" onclick="notest=false;return;"></td>
				   <td class="smalltext">$tmp{'id_admin_users'}</td>
				   <td class="smalltext">$tmp{'lastname'}</td>
				   <td class="smalltext">$tmp{'firstname'}</td>
				   <td class="smalltext">$date</td>
				   <td class="smalltext">$time2 $time1</td>
				   <td class="smalltext">$tmp{'lastip'}</td>
				</tr>\n|;
		}
	}
	if ($va{'matches'}==0){
		$va{'matches'} = 0;
		$va{'pageslist'} = 0;
		$va{'searchresults'} = qq|
			<tr>
			   <td colspan="7" align="center"><p>&nbsp;</p><p>|.&trans_txt("usr_sesnone").qq|</p><p>&nbsp;</p></td>
			</tr>\n|;
	}else{
		($va{'pageslist'},$qs) = &pages_list($in{'nh'},$cfg{'pathcgi_adm_admin'},$va{'matches'},$usr{'pref_maxh'});
	}

	print "Content-type: text/html\n\n";
 	print &build_page('userman_ses.html');
	return;
}




##################################################################
#     USERS : DELETE LOGS   	#
##################################################################
sub usr_permtree_flist {
# --------------------------------------------------------
# Created on: 10/06/08 @ 11:46:38
# Author: Carlos Haas
# Last Modified on: 10/06/08 @ 11:46:38
# Last Modified by: Carlos Haas
# Description : 
# Parameters : 
#			   
	my ($flagchild,$flagparent);
	$flagchild  = 0;
	$flagparent = 0;
	
 	$va{'searchresults'}=&branch_application('admin');
	$va{'searchresults'}.=&branch_application('sales');
# 	$va{'searchresults'}.=&branch_application('administration');
	
	print "Content-type: text/html\n\n";
	print &build_page('usr_permtree_flist.html');	

}


##################################################################
#    USERS : SESSIONS  	#
##################################################################
sub usr_view_admin_perm {
# --------------------------------------------------------
# Created :  Arturo Hernandez 15/07/2014 6:47:28 PM
# Modified by: Gilberto Quirino C.
# Last Update : 
# Locked by : 
# Description :
#
#
	my (@c) = split(/,/,$cfg{'srcolors'});
	$va{'specialpermslist'} .= '<table cellspacing="0" cellpadding="0" width="100%">
		<tr>
			<td class="menu_bar_title">Command</td>
			<td class="menu_bar_title">Application</td>
			<td class="menu_bar_title">Users</td>
		</tr>
	';
	#--------------------------------------------------------------------#
	#-- Generando listado de comands
	#--------------------------------------------------------------------#
	#-- Se crea la tabla temporal
	&Do_SQL("CREATE TEMPORARY TABLE admin_commands_temp(
							ID_temp INT(11) NOT NULL AUTO_INCREMENT,
							command VARCHAR(150) NOT NULL,
							application VARCHAR(30) NOT NULL,
							PRIMARY KEY (`ID_temp`)
						)COLLATE='latin1_general_ci' 
						 ENGINE=InnoDB 
						 AUTO_INCREMENT=1;");
	#-- Se agregan los registros de la tabla admin_users_perms a la tabla temporal
	&Do_SQL("INSERT INTO admin_commands_temp(command, application)
				 SELECT DISTINCT up.command, up.application
				 FROM admin_users_perms up 
				 ORDER BY up.command, up.application;");
	#-- Se agregan los registros de la tabla admin_groups_perms a la tabla temporal
	#-- siempre y cuando no estén en la tabla admin_users_perms.
	&Do_SQL("INSERT INTO admin_commands_temp(command, application)
			 	SELECT DISTINCT gp.command, gp.application
				FROM admin_groups_perms gp
				WHERE gp.command Not In(Select Distinct up.command
										From admin_users_perms up);");

	$sthList = &Do_SQL("SELECT DISTINCT ID_temp, tmp.command, tmp.application
						FROM admin_commands_temp tmp
						ORDER BY tmp.command, tmp.application;");
	#--------------------------------------------------------------------#

	while(my ($id_admin_perms, $command, $application) = $sthList->fetchrow){
		$d = 1 - $d;

		$qTotal = "SELECT 
						COUNT(*)
					FROM admin_users_perms 
				   		INNER JOIN admin_users 
				   			ON admin_users.ID_admin_users = admin_users_perms.ID_admin_users
					WHERE command = '$command' 
						AND admin_users_perms.application = '$application'";
		my($sthcount) = &Do_SQL($qTotal);
		my ($total) = $sthcount->fetchrow;

		$va{'specialpermslist'} .= 
		'<tr bgcolor="'.$c[$d].'" style="height:25px;">
			<td ><img id="link_'.$id_admin_perms.'" class="collapse" style="cursor:pointer;" src="/sitimages/icon-collapse-plus.gif"> '.$command.'</td>
			<td >'.$application.'</td>
			<td >'.$total.'</td>
		</tr>
		';	

		$sql = "SELECT 
					admin_users_perms.ID_admin_users,
					admin_users_perms.application,
					admin_users_perms.command,
					admin_users_perms.Type,
					admin_users.FirstName,
					admin_users.LastName,
					admin_users.Username
				FROM admin_users_perms 
					INNER JOIN admin_users  
						ON admin_users.ID_admin_users = admin_users_perms.ID_admin_users
				WHERE command = '$command' 
					AND admin_users_perms.application = '$application'";
		my ($sthsql) = &Do_SQL($sql);
		if($total > 0){
			$va{'specialpermslist'} .= '
				<tr><td colspan="2">
					<table cellpadding="0" cellspacing="0" width="95%" style="margin-left:20px;" id="table_'.$id_admin_perms.'" class="tablecollapse">
					<tr>
						<td class="menu_bar_title">User ID</td>
						<td class="menu_bar_title">First Name</td>
						<td class="menu_bar_title">Last Name</td>
						<td class="menu_bar_title">Username</td>
						<td class="menu_bar_title">Type</td>
					</tr>';
			while(my ($id_admin_users, $applicationusr, $commandusr, $type, $firstname, $lastname, $username) = $sthsql->fetchrow){
				$b = 1 - $b;
				my $status_color = ($type eq "Allow") ? 'black' : 'red';
				$va{'specialpermslist'} .= '
					<tr bgcolor="'.$c[$b].'" style="color: '.$status_color.';">
						<td><a href="/cgi-bin/mod/'.$usr{'application'}.'/dbman?cmd=usrman&view='.$id_admin_users.'">'.$id_admin_users.'</a></td>
						<td style="text-transform: capitalize;">'.$firstname.'</td>
						<td style="text-transform: capitalize;">'.$lastname.'</td>
						<td>'.$username.'</td>
						<td>'.$type.'</td>
					</tr>
				';
			}			
		}else{
			$va{'specialpermslist'} .= '
				<tr><td colspan="2">
					<table cellpadding="0" cellspacing="0" width="90%" style="margin-left:20px;" id="table_'.$id_admin_perms.'" class="tablecollapse">
					<tr style="height:25px;">
						<td colspan="4" text-align:center;><b>No Record Found</b></td>
					</tr>';
		}		
		$va{'specialpermslist'} .= '
				</table>
			</td>
		</tr>
		';
		
	}
	$va{'specialpermslist'} .= '</table>';
	print "Content-type: text/html\n\n";
	print &build_page('usr_view_admin_perm.html');	
}


#############################################################################
#############################################################################
#   Function: usr_view_groups_perm
#
#       Es: Listado de grupos con sus respectivas restricciones
#
#    Created on: 2014-12-17
#
#    Author: Gilberto Quirino C.
#
#    Modifications:
#
#        - Modified on **: 
#
#   Parameters:
#	
#  Returns:
#
#   See Also:
#
sub usr_view_groups_perm {
#############################################################################
#############################################################################

	if ($in{'action'} and $in{'export'}){
		my($output);
		$output = qq|"ID GROUP","GROUP NAME","APPLICATION"\r\n|;

		$sthList = &Do_SQL("SELECT DISTINCT
								admin_groups.ID_admin_groups, 
								admin_groups.Name, 
								admin_groups.`Status`, 
								admin_groups_perms.application
							FROM admin_groups
								INNER JOIN admin_groups_perms USING(ID_admin_groups)
							ORDER BY admin_groups.Name;");
		while(my ($id_group, $name_group, $status, $application) = $sthList->fetchrow){
			$output .= qq|"$id_group","$name_group","$application"\r\n|;
			$qTotal = "SELECT COUNT(*)
						FROM admin_groups_perms
						WHERE ID_admin_groups = $id_group
							AND application = '$application';";
			my($sthcount) = &Do_SQL($qTotal);
			my ($total) = $sthcount->fetchrow;
			$sql = "SELECT 
						ID_admin_groups_perms, 
						command
					FROM admin_groups_perms
					WHERE ID_admin_groups = $id_group
						AND application = '$application';";
			my ($sthsql) = &Do_SQL($sql);
			if($total > 0){
				while(my ($id_groups_perms, $command) = $sthsql->fetchrow){					
					$output .= qq|"$id_groups_perms","$command"\r\n|;
				}
			}else{
				$output .= &trans_txt('search_nomatches').qq|\r\n|;
			}
		}

		print "Content-type: application/octetstream\n";
		print "Content-disposition: attachment; filename=Groups_perms_list.csv\n\n";
		print "$output\r\n";

		return ;
	}	

	if( int($in{'id_admin_groups'}) > 0 ){

		my (@c) = split(/,/,$cfg{'srcolors'});
		$va{'specialpermslist'} .= '<table cellspacing="0" cellpadding="0" width="100%">
			<tr>
				<td class="menu_bar_title">ID Group</td>
				<td class="menu_bar_title">Group</td>
				<td class="menu_bar_title">Application</td>
				<!--
				<td class="menu_bar_title">Status</td>
				-->
			</tr>
		';	

		$sthList = &Do_SQL("SELECT DISTINCT 
								admin_groups.ID_admin_groups, 
								admin_groups.Name, 
								admin_groups.`Status`, 
								admin_groups_perms.application
							FROM admin_groups
								INNER JOIN admin_groups_perms USING(ID_admin_groups)
							WHERE admin_groups_perms.ID_admin_groups = ".int($in{'id_admin_groups'})."
							ORDER BY admin_groups.Name;");
		my $id_row = 0;
		while(my ($id_group, $name_group, $status, $application) = $sthList->fetchrow){
			$d = 1 - $d;
			$id_row++;
			$va{'specialpermslist'} .= 
			'<tr bgcolor="'.$c[$d].'" style="height:25px;">
				<td ><img id="link_'.$id_row.'" class="collapse" style="cursor:pointer;" src="/sitimages/icon-collapse-plus.gif"> '.$id_group.'</td>
				<td >'.$name_group.'</td>
				<td >'.$application.'</td>
				<!--
				<td >'.$status.'</td>
				-->
			</tr>
			';	

			$qTotal = "SELECT COUNT(*)
						FROM admin_groups_perms
						WHERE ID_admin_groups = $id_group
							AND application = '$application';";
			my($sthcount) = &Do_SQL($qTotal);
			my ($total) = $sthcount->fetchrow;
			$sql = "SELECT 
						ID_admin_groups_perms, 
						command
					FROM admin_groups_perms
					WHERE ID_admin_groups = $id_group
						AND application = '$application';";
			my ($sthsql) = &Do_SQL($sql);
			if($total > 0){
				$va{'specialpermslist'} .= '
					<tr><td colspan="3">
						<table cellpadding="0" cellspacing="0" width="95%" style="margin-left:20px;" id="table_'.$id_row.'" class="tablecollapse">
						<tr>
							<td class="menu_bar_title">ID</td>
							<td class="menu_bar_title">Command</td>
						</tr>';
				while(my ($id_groups_perms, $command) = $sthsql->fetchrow){
					$b = 1 - $b;
					$va{'specialpermslist'} .= '
						<tr bgcolor="'.$c[$b].'">
							<td><a href="#">'.$id_groups_perms.'</a></td>
							<td style="text-transform: capitalize;">'.$command.'</td>
						</tr>
					';
					#/cgi-bin/mod/'.$usr{'application'}.'/dbman?cmd=usrman&view='.$id_groups_perms.'
				}			
			}else{
				$va{'specialpermslist'} .= '
					<tr><td colspan="3">
						<table cellpadding="0" cellspacing="0" width="90%" style="margin-left:20px;" id="table_'.$id_row.'" class="tablecollapse">
						<tr style="height:25px;">
							<td colspan="2" text-align:center;><b>No Record Found</b></td>
						</tr>';
			}		
			$va{'specialpermslist'} .= '
					</table>
				</td>
			</tr>
			';
			
		}
		$va{'specialpermslist'} .= '</table>';
	}

	print "Content-type: text/html\n\n";
	print &build_page('usr_groups_perms_list.html');
}

##################################################################
#    USERS : SESSIONS  	#
##################################################################
sub usr_admin_perm {
# --------------------------------------------------------
# Created :  Arturo Hernandez 13/06/2014 6:47:28 PM
# Last Update : 
# Locked by : 
# Description :
#
#
	$va{'expanditem'} = 8;
	my (@c) = split(/,/,$cfg{'srcolors'});
	if($in{'action'} and &check_permissions('edit_perm_bulk','','')){
		$va{'display'} = '';
		my @users = split(",", $in{'user'});
		
		if($in{'type'} eq 'admin' or $in{'type'} eq 'dbman'){
			my $sth_aux = &Do_SQL("SELECT COUNT(*) FROM admin_perms WHERE application='".&filter_values($in{'application'})."' AND type='".&filter_values($in{'type'})."' AND command='".&filter_values($in{'command'})."'");
				if ($sth_aux->fetchrow == 0) {
					$sth = &Do_SQL("REPLACE INTO `admin_perms` (`Name`, `Node`, `application`, `command`, `type`, `tabs`, `ID_parent`, `Path`, `Status`, `Date`, `Time`, `ID_admin_users`) VALUES
	(NULL, NULL, '".&filter_values($in{'application'})."', '".&filter_values($in{'command'})."', '".&filter_values($in{'type'})."', 0, NULL, NULL, 'New', CURDATE(), CURTIME(), $usr{'id_admin_users'});");
					
				}
				$sth = &Do_SQL("SELECT COUNT(*) FROM admin_perms WHERE application='".&filter_values($in{'application'})."' AND type='".&filter_values($in{'type'})."' AND command='".&filter_values($in{'command'})."'");
				if ($sth->fetchrow == 1 and $in{'ptype'}){
					
					$i = 0;
					foreach(@users) {
						my ($iduser) = $users[$i];
						
						if ($in{'type'} eq 'admin'){
							$sth = &Do_SQL("REPLACE INTO admin_users_perms SET ID_admin_users='$iduser', application='".&filter_values($in{'application'})."',  command='".&filter_values($in{'command'})."', Type='$in{'ptype'}' ");
						}else{
							$sth = &Do_SQL("REPLACE INTO admin_users_perms SET ID_admin_users='$iduser', application='".&filter_values($in{'application'})."',  command='".&filter_values($in{'command'}.'_add'). "', Type='$in{'ptype'}'") if ($in{'dbman_add'} eq 'on');
							$sth = &Do_SQL("INSERT INTO admin_users_perms SET ID_admin_users='$iduser', application='".&filter_values($in{'application'})."',  command='".&filter_values($in{'command'}.'_view'). "', Type='$in{'ptype'}'") if ($in{'dbman_view'} eq 'on');
							$sth = &Do_SQL("INSERT INTO admin_users_perms SET ID_admin_users='$iduser', application='".&filter_values($in{'application'})."',  command='".&filter_values($in{'command'}.'_del'). "', Type='$in{'ptype'}'") if ($in{'dbman_del'} eq 'on');
							$sth = &Do_SQL("INSERT INTO admin_users_perms SET ID_admin_users='$iduser', application='".&filter_values($in{'application'})."',  command='".&filter_values($in{'command'}.'_edit'). "', Type='$in{'ptype'}'") if ($in{'dbman_edit'} eq 'on');
							$sth = &Do_SQL("INSERT INTO admin_users_perms SET ID_admin_users='$iduser', application='".&filter_values($in{'application'})."',  command='".&filter_values($in{'command'}.'_print'). "', Type='$in{'ptype'}'") if ($in{'dbman_print'} eq 'on');
							for(my ($z) = 1;$z<=20;$z++){
							my $tab = 'dbman_tab'.$z;
								if($in{$tab}){
								$va{'result'} .= $z.'--><br>';
									$sth = &Do_SQL("INSERT INTO admin_users_perms SET ID_admin_users='$iduser', application='".&filter_values($in{'application'})."',  command='".&filter_values($in{'command'}.$z)."', Type='$in{'ptype'}' ") if ($in{'dbman_tab'.$z} eq 'on');
								}
							}
						}
						++$i;
					}
				}
		}
			
		$va{'command'} = $in{'command'}.'->'.$in{'ptype'};
		if($in{'type'} eq 'special'){
			$i = 0;
			foreach(@users) {
				my ($iduser) = $users[$i];
				my $sth_aux = &Do_SQL("SELECT COUNT(*) FROM admin_perms WHERE application='".&filter_values($in{'new_application'})."' AND command='".&filter_values($in{'command'})."'");
				if ($sth_aux->fetchrow == 0) {
					$sth = &Do_SQL("INSERT INTO `admin_perms` (`Name`, `Node`, `application`, `command`, `type`, `tabs`, `ID_parent`, `Path`, `Status`, `Date`, `Time`, `ID_admin_users`) VALUES (NULL, NULL, '".&filter_values($in{'application'})."', '".&filter_values($in{'command'})."', '".'NULL'."', 0, NULL, NULL, 'New', CURDATE(), CURTIME(), $usr{'id_admin_users'});");
				}
				my $sth2 = &Do_SQL("SELECT
				(SELECT IF(COUNT(*)=0,0,1) FROM admin_perms WHERE application='".&filter_values($in{'application'})."' AND command='".&filter_values($in{'command'})."')valid
				,(SELECT IF(COUNT(*)=0,0,1)permexists FROM admin_users_perms WHERE ID_admin_users='".$iduser."' AND application='".&filter_values($in{'application'})."' AND command='".&filter_values($in{'command'})."' AND Type='".$in{'ptype'}."')permexists;");
				my ($is_valid,$already_exists) = $sth2->fetchrow_array();
				if ($is_valid and !$already_exists and $in{'ptype'}){

						my $sth = &Do_SQL("REPLACE INTO admin_users_perms SET ID_admin_users='".$iduser."', application='".&filter_values($in{'application'})."',  command='".&filter_values($in{'command'})."', Type='".$in{'ptype'}."' ");

						if ($sth->rows() == 1) {
							$va{'message'} = &trans_txt('record_added');
							&auth_logging('usrman_addperm',$iduser);
						}
				}else{
					if (!$in{'ptype'}){
						$va{'message'} = &trans_txt('reqfields');
					}elsif (!$is_valid){
						$va{'message'} = &trans_txt('usrman_perm_unknown');
					}elsif ($already_exists){
						$va{'message'} = &trans_txt('usrman_perm_already_exists');
					}
				}
				++$i;
			}
		}
		$va{'message'} .= 'Record Added ['.$va{'command'}.']';
	}else{
		$va{'display2'} = '';
		$va{'display'} = 'display:none;';
	}

	print "Content-type: text/html\n\n";
	print &build_page('usr_admin_perm.html');	
}

#############################################################################
#############################################################################
#   Function: group_admin_perm
#
#       Es: Adminstrador de Permiso del Grupo
#       En: Groups Permissions Manager
#
#
#    Created on: 08-07-2016
#
#    Author: ISC ALejandro Diaz
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
#
#   See Also:
#
#
sub usr_group_admin_perm{
#############################################################################
#############################################################################
	my (@c) = split(/,/,$cfg{'srcolors'});

	if ($in{'action'}){

		if (!$in{'groups'}){
			$error{'groups'} = &trans_txt('required');
		}if (!$in{'application'}){
			$error{'application'} = &trans_txt('required');
		}if (!$in{'new_command'}){
			$error{'new_command'} = &trans_txt('required');
		}if (!$in{'ptype'}){
			$error{'ptype'} = &trans_txt('required');
		}

		if (!%error){

			my @groups = split(",", $in{'groups'});

			$i=0;
			foreach (@groups) {

				my ($id_admin_groups) = $groups[$i];
				$va{'command'} = $id_admin_groups.'->'.$in{'application'}.'->'.$in{'new_command'}.'->'.$in{'ptype'};

				if ($in{'ptype'} eq 'allow'){

					## Allow
					&Do_SQL("DELETE FROM admin_groups_perms WHERE ID_admin_groups='".$id_admin_groups."' AND application='".&filter_values($in{'application'})."' AND command='".&filter_values($in{'new_command'})."';");
					$in{'db'} = 'admin_groups';
					&auth_logging('usrman_remperm',$id_admin_groups);

				}else{

					## Disallow
					&Do_SQL("DELETE FROM admin_groups_perms WHERE ID_admin_groups='".$id_admin_groups."' AND application='".&filter_values($in{'application'})."' AND command='".&filter_values($in{'new_command'})."';");
					&Do_SQL("INSERT INTO admin_groups_perms SET ID_admin_groups='".$id_admin_groups."', application='".&filter_values($in{'application'})."', command='".&filter_values($in{'new_command'})."';");
					$in{'db'} = 'admin_groups';
					&auth_logging('usrman_addperm',$id_admin_groups);
				}
				$va{'message'} .= 'Record Added ['.$va{'command'}.']<br>';
				$i++;
			}

			delete($in{'application'});
			delete($in{'new_command'});
			delete($in{'ptype'});
			&memcached_delete('','',1);

		}else{
			$va{'message'} = &trans_txt('reqfields');
		}
	}

	print "Content-type: text/html\n\n";
	print &build_page('group_admin_perm.html');	
}

#############################################################################
#############################################################################
#   Function: usr_users_perms_list
#
#       Es: Listado de permisos por usuario
#       En: List of permissions per user
#
#
#    Created on: 2014-12-17
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
#
#   See Also:
#
#
#
sub usr_users_perms_list{
#############################################################################
#############################################################################
	if ($in{'action'} and $in{'export'}){
		my ($output);
		my $sth = &Do_SQL("SELECT
			admin_users.ID_admin_users
			, admin_users.Username
			, UPPER(CONCAT(admin_users.FirstName,' ',admin_users.MiddleName,' ', admin_users.LastName))User
			, admin_users.Status
			, admin_groups.Name as GroupName
			, admin_users.MultiApp
		FROM admin_users
		LEFT JOIN admin_users_groups ON admin_users.ID_admin_users=admin_users_groups.ID_admin_users
		LEFT JOIN admin_groups ON admin_groups.ID_admin_groups=admin_users_groups.ID_admin_groups
		WHERE admin_groups.Status='Active'
		-- AND admin_users.Status='Active'
		AND admin_users.ID_admin_users>=3000
		ORDER BY admin_users.FirstName, admin_users.MiddleName, admin_users.LastName");
		$output .= qq|"ID","Username","User","Status","Group","Module","Perm","Status"\r\n|;
		while(my $rec = $sth->fetchrow_hashref()){
			# $output .= qq|"$rec->{'ID_admin_users'}","$rec->{'Username'}","$rec->{'User'}","$rec->{'Status'}","$rec->{'GroupName'}"|;

			my (@modules) = split(/\|/, $rec->{'MultiApp'});
			for (0..$#modules){

				# $output .= qq|"Module","Perm","Status"\r\n|;

				my $sth_usr = &Do_SQL("SELECT
					admin_users_perms.application
					, admin_users_perms.command
					, admin_users_perms.Type
				FROM admin_users_perms
				WHERE admin_users_perms.ID_admin_users='$rec->{'ID_admin_users'}'
				AND admin_users_perms.application='$modules[$_]'
				ORDER BY admin_users_perms.command");
				my $num_rec_usr = 0;
				while(my $rec_usr = $sth_usr->fetchrow_hashref()){
					$num_rec_usr++;
					$output .= qq|"$rec->{'ID_admin_users'}","$rec->{'Username'}","$rec->{'User'}","$rec->{'Status'}","$rec->{'GroupName'}","$modules[$_]","$rec_usr->{'command'}","$rec_usr->{'Type'}"\r\n|;
				}
				
				if (!$num_rec_usr){
					$output .= qq|"$rec->{'ID_admin_users'}","$rec->{'Username'}","$rec->{'User'}","$rec->{'Status'}","$rec->{'GroupName'}","$modules[$_]",|.&trans_txt('search_nomatches').qq|\r\n|;
				}

			}
		}
		
		print "Content-type: application/octetstream\n";
		print "Content-disposition: attachment; filename=Users_perms_list.csv\n\n";
		print "$output\r\n";

		return;
	}

	if( $in{'id_admin_users'} ){

		my $filter_usr = '';
		if( $in{'id_admin_users'} =~ /\D/ ){
			$filter_usr = " AND admin_users.Username = '".&filter_values($in{'id_admin_users'})."' ";
		} else {
			$filter_usr = " AND admin_users.ID_admin_users = ".int($in{'id_admin_users'});
		}

		my (@c) = split(/,/,$cfg{'srcolors'});
		$va{'specialpermslist'} .= '<table cellpadding=5 cellspacing=0 width=100% border=1>';

		my $sth = &Do_SQL("SELECT
			admin_users.ID_admin_users
			, admin_users.Username
			, UPPER(CONCAT(admin_users.FirstName,' ',admin_users.MiddleName,' ', admin_users.LastName))User
			, admin_users.Status
			, admin_groups.Name as GroupName
			, admin_users.MultiApp
		FROM admin_users
		LEFT JOIN admin_users_groups ON admin_users.ID_admin_users=admin_users_groups.ID_admin_users
		LEFT JOIN admin_groups ON admin_groups.ID_admin_groups=admin_users_groups.ID_admin_groups
		WHERE admin_groups.Status='Active'
		-- AND admin_users.Status='Active'
		-- AND admin_users.ID_admin_users>=3000
		".$filter_usr."
		ORDER BY admin_users.FirstName, admin_users.MiddleName, admin_users.LastName");
		while(my $rec = $sth->fetchrow_hashref()){
			$d = 1 - $d;
			$va{'specialpermslist'} .= qq|
			<tr>
				<td class="" colspan=5><br><br>
				 <img src=/sitimages/user$rec->{'Status'}.png align=left style="position:relative;top:3px;margin-right:10px">
				<font class="menu2"> $rec->{'User'}	<b>$rec->{'ID_admin_users'} </b></font><br>
				Username: <b>$rec->{'Username'} </b>
				Group: <b>$rec->{'GroupName'}</b>
				</td>
			</tr>|;

			# split por , y recorrer cada modulo
			my (@modules) = split(/\|/, $rec->{'MultiApp'});
			for (0..$#modules){

				$va{'specialpermslist'} .= qq|
			<tr>
				<td class="menu_bar_title">Module</td>
				<td class="menu_bar_title" colspan="3">Perm</td>
				<td class="menu_bar_title">Status</td>
			</tr>|;

				my $sth_usr = &Do_SQL("SELECT
					admin_users_perms.application
					, admin_users_perms.command
					, admin_users_perms.Type
				FROM admin_users_perms
				WHERE admin_users_perms.ID_admin_users='$rec->{'ID_admin_users'}'
				AND admin_users_perms.application='$modules[$_]'
				ORDER BY admin_users_perms.command");
				my $num_rec_usr = 0;
				while(my $rec_usr = $sth_usr->fetchrow_hashref()){
					$num_rec_usr++;
					$va{'specialpermslist'} .= qq|
			<tr style="border:1px #111111 solid;">
				<td style="border-left: 1px #111111 solid;border-bottom: 1px #111111 solid;">$modules[$_]</td>
				<td colspan="3" style="border-bottom: 1px #111111 solid;">$rec_usr->{'command'}</td>
				<td style="border-right: 1px #111111 solid;border-bottom: 1px #111111 solid;">$rec_usr->{'Type'}</td>
			</tr>|;
				}
				
				if (!$num_rec_usr){
					$va{'specialpermslist'} .= qq|
			<tr>
				<td class="" colspan="5" style="text-align:center;border: 1px #111111 solid;">|.&trans_txt('search_nomatches').qq|</td>
			</tr>|;
				}

			}
		}

		$va{'specialpermslist'} .= '</table>';

	} 
	print "Content-type: text/html\n\n";
	print &build_page('usr_users_perms_list.html');	
}


#############################################################################
#############################################################################
#   Function: usr_tree_list
#
#       Es: Listado usuarios con supervisor y coordinador
#       En: List users with supervisor and coordinator
#
#
#    Created on: 2016-04-15
#
#    Author: Fabian Cañaveral
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
#
#   See Also:
#
#
#
sub usr_admin_tree{
#############################################################################
#############################################################################
	
	print "Content-type: text/html\n\n";

	$query = "select 
		ID_admin_users user
		, (select upper(concat(FirstName, ' ', LastName, ' ', MiddleName)) from admin_users where id_admin_users = aut.ID_admin_users) user_name
		,ID_admin_users2 sup
		, (select upper(concat(FirstName, ' ', LastName, ' ', MiddleName)) from admin_users where id_admin_users = aut.ID_admin_users2) sup_name
		,ID_admin_users3 coor
		, (select upper(concat(FirstName, ' ', LastName, ' ', MiddleName)) from admin_users where id_admin_users = aut.ID_admin_users3) coor_name
	from cu_admin_users_tree aut
	order by ID_admin_users asc";
	$rs = &Do_SQL($query);
	$va{'body_table'} = '';
	while( my $row = $rs->fetchrow_hashref() ){
		$va{'body_table'} .= "
		<tr>
			<td> <input type='number' class='userID input' data-pos='1' value='$row->{'user'}'/> <span>- $row->{'user_name'}</span></td>
			<td> <input type='number' class='userID input' data-pos='2' value='$row->{'sup'}'/> <span>- $row->{'sup_name'}</span></td>
			<td> <input type='number' class='userID input' data-pos='3' value='$row->{'coor'}'/> <span>- $row->{'coor_name'}</span></td>
			<td> <input class='button' type='button' value='Guardar' data-id='saveButton'/></td>
			<td> <img src='/sitimages/close.png' data-id='deleteRow' class='deleteRow' /> </td>
		</tr>";
	}
	print &build_page('usr_admin_tree.html');

}


#############################################################################
#   Function: blocked_users
#
#       Es: Listado de usuarios bloqueados
#       En: Users blocked list
#
#
#    Created on: 2018-02-28
#
#    Author: Alfredo Salazar
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
#
#   See Also:
#
#
#

sub usr_admin_banned{
	print "Content-type: text/html\n\n";	

	my $where='';

	if($in{'usernametofind'}){
		$va{'usernametofind'}=$in{'usernametofind'};
		$where=' WHERE admin_users.Username like "%'.$in{'usernametofind'}.'%"';
	}
	$query = "	SELECT   admin_users_locked.ID_admin_users_locked
						,admin_users_locked.ID_admin_users
						,admin_users_locked.ID_ipmanager
						,admin_users_locked.Time
						,admin_users_locked.Date
						,admin_users.FirstName
						,admin_users.MiddleName
						,admin_users.LastName
						,admin_users.Username
						,sl_ipmanager.IP
				FROM admin_users_locked
				LEFT JOIN admin_users ON admin_users.ID_admin_users=admin_users_locked.ID_admin_users 
				LEFT JOIN sl_ipmanager on sl_ipmanager.ID_ipmanager=admin_users_locked.ID_ipmanager 
				".$where."
				ORDER BY DATE DESC
				LIMIT 30";

	$rs = &Do_SQL($query);
	my $numrows=$rs->rows;

	if($numrows>30){
		$va{'qty'}="30 of ".$numrows;
	}else{
		$va{'qty'}=$numrows;
	}

	$va{'body_table'} = '';
	my $color="";
	my $cont=1;
	while( my $row = $rs->fetchrow_hashref() ){
		if(($cont%2)==0){
			$color="#f2f2f2";
		}else{
			$color="#ffffff";
		}

		$va{'body_table'} .= '
		<tr class="tr_'.$row->{'ID_admin_users'}.'" bgcolor="'.$color.'">			
			<td><center>'.$row->{'Username'}.'(<a href="/cgi-bin/mod/admin/dbman?cmd=usrman&view='.$row->{'ID_admin_users'}.'&second_conn=0">'.$row->{'ID_admin_users'}.'</a>)<center></td>
			<td><center>'.$row->{'FirstName'}.' '.$row->{'MiddleName'}.' '.$row->{'LastName'}.'<center></td>
			<td><center>'.$row->{'IP'}.'<center></td>
			<td><center>'.$row->{'Date'}.'<center></td>
			<td><center>'.$row->{'Time'}.'<center></td>
			<td><center><input type="checkbox" name="users[]" value="'.$row->{'ID_admin_users'}.'" class="chk"></center></td>
		</tr>';
		$cont++;
	}

	print &build_page('usr_locks.html');
}

1;