#!/usr/bin/perl
	$va{'steptemp'} = 3;
	if($in{'action'} eq 'finish' and $in{'id_orders'} > 0){
		my $data = loadDataPos();
		$id_customers = $data{'customer'};
		$id_warehouses = $data{'warehouse'};
		my($id_orders) = $in{'id_orders'};
		#Verificamos el PAgo de la Orden
		my ($sth) = &Do_SQL("SELECT * from sl_orders_payments WHERE 1 
			AND ID_orders = '$id_orders'
			AND  Status != 'Cancelled'
			AND Captured = 'Yes'
			AND Capdate != '0000-00-00' 
			AND Capdate != '' 
			AND not isnull(Capdate) ");
		if($rec = $sth->fetchrow_hashref){
			if($rec->{'PmtField7'} eq 'CreditCard'){
				$id_banks = 3;
				my ($sth2) = &Do_SQL("INSERT INTO sl_banks_movements
				SET
				ID_banks = '$id_banks',
				Type='Debits',
				BankDate = NOW(),
				Amount = '$rec->{Amount}',
				RefNumCustom = '$rec->{ID_orders}',
				doc_type = 'NA',
				Status = 'Active',
				Date = NOW(),
				TIME = NOW(),
				Memo = '$rec->{ID_orders}'");
				$id_banks_movements = $sth2->{'mysql_insertid'};
				my ($sth3) = &Do_SQL("INSERT INTO sl_banks_movrel
				SET
				ID_banks_movements = '$id_banks_movements',
				tablename = 'orders_payments',
				tableid = '$rec->{ID_orders_payments}',
				AmountPaid = '$rec->{Amount}',
				Status = 'Active',
				Date = NOW(),
				Time = NOW()
				");
				my ($sth) = &Do_SQL("SELECT Ptype, Type FROM sl_orders INNER JOIN sl_customers USING(ID_customers) WHERE ID_orders = '$id_orders';");
				($order_type, $ctype) = $sth->fetchrow();
			
				my ($tracking) = &urlencode("$cfg{'prefixentershipment'}$id_orders\nups\@12345");
				my ($url) = $cfg{'entershipment'}."?cmd=entershipment&sid=&e=$in{e}&action=1&tracking=$tracking&shpdate=$shpdate&id_warehouses=$id_warehouses&bulk=1&scan_from_pack=1";
				#&cgierr($url);
				use LWP::UserAgent;
				use HTTP::Request::Common;
				$ua=new LWP::UserAgent;	
				my $req = HTTP::Request->new(GET => $url);
				$resp = $ua->request($req);
				$va{'cc'} = 'ok';
				$va{'error'} = '0';
			}			
		}else{
			$va{'error'} = 'error_order';
		}
	}
1;