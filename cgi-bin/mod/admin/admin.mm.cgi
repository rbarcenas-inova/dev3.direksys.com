#!/usr/bin/perl
##########################################################
##			 ADMIN PAGES :MEDIA & PLANNING TOOLS	##
##########################################################



#	Function: mm_did0
#
#   	Build a list of orders without ID_mediacontracts assigned.
#
#
#	Created by: _Carlos Haas_
#
#	Modified By:
#
#		Roberto Barcenas on 01/03/2012: Added option to filter by Dates
#		Roberto Barcenas on 03/22/2012: Includes orders without DNIS / DIDS7
#
#   	Parameters:
#
#		None
#
#   	Returns:
#
#      	Build a variable with the list of orders paginated
#
#   	See Also:
#
#      None

sub mm_did0 {
# --------------------------------------------------------
	my ($start_date) = $in{'from_date'} ? &filter_values($in{'from_date'}) : '2011-01-01';
	my ($stop_date) = $in{'to_date'} ? &filter_values($in{'to_date'}) : &get_sql_date();

	my ($sth)=&Do_SQL("SELECT COUNT(*) FROM sl_orders LEFT JOIN sl_customers ON sl_orders.ID_customers=sl_customers.ID_customers WHERE DIDS7='0' AND ID_mediacontracts=0 /*AND sl_customers.Type='Retail'*/ AND sl_orders.Date>='$start_date' AND sl_orders.Date<='$stop_date' AND sl_orders.Status NOT IN ('System Error','Void');");
	$va{'matches'} = $sth->fetchrow();
	if ($va{'matches'}>0){
		($va{'pageslist'},$qs) = &pages_list($in{'nh'},"/cgi-bin/mod/$usr{'application'}/admin",$va{'matches'},$usr{'pref_maxh'});
		$va{'matches'} = &format_number($va{'matches'});
		my (@c) = split(/,/,$cfg{'srcolors'});
		(!$in{'nh'}) and ($in{'nh'}=1);
		my ($first) = ($in{'nh'} - 1) * $usr{'pref_maxh'};
		my ($rec,$tmp,$products,$phones);
		my ($sth) = &Do_SQL("SELECT sl_customers.*,sl_orders.* FROM sl_orders LEFT JOIN sl_customers ON sl_orders.ID_customers=sl_customers.ID_customers WHERE DIDS7='0' AND ID_mediacontracts=0 /*AND sl_customers.Type='Retail'*/  AND sl_orders.Date>='$start_date' AND sl_orders.Date<='$stop_date' AND sl_orders.Status NOT IN ('System Error','Void') ORDER BY sl_orders.Date DESC LIMIT $first,$usr{'pref_maxh'};");
		while($rec = $sth->fetchrow_hashref()){
			my ($sth2) = &Do_SQL("SELECT Name FROM sl_orders_products LEFT JOIN sl_products ON sl_products.ID_products=RIGHT(sl_orders_products.ID_products,6) WHERE ID_orders=$rec->{'ID_orders'} GROUP BY Name;");	
			$products  = ''; $phones = '';
			while($tmp = $sth2->fetchrow_hashref()){
				($products) and ($products .= "<br>");
				$products .= $tmp->{'Name'};
			}
			($phones,$arecodes) = &get_areacodes(substr($rec->{'CID'},0,3),substr($rec->{'Phone1'},0,3),substr($rec->{'Phone2'},0,3),substr($rec->{'Cellphone'},0,3));
			$va{'searchresults'} .= qq|
						<tr bgcolor='$c[$d]'>
							<td class='smalltext' valign='top'><a href="/cgi-bin/mod/admin/dbman?cmd=opr_orders&view=$rec->{'ID_orders'}">$rec->{'ID_orders'}</a></td>
							<td class='smalltext' valign='top'>$rec->{'FirstName'} $rec->{'LastName1'}<br>
									$rec->{'City'},$rec->{'State'}</td>
							<td class='smalltext' valign='top'>$phones</td>
							<td class='smalltext' valign='top'>$rec->{'Date'}<br>$rec->{'Time'}</td>
							<td class='smalltext' valign='top'>$products</td>
							<td class='smalltext' valign='top'>
							<div id="assign_$rec->{'ID_orders'}">
								<a href="#assign_$rec->{'ID_orders'}" class="scroll" onClick="popup_show('ajax_windows', 'ajax_drag', 'ajax_exit', 'element-right', -600, -1,'assign_$rec->{'ID_orders'}');loadDoc('/cgi-bin/common/apps/ajaxbuild?ajaxbuild=assign_did&id_orders=$rec->{'ID_orders'}&date=$rec->{'Date'}&time=$rec->{'Time'}&areacode=$arecodes&zip=$rec->{'Zip'}&state=| . &urlencode($rec->{'State'}) . qq|&products=| . &urlencode($products) . qq|');">
									<button type="button">Assign</button>	
								</a>
							</div></td>
						</tr>\n|;						
		}
	}
	
	print "Content-type: text/html\n\n";
	print &build_page('mm_did0.html');    
}

sub get_areacodes {
# --------------------------------------------------------
	my (@nums)=@_;
	my ($phones, $arecodes);
	for my $i(0..$#nums){
		if ($nums[$i]>0 and $arecodes !~ /$nums[$i]/){
			$phones .= "($nums[$i]) ". &load_db_names('sl_zipcodes','AreaCode',$nums[$i],'[City],[State]')."<br>";
			$arecodes .= $nums[$i];
		}
		
	}
	return ( $phones, $arecodes);
#		$phones .= "(".substr($rec->{'CID'},0,3) . ") ". &load_db_names('sl_zipcodes','AreaCode',substr($rec->{'CID'},0,3),'[City],[State]') if ($rec->{'CID'});
#		($phones) and ($phones .= "<br>");
#		$phones .= "(".substr($rec->{'Phone1'},0,3) . ") ". &load_db_names('sl_zipcodes','AreaCode',substr($rec->{'Phone1'},0,3),'[City],[State]') if (substr($rec->{'Phone1'},0,3) and substr($rec->{'Phone1'},0,3) ne substr($rec->{'CID'},0,3));
#		($phones) and ($phones .= "<br>");
#		$phones .= "(".substr($rec->{'Phone2'},0,3) . ") ". &load_db_names('sl_zipcodes','AreaCode',substr($rec->{'Phone2'},0,3),'[City],[State]') if (substr($rec->{'Phone2'},0,3) and substr($rec->{'Phone2'},0,3) ne substr($rec->{'Phone1'},0,3));
#		($phones) and ($phones .= "<br>");
#		$phones .= "(".substr($rec->{'Cellphone'},0,3) . ") ". &load_db_names('sl_zipcodes','AreaCode',substr($rec->{'Cellphone'},0,3),'[City],[State]') if (substr($rec->{'Cellphone'},0,3) and substr($rec->{'Cellphone'},0,3) ne substr($rec->{'Phone2'},0,3)  and substr($rec->{'Cellphone'},0,3) ne substr($rec->{'Phone1'},0,3));
#		$phones =~ s/<br><br>/<br>/g;
}


################################################
############### Notas ##########################
################################################
#
# DONE   1) Dividir Formato USA en 2 : Formato USA y Formato GTS  DONE
# DONE   2) Tabs a Contracts
# 3) Al editar un contrato desasignar las ordenes de ese contrato y volver a asignarlas
# DONE   4) Editar sl_contracts con el producto DONE
# DONE   5) Agregar Producto al Menu de asignacion de DID DONE
# DONE 6) Edicion de Contratos en Excel, que no borre lo hecho en Direksys
# 7) Cambiar el status de un contrato al momento de asignar las ordenes
# DONE  8) Revisar que no se borre el ID_contracts de la orden al editarla





sub mm_uploadcode {
# --------------------------------------------------------
# Created :  Carlos Haas 01/01/2007 6:47:28 PM
# Last Update : 
# Locked by : 
# Description :
#
#

	print "Content-type: text/html\n\n";
	my ($err);
	
	if ($in{'action'}){
			$num=int(rand 1000000000);
			$cad=sprintf ("%.04d",$num);
			$va{'authnumr'}=$cad;
			#insert sl_vars SET VNAME="Auth Order",VValue=$id_order,$id_user,$num
			my ($sth)=&Do_SQL("SELECT COUNT(*) FROM sl_vars WHERE VName='Auth Upload'");
			if ($sth->fetchrow() >0){
				my ($sth)=&Do_SQL("UPDATE sl_vars SET VValue='$cad', Subcode='$usr{'id_admin_users'}.".&get_sql_date()."'  WHERE VName='Auth Upload'");
				&auth_logging('var_updated',$in{'id_orders'});
			}else{
				my ($sth)=&Do_SQL("INSERT INTO sl_vars SET VName='Auth Upload',VValue='$cad', Subcode='$usr{'id_admin_users'}.".&get_sql_date()."'");
				&auth_logging('var_added',$sth->{'mysql_insertid'});
			}
	}

	print &build_page('mm_uploadcode.html');    
}


#	Function: mm_datax
#
#   	Generates a file with contracts data for media analysis
#   	Note: Files over NFS directory in S3
#
#	Created by: _Carlos Haas_
#
#	Modified By:
#
#		Roberto Barcenas on 03/21/2012: Files path changes to "files/files_s3/dataexchange" (NFS)
#
#   	Parameters:
#
#		action: Indicates to execute an action
#		from_date: Starting Date
#		to_date: Ending Date
#		dn: Download Report
#		del: Delete Report
#
#   	Returns:
#
#      	1) If action+from_date+to_date : Creates a sl_cron_scripts record to execute a file creation by S3 cron
#		2) If dn: Downloads the specified file
#		3) If del: Deletes the specified file
#		In all cases build a list of files already created 
#
#   	See Also:
#
#      None
sub mm_datax {
# --------------------------------------------------------

	delete($in{'fromdate'}) if (!&valid_date_sql($in{'fromdate'}));
	delete($in{'todate'}) if (!&valid_date_sql($in{'todate'}));
	$in{'del'} = int($in{'del'});
	$in{'dn'} = int($in{'dn'});
	my ($err);
	if ($in{'action'} and $in{'fromdate'} and $in{'todate'} and $in{'ftype'}){
			#($from_mail,$to_mail,$subject_mail,$body_mail)
			#send_text_mail('chaas@inovaus.com','7862004423@txt.att.net','Email test','SMS');
			#send_text_mail('chaas@inovaus.com','chaas@inovaus.com','Email test','SMS');
			my ($sth) = &Do_SQL("INSERT INTO sl_mediacontracts_logs SET FromDate='$in{'fromdate'}',Ftype='$in{'ftype'}', ToDate='$in{'todate'}', Status='New', Date=CURDATE(),Time=CURTIME(),ID_admin_users='$usr{'id_admin_users'}'");
			my ($sth) = &Do_SQL("INSERT INTO sl_cron_scripts SET script='create_dataexchange', Server='s11', type='function', scheduledate=CURDATE(),scheduletime=CURTIME(),Status='Active'");
			$va{'message'} = 'Process Scheduled';

	}elsif($in{'action'}){
		(!$in{'fromdate'}) and ($error{'fromdate'} = &trans_txt('required'));
		(!$in{'todate'}) and ($error{'todate'} = &trans_txt('required'));
		(!$in{'ftype'}) and ($error{'ftype'} = &trans_txt('required'));
		$va{'message'} = &trans_txt('reqfields');
	}elsif($in{'dn'}>0){
		#print "Content-type: text/html\n\n";
		print "Content-type: application/octetstream\n";
		print "Content-disposition: attachment; filename=".&load_db_names('sl_mediacontracts_logs','ID_mediacontracts_logs',$in{'dn'},'dataexchange_[fromdate]_to_[todate]').".xls\n\n";
		if (open(XLS, "<$cfg{'path_upfiles'}/files_s3/dataexchange/$in{'dn'}.xls")){
			print <XLS>;
			close XLS;
		}
		return;
	}elsif($in{'del'}>0){
		my ($sth) = &Do_SQL("UPDATE sl_mediacontracts_logs SET Status='Deleted' WHERE ID_mediacontracts_logs=$in{'del'}");
		unlink("$cfg{'path_upfiles'}/files_s3/dataexchange/$in{'del'}.xls");
		$va{'message'} ="File Deleted";
	}
	my ($n) = 1;
	my ($sth) = &Do_SQL("SELECT * FROM sl_mediacontracts_logs ORDER BY ID_mediacontracts_logs DESC");
	my ($total)=$sth->rows();
	while ($rec = $sth->fetchrow_hashref() ) {
		($n==1) and ($va{'reports'} .= "<tr>");
		$info = "  $rec->{'FromDate'} -> $rec->{'ToDate'}<br>".&load_db_names('admin_users','ID_admin_users',$rec->{'ID_admin_users'},'[FirstName] [LastName]').' @ '. $rec->{'Date'}.' '.$rec->{'Time'} . " # ".$rec->{'FType'} ;
		if ($rec->{'Status'} eq 'Finished'){
			++$n;
			if (-e "$cfg{'path_upfiles'}/files_s3/dataexchange/$rec->{'ID_mediacontracts_logs'}.xls"){
				$va{'reports'} .= "<td class='smalltxt' align='center'><a href='/cgi-bin/mod/admin/admin?cmd=mm_datax&del=$rec->{'ID_mediacontracts_logs'}'><img src='$va{'imgurl'}/$usr{'pref_style'}/b_drop.png'></a> 
						<a href='/cgi-bin/mod/admin/admin?cmd=mm_datax&dn=$rec->{'ID_mediacontracts_logs'}'><img src='$va{'imgurl'}/$usr{'pref_style'}/b_xls.gif'></a>$info</td>";
			}else{
				$va{'reports'} .= "<td class='smalltxt' align='center'><a href='/cgi-bin/mod/admin/admin?cmd=mm_datax&del=$rec->{'ID_mediacontracts_logs'}'><img src='$va{'imgurl'}/$usr{'pref_style'}/b_drop.png'></a> $info</td>";
			}
		}elsif($rec->{'Status'} eq 'InProcess'){
			++$n;
			$va{'reports'} .= "<td class='smalltxt' align='center'><img src='$va{'imgurl'}/$usr{'pref_style'}/loading.gif'> $info</td>";
		}elsif($rec->{'Status'} eq 'New'){
			++$n;
			$va{'reports'} .= "<td class='smalltxt' align='center'><a href='/cgi-bin/mod/admin/admin?cmd=mm_datax&del=$rec->{'ID_mediacontracts_logs'}'><img src='$va{'imgurl'}/$usr{'pref_style'}/b_drop.png'></a>
						<img src='$va{'imgurl'}/$usr{'pref_style'}/waiting.png'> $info</td>";
		}
		
		if ($n>4){
			$va{'reports'} .= "</tr>";
			$n=1;
		}
	}
	if ($total==0){
		$va{'reports'} = "<td class='smalltxt' align='center'>". &trans_txt('notmatch'). "</td>";
	}
	print "Content-type: text/html\n\n";
	print &build_page('mm_dataex.html');    
}


sub mm_callcenters_availability{
# --------------------------------------------------------
# Created :  Roberto Barcenas 10/26/2011 4:05:28 PM
# Last Update :
# Description : Muestra los horarios de cada callcenter, para su modificacion
#

	&connect_db_w($cfg{'dbi_db_pbx'},$cfg{'dbi_host_pbx'},$cfg{'dbi_user_pbx'},$cfg{'dbi_pw_pbx'});

	## Update Records
	if($in{'action'}){

		my $sub_action=$in{'sub_action'};
		my $sub_id=int($in{'sub_id'});

		if($sub_action eq 'slider-add'){
			## Add New Record
			if($sub_id){
				my ($tmp_sth)=&Do_SQL("SELECT Name,FromTime,ToTime,WD,Status FROM sl_callcenters WHERE ID_callcenter='$sub_id';");
				my( $tmp_name, $tmp_fromtime, $tmp_totime, $tmp_wd, $tmp_status ) = $tmp_sth->fetchrow_array();

				my ($sth)=&Do_SQL("INSERT INTO sl_callcenters VALUES( 0,'$tmp_name','$tmp_fromtime','$tmp_totime', '$tmp_wd', '$tmp_status', CURDATE(), Time=CURTIME(), '$usr{'id_admin_users'}' );",1);
				if($sth->rows() == 1){
					$new_id = $sth->{'mysql_insertid'};
					$in{'db'}='sl_callcenters';
					&auth_logging('schedule_added',$new_id,1);
					$va{'message'}="Done:New Record Added";
				}
			}
		}elsif($sub_action eq 'slider-drop'){
			## Drop Record
			if($sub_id){
				my ($sth)=&Do_SQL("DELETE FROM sl_callcenters WHERE ID_callcenter='$sub_id';",1);
				if($sth->rows() == 1){
					$in{'db'}='sl_callcenters';
					&auth_logging('schedule_dropped',$sub_id,1);
					$va{'message'}="Done:Record Deleted";
				}
			}
		}else{
			## Update all records

			my $rows = int($in{'rows'});
			if($rows > 0){

				my $total=0;
				my $updated=0;

				for(1..$rows){
					my $i=$_;
					if($in{'id_'.$i}){
						my $id = int($in{'id_'.$i});
						my $from_time = $in{'from_time_'.$i};
						my $to_time = $in{'to_time_'.$i};
						(length($from_time)==5) and ($from_time.=":00");
						(length($to_time)==5 and $to_time ne '24:00') and ($to_time.=":00");
						($to_time eq '24:00' or $to_time eq '23:59:00') and ($to_time="23:59:59");

						my ($sth)=&Do_SQL("UPDATE sl_callcenters SET FromTime='$from_time', ToTime='$to_time' WHERE ID_Callcenter='$id';",1);
						if($sth->rows() == 1){
							$in{'db'}='sl_callcenters';
							&auth_logging('schedule_updated',$id,1);
							$updated++;
						}
						$total++;
					}
				}
				$va{'message'}="Done:$updated of $total records updated";

			}

		}
	}

	## List Records
	my @ary_days=("Sunday","Monday","Tuesday","Wednesday","Thursday","Friday","Saturday");

	my $this_row=1;
	my ($sth)=&Do_SQL("SELECT DISTINCT Name FROM sl_callcenters ORDER BY Name,WD,FromTime",1);
	while(my($ccname)=$sth->fetchrow()){

		$va{'searchresults'}.=qq|<table align="center" width="90%">
							<tr>
								<td class="cell_on" align="center" valign="middle" colspan="5" class="formtable"><h2>$ccname</h2></td>
							</tr>
							<tr>
								<td class="gcell_on" align="center" width="20%"><h3>Day of Week</h3></td>
								<td class="gcell_on" align="center"><h3>Schedule</h3></td>
								<td class="gcell_on" align="center" width="20%"><h3>From</h3></td>
								<td class="gcell_on" align="center" width="25%" colspan="2"><h3>To</h3></td>
							</tr>|;

		my (@c) = split(/,/,$cfg{'srcolors'});
		#my $rows = $sth->rows();

		my ($sth)=&Do_SQL("SELECT ID_callcenter,FromTime,ToTime,TIMESTAMPDIFF(MINUTE,CONCAT(CURDATE(),' 00:00:00'),CONCAT(CURDATE(),' ',FromTime))AS FromTimeMin,TIMESTAMPDIFF(MINUTE,CONCAT(CURDATE(),' 00:00:00'),CONCAT(CURDATE(),' ',ToTime))AS ToTimeMin,WD FROM sl_callcenters WHERE Name='$ccname' AND Status='Active'  ORDER BY WD,FromTime",1);
		while(my($id,$from_time,$to_time,$from_time_min,$to_time_min,$wd) = $sth->fetchrow()){

			$string_day = $ary_days[$wd];

			$d = 1 - $d;

			$va{'searchresults_js'} .= qq|
			\$(function() {
				\$( "#slider-range_$this_row" ).slider({
					range: true,
					min: 0,
					max: 1439,
					step: 30,
					values: [ $from_time_min, $to_time_min ],
					slide: function( event, ui ) {
						var from_hours = Math.floor(ui.values[0] / 60);
						var from_minutes = ui.values[0] - (from_hours * 60);

						var to_hours = Math.floor(ui.values[1] / 60);
						var to_minutes = ui.values[1] - (to_hours * 60);

						if(from_hours < 10) from_hours = '0' + from_hours;
						if(to_hours < 10) to_hours = '0' + to_hours;
						if(from_minutes < 10) from_minutes = '0' + from_minutes;
						if(to_minutes < 10) to_minutes = '0' + to_minutes;

						\$('#slider-from_$this_row').html(from_hours+':'+from_minutes);
						\$('#slider-to_$this_row').html(to_hours+':'+to_minutes);
						\$('#from_time_$this_row').val(from_hours+':'+from_minutes);
						\$('#to_time_$this_row').val(to_hours+':'+to_minutes);

						\$('#slider-from_$this_row').css('background-color','#fffacd');
						\$('#slider-to_$this_row').css('background-color','#fffacd');

					}
				});
				var from_hours = Math.floor(\$("#slider-range_$this_row" ).slider( "values", 0 ) / 60);
				var from_minutes = \$("#slider-range_$this_row" ).slider( "values", 0 ) - (from_hours * 60);

				var to_hours = Math.floor(\$("#slider-range_$this_row" ).slider( "values", 1 ) / 60);
				var to_minutes = \$( "#slider-range_$this_row" ).slider( "values", 1 ) - (to_hours * 60);

				if(from_hours < 10) from_hours = '0' + from_hours;
				if(to_hours < 10) to_hours = '0' + to_hours;
				if(from_minutes < 10) from_minutes = '0' + from_minutes;
				if(to_minutes < 10) to_minutes = '0' + to_minutes;
				\$('#slider-from_$this_row').html(from_hours+':'+from_minutes);
				\$('#slider-to_$this_row').html(to_hours+':'+to_minutes);
			});\n|;


			$va{'searchresults'} .= qq|
							<tr bgcolor='$c[$d]'>
								<td class='smalltext' valign='top'>
									<input type="hidden" id="id_$this_row" name="id_$this_row" value="$id">
									<input type="hidden" id="from_time_$this_row" name="from_time_$this_row" value="$from_time">
									<input type="hidden" id="to_time_$this_row" name="to_time_$this_row" value="$to_time">
									<img src='[va_imgurl]/[ur_pref_style]/b_drop.png' title='Drop This $string_day Record' alt='' border='0' id="slider-drop_$this_row" style="cursor:pointer;">
									&nbsp;
									$string_day
								</td>
								<td class='smalltext' valign='top' align='center'>\n
									<div class="demo">\n
										<div id="slider-range_$this_row"></div>\n
									</div>\n
								</td>\n
								<td class='smalltext' align="center" valign='top' id="slider-from_$this_row"></td>\n
								<td class='smalltext' align="center"  valign='top' id="slider-to_$this_row"></td>\n
								<td class='smalltext' align="center"  valign='top' id="slider-each_$this_row">
									<img src='[va_imgurl]/[ur_pref_style]/b_reload.gif' title='Update $string_day' alt='' border='0' id="slider-update_$this_row" style="cursor:pointer;">
									<img src='[va_imgurl]/[ur_pref_style]/b_add.gif' title='Add New $string_day Record' alt='' border='0' id="slider-add_$this_row" style="cursor:pointer;">
								</td>
							</tr>\n|;

			$va{'options_selected'} .= qq|chg_select('from_hour_$this_row','$this_fhour')\n
								chg_select('from_minute_$this_row','$this_fmin')\n
								chg_select('to_hour_$this_row','$this_thour')\n
								chg_select('to_minute_$this_row','$this_tmin')\n|;

			$this_row++;
		}

		$va{'searchresults'} .= "</table>\n&nbsp;\n";
		$va{'rows'}=$this_row;

	}


	print "Content-type: text/html\n\n";
	print &build_page('mm_callcenters_availability.html');

}


sub mm_dids_home {
# --------------------------------------------------------
# Forms Involved: 
# Created on: 9/12/2007 9:43AM
# Last Modified on:
# Last Modified by:
# Author: 
# Description : This function goes only here in admin.html
	print "Content-type: text/html\n\n";
	if($in{'chgto'} and $usr{'usergroup'} <=2){
		
		&connect_db_w($cfg{'dbi_db_pbx'},$cfg{'dbi_host_pbx'},$cfg{'dbi_user_pbx'},$cfg{'dbi_pw_pbx'});
		
		my $sth=&Do_SQL("UPDATE sl_numbers SET Destination='$in{'chgto'}';",1);
		if($sth->rows() > 0){
			## Note
			&auth_logging('destination_updated_all','123456',1);
			$va{'message'} = 'All Destinations Updated';
		}else{
			$va{'message'} = 'Error: The change dind\'t take effect';
		}
	}

	for(1..9){
		$va{'did_mixicom'} .= '<li><a href="/cgi-bin/mod/admin/admin?cmd=mm_dids_home&chgto=Mixicom'.$_.'">Redirect all to Mixicom'.$_.'</a></li>';
	}


	print &build_page('mm_dids_home.html');
}


sub mm_contracts_home {
# --------------------------------------------------------
# Forms Involved: mm_contracts_home
# Created on: 03/20/2012 9:43AM
# Last Modified on:
# Last Modified by:
# Author:
# Description : This function goes only here in admin.html.cgi


	## Status Links
	my @ary_status = load_enum_toarray('sl_mediacontracts','Status');
	for(0..$#ary_status){
		my $status = $ary_status[$_];
		$str .= "$status<br>";
		$va{'status_links'} .= '<li><a href="/cgi-bin/mod/admin/dbman?cmd=mm_contracts&search=Search&status='.$status.'">'.$status.'</a></li>'."\n";
	}

	print "Content-type: text/html\n\n";
	print &build_page('mm_contracts_home.html');
}

sub mm_contracts_daymatrix {
# --------------------------------------------------------
# Forms Involved: mm_contracts_home
# Created on: 03/20/2012 9:43AM
# Last Modified on:
# Last Modified by:
# Author:
# Description : This function goes only here in admin.html.cgi


	## Status Links
	if ($in{'from_estday'}){
		my ($sth) = &Do_SQL("SELECT TIME( DATE_ADD( '$in{'from_estday'} 00:00:00', INTERVAL TRUNCATE( (HOUR( sl_leads_calls.Time ) *60 + MINUTE( sl_leads_calls.Time )) /5, 0 ) *5
					MINUTE ) ) AS t, 
					sl_leads_calls.DIDUS, 
					COUNT( DISTINCT (ID_leads) ) AS q,
					didmx AS DIDMX,
					ID_mediacontracts,
					product,
					channel
					
					FROM `sl_leads_calls`
					LEFT JOIN sl_mediadids
					ON sl_leads_calls.DIDUS=sl_mediadids.didusa
					
					WHERE sl_leads_calls.Date = '$in{'from_estday'}'
					GROUP BY TRUNCATE( HOUR( (sl_leads_calls.Time ) *60 + MINUTE( sl_leads_calls.Time )) /5, 0 ) , sl_leads_calls.DIDUS ORDER BY sl_leads_calls.Time");
		while($rec = $sth->fetchrow_hashref()){
			if ($rec->{'q'}>5){
				++$va{'matches'};
				if ($rec->{'ID_mediacontracts'}>0){
					$cont_info = &load_db_names('sl_mediacontracts','ID_mediacontracts',$rec->{'ID_mediacontracts'},"<a href='/cgi-bin/mod/admin/dbman?cmd=mm_contracts&view=[ID_mediacontracts]'>([ID_mediacontracts])</a>  [Station]/[Offer]/[Status]");
					if ($cont_info =~ /No Identificado/){
						$cont_info = "<font color='red'>$cont_info</font>";
					}
				}else{
					$cont_info = 'N/A';
				}
				$va{'searchresults'} .= qq|
					<tr>
						<td>$rec->{'t'}</td>
						<td>$rec->{'DIDUS'}</td>
						<td>$rec->{'DIDMX'}</td>
						<td>$rec->{'product'}</td>
						<td>$rec->{'channel'}</td>
						<td>$rec->{'q'}</td>
						<td>$cont_info</td>
					<tr>\n|;
			}
		}
	}

	print "Content-type: text/html\n\n";
	if ($va{'matches'}>0){
		$va{'yesterday'}= sqldate_plus($in{'from_estday'},-1);
		$va{'tomorrow'}= sqldate_plus($in{'from_estday'},1);
		print &build_page('mm_contracts_daymatrix_results.html');
	}else{
		print &build_page('mm_contracts_daymatrix.html');
	}
}



sub mm_dids_bulk {
# --------------------------------------------------------

	if($in{'action'}){

		if(!$in{'dids_bulk'}){
			$error++;
			$error['dids_bulk'] = trans_txt('required');
		}


		if(!$error){

			my $from_date_from_time = "CURDATE(),ADDTIME(CURTIME(),'00:05:00')";
			my $bad_did;
			my $total=0;
			my ($from_date,$from_time,$to_date,$to_time,$from_date_from_time,$to_date_to_time);
			my $date_execueted='0000-00-00';

			if($in{'from_date'}){
				($from_date,$from_time) = split(/\s/,$in{'from_date'},2);
				$from_date_from_time = "'$from_date','$from_time'";
			}

			if($in{'to_date'}){
				($to_date,$to_time) = split(/\s/,$in{'to_date'},2);
				$to_date_to_time = "'$to_date','$to_time'";
			}


			if(lc($in{'dids_bulk'}) eq 'all'){
				&connect_db_w($cfg{'dbi_db_pbx'},$cfg{'dbi_host_pbx'},$cfg{'dbi_user_pbx'},$cfg{'dbi_pw_pbx'});
				my ($sth) = &Do_SQL("SELECT GROUP_CONCAT(DISTINCT didmx ORDER BY didmx) FROM sl_numbers WHERE Status='Active';",1);
				$in{'dids_bulk'} = $sth->fetchrow();
			}

			my ($sth) = &Do_SQL("SELECT IF(TIMESTAMPDIFF(MINUTE,NOW(),'$in{'fromdate'}') < 5,1,0);");
			if($sth->fetchrow()){
				$va{'message'} = &trans_txt('invalid') . 'The exception can\'t be less than 5 mins away fron now.<br>';
			}else{


				my (@ary) = split(/\s+|,|\n|\t/,$in{'dids_bulk'});
				DIDS:for my $i(0..$#ary){

					my $this_did = int($ary[$i]);
					my $id_mediadids = &load_name('sl_mediadids','didmx',$this_did,"ID_mediadids");

					&connect_db_w($cfg{'dbi_db_pbx'},$cfg{'dbi_host_pbx'},$cfg{'dbi_user_pbx'},$cfg{'dbi_pw_pbx'});
					my ($sth) = &Do_SQL("SELECT destination FROM sl_numbers WHERE didmx='$this_did';",1);
					my($this_destination) = $sth->fetchrow();

					$i++;

					if($to_date){
						$va{'message'} = &trans_txt('mm_dids_exceptionadded') . '<br>';	

						my ($sth) = &Do_SQL("SELECT IF(TIMESTAMPDIFF(MINUTE,NOW(),'$in{'to_date'}') < 5,1,0);");
						if($sth->fetchrow()){
							$bad_did .= "$this_did<br>";
							next DIDS;
						}
						my ($sth) = &Do_SQL("INSERT INTO sl_cron_scripts VALUES(0,\"UPDATE `sl_numbers` SET destination='$this_destination' WHERE `didmx` IN('$this_did') \",'s7','sql',0,'$to_date','$to_time','','Active',1);");
						my ($sth) = &Do_SQL("INSERT INTO sl_mediadids_notes SET ID_mediadids='$id_mediadids',Notes='DIDMx: $this_did\nFrom/To: $in{'todestination'} / $this_destination\nDate: $in{'to_date'}',Type='Low',Date=CURDATE(),Time=CURTIME(),ID_admin_users='$usr{'id_admin_users'}';");

					}
					my ($sth) = &Do_SQL("INSERT INTO sl_cron_scripts VALUES(0,\"UPDATE `sl_numbers` SET destination='$in{'todestination'}' WHERE `didmx` IN('$this_did') \",'s7','sql',0,$from_date_from_time,'','Active',1);");
					my ($sth) = &Do_SQL("INSERT INTO sl_mediadids_notes SET ID_mediadids='$id_mediadids',Notes='DIDMx: $this_did\nFrom/To:$this_destination / $in{'todestination'}\nDate: $in{'from_date'}',Type='Low',Date=CURDATE(),Time=CURTIME(),ID_admin_users='$usr{'id_admin_users'}';");
					$total++;
				}
			}

			if($bad_did ne ''){
				$va{'message'} .= "DIDs not inserted :<br>" . $bad_did;
			}else{
				$va{'message'} .= "Done: All DIDs redirected ($total)";
			}

		}
		delete($in{'action'});
	}

	print "Content-type: text/html\n\n";
	print &build_page('mm_dids_bulk.html');
		
}


sub mm_dids_cronlist {
# --------------------------------------------------------

	if($in{'action'}){

		if($in{'delete'}){

			my $id_cron_scripts = int($in{'delete'});
			my ($sth) = &Do_SQL("UPDATE sl_cron_scripts SET Status='Inactive' WHERE ID_cron_scripts = '$id_cron_scripts';");
			$va{'message'} = 'Redirection Dropped';
			$in{'db'}='sl_cron_scripts';
			&auth_logging('cron_script_dopped',$id_cron_scripts);
		}
		delete($in{'action'});
	}

	my (@c) = split(/,/,$cfg{'srcolors'});
	my ($sth) = &Do_SQL("SELECT COUNT(*) FROM sl_cron_scripts WHERE server='s7' AND type='sql' AND script LIKE 'UPDATE `sl_numbers` SET destination%' AND Status IN('Active'/*,'Inactive'*/)  AND TIMESTAMPDIFF(MINUTE,CONCAT(scheduledate,' ',scheduletime),NOW()) < 15;");
	$va{'matches'} = $sth->fetchrow;
	if ($va{'matches'}>0){
		if ($in{'print'}){
			$sth = &Do_SQL("SELECT sl_cron_scripts.*,FirstName,LastName FROM sl_cron_scripts,admin_users WHERE server='s7' AND type='sql' AND script LIKE 'UPDATE `sl_numbers` SET destination%' AND Status IN('Active'/*,'Inactive'*/)  AND TIMESTAMPDIFF(MINUTE,CONCAT(scheduledate,' ',scheduletime),NOW()) < 15 AND sl_cron_scripts.ID_admin_users=admin_users.ID_admin_users ORDER BY scheduledate DESC, scheduletime DESC;");
		}else{
			(!$in{'nh'}) and ($in{'nh'}=1);
			$first = ($in{'nh'} - 1) * $usr{'pref_maxh'};
			($va{'pageslist'},$qs) = &pages_list($in{'nh'},"/cgi-bin/mod/$usr{'application'}/admin",$va{'matches'},$usr{'pref_maxh'});
			$sth = &Do_SQL("SELECT sl_cron_scripts.*,FirstName,LastName FROM sl_cron_scripts,admin_users WHERE server='s7' AND type='sql' AND script LIKE 'UPDATE `sl_numbers` SET destination%' AND sl_cron_scripts.Status IN('Active'/*,'Inactive'*/) AND CONCAT(scheduledate,' ',scheduletime) > NOW() AND sl_cron_scripts.ID_admin_users=admin_users.ID_admin_users ORDER BY scheduledate,scheduletime LIMIT $first,$usr{'pref_maxh'};");
		}

		while ($rec = $sth->fetchrow_hashref){
			$d = 1 - $d;

			if($rec->{'script'} =~ /destination='(\w*)'/){
				$rec->{'Destination'} = $1;
			}

			$rec->{'script'} =~ s/\`|'//g; #'
			if($rec->{'script'} =~ /didmx IN\(([\d{4},*]+)\)/ or $rec->{'script'} =~ /didmx = '(\d{4})'/){
				$rec->{'didmx'} = $1;
			}

			my @ary = split(/,/,$rec->{'didmx'});

			if($#ary > 0){


				for $i(0..$#ary){
					$rec->{'didmx'} = $ary[$_];
					&connect_db_w($cfg{'dbi_db_pbx'},$cfg{'dbi_host_pbx'},$cfg{'dbi_user_pbx'},$cfg{'dbi_pw_pbx'});
					my ($sth) = &Do_SQL("SELECT destination FROM sl_numbers WHERE didmx='$rec->{'didmx'}';",1);
					$rec->{'Original_Destination'} = $sth->fetchrow();

					my $delete_this = ($rec->{'Status'} eq 'Active' and $i == 0) ? "<a href='javascript:trjump(\"[va_script_url]?cmd=[in_cmd]&action=1&delete=$rec->{'ID_cron_scripts'}\")'><img src='[va_imgurl]/[ur_pref_style]/b_drop.png' title='Delete' alt='' border='0'></a>" : '';
					my $this_style = $rec->{'Status'} eq 'Inactive' ? "style='text-decoration:line-through;'" : '';

					$va{'searchresults'} .= "<tr bgcolor='$c[$d]' $this_style>\n";
					$va{'searchresults'} .= "  <td class='smalltext' valign='top'>$delete_this</td>\n";
					$va{'searchresults'} .= "  <td class='smalltext' valign='top'>$rec->{'didmx'}</td>\n";
					$va{'searchresults'} .= "  <td class='smalltext' valign='top'>$rec->{'Original_Destination'}</td>\n";
					$va{'searchresults'} .= "  <td class='smalltext' valign='top'>$rec->{'Destination'}</td>\n";
					$va{'searchresults'} .= "  <td class='smalltext' valign='top'>$rec->{'scheduledate'}</td>\n";
					$va{'searchresults'} .= "  <td class='smalltext' valign='top'>$rec->{'scheduletime'}</td>\n";
					$va{'searchresults'} .= "  <td class='smalltext' valign='top'>($rec->{'ID_admin_users'}) $rec->{'FirstName'} $rec->{'LastName'}</td>\n";
					$va{'searchresults'} .= "</tr>\n";
					$i++;
				}

			}else{

				&connect_db_w($cfg{'dbi_db_pbx'},$cfg{'dbi_host_pbx'},$cfg{'dbi_user_pbx'},$cfg{'dbi_pw_pbx'});
				my ($sth) = &Do_SQL("SELECT destination FROM sl_numbers WHERE didmx='$rec->{'didmx'}';",1);
				$rec->{'Original_Destination'} = $sth->fetchrow();

				my $delete_this = $rec->{'Status'} eq 'Active' ? "<a href='javascript:trjump(\"[va_script_url]?cmd=[in_cmd]&action=1&delete=$rec->{'ID_cron_scripts'}\")'><img src='[va_imgurl]/[ur_pref_style]/b_drop.png' title='Delete' alt='' border='0'></a>" : '';
				my $this_style = $rec->{'Status'} eq 'Inactive' ? "style='text-decoration:line-through;'" : '';

				$va{'searchresults'} .= "<tr bgcolor='$c[$d]' $this_style>\n";
				$va{'searchresults'} .= "  <td class='smalltext' valign='top'>$delete_this</td>\n";
				$va{'searchresults'} .= "  <td class='smalltext' valign='top'>$rec->{'didmx'}</td>\n";
				$va{'searchresults'} .= "  <td class='smalltext' valign='top'>$rec->{'Original_Destination'}</td>\n";
				$va{'searchresults'} .= "  <td class='smalltext' valign='top'>$rec->{'Destination'}</td>\n";
				$va{'searchresults'} .= "  <td class='smalltext' valign='top'>$rec->{'scheduledate'}</td>\n";
				$va{'searchresults'} .= "  <td class='smalltext' valign='top'>$rec->{'scheduletime'}</td>\n";
				$va{'searchresults'} .= "  <td class='smalltext' valign='top'>($rec->{'ID_admin_users'}) $rec->{'FirstName'} $rec->{'LastName'}</td>\n";
				$va{'searchresults'} .= "</tr>\n";


			}

		}
	}else{
		$va{'pageslist'} = 1;
		$va{'searchresults'} = qq|
			<tr>
				<td colspan='7' align="center">|.&trans_txt('search_nomatches').qq|</td>
			</tr>\n|;
	}

	print "Content-type: text/html\n\n";
	print &build_page('mm_dids_cronlist.html');

}

1;
