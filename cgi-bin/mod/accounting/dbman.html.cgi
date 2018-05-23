## Load Dbman
opendir (LIBDIR, "./") || &cgierr("Unable to open directory ./",604,$!);
	@files = readdir(LIBDIR);		# Read in list of files in directory..
closedir (LIBDIR);
FILE: foreach $file (@files) {
	next if ($file !~ /^dbman_/);
	require "./$file";
}

#############################################################################
#############################################################################
#   Function: view_acc_periods
#
#       Es: Vista de periodo contable
#       En: 
#
#
#    Created on: 09/03/2016
#
#    Author: ISC Alejandro Diaz
#
#    Modifications:
#
#        - Modified on 
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
#      <>
#
sub view_acc_periods{
#############################################################################
#############################################################################
	
	if ($in{'chgstatusto'} and $in{'chgstatusto'} ne '' and $in{'status'} ne $in{'chgstatusto'}){
		if (&check_permissions('acc_periods_chgstatus','','')){
			&Do_SQL("UPDATE sl_accounting_periods SET Status='".&filter_values($in{'chgstatusto'})."' WHERE ID_accounting_periods='$in{'id_accounting_periods'}';");
			&auth_logging('acc_periods_chgstatus_'.lc($in{'status'}).'_to_'.lc($in{'chgstatusto'}),$in{'id_accounting_periods'});

			$va{'message_good'} = &trans_txt('acc_periods_chgstatus_'.lc($in{'status'}).'_to_'.lc($in{'chgstatusto'}));
			$in{'status'} = $in{'chgstatusto'};
		}else{
			$va{'message_error'} = &trans_txt('unauth_action');
		}
	}

	my (@ary) = &load_enum_toarray('sl_accounting_periods','Status');
	for (0..$#ary){
		if ($ary[$_] ne $in{'status'}){
			$va{'chgstatus'} .= qq| <a href="/cgi-bin/mod/$usr{'application'}/dbman?cmd=acc_periods&view=$in{'id_accounting_periods'}&chgstatusto=$ary[$_]">$ary[$_]</a> &nbsp;&nbsp;&nbsp;|;
		}
	}
}

#############################################################################
#############################################################################
#   Function: view_acc_periods
#
#       Es: Vista de periodo contable
#       En: 
#
#
#    Created on: 09/03/2016
#
#    Author: ISC Alejandro Diaz
#
#    Modifications:
#
#        - Modified on 
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
#      <>
#
sub view_acc_segments{
#############################################################################
#############################################################################
	
	if ($in{'chgstatusto'} and $in{'chgstatusto'} ne '' and $in{'status'} ne $in{'chgstatusto'}){
		if (&check_permissions('acc_segments_chgstatus','','')){
			&Do_SQL("UPDATE sl_accounts_segments SET Status='".&filter_values($in{'chgstatusto'})."' WHERE ID_accounts_segments='$in{'id_accounts_segments'}';");
			&auth_logging('acc_segments_chgstatus_'.lc($in{'status'}).'_to_'.lc($in{'chgstatusto'}),$in{'id_accounts_segments'});

			$va{'message_good'} = &trans_txt('acc_segments_chgstatus_'.lc($in{'status'}).'_to_'.lc($in{'chgstatusto'}));
			$in{'status'} = $in{'chgstatusto'};
		}else{
			$va{'message_error'} = &trans_txt('unauth_action');
		}
	}

	my (@ary) = &load_enum_toarray('sl_accounts_segments','Status');
	for (0..$#ary){
		if ($ary[$_] ne $in{'status'}){
			$va{'chgstatus'} .= qq| <a href="/cgi-bin/mod/$usr{'application'}/dbman?cmd=acc_segments&view=$in{'id_accounts_segments'}&chgstatusto=$ary[$_]">$ary[$_]</a> &nbsp;&nbsp;&nbsp;|;
		}
	}

	$va{'parent'} = &load_db_names('sl_accounts_segments','ID_accounts_segments',$in{'id_parent'},'[Name]');
}



sub add_acc_periods{
	&Do_SQL(q|SET @rownr := 0;|);
	$query = q|
		SELECT
			@rownr:=@rownr+1 id
			, ID_accounting_periods
		FROM
			sl_accounting_periods
		ORDER BY
			SUBSTR(code,3,6) ASC,
			SUBSTR(code,1,2) ASC;
	|;
	$rw = &Do_SQL($query);
	while($row = $rw->fetchrow_hashref()){
		&Do_SQL("UPDATE sl_accounting_periods SET `order` = '$row->{'id'}' WHERE id_accounting_periods = $row->{'ID_accounting_periods'}");
	}
	return 0;
}

sub updated_acc_periods{
	&Do_SQL(q|SET @rownr := 0;|);
	$query = q|
		SELECT
			@rownr:=@rownr+1 id
			, ID_accounting_periods
		FROM
			sl_accounting_periods
		ORDER BY
			SUBSTR(code,3,6) ASC,
			SUBSTR(code,1,2) ASC;
	|;
	$rw = &Do_SQL($query);
	while($row = $rw->fetchrow_hashref()){
		&Do_SQL("UPDATE sl_accounting_periods SET `order` = '$row->{'id'}' WHERE id_accounting_periods = $row->{'ID_accounting_periods'}");
	}	
}


sub validate_acc_periods{
	$in{'code'} = $in{'num'}.$in{'year'};
	$in{'order'} = 0;
	return 0;
}

sub loading_acc_periods{
	$in{'num'} = substr $in{'code'}, 0, 2;
	$in{'year'} = substr $in{'code'}, -4;
}

1;