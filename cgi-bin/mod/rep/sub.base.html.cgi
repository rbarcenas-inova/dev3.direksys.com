####################################################################
########              Home Page                     ########
####################################################################

sub shour_to_txt {
# --------------------------------------------------------
	my ($shour) = @_;
	my (@ary) = split(/,/,$cfg{'dayhour'});
	$shourtext = $ary[$shour-1];
	return $shourtext;
}


###############################################################
############             EXTENSION SUBS         ###############
###############################################################

sub product_query {
# --------------------------------------------------------

	my ($db)=@_;
	my ($i,$column,$maxhits,$numhits,$nh,$first,@hits,$value,$query, $condtype,$sort_order,@aux,$sth);

	if ($in{'keyword'}) {
		for my $i(0..$#db_cols){
			$column = lc($db_cols[$i]);
			($column eq 'sprice') and (next);
			$in{'keyword'} =~ s/^\s+//g;
			$in{'keyword'} =~ s/\s+$//g;
			if ($db_valid_types{$column} eq 'date' and &date_to_sql($in{'keyword'})){
				$query .= "$db_cols[$i] = '" . &date_to_sql($in{'keyword'}) . "' OR ";
			}elsif ($in{'sx'} or $in{'SX'}){
				$query .= "$db_cols[$i] = '" . &filter_values($in{'keyword'}) . "' OR ";
			}else{
				$query .= "$db_cols[$i] like '%" . &filter_values($in{'keyword'}) . "%' OR ";
			}
		}
		$query = substr($query,0,-3);
	}elsif ($in{lc($db_cols[0])} ne "*" or !$in{'listall'}){
		if ($in{'st'} =~ /or/i){
			$condtype = "OR";
		}else{
			$condtype = "AND";
		}
		for my $i(0..$#db_cols){
			$column = lc($db_cols[$i]);
			$in{$column} =~ s/^\s+//g;
			$in{$column} =~ s/\s+$//g;
			$value = &filter_values($in{$column});
			#($db_valid_types{$column} eq 'date') ?
			#	($value = &date_to_sql($in{$column})):
			#	($value = &filter_values($in{$column}));

			if ($in{$column} !~ /^\s*$/) {
				if ($in{$column} =~ /~~|\|/){
					@aux = split(/~~|\|/, $in{$column});
					$query .= "(";
					for (0..$#aux){
						($db_valid_types{$column} eq 'date') ?
							($value = &date_to_sql($aux[$_])):
							($value = &filter_values($aux[$_]));
							($in{'sx'} or $db_valid_types{$column} eq 'date')?
							($query .= "$db_cols[$i] = '$value' $condtype "):
							($query .= "$db_cols[$i] like '%$value%' $condtype ");
					}
					$query = substr($query,0,-4) . " ) $condtype ";
				
				}else{
					if ($db_valid_types{$column} eq 'date' and $value eq 'today'){
						$query .= "$db_cols[$i] = Curdate() $condtype ";
					}elsif($db_valid_types{$column} eq 'date' and $value eq 'thisweek'){
						$query .= "WEEK($db_cols[$i]) = WEEK(NOW()) $condtype ";
					}elsif($db_valid_types{$column} eq 'date' and $value eq 'thismonth'){
						$query .= "MONTH($db_cols[$i]) = MONTH(NOW()) $condtype ";
					}elsif($db_valid_types{$column} eq 'date' and $value eq 'thisyear'){	
						$query .= "YEAR($db_cols[$i]) = YEAR(NOW()) $condtype ";
					}elsif($value eq 'NULL'){
						$query .= "ISNULL($db_cols[$i]) $condtype ";			
					}elsif($in{'sx'} or $db_valid_types{$column} eq 'date'){
						$query .= "$db_cols[$i]  = '$value' $condtype ";
					}else{
						$query .= "$db_cols[$i] like '%$value%'  $condtype ";
					}
				}
			}
			if ($in{'from_'.$column} !~ /^\s*$/) {
				$in{'from_'.$column} =~ s/^\s+//g;
				$in{'from_'.$column} =~ s/\s+$//g;
				$value = &filter_values($in{'from_'.$column});
				### From To Fields
				if ($db_valid_types{$column} eq 'date' and $value eq 'today'){
					$query .= "$db_cols[$i] > Curdate() $condtype ";
				}elsif($db_valid_types{$column} eq 'date' and $value eq 'thisweek'){
					$query .= "WEEK($db_cols[$i]) > WEEK(NOW()) $condtype ";
				}elsif($db_valid_types{$column} eq 'date' and $value eq 'thismonth'){
					$query .= "MONTH($db_cols[$i]) > MONTH(NOW()) $condtype ";
				}elsif($db_valid_types{$column} eq 'date' and $value eq 'thisyear'){	
					$query .= "YEAR($db_cols[$i]) > YEAR(NOW()) $condtype ";
				}elsif($in{'sx'} or $db_valid_types{$column} eq 'date'){
					$query .= "$db_cols[$i]  > '$value' $condtype ";
				}else{
					$query .= "$db_cols[$i] > '$value'  $condtype ";
				}
			}
			if ($in{'to_'.$column} !~ /^\s*$/) {
				$in{'to_'.$column} =~ s/^\s+//g;
				$in{'to_'.$column} =~ s/\s+$//g;
				$value = &filter_values($in{'to_'.$column});
				### From To Fields
				if ($db_valid_types{$column} eq 'date' and $value eq 'today'){
					$query .= "$db_cols[$i] < Curdate() $condtype ";
				}elsif($db_valid_types{$column} eq 'date' and $in{$column} eq 'thisweek'){
					$query .= "WEEK($db_cols[$i]) < WEEK(NOW()) $condtype ";
				}elsif($db_valid_types{$column} eq 'date' and $in{$column} eq 'thismonth'){
					$query .= "MONTH($db_cols[$i]) < MONTH(NOW()) $condtype ";
				}elsif($db_valid_types{$column} eq 'date' and $in{$column} eq 'thisyear'){	
					$query .= "YEAR($db_cols[$i]) < YEAR(NOW()) $condtype ";
				}elsif($in{'sx'} or $db_valid_types{$column} eq 'date'){
					$query .= "$db_cols[$i]  < '$value' $condtype ";
				}else{
					$query .= "$db_cols[$i] < '$value'  $condtype ";
				}
			}
		}
		$query = substr($query,0,-4);
	}
	############################
	#### Search parameters #####
	############################
	####
	#### Sort by
	#### sb = ##  (## = field order) 
	####
	#### Sort Type
	#### st = or/and  (## = field order) 
	####
	#### Exact Sort
	#### sx = 1
	####
	#### From/To
	#### from_{field-name} To_{field-name}
	####
	#### Multiples Search
	#### fieldname=value1|value2|value...
	#### 
	#### Date Search (only valid for Date type fields)
	#### date_field=today
	#### date_field=thisweek 
	#### date_field=thismonth 
	#### date_field=thisyear
	#### 
	#### Null Data
	#### fieldname=NULL
	#### 
	

	### Nothing to Search
	if (!$query and $in{to_sprices.price} = 0){
		$query = "WHERE Status='On-Air' AND SPrice>0";
	}elsif ($in{'from_sprices'} != 0 or $in{'to_sprices'} != 0){
		$query = "WHERE SPrice BETWEEN $in{'from_sprices'} AND $in{'to_sprices'} AND Status='On-Air'";
	}elsif ($query){
		$query = "WHERE ($query) AND Status='On-Air' AND SPrice>0";
	}else{
		$query = "WHERE Status='On-Air' AND SPrice>0";
	}
	
	$in{'nh'} ? ($nh = $in{'nh'}) : ($nh = 1);
	$numhits = 0;

	### Count Records ###
	(exists($in{'sb'}) and $db_cols[$in{'sb'}]) and ($sort_order = "ORDER BY $db_cols[$in{'sb'}] $in{'so'}");
	my ($sth) = &Do_SQL("SELECT COUNT(*) FROM $db $query;");
	$numhits = $sth->fetchrow();

	if ($numhits == 0){
		return (0,'');
	}
	if ($in{'printingmode'}){
		$sth = &Do_SQL("SELECT * FROM $db $query $sort_order");
	}else{
		$first = ($usr{'pref_maxh'} * ($nh - 1));
		$sth = &Do_SQL("SELECT * FROM $db $query $sort_order LIMIT $first,$usr{'pref_maxh'}");
	}

	while ($rec = $sth->fetchrow_hashref){
		foreach $column (@db_cols) {
			push(@hits, $rec->{$column});
		}
	}
	return ($numhits, @hits);
}


sub gen_passwd {
# --------------------------------------------------------
# Form: validate_man_users in dbman.html.cgi
# Service: 
# Type : subroutine
# Time Last : 9/06/2007 4:34PM
# Author: Rafael Sobrino
# Description : generates a 6-character (upper/lower alpha + numeric) random password 

	my ($len) = 6;		# length of the random password
	my @chars=('a'..'z','A'..'Z','0'..'9','_');
	my ($password);
	foreach (1..$len){
		$password.=$chars[rand @chars];
	}
	return $password;	
}

sub valid_address {
# --------------------------------------------------------	
# Form: 
# Service: 
# Type : subroutine
# Time Last : 9/05/2007 4:34PM
# Author: Rafael Sobrino
# Description : validates an email address

	my($addr) = @_;
	my($domain, $valid);

	#return(0) unless ($addr =~ /^[^@]+@([-\w]+\.)+[A-Za-z]{2,4}$/);
	if ($addr =~ /^[a-zA-Z][\w\.-]*[a-zA-Z0-9]@[a-zA-Z0-9][\w\.-]*[a-zA-Z0-9]\.[a-zA-Z][a-zA-Z\.]*[a-zA-Z]$/){
		$valid = 1;
	}

	#$domain = (split(/@/, $addr))[1];
	#$valid = 0; open(DNS, "nslookup -q=any $domain |") ||	return(-1);
	#while (<DNS>) {
	#	$valid = 1 if (/^$domain.*\s(mail exchanger|
	#	internet address)\s=/);
	#}
	return($valid);
}



1;
