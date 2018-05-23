#!/usr/bin/perl

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
	### Auto Get Home_dir
	#
	# Tip: Aqui la ruta del script es cgi-bin/
	#  
	use Cwd;
	my $queryError = 0;
	my $dir = getcwd;
	my $inTransaction = 0;
	my($b_cgibin,$a_cgibin) = split(/cgi-bin/,$dir);
	my $home_dir = $b_cgibin.'cgi-bin/common';

	## Load Libs
	opendir (my $libdir, "$home_dir/subs/libs") || &cgierr("Unable to open directory $home_dir/subs/libs",604,$!);
		@files = readdir($libdir);		# Read in list of files in directory..
	closedir (LIBDIR);
	FILE: foreach my $file (@files) {
		next if ($file !~ /^lib\./);
		require ("$home_dir/subs/libs/$file");
	}
	## Load {e} libs
	if ($in{'e'}>0){
		if (-e "$home_dir/subs/e/e$in{'e'}.dbman.pl" and $0 =~ /dbman/){
			require ("$home_dir/subs/e/e$in{'e'}.dbman.pl");
		}elsif(-e "$home_dir/subs/e/e$in{'e'}.admin.pl"){
			require ("$home_dir/subs/e/e$in{'e'}.admin.pl");
		}
		## Common Libs
		if(-e "$home_dir/subs/e/e$in{'e'}.common.pl"){
			require ("$home_dir/subs/e/e$in{'e'}.common.pl");
		}
		## Functions Libs
		if(-e "$home_dir/subs/e/e$in{'e'}.functions.pl"){
			require ("$home_dir/subs/e/e$in{'e'}.functions.pl");
		}
	}


	if($cfg{'memcached'}){

		###
		### Memcached
		###
		use Cache::Memcached;

		my $cache_servers;
		#my @ary_servers = $cfg{'memcached_servers'} ? split(/,/, $cfg{'memcached_servers'}) : ("localhost:11212");
		#$cache_servers = \@ary_servers;
		$cache_servers = $cfg{'memcached_servers'} ? $cfg{'memcached_servers'} : ("localhost:11212");

		## 1) Declaramos los servidores que usara memcached
		$va{'cache'} = new Cache::Memcached {
			'servers' => [$cache_servers],
	    	'debug' => 1,       	
	    };
	    #$va{'cache'}->set_servers($cache_servers);
	    #$va{'cache'}->set('this_key','1000');
	    #$this_cache_value = $va{'cache'}->get('this_key');
	    #&cgierr( $this_cache_value );

	}


####################################################################
########              Home Page                     ########
####################################################################

sub html_base_home {
# --------------------------------------------------------
	# my $page = 
	my $fname = $cfg{'path_templates'}."/mod/".$usr{'application'}."/home".".e".$in{'e'}.".html";
	my $fnameDefault = $cfg{'path_templates'}."/mod/".$usr{'application'}."/home.html";
	my $fnameMain = "home.html";
	print "Content-type: text/html\n\n";
	if( -e $fname ){
		print &build_page($fname);
	}elsif( -e $fnameDefault){
		print &build_page($fnameDefault);
	}else{
		print &build_page($fnameMain);
	}
}

sub build_page {
# --------------------------------------------------------
	my ($tname) = @_;

	(!$usr{'pref_style'}) and ($usr{'pref_style'}=$cfg{'default_style'});
	
	my ($field,$cmdname,$cmdtype,$rep_str,$num,$page);
	if ($tname eq 'prepage'){
		$page = $va{'prepage'};
	}else{
		$page = &loadpages($cfg{'path_templates'} . $tname) ;
	}
	my ($z,$f,$fr,$fi);
	$z=$page;
	
	while ($page =~ /\[(\w{2})_([^]]+)\]/ and $num<300){
		$cmdtype  = lc($1).'_';
		$cmdname  = lc($2);
		$field    = "$1_$2";
		$rep_str = "";
		if ($cmdtype eq 'ck_'){
			$rep_str = &GetCookies($cmdname);
		}elsif($cmdtype eq 'in_'){
			$rep_str = $in{$cmdname};
		}elsif($cmdtype eq 'va_'){
			$rep_str = $va{$cmdname};

			if ($va{$cmdname} ne ''){
				if ($cmdname eq 'message_good'){
					$rep_str = qq|<div class="good">$va{$cmdname}</div>|;
				}elsif ($cmdname eq 'message_error'){
					$rep_str = qq|<div class="error">$va{$cmdname}</div>|;
				}elsif ($cmdname eq 'message_notes'){
					$rep_str = qq|<div class="notes">$va{$cmdname}</div>|;
				}
			}
		}elsif($cmdtype eq 'er_'){
			$rep_str = $error{$cmdname};
		}elsif($cmdtype eq 'ur_'){
			$rep_str = $usr{$cmdname};
		}elsif($cmdtype eq 'pm_'){
			$rep_str = $perm{$cmdname};
		}elsif($cmdtype eq 'ip_'){
			$rep_str = &build_page($cmdname.'.html') ;
		}elsif($cmdtype eq 'bz_'){ 
			my ($field,$tbl,$sel) = split(/@/,$cmdname,3);
			$rep_str = &build_select_from_enum_with_selected($field,$tbl,$sel);	
		}elsif($cmdtype eq 'bs_'){ 
			my ($field,$tbl) = split(/@/,$cmdname,2);
			$rep_str = &build_select_from_enum($field,$tbl);
		}elsif($cmdtype eq 'bc_'){ 
			my ($field,$tbl) = split(/@/,$cmdname,2);
			$rep_str = &build_checkbox_from_enum($field,$tbl);
		}elsif($cmdtype eq 'br_'){ 
			my ($field,$tbl) = split(/@/,$cmdname,2);
			$rep_str = &build_radio_from_enum($field,$tbl);
		}elsif($cmdtype eq 'ln_'){
			my ($id_name,$tbl,$field) = split(/@|:/,$cmdname,3);
			$rep_str = load_name($tbl,$id_name,$in{$id_name},$field);
			
		}elsif($cmdtype eq 'tb_'){
			if($cmdname =~ /{cmd}/){
				if($in{'cmd'} =~ /\w{2,3}_(\w+)/){
					my $cmd = $1;
					$cmdname =~ s/{cmd}/$cmd/;
				}else{
					$cmdname =~ s/{cmd}/$in{'cmd'}/;
				}
			}
			if ($cmdname eq 'templatetab'){
				$cmdname = $sys{'db_'.$in{'cmd'}.'_form'};
			}
			## check if file exists
			## require file
			$va{'tbname'} = $cmdname;
			if (-e "../../common/tabs/".$cmdname.".cgi"){
				require ('../../common/tabs/' .$cmdname. '.cgi');
				$rep_str = &build_tabs;
			}else{
				$rep_str = ' ';
			}
		}elsif($cmdtype eq 'fc_'){
			if ($in{'e'}){
				my ($func) = $cmdname . '_er_';  ## This Replace the Standard Function
				if (defined &$func){
					$rep_str =  &$func(@in_params);
				}elsif(defined &$cmdname){
					$rep_str = &$cmdname();
				}
			}elsif (defined &$cmdname){
				$rep_str = &$cmdname();
			}else{
				$rep_str = ' ';
			}
		}elsif($field =~ /^tt_([^_]+)_(.*)/){
			$rep_str = &trans_txt(${$1}{$2});
		}else{
			$rep_str = " ";
		}
		$page =~ s/\[$field\]/$rep_str/gi;
		++$num;
		$fr = $field;
	}

	## Debug Sales
	if ($cfg{'sales_debug'} and $cfg{'sales_debug'} == 1 and $tname =~ /footer/){
		$page .= "<table cellspacing=0 cellpadding=15px style='width:100%; background-color:#ffffff; background-image: url(/sitimages/debug.jpg); background-repeat: repeat-x;-moz-border-radius: 13px;border-radius: 13px ;margin-bottom:10px;'><tr><td align=center><font color=#ffffff size=4> Debug $tname </td></tr>";
		$page .= '<tr><td>';
		if(%cses){
			$page .= '<table width="48%" cellpadding=4 cellspacing=1px style="float:left;margin-right:2%;" border="0" bgcolor=#aaaaaa>';
			$page .= '<tr bgcolor=#555555 height=25px><td><font color=#ffffff><b>Variable CSES</td><td><font color=#ffffff><b>Valor</td></tr>';
			foreach my $key (keys %cses){
				$page .= '<tr height=25px bgcolor=#ffffff><td>'.$key.'</td><td><div><table>'.$cses{$key}.'</table></div></td></tr>';
			}
			$page .= '</table>';
		}

		if(%in){
			$page .= '<table width="48%" cellpadding=4 cellspacing=1px  style="float:left;margin-right:2%;" border="0"  bgcolor=#aaaaaa>';
			$page .='<tr bgcolor=#555555 height=25px><td><font color=#ffffff><b>Variable IN</td><td><font color=#ffffff><b>Valor</td></tr>';
			foreach my $key (keys %in){
				$page .= '<tr height=25px bgcolor=#ffffff><td>'.$key.'</td><td><div><table>'.$in{$key}.'</table></div></td></tr>';
			}
			$page .= '</table>';
		}
		
		if(%in){
			$page .= '<table width="98%" cellpadding=4 cellspacing=1px  style="float:left;margin-right:2%;margin-top:15px;" border="0"  bgcolor=#aaaaaa>';
			$page .='<tr bgcolor=#555555 height=25px><td><font color=#ffffff><b>Variable VA</td><td><font color=#ffffff><b>Valor</td></tr>';
			foreach my $key (keys %va){
				$page .= '<tr height=25px bgcolor=#ffffff><td valign=top>'.$key.'</td><td><div><table>'.$va{$key}.'</table></div></td></tr>';
			}
			$page .= '</table>';
		}
		$page .= '</div>';
	}

	## 11062015-AD-Log Print
	if ($in{'search'} eq 'Print' and $in{'toprint'} and $in{'cmd'} ne '' and $tname eq 'header_print.html'){
		my $message = $in{'cmd'};
		$message .= ($in{'f'})? '_'.$in{'f'}:'';
		$message .= "_printed";
		&auth_logging2($message, $in{'toprint'});
	}

	return $page;
}

sub loadpages {
# --------------------------------------------------------
# Last Modified on: 11/08/10 12:52:44
	my ($str,$f,$fi,$filetype,$ifname);
	my ($fname)= @_;
	$ifname = $fname;
	
	#if ($fname =~ /(.*)\/([a-z]*):(.*)$/ and $cfg{'path_ns_cgi_'.$2}){
	#	$fname = $1."/".$2."/".$3;
	#	$f = "1:$1 2:$2 3:$3";
	#}else{
		$fname =~ s/:/\//;
	#}
	$t = "<br>orig : $fname<br>";


	## Temporary Only English
	(!$usr{'pref_language'}) and ($usr{'pref_language'}=$cfg{'default_lang'});
	$usr{'pref_language'} = 'en';

	
	if ($fname =~ /widgets/ or  $fname =~ /perm\//  or $fname =~ /searchid|customapps|upfile|apporders/ or $fname =~ /mode_updating\.html/ or $fname =~ /mode_stopped\.html/){
		$str = $usr{'pref_language'}."/apps/";
	}elsif ($fname =~ /tab\d+\.html$/ or $fname =~ /tab\d+_\w+\.html$/){
		$str = $usr{'pref_language'} . "/tabs/";
	}elsif ($fname =~ /tabx\d+\.html$/ or $fname =~ /tabx\d+_\w+\.html$/){
		$str = $usr{'pref_language'} . "/tabs/";
	}elsif ($fname =~ /constructor.html$/ or $fname =~ /construct.html$/){
		$str = $usr{'pref_language'} . "/tabs/";
	}elsif ($fname =~ /imgman/){
		$str = $usr{'pref_language'};
	}elsif ($fname =~ /ajaxbuild/){
		$str = $usr{'pref_language'}."/apps/";
	}elsif ($fname =~ /forms/){
		if ($fname =~ /template_form\.html$|template_view\.html$/){
			$fname =~ s/template/$sys{'db_'.$in{'cmd'}.'_form'}/;
		}
		$str = $usr{'pref_language'};
		if($fname =~ /{cmd}/){
			if($in{'cmd'} =~ /\w{2,3}_(\w+)/){
				my $cmd = $1;
				$fname =~ s/{cmd}/$cmd/;
			}else{
				$fname =~ s/{cmd}/$in{'cmd'}/;
			}
		}
		$filetype = 'form';
	}elsif ($fname =~ /plist/){
		$str = $usr{'pref_language'}."/print/lprint/";
	}elsif ($fname =~ /print/){
		$fname =~ s/print//;
		if ($0 =~ /dbman$/){
			$str = $usr{'pref_language'}."/print/dbman/";
		}else{
			$str = $usr{'pref_language'}."/print/admin/";
		}
		$filetype = 'print';

	}elsif ($fname =~ /ajax/){
		## Insert ajax code in templates where exists
		
		$str = $usr{'pref_language'};
		if($fname =~ /{cmd}/){
			if($in{'cmd'} =~ /\w{2,3}_(\w+)/){
				my $cmd = $1;
				$fname =~ s/{cmd}/$cmd/;
			}else{
				$fname =~ s/{cmd}/$in{'cmd'}/;
			}
		}
		$fname =~ s/\[lang\]/$str/gi;
		if(!-e $fname){
			return '';
		}
	}elsif ($fname =~ /func/){
		$str = $usr{'pref_language'};
	#}elsif ($fname =~ /base/){
	#	$str = $usr{'pref_language'} . "/base/";	
	#}elsif ($usr{'application'}){
	#	$str = $usr{'pref_language'} . "/app/$usr{'application'}";
	}elsif ($usr{'application'}){
		$str = $usr{'pref_language'}."/mod/".$usr{'application'};
	}else{
		$str = $usr{'pref_language'};
	}
	
	
	$fname =~ s/\[lang\]/$str/gi;

	## Short Version
	my ($sfname) = $fname;
	$sfname =~ s/\.html$/_short.html/;
	if (-e $sfname and $cfg{'use_short_view_template'} == 1 and !&check_permissions('full_view_template','','')){
		$fname = $sfname;
	}

	if ($in{'e'}){

		## Short Version
		my ($sfname) = $fname;
		$sfname =~ s/_short\.html/.html/;
		$sfname =~ s/\.html$/_short.e$in{'e'}.html/;
		
		if (-e $sfname and $cfg{'use_short_view_template'} == 1 and !&check_permissions('full_view_template','','')){

			$fname = $sfname;

		}else{

			my ($tfname) = $fname;
			$tfname =~ s/\.html$/.e$in{'e'}.html/;
			if (-e $tfname){
				$fname = $tfname;
			}

		}

	}

	$f = $fname;
	if (!-e $fname){
		$fname = $ifname;
		$str = $usr{'pref_language'}.'/common';
		$fname =~ s/\[lang\]/$str/gi;

		my ($tfname) = $fname;
		$tfname =~ s/\.html$/.e$in{'e'}.html/;
		if (-e $tfname){
			$fname = $tfname;
		}
	}

	if (open (my $cfg,"<", $fname)){
		return (join("",<$cfg>));
	}elsif ($filetype eq 'form'){
		return 	&build_form($fname)
	}elsif ($filetype eq 'print'){
		return &build_custom_viewfields($va{'page_title'},join(',',@db_cols));
	}elsif($cfg{'cd'}){
		&cgierr("Unable to Open<br>$t<br>fname:$fname<br>f:$f<br>path_templates:$cfg{'path_templates'}<br><br>",$!,234);

	}
	return '';
}

sub html_unauth {
# --------------------------------------------------------
	print "Content-type: text/html\n\n";
 	print &build_page('unauth.html');
}

sub html_smallunauth {
# --------------------------------------------------------
	print "Content-type: text/html\n\n";
 	print &build_page('unauth_small.html');
}

sub html_unauth_tab {
# --------------------------------------------------------
	print "Content-type: text/html\n\n";
 	print &build_page('tab_unauth.html');
	if ($in{'xtabs'}){
		print "Content-type: text/html\n\n";
	 	print &build_page('tab_unauth.html');
	}else{
		return &build_page('tab_unauth.html');
	}
}
sub html_message_tab {
# --------------------------------------------------------
	if ($in{'xtabs'}){
		print "Content-type: text/html\n\n";
	 	print &build_page('tab_message.html');
	}else{
		return &build_page('tab_message.html');
	}
}

sub html_closed {
# --------------------------------------------------------
	print "Content-type: text/html\n\n";
 	print &build_page('mode_stopped.html');
}

sub html_updating {
# --------------------------------------------------------
	print "Content-type: text/html\n\n";
 	print &build_page('mode_updating.html');
}

sub html_notavail {
# --------------------------------------------------------
	print "Content-type: text/html\n\n";
 	print &build_page('not_available.html');
}

sub html_blank {
# --------------------------------------------------------
	print "Content-type: text/html\n\n";
	print "<body></body></html>";
}


sub trans_txt {
# --------------------------------------------------------
# Last Modified RB: 05/15/09  18:14:58 -- Se incluye multiempresa

	my ($to_trans) = @_;
	my (@ary,$fname,$line);
	if ($trs{$to_trans}){
		return $trs{$to_trans};
	}else{
		(!$usr{'pref_language'}) and ($usr{'pref_language'}=$cfg{'default_lang'});
		$fname = "$cfg{'path_templates'}";  ##$cfg{'path_templates'}.$femp;
		$fname =~ s/\[lang\]/$usr{'pref_language'}/gi;	
		
		
		if ($in{'e'}>0 and -e $fname."messages.e$in{'e'}.txt"){
			$femp =	"messages.e$in{'e'}.txt";
		}elsif (&GetCookies("e") > 0 and !exists($in{'e'}) and -e $fname."messages.e$in{'e'}.txt"){
			$in{'e'} = &GetCookies("e");
			$femp =	"messages.e$in{'e'}.txt";
		}else{
			$femp = "messages.txt";
		}
		if (open (my $cfg, "<", $fname . $femp)){
			LINE: while (<$cfg>) {
				(/^#/)      and next LINE;
				(/^\s*$/)   and next LINE;
				$line = $_;
				$line =~ s/\r|\n//g;
				@ary = split(/=/,$line,2);
				$trs{$ary[0]} = $ary[1];
			}
		}else{
			&cgierr($!);
		}
		my (@apps) = ('admin','crm','sales','wms','setup','ecom','custom','pos','accounting');
		for (0..$#apps){
			$fname = $cfg{'path_templates'}."mod/$apps[$_]/";
			$fname =~ s/\[lang\]/$usr{'pref_language'}/gi;
			if ($in{'e'}>0 and -e $fname."messages.e$in{'e'}.txt"){
				$femp =	"messages.e$in{'e'}.txt";
			}elsif (&GetCookies("e") > 0 and !exists($in{'e'}) and -e $fname."messages.e$in{'e'}.txt"){
				$in{'e'} = &GetCookies("e");
				$femp =	"messages.e$in{'e'}.txt";
			}else{
				$femp = "messages.txt";
			}
			if (open (my $cfg, "<", $fname . $femp)){
				LINE: while (<$cfg>) {
					(/^#/)      and next LINE;
					(/^\s*$/)   and next LINE;
					$line = $_;
					$line =~ s/\r|\n//g;
					@ary = split(/=/,$line,2);
					$trs{$ary[0]} = $ary[1];
				}
			}
			if ($trs{$to_trans}){
				return $trs{$to_trans};
			}
		}
		
		## Apps
		$fname = $cfg{'path_templates'}."apps/";
		$fname =~ s/\[lang\]/$usr{'pref_language'}/gi;
		if ($in{'e'}>0 and -e $fname."messages.e$in{'e'}.txt"){
			$femp =	"messages.e$in{'e'}.txt";
		}elsif (&GetCookies("e") > 0 and !exists($in{'e'}) and -e $fname."messages.e$in{'e'}.txt"){
			$in{'e'} = &GetCookies("e");
			$femp =	"messages.e$in{'e'}.txt";
		}else{
			$femp = "messages.txt";
		}
		if (open (my $cfg, "<", $fname . $femp)){
			LINE: while (<$cfg>) {
				(/^#/)      and next LINE;
				(/^\s*$/)   and next LINE;
				$line = $_;
				$line =~ s/\r|\n//g;
				@ary = split(/=/,$line,2);
				$trs{$ary[0]} = $ary[1];
			}
			if ($trs{$to_trans}){
				return $trs{$to_trans};
			}
		}

		## customapps
		$fname = $cfg{'path_templates'}."apps/customapps/";
		$fname =~ s/\[lang\]/$usr{'pref_language'}/gi;
		if ($in{'e'}>0 and -e $fname."messages.e$in{'e'}.txt"){
			$femp =	"messages.e$in{'e'}.txt";
		}elsif (&GetCookies("e") > 0 and !exists($in{'e'}) and -e $fname."messages.e$in{'e'}.txt"){
			$in{'e'} = &GetCookies("e");
			$femp =	"messages.e$in{'e'}.txt";
		}else{
			$femp = "messages.txt";
		}
		if (open (my $cfg, "<", $fname . $femp)){
			LINE: while (<$cfg>) {
				(/^#/)      and next LINE;
				(/^\s*$/)   and next LINE;
				$line = $_;
				$line =~ s/\r|\n//g;
				@ary = split(/=/,$line,2);
				$trs{$ary[0]} = $ary[1];
			}
			if ($trs{$to_trans}){
				return $trs{$to_trans};
			}
		}
	}
	if ($trs{$to_trans}){
		return $trs{$to_trans};
	}else{
		return $to_trans;
	}
}

##########################################################
##			Misc   				##
##########################################################

sub build_select_field {
# --------------------------------------------------------
	my ($column, $value) = @_;
	my (@fields, $output);

	@fields = split (/\,/, $db_select_fields{$column});
	if ($#fields == -1) {
		$db_select_fields{$column} = &trans_txt('none');
		@fields = ();
	}
	$output = qq|<select name="$column" onFocus='focusOn( this )' onBlur='focusOff( this )'><option>---</option>|;
	foreach my $field (@fields) {
		$field eq $value ?
			($output .= "<option value='$field' selected>$field</option>\n") :
			($output .= "<option value='$field'>$field</option>\n");
	}
	$output .= "</select>";

	return $output;
}

sub build_select_dbfield {
# --------------------------------------------------------
	my ($column,$value,$tabindex,$fname,$db,$style,$showid,$showcustomid,$sortbydesc) = @_;
	my ($output,$rec);

	$output = qq|<select $style name="$column" onFocus='focusOn( this )' onBlur='focusOff( this )'><option>---</option>\n|;
	my ($orderby) = ($sortbydesc and $sortbydesc == 1)? " ORDER BY $fname" : "";
	my ($sth) = &Do_SQL("SELECT * FROM $db $orderby");
	$db =~ s/^(sl_|cu_)+//g;
	while ($rec = $sth->fetchrow_hashref){
		if ($showid and $showid == 1){
			my ($showcustomid) = ($showcustomid and $showcustomid ne '')? $showcustomid : $rec->{'ID_'.$db};
			($rec->{'ID_'.$db} eq $value) ?
				($output .= "<option value='$rec->{'ID_'.$db}' selected>$rec->{$fname} (".$showcustomid.")</option>\n") :
				($output .= "<option value='$rec->{'ID_'.$db}'>$rec->{$fname} (".$showcustomid.")</option>\n");
		}else{
			($rec->{'ID_'.$db} eq $value) ?
				($output .= "<option value='$rec->{'ID_'.$db}' selected>$rec->{$fname}</option>\n") :
				($output .= "<option value='$rec->{'ID_'.$db}'>$rec->{$fname}</option>\n");
		}

	}
	$output .= "</select>";

	return $output;
}

sub load_enum_toarray {
# --------------------------------------------------------
	my ($tbl_name,$col_name) = @_;
	my (@ary,@ary_memcache,@fields,%tmp,$data);
	my $sth;
	my $cache_flag = 0;

	if( $cfg{'memcached'} ){

		###
		##  Memcache Data
		###
		(%tmp) = $va{'cache'}->get('load_enum_toarray_e' . $in{'e'} . '_' . $tbl_name . '_' . $in{'second_conn'});
		$data = $tmp{$tbl_name . '_values'}->[1];

	}

	if(!$tmp{$tbl_name . '_values'}->[0]){

		## Result is not cached yet
		$cache_flag = 1 if $cfg{'memcached'};

		###### Load Table Properties
		$sth = &Do_SQL("describe $tbl_name $col_name;")	if !$in{'second_conn'};
		$sth = &Do_SQL("describe $tbl_name $col_name;",1)	if $in{'second_conn'};
		while (@ary = $sth->fetchrow_array() ) {
			push(@db_cols,$ary[0]);
			$ary[0] = lc($ary[0]);
			if ($ary[1] =~ /enum\((.*)/i){
				$data = $1;
				# $data =~ s/','/,/g; ## AD:Se comenta porque creaba 2 option con 'ACAPULCO,GRO'
				$data = substr($data,1,-2)
			}
		}

		@ary_memcache = (1, $data);

	}else{

		## Data Cached
		$tmp{$tbl_name . '_values'}->[0] = 2;
		#$va{'str'} = qq|Tabla: |. $tbl_name .qq|<br>
		#	Cachada: |. $tmp{$tbl_name . '_values'}->[0] .qq|<br>|;
		#&cgierr($data);

	}

	## Set Memcached if flag activated 
	$va{'cache'}->set('load_enum_toarray_e' . $in{'e'} . '_' . $tbl_name . '_' . $in{'second_conn'}, { $tbl_name . '_values' => [1, "$data"] }) if $cache_flag;


	@fields = split (/\','/, $data);
	return @fields;

}

sub load_enum_toarray_secondConn{
# --------------------------------------------------------
	my ($tbl_name,$col_name) = @_;
	my (@ary,@fields,$data);
	###### Load Table Properties
	my ($sth) = &Do_SQL("describe $tbl_name $col_name;",1);
	while (@ary = $sth->fetchrow_array() ) {
		push(@db_cols,$ary[0]);
		$ary[0] = lc($ary[0]);
		if ($ary[1] =~ /enum\((.*)/i){
			$data = $1;
			$data =~ s/','/,/g;
			$data = substr($data,1,-2)
		}
	}
	@fields = split (/\,/, $data);
	return @fields;
}

sub build_select_from_enum {
# --------------------------------------------------------
	my ($column,$tbl_name) = @_;
	my ($data,$output);
	@fields = &load_enum_toarray($tbl_name,$column);
	
	if ($#fields == -1) {
		$db_select_fields{$column} = &trans_txt('none');
		return $output;
	}
	foreach my $field (@fields) {
		$output .= "<option value='$field'>$field</option>\n";
	}
	return $output;
}



sub build_select_from_enum_with_selected{
# --------------------------------------------------------
# Forms Involved: 
# Created on: 06/18/09 13:22:55
# Author: MCC C. Gabriel Varela S.
# Description :   
# Parameters :
	my ($column,$tbl_name,$selected) = @_;
	my ($data,$output);

	@fields = &load_enum_toarray($tbl_name,$column);
	if ($#fields == -1) {
		$db_select_fields{$column} = &trans_txt('none');
		return $output;
	}
	foreach my $field (@fields) {
		$selectedtxt="";
		$selectedtxt="selected"if($field eq $selected);
		$output .= "<option value='$field' $selectedtxt>$field</option>\n";
	}
	return $output;
}

#############################################################################
#############################################################################
#   Function: build_checkbox_from_enum 
#
#       Es: Crea una serie de checboxes basados en los valores de un campo ENUM de la DB 
#       En: 
#
#
#    Created on: 
#
#    Author: _Carlos Haas_
#
#    Modifications:
#
#        - Modified on ** by _Roberto Barcenas_ : 
#
#   Parameters:
#
#      - x  
#      - y  
#
#  Returns:
#
#      - $output: Cadena con los checkbox creados
#
#   See Also:
#
#      <build_checkbox_field>
#
sub build_checkbox_from_enum {
#############################################################################
#############################################################################

	my ($column,$tbl_name) = @_;
	my ($data,$output);
	my $iname = $column;
	if($column =~ /(.+):(.+)/){
		$column = $1;
		$iname = $2;
	}

	@fields = &load_enum_toarray($tbl_name,$column);
	if ($#fields == -1) {
		$db_select_fields{$column} = &trans_txt('none');
		return $output;
	}



	for (0..$#fields){
		$output .= '<span class="checa"><input type="checkbox" id="'.$column.'_'.lc($fields[$_]).'" name="'.$iname.'" value="'.$fields[$_].'" class="checkbox"> <label for="'.$column.'_'.lc($fields[$_]).'">'.$fields[$_].'</label></span>'."\n";
	}

	return $output;
}

#############################################################################
#############################################################################
#   Function: build_radio_from_enum
#
#       Es: Crea una serie de checboxes basados en los valores de un campo ENUM de la DB 
#       En: 
#
#
#    Created on: 
#
#    Author: Roberto Barcenas
#
#    Modifications:
#
#        - Modified on ** by _Roberto Barcenas_ : 
#
#   Parameters:
#
#      - x  
#      - y  
#
#  Returns:
#
#      - $output: Cadena con los radio button creados
#
#   See Also:
#
#      <build_radio_field>
#
sub build_radio_from_enum {
#############################################################################
#############################################################################

	my ($column,$tbl_name) = @_;
	my ($data,$output);
	my $iname = $column;
	if($column =~ /(.+):(.+)/){
		$column = $1;
		$iname = $2;
	}

	my (@fields) = &load_enum_toarray($tbl_name,$column);
	if ($#fields == -1) {
		$db_select_fields{$column} = &trans_txt('none');
		return $output;
	}

	for (0..$#fields){
		$output .= '<span class="checa"><input type="radio" id="'.$column.'_'.lc($fields[$_]).'" name="'.$iname.'" value="'.$fields[$_].'" class="radio"> <label for="'.$column.'_'.lc($fields[$_]).'">'.$fields[$_].'</label></span>'."\n";
	}

	return $output;
}

#############################################################################
#############################################################################
#   Function: build_checkbox_field 
#
#       Es: Crea una serie de checkbox enlazados a un campo de DB, basados en una serie de valores recibidos
#       En: 
#
#
#    Created on: 
#
#    Author: _Carlos Haas_
#
#    Modifications:
#
#        - Modified on ** by _Roberto Barcenas_ : 
#
#   Parameters:
#
#      - x  
#      - y  
#
#  Returns:
#
#      - $output: Cadena con los checkbox creados
#
#   See Also:
#
#      <build_checkbox_from_enum>
#
sub build_checkbox_field {
#############################################################################
#############################################################################

	my ($column, $values) = @_;
	if (!$db_select_fields{$column}) {
		$db_select_fields{$column} = &trans_txt('none');
	}

	my @names  = split (/,/, $db_select_fields{$column});
	my @values = split (/\|/, $values);
	my ($name, $output);

	LINE: foreach my $name (@names) {
		($name eq '---') and (next LINE);
		(grep $_ eq $name, @values) ?
			($output .= '<span class="checa"><input type="checkbox" id="'.$column.'_'.$name.'" name="'.$column.'" value="'.$name.'" checked class="checkbox"> <label for="'.$column.'_'.$name.'">'.$name.'</label></span>'."\n") :
			($output .= '<span class="checa"><input type="checkbox" id="'.$column.'_'.$name.'" name="'.$column.'" value="'.$name.'" class="checkbox"> <label for="'.$column.'_'.$name.'">'.$name.'</label></span>'."\n");
	}
	return $output;
}

#############################################################################
#############################################################################
#   Function: build_radio_field
#
#       Es: Crea una serie de radio button enlazados a un campo de DB, basados en una serie de valores recibidos
#       En: 
#
#
#    Created on: 
#
#    Author: _Carlos Haas_
#
#    Modifications:
#
#        - Modified on ** by _Roberto Barcenas_ : 
#
#   Parameters:
#
#      - x  
#      - y  
#
#  Returns:
#
#      - 
#
#   See Also:
#
#      <build_radio_from_enum>
#
sub build_radio_field {
#############################################################################
#############################################################################

	my ($column, $value) = @_;
	my (@buttons, $button, $output);
	my $count  = 1;

	@buttons = split (/,/, $db_select_fields{$column});

	if ($#buttons == -1) {
		$db_select_fields{$column} = &trans_txt('none');
		@fields = 'None';
	}
	LINE: foreach my $button (@buttons) {
		($button eq '---') and (next LINE);
		($button eq $value) ?
			($output .= '<span class="checa"><input type="radio" id="'.$column.'_'.$button.'" name="'.$column.'" value="'.$button.'" checked class="radio"> <label for="'.$column.'_'.$button.'">'.$button.'</label></span>'."\n") :
			($output .= '<span class="checa"><input type="radio" id="'.$column.'_'.$button.'" name="'.$column.'" value="'.$button.'" class="radio"> <label for="'.$column.'_'.$button.'">'.$button.'</label></span>'."\n");

	}
	return $output;
}

sub build_select_dbtypes {
# --------------------------------------------------------
	my ($column, $value) = @_;
	my (@fields1,@fields2, $output);

	@fields1 = split (/\,/, 'alpha,numeric,decimal,date,time,text,list');
	@fields2 = split (/\,/, &trans_txt('dbsfldtypes'));


	$output = qq|<select name="$column"  onFocus='focusOn( this )' onBlur='focusOff( this )'><option>---</option>|;
	for (0..$#fields1) {
		$fields1[$_] eq $value ?
			($output .= "<option value='$fields1[$_]' selected>$fields2[$_]</option>\n") :
			($output .= "<option value='$fields1[$_]'>$fields2[$_]</option>\n");
	}
	$output .= "</select>";

	return $output;
}


##########################################################
##			Misc   				##
##########################################################
sub send_mail {
# --------------------------------------------------------
	my ($from_mail,$to_mail,$subject_mail,$body_mail,$content_type) = @_;
	my ($status);
	if ($subject_mail=~ /^\s*$/) {$subject_mail = "No Subject"}
	if ($to_mail=~ /^\s*$/) { return;}
	
	if ($body_mail=~ /^\s*$/ ) { $status .= "<li>The message can not be left blank</li>";}
#  	if ($to_mail =~ /(@.*@)|(\.\.)|(@\.)|(\.@)|(^\.)/ or $to_mail !~ /^.+\@(\[?)[a-zA-Z0-9\-\.]+\.([a-zA-Z]{2,3}|[0-9]{1,3})(\]?)$/ ){
	if ($to_mail =~ /(@.*@)|(\.\.)|(@\.)|(\.@)|(^\.)/){
 		$status .= "<li>Invalid Email Address</li>";
 	}
 	if ($status){
 		return ($status);
 	}
 	if($content_type eq ''){
		$content_type = 'Content-type: text/html; charset=iso-8859-1';
 	}elsif ($content_type eq 'none'){
		$content_type = '';
	}
 	
 	if ($cfg{'MailType'} eq 'ext'){
		open(MAIL, "| $cfg{'sendmail'} -t");
		$status = $!;
		print MAIL "From: \"$from_mail\" <$from_mail>\n";
		print MAIL "To: \"$to_mail\" <$to_mail>\n";
		#print MAIL "BCC: \"$cfg{'to_email_debug'}\" <$cfg{'to_email_debug'}>\n";
		print MAIL "Subject: $subject_mail\n";
		print MAIL "Reply-To:  <$from_mail>\n";
		print MAIL "X-Priority: 3\n";
		print MAIL "X-MSmail-Priority: Normal\n";
		print MAIL "Return-Path: $from_mail\n";
		print MAIL "X-mailer: nsmail\n";
		print MAIL "$content_type\n\n";
		
		print MAIL "$body_mail\n\n";
		close MAIL;
		return ($status);

	}elsif ($cfg{'MailType'} =~ /smtpnet/){
		use Net::SMTP;
		$SMTP_HOST =  $line[0]; # where your SMTP server resides
		$smtp = Net::SMTP->new($cfg{'sendmail'},Timeout=>30) or die 'server unreachable:' .$cfg{'sendmail'};
		$smtp->auth($cfg{'sendmail_user'},$cfg{'sendmail_pass'});
		$smtp->mail($from_mail);
		$smtp->recipient($to_mail);
		#$smtp->bcc($cfg{'to_email_debug'});
		$smtp->data;
		$smtp->datasend("From: $from_mail\nTo: $to_mail\nBCC: $cfg{'to_email_debug'}\nSubject: $subject_mail\n$content_type\n\n$body_mail");
		$smtp->dataend;
		$smtp->quit;
	}elsif ($cfg{'MailType'} =~ /gmail/){
		use Net::SMTP::SSL;
		my $smtp = Net::SMTP::SSL->new(
		        'smtp.gmail.com',
		        Port  => 465,
		        Debug => 0,
		        );
		$smtp->auth( $cfg{'sendmail_user'}, $cfg{'sendmail_pass'} );
		$smtp->mail($from_mail);
		$smtp->to($to_mail);
		#$smtp->cc("$mail_cc") if $mail_cc;
		#$smtp->bcc("$mail_bcc") if $mail_bcc;
		$smtp->bcc($cfg{'to_email_debug'});
		$smtp->data();
		$smtp->datasend("From: $from_mail\nTo: $to_mail\nBCC: $cfg{'to_email_debug'}\nSubject: $subject_mail\n$content_type\n\n$body_mail");
		$smtp->dataend();
		$smtp->quit;
	}else{
		##($from_mail,$to_mail,$subject_mail,$body_mail)
		use Socket;
		my($mailServer) = $cfg{'sendmail'};
		$main::SIG{'INT'} = 'closeSocket';
		my($proto)      = getprotobyname("tcp")        || 6;
		my($port)       = getservbyname("SMTP", "tcp") || 25;
		my($serverAddr) = (gethostbyname($mailServer))[4];
		if (!$serverAddr) {  return 6;};
		socket(SMTP, AF_INET(), SOCK_STREAM(), $proto)  or (return 7);
		connect(SMTP, pack('S n a4 x8', AF_INET(), $port, $serverAddr));
		select(SMTP); $| = 1; select(STDOUT);    # use unbuffered i/o.
		sendSMTP("HELO\n");
		sendSMTP("MAIL From: <$from_mail>\n");
		sendSMTP("RCPT To: <$to_mail>\n");
		sendSMTP("DATA\n");
		send(SMTP, "From: <$from_mail> \n", 0);
		send(SMTP, "Subject: $subject_mail \n", 0);
		send(SMTP, "$content_type \n\n", 0);
		send(SMTP, $body_mail, 0);
		sendSMTP("\r\n.\r\n");
		$buffer = sendSMTP(1, "QUIT\n");
		close(SMTP);
		$resp = (split(/ /, $buffer))[0] ;
		if ($resp ne "250") {return 8;}

	}
}

sub closeSocket {
	close(SMTP);
	return 10;
}

sub sendSMTP {
	my($buffer) = @_;
	send(SMTP, $buffer, 0);
	recv(SMTP, $buffer, 200, 0);
	return $buffer;
}

sub send_text_mail {
# --------------------------------------------------------
	my ($from_mail,$to_mail,$subject_mail,$body_mail) = @_;
	return send_mail($from_mail,$to_mail,$subject_mail,$body_mail,'none');
}

sub send_email {
# --------------------------------------------------------
# Created on: 11/05/2007 3:31PM
# Author: Rafael Sobrino
# Description : This subroutine sends an email using debian's sendmail
# Probar Email::Lite

	return send_mail($from_mail,$to_mail,$subject_mail,$body_mail,'none');
}


#############################################################################
#############################################################################
#   Function: send_mandrillapp_email
#
#       Es: Envia correo electronico a traves del servicio smtp de Mandrillapp
#       En: Send email through mandrillapp smtp service
#
#
#    Created on: 05/28/2014  11:39:34
#
#    Author: _Roberto Barcenas_
#
#    Modifications:
#
#   Parameters:
#
#       - 
#		- 
#
#  Returns:
#
#      - 
#
#   See Also:
#
#      <>
#
#
sub send_mandrillapp_email{
#############################################################################
#############################################################################

	my ($from_mail,$to_mail,$subject_mail,$body_mail,$text_mail,$attachment_string,$attachment_name,$attachment_ext) = @_;

	#&cgierr(qq|$from_mail,$to_mail,$subject_mail,$body_mail,$text_mail|);
	use JSON;
	use JSON::Parse 'parse_json';
	use JSON::Parse 'valid_json';
	use Data::Dumper;
	use WebService::Mandrill;
	
	my @ary_email = split(/,/, $to_mail);
	my $str_email;
	my $response;
	my $status;
	my $this_attachment_type = 'text/plain';
	(!$attachment_name) and ($attachment_name = 'attachment.' . $attachment_ext);


	if($attachment_string ne '' and $attachment_ext ne ''){

		if( lc($attachment_ext) eq 'csv' ){
			$this_attachment_type = 'text/csv';
		}elsif(lc($attachment_ext) eq 'pdf' ){
			$this_attachment_type = 'application/pdf';
		}elsif(lc($attachment_ext) eq 'xls' ){
			$this_attachment_type = 'application/vnd.ms-excel';
		}elsif(lc($attachment_ext) eq 'gif' ){
			$this_attachment_type = 'image/gif';
		}elsif(lc($attachment_ext) eq 'png' ){
			$this_attachment_type = 'image/png';
		}elsif(lc($attachment_ext) eq 'jpeg' ){
			$this_attachment_type = 'image/jpeg';
		}	

	}


	for(0..$#ary_email){

		my $this_email = $ary_email[$_];
		
		if ($this_email =~ /^invalid::/){

			$status = 'Invalid';

		}else{

			#print "Email: $this_email is ok to send\n";
		    my $mandrill = WebService::Mandrill->new(
		        debug   => 0,
		        api_key => $cfg{'mandrillapp_key'},
		    );
		    
		    #&cgierr("$from_mail - $to_mail - $str_email -  $subject_mail - $body_mail - " .$cfg{'mandrillapp_key'});
		    $response = $mandrill->send(
		        subject      => $subject_mail,
		        from_email   => $from_mail,
		        html 		 => $body_mail,
		        text         => $text_mail,
		        track_opens  => 1,
		        track_clicks => 1,
		        to => [
		            { 
		            	email => $this_email 
		            }
		        ],
		        attachments => [
		            {
		                type => $attachment_type,
		                name => $attachment_name,
		                content => $attachment_string
		            }
		        ],

		    );
		    
		    if ( valid_json($response->{'raw'}) ) {

				# Decode the entire JSON
				my $decoded_json = decode_json( $response->{'raw'} );

				my @res = @{ $decoded_json };
				foreach my $f ( @res ) {
					$status = $f->{"status"};
					$reason = $f->{"reject_reason"};
					 #print $f->{"email"} . "<br>";
					 #print $f->{"status"} . "<br>";
					 #print $f->{"_id"} . "<br>";
					 #print $f->{"reject_reason"} . "<br>";
				}
				
				$status = 'ok' if ($status =~ /sent|queued/);
		    }
		
		}

	}
 	
 	return ($status, $reason);

}

#############################################################################
#############################################################################
#   Function: send_mandrillapp_email_attachment
#
#       Es: Envia correo electronico a traves del servicio smtp de Mandrillapp
#       En: Send email through mandrillapp smtp service
#
#
#    Created on: 05/13/2016  11:39:34
#
#    Author: _Fabian Cañaveral_
#
#    Modifications:
#
#   Parameters:
#
#       - 
#		- 
#
#  Returns:
#
#      - 
#
#   See Also:
#
#      <>
#
#
sub send_mandrillapp_email_attachment{
#############################################################################
#############################################################################

    my ($from_mail,$to_mail,$subject_mail,$body_mail,$text_mail,$attachment) = @_;
    use JSON;
    use Data::Dumper;
    use WebService::Mandrill;
    my @ary_email = split(/,/, $to_mail);
    my $str_email;
    my $response;

    for(0..$#ary_email){
        my $this_email = $ary_email[$_];
        my $mandrill = WebService::Mandrill->new(
            debug   => 0,
            api_key => $cfg{'mandrillapp_key'},
        );
        
        my @fileAtt;
        use Data::Dumper;        
        if($attachment){
            while (($fileName,$fileContent) = each %{$attachment}){
                push @fileAtt, {
                    type    => 'application/octet-stream',
                    content =>  $fileContent,
                    name    =>  $fileName,
                };
            }
        }
        my %pars = (
            subject      => $subject_mail,
            from_email   => $from_mail,
            html         => $body_mail,
            text         => $text_mail,
            track_opens  => 1,
            track_clicks => 1,
            to => [
                { email => $this_email }
            ],
        );
        $pars{'attachments'} =\@fileAtt;
        $response = $mandrill->send(%pars);         
    }

    return $response;
}


sub html_print_headers {
# --------------------------------------------------------
	my ($title) = @_;
	print "Content-type: text/html\n\n";
	if ($title){
			print qq|
			<html>
			<title>SLTV Administration : $title</title>
			<meta http-equiv="Content-Type" content="text/html; charset=iso-8859-1">
			<link REL="STYLESHEET" HREF="$va{'imgurl'}/$usr{'pref_style'}/main.css" TYPE="text/css">
			<script language="JavaScript1.2" src="$va{'imgurl'}/$usr{'pref_style'}/main.js"></script>
			<script language="JavaScript1.2">
			function logoff(){
				if (confirm("Are you sure want to Exit?    ")){
					this.location.href = '/index.php?logoff=1';
				}
			}
			</script>
			
			<style type="text/css">\@import url($va{'imgurl'}/jscalendar/calendar-win2k-1.css);</style>
			<link rel="stylesheet" type="text/css" media="all" href="$va{'imgurl'}/jscalendar/skins/aqua/theme.css" title="Aqua" />
			
			<script type="text/javascript" src="$va{'imgurl'}/jscalendar/calendar.js"></script>
			<script type="text/javascript" src="$va{'imgurl'}/$usr{'pref_style'}/calendar_lang.js"></script>
			<script type="text/javascript" src="$va{'imgurl'}/jscalendar/calendar-setup.js"></script>
			</head>\n\n|;
	}
}




##########################################################
##			General Subs				  ##
##########################################################
sub html_login_form {
# --------------------------------------------------------
	$in{'errormessage'} = @_;
	$usr{'pref_style'}  = $cfg{'default_style'};
	print "Content-type: text/html\n\n";
 	print &build_page('login.html');
}

##########################################################
##			General Subs				  ##
##########################################################

sub html_print_jstop {
# --------------------------------------------------------
	&html_print_headers ('Printing.....');
	print qq|
	<body onload="prn()" style="background-color:#FFFFFF">
<script defer>
function prn() {
	window.print()
	return false;
}
</script>\n|;
}

sub get_sec {
# --------------------------------------------------------
	my ($sec, $min, $hour, $day, $mon, $year, $dweek, $dyear, $daylight) = localtime(time());
	return ($sec+$min*60+$hour*3600);
}

sub get_time {
# --------------------------------------------------------
	my ($sec, $min, $hour, $day, $mon, $year, $dweek, $dyear, $daylight) = localtime(time());
	($sec < 10)  and ($sec = "0$sec");
	($min < 10)  and ($min = "0$min");
	($hour < 10) and ($hour = "0$hour");

	return "$hour:$min";
}

sub get_date {
# --------------------------------------------------------
	my ($sec, $min, $hour, $day, $mon, $year, $dweek, $dyear, $daylight) = localtime(time());
	my (@months, $output,$year_num,$mon_num);
	if ($usr{'pref_language'}){
		@months = qw!Jan Feb Mar Apr May Jun Jul Aug Sep Oct Nov Dec!;
	}else{
		@months = qw!Ene Feb Mar Apr May Jun Jul Ago Sep Oct Nov Dic!;
	}

	($day < 10) and ($day = "0$day");

	$year_num = $year - 100;
	($year_num < 10) and ($year_num = "0$year_num");

	$mon_num = $mon + 1;
	($mon_num < 10) and ($mon_num = "0$mon_num");
	$output = "$day-$months[$mon]-" . ($year + 1900);

    return $output;
}

sub get_sql_date {
# --------------------------------------------------------
	my ($sec, $min, $hour, $day, $mon, $year, $dweek, $dyear, $daylight);
	my ($in_date) = @_;
	if ($in_date){
		($sec, $min, $hour, $day, $mon, $year, $dweek, $dyear, $daylight) = localtime($in_date);
	}else{
		($sec, $min, $hour, $day, $mon, $year, $dweek, $dyear, $daylight) = localtime(time());
	}
	my (@months, $output,$year_num,$mon_num);

	$year += 1900;
	++$mon;

	$mon = '0' . $mon if length($mon) == 1;
	$day = '0' . $day if length($day) == 1;

    return "$year-$mon-$day";
}

sub sql_to_date {
# --------------------------------------------------------
	my ($date)   = $_[0];
	($date eq '0000-00-00') and ($date = '');
	
	return $date;
	my (@months) = split(/ /, $cfg{'months_'.$usr{'pref_language'}});;

	my ($year,$mon,$day) = split(/-|\/|:/, $date,3);
	return ("$day-$months[$mon-1]-$year");
}


sub format_date {
# --------------------------------------------------------
# Created on: 11/15/2007 9:15AM
# Author: Rafael Sobrino
# Description : changes a date format from dd/mm/yyyy to yyyy-mm-dd
# Notes: 

	my ($mydate) = @_;
	my (@ary) = split('\/', $mydate);
	#$mydate =~ s/\//\-/g;
	foreach my $value (@ary){
		if ($value < 10){
			$value = "0$value";
		}
	}
	
	return "$ary[2]-$ary[1]-$ary[0]";
}

sub format_us_date {
# --------------------------------------------------------
# Created on: 11/15/2007 9:15AM
# Author: Rafael Sobrino
# Description : changes a date format from yyyy-mm-dd to mm-dd-yyyy
# Notes: 

	my ($mydate) = @_;
	my (@ary) = split("\/|-", $mydate);
	#$mydate =~ s/\//\-/g;
	foreach my $value (@ary){
		if ($value < 10){
			$value = "0$value";
		}
	}
	
	return "$ary[1]/$ary[2]/$ary[0]";
}

sub weeknum{
# --------------------------------------------------------
	my ($in_date) = @_;
	my ($sth) = &Do_SQL("SELECT WEEK('$in_date',1),WEEK(CONCAT(YEAR('$in_date'),'-01-01'))");
	my ($wnum,$startweek) = $sth->fetchrow_array;
	++$wnum;
	if ($startweek == 0){
		--$wnum;
	}
	if ($wnum > 53){
		$wnum = 1;
	}
	return $wnum;
}


sub timestamp_to_date{
# --------------------------------------------------------
	my ($timestamp) = @_;
	$year = substr($timestamp,0,4);
	$mon = substr($timestamp,5,2);
	$day = substr($timestamp,8,2);
    return "$year-$mon-$day";	
}

sub fixdate {
# --------------------------------------------------------
	my ($date,$type) = @_;
	
	my (@ary) = split(/\/|-/,$date,3);
	
	if ($type eq 'mdy'){
		#11/1/2007
		return "$ary[2]-$ary[0]-$ary[1]";
	}
}

sub valid_date_sql{
# --------------------------------------------------------
	my ($date)   = $_[0];
	
	my ($year,$mon,$day) = split(/-|\/|:/, $date,3);
	($day =~ /[^0-9]/) and (return 0);
	($year =~ /[^0-9]/) and (return 0);
	($mon =~ /[^0-9]/) and (return 0);	
	$day  = int($day);
	$year = int($year);
	$mon  = int($mon);

	($day == 0 or $year==0 or !$mon) and (return 0);
	
	## Check Months
	if ($mon<1 or $mon>12){
		return 0;
	}
	
	## Load Months
	my (@months) = (0,31,28,31,30,31,30,31,31,30,31,30,31);
	### A?os Viciestos
	($year < 100) and ($year += 2000);
	if ($mon ==2){
		$yy1 = $year/4;
		$yy2 = int($year/4);
		if ($yy1 eq $yy2 and ($mon>29)){
			return 0;
		}elsif ($yy1 eq $yy2){
			++$months[2];
		}
	}
	if ($year <1800 or $year>3000){
		return 0;
	}

	## Check Days
	if ($day>$months[$mon]){
		return 0;
	}
	

	## Date OK
	return 1;

}

sub date_to_sql {
# --------------------------------------------------------

	my (%months) = ("jan" => [1,31], "feb" => [2,28], "mar" => [3,31], "apr" => [4,30], "may" => [5,31], "jun" => [6,30],
                    "jul" => [7,31], "aug" => [8,31], "sep" => [9,30], "oct" => [10,31], "nov" => [11,30], "dec" => [12,31],
			  	"ene" => [1,31], "abr" => [4,30], "ago" => [8,31], "set" => [9,30],"dic" => [12,31]);

	##12-Mar-2002

	## Valid Format    : dd-mm-yyyy,mm-dd-yy,yy-mm-dd,dd-Mmmm-yyyy,Mmmm-dd-yyyy";
	## Valid Languages :English,Spanish";
	## Valid Separator : -,/,:

	my ($day,$mon,$year) = split(/-|\/|:/, $date,3);
	$day = int($day);
	$year = int($year);
	$mon = lc($mon);

	($day == 0 or $year==0 or !$mon) and (return 0);

	($year < 100) and ($year += 2000);
	$yy1 = $year/4;
	$yy2 = int($year/4);
	$mon = lc($mon);

	### A?os Viciestos
	if ($yy1 eq $yy2){
		++$months{'feb'}[1];
	}
	######## Month ####
	if (!$months{$mon}){
		return 0;
	}
	######## Day ####
	if ($day>$months{$mon}[1]){
		
		return 0;
	}
	($day <10) and ($day = "0$day");
	($months{$mon}[0] <10) and ($months{$mon}[0] = "0$months{$mon}[0]");


	return ("$year-$months{$mon}[0]-$day");
}

sub sqldate_plus {
# --------------------------------------------------------
	my ($date,$plus) = @_;
	#GV  08/abr/2008 Modifica: Se actualiza la cadena para incluir el par?metro $date
	$plus = int ($plus);
	(!$plus) and ($plus=1);
	my ($sth) = &Do_SQL("SELECT DATE_ADD('$date', INTERVAL $plus DAY)");

	return substr($sth->fetchrow,0,10);
}

sub datetime_diff{
# --------------------------------------------------------
	my ($datetime1,$datetime2,$fmt) = @_;
	my ($sth) = &Do_SQL("SELECT SUBTIME('$datetime1','$datetime2');");
	my ($r) = $sth->fetchrow;
	my (@ary) = split(/:/, $r);
	if ($fmt eq 'm'){
		return $ary[0]*60+$ary[1]+round($ary[3]/60,2);
	}elsif($fmt eq 's'){
		return $ary[0]*3600+$ary[1]*60+i$ary[3];
	}elsif ($fmt eq 'h'){
		return $ary[0]+round($ary[1]/60+$ary[3]/3660,2);
	}else{
		return $r;
	}
}

sub date_to_unixtime {
# --------------------------------------------------------
	my ($date)   = $_[0];
	my ($year,$mon,$day) = split(/-|\/|:|\//, $date,3);
	$yy1 = $year/4;
	$yy2 = int($year/4);
	$mon = lc($mon);

	######## Days from 1-1 to Month ####
	if ($mon =~ /\d+/ and $mon<= 12){
		my (@months_num) = (0,31,59,90,120,151,181,212,243,273,304,334);
		$num = $months_num[$mon-1];
	}elsif ($mon =~ /\D+/){
		$mon = lc($mon);
		my (%months) = ("jan" => [0,31],"ene" => [0,31],"gen" => [0,31],
				 "feb" => [31,28], "fev" => [31,28],
				 "mar" => [59,31], "m?r" => [59,31],
				 "apr" => [90,30], "abr" => [90,30], "avr" => [90,30],
				 "may" => [120,31], "mai" => [120,31], "mag" => [120,31],
				 "jun" => [151,30], "giu" => [151,30],
      			 "jul" => [181,31], "lug" => [181,31],
      			 "aug" => [212,31], "ago" => [212,31], "ao?" => [212,31],
      			 "sep" => [243,30], "set" => [243,30],
      			 "oct" => [273,31], "okt" => [273,31], "ott" => [273,31],"out" => [273,31],
      			 "nov" => [304,30],
      			 "dec" => [334,31], "dic" => [334,31], "dez" => [334,31],  "d?c" => [334,31] );
		$num = $months{$mon}[0];
	}

	### Valid Days
	if ($yy1 eq $yy2){
		($num>59) and (++$num);
	}

	######## First Day 1-1-2000 #######
	$year -= 2000;
	$num = $day + $num+ ($year * 365.25);
	#$year -= 1970;
	#$num = ($day + $num+ ($year * 365.25))*86400;

	return ($num);
}

sub format_number {
# --------------------------------------------------------
	my ($number, $precision, $trailing_zeroes, $thousands_sep,$decimal_point) = @_;
	# Set defaults and standardize number
	$precision = $sys{'fmt_decimal_digits'}  unless defined $precision;
	$thousands_sep = $sys{'fmt_thousands_sep'}  unless defined $thousands_sep;
	$decimal_point = $sys{'fmt_decimal_point'}  unless $decimal_point;
	$trailing_zeroes = 1 unless defined $trailing_zeroes;

	# Handle negative numbers
	my $sign = $number <=> 0;
	$number = abs($number) if $sign < 0;
	$number = &round($number, $precision); # round off $number

	# Split integer and decimal parts of the number and add commas
	my ($integer, $decimal) = split(/\./, $number, 2);
	$decimal = '' unless defined $decimal;

	# Add trailing 0's if $trailing_zeroes is set.
	$decimal .= '0'x( $precision - length($decimal) )
	if $trailing_zeroes && $precision > length($decimal);

	# Add leading 0's so length($integer) is divisible by 3
	$integer = '0'x(3 - (length($integer) % 3)).$integer;

	# Split $integer into groups of 3 characters and insert commas
	$integer = join($thousands_sep , grep {$_ ne ''} split(/(...)/, $integer));

	# Strip off leading zeroes and/or comma
	$integer =~ s/^0+\Q$thousands_sep\E?//;
	$integer = '0' if $integer eq '';

	# Combine integer and decimal parts and return the result.
	my $result = ((defined $decimal && length $decimal) ?
		  join($decimal_point, $integer, $decimal) :
		  $integer);
	($sign < 0) and ($result = "-$result");

    return  $result;

}

sub round{
# --------------------------------------------------------
    my ($number, $precision) = @_;
    my $sign = $number <=> 0;
    $number = abs($number) if $sign < 0;
    $precision = $sys{'fmt_decimal_digits'} unless defined $precision;
    $precision = 2 unless defined $precision;

    $number    = 0 unless defined $number;
    my $multiplier = (10 ** $precision);
    $number = int(($number * $multiplier) + 0.5) / $multiplier;
    $number = -$number if $sign < 0;
    return $number;
}

sub format_price{
# --------------------------------------------------------
    my ($number, $precision) = @_;
    $precision = $sys{'fmt_curr_decimal_digits'} unless defined $precision;
    $precision = 2 unless defined $precision; # default

    my $sign = $number <=> 0;
    $number = abs($number) if $sign < 0;

    #$number = &format_number($number, $precision,0,$sys{'fmt_curr_thousands_sep'},$sys{'fmt_curr_decimal_digits'}); # format it first
	
		$result = $sys{'fmt_curr_symbol'} . ' ' .&format_number($number,$precision);
		##($number, $precision, $trailing_zeroes, $thousands_sep,$decimal_point)
		#$number = &format_number($number, $precision,0,',',2); # format it first

    # Now we make sure the decimal part has enough zeroes
    #my ($integer, $decimal) = split(/\Q$sys{'fmt_curr_decimal_point'}\E/, $number, 2);
    #$decimal = '0'x$precision unless $decimal;
    #$decimal .= '0'x($precision - length $decimal);

    # Combine it all back together and return it.
    #my $result = ($sys{'fmt_curr_symbol'} . ($precision ? join($sys{'fmt_curr_decimal_point'}, $integer, $decimal) :  $integer));
    my $result_color = ($sign < 0)? "<font color=red>- $result</font>" : $result;
    ($sign < 0) and ($result = "- $result");

    return ($in{'export'})? $result : $result_color;
}

##########################################
## SQL ROUTINES ##
##########################################

sub connect_dbx{
# --------------------------------------------------------
## Create a connection to the database. ##
	if ($DBH) {return}

	my $dsn_host = $cfg{'dbi_host'};
	my $dsn_base = $cfg{'dbi_db'};
	my $dsn_user = $cfg{'dbi_user'};
	my $dsn_pass = $cfg{'dbi_pw'};
	my $dsn = "DBI:mysql:$dsn_base:$dsn_host";

	$DBH = DBIx::Connector->new(
	    $dsn,
	    $dsn_user,
	    $dsn_pass,
	    {   
	    	RaiseError        => 1,
	        #mysql_enable_utf8 => 1,
	    }
	);

	&cgierr("Cannot connect: $DBI::errstr\n") unless $DBH;
	return;
}

sub connect_db_wx{
# --------------------------------------------------------
## Create a connection to the database. ##

	my ($db_selected,$host_selected,$user_selected,$pw_selected)=@_;
	
	my $dsn_host = $host_selected;
	my $dsn_base = $db_selected;
	my $dsn_user = $user_selected;
	my $dsn_pass = $pw_selected;
	my $dsn = "DBI:mysql:$dsn_base:$dsn_host";

	$DBH1 = DBIx::Connector->new(
	    $dsn,
	    $dsn_user,
	    $dsn_pass,
	    {   
	    	RaiseError        => 1,
	        # mysql_enable_utf8 => 1,
	    }
	);

	&cgierr("Cannot connect: $DBI::errstr\n") unless $DBH1;
	return;
}


sub connect_db{
# --------------------------------------------------------
## Create a connection to the database. ##
	
	if($cfg{'dbix'}) { return &connect_dbx(); }
	if ($DBH) {return}
	
	$DBH  = "dbi:mysql:database=$cfg{'dbi_db'};host=$cfg{'dbi_host'};mysql_read_default_file=/etc/mysql/my.cnf";
	$DBH  = DBI->connect_cached($DBH,$cfg{'dbi_user'},$cfg{'dbi_pw'});

	&cgierr("Cannot connect: $DBI::errstr\n") unless $DBH;
	return;
}


sub connect_db_w{
# --------------------------------------------------------
# Forms Involved: 
# Created on: 10/01/09 09:46:54
# Author: MCC C. Gabriel Varela S.
# Description :   
# Parameters :
#Last modified on 15 Aug 2011 17:55:38
#Last modified by: MCC C. Gabriel Varela S. :Condition is changed to unless $DBH1;
#
	if($cfg{'dbix'}) { return &connect_db_wx(@_); }

	my ($db_selected,$host_selected,$user_selected,$pw_selected)=@_;

	$DBH1  = "dbi:mysql:database=$db_selected;host=$host_selected;mysql_read_default_file=/etc/mysql/my.cnf";
	$DBH1  = DBI->connect_cached($DBH1,$user_selected,$pw_selected);

	&cgierr("Cannot connect: $DBI::errstr\n") unless $DBH1;
	return;
}

sub disconnect_db{
# --------------------------------------------------------
	if ($DBH) {
		$DBH->disconnect;
	}
}

sub Do_SQLx{
# --------------------------------------------------------
# Last Modified on: 04/27/09 10:47:06
# Last Modified by: MCC C. Gabriel Varela S: Se modifica para actualizar tablas relacionadas con WH
# Last Modified on: 04/28/09 10:21:42
# Last Modified by: MCC C. Gabriel Varela S: Se hace ahora con archivos.
# Last Modified on: 05/11/09 13:08:45
# Last Modified by: MCC C. Gabriel Varela S: Se adapta multiempresa
# Last Modified on: 05/21/09 10:10:58
# Last Modified by: MCC C. Gabriel Varela S: Se modifica para sincronizar por medio de tabla.
# Last Modified on: 06/02/09 16:33:01
# Last Modified by: MCC C. Gabriel Varela S: Se modifica para contemplar e.
# Last Modified on: 09/02/09 11:47:42
# Last Modified on: 29/06/2017 Fabian Cañaveral Reportes se Pasan a Replicacion.
	use Try::Tiny;

	my ($SQL,$ext) = @_;
	my ($sth,$msg,$sthu);
	my (@lines);

	#Inicia Modificaci?n temporal 05/18/2009
	if ($cfg{'pathcgi_sql'}){
	  use Benchmark;
	  $start = new Benchmark;
  	}

	# strips out the beginning and ending spaces.
	$SQL =~ s/^\s+//;
	$SQL =~ s/\s+$//;
	$SQL =~ s/[\t\r]+//g;


	#########
	######### Iniciamos funciones DBIx
	#########
	my $max_tries = int(rand(5)) + 4;
	my $exec_error; my $tries = 0;
	my $qry_start = new Benchmark if ($SQL =~ /^select/i);
	# my $savePointName = 'transaction-'.int(rand(100000));
	# my $deadLockReturn = 0; 
	# if($SQL =~ /start transaction/i ){
	# 	$inTransaction = 1;
	# }
	# if($SQL =~ /commit|rollback/i ){
	# 	$inTransaction = 0;
	# }
	do{

		++$tries;
   		$exec_error = 0;
   		try{


   			### Override Conection on Reports Query
   			# use Data::Dumper;


   			if($cfg{'use_ext_host_for_repmans'} and $cfg{'use_ext_host_for_repmans'} == 1 and $SQL =~ /^select/i and $in{'cmd'} =~ /^rep/ ){
   				$ext = 1;
   			}

   			#### Detectamos si esta una transacction Activa?
   	# 		if($cfg{'detect_active_transaction'}){
				# if($inTransaction){

				# 	$_query = qq|SAVEPOINT `$savePointName`;|;
				# 	$DBH->run(fixup => sub {
				# 		$sth = $_->prepare($_query);
	   # 					if(!$sth){
				# 			$DBH->disconnect;
				# 			&cgierr("An ERROR occurred $DBI::errstr",120,$@);
				# 		}
				# 		$sth->execute;
				# 		$sth;
				# 	});
				# }
   	# 		}
   			####
   			#### Trying to execute Query
   			####
   			if (!$ext or $ext != 1){

   				#####
   				##### a) Primary Connection
   				#####

   				$DBH->run(fixup => sub {
					$sth = $_->prepare($SQL);

   					if(!$sth){

   						#####
   						##### Errors in Query?
   						#####
						$DBH->disconnect;
						&cgierr("An ERROR occurred $DBI::errstr",120,$@);

					}
					$sth->execute;
					$sth;

				});

   			}elsif($ext == 1){

   				#####
   				##### b) Secondary Connection
   				#####
   				if(!$DBH1){
   					&connect_db_w(
   						$cfg{'dbi_db_rep'},
   						$cfg{'dbi_host_rep'},
   						$cfg{'dbi_user_rep'},
   						$cfg{'dbi_pw_rep'}
   					);
   				}
	   			$DBH1->run(fixup => sub {
					$sth = $_->prepare($SQL);

					if($@){

						#####
   						##### Errors in Query?
   						#####
						$DBH1->disconnect;
						&cgierr("An ERROR occurred $DBI::errstr",120,$@)
					}

					$sth->execute;
					$sth;

				});
   			}

   		}catch{

   			####
   			#### Execution Error?
   			####
       		$exec_error = &dbi_err_handler($DBI::err, $DBI::errstr);
       		$this_str_err .= "Try: ". $tries ."\nExError: ". $exec_error ."\nDBIErrno: " . $DBI::err . "\nDBIErrstr:\n" . $DBI::errstr ."\n\n";

       		if( $exec_error and $tries < $max_tries and $tries % 2 == 0){
       			###
       			### Deadlock sleep
       			###
     #   			if($inTransaction){
	    #    			$_query = qq|ROLLBACK TO SAVEPOINT `$savePointName`;|;
					# $DBH->run(fixup => sub {
					# 	$sth = $_->prepare($_query);
	   	# 				if(!$sth){
					# 		$DBH->disconnect;
					# 		&cgierr("An ERROR occurred $DBI::errstr",120,$@);
					# 	}
					# 	$sth->execute;
					# 	$sth;
					# });
				$save_query = &filter_values($SQL);
				$_query = qq|INSERT INTO sl_deadlock_log (ID_deadlock_log,query,date_time)
				VALUES (NULL,'$save_query',now());|;
				$DBH->run(fixup => sub {
					$sth = $_->prepare($_query);
   					if(!$sth){
						$DBH->disconnect;
						&cgierr("An ERROR occurred $DBI::errstr",120,$@);
					}
					$sth->execute;
					$sth;
				});
				cgierr('Error in transaction');
					# $deadLockReturn++;
     #   			}

       			# sleep 3;
       		}elsif ( (!$exec_error or $tries == $max_tries) and $DBI::err == 1062){
       			###
       			### Duplicate entry for key PRIMARY
       			###
				$msg = $DBI::errstr;
				return '';
			}elsif ( (!$exec_error or $tries == $max_tries) and $DBI::errstr){
				###
       			### Any Error
       			###
       			if ($cfg{'debug_cgierr'} and (!$exec_error or $tries == $max_tries) ){
					&send_text_mail($cfg{'from_email_info'},"rbarcenas\@inovaus.com","DoSQL ERR", "SQL\n". $SQL ."\n\nMaxtries: ". $max_tries ."\n" . $this_str_err);
				}
       			
				&cgierr($SQL,$DBI::err,$DBI::errstr);
			}

   		}

	}while($exec_error and $tries <= $max_tries);
	my $qry_end = new Benchmark if ($SQL =~ /^select/i);
	
	# if($deadLockReturn eq '2'){
	# 	$queryError = 1;
	# }

	####
	#### write $SQL query to a text file
	####
	if ($cfg{'pathcgi_sql'}){
	    my ($explain);
	    $end = new Benchmark;
	    if ($SQL =~ /^select/i){
	    	if ($ext){
		    	$sth2 = $DBH1->prepare("EXPLAIN $SQL");
		    }else{
				$sth2 = $DBH->prepare("EXPLAIN $SQL");
			}
		    $sth2->execute;
		    if (!$DBI::errstr){
		    	$explain=join("|",);
		    }
	    }
	    $SQL=~s/\n/ /g;
	    if (open(my $auth, ">>", $cfg{'pathcgi_sql'})){
		    print $auth "$in{'e'}\t$in{'cmd'}\tTime taken was ". timestr(timediff($end, $start), 'all')." seconds\t$explain\t$SQL\n";
	    }
	}


	####
	#### Post Execution
	####
	if(!$exec_error){

		####
		#### Memcached Key Deletion
		####
		if($SQL =~ /update [^admin_]/i){ 
			#/update\s+(\w+)\s/
			#$in{'db'] = $1;
			#$db =~ s/^[az]{2}_//i;
			#if($SQL =~ /ID_$db\s*=\s*['|"]{0,1}\d{1,}['|"]{0,1})/)

			&memcached_delete('e' . $in{'e'} . '_' .$in{'db'} . '_' . $in{lc($db_cols[0])}, $SQL); 
		}

		####
		#### Inventory Fingerprint
		####
		if($cfg{'track_inventory'} and $SQL=~/(update|insert|delete){1,1}.*(sl_warehouses_location\s{1,1}|sl_skus_cost\s{1,1}){1,1}/i){
			if (open(my $upd, ">>", $cfg{'path_upfiles'}."e". $in{'e'} ."/track_inventory/".&get_sql_date().".sql")) {
				#Escribir en archivo actual.
				$towrite=$SQL;
				$towrite=~s/\n/ /g;
				print $upd "$towrite\n";
			}
		}

	}

	####
	#### Inventory Fingerprint
	####
	if(!$exec_error and $cfg{'track_inventory'} and $SQL=~/(update|insert|delete){1,1}.*(sl_warehouses_location\s{1,1}|sl_skus_cost\s{1,1}){1,1}/i){
		if (open(my $upd, ">>", $cfg{'path_upfiles'}."e". $in{'e'} ."/track_inventory/".&get_sql_date().".sql")) {
			#Escribir en archivo actual.
			$towrite=$SQL;
			$towrite=~s/\n/ /g;
			print $upd "$towrite\n";
		}
	}
	
	return $sth;
}


sub Do_mSQLx{
# --------------------------------------------------------
## Executes the SQL command and then    ##
## returns to the calling area of the   ##
## program.                             ##
# Last Modified by RB on 09/30/2010: Se guarda el fingerprint de los queries de inventario

	use Try::Tiny;

	my ($SQL) = @_;
	my ($sth,$msg,$i,@lines);
	my (@lines);
	@lines = split(/;/, $SQL);
	my $i=0;

	MQUERY:for (my $i=0; $i <= $#lines; $i++) {

		####
		#### strips out the beginning and ending spaces.
		####
		$lines[$i] =~ s/^\s+//;
		$lines[$i] =~ s/\s+$//;
		$lines[$i] =~ s/\n|\r//;
		$lines[$i] =~ s/[\t\r]+//g;
		$SQL = $lines[$i];

		
		#$sth->execute;
		my $max_tries = int(rand(10)) + 1;
		my $exec_error; my $tries = 1;
		do{
   
   			++$tries;
	   		$exec_error = 0;
	   		try{

	   			$DBH->run(fixup => sub {
					$sth = $_->prepare($SQL);

   					if($@){

   						#####
   						##### Errors in Query?
   						#####
						$DBH->disconnect;
						&cgierr("An ERROR occurred $DBI::errstr",120,$@);

					}

					$sth->execute;
					$sth;

				});

	   		}catch{

	   			####
	   			#### Execution Error?
	   			####
	       		$exec_error = &dbi_err_handler($DBI::err, $DBI::errstr);
	       		
	       		if( $exec_error and $tries % 4 == 0){
	       			###
	       			### Deadlock sleep
	       			###
	       			sleep 1;
	       		}elsif ($DBI::err == 1062){
	       			###
	       			### Duplicate entry for key PRIMARY
	       			###
					$msg = $DBI::errstr;
					return '';
				}elsif ($DBI::errstr){
					###
	       			### Any Error
	       			###
					&cgierr($SQL,$DBI::err,$DBI::errstr);
				}

	   		}

		}while($exec_error and $tries <= $max_tries);

	
		####
		#### Post Execution
		####
		if(!$exec_error){

			####
			#### Memcached Key Deletion
			####
			if($SQL =~ /update [^admin_]/i){
				&memcached_delete('e' . $in{'e'} . '_' .$in{'db'} . '_' . $in{lc($db_cols[0])}, $SQL); 
			}

			####
			#### Inventory Fingerprint
			####
			if($cfg{'track_inventory'} and $SQL=~/(update|insert|delete){1,1}.*(sl_warehouses_location\s{1,1}|sl_skus_cost\s{1,1}){1,1}/i){
				if (open(my $upd, ">>", $cfg{'path_upfiles'}."e". $in{'e'} ."/track_inventory/".&get_sql_date().".sql")) {
					#Escribir en archivo actual.
					$towrite=$SQL;
					$towrite=~s/\n/ /g;
					print $upd "$towrite\n";
				}
			}

		}

	}

	return $sth;
}


sub Do_SQL{
# --------------------------------------------------------
# Last Modified on: 04/27/09 10:47:06
# Last Modified by: MCC C. Gabriel Varela S: Se modifica para actualizar tablas relacionadas con WH
# Last Modified on: 04/28/09 10:21:42
# Last Modified by: MCC C. Gabriel Varela S: Se hace ahora con archivos.
# Last Modified on: 05/11/09 13:08:45
# Last Modified by: MCC C. Gabriel Varela S: Se adapta multiempresa
# Last Modified on: 05/21/09 10:10:58
# Last Modified by: MCC C. Gabriel Varela S: Se modifica para sincronizar por medio de tabla.
# Last Modified on: 06/02/09 16:33:01
# Last Modified by: MCC C. Gabriel Varela S: Se modifica para contemplar e.
# Last Modified on: 09/02/09 11:47:42
	if($cfg{'dbix'}) { return &Do_SQLx(@_); }

	use Try::Tiny;

	my ($SQL,$ext) = @_;
	my ($sth,$msg,$sthu);
	my (@lines);

	if ($cfg{'pathcgi_sql'}){
	  use Benchmark;
	  $start = new Benchmark;
 	}

	# strips out the beginning and ending spaces.
	$SQL =~ s/^\s+//;
	$SQL =~ s/\s+$//;
	$SQL =~ s/[\t\r]+//g;

	if ($ext){
		eval{
			$sth = $DBH1->prepare($SQL);
		}; # End of eval
	}else{
		eval{
			$sth = $DBH->prepare($SQL);
		}; # End of eval
	}
	

	####
	#### Check for errors.
	####
	if($@){
		if ($ext){
			$DBH1->disconnect;
		}else{
			$DBH->disconnect;
		}
		&cgierr("An ERROR occurred $DBI::errstr",120,$@)

	} else {
		
		#&cgierr($cfg{'path_upfiles'}."track_inventory/e". $in{'e'} ."/".&get_sql_date().".sql");
		my $qry_start = new Benchmark if ($SQL =~ /^select/i);

		my $max_tries = int(rand(10)) + 11;
		my $exec_error; my $tries = 1;
		do{
   
   			++$tries;
	   		$exec_error = 0;
	   		try{

	   			####
	   			#### Trying to execute Query
	   			####
	   			$sth->execute;

	   		}catch{

	   			####
	   			#### Execution Error?
	   			####
	       		$exec_error = &dbi_err_handler($DBI::err, $DBI::errstr);
	       		if( $exec_error and $tries % 4 == 0){

	       			sleep 1;

	       		}

	   		}

		}while($exec_error and $tries <= $max_tries);

		my $qry_end = new Benchmark if ($SQL =~ /^select/i);


		####
		#### write $SQL query to a text file
		####
		if ($cfg{'pathcgi_sql'}){
		    my ($explain);
		    $end = new Benchmark;
		    if ($SQL =~ /^select/i){
		    	if ($ext){
			    	$sth2 = $DBH1->prepare("EXPLAIN $SQL");
			    }else{
					$sth2 = $DBH->prepare("EXPLAIN $SQL");
				}
			    $sth2->execute;
			    if (!$DBI::errstr){
			    	$explain=join("|",);
			    }
		    }
		    $SQL=~s/\n/ /g;
		    if (open(my $auth, ">>", $cfg{'pathcgi_sql'})){
			    print $auth "$in{'e'}\t$in{'cmd'}\tTime taken was ". timestr(timediff($end, $start), 'all')." seconds\t$explain\t$SQL\n";
		    }
		}
		
		####
		#### Post Execution
		####
		if(!$exec_error){

			####
			#### Memcached Key Deletion
			####
			if($SQL =~ /update [^admin_]/i){
				&memcached_delete('e' . $in{'e'} . '_' .$in{'db'} . '_' . $in{lc($db_cols[0])}); 
			}

			####
			#### Inventory Fingerprint
			####
			if($cfg{'track_inventory'} and $SQL=~/(update|insert|delete){1,1}.*(sl_warehouses_location\s{1,1}|sl_skus_cost\s{1,1}){1,1}/i){
				if (open(my $upd, ">>", $cfg{'path_upfiles'}."e". $in{'e'} ."/track_inventory/".&get_sql_date().".sql")) {
					#Escribir en archivo actual.
					$towrite=$SQL;
					$towrite=~s/\n/ /g;
					print $upd "$towrite\n";
				}
			}

		}

	} # End of if..else ERRORS

	if ($DBI::err == 1062){

		$msg = $DBI::errstr;
		return '';

	}elsif ($DBI::errstr){

		&cgierr($SQL,$DBI::err,$DBI::errstr);

	}
	
	return $sth;
}


sub Do_mSQL{
# --------------------------------------------------------
## Executes the SQL command and then    ##
## returns to the calling area of the   ##
## program.                             ##
# Last Modified by RB on 09/30/2010: Se guarda el fingerprint de los queries de inventario

	if($cfg{'dbix'}) { return &Do_mSQLx(@_); }

	use Try::Tiny;

	my ($SQL) = @_;
	my ($sth,$msg,$i,@lines);
	my (@lines);
	@lines = split(/;/, $SQL);
	my $i=0;

	MQUERY:for (my $i=0; $i <= $#lines; $i++) {

		####
		#### strips out the beginning and ending spaces.
		####
		$lines[$i] =~ s/^\s+//;
		$lines[$i] =~ s/\s+$//;
		$lines[$i] =~ s/\n|\r//;
		$lines[$i] =~ s/[\t\r]+//g;
		$SQL = $lines[$i];

		eval{

			$sth = $DBH->prepare($SQL);

		}; # End of eval

		####
		#### Check for errors.
		####
		if($@){

			$DBH->disconnect;
			&cgierr("An ERROR occurred $DBI::errstr",120,$@)

		} else {

			my $max_tries = int(rand(10)) + 11;
			my $exec_error; my $tries = 1;
			do{
	   
	   			++$tries;
		   		$exec_error = 0;
		   		try{

		   			####
		   			#### Trying to execute Query
		   			####
		   			$sth->execute;

		   		}catch{

		   			####
		   			#### Execution Error?
		   			####
		       		$exec_error = &dbi_err_handler($DBI::err, $DBI::errstr);
		       		if( $exec_error and $tries % 3 == 0){

		       			sleep 1;

		       		}

		   		}

			}while($exec_error and $tries <= $max_tries);

			
			####
			#### Post Execution
			####
			if(!$exec_error){

				####
				#### Memcached Key Deletion
				####
				if($SQL =~ /update [^admin_]/i){
					&memcached_delete('e' . $in{'e'} . '_' .$in{'db'} . '_' . $in{lc($db_cols[0])}, $SQL); 
				}

				####
				#### Inventory Fingerprint
				####
				if($cfg{'track_inventory'} and $SQL=~/(update|insert|delete){1,1}.*(sl_warehouses_location\s{1,1}|sl_skus_cost\s{1,1}){1,1}/i){
					if (open(my $upd, ">>", $cfg{'path_upfiles'}."e". $in{'e'} ."/track_inventory/".&get_sql_date().".sql")) {
						#Escribir en archivo actual.
						$towrite=$SQL;
						$towrite=~s/\n/ /g;
						print $upd "$towrite\n";
					}
				}

			}
			
		} # End of if..else ERROR


		if ($DBI::err == 1062){
			$msg = $DBI::errstr;
			return '';
		}elsif ($DBI::errstr){
			&cgierr($SQL,$DBI::err,$DBI::errstr);
		}
	}
	return $sth;
}


sub Do_selectinsert{
# --------------------------------------------------------
	my ($table_name, $where, $order, $limit, %overwite) = @_;
	my (%tmp,$key,$id_key,$ins_id);

	### GEt Primary Key
	my ($sth) = &Do_SQL("describe $table_name;");
	COLS: while (@ary = $sth->fetchrow_array() ) {
		if ($ary[5] eq 'auto_increment' or $ary[3] eq 'PRI'){
			$id_key = lc($ary[0]);
		}
	}
	## To cols Name in Lowercase
	foreach my $key (keys %overwite){
		$overwite{lc($key)} = $overwite{$key};
	}
	
	my ($sth) = &Do_SQL("SELECT * FROM $table_name WHERE $where $order $limit");
	while ($rec = $sth->fetchrow_hashref){
		
		%tmp = ();  ## Clear Buffer
		## To cols Name in Lowercase and Skip Autoincremental
		foreach my $key (keys %{$rec}){
			$tmp{lc($key)} = $rec->{$key} if (lc($key) ne $id_key);
		}
		## Replace Values
		foreach my $key (keys %overwite){
			$tmp{$key} = $overwite{$key};
		}
		
		## build Query
		my ($query);
		foreach my $key (keys %tmp){
			if ($tmp{$key} =~ /CURDATE|CURTIME|NOW|SELECT|CONCAT/i){
				$query .= " $key=$tmp{$key},";
			}else{
				$query .= " $key='".&filter_values($tmp{$key})."',";
			}
		}
		chop($query);
		my ($sth2) = &Do_SQL("INSERT INTO $table_name SET $query ");
		$ins_id  .= $sth2->{'mysql_insertid'}.',';
	}
	chop($ins_id );
	return $ins_id;
}


#############################################################################
#############################################################################
#   Function: dbi_err_handler
#
#       Es: Evalua errores devueltos por mysql para saber si se debe volver a ejecutar el query
#       En: 
#
#
#    Created on: 07/21/2014 15:37:44
#
#    Author: _RB_
#
#    Modifications:
#
#
#   Parameters:
#
#		- $keypoint,
#		- $cond1,
#		- $cond2,
#		- $cond3,
#		- $type,
#		-$credebit
#
#  Returns:
#
#      - 
#
#   See Also:
#
#		<load_accounts>
#
#
sub dbi_err_handler {
#############################################################################
#############################################################################

    my($errno, $errmsg) = @_;
    my $retval = 0;
    my @ary_errno = ('1213','1205'); ## Array of errores to look for

    LERROR:for(0..$#ary_errno){

    	my $this_errno = $ary_errno[$_];
	    if($errno eq $this_errno){
	    
	       $caught = 1;
	       $retval = 1; # we'll check this value and sleep/re-execute if necessary
	       last LERROR;
	    
	    }

	}

    return $retval;
}


sub filter_values{
# --------------------------------------------------------
### Filter - Gets rid of         ###
### characters that screw up the ###
### program.                     ###
	$line = shift;
	$type = shift;

	# switch ($type) {
	# 	case "number" { $line =~ s/[^\d]//g; }
	# 	case "text" { $line =~ s/[^\w]//gi; }
	# 	else {
			$line =~ s/\\'/'/g;
			$line =~ s/\'/\\\'/g;
			$line =~ s/\n/\\n/g;
			$line =~ s/\r/\\r/g;
			$line =~ s/"/\\"/g;
			$line =~ s/\\$//g;
	# 	}
	# }
	return $line;
}

sub urlencode {
# --------------------------------------------------------
# Escapes a string to make it suitable for printing as a URL.
#
    my($toencode) = shift;
    $toencode =~ s/([^a-zA-Z0-9_\-.])/uc sprintf("%%%02x",ord($1))/eg;
    return $toencode;
}

sub encode_html {
# --------------------------------------------------------
	my ($input) = @_;
	$input =~ s/</&lt;/g;
	$input =~ s/>/&gt;/g;
	$input =~ s/&nbsp;/&amp;nbsp;/g;
	#$input =~ s/&nbsp/&amp;nbsp;/g;
	$input =~ s/\"/&quot;/g;
	return $input;
}





sub build_form {
# --------------------------------------------------------
	my ($fname) = @_;
	my ($output);	
	if ($fname =~ /view\.html/ or $fname =~ /print\.html/){
		$va{'form_view'}=1;
		### Deberia poder sacarse de Un Template la "base"
		$title = $sys{'db_'.$in{'cmd'}.'_title'};
		$title = $in{'cmd'} if (!$title);
		$dbfields = $sys{'db_'.$in{'cmd'}.'_viewlist'};
		$dbfields = join(",", @db_cols) if (!$dbfields);
		$output .= &build_custom_viewfields ($title,$dbfields);
	}elsif($in{'modify'}){
		$va{'form_edit'}=1;
		### Deberia poder sacarse de Un Template la "base"
		$title = $sys{'db_'.$in{'cmd'}.'_title'};
		$title = $in{'cmd'} if (!$title);
		#$dbfields = $sys{'db_'.$in{'cmd'}.'_viewlist'};
		$dbfields = join(",", @db_cols[1..$#db_cols]);
		$output .= &build_custom_formfields ($title,$dbfields);	
	}else{
		$va{'form_add'}=1;
		### Deberia poder sacarse de Un Template la "base"
		$title = $sys{'db_'.$in{'cmd'}.'_title'};
		$title = $in{'cmd'} if (!$title);
		$dbfields = $sys{'db_'.$in{'cmd'}.'_viewlist'};
		$dbfields = join(",", @db_cols) if (!$dbfields);
		$output .= &build_custom_formfields ($title,$dbfields);
	}
	##%error = %va;
	##&cgierr($fname.$dbfields);
	return $output;
}

sub load_name {
# --------------------------------------------------------
	my ($db,$id_name,$id_value,$field) = @_;
	&connect_db;
	($id_value ne 'NOW()' or $id_value ne 'CURDATE()') and ($id_value="'$id_value'");
	my ($sth) = &Do_SQL("SELECT $field FROM $db WHERE $id_name=$id_value;");
	return $sth->fetchrow();
}

sub load_db_names {
# --------------------------------------------------------
	my ($db,$id_name,$id_value,$str_out) = @_;
	my ($key,$output);
	&connect_db;
	my ($sth) = &Do_SQL("SELECT * FROM $db WHERE $id_name='$id_value';");
	my ($rec) = $sth->fetchrow_hashref();
	if ($rec->{$id_name}>0){
		foreach my $key (keys %{$rec}){
			$str_out =~ s/\[$key\]/$rec->{$key}/gi;
		}
		return $str_out;
	}else{
		return '';
	}
}

sub sum_records {
# --------------------------------------------------------
	my ($tbl,$where,$field) = @_;
	my ($sth) = &Do_SQL("SELECT SUM($field) FROM $tbl WHERE $where;");
	return &format_number($sth->fetchrow);
}

sub count_records {
# --------------------------------------------------------
	my ($tbl,$where,$field) = @_;
	my ($sth) = &Do_SQL("SELECT COUNT($field) FROM $tbl WHERE $where;");
	return &format_number($sth->fetchrow);
}

sub build_link {
# --------------------------------------------------------
	my ($db,$id_name,$id_value) = @_;
	my ($key,$cmd);
	foreach my $key (keys %sys){
		if ($sys{$key} eq $db and $key =~ /db_(.*)/){
			$cmd = $1;
		} 
	}
	return $script_url."?cmd=$cmd&view=$id_value";
	#foreach $key (keys %sys){
	#	if ($sys{$key} eq $db and $key =~ /db_(.*)/){
	#		$cmd = $1;
	#	} 
	#}
	#if ($cmd and $in{'sit_app'} =~ /(.*):/){
	#	return $cfg{'path_ns_cgi'}.$cfg{'path_ns_cgi_'.$1.'_dbman'}."?cmd=$cmd&view=$id_value";
	#}else{
	#	return '#';
	#}
}

sub load_dbw_names {
# --------------------------------------------------------
	my ($db,$where,$str_out) = @_;
	my ($key,$output);
	&connect_db;
	my ($sth) = &Do_SQL("SELECT * FROM $db WHERE $where;");
	my ($rec) = $sth->fetchrow_hashref();
	foreach my $key (keys %{$rec}){
		$str_out =~ s/\[$key\]/$rec->{$key}/gi;
	}
	return $str_out ;
}





sub load_cfg {
# --------------------------------------------------------
#Last modified on 15 Aug 2011 16:02:55
#Last modified by: MCC C. Gabriel Varela S. : second_conn is considered
	my ($db) = @_;

	
	my (@ary);
	@db_cols =();
	my $conn_type=0;
	$conn_type=0;
	&connect_db;
	
	#my ($sth) = &Do_SQL("SHOW TABLES LIKE '$db'",$conn_type);
	#@ary  = $sth->fetchrow_array();
	#if (!$ary[0]){
	#	return;
	#}

	###### Check if Table Exists
	return if !table_exists($db);


	###### Load Table Properties
	my ($sth) = &Do_SQL("describe $db;",$conn_type);
	
	while (@ary = $sth->fetchrow_array() ) {
		push(@db_cols,$ary[0]);
		$ary[0] = lc($ary[0]);
		if ($ary[5] eq 'auto_increment' or $ary[3] eq 'PRI'){
			$db_valid_types{$ary[0]} = "PRIMARY";
			$ary[2] = "YES";
			$db_valid_length{$ary[0]}=20;
		}elsif ($ary[1] =~ /enum\((.*)/i){
			$db_select_fields{$ary[0]} = $1;
			$db_select_fields{$ary[0]} =~ s/','/,/g;
			if ($ary[0] =~ /Status/i or length($db_select_fields{$ary[0]})<30){
				$db_valid_types{$ary[0]} = "radio";
				$db_select_fields{$ary[0]} = substr($db_select_fields{$ary[0]},1,-2);
			}else{
				$db_valid_types{$ary[0]} = "selection";
				$db_select_fields{$ary[0]} = substr($db_select_fields{$ary[0]},1,-2);
			}
		}elsif ($ary[1] =~ /set\((.*)/i){
			$db_select_fields{$ary[0]} = $1;
			$db_select_fields{$ary[0]} =~ s/','/,/g;
			$db_valid_types{$ary[0]} = "checkbox";
			$db_select_fields{$ary[0]} = substr($db_select_fields{$ary[0]},1,-2);
		}elsif ($ary[1] =~ /varchar\((\d+)\)/i){
			
			if ($ary[4] eq 'email'){
				$db_valid_types{$ary[0]} = "email";
			}elsif ($ary[4] eq 'image'){
				($db_valid_types{$ary[0]} = "image");
			}else{
				($db_valid_types{$ary[0]} = "alpha");
			}
			$db_valid_length{$ary[0]}=$1;
			$db_valid_length{$ary[0]}=80 if($db_valid_length{$ary[0]}>80);
		}elsif ($ary[1] eq 'text'){
			$db_valid_types{$ary[0]} = "text";
		}elsif ($ary[1] eq 'date'){
			$db_valid_types{$ary[0]} = "date";
		}elsif ($ary[1] =~ /^int/ or $ary[1] =~ /^tinyint/){
			$db_valid_types{$ary[0]} = "numeric";
			$db_valid_length{$ary[0]}=20;
		}elsif ($ary[1] =~ /^decimal\(([^)]+)\)/){
			$db_valid_types{$ary[0]} = "currency";
			$db_valid_length{$ary[0]}=20;
		}else{
			$db_valid_types{$ary[0]} = "alpha";
		}
		($sys{'db_'.$db.'.'.$ary[0]}) and ($db_valid_types{$ary[0]}=$sys{'db_'.$db.'.'.$ary[0]});
		(!$ary[2] or $ary[2] eq 'NO') and ($db_not_null{$ary[0]} = 1);
	}
}

sub query {
# --------------------------------------------------------
# Last Modified on: 09/11/08 15:49:42
# Last Modified by: MCC C. Gabriel Varela S: Se hace lo necesario para que cuando se tenga una variable in del tipo neg_[variable] se tome !=
# Last Modified RB: 02/23/09  17:28:46 - Se agrego $id_table para hacer busqueda por varios id's
#Last modified on 15 Aug 2011 12:52:08
#Last modified by: MCC C. Gabriel Varela S. : second_conn is considered

	my ($db,$queryonly)=@_;
	my ($i, $column, $maxhits, $numhits, $nh, $first , @hits, $value,
	    $query, $condtype,$sort_order,@aux,$sth,$xquery);
	
	if ($in{'keyword'}) {
		for my $i(0..$#db_cols){
			$column = lc($db_cols[$i]);
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
		
		($in{'id_table'}) and ($in{lc($db_cols[0])} = $in{'id_table'});
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
					$xquery = '';
					for (0..$#aux){
						($db_valid_types{$column} eq 'date') ?
							($value = &date_to_sql($aux[$_])):
							($value = &filter_values($aux[$_]));
						($in{'sx'} or $db_valid_types{$column} eq 'date')?
							($xquery .= "$db_cols[$i] = '$value'  OR "):
							($xquery .= "$db_cols[$i] like '%$value%'  OR ");
					}
					$query .= "(" . substr($xquery,0,-4) . " ) $condtype " unless (!$xquery);

				}else{
					if ($db_valid_types{$column} eq 'date' and $value eq 'today'){
						$query .= "$db_cols[$i] = CURDATE() $condtype ";
					}elsif($db_valid_types{$column} eq 'date' and $value eq 'thisweek'){
						$query .= "WEEK($db_cols[$i]) = WEEK(CURDATE()) $condtype ";
					}elsif($db_valid_types{$column} eq 'date' and $value eq 'thismonth'){
						$query .= "MONTH($db_cols[$i]) = MONTH(CURDATE()) $condtype ";
					}elsif($db_valid_types{$column} eq 'date' and $value eq 'thisyear'){	
						$query .= "YEAR($db_cols[$i]) = YEAR(CURDATE()) $condtype ";
					}elsif($value eq 'NULL'){
						$query .= "ISNULL($db_cols[$i]) $condtype ";						
					}elsif($in{'sx'} or $db_valid_types{$column} eq 'date'){
						$query .= "$db_cols[$i]  = '$value' $condtype ";
					}else{
						my $tmp_column = uc($db_valid_types{$column});
						if ($tmp_column eq 'PRIMARY' or $tmp_column eq 'NUMERIC'){
							$query .= "$db_cols[$i] = '$value' $condtype ";
						}else{
							$query .= "$db_cols[$i] like '%$value%' $condtype ";
						}
					}
				}
			}
			if($in{'neg_'.$column} ne ''){
				$query .= "$db_cols[$i] != '$value'  $condtype ";
			}
			#-Se agrega una condici?n and para verificar si el campo contiene 2 limitantes. En caso de tenerlas, se utilizar? la condici?n between o del tipo (campo>=valor and campo<=valor)
			#-Se cambian los signos < y > por <= y >= respectivamente
			#GV Inicia 16may2008
			if (($in{'from_'.$column} !~ /^\s*$/)&& ($in{'to_'.$column} !~ /^\s*$/)){  #Contiene los 2 delimitadores
				$in{'from_'.$column} =~ s/^\s+//g;
				$in{'from_'.$column} =~ s/\s+$//g;
				$in{'to_'.$column} =~ s/^\s+//g;
				$in{'to_'.$column} =~ s/\s+$//g;
				$valuef = &filter_values($in{'from_'.$column});
				$valuet = &filter_values($in{'to_'.$column});
				### From To Fields
				$query .= "$db_cols[$i] between '$valuef' and '$valuet'  $condtype ";
			}else{
				if ($in{'from_'.$column} !~ /^\s*$/) {
					$in{'from_'.$column} =~ s/^\s+//g;
					$in{'from_'.$column} =~ s/\s+$//g;
					$value = &filter_values($in{'from_'.$column});
					### From To Fields
					if ($db_valid_types{$column} eq 'date' and $value eq 'today'){
						$query .= "$db_cols[$i] >= CURDATE() $condtype ";
					}elsif($db_valid_types{$column} eq 'date' and $value eq 'thisweek'){
						$query .= "WEEK($db_cols[$i]) >= WEEK(CURDATE()) $condtype ";
					}elsif($db_valid_types{$column} eq 'date' and $value eq 'thismonth'){
						$query .= "MONTH($db_cols[$i]) >= MONTH(CURDATE()) $condtype ";
					}elsif($db_valid_types{$column} eq 'date' and $value eq 'thisyear'){	
						$query .= "YEAR($db_cols[$i]) >= YEAR(CURDATE()) $condtype ";
					}elsif($in{'sx'} or $db_valid_types{$column} eq 'date'){
						$query .= "$db_cols[$i]  >= '$value' $condtype ";
					}else{
						$query .= "$db_cols[$i] >= '$value'  $condtype ";
					}
				}
				if ($in{'to_'.$column} !~ /^\s*$/) {
					$in{'to_'.$column} =~ s/^\s+//g;
					$in{'to_'.$column} =~ s/\s+$//g;
					$value = &filter_values($in{'to_'.$column});
					### From To Fields
					if ($db_valid_types{$column} eq 'date' and $value eq 'today'){
						$query .= "$db_cols[$i] <= CURDATE() $condtype ";
					}elsif($db_valid_types{$column} eq 'date' and $in{$column} eq 'thisweek'){
						$query .= "WEEK($db_cols[$i]) <= WEEK(CURDATE()) $condtype ";
					}elsif($db_valid_types{$column} eq 'date' and $in{$column} eq 'thismonth'){
						$query .= "MONTH($db_cols[$i]) <= MONTH(CURDATE()) $condtype ";
					}elsif($db_valid_types{$column} eq 'date' and $in{$column} eq 'thisyear'){	
						$query .= "YEAR($db_cols[$i]) <= YEAR(CURDATE()) $condtype ";
					}elsif($in{'sx'} or $db_valid_types{$column} eq 'date'){
						$query .= "$db_cols[$i]  <= '$value' $condtype ";
					}else{
						$query .= "$db_cols[$i] <= '$value'  $condtype ";
					}
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
	#### Search Type
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
	#### only_my_records=1
	#### Show only Record for the logged user
	####
	
	## Se agrega restriccion basada a Arbol de Agentes, Supervisores y Coordinadores
	$custom_id_admin_users = &get_call_center_agents_list();

	if ($in{'only_my_records'}){
		$query = ($query)? "($query) AND ID_admin_users = ".$usr{'id_admin_users'}." ":"ID_admin_users = ".$usr{'id_admin_users'}." ";
	}elsif($custom_id_admin_users ne ''){
		$query = ($query)? "($query) AND ID_admin_users IN (".$custom_id_admin_users.") ":"ID_admin_users IN (".$custom_id_admin_users.") ";
	}

	#####
	##### Se agrega reestriccion para mostrar solo Orders de Canales de Venta que el usuario tenga asignados.
	#####
	if ($in{'only_records_by_salesorigins'} and $in{'only_records_by_salesorigins'}){
		$query .= ($query)? " AND sl_orders.ID_salesorigins IN ($in{'only_records_by_salesorigins'}) ":" sl_orders.ID_salesorigins IN ($in{'only_records_by_salesorigins'}) ";
	}

	if ($queryonly){
		return $query;
	}

	### Nothing to Search
	if (!$query and ($in{lc($db_cols[0])} ne "*" and !$in{'listall'})){
		#return (0,'');
	}elsif ($query){
		$query = "WHERE $query";
	}
	$in{'nh'} ? ($nh = $in{'nh'}) : ($nh = 1);
	$numhits = 0;

	### sort Records ###
	#(exists($in{'sb'}) and $db_cols[$in{'sb'}]) and ($sort_order = "ORDER BY $db_cols[$in{'sb'}] $in{'so'}");
	if (exists($in{'sb'})) {
		#&cgierr("$in{'sb'}");
		if ($db_valid_types{$in{'sb'}}){
			$sort_order = "ORDER BY $in{'sb'} $in{'so'}";
		}elsif( $db_cols[$in{'sb'}]){
			$sort_order = "ORDER BY $db_cols[$in{'sb'}] $in{'so'}";
		}
	}
	
	
	my $conn_type=0;
	if($in{'second_conn'}){
# 		&connect_db_w($cfg{'dbi_db_pbx'},$cfg{'dbi_host_pbx'},$cfg{'dbi_user_pbx'},$cfg{'dbi_pw_pbx'});
		$conn_type=1;
	}else{
		$conn_type=0;
# 		&connect_db;
	}
	### Count Records ###
	my ($sth) = &Do_SQL("SELECT COUNT(*) FROM $db $query;",$conn_type);
	$numhits = $sth->fetchrow();
	
	if ($numhits == 0){
		return (0,'');
	}
	$first = ($usr{'pref_maxh'} * ($nh - 1));
	$sth = &Do_SQL("SELECT * FROM $db $query $sort_order LIMIT $first,$usr{'pref_maxh'}",$conn_type);
	while ($rec = $sth->fetchrow_hashref){
		foreach my $column (@db_cols) {
			push(@hits, $rec->{$column});
		}
	}
	return ($numhits, @hits);
}

sub querydb2 {
# --------------------------------------------------------
	my ($db1,$db2,$jqry,$header_fields)=@_;
	my ($i, $column, $maxhits, $numhits, $nh, $first , @hits, $value,
	    $query, $condtype,$sort_order,@rec,@cols,$q2);
	#if ($in{'keyword'}){
	#	$in{"st"} = 'or';
	#}
	
	if ($in{'st'} =~ /or/i){
		$condtype = "OR";
	}else{
		$condtype = "AND";
	}
	
	$query = &build_query_str($db1);
	@cols = @db_cols;
	($query) and ($query = "($query)");
	$q2 = &build_query_str($db2);
	($q2) and ($q2 = "($q2)");
	if ($query and $q2) {
		$query = " $query $condtype $q2";
	}elsif($q2){
		$query = $q2;
	}
	
	push(@cols, @db_cols);

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
	if (!$query and !$in{'listall'}){
		return (0,'');
	}elsif ($query){
		$query = "AND ($query)";
	}
	$in{'nh'} ? ($nh = $in{'nh'}) : ($nh = 1);
	$numhits = 0;


	### SORT Records ###
	if (exists($in{'sb'})) {
		if ($db_cols[$in{'sb'}]){
			$sort_order = "ORDER BY $db_cols[$in{'sb'}] $in{'so'}";
		}elsif ($db_field_types{$in{'sb'}}){
			$sort_order = "ORDER BY $in{'sb'} $in{'so'}";
		}
	}
	my ($sth) = &Do_SQL("SELECT COUNT(*) FROM $db1,$db2 WHERE $jqry  $query;");
	$numhits = $sth->fetchrow();

	if ($numhits == 0){
		return (0,'');
	}
	$first = ($usr{'pref_maxh'} * ($nh - 1));
	my(@cols) = split(/,/,$header_fields);
	my ($sth) = &Do_SQL("SELECT $header_fields FROM $db1,$db2 WHERE $jqry  $query $sort_order LIMIT $first,$usr{'pref_maxh'}");
	while (@rec = $sth->fetchrow_array){
		for (0..$#cols){
			push(@hits, $rec[$_]);
		}
	}
	@db_cols = ();
	my ($fname);
	for (0..$#cols){
		if ($cols[$_] =~ /[^.]\.(.*)/){ 
			$fname = $1;
		}else{
			$fname = $cols[$_];
		}
		push(@db_cols, $fname);
	}
	return ($numhits, @hits);
}


sub query_sql {
# --------------------------------------------------------
	my ($header_fields,$query,$id,@cols)=@_;
	my ($i, $column, $maxhits, $numhits, $nh, $first , @hits);

	$in{'nh'} ? ($nh = $in{'nh'}) : ($nh = 1);
	$numhits = 0;


	my ($sth) = &Do_SQL("SELECT COUNT($id) FROM $query");
	$numhits = $sth->fetchrow();
	if ($numhits == 0){
		return (0,'');
	}
	$first = ($usr{'pref_maxh'} * ($nh - 1));
	my ($sth) = &Do_SQL("SELECT $header_fields FROM $query LIMIT $first,$usr{'pref_maxh'}");
	while ($rec = $sth->fetchrow_hashref){
		foreach my $column (@cols) {
			push(@hits, $rec->{$column});
		}
	}

	return ($numhits, @hits);
}



sub build_query_str {
# --------------------------------------------------------
	my ($db) = @_;
	my ($column,$colval,$query,$xquery);
	&load_cfg($db);
	if ($in{"$db.keyword"}) {
		for my $i(0..$#db_cols){
			$column = lc($db_cols[$i]);
			$in{"$db.keyword"} =~ s/^\s+//g;
			$in{"$db.keyword"} =~ s/\s+$//g;
			if ($db_valid_types{$column} eq 'date' and &date_to_sql($in{'keyword'})){
				$query .= "$db.$db_cols[$i] = '" . &date_to_sql($in{'keyword'}) . "' OR ";
			}elsif ($in{"$db.sx"} or $in{"$db.SX"}){
				$query .= "$db.$db_cols[$i] = '" . &filter_values($in{'keyword'}) . "' OR ";
			}else{
				$query .= "$db.$db_cols[$i] like '%" . &filter_values($in{'keyword'}) . "%' OR ";
			}
		}
		$query = substr($query,0,-3);
	}elsif (!$in{"$db.listall"}){
		if ($in{"$db.st"} =~ /or/i){
			$condtype = "OR";
		}else{
			$condtype = "AND";
		}
		for my $i(0..$#db_cols){
			$column = lc($db_cols[$i]);
			$colval = $in{"$db.$column"};
			$colval =~ s/^\s+//g;
			$colval =~ s/\s+$//g;
			$colval = &filter_values($colval);
			#($db_valid_types{$column} eq 'date') ?
			#	($value = &date_to_sql($in{$column})):
			#	($value = &filter_values($in{$column}));
			if ($colval !~ /^\s*$/) {
				if ($colval =~ /~~|\|/){
					@aux = split(/~~|\|/, $colval);
					$xquery = '';
					for (0..$#aux){
						($db_valid_types{$column} eq 'date') ?
							($value = &date_to_sql($aux[$_])):
							($value = &filter_values($aux[$_]));
						($in{'sx'} or $db_valid_types{$column} eq 'date')?
							($xquery .= "$db.$db_cols[$i] = '$value'  OR "):
							($xquery .= "$db.$db_cols[$i] like '%$value%'  OR ");
					}
					$query = "(" . substr($xquery,0,-4) . " ) $condtype " unless (!$xquery);
				
				}else{
					if ($db_valid_types{$column} eq 'date' and $colval eq 'today'){
						$query .= "$db.$db_cols[$i] = CURDATE() $condtype ";
					}elsif($db_valid_types{$column} eq 'date' and $colval eq 'thisweek'){
						$query .= "WEEK($db.$db_cols[$i]) = WEEK(CURDATE()) $condtype ";
					}elsif($db_valid_types{$column} eq 'date' and $colval eq 'thismonth'){
						$query .= "MONTH($db.$db_cols[$i]) = MONTH(CURDATE()) $condtype ";
					}elsif($db_valid_types{$column} eq 'date' and $colval eq 'thisyear'){	
						$query .= "YEAR($db.$db_cols[$i]) = YEAR(CURDATE()) $condtype ";
					}elsif($value eq 'NULL'){
						$query .= "ISNULL($db.$db_cols[$i]) $condtype ";						
					}elsif($in{"$db.sx"} or $db_valid_types{$column} eq 'date'){
						$query .= "$db.$db_cols[$i]  = '$colval' $condtype ";
					}else{
						$query .= "$db.$db_cols[$i] like '%$colval%'  $condtype ";
					}
					
				}
			}
			if ($in{"from_$db.$column"} !~ /^\s*$/) {
				$colval = $in{"from_$db.$column"};
				$colval =~ s/^\s+//g;
				$colval =~ s/\s+$//g;
				$colval = &filter_values($colval);
				### From To Fields
				if ($db_valid_types{$column} eq 'date' and $colval eq 'today'){
					$query .= "$db.$db_cols[$i] > CURDATE() $condtype ";
				}elsif($db_valid_types{$column} eq 'date' and $colval eq 'thisweek'){
					$query .= "WEEK($db.$db_cols[$i]) > WEEK(CURDATE()) $condtype ";
				}elsif($db_valid_types{$column} eq 'date' and $colval eq 'thismonth'){
					$query .= "MONTH($db.$db_cols[$i]) > MONTH(CURDATE()) $condtype ";
				}elsif($db_valid_types{$column} eq 'date' and $colval eq 'thisyear'){	
					$query .= "YEAR($db.$db_cols[$i]) > YEAR(CURDATE()) $condtype ";
				}elsif($in{'sx'} or $db_valid_types{$column} eq 'date'){
					$query .= "$db.$db_cols[$i]  > '$colval'  $condtype ";
				}else{
					$query .= "$db.$db_cols[$i] > '$colval'  $condtype ";
				}
			}
			if ($in{"to_$db.$column"} !~ /^\s*$/) {
				$colval = $in{"to_$db.$column"};
				$colval =~ s/^\s+//g;
				$colval =~ s/\s+$//g;
				$colval = &filter_values($colval);
				### From To Fields
				if ($db_valid_types{$column} eq 'date' and $colval eq 'today'){
					$query .= "$db.$db_cols[$i] < CURDATE() $condtype ";
				}elsif($db_valid_types{$column} eq 'date' and $colval eq 'thisweek'){
					$query .= "$db.$db_cols[$i] < WEEK(CURDATE()) $condtype ";
				}elsif($db_valid_types{$column} eq 'date' and $colval eq 'thismonth'){
					$query .= "$db.$db_cols[$i] < MONTH(CURDATE()) $condtype ";
				}elsif($db_valid_types{$column} eq 'date' and $colval eq 'thisyear'){	
					$query .= "$db.$db_cols[$i] < YEAR(CURDATE()) $condtype ";
				}elsif($in{'sx'} or $db_valid_types{$column} eq 'date'){
					$query .= "$db.$db_cols[$i]  < '$colval'  $condtype ";
				}else{
					$query .= "$db.$db_cols[$i] < '$colval'  $condtype ";
				}
			}
		}
		$query = substr($query,0,-4);
	}
	return $query;
}


sub array_to_hash {
# --------------------------------------------------------
	my($hit, @array) = @_;
	my(%hash, $j);

	for ($j = 0; $j <= $#db_cols; $j++) {
		$hash{$db_cols[$j]} = $array[$hit * ($#db_cols+1) + $j];
	}
	return %hash;
}

sub pages_list {
# --------------------------------------------------------
# Last Modified RB: 10/07/09  13:08:47 -- Skiping the string if length is greater than 600 digits to prevent browser's string overlimit


	my ($nh,$url,$numhits,$maxhits) = @_;
	
	my ($next_url,$key,$left,$upper,$output,$prev_hit,$qs,$lastpage);
	my ($maxpages) = 3;
	(!$maxhits) and ($maxhits = 20);
	
	if ($numhits == 0){
		return (0,'0');
	}
	
	foreach my $key (sort keys %in) {
		($key =~ /^nh$|^qs$/) and (next);
		($in{$key} =~ /(\d{6}\|){100,}/) and (next); #Used to prevent overlimit browser string
		next if( $key =~ /admin_users\../ or length($in{$key}) > 100 );
		($in{$key}) and ($next_url .= "$key=$in{$key}&");
	}

	chop($next_url);
	$next_url =~ s/\&nh=\d+//;
	$next_url =~ s/&xtabs=[a-z]+//;
	(!$nh) and ($nh = 1);
	$qs = $next_url;
	$next_hit = $nh + 1;
	$prev_hit = $nh - 1;
	if ($numhits <= $maxhits) {
		return ('1',$qs);
	}
	$lastpage = int($numhits/$maxhits) + 1;
	
	$left  = $nh;
	$right = int($numhits/$maxhits) - $nh;
	($left > $maxpages)  ? ($lower = $left - $maxpages) : ($lower = 1);
	($right > $maxpages) ? ($upper = $nh + $maxpages)   : ($upper = int($numhits/$maxhits) + 1);
	($maxpages - $nh >= 0) and ($upper = $upper + ($maxpages +1 - $nh));
	($nh > ($numhits/$maxhits - $maxpages)) and ($lower = $lower - ($nh - int($numhits/$maxhits - $maxpages) - 1));
	$output = "";

	if ($nh >1 and $lastpage > 7){
		$output .= qq|
			<a href="$url?$next_url&nh=1"><<</a> &nbsp;
			<a href="$url?$next_url&nh=$prev_hit"><</a> |;
	}elsif ($nh >1){
		$output .= qq|<a href="$url?$next_url&nh=$prev_hit"><</a>|;
	}
	for ($i = 1; $i <= int($numhits/$maxhits) + 1; $i++) {
		if ($i < $lower) { $output .= " ... "; $i = ($lower-1); next; }
		if ($i > $upper) { $output .= qq| ... |; last; }
		($i eq $nh) ?
			($output .= qq~<b>$i</b> ~) :
			($output .= qq~<a href="$url?$next_url&nh=$i">$i</a> ~);
		if (($i * $maxhits) >= $numhits) { last; }  # Special case if we hit exact.
	}
	if ($nh < $i and $lastpage > 7){
		$output .= qq|
			<a href="$url?$next_url&nh=$next_hit">></a> &nbsp;
			<a href="$url?$next_url&nh=$lastpage">>></a> |;
	}elsif ($nh < $i){
		$output .= qq|<a href="$url?$next_url&nh=$next_hit">></a>|;
	}
	if ($lastpage > 15){
		my ($select_str,$i);
		if($nh > 5){
			$dif = $nh/10;
			if ($dif<1){
				for my $i (1..$lower){
					$select_str .= "<option value='$i'>$i</option>\n";
				}	
			}else{
				$dif = $nh/(10 *.6);
				if ($dif>0){
					for my $i (1..5){
						$select_str .= "<option value='".int($i*$dif)."'>".int($i*$dif)."</option>\n";
					}
				}
				
			}
			if ($lastpage-$upper >5){
				$select_str .= "<option style='color:red' disabled>$nh</option>\n";
			}
		}
		
		if ($lastpage-$upper >5){
			if (!$select_str){
				$select_str .= "<option style='color:red' disabled>$nh</option>\n";
			}
			$dif = ($lastpage-$upper)/(10 *.6);
			if ($dif<1){
				for my $i ($upper..$lastpage){
					$select_str .= "<option value='$i'>$i</option>\n";
				}	
			}else{
				$dif = ($lastpage-$upper)/(10 *.6);
				if ($dif>0){
					for my $i (1..5){
						$select_str .= "<option value='".int($i*$dif+$upper)."'>".int($i*$dif+$upper)."</option>\n";
					}
				}
				
			}
		}else{
			$upper = $lastpage - 6;
			for my $i ($upper..$lastpage-1){
				$select_str .= "<option value='$i'>$i</option>\n";
			}
			$select_str .= "<option style='color:red' disabled>$nh</option>\n";
		}
		
#		if($upper < int($numhits/$maxhits)){
#			$fwd = $upper+10; 
#			$i = 1;
#			while($i < 8 and $fwd <= int($numhits/$maxhits) + 1){
#				$select_str .= "<option value='$fwd'>$fwd</option>\n";
#				$fwd +=10;
#				$i++;
#			}
#		}
		if ($select_str){
			$output .= qq|<select onChange="trjump('$url?$next_url&nh='+this.value)"><option value=''>---</option>$select_str</select> |;
		}else{
			$output .= "$dif";
		}
	}
	return ($output,$qs);
}


sub validate_cols {
# --------------------------------------------------------
	my ($notnullvals) = @_;
	my ($col,$err,$query,$start_col);

	if ($in{'not_autoincrement'}){
		$start_col = 0;
	}else{
		$start_col = 1;
	}


	for ($start_col..$#db_cols-3){
		
		$col = lc($db_cols[$_]);
		$in{$col} =~ s/^\s+//g;
		$in{$col} =~ s/\s+$//g;
		if ($in{'edit'} and $sys{'db_'.$in{'cmd'}.'_edit_fixed'}){
			$sys{'db_'.$in{'cmd'}.'_edit_fixed'} = ','.$sys{'db_'.$in{'cmd'}.'_edit_fixed'}.',';
			($sys{'db_'.$in{'cmd'}.'_edit_fixed'} =~ /,$col,/i) and (next);
		}
		##### Not Null Check #####
		if ($in{$col} =~ /^\s*$/ && $db_not_null{$col}) {
			$error{$col} = &trans_txt("required");
			$ele = $col;
			++$err;
			#&cgierr("1-$col");
		##### Valid E-Mail Check #####
		}elsif ($db_valid_types{$col} eq "email" and $in{$col} and($in{$col} =~ /(@.*@)|(\.\.)|(@\.)|(\.@)|(^\.)/ or $in{$col} !~ /^.+\@(\[?)[a-zA-Z0-9\-\.]+\.([a-zA-Z]{2,3}|[0-9]{1,3})(\]?)$/ )){
			$error{$col} = &trans_txt("invalid");
			++$err;
			#&cgierr("2-$col");
		##### Valid numeric field Check #####
		}elsif ($db_valid_types{$col} eq "numeric" and $in{$col} =~ /[a-zA-Z]/){
			$error{$col} = &trans_txt("invalid");
			++$err;
			#&cgierr("3-$col");
		}elsif ($db_valid_types{$col} eq "currency" and $in{$col} =~ /[a-zA-Z]/){
			$error{$col} = &trans_txt("invalid");
			++$err;
			#&cgierr("4-$col");
		##### Valid Date field Check #####
		}elsif ($in{$col} and $db_valid_types{$col} eq "date" and $in{$col} !~ /^\s*$/ and ($in{$col} ne 'NOW()' or $in{$col} ne 'CURDATE()') and $in{$col} ne 'NULL'){
			if (&valid_date_sql($in{$col}) == 0){
				$error{$col} = &trans_txt("invalid");
				++$err;
				#&cgierr("5-$col");
			}
		}
		### Save Query
		if($in{$col} eq "NOW()" or $in{$col} eq "CURDATE()"){
			$query .= "`$db_cols[$_]`=CURDATE() ,";
		#}elsif ($db_valid_types{$col} eq 'date' and $in{$col}){
		#	$query .= "$db_cols[$_]='" . &date_to_sql($in{$col}) . "' ,";
		}elsif($in{$col} eq 'NULL' or $in{$col} eq '' ){
			$query .= "`$db_cols[$_]`=NULL ,";
		}elsif($db_valid_types{$col} eq "checkbox"){
			my ($str) = $in{$col};
			$str =~ s/\|/,/g;
			$query .= "`$db_cols[$_]`='" . &filter_values($str) . "' ,";
		}elsif($in{$col}){
			$query .= "`$db_cols[$_]`='" . &filter_values($in{$col}) . "' ,";
		}elsif($db_valid_types{$col} eq "numeric"){
			$query .= "`$db_cols[$_]`=" . &filter_values($in{$col}) . " ,";
		}elsif (!$in{$col} and $notnullvals and $db_valid_types{$col} ne "numeric"){
			$query .= "`$db_cols[$_]`='',"
		}
	}
	chop($query);
	return ($err,$query);
}


sub update_system {
# --------------------------------------------------------
	my ($fname) = @_;
	my ($file, $key,$td,$name,$value,%stmp,%ctmp);


	#### Load Actual File
	# --------------------------------------------------------
	if (open (my $cfg, "<", $fname)){
		LINE: while (<$cfg>) {
			(/^#/)      and next LINE;
			(/^\s*$/)   and next LINE;
			$line = $_;
			$line =~ s/\n|\r//g;
			($td,$name,$value) = split (/\||\=/, $line,3);
			if ($td eq "conf") {
				if ($cfg{$name}){
					$cfg{$name} =~ s/\n/~~/g;
					$ctmp{$name} = $cfg{$name};
				}else{
					$ctmp{$name} = $value;
				}
				next LINE;
			}elsif ($td eq "sys"){
				if ($sys{$name}){
					$sys{$name} =~ s/\n/~~/g;
					$stmp{$name} = $sys{$name};
				}else{
					$stmp{$name} = $value;
				}
				next LINE;
			}
		}
	}else{
		return 'error';
	}

	$file =	qq~#######################################################################\n## This File was generated by the system. Edit with Caution\n## \n## type|Name=Value\n## \n## You can edit only the VALUE of the following types: conf,sys and menus\n##\n##\n~;
	$file .= "\n\n";
	$file .= "###### Path/urls/filenames\n";
	foreach my $key (sort keys %ctmp) {
		$file .= "conf|$key=$ctmp{$key}\n";
	}

	$file .= "\n\n";
	$file .= "###### System Data\n";
	foreach my $key (sort keys %stmp) {
		$file .= "sys|$key=$stmp{$key}\n";
	}

	if (open (my $cfg, ">", $fname)){
		print $cfg $file;
	}else{
		return 'error';
	}
	return "ok"
}


sub check_field {
# --------------------------------------------------------
	my ($in_val,$col_null,$col_type,$err) = @_;
	my ($output);
	$in_val =~ s/^\s+//g;
	$in_val =~ s/\s+$//g;
	##### Not Null Check #####
	if ($in_val =~ /^\s*$/ && $col_null) {
		$output = "<span class='fieldterr'>Required</span>";
		++$err;
	##### Valid E-Mail Check #####
	}elsif ($col_type eq "email" and $in_val and($in_val =~ /(@.*@)|(\.\.)|(@\.)|(\.@)|(^\.)/ or $in_val !~ /^.+\@(\[?)[a-zA-Z0-9\-\.]+\.([a-zA-Z]{2,3}|[0-9]{1,3})(\]?)$/ )){
		$output = "<span class='fieldterr'>Invalid</span>";
		++$err;
	##### Valid numeric field Check #####
	}elsif ($col_type eq "numeric" and $in_val =~ /[a-zA-Z]/){
		$output = "<span class='fieldterr'>Invalid</span>";
		++$err;
	}elsif ($col_type eq "currency" and $in_val =~ /[a-zA-Z]/){
		$output = "<span class='fieldterr'>Invalid</span>";
		++$err;
	##### Valid Date field Check #####
	}elsif ($col_type eq "date" and $in_val !~ /^\s*$/){
		if (&date_to_sql($in_val) == 0){
			$output = "<span class='fieldterr'>Required</span>";

		}
	}
	return ($output,$err);
}


#############################################################################
#############################################################################
#   Function: get_record
#
#       Es: Extrae la informacion de un registro especifico en la DB.
#       En: 
#
#
#    Created on: 
#
#    Author: Roberto Barcenas
#
#    Modifications:
#
#		 - Modified on *2011/08/12* by _MCC C. Gabriel Varela S_ : connection type to the DB is considered
#		 - Modified on *2014/12/15* by _Roberto Barcenas_ : Se agrega Variable only_my_records para ver solo el registro si es dueno el usuario
#
#   Parameters:
#
#      - @param_data: Arreglo con datos (ID_po, Cost, Tax,ID_accounts for Vendor, ID_accounts tax payable, ID_accounts tax paid)
#      -   
#
#  Returns:
#
#      - 
#
#   See Also:
#
#
sub get_record {
#############################################################################
#############################################################################

	my ($idname,$key,$db) = @_;
	my ($query, $found, %tmp, $rec, $column);
	$key = &filter_values($key);
	my $conn=0;
	$conn=1 if ($in{'second_conn'}==1);

	###################################
	###################################
	####################################
	#
	#	View Only My Records
	#
	###################################
	###################################
	####################################
	## Se agrega restriccion basada a Arbol de Agentes, Supervisores y Coordinadores
	$custom_id_admin_users = &get_call_center_agents_list();

	if ($in{'only_my_records'}){
		$query = "AND ID_admin_users = '$usr{'id_admin_users'}' ";
	}elsif($custom_id_admin_users ne ''){
		$query = "AND ID_admin_users IN (".$custom_id_admin_users.") ";
	}

	#####
	##### Se agrega reestriccion para mostrar solo Orders de Canales de Venta que el usuario tenga asignados.
	#####
	$query_only_my_records .= ($in{'only_records_by_salesorigins'} and $in{'only_records_by_salesorigins'} ne '')? " AND sl_orders.ID_salesorigins IN ($in{'only_records_by_salesorigins'}) ":"";

	my ($sth) = &Do_SQL("SELECT * FROM $cfg{'dbi_suf'}$db WHERE $idname='$key' $query",$conn);
	$rec = $sth->fetchrow_hashref;
	foreach my $column (@db_cols) {
		$tmp{lc($column)} = $rec->{$column};
		if ($db_valid_types{lc($column)} eq 'date' and $tmp{lc($column)} eq '0000-00-00'){
			$tmp{lc($column)} = '';
		}elsif ($db_valid_types{$column} eq 'checkbox'){
			$tmp{$column} =~ s/,/|/g;;
		#}elsif ($db_valid_types{lc($column)} eq 'email' and $tmp{lc($column)} eq 'email'){
		#	$tmp{lc($column)} = '';
		#}
		}elsif ($db_valid_types{lc($column)} eq 'email' and $tmp{lc($column)} eq 'email'){
			$tmp{lc($column)} = '';
		}
	}
	($tmp{lc($idname)} eq $key) ?
		(return %tmp) :
		(return undef);

}



sub get_user_info {
# --------------------------------------------------------
	my ($uid)= @_;
	my ($sth) = &Do_SQL("SELECT * FROM admin_users WHERE ID_admin_users='$uid';");
	my ($rec) = $sth->fetchrow_hashref();
	foreach my $key (keys %{$rec}){
		$in{"admin_users.".lc($key)} = $rec->{$key};
	}
}

sub get_db_extrainfo {
# --------------------------------------------------------
	my ($db,$uid)= @_;
	my ($name);
	if ($db =~ /^\w{3}_.*/){
		$name = substr($db,4);
	}else{
		$name = $db;
	}
	my ($sth) = &Do_SQL("SELECT * FROM $db WHERE ID_$name='$uid';");
	my ($rec) = $sth->fetchrow_hashref();
	foreach my $key (keys %{$rec}){
		$in{$name.".".lc($key)} = $rec->{$key};
	}
}

sub split_lines {
# --------------------------------------------------------
	my ($dbfields,$dbmenus,$dbtypefields,$dbvalidfields) = @_;
	my (%tmp,@ary,@lines);

	## Load Menus Info
	my (@lines) = split(/\n|~~/,$dbmenus);
	for (0..$#lines){
		@ary = split(/:/,$lines[$_],2);
		$tmp{$ary[0].'_menu'} = $ary[1];
	}
	
	## Load File Types
	my (@lines) = split(/\n|~~/,$dbtypefields);
	for (0..$#lines){
		@ary = split(/:/,$lines[$_]);
		##field_1:40:text:right
		$tmp{$ary[0].'_lsize'}  = $ary[1];
		$tmp{$ary[0].'_ltype'}  = $ary[2];
		$tmp{$ary[0].'_lpos'} = $ary[3];
	}
	
	## Load Fields Info
	my (@lines) = split(/\n|~~/,$dbfields);
	for (0..$#lines){
		@ary = split(/:/,$lines[$_]);
		##field_1:First Name:alpha:40:ON
		$tmp{$ary[0]} = 'field';
		$tmp{$ary[1].'_fname'}   = $ary[0];
		$tmp{$ary[0].'_name'}   = $ary[1];
		$tmp{$ary[0].'_ftype'}   = $ary[2];
		$tmp{$ary[0].'_flen'} = $ary[3];
		$tmp{$ary[0].'_freq'}    = $ary[4];
		
	}
	
	## Load Validation Rules
	my (@lines) = split(/\n|~~/,$dbvalidfields);
	for (0..$#lines){
		@ary = split(/:/,$lines[$_]);
		##field_1:5:9:alpha:1
		$tmp{$ary[0].'_vmin'}  = $ary[1];
		$tmp{$ary[0].'_vmax'}  = $ary[2];
		$tmp{$ary[0].'_vtype'} = $ary[3];
		$tmp{$ary[0].'_vreq'}  = $ary[4];
	}	
	
	return %tmp;
}

sub validate_ccol {
# --------------------------------------------------------
	my ($min,$max,$req,$type,$col,$err)= @_;
	
	if ($req and !$in{$col}){
		$error{$col} = &trans_txt("required");
		++$err;
	##### Valid E-Mail Check #####
	
	}elsif ($type eq "email" and $in{$col} and($in{$col} =~ /(@.*@)|(\.\.)|(@\.)|(\.@)|(^\.)/ or $in{$col} !~ /^.+\@(\[?)[a-zA-Z0-9\-\.]+\.([a-zA-Z]{2,3}|[0-9]{1,3})(\]?)$/ )){
		$error{$col} = &trans_txt("invalid");
		++$err;
	##### Valid numeric field Check #####
	}elsif ($type eq "numeric" and $in{$col} =~ /[a-zA-Z]/){
		$error{$col} = &trans_txt("invalid");
		++$err;
	}elsif ($type eq "currency" and $in{$col} =~ /[a-zA-Z]/){
		$error{$col} = &trans_txt("invalid");
		++$err;
	##### Valid Date field Check #####
	}elsif ($in{$col} and $type eq "date" and $in{$col} !~ /^\s*$/){
		if (&valid_date_sql($in{$col}) == 0){
			$error{$col} = &trans_txt("invalid");
			++$err;
		}
	}elsif(($req or $in{$col}) and (length($in{$col})<$min and $min>0) or (length($in{$col})>$max and $max>0)){
		$error{$col} = &trans_txt("invalidlen");
		++$err;
	}
	return $err;
}

sub build_comments {
# --------------------------------------------------------
	my ($tbl,$id_name,$id_value,$tbl_id) = @_;
	my ($rec,$tmp,$line,$output,$fname,$tline);
	my ($sth) = &Do_SQL("SELECT COUNT(*) FROM $tbl WHERE $id_name='$id_value';");
	if ($sth->fetchrow>0){
		$line = &trans_txt('comments_legend');
		my ($sth) = &Do_SQL("SELECT * FROM $tbl WHERE $id_name='$id_value' ORDER BY $tbl_id DESC;");
		while ($rec = $sth->fetchrow_hashref){
			$rec->{'Comments'} =~ s/\n/<br>/g;
			my ($sth2) = &Do_SQL("SELECT * FROM admin_users WHERE ID_admin_users='$rec->{'ID_admin_users'}';");
			$tmp = $sth2->fetchrow_hashref;
			$tline = $line;
			while ($tline =~ /\[([^]]+)\]/){
				$fname = $1;
				if ($rec->{$fname}){
					$tline =~ s/\[$fname\]/$rec->{$fname}/gi;
				}else{
					$tline =~ s/\[$fname\]/$tmp->{$fname}/gi;
				}
			}
			$output .= "<tr><td class='smalltext'>$tline</td></tr>";
		}
		return $output;
	}else{
		return "<tr><td class='smalltext'>".&trans_txt('comments_no')."</td></tr>";
	}
}

sub build_select_fieldnames {
# --------------------------------------------------------
	my ($db_name,$dbcmd)=@_;
	my (@db_cols,$output);
	my ($sth) = &Do_SQL("describe $db_name;");
	while (@ary = $sth->fetchrow_array() ) {
		push(@db_cols,$ary[0]);
	}
	%finfo = &split_lines($sys{$dbcmd.'_DbFields'},$sys{$dbcmd.'_DbMenus'},$sys{$dbcmd.'_DbTypeFields'},$sys{$dbcmd.'_DbValidFields'});

	$va{'db_sfields'} =  "";
	for(0..$#db_cols){
		if ($db_cols[$_] =~ /^ID_(.*)/){
			$output .=  "<option value='$db_cols[$_]'>ID $1</option>\n";
		}elsif($db_cols[$_] =~ /^field/){
			$output .=  "<option value='$db_cols[$_]'>$finfo{$db_cols[$_].'_name'}</option>\n";
		}else{
			$output .=  "<option value='$db_cols[$_]'>$db_cols[$_]</option>\n";
		}
	}
	return $output;
}


sub update_egwperm {
# --------------------------------------------------------
	my ($egw_uid,$usergroup)=@_;
	if ($cfg{'egw_off'}){
		return;
	}
	### Insert Applications Permmissions
	my ($sth) = &Do_SQL("DELETE FROM egw_acl WHERE acl_account='$egw_uid'");
	my ($sth) = &Do_SQL("SELECT app_perm FROM admin_users_group_app WHERE ID_admin_users_group='$usergroup' AND app='egw'");
	my (@ary) = split(/,/, $sth->fetchrow);
	my ($sth) = &Do_SQL("INSERT INTO egw_acl SET acl_appname='home',acl_location='run',acl_account='$egw_uid',acl_rights='1'");
	for (0..$#ary){
		if ($ary[$_] =~ /([^=]+)=on/){
			my ($sth) = &Do_SQL("INSERT INTO egw_acl SET acl_appname='$1',acl_location='run',acl_account='$egw_uid',acl_rights='1'");
		}
	}
}



sub specialchar_cnv{
# --------------------------------------------------------
	local($ch) = @_;

	$ch =~ s/&/&amp;/g;		# &
	$ch =~ s/\"/&quot;/g;	#"
	$ch =~ s/\'/&#39;/g;	# '
	$ch =~ s/</&lt;/g;		# <
	$ch =~ s/>/&gt;/g;		# >
	
	return($ch);
}

sub FCKCreateHtml{
# --------------------------------------------------------
	my ($InstanceName,$Value) = @_;
	#$Value = @_[0];
	#$InstanceName	     = 'siteditor';
	$BasePath		     = $cfg{'path_ns_img'} . 'FCKeditor/';
	$Width			= '100%';
	$Height			= '350';
	$ToolbarSet		= 'Default';

	if($usr{'application'} ne 'admin') {	
		$HtmlValue = &specialchar_cnv($Value);
	}else {
		$HtmlValue = $Value;
	}

	$Html = '' ;
	if(&IsCompatible()) {
		$Link = $BasePath . "editor/fckeditor.html?InstanceName=$InstanceName";
		if($ToolbarSet ne '') {
			$Link .= "&amp;Toolbar=$ToolbarSet";
		}
		#// Render the linked hidden field.
		$Html .= "<input type=\"hidden\" id=\"$InstanceName\" name=\"$InstanceName\" value=\"$HtmlValue\" style=\"display:none\" />" ;

		#// Render the configurations hidden field.
		$cfgstr = &GetConfigFieldString();
		$wk = $InstanceName."___Config";
		$Html .= "<input type=\"hidden\" id=\"$wk\" value=\"$cfgstr\" style=\"display:none\" />" ;

		#// Render the editor IFRAME.
		$wk = $InstanceName."___Frame";
		$Html .= "<iframe id=\"$wk\" src=\"$Link\" width=\"$Width\" height=\"$Height\" frameborder=\"0\" scrolling=\"no\"></iframe>";
	} else {
		if($Width =~ /\%/g){
			$WidthCSS = $Width;
		} else {
			$WidthCSS = $Width . 'px';
		}
		if($Height =~ /\%/g){
			$HeightCSS = $Height;
		} else {
			$HeightCSS = $Height . 'px';
		}
		$Html .= "<textarea name=\"$InstanceName\" rows=\"4\" cols=\"40\" style=\"width: $WidthCSS; height: $HeightCSS\">$HtmlValue</textarea>";
	}
	return($Html);







}

sub IsCompatible{
# --------------------------------------------------------	
	$sAgent = $ENV{'HTTP_USER_AGENT'};
	if(($sAgent =~ /MSIE/i) && !($sAgent =~ /mac/i) && !($sAgent =~ /Opera/i)) {
		$iVersion = substr($sAgent,index($sAgent,'MSIE') + 5,3);
		return($iVersion >= 5.5) ;
	} elsif($sAgent =~ /Gecko\//i) {
		$iVersion = substr($sAgent,index($sAgent,'Gecko/') + 6,8);
		return($iVersion >= 20030210) ;
	} elsif($sAgent =~ /Opera\//i) {
		$iVersion = substr($sAgent,index($sAgent,'Opera/') + 6,4);
		return($iVersion >= 9.5) ;
	} elsif($sAgent =~ /AppleWebKit\/(\d+)/i) {
		return($1 >= 522) ;
	} else {
		return(0);		# 2.0 PR fix
	}
}

sub GetConfigFieldString{
# --------------------------------------------------------		
	$sParams = '';
	$bFirst = 0;
	foreach my $sKey (keys %Config) {
		$sValue = $Config{$sKey};
		if($bFirst == 1) {
			$sParams .= '&amp;';
		} else {
			$bFirst = 1;
		}
		$k = &specialchar_cnv($sKey);
		$v = &specialchar_cnv($sValue);
		if($sValue eq "true") {
			$sParams .= "$k=true";
		} elsif($sValue eq "false") {
			$sParams .= "$k=false";
		} else {
			$sParams .= "$k=$v";
		}
	}
	return($sParams);
}

sub build_product_pay_typedescription{
# --------------------------------------------------------

# Author: Jose Ramirez Garcia
# Created on: 9/14/2008
# Last Modified on: 
# Last Modified by: 
# Description : 
# Forms Involved: 
# Parameters : 
# Last Modified on: 10/28/08 16:03:06
# Last Modified by: MCC C. Gabriel Varela S, Lic. Roberto B?rcenas: Se hacen validaciones solicitadas por Carlos
# Last Modified by RB on 06/09/2011 04:36:42 PM : Se agrega Paypal, Google Checkout y Prepaid Card a la lista, pero solo Prepaid Card se agrega a la cadena 

	if($in{'paytype'}){
		my @paytype=split(/\|/,$in{'paytype'});
		%textpaytype = ('COD'=>'COD', 'Layaway'=>'Layaway', 'Money-Order'=>'Money Order', 'Western-Union'=>'Western Union', 'Check'=>'Check', 'Credit-Card-7'=>'Credit Card Weekly', 'Credit-Card-15'=>'Credit Card Biweekly', 'Credit-Card-30'=>'Credit Card Monthly','paypal'=>'Paypal','google'=>'Google Check Out','Prepaid-Card'=>'Prepaid Card');
		for my $i(0.. $#paytype){
			if($textpaytype{$paytype[$i]}eq'COD' and $cfg{'paytypescod'}==1)
			{
				$desc .= " ".$textpaytype{$paytype[$i]}.",";
			}
			if($textpaytype{$paytype[$i]}eq'Layaway' and $cfg{'paytypeslay'}==1)
			{
				$desc .= " ".$textpaytype{$paytype[$i]}.",";
			}
			if($textpaytype{$paytype[$i]}eq'Money-Order' and $cfg{'paytypesmo'}==1)
			{
				$desc .= " ".$textpaytype{$paytype[$i]}.",";
			}
			if($textpaytype{$paytype[$i]}eq'Western-Union' and $cfg{'paytypeswu'}==1)
			{
				$desc .= " ".$textpaytype{$paytype[$i]}.",";
			}
			if($textpaytype{$paytype[$i]}eq'Check' and $cfg{'paytypeschk'}==1)
			{
				$desc .= " ".$textpaytype{$paytype[$i]}.",";
			}
			if($textpaytype{$paytype[$i]}eq'Check' and $cfg{'paytypeschk'}==1)
			{
				$desc .= " ".$textpaytype{$paytype[$i]}.",";
			}
			if($cfg{'paytypescc'}==1)
			{
				if($textpaytype{$paytype[$i]}eq'Credit Card Weekly' and $cfg{'fpweekly'}==1)
				{
					$desc .= " ".$textpaytype{$paytype[$i]}.",";
				}
				if($textpaytype{$paytype[$i]}eq'Credit Card Biweekly' and $cfg{'fpbiweekly'}==1)
				{
					$desc .= " ".$textpaytype{$paytype[$i]}.",";
				}
				if($textpaytype{$paytype[$i]}eq'Credit Card Monthly' and $cfg{'fpmonthly'}==1)
				{
					$desc .= " ".$textpaytype{$paytype[$i]}.",";
				}
			}
			if($textpaytype{$paytype[$i]}eq'Prepaid Card' and $cfg{'paytypesppc'}==1)
			{
				$desc .= " ".$textpaytype{$paytype[$i]}.",";
			}
		}
		chop($desc);
	}
	return $desc;
}

sub build_autocomplete_from_enum{
# --------------------------------------------------------
# Forms Involved: 
# Created on: 02/25/09 16:10:29
# Author: MCC C. Gabriel Varela S.
# Description :   
# Parameters :
	my ($column,$tbl_name) = @_;
	my ($data,$output);
	my @tmpo,$i=0;
	@fields = &load_enum_toarray($tbl_name,$column);
	if ($#fields == -1) {
		$db_select_fields{$column} = &trans_txt('none');
		return $output;
	}
	$output="[";
	foreach my $field (@fields) {
		$output .= "\"$field\",";
		$tmpo[$i]="\"$field\"";
		++$i;
	}
	$output=join(',',@tmpo);
	$output="[$output]";
	return $output;
}

sub gen_passwd {
# --------------------------------------------------------
# Form: validate_man_users in dbman.html.cgi
# Service: 
# Type : subroutine
# Time Last : 9/06/2007 4:34PM
# Author: Rafael Sobrino
# Description : generates a 6-character (upper/lower alpha + numeric) random password 
# Last Modified on: 11/11/10 16:46:59
# Last Modified by: MCC C. Gabriel Varela S: Copiada desde sub.base de Administration

	my ($len) = 6;		# length of the random password
	my @chars=('a'..'z','A'..'Z','0'..'9','_');
	my ($password);
	foreach (1..$len){
		$password.=$chars[rand @chars];
	}
	return $password;	
}


sub send_lite_mail{
# --------------------------------------------------------
# Author: Roberto Barcenas
# Created on: 10/04/2011
# Description : Envia email utilizando la libreria MIME::Lite
# Forms Involved:
# Parameters : $from, to $cc, $bcc, $subject, $body, $attachment

	my ($from,$to,$cc,$bcc,$subject,$body,$attachment) = @_;

	$to =~ s/\|/,/g;
	$cc =~ s/\|/,/g;
	$bcc =~ s/\|/,/g;

	## Body from a function?
	if (defined &$body){
		$body_msg = &$body();
	}else{
		$body_msg = $body;
	}

	use MIME::Lite;

	$msg = MIME::Lite->new(
	From    	=>$from,
	To      	=>$to,
	Cc      	=>$cc,
	Bcc     	=>$bcc,
	Subject 	=>$subject,
	Type    	=>'text',
	Data    	=>"$body_msg"
	);

	## Attachment part
	if($attachment ne '' and -e $attachment){

		my @ary_path = split(/\//,$attachment);

		my $fname = $ary_path[-1];
		my $type;


		if($attachment =~ /(jpg|gif|png|jpeg|pjpeg|tiff)$/){
			$type = 'image/'.$1;
		}elsif($attachment =~ /(pdf|zip)$/){
			$type = 'application/'.$1;
		}else{
			$type = 'application/octet-stream';
		}


		$msg->attach(
		Type     =>$type,
		Encoding => 'base64',
		Path     =>$attachment,
		Filename =>$fname,
		Disposition => 'attachment'
		);
	}
	$msg->send();
}


sub print_r {
# --------------------------------------------------------
# Author: Carlos Haas
# Created on: 11/14/2011 4:06:48 PM
# Description : equivalente a print_r de php
# Forms Involved:
    package print_r;
    our $level;
    our @level_index;
    print "<pre>";
    if ( ! defined $level ) { $level = 0 };
    if ( ! @level_index ) { $level_index[$level] = 0 };
	
    for ( @_ ) {
        my $element = $_;
        my $index   = $level_index[$level];

        print "\t" x $level . "[$index] => ";

        if ( ref($element) eq 'ARRAY' ) {
            my $array = $_;

            $level_index[++$level] = 0;

            print "(Array)\n";

            for ( @$array ) {
                main::print_r( $_ );
            }
            --$level if ( $level > 0 );
        } elsif ( ref($element) eq 'HASH' ) {
            my $hash = $_;

            print "(Hash)\n";

            ++$level;

            for ( sort keys %$hash ) {
                $level_index[$level] = $_;
                main::print_r( $$hash{$_} );
            }
        } else {
            print "$element\n";
        }

        $level_index[$level]++;
    }
    print "</pre>";
} # End print_r

sub load_db_fields_values {
# --------------------------------------------------------
# Forms Involved:
# Created on: 12/06/07 13:21:00
# Author: Pablo Hdez.
# Description : Carga los campos de una tabla en varibles $in{tabla.campo}
# Parameters : $db: nombre de la tabla, $id_name: id de la tabla, $id_value: valor del id, $fields: campos en formato: campo1, campo2

}

sub changemod {
# --------------------------------------------------------
	if ($usr{'multiapp'} =~ /$in{'to'}/){
		$usr{'application'} = $in{'to'};
		&save_auth_data;
		if ($in{'to'}){
			print "Location: $cfg{'pathcgi'}/mod/$in{'to'}/admin?cmd=home\n\n";
		}else{
			print "Location: $cfg{'auth_logoff'}\n\n";
		}
	}else{
		&html_unauth
	}
}

 sub run_function {
# --------------------------------------------------------
	my ($ptype,@in_params) = @_;
	my ($func,@out_params);
	if ($0 =~ /dbman/){
		
		if ($in{'e'}){
			$func = $ptype . '_er_'.$in{'cmd'};  ## This Replace the Standard Function
			if (defined &$func){
				return &$func(@in_params);
			}
			$func = $ptype . '_eb_'. $in{'cmd'};  ## This is an Addition the Standard Function
			if (defined &$func){
				&$func(@in_params);  ## Does notaccept $out_params
			}
		}
		
		################################
		## This is the standard Function
		$func = $ptype . '_'. $in{'cmd'};
		if (defined &$func){
			@out_params = &$func(@in_params);  
		}
	
		if ($in{'e'}){
			$func = $ptype . '_ea_'. $in{'cmd'};  ## This is an Addition the Standard Function
			if (defined &$func){
				&$func(@in_params);  ## Does notaccept $out_params
			}
		}
		if ($#out_params eq 0){
			return $out_params[0];
		}elsif($#out_params >=1){
			return @out_params;
		}else{
			return;
		}
	}else{
		if ($in{'e'}){
			$func = $ptype . '_er';  ## This Replace the Standard Function $ptype = $in{'cmd'}
			if (defined &$func){
				&$func();
				return 1;
			}
			$func = $ptype . '_eb';  ## This is an Addition the Standard Function
			if (defined &$func){
				&$func();  ## Does notaccept $out_params
			}
		}
		$func = $ptype ;## This is the standard Function
		if (defined &$func){
			&$func(); 
			return 1;
		}
		return 0;
	}
}

sub run_eafunction {
# --------------------------------------------------------
	my ($ptype,@in_params) = @_;
	my ($func,@out_params);
	if ($0 =~ /dbman/){
		if ($in{'e'}){
			$func = $ptype . '_ea'.$in{'cmd'};  ## This Replace the Standard Function
			if (defined &$func){
				&$func(@in_params);
			}
		}
		return;
	}else{
		$func = $ptype . '_ea';  ## This is an Addition the Standard Function $ptype = $in{'cmd'}
		if (defined &$func){
			&$func();  ## Does notaccept $out_params
		}
		return 1;
	}
}

sub run_notifs {
# --------------------------------------------------------
	my ($event) = @_;
	my ($sth) = &Do_SQL("SELECT * FROM admin_notifs WHERE Status='Active' AND Event='".&filter_values($event)."';");
    my ($rec) = $sth->fetchrow_hashref();
    if ($rec->{'ID_notifs'}>0){
    	for my $i(1..3){
    		if ($rec->{'Filter'.$i.'Name'} and $rec->{'Filter'.$i.'Cond'} and $rec->{'Filter'.$i.'Value'}){
    			$query .= " $in{$rec->{'Filter'.$i.'Name'}} $rec->{'Filter'.$i.'Cond'} '$rec->{'Filter'.$i.'Value'}' $rec->{'FiltersCond'}";
    		}
    	}
    	$query =~ s/$rec->{'FiltersCond'}$//;
    	my ($sth2) = &Do_SQL("SELECT IF($query,1,0)");
    	if ($sth2->fetchrow()){
    		my ($sth2) = &Do_SQL("SELECT * FROM admin_notifs_actions WHERE ID_admin_notifs=$rec->{'ID_notifs'} AND Status='Active'");
    		while ($tmp -> fetchrow_hashref() ){
    			if ($tmp->{'Type'} eq 'eMail' and $tmp->{'Destination'} and $tmp->{'From'}){
    				my (@emal_list) = split(/,|\s/, $tmp->{'Destination'});
    				for my $i(0..$#emal_list){
    					send_mail($tmp->{'From'},$emal_list[$i],$rec->{'Name'},$rec->{'Message'});
    				}
    			}
    		}
    	}
	}
	
	return 'OK'
}




#############################################################################
#############################################################################
#   Function: accounting_keypoints
#
#       Es: Recibe llamadas para ejecutar un posible movimiento contable. Dependiendo de la configuracion por empresa, esta funcion puede registrar movimientos contables para el llamado recibido
#       En: 
#
#
#    Created on: 11/08/2012
#
#    Author: _Roberto Barcenas_
#
#    Modifications:
#
#        - Modified on ** by _Roberto Barcenas_ : 
#
#   Parameters:
#
#      - keypoint: Cadena con el keypoint a ejecutar  
#      - data: array con los valores de entrada para la funcion a ejecutar  
#
#  Returns:
#
#      - 
#
#   See Also:
#
#
sub accounting_keypoints {
#############################################################################
#############################################################################

	my ($this_keypoint, $this_data) = @_;

	my $log_status = 'ERROR';
	my ($this_acc, $this_acc_str);

	my ($sth) = &Do_SQL("SELECT Function,Params FROM sl_keypoints_functions WHERE Keypoint = LOWER('".&filter_values($this_keypoint)."');");
	my ($fn,$pr) = $sth->fetchrow_array();
	my (@ary) = (@{$this_data},split(/\n/, $pr));

	if($fn){

		use Cwd;
		my $dir = getcwd;
		my($b_cgibin,$a_cgibin) = split(/cgi-bin/,$dir);
		my $home_dir = $b_cgibin.'cgi-bin/common';
		
		require ("$home_dir/subs/sub.acc_movements.html.cgi");
		if (-e $home_dir . '/subs/sub.acc_movements.e'.$in{'e'}.'.html.cgi') {
			require ($home_dir . '/subs/sub.acc_movements.e'.$in{'e'}.'.html.cgi');
		}

		if(defined &$fn ) {

			$log_status = 'OK';

		}else{

			$log_status = 'FN_NOTDEFINED';

		}

	}

	#######
	####### Log Keypoints
	#######
	my ($sth) = &Do_SQL("INSERT INTO sl_movements_logs SET 
							Keypoint = LOWER('".filter_values($this_keypoint)."')
							, Params = '".join(';;', @ary)."'
							, Application = '".&filter_values($usr{'application'})."'
							, Command = '".&filter_values($in{'cmd'})."'
							, Function = '". $fn ."'
							, Status = '". $log_status ."'
							, Date = CURDATE()
							, Time = CURTIME()
							, ID_admin_users = '".$usr{'id_admin_users'}."'
						;");

	return (1,$log_status . ';;' . $this_keypoint) if $log_status eq 'ERROR';
	($this_acc, $this_acc_str) = &$fn(@ary) if $log_status eq 'OK';
	$this_acc = 0 if !$this_acc; $this_acc_str = 'OK' if !$this_acc_str;

	return ($this_acc, $this_acc_str);
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


#############################################################################
#############################################################################
#   Function: replace_accents
#
#       Es: Reemplaza acentos en una cadena
#       En: Replace accents in string
#
#
#    Created on: 2013-09-09
#
#    Author: Alejandro Diaz
#
#    Modifications:
#
#        - Modified on **: 
#
#   Parameters:
#
#		str: Original string
#	
#  Returns:
#
#		str: Procecessed string
#
#   See Also:
#
#
#
sub replace_accents{
#############################################################################
#############################################################################
  	use utf8;
	my ($str) = @_;
	if ($str ne ''){		
		utf8::decode($str);

	    $str =~ s/À/A/g;
	    $str =~ s/à/a/g;
	    $str =~ s/È/E/g;
	    $str =~ s/è/e/g;
	    $str =~ s/Ì/I/g;
	    $str =~ s/ì/i/g;
	    $str =~ s/Ò/O/g;
	    $str =~ s/ò/o/g;
	    $str =~ s/Ù/U/g;
	    $str =~ s/ù/u/g;

	    $str =~ s/Á/A/g;
	    $str =~ s/á/a/g;
	    $str =~ s/É/E/g;
	    $str =~ s/é/e/g;
	    $str =~ s/Í/I/g;
	    $str =~ s/í/i/g;
	    $str =~ s/Ó/O/g;
	    $str =~ s/ó/o/g;
	    $str =~ s/Ú/U/g;
	    $str =~ s/ú/u/g;

	    $str =~ s/Ü/U/g;
	    $str =~ s/ü/u/g;
	    $str =~ s/Ñ/N/g;
	    $str =~ s/ñ/n/g;
	    
	    ## Specials Chars FEDEX
	    $str =~ s/\°//g;
	    $str =~ s/\|//g;
	    $str =~ s/\¬//g;
	    $str =~ s/\#//g;
	    $str =~ s/\%//g;
	    $str =~ s/\&//g;
	    $str =~ s/\(//g;
	    $str =~ s/\)//g;
	    $str =~ s/\[//g;
	    $str =~ s/\]//g;
	    $str =~ s/\-//g;

	    $str =~ s/\"//g;
	}

    return $str;

}

sub is_enum {
# --------------------------------------------------------
	my ($tbl_col) = @_;
	my (@ary);
	my ($enum_detected) = 0;
	my ($tbl_name,$col_name);
	my $sth;

	@fields = split(/\./, $tbl_col);
	# &cgierr($tbl_col.'->'.$#fields.'->'.$fields[0].'->'.$fields[1]);
	if ($tbl_col =~ '.' and $#fields == 1 ){
		$tbl_name = $fields[0];
		$col_name = $fields[1];

		
 
		$sth = (!$in{'second_conn'}) ? 
		  &Do_SQL("SELECT COUNT(*) AS count  FROM information_schema.tables  WHERE table_schema = '". $cfg{'dbi_db'} ."'  AND table_name = '". $tbl_name ."';")
		: &Do_SQL("SELECT COUNT(*) AS count  FROM information_schema.tables  WHERE table_schema = '". $cfg{'dbi_db'} ."'  AND table_name = '". $tbl_name ."';",1);
		
		my($is_valid_table) = $sth->fetchrow_array(); 
		
		if ($is_valid_table){
			###### Load Table Properties
			$sth = (!$in{'second_conn'})? &Do_SQL("describe $tbl_name $col_name;"): &Do_SQL("describe $tbl_name $col_name;",1);
			while (@ary = $sth->fetchrow_array() ) {
				push(@db_cols,$ary[0]);
				$ary[0] = lc($ary[0]);
				if ($ary[1] =~ /enum\((.*)/i){
					$enum_detected = 1;
				}
			}
		}
	}
	
	
	return $enum_detected;
}

############################################################################################
############################################################################################
#	Function: is_text
#   	Indica si el parametro recibido corresponde a un campo de texto valido en las tablas del Sistema
#
#	Created by:
#		24-09-2014::Ing. Alejandro Diaz
#
#	Modified By:
#
#   	Parameters:
#
#   	Returns:
#
#   	See Also:
#
sub is_text {
############################################################################################
############################################################################################

	my ($tbl_col) = @_;
	my (@ary);
	my ($enum_detected) = 0;
	my ($tbl_name,$col_name);
	my $sth;

	@fields = split(/\./, $tbl_col);
	if ($tbl_col =~ '.' and $#fields == 1 ){
		$tbl_name = $fields[0];
		$col_name = $fields[1];

		$sth = (!$in{'second_conn'}) ? 
		  &Do_SQL("SELECT COUNT(*) AS count  FROM information_schema.tables  WHERE table_schema = '". $cfg{'dbi_db'} ."'  AND table_name = '". $tbl_name ."';")
		: &Do_SQL("SELECT COUNT(*) AS count  FROM information_schema.tables  WHERE table_schema = '". $cfg{'dbi_db'} ."'  AND table_name = '". $tbl_name ."';",1);
		
		my($is_valid_table) = $sth->fetchrow_array(); 
		
		if ($is_valid_table){
			###### Load Table Properties
			$sth = (!$in{'second_conn'})? &Do_SQL("describe $tbl_name $col_name;"): &Do_SQL("describe $tbl_name $col_name;",1);
			while (@ary = $sth->fetchrow_array() ) {
				push(@db_cols,$ary[0]);
				$ary[0] = lc($ary[0]);
				if ($ary[1] =~ /char\((.*)/i or $ary[1] =~ /varchar\((.*)/i or $ary[1] =~ /tinytext\((.*)/i or $ary[1] =~ /text\((.*)/i or $ary[1] =~ /mediumtext\((.*)/i or $ary[1] =~ /longtext\((.*)/i){
					$enum_detected = 1;
				}
			}
		}
	}
	return $enum_detected;
}


#############################################################################
#############################################################################
#   Function: memcached_delete
#
#       Es: Elimina una llave de cache
#       En: Deletes cache key
#
#
#    Created on: 01/14/2014 09:55:44
#
#    Author: _RB_
#
#    Modifications:
#
#
#   Parameters:
#
#		- $key
#
#
#  Returns:
#
#      - 
#
#   See Also:
#
#		<>
#
#
sub memcached_delete {
#############################################################################
#############################################################################

	my ($key, $sql, $flush) = @_;

	if($cfg{'memcached'}){

		###
		### Memcached
		###

		if($flush){

			### Borramos todos los keys
			$va{'cache'}->flush_all;

		}elsif($key =~ /_\d{1,}-/ or $key =~ /^e\d{1,2}_(call)?\d{1,}-/){
		
			### Borramos el key guardado en cache
			$va{'cache'}->delete($key);

		}elsif($key =~ /^(Asterisk_Overflow)_\d/){
		
			### Borramos el key guardado en cache (Asterisk)
			$va{'cache'}->delete($key);

		}

	}

}


#############################################################################
#############################################################################
#   Function: table_exists
#
#       Es: Devuelve 1 si la tabla existe, cero si no existe
#       En: Returns 1 if table exists, zero otherwise
#
#
#    Created on: 04/30/2015 17:55:44
#
#    Author: _RB_
#
#    Modifications:
#
#
#   Parameters:
#
#		- $table
#
#
#  Returns:
#
#      - 
#
#   See Also:
#
#		<>
#
#
sub table_exists {
#############################################################################
#############################################################################
	
	my ($this_table) = @_;

	my (%tmp);
	my $table_exists = 0;
	my $cache_flag = 0;

	if( $cfg{'memcached'} ){

		###
		##  Memcache Data
		###
		(%tmp) = %{$va{'cache'}->get('e' . $in{'e'} . '_' .$this_table)};
		$table_exists = $tmp{'exists'};

	}

	if(!$tmp{'is_cached'} ){

		## Result is not cached yet
		$cache_flag = 1 if $cfg{'memcached'};

		my ($sth) = &Do_SQL("SHOW TABLES LIKE '". &filter_values($this_table) ."';");
		$table_exists = $sth->rows();

		$tmp{'is_cached'} = 1;
		$tmp{'exists'} = $table_exists;
		$tmp{'table_name'} = $this_table;

	}else{

		$tmp{'is_cached'} = 2;

	}

	## Set Memcached if flag activated 
	$va{'cache'}->set('e' . $in{'e'} . '_' .$this_table,\%tmp) if $cache_flag;
	#$va{'str'} = qq|Tabla: |. $tmp{'table_name'} .qq|<br>
	#		Cachada: |. $tmp{'is_cached'} .qq|<br>
	#		Existe: |. $tmp{'exists'} .qq|<br>|;

	return $table_exists;

}


#############################################################################
#############################################################################
#   Function: table_field_exists
#
#       Es: Devuelve 1 si el campo de la tabla existe, cero si no existe
#       En: Returns 1 if table column exists, zero otherwise
#
#
#    Created on: 12/01/2015 17:55:44
#
#    Author: _RB_
#
#    Modifications:
#
#
#   Parameters:
#
#		- $table
#
#
#  Returns:
#
#      - 
#
#   See Also:
#
#		<>
#
#
sub table_field_exists {
#############################################################################
#############################################################################
	
	my ($this_table, $this_field) = @_;
	my ($sth) = &Do_SQL("SELECT COUNT(*) FROM information_schema.COLUMNS WHERE TABLE_SCHEMA = '". &filter_values($cfg{'dbi_db'}) ."' AND TABLE_NAME = '". &filter_values($this_table) ."' AND COLUMN_NAME = '". &filter_values($this_field) ."';");
	my ($table_field_exists) = $sth->fetchrow();

	return $table_field_exists;

}

#############################################################################
#############################################################################
#   Function: table_to_json
#
#       Es: Devuelve los resultados de un select simple en formateo JSON

#
#
#    Created on: 18/07/2016
#
#    Author: Ing Fabian Cañaveral
#
#    Modifications:
#
#
#   Parameters:
#
#		- tableName obligatorio
#		- fields opcional
#		- where opcional
#
#
#  Returns:
#
#      - 
#
#   See Also:
#
#		<>
#
#
sub table_to_json{
#############################################################################
#############################################################################
	use JSON;
	use Data::Dumper;
	my $tableName = shift;
	my $fields = shift or '*';
	my $where = shift or ' 1 ';
	my @results = ();
	if(!$tableName){
		return "{}";
	}
	$rs = &Do_SQL("SELECT $fields FROM $tableName WHERE 1 AND $where");
	while($rec = $rs->fetchrow_hashref()){
		push @results, $rec;
	}
	return encode_json \@results;
}

#############################################################################
#############################################################################
#   Function: enum_to_json
#
#       Es: Devuelve enum en formateo JSON

#
#
#    Created on: 18/07/2016
#
#    Author: Ing Fabian Cañaveral
#
#    Modifications:
#
#
#   Parameters:
#
#		- tableName obligatorio
#		- field obligatorio
#		- where opcional
#
#
#  Returns:
#
#      - 
#
#   See Also:
#
#		<>
#
#
sub enum_to_json{
#############################################################################
#############################################################################
	use JSON;
	use Data::Dumper;
	my $tableName = shift;
	my $fields = shift;
	my @results = ();
	if(!$tableName or !fields){
		return "{}";
	}
	@rs = &load_enum_toarray($tableName,$fields);
	for my $el (@rs){
		my %r = ('Id'=>$el, 'Name'=>$el);
		push @results, \%r;
	}
	return encode_json \@results;
}

#############################################################################
#############################################################################
#       Function: get_call_center_agents_list
#
#       Es: Obtiene el listado de usuarios a su cargo
#       En: 
#
#       Created on: 12/10/2016
#
#       Author: ISC Alejandro Diaz
#       
#       
#       
#       
sub get_call_center_agents_list {
#############################################################################
#############################################################################

    my $agents_list = '';

    ## Se anula cambio temporalmente
    if (1 == 2){
    # if ($cfg{'use_admin_users_tree'} and $cfg{'use_admin_users_tree'}==1){
	    my ($sth) = &Do_SQL("SELECT 
	    (SELECT count(*) FROM cu_admin_users_tree WHERE ID_admin_users2 = ".$usr{'id_admin_users'}." )AS 'Supervisor',
	    (SELECT count(*) FROM cu_admin_users_tree WHERE ID_admin_users3 = ".$usr{'id_admin_users'}." )AS 'Coordinator'");
		my ($supervisor, $coordinator) = $sth->fetchrow_array();

		if ($supervisor) {
			$add_sql = ($supervisor)? " AND ID_admin_users2 = ".$usr{'id_admin_users'}:" AND ID_admin_users3 = ".$usr{'id_admin_users'};
			$sth = &Do_SQL("SELECT GROUP_CONCAT(DISTINCT ID_admin_users) FROM cu_admin_users_tree WHERE 1 ".$add_sql." ;");
			($list) = $sth->fetchrow_array();
			$agents_list .= $usr{'id_admin_users'};
			$agents_list .= ($list ne '')? ','.$list : '';
		}

    }

	return $agents_list;
}

sub in_array{

     my ($arr,$search_for) = @_;
     my %items = map {$_ => 1} @$arr;
     return (exists($items{$search_for}))?1:0;
}

##################################################################
#     CGIERR   	#
##################################################################
sub cgierr {
# --------------------------------------------------------
# Last Modified on: 11/10/08 12:13:39
# Last Modified by: MCC C. Gabriel Varela S: Se corrige la forma de mostrar la fecha
	my (@sys_err) = @_;
	print "Content-type: text/html\n\n";

	my ($key,$env,$out_in,$out_env);
	if (!$cfg{'cd'}){
		print qq|
					<head>
						<title>CGI - ERROR</title>
					</head>					
					<body BGCOLOR="#FFFFFF" LINK="#FF0000" VLINK="#FF0000" ALINK="#FF0000">
							<table BORDER="0" WIDTH="500" CELLPADDING="10" CELLSPACING="10">
							  <tr>
							    <td BGCOLOR="#FF0000" colspan="2"><font size="5" color="#FFFFFF" face="Arial"><b>CGI-Error</b></font></td>
							  </tr>
							</table>
							<table BORDER="0" WIDTH="550" CELLPADDING="2" CELLSPACING="0">|;
								$sys_err[0]	and print "\n<tr>\n  <td valign='top' width='200'><font face='Arial' size='3'>Error Message</font></td>\n  <td><font face='Arial' size='3' color='#FF0000'><b>$sys_err[0]</b></font></td>\n</tr>\n";
								$sys_err[1]	and print "<tr>\n  <td width='200'><font face='Arial' size='2'>Error Code</font></td>\n  <td><font face='Arial' size='2'>$sys_err[1]</font></td>\n";
								$sys_err[2]	and print "<tr>\n  <td valign='top' width='200'><font face='Arial' size='2'>System Message</font></td>\n  <td><font face='Arial' size='2'>$sys_err[2]</font></td>\n";
								print qq|
							<tr>
							  <td colspan="2"><p>&nbsp</p><font face='Arial' size='2'>If the problem percist, please contact us with the above Information.</font><br>
									<font face='Arial' size='2'><a href="mailto:$systememail">$systememail</a></font></td>
							</tr>
						</table>
					</body>
				</html>|;
		######################################
		### Save CGI ERR			
		##############################
		my ($ip);
		my (@outmsg) = @sys_err;
		my ($sec, $min, $hour, $day, $mon, $year, $dweek, $dyear, $daylight) = localtime(time());
		$year+=1900;
		$mon++;
		my ($time,$date) = ("$hour:$min:$sec","$mon-$day-$year");

		foreach $key (sort keys %in) {
			$outmsg[3] .= "$key=$in{$key},";
		}

		foreach $env (sort keys %ENV) {
			$outmsg[4] .= "$env=$ENV{$env},";
		}

		for (0..4){
			$outmsg[$_] =~ s/\n|\r/ /g;
			$outmsg[$_] =~ s/\|/ /g;
		}

		if ($ENV{'REMOTE_ADDR'}){
			$ip = $ENV{'REMOTE_ADDR'};
		}elsif ($ENV{'REMOTE_HOST'}){
			$ip = $ENV{'REMOTE_HOST'};
		}elsif ($ENV{'HTTP_CLIENT_IP'}){
			$ip = $ENV{'HTTP_CLIENT_IP'};
		}else{
			$ip = "Unknow";
		}

		if (open (LOG, ">>$cfg{'cgierr_log_file'}")){;
			print LOG "$usr{'username'}|$outmsg[0]|$outmsg[1]|$outmsg[2]|$outmsg[3]|$outmsg[4]|$time|$date|$ip\n";
			close AUTH;
		}


	}else{

		if( $cfg{'oper_mode'} eq 'updating' ){
			print &build_page('mode_updating.html');
			return;
		}

		my $print;
		$print .= "<PRE>\n\nCGI ERROR\n==========================================\n";
					$sys_err[0]	and $print .= "Error Message       : $sys_err[0]\n";
					$sys_err[1]	and $print .= "Error Code          : $sys_err[1]\n";
					$sys_err[2]	and $print .= "System Message      : $sys_err[2]\n";
					$0			and $print .= "Script Location     : $0\n";
					$]			and $print .= "Perl Version        : $]\n";
					$sid		and $print .= "Session ID          : $sid\n";


		$print .= "\nForm Variables IN\n-------------------------------------------\n";
		
		foreach $key (sort keys %in) {
			my $space = " " x (20 - length($key));
			$out_in .= "$key=$in{$key},";
			$print .= "$key$space: $in{$key}\n";
		}
		
		$print .= "\nForm Variables ERROR\n-------------------------------------------\n";
		foreach $key (sort keys %error) {
			my $space = " " x (20 - length($key));
			$print .= "$key$space: $error{$key}\n";
		}
		
		$print .= "\nEnvironment Variables\n-------------------------------------------\n";
		foreach $env (sort keys %ENV) {
			my $space = " " x (20 - length($env));
			$out_env .= "$env=$ENV{$env},";
			$print .= "$env$space: $ENV{$env}\n";
		}
		
		$print .= "\n</PRE>";

		## Encrypt message
		use MIME::Base64;
		$va{'cgierr_msg'} = $cfg{'debug_cgierr_mode_on'} ?
								"<PRE>".$print."</PRE>" :
								"<PRE>".encode_base64($print)."</PRE>";
		
		if($cfg{'raw_cgierr'}){
			print $print;
		}elsif($ENV{'REQUEST_METHOD'} eq 'GET' or $ENV{'REQUEST_METHOD'} eq 'POST') {
			print &build_page('cgierr.html');
		}else{
			print $print;
		}

		if ($cfg{'debug_cgierr'} and $cfg{'debug_cgierr'}==1 and $cfg{'team_direksys_email'} ne ''){
			my (@email) = split(/\,/, $cfg{'team_direksys_email'});
            for my $i(0..$#email){
            	&send_mandrillapp_email_attachment($cfg{'from_email_info'},$email[$i],"CGIERR->$in{'e'}:$cfg{'app_title'}->$usr{'application'}->$in{'cmd'}","$print","none","none");
            }
		}

	}

	exit -1;
}

1;