#####################################################################
########                   banks movements                  #########
#####################################################################
sub load_tabsconf {
# --------------------------------------------------------
	if($in{'tab'} eq 3){
		## Notes Tab
		$va{'tab_type'}  = 'logs';
		$va{'tab_title'} = &trans_txt('logs');
		$va{'tab_table'} = 'cu_promotions';
	}
}

##############################################
## tab1 : Rules
##############################################
sub load_tabs1{

	
	### Obtiene los detalles de la promoción
	my $sth_rules = &Do_SQL("SELECT * FROM cu_promotion_rules WHERE ID_promotions = ".$in{'id_promotions'}.";");
	my $promo_rules = $sth_rules->fetchrow_hashref();

	# if( $promo_rules->{'ID_products'} > 0 ){
		### Regla por tipo de pago
		if( $promo_rules->{'Ptype_flag'} ){
			if( $promo_rules->{'Ptype_ID_products'} ){
				$va{'promo_ptype'} = $promo_rules->{'Ptype_flag'};

				my $sql_prod = "SELECT ID_products, Model FROM sl_products WHERE ID_products IN(".$promo_rules->{'Ptype_ID_products'}.") AND `Status` = 'On-Air';";
				my $sth_prod = &Do_SQL($sql_prod);
				while( my $prod = $sth_prod->fetchrow_hashref() ){
					$va{'promo_ptype_products'} .= $prod->{'ID_products'}.': '.$prod->{'Model'}.'<br />';
				}
			}
		} else {
			$va{'promo_ptype'} = 'No Apply';
		}

		### Regla por la compra de un producto de catálogo
		if( $promo_rules->{'Catalog_flag'} ){
			if( $promo_rules->{'Catalog_ID_products'} ){
				$va{'promo_catalog'} = 'Apply';

				my $sql_prod = "SELECT ID_products, Model FROM sl_products WHERE ID_products IN(".$promo_rules->{'Catalog_ID_products'}.") AND `Status` = 'On-Air';";
				my $sth_prod = &Do_SQL($sql_prod);
				while( my $prod = $sth_prod->fetchrow_hashref() ){
					$va{'promo_catalog_products'} .= $prod->{'ID_products'}.': '.$prod->{'Model'}.'<br />';
				}
			}
		} else {
			$va{'promo_catalog'} = 'No Apply';
		}

		### Regla por monto mínimo
		if( $promo_rules->{'Min_amount_flag'} ){
			if( $promo_rules->{'Min_amount_ID_products'} ){
				$va{'promo_min_amt'} = &format_price($promo_rules->{'Min_amount_flag'});

				my $sql_prod = "SELECT ID_products, Model FROM sl_products WHERE ID_products IN(".$promo_rules->{'Min_amount_ID_products'}.") AND `Status` = 'On-Air';";
				my $sth_prod = &Do_SQL($sql_prod);
				while( my $prod = $sth_prod->fetchrow_hashref() ){
					$va{'promo_min_amt_products'} .= $prod->{'ID_products'}.': '.$prod->{'Model'}.'<br />';
				}
			}
		} else {
			$va{'promo_min_amt'} = 'No Apply';
		}

		### Regla por cada monto
		if( $promo_rules->{'Per_amount_flag'} ){
			if( $promo_rules->{'Per_amount_ID_products'} ){
				$va{'promo_per_amt'} = &format_price($promo_rules->{'Per_amount_flag'});

				my $sql_prod = "SELECT ID_products, Model FROM sl_products WHERE ID_products IN(".$promo_rules->{'Per_amount_ID_products'}.") AND `Status` = 'On-Air';";
				my $sth_prod = &Do_SQL($sql_prod);
				while( my $prod = $sth_prod->fetchrow_hashref() ){
					$va{'promo_per_amt_products'} .= $prod->{'ID_products'}.': '.$prod->{'Model'}.'<br />';
				}
			}
		} else {
			$va{'promo_per_amt'} = 'No Apply';
		}
		
	# } else {
		
	# }
}

##############################################
## tab2 : Customers
##############################################
sub load_tabs2{

	my (@c) = split(/,/,$cfg{'srcolors'});
	my ($name,$stlink);
	my ($sth) = &Do_SQL("SELECT COUNT(*) FROM cu_customer_promotions WHERE ID_promotions=".$in{'id_promotions'}.";");
	$va{'matches'} = $sth->fetchrow;

	if ($va{'matches'}>0){
		(!$in{'nh'}) and ($in{'nh'}=1);
		$first = ($in{'nh'} - 1) * $usr{'pref_maxh'};			
		($va{'pageslist'},$qs) = &pages_list($in{'nh'},"/cgi-bin/mod/$usr{'application'}/dbman",$va{'matches'},$usr{'pref_maxh'});

		my $sth = &Do_SQL("SELECT 
								sl_customers.ID_customers
								, CONCAT(sl_customers.FirstName, ' ', sl_customers.LastName1, ' ', sl_customers.LastName2) Name
								, sl_customers.City
								, sl_customers.State
								, sl_customers.Zip
								, cu_customer_promotions.Unique_code
								, cu_customer_promotions.ID_orders
							FROM cu_customer_promotions
								INNER JOIN sl_customers ON cu_customer_promotions.ID_customers = sl_customers.ID_customers
							WHERE cu_customer_promotions.ID_promotions = ".$in{'id_promotions'}."
							LIMIT ".$first.", ".$usr{'pref_maxh'}.";");
		while( my $rec = $sth->fetchrow_hashref() ){
			$va{'searchresults'} .= '<tr>';
			$va{'searchresults'} .= '<td>'.$rec->{'ID_customers'}.'</td>';
			$va{'searchresults'} .= '<td>'.$rec->{'Name'}.'</td>';
			$va{'searchresults'} .= '<td>'.$rec->{'City'}.'</td>';
			$va{'searchresults'} .= '<td>'.$rec->{'State'}.'</td>';
			$va{'searchresults'} .= '<td>'.$rec->{'Zip'}.'</td>';
			$va{'searchresults'} .= '<td>'.$rec->{'Unique_code'}.'</td>';
			$va{'searchresults'} .= '<td>'.$rec->{'ID_orders'}.'</td>';
			$va{'searchresults'} .= '<tr>';
		}

	} else {
		$va{'pageslist'} = 1;
		$va{'searchresults'} = qq|
			<tr>
				<td colspan='6' align="center">|.&trans_txt('search_nomatches').qq|</td>
			</tr>\n|;
	}

}

1;