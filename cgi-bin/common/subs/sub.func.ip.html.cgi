sub build_images_catlist {
# --------------------------------------------------------
	## Images Root Directory
	my ($output,$rec);
	my ($sth) = &Do_SQL("SELECT * FROM igd_categories WHERE Status='Active' ORDER BY Name");
	$output .= "<option value=''>---</option>\n";
	while ($rec = $sth->fetchrow_hashref()){
		$output .= "<option value='$rec->{'ID_categories'}'>$rec->{'Name'}</option>\n";
	}

	return $output;
}

sub build_select_exten {
# -----------------------------
	##Load SIP Extension
	my ($output);
	my ($sth) = &Do_SQL("SELECT * FROM vxd_extsip WHERE Status='Enabled' ORDER BY Number");
	while ($rec = $sth->fetchrow_hashref){
		$output .= "<option value='SIP/$rec->{'ID_extsip'}'>SIP/$rec->{'Name'} &lt;$rec->{'Number'}&gt;</option>\n";
		#$output .= "<option value='EXT-$rec->{'Number'}'>SIP/$rec->{'Name'} &lt;$rec->{'Number'}&gt;</option>\n";
	}
	my ($sth) = &Do_SQL("SELECT * FROM vxd_extiax WHERE Status='Enabled' ORDER BY Number");
	while ($rec = $sth->fetchrow_hashref){
		$output .= "<option value='IAX/$rec->{'ID_extiax'}'>IAX2/$rec->{'Name'} &lt;$rec->{'Number'}&gt;</option>\n";
		#$output .= "<option value='EXT-$rec->{'Number'}'>IAX2/$rec->{'Name'} &lt;$rec->{'Number'}&gt;</option>\n";
	}
	my ($sth) = &Do_SQL("SELECT * FROM vxd_extzap WHERE Status='Enabled' ORDER BY Number");
	while ($rec = $sth->fetchrow_hashref){
		$output .= "<option value='ZAP/$rec->{'ID_extzap'}'>ZAP/$rec->{'Name'} &lt;$rec->{'Number'}&gt;</option>\n";
		#$output .= "<option value='EXT-$rec->{'Number'}'>ZAP/$rec->{'Name'} &lt;$rec->{'Number'}&gt;</option>\n";
	}
	(!$output) and ($output .= "<option value='---'>".&trans_txt('none')."</option>\n");
	return $output;
}

sub build_select_operators {
# --------------------------------------------------------
	my ($output,$ext);
	my ($sth) = &Do_SQL("SELECT * FROM admin_users WHERE application LIKE 'cc-%' AND Status='Enabled' ORDER BY LastName");
	while ($rec = $sth->fetchrow_hashref){
		($rec->{'extension'}) ? ($ext = "($rec->{'extension'})"):
							($ext = "");
		$output .= "<option value='$rec->{'ID_admin_users'}'>$rec->{'LastName'}, $rec->{'FirstName'} $ext</option>\n";
	}
	(!$output) and ($output .= "<option value='---'>".&trans_txt('none')."</option>\n");
	return $output;
}

sub applychgs_class(){
# --------------------------------------------------------
	my ($sth) = &Do_SQL("SELECT COUNT(*) FROM vxd_changes WHERE AppliedDate IS NULL;");
	if ($sth->fetchrow>0){
		return "menu_bar_red"
	}else{
		return "menu_bar"
	}
}



sub build_select_vmm {
# --------------------------------------------------------
	##Load Ring Group
	my ($output);
	my ($sth) = &Do_SQL("SELECT ID_voicemail FROM vxd_voicemail ORDER BY ID_voicemail");
	VMM: while ($id = $sth->fetchrow()){
		my ($sth2) = &Do_SQL("SELECT * FROM vxd_extsip WHERE ID_voicemail='$id'");
		$rec = $sth2->fetchrow_hashref;
		if ($rec->{'ID_extsip'}>0){
			$output .= "<option value='$id'>SIP/$rec->{'Name'} &lt;$rec->{'Number'}&gt;</option>\n";
			next VMM;
		}
		my ($sth2) = &Do_SQL("SELECT * FROM vxd_extiax WHERE ID_voicemail='$id'");
		$rec = $sth2->fetchrow_hashref;
		if ($rec->{'ID_extiax'}>0){
			$output .= "<option value='$id'>IAX2/$rec->{'Name'} &lt;$rec->{'Number'}&gt;</option>\n";
			next VMM;
		}
		my ($sth2) = &Do_SQL("SELECT * FROM vxd_extzap WHERE ID_voicemail='$id'");
		$rec = $sth2->fetchrow_hashref;
		if ($rec->{'ID_extzap'}>0){
			$output .= "<option value='$id'>ZAP/$rec->{'Name'} &lt;$rec->{'Number'}&gt;</option>\n";
			next VMM;
		}

	}
	(!$output) and ($output .= "<option value='---'>".&trans_txt('none')."</option>\n");
	return $output;
}

sub build_select_meetme {
# --------------------------------------------------------
	my ($output);
	my ($sth) = &Do_SQL("SELECT * FROM vxd_meetme WHERE Status='Enabled' ORDER BY Number");
	while ($rec = $sth->fetchrow_hashref){
		$output .= "<option value='$rec->{'ID_meetme'}'>$rec->{'Name'} &lt;$rec->{'Number'}&gt;</option>\n";
	}
	(!$output) and ($output .= "<option value='---'>".&trans_txt('none')."</option>\n");	
	
	return $output;
}

sub build_select_grp {
# --------------------------------------------------------
	##Load Ring Group
	my ($output);
	my ($sth) = &Do_SQL("SELECT ID_ringgroup,Number,Name FROM vxd_ringgroup WHERE Status='Enabled'  ORDER BY ID_ringgroup");
	while ($rec = $sth->fetchrow_hashref){
		$output .= "<option value='$rec->{'ID_ringgroup'}'>$rec->{'Name'} &lt;$rec->{'Number'}&gt;</option>\n";
		#$output .= "<option value='GRP-$rec->{'Number'}'>$rec->{'Name'} &lt;$rec->{'Number'}&gt;</option>\n";
	}
	(!$output) and ($output .= "<option value='---'>".&trans_txt('none')."</option>\n");
	return $output;
}

sub build_select_queue {
# --------------------------------------------------------
	my ($output);
	my ($sth) = &Do_SQL("SELECT ID_queue,Number,Name FROM vxd_queue WHERE Status='Enabled'  ORDER BY ID_queue");
	while ($rec = $sth->fetchrow_hashref){
		$output .= "<option value='$rec->{'ID_queue'}'>$rec->{'Name'} &lt;$rec->{'Number'}&gt;</option>\n";
	}
	(!$output) and ($output .= "<option value='---'>".&trans_txt('none')."</option>\n");
	return $output;
}

sub build_select_ivr {
# --------------------------------------------------------
	my ($output);
	my ($sth) = &Do_SQL("SELECT ID_ivr,Name FROM vxd_ivr WHERE Status='Enabled' AND NodeType!='Subnode' ORDER BY ID_ivr");
	while ($rec = $sth->fetchrow_hashref){
		$output .= "<option value='$rec->{'ID_ivr'}'>$rec->{'Name'}</option>\n";
	}
	(!$output) and ($output .= "<option value='---'>".&trans_txt('none')."</option>\n");
	return $output;
}

sub build_select_ivr_all {
# --------------------------------------------------------
	my ($output);
	my ($sth) = &Do_SQL("SELECT ID_ivr,Name FROM vxd_ivr WHERE Status='Enabled' ORDER BY ID_ivr");
	while ($rec = $sth->fetchrow_hashref){
		$output .= "<option value='$rec->{'ID_ivr'}'>$rec->{'Name'}</option>\n";
	}
	(!$output) and ($output .= "<option value='---'>".&trans_txt('none')."</option>\n");
	return $output;
}

sub build_select_audiofiles {
# --------------------------------------------------------
	my ($output);
	my ($sth) = &Do_SQL("SELECT filename,Name FROM vxd_audio_files WHERE Status='Enabled' ORDER BY filename");
	while ($rec = $sth->fetchrow_hashref){
		$output .= "<option value='$rec->{'filename'}'>$rec->{'Name'}</option>\n";
	}
	(!$output) and ($output .= "<option value='---'>".&trans_txt('none')."</option>\n");
	return $output;
}

sub build_select_audiofiles_id {
# --------------------------------------------------------
	my ($output);
	my ($sth) = &Do_SQL("SELECT * FROM vxd_audio_files WHERE Status='Enabled' ORDER BY filename");
	while ($rec = $sth->fetchrow_hashref){
		$output .= "<option value='$rec->{'ID_audio_files'}'>$rec->{'Name'}</option>\n";
	}
	(!$output) and ($output .= "<option value='---'>".&trans_txt('none')."</option>\n");
	return $output;
}

sub build_select_ohcat {
# --------------------------------------------------------
	my ($output);
	my ($sth) = &Do_SQL("SELECT ID_ohcat,Name FROM vxd_ohcat WHERE Status='Enabled' ORDER BY ID_ohcat");
	while ($rec = $sth->fetchrow_hashref){
		$output .= "<option value='$rec->{'ID_ohcat'}'>$rec->{'Name'}</option>\n";
	}
	(!$output) and ($output .= "<option value='---'>".&trans_txt('none')."</option>\n");
	return $output;
}

sub build_select_trunks {
# --------------------------------------------------------
	my ($output);
	my ($sth) = &Do_SQL("SELECT ID_trunksip,Name FROM vxd_trunksip WHERE Status='Enabled';");
	while ($rec = $sth->fetchrow_hashref){
		$output .= "<option value='sip-$rec->{'ID_trunksip'}'>SIP $rec->{'Name'}</option>\n";
	}
	my ($sth) = &Do_SQL("SELECT ID_trunkzap,Name FROM vxd_trunkzap WHERE Status='Enabled';");
	while ($rec = $sth->fetchrow_hashref){
		$output .= "<option value='zap-$rec->{'ID_trunkzap'}'>ZAP $rec->{'Name'}</option>\n";
	}
	my ($sth) = &Do_SQL("SELECT ID_trunkiax,Name FROM vxd_trunkiax WHERE Status='Enabled';");
	while ($rec = $sth->fetchrow_hashref){
		$output .= "<option value='iax-$rec->{'ID_trunkiax'}'>IAX2 $rec->{'Name'}</option>\n";
	}
	my ($sth) = &Do_SQL("SELECT ID_trunkenum,Name FROM vxd_trunkenum WHERE Status='Enabled';");
	while ($rec = $sth->fetchrow_hashref){
		$output .= "<option value='enum-$rec->{'ID_trunkenum'}'>ENUM $rec->{'Name'}</option>\n";
	}
	my ($sth) = &Do_SQL("SELECT ID_trunkcust,Name FROM vxd_trunkcust WHERE Status='Enabled';");
	while ($rec = $sth->fetchrow_hashref){
		$output .= "<option value='cust-$rec->{'ID_trunkcust'}'>CUST $rec->{'Name'}</option>\n";
	}

	return $output;
}

sub ohcat_view {
# --------------------------------------------------------
	my ($sth) = &Do_SQL("SELECT * FROM vxd_ohcat WHERE ID_ohcat='$in{'id_ohcat'}' AND Status='Enabled' ");
	$rec = $sth->fetchrow_hashref;
	if ($rec->{'ID_ohcat'}>0){
		return $rec->{'Name'};
	}else{
		return &trans_txt('none');
	}
}

sub ivr_view {
# --------------------------------------------------------
	my ($sth) = &Do_SQL("SELECT * FROM vxd_ivr WHERE ID_ivr='$in{'id_ivr'}' AND Status='Enabled'");
	$rec = $sth->fetchrow_hashref;
	if ($rec->{'ID_ivr'}>0){
		return $rec->{'Name'};
	}else{
		return &trans_txt('none');
	}
}


#################################################################################
#######            VOICE MAIL                              ######################
#################################################################################

sub voicemail {
# --------------------------------------------------------
	(!$in{'voicemail'} and !$in{'id_voicemail'}) and ($in{'voicemail'}='off');
	
	if ($in{'id_voicemail'}>0 and $in{'voicemail'} ne 'off'){
		my ($sth) = &Do_SQL("SELECT * FROM vxd_voicemail WHERE ID_voicemail='$in{'id_voicemail'}'");
		$rec = $sth->fetchrow_hashref;
		foreach $key (keys %{$rec}){
			$in{'vm'.lc($key)} = $rec->{$key};
		}
		if ($in{'vmid_voicemail'}>0){
			$in{'voicemail'}='on';
		#}else{
		#	$in{'voicemail'}='off';
		}
	}
	(!$in{'voicemail'} or $in{'voicemail'} eq 'disabled') and ($in{'voicemail'}='off');
	return &build_page('sitvoip/mods/voicemail_'.$in{'voicemail'}.'.html');
}

sub voicemail_view {
# --------------------------------------------------------
	$in{'voicemail'}='off';
	if ($in{'id_voicemail'}>0){
		my ($sth) = &Do_SQL("SELECT * FROM vxd_voicemail WHERE ID_voicemail='$in{'id_voicemail'}'");
		$rec = $sth->fetchrow_hashref;
		foreach $key (keys %{$rec}){
			$in{'vm'.lc($key)} = $rec->{$key};
		}
		if ($in{'vmid_voicemail'}>0){
			$in{'voicemail'}='on';
		}
	}
	(!$in{'voicemail'}) and ($in{'voicemail'}='off');
	return &build_page('sitvoip/mods/voicemailview_'.$in{'voicemail'}.'.html');
}

#################################################################################
#######            FOLLOW ME                               ######################
#################################################################################

sub followme {
# --------------------------------------------------------
	(!$in{'followme'}) and ($in{'followme'}='Off');
	return &build_page('sitvoip/mods/followme_'.lc($in{'followme'}).'.html');
}

sub followme_view {
# --------------------------------------------------------
	(!$in{'followme'}) and ($in{'followme'}='Off');
	return &build_page('sitvoip/mods/followmeview_'.lc($in{'followme'}).'.html');
}


sub build_destination {
# --------------------------------------------------------
	my ($output);
	if ($in{'indicate'} eq 'grp'){
		my ($sth) = &Do_SQL("SELECT * FROM vxd_ringgroup WHERE ID_ringgroup='$in{'destination'}'");
		$rec = $sth->fetchrow_hashref;
		$output = &trans_txt('dest_grp');
	}elsif($in{'indicate'} eq 'ext' and $in{'destination'} =~ /^SIP\/(\d+)/){
		my ($sth) = &Do_SQL("SELECT * FROM vxd_extsip WHERE ID_extsip='$1'");
		$rec = $sth->fetchrow_hashref;
		$output = &trans_txt('dest_sip');
	}elsif($in{'indicate'} eq 'ext' and $in{'destination'} =~ /^ZAP\/(\d+)/){
		my ($sth) = &Do_SQL("SELECT * FROM vxd_extzap WHERE ID_extzap='$1'");
		$rec = $sth->fetchrow_hashref;
		$output = &trans_txt('dest_zap');
	}elsif($in{'indicate'} eq 'ext' and $in{'destination'} =~ /^IAX\/(\d+)/){
		my ($sth) = &Do_SQL("SELECT * FROM vxd_extiax WHERE ID_extiax='$1'");
		$rec = $sth->fetchrow_hashref;
		$output = &trans_txt('dest_iax');
	}elsif($in{'indicate'} eq 'que'){
		my ($sth) = &Do_SQL("SELECT * FROM vxd_queue WHERE ID_queue='$in{'destination'}'");
		$rec = $sth->fetchrow_hashref;
		$output = &trans_txt('dest_que');
	}elsif($in{'indicate'} eq 'cust'){
		$output = &trans_txt('dest_cust') . $in{'destination'};
	}elsif($in{'indicate'} eq 'ivr'){
		my ($sth) = &Do_SQL("SELECT * FROM vxd_ivr WHERE ID_ivr='$in{'destination'}'");
		$rec = $sth->fetchrow_hashref;
		$output = &trans_txt('dest_ivr');
	}elsif($in{'indicate'} eq 'bye'){
		my ($sth) = &Do_SQL("SELECT * FROM vxd_audio_files WHERE filename='$in{'destination'}'");
		$rec = $sth->fetchrow_hashref;
		$output = &trans_txt('dest_bye');
	}elsif($in{'indicate'} eq 'ask'){
		my ($sth) = &Do_SQL("SELECT * FROM vxd_audio_files WHERE filename='$in{'destination'}'");
		$rec = $sth->fetchrow_hashref;
		$output = &trans_txt('dest_ask');	
	}elsif($in{'indicate'} eq 'vmm'){
		my ($sth) = &Do_SQL("SELECT * FROM vxd_extsip WHERE ID_voicemail='$in{'destination'}'");
		$rec = $sth->fetchrow_hashref;
		if ($rec->{'ID_extsip'}>0){
			$rec->{'ext_type'} = 'SIP';
			$output = &trans_txt('dest_vmm');
		}else{
			my ($sth) = &Do_SQL("SELECT * FROM vxd_extiax WHERE ID_voicemail='$in{'destination'}'");
			$rec = $sth->fetchrow_hashref;
			if ($rec->{'ID_extiax'}>0){
				$rec->{'ext_type'} = 'IAX2';
				$output = &trans_txt('dest_vmm');
			}else{
				my ($sth) = &Do_SQL("SELECT * FROM vxd_extzap WHERE ID_voicemail='$in{'destination'}'");
				$rec = $sth->fetchrow_hashref;
				if ($rec->{'ID_extzap'}>0){
					$rec->{'ext_type'} = 'ZAP';
					$output = &trans_txt('dest_vmm');
				}else{
					$output = "&nbsp; $in{'destination'} $in{'indicate'} ";
				}
			}
		}

	}elsif($in{'indicate'} eq 'incom'){
		$output = &trans_txt('dest_incom');
	}else{
		$output = "&nbsp; $in{'destination'} $in{'indicate'} ";
	}

	foreach $key (keys %{$rec}){
		$output =~ s/\[$key\]/$rec->{$key}/gi;
	}

	return "$output &nbsp;";
}

sub extensionlist_view(){
# --------------------------------------------------------
	my ($output,$type,$id,$line,$key);
	my (@list) = split(/\|/, $in{'extensionlist'});
	for (0..$#list){
		($type,$id) = split(/\//, $list[$_]);
		if ($type =~ /^SIP$|^ZAP$|^IAX$/ and $id>0){
			my ($sth) = &Do_SQL("SELECT * FROM vxd_ext".lc($type)." WHERE ID_ext".lc($type)."='$id'");
			while ($rec = $sth->fetchrow_hashref){
				$rec->{'extenType'} = $type;
				$line = &trans_txt('extenlist');
				if ($rec->{'ID_accounts'}>0){
					$rec->{'ID_accounts'} =  "($rec->{'ID_accounts'}) ".&load_name('vxd_accounts','ID_accounts',$rec->{'ID_accounts'},'Name');
				}else{
					$rec->{'ID_accounts'} = '---';
				}
				foreach $key (keys %{$rec}){
					$line =~ s/\[$key\]/$rec->{$key}/g;
				}
				$output .= "<a href='$cfg{'pathcgi'}$cfg{'pathcgi_voip_dbman'}?cmd=exten".lc($type)."&view_$id=V'>$line</a><br>";
			}
			
		}
	}
	return $output;
}

1;




