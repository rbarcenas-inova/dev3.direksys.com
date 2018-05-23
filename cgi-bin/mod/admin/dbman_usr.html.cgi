
##########################################################
##		PERM MANAGER
##########################################################
sub view_usrptree{
# --------------------------------------------------------
# Created on: 09/23/08 @ 15:13:52
# Author: Carlos Haas
# Last Modified on: 09/23/08 @ 15:13:52
# Last Modified by: Carlos Haas
# Description : 
# Parameters : 
#			   
	if ($in{'id_parent'}){
		$va{'parent'} = &load_name('admin_perms','ID_perms',$in{'id_parent'},'Name')
	}else{
		$va{'parent'} = &trans_txt('top_level');
	}
}

sub validate_usrptree{
# --------------------------------------------------------
# Created on: 09/23/08 @ 15:13:46
# Author: Carlos Haas
# Last Modified on: 09/23/08 @ 15:13:46
# Last Modified by: Carlos Haas
# Description : 
# Parameters : 
#			   
	# my ($query,$err);
	# $in{'id_perms'} = int($in{'id_perms'});
	# if ($in{'id_perms'}){
	# 	$sth = &Do_SQL("+SELECT COUNT(*) FROM admin_perms WHERE ID_admin_perms!='$in{'id_perms'}' AND application='$in{'application'}' AND command='".&filter_values($in{'perm'})."'");
	# }else{
	# 	$sth = &Do_SQL("-SELECT COUNT(*) FROM admin_perms WHERE ID_admin_perms!='$in{'id_perms'}' AND application='$in{'application'}' AND command='".&filter_values($in{'perm'})."'");
	# }
	# if ($sth->fetchrow>0){
	# 	$error{'perm'} = &trans_txt('invalid');
	# 	++$err;
	# }
	
	# return $err;
}



##########################################################
##	ADMINISTRATIONS : ADMIN USERS 		          ##
##########################################################
sub loaddefault_usrgroup{
# --------------------------------------------------------
#Last modified on 11 May 2011 13:10:14
#Last modified by: MCC C. Gabriel Varela S. : Se hace que ipfilter sea igual al usuario que lo crea.
	#Se obtiene ipfilter del creador
	my $created_by_ipfilter=&load_name('admin_users','ID_admin_users',$usr{'id_admin_users'},'ipfilter');
	$in{'ipfilter'} = $created_by_ipfilter;
	$in{'status'} = 'Active';
	$in{'never_expires'} = 'on';
}

sub view_usrgroup {
# --------------------------------------------------------
# Forms Involved: 
# Created on: 
# Last Modified on: 9/07/2007 5:01PM
# Last Modified by: Rafael Sobrino
# Author: Rafael Sobrino
# Description : 
#Last modified on 11 May 2011 13:53:03
#Last modified by: MCC C. Gabriel Varela S. : Se corrige problema de mostrar verdadero nombre del creador

	$in{'createdby.firstname'}=&load_name('admin_users','ID_admin_users',$in{'createdby'},'Firstname');
	$in{'createdby.lastname'}=&load_name('admin_users','ID_admin_users',$in{'createdby'},'LastName');
	if (!$in{'id_parent'}){
		$in{'parentname'} = &trans_txt('top_level');
	}else{
		$in{'parentname'} = &load_name('sl_categories','ID_categories',$in{'id_parent'},'Title');
	}
	
	if ($in{'expiration'} eq ""){
		$va{'expiration'} = &trans_txt("no_expiration");
	}else{
		$va{'expiration'} = $in{'expiration'};
	}
	
	(!$in{'opcnotes'}) and ($in{'opcnotes'} = '---');
	
}

sub validate_usrgroup {
# --------------------------------------------------------
# Created on: 1/1/2007 9:43AM
# Last Modified on:
# Last Modified by:
# Author: 
# Description : 
# Parameters :
# Last Modified RB: 03/18/09  10:12:26 -- LastLogin initialization 
#Last modified on 16 Dec 2010 11:07:12
#Last modified by: MCC C. Gabriel Varela S. :Se incorpora sha1
#Last modified on 11 May 2011 12:56:15
#Last modified by: MCC C. Gabriel Varela S. : Hacer que el usuario creado tenga el mismo ipfilter que el que lo crea.
#Last modified on 17 May 2011 16:31:59
#Last modified by: MCC C. Gabriel Varela S. : Se hace que las x se tomen como *
#Last modified on 20 May 2011 15:18:09
#Last modified by: MCC C. Gabriel Varela S. :Se hace que el \r sea opcional
 
	my $err;

	#Se evalúa ipfilter (solo no developers)
	if($usr{'usergroup'} > 1){

		#Se obtiene ipfilter del creador
		my $created_by_ipfilter;
		if($in{'id_admin_users'}ne'')
		{#Si se edita
			#obtiene created by
			my $created_by=&load_name('admin_users','ID_admin_users',$in{'id_admin_users'},'CreatedBy');
			$created_by_ipfilter=&load_name('admin_users','ID_admin_users',$created_by,'ipfilter');
		}
		else
		{#Si se crea
			$created_by_ipfilter=&load_name('admin_users','ID_admin_users',$usr{'id_admin_users'},'ipfilter');
		}

		#Se cambia la forma de evaluar la ipfilter de los creados
		my (@ipfilter_values) = split(/\r?\n/,$created_by_ipfilter);
		my $ipfilter_turn;
		my $valid_ip=0;
		my (@ipfilter_values_in) = split(/\r?\n/,$in{'ipfilter'});
		foreach $ipfilter_turn (@ipfilter_values){
	# 		if(!$valid_ip or 1)
	# 		{
				$ipfilter_turn=~s/\./\\\./g;
				$ipfilter_turn=~s/x/\[\\d\|x\]\*/g;
				foreach $ipfilter_turn_in (@ipfilter_values_in)
				{
					if($ipfilter_turn_in=~/$ipfilter_turn/)
					{
	# 					$variable="$ipfilter_turn";
						++$valid_ip;
					}
				}
	# 		}
		}
	#  	cgierr("$variable y valid_ip:$valid_ip y ".($#ipfilter_values_in+1));
		if($valid_ip<($#ipfilter_values_in+1)){
			$error{'ipfilter'} = &trans_txt("invalid");
	# 		$in{'ipfilter'} = $created_by_ipfilter;
			++$err;
		}

	}
	
	if ($usr{'usergroup'} > 2){
		&html_unauth;
		return;
	}
	
	(!$in{'status'}) and ($in{'status'} = 'Active');
	if($in{'username'} and (length($in{'username'})<5 or length($in{'username'})>12)){
		$error{'username'} = &trans_txt("invalid");
		++$err;
	}
	 
	### validate email by rafael 2007-09-05
	if ($in{'email'}){
		if (!&valid_address($in{'email'})){
			$error{'email'} = &trans_txt("invalid");
			++$err;
		}			
	}
	
	$in{'lastlogin'}	=	'NOW()' if $in{'status'}eq 'Active';	
	
	if ($in{'add'}){
		my ($passwd) = &gen_passwd;
		
			use Digest::SHA1;
			my $sha1= Digest::SHA1->new;
			$sha1->add($passwd);
			$in{'password'} = $sha1->hexdigest;
		
		$in{'temppasswd'} = $passwd;

		if($in{'username'}){
			my ($sth) = &Do_SQL("SELECT COUNT(*) FROM admin_users WHERE Username='$in{'username'}';");
			$found = $sth->fetchrow();
			if ($found>0){
				$error{'username'} = &trans_txt("repeated");
				++$err;
			}else{
				### send email with password to the newly created user
				$body = "Your password: $passwd";
				$subject = &trans_txt("admin_email_subject");
				if (send_email("admin\@innovagroupusa.com",$in{'email'},$subject,$body) eq "ok"){
					$va{'email_status'} = &trans_txt("admin_email_success");
				}else{
					$va{'email_status'} = &trans_txt("admin_email_err");
				}				
			}
		}
	}else{
		my ($sth) = &Do_SQL("SELECT COUNT(*) FROM admin_users WHERE Username='$in{'username'}' AND ID_admin_users<>'$in{'id_admin_users'}';");
		$found = $sth->fetchrow();
		if ($found>0){
			$error{'username'} = &trans_txt("repeated");
			++$err;
		}
		$in{'password'} = &load_name('admin_users','ID_admin_users',$in{'id_admin_users'},'Password');
		$in{'temppasswd'} = &load_name('admin_users','ID_admin_users',$in{'id_admin_users'},'tempPasswd');
	}
	
	if ($in{'never_expires'}){
		$in{'expiration'} = 'NULL';
	}
	
	return $err;
}

sub add_usrgroup {
# --------------------------------------------------------
	## Send Email 
	### send password via email by rafael 2007-09-06
	#send_mail("rsobrino@innovagroupusa.com","rsobrino@innovagroupusa.com","etst","test");		
	#$in{'email_passwd'} = &trans_txt("email_passwd");	
}

1;