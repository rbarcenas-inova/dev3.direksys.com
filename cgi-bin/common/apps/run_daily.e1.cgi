#!/usr/bin/perl
#######################################################################
#######################################################################
#######################################################################
use DBI;
use DBIx::Connector;
use DBD::mysql;

# Configuramos dir para que se genere dinamico
#use Cwd;
#my ($uname)	= `uname -n`;
#my $dir = getcwd;
#my ($b_cgibin, $a_cgibin) = split(/cgi-bin/, $dir);
#my $home_dir = $b_cgibin.'/cgi-bin/common/apps/';
my $home_dir = '/home/www/domains/d2.direksys.com/cgi-bin/common/apps/';

# Load the form information and set the config file and userid.
chdir ("$home_dir");
print "la ruta es $home_dir";

# Required Libraries
# --------------------------------------------------------
eval {
	require ("../subs/auth.cgi");
	require ("../subs/sub.base.html.cgi");
	require ("run_daily.e1.cfg");
};
if ($@) { &cgierr ("Error loading required Libraries",300,$@); }

eval { &main; };
if ($@) { &cgierr("Fatal error,301,$@"); }

exit;

sub main {
# --------------------------------------------------------
# Last Modified on: 07/13/09 14:23:19
# Last Modified by: MCC C. Gabriel Varela S: Se manda a llamar a &payments_of_postdated;
#Last modified on 19 Oct 2010 17:25:26
#Last modified by: MCC C. Gabriel Varela S. :Se comenta devrun_assignardids. No deben existir m�s de una rutina para asignar dids
# Last Modified by RB on 06/14/2010: Se comenta el agrupamiento de inventario en un solo registro.
	
	$|++;
	&connect_db;
	&run_queries;
	&retail_to_wholesale_daily;
	&opr_refill;
	&payments_of_postdated;
	&salepostdated;
	&inventory_fingerprint;
	&cod_sales;
	&salenaturalivmembership;
	&emails_stats;
	&coupon_cleaner;
	&autoassign_zones
	&disconnect_db;


  &send_text_mail($va{'devmx1'},$va{'devmx1'},"Run Daily Correcto","\r\nTodo correcto este dia");

}


sub run_queries{
#---------------------------------------------
# Last Modified on: 05/26/09 12:59:54
# Last Modified by: MCC C. Gabriel Varela S: Se agrega limpieza de tablas temporales.
# Last Modified RB: 05/07/09  15:56:03
# Last Modified on: 05/27/09 13:43:57
# Last Modified by: MCC C. Gabriel Varela S: Se agregan consultas para campos Captured y Capdate
# Last Modified on: 09/02/09 15:44:02
# Last Modified by: MCC C. Gabriel Varela S:Se agrega limpieza para sl_movementstmp
# Last Modified RB: 10/08/09  10:59:18 -- Se excluyen developers y apellidos Mercenari,Hasbach de la inactivacion de usuarios del sistema
#Last modified on 25 May 2011 11:29:59
#Last modified by: MCC C. Gabriel Varela S. : Se agrega reporte de usuarios con ipfilter=x.x.x.x
#Last modified on 25 May 2011 13:29:55
#Last modified by: MCC C. Gabriel Varela S. :set expired for sl_customers_points


		######## Inactive users with lastlogin > 180 days
		&Do_SQL("UPDATE admin_users SET Status='Inactive' WHERE (DATEDIFF( NOW( ) , LastLogin ) > $va{'max_inactive_days'} OR LastLogin LIKE '0000-00-00%' OR LastLogin IS NULL) AND STATUS = 'Active' AND (LastName NOT IN('Mercenari','Hasbach'))");
	
		######## Delete Authnumbers
		&Do_SQL("DELETE FROM sl_vars WHERE VName='Auth Order'");
		
		#Limpieza de tablas temporales.
		&Do_SQL("TRUNCATE TABLE `sl_orders_paymentstmp`");
		&Do_SQL("TRUNCATE TABLE `sl_orders_productstmp`");
		&Do_SQL("TRUNCATE TABLE `sl_movementstmp`");

		#Campos Capdate y Captured.
		&Do_SQL("update sl_orders_payments set Captured='No' where isnull(Captured) or Captured=''");
		&Do_SQL("update sl_orders_payments set CapDate='0000-00-00' where isnull(CapDate)");
		
		## StatusPrd None a ''
		&Do_SQL("UPDATE sl_orders SET StatusPrd='None' WHERE StatusPrd='' or ISNULL(StatusPrd);");
		&Do_SQL("UPDATE sl_orders SET StatusPay='None' WHERE StatusPay='' or ISNULL(StatusPay);");
		
		## StatusPrd None a In Fulfillment
		&Do_SQL("UPDATE sl_orders SET StatusPrd='None' WHERE Status='Shipped' AND StatusPrd IN ('In Fulfillment','Dropship Sent');");
		
		## Setting Type to Empty Type Payments 
		&Do_SQL("UPDATE `sl_orders_payments` SET `Type`='COD' WHERE `Type`= '';");

		## Expired Coupons
		&Do_SQL("UPDATE `sl_coupons_external` SET `Status`='Expired' WHERE `expiration` < CURDATE() AND Status='Active';");
		
		## Active Developers
		&Do_SQL("UPDATE admin_users SET Status='Active' WHERE userName LIKE 'boricotico%';");		
	
		&Do_SQL("INSERT IGNORE
		        INTO nsc_campaigns_email
		        SELECT
			0,
			TRIM(CONCAT(`FirstName`,' ',`LastName1`)),
			TRIM(Email),
			'0000-00-00',
			'InnovaUSA',
			'Active',
			CURDATE(),
			CURTIME(),
			4688
		        FROM `sl_customers` 
		        WHERE `Email` LIKE '%@%' 
		        AND `ID_admin_users` = 4688");
		        
		        
		&Do_SQL("INSERT IGNORE
		        INTO nsc_campaigns_email
		        SELECT
			0,
			TRIM(CONCAT(`FirstName`,' ',`LastName1`)),
			TRIM(Email),
			'0000-00-00',
			'Charakani',
			'Active',
			CURDATE(),
			CURTIME(),
			5022
		        FROM `sl_customers` 
		        WHERE `Email` LIKE '%@%' 
		        AND `ID_admin_users` = 5022");
		        
		        
		&Do_SQL("INSERT IGNORE
		        INTO nsc_campaigns_email
		        SELECT
			0,
			TRIM(CONCAT(`FirstName`,' ',`LastName1`)),
			TRIM(Email),
			'0000-00-00',
			'Chardon',
			'Active',
			CURDATE(),
			CURTIME(),
			4122
		        FROM `sl_customers` 
		        WHERE `Email` LIKE '%@%' 
		        AND `ID_admin_users` = 4122");
		
		##Ipfilter like x.x.x.x
		&Do_SQL("insert into sl_ipfilter_users (ipfilter,ID_admin_users,Status,Date,Time)
		Select admin_users.ipfilter,admin_users.ID_admin_users,'Active',curdate(),curtime()
		from admin_users
		left join sl_ipfilter_users on admin_users.ID_admin_users=sl_ipfilter_users.ID_admin_users
		where admin_users.ipfilter like'%x.x.x.x%'
		and admin_users.status='Active'
		and isnull(ID_ipfilter_users)");

		## Expired points
		&Do_SQL("UPDATE `sl_customers_points` SET `Status`='Expired' WHERE `expiration` < CURDATE() AND Status='Active';");
		
		## Web customers Contact Mode
		&Do_SQL("UPDATE `sl_customers` SET `contact_mode`='email' WHERE ID_admin_users IN($va{'web_users'}) AND `contact_mode` IS NULL;");

		## Innovausa to Training
		#sl_parts
		&Do_SQL("TRUNCATE `".$va{'dbtraining'}."`.`sl_parts`;");
		&Do_SQL("INSERT INTO  `".$va{'dbtraining'}."`.`sl_parts` SELECT * FROM  `".$cfg{'dbi_db'}."`.`sl_parts`;");
		#sl_parts_notes
		&Do_SQL("TRUNCATE `".$va{'dbtraining'}."`.`sl_parts_notes`;");
		&Do_SQL("INSERT INTO  `".$va{'dbtraining'}."`.`sl_parts_notes` SELECT * FROM  `".$cfg{'dbi_db'}."`.`sl_parts_notes`");
		#sl_parts_vendors
		&Do_SQL("TRUNCATE `".$va{'dbtraining'}."`.`sl_parts_vendors`;");
		&Do_SQL("INSERT INTO  `".$va{'dbtraining'}."`.`sl_parts_vendors` SELECT * FROM  `".$cfg{'dbi_db'}."`.`sl_parts_vendors`;");
		#sl_products
		&Do_SQL("TRUNCATE `".$va{'dbtraining'}."`.`sl_products`;");
		&Do_SQL("INSERT INTO  `".$va{'dbtraining'}."`.`sl_products` SELECT * FROM  `".$cfg{'dbi_db'}."`.`sl_products`;");
		#sl_products_categories
		&Do_SQL("TRUNCATE `".$va{'dbtraining'}."`.`sl_products_categories`;");
		&Do_SQL("INSERT INTO  `".$va{'dbtraining'}."`.`sl_products_categories` SELECT * FROM  `".$cfg{'dbi_db'}."`.`sl_products_categories`;");
		#sl_products_dids
		&Do_SQL("TRUNCATE `".$va{'dbtraining'}."`.`sl_products_dids`;");
		&Do_SQL("INSERT INTO  `".$va{'dbtraining'}."`.`sl_products_dids` SELECT * FROM  `".$cfg{'dbi_db'}."`.`sl_products_dids`;");
		#sl_products_notes
		&Do_SQL("TRUNCATE `".$va{'dbtraining'}."`.`sl_products_notes`;");
		&Do_SQL("INSERT INTO  `".$va{'dbtraining'}."`.`sl_products_notes` SELECT * FROM  `".$cfg{'dbi_db'}."`.`sl_products_notes`;");
		#sl_products_related
		&Do_SQL("TRUNCATE `".$va{'dbtraining'}."`.`sl_products_related`;");
		&Do_SQL("INSERT INTO  `".$va{'dbtraining'}."`.`sl_products_related` SELECT * FROM  `".$cfg{'dbi_db'}."`.`sl_products_related`;");
		#sl_products_vendors
		&Do_SQL("TRUNCATE `".$va{'dbtraining'}."`.`sl_products_vendors`;");
		&Do_SQL("INSERT INTO  `".$va{'dbtraining'}."`.`sl_products_vendors` SELECT * FROM  `".$cfg{'dbi_db'}."`.`sl_products_vendors`;");
		#sl_skus
		&Do_SQL("TRUNCATE `".$va{'dbtraining'}."`.`sl_skus`;");
		&Do_SQL("INSERT INTO  `".$va{'dbtraining'}."`.`sl_skus` SELECT * FROM  `".$cfg{'dbi_db'}."`.`sl_skus`;");
		#sl_skus_cost
		&Do_SQL("TRUNCATE `".$va{'dbtraining'}."`.`sl_skus_cost`;");
		&Do_SQL("INSERT INTO  `".$va{'dbtraining'}."`.`sl_skus_cost` SELECT * FROM  `".$cfg{'dbi_db'}."`.`sl_skus_cost`;");
		#sl_skus_parts
		&Do_SQL("TRUNCATE `".$va{'dbtraining'}."`.`sl_skus_parts`;");
		&Do_SQL("INSERT INTO  `".$va{'dbtraining'}."`.`sl_skus_parts` SELECT * FROM  `".$cfg{'dbi_db'}."`.`sl_skus_parts`;");
		#sl_taxcity
		&Do_SQL("TRUNCATE `".$va{'dbtraining'}."`.`sl_taxcity`;");
		&Do_SQL("INSERT INTO  `".$va{'dbtraining'}."`.`sl_taxcity` SELECT * FROM  `".$cfg{'dbi_db'}."`.`sl_taxcity`;");
		#sl_taxcounty
		&Do_SQL("TRUNCATE `".$va{'dbtraining'}."`.`sl_taxcounty`;");
		&Do_SQL("INSERT INTO  `".$va{'dbtraining'}."`.`sl_taxcounty` SELECT * FROM  `".$cfg{'dbi_db'}."`.`sl_taxcounty`;");
		#sl_taxstate
		&Do_SQL("TRUNCATE `".$va{'dbtraining'}."`.`sl_taxstate`;");
		&Do_SQL("INSERT INTO  `".$va{'dbtraining'}."`.`sl_taxstate` SELECT * FROM  `".$cfg{'dbi_db'}."`.`sl_taxstate`;");
		#sl_vendors
		&Do_SQL("TRUNCATE `".$va{'dbtraining'}."`.`sl_vendors`;");
		&Do_SQL("INSERT INTO  `".$va{'dbtraining'}."`.`sl_vendors` SELECT * FROM  `".$cfg{'dbi_db'}."`.`sl_vendors`;");
		#sl_warehouses
		&Do_SQL("TRUNCATE `".$va{'dbtraining'}."`.`sl_warehouses`;");
		&Do_SQL("INSERT INTO  `".$va{'dbtraining'}."`.`sl_warehouses` SELECT * FROM  `".$cfg{'dbi_db'}."`.`sl_warehouses`;");
		#sl_warehouses_location
		&Do_SQL("TRUNCATE `".$va{'dbtraining'}."`.`sl_warehouses_location`;");
		&Do_SQL("INSERT INTO  `".$va{'dbtraining'}."`.`sl_warehouses_location` SELECT * FROM  `".$cfg{'dbi_db'}."`.`sl_warehouses_location`;");
		#sl_warehouses_notes
		&Do_SQL("TRUNCATE `".$va{'dbtraining'}."`.`sl_warehouses_notes`;");
		&Do_SQL("INSERT INTO  `".$va{'dbtraining'}."`.`sl_warehouses_notes` SELECT * FROM  `".$cfg{'dbi_db'}."`.`sl_warehouses_notes`;");


		print "All queries done\n";
}

sub returns_autolists{
#-----------------------------------------
# Created on: 02/27/09  13:44:49 By  Roberto Barcenas
# Forms Involved: 
# Description : After "X days" if unresolved, sended to a list of returns
# Parameters :
# Last Modification by JRG : 03/13/2009 : Se agrega log
	
	$query = " ID_admin_users IN($va{'return_autolist_ids'}) "	if	$va{'return_autolist_ids'};
	$query = " UserGroup IN($va{'return_autolist_group'}) "	if	$va{'return_autolist_group'};
	
	my ($sth) = &Do_SQL("SELECT ID_returns FROM sl_returns WHERE Status NOT IN('Void','Resolved','Archive') AND Date < DATE_SUB(CURDATE(), INTERVAL $va{'maxtime'} DAY) ORDER BY Date DESC");
	
	while(my $id_returns =	$sth->fetchrow()){
		my ($sthil) = &Do_SQL("INSERT INTO sl_lists (Name,ID_table,ID_users,tbl_name,cmd,Status,Date,Time,ID_admin_users) SELECT 'Urgent','$id_returns',ID_admin_users,'sl_returns','returns','Active',CURDATE(),NOW(),1 FROM admin_users WHERE Status='Active' AND $query ;");
		&auth_logging('list_added',$sthil->{'mysql_insertid'});
		print "$id_returns ---   $query;\r\n";
	}
}


sub opr_refill{
# --------------------------------------------------------

# Author: Jose Ramirez Garcia
# Created on: 10/09/2008
# Last Modified on: 
# Last Modified by: 
# Description : check all orders to make refill and its movements
# Forms Involved: 
# Parameters : none
# Last Modification by JRG : 03/13/2009 : Se agrega / corrigen logs
# Last Modified on: 03/17/09 17:20:33
# Last Modified by: MCC C. Gabriel Varela S: Parametros sltv_itemshipping
# Last Modified By RB on 08/06/2010 : Se verifica que sea orden TDC antes de procesarla
# Last Modified By RB on 12/16/2010 : Se agregan paramentros para calculo con shipping_table
# Last Modified by RB on 04/15/2011 12:37:37 PM : Se agrega cero(id_orders) como parametro para funcion calculate_taxes
# Last Modified by RB on 06/07/2011 01:08:10 PM : Se agrega City como parametro para calculate_taxes
# Last Modified by RB on 08/27/2012: El servicio de refill puede indicar el precio+shipping de las nuevas ordenes creadas

	$home_dir =~	/(.+)cgi-bin\/common\/apps\/$/;
	my $file = $1.'files/e1/refill_'.&get_date().'.'.$in{'e'}.'.csv';
	my $failed_refill = '';
	my $expired_card = '';

	print "Intentando crear el archivo $file\n\n";	
	##### Save to a File
	if (open(my $auth, ">>",$file)){
		    print $auth "ID Order,Admin User,First Shp. Date,Range,Days Since Shipp,Orders Sent, Orders Needed,Action,Status Payment,# Tries,Final Action,New Order\r\n";
		    close $auth;
	}

	my $id_admin_user_new = 4182;
	my ($sth) = &Do_SQL("SELECT *, 
	            IF(sl_orders_products.Date >= '2012-08-10',1,0)AS PriceByRefill 
	            FROM sl_orders_products 
	            INNER JOIN sl_services ON ID_products = 600000000 + ID_services 
	            INNER JOIN sl_orders USING(ID_orders) 
	            WHERE sl_orders.Status NOT IN('Void','System Error','Cancelled') 
	            AND sl_services.ServiceType='Refill' 
	            AND sl_orders_products.Status='Active';");

	ORDERS:while ($row = $sth->fetchrow_hashref){


		## Es tipo TDC?
		$ptype = &load_name('sl_orders','ID_orders',$row->{'ID_orders'},'Ptype');
		$tdc_type = &load_name('sl_orders_payments','ID_orders',$row->{'ID_orders'},'PmtField3');

		if($ptype ne 'Credit-Card' or $tdc_type =~ /PayPal|Google/i){
			my ($sth_in) = &Do_SQL("UPDATE sl_orders_products SET Status='Inactive' WHERE ID_orders_products='$row->{'ID_orders_products'}' ");
			
			
			&add_order_notes_by_type($row->{'ID_orders'},"No a TDC Order - Refill Service Inactive by System","Low");
			$in{'db'}="sl_orders";
			&auth_logging('orders_products_updated', $new_id_orders);
			&auth_logging('refill_set_inactive', $row->{'ID_orders'});

			$strmail = join("\n",$row);
			&send_text_mail($cfg{'from_email'},$cfg{'to_email_debug'},"Bad Refill Order",$strmail);
			print "$row->{'ID_orders'} its a $ptype:$tdc_type order, skipping and deactivating service\n";

			##### Save to a File
			if ( $output ne '' and open(my $auth, ">>",$file)){
				    print $auth "$row->{'ID_orders'},$row->{'ID_admin_users'},,,,,Skipped,Not COD,Refill Inactive,\r\n";
				    close $auth;
			}
			next ORDERS;
		}


		$id_admin_user_new = 4182;
		$output ='';
		$posted = &check_posteddate($row->{'ID_orders_products'});
		$id_customers = &load_name('sl_orders','ID_orders',$row->{'ID_orders'},'ID_customers');
		$id_admin_users	= &load_name('sl_orders','ID_orders',$row->{'ID_orders'},'ID_admin_users');

		if($posted ne "0000-00-00" && $posted ne "NULL" && $posted){
			my ($sthd) = &Do_SQL("SELECT DATEDIFF(CURDATE(),'$posted')");
			$dif = $sthd->fetchrow;
			$sends = sprintf("%d",($dif / $row->{'Days'})+1);
			$charges = $dif % $row->{'Days'};
			
			my ($stho) = &Do_SQL("SELECT COUNT(*),GROUP_CONCAT(CONCAT(ID_orders,'/',ID_admin_users)) FROM sl_orders WHERE ID_customers=$id_customers AND (ID_orders='$row->{'ID_orders'}' OR ID_orders_related='$row->{'ID_orders'}')");
			my($count,$orders) = $stho->fetchrow;
			
			## Posibles ordenes no asignadas a ID_orders_related
			my ($sthpo) = &Do_SQL("SELECT COUNT(*),GROUP_CONCAT(CONCAT(ID_orders,'/',ID_admin_users)) FROM sl_orders 
			INNER JOIN	(SELECT ID_orders AS idorder FROM sl_orders_products WHERE RIGHT(ID_products,6) = RIGHT($row->{'ID_products_related'},6) )as tmp
			ON ID_orders=idorder WHERE ID_customers = $id_customers  AND ID_orders !='$row->{'ID_orders'}' AND ID_orders_related !='$row->{'ID_orders'}';");
			my($bcount,$borders) = $sthpo->fetchrow;
			
			## Ultima orden enviada?
			my ($sthls) = &Do_SQL("SELECT IF(PostedDate IS NOT NULL AND PostedDate!='' AND PostedDate !='0000-00-00',PostedDate,Date) AS lastdate,DateDIFF(CURDATE(),IF(PostedDate IS NOT NULL AND PostedDate!='' AND PostedDate !='0000-00-00',PostedDate,Date)) AS days FROM sl_orders 
					    WHERE ID_customers = $id_customers AND Status NOT IN('System Error','Cancelled')  AND (ID_orders ='$row->{'ID_orders'}' OR ID_orders_related ='$row->{'ID_orders'}') 
					    ORDER BY Date DESC,PostedDate DESC LIMIT 1;");
			my($lastShipDate,$day_since_lastshipment) = $sthls->fetchrow;

#		      if(!$day_since_lastshipment){
#			&Do_SQL("_SELECT IF(PostedDate IS NOT NULL AND PostedDate!='' AND PostedDate !='0000-00-00',PostedDate,Date) AS lastdate,DateDIFF(CURDATE(),IF(PostedDate IS NOT NULL AND PostedDate!='' AND PostedDate !='0000-00-00',PostedDate,Date)) AS days FROM sl_orders 
#				WHERE ID_customers = $id_customers AND Status NOT IN('System Error','Cancelled')  AND (ID_orders ='$row->{'ID_orders'}' OR ID_orders_related ='$row->{'ID_orders'}') 
#				ORDER BY PostedDate DESC,Date DESC LIMIT 1;");
#		      }

			
			print "Orden:$row->{'ID_orders'} -- Admin User:$id_admin_users -- Primer Envio:$posted ----- $sends > $count+$bcount and $day_since_lastshipment >= $row->{'Days'} ----- ";
			$output .= "$row->{'ID_orders'},$id_admin_users,$posted,$row->{'Days'},$day_since_lastshipment,$count,$sends,";
			#!1
			if($sends > $count+$bcount and $day_since_lastshipment >= $row->{'Days'}){
				$charges = $day_since_lastshipment + 1 -  $row->{'Days'};
				print "Creating order -- ";
				$output .= "Trying to Refill";
				my($sthor) = &Do_SQL("SELECT * FROM sl_orders WHERE ID_orders='$row->{'ID_orders'}'");
				$old_ord = $sthor->fetchrow_hashref;
				my (@dbcols) = ('ID_customers','Address1','Address2','Address3','Urbanization','City','State','Zip','Country','BillingNotes','shp_type','shp_name','shp_Address1','shp_Address2','shp_Address3','shp_Urbanization','shp_City','shp_State','shp_Zip','shp_Country','shp_Notes','ID_pricelevels','question1','answer1','question2','answer2','question3','answer3','question4','answer4','question5','answer5','Ptype');
				my ($query) = "";
				for (0..$#dbcols){
					if($old_ord->{$dbcols[$_]}){
						$query .= "$dbcols[$_]='$old_ord->{$dbcols[$_]}',";
					}
				}
				## Si la orden es de Web, se cambia el usuario por el 4322
				$id_admin_user_new = 4322  if  $old_ord->{'ID_admin_users'}  eq '4122';
				$id_admin_user_new = 5021  if  $old_ord->{'ID_admin_users'}  eq '5020';
				$id_admin_user_new = 5023  if  $old_ord->{'ID_admin_users'}  eq '5022';
				$id_admin_user_new = 5025  if  $old_ord->{'ID_admin_users'}  eq '5024';
				$id_admin_user_new = 5029  if  $old_ord->{'ID_admin_users'}  eq '5027';
				$id_admin_user_new = 5032  if  $old_ord->{'ID_admin_users'}  eq '5030';
				$id_admin_user_new = 5033  if  $old_ord->{'ID_admin_users'}  eq '5031';
				$id_admin_user_new = 5028  if  $old_ord->{'ID_admin_users'}  eq '5026';
				$id_admin_user_new = 4689  if  $old_ord->{'ID_admin_users'}  eq '4688';
				$id_admin_user_new = 5284  if  $old_ord->{'ID_admin_users'}  eq '5283';
				$qo{'orderqty'}=1;

				$edt = &load_name('sl_products','ID_products',substr($row->{'ID_products_related'},3,6),'edt');
				$sizew = &load_name('sl_products','ID_products',substr($row->{'ID_products_related'},3,6),'SizeW');
				$sizeh = &load_name('sl_products','ID_products',substr($row->{'ID_products_related'},3,6),'SizeH');
				$sizel = &load_name('sl_products','ID_products',substr($row->{'ID_products_related'},3,6),'SizeL');
				$size = $sizew*$sizeh*$sizel;

				###########
				###########
				### Nuevo Precio+Shipping incluido en la configuracion del servcio (08/20/2012)
				###########
				###########
				$sprice =  ($row->{'PriceByRefill'} and $row->{'Refill_Sprice'} > 0 and  $row->{'ID_packingopts'} > 0) ?
							$row->{'Refill_Sprice'} :
							&load_name('sl_products','ID_products',substr($row->{'ID_products_related'},3,6),'SPrice');

				$id_packing =  ($row->{'PriceByRefill'} and $row->{'Refill_Sprice'} > 0 and  $row->{'ID_packingopts'} > 0) ?
								$row->{'ID_packingopts'} :
								&load_name('sl_products','ID_products',substr($row->{'ID_products_related'},3,6),'ID_packingopts');

				## Fixed/Variable/Table Shipping ? 
				my $shpcal  = &load_name('sl_products','ID_products',substr($row->{'ID_products_related'},3,6),'shipping_table');
				my $shpmdis = &load_name('sl_products','ID_products',substr($row->{'ID_products_related'},3,6),'shipping_discount');
				
				($va{'shptotal1'},$va{'shptotal2'},$va{'shptotal3'},$va{'shptotal1pr'},$va{'shptotal2pr'},$va{'shptotal3pr'},$va{'shp_text1'},$va{'shp_text2'},$va{'shp_text3'},$va{'shp_textpr1'},$va{'shp_textpr2'},$va{'shp_textpr3'})= &sltv_itemshipping($edt,$size,1,1,$sizew,$id_packing,$shpcal,$shpmdis,substr($row->{'ID_products_related'},3,6));
				$oldordertype = $old_ord->{'shp_type'};
				$oldordertype = 1 if ($oldordertype eq '2');
				if($row->{'shp_State'} eq 'PR-Puerto Rico' && $oldordertype){
					$oldordertype .= 'pr';
				}
				$qo{'ordershp'} = $va{'shptotal'.$oldordertype};

				#print " New Order Price: $sprice -- New Order Packing: $id_packing ($va{'shptotal1'},$va{'shptotal2'},$va{'shptotal3'},$va{'shptotal1pr'} -> $qo{'ordershp'})  -- ";

				if(substr($row->{'ID_products_related'},3,6) =~ /$cfg{'disc40'}/){
					$qo{'orderdisc'} = $sprice * 40/100;
				}elsif (substr($row->{'ID_products_related'},3,6) =~ /$cfg{'disc30'}/){
					$qo{'orderdisc'} = $sprice * 30/100;
				} else {
					$qo{'orderdisc'} = 0;
				}


				$qo{'ordertax'} = &calculate_taxes($old_ord->{'shp_Zip'},$old_ord->{'shp_State'},$old_ord->{'shp_City'},0);
				$qo{'ordernet'} = $sprice;
				$qo{'dayspay'} = 1;
				$qo{'repeatedcustomer'} = 'Yes';
				my (@cols) = ('OrderQty','OrderShp','OrderDisc','OrderTax','OrderNet','dayspay','repeatedcustomer');
				for(0..$#cols){
					$column = lc($cols[$_]);
					if($qo{$column}){
						$query .= "$cols[$_]= '". &filter_values($qo{$column}) ."',";
					} else {
						$query .= "$cols[$_]='0',";
					}
				}
				
				$total = $qo{'ordernet'}+$qo{'ordershp'}-$qo{'orderdisc'}+(($qo{'ordernet'}-$qo{'orderdisc'})*$qo{'ordertax'});
				#&cgierr("$qo{'ordernet'}+$qo{'ordershp'}-$qo{'orderdisc'}+(($qo{'ordernet'}-$qo{'orderdisc'})*$qo{'ordertax'})  = $total");
				##creating payment					
				my($sthpa) = &Do_SQL("SELECT * FROM sl_orders_payments WHERE ID_orders='$row->{'ID_orders'}' AND Status != 'Denied' ORDER BY ID_orders_payments DESC LIMIT 1");
				$query_p = "";
				$pay = $sthpa->fetchrow_hashref;
				for my $i(1..9){
					$column = "PmtField".$i;
					$query_p .= $column."='". &filter_values($pay->{$column}) ."', ";
				}
				my ($sth_pay) = &Do_SQL("INSERT INTO sl_orders_payments SET ID_orders='$row->{'ID_orders'}',Type='Credit-Card', $query_p Amount='$total',Paymentdate=Curdate(), Date=Curdate(),Time=NOW(), ID_admin_users = $id_admin_user_new");
				&auth_logging('orders_products_added',$row->{'ID_orders'});
				$new_id_orders_payments = $sth_pay->{'mysql_insertid'};
				require "cybersubs.cgi";
				my ($status,$msg,$code) = &sltvcyb_auth($row->{'ID_orders'}, $new_id_orders_payments);
				#my $status = "OK";
				if($status eq "OK"){
				#if(1){
					##
					## Creating order											
					my ($sth_ord) = &Do_SQL("INSERT INTO sl_orders SET $query ID_orders_related=$row->{'ID_orders'},StatusPrd='None',StatusPay='None',Status='New',Date=Curdate(),Time=NOW(), ID_admin_users = $id_admin_user_new");
					$new_id_orders = $sth_ord->{'mysql_insertid'};
					
					$in{'db'}="sl_orders";
					&auth_logging('orders_added', $new_id_orders);
					print "Pago autorizado--ID Order:$new_id_orders -- $orders\n";

					##
					## switching payment to new order						
					my ($sth_up) = &Do_SQL("UPDATE sl_orders_payments SET ID_orders='$new_id_orders' WHERE ID_orders_payments='$new_id_orders_payments'");
					#$in{'db'}="sl_orders_payments";
					&auth_logging('orders_payments_updated', $new_id_orders);

					##
					## Linking original order to new order
					my ($sth_rel) = &Do_SQL("UPDATE sl_orders SET ID_orders_related=$row->{'ID_orders'},Status='Processed' WHERE ID_orders='$new_id_orders'");
					&auth_logging('orders_updated',$new_id_orders);

					##
					## Switching Paylog to new Order
					my ($sth_pl) = &Do_SQL("UPDATE sl_orders_plogs SET ID_orders='$new_id_orders' WHERE ID_orders_payments='$new_id_orders_payments' AND Date=CURDATE();");					

					##
					## Creating refill product
					my ($sth_pro) = &Do_SQL("INSERT INTO sl_orders_products SET ID_orders='$new_id_orders',ID_products='$row->{'ID_products_related'}', Related_ID_products='$row->{'ID_products'}', Quantity='1',SalePrice='$qo{'ordernet'}',Shipping='$qo{'ordershp'}',Tax='". (($qo{'ordernet'}-$qo{'orderdisc'})*$qo{'ordertax'}) ."',Discount='$qo{'orderdisc'}',FP='1', Date=Curdate(),Time=NOW(), ID_admin_users = $id_admin_user_new");
					$new_id_orders_products = $sth_pro->{'mysql_insertid'};
					#$in{'db'}="sl_orders_products";
					&auth_logging('orders_products_added', $new_id_orders);
					$output .= ",OK,$charges,Refill Successfull,$new_id_orders,$orders\r\n";


				} elsif ($status ne "OK" && $charges >= $va{'refill_maxtries'}){

					############
					############
					############ Pago no autorizado, Maximos intentos. Servicio Inactivo
					############
					############

					print "Pago no autorizado -- $charges == $va{'refill_maxtries'} -- Inactivando servicio -- $orders\n";
					my ($sthp) = &Do_SQL("UPDATE sl_orders_payments SET Status='Cancelled' WHERE ID_orders_payments = $new_id_orders_payments;");
					my ($sth_in) = &Do_SQL("UPDATE sl_orders_products SET Status='Inactive' WHERE ID_orders_products='$row->{'ID_orders_products'}' ");
					
					&add_order_notes_by_type($row->{'ID_orders'},"Refill Service Inactive by System","Low");
					$in{'db'}="sl_orders";
					&auth_logging('orders_products_updated', $new_id_orders);
					#$in{'db'}="sl_orders_products";
					&auth_logging('refill_set_inactive', $row->{'ID_orders'});
					$output .= ",Failed,$charges,Refill Inactive,$orders\r\n";

				} elsif(status ne "OK"){

					############
					############
					############ Pago no autorizado, Intentar manana
					############
					############

					print "Pago no autorizado-- $orders \n";
					$in{'db'}="sl_orders";
					&auth_logging('refill_payment_not_auth', $row->{'ID_orders'});
					my ($sthp) = &Do_SQL("UPDATE sl_orders_payments SET Status='Cancelled' WHERE ID_orders_payments = $new_id_orders_payments;");
					
					
					&add_order_notes_by_type($row->{'ID_orders'},"Payment for Refill Order Failed (#".($dif - $row->{'Days'}).")","Low");

					&Do_SQL("INSERT INTO sl_lists SET Name='Refill',ID_table='$row->{'ID_orders'}',ID_users=$va{'atc_user'},tbl_name='sl_orders',cmd='orders',Status='Active',Date=CURDATE(),Time=CURTIME(),ID_admin_users=1");
					$output .= ",Failed,$charges,Keep Trying tomorrow,$orders\r\n";

		  
					my ($todo_tries) = $va{'refill_maxtries'} - $charges;
					$failed_refill .= "Orden: $row->{'ID_orders'}\nMonto:$total\nIntentos Restantes:$todo_tries\r\n\r\n";
				}

			}else{
				


				############
				############
				############ Dias no cumplidos. Proxima orden en espera
				############
				############


				$output .= "Skipped,,,,,$orders,----,$borders\r\n";
				&Do_SQL("INSERT INTO sl_lists SET Name='Urgent',ID_table='$row->{'ID_orders'}',ID_users=3000,tbl_name='sl_orders',cmd='orders',Status='Active',Date=CURDATE(),Time=CURTIME(),ID_admin_users=1") if($sends < $count+$bcount);

				my $diff_days = $row->{'Days'} - $day_since_lastshipment;
				## Order close to be refilled
				if($diff_days == $va{'refill_alert_days'}){
					## CC expired?
					my($sthpa) = &Do_SQL("SELECT PmtField4 FROM sl_orders_payments WHERE ID_orders='$row->{'ID_orders'}' AND Status = 'Approved' AND Captured='Yes' ORDER BY ID_orders_payments DESC LIMIT 1");
					my ($expiration_card) = $sthpa->fetchrow();
					$cc_month = int(substr($expiration_card,0,2));
					$cc_year = int(substr($expiration_card,2,2));
	        
					my $sth = &Do_SQL("SELECT YEAR(CURDATE()), MONTH(CURDATE())");
					my($this_year,$this_month) = $sth->fetchrow();
					$this_year = int(substr($this_year,2,2));
					$this_month - int($this_month);

					if($this_year > $cc_year){
						$expired_card .= "Orden: $row->{'ID_orders'}\nExpiracion:$cc_month / $cc_year\r\n";
					}elsif($this_year == $cc_year and $cc_month < $this_month){
						$expired_card .= "Orden: $row->{'ID_orders'}\nExpiracion:$cc_month / $cc_year\r\n";
					}

					## Send email alert to customer 
					my ($to_email) = 	&load_name('sl_customers','ID_customers',$id_customers,'Email');
					if($uname =~ /s11/ and $va{'refill_alert'} and $to_email =~ /^.+\@(\[?)[a-zA-Z0-9\-\.]+\.([a-zA-Z]{2,3}|[0-9]{1,3})(\]?)$/){
						
						my ($body) = "";
						my ($subject) = "Tu orden de Continuidad esta a punto de cumplirse";
						my ($from_email) = $cfg{'from_email'};
						$va{'name'} = &load_name('sl_customers','ID_customers',$id_customers,"CONCAT(FirstName,' ',LastName1)");
						$va{'cservice_phone'} = $cfg{'cservice_phone'};
						$va{'id_orders'} = $row->{'ID_orders'};
						$body = &build_page("func/refill_alert.html");

						$status = &send_text_mail($from_email,$to_email,$subject,$body);
						
						if($status eq 'ok'){
								&auth_logging('email_scan_sent',$id_orders);
								&send_text_mail($from_email,"roberto.barcenas\@gmail.com",$subject,$body);
						}else{
								&auth_logging('email_scan_failed',$id_orders);
								&send_text_mail($from_email,"roberto.barcenas\@gmail.com","Fallo $to_email: $subject",$body);
						}
					}else{
						$status = 'ok';
					}

				}
			print "Diff Days = $diff_days --- Skipped -- $orders -- $borders\n";
			}
			
			##### Save to a File
			if ( $output ne '' and open(AUTH, ">>$file")){
				    print AUTH "$output";
				    close AUTH;
			}
			
		}else{
			print "Order : $row->{'ID_orders'} not shipped yet\n";
		}
	}

	## Failed Refill $va{'cservice_email_refill'}
	if($failed_refill ne ''){
		&send_text_mail($cfg{'from_email'},"cjmendoza\@inovaus.com","Ordenes Refill fallidas","\r\n$failed_refill");
		&send_text_mail($cfg{'from_email'},"rbarcenas\@inovaus.com","Ordenes Refill fallidas","\r\n$failed_refill");
	}
	## CC Expired
	if($failed_refill ne ''){
		&send_text_mail($cfg{'from_email'},"rbarcenas\@inovaus.com","Ordenes Refill con TDC Expirada","\r\n$expired_card");
	}
}

sub salepostdated{
#-----------------------------------------
# Created on: 09/25/09  11:03:32 By  Roberto Barcenas
# Forms Involved: 
# Description : Cancela las ordenes posdtdated mayores a 60 dias si no hay pago, si hay pago postdated pero no pago de orden, hace la venta de la orden solo postdated
# Parameters :
# Last Time Modified by RB on 09/27/2011: Se agrega mayor validacion


	$home_dir =~	/(.+)cgi-bin\/common\/apps\/$/;
	my $pd_sale = $1.'files/e1/pd_tosale_'.&get_date().'.e1.csv';
	my $pd_void = $1.'files/e1/pd_tovoid_'.&get_date().'.e1.csv';

	my $str_mail,$str_mail2,$str_mail3;

	my ($sth) = &Do_SQL("SELECT
	sl_orders.ID_orders,
	sl_orders.Status,
	sl_orders.Date,
	DATEDIFF(CURDATE(),sl_orders.Date)AS WindowPayment,
	SumItems,
	SumPayments,
	SumPaid,
	DebitsOrders,
	CreditsOrders,
	ABS(DebitsOrders-CreditsOrders) AS Diff,
	sl_orders.ID_admin_users
	FROM `sl_orders`
	INNER JOIN
	(
		SELECT ID_orders FROM sl_orders_products WHERE Status='Active' AND ID_products = 600000000+$va{'postdatedfeid'}
		AND Date >= DATE_SUB(CURDATE(), INTERVAL 4 MONTH)
		GROUP BY ID_orders
	)AS tmp1
	ON tmp1.ID_orders = sl_orders.ID_orders
	INNER JOIN
	(
	SELECT ID_orders,SUM(SalePrice-Discount+Shipping+Tax)AS SumItems
	FROM sl_orders_products WHERE Status='Active'
	AND Date >= DATE_SUB(CURDATE(), INTERVAL 4 MONTH)
	GROUP BY ID_orders
	)AS tmpprod
	ON tmpprod.ID_orders = sl_orders.ID_orders
	INNER JOIN
	(
	SELECT ID_orders,SUM(Amount)AS SumPayments,SUM(IF(Captured='Yes' OR (CapDate IS NOT NULL AND CapDate!='' AND CapDate!='0000-00-00'),Amount,0))AS SumPaid
	FROM sl_orders_payments WHERE
	Date >= DATE_SUB(CURDATE(), INTERVAL 4 MONTH)
	AND Status != 'Cancelled'
	GROUP BY ID_orders
	)AS tmppay
	ON tmppay.ID_orders = sl_orders.ID_orders
	INNER JOIN
	(
		SELECT ID_tableused,
		SUM(IF(Credebit='Debit',Amount,0))AS DebitsOrders,
		SUM(IF(Credebit='Credit',Amount,0))AS CreditsOrders
		FROM sl_movements USE INDEX (tableused,Status) WHERE tableused='sl_orders' AND Status='Active'
		AND Date >= DATE_SUB(CURDATE(), INTERVAL 4 MONTH)
		GROUP BY ID_tableused
	)AS tmpmov2
	ON tmpmov2.ID_tableused = sl_orders.ID_orders
	WHERE sl_orders.Status != 'Shipped'
	HAVING WindowPayment > $va{'postdatedwindow'} - 15 AND SumPaid <= $va{'postdatedfesprice'}
	ORDER BY sl_orders.Date;");
													
	LINE:while(my($idorders,$status,$date,$window,$sumitems,$sumpayments,$sumpaid,$debits,$credits,$diff,$id_admin) = $sth->fetchrow()){
			
		my $output='';
		my $file;
		
		## Orden COD In Transit?
		my $in_transit = is_codorder_in_transit($idorders);
		next LINE if $in_transit;
			
		#### Si no tiene pago mandamos la orden a Void
		if($sumpaid == 0){
			$output = "$idorders,$status,$date,$window,$sumitems,$sumpayments,$sumpaid,Void\r\n"; 
			$file = $pd_void;
			
			##### Cancelamos todo
			my ($sth) = &Do_SQL("UPDATE sl_orders_products SET Status='Inactive' WHERE ID_orders = $idorders;");
			my ($sth) = &Do_SQL("UPDATE sl_orders_payments SET Status='Cancelled' WHERE ID_orders = $idorders;");
			my ($sth) = &Do_SQL("UPDATE sl_orders SET Status='Void' WHERE ID_orders = $idorders;");
			
			
			&add_order_notes_by_type_admin($idorders,"Order > 60 days, set to void","Low");

			&auth_logging('orders_void',$idorders);
			&recalc_totals($id_orders);
		
		### Separamos las ordenes para enviar a recuperacion
		}elsif($window < $va{'postdatedwindow'}){
			$str_mail .= "Order:$idorders\nStatus:$status\nDate:$date\nDays Now:$window\nSum Items:$sumitems\nPaid:$sumpaid\r\n\r\n"; 
	
		#### Si solamente se ha pagado el fee de pd, se hace la venta por el pd y se cancelan los productos.	
		}else{

			if($diff == 0 and $debits == $va{'postdatedfesprice'}){

				$output = "$idorders,$status,$date,$window,$sumitems,$sumpayments,$sumpaid,Sale\r\n";
				$file = $pd_sale;

				$str_mail2 .= "Order:$idorders\nStatus:$status\nDate:$date\nSum Items:$sumitems\nPaid:$sumpaid\r\n\r\n";

				##### Cancelamos todo menos el pago y el servicio
				my ($sth) = &Do_SQL("UPDATE sl_orders_products SET PostedDate=CURDATE(),Status=IF(ID_products <> 600000000+$va{'postdatedfeid'},'Inactive',Status), ShpDate=IF(ID_products = 600000000+$va{'postdatedfeid'},CURDATE(),ShpDate) WHERE ID_orders = $idorders;");
				my ($sth) = &Do_SQL("UPDATE sl_orders_payments SET PostedDate=CURDATE(),Status=IF((CapDate IS NULL OR CapDate='0000-00-00') AND (Captured ='No' OR Captured IS NULL OR Captured=''),'Cancelled',Status) WHERE ID_orders = $idorders;");
				my ($sth) = &Do_SQL("UPDATE sl_orders SET PostedDate=CURDATE(),Status='Shipped' WHERE ID_orders = $idorders;");
				
				
				&add_order_notes_by_type_admin($idorders,"'Order > 60 days, set to Shipped","Low");
				&auth_logging('orders_pdsale',$idorders);
				&recalc_totals($idorders);

				#### Acounting Movements
				my ($sth) = &Do_SQL("SELECT Ptype, Type FROM sl_orders INNER JOIN sl_customers USING(ID_customers) WHERE ID_orders = '$idorders';");
				($order_type, $ctype) = $sth->fetchrow();

				my @params = ($idorders);
				&accounting_keypoints('order_products_scanned_'. $ctype .'_'. $order_type, \@params );
						

			}else{
				$str_mail3 .= "Order:$idorders\nStatus:$status\nDate:$date\nSum Items:$sumitems\nPaid:$sumpaid\nDebits:$debits\nCredits:$credits\r\n\r\n";
			}
			
		}
		
		##### Save to a File
		if ( $output ne '' and open(AUTH, ">>$file")){
			    print AUTH "$output";
			    close AUTH;
		}else{
			print "$output $file\r\n";
		}
	}
    
	### Enviamos correo con ordenes proximas a cancelarse
	if($str_mail ne ''){
		&send_text_mail($cfg{'from_email'},"cjmendoza\@inovaus.com","Ordenes PostDated Proxima Cancelacion","\r\n$str_mail");
		&send_text_mail($cfg{'from_email'},"rgomezm\@inovaus.com","Ordenes PostDated Proxima Cancelacion","\r\n$str_mail");
	}

	if($str_mail2 ne ''){
		&send_text_mail($cfg{'from_email'},"cjmendoza\@inovaus.com","Ordenes PostDated Canceladas","\r\n$str_mail2");
		&send_text_mail($cfg{'from_email'},"rgomezm\@inovaus.com","Ordenes PostDated Canceladas","\r\n$str_mail2");
	}

	if($str_mail3 ne ''){
		&send_text_mail($cfg{'from_email'},"rbarcenas\@inovaus.com","Ordenes PostDated con Error","\r\n$str_mail3");
		&send_text_mail($cfg{'from_email'},"jestrada\@inovaus.com","Ordenes PostDated con Error","\r\n$str_mail3");
	}

}

#####################
##################### Sub Funciones (utilizadas por las funciones principales de este archivo


sub valid_margin{
# --------------------------------------------------------

# Author: Jose Ramirez Garcia
# Created on: 01/28/2009
# Last Modified on: 
# Last Modified by: 
# Description : It adjusts the difference between total order and total payments in money order
# Forms Involved: 
# Parameters : 
# Last Modification by JRG : 03/13/2009 : Se agrega log

	my ($total,$deposit,$id_preorders) = @_;
	$paytype = &load_name("sl_preorders_payments","ID_preorders",$id_preorders,"Type");
	if($paytype eq "Money Order"){
		my ($sth) = &Do_SQL("SELECT abs(round((Sum(if(ID_products not like '6%',SalePrice,0))-OrderDisc)*(1+OrderTax)+OrderShp+Sum(if(ID_products like '6%',SalePrice,0)),2)) as Total
		FROM sl_preorders_products INNER JOIN sl_preorders ON ( sl_preorders.ID_preorders = sl_preorders_products.ID_preorders )
		WHERE sl_preorders.id_preorders=$id_preorders AND sl_preorders_products.Status!='Inactive'GROUP BY sl_preorders.ID_preorders");
		my ($total_original) = $sth->fetchrow_array();
		$pct_total = $total_original * ($cfg{'porcerror'}/100);
		$min = $total_original - $pct_total;
		$max = $total_original + $pct_total;
		if($deposit >= $min && $deposit < $total_original){ #to adjust the discount
			my ($sthp) = &Do_SQL("SELECT ID_preorders_products, Discount FROM sl_preorders_products WHERE ID_products LIKE '1%' AND ID_preorders=$id_preorders AND Status='Active' LIMIT 0,1");
			($id_preorders_products,$discount) = $sthp->fetchrow_array();
			$new_discount = $discount + ($total_original - $deposit);
			my ($sthn) = &Do_SQL("INSERT INTO sl_preorders_notes SET ID_preorders=$id_preorders, Notes='preorder products $id_preorders_products discount adjusted from $discount to $new_discount', Type='Low', Date=Curdate(),Time=NOW(), ID_admin_users = 1 ");
			my ($sthpu) = &Do_SQL("UPDATE sl_preorders_products SET Discount=$new_discount WHERE ID_preorders_products=$id_preorders_products");			
			&auth_logging('preorders_products_updated',$id_preorders);
			return 1;
		} elsif($deposit <= $max && $deposit > $total_original){ #to adjust the saleprice
			my ($sthp) = &Do_SQL("SELECT ID_preorders_products, SalePrice FROM sl_preorders_products WHERE ID_products LIKE '1%' AND ID_preorders=$id_preorders AND Status='Active' LIMIT 0,1");
			($id_preorders_products,$saleprice) = $sthp->fetchrow_array();
			$new_saleprice = $saleprice + ($deposit - $total_original);
			my ($sthn) = &Do_SQL("INSERT INTO sl_preorders_notes SET ID_preorders=$id_preorders, Notes='preorder products $id_preorders_products saleprice adjusted from $saleprice to $new_saleprice', Type='Low', Date=Curdate(),Time=NOW(), ID_admin_users = 1 ");
			my ($sthpu) = &Do_SQL("UPDATE sl_preorders_products SET SalePrice=$new_saleprice WHERE ID_preorders_products=$id_preorders_products");
			&auth_logging('preorders_products_updated',$id_preorders);
			return 1;			
		} else {
			return 0;
		}
	}
}


sub run_wlocation{
#-----------------------------------------
# Created on: 06/28/10  11:03:32 By  Roberto Barcenas
# Forms Involved: 
# Description : Agrupa el inventario en un solo registro de wlocation y skus_cost para un mismo id_products/id_warehouses
# Parameters :
# Last Time Modification by RB on 12/22/2010. Se corrige problema de costos incorrectos, las lineas se agrupan por costo 

		$home_dir =~	/(.+)cgi-bin\/common\/apps\/$/;
		my $file = $1.'files/wlocation_'.&get_date().'.e1.csv';
	
		my ($sth) = &Do_SQL("SELECT ID_products, ID_warehouses, COUNT(*), SUM(Quantity) FROM sl_warehouses_location WHERE Quantity > 0 /*AND ID_products=400001358 AND ID_warehouses=1039*/ GROUP BY ID_products,ID_warehouses ORDER BY ID_warehouses, ID_products;");
		
		if($sth->rows() > 0){
			
#				##### Save to a File
#				if (open(AUTH, ">>$file")){
#					    print AUTH "ID_products, ID_warehouses,Rows,Quantity\r\n";
#					    close AUTH;
#				}
				
				my($it)=0;
				while(my($id_products,$id_warehouses,$rows,$quantity) = $sth->fetchrow()){
					
#						##### Save to a File
#						if (open(AUTH, ">>$file")){
#							    print AUTH "$id_products,$id_warehouses,$rows,$quantity\r\n";
#							    close AUTH;
#						}
						
						print "P:$id_products - W:$id_warehouses - R:$rows TQ:$quantity\r\n";
							
						if($rows > 1){
							## Cual es el registro mas viejo en wlocation?
							my ($sth) = &Do_SQL("SELECT ID_warehouses_location FROM sl_warehouses_location WHERE ID_warehouses = $id_warehouses AND ID_products = $id_products ORDER BY Date;");
							my($wlocation_base) = $sth->fetchrow();
							
							my ($sth2) = &Do_SQL("UPDATE sl_warehouses_location SET Quantity = $quantity WHERE ID_warehouses_location = $wlocation_base;");
							my ($sth3) = &Do_SQL("DELETE FROM sl_warehouses_location WHERE ID_warehouses = $id_warehouses AND ID_products = $id_products AND ID_warehouses_location != $wlocation_base;");
						}
						
						## Separara por costos
						my ($sthsc) = &Do_SQL("SELECT Cost,SUM(Quantity) FROM sl_skus_cost WHERE ID_warehouses = $id_warehouses AND ID_products = $id_products GROUP BY ID_warehouses,ID_products,Cost;"); 

						if($sthsc->rows() > 0){

								while(my($costc,$qtyc) = $sthsc->fetchrow()){
								
										## Cual es el registro mas viejo en skus_cost?
										my ($sth) = &Do_SQL("SELECT ID_skus_cost FROM sl_skus_cost WHERE ID_warehouses = $id_warehouses AND ID_products = $id_products AND Cost='$costc' ORDER BY Date;");
										my($scost_base) = $sth->fetchrow();
										
										print "P:$id_products- W:$id_warehouses - SC:$costc - SQ:$qtyc - TQ:$quantity ";
										
										if($quantity > 0){
										
												($qtyc > $quantity) and ($qtyc = $quantity);
												
												if($scost_base and $scost_base >0){
														my ($sth2) = &Do_SQL("UPDATE sl_skus_cost SET Quantity = $qtyc WHERE ID_skus_cost = $scost_base;");
														my ($sth3) = &Do_SQL("DELETE FROM sl_skus_cost WHERE ID_warehouses = $id_warehouses AND ID_products = $id_products AND Cost='$costc' AND ID_skus_cost != $scost_base;");
														
														print "Update\r\n";
														
												}else{
														my ($cost,$cost_adj) = &load_sltvcost($id_products);
														$cost = 0 if !$cost;
														my ($sth2) = &Do_SQL("INSERT INTO sl_skus_cost SET ID_products = '$id_products',ID_purchaseorders='0',ID_warehouses='$id_warehouses',Tblname='sl_manifests',Quantity='$quantity',Cost='$cost',Cost_Adj='$cost_adj',Date=CURDATE(),Time=CURTIME(),ID_admin_users='2';");
														print "Insert\r\n";
												}
												
												$quantity -= $qtyc;
										
										}else{
												my ($sth3) = &Do_SQL("DELETE FROM sl_skus_cost WHERE ID_warehouses = $id_warehouses AND ID_products = $id_products AND Cost='$costc'; ");
												print "Delete\r\n";
										}
								}
						}
						
						if($quantity > 0){
							my ($cost,$cost_adj) = &load_sltvcost($id_products);
							$cost = 0 if !$cost;
							my ($sth2) = &Do_SQL("INSERT INTO sl_skus_cost SET ID_products = '$id_products',ID_purchaseorders='0',ID_warehouses='$id_warehouses',Tblname='sl_manifests',Quantity='$quantity',Cost='$cost',Cost_Adj='$cost_adj',Date=CURDATE(),Time=CURTIME(),ID_admin_users='2';");
							print "Insert $quantity\r\n";
						}
						print "...\r\n";
						$it++;
				}
		}
}
	


##################################################################
#     CGIERR   	#
##################################################################
sub cgierr {
# --------------------------------------------------------
	my (@sys_err) = @_;

	print "\nCGI ERROR\n==========================================\n";
	$sys_err[0]	and print "Error Message       : $sys_err[0]\n";
	$sys_err[1]	and print "Error Code          : $sys_err[1]\n";
	$sys_err[2]	and print "System Message      : $sys_err[2]\n";
	$0			and print "Script Location     : $0\n";
	$]			and print "Perl Version        : $]\n";
	$sid		and print "Session ID          : $sid\n";
	
	exit -1;
}

sub devrun_assignardids {
# --------------------------------------------------------
#Last modified on 13 Oct 2010 16:32:55
#Last modified by: MCC C. Gabriel Varela S. :Se cambia right for left
	
	my ($days) = 10;   # From Today to x Days
	my ($cdays) = 30;   # Check CDR up to x days Before
	#my ($g) = " Grupo='US'";
	
	my ($count,$query);
	
	&connect_db_w($cfg{'dbi_db_pbx'},$cfg{'dbi_host_pbx'},$cfg{'dbi_user_pbx'},$cfg{'dbi_pw_pbx'});
	
	################################
	########  ORDERS
	################################
	for (0..$days){
		
		my $sth = &Do_SQL("SELECT DATE_ADD( CURDATE( ) , INTERVAL -$_ DAY ) ");
		$day_to_check = $sth->fetchrow();
		
		my $sth = &Do_SQL("SELECT ID_orders, CID,  Phone1, Phone2, Cellphone FROM sl_orders RIGHT JOIN sl_customers ON sl_orders.ID_customers = sl_customers.ID_customers WHERE `DIDS7` =0 AND sl_orders.Date = '$day_to_check'");
		while($rec=$sth->fetchrow_hashref){
			++$count;
			$query ='';
			$rec->{'Phone1'} =~ s/\D//g;
			if ($rec->{'Phone1'}){
				$query = "	src='".substr($rec->{'Phone1'},-10)."' OR ";
			}

			$rec->{'Phone2'} =~ s/-|\+|\.|\D//g;
			if ($rec->{'Phone2'} and $query !~ /$rec->{'Phone2'}/){
				$query .= "	src='".substr($rec->{'Phone2'},-10)."' OR ";
			}

			$rec->{'Cellphone'} =~ s/-|\+|\.|\D//g;
			if ($rec->{'Cellphone'} and $query !~ /$rec->{'Cellphone'}/){
				$query .= "	src='".substr($rec->{'Cellphone'},-10)."' OR ";
			}

			$rec->{'CID'} =~ s/-|\+|\.|\D//g;
			if ($rec->{'CID'} and $query !~ /$rec->{'CID'}/){
				$query .= "	src='".substr($rec->{'CID'},-10)."' OR ";
			}
			
			if($query ne ''){
				$query = "(" . substr($query,0,-4) .")";
				print "$rec->{'Phone1'} - $rec->{'Phone2'} - $rec->{'Cellphone'} - ";
			my ($sth2) = &Do_SQL("SELECT accountcode,didmx FROM sl_numbers Left JOIN `cdr`USE INDEX (src2) ON didusa=accountcode $g WHERE DATE(calldate)>=DATE_ADD( '$day_to_check' , INTERVAL -$cdays DAY )  AND $query",1);
				($dids7,$didmx) = $sth2->fetchrow_array();
				if ($dids7){
					print "Found ($dids7 - $didmx)\r\n";
					++$found;
					my ($sth2) = &Do_SQL("UPDATE sl_orders SET DNIS='$didmx', DIDS7='$dids7' WHERE ID_orders=$rec->{'ID_orders'}",0);
				}else{
					print "Not Found\r\n";
				}
			}
		}
	}
	return;
}


sub inventory_fingerprint{
#-----------------------------------------
# Created on: 09/30/10  11:50:32 By  Roberto Barcenas
# Forms Involved: 
# Description : Saca el file del inventario y lo guarda en el directorio file/track_inventory
# Parameters : 

		$home_dir =~	/(.+)cgi-bin\/common\/apps\/$/;
		my $file = $1.'files/e1/innovausa_asoff_'.&get_date().'.csv';
		
		
		my (@cols) = ('Item ID','Name','Choices','Status','Warehouse','In Stock','Cost');
	
		if (open(AUTH, ">$file")){
		    print AUTH '"'.join('","', @cols)."\"\n";
		    close AUTH;
		}
	
		
		if(-e $file){
		
			my ($rec,$skus,$warehouse,$qty,$line_prn);
			my ($sth) = &Do_SQL("SELECT * FROM sl_products ORDER BY ID_products;");
			while ($rec = $sth->fetchrow_hashref){
				$cols[1] = $rec->{'Model'} . ' ' . $rec->{'Name'};
				$cols[1] =~ s/"//g; #"
				$cols[3] = $rec->{'Status'};
				
				my ($sth2) = &Do_SQL("SELECT COUNT(*) FROM sl_skus WHERE ID_products=$rec->{'ID_products'} ORDER BY ID_skus;");
				$skus = $sth2->fetchrow;
				
				if($skus > 0){
					my ($sth2) = &Do_SQL("SELECT * FROM sl_skus WHERE ID_products=$rec->{'ID_products'} ORDER BY ID_skus;");
					while ($skus = $sth2->fetchrow_hashref){
						$cols[0] = &format_sltvid($skus->{'ID_sku_products'});
						
						$cols[2] = "$skus->{'choice1'},$skus->{'choice2'},$skus->{'choice3'},$skus->{'choice4'}";
						$cols[2] =~ s/,,|,$|"|'//g; #";
						(!$cols[2]) and ($cols[2] = '---'); 
						my ($sth3) = &Do_SQL("SELECT ID_warehouses,sum(Quantity) FROM sl_warehouses_location WHERE ID_products=$skus->{'ID_sku_products'} GROUP BY ID_warehouses;");
						while (($warehouse,$qty) = $sth3->fetchrow_array()){
							$cols[4] = $warehouse; 
							$cols[5] = $qty;
							($cols[6],$cost_adj) = &load_sltvcost($skus->{'ID_sku_products'});
							
							if (open(AUTH, ">>$file")){
				    		print AUTH '"'.join('","', @cols)."\"\n";
				    		close AUTH;
							}
							
							$line_prn = 1;
						}
						if (!$line_prn){
							$cols[4] = '---';
							$cols[5] = 0;
							($cols[6],$cost_adj) = &load_sltvcost($skus->{'ID_sku_products'});
							
							if (open(AUTH, ">>$file")){
				    		print AUTH '"'.join('","', @cols)."\"\n";
				    		close AUTH;
							}
							
						}
						$line_prn = 0;
					}
				}else{
					$cols[0] = &format_sltvid(100000000+$rec->{'ID_products'});
					$cols[2] = '---';
					$cols[4] = '---';
					$cols[5] = 0;
					
					if (open(AUTH, ">>$file")){
				  	print AUTH '"'.join('","', @cols)."\"\n";
				   	close AUTH;
					}
					
				}
			}
			
			
			################################################
			################ PARTS
			################################################
			my ($sth) = &Do_SQL("SELECT * FROM sl_parts ORDER BY ID_parts;");
			while ($rec = $sth->fetchrow_hashref){	
				$cols[1] = $rec->{'Model'} . ' ' . $rec->{'Name'};
				$cols[1] =~ s/"//g; #"
				$cols[3] = $rec->{'Status'};
		
				my ($sth2) = &Do_SQL("SELECT COUNT(*) FROM sl_skus WHERE ID_products=$rec->{'ID_parts'} ORDER BY ID_skus;");
				$skus = $sth2->fetchrow;
				
				if($skus > 0){
					my ($sth2) = &Do_SQL("SELECT * FROM sl_skus WHERE ID_products=$rec->{'ID_parts'} ORDER BY ID_skus;");
					while ($skus = $sth2->fetchrow_hashref){
						$cols[0] = &format_sltvid($skus->{'ID_sku_products'});
			
						$cols[2] = "$skus->{'choice1'},$skus->{'choice2'},$skus->{'choice3'},$skus->{'choice4'}";
						$cols[2] =~ s/,,|,$|"|'//g; #";
						(!$cols[2]) and ($cols[2] = '---'); 
						my ($sth3) = &Do_SQL("SELECT ID_warehouses,sum(Quantity) FROM sl_warehouses_location WHERE ID_products=$skus->{'ID_sku_products'} GROUP BY ID_warehouses;");
						while (($warehouse,$qty) = $sth3->fetchrow_array()){
							$cols[4] = $warehouse; 
							$cols[5] = $qty;
							($cols[6],$cost_adj) = &load_sltvcost($skus->{'ID_sku_products'});
							
							if (open(AUTH, ">>$file")){
				    		print AUTH '"'.join('","', @cols)."\"\n";
				    		close AUTH;
							}
							
							$line_prn = 1;
						}
						if (!$line_prn){
							$cols[4] = '---';
							$cols[5] = 0;
							($cols[6],$cost_adj) = &load_sltvcost($skus->{'ID_sku_products'});
							
							if (open(AUTH, ">>$file")){
				    		print AUTH '"'.join('","', @cols)."\"\n";
				    		close AUTH;
							}
							
						}
						$line_prn = 0;
					}
				}else{
					$cols[0] = &format_sltvid(400000000+$rec->{'ID_parts'});
					$cols[2] = '---';
					$cols[4] = '---';
					$cols[5] = 0;
					
					if (open(AUTH, ">>$file")){
				  	print AUTH '"'.join('","', @cols)."\"\n";
				    close AUTH;
					}
					
				}	
			}
			
			print "Successfully written $fil;";
		}else{
				print "Impossible write $file";
		}
}



sub chg_perm_trackinventory{
#--------------------------------------
#--------------------------------------

	$home_dir =~ /(.+)cgi-bin\/common\/apps\/$/;
	my $dir = $1.'files/e1/*';

	`chmod 766 $dir`

}

sub emails_stats{
# --------------------------------------------------------
# Forms Involved: 
# Created on: 18 Feb 2011 13:01:16
# Author: MCC C. Gabriel Varela S.
# Description :   
# Parameters :
	#obtiene los datos de los correos
	my $sth=&Do_SQL("Select count(email) as total_emails
from (select trim(email)as email
			from innovausa.nsc_campaigns_email
			where email!='' 
			and not isnull(email)
			and email like '%@%'
			group by email
union select trim(email)as email
			from innovausa.nsc_email_inviters
			where email!='' 
			and not isnull(email)
			and email like '%@%'
			group by email
union select trim(email)as email
			from innovausa.nsc_email_invites
			where email!='' 
			and not isnull(email)
			and email like '%@%'
			group by email
union select trim(email)as email
			from innovausa.nsc_incomplete_orders
			where email!='' 
			and not isnull(email)
			and email like '%@%'
			group by email
union select trim(email)as email
			from innovausa.sl_customers
			where email!='' 
			and not isnull(email)
			and email like '%@%'
			group by email
union select trim(email)as email
			from gtsmiami.sl_customers
			where email!='' 
			and not isnull(email)
			and email like '%@%'
			group by email)as table1");
	my $rec=$sth->fetchrow_hashref;
	
	#Se insertan resultados.
	my $sth=&Do_SQL("insert into nsc_emails_stats set total_emails='$rec->{'total_emails'}',Date=curdate(),Time=curtime(),ID_admin_users=1");

}


sub coupon_cleaner{
# --------------------------------------------------------
# Created on: 05/19/2011 11:11:28 AM 
# Author: Roberto Barcenas
# Description : 
# Parameters : 
#  
	my $sth=&Do_SQL("SELECT COUNT(*) FROM sl_coupons_external WHERE STATUS = 'Expired';");
	my ($to_delete) = $sth->fetchrow();
	
	if($to_delete > 10){
	
	  &Do_SQL("DELETE FROM sl_coupons_external WHERE STATUS = 'Expired';");
	  &Do_SQL("INSERT INTO sl_vars SET VName='Coupon Cleaner', VValue='$to_delete', Definition_En='Expired coupons deleted by run_daily cron file';");
	
	}
	
}


sub cod_sales{
# --------------------------------------------------------
# Created on: 06/15/2011 12:28:50 PM  
# Author: Roberto Barcenas
# Description : Guarda los registros correspondientes a la tabla de ventas COD para ser extraidos por sales table de admin y fup
# Parameters : 
#

    &Do_SQL("TRUNCATE TABLE `sl_cod_sales`;");
    &cod_sales_execute(0);
    my $sth=&Do_SQL("SELECT ID_warehouses FROM sl_warehouses WHERE Type='Virtual' AND Status='Active' ORDER BY ID_warehouses;");
	while(my($id_warehouse) =  $sth->fetchrow()){
		&cod_sales_execute($id_warehouse);
	}
}


sub cod_sales_execute{
# --------------------------------------------------------
# Created on: 06/16/2011 15:33:56 PM  
# Author: Roberto Barcenas
# Description : Ejecuta el query que consulta cada warehouse virtual y guarda los datos resultantes en la tabla sl_cod_sales
# Parameters : $id_warehouses
#  

    my ($id_warehouses) = @_;

    ($id_warehouses) and ($innerWarehouse=' INNER JOIN sl_deliveryschs USE INDEX(Zip) ON sl_deliveryschs.Zip = sl_orders.shp_Zip ') and ($modWarehouse=" AND sl_deliveryschs.ID_warehouses = $id_warehouses ") and ($linkwarehouse = "&id_warehouses=$id_warehouses");

    my $sth=&Do_SQL("Select Status,
    Sum(if(KindOfContact='Never',1,0))as Never,
    Sum(if(KindOfContact='>7 days',1,0))as More_than_7_days,
    Sum(if(KindOfContact='7 days',1,0))as Seven_days,
    Sum(if(KindOfContact='2 days',1,0))as Two_days,
    Sum(if(KindOfContact='1 days',1,0))as One_day
  from(
    SELECT sl_orders.ID_orders,
    if(sl_orders.Status='Processed',if(not isnull(sl_orders_datecod.ID_orders),'Processed-In transit','Processed-To be fulfilled'),sl_orders.Status)as Status,
    count(ID_orders_notes)as NNotes,Max(concat(sl_orders_notes.Date,' ',sl_orders_notes.Time)) as LastTimeOfContact,
    if(isnull(Max(concat(sl_orders_notes.Date,' ',sl_orders_notes.Time))),'Never',
    if(datediff(Curdate(),Max(concat(sl_orders_notes.Date,' ',sl_orders_notes.Time)))>7,'>7 days',
    if(datediff(Curdate(),Max(concat(sl_orders_notes.Date,' ',sl_orders_notes.Time)))>2,'7 days',
    if(datediff(Curdate(),Max(concat(sl_orders_notes.Date,' ',sl_orders_notes.Time)))>1,'2 days',
    if(datediff(Curdate(),Max(concat(sl_orders_notes.Date,' ',sl_orders_notes.Time)))>=0,'1 days',0)
    )
    )
    )
    )as KindOfContact,
    datediff(Curdate(),Max(concat(sl_orders_notes.Date,' ',sl_orders_notes.Time)))as diff
    FROM sl_orders
    $innerWarehouse
    
    LEFT JOIN sl_orders_notes ON(sl_orders_notes.ID_orders = sl_orders.ID_orders)
    left join sl_orders_datecod on(sl_orders.ID_orders=sl_orders_datecod.ID_orders)
    WHERE sl_orders.shp_type=$cfg{'codshptype'} and Ptype='COD' $modWarehouse 
    GROUP BY sl_orders.ID_orders
  )as tmp
  GROUP BY Status");

    if($sth->rows() > 0){

      while($rec=$sth->fetchrow_hashref()){    
		    
		    &Do_SQL("INSERT INTO sl_cod_sales SET ID_warehouses='".$id_warehouses."', Status='$rec->{'Status'}', More='$rec->{'More_than_7_days'}',Seven='$rec->{'Seven_days'}',Two='$rec->{'Two_days'}',One='$rec->{'One_day'}',Never='$rec->{'Never'}';");
		    print "Warehouse: $id_warehouses\nMore than Seven:$rec->{'More_than_7_days'}\nSeven Days:$rec->{'Seven_days'}\nTwo Days:$rec->{'Two_days'}\nOne Day:$rec->{'One_day'}\nNever:$rec->{'Never'}\n\n";
		    
		  }
		  
    }else{
    
      print "Warehouse: $id_warehouses\nNo Data...\n\n";
    
    }

}


sub salenaturalivmembership{
# --------------------------------------------------------
# Created on: 07/06/2011 05:57:51 PM  
# Author: Roberto Barcenas
# Description : Genera los movimientos contables para las ventas de membresias naturaliv
# Parameters : 
#  

	$home_dir =~	/(.+)cgi-bin\/common\/apps\/$/;

	my $str_mail;

	my ($sth) = &Do_SQL("SELECT   
			    sl_orders.ID_orders,
			    sl_orders.Status,
			    sl_orders.Date,
			    SumPayments,
			    SumPaid
			  FROM `sl_orders`
			  INNER JOIN sl_orders_products
			  ON sl_orders.ID_orders = sl_orders_products.ID_orders
			  INNER JOIN
			  (
			    SELECT ID_orders,SUM(Amount)AS SumPayments,SUM(IF(Captured='Yes' OR (CapDate IS NOT NULL AND CapDate!='' AND CapDate!='0000-00-00'),Amount,0))AS SumPaid
			    FROM sl_orders_payments WHERE Status != 'Cancelled'
			    GROUP BY ID_orders
			  )AS tmppay
			  ON tmppay.ID_orders = sl_orders.ID_orders
			  WHERE ID_products = 600000000+$va{'naturaliv_membership'}
			  AND sl_orders_products.Status = 'Active'
			  AND sl_orders.Status NOT IN ('Void', 'Cancelled', 'System Error')
			  AND SumPayments > 0 AND SumPaid >0
			  AND 1 > (SELECT COUNT(*) FROM sl_movements WHERE ID_tableused = sl_orders.ID_orders AND ID_accounts=170 AND Credebit='Credit' )");
													
	LINE:while(my($idorders,$status,$date,$paymnets,$paid) = $sth->fetchrow()){
			
    #### Acounting Movements
		
		#ADG cambio la forma de llamar a la function
		#&accounting_sale($idorders);
		#### Acounting Movements
		my ($sth) = &Do_SQL("SELECT Ptype, Type FROM sl_orders INNER JOIN sl_customers USING(ID_customers) WHERE ID_orders = '$idorders';");
		($order_type, $ctype) = $sth->fetchrow();

		my @params = ($idorders);
		&accounting_keypoints('order_products_scanned_'. $ctype .'_'. $order_type, \@params );


		my ($sth) = &Do_SQL("UPDATE sl_orders SET Status='Shipped' WHERE ID_orders = '$idorders';");
		
		&add_order_notes_by_type($idorders,"'Naturaliv Membership Movements Created","Low");
  }

}



sub retail_to_wholesale_daily{
# --------------------------------------------------------
# Created on: 09/16/2011 16:28:51 PM
# Author: Roberto Barcenas
# Description : Manda llamar a la funcion retail_to_wholesale de sub.base_sltv
# Parameters :
#  
	print "Buscando ordenes retail para cambiar\n";
	&retail_to_wholesale;
	print "Saliendo retail to wholesale\n";
}




#########################################################################################
#########################################################################################
#   Function: earcalls_verify
#
#       Es: Se realiza la verificacion de insersion correcta de did y cid obtenidas por earcalls en las ventas de consola
#
#       En: Verification is performed correctly insersion did and cid obtained by earcalls console sales
#
#
#
#   Created on: 19/12/2012  10:59
#
#   Author: Alejandro Diaz
#
#   Modifications:
#
#      - Modified on 
#
#   Parameters:
#
#      --- 
#   
#
#   Returns:
#
#      --- 
#
#   See Also:
#
#      ---
#
sub earcalls_verify{

	print "Buscando ordenes retail para cambiar\n";
	&retail_to_wholesale;
	print "Saliendo retail to wholesale\n";
}

#########################################################################################
#########################################################################################
#   Function: autoassign_zones
#
#       Es: Realiza una busqueda de ordenes que no cuenten con una Zona asignada, para intentar asignarla de forma automatica.
#
#       En: Looking orders without zone, to try to automatically assign
#
#
#
#   Created on: 19/12/2012  10:59
#
#   Author: Alejandro Diaz
#
#   Modifications:
#
#      - Modified on 
#
#   Parameters:
#
#      --- 
#   
#   Returns:
#
#      --- 
#
#   See Also:
#
#      ---
#
sub autoassign_zones{

	print "Looking orders without zone, to try to automatically assign: \n";
	
	my $sth=&Do_SQL("SELECT ID_orders, shp_Zip FROM sl_orders WHERE ID_zones = 0");
	my ($registers) = 0;
    if($sth->rows() > 0) {

    	while($rec=$sth->fetchrow_hashref()) {
    		$id_orders = $rec->{'ID_orders'};
    		$zipcode = $rec->{'shp_Zip'};
    		
    		&Do_SQL("UPDATE sl_orders SET ID_zones = (SELECT ID_zones FROM sl_zones_zipcodes WHERE ZipCode = '$zipcode') WHERE ID_orders = $id_orders; ");

		    $registers++;
		}

		print "$registers orders found\n\n";
		  
    }else{

    	print "No data found...\n\n";
    
    }

	print "Search completed.\n";
}