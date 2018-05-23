#!/usr/bin/perl
#####################################################################
########                   APARTS	        		           		#########
#####################################################################
sub load_tabsconf {
# --------------------------------------------------------
	if ($in{'tab'} eq 3){
		## Notes Tab
		$va{'tab_type'}  = 'notes';
		$va{'tab_title'} = &trans_txt('notes');
		$va{'tab_table'} = 'sl_keypoints_notes';
	}elsif($in{'tab'} eq 4){
		## Notes Tab
		$va{'tab_type'}  = 'logs';
		$va{'tab_title'} = &trans_txt('logs');
		$va{'tab_table'} = 'sl_keypoints';
	}
}

sub load_tabs1 {
# --------------------------------------------------------
##############################################
## tab1 : Families
##############################################
	$in{'drop'} = int($in{'drop'});
	if ($in{'tabaction'} and $in{'new_tag'} and $in{'type'} and $in{'new_data'}){
		## TODO... Permisos
		my ($sth) = &Do_SQL("REPLACE INTO sl_keypoints_fams SET ID_keypoints='$in{'id_keypoints'}',
					Tag='".&filter_values($in{'new_tag'})."',
					Type='".&filter_values($in{'type'})."',
					Data='".&filter_values($in{'new_data'})."'   ");
		delete($in{'new_tag'});
		delete($in{'type'});
		delete($in{'new_data'});
		&auth_logging('acc_keypoints_added',$in{'id_keypoints'});
	}elsif ($in{'drop'}){
		## TODO... Permisos
		my ($sth) = &Do_SQL("DELETE FROM sl_keypoints_fams WHERE ID_keypoints='$in{'id_keypoints'}' AND ID_keypoints_fams=$in{'drop'}");
		&auth_logging('acc_keypoints_droped',$in{'id_keypoints'});
	}	
	## ITEMS LIST
	my (@c) = split(/,/,$cfg{'srcolors'});
	my ($d);
	my ($sth) = &Do_SQL("SELECT COUNT(*) FROM sl_keypoints_fams WHERE ID_keypoints='$in{'id_keypoints'}'");
	$va{'matches'} = $sth->fetchrow;
	if ($va{'matches'}>0){
		if ($in{'print'}){
			$sth = &Do_SQL("SELECT * FROM sl_keypoints_fams WHERE ID_keypoints='$in{'id_keypoints'}' ORDER BY Tag DESC ");
		}else{
			(!$in{'nh'}) and ($in{'nh'}=1);
			$first = ($in{'nh'} - 1) * $usr{'pref_maxh'};			
			($va{'pageslist'},$qs) = &pages_list($in{'nh'},"/cgi-bin/mod/$usr{'application'}/dbman",$va{'matches'},$usr{'pref_maxh'});
			$sth = &Do_SQL("SELECT * FROM sl_keypoints_fams WHERE ID_keypoints='$in{'id_keypoints'}' ORDER BY Tag DESC LIMIT $first,$usr{'pref_maxh'};");			
		}
	
		
		while ($rec = $sth->fetchrow_hashref){
			$d = 1 - $d;
			$va{'searchresults'} .= "<tr bgcolor='$c[$d]'>\n";
			$va{'searchresults'} .= qq|<td class='smalltext' valign='top' nowrap>
								<a href="/cgi-bin/mod/setup/dbman?cmd=acc_keypoints&view=$in{'id_keypoints'}&tab=1&drop=$rec->{'ID_keypoints_fams'}"><img src='$va{'imgurl'}/$usr{'pref_style'}/b_drop.png' title='Drop' alt='' border='0'></a>
								$rec->{'Tag'}</td>\n|;
			$va{'searchresults'} .= "  <td class='smalltext' valign='top' nowrap>$rec->{'Type'}</td>\n";
			$va{'searchresults'} .= "  <td class='smalltext' valign='top'>$rec->{'Data'}</td>\n";
			$va{'searchresults'} .= "</tr>\n";
		}	
	}else{
		$va{'pageslist'} = 1;
		$va{'searchresults'} = qq|
			<tr>
				<td colspan='3' align="center">|.&trans_txt('search_nomatches').qq|</td>
			</tr>\n|;
	}

}


sub load_tabs2 {
# --------------------------------------------------------
##############################################
## tab2 : Tree
##############################################

	
	## ITEMS LIST
	my (@c) = split(/,/,$cfg{'srcolors'});
	my (%fam,@keypoints,$level,@lines,$d);
	my ($sth) = &Do_SQL("SELECT COUNT(*) FROM sl_keypoints_fams WHERE ID_keypoints='$in{'id_keypoints'}'");
	$va{'matches'} = $sth->fetchrow;
	if ($va{'matches'}>0){
		if ($in{'print'}){
			$sth = &Do_SQL("SELECT * FROM sl_keypoints_fams WHERE ID_keypoints='$in{'id_keypoints'}' ORDER BY Tag DESC ");
		}else{
			(!$in{'nh'}) and ($in{'nh'}=1);
			$first = ($in{'nh'} - 1) * $usr{'pref_maxh'};			
			($va{'pageslist'},$qs) = &pages_list($in{'nh'},"/cgi-bin/mod/$usr{'application'}/dbman",$va{'matches'},$usr{'pref_maxh'});
			$sth = &Do_SQL("SELECT * FROM sl_keypoints_fams WHERE ID_keypoints='$in{'id_keypoints'}' ORDER BY Tag DESC;");			
		}
	
		$tag = &load_name('sl_keypoints','ID_keypoints',$in{'id_keypoints'},'Tag');
		##order_{Type}_scanned_{Ctype}_{PType}
		
		while ($rec = $sth->fetchrow_hashref){
			++$level;
			if ($rec->{'Type'} eq 'List' and $rec->{'Data'}){
				@ary = split(/,/,$rec->{'Data'});
			}else{
				my ($tbl,$fname) = split(/\./,$rec->{'Data'});
				@ary = &load_enum_toarray($tbl,$fname);
				$rec->{'Data'} = join(",",@ary);
			}
			$fam{$level.':Data'}=$rec->{'Data'};
			$fam{$level.':Name'}=$rec->{'Tag'};
			$fam{$level.':First'}= $ary[0];
			$fam{$level.':Size'}= $#ary;
		}
		##%error = %fam;&cgierr($level . "-=".$#lines . "--$lines[0]-$lines[1]--");
		my (@lines);
#		$fam{'5:Data'}= ("opc1","opc2","opc3","opc4");
#		push(@lines,${fam{'5:Data'}}[2]);
		for my $i(1..$level){  #$level)
			my @ary = split(/,/, $fam{$i.':Data'});
			my ($orig_size) = $#lines;
			for (my $x = $fam{$i.':Size'}; $x >= 0; $x--) {
				if ($i>1){
					if ($x eq 0){
						for my $z (0..$#lines){
							$lines[$z]= &trans_tag($lines[$z],$fam{$i.':Name'},$ary[$x]);
						}
					}else{
						for my $z (0..$orig_size){
							push(@lines,&trans_tag($lines[$z],$fam{$i.':Name'},$ary[$x]));
						}
					}
				}else{
					push(@lines,&trans_tag($tag,$fam{$i.':Name'},$ary[$x]))
				}
			}
		}
		#&cgierr($level . "-=".$#lines . "--$lines[0]-$lines[1]--");
		my(@funcs);
		$sth = &Do_SQL("SELECT Name FROM sl_keypfunctions_keypoints LEFT JOIN sl_keypfunctions 
							ON sl_keypfunctions_keypoints.ID_keypfunctions=sl_keypfunctions.ID_keypfunctions
							WHERE ID_keypoints=$in{'id_keypoints'} OR ID_keypoints IS NULL");
		while (my $name = $sth->fetchrow){
			push(@funcs, $name);
		}
		@lines = sort { lc($a) cmp lc($b) } @lines;
		for my $i(0..$#lines){
			if ($in{'tabaction'}){
				if($in{$lines[$i]}){
					#&cgierr("$lines[$i] : $in{$lines[$i]}");
					$sth = &Do_SQL("REPLACE INTO sl_keypoints_functions SET Keypoint='$lines[$i]', Function='$in{$lines[$i]}',Status='Active', Date=CURDATE(), Time=CURTIME()");
				}	
			}	
			
			$d = 1 - $d;
			$va{'searchresults'} .= "<tr bgcolor='$c[$d]'>\n";
			$va{'searchresults'} .= "  <td class='smalltext' valign='top' nowrap>$lines[$i]</td>\n";
			$sth = &Do_SQL("SELECT * FROM sl_keypoints_functions WHERE Keypoint='$lines[$i]'");
			$rec = $sth->fetchrow_hashref;
			$va{'searchresults'} .= "  <td class='smalltext' valign='top' nowrap>".&build_select_functions($lines[$i],$rec->{'Function'},@funcs)."</td>\n";
			$va{'searchresults'} .= "  <td class='smalltext' valign='top'>".&build_params_list($lines[$i],$rec->{'Function'},$rec->{'Params'})."</td>\n";
			$va{'searchresults'} .= "</tr>\n";
		}		
		$va{'matches'} = $#lines +1;
	}else{
		$va{'pageslist'} = 1;
		$va{'searchresults'} = qq|
			<tr>
				<td colspan='3' align="center">|.&trans_txt('search_nomatches').qq|</td>
			</tr>\n|;
	}

}
sub build_params_list{
# --------------------------------------------------------
	my ($fname,$ffunc,$params)= @_;
	my ($output,$line,@ary_pname,@ary_pdesc);
	if ($ffunc){

		$sth = &Do_SQL("SELECT ParamName,ParamDesc FROM sl_keypfunctions_params LEFT JOIN sl_keypfunctions ON sl_keypfunctions.ID_keypfunctions=sl_keypfunctions_params.ID_keypfunctions  WHERE Name='$ffunc' ORDER BY Line ASC");
		while (my ($pname,$pdesc) = $sth->fetchrow_array){
			push(@ary_pname,$pname);
			push(@ary_pdesc,$pdesc);
		}
		($#ary_pname <0) and (return '---');
		if ($in{'tabaction'}){
			$params = '';
			for my $line(0..$#ary_pname){
				if ($in{$fname.':'.($line+1)}){
					$params .= "\n" if ($params);
					$params .= $in{$fname.':'.($line+1)};
				}
			}
			if ($params){
				$sth = &Do_SQL("UPDATE sl_keypoints_functions SET Params='".&filter_values($params)."' WHERE Keypoint='$fname'");
			}
		}
		
		$params =~ s/\r\n/\n/g;
		my (@ary) = split(/\n/, $params);		
		for my $line(0..$#ary_pname){
			$output .= qq|<tr>\n<td class='smalltxt' nowrap>$ary_pname[$line] &nbsp;</td>\n<td class='smalltxt'><input name="$fname:|.($line+1).qq|" value="$ary[$line]" size="20" onfocus="focusOn( this )" onblur="focusOff( this )" type="text"></td>\n</tr>|;		
		}
		if ($output){
			$output = "<table border='0' cellpadding='0' cellspacing='1'>".$output."</table>";
		}		
	}else{
		$output = "---";
	}
	return $output;
}


sub build_select_functions{
# --------------------------------------------------------
	my ($fname,$fvalue,@array)= @_;
	my ($output) = "";
	$output = "<option value='' selected>---</option>\n" if (!$fvalue);
	for my $i(0..$#array) {
		if ($fvalue eq $array[$i]){
			$output .= "<option value='$array[$i]' selected>$array[$i]</option>\n";
		}else{
			$output .= "<option value='$array[$i]'>$array[$i]</option>\n";
		}
	}
	
	$output = "<select name='$fname' onFocus='focusOn( this )' onBlur='focusOff( this )'>$output</select>";
	return $output;
}

sub trans_tag{
# --------------------------------------------------------
##############################################
	my ($tag,$name,$v) = @_;
	$v = lc($v);
	$tag =~ s/\{$name\}/$v/ig;
	return $tag;
}



 1;