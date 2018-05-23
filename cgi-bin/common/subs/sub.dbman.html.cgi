	my $dir = getcwd;
	my($b_cgibin,$a_cgibin) = split(/cgi-bin/,$dir);
	my $home_dir = $b_cgibin.'cgi-bin/common';

	## Load CMD File is exists
	if (-e "$home_dir/subs/dbman/".$in{'cmd'}.".pl" and $sys{'db_'.$in{'cmd'}}){
		require "$home_dir/subs/dbman/".$in{'cmd'}.".pl";
	}
	
	
1;
