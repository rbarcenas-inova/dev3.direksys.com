#!/usr/bin/perl
##################################################################
############              CONSOLE                #################
##################################################################




sub console {
# --------------------------------------------------------
	$cses{'start_sec'} = &get_sec();
	$cses{'items_in_basket'} = 0;
	$cses{'sameshipping'} = "same";
	$cses{'id_salesorigins'} = $in{'origin'} if ($in{'origin'} and !$cses{'id_salesorigins'});
	$cses{'pterms'} = 'Contado' if !$cses{'pterms'};
	$cses{'currency'} = $cfg{'acc_default_currency'};
	$va{'salesorigins.channel'} = &load_name("sl_salesorigins","ID_salesorigins",$cses{'id_salesorigins'},"channel") if($cses{'id_salesorigins'});
	$in{'step'} = int($in{'step'});	
	print "Content-type: text/html\n\n";	
	$va{'tblw'} = $sys{'console_'.$usr{'application'}.'tbl'};

	$va{'mfw'} = $sys{'console_'.$usr{'application'}.'mfw'};
	$va{'mfh'} = $sys{'console_'.$usr{'application'}.'mfh'};
	$va{'stw'} = $sys{'console_'.$usr{'application'}.'stw'};
	$va{'sth'} = $sys{'console_'.$usr{'application'}.'sth'};
	
	
	if ($in{'action'} eq 'add_to_cart' and $in{'step'} eq "0"){
		### Shopping Cart
		my ($cant);
		foreach $key (keys %in){
			if ($key =~ /add_(\d+)/ and int($in{$key})>0){
				$va{'cart_out'} .= "&$1=".int($in{$key});
				++$cant;
			}
		}
		if ($cant > 0 ){
			$in{'step'} = 1;
		}else{
			$va{'message'} = &trans_txt('empty_cart');
		}
	}elsif ($in{'step'} eq "2" and $in{'id_orders'}>0){
			$in{'step'} = 2;
	}elsif ($in{'step'} eq "3" and $in{'id_orders'}>0){
			$in{'step'} = 3;
	}elsif ($in{'step'} eq "10"){
			$in{'step'} = 10;
	}

	if(-e "admin.step".$in{'step'}.".html.cgi"){
		require ("admin.step".$in{'step'}.".html.cgi");
	}

	print &build_page("console_step".$va{'steptemp'}.".html");
}




1;

