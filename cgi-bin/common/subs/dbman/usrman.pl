
#############################################################################
#############################################################################
#   Function: validate_usrman
#
#       Es: validacion de datos de usuario
#       En: 
#
#
#    Created on: *12/16/2014*
#
#    Author: _Roberto Barcenas_
#
#    Modifications:
#
# Last Modified RB: 03/18/09  10:12:26 -- LastLogin initialization
# Last Modified RB: 04/07/09  13:01:35 -- Se Modifica el acceso para grupos 1,7
# Last Modified RB: 08/23/2010  11:51:35 -- Se requiere el user_type
# Last modified on 16 Dec 2010 11:50:38
# Last modified by: MCC C. Gabriel Varela S. : Se implementa sha1
# Last modified on 11 May 2011 13:28:46
# Last modified by: MCC C. Gabriel Varela S. : Se hace que el ipfilter sea igual al del creador
# Last modified on 17 May 2011 16:31:59
# Last modified by: MCC C. Gabriel Varela S. : Se hace que las x se tomen como *
# Last modified on 20 May 2011 15:20:34
# Last modified by: MCC C. Gabriel Varela S. :Se hace que \r sea opcional
#
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
#      <validate_cols>
#
sub validate_usrman {
#############################################################################
#############################################################################

	my ($err);

	####
	#### 1) Permisos de edicion
	####
	if(!&check_permissions($in{'cmd'},'','')){ 

		$error{'message'} = trans_txt('not_auth');
		++$err;

	}


	####
	#### 2) Application vs MultiApp Error
	####
	if ($in{'multiapp'} !~ /$in{'application'}/){

		$error{'application'} = &trans_txt('usrman_appvsmultiapp');
		++$err;

	}
	#Si el usuario esta en estatus Baja (Cancel), no prosigue
	my $bd_status = &load_name('admin_users','ID_admin_users',$in{'id_admin_users'},'Status');

	if ($bd_status eq 'Cancel') {
		$error{'message'} = &trans_txt("usrman_unable_edit_cancel_user");
		$error{'status'} = &trans_txt("usrman_unable_edit_cancel_user");
		++$err;

		return $err;
	}
	#Se evalúa ipfilter
	#Se obtiene ipfilter del creador
	my $created_by_ipfilter;
 	if($in{'id_admin_users'} ne ''){
		
		#obtiene created by
		my $created_by=&load_name('admin_users','ID_admin_users',$in{'id_admin_users'},'CreatedBy');
		$created_by_ipfilter=&load_name('admin_users','ID_admin_users',$created_by,'ipfilter');

 	}else{
		$created_by_ipfilter=&load_name('admin_users','ID_admin_users',$usr{'id_admin_users'},'ipfilter');
 	}
 	
 	####
	#### 3) IPFilter
	####
 	my (@ipfilter_values) = split(/\r?\n/,$created_by_ipfilter);
 	my $ipfilter_turn;
 	my $valid_ip=0;
 	my (@ipfilter_values_in) = split(/\r?\n/,$in{'ipfilter'});
 	foreach my $ipfilter_turn (@ipfilter_values){

		$ipfilter_turn=~s/\./\\\./g;
		$ipfilter_turn=~s/x/\[\\d\|x\]\*/g;
 		foreach my $ipfilter_turn_in (@ipfilter_values_in){

			if($ipfilter_turn_in=~/$ipfilter_turn/){

				#$variable="$ipfilter_turn";
				++$valid_ip;

			}

		}

	}
	#cgierr("$variable y valid_ip:$valid_ip y ".($#ipfilter_values_in+1));

	(!$in{'status'}) and ($in{'status'} = 'Active');

	####
	#### 4) Username Length
	####
	if($in{'username'} and (length($in{'username'})<5 or length($in{'username'})>16)){
		$error{'username'} = &trans_txt("invalid");
		++$err;
	}


	####
	#### 5) Email
	####
	if ($in{'email'}){
		if (!&valid_address($in{'email'})){
			$error{'email'} = &trans_txt("invalid");
			++$err;
		}			
	}

	####
	#### 6) User Type
	####
	if(!$in{'user_type'}){
		$error{'user_type'} = &trans_txt("required");
		++$err;
	}

	$in{'lastlogin'} = "NOW()" if $in{'status'} eq 'Active';
	$in{'usergroup'} = 3;



	if ($in{'add'}){

		####
		#### 7) Only when user New
		####

		my ($passwd) = &gen_passwd;

		use Digest::SHA1;
		my $sha1= Digest::SHA1->new;
		$sha1->add($passwd);
		$in{'password'} = $sha1->hexdigest;
		$in{'temppasswd'} = $passwd;

		if($in{'username'}){

			####
			#### 7.1) Searching UserName
			####

			my ($sth) = &Do_SQL("SELECT COUNT(*) FROM admin_users WHERE Username='$in{'username'}';");
			$found = $sth->fetchrow();
			
			if ($found>0){

				####
				#### 7.1.1) Previous User Found
				####

				$error{'username'} = &trans_txt("repeated");
				++$err;

			}else{

				####
				#### 7.1.2) OK: New User Created
				####
				$body = "Your password: $passwd";
				$subject = &trans_txt("admin_email_subject");
				
				if (send_email("admin\@innovagroupusa.com",$in{'email'},$subject,$body) eq "ok"){

					$va{'email_status'} = &trans_txt("admin_email_success");

				}else{

					$va{'email_status'} = &trans_txt("admin_email_err");

				}

			}

		}

		### Expiration
		$in{'never_expires'} = 'off';
		my $sth = &Do_SQL("SELECT DATE_ADD(CURDATE(), INTERVAL 5 DAY) AS date_exp;");
		$date_exp = $sth->fetchrow();
		$in{'expiration'} = $date_exp;		
		### Change Pswd
		$in{'change_pass'} = 'Yes';

	}else{

		####
		#### 8) USer Edition
		####

		my ($sth) = &Do_SQL("SELECT COUNT(*) FROM admin_users WHERE Username='$in{'username'}' AND ID_admin_users<>'$in{'id_admin_users'}';");
		$found = $sth->fetchrow();
		
		if ($found>0){

			####
			#### 8.1) UserName Repeated
			####
			$error{'username'} = &trans_txt("repeated");
			++$err;

		}

		$in{'password'} = &load_name('admin_users','ID_admin_users',$in{'id_admin_users'},'Password');
		$in{'temppasswd'} = &load_name('admin_users','ID_admin_users',$in{'id_admin_users'},'tempPasswd');

	}
	if ($in{'status'} eq 'Cancel' and ! &check_permissions('user_cancel',,)) {
		$error{'message'} = &trans_txt("usrman_requires_permission");
		$error{'status'} = &trans_txt("usrman_requires_permission");
		++$err;
	}
	if ($in{'user_type'} ne "Vendors") {
		if ($in{'opclegalid'} ne "") {
			my ($sth) = &Do_SQL("SELECT COUNT(*) FROM admin_users WHERE opcLegalID='".$in{'opclegalid'}."' AND ID_admin_users<>'".$in{'id_admin_users'}."';");
			$tot_repeated = $sth->fetchrow();

			if ($tot_repeated > 0){
				$error{'opclegalid'} = &trans_txt("repeated");
				++$err;
			}
		}
	}
	####
	#### 9) Expiration
	####
	# if ($in{'never_expires'}){

	# 	$in{'expiration'} = 'NULL';

	# }

	return $err;

}


#############################################################################
#############################################################################
#   Function: updated_usrman
#
#       Es: Usuario actualizado
#       En: 
#
#
#    Created on: 02/05/2017
#
#    Author: _RB_
#
#    Modifications:
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
#      <validate_cols>
#
sub updated_usrman {
#############################################################################
#############################################################################

	if( $cfg{'memcached'} ){

		###
		##  Memcache Data
		###
		my ($sth) = &Do_SQL("SELECT ses FROM admin_sessions WHERE CreatedBy = ". $in{'id_admin_users'} ." AND Date(CreatedDateTime) = CURDATE() ORDER BY CreatedDateTime DESC LIMIT 1;");
		my ($this_sid) = $sth->fetchrow();

		if($this_sid){

			###
			##  Memcache Key Deletion
			###
			&memcached_delete('e' . $in{'e'} . '_' . $this_sid);

		}

	}
	# Baja definitiva de usuario
	if ($in{'status'} eq 'Cancel'){
		&user_canelling($in{'opclegalid'});
	}

}


#############################################################################
#############################################################################
#   Function: view_usrman
#
#       Es: vista de datos de usuario
#       En: 
#
#
#    Created on: 08/03/2016
#
#    Author: ISC Alejandro Diaz
#
#    Modifications:
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
#      <validate_cols>
#
sub view_usrman {
#############################################################################
#############################################################################

	### Sale Channels Restriction
	if ($in{'id_salesorigins'} =~ m/\|/){
		my $id_salesorigins_temp;
		my @arr = split /\|/ , $in{'id_salesorigins'};
		for (0..$#arr) {
			$id_salesorigins_temp .= $arr[$_]."," if($arr[$_] ne '');
		}
		chop $id_salesorigins_temp;
		$in{'id_salesorigins'} = $id_salesorigins_temp;
	}
	if ($in{'id_salesorigins_view'} =~ m/\|/){

		my $id_salesorigins_view_temp;
		my @arr = split /\|/ , $in{'id_salesorigins_view'};
		for (0..$#arr) {
			$id_salesorigins_view_temp .= $arr[$_]."," if($arr[$_] ne '');
		}
		chop $id_salesorigins_view_temp;
		$in{'id_salesorigins_view'} = $id_salesorigins_view_temp;
	}

	my $add_sql = " AND id_salesorigins IN ($in{'id_salesorigins'}) "if ($in{'id_salesorigins'});
	my ($sth) = &Do_SQL("SELECT group_concat(Channel) FROM sl_salesorigins WHERE 1 $add_sql AND Status='Active';");
	$va{'sale_channel'} = $sth->fetchrow();
	
	$add_sql = " AND id_salesorigins IN ($in{'id_salesorigins_view'}) "if ($in{'id_salesorigins_view'});
	$sth = &Do_SQL("SELECT group_concat(Channel) FROM sl_salesorigins WHERE 1 $add_sql AND Status='Active';");
	$va{'sale_channel_view'} = $sth->fetchrow();

	$va{'sale_channel_restriction'} = ($cfg{'use_salesorigins_restriction'} and $cfg{'use_salesorigins_restriction'}==1)?"Enabled":"Disabled";
	
	if ($in{'id_accounts_segments'}){
		my $ids_segments = $in{'id_accounts_segments'};
		$ids_segments =~ s/\|/,/g;
		my ($sth) = &Do_SQL("SELECT GROUP_CONCAT(Name) FROM sl_accounts_segments WHERE ID_accounts_segments IN (".$ids_segments.") AND Status='Active';");
		$va{'accounts_segments'} = $sth->fetchrow();
	}

	## Validacion de Fecha de expiracion de contraseña
	$va{'display_expirated'} = 'none';
	if ($in{'expiration'} ne ''){

		my ($sth) = &Do_SQL("SELECT IFNULL(DATEDIFF(CURDATE(),'$in{'expiration'}'),'invalid') AS DiffDate;");
		$expirated = $sth->fetchrow();
		$va{'display_expirated'} = ($expirated > 0)? 'inline':$va{'display_expirated'};

	}

	## Activacion/Inactivacion de Usuarios
	if ($in{'chgstatusto'}){

		if (&check_permissions('usrman_chgstatus','','')){
			my $continue = 1;
			if ($in{'chgstatusto'} eq 'Cancel' and ! &check_permissions('user_cancel','','')) {
				$continue = 0;
			}
			if ($continue == 1) {
				my ($sth) = &Do_SQL("UPDATE admin_users SET Status='".&filter_values($in{'chgstatusto'})."' WHERE ID_admin_users='$in{'view'}'");

				&auth_logging('usrman_chgstatus_'.lc($in{'chgstatusto'}),$in{'view'});

				$in{'status'} = $in{'chgstatusto'};

				if ($in{'chgstatusto'} eq 'Cancel') {
					&user_canelling($in{'opclegalid'});
				}
				$va{'message_good'} = &trans_txt('usrman_chgstatus')." to ".$in{'status'};
			} else {
				$va{'message_error'} = &trans_txt('unauth_action');
			}
		}else{
			$va{'message_error'} = &trans_txt('unauth_action');
		}
	}

	if (&check_permissions('usrman_chgstatus','','')){
		my (@ary) = &load_enum_toarray('admin_users','Status');
		for (0..$#ary){
			if ($ary[$_] ne $in{'status'}) {
				if ($ary[$_] eq 'Cancel') {
					if (&check_permissions('user_cancel','','')) {
						$va{'chgstatus'} .= qq| <a href="/cgi-bin/mod/$usr{'application'}/dbman?cmd=usrman&view=$in{'view'}&chgstatusto=$ary[$_]">$ary[$_]</a> &nbsp;&nbsp;&nbsp;|;
					}
				} else {
					if ($in{'status'} ne 'Cancel') {
						$va{'chgstatus'} .= qq| <a href="/cgi-bin/mod/$usr{'application'}/dbman?cmd=usrman&view=$in{'view'}&chgstatusto=$ary[$_]">$ary[$_]</a> &nbsp;&nbsp;&nbsp;|;
					}
				}
			}
		}
	}

	###
	### Muestra el autorizador del usuario
	###
	$va{'authorizer'} = '';
	if( &table_exists('cu_admin_users_rel') ){
		my $sth = &Do_SQL("SELECT admin_users.ID_admin_users, admin_users.FirstName, admin_users.LastName, admin_users.MiddleName
							FROM cu_admin_users_rel 
								INNER JOIN admin_users ON cu_admin_users_rel.ID_admin_users_rel1 = admin_users.ID_admin_users 
							WHERE cu_admin_users_rel.ID_admin_users_main = ".$in{'id_admin_users'}." 
								AND Type_rel = 'Authorization'
							LIMIT 1;");
		my ($id_admin_users, $firstname, $lastname, $middlename) = $sth->fetchrow_array();
		$va{'authorizer'} = $id_admin_users.' - '.$lastname.' '.$middlename.' '.$firstname;
	}

	####
	#### Configuración para el acceso al portal de proveedores
	####
	if( int($in{'drop_uvendor'}) == 1 ){
		&Do_SQL("DELETE FROM admin_users_vendors WHERE id_admin_users = ".int($in{'id_admin_users'}).";");
	}

	$va{'vendorsite_user'} = '';
	my $sth = &Do_SQL("SELECT sl_vendors.ID_vendors
							, sl_vendors.RFC
							, sl_vendors.CompanyName
							, sl_vendors.Currency
						FROM admin_users_vendors
							INNER JOIN sl_vendors ON admin_users_vendors.id_vendors = sl_vendors.ID_vendors
						WHERE admin_users_vendors.id_admin_users = ".$in{'id_admin_users'}.";");
	my $cont = 1;
	while( my $rec = $sth->fetchrow_hashref() ){

		my $lnk_dlt = '';
		if( $cont == 1 ){
			$lnk_dlt = '<a href="/cgi-bin/mod/[ur_application]/dbman?cmd=usrman&drop_uvendor=1&view=[in_id_admin_users]" onclick="javascript: return confirm(\"Are you sure?\");"><img src="[va_imgurl]/[ur_pref_style]/b_drop.png" alt="drop" style="vertical-align: middle;"></a>';
		}
		$va{'vendorsite_user'} .= '<p>['.$rec->{'ID_vendors'}.'] - '.$rec->{'RFC'}.' - '.$rec->{'CompanyName'}.' ('.$rec->{'Currency'}.') '.$lnk_dlt.'</p>';
		$cont++;

	}

	### Created By
	my $sth_cb = &Do_SQL("SELECT FirstName, LastName FROM admin_users WHERE ID_admin_users = ".int($in{'createdby'}).";");
	my $created_by = $sth_cb->fetchrow_hashref();
	$in{'createdby.firstname'} = $created_by->{'FirstName'};
	$in{'createdby.lastname'} = $created_by->{'LastName'};

	################################################################################
	################################################################################
	################################################################################
	###########################									####################
	###########################				TABS				####################
	###########################									####################	
	################################################################################
	################################################################################
	################################################################################


	if($in{'tab'} == 1){

		delete($va{'message'}) if $va{'message'};
		if ($in{'addperm'}){

			$va{'display_perm'} = '';
			if(!&check_permissions($in{'cmd'},'_addperm','')){ return &html_unauth_tab; };
			$va{'new_tbname'} = 'usrman_tab1_add';
			
			if($in{'action'}){
			
				###
				##
				###
				my $sth_aux = &Do_SQL("SELECT 
											COUNT(*) 
										FROM admin_perms 
										WHERE 
											application = '".&filter_values($in{'new_application'})."' 
											AND type='".&filter_values($in{'type'})."' 
											AND command='".&filter_values($in{$in{'type'}.'_cmd'})."';");

				if ($sth_aux->fetchrow == 0) {

					$sth = &Do_SQL("REPLACE 
										INTO `admin_perms` 
										(`Name`, `Node`, `application`, `command`, `type`, `tabs`, `ID_parent`, `Path`, `Status`, `Date`, `Time`, `ID_admin_users`) 
									VALUES
										(NULL, NULL, '".&filter_values($in{'new_application'})."', '".&filter_values($in{$in{'type'}.'_cmd'})."', '".&filter_values($in{'type'})."', 0, NULL, NULL, 'New', CURDATE(), CURTIME(), $usr{'id_admin_users'});");

				}

				$sth = &Do_SQL("SELECT COUNT(*) FROM admin_perms WHERE application='".&filter_values($in{'new_application'})."' AND type='".&filter_values($in{'type'})."' AND command='".&filter_values($in{$in{'type'}.'_cmd'})."'");
				if ($sth->fetchrow == 1 and $in{'ptype'}){
					
					## OK
					if ($in{'type'} eq 'admin'){

						$sth = &Do_SQL("REPLACE INTO admin_users_perms SET ID_admin_users='$in{'id_admin_users'}', application='".&filter_values($in{'new_application'})."',  command='".&filter_values($in{'admin_cmd'})."', Type='$in{'ptype'}' ");
					
					}else{

						$sth = &Do_SQL("REPLACE INTO admin_users_perms SET ID_admin_users='$in{'id_admin_users'}', application='".&filter_values($in{'new_application'})."',  command='".&filter_values($in{'dbman_cmd'}.'_add'). "', Type='$in{'ptype'}'") if ($in{'dbman_add'} eq 'on');
						$sth = &Do_SQL("INSERT INTO admin_users_perms SET ID_admin_users='$in{'id_admin_users'}', application='".&filter_values($in{'new_application'})."',  command='".&filter_values($in{'dbman_cmd'}.'_view'). "', Type='$in{'ptype'}'") if ($in{'dbman_view'} eq 'on');
						$sth = &Do_SQL("INSERT INTO admin_users_perms SET ID_admin_users='$in{'id_admin_users'}', application='".&filter_values($in{'new_application'})."',  command='".&filter_values($in{'dbman_cmd'}.'_del'). "', Type='$in{'ptype'}'") if ($in{'dbman_del'} eq 'on');
						$sth = &Do_SQL("INSERT INTO admin_users_perms SET ID_admin_users='$in{'id_admin_users'}', application='".&filter_values($in{'new_application'})."',  command='".&filter_values($in{'dbman_cmd'}.'_edit'). "', Type='$in{'ptype'}'") if ($in{'dbman_edit'} eq 'on');
						$sth = &Do_SQL("INSERT INTO admin_users_perms SET ID_admin_users='$in{'id_admin_users'}', application='".&filter_values($in{'new_application'})."',  command='".&filter_values($in{'dbman_cmd'}.'_print'). "', Type='$in{'ptype'}'") if ($in{'dbman_print'} eq 'on');
						$sth = &Do_SQL("SELECT tabs FROM admin_perms WHERE application='".&filter_values($in{'new_application'})."' AND type='dbman' AND command='".&filter_values($in{'dbman_cmd'})."'");		
						my ($tot_tabs) = $sth->fetchrow;
						
						if ($tot_tabs>0){
							for my $i(1..$tot_tabs){
								$sth = &Do_SQL("INSERT INTO admin_users_perms SET ID_admin_users='$in{'id_admin_users'}', application='".&filter_values($in{'new_application'})."',  command='".&filter_values($in{'dbman_cmd'}.$i)."', Type='$in{'ptype'}' ") if ($in{'dbman_tab'.$i} eq 'on');
							}
						}
					}

					$va{'message'} = &trans_txt('record_added');
					&auth_logging('usrman_addperm',$in{'id_admin_users'});

				}else{
					$va{'message'} = &trans_txt('reqfields');
				}
			}

		}elsif ($in{'addspecialperm'}){

			$va{'display_special_perm'} = '';
			$va{'display_perm'} = 'display:none;';
			
			## Special perms
			if(!&check_permissions($in{'cmd'},'_addperm','')){ return &html_unauth_tab; };
			$va{'new_tbname'} = 'usrman_tab1_add';
			
			if($in{'action'}){

				##############################################################################################################
				
				my $sth_aux = &Do_SQL("SELECT 
											COUNT(*) 
									FROM admin_perms 
									WHERE 
										application = '".&filter_values($in{'new_application'})."' 
										AND command='".&filter_values($in{'command'})."';");

				if ($sth_aux->fetchrow == 0) {

					$sth = &Do_SQL("INSERT 
										INTO `admin_perms` 
										(`Name`, `Node`, `application`, `command`, `type`, `tabs`, `ID_parent`, `Path`, `Status`, `Date`, `Time`, `ID_admin_users`) 
									VALUES
										(NULL, NULL, '".&filter_values($in{'new_application'})."', '".&filter_values($in{'command'})."', '".'NULL'."', 0, NULL, NULL, 'New', CURDATE(), CURTIME(), $usr{'id_admin_users'});");
				}
				##############################################################################################################
				
				my $sth2 = &Do_SQL("SELECT
					(SELECT IF(COUNT(*)=0,0,1) FROM admin_perms WHERE application='".&filter_values($in{'new_application'})."' AND command='".&filter_values($in{'command'})."')valid
					,(SELECT IF(COUNT(*)=0,0,1)permexists FROM admin_users_perms WHERE ID_admin_users='".$in{'view'}."' AND application='".&filter_values($in{'new_application'})."' AND command='".&filter_values($in{'command'})."' AND Type='".$in{'ptype'}."')permexists;");
				my ($is_valid,$already_exists) = $sth2->fetchrow_array();
				if ($is_valid and !$already_exists and $in{'ptype'}){

						my $sth = &Do_SQL("REPLACE INTO admin_users_perms SET ID_admin_users='".$in{'view'}."', application='".&filter_values($in{'new_application'})."',  command='".&filter_values($in{'command'})."', Type='".$in{'ptype'}."' ");

						if ($sth->rows() == 1) {
							$va{'message'} = &trans_txt('record_added');
							&auth_logging('usrman_addperm',$in{'id_admin_users'});
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
			}

		}elsif ($in{'drop'}){

			## Drop Permission
			if(!&check_permissions($in{'cmd'},'_delperm','')){ return &html_unauth_tab; };
			my ($sth) = &Do_SQL("DELETE FROM admin_users_perms WHERE ID_admin_users='$in{'id_admin_users'}' AND ID_admin_users_perms=$in{'drop'}");
			$va{'message'} = &trans_txt('permission_dropped');
			&auth_logging('usrman_delperm',$in{'id_admin_users'});

		}

		###
		##  Memcache Key Deletion
		###
		my $this_sid = &get_user_sessid();
		&memcached_delete('e' . $in{'e'} . '_perm_' . $this_sid);
		#&cgierr('e' . $in{'e'} . '_perm_' . $this_sid);

	}


}

#############################################################################
#############################################################################
#   Function: vendorsite_user_button
#
#       Es: Funcion que genera el link para crear la cuenta de usuario para el portal de proveedores
#       En: 
#
#
#    Created on: 12/12/2016
#
#    Author: ISC Gilberto Quirino
#
#    Modifications:
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
#      <validate_cols>
#
sub vendorsite_user_button{
#############################################################################
#############################################################################
	
	### Verifica que el usuario aún no tenga registro en la tabla users-vendors
	my $sth = &Do_SQL("SELECT COUNT(*) exist FROM admin_users_vendors WHERE id_admin_users = ".$in{'id_admin_users'});
	$exist = $sth->fetchrow();

	if( !$exist and $in{'status'} eq 'Inactive' ){
		$link = '<a id="btnVendorUser" href="/cgi-bin/common/apps/ajaxbuild?ajaxbuild=usrman_vendor&view='.$in{'id_admin_users'}.'" class="fancy_modal_iframe" title="Usuario para proveedores">
	                    <img                     
	                        src="[va_imgurl]/[ur_pref_style]/vendor.png" 
	                        alt="vendor" 
	                        title="To vendor user" 
	                        style="width: 24px;"
	                    >
	                </a>';
	}

    return $link;
}

#############################################################################
#############################################################################
#   Function: user_canelling
#
#       Es: Funcion para dar de baja definitiva a un usuario
#       En: 
#
#
#    Created on: 23/05/2017
#
#    Author: Jonathan Alcantara
#
#    Modifications:
#
#    Parameters:
#
#
#    Returns:
#
#
#   See Also:
#
sub user_canelling {

	use Cwd;
	my($opclegalid) = @_;

	if ($opclegalid > 0) {

		my $dir = getcwd;
		my($b_cgibin,$a_cgibin) = split(/cgi-bin/,$dir);
		my $home_dir = $b_cgibin.'cgi-bin/common';

		#Aplica baja definitiva en todas las empresas

		EMP:for($e = 1; $e <= $cfg{'max_e'}; $e++) {
			next EMP if $in{'e'} eq '$e';		
			my %tmp_cfg;
			if(open (my $cfg, "<", $home_dir.'/general.e'.$e.'.cfg')) {
				LINE: while (<$cfg>) {
					(/^#/)      and next LINE;
					(/^\s*$/)   and next LINE;
					$line = $_;
					$line =~ s/\n|\r//g;
					my ($td,$name,$value) = split (/\||\=/, $line,3);
					if ($td eq "conf" and $name =~ /^dbi_/) {
						$tmp_cfg{$name} = $value;
					}
				}
				close $cfg;
				&connect_db_w($tmp_cfg{'dbi_db'},$tmp_cfg{'dbi_host'},$tmp_cfg{'dbi_user'},$tmp_cfg{'dbi_pw'});

				#Bloqueamos el acceso del usuario por IP, reseteamos password y dejamos el acceso expirado
				#Denegamos todos los permisos que tenia otorgados el usuario

				$db = $tmp_cfg{'dbi_db'};

				my $query = "UPDATE ".$db.".admin_users
							LEFT JOIN ".$db.".admin_users_perms ON admin_users_perms.ID_admin_users = admin_users.ID_admin_users
							SET admin_users.Status = 'Cancel',
							admin_users.IPFilter = '1.1.1.1',
							admin_users.expiration = CURDATE(),
							admin_users.Password = '',
							admin_users_perms.Type = 'Disallow'
							WHERE admin_users.opcLegalID = ".$opclegalid."
							;";
				my ($sth) = &Do_SQL($query,1);
			}
		}
	}
}

1;