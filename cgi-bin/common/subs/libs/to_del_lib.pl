sub did_link{
# --------------------------------------------------------
# Forms Involved: 
# Created on: 09/14/09 17:54:06
# Author: MCC C. Gabriel Varela S.
# Description :   
# Parameters :
# Last Modified on: 09/15/09 16:41:43
# Last Modified by: MCC C. Gabriel Varela S: Se valida la existencia de $in{'dnis'}
	return "No DID"if(!$in{'dnis'});
	my $sth=&Do_SQL("Select ID_mediadids from sl_mediadids where DNIS=$in{'dnis'}");
	$dnis=$sth->fetchrow();
	return "No DID"if(!$dnis);
	return "$dnis"
}


sub build_select_usergroups {
# --------------------------------------------------------
# Created :  Carlos Haas 01/01/2007 6:47:28 PM
# Last Update : 
# Locked by : 
# Description :
#
#

	### Build User Groups
#	if ($usr{'username'} eq 'admin' or $usr{'usergroup'} eq 1){
#		$va{'usergroup'} = &build_select_dbfield('usergroup',$in{'usergroup'},'','Name','admin_users_group');
#	}else{
#		$va{'usergroup'} = &build_select_dbfield('usergroup',$in{'usergroup'},'','Name','admin_users_group WHERE ID_admin_users_group<>1');
#	}
}

1;