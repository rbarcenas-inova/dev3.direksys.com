##########################################################
##		IT 		  ##
##########################################################
sub view_it_jobs {
# --------------------------------------------------------
	if ($in{'id_user'}){
		$in{'id_user_name'} = &load_db_names('admin_users','ID_admin_users',$in{'id_user'},'[FirstName] [LastName]');
	}
	if ($in{'id_departments'}){
		#($db,$id_name,$id_value,$field)
		$in{'id_department_name'} = &load_db_names('sl_departments','ID_departments',$in{'id_departments'},'[Name]');
	}
}

sub del_it_jobs {
# --------------------------------------------------------
# Last Modification by JRG : 03/11/2009 : Se agrega log
	my ($sth) = &Do_SQL("DELETE FROM sl_itjobs_notes WHERE ID_itjobs='$in{'delete'}';");
	&auth_logging('it_jobs_noteadded',$in{'delete'});
}









1;