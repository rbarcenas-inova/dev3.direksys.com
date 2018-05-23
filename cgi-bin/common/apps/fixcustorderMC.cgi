#!/usr/bin/perl -I.
#######################################################################
#######################################################################
#######################################################################
use DBI;
use DBIx::Connector;
use DBD::mysql;

local ($home_dir) = '/home/www/domains/dev.shoplatinotv_new.com/cgi-bin/common/apps/'; 


# Load the form information and set the config file and userid.
chdir ("$home_dir");


# Required Libraries
# --------------------------------------------------------
eval {
	require ("../subs/auth.cgi");
	require ("../subs/sub.base.html.cgi");
	require ("run_daily.cfg");
};
if ($@) { &cgierr ("Error loading required Libraries",300,$@); }

eval { &main; };
if ($@) { &cgierr("Fatal error,301,$@"); }

exit;

sub main {
# --------------------------------------------------------
	$|++;
	&connect_db;
	&fixcustorder;
	&disconnect_db;
#	exec("/etc/init.d/mysql restart");
}


##########################################################
##			Function			##
##########################################################
sub fixcustorder{
	
	my($id_orders,$id_customers_new,$add1,$add2,$add3,$id_customers_old,$customer_old);
	my $trows=0;$ok=0;$bug=0;$fix=0;
	my $start='';$stop='';$time=0;
	
	$sth = &Do_SQL("SELECT NOW()");
	$start = $sth->fetchrow();
	
	my $line;
	open (GVO, "<./bug_customers_only_ids.txt");
	while(<GVO>)
	{
		$line=$_;
		$line =~ s/\n|\r//g;
		
		$sth = &Do_SQL("SELECT ID_orders,ID_customers,TRIM(concat( if( isnull(Address1 ) , '', Address1 ) , ' ', if( isnull( Address2 ) , '', Address2 ) , ' ', if( isnull( Address3 ) , '', Address3 ) , ' ', Zip, ' ', state )),shp_name,
				TRIM(concat( if( isnull(shp_Address1) , '', shp_Address1 ) , ' ', if( isnull(shp_Address2) , '', shp_Address2 ) , ' ', if( isnull( shp_Address3 ) , '', shp_Address3 ) , ' ', shp_Zip, ' ', shp_state ))
				FROM sl_orders WHERE ID_orders = $line;");
		while(($id_orders,$id_customers_new,$addn,$shp_name,$shp_add) = $sth->fetchrow()){
			my $customer_new  = &load_name('sl_customers','ID_customers',$id_customers_new,"CONCAT(FirstName,' ',LastName1,' ',LastName2)");
			my $customer_new_add = &load_name('sl_customers','ID_customers',$id_customers_new,"TRIM(concat( if( isnull(Address1 ) , '', Address1 ) , ' ', if( isnull( Address2 ) , '', Address2 ) , ' ', if( isnull( Address3 ) , '', Address3 ) , ' ', Zip, ' ', state ))");
			
			my $maindata = "
	<Order>
	  <Main_Info>
	    <ID_Order>$id_orders</ID_Order>
	    <Address_Order>$addn</Address_Order>
	  </Main_Info>
	  <Shp_Info>
	    <Shp_Name>$shp_name</Shp_Name>
	    <Shp_Address>$shp_add</Shp_Address>
	  </Shp_Info>
	  <Customer_Info>
	    <ID_Customer>$id_customers_new</ID_customer>
	    <Customer_Name>$customer_new</Customer_Name>
	    <Customer_Address>$customer_new_add</Customer_Address>
	  </Customer_Info>";
						
			if($shp_add eq $customer_new_add){
				$file = "same_customers.xml";
				$flag=0;
				$ok++;
			}else{
				$sth2 = &Do_SQL("SELECT  ID_customers,CONCAT(FirstName,' ',LastName1,' ',LastName2) FROM sl_customers WHERE 
						TRIM(concat( if( isnull( Address1 ) , '', Address1 ) , ' ', if( isnull( Address2 ) , '', Address2 ) , ' ', if( isnull( Address3 ) , '', Address3 ) , ' ', Zip, ' ', state )) = '$shp_add';");
				($id_customers_old,$customer_old) = $sth2->fetchrow();
				if($sth2->rows() == 0){
					$file = "bug_customers.xml";
					$flag=0;
					$bug++;
					$maindata .= "
	  <Error>SELECT  ID_customers,CONCAT(FirstName,' ',LastName1,' ',LastName2) FROM sl_customers WHERE TRIM(concat( if( isnull( Address1 ) , '', Address1 ) , ' ', if( isnull( Address2 ) , '', Address2 ) , ' ', if( isnull( Address3 ) , '', Address3 ) , ' ', Zip, ' ', state )) = '$shp_add';</Error>";
				}else{
					$file = "wrong_customers.xml";
					$flag=1;
					$fix++;
					my $customer_old_add = &load_name('sl_customers','ID_customers',$id_customers_old,"concat( if( isnull(Address1 ) , '', Address1 ) , ' ', if( isnull( Address2 ) , '', Address2 ) , ' ', if( isnull( Address3 ) , '', Address3 ) , ' ', Zip, ' ', state )");
					$maindata .= "	
	  <Right_Info>
	    <Right_ID_Customer>$id_customers_old</Right_ID_customer>
	    <Right_Customer_Name>$customer_old</Right_Customer_Name>
	    <Right_Customer_Address>$customer_old_add</Right_Customer_Address>
	  </Right_Info>";
							
					$query = "UPDATE sl_orders SET ID_customers=$id_customers_old WHERE ID_orders = $id_orders ANDId_customers=$id_customers_new;\r\n" if $id_customers_old > 0;
				}
			}
			$maindata .="
	</Order>\r\n";
			open FILE, ">>../../../files/$file" or die $!; 
			print FILE $maindata; 
			close FILE;
			
			if($flag){
				open UPDATEF, ">>../../../files/update_orders_customers.sql" or die $!; 
				print UPDATEF $query; 
				close UPDATEF;
			}
			$trows++;
		}
	}
	close GVO;
	$sth = &Do_SQL("SELECT NOW(),TIMESTAMPDIFF(MINUTE,'$start',NOW());");
	($stop,$time) = $sth->fetchrow();
	$info = "
<Info>  
  <Start_Time>$start</Start_Time>  
  <Stop_Time>$stop</Stop_Time>  
  <Total_Minutes>$time</Total_Minutes>  
  <Total_Orders>$trows</Total_Orders>  
  <Total_Same>$ok</Total_Same>  
  <Total_Fixed>$fix</Total_Fixed>  
  <Total_Errors>$bug</Total_Erros>
 </Info>";
	open FILE, ">>../../../files/resume.xml" or die $!; 
	print FILE $info; 
	close FILE;
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

