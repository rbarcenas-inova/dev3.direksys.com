#!/usr/bin/perl
##################################################################
#     MERCHANDISING : RESOURCES PAGES       	#
##################################################################
sub view_repman {
# --------------------------------------------------------
	my ($query_select);
	$in{'drop'} = int($in{'drop'});
	$in{'order_down'} = int($in{'order_down'});
	$in{'order_up'} = int($in{'order_up'});

	if ($in{'action'} and &check_permissions('repman_addfield','','')){

		my $dir = getcwd;
		my($b_cgibin,$a_cgibin) = split(/cgi-bin/,$dir);
		my $home_dir = $b_cgibin.'cgi-bin/common';
		if (-e $home_dir."/subs/admin/lib_repman.pl"){
			require ($home_dir."/subs/admin/lib_repman.pl");
		}
		my ($err,$query);
		if ($in{'fieldtype'} eq 'CusFunc'){
			$in{'filter'} = 'Disable';
			my($func) = 'repman_'. $in{'field'};  ## External Func
			if (not defined &$func){
				$error{'field'} = &trans_txt('invalid');
				++$err;
			}
		}
		if ($in{'fieldtype'} eq 'SQLFunc'){
			$in{'filter'} = 'Disable';
		}
		if (!$in{'visibility'}){
			$in{'visibility'} = 'Visible';
		}
		
		
		my (@cols) = ('PrintName','Field','FieldType','Filter','FormatType','visibility','ListOrder'); 
		for (0..$#cols){
			if (!$in{lc($cols[$_])}){
				$error{lc($cols[$_])} = &trans_txt('required');
				++$err;
			}else{
				$query .= "$cols[$_]='".&filter_values($in{lc($cols[$_])})."', "
			}
		}

		if (!$err){
			my ($sth) = &Do_SQL("INSERT INTO admin_reports_fields SET $query ID_admin_reports=$in{'id_admin_reports'},Date=CURDATE(),Time=CURTIME(),ID_admin_users=$usr{'id_admin_users'}");
			$va{'tabmessages'} = &trans_txt('repman_field_added');
			&auth_logging('repman_field_added',"$in{'id_admin_reports'}");
			for (0..$#cols){
				delete($in{lc($cols[$_])});
			}
		}else{
			$va{'tabmessages'} = &trans_txt('reqfields');
		}
		
	}elsif($in{'drop'}>0 and &check_permissions('repman_delfield','','')){
		my ($sth) = &Do_SQL("DELETE FROM admin_reports_fields WHERE ID_admin_reports=$in{'id_admin_reports'} AND ID_admin_reports_fields=$in{'drop'}");
		$va{'tabmessages'} = &trans_txt('repman_field_droped');
		&auth_logging('repman_field_droped',"$in{'id_admin_reports'}");
	}elsif($in{'order_down'}){
		my ($sth) = &Do_SQL("UPDATE admin_reports_fields SET ListOrder=ListOrder+1 WHERE ID_admin_reports=$in{'id_admin_reports'} AND ID_admin_reports_fields=$in{'order_down'}");
	}elsif($in{'order_up'}){
		my ($sth) = &Do_SQL("UPDATE admin_reports_fields SET ListOrder=ListOrder-1 WHERE ID_admin_reports=$in{'id_admin_reports'} AND ID_admin_reports_fields=$in{'order_up'}");
	}

	if ($in{'sql_group'}){
		$in{'sql_group'} = " GROUP BY $in{'sql_group'}";
	}
	if ($in{'sql_order'}){
	    $in{'sql_order'} = " ORDER BY $in{'sql_order'}";
		if ($in{'sql_order_type'}){
			$in{'sql_order'} .= " $in{'sql_order_type'} ";
		}
	}
	$sth = &Do_SQL("SELECT * FROM admin_reports_fields WHERE ID_admin_reports='$in{'id_admin_reports'}' ORDER BY ListOrder ASC ");
	while ($rec = $sth->fetchrow_hashref){
		if ($rec->{'FieldType'} eq 'Field'){
			my @arr_fields = split /\./, $rec->{'Field'};
			if ($arr_fields[0] ne $rec->{'Field'}){
				$query_select .= " `".$arr_fields[0]."`.`".$arr_fields[1]."`,";
				$rec->{'Field'} = "`".$arr_fields[0]."`.`".$arr_fields[1]."`";
			}else{
				$query_select .= " `$rec->{'Field'}`,";
			}
		}elsif($rec->{'FieldType'} eq 'SQLFunc'){
			$query_select .= " ($rec->{'Field'}),";
		}elsif($rec->{'FieldType'} eq 'Text'){
			$query_select .= " '$rec->{'Field'}',";
		}
	}
	chop($query_select);
	$query_select = '1' if ($query_select eq '');
	$in{'sql_from'} =~ s/<br>/\n/g;
	$in{'sql_where'} =~ s/<br>/\n/g;
	$va{'sql_sample'} = "SELECT " . $query_select . " FROM " . $in{'sql_from'} . " WHERE " . $in{'sql_where'} . $in{'sql_group'} . $in{'sql_order'};
	
	if ($in{'view_explain'}) {

		$sth = &Do_SQL("EXPLAIN $va{'sql_sample'}");

		#$sth->execute;
		#if ($DBI::errstr){
		#	$va{'cls_explain'} = "smallfieldterr";
		#	$va{'sql_explain'} = "Error :" . $DBI::err ."<br>" .$DBI::errstr;
		#}else{
			$va{'cls_explain'} = "smalltext";
			$rec = $sth->fetchrow_hashref;
			foreach my $key (keys %{$rec}){
				$va{'sql_explain'}	.= "$key : $rec->{$key} &nbsp;";
			}
		#}
		
	}
		
}

sub add_repman {
	my $id_new_repman = $in{'id_admin_reports'};
	&Do_SQL("INSERT INTO admin_groups_perms SET ID_admin_groups=6, application='admin', command='repmans$id_new_repman';");
	&Do_SQL("INSERT INTO admin_groups_perms SET ID_admin_groups=6, application='crm', command='repmans$id_new_repman';");
	&Do_SQL("INSERT INTO admin_groups_perms SET ID_admin_groups=6, application='wms', command='repmans$id_new_repman';");
}

##################################################################
#     NOTIFIS
##################################################################
sub validate_notifs {
# --------------------------------------------------------
	my ($err);
	if ($in{'event'}){
		$sth = &Do_SQL("SELECT COUNT(*) FROM admin_perms WHERE command='$in{'event'}' AND type='dbman' AND Status <> 'Inactive'");
		if ($sth->fetchrow eq 0){
			$error{'event'} = &trans_txt('invalid');
			++$err;
		}
	}
}

sub view_notifs {
# --------------------------------------------------------
	my ($err);
	if ($in{'action'} and &check_permissions('notifs_addactions','','')){
		if (!$in{'type'}){
			++$err;
			$error{'type'} = &trans_txt('required');
		}
		if (!$in{'from'}){
			++$err;
			$error{'from'} = &trans_txt('required');
		}
		if (!$in{'destination'}){
			++$err;
			$error{'destination'} = &trans_txt('required');
		}
		if ($in{'type'} eq 'eMail' and $in{'from'} and $in{'from'} =~ /(@.*@)|(\.\.)|(@\.)|(\.@)|(^\.)/ or $in{$col} !~ /^.+\@(\[?)[a-zA-Z0-9\-\.]+\.([a-zA-Z]{2,3}|[0-9]{1,3})(\]?)$/ ){
			++$err;
			$error{'from'} = &trans_txt('invalid');
		}
		if ($in{'type'} eq 'eMail' and $in{'destination'} and $in{'destination'} =~ /(@.*@)|(\.\.)|(@\.)|(\.@)|(^\.)/ or $in{$col} !~ /^.+\@(\[?)[a-zA-Z0-9\-\.]+\.([a-zA-Z]{2,3}|[0-9]{1,3})(\]?)$/ ){
			++$err;
			$error{'destination'} = &trans_txt('invalid');
		}

		if (!$err){
			my ($sth) = &Do_SQL("INSERT INTO admin_notifs_actions SET Type='".&filter_values($in{'type'})."', `From`='".&filter_values($in{'from'})."', Destination='".&filter_values($in{'destination'})."', ID_admin_notifs=$in{'id_admin_notifs'},Date=CURDATE(),Time=CURTIME(),ID_admin_users=$usr{'id_admin_users'}");
			$va{'tabmessages'} = &trans_txt('repman_field_added');
			delete($in{'type'});
			delete($in{'from'});
			delete($in{'destination'});
			&auth_logging('notifs_action_added',"$in{'id_admin_reports'}");
		}else{
			$va{'tabmessages'} = &trans_txt('reqfields');
		}
	}elsif($in{'drop'}>0 and &check_permissions('notifs_delactions','','')){
		my ($sth) = &Do_SQL("DELETE FROM admin_notifs_actions WHERE ID_admin_notifs=$in{'id_admin_notifs'} AND ID_admin_notifs_actions=$in{'drop'}");
		$va{'tabmessages'} = &trans_txt('notifs_action_droped');
		&auth_logging('notifs_action_droped',"$in{'id_admin_reports'}");
	}
	
}


##################################################################
#     EVENTS
##################################################################
sub validate_events {
# --------------------------------------------------------
	
	my ($err);
	$in{'ok_id_admin_notifs'} = int($in{'ok_id_admin_notifs'});
	$in{'nok_id_admin_notifs'} = int($in{'nok_id_admin_notifs'});
	$in{'timeout'} = int($in{'timeout'});
	$in{'everymin'} = int($in{'everymin'});
	$in{'everyhour'} = int($in{'everyhour'});
	$in{'everyday'} = int($in{'everyday'});
	## Validate From
	if ($in{'fromdate'} and !$in{'fromtime'}){
		$in{'fromtime'} = '00:00:00';
		$in{'fromdatetime'} = "$in{'fromdate'} $in{'fromtime'}";
	}elsif (!$in{'fromdate'} and $in{'fromtime'}){
		$error{'fromdatetime'} = &trans_txt('invalid');
		++$err;
	}elsif ($in{'fromdate'} and $in{'fromtime'}){
		$in{'fromdatetime'} = "$in{'fromdate'} $in{'fromtime'}";
	}
	## Validate To
	if ($in{'todate'} and !$in{'totime'}){
		$in{'totime'} = '23:59:59';
		$in{'todatetime'} = "$in{'todate'} $in{'totime'}";
	}elsif (!$in{'todate'} and $in{'totime'}){
		$error{'todatetime'} = &trans_txt('invalid');
		++$err;
	}elsif ($in{'todate'} and $in{'totime'}){
		$in{'todatetime'} = "$in{'todate'} $in{'totime'}";
	}
	## Validate Notifications
	if ($in{'ok_id_admin_notifs'}>0){
		$sth = &Do_SQL("SELECT COUNT(*) FROM admin_notifs WHERE ID_admin_notifs=$in{'ok_id_admin_notifs'} AND Status='Active'");
		if ($sth->fetchrow eq 0){
			$error{'ok_id_admin_notifs'} = &trans_txt('invalid');
			++$err;
		}
	}
	if ($in{'nok_id_admin_notifs'}>0){
		$sth = &Do_SQL("SELECT COUNT(*) FROM admin_notifs WHERE ID_admin_notifs=$in{'nok_id_admin_notifs'} AND Status='Active'");
		if ($sth->fetchrow eq 0){
			$error{'nok_id_admin_notifs'} = &trans_txt('invalid');
			++$err;
		}
	}
	## Trigger
	if ($in{'eventtriggertype'} ne 'No Trigger'){
		if (!$in{'eventtrigger'}){
			$error{'eventtrigger'}= &trans_txt('required');
			++$err;
		}
		### 
		if ($in{'eventtriggercond'}  and !$in{'eventtriggervalue'}){
			$error{'eventtriggervalue'}= &trans_txt('required');
			++$err;
		}
	}
	#&cgierr;
	return $err;
}

sub view_events {
# --------------------------------------------------------
	$in{'fromdatetime'} = '---' if ($in{'fromdatetime'} eq '0000-00-00 00:00:00');
	$in{'todatetime'} = '---' if ($in{'todatetime'} eq '0000-00-00 00:00:00');
	$in{'everyweekday'} =~ s/\|/ - /g;
	if ($in{'id_admin_notifs'} > 0){
		$va{'notifname'} = "(<a href='/cgi-bin/mod/setup/dbman?cmd=notifs&view=$in{'id_admin_notifs'}'><span  class='smalltext'>$in{'id_admin_notifs'}</span></a>) ".&load_name('admin_notifs','ID_admin_notifs',$in{'id_admin_notifs'},'Name');
	}
}
sub loading_events {
# --------------------------------------------------------
	if ($in{'fromdatetime'}){
		($in{'fromdate'},$in{'fromtime'}) = split(/\s/, $in{'fromdatetime'});
	}
	if ($in{'todatetime'}){
		($in{'todate'},$in{'totime'}) = split(/\s/, $in{'todatetime'});
	}
}


1;
