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
sub build_report_search {
# --------------------------------------------------------

	my($db,$fields_names,$fields)=@_;
	if ($in{'build'} = 'xrep'){
		### Special query
		my ($func) = "loadcfgs_" . $db;
		if (defined &$func){
			&$func(%tmp);
		}
	}else{
		&load_cfg($db);
	}
	my ($output,$sofields);
	my (@fields) = split(/,/,$fields);
	my (@names) = split(/,/,$fields_names);
	for (0..$#fields){
		### Fields Form
		if ($db_valid_types{lc($fields[$_])} eq 'date'){
			$output .= qq|
		<tr>
		   <td class='smalltext'>$names[$_]</td>
		   <td><input id="from_$fields[$_]" size="16" name="from_$fields[$_]" value="$in{'from_'.$fields[$_]}" onFocus='focusOn( this )' onBlur='focusOff( this )'>&nbsp;</td>
		   <td><input id="to_$fields[$_]" size="16" name="to_$fields[$_]" value="$in{'to_'.$fields[$_]}" onFocus='focusOn( this )' onBlur='focusOff( this )'>&nbsp;</td>
		   <td><input id="$fields[$_]" size="16" name="$fields[$_]" value="$in{$fields[$_]}" onFocus='focusOn( this )' onBlur='focusOff( this )'>&nbsp;

<script language='javascript'>
<!--
    
	$(document).ready(function() {

		/*AJAX Error handler*/
		$(document).ajaxError(function(e, xhr, settings, exception) {
			alert('error in: ' + settings.url + ' \n'+'error:\n' + xhr.responseText );
		});

		var dates = $( '#from_$fields[$_], #to_$fields[$_]' ).datepicker({
			dateFormat: 'yy-mm-dd',
			defaultDate: '-2m',
			minDate: new Date(2009,1-1,1),
			maxDate: new Date(),
			changeMonth: true,
			numberOfMonths: 3,
			onSelect: function( selectedDate ) {
				var option = this.id == 'from_$fields[$_]' ? 'minDate' : 'maxDate',
				instance = $( this ).data( 'datepicker' ),
				date = $.datepicker.parseDate(
					instance.settings.dateFormat \|\|
					$.datepicker._defaults.dateFormat,
					selectedDate, instance.settings );
				dates.not( this ).datepicker( 'option', option, date );
			}
		});
		
		var dates2 = $( '#$fields[$_]' ).datepicker({
			dateFormat: 'yy-mm-dd',
			defaultDate: '-2m',
			maxDate: new Date(),
			changeMonth: true,
			numberOfMonths: 3,
		});

	});

//-->
</script>
								    
								    </td>
		</tr>\n|;			
		}else{
			$output .= qq|
		<tr>
		   <td class='smalltext'>$names[$_] </td>
		   <td><input type="text" name="from_$fields[$_]" value="$in{'from_'.$fields[$_]}" size="20" onFocus='focusOn( this )' onBlur='focusOff( this )'></td>
		   <td><input type="text" name="to_$fields[$_]" value="$in{'to_'.$fields[$_]}" size="20" onFocus='focusOn( this )' onBlur='focusOff( this )'></td>
		   <td><input type="text" name="$fields[$_]" value="$in{$fields[$_]}" size="20" onFocus='focusOn( this )' onBlur='focusOff( this )'></td>
		</tr>\n|;
		}
		
		## Sort Order Fields
		$sofields .= "<option value='$fields[$_]'>$names[$_]</option>";
	}
	return ($output,$sofields);
}



sub build_report_header {
# --------------------------------------------------------
	my($header_title)=@_;
	my ($output) = "<tr>\n";
	
	my (@ary) = split(/,/,$header_title);
	for (0..$#ary){
		$output .= "<td class='menu_bar_title'>$ary[$_]</td>";
	}
	$output .= "</tr>\n";
	
	return $output;
}


sub build_report {
# --------------------------------------------------------
	my($db,$header_fields)=@_;
	&load_cfg($db);
	my ($page,$pageslist);
	
	### Special query
	my ($func) = "query_" . $db;
	if (defined &$func){
		%tmp = &$func(%tmp);
	}
	
	my ($numhits, @hits) = &query($db);
	my (@headerfields) = split(/,/,$header_fields);
	my ($func) = "report_" . $db;

	if ($numhits>0){
		my ($rows) = ($#hits+1)/($#db_cols+1);
		for (0 .. $rows-1) {
			%tmp = &array_to_hash($_, @hits);
			
			### Special fields
			if (defined &$func){
				%tmp = &$func(%tmp);
			}
			
			$page .= "		<tr>";
			for (0..$#headerfields){
				if ($db_valid_types{lc($headerfields[$_])} eq "date"){
					$page .= qq|	<td align="center" nowrap valign='top'>| . &sql_to_date($tmp{$headerfields[$_]}) . qq|&nbsp;</td>\n|;
				}elsif($db_valid_types{lc($headerfields[$_])} eq "currency"){
					$page .= qq|	<td align="right" nowrap valign='top'>| . &format_price($tmp{$headerfields[$_]}) . qq|&nbsp;</td>\n|;
				}elsif ($db_valid_types{lc($headerfields[$_])} eq "numeric"){
					$page .= qq|	<td align="right" nowrap valign='top'>| . &format_number($tmp{$headerfields[$_]}) . qq|&nbsp;</td>\n|;
				}else{
					$tmp{$headerfields[$_]} =~ s/\n/<br>/g;
					$page .= qq|	<td valign='top'>$tmp{$headerfields[$_]}&nbsp;</td>\n|;
				}
			}
			$page .= "		</tr>";
		}
		#$va{'searchresults'} = $page;
		($pageslist,$va{'qs'})  = &pages_list($in{'nh'},$script_url,$numhits,$usr{'pref_maxh'});
		#$va{'matches'}     = $numhits;
	}else{
		my ($colspan) = $#headerfields+2;
		$pageslist = 1;
		$numhits = 0;
		$page = qq|
		<tr>
		    <td align="center" colspan="$colspan" class='stdtxterr'><p>&nbsp;</p>| . &trans_txt('search_nomatches') . qq|<p>&nbsp;</p></td>
		 </tr>\n|;
	}
	
	return ($page,$numhits,$pageslist);
}

sub build_print_report {
# --------------------------------------------------------
	my($db,$header_fields,$header,$fname)=@_;
	&load_cfg($db);
	my ($output,$page,$pageslist,$page);
	
	### Special query
	my ($func) = "query_" . $db;
	if (defined &$func){
		%tmp = &$func(%tmp);
	}
	
	my ($numhits, @hits) = &query($db);
	my (@headerfields) = split(/,/,$header_fields);
	my ($func) = "report_" . $db;
	$va{'report_header'} = &build_report_header($header);
	$va{'report_matches'} = 'matches';
	$va{'matches'}        = $numhits;
	$va{'pageslist'}      = 0;
	if ($numhits>0){
		my ($rows) = ($#hits+1)/($#db_cols+1);
		
		for my $i(0 .. $rows-1) {
			%tmp = &array_to_hash($i, @hits);
			
			### Special fields
			if (defined &$func){
				%tmp = &$func(%tmp);
			}
			
			$va{'searchresults'} .= "		<tr>";
			for (0..$#headerfields){
				if ($db_valid_types{lc($headerfields[$_])} eq "date"){
					$va{'searchresults'} .= qq|	<td align="center" nowrap valign='top'>| . &sql_to_date($tmp{$headerfields[$_]}) . qq|&nbsp;</td>\n|;
				}elsif($db_valid_types{lc($headerfields[$_])} eq "currency"){
					$va{'searchresults'} .= qq|	<td align="right" nowrap valign='top'>| . &format_price($tmp{$headerfields[$_]}) . qq|&nbsp;</td>\n|;
				}elsif ($db_valid_types{lc($headerfields[$_])} eq "numeric"){
					$va{'searchresults'}.= qq|	<td align="right" nowrap valign='top'>| . &format_number($tmp{$headerfields[$_]}) . qq|&nbsp;</td>\n|;
				}else{
					$tmp{$headerfields[$_]} =~ s/\n/<br>/g;
					$va{'searchresults'} .= qq|	<td valign='top'>$tmp{$headerfields[$_]}&nbsp;</td>\n|;
				}
			}
			$va{'searchresults'} .= "		</tr>";
			if ((($i+1)/20) == int(($i+1)/20)){
				++$va{'pageslist'};
				$output .= &build_page('ccenter:print/default_page.html');
				$va{'searchresults'} = '';
			}
		}
		if ($va{'searchresults'}){
			++$va{'pageslist'};
			$output .= &build_page('ccenter:print/default_page.html');
		}
		
		
	}else{
		my ($colspan) = $#headerfields+2;
		$pageslist = 1;
		$numhits = 0;
		$output = qq|
		<tr>
		    <td align="center" colspan="$colspan" class='stdtxterr'><p>&nbsp;</p>| . &trans_txt('search_nomatches') . qq|<p>&nbsp;</p></td>
		 </tr>\n|;
		 
	}
	
	return $output;
}

sub build_xreport {
# --------------------------------------------------------
	my($db,$header_fields)=@_;
	my ($page,$pageslist,$numhits, @hits);
	
	### Special query
	my ($func) = "query_" . $db;
	if (defined &$func){
		($numhits, @hits) = &$func($header_fields);
	}

	my (@headerfields) = split(/,/,$header_fields);
	my ($func) = "report_" . $db;

	if ($numhits>0){
		my ($rows) = ($#hits+1)/($#db_cols+1);
		for (0 .. $rows-1) {
			%tmp = &array_to_hash($_, @hits);

			
			### Special fields
			if (defined &$func){
				%tmp = &$func(%tmp);
			}
			
			$page .= "		<tr>";
			for (0..$#headerfields){
				if ($db_valid_types{lc($headerfields[$_])} eq "date"){
					$page .= qq|	<td align="center" nowrap valign='top'>| . &sql_to_date($tmp{$headerfields[$_]}) . qq|&nbsp;</td>\n|;
				}elsif($db_valid_types{lc($headerfields[$_])} eq "currency"){
					$page .= qq|	<td align="right" nowrap valign='top'>| . &format_price($tmp{$headerfields[$_]}) . qq|&nbsp;</td>\n|;
				}elsif ($db_valid_types{lc($headerfields[$_])} eq "numeric"){
					$page .= qq|	<td align="right" nowrap valign='top'>| . &format_number($tmp{$headerfields[$_]}) . qq|&nbsp;</td>\n|;
				}else{
					$tmp{$headerfields[$_]} =~ s/\n/<br>/g;
					$page .= qq|	<td valign='top'>$tmp{$headerfields[$_]} &nbsp;</td>\n|;
				}
			}
			$page .= "		</tr>";
		}
		#$va{'searchresults'} = $page;
		($pageslist,$va{'qs'})  = &pages_list($in{'nh'},$script_url,$numhits,$usr{'pref_maxh'});
		#$va{'matches'}     = $numhits;
	}else{
		my ($colspan) = $#headerfields+2;
		$pageslist = 1;
		$numhits = 0;
		$page = qq|
		<tr>
		    <td align="center" colspan="$colspan" class='stdtxterr'><p>&nbsp;</p>| . &trans_txt('search_nomatches') . qq|<p>&nbsp;</p></td>
		 </tr>\n|;
	}
	
	##($va{'searchresults'},$va{'matches'},$va{'pageslist'})
	return ($page,$numhits,$pageslist);
}

1;

