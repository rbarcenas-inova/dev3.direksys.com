

sub custom_id_link {
# --------------------------------------------------------

	if ($in{'cmd'} eq 'mer_po'){
		if ($in{'id_purchaseorders'}>0 and &check_permissions($in{'cmd'},'_custom','')){
			my ($sth) = &Do_SQL("SELECT COUNT(*) FROM sl_purchaseorders WHERE Auth='In Process' AND Status='New' AND ID_purchaseorders=$in{'id_purchaseorders'} ");
			if ($sth->fetchrow ne 1){
				++$err;
			}
			if (!$err){
				my ($sth) = &Do_SQL("SELECT COUNT(*) FROM sl_movements WHERE  tableused='sl_purchaseorders' AND ID_tableused=$in{'id_purchaseorders'} ");
				if ($sth->fetchrow >0){
					++$err;
				}
			}
		}else{
			++$err;
		}
		if (!$err){
			return qq|
				<a href="/cgi-bin/common/apps/custom?cmd=mer_po&id=$in{'id_purchaseorders'}" class="fancy_modal_iframe">
					<img src='[va_imgurl]/[ur_pref_style]/b_special.gif' title='Custom App' alt='' border='0'>
				</a>|;
		}
	}elsif ($in{'cmd'} eq 'opr_orders' and &check_permissions($in{'cmd'},'_custom','')){
		if ($in{'id_orders'}>0){
			my ($sth) = &Do_SQL("SELECT COUNT(*) FROM sl_orders WHERE Status='New' AND ID_orders=$in{'id_orders'} ");
			if ($sth->fetchrow ne 1){
				++$err;
			}
			if (!$err){
				my ($sth) = &Do_SQL("SELECT COUNT(*) FROM sl_movements WHERE  tableused='sl_orders' AND ID_tableused=$in{'id_orders'} ");
				if ($sth->fetchrow >0){
					++$err;
				}
			}
		}else{
			++$err;
		}
		if (!$err){
			return qq|
				<a href="/cgi-bin/common/apps/custom?cmd=opr_orders&id=$in{'id_orders'}" class="fancy_modal_iframe">
					<img src='[va_imgurl]/[ur_pref_style]/b_special.gif' title='Custom App' alt='' border='0'>
				</a>|;
		}
	}elsif ($in{'cmd'} eq 'mer_bills' and &check_permissions($in{'cmd'},'_custom','')){
		if ($in{'id_bills'}>0){
			if (&load_name('sl_bills','ID_bills',$in{'id_bills'},'Status') eq 'Paid'){
				++$err;
			}
			if (!$err){
				my ($sth) = &Do_SQL("SELECT COUNT(*) FROM sl_movements WHERE  tableused='sl_bills' AND ID_tableused=$in{'id_bills'} ");
				if ($sth->fetchrow >0){
					++$err;
				}
			}
		}else{
			++$err;
		}
		if (!$err){
			return qq|
				<a href="/cgi-bin/common/apps/custom?cmd=mer_bills&id=$in{'id_bills'}" class="fancy_modal_iframe">
					<img src='[va_imgurl]/[ur_pref_style]/b_special.gif' title='Custom App' alt='' border='0'>
				</a>|;
		}
	}
	return ;
}

1;