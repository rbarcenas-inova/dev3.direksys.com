#!/usr/bin/perl
####################################################################
###
###
###
###        STOP !!!!!!!!!!!!!
###
###
###     NO MODIFICAR RUTINAS EN ESTA APLICACION
###
###
###    SOLO PARA PRUEBA AGREGAR 
###    &cgierr('P-Nombre:comments')  TEMPORALMENTE!!!!!!!!!
###
###
###
####################################################################

	### Auto Get Home_dir
	use Cwd;
	my $dir = getcwd;
	my($b_cgibin,$a_cgibin) = split(/cgi-bin/,$dir);
	my $home_dir = $b_cgibin.'cgi-bin/common';

	($in{'e'}) and ($in{'e'} = int($in{'e'}));

	## Load Common General .ex
	open (CFG, "< $home_dir/general.ex.cfg") or &cgierr ("Unable to open: $home_dir/general.ex.cfg",152,$!);
	LINE: while (<CFG>) {
		(/^#/)      and next LINE;
		(/^\s*$/)   and next LINE;
		$line = $_;
		$line =~ s/\n|\r//g;
		my ($td,$name,$value) = split (/\||\=/, $line,3);
		if ($td eq "conf") {
			$cfg{$name} = $value;
			next LINE;
		}elsif ($td eq "sys"){
			$sys{$name} = $value;
			next LINE;
		}
	}
	close CFG;
	(!$in{'e'} and !&GetCookies("e")) and ($in{'e'} = $cfg{'def_e'});

	if ($in{'e'}>0){
		open (CFG, "<$home_dir/general.e$in{'e'}.cfg") or &cgierr ("Unable to open: general.e$in{'e'}.cfg",150,$!);
		print "Set-Cookie: e=$in{'e'}; path=/;\n";
	}elsif (&GetCookies("e") > 0 and !exists($in{'e'})){
		$in{'e'} = &GetCookies("e");
		open (CFG, "<$home_dir/general.e$in{'e'}.cfg") or &cgierr ("Unable to open: general.e$in{'e'}.cfg",151,$!);
	}
	LINE: while (<CFG>) {
		(/^#/)      and next LINE;
		(/^\s*$/)   and next LINE;
		$line = $_;
		$line =~ s/\n|\r//g;
		my ($td,$name,$value) = split (/\||\=/, $line,3);
		if ($td eq "conf") {
			$cfg{$name} = $value;
			next LINE;
		}elsif ($td eq "sys"){
			$sys{$name} = $value;
			next LINE;
		}
	}
	close CFG;
	$va{'app_title'} = $cfg{'app_title'};


$va{'softversion'} = $cfg{'ver_admin'};


#########################################################
### Authorization
#########################################################

sub auth_check_password {
# --------------------------------------------------------
# 
# Last Modified on: 09/16/09 12:37:29
# Last Modified by: MCC C. Gabriel Varela S: Se habilita cookie multicompa??a
#Last modified on 10 Nov 2010 13:16:08
#Last modified by: MCC C. Gabriel Varela S. : Se habilita lenguaje en yui
#Last modified on 16 Dec 2010 11:23:25
#Last modified by: MCC C. Gabriel Varela S. :Se implementa sha1
#Last modified on 17 Dec 2010 12:27:27
#Last modified by: MCC C. Gabriel Varela S. :Se implementa campo change_pass

	### Load Defaults Vars
	$va{'imgurl'} = $cfg{'path_ns_img'};
	$va{'cgiurl'} = $cfg{'pathcgi'} . $cfg{'pathcgi_admin'};
	$va{'jquery_version'} = $cfg{'jquery_version'};
	$va{'highcharts_version'} = $cfg{'highcharts_version'};
	$va{'yui_url'} = $cfg{'path_yui'};
	
	(!$usr{'pref_maxh'}) and ($usr{'pref_maxh'}=20);
	foreach $key (keys %cfg){
		if ($key =~ /pathcgi_(.*)/){
			$va{'cgiurl_'.$1} = $cfg{'pathcgi'} . $cfg{$key};
		}
	}
	
	#### Load Key
	if ($in{'login'}) {

		###
		##  Possible User Trying to Sign In
		###

		if (!$in{'username'} and !$in{'password'}){
			return '';
		}

		#### Usuarios DB
		&connect_db;
		my ($sth) = &Do_SQL("describe admin_users;");
		my (@cols,@ary);
		while (@ary = $sth->fetchrow_array() ) {
			push(@cols,$ary[0]);
		}
		
		### Search Usuario ###
		my ($sth) = &Do_SQL("SELECT * FROM admin_users WHERE Username='$in{'username'}' AND Status='Active' AND (expiration>Curdate() or isNULL(expiration) or expiration = '0000-00-00');");
		my ($rec) = $sth->fetchrow_hashref;
		my $lenpass=length($rec->{'Password'});
		use Digest::SHA1;
		my $sha1= Digest::SHA1->new;
		$sha1->add($in{'password'});
		my $password = $sha1->hexdigest;

		if ((($lenpass=13 and lc($rec->{'Username'}) eq lc($in{'username'}) and crypt($in{'password'},substr(crypt($in{'password'},'ns'),3,7)) eq $rec->{'Password'})or($lenpass=40 and lc($rec->{'Username'}) eq lc($in{'username'}) and $password eq $rec->{'Password'}) ) and $rec->{'Status'} eq 'Active'){

			if (&check_ip(&get_ip,$rec->{'IPMask'})){

				COLS: for (0..$#cols){
					($cols[$_] eq "Password") and (next COLS);
					$usr{lc($cols[$_])} = $rec->{$cols[$_]};
				}
				
				if ($usr{'change_pass'} eq 'Yes'){
					$in{'cmd'}='myprefs_mypass';
					print "Location: /cgi-bin/mod/$usr{'application'}/admin?cmd=myprefs_mypass\n\n";
				}
				
				
				srand( time() ^ ($$ + ($$ << 15)) );
				$sid = $usr{'id_admin_users'} .'-'.(int(rand(100000)) + 1) .  time() . (int(rand(1000000000)) + 1);
				(!$usr{'pref_maxh'}) and ($usr{'pref_maxh'}=20);
				(!$usr{'pref_style'}) and ($usr{'pref_style'}="default");
				#($usr{'table_width'}>0) or ($usr{'table_width'}="860");
				$usr{'table_width'} = "100%";


				if ($in{'password'} eq 'admin' or $in{'password'} eq '12345'){
					$usr{'change_pass'} = 'Yes';
				}
				
				$usr{'pref_language'} = 'en';
				$usr{'pref_language'} = $rec->{'pref_language'}if($rec->{'pref_language'}ne'');
				$va{'yui_url'}=~s/\[lang\]/$usr{'pref_language'}/gi;
				
				&save_auth_data;
				&sameid_cleanup;
				
				# Update LastLogin
				($sth) = &Do_SQL("UPDATE admin_users SET LastLogin=NOW(),LastIP='".&get_ip."' WHERE ID_admin_users='$usr{'id_admin_users'}';");

				print "Set-Cookie: $cfg{'ckname'}=$sid; path=/;\n";
				print "Set-Cookie: nshelp=On; path=/;\n";
				&auth_logging('login','');

				$tpath = $cfg{'path_templates'};
				$tpath =~ s/\[lang\]/$usr{'pref_language'}/gi;
				
				return 'ok';

			}else{

				&auth_logging('log_unauthlogin',"$in{'username'}/$in{'password'} \@ ". &get_ip );
				return &trans_txt('log_unauthlogin');
			
			}

		}

		&auth_logging('log_invalidlogin',"$in{'username'} \@ ". &get_ip );
		return &trans_txt('log_invalidlogin');		
	
	}else{

		###
		##  User Already Signed In
		###

		if($in{'sid'} and $cfg{'api_key'} and $in{'sid'} eq $cfg{'api_key'}){
			return 'ok';
		}
		if ($in{'sid'} and $in{'e'}){
			$sid = $in{'sid'};
		}else{
			$sid = &GetCookies("$cfg{'ckname'}");
		}

		if ($sid){

			if (!-e "$cfg{'auth_dir'}/$sid" and $cfg{'gensessiontype'} ne 'mysql') {
				return &trans_txt('log_sesexpired');
			}

			## Load Session & Perms
			%usr = &load_session("$cfg{'auth_dir'}",$sid);
			%perm = &load_permission("$cfg{'auth_dir'}",$sid) if $cfg{'memcached'};


			if (!$usr{'id_admin_users'}){
				return &trans_txt('log_sesexpired');
			}
			
			if($usr{'change_pass'} eq 'Yes' and $in{'cmd'} ne 'myprefs_mypass'){
				$in{'cmd'}='myprefs_mypass';
				print "Location: /cgi-bin/mod/$usr{'application'}/admin?cmd=myprefs_mypass\n\n";
			}
			
			$va{'yui_url'}=~s/\[lang\]/$usr{'pref_language'}/gi;

			&auth_cleanup(0);
			&sameid_cleanup;
			(!$usr{'pref_maxh'}) and ($usr{'pref_maxh'}=20);
			($usr{'table_width'}>0) or ($usr{'table_width'}="860");
			$usr{'table_width'} = "100%";
			
			### Lists for the user?
			# my ($sth) = &Do_SQL("SELECT COUNT(*) FROM sl_lists WHERE ID_users = $usr{'id_admin_users'} ");
			# $usr{'lists'} = '1'	if $sth->fetchrow > 0;

			$tpath = $cfg{'path_templates'};
			$tpath =~ s/\[lang\]/$usr{'pref_language'}/gi;

			# Update LastLogin
			if( $in{'cmd'} eq 'changee' ){
				&Do_SQL("UPDATE admin_users SET LastLogin=NOW(),LastIP='".&get_ip."' WHERE ID_admin_users='$usr{'id_admin_users'}';");
				&auth_logging('login','');
			}
			## For password expiration warning!
			$va{'days_until_expiration'} = ( date_to_unixtime( $usr{'expiration'}) - date_to_unixtime(get_sql_date()) ) ;
			$va{'days_until_expiration'} = ($va{'days_until_expiration'} > $cfg{'days_advise_expiration'})? 0:$va{'days_until_expiration'};
			$va{'days_expiration'} =  $cfg{'days_advise_expiration'};

			return 'ok';
		}else {
			return &trans_txt('nologin');
		}
	}
}

sub load_session {
# --------------------------------------------------------
# Last Modified on: 11/08/10 12:54:31
# Last Modified by: MCC C. Gabriel Varela S: Se toma en cuenta pref_language de $usr
# Last Modified by: @ivanmiranda: Control para segurización de sesiones
	my ($dir,$ses)= @_;
	my (%tmp,$line,@ary,$cache_flag);

	if( $cfg{'memcached'} ){

		###
		##  Memcache Data
		###
		(%tmp) = %{$va{'cache'}->get('e' . $in{'e'} . '_' .$ses)};
		

	}

	if(!$tmp{'id_admin_users'}){

		###
		##   Data is not loaded yet.
		###
		$cache_flag = 1 if $cfg{'memcached'};


		if ($cfg{'gensessiontype'} eq 'mysql'){

			@ary = split(/\n/, &load_name('admin_sessions','ses',$ses,'Content'));
			$ipAcceso = &load_name('admin_sessions','ses',$ses,'ip');
			
			LINE:for my $i (0..$#ary){

				($ary[$i] =~ /([^=]+)=(.*)/) or (next LINE);
				$tmp{$1} = $2;

			}

			#Evitar clonación de cookie
			# if($ipAcceso ne '' and $ipAcceso ne get_ip()) {
			# 	&Do_SQL("DELETE FROM admin_sessions WHERE ses='$sid'");
			# 	&Do_SQL("INSERT INTO admin_logs SET LogDate=CURDATE(),LogTime=CURTIME(), ID_admin_users='$tmp{'id_admin_users'}', Type='Access', Message='SECURITY', Action='Intento de clonacion de cookie $sid', IP='" . &get_ip . "'");
			# 	die("ALERTA DE SEGURIDAD - Este intento de acceso sera reportado");
			# 	return 0;
			# } else {
				
				#Control de cookie clonada
				# my($sth) = &Do_SQL("SELECT * FROM admin_logs WHERE Message='SECURITY' AND Action like '%$sid%' AND ID_admin_users='$tmp{'id_admin_users'}' LIMIT 1;");
				# if($log = $sth->fetchrow_hashref) {
				# 	&cgierr($log->{'Action'});
				# }
				
				#Control de colisión de sesiones
				# my($sth) = &Do_SQL("SELECT * FROM admin_logs WHERE Message='SECURITY' AND Action = 'Cierre de sesiones duplicadas para el usuario $sid' AND LogDate=CURDATE() AND TIMEDIFF(LogTime,CURTIME()) < '-00:01:00' LIMIT 1;");
				# if($log = $sth->fetchrow_hashref) {
				# 	&cgierr($log->{'Action'});
				# }
				
				# Alejandro Diaz::04052016::Se comenta update
				# my($sth) = &Do_SQL("UPDATE admin_sessions SET ExpDateTime=NOW(),InModule='$tmp{'application'}' WHERE ses='$sid'");
			# }
		}else{
			open(AUTH, "+<$dir$ses") or &cgierr("Unable to open file: $dir$ses",602,$!);
			LINE: while (<AUTH>) {
				$line = $_;
				$line =~ s/\r|\n//g;
				($line =~ /([^=]+)=(.*)/) or (next LINE);
				$tmp{$1} = $2;
			}
			print AUTH " ";
			close AUTH;
		}

		$tmp{'pref_language'} = &load_name('admin_users','ID_admin_users',$tmp{'id_admin_users'},'pref_language');
		(!$tmp{'pref_language'}) and ($tmp{'pref_language'}=$cfg{'default_lang'});
		$tmp{'pref_language'} = 'en';
		
		### Dial Extension
		if ($tmp{'extension'} and $in{'sitdialnum'}){
			&send_cmd_to_ast( qq|ACTION: Originate\nChannel: $tmp{'extension'}\nExten: $in{'sitdialnum'}\nPriority: 1\nContext: from-internal\nAsync: True\nCallerid: <$in{'sitdialnum'}>\n\n|);

		}
		# Path to Images
		$va{'imgurl'} =  $cfg{'path_ns_img'};
		$va{'script_url'} = $script_url;
		
		### Check Password
		my ($pass) = &load_name('admin_users','ID_admin_users',$tmp{'id_admin_users'},'Password');
		if ($pass eq 'QXaeBTC2ZSiVY' or $pass eq 'ixjh7hkvkrc.s'){
			$tmp{'change_pass'} = 'Yes';
		}
		$va{'rndnumber'} = (int(rand(1000000000)) + 1);
		
		if ($tmp{'application'} eq 'custom'){
			$tmp{'appname'} = $cfg{'app_title'};
		}else{
			$tmp{'appname'} = &trans_txt('appname_'.$tmp{'application'});	
		}

	}else{

		## Session Cached
		$va{'session_cached'} = 2;

	}

	## Set Memcached if flag activated 
	$va{'cache'}->set('e' . $in{'e'} . '_' .$ses,\%tmp) if $cache_flag;
	$va{'session_cached'} = 1 if $cache_flag;
	
	return %tmp;
}


###############################################################################
#   Function: load_permission
#
#       Es: Carga permisos del usuario en hash %perm
#       En: 
#
#   Created by:
#       _RB_
#
#   Modified By:
#   	
#
#   Parameters:
#
#       ID_products
#
#   Returns:
#   
#   	Cost
#
sub load_permission {
###############################################################################

	my ($dir,$ses)= @_;
	my (%tmp,$line,@ary,$cache_flag,$tp);

	if( $cfg{'memcached'} ){

		###
		##  Memcache Data
		###
		(%tmp) = %{$va{'cache'}->get('e' . $in{'e'} . '_perm_' .$ses)};

	}

	if(!$tmp{'id_admin_users'}){

		###
		##   Data is not loaded yet.
		###
		$cache_flag = 1 if $cfg{'memcached'};

		if(!$usr{'id_admin_users'}){

			my ($sth) = &Do_SQL("SELECT CreatedBy FROM admin_sessions WHERE ses = '". $ses ."' AND Date(CreatedDateTime) = CURDATE() ORDER BY CreatedDateTime DESC LIMIT 1;");
			my ($this_id) = $sth->fetchrow();
			$usr{'id_admin_users'} = $this_id;

		}
		return if !$usr{'id_admin_users'}; 

		## Group Perms
		$sth = &Do_SQL("SELECT 
							admin_groups_perms.application
							, admin_groups_perms.command
							, 'Disallow' AS Type
						FROM
							admin_users_groups INNER JOIN admin_groups_perms
							ON admin_users_groups.ID_admin_groups = admin_groups_perms.ID_admin_groups
						WHERE
							admin_users_groups.ID_admin_users = ". $usr{'id_admin_users'} ."
						ORDER BY
							admin_groups_perms.application
							, admin_groups_perms.command;");
		while( my ($this_app, $this_command, $this_type) = $sth->fetchrow()){

			++$tp;
			$this_command = $this_app . '_' . $this_command if $this_app;
			$tmp{$this_command} = $this_type;

		}

		## User Perms
		$sth = &Do_SQL("SELECT 
							admin_users_perms.application
							, admin_users_perms.command
							, admin_users_perms.`Type`
						FROM
							admin_users_perms
						WHERE
							admin_users_perms.ID_admin_users = ". $usr{'id_admin_users'} ."
						ORDER BY
							admin_users_perms.application
							, admin_users_perms.command;");
		while( my ($this_app, $this_command, $this_type) = $sth->fetchrow()){

			++$tp;
			$this_command = $this_app . '_' . $this_command if $this_app;
			$tmp{$this_command} = $this_type;

		}

		$tmp{'id_admin_users'} = 1; ## Only as a flag to know if does cache perms exists
		$t = 'MC: 1';


	}else{

		## Cached Data
		$va{'permission_cached'} = 2;
		$t = 'MC: 2';

	}

	## Set Memcached if flag activated 
	$va{'cache'}->set('e' . $in{'e'} . '_perm_' .$ses,\%tmp) if $cache_flag;
	$va{'permission_cached'} = 1 if $cache_flag;
	

	return %tmp;
}


sub auth_logging {
# --------------------------------------------------------
	my ($message,$action,$mode) = @_;

	(!$usr{'id_admin_users'}) and ($usr{'id_admin_users'} = 0);
	$action =~ s/<li>/ /g;
	$action =~ s/<\/li>/, /g;
	if ($message eq 'login' or $message eq 'logout'){
		$type = 'Access';
	}else{
		$type = 'Application';
	}

	my ($sth);

	&connect_db;
	$value = "LogDate=CURDATE(),LogTime=CURTIME(), ID_admin_users='$usr{'id_admin_users'}', tbl_name='$in{'db'}',Logcmd='$in{'cmd'}', Type='$type', application='".$usr{'application'}."', Message='".&filter_values($message)."', Action='".&filter_values($action)."', IP='" . &get_ip . "'";

	if ($in{'cmd'} ne 'home' and $in{'cmd'} ne 'changee' and $in{'cmd'} ne 'changemod' and $usr{'id_admin_users'} != 0){
		if($mode == 1){
			$sth = &Do_SQL("INSERT INTO admin_logs SET $value",1);
		}else{
			$sth = &Do_SQL("INSERT INTO admin_logs SET $value");
		}
	}
}

sub auth_logging2 {
# --------------------------------------------------------
	my ($message,$action) = @_;
	(!$usr{'id_admin_users'}) and ($usr{'id_admin_users'} = 0);
	$action =~ s/<li>/ /g;
	$action =~ s/<\/li>/, /g;
	if ($message eq 'login' or $message eq 'logout'){
		$type = 'Access';
	}else{
		$type = 'Application';
	}

	&connect_db;
	$value = "LogDate=Curdate(),LogTime=NOW(), ID_admin_users='$usr{'id_admin_users'}', tbl_name='$in{'db'}',Logcmd='$in{'cmd'}', Type='$type', application='".$usr{'application'}."', Message='".&filter_values($message)."', Action='".&filter_values($action)."', IP='" . &get_ip . "'";

	if ($in{'cmd'} ne 'home' and $in{'cmd'} ne 'changee' and $in{'cmd'} ne 'changemod' and $usr{'id_admin_users'} != 0){
		my ($sth) = &Do_SQL("INSERT INTO admin_vlogs SET $value");
	}
}


sub chgs_logging {
# --------------------------------------------------------
	
}

sub sid_dv {
# --------------------------------------------------------
	my ($input) = @_;
	my ($lg,$dv,$tot);
	$input .= &get_ip;
	$lg = length($input);
	for (0..$lg){
		$tot += ord(substr($input,$_,1)) + ord(substr($input,$_+1,1)) - 30 - $_;
	}
	$dv = int(($tot/11-int($tot/11))*11);
	($dv==10) and ($dv='K');
	return $dv;

}

sub check_sid {
# --------------------------------------------------------
	my ($input) = @_;
	my ($lg,$tot,$dv);

	$idv = substr($input,-1);
	$input = substr($input,0,-1) . &get_ip;
	$lg = length($input);
	for (0..$lg){
		$tot += ord(substr($input,$_,1)) + ord(substr($input,$_+1,1)) - 30 - $_;
	}
	$dv = int(($tot/11-int($tot/11))*11);
	($dv==10) and ($dv='K');

	if ($dv eq $idv){
		return 'ok';
	}else{
		return 'error';
	}
}

sub check_ip {
# --------------------------------------------------------
	my ($ip, $ipfilter) = @_;
	my (@ip) = split(/\./,$ip,4);
	my (@allowip) = split(/\,/,$ipfilter,4);
	for (0..$#allowip){
		my (@ipfilter) = split(/\./,$allowip[$_],4);
		for (0..3){
			if ($ip[$_] ne $ipfilter[$_] and $ipfilter[$_] ne 'x'){
				return 0;
			}
		}
	}
	return 1;
}

sub get_ip {
# --------------------------------------------------------
	use CGI;

	my $q = CGI->new;
	my %headers = map { $_ => $q->http($_) } $q->http();

	if ($headers{'HTTP_X_REAL_IP'}){
		return $headers{'HTTP_X_REAL_IP'};
	}elsif ($ENV{'REMOTE_ADDR'}){
		return $ENV{'REMOTE_ADDR'};
	}elsif ($ENV{'REMOTE_HOST'}){
		return $ENV{'REMOTE_HOST'};
	}elsif ($ENV{'HTTP_CLIENT_IP'}){
		return $ENV{'HTTP_CLIENT_IP'};
	}else{
		return "Unknow";
	}
}

sub save_auth_data {
# --------------------------------------------------------
	my ($key,$output);
	COLS: foreach $key (sort keys %usr) {
		($key eq "Password") and (next COLS);
		$output .= "$key=$usr{$key}\n";
	}	

	if ($cfg{'gensessiontype'} eq 'mysql'){

		my($sth) = &Do_SQL("UPDATE admin_sessions SET Content='". &filter_values($output)."',InModule='". $usr{'application'} ."', ExpDateTime=NOW() WHERE ses = '". $sid ."';");

	}else{

		open(AUTH, ">$cfg{'auth_dir'}/$sid") or &cgierr("Unable to open file: $cfg{'auth_dir'}/$sid",603,$!);
		print AUTH $output;
		close AUTH;

	}

	&memcached_delete('e' . $in{'e'} . '_' . $sid) if $cfg{'memcached'};
	# Path to Images
	$va{'imgurl'} =  $cfg{'path_ns_img'};
}

sub auth_cleanup {
# --------------------------------------------------------
	my ($d_sid)=@_;
	my (@files);
	my ($auttime) = 21600;
	if ($d_sid){
		unlink ("$cfg{'auth_dir'}/$d_sid");
		#unlink ("$cfg{'auth_dir_egw'}/$file");
		print "Set-Cookie: $cfg{'ckname'}=0; expires=; path=/;\n";
		print "Set-Cookie: kp3=0; expires=; path=/;\n";
		print "Set-Cookie: sessionid=0; expires=; path=/;\n";
	}else{
		## Session Files
		for my $i(1..$cfg{'max_e'}){
			if ($cfg{'gensessiontype'} eq 'mysql'){
				#Se creó un un cron (auth_cleanup_mysql) para este proceso
				#my($sth) = &Do_SQL("DELETE FROM admin_sessions WHERE TIMESTAMPDIFF(SECOND,ExpDateTime,NOW()) > 21600");
			}else{
				opendir (AUTHDIR, "$cfg{'genauth_dir'}/e$i/") || &cgierr("Unable to open directory $cfg{'genauth_dir'}/e$i/",604,$!);
					@files = readdir(AUTHDIR);		# Read in list of files in directory..
				closedir (AUTHDIR);
				FILE: foreach $file (@files) {
					next if ($file =~ /^\./);		# Skip "." and ".." entries..
					next if ($file =~ /^index/);		# Skip index.htm type files..
					if ((stat("$cfg{'genauth_dir'}/e$i/$file"))[9] + $auttime < time) {
						if ($file =~ /^call/){
							&save_inorder($file);
						}
						unlink ("$cfg{'genauth_dir'}/e$i/$file");		# Delete the file if it is too old.
					}
				}			
			}
		}
	}
}

sub sameid_cleanup {
# --------------------------------------------------------
	if (!$cfg{'auth_sameid'}){
		return;
	}
	if ($cfg{'gensessiontype'} eq 'mysql'){
		my($sth) = &Do_SQL("DELETE FROM admin_sessions WHERE CreatedBy=$usr{'id_admin_users'} AND ses NOT IN ('$sid','call$sid')");
	}else{
		## Session Files
		opendir (AUTHDIR, "$cfg{'auth_dir'}") || &cgierr("Unable to open directory $cfg{'auth_dir'}",604,$!);
			@files = readdir(AUTHDIR);		# Read in list of files in directory..
		closedir (AUTHDIR);
		FILE: foreach $file (@files) {
			next if ($file =~ /^\./);		# Skip "." and ".." entries..
			next if ($file =~ /^index/);		# Skip index.htm type files..
			if ($file =~ /^$usr{'id_admin_users'}-\d+/ and $file ne $sid and $file !~ /^call/){
				unlink ("$cfg{'auth_dir'}/$file");		# Delete the file User Already logged in
			}elsif ($file =~ /^call$usr{'id_admin_users'}-\d+/ and $file ne "call$sid"){
				&save_inorder($file);
				unlink ("$cfg{'auth_dir'}/$file");
			}
		}
	}
}


##############################################################
########         CREATINMG THE KEY      ######################
##############################################################


sub encode_info {
# --------------------------------------------------------
	my ($input) = @_;
	my ($output,$c,$offset);
	my ($l) = length($input);
	for (0..$l){
		$output .= dec2hex(ord(substr($input,$_,1)));
	}
	$offset = int(rand($l/3)+$l/3);
	($offset<10) and($offset = "00$offset");
	($offset<100 and $offset>10) and ($offset = "0$offset");
	return $offset . substr($output,$offset) . substr($output,0,$offset);
}


sub decode_info {
# --------------------------------------------------------
	my ($input) = @_;
	my ($output,$l);
	$offset = substr($input,0,3);
	$input = substr($input,3);
	$l = length($input);
	$input = substr($input,$l-$offset) . substr($input,0,$l-$offset);	
	for (0..($l/2)-2){
		$output .= chr(hex(substr($input,$_*2,2)));
	}
	return $output;
}

sub get_line_data {
# --------------------------------------------------------
	my ($in,$lookfor) = @_;
	@ary = split(/\n/,$in);
	for (0..$#ary){
		if ($ary[$_] =~ /$lookfor(.*)/){
			return $1;
		}
	}
	return 'not-found' . $in .$lookfor;
}


sub dec2hex {
# --------------------------------------------------------
	# parameter passed to
	# the subfunction
	my $decnum = $_[0];
	# the final hex number
	my $hexnum;
	my $tempval;
	if ($decnum ==0){
		return '00';
	}
	while ($decnum != 0) {
		# get the remainder (modulus function)
		# by dividing by 16
		$tempval = $decnum % 16;
		# convert to the appropriate letter
		# if the value is greater than 9
		if ($tempval > 9) {
			$tempval = chr($tempval + 55);
		}
		# 'concatenate' the number to
		# what we have so far in what will
		# be the final variable
		$hexnum = $tempval . $hexnum ;
		# new actually divide by 16, and
		# keep the integer value of the
		# answer
		$decnum = int($decnum / 16);
		# if we cant divide by 16, this is the
		# last step
		if ($decnum < 16) {
			# convert to letters again..
			if ($decnum > 9) {
				$decnum = chr($decnum + 55);
			}

		# add this onto the final answer..
		# reset decnum variable to zero so loop
		# will exit
		$hexnum = $decnum . $hexnum;
		$decnum = 0
		}
	}
	return $hexnum;
} # end sub



##############################################################
###########   MORE SUBROUTIENS     ###########################
##############################################################

sub GetCookies {
# --------------------------------------------------------
  my(@ReturnCookies) = @_;
  my($cookie_flag) = 0;
  my($cookie,$value);
  if ($ENV{'HTTP_COOKIE'}) {
    if ($ReturnCookies[0] ne '') {
      foreach (split(/; /,$ENV{'HTTP_COOKIE'})) {
        ($cookie,$value) = split(/=/);
        foreach $char (@Cookie_Decode_Chars) {
          $cookie =~ s/$char/$Cookie_Decode_Chars{$char}/g;
          $value =~ s/$char/$Cookie_Decode_Chars{$char}/g;
        }
        foreach $ReturnCookie (@ReturnCookies) {
          if ($ReturnCookie eq $cookie) {
              $Cookies{$cookie} = $value;
              $cookie_flag = $value;
            }
          }
        }
      }else {
        foreach (split(/; /,$ENV{'HTTP_COOKIE'})) {
          ($cookie,$value) = split(/=/);
          foreach $char (@Cookie_Decode_Chars) {
            $cookie =~ s/$char/$Cookie_Decode_Chars{$char}/g;
            $value =~ s/$char/$Cookie_Decode_Chars{$char}/g;
        	}
        	$Cookies{$cookie} = $value;
      	}
      	$cookie_flag = $value;
    	}
  }
  return $cookie_flag;
}

sub num_dv {
# --------------------------------------------------------
	my ($input,$tot) = @_;
	my ($lg,$dv);
	$lg = length($input);
	for (0..$lg){
		$tot += ord(substr($input,$_,1)) + ord(substr($input,$_+1,1)) - 30 - $_;
	}
	$dv = int(($tot/11-int($tot/11))*11);
	($dv==10) and ($dv='K');
	return $dv;
}

sub save_inorder {
# --------------------------------------------------------
	my ($file) = @_;
	my (%tmp,$line);
	if (open(AUTH, "<$cfg{'auth_dir'}/$file")){
		LINE: while (<AUTH>) {
			$line = $_;
			$line =~ s/\r|\n//g;
			($line =~ /([^=]+)=(.*)/) or (next LINE);
			$tmp{$1} = $2;
			$tmp{$1} =~ s/~~/\n/g;
		}
	}
	####### Load Products #######
	my ($sth);
	if ($tmp{'items_in_basket'} > 0){
		for my $i(1..$tmp{'items_in_basket'}){
			if ($tmp{'items_'.$i.'_qty'}>0 and $tmp{'items_'.$i.'_id'}>0){
				($sth) = &Do_SQL("SELECT sl_products.Model, sl_products.SPrice, sl_products.Name FROM sl_products WHERE ID_products='".substr($tmp{'items_'.$i.'_id'},3,6)."'");
				$rec = $sth->fetchrow_hashref;
				$tmp{'products'} .= qq|<li> $tmp{'items_'.$i.'_qty'} x  ($tmp{'items_'.$i.'_id'}) $rec->{'Model'} = |. &format_price($rec->{'SPrice'}). qq|<br>$rec->{'Name'}</a>\n|;
			}
		}
	}else{
		$tmp{'products'} &trans_txt('empty_cart');
	}
	
	####### Load Payments #######
	my (%paytype)  = ('cc'=>'Credit-Card', 'check'=>'Check','wu' => 'Wester Union','mo'=> 'Money Order','fp'=> 'Fexipago');
	$tmp{'payments'} = $paytype{$tmp{'pay_type'}};
	
	####### CREATE IN-ORDER #######
	my (@cols);
	my ($sth) = &Do_SQL("describe sl_inorders;");
	while (@ary = $sth->fetchrow_array() ) {
		push(@cols,$ary[0]);
	}
	my ($query);
	for my $i(1..$#cols-4){
		$query .= "$cols[$i]='".&filter_values($tmp{lc($cols[$i])})."',";
	}
	if ($tmp{'cid'} or $tmp{'FirstName'}){
		my ($sth) = &Do_SQL("INSERT INTO sl_inorders SET $query Status='New',Date=Curdate(),Time=NOW(),ID_admin_users='$usr{'id_admin_users'}'");
	}
}

sub check_permissions {
# --------------------------------------------------------
	my ($cmd,$action,$tab,$debug)= @_;
	my ($stype) = 'admin';
	my ($resp) = 1;
	
	(!$tab) and ($tab=''); ## Delete 0 if tab = 0
	if ($ENV{'SCRIPT_FILENAME'} =~ /dbman/i){
		$stype = 'dbman';
		$va{'formtitle'} = $sys{'db_'.$cmd.'_title_'.$usr{'pref_language'}} if(!$va{'formtitle'});
		$va{'formtitle'} = $sys{'db_'.$cmd.'_title'} if(!$va{'formtitle'});
		$va{'expanditem'}= $sys{'db_'.$cmd.'_menu'} if ($sys{'db_'.$cmd.'_menu'});
		$va{'expanditem'} = $in{'expanditem'} if ($in{'expanditem'}>0);
		$va{'idform'} = $db_cols[0] if(!$va{'formtitle'});
	}

	while( my( $key, $value ) = each %perm ){
	    $this_hash .= "$key: $value\n";
	}
	
	
	## Memcached Data
	if($perm{$cmd} or $perm{$usr{'application'} . '_' . $cmd} or $perm{$cmd.$action.$tab} or $perm{$usr{'application'} . '_' . $cmd.$action.$tab}){
		
		if ($perm{$cmd} eq 'Allow' or $perm{$usr{'application'} . '_' . $cmd} eq 'Allow' or $perm{$cmd.$action.$tab} eq 'Allow' or $perm{$usr{'application'} . '_' . $cmd.$action.$tab} eq 'Allow'){
			return 1;
		}else{
			#&cgierr("\n" . $usr{'application'} . '_' . $cmd.$action.$tab . ' = ' . $perm{$usr{'application'} . '_' . $cmd.$action.$tab} . " \n ". $cmd.$action.$tab . " = ". $perm{$cmd.$action.$tab} ."\n " . $cmd . " = " . $perm{$usr{'application'} . '_' . $cmd} ."\n\n" . $this_hash) if $debug;
			&auth_logging('Permission ' . $cmd . ' unauthorized', 'Check Permission');
			return 0;
		}

	}
	return $resp if $perm{'id_admin_users'}; ## Flag, indicates perm are cached and not disallow value found to this action

    if (!$cfg{'cd'} and $cmd){  
        $sth = &Do_SQL("SELECT COUNT(*) FROM admin_perms WHERE  application='". $usr{'application'} ."' AND command = '". $cmd ."' AND type = '". $stype ."';");
        if (!$sth->fetchrow()){
        	&auth_logging2('Permission ' . $cmd . ' unauthorized', 'Check Permission');
            return 0;
        }
    }


    # Verifica si el comando tiene registro por IP, si no lo tiene registro no es necesario validar su IP de procedencia
    $sth = &Do_SQL("SELECT count(*) FROM admin_perms_ip WHERE command = '". $cmd ."' AND Status = 'Active';");
    if ( $sth->fetchrow() )
    {
        # ..si lo tiene verifica que si la IP coincide con la procedencia
        my $current_ip = &get_ip;

        $sth = &Do_SQL("SELECT count(*) FROM admin_perms_ip WHERE command = '". $cmd ."' AND ip='".$current_ip."' AND Status = 'Active';");
        if (!$sth->fetchrow())
        {
        	&auth_logging('Permission ' . $cmd . ' unauthorized', 'Check Permission');
            return 0;
        }
    }

	if($cmd =~ /\.\.|\//){ return 0; };
	
	$sth = &Do_SQL("SELECT IF(COUNT(*)>0,Type,'None') FROM admin_users_perms WHERE ID_admin_users = '". $usr{'id_admin_users'} ."' AND application = '". $usr{'application'} ."' AND (command='".&filter_values($cmd.$action.$tab)."' OR command='".&filter_values($cmd)."');");
	my ($utype) = $sth->fetchrow();
	
	$sth = &Do_SQL("SELECT 
						IF(COUNT(*) > 0,'Disallow','Allow') 
					FROM 
						admin_groups_perms 
					WHERE 
						(ID_admin_groups IN 
							(SELECT 
								admin_users_groups.ID_admin_groups 
							FROM 
								admin_users_groups LEFT JOIN admin_groups ON admin_groups.ID_admin_groups = admin_users_groups.ID_admin_groups  
							WHERE 
								admin_users_groups.ID_admin_users = '". $usr{'id_admin_users'} ."' 
								AND Status='Active'
							)
				 		OR ID_admin_groups = 0) 
						AND application = '". $usr{'application'} ."' 
						AND (command = '".&filter_values($cmd.$action.$tab)."' 
							OR command='".&filter_values($cmd)."')
					;");
	my ($gtype) = $sth->fetchrow();
	
	if ($utype eq 'Disallow' or ($gtype eq 'Disallow' and  $utype ne 'Allow')){
		&auth_logging('Permission ' . $cmd . ' unauthorized', 'Check Permission');
		$resp = 0
	}
	
	## If direksys is in Debug Mode, check for the permisions Tree
	if ($cfg{'cd'} and $cmd and $stype){
		$sth = &Do_SQL("SELECT count(*) FROM admin_perms WHERE 1 AND application='$usr{'application'}' AND command='$cmd' AND type='$stype';");
		if ($sth->fetchrow == 0){
			my $add_tabs = ($tab>0)?" tabs='$tab',":" tabs='0',";
			$sth = &Do_SQL("INSERT IGNORE admin_perms SET $add_tabs application='$usr{'application'}', command='$cmd', type='$stype',Date=CURDATE(),Time=NOW(),ID_admin_users='$usr{'id_admin_users'}'");
		}elsif ($tab>0 and $stype eq 'dbman'){
			$sth = &Do_SQL("UPDATE admin_perms SET tabs=$tab WHERE application='$usr{'application'}' AND command='$cmd' AND type='$stype' AND tabs<$tab");
		}
	}
	$sth = &Do_SQL("SELECT Name FROM admin_perms WHERE application='$usr{'application'}' AND command='$cmd' AND type='$stype' AND Status='Active'");
	$va{'page_title'} = $sth->fetchrow();
	(!$va{'page_title'}) and ($va{'page_title'} = $cfg{'company_name'});
	
	return $resp;
}

sub load_callsession {
# --------------------------------------------------------
	if ($cfg{'gensessiontype'} eq 'mysql'){
		@ary = split(/\n/, &load_name('admin_sessions','ses',"call$sid",'Content'));
		LINE:for my $i (0..$#ary){
			($ary[$i] =~ /([^=]+)=(.*)/) or (next LINE);
			$cses{$1} = $2;
			$cses{$1} =~ s/~~/\n/g;
		}
		# Alejandro Diaz::04052016::Se comenta update
		# my($sth) = &Do_SQL("UPDATE admin_sessions SET ExpDateTime=NOW(),InModule='Sales' WHERE ses='call$sid'");
	}else{
		if (open(my $auth, "+<", "$cfg{'auth_dir'}/call$sid")){
			LINE: while (<$auth>) {
				$line = $_;
				$line =~ s/\r|\n//g;
				($line =~ /([^=]+)=(.*)/) or (next LINE);
				$cses{$1} = $2;
				$cses{$1} =~ s/~~/\n/g;
			}
			print $auth " ";
		}
	}
	return;
}

sub save_callsession {
# --------------------------------------------------------
	my ($deleteall) = @_;
	if ($deleteall){
		if ($cfg{'gensessiontype'} eq 'mysql'){
			my($sth) = &Do_SQL("DELETE FROM admin_sessions WHERE ses='call$sid'");
		}else{
			unlink("$cfg{'auth_dir'}/");
			foreach my $key (keys %cses){
				delete($cses{$key});
			}
		}
		return;
	}
	my ($key,$output,$data);
	foreach my $key (sort keys %cses) {
		$data = $cses{$key};
		$data =~ s/\n/~~/g;
		$output .= "$key=$data\n";
	}
	
	if ($cfg{'gensessiontype'} eq 'mysql'){
		##my($sth) = &Do_SQL("REPLACE INTO admin_sessions SET ses='call$sid',InModule='Sales', Content='".&filter_values($output)."', CreatedBy=$usr{'id_admin_users'}, CreatedDateTime=NOW(),ExpDateTime=NOW();");
		my($id) = &load_name('admin_sessions','ses',"call$sid",'ID_admin_sessions');
		if ($id>0){
			my($sth) = &Do_SQL("UPDATE admin_sessions SET Content='". &filter_values($output)."',InModule='$usr{'application'}', ExpDateTime=NOW() WHERE ses='call$sid'");
		}else{
			my($sth) = &Do_SQL("INSERT INTO admin_sessions SET ses='call$sid',InModule='Sales', Content='".&filter_values($output)."', CreatedBy=$usr{'id_admin_users'}, CreatedDateTime=NOW(),ExpDateTime=NOW(),ip='".get_ip()."';");
		}
	}else{
		if (open(my $auth, ">", "$cfg{'auth_dir'}/call$sid")){		 
			print $auth $output;
		}else{
			&cgierr("Unable to open file: $cfg{'auth_dir'}/call$sid",703,$!);
		}
	}
}

#############################################################################
#############################################################################
#   Function: status_logging
#
#       Es: Registra los cambios de estatus de los pedidos
#       En: Records changes in order status
#
#
#    Created on: 2014-01-16
#
#    Author: Alejandro Diaz
#
#    Modifications:
#
#        - Modified on **: 
#			 FC on 2018-01-22
#				Se comenta funcion, esta tarea se realiza a traves de un trigger.
#   Parameters:
#
#		 - ID_orders int
#		 - Status string
#	
#  Returns:
#
#
#   See Also:
#
#
#
sub status_logging {
#############################################################################
#############################################################################
	
	return;
	
}

1;