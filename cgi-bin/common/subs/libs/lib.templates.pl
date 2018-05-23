sub build_custom_formfields {
# --------------------------------------------------------
	my ($title,$dbfields) = @_;
	my (@fnames, $headers,$output,$error,$js_output);
	@fnames = split(/,/,$dbfields);
	FN: for my $i(0 .. $#fnames) {
		if ($fnames[$i] eq '---'){
			$output .= "			<tr>\n			  <td colspan='2'>&nbsp;</td>\n			</tr>\n";
		}elsif($fnames[$i] =~ /^_(.*)/){
			$output .= "			<tr>\n			  <td colspan='2'>$1</td>\n			</tr>\n";
		}else{
			$fname = lc($fnames[$i]);
			if ($fname =~ /^date$|^time$|^id_admin_users$/ or ($in{'add'} and $db_valid_types{$fname} eq 'PRIMARY')){
				next FN;
			}elsif($db_valid_types{$fname} eq 'PRIMARY' and !$in{'add'}){
				$output .= &build_customform_idfield($title,$fname,$in{'cmd'});
			}else{
				if(!$headers){
					$headers =1;
					$output  .= qq|	&nbsp;
							<fieldset><legend>$title</legend>
							<table border="0" cellspacing="0" cellpadding="2" width="100%">\n|;
				}
				$output  .= "<tr>\n";
				if ($fname =~ /id_(.*)/ and $i==0){
					$output  .= "<td width='30%'>ID : <span class='smallfieldterr'>$error{$fname}</span>$error{$fname}</td>\n";
				}else{
					my($str) = $fname;
					$str =~ s/_/ /g;
					$output  .= "<td width='30%'>".ucfirst($str)." :  <span class='smallfieldterr'>$error{$fname}</span></td>\n";
				}
				#### Build Field
				if ($db_valid_types{$fname} eq 'date'){
					$output .= "<td><input id='$fname' size='20' name='$fname' value='$in{$fname}' onFocus='focusOn( this )' onBlur='focusOff( this )'>&nbsp;								    <script language='javascript'>\n<!--\n\n$(document).ready(function() {\n\n$(document).ajaxError(function(e, xhr, settings, exception) {\nalert('error in: ' + settings.url + ' \n'+'error:\n' + xhr.responseText );\n});\n\nvar dates = $( '#$fname' ).datepicker({\ndateFormat: 'yy-mm-dd',\ndefaultDate: '-2m',\nmaxDate: new Date(),\nchangeMonth: true,\nnumberOfMonths: 3,\n});\n\n});\n//-->\n</script>\n				</td>\n";
				}elsif($db_valid_types{$fname} eq 'selection'){
					$output  .= "<td>".&build_select_field($fname,$in{$fname})."</td>\n";
					$js_output .= "chg_select('$fname','".&filter_values($in{$fname})."');\n";
				}elsif($db_valid_types{$fname} eq 'radio'){
					$output  .= "<td>".&build_radio_field($fname,$in{$fname})."</td>\n";
					$js_output .= "chg_radio('$fname','".&filter_values($in{$fname})."');\n";
				}elsif($db_valid_types{$fname} eq 'checkbox'){
					$output  .= "<td>".&build_checkbox_field($fname,$in{$fname})."</td>\n";
					my ($str) = $in{$fname};
					$str =~ s/,/|/g;
					$js_output .= "chg_chkbox('$fname','".&filter_values($str)."');\n";
				}elsif($db_valid_types{$fname} eq 'text'){
					my ($cols,$rows);
					$cols = $1; ($cols=20) unless ($cols>0);
					$rows = $2; ($rows=20) unless ($rows>0);
					$output  .= "<td><textarea rows='5' cols='10' style='width: 100%;' name='$fname' onFocus='focusOn( this )' onBlur='focusOff( this )'>$in{$fname}</textarea></td>\n"
				}else{
					$output .= "<td><input type='text' name='$fname' value='$in{$fname}' size='$db_valid_length{$fname}' onFocus='focusOn( this )' onBlur='focusOff( this )'></td>\n";
				}
				
				$output .= "</tr>\n";
			}
		}
	}
	$output .= "</table>\n	</fieldset>\n	&nbsp;" if ($headers);
	if ($js_output){
		$output .= qq|
		<script language="javascript">
		$js_output
		</script>\n|;
	}
	return $output;
}

sub build_custom_viewfields {
# --------------------------------------------------------
# Last time Modified by RB on 12/07/2011: Se agrega variable para ejecutar acciones extras de ser necesario en cada elemento con el nombre $va{'chg_[nombreelemento]'}

	my ($title,$dbfields) = @_;
	my (@fnames, $headers,$output);
	
	@fnames = split(/,/,$dbfields);
	FN: for my $i(0 .. $#fnames) {
		if ($fnames[$i] eq '---'){
			$output .= "			<tr>\n			  <td colspan='2'>&nbsp;</td>\n			</tr>\n";
		}elsif($fnames[$i] =~ /^_(.*)/){
			$output .= "			<tr>\n			  <td colspan='2'>$1</td>\n			</tr>\n";
		}else{
			$fname = lc($fnames[$i]);
			if ($fname =~ /^date$|^time$|^id_admin_users$/){
				next FN;
			}elsif($db_valid_types{$fname} eq 'PRIMARY'){
				$output .= &build_custom_idfield($title,$fname,$in{'cmd'});
			}elsif($fname =~ /^status$/){
				if ($headers){
					$headers = 0;
					$output .= "</table>\n	</fieldset>\n	&nbsp;";
				}
				$output .= qq|	&nbsp;
				     <fieldset><legend>$title Status</legend>
					<table border="0" cellspacing="0" cellpadding="2" width="100%">
				  		<tr>
						    <td width="30%">Status  :</td>
						    <td class="smalltext" id='td_status'><span id='span_status'>[in_status]</span> [va_chg_status]</td>
						 </tr>
				  	</table>
					</fieldset>\n|
			}else{
				if(!$headers){
					$headers =1;
					$output  .= qq|	&nbsp;
							<fieldset><legend>$title</legend>
							<table border="0" cellspacing="0" cellpadding="2" width="100%">\n|;
				}
				$output  .= "<tr>\n";
				$output  .= "<td width='30%'>".ucfirst($fname)."</td>\n";
				## Colspan & field name
				if ($db_valid_types{$fname} eq 'email'){
					$output .= "<td class='smalltext'><a href='mailto:'$in{$fname}'>$in{$fname}</td>\n";
				}else{
					$output  .= "<td class='smalltext' id='td_".$fname."'><span id='span_".$fname."'>$in{$fname}</span> [va_chg_".$fname."]</td>\n"
				}
				
				$output .= "</tr>\n";
			}
		}
	}
	$output .= "</table>\n	</fieldset>\n	&nbsp;" if ($headers);
	return $output;
}

sub build_custom_idfield {
# --------------------------------------------------------
	my ($title,$fname,$cmd) = @_;
	&get_user_info($in{'id_admin_users'});
	my ($output) = qq|
	&nbsp;
	<fieldset><legend>$title</legend>
	<table border="0" cellspacing="0" cellpadding="2" width="100%">
		<tr>
			<td width="30%" class="titletext">$title ID : </td>
			<td class="titletext">$in{$fname} &nbsp;|;
	if (!$in{'toprint'}){
		if ($va{'form_view'} and !$sys{'db_'.$in{'cmd'}.'_listonly'}){
			$output .= qq|
				<a href="/cgi-bin/mod/$usr{'application'}/dbman?cmd=$cmd&modify=$in{$fname}"><img src='[va_imgurl]/[ur_pref_style]/b_edit.gif' title='Edit' alt='' border='0'></a>
		  	    <a href="javascript:prnwin('/cgi-bin/mod/$usr{'application'}/dbman?cmd=$cmd&search=Print&toprint=$in{$fname}')"><img src='[va_imgurl]/[ur_pref_style]/b_print.gif' title='Print' alt='' border='0'></a>\n|;
		}elsif($va{'form_edit'} and !$sys{'db_'.$in{'cmd'}.'_listonly'}){
			$output .= qq|
				<a href="/cgi-bin/mod/$usr{'application'}/dbman?cmd=$cmd&view=$in{$fname}"><img src='[va_imgurl]/[ur_pref_style]/b_view.gif' title='Edit' alt='' border='0'></a>
		  	    <a href="javascript:prnwin('/cgi-bin/mod/$usr{'application'}/dbman?cmd=$cmd&search=Print&toprint=$in{$fname}')"><img src='[va_imgurl]/[ur_pref_style]/b_print.gif' title='Print' alt='' border='0'></a>\n|;
		}elsif($sys{'db_'.$in{'cmd'}.'_listonly'}){
			$output .= qq|
		  	    <a href="javascript:prnwin('/cgi-bin/mod/$usr{'application'}/dbman?cmd=$cmd&search=Print&toprint=$in{$fname}')"><img src='[va_imgurl]/[ur_pref_style]/b_print.gif' title='Print' alt='' border='0'></a>\n|;
		}
	}
	$output .= qq|
			</td>
		</tr>
		<tr>
			<td width="30%" class="smalltext">Date / Time /user  : </td>
			<td class="smalltext">[in_date] [in_time] &nbsp; Created by : ([in_id_admin_users]) [in_admin_users.firstname] [in_admin_users.lastname]</td>
		</tr>		
	</table>
	</fieldset>\n|;
	
	return $output;
}

sub build_customform_idfield {
# --------------------------------------------------------
	my ($title,$fname,$cmd) = @_;
	&get_user_info($in{'id_admin_users'});
	my ($output) = qq|
			&nbsp;
			<fieldset><legend>$title</legend>
			<table border="0" cellspacing="0" cellpadding="2" width="100%">
				<tr>\n|;
	if (!$in{'search'}){
		$output .= qq|
			<td width="30%" class="titletext">$title ID : </td>
			<td class="titletext">$in{$fname} &nbsp;\n|;
		if (!$sys{'db_'.$in{'cmd'}.'_listonly'}){
			$output .= qq|<a href="/cgi-bin/mod/$usr{'application'}/dbman?cmd=$cmd&view=$in{$fname}"><img src='[va_imgurl]/[ur_pref_style]/b_view.gif' title='View' alt='' border='0'></a>\n|;
		}
		$output .= qq|<a href="javascript:prnwin('/cgi-bin/mod/$usr{'application'}/dbman?cmd=$cmd&search=Print&toprint=$in{$fname}')"><img src='[va_imgurl]/[ur_pref_style]/b_print.gif' title='Print' alt='' border='0'></a>\n|;
	}else{
		$output .= qq|<td width="30%" class="titletext">$title ID : </td>\n|;
		$output .= "<td><input type='text' name='$fname' value='$in{$fname}' size='30' onFocus='focusOn( this )' onBlur='focusOff( this )'></td>\n";	
	}
	$output .= qq|
		</tr>
		<tr>
			<td width="30%" class="smalltext">Date / Time /user  : </td>
			<td class="smalltext">[in_date] [in_time] &nbsp; Created by : ([in_id_admin_users]) [in_admin_users.firstname] [in_admin_users.lastname]</td>
		</tr>\n| if (!$in{'search'});
	$output .= "	</table>\n	</fieldset>\n";
	
	return $output;
}


sub template_listheaders{
# --------------------------------------------------------
	my (@ary, $output, $des_url);
	if ($sys{'db_'.$in{'cmd'}.'_list_'.$usr{'pref_language'}}){
		@ary = split(/,/,$sys{'db_'.$in{'cmd'}.'_list_'.$usr{'pref_language'}});
	}else{
		@ary = split(/,/,$sys{'db_'.$in{'cmd'}.'_list'});
	}
	my (@ary_fields) = split(/,/,$sys{'db_'.$in{'cmd'}.'_list'});
	for my $i(0..$#db_cols){
		$des_url .= '&'.lc($db_cols[$i]).'='.$in{lc($db_cols[$i])} if ($in{lc($db_cols[$i])});
	}

	for my $i(0..$#ary){
		($i==0 and $ary[$i]=~ /^ID/) and ($ary[$i] = 'ID');
		if ($in{'sb'} eq $ary_fields[$i] and $in{'so'} eq 'DESC'){
			$output .= qq|<td class="menu_bar_title">$ary[$i] <a href='/cgi-bin/mod/$usr{'application'}/dbman?cmd=$in{'cmd'}&sb=$ary_fields[$i]&so=ASC$des_url'><img src='[va_imgurl]/[ur_pref_style]/arr.up.gif'></a></td>\n|;
		}elsif($in{'sb'} eq $ary_fields[$i]){
			$output .= qq|<td class="menu_bar_title">$ary[$i] <a href='/cgi-bin/mod/$usr{'application'}/dbman?cmd=$in{'cmd'}&sb=$ary_fields[$i]&so=DESC$des_url'><img src='[va_imgurl]/[ur_pref_style]/arr.down.gif'></a></td>\n|;
		}else{
			$output .= qq|<td class="menu_bar_title" onmouseover="m_over(this)" onmouseout="m_out(this)" OnClick="trjump('/cgi-bin/mod/$usr{'application'}/dbman?cmd=$in{'cmd'}&sb=$ary_fields[$i]&so=DESC$des_url')">$ary[$i] </td>\n|;
		}
	}
	return $output;
}

sub template_idbutton{
# --------------------------------------------------------
	if ($sys{'db_'.$in{'cmd'}.'_listonly'}){
		return '';
	}elsif ($in{'view'}){
		return qq|<a href="/cgi-bin/mod/$usr{'application'}/dbman?cmd=[in_cmd]&modify=[in_$db_cols[0]]"><img src='[va_imgurl]/[ur_pref_style]/b_edit.gif' title='Edit' alt='' border='0'></a>|;
	}else{
		return qq|<a href="/cgi-bin/mod/$usr{'application'}/dbman?cmd=[in_cmd]&view=[in_$db_cols[0]]"><img src='[va_imgurl]/[ur_pref_style]/b_view.gif' title='View' alt='' border='0'></a>|;
	}
}

sub template_prnbutton{
# --------------------------------------------------------
	## ToDO: Revisar permisos (Solo de View), vercuantos templates hay disponibles, si hay mas de 1 llamar a ventana en Ajax
	## Si hay uno directo se puede llamar.
	## 21/08/2014:AD:Se agrega multimodo para Formatos de Impresion
	my ($output,$c);

	if(&check_permissions($in{'cmd'},'_print','')){	
		(!$sys{'db_'.$in{'cmd'}.'_prntemp'}) and ($sys{'db_'.$in{'cmd'}.'_prntemp'} = $sys{'db_'.$in{'cmd'}.'_form'});
		my (@ary) = split(/,/, $sys{'db_'.$in{'cmd'}.'_prntemp'});
		use Data::Dumper;
		if ($#ary >= 1){
			my $ow = 0;
			
			my $fname = $cfg{'path_templates'}.'print/dbman/';
			$fname =~ s/\[lang\]/$usr{'pref_language'}/gi;
			for my $i(0..$#ary){

				## cortar normal o por puntos
				if ($ary[$i] =~ m/\::/){
					my @arr_tmpl = split /\::/ , $ary[$i];
					$ow = $arr_tmpl[0];
					$ary[$i] = $arr_tmpl[1];
				}

				#######
				####### rw_ sirve para sobreescribir las variables y mandar a ejecutar diferente comando
				my $rw_cmd = $va{'cmd' . ($i+1)} ? $va{'cmd' . ($i+1)} : "[in_cmd]";
				my $rw_toprint = $va{'toprint' . ($i+1)} ? $va{'toprint' . ($i+1)} : "$in{lc($db_cols[0])}";
				my $rw_f = ($va{'f' . ($i+1)}) ? $va{'f' . ($i+1)} : (($ow)? $ow : ($i+1));

				if ((-e $fname.$sys{'db_'.$in{'cmd'}.'_form'}.'.html' or -e $fname.$sys{'db_'.$in{'cmd'}.'_form'}.'.e'.$in{'e'}.'.html') and $i eq 0){
					$output .= " <a href=\"javascript:prnwin('/cgi-bin/mod/$usr{'application'}/dbman?cmd=[in_cmd]&search=Print&toprint=$in{lc($db_cols[0])}')\" class=menu>$ary[$i]</a>\n";
					++$c;
				}elsif ((-e $fname.$sys{'db_'.$in{'cmd'}.'_form'}.($i+1).'.html' or -e $fname.$sys{'db_'.$in{'cmd'}.'_form'}.($i+1).'.e'.$in{'e'}.'.html') and $i>0){
					$output .= " <a href=\"javascript:prnwin('/cgi-bin/mod/$usr{'application'}/dbman?cmd=".$rw_cmd."&search=Print&toprint=".$rw_toprint."&f=".$rw_f."')\" class=menu>$ary[$i]</a>\n";
					++$c;
				}
			}

			if ($c>1){
				$output = qq|<a href="/" class="anchorclass modulo" style="display: inline;" rel="submenu3[click]">
			<img src='[va_imgurl]/[ur_pref_style]/b_print.gif' title='Print' alt='' border='0'>
			</a>
			 <div id="submenu3" class="anylinkcsscols">
				<div class="column">
				$output
			<img src="$va{'imgurl'}app_bar/mod/menushadowfin.png">
	    </div>
	  </div>\n|;
			}elsif ($c eq 1){
				$output = qq|<a href="javascript:prnwin('/cgi-bin/mod/$usr{'application'}/dbman?cmd=[in_cmd]&search=Print&toprint=$in{lc($db_cols[0])}')"><img src='[va_imgurl]/[ur_pref_style]/b_print.gif' title='Print' alt='' border='0'></a>|;
			}
		}
		if (!$output){
			$output = qq|<a href="javascript:prnwin('/cgi-bin/mod/$usr{'application'}/dbman?cmd=[in_cmd]&search=Print&toprint=$in{lc($db_cols[0])}')"><img src='[va_imgurl]/[ur_pref_style]/b_print.gif' title='Print' alt='' border='0'></a>|;
		}
	}
	return $output;
}

sub template_lprnbutton{
# --------------------------------------------------------
	my ($output,$fname,$x);
	## ALWAYS  1)Width Headers,2)No Headers
	##

	if(&check_permissions($in{'cmd'},'_lprint','')){

		my (@ary) = split(/,/, &trans_txt('base_plist').','.$sys{'db_'.$in{'cmd'}.'_lprntemp'});
		$fname = $cfg{'path_templates'}.'/print/lprint/'.$sys{'db_'.$in{'cmd'}.'_form'}.'_plist';
		$fname =~ s/\[lang\]/$usr{'pref_language'}/gi;

		my $qs = $va{'qs'};
		$qs =~ s/cmd=\w+|search=\w+//g;
	
		for my $i(0..$#ary){
			if ($ary[$i]){
				++$x;
				if ($x>2){
					if (-e $fname.$x.'.html' or -e $fname.$x.'.e'.$in{'e'}.'.html'){
						$output .= " <a href=\"javascript:prnwin('/cgi-bin/mod/$usr{'application'}/dbman?cmd=[in_cmd]&search=lprint&$qs&f=".($x)."')\" class=menu>$ary[$i]</a>\n";
					}
				}else{
					$output .= " <a href=\"javascript:prnwin('/cgi-bin/mod/$usr{'application'}/dbman?cmd=[in_cmd]&search=lprint&$qs&f=".($x)."')\" class=menu>$ary[$i]</a>\n";
				}
			}
		}
	
		$output = qq|
		<a href="/" class="anchorclass modulo" style="display: inline;" rel="submenu3[click]">
		<img src='[va_imgurl]/[ur_pref_style]/b_print.png' title='Print' alt='' border='0'>
		</a>
		 <div id="submenu3" class="anylinkcsscols">
			<div class="column">
					$output
				<img src="$va{'imgurl'}app_bar/mod/menushadowfin.png">
    		</div>
  		</div>\n|;
	
	}
	return $output;
	
}


sub template_exportbutton{
# --------------------------------------------------------
	## ToDO: Revisar permisos (Solo de View), vercuantos templates hay disponibles, si hay mas de 1 llamar a ventana en Ajax
	## Si hay uno directo se puede llamar.
	##
	my ($output,$c);

	if(&check_permissions($in{'cmd'},'_export','')){

		my (@ary) = split(/,/,$sys{'db_'.$in{'cmd'}.'_export'});

		if ($#ary >= 1){

			for my $i(0..$#ary){
				
				if ($ary[$i]){
					++$x;
					if ($x>1){
						
						if ($sys{'db_'.$in{'cmd'}.'_expo'.$x}){
							$output .= " <a href=\"javascript:trjump('/cgi-bin/mod/$usr{'application'}/dbman?cmd=[in_cmd]&view=[in_view]&export=1&f=".$x."')\" class=menu>$ary[$i]</a>\n";
							++$c;
						}
					}else{
						$output .= " <a href=\"javascript:trjump('/cgi-bin/mod/$usr{'application'}/dbman?cmd=[in_cmd]&view=[in_view]&export=1&f=".$x."')\" class=menu>$ary[$i]</a>\n";
						++$c;
					}
			
				}
			}

			if ($c >1){
				$output = qq|<a href="/" class="anchorclass modulo" style="display: inline;" rel="submenu4[click]">
							<img src='[va_imgurl]/[ur_pref_style]/b_xls.gif' width='24' height='24' title='Export' alt='' border='0'>
							</a>
							 <div id="submenu4" class="anylinkcsscols">
								<div class="column">
								$output
							<img src="$va{'imgurl'}app_bar/mod/menushadowfin.png">
					    </div>
					  </div>\n|;
	  		}else{
	  			return qq|<a href="javascript:trjump('[va_script_url]?cmd=[in_cmd]&view=[in_view]=export=1&f=1')"><img src='[va_imgurl]/[ur_pref_style]/b_xls.gif' title='Export' alt='' border='0'></a>|;
	  		}
	  	}
	}
	return $output;
}


sub template_expbutton{
# --------------------------------------------------------
	my ($output,$fname,$c);
#	if(&check_permissions($in{'cmd'},'_export','')){
#		return qq|<a href="javascript:prnwin('[va_script_url]?cmd=[in_cmd]&search=Print&toprint=[in_id_customers]')"><img src='[va_imgurl]/[ur_pref_style]/b_xls.gif' title='Export' alt='' border='0'></a>|;
#	}
	if(&check_permissions($in{'cmd'},'_export','')){
		
		my (@ary) = split(/,/, &trans_txt('base_xlist').','.$sys{'db_'.$in{'cmd'}.'_export'});

		my $qs = $va{'qs'};
		$qs =~ s/cmd=\w+|search=\w+//g;


		for my $i(0..$#ary){
			if ($ary[$i]){
				++$x;
				if ($x>1){
					
					if ($sys{'db_'.$in{'cmd'}.'_expo'.$x}){
						$output .= " <a href=\"javascript:trjump('/cgi-bin/mod/$usr{'application'}/dbman?cmd=[in_cmd]&search=export&$qs&f=".$x."')\" class=menu>$ary[$i]</a>\n";
						++$c;
					}
				}else{
					$output .= " <a href=\"javascript:trjump('/cgi-bin/mod/$usr{'application'}/dbman?cmd=[in_cmd]&search=export&$qs&f=".$x."')\" class=menu>$ary[$i]</a>\n";
					++$c;
				}
			}
		}
		
		if ($c >1){
			$output = qq|<a href="/" class="anchorclass modulo" style="display: inline;" rel="submenu3[click]">
		<img src='[va_imgurl]/[ur_pref_style]/b_xls.gif' title='Export' alt='' border='0'>
		</a>
		 <div id="submenu3" class="anylinkcsscols">
			<div class="column">
			$output
		<img src="$va{'imgurl'}app_bar/mod/menushadowfin.png">
    </div>
  </div>\n|;
  		}else{
  			return qq|<a href="javascript:trjump('[va_script_url]?cmd=[in_cmd]&search=export&$qs&f=1')"><img src='[va_imgurl]/[ur_pref_style]/b_xls.gif' title='Export' alt='' border='0'></a>|;
  		}
	}
	return $output;
}

sub template_idvalue{
# --------------------------------------------------------
	return $in{lc($db_cols[0])};
}

sub template_idname{
# --------------------------------------------------------
	return lc($db_cols[0]);
}

sub template_myprefsmenu{
# --------------------------------------------------------
		return $sys{'myprefsmenu'};
}

sub template_reportsmenu{
	#&cgierr($sys{'reportsmenu'});
# --------------------------------------------------------
	return $sys{'reportsmenu'};
}



sub template_toptabs{
# --------------------------------------------------------
	my ($output,$width,$onoff);
	$width = 3;
	($sys{'db_'.$in{'cmd'}.'_add'} eq 'disable') and ($width = 2);
	
	$output =qq|
	<table width="100%" border="0" cellspacing="0" cellpadding="0" class="tab" align="center">
	  <tr>
	    <td width="30%" align="center"></td>\n|;
	    
	    ### Home Tab & Add
	    ($in{'add'}) ? ($onoff = 'on'):($onoff = 'off');
	    my ($fname) = $cfg{'path_templates'}."/mod/".$usr{'application'}."/".$in{'cmd'} ."_home.html";
		$fname =~ s/\[lang\]/$usr{'pref_language'}/gi;
		if (-e "$fname"){
			$output .= qq|<td width="[va_toptablewidth]%" class="cell_off" align="center" onClick='trjump("/cgi-bin/mod/$usr{'application'}/admin?cmd=[in_cmd]_home")'>$va{'formtitle'}</td>\n|;
			$output .= qq|<td width="[va_toptablewidth]%" class="cell_$onoff" align="center" onClick='trjump("/cgi-bin/mod/$usr{'application'}/dbman?cmd=[in_cmd]&add=1")'>|.&trans_txt('tab_add').qq|</td>\n| if ($sys{'db_'.$in{'cmd'}.'_add'} ne 'disable');
			++$width;
		}else{
			$output .= qq|<td width="[va_toptablewidth]%" class="cell_$onoff" align="center" onClick='trjump("/cgi-bin/mod/$usr{'application'}/dbman?cmd=[in_cmd]&add=1")'>|.&trans_txt('tab_add').qq| [va_formtitle]</td>\n| if ($sys{'db_'.$in{'cmd'}.'_add'} ne 'disable');
		}
		## Standard Search
		($in{'search'} eq 'form') ? ($onoff = 'on'):($onoff = 'off');
		$output .= qq|<td width="[va_toptablewidth]%" class="cell_$onoff" align="center" onClick='trjump("/cgi-bin/mod/$usr{'application'}/dbman?cmd=[in_cmd]&search=form")'>|.&trans_txt('tab_search').qq|</td>\n|;
		
		## Advance Search
	    ($in{'search'} eq 'advform') ? ($onoff = 'on'):($onoff = 'off');
	    my ($fname) = $cfg{'path_templates'}."/mod/".$usr{'application'}."/".$in{'cmd'} ."_advsearch.html";
		$fname =~ s/\[lang\]/$usr{'pref_language'}/gi;
		if (-e "$fname"){
			$output .= qq|<td width="[va_toptablewidth]%" class="cell_$onoff" align="center" onClick='trjump("/cgi-bin/mod/$usr{'application'}/dbman?cmd=[in_cmd]&search=advform")'>|.&trans_txt('tab_advsearch').qq|</td>\n|;
			++$width;
		}
		## View/ Search Edit
		(($in{'view'} and !$in{'add'}) or $in{'modify'} or ($in{'search'} and $in{'search'} ne 'advform' and $in{'search'} ne 'form')) ? ($onoff = 'on'):($onoff = 'off');
	    $output .= qq|<td width="[va_toptablewidth]%" class='cell_$onoff' align='center' onClick='trjump("/cgi-bin/mod/$usr{'application'}/dbman?cmd=[in_cmd]&search=listall&so=DESC&sb=$db_cols[0]")'>|.&trans_txt('tab_ved').qq|</td>\n|;
	    
	    ## Width [3..5]
	    $va{'toptablewidth'}=int(70/$width);
	    
	    
	$output .= qq|
	  </tr>
	</table>\n|;
	return $output;
}

sub template_chgshptypebutton{
# --------------------------------------------------------

	my ($output);

	if ( &check_permissions('order_change_payment_type','','') and !$va{'cod_blocked'} ){

		## Batch validation
		my $response = &block_orders_in_batch($in{'id_orders'});
		my $orders_in_batch = ($response ne 'OK') ? 1 : 0;

		## To CC
		if (&is_cc_convertible($in{'id_orders'}) == 1 and $orders_in_batch == 0){
			$output .= " <a href=\"#\" onClick=\"return confirm_changeto_cc('[va_script_url]','[in_cmd]',[in_view]);\" class=menu>Change to Credit Card</a>\n";
		}	
		## To COD
		if (&changeto_cod($in{'id_orders'}) == 1 and !$in{'tocod'} and &check_permissions('edit_order_wholesale_ajaxmode','','')){
			$output .= " <a href=\"#\" class=menu onClick=\"return confirm_changeto_cod('[va_script_url]','[in_cmd]',[in_view]);\">Change to COD</a>\n";
		}	
		## To Referenced Deposit
		if (&check_permissions('change_order_toreferenced_deposit','','') and $orders_in_batch == 0){ #and $in{'ptype'} ne 'Referenced Deposit'
			$output .= " <a href=\"#\" onClick=\"return confirm_changeto_depositref('[va_script_url]','[in_cmd]',[in_view]);\" class=menu>Change to Referenced Deposit</a>\n";
		}
		## To WholeSale
		# if (&check_permissions('edit_order_cleanup','','')){
		# 	$output .= " <a href=\"#\" onClick=\"return confirm_changeto_wholesale('[va_script_url]','[in_cmd]',[in_view]);\" class=menu>Change to Wholesale</a>\n";
		# }

		if( $output ne '' ){
			$output = qq|<a href="/" class="anchorclass modulo" style="display: inline;" rel="submenu3[click]">
						<img src='[va_imgurl]/[ur_pref_style]/b_chpaytype.gif' title='Change Payment Type' alt='' border='0'>
						</a>
						 <div id="submenu3" class="anylinkcsscols">
							<div class="column">
							$output
						<img src="$va{'imgurl'}app_bar/mod/menushadowfin.png">
				    </div>
				  </div>\n|;
		}
		
	}	

	return $output;
}


1;