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







##########################################################
##			Deleting			##
##########################################################
sub html_delete {
# --------------------------------------------------------
	# 190813::AD - Security restricts eliminate
	&html_unauth; return;
	# 190813::AD - Security restricts eliminate


	if(!&check_permissions($in{'cmd'},'_del','')){ &html_unauth; return; };
	
	### Delete Record
	my ($sth) = &Do_SQL("DELETE FROM $in{'db'} WHERE $db_cols[0]='$in{'delete'}';");
	$sth->finish();

	## Page Message
	$va{'message'} = &trans_txt($in{'cmd'}.'_deleted') . " " . $in{'delete'};

     ## Run Other App
     &run_function("del");
     &run_notifs($in{'cmd'}.'_deleted');

	## Save logs
	&auth_logging($in{'cmd'}.'_deleted'," $in{'delete'}");
	&chgs_logging($in{'cmd'}.'_deleted'," $in{'delete'}");
	&run_eafunction("del");

	## Load List All Page w/message
	$in{'search'}='listall';
	&html_search_select;

}



1;
