
sub rephome {
# --------------------------------------------------------
# Created :  Carlos Haas 01/01/2007 6:47:28 PM
# Last Update : 
# Locked by : 
# Description :
#
#
	my ($days_range) =  7;
	## Dates
	my ($sth) = &Do_SQL("SELECT 
			CONCAT(MONTH(CURDATE()),'-',YEAR(CURDATE())) AS this_month,
			CONCAT(YEAR(CURDATE()),'-', MONTH(CURDATE()),'-01') AS this_month_fromday,
			CURDATE() AS this_month_today,
			
			CONCAT(MONTH(DATE_SUB(CURDATE(), INTERVAL 1 MONTH)),'-',YEAR(DATE_SUB(CURDATE(), INTERVAL 1 MONTH))) AS last_month,
			CONCAT(YEAR(DATE_SUB(CURDATE(), INTERVAL 1 MONTH)),'-', MONTH(DATE_SUB(CURDATE(), INTERVAL 1 MONTH)),'-01') AS last_month_fromday,
			CONCAT(YEAR(DATE_SUB(CURDATE(), INTERVAL 1 MONTH)),'-', MONTH(DATE_SUB(CURDATE(), INTERVAL 1 MONTH)),'-',
			DAY(DATE_SUB(CONCAT(YEAR(CURDATE()),'-', MONTH(CURDATE()),'-01'), INTERVAL 1 DAY))) AS last_month_fromday");
	my ($rec) = $sth->fetchrow_hashref;
	foreach my $key (keys %{$rec}){
		$va{$key} = $rec->{$key};
	}
	
	### LOAD DATA
	my (%data,$total,$total_shipped,$total_vc, $total_scanned);
	my ($sth) = &Do_SQL("SELECT 
					COUNT(*), 
					Ptype , 
					SUM(IF(Status='Shipped',1,0)) AS Shipped, 
					SUM(IF(Status='Void' OR Status='Cancelled',1,0)) AS VoidCancelled, 
					SUM((SELECT count(*) FROM sl_entershipments WHERE
					sl_entershipments.ID_orders=sl_orders.ID_orders
					AND Status='ok')) AS Scanned
					FROM sl_orders
					WHERE sl_orders.Date >= DATE_SUB( CURDATE( ) , INTERVAL $days_range DAY ) AND Status <> 'System Error'
					GROUP BY Ptype");
	
	while (@ary = $sth->fetchrow_array){
		$data{$ary[1].'_total'} = $ary[0]; 	$total += $ary[0];
		$data{$ary[1].'_shipped'} = $ary[2]; $shipped += $ary[2];
		$data{$ary[1].'_vc'} = $ary[3]; $vc += $ary[3];
		$data{$ary[1].'_scanned'} = $ary[4]; $scanned += $ary[4];
	}
	my ($sth) = &Do_SQL("SELECT 
			DATEDIFF(CURDATE(),sl_orders.Date) AS OrdOld,
			COUNT(*), 
			Ptype , 
			SUM(IF(Status='Shipped',1,0)) AS Shipped, 
			SUM(IF(Status='Void' OR Status='Cancelled',1,0)) AS VoidCancelled, 
			SUM((SELECT count(*) FROM sl_entershipments WHERE
			     sl_entershipments.ID_orders=sl_orders.ID_orders
			     AND Status='ok')) AS Scanned
			FROM sl_orders
			WHERE sl_orders.Date >= DATE_SUB( CURDATE( ) , INTERVAL $days_range DAY ) AND Status <> 'System Error'
			GROUP BY DATEDIFF(CURDATE(),sl_orders.Date),Ptype");
	while (@ary = $sth->fetchrow_array){
		$data{$ary[0].'all_total'} += $ary[1]; 	
		$data{$ary[0].'all_scanned'} += $ary[5]; 
		$data{$ary[0].$ary[2].'_total'} = $ary[1]; 	
		$data{$ary[0].$ary[2].'_shipped'} = $ary[3]; 
		$data{$ary[0].$ary[2].'_vc'} = $ary[4]; 
		$data{$ary[0].$ary[2].'_scanned'} = $ary[5]; 
	}
	
	###########################	
	### build Reports
	###########################	
		##################################
		## Pie Orders by Paid Type
		##################################
		$va{'chart_options'} = "renderTo: 'container1', margin: [50, 50, 50, 50], width: 400";
		$va{'chart_title'} = 'Orders by Paid Type';
		$va{'chart_subtitle'} = 'Percentages';
		$va{'chart_plotarea'} = 'shadow: null, borderWidth: null, backgroundColor: null';
		$va{'chart_tooltip'} = "enabled: true,formatter: function() { return '<b>'+ this.point.name +'</b>: '+ this.y +' %';}";
		$va{'chart_plotoptions'} = "pie: {
							allowPointSelect: true,
							cursor: 'pointer',
							dataLabels: {
								enabled: true,
								format: '<b>{point.name}</b>: '+ this.y +' %',
								style: {
									color: 'black'
								}
							}
						}";
		#$va{'chart_legend'} = "layout: 'vertical', style: { left: 'auto', bottom: 'auto', right: '10px', top: '50px' }";
		$va{'series_data'} = "{ type: 'pie', name: 'Orders by Paid Type ', data: [['Tot Orders TDC',".&fix_number($data{'Credit-Card_total'}*100,$total,2)."],['Tot Orders COD',".&fix_number($data{'COD_total'}*100,$total,2)."],['Tot Orders Dep',".&fix_number($data{'Referenced Deposit_total'}*100,$total,2)."]] }";
		$va{'highchart1'} = &build_page('func/construct_highcharts.html');
		
		##################################
		## Pie Orders Shipped
		##################################
		$va{'chart_options'} = "renderTo: 'container2', margin: [50, 50, 50, 50], width: 400";
		$va{'chart_title'} = 'Orders Shipped';
		$va{'chart_subtitle'} = 'Percentages';
		$va{'chart_plotarea'} = 'shadow: null, borderWidth: null, backgroundColor: null';
		$va{'chart_tooltip'} = "enabled: true,formatter: function() { return '<b>'+ this.point.name +'</b>: '+ this.y +' %';}";
		$va{'chart_plotoptions'} = "pie: {
							allowPointSelect: true,
							cursor: 'pointer',
							dataLabels: {
								enabled: true,
								format: '<b>{point.name}</b>: '+ this.y +' %',
								style: {
									color: 'black'
								}
							}
						}";
		#$va{'chart_legend'} = "layout: 'vertical', style: { left: 'auto', bottom: 'auto', right: '10px', top: '50px' }";
		$va{'series_data'} = "{ type: 'pie', name: 'Orders vs Shipped ', data: [['Shipped',".&fix_number($scanned*100,$total,2)."],['Void/Cancelled',".&fix_number($vc*100,$total,2)."],['In Process',".&fix_number(($total-$vc-$scanned)*100,$total,2)."]] }";
		$va{'highchart2'} = &build_page('func/construct_highcharts.html');
		
		##################################
		## TDC Shipped
		##################################
		$va{'chart_options'} = "renderTo: 'container3', margin: [50, 50, 50, 50], width: 400";
		$va{'chart_title'} = 'Orders TDC Shipped';
		$va{'chart_subtitle'} = 'Percentages';
		$va{'chart_plotarea'} = 'shadow: null, borderWidth: null, backgroundColor: null';
		$va{'chart_tooltip'} = "enabled: true,formatter: function() { return '<b>'+ this.point.name +'</b>: '+ this.y +' %';}";
		$va{'chart_plotoptions'} = "pie: {
							allowPointSelect: true,
							cursor: 'pointer',
							dataLabels: {
								enabled: true,
								format: '<b>{point.name}</b>: '+ this.y +' %',
								style: {
									color: 'black'
								}
							}
						}";
		#$va{'chart_legend'} = "layout: 'vertical', style: { left: 'auto', bottom: 'auto', right: '10px', top: '50px' }";
		$va{'series_data'} = "{ type: 'pie', name: 'Orders by Paid Type ', data: [['Shipped',".&fix_number($data{'Credit-Card_scanned'}*100,$data{'Credit-Card_total'},2)."],['Void/cancelled',".&fix_number($data{'Credit-Card_vc'}*100,$data{'Credit-Card_total'},2)."],['In Process',".&fix_number(($data{'Credit-Card_total'}-$data{'Credit-Card_scanned'}-$data{'Credit-Card_vc'})*100,$total,2)."]] }";
		$va{'highchart3'} = &build_page('func/construct_highcharts.html');

		##################################
		## COD Shipped
		##################################
		$va{'chart_options'} = "renderTo: 'container4', margin: [50, 50, 50, 50], width: 400";
		$va{'chart_title'} = 'Orders COD Shipped';
		$va{'chart_subtitle'} = 'Percentages';
		$va{'chart_plotarea'} = 'shadow: null, borderWidth: null, backgroundColor: null';
		$va{'chart_tooltip'} = "enabled: true,formatter: function() { return '<b>'+ this.point.name +'</b>: '+ this.y +' %';}";
		$va{'chart_plotoptions'} = "pie: {
							allowPointSelect: true,
							cursor: 'pointer',
							dataLabels: {
								enabled: true,
								format: '<b>{point.name}</b>: '+ this.y +' %',
								style: {
									color: 'black'
								}
							}
						}";
		#$va{'chart_legend'} = "layout: 'vertical', style: { left: 'auto', bottom: 'auto', right: '10px', top: '50px' }";
		$va{'series_data'} = "{ type: 'pie', name: 'Orders by Paid Type ', data: [['Shipped',".&fix_number($data{'COD_scanned'}*100,$data{'COD_total'},2)."],['Void/cancelled',".&fix_number($data{'COD_vc'}*100,$data{'COD_total'},2)."],['In Process',".&fix_number(($data{'COD_total'}-$data{'COD_scanned'}-$data{'COD_vc'})*100,$total,2)."]] }";
		$va{'highchart4'} = &build_page('func/construct_highcharts.html');

		##################################
		## Shipped / Day
		##################################
		$va{'chart_options'} = "renderTo: 'container5', width: 750, type: 'column'";
		$va{'chart_title'} = 'Orders Shipped Per Day';
		$va{'chart_xaxis'} = " categories: [
                'Today',
                '-1',
                '-2',
                '-3',
                '-4',
                '-5',
                '-6',
                '-7'
            ]";
		$va{'chart_yaxis'} = " min: 0, title: { text: 'Shipped (%)'}  ";
		$va{'chart_tooltip'} = qq| headerFormat: '<span style="font-size:10px">{point.key} Days</span><table>', pointFormat: '<tr><td style="color:{series.color};padding:0">{series.name}: </td><td style="padding:0"><b>{point.y} %</b></td></tr>', footerFormat: '</table>', shared: true, useHTML: true|;
    	$va{'chart_plotoptions'} = qq| column: { pointPadding: 0.2, borderWidth: 0 }|;
        $va{'series_data'} = qq|
        {
            name: 'All',
            data: [|.&build_serie('all',0,7,%data).qq|]

        }, {
            name: 'Credit-Card',
            data: [|.&build_serie('Credit-Card',0,7,%data).qq|]

        }, {
            name: 'COD',
            data: [|.&build_serie('COD',0,7,%data).qq|]

        }|;
		$va{'chart_subtitle'} = 'Qty';
		$va{'highchart5'} = &build_page('func/construct_highcharts.html');
		

		
#		$va{'message'} = "<pre>".$va{'series_data'} ."</pre>"; 
#		$data{$ary[1].'_total'} = $ary[0]; 	$total += $ary[0];
#		$data{$ary[1].'_shipped'} = $ary[2]; $shipped += $ary[2];
#		$data{$ary[1].'_vc'} = $ary[3]; $vc += $ary[3];
#		$data{$ary[1].'_scanned'} = $ary[4]; $scanned += $ary[4];
#
#
#		$data{$ary[0].$ary[2].'_total'} = $ary[1]; 	
#		$data{$ary[0].$ary[2].'_shipped'} = $ary[3]; 
#		$data{$ary[0].$ary[2].'_vc'} = $ary[4]; 
#		$data{$ary[0].$ary[2].'_scanned'} = $ary[5]; 



		
		###### Charge the js scripts if not charged
		if(!$va{'highcharts_js'}){
			$va{'highcharts_js'} = &build_page('func/highcharts_js.html');
		}
		
	
	
	print "Content-type: text/html\n\n";
	print &build_page('rephome.html');
}


sub build_serie {
# --------------------------------------------------------
	my ($tag,$from,$to,%data) = @_;
	my ($output,$num);
	for my $i($from..$to){
		if ($data{$i.$tag.'_total'}>0){
			$output .= &round($data{$i.$tag.'_scanned'}/$data{$i.$tag.'_total'}*100).',';
			#$output .= $data{$i.$tag.'_scanned'}.',';
			#$output .= $data{$i.$tag.'_total'}.',';
		}else{
			$output .= '0,';
		}
	}
	chop($output);
	return $output;
#	name: 'Credit-Card',
#	data: [0$data{'0Credit-Card_total'}/$data{'0Credit-Card_scanned'}, 0$data{'1Credit-Card_total'}, 0$data{'2Credit-Card_total'}, 0$data{'3Credit-Card_total'}, 0$data{'4Credit-Card_total'}, 0$data{'5Credit-Card_total'}, 0$data{'6Credit-Card_total'}, 0$data{'7Credit-Card_total'}]
#	name: 'All',
#	data: [0$data{'0_total'}, 0$data{'1_total'}, 0$data{'2_total'}, 0$data{'3_total'}, 0$data{'4_total'}, 0$data{'5_total'}, 0$data{'6_total'}, 0$data{'7_total'}]

}

sub fix_number {
# --------------------------------------------------------
	my ($dividend, $divisor,$decimals) = @_;
	
	if ($divisor>0){
		return &round($dividend / $divisor,$decimals);
	}else{
		return 0;
	}
}

1;
 #data: [0,0,0,17,25,32,43,19]
 #data: [0,0,0,50,39,50,59,26]