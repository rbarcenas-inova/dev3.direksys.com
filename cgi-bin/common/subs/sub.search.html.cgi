#!/usr/bin/perl

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
##			Viewing				##
##########################################################
sub html_search_select {
# --------------------------------------------------------
 	if(!&check_permissions($in{'cmd'},'_view','')){ &html_unauth; return; };
	
	if ($in{'search'} eq 'lprint' or $in{'search'} eq 'export'){

		$in{'nh'} = 1; ## Start always in the first page
		$in{'f'} = 1 if (!$in{'f'});

		if ($in{'search'} eq 'export'){
			
			$usr{'pref_maxh'} = 30 if !$usr{'pref_maxh'};
			$usr{'pref_maxh'} *= 100;

			if ($in{'e'}){

				$func = 'export_er_'.$in{'cmd'};  ## This Replace the Standard Function
				if (defined &$func){
					&$func();
					return;
				}else{
					$func = 'export_eb_'. $in{'cmd'};  ## This is an Addition the Standard Function
					if (defined &$func){
						&$func();  ## Does notaccept $out_params
					}

					
					$func = 'export_'. $in{'cmd'};## This is the standard Function

					if (defined &$func){
						($numhits, @hits) = &$func();  
					}else{
						($numhits, @hits) = &query($in{'db'});
					}

				}
			}else{

				$func = 'export_'. $in{'cmd'};## This is the standard Function

				if (defined &$func){
					($numhits, @hits) = &$func();  
				}else{
					($numhits, @hits) = &query($in{'db'});
				}
			}
			
			if ($numhits >0){

				#print "Content-type: text/html\n\n";
				print "Content-Type: text/csv\n";
				print "Content-disposition: attachment; filename=".$in{'cmd'}."_".&get_date().".csv\n\n";
				&txt_export_success($numhits,@hits);
				return;

			}
			
		}else{
			if ($in{'e'}){
				$func = 'plist_er_'.$in{'cmd'};  ## This Replace the Standard Function
				if (defined &$func){
					&$func();
					return;
				}else{
					$func = 'plist_eb_'. $in{'cmd'};  ## This is an Addition the Standard Function
					if (defined &$func){
						&$func();  ## Does notaccept $out_params
					}
					$func = 'plist_'. $in{'cmd'};## This is the standard Function
					if (defined &$func){
						($numhits, @hits) = &$func();  
					}else{
						($numhits, @hits) = &query($in{'db'});
					}
				}
			}else{
				$func = 'plist_'. $in{'cmd'};## This is the standard Function
				if (defined &$func){
					($numhits, @hits) = &$func();  
				}else{
					($numhits, @hits) = &query($in{'db'});
				}
			}
			if ($numhits >0) {
				$va{'tpage'} = round($numhits/$usr{'pref_maxh'},0);				
				if ($in{'f'} > 2 and $sys{'db_'.$in{'cmd'}.'_lprn'.$in{'f'}}){
					@headerfields = split(/,/, $sys{'db_'.$in{'cmd'}.'_lprn'.$in{'f'}}) ;
				}

				print "Content-type: text/html\n\n";
				$va{'page'} = 1;
				&html_lprint_success($numhits,@hits);
				if ($va{'tpage'}>1){
					for (2..$va{'tpage'}){
						$in{'nh'} = $_;
						$va{'searchresults'} = '';
						my ($numhits, @hits) = &query($in{'db'});
						print "<span style='page-break-before: always'></span>";
						&html_lprint_success($numhits,@hits);
					}
				}
				return;
			}
		}
		$va{'message'}= &trans_txt('search_nomatches');
		print "Content-type: text/html\n\n";
		print &build_page('toprint_msg.html');
		return;
		
	}elsif ($in{'search'} eq "List All" or $in{'search'} eq "listall"){
	
		my ($numhits, @hits);	
		&run_function("presearch");
		$in{'listall'} = 1;
		
		$func = 'plist_er_'.$in{'cmd'};  ## This Replace the Standard Function
		if (defined &$func){
			($numhits, @hits) = &$func();
		}else{
			($numhits, @hits) = &query($in{'db'});
		}

		if ($numhits >0) {
			&html_view_success($numhits,@hits);
		}else{
			&html_view_failure;
		}
	}elsif ($in{'search'} eq "Search" ){
		&run_function("presearch");
		my ($numhits, @hits) = &query($in{'db'});
		if ($numhits ==1) {
			$in{'view'} = $hits[0];
			&html_view_record;
		}elsif($numhits >0) {
			&html_view_success($numhits,@hits);
		}else {
			&html_view_failure;
		}
	}elsif ($in{'search'} eq "advSearch"){
		&run_function("preadvsearch");
		my ($numhits, @hits,$func);
		if ($in{'e'}){
			$func = 'advsearch_er_'.$in{'cmd'};  ## This Replace the Standard Function
			if (defined &$func){
				($numhits, @hits) = &$func();
			}else{
				$func = 'advsearch_eb_'. $in{'cmd'};  ## This is an Addition the Standard Function
				if (defined &$func){
					&$func();  ## Does notaccept $out_params
				}
				$func = 'advsearch_'. $in{'cmd'};## This is the standard Function
				if (defined &$func){
					($numhits, @hits) = &$func();  
				}else{
					($numhits, @hits) = &query($in{'db'});
				}
			}
		}else{
			$func = 'advsearch_'. $in{'cmd'};## This is the standard Function
			if (defined &$func){
				($numhits, @hits) = &$func();  
			}else{
				($numhits, @hits) = &query($in{'db'});
			}
		}

		if ($numhits == 1) {
			if($in{'show_only_list'} && $in{'show_edit_list'}) {
				&html_view_success($numhits,@hits);
			} else {
				&load_cfg($in{'db'});
				$in{'view'} = $hits[0];
				&html_view_record;
			}#JRG 17-06-2008
		}elsif($numhits >0) {
			&html_view_success($numhits,@hits);
		}else {
			&html_view_failure;
		}
		
	}elsif ($in{'search'} eq "form" ){
		&html_search_form;
	}elsif ($in{'search'} eq "Print" ){
		&html_print;
	}elsif ($in{'search'} eq "Report" ){
		&html_print_report;
	}elsif ($in{'search'} eq "advform" ){
		&html_advsearch_form;	
 	}else{
		&html_view_search;
	}
	&run_eafunction('search');
}


##########################################################
##			Viewing				##
##########################################################
sub html_search_form {
# --------------------------------------------------------
# Last Modified on: 11/08/10 13:51:33
# Last Modified by: MCC C. Gabriel Varela S: Se arregla para evaluar en base a $usr, etc.
	### Print Page
	print "Content-type: text/html\n\n";
	
	my ($fname) = $cfg{'path_templates'}."/mod/".$usr{'application'}."/".$in{'cmd'} ."_search.html";
	$fname =~ s/\[lang\]/$usr{'pref_language'}/gi;
	if (-e "$fname"){
		print &build_page($in{'cmd'}.'_search.html');
	}else{
		print &build_page('template_search.html');
	}
}

sub html_advsearch_form {
# --------------------------------------------------------
# Last Modified on: 11/08/10 13:52:57
	### Print Page
	print "Content-type: text/html\n\n";
	
	my ($fname) = $cfg{'path_templates'}."/mod/".$usr{'application'}."/".$in{'cmd'} ."_advsearch.html";
	$fname =~ s/\[lang\]/$usr{'pref_language'}/gi;
	if (-e "$fname"){
		print &build_page($in{'cmd'}.'_advsearch.html');
	}else{
		print &build_page('template_advsearch.html');
	}

}

sub html_view_search {
# --------------------------------------------------------
	#$va{'searchresults'} = &trans_txt("searcherror");
	
	### Print Page
	print "Content-type: text/html\n\n";
	$va{'message'} = &trans_txt("searcherror");
	my ($fname) = $cfg{'path_templates'}."/mod/".$usr{'application'}."/".$in{'cmd'} ."_list.html";
	$fname =~ s/\[lang\]/$usr{'pref_language'}/gi;
	if (-e "$fname"){
		print &build_page($in{'cmd'}.'_list.html');
	}else{
		print &build_page('template_list.html');
	}
}


sub html_view_success {
# --------------------------------------------------------
# Last Modified on: 02/17/09 11:08:28
# Last Modified by: MCC C. Gabriel Varela S: Se pone funci?n para mostrar cookies guardadas
# Last Modified on: 02/23/09 16:26:05
# Last Modified by: MCC C. Gabriel Varela S: Se agrega columna de favoritos
# Last Modified on: 02/25/09 12:04:42
# Last Modified by: MCC C. Gabriel Varela S: Se da formato a la fila de favoritos, se cambian por links los inputs
# Last Modified on: 02/26/09 13:32:09
# Last Modified by: MCC C. Gabriel Varela S: Se corrige el view para show_only_list
# Last Modified on: 09/16/09 11:09:45
# Last Modified by: MCC C. Gabriel Varela S: Se habilita cookie para multi compa??a
#Last modified on 2 Nov 2010 17:06:48
#Last modified by: MCC C. Gabriel Varela S. :Se habilita template de nuevo look
#Last modified on 15 Aug 2011 15:57:58
#Last modified by: MCC C. Gabriel Varela S. :second_conn is considered
	## Loading Custom List
	my ($numhits,@hits) = @_;	

	&run_function("list");

	($sys{'db_'.$in{'cmd'}.'_listonly'} eq 'enable') and ($in{'show_only_list'}=1);
	
	
	my (%tmp, $qs, $add_title);
	my (@c) = split(/,/,$cfg{'srcolors'});
	my (@g) = split(/,/,$cfg{'srcolorsv'});
	my ($rows) = ($#hits+1)/($#db_cols+1);
	my $rowsviewed=&GetCookies("$in{'db'}$in{'e'}");


	for (0 .. $rows-1) {
		
		$d = 1 - $d;
		%tmp = &array_to_hash($_, @hits);
		
		my $color="$c[$d]";
		my $iddb=$in{'db'},$favorites;
		$iddb=~s/sl_/id_/g;
		for (0..$#headerfields){
			if (lc($headerfields[$_]) =~/$iddb/){
				if($rowsviewed=~/$tmp{$headerfields[$_]}/){
					$color="$g[$d]";
				}
				&get_favorites("$in{'db'}$in{'e'}",$tmp{$headerfields[$_]});
				$favorites="	<!--td valign='top' nowrap-->
						<img name='bookmarkred$tmp{$headerfields[$_]}' src='$va{'imgurl'}/app_bar/small_bookmarksred$va{'bookmarkred'}.gif' title='red' alt='red' border='0' onmouseover='m_over(this)' onmouseout='m_out(this)' onclick=\"setCookie('".$in{'db'}.$in{'e'}."red',$tmp{$headerfields[$_]},365,'red');\"><!--br /-->
							<img name='bookmarkgreen$tmp{$headerfields[$_]}' src='$va{'imgurl'}/app_bar/small_bookmarksgreen$va{'bookmarkgreen'}.gif' title='green' alt='green' border='0' onmouseover='m_over(this)' onmouseout='m_out(this)' onclick=\"setCookie('".$in{'db'}.$in{'e'}."green',$tmp{$headerfields[$_]},365,'green');\"><!--br /-->
							<img name='bookmarkblue$tmp{$headerfields[$_]}' src='$va{'imgurl'}/app_bar/small_bookmarksblue$va{'bookmarkblue'}.gif' title='blue' alt='blue' border='0' onmouseover='m_over(this)' onmouseout='m_out(this)' onclick=\"setCookie('".$in{'db'}.$in{'e'}."blue',$tmp{$headerfields[$_]},365,'blue');\">
		<!--/td-->\n";
			}
		}
		
		my $conn_type=0;
		if($in{'second_conn'}){
			$conn_type=1;
		}else{
			$conn_type=0;
		}
		
		if (!$in{'show_only_list'}){
			$page .= qq|
			<tr onmouseover='m_over(this)' onmouseout='m_out(this)' bgcolor='$color'>
				
    		<td  valign='top' nowrap>
     		<a href="/cgi-bin/mod/$usr{'application'}/dbman?cmd=$in{'cmd'}&view=$tmp{$db_cols[0]}&second_conn=$conn_type"><img name="view_$tmp{$db_cols[0]}" src='$va{'imgurl'}/$usr{'pref_style'}/view.png' title='view' alt='view' width="20" height="20" border='0'></a>
				<a href="/cgi-bin/mod/$usr{'application'}/dbman?cmd=$in{'cmd'}&modify=$tmp{$db_cols[0]}&second_conn=$conn_type"><img name="edit_$tmp{$db_cols[0]}" src='$va{'imgurl'}/$usr{'pref_style'}/edit.png' title='edit' alt='edit' width="20" height="20" border='0'></a>
				<input type="image" src="$va{'imgurl'}/$usr{'pref_style'}/delete.png" name="del__$tmp{$db_cols[0]}" value="|.&trans_txt('btn_del').qq|" onclick="notest=false;return;" width="15" height="15" style="border:none">
				<br />$favorites</td>|;
		}elsif($in{'show_edit_list'}){ #modified to show list and edit JRG 05-05-2008
			$page .= qq|
			<tr onmouseover='m_over(this)' onmouseout='m_out(this)' bgcolor='$color' >
				<td nowrap><a href="/cgi-bin/mod/$usr{'application'}/dbman?cmd=$in{'cmd'}&modify=$tmp{$db_cols[0]}&second_conn=$conn_type"><img name="edit_$tmp{$db_cols[0]}" src='$va{'imgurl'}/$usr{'pref_style'}/edit.png' title='edit' alt='edit' width="15" height="15" border='0'></a><br>$favorites</td>|;
		}else{
			$page .= qq|
			<tr onmouseover='m_over(this)' onmouseout='m_out(this)' bgcolor='$color' >
				<td nowrap><a href="/cgi-bin/mod/$usr{'application'}/dbman?cmd=$in{'cmd'}&view=$tmp{$db_cols[0]}&second_conn=$conn_type"><img name="view_$tmp{$db_cols[0]}" src='$va{'imgurl'}/$usr{'pref_style'}/view.png' title='view' alt='view' width="15" height="15" border='0'></a><br>$favorites</td>|;
				
		}		

		for (0..$#headerfields){

			if ($headerfields[$_] =~ /^(\w{2})_([^:]+)->([^\.]+)/){
				## tbl_name->field_id 1)DB  2)ID
				$page .= "	<td valign='top'>".$tmp{$3}."</td>\n";
			}elsif ($headerfields[$_] =~ /^(\w{2})_([^:]+):([^\.]+)\.([^\.]+)/){
				## tbl_name:field_id.field_name 1)DB  2)ID  3)Name
				$page .= "	<td valign='top'><a href='".&build_link("$1_$2",$4,$tmp{$3})."' class='error'>". &load_name("$1_$2","ID_$2",$tmp{$3},$4) ."</a></td>\n";
			}elsif($headerfields[$_] =~ /^admin_users:([^\.]+)\.([^\.]+)/){
				## tbl_name:field_id.field_name 1)DB  2)ID  3)Name
				$page .= "	<td valign='top'><a href='".&build_link("admin_users",$2,$tmp{$1})."' class='error'>". &load_name("admin_users","ID_admin_users",$tmp{$1},$2) ."</a></td>\n";
			}elsif($db_valid_types{lc($headerfields[$_])} eq "date"){
				$page .= qq|	<td align="center" nowrap valign='top'>| . &sql_to_date($tmp{$headerfields[$_]}) . qq|&nbsp;</td>\n|;
			}elsif($db_valid_types{lc($headerfields[$_])} eq "currency"){
				$page .= qq|	<td align="right" nowrap valign='top'>| . &format_price($tmp{$headerfields[$_]}) . qq|&nbsp;</td>\n|;
			}elsif ($db_valid_types{lc($headerfields[$_])} eq "numeric"){
				$page .= qq|	<td align="right" nowrap valign='top'>| . &format_number($tmp{$headerfields[$_]}) . qq|&nbsp;</td>\n|;
			}elsif($db_valid_types{lc($headerfields[$_])} =~ /function:(.*)/){
				my ($fcmd) = $1;
				if (defined &$fcmd){
					$page .= qq|	<td valign='top'>$tmp{$headerfields[$_]}| . &$fcmd($tmp{$headerfields[$_]},$tmp{$headerfields[0]},$color) . qq|</td>\n|;
				}else{
					$page .= qq|	<td valign='top'>$tmp{$headerfields[$_]}&nbsp;</td>\n|;
				}
			}else{
				$tmp{$headerfields[$_]} =~ s/\n/<br>/g;
				$page .= qq|	<td valign='top'>$tmp{$headerfields[$_]}&nbsp;</td>\n|;
			}
		}
		
		my $id=$in{'db'};
		$id=~s/sl_/id_/g;
		#$page .= $favorites;
		$page .= "		</tr>";
	}
	$va{'searchresults'} = $page;
	($va{'pageslist'},$va{'qs'})  = &pages_list($in{'nh'},"$script_url",$numhits,$usr{'pref_maxh'});
	$va{'matches'}     = $numhits;

	print "Content-type: text/html\n\n";
	my ($fname) = $cfg{'path_templates'}."/mod/".$usr{'application'}."/".$in{'cmd'} ."_list.html";
	$fname =~ s/\[lang\]/$usr{'pref_language'}/gi;
	if (-e "$fname"){
		print &build_page($in{'cmd'}.'_list.html');
	}else{
		print &build_page('template_list.html');
	}	
	
	print "<SCRIPT language='JavaScript'>
	<!-- Begin
function movepic(img_name,img_src) {
document[img_name].src=img_src;
}
// End -->
	function setCookie(c_name,valuet,expiredays,color)
	{
		var exdate=new Date();
		var prevcont;
		prevcont=getCookie(c_name);
		var RegularExpression  =  new RegExp(valuet);
		var RegularExpression1  =  new RegExp('('+valuet+'\,?)','ig');
		if(prevcont.match(RegularExpression))
		{
			prevcont=prevcont.replace(RegularExpression1,'');
			movepic('bookmark'+color+valuet,'$va{'imgurl'}/app_bar/small_bookmarks'+color+'off.gif');
		}
		else
		{
			prevcont+=valuet+',';
			movepic('bookmark'+color+valuet,'$va{'imgurl'}/app_bar/small_bookmarks'+color+'on.gif');
		}
		exdate.setDate(exdate.getDate()+expiredays);
		document.cookie=c_name+ '=' +prevcont+
		((expiredays==null) ? '' : ';expires='+exdate.toGMTString())+';path=/;';
	}
	function getCookie(c_name)
	{
		if (document.cookie.length>0)
		  {
			  c_start=document.cookie.indexOf(c_name + '=');
			  if (c_start!=-1)
		    { 
			    c_start=c_start + c_name.length+1; 
			    c_end=document.cookie.indexOf(';',c_start);
			    if (c_end==-1) c_end=document.cookie.length;
			    return unescape(document.cookie.substring(c_start,c_end));
		    } 
		  }
		return '';
	}
	<!-- This script and many more are available free online at -->
<!-- The JavaScript Source!! http://javascript.internet.com -->
</SCRIPT>";
}
#"

#############################################################################
#############################################################################
# Function: txt_export_success
#
# Es: Imprime las lineas de la busqueda al archivo xls
# En: 
#
# Created on: 1/23/2013 6:46:39 PM
#
# Author: Carlos Haas
#
# Modifications:
# 
# 				Last Modification by _RB_ : Se agrega if para datos tipo sl_table->ID_field
#
# Parameters:
#
#
# Returns:
#
#
# See Also:
#
#  Todo:
#
sub txt_export_success{
#############################################################################
#############################################################################

	if(!&check_permissions($in{'cmd'},'_export','')){ &html_smallunauth; return; };
	my ($numhits,@hits) = @_;
	my (%tmp, $qs, $add_title,$line,@hary);
	my ($rows) = ($#hits+1)/($#db_cols+1);	
	
	if ($in{'f'} > 1 and $sys{'db_'.$in{'cmd'}.'_expo'.$in{'f'}}){
		@headerfields = split(/,/, $sys{'db_'.$in{'cmd'}.'_expo'.$in{'f'}}) if ($sys{'db_'.$in{'cmd'}.'_expo'.$in{'f'}});
		### Headers
		if ($sys{'db_'.$in{'cmd'}.'_expo'.$in{'f'}.'_'.$usr{'pref_language'}}){
			@hary = split(/,/,$sys{'db_'.$in{'cmd'}.'_expo'.$in{'f'}.'_'.$usr{'pref_language'}});
		}else{
			@hary = split(/,/,$sys{'db_'.$in{'cmd'}.'_expo'.$in{'f'}});
		}
	}
	if ($in{'f'} eq 1 or $#headerfields<0){
		if ($sys{'db_'.$in{'cmd'}.'_list_'.$usr{'pref_language'}}){
			@hary = split(/,/,$sys{'db_'.$in{'cmd'}.'_list_'.$usr{'pref_language'}});
		}else{
			@hary = split(/,/,$sys{'db_'.$in{'cmd'}.'_list'});
		}

	}

	## Print Headers
	$line = '';
	for my $i(0..$#hary){
		($i==0 and $hary[$i]=~ /^ID/) and ($hary[$i] = 'ID');
		$line .= '"'.$hary[$i].'",';
	}
	chop($line);
	print "$line\r\n"; 			
	
	## Loading Custom List,

	for (0 .. $rows-1) {
		$d = 1 - $d;
		%tmp = &array_to_hash($_, @hits);
		$line = '';
		for (0..$#headerfields){
			
			if($headerfields[$_] =~ /^\w{2}_[^:]+->([^\.]+)/){
				$line .= '"'.$tmp{$1}.'",';
			}elsif ($headerfields[$_] =~ /^(\w{2})_([^:]+):([^\.]+)\.([^\.]+)/){
				## tbl_name:field_id.field_name 1)DB  2)ID  3)Name
				$line .= '"'.&load_name("$1_$2","ID_$2",$tmp{$3},$4) .'",';
			}elsif($headerfields[$_] =~ /^admin_users:([^\.]+)\.([^\.]+)/){
				## tbl_name:field_id.field_name 1)DB  2)ID  3)Name
				$line .=  '"'.&load_name("admin_users","ID_admin_users",$tmp{$1},$2) .'",';
			
			}elsif($db_valid_types{lc($headerfields[$_])} eq "date"){
				$line .= '"'.&sql_to_date($tmp{$headerfields[$_]}) .'",';
			}elsif($db_valid_types{lc($headerfields[$_])} eq "currency"){
				$line .= '"'.&format_price($tmp{$headerfields[$_]}) .'",';
			}elsif ($db_valid_types{lc($headerfields[$_])} eq "numeric"){
				$line .= '"'.&format_number($tmp{$headerfields[$_]}) .'",';
			}elsif($db_valid_types{lc($headerfields[$_])} =~ /function:(.*)/){
				my ($fcmd) = $1;
				if (defined &$fcmd){
					$line .= '"'.&$fcmd($tmp{$headerfields[$_]},$tmp{$headerfields[0]},$c[$d]) .'",';
				}else{
					$line .= '"'.$tmp{$headerfields[$_]}.'",';
				}
			}else{
				$tmp{$headerfields[$_]} =~ s/\n/<br>/g;
				$line .= '"'.$tmp{$headerfields[$_]}.'",';
			}
		}
		chop($line);
		print "$line\r\n"; 
	}
	
}

sub html_lprint_success {
# --------------------------------------------------------
	if(!&check_permissions($in{'cmd'},'_lprint','')){ &html_smallunauth; return; };

	## Loading Custom List
	my ($numhits,@hits) = @_;
	my (%tmp, $qs, $add_title,$page);
	my ($rows) = ($#hits+1)/($#db_cols+1);
	for (0 .. $rows-1) {
		$d = 1 - $d;
		%tmp = &array_to_hash($_, @hits);
		
		$page .= qq| <tr>\n\n|;
		for (0..$#headerfields){
			if ($headerfields[$_] =~ /^(\w{2})_([^:]+):([^\.]+)\.([^\.]+)/){
				## tbl_name:field_id.field_name 1)DB 2)ID 3)Name
				$page .= " <td valign='top'>". &load_name("$1_$2","ID_$2",$tmp{$3},$4) ."</td>\n";
			}elsif($headerfields[$_] =~ /^admin_users:([^\.]+)\.([^\.]+)/){
				## tbl_name:field_id.field_name 1)DB 2)ID 3)Name
				$page .= " <td valign='top'>". &load_name("admin_users","ID_admin_users",$tmp{$1},$2) ."</td>\n";
			
			}elsif($db_valid_types{lc($headerfields[$_])} eq "date"){
				$page .= qq| <td align="center" nowrap valign='top'>| . &sql_to_date($tmp{$headerfields[$_]}) . qq|&nbsp;</td>\n|;
			}elsif($db_valid_types{lc($headerfields[$_])} eq "currency"){
				$page .= qq| <td align="right" nowrap valign='top'>| . &format_price($tmp{$headerfields[$_]}) . qq|&nbsp;</td>\n|;
			}elsif ($db_valid_types{lc($headerfields[$_])} eq "numeric"){
				$page .= qq| <td align="right" nowrap valign='top'>| . &format_number($tmp{$headerfields[$_]}) . qq|&nbsp;</td>\n|;
			}elsif($db_valid_types{lc($headerfields[$_])} =~ /function:(.*)/){
				my ($fcmd) = $1;
				if (defined &$fcmd){
					$page .= qq| <td valign='top'>$tmp{$headerfields[$_]}| . &$fcmd($tmp{$headerfields[$_]},$tmp{$headerfields[0]},$c[$d]) . qq|</td>\n|;
				}else{
					$page .= qq| <td valign='top'>$tmp{$headerfields[$_]}&nbsp;</td>\n|;
				}
			}else{
				$tmp{$headerfields[$_]} =~ s/\n/<br>/g;
				$page .= qq| <td valign='top'>$tmp{$headerfields[$_]}&nbsp;</td>\n|;
			}
		}
		$page .= " </tr>";
	}
	$va{'searchresults'} = $page;
	$va{'matches'} = $numhits;
	
	my ($fname) = $cfg{'path_templates'}."/print/lprint/".$sys{'db_'.$in{'cmd'}.'_form'} ."_plist$in{'f'}.html";
	$fname =~ s/\[lang\]/$usr{'pref_language'}/gi;
	if (-e "$fname"){
		print &build_page($sys{'db_'.$in{'cmd'}.'_form'}.'_plist'.$in{'f'}.'.html');
	}else{
		print &build_page('template_plist'.$in{'f'}.'.html');
	}

}

sub html_view_failure {
# --------------------------------------------------------
#Last modified on 2 Nov 2010 17:47:11
#Last modified by: MCC C. Gabriel Varela S. :Se incorpora nuevo look
	## Loading Custom List
	&run_function("list");
	my ($colspan) = $#headerfields+2;
	$va{'matches'}     = 0;
	$va{'pageslist'} = 0;
	$colspan++;
	$va{'searchresults'} = qq|
		<tr>
			<td align="center" colspan="$colspan" class='stdtxterr'><p>&nbsp;</p>| . &trans_txt('search_nomatches') . qq|<p>&nbsp;</p></td>
		</tr>\n|;
	print "Content-type: text/html\n\n";
	my ($fname) = $cfg{'path_templates'}."/mod/".$usr{'application'}."/".$in{'cmd'} ."_list.html";
	$fname =~ s/\[lang\]/$usr{'pref_language'}/gi;
	if (-e "$fname"){
		print &build_page($in{'cmd'}.'_list.html');
	}else{
		print &build_page('template_list.html');
	}

}


##################################################################
#########               VIEW RECORD                        #######
##################################################################
sub html_view_record {
# --------------------------------------------------------
# Last Modified on: 02/17/09 11:08:09
# Last Modified by: MCC C. Gabriel Varela S: Se pone funci?n para guardar cookies
# Last Modified on: 02/23/09 10:14:43
# Last Modified by: MCC C. Gabriel Varela S: Se pone referencia de ventana de listas y favoritos
# Last Modified on: 09/16/09 11:02:18
# Last Modified by: MCC C. Gabriel Varela S: Se habilitan cookies para multi compa??a
#Last modified on 28 Oct 2010 17:43:56
#Last modified by: MCC C. Gabriel Varela S. : Se incluye template de view

	if(!&check_permissions($in{'cmd'},'_view','')){ &html_unauth; return; };
	my ($cache_res, $cache_exp);

	if($cfg{'memcached'} and $cfg{'memcached_dbman'} ){

		###
		### Memcached
		##

	    ## Buscamos la informacion en cache
		#$cache->delete($in{'db'} . '_' . $in{'view'});
		(%rec) = %{$va{'cache'}->get('e' . $in{'e'} . '_' .$in{'db'} . '_' . $in{'view'})};

		if(!$rec{lc($db_cols[0])}){

	    	$cache_exp = $cfg{'memcached_exp'} ? $cfg{'memcached_exp'} : 28800;
	    	(%rec) = &get_record($db_cols[0],$in{'view'},$in{'db'});
			
			if ( !$va{'cache'}->set('e' . $in{'e'} . '_' .$in{'db'} . '_' . $in{'view'},\%rec) ){	
				
				$cache_res = '0';

			}else{

				$cache_res = '1';

			}

		}else{

			$cache_res = '2';

		}


	}else{

		###
		### No Cached
		###
		(%rec) = &get_record($db_cols[0],$in{'view'},$in{'db'});
		$cache_res = '-';

	}


	if (!$rec{lc($db_cols[0])}){ 

		$va{'message'} = &trans_txt("searcherror");
		$in{'search'}  = 'listall';
		&html_search_select;
		return;

	}

	foreach my $key (sort keys %rec) {

		$in{lc($key)} = $rec{$key};
		($db_valid_types{lc($key)} ne 'html') and ($in{lc($key)} =~ s/\n/<br>/g);

	}

	#	&cgierr("..".$sys{'db_mer_products_menu'}."--".$va{'expanditem'});
	&run_function("view"); ## Borra $va{'expanditem'}


	## User Info
	&get_db_extrainfo('admin_users',$in{'id_admin_users'});
	
	## Save Log
	&auth_logging2($in{'cmd'}.'_viewed',"$in{lc($db_cols[0])}");
	$idf=$in{'db'};
	$idf=~s/sl_/id_/g;
	&write_cookie("$in{'db'}$in{'e'}",$in{$idf},$cfg{'expcookie'},"add");

	print "Content-type: text/html\n\n";
	print "cr: $cache_res";

	if ($in{'frameview'}){

		my ($fname) = $cfg{'path_templates'}."/mod/".$usr{'application'}."/".$in{'cmd'} ."_fview.html";
		$fname =~ s/\[lang\]/$usr{'pref_language'}/gi;
		if (-e "$fname"){
			print &build_page($in{'cmd'}.'_fview.html');
		}else{
			print &build_page('template_fview.html');
		}

	}else{

		my $cadlist,$id,$db;
		$db=$in{'db'};
		$id=$db;
		$id=~s/sl_/id_/g;
		$cadlist="<!-- lists -->
			<div id='lists_windows' style='visibility: hidden; display: none; background-color: #ffffff;'>
				<div class='menu_bar_title' id='lists_drag'>
				<img id='lists_exit' src='$va{'imgurl'}/$usr{'pref_style'}/popupclose.gif'>
				&nbsp;&nbsp;&nbsp;List Manager
				</div>
				<div class='formtable'>
				<IFRAME SRC='/cgi-bin/common/apps/ajaxbuild?ajaxbuild=manage_lists&id=$in{$id}&db=$db&table=$db&path=/cgi-bin/mod/$usr{'application'}/dbman&cmdo=$in{'cmd'}&id_admin_users=$usr{'id_admin_users'}' name='rcmd' TITLE='Recieve Commands' width='446' height='320' FRAMEBORDER='0' MARGINWIDTH='0' MARGINHEIGHT='0' SCROLLING='auto'>
				<H2>Unable to do the script</H2>
				<H3>Please update your Browser</H3>
				</IFRAME>	
				</div></div>";

		my ($fname) = $cfg{'path_templates'}."/mod/".$usr{'application'}."/".$in{'cmd'} ."_view.html";
		$fname =~ s/\[lang\]/$usr{'pref_language'}/gi;
		if (-e "$fname"){
			print &build_page($in{'cmd'}.'_view.html');
		}else{
			print &build_page('template_view.html');
		}

	}
}

sub html_view_record_failure {
# --------------------------------------------------------
	$va{'message'} = &trans_txt("searcherror");
	$in{'search'}='listall';
	&html_search_select;
}

##########################################################
##			Search Options 				##
##########################################################

sub html_print {
# --------------------------------------------------------
	## Validación de permisos de impresion
	if (!&check_permissions($in{'cmd'},'_print','')){ &html_smallunauth; return; };

	print "Content-type: text/html\n\n";
	(!$in{'custom_print_header'} and $in{'cmd'} ne 'fin_banks_movements') and (print &build_page('header_print.html'));
	my ($page,%rec,@pcols);
	@pcols = @db_cols;
	my (@ary) = split(/,/,$in{'toprint'});
	for my $i(0..$#ary){
		if ($ary[$i]>0){
			@db_cols = @pcols;
			my (%rec) = &get_record($db_cols[0],$ary[$i],$in{'db'});
			if ($rec{lc($db_cols[0])}){
				foreach my $key (sort keys %rec) {
					$in{lc($key)} = $rec{$key};
					($db_valid_types{lc($key)} ne 'html') and ($in{lc($key)} =~ s/\n/<br>/g);
				}
			
				## User Info
				&get_db_extrainfo('admin_users',$in{'id_admin_users'});
				if ($in{'tab'} and $in{'tabcmd'} and -e "../common/tabs/$in{'tabcmd'}.cgi"){
					require ("../common/tabs/$in{'tabcmd'}.cgi");
					print &print_tabs;
				}else{
					&run_function("view");
					my ($fname);
					$in{'f'} = int($in{'f'});
					if (!$in{'f'}){
						delete($in{'f'});
					}
					#$fname = $cfg{'path_templates'}."/print/dbman/".$sys{'db_'.$in{'cmd'}.'_form'} ."$in{'f'}.html";
					#$fname =~ s/\[lang\]/$usr{'pref_language'}/gi;
					#if (-e "$fname"){
						print &build_page("print:$sys{'db_'.$in{'cmd'}.'_form'}$in{'f'}.html");
						#print &build_page("print/dbman/$sys{'db_'.$in{'cmd'}.'_form'}$in{'f'}.html");
					#}else{
						# TODO: No funciona para imprimir bien cuando no hay templates
						
						#print &build_custom_viewfields($va{'page_title'},join(',',@db_cols));
					#}
				}
			}
		}
		if ($ary[$i+1]>0){
			print '<div style="page-break-before:always"></div>';
		}
	}
	print qq|
</body>
</html>\n|;

}



1;

