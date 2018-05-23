
sub html_error_page {
# --------------------------------------------------------
	$va{'message'} = @_[0];
	print "Content-type: text/html\n\n";
	print &build_page('searchid:form.html');
}

sub html_search_form {
# --------------------------------------------------------
	$va{'message'} = @_[0];
	$va{'searchform'} = &html_record_form (%rec);
	print "Content-type: text/html\n\n";
	print &build_page('searchid:form.html');
}


sub search_menu {
# --------------------------------------------------------
	if ($in{'listall'}){
		$in{lc($db_cols[0])} = '*';
	}
	my ($numhits, @hits) = &query($in{'db'});
	if ($numhits >0) {
		&html_search_result($numhits,@hits);
	}else{
		&html_search_form(&trans_txt('search_nomatches'));
	}
}

sub html_search_result{
# --------------------------------------------------------

	my ($numhits,@hits) = @_;
	my ($field);
	#my ($numhits) = ($#hits+1) / ($#db_cols+1);
	($message)  and ($message = "<p>$message</p>");
	#($db_next_hits) and ($db_next_hits = "<div class='stdtext'>Pages: $db_next_hits</div>");
	$va{'matches'} = $numhits;

	my ($numhits,@hits) = @_;
	my (%tmp, $qs, $add_title);
	my (@c) = split(/,/,$cfg{'srcolors'});
	my ($rows) = ($#hits+1)/($#db_cols+1);
	my ($returl) = &decode_returl($in{'returnurl'});
	
	$in{'returnfield'}= $db_cols[0] if (!$in{'returnfield'});
	$in{'returnid'} = $db_cols[0] if (!$in{'returnid'});
	
	$va{'searchresult'} = qq|
         <tr bgcolor="#3E76DD" align="center">
            <td class="tbltextttlwte">Sel/View</td>\n|;
	for (0..$#titlefields){
		$va{'searchresult'} .= qq|            <td class="tbltextttlwte">$titlefields[$_]</td>\n|;
	}
	$page .= "         </tr>\n";

	for (0 .. $rows-1) {
		my (@c) = split(/,/,$cfg{'srcolors'});
		%tmp = &array_to_hash($_, @hits);
		$va{'searchresult'} .= qq|
		    <tr onmouseover='m_over(this)' onmouseout='m_out(this)' bgcolor='$c[$d]'>
		       <td align="center" valign='top' nowrap>|;
		if($in{'returnurl'}){
			#$va{'searchresult'} .= qq|<input type="button" name="sel__$tmp{$db_cols[0]}" value="S" class="button" onclick="trjump('$returl$tmp{$db_cols[0]}')">\n|;
			$va{'searchresult'} .= qq|<a href="#" onclick="trjump('$returl$tmp{$in{'returnfield'}}')"><img src="$va{'imgurl'}/$usr{'pref_style'}/b_ok.png" border="0"></a> &nbsp;&nbsp;|;
		}else{
			#$va{'searchresult'} .= qq|<input type="button" name="sel__$tmp{$db_cols[0]}" value="S" class="button" onclick="setid($tmp{$db_cols[0]},'  $name')">\n|;
			$va{'searchresult'} .= qq|<a href="#" onclick="setid('$tmp{$in{'returnfield'}}','$in{'returnid'}')"><img src="$va{'imgurl'}/$usr{'pref_style'}/b_ok.png" border="0"></a> &nbsp;&nbsp;|;
		}
		#$va{'searchresult'} .= qq|<input type="submit" name="view_$tmp{$db_cols[0]}" value="V" class="button"></td>\n|;
		$va{'searchresult'} .= qq|<a href="/cgi-bin/common/apps/schid?view_$tmp{$db_cols[0]}=V&db=$in{'db'}&app=$in{'app'}&fname=$in{'fname'}&cmd=$in{'cmd'}&returnid=$in{'returnid'}&returnurl=$in{'returnurl'}&returnfield=$in{'returnurl'}"><img src="$va{'imgurl'}/$usr{'pref_style'}/view.png" border="0"></a>|;

		
		for (0..$#headerfields){
			if ($db_valid_types{$headerfields[$_]} eq "currency"){
				$va{'searchresult'} .= qq|	<td align="right" nowrap valign='top' class='smalltext'>| . &format_price($tmp{$headerfields[$_]}) . qq|&nbsp</td>\n|;
			}elsif ($db_valid_types{$headerfields[$_]} eq "numeric"){
				$va{'searchresult'} .= qq|	<td align="right" nowrap valign='top' class='smalltext'>| . &format_number($tmp{$headerfields[$_]}) . qq|&nbsp</td>\n|;
			}else{
				$va{'searchresult'} .= qq|	<td valign='top' class='smalltext'>$tmp{$headerfields[$_]}&nbsp</td>\n|;
			}
		}
		$va{'searchresult'} .= "		</tr>";
	}
	$va{'matches'}     = $numhits;
	($va{'pageslist'},$in{'qs'}) = &pages_list($in{'nh'},"/cgi-bin/common/apps/schid",$va{'matches'},$usr{'pref_maxh'});
	print "Content-type: text/html\n\n";
	print &build_page('searchid:result.html');
}


sub html_view_record {
# --------------------------------------------------------
	my ($message) = @_;
	my (%rec) = &get_record($db_cols[0],$in{'value'},$in{'db'});
	if (!$rec{lc($db_cols[0])}) {
		&html_error_page(&trans_txt('schid_notfind')." $in{'value'} ");
	}else {
		$va{'idvalue'}    = $rec{lc($db_cols[0])};
		my ($returl) = &decode_returl($in{'returnurl'});
		if($in{'returnurl'}){
			$va{'jsselect'} .= qq|trjump('$returl$tmp{$db_cols[0]}')|;
		}else{
			$in{'returnid'} = $db_cols[0] if (!$in{'returnid'});
			$va{'jsselect'} .= qq|setid('[va_idvalue]',' [va_name]')|;
		}
		print "Content-type: text/html\n\n";
		$va{'viewrecord'} = &html_record(%rec);
		print &build_page('searchid:view.html');
	}
}

sub html_record_form {
# --------------------------------------------------------
# Last Modified on: 10/28/08 13:10:48
# Last Modified by: MCC C. Gabriel Varela S: Se corrige funcionamiento: Se quita debug
	my (%rec) = @_;		# Load any defaults to put in the VALUE field.
	my ($page);
    for my $i(0.. $#headerfields){
		$field = lc($headerfields[$i]);
		#next if ($field =~ /^ns/);
		$page .= qq|\n			<tr>\n			  <td>&nbsp;</td>\n			  <td valign="top" nowrap>$titlefields[$i] : </td>\n|;
		if ($db_valid_types{$field} eq 'selection'){
			$page .= qq|		<td>| . &build_select_field ($field, "$rec{$field}") . qq|</td>\n|;
		}elsif ($db_valid_types{$field} eq 'radio') {
			$page .= qq| 		<td class="smalltext">| . &build_radio_field($field, $rec{$field}) . qq|</td>\n|;
		}elsif ($db_valid_types{$field} eq 'checkbox' ) {
			$page .= qq| 		<td>| . &build_checkbox_field ($field, $rec{$field}) . qq|</td>\n|;
		}elsif ($db_valid_types{$field} eq 'date') {
			$page .=  qq|<td><input type="text" id="$field" NAME="$field" VALUE="$rec{$field}" SIZE="25" onFocus='focusOn( this )' onBlur='focusOff( this )'>
<script language="javascript">
    \$(document).ready(function() {

		var dates = \$( "#$field" ).datepicker({
			dateFormat: 'yy-mm-dd',
			defaultDate: "-2m",
			maxDate: new Date(),
			changeMonth: true,
			numberOfMonths: 3,
		});

    });
</script>
</td>|;
		}else{
			$page .= qq| 	<td><input type=text  NAME="$field" VALUE="$rec{$field}" SIZE="25" onFocus='focusOn( this )' onBlur='focusOff( this )'></td>\n|;
		}
		$page .= "			</tr>\n";
		
		## Build fieldslist
		$va{'fieldslist'} .= "<option name='$field'>$titlefields[$i]</option>";
	}
	return $page;
}

sub html_record {
# --------------------------------------------------------
	my (%rec) = @_;		# Load any defaults to put in the VALUE field.
	my ($fiels,$page);
    	for (0.. $#db_cols){
		$field = $db_cols[$_];
		next if ($field =~ /^ns/);
		$page .= qq|\n			<tr>\n			  <td>&nbsp;</td>\n			  <td valign="top" nowrap>$field : $a</td>\n|;
		if ($db_valid_types{$field} eq "currency"){
			$page .= qq|		  <td nowrap>| . &format_price($rec{lc($field)}) . qq|</td>\n|;
		}elsif($db_valid_types{$field} eq "numeric" and $field !~ /^ID/){
			$page .= qq|		  <td nowrap>| . &format_number($rec{lc($field)}) . qq|</td>\n|;
		}else{
			$page .= "		  <td>".$rec{lc($field)}." $db_valid_types{$field}</td>\n";
		}
		$page .= "			</tr>\n";
	}
	return $page;
}

sub parts_addvendor {
# --------------------------------------------------------
	my ($query);
	if ($in{'keyword'}){
		$query = "AND (CompanyName like '%$in{'keyword'}%' or ID_vendors like '%$in{'keyword'}%')";
	}
	my ($sth) = &Do_SQL("SELECT COUNT(*) FROM sl_vendors WHERE Status='Active' $query;");
	$va{'matches'} = $sth->fetchrow();
	my (@c) = split(/,/,$cfg{'srcolors'});
	if ($va{'matches'}>0){
		(!$in{'nh'}) and ($in{'nh'}=1);
		$first = ($in{'nh'} - 1) * $usr{'pref_maxh'};			
		($va{'pageslist'},$qs) = &pages_list($in{'nh'},"/cgi-bin/common/apps/schid",$va{'matches'},$usr{'pref_maxh'});
		
		my ($sth) = &Do_SQL("SELECT * FROM sl_vendors WHERE Status='Active' $query LIMIT $first,$usr{'pref_maxh'};");
		while ($rec = $sth->fetchrow_hashref){
			$d = 1 - $d;
			$va{'searchresults'} .= qq|
			<tr bgcolor='$c[$d]' onmouseover='m_over(this)' onmouseout='m_out(this)' onclick="trjump('/cgi-bin/mod/$usr{'application'}/dbman?cmd=mer_parts&view=$in{'id_parts'}&addvendor=$rec->{'ID_vendors'}&tab=2#tabs')">
				<td class="smalltext">$rec->{'ID_vendors'}</td>
				<td class="smalltext">$rec->{'CompanyName'}</td>
			</tr>\n|;
		}
	}else{
		$va{'pageslist'} = 1;
		$va{'searchresults'} = qq|
			<tr>
				<td colspan='5' align="center">|.&trans_txt('search_nomatches').qq|</td>
			</tr>\n|;
	}
	$in{'id_name'} = "id_parts";
	$in{'id_value'} = $in{'id_parts'};
	$va{'header'} = qq|
		<tr>
		    <td class="menu_bar_title">ID</td>
		    <td class="menu_bar_title">Name</td>
		 </tr>\n|;

	print "Content-type: text/html\n\n";
	print &build_page('searchid:addid.html');

}

sub services_addvendor {
# --------------------------------------------------------
	my ($query);
	if ($in{'keyword'}){
		$query = "AND (CompanyName like '%$in{'keyword'}%' or ID_vendors like '%$in{'keyword'}%')";
	}
	my ($sth) = &Do_SQL("SELECT COUNT(*) FROM sl_vendors WHERE Status='Active' $query;");
	$va{'matches'} = $sth->fetchrow();
	my (@c) = split(/,/,$cfg{'srcolors'});
	if ($va{'matches'}>0){
		(!$in{'nh'}) and ($in{'nh'}=1);
		$first = ($in{'nh'} - 1) * $usr{'pref_maxh'};			
		($va{'pageslist'},$qs) = &pages_list($in{'nh'},"/cgi-bin/common/apps/schid",$va{'matches'},$usr{'pref_maxh'});
		
		my ($sth) = &Do_SQL("SELECT * FROM sl_vendors WHERE Status='Active' $query LIMIT $first,$usr{'pref_maxh'};");
		while ($rec = $sth->fetchrow_hashref){
			$d = 1 - $d;
			$va{'searchresults'} .= qq|
			<tr bgcolor='$c[$d]' onmouseover='m_over(this)' onmouseout='m_out(this)' onclick="trjump('/cgi-bin/mod/$usr{'application'}/dbman?cmd=mer_services&view=$in{'id_services'}&addvendor=$rec->{'ID_vendors'}&tab=6#tabs=1')">
				<td class="smalltext">$rec->{'ID_vendors'}</td>
				<td class="smalltext">$rec->{'CompanyName'}</td>
			</tr>\n|;
		}
	}else{
		$va{'pageslist'} = 1;
		$va{'searchresults'} = qq|
			<tr>
				<td colspan='5' align="center">|.&trans_txt('search_nomatches').qq|</td>
			</tr>\n|;
	}
	$in{'id_name'} = "id_services";
	$in{'id_value'} = $in{'id_services'};
	$va{'header'} = qq|
		<tr>
		    <td class="menu_bar_title">ID</td>
		    <td class="menu_bar_title">Name</td>
		 </tr>\n|;

	print "Content-type: text/html\n\n";
	print &build_page('searchid:addid.html');

}

sub services_retention_setup {
# --------------------------------------------------------
	use JSON;

	if( $in{'action'} == 1 ){

		my %json_data;
		my $command = 'service_account_retention';

		my $allow_perm = 0;
		if( &check_permissions('services_retention_setup','','') ){
			$allow_perm = 1;
		}

		###------------------------------------------
		### Agregar una cuenta
		###------------------------------------------
		if( $in{'act_type'} eq 'add' ){
			###
			### Validación
			###
			$json_data{'result'} = 200;
			if( !$in{'id_accounts'} ){
				$json_data{'result'} = 400;
				$json_data{'error'} .= 'La cuenta contable es requerida<br>';
			}
			if( !$in{'percent'} or $in{'percent'} < 0 or $in{'percent'} > 100 ){
				$json_data{'result'} = 400;
				$json_data{'error'} .= 'El porcentage es inv&aacute;lido<br>';
			}
			if( !$in{'credebit'} ){
				$json_data{'result'} = 400;
				$json_data{'error'} .= 'El credebit es requerido<br>';
			}

			###
			### Se guardan los datos en vars_config
			###
			if( $json_data{'result'} == 200 ){				

				my $sth = &Do_SQL("SELECT COUNT(*) FROM sl_vars_config WHERE Command = '".$command."' AND IDValue = ".$in{'id_services'}." AND Code = '".$in{'id_accounts'}."' AND Largecode = '".$in{'credebit'}."';");
				my $exist = $sth->fetchrow();
				if( !$exist ){
					my $sql = "INSERT INTO sl_vars_config SET 
									Command = '".$command."'
									, IDValue = ".$in{'id_services'}."
									, Code = '".$in{'id_accounts'}."'
									, Subcode = '".$in{'percent'}."'
									, Largecode = '".$in{'credebit'}."'
									, Description = '".$in{'extra'}."'
									, Date = CURDATE()
									, Time = CURTIME()
									, ID_admin_users = ".$usr{'id_admin_users'}."
								;";
					&Do_SQL($sql);

					my $sth = &Do_SQL("SELECT sl_vars_config.ID_vars_config
											, sl_vars_config.Code 
											, sl_vars_config.Subcode
											, sl_vars_config.Largecode
											, sl_vars_config.Description
											, sl_accounts.Name
											, sl_accounts.ID_accounting
										FROM sl_vars_config 
											INNER JOIN sl_accounts ON sl_accounts.ID_accounts = sl_vars_config.Code 
										WHERE Command = '".$command."' AND IDValue = ".$in{'id_services'}.";");
					while( my $rec = $sth->fetchrow_hashref() ){
						$json_data{'html_result'} .= '<tr>';
						$json_data{'html_result'} .= '<td>['.$rec->{'ID_accounting'}.'] - '.$rec->{'Name'}.'</td>';
						$json_data{'html_result'} .= '<td style="text-align: center;">'.$rec->{'Subcode'}.' %</td>';
						$json_data{'html_result'} .= '<td style="text-align: center;">'.$rec->{'Largecode'}.'</td>';
						$json_data{'html_result'} .= '<td style="text-align: center;">'.$rec->{'Description'}.'</td>';
						$json_data{'html_result'} .= '<td style="text-align: right;">';
						if( $allow_perm == 1 ){
							$json_data{'html_result'} .= '<a href="#" data-id="'.$rec->{'ID_vars_config'}.'" class="lnk_drop_retention" title="Eliminar esta cuenta"><img src="/sitimages/default/b_drop.png" alt="delete" /></a>';
						} else {
							$json_data{'html_result'} .= '&nbsp;';
						}
						$json_data{'html_result'} .= '</td>';
						$json_data{'html_result'} .= '</tr>';
					}

				}else{
					$json_data{'result'} = 400;
					$json_data{'error'} = 'Esta configuración ya existe para este servicio';
				}
			}

		###------------------------------------------
		### Eliminar una cuenta
		###------------------------------------------
		} elsif( $in{'act_type'} eq 'drop' ){

			$json_data{'result'} = 200;
			my $sth = &Do_SQL("DELETE FROM sl_vars_config WHERE ID_vars_config = ".int($in{'drop'}).";");

			my $sth = &Do_SQL("SELECT sl_vars_config.ID_vars_config
									, sl_vars_config.Code 
									, sl_vars_config.Subcode
									, sl_vars_config.Largecode
									, sl_vars_config.Description
									, sl_accounts.Name
									, sl_accounts.ID_accounting
								FROM sl_vars_config 
									INNER JOIN sl_accounts ON sl_accounts.ID_accounts = sl_vars_config.Code 
								WHERE Command = '".$command."' AND IDValue = ".$in{'id_services'}.";");
			while( my $rec = $sth->fetchrow_hashref() ){
				$json_data{'html_result'} .= '<tr>';
				$json_data{'html_result'} .= '<td>['.$rec->{'ID_accounting'}.'] - '.$rec->{'Name'}.'</td>';
				$json_data{'html_result'} .= '<td style="text-align: center;">'.$rec->{'Subcode'}.' %</td>';
				$json_data{'html_result'} .= '<td style="text-align: center;">'.$rec->{'Largecode'}.'</td>';
				$json_data{'html_result'} .= '<td style="text-align: center;">'.$rec->{'Description'}.'</td>';
				$json_data{'html_result'} .= '<td style="text-align: right;">';
				if( $allow_perm == 1 ){
					$json_data{'html_result'} .= '<a href="#" data-id="'.$rec->{'ID_vars_config'}.'" class="lnk_drop_retention" title="Eliminar esta cuenta"><img src="/sitimages/default/b_drop.png" alt="delete" /></a>';
				} else {
					$json_data{'html_result'} .= '&nbsp;';
				}
				$json_data{'html_result'} .= '</td>';
				$json_data{'html_result'} .= '</tr>';
			}

			if( !$json_data{'html_result'} ){
				$json_data{'html_result'} = '<tr><td colspan="5">'.&trans_txt('notmatch').'</td></tr>';
			}

		}

		print "Content-type: application/json\n\n";
		print encode_json(\%json_data);

	}else {
		print "Content-type: text/html\n\n";
		if( &check_permissions('services_retention_setup','','') ){
			print &build_page('mer_services_addretention.html');
		} else {
			print &build_page('unauth_small.html');
		}

	}
}

sub po_additems {
# --------------------------------------------------------
# Last Modified RB: 05/15/09  16:32:22 -- Solo muestra productos que no son sets
# Last Modified RB: 06/30/09  18:02:25 -- Se cambia el comando de acuerdo a si sera po o rvendor


	my ($query);
	my $cmd = 'mer_po';
	$cmd = 'mer_rvendor' if $in{'type'}eq'rvendor';
	
	if ($in{'keyword'}){
		$query = "AND (MATCH(sl_products.Name) AGAINST('*".$in{'keyword'}."*' IN BOOLEAN MODE) OR MATCH(sl_products.Model) AGAINST('*".$in{'keyword'}."*' IN BOOLEAN MODE) OR sl_products.ID_products like '%".$in{'keyword'}."%')";
	}
	my ($id_vendors) = &load_name('sl_purchaseorders','ID_purchaseorders',$in{'id_purchaseorders'},'ID_vendors');
	
	my ($sth) = &Do_SQL("SELECT COUNT(*) FROM sl_products_vendors,sl_products WHERE RIGHT(sl_products_vendors.ID_products,6)=sl_products.ID_products AND sl_products.Status<>'Inactive' AND ID_vendors='$id_vendors' AND  1 > (SELECT COUNT(*) FROM sl_skus WHERE IsSet='Y' AND ID_products = sl_products.ID_products) $query;");
	$va{'matches'} = $sth->fetchrow();
	my (@c) = split(/,/,$cfg{'srcolors'});
	if ($va{'matches'}>0){
		(!$in{'nh'}) and ($in{'nh'}=1);
		$first = ($in{'nh'} - 1) * $usr{'pref_maxh'};			
		($va{'pageslist'},$qs) = &pages_list($in{'nh'},"/cgi-bin/common/apps/schid",$va{'matches'},$usr{'pref_maxh'});
		
		my ($sth) = &Do_SQL("SELECT * FROM sl_products_vendors,sl_products WHERE RIGHT(sl_products_vendors.ID_products,6)=sl_products.ID_products AND sl_products.Status<>'Inactive' AND ID_vendors='$id_vendors' AND  1 > (SELECT COUNT(*) FROM sl_skus WHERE IsSet='Y' AND ID_products = sl_products.ID_products) $query GROUP BY sl_products.ID_products LIMIT $first,$usr{'pref_maxh'};");
		while ($rec = $sth->fetchrow_hashref){
			$d = 1 - $d;
			my ($sth2) = &Do_SQL("SELECT COUNT(*) FROM sl_skus WHERE ID_products=$rec->{'ID_products'};");
			if ($sth2->fetchrow>1){
				## Multiples Choices
				my ($sth2) = &Do_SQL("SELECT * FROM sl_skus WHERE ID_products=$rec->{'ID_products'};");
				while ($tmp = $sth2->fetchrow_hashref){
					$choices = &load_choices('-',$tmp->{'choice1'},$tmp->{'choice2'},$tmp->{'choice3'},$tmp->{'choice4'});
					$va{'searchresults'} .= qq|
			<tr bgcolor='$c[$d]' onmouseover='m_over(this)' onmouseout='m_out(this)' onclick="trjump('/cgi-bin/mod/$usr{'application'}/dbman?cmd=$cmd&view=$in{'id_purchaseorders'}&additem=$tmp->{'ID_sku_products'}&qty=1&tab=1#tabs')">
				<td class="smalltext" valign="top">|.&format_sltvid($tmp->{'ID_sku_products'}).qq|</td>
				<td class="smalltext">$rec->{'Model'}<br>$rec->{'Name'}  $choices</td>
				<td class="smalltext" valign="top" align="right" nowrap>|.&format_price($rec->{'SPrice'}).qq|</td>
			</tr>\n|;
				}
			}else{
				$va{'searchresults'} .= qq|
			<tr bgcolor='$c[$d]' onmouseover='m_over(this)' onmouseout='m_out(this)' onclick="trjump('/cgi-bin/mod/$usr{'application'}/dbman?cmd=$cmd&view=$in{'id_purchaseorders'}&additem=$rec->{'ID_products'}&qty=1&tab=1#tabs')">
				<td class="smalltext" valign="top">|.&format_sltvid($rec->{'ID_products'}).qq|</td>
				<td class="smalltext">$rec->{'Model'}<br>$rec->{'Name'}</td>
				<td class="smalltext" valign="top" align="right">|.&format_price($rec->{'SPrice'}).qq|</td>
			</tr>\n|;
			}
		}
	}else{
		$va{'pageslist'} = 1;
		$va{'searchresults'} = qq|
			<tr>
				<td colspan='5' align="center">  |.&trans_txt('search_nomatches').qq|</td>
			</tr>\n|;
	}
	
	$va{'header'} = qq|
		<tr>
		    <td class="menu_bar_title">ID</td>
		    <td class="menu_bar_title">Model/Name</td>
		    <td class="menu_bar_title">Price</td>
		 </tr>\n|;
	$in{'id_name'} = "id_purchaseorders";
	$in{'id_value'} = $in{'id_purchaseorders'};

	print "Content-type: text/html\n\n";
	print &build_page('searchid:addid.html');
}

sub add_product{

	my ($query);
	if ($in{'keyword'}){
		$query = "and Name like '%$in{'keyword'}%'";
	}

	
	my $q = qq|select 
		sl_parts.ID_parts,
		sl_parts.Name,
		sl_skus.UPC
	from 
		sl_parts 
		inner join sl_customers_parts on sl_parts.ID_parts =  sl_customers_parts.ID_parts 
		inner join sl_skus on sl_parts.ID_parts = sl_skus.ID_products
		where sl_customers_parts.ID_customers = $in{'id_customers'} $query|;
	my ($sth) = &Do_SQL("$q");
	$va{'matches'} = $sth->rows();
	my (@c) = split(/,/,$cfg{'srcolors'});
	if ($va{'matches'}>0){
		(!$in{'nh'}) and ($in{'nh'}=1);
		$first = ($in{'nh'} - 1) * $usr{'pref_maxh'};			
		($va{'pageslist'},$qs) = &pages_list($in{'nh'},"/cgi-bin/common/apps/schid",$va{'matches'},$usr{'pref_maxh'});
		
		my ($sth) = &Do_SQL("$q LIMIT $first,$usr{'pref_maxh'};");
		while ($rec = $sth->fetchrow_hashref){
			$d = 1 - $d;
			$va{'searchresults'} .= qq|
			<tr bgcolor='$c[$d]' onmouseover='m_over(this)' onmouseout='m_out(this)'>			 
				<td class="smalltext" valign="top">
					<input type="button" class="button" value="S" onclick="trjump('/cgi-bin/mod/$usr{'application'}/dbman?cmd=opr_return_notices&view=$in{'id_return_notices'}&id_products=$rec->{'ID_parts'}')"  onmouseover="m_over(this)" onmouseout="m_out(this)">
				</td>
				<td class="smalltext" valign="top">|.&format_sltvid(400000000+$rec->{'ID_parts'}).qq|</td>
				<td class="smalltext" valign="top">|.$rec->{'UPC'}.qq|</td>
				<td class="smalltext">$rec->{'Model'} $rec->{'Name'}</td>
			</tr>\n|;
		}
	}else{
		$va{'pageslist'} = 1;
		$va{'searchresults'} = qq|
			<tr>
				<td colspan='5' align="center">  |.&trans_txt('search_nomatches').qq|</td>
			</tr>\n|;
	}
	$in{'id_name'} = 'view';
	$in{'name_customer'} = 'id_customers';
	$in{'name_notices'} = 'id_return_notices';
	$in{'id_name'} = 'view';
	$in{'cmd'} = 'add_product';

	$va{'header'} = qq|
		<tr>
		    <td class="menu_bar_title">Sel</td>
		    <td class="menu_bar_title">SKU</td>
		    <td class="menu_bar_title">UPC</td>
		    <td class="menu_bar_title">Model/Name</td>
		 </tr>\n|;
	print "Content-type: text/html\n\n";
	# print $q;
	# print $in{'keywork'};
	$in{'keyword'} = '';
	print &build_page('searchid:addidcus.html');
}


sub po_addparts {
# --------------------------------------------------------
# Last Modified RB: 06/30/09  18:02:25 -- Se cambia el comando de acuerdo a si sera po o rvendor

	my ($query);
	my $cmd = 'mer_po';
	$cmd = 'mer_rvendor' if $in{'type'}eq'rvendor';
	
	if ($in{'keyword'}){
		$add_sql = (int($in{'keyword'}) eq 'nan')? "":" OR sl_parts.ID_parts = ".int($in{'keyword'});
		$query = "AND (Model LIKE '%".&filter_values($in{'keyword'})."%' OR Name LIKE '%".&filter_values($in{'keyword'})."%' $add_sql) ";
	}
	my ($id_vendors) = &load_name('sl_purchaseorders','ID_purchaseorders',$in{'id_purchaseorders'},'ID_vendors');

	$va{'btn_select'} = '<input type="button" class="button" value="Select" id="btn_sel_mult" onmouseover="m_over(this)" onmouseout="m_out(this)" href="/cgi-bin/mod/'.$usr{'application'}.'/dbman?cmd=mer_po&view='.$in{'id_purchaseorders'}.'&tab=1">';
	


	my ($sth) = &Do_SQL("SELECT COUNT(*) FROM sl_parts_vendors,sl_parts
						INNER JOIN sl_skus ON sl_skus.ID_products = sl_parts.ID_parts
						WHERE sl_parts_vendors.ID_parts=sl_parts.ID_parts AND sl_parts.Status='Active' AND ID_vendors='$id_vendors' $query;");
	$va{'matches'} = $sth->fetchrow();
	my (@c) = split(/,/,$cfg{'srcolors'});
	if ($va{'matches'}>0){
		(!$in{'nh'}) and ($in{'nh'}=1);
		$first = ($in{'nh'} - 1) * $usr{'pref_maxh'};			
		($va{'pageslist'},$qs) = &pages_list($in{'nh'},"/cgi-bin/common/apps/schid",$va{'matches'},$usr{'pref_maxh'});
		
		my ($sth) = &Do_SQL("SELECT * FROM sl_parts_vendors,sl_parts
							  INNER JOIN sl_skus ON sl_skus.ID_products = sl_parts.ID_parts
							  WHERE sl_parts_vendors.ID_parts=sl_parts.ID_parts AND sl_parts.Status='Active' AND ID_vendors='$id_vendors' $query GROUP BY sl_parts.ID_parts LIMIT $first,$usr{'pref_maxh'};");
		while ($rec = $sth->fetchrow_hashref){
			$d = 1 - $d;
			$va{'searchresults'} .= qq|
			<tr bgcolor='$c[$d]' onmouseover='m_over(this)' onmouseout='m_out(this)'>			 
				<td valign="top" class="smalltext"><input type="checkbox" class="inpcheck" value="|.(400000000+$rec->{'ID_parts'}).qq|" name="additem"></td>
				<td class="smalltext" valign="top">
					<input type="button" class="button" value="S" onclick="trjump('/cgi-bin/mod/$usr{'application'}/dbman?cmd=mer_po&view=$in{'id_purchaseorders'}&additem=|.(400000000+$rec->{'ID_parts'}).qq|&tab=1#tabs')"  onmouseover="m_over(this)" onmouseout="m_out(this)">
				</td>
				<td class="smalltext" valign="top">|.&format_sltvid(400000000+$rec->{'ID_parts'}).qq|</td>
				<td class="smalltext" valign="top">|.$rec->{'UPC'}.qq|</td>
				<td class="smalltext">$rec->{'Model'} $rec->{'Name'}</td>
			</tr>\n|;
		}
	}else{
		$va{'pageslist'} = 1;
		$va{'searchresults'} = qq|
			<tr>
				<td colspan='5' align="center">  |.&trans_txt('search_nomatches').qq|</td>
			</tr>\n|;
	}
	$in{'id_name'} = "id_purchaseorders";
	$in{'id_value'} = $in{'id_purchaseorders'};
	$va{'header'} = qq|
		<tr>
		    <td class="menu_bar_title"><input type="checkbox" name="checkall" id="checkall" value=""></td>
		    <td class="menu_bar_title">Sel</td>
		    <td class="menu_bar_title">ID</td>
			<td class="menu_bar_title">UPC</td>
		    <td class="menu_bar_title">Model/Name</td>
		 </tr>\n|;
	print "Content-type: text/html\n\n";
	print &build_page('searchid:addid.html');
}

sub po_addnoinv{
# --------------------------------------------------------

	my ($query);
	my $cmd = 'mer_po';
	
	if ($in{'keyword'}){
		$query = "AND ( Name like '%$in{'keyword'}%' OR ID_noninventory = '".int($in{'keyword'})."' OR Description = '$in{'keyword'}' )";
	}
	my ($id_vendors) = &load_name('sl_purchaseorders','ID_purchaseorders',$in{'id_purchaseorders'},'ID_vendors');
	
	my ($sth) = &Do_SQL("SELECT COUNT(*) FROM sl_noninventory WHERE (AnyVendor='Yes' OR ID_noninventory IN (SELECT ID_noninventory FROM sl_noninventory_vendors WHERE ID_vendors=$id_vendors)) AND Status='Active'  $query;");
	$va{'matches'} = $sth->fetchrow();
	my (@c) = split(/,/,$cfg{'srcolors'});
	if ($va{'matches'}>0){
		(!$in{'nh'}) and ($in{'nh'}=1);
		$first = ($in{'nh'} - 1) * $usr{'pref_maxh'};			
		($va{'pageslist'},$qs) = &pages_list($in{'nh'},"/cgi-bin/common/apps/schid",$va{'matches'},$usr{'pref_maxh'});
		
		my ($sth) = &Do_SQL("SELECT * FROM sl_noninventory WHERE (AnyVendor='Yes' OR ID_noninventory IN (SELECT ID_noninventory FROM sl_noninventory_vendors WHERE ID_vendors=$id_vendors)) AND Status='Active' $query LIMIT $first,$usr{'pref_maxh'};");
		while ($rec = $sth->fetchrow_hashref){
			$d = 1 - $d;
			$va{'searchresults'} .= qq|
			<tr bgcolor='$c[$d]' onmouseover='m_over(this)' onmouseout='m_out(this)' onclick="trjump('/cgi-bin/mod/$usr{'application'}/dbman?cmd=$cmd&view=$in{'id_purchaseorders'}&additem=|.(500000000+$rec->{'ID_noninventory'}).qq|&qty=1&tab=1#tabs')">
				<td class="smalltext" valign="top">|.&format_sltvid(500000000+$rec->{'ID_noninventory'}).qq|</td>
				<td class="smalltext">$rec->{'Model'} $rec->{'Name'}</td>
			</tr>\n|;
		}
	}else{
		$va{'pageslist'} = 1;
		$va{'searchresults'} = qq|
			<tr>
				<td colspan='5' align="center">  |.&trans_txt('search_nomatches').qq|</td>
			</tr>\n|;
	}
	$in{'id_name'} = "id_purchaseorders";
	$in{'id_value'} = $in{'id_purchaseorders'};
	$va{'header'} = qq|
		<tr>
		    <td class="menu_bar_title">ID</td>
		    <td class="menu_bar_title">Model/Name</td>
		 </tr>\n|;
	print "Content-type: text/html\n\n";
	print &build_page('searchid:addid.html');
}

#############################################################################
#############################################################################
#   Function: po_addservices
#
#       Es: Agrega servicios a una orden de compra
#       En: Add Services to Purchase Order
#
#
#    Created on: 
#
#    Author: ISC Alejandro Diaz
#
#    Modifications:
#
#   Parameters:
#
#      - id_purchaseorders: ID Purchase Order
#
#   Returns:
#
#      - 
#
#   See Also:
#
#
sub po_addservices {
#############################################################################
#############################################################################

	my ($query);
	
	if ($in{'keyword'} and $in{'keyword'} ne ''){
		$query = "AND (sl_services.Description LIKE '%".&filter_values($in{'keyword'})."%' OR sl_services.Name LIKE '%".&filter_values($in{'keyword'})."%' OR sl_services.ID_services = ".int($in{'keyword'}).") ";
	}

	### Se obtiene el ID_vendors del PO
	my $id_vendors = &load_name('sl_purchaseorders', 'ID_purchaseorders', $in{'id_purchaseorders'}, 'ID_vendors');

	my ($sth) = &Do_SQL("SELECT COUNT(*) 
						 FROM sl_services 
						 	INNER JOIN sl_services_vendors ON sl_services.ID_services = sl_services_vendors.ID_services AND sl_services_vendors.ID_vendors = ".int($id_vendors)."
						 WHERE sl_services.Status='Active' $query;");
	$va{'matches'} = $sth->fetchrow();
	my (@c) = split(/,/,$cfg{'srcolors'});
	if ($va{'matches'}>0){
		(!$in{'nh'}) and ($in{'nh'}=1);
		$first = ($in{'nh'} - 1) * $usr{'pref_maxh'};			
		($va{'pageslist'},$qs) = &pages_list($in{'nh'},"/cgi-bin/common/apps/schid",$va{'matches'},$usr{'pref_maxh'});
		
		my ($sth) = &Do_SQL("SELECT (600000000+sl_services.ID_services)SKU
								, sl_services.ID_services 
								, sl_services.Name
								, sl_services.Description
								, sl_services.SPrice
								, sl_services.Tax 
							 FROM sl_services 
							 	INNER JOIN sl_services_vendors ON sl_services.ID_services = sl_services_vendors.ID_services AND sl_services_vendors.ID_vendors = ".int($id_vendors)."
							 WHERE sl_services.Status='Active' 
							 	AND sl_services.ServiceType = 'Purchase'
							 	$query 
							 LIMIT $first, $usr{'pref_maxh'};");
		while ($rec = $sth->fetchrow_hashref){
			$d = 1 - $d;
			$va{'searchresults'} .= qq|
			<tr bgcolor='$c[$d]' onmouseover='m_over(this)' onmouseout='m_out(this)'>
				<td class="smalltext" valign="top">
					<input type="button" class="button" value="S" onclick="trjump('/cgi-bin/mod/$usr{'application'}/dbman?cmd=mer_po&view=$in{'id_purchaseorders'}&addservice=|.($rec->{'SKU'}).qq|')"  onmouseover="m_over(this)" onmouseout="m_out(this)">
				</td>
				<td class="smalltext" valign="top">|.$rec->{'SKU'}.qq|</td>
				<td class="smalltext" valign="top">|.$rec->{'Name'}.qq|</td>
				<td class="smalltext" valign="top">|.$rec->{'Description'}.qq|</td>
				<td class="smalltext" valign="top">|.$rec->{'Tax'}.qq|</td>
			</tr>\n|;
		}
	}else{
		$va{'pageslist'} = 1;
		$va{'searchresults'} = qq|
			<tr>
				<td colspan='5' align="center">  |.&trans_txt('search_nomatches').qq|</td>
			</tr>\n|;
	}
	$in{'id_name'} = "id_purchaseorders";
	$in{'id_value'} = $in{'id_purchaseorders'};
	$va{'header'} = qq|
		<tr>
		    <td class="menu_bar_title">Sel</td>
		    <td class="menu_bar_title">ID</td>
			<td class="menu_bar_title">Name</td>
		    <td class="menu_bar_title">Description</td>
		    <td class="menu_bar_title">Tax %</td>
		 </tr>\n|;
	print "Content-type: text/html\n\n";
	print &build_page('searchid:addid.html');
}

#RB Start
sub products_addrelated {
# --------------------------------------------------------
# Forms Involved: products_tab3
# Created on: 3/28/2008 1:40PM
# Last Modified on: 3/28/2008 
# Last Modified by: Roberto Barcenas
# Author: Roberto Barcenas 
# Description : iFrame to add related items
# Parameters : 

	my ($query);
	if ($in{'keyword'}){
		$query = "AND (Name LIKE '%$in{'keyword'}%' OR Model LIKE '%$in{'keyword'}%' OR ID_products LIKE '%$in{'keyword'}%') ";
	}
	
	my ($sth) = &Do_SQL("SELECT COUNT(*) FROM sl_products WHERE Status<>'Inactive' $query ");
	$va{'matches'} = $sth->fetchrow();
	my (@c) = split(/,/,$cfg{'srcolors'});
	if ($va{'matches'}>0){
		(!$in{'nh'}) and ($in{'nh'}=1);
		$first = ($in{'nh'} - 1) * $usr{'pref_maxh'};			
		($va{'pageslist'},$qs) = &pages_list($in{'nh'},"/cgi-bin/common/apps/schid",$va{'matches'},$usr{'pref_maxh'});
		
		my ($sth) = &Do_SQL("SELECT * FROM sl_products WHERE Status<>'Inactive' $query LIMIT $first,$usr{'pref_maxh'} ");
		while ($rec = $sth->fetchrow_hashref){
			$d = 1 - $d;
			$va{'searchresults'} .= qq|
			<tr bgcolor='$c[$d]' onmouseover='m_over(this)' onmouseout='m_out(this)' onclick="trjump('/cgi-bin/mod/$usr{'application'}/dbman?cmd=mer_products&view=$in{'id_products'}&addritem=$rec->{'ID_products'}&tab=3#tabs#tabs')">
				<td class="smalltext" valign="top">|.&format_sltvid($rec->{'ID_products'}).qq|</td>
				<td class="smalltext">$rec->{'Model'}<br>$rec->{'Name'}</td>
				<td class="smalltext" valign="top" align="right" nowrap>|.&format_price($rec->{'SPrice'}).qq|</td>
			</tr>\n|;
		}
	}else{
		$va{'pageslist'} = 1;
		$va{'searchresults'} = qq|
			<tr>
				<td colspan='5' align="center">  |.&trans_txt('search_nomatches').qq|</td>
			</tr>\n|;
	}
	
	$va{'header'} = qq|
		<tr>
		    <td class="menu_bar_title">ID</td>
		    <td class="menu_bar_title">Model/Name</td>
		    <td class="menu_bar_title">Price</td>
		 </tr>\n|;
	$in{'id_name'} = "id_products";
	$in{'id_value'} = $in{'id_products'};

	print "Content-type: text/html\n\n";
	print &build_page('searchid:addid.html');
}
#RB End


#RB Start
sub products_addrelatedservices {
# --------------------------------------------------------
# Forms Involved: products_tab3
# Created on: 3/31/2008 3:40PM
# Last Modified on: 3/31/2008 
# Last Modified by: Roberto Barcenas
# Author: Roberto Barcenas 
# Description : iFrame to add related non inventory items
# Parameters : 

	my ($query);
	if ($in{'keyword'}){
		$query = "AND (Name LIKE '%$in{'keyword'}%' OR ID_noninv LIKE '%$in{'keyword'}%') ";
	}
	
	my ($sth) = &Do_SQL("SELECT COUNT(*) FROM sl_services WHERE Status<>'Inactive' $query ");
	$va{'matches'} = $sth->fetchrow();
	my (@c) = split(/,/,$cfg{'srcolors'});
	if ($va{'matches'}>0){
		(!$in{'nh'}) and ($in{'nh'}=1);
		$first = ($in{'nh'} - 1) * $usr{'pref_maxh'};			
		($va{'pageslist'},$qs) = &pages_list($in{'nh'},"/cgi-bin/common/apps/schid",$va{'matches'},$usr{'pref_maxh'});
		
		my ($sth) = &Do_SQL("SELECT * FROM sl_services WHERE Status<>'Inactive' $query LIMIT $first,$usr{'pref_maxh'} ");
		while ($rec = $sth->fetchrow_hashref){
			$d = 1 - $d;
			$va{'searchresults'} .= qq|
			<tr bgcolor='$c[$d]' onmouseover='m_over(this)' onmouseout='m_out(this)' onclick="trjump('/cgi-bin/mod/$usr{'application'}/dbman?cmd=mer_products&view=$in{'id_products'}&addrnitem=$rec->{'ID_services'}&tab=3#tabs')">
				<td class="smalltext" valign="top">|.&format_sltvid($rec->{'ID_services'}).qq|</td>
				<td class="smalltext">$rec->{'Model'}<br>$rec->{'Name'}</td>
				<td class="smalltext" valign="top" align="right" nowrap>|.&format_price($rec->{'SPrice'}).qq|</td>
			</tr>\n|;
		}
	}else{
		$va{'pageslist'} = 1;
		$va{'searchresults'} = qq|
			<tr>
				<td colspan='5' align="center">  |.&trans_txt('search_nomatches').qq|</td>
			</tr>\n|;
	}
	
	$va{'header'} = qq|
		<tr>
		    <td class="menu_bar_title">ID</td>
		    <td class="menu_bar_title">Model/Name</td>
		    <td class="menu_bar_title">Price</td>
		 </tr>\n|;
	$in{'id_name'} = "id_products";
	$in{'id_value'} = $in{'id_products'};

	print "Content-type: text/html\n\n";
	print &build_page('searchid:addid.html');
}
#RB End


sub orders_addnoninv {
# --------------------------------------------------------
# Forms Involved: products_tab3
# Created on: 04/21/2008 3:40PM
# Last Modified on: 04/21/2008
# Last Modified by: Roberto Barcenas
# Author: Roberto Barcenas
# Description : iFrame to add non inventory items to an order
# Parameters :
# Last Modified on: 08/25/08 16:17:43
# Last Modified by: MCC C. Gabriel Varela S: 

my ($query);
if ($in{'keyword'}){
$query = "AND (Name LIKE '%$in{'keyword'}%'  OR ID_services LIKE '%$in{'keyword'}%') ";
}

my ($sth) = &Do_SQL("SELECT COUNT(*) FROM sl_services WHERE Status<>'Inactive' $query ");
$va{'matches'} = $sth->fetchrow();
my (@c) = split(/,/,$cfg{'srcolors'});
if ($va{'matches'}>0){
(!$in{'nh'}) and ($in{'nh'}=1);
$first = ($in{'nh'} - 1) * $usr{'pref_maxh'};
($va{'pageslist'},$qs) = &pages_list($in{'nh'},"/cgi-bin/common/apps/schid",$va{'matches'},$usr{'pref_maxh'});

my ($sth) = &Do_SQL("SELECT * FROM sl_services WHERE Status<>'Inactive' $query LIMIT $first,$usr{'pref_maxh'} ");
while ($rec = $sth->fetchrow_hashref){
$d = 1 - $d;
$va{'searchresults'} .= qq|
<tr bgcolor='$c[$d]' onmouseover='m_over(this)' onmouseout='m_out(this)' onclick="trjump('$in{'path'}?cmd=opr_orders&view=$in{'id_orders'}&addnitem=$rec->{'ID_services'}&tab=1#tabs')">
<td class="smalltext" valign="top">|.&format_sltvid(600000000+$rec->{'ID_services'}).qq|</td>
<td class="smalltext">$rec->{'Model'}<br>$rec->{'Name'}</td>
<td class="smalltext" valign="top" align="right" nowrap>|.&format_price($rec->{'SPrice'}).qq|</td>
</tr>\n|;
}
}else{
$va{'pageslist'} = 1;
$va{'searchresults'} = qq|
<tr>
<td colspan='5' align="center"> |.&trans_txt('search_nomatches').qq|</td>
</tr>\n|;
}

$va{'header'} = qq|
<tr>
<td class="menu_bar_title">ID</td>
<td class="menu_bar_title">Model/Name</td>
<td class="menu_bar_title">Price</td>
</tr>\n|;
$in{'id_name'} = "id_products";
$in{'id_value'} = $in{'id_products'};

print "Content-type: text/html\n\n";
print &build_page('searchid:addid.html');
}


sub orders_additems {
# --------------------------------------------------------
# Last Modified on: 08/25/08 16:37:21
# Last Modified by: MCC C. Gabriel Varela S: 
	my ($query);
	$query=" and Status NOT IN ('Testing','Inactive') AND SPrice>0";

	if ($in{'keyword'}){
		$query .= " AND (Name like '%$in{'keyword'}%' OR Model like '%$in{'keyword'}%' OR ID_products like '%$in{'keyword'}%')";
	}
	
	#my ($sth) = &Do_SQL("SELECT COUNT(*) FROM sl_products WHERE Status<>'Inactive' $query;");
	my ($sth) = &Do_SQL("SELECT COUNT(*) FROM sl_products WHERE Status<>'' $query;");
	$va{'matches'} = $sth->fetchrow();
	my (@c) = split(/,/,$cfg{'srcolors'});
	if ($va{'matches'}>0){
		(!$in{'nh'}) and ($in{'nh'}=1);
		$first = ($in{'nh'} - 1) * $usr{'pref_maxh'};			
		($va{'pageslist'},$qs) = &pages_list($in{'nh'},"/cgi-bin/common/apps/schid",$va{'matches'},$usr{'pref_maxh'});
		
		#my ($sth) = &Do_SQL("SELECT * FROM sl_products WHERE Status NOT IN ('Testing','Inactive') AND SPrice>0 $query GROUP BY ID_products LIMIT $first,$usr{'pref_maxh'};");
		my ($sth) = &Do_SQL("SELECT * FROM sl_products WHERE SPrice>0 $query GROUP BY ID_products LIMIT $first,$usr{'pref_maxh'};");
		while ($rec = $sth->fetchrow_hashref){
			$d = 1 - $d;
			$va{'searchresults'} .= qq|
			<tr bgcolor='$c[$d]' onmouseover='m_over(this)' onmouseout='m_out(this)' onclick="trjump('$in{'path'}?cmd=opr_orders&view=$in{'id_orders'}&additem=$rec->{'ID_products'}&qty=1&tab=1#tabs')">
				<td class="smalltext" valign="top">|.&format_sltvid($rec->{'ID_products'}).qq|</td>
				<td class="smalltext">$rec->{'Model'}<br>$rec->{'Name'}</td>
				<td class="smalltext" valign="top" align="right">|.&format_price($rec->{'SPrice'}).qq|</td>
				<td class="smalltext" valign="top" align="right" nowrap>$rec->{'Status'}</td>
			</tr>\n|;
		}
	}else{
		$va{'pageslist'} = 1;
		$va{'searchresults'} = qq|
			<tr>
				<td colspan='4' align="center">  |.&trans_txt('search_nomatches').qq|</td>
			</tr>\n|;
	}
	
	$va{'header'} = qq|
		<tr>
		    <td class="menu_bar_title">ID</td>
		    <td class="menu_bar_title">Model/Name</td>
		    <td class="menu_bar_title">Price</td>
		    <td class="menu_bar_title">Status</td>
		 </tr>\n|;
	$in{'id_name'} = "id_orders";
	$in{'id_value'} = $in{'id_orders'};

	print "Content-type: text/html\n\n";
	print &build_page('searchid:addid.html');
}


sub returns_addupcs{
# --------------------------------------------------------
# Forms Involved: 
# Created on: 10/27/08 12:02:56
# Author: MCC C. Gabriel Varela S.
# Description :   
# Parameters : MCC C. Gabriel Varela S: 
	my ($query);
	$query=" and Status NOT IN ('Inactive')";
	if ($in{'keyword'}){
		$query = " AND (ID_sku_products like '%$in{'keyword'}%' OR ID_products like '%$in{'keyword'}%' OR UPC like '%$in{'keyword'}%')";
	}
	
	#my ($sth) = &Do_SQL("SELECT COUNT(*) FROM sl_products WHERE Status<>'Inactive' $query;");
	my ($sth) = &Do_SQL("SELECT COUNT(*) FROM sl_skus WHERE UPC<>'' $query;");
	$va{'matches'} = $sth->fetchrow();
	my (@c) = split(/,/,$cfg{'srcolors'});
	if ($va{'matches'}>0){
		(!$in{'nh'}) and ($in{'nh'}=1);
		$first = ($in{'nh'} - 1) * $usr{'pref_maxh'};			
		($va{'pageslist'},$qs) = &pages_list($in{'nh'},"/cgi-bin/common/apps/schid",$va{'matches'},$usr{'pref_maxh'});
		
		#my ($sth) = &Do_SQL("SELECT * FROM sl_products WHERE Status NOT IN ('Testing','Inactive') AND SPrice>0 $query GROUP BY ID_products LIMIT $first,$usr{'pref_maxh'};");
		my ($sth) = &Do_SQL("SELECT * FROM sl_skus WHERE UPC<>'' $query LIMIT $first,$usr{'pref_maxh'};");
		while ($rec = $sth->fetchrow_hashref){
			$d = 1 - $d;
			$va{'searchresults'} .= qq|
			<tr bgcolor='$c[$d]' onmouseover='m_over(this)' onmouseout='m_out(this)' onclick="trjump('$in{'path'}?cmd=$in{'cmdo'}&view=$in{'id_returns'}&addupc=$rec->{'UPC'}&qty=1&tab=1#tabs')">
				<td class="smalltext" valign="top">|.$rec->{'UPC'}.qq|</td>
				<td class="smalltext">$rec->{'Model'}<br>$rec->{'ID_sku_products'}</td>
				<td class="smalltext" valign="top" align="right">|.$rec->{'VendorSKU'}.qq|</td>
				<td class="smalltext" valign="top" align="right" nowrap>$rec->{'Status'}</td>
			</tr>\n|;
		}
	}else{
		$va{'pageslist'} = 1;
		$va{'searchresults'} = qq|
			<tr>
				<td colspan='4' align="center">  |.&trans_txt('search_nomatches').qq|</td>
			</tr>\n|;
	}
	
	$va{'header'} = qq|
		<tr>
		    <td class="menu_bar_title">UPC</td>
		    <td class="menu_bar_title">Product ID</td>
		    <td class="menu_bar_title">VendorSKU</td>
		    <td class="menu_bar_title">Status</td>
		 </tr>\n|;
	$in{'id_name'} = "id_returns";
	$in{'id_value'} = $in{'id_returns'};
	$in{'id_name2'} = "cmdo";
	$in{'id_value2'} = $in{'cmdo'};
	print "Content-type: text/html\n\n";
	print &build_page('searchid:addid.html');
}

sub return_additems{
	
}

sub wr_additems {
# --------------------------------------------------------
# Last Modified on: 07/25/08 17:03:14
# Last Modified by: MCC C. Gabriel Varela S: Correcciones generales
# Last Modified on: 06/02/09 17:42:38
# Last Modified by: MCC C. Gabriel Varela S: Se hace que se muestren s�lo los productos que no sean sets.

	my ($query);
	if ($in{'keyword'}ne""){
		$query = "AND (MATCH(sl_products.Name) AGAINST('*".$in{'keyword'}."*' IN BOOLEAN MODE) OR MATCH(sl_products.Model) AGAINST('*".$in{'keyword'}."*' IN BOOLEAN MODE) OR sl_products.ID_products like '%".$in{'keyword'}."%')";
	}
	
	my ($id_vendors) = $in{'id_vendors'};
	my ($sth) = &Do_SQL("SELECT COUNT( * ) FROM sl_products_vendors inner join sl_skus on (sl_products_vendors.ID_products = sl_skus.ID_products) inner join sl_products on (right(sl_skus.ID_products,6)=sl_products.ID_products) WHERE 'Inactive'<>(SELECT Status FROM sl_products WHERE ID_products=sl_skus.ID_products) AND ID_vendors = '$id_vendors' and IsSet='N' $query;");
	$va{'matches'} = $sth->fetchrow();
	my (@c) = split(/,/,$cfg{'srcolors'});
	if ($va{'matches'}>0){
		(!$in{'nh'}) and ($in{'nh'}=1);
		$first = ($in{'nh'} - 1) * $usr{'pref_maxh'};			
		($va{'pageslist'},$qs) = &pages_list($in{'nh'},"/cgi-bin/common/apps/schid",$va{'matches'},$usr{'pref_maxh'});
		my ($sth) = &Do_SQL("SELECT * FROM sl_products_vendors inner join sl_skus on (sl_products_vendors.ID_products = sl_skus.ID_products) inner join sl_products on (right(sl_skus.ID_products,6)=sl_products.ID_products) WHERE 'Inactive'<>(SELECT Status FROM sl_products WHERE ID_products=sl_skus.ID_products) AND ID_vendors = '$id_vendors' and IsSet='N' $query LIMIT $first,$usr{'pref_maxh'};");
		while ($rec = $sth->fetchrow_hashref){
			$d = 1 - $d;
			my ($sth2) = &Do_SQL("SELECT * FROM sl_products WHERE ID_products=$rec->{'ID_products'};");	
			$col = $sth2->fetchrow_hashref;
			$choices = &load_choices('-',$rec->{'choice1'},$rec->{'choice2'},$rec->{'choice3'},$rec->{'choice4'});
			$va{'searchresults'} .= qq|
			<tr bgcolor='$c[$d]' onmouseover='m_over(this)' onmouseout='m_out(this)' onclick="trjump('/cgi-bin/mod/$usr{'application'}/dbman?cmd=wreceipt&view=$in{'id_wreceipts'}&additem=$rec->{'ID_sku_products'}&qty=1&tab=1#tabs')">
				<td class="smalltext" valign="top">|.&format_sltvid($rec->{'ID_sku_products'}).qq|</td>
				<td class="smalltext">$col->{'Model'}<br>$col->{'Name'} $choices</td>
				<td class="smalltext" valign="top" align="right" nowrap>|.&format_price($col->{'SPrice'}).qq|</td>
			</tr>\n|;
		}
	}else{
		$va{'pageslist'} = 1;
		$va{'searchresults'} = qq|
			<tr>
				<td colspan='5' align="center">  |.&trans_txt('search_nomatches').qq|</td>
			</tr>\n|;
	}
	
	$va{'header'} = qq|
		<tr>
		    <td class="menu_bar_title">ID</td>
		    <td class="menu_bar_title">Model/Name</td>
		    <td class="menu_bar_title">Price</td>
		 </tr>\n|;
	$in{'id_name'} = "id_wreceipts";
	$in{'id_value'} = $in{'id_wreceipts'};
	$in{'id_name2'} = "id_vendors";
	$in{'id_value2'} = $in{'id_vendors'};

	print "Content-type: text/html\n\n";
	print &build_page('searchid:addid.html');
}


#############################################################################
#############################################################################
#   Function: wr_addparts
#
#       Es: Muestra listado de SKUs basado en Vendor o PO
#       En: Build SKUs table based on PO / Vendor 
#
#
#    Created on: 2008-07-25
#
#    Author: _MCC C. Gabriel Varela S_
#
#    Modifications:
#
#        - Modified on *2013-03-13* by _Roberto Barcenas_ : Se permite filtrar por PO
#        - Modified on *2013-03-20* by _Alejandro Diaz_ : Se permite seleccion multiple
#
#   Parameters:
#
#
#  Returns:
#
#      - 
#
#   See Also:
#
#      <view_mer_po>
#
sub wr_addparts {
#############################################################################
#############################################################################


	my ($query, $this_query,$this_query2);
	if ($in{'keyword'}){
		#$query = "AND CompanyName like '%$in{'keyword'}%'";
		$query = "AND (sl_parts.Name like '%$in{'keyword'}%' OR sl_parts.Model like '%$in{'keyword'}%' OR sl_parts.ID_parts like '%$in{'keyword'}%')";
	}
	my ($id_vendors) = int($in{'id_vendors'});
	my ($id_po) = int($in{'po'});
	
	($in{'by_vendor'}) ? 
		($this_query = "SELECT COUNT(*) FROM sl_parts_vendors,sl_parts WHERE sl_parts_vendors.ID_parts=sl_parts.ID_parts AND sl_parts.Status='Active' AND ID_vendors='$id_vendors' $query;") :
		($this_query = "SELECT COUNT(*) FROM sl_purchaseorders_items
			INNER JOIN sl_skus ON sl_purchaseorders_items.ID_products=ID_sku_products
			WHERE ID_purchaseorders = '$id_po' AND Qty - Received > 0;");

	($in{'by_vendor'}) ?
		($va{'this_link'} = '<a href="/cgi-bin/common/apps/schid?cmd=wr_addparts&id_vendors='.$id_vendors.'&id_wreceipts='.$in{'id_wreceipts'}.'&po='.$id_po.'&rndnumber='.$in{'rndnumber'}.'" title="By PO"> Show List By PO</a>') :
		($va{'this_link'} = '<a href="/cgi-bin/common/apps/schid?cmd=wr_addparts&id_vendors='.$id_vendors.'&id_wreceipts='.$in{'id_wreceipts'}.'&po='.$id_po.'&rndnumber='.$in{'rndnumber'}.'&by_vendor=1" title="By PO"> Show List By Vendor</a>');
		
					
	$va{'btn_select'} = '<input type="button" class="button" value="Select" id="btn_sel_mult" onmouseover="m_over(this)" onmouseout="m_out(this)" href="/cgi-bin/mod/'.$usr{'application'}.'/dbman?cmd=mer_wreceipts&view='.$in{'id_wreceipts'}.'&qty=1&tab=1">';

	my ($sth) = &Do_SQL($this_query);
	#&cgierr("SELECT COUNT(*) FROM sl_parts_vendors,sl_parts WHERE sl_parts_vendors.ID_parts=sl_parts.ID_parts AND sl_parts.Status='Active' AND ID_vendors='$id_vendors' $query;");
	$va{'matches'} = $sth->fetchrow();
	my $extra_col = '';
	if ($va{'matches'}>0){

		my (@c) = split(/,/,$cfg{'srcolors'});
		(!$in{'nh'}) and ($in{'nh'}=1);
		$first = ($in{'nh'} - 1) * $usr{'pref_maxh'};			
		($va{'pageslist'},$qs) = &pages_list($in{'nh'},"/cgi-bin/common/apps/schid",$va{'matches'},$usr{'pref_maxh'});
		
		($in{'by_vendor'}) ? 
		($this_query2 = "SELECT *,
		( SELECT if((Qty - Received) > 0, SUM(Qty - Received), 0) FROM sl_purchaseorders_items 
			WHERE ID_purchaseorders = '".$in{'po'}."' AND RIGHT(ID_products,4) = sl_parts.ID_parts ) as maxim
		 FROM sl_parts_vendors,sl_parts WHERE sl_parts_vendors.ID_parts=sl_parts.ID_parts AND sl_parts.Status='Active' AND ID_vendors='$id_vendors' $query GROUP BY sl_parts.ID_parts LIMIT $first,$usr{'pref_maxh'};") :
		($this_query2 = "SELECT *,
		( SELECT if((Qty - Received) > 0, SUM(Qty - Received), 0) FROM sl_purchaseorders_items
			WHERE ID_purchaseorders = '".$in{'po'}."' AND RIGHT(sl_purchaseorders_items.ID_products,4) = sl_parts.ID_parts ) as maxim
		 FROM sl_purchaseorders_items
		 INNER JOIN sl_parts ON ID_parts = RIGHT(sl_purchaseorders_items.ID_products,4)
		 INNER JOIN sl_skus ON sl_purchaseorders_items.ID_products=ID_sku_products
		 WHERE ID_purchaseorders = '$id_po' AND Qty - Received > 0 GROUP BY sl_parts.ID_parts;");
		 $extra_col = ($in{'by_vendor'}) ?'':'<td class="menu_bar_title">UPC</td>';
		 
		my ($sth) = &Do_SQL($this_query2);
		while ($rec = $sth->fetchrow_hashref){
			### Se valida la cantidad que a�n se puede seleccionar para la recepci�n
			my $qty_sql = "SELECT SUM(Qty) FROM sl_wreceipts_items WHERE ID_wreceipts=$in{'id_wreceipts'} AND ID_products=400000000+".$rec->{'ID_parts'}.";";
			my $sthQty = &Do_SQL($qty_sql);
			$qty_this_wreceipts = $sthQty->fetchrow();

			### Se obtiene la cantidad disponible para recepcionar
			my $qty_left = $rec->{'maxim'} - $qty_this_wreceipts;

			$d = 1 - $d;
			if( $qty_left > 0 ){
				$va{'searchresults'} .= qq|
				<tr bgcolor='$c[$d]'>
					<td class="smalltext" valign="top"><input type="checkbox" name="additem" value="|.(400000000+$rec->{'ID_parts'}).qq|" class="inpcheck"></td>
					<td class="smalltext" valign="top">
						<input type="button" class="button" value="S" onclick="trjump('/cgi-bin/mod/$usr{'application'}/dbman?cmd=mer_wreceipts&view=$in{'id_wreceipts'}&additem=|.(400000000+$rec->{'ID_parts'}).qq|&qty=|.$rec->{'maxim'}.qq|&tab=1#tabs')"  onmouseover="m_over(this)" onmouseout="m_out(this)">
					</td>|;
			}else{
				$va{'searchresults'} .= qq|
				<tr bgcolor='$c[$d]'>
					<td class="smalltext" valign="top">&nbsp;</td><td class="smalltext" valign="top">&nbsp;</td>|;
			}
			$va{'searchresults'} .= qq|
				<td class="smalltext" valign="top">|.&format_number($qty_left).qq|</td>
				<td class="smalltext" valign="top">|.&format_sltvid(400000000+$rec->{'ID_parts'}).qq|</td>
				<td class="smalltext" valign="top">|.$rec->{'UPC'}.qq|</td>
				<td class="smalltext" valign="top">$rec->{'Model'} $rec->{'Name'}</td>
			</tr>\n|;
		}
	}else{
		$va{'pageslist'} = 1;
		$va{'searchresults'} = qq|
			<tr>
				<td colspan='5' align="center">  |.&trans_txt('search_nomatches').qq|</td>
			</tr>\n|;
	}

	$in{'id_name'} = "id_wreceipts";
	$in{'id_value'} = $in{'id_wreceipts'};
	$va{'header'} = qq|
		<tr>
		    <td class="menu_bar_title"><input type="checkbox" value="" id="checkall" name="checkall"></td>
		    <td class="menu_bar_title">Sel</td>
		    <td class="menu_bar_title">Max</td>
		    <td class="menu_bar_title">ID</td>
			$extra_col
		    <td class="menu_bar_title">Model/Name</td>
		 </tr>\n|;
		 
	$in{'id_name'} = "id_wreceipts";
	$in{'id_value'} = $in{'id_wreceipts'};
	$in{'id_name2'} = "id_vendors";
	$in{'id_value2'} = $in{'id_vendors'};
	$in{'id_name3'} = "po";
	$in{'id_value3'} = $in{'po'};
	
	print "Content-type: text/html\n\n";
	print &build_page('searchid:addid.html');
}

#RB Start
sub products_exchange {
# --------------------------------------------------------
# Forms Involved: qcreturns
# Created on: 3/28/2008 1:40PM
# Last Modified on: 4/30/2008 
# Last Modified by: Jose Ramirez to exchange products on returns
# Author: Roberto Barcenas 
# Description : iFrame to add related items
# Parameters : 
# Last Modified on: 09/12/08 13:41:41
# Last Modified by: MCC C. Gabriel Varela S: Se hace que se muestren las opciones del producto cuando se va a elegir uno
# Last Modified on: 10/14/08 11:28:07
# Last Modified by: MCC C. Gabriel Varela S: Se corrige error de b�squeda y luego seleccionar producto con choices

	my ($query);
	if ($in{'keyword'}){
		$query = "AND (Name LIKE '%$in{'keyword'}%' OR Model LIKE '%$in{'keyword'}%' OR ID_products LIKE '%$in{'keyword'}%') ";
	}
	
	my ($sth) = &Do_SQL("SELECT COUNT(*) FROM sl_products WHERE Status<>'Inactive' $query ");
	$va{'matches'} = $sth->fetchrow();
	my (@c) = split(/,/,$cfg{'srcolors'});
	if ($va{'matches'}>0){
		(!$in{'nh'}) and ($in{'nh'}=1);
		$first = ($in{'nh'} - 1) * $usr{'pref_maxh'};			
		($va{'pageslist'},$qs) = &pages_list($in{'nh'},"/cgi-bin/common/apps/schid",$va{'matches'},$usr{'pref_maxh'});
		
		my ($sth) = &Do_SQL("SELECT * FROM sl_products WHERE Status<>'Inactive' $query LIMIT $first,$usr{'pref_maxh'} ");
		while ($rec = $sth->fetchrow_hashref){
			$d = 1 - $d;
			$id_products = &load_name('sl_skus','ID_products',$rec->{'ID_products'},'ID_sku_products');
			$choices=&build_edit_choices($id_products,$in{'path'},"cmd=$in{'cmdret'}&modify=$in{'id_returns'}&meraction=Exchange");
			$onclickstr='';
			$onclickstr="onclick=\"window.top.document.sitform.id_products_exchange.value='$id_products';window.top.document.getElementById('popup_ritem').style.visibility='hidden';window.top.document.getElementById('popup_ritem').style.display='none';\"" if($choices eq '');
			$va{'searchresults'} .= qq|
			<tr bgcolor='$c[$d]' onmouseover='m_over(this)' onmouseout='m_out(this)' $onclickstr>
				<td class="smalltext" valign="top">|.&format_sltvid($id_products).$choices.qq|</td>
				<td class="smalltext">$rec->{'Model'}<br>$rec->{'Name'}</td>
				<td class="smalltext" valign="top" align="right" nowrap>|.&format_price($rec->{'SPrice'}).qq|</td>
			</tr>\n|;
		}
	}else{
		$va{'pageslist'} = 1;
		$va{'searchresults'} = qq|
			<tr>
				<td colspan='5' align="center">  |.&trans_txt('search_nomatches').qq|</td>
			</tr>\n|;
	}
	
	$va{'header'} = qq|
		<tr>
		    <td class="menu_bar_title">ID</td>
		    <td class="menu_bar_title">Model/Name</td>
		    <td class="menu_bar_title">Price</td>
		 </tr>\n|;
	$in{'id_name'} = "id_products";
	$in{'id_value'} = $in{'id_products'};
	$in{'cmdret'} = $in{'cmdret'};
	$in{'modify'} = $in{'modify'};
	print "Content-type: text/html\n\n";
	print &build_page('products_exchange.html');
}
#RB End


sub customers_submit {
# --------------------------------------------------------
# Last Modified on: 07/22/08 12:13:54
# Last Modified by: MCC C. Gabriel Varela S: Se verifica el m�dulo desde el que se llama a la funci�n. La opci�n por defecto es Administration y subfijo=opr_
# Last Modified on: 09/17/08 16:51:16
# Last Modified by: MCC C. Gabriel Varela S: el subfijo ser� constante
	my ($script_path,$subfijo,$urltojump,$ref);
	$script_path="/cgi-bin/mod/".$usr{'application'}."/dbman";
	$subfijo="opr_orders";
	
	$urltojump = qq| onclick="trjump('$script_path?cmd=$subfijo&add=1&loadaddress=1 |;  #"
	$ref = "";
	if($in{'urlpathy'}ne"")	{
		$script_path=$in{'urlpathy'};
		$in{'urlpathy'}=~/cgi-bin\/(.*)\//;
		if($1 ne "administration")
		{
			$subfijo="opr_orders";
			$in{'id_name'} = "id_purchaseorders";
			$in{'id_value'} = $in{'id_purchaseorders'};
			$ref = "#id_customers";
		}
	}elsif($in{'pathurlmov'}){
		$script_path = $in{'pathurlmov'};
		$subfijo     = $in{'cmdrecieve'};
		$urltojump = qq| onclick="trjump('$script_path?cmd=$subfijo&view=$in{'view'}&tab=$in{'in_tab'} |;  #"
		
		$in{'id_name2'}  = "pathurlmov";
		$in{'id_value2'} = $script_path;
		
		$in{'id_name3'}  = "tab";
		$in{'id_value3'} = $in{'tab'};	

		$in{'id_name4'}  = "view";
		$in{'id_value4'} = $in{'view'};	
		
		$in{'id_name'}  = "cmdrecieve";
		$in{'id_value'} = $in{'cmdrecieve'};
	}
	
	my ($query);
	if ($in{'keyword'}){
		$query = "AND (ID_customers LIKE '%$in{'keyword'}%' OR company_name LIKE '%$in{'keyword'}%' OR FirstName like '%$in{'keyword'}%' OR LastName1 like '%$in{'keyword'}%' OR LastName2 like '%$in{'keyword'}%' OR Phone1 like '%$in{'keyword'}%' OR Phone2 like '%$in{'keyword'}%' OR Cellphone like '%$in{'keyword'}%')";
	}

	my ($sth) = &Do_SQL("SELECT COUNT(*) FROM sl_customers WHERE Status='Active' $query;");
	$va{'matches'} = $sth->fetchrow();
	my (@c) = split(/,/,$cfg{'srcolors'});
	if ($va{'matches'}>0){
		(!$in{'nh'}) and ($in{'nh'}=1);
		$first = ($in{'nh'} - 1) * $usr{'pref_maxh'};			
		($va{'pageslist'},$qs) = &pages_list($in{'nh'},"/cgi-bin/common/apps/schid",$va{'matches'},$usr{'pref_maxh'});
		
		my ($sth) = &Do_SQL("SELECT * FROM sl_customers WHERE Status='Active' $query LIMIT $first,$usr{'pref_maxh'};");
		while ($rec = $sth->fetchrow_hashref){
			$d = 1 - $d;
			$va{'searchresults'} .= qq|
			<tr bgcolor='$c[$d]' onmouseover='m_over(this)' onmouseout='m_out(this)' $urltojump&id_customers=$rec->{'ID_customers'}$ref')" >
				<td class="smalltext" valign="top">$rec->{'ID_customers'}</td>
				<td class="smalltext">$rec->{'company_name'} </td>
				<td class="smalltext">$rec->{'FirstName'}</td>
				<td class="smalltext">$rec->{'LastName1'} $rec->{'LastName2'}</td>
				<td class="smalltext">$rec->{'Phone1'} $rec->{'Phone2'} $rec->{'Cellphone'}</td>
			</tr>\n|;  #'
		}
	}else{
		$va{'pageslist'} = 1;
		$va{'searchresults'} = qq|
			<tr>
				<td colspan='5' align="center">  |.&trans_txt('search_nomatches').qq|</td>
			</tr>\n|;
	}
	
	$va{'header'} = qq|
		<tr>
		    <td class="menu_bar_title">ID</td>
		    <td class="menu_bar_title">Company</td>
		    <td class="menu_bar_title">First Name</td>
		    <td class="menu_bar_title">Last Name</td>
		    <td class="menu_bar_title">Phones</td>
		 </tr>\n|; 
	print "Content-type: text/html\n\n";
	print &build_page('searchid:addid.html');
}

sub accounts_submit {
# --------------------------------------------------------
# Last Modified on: 07/22/08 12:13:54
# Last Modified by: MCC C. Gabriel Varela S: Se verifica el m�dulo desde el que se llama a la funci�n. La opci�n por defecto es Administration y subfijo=opr_
# Last Modified on: 09/17/08 16:51:16
# Last Modified by: MCC C. Gabriel Varela S: el subfijo ser� constante
# 
	my ($script_path,$subfijo,$urltojump,$ref);
	$script_path="/cgi-bin/mod/".$usr{'application'}."/dbman";
	$subfijo="opr_orders";
	
	$urltojump = qq| onclick="trjump('$script_path?cmd=$subfijo&add=1&loadaddress=1 |;  #"
	$ref = "";
	if($in{'urlpathy'}ne""){

		$script_path=$in{'urlpathy'};
		$in{'urlpathy'}=~/cgi-bin\/(.*)\//;
		
		if($1 ne "administration"){

			$subfijo="opr_orders";
			$in{'id_name'} = "id_purchaseorders";
			$in{'id_value'} = $in{'id_purchaseorders'};
			$ref = "#id_customers";
		}

	}elsif($in{'pathurlmov'}){

		$script_path = $in{'pathurlmov'};
		$subfijo     = $in{'cmdrecieve'};
		$urltojump = qq| onclick="trjump('$script_path?cmd=$subfijo&view=$in{'view'}&tab=$in{'in_tab'} |;  #"
		
		$in{'id_name2'}  = "pathurlmov";
		$in{'id_value2'} = $script_path;
		
		$in{'id_name3'}  = "tab";
		$in{'id_value3'} = $in{'tab'};	

		$in{'id_name4'}  = "view";
		$in{'id_value4'} = $in{'view'};	
		
		$in{'id_name'}  = "cmdrecieve";
		$in{'id_value'} = $in{'cmdrecieve'};
	}
	
	my ($query);
	if ($in{'keyword'}){
		$query = "AND (ID_accounts LIKE '%$in{'keyword'}%' OR Name LIKE '%$in{'keyword'}%' OR ID_accounting like '%$in{'keyword'}%')";
	}

	my ($sth) = &Do_SQL("SELECT COUNT(*) FROM sl_accounts WHERE 1 $query AND ID_accounts > 1000;");
	$va{'matches'} = $sth->fetchrow();
	my (@c) = split(/,/,$cfg{'srcolors'});
	if ($va{'matches'}>0){
		(!$in{'nh'}) and ($in{'nh'}=1);
		$first = ($in{'nh'} - 1) * $usr{'pref_maxh'};			
		($va{'pageslist'},$qs) = &pages_list($in{'nh'},"/cgi-bin/common/apps/schid",$va{'matches'},$usr{'pref_maxh'});
		
		my ($sth) = &Do_SQL("SELECT 
								ID_accounts
								, Name
								, ID_accounting
								, Status 
							FROM 
								sl_accounts 
							WHERE 
								1 
								$query
								 AND ID_accounts > 1000 
							LIMIT 
								$first,$usr{'pref_maxh'};");
		while ($rec = $sth->fetchrow_hashref){
			$d = 1 - $d;

			my $account_status_link = $rec->{'Status'} eq 'Active' ?
									"<tr bgcolor='$c[$d]' onmouseover='m_over(this)' onmouseout='m_out(this)' onclick='select_row(this);' >" :
									"<tr bgcolor='#F6989D'>" ;

			$va{'searchresults'} .= 
				$account_status_link . qq|
				<td class="smalltext" valign="top">$rec->{'ID_accounts'}</td>
				<td class="smalltext">$rec->{'ID_accounting'} </td>
				<td class="smalltext">$rec->{'Name'}</td>
				
			</tr>\n|;
		}
	}else{
		$va{'pageslist'} = 1;
		$va{'searchresults'} = qq|
			<tr>
				<td colspan='5' align="center">  |.&trans_txt('search_nomatches').qq|</td>
			</tr>\n|;
	}
	
	$va{'header'} = qq|
		<tr>
		    <td class="menu_bar_title">ID Accounts</td>
		    <td class="menu_bar_title">ID Accounting</td>
		    <td class="menu_bar_title">Name</td>
		    
		 </tr>\n|;
	 $va{'element_id'} = $in{'element_id'};
	 $va{'hide_element'} = $in{'hide_element'};
	print "Content-type: text/html\n\n";
	print &build_page('searchid:account.html');
}

sub orders_addshp {
# --------------------------------------------------------
# Forms Involved: products_tab1
# Created on: 06/19/2008 9:54 AM
# Last Modified on:
# Last Modified by:
# Author: Jose Ramirez Garcia
# Description : iFrame to add shipping discount
# Parameters :
	print "Content-type: text/html\n\n";
	print &build_page('searchid:amount.html');
}


sub orders_addfee {
# --------------------------------------------------------
# Forms Involved: products_tab1
# Created on: 06/20/2008 12:00 PM
# Last Modified on:
# Last Modified by:
# Author: Jose Ramirez Garcia
# Description : iFrame to select the products and add fees
# Parameters :
	my ($sth) = &Do_SQL("SELECT * FROM `sl_orders_products` WHERE LEFT(`ID_products`,1)=1 AND id_orders=$in{'id_orders'};");
	$va{'matches'} = $sth->fetchrow();
	my (@c) = split(/,/,$cfg{'srcolors'});
	if ($va{'matches'}>0){				
		my ($sth1) = &Do_SQL("SELECT * FROM `sl_orders_products` WHERE LEFT(`ID_products`,1)=1 AND id_orders=$in{'id_orders'} ORDER BY ID_orders_products DESC;");
		my ($col);
		while ($col = $sth1->fetchrow_hashref){
			$d = 1 - $d;
			$sku_id_p=substr($col->{'ID_products'},3,6);
			$sku_id_e=$col->{'ID_products'};
			$sku_id_d=format_sltvid($col->{'ID_products'});
		
			my ($sthk) = &Do_SQL("SELECT * FROM sl_skus WHERE ID_sku_products='$col->{'ID_products'}' and Status='Active'");
			$rec = $sthk->fetchrow_hashref;
			$choices = &load_choices('-',$rec->{'choice1'},$rec->{'choice2'},$rec->{'choice3'},$rec->{'choice4'});

			if($in{'feetype'} eq "return"){
				my ($nm) = &Do_SQL("SELECT Weight FROM sl_products WHERE ID_products=$sku_id_p;");
				$in{'weight'} = $nm->fetchrow();
				$va{'searchresults'} .= qq|<tr bgcolor='$c[$d]' onmouseover='m_over(this)' onmouseout='m_out(this)' onclick="trjump('$in{'path'}?cmd=opr_orders&view=$in{'id_orders'}&fee=1&returnfee=1&weight=$in{'weight'}&related_id=$col->{'ID_products'}&tab=1#tabs')">\n|;
			} elsif($in{'feetype'} eq "restock"){
				my ($pr) = &Do_SQL("SELECT SPrice FROM sl_products WHERE ID_products=$sku_id_p;");
				$sprice = $pr->fetchrow();
				$va{'searchresults'} .= qq|<tr bgcolor='$c[$d]' onmouseover='m_over(this)' onmouseout='m_out(this)' onclick="trjump('$in{'path'}?cmd=opr_orders&view=$in{'id_orders'}&fee=1&restockfee=1&product_sprice=$sprice&related_id=$col->{'ID_products'}&tab=1#tabs')">\n|;
			} else {
				$va{'searchresults'} .= qq|<tr bgcolor='$c[$d]' onmouseover='m_over(this)' onmouseout='m_out(this)' >\n|;
			}
			$va{'searchresults'} .= " <td class='smalltext' valign='top'>";

     	### Products
      $va{'searchresults'} .= &format_sltvid($col->{'ID_products'})."--".substr($col->{'ID_products'},0,1)."</td>\n";		
      (!$col->{'SerialNumber'}) and ($col->{'SerialNumber'} = '---');
			($status,%tmp) = &load_product_info($sku_id_p);
			$va{'searchresults'} .= "  <td class='smalltext' valign='top'>$tmp{'model'}<br>".substr($tmp{'name'},0,30)." ".$choices."</td>\n";
			
			$va{'searchresults'} .= "  <td class='smalltext' valign='top'> $col->{'SerialNumber'}</td>\n";
			$va{'searchresults'} .= "  <td class='smalltext' valign='top'> $col->{'ShpDate'}<br>$tmp{'shpprovider'} $tmp{'tracking'}</td>\n";
			if ($col->{'Status'} eq 'Inactive'){
				$decor = " style=' text-decoration: line-through'";
			}else{
				$decor ='';
				$tot_qty += $col->{'Quantity'};
				$tot_ord +=$col->{'SalePrice'}*$col->{'Quantity'};
			}
			$va{'searchresults'} .= "  <td class='smalltext' align='right' valign='top' $decor>".&format_number($col->{'Quantity'})."</td>\n";
			$va{'searchresults'} .= "  <td class='smalltext' align='right' valign='top' $decor>".&format_price($col->{'Shipping'})."</td>\n";
			$va{'searchresults'} .= "  <td class='smalltext' align='right' valign='top' $decor>".&format_price($col->{'SalePrice'})."</td>\n";
			$va{'searchresults'} .= "</tr>\n";						
		}
	}else{
		$va{'pageslist'} = 1;
		$va{'searchresults'} = qq|
			<tr>
				<td colspan='6' align="center">|.&trans_txt('search_nomatches').qq|</td>
			</tr>\n|;
	}			
	print "Content-type: text/html\n\n";
	print &build_page('searchid:productsinorder.html');
}

sub products_rm {
# --------------------------------------------------------
# Forms Involved: opr_repmemos
# Created on: 3/28/2008 1:40PM
# Last Modified on: 06/30/2008 
# Last Modified by: Jose Ramirez to add products on repmemos
# Author: Roberto Barcenas 
# Description : iFrame to add related items
# Parameters : 

	my ($query);
	if ($in{'keyword'}){
		$query = "AND (Name LIKE '%$in{'keyword'}%' OR Model LIKE '%$in{'keyword'}%' OR ID_products LIKE '%$in{'keyword'}%') ";
	}
	
	my ($sth) = &Do_SQL("SELECT COUNT(*) FROM sl_products WHERE Status<>'Inactive' $query ");
	$va{'matches'} = $sth->fetchrow();
	my (@c) = split(/,/,$cfg{'srcolors'});
	if ($va{'matches'}>0){
		(!$in{'nh'}) and ($in{'nh'}=1);
		$first = ($in{'nh'} - 1) * $usr{'pref_maxh'};			
		($va{'pageslist'},$qs) = &pages_list($in{'nh'},"/cgi-bin/common/apps/schid",$va{'matches'},$usr{'pref_maxh'});
		
		my ($sth) = &Do_SQL("SELECT * FROM sl_products WHERE Status<>'Inactive' $query LIMIT $first,$usr{'pref_maxh'} ");
		while ($rec = $sth->fetchrow_hashref){
			$d = 1 - $d;
			$id_products = &load_name('sl_skus','ID_products',$rec->{'ID_products'},'ID_sku_products');
			$va{'searchresults'} .= qq|
			<tr bgcolor='$c[$d]' onmouseover='m_over(this)' onmouseout='m_out(this)' onclick="window.top.document.sitform.id_products.value='$id_products';window.top.document.getElementById('popup_product').style.visibility='hidden';window.top.document.getElementById('popup_product').style.display='none';">
				<td class="smalltext" valign="top">|.&format_sltvid($id_products).qq|</td>
				<td class="smalltext">$rec->{'Model'}<br>$rec->{'Name'}</td>
				<td class="smalltext" valign="top" align="right" nowrap>|.&format_price($rec->{'SPrice'}).qq|</td>
			</tr>\n|;
		}
	}else{
		$va{'pageslist'} = 1;
		$va{'searchresults'} = qq|
			<tr>
				<td colspan='5' align="center">  |.&trans_txt('search_nomatches').qq|</td>
			</tr>\n|;
	}
	
	$va{'header'} = qq|
		<tr>
		    <td class="menu_bar_title">ID</td>
		    <td class="menu_bar_title">Model/Name</td>
		    <td class="menu_bar_title">Price</td>
		 </tr>\n|;
	$in{'id_name'} = "id_products";
	$in{'id_value'} = $in{'id_products'};

	print "Content-type: text/html\n\n";
	print &build_page('products_exchange.html');
}

sub parts_rm {
# --------------------------------------------------------
# Forms Involved: opr_repmemos
# Created on: 3/28/2008 1:40PM
# Last Modified on: 06/30/2008 
# Last Modified by: Jose Ramirez to add products on repmemos
# Author: Roberto Barcenas 
# Description : iFrame to add related items
# Parameters : 

	my ($query);
	if ($in{'keyword'}){
		$query = "AND (Name LIKE '%$in{'keyword'}%' OR Model LIKE '%$in{'keyword'}%' OR ID_parts LIKE '%$in{'keyword'}%') ";
	}
	
	my ($sth) = &Do_SQL("SELECT COUNT(*) FROM sl_parts WHERE Status<>'Inactive' $query ");
	$va{'matches'} = $sth->fetchrow();
	my (@c) = split(/,/,$cfg{'srcolors'});
	if ($va{'matches'}>0){
		(!$in{'nh'}) and ($in{'nh'}=1);
		$first = ($in{'nh'} - 1) * $usr{'pref_maxh'};			
		($va{'pageslist'},$qs) = &pages_list($in{'nh'},"/cgi-bin/common/apps/schid",$va{'matches'},$usr{'pref_maxh'});
		
		my ($sth) = &Do_SQL("SELECT * FROM sl_parts WHERE Status<>'Inactive' $query LIMIT $first,$usr{'pref_maxh'} ");
		while ($rec = $sth->fetchrow_hashref){
			$d = 1 - $d;
			#$id_products = &load_name('sl_skus','ID_products',$rec->{'ID_products'},'ID_sku_products');
			$id_parts = 400000000+$rec->{'ID_parts'};
			$va{'searchresults'} .= qq|
			<tr bgcolor='$c[$d]' onmouseover='m_over(this)' onmouseout='m_out(this)' onclick="window.top.document.sitform.id_products.value='$id_parts';window.top.document.getElementById('popup_part').style.visibility='hidden';window.top.document.getElementById('popup_part').style.display='none';">
				<td class="smalltext" valign="top">|.&format_sltvid($id_parts).qq|</td>
				<td class="smalltext">$rec->{'Model'}<br>$rec->{'Name'}</td>
			</tr>\n|;
		}
	}else{
		$va{'pageslist'} = 1;
		$va{'searchresults'} = qq|
			<tr>
				<td colspan='5' align="center">  |.&trans_txt('search_nomatches').qq|</td>
			</tr>\n|;
	}
	
	$va{'header'} = qq|
		<tr>
		    <td class="menu_bar_title">ID</td>
		    <td class="menu_bar_title">Model/Name</td>
		 </tr>\n|;
	$in{'id_name'} = "id_products";
	$in{'id_value'} = $in{'id_products'};

	print "Content-type: text/html\n\n";
	print &build_page('products_exchange.html');
}

sub load_script_variables{
# --------------------------------------------------------
# Last Modified on: 09/04/08 10:05:03
# Last Modified by: MCC C. Gabriel Varela S: Copiada desde otro lado, basada en la funci�n del mismo nombre
	my ($idproducts)=@_;
	#$idproducts=1;
	#Acci�n: Creaci�n
	#Comentarios:
	# --------------------------------------------------------
	# Forms Involved: 
	# Created on: 28/may/2008 16:14PM GMT -0600
	# Last Modified on:
	# Last Modified by:
	# Author: MCC C. Gabriel Varela S.
	# Description :  Genera las variables para tomarse en cuenta por el archivo: Y:\domains\dev.shoplatinotv.com\cgi-bin\templates\en\app\cc-inbound\script.html
	# Parameters : 
	
	# Last Modified on: 07/14/08 11:31:37
  # Last Modified by: MCC C. Gabriel Varela S: Se cambia el nombre de la funci�n de load_paguitos a load_script_variables
#  &converts_in_to_va();
#  &converts_cses_to_va();

# Last Modified on: 07/14/08 16:22:24
# Last Modified by: MCC C. Gabriel Varela S: Se manda a llamar a la funci�n load_variables que carga los valores para ser utilizados en los speeches
# Last Modified on: 10/26/09 09:30:56
# Last Modified by: MCC C. Gabriel Varela S: Se hace que $rec->{'Flexipago'} sea igual a uno si no tiene un valor espec�fico, para evitar divisi�n por 0


	&load_variables();
	my $sth=&Do_SQL("SELECT * FROM sl_products WHERE ID_products=$idproducts");
	my $rec=$sth->fetchrow_hashref();
	$va{'productname'}=$rec->{'Name'};
	$va{'months'}=$rec->{'Flexipago'};
	$va{'weeks'}=$rec->{'Flexipago'}*4;
	$va{'price'} = $rec->{'SPrice'};
	
	
	if ($rec->{'FPPrice'}>0){
		$va{'discountporc'} = int($rec->{'SPrice'}/$rec->{'FPPrice'});
		$va{'discountvakue'} = &format_price($rec->{'FPPrice'}-$rec->{'SPrice'});
		$va{'onepayment'} = &format_price($rec->{'SPrice'});
		$va{'weeklyprice'}=&format_price($rec->{'FPPrice'}/$rec->{'Flexipago'}/4);
		$va{'monthlyprice'}=&format_price($rec->{'FPPrice'}/$rec->{'Flexipago'});
		$va{'sprice'}=&format_price($rec->{'FPPrice'});
		$va{'weekdownpayment'}=&format_price($rec->{'FPPrice'}/$rec->{'Flexipago'}/4+99+$va{'shipping'});
	}else{
		if ($idproducts =~ /$cfg{'disc40'}/){
			$va{'discountporc'}= 40;
			$va{'discountvakue'}=&format_price($rec->{'SPrice'}*40/100);
			$va{'onepayment'} = &format_price($rec->{'SPrice'}-$rec->{'SPrice'}*40/100);
		}elsif ($idproducts =~ /$cfg{'disc30'}/){
			$va{'discountporc'}= 30;
			$va{'discountvakue'}=&format_price($rec->{'SPrice'}*30/100);
			$va{'onepayment'} = &format_price($rec->{'SPrice'}-$rec->{'SPrice'}*30/100);
		}else{
			$va{'discountporc'}=$cfg{'fpdiscount'.$rec->{'Flexipago'}};
			$va{'discountvakue'}=&format_price($rec->{'SPrice'}*$cfg{'fpdiscount'.$rec->{'Flexipago'}}/100);
			$va{'onepayment'} = &format_price($rec->{'SPrice'}-$rec->{'SPrice'}*$cfg{'fpdiscount'.$rec->{'Flexipago'}}/100);
		}
		$rec->{'Flexipago'}=1 if(!$rec->{'Flexipago'});
		$va{'weeklyprice'}=&format_price($rec->{'SPrice'}/$rec->{'Flexipago'}/4);
		$va{'monthlyprice'}=&format_price($rec->{'SPrice'}/$rec->{'Flexipago'});
		$va{'sprice'}=&format_price($rec->{'SPrice'});
		$va{'weekdownpayment'}=&format_price($rec->{'SPrice'}/$rec->{'Flexipago'}/4+99+$va{'shipping'});
	}
	
	$va{'beweekly3'} = &format_price($rec->{'SPrice'} / 3);
	$va{'shipping'} = &load_regular_shipping($idproducts);
	$va{'shipping'} = &format_price($va{'shipping'});
	
	my $sth=&Do_SQL("SELECT DATE_ADD(CURDATE(), INTERVAL 2 WEEK)");
	$va{'secondpaybeweekly3'} = $sth->fetchrow;
	
	my $sth=&Do_SQL("SELECT DATE_ADD(CURDATE(), INTERVAL 1 MONTH)");
	$va{'tirdpaybeweekly3'} = $sth->fetchrow;
	
	$va{'firstpayment'} = &format_price($rec->{'SPrice'}/$rec->{'Flexipago'}+&load_regular_shipping($idproducts),2);
	
	return;
}

sub show_script {
# --------------------------------------------------------

# Author: Jose Ramirez Garcia
# Created on: 8/7/2008
# Last Modified on: 
# Last Modified by: 
# Description : 
# Forms Involved: 
# Parameters : 
# Last Modified on: 09/03/08 19:15:51
# Last Modified by: MCC C. Gabriel Varela S: Last promo
# Last Modified on: 09/04/08 11:24:40
# Last Modified by: MCC C. Gabriel Varela S: Se hace que siempre se muestren los nuevos speeches
	
	my ($dir);
	print "Content-type: text/html\n\n";
	my($sql)=&Do_SQL("SELECT Speech FROM sl_products INNER JOIN sl_speech ON (sl_products.ID_products_speech=sl_speech.ID_speech) WHERE ID_products=$in{'id_products'}");
	$in{'speech'}=$sql->fetchrow();
	if($in{'speech'}){
		$va{'product_tab'}=qq|<td class="cell_off" align="center"><a href='/cgi-bin/common/apps/schid?cmd=show_script&id_products=[in_id_products]'>[in_id_products]</a></td>|;
	}
	if($in{'fm'}){
		$files_module = $in{'fm'};
	} else {
		$files_module = "administration"; 
	}
	&load_script_variables($in{'id_products'});

	if($in{'name'} && -e "../../templates/$usr{'pref_language'}/app/$files_module/$in{'name'}.html"){
		if($cfg{'lastpromo'})
		{
			if ($in{'id_products'}=~ /$cfg{'lastpromoprods'}/ or 1)
			{
				$in{'name'}.="lastp";
			}
		}
		elsif($cfg{'mailinrebatepromo'}){
			if ($in{'id_products'}=~ /$cfg{'discmailinrebate'}/ or 1){
				if(-e "../../templates/$usr{'pref_language'}/app/$files_module/$in{'name'}mailinrebate.html"){
					$in{'name'}.="mailinrebate";
				}
			}
		}

		print &build_page("$in{'name'}.html");
	}elsif($in{'speech'}){
		print &build_page('product_script.html');
	}else {
		print &build_page('script.html');
	}
}

sub enter_shipment_show {
# --------------------------------------------------------

# Author: Jose Ramirez Garcia
# Created on: 08/15/2008
# Last Modified on: 
# Last Modified by: 
# Description : it show the items/parts to add shipment information
# Forms Involved: opr_orders_view
# Parameters : 

# Last Modified on: 09/24/08  12:02:19
# Last Modified by: Roberto Barcenas
# Last Modified Desc: it is possible to change shipdates to product thaty already have it (not in production yet)
	
	if($in{'id_orders'}){
		my ($sth0) = &Do_SQL("SELECT ID_orders_products,IsSet FROM sl_orders_products INNER JOIN sl_skus ON(sl_orders_products.ID_products=sl_skus.ID_sku_products) WHERE sl_orders_products.id_orders='$in{'id_orders'}'");
		while ($tmp0 = $sth0->fetchrow_hashref){
			if ($tmp0->{'IsSet'} eq 'Y'){
				&check_kit_shipped($tmp0->{'ID_orders_products'},'orders');	      	
      }
		}
		my (@c) = split(/,/,$cfg{'srcolors'});
		my ($sth1) = &Do_SQL("SELECT COUNT(*) FROM sl_orders_products WHERE ID_orders='$in{'id_orders'}' AND LEFT(sl_orders_products.ID_products,1)<>'6'");
		$va{'matches'} = $sth1->fetchrow;
		if ($va{'matches'}>0){
			my ($sth2) = &Do_SQL("SELECT sl_orders_products.*,sl_skus.* FROM sl_orders_products INNER JOIN sl_skus ON(sl_orders_products.ID_products=sl_skus.ID_sku_products) WHERE sl_orders_products.id_orders='$in{'id_orders'}' AND LEFT(sl_orders_products.ID_products,1)<>'6' ORDER BY ID_orders_products DESC");
			while ($col = $sth2->fetchrow_hashref){
				$d = 1 - $d;
				$sku_id_p=substr($col->{'ID_products'},3,6);
				$sku_id_e=$col->{'ID_products'};
				$sku_id_d=format_sltvid($col->{'ID_products'});				
			  if ($col->{'IsSet'} eq 'Y'){
	      	### SETS / Kits
					$va{'searchresults'} .= "<tr bgcolor='$c[$d]' onmouseover='m_over(this)' onmouseout='m_out(this)'>\n";
					$va{'searchresults'} .= " <td class='smalltext' valign='top'>";
	      	### Products
	      	$va{'searchresults'} .= &format_sltvid($col->{'ID_sku_products'});
					$va{'searchresults'} .= "</td>\n";		
					(!$col->{'SerialNumber'}) and ($col->{'SerialNumber'} = '---');
					($status,%tmp) = &load_product_info($col->{'ID_products'});
					$va{'searchresults'} .= "  <td class='smalltext' valign='top'>$tmp{'model'}<br>".substr($tmp{'name'},0,30)." </td>\n";
					$va{'searchresults'} .= "  <td class='smalltext' valign='top'> $col->{'SerialNumber'} </td>\n";
					$tracking1 = &build_tracking_link($col->{'Tracking'},$col->{'ShpProvider'},$col->{'ShpDate'},$col->{'ID_products'});
					$tracking1 =~ s/More Info//; 
					$va{'searchresults'} .= "  <td class='smalltext' valign='top'>".$tracking1."</td>\n";
					$va{'searchresults'} .= "</tr>\n";
					my ($sth3) = &Do_SQL("SELECT * FROM sl_skus_parts WHERE ID_sku_products='$col->{'ID_sku_products'}';");
					while ($tmp = $sth3->fetchrow_hashref){
						for my $i(1..$tmp->{'Qty'}){
							my ($linkedit) = '';
							my ($chkship) = '';
							my ($sth3) = &Do_SQL("SELECT * FROM sl_orders_parts WHERE ID_orders_products='$col->{'ID_orders_products'}' AND ID_parts='$tmp->{'ID_parts'}' LIMIT 0,1;");
							my ($shp) = $sth3->fetchrow_hashref;
							if($shp->{'ShpDate'} and $shp->{'ShpDate'} ne "0000-00-00"){
								$tracking2 = &build_tracking_link($shp->{'Tracking'},$shp->{'ShpProvider'},$shp->{'ShpDate'},400000000+$tmp->{'ID_parts'});
								$tracking2 =~ s/More Info//;
								
								$linkedit = qq|onclick="chgShip('$shp->{'Tracking'}','$shp->{'ShpProvider'}','$shp->{'ShpDate'}')" |;
							}
															
							$chk_id_parts = 400000000+$tmp->{'ID_parts'};		
							$chkship = qq| <input type='checkbox' class='checkbox' name="chk_part_$chk_id_parts" value="$col->{'ID_orders_products'}" $linkedit>|;
							(!$tmp->{'Serial'}) and ($tmp->{'Serial'} = '---');
							
							$va{'searchresults'} .= qq|<tr bgcolor='$c[$d]' onmouseover='m_over(this)' onmouseout='m_out(this)' $linkedit>
							<td class='smalltext' $style valign='top' align='left' >
									&nbsp;
									$chkship |.&format_sltvid(400000000+$tmp->{'ID_parts'}).qq|
									<br>
									</td>
							<td class="smalltext" $style valign="top">|.&load_db_names('sl_parts','ID_parts',$tmp->{'ID_parts'},'[Model]<br>[Name]').qq|</td>
							<td class="smalltext" $style valign="top">$tmp->{'Serial'}</td>
							<td class="smalltext" $style valign="top">|.$tracking2.qq|</td>							
							</tr>\n|;

						}
					}
				} else {
					my ($linkedit) = '';
					my ($chkship) = '';
					$tracking3 = '';
							
					if($col->{'ShpDate'} and $col->{'ShpDate'} ne "0000-00-00"){
						$tracking3 = &build_tracking_link($col->{'Tracking'},$col->{'ShpProvider'},$col->{'ShpDate'},$col->{'ID_products'});
						$tracking3 =~ s/More Info//;
						
						$linkedit = qq|onclick="chgShip('$col->{'Tracking'}','$col->{'ShpProvider'}','$col->{'ShpDate'}')" |;
					}
						
					$chk_id_products = $col->{'ID_orders_products'};
					$chkship = qq| <input type='checkbox' class='checkbox' name="chk_prod_$chk_id_products" value="$col->{'ID_orders_products'} $linkedit">|;
					$va{'searchresults'} .= "<tr bgcolor='$c[$d]' onmouseover='m_over(this)' onmouseout='m_out(this)' $linkedit>\n";
					$va{'searchresults'} .= " <td class='smalltext' valign='top'>";
         	### Products
         	$va{'searchresults'} .= qq|$chkship |;
        	$va{'searchresults'} .= &format_sltvid($col->{'ID_sku_products'});
					$va{'searchresults'} .= "</td>\n";		
					(!$col->{'SerialNumber'}) and ($col->{'SerialNumber'} = '---');
					($status,%tmp) = &load_product_info($col->{'ID_products'});
					$va{'searchresults'} .= "  <td class='smalltext' valign='top'>$tmp{'model'}<br>".substr($tmp{'name'},0,30)." </td>\n";
					$va{'searchresults'} .= "  <td class='smalltext' valign='top'> $col->{'SerialNumber'}</td>\n";
					
					$va{'searchresults'} .= "  <td class='smalltext' valign='top'>".$tracking3."</td>\n";					
					$va{'searchresults'} .= "</tr>\n";	
				}
			}
		$va{'productsoptionsform'}="[ip_products_options1]";
		}else{
			$va{'pageslist'} = 1;
			$va{'searchresults'} = qq|
				<tr>
					<td colspan='3' align="center">|.&trans_txt('search_nomatches').qq|</td>
				</tr>\n|;
		}
	}
	$in{'cmd_ajax'} = "enter_shipment";
	print "Content-type: text/html\n\n";
	print &build_page('products_options.html');
}
			

sub enter_shipment {
# --------------------------------------------------------

# Author: Jose Ramirez Garcia
# Created on: 08/15/2008
# Last Modified on: 
# Last Modified by: 
# Description : it show the items/parts to add shipment information
# Forms Involved: opr_orders_view
# Parameters : 
# Last Modified on: 09/15/08 17:09:17
# Last Modified by: MCC C. Gabriel Varela S: Se hace que tambi�n se pueda acceder desde cc-cservice
	
	
	if($in{'shpdate'} && $in{'tracking'} && $in{'shpprovider'} && $in{'shpinfo'}){
		my ($sth2) = &Do_SQL("SELECT sl_orders_products.*,sl_skus.* FROM sl_orders_products INNER JOIN sl_skus ON(sl_orders_products.ID_products=sl_skus.ID_sku_products) WHERE sl_orders_products.id_orders='$in{'id_orders'}' AND LEFT(sl_orders_products.ID_products,1)<>'6'");
		while ($col = $sth2->fetchrow_hashref){
			$id_orders_products = $col->{'ID_orders_products'};
			$set = $col->{'IsSet'};
			$sku = $col->{'ID_sku_products'};
			$posted = &posteddate_orders_products($id_orders_products);
			my $d = 1 - $d;
		  if ($set eq 'Y'){
				my ($sth3) = &Do_SQL("SELECT * FROM sl_skus_parts WHERE ID_sku_products='$sku';");
				while ($tmp = $sth3->fetchrow_hashref){
					$chk_id_parts = 400000000+$tmp->{'ID_parts'};
					if($in{'chk_part_'.$chk_id_parts} eq $id_orders_products){
						my ($sthp) = &Do_SQL("SELECT COUNT(*) FROM sl_orders_parts WHERE ID_orders_products='$id_orders_products' AND ID_parts='$tmp->{'ID_parts'}'");
						$exist_orders_parts = $sthp->fetchrow;
						if(!$exist_orders_parts){
							my ($sthc) = &Do_SQL("SELECT AVG(Cost) FROM sl_skus_cost WHERE ID_products = '$chk_id_parts'");
							$part_cost=$sthc->fetchrow;
							if(&Do_SQL("INSERT INTO sl_orders_parts SET ID_parts='$tmp->{'ID_parts'}',ID_orders_products='$id_orders_products',Quantity=1,Cost='$part_cost',ShpDate='".&filter_values($in{'shpdate'})."', Tracking='".&filter_values($in{'tracking'})."',ShpProvider='".&filter_values($in{'shpprovider'})."',PostedDate='$posted',Status='Shipped',Date=Curdate(),Time=NOW(),ID_admin_users='$usr{'id_admin_users'}'")){
								my ($sthl)=&Do_SQL("SELECT last_insert_id(ID_orders_parts)as last from sl_orders_parts order by last desc limit 1");
								$lastid=$sthl->fetchrow();
								&auth_logging('part_shipping_info_added',$lastid);
								$va{'message'} = &trans_txt('record_updated');
							}
						}else{
							if(&Do_SQL("UPDATE sl_orders_parts SET ShpDate='".&filter_values($in{'shpdate'})."', Tracking='".&filter_values($in{'tracking'})."', ShpProvider='".&filter_values($in{'shpprovider'})."' WHERE ID_parts='$tmp->{'ID_parts'}' AND ID_orders_products='$id_orders_products';")){
								&auth_logging('part_shipping_info_updated',$shp->{'ID_orders_parts'});
								$va{'message'} = &trans_txt('record_updated');
							}
						}
					}
				}
			} else {
				if($in{'chk_prod_'.$id_orders_products}){
					if(&Do_SQL("UPDATE sl_orders_products SET ShpDate='".&filter_values($in{'shpdate'})."', Tracking='".&filter_values($in{'tracking'})."', ShpProvider='".&filter_values($in{'shpprovider'})."' WHERE ID_orders_products='$id_orders_products';")){
						&auth_logging('product_shipping_info_updated',$id_orders_products);
						$va{'message'} = &trans_txt('record_updated');
					}
				}
			}
		}
	} else {
		if(!$in{'shpdate'}){
			$error{'shpdate'} = &trans_txt('required');
		}
		if(!$in{'tracking'}){
			$error{'tracking'} = &trans_txt('required');
		}
		if(!$in{'shpprovider'}){
			$error{'shpprovider'} = &trans_txt('required');
		}																				
	}
	#&enter_shipment_show();
	$id_orders=$in{'id_orders'};
	print "Content-type: text/html\n\n";
	print qq|<script type="text/javascript">
			parent.location.href = "$in{'path'}?cmd=opr_orders&view=$id_orders";
			</script>|;
}

sub posteddate_orders_products {
# --------------------------------------------------------

# Author: Jose Ramirez Garcia
# Created on: 08/18/2008
# Last Modified on: 
# Last Modified by: 
# Description : Search and set posteddate by orders_products
# Forms Involved: 
# Parameters : id_orders_products
# Last Modification by JRG : 03/13/2009 : Se agrega log
	
	my ($id_orders_products) = @_;
	my ($sthop) = &Do_SQL("SELECT * FROM sl_orders_products WHERE ID_orders_products=$id_orders_products");
	while ($col = $sthop->fetchrow_hashref){
		$orders_op = $col->{'ID_orders'};
		$posted_op = $col->{'PostedDate'};
		$date_op = $col->{'Date'};
	}
	if($posted_op eq "0000-00-00" || $posted_op eq "NULL" || !$posted_op){
		my ($sth1) = &Do_SQL("UPDATE sl_orders_parts SET PostedDate=Curdate() WHERE ID_orders_products=$id_orders_products AND (PostedDate IS NULL OR PostedDate='0000-00-00')");
		my ($sth3) = &Do_SQL("UPDATE sl_orders SET PostedDate=Curdate() WHERE ID_orders=$orders_op AND Date='$date_op' AND (PostedDate IS NULL OR PostedDate='0000-00-00')");
		my ($sth3) = &Do_SQL("UPDATE sl_orders_products SET PostedDate=Curdate() WHERE ID_orders=$orders_op AND Date='$date_op' AND (PostedDate IS NULL OR PostedDate='0000-00-00')");
		my ($sth4) = &Do_SQL("UPDATE sl_orders_payments SET PostedDate=Curdate() WHERE ID_orders=$orders_op AND Date='$date_op' AND (PostedDate IS NULL OR PostedDate='0000-00-00')");
		&auth_logging('orders_posteddate_updated',$orders_op);
		my ($sth5) = &Do_SQL("SELECT * FROM sl_orders_products WHERE ID_orders_products=$id_orders_products");
		while ($col = $sth5->fetchrow_hashref){
			$posted_op = $col->{'PostedDate'};
		}
	}
	return $posted_op;
}

sub adjust_price_show {
# --------------------------------------------------------

# Author: Jose Ramirez Garcia
# Created on: 08/19/2008
# Last Modified on: 
# Last Modified by: 
# Description : it show the items to add adjust price
# Forms Involved: opr_orders_view
# Parameters : 
	
	if($in{'id_orders'}){
		my ($sth0) = &Do_SQL("SELECT ID_orders_products,IsSet FROM sl_orders_products INNER JOIN sl_skus ON(sl_orders_products.ID_products=sl_skus.ID_sku_products) WHERE sl_orders_products.id_orders='$in{'id_orders'}'");
		while ($tmp0 = $sth0->fetchrow_hashref){
			if ($tmp0->{'IsSet'} eq 'Y'){
				&check_kit_shipped($tmp0->{'ID_orders_products'});	      	
      }
		}
		my (@c) = split(/,/,$cfg{'srcolors'});
		my ($sth1) = &Do_SQL("SELECT COUNT(*) FROM sl_orders_products WHERE ID_orders='$in{'id_orders'}' AND (ShpDate IS NULL OR ShpDate='0000-00-00')");
		$va{'matches'} = $sth1->fetchrow;
		if ($va{'matches'}>0){
			my ($sth2) = &Do_SQL("SELECT sl_orders_products.*,sl_skus.* FROM sl_orders_products INNER JOIN sl_skus ON(sl_orders_products.ID_products=sl_skus.ID_sku_products) WHERE sl_orders_products.id_orders='$in{'id_orders'}' AND (ShpDate IS NULL OR ShpDate='0000-00-00') ORDER BY ID_orders_products DESC");
			while ($col = $sth2->fetchrow_hashref){
				$d = 1 - $d;
				$sku_id_p=substr($col->{'ID_products'},3,6);
				$sku_id_e=$col->{'ID_products'};
				$sku_id_d=format_sltvid($col->{'ID_products'});				
			  if ($col->{'IsSet'} eq 'Y'){
	      	### SETS / Kits
					$va{'searchresults'} .= "<tr bgcolor='$c[$d]' onmouseover='m_over(this)' onmouseout='m_out(this)'>\n";
					$va{'searchresults'} .= " <td class='smalltext' valign='top'>";
	      	### Products
	      	$chk_id_products = $col->{'ID_orders_products'};
	      	$va{'searchresults'} .= qq|<input type='checkbox' class='checkbox' name="chk_prod_$chk_id_products" value='$chk_id_products'>|;
	      	$va{'searchresults'} .= &format_sltvid($col->{'ID_sku_products'});
					$va{'searchresults'} .= "</td>\n";		
					(!$col->{'SerialNumber'}) and ($col->{'SerialNumber'} = '---');
					($status,%tmp) = &load_product_info($col->{'ID_products'});
					$va{'searchresults'} .= "  <td class='smalltext' valign='top'>$tmp{'model'}<br>".substr($tmp{'name'},0,30)." </td>\n";
					$va{'searchresults'} .= "  <td class='smalltext' valign='top'> $col->{'SerialNumber'} </td>\n";
					$tracking1 = &build_tracking_link($col->{'Tracking'},$col->{'ShpProvider'},$col->{'ShpDate'},$col->{'ID_products'});
					$tracking1 =~ s/More Info//; 
					$va{'searchresults'} .= "  <td class='smalltext' valign='top'>".$tracking1."</td>\n";
					$va{'searchresults'} .= "</tr>\n";
					my ($sth3) = &Do_SQL("SELECT * FROM sl_skus_parts WHERE ID_sku_products='$col->{'ID_sku_products'}';");
					while ($tmp = $sth3->fetchrow_hashref){
						for my $i(1..$tmp->{'Qty'}){
							my ($sth3) = &Do_SQL("SELECT * FROM sl_orders_parts WHERE ID_orders_products='$col->{'ID_orders_products'}' AND ID_parts='$tmp->{'ID_parts'}' LIMIT 0,1;");
							my ($shp) = $sth3->fetchrow_hashref;
							if(!$shp->{'ShpDate'} || $shp->{'ShpDate'} eq "0000-00-00"){
								$chk_id_parts = 400000000+$tmp->{'ID_parts'};		
								(!$tmp->{'Serial'}) and ($tmp->{'Serial'} = '---');
								$tracking2 = &build_tracking_link($shp->{'Tracking'},$shp->{'ShpProvider'},$shp->{'ShpDate'},400000000+$tmp->{'ID_parts'});
								$tracking2 =~ s/More Info//;
								$va{'searchresults'} .= qq|<tr bgcolor='$c[$d]' onmouseover='m_over(this)' onmouseout='m_out(this)'>
								<td class='smalltext' $style valign='top' align='left' >
										&nbsp;
										<img src="/sitimages/tri.gif" border="0"> |.
										&format_sltvid(400000000+$tmp->{'ID_parts'}).qq|
										<br>
										</td>
								<td class="smalltext" $style valign="top">|.&load_db_names('sl_parts','ID_parts',$tmp->{'ID_parts'},'[Model]<br>[Name]').qq|</td>
								<td class="smalltext" $style valign="top">$tmp->{'Serial'}</td>
								<td class="smalltext" $style valign="top">|.$tracking2.qq|</td>							
								</tr>\n|;
							}
						}
					}
				} else {
					$chk_id_products = $col->{'ID_orders_products'};
					$va{'searchresults'} .= "<tr bgcolor='$c[$d]' onmouseover='m_over(this)' onmouseout='m_out(this)'>\n";
					$va{'searchresults'} .= " <td class='smalltext' valign='top'>";
         	### Products
         	$va{'searchresults'} .= qq|<input type='checkbox' class='checkbox' name="chk_prod_$chk_id_products" value='$chk_id_products'>|;
        	$va{'searchresults'} .= &format_sltvid($col->{'ID_sku_products'});
					$va{'searchresults'} .= "</td>\n";		
					(!$col->{'SerialNumber'}) and ($col->{'SerialNumber'} = '---');
					($status,%tmp) = &load_product_info($col->{'ID_products'});
					$va{'searchresults'} .= "  <td class='smalltext' valign='top'>$tmp{'model'}<br>".substr($tmp{'name'},0,30)." </td>\n";
					$va{'searchresults'} .= "  <td class='smalltext' valign='top'> $col->{'SerialNumber'}</td>\n";
					$tracking3 = &build_tracking_link($col->{'Tracking'},$col->{'ShpProvider'},$col->{'ShpDate'},$col->{'ID_products'});
					$tracking3 =~ s/More Info//;
					$va{'searchresults'} .= "  <td class='smalltext' valign='top'>".$tracking3."</td>\n";					
					$va{'searchresults'} .= "</tr>\n";	
				}
			}
		$va{'productsoptionsform'}="[ip_products_options2]";
		}else{
			$va{'pageslist'} = 1;
			$va{'searchresults'} = qq|
				<tr>
					<td colspan='3' align="center">|.&trans_txt('search_nomatches').qq|</td>
				</tr>\n|;
		}
	}
	$in{'cmd_ajax'} = "adjust_price";
	print "Content-type: text/html\n\n";
	print &build_page('products_options.html');
}


sub adjust_price {
# --------------------------------------------------------

# Author: Jose Ramirez Garcia
# Created on: 08/19/2008
# Last Modified on: 
# Last Modified by: 
# Description : it show the items/parts to add shipment information
# Forms Involved: opr_orders_view
# Parameters : 
# Last Modified on: 09/15/08 17:17:52
# Last Modified by: MCC C. Gabriel Varela S: Se corrige para que pueda ser llamada desde cc-cservice
# Last Modification by JRG : 03/13/2009 : Se corrige log

	if($in{'saleprice'} && $in{'priceupd'}){
		my ($sth2) = &Do_SQL("SELECT sl_orders_products.*,sl_skus.* FROM sl_orders_products INNER JOIN sl_skus ON(sl_orders_products.ID_products=sl_skus.ID_sku_products) WHERE sl_orders_products.id_orders='$in{'id_orders'}' AND (ShpDate IS NULL OR ShpDate='0000-00-00')");
		while ($col = $sth2->fetchrow_hashref){
			$id_orders_products = $col->{'ID_orders_products'};
			if($in{'chk_prod_'.$id_orders_products}){
				if(&Do_SQL("UPDATE sl_orders_products SET SalePrice='".&filter_values($in{'saleprice'})."' WHERE ID_orders_products='$id_orders_products';")){
					$old_sp = $col->{'SalePrice'};
					$new_sp = $in{'saleprice'};
					&auth_logging('orders_products_updated',$col->{'ID_orders'});
					$va{'message'} = &trans_txt('record_updated');
				}
			}
		}
	} else {
		if(!$in{'saleprice'}){
			$error{'saleprice'} = &trans_txt('required');
		}
	}
	#&adjust_price_show();
	$id_orders=$in{'id_orders'};
	print "Content-type: text/html\n\n";
	print qq|<script type="text/javascript">
			parent.location.href = "$in{'path'}?cmd=opr_orders&view=$id_orders";
			</script>|;
	
}

sub add_return_show {
# --------------------------------------------------------

# Author: Jose Ramirez Garcia
# Created on: 08/19/2008
# Last Modified on: 
# Last Modified by: 
# Description : it show the items to add return
# Forms Involved: opr_orders_view
# Parameters : 
	
	if($in{'id_orders'}){
		my ($sth0) = &Do_SQL("SELECT ID_orders_products,IsSet FROM sl_orders_products INNER JOIN sl_skus ON(sl_orders_products.ID_products=sl_skus.ID_sku_products) WHERE sl_orders_products.id_orders='$in{'id_orders'}'");
		while ($tmp0 = $sth0->fetchrow_hashref){
			if ($tmp0->{'IsSet'} eq 'Y'){
				&check_kit_shipped($tmp0->{'ID_orders_products'});	      	
      }
		}
		my (@c) = split(/,/,$cfg{'srcolors'});
		my ($sth1) = &Do_SQL("SELECT COUNT(*) FROM sl_orders_products WHERE ID_orders='$in{'id_orders'}' AND (ShpDate IS NOT NULL AND ShpDate<>'0000-00-00') AND LEFT(sl_orders_products.ID_products,1)<>'6'");
		$va{'matches'} = $sth1->fetchrow;
		if ($va{'matches'}>0){
			my ($sth2) = &Do_SQL("SELECT sl_orders_products.*,sl_skus.* FROM sl_orders_products INNER JOIN sl_skus ON(sl_orders_products.ID_products=sl_skus.ID_sku_products) WHERE sl_orders_products.id_orders='$in{'id_orders'}' AND (ShpDate IS NOT NULL OR ShpDate<>'0000-00-00') AND LEFT(sl_orders_products.ID_products,1)<>'6' ORDER BY ID_orders_products DESC");
			while ($col = $sth2->fetchrow_hashref){
				$d = 1 - $d;
				$sku_id_p=substr($col->{'ID_products'},3,6);
				$sku_id_e=$col->{'ID_products'};
				$sku_id_d=format_sltvid($col->{'ID_products'});				
			  if ($col->{'IsSet'} eq 'Y'){
	      	### SETS / Kits
					$va{'searchresults'} .= "<tr bgcolor='$c[$d]' onmouseover='m_over(this)' onmouseout='m_out(this)'>\n";
					$va{'searchresults'} .= " <td class='smalltext' valign='top'>";
	      	### Products
	      	$chk_id_products = $col->{'ID_orders_products'};
	      	$va{'searchresults'} .= qq|<input type='radio' class='checkbox' name="chk_prod" value='$chk_id_products'>|;
	      	$va{'searchresults'} .= &format_sltvid($col->{'ID_sku_products'});
					$va{'searchresults'} .= "</td>\n";		
					(!$col->{'SerialNumber'}) and ($col->{'SerialNumber'} = '---');
					($status,%tmp) = &load_product_info($col->{'ID_products'});
					$va{'searchresults'} .= "  <td class='smalltext' valign='top'>$tmp{'model'}<br>".substr($tmp{'name'},0,30)." </td>\n";
					$va{'searchresults'} .= "  <td class='smalltext' valign='top'> $col->{'SerialNumber'} </td>\n";
					$tracking1 = &build_tracking_link($col->{'Tracking'},$col->{'ShpProvider'},$col->{'ShpDate'},$col->{'ID_products'});
					$tracking1 =~ s/More Info//; 
					$va{'searchresults'} .= "  <td class='smalltext' valign='top'>".$tracking1."</td>\n";
					$va{'searchresults'} .= "</tr>\n";
					my ($sth3) = &Do_SQL("SELECT * FROM sl_skus_parts WHERE ID_sku_products='$col->{'ID_sku_products'}';");
					while ($tmp = $sth3->fetchrow_hashref){
						for my $i(1..$tmp->{'Qty'}){
							my ($sth3) = &Do_SQL("SELECT * FROM sl_orders_parts WHERE ID_orders_products='$col->{'ID_orders_products'}' AND ID_parts='$tmp->{'ID_parts'}' LIMIT 0,1;");
							my ($shp) = $sth3->fetchrow_hashref;
							if($shp->{'ShpDate'} && $shp->{'ShpDate'} ne "0000-00-00"){
								$chk_id_parts = 400000000+$tmp->{'ID_parts'};		
								(!$tmp->{'Serial'}) and ($tmp->{'Serial'} = '---');
								$tracking2 = &build_tracking_link($shp->{'Tracking'},$shp->{'ShpProvider'},$shp->{'ShpDate'},400000000+$tmp->{'ID_parts'});
								$tracking2 =~ s/More Info//;
								$va{'searchresults'} .= qq|<tr bgcolor='$c[$d]' onmouseover='m_over(this)' onmouseout='m_out(this)'>
								<td class='smalltext' $style valign='top' align='left' >
										&nbsp;
										<img src="/sitimages/tri.gif" border="0"> |.
										&format_sltvid(400000000+$tmp->{'ID_parts'}).qq|
										<br>
										</td>
								<td class="smalltext" $style valign="top">|.&load_db_names('sl_parts','ID_parts',$tmp->{'ID_parts'},'[Model]<br>[Name]').qq|</td>
								<td class="smalltext" $style valign="top">$tmp->{'Serial'}</td>
								<td class="smalltext" $style valign="top">|.$tracking2.qq|</td>							
								</tr>\n|;
							}
						}
					}
				} else {
					$chk_id_products = $col->{'ID_orders_products'};
					$va{'searchresults'} .= "<tr bgcolor='$c[$d]' onmouseover='m_over(this)' onmouseout='m_out(this)'>\n";
					$va{'searchresults'} .= " <td class='smalltext' valign='top'>";
         	### Products
         	$va{'searchresults'} .= qq|<input type='radio' class='checkbox' name="chk_prod" value='$chk_id_products'>|;
        	$va{'searchresults'} .= &format_sltvid($col->{'ID_sku_products'});
					$va{'searchresults'} .= "</td>\n";		
					(!$col->{'SerialNumber'}) and ($col->{'SerialNumber'} = '---');
					($status,%tmp) = &load_product_info($col->{'ID_products'});
					$va{'searchresults'} .= "  <td class='smalltext' valign='top'>$tmp{'model'}<br>".substr($tmp{'name'},0,30)." </td>\n";
					$va{'searchresults'} .= "  <td class='smalltext' valign='top'> $col->{'SerialNumber'}</td>\n";
					$tracking3 = &build_tracking_link($col->{'Tracking'},$col->{'ShpProvider'},$col->{'ShpDate'},$col->{'ID_products'});
					$tracking3 =~ s/More Info//;
					$va{'searchresults'} .= "  <td class='smalltext' valign='top'>".$tracking3."</td>\n";					
					$va{'searchresults'} .= "</tr>\n";	
				}
			}
		$va{'productsoptionsform'}="[ip_products_options3]";
		}else{
			$va{'pageslist'} = 1;
			$va{'searchresults'} = qq|
				<tr>
					<td colspan='3' align="center">|.&trans_txt('search_nomatches').qq|</td>
				</tr>\n|;
		}
	}
	$in{'cmd_ajax'} = "add_return";
	print "Content-type: text/html\n\n";
	print &build_page('products_options.html');
}

sub add_return {
# --------------------------------------------------------

# Author: Jose Ramirez Garcia
# Created on: 08/19/2008
# Last Modified on: 
# Last Modified by: 
# Description : it show the items/parts to add shipment information
# Forms Involved: opr_orders_view
# Parameters : 
# Last Modified on: 09/04/08 16:48:18
# Last Modified by: MCC C. Gabriel Varela S: Se agrega funci�n &calc_tax_disc_shp
# Last Modified on: 09/08/08 16:57:23
# Last Modified by: MCC C. Gabriel Varela S: 
# Last Modified on: 09/15/08 17:26:29
# Last Modified by: MCC C. Gabriel Varela S: Se hace que se pueda llamar desde cc-cservice
# Last Modification by JRG : 03/13/2009 : Se corrige log

	if($in{'posteddate'} && $in{'chk_prod'} && $in{'addreturn'}){
		my ($sth2) = &Do_SQL("SELECT sl_orders_products.*,sl_skus.* FROM sl_orders_products INNER JOIN sl_skus ON(sl_orders_products.ID_products=sl_skus.ID_sku_products) WHERE sl_orders_products.id_orders_products='$in{'chk_prod'}'");
		while ($col = $sth2->fetchrow_hashref){
			$id_orders_products = $col->{'ID_orders_products'};
			$id_products = &load_name('sl_skus','ID_products',$col->{'ID_products'},'ID_sku_products');
			if(&Do_SQL("INSERT INTO sl_orders_products SET ID_products='$id_products',ID_orders='$col->{'ID_orders'}',ID_packinglist='$col->{'ID_packinglist'}',Quantity='1',SalePrice='-$col->{'SalePrice'}',Shipping='$col->{'Shipping'}',Cost='$col->{'Cost'}',Tax='$col->{'Tax'}',Discount='$col->{'Discount'}',Status='Returned',PostedDate='$in{'posteddate'}',Date=Curdate(),Time=NOW(),ID_admin_users='$usr{'id_admin_users'}'")){
				my ($sthl)=&Do_SQL("SELECT last_insert_id(ID_orders_products)as last from sl_orders_products order by last desc limit 1");
				$lastid=$sthl->fetchrow();
				&calc_tax_disc_shp($lastid,1);
				&auth_logging('orders_products_added',$col->{'ID_orders'});
				$va{'message'} = &trans_txt('record_added');
			}
		}
	} else {
		if(!$in{'date'}){
			$error{'date'} = &trans_txt('required');
		}
	}
	#&add_return_show();
		$id_orders=$in{'id_orders'};
	print "Content-type: text/html\n\n";
	print qq|<script type="text/javascript">
			parent.location.href = "$in{'path'}?cmd=opr_orders&view=$id_orders";
			</script>|;
}

sub add_ip_show{
# --------------------------------------------------------
# Author: Jose Ramirez Garcia
# Created on: 08/25/2008
# Last Modified on: 
# Last Modified by: 
# Description : it show the items to add insurance payment
# Forms Involved: opr_orders_view
# Parameters : 
	
	if($in{'id_orders'}){
		my ($sth0) = &Do_SQL("SELECT ID_orders_products,IsSet FROM sl_orders_products INNER JOIN sl_skus ON(sl_orders_products.ID_products=sl_skus.ID_sku_products) WHERE sl_orders_products.id_orders='$in{'id_orders'}' AND sl_orders_products.Status <> 'Inactive'");
		while ($tmp0 = $sth0->fetchrow_hashref){
			if ($tmp0->{'IsSet'} eq 'Y'){
				&check_kit_shipped($tmp0->{'ID_orders_products'});	      	
      }
		}
		my (@c) = split(/,/,$cfg{'srcolors'});
		my ($sth1) = &Do_SQL("SELECT COUNT(*) FROM sl_orders_products WHERE ID_orders='$in{'id_orders'}' AND LEFT(sl_orders_products.ID_products,1)<>'6' AND sl_orders_products.Status <> 'Inactive'");
		$va{'matches'} = $sth1->fetchrow;
		if ($va{'matches'}>0){
			my ($sth2) = &Do_SQL("SELECT sl_orders_products.*,sl_skus.* FROM sl_orders_products INNER JOIN sl_skus ON(sl_orders_products.ID_products=sl_skus.ID_sku_products) WHERE sl_orders_products.id_orders='$in{'id_orders'}' AND LEFT(sl_orders_products.ID_products,1)<>'6' AND sl_orders_products.Status <> 'Inactive' ORDER BY ID_orders_products DESC");
			while ($col = $sth2->fetchrow_hashref){
				$d = 1 - $d;
				$sku_id_p=substr($col->{'ID_products'},3,6);
				$sku_id_e=$col->{'ID_products'};
				$sku_id_d=format_sltvid($col->{'ID_products'});				
			  if ($col->{'IsSet'} eq 'Y'){
	      	### SETS / Kits
					$va{'searchresults'} .= "<tr bgcolor='$c[$d]' onmouseover='m_over(this)' onmouseout='m_out(this)'>\n";
					$va{'searchresults'} .= " <td class='smalltext' valign='top'>";
	      	### Products
	      	$chk_id_products = $col->{'ID_orders_products'};
	      	$va{'searchresults'} .= qq|<input type='checkbox' class='checkbox' name="chk_prod_$chk_id_products" value='$chk_id_products'>|;
	      	$va{'searchresults'} .= &format_sltvid($col->{'ID_sku_products'});
					$va{'searchresults'} .= "</td>\n";		
					(!$col->{'SerialNumber'}) and ($col->{'SerialNumber'} = '---');
					($status,%tmp) = &load_product_info($col->{'ID_products'});
					$va{'searchresults'} .= "  <td class='smalltext' valign='top'>$tmp{'model'}<br>".substr($tmp{'name'},0,30)." </td>\n";
					$va{'searchresults'} .= "  <td class='smalltext' valign='top'> $col->{'SerialNumber'} </td>\n";
					$tracking1 = &build_tracking_link($col->{'Tracking'},$col->{'ShpProvider'},$col->{'ShpDate'},$col->{'ID_products'});
					$tracking1 =~ s/More Info//; 
					$va{'searchresults'} .= "  <td class='smalltext' valign='top'>".$tracking1."</td>\n";
					$va{'searchresults'} .= "</tr>\n";
					my ($sth3) = &Do_SQL("SELECT * FROM sl_skus_parts WHERE ID_sku_products='$col->{'ID_sku_products'}';");
					while ($tmp = $sth3->fetchrow_hashref){
						for my $i(1..$tmp->{'Qty'}){
							my ($sth3) = &Do_SQL("SELECT * FROM sl_orders_parts WHERE ID_orders_products='$col->{'ID_orders_products'}' AND ID_parts='$tmp->{'ID_parts'}' LIMIT 0,1;");
							my ($shp) = $sth3->fetchrow_hashref;
							if(!$shp->{'ShpDate'} || $shp->{'ShpDate'} eq "0000-00-00"){
								$chk_id_parts = 400000000+$tmp->{'ID_parts'};		
								(!$tmp->{'Serial'}) and ($tmp->{'Serial'} = '---');
								$tracking2 = &build_tracking_link($shp->{'Tracking'},$shp->{'ShpProvider'},$shp->{'ShpDate'},400000000+$tmp->{'ID_parts'});
								$tracking2 =~ s/More Info//;
								$va{'searchresults'} .= qq|<tr bgcolor='$c[$d]' onmouseover='m_over(this)' onmouseout='m_out(this)'>
								<td class='smalltext' $style valign='top' align='left' >
										&nbsp;
										<img src="/sitimages/tri.gif" border="0"> |.
										&format_sltvid(400000000+$tmp->{'ID_parts'}).qq|
										<br>
										</td>
								<td class="smalltext" $style valign="top">|.&load_db_names('sl_parts','ID_parts',$tmp->{'ID_parts'},'[Model]<br>[Name]').qq|</td>
								<td class="smalltext" $style valign="top">$tmp->{'Serial'}</td>
								<td class="smalltext" $style valign="top">|.$tracking2.qq|</td>							
								</tr>\n|;
							}
						}
					}
				} else {
					$chk_id_products = $col->{'ID_orders_products'};
					$va{'searchresults'} .= "<tr bgcolor='$c[$d]' onmouseover='m_over(this)' onmouseout='m_out(this)'>\n";
					$va{'searchresults'} .= " <td class='smalltext' valign='top'>";
         	### Products
         	$va{'searchresults'} .= qq|<input type='checkbox' class='checkbox' name="chk_prod_$chk_id_products" value='$chk_id_products'>|;
        	$va{'searchresults'} .= &format_sltvid($col->{'ID_sku_products'});
					$va{'searchresults'} .= "</td>\n";		
					(!$col->{'SerialNumber'}) and ($col->{'SerialNumber'} = '---');
					($status,%tmp) = &load_product_info($col->{'ID_products'});
					$va{'searchresults'} .= "  <td class='smalltext' valign='top'>$tmp{'model'}<br>".substr($tmp{'name'},0,30)." </td>\n";
					$va{'searchresults'} .= "  <td class='smalltext' valign='top'> $col->{'SerialNumber'}</td>\n";
					$tracking3 = &build_tracking_link($col->{'Tracking'},$col->{'ShpProvider'},$col->{'ShpDate'},$col->{'ID_products'});
					$tracking3 =~ s/More Info//;
					$va{'searchresults'} .= "  <td class='smalltext' valign='top'>".$tracking3."</td>\n";					
					$va{'searchresults'} .= "</tr>\n";	
				}
			}
		$va{'productsoptionsform'}="[ip_products_options4]";
		}else{
			$va{'pageslist'} = 1;
			$va{'searchresults'} = qq|
				<tr>
					<td colspan='3' align="center">|.&trans_txt('search_nomatches').qq|</td>
				</tr>\n|;
		}
	}
	$in{'cmd_ajax'} = "add_ip";
	print "Content-type: text/html\n\n";
	print &build_page('products_options.html');
}

sub add_ip {
# --------------------------------------------------------

# Author: Jose Ramirez Garcia
# Created on: 08/25/2008
# Last Modified on: 
# Last Modified by: 
# Description : it show the items to add insurance payment
# Forms Involved: opr_orders_view
# Parameters :

# Last Modified on: 10/06/08  15:56:10
# Last Modified by: Roberto Barcenas
# Last Modified Desc: Show only items <> 'Inactive'. Also the paymemt is created with Status= 'Claim' 
# Last Modification by JRG : 03/13/2009 : Se agrega log

	if($in{'pmtfield2'} && $in{'addip'}){
		my ($sth2) = &Do_SQL("SELECT sl_orders_products.*,sl_skus.* FROM sl_orders_products INNER JOIN sl_skus ON(sl_orders_products.ID_products=sl_skus.ID_sku_products) WHERE sl_orders_products.id_orders='$in{'id_orders'}' AND LEFT(sl_orders_products.ID_products,1)<>'6' ");
		while ($col = $sth2->fetchrow_hashref){
			$id_orders_products = $col->{'ID_orders_products'};
			if($in{'chk_prod_'.$id_orders_products}){
				my ($sth)= &Do_SQL("SELECT * FROM sl_orders_products WHERE ID_orders_products='$id_orders_products' AND LEFT(sl_orders_products.ID_products,1)<>'6'");
				$ordertax = &load_name('sl_orders','ID_orders',$in{'id_orders'},'OrderTax');
				while ($tmp = $sth->fetchrow_hashref){
					$subt = ($tmp->{'SalePrice'}*(1+$ordertax))+$tmp->{'Shipping'};
					$total += $subt;
					my ($sthad) = &Do_SQL("INSERT INTO sl_orders_products SET ID_orders='$tmp->{'ID_orders'}',ID_products='$tmp->{'ID_products'}',Quantity='$tmp->{'Quantity'}',SalePrice='$tmp->{'SalePrice'}',Shipping='$tmp->{'Shipping'}',Tax='$tmp->{'Tax'}',Discount='$tmp->{'Discount'}',FP='$tmp->{'FP'}',Date=Curdate(),Time=NOW(),ID_admin_users='$usr{'id_admin_users'}'");
					&auth_logging('orders_products_added',$tmp->{'ID_orders'});
				}
			}
		}
		if($total){
			if(&Do_SQL("INSERT INTO sl_orders_payments SET ID_orders='$in{'id_orders'}', Type='Credit-Card', PmtField2='$in{'pmtfield2'}',Amount='$total',Status='Claim',Date=Curdate(),Time=NOW(),ID_admin_users='$usr{'id_admin_users'}'")){
				my ($sthl)=&Do_SQL("SELECT last_insert_id(ID_orders_payments)as last from sl_orders_payments order by last desc limit 1");
				$lastid=$sthl->fetchrow();
				&auth_logging('orders_payments_added',$in{'id_orders'});
				$va{'message'} = &trans_txt('record_added');			
			}
		}
	} else {
		if(!$in{'pmtfield2'}){
			$error{'pmtfield2'} = &trans_txt('required');
		}
	}
	#&adjust_price_show();
	$id_orders=$in{'id_orders'};
	print "Content-type: text/html\n\n";
	print qq|<script type="text/javascript">
			parent.location.href = "/cgi-bin/mod/$usr{'application'}/dbman?cmd=opr_orders&view=$id_orders";
			</script>|;
	
}


sub services_related_products {
# --------------------------------------------------------
# Forms Involved: mer_services
# Created on: 10/10/2008
# Last Modified on: 
# Last Modified by: 
# Author: Jose Ramirez
# Description : iFrame to add related products
# Parameters : 

	my ($query);
	if ($in{'keyword'}){
		$query = "AND (Name LIKE '%$in{'keyword'}%' OR Model LIKE '%$in{'keyword'}%' OR ID_products LIKE '%$in{'keyword'}%') ";
	}
	
	my ($sth) = &Do_SQL("SELECT COUNT(*) FROM sl_products WHERE Status<>'Inactive' $query ");
	$va{'matches'} = $sth->fetchrow();
	my (@c) = split(/,/,$cfg{'srcolors'});
	if ($va{'matches'}>0){
		(!$in{'nh'}) and ($in{'nh'}=1);
		$first = ($in{'nh'} - 1) * $usr{'pref_maxh'};			
		($va{'pageslist'},$qs) = &pages_list($in{'nh'},"/cgi-bin/common/apps/schid",$va{'matches'},$usr{'pref_maxh'});
		
		my ($sth) = &Do_SQL("SELECT * FROM sl_products WHERE Status<>'Inactive' $query LIMIT $first,$usr{'pref_maxh'} ");
		while ($rec = $sth->fetchrow_hashref){
			$d = 1 - $d;
			$id_products = &load_name('sl_skus','ID_products',$rec->{'ID_products'},'ID_sku_products');
			$va{'searchresults'} .= qq|
			<tr bgcolor='$c[$d]' onmouseover='m_over(this)' onmouseout='m_out(this)' onclick="window.top.document.sitform.id_products_related.value='$id_products';window.top.document.getElementById('popup_product').style.visibility='hidden';window.top.document.getElementById('popup_product').style.display='none';">
				<td class="smalltext" valign="top">|.&format_sltvid($id_products).qq|</td>
				<td class="smalltext">$rec->{'Model'}<br>$rec->{'Name'}</td>
				<td class="smalltext" valign="top" align="right" nowrap>|.&format_price($rec->{'SPrice'}).qq|</td>
			</tr>\n|;
		}
	}else{
		$va{'pageslist'} = 1;
		$va{'searchresults'} = qq|
			<tr>
				<td colspan='5' align="center">  |.&trans_txt('search_nomatches').qq|</td>
			</tr>\n|;
	}
	
	$va{'header'} = qq|
		<tr>
		    <td class="menu_bar_title">ID</td>
		    <td class="menu_bar_title">Model/Name</td>
		    <td class="menu_bar_title">Price</td>
		 </tr>\n|;
	$in{'id_name'} = "id_products";
	$in{'id_value'} = $in{'id_products'};

	print "Content-type: text/html\n\n";
	print &build_page('products_exchange.html');
}

sub select_orders {
# --------------------------------------------------------

# Author: Jose Ramirez Garcia
# Created on: 12/12/2008
# Last Modified on: 
# Last Modified by: 
# Description : 
# Forms Involved: 
# Parameters : 
 
	my ($query);
	if ($in{'keyword'}){
		$query = "AND (ID_orders LIKE '%$in{'keyword'}%' OR FirstName LIKE '%$in{'keyword'}%' OR LastName1 LIKE '%$in{'keyword'}%' OR LastName2 LIKE '%$in{'keyword'}%') ";
	}
	
	my ($sth) = &Do_SQL("SELECT ID_orders FROM sl_orders,sl_customers WHERE sl_orders.ID_customers=sl_customers.ID_customers $query GROUP BY sl_orders.ID_orders");
	$va{'matches'} = $sth->rows();
	my (@c) = split(/,/,$cfg{'srcolors'});
	if ($va{'matches'}>0){
		(!$in{'nh'}) and ($in{'nh'}=1);
		$first = ($in{'nh'} - 1) * $usr{'pref_maxh'};			
		($va{'pageslist'},$qs) = &pages_list($in{'nh'},"/cgi-bin/common/apps/schid",$va{'matches'},$usr{'pref_maxh'});
		
		my ($sth) = &Do_SQL("SELECT ID_orders,sl_orders.Date as Date, FirstName, LastName1, LastName2, StatusPrd, StatusPay, sl_orders.Status as Status FROM sl_orders,sl_customers WHERE sl_orders.ID_customers=sl_customers.ID_customers $query GROUP BY sl_orders.ID_orders LIMIT $first,$usr{'pref_maxh'} ");
		while ($rec = $sth->fetchrow_hashref){
			$d = 1 - $d;
			$va{'searchresults'} .= qq|
			<tr bgcolor='$c[$d]' onmouseover='m_over(this)' onmouseout='m_out(this)' onclick="window.top.document.sitform.id_orders.value='$rec->{'ID_orders'}';window.top.document.getElementById('popup_ord').style.visibility='hidden';window.top.document.getElementById('popup_ord').style.display='none';">
				<td class="smalltext" valign="top">|.$rec->{'ID_orders'}.qq|</td>
				<td class="smalltext">$rec->{'Date'}</td>
				<td class="smalltext">$rec->{'FirstName'}</td>
				<td class="smalltext">$rec->{'LastName1'} $rec->{'LastName2'}</td>
				<td class="smalltext">$rec->{'StatusPay'}</td>
				<td class="smalltext">$rec->{'StatusPrd'}</td>
				<td class="smalltext">$rec->{'Status'}</td>
			</tr>\n|;
		}
	}else{
		$va{'pageslist'} = 1;
		$va{'searchresults'} = qq|
			<tr>
				<td colspan='5' align="center">  |.&trans_txt('search_nomatches').qq|</td>
			</tr>\n|;
	}
	
	$va{'header'} = qq|
		<tr>
		    <td class="menu_bar_title">Order ID</td>
		    <td class="menu_bar_title">Date</td>
		    <td class="menu_bar_title">First Name</td>
		    <td class="menu_bar_title">Last Name</td>
		    <td class="menu_bar_title">xPay</td>
		    <td class="menu_bar_title">xShip</td>
		    <td class="menu_bar_title">Status</td>
		 </tr>\n|;
	$in{'id_name'} = "id_products";
	$in{'id_value'} = $in{'id_products'};

	print "Content-type: text/html\n\n";
	print &build_page('select_orders.html');
}

sub select_products_in_orders {
# --------------------------------------------------------

# Author: Jose Ramirez Garcia
# Created on: 12/12/2008
# Last Modified on: 
# Last Modified by: 
# Description : 
# Forms Involved: 
# Parameters :
	if($in{'id_orders'}){
		my ($query);
		if ($in{'keyword'}){
			$query = "AND (ID_orders LIKE '%$in{'keyword'}%' OR FirstName LIKE '%$in{'keyword'}%' OR LastName1 LIKE '%$in{'keyword'}%' OR LastName2 LIKE '%$in{'keyword'}%') ";
		}
		
		my ($sth) = &Do_SQL("SELECT COUNT(*) 
			FROM sl_orders_products
			LEFT JOIN sl_products ON RIGHT(sl_orders_products.ID_products,6)=sl_products.ID_products 
			LEFT JOIN sl_skus ON sl_orders_products.ID_products=sl_skus.ID_sku_products
			LEFT JOIN sl_parts on RIGHT(sl_orders_products.Related_ID_products,4)=sl_parts.ID_parts
			WHERE ID_orders='$in{'id_orders'}'
			AND LEFT(sl_orders_products.ID_products,1) <> 6");
		$va{'matches'} = $sth->fetchrow();
		my (@c) = split(/,/,$cfg{'srcolors'});
		if ($va{'matches'}>0){
			(!$in{'nh'}) and ($in{'nh'}=1);
			$first = ($in{'nh'} - 1) * $usr{'pref_maxh'};			
			($va{'pageslist'},$qs) = &pages_list($in{'nh'},"/cgi-bin/common/apps/schid",$va{'matches'},$usr{'pref_maxh'});
			
			my ($sth) = &Do_SQL("SELECT ID_orders, IFNULL(sl_orders_products.Related_ID_products,sl_orders_products.ID_products) as ID_products, CASE WHEN sl_orders_products.Related_ID_products IS NULL THEN sl_products.Name ELSE sl_parts.Name END AS Name, ID_orders_products, choice1, choice2, choice3, choice4 
				FROM sl_orders_products
				LEFT JOIN sl_products ON RIGHT(sl_orders_products.ID_products,6)=sl_products.ID_products 
				LEFT JOIN sl_skus ON sl_orders_products.ID_products=sl_skus.ID_sku_products
				LEFT JOIN sl_parts on RIGHT(sl_orders_products.Related_ID_products,4)=sl_parts.ID_parts
				WHERE ID_orders='$in{'id_orders'}'
				AND LEFT(sl_orders_products.ID_products,1) <> 6
				LIMIT $first,$usr{'pref_maxh'} ");
			while ($rec = $sth->fetchrow_hashref){
				$d = 1 - $d;
				$va{'searchresults'} .= qq|
				<tr bgcolor='$c[$d]' onmouseover='m_over(this)' onmouseout='m_out(this)' onclick="window.top.document.sitform.id_products.value='$rec->{'ID_products'}';window.top.document.sitform.id_orders_products.value='$rec->{'ID_orders_products'}';window.top.document.getElementById('popup_ord').style.visibility='hidden';window.top.document.getElementById('popup_prod').style.display='none';">
					<td class="smalltext" valign="top">|.$rec->{'ID_products'}.qq|</td>
					<td class="smalltext">$rec->{'ID_orders_products'}</td>
					<td class="smalltext">$rec->{'Name'} $rec->{'choice1'} $rec->{'choice2'} $rec->{'choice3'} $rec->{'choice4'}</td>
				</tr>\n|;
			}
		}else{
			$va{'pageslist'} = 1;
			$va{'searchresults'} = qq|
				<tr>
					<td colspan='5' align="center">  |.&trans_txt('search_nomatches').qq|</td>
				</tr>\n|;
		}
		
		$va{'header'} = qq|
			<tr>
			    <td class="menu_bar_title">ID Products</td>
			    <td class="menu_bar_title">ID Orders Products</td>
			    <td class="menu_bar_title">Name</td>
			 </tr>\n|;
		$in{'id_name'} = "id_products";
		$in{'id_value'} = $in{'id_products'};
	} else {
		$va{'searchresults'} .= qq|<tr><td align='center'>|.&trans_txt("reqfields_short").qq|</td></tr>|;
	}
		print "Content-type: text/html\n\n";
		print &build_page('select_products_orders.html');

}

sub add_sample {
# --------------------------------------------------------

# Author: Jose Ramirez Garcia
# Created on: 12/17/2008
# Last Modified on: 
# Last Modified by: 
# Description : 
# Forms Involved: 
# Parameters : 

	my ($query);
	$query=" AND Status NOT IN ('Testing','Inactive')";
	if ($in{'keyword'}){
		$query = " AND (Name like '%$in{'keyword'}%' OR Model like '%$in{'keyword'}%' OR ID_samples like '%$in{'keyword'}%')";
	}
	
	my ($sth) = &Do_SQL("SELECT COUNT(*) FROM sl_samples WHERE Status<>'' $query;");
	$va{'matches'} = $sth->fetchrow();
	my (@c) = split(/,/,$cfg{'srcolors'});
	if ($va{'matches'}>0){
		(!$in{'nh'}) and ($in{'nh'}=1);
		$first = ($in{'nh'} - 1) * $usr{'pref_maxh'};			
		($va{'pageslist'},$qs) = &pages_list($in{'nh'},"/cgi-bin/common/apps/schid",$va{'matches'},$usr{'pref_maxh'});
		
		my ($sth) = &Do_SQL("SELECT * FROM sl_samples WHERE Status<>'' $query GROUP BY ID_samples LIMIT $first,$usr{'pref_maxh'};");
		while ($rec = $sth->fetchrow_hashref){
			$d = 1 - $d;
			$va{'searchresults'} .= qq|
			<tr bgcolor='$c[$d]' onmouseover='m_over(this)' onmouseout='m_out(this)' onclick="trjump('$in{'path'}?cmd=opr_orders&view=$in{'id_orders'}&addsample=$rec->{'ID_samples'}&qty=1&tab=1#tabs')">
				<td class="smalltext" valign="top">|.&format_sltvid(500000000+$rec->{'ID_samples'}).qq|</td>
				<td class="smalltext">$rec->{'Model'}<br>$rec->{'Name'}</td>
				<td class="smalltext" nowrap>$rec->{'Status'}</td>
			</tr>\n|;
		}
	}else{
		$va{'pageslist'} = 1;
		$va{'searchresults'} = qq|
			<tr>
				<td colspan='3' align="center">  |.&trans_txt('search_nomatches').qq|</td>
			</tr>\n|;
	}
	
	$va{'header'} = qq|
		<tr>
		    <td class="menu_bar_title">ID</td>
		    <td class="menu_bar_title">Model/Name</td>
		    <td class="menu_bar_title">Status</td>
		 </tr>\n|;
	$in{'id_name'} = "id_orders";
	$in{'id_value'} = $in{'id_orders'};

	print "Content-type: text/html\n\n";
	print &build_page('searchid:addid.html');
}

sub noninventory_addvendor {
# --------------------------------------------------------	
	my ($query);
	if ($in{'keyword'}){
		$query = "AND (CompanyName like '%$in{'keyword'}%' or ID_vendors like '%$in{'keyword'}%')";
	}
	my ($sth) = &Do_SQL("SELECT COUNT(*) FROM sl_vendors WHERE Status='Active' $query;");
	$va{'matches'} = $sth->fetchrow();
	my (@c) = split(/,/,$cfg{'srcolors'});
	if ($va{'matches'}>0){
		(!$in{'nh'}) and ($in{'nh'}=1);
		$first = ($in{'nh'} - 1) * $usr{'pref_maxh'};			
		($va{'pageslist'},$qs) = &pages_list($in{'nh'},"/cgi-bin/common/apps/schid",$va{'matches'},$usr{'pref_maxh'});
		
		my ($sth) = &Do_SQL("SELECT * FROM sl_vendors WHERE Status='Active' $query LIMIT $first,$usr{'pref_maxh'};");
		while ($rec = $sth->fetchrow_hashref){
			$d = 1 - $d;
			$va{'searchresults'} .= qq|
			<tr bgcolor='$c[$d]' onmouseover='m_over(this)' onmouseout='m_out(this)' onclick="trjump('/cgi-bin/mod/$usr{'application'}/dbman?cmd=mer_noninventory&view=$in{'id_noninventory'}&addvendor=$rec->{'ID_vendors'}&tab=2#tabs')">
				<td class="smalltext">$rec->{'ID_vendors'}</td>
				<td class="smalltext">$rec->{'CompanyName'}</td>
			</tr>\n|;
		}
	}else{
		$va{'pageslist'} = 1;
		$va{'searchresults'} = qq|
			<tr>
				<td colspan='5' align="center">|.&trans_txt('search_nomatches').qq|</td>
			</tr>\n|;
	}
	 $in{'id_name'} = "id_noninventory";
	 $in{'id_value'} = $in{'id_noninventory'};
	 $va{'header'} = qq|
		# <tr>
		    # <td class="menu_bar_title">ID</td>
		    # <td class="menu_bar_title">Name</td>
		 # </tr>\n|;

	 print "Content-type: text/html\n\n";
	 print &build_page('searchid:addid.html');

}


sub categories_addvendor {
# --------------------------------------------------------
	my ($query);
	if ($in{'keyword'}){
		$query = "AND (CompanyName like '%$in{'keyword'}%' or ID_vendors like '%$in{'keyword'}%')";
	}
	my ($sth) = &Do_SQL("SELECT COUNT(*) FROM sl_vendors WHERE Status='Active' $query;");
	$va{'matches'} = $sth->fetchrow();
	my (@c) = split(/,/,$cfg{'srcolors'});
	if ($va{'matches'}>0){
		(!$in{'nh'}) and ($in{'nh'}=1);
		$first = ($in{'nh'} - 1) * $usr{'pref_maxh'};			
		($va{'pageslist'},$qs) = &pages_list($in{'nh'},"/cgi-bin/common/apps/schid",$va{'matches'},$usr{'pref_maxh'});
		
		my ($sth) = &Do_SQL("SELECT * FROM sl_vendors WHERE Status='Active' $query LIMIT $first,$usr{'pref_maxh'};");
		while ($rec = $sth->fetchrow_hashref){
			$d = 1 - $d;
			$va{'searchresults'} .= qq|
			<tr bgcolor='$c[$d]' onmouseover='m_over(this)' onmouseout='m_out(this)' onclick="trjump('/cgi-bin/mod/$usr{'application'}/dbman?cmd=mer_categories&view=$in{'id_categories'}&addvendor=$rec->{'ID_vendors'}&tab=2#tabs')">
				<td class="smalltext">$rec->{'ID_vendors'}</td>
				<td class="smalltext">$rec->{'CompanyName'}</td>
			</tr>\n|;
		}
	}else{
		$va{'pageslist'} = 1;
		$va{'searchresults'} = qq|
			<tr>
				<td colspan='5' align="center">|.&trans_txt('search_nomatches').qq|</td>
			</tr>\n|;
	}
	$in{'id_name'} = "id_parts";
	$in{'id_value'} = $in{'id_parts'};
	$va{'header'} = qq|
		<tr>
		    <td class="menu_bar_title">ID</td>
		    <td class="menu_bar_title">Name</td>
		 </tr>\n|;

	print "Content-type: text/html\n\n";
	print &build_page('searchid:addid.html');

}

sub wreceipts_addpo {
# --------------------------------------------------------

	my ($query);
	if ($in{'id_vendors'}) {
		$query = " AND sl_purchaseorders.ID_vendors = '$in{'id_vendors'}'";
	}
	if ($in{'keyword'}){
		$query .= " AND (sl_purchaseorders.ID_purchaseorders = '".int($in{'keyword'})."' or sl_purchaseorders.POTerms like '%$in{'keyword'}%')";
	}

	my ($sth) = &Do_SQL("SELECT COUNT(*) FROM sl_purchaseorders WHERE sl_purchaseorders.Status NOT IN ('New','Received', 'Cancelled') $query;");
	$va{'matches'} = $sth->fetchrow();
	my (@c) = split(/,/,$cfg{'srcolors'});
	if ($va{'matches'}>0){
		(!$in{'nh'}) and ($in{'nh'} = 1);
		$first = ($in{'nh'} - 1) * $usr{'pref_maxh'};			
		($va{'pageslist'},$qs) = &pages_list($in{'nh'},"/cgi-bin/common/apps/schid",$va{'matches'}, $usr{'pref_maxh'});
		
		my ($sth) = &Do_SQL("SELECT sl_purchaseorders.*, sl_vendors.CompanyName FROM sl_purchaseorders INNER JOIN sl_vendors ON sl_vendors.ID_vendors=sl_purchaseorders.ID_vendors WHERE sl_purchaseorders.Status NOT IN ('New','Received', 'Cancelled') $query ORDER BY sl_purchaseorders.PODate desc LIMIT $first,$usr{'pref_maxh'};");
		while ($rec = $sth->fetchrow_hashref){
			$d = 1 - $d;
			$va{'searchresults'} .= qq|
			<tr bgcolor='$c[$d]' onmouseover='m_over(this)' onmouseout='m_out(this)'>
				<td align="center" valign='top' nowrap>
		       		<input type="button" name="sel__$rec->{'ID_purchaseorders'}" value="S" class="button" onclick="setid($rec->{'ID_purchaseorders'},$rec->{'ID_vendors'})">
		       	</td>
				<td class="smalltext">$rec->{'ID_purchaseorders'}</td>
				<td class="smalltext">$rec->{'CompanyName'} ($rec->{'ID_vendors'})</td>
				<td class="smalltext">$rec->{'PODate'}</td>
				<td class="smalltext">$rec->{'POTerms'}</td>
				<td class="smalltext">$rec->{'Status'}</td>
			</tr>\n|;
		}
	}else{
		$va{'pageslist'} = 1;
		$va{'searchresults'} = qq|
			<tr>
				<td colspan='5' align="center">|.&trans_txt('search_nomatches').qq|</td>
			</tr>\n|;
	}

	$in{'id_name'} = "id_parts";
	$in{'id_value'} = $in{'id_parts'};
	$va{'header'} = qq|
		<tr>
		    <td class="menu_bar_title">Sel/View</td>
		    <td class="menu_bar_title">PO #</td>
		    <td class="menu_bar_title">Vendor</td>
		    <td class="menu_bar_title">Date</td>
		    <td class="menu_bar_title">Terms</td>
		    <td class="menu_bar_title">Status</td>
		 </tr>\n|;

	print "Content-type: text/html\n\n";
	print &build_page('searchid:po_addid.html');

}

sub zones_addzipcode {
# --------------------------------------------------------

	my ($query);
	if ($in{'zipcode'}) {
		$query = " AND `ZipCode` = '$in{'zipcode'}'";
	}
	if ($in{'keyword'}){
		$query .= " AND (`ZipCode` = '" . $in{'keyword'}."' or StateFullName like '%$in{'keyword'}%' or City like '%$in{'keyword'}%' or CountyName like '%$in{'keyword'}%')";
	}

	my ($sth) = &Do_SQL("SELECT COUNT(*) FROM `sl_zipcodes` WHERE 1 $query;");
	$va{'matches'} = $sth->fetchrow();
	my (@c) = split(/,/,$cfg{'srcolors'});
	if ($va{'matches'}>0){
		(!$in{'nh'}) and ($in{'nh'} = 1);
		$first = ($in{'nh'} - 1) * $usr{'pref_maxh'};			
		($va{'pageslist'},$qs) = &pages_list($in{'nh'},"/cgi-bin/common/apps/schid",$va{'matches'}, $usr{'pref_maxh'});
		
		my ($sth) = &Do_SQL("SELECT * FROM `sl_zipcodes` WHERE 1 $query ORDER BY ZipCode ASC LIMIT $first,$usr{'pref_maxh'};");
		while ($rec = $sth->fetchrow_hashref){
			$d = 1 - $d;
			$va{'searchresults'} .= qq|
			<tr bgcolor='$c[$d]' onmouseover='m_over(this)' onmouseout='m_out(this)'>
				<td align="center" valign='top' nowrap>
		       		<input type="button" name="sel__$rec->{'ID_zipcodes'}" value="S" class="button" onclick="setid($rec->{'ID_zipcodes'},'$rec->{'ZipCode'}')">
		       		<input type="submit" name="view_$rec->{'ID_zipcodes'}" value="V" class="button">
		       	</td>
				<td class="smalltext">$rec->{'ZipCode'}</td>
				<td class="smalltext">$rec->{'StateFullName'}</td>
				<td class="smalltext">$rec->{'City'}</td>
				<td class="smalltext">$rec->{'CountyName'}</td>				
			</tr>\n|;
		}
	}else{
		$va{'pageslist'} = 1;
		$va{'searchresults'} = qq|
			<tr>
				<td colspan='5' align="center">|.&trans_txt('search_nomatches').qq|</td>
			</tr>\n|;
	}

	$in{'id_name'} = "id_parts";
	$in{'id_value'} = $in{'id_parts'};
	$va{'header'} = qq|
		<tr>
		    <td class="menu_bar_title">ZipCode</td>
		    <td class="menu_bar_title">State</td>
		    <td class="menu_bar_title">City</td>
		    <td class="menu_bar_title">County Name</td>		    
		    <td class="menu_bar_title"></td>		    
		 </tr>\n|;

	print "Content-type: text/html\n\n";
	print &build_page('searchid:zones_addzipcode.html');

}
#########################################################	
#	Function: 
#   	creditmemo_addorder
#
#	Created by:
#		CARLOS HAAS
#
#	Modified By:
#
#   	Parameters:
#
#   	Returns:
#			- list Vendors
#
#   	See Also:
#
sub creditmemo_addorder {
# --------------------------------------------------------
	my ($query,$click_url);
	$in{'id_customers'} = int($in{id_customers});
	$in{'id_name'} = 'id_customers';
	$in{'id_value'} = $in{'id_customers'};
	$in{'id_name2'} = 'id_creditmemos';
	$in{'id_value2'} = $in{'id_creditmemos'};
	if ($in{'keyword'}){
		$in{'keyword'} = &filter_values($in{'keyword'});
		$query	= "AND (sl_orders.ID_orders LIKE '%$in{'keyword'}%' OR sl_orders.Date LIKE '%$in{'keyword'}%' OR sl_orders.OrderNet LIKE '%$in{'keyword'}%')";
	}
	my($idcustomer);
	if($in{'id_customers'} eq 100000){$idcustomer='';}else{
		if($cfg{'use_rfc'}){
			my $ids = &Do_SQL(qq|SELECT 
				group_concat(c2.ID_customers) ids
			FROM sl_customers c1
			INNER JOIN sl_customers c2 on c2.RFC = c1.RFC
			WHERE 1
				AND c1.ID_customers = $in{'id_customers'}
			GROUP BY c2.RFC;|)->fetchrow();
			$idcustomer= ($ids) ? " AND sl_orders.ID_customers IN ($ids)" : " AND sl_orders.ID_customers='$in{id_customers}'";
		}else{
			$idcustomer="AND sl_orders.ID_customers='$in{id_customers}'";
		}
	}

	my $base_query = " TotalProducts	  
					 	, SUM(Amount)AS TotalPayments
						, SUM(IF(Captured='Yes' and Reason='Sale', ABS(Amount),0)) AS Paid,
						/*SUM(IF(Captured='Yes' or Amount < 0, ABS(Amount),0)) AS Paid,*/ 
					 	IF(
					 		(SELECT 
					 			SUM(sl_creditmemos_payments.Amount)
					 		FROM sl_creditmemos
					 		INNER JOIN sl_creditmemos_payments using (ID_creditmemos)
					 		WHERE 
					 			sl_creditmemos.Status = 'Approved' 
					 			AND sl_creditmemos_payments.ID_orders=sl_orders.ID_orders
					 			GROUP BY sl_creditmemos_payments.ID_orders
					 		) >= 0 ,
						(SELECT 
							SUM(sl_creditmemos_payments.Amount) 
					 	FROM sl_creditmemos
					 	INNER JOIN sl_creditmemos_payments using (ID_creditmemos)
						WHERE 
					 		sl_creditmemos.Status = 'Approved' 
					 		AND sl_creditmemos_payments.ID_orders=sl_orders.ID_orders
					 	GROUP BY sl_creditmemos_payments.ID_orders
					 	)
						,0) memos_total_amount
					  FROM sl_orders
					  INNER JOIN 
					  (
					  		SELECT
							 	sl_orders_products.ID_orders
							 	, SUM(sl_orders_products.SalePrice + sl_orders_products.Shipping + sl_orders_products.Tax + sl_orders_products.ShpTax - sl_orders_products.Discount) AS TotalProducts
							FROM sl_orders_products INNER JOIN sl_orders
							ON sl_orders_products.ID_orders = sl_orders.ID_orders
							WHERE 
							  	1 
								". $idcustomer ."
								AND sl_orders_products.Status= 'Active'
							GROUP BY
								sl_orders_products.ID_orders	
					  )tmp
					  ON sl_orders.ID_orders = tmp.ID_orders 
					  INNER JOIN sl_orders_payments
					  ON sl_orders.ID_orders = sl_orders_payments.ID_orders 
					  AND sl_orders_payments.Status NOT IN('Void','Order Cancelled','Cancelled')
					  WHERE 
					  	1 ". $idcustomer ." 
					  	AND sl_orders.Status NOT IN ('Cancelled','Void','System Error','Processed')
						". $query ."
					  GROUP BY  sl_orders.ID_orders
					  HAVING (ROUND(TotalPayments,2) <= ROUND(TotalProducts,2) AND (TotalPayments - memos_total_amount) > Paid)";


	my ($sth) = &Do_SQL("SELECT 
							sl_orders.ID_orders,
								". $base_query ."
						  ;");
	$va{'matches'} = $sth->rows();
	my (@c) = split(/,/,$cfg{'srcolors'});
	if ($va{'matches'} > 0){

		(!$in{'nh'}) and ($in{'nh'}=1);
		$first = ($in{'nh'} - 1) * $usr{'pref_maxh'};			
		($va{'pageslist'},$qs) = &pages_list($in{'nh'},"/cgi-bin/common/apps/schid",$va{'matches'},$usr{'pref_maxh'});
		
		
		my ($sth) = &Do_SQL("SELECT 
								 sl_orders.ID_orders, 
								 sl_orders.OrderNet,
								 sl_orders.Date,
								 sl_orders.Status,
								 	". $base_query ."
							  ORDER BY FIELD(sl_orders.Status, 'Shipped','Processed','New','Pending'), Date LIMIT $first,$usr{'pref_maxh'};");
		
		while ($rec = $sth->fetchrow_hashref){
			my ($sth5) = &Do_SQL("SELECT SUM(Amount) FROM sl_orders_payments WHERE ID_orders = '$rec->{'ID_orders'}' AND Reason='Sale' AND (Captured='No' OR Captured IS NULL OR Captured = '' OR CapDate IS NULL OR CapDate = '0000-00-00');");			
			my ($unpaid) = $sth5->fetchrow();

			$d = 1 - $d;
			$click_url = "trjump('/cgi-bin/mod/$usr{'application'}/dbman?cmd=opr_creditmemos&view=$in{'id_creditmemos'}&tab=2&addorder=$rec->{'ID_orders'}')";
			$va{'searchresults'} .= qq|
			<tr bgcolor='$c[$d]' onmouseover='m_over(this)' onmouseout='m_out(this)' onClick="$click_url">
				<td class="smalltext" valign="top">$rec->{'ID_orders'}</td>
				<td class="smalltext" align='right'>|. &format_price($rec->{'OrderNet'}) . qq|</td>
				<td class="smalltext" align='right' style='color:blue;''>|. &format_price($unpaid) . qq|</td>
				<td class="smalltext">$rec->{'Date'}</td>
				<td class="smalltext">|. &invoices_list($rec->{'ID_orders'}) .qq|</td>
				<td class="smalltext">$rec->{'Status'}</td>
			</tr>\n|;

		}
	}else{
		$va{'pageslist'} = 1;
		$va{'searchresults'} = qq|
			<tr>
				<td colspan='5' align="center">  |.&trans_txt('search_nomatches').qq|</td>
			</tr>\n|;
	}
	
	$va{'header'} = qq|
		<tr>
		    <td class="menu_bar_title">ID</td>
		    <td class="menu_bar_title">Order Net</td>
		    <td class="menu_bar_title">Unpaid</td>
		    <td class="menu_bar_title">Date</td>
		    <td class="menu_bar_title">Invoices</td>
		    <td class="menu_bar_title">Status</td>
		 </tr>\n|; 
	print "Content-type: text/html\n\n";
	print &build_page('searchid:addid.html');
}


#########################################################	
#	Function: 
#   	vendors
#
#	Created by:
#		Alejandro Diaz_
#
#	Modified By:
#
#   	Parameters:
#
#   	Returns:
#			- list Vendors
#
#   	See Also:
#
sub vendors_submit {
# --------------------------------------------------------

	my ($script_path,$subfijo,$urltojump);
	$script_path="/cgi-bin/mod/".$usr{'application'}."/dbman";
	$subfijo="fin_banks_movements";
	
	$urltojump = qq| onclick="trjump('$script_path?cmd=$subfijo&view=$in{'view'} |;  #"
	if($in{'urlpathy'}ne"")	{
		$script_path=$in{'urlpathy'};
		$in{'urlpathy'}=~/cgi-bin\/(.*)\//;
		if($1 ne "administration")
		{
			$subfijo="mer_vendors";
			$in{'id_name'} = "id_purchaseorders";
			$in{'id_value'} = $in{'id_purchaseorders'};
		}
	}elsif($in{'pathurlmov'}){
		$script_path = $in{'pathurlmov'};
		$subfijo     = $in{'cmdrecieve'};
		$urltojump = qq| onclick="trjump('$script_path?cmd=$subfijo&view=$in{'view'}&tab=$in{'in_tab'} |;  #"
		
		$in{'id_name2'}  = "pathurlmov";
		$in{'id_value2'} = $script_path;
		
		$in{'id_name3'}  = "tab";
		$in{'id_value3'} = $in{'tab'};	

		$in{'id_name4'}  = "view";
		$in{'id_value4'} = $in{'view'};	
		
		$in{'id_name'}  = "cmdrecieve";
		$in{'id_value'} = $in{'cmdrecieve'};
	}
	
	my ($query);
	if ($in{'keyword'}){
		$query = "AND (CompanyName like '%$in{'keyword'}%' OR ID_vendors=".int($in{'keyword'})." OR RFC like '%$in{'keyword'}%' OR State like '%$in{'keyword'}%' )";
	}

	my ($sth) = &Do_SQL("SELECT COUNT(*) FROM sl_vendors WHERE Status<>'Inactive' $query;");
	$va{'matches'} = $sth->fetchrow();
	my (@c) = split(/,/,$cfg{'srcolors'});
	if ($va{'matches'}>0){
		(!$in{'nh'}) and ($in{'nh'}=1);
		$first = ($in{'nh'} - 1) * $usr{'pref_maxh'};			
		($va{'pageslist'},$qs) = &pages_list($in{'nh'},"/cgi-bin/common/apps/schid",$va{'matches'},$usr{'pref_maxh'});
		
		my ($sth) = &Do_SQL("SELECT * FROM sl_vendors WHERE Status<>'Inactive' $query LIMIT $first,$usr{'pref_maxh'};");
		while ($rec = $sth->fetchrow_hashref){
			$d = 1 - $d;
			$va{'searchresults'} .= qq|
			<tr bgcolor='$c[$d]' onmouseover='m_over(this)' onmouseout='m_out(this)' $urltojump&id_vendors=$rec->{'ID_vendors'}')" >
				<td class="smalltext" valign="top">$rec->{'ID_vendors'}</td>
				<td class="smalltext">$rec->{'CompanyName'}</td>
				<td class="smalltext">$rec->{'Category'}</td>
				<td class="smalltext">$rec->{'City'}</td>
				<td class="smalltext">$rec->{'State'}</td>
				<td class="smalltext">$rec->{'Zip'}</td>
			</tr>\n|;  #'
		}
	}else{
		$va{'pageslist'} = 1;
		$va{'searchresults'} = qq|
			<tr>
				<td colspan='5' align="center">  |.&trans_txt('search_nomatches').qq|</td>
			</tr>\n|;
	}
	
	$va{'header'} = qq|
		<tr>
		    <td class="menu_bar_title">ID</td>
		    <td class="menu_bar_title">Company Name</td>
		    <td class="menu_bar_title">Category</td>
		    <td class="menu_bar_title">City</td>
		    <td class="menu_bar_title">State</td>
		    <td class="menu_bar_title">Zip</td>
		 </tr>\n|; 
	print "Content-type: text/html\n\n";
	print &build_page('searchid:addid.html');
}
sub advorders {
# --------------------------------------------------------
	print "Content-type: text/html\n\n";
	print &build_page('searchid:advorders.html');
}

sub orders {
# --------------------------------------------------------
	$in{'db'} = 'orders';
	my ($query);
	if ($in{'search'} or $in{'listall'}){
		@db_cols = split(/,/, $sys{'db_orders_list'});
		#&cgierr("$numhits --  $sys{'db_orders_list'} -- ".$#db_cols);
		#&load_cfg('sl_orders');
		@headerfields = split(/,/,$sys{'db_orders_list'});
		@titlefields = split(/,/,$sys{"db_orders_headers"});
		$db_max_hits   = 20;
		if ($in{'listall'}){
			$query = '';
		}else{
			$in{'id_orders'} = int($in{'id_orders'});
			if ($in{'id_orders'}){
				$query .= "AND ID_orders='$in{'id_orders'}'";
			}
			if ($in{'id_customers'}){
				$query .= "AND sl_orders.ID_customers='$in{'id_customers'}'";
			}
			if ($in{'firstname'}){
				$query .= "AND FirstName='$in{'firstname'}'";
			}
			if ($in{'lastname'}){
				$query .= "AND FirstName='$in{'lastname'}'";
			}
			if ($in{'company_name'}){
				$query .= "AND company_name='$in{'company_name'}'";
			}
			if ($in{'status'}){
				$query .= "AND sl_orders.status='$in{'status'}'";
			}
		}
		my ($numhits, @hits) = &query_sql("ID_orders,sl_customers.ID_customers,FirstName,LastName1,company_name,sl_orders.Status","sl_orders LEFT JOIN sl_customers ON sl_orders.ID_customers=sl_customers.ID_customers WHERE 1 $query",'ID_orders',('ID_orders','ID_customers','FirstName','LastName1','company_name','Status'));
		if ($numhits >0) {
			#&cgierr("$numhits --  $sys{'db_orders_list'} -- ".$#db_cols);
			&html_search_result($numhits,@hits);
		}else{
			$va{'message'} = &trans_txt('search_nomatches');
			&advorders;
			#&html_search_form(&trans_txt('search_nomatches'));
		}
	}else{
		$va{'message'} = &trans_txt('search_nomatches');
		&advorders;
		#$va{'message'} = @_[0];
		#$va{'searchform'} = &html_record_form (%rec);
		#print "Content-type: text/html\n\n";
		#print &build_page('searchid:form.html');
	}
}

#########################################################	
#	Function: 
#   	debitmemo_addorder
#
#	Created by:
#		Oscar Maldonado
#
#	Modified By:
#
#   	Parameters:
#
#   	Returns:
#			- list Vendors
#
#   	See Also:
#
sub debitmemo_addorder {
# --------------------------------------------------------
	my ($query,$click_url);
	$in{'id_customers'} = int($in{id_customers});
	$in{'id_name'} = 'id_customers';
	$in{'id_value'} = $in{'id_customers'};
	$in{'id_name2'} = 'id_debitmemos';
	$in{'id_value2'} = $in{'id_debitmemos'};
	if ($in{'keyword'}){
		$in{'keyword'} = &filter_values($in{'keyword'});
		$query	= "AND (sl_orders.ID_orders LIKE '%$in{'keyword'}%' OR sl_orders.Date LIKE '%$in{'keyword'}%' OR sl_orders.OrderNet LIKE '%$in{'keyword'}%')";
	}
	my($idcustomer);
	if($in{id_customers} eq 100000){$idcustomer='';}else{$idcustomer="AND sl_orders.ID_customers='$in{id_customers}'";}
	my ($sth) = &Do_SQL("SELECT SUM(Amount) AS Total,
								 SUM(IF(Captured='Yes',Amount,0)) AS Paid,
								 IF((select sum(sl_debitmemos_payments.Amount)
								 FROM sl_debitmemos
								 INNER JOIN sl_debitmemos_payments using (ID_debitmemos)
								 WHERE sl_debitmemos.Status = 'Approved' AND sl_debitmemos_payments.ID_orders=sl_orders.ID_orders
								 GROUP BY sl_debitmemos_payments.ID_orders
								 ) >=0 ,(select sum(sl_debitmemos_payments.Amount) 
								 FROM sl_debitmemos
								 INNER JOIN sl_debitmemos_payments USING (ID_debitmemos)
								 WHERE sl_debitmemos.Status = 'Approved' AND sl_debitmemos_payments.ID_orders=sl_orders.ID_orders
								 GROUP BY sl_debitmemos_payments.ID_orders
								 ),0) memos_total_amount
							  FROM sl_orders 
							  LEFT JOIN sl_orders_payments ON sl_orders.ID_orders=sl_orders_payments.ID_orders
							  WHERE 1 $idcustomer AND sl_orders.Status<>'System Error' AND Captured='Yes' $query
							  GROUP BY  sl_orders.ID_orders
							  HAVING ((Total - memos_total_amount)>=Paid);");
	$va{'matches'} = $sth->rows();
	my (@c) = split(/,/,$cfg{'srcolors'});
	if ($va{'matches'}>0){
		(!$in{'nh'}) and ($in{'nh'}=1);
		$first = ($in{'nh'} - 1) * $usr{'pref_maxh'};			
		($va{'pageslist'},$qs) = &pages_list($in{'nh'},"/cgi-bin/common/apps/schid",$va{'matches'},$usr{'pref_maxh'});
		
		
		my ($sth) = &Do_SQL("SELECT 
								 sl_orders.ID_orders, 
								 sl_orders.OrderNet,
								 sl_orders.Date,
								 sl_orders.Status,
								
								 SUM(Amount) AS Total,
								 SUM(IF(Captured='Yes',Amount,0)) AS Paid,
								 IF((select sum(sl_debitmemos_payments.Amount)
								 from sl_debitmemos
								 inner join sl_debitmemos_payments using (ID_debitmemos)
								 where sl_debitmemos.Status = 'Approved' and sl_debitmemos_payments.ID_orders=sl_orders.ID_orders
								 group by sl_debitmemos_payments.ID_orders
								 ) >=0 ,(select sum(sl_debitmemos_payments.Amount) 
								 from sl_debitmemos
								 inner join sl_debitmemos_payments using (ID_debitmemos)
								 where sl_debitmemos.Status = 'Approved' and sl_debitmemos_payments.ID_orders=sl_orders.ID_orders
								 group by sl_debitmemos_payments.ID_orders
								 ),0) memos_total_amount
							  FROM sl_orders 
							  LEFT JOIN sl_orders_payments ON sl_orders.ID_orders=sl_orders_payments.ID_orders
							  WHERE 1 $idcustomer AND sl_orders.Status<>'System Error' AND Captured='Yes' $query
							  GROUP BY  sl_orders.ID_orders
							  HAVING ((Total - memos_total_amount)>=Paid)
							  ORDER BY Date DESC LIMIT $first,$usr{'pref_maxh'};");
		while ($rec = $sth->fetchrow_hashref){
			$d = 1 - $d;
			$click_url = "trjump('/cgi-bin/mod/$usr{'application'}/dbman?cmd=opr_debitmemos&view=$in{'id_debitmemos'}&tab=2&addorder=$rec->{'ID_orders'}')";
			$va{'searchresults'} .= qq|
			<tr bgcolor='$c[$d]' onmouseover='m_over(this)' onmouseout='m_out(this)' onClick="$click_url">
				<td class="smalltext" valign="top">$rec->{'ID_orders'}</td>
				<td class="smalltext" align='right'>|. &format_price($rec->{'OrderNet'}) . qq|</td>
				<td class="smalltext">$rec->{'Date'}</td>
				<td class="smalltext">|. &invoices_list($rec->{'ID_orders'}) .qq|</td>
				<td class="smalltext">$rec->{'Status'}</td>
			</tr>\n|; 
		}
	}else{
		$va{'pageslist'} = 1;
		$va{'searchresults'} = qq|
			<tr>
				<td colspan='5' align="center">  |.&trans_txt('search_nomatches').qq|</td>
			</tr>\n|;
	}
	
	$va{'header'} = qq|
		<tr>
		    <td class="menu_bar_title">ID</td>
		    <td class="menu_bar_title">Order Net</td>
		    <td class="menu_bar_title">Date</td>
		    <td class="menu_bar_title">Invoices</td>
		    <td class="menu_bar_title">Status</td>
		 </tr>\n|; 
	print "Content-type: text/html\n\n";
	print &build_page('searchid:addid.html');
}

sub add_notes_attached{

	$tbl_notes = ( !$in{'tbl'} ) ? 'sl_creditmemos' : $in{'tbl'};
	$tbl_notes .= '_notes';

	my $html = '';
	if( $in{'rslt'} and $in{'rslt'} == 1 ){

		$html = '<table width="80%" border="0" cellspacing="0" cellpadding="0" align="center">
					<tr>
						<td class="stdtxterr" colspan="3" style="text-align: center;">
							The note added successfully. Please close this window
							<br /><br />
						</td>
					</tr>
					<tr>
						<td align="center" colspan="3">
							<input type="button" value="Close" class="button" onclick="window.parent.location.href = \'/cgi-bin/mod/[ur_application]/dbman?cmd='.$in{'cmdmain'}.'&view='.$in{'view'}.'&tab='.$in{'tab'}.'&tabs=1\';parent.$.fancybox.close();">
						</td>
					</tr>
				</table>';

	}else{

		if( &check_permissions('add_notes_attached','','') ){

			my (@ary) = &load_enum_toarray($tbl_notes,'Type');
			for my $i(0..$#ary){
				$va{'notetypes'}    .= qq|<input type="radio" name="notestype" class="radio" value="$ary[$i]">$ary[$i] &nbsp;\n|;
			}

			my $html_error = '';
			if( $in{'error'} == 1 ){
				$html_error = '</tr>
			    				<td class="stdtxterr" colspan="3">
			    					'.&trans_txt('reqfields_short').'
			    				</td>
			 				</tr>';
			 	$error{'notestype'} = &trans_txt('required') if( $in{'notestype'} );
			 	$error{'notestxt'} = &trans_txt('required') if( $in{'notestxt'} );
			 	if( $in{'file_attached'} ){
			 		$error{'file_attached'} = &trans_txt($in{'file_attached'});
			 	}
			}

			$html = '<form method="post" id="frm_notes" action="/apps/upload_file.php" enctype="multipart/form-data">
						<input type="hidden" name="tab" value="'.$in{'tab'}.'">
						<input type="hidden" name="cmd" value="'.$in{'cmd'}.'">
						<input type="hidden" name="cmdmain" value="'.$in{'cmdmain'}.'">
						<input type="hidden" name="tbl" value="'.$in{'tbl'}.'">
						<input type="hidden" name="view" value="'.$in{'view'}.'">
						<input type="hidden" name="e" value="'.$in{'e'}.'">
						<input type="hidden" name="id_admin_users" value="'.$usr{'id_admin_users'}.'">

						<table width="80%" border="0" cellspacing="0" cellpadding="0" class="gborder" align="center">						
							<tr colspan="3"><td>&nbsp;</td></tr>
							'.$html_error.'
							<tr>
								<td>
									Type: <span class="smallfieldterr">'.$error{'notestype'}.'</span>
								</td>
								<td class="smalltext" colspan="2">
									'.$va{'notetypes'}.' 
								</td>
							</tr>
							<tr>
								<td>
									Description: <span class="smallfieldterr">'.$error{'notestxt'}.'</span>
								</td>
								<td class="smalltext" colspan="2">
									<textarea name="notestxt" id="notestxt" style="width: 95%; font-size: 11pt;" cols="50" rows="4" onFocus="focusOn( this )" onBlur="focusOff( this )""></textarea>
								</td>
							</tr>
							<tr>
								<td>
									File attached: 
								</td>
								<td class="smalltext" colspan="2">
									<input type="file" name="file_attached" id="file_attached" size="40">
									<span class="smallfieldterr">'.$error{'file_attached'}.'</span>
								</td>
							</tr>
							<tr colspan="3"><td>&nbsp;</td></tr>
							<tr>
								<td align="center" colspan="2">
									<input type="submit" value="Save" class="button">
								</td>
							</tr>
						</table>
					</form>';
		}else{
			$html = '<table width="80%" border="0" cellspacing="0" cellpadding="0" align="center">
						<tr>
							<td class="stdtxterr" colspan="3" style="text-align: center;">
								'.&trans_txt('perms_insufficient_perms').'
								<br /><br />
							</td>
						</tr>
						<tr>
							<td align="center" colspan="3">
								<input type="button" value="Close" class="button" onclick="parent.$.fancybox.close();">
							</td>
						</tr>
					</table>';
		}
	}
	$va{'html'} = $html;

	print "Content-type: text/html\n\n";
	print &build_page('upfile:notes_attached.html');
}

sub view_notes_attached{


	my $html = '';
	if( $in{'id'} ){
		my $sth = &Do_SQL("SELECT extension FROM sl_notes_attached WHERE ID_notes_attached=".$in{'id'}.";");
		my $file_ext = $sth->fetchrow();

		$cfg{'file_extensions_images'} =~ s/\,/\|/g;
		if( $file_ext =~ /$cfg{'file_extensions_images'}/ ){
			$html = '<div style="min-width: 400px; min-height: 200px; border: 1px solid gray; display: block; margin: auto auto;">
						<img src="/apps/get_file.php?e='.$in{'e'}.'&id='.$in{'id'}.'" alt="image" title="" style="" />
					</div>';
		}elsif( $file_ext eq 'pdf' ){
			$html = '<object data="/apps/get_file.php?e='.$in{'e'}.'&id='.$in{'id'}.'" type="application/pdf" width="100%" height="98%">
						alt : <a href="/apps/get_file.php?e='.$in{'e'}.'&id='.$in{'id'}.'">file.pdf</a>
					</object>';
		}else{
			$html = '<div style="min-width: 400px; min-height: 100px; display: block; margin: auto auto;">
						<span style="font-size: 12pt;">
							Archivo disponible solo para <a href="/apps/get_file.php?e='.$in{'e'}.'&id='.$in{'id'}.'" title="Click para descargar" style="color: #08088a; font-size: 10pt; font-weight: bold;">Descargar</a>.
						</span>
					</div>';
		}
	}

	$va{'html'} = $html;

	print "Content-type: text/html\n\n";
	print &build_page('upfile:notes_attached.html');
}


#########################################################	
#	Function: 
#   	customers_advances_addorder
#
#	Created by:
#		HC
#
#	Modified By:
#
#   	Parameters:
#
#   	Returns:
#			- list Orders
#
#   	See Also:
#
sub customers_advances_addorder {
# --------------------------------------------------------
	my ($query,$click_url);
	$in{'id_customers'} = int($in{'id_customers'});
	$in{'id_name'} 		= 'id_customers';
	$in{'id_value'} 	= $in{'id_customers'};
	$in{'id_name2'} 	= 'id_customers_advances';
	$in{'id_value2'} 	= $in{'id_customers_advances'};

	if ($in{'keyword'}){
		$in{'keyword'} = &filter_values($in{'keyword'});
		$query	= "AND (sl_orders.ID_orders LIKE '%$in{'keyword'}%' OR sl_orders.Date LIKE '%$in{'keyword'}%' OR sl_orders.OrderNet LIKE '%$in{'keyword'}%')";
	}
	my($idcustomer);
	if($in{'id_customers'} eq 100000){$idcustomer = '';}else{ $idcustomer = "AND sl_orders.ID_customers = ". $in{'id_customers'}; }

	my $base_query = " 
						IFNULL((
							SELECT SUM(SalePrice - Discount + Shipping + Tax + ShpTax) 
							FROM sl_orders_products 
							WHERE 
								ID_orders = sl_orders.ID_orders 
								AND Status NOT IN ('Inactive','Order Cancelled')
						),0) AS Total,
						IFNULL((
							SELECT SUM(Amount) 
							FROM sl_orders_payments 
							WHERE 
								ID_orders = sl_orders.ID_orders
								AND Captured='Yes' 
								AND CapDate IS NOT NULL 
								AND CapDate != '0000-00-00'
								AND Status != 'Cancelled'
						),0) AS Paid
						FROM sl_orders 
						WHERE 1 ". $idcustomer ."
						AND sl_orders.Status NOT IN ('Cancelled','Void','System Error','Processed')
						". $query ."
						GROUP BY  sl_orders.ID_orders
						HAVING ( ABS(Total-Paid) > 0.01 )";


	my ($sth) = &Do_SQL("SELECT 
							sl_orders.ID_orders,
							". $base_query .";");

	
	$va{'matches'} = $sth->rows();
	my (@c) = split(/,/,$cfg{'srcolors'});
	if ($va{'matches'} > 0){

		(!$in{'nh'}) and ($in{'nh'}=1);
		$first = ($in{'nh'} - 1) * $usr{'pref_maxh'};			
		($va{'pageslist'},$qs) = &pages_list($in{'nh'},"/cgi-bin/common/apps/schid",$va{'matches'},$usr{'pref_maxh'});
		
		
		my ($sth) = &Do_SQL("SELECT 
								 sl_orders.ID_orders, 
								 sl_orders.Date,
								 sl_orders.Status,
								 ". $base_query ."
							ORDER BY FIELD(sl_orders.Status, 'Shipped','Processed','New','Pending'), Date LIMIT $first,$usr{'pref_maxh'};");
		
		while ($rec = $sth->fetchrow_hashref){

			my ($amounts) = &get_paid_unpaid($rec->{'ID_orders'});

			$d = 1 - $d;
			$click_url = "trjump('/cgi-bin/mod/$usr{'application'}/dbman?cmd=opr_customers_advances&view=". $in{'id_customers_advances'} ."&tab=2&addorder=". $rec->{'ID_orders'} ."')";
			$va{'searchresults'} .= qq|
			<tr bgcolor='$c[$d]' onmouseover='m_over(this)' onmouseout='m_out(this)' onClick="|. $click_url .qq|">
				<td class="smalltext" valign="top">|. $rec->{'ID_orders'} .qq|</td>
				<td class="smalltext" align='right'>|. &format_price($amounts->{'total'}) .qq|</td>
				<td class="smalltext" align='right' style='color:blue;'>|. &format_price($amounts->{'calculated_unpaid'}) . qq|</td>
				<td class="smalltext">|. $rec->{'Date'} .qq|</td>
				<td class="smalltext">|. &invoices_list($rec->{'ID_orders'}) .qq|</td>
				<td class="smalltext">|. $rec->{'Status'} .qq|</td>
			</tr>\n|;

		}
	}else{
		$va{'pageslist'} = 1;
		$va{'searchresults'} = qq|
			<tr>
				<td colspan='5' align="center">  |.&trans_txt('search_nomatches').qq|</td>
			</tr>\n|;
	}
	
	$va{'header'} = qq|
		<tr>
		    <td class="menu_bar_title">ID</td>
		    <td class="menu_bar_title">Total Order</td>
		    <td class="menu_bar_title">Unpaid</td>
		    <td class="menu_bar_title">Date</td>
		    <td class="menu_bar_title">Invoices</td>
		    <td class="menu_bar_title">Status</td>
		 </tr>\n|; 
	print "Content-type: text/html\n\n";
	print &build_page('searchid:addid.html');
}

#########################################################	
#	Function: 
#   	users_authorizer_setup
#
#	Created by:
#		GQ: 2017-02-09
#
#	Modified By:
#
#   	Parameters:
#
#   	Returns:
#			- list Orders
#
#   	See Also:
#
sub users_authorizer_setup {
# --------------------------------------------------------
	use JSON;

	my %response;

	if( $in{'id_user'} and $in{'id_auth'} ){

		my $sth = &Do_SQL("SELECT ID_admin_users_rel FROM cu_admin_users_rel WHERE ID_admin_users_main = ".$in{'id_user'}." AND Type_rel = 'Authorization' LIMIT 1;");
		$this_id = $sth->fetchrow();

		if( $this_id ){
			&Do_SQL("UPDATE cu_admin_users_rel SET ID_admin_users_rel1 = ".$in{'id_auth'}." WHERE ID_admin_users_rel = ".int($this_id).";");
		} else {
			&Do_SQL("INSERT INTO cu_admin_users_rel SET ID_admin_users_main = ".$in{'id_user'}.", ID_admin_users_rel1 = ".$in{'id_auth'}.", Type_rel = 'Authorization', Date=CURDATE(), Time=CURTIME(), ID_admin_users = ".$usr{'id_admin_users'}.";");
		}

		$response{'result'} = 200;
		$response{'message'} = 'OK';

	} else {
		$response{'result'} = 400;
		$response{'message'} = 'Data required';
	}

	print "Content-type: application/json\n\n";
	print encode_json(\%response);
}

1;
