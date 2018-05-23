#!/usr/bin/perl
##################################################################
#   REPORTS : MEDIA
##################################################################


sub rep_mm_ratios {
# --------------------------------------------------------
##TODO: Todos los textos deben estar fuera del codigo y/o a traves de transtxt

	my ($field,$query,$sb);
	if ($in{'action'}){
		$in{'sortby'} = int($in{'sortby'});
		(!$in{'sortby'}) and ($in{'sortby'} = 1);
		## Group by
		if ($in{'groupby'} eq 'week'){
			$field = 'Week';
		}elsif($in{'groupby'} eq 'month'){
			$field = 'Month';
		}elsif($in{'groupby'} eq 'famprod'){
			$field = 'FamProd';	
		}elsif($in{'groupby'} eq 'dma'){
			$field = 'DMA';
		}elsif($in{'groupby'} eq 'station'){
			$field = 'Station';
		}elsif($in{'groupby'} eq 'agency'){
			$field = 'Agency';
		}elsif($in{'groupby'} eq 'destination'){
			$field = 'Destination';
		}elsif($in{'groupby'} eq 'format'){
			$field = 'Format';
		}else{
			$in{'groupby'} = 'day';
			$field = 'ESTDay';
		}
		$va{'title_colx'} = $field;
		$in{'qs'} = "&groupby=".$in{'groupby'};
		
		## Exclude Ratio=0
		if ($in{'excluder0'}){
			$query .= " AND Ratio>0";
			$in{'qs'} .= "&excluder0=on";
		}
		if ($in{'exclude999'}){
			$query .= " AND DestinationDID<>9998  AND DestinationDID<>9995";
			$in{'qs'} .= "&exclude999=on";
		}
		if ($in{'dma'}){
			$query .= " AND DMA='".&filter_values($in{'dma'})."'";
			$in{'qs'} .= "&dma=".$in{'dma'};
		}
		if ($in{'from_date'}){
			$in{'from_date'} =~ s/\//-/g;
			$in{'qs'} .= "&from_date=".$in{'from_date'};
			$query .= " AND sl_mediacontracts.ESTDay>='$in{'from_date'}'";
		}
		if ($in{'to_date'}){
			$in{'to_date'} =~ s/\//-/g;
			$in{'qs'} .= "&to_date=".$in{'to_date'};
			$query .= " AND sl_mediacontracts.ESTDay<='$in{'to_date'}'";
		}
		if($in{'from_time'} or $in{'to_time'}){
			$in{'from_time'} 	= "00:00:00"	if !$in{'from_time'};
			$in{'to_time'} 		= "23:59:59"	if !$in{'to_time'};
			$query .= " AND sl_mediacontracts.ESTTime BETWEEN '$in{'from_time'}' AND '$in{'to_time'}'";
		}
		if ($in{'dids'} !~ /-1/ and $in{'dids'}){
			my $dids=$in{'dids'};
			$dids =~ s/\|/','/g;
			
			my @ary = split(/\|/,$in{'dids'});
			for (0..$#ary){
				$dname .= &load_name('sl_mediadids','didmx',$ary[$_],'num800').',';
			}
			chop($dname);
			$query .= " AND sl_mediacontracts.DestinationDID IN ('$dids') ";  #DNIS-NUMBER
			$in{'qs'} .= "&dids=".$in{'dids'};
		}
		if ($in{'famprod'} !~ /-1/ and $in{'famprod'}){
			my $famprod=$in{'famprod'};
			$famprod =~ s/\|/','/g;
			
			$query .= " AND FamProd IN ('$famprod') ";  #DNIS-NUMBER
			$in{'qs'} .= "&famprod=".$in{'famprod'};
		}
	
		## Sort By

		if ($in{'sortby'}){
			$sb = ' ORDER BY scol'.$in{'sortby'};
			$in{'qs'} .= "&sortby=".$in{'sortby'};
		}
		
		## Sort Order
		if ($in{'sortorder'}){
			$sb = $sb . ' ' . $in{'sortorder'};
			$in{'qs'} .= "&sortorder=".$in{'sortorder'};
		}
		
		if ($query){
			$query = "WHERE ". substr($query, 4)
		}
		
		my ($sth) = &Do_SQL("SELECT COUNT(*) FROM sl_mediacontracts INNER JOIN sl_mediacontracts_stats ON sl_mediacontracts.ID_mediacontracts=sl_mediacontracts_stats.ID_mediacontracts $query");
		my ($tot) = $sth->fetchrow();
		$va{'tot_max'} = .01; $va{'tot_min'} =99;
		if ($tot>0){
			(!$in{'nh'}) and ($in{'nh'}=1);
			my (@c) = split(/,/,$cfg{'srcolors'});
	    	my ($sth);
			if($in{'groupby'} eq 'month'){
				$sth = &Do_SQL("SELECT MONTH(ESTDay) AS x, Ratio as Y, SUM(Calls),COUNT(*), SUM(Cost), SUM(TotOrders), SUM(QtyOrders) FROM sl_mediacontracts INNER JOIN sl_mediacontracts_stats ON sl_mediacontracts.ID_mediacontracts=sl_mediacontracts_stats.ID_mediacontracts $query GROUP BY MONTH(ESTDay) $sb ");
			}else{
				$sth = &Do_SQL("SELECT 
						$field AS scol1, 
						SUM(Cost) AS scol2,
						SUM(Calls) AS scol3,
						SUM(TotOrders)  AS scol4,
						IF(SUM(Calls)>0,SUM(QtyOrders)/SUM(Calls),0) AS scol5,
						IF(SUM(TotOrders)>0,SUM(TotTDC)/SUM(TotOrders),0) AS scol6,
						IF(SUM(QtyOrders),SUM(TotOrders)/SUM(QtyOrders),0) AS scol7,
						IF(SUM(Calls)>0,SUM(Cost)/SUM(Calls),0) AS scol8,
						IF(SUM(Cost)>0,SUM(TotOrders)/SUM(Cost),0) AS scol9,
						SUM(QtyOrders),
						COUNT(*),
						SUM(TotTDC)
						FROM sl_mediacontracts INNER JOIN sl_mediacontracts_stats ON sl_mediacontracts.ID_mediacontracts=sl_mediacontracts_stats.ID_mediacontracts $query GROUP BY $field $sb ");
			}
			$va{'matches'} = $sth->rows;
			while (@ary = $sth->fetchrow_array){
				$d = 1 - $d;
				$va{'searchresults'} .= qq|
					<tr bgcolor='$c[$d]'>
						<td class="smalltext">&nbsp;&nbsp;&nbsp;$ary[0]</td>
						<td class="smalltext" nowrap>|.&format_price($ary[1]).qq|</td>
						<td class="smalltext" nowrap>$ary[2]</td>
						<td class="smalltext" nowrap>|.&format_price($ary[3]).qq|</td>						
						<td class="smalltext" nowrap>|.&round($ary[4]*100,2).qq|%</td>
						<td class="smalltext" nowrap>|.&round($ary[5]*100,2).qq|%</td>
						<td class="smalltext" nowrap>|.&format_price($ary[6]).qq|</td>	
						<td class="smalltext" nowrap>|.&format_price($ary[7]).qq|</td>	
						<td class="smalltext" nowrap>|.&round($ary[8],2).qq|</td>
					</tr>\n|;
				$va{'tot_calls'}  += $ary[2];
				$va{'tot_ord'}    += $ary[3];
				$va{'tot_ordqty'} += $ary[9];
				$va{'tot_cost'}   += $ary[1];
				$va{'tot_costqty'}+= $ary[10];
				$va{'tot_tdc'}    += $ary[12];

				###### Data for Graph
				$series_data[0] .= "'$ary[0]',";   # X xaxis
				$series_data[1] .= $ary[8] . ',';  # Ratio
				$series_data[2] .= $ary[2] .',';   # Calls
				$series_data[3] .= round($ary[1],2) .','; # Cost
				$series_data[4] .= round($ary[3],2) .','; # Orders
				
			}
		}else{
			$va{'tot_calls'} = 0;
			$va{'tot_ord'}    = 0;
			$va{'tot_ordqty'} = 0;
			$va{'tot_cost'}   = 0;
			$va{'tot_costqty'}= 0;
			$va{'matches'} = 0;
			$va{'pageslist'} = 1;
			$va{'searchresults'} .= qq|
						<tr>
							<td colspan="5" align="center">|.&trans_txt('search_nomatches').qq|</td>
						</tr>\n|;
		}
		
		if ($in{'print'}){
			print "Content-type: text/html\n\n";
			print &build_page('header_print.html');
			print &build_page('rep_mm_ratios_print.html');
		}else{
			$va{'tot_ratio'}  = &round($va{'tot_ord'}/$va{'tot_cost'},2) if ($va{'tot_cost'}>0);
			$va{'tot_ptdc'}  =  &round($va{'tot_tdc'}/$va{'tot_ord'}*100,2) if ($va{'tot_ord'}>0);
			$va{'tot_orders'} = &format_price($va{'tot_ord'}) . " (".$va{'tot_ordqty'}.")";
			$va{'tot_cost'}   = &format_price($va{'tot_cost'}) . " (".$va{'tot_costqty'}.")";
			$va{'tot_calls'}  = &format_number($va{'tot_calls'});
			
			
			
			#################################
			## Building Sorting Header
			#################################
			my ($qs) = $in{'qs'};
			$qs =~ s/sortby/oldsortby/i;			
			for my $i(0..9){
				if ($i eq $in{'sortby'}){
					my ($img,$nsorder);

					if ($in{'sortorder'} eq 'ASC'){
						$img = 'arr.up.gif';
						$nsorder = 'DESC';
					}else{
						$img = 'arr.down.gif';
						$nsorder = 'ASC';
					}
					
					$va{'sort_col'.$i} = qq|
			<a name='qmenu' id='qmenu'> </a>
		    	<a href='#qmenu' id='ajax_btn' onClick="popup_show('ajax_windows', 'ajax_drag', 'ajax_exit', 'element-right', -1, -1,'qmenu');loadDoc('/cgi-bin/common/apps/ajaxbuild?ajaxbuild=report_quickchg&glist=day,week,month,famprod,dma,station,agency,destination,format&url=|. &urlencode($in{'qs'}."&cmd=$in{'cmd'}&action=1"). qq|');">
		    	<img src="[va_imgurl]/[ur_pref_style]/$img">
		    </a>|;
		    	}else{
		    		$va{'link_col'.$i} = "onmouseover='m_over(this)' onmouseout='m_out(this)' onclick=\"trjump('/cgi-bin/mod/[ur_application]/admin?cmd=$in{'cmd'}&action=1$qs&sortby=$i')\" ";
		    	}
			}

			&auth_logging('report_view','');
			&load_graph($field,'gray','Ratio,Calls,Cost,Orders','line,pie,pie,pie,pie',@series_data);
			($va{'rep1'},$va{'rep2'},$va{'rep3'},$va{'rep4'},$va{'rep5'},$va{'rep6'}) = ('on','off','off','off','off','off');
			print "Content-type: text/html\n\n";

			print &build_page('rep_mm_ratios_list.html');
		}
		return;
	}

	print "Content-type: text/html\n\n";
	print &build_page('rep_mm_ratios.html');
}



sub load_graph {
# --------------------------------------------------------
	my ($rep_type,$rep_theme,$xaxis_tit,$gype,@series_data)=@_;
	my ($output,$data);
	for (1..$#series_data){
		if ($series_data[$_] =~ /(.*),$/){
			$series_data[$_] = $1;
		}
	}
	my (@xaxis_titles) = split(/,/, $xaxis_tit);
	my (@graph_type)   = split(/,/, $gype);

	(!$rep_theme) and ($rep_theme = 'gray');
	$va{'highchart_theme'} = ($rep_theme eq 'blank') ? '' : &build_page('func/highcharts_theme_'. $rep_theme .'.html');

	my $xaxis_mod = ",title: { text: '$rep_type' } ";
	my $chart_mod= '';
#	if($sth->rows() > 5){
		$xaxis_mod = ",labels: {rotation: -45, align: 'right', style: { font: 'normal 13px Verdana, sans-serif'}} ";
		$chart_mod = ',height: 450, margin: [ 50, 50, 150, 100]';
#	}
	
	$va{'chart_options'} = "renderTo: 'container1', defaultSeriesType: 'areaspline' $chart_mod ";
	$va{'chart_title'} = $rep_type;
	#$va{'chart_subtitle'} = $rep_type;
	$va{'chart_xaxis'} = "categories: [".$series_data[0]."] $xaxis_mod ";
	
	$va{'chart_tooltip'} = "enabled: true,formatter: function() {return '<b>'+ this.series.name +'</b><br/>'+this.x +': '+ this.y;}";
	
	$va{'chart_yaxis'} = "title: { text: '";
	for my $i(1..$#series_data){
		$va{'chart_yaxis'} .= " ". $xaxis_titles[$i-1] . "  /";
		$va{'series_data'} .= "{ name: '$xaxis_titles[$i-1]', data: [$series_data[$i]]},";
	}
	chop($va{'chart_yaxis'});
	$va{'chart_yaxis'} .= "', margin: 75 }";
	chop($va{'series_data'});
	
	
	$output = &build_page('func/construct_highcharts.html');
	
	## Pie per Serie
	for my $i(1..$#series_data){
		$names = $xaxis_titles[$i-1];
		if ($graph_type[$i-1] eq 'line'){
			$data = $series_data[$i]
			
		}else{
			$data = '';
		}
		
		$va{'chart_title'} = $xaxis_titles[$i-1];

		if  ($graph_type[$i-1] eq 'line'){
			$xaxis_mod = ",labels: {rotation: -45, align: 'right', style: { font: 'normal 13px Verdana, sans-serif'}} ";
			$chart_mod = ',height: 400, margin: [ 50, 50, 150, 100]';
		
			$va{'chart_options'} = "renderTo: 'container".($i+1)."', margin: [50, 150, 10, 5], defaultSeriesType: 'areaspline' $chart_mod";
			
			$va{'chart_xaxis'} = "categories: [".$series_data[0]."] $xaxis_mod";
			
			$va{'chart_tooltip'} = "enabled: true,formatter: function() {return '<b>'+ this.series.name +'</b><br/>'+this.x +': '+ this.y;}";
			
			$va{'chart_yaxis'} = "title: { text: '". $xaxis_titles[$i-1] . "  ', margin: 75 }";
			$va{'series_data'} = "{ name:'$xaxis_titles[$i-1]', data: [$series_data[$i]]}";
			
		}else{
			my ($tot);
			my (@d) = split (/,/, $series_data[$i]);
			my (@c) = split (/,/, $series_data[0]);
			for (0..$#d){
				$tot += $d[$_];
			}
			my ($data) = '';
			for (0..$#d){
				$data .= '['.$c[$_] . ', ' . &round($d[$_]/$tot*100,2).'],';
			}
			chop($data);
			
			$va{'chart_options'} = "renderTo: 'container".($i+1)."', margin: [50, 150, 10, 5], width: 400";
			$va{'chart_subtitle'} = 'Percentages';
			$va{'chart_plotarea'} = 'shadow: null, borderWidth: null, backgroundColor: null';
			$va{'chart_tooltip'} = "enabled: true,formatter: function() { return '<b>'+ this.point.name +'</b>: '+ this.y +' %';}";			
			$va{'chart_plotoptions'} = "pie: {
							allowPointSelect: true,
							cursor: 'pointer',
							dataLabels: {
								enabled: true,
								formatter: function() {
									if (this.y > 50) return this.point.name;
								},
								color: 'white',
								style: {
									font: '13px Trebuchet MS, Verdana, sans-serif'
								}
							}
						}";
			$va{'chart_legend'} = "layout: 'vertical', style: { left: 'auto', bottom: 'auto', right: '10px', top: '50px' }";
			$va{'series_data'} = "{ type: 'pie', data: [$data] }";
		}

		#$va{'highchart'.$i}=&build_page('func/construct_highcharts.html');
		$output .= &build_page('func/construct_highcharts.html');
	}
	
#	## Pie Quantity
#	$va{'chart_options'} = "renderTo: 'container2', margin: [50, 150, 10, 5], width: 400";
#	$va{'chart_title'} = 'Quantity';
#	$va{'chart_subtitle'} = 'Percentages';
#	$va{'chart_plotarea'} = 'shadow: null, borderWidth: null, backgroundColor: null';
#	$va{'chart_tooltip'} = "enabled: true,formatter: function() { return '<b>'+ this.point.name +'</b>: '+ this.y +' %';}";
#	$va{'chart_plotoptions'} = "pie: {
#						allowPointSelect: true,
#						cursor: 'pointer',
#						dataLabels: {
#							enabled: true,
#							formatter: function() {
#								if (this.y > 50) return this.point.name;
#							},
#							color: 'white',
#							style: {
#								font: '13px Trebuchet MS, Verdana, sans-serif'
#							}
#						}
#					}";
#	$va{'chart_legend'} = "layout: 'vertical', style: { left: 'auto', bottom: 'auto', right: '10px', top: '50px' }";
#	$va{'series_data'} = "{ type: 'pie', name: 'Quantity Percentages ', data: [$series_quantityp] }";
#	#$va{'highchart2'} = &build_page('func/construct_highcharts.html');
#	
#
#	## Pie Amount
#	$va{'chart_options'} = "renderTo: 'container3', margin: [50, 150, 10, 5], width: 400";
#	$va{'chart_title'} = 'Amount';
#	$va{'series_data'} = "{ type: 'pie', name: 'Quantity Percentages ', data: [$series_amountp] }";
#	#$va{'highchart3'} = &build_page('func/construct_highcharts.html');

	
	###### Charge the js scripts if not charged
	if(!$va{'highcharts_js'}){
		$va{'highcharts_js'} = &build_page('func/highcharts_js.html').$output;
	}
}

1;
