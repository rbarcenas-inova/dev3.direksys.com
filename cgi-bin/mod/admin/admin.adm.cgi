##########################################################
##			 ADMIN PAGES :BACKUP LIST		##
##########################################################

sub admin_backup_list {
# --------------------------------------------------------
# Created :  Carlos Haas 01/01/2007 6:47:28 PM
# Last Update : 
# Locked by : 
# Description :
#
#

	foreach $key (keys %in) {
		if ($in{$key} eq &trans_txt('btn_save')){
		}elsif ($in{$key} eq &trans_txt('btn_del')){
			unlink ("$cfg{'backup_files'}/".substr($key,4));
			$va{'message'} = &trans_txt('admin_delbackup');
		}elsif ($in{$key} eq &trans_txt('btn_apply')){

		}
	}
	
	if (opendir (AUTHDIR, "$cfg{'backup_files'}")){
		my ($play_btn,@files,$name,$comments);
		@files = readdir(AUTHDIR);		# Read in list of files in directory..
		closedir (AUTHDIR);
		@files = grep(/tar\.gz$/,@files);
		@files = @files;
		@c = split(/,/,$cfg{'srcolors'});
		$va{'matches'} = $#files+1;
		(!$in{'nh'}) and ($in{'nh'}=1);
		$first = ($in{'nh'} - 1) * $usr{'pref_maxh'};
		$last = $va{'matches'};
		($last-$first > $usr{'pref_maxh'}) and ($last = $first+$usr{'pref_maxh'});
		
		for ($x = $first; $x < $last; $x++) {
			@ary = stat("$cfg{'backup_files'}/$files[$x-1]");
			my ($sec, $min, $hour, $day, $mon, $year, $dweek, $dyear, $daylight) = localtime($ary[9]);
			($hour<10) and ($hour = "0$hour");
			($min<10) and ($min = "0$min");
			($sec<10) and ($sec = "0$sec");
			if ($files[$x-1] =~ /ast\.conf\./){
				$type = &trans_txt('admin_filetype_sitpbx');
			}elsif($files[$x-1] =~ /dbsit\.mysql\./){
				$type = &trans_txt('admin_filetype_sitdbs');
			}elsif($files[$x-1] =~ /dbccenter\.mysql\./){
				$type = &trans_txt('admin_filetype_ccenter');
			}elsif($files[$x-1] =~ /dbtsales\.mysql\./){
				$type = &trans_txt('admin_filetype_sales');
			}elsif($files[$x-1] =~ /dbman\.mysql\./){
				$type = &trans_txt('admin_filetype_dbman');
			}elsif($files[$x-1] =~ /dbegw\.mysql\./){
				$type = &trans_txt('admin_filetype_egw');
			}else{
				$type = &trans_txt('admin_filetype_unknow');
			}
			
			$date = &sql_to_date(($year+1900)."-$mon-$day");
			$size = &format_number($ary[7]/1000,0) . " Kb";
			$time = "$hour:$min:$sec";
			$d = 1 - $d;
			$va{'searchresults'} .= qq|
				<tr bgcolor='$c[$d]' onmouseover='m_over(this)' onmouseout='m_out(this)'>
				   <td align="center"><input type="button" value="|.&trans_txt("btn_save").qq|" class="button" OnClick="download('$files[$x]')">
					<input type="submit" name="del_$files[$x]" value="|.&trans_txt("btn_del").qq|" class="button" onclick="notest=false;return;">
					<input type="submit" name="app__$files[$x]" value="|.&trans_txt("btn_apply").qq|" class="button"></td>
				   <td class="smalltext">$type</td>
				   <td class="smalltext" align="right">$size</td>
				   <td class="smalltext" align="center">$date</td>
				   <td class="smalltext" align="center">$time</td>
				</tr>\n|;
		}	
	}
	if ($va{'matches'}==0){
		$va{'matches'} = 0;
		$va{'pageslist'} = 0;
		$va{'searchresults'} = qq|
			<tr>
			   <td colspan="5" align="center"><p>&nbsp;</p><p>|.&trans_txt("applychgs_bk_nofiles").qq| </p><p>&nbsp;</p></td>
			</tr>\n|;
	}else{
		($va{'pageslist'},$va{'qs'})  = &pages_list($in{'nh'},"$cfg{'path_ns_cgi'}$cfg{'path_ns_cgi_dbapp'}",$va{'matches'},$usr{'pref_maxh'});
	}
	
	
  print "Content-type: text/html\n\n";
	print &build_page('admin_backup_list.html');	
}

##########################################################
##			 ADMIN PAGES :DB TOOLS	##
##########################################################

sub admin_dbtools {
# --------------------------------------------------------
# Created :  Carlos Haas 01/01/2007 6:47:28 PM
# Last Update : 
# Locked by : 
# Description :
#
#

	print "Content-type: text/html\n\n";
	my ($err);
	
	if ($in{'action'}){
		if ($in{'del'} eq 'logs'){
			if(!$in{'lto_date'}){
				$error{'lto_date'} = &trans_txt("required");
				++$err;
			}
			if(!$in{'lfrom_date'}){
				$error{'lfrom_date'} = &trans_txt("required");
				++$err;
			}
			if (!$err){
				$va{'message'} = &trans_txt('admin_dellogs') . " $in{'lfrom_date'} -> $in{'lto_date'}" ;
				my ($sth) = &Do_SQL("DELETE FROM admin_logs WHERE LogDate>='$in{'lfrom_date'}' AND LogDate<='$in{'lto_date'}';");
				&auth_logging('admin_dellogs'," $in{'lfrom_date'} -> $in{'lto_date'}");
			}else{
				$va{'message'} = &trans_txt('reqfields');
			}
		}elsif($in{'del'} eq 'cdr'){
			if(!$in{'cto_date'}){
				$error{'cto_date'} = &trans_txt("required");
				++$err;
			}
			if(!$in{'cfrom_date'}){
				$error{'cfrom_date'} = &trans_txt("required");
				++$err;
			}
			if (!$err){
				$va{'message'} = &trans_txt('admin_delcdrs') . " $in{'cfrom_date'} -> $in{'cto_date'}" ;
				my ($sth) = &Do_SQL("DELETE FROM cdr WHERE calldate>='$in{'cfrom_date'}' AND calldate<='$in{'cto_date'}';");
				&auth_logging('admin_delcdrs'," $in{'cfrom_date'} -> $in{'cto_date'}");
			}else{
				$va{'message'} = &trans_txt('reqfields');
			}
		}elsif($in{'tables'} and $in{'type'}){
			my ($outtext) = " $in{'tables'}";
			my ($sth) = &Do_SQL("$in{'type'} TABLE $in{'tables'};");
			$va{'query_result'} = "<tr><td>Table</td><td>Op</td><td>Message Type</td><td>Message text</td></tr>";			
			while ($rec = $sth->fetchrow_hashref()){
				$va{'query_result'} .= "<tr><td class='smalltext'>$rec->{'Table'}</td><td class='smalltext'>$rec->{'Op'}</td><td class='smalltext'>$rec->{'Msg_type'}</td><td class='smalltext'>$rec->{'Msg_text'}</td></tr>";
				$outtext .= " $rec->{'Msg_type'}/$rec->{'Msg_text'}";
			}
			
			&auth_logging('admin_table'.$in{'type'},$outtext);
			$va{'message'} = &trans_txt("admin_table$in{'type'}") . $outtext ;
		}else{
			$va{'message'} = &trans_txt("admin_notable");
		}		
	}

  print &build_page('admin_dbtools.html');    
}

1;
