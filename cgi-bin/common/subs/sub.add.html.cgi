####################################################################
###
###
###
###    STOP !!!!!!!!!!!!!
###
###
###    NO MODIFICAR RUTINAS EN ESTA APLICACION
###
###
###    SOLO PARA PRUEBA AGREGAR 
###    &cgierr('P-Nombre:comments')  TEMPORALMENTE!!!!!!!!!
###
###
###
####################################################################



##########################################################
##			Adding				##
##########################################################
sub html_add_select {
# --------------------------------------------------------
	if(!&check_permissions($in{'cmd'},'_add','')){ &html_unauth; return; };
	
	if($in{'cmd'} eq "opr_orders" and $in{'add'} eq "1"){
		$va{'canceldate_required'}="required";
		$va{'canceldate_format'}="minDate: 0";
	}

	if ($in{'action'}){

		my ($message) = &add_record;
		if ($message eq "ok"){
			&html_add_success;
		}else{
			&html_add_failure;
		}
	}else{
		&html_add_form;
	}
	&run_eafunction('add');
}

##########################################################
##			Adding Process		##
##########################################################

sub add_record {
# --------------------------------------------------------
#Last modified on 15 Aug 2011 15:55:02
#Last modified by: MCC C. Gabriel Varela S. : second_conn is considered

	my ($x,$err,$query);
	$err = &run_function("validate");

	($x,$query) = &validate_cols('1');
	$err += $x;

	#&cgierr();

	my ($sth);
	if ($err==0){
		if ($in{'db'} eq "admin_users"){
			$sth = &Do_SQL("INSERT INTO $in{'db'} SET $query,Date=Curdate(),Time=NOW(),CreatedBy='$usr{'id_admin_users'}';");
		}else{
			my $ins=0;
			$ins=1 if ($in{'second_conn'});
			$sth = &Do_SQL("INSERT INTO $in{'db'} SET $query,Date=Curdate(),Time=NOW(),ID_admin_users='$usr{'id_admin_users'}';",$ins);
		}
		
		if (!$in{'not_autoincrement'}){
			$in{lc($db_cols[0])} = $sth->{'mysql_insertid'};
		}
		if ($sth){$sth->finish();}
		
		&run_function("add");
		&run_notifs($in{'cmd'}.'_added');

		## Page Message
		$va{'message'} = &trans_txt($in{'cmd'}.'_added') . "  " . $in{lc($db_cols[0])};

		## Save logs
		&auth_logging($in{'cmd'}.'_added',$in{lc($db_cols[0])});
		return ("ok");
	}else {
		return $status;
	}
}


##########################################################
##			Add Forms			##
##########################################################
sub html_add_form {
# --------------------------------------------------------
#Last modified on 29 Oct 2010 15:51:37
#Last modified by: MCC C. Gabriel Varela S. :Se incorpora opción de nuevo look
	print "Content-type: text/html\n\n";
	&run_function("loaddefault");

	my ($fname) = $cfg{'path_templates'}."/mod/".$usr{'application'}."/".$in{'cmd'} .".html";
	$fname =~ s/\[lang\]/$usr{'pref_language'}/gi;
	if (-e "$fname"){
		print &build_page($in{'cmd'}.'.html');
	}else{
		print &build_page('template_add.html');
	}
}

sub html_add_success {
# --------------------------------------------------------
	$in{'view'} = $in{lc($db_cols[0])};
	for (0..$#db_cols){
		delete($in{lc($db_cols[$_])});
	}
	&html_view_record;
}

sub html_add_failure {
# --------------------------------------------------------
	$va{'message'} = &trans_txt('reqfields');
	print "Content-type: text/html\n\n";
	my ($fname) = $cfg{'path_templates'}."/mod/".$usr{'application'}."/".$in{'cmd'} .".html";
	$fname =~ s/\[lang\]/$usr{'pref_language'}/gi;
	if (-e "$fname"){
		print &build_page($in{'cmd'}.'.html');
	}else{
		print &build_page('template_add.html');
	}
}

1;
