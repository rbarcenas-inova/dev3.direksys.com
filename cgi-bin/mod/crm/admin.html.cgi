#!/usr/bin/perl


################################################################
######             PRODUCT SHEET              ##################
################################################################

sub products_dsheet {
# --------------------------------------------------------
	print "Content-type: text/html\n\n";
	print &build_page('products_dsheet.html');
}

sub products_dsheet_window {
# --------------------------------------------------------
	my ($status,$pages);
	print "Content-type: text/html\n\n";
	print print &build_page('header_print.html');
	$in{'id_products'} = int($in{'id_products'});
	if ($in{'id_products'}){
		$status = &build_desc_page($in{'id_products'});
		($status eq 'ok') and (++$pages);
	}elsif($in{'id_products_bulk'}){
		my (@ids) = split(/,/, $in{'id_products_bulk'});
		for my $i(0..$#ids){
			$ids[$i] = int($ids[$i]);
			if ($ids[$i]){
				($status eq 'ok') and (print "<span style=\"page-break-before: always;\">&nbsp;</span>");
				$status = &build_desc_page($ids[$i]);
				($status eq 'ok') and (++$pages);
			}else{
				$status = 'error';
			}
		}
	}
	if (!$pages){
		print "<p>&nbsp;</p><p align='center'>".&trans_txt('search_nomatches')."</p>";
	}
	## <span style="page-break-before: always;">&nbsp;</span>
}

sub products {
# --------------------------------------------------------
	## TO-DO: Agregar Permisos
	($in{'view'}) and ($in{'id_products'} = $in{'view'});

	$in{'id_products'} = int($in{'id_products'});
	if ($in{'id_products'}>0){
		&load_cfg('sl_products');
		%tmp = &get_record('ID_products',$in{'id_products'},'sl_products');


		for (0..$#db_cols){
			$in{lc($db_cols[$_])} = $tmp{lc($db_cols[$_])};
		}

		print "Content-type: text/html\n\n";
		print &build_page('products_view.html');
	}else{
		&prod_list;
	}
}

sub msglist {
# --------------------------------------------------------
	if ($in{'action'}){
		$va{'message'} = &trans_txt('msgd_nomsgs');
	}
	print "Content-type: text/html\n\n";
	print &build_page('msgs_search.html');
}



sub wuform {
# --------------------------------------------------------
	my (@c) = split(/,/,$cfg{'srcolors'});
	$in{'zip'} = int($in{'zip'});
	if ($in{'zip'}){

		my ($sth) = &Do_SQL("SELECT COUNT(*) FROM sl_wuagents WHERE ZipCode='$in{'zip'}'");
		$va{'matches'} = $sth->fetchrow;
		if ($va{'matches'}>0){
			#$usr{'pref_maxh'} = 2;
			(!$in{'nh'}) and ($in{'nh'}=1);
			$first = ($in{'nh'} - 1) * $usr{'pref_maxh'};			
			($va{'pageslist'},$qs) = &pages_list($in{'nh'},"/cgi-bin/mod/sales/console",$va{'matches'},$usr{'pref_maxh'});
			#5551212
			my ($sth) = &Do_SQL("SELECT * FROM sl_wuagents WHERE ZipCode='$in{'zip'}' ORDER BY AgentName DESC LIMIT $first,$usr{'pref_maxh'};");
			while ($rec = $sth->fetchrow_hashref){
				$d = 1 - $d;
				$rec->{'Notes'} =~ s/\n/<br>/g;
				$va{'searchresults'} .= "<tr bgcolor='$c[$d]'>\n";
				$va{'searchresults'} .= "   <td class='smalltext'>$rec->{'AgentName'}<br>$rec->{'Address1'}<br>$rec->{'Address2'}</td>\n";
				$va{'searchresults'} .= "   <td class='smalltext' align='top'>$rec->{'Phone'}</td>\n";
				$va{'searchresults'} .= "</tr>\n";
			}
		}else{
			$va{'pageslist'} = 1;
			$va{'searchresults'} = qq|
				<tr>
					<td colspan='3' align="center">|.&trans_txt('search_nomatches').qq|</td>
				</tr>\n|;
		}
		print "Content-type: text/html\n\n";
		print &build_page("wulist.html");		
	}else{
		print "Content-type: text/html\n\n";
		print &build_page("wuform.html");			
	}
}

sub sameaddress{
# --------------------------------------------------------
# Forms Involved: 
# Created on: 01/28/09 12:35:18
# Author: MCC C. Gabriel Varela S.
# Description :   
# Parameters :
# Last Modified on: 01/29/09 09:26:58
# Last Modified by: MCC C. Gabriel Varela S: Se habilita para preorders. También se da formato a filas y se valida fecha.
	##
	## CH-TODO : Hay que expluir las ordenes de Distribuidores
	##

	my $caddate;

	if($in{'action'}==1){
		if($in{'date'} ne ""){
			$caddate='1';
			$caddate="date='$in{'date'}'" if($in{'date'});
			$sth=&Do_SQL("Select count(ID_orders)from(
	SELECT ID_orders
	FROM sl_orders
	INNER JOIN (
	SELECT Address1, /*Zip,*/count( ID_orders ) AS cuenta
	FROM sl_orders
	WHERE Date <= '$in{'date'}'
	GROUP BY Address1,Zip
	HAVING cuenta >1
	) AS tempo ON ( tempo.Address1 = sl_orders.Address1/* and tempo.Zip = sl_orders.Zip*/)
	WHERE Date = '$in{'date'}')as der");
			$va{'matches'} = $sth->fetchrow();
			if ($va{'matches'}>0){
				(!$in{'nh'}) and ($in{'nh'}=1);
				$first = ($in{'nh'} - 1) * $usr{'pref_maxh'};			
				($va{'pageslist'},$va{'qs'}) = &pages_list($in{'nh'},"/cgi-bin/mod/$usr{'application'}/admin",$va{'matches'},$usr{'pref_maxh'});
				$sth=&Do_SQL("Select ID_orders,sl_orders.Address1,orders,cuenta,/*Dates,*/sl_orders.Date,FirstName,LastName1,StatusPrd,StatusPay,sl_orders.Status
	FROM
	sl_orders 
	inner join (Select Address1,count(ID_orders)as cuenta,group_concat(ID_orders separator ',')as orders/*,group_concat(Date separator ',')as dates*/
	from sl_orders
	where Date <= '$in{'date'}'
	group by Address1
	having cuenta>1)as tempo on (tempo.Address1=sl_orders.Address1)
	inner join sl_customers on (sl_orders.ID_customers=sl_customers.ID_customers)
	where sl_orders.Date = '$in{'date'}'   LIMIT $first,$usr{'pref_maxh'}");
				my (@c) = split(/,/,$cfg{'srcolors'});
				while($rec=$sth->fetchrow_hashref){
					@cadorders=split((/,/,$rec->{'orders'}));
					for my $i(0..$#cadordersi){
						delete($cadordersi[$i]);#="";
					}
					my $j=0;
					for my $i(0..$#cadorders){
						if($rec->{ID_orders}!=$cadorders[$i]){
							$cadordersi[$j]="<a href=\"/cgi-bin/mod/crm/dbman?cmd=opr_orders&view=$cadorders[$i]\">$cadorders[$i]</a>";
							$j++;
						}
					}
					$cadtoorders=join(', ',@cadordersi);
					$d = 1 - $d;
					$va{'searchresults'} .= qq|
						<tr bgcolor='$c[$d]'>
							<td class='smalltext'><a href=\"/cgi-bin/mod/crm/dbman?cmd=opr_orders&view=$rec->{ID_orders}\">$rec->{ID_orders}</a></td>
							<td class='smalltext'>$rec->{'Date'}</td>
							<td class='smalltext'>$rec->{'FirstName'}</td>
							<td class='smalltext'>$rec->{'LastName1'}</td>
							<td class='smalltext'>$rec->{'StatusPrd'}</td>
							<td class='smalltext'>$rec->{'StatusPay'}</td>
							<td class='smalltext'>$rec->{'Status'}</td>
						</tr>
						<tr bgcolor='$c[$d]'>
							<td colspan="7">$cadtoorders</td>
						</tr>\n|;
				}
			}else{
				$va{'matches'} = 0;
				$va{'pageslist'} = 1;
				$va{'searchresults'} = qq|
								<tr>
									<td colspan='7' align='center'>|.&trans_txt('search_nomatches').qq|</td>
								</tr>\n|;
			}
			print "Content-type: text/html\n\n";
			print &build_page("sameaddress_list.html");
		}else{
			++$err;
			$error{'date'} = &trans_txt('invalid');
			print "Content-type: text/html\n\n";
			print &build_page("sameaddress.html");
		}
	}else{
		print "Content-type: text/html\n\n";
		print &build_page("sameaddress.html");
	}
}


##############################################
####################
#################### REPORTES
####################
###############################################



sub authnumber{
#-----------------------------------------
# Created on: 09/08/09  15:49:58 By  Roberto Barcenas
# Forms Involved: 
# Description : Genera codigos de autorizacion para permitir activar un nivel de Downsale en Inbound
# Parameters : 
# Last Modified by RB on 2010/01/21: Se eliminan los signos "+" en la llamada
# Last Modified by RB on 2011/11/23: Se inactiva esta opcion

	my ($num,$cad);
	$va{'authnumr'} = '----';
 	
 	if( $cfg{'use_downsale_authorization_number'} and $cfg{'use_downsale_authorization_number'} == 1 ){
 		$num = int(rand 10000);
 		$cad = sprintf ("%.04d",$num);
 		$va{'authnumr'} = $cad;

 		&Do_SQL("REPLACE INTO sl_vars SET VName='Downsale Price $usr{'id_admin_users'}',VValue='$usr{'id_admin_users'},$cad',Definition_En='Downsale Price Authorizathion';");
 	}

	print "Content-type: text/html\n\n";
	print &build_page('authnumber.html');		
}

sub drop_calls{
#-----------------------------------------
# Last Modified on: 10/05/09 11:19:59
# Last Modified by: MCC C. Gabriel Varela S: Se conecta a S7 directamente.
#Last modified on 13 Oct 2010 17:31:06
#Last modified by: MCC C. Gabriel Varela S. :Se hace inner con sl_numbers_assign
#Last Modified on: 08/11/09 10:00:59
#Last modified by: EP. :Se agregan textos a trans_txt
#Last modified by: EP. :Se modificaron los querys para que tome la informacion de la misma base y no se conecte a otra.
# # TO DO -> CHECAR LA TABLA DE SL_NUMBERS_ASSIGN
	##
	if($in{'action'}){
		### Busqueda por rango de tiempo
		if($in{'from_time'} or $in{'to_time'}){
			$in{'from_time'} 	= "00:00:00"	if !$in{'from_time'};
			$in{'to_time'} 		= "23:59:59"	if !$in{'to_time'};
			$va{'report_tbl'} .= "<tr><td width='100' class='smalltext'>".&trans_txt('reoprts_from_schedule')." : </td><td class='smalltext'>$in{'from_time'}</td></tr>\n";
			$va{'report_tbl'} .= "<tr><td width='100' class='smalltext'>".&trans_txt('reoprts_to_schedule')." : </td><td class='smalltext'>$in{'to_time'}</td></tr>\n";
			$query .= " AND time(sl_leads_calls.Time) BETWEEN '$in{'from_time'}' AND '$in{'to_time'}'";
		}
		## Filter by Date
		if ($in{'from_date'}){
			$in{'from_date'}=~s/\//-/g;
			$va{'report_tbl'} .= "<tr><td width='100' class='smalltext'>".&trans_txt('from_date')." : </td><td class='smalltext'>$in{'from_date'}</td></tr>\n";
			$query .= " AND DATE(sl_leads_calls.Date)>='$in{'from_date'}' ";
		}
		if ($in{'to_date'}){
			$in{'to_date'}=~s/\//-/g;
			$va{'report_tbl'} .= "<tr><td width='100' class='smalltext'>".&trans_txt('to_date')." : </td><td class='smalltext'>$in{'to_date'}</td></tr>\n";
			$query .= " AND DATE(sl_leads_calls.Date)<='$in{'to_date'}' ";
		}
		##Filter by duration
		if($in{'duration'} eq '1to3min'){
			$va{'report_tbl'} .= "<tr><td width='100' class='smalltext'>".&trans_txt('reports_duration')." : </td><td class='smalltext'>".&trans_txt('drop_calls_one_to_three')."</td></tr>\n";
			$query .= " AND Duration BETWEEN 61 AND 180 ";
		}elsif($in{'duration'} eq '0to1min'){
			$va{'report_tbl'} .= "<tr><td width='100' class='smalltext'>".&trans_txt('reports_duration')." : </td><td class='smalltext'>".&trans_txt('drop_calls_less_one_minute')."</td></tr>\n";
			$query .= " AND Duration BETWEEN 1 AND 60 ";
		}
		
		$query .=" AND (LOCATE('SIP',channel) > 0 OR LOCATE('vixicom',channel) > 0) ";

		##$query .=" AND sl_mediadids.grupo IN('','US')"	if $in{'e'}	==	1;
		##$query .=" AND sl_mediadids.grupo = 'GTS'	"	if $in{'e'}	==	4;

		## Filter by Type
		if($in{'type'}){
			$in{'type'}=~ s/\|/','/g;
			$va{'report_tbl'} .= "<tr><td width='100' class='smalltext'>".&trans_txt('reports_classification')." : </td><td class='smalltext'>$in{'type'}</td></tr>\n";
			$query .= " AND Calif IN ('$in{'type'}') ";
			$in{'type'} =~ s/','/\|/g;
			$modquery = " NOT ";
		}else{
			$modquery = "";
		}
		
		$va{'report_tbl'} .= "<tr><td class='smalltext' colspan='2'>".&trans_txt('reports_created_by').": (".$usr{'id_admin_users'}.") ".$usr{'firstname'}." ".$usr{'lastname'}." \@ ".&get_sql_date." &nbsp;".&get_time()."</td></tr>";
		
		my $sth;
		if(!$in{'exclude_notes'} and !$in{'type'}) {
			if($cfg{'product_assign'}==1) {
				# # TO DO -> CHECAR LA TABLA DE SL_NUMBERS_ASSIGN
				# $sth=&Do_SQL("-*Select count(*) 
						# from cdr USE INDEX (accountcode)
						# /*INNER JOIN dnis ON accountcode = USDnis AND RIGHT(dst,4) = MXDnis */
						# INNER JOIN sl_numbers USE INDEX (didusa) ON didusa = accountcode
						# inner join sl_numbers_assign on sl_numbers.ID_numbers=sl_numbers_assign.ID_numbers
						# where 1 $query");
			} else {
				###LISTO
				$sth=&Do_SQL("SELECT COUNT(*) 
						FROM sl_leads_calls USE INDEX (DIDUS)
						INNER JOIN sl_mediadids USE INDEX (didusa) ON didusa = DIDUS
						WHERE 1 $query");
			}
		}else{
			$va{'report_tbl'} .= "<tr><td width='100' class='smalltext'>".&trans_txt('drop_calls_excluded_notes')."</td></tr>\n";
			if($cfg{'product_assign'}==1){
				# TO DO -> CHECAR LA TABLA DE SL_NUMBERS_ASSIGN
				# $sth=&Do_SQL("*Select count(*) 
						# from cdr USE INDEX (accountcode)
						# /*INNER JOIN dnis ON accountcode = USDnis AND RIGHT(dst,4) = MXDnis */
						# INNER JOIN sl_numbers USE INDEX (didusa) ON didusa = accountcode
						# inner join sl_numbers_assign.ID_numbers=sl_numbers.ID_numbers
						# left join cdr_s7_notes on (REPLACE(cdr.src,'+','')=cdr_s7_notes.src and cdr.calldate=cdr_s7_notes.calldate) 
						# where 1 $query 
						# and ID_cdr_s7_notes is $modquery null");
			}else{
				###LISTO
				$sth=&Do_SQL("SELECT COUNT(*) 
						FROM sl_leads_calls USE INDEX (DIDUS)
						INNER JOIN sl_mediadids USE INDEX (didusa) ON didusa = DIDUS
						LEFT JOIN sl_leads_notes ON sl_leads_calls.ID_leads = sl_leads_notes.ID_leads and sl_leads_calls.Date = sl_leads_notes.Date
						WHERE 1   $query 
						AND ID_leads_notes IS $modquery NULL");
			}
		}
		
		$va{'matches'}=$sth->fetchrow;
		if ($va{'matches'}>0){
			(!$in{'nh'}) and ($in{'nh'}=1);
			my (@c) = split(/,/,$cfg{'srcolors'});
			$first = ($in{'nh'} - 1) * $usr{'pref_maxh'};	
			#my ($sth) = &Do_SQL($query_list);
			#$va{'matches'} = $sth->rows;
			($va{'pageslist'},$qs) = &pages_list($in{'nh'},"/cgi-bin/mod/$usr{'application'}/admin",$va{'matches'},$usr{'pref_maxh'});
			if ($in{'print'}){
				$limit="";
			}else{
				$limit=" LIMIT $first,$usr{'pref_maxh'} ";
			}
			my $sth;
			if(!$in{'exclude_notes'} and !$in{'type'}){
				if($cfg{'product_assign'}==1){					
					# # TO DO -> CHECAR LA TABLA DE SL_NUMBERS_ASSIGN
					# $sth=&Do_SQL("Select *,src as ID_cdr_s7, right(dst,4) as dst,product_assign as product 
							# from cdr USE INDEX (accountcode)
							# /*INNER JOIN dnis ON accountcode = USDnis AND RIGHT(dst,4) = MXDnis */
							# INNER JOIN sl_numbers USE INDEX (didusa) ON didusa = accountcode
							# inner join sl_numbers_assign on sl_numbers.ID_numbers=sl_numbers_assign.ID_numbers
							# where 1 $query 
							# order by calldate desc $limit");
				}else{
					$sth=&Do_SQL("Select *,src as ID_cdr_s7, right(dst,4) as dst 
							from cdr USE INDEX (accountcode)
							INNER JOIN sl_numbers USE INDEX (didusa) ON didusa = accountcode
							where 1 $query 
							order by calldate desc $limit");
							
							"FROM sl_leads_calls USE INDEX (DIDUS)
							 INNER JOIN sl_mediadids USE INDEX (didusa) ON didusa = DIDUS"
				}
			}else{
				if($cfg{'product_assign'}==1){
					# TO DO -> CHECAR LA TABLA DE SL_NUMBERS_ASSIGN
					# $sth=&Do_SQL("Select cdr.*,cdr.src as ID_cdr_s7, right(dst,4) as dst,product_assign as product
							# from cdr USE INDEX (accountcode)
							# /*INNER JOIN dnis ON accountcode = USDnis AND RIGHT(dst,4) = MXDnis */
							# INNER JOIN sl_numbers USE INDEX (didusa) ON didusa = accountcode
							# inner join sl_numbers_assign on sl_numbers.ID_numbers=sl_numbers_assign.ID_numbers
							# left join cdr_s7_notes on (REPLACE(cdr.src,'+','')=cdr_s7_notes.src and cdr.calldate=cdr_s7_notes.calldate) 
							# where 1 $query 
							# and ID_cdr_s7_notes is $modquery null 
							# order by cdr.calldate desc $limit");
				}else{
					$sth=&Do_SQL("Select cdr.*,cdr.src as ID_cdr_s7, right(dst,4) as dst 
							from cdr USE INDEX (accountcode)
							INNER JOIN sl_numbers USE INDEX (didusa) ON didusa = accountcode
							left join cdr_s7_notes on (REPLACE(cdr.src,'+','')=cdr_s7_notes.src and cdr.calldate=cdr_s7_notes.calldate) 
							where 1 $query 
							and ID_cdr_s7_notes is $modquery null 
							order by cdr.calldate desc $limit");
				}
			}
			while($rec=$sth->fetchrow_hashref){
				$d = 1 - $d;
				$didmx="";
				$linkorders="";
				#$didmx=$rec->{'lastdata'};
				#$didmx=~/\/(\d+)\@/;
				#$didmx=$1;
				$didmx=$rec->{'dst'};
				$rec->{'src'}	=~	s/\+//g;

				@ary = split(/,/,orders_vs_clid($rec->{'src'}));

				for(0..$#ary){
					$cmd='orders';
					$cmd = 'preorders' if($ary[$_]) >= 500000;

					$linkorders .= "<br>"	if $linkorders ne '';
					$linkorders .= qq|<a href="" onClick="trjump('/cgi-bin/mod/crm/dbman?cmd=$cmd&view=$ary[_]'); return false;">$ary[$_]</a>|;
				}
				$linkorders="---"	if $linkorders eq '';


				$va{'searchresults'} .= qq|<tr bgcolor='$c[$d]'>|;
				$va{'searchresults'} .= qq|<td  valign='top'>$linkorders</td>|;
				$va{'searchresults'} .= qq|<td  valign='top'>$rec->{'src'}</td>|;
				$va{'searchresults'} .= qq|<td  valign='top'>$rec->{'calldate'}</td>|;
				$va{'searchresults'} .= qq|<td  valign='top' align="center">$rec->{'duration'}</td>|;
				$va{'searchresults'} .= qq|<td  valign='top' align="left"><span style="color:red;">No. 800:</span> $rec->{'num800'}<br><span style="color:red;">|.&trans_txt('rep_orders_p_dids_usa').qq|:</span> $rec->{'accountcode'}<br><span style="color:red;">|.&trans_txt('rep_orders_p_dids_mex').qq|:</span> $didmx</td>|;
				$va{'searchresults'} .= qq|<td  valign='top' align="left">$rec->{'product'}</td>|;
					$va{'searchresults'} .= qq|<td  valign='top'>|.&check_callnote($rec->{'ID_cdr_s7'},$rec->{'calldate'}).qq|<a id="showcn_$rec->{'ID_cdr_s7'}">&nbsp;</a>
																		<div id="viewcn_$rec->{'ID_cdr_s7'}" style="visibility: hidden; display: none; background-color: #ffffff;width:700px">
																			<div class="menu_bar_title" id="ajax_vdrag_$rec->{'ID_cdr_s7'}" align="left" style="width:700px;">
																				<img id="ajax_vexit_$rec->{'ID_cdr_s7'}" src="/sitimages//default/popupclose.gif" />&nbsp;&nbsp;&nbsp;|.&trans_txt('reports_call_notes').qq|
																			</div>
																			<div class='formtable' style="width:700px;border:1px solid;">
																				<IFRAME SRC='/cgi-bin/common/apps/ajaxbuild.cgi?ajaxbuild=check_xcallnote_view&id_cdr=$rec->{'ID_cdr_s7'}&calldate=$rec->{'calldate'}&script_url=$script_url&action=1&nh=[in_nh]&from_date=[in_from_date]&to_date=[in_to_date]&from_time=[in_from_time]&to_time=[in_to_time]&duration=[in_duration]&exclude_notes=[in_exclude_notes]' name='rcmd' TITLE='Recieve Commands' width='700' height='350' FRAMEBORDER='0' MARGINWIDTH='0' MARGINHEIGHT='0' SCROLLING='auto'>
																					<h2>Unable to do the script</H2>
																					<h3>Please update your Browser</H3>
																				</IFRAME>	
																			</div>
																		</div>
																		<div id="postcn_$rec->{'ID_cdr_s7'}" style="visibility: hidden; display: none; background-color: #ffffff;">
																			<div class="menu_bar_title" id="ajax_pdrag_$rec->{'ID_cdr_s7'}" align="left">
																				<img id="ajax_pexit_$rec->{'ID_cdr_s7'}" src="/sitimages//default/popupclose.gif" />&nbsp;&nbsp;&nbsp;|.&trans_txt('reports_call_notes').qq|
																			</div>
																			<div class='formtable'>
																				<IFRAME SRC='/cgi-bin/common/apps/ajaxbuild.cgi?ajaxbuild=check_xcallnote_post&id_cdr=$rec->{'ID_cdr_s7'}&calldate=$rec->{'calldate'}&script_url=$script_url&action=1&nh=[in_nh]&from_date=[in_from_date]&to_date=[in_to_date]&from_time=[in_from_time]&to_time=[in_to_time]&duration=[in_duration]&exclude_notes=[in_exclude_notes]' name='rcmd' TITLE='Recieve Commands' width='446' height='320' FRAMEBORDER='0' MARGINWIDTH='0' MARGINHEIGHT='0' SCROLLING='auto'>
																					<h2>|.&trans_txt('unable_do_script').qq|</H2>
																					<h3>|.&trans_txt('update_browser').qq|</H3>
																				</IFRAME>	
																			</div>
																		</div>
																	</td>|;
				$va{'searchresults'} .= qq|</tr>\n|;
			}
		}else{
			$va{'tot_cant'} = 0;
			$va{'tot_amount'} = &format_price(0);
			$va{'matches'} = 0;
			$va{'pageslist'} = 1;
			$va{'searchresults'} .= qq|
				<tr>
					<td colspan="6" align="center">|.&trans_txt('search_nomatches').qq|</td>
				</tr>\n|;
		}

		if ($in{'print'}){
			print "Content-type: text/html\n\n";
			print &build_page('header_print.html');
			print &build_page('drop_calls_print.html');
		}else{
			print "Content-type: text/html\n\n";
			print &build_page('drop_calls_list.html');
		}
					
	}else{
		print "Content-type: text/html\n\n";
		print &build_page('drop_calls.html');
	}
}


sub tracking_email_reply{
# --------------------------------------------------------
# Forms Involved: 
# Created on: 13 Oct 2010 12:17:42
# Author: MCC C. Gabriel Varela S.
# Description :   
# Parameters :
# 	<input type="hidden" name="subject" value="Re:[in_subject] case: [in_uid]">
# 	<input type="hidden" name="from" value="[in_to]">
# 	<input type="hidden" name="to" value="[in_from]">
	my $err=0;
	my $dir_emails = 'email_templates/';
	my $str_template = '';

	if ($in{'action_reply'}){
		if (!$in{'subject'}){
			$va{'message'}  = &trans_txt('reqfields');
			$error{'subject'} = &trans_txt('required');
			$err++;	
		}

		if (!$in{'from'}){
			$va{'message'}  = &trans_txt('reqfields');
			$error{'from'} = &trans_txt('required');
			$err++;	
		}

		if (!$in{'to'}){
			$va{'message'}  = &trans_txt('reqfields');
			$error{'to'} = &trans_txt('required');
			$err++;	
		}

		if (!$in{'body'}){
			$va{'message'}  = &trans_txt('reqfields');
			$error{'body'} = &trans_txt('required');
			$err++;	
		}



		if(!$err){
			my $id_orders = int($in{'id_orders'});

			if($in{'to'}){
				$va{'email'} = $in{'to'};
			}else{
				$va{'email'} = $to_mail;
			}

			## Sender Information
			$va{'contact_phone'} = $cfg{'cservice_phone'};
			$va{'contact_phone'} = '1-888-425-5350';
			$va{'contact_mail'} = $in{'from'};
			$va{'sales_name'} = "Innovagroup USA" if (!$in{'e'} or $in{'e'}eq'1');
			$va{'sales_name'} = "Innovagroup Puerto Rico" if ($in{'e'}eq'2');
			$va{'sales_name'} = "Innovagroup USA" if ($in{'e'}eq'3');
			$va{'sales_name'} = "General Trading Services" if ($in{'e'}eq'4');
			$va{'sales_name'} = "General Marketing Solutions" if ($in{'e'}eq'5');



			my $uname	= `uname -n`;
			my $new_sent_mail=0;
			if($uname =~ /s11/ or $uname=~/washydoro/){
					#&cgierr("From:$in{'from'}\r\nTo:$va{'email'}\r\nSubject:$in{'subject'}\r\nBody:\r\n$in{'body'}");
					$status = &send_mail($in{'from'},$va{'email'},$in{'subject'},$in{'body'},'Content-type: text/plain; charset=iso-8859-1');
# 					&send_mail($in{'from'},"rbarcenas\@innovagroupusa.com",$in{'subject'},$body);
# 					&send_mail($in{'from'},"gvsauceda\@innovagroupusa.com",$in{'subject'},$body);
    

					if($status eq 'ok'){
						$new_sent_mail=&save_imap_email($in{'from'},$va{'email'},$in{'subject'},$in{'body'});
							&auth_logging('trackingemail_reply:'.$new_sent_mail,$id_orders);	
					}else{
							&auth_logging('trackingemail_reply_failed',$id_orders);
					}
			}else{
					$status = 'ok';
			}
			$va{'message'} .= "Mail Sent to $va{'email'}: $status<SCRIPT language='JavaScript'>
<!--
window.location='/cgi-bin/mod/crm/dbman?cmd=tracking_email&view=$in{'id_tracking_email'}&message=Mail Sent to $va{'email'}: $status';
//-->
</SCRIPT>";
			$in{'db'}='sl_tracking_email';
			&auth_logging('email_replied'.$status,$in{'id_tracking_email'});
			if($status eq'ok')
			{
#				use HTML::Entities ();
#				$in{'from'}=HTML::Entities::encode($in{'from'});
#				$in{'to'}=HTML::Entities::encode($in{'to'});
				&Do_SQL("Insert into sl_tracking_email_out set 
				`id_tracking_email`=$in{'id_tracking_email'},
				`Uid`=$new_sent_mail,
				`subject`='".&filter_values($in{'subject'})."',
				`to`='".&filter_values($in{'to'})."',
				`EmailDate`=curdate(),
				`from`='".&filter_values($in{'from'})."',
				`Body`='$in{'body'}',
				`ID_orders`='$in{'id_orders'}',
				`site`='$in{'site'}',
				`Status`='Active',
				`Date`=curdate(),
				`Time`=curtime(),
				`ID_admin_users`=$usr{'id_admin_users'}");
				&Do_SQL("update sl_tracking_email set ID_orders=$in{'id_orders'} where Uid=$in{'uid'}");
			}

		}
	}
	else
	{
		my $emailq=&Do_SQL("Select `uid`,`subject`,`to` as `from`,`from` as `to`,`body`,`id_orders`,`site` from sl_tracking_email where ID_tracking_email=$in{'id_tracking_email'}");
		$recemailq=$emailq->fetchrow_hashref;
		foreach $key (keys %{$recemailq})
		{
			$in{$key} = $recemailq->{$key};
		}
	  #cgierr("Values".$values);
	  $in{'subject'}="Re: $in{'subject'} (case number $in{'uid'})";

	  $in{'body'}=~s/(.*)\n/>$1\n/gi;
	  my $bodyf ;
	  $bodyf = &build_page($str_template . $dir_emails . $in{'template'} .".txt") if($in{'template'} ne'none');
	  $in{'body'}="$bodyf\n\n\n\n$in{'body'}";
  }
  
	print "Content-type: text/html\n\n";
	print &build_page('tracking_email_reply.html');

}



sub send_sms{
	# --------------------------------------------------------
	# Created on: 10/25/10 7:57 PM
	# Author: L.I. Roberto Barcenas.
	# Description : Envia sms con el API de Twilio
	# Parameters : From, To, Body
	# Forms Involved: follow-up send_sms | 

	my($query,$queryf);

	print "Content-type: text/html\n\n";


	if( $in{'action'} )
	{


		if( !$in{'to_number'} ){
			$va{'message'}  = &trans_txt('reqfields');
			$error{'to_number'} = &trans_txt('required');
			$err++;
		}else{
			$in{'to_number'} =~ s/\s|-|\///g;
		}

		if( !$in{'to_message'} )
		{
			$va{'message'}  = &trans_txt('reqfields');
			$error{'to_message'} = &trans_txt('required');
			$err++;
		}

		$in{'to_message'} =~ tr/á/a/;
		$in{'to_message'} =~ tr/é/e/;
		$in{'to_message'} =~ tr/í/i/;
		$in{'to_message'} =~ tr/ó/o/;
		$in{'to_message'} =~ tr/ú/u/;


		if(!$err)
		{

    		use LWP::UserAgent;
			
			my $ua = LWP::UserAgent->new;
			my $response = $ua->post(
										$cfg{'api_url'}.'sms/send/',
										'Content-Type' => 'application/x-www-form-urlencoded',
										'Authorization' => $cfg{'api_direksys_key'},
										'Content' => 'to='.$in{'to_number'}.'&msg='.$in{'to_message'}
									);

			$va{'result'} = $response->content; 

			my ($sth) = &Do_SQL("INSERT INTO sl_twilio_sms_logs SET  Date=CURDATE(),Time=CURTIME(),ID_admin_users='$usr{'id_admin_users'}';");

		}
	}

	print &build_page('send_sms.html');

}


sub eco_orders{
# --------------------------------------------------------
# Forms Involved:
# Created on: 25 Aug 2010 17:32:37
# Author: MCC C. Gabriel Varela S.
# Description :
# Parameters :
# Last Time Modified By RB on 31/08/2010 : Se agrega Ptype a la orden y captura de pago si es TDC
# Last Time Modified By RB on 03/1/2011 : Se agrega language para el envio de correo de confirmacion y escaneo
#Last modified on 3/25/11 9:56 AM
#Last modified by: MCC C. Gabriel Varela S. : Se cambia 4122 por 4688
# Last Modified by RB on 04/15/2011 12:39:42 PM : Se agrega cero(id_orders) como parametro para funcion calculate_taxes
# Last Modified by RB on 06/07/2011 01:29:24 PM : Se agrega City como parametro para calculate_taxes
#Last modified on 14 Jun 2011 18:10:33
#Last modified by: MCC C. Gabriel Varela S. : Se evalúa si crea cliente o no
# Last time Modified By RB on 10/07/2011: Se agrega Amazon

	my ($x,$err,$query);

	if($in{'id_customers'}ne'' and !$in{'action'})
	{
		my $sth=&Do_SQL("Select *
		from sl_customers
		where ID_customers='$in{'id_customers'}'
		limit 1");
		$rec=$sth->fetchrow_hashref;
		$in{'firstname'}=$rec->{'FirstName'};
		$in{'lastname1'}=$rec->{'LastName1'};
		$in{'lastname2'}=$rec->{'LastName2'};
		$in{'sex'}=$rec->{'Sex'};
		$in{'phone1'}=$rec->{'Phone1'};
		$in{'address1'}=$rec->{'Address1'};
		$in{'address2'}=$rec->{'Address2'};
		$in{'address3'}=$rec->{'Address3'};
		$in{'urbanization'}=$rec->{'Urbanization'};
		$in{'city'}=$rec->{'City'};
		$in{'state'}=$rec->{'State'};
		$in{'zip'}=$rec->{'Zip'};
		$in{'email'}=$rec->{'Email'};
		print "Content-type: text/html\n\n";
		print &build_page('eco_orders_with_customer.html');
		return;
	}
	if($in{'action'})
	{
		#Valida los datos para la creación de cliente
		$err = &validate_eco_orders();
		&load_cfg('sl_customers');
		($x,$query) = &validate_cols('1');

		if(!$in{'id_admin_users'}){
			$error{'id_admin_users'}=&trans_txt('required');
			$err++;
		}

		$err += $x;
		if ($err==0)
		{
			#Inserta cliente
			if(!$in{'id_customers'})
			{
				$sth=&Do_SQL("Insert into sl_customers
				set FirstName='$in{'firstname'}',
				LastName1='$in{'lastname1'}',
				LastName2='$in{'lastname2'}',
				Sex='$in{'sex'}',
				Phone1='$in{'phone1'}',
				Cellphone='$in{'cellphone'}',
				Email='$in{'email'}',
				Address1='$in{'address1'}',
				Address2='$in{'address2'}',
				Address3='$in{'address3'}',
				urbanization='$in{'urbanization'}',
				City='$in{'city'}',
				State='$in{'state'}',
				Zip='$in{'zip'}',
				Country='UNITED STATES',
				Status='Active',
				Type='Retail',
				Date=curdate(),
				Time=curtime(),
				ID_admin_users='$in{'id_admin_users'}'");
				$lastid_cus = $sth->{'mysql_insertid'};

			}else{
				$lastid_cus=$in{'id_customers'};
			}
# 			$lastid_cus=217127;
			#Calcular OrderQty,OrderShp,OrderTax,OrderNet
			$orderqty=0;
			for my $i(1..5){
				if($in{"id_products$i"}){
					$orderqty++;
				}
			}
			$ordertax=&calculate_taxes($in{'zip'},$in{'state'},$in{'city'},0);
			$ordershp=0;
			
			for my  $i(1..5){
				if($in{"shipping$i"}){
					$ordershp+=$in{"shipping$i"};
				}
			}
			$ordernet=0;
			for my $i(1..5){
				if($in{"sprice$i"}){
					$ordernet+=$in{"sprice$i"};
				}
			}
			#Language
			$in{'language'}='spanish' if !$in{'language'};

			#Inserta la orden
			$sth=&Do_SQL("Insert into sl_orders set ID_customers=$lastid_cus,Address1='$in{'address1'}',Address2='$in{'address2'}',Address3='$in{'address3'}',urbanization='$in{'urbanization'}',City='$in{'city'}',State='$in{'state'}',Zip='$in{'zip'}',Country='UNITED STATES',shp_type=1,shp_Address1='$in{'address1'}',shp_Address2='$in{'address2'}',shp_Address3='$in{'address3'}',shp_urbanization='$in{'urbanization'}',shp_City='$in{'city'}',shp_State='$in{'state'}',shp_Zip='$in{'zip'}',shp_Country='UNITED STATES',StatusPrd='None',StatusPay='None',OrderTax='$ordertax',OrderQty='$orderqty',OrderShp='$ordershp',OrderNet='$ordernet',Ptype='Credit-Card',language='$in{'language'}',Status=IF('$in{'type'}' != 'Credit-Card','Processed','Void'),Date=curdate(),Time=curtime(),ID_admin_users='$in{'id_admin_users'}'");
			$lastid_ord = $sth->{'mysql_insertid'};


			&add_order_notes_by_type( $lastid_ord,"Order Created","Web Creator");
			#Inserta los productos
			#&cgierr("Productos");
			for my $i(1..5){
				if($in{"id_products$i"}){
					#calcular el tax aquí.
					$tax=$in{"sprice$i"}*$ordertax;
					$sth=&Do_SQL("Insert into sl_orders_products set ID_products='".$in{"id_products$i"}."',ID_orders='$lastid_ord',Quantity=1,SalePrice='".$in{"sprice$i"}."',Shipping='".$in{"shipping$i"}."',Tax='$tax',Discount=0,Status='Active',Date=curdate(),Time=curtime(),ID_admin_users='$in{'id_admin_users'}'");
				}else{
					#&cgierr("$i:fdfdfd".$in{'id_products1'});
				}
			}
			#Inserta los payments
			if($in{'type'}eq'Credit-Card'){
				$sth=&Do_SQL("Insert into sl_orders_payments set ID_orders='$lastid_ord',Type='$in{'type'}',PmtField1='$in{'pmtfield1'}',PmtField2='".$in{'firstname'}.' '.$in{'lastname1'}.' '.$in{'lastname2'}."',Pmtfield3='$in{'pmtfield3'}',PmtField4='$in{'pmtfield4'}',PmtField5='$in{'pmtfield5'}',PmtField6='$in{'pmtfield6'}',PmtField7='CreditCard',Amount='$in{'amount'}',Reason='Sale',Paymentdate=curdate(),Status='Approved',Date=curdate(),Time=curtime(),ID_admin_users='$usr{'id_admin_users'}'");
			}
			elsif($in{'type'} =~ /PayPal|Google|Amazon/){
				$sth=&Do_SQL("Insert into sl_orders_payments set ID_orders='$lastid_ord',Type='Credit-Card',PmtField1='Visa',PmtField2='".$in{'firstname'}.' '.$in{'lastname1'}.' '.$in{'lastname2'}."',Pmtfield3='$in{'type'}',Amount='$in{'amount'}',Reason='Sale',Paymentdate=curdate(),AuthCode='$in{'authcode'}',Captured='Yes',CapDate=CURDATE(),Status='Approved',Date=curdate(),Time=curtime(),ID_admin_users='$in{'id_admin_users'}'");
			}elsif($in{'type'}eq'COD'){
				$sth=&Do_SQL("Insert into sl_orders_payments set ID_orders='$lastid_ord',Type='COD',PmtField1='$in{'pmtfield1'}',PmtField2='".$in{'firstname'}.' '.$in{'lastname1'}.' '.$in{'lastname2'}."',Pmtfield3='',Amount='$in{'amount'}',Reason='Sale',Paymentdate=curdate(),Status='Approved',Date=curdate(),Time=curtime(),ID_admin_users='$in{'id_admin_users'}'");
			}
			$lastid_payment = $sth->{'mysql_insertid'};


			if($in{'type'} !~ /Credit-Card/){

				$status='OK';
				
				## Movimientos Contables
				my ($order_type, $ctype, $ptype,@params);
				my ($sth) = &Do_SQL("SELECT Ptype, Type FROM sl_orders INNER JOIN sl_customers USING(ID_customers) WHERE ID_orders = '$lastid_ord';");
				($order_type, $ctype) = $sth->fetchrow();
				$ptype = get_deposit_type($lastid_payment,'');
				@params = ($lastid_ord,$lastid_payment, 1);
				&accounting_keypoints('order_deposit_'. $ctype .'_'. $order_type .'_'. $ptype, \@params );

			}else{

				if(!$va{'from_run_daily'} == 1){
					require ("../../common/apps/cybersubs.cgi");
				}
				($status,$statmsg,$codemsg) = &sltvcyb_auth($lastid_ord,$lastid_payment);
			}


			if($status =~ /ok/i){
				$va{'message'}= &trans_txt('payments_authorized');
			}else{
				$va{'message'}= $statmsg;
			}

			$script_url =~ s/admin$/dbman/;
			$va{'message'}= &trans_txt('orders_added') . ": ID <a href=\"$script_url?cmd=orders&view=$lastid_ord\">$lastid_ord</a>, Customer ID <a href=\"$script_url?cmd=opr_customers&view=$lastid_cus\">$lastid_cus</a><br>$va{'message'}";
			foreach my $key (keys %in){
				delete($in{$key});
			}
			$in{'cmd'}='eco_orders';

			if($va{'from_run_daily'} == 1){
				return $lastid_ord;
			}


		}else{
			if($va{'from_run_daily'} == 1){
				return -1;
			}
			#&cgierr("Errors:$err,$x,$#error");
		}
	}
	print "Content-type: text/html\n\n";
	print &build_page('eco_orders.html');

}

sub validate_eco_orders{
# --------------------------------------------------------
# Forms Involved:
# Created on: 25 Aug 2010 18:32:09
# Author: MCC C. Gabriel Varela S.
# Description :
# Parameters :

	my $err=0;

	$in{'id_products1'} = '100'.$in{'id_products1'} if length($in{'id_products1'})==6;
	$in{'id_products2'} = '100'.$in{'id_products2'} if length($in{'id_products2'})==6;
	$in{'id_products3'} = '100'.$in{'id_products3'} if length($in{'id_products3'})==6;
	$in{'id_products4'} = '100'.$in{'id_products4'} if length($in{'id_products4'})==6;
	$in{'id_products5'} = '100'.$in{'id_products5'} if length($in{'id_products5'})==6;
	$in{'id_products6'} = '100'.$in{'id_products6'} if length($in{'id_products6'})==6;

	$in{'pmtfield4'}=$in{'expdate'};
	$in{'pmtfield2'}=$in{'firstname'}.' '.$in{'lastname1'}.' '.$in{'lastname2'};
	if (!$in{'address1'}){
		$error{'address1'} = &trans_txt('required');
		++$err;
	}
	if (!$in{'city'}){
		$error{'city'} = &trans_txt('required');
		++$err;
	}
	if (!$in{'state'}){
		$error{'state'} = &trans_txt('required');
		++$err;
	}
	if (!$in{'zip'}){
		$error{'zip'} = &trans_txt('required');
		++$err;
	}
	if (!$in{'email'}){
		#$error{'email'} = &trans_txt('required');
		#++$err;
	}
	if (!$in{'id_products1'}){
		$error{'id_products1'} = &trans_txt('required');
		++$err;
	}
	if (!$in{'sprice1'}){
		$error{'sprice1'} = &trans_txt('required');
		++$err;
	}
	if ($in{'shipping1'}eq''){
		$error{'shipping1'} = &trans_txt('required');
		++$err;
	}
	if ($in{'type'}eq''){
		$error{'type'} = &trans_txt('required');
		++$err;
	}
	if ($in{'pmtfield1'}eq'' and $in{'type'}eq'Credit-Card'){
		$error{'pmtfield1'} = &trans_txt('required');
		++$err;
	}
	if ($in{'pmtfield2'}eq''){
		$error{'pmtfield2'} = &trans_txt('required');
		++$err;
	}
	if ($in{'pmtfield3'}eq'' and $in{'type'}eq'Credit-Card'){
		$error{'pmtfield3'} = &trans_txt('required');
		++$err;
	}
	if ($in{'type'}eq'Credit-Card' and !$in{'expdate'}){
		$error{'pmtfield4'} = &trans_txt('required');
		++$err;
	}
	if ($in{'type'}eq'Credit-Card' and !$in{'pmtfield5'}){
		$error{'pmtfield5'} = &trans_txt('required');
		++$err;
	}
	if (!$in{'amount'}){
		$error{'amount'} = &trans_txt('required');
		++$err;
	}

	if($in{'id_products1'} and length($in{'id_products1'})<9){
		$error{'id_products1'} = &trans_txt('invalid');
		++$err;
	}
	if($in{'id_products2'} and length($in{'id_products2'})<9){
		$error{'id_products2'} = &trans_txt('invalid');
		++$err;
	}
	if($in{'id_products5'} and length($in{'id_products5'})<9){
		$error{'id_products5'} = &trans_txt('invalid');
		++$err;
	}
	if($in{'id_products3'} and length($in{'id_products3'})<9){
		$error{'id_products3'} = &trans_txt('invalid');
		++$err;
	}
	if($in{'id_products4'} and length($in{'id_products4'})<9){
		$error{'id_products4'} = &trans_txt('invalid');
		++$err;
	}

	if($in{'id_products2'} and $in{'sprice2'}eq''){
		$error{'sprice2'} = &trans_txt('required');
		++$err;
	}
	if($in{'id_products2'} and $in{'shipping2'}eq''){
		$error{'shipping2'} = &trans_txt('required');
		++$err;
	}
	if($in{'id_products3'} and $in{'sprice3'}eq''){
		$error{'sprice3'} = &trans_txt('required');
		++$err;
	}
	if($in{'id_products3'} and $in{'shipping3'}eq''){
		$error{'shipping3'} = &trans_txt('required');
		++$err;
	}
	if($in{'id_products4'} and $in{'sprice4'}eq''){
		$error{'sprice4'} = &trans_txt('required');
		++$err;
	}
	if($in{'id_products4'} and $in{'shipping4'}eq''){
		$error{'shipping4'} = &trans_txt('required');
		++$err;
	}
	if($in{'id_products5'} and $in{'sprice5'}eq''){
		$error{'sprice5'} = &trans_txt('required');
		++$err;
	}
	if($in{'id_products5'} and $in{'shipping5'}eq''){
		$error{'shipping5'} = &trans_txt('required');
		++$err;
	}
	if($in{'id_products6'} and $in{'sprice6'}eq''){
		$error{'sprice6'} = &trans_txt('required');
		++$err;
	}
	if($in{'id_products6'} and $in{'shipping6'}eq''){
		$error{'shipping6'} = &trans_txt('required');
		++$err;
	}

	return $err;
}

###################################################################################
###################################################################################
#	Function: leads_flash
#   	Build list of Lead Flash to be assigned.
#
#	Created by: _Roberto Barcenas_
#
#	Modified By:
#
#   Parameters:
#		date_from: Date From
#		date_to: Date To	
#
#   Returns:
#
#   See Also: None
#
sub leads_flash {
####################################################################################
####################################################################################


	$usr{'pref_maxh'} = 50;
	my ($start_date) = $in{'from_date'} ? &filter_values($in{'from_date'}) : '2012-08-01';
	my ($stop_date) = $in{'to_date'} ? &filter_values($in{'to_date'}) : &get_sql_date();

	my $query .= " Date>='$start_date' AND Date<='$stop_date' ";

	if(int($in{'id_admin_users'}) >= 0){
		$query .= " AND ID_admin_users = '". int($in{'id_admin_users'}) ."' "; 
	}

	
	### Check Permissions

	$va{'inbound_agents'}='';
	$sth=&Do_SQL("SELECT ID_admin_users,CONCAT(FirstName,' ',LastName)AS Name FROM admin_users WHERE application='cc-inbound' AND Status='Active' AND user_type NOT IN('Internet','LA','Recompras') ORDER BY CONCAT(FirstName,' ',LastName)");
	while($rec=$sth->fetchrow_hashref){
		$va{'inbound_agents'} .= ",'$rec->{'ID_admin_users'}':'$rec->{'ID_admin_users'} -- $rec->{'Name'}'";
	}

	my ($sth)=&Do_SQL("SELECT COUNT(*) FROM sl_leads_flash WHERE $query;");
	$va{'matches'} = $sth->fetchrow();
	if ($va{'matches'}>0){
		($va{'pageslist'},$qs) = &pages_list($in{'nh'},"/cgi-bin/mod/$usr{'application'}/admin",$va{'matches'},$usr{'pref_maxh'});
		$va{'matches'} = &format_number($va{'matches'});
		my (@c) = split(/,/,$cfg{'srcolors'});
		(!$in{'nh'}) and ($in{'nh'}=1);
		my ($first) = ($in{'nh'} - 1) * $usr{'pref_maxh'};
		my ($rec);
		my ($sth) = &Do_SQL("SELECT * FROM sl_leads_flash WHERE $query ORDER BY Date DESC LIMIT $first,$usr{'pref_maxh'};");
		while($rec = $sth->fetchrow_hashref()){

			my $agent_name = !$rec->{'ID_admin_users'} ? 0 : &load_db_names('admin_users','ID_admin_users',$rec->{'ID_admin_users'},'[FirstName] [LastName]');
			if(!$agent_name or $va{'inbound_agents'} !~ /$agent_name/ ){
				$agent_name = 'Not Assigned';
			}else{
				#&cgierr("$va{'inbound_agents'} !~ /$agent_name/");
			}

			$d = 1 - $d;
			$va{'searchresults'} .= qq|
						<tr bgcolor='$c[$d]'>
							<td class='smalltext' valign='top'>$rec->{'ID_leads'}</td>
							<td class='smalltext' valign='top'>$rec->{'Name'}</td>
							<td class='smalltext' valign='top'>$rec->{'Contact_time'}</td>
							<td class='smalltext' valign='top'>$rec->{'Products'}</td>
							<td class='smalltext' valign='top'>$rec->{'Status'}</td>
							<td class='smalltext' valign='top'>$rec->{'Date'}<br>$rec->{'Time'}</td>
							<td class='smalltext' valign='top'><div class="field_editable" id="$rec->{'ID_leads_flash'}">$agent_name</div></td>
						</tr>\n|;
		}
	}

	print "Content-type: text/html\n\n";
	print &build_page('leads_flash_assign.html');    
}


sub websites_chat{
# --------------------------------------------------------
# Forms Involved: 
# Created on: 07 December 2010
# Author: Roberto Barcenas.
# Description :   
# Parameters :


	$va{'algafit'} = &trans_txt('search_nomatches');
	$va{'charakani'} = &trans_txt('search_nomatches');
	$va{'chardon'} = &trans_txt('search_nomatches');
	$va{'colageina'} = &trans_txt('search_nomatches');
	$va{'diabestevia'} = &trans_txt('search_nomatches');
	$va{'innovashop'} = &trans_txt('search_nomatches');
	$va{'moinsage'} = &trans_txt('search_nomatches');
	$va{'rejuvital'} = &trans_txt('search_nomatches');
	$va{'allnatpro'} = &trans_txt('search_nomatches');
	$va{'prostaliv'} = &trans_txt('search_nomatches');
	$va{'naturaliv'} = &trans_txt('search_nomatches');
	$va{'keraorganiq'} = &trans_txt('search_nomatches');
	$va{'singivitis'} = &trans_txt('search_nomatches');
	$va{'fibraagavera'} = &trans_txt('search_nomatches');
	$va{'buyspineflex'} = &trans_txt('search_nomatches');

	my $sth=&Do_SQL("SELECT * FROM chat_admin_users WHERE ID_admin_users = '$usr{'id_admin_users'}';");
	my($total) = $sth->rows();

	if($total > 0){
		while(my($id_chat,$id_admin_users,$username,$passwd,$website,$urlwebsite) = $sth->fetchrow()){
			$urlwebsite .= 'login_direksys.php';
			$va{$website} = qq|<iframe src="$urlwebsite?password=|. &filter_values($passwd) .qq|&login=$username&" id='rcmd_$website' name='$website' title='$website' width='800' height='200' frameborder='0' marginwidth='0' marginheight='0' scrolling='auto'>
				<h2>Unable to do the script</h2>
				<h3>Please update your Browser</h3>
				</iframe>|;	
		}
	}


	print "Content-type: text/html\n\n";
	print &build_page('websites_chat.html');

}

sub control_panel {
# --------------------------------------------------------
	my (%agents,$totlines,$idx,$more_info,$ag_name,$having);
	($va{'cellall'},$va{'cellincall'},$va{'cellidle'},$va{'cellperms'})= ('off','off','off','off');
	if ($in{'status'} eq 'in_call'){
		$having = 'Having qty>1';
		$va{'cellincall'} = 'on';
	}elsif($in{'status'} eq 'idle'){
		$having = 'Having qty=1';
		$va{'cellidle'} = 'on';
	}elsif($in{'status'} eq 'perms'){
		$va{'cellperms'} = 'on';
	}else{
		$va{'cellall'} = 'on';
	}
	my $sth=&Do_SQL("SELECT t.*, COUNT(*) AS qty,MIN(LoggedTime) AS lmin, MAX(LoggedTime) AS lmax FROM (
				SELECT CreatedBy, CreatedDateTime, ses, 
				TIMESTAMPDIFF(MINUTE,CreatedDateTime,NOW()) AS LoggedTime
				FROM `admin_sessions` WHERE InModule='Sales'  ORDER BY ID_admin_sessions ASC) t 
				GROUP BY t.CreatedBy $having");
	while($rec = $sth->fetchrow_hashref()){
		++$agents{'agents'};
		$agents{$agents{'agents'}} = $rec->{'CreatedBy'};
		$agents{$agents{'agents'}.'_qty'} = $rec->{'qty'};
		$agents{$agents{'agents'}.'_min'} = $rec->{'LoggedTime'};
		$agents{$agents{'agents'}.'_ses'} = $rec->{'ses'};
		if($rec->{'qty'}>1){
			$agents{$agents{'agents'}.'_call'} = $rec->{'lmin'};
		}
		
	}
	$va{'searchresult'} = '';
	$va{'perms_calls_tab'} = '';

	if (&check_permissions('call_phone_perms_management','','')) {
		$va{'perms_calls_tab'} = '<td width="23%" class="cell_[va_cellperms]" align="center" onClick=\'trjump("/cgi-bin/mod/crm/admin?cmd=control_panel&status=perms")\'>Perms</td>';
	}
	if ($in{'status'} eq 'perms') {
		my $query = "SELECT DISTINCT admin_users.ID_admin_users,
				CONCAT(CONCAT_WS(' ',admin_users.FirstName, admin_users.LastName, admin_users.LastName),' (', admin_users.Username,')') name,
				admin_users_perms.Type
				FROM admin_users_perms
				INNER JOIN admin_users ON admin_users.ID_admin_users = admin_users_perms.ID_admin_users
					AND admin_users.Status = 'Active'
				INNER JOIN admin_users_groups ON admin_users_groups.ID_admin_users = admin_users.ID_admin_users
					#AND admin_users_groups.ID_admin_groups = 3
				INNER JOIN admin_groups ON admin_groups.ID_admin_groups = admin_users_groups.ID_admin_groups
				WHERE 1
				AND admin_users_perms.command = 'phone_button'
				AND admin_users.application = 'sales'
				ORDER BY admin_users.firstname
				;";
		my $sth = &Do_SQL($query);
		$va{'searchresult'} .= qq|<tr>\n<td class="menu_bar_title" width="2%"></td>\n|;
		$va{'searchresult'} .= qq|<td colspan=5 align="center" class="smalltxt"><table border=0><tr><td><table border=0>|;
		while ($rec = $sth->fetchrow_hashref()) {
			my $color = 'black';
			if ($rec->{'Type'} eq 'Allow') {
				$color = 'green';
			} else {
				$color = 'red';
			}
			$va{'searchresult'} .= '<tr><td>('.$rec->{'ID_admin_users'}.')';
			$va{'searchresult'} .= ' '.$rec->{'name'};
			$va{'searchresult'} .= ' </td><td style="color:'.$color.';">'.$rec->{'Type'}.'</tr>';
		}
		$va{'searchresult'} .= '</table>';
		$va{'searchresult'} .= qq|<br></td></tr><tr><td><textarea id="text_perms_calls" rows="4" cols="50" placeholder="ID users separated by commas, example: 12345, 6789, 0123"></textarea>
			Allow <input type="radio" name="input_perms_call" value="Allow" />
			Disallow <input type="radio" name="input_perms_call" value="Disallow" />
			<br>
			<br>
			<br>
			<center>
			<input type="button" id="apply_perms_calls" value="Apply" class="button">
			<img src="$va{'imgurl'}/$usr{'pref_style'}/loading.gif" id="img_perms_calls" style="display:none" />
			</center>
		</td></tr></table></td>\n|;
		$va{'searchresult'} .= qq|<td class="menu_bar_title" width="2%"></td>\n</tr>\n|;

		print "Content-type: text/html\n\n";
		print &build_page('perms_phone_call.html');
	} else {
		## Lines
		$totlines = int($agents{'agents'}/5)+1;

		
		for my $x (1..$totlines){
			$va{'searchresult'} .= qq|<tr>\n		    <td class="menu_bar_title" width="2%"></td>\n|;
			for my $i (0..4){
				$idx = ($x-1)*5+$i+1;
				if ($agents{$idx}){
					$ag_name   = "(". $agents{$idx}.") ".&load_db_names('admin_users','ID_admin_users',$agents{$idx},'[FirstName] [LastName]');
					$more_info = "Logged: ".&format_number($agents{$idx.'_min'}) . "Mins<br>";
					if ($agents{$idx.'_call'}){
						$more_info .= &ses_moreinfo($agents{$idx.'_ses'});
						$va{'searchresult'} .= qq|<td align="center" class="smalltxt"><img src="$va{'imgurl'}/$usr{'pref_style'}/b_face_incall.jpg" title='Agent' alt='Agent' border='0'><br>
							$ag_name
							<a href="#" class="info"><img src="$va{'imgurl'}/$usr{'pref_style'}/ichelpsmall.gif" title='More Info' alt='More Info' border='0'>
								<span>$more_info</span>
							</a>
							</td>\n|;	
					}else{
						$va{'searchresult'} .= qq|<td align="center" class="smalltxt"><img src="$va{'imgurl'}/$usr{'pref_style'}/b_face_inactive.jpg" title='Agent' alt='Agent' border='0'><br>
						$ag_name
							<a href="#" class="info"><img src="$va{'imgurl'}/$usr{'pref_style'}/ichelpsmall.gif" title='More Info' alt='More Info' border='0'>
								<span>$more_info</span>
							</a></td>\n|;	
					}
				}else{
					$va{'searchresult'} .= qq|<td align="center">&nbsp;</td>\n|;
				}
			}
			$va{'searchresult'} .= qq|<td class="menu_bar_title" width="2%"></td>\n		 </tr>\n|;
		}
		if (!$agents{'agents'}){
			$va{'message'} = &trans_txt('ses_empty');
		}
		print "Content-type: text/html\n\n";
		print &build_page('control_panel.html');	
	}

	
}

sub ses_moreinfo{
# --------------------------------------------------------
	my ($ses) = @_;
	my (%tmp);
	my ($out_msg)= &trans_txt('ses_info');
	my (@ary) = split(/\n/, &load_name('admin_sessions','ses','call'.$ses,'Content'));
	if ($#ary>0){
		for (0..$#ary){
			my ($name,$value) = split(/=/, $ary[$_]);
			$tmp{$name}= $value;
			if ($ary[$_] =~ /step(\d+)_time/){
				$tmp{'curstep'} = $1 if($tmp{'last_step'} < $1);
			}
		}
		$tmp{'tottime'} = int(($tmp{'step'.$tmp{'curstep'}.'_time'}-$tmp{'start_sec'})/60);
		foreach my $key (keys %tmp){
			$out_msg =~ s/\[$key\]/$tmp{$key}/gi;
		}
		return $out_msg;
	}else{
		return;
	}
	
#advbar=1
#cid=3453456345
#did=1
#id_customers=0
#id_dids=1
#id_salesorigins=1
#id_speech=
#items_in_basket=0
#prodfam=
#sameshipping=same
#start_sec=63018
#step0_time=63032
#step1_time=63025
#step2_time=63041
}

sub opr_wizard_crmtickets{

	print "Content-type: text/html\n\n";
	print &build_page('opr_wizard_crmtickets.html');

}




sub send_mail_template
{
	# --------------------------------------------------------
	# Forms Involved: 
	# Created on: 04 Octubre 2010
	# Author: Huitzilihuitl Ceja.
	# Description :   
	# Parameters :


	print "Content-type: text/html\n\n";


	use LWP::UserAgent;
	my $ua = LWP::UserAgent->new;
	my $response = $ua->get(
								$cfg{'api_url'}.'mailtemplate/list',
								'Content-Type' => 'application/x-www-form-urlencoded',
								'Authorization' => $cfg{'api_direksys_key'}
							);

	#'Content' => 'to='.$in{'to_number'}.'&msg='.$in{'to_message'}
	
	$va{'company'} =$cfg{'dbi_db'};
	$va{'select_template'} = '<select id="template" name="template" style="background-color: rgb(255, 255, 255); cursor: pointer;" class="input">';
	$va{'select_template'} .= '<option value="">----</option>';


	my @templates = split /,/, $response->content; 

	foreach $name (@templates)
	{
		$va{'select_template'} .= '<option value="'.$name.'">'.$name.'</option>';
	}
	$va{'select_template'} .=	'</select>';


	my $err = 0;

	if( $in{'action'} )
	{

		if( !$in{'to_mails'} ){
			$va{'message'}  = &trans_txt('reqfields');
			$error{'to_mails'} = &trans_txt('required');
			$err++;
		}

		if( !$in{'template'} )
		{
			$va{'message'}  = &trans_txt('reqfields');
			$error{'template'} = &trans_txt('required');
			$err++;
		}

		if( !$in{'subject'} )
		{
			$va{'message'}  = &trans_txt('reqfields');
			$error{'subject'} = &trans_txt('required');
			$err++;
		}

		if(!$err)
		{
			use LWP::UserAgent;
			
			my $ua = LWP::UserAgent->new;
			my $response = $ua->post(
										$cfg{'api_url'}.'mailtemplate/send/'.$in{'template'},
										'Content-Type' => 'application/x-www-form-urlencoded',
										'Authorization' => $cfg{'api_direksys_key'},
										'Content' => 'company='.$in{'company'}.'&emails='.$in{'to_mails'}.'&subject='.$in{'subject'}.'&fecha='.$in{'date'}.'&textA='.$in{'texta'}.'&textB='.$in{'textb'}.'&textC='.$in{'textc'}
									);

			$in{'to_mails'} = $response->content; 

		}
	}



	print &build_page('send_mail.html');

}



1;
