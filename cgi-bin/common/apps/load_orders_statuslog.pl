#!/usr/bin/perl
#######################################################################
#######################################################################
#######################################################################
use DBI;
use DBIx::Connector;
use DBD::mysql;
use Cwd;
use File::Find;
use XML::Simple;
use Data::Dumper;

local ($dir) = getcwd;
$in{'e'} = 2;


chdir($dir);

# Required Libraries
# --------------------------------------------------------
eval {
	require ('../subs/auth.cgi');
	require ('../subs/sub.base.html.cgi');
	require ('../subs/sub.func.html.cgi');
};
if ($@) { &cgierr ("Error loading required Libraries",300,$@); }

eval { &main; };
if ($@) { &cgierr("Fatal error,301,$@"); }

exit;

#################################################################
#################################################################
#	Function: main
#
#   		Main function: Calls execution scripts. Script called from cron task
#
#	Created by: _Roberto Barcenas_
#
#
#	Modified By:
#
#
#   	Parameters:
#
#
#   	Returns:
#
#
#
#   	See Also:
#
sub main {
#################################################################
#################################################################

	$|++;
	# &connect_db;
	# &set_orders_status_log;
	# &disconnect_db;
	exit;

}


#############################################################################
#############################################################################
#       Function: set_orders_status_log
#
#       Es: Revisa carpeta cvns y si encuentra archivos los procesa y devuelve en la carpeta done/ con los valores de los cvns
#       En: 
#
#       Created on: 08/01/2014
#
#       Author: Roberto Barcenas
#
#       Modifications:
#
#       Parameters:
#
#
#       Returns:
#
#
#       See Also:
#
#       Todo:
#
sub set_orders_status_log{
#############################################################################
#############################################################################


    ######
    ###### 1) Table already populated ?
    ######
    #my ($sth) = &Do_SQL("SELECT COUNT(*) FROM sl_orders_statuslog;");
    #my ($t) = $sth->fetchrow();

    #####
    ##### 3) Table empty. Populate each Order
    #####
    my $this_query = "SELECT ID_orders,PType,PostedDate,Status,StatusPay,Date,Time,ID_admin_users FROM sl_orders WHERE 1 /*AND ID_orders = '9000987' /*AND Date >= DATE_SUB(CURDATE(), INTERVAL 5 DAY)*/ AND Status <> 'System Error' ORDER BY ID_orders /*LIMIT 0,1000*/;";
    my ($sth) = &Do_SQL($this_query);

    ORDERS:while(my ($id_orders, $ptype, $pd, $x, $y, $d, $t, $id_admin_users) = $sth->fetchrow()) {
  
    	my ($stx) = &Do_SQL("SELECT COUNT(*) FROM sl_orders_statuslog WHERE ID_orders = '$id_orders';");
    	my ($x1) = $stx->fetchrow();

    	if($x1){

            print "$id_orders - Skipped\n";
            next ORDERS;

        }

    	my $id;
        ####
        #### 3.1) Call Function By Order
        ####
        print "\n\n...\n\n\n";

        ####
        #### 3.1.1) Populating Inital State
        ####
        if($x =~ /New|Void|System Error/){

            ####
            #### 3.1.1.1) Updating Log Table
            ####
            my $q1 = "/*Inital 1*/ REPLACE INTO sl_orders_statuslog SET ID_orders = '$id_orders', $x = '$d $t', Date = '$d', Time = '$t', ID_admin_users = '$id_admin_users';";
            print "$q1\n";
            &Do_SQL($q1);
            next ORDERS;

        }else{

            if($ptype ne 'Credit-Card'){

                ######## Started as New?
                my $q2 = "/*Inital 2*/ REPLACE INTO sl_orders_statuslog SET ID_orders = '$id_orders', New = '$d $t', Date = '$d', Time = '$t', ID_admin_users = '$id_admin_users';";
                print "$q2\n";
                my ($sth) = &Do_SQL($q2);
            	$id = $sth->{'mysql_insertid'};
            
            }else{

                my ($sth1) = &Do_SQL("SELECT IF(
                                                        Notes='Order Processed' AND Type='High', 'Processed',
                                                     IF(
                                                            Notes LIKE 'La fecha de hoy es%' AND Type='Low', 'New', 0
                                                        )
                                                    ) AS InitialStatus
                                            FROM sl_orders_notes 
                                            WHERE ID_orders = '$id_orders' AND Date = '$d'
                                            AND (
                                                     (Notes='Order Processed' AND Type='High')
                                                     OR
                                                      (Notes LIKE 'La fecha de hoy es%' AND Type='Low')
                                                )
                                            ORDER BY TIME DESC LIMIT 1;");
                my ($x_ini) = $sth1->fetchrow();
                $x_ini = 'Void ' if !$x_ini;

                ######## Started as Processed|New|Void 9123163 9112784
                my $q3 = "/* Inital 3*/ REPLACE INTO sl_orders_statuslog SET ID_orders = '$id_orders', $x_ini = '$d $t', Date = '$d', Time = '$t', ID_admin_users = '$id_admin_users';";
                print "$q3\n";
                my ($sth) = &Do_SQL($q3);
                $id = $sth->{'mysql_insertid'};

            }


        }



        ####
        #### 3.1.1.2) Updating Log Table [Intermediate's Status]
        ####
        $in{'id_orders'} = $id_orders;
        &set_order_status_log();
        delete($in{'id_orders'}) if $in{'id_orders'};


        ######
        ###### 3.1.1.2.1) Any other intermediate Event?
        ######

         my ($sth1) = &Do_SQL("SELECT IF(
                                                Notes='Order Processed' AND Type='High', 'Processed',
                                             IF(
                                                    Notes LIKE 'La fecha de hoy es%' AND Type='Low', 'New', 0
                                                )
                                            ) AS MidStatus
										, Date, Time, ID_admin_users
                                    FROM sl_orders_notes 
                                    WHERE ID_orders = '$id_orders' AND Date > '$d'
                                    AND (
                                             (Notes='Order Processed' AND Type='High')
                                             OR
                                              (Notes LIKE 'La fecha de hoy es%' AND Type='Low')
                                        )
                                    ORDER BY TIME DESC LIMIT 1;");
        my ($xm, $xd, $xt, $id_admin_usersx) = $sth1->fetchrow();
		if($xm){

            my ($sth3) = &Do_SQL("SELECT IF( CONCAT(Date,' ',Time) < '$xd $xt',1,0) FROM sl_orders_statuslog WHERE ID_orders_statuslog = '$id';");
            my ($this_newer) = $sth3->fetchrow();

            if($this_newer){

            	my $q7 = "UPDATE sl_orders_statuslog SET $xm = '$xd $xt' WHERE ID_orders_statuslog = '$id';";
            	print "$q7\n";
            	&Do_SQL($q7) ;

            }

        }


        if($ptype eq 'COD'){

        	####### Processed -> In Transit
        	 my ($sthit) = &Do_SQL("SELECT 'InTransit', LogDate, LogTime, ID_admin_users 
        	 					FROM `admin_logs` WHERE 1
        	 					AND Action = '$id_orders'
	                        	AND Type = 'Application' 
	                        	AND tbl_name = 'sl_orders'
	                        	AND `Message` =  'cod_order_shipped'
	                        	ORDER BY Action, CONCAT(LogDate,' ',LogTime) DESC LIMIT 1;");
        	my ($a, $b, $c, $id_admin_userst) = $sthit->fetchrow();

        	if($a){

        		my $qi = "UPDATE sl_orders_statuslog SET $a = '$b $c' WHERE ID_orders_statuslog = '$id';";
            	print "$qi\n";
            	&Do_SQL($qi) ;

        	}

        }


        my ($xt, $dt, $tt, $id_admin_userst);
        my ($xt2, $dt2, $tt2, $id_admin_userst2);
        if($ptype ne 'COD') {
        
        	if($ptype ne 'Referenced Deposit') {

	            ####### PostDated -> Processed 
	            my ($sth2) = &Do_SQL("SELECT 'Processed', Date, Time, ID_admin_users
	                                        FROM sl_orders_notes 
	                                        WHERE ID_orders = '$id_orders'
	                                        AND Notes='Payment Captured by Direksys Cron'
	                                        ORDER BY CONCAT(Date,' ',Time) DESC LIMIT 1;");
	            ($xt, $dt, $tt, $id_admin_userst) = $sth2->fetchrow();

	        }else{

	            ####### Referenced Deposit -> Processed
	            my $qrd = "SELECT 'Processed', Date, Time, ID_admin_users
	                                        FROM sl_orders_notes 
	                                        WHERE ID_orders = '$id_orders'
	                                        AND Notes LIKE 'Order Has Been Captured%'
	                                        ORDER BY CONCAT(Date,' ',Time) DESC LIMIT 1;";
	            print "$qrd\n";                             
	            my ($sth2) = &Do_SQL($qrd);
	            ($xt, $dt, $tt, $id_admin_userst) = $sth2->fetchrow();

	        }

        }else{

            ####### Processed -> Cancelled [COD Not Delivered]
             my ($sth4) = &Do_SQL("SELECT 'Cancelled', Date, Time, ID_admin_users
                                        FROM sl_orders_notes 
                                        WHERE ID_orders = '$id_orders'
                                        AND Notes LIKE 'Order Cancelled%'
                                        AND Type = 'High'
                                        ORDER BY CONCAT(Date,' ',Time) DESC LIMIT 1;");
            ($xt, $dt, $tt, $id_admin_userst) = $sth4->fetchrow();

        }


        if($ptype eq 'COD') {

            ####### Cancelled -> Processed [COD Reactivated]
            my ($sth5) = &Do_SQL("SELECT 'Processed', Date, Time, ID_admin_users
                                        FROM sl_orders_notes 
                                        WHERE ID_orders = '$id_orders'
                                        AND Notes = 'COD Order Reactivated'
                                        AND Type = 'Medium'
                                        ORDER BY CONCAT(Date,' ',Time) DESC LIMIT 1;");
            ($xt2, $dt2, $tt2, $id_admin_userst2) = $sth5->fetchrow();
       
        }


        for(0..1){

            ######
            ###### Any Intermediate status was detected?
            ######
            ($_ == 1) and ($xt = $xt2) and ($dt = $dt2) and ($tt = $tt2) and ($id_admin_userst = $id_admin_userst2);

            if($xt){

            	my $qs = "/*Buscando Anterior*/ SELECT IF($xt IS NULL OR $xt < '$dt $tt',1,0) FROM sl_orders_statuslog WHERE ID_orders_statuslog = '$id';";
            	print "$qs\n";
                my ($sth3) = &Do_SQL($qs);
                my ($is_newer) = $sth3->fetchrow();

                if($is_newer){

                	my $q4 = "UPDATE sl_orders_statuslog SET $xt = '$dt $tt' WHERE ID_orders_statuslog = '$id';";
                	print "$q4\n";
                	&Do_SQL($q4) ;

                }

            }

        }




        ####
        #### 3.1.1.3) Updating Log Table [Final Status]
        ####
        if($x eq 'Shipped'){

            my $q5 = "UPDATE sl_orders_statuslog SET Shipped = '$pd $t' WHERE ID_orders_statuslog = '$id';";
            print "$q5\n";
            &Do_SQL($q5);

        }


        my ($sthf) = &Do_SQL("SELECT COUNT(*) FROM sl_orders_statuslog WHERE ID_orders = '$id_orders' AND Processed > '2013-01-01';");
        my ($f) = $sthf->fetchrow();

        if(!$f){

            &Do_SQL("UPDATE sl_orders_statuslog SET Processed = '$d $t' WHERE ID_orders_statuslog = '$id';");

        }


    }

    return;
}


#############################################################################
#############################################################################
#       Function: set_order_status_log
#
#       Es: Es llamada por funcion event_act_e2_set_orders_status_log y puede guardar el log de una sola orden en todos sus staus o bien revisa la ultima hora 
#       En: 
#
#       Created on: 15/01/2014
#
#       Author: Roberto Barcenas
#
#       Modifications:
#
#       Parameters:
#
#
#       Returns:
#
#
#       See Also:
#
#       Todo:
#
sub set_order_status_log{
#############################################################################
#############################################################################


    #####
    ##### 1) Extract Status
    #####
    my @ary_logmsg;
    my $log_string = 'opr_orders_st';
    my @ary_status = &load_enum_toarray('sl_orders','Status');
    #for(0..$#ary_status){
    #    push(@ary_logmsg, "opr_orders_st" . $ary_status[$_]);
    #}


    #####
    ##### 2) Fn was called by Order or By Time?
    #####
    my $mod_query = $in{'id_orders'} ?
                " AND Action = '". $in{'id_orders'} ."'" :
                " AND TIMESTAMPDIFF(MINUTE,CONCAT(LogDate,' ',LogTime),NOW()) BETWEEN 0 AND 1440";


    #####
    ##### 3) Looking up for last hour changes each status
    #####
    #STAT:for(0..$#ary_logmsg) {
    STAT:for(0..$#ary_status) {

        $this_log_status = $ary_status[$_];
        $this_log_status =~ s/\s//g;
        my $this_id = 0;
        my $this_query = "SELECT Action,Message,LogDate, LogTime, ID_admin_users FROM `admin_logs` WHERE 1
                        ". $mod_query ."
                        AND Type = 'Application' 
                        AND tbl_name = 'sl_orders'
                        AND `Message` =  '". $log_string . $this_log_status ."'
                        ORDER BY Action, CONCAT(LogDate,' ',LogTime) DESC;";
        my ($sth) = &Do_SQL($this_query);
        print "$this_query\n\n";

        ORDERS:while(my ($id_orders, $logst, $d, $t, $id_admin_users) = $sth->fetchrow()) {
        
            ####
            #### 3.1) Skip Same order
            ####
            next ORDERS if($this_id == $id_orders );

            ####
            #### 3.3) Updating Log Table
            ####
            #&Do_SQL("REPLACE INTO sl_orders_statuslog SET ID_orders = '$id_orders', Status = '$this_log_status', Date = '$d', Time = '$t', ID_admin_users = '$id_admin_users';");
            &Do_SQL("UPDATE sl_orders_statuslog SET $this_log_status = '$d $t' WHERE ID_orders = '$id_orders';");

            $this_id = $id_orders; ### Flag to skip same order when called by Time

            ####
            #### 3.3) Next Order (Only triggered when call to populate first time for each order)
            ####
            next STAT if $in{'id_orders'};

        }

    }
    
    delete($in{'id_orders'}) if $in{'id_orders'};    
    return;

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
