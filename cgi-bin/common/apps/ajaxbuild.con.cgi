##########
########## New Sales
##########

#############################################################################
#############################################################################
# Function: sale_search_products
#
# Es: Realiza la busqueda dinamica de productos
# En: 
#
# Created on: 11/02/2016 
#
# Author: Ing. Gilberto Quirino
#
# Modifications:
#
# Parameters:
#
#
# Returns:
#
#
# See Also:
#
#
sub sale_search_products{
#############################################################################
#############################################################################

	use JSON;

	my %json_data;
	my $general_result = 'OK';
	my $sql = '';

	if( ($in{'pay_type_available'} and $in{'pay_type_available'} ne '') or int($in{'zipcode'}) > 0 ){
		
		if( $in{'pay_type_available'} eq '' and int($in{'zipcode'}) > 0 ){
			$sql = "SELECT sl_zones.Payment_Type
					FROM sl_zipcodes
						INNER JOIN sl_zones USING(ID_zones)
					WHERE 1
						AND sl_zipcodes.ZipCode='".$in{'zipcode'}."' 
						AND sl_zipcodes.`Status` = 'Active' 
						AND sl_zones.`Status` = 'Active';";
			my $sth_zone = &Do_SQL($sql);
			my $data_zone = $sth_zone->fetchrow_hashref();

			$in{'pay_type_available'}	= $data_zone->{'Payment_Type'};			
		}

		### Preparacion de las formas de pago
		$in{'pay_type_available'} =~ s/\,/\'\,\'/g;
		### Preparacion del origen de venta
		my $id_salesorigins = int($in{'id_salesorigins'});
		### Preparacion del texto de busqueda
		my $txtsearch = &filter_values($in{'txt_search'});
		$txtsearch = &filter_text_match($txtsearch);
		### Se procesa el texto recibido para generar una búsqueda mas exacta
		my $sql_txt_search = '';
		if( $txtsearch =~ /\s/ ){
			my @words = split(/\s/, $txtsearch);
			foreach $word(@words){
				$word =~ s/\s+//g; 
				if( $word !~ /\s/ and $word ne ""){
					if( $word =~ /\d{1,}/ ){
						$sql_txt_search .= ($sql_txt_search ne '') ? " OR (MATCH(sl_products.Model) AGAINST('*".$word."*' IN BOOLEAN MODE) OR sl_products.ID_products LIKE '%".$word."%') " : " (MATCH(sl_products.Model) AGAINST('*".$word."*' IN BOOLEAN MODE) OR sl_products.ID_products LIKE '%".$word."%') ";
					}else{
						$sql_txt_search .= ($sql_txt_search ne '') ? " AND MATCH(sl_products.Model) AGAINST('*".$word."*' IN BOOLEAN MODE) " : " MATCH(sl_products.Model) AGAINST('*".$word."*' IN BOOLEAN MODE) ";
					}
				}
			}

			$sql_txt_search = "AND (".$sql_txt_search.")" if( $sql_txt_search ne '' );
		}elsif( $txtsearch =~ /^\d{1,}+$/ ){
			$sql_txt_search = "AND sl_products.ID_products LIKE '%".$txtsearch."%'";
		}elsif( $txtsearch ne '' ){
			$sql_txt_search = "AND (MATCH(sl_products.Model) AGAINST('*".$txtsearch."*' IN BOOLEAN MODE) OR MATCH(sl_products.Name) AGAINST('*".$txtsearch."*' IN BOOLEAN MODE))";
		}

		### Si se recibe la forma de pago
		$sql_pay_type = ($in{'pay_type'}) ? " AND sl_products_prices.PayType = '".$in{'pay_type'}."'" : " AND sl_products_prices.PayType IN('".$in{'pay_type_available'}."')";

		### Si se recibe la cantidad de pagos
		$sql_fpmts = " AND sl_products_prices.FP = ".$in{'fpmts'}." " if( $in{'fpmts'} and int($in{'fpmts'}) > 0 );

		### Filtro del status del producto
		my $sql_status_prod = '';
		if( $cfg{'pauta_seca_enabled'} and $cfg{'pauta_seca_enabled'} == 1 ){
			$sql_status_prod = " IN('On-Air','Pauta Seca') ";
		}else{
			$sql_status_prod = " = 'On-Air' ";
		}

		###--------------------------------------------
		### Búsquedas predefinidas
		###--------------------------------------------
		my $sql_join = '';
		if( $in{'filter'} and $in{'filter'} eq 'topsales' ){
						
			$sql_join = "INNER JOIN cu_topsales_products ON cu_topsales_products.ID_products = sl_products.ID_products";

		}elsif( $in{'filter'} and $in{'filter'} eq 'lastorder' ){
			my $sql_cus = "SELECT GROUP_CONCAT(DISTINCT RIGHT(sl_orders_products.ID_products, 6)) AS ids_products
								, GROUP_CONCAT(DISTINCT sl_orders_products.Related_ID_products) AS ids_prod_rel
							FROM sl_orders_products
								INNER JOIN (
									SELECT MAX(sl_orders.ID_orders) ID_orders
									FROM sl_orders	
									WHERE sl_orders.Date >= DATE_SUB(CURDATE(), INTERVAL 30 DAY)
										AND sl_orders.`Status` != 'System Error' 
										AND sl_orders.ID_salesorigins = ".$id_salesorigins."
								)sl_orders ON sl_orders_products.ID_orders = sl_orders.ID_orders
							WHERE 1 AND sl_orders_products.ID_products < 600000000
							#GROUP BY sl_orders_products.ID_products 
							LIMIT 1;";
			my $sth_cus = &Do_SQL($sql_cus);
			my $dat_cus = $sth_cus->fetchrow_hashref();
			if( $dat_cus->{'ids_products'} ){
				$sql_txt_search = " AND sl_products.ID_products IN(".$dat_cus->{'ids_products'};
				$sql_txt_search .= ( $dat_cus->{'ids_prod_rel'} ) ? ",".$dat_cus->{'ids_prod_rel'}.") " : ") ";
			}
		}

		###--------------------------------------------
		### Paginación
		###--------------------------------------------		
		# Página actual
		my $current_page = ($in{'current_page'} and int($in{'current_page'}) > 0) ? $in{'current_page'} : 1;
		# productos mostrados por página
		my $prod_per_page = ($in{'prod_per_page'} and int($in{'prod_per_page'}) > 0) ? $in{'prod_per_page'}  :10;
		# Limit
		$limit_start = $prod_per_page * ($current_page - 1);

		### Se obtiene la cantidad de productos encontrados con las condiciones definidas
		my $sql_qty = "SELECT COUNT(*)
						FROM sl_products 
							INNER JOIN (
								SELECT sl_products_prices.ID_products 
								FROM sl_products_prices 
								WHERE 1
									AND sl_products_prices.`Status` = 'Active' 
									AND sl_products_prices.Origins LIKE '%|".$id_salesorigins."|%'
									".$sql_pay_type." 
									".$sql_fpmts."
								GROUP BY sl_products_prices.ID_products 
							)sl_products_prices ON sl_products.ID_products = sl_products_prices.ID_products
							".$sql_join."
						WHERE 1
							".$sql_txt_search."
							AND sl_products.`Status`".$sql_status_prod.";";
		my $sth_qty = &Do_SQL($sql_qty);
		my $total_prod_find = $sth_qty->fetchrow();

		if( $total_prod_find > 0 ){

			my $sql_limit = '';
			if( $in{'filter'} and $in{'filter'} eq 'topsales' ){
				$sql_limit = " LIMIT 50";
				$sql_order = " ORDER BY cu_topsales_products.Quantity DESC";
			}else{
				$sql_limit = " LIMIT ".$limit_start.", ".$prod_per_page;
				$sql_order = " ORDER BY sl_products.Model, sl_products.Name";
			}

			###--------------------------------------------
			### Se obtienen los datos generales del producto
			###--------------------------------------------
			$sql = "SELECT sl_products.ID_products
						, sl_products.Model
						, sl_products.Name AS ProductName
						, sl_products.`Status` 
						, ( SELECT COUNT(*) 
							FROM sl_skus 
							WHERE ID_products=sl_products.ID_products 
								AND sl_skus.`Status`='Active'
								AND (
									(sl_skus.choice1 != '' AND sl_skus.choice1 IS NOT NULL) 
									OR (sl_skus.choice2 != '' AND sl_skus.choice2 IS NOT NULL) 
									OR (sl_skus.choice3 != '' AND sl_skus.choice3 IS NOT NULL) 
									OR (sl_skus.choice4 != '' AND sl_skus.choice4 IS NOT NULL)
								)
						   ) AS choices
						, sl_vars.VValue AS promo
						, sl_products.free_shp_opt
						, sl_products.TaxAux
					FROM sl_products 
						INNER JOIN sl_products_prices ON sl_products.ID_products = sl_products_prices.ID_products
							AND sl_products_prices.`Status` = 'Active' 
							AND sl_products_prices.Origins LIKE '%|".$id_salesorigins."|%'
							".$sql_pay_type." 
							".$sql_fpmts."
						".$sql_join."
						LEFT JOIN( 
							SELECT VName, VValue FROM sl_vars WHERE sl_vars.VName LIKE 'promo%' GROUP BY VName
						) sl_vars ON RIGHT(sl_vars.VName, 6) = sl_products.ID_products						
					WHERE 1
						".$sql_txt_search." 
						AND sl_products.`Status`".$sql_status_prod." 						
					GROUP BY sl_products_prices.ID_products
					".$sql_order."
					".$sql_limit.";";
			$json_data{'sql'} = $sql;
			my $sth_prod = &Do_SQL($sql);

			my $i = 0;
			while( my $rec_prod = $sth_prod->fetchrow_hashref() ){

				### Se obtienen los datos de las formas de pago
				$sql = "SELECT sl_products_prices.ID_products_prices
							, sl_products_prices.Name PriceName
							, sl_products_prices.Price
							, sl_products_prices.AuthCode
							, sl_products_prices.FP AS FlexiPmts
							, sl_products_prices.PayType
						FROM sl_products_prices 
						WHERE 1
							AND sl_products_prices.ID_products = ".$rec_prod->{'ID_products'}."
							AND sl_products_prices.`Status` = 'Active' 
							AND sl_products_prices.Origins LIKE '%|".$id_salesorigins."|%'
							/*AND sl_products_prices.Price >= 1*/
							".$sql_pay_type." 
							".$sql_fpmts." 
						ORDER BY sl_products_prices.Price DESC, sl_products_prices.PayType, sl_products_prices.FP DESC, sl_products_prices.Name;";
				my $sth_prices = &Do_SQL($sql);
				#$json_data{'sql'} = $sql;
				my $j = 0;
				while( my $rec_prices = $sth_prices->fetchrow_hashref() ){
					$json_data{'products'}{$i}{'prices'}{$j}{'id_prod_prices'} = $rec_prices->{'ID_products_prices'};
					$json_data{'products'}{$i}{'prices'}{$j}{'pay_type'} = $rec_prices->{'PayType'};
					$json_data{'products'}{$i}{'prices'}{$j}{'price_name'} = $rec_prices->{'PriceName'};
					$json_data{'products'}{$i}{'prices'}{$j}{'price'} = round($rec_prices->{'Price'}, 2);
					$json_data{'products'}{$i}{'prices'}{$j}{'tax_pct'} = round($rec_prod->{'TaxAux'}, 2);
					#$json_data{'products'}{$i}{'prices'}{$j}{'fprice'} = &format_price(round($rec_prices->{'Price'}, 2));
					$json_data{'products'}{$i}{'prices'}{$j}{'flexi_pmts'} = $rec_prices->{'FlexiPmts'};
					if( $rec_prices->{'PayType'} eq 'Credit-Card' ){
						$json_data{'products'}{$i}{'prices'}{$j}{'shipping'} = ($cfg{'shipment_cc_standard'}) ? $cfg{'shipment_cc_standard'} : 0;
					}elsif( $rec_prices->{'PayType'} eq 'Referenced Deposit' ){
						$json_data{'products'}{$i}{'prices'}{$j}{'shipping'} = ($cfg{'shipment_rd_standard'}) ? $cfg{'shipment_rd_standard'} : 0;
					}elsif( $rec_prices->{'PayType'} eq 'COD' ){
						$json_data{'products'}{$i}{'prices'}{$j}{'shipping'} = ($cfg{'shipment_cod_standard'}) ? $cfg{'shipment_cod_standard'} : 0;
					}

					$j++;
				}
				if( $j > 0 ){
					$json_data{'products'}{$i}{'id_products'} = $rec_prod->{'ID_products'};
					$json_data{'products'}{$i}{'model'} = $rec_prod->{'Model'};
					$json_data{'products'}{$i}{'name'} = $rec_prod->{'ProductName'};
					$json_data{'products'}{$i}{'status'} = $rec_prod->{'Status'};
					$json_data{'products'}{$i}{'choices'} = $rec_prod->{'choices'};
					$json_data{'products'}{$i}{'promo'} = ($rec_prod->{'promo'}) ? 1 : 0;
					$json_data{'products'}{$i}{'free_shp'} = (lc($rec_prod->{'free_shp_opt'}) eq lc('Yes') and int($cfg{'sales_free_shipping'}) == 1) ? 1 : 0;
					$json_data{'products'}{$i}{'prices_matches'} = $j;
					my $this_img = 'sales/prod/'.$rec_prod->{'ID_products'}.'.jpg';
					$json_data{'products'}{$i}{'image'} = (-e $cfg{'path_images'}.$this_img) ? '/sitimages/'.$this_img : '/sitimages/sales/prod/none.jpg';

					### Valida si es un promo y si los items de dicha promo tienen choices
					if( $json_data{'products'}{$i}{'choices'} == 0 and $rec_prod->{'promo'} ){
						### Obtienen los id_products de la promo
						my (@items_prod) = split(/\|/,$rec_prod->{'promo'});
						### Revisa si alguno de esos products tiene choices
						for( 0..$#items_prod ){
							if( $items_prod[$_] and $items_prod[$_] ne '' ){
								$sql = "SELECT COUNT(*) 
										FROM sl_skus 
										WHERE ID_products=".$items_prod[$_]." 
											AND sl_skus.`Status`='Active'
											AND (
												(sl_skus.choice1 != '' AND sl_skus.choice1 IS NOT NULL) 
												OR (sl_skus.choice2 != '' AND sl_skus.choice2 IS NOT NULL) 
												OR (sl_skus.choice3 != '' AND sl_skus.choice3 IS NOT NULL) 
												OR (sl_skus.choice4 != '' AND sl_skus.choice4 IS NOT NULL)
											);";
								my $sth = &Do_SQL($sql);
								my $choices = $sth->fetchrow();
								if( $choices > 0 ){
									$json_data{'products'}{$i}{'choices'} = $choices;
									last;
								}
							}
						}
					}
					$i++;
				}

				if( ($in{'filter'} and $in{'filter'} eq 'topsales') and $i == 10 ){
					last;
				}

			}
			### Total de productos en la página actual
			$json_data{'matches'} = $i;

			$total_prod_find = $i if( $in{'filter'} and ($in{'filter'} eq 'topsales' || $in{'filter'} eq 'lastorder') );

		}else{
			### Total de productos en la página actual
			$json_data{'matches'} = 0;
		}
		### Total de productos encontrados
		$json_data{'total_matches'} = $total_prod_find;

	}else{
		### Total de productos en la página actual
		$json_data{'matches'} = 0;
		$json_data{'zipcode'} = $in{'zipdoce'};
		### Total de productos encontrados
		$json_data{'total_matches'} = 0;
	}

	$json_data{'result'} = $general_result;
	
	print "Content-type: application/json\n\n";
	print encode_json(\%json_data);
}

#############################################################################
#############################################################################
# Function: sale_get_choices
#
# Es: Obtiene las opciones o choices(talla, color, etc) de los productos
# En: 
#
# Created on: 12/02/2016 
#
# Author: Ing. Gilberto Quirino
#
# Modifications:
#
# Parameters:
#
#
# Returns:
#
#
# See Also:
#
#
sub sale_get_choices{
#############################################################################
#############################################################################

	use JSON;

	my %json_data;
	my $sql;

	$json_data{'result'} = 'OK';

	### Si es un promo
	if( int($in{'promo'}) > 0 ){

		$sql = "SELECT VValue FROM sl_vars WHERE VName='promo".int($in{'id_product'})."';";
		my ($sth) = &Do_SQL($sql);
		my $promo = $sth->fetchrow;
		my (@items_prod) = split(/\|/,$promo) if( $promo );

		my $items_with_choices = 0;
		CHOICES: for( 0..$#items_prod ){
			
			next CHOICES if( int($items_prod[$_]) == 0 or !$items_prod[$_] );

			$sql = "SELECT Model, ChoiceName1, ChoiceName2, ChoiceName3, ChoiceName4
					FROM sl_products 
					WHERE ID_products = ".$items_prod[$_].";";
			my $sth_prod = &Do_SQL($sql);
			my $rec_prod = $sth_prod->fetchrow_hashref();

			my $choice_descrip = '';
			$choice_descrip = $rec_prod->{'ChoiceName1'}.'/' if( $rec_prod->{'ChoiceName1'} and $rec_prod->{'ChoiceName1'} ne '' );
			$choice_descrip .= $rec_prod->{'ChoiceName2'}.'/' if( $rec_prod->{'ChoiceName2'} and $rec_prod->{'ChoiceName2'} ne '' );
			$choice_descrip .= $rec_prod->{'ChoiceName3'}.'/' if( $rec_prod->{'ChoiceName3'} and $rec_prod->{'ChoiceName3'} ne '' );
			$choice_descrip .= $rec_prod->{'ChoiceName4'}.'/' if( $rec_prod->{'ChoiceName4'} and $rec_prod->{'ChoiceName4'} ne '' );
			#if( $choice_descrip ne '' ){
				$choice_descrip = substr($choice_descrip, 0, -1);

				$json_data{'choice_list'}{$items_with_choices}{'model'} = $rec_prod->{'Model'};
				$json_data{'choice_list'}{$items_with_choices}{'descrip'} = $choice_descrip;

				$sql = "SELECT ID_sku_products, choice1, choice2, choice3, choice4 
						FROM sl_skus 
						WHERE ID_products = ".$items_prod[$_]." AND sl_skus.`Status`='Active'
							AND (
								(sl_skus.choice1 != '' AND sl_skus.choice1 IS NOT NULL) 
								OR (sl_skus.choice2 != '' AND sl_skus.choice2 IS NOT NULL) 
								OR (sl_skus.choice3 != '' AND sl_skus.choice3 IS NOT NULL) 
								OR (sl_skus.choice4 != '' AND sl_skus.choice4 IS NOT NULL)
							);";
				my $sth_chc = &Do_SQL($sql);

				my $i = 0;
				while( my $rec_chc = $sth_chc->fetchrow_hashref() ){
					my $choice_value = '';
					$choice_value = $rec_chc->{'choice1'}.' :: ' if( $rec_chc->{'choice1'} );
					$choice_value .= $rec_chc->{'choice2'}.' :: ' if( $rec_chc->{'choice2'} );
					$choice_value .= $rec_chc->{'choice3'}.' :: ' if( $rec_chc->{'choice3'} );
					$choice_value .= $rec_chc->{'choice4'}.' :: ' if( $rec_chc->{'choice4'} );
					$choice_value = substr($choice_value, 0, -4) if( $choice_value ne '' );

					$json_data{'choice_list'}{$items_with_choices}{'items'}{$i}{'value'} = $choice_value;
					$json_data{'choice_list'}{$items_with_choices}{'items'}{$i}{'id_sku_prod'} = $rec_chc->{'ID_sku_products'};
					$i++;
				}
				#$items_with_choices++;
			#}else{
				if( $i == 0 ){
					$sql = "SELECT ID_sku_products 
							FROM sl_skus 
							WHERE ID_products = ".$items_prod[$_].";";
					my $sth_sku = &Do_SQL($sql);
					my $id_sku_prod = $sth_sku->fetchrow();

					$json_data{'choice_list'}{$items_with_choices}{'model'} = $rec_prod->{'Model'};
					$json_data{'choice_list'}{$items_with_choices}{'descrip'} = 'MODELO';
					$json_data{'choice_list'}{$items_with_choices}{'matches'} = 0;
					$json_data{'choice_list'}{$items_with_choices}{'id_sku_prod'} = $id_sku_prod;
				}else{
					$json_data{'choice_list'}{$items_with_choices}{'matches'} = $i;
				}

				$items_with_choices++;
			#}
		}

		$json_data{'items_matches'} = $items_with_choices;

	### Si es solo un producto
	}else{
		$json_data{'items_matches'} = 1;
		###---------------------------------------------------------------------------
		$sql = "SELECT Model, ChoiceName1, ChoiceName2, ChoiceName3, ChoiceName4
				FROM sl_products 
				WHERE ID_products = ".$in{'id_product'}.";";
		my $sth_prod = &Do_SQL($sql);
		my $rec_prod = $sth_prod->fetchrow_hashref();

		my $choice_descrip = '';
		$choice_descrip = $rec_prod->{'ChoiceName1'}.'/' if( $rec_prod->{'ChoiceName1'} and $rec_prod->{'ChoiceName1'} ne '' );
		$choice_descrip .= $rec_prod->{'ChoiceName2'}.'/' if( $rec_prod->{'ChoiceName2'} and $rec_prod->{'ChoiceName2'} ne '' );
		$choice_descrip .= $rec_prod->{'ChoiceName3'}.'/' if( $rec_prod->{'ChoiceName3'} and $rec_prod->{'ChoiceName3'} ne '' );
		$choice_descrip .= $rec_prod->{'ChoiceName4'}.'/' if( $rec_prod->{'ChoiceName4'} and $rec_prod->{'ChoiceName4'} ne '' );
		$choice_descrip = substr($choice_descrip, 0, -1);

		$json_data{'choice_list'}{0}{'model'} = $rec_prod->{'Model'};
		$json_data{'choice_list'}{0}{'descrip'} = $choice_descrip;
		###---------------------------------------------------------------------------

		$sql = "SELECT ID_sku_products, choice1, choice2, choice3, choice4 
				FROM sl_skus 
				WHERE ID_products = ".$in{'id_product'}." AND sl_skus.`Status`='Active'
					AND (
						(sl_skus.choice1 != '' AND sl_skus.choice1 IS NOT NULL) 
						OR (sl_skus.choice2 != '' AND sl_skus.choice2 IS NOT NULL) 
						OR (sl_skus.choice3 != '' AND sl_skus.choice3 IS NOT NULL) 
						OR (sl_skus.choice4 != '' AND sl_skus.choice4 IS NOT NULL)
					);";
		my $sth_chc = &Do_SQL($sql);

		my $i = 0;
		while( my $rec_chc = $sth_chc->fetchrow_hashref() ){
			### Se valida Precio/Choice
			$sql = "SELECT sl_products_prices.Price, sl_products_prices.ValidKits
					FROM sl_products_prices
					WHERE sl_products_prices.ID_products_prices = ".$in{'id_prod_price'}." 
						AND sl_products_prices.ValidKits LIKE '%".$rec_chc->{'ID_sku_products'}."%'
						AND sl_products_prices.ValidKits != '';";
			my $sth_price = &Do_SQL($sql);
			my ($this_price, $this_validkits) = $sth_price->fetchrow();

			if( $this_price ){
				my $choice_value = '';
				$choice_value = $rec_chc->{'choice1'}.' :: ' if( $rec_chc->{'choice1'} );
				$choice_value .= $rec_chc->{'choice2'}.' :: ' if( $rec_chc->{'choice2'} );
				$choice_value .= $rec_chc->{'choice3'}.' :: ' if( $rec_chc->{'choice3'} );
				$choice_value .= $rec_chc->{'choice4'} if( $rec_chc->{'choice4'} );
				$choice_value = substr($choice_value, 0, -4) if( substr($choice_value, -4) eq ' :: ' );

				$json_data{'choice_list'}{0}{'items'}{$i}{'value'} = $choice_value;
				$json_data{'choice_list'}{0}{'items'}{$i}{'id_sku_prod'} = $rec_chc->{'ID_sku_products'};
				$i++;
			}
		}
		$json_data{'choice_list'}{0}{'matches'} = $i;
	}

	print "Content-type: application/json\n\n";
	print encode_json(\%json_data);
}

#############################################################################
#############################################################################
# Function: sale_get_products_promo
#
# Es: Obtiene los productos de una promoción
# En: 
#
# Created on: 12/02/2016 
#
# Author: Ing. Gilberto Quirino
#
# Modifications:
#
# Parameters:
#
#
# Returns:
#
#
# See Also:
#
#
sub sale_get_products_promo{
#############################################################################
#############################################################################
	
	use JSON;

	my %json_data;
	my $sql = '';

	### Se obtienen los porcentajes de los precios de cada producto
	$sql = "SELECT VValue
			FROM sl_vars
			WHERE VName='percent_promo".int($in{'id_product'})."';";
	my $sth_var = &Do_SQL($sql);
	my $percents_promo = $sth_var->fetchrow();

	#if( $percents_promo ){

		my @products;
		my @sku_products;
		if( $in{'ids_products'} and $in{'ids_products'} ne '' ){
			@sku_products = split(/\,/,$in{'ids_products'});
			foreach my $i (0 .. $#sku_products){
				$products[$i] = substr($sku_products[$i], 3) if( $sku_products[$i] );
			}
		}else{
			$sql = "SELECT VValue
					FROM sl_vars
					WHERE VName='promo".int($in{'id_product'})."';";
			my $sth_prod = &Do_SQL($sql);
			my $this_products = $sth_prod->fetchrow();			
			$this_products =~ s/\|// if( $this_products =~ /^\|/ );

			@products = split(/\|/,$this_products);
		}		
		### Si no existen procentajes
		if( !$percents_promo ){
			my $num_pcts = scalar(@products);
			if( $num_pcts > 0 ){
				my $this_pct = (100 / $num_pcts);
				my $this_pct_add = (100 % $num_pcts);
				foreach my $i (0 .. $#products){
					$this_pct = ($this_pct + $this_pct_add) if( $i == 0 );
					$percents_promo .= $this_pct.'|';
				}
				$percents_promo = substr($percents_promo, 0, length($percents_promo)-1);
			}
		}

		my @percents = split(/\|/,$percents_promo);

		if( scalar(@percents) == scalar(@products) ){

			### Preparacion del origen de venta
			my $id_salesorigins = int($in{'id_salesorigins'});

			### Se obtiene el precio total de la promo
			$sql = "SELECT sl_products_prices.Price 
					FROM sl_products_prices
					WHERE 1 
						AND sl_products_prices.ID_products_prices=".$in{'id_prod_prices'}."
						/*AND sl_products_prices.PayType='".$in{'pay_type'}."'
						AND sl_products_prices.Origins LIKE '%|".$id_salesorigins."|%'*/;";
			my $sth_price = &Do_SQL($sql);
			my $price_total = $sth_price->fetchrow();
			if( $price_total > 0 ){
				foreach my $i (0 .. $#products){
					$sql = "SELECT sl_products.Model, sl_skus.ID_sku_products 
							FROM sl_products 
								INNER JOIN sl_skus ON sl_products.ID_products = sl_skus.ID_products
							WHERE sl_products.ID_products=".$products[$i].";";
					my $sth_prod = &Do_SQL($sql);
					my $data_prod = $sth_prod->fetchrow_hashref();

					$json_data{'products'}{$i}{'model'} = $data_prod->{'Model'};
					$json_data{'products'}{$i}{'id_sku_prod'} = ($sku_products[$i]) ? $sku_products[$i] : $data_prod->{'ID_sku_products'};
					my $this_price = ($percents[$i] > 0) ? round($price_total * ($percents[$i] / 100), 2) : 0;
					$json_data{'products'}{$i}{'price'} = $this_price;
				}
			}

			$json_data{'result'} = 'OK';
			$json_data{'matches'} = scalar(@percents);

		}else{
			$json_data{'result'} = 'ERROR';
			$json_data{'error'} = 'No coinciden los productos con los porcentajes';
		}

	# }else{
	# 	$json_data{'result'} = 'ERROR';
	# 	$json_data{'error'} = 'No existen porcentajes para esta promocion';
	# }

	print "Content-type: application/json\n\n";
	print encode_json(\%json_data);
}

#############################################################################
#############################################################################
# Function: sales_search_customers
#
# Es: Realiza la búsqueda de clientes por núm. telfónico o nombre y apellidos
# En: 
#
# Created on: 20/02/2016 
#
# Author: Ing. Gilberto Quirino
#
# Modifications:
#
# Parameters:
#
#
# Returns:
#
#
# See Also:
#
#
sub sales_search_customers{
#############################################################################
#############################################################################

	use JSON;

	my %json_data;
	my $sql = '';

	my $sql_phone = '';
	my $sql_name = '';	
	my $sql_orders_inner = '';	
	if( $in{'phone'} and $in{'phone'} ne '' ){
		my $phone = &filter_values($in{'phone'});
		$sql_phone = " AND (sl_customers.Phone1 LIKE '".$phone."%'
						OR sl_customers.Phone2 LIKE '".$phone."%'
						OR sl_customers.Cellphone LIKE '".$phone."%') ";
	}
	$in{'firstname'} = &filter_text_match($in{'firstname'});
	$sql_name = " AND MATCH(FirstName) AGAINST('*".&filter_values($in{'firstname'})."*' IN BOOLEAN MODE) " if( $in{'firstname'} and $in{'firstname'} ne '' );
	$in{'lastname1'} = &filter_text_match($in{'lastname1'});
	$sql_name .= " AND MATCH(LastName1) AGAINST('*".&filter_values($in{'lastname1'})."*' IN BOOLEAN MODE) " if( $in{'lastname1'} and $in{'lastname1'} ne '' );
	$in{'lastname2'} = &filter_text_match($in{'lastname2'});
	$sql_name .= " AND MATCH(LastName2) AGAINST('*".&filter_values($in{'lastname2'})."*' IN BOOLEAN MODE) " if( $in{'lastname2'} and $in{'lastname2'} ne '' );
	$sql_name .= " AND Zip = '".&filter_values($in{'zipcode'})."' " if( $in{'zipcode'} and $in{'zipcode'} ne '' );	
	$sql_name .= " AND sl_customers.ID_customers = '".int($in{'id_customers'})."' " if( $in{'id_customers'} and $in{'id_customers'} ne '' );	
	$sql_orders_inner = " INNER JOIN sl_orders ON sl_customers.ID_customers = sl_orders.ID_customers AND sl_orders.ID_orders = ".int($in{'id_orders'})." " if( $in{'id_orders'} and $in{'id_orders'} ne '' );	

	$sql = "SELECT * 
			FROM(
				SELECT sl_customers.ID_customers
					, sl_customers.FirstName
					, sl_customers.LastName1
					, sl_customers.LastName2
					, sl_customers.Zip
					, sl_customers.State
					, sl_customers.City
					, sl_customers.Urbanization
					, sl_customers.Address1
					, sl_customers.Phone1
					, sl_customers.Phone2
					, sl_customers.Cellphone
					, sl_customers.`Status`
				FROM sl_customers
					$sql_orders_inner
				WHERE 1					
					$sql_phone 	
				# GROUP BY sl_customers.ID_customers	
			) sl_customers
			WHERE 1
				AND `Status` = 'Active' 
				$sql_name
			ORDER BY FirstName, LastName1, LastName2, ID_customers
			LIMIT 100;";
	my $sth = &Do_SQL($sql);
	my $i = 0;
	while( my $rec = $sth->fetchrow_hashref() ){
		### Se valida que el número telefónico no esté en la lista negra
		my ($rslt_blacklist, $type) = &sales_phone_blacklist($rec->{'ID_customers'}, '');
		$json_data{'items'}{$i}{'valid_phone'}	= ( $rslt_blacklist != 0 ) ? 'No' : 'Yes';
		$json_data{'items'}{$i}{'valid_phone_type'} = $type;

		$json_data{'items'}{$i}{'id_customers'}	= $rec->{'ID_customers'};
		$json_data{'items'}{$i}{'firstname'}	= $rec->{'FirstName'};
		$json_data{'items'}{$i}{'lastname1'}	= $rec->{'LastName1'};
		$json_data{'items'}{$i}{'lastname2'}	= $rec->{'LastName2'};
		$json_data{'items'}{$i}{'zipcode'}		= $rec->{'Zip'};
		$json_data{'items'}{$i}{'state'}		= $rec->{'State'};
		$json_data{'items'}{$i}{'city'}			= $rec->{'City'};
		$json_data{'items'}{$i}{'urbanization'}	= $rec->{'Urbanization'};
		$json_data{'items'}{$i}{'address1'}		= $rec->{'Address1'};
		$json_data{'items'}{$i}{'phone1'}		= $rec->{'Phone1'};
		$json_data{'items'}{$i}{'phone2'}		= $rec->{'Phone2'};
		$json_data{'items'}{$i}{'cellphone'}	= $rec->{'Cellphone'};
		### Se determina con cual de los números telefónicos coincidió
		if( $rec->{'Phone1'} =~ /$phone/ ){
			$json_data{'items'}{$i}{'thisphone'}= $rec->{'Phone1'};
		}elsif( $rec->{'Phone2'} =~ /$phone/ ){
			$json_data{'items'}{$i}{'thisphone'}= $rec->{'Phone2'};
		}elsif( $rec->{'Cellphone'} =~ /$phone/ ){
			$json_data{'items'}{$i}{'thisphone'}= $rec->{'Cellphone'};
		}
		
		### Se obtienen los datos de su ultima compra
		my $sql_ord = "SELECT sl_orders.ID_orders, sl_orders.Date, sl_orders.`Status`
						FROM sl_orders
						WHERE sl_orders.ID_customers = ".$rec->{'ID_customers'}." 
							AND sl_orders.`Status` != 'System Error'
						ORDER BY sl_orders.Date DESC, sl_orders.ID_orders DESC
						LIMIT 5;";
		my $sth_ord = &Do_SQL($sql_ord);
		my $ord_idx = 0;
		while( $rec_ord = $sth_ord->fetchrow_hashref() ){
			$json_data{'items'}{$i}{'orders'}{$ord_idx}{'id_order'}	= $rec_ord->{'ID_orders'};
			$json_data{'items'}{$i}{'orders'}{$ord_idx}{'date'}		= $rec_ord->{'Date'};
			$json_data{'items'}{$i}{'orders'}{$ord_idx}{'status'}	= $rec_ord->{'Status'};

			$ord_idx++;
		}
		$json_data{'items'}{$i}{'orders_matches'} = $ord_idx;
		$json_data{'items'}{$i}{'last_id_order'}	= $json_data{'items'}{$i}{'orders'}{0}{'id_order'};
		$json_data{'items'}{$i}{'last_date_order'}	= $json_data{'items'}{$i}{'orders'}{0}{'date'};
		$json_data{'items'}{$i}{'last_status_order'}= $json_data{'items'}{$i}{'orders'}{0}{'status'};

		$i++;
	}
	$json_data{'matches'} = $i;

	### Si no hubo coincidencia con ningún cliente, se valida unicamente el núm. telefónico
	if( $i == 0 and ($in{'phone'} and $in{'phone'} ne '') ){
		my ($rslt_blacklist, $type) = &sales_phone_blacklist(0, $in{'phone'});
		$json_data{'valid_phone'} = ( $rslt_blacklist != 0 ) ? 'No' : 'Yes';
		$json_data{'valid_phone_type'} = $type;
	}
	
	print "Content-type: application/json\n\n";
	print encode_json(\%json_data);
}

#############################################################################
#############################################################################
# Function: sales_search_zipcodes
#
# Es: Realiza la búsqueda de códigos postales por Estado y municipio
# En: 
#
# Created on: 22/02/2016 
#
# Author: Ing. Gilberto Quirino
#
# Modifications:
#
# Parameters:
#
#
# Returns:
#
#
# See Also:
#
#
sub sales_search_zipcodes{
#############################################################################
#############################################################################
	
	use utf8;
	use JSON;

	my %json_data;
	
	my $where = '1';
	$json_data{'zipcode_valid'} = 1;
	if( $in{'zipcode'} and int($in{'zipcode'}) > 0 ){
		if( $in{'zipcode'} !~ /\D/ ){
			$where = "ZipCode = '".$in{'zipcode'} ."'";
		} else {
			$json_data{'zipcode_valid'} = 0;
		}
	}elsif( $in{'state'} ){
		$where = "StateFullName = '".&filter_values($in{'state'})."' AND City = '".&filter_values($in{'city'})."'";
	}

	if( $json_data{'zipcode_valid'} == 1 ){
		my $sql_add = ($in{'urbanization'}) ? " AND CountyName LIKE '%".&filter_values($in{'urbanization'})."%'" : "";
		my $sql = "SELECT UPPER(sl_zipcodes.StateFullName) AS StateFullName
						, UPPER(sl_zipcodes.City) AS City
						, UPPER(sl_zipcodes.CountyName) AS CountyName
						, sl_zipcodes.ZipCode
						, sl_zones.ExpressShipping
					FROM sl_zipcodes
						LEFT JOIN sl_zones ON sl_zipcodes.ID_zones = sl_zones.ID_zones
					WHERE  
						$where 
						$sql_add
					ORDER BY StateFullName, City, ZipCode, CountyName;";
		&Do_SQL("SET CHARACTER SET utf8;");
		my $sth = &Do_SQL($sql);

		my $i = 0;
		while( my $rec = $sth->fetchrow_hashref() ){
			$json_data{'items'}{$i}{'state'}		= decode("utf-8", $rec->{'StateFullName'});
			$json_data{'items'}{$i}{'city'}			= decode("utf-8", $rec->{'City'});
			$json_data{'items'}{$i}{'urbanization'}	= decode("utf-8", $rec->{'CountyName'});
			$json_data{'items'}{$i}{'zipcode'}		= $rec->{'ZipCode'};
			$json_data{'items'}{$i}{'express_delivery'}	= $rec->{'ExpressShipping'};

			$i++;
		}
		$json_data{'matches'} = $i;
	} else {
		$json_data{'matches'} = 0;
	}

	###-------------------------------------
	### Se valida la disponibilidad de los productos del carrito de compras
	### con el código postal encontrado(si solo hubo una coincidencia)
	###------------------------------------- 
	if( $in{'products'} and $in{'products'} ne '' and $json_data{'matches'} == 1 ){
		my $results = &sales_chgzipcode_products_available($in{'zipcode'}, $in{'pay_type'}, $in{'products'});

		$json_data{'available'} = $results->{'available'};
		$json_data{'express_delivery'} = $results->{'express_delivery'};

		if( $json_data{'available'} eq 'Some' ){
			my $rslt_prod = $results->{'products'};
			while( ($key, $value) = each $rslt_prod ){
				$json_data{'products_list'}{$key}{'id_products'} = $value->{'id_products'};
				$json_data{'products_list'}{$key}{'model'} = $value->{'model'};
				$json_data{'products_list'}{$key}{'available'} = $value->{'available'};
			}
		}
	}
	
	print "Content-type: application/json\n\n";
	print encode_json(\%json_data);

}

#############################################################################
#############################################################################
# Function: sales_zipcode_products_available
#
# Es: Mediante una llamada Ajax, verifica la disponiblidad de los productos agregados al carrito de compras
# En: 
#
# Created on: 21/04/2016 
#
# Author: Ing. Gilberto Quirino
#
# Modifications:
#
# Parameters:
#
#
# Returns:
#
#
# See Also:
#
#
sub sales_zipcode_products_available{
#############################################################################
#############################################################################
	
	use JSON;
	my %json_data;

	###-------------------------------------
	### Se valida la disponibilidad de los productos del carrito de compras
	### con el código postal encontrado(si solo hubo una coincidencia)
	###------------------------------------- 
	if( $in{'products'} and $in{'products'} ne '' ){
		my $results = &sales_chgzipcode_products_available($in{'zipcode'}, $in{'pay_type'}, $in{'products'});

		$json_data{'available'} = $results->{'available'};
		$json_data{'express_delivery'} = $results->{'express_delivery'};

		if( $json_data{'available'} eq 'Some' ){
			my $rslt_prod = $results->{'products'};
			while( ($key, $value) = each $rslt_prod ){
				$json_data{'products_list'}{$key}{'id_products'} = $value->{'id_products'};
				$json_data{'products_list'}{$key}{'model'} = $value->{'model'};
				$json_data{'products_list'}{$key}{'available'} = $value->{'available'};
			}
		}
	}
	
	print "Content-type: application/json\n\n";
	print encode_json(\%json_data);
}

#############################################################################
#############################################################################
# Function: sales_chgzipcode_products_available
#
# Es: Verifica la disponiblidad de los productos agregados al carrito de compras, cuando es moficado el código postal
# En: 
#
# Created on: 15/04/2016 
#
# Author: Ing. Gilberto Quirino
#
# Modifications:
#
# Parameters:
#
#
# Returns:
#
#
# See Also:
#
#
sub sales_chgzipcode_products_available{
#############################################################################
#############################################################################
	
	my ($zipcode, $pay_type, $products) = @_;
	my %results;

	### Se obtienen los datos necesario de la zona en base al zipcode proporcionado
	$va{'pay_type_available'} = '';	
	if( $zipcode > 0 ){
		$sql = "SELECT 
					sl_zones.Name
					, sl_zones.Payment_Type
					, sl_zones.ExpressShipping
				FROM sl_zipcodes
					INNER JOIN sl_zones ON sl_zipcodes.ID_zones = sl_zones.ID_zones
				WHERE 1
					AND sl_zipcodes.ZipCode='".$zipcode."' 
					AND sl_zipcodes.`Status` = 'Active' 
					AND sl_zones.`Status` = 'Active';";
		my $sth_zone = &Do_SQL($sql);
		my $data_zone = $sth_zone->fetchrow_hashref();

		$va{'pay_type_available'}	= $data_zone->{'Payment_Type'};
		$va{'zones_express_delivery'}	= $data_zone->{'ExpressShipping'};

		$results{'express_delivery'} = $va{'zones_express_delivery'};
	}


	### Se comparan las formas de pago disponibles para la nueva zona
	### con la forma de pago seleccionada previamente
	if( $va{'pay_type_available'} =~ /$pay_type/ ){
		### Preparacion de las formas de pago
		$va{'pay_type_available'} =~ s/\,/\'\,\'/g;

		### Si la forma de pago seleccionada está dentro de los disponibles para la nueva zona,
		### entonces se comparan los precios
		$chk_rslt = 'All';
		my @this_products = split(/\,/, $products);
		foreach my $i (0 .. $#this_products){
			my @this_info = split(/:/, $this_products[$i]);

			if( $this_info[0] =~ /^1/ ){
				$results{'products'}{$i}{'id_products'} = $this_info[0];
				$results{'products'}{$i}{'model'} = 'Servicio '.$this_info[0];
				$results{'products'}{$i}{'available'} = 'Yes';				
			}else{
				my $sql = "SELECT sl_products.Model, ID_products_prices 
							FROM sl_products
								LEFT JOIN (
									SELECT ID_products, ID_products_prices 
									FROM sl_products_prices 
									WHERE ID_products_prices = ".$this_info[1]." 
										AND sl_products_prices.PayType IN('".$va{'pay_type_available'}."')
								)sl_products_prices ON sl_products.ID_products = sl_products_prices.ID_products
							WHERE sl_products.ID_products = ".$this_info[0].";";
				my $sth = &Do_SQL($sql);
				my ($model, $id_price) = $sth->fetchrow();
				$results{'products'}{$i}{'id_products'} = $this_info[0];
				$results{'products'}{$i}{'model'} = $model;

				if( int($id_price) > 0 ){
					$results{'products'}{$i}{'available'} = 'Yes';
				}else{
					$results{'products'}{$i}{'available'} = 'No';
					$chk_rslt = 'Some';
				}
			}
		}
		$results{'available'} = $chk_rslt;

	}else{
		### Esto quiere decir que ningún producto está disponible del carrito de compras
		### está disponible para la nueva zona
		$results{'available'} = 'None';
	}

	return \%results;
}

#############################################################################
#############################################################################
# Function: sales_build_select_zipcodes_city
#
# Es: Obtiene los municipios de un estado seleccionado en la búsqueda de códigos postales
# En: 
#
# Created on: 22/04/2016 
#
# Author: Ing. Gilberto Quirino
#
# Modifications:
#
# Parameters:
#
#
# Returns:
#
#
# See Also:
#
#
sub sales_build_select_zipcodes_city{
#############################################################################
#############################################################################

	use JSON;

	my %json_data;
	my $sql = "SELECT City
				FROM sl_zipcodes
				WHERE StateFullName = '".&filter_values($in{'state'})."' AND City != '' AND City IS NOT NULL
				GROUP BY City
				ORDER BY City;";
	&Do_SQL("SET CHARACTER SET utf8;");
	my $sth = &Do_SQL($sql);

	my $i = 0;
	while( my $rec = $sth->fetchrow_hashref() ){		
		$json_data{'items'}{$i}{'city'} = decode("utf-8", $rec->{'City'});

		$i++;
	}
	$json_data{'matches'} = $i;

	print "Content-type: application/json\n\n";
	print encode_json(\%json_data);

}


#############################################################################
#############################################################################
# Function: sales_info_coupon
#
# Es: Valida la vigencia y obtiene los datos de un cupón de descuento
# En: 
#
# Created on: 15/03/2016 
#
# Author: Ing. Gilberto Quirino
#
# Modifications:
#
# Parameters:
#
#
# Returns:
#
#
# See Also:
#
#
sub sales_info_coupon{
#############################################################################
#############################################################################
	use JSON;

	my $sth=&Do_SQL("SELECT sl_coupons.*
						, IF(sl_coupons.`Status` = 'Active' AND (CURDATE() BETWEEN sl_coupons.ValidFrom AND sl_coupons.ValidTo), 'Valid', 'Invalid') AS CouponStatus
					 FROM sl_coupons 
					 WHERE PublicID ='".&filter_values($in{'coupon'})."';");
	my $rec = $sth->fetchrow_hashref;

	my %json_data;
	if($rec->{'Name'}){
		$va{'name'}				= $rec->{'Name'};
		$va{'public_id'}		= $rec->{'PublicID'};
		$va{'public_id'}		= '*'x(length($va{'public_id'}) - 2).substr($va{'public_id'}, -2) if( $cfg{'coupon_hide'} and $cfg{'coupon_hide'} == 1 );
		$va{'company'} 			= $rec->{'Type'};
		$va{'applied'}			= $rec->{'Applied'};
		$va{'validfrom'}		= $rec->{'ValidFrom'};
		$va{'validto'} 			= $rec->{'ValidTo'};
		$va{'discount'} 		= ($rec->{'DiscPerc'}) ?  $rec->{'DiscPerc'}.'%' : &format_price($rec->{'DiscValue'});
		$va{'max_per_cust'} 	= $rec->{'MaxPerCust'};
		$va{'max_per_zip'} 		= $rec->{'MaxPerZip'};
		$va{'max_per_state'}	= $rec->{'MaxPerState'};
		$va{'min_amount'} 		= $rec->{'MinAmount'};

		$json_data{'result'}		= 'OK';
		$json_data{'id_coupon'}		= $rec->{'ID_coupons'};
		$json_data{'status'}		= $rec->{'CouponStatus'};
		$json_data{'applied'}		= $va{'applied'};
		$json_data{'discount'}		= ($rec->{'DiscPerc'}) ?  $rec->{'DiscPerc'} : $rec->{'DiscValue'};
		$json_data{'discount_type'}	= ($rec->{'DiscPerc'}) ? '%' : '$';
		$json_data{'min_amount'}	= $va{'min_amount'};
		if( $rec->{'CouponStatus'} eq 'Valid' ){
			$va{'status'} = '<span style="color: green; font-size: 12pt; font-weight: bold;">Valid</span>';
		}else{
			$va{'status'} = '<span style="color: red; font-size: 12pt; font-weight: bold;">Not Applicable</span>';
		}

		$json_data{'html'} = &build_page("info_coupon.html");
	}else{
		$json_data{'result'} = 'ERROR';
		$json_data{'html'} = '<span class="smallfieldterr" style="margin: auto auto; position: relative;">Invalid or missing coupon</span>';
	}


	print "Content-type: text/json\n\n";
	print encode_json(\%json_data);

}

#############################################################################
#############################################################################
# Function: sales_search_services
#
# Es: Genera el listado de servicios disponibles
# En: 
#
# Created on: 16/03/2016 
#
# Author: Ing. Gilberto Quirino
#
# Modifications:
#
# Parameters:
#
#
# Returns:
#
#
# See Also:
#
#
sub sales_search_services{
#############################################################################
#############################################################################
	
	use utf8;
	use JSON;

	my %json_data;
	
	my $where = '1';
	
	my $sql = "SELECT ID_services, Name, Description, SPrice, ServiceType, Tax
				FROM sl_services
				WHERE Status = 'Active'	
				ORDER BY ID_services;";
	&Do_SQL("SET CHARACTER SET utf8;");
	my $sth = &Do_SQL($sql);

	my $i = 0;
	while( my $rec = $sth->fetchrow_hashref() ){
		$json_data{'items'}{$i}{'id_services'}	= $rec->{'ID_services'};
		$json_data{'items'}{$i}{'fid_services'}	= &format_sltvid('60000'.$rec->{'ID_services'});
		$json_data{'items'}{$i}{'name'}			= decode("utf-8", $rec->{'Name'});
		$json_data{'items'}{$i}{'description'}	= decode("utf-8", $rec->{'Description'});
		$json_data{'items'}{$i}{'price'}		= round($rec->{'SPrice'}, 2);
		$json_data{'items'}{$i}{'type'}			= $rec->{'ServiceType'};
		$json_data{'items'}{$i}{'tax_pct'}		= ( $rec->{'Tax'} > 1 ) ? round($rec->{'Tax'} / 100, 2) : round($rec->{'Tax'}, 2);

		$i++;
	}
	$json_data{'matches'} = $i;
	
	print "Content-type: application/json\n\n";
	print encode_json(\%json_data);

}

#############################################################################
#############################################################################
# Function: sales_product_info
#
# Es: Genera el html para info detallada de cada producto
# En: 
#
# Created on: 09/05/2016 
#
# Author: Ing. Gilberto Quirino
#
# Modifications:
#
# Parameters:
#
#
# Returns:
#
#
# See Also:
#
#
sub sales_product_info{
#############################################################################
#############################################################################
	
	if( $in{'id_product'} ){

		### Si es un promo
		my $this_id_product = '';
		if( int($in{'promo'}) == 1 ){
			my $sql = "SELECT VValue
						FROM sl_vars
						WHERE VName='promo".int($in{'id_product'})."';";
			my $sth = &Do_SQL($sql);

			my $this_products = $sth->fetchrow();
			my @products = split(/\|/,$this_products);
			foreach my $i (0 .. $#products){
				if(int($products[$i]) > 0){
					$this_id_product = $products[$i];
					last;
				}
			}
		}else{
			$this_id_product = $in{'id_product'};
		}

		my $sth = &Do_SQL("SELECT Description1,  Description2,  Description3,  Description4 
							FROM cu_skus_descriptions 
								INNER JOIN sl_skus_parts ON sl_skus_parts.ID_parts = cu_skus_descriptions.ID_parts
							WHERE RIGHT(sl_skus_parts.ID_sku_products, 6) = ".$this_id_product.";");
		while( my $rec = $sth->fetchrow_hashref ){
			$in{'description1'} = $rec->{'Description1'};
			$in{'description2'} = $rec->{'Description2'};
			$in{'description3'} = $rec->{'Description3'};
			$in{'description4'} = $rec->{'Description4'};
		}
	}

	print "Content-type: text/html\n\n";
	print &build_page("ajaxbuild:product_info.html");

}


#############################################################################
#############################################################################
# Function: sales_zones_delivery
#
# Es: Genera el html de la tabla con los tiempo de entrega
# En: 
#
# Created on: 17/05/2016 
#
# Author: Ing. Gilberto Quirino
#
# Modifications:
#
# Parameters:
#
#
# Returns:
#
#
# See Also:
#
#
sub sales_zones_delivery{
#############################################################################
#############################################################################

	########
	######## Metodos de pago aceptados
	########					
	my ($sth) = &Do_SQL("SELECT ID_zones
							, Name
							, Payment_Type
							, ExpressShipping 
						FROM sl_zones 
							INNER JOIN sl_zipcodes USING(ID_zones) 
						WHERE ZipCode = '".$in{'zipcode'}."';");
	my $rec_zone = $sth->fetchrow_hashref();

	### Se valida si los productos están diponibles para envío express
	if( $in{'products'} and $in{'products'} ne '' and $in{'pay_type'} ne 'Referenced Deposit' ){

		### Si el envio express está disponible para la zona<->código postal
		if( $rec_zone->{'ExpressShipping'} eq 'Yes' ){
			### Se valida que todos los productos de la orden tengan envío express
			my $products = '';
			my @products_info = split(/\,/, substr($in{'products'}, 0, -1));
			foreach my $i (0 .. $#products_info){
				my @this_info = split(/\:/,$products_info[$i]);
				$products .= $this_info[0].',';
			}
			$products = substr($products, 0, -1);

			my $sql = "SELECT ExpressShipping
						FROM sl_products							
						WHERE ID_products IN(".$products.");";
			my $sth = &Do_SQL($sql);
			my $express = 'Yes';
			while( my $rec = $sth->fetchrow_hashref() ){
				if( uc($rec->{'ExpressShipping'}) eq 'NO' ){
					$express = 'No';
					last;
				}
			}
			$va{'prod_express_delivery'} = $express;

		}else{
			$va{'prod_express_delivery'} = 'No';
		}		

	}else{
		$va{'prod_express_delivery'} = 'No';	
	}

	$va{'paytype_accepted'} = '';
	$va{'zone_name'} = '';
	$va{'warehouses_zone'} = '';
	$va{'express_allowed'} = ($cfg{'express_delivery'} and $va{'prod_express_delivery'} eq 'Yes' and $rec_zone->{'ExpressShipping'} eq 'Yes') ? '' : 'delivery_types_off';

	if($rec_zone->{'Payment_Type'} ne ''){

		$va{'zone_name'} = $rec_zone->{'Name'};
		my @ary = split(/,/, $rec_zone->{'Payment_Type'});
		for(0..$#ary){

			if($_ == 0){
				$va{'paytype_accepted'} .= qq|<tr>\n|;
			}elsif($_ % 3 == 0){
				$va{'paytype_accepted'} .= qq|</tr>\n<tr>\n|;
			}

			$va{'paytype_accepted'} .= qq|<td style="height:60px;width:100px;background:#F39814;color:#FFFFFF;text-align:center;font-size:1.2em" align="center">$ary[$_]</td>|;

		}

		my $x = 0;
		my ($sth1) = &Do_SQL("SELECT Name FROM sl_warehouses INNER JOIN sl_zones_warehouses USING(ID_warehouses) WHERE ID_zones = '".$rec_zone->{'ID_zones'}."';");
		while( my($wn) = $sth1->fetchrow()) {

			if($x == 0){
				$va{'warehouses_zone'} .= qq|<tr>\n|;
			}elsif($x % 3 == 0){
				$va{'warehouses_zone'} .= qq|</tr>\n<tr>\n|;
			}

			$va{'warehouses_zone'} .= qq|<td style="height:60px;width:100px;background:#F39814;color:#FFFFFF;text-align:center;font-size:1.2em" align="center">$wn</td>|;
			$x++;
		}
		(!$x) and (qq|<td style="height:60px;width:300px;background:#F39814;color:#FFFFFF" align="center">|.&trans_txt('search_nomatches').qq|</td>|);

	}else{

		$va{'paytype_accepted'} .= qq|<td style="height:60px;width:300px;background:#F39814;color:#FFFFFF" align="center">|.&trans_txt('search_nomatches').qq|</td>|;
		$va{'warehouses_zone'} .= qq|<td style="height:60px;width:300px;background:#F39814;color:#FFFFFF" align="center">|.&trans_txt('search_nomatches').qq|</td>|;

	}

	print "Content-type: text/html\n\n";
	print &build_page("sales_show_zones_delivery.html");
}

#############################################################################
#############################################################################
# Function: sales_valid_phone
#
# Es: Verifica si un número telefónico está en el blacklist
# En: 
#
# Created on: 01/08/2016 
#
# Author: Ing. Gilberto Quirino
#
# Modifications:
#
# Parameters:
#
#
# Returns:
#
#
# See Also:
#
#
sub sales_valid_phone{
#############################################################################
#############################################################################
	use utf8;
	use JSON;

	my %json_data;

	### Phone
	my ($rslt_blacklist, $type) = &sales_phone_blacklist(0, $in{'phone'});
	$json_data{'valid_phone'} = ( $rslt_blacklist != 0 ) ? 'No' : 'Yes';
	$json_data{'valid_phone_type'} = $type;
	### Cellphone
	my ($rslt_blacklist, $type) = &sales_phone_blacklist(0, $in{'cellphone'});
	$json_data{'valid_cellphone'} = ( $rslt_blacklist != 0 ) ? 'No' : 'Yes';
	$json_data{'valid_cellphone_type'} = $type;
	### Phone2
	$json_data{'valid_phone2'} = 'Yes';
	if( $in{'phone2'} != '' ){
		my ($rslt_blacklist, $type) = &sales_phone_blacklist(0, $in{'phone2'});
		$json_data{'valid_phone2'} = ( $rslt_blacklist != 0 ) ? 'No' : 'Yes';
		$json_data{'valid_phone2_type'} = $type;
	}

	print "Content-type: application/json\n\n";
	print encode_json(\%json_data);
}

#############################################################################
#############################################################################
# Function: sales_phone_blacklist
#
# Es: Valida los números telefónicos de un cliente en el blacklist
# En: 
#
# Created on: 01/08/2016 
#
# Author: Ing. Gilberto Quirino
#
# Modifications:
#
# Parameters:
#
#
# Returns:
#
#
# See Also:
#
#
sub sales_phone_blacklist{
#############################################################################
#############################################################################
	
	my ($id_customers, $phone) = @_;

	my @result = {};
	
	if( !$cfg{'check_phone_blacklist'} or int($cfg{'check_phone_blacklist'}) == 0 ){
		$result{0} = '1';
		$result{1} = 'None';

		return @$result;
	}

	my $sql = "";

	if( int($id_customers) > 0 ){
		$sql = "SELECT COUNT(*) Invalid, cu_phone_blacklist.`Type`
				FROM sl_customers
					INNER JOIN cu_phone_blacklist ON
						sl_customers.CID = cu_phone_blacklist.Phone 
						OR sl_customers.Phone1 = cu_phone_blacklist.Phone 
						OR sl_customers.Phone2 = cu_phone_blacklist.Phone 
						OR sl_customers.Cellphone = cu_phone_blacklist.Phone
				WHERE sl_customers.ID_customers = ".int($id_customers)." 
					AND cu_phone_blacklist.`Status` = 'Active';";
	}elsif( $phone ){
		$sql = "SELECT COUNT(*) Invalid, `Type`
				FROM cu_phone_blacklist
				WHERE Phone = '".&filter_values($phone)."'
					AND `Status` = 'Active';";
	}

	if( $sql ne '' ){
		my $sth = &Do_SQL($sql);
		@result = $sth->fetchrow_array();
	}

	return @result;
}

#############################################################################
#############################################################################
# Function: sales_validate_folio
#
# Es: Verifica si un folio de promoción es válido
# En: 
#
# Created on: 01/08/2016 
#
# Author: Ing. Gilberto Quirino
#
# Modifications:
#
# Parameters:
#
#
# Returns:
#
#
# See Also:
#
#
sub sales_validate_folio{
#############################################################################
#############################################################################
	use utf8;
	use JSON;

	my %json_data;

	my $sql_customers = ( int($in{'id_customers'}) > 0 ) ? " AND cu_customer_promotions.ID_customers = ".int($in{'id_customers'}) : "";
	my $sql_step_info = ( int($in{'step'}) == 6 ) ? "OR 1" : "";
	my $sql = "SELECT cu_customer_promotions.ID_customers
					, cu_promotions.*
					, sl_customers.FirstName
					, sl_customers.LastName1
					, sl_customers.LastName2
					, sl_customers.Phone1
					, sl_customers.Zip
					, sl_customers.Address1
					, sl_customers.Urbanization
					, sl_customers.City
					, sl_customers.State
				FROM cu_promotions
					INNER JOIN cu_customer_promotions ON cu_promotions.ID_promotions = cu_customer_promotions.ID_promotions
					INNER JOIN sl_customers ON cu_customer_promotions.ID_customers = sl_customers.ID_customers
				WHERE cu_customer_promotions.Unique_code = '".&filter_values($in{'folio'})."' 
					AND (cu_customer_promotions.ID_orders = 0 OR cu_customer_promotions.ID_orders IS NULL ".$sql_step_info.")
					AND NOW() >= CONCAT(cu_promotions.Valid_from_date, ' ', cu_promotions.Valid_from_hour)
					AND NOW() <= CONCAT(cu_promotions.Valid_to_date, ' ', cu_promotions.Valid_to_hour)
					".$sql_customers.";";
	my $sth = &Do_SQL($sql);
	my $promo = $sth->fetchrow_hashref();

	if( int($promo->{'ID_promotions'}) > 0 ){

		$json_data{'result'} = 'true';
		$json_data{'id_promotions'} = $promo->{'ID_promotions'};
		$json_data{'id_customers'} = $promo->{'ID_customers'};

		$va{'promo_name'} = $promo->{'Name'};
		$va{'promo_validfrom'} = $promo->{'Valid_from_date'};
		$va{'promo_validto'} = $promo->{'Valid_to_date'};

		### Obtiene los detalles de la promoción
		my $sth_rules = &Do_SQL("SELECT * FROM cu_promotion_rules WHERE ID_promotions = ".$promo->{'ID_promotions'}.";");
		my $promo_rules = $sth_rules->fetchrow_hashref();

		### Lista de productos que se obsequiarán
		my %promotion;

		### Regla por tipo de pago
		if( $promo_rules->{'Ptype_flag'} ){
			if( $promo_rules->{'Ptype_ID_products'} ){
				$promotion{'ptype'}{'apply'} = '1';
				$promotion{'ptype'}{'value'} = $promo_rules->{'Ptype_flag'};

				$va{'promo_ptype'} = $promo_rules->{'Ptype_flag'};

				my $sql_prod = "SELECT ID_products, Model FROM sl_products WHERE ID_products IN(".$promo_rules->{'Ptype_ID_products'}.") AND `Status` = 'On-Air';";
				my $sth_prod = &Do_SQL($sql_prod);
				my $i = 0;
				while( my $prod = $sth_prod->fetchrow_hashref() ){
					$promotion{'ptype'}{'products'}{$i} = $prod->{'ID_products'};

					$va{'promo_ptype_products'} .= $prod->{'ID_products'}.': '.$prod->{'Model'}.'<br />';
					$i++;
				}
			}
		} else {
			$va{'promo_ptype'} = 'No Apply';
		}

		### Regla por la compra de un producto de catálogo
		if( $promo_rules->{'Catalog_flag'} ){
			if( $promo_rules->{'Catalog_ID_products'} ){
				$promotion{'catalog'}{'apply'} = '1';
				$promotion{'catalog'}{'value'} = '1';

				$va{'promo_catalog'} = 'Apply';

				my $sql_prod = "SELECT ID_products, Model FROM sl_products WHERE ID_products IN(".$promo_rules->{'Catalog_ID_products'}.") AND `Status` = 'On-Air';";
				my $sth_prod = &Do_SQL($sql_prod);
				my $i = 0;
				while( my $prod = $sth_prod->fetchrow_hashref() ){
					$promotion{'catalog'}{'products'}{$i} = $prod->{'ID_products'};

					$va{'promo_catalog_products'} .= $prod->{'ID_products'}.': '.$prod->{'Model'}.'<br />';
					$i++;
				}
			}
		} else {
			$va{'promo_catalog'} = 'No Apply';
		}

		### Regla por monto mínimo
		if( $promo_rules->{'Min_amount_flag'} ){
			if( $promo_rules->{'Min_amount_ID_products'} ){
				$promotion{'min_amount'}{'apply'} = '1';
				$promotion{'min_amount'}{'value'} = $promo_rules->{'Min_amount_flag'};

				$va{'promo_min_amt'} = &format_price($promo_rules->{'Min_amount_flag'});

				my $sql_prod = "SELECT ID_products, Model FROM sl_products WHERE ID_products IN(".$promo_rules->{'Min_amount_ID_products'}.") AND `Status` = 'On-Air';";
				my $sth_prod = &Do_SQL($sql_prod);
				my $i = 0;
				while( my $prod = $sth_prod->fetchrow_hashref() ){
					$promotion{'min_amount'}{'products'}{$i} = $prod->{'ID_products'};

					$va{'promo_min_amt_products'} .= $prod->{'ID_products'}.': '.$prod->{'Model'}.'<br />';
					$i++;
				}
			}
		} else {
			$va{'promo_min_amt'} = 'No Apply';
		}

		### Regla por cada monto
		if( $promo_rules->{'Per_amount_flag'} ){
			if( $promo_rules->{'Per_amount_ID_products'} ){
				$promotion{'per_amount'}{'apply'} = '1';
				$promotion{'per_amount'}{'value'} = $promo_rules->{'Per_amount_flag'};

				$va{'promo_per_amt'} = &format_price($promo_rules->{'Per_amount_flag'});

				my $sql_prod = "SELECT ID_products, Model FROM sl_products WHERE ID_products IN(".$promo_rules->{'Per_amount_ID_products'}.") AND `Status` = 'On-Air';";
				my $sth_prod = &Do_SQL($sql_prod);
				my $i = 0;
				while( my $prod = $sth_prod->fetchrow_hashref() ){
					$promotion{'per_amount'}{'products'}{$i} = $prod->{'ID_products'};

					$va{'promo_per_amt_products'} .= $prod->{'ID_products'}.': '.$prod->{'Model'}.'<br />';
					$i++;
				}
			}
		} else {
			$va{'promo_per_amt'} = 'No Apply';
		}

		### Datos del cliente
		$json_data{'customer'}{'phone1'} = $promo->{'Phone1'};
		$json_data{'customer'}{'firstname'} = $promo->{'FirstName'};
		$json_data{'customer'}{'lastname1'} = $promo->{'LastName1'};
		$json_data{'customer'}{'lastname2'} = $promo->{'LastName2'};
		$json_data{'customer'}{'zipcode'} = $promo->{'Zip'};
		$json_data{'customer'}{'address1'} = $promo->{'Address1'};
		$json_data{'customer'}{'urbanization'} = $promo->{'Urbanization'};
		$json_data{'customer'}{'city'} = $promo->{'City'};
		$json_data{'customer'}{'state'} = $promo->{'State'};

		### Se obtienen los datos de la ultima compra del cliente relacionado con el folio
		my $sql_ord = "SELECT sl_orders.ID_orders, sl_orders.Date, sl_orders.`Status`
						FROM sl_orders
						WHERE sl_orders.ID_customers = ".$promo->{'ID_customers'}." 
							AND sl_orders.`Status` != 'System Error'
						ORDER BY sl_orders.Date DESC, sl_orders.ID_orders DESC
						LIMIT 1;";
		my $sth_ord = &Do_SQL($sql_ord);
		if( $sth_ord ){
			$json_data{'customer'}{'last_order'}{'id_orders'} = $sth_ord->{'ID_orders'};
			$json_data{'customer'}{'last_order'}{'date'} = $sth_ord->{'Date'};
			$json_data{'customer'}{'last_order'}{'status'} = $sth_ord->{'Status'};
		}


		### Se asignan los valores obtenidos de la promoción
		$json_data{'promotion'} = \%promotion;

		$json_data{'html_promo'} = &build_page("sales_info_promo.html");

	} else {

		### Se busca en las promos de MOW específicamete
		if( int($cfg{'promos_mow'}) == 1 ){
			my $sth = &Do_SQL("SELECT * 
								FROM cu_customer_promotions_mow 
								WHERE Unique_code = '".&filter_values($in{'folio'})."'
									AND (ID_orders IS NULL OR ID_orders = 0)
								LIMIT 1;");
			my $customer = $sth->fetchrow_hashref();

			if( $customer->{'FirstName'} ne '' ){
				$json_data{'result'} = 'true';
				$json_data{'promo_mow'}{'result'} = '1';
				$json_data{'promo_mow'}{'values'}{'FirstName'} = $customer->{'FirstName'};
				$json_data{'promo_mow'}{'values'}{'LastName1'} = $customer->{'LastName1'};
				$json_data{'promo_mow'}{'values'}{'LastName2'} = $customer->{'LastName2'};
				$json_data{'promo_mow'}{'values'}{'Address1'} = $customer->{'Address1'};
				$json_data{'promo_mow'}{'values'}{'Urbanization'} = $customer->{'Urbanization'};
				$json_data{'promo_mow'}{'values'}{'City'} = $customer->{'City'};
				$json_data{'promo_mow'}{'values'}{'State'} = $customer->{'State'};
				$json_data{'promo_mow'}{'values'}{'Zip'} = $customer->{'Zip'};
				$json_data{'promo_mow'}{'values'}{'ID_promotions'} = $customer->{'ID_customers_promotions'};
			} else {
				$json_data{'result'} = 'false';
				$json_data{'message'} = 'El folio proporcionado ya fue utilizado o no es v&aacute;lido.';
			}

		} else {

			$json_data{'result'} = 'false';
			my $sth = &Do_SQL("SELECT ID_orders 
								FROM cu_customer_promotions 
								WHERE Unique_code = '".&filter_values($in{'folio'})."';");
			my $promo_orders = $sth->fetchrow();
			if( int($promo_orders) > 0 ){
				$json_data{'message'} = 'El folio proporcionado ya fue utilizado';
			} else {
				$json_data{'message'} = 'El folio proporcionado no es v&aacute;lido, por favor verif&iacute;quelo.';
			}
		}
	}
	


	print "Content-type: application/json\n\n";
	print encode_json(\%json_data);
}

1;