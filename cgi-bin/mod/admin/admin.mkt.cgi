#!/usr/bin/perl
##########################################################
##			 ADMIN PAGES :MEDIA & PLANNING TOOLS	##
##########################################################



sub mkt_callcenters_availability{
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
				my ($tmp_sth)=&Do_SQL("SELECT Name, FromTime, ToTime, WD, Status FROM sl_callcenters WHERE ID_callcenter='$sub_id';");
				my( $tmp_name, $tmp_fromtime, $tmp_totime, $tmp_wd, $tmp_status ) = $tmp_sth->fetchrow_array();

				my ($sth)=&Do_SQL("INSERT INTO sl_callcenters values( 0, '$tmp_name', '$tmp_fromtime', '$tmp_totime', '$tmp_wd', '$tmp_status', CURDATE(), Time=CURTIME(), '$usr{'id_admin_users'}');",1);
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
	print &build_page('mkt_callcenters_availability.html');

}


sub mkt_callcenters_logs{
# --------------------------------------------------------
# Created :  Roberto Barcenas 10/26/2011 4:05:28 PM
# Last Update :
# Description : Muestra los logs de los movimientos realizados al callcenter
#

	&connect_db_w($cfg{'dbi_db_pbx'},$cfg{'dbi_host_pbx'},$cfg{'dbi_user_pbx'},$cfg{'dbi_pw_pbx'});
	

	my (@c) = split(/,/,$cfg{'srcolors'});
	$sth = &Do_SQL("SELECT COUNT(*) FROM admin_logs WHERE tbl_name='sl_callcenters';",1);
	$va{'matches'} = $sth->fetchrow;
	if ($va{'matches'}>0){
		if ($in{'print'}){
			$sth = &Do_SQL("SELECT * FROM admin_logs WHERE tbl_name='sl_callcenters' ORDER BY ID_admin_logs DESC;",1);
		}else{
			(!$in{'nh'}) and ($in{'nh'}=1);
			$first = ($in{'nh'} - 1) * $usr{'pref_maxh'};
			($va{'pageslist'},$qs) = &pages_list($in{'nh'},"/cgi-bin/mod/$usr{'application'}/admin",$va{'matches'},$usr{'pref_maxh'});
			$va{'pageslist'} =~	s/xtabs=products&//g;
			$sth = &Do_SQL("SELECT * FROM admin_logs WHERE tbl_name='sl_callcenters' ORDER BY ID_admin_logs DESC LIMIT $first,$usr{'pref_maxh'};",1);
		}

		while ($rec = $sth->fetchrow_hashref){
			my $admin_name = &load_name('admin_users','ID_admin_users',$rec->{'id_admin_users'},"CONCAT(FirstName,' ',LastName)");
			$d = 1 - $d;
			$va{'searchresults'} .= "<tr bgcolor='$c[$d]'>\n";
			$va{'searchresults'} .= "   <td class='smalltext'>$rec->{'LogDate'}</td>\n";
			$va{'searchresults'} .= "   <td class='smalltext'>$rec->{'LogTime'}</td>\n";
			$va{'searchresults'} .= "   <td class='smalltext'>".&trans_txt($rec->{'Message'})."</td>\n";
			$va{'searchresults'} .= "   <td class='smalltext'>$rec->{'ID_admin_users'}</td>\n";
			$va{'searchresults'} .= "   <td class='smalltext'>$admin_name</td>\n";
			$va{'searchresults'} .= "   <td class='smalltext'>$rec->{'IP'}</td>\n";
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
	print &build_page('mkt_callcenters_logs.html');

}

1;
