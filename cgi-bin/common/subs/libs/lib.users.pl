
#############################################################################
#############################################################################
#   Function: chg_multipass
#
#       Es: Ejecuta cambio de clave en todas las empresas donde esta dado de alta el usuario
#       En: Executes password update on all user's companies
#
#
#    Created on: 08/06/09  16:30:22
#
#    Author: _Roberto Barcenas_
#
#    Modifications:
#
#        - Modified on *03/08/2013* by _Roberto Barcenas_ : 
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
#      <myprefs_mypass>
#      <mypass>
#      <usrman_admin>
#
sub chg_multipass {
#############################################################################
#############################################################################
	
	my($username,$password,$days,$chgmod,$tmppswd)	=	@_;

	use Cwd;
	my $dir = getcwd;
	my($b_cgibin,$a_cgibin) = split(/cgi-bin/,$dir);
	my $home_dir = $b_cgibin.'cgi-bin/common';
	
	### Dias para la proxima fecha de expiracion
	$days = 30 if(!$days);
	### Modo en que se esta actualizando el pswd
	### 1 = Por el mismo usuario, los dias para la fecha de expiracion será definida por el parametro $days
	### 2 = Por el admin., en este caso se pondrá expiración de 2 dias(definido por $days) y se activara el campo change_pass
	my $sql_chg_pswd = '';
	$sql_chg_pswd = ",change_pass='Yes'" if( int($chgmod) == 2 );
	$sql_chg_pswd .= ( $tmppswd and int($chgmod) == 2 ) ? ",tempPasswd='$tmppswd'" : ",tempPasswd=NULL, change_pass='No'";

	my $str = '';
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

			$db = $tmp_cfg{'dbi_db'};			
			my ($sth) = &Do_SQL("UPDATE ".$db.".admin_users SET Password='".&filter_values($password)."', expiration = DATE_ADD(CURDATE(), INTERVAL $days DAY) $sql_chg_pswd WHERE userName = '$username';",1);
		}

	}	

}


#############################################################################
#############################################################################
#   Function: get_user_sessid
#
#       Es: Devuelve la sesid del usuario
#       En: 
#
#
#    Created on: 22-05-2017
#
#    Author: _Roberto Barcenas_
#
#    Modifications:
#
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
#    
#
sub get_user_sessid{
#############################################################################
#############################################################################

	my ($sid);

	if($in{'sid'} and $in{'e'}){
		
		$sid = $in{'sid'};

	}elsif($cfg{'ckname'}){
		
		$sid = &GetCookies("$cfg{'ckname'}");

	}elsif($in{'id_admin_users'}){

		my ($sth) = &Do_SQL("SELECT ses FROM admin_sessions WHERE CreatedBy = ". $usr{'id_admin_users'} ." AND Date(CreatedDateTime) = CURDATE() ORDER BY CreatedDateTime DESC LIMIT 1;");
		($sid) = $sth->fetchrow();

	}

	return $sid;

}

1;