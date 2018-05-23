#!/usr/bin/perl
sub dev_home {
# --------------------------------------------------------
	if ($in{'action'}){
		my $cmd = 'devrun_'.$in{'action'};
		if (defined &$cmd){
			&$cmd();
			return;
		}
	}
	my (%rec) = (
		'scustomer' =>	'Show Customer Relationship',
		'dbproducts' =>	'Download Products List',
		'order_movements' =>	'Repair Order Movements',
#		'phonemart_payments' =>	'Phonemart to Diresksys',

		'rr_salesprodorigin'=>	'Report : Sales by Product and Origin',
		'rr_salesretail'	=>	'Report : Retail Sales (Detailled)',
		'rr_salesdist'		=>	'Report : Dist Sales (Detailled)',

		'weborders'			=>	'Ecommerce : Web Orders (Semi-Monthly)',
		'weborders_prod'	=>	'Ecommerce : Web Orders/products (Quarterly)',
		'weborders_weekly'	=>	'Ecommerce : Web Orders (Weekly >=2014)',
		'webpricelist'		=>	'Ecommerce : Price List',
		'webprodlist'		=>	'Ecommerce : Product List ',
		'webgetWebSales'	=>	'Ecommerce : MX Sale Bonus ',
		'ecommerce_orders_by_source' =>	'Ecommerce : Orders by Source',
			
		
		'prod_check_inventory'	=>	'Products Tools : Download Inventory, for selected IDs',		
		'prod_bulkPriceChanges'	=>	'Products Tools : Update Bulk prices',			
		
#		'cpc'	=>	'CDR : Calculate CPC',

		'add_mediadids' =>  'CDR : Update MediaDIDs table',
#		'pretoordintransit'	=>	'Convert preorders in transit',
		
		'assignardids'	=>	'Media : Assign DID',
		'loadformato'	=>	'Media: Load Formato USA',
		'checkformato'	=>	'Media: Check Formato USA',
		'updatestatus'	=>	'Media: Recheck Status',
		'updateleads'	=>	'Media: Create Leads from S7',
		'checkleads'	=>	'Media: Data check ',
		'ratiossummary'	=>	'Media: Ratios Consolidados',
		
		
		'ccbonus_monthly' =>	'CC-Inbound: Callcenter Bonus',


		'daily_prepaidcard_report' => 'CC-Inbound: Prepaid Card',
		'warehouse_mod_codsales_table' => 'Warehouse: Repair COD Sales Table',
		'dbproducts' => 'Merchandising: Products List',
		);
	foreach $key (sort{$rec{$a} cmp $rec{$b}} keys %rec){
		$va{'searchresults'} .= qq|<li><a href="/cgi-bin/mod/$usr{'application'}/admin?cmd=dev_home&action=$key">$rec{$key}</li>\n|;
	}
	
	print "Content-type: text/html\n\n";
	print &build_page('dev_runhome.html');
	
}

sub devrun_rr_salesprodorigin{
# --------------------------------------------------------
	#print "Content-type: text/html\n\n";
	#print "<pre>";
	print "Content-type: application/vnd.ms-excel\n";
	print "Content-disposition: attachment; filename=sales_by_prod_by_origin.csv\n\n";
	
	my (%report);
	my ($sth) = &Do_SQL("SELECT * FROM `sl_categories` WHERE Status='Active' AND ID_categories IN(1,86,48,67,71,81,82,87,96,110,115)");
	while ($rec = $sth->fetchrow_hashref() ) {
		#$report{'pname_'.$rec->{ID_categories}} = $rec->{Title}
		#print "Report Product : ($rec->{ID_categories})$rec->{Title}\n";
		## TV Sales by Month
		my ($sth2) = &Do_SQL("
	SELECT MONTH(sl_orders.Date) as Month , SUM(SalePrice*Quantity) AS Tot FROM `sl_orders_products` 

LEFT JOIN sl_orders ON sl_orders.ID_orders=sl_orders_products.ID_orders
WHERE 
ID_products IN 
    (SELECT 100000000+ID_products FROM `sl_products_categories` WHERE `ID_categories`=$rec->{ID_categories}) AND 
sl_orders.Date >='2011-01-01' AND
sl_orders.Status='Shipped' AND
sl_orders.ID_admin_users IN 
    (SELECT ID_admin_users FROM admin_users WHERE user_type IN ('INCC-Matutino','INCC-Vespertino','INCC-Nocturno','LA','Mexico','Hermosillo','Puerto Rico','Recompras','IN-Outbound','Monterrey','cc103','cc104'))

Group by MONTH(sl_orders.Date)");
		while ($tmp = $sth2->fetchrow_hashref() ) {
			print "$rec->{Title},TV,$tmp->{'Month'},$tmp->{'Tot'}\n";
		}
		
		### WH-DR Sales by Month
		my ($sth2) = &Do_SQL("
SELECT MONTH(sl_orders.Date) as Month , SUM(SalePrice) AS Tot, SUM(Quantity) AS Qty FROM `sl_orders_products` 

LEFT JOIN sl_orders ON sl_orders.ID_orders=sl_orders_products.ID_orders
WHERE 
ID_products = 100000000 AND
Related_ID_products IN 
    (SELECT 400000000+ID_parts FROM `sl_parts` WHERE `ID_categories` =$rec->{ID_categories}) AND 
sl_orders.Date >='2011-01-01' AND
sl_orders.Status='Shipped' AND
sl_orders.ID_customers IN 
    (SELECT ID_customers FROM sl_customers WHERE type='Wholesale-DR')

Group by MONTH(sl_orders.Date)");
		while ($tmp = $sth2->fetchrow_hashref() ) {
			print "$rec->{Title},Distributors,$tmp->{'Month'},$tmp->{'Tot'},$tmp->{'Qty'}\n";
		}

		### WH-Retail Sales by Month
		my ($sth2) = &Do_SQL("
SELECT MONTH(sl_orders.Date) as Month , SUM(SalePrice) AS Tot, SUM(Quantity) AS Qty FROM `sl_orders_products` 

LEFT JOIN sl_orders ON sl_orders.ID_orders=sl_orders_products.ID_orders
WHERE 
ID_products = 100000000 AND
Related_ID_products IN 
    (SELECT 400000000+ID_parts FROM `sl_parts` WHERE `ID_categories` =$rec->{ID_categories}) AND 
sl_orders.Date >='2011-01-01' AND
sl_orders.Status='Shipped' AND
sl_orders.ID_customers IN 
    (SELECT ID_customers FROM sl_customers WHERE type='Wholesale-Retail')

Group by MONTH(sl_orders.Date)");
		while ($tmp = $sth2->fetchrow_hashref() ) {
			print "$rec->{Title},Retail,$tmp->{'Month'},$tmp->{'Tot'},$tmp->{'Qty'}\n";
		}

		## Ecommerce Sales by Month Part 1
		my ($sth2) = &Do_SQL("
	SELECT MONTH(sl_orders.Date) as Month , SUM(SalePrice*Quantity) AS Tot FROM `sl_orders_products` 

LEFT JOIN sl_orders ON sl_orders.ID_orders=sl_orders_products.ID_orders
WHERE 
ID_products IN 
    (SELECT 100000000+ID_products FROM `sl_products_categories` WHERE `ID_categories`=$rec->{ID_categories}) AND 
sl_orders.Date >='2011-01-01' AND
sl_orders.Status='Shipped' AND
sl_orders.ID_admin_users IN 
    (SELECT ID_admin_users FROM admin_users WHERE user_type = 'Internet')

Group by MONTH(sl_orders.Date)");
		while ($tmp = $sth2->fetchrow_hashref() ) {
			print "$rec->{Title},Ecommerce,$tmp->{'Month'},$tmp->{'Tot'}\n";
		}

		## Ecommerce Sales by Month Part 2
		my ($sth2) = &Do_SQL("
SELECT MONTH(sl_orders.Date) as Month , SUM(SalePrice) AS Tot, SUM(Quantity) AS Qty FROM `sl_orders_products` 

LEFT JOIN sl_orders ON sl_orders.ID_orders=sl_orders_products.ID_orders
WHERE 
ID_products = 100000000 AND
Related_ID_products IN 
    (SELECT 400000000+ID_parts FROM `sl_parts` WHERE `ID_categories` =$rec->{ID_categories}) AND 
sl_orders.Date >='2011-01-01' AND
sl_orders.Status='Shipped' AND
sl_orders.ID_admin_users IN 
    (SELECT ID_admin_users FROM admin_users WHERE user_type = 'Internet')

Group by MONTH(sl_orders.Date)");
		while ($tmp = $sth2->fetchrow_hashref() ) {
			print "$rec->{Title},Ecommerce,$tmp->{'Month'},$tmp->{'Tot'}\n";
		}
	}
}

sub devrun_rr_salesretail{
# --------------------------------------------------------
	#print "Content-type: text/html\n\n";
	#print "<pre>";
	print "Content-type: application/vnd.ms-excel\n";
	print "Content-disposition: attachment; filename=salesretail.csv\n\n";
	my ($query,$headers);
	$headers = "Cust ID,Name,";
	for my $m(1..10){
		$query .= "SUM(IF(MONTH(sl_orders.Date) =$m, SalePrice ,0)) AS T$m,";
		$query .= "SUM(IF(MONTH(sl_orders.Date) =$m, Quantity,0)) AS Q$m,";
		$headers .= "Tot-$m,Qty-$m,";
	}
	chop($query);
	chop($query,$headers);
	
	my ($sth) = &Do_SQL("
SELECT ID_customers , (SELECT CONCAT(FirstName,' ', LastName1,' ',company_name)  From sl_customers WHERE ID_customers=sl_orders.ID_customers) AS Name, 

$query 

FROM `sl_orders_products` 

LEFT JOIN sl_orders ON sl_orders.ID_orders=sl_orders_products.ID_orders
WHERE 
sl_orders.Date >='2011-01-01' AND
sl_orders.Status='Shipped' AND
sl_orders.ID_customers IN 
    (SELECT ID_customers FROM sl_customers WHERE type='Wholesale-Retail')

group by ID_customers");
	print $headers."\n";
	while (@tmp = $sth->fetchrow_array() ) {
		$tmp[1] =~ s/,/ /g;
		print join(',', @tmp). "\n";
	}

}

sub devrun_rr_salesdist{
# --------------------------------------------------------
	#print "Content-type: text/html\n\n";
	#print "<pre>";
	print "Content-type: application/vnd.ms-excel\n";
	print "Content-disposition: attachment; filename=sales_dist.csv\n\n";
	my ($query,$headers);
	$headers = "Cust ID,Name,";
	for my $m(1..10){
		$query .= "SUM(IF(MONTH(sl_orders.Date) =$m, SalePrice ,0)) AS T$m,";
		$query .= "SUM(IF(MONTH(sl_orders.Date) =$m, Quantity,0)) AS Q$m,";
		$headers .= "Tot-$m,Qty-$m,";
	}
	chop($query);
	chop($query,$headers);
	
	my ($sth) = &Do_SQL("
SELECT ID_customers , (SELECT CONCAT(FirstName,' ', LastName1,' ',company_name)  From sl_customers WHERE ID_customers=sl_orders.ID_customers) AS Name, 

$query 

FROM `sl_orders_products` 

LEFT JOIN sl_orders ON sl_orders.ID_orders=sl_orders_products.ID_orders
WHERE 
sl_orders.Date >='2011-01-01' AND
sl_orders.Status='Shipped' AND
sl_orders.ID_customers IN 
    (SELECT ID_customers FROM sl_customers WHERE type='Wholesale-DR')

group by ID_customers");
	print $headers."\n";
	while (@tmp = $sth->fetchrow_array() ) {
		$tmp[1] =~ s/,/ /g;
		print join(',', @tmp). "\n";
	}

}



##################################################################
#    OPERATIONS : ORDERS   	#
##################################################################

sub devrun_scustomer{
#-----------------------------------------	
	my($id_orders,$id_customers_new,$add1,$add2,$add3,$id_customers_old,$customer_old);
	print "Content-type: application/octetstream\n";
	print "Content-disposition: attachment; filename=custorder.csv\n\n";
	
	
	$sth = &Do_SQL("SELECT ID_orders,ID_customers,concat( if( isnull( Address1 ) , '', Address1 ) , ' ', if( isnull( Address2 ) , '', Address2 ) , ' ', if( isnull( Address3 ) , '', Address3 ) , ' ', Zip, ' ', state )
									 FROM sl_orders WHERE ID_orders >= 100000 ORDER BY ID_orders LIMIT 1000");
	while(($id_orders,$id_customers_new,$addn) = $sth->fetchrow()){
		my $customer_new  = &load_name('sl_customers','ID_customers',$id_customers_new,"CONCAT(FirstName,' ',LastName1,' ',LastName2)");
		my $customer_add1 = &load_name('sl_customers','ID_customers',$id_customers_new,"Address1");
		
		$sth2 = &Do_SQL("SELECT  ID_customers,CONCAT(FirstName,' ',LastName1,' ',LastName2) FROM sl_customers WHERE concat( if( isnull( Address1 ) , '', Address1 ) , ' ', if( isnull( Address2 ) , '', Address2 ) , ' ', if( isnull( Address3 ) , '', Address3 ) , ' ', Zip, ' ', state ) = '$addn' ");
		($id_customers_old,$customer_old) = $sth2->fetchrow();  
		if($id_customers_new ne $id_customers_old){
#			print "SAME CUSTOMER\r\n";
#		}else{
			print "$id_orders,($id_customers_new) $customer_new -- $customer_add1,$addn,";
			print "($id_customers_old) $customer_old\r\n";  
		}	
	}
}


sub devrun_dbproducts{
#-----------------------------------------
# Created on: 07/15/09  11:38:00 By  Roberto Barcenas
# Forms Involved: 
# Description : Descarga la relacion de productos de la DB
# Parameters : 	

	my $fname = 'sltv_products.csv';
	$fname = 'innovausa_products.csv'	if $in{'e'} eq '1';
	$fname = 'innovapr_products.csv'	if $in{'e'} eq '2';
	$fname = 'training_products.csv'	if $in{'e'} eq '3';
	$fname = 'gts_products.csv'	if $in{'e'} eq '4';

	print "Content-type: application/octetstream\n";
	print "Content-disposition: attachment; filename=$fname\n\n";
	print "ID Product,Model,Name,Status,Sale Price,DownSale 1,DownSale 2,DownSale 3,DownSale 4,FP Price,Flexpays,Free Shipping,Pay Type,Product Cost,Packing Options,Vendor,Cost,Shipping\r\n";
	
	$sth = &Do_SQL("SELECT `ID_products` , `Model` , sl_products.`Name` , sl_products.`Status` , `SPrice` , `SPrice1` , `SPrice2` , `SPrice3` , `SPrice4` , 
									FPPrice,`Flexipago` ,free_shp_opt, `PayType` ,SLTV_NetCost,sl_packingopts.`Name` , `Vendor` , `Cost` , `Shipping` 
									FROM `sl_products` INNER JOIN sl_packingopts ON sl_packingopts.`ID_packingopts` = sl_products.`ID_packingopts`
									ORDER BY ID_products;");
									
	while(my($idp,$model,$pname,$pstatus,$sp1,$sp2,$sp3,$sp4,$sp5,$fpp,$fp,$fs,$pt,$pcost,$poname,$vendor,$cost,$shipping)	= $sth->fetchrow()){
			print "$idp,$model,$pname,$pstatus,$sp1,$sp2,$sp3,$sp4,$sp5,$fpp,$fp,$fs,$pt,$pcost,$poname,$vendor,$cost,$shipping\r\n";
	}						
}




sub devrun_prod_check_inventory{
## -------------------------------------------------------- ##

	my $fname = 'inventory.csv';
	my ($ids) = "224003,871259,993870,170242,743200,544897,505865,359785,311629,783445,159661,379402,966457,315155,693194,922478,281794,488456,925616,979659,579165,696500,393556,781374,665289,126314,731605,869889,347888,962924,937925,459075,775297,595489,941401,687694,472032,812555,444468,678682,604417,270599,290542,248104,473013,683851,610563,577467,998180,701784,491742,283992,306510,326787,947878,463776,446770,903112,712841,152783,579787,188245,446345,978610,460708,910894,108702,913221,511312,850775,368239,261798,719528,864766,491850,994356,129158,921422,361953,714737,846598,132798,565649,946322,770694,749297,749022,392455,185554,661715,624236,110212,983614,953585,223458,337187,847985,334718,122782,271562,983957,478573,253719,582979,658036,668693,709320,295198,998400,296383,981882,616785,208716,305092,221422,836679,915761,119083,932537,601573,558203,396359,419439,842639,954368,292667,767713,196885,438327,551804,924423,261916,176050,286362,539723,416766,451417,479666,923797,950545,385594,386592,568650,206069,259353,591961,260545,306761,992340,656851,107704,251046,343713,252562,699877,269273,740008,691438,754063,683041,525521,331268,567035,848812,324411,735438,825321,299973,557216,628796,925296,875224,908187,521629,728167,566673,729198,699227,761199,945571,558854,240244,691540,935510,363862,767546,711250,463376,605152,135164,676244,510912,636450,394046,824508,469595,846741,643494,835206,821825,846871,216249,988222,921753,230621,704351,414296,670570,438935,580007,170613,628157,641458,376232,551890,330381,738950,638979,918287,124925,578648,532205,853154,196872,264241,866502,770484,571344,327057,987084,831991,826765,547646,667123,706927,242796,346217,331856,252761,247873,159001,677759,671633,257148,574633,513830,202245,532019,402539,306171,539311,774549,595970,786345,646082,853162,826607,256737,904476,178446,375472,437716,565429,613160,738781,221127,528955,675169,940674,927152,605790,957150,415497,632115,972010,634488,320055,700015,568020,115722,159591,191218,255639,988075,435517,308939,170992,626107,761794,555439,711644,268410,992599,512768,421884,525182,243462,759738,997215,107449,271713,802540,795576,519310,522151,575050,331235,449646,787918,238852,776673,522526,422908,241303,416517,517948,172316,800789,462603,783118,665862,405249,788217,848319,537588,951960,319117,797978,580278,146909,968293,892520,321957,905854,949466,163125,215792,327418,607553,673552,823946,159976,803815,737773,657109,783059,901413,934056,705460";
	
	
	#print "Content-type: text/html\n\n";
	print "Content-type: application/octetstream\n";
	#print "Content-type: application/vnd.ms-excel\n";
	print "Content-disposition: attachment; filename=$fname\n\n";
	#print "ID_orders,Date,ID_neworder,Product,COGS,OrderStatus,OrderNet,Tax,Shipping,OrderTotal,Payments\r\n";
	
	my $sth = &Do_SQL("SELECT ID_products,Name,Model,Sprice,FPPrice,FlexiPago,Status
			FROM sl_products
			WHERE ID_products IN ($ids);");
									
	print "ID_products,Name,Model,Sprice,FPPrice,FlexiPago,Cost,On-Hand,Status\r\n";
	my ($q) = 2;
	my ($i,$pw,$p_add,$p_main,$p_cost,$p_inv);
	while(my($id_products,$name,$model,$sprice,$fpprice,$flexipago,$status)	= $sth->fetchrow()){
	    my $prefix = '';
	    $name =~ s/,/ /g;
	    $model =~ s/,/ /g; 
	    $prefix = 'pre'    if    $type    eq    'Preorder';
	    #print "1)$type,2)$ptype,3)$ido,4)$date,5)$neworder,6)$cogs,7)$status,8)$net,11)$total,13)$id_user\r\n";
	    #next;
	    #my $cogs=0;
	    #(!$id_user) and ($id_user='xx');
	    my (%prods,$p_skus,$inv);
	    my $sthc = &Do_SQL("SELECT ID_sku_products,ID_parts,Qty FROM `sl_skus_parts` WHERE `ID_sku_products` LIKE '%$id_products'");
		while(my($id_prod,$id_sku,$qty) = $sthc->fetchrow()){
			$prods{$id_prod.'_cost'} += $qty*load_sltvcost(400000000+$id_sku);
		    $inv = calc_parts_inventory(400000000+$id_sku)/$qty;
		    if ($prods{$id_prod.'_inv'}==0 or $prods{$id_prod.'_inv'}> $inv){
		    	$prods{$id_prod.'_inv'} = $inv;
		    }
		}
		$p_add = '';$p_cost = 0;$p_inv = 0;
		$p_main = "$id_products,$name,$model,$sprice,$fpprice,$flexipago";
		#print "$id_products,$name,$model,$sprice,$shipping,$fpprice,$flexipago\r\n";
		foreach $key (keys %prods){
			if ($key =~ /(\d+)_cost/){
				$id = $1;
				$n = &load_db_names('sl_skus','ID_sku_products',$id,'[choice1],[choice2],[choice3],[choice4]');
				$n =~ s/,,|,$//g; $n =~ s/,/-/g;
				(!$n) and ($n = '---');
				$p_add .= ",($id)$n,,,,,,$prods{$id.'_cost'},$prods{$id.'_inv'},".&load_name('sl_skus','ID_sku_products',$id,'Status')."\r\n";
				($p_cost<$prods{$id.'_cost'}) and ($p_cost=$prods{$id.'_cost'});
				($p_inv<$prods{$id.'_inv'}) and ($p_inv=$prods{$id.'_inv'});
			}
		}
		print $p_main . ",$p_cost,".int($p_inv).",$status\r\n";
	}
}

sub devrun_prod_bulkPriceChanges{
#-----------------------------------------
# Created on: 07/30/09  15:42:02 By  Roberto Barcenas
# Forms Involved: 
# Description : Arregla los costos en las tablas correspondientes
# Parameters : 

	my $file = $cfg{'path_upfiles'}.'products.txt';
	#print "Content-type: text/html\n\n";
	delete($in{'action'});
	if(-e "$file"){
		my ($query,$num);
		open(FILE,"<$file");
			PROD :while ($line = <FILE>){
				my (@ary) = split(/\t/, $line);
				$line =~ s/\r|\n//g;
				my $id_products = $ary[0];
				my $status 	=	$ary[13];
				$query = '';
				if($status eq 'On-Air'){
					for $i(0..4){
						($i>0) and ($num = $i);
						$query .= 'SPrice'.$num .'='.$ary[3+$i*2] . ' ,'; # Price
						$query .= 'SPrice'.$num .'Name=\''.$ary[4+$i*2] . '\' ,'; # Price Name
					}
					#print "UPDATE sl_products SET $query Status='$status' WHERE ID_products=$id_products<br><br>";
					$sth = &Do_SQL("UPDATE sl_products SET $query Status='$status' WHERE ID_products=$id_products");
					
				}else{
					#print "UPDATE sl_products SET Status='$status' WHERE ID_products=$id_products<br><br>";
					$sth = &Do_SQL("UPDATE sl_products SET Status='$status' WHERE ID_products=$id_products");
				}
				
				
		}
	}else{
		$va{'message'} = "No data to read from $file : $!";
		&dev_home;
		return;
	}
	$va{'message'} = 'ok';
	&dev_home;
	return;
}



sub devrun_phonemart_payments{
#-----------------------------------------
# Created on: 07/30/09  15:42:02 By  Roberto Barcenas
# Forms Involved: 
# Description : Crea
# Parameters : 

	my $pathfile = $cfg{'path_upfiles'};
	my $hits=0;
	my $fsource = 'phonemart_sosl.csv';
	my $fname   =	'direksys_sosl.csv';
	my $id_orders=0;	
	my $total_service=0;
	my $tpayments=0;
	my @db_cols = ("ID_customers","Address1","City","State","Zip");
	
	($in{'e'} eq '1') and ($fsource =~	s/sosl/usa/) and ($fname =~	s/sosl/usa/);
	($in{'e'} eq '2') and ($fsource =~	s/sosl/pr/) and ($fname =~	s/sosl/pr/);
	($in{'e'} eq '3') and ($fsource =~	s/sosl/training/) and ($fname =~	s/sosl/training/);
	($in{'e'} eq '4') and ($fsource =~	s/sosl/gts/) and ($fname =~	s/sosl/gts/);
	
	
	if(-e "$pathfile/$fsource"){
		print "Content-type: application/octetstream\n";
		print "Content-disposition: attachment; filename=$fname\n\n";
		print "Direksys Order,Customer ID, # Payments, Total Amount\r\n";
		
		if(open(FILE,"$pathfile/$fsource")){
			
			my ($sthc) = &Do_SQL("SELECT * FROM sl_customers WHERE FirstName = 'Internal';");
			my ($customer)	= $sthc->fetchrow_hashref();
			
			if($customer->{'ID_customers'} > 0){
			
				for my $i(0..$#db_cols){
					$query .= "$db_cols[$i]= '".$customer->{$db_cols[$i]}."', ";
				}
				$query .= "shp_Address1 = '$customer->{'Address1'}' ,shp_City = '$customer->{'City'}' ,shp_State = '$customer->{'State'}' , shp_Zip='$customer->{'Zip'}' , ";
				
				
				## Creating Order
				my ($stho) = &Do_SQL("INSERT INTO sl_orders SET $query shp_type=1, StatusPrd='None', PostedDate='2009-08-01', StatusPay='None', Status='Shipped', Date=Curdate(), Time=NOW(), ID_admin_users='1' ");
				$id_orders = $stho->{'mysql_insertid'};
				
				## Order created?
				if($id_orders > 0){
				#if(1){
					my $id_service = 600000000 +  &load_name('sl_services','Name','Phonemart Adjustment','ID_services');
					
					PROD :while ($record = <FILE>){
						my (@rec) = split(/\n/, $record);
						my (@ary) = split(/,/, $rec[$_]);
						my $id_phonemart 		= $ary[0];
						my $cc_name 				=	$ary[1];
						my $cc_number 			=	$ary[2];
						my $cc_cvn					=	$ary[3];
						my $cc_month				= $ary[4];
						my $cc_year					= $ary[5];
						my $cc_type					=	$ary[6];
						my $cc_phone				=	$ary[7];
						my $payment_date		= $ary[8];
						my $payment_amount	= $ary[9];
						$cc_month = '0'.$cc_month	if length($cc_month) == 1;
						
						## Creating Payments
						my ($sthp) = &Do_SQL("INSERT INTO sl_orders_payments SET ID_orders='$id_orders',Type='Credit-Card',PmtField1='$cc_type',PmtField2='$cc_name',PmtField3='$cc_number',PmtField4='".$cc_month.$cc_year."',PmtField5='$cc_cvn',PmtField6='$cc_phone',Reason='Sale',PostedDate='2009-08-01',AuthCode='',AuthDateTime='',Amount='$payment_amount',Paymentdate='$payment_date', Date=Curdate(),Time=CURTIME(),ID_admin_users='1'");
						$total_service += $payment_amount;
						$tpayments++;
					}
					## Creating Service
					my ($sthpr) = &Do_SQL("INSERT INTO sl_orders_products SET ID_products='$id_service',ID_orders='$id_orders',ID_packinglist=0,Quantity=1,SalePrice='$total_service',FP=1,Status='Active',PostedDate='2009-08-01',Date=CURDATE(),Time=CURTIME(),ID_admin_users='1'");
					&recalc_totals($id_orders);
					
					print "$id_orders,$customer->{'ID_customers'},$tpayments,$total_service\r\n";
					
				}else{
					print "Order failed to create"; 
				}
			}else{
				print "Unable to find customer";		
			}
		}else{
			print "Unable to open $pathfile/$fsource";
		}
	}
}			


sub devrun_weborders{
## -------------------------------------------------------- ##
#Last modified on 18 Jul 2011 11:52:29
#Last modified by: MCC C. Gabriel Varela S. :The user ids 5201,5202,5286,5289 from innovausa are added (puassance both, allnatpro refill, dreambody refill)

	my $fname = 'sosl_weborders.csv';
	
	($in{'e'} eq '1') and ($fname =~	s/sosl/usa/);
	($in{'e'} eq '2') and ($fname =~	s/sosl/pr/);
	($in{'e'} eq '3') and ($fname =~	s/sosl/training/);
	($in{'e'} eq '4') and ($fname =~	s/sosl/gts/);
	
	##my ($uids)= "5723,5724,5711,5712,4122,4322,4688,4689,5020,5021,5022,5023,5024,5025,5026,5027,5028,5029,5030,5031,5032,5033,5283,5284,5285,5288,5368,5369,5201,5202,5286,5289";
	print "Content-type: application/octetstream\n";
	print "Content-disposition: attachment; filename=$fname\n\n";
	#print "ID_orders,Date,ID_neworder,Product,COGS,OrderStatus,OrderNet,Tax,Shipping,OrderTotal,Payments\r\n";
	
	my $sth = &Do_SQL("SELECT
   Type,
   Ptype,
   ID_orders,
   OrderDate,
   ID_neworder,
   COGS,
   OrderStatus,
   OrderNet,
   OrderTax,
   Shipping,
   OrderTotal,
   ID_user
FROM
(

        SELECT
        'Preorder' AS Type,
        'COD' AS PType,
    zdev1_sl_preorders.ID_preorders AS ID_orders,
    zdev1_sl_preorders.Date AS OrderDate,
    ID_orders AS ID_neworder,
    zdev1_sl_preorders.Status AS OrderStatus,
    SUM(SalePrice-Discount)AS OrderNet,
    SUM(Tax)AS OrderTax,
    SUM(SalePrice-Discount+Tax+Shipping)AS OrderTotal,
    Shipping,
    SUM(Cost)AS COGS,
    zdev1_sl_preorders.ID_admin_users AS ID_user
        FROM
                zdev1_sl_preorders_products
        INNER JOIN
                (SELECT sum(Amount)as sumamount,ID_preorders 
                FROM zdev1_sl_preorders_payments
                WHERE Status NOT IN('Order Cancelled','Cancelled')
                group by ID_preorders)as zdev1_sl_preorders_payments
        ON
                zdev1_sl_preorders_products.ID_preorders = zdev1_sl_preorders_payments.ID_preorders
        INNER JOIN 
                zdev1_sl_preorders
        ON
                zdev1_sl_preorders.ID_preorders        =        zdev1_sl_preorders_products.ID_preorders 
                WHERE zdev1_sl_preorders.ID_admin_users IN(SELECT ID_admin_users FROM admin_users WHERE user_type IN('Internet','Recompras')) AND zdev1_sl_preorders.Date >= '2009-11-01' 
	      AND zdev1_sl_preorders.Status NOT IN ('System Error','Converted') 
                AND zdev1_sl_preorders_products.Status NOT IN('Cancelled','Inactive')
    GROUP BY zdev1_sl_preorders.ID_Preorders
UNION ALL

       SELECT
        'Order' AS Type,
        Ptype,
    sl_orders.ID_orders,
    sl_orders.Date AS OrderDate,
    'N/A' AS algo,
    sl_orders.Status AS OrderStatus,
    SUM(SalePrice-Discount)AS OrderNet,
    SUM(Tax)AS OrderTax,
    SUM(SalePrice-Discount+Tax+Shipping)AS OrderTotal,
    Shipping,
    SUM(Cost)AS COGS,
    sl_orders.ID_admin_users AS ID_user
        FROM
                sl_orders_products
        INNER JOIN
                (SELECT sum(Amount) as sumamount,ID_orders 
                FROM sl_orders_payments
                WHERE Status NOT IN('Order Cancelled','Cancelled')
                group by ID_orders)as sl_orders_payments
        ON
                sl_orders_products.ID_orders = sl_orders_payments.ID_orders
        INNER JOIN 
                sl_orders
        ON
                sl_orders.ID_orders =  sl_orders_products.ID_orders 
                WHERE 
               (sl_orders.ID_admin_users IN (SELECT ID_admin_users FROM admin_users WHERE user_type IN('Internet','Recompras'))
               OR
               sl_orders.ID_orders IN (SELECT sl_leads_calls.ID_orders FROM sl_leads_calls WHERE `DIDUS` = 8730500 AND sl_leads_calls.ID_orders>0)
               ) AND sl_orders.Date >= '2009-11-01'  AND sl_orders.Status != 'System Error'
                AND sl_orders_products.Status NOT IN('Cancelled','Inactive') and sl_orders_products.SalePrice>0
                AND 1 > (SELECT COUNT(*) FROM zdev1_sl_preorders WHERE ID_orders  =  sl_orders.ID_orders AND Status NOT IN ('System Error','Converted')) 
    GROUP BY sl_orders.ID_orders
)AS tmp
ORDER BY ID_orders,OrderDate,OrderStatus;");
									

### 
### Agregar Ptype
###
###


	print "Period,Product,PayType,ID_orders,Date,ID_neworder,Product,COGS,OrderStatus,OrderNet,Tax,Shipping,OrderTotal,Site,UserID,New COGS,Product Name\r\n";
	my ($q) = 2;
	my ($i,$pw);
	while(my($type,$ptype,$ido,$date,$neworder,$cogs,$status,$net,$tax,$shipping,$total,$id_user)	= $sth->fetchrow()){
	    #print "1)$type,2)$ptype,3)$ido,4)$date,5)$neworder,6)$cogs,7)$status,8)$net,11)$total,13)$id_user\r\n";
	    #next;
	    #my $cogs=0;
	    #(!$id_user) and ($id_user='xx');
	    my $sthp;
	    
	    if ($type eq 'Preorder'){
	    	$sthp = &Do_SQL("SELECT zdev1_sl_preorders_products.ID_products,Name FROM zdev1_sl_preorders_products INNER JOIN sl_products ON RIGHT(zdev1_sl_preorders_products.ID_products,6) = sl_products.ID_products  WHERE ID_preorders = $ido AND LEFT(zdev1_sl_preorders_products.ID_products,1) < 4 ORDER BY ID_preorders_products LIMIT 1;");
	    }else{
	    	$sthp = &Do_SQL("SELECT sl_orders_products.ID_products,Name FROM sl_orders_products INNER JOIN sl_products ON RIGHT(sl_orders_products.ID_products,6) = sl_products.ID_products  WHERE ID_orders = $ido AND LEFT(sl_orders_products.ID_products,1) < 4 ORDER BY ID_orders_products LIMIT 1;");
	    }
	    
	    my ($idp,$pname) = $sthp->fetchrow();
	    $pname =~ s/,/ /g;
	    # $cogs = load_sltvcost($idp);
	    
#	    if (&day_of_month($date) >= 1 and &day_of_month($date)<16 and $q==2){
#	    	## Principio 1er Quincena
#	    	$q = 1;
#	    	#print ",,,,,,$tot_net,,,$tot_total,,\r\n";
#	    	#print "\n\n\nID_orders,Date,ID_neworder,Product,COGS,OrderStatus,OrderNet,Tax,Shipping,OrderTotal,Payments\r\n";
#	    	$tot_net = 0;$tot_total= 0;
#	    }elsif (&day_of_month($date) >= 16 and $q==1){
#			## Principio 2er Quincena
#			$q = 2;
#			#print ",,,,,,$tot_net,,,$tot_total,,\r\n";
#			#print "\n\n\nID_orders,Date,ID_neworder,Product,COGS,OrderStatus,OrderNet,Tax,Shipping,OrderTotal,Payments\r\n";
#			$tot_net = 0;$tot_total= 0;
#		}
		$pw = weekperiod($date);
		$prodcat  = &productcat($pname);
		$prodname = &productcat_summ($pname);
		if ($id_user eq '5285'){
			$site = 'allnatpro';
		}elsif($id_user eq '5723'){
			$site = 'naturista';
		}elsif($id_user eq '5027'){
			$site = 'naturaliv';
		}elsif($id_user eq '5288'){
			$prodcat = 'dreambody';
			$prodname = 'dreambody';
			$site = 'lineal';
		}elsif($id_user eq '5711'){
			$site = 'amazon';
		}elsif($id_user eq '6396'){
			$site = 'ebay';
		}elsif($id_user eq '4688' or $id_user eq '4689' or $id_user eq '5711' or $prodcat =~ /^Unknown/){
			$site = 'innovashop';
		}else{
			if ($prodcat =~ /charakani|chardon|colageina|dreambody|diabestevia|fibra|moinsage|singivitis|sleggins|prostaliv|botas|rejuvital|puassance|algafit/i){
				$site = 'lineal';
			}else{
				$site = 'innovashop';
			}
		}
		## Fix Some errors
		if ($site eq 'lineal' and ($prodname =~ /Fitness|Others|Keraorganiq|Fajas/i)){
			$site = 'innovashop';
		}
		####
		
		if ((($total-$cogs)/4)>($net*0.1)){
			$fcogs = $cogs;
		}else{
			$fcogs = $total*0.6;  ### then 25% of Gross Margin = 10% of Price
		}
		($ptype eq 'Money Order') and ($ptype = 'COD');
		
		++$i;
	    #print "ID_orders,Date,ID_neworder,Product,COGS,OrderStatus,OrderNet,Tax,Shipping,OrderTotal,Payments\r\n";
	    if ($ido<500000){
	    	## Orders
	    	if ($status =~ /Shipped|Processed/){
				print "$pw,$prodcat,$ptype,$ido,$date,$neworder,$pname,$cogs,$status,$net,$tax,$shipping,$total,$site,$id_user,$fcogs,$prodname\r\n";
			#	$tot_total += $total;
			}else{
				print "$pw,$prodcat,$ptype,$ido,$date,$neworder,$pname,$cogs,$status,$net,0,0,0,$site,$id_user,$fcogs,$prodname\r\n";
			}
			$tot_net += $net;
			$last_ido = $ido;
		}else{
			#if ($last_ido<500000){
			#	print "\n\n\nID_orders,Date,ID_neworder,Product,COGS,OrderStatus,OrderNet,Tax,Shipping,OrderTotal,Payments\r\n";
			#	$tot_net = 0;$tot_total= 0;
			#}
			## PreOrders
	    	if ($status =~ /Paid/){
				print "$pw,$prodcat,$ptype,$ido,$date,$neworder,$pname,$cogs,$status,$net,$tax,$shipping,$total,$site,$id_user,$fcogs,$prodname\r\n";
				$tot_total += $total;
			}else{
				print "$pw,$prodcat,$ptype,$ido,$date,$neworder,$pname,$cogs,$status,$net,0,0,0,$site,$id_user,$fcogs,$prodname\r\n";
			}
			$tot_net += $net;
			
			$last_ido = $ido;
		}
	}
}


sub devrun_weborders_weekly{
## -------------------------------------------------------- ##
#Last modified on 18 Jul 2011 11:52:29
#Last modified by: MCC C. Gabriel Varela S. :The user ids 5201,5202,5286,5289 from innovausa are added (puassance both, allnatpro refill, dreambody refill)

	my $fname = 'sosl_weborders.csv';
	
	($in{'e'} eq '1') and ($fname =~	s/sosl/usa/);
	($in{'e'} eq '2') and ($fname =~	s/sosl/pr/);
	($in{'e'} eq '3') and ($fname =~	s/sosl/training/);
	($in{'e'} eq '4') and ($fname =~	s/sosl/gts/);
	
	##my ($uids)= "5723,5724,5711,5712,4122,4322,4688,4689,5020,5021,5022,5023,5024,5025,5026,5027,5028,5029,5030,5031,5032,5033,5283,5284,5285,5288,5368,5369,5201,5202,5286,5289";
	
	print "Content-type: application/octetstream\n";
	#print "Content-type: text/html\n\n";
	print "Content-disposition: attachment; filename=$fname\n\n";
	
	my $sth = &Do_SQL("SELECT
   Ptype,
   ID_orders,
   OrderDate,
   OrderStatus,
   OrderNet,
   OrderTax,
   Shipping,
   OrderTotal,
   COGS,
   ID_user
FROM
(

       SELECT
        Ptype,
    sl_orders.ID_orders,
    sl_orders.Date AS OrderDate,
    sl_orders.Status AS OrderStatus,
    SUM(SalePrice-Discount)AS OrderNet,
    SUM(Tax)AS OrderTax,
    SUM(SalePrice-Discount+Tax+Shipping)AS OrderTotal,
    Shipping,
    SUM(Cost)AS COGS,
    sl_orders.ID_admin_users AS ID_user
        FROM
                sl_orders_products
        INNER JOIN
                (SELECT sum(Amount) as sumamount,ID_orders 
                FROM sl_orders_payments
                WHERE Status NOT IN('Order Cancelled','Cancelled')
                group by ID_orders)as sl_orders_payments
        ON
                sl_orders_products.ID_orders = sl_orders_payments.ID_orders
        INNER JOIN 
                sl_orders
        ON
                sl_orders.ID_orders        =        sl_orders_products.ID_orders 
                WHERE sl_orders.ID_admin_users IN(SELECT ID_admin_users FROM admin_users WHERE user_type IN('Internet','Recompras')) AND sl_orders.Date >= '2009-11-01'  AND sl_orders.Status != 'System Error'
                AND sl_orders_products.Status NOT IN('Cancelled','Inactive') AND sl_orders_products.SalePrice>0
                AND sl_orders.Date >= '2014-01-01' 
    GROUP BY sl_orders.ID_orders
)AS tmp
ORDER BY ID_orders,OrderDate,OrderStatus;");
									

### 
### Agregar Ptype
###
###


	print "Period,PayType,ID_orders,Date,Product,OrderStatus,OrderNet,Tax,Shipping,OrderTotal,COGS,UserID,Product Name\r\n";
	my ($q) = 2;
	my ($i,$pw);
	while(my($ptype,$ido,$date,$status,$net,$tax,$shipping,$total,$cogs,$id_user)	= $sth->fetchrow()){
	    #print "1)$type,2)$ptype,3)$ido,4)$date,5)$neworder,6)$cogs,7)$status,8)$net,11)$total,13)$id_user\r\n";
	    #next;
	    #my $cogs=0;
	    #(!$id_user) and ($id_user='xx');
	    
	    my $sthp = &Do_SQL("SELECT sl_orders_products.ID_products,Name FROM sl_orders_products INNER JOIN sl_products ON RIGHT(sl_orders_products.ID_products,6) = sl_products.ID_products  WHERE ID_orders = $ido AND LEFT(sl_orders_products.ID_products,1) < 4 ORDER BY ID_orders_products LIMIT 1;");
	    my ($idp,$pname) = $sthp->fetchrow();
	    
	    $pname =~ s/,/ /g;

		$pw = &weeknum($date);

		$prodname = &productcat_summ($pname);

		($ptype eq 'Money Order') and ($ptype = 'COD');
		
		++$i;
    	## Orders
    	if ($status =~ /Shipped|Processed/){
			print "$pw,$ptype,$ido,$date,$pname,$status,$net,$tax,$shipping,$total,$cogs,$id_user,$prodname\r\n";
		#	$tot_total += $total;
		}else{
			print "$pw,$ptype,$ido,$date,$pname,$status,$net,0,0,0,0,$id_user,$prodname\r\n";
		}
		$tot_net += $net;
		$last_ido = $ido;
	}
}

sub devrun_weborders_prod{
## -------------------------------------------------------- ##

	my $fname = 'sosl_weborders.csv';
	
	($in{'e'} eq '1') and ($fname =~	s/sosl/usa/);
	($in{'e'} eq '2') and ($fname =~	s/sosl/pr/);
	($in{'e'} eq '3') and ($fname =~	s/sosl/training/);
	($in{'e'} eq '4') and ($fname =~	s/sosl/gts/);
	
	my ($uids)= "5723,5724,5711,5712,4122,4322,4688,4689,5020,5021,5022,5023,5024,5025,5026,5027,5028,5029,5030,5031,5032,5033,5283,5284,5285,5288";
	print "Content-type: application/octetstream\n";
	print "Content-disposition: attachment; filename=$fname\n\n";
	#print "ID_orders,Date,ID_neworder,Product,COGS,OrderStatus,OrderNet,Tax,Shipping,OrderTotal,Payments\r\n";
	
	my $sth = &Do_SQL("SELECT
   Type,
   Ptype,
   ID_orders,
   Date,
   ID_neworder,
   COGS,
   OrderStatus,
   OrderNet,
   OrderTax,
   Shipping,
   OrderTotal,
   ID_user
FROM
(

        SELECT
        'Preorder' AS Type,
        'COD' AS PType,
    zdev1_sl_preorders.ID_preorders AS ID_orders,
    zdev1_sl_preorders.Date AS Date,
    ID_orders AS ID_neworder,
    zdev1_sl_preorders.Status AS OrderStatus,
    SUM(SalePrice-Discount)AS OrderNet,
    SUM(Tax)AS OrderTax,
    SUM(SalePrice-Discount+Tax+Shipping)AS OrderTotal,
    Shipping,
    SUM(Cost)AS COGS,
    zdev1_sl_preorders.ID_admin_users AS ID_user
        FROM
                zdev1_sl_preorders_products
        INNER JOIN
                (SELECT sum(Amount)as sumamount,ID_preorders 
                FROM zdev1_sl_preorders_payments
                WHERE Status NOT IN('Order Cancelled','Cancelled')
                group by ID_preorders)as zdev1_sl_preorders_payments
        ON
                zdev1_sl_preorders_products.ID_preorders = zdev1_sl_preorders_payments.ID_preorders
        INNER JOIN 
                zdev1_sl_preorders
        ON
                zdev1_sl_preorders.ID_preorders        =        zdev1_sl_preorders_products.ID_preorders 
                WHERE zdev1_sl_preorders.ID_admin_users IN($uids) AND zdev1_sl_preorders.Date >= '2009-11-01' 
	      AND zdev1_sl_preorders.Status NOT IN ('System Error','Converted') 
                AND zdev1_sl_preorders_products.Status NOT IN('Cancelled','Inactive')
    GROUP BY zdev1_sl_preorders.ID_Preorders
UNION ALL

       SELECT
        'Order' AS Type,
        Ptype,
    sl_orders.ID_orders,
    sl_orders.Date AS OrderDate,
    'N/A' AS algo,
    sl_orders.Status AS OrderStatus,
    SUM(SalePrice-Discount)AS OrderNet,
    SUM(Tax)AS OrderTax,
    SUM(SalePrice-Discount+Tax+Shipping)AS OrderTotal,
    Shipping,
    SUM(Cost)AS COGS,
    sl_orders.ID_admin_users AS ID_user
        FROM
                sl_orders_products
        INNER JOIN
                (SELECT sum(Amount) as sumamount,ID_orders 
                FROM sl_orders_payments
                WHERE Status NOT IN('Order Cancelled','Cancelled')
                group by ID_orders)as sl_orders_payments
        ON
                sl_orders_products.ID_orders = sl_orders_payments.ID_orders
        INNER JOIN 
                sl_orders
        ON
                sl_orders.ID_orders        =        sl_orders_products.ID_orders 
                WHERE sl_orders.ID_admin_users IN($uids) AND sl_orders.Date >= '2009-11-01'  AND sl_orders.Status != 'System Error'
                AND sl_orders_products.Status NOT IN('Cancelled','Inactive') and sl_orders_products.SalePrice>0
                AND 1 > (SELECT COUNT(*) FROM zdev1_sl_preorders WHERE ID_orders  =  sl_orders.ID_orders AND Status NOT IN ('System Error','Converted')) 
    GROUP BY sl_orders.ID_orders
)AS tmp
ORDER BY ID_orders,Date,OrderStatus;");
									

### 
### Agregar Ptype
###
###


	print "Period,Product,PayType,ID_orders,Date,ID_neworder,Product,COGS,OrderStatus,OrderNet,Tax,Shipping,OrderTotal,UserID\r\n";
	my ($q) = 2;
	my ($i,$pw);
	while(my($type,$ptype,$ido,$date,$neworder,$cogs,$status,$net,$tax,$shipping,$total,$id_user)	= $sth->fetchrow()){
	    my $prefix = '';    
	    $prefix = 'pre'    if    $type    eq    'Preorder';
	    #print "1)$type,2)$ptype,3)$ido,4)$date,5)$neworder,6)$cogs,7)$status,8)$net,11)$total,13)$id_user\r\n";
	    #next;
	    #my $cogs=0;
	    #(!$id_user) and ($id_user='xx');
	    
	    my $sthp = &Do_SQL("SELECT sl_".$prefix."orders_products.ID_products,Name FROM sl_".$prefix."orders_products INNER JOIN sl_products ON RIGHT(sl_".$prefix."orders_products.ID_products,6) = sl_products.ID_products  WHERE ID_".$prefix."orders = $ido AND LEFT(sl_".$prefix."orders_products.ID_products,1) < 4 ORDER BY ID_".$prefix."orders_products LIMIT 1;");
	    my ($idp,$pname) = $sthp->fetchrow();
	    # $cogs = load_sltvcost($idp);
	    
#	    if (&day_of_month($date) >= 1 and &day_of_month($date)<16 and $q==2){
#	    	## Principio 1er Quincena
#	    	$q = 1;
#	    	#print ",,,,,,$tot_net,,,$tot_total,,\r\n";
#	    	#print "\n\n\nID_orders,Date,ID_neworder,Product,COGS,OrderStatus,OrderNet,Tax,Shipping,OrderTotal,Payments\r\n";
#	    	$tot_net = 0;$tot_total= 0;
#	    }elsif (&day_of_month($date) >= 16 and $q==1){
#			## Principio 2er Quincena
#			$q = 2;
#			#print ",,,,,,$tot_net,,,$tot_total,,\r\n";
#			#print "\n\n\nID_orders,Date,ID_neworder,Product,COGS,OrderStatus,OrderNet,Tax,Shipping,OrderTotal,Payments\r\n";
#			$tot_net = 0;$tot_total= 0;
#		}
		$pw = qperiod($date);
		$prodcat = &productcat_summ($pname);
		if ($id_user eq '5723' or $id_user eq '5724'){
			$id_user = 'naturista';
		}elsif($id_user eq '5285'){
			$id_user = 'allnatpro';
		}elsif($id_user eq '5027'){
			$id_user = 'naturaliv';
		}elsif($id_user eq '4688' or $id_user eq '4689' or $id_user eq '5711'  or $prodcat =~ /^Unknown/){
			$id_user = 'innovashop';
		}elsif($id_user eq '5711'){
			$site = 'amazon';
		}elsif($id_user eq '6396'){
			$site = 'ebay';
		}else{
			$id_user = 'lineal';
		}
		++$i;
	    #print "ID_orders,Date,ID_neworder,Product,COGS,OrderStatus,OrderNet,Tax,Shipping,OrderTotal,Payments\r\n";
	    if ($ido<500000){
	    	## Orders
	    	if ($status =~ /Shipped|Processed/){
				print "$pw,$prodcat,$ptype,$ido,$date,$neworder,$pname,$cogs,$status,$net,$tax,$shipping,$total,$id_user\r\n";
			#	$tot_total += $total;
			}else{
				print "$pw,$prodcat,$ptype,$ido,$date,$neworder,$pname,$cogs,$status,$net,0,0,0,$id_user\r\n";
			}
			$tot_net += $net;
			$last_ido = $ido;
		}else{
			#if ($last_ido<500000){
			#	print "\n\n\nID_orders,Date,ID_neworder,Product,COGS,OrderStatus,OrderNet,Tax,Shipping,OrderTotal,Payments\r\n";
			#	$tot_net = 0;$tot_total= 0;
			#}
			## PreOrders
	    	if ($status =~ /Paid/){
				print "$pw,$prodcat,$ptype,$ido,$date,$neworder,$pname,$cogs,$status,$net,$tax,$shipping,$total,$id_user\r\n";
				$tot_total += $total;
			}else{
				print "$pw,$prodcat,$ptype,$ido,$date,$neworder,$pname,$cogs,$status,$net,0,0,0,$id_user\r\n";
			}
			$tot_net += $net;
			
			$last_ido = $ido;
		}
	}
}


sub devrun_webpricelist{
## -------------------------------------------------------- ##

	my $fname = 'sosl_webpricelist.csv';
	
	($in{'e'} eq '1') and ($fname =~	s/sosl/usa/);
	($in{'e'} eq '2') and ($fname =~	s/sosl/pr/);
	($in{'e'} eq '3') and ($fname =~	s/sosl/training/);
	($in{'e'} eq '4') and ($fname =~	s/sosl/gts/);
	
#print "Content-type: text/html\n\n";
	print "Content-type: application/octetstream\n";
	#print "Content-type: application/vnd.ms-excel\n";
	print "Content-disposition: attachment; filename=$fname\n\n";
	#print "ID_orders,Date,ID_neworder,Product,COGS,OrderStatus,OrderNet,Tax,Shipping,OrderTotal,Payments\r\n";
	
	my $sth = &Do_SQL("SELECT ID_products,sl_products.Name,Model,Sprice,Shipping,FPPrice,FlexiPago
			from (Select 
			if(not isnull(sl_products_prior.SPrice)and sl_products_prior.SPrice!=0,sl_products_prior.SPrice,sl_products.SPrice)as SPrice,
			if(not isnull(sl_products_prior.MemberPrice)and sl_products_prior.MemberPrice > 0,sl_products_prior.MemberPrice,sl_products.MemberPrice)as MemberPrice,
			if(not isnull(sl_products_prior.Status)and sl_products_prior.Status!='',sl_products_prior.Status,sl_products.Status) as Status,
			if(not isnull(sl_products_w.Title)and sl_products_w.Title!='',sl_products_w.Title,if(not isnull(sl_categories.Title),sl_categories.Title,'Other'))as Title,
			sl_products.ID_products,
			if(not isnull(sl_products_prior.Name)and sl_products_prior.Name!='',sl_products_prior.Name,sl_products.Name) as Name,
			if(not isnull(sl_products_w.Name),sl_products_w.Name,'Other') as Name_link,
			if(not isnull(sl_products_prior.Model)and sl_products_prior.Model!='',sl_products_prior.Model,sl_products.Model) as Model,
			if(not isnull(sl_products_prior.SmallDescription)and sl_products_prior.SmallDescription!='',sl_products_prior.SmallDescription,sl_products.SmallDescription) as SmallDescription,
			if(not isnull(sl_products_prior.Description)and sl_products_prior.Description!='',sl_products_prior.Description,sl_products.Description) as Description,
			if(not isnull(sl_products_prior.Weight)and sl_products_prior.Weight!=0,sl_products_prior.Weight,sl_products.Weight) as Weight,
			if(not isnull(sl_products_prior.SizeW)and sl_products_prior.SizeW!=0 and sl_products_prior.SizeW!='',sl_products_prior.SizeW,sl_products.SizeW) as SizeW,
			if(not isnull(sl_products_prior.SizeH)and sl_products_prior.SizeH!=0 and sl_products_prior.SizeH!='',sl_products_prior.SizeH,sl_products.SizeH) as SizeH,
			if(not isnull(sl_products_prior.SizeL)and sl_products_prior.SizeL!=0 and sl_products_prior.SizeL!='',sl_products_prior.SizeL,sl_products.SizeL) as SizeL,
			if(not isnull(sl_products_prior.Flexipago)and sl_products_prior.Flexipago!=0,sl_products_prior.Flexipago,sl_products.Flexipago) as Flexipago,
			if(not isnull(sl_products_prior.FPPrice)and sl_products_prior.FPPrice!=0,sl_products_prior.FPPrice,sl_products.FPPrice) as FPPrice,
			if(not isnull(sl_products_prior.PayType)and sl_products_prior.PayType!='',sl_products_prior.PayType,sl_products.PayType) as PayType,
			if(not isnull(sl_products_prior.edt)and sl_products_prior.edt!=0 and sl_products_prior.edt!='',sl_products_prior.edt,sl_products.edt) as edt,
			if(not isnull(sl_products_prior.ID_packingopts)and sl_products_prior.ID_packingopts!=0 and sl_products_prior.ID_packingopts!='',sl_products_prior.ID_packingopts,sl_products.ID_packingopts) as ID_packingopts,
			if(not isnull(sl_products_prior.Downpayment)and sl_products_prior.Downpayment!=0,sl_products_prior.Downpayment,sl_products.Downpayment) as Downpayment,
			if(not isnull(sl_products_prior.ChoiceName1)and sl_products_prior.ChoiceName1!='',sl_products_prior.ChoiceName1,sl_products.ChoiceName1) as ChoiceName1,
			if(not isnull(sl_products_prior.ChoiceName2)and sl_products_prior.ChoiceName2!='',sl_products_prior.ChoiceName2,sl_products.ChoiceName2) as ChoiceName2,
			if(not isnull(sl_products_prior.ChoiceName3)and sl_products_prior.ChoiceName3!='',sl_products_prior.ChoiceName3,sl_products.ChoiceName3) as ChoiceName3,
			if(not isnull(sl_products_prior.ChoiceName4)and sl_products_prior.ChoiceName4!='',sl_products_prior.ChoiceName4,sl_products.ChoiceName4) as ChoiceName4,
			if(not isnull(sl_products_prior.web_available)and sl_products_prior.web_available!='',sl_products_prior.web_available,sl_products.web_available) as web_available,
			keyword
			from sl_products
			left join sl_products_prior on(sl_products.ID_products=sl_products_prior.ID_products)
			inner join sl_products_w on(sl_products.ID_products=sl_products_w.ID_products)
			left join sl_products_categories on(sl_products.ID_products=sl_products_categories.ID_products)
			left join sl_categories on (sl_products_categories.ID_categories=sl_categories.ID_categories)
			where ((sl_products.Status='On-Air' AND sl_products.web_available='Yes') OR sl_products.Status='Web Only') ORDER BY sl_products.ID_products)as sl_products
			inner join sl_packingopts on sl_products.ID_packingopts=sl_packingopts.ID_packingopts;");
									
#
### 
### Agregar Ptype
###
###


	print "ID_products,Name,Model,Sprice,Shipping,FPPrice,FlexiPago,Cost,On-Hand,Status\r\n";
	my ($q) = 2;
	my ($i,$pw,$p_add,$p_main,$p_cost,$p_inv);
	while(my($id_products,$name,$model,$sprice,$shipping,$fpprice,$flexipago)	= $sth->fetchrow()){
	    my $prefix = '';
	    $name =~ s/,/ /g;
	    $model =~ s/,/ /g; 
	    $prefix = 'pre'    if    $type    eq    'Preorder';
	    #print "1)$type,2)$ptype,3)$ido,4)$date,5)$neworder,6)$cogs,7)$status,8)$net,11)$total,13)$id_user\r\n";
	    #next;
	    #my $cogs=0;
	    #(!$id_user) and ($id_user='xx');
	    my (%prods,$p_skus,$inv);
	    my $sthc = &Do_SQL("SELECT ID_sku_products,ID_parts,Qty FROM `sl_skus_parts` WHERE `ID_sku_products` LIKE '%$id_products'");
		while(my($id_prod,$id_sku,$qty) = $sthc->fetchrow()){
			$prods{$id_prod.'_cost'} += $qty*load_sltvcost(400000000+$id_sku);
		    $inv = calc_parts_inventory(400000000+$id_sku)/$qty;
		    if ($prods{$id_prod.'_inv'}==0 or $prods{$id_prod.'_inv'}> $inv){
		    	$prods{$id_prod.'_inv'} = $inv;
		    }
		}
		$p_add = '';$p_cost = 0;$p_inv = 0;
		$p_main = " ".(100000000+$id_products).",$name,$model,$sprice,$shipping,$fpprice,$flexipago";
		#print "$id_products,$name,$model,$sprice,$shipping,$fpprice,$flexipago\r\n";
		foreach $key (keys %prods){
			if ($key =~ /(\d+)_cost/){
				$id = $1;
				$n = &load_db_names('sl_skus','ID_sku_products',$id,'[choice1],[choice2],[choice3],[choice4]');
				$n =~ s/,,|,$//g; $n =~ s/,/-/g;
				(!$n) and ($n = '---');
				$p_add .= ",($id)$n,,,,,,$prods{$id.'_cost'},$prods{$id.'_inv'},".&load_name('sl_skus','ID_sku_products',$id,'Status')."\r\n";
				($p_cost<$prods{$id.'_cost'}) and ($p_cost=$prods{$id.'_cost'});
				($p_inv<$prods{$id.'_inv'}) and ($p_inv=$prods{$id.'_inv'});
			}
		}
		print $p_main . ",$p_cost,$p_inv\r\n". $p_add;
	}
}


sub devrun_cpc {
# --------------------------------------------------------
	print "Content-type: text/html\n\n";
	my (@ary,$d,$g);
	$from = '2010-04-01';
	$to   = '2010-06-15';
	$min  = 5;
	
	&connect_db_w($cfg{'dbi_db_pbx'},$cfg{'dbi_host_pbx'},$cfg{'dbi_user_pbx'},$cfg{'dbi_pw_pbx'});
#	#print "SELECT accountcode, (HOUR(calldate)*2+if(MINUTE(calldate)>30,1,0))AS horanum, IF(DAYOFWEEK(calldate) BETWEEN 2 and 6,'Lu-Vie','Sa-Do')AS dayweek, COUNT(DISTINCT(src)) as Cantidad FROM cdr WHERE DATE(calldate) BETWEEN '$from' AND '$to' GROUP BY accountcode,horanum,dayweek ORDER BY Cantidad DESC ";
#	my ($sth) = &Do_SQL("SELECT accountcode, (HOUR(calldate)*2+if(MINUTE(calldate)>30,1,0))AS horanum, IF(DAYOFWEEK(calldate) BETWEEN 2 and 6,'Lu-Vie','Sa-Do')AS dayweek,COUNT(DISTINCT(src)) as Cantidad FROM cdr WHERE DATE(calldate) BETWEEN '$from' AND '$to' GROUP BY accountcode,horanum,dayweek ORDER BY Cantidad DESC ",1);
#	while($rec=$sth->fetchrow_hashref){
#		print "$rec->{'accountcode'}, $rec->{'horanum'}, $rec->{'dayweek'}, $rec->{'Cantidad'}<br>";
#		if ($rec->{'Cantidad'}>=$min){
#			$tmp{$rec->{'accountcode'}.'_horanum'}=$rec->{'horanum'};
#			$tmp{$rec->{'accountcode'}.'_dayweek'}=$rec->{'dayweek'};
#			push(@dids,$rec->{'accountcode'});
#		}
#	}
	#for (0..$#dids){
		$did = 1574000;
		my ($sth) = &Do_SQL("
					SELECT 
						DATE(calldate) AS d,
						(HOUR(calldate)*2+if(MINUTE(calldate)>30,1,0)) AS horanum, 
						IF(DAYOFWEEK(calldate) BETWEEN 2 and 6,'Lu-Vie','Sa-Do')AS dayweek,
						COUNT(DISTINCT(src)) as Cantidad
						
						FROM cdr WHERE DATE(calldate) BETWEEN '2010-04-01' AND '2010-06-15'  and accountcode=1574000
						
						GROUP BY horanum,DATE(calldate)
						ORDER BY horanum		
		",1);
		while($rec=$sth->fetchrow_hashref){	
			if ($rec->{'Cantidad'}>5){
				print "$did, $rec->{'d'}, $rec->{'horanum'}, $rec->{'dayweek'}, $rec->{'Cantidad'}<br>";
			}
		
		}
	#}


	print "done : " .($#ary+1)
}


sub devrun_add_mediadids{
# --------------------------------------------------------
# Forms Involved: 
# Created on: 23 Feb 2010 10:36:10
# Author: MCC C. Gabriel Varela S.
# Description :   
# Parameters :
&connect_db;
	#Se conecta a S7
	&connect_db_w($cfg{'dbi_db_pbx'},$cfg{'dbi_host_pbx'},$cfg{'dbi_user_pbx'},$cfg{'dbi_pw_pbx'});
	#Obtiene la información de sl_numbers
	my $sth=&Do_SQL("Select * from sl_numbers;",1);  # Usa la conexion DBH1
	#Recorre la información
	while(my $rec=$sth->fetchrow_hashref){
		#Si es innovausa escribe en innovausa
		if($rec->{'grupo'} eq 'US'){
			&Do_SQL("insert ignore into innovausa.sl_mediadids set num800='$rec->{'num800'}', didmx='$rec->{'didmx'}', didusa='$rec->{'didusa'}', grupo='$rec->{'grupo'}',product='$rec->{'product'}',assignto='$rec->{'assignto'}',DMA='$rec->{'DMA'}',channel='$rec->{'channel'}',Status='Active',Date=curdate(),Time=curtime(),ID_admin_users='$rec->{'ID_admin_users'}';");
		}
	}
	
	#fin
	$va{'message'}="The DID records have been added.";
	print "Content-type: text/html\n\n";
	print &build_page('home.html');
}


sub devrun_updatestatus {
# --------------------------------------------------------
	print "Content-type: text/html\n\n";
	my ($from_date) = '2012-04-30';
	my ($to_date)   = "2012-04-30";
	my ($err,$p1calls,$p2calls,$p3calls,$tot);
	#'Programado','Transmitido','Auto Transmitido','NoTX: Pendiente','NoTX: Credito','NoTX: No Facturado','Aircheck','Pending Aircheck','System Error','Station Error'
	#print "SELECT *	FROM sl_mediacontracts 	WHERE ESTDay BETWEEN '$from_date' AND '$to_date';";
	my $sth = &Do_SQL("SELECT *	FROM sl_mediacontracts WHERE ESTDay BETWEEN '$from_date' AND '$to_date' AND Destinationdid<9990;");
	while ($contract = $sth->fetchrow_hashref){
		++$tot;
		if ($contract->{'Cost'}<100 and $contract->{'Status'} !~ /Auto Transmitido|NoTX|Error/){
			print $contract->{'ID_mediacontracts'} . " - " . $contract->{'Status'}. " Calls:$p1calls / Cost:".&format_price($contract->{'Cost'})." -> Auto<br>";
			++$err;
		}elsif($contract->{'Cost'}>=100){
			
			$sth2 = &Do_SQL("SELECT 
				SUM(IF(TIMESTAMPDIFF(MINUTE, '$contract->{'ESTDay'} $contract->{'ESTTime'}', CONCAT(Date, ' ', Time) ) BETWEEN -30 AND 90,1,0))AS P1, 
				SUM(IF(TIMESTAMPDIFF(MINUTE, '$contract->{'ESTDay'} $contract->{'ESTTime'}', CONCAT(Date, ' ', Time) ) BETWEEN 91 AND 360,1,0))AS P2, 
				SUM(IF(TIMESTAMPDIFF(MINUTE, '$contract->{'ESTDay'} $contract->{'ESTTime'}', CONCAT(Date, ' ', Time) ) > 360,1,0))AS P3
				FROM sl_leads_calls WHERE ID_mediacontracts = '$contract->{'ID_mediacontracts'}' ");
				($p1calls,$p2calls,$p3calls)=$sth2->fetchrow();
	
			if ($p1calls>0){
				if ($contract->{'Cost'}/$p1calls > 50 and $p1calls < 4 and $contract->{'Status'} !~ /NoTX: Pendiente|NoTX: Credito|NoTX: No Facturado/){
					print $contract->{'ID_mediacontracts'} . " - " . $contract->{'Status'}. " Calls:$p1calls / Cost:".&format_price($contract->{'Cost'})." -> NoTX<br>";
					++$err;
				}elsif(($contract->{'Cost'}/$p1calls <= 50 or $p1calls >= 4) and $contract->{'Status'} ne 'Transmitido'){
					print $contract->{'ID_mediacontracts'} . " - " . $contract->{'Status'}. " Calls:$p1calls / Cost:".&format_price($contract->{'Cost'})." -> Transmitido<br>";
					++$err;
				}
			}elsif ($contract->{'Status'} !~ /NoTX: Pendiente|NoTX: Credito|NoTX: No Facturado/){
				print $contract->{'ID_mediacontracts'} . " - " . $contract->{'Status'}. " Calls:$p1calls / Cost:".&format_price($contract->{'Cost'})." -> NoTX<br>";
				++$err;
			}
		}	
	}
	if ($err>0){
		print "% errores  : $err/$tot (". (int($err/$tot*100)) ."%)\n";
	}else{
		print "No errors\n";
	}
}
sub devrun_updateleads {
# --------------------------------------------------------
	my ($from_date) = "2011-01-01";
	my ($from_time) = "00:00:00";
	my ($to_date) = "2012-05-01";
	my ($to_time) = "23:59:59";
	
	print "Content-type: text/html\n\n";
	my $sth = &Do_SQL("TRUNCATE TABLE  `sl_leads_calls`");
	my $sth = &Do_SQL("TRUNCATE TABLE  `sl_leads`");
	
	## Local Overwrite
	$cfg{'dbi_db_pbx'}   = 'asteriskcdrdb';
	$cfg{'dbi_host_pbx'} = '127.0.0.1';
	$cfg{'dbi_user_pbx'} = 'root';
	$cfg{'dbi_pw_pbx'}   = 'nowsee123';
	&connect_db_w($cfg{'dbi_db_pbx'},$cfg{'dbi_host_pbx'},$cfg{'dbi_user_pbx'},$cfg{'dbi_pw_pbx'});	
	my $sth = &Do_SQL("SELECT * FROM cdr WHERE src>100000 AND calldate BETWEEN '$from_date $from_time' AND '$to_date $to_time' AND (dstchannel LIKE 'SIP%' OR dstchannel like 'IAX2/vixicom%' OR dstchannel like 'IAX2/s8server%' OR dstchannel like 'IAX2/mtyserver%' OR lastapp='Queue' OR ((lastapp='BackGround' OR lastapp='Playback') AND (lastdata like '%flash%' OR lastdata like '%AUDIOCALLCENTER%')) OR (lastapp = 'Hangup' AND dcontext='app-blackhole')) and accountcode>0",1);
	CDR: while ($cdr = $sth->fetchrow_hashref){
		
		if ($cdr->{'dcontext'} eq 'from-lost'){
			$dest = 'Drop';
		}elsif($cdr->{'dcontext'} eq 'app-blackhole'){
			$dest = 'IVR-blackhole';
		}elsif($cdr->{'dcontext'} =~ /app-announcement/i){
			$dest = 'IVR-flash';	
		}elsif($cdr->{'accountcode'} eq '2542200' or $cdr->{'dstchannel'} =~ /200\.57\.93\.19/i){
			$dest = 'ATC';
		}elsif($cdr->{'accountcode'} =~ /2530800|2238800/ or $cdr->{'src'} =~ /3057286384|7862004423|3057286264/ or $cdr->{'dstchannel'} =~ /67\.107\.189\.61/ or $cdr->{'channel'} =~ /918664924670/){
			$dest = 'Local'; #2238800 Main FAX / 2530800 Main Local / 67.107.189.61 Cascorp / 918664924670 Telemercadeo
			next CDR;
		}elsif($cdr->{'dstchannel'} =~ /vixicom/i){
			$dest = 'Vixicom';
		}elsif($cdr->{'dstchannel'} =~ /mtyserver|187\.141\.248\.227/i){
			$dest = 'Monterey';
		}elsif($cdr->{'dstchannel'} =~ /Nuxiba|200\.57\.93\.20|s8server|Local\/\d{3}\@|SIP\/\d{3}/i or $cdr->{'lastapp'} =~ /Queue/i){
			$dest = 'Mixcoac';
		}else{
			$dest = 'Others';
			print $cdr->{'calldate'} . " " . $cdr->{'src'} ." ". $cdr->{'dstchannel'}."<br>";
			++$i;
		}
		#print $cdr->{'dstchannel'} . " - dcontext: " . $cdr->{'dcontext'} . " => $dest<br>";
		
		# sl_leads
		my $sth2 = &Do_SQL("INSERT IGNORE INTO sl_leads SET ID_leads='$cdr->{'src'}', Status='Active',Date=DATE('$cdr->{'calldate'}'), Time=TIME('$cdr->{'calldate'}'), ID_admin_users=1;");

		# sl_leads_calls
		my $sth2 = &Do_SQL("INSERT IGNORE INTO sl_leads_calls SET ID_leads='$cdr->{'src'}',IO='In',	DIDUS='$cdr->{'accountcode'}',Duration='$cdr->{'duration'}',Destination='$dest', Date=DATE('$cdr->{'calldate'}'), Time=TIME('$cdr->{'calldate'}'), ID_admin_users=1;");
	}
	print "tot:". $i;
	#while ($contract = $sth->fetchrow_hashref){

}



sub devrun_checkleads {
# --------------------------------------------------------
	my ($x,$t);
	
	print "Content-type: text/html\n\n";
	print "<pre>";
	
	## Leads Vs MediaData
	my $sth = &Do_SQL("SELECT sl_leads_calls.ID_mediacontracts,COUNT(DISTINCT(ID_leads)) AS calls,SUM(IF(ID_orders>0,1,0)) AS Ords FROM sl_leads_calls LEFT JOIN sl_mediacontracts ON sl_mediacontracts.ID_mediacontracts=sl_leads_calls.ID_mediacontracts WHERE sl_leads_calls.ID_mediacontracts>0  AND DestinationDID<9990 GROUP BY sl_leads_calls.ID_mediacontracts");
	while (($id_cont,$calls,$orders) = $sth->fetchrow_array){
		++$t;
		# Orders
		my $sth2 = &Do_SQL("SELECT COUNT(*) FROM sl_orders WHERE ID_mediacontracts=$id_cont");
		$data_orders = $sth2->fetchrow;

		if ($orders ne $data_orders){
			my $sth2 = &Do_SQL("SELECT * FROM sl_mediacontracts WHERE ID_mediacontracts=$id_cont");
			$contract = $sth2->fetchrow_hashref;
			
			my $sth2 = &Do_SQL("SELECT DATE_SUB(CONCAT(ESTDay, ' ', ESTTime),INTERVAL 1 MINUTE)  FROM sl_mediacontracts WHERE DestinationDID=$contract->{'DestinationDID'} AND Status IN(". $cfg{'contract_valid_status'} .") AND TIMESTAMPDIFF(MINUTE,'$contract->{'ESTDay'} $contract->{'ESTTime'}',CONCAT(ESTDay, ' ', ESTTime)) BETWEEN 1 AND $cfg{'contract_nextmin'} ORDER BY DATE_SUB(CONCAT(ESTDay, ' ', ESTTime),INTERVAL 30 MINUTE) ASC LIMIT 0,1");
			$nextcontract = $sth2->fetchrow;
			if (!$nextcontract){
				## No Next Contract, then end in 7 days
				$nextcontract = &sqldate_plus($contract->{'ESTDay'},7). ' '. $contract->{'ESTTime'};
			}
			
			print "$id_cont : $orders <> $data_orders / NextContract : $nextcontract \n";
			++$o;
		}
	}
	## Checking DID Leads_calls vs Orders
	my $sth = &Do_SQL("SELECT COUNT(*) FROM sl_leads_calls LEFT JOIN sl_orders ON sl_orders.ID_orders=sl_leads_calls.ID_orders WHERE sl_leads_calls.ID_orders>0 AND DIDUS<>DIDS7");
	$error_did1 = $sth->fetchrow;
	
	
	## Checking DID  Contracts vs Orders
	my $sth = &Do_SQL("SELECT ID_orders,sl_mediacontracts.ID_mediacontracts,DNIS, DestinationDID FROM sl_orders LEFT JOIN sl_mediacontracts ON sl_orders.ID_mediacontracts = sl_mediacontracts.ID_mediacontracts WHERE sl_orders.ID_mediacontracts >0 AND DestinationDID<9990 AND DNIS<>DestinationDID");
	while (($order,$id_cont,$dnis,$destdid) = $sth->fetchrow_array){
		
		my $sth2 = &Do_SQL("SELECT * FROM sl_mediacontracts WHERE ID_mediacontracts=$id_cont");
		$contract = $sth2->fetchrow_hashref;
		my $sth2 = &Do_SQL("SELECT DATE_SUB(CONCAT(ESTDay, ' ', ESTTime),INTERVAL 1 MINUTE)  FROM sl_mediacontracts WHERE DestinationDID=$contract->{'DestinationDID'} AND Status IN(". $cfg{'contract_valid_status'} .") AND TIMESTAMPDIFF(MINUTE,'$contract->{'ESTDay'} $contract->{'ESTTime'}',CONCAT(ESTDay, ' ', ESTTime)) BETWEEN 1 AND $cfg{'contract_nextmin'} ORDER BY DATE_SUB(CONCAT(ESTDay, ' ', ESTTime),INTERVAL 30 MINUTE) ASC LIMIT 0,1");
		$nextcontract = $sth2->fetchrow;
		if (!$nextcontract){
			## No Next Contract, then end in 7 days
			$nextcontract = &sqldate_plus($contract->{'ESTDay'},7). ' '. $contract->{'ESTTime'};
		}
		
		print "Order : $order    Cont:$id_cont  DIDs: $dnis <> $destdid // Next: $nextcontract \n";
		++$error_did2;
	}
	if ($t>0){
		print "% errores (Orders) : $o/$t (". (int($o/$t*100)) ."%)\n";
	}else{
		print " Nothing to check \n";
	}
	print " Error DID (Leads vs Orders) : $error_did1\n";
	print " Error DID (Contracts vs Orders) : $error_did2\n";
}


sub devrun_loadformato {
# --------------------------------------------------------
	print "Content-type: text/html\n\n";
	
	## Fecha	Sem	Día	Call Center	Canal	DID	Agencia	Formato	Hora Canal	Hora EST	DMA	Prod	 Ordenes 	 $ Pauta 
	##1/1/2011(0)	1(1)	Sat(2)	Mixcoac(3)	Canal 57(4)	1631(5)	KJLA(6)	""" 28:30 MIN """(7)	22:00(8)	0:00(9)	LOS ANGELES CA(10)
	##			Moinsage(11)	 $-(12)   	 $637.50(13)

	my $partial=1;
	if(!$partial){

		my $sth = &Do_SQL("TRUNCATE TABLE `sl_mediacontracts` ");
		my $sth = &Do_SQL("TRUNCATE TABLE `sl_mediacontracts_notes` ");
		my $sth = &Do_SQL("UPDATE sl_orders SET ID_mediacontracts=0 WHERE 1");

	}else{
		my $delete_query = "SELECT ID_mediacontracts  FROM `sl_mediacontracts` WHERE (`ESTDay` BETWEEN '2011-01-01' AND '2011-12-31' OR DestinationDID = 0)";
		my ($sth) = &Do_SQL("SELECT COUNT(*)  FROM `sl_mediacontracts` WHERE (`ESTDay` BETWEEN '2011-01-01' AND '2011-12-31' OR DestinationDID = 0) AND DestinationDID < 9995;");
		my $contracts_total = $sth->fetchrow();
		my ($sth) = &Do_SQL("SELECT COUNT(*) FROM sl_orders WHERE ID_mediacontracts IN ($delete_query);");
		my $orders_total = $sth->fetchrow();
		print "<br>Total Contract Records: $contracts_total<br>Total Order Records: $orders_total<br>";
		#while(my($rec)=$sth->fetchrow_hashref()){

		##Orders
		#my $sth2 = &Do_SQL("UPDATE sl_orders INNER JOIN sl_mediacontracts USING(ID_mediacontracts) SET sl_orders.ID_mediacontracts=0 WHERE `ESTDay` BETWEEN '2011-01-01' AND '2011-12-31';");
		my $sth2 = &Do_SQL("UPDATE sl_orders SET ID_mediacontracts=0 WHERE ID_mediacontracts IN($delete_query);");
		##MediaContractsNotes
		my $sth4 = &Do_SQL("DELETE FROM sl_mediacontracts_notes WHERE ID_mediacontracts IN($delete_query AND DestinationDID < 9995);");
		##MediaContracts
		my $sth5 = &Do_SQL("DELETE FROM sl_mediacontracts WHERE (`ESTDay` BETWEEN '2011-01-01' AND '2011-12-31' OR DestinationDID = 0) AND DestinationDID < 9995;");


		#print "$rec->{'ID_mediacontracts'} : $rec->{'ESTDay'} $rec->{'ESTTime'}<br>";
		#}
		print "Done [Deleting/Updating]...<br><br>";
	}

	
	my ($file);
	local	($uname)	=	 `uname -n`;
	if($uname =~ /n3|n4|hawking/){
		$file='/home/www/docs/FormatoUSA_2011_v3.txt';
	}else{	
		$file = '/home/www/domains/direksys.com/docs/FormatoUSA_2011_v3.txt';
	}
	print "Processing : $file <br><br>";
	open(FILE,"<". $file);
	LINE :while ($line = <FILE>){
		@ary = split(/\t/,$line);
		#print $#ary."<br>";
		($ary[4] =~/fuera|Revenue|Recuperaciones/i) and ( next LINE);
		($ary[3] =~/fuera|Revenue|Recuperaciones/i) and ( next LINE);
		#fix date 1/27/2011
		($m,$d,$y) = split(/\//,$ary[0]);
		if ($ary[11] =~ /prostaliv/i and $m<4){
			next LINE;
		}

		$rec{'StationDate'} = "$y-$m-$d";
		$rec{'ESTDay'} = "$y-$m-$d";
		$rec{'Week'} = $ary[1];
		$rec{'Destination'} = $ary[3];
		$rec{'Station'} = $ary[4];
		$rec{'DestinationDID'} = $ary[5];
		$rec{'Agency'} = $ary[6];
		$rec{'Format'} = &conv_format($ary[7]);
		if ($ary[8] =~ /([^-]*)-([^-]*)/){
			$rec{'StationTime'} = "$1:00";
		}else{
			$rec{'StationTime'} = "$ary[8]:00";
		}
		if ($ary[9] =~ /([^-]*)-([^-]*)/){
			$rec{'ESTTime'} = "$1:00";
		}else{
			$rec{'ESTTime'} = "$ary[9]:00";
		}
		$rec{'Cost'} = $ary[13];
		$rec{'Cost'} =~ s/[^\d.]//g;
		print "$ary[0]-$ary[4]-$ary[5] ----- Cost:$rec{'Cost'}=$ary[13]<br>" if (!$rec{'Cost'});
		
		$rec{'DMA'} = $ary[10];
		$rec{'Offer'} = $ary[11];
		
		$rec{'Comments'} =  $ary[14];
		if ($ary[15]){
			$rec{'Status'} =  $ary[15]; # Status
		}else{
			$rec{'Status'} = 'Programado';
		}
		
		my ($query);
		foreach $key (keys %rec){
			$query .= ",$key = '". &filter_values($rec{$key})."' ";
		}
		
		my $sth = &Do_SQL("SELECT COUNT(*) FROM sl_mediacontracts WHERE Station='$rec{'Station'}' AND DMA='$rec{'DMA'}' AND Format='$rec{'Format'}' AND ESTDay='$rec{'ESTDay'}' AND ESTTime='$rec{'ESTTime'}' AND DestinationDID='$rec{'DestinationDID'}'");
		$q = $sth->fetchrow;
		if ($q > 0){
			print "Skip Duplicated :: Station='$rec{'Station'}' AND DMA='$rec{'DMA'}' AND Format='$rec{'Format'}' AND ESTDay='$rec{'ESTDay'}' AND ESTTime='$rec{'ESTTime'}' AND DestinationDID='$rec{'DestinationDID'}'<br>";
			print "INSERT INTO sl_mediacontracts SET Date=CURDATE(), Time=CURTIME(), ID_admin_users=2 $query\n";
			next LINE;
		}
			
		my $sth2 = &Do_SQL("INSERT INTO sl_mediacontracts SET Date=CURDATE(), Time=CURTIME(), ID_admin_users=2 $query");
		if ($sth2->rows != 1){
			print "Record Not Inserted :: ESTDay='$rec{'ESTDay'}' AND ESTTime='$rec{'ESTTime'}' AND StationDate='$rec{'StationDate'}' AND StationTime='$rec{'StationTime'}' AND DestinationDID='$rec{'DestinationDID'}'<br>";
			print "INSERT INTO sl_mediacontracts SET Date=CURDATE(), Time=CURTIME(), ID_admin_users=2 $query\n";
			#exit;
		}
		++$n;
		
		
		#if ($n>100){
		#	exit;
		#}
	}
	print "lineas : $n";
}

sub conv_format {
# --------------------------------------------------------
	my ($f) = @_;
	### '5:00',':120',,':90',,'Mencion'
	if ($f =~ /28:30/i){
		return '28:30 MIN';
	}elsif($f =~/1 MIN/i){
		return ':60';
	}elsif($f =~/1 MIN/i){
		return ':60';
	}elsif($f =~/2 MIN/i){
		return ':120';
	}elsif($f =~/30 SEG/i){
		return ':30';		
	}elsif($f =~/90 SEG/i){
		return ':90';			
	}elsif($f =~/MENC/i){
		return 'Mencion';	
	}elsif($f =~/5 MIN/i){
		return '5:00';	
	}else{
		#print "$f = Invalid $ary[4]<br>";
		return '28:30 MIN';
	}
}
sub devrun_checkformato {
# --------------------------------------------------------
	print "Content-type: text/html\n\n";
	
	## Fecha	Sem	Día	Call Center	Canal	DID	Agencia	Formato	Hora Canal	Hora EST	DMA	Prod	 Ordenes 	 $ Pauta 
	##1/1/2011(0)	1(1)	Sat(2)	Mixcoac(3)	Canal 57(4)	1631(5)	KJLA(6)	""" 28:30 MIN """(7)	22:00(8)	0:00(9)	LOS ANGELES CA(10)
	##			Moinsage(11)	 $-(12)   	 $637.50(13) 
	open(FILE,"</home/www/docs/FormatoUSA_Ene.txt");
	LINE :while ($line = <FILE>){
		@ary = split(/\t/,$line);
		#print $#ary."<br>";
		($ary[4] =~/fuera|Revenue|Recuperaciones/i) and ( next LINE);
		($ary[3] =~/fuera|Revenue|Recuperaciones/i) and ( next LINE);
		#fix date 1/27/2011
		($m,$d,$y) = split(/\//,$ary[0]);
		if ($rec{'Offer'} !~ /prostaliv/i and $m<4){
			next LINE;
		}
		++$l;
		$rec{'StationDate'} = "$y-$m-$d";
		$rec{'ESTDay'} = "$y-$m-$d";
		$rec{'Week'} = $ary[1];
		$rec{'Destination'} = $ary[3];
		$rec{'Station'} = $ary[4];
		$rec{'DestinationDID'} = $ary[5];
		$rec{'Agency'} = $ary[6];
		$rec{'Format'} = &conv_format($ary[7]);
		if ($ary[8] =~ /([^-]*)-([^-]*)/){
			$rec{'StationTime'} = "$1:00";
		}else{
			$rec{'StationTime'} = "$ary[8]:00";
		}
		if ($ary[9] =~ /([^-]*)-([^-]*)/){
			$rec{'ESTTime'} = "$1:00";
		}else{
			$rec{'ESTTime'} = "$ary[9]:00";
		}
		$rec{'Cost'} = $ary[13];
		$rec{'Cost'} =~ s/[^\d.]//g;
		#print "$ary[0]-$ary[4]-$ary[5] ----- Cost:$rec{'Cost'}=$ary[13]<br>" if (!$rec{'Cost'});
		$rec{'DMA'} = $ary[10];
		$rec{'Offer'} = $ary[11];
		$rec{'Status'} = 'Programado';
		$rec{'Comments'} =  $ary[14];
		if ($rec{'Offer'} =~ /prostaliv/i){
			++$p;
		}else{
			$cost = $ary[13];
			#$cost  =~ s/\$//g;
			#$cost  = $cost*1;
			if ($cost<0){
				next LINE;
			}
			my $sth = &Do_SQL("SELECT COUNT(*) FROM sl_mediacontracts WHERE ESTDay='$rec{'ESTDay'}' AND ESTTime='$rec{'ESTTime'}' AND StationDate='$rec{'StationDate'}' AND StationTime='$rec{'StationTime'}' AND DestinationDID='$rec{'DestinationDID'}'");
			$q = $sth->fetchrow;
			if ($q != 1){
				print "Error q=$q / Linea: $l: Cost : $cost /ESTDay='$rec{'ESTDay'}' AND ESTTime='$rec{'ESTTime'}' AND StationDate='$rec{'StationDate'}' AND StationTime='$rec{'StationTime'}' AND DestinationDID='$rec{'DestinationDID'}'<br>";
				++$n
			}
		}
	}
	print "lineas : $n<br>Prostaliv: $p";
}

sub devrun_assignardids {
# --------------------------------------------------------
#Last modified on 13 Oct 2010 16:24:10
#Last modified by: MCC C. Gabriel Varela S. :Se cambia right for left
#Last modified on 20 Oct 2010 15:30:01
#Last modified by: MCC C. Gabriel Varela S. :Se actualiza para estandarizar con la versión del cron
	print "Content-type: text/html\n\n";
	my ($days) = 180;   # From Today to x Days
	my ($cdays) = 30;   # Check CDR up to x days Before
	#my ($g) = " Grupo='US'";
	use Benchmark;
	my ($start) = new Benchmark;
	my ($count,$query);
	
	&connect_db_w($cfg{'dbi_db_pbx'},$cfg{'dbi_host_pbx'},$cfg{'dbi_user_pbx'},$cfg{'dbi_pw_pbx'});
	
	################################
	########  ORDERS
	################################
	for (0..$days){
		my $sth = &Do_SQL("SELECT DATE_ADD( CURDATE( ) , INTERVAL -$_ DAY ) ");
		$day_to_check = $sth->fetchrow();
		print "Checking : $day_to_check<br>";
		my $sth = &Do_SQL("SELECT ID_orders, CID,  Phone1, Phone2, Cellphone,concat(sl_orders.Date,' ',sl_orders.Time) as OrderDate 
		FROM sl_orders 
		Inner JOIN sl_customers 
		ON sl_orders.ID_customers = sl_customers.ID_customers 
		WHERE ((`DIDS7`=0 or isnull(DIDS7)) OR (`DNIS`=0 or isnull(DNIS)))
		AND sl_orders.Date = '$day_to_check'");
		while($rec=$sth->fetchrow_hashref){
			++$count;
			$query ='';
			$rec->{'Phone1'} =~ s/\D//g;
			if ($rec->{'Phone1'} ne ''){
				$query = "	(src='".substr($rec->{'Phone1'},-10)."' or src='1".substr($rec->{'Phone1'},-10)."') OR ";
			}

			$rec->{'Phone2'} =~ s/-|\+|\.|\D//g;
			if ($rec->{'Phone2'} ne '' and $query !~ /$rec->{'Phone2'}/){
				$query .= "	(src='".substr($rec->{'Phone2'},-10)."' or src='1".substr($rec->{'Phone2'},-10)."') OR ";
			}

			$rec->{'Cellphone'} =~ s/-|\+|\.|\D//g;
			if ($rec->{'Cellphone'} ne '' and $query !~ /$rec->{'Cellphone'}/){
				$query .= "	(src='".substr($rec->{'Cellphone'},-10)."' or src='1".substr($rec->{'Cellphone'},-10)."') OR ";
			}

			$rec->{'CID'} =~ s/-|\+|\.|\D//g;
			if ($rec->{'CID'} ne '' and $query !~ /$rec->{'CID'}/){
				$query .= "	(src='".substr($rec->{'CID'},-10)."' or src='1".substr($rec->{'CID'},-10)."') OR ";
			}
			$query = "(" . substr($query,0,-4) .")" if ($query ne '');
			
			if($query eq '')
			{
				$query='0';
			}
			my ($sth2) = &Do_SQL("SELECT accountcode,didmx,calldate,duration FROM sl_numbers Left JOIN `cdr`USE INDEX (src2) ON didusa=accountcode $g WHERE DATE(calldate)>=DATE_ADD( '$day_to_check' , INTERVAL -$cdays DAY )  AND $query order by calldate desc",1);
			($dids7,$didmx,$calldate,$duration) = $sth2->fetchrow_array();
			if ($dids7){
				$dateq=&Do_SQL("select datediff('$rec->{'OrderDate'}','$calldate') as diffd");
				$recdateq=$dateq->fetchrow_hashref;
				#print "$rec->{'ID_orders'},$didmx,$dids7,$calldate,$rec->{'OrderDate'},$recdateq->{'diffd'}\n";
				print "SELECT * FROM sl_numbers Left JOIN `cdr` ON didusa=accountcode $g WHERE DATE(calldate)>=DATE_ADD( '$day_to_check' , INTERVAL -$cdays DAY )  AND $query<br>";
				++$found;
				#Se determina first_call
				my($fcquery)=&Do_SQL("SELECT if(TIMESTAMPDIFF(minute,'$calldate', '$rec->{'OrderDate'}')between 0 and $cfg{'fc_minutes'} or TIMESTAMPDIFF(minute,'$calldate', '$rec->{'OrderDate'}')between 0 and (($duration)/60)+5,'Yes','No') as first_call");
				#print "SELECT if(TIMESTAMPDIFF(minute,'$calldate', '$rec->{'OrderDate'}')between 0 and $cfg{'fc_minutes'},'Yes','No') as first_call\n";
				my $first_call=$fcquery->fetchrow();

				my ($sth2) = &Do_SQL("UPDATE $cfg{'dbi_db'}.sl_orders SET DNIS='$didmx', DIDS7='$dids7',first_call='$first_call' WHERE ID_orders=$rec->{'ID_orders'}",0);
				print "UPDATE sl_orders SET DNIS='$didmx', DIDS7='$dids7',first_call='$first_call' WHERE ID_orders=$rec->{'ID_orders'}\n";
			}
			print "$dids7,$didmx<br><br>";
		}
#		################################
#		########  preORDERS
#		################################
#		
#		my $sth = &Do_SQL("SELECT ID_preorders, CID,  Phone1, Phone2, Cellphone FROM sl_preorders RIGHT JOIN sl_customers ON sl_preorders.ID_customers = sl_customers.ID_customers WHERE `DIDS7` =0 AND sl_preorders.Date = '$day_to_check'");
#		while($rec=$sth->fetchrow_hashref){
#			++$count;
#			$query ='';
#			$rec->{'Phone1'} =~ s/-//g;
#			if ($rec->{'Phone1'}){
#				$query = "	src='".substr($rec->{'Phone1'},-10)."' OR ";
#			}
#			$rec->{'Phone2'} =~ s/-//g;
#			if ($rec->{'Phone2'} and $query !~ /$rec->{'Phone2'}/){
#				$query .= "	src='".substr($rec->{'Phone2'},-10)."' OR ";
#			}
#			$rec->{'Cellphone'} =~ s/-//g;
#			if ($rec->{'Cellphone'} and $query !~ /$rec->{'Cellphone'}/){
#				$query .= "	src='".substr($rec->{'Cellphone'},-10)."' OR ";
#			}
#			$rec->{'CID'} =~ s/-//g;
#			if ($rec->{'CID'} and $query !~ /$rec->{'CID'}/){
#				$query .= "	src='".substr($rec->{'CID'},-10)."' OR ";
#			}
#			$query = "(" . substr($query,0,-4) .")";
#			my ($sth2) = &Do_SQL("SELECT accountcode,didmx FROM sl_numbers Left JOIN `cdr`USE INDEX (src2) ON didusa=accountcode $g WHERE DATE(calldate)>=DATE_ADD( '$day_to_check' , INTERVAL -$cdays DAY )  AND $query",1);
#			($dids7,$didmx) = $sth2->fetchrow_array();
#			if ($dids7){
#				print "SELECT * FROM sl_numbers Left JOIN `cdr` ON didusa=accountcode $g WHERE DATE(calldate)>=DATE_ADD( '$day_to_check' , INTERVAL -$cdays DAY )  AND $query<br>";
#				++$found;
#				print "UPDATE sl_preorders SET DNIS='$didmx', DIDS7=$dids7 WHERE ID_preorders=$rec->{'ID_preorders'}";
#				my ($sth2) = &Do_SQL("UPDATE sl_preorders SET DNIS='$didmx', DIDS7='$dids7' WHERE ID_preorders=$rec->{'ID_preorders'}",0);
#			}
#			print "$dids7,$didmx<br><br>";
#		}
	
		
	}
	
	&Do_SQL("update sl_orders set first_call='Unknown' where first_call='' or isnull(first_call);");
	
	&Do_SQL("update sl_orders
inner join sl_numbers on (dnis=didmx)
set DIDS7=didusa
where (((dnis=0 or isnull(dnis))and(dids7!=0 and not isnull(dids7))) or ((dnis!=0 and not isnull(dnis))and(dids7=0 or isnull(dids7))))
and DNIS!=0
and not isnull(DNIS)");

	&Do_SQL("update sl_orders
inner join sl_numbers on (dids7=didusa)
set DNIS=didmx
where (((dnis=0 or isnull(dnis))and(dids7!=0 and not isnull(dids7)))or ((dnis!=0 and not isnull(dnis))and(dids7=0 or isnull(dids7))))
and dids7!=0
and not isnull(dids7)");
	
	my  ($end) = new Benchmark;
	print timestr(timediff($end, $start), 'all')."seconds for $count and found: $found";
	
	return;
	
}

#################################################################
############# Funciones de reuso
#################################################################

sub day_of_month {
# --------------------------------------------------------
	my ($d) = @_;
	my (@ary) = split(/-/,$d,3);
	return $ary[2];
}

sub weekperiod {
# --------------------------------------------------------
	my ($d) = @_;
	my (@ary) = split(/-/,$d,3);
	if ($ary[2]>15){
		return (2*($ary[1]-1)+2)."_".substr($ary[0],2);
	}else{
		return (2*($ary[1]-1)+1)."_".substr($ary[0],2);
	}
	
	return $ary[2];
}

sub qperiod {
# --------------------------------------------------------
	my ($d) = @_;
	my (@ary) = split(/-/,$d,3);
	return (int(($ary[1]-1)/3)+1)."_".substr($ary[0],2);
	
	return $ary[2];
}


sub productcat {
# --------------------------------------------------------
	my ($p) = @_;
	
#	my (%c) = ('prostaliv'=>'Prostaliv','dream'=>'DreamBody',
#			'chardon'=>'Chardon de Marie','botas'=>'Botas Mexicanas',
#			'charakani'=>'Charakani','colageina'=>'Colageina',
#			'moinsage'=>'Moinsage','rejuvital'=>'Rejuvital','algafit'=>'Algafit',
#			'diabestevia'=>'Diabestevia','puassance'=>'Puassance','singivitis'=>'Singivitis');
	my (%c) = ('prostaliv'=>'Prostaliv','dream'=>'Fajas',
			'chardon'=>'Chardon de Marie','botas'=>'Botas Mexicanas',
			'charakani'=>'Charakani','colageina'=>'Colageina',
			'moinsage'=>'Moinsage','rejuvital'=>'Rejuvital','algafit'=>'Algafit','alga'=>'Algafit',
			'diabestevia'=>'Diabestevia','puassance'=>'Puassance','singivitis'=>'Singivitis',
			'BODY SIGNER'=>'Fajas','CONTROL MAN'=>'Fajas','QUEBARE'=>'Fajas',
			'secreto de la juventud'=>'Colageina','Set de belleza'=>'Colageina',
			'bioxtron'=>'Bioxtron','moulding'=>'Moulding Motion 5','Algafit'=>'Algafit', 'Diabestevia'=>'Diabestevia',
			'natural red and green'=>'natural Red And Green','marvel'=>'green Marvel','keraorganiq'=>'Keraorganiq',
			'dicer'=>'Nicer Dicer','Bionergiser'=>'Bionergiser',
			'crucifijo'=>'Joyeria','guadalupe'=>'Joyeria','virgen'=>'Joyeria',
			'scalp'=>'Scalp Med','vipex'=>'Vipex',
			'de la cruz'=>'De la Cruz',
			'agavera'=>'Fibra Agavera',
			'climber'=>'Maxiclimber',
			'sleggins'=>'Sleggins',
			'DEBESTEVIA'=>'Diabestevia','CELLULESS'=>'Celluless',
			'Rocket'=>'Fitness','Flyer'=>'Fitness','PERLOP'=>'PERLOP'
			);
	foreach $key (keys %c){
		if ($p =~ /$key/i){
			if ($in{'e'} eq '4' and ($c{$key} ne 'Prostaliv' and $c{$key} ne 'DreamBody')){
				return 'allnatpro';
			}else{
				return $c{$key};
			}
		}
	}
	if ($in{'e'} eq '4'){
		return 'allnatpro';
	}
	return 'Unknown'.$p;
}

sub productcat_summ {
# --------------------------------------------------------
	my ($p) = @_;
	my (%c) = ('prostaliv'=>'Prostaliv','dream'=>'Fajas',
			'chardon'=>'Chardon de Marie','botas'=>'Botas Mexicanas',
			'charakani'=>'Charakani','colageina'=>'Colageina',
			'moinsage'=>'Moinsage','rejuvital'=>'Rejuvital','algafit'=>'Algafit','alga'=>'Algafit',
			'diabestevia'=>'Diabestevia','puassance'=>'Puassance','singivitis'=>'Singivitis',
			'BODY SIGNER'=>'Fajas','CONTROL MAN'=>'Fajas','QUEBARE'=>'Fajas',
			'secreto de la juventud'=>'Colageina','Set de belleza'=>'Colageina',
			'bioxtron'=>'Bioxtron','moulding'=>'Moulding Motion 5','Algafit'=>'Algafit', 'Diabestevia'=>'Diabestevia',
			'natural red and green'=>'natural Red And Green','marvel'=>'green Marvel','keraorganiq'=>'Keraorganiq',
			'dicer'=>'Nicer Dicer','Bionergiser'=>'Bionergiser',
			'crucifijo'=>'Joyeria','guadalupe'=>'Joyeria','virgen'=>'Joyeria',
			'scalp'=>'Scalp Med','vipex'=>'Vipex',
			'de la cruz'=>'De la Cruz',
			'agavera'=>'Fibra Agavera',
			'sleggins'=>'Sleggins',
			'climber'=>'Maxiclimber',
			'DEBESTEVIA'=>'Diabestevia','CELLULESS'=>'Celluless',
			'Rocket'=>'Fitness','Flyer'=>'Fitness','PERLOP'=>'PERLOP'
			);
	
	foreach $key (keys %c){
		if ($p =~ /$key/i){
			return $c{$key};
		}
	}
	return 'Others';
}



sub devrun_clonate_intercompanies{
#-----------------------------------------
# Created on: 07/28/09  15:29:37 By  Roberto Barcenas
# Forms Involved: 
# Description : Clona productos entre companias.
# Parameters :
	
	my @cols=('ID_products','Model','Name','SmallDescription','Description','SmallDescription_en','Description_en','Disclaimer','CountryOrigin','Weight','SizeW','SizeH','SizeL','Packing','Handling','WarehouseHandling','PayType','ProductType','ID_packingopts','ProductDocs','ManufacterSKU','WholesalePriceOrigin','WholesaleOrigin','WholesalePrice','Tariff','Discount','SLTV_NetCost','MSRP','MAP','BreakEvenVolume','Margin','AirTimeMinutes','MinimumStock','MaximumStock','edt','ID_services_related','SPrice','SPriceName','SPrice1','SPrice1Name','SPrice2','SPrice2Name','SPrice3','SPrice3Name','SPrice4','SPrice4Name','FPPrice','MemberPrice','Flexipago','Downpayment','Rebate','Duties','Insurance','ChoiceName1','ChoiceName2','ChoiceName3','ChoiceName4','Testing','Testing_AuthBy','IsFinal','DropShipment','ID_products_speech','free_shp_opt');
	my $from_company='';
	$from_company = 'sltv'	if (!$in{'e'} or $in{'e'} eq '0');
	$from_company = 'innovausa'	if $in{'e'} eq '1';
	$from_company = 'innovapr'	if $in{'e'} eq '2';
	$from_company = 'training'	if $in{'e'} eq '3';
	$from_company = 'gts'	if $in{'e'} eq '4';

	my $to_company = 'innovausa';
	my $id_vendors = 260;
	my $fname = $from_company.'_to_'.$to_company.'_products.xls';
	
	print "Content-type: application/octetstream\n";
	print "Content-disposition: attachment; filename=$fname\n\n";
	print "\r\n\r\nID Products $from_company,Exists,ID Products $to_company\r\n";

	$in{'set_sale_movements'} = 'Sale';
 	my $sth = &Do_SQL("SELECT ID_products FROM sl_products_vendors WHERE ID_vendors = $id_vendors;");

	LINE: while(my($id_products) = $sth->fetchrow()){
		
		## Product Info
		my $sth2 = &Do_SQL("SELECT * FROM sl_products WHERE ID_products = '$id_products' AND Status != 'Testing';");
		$rec_prod = $sth2->fetchrow_hashref();

		if($rec_prod->{'ID_products'} > 0){

			## The ID exists?
			my $sth3 = &Do_SQL("SELECT COUNT(*) FROM $to_company.sl_products WHERE ID_products = '$id_products';");
			my($id_exists) = $sth3->fetchrow();

			if($id_exists > 0){
				while (!$in{'id_products'} and $in{'id_products'}<=100000 and $count<300){
					$in{'id_products'} = substr(int(rand(10000000000)) + 1,2,6);
					my ($sth) = &Do_SQL("SELECT COUNT(*) FROM $to_company.sl_products WHERE ID_products='$in{'id_products'}';");
					if ($sth->fetchrow >0 or $in{'id_products'}<=100000){
						delete($in{'id_products'});
					}
					++$count;
				}
				if (!$in{'id_products'}){
					&load_new_prodid;
				}
				$rec_prod->{'ID_products'} = $in{'id_products'};
			}
			my $query='';
			for(0..$#cols){
				$query .= "$cols[$_] = '".&filter_values($rec_prod->{$cols[$_]})."',";
			}
			$query .="ID_brands=0,web_available='Yes',Status='Web Only',Date=CURDATE(),Time=CURTIME(),ID_admin_users=1";
			&Do_SQL("INSERT INTO $to_company.sl_products SET $query");

			print "$id_products,$id_exists,$rec_prod->{'ID_products'}\r\n";
		}
	}

}


sub devrun_webprodlist{

	my $fname = 'eccomerce_products_list.xls';
	print "Content-type: application/octetstream\n";
	print "Content-disposition: attachment; filename=$fname\n\n";
	print "ID_products,ID_products W,Name,Status,Web Available\r\n";


	my $sth = &Do_SQL("SELECT sl_products.ID_products,sl_products_w.ID_products,sl_products.Name,sl_products.Status,sl_products.web_available  
FROM sl_products
LEFT JOIN sl_products_w
ON sl_products.ID_products = sl_products_w.ID_products
WHERE
((sl_products.Status='On-Air' AND sl_products.web_available='Yes') OR sl_products.Status='Web Only')
ORDER BY sl_products_w.ID_products;");
	while(my($id_products,$id_products_w,$name,$status,$web_available) = $sth->fetchrow()){
		print "$id_products,$id_products_w,$name,$status,$web_available\r\n";
	}

	print "\r\n\r\n";

	my $sth = &Do_SQL("SELECT sl_products.ID_products,sl_products_w.ID_products,sl_products.Name,sl_products.Status,sl_products.web_available  
FROM sl_products_w
LEFT JOIN sl_products
ON sl_products.ID_products = sl_products_w.ID_products
WHERE
sl_products.Status !='Web Only' AND sl_products.web_available='No'
ORDER BY sl_products_w.ID_products;");

	while(my($id_products,$id_products_w,$name,$status,$web_available) = $sth->fetchrow()){
		print "$id_products,$id_products_w,$name,$status,$web_available\r\n";
	}


}


sub devrun_daily_prepaidcard_report{
# --------------------------------------------------------
# Author: Roberto Barcenas
# Created on: 09/22/2011
# Description : Envia reporte semanal de llamadas a Bernardo Hasbach
# Forms Involved:
# Parameters : Se manda a llamar desde sl_cron_scripts en S3


	my $from_mail="rbarcenas\@innovagroupusa.com";
	#my $to_mail="bhasbach\@innovagroupusa.com";
	my $to_mail2="rbarcenas\@innovagroupusa.com";
	my $to_mail3="chaas\@innovagroupusa.com";
	my $subject_mail='Ordenes con tarjeta de Prepago';
	my $body_mail;


	my ($sth) =&Do_SQL("SELECT sl_customers.ID_customers,ID_Orders FROM innovausa.sl_customers INNER JOIN innovausa.sl_orders ON sl_orders.ID_customers = sl_customers.ID_customers WHERE Ptype='Prepaid-Card' AND sl_orders.Status='New' /*AND sl_orders.Date=DATE_SUB(CURDATE(), INTERVAL 1 DAY)*/;");

	if($sth->rows() > 0){

		my $workbook,$worksheet,$date_format,$data_required,$data_extra;
		my $fname   = 'sosl_prepaidcard_daily_batch-'.$batch_day.'.xls';

		($in{'e'} eq '1') and ($fname =~	s/sosl/usa/);
		($in{'e'} eq '2') and ($fname =~	s/sosl/pr/);
		($in{'e'} eq '3') and ($fname =~	s/sosl/training/);
		($in{'e'} eq '4') and ($fname =~	s/sosl/gts/);
		$fname =~	s/\///g;

		use Spreadsheet::WriteExcel;

		# Send the content type
		#print "Content-type: application/vnd.ms-excel\n\n";
		print "Content-type: application/octetstream\n";
		print "Content-disposition: attachment; filename=$fname\n\n";

		# Redirect the output to STDOUT
		$workbook  = Spreadsheet::WriteExcel->new("-");
		$worksheet = $workbook->add_worksheet();

		# Headers.
		$worksheet->write(0, 0,'ID');
		$worksheet->write(0, 1,'Type');
		$worksheet->write(0, 2,'IDCountry');
		$worksheet->write(0, 3,'IDState');
		$worksheet->write(0, 4,'IdGoodThru');
		$worksheet->write(0, 5,'Sec.Identification ');
		$worksheet->write(0, 6,'Sec.ID Type');
		$worksheet->write(0, 7,'Sec.ID Country ');
		$worksheet->write(0, 8,'Sec.ID State ');
		$worksheet->write(0, 9,'Sec.IdGoodThru');
		$worksheet->write(0, 10,'Title');
		$worksheet->write(0, 11,'FirstName');
		$worksheet->write(0, 12,'MiddleName');
		$worksheet->write(0, 13,'FirstLastName');
		$worksheet->write(0, 14,'SecondLastName');
		$worksheet->write(0, 15,'BirthDay');
		$worksheet->write(0, 16,'Country');
		$worksheet->write(0, 17,'Address');
		$worksheet->write(0, 18,'City');
		$worksheet->write(0, 19,'State');
		$worksheet->write(0, 20,'Zip');
		$worksheet->write(0, 21,'HomeLada');
		$worksheet->write(0, 22,'HomePhone');
		$worksheet->write(0, 23,'CellLada');
		$worksheet->write(0, 24,'CellPhone');
		$worksheet->write(0, 25,'FaxLada');
		$worksheet->write(0, 26,'FaxPhone');
		$worksheet->write(0, 27,'WorkLada');
		$worksheet->write(0, 28,'WorkPhone');
		$worksheet->write(0, 29,'Email');
		$worksheet->write(0, 30,'Reference1');
		$worksheet->write(0, 31,'Reference2');


		## Formatting
		$date_format = $workbook->add_format(num_format => 'yyyymmdd');
		$data_required = $workbook->add_format(border => '2', border_color => 'red');
		$data_extra = $workbook->add_format(border => '2', border_color => 'green');

		my $row=1;
		LINE:while(my($id_customers,$id_orders) = $sth->fetchrow()){

			my ($sth) = &Do_SQL("SELECT IF(Confirmed IS NULL,0,Confirmed)AS Confirmed,IF(Tofile IS NULL,0,Tofile)AS Tofile FROM sl_orders LEFT JOIN
(SELECT ID_Orders,COUNT(*)AS Confirmed FROM sl_orders_notes WHERE ID_Orders='$id_orders' AND Type='Unicard/OK')AS tmp1
ON sl_orders.ID_Orders = tmp1.ID_orders
LEFT JOIN
(SELECT ID_Orders,COUNT(*)AS Tofile FROM sl_orders_notes WHERE ID_Orders='$id_orders' AND Type='Unicard/File')AS tmp2
ON sl_orders.ID_Orders = tmp2.ID_orders
WHERE sl_orders.ID_Orders = '$id_orders';");

			my($confirmed,$tofile) = $sth->fetchrow();

			#!$confirmed or 
			next LINE if ($tofile > 0);


			my %prepaid_data;
			my $cname,$clastname;

			#Extraemos los datos de notes
			my ($sth2) =&Do_SQL("SELECT Notes from sl_customers_notes WHERE ID_customers='$id_customers' AND Notes LIKE 'Prepaid-Card Info%' LIMIT 1;");
			my ($ppc_data) = $sth2->fetchrow();

			my @ary_data = split(/\n|\r/,$ppc_data);

			for(0..$#ary_data){
				my $line = $ary_data[$_];

				if($line =~ /=/){
					my ($key,$value) = split(/=/,$line,2);
					$key=lc($key);
					$key =~ s/\s|_//g;
					$prepaid_data{$key} = $value;
				}
			}
			## Temporal $prepaid_data{'idnumber'}
			if(!$prepaid_data{'customerlastname'}){
				($cname,$clastname)= split(/\s/,$prepaid_data{'name'},2);
			}else{
				$cname = $prepaid_data{'customerfirstname'};
				$clastname = $prepaid_data{'customerlastname'};
			}

			if($prepaid_data{'idtype'} =~ /^\((\d{1,2})/){
				$prepaid_data{'idtype'} = $1;
			}

			if($prepaid_data{'idcountry'} =~ /^\((\d{1,3})/){
				$prepaid_data{'idcountry'} = $1;
			}

			if($prepaid_data{'idstate'} =~ /^\((\d{1,2})/){
				$prepaid_data{'idstate'} = $1;
			}

			$prepaid_data{'idstate'}='' if($prepaid_data{'idtype'} =~ /1|3|4|5|6|100|102/ or $prepaid_data{'idcountry'} !~ /840/);
			$prepaid_data{'idgoodthru'}='' if($prepaid_data{'idtype'} =~ /1|6|100|102/);
			$prepaid_data{'postalzip'}=&load_name('sl_customers','ID_customers',$id_customers,'Zip') if length($prepaid_data{'postalzip'}) < 5;

			$prepaid_data{'cellphone_lada'}='1';
			$prepaid_data{'cellphone_lada'}='52' if $prepaid_data{'idcountry'} =~ /484/;#Mexico
			$prepaid_data{'cellphone_lada'}='504' if $prepaid_data{'idcountry'} =~ /340/;#Honduras
			$prepaid_data{'cellphone_lada'}='503' if $prepaid_data{'idcountry'} =~ /222/;#ElSalvador
			$prepaid_data{'cellphone_lada'}='57' if $prepaid_data{'idcountry'} =~ /170/;#Colombia
			$prepaid_data{'cellphone_lada'}='58' if $prepaid_data{'idcountry'} =~ /862/;#Venezuela
			$prepaid_data{'cellphone_lada'}='505' if $prepaid_data{'idcountry'} =~ /558/;#Nicaragua
			$prepaid_data{'cellphone_lada'}='54' if $prepaid_data{'idcountry'} =~ /032/;#Argentina
			$prepaid_data{'cellphone_lada'}='593' if $prepaid_data{'idcountry'} =~ /218/;#Ecuador


			# Data.
			$worksheet->write_string($row, 0,$prepaid_data{'idnumber'},$data_required); #1
			$worksheet->write_number($row, 1,$prepaid_data{'idtype'},$data_required); #1
			$worksheet->write($row, 2,$prepaid_data{'idcountry'},$data_required); #1
			$worksheet->write($row, 3,$prepaid_data{'idstate'},$data_required); #1
			$worksheet->write_string($row, 4,$prepaid_data{'idgoodthru'},$date_format); #1
			$worksheet->write($row, 5,'',); #Secondary ID
			$worksheet->write($row, 6,'');
			$worksheet->write($row, 7,'');
			$worksheet->write($row, 8,'');
			$worksheet->write($row, 9,'');
			$worksheet->write($row, 10,'');
			$worksheet->write_string($row, 11,$cname,$data_required); #1
			$worksheet->write($row, 12,'');
			$worksheet->write_string($row, 13,$clastname,$data_required); #1
			$worksheet->write($row, 14,'');
			$worksheet->write_string($row, 15,$prepaid_data{'birthday'},$date_format);
			$worksheet->write($row, 16,'');
			$worksheet->write_string($row, 17,"$prepaid_data{'postaladdress1'} $prepaid_data{'postaladdress2'}",$data_extra);
			$worksheet->write_string($row, 18,$prepaid_data{'postalcity'},$data_extra);
			$worksheet->write_string($row, 19,$prepaid_data{'postalstate'},$data_extra);
			$worksheet->write_string($row, 20,$prepaid_data{'postalzip'},$data_required); #1
			$worksheet->write($row, 21,'');
			$worksheet->write($row, 22,'');
			$worksheet->write_number($row, 23,$prepaid_data{'cellphone_lada'},$data_required);
			$worksheet->write_string($row, 24,$prepaid_data{'cellphone'},$data_required);
			$worksheet->write($row, 25,'');
			$worksheet->write($row, 26,'');
			$worksheet->write($row, 27,'');
			$worksheet->write($row, 28,'');
			$worksheet->write($row, 29,'');
			$worksheet->write($row, 30,'');
			$worksheet->write($row, 31,'');
			#$worksheet->write($row, 32,$id_orders);
			#$worksheet->write($row, 33,$id_customers);

			$row++;
		}
	}else{
		print "Content-type: text/html\n\n";
		print "Done - No data founded";
	}
}


sub devrun_warehouse_mod_codsales_table{
# --------------------------------------------------------
# Author: Roberto Barcenas
# Created on: 10/10/2011
# Description : Corrige la tabla de ventas cod que esta en el home de orders
# Forms Involved:
# Parameters : 

	print "Content-type: text/html\n\n";
	&Do_SQL("TRUNCATE TABLE `sl_cod_sales`;");
	&cod_sales_execute(0);
	my $sth=&Do_SQL("SELECT ID_warehouses FROM sl_warehouses WHERE Type='Virtual' AND Status='Active' ORDER BY ID_warehouses;");
	while(my($id_warehouse) =  $sth->fetchrow()){
		&cod_sales_execute($id_warehouse);
	}
	print "Listo";

}


sub devrun_webgetWebSales{
# --------------------------------------------------------
# Author: Roberto Barcenas
# Created on: 11/29/2011
# Description : Genera el reporte de Ventas Web para asignacion de Bonos a los vendedores
# Forms Involved:
# Parameters :

	#$in{'automatic'}=1;
	&getWebsiteSales(" AND sl_orders.Date>='2012-06-01'");
}

#########################################################
#########################################################	
#	Function: ccbonus_monthly
#   		Genera reporte de ventas del callcenter en el periodo actual
#
#	Created by:
#		_Carlos Haas_
#
#	Modified By:
#
#   	Parameters:
#
#   	Returns:
#
#   	See Also:
#
sub devrun_ccbonus_monthly {
########################################################
########################################################	
	
	my $dates;

	if($in{'from_date'} and $in{'to_date'}){
		$dates = $in{'from_date'} .'_'.$in{'to_date'};	
	}else{
		my $sth = Do_SQL("SELECT CONCAT( CONCAT(DATE_FORMAT(LAST_DAY(CURDATE()),'%Y-%m-'),'01'),'_',  CURDATE() );");
		$dates = $sth->fetchrow();
	}
	
	my @ary_dates = split(/_/,$dates); 
	my $fromdate = $ary_dates[0];
	my $todate = $ary_dates[1];
	my @ary_status = ('New','Processed','Pending','Shipped','Cancelled','Void','System Error');

	my ($sth) = Do_SQL("SELECT ID_admin_users,CONCAT(FirstName,' ',LastName),user_type FROM admin_users WHERE application='sales' AND Status='Active' ORDER BY user_type,ID_admin_users;");
	$va{'matches'} =  $sth->rows();
	
	if($va{'matches'} > 0){
	
		my $fname   = 'ccbonus.'.$dates.'.csv';
		print "Content-type: application/octetstream\n";
		print "Content-disposition: attachment; filename=$fname\n\n";
	
		my $str_orders_detail;
		for my $i(0..$#ary_status){
			$this_status = $ary_status[$i];
			$str_orders_detail .= $this_status . ' Cantidad, ' . $this_status . "\$, " . $this_status . " TDC \$, ";
			$i++;
		}

		my ($sth2) = Do_SQL("SELECT ID_admin_users,CONCAT(FirstName,' ',LastName),user_type FROM admin_users WHERE application='sales' AND Status='Active' ORDER BY user_type,ID_admin_users;");		
		
		#print AUTH "ID User, Nombre Completo, Ordenes Cantidad, Ordenes Total \$, Ventas Cantidad, Ventas Total \$, % TDC, Ticket Promedio, Datos Completos \$, Comision a pagar en MX\$\n";
		print "ID User, Nombre Completo, Tipo, $str_orders_detail Ordenes Cantidad, Ordenes Total \$, TDC Ordenes \$, Conv TDC %, Comision Ordenes \$, Cantidad Ventas, Total Ventas \$, Ticket Promedio, Comision Fija Venta %, Comision TDC %, Comision Ticket %, Total Comision %, Comision Ventas \$,Ordenes Datos Completos, Comision Datos Completos \$, Ordenes Datos Incompletos, Descuento Datos Incompletos \$, Comision a pagar en MX \$   \n";
	
		while(my($id_admin_users,$name,$utype) = $sth->fetchrow()){
			#my ($qty_orders, $total_orders, $total_orders_tdc, $qty_sales, $total_sales, $base_order, $base_sale, $pot_base_sale, $pbase_order, $pbase_sale, $bono_ticket, $pot_bono_ticket, $bono_tdc, $pot_bono_tdc, $ticket_prom, $pot_ticket_prom, $Conv_TDC, $pot_Conv_TDC, $order_data, $bonus_data, $discount_data) = &agent_bonus($id_admin_users, $fromdate, $todate);
			my ($total_orders_tdc, $base_order, $base_sale, $pot_base_sale, $pbase_order, $pbase_sale, $bonus_data, $discount_data, $bono_ticket, $pot_bono_ticket, $bono_tdc, $pot_bono_tdc, $ticket_prom, $pot_ticket_prom, $Conv_TDC, $pot_Conv_TDC, $orders_data, $qty_orders, $bonus_data_qty, $bonus_data_amt, $discount_data_qty, $discount_data_amt,$pot_orders_data, $pot_bonus_data_amt, $pot_discount_data_amt, $qty_sales, $total_sales, $str_orders, @ary_orders) = &agent_bonus($id_admin_users, $fromdate, $todate);
			my $str_orders_detail='';
			my $str_orders_fdetail='';

			if($qty_orders > 0 or $qty_sales > 0){
				
				my $aname = &load_name('admin_users','ID_admin_users',$id_admin_users,"CONCAT(FirstName,' ',LastName)");
				my $utype = &load_name('admin_users','ID_admin_users',$id_admin_users,'user_type');
				my $pct =  $pbase_sale + $bono_tdc + $bono_ticket;

				my @ary_data_orders = split(/\|/,$str_orders);
				my $total_orders_qty=0; my $total_orders_amt=0; my $total_orders_tdc=0; my $total_orders_bonus=0;

				STATUS:for my $j(0..$#ary_status){
					my $flag=0;
					for my $i(0..$#ary_orders){

						if($ary_status[$j] eq $ary_orders[$i]){
						
							$this_status = $ary_orders[$i];
							my ($qty,$amt,$tdc) = split(/;/,$ary_data_orders[$i]);
							$amt = &round($amt,2);
							$tdc = &round($tdc,2);
							my $this_bonus = $this_status !~ /Void|System/ ? ($pbase_order / 100 * $amt) : 0;

							$total_orders_qty += $qty;
							$total_orders_amt += $amt;
							$total_orders_tdc +=  $this_status !~ /Void|System/ ? $tdc : 0;
							$total_orders_bonus += $this_bonus;


							$str_orders_detail .= "`$ary_status[$j]` = '$qty|$amt|$tdc', ";
							$str_orders_fdetail .= "$qty,$amt,$tdc, ";
							$flag=1;
							next STATUS;
						}
						$i++;
					}
					$str_orders_detail .= "`$ary_status[$j]` = '0|0|0', " if !$flag;
					$str_orders_fdetail .= "0,0,0," if !$flag;
					$j++;
				}

				

				## Downloadable File
				#print "$id_admin_users,$aname,$qty_orders,".round($total_orders_amt,2).",$qty_sales,".round($total_sales,2).",".round($Conv_TDC*100,2).",".round($ticket_prom,2).",".round($bonus_data_amt,2).",".round($base_order+$base_sale+$bonus_data_amt,2)."\n";
				#print "Downloadable\n$id_admin_users,$aname,$qty_orders,".round($total_orders_amt,2).",".round($total_orders_tdc,2).",$qty_sales,".round($total_sales,2).",".round($Conv_TDC*100,2).",".round($ticket_prom,2).",".round($bonus_data_amt,2).",".round($discount_data_amt,2).",".round($base_order+$base_sale+$bonus_data_amt,2)."\n";

			
				## Developers File
				print "$id_admin_users,$aname,$utype, $str_orders_fdetail $total_orders_qty,".round($total_orders_amt,2).",".round($total_orders_tdc,2).",".round($Conv_TDC*100,2).",".round($base_order,2).",$qty_sales,".round($total_sales,2).",".round($ticket_prom,2).",$pbase_sale,".&round($bono_tdc,2).",".&round($bono_ticket,2).",".round($pct,2).",".round($base_sale,2).", $bonus_data_qty ($bonus_data),".round($bonus_data_amt,2).", $discount_data_qty ($discount_data), ".round($discount_data_amt,2).",".round($base_order+$base_sale+$bonus_data_amt,2)."\n";
				#print "Developers\n$id_admin_users,$aname,$utype $str_orders_fdetail $total_orders_qty,".round($total_orders_amt,2).",".round($total_orders_tdc,2).",".round($Conv_TDC*100,2).",".round($base_order,2).",$qty_sales,".round($total_sales,2).",".round($ticket_prom,2).",".round($pct,2).",$pbase_sale,$bono_tdc,$bono_ticket,".round($base_sale,2).", $bonus_data_qty".round($bonus_data_amt,2).", $discount_data_qty, ".round($discount_data_amt,2).",".round($base_order+$base_sale+$bonus_data_amt,2)."\n\n";
			}
		}
	}else{
		print "Content-type: text/html\n\n";
		print "$va{'matches'} matches";
	}
}


sub devrun_ratiossummary{
# --------------------------------------------------------
	my ($fromdate)= '2012-06-01';
	my ($todate)= '2012-08-14';
	
	$curdate = '2012-07-08';
	$curtime = '13:15:00';
	my ($c);
	
	### Bulding Report
	my ($sth) = &Do_SQL("SELECT * FROM `sl_mediacontracts` WHERE ESTDay BETWEEN '$fromdate' AND '$todate' AND Status IN(". $cfg{'contract_valid_status'} .") AND CONCAT(ESTDay,' ',ESTTime) < NOW() ORDER BY ESTDay ASC");
	while ($rec = $sth->fetchrow_hashref() ) {
		my ($tmp) = load_contract_totals($rec->{'ID_mediacontracts'},$rec->{'ESTTime'},$rec->{'ESTDay'},$rec->{'DestinationDID'});
		$str .= "$rec->{'ID_mediacontracts'},$rec->{'ESTTime'},$rec->{'ESTDay'},$rec->{'DestinationDID'}<br>";

		### Load Calls
		$sth2 = &Do_SQL("SELECT 
			SUM(IF(TIMESTAMPDIFF(MINUTE, '$rec->{'ESTDay'} $rec->{'ESTTime'}', CONCAT(Date, ' ', Time) ) BETWEEN -30 AND 90,1,0))AS P1, 
			SUM(IF(TIMESTAMPDIFF(MINUTE, '$rec->{'ESTDay'} $rec->{'ESTTime'}', CONCAT(Date, ' ', Time) ) BETWEEN 91 AND 360,1,0))AS P2, 
			SUM(IF(TIMESTAMPDIFF(MINUTE, '$rec->{'ESTDay'} $rec->{'ESTTime'}', CONCAT(Date, ' ', Time) ) > 360,1,0))AS P3,

			SUM(IF(TIMESTAMPDIFF(MINUTE, '$rec->{'ESTDay'} $rec->{'ESTTime'}', CONCAT(Date, ' ', Time) ) BETWEEN -30 AND 90,Duration,0))AS D1, 
			SUM(IF(TIMESTAMPDIFF(MINUTE, '$rec->{'ESTDay'} $rec->{'ESTTime'}', CONCAT(Date, ' ', Time) ) BETWEEN 91 AND 360,Duration,0))AS D2, 
			SUM(IF(TIMESTAMPDIFF(MINUTE, '$rec->{'ESTDay'} $rec->{'ESTTime'}', CONCAT(Date, ' ', Time) ) > 360,Duration,0))AS D3				
			
			FROM sl_leads_calls WHERE ID_mediacontracts = '$rec->{'ID_mediacontracts'}' AND IO='In'");
			($rec->{'P1Calls'},$rec->{'P2Calls'},$rec->{'P3Calls'},$rec->{'P1CallsSec'},$rec->{'P2CallsSec'},$rec->{'P3CallsSec'})=$sth2->fetchrow();
			

		## Totals 
		$rec->{'tcalls'} = $rec->{'P1Calls'}+$rec->{'P2Calls'}+$rec->{'P3Calls'};
		$rec->{'qOrders'} = $tmp->{'P1qtyTDC'}+$tmp->{'P2qtyTDC'}+$tmp->{'P3qtyTDC'}+$tmp->{'P1qtyCOD'}+$tmp->{'P2qtyCOD'}+$tmp->{'P3qtyCOD'};
		$rec->{'tOrders'} = $tmp->{'P1totTDC'}+$tmp->{'P2totTDC'}+$tmp->{'P3totTDC'}+$tmp->{'P1totCOD'}+$tmp->{'P2totCOD'}+$tmp->{'P3totCOD'};		
		
		## CPC
		if ($rec->{'tcalls'}>0){
			$rec->{'cpc'} = &round($rec->{'Cost'}/$rec->{'tcalls'},2);
			$rec->{'conv'} = &round($rec->{'qOrders'}/$rec->{'tcalls'}*100,2);
		}else{
			$rec->{'cpc'} =  0;
			$rec->{'conv'} = 0;
		}
		if ($rec->{'tOrders'}>0){
			$rec->{'tottdc'} = $tmp->{'P1totTDC'}+$tmp->{'P2totTDC'}+$tmp->{'P3totTDC'};
			
		}else{
			$rec->{'ptdc'} =  0;
			$rec->{'ratio'} =  0;
		}
		if ($rec->{'Cost'}>1){  ## Cost .01 no llevan ratio
			$rec->{'ratio'} = &round($rec->{'tOrders'}/$rec->{'Cost'},2);
		}else{
			$rec->{'ratio'} = 0;
		}
		if ($rec->{'qOrders'}>0){
			$rec->{'cpo'} = &round($rec->{'Cost'}/$rec->{'qOrders'},2);
			$rec->{'aov'} = &round($rec->{'tOrders'}/$rec->{'qOrders'},2)
		}else{
			$rec->{'cpo'} = 0;
			$rec->{'aov'} = 0;
		}
		
		my $q ="REPLACE INTO sl_mediacontracts_stats SET
					ID_mediacontracts=$rec->{'ID_mediacontracts'},
					Calls = '$rec->{'tcalls'}',
					CPC   = '$rec->{'cpc'}',
					Conv  = '$rec->{'conv'}',
					QtyOrders = '$rec->{'qOrders'}',
					TotOrders = '$rec->{'tOrders'}',
					TotTDC = '$rec->{'tottdc'}',
					CPO = '$rec->{'cpo'}',
					AOV = '$rec->{'aov'}',
					Ratio = '$rec->{'ratio'}',
					FamProd = '". &product_family($rec->{'Offer'})."',
					Date = CURDATE(),
					Time = CURTIME(),
					ID_admin_users = 1;";
		my ($sth2) = &Do_SQL($q);
		$str .="$q<br><br>";
		++$c;
	}
	$va{'message'} .= &trans_txt('done') . " : ". $c;
	delete($in{'action'});
	&dev_home;
}


#	Function: agent_bonus: Para cualquier cambio, copiar esta funcion desde cron_scripts
#
#	Created by:
#		_Carlos Haas_
#
#	Modified By:
#
#		Roberto Barcenas on 03/05/2012: Function results revised againts original excel formula
#
#   	Parameters:
#
#		agent: ID_admin_users
#		day_start: Period Starting Point
#		day_end: Period Ending Point
#
#   	Returns:
#
#		An array with data containing information about the bonus for the agent
#
#   	See Also:
#
sub agent_bonus {

	my ($agent, $day_start, $day_end) = @_;
	my $sth, $str_sql;
	my $str_status;
	my $base_order=0;
	my $pot_base_order=0;
	my $base_sale=0;
	my $pot_base_sale=0;
	my $pct=0;
	my $qty_orders=0;
	my $total_orders=0;
	my $total_orders_tdc=0;
	my $qty_sales = 0;
	my $total_sales=0;
	my $pot_total_sales=0;
	my $ticket_prom=0;
	my $pot_ticket_prom=0;
	my $Conv_TDC=0;
	my $pot_Conv_TDC=0;
	my $orders_data=0;
	my $bonus_data_amt=0;
	my $discount_data_amt=0;
	my $pot_orders_data=0;
	my $pot_bonus_data_amt=0;
	my $pot_discount_data_amt=0;
	my $total_orders_bonus=0;

	my $str_orders='';
	my @ary_orders;

	delete($usr{'user_type'});
	(!$usr{'user_type'}) and ($usr{'user_type'}=&load_name('admin_users','ID_admin_users',$agent,'user_type'));

	$str_sql = "SELECT pbase_order, pbase_sale, fulldata_bonus, cs_discount FROM sl_rewards WHERE user_type='$usr{'user_type'}' AND Status='Active' ";
	$sth=&Do_SQL($str_sql);
	my ($pbase_order, $pbase_sale, $bonus_data, $discount_data) = $sth->fetchrow();

	## User Type Agent available for bonus?
	if($pbase_order or $pbase_sale){

			## Quantity Orders / Total Orders / Total orders TDC
			$str_sql = "SELECT Status,
					COUNT(*)AS Quantity,
					SUM(OrderNet)AS Amount,
					SUM(IF(Ptype='Credit-Card',OrderNet,0))AS TDC
					FROM sl_orders WHERE Date BETWEEN '$day_start' AND '$day_end'
					AND ID_admin_users = $agent GROUP BY Status;";
			$sth=&Do_SQL($str_sql);
			while(my($status,$qty,$amt,$tdc) = $sth->fetchrow()){
				$str_orders .= "$qty;$amt;$tdc|";
				push(@ary_orders, $status);

				#if($status !~ /Void|System/){
					$qty_orders += $qty;
					$total_orders += $amt;
					$total_orders_tdc += $tdc;
				#}

				$total_orders_bonus += $status !~ /Void|System/ ? $amt : 0;
			}
			chop($str_orders);

			## Quantity Sales / Total Sales
			$str_sql = "SELECT COUNT(OrderNet), SUM(OrderNet) FROM sl_orders WHERE PostedDate BETWEEN '$day_start' AND '$day_end' AND ID_admin_users = $agent; ";
			$sth=&Do_SQL($str_sql);
			($qty_sales, $total_sales) = $sth->fetchrow_array();

			## Potential Quantity Sales	/ Total Sales / Total  Sales TDC
			$str_sql = "SELECT COUNT(OrderNet), SUM(OrderNet), SUM(IF(Ptype='Credit-Card',OrderNet,0)) FROM sl_orders WHERE ID_admin_users = $agent AND Status IN ('New', 'Processed', 'Pending'); ";
			$sth=&Do_SQL($str_sql);
			my ($pot_qty_sales, $pot_total_sales, $pot_sales_tdc) = $sth->fetchrow_array();


			## Data Bonus / Data Discount
			$str_sql = "SELECT
						COUNT(*)AS Total_Orders_Qty,
						/*GROUP_CONCAT(ID_orders)AS ID_orders*/
						SUM(IF(DataDiscount = 0 AND LENGTH(Phone1) >= 10 AND (LENGTH(Phone2) >= 10 OR LENGTH(Cellphone) >= 10) AND Email LIKE '%@%',1,0))AS Total_Data_Qty,
						SUM(DataDiscount)AS Total_Discount_Qty,
						SUM(IF(DataDiscount = 0 AND LENGTH(Phone1) >= 10 AND (LENGTH(Phone2) >= 10 OR LENGTH(Cellphone) >= 10) AND Email LIKE '%@%' ,$bonus_data,0))AS Bonus_Data,
						SUM(IF(DataDiscount > 0,$discount_data,0))AS Discount_Data FROM
					(
						SELECT ID_customers,ID_orders,SUM(IF(Type = 'C.E.L C/ERROR',1,0))AS DataDiscount
						FROM
						(
							SELECT ID_customers,ID_orders FROM sl_orders
							WHERE Date BETWEEN '$day_start' AND '$day_end'
							AND ID_admin_users = '$agent'
							AND Status NOT IN('Void','System Error')
						)tmp2
						INNER JOIN sl_orders_notes
						USING(ID_orders)
						GROUP BY tmp2.ID_orders
					)tmp
					INNER JOIN sl_customers USING(ID_customers);";

			$sth=&Do_SQL($str_sql);
			($orders_data, $bonus_data_qty, $discount_data_qty, $bonus_data_amt, $discount_data_amt) = $sth->fetchrow();


			## Potential Data Bonus / Data Discount
			$str_sql = "SELECT
						COUNT(*)AS Total_ORders,
						SUM(IF(DataDiscount = 0 AND LENGTH(Phone1) >= 10 AND LENGTH(Phone2) >= 10 AND Email LIKE '%@%' ,$bonus_data,0))AS Bonus_Data,
						SUM(IF(DataDiscount > 0,$discount_data,0))AS Discount_Data FROM
					(
						SELECT ID_customers,ID_orders,SUM(IF(Type = 'C.E.L C/ERROR',1,0))AS DataDiscount
						FROM
						(
							SELECT ID_customers,ID_orders FROM sl_orders
							WHERE ID_admin_users = '$agent'
							AND Status NOT IN('Void','System Error')
						)tmp2
						INNER JOIN sl_orders_notes
						USING(ID_orders)
						GROUP BY tmp2.ID_orders
					)tmp
					INNER JOIN sl_customers USING(ID_customers);";

			$sth=&Do_SQL($str_sql);
			($pot_orders_data, $pot_bonus_data_amt, $pot_discount_data_amt) = $sth->fetchrow();


			## Sales OR Orders
			if ($qty_orders or $qty_sales){

					## Ticket Prom
					if ($qty_sales) {
						$ticket_prom = $total_sales / $qty_sales;
					}

					## Potential Ticket Prom
					if ($pot_qty_sales) {
						$pot_ticket_prom = $pot_total_sales / $pot_qty_sales;
					}

					## TDC Conversion
					if ($total_orders_tdc) {
						$Conv_TDC = $total_orders_tdc / $total_orders;
					}
					(!$Conv_TDC) and ($Conv_TDC=0);


					## Potential TDC Conversion
					if ($pot_total_sales) {
						$pot_Conv_TDC = $pot_sales_tdc / $pot_total_sales;
					}
					(!$pot_Conv_TDC) and ($pot_Conv_TDC=0);

					## Order Bonus
					if ($pbase_order) {
						$base_order = $total_orders_bonus * $pbase_order / 100;
					}
					(!$base_order) and ($base_order=0);

					$str_sql = "SELECT
					IF($Conv_TDC*100>tdc_55,tdc_c55*100/100,
					IF($Conv_TDC*100>tdc_45,IF(($Conv_TDC*100-tdc_45-2)>0,( POW(2,(1 +($Conv_TDC*100-tdc_45-2)/3)) / POW(2,(1 +(tdc_55-tdc_45-2)/3))) * (tdc_c55-tdc_c45)+tdc_c45,tdc_c45*100/100),
					IF($Conv_TDC*100>tdc_35,IF(($Conv_TDC*100-tdc_35-2)>0,( POW(2,(1 +($Conv_TDC*100-tdc_35-2)/3)) / POW(2,(1 +(tdc_45-tdc_35-2)/3))) * (tdc_c45-tdc_c35)+tdc_c35,tdc_c35*100/100),
					IF($Conv_TDC*100>tdc_25,IF(($Conv_TDC*100-tdc_25-2)>0,( POW(2,(1 +($Conv_TDC*100-tdc_25-2)/3)) / POW(2,(1 +(tdc_35-tdc_25-2)/3))) * (tdc_c35-tdc_c25)+tdc_c25,tdc_c25*100/100),
					IF($Conv_TDC*100>tdc_10,IF(($Conv_TDC*100-tdc_10-2)>0,( POW(2,(1 +($Conv_TDC*100-tdc_10-2)/3)) / POW(2,(1 +(tdc_25-tdc_10-2)/3))) * (tdc_c25-tdc_c10)+tdc_c10,tdc_c10*100/100), 0
					)))))
					FROM sl_rewards WHERE user_type='$usr{'user_type'}' AND Status='Active'; ";

					$sth=&Do_SQL($str_sql);
					$bono_tdc = eval($sth->fetchrow());
					(!$bono_tdc) and ($bono_tdc=0);

					## Potential TDC Bonus
					$str_sql = "SELECT
							IF($pot_Conv_TDC*100>tdc_55,tdc_c55*100/100,
							IF($pot_Conv_TDC*100>tdc_45,IF(($pot_Conv_TDC*100-tdc_45-2)>0,( POW(2,(1 +($pot_Conv_TDC*100-tdc_45-2)/3)) / POW(2,(1 +(tdc_55-tdc_45-2)/3))) * (tdc_c55-tdc_c45)+tdc_c45,tdc_c45*100/100),
							IF($pot_Conv_TDC*100>tdc_35,IF(($pot_Conv_TDC*100-tdc_35-2)>0,( POW(2,(1 +($pot_Conv_TDC*100-tdc_35-2)/3)) / POW(2,(1 +(tdc_45-tdc_35-2)/3))) * (tdc_c45-tdc_c35)+tdc_c35,tdc_c35*100/100),
							IF($pot_Conv_TDC*100>tdc_25,IF(($pot_Conv_TDC*100-tdc_25-2)>0,( POW(2,(1 +($pot_Conv_TDC*100-tdc_25-2)/3)) / POW(2,(1 +(tdc_35-tdc_25-2)/3))) * (tdc_c35-tdc_c25)+tdc_c25,tdc_c25*100/100),
							IF($pot_Conv_TDC*100>tdc_10,IF(($pot_Conv_TDC*100-tdc_10-2)>0,( POW(2,(1 +($pot_Conv_TDC*100-tdc_10-2)/3)) / POW(2,(1 +(tdc_25-tdc_10-2)/3))) * (tdc_c25-tdc_c10)+tdc_c10,tdc_c10*100/100), 0
							)))))
					FROM sl_rewards WHERE user_type='$usr{'user_type'}' AND Status='Active'; ";

					$sth=&Do_SQL($str_sql);
					$pot_bono_tdc = eval($sth->fetchrow());
					(!$pot_bono_tdc) and ($pot_bono_tdc=0);

					## Ticket Bonus
					$str_sql = "SELECT IF($ticket_prom>ticket_200,ticket_c200*100/100,
					  IF($ticket_prom>ticket_170,IF(($ticket_prom-ticket_170-2)>0,( POW(2,(1 +($ticket_prom-ticket_170-2)/3)) / POW(2,(1 +(ticket_200-ticket_170-2)/3))) * (ticket_c200-ticket_c170)+ticket_c170,ticket_c170*100/100),
					  IF($ticket_prom>ticket_160,IF(($ticket_prom-ticket_160-2)>0,( POW(2,(1 +($ticket_prom-ticket_160-2)/3)) / POW(2,(1 +(ticket_170-ticket_160-2)/3))) * (ticket_c170-ticket_c160)+ticket_c160,ticket_c160*100/100),
					  IF($ticket_prom>ticket_150,IF(($ticket_prom-ticket_150-2)>0,( POW(2,(1 +($ticket_prom-ticket_150-2)/3)) / POW(2,(1 +(ticket_160-ticket_150-2)/3))) * (ticket_c160-ticket_c150)+ticket_c150,ticket_c150*100/100),
					  IF($ticket_prom>ticket_140,IF(($ticket_prom-ticket_140-2)>0,( POW(2,(1 +($ticket_prom-ticket_140-2)/3)) / POW(2,(1 +(ticket_150-ticket_140-2)/3))) * (ticket_c150-ticket_c140)+ticket_c140,ticket_c140*100/100), 0
					)))))
					FROM sl_rewards WHERE user_type='$usr{'user_type'}' AND Status='Active'; ";
					$sth=&Do_SQL($str_sql);
					$bono_ticket = eval($sth->fetchrow());
					(!$bono_ticket) and ($bono_ticket=0);

					## Potential Ticket Bonus
					$str_sql = "SELECT IF($pot_ticket_prom>ticket_200,ticket_c200*100/100,
					  IF($pot_ticket_prom>ticket_170,IF(($pot_ticket_prom-ticket_170-2)>0,( POW(2,(1 +($pot_ticket_prom-ticket_170-2)/3)) / POW(2,(1 +(ticket_200-ticket_170-2)/3))) * (ticket_c200-ticket_c170)+ticket_c170,ticket_c170*100/100),
					  IF($pot_ticket_prom>ticket_160,IF(($pot_ticket_prom-ticket_160-2)>0,( POW(2,(1 +($pot_ticket_prom-ticket_160-2)/3)) / POW(2,(1 +(ticket_170-ticket_160-2)/3))) * (ticket_c170-ticket_c160)+ticket_c160,ticket_c160*100/100),
					  IF($pot_ticket_prom>ticket_150,IF(($pot_ticket_prom-ticket_150-2)>0,( POW(2,(1 +($pot_ticket_prom-ticket_150-2)/3)) / POW(2,(1 +(ticket_160-ticket_150-2)/3))) * (ticket_c160-ticket_c150)+ticket_c150,ticket_c150*100/100),
					  IF($pot_ticket_prom>ticket_140,IF(($pot_ticket_prom-ticket_140-2)>0,( POW(2,(1 +($pot_ticket_prom-ticket_140-2)/3)) / POW(2,(1 +(ticket_150-ticket_140-2)/3))) * (ticket_c150-ticket_c140)+ticket_c140,ticket_c140*100/100), 0
					)))))
					FROM sl_rewards WHERE user_type='$usr{'user_type'}' AND Status='Active'; ";
					$sth=&Do_SQL($str_sql);
					$pot_bono_ticket = eval($sth->fetchrow());
					(!$pot_bono_ticket) and ($pot_bono_ticket=0);

					## Sale completed Bonus
					$base_sale  = round($pbase_sale + $bono_ticket + $bono_tdc,2) * $total_sales / 100;
					$pct = $base_sale * 100 / $total_sales if $base_sale > 0;
					#print "Agente:$agent<br>Ventas: $qty_sales<br>Venta Total:$total_sales<br>Ticket Promedio: $ticket_prom<br>Conversion TDC:$Conv_TDC<br>";
					#print "Comision Venta(%): ". $base_sale * 100 / $total_sales ."<br>";
					#print "ComisionVenta($base_sale)  = (Bonofijo($pbase_sale) + BonoTicket($bono_ticket) + BonoTDC($bono_tdc)) * VentaTotal($total_sales) / 100<br>";

			}  # 
			$pot_base_sale  = round($pbase_sale + $pot_bono_ticket + $pot_bono_tdc,2) * $pot_total_sales / 100;
			#print "Potencial: $pot_base_sale  = int($pbase_sale + $pot_bono_ticket + $pot_bono_tdc) * $pot_total_sales / 100;<br>";
			#print "qty_orders = $qty_orders ,qty_sales = $qty_sales, base_order = $base_order, base_sale = $base_sale, pot_base_sale = $pot_base_sale, pbase_order = $pbase_order, pbase_sale = $pbase_sale, bono_ticket = $bono_ticket, pot_bono_ticket = $pot_bono_ticket, bono_tdc = $bono_tdc, pot_bono_tdc = $pot_bono_tdc, ticket_prom = $ticket_prom, pot_ticket_prom = $pot_ticket_prom, Conv_TDC = $Conv_TDC, pot_Conv_TDC = $pot_Conv_TDC<hr>";	#&cgierr(scalar @ary_orders);
			#&cgierr();
	}  # $pbase_order or $pbase_sale
	#print "qty_orders = $qty_orders ,qty_sales = $qty_sales, base_order = $base_order, base_sale = $base_sale, pot_base_sale = $pot_base_sale, pbase_order = $pbase_order, pbase_sale = $pbase_sale, bono_ticket = $bono_ticket, pot_bono_ticket = $pot_bono_ticket, bono_tdc = $bono_tdc, pot_bono_tdc = $pot_bono_tdc, ticket_prom = $ticket_prom, pot_ticket_prom = $pot_ticket_prom, Conv_TDC = $Conv_TDC, pot_Conv_TDC = $pot_Conv_TDC<hr>";	#&cgierr(scalar @ary_orders);
	return ($total_orders_tdc, $base_order, $base_sale, $pot_base_sale, $pbase_order, $pbase_sale, $bonus_data, $discount_data, $bono_ticket, $pot_bono_ticket, $bono_tdc, $pot_bono_tdc, $ticket_prom, $pot_ticket_prom, $Conv_TDC, $pot_Conv_TDC, $orders_data, $qty_orders, $bonus_data_qty, $bonus_data_amt, $discount_data_qty, $discount_data_amt, $pot_orders_data, $pot_bonus_data_amt, $pot_discount_data_amt, $qty_sales, $total_sales, $str_orders, @ary_orders);

}  # End function

sub devrun_ecommerce_orders_by_source {
###############################################################
###############################################################
	
	#print "\nCreando Reporte Ecommerce By Source\n";

	## From Date / To Date  is Always last month
#	my $sth = Do_SQL("SELECT
#	                 CONCAT(DATE_FORMAT(LAST_DAY(CURDATE() - INTERVAL 1 MONTH),'%Y-%m-'),'01')AS FromDate,
#					 LAST_DAY(CURDATE() - INTERVAL 1 MONTH)AS ToDate 
#	/*'2012-01-01' AS FromDate, '2012-10-31' AS ToDate*/ ;");
#	my($from_date, $to_date) = $sth->fetchrow();
	my($from_date) = '2012-10-01';
	my($to_date)   = &get_sql_date();

	my $query_tot = "SELECT COUNT(*) FROM sl_orders
					INNER JOIN
					(
					 	SELECT ID_admin_users FROM admin_users WHERE user_type IN ('Internet','Recompras')
					 	AND ID_admin_users <> 4182
					 )tmp
					USING(ID_admin_users)
					WHERE sl_orders.Date BETWEEN '$from_date' AND '$to_date'
					AND Status <> 'System Error';";

	my $query_list = "SELECT 
						sl_orders.ID_orders, 
						sl_orders.ID_admin_users, 
						Website, 
						sl_orders.Date,
						IF(WebCreator IS NULL,0,WebCreator)AS WebCreator,  
						AmazonID,
						IF(WebCreator IS NOT NULL AND AmazonID IS NULL,'Customer Service',
							IF(AmazonID IS NOT NULL AND tmp5.ID_orders IS NULL,'Amazon',
							IF(AmazonID IS NOT NULL AND tmp5.ID_orders IS  NOT NULL,'Amazon FBA', 'Ecommerce'))
						)AS Source, 
						shp_State AS OrderState,
						Saleprice, 
						Shipping, 
						Tax, 
						Cost,
						Status
					FROM sl_orders
					INNER JOIN
					(
					 	SELECT ID_admin_users, LastName AS Website FROM admin_users WHERE user_type IN ('Internet','Recompras')
					 	AND ID_admin_users <> 4182
					 )tmp
					USING(ID_admin_users)
					INNER JOIN 
					(
						SELECT 
							ID_orders,
							SUM(Saleprice)AS Saleprice,
							SUM(Shipping)AS Shipping,
							SUM(Tax)AS Tax,
							SUM(Cost)AS Cost
					 	FROM sl_orders_products
					 	WHERE Saleprice > 0
					 	AND Status = 'Active'
					 	AND Date BETWEEN '$from_date' AND DATE_ADD('$to_date', INTERVAL 10 DAY)
						GROUP BY ID_orders
					)tmp2 /* Suma Productos */
					USING(ID_orders)
					LEFT JOIN 
					(
					 	SELECT ID_orders, ID_admin_users AS WebCreator FROM sl_orders_notes WHERE Type = 'Web Creator'
					 	GROUP BY ID_orders 
					 )tmp3 /* Nota Ecommerce Phone */
					USING(ID_orders)
					LEFT JOIN 
					(
					 	SELECT ID_orders,Notes AS AmazonID FROM sl_orders_notes WHERE Type = 'AmazonID'
					 	GROUP BY ID_orders 
					 )tmp4 /* Nota AmazonID */
					USING(ID_orders)
					LEFT JOIN 
					(
					 	SELECT ID_orders FROM sl_orders_notes WHERE Notes = 'The Order has been Fulfilled and Shipped by Amazon' 
					 	GROUP BY ID_orders 
					 )tmp5 /* Nota Amazon FBA */
					USING(ID_orders)
					WHERE sl_orders.Date BETWEEN '$from_date' AND '$to_date' 
					AND Status <> 'System Error'
					ORDER BY ID_orders;";


	my ($sth) = &Do_SQL($query_tot);
	$matches = $sth->rows();

	if($matches) {
		my $fname   = 'ecommerce_by_source_'.$from_date.'_to_'.$to_date.'.csv';
		
		print "Content-type: application/octetstream\n";
		print "Content-disposition: attachment; filename=$fname\n\n";
		print "ID Order,Date,Source,Website,Web Creator,Amazon ID,Order State,Order Net,Order Shipping,Order Tax,Order Cost,Order Status\r\n";

	    my ($sth) = &Do_SQL($query_list);

	    my $row=1;
	    while ($orders = $sth->fetchrow_hashref){
	    	$web_creator = !$orders->{'WebCreator'} ? 'N/A' : &load_db_names('admin_users','ID_admin_users',$orders->{'WebCreator'},'[FirstName] [LastName]');
			print "$orders->{'ID_orders'},$orders->{'Date'},$orders->{'Source'},$orders->{'Website'},$web_creator,$orders->{'AmazonID'},$orders->{'OrderState'},$orders->{'Saleprice'},$orders->{'Shipping'},$orders->{'Tax'},$orders->{'Cost'},$orders->{'Status'}\r\n";
    	}
	}else{
		delete($in{'cmd'});
		$va{'message'} = "No se encontraron ordenes ecommerce...\n";
		dev_home;
	}
   
}

1;

