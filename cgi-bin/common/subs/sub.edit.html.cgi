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
##			Modifying			##
##########################################################

sub html_edit_select {
# --------------------------------------------------------
#Last modified on 15 Aug 2011 15:11:50
#Last modified by: MCC C. Gabriel Varela S. : second_conn is considered
	if(!&check_permissions($in{'cmd'},'_edit','')){ &html_unauth; return; };

	if  ($in{'action'}){
		my $conn_type=0;
		if($in{'second_conn'}){
			$conn_type=1;
		}else{
			$conn_type=0;
		}
		
		my ($sth) = &Do_SQL("SELECT COUNT(*) FROM $in{'db'} WHERE $db_cols[0]='$in{lc($db_cols[0])}'; ",$conn_type);
		if ($sth->fetchrow()==0) {
			$va{'message'} = &trans_txt("searcherror");
			$in{'search'}='listall';
			&html_search_select;
			return;
		}
		my ($message) = &modify_record;
		if ($message eq 'ok'){
			&memcached_delete('e' . $in{'e'} . '_' .$in{'db'} . '_' . $in{lc($db_cols[0])}, $SQL); 
			&html_modify_success($message);
	    }else{
			&html_modify_failure($message);
	    }
	}elsif ($in{'edit'} eq 1){
		&html_modify_failure;
 	}else{
		&html_modify_form_record;
	}
	&run_eafunction('edit');
}


##########################################################
##			Modifying			##
##########################################################
sub modify_record {
# --------------------------------------------------------
#Last modified on 15 Aug 2011 15:16:50
#Last modified by: MCC C. Gabriel Varela S. : second_conn is considered
	my ($x,$err,$query);
	$err = &run_function("validate");

	($x,$query) = &validate_cols('1');
	$err += $x;

	if ($err==0) {
		my ($c_query) =  &run_function("modify");
		if ($c_query){
			$query = $c_query;
		}
			
		#for (1..$#db_cols-3){
		#	($db_valid_types{$db_cols[$_]} eq 'date') and ($in{lc($db_cols[$_])} = &date_to_sql(lc($in{$db_cols[$_]})));
		#	$query .= " $db_cols[$_]='" . &filter_values($in{lc($db_cols[$_])}) . "',";
		#}
		#chop($update);
		
		my $conn_type=0;
		if($in{'second_conn'}){
			$conn_type=1;
		}else{
			$conn_type=0;
		}
		
		my ($sth) = &Do_SQL("UPDATE $in{'db'} SET $query WHERE $db_cols[0]='$in{lc($db_cols[0])}';",$conn_type);
		## Page Message		
		$va{'message'} = &trans_txt($in{'cmd'}.'_updated') . " $in{lc($db_cols[0])}";
		
		&run_function("updated",$query);
		&run_notifs($in{'cmd'}.'_updated');

		## Save logs
		&auth_logging($in{'cmd'}.'_updated',"$in{lc($db_cols[0])}");
		return "ok";
	}else {
		return $status;
	}
}


##########################################################
##			Modifying			##
##########################################################

sub html_modify_form_record {
# --------------------------------------------------------
# Last Modified on: 09/12/08 13:37:19
# Last Modified by: MCC C. Gabriel Varela S: Se establece el valor siempre y cuando no est? establecido ya
# Last Modified on: 02/25/09 11:59:06
# Last Modified by: MCC C. Gabriel Varela S: Se hace que se guarde registro de have seen tambi?n
# Last Modified on: 09/15/09 17:57:02
# Last Modified by: MCC C. Gabriel Varela S: Se implementan cookies para multicompa??a
#Last modified on 29 Oct 2010 16:20:22
#Last modified by: MCC C. Gabriel Varela S. :Se incorpora opci?n de nuevo look
	if(!&check_permissions($in{'cmd'},'_edit','')){ &html_unauth; return; };
	my (%rec) = &get_record($db_cols[0],$in{'modify'},$in{'db'});

	 if (!$rec{lc($db_cols[0])} or !$in{'modify'}) {
		  $va{'message'} = &trans_txt("searcherror");
		  $in{'search'}='listall';
		  &html_search_select;
	 }else{

	 	if($in{'cmd'} eq "opr_orders" and $in{'modify'}){
			$va{'canceldate_required'}="required";
			$va{'canceldate_format'}="minDate: 0";
		}
	 	
		foreach $key (keys %rec){
		  $in{lc($key)} = &encode_html($rec{$key}) if(!$in{lc($key)});
		}
		## Loading Special Options
		&run_function("loading");

		my $idf=$in{'db'};
		$idf=~s/sl_/id_/g;
		&write_cookie("$in{'db'}$in{'e'}",$in{$idf},$cfg{'expcookie'},"add");
		print "Content-type: text/html\n\n";
	
		my ($fname) = $cfg{'path_templates'}."/mod/".$usr{'application'}."/".$in{'cmd'} ."_edit.html";
		$fname =~ s/\[lang\]/$usr{'pref_language'}/gi;
		if (-e "$fname"){
			print &build_page($in{'cmd'}.'_edit.html');
		}else{
			print &build_page('template_edit.html');
		}

	 }
}

sub html_modify_success {
# --------------------------------------------------------
# Last Modified on: 07/16/08  13:36:01
# Last Modified by: Roberto Barcenas
# Last Modified Desc: nodel functionallity updated
	
	if($in{'show_edit_list'}){ #show the list, edit item and show the list again JRG 05-05-2008
		for (0..$#db_cols){
			if(!$in{'nodel_'.lc($db_cols[$_])} ){ #no delete this variables
				delete($in{lc($db_cols[$_])});
			} 
		}
		$in{'search'} = 'Search';
		&html_search_select;
	} else {
		$in{'view'} = $in{lc($db_cols[0])};
		for (0..$#db_cols){
			delete($in{lc($db_cols[$_])});
		}
		&html_view_record;
	}
	
}

#sub html_modify_success {
## --------------------------------------------------------
#	$in{'view'} = $in{lc($db_cols[0])};
#	for (0..$#db_cols){
#		delete($in{lc($db_cols[$_])});
#	}
#	&html_view_record;
#}

sub html_modify_failure {
# --------------------------------------------------------
	for (0..$#db_cols-3){
		  $in{lc($db_cols[$_])} = &encode_html($in{lc($db_cols[$_])});
	 }
	$va{'message'} = &trans_txt('reqfields')  if !$va{'message'};
	print "Content-type: text/html\n\n";

	my ($fname) = $cfg{'path_templates'}."/mod/".$usr{'application'}."/".$in{'cmd'} ."_edit.html";
	$fname =~ s/\[lang\]/$usr{'pref_language'}/gi;
	if (-e "$fname"){
		print &build_page($in{'cmd'}.'_edit.html');
	}else{
		print &build_page('template_edit.html');
	}

}




1;
