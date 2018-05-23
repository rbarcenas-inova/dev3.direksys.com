	my $dir = getcwd;
	my($b_cgibin,$a_cgibin) = split(/cgi-bin/,$dir);
	my $home_dir = $b_cgibin.'cgi-bin/common';
	if (-e $home_dir."/subs/admin/lib_repman.pl"){
		require ($home_dir."/subs/admin/lib_repman.pl");
	}

##################################################################
#         CUSTOM REPORTS
##################################################################
sub repmans {
# --------------------------------------------------------

    use JSON;

	if(!&check_permissions('repmans'.$in{'id'},'','')){ &html_unauth; return; };

	my ($query_select,$query_where,@pcols,%ptypes,%pformat,%pfields,$col,$limits);
	if ($in{'fulllist'}){
		&repmans_fulllist();
		return;
	}
	## Load Record
	&load_cfg('admin_reports');
	my (%tmp) = &get_record('ID_admin_reports',$in{'id'},'admin_reports');
	
	## Fabian Cañaveral Verificar si se guardara Log
	$save_log = $tmp{'is_sensitive_information'};

	## AD-clean-bugs
	$tmp{'sql_from'} =~ s/\n/ /g;

	## Load vars
	$va{'reportname'} = $tmp{'name'} ;
	$va{'expanditem'} = $sys{'reportsmenu'};
	
	if ($tmp{'sql_group'}){
		$tmp{'sql_group'} = " GROUP BY $tmp{'sql_group'}";
	}
	if ($tmp{'sql_order'}){
		$tmp{'sql_order'} = " ORDER BY $tmp{'sql_order'} ";
		if ($tmp{'sql_order_type'} and !$in{'sortorder'}){
			$tmp{'sql_order'} .= " $tmp{'sql_order_type'} ";
		}elsif ($in{'sortorder'}){
			$tmp{'sql_order'} .= " $in{'sortorder'} ";
		}
	}

	# Si esta OK pone 1 si esta OFF pone 0
	my $sthvars = &Do_SQL("SELECT COUNT(*) FROM sl_vars WHERE VVALUE=1 AND VName = 'Replication_Slave_ON'");
	my ($vval) = $sthvars->fetchrow_array();

    ## Hash para la recolección de Condiciones a mostrar en Background Reports
    my %query_parameters;

	$vval =1; # AD temporalmente para el cierre
	
	## Alternative Conection
	if ($cfg{'use_ext_host_for_repmans'} and $vval == 1){
		&connect_db_w($cfg{'dbi_db_rep'},$cfg{'dbi_host_rep'},$cfg{'dbi_user_rep'},$cfg{'dbi_pw_rep'});
	}

	$sql = "SELECT * FROM admin_reports_fields WHERE ID_admin_reports='$in{'id'}' ORDER BY ListOrder ASC ;";
	$sth = ($cfg{'use_ext_host_for_repmans'} and $vval == 1)? &Do_SQL($sql,1) : &Do_SQL($sql);
	while ($rec = $sth->fetchrow_hashref){
		if ($rec->{'Filter'} eq 'Enable'){
			if ($rec->{'FormatType'} eq 'Date'){
					$va{'date_filters'} .= '#from_'.$rec->{'ID_admin_reports_fields'}.',#to_'.$rec->{'ID_admin_reports_fields'}.',#equal_'.$rec->{'ID_admin_reports_fields'}.',';
					$va{'filters'} .= qq|
					<tr>
				    <td width="30%">$rec->{'PrintName'} : </td>
				    <td class="smalltext"><input id="from_$rec->{'ID_admin_reports_fields'}" name="from_$rec->{'ID_admin_reports_fields'}" value="$in{'from_'.$rec->{'ID_admin_reports_fields'}}" size="40" onfocus="focusOn( this )" onblur="focusOff( this )" type="text"></td>
				    <td class="smalltext"><input id="to_$rec->{'ID_admin_reports_fields'}" name="to_$rec->{'ID_admin_reports_fields'}" value="$in{'to_'.$rec->{'ID_admin_reports_fields'}}" size="40" onfocus="focusOn( this )" onblur="focusOff( this )" type="text"></td>
				    <td class="smalltext"><input id="equal_$rec->{'ID_admin_reports_fields'}" name="equal_$rec->{'ID_admin_reports_fields'}" value="$in{'equal_'.$rec->{'ID_admin_reports_fields'}}" size="40" onfocus="focusOn( this )" onblur="focusOff( this )" type="text"></td>
				 </tr>\n|;
			}else{
				if ($rec->{'FieldType'} eq 'Field' and &is_enum($rec->{'Field'})){
					## Si es un enum
						$va{'filters'} .= qq|
						<tr>
						    <td width="30%">$rec->{'PrintName'} : </td>
						    <td class="smalltext">&nbsp;</td>
						    <td class="smalltext">&nbsp;</td>
						    <td class="smalltext">
						    	<select name="equal_$rec->{'ID_admin_reports_fields'}" onfocus="focusOn( this )" onblur="focusOff( this )">
						    		<option value=""></option>
						    		|.&build_select_from_enum($fields[1],$fields[0]).qq|
						    	</select>
						    </td>
						</tr>\n|;
				}elsif ($rec->{'FieldType'} eq 'Field' and &is_text($rec->{'Field'})){
					## Si es un texto
						$va{'filters'} .= qq|
						<tr>
						    <td width="30%">$rec->{'PrintName'} : </td>
						    <td class="smalltext">&nbsp;</td>
						    <td class="smalltext">&nbsp;</td>
						    <td class="smalltext">
						    	<input name="equal_$rec->{'ID_admin_reports_fields'}" value="$in{'equal_'.$rec->{'ID_admin_reports_fields'}}" size="40" onfocus="focusOn( this )" onblur="focusOff( this )" type="text">
						    	<input name="equal_$rec->{'ID_admin_reports_fields'}_text" value="1" type="hidden" />
						    </td>
						</tr>\n|;
				}else{					
					$va{'filters'} .= qq|
					<tr>
					    <td width="30%">$rec->{'PrintName'} : </td>
					    <td class="smalltext"><input name="from_$rec->{'ID_admin_reports_fields'}" value="$in{'from_'.$rec->{'ID_admin_reports_fields'}}" size="40" onfocus="focusOn( this )" onblur="focusOff( this )" type="text"></td>
					    <td class="smalltext"><input name="to_$rec->{'ID_admin_reports_fields'}" value="$in{'to_'.$rec->{'ID_admin_reports_fields'}}" size="40" onfocus="focusOn( this )" onblur="focusOff( this )" type="text"></td>
					    <td class="smalltext"><input name="equal_$rec->{'ID_admin_reports_fields'}" value="$in{'equal_'.$rec->{'ID_admin_reports_fields'}}" size="40" onfocus="focusOn( this )" onblur="focusOff( this )" type="text"></td>
					 </tr>\n|;
				}
			}
		}
		## Define Types
		push (@pcols,$rec->{'PrintName'}) if ($rec->{'Visibility'} ne 'Hidden');
		$ptypes{$rec->{'PrintName'}} = $rec->{'FieldType'};
		$pformat{$rec->{'PrintName'}} = $rec->{'FormatType'};
		$pfields{$rec->{'PrintName'}} = $rec->{'Field'};
		
		## Build Query / Select / WHERE
		if ($rec->{'FieldType'} eq 'Field'){
			my @arr_fields = split /\./, $rec->{'Field'};
			if ($arr_fields[0] ne $rec->{'Field'} and $rec->{'Visibility'} ne 'Hidden'){
				$query_select .= " `".$arr_fields[0]."`.`".$arr_fields[1]."`,";
				$rec->{'Field'} = "`".$arr_fields[0]."`.`".$arr_fields[1]."`";
			}else{
				$query_select .= " `$rec->{'Field'}`," if($rec->{'Visibility'} ne 'Hidden');
			}
			## Build Query / Where
			if ($in{'equal_'.$rec->{'ID_admin_reports_fields'}}){
				if ($rec->{'FormatType'} eq 'Date'){
					$query_where .= " AND $rec->{'Field'} BETWEEN '".&filter_values($in{'equal_'.$rec->{'ID_admin_reports_fields'}})." 00:00:00' AND '".&filter_values($in{'equal_'.$rec->{'ID_admin_reports_fields'}})." 23:59:59'";
                    $query_parameters{$rec->{'PrintName'}} = "BETWEEN ".&filter_values($in{'equal_'.$rec->{'ID_admin_reports_fields'}})." 00:00:00 AND ".&filter_values($in{'equal_'.$rec->{'ID_admin_reports_fields'}})." 23:59:59";
				}elsif ($in{'equal_'.$rec->{'ID_admin_reports_fields'}.'_text'}){
					$query_where .= " AND $rec->{'Field'} LIKE ('%".&filter_values($in{'equal_'.$rec->{'ID_admin_reports_fields'}})."%') ";
                    $query_parameters{$rec->{'PrintName'}} = "CONTAIN ".&filter_values($in{'equal_'.$rec->{'ID_admin_reports_fields'}});
				}else{
					$query_where .= " AND $rec->{'Field'}='".&filter_values($in{'equal_'.$rec->{'ID_admin_reports_fields'}})."' ";
                    $query_parameters{$rec->{'PrintName'}} = "EQUAL ".&filter_values($in{'equal_'.$rec->{'ID_admin_reports_fields'}});
				}
				
				$va{'extrains'} .= '&equal_'.$rec->{'ID_admin_reports_fields'}.'='.$in{'equal_'.$rec->{'ID_admin_reports_fields'}};
			}elsif ($in{'from_'.$rec->{'ID_admin_reports_fields'}} and $in{'to_'.$rec->{'ID_admin_reports_fields'}}){				
				if ($rec->{'FormatType'} eq 'Date'){
					$query_where .= " AND $rec->{'Field'} BETWEEN '".&filter_values($in{'from_'.$rec->{'ID_admin_reports_fields'}})." 00:00:00' AND '". $in{'to_'.$rec->{'ID_admin_reports_fields'}}." 23:59:59' ";
                    $query_parameters{$rec->{'PrintName'}} = "BETWEEN ".&filter_values($in{'from_'.$rec->{'ID_admin_reports_fields'}})." 00:00:00 AND ". $in{'to_'.$rec->{'ID_admin_reports_fields'}}." 23:59:59";
				}else{
					$query_where .= " AND $rec->{'Field'} BETWEEN '".&filter_values($in{'from_'.$rec->{'ID_admin_reports_fields'}})."' AND '". $in{'to_'.$rec->{'ID_admin_reports_fields'}}."' ";
                    $query_parameters{$rec->{'PrintName'}} = "BETWEEN ".&filter_values($in{'from_'.$rec->{'ID_admin_reports_fields'}})." AND ". $in{'to_'.$rec->{'ID_admin_reports_fields'}};
				}

				$va{'extrains'} .= '&from_'.$rec->{'ID_admin_reports_fields'}.'='.$in{'from_'.$rec->{'ID_admin_reports_fields'}};
				$va{'extrains'} .= '&to_'.$rec->{'ID_admin_reports_fields'}.'='.$in{'to_'.$rec->{'ID_admin_reports_fields'}};
			}elsif ($in{'from_'.$rec->{'ID_admin_reports_fields'}}){
				if ($rec->{'FormatType'} eq 'Date'){
					$query_where .= " AND $rec->{'Field'}>='".&filter_values($in{'from_'.$rec->{'ID_admin_reports_fields'}})." 00:00:00' ";
                    $query_parameters{$rec->{'PrintName'}} = "GREATER OR EQUAL THAN ".&filter_values($in{'from_'.$rec->{'ID_admin_reports_fields'}})." 00:00:00";
				}else{
					$query_where .= " AND $rec->{'Field'}>='".&filter_values($in{'from_'.$rec->{'ID_admin_reports_fields'}})."' ";
                    $query_parameters{$rec->{'PrintName'}} = "GREATER OR EQUAL THAN ".&filter_values($in{'from_'.$rec->{'ID_admin_reports_fields'}});
				}

				$va{'extrains'} .= '&from_'.$rec->{'ID_admin_reports_fields'}.'='.$in{'from_'.$rec->{'ID_admin_reports_fields'}};
			}elsif ($in{'to_'.$rec->{'ID_admin_reports_fields'}}){
				if ($rec->{'FormatType'} eq 'Date'){
					$query_where .= " AND $rec->{'Field'}<='".&filter_values($in{'to_'.$rec->{'ID_admin_reports_fields'}})." 23:59:59' ";
                    $query_parameters{$rec->{'PrintName'}} = "LOWER OR EQUAL THAN ".&filter_values($in{'to_'.$rec->{'ID_admin_reports_fields'}})." 23:59:59 ";
				}else{
					$query_where .= " AND $rec->{'Field'}<='".&filter_values($in{'to_'.$rec->{'ID_admin_reports_fields'}})."' ";
                    $query_parameters{$rec->{'PrintName'}} = "LOWER OR EQUAL THAN ".&filter_values($in{'to_'.$rec->{'ID_admin_reports_fields'}});
				}

				$va{'extrains'} .= '&to_'.$rec->{'ID_admin_reports_fields'}.'='.$in{'to_'.$rec->{'ID_admin_reports_fields'}};
			}
		}elsif($rec->{'FieldType'} eq 'SQLFunc'){
			$query_select .= " ($rec->{'Field'}),";
		}elsif($rec->{'FieldType'} eq 'Text'){
			$query_select .= " '$rec->{'Field'}',";
		}
		

		
		## Headers
		$va{'listheaders'} .= qq|	<td class="menu_bar_title">$rec->{'PrintName'}</td>\n| if($rec->{'Visibility'} ne 'Hidden');
	}
	chop($va{'date_filters'});
	chop($query_select);

	if($in{'action'}){		
		my $sql = "SELECT COUNT(*) FROM (SELECT 1 FROM " . $tmp{'sql_from'} . " WHERE " . $tmp{'sql_where'} . $query_where . $tmp{'sql_group'} . $tmp{'sql_order'} ." )tmp";

		$sth = ($cfg{'use_ext_host_for_repmans'} and $vval == 1) ?
			&Do_SQL($sql,1) :
			&Do_SQL($sql);
		$va{'matches'} = $sth->fetchrow();

		## 16122013-AD :: Se crea log para analizar cuantas veces ejecutaban reportes sin filtro
		if ($va{'matches'}){
			$va{'icono'} = $va{'matches'}.'::';
			$va{'icono'} .= 'Reporte sin filtros' if ($query_where eq '');
			$va{'icono'} .= '-Print' if($in{'print'});
			$va{'icono'} .= '-Export' if($in{'export'});
			&Do_SQL("INSERT INTO admin_logs (LogDate,  LogTime,  Message,  Action,  Type,  tbl_name,  Logcmd,  ID_admin_users,  IP ) VALUES (CURDATE(), CURTIME(), '$va{'icono'}', '$in{'id'}', 'Access', 'admin_reports', 'repmans', $usr{'id_admin_users'}, '".&get_ip."');");
		}
	}

	$tmp{'max_rows'} = 500 if(!$tmp{'max_rows'});
	if ($in{'action'} and (!$va{'matches'} or $va{'matches'} > $tmp{'max_rows'}) and $in{'extraction_method'} ne 'background'){
		$va{'message'} = &trans_txt('search_nomatches');
		$va{'message'} = &trans_txt('report_filter_required')." ".&format_number($tmp{'max_rows'})." Max rows, Required ".&format_number($va{'matches'}) if($va{'matches'} > $tmp{'max_rows'});

		## 16122013-AD :: Se crea log para analizar cuantas veces ejecutaban reportes grandes
		$va{'icono'} = "Max rows: ".&format_number($tmp{'max_rows'})." Required: ".&format_number($va{'matches'});
		&Do_SQL("INSERT INTO admin_logs (LogDate,  LogTime,  Message,  Action,  Type,  tbl_name,  Logcmd,  ID_admin_users,  IP ) VALUES (CURDATE(), CURTIME(), '$va{'icono'}', '$in{'id'}', 'Access', 'admin_reports', 'repmans', $usr{'id_admin_users'}, '".&get_ip."');");
	}else{
		if ($in{'action'}){
            if($in{'extraction_method'} ne 'background'){
    			if ($in{'print'}){
    				$limits = '';
    			}elsif($in{'export'}){
    				my ($fname) = $va{'reportname'} . '.csv';
    				$fname =~ s/\s/_/g;
    				print "Content-type: application/octetstream\n";
    				print "Content-disposition: attachment; filename=$fname\n\n";
    				print '"'. join('","',@pcols).'"' . "\n";  #Headers
    			}else{
    				(!$in{'nh'}) and ($in{'nh'}=1);
    				my ($first) = ($in{'nh'} - 1) * $usr{'pref_maxh'};			
    				($va{'pageslist'},$qs) = &pages_list($in{'nh'},"/cgi-bin/mod/$usr{'application'}/admin",$va{'matches'},$usr{'pref_maxh'});
    				$limits = "  LIMIT $first,$usr{'pref_maxh'}";
    			}
            }
			$sql = "SELECT $query_select FROM " . $tmp{'sql_from'} . " WHERE " . $tmp{'sql_where'} . $query_where . $tmp{'sql_group'} . $tmp{'sql_order'}. $limits;
            if($save_log == 1 and $cfg{'save_log'} == 1){
				$q_save = $sql;
				$q_save =~ s/\'/\'\'/g;
				$log_query = qq|INSERT INTO `sl_debug` (`cmd`, `id`, `log`, `Date`, `Time`, `ID_admin_users`) 
				VALUES ('log_query_report', '$in{'id'}', '$q_save', curdate(), curtime(), '$usr{'id_admin_users'}');|;
				&Do_SQL($log_query);
				
			}

            ## Se verifica si el usuario eligio descargar el reporte de modo Background
            if( $in{'extraction_method'} eq 'background' )
            {
                my $json_data = encode_json \%query_parameters;

                ## Checa si este reporte con la mismas condiciones, ha sido pedido con anterioridad.
                $result = &ax_set_report_background( 'repmans'.$in{'id'}, $json_data, $sql);
                if( $result->{'status'} ne 'Fail' )
                {
                    if( $result->{'status'} =~ m/Finished/ ){
                        $va{'message'} = &trans_txt('report_in_background_existing').'<a href="/cgi-bin/mod/admin/admin?cmd=extracted_reports&report='.$result->{'status'}.'"><img src="/sitimages/file.png" style="height:32px; vertical-align: middle;" /></a>';
                    }else{
                        $va{'message'} = &trans_txt('report_in_background_processing');
                    }
                    
                    print "Content-type: text/html\n\n";
                    print &build_page('repmans.html');
                    return null;
                }
            }            

			$sth = ($cfg{'use_ext_host_for_repmans'} and $vval == 1)? &Do_SQL($sql,1) : &Do_SQL($sql);
			while (my (@ary) = $sth->fetchrow_array){
				$va{'searchresults'} .= "<tr>\n";
				$col = 0;
				my ($export_line);
				for my $i(0..$#pcols){
					## Get Value
					my ($line_value);
					if ($ptypes{$pcols[$i]} eq 'CusFunc'){
						my($func) = 'repman_'. $pfields{$pcols[$i]};  ## External Func
						if (defined &$func){
							$line_value =  &$func(@ary,$query_where); 
						}else{
							$line_value = 'err:'.$func;
						}
					}else{
						$line_value = $ary[$col];
						++$col;
					}
					## Print based in Format
					if ($pformat{$pcols[$i]} eq 'Currency'){
						$va{'searchresults'} .= "<td align='right'>".&format_price($line_value)."</td>";
						$export_line .= '"'.&format_price($line_value) .'",' if($in{'export'});
					}elsif($pformat{$pcols[$i]} eq 'Number'){
						$va{'searchresults'} .= "<td align='right'>".&format_number($line_value)."</td>";
						$export_line .= '"'.&format_number($line_value).'",' if($in{'export'});
					}elsif($pformat{$pcols[$i]} eq 'ID9'){
						$va{'searchresults'} .= "<td align='right'>".&format_sltvid($line_value)."</td>";
						$export_line .= '"'. &format_sltvid($line_value) .'",' if($in{'export'});
					}elsif($pformat{$pcols[$i]} eq 'Account'){
						$va{'searchresults'} .= "<td align='right'>".&format_account($line_value)."</td>";
						$export_line .= '"'. &format_account($line_value) .'",' if($in{'export'});
					}else{
						$line_value =~ s/\"//g;
						$va{'searchresults'} .= "<td>$line_value</td>";
						$export_line .= '"'. $line_value .'",' if($in{'export'});
					}
				}
				if($in{'export'}){
					chop($export_line);
					print $export_line . "\n";
				}
				$va{'searchresults'} .= "</tr>\n";
			}

			$in{'db'} = 'admin_reports';
			&auth_logging2('repmans_viewed',$in{'id'});

			if ($in{'print'}){
				print "Content-type: text/html\n\n";
				print &build_page('repmans_plist.html');
			}elsif($in{'export'}){
				return;
			}else{
				print "Content-type: text/html\n\n";
				print &build_page('repmans_list.html');
			}
			return;
		}
	}
	
	print "Content-type: text/html\n\n";
	print &build_page('repmans.html');
}

sub repmans_fulllist {
# --------------------------------------------------------
	$va{'expanditem'} = $sys{'reportsmenu'};
	my ($d);
	my (@c) = split(/,/,$cfg{'srcolors'});
	my $where = '';
	if($in{'keyword'} ne ''){
		$where = " AND (Name like '%$in{'keyword'}%' OR Description like '%$in{'keyword'}%') ";
	}
	
	my($sth) = &Do_SQL("SELECT COUNT(*) FROM admin_reports WHERE 1 $where AND Status='Active';");			
	$va{'matches'} = $sth->fetchrow();
	if ($va{'matches'} > 0){
		(!$in{'nh'}) and ($in{'nh'}=1);
		my ($first) = ($in{'nh'} - 1) * $usr{'pref_maxh'};			
		($va{'pageslist'},$qs) = &pages_list($in{'nh'},"/cgi-bin/mod/$usr{'application'}/admin",$va{'matches'},$usr{'pref_maxh'});

		my ($sth) = &Do_SQL("SELECT * FROM admin_reports WHERE 1 $where AND Status='Active' LIMIT $first,$usr{'pref_maxh'};");	
		while ($rec = $sth->fetchrow_hashref){
			$d = 1 - $d;
			$va{'searchresults'} .= qq|
			<tr  bgcolor='$c[$d]' onmouseover="m_over(this)" onmouseout="m_out(this)">
				<td class="smalltext">$rec->{'Name'}</td>
				<td class="smalltext">$rec->{'Description'}</td>
				<td nowrap>
				<a href="/cgi-bin/mod/$usr{'application'}/admin?cmd=repmans&id=$rec->{'ID_admin_reports'}"><img src='[va_imgurl]/[ur_pref_style]/b_primary.png' title='Filter' alt='' border='0'></a> &nbsp;
				<a href="/cgi-bin/mod/$usr{'application'}/admin?cmd=repmans&id=$rec->{'ID_admin_reports'}&log=1&lisd=1"><img src='[va_imgurl]/[ur_pref_style]/b_view.png' title='Filter' alt='' border='0'></a> &nbsp;
				<a href="/cgi-bin/mod/$usr{'application'}/admin?cmd=repmans&id=$rec->{'ID_admin_reports'}&log=1&impd=1"><img src='[va_imgurl]/[ur_pref_style]/b_print.png' title='Print' alt='' border='0'>
				<a href="/cgi-bin/mod/$usr{'application'}/admin?cmd=repmans&id=$rec->{'ID_admin_reports'}&log=1&csvd=1"><img src='[va_imgurl]/[ur_pref_style]/b_xls.gif' title='Export' alt='' border='0'>
				</td>
			</tr>\n|;

			# $va{'searchresults'} .= qq|
			# <tr  bgcolor='$c[$d]' onmouseover="m_over(this)" onmouseout="m_out(this)">
			# 	<td class="smalltext">$rec->{'Name'}</td>
			# 	<td class="smalltext">$rec->{'Description'}</td>
			# 	<td nowrap>
			# 	<a href="/cgi-bin/mod/$usr{'application'}/admin?cmd=repmans&id=$rec->{'ID_admin_reports'}"><img src='[va_imgurl]/[ur_pref_style]/b_primary.png' title='Filter' alt='' border='0'></a> &nbsp;
			# 	<a href="/cgi-bin/mod/$usr{'application'}/admin?cmd=repmans&id=$rec->{'ID_admin_reports'}&action=1"><img src='[va_imgurl]/[ur_pref_style]/b_view.png' title='Filter' alt='' border='0'></a> &nbsp;
			# 	<a href="javascript:prnwin('/cgi-bin/mod/$usr{'application'}/admin?cmd=repmans&id=$rec->{'ID_admin_reports'}&action=1&print=1')"><img src='[va_imgurl]/[ur_pref_style]/b_print.png' title='Print' alt='' border='0'>
			# 	<a href="/cgi-bin/mod/$usr{'application'}/admin?cmd=repmans&id=$rec->{'ID_admin_reports'}&action=1&export=1"><img src='[va_imgurl]/[ur_pref_style]/b_xls.gif' title='Export' alt='' border='0'>
			# 	</td>
			# </tr>\n|;
		}
	}else{
		$va{'pageslist'} = 1;
		$va{'searchresults'} = qq|
			<tr>
				<td colspan="3" class="stdtxterr">|. &trans_txt('search_nomatches') . qq|</td>
			</tr>\n|;
	}
	
	print "Content-type: text/html\n\n";
	print &build_page('repmans_fulllist.html');
}

1;
