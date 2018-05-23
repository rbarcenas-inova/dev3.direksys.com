##########################################################
##	ACCOUNTING
##  BDMAN fin_journalentries
##########################################################


#############################################################################
#############################################################################
#   Function: loaddefault_fin_journalentries
#
#       Es: datos iniciales
#       En: 
#
#    Created on: 
#
#    Author: CARLOS HAAS
#
#    Modifications:
#
#
#   Parameters:
#
#  Returns:
#
#   See Also:
#
#
sub loaddefault_fin_journalentries {
#############################################################################
#############################################################################

	$in{'status'} = 'New';
	$va{'journalentries_category'} = '[bc_category:categories@sl_movements]';

}


#############################################################################
#############################################################################
#   Function: loaddefault_fin_journalentries
#
#       Es: datos iniciales
#       En: 
#
#    Created on: 
#
#    Author: CARLOS HAAS
#
#    Modifications:
#
#
#   Parameters:
#
#  Returns:
#
#   See Also:
#
#
sub loading_fin_journalentries {
#############################################################################
#############################################################################

	$va{'journalentries_category'} = $in{'status'} eq 'New' ? '[bc_category:categories@sl_movements]' : qq|<input type="hidden" name="category" value="$in{'category'}">$in{'category'}|;

}


#############################################################################
#############################################################################
#   Function: validate_fin_journalentries
#
#       Es: validacion
#       En: 
#
#    Created on: 
#
#    Author: CARLOS HAAS
#
#    Modifications:
#
#
#   Parameters:
#
#  Returns:
#
#   See Also:
#
#
sub validate_fin_journalentries {
# --------------------------------------------------------
	if ($in{'add'}){
		$in{'status'} = 'New';
	}
	return 0;
}

#############################################################################
#############################################################################
#   Function: loaddefault_fin_journalentries
#
#       Es: validacion
#       En: 
#
#    Created on: 
#
#    Author: CARLOS HAAS
#
#    Modifications:
#		Modified by _RB_ on 2013-06-27: Se agrega validacion para agregar registros al Journal. Solamente se debe permitir el agregado en Status New
#
#
#   Parameters:
#
#  Returns:
#
#   See Also:
#
#
sub view_fin_journalentries {
# --------------------------------------------------------

	$in{'drop'} = int($in{'drop'});
	if (($in{'drop'}>0 or $in{'gdrop'} or $in{'dropcat'}) and !&check_permissions('fin_journalentries_dropentries','','')){
		$va{'tabmessage'} = "<p class='stdtxterr'>".&trans_txt('unauth_action')."</p>";
	}elsif($in{'drop'} > 0 ){

		#######
		####### Drop Lines
		#######	

		my ($sth) = &Do_SQL("UPDATE sl_movements SET ID_journalentries = 0 WHERE ID_journalentries = '$in{'id_journalentries'}' AND ID_movements = '$in{'drop'}';");
		$va{'tabmessage'} = "<p class='stdtxterr'>".&trans_txt('fin_journalentries_edrop')."</p>";
		&auth_logging('fin_journalentries_edrop',"$in{'id_journalentries'}");

	}elsif ($in{'gdrop'} =~ /(\d+),(.*)/ ){

		#######
		####### Drop Group
		#######

		my ($sth) = &Do_SQL("UPDATE sl_movements SET ID_journalentries = 0 WHERE ID_journalentries = '$in{'id_journalentries'}' AND ID_tableused=$1 AND tableused='$2';") if ($1>0 and $2);
		$va{'tabmessage'} = "<p class='stdtxterr'>".&trans_txt('fin_journalentries_edrop')."</p>";
		&auth_logging('fin_journalentries_edrop',"$in{'id_journalentries'}");

	}elsif($in{'dropcat'} and $in{'dropdate'}){

		#######
		####### Drop Group By Category + Effdate
		#######

		my ($sth) = &Do_SQL("UPDATE sl_movements SET ID_journalentries = 0 WHERE ID_journalentries = '$in{'id_journalentries'}' AND Category = '". &filter_values($in{'dropcat'}) ."' AND Effdate  = '". &filter_values($in{'dropdate'}) ."';");
		$va{'tabmessage'} = "<p class='stdtxterr'>".&trans_txt('fin_journalentries_edrop')." Category:$in{'dropcat'} Effective Date: $in{'dropdate'}</p>";
		&auth_logging('fin_journalentries_edrop',"$in{'id_journalentries'}");


	}elsif($in{'new'}) {

		#######
		####### Change to New
		#######

		if($in{'status'} =~ /Posted|In Process/ and !&check_permissions('fin_journalentries_unposted','','')){
			$va{'message'} = &trans_txt('fin_journalentries_blocked')."<br>".&trans_txt('unauth_action');
		}else{

			&Do_SQL("UPDATE sl_journalentries SET Status = 'New' WHERE ID_journalentries = '$in{'id_journalentries'}';");
			&auth_logging('fin_journalentries_new',"$in{'id_journalentries'}");
			$in{'status'} = 'New';
			$va{'message'} = &trans_txt('fin_journalentries_new');

		}

	}elsif($in{'void'}) {

		#######
		####### Change to Void
		#######

		if($in{'status'} =~ /Posted|In Process/){
			$va{'message'} = &trans_txt('fin_journalentries_blocked');
		}else{

			&Do_SQL("UPDATE sl_journalentries SET Status = 'Void' WHERE ID_journalentries = '$in{'id_journalentries'}';");
			&auth_logging('fin_journalentries_void',"$in{'id_journalentries'}");
			$in{'status'} = 'Void';
		}

	}elsif($in{'posted'} and &check_permissions('fin_journalentries_postentries','','')){

		#######
		####### Change to To Process
		#######

		if($in{'status'} =~ /Posted|In Process|Void/){
			$va{'message'} = &trans_txt('fin_journalentries_blocked');
		}else{

			&Do_SQL("START TRANSACTION");

			# Se calculan  totales en sl_journalentries
			$query = "SELECT 
				SUM(IF(sl_movements.Credebit='Credit',sl_movements.Amount,0)) AS Credit
				, SUM(IF(sl_movements.Credebit='Debit',sl_movements.Amount,0)) AS Debit
				, SUM(IF(sl_movements.Credebit='',sl_movements.Amount,0)) AS 'Error'
				, COUNT(*)movs
			FROM sl_movements
			INNER JOIN sl_journalentries ON sl_movements.ID_journalentries=sl_journalentries.ID_journalentries
			WHERE sl_movements.Status='Active' 
			AND sl_journalentries.ID_journalentries=$in{'id_journalentries'};";
			$sth = &Do_SQL($query);
			my $row = $sth->fetchrow_hashref();

			if ($row->{'movs'}==0){
				$va{'message'} = &trans_txt('fin_journalentries_no_records');
			}else{

				if ($row->{'Error'} > 0){

					&Do_SQL("ROLLBACK");
					$va{'message'} = &trans_txt('fin_journalentries_error');

				}elsif( abs($row->{'Credit'} - $row->{'Debit'}) <= 1 ){

					## Accountig Period Validation
					my ($numberperiods, $nullperiods) = &Do_SQL("SELECT 
											SUM(DISTINCT IF(sl_movements.ID_accounting_periods >=0,1,0))AS Periods
											, SUM(IF(sl_movements.ID_accounting_periods IS NULL,1,0))AS NullPeriods
										FROM 
											sl_movements	
										WHERE 
											1
											AND sl_movements.id_journalentries = ". $in{'id_journalentries'} ."
											AND status = 'Active';")->fetchrow();
					
					if($numberperiods > 1){

						## There is more than 1 period in the journal
						&Do_SQL("ROLLBACK");
						$va{'message'} = &trans_txt('fin_journalentries_accperiodsnotmatch');
						return;

					}elsif($nullperiods){

						## Null Period records
						&Do_SQL("ROLLBACK");
						$va{'message'} = &trans_txt('fin_journalentries_accperiodsnull') . ' ' . $nullperiods;
						return;

					}

					# Se actualiza Status
					&Do_SQL("UPDATE sl_journalentries SET Status = 'To Process', Debits_Amount='$row->{'Debit'}', Credits_Amount='$row->{'Credit'}' WHERE ID_journalentries = '$in{'id_journalentries'}';");
					
					my ($sth) = &Do_SQL("INSERT INTO sl_cron_scripts SET script='create_journal_e$in{'e'}', Server='s11', type='function', scheduledate=CURDATE(),scheduletime=CURTIME(),Status='Active'");
					$va{'message'} = &trans_txt('fin_journalentries_process_scheduled');
					&auth_logging('fin_journalentries_posted',"$in{'id_journalentries'}");
					$in{'status'} = 'To Process';

					&Do_SQL("COMMIT");
				}else{
					&Do_SQL("ROLLBACK");
					$va{'message'} = &trans_txt('fin_journalentries_error_diference').format_number(abs($row->{'Credit'} - $row->{'Debit'}), 2);
				}
			}
		}
		
	}elsif($in{'add_entries'} and &check_permissions('fin_journalentries_addentries','','')) {

		#######
		####### Add Entries
		#######

		if ($in{'fromdate'}){
			$query .= "AND EffDate >= '".$in{'fromdate'}."'";
		}
		if ($in{'todate'}){
			$query .= "AND EffDate <= '".$in{'todate'}."'";
		}
		if ($in{'category'}){
			$in{'category'} =~ s/\|/','/g;  
			$query .= "AND Category IN ('".$in{'category'}."')"; 
		}
		$in{'type_id'} = int($in{'type_id'});
		if ($in{'type'} and $in{'type_id'}>0){
			$query .= "AND ID_tableused = '$in{'type_id'}' AND tableused = '$in{'type'}'" ;
		}	
	
		if($query and $in{'status'} eq 'New') {

			my ($sth) = &Do_SQL("UPDATE sl_movements SET ID_journalentries = '$in{'id_journalentries'}' WHERE Status = 'Active' AND (ID_journalentries IS NULL OR ID_journalentries=0) $query");
			$va{'tabmessage'} = "<p class='stdtxterr'>".&trans_txt('fin_journalentries_ea')."</p>";
			&auth_logging('fin_journalentries_addentries',"$in{'id_journalentries'}");

		}else{
			$va{'message'} = &trans_txt('unauth_action');
		}

	}

	#######
	####### Error Messages
	#######
	if (($in{'posted'} and !&check_permissions('fin_journalentries_postentries','','')) or ($in{'add_entries'} and !&check_permissions('fin_journalentries_addentries','','')) ) {
		$va{'message'} = &trans_txt('unauth_action');
	}


	#######
	####### Links
	#######

	if($in{'status'} eq 'New'){

		$va{'action_status'} = qq|&nbsp; \| &nbsp;<img src="/sitimages/default/b_accounting.png" title="Post" style="cursor:pointer" onClick='if(confirm("Do you want to POST the file?")){ sendForm(1); }'>&nbsp;&nbsp;|;
		$va{'action_status'} .= qq|<img src="/sitimages/default/b_accountingx.png" title="Void" style="cursor:pointer" onClick='if(confirm("Do you want to VOID the Process?")){ sendForm(2); }'>&nbsp;&nbsp;|;

	}elsif($in{'status'} eq 'To Process'){

		$va{'action_status'} = qq|&nbsp; \| <a href="/cgi-bin/mod/$usr{'application'}/dbman?cmd=$in{'cmd'}&view=$in{'id_journalentries'}&new=1">New</a>&nbsp;&nbsp;|;

	}elsif($in{'status'} eq 'Posted' and &check_permissions('fin_journalentries_unposted','','')){

		$va{'action_status'} .= qq|&nbsp; \|&nbsp; <a href="/cgi-bin/mod/$usr{'application'}/dbman?cmd=$in{'cmd'}&view=$in{'id_journalentries'}&new=1" style="color:red;">Unposted</a>&nbsp;&nbsp;|;

	}

}

1;