#!/usr/bin/perl


##################################################################
#      CUSTOM PAGES       	#
##################################################################
sub custom_page {
# --------------------------------------------------------
# Created :  Carlos Haas 01/01/2007 6:47:28 PM
# Last Update : 
# Locked by : 
# Description :
#
#
	my ($fname) = $cfg{'path_templates'};
	$fname =~ s/\[lang\]/$usr{'pref_language'}/gi;
	if ($vkey{'custom_name'}){
		if (-e "$fname/custpages/$vkey{'custom_name'}/$in{'page'}.html"){
			print "Content-type: text/html\n\n";
			print &build_page("/custpages/$vkey{'custom_name'}/$in{'page'}.html");	
			return;	
		}
	}
	&html_base_home;
}


#############################################################################
#############################################################################
#       Function: build_dashboard
#
#       Es: Home dinamico de modulo Accounting
#       En: Dynamic home for Accounting module
#
#       Created on: 01/05/2016 12:00:00
#
#       Author: Fabián Cañaveral
#
#       Modifications: Alejandro Diaz
#
#       Parameters:
#
#       Returns:
#
#`
#       See Also: Accounting Periods
#
#       Todo:
#
sub build_dashboard{
#############################################################################
#############################################################################
	my ($ini, $fin, $add_sql);
	if ($in{'id_accounting_periods'}){
		$in{'id_accounting_periods'} = int($in{'id_accounting_periods'});

		my $sth = &Do_SQL("SELECT From_Date, To_Date FROM sl_accounting_periods WHERE sl_accounting_periods.ID_accounting_periods=".$in{'id_accounting_periods'}.";");
		($ini, $fin) = $sth->fetchrow_array();
		$add_sql = " AND Date >= '".$ini."' AND Date <= '".$fin."'";
	}

	if (!$ini and !$fin){
		&Do_SQL("SET \@fecha = curdate() ");
		$ini = &Do_SQL("SELECT concat(YEAR(\@fecha), '-', MONTH(\@fecha), '-01');")->fetchrow();
		$fin = &Do_SQL("SELECT DATE_ADD('$ini', INTERVAL 1 MONTH);")->fetchrow();
		$add_sql = " AND Date >= '".$ini."' AND Date < '".$fin."'";
	}

	my $query = "SELECT count(*)n, Category, sum(amount) from sl_movements WHERE 1 $add_sql AND status = 'active' GROUP BY Category;";

	my $rs = &Do_SQL($query);
	$va{'datos'} = "[['Category', 'Movements'],";
	while (my $row = $rs->fetchrow_hashref() ) {
		$va{'datos'} .= "[ '".$row->{'Category'}."', ".$row->{'n'}." ],";
	}
	$va{'datos'} .= "];";


	$query = "SELECT COUNT(*)t, IF(ID_journalentries IS NULL, 'No' , 'Si')n FROM sl_movements WHERE 1 $add_sql AND status = 'active' GROUP BY n;";

	$rs = &Do_SQL($query);
	$va{'datos2'} = "[['Total', 'Estatus'],";
	while (my $row = $rs->fetchrow_hashref() ) {
		$va{'datos2'} .= "[ '".$row->{'n'}."', ".$row->{'t'}." ],";
	}
	$va{'datos2'} .= "];";


	$query = "SELECT COUNT(*) n ,Status FROM sl_journalentries WHERE 1 $add_sql GROUP BY Status ";

	$rs = &Do_SQL($query);
	$va{'datos3'} = "[['Total', 'Estatus'],";
	while (my $row = $rs->fetchrow_hashref() ) {
		$va{'datos3'} .= "[ '".$row->{'Status'}."', ".$row->{'n'}." ],";
	}
	$va{'datos3'} .= "];";


	$query = "SELECT COUNT(*) n ,Status FROM sl_journalentries WHERE 1 $add_sql GROUP BY Status ";

	$rs = &Do_SQL($query);
	$va{'datos3'} = "[['Total', 'Estatus'],";
	while (my $row = $rs->fetchrow_hashref() ) {
		$va{'datos3'} .= "[ '".$row->{'Status'}."', ".$row->{'n'}." ],";
	}
	$va{'datos3'} .= "];";


	$query = "SELECT COUNT(*) n ,Status FROM cu_invoices WHERE 1 $add_sql GROUP BY Status ";

	$rs = &Do_SQL($query);
	$va{'datos0'} = "[['Total', 'Estatus'],";
	while (my $row = $rs->fetchrow_hashref() ) {
		$va{'datos0'} .= "[ '".$row->{'Status'}."', ".$row->{'n'}." ],";
	}
	$va{'datos0'} .= "];";


	if ($in{'e'}==2){

		$value = &Do_SQL("SELECT IF(sl_vars.VValue = 1, 'userActive.png', 'userInactive.png')name FROM sl_vars where sl_vars.VName = 'billingstat'")->fetchrow();

		$va{'status_facturacion'} = "<div class=\"status\"><img src='/sitimages/".$value."'/>&nbsp;Sitio Facturaci&oacute;n</div>";
	}


	my $sth = &Do_SQL("SELECT Date_exchange_rate, exchange_rate, Currency FROM sl_exchangerates WHERE DATE=CURDATE() AND Currency='US\$';");
	my ($date_exchange_rate, $exchange_rate, $currency) = $sth->fetchrow_array();
	if ($exchange_rate){
		$va{'date_exchange_rate'} = $date_exchange_rate;
		$va{'exchange_rate'} = $exchange_rate;
		$va{'currency'} = $currency;
	}

	return;
}

sub accounts{
	my $query = "SELECT sl_accounts.ID_accounts, sl_accounts.ID_accounting, sl_accounts.Name, sl_accounts.Status, sl_accategories.Name cat 
	FROM sl_accounts 
	LEFT JOIN sl_accategories USING(ID_accategories)
	WHERE id_parent = 0
	ORDER BY sl_accounts.ID_accounts asc";
	my $rs = &Do_SQL($query);
	$va{'datos'} = "[['Category', 'Movements'],";
	while (my $row = $rs->fetchrow_hashref() ) {
		$va{'datos'} .= "[ '".$row->{'Category'}."', ".$row->{'n'}." ],";
	}
	$va{'datos'} .= "];";


	$query = "SELECT COUNT(*)t, if(ID_journalentries is null, 'No' , 'Si')n FROM sl_movements WHERE 1 $add_sql and status = 'active' group by n;";

	$rs = &Do_SQL($query);
	$va{'datos2'} = "[['Total', 'Estatus'],";
	while (my $row = $rs->fetchrow_hashref() ) {
		$va{'datos2'} .= "[ '".$row->{'n'}."', ".$row->{'t'}." ],";
	}
	$va{'datos2'} .= "];";


	$query = "SELECT COUNT(*) n ,Status FROM sl_journalentries WHERE 1 $add_sql group by Status ";

	$rs = &Do_SQL($query);
	$va{'datos3'} = "[['Total', 'Estatus'],";
	while (my $row = $rs->fetchrow_hashref() ) {
		$va{'datos3'} .= "[ '".$row->{'Status'}."', ".$row->{'n'}." ],";
	}
	$va{'datos3'} .= "];";


	$query = "SELECT COUNT(*) n ,Status FROM sl_journalentries WHERE 1 $add_sql group by Status ";

	$rs = &Do_SQL($query);
	$va{'datos3'} = "[['Total', 'Estatus'],";
	while (my $row = $rs->fetchrow_hashref() ) {
		$va{'datos3'} .= "[ '".$row->{'Status'}."', ".$row->{'n'}." ],";
	}
	$va{'datos3'} .= "];";


	$query = "SELECT COUNT(*) n ,Status FROM cu_invoices WHERE 1 $add_sql group by Status ";

	$rs = &Do_SQL($query);
	$va{'datos0'} = "[['Total', 'Estatus'],";
	while (my $row = $rs->fetchrow_hashref() ) {
		$va{'datos0'} .= "[ '".$row->{'Status'}."', ".$row->{'n'}." ],";
	}
	$va{'datos0'} .= "];";


	$value = &Do_SQL("select IF(sl_vars.VValue = 1, 'userActive.png', 'userInactive.png')name from sl_vars where sl_vars.VName = 'billingstat'")->fetchrow();

	$va{'icon_status'} = '<img src="/sitimages/'.$value.'" />';

	my $sth = &Do_SQL("SELECT Date_exchange_rate, exchange_rate, Currency FROM sl_exchangerates WHERE DATE=CURDATE() AND Currency='US\$';");
	my ($date_exchange_rate, $exchange_rate, $currency) = $sth->fetchrow_array();
	if ($exchange_rate){
		$va{'date_exchange_rate'} = $date_exchange_rate;
		$va{'exchange_rate'} = $exchange_rate;
		$va{'currency'} = $currency;
	}
	
	return;
}

############################################################################################
############################################################################################
#	Function: trial_balance
#   	Genera balanza de comprobacion
#
#	Created by:
#		01-06-2016 Fabian Cañaveral
#
#	Modified By: ISC Alejandro Diaz
#
#   	Parameters:
#
#   	Returns:
#
#   	See Also:
#
#
sub trial_balance{
############################################################################################
############################################################################################

	# Obtenemos informacion de la empresa
	&get_company_info();
	$in{'id_accounting_periods'} = int($in{'id_accounting_periods'});

	$va{'expanditem'} = 1;
	$va{'display_filter_form'} = 'display:block;';
	$va{'display_trial_balance'} = 'display:none;';

	## Trabajamos el filtro de periodo
	$query ="SELECT sl_accounting_periods.From_Date, sl_accounting_periods.To_Date FROM sl_accounting_periods WHERE sl_accounting_periods.ID_accounting_periods=$in{'id_accounting_periods'};";
	my $sth = &Do_SQL($query);
	my $row_filters = $sth->fetchrow_hashref();

	$va{'from_date'} = $row_filters->{'From_Date'};
	$va{'to_date'} = $row_filters->{'To_Date'};

	if ($in{'action'}){
		$err = 0;
		if (!$in{'id_accounting_periods'}){
			$error{'id_accounting_periods'} = &trans_txt('required');
			$err++;
		}

		if (!$err){

			$va{'display_filter_form'} = 'display:none;';
			$va{'display_trial_balance'} = 'display:block;';

			$va{'csv'} .= qq|$va{'company_name'}\n|;
			$va{'csv'} .= qq|Balanza de Comprobacion del $va{'from_date'} al $va{'to_date'}\n\n|;
			
			$va{'csv'} .= qq|"Cuenta","Nombre","Saldos Iniciales","Cargos","Abonos","Saldos Finales"\n|;
			
			$add_sql_accounts = ($in{'level'} and $in{'level'} ne '')?" AND sl_accounts.level = ".$in{'level'}:"";

			my $query = "SELECT
				sl_accounts.ID_accounts
				, sl_accounts.Name
				, sl_accounts.ID_accounting
				, LOWER(sl_accounts_nature.Name)Nature
				, sl_accounts.level
				, sl_accounts.isdetailaccount
				, sl_accounting_periods_balance.sinicial
				, sl_accounting_periods_balance.credit
				, sl_accounting_periods_balance.debit
				, sl_accounting_periods_balance.sfinal
			FROM sl_accounts
			LEFT JOIN sl_accounts_nature ON sl_accounts.ID_account_nature=sl_accounts_nature.ID_accounts_nature
			LEFT JOIN sl_accounting_periods_balance ON sl_accounting_periods_balance.ID_accounts=sl_accounts.ID_accounts AND sl_accounting_periods_balance.ID_accounting_periods=".$in{'id_accounting_periods'}."
			WHERE sl_accounts.Status in ('Active', 'Inactive')
			$add_sql_accounts
			ORDER BY sl_accounts.ID_accounting, sl_accounts.Name ASC";
			my $res = &Do_SQL($query);
			$va{'table_body'} = '<tbody>';

			# Esto se aplica para que funcione correctamente la funcion format_price()
			my $tab_char = ($in{'type'} eq 'csv')? "    ":"&nbsp;&nbsp;&nbsp;&nbsp;";
			# Variables para Sumas Iguales
			my $total_saldos_iniciales_deudor=0;
			my $total_saldos_iniciales_acreedor=0;
			my $total_movimientos_deudor=0;
			my $total_movimientos_acreedor=0;
			my $total_saldos_actuales_deudor=0;
			my $total_saldos_actuales_acreedor=0;


			while (my $row = $res->fetchrow_hashref() ) {
				## Si se solicita una Balanza Agrupada
				my $limit_id_accounts = '';
				if ($in{'level'} == 2){

					## Obtenemos el ID siguiente para utilizarlo como limitante
					$query = "SELECT ID_accounting
					FROM sl_accounts
					WHERE sl_accounts.Status = 'Active'
					$add_sql_accounts
					AND sl_accounts.ID_accounting > ".$row->{'ID_accounting'}." LIMIT 1;";
					$res_next = &Do_SQL($query);
					my $limit_id_accounting = $res_next->fetchrow_array();

					my $add_sql_accounts2 = ($limit_id_accounting)? " AND sl_accounts.ID_accounting < ".$limit_id_accounting:"";

					## Obtengo las cuentas que se van a filtrar
					$query = "SELECT GROUP_CONCAT(ID_accounts)ID_accounts
					FROM sl_accounts
					WHERE sl_accounts.Status = 'Active'
					AND sl_accounts.isdetailaccount='Yes'
					AND sl_accounts.ID_accounting > ".$row->{'ID_accounting'}."
					$add_sql_accounts2 ;";
					$res_next = &Do_SQL($query);
					$limit_id_accounts = $res_next->fetchrow_array();
				}

				my $class_highlights = ($row->{'level'} == 1)? ' class="highlights"':'';

				$add_sql = ($limit_id_accounts and $limit_id_accounts ne '')?" AND sl_movements.ID_accounts IN (".$limit_id_accounts.")":" AND sl_movements.ID_accounts = ".$row->{'ID_accounts'}." GROUP BY sl_movements.ID_accounts";
				# ##
				$saldoInicial = &format_price($row->{'sinicial'});
				$saldoFinal = &format_price($row->{'sfinal'});


				my $level_tab = $tab_char x (int($row->{'level'})-1);

				## Validacion en base a filtros
				my $display = 1;
				if ($in{'cuentas_choice'}==5){
					if ($row->{'debit'} != 0 or $row->{'credit'} != 0 or $row->{'sinicial'} != 0 or $row->{'sfinal'} != 0){
						$display = 1;
					}else{
						$display = 0;
					}
				}

				if ($display){

					my ($export_detail) = ($row->{'isdetailaccount'} eq 'Yes' )? qq|<a href="?cmd=rep_accounting_auxiliary&action=1&export=1&effdate_from=$va{'from_date'}&effdate_to=$va{'to_date'}&id_journalentries=&id_accounts=$row->{'ID_accounts'}&posted=Posted"><img border="0" src="[va_imgurl]/[ur_pref_style]/b_xls.gif" width="12" height="12" title="Export Detail" alt="Export Detail"></a>|:"";
					
					$va{'table_body'} .= '<tr>';
					$va{'table_body'} .= '<td nowrap '.$class_highlights.' align="right">'.&format_account($row->{'ID_accounting'}).'</td>';
					$va{'table_body'} .= '<td nowrap '.$class_highlights.'>'.$level_tab.$row->{'Name'}.'</td>';
					$va{'table_body'} .= '<td nowrap '.$class_highlights.' align="right">'.$saldoInicial.'</td>';
					$va{'table_body'} .= '<td nowrap '.$class_highlights.' align="right">'.&format_price($row->{'debit'}).'</td>';
					$va{'table_body'} .= '<td nowrap '.$class_highlights.' align="right">'.&format_price($row->{'credit'}).'</td>';
					$va{'table_body'} .= '<td nowrap '.$class_highlights.' align="right">'.$saldoFinal.'</td>';
					$va{'table_body'} .= '<td nowrap '.$class_highlights.' align="center">'.$export_detail.'</td>';
					$va{'table_body'} .= '</tr>';

					## CSV generator
					$va{'csv'} .= qq|"|.&format_account($row->{'ID_accounting'}).qq|","$level_tab$row->{'Name'}","$saldoInicial","|.&format_price($row->{'debit'}).qq|","|.&format_price($row->{'credit'}).qq|","$saldoFinal"\n|;
				}

			}

			$query = qq|SELECT
				sum(sinicial) sinicial
				, sum(credit) haber
				, sum(debit) debe
				, sum(sfinal) sfinal
			FROM sl_accounting_periods_balance
			INNER JOIN sl_accounts on sl_accounting_periods_balance.ID_accounts = sl_accounts.ID_accounts
			WHERE 1
				AND ID_accounting_periods = $in{'id_accounting_periods'}
				AND sl_accounts.`level` = 1|;
			$saldosTotales = &Do_SQL($query)->fetchrow_hashref();


			## Sumas Iguales
			$va{'table_body'} .= '<tr>';
			$va{'table_body'} .= '<td nowrap '.$class_highlights.' align="right" colspan="7">&nbsp;</td>';
			$va{'table_body'} .= '</tr>';

			$va{'table_body'} .= '<tr>';
			$va{'table_body'} .= '<td nowrap '.$class_highlights.' align="right">&nbsp;</td>';
			$va{'table_body'} .= '<td nowrap '.$class_highlights.'>SUMAS IGUALES</td>';
			$va{'table_body'} .= '<td nowrap '.$class_highlights.' align="right">'.&format_price($saldosTotales->{'sinicial'}).'</td>';
			$va{'table_body'} .= '<td nowrap '.$class_highlights.' align="right">'.&format_price($saldosTotales->{'debe'}).'</td>';
			$va{'table_body'} .= '<td nowrap '.$class_highlights.' align="right">'.&format_price($saldosTotales->{'haber'}).'</td>';
			$va{'table_body'} .= '<td nowrap '.$class_highlights.' align="right">'.&format_price($saldosTotales->{'sfinal'}).'</td>';
			$va{'table_body'} .= '<td></td>';
			$va{'table_body'} .= '</tr>';

			$va{'table_body'} .= '</tbody>';
			
			if($in{'type'} eq 'csv'){
				## Sumas Iguales
				$va{'csv'} .= qq|"",\n|;
				$va{'csv'} .= qq|"","SUMAS IGUALES","|.&format_price($saldosTotales->{'sinicial'}).qq|","|.&format_price($saldosTotales->{'debe'}).qq|","|.&format_price($saldosTotales->{'haber'}).qq|","|.&format_price($saldosTotales->{'sfinal'}).qq|",\n|;
				
				## Pie de reporte
				$va{'csv'} .= &report_footer();

				my $f = lc($cfg{"app_title"}."-balanza de comprobacion del $va{'from_date'} al $va{'to_date'}");
				
				$f =~ s/ /_/g;
				print "Content-Disposition: attachment; filename=$f.csv;";
				print "Content-type: text/csv\n\n";
				print $va{'csv'};
				return;
			}
		}
	}
	
	print "Content-type: text/html\n\n";
	print &build_page("trial_balance.html");	

}

sub fix_accounts{

	$query = "select 
		id_accounts, 
		ID_accounting,
		SUBSTR(CAST(ID_accounting AS CHAR(8)),2,2) aa,
		CONCAT(SUBSTR(CAST(ID_accounting AS CHAR(8)),1,1),'0000000') bb,
		SUBSTR(CAST(ID_accounting AS CHAR(8)),1,3) a, 
		SUBSTR(CAST(ID_accounting AS CHAR(8)),4,2) b, 
		SUBSTR(CAST(ID_accounting AS CHAR(8)),6,3) c 
	from sl_accounts where status = 'Active' ";
	my $rs = &Do_SQL($query);
	print "Content-type: text/html\n\n";
	use Data::Dumper;
	while(my $row = $rs->fetchrow_hashref()){
		if($row->{'aa'} eq '00' and $row->{'b'} eq '00' and $row->{'c'} eq '000'){
			&Do_SQL("update sl_accounts set ID_parent = 0, level=1 where ID_accounts = $row->{'id_accounts'} and status = 'Active'");
			print "CUENTA: $row->{'ID_accounting'} PARENT: 0 <br>";
		}elsif($row->{'b'} eq '00' and $row->{'c'} eq '000'){
			$parent = $row->{'bb'};
			$id_parent = &Do_SQL("select ID_accounts from sl_accounts where ID_accounting = $parent and status = 'Active' limit 1")->fetchrow();
			if($id_parent eq ''){
				$id_parent = 0;
			}
			&Do_SQL("update sl_accounts set ID_parent = $id_parent, level=2 where ID_accounts = $row->{'id_accounts'} and status = 'Active'");
			print "CUENTA: $row->{'ID_accounting'} PARENT: $parent <br>";
		}elsif($row->{'c'} eq '000'){
			$parent = $row->{'a'}.'00000';
			$id_parent = &Do_SQL("select ID_accounts from sl_accounts where 
				ID_accounting = $parent and status='Active' limit 1")->fetchrow();
			if($id_parent eq ''){
				$id_parent = 0;
			}
			&Do_SQL("update sl_accounts set ID_parent = $id_parent, level=3 where ID_accounts = $row->{'id_accounts'} and status = 'Active'");
			print "CUENTA: $row->{'ID_accounting'} PARENT: $parent <br>";
		}elsif($row->{'c'} ne '000'){
			$parent = "$row->{'a'}$row->{'b'}000";
			$id_parent = &Do_SQL("select ID_accounts from sl_accounts where ID_accounting = $parent and status = 'Active' limit 1")->fetchrow();
			if($id_parent eq ''){
				$id_parent = 0;
			}
			&Do_SQL("update sl_accounts set ID_parent = $id_parent, level=4 where ID_accounts = $row->{'id_accounts'} and status = 'Active'");
			print "CUENTA: $row->{'ID_accounting'} PARENT: $parent <br>";
		}


	}
	print 'LISTO';
}

sub end_exercise{
	use Data::Dumper;
	use Try::Tiny;

	if($in{'action'} eq "add"){
		my ($rs, $query, $err, $credit, $debit, $amount, $credebit, $id_movement) = undef;
		my ($periodo_name14, $date_movements) = &Do_SQL(qq|SELECT Short_Name, From_Date FROM sl_accounting_periods WHERE id_accounting_periods = $in{'id_accounting_periods14'}|)->fetchrow();
		## Buscamos si el periodo tiene un Journal Entries de cierre previo en caso de no creamos uno.
		my $id_journalentries = &Do_SQL(qq|
		select sl_journalentries.ID_journalentries 
		from sl_movements
		inner join sl_journalentries on sl_movements.ID_journalentries = sl_journalentries.ID_journalentries
		where 1
			AND sl_movements.ID_accounting_periods = '$in{'id_accounting_periods14'}'
			AND sl_journalentries.Status = 'Posted'
		LIMIT 1|)->fetchrow();
		

		&Do_SQL('START TRANSACTION');

		if($id_journalentries){
			### Actualizamos el Journal del Cierre a estatus New, para eliminar los resultados de la balanza, para proceder a actualizar los movimientos del mismo, Tambien borramos los movimientos existentes de este Periodo, para generar los actulizados.
			try {
        		&Do_SQL(qq|DELETE FROM sl_movements WHERE id_journalentries = $id_journalentries|);
        		$query = qq|update sl_accounting_periods set Status = 'Open' where id_accounting_periods = $in{'id_accounting_periods14'}|;
				&Do_SQL($query);
        		&Do_SQL(qq|UPDATE sl_journalentries SET status = 'New' WHERE id_journalentries = $id_journalentries|);
			} catch {
				&Do_SQL('ROLLBACK');
				$err = 1; 
			};
			
		}else{
			$query = qq|update sl_accounting_periods set Status = 'Open' where id_accounting_periods = $in{'id_accounting_periods14'}|;
			&Do_SQL($query);
			$rs = &Do_SQL(qq|INSERT INTO sl_journalentries(JournalDate, Categories, comments, Debits_Amount, Credits_Amount, Status, `Date`, `Time`, ID_admin_users)
				VALUES
				(CURDATE(), 'Diario', 'Poliza de Cierre Periodo $periodo_name14', 0.00, 0.00, 'Posted', CURDATE(), CURTIME(), $usr{'id_admin_users'});|);
			$id_journalentries = $rs->{'mysql_insertid'};
		}



		## Creamos Movimientos de Diario Nuevos, los movimientos son creados invirtiendo el movimiento segun los resultados del periodo 13.

		$query = qq|
		insert into sl_movements(ID_accounts, Amount, EffDate, tableused, ID_tableused, tablerelated, ID_tablerelated, Category, Credebit, ID_segments, ID_journalentries, ID_accounting_periods, MD5Verification, Status, Date, Time, ID_admin_users)
		select
			sl_accounts.ID_accounts ID_accounts
			, ABS(sfinal) Amount
			, '$date_movements' EffDate
			, 'Unknown' tableused
			, 0 ID_tableused
			, '' tablerelated
			, 0 ID_tablerelated
			, 'Diario' Category
			, IF(sfinal > 0, 'Credit', 'Debit') Credebit
			, 0 ID_segments
			, $id_journalentries ID_journalentries
			, $in{'id_accounting_periods14'} ID_accounting_periods
			, null MD5Verification
			, 'Active' Status
			, CURDATE() Date
			, CURTIME() Time
			, '$usr{'id_admin_users'}' ID_admin_users
		from
			sl_accounting_periods_balance
		inner join sl_accounts on sl_accounting_periods_balance.ID_accounts = sl_accounts.ID_accounts
		inner join sl_accounts_nature on sl_accounts.ID_account_nature = sl_accounts_nature.ID_accounts_nature and sl_accounts_nature.ID_parent = 4
		where 1
			AND ID_accounting_periods = $in{'id_accounting_periods13'}
			AND sl_accounts.level = 4
			AND sfinal!= 0
		|;
		&Do_SQL($query);
		## Ponemos periodo requerido y Agregamos Comentarios a los movimientos.
		$query = qq|select * from sl_movements where ID_journalentries = $id_journalentries|;
		
		$rs = &Do_SQL($query);
		$debit = 0;
		$credit = 0;
		$query = qq|INSERT INTO sl_movements_auxiliary(ID_movements, FieldName, FieldValue) VALUES |;
		while (my $row = $rs->fetchrow_hashref()){
			$debit += $row->{'Credebit'} eq 'Debit' ? $row->{'Amount'} : 0;
			$credit += $row->{'Credebit'} eq 'Credit' ? $row->{'Amount'} : 0;
			$query .= qq|($row->{'ID_movements'}, 'Description', 'Movimiento de Cierre de Periodo $periodo_name14'),|;
			### Actualizamos el periodo Contable
			#&Do_SQL(qq|update sl_movements_auxiliary set FieldValue = $in{'id_accounting_periods14'} where ID_movements = '$row->{'ID_movements'}' and FieldName = 'ID_accounting_periods'|);
		}
		chop $query;
		&Do_SQL($query);


		# $query = qq|select sum(credit - debit) Resultado from sl_accounting_periods_balance where ID_accounting_periods =$in{'id_accounting_periods14'};|;
		$amount = $debit - $credit; #&Do_SQL($query)->fetchrow();
		$credebit = $amount > 0 ? 'Debit' : 'Credit';
		$query = qq|insert into sl_movements(ID_accounts, Amount, EffDate, tableused, ID_tableused, tablerelated, ID_tablerelated, Category, Credebit, ID_segments, ID_journalentries, ID_accounting_periods, MD5Verification, Status, Date, Time, ID_admin_users) VALUES 
		($in{'id_accounts'}, ABS($amount) , '$date_movements', 'Unknown', 0, '', 0, 'Diario', IF($amount > 0, 'Credit', 'Debit'), 0, $id_journalentries, '$in{'id_accounting_periods14'}', null, 'Active', CURDATE(), CURTIME(), '$usr{'id_admin_users'}')|;
		$id_movement = &Do_SQL($query)->{'mysql_insertid'};
		$query = qq|INSERT INTO sl_movements_auxiliary(ID_movements, FieldName, FieldValue) VALUES
		($id_movement, 'Description', 'Movimiento de Cierre de Periodo $periodo_name14')|;
		&Do_SQL($query);
		# $query = qq|update sl_movements_auxiliary set FieldValue = $in{'id_accounting_periods14'} where ID_movements = '$id_movement' and FieldName = 'ID_accounting_periods'|;
		# &Do_SQL($query);


		### Llamamos procedimiento para Actualizar periodo 14, tambien cerramos periodo 14
		# $query = qq|call update_closing_balance($in{'id_accounting_periods14'}, $in{'id_accounting_periods13'})|;
		# &Do_SQL($query);

		# $query = qq|call update_parents_accounts($in{'id_accounting_periods14'})|;
		# &Do_SQL($query);
		$query = qq|update sl_journalentries set status = 'Posted' where id_journalentries = $id_journalentries|;
		&Do_SQL($query);

		$query = qq|update sl_accounting_periods set Status = 'Closed' where id_accounting_periods = $in{'id_accounting_periods14'}|;
		# &Do_SQL($query);
		&Do_SQL("COMMIT");
		# print $id_journalentries;	
		# exit;
		$va{'message_good'} = qq|Se creo Journalentries: $id_journalentries, con los movimientos de Cierre de Periodos $periodo_name14|;
	}
	$in{'action'} = 'add';
	$in{'id_accounts'} = '';
	$va{'expanditem'} = 1;
	print "Content-type:text/html\n\n";
	print &build_page("end_exercise.html")
}

#############################################################################
#############################################################################
#   Function: fin_billingonoff
#
#       Es: Activa o Inactiva el sitio de facturación
#       En: 
#
#
#    Created on: 2013-06-11
#
#    Author: ISC J. Alfredo Salazar
#
#    Modifications:
#		ISC Gilberto Quirino 
#			- 06-10-2017 :: Muestra el log de modificaciones
#
#   Parameters:
#
#      -   
#
#  Returns:
#
#      - 
#
#   See Also:
#
#
sub fin_billingonoff{
#############################################################################
#############################################################################

	if(&check_permissions('fin_billingonoff','','')){
		my ($sth) = &Do_SQL('SELECT VValue FROM sl_vars WHERE VName="billingstat"');
		my ($stat) = $sth->fetchrow();
		$va{'stat'}=$stat;

		$va{'matches'} = 'Last 20 rows';
		$va{'pageslist'} = 1;
		my (@c) = split(/,/,$cfg{'srcolors'});
		
		my $sql_log = "SELECT admin_logs.*, admin_users.FirstName, admin_users.MiddleName, admin_users.LastName
						FROM (
								SELECT *
								FROM admin_logs
								WHERE tbl_name='sl_vars' AND admin_logs.Logcmd='billingcontrol'
								ORDER BY LogDate DESC, LogTime DESC
								LIMIT 50
							) admin_logs
							INNER JOIN admin_users ON admin_logs.ID_admin_users = admin_users.ID_admin_users
						WHERE 1
						LIMIT 20;";
		my $sth_log = &Do_SQL($sql_log);

		while ($rec_log = $sth_log->fetchrow_hashref){
			$d = 1 - $d;
			$va{'searchresults'} .= "<tr bgcolor='$c[$d]'>\n";
			$va{'searchresults'} .= "  <td class='smalltext'>".$rec_log->{'LogDate'}."</td>\n";
			$va{'searchresults'} .= "  <td class='smalltext'>".$rec_log->{'LogTime'}."</td>\n";
			$va{'searchresults'} .= "  <td class='smalltext'>".$rec_log->{'Message'}."</td>\n";		
			$va{'searchresults'} .= "  <td class='smalltext'>(".$rec_log->{'ID_admin_users'}.") ".$rec_log->{'FirstName'}." ".$rec_log->{'LastName'}." ".$rec_log->{'MiddleName'}."</td>\n";		
			$va{'searchresults'} .= "  <td class='smalltext'>".$rec_log->{'IP'}."</td>\n";		
			$va{'searchresults'} .= "</tr>\n";
		}

		print "Content-type: text/html\n\n";
		print &build_page('fin_billingonoff.html');
	}else{
		&html_unauth;
	}
}

#############################################################################
#############################################################################
#   Function: chart_of_accounts
#
#       Es: Catalogo de Cuentas Contables
#       En: 
#
#
#    Created on: 2013-06-11
#
#    Author: ISC Alejandro Diaz
#
#    Modifications:
#
#
#   Parameters:
#
#      - export: Variable para determinar que se debe generar el reporte exportable
#      -   
#
#  Returns:
#
#      - 
#
#   See Also:
#
#
sub chart_of_accounts {
#############################################################################
#############################################################################
	# Obtenemos informacion de la empresa
	&get_company_info();

	$va{'expanditem'} = 1;
	$va{'html_print'};
	my $tab_char = ($in{'type'} eq 'csv')? "    ":"&nbsp;&nbsp;&nbsp;&nbsp;";

	$va{'csv'} .= qq|$va{'company_name'}\n|;
	$va{'csv'} .= qq|Catalogo de Cuentas\n\n|;
	$va{'csv'} .= qq|"Nivel","Cuenta","Nombre","Tipo","","Dig Agr","Edo Fin","Moneda","Seg Neg","Rubro NIF","Agrup SAT","Estatus"\n|;

	$query = "SELECT 
		sl_accounts.level
		, sl_accounts.ID_accounting
		, sl_accounts.Name
		, CONCAT((SELECT nature.Name FROM sl_accounts_nature nature WHERE nature.ID_accounts_nature=sl_accounts_nature.ID_parent),' ',sl_accounts_nature.Name)Type
		, CASE WHEN sl_accounts.isdetailaccount='Si' THEN 'Afectable' ELSE '' END AS 'isdetailaccount'
		, '' AS 'Dig Agr'
		, '' AS 'Edo Fin'
		, sl_accounts.Currency
		, sl_accounts.Segment
		, '' AS 'Rubro NIF'
		, sl_agrupadorsat.codigoAgrupador
		, sl_accounts.Status
	FROM sl_accounts
	LEFT JOIN sl_accounts_nature ON sl_accounts_nature.ID_accounts_nature=sl_accounts.ID_account_nature
	LEFT JOIN sl_agrupadorsat ON sl_agrupadorsat.id_agrupadorSat=sl_accounts.id_agrupadorSat
	WHERE sl_accounts.Status = 'Active'
	ORDER BY sl_accounts.ID_accounting";
	$sth = &Do_SQL($query);
	while(my $row = $sth->fetchrow_hashref()){
		my $level_tab = $tab_char x (int($row->{'level'})-1);
		
		my $class_highlights = ($row->{'level'} == 1)? 'highlights':'';
		$class_highlights .= ($row->{'Status'} eq 'Inactive')? ' inactive':'';
		my $id_accounting = &format_account($row->{'ID_accounting'});

		$va{'html_print'} .= qq|
		<tr class="">
			<td nowrap class="$class_highlights">$level_tab$row->{'level'}</td>
			<td nowrap class="$class_highlights" align="right">$id_accounting</td>
			<td nowrap class="$class_highlights">$level_tab$row->{'Name'}</td>
			<td nowrap class="$class_highlights">$row->{'Type'}</td>
			<td nowrap class="$class_highlights">$row->{'isdetailaccount'}</td>
			<td nowrap class="$class_highlights">$row->{'Dig Agr'}</td>
			<td nowrap class="$class_highlights">$row->{'Edo Fin'}</td>
			<td nowrap class="$class_highlights">$row->{'Currency'}</td>
			<td nowrap class="$class_highlights">$row->{'Segment'}</td>
			<td nowrap class="$class_highlights">$row->{'Rubro NIF'}</td>
			<td nowrap class="$class_highlights" align="right">$row->{'codigoAgrupador'}</td>
		</tr>|;

		$va{'csv'} .= qq|"$level_tab$row->{'level'}","$id_accounting","$level_tab$row->{'Name'}","$row->{'Type'}","$row->{'isdetailaccount'}","$row->{'Dig Agr'}","$row->{'Edo Fin'}","$row->{'Currency'}","$row->{'Segment'}","$row->{'Rubro NIF'}","$row->{'codigoAgrupador'}","$row->{'Status'}"\n|;

	}
	
	## Impresion de archivo CSV
	if($in{'type'} eq 'csv'){
		my $f = lc($cfg{"app_title"}."-Catalogo de Cuentas");
		
		$f =~ s/ /_/g;
		print "Content-Disposition: attachment; filename=$f.csv;";
		print "Content-type: text/csv\n\n";
		print $va{'csv'};
		return;
	}

	print "Content-type: text/html\n\n";
	print &build_page('chart_of_accounts.html');
}


#############################################################################
#############################################################################
#   Function: acc_reclasification
#
#       Es: Genera Reporte en Excel con los movimientos bancarios y su afectacion operativa
#       En: 
#
#
#    Created on: 2014-08-00
#
#    Author: _Roberto Barcenas_
#
#    Modifications:
#
#
#   Parameters:
#
#      - in_export: Variable para determinar que se degenerar el reporte exportable
#      -   
#
#  Returns:
#
#      - 
#
#   See Also:
#
#
sub acc_reclasification{
#############################################################################
#############################################################################

	if($in{'action'}){


		if(!$in{'id_movements_bulk'}){
			$error{'id_movements_bulk'} = &trans_txt('required');
			$err++;
		}

		if(!$in{'id_accounts'}){
			$error{'id_accounts'} = &trans_txt('required');
			$err++;
		}

		if(!$in{'effdate_to'}){
			$error{'effdate_to'} = &trans_txt('required');
			$err++;
		}

		if(!validate_date_in_openperiod($in{'effdate_to'})){

			$error{'effdate_to'} = &trans_txt('invalid');
			$err++;

		}

		if(!$in{'category'}){
			$error{'category'} = &trans_txt('required');
			$err++;
		}


		if(!$err){

			$va{'thisresult'} .= qq|$in{'id_movements_bulk'}<br><br>|;
			my @ary_movs_ok; @ary_movs_fail; my @ary_movs_unposted; my $str_movements;
			my (@ary) = split(/\s+|,|\n|\t/,$in{'id_movements_bulk'});
			for my $i(0..$#ary){

				my $id_movements = int($ary[$i]);

				if($id_movements and $str_movements !~ /pp$id_movements;;/){

					$va{'thisresult'} .= qq|$id_movements<br>|;

					# ## Doing one record reclasification
					my ($sth) = &Do_SQL("SELECT IF(Credebit = 'Debit', 'Credit','Debit')AS ReverseNature FROM sl_movements WHERE sl_movements.ID_movements = ". $id_movements ." AND sl_movements.Status = 'Active' AND sl_movements.ID_journalentries > 0;");
					my ($this_reverse_nature) =  $sth->fetchrow();

					if($this_reverse_nature){

						## Starting Reclasification
						&Do_SQL("START TRANSACTION");

						## 1.1 Reversing original movement
						my (%overwrite) = ('effdate' => "$in{'effdate_to'}", 'category' => "$in{'category'}" ,'credebit' => "$this_reverse_nature", 'id_journalentries' => 0);
 						my $this_reverse_movement = &Do_selectinsert('sl_movements', "ID_movements = '$id_movements'", "", "", %overwrite);

						## 1.2. Generating New Record
						my (%overwrite) = ('id_accounts' => "$in{'id_accounts'}",'effdate' => "$in{'effdate_to'}", 'category' => "$in{'category'}", 'id_journalentries' => 0);
 						my $this_reclasification_movement = &Do_selectinsert('sl_movements', "ID_movements = '$id_movements'", "", "", %overwrite);


 						if($this_reverse_movement and $this_reclasification_movement){

 							## Reclasification OK
 							push(@ary_movs_ok, $id_movements);
 							&Do_SQL("COMMIT");

 						}else{

 							## Reclasification Failed
 							push(@ary_movs_fail, $id_movements . qq| - Failed|);
 							&Do_SQL("ROLLBACK");

 						}

					}else{

						## Movement Not Posted
						push(@ary_movs_unposted, $id_movements);

					}

				}else{

					if($str_movements =~ /pp$id_movements;;/){

						## Duplicated Record Found
						push(@ary_movs_fail, $ary[$_] . qq| - Duplicated|);

					}else{

						## Ary Element Not Numeric
						push(@ary_movs_fail, $ary[$_] . qq| - Not a Record ID|);

					}

				}

				$str_movements .= qq|pp$id_movements;;|;

			} ## for

			$va{'message'} = &trans_txt('done');
			$va{'thisresult'} = qq|Movements Done<br>|.join('<br>', @ary_movs_ok).qq|<br><br>Movements Not Posted Yet<br>|.join('<br>', @ary_movs_unposted).qq|<br><br>Movements Failed<br>|.join('<br>', @ary_movs_fail);

		}

	}


	print "Content-type: text/html\n\n";
	print &build_page('acc_reclasification.html');	

}


#############################################################################
#############################################################################
#   Function: acc_layout_load
#
#       Es: Ejecuta  contabilidad cargada de manera manual en pantalla o archivo
#       En: 
#
#
#    Created on: 2014-08-00
#
#    Author: _Roberto Barcenas_
#
#    Modifications:
#
#
#   Parameters:
#
#      - id_movements_bulk: Variable con lineas a ejecutar
#      -   
#
#  Returns:
#
#      - 
#
#   See Also:
#
#
sub acc_layout_load{
#############################################################################
#############################################################################

	$va{'path_layouts'} = $cfg{'path_layouts'};
	
	if($in{'action'}){

		my @these_cols = ('ID_accounts','Debit','Credit','tableused','ID_tableused','tablerelated','ID_tablerelated','Category','EffDate','Reference','ID_journalentries');
		my @ary_ids_ok; my @ary_id_journalentries;

		if($in{'file_movements_bulk'}){

			my ($file) = $cfg{'path_layouts'} . $in{'file_movements_bulk'} ;


			## File Uploaded
			if(-e $file and -r $file and open (my $this_file, $file)) {
				
				## Open and Read File	
				while (my $record = <$this_file>) {

					## Loading records into variable
					chomp $record;
					$record =~ s/"//g;
					$in{'id_movements_bulk'} .= $record . "\n";

				}

				close $this_file;
				unlink($file);

			}else{

				## File Error
				$err++;
				$va{'message'} = &trans_txt('file_read_error') . '<br>' . $file;

			}

		}

		if(!$in{'id_movements_bulk'}){
			$error{'id_movements_bulk'} = &trans_txt('required');
			$err++;
		}

		if(!$err){

			$va{'thisresult'} .= qq|$in{'id_movements_bulk'}<br><br>|;
			my @ary_movs_ok; @ary_movs_fail;
			my (@ary_lines) = split(/\n/,$in{'id_movements_bulk'});

			## Starting Process
			&Do_SQL("START TRANSACTION");

			RECORDLINE: for(0..$#ary_lines){

				## Each Line
				my $modquery; my $this_amount_flag = 0;
				my $this_line = $ary_lines[$_]; $this_line =~ s/"//g;
				my (@ary_cols) = split(/,/,$this_line);

				###
				## Each Line Cols
				###
				if( abs(scalar @ary_cols  - scalar @these_cols ) ){

					## Invalid Line, Corrupt
					push(@ary_movs_fail, $this_line . qq| - <font color="red">Invalid Columns Count (|. scalar @these_cols .qq| vs |. scalar @ary_cols .qq|)</font>|);
					next RECORDLINE;

				}elsif(!validate_date_in_openperiod($ary_cols[8])){

					## Invalid, Period Closed
					push(@ary_movs_fail, $this_line . qq| - <font color="red">Period Closed</font>|);
					next RECORDLINE;

				}else{

					## ID_accounts
					$ary_cols[0] =~ s/\D//g; 
					my ($sth) = &Do_SQL("SELECT ID_accounts FROM sl_accounts WHERE sl_accounts.Status = 'Active' AND (sl_accounts.ID_accounts = ". $ary_cols[0] ." OR sl_accounts.ID_accounting = ". $ary_cols[0] .") ;");
					$ary_cols[0] = $sth->fetchrow();


					if(!$ary_cols[0]){

						## Invalid ID_accounts
						push(@ary_movs_fail, $this_line . qq| - <font color="red">Invalid ID account (|. $ary_cols[0] .qq|)</font>|);
						next RECORDLINE;

					}

				}



				## Load Variables INTO query string
				for (0..$#ary_cols){

					$ary_cols[$_] =~ s/^[^a-zA-Z0-9]+|[^a-zA-Z0-9]+$//g;
					
					if($these_cols[$_] eq 'Debit' and $ary_cols[$_] > 0){

						## Debit Amount
						$modquery .= qq| Amount = '| . &round($ary_cols[$_],2) .qq|', Credebit = '|. $these_cols[$_] .qq|', |;
						++$this_amount_flag;

					}elsif($these_cols[$_] eq 'Credit' and $ary_cols[$_] > 0){

						## Credit Amount
						$modquery .= qq| Amount = '| . &round($ary_cols[$_],2) .qq|', Credebit = '|. $these_cols[$_] .qq|', |;
						++$this_amount_flag;

					}elsif($these_cols[$_] !~ /Debit|Credit/){

						## All Columns
						$modquery .= $these_cols[$_] ." = '". &filter_values($ary_cols[$_]) ."', " if $ary_cols[$_];

						
						if ($these_cols[$_] eq 'ID_journalentries' and $ary_cols[$_]){

							## Storing ID_journalentries | grep is used as NOT in array to store unique values and 
							my $hits = 0; my $i = $_;
							for(0..$#ary_id_journalentries){ 

								my $j = $_;
								++$hits if $ary_id_journalentries[$j] == $ary_cols[$i]; 

							}
							push(@ary_id_journalentries, int($ary_cols[$i]) ) if !$hits;

						} $str.= "<br>";

					}

				}

				if(!$this_amount_flag){

					## Invalid Amount
					push(@ary_movs_fail, $this_line . qq| - <font color="red">Amount Not Found</font>|);
					next RECORDLINE;

				}

				## Generating New Record
				my $query = "INSERT INTO sl_movements SET ". $modquery ." Date = CURDATE(), Time = CURTIME(), ID_admin_users = '". $usr{'id_admin_users'} ."';";
				my ($sth) = &Do_SQL($query);
				my $this_record = $sth->{mysql_insertid};
				push(@ary_ids_ok, $this_record);

				if($this_record){

					## Record Insertion OK
					push(@ary_movs_ok, $this_record .qq| - | . $this_line );

				}else{

					## Record Insertion Failed
					push(@ary_movs_fail, $this_line . qq| - <font color="red">Failed $query</font>|);

				}

			} ## for i

			###
			##  Final Validations
			###


			##Journal Same Category Records
			my $these_categories, $emptycategories;
			if(scalar @ary_ids_ok){

				my ($sth) = &Do_SQL("SELECT
										COUNT(DISTINCT sl_movements.Category) AS TCategories
										, SUM(IF(sl_movements.Category IS NULL OR sl_movements.Category = '',1,0))AS EmptyCategory
									FROM
										sl_movements
									WHERE
										sl_movements.ID_movements
									IN
									(
										". join(',', @ary_ids_ok) ."
									)	");
				($these_categories, $emptycategories) = $sth->fetchrow();

			}


			if(scalar @ary_id_journalentries){

				##Journal Same Category Records
				my ($sth) = &Do_SQL("SELECT
										sl_journalentries.ID_journalentries
										, COUNT(DISTINCT sl_movements.Category)
										, GROUP_CONCAT(DISTINCT sl_movements.Category)
										, sl_journalentries.Status
									FROM
										sl_movements INNER JOIN sl_journalentries
										ON sl_movements.ID_journalentries = sl_journalentries.ID_journalentries
									WHERE
										sl_journalentries.ID_journalentries
									IN
									(
										". join(',', @ary_id_journalentries) ."
									)
									GROUP BY 
										sl_journalentries.ID_journalentries;");
				while(my ($this_id_journalentries, $hits_categories, $group_categories, $this_status_journalentries) = $sth->fetchrow() ){

					## Eval each line looking for errors
					if($hits_categories > 1){

						## More than one categorie in Journal.
						push(@ary_movs_fail, $this_line . qq| - <font color="red">|. $this_id_journalentries .qq| Contains |. $hits_categories .qq| Categories(|. $group_categories .qq|) </font>|);

					}

					if($this_status_journalentries !~ /New|Assigned/i){

						## Status incorrect in Journal
						push(@ary_movs_fail, $this_line . qq| - <font color="red">|. $this_id_journalentries .qq| Status incorrect  (|. $this_status_journalentries .qq|) </font>|);

					}

				}

			}

			# or $these_categories > 1
			if(scalar @ary_movs_fail){

				#### Errors Detected
				&Do_SQL("ROLLBACK;");
				@ary_movs_ok = ();
				$va{'message'} = &trans_txt('acc_layout_load_movsfail');

			}elsif($these_categories > 1 or $emptycategories){

				#### Errors Detected
				&Do_SQL("ROLLBACK;");
				@ary_movs_ok = ();
				$va{'message'} = &trans_txt('acc_layout_load_categoryfail');


			}else{

				## Everything OK
				&Do_SQL("COMMIT;");
				$va{'message'} = &trans_txt('done');

			}

			delete($in{'id_movements_bulk'});
			$va{'thisresult'} = qq|<font color="Green">Movements Done</font><br>|.join('<br>', @ary_movs_ok).qq|<br><br><font color="blue">Movements Failed</font><br>|.join('<br>', @ary_movs_fail);

		}

	}


	print "Content-type: text/html\n\n";
	print &build_page('acc_layout_load.html');	

}




1;