#!/usr/bin/perl

####################################################################
########              Home Page                     ########
####################################################################


sub header_links(){
# --------------------------------------------------------
	my (@list) = split(/,/, $cfg{'applications'});
	my (@ary_url,@ary_img,$output);
	for my $i(0..$#list/3) {
		$ary_url{$list[$i*3]} = $list[$i*3+2];
		$ary_img{$list[$i*3]} = $list[$i*3+1];
	}
	my (@prefs) = split(/\|/, $usr{'pref_applications'});
 	for my $i(0..$#prefs) {
		if ($ary_img{$prefs[$i]}){
			($ary_url{$prefs[$i]} =~ /^http/) ? ($linkto = "target='blank'"):
										($linkto = "");
			#($ary_url{$prefs[$i]} =~ /egw/) and ($ary_url{$prefs[$i]} .= "?sessionid=$usr{'egw_sessionid'}&kp3=0&domain=default");
			
			$output .= "<a href='".$ary_url{$prefs[$i]}."' $linkto><img src='$va{'imgurl'}/app_bar/".$ary_img{$prefs[$i]}."' title='$prefs[$i]' alt='' border='0'></a>\n";
		}
	}
	return $output;
}

sub validate_year {
# --------------------------------------------------------
	#&cgierr("year: $in{'year'}");
	my ($sec, $min, $hour, $day, $mon, $year, $dweek, $dyear, $daylight) = localtime(time());
	$the_year =$year + 1900;
	
	$tmp = $in{'year'};
	if ($in{'year'} < $the_year) {
		$year = $the_year;
	}else{
		$year = $tmp;		
	}
	$in{'year'} = $year;
}



sub build_read_dayhour {
# --------------------------------------------------------
	my ($output);
	my (@ary) = split(/,/,$cfg{'dayhour'});
  $k=0;
	for (0..$#ary){
		$k ++;
	 if ($k == $horar) {
	  $output ="$ary[$_]";
   } 
	}
	return $output;
}

1;