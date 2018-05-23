#!/usr/bin/perl
####################################################################
########             PRODUCTS                 ########
####################################################################

sub load_tabsconf {
# --------------------------------------------------------
	if ($in{'tab'} eq 1){
		## Notes Tab
		$va{'tab_type'}  = 'notes';
		$va{'tab_title'} = &trans_txt('notes');
		$va{'tab_table'} = 'sl_products_notes';
	}elsif($in{'tab'} eq 11){
		## Notes Tab
		$va{'tab_type'}  = 'logs';
		$va{'tab_title'} = &trans_txt('logs');
		$va{'tab_table'} = 'sl_products';
	}
}


sub load_tabs2 {
# --------------------------------------------------------
##############################################
## tab2 : 
##############################################

	### ADD			
	if ($in{'action'} eq 'add_category'){
		if (!$in{'id_categories'}){
			$va{'message'} = &trans_txt('reqfields');
			$error{'id_categories'} = &trans_txt('required');
		}else{
			my ($sth) = &Do_SQL("SELECT COUNT(*) FROM sl_products_categories WHERE ID_products='$in{'id_products'}' AND ID_categories='$in{'id_categories'}'");
			if ($sth->fetchrow >0){
				$error{'id_categories'} = &trans_txt('repeated');
			}else{
				$va{'tabmessages_cat'} = &trans_txt('mer_products_catadded');
				my ($sth) = &Do_SQL("INSERT INTO sl_products_categories SET ID_products='$in{'id_products'}',ID_top='".&load_topparent_id($in{'id_categories'})."',ID_categories='$in{'id_categories'}',Date=Curdate(),Time=NOW(),ID_admin_users='$usr{'id_admin_users'}'");
				delete($in{'id_categories'});
				&auth_logging('mer_products_catadded',$in{'id_products'});
				$in{'tabs'} = 1;
			}
		}
	## DROP	
	}elsif ($in{'dropcat'}){
		my ($sth) = &Do_SQL("DELETE FROM sl_products_categories WHERE ID_products_categories='$in{'dropcat'}'");
		$va{'message'} = &trans_txt('mer_products_catdel');
		&auth_logging('mer_products_catdel',$in{'id_products'});
		$va{'tabmessages_cat'} = &trans_txt('mer_products_catdel');
		$in{'tabs'} = 1;
	}

	my (@c) = split(/,/,$cfg{'srcolors'});
	my ($sth) = &Do_SQL("SELECT COUNT(*) FROM sl_products_categories WHERE ID_products='$in{'id_products'}'");
	$va{'matches'} = $sth->fetchrow;
	if ($va{'matches'}>0){
		my ($sth) = &Do_SQL("SELECT * FROM sl_products_categories,sl_categories WHERE ID_products='$in{'id_products'}' AND sl_categories.ID_categories=sl_products_categories.ID_categories ORDER BY Title;");
		while ($rec = $sth->fetchrow_hashref){
			$d = 1 - $d;
			$va{'searchresults'} .= "<tr bgcolor='$c[$d]' onmouseover='m_over(this)' onmouseout='m_out(this)'>\n";
			$va{'searchresults'} .= "   <td class='smalltext'><a href='/cgi-bin/mod/$usr{'application'}/dbman?cmd=$in{'cmd'}&view=$in{'id_products'}&tab=2&dropcat=$rec->{'ID_products_categories'}'><img src='$va{'imgurl'}/$usr{'pref_style'}/b_drop.png' title='Drop' alt='' border='0'></a></td>";
			$va{'searchresults'} .= "   <td class='smalltext' onClick=\"trjump('/cgi-bin/mod/$usr{'application'}/dbman?cmd=mer_categories&view=$rec->{'ID_categories'}&tab=1')\">($rec->{'ID_categories'}) $rec->{'Title'}</td>\n";
			$va{'searchresults'} .= "</tr>\n";
		}
	}else{
		$va{'searchresults'} = qq|
			<tr>
				<td colspan='2' align="center">|.&trans_txt('search_nomatches').qq|</td>
			</tr>\n|;
	}
	### Properties		
	if ($in{'action'} eq 'add_property'){
		if (!$in{'id_properties'}){
			$va{'message'} = &trans_txt('reqfields');
			$error{'id_properties'} = &trans_txt('required');
		}else{
			my ($sth) = &Do_SQL("SELECT COUNT(*) FROM sl_products_properties WHERE ID_products='$in{'id_products'}' AND ID_properties='$in{'id_properties'}'");
			if ($sth->fetchrow >0){
				$error{'id_properties'} = &trans_txt('repeated');
			}else{
				$va{'tabmessages_pro'} = &trans_txt('mer_products_propadded');
				my ($sth) = &Do_SQL("INSERT INTO sl_products_properties SET ID_products='$in{'id_products'}',ID_properties='$in{'id_properties'}',Date=Curdate(),Time=NOW(),ID_admin_users='$usr{'id_admin_users'}'");
				delete($in{'id_properties'});
				&auth_logging('mer_products_propadded',$in{'id_products'});
				$va{'message'} = &trans_txt('mer_products_propadded');
				$in{'tabs'} = 1;
			}
		}
	}elsif ($in{'dropprop'}){
		my ($sth) = &Do_SQL("DELETE FROM sl_products_properties WHERE ID_products_properties='$in{'dropprop'}'");
		$va{'tabmessages_pro'} = &trans_txt('mer_products_prodel');
		&auth_logging('mer_products_prodel',$in{'id_products'});
		$va{'message'} = &trans_txt('mer_products_prodel');
		$in{'tabs'} = 1;
	}
	my (@c) = split(/,/,$cfg{'srcolors'});
	my ($sth) = &Do_SQL("SELECT COUNT(*) FROM sl_products_properties WHERE ID_products='$in{'id_products'}'");
	$va{'matches_prop'} = $sth->fetchrow;
	if ($va{'matches_prop'}>0){
		my ($sth) = &Do_SQL("SELECT * FROM sl_products_properties,sl_properties WHERE ID_products='$in{'id_products'}' AND sl_properties.ID_properties=sl_products_properties.ID_properties ORDER BY Title;");
		while ($rec = $sth->fetchrow_hashref){
			$d = 1 - $d;
			$va{'searchresults_prop'} .= "<tr bgcolor='$c[$d]'>\n";
			$va{'searchresults_prop'} .= "  <td class='smalltext'><a href='/cgi-bin/mod/$usr{'application'}/dbman?cmd=$in{'cmd'}&view=$in{'id_products'}&tab=2&dropprop=$rec->{'ID_products_properties'}'><img src='$va{'imgurl'}/$usr{'pref_style'}/b_drop.png' title='Drop' alt='' border='0'></a> ($rec->{'ID_properties'}) $rec->{'Title'}</td>\n";
			$va{'searchresults_prop'} .= "</tr>\n";
		}
	}else{
		$va{'searchresults_prop'} = qq|
			<tr>
				<td colspan='3' align="center">|.&trans_txt('search_nomatches').qq|</td>
			</tr>\n|;
	}
}


sub load_tabs3 {
# --------------------------------------------------------
# Last Modified on: 02/03/09 13:43:22
# Last Modified by: MCC C. Gabriel Varela S: Se arregla para que se puedan agregar services items como productos relacionados.
##############################################
## tab3 : SETUP
##############################################
	## Check if it is Blocked
	# if($in{'savechoices'}){
	# 	return savechoices();
	# }
	use Data::Dumper;
	use JSON;

	local ($blocked);
	my ($sth) = &Do_SQL("SELECT COUNT(*) FROM sl_orders_products WHERE ID_products='$in{'id_sku_products'}' OR Related_ID_products='$in{'id_products'}';");
	($blocked=1) if ($sth->fetchrow() > 0);


	my ($sth) = &Do_SQL("SELECT COUNT(*) FROM sl_purchaseorders_items WHERE ID_products='$in{'id_products'}';");
	($blocked=1) if ($sth->fetchrow() > 0);


	## Choices Suggests
	$va{'choices1'} = &Do_SQL("select group_concat( distinct choiceName1) choiceName1 from sl_products where choiceName1 is not null and choiceName1 != '';")->fetchrow();
	$va{'choices2'} = &Do_SQL("select group_concat( distinct choiceName2) choiceName2 from sl_products where choiceName2 is not null and choiceName2 != '';")->fetchrow();
	$va{'choices3'} = &Do_SQL("select group_concat( distinct choiceName3) choiceName3 from sl_products where choiceName3 is not null and choiceName3 != '';")->fetchrow();
	$va{'choices4'} = &Do_SQL("select group_concat( distinct choiceName4) choiceName4 from sl_products where choiceName4 is not null and choiceName4 != '';")->fetchrow();
	## Build choices Values
	$in{'list_choice1'} = "[". &Do_SQL(qq|select group_concat( distinct concat('\\'',choice1, '\\'') ) from sl_skus where id_products = $in{'id_products'} and choice1 is not null;|)->fetchrow(). "]";
	$in{'list_choice2'} = "[". &Do_SQL(qq|select group_concat( distinct concat('\\'',choice2, '\\'') ) from sl_skus where id_products = $in{'id_products'} and choice2 is not null;|)->fetchrow(). "]";
	$in{'list_choice3'} = "[". &Do_SQL(qq|select group_concat( distinct concat('\\'',choice3, '\\'') ) from sl_skus where id_products = $in{'id_products'} and choice3 is not null;|)->fetchrow(). "]";
	$in{'list_choice4'} = "[". &Do_SQL(qq|select group_concat( distinct concat('\\'',choice4, '\\'') ) from sl_skus where id_products = $in{'id_products'} and choice4 is not null;|)->fetchrow(). "]";
	## Choices Names
	$in{'choice1'} = &Do_SQL(qq|select ChoiceName1 from sl_products where id_products = $in{'id_products'}|)->fetchrow();
	$in{'choice2'} = &Do_SQL(qq|select ChoiceName2 from sl_products where id_products = $in{'id_products'}|)->fetchrow();
	$in{'choice3'} = &Do_SQL(qq|select ChoiceName3 from sl_products where id_products = $in{'id_products'}|)->fetchrow();
	$in{'choice4'} = &Do_SQL(qq|select ChoiceName4 from sl_products where id_products = $in{'id_products'}|)->fetchrow();

	$va{'skus'} = buildSkusTable($in{'id_products'});



	# cgierr(Dumper \%va);

	
	
	
	## Load Promo
	my ($sth) = &Do_SQL("SELECT ID_vars, VValue FROM sl_vars WHERE VName='promo$in{'id_products'}';");
	# $cfg{'promo'.$in{'id_products'}} = $sth->fetchrow_hashref;
	$promoData = $sth->fetchrow_hashref();
	# cgierr(Dumper $promoData);
	## Drop From Promo
	# if (!$blocked){
	# 	$in{'droppromo'} = int($in{'droppromo'});
	# 	if ($in{'droppromo'}>0){
			
	# 		$cfg{'promo'.$in{'id_products'}} =~ s/$in{'droppromo'}|$in{'droppromo'}\|//;
	# 		$cfg{'promo'.$in{'id_products'}} =~ s/\|\|//g;
	# 		if ($cfg{'promo'.$in{'id_products'}} eq '|'){
	# 			delete($cfg{'promo'.$in{'id_products'}});
	# 			my ($sth) = &Do_SQL("DELETE FROM sl_vars WHERE VName='promo$in{'id_products'}';");		
	# 			my ($sth) = &Do_SQL("DELETE FROM sl_vars WHERE VName='percent_promo$in{'id_products'}';");		
	# 		}else{
	# 			my ($sth) = &Do_SQL("UPDATE sl_vars SET VValue='$cfg{'promo'.$in{'id_products'}}' WHERE VName='promo$in{'id_products'}';");		
	# 		}
	# 		&auth_logging('mer_products_promo_upd',$in{'id_products'});
	# 	}
	# }
	# $cfg{'promo'.$in{'id_products'}} =~ s/\|\|//g;
	# delete($cfg{'promo'.$in{'id_products'}}) if ($cfg{'promo'.$in{'id_products'}} eq '|');
	if($promoData and $promoData->{'ID_vars'}){
		return &load_tabs3_promo();
	}
	# return &load_tabs3_parts if $in{'addparts'};
	# return &load_tabs3_skus if $in{'viewsku'};
	# return &load_tabs3_promo if $cfg{'promo'.$in{'id_products'}};
	# return &load_tabs3_promo if $in{'convert_to_promo'};

	#UPDATE NAMES
# 	if($in{'updatenames'}){
# 		my ($sth) = &Do_SQL("UPDATE sl_products SET ChoiceName1='$in{'choice1'}',ChoiceName2='$in{'choice2'}',ChoiceName3='$in{'choice3'}',ChoiceName4='$in{'choice4'}' WHERE id_products='$in{'id_products'}'");
# 		&auth_logging('mer_products_updated',$in{'id_products'});
# 		for (1..4){
# 			$in{'choicename'.$_} = $in{'choice'.$_};
# 		}
# 		my ($tmp);

# 		delete($va{'tabmessage'});
# 		foreach $key (keys %in){
# 			#$tmp .= "$in{$key} $key<br>";
# 			if ($key =~ /vsku(.*)/){
# 				my ($sth) = &Do_SQL("UPDATE sl_skus SET VendorSKU='$in{$key}' WHERE ID_sku_products='$1'");
# 				#$tmp .= "UPDATE sl_skus SET VendorSKU='$in{$key}' WHERE ID_sku_products='$1'<br>";
# 				#choice1='".&filter_values($in{'ch1'.$1})."', choice2='".&filter_values($in{'ch2'.$1})."', choice3='".&filter_values($in{'ch3'.$1})."', choice4='".&filter_values($in{'ch4'.$1})."'
# 			}elsif($key =~ /upc(.*)/){
# 				#$tmp .= "$in{$key} = $key<br>";
# 				my ($sth) = &Do_SQL("SELECT COUNT(*) FROM sl_skus WHERE UPC='$in{$key}' AND ID_sku_products<>'$1'");
# 				if ($sth->fetchrow>0 and $in{$key}){
# 					$va{'tabmessage'} = &trans_txt('products_chnamesupderror');
# 				}elsif ($in{$key}){
# 					my ($sth) = &Do_SQL("UPDATE sl_skus SET UPC='$in{$key}' WHERE ID_sku_products='$1'");
# 				}
# 			}elsif ($key =~ /ch(\d)(.*)/ and $in{$key}){
# 				my ($sth) = &Do_SQL("UPDATE sl_skus SET choice$1='".&filter_values($in{$key})."' WHERE ID_products='$in{'id_products'}' AND choice$1='".&filter_values($2)."'");
# 			}
# 		}
# 		(!$va{'tabmessage'}) and ($va{'tabmessage'} = &trans_txt('products_chnamesupd'));
# 		&auth_logging('products_chnamesupd'," $in{'id_products'}");	
# 		$in{'tabs'} = 1;

# 	# ADD CHOICES
# 	}elsif ($in{'add_choices'}){
# 		# $in{'choicenum'}  <==  Numero del choice!!!!!!!
# 		my (@ary1)= &array_choices($in{'id_products'},'choice1');
# 		my (@ary2)= &array_choices($in{'id_products'},'choice2');
# 		my (@ary3)= &array_choices($in{'id_products'},'choice3');
# 		my (@ary4)= &array_choices($in{'id_products'},'choice4');
# 		($in{'choicenum'} eq 1) and (push(@ary1,$in{'choicename'}));
# 		($in{'choicenum'} eq 2) and (push(@ary2,$in{'choicename'}));
# 		($in{'choicenum'} eq 3) and (push(@ary3,$in{'choicename'}));
# 		($in{'choicenum'} eq 4) and (push(@ary4,$in{'choicename'}));
# 		for my $c1(0..$#ary1){
# 			if ($#ary2>=0){
# 				for my $c2(0..$#ary2){
# 					if ($#ary3>=0){
# 						for my $c3(0..$#ary3){
# 							if ($#ary4>=0){
# 								for my $c4(0..$#ary4){
# 									&check_tblchoices($in{'id_products'},$ary1[$c1],$ary2[$c2],$ary3[$c3],$ary4[$c4]);
# 								}
# 							}else{
# 								&check_tblchoices($in{'id_products'},$ary1[$c1],$ary2[$c2],$ary3[$c3],$ary4[$c4]);
# 							}
# 						}
# 					}else{
# 						&check_tblchoices($in{'id_products'},$ary1[$c1],$ary2[$c2],$ary3[$c3],$ary4[$c4]);
# 					}
# 				}
# 			}else{
# 				&check_tblchoices($in{'id_products'},$ary1[$c1],$ary2[$c2],$ary3[$c3],$ary4[$c4]);
# 			}
# 		}
# 		delete($in{'choicename'});
# 		delete($in{'choicesku'});
# 		$va{'tabmessage'} = &trans_txt('products_chadded') . $in{'aaa'};
# 		&auth_logging('products_chadded'," $in{'id_products'}");	

# 	#ACTIVE
# 	}elsif ($in{'active'}){
# 		my ($sth) = &Do_SQL("UPDATE sl_skus SET Status='Active' WHERE ID_sku_products='$in{'active'}'");		
# 		$va{'tabmessage'} = &trans_txt('products_chactivated');
# 		&auth_logging('products_chactivated'," $in{'id_products'}");
# 		$in{'tabs'} = 1;	

# 	#INACTIVE
# 	}elsif ($in{'inactive'}){
# 		my ($sth) = &Do_SQL("UPDATE sl_skus SET Status='Inactive' WHERE ID_sku_products='$in{'inactive'}'");		
# 		$va{'tabmessage'} = &trans_txt('products_chdeactivated');
# 		&auth_logging('products_chdeactivated'," $in{'id_products'}");
# 		$in{'tabs'} = 1;	

# 	#INACTIVE
# 	}elsif ($in{'backorder'}){
# 		my ($sth) = &Do_SQL("UPDATE sl_skus SET Status='Backorder' WHERE ID_sku_products='$in{'backorder'}'");		
# 		$va{'tabmessage'} = &trans_txt('products_chbackorder');
# 		&auth_logging('products_chdbackorder'," $in{'id_products'}");
# 		$in{'tabs'} = 1;

# 	## RELATED ITEMS
# 	}elsif($in{'addritem'}){
# 		if ($in{'upd'}) {
# 			my ($sth) = &Do_SQL("UPDATE sl_products_related SET pack_option=IF(pack_option='Yes','No','Yes') WHERE ID_products_related =  '$in{'upd'}' ;");
# 			&auth_logging('products_relatedupdated'," $in{'id_products'}");
# 		} else {

# 			my ($sth) = &Do_SQL("SELECT Status FROM sl_products_related WHERE ID_products = $in{'id_products'} AND ID_products_options = $in{'addritem'} ");
# 			my ($st) = $sth->fetchrow;
# 			if($st eq 'Active'){
# 				$va{'tabmessage'} = &trans_txt('products_ritemduplicated');
# 			}elsif($st eq 'Inactive'){
# 				my ($sth) = &Do_SQL("UPDATE sl_products_related SET Status = 'Active' WHERE ID_products = $in{'id_products'} AND ID_products_options = $in{'addritem'} ");
# 				$va{'tabmessage'} = &trans_txt('products_ritemactivated');
# 				&auth_logging('products_relatedupdated'," $in{'id_products'}");
# 				$in{'tabs'} = 1;
# 			}else{
# 				my ($sth) = &Do_SQL("INSERT INTO sl_products_related SET ID_products = $in{'id_products'},ID_products_options = $in{'addritem'},Status = 'Active',Date=CURDATE(),Time=NOW(),ID_admin_users='$usr{'id_admin_users'}'");
# 				$va{'tabmessage'} = &trans_txt('products_ritemadded');
# 				&auth_logging('products_relatedadd'," $in{'id_products'}");
# 				$in{'tabs'} = 1;
# 			}
# 		}  # End if $in{'upd'}

# 	# RELATED SERVICES
# 	}elsif($in{'addrnitem'}){
# 		my ($sth) = &Do_SQL("SELECT Status FROM sl_services_related WHERE ID_products = $in{'id_products'} AND ID_services = $in{'addrnitem'} ");
# 		my ($st) = $sth->fetchrow;
# 		if($st eq 'Active'){
# 			$va{'tabmessage'} = &trans_txt('products_rnitemduplicated');
# 		}elsif($st eq 'Inactive'){
# 			my ($sth) = &Do_SQL("UPDATE sl_services_related SET Status = 'Active' WHERE ID_products = $in{'id_products'} AND ID_services = $in{'addrnitem'} ");
# 			&auth_logging('services_related_updated',$in{'id_products'});
# 			$va{'tabmessage'} = &trans_txt('products_rnitemactivated');
# 		}else{
# 			my ($sth) = &Do_SQL("INSERT INTO sl_services_related SET ID_products = $in{'id_products'},ID_services = $in{'addrnitem'},Status = 'Active',Date=Curdate(),Time=NOW(),ID_admin_users='$usr{'id_admin_users'}'");
# 			$va{'tabmessage'} = &trans_txt('products_rnitemadded');
# 			&auth_logging('products_rnitemadded',$sth->{'mysql_insertid'});
# 		}
# 		$in{'tabs'} = 1;

# 	# DELETE ITEMS	
# 	}elsif ($in{'dropritem'}){
# 		my ($sth) = &Do_SQL("UPDATE sl_products_related SET Status = 'Inactive' WHERE ID_products_related = '$in{'dropritem'}' ");
# 		&auth_logging('products_related_updated',$in{'id_products'});
# 		$va{'tabmessage'} = &trans_txt('products_riteminactive');	
# 		$in{'tabs'} = 1;

# 	# DELETE SERVICES
# 	}elsif ($in{'droprnitem'}){
# 		my ($sth) = &Do_SQL("UPDATE sl_services_related SET Status = 'Inactive' WHERE ID_services_related = '$in{'droprnitem'}' ");
# 		&auth_logging('services_related_updated',$in{'id_products'});
# 		$va{'tabmessage'} = &trans_txt('products_rniteminactive');	
# 		$in{'tabs'} = 1;

# 	# CHOICES	
# 	}else{
# 		($in{'choicename1'},$in{'choicename2'},$in{'choicename3'},$in{'choicename4'})
# 		= split(/,/,&load_db_names('sl_products','ID_products',$in{'id_products'},'[choicename1],[choicename2],[choicename3],[choicename4]'));
# 	}


# 	############################
# 	## Build Choices 
# 	############################	
# 	my (@c) = split(/,/,$cfg{'srcolors'});
# 	my ($status,$style,$vsku, $tot_skus);
# 	my ($sth) = &Do_SQL("SELECT COUNT(*) FROM sl_skus WHERE ID_products='$in{'id_products'}'");
# 	$va{'matches'} = $sth->fetchrow;
# 	if ($va{'matches'}>0){

# 		#################################
# 		##### build Choice 1
# 		#################################
# 		my ($sth) = &Do_SQL("SELECT DISTINCT(choice1) FROM sl_skus WHERE ID_products='$in{'id_products'}';");
# 		while ($rec = $sth->fetchrow_hashref){
# 			$d = 1 - $d;
# 			if (exists($rec->{'choice1'})){
# 				$va{'choice1_list'} .= "<tr bgcolor='$c[$d]'>\n";
# 				$va{'choice1_list'} .= "  <td class='smalltext' width='50%'>$rec->{'choice1'}</td>\n";
# 				$va{'choice1_list'} .= "  <td class='smalltext' width='50%'><input type='text' name='ch1$rec->{'choice1'}' value='$rec->{'choice1'}' onFocus='focusOn( this )' onBlur='focusOff( this )' size='35'></td>\n";
# 				$va{'choice1_list'} .= "</tr>\n";
# 			}	
# 		}
# 		#################################
# 		##### build Choice 2
# 		#################################
# 		my ($sth) = &Do_SQL("SELECT DISTINCT(choice2) FROM sl_skus WHERE ID_products='$in{'id_products'}';");
# 		while ($rec = $sth->fetchrow_hashref){
# 			$d = 1 - $d;
# 			if ($rec->{'choice2'}){
# 				$va{'choice2_list'} .= "<tr bgcolor='$c[$d]'>\n";
# 				$va{'choice2_list'} .= "  <td class='smalltext' width='50%'>$rec->{'choice2'}</td>\n";
# 				$va{'choice2_list'} .= "  <td class='smalltext' width='50%'><input type='text' name='ch2$rec->{'choice2'}' value='$rec->{'choice2'}' onFocus='focusOn( this )' onBlur='focusOff( this )' size='35'></td>\n";
# 				$va{'choice2_list'} .= "</tr>\n";
# 			}	
# 		}
# 		#################################
# 		##### build Choice 3
# 		#################################
# 		my ($sth) = &Do_SQL("SELECT DISTINCT(choice3) FROM sl_skus WHERE ID_products='$in{'id_products'}';");
# 		while ($rec = $sth->fetchrow_hashref){
# 			$d = 1 - $d;
# 			if ($rec->{'choice3'}){
# 				$va{'choice3_list'} .= "<tr bgcolor='$c[$d]'>\n";
# 				$va{'choice3_list'} .= "  <td class='smalltext' width='50%'>$rec->{'choice3'}</td>\n";
# 				$va{'choice3_list'} .= "  <td class='smalltext' width='50%'><input type='text' name='ch3$rec->{'choice3'}' value='$rec->{'choice3'}' onFocus='focusOn( this )' onBlur='focusOff( this )' size='35'></td>\n";
# 				$va{'choice3_list'} .= "</tr>\n";
# 			}	
# 		}
# 		#################################
# 		##### build Choice 4
# 		#################################
# 		my ($sth) = &Do_SQL("SELECT DISTINCT(choice4) FROM sl_skus WHERE ID_products='$in{'id_products'}';");
# 		while ($rec = $sth->fetchrow_hashref){
# 			$d = 1 - $d;
# 			if ($rec->{'choice4'}){
# 				$va{'choice4_list'} .= "<tr bgcolor='$c[$d]'>\n";
# 				$va{'choice4_list'} .= "  <td class='smalltext' width='50%'>$rec->{'choice4'}</td>\n";
# 				$va{'choice4_list'} .= "  <td class='smalltext' width='50%'><input type='text' name='ch3$rec->{'choice4'}' value='$rec->{'choice4'}' onFocus='focusOn( this )' onBlur='focusOff( this )' size='35'></td>\n";
# 				$va{'choice4_list'} .= "</tr>\n";
# 			}	
# 		}
# 		#################################
# 		##### build Vendor SKUs
# 		#################################
# 		my ($sth) = &Do_SQL("SELECT * FROM sl_skus WHERE ID_products='$in{'id_products'}' ORDER BY ID_sku_products;");
# 		while ($rec = $sth->fetchrow_hashref){
# 			++$tot_skus;

# 			## Is Set?
# 			my ($sth) = &Do_SQL("SELECT COUNT(*) FROM sl_skus_parts WHERE ID_sku_products='$rec->{'ID_sku_products'}';");
# 			if ($sth->fetchrow() > 0){
# 				my ($sth) = &Do_SQL("UPDATE sl_skus SET IsSet='Y' WHERE ID_sku_products='$rec->{'ID_sku_products'}';");
# 			}else{
# 				my ($sth) = &Do_SQL("UPDATE sl_skus SET IsSet='N' WHERE ID_sku_products='$rec->{'ID_sku_products'}';");
# 			}

# 			$d = 1 - $d;

# 			$status='';
# 			$backorder='';
# 			($rec->{'Status'} eq 'Backorder') and ($backorder='<span style="font-size:12px;font-weight:bolder;">[B.O.]</span>');

# 			if ($rec->{'Status'} eq 'Backorder'){
# 				$status = qq| <a href="/cgi-bin/mod/$usr{'application'}/dbman?cmd=$in{'cmd'}&view=$in{'id_products'}&tab=3&inactive=$rec->{'ID_sku_products'}"><img src='$va{'imgurl'}/$usr{'pref_style'}/b_toinact.png' title='Inactive' alt='' border='0'></a>&nbsp;&nbsp;
# 											<a href="/cgi-bin/mod/$usr{'application'}/dbman?cmd=$in{'cmd'}&view=$in{'id_products'}&tab=3&active=$rec->{'ID_sku_products'}"><img src='$va{'imgurl'}/$usr{'pref_style'}/b_toact.png' title='Active' alt='' border='0'></a>|;
# 				$style ='style="font-style:italic;"';
# 				$vsku = qq|<input type="text" name="vsku$rec->{'ID_sku_products'}" value="$rec->{'VendorSKU'}" onFocus='focusOn( this )' onBlur='focusOff( this )' size="15">|;
# 				$upc = qq|<input type="text" name="upc$rec->{'ID_sku_products'}" value="$rec->{'UPC'}" onFocus='focusOn( this )' onBlur='focusOff( this )' size="15">
# 						<a href="/cgi-bin/mod/$usr{'application'}/dbman?cmd=$in{'cmd'}&view=$in{'id_products'}&tab=3&addparts=$rec->{'ID_sku_products'}&tabs=1">
# 								<img id='tabs' src='/sitimages/default/b_edit.png' title='Add Parts' alt='Add Parts' border='0'>
# 								</a>|;	
# 			}elsif ($rec->{'Status'} eq 'Active'){
# 				$status = qq|<a href="/cgi-bin/mod/$usr{'application'}/dbman?cmd=$in{'cmd'}&view=$in{'id_products'}&tab=3&backorder=$rec->{'ID_sku_products'}"><img src='$va{'imgurl'}/$usr{'pref_style'}/backorder.jpeg' title='Backorder' alt='' border='0'></a>&nbsp;&nbsp; 
# 										<a href="/cgi-bin/mod/$usr{'application'}/dbman?cmd=$in{'cmd'}&view=$in{'id_products'}&tab=3&inactive=$rec->{'ID_sku_products'}"><img src='$va{'imgurl'}/$usr{'pref_style'}/b_toinact.png' title='Inactive' alt='' border='0'></a>|;
# 				$style ='';
# 				$vsku = qq|<input type="text" name="vsku$rec->{'ID_sku_products'}" value="$rec->{'VendorSKU'}" onFocus='focusOn( this )' onBlur='focusOff( this )' size="15">|;
# 				$upc = qq|<input type="text" name="upc$rec->{'ID_sku_products'}" value="$rec->{'UPC'}" onFocus='focusOn( this )' onBlur='focusOff( this )' size="15">
# 						<a href="/cgi-bin/mod/$usr{'application'}/dbman?cmd=$in{'cmd'}&view=$in{'id_products'}&tab=3&addparts=$rec->{'ID_sku_products'}&tabs=1">
# 								<img id='tabs' src='/sitimages/default/b_edit.png' title='Add Parts' alt='Add Parts' border='0'>
# 								</a>|;
# 			}else{
# 				$status = qq|<a href="/cgi-bin/mod/$usr{'application'}/dbman?cmd=$in{'cmd'}&view=$in{'id_products'}&tab=3&backorder=$rec->{'ID_sku_products'}"><img src='$va{'imgurl'}/$usr{'pref_style'}/backorder.jpeg' title='Backorder' alt='' border='0'></a>&nbsp;&nbsp; 
# 										<a href="/cgi-bin/mod/$usr{'application'}/dbman?cmd=$in{'cmd'}&view=$in{'id_products'}&tab=3&active=$rec->{'ID_sku_products'}"><img src='$va{'imgurl'}/$usr{'pref_style'}/b_toact.png' title='Active' alt='' border='0'></a>|;
# 				$style = " style=' text-decoration: line-through'";
# 				$vsku = qq|<input type="hidden" name="vsku$rec->{'ID_sku_products'}" value="$rec->{'VendorSKU'}" onFocus='focusOn( this )' onBlur='focusOff( this )' size="15">$rec->{'VendorSKU'}|;
# 				$upc = qq|<input type="hidden" name="upc$rec->{'ID_sku_products'}" value="$rec->{'UPC'}" onFocus='focusOn( this )' onBlur='focusOff( this )' size="15">$rec->{'UPC'}|;

# 			}
# 			(!$rec->{'choice2'}) and ($rec->{'choice2'}='---');
# 			(!$rec->{'choice3'}) and ($rec->{'choice3'}='---');
# 			(!$rec->{'choice4'}) and ($rec->{'choice4'}='---');
# 			$va{'skus_list'} .= qq|
# 			<tr bgcolor='$c[$d]' onmouseover='m_over(this)' onmouseout='m_out(this)'>
# 				<td align="center" class="smalltext" $style>$status
# 							<a href="/cgi-bin/mod/$usr{'application'}/dbman?cmd=$in{'cmd'}&view=$in{'id_products'}&tab=3&viewsku=$rec->{'ID_sku_products'}">|.format_sltvid($rec->{'ID_sku_products'}).qq| $backorder</a></td>
# 				<td align="center" class="smalltext" $style>$rec->{'choice1'}</td>
# 				<td align="center" class="smalltext" $style>$rec->{'choice2'}</td>
# 				<td align="center" class="smalltext" $style>$rec->{'choice3'}</td>
# 				<td align="center" class="smalltext" $style>$rec->{'choice4'}</td>
# 				<td align="center" class="smalltext" $style>$vsku</td>
# 				<td align="center" class="smalltext" $style>$upc</td>
# 			</tr>\n|;
# 			my ($sth2) = &Do_SQL("SELECT * FROM sl_skus_parts WHERE ID_sku_products='$rec->{'ID_sku_products'}';");
# 			while ($tmp = $sth2->fetchrow_hashref){
# 				$va{'skus_list'} .= qq|
# 			<tr bgcolor='$c[$d]' onmouseover='m_over(this)' onmouseout='m_out(this)'>
# 				<td>&nbsp;</td>
# 				<td class="smalltext" $style colspan="6"><img src="$va{'imgurl'}/$usr{'pref_style'}/tri.gif" border="0"> 
# 				$tmp->{'Qty'} <span class="help_on">x</span> 
# 				(<a href="/cgi-bin/mod/$usr{'application'}/dbman?cmd=mer_parts&view=$tmp->{'ID_parts'}">|.&format_sltvid(400000000+$tmp->{'ID_parts'}).qq|</a>) |. &load_db_names('sl_parts','ID_parts',$tmp->{'ID_parts'},'[Model]/[Name]') .qq|</td>
# 			</tr>\n|;
# 			}
# 		}
# 	}
# 	## Converto to Promo
# 	$va{'btnconvertpromo'} = qq|<input type="submit" name="convert_to_promo" value="Convert to Promo" class="button">| if ($tot_skus==1);
	
# 	#CHOICES LIST
# 	if (!$va{'choice1_list'}){
# 		$va{'choice1_list'} = qq|
# 			<tr>
# 				<td align="center" colspan="2">|.&trans_txt('search_nomatches').qq|</td>
# 			</tr>\n|;
# 	}
# 	if (!$va{'choice2_list'}){
# 		$va{'choice2_list'} = qq|
# 			<tr>
# 				<td align="center" colspan="2">|.&trans_txt('search_nomatches').qq|</td>
# 			</tr>\n|;
# 	}
# 	if (!$va{'choice3_list'}){
# 		$va{'choice3_list'} = qq|
# 			<tr>
# 				<td align="center" colspan="2">|.&trans_txt('search_nomatches').qq|</td>
# 			</tr>\n|;
# 	}
# 	if (!$va{'choice4_list'}){
# 		$va{'choice4_list'} = qq|
# 			<tr>
# 				<td align="center" colspan="2">|.&trans_txt('search_nomatches').qq|</td>
# 			</tr>\n|;
# 	}

# 	############################
# 	#    Build Relatd Items    #
# 	############################

# 	my (@c) = split(/,/,$cfg{'srcolors'});
# 	my ($sth) = &Do_SQL("SELECT COUNT(ID_products_options) FROM (SELECT ID_products_options,ID_products_related,Model,Name,SPrice,'Product'as Type
# FROM sl_products_related,sl_products 
# WHERE sl_products_related.ID_products='$in{'id_products'}' 
# AND sl_products_related.ID_products_options = sl_products.ID_products 
# AND sl_products_related.Status = 'Active' 
# union
# SELECT sl_services_related.ID_services as ID_products_options,ID_services_related,'' as Model,Name,SPrice,'Servis'as Type
# FROM sl_services_related,sl_services
# WHERE sl_services_related.ID_products='$in{'id_products'}' 
# AND sl_services_related.ID_services = sl_services.ID_services
# AND sl_services_related.Status = 'Active' 
# )as tempo");
# 	$va{'matches'} = $sth->fetchrow;
# 	if ($va{'matches'}>0){
# 		my ($sth) = &Do_SQL("SELECT ID_products_options,ID_products_related,Model,Name,SPrice,'Product'as Type,pack_option 
# FROM sl_products_related,sl_products 
# WHERE sl_products_related.ID_products='$in{'id_products'}' 
# AND sl_products_related.ID_products_options = sl_products.ID_products 
# AND sl_products_related.Status = 'Active' 
# union
# SELECT sl_services_related.ID_services as ID_products_options,ID_services_related,'' as Model,Name,SPrice,'Servis'as Type, '' as pack_option 
# FROM sl_services_related,sl_services
# WHERE sl_services_related.ID_products='$in{'id_products'}' 
# AND sl_services_related.ID_services = sl_services.ID_services
# AND sl_services_related.Status = 'Active' 
# ORDER BY Name ");
# 		while ($rec = $sth->fetchrow_hashref){
# 			$d = 1 - $d;
# 				if($rec->{'Type'} eq "Product")
# 				{
# 					$va{'related_list'} .= qq|<tr bgcolor='$c[$d]'>
# 					<td class="smalltext" valign="top">&nbsp;&nbsp;&nbsp;&nbsp;
# 					<a href="/cgi-bin/mod/$usr{'application'}/dbman?cmd=$in{'cmd'}&view=$rec->{'ID_products_options'}"><img src='$va{'imgurl'}/$usr{'pref_style'}/b_view.gif' title='View' alt='' border='0'></a>&nbsp;
# 					<a href="/cgi-bin/mod/$usr{'application'}/dbman?cmd=$in{'cmd'}&view=$in{'id_products'}&tab=3&dropritem=$rec->{'ID_products_related'}"><img src='$va{'imgurl'}/$usr{'pref_style'}/b_drop.png' title='Delete' alt='' border='0'></a>
# 					|.&format_sltvid($rec->{'ID_products_options'}+100000000).qq|</td>
# 					<td class="smalltext">
# 					$rec->{'Model'}<br>$rec->{'Name'}</td>
# 					<td class="smalltext" valign="top" align="center">
# 					<a href="/cgi-bin/mod/$usr{'application'}/dbman?cmd=$in{'cmd'}&view=$in{'id_products'}&tab=3&addritem=1&upd=$rec->{'ID_products_related'}">$rec->{'pack_option'}</a></td>
# 					<td class="smalltext" valign="top" align="right" nowrap>|.&format_price($rec->{'SPrice'}).qq|</a></td>
# 					</tr>\n |;
# 				}
# 				else
# 				{
# 					$va{'related_list'} .= qq|<tr bgcolor='$c[$d]'>
# 					<td class="smalltext" valign="top">&nbsp;&nbsp;&nbsp;&nbsp;
# 					<a href="/cgi-bin/mod/$usr{'application'}/dbman?cmd=mer_services&view=$rec->{'ID_products_options'}"><img src='$va{'imgurl'}/$usr{'pref_style'}/b_view.gif' title='View' alt='' border='0'></a>&nbsp;
# 					<a href="/cgi-bin/mod/$usr{'application'}/dbman?cmd=$in{'cmd'}&view=$in{'id_products'}&tab=3&droprnitem=$rec->{'ID_products_related'}"><img src='$va{'imgurl'}/$usr{'pref_style'}/b_drop.png' title='Delete' alt='' border='0'></a>
# 					|.&format_sltvid($rec->{'ID_products_options'}+600000000).qq|</td>
# 					<td class="smalltext">
# 					$rec->{'Model'}<br>$rec->{'Name'}</td>					
# 					<td class="smalltext" valign="top" align="right" nowrap>|.&format_price($rec->{'SPrice'}).qq|</a></td>					
# 					</tr>\n |;
# 				}				
# 		}		
# 	}else{
# 			$va{'related_list'} .= qq|<tr bgcolor='$c[$d]'>
# 			<td valign="top" align="center" colspan="3">|.&trans_txt('search_nomatches').qq|\n |;
# 	}
	
}


sub load_tabs3_skus {
# --------------------------------------------------------
##############################################
## tab3 : SKUS
##############################################

	$va{'new_tbname'} = 'products_tab3_skus';

	my($sth) = &Do_SQL("SELECT * FROM sl_skus WHERE ID_sku_products= $in{'viewsku'} and Status='Active'");
	while ($rec = $sth->fetchrow_hashref){
		my ($query) = &Do_SQL("SELECT sl_warehouses.name,sl_warehouses_location.quantity,sl_warehouses_location.Location FROM sl_warehouses,sl_warehouses_location WHERE sl_warehouses.ID_warehouses= sl_warehouses_location.ID_warehouses and sl_warehouses_location.ID_products=$in{'viewsku'}");
		while ($rel = $query->fetchrow_hashref){
			(!$rec->{'choice1'}) and ($rec->{'choice1'}='---');
			(!$rec->{'choice2'}) and ($rec->{'choice2'}='---');
			(!$rec->{'choice3'}) and ($rec->{'choice3'}='---');
			(!$rec->{'choice4'}) and ($rec->{'choice4'}='---');
			$va{'inventory'} .= qq|
		<tr bgcolor='$c[$d]' onmouseover='m_over(this)' data-id_products="$rec->{'ID_sku_products'}" onmouseout='m_out(this)'>
			<td align="center" class="smalltext">$rec->{'ID_sku_products'}</td>
			<td align="center" class="smalltext">$rec->{'choice1'}</td>
			<td align="center" class="smalltext">$rec->{'choice2'}</td>
			<td align="center" class="smalltext">$rec->{'choice3'}</td>
			<td align="center" class="smalltext">$rec->{'choice4'}</td>
			<td align="center" class="smalltext">$rel->{'quantity'}</td>				
			<td align="center" class="smalltext">$rel->{'Location'}<br>$rel->{'name'}</td>
			<td align="center" class="smalltext">$rec->{'ID_admin_users'} |. &load_db_names('admin_users','ID_admin_users',$rec->{'ID_admin_users'},'[FirstName] [LastName]').qq|
		<br>\@ $rec->{'Date'} $rec->{'Time'}</td>
		</tr>\n|;
    	}
    	if (!$va{'inventory'}){
    		$va{'inventory'} = qq|
					<tr>
						<td align="center" colspan="7">|.&trans_txt('search_nomatches').qq|</td>
					</tr>\n|;
    	}
	}	  
	$skus = '_skus';
}


sub load_tabs3_parts {
# --------------------------------------------------------
##############################################
## tab3 : PARTS
##############################################

	my ($rec,$id);
	$va{'new_tbname'} = 'products_tab3_parts';

	#UPDATE
	if ($in{'update_parts'}){
		foreach $key (keys %in){
			if ($key =~ /^qty(\d+)/){
				$id = $1;;
				$in{$key} = int($in{$key});
				if ($in{$key}>0){
					## Update Record
					my ($sth) = &Do_SQL("UPDATE sl_skus_parts SET Qty=$in{$key} WHERE ID_skus_parts='$id';");
					&auth_logging('sku_parts_updated',$id);
				}else{
					## Delete Record
					my ($sth) = &Do_SQL("DELETE FROM sl_skus_parts WHERE ID_skus_parts='$id';");
					&auth_logging('sku_parts_deleted',$id);
				}
			}
		}	
	}

	if ($in{'id_parts'} and !$blocked){
		my ($sth) = &Do_SQL("INSERT INTO sl_skus_parts SET ID_sku_products='$in{'addparts'}',Qty=1,ID_parts='$in{'id_parts'}',Date=Curdate(),Time=NOW(),ID_admin_users='$usr{'id_admin_users'}';");
		&auth_logging('sku_parts_added',$sth->{'mysql_insertid'});
	}

	## Is Set?
	my ($sth) = &Do_SQL("SELECT COUNT(*) FROM sl_skus_parts WHERE ID_sku_products='$in{'addparts'}';");
	if ($sth->fetchrow() > 0){
		my ($sth) = &Do_SQL("UPDATE sl_skus SET IsSet='Y' WHERE ID_sku_products='$in{'addparts'}';");
	}else{
		my ($sth) = &Do_SQL("UPDATE sl_skus SET IsSet='N' WHERE ID_sku_products='$in{'addparts'}';");
	}
	&auth_logging('sku_updated',$in{'addparts'});


	my ($sth) = &Do_SQL("SELECT * FROM sl_skus WHERE ID_sku_products='$in{'addparts'}' and Status='Active';");
	$rec = $sth->fetchrow_hashref;
	(!$rec->{'choice2'}) and ($rec->{'choice2'}='---');
	(!$rec->{'choice3'}) and ($rec->{'choice3'}='---');
	(!$rec->{'choice4'}) and ($rec->{'choice4'}='---');
	$va{'skus_info'} .= qq|
		<tr bgcolor='$c[$d]' onmouseover='m_over(this)' onmouseout='m_out(this)'>
			<td align="center" class="smalltext" $style>|.format_sltvid($rec->{'ID_sku_products'}).qq|</td>
			<td align="center" class="smalltext" $style>$rec->{'choice1'}</td>
			<td align="center" class="smalltext" $style>$rec->{'choice2'}</td>
			<td align="center" class="smalltext" $style>$rec->{'choice3'}</td>
			<td align="center" class="smalltext" $style>$rec->{'choice4'}</td>
			<td align="center" class="smalltext" $style>$rec->{'VendorSKU'}</td>
			<td align="center" class="smalltext" $style>$rec->{'UPC'}</td>
		</tr>\n|;
	if ($blocked){
		$va{'hstart'} = '<!--';
		$va{'hend'}   = '-->';
	}
	my ($sth) = &Do_SQL("SELECT sl_skus_parts.ID_sku_products, sl_skus_parts.ID_parts, sl_skus_parts.Qty, sl_skus.UPC 
						FROM sl_skus_parts 
							LEFT JOIN sl_skus ON sl_skus_parts.ID_parts = sl_skus.ID_products
						WHERE sl_skus_parts.ID_sku_products='".$in{'addparts'}."'
						GROUP BY sl_skus_parts.ID_parts;");
	while ($rec = $sth->fetchrow_hashref){
		if (!$blocked){
			$rec->{'Qty'} = qq|<input type="text" name="qty$rec->{'ID_skus_parts'}" value="$rec->{'Qty'}" size="2" onFocus='focusOn( this )' onBlur='focusOff( this )'>|;
		}
		$va{'parts_list'} .= qq|
		<tr bgcolor='$c[$d]' onmouseover='m_over(this)' onmouseout='m_out(this)'>
			<td align="center" class="smalltext">$rec->{'Qty'}</td>
			<td align="center" class="smalltext"><a href="/cgi-bin/mod/$usr{'application'}/dbman?cmd=mer_parts&view=$rec->{'ID_parts'}">|.&format_sltvid($rec->{'ID_parts'}+400000000).qq|</a></td>
			<td align="center" class="smalltext">|.$rec->{'UPC'}.qq|</td>
			<td class="smalltext">|.&load_db_names('sl_parts','ID_parts',$rec->{'ID_parts'},'[Model]/[Name]') .qq|</td>
		</tr>\n|;
	}
	if (!$va{'parts_list'}){
		$va{'parts_list'} .= qq|
		<tr bgcolor='$c[$d]' onmouseover='m_over(this)' onmouseout='m_out(this)'>
			<td align="center" class="smalltext" colspan="7">|. &trans_txt('search_nomatches') .qq|</td>
		</tr>\n|;
	}
}


sub load_tabs3_promo{
#-----------------------------------------
# Created on: 07/07/09  19:28:25 By  Carlos Haas
# Forms Involved: 
# Description : Si el producto es un promo, entonces se imprime otro html
# Parameters : 	

	# if ($blocked){
	# 	$va{'new_tbname'} = 'products_tab3_promo';
	# }else{
	# 	$in{'addpromo'} = int($in{'addpromo'});
	# 	if ($in{'addpromo'}>0 or $in{'addpromo'} eq $in{'id_products'}){
	# 		## Valida if the ID is not a promo
	# 		my ($sth) = &Do_SQL("SELECT COUNT(*) FROM sl_vars WHERE VName='promo$in{'addpromo'}';");
	# 		if ($sth->fetchrow eq 0){
	# 			&auth_logging('mer_products_promo_upd',$in{'id_products'});
	# 			my ($sth) = &Do_SQL("SELECT ID_vars, VValue FROM sl_vars WHERE VName='promo$in{'id_products'}';");
	# 			my ($id,$vval) = $sth->fetchrow_array();
	# 			if ($id>0){
	# 				my ($sth) = &Do_SQL("UPDATE sl_vars SET VValue='$vval|$in{'addpromo'}' WHERE ID_vars=$id;");
	# 			}else{
	# 				my ($sth) = &Do_SQL("INSERT INTO sl_vars SET VName='promo$in{'id_products'}',VValue='$in{'addpromo'}';");
	# 			}
	# 		}
	# 	}
	# 	$va{'new_tbname'} = 'products_tab3_cpromo';
	# }
	
	$va{'new_tbname'} = 'products_tab3_promo';
	
	my ($sth) = &Do_SQL("SELECT 
		(SELECT TRIM( BOTH '|' FROM VValue ) FROM sl_vars WHERE VName='promo$in{'id_products'}')promo
		, (SELECT TRIM( BOTH '|' FROM VValue ) FROM sl_vars WHERE VName='percent_promo$in{'id_products'}')percent_promo;");
	my ($promo,$percent_promo) = $sth->fetchrow;
	$promo = $cfg{'promo'.$in{'id_products'}} if (!$promo and $cfg{'promo'.$in{'id_products'}});
	
	my (@products) = split(/\|/,$promo);
	my (@percents) = split(/\|/,$percent_promo);
	my (@c) = split(/,/,$cfg{'srcolors'});

	for(0..$#products){

		if($products[$_]>0){

			$d = 1 - $d;

			my $this_pct = $percents[$_] >= 0 ? $percents[$_] : 0;
			my ($sth) = &Do_SQL("SELECT ID_products,Model,Name FROM sl_products WHERE ID_products = $products[$_];");
			my ($id_products,$model,$name) = $sth->fetchrow();
	
			$va{'searchresults'} .= "<tr bgcolor='$c[$d]'>\n";

			if ($blocked){
			
				$va{'searchresults'} .= "  <td class='smalltext'><a href='/cgi-bin/mod/$usr{'application'}/dbman?cmd=$in{'cmd'}&view=$id_products'>".&format_sltvid(100000000+$id_products)."</td>\n";
			
			}else{

				$va{'searchresults'} .= "  <td colspan='4'>
					<div data-id_skus_products='$in{'id_products'}' data-id_part='$id_products'>( <a target='_blank' href='/cgi-bin/mod/admin/dbman?cmd=mer_parts&amp;view=$id_products'> ".&format_sltvid(100000000+$id_products)."</a> ) $model / $name <img src='/sitimages/aqua/b_drop.png' class='borrarSku'> 
						<input type='number' name='porcentaje' value='$this_pct'></div></td>";
			}

		
		}
	}

	$va{'script'} =q|<script>
		$(function() {
				$('[data-id_skus_products] .borrarSku').on('click', function(){
				if(confirm('¿Esta seguro de eliminar el Part seleccionado?')){
					$(this).parent().hide('slow', function(){$(this).remove()});
				}
			});
		});
	</script>|;
	if (!$va{'searchresults'}){
		$va{'searchresults'} .= qq|
		<tr bgcolor='$c[$d]' onmouseover='m_over(this)' onmouseout='m_out(this)'>
			<td align="center" class="smalltext" id="no-result" colspan="4">|. &trans_txt('search_nomatches') .qq|</td>
		</tr>\n|;
	}	
}

sub load_tabs4 {
# --------------------------------------------------------
##############################################
## tab4 : PRICES
##############################################

	### Sale Prices		
	my (@c) = split(/,/,$cfg{'srcolors'});
	my ($sth) = &Do_SQL("SELECT COUNT(*) FROM sl_products_prices WHERE ID_products='$in{'id_products'}'");
	$va{'matches'} = $sth->fetchrow;

	if ($va{'matches'}>0){	

		my ($sth) = &Do_SQL("SELECT ID_products_prices, Name, Price, Downpayment, AuthCode, FP, PayType, Origins, BelongsTo, ValidKits FROM sl_products_prices WHERE ID_products='$in{'id_products'}' ORDER BY Name,PayType,Price ASC;");
		while (my ($idpp, $name, $price, $dp, $authcode, $fp, $ptype, $origins, $belongsto, $kits)= $sth->fetchrow() ){
			$origins =~ s/\|/\,/g;
			$origins = substr($origins,1) if(substr($origins,0,1) eq ',');
			$origins = substr($origins,0,(length($origins)-1)) if(substr($origins,-1) eq ',');
			$kits =~ s/\|/\,/g;
			my $add_sql = ($origins ne '')? " AND ID_salesorigins IN( $origins) ":"";
			my ($sth2) = &Do_SQL("SELECT group_concat(channel)as channel FROM sl_salesorigins WHERE 1 $add_sql ORDER BY channel;");
			my ($consoles)= $sth2->fetchrow();

			$d = 1 - $d;
			$va{'searchresults'} .= "<tr bgcolor='$c[$d]'>\n";
			$va{'searchresults'} .= "  <td class='smalltext'><a href='/cgi-bin/mod/".$usr{'application'}."/dbman?cmd=".$in{'cmd'}."&view=".$in{'id_products'}."&tab=4&action=1&drop=".$idpp."'>
										<img src='$va{'imgurl'}/$usr{'pref_style'}/b_drop.png' title='Delete' alt='' border='0'></a>&nbsp;
										<img src='$va{'imgurl'}/main/list.png' alt='$consoles' title='$consoles' border='0'>
										<img src='$va{'imgurl'}/main/b_ok.png' alt='$kits' title='$kits' border='0'>
										<img src='$va{'imgurl'}/main/web.png' alt='$belongsto' title='$belongsto' border='0'></td>";			
			$va{'searchresults'} .= "  <td class='smalltext'>$name</td>\n";
			$va{'searchresults'} .= "  <td class='smalltext'>$fp</td>\n";
			$va{'searchresults'} .= "  <td class='smalltext'>$ptype</td>\n";
			$va{'searchresults'} .= "  <td class='smalltext'>$authcode</td>\n";
			$va{'searchresults'} .= "  <td class='smalltext'align='right'>".&format_price($price)."</td>\n";
			$va{'searchresults'} .= "  <td class='smalltext'align='right'>".&format_price($dp)."</td>\n";
			$va{'searchresults'} .= "</tr>\n";
		
		}
	
	}else{
	
		$va{'searchresults'} = qq|
			<tr>
				<td colspan='8' align="center">|.&trans_txt('search_nomatches').qq|</td>
			</tr>\n|;
	
	}

}


sub load_tabs5 {
# --------------------------------------------------------
##############################################
## tab6 : TESTING
##############################################
# Last Modified RB: 09/10/09  16:31:41 -- Productos aprobados por niveles developer,administrator
# Last Modified RB: 06/16/10  17:38:41 -- Productos solamente aprobados si tienen registro en sku y cada sku tiene al menos una parte 
# Last Modified RB: 06/16/10  17:38:41 -- Se agrego regla en productos aprobados. Deben tener al menos una categoria asignada.

	$in{'testing_authby'} = &load_name('sl_products','ID_products',$in{'id_products'},'Testing_AuthBy');
	($in{'testing_authby'} eq '') and ($in{'testing_authby'} = 0);

	if ($in{'testing_authby'} > 0){
		$va{'strdel_start'} = "<!--";
		$va{'strdel_end'} = "-->";
	}

	my ($query);
	if ($in{'filter'}){
		$query = "AND Type='".&filter_values($in{'filter'})."' ";
		$va{'query'} = $in{'filter'};
		$in{'tabs'} = 1;
	}

	my (@c) = split(/,/,$cfg{'srcolors'});
	my ($sth) = &Do_SQL("SELECT COUNT(*) FROM sl_products_tests WHERE id_products='$in{'id_products'}' $query");
	$va{'matches'} = $sth->fetchrow;
	if ($va{'matches'}>0){
		if ($in{'print'}){
			$sth = &Do_SQL("SELECT sl_products_tests.Date,sl_products_tests.Time,sl_products_tests.ID_admin_users,Type,Notes,FirstName,LastName FROM sl_products_tests,admin_users WHERE id_products='$in{'id_products'}' AND sl_products_tests.ID_admin_users=admin_users.ID_admin_users $query ORDER BY ID_products_tests DESC");
		}else{
			(!$in{'nh'}) and ($in{'nh'}=1);
			$first = ($in{'nh'} - 1) * $usr{'pref_maxh'};			
			($va{'pageslist'},$qs) = &pages_list($in{'nh'},"/cgi-bin/mod/$usr{'application'}/dbman",$va{'matches'},$usr{'pref_maxh'});
			$sth = &Do_SQL("SELECT sl_products_tests.Date,sl_products_tests.Time,sl_products_tests.ID_admin_users,Type,Notes,FirstName,LastName FROM sl_products_tests,admin_users WHERE id_products='$in{'id_products'}' AND sl_products_tests.ID_admin_users=admin_users.ID_admin_users $query ORDER BY ID_products_tests DESC LIMIT $first,$usr{'pref_maxh'};");
		}

		while ($rec = $sth->fetchrow_hashref){
			$d = 1 - $d;
			$rec->{'Notes'} =~ s/\n/<br>/g;
			$va{'searchresults'} .= "<tr bgcolor='$c[$d]'>\n";
			$va{'searchresults'} .= "   <td class='smalltext' valign='top'>$rec->{'Date'} $rec->{'Time'}<br>($rec->{'ID_admin_users'}) $rec->{'FirstName'} $rec->{'LastName'}</td>\n";
			$va{'searchresults'} .= "   <td class='smalltext' valign='top'>$rec->{'Type'}</td>\n";
			$va{'searchresults'} .= "   <td class='smalltext' valign='top'>$rec->{'Notes'}</td>\n";
			$va{'searchresults'} .= "</tr>\n";
		}
	}else{
		$va{'pageslist'} = 1;
		$va{'searchresults'} = qq|
			<tr>
				<td colspan='3' align="center">|.&trans_txt('search_nomatches').qq|</td>
			</tr>\n|;
	}

	
}


sub load_tabs6 {
# --------------------------------------------------------
##############################################
## tab11 : ORDERS
##############################################

	my (@c) = split(/,/,$cfg{'srcolors'});
	my ($sth) = &Do_SQL("SELECT COUNT(DISTINCT sl_orders.ID_orders) FROM sl_orders_products
											INNER JOIN sl_orders ON sl_orders_products.ID_orders = sl_orders.ID_orders
											AND RIGHT( ID_products, 6 ) = '$in{'id_products'}' AND sl_orders_products.Status = 'Active'
											INNER JOIN sl_customers ON sl_orders.ID_customers = sl_customers.ID_customers  ");

	$va{'matches'} = $sth->fetchrow;
	if ($va{'matches'}>0){
		if ($in{'print'}){
			$sth = &Do_SQL("SELECT DISTINCT sl_orders_products.ID_orders,sl_customers.ID_customers, CONCAT(FirstName,' ',LastName1) AS Name,
												ShpDate, sl_orders.Date, sl_orders.Status  
												FROM sl_orders_products INNER JOIN sl_orders ON sl_orders_products.ID_orders = sl_orders.ID_orders AND
												RIGHT(ID_products,6) = '$in{'id_products'}' AND sl_orders_products.Status = 'Active' 
												INNER JOIN sl_customers ON sl_orders.ID_customers = sl_customers.ID_customers 
												ORDER BY sl_orders.ID_orders DESC;");
		}else{
			(!$in{'nh'}) and ($in{'nh'}=1);
			$first = ($in{'nh'} - 1) * $usr{'pref_maxh'};			
			($va{'pageslist'},$qs) = &pages_list($in{'nh'},"/cgi-bin/mod/$usr{'application'}/dbman",$va{'matches'},$usr{'pref_maxh'});

			$sth = &Do_SQL("SELECT DISTINCT sl_orders_products.ID_orders,sl_customers.ID_customers, CONCAT(FirstName,' ',LastName1) AS Name,
													ShpDate, sl_orders.Date, sl_orders.Status  
													FROM sl_orders_products INNER JOIN sl_orders ON sl_orders_products.ID_orders = sl_orders.ID_orders AND
													RIGHT(ID_products,6) = '$in{'id_products'}' AND sl_orders_products.Status = 'Active' 
													INNER JOIN sl_customers ON sl_orders.ID_customers = sl_customers.ID_customers 
													ORDER BY sl_orders.ID_orders DESC LIMIT $first,$usr{'pref_maxh'};");
		}

		while ($rec = $sth->fetchrow_hashref){
			($rec->{'ShpDate'} eq '0000-00-00') and ($rec->{'ShpDate'} = '');
			$d = 1 - $d;
			$va{'searchresults'} .= "<tr bgcolor='$c[$d]'>\n";
			$va{'searchresults'} .= "   <td class='smalltext'><a href=\"/cgi-bin/mod/$usr{'application'}/dbman?cmd=opr_orders&view=$rec->{'ID_orders'}\">$rec->{'ID_orders'}</a></td>\n";
			$va{'searchresults'} .= "   <td class='smalltext'><a href=\"/cgi-bin/mod/$usr{'application'}/dbman?cmd=opr_customers&view=$rec->{'ID_customers'}\">$rec->{'Name'}</a></td>\n";
			$va{'searchresults'} .= "   <td class='smalltext'>$rec->{'Date'}</td>\n";
			$va{'searchresults'} .= "   <td class='smalltext'>$rec->{'ShpDate'}</td>\n";
			$va{'searchresults'} .= "   <td class='smalltext'>$rec->{'Status'}</td>\n";
			$va{'searchresults'} .= "</tr>\n";
		}
	}else{
		$va{'pageslist'} = 1;
		$va{'searchresults'} = qq|
			<tr>
				<td colspan='6' align="center">|.&trans_txt('search_nomatches').qq|</td>
			</tr>\n|;
	}


}


#############################################################################
#############################################################################
#   Function: tab16 : INVENTORY
#
#       Es: Muestra PO´S relacionados al productos
#       En: English description if possible
#
#
#    Created on: 26/10/2012  13:20:10
#
#    Author: Enrique Peña
#
#    Modifications:
#
#        - Modified on *26/11/2012* by _Enrique Peña_ : Sacar este listado con las partes que integran la oferta, mostrar el mismo icono que esta en la pantalla de Skus, donde al hacer click se muestra el inventario del SKU
#
#   Parameters:
#
#      - id_products Id del producto
#
#  Returns:
#      - Muestra listado con Inventario de las partes del producto
#
#   See Also:
#
#
#
sub load_tabs7 {
##############################################################
##############################################################
	my (@c) = split(/,/,$cfg{'srcolors'});
	$sth = &Do_SQL("SELECT count(*)
			FROM sl_skus_parts
			INNER JOIN sl_products ON ID_products = RIGHT(ID_sku_products,6)
			INNER JOIN sl_parts USING(ID_parts)
			WHERE sl_products.ID_products = '$in{'id_products'}'
			GROUP BY ID_parts");
	$va{'matches'} = $sth->fetchrow;
	if ($va{'matches'}>0){
		(!$in{'nh'}) and ($in{'nh'}=1);
		$first = ($in{'nh'} - 1) * $usr{'pref_maxh'};			
		($va{'pageslist'},$qs) = &pages_list($in{'nh'},"/cgi-bin/mod/$usr{'application'}/dbman",$va{'matches'},$usr{'pref_maxh'});
		
		$sth = &Do_SQL("SELECT sl_parts.ID_parts , sl_parts.Name, (SELECT SUM(Quantity) FROM sl_warehouses_location  WHERE ID_products= 400000000+ID_parts) AS TOTAL
				FROM sl_skus_parts
				INNER JOIN sl_products ON ID_products = RIGHT(ID_sku_products,6)
				INNER JOIN sl_parts USING(ID_parts)
				WHERE sl_products.ID_products = '$in{'id_products'}'
				GROUP BY ID_parts ");
		while ($rec = $sth->fetchrow_hashref){
			$d = 1 - $d;
			$va{'searchresults'} .= "<tr bgcolor='$c[$d]'>\n";
			$va{'searchresults'} .= "   <td class='smalltext'><a href=\"/cgi-bin/mod/$usr{'application'}/dbman?cmd=mer_parts&view=$rec->{'ID_parts'}\">$rec->{'ID_parts'}</a></td>\n";
			$va{'searchresults'} .= "   <td class='smalltext' width='33%'>$rec->{'Name'}</a></td>\n";
			$va{'searchresults'} .= " <td class='smalltext' width='33%' onmouseover='m_over(this)' onmouseout='m_out(this)' >";
			$va{'searchresults'} .= " <span class='help_on'>$rec->{'TOTAL'} Units</span>";
			$va{'searchresults'} .= " <a class=\"scroll\"  href=\"#ajax_inv$in{'id_products'}\" onClick=\"popup_show('ajax_windows', 'ajax_drag', 'ajax_exit', 'element-right', 0, 0,'ajax_inv$in{'id_products'}');loadDoc('/cgi-bin/common/apps/ajaxbuild?ajaxbuild=inventory&id_products=$rec->{'ID_parts'}&cols=ID,Choices,Vendor SKU,Warehouse,Qty');\" >";
			$va{'searchresults'} .= " <img class=\"scroll\" id='ajax_inv$in{'id_products'}' src=\"[va_imgurl]/[ur_pref_style]/b_view.png\" title='More Info' alt='More Info' border='0'></a></td>\n";
			$va{'searchresults'} .= "</tr>\n";
		}
	}else{
		$va{'pageslist'} = 1;
		$va{'searchresults'} = qq|
			<tr>
				<td colspan='6' align="center">|.&trans_txt('search_nomatches').qq|</td>
			</tr>\n|;
	}

	
}


sub load_tabs8 {
# --------------------------------------------------------
##############################################
## tab7 : ANALYSIS
##############################################

	### ADD			
	if ($in{'action'}){
		if (!$in{'source'} or !$in{'price'} or $in{'price'} =~ /[a-zA-Z]/){
			$va{'tabmessages'} = &trans_txt('reqfields');
			(!$in{'source'}) and ($error{'source'} = &trans_txt('required'));
			(!$in{'price'}) and ($error{'price'} = &trans_txt('required'));
			($in{'price'} =~ /[a-zA-Z]/) and ($error{'price'} = &trans_txt('invalid'));
		}else{
			my ($sth) = &Do_SQL("SELECT COUNT(*) FROM sl_products_panalisis WHERE ID_products='$in{'id_products'}' AND Source='$in{'source'}'");
			if ($sth->fetchrow >0){
				$error{'source'} = &trans_txt('repeated');
			}else{
				$va{'tabmessages'} = &trans_txt('mer_products_panadded');
				my ($sth) = &Do_SQL("INSERT INTO sl_products_panalisis SET ID_products='$in{'id_products'}',Source='$in{'source'}',Price='$in{'price'}',Date=Curdate(),Time=NOW(),ID_admin_users='$usr{'id_admin_users'}'");
				delete($in{'source'});
				delete($in{'price'});
				&auth_logging('mer_products_panadded',$in{'id_products'});
				$in{'tabs'} = 1;
			}
		}

	## DROP
	}elsif ($in{'drop'}){
		my ($sth) = &Do_SQL("DELETE FROM sl_products_panalisis WHERE ID_products_panalisis='$in{'drop'}'");
		$va{'tabmessages'} = &trans_txt('mer_products_pandel');
		&auth_logging('mer_products_pandel',$in{'id_products'});
		$in{'tabs'} = 1;
	}

	## Categs
	my (@c) = split(/,/,$cfg{'srcolors'});
	my ($sth) = &Do_SQL("SELECT COUNT(*) FROM sl_products_panalisis WHERE ID_products='$in{'id_products'}'");
	$va{'matches'} = $sth->fetchrow;
	if ($va{'matches'}>0){
		my ($sth) = &Do_SQL("SELECT * FROM sl_products_panalisis WHERE ID_products='$in{'id_products'}' ORDER BY Source;");
		while ($rec = $sth->fetchrow_hashref){
			$d = 1 - $d;
			$va{'searchresults'} .= "<tr bgcolor='$c[$d]'>\n";
			$va{'searchresults'} .= "   <td class='smalltext'><a href='/cgi-bin/mod/$usr{'application'}/dbman?cmd=$in{'cmd'}&view=$in{'id_products'}&tab=7&drop=$rec->{'ID_products_panalisis'}'><img src='$va{'imgurl'}/$usr{'pref_style'}/b_drop.png' title='Drop' alt='' border='0'></a></td>\n";
			$va{'searchresults'} .= "   <td class='smalltext' width='85%'>$rec->{'Source'}</td>\n";
			$va{'searchresults'} .= "   <td class='smalltext' align='right' nowrap>".&format_price($rec->{'Price'})."</td>\n";
			$va{'searchresults'} .= "</tr>\n";
		}
	}else{
		$va{'searchresults'} = qq|
			<tr>
				<td colspan='3' align="center">|.&trans_txt('search_nomatches').qq|</td>
			</tr>\n|;
	}


}


sub load_tabs9 {
# --------------------------------------------------------
##############################################
## tab9 : STATICS
##############################################


	## Tables Header/Titles
	$va{'keyname'} = '';
}


sub load_tabs10 {
# --------------------------------------------------------
##############################################
## tab10 : RMAs
##############################################
#Notes: Sets?

	my (@c) = split(/,/,$cfg{'srcolors'});
	my ($sth) = &Do_SQL("SELECT COUNT(*) FROM sl_returns INNER JOIN sl_orders_products 
											ON sl_orders_products.ID_orders_products = sl_returns.ID_orders_products
											AND RIGHT( ID_products, 6 ) = '$in{'id_products'}' AND Quantity < 0
											GROUP BY sl_orders_products.ID_orders_products  ");
	$va{'matches'} = 0;
	$va{'matches'} = $sth->fetchrow if ($sth->fetchrow);
	if ($va{'matches'}>0){
		if ($in{'print'}){
			$sth = &Do_SQL("SELECT ID_orders,Type,ProdCondition,merAction,sl_returns.Date FROM sl_returns INNER JOIN sl_orders_products 
												ON sl_orders_products.ID_orders_products = sl_returns.ID_orders_products
												AND RIGHT( ID_products, 6 ) = '$in{'id_products'}' AND Quantity < 0
												GROUP BY sl_orders_products.ID_orders_products
												ORDER BY sl_returns.Date DESC");
		}else{
			(!$in{'nh'}) and ($in{'nh'}=1);
			$first = ($in{'nh'} - 1) * $usr{'pref_maxh'};			
			($va{'pageslist'},$qs) = &pages_list($in{'nh'},"/cgi-bin/mod/$usr{'application'}/dbman",$va{'matches'},$usr{'pref_maxh'});
			$sth = &Do_SQL("SELECT ID_orders,Type,ProdCondition,merAction,sl_returns.Date FROM sl_returns INNER JOIN sl_orders_products 
													ON sl_orders_products.ID_orders_products = sl_returns.ID_orders_products
													AND RIGHT( ID_products, 6 ) = '$in{'id_products'}' AND Quantity < 0
													GROUP BY sl_orders_products.ID_orders_products
													ORDER BY sl_returns.Date DESC LIMIT $first,$usr{'pref_maxh'};");
		}

		while ($rec = $sth->fetchrow_hashref){
			$d = 1 - $d;
			$va{'searchresults'} .= "<tr bgcolor='$c[$d]'>\n";
			$va{'searchresults'} .= "   <td class='smalltext'><a href=\"/cgi-bin/mod/$usr{'application'}/dbman?cmd=opr_orders&view=$rec->{'ID_orders'}\">$rec->{'ID_orders'}</a></td>\n";
			$va{'searchresults'} .= "   <td class='smalltext'>$rec->{'Type'}</td>\n";
			$va{'searchresults'} .= "   <td class='smalltext'>$rec->{'ProdCondition'}</td>\n";
			$va{'searchresults'} .= "   <td class='smalltext'>$rec->{'merAction'}</td>\n";
			$va{'searchresults'} .= "   <td class='smalltext'>$rec->{'Date'}</td>\n";
			$va{'searchresults'} .= "</tr>\n";
		}
	}else{
		$va{'pageslist'} = 1;
		$va{'searchresults'} = qq|
			<tr>
				<td colspan='6' align="center">|.&trans_txt('search_nomatches').qq|</td>
			</tr>\n|;
	}

}


sub load_tabs13 {
# --------------------------------------------------------
##############################################
## tab13 : Products prior (Ecommerce
##############################################


	use Data::Dumper;
	use HTML::Entities;

	## update
	if ($in{'action'}){
		if($in{'add_new'}){
			
			if ($in{'status'} eq 'On-Air' and $in{'web_available'} eq 'No') {
				$sth = &Do_SQL("UPDATE sl_products SET web_available='Yes' WHERE ID_products = '$in{'id_products'}'");
			}  # End if On-Air

			my $sth = &Do_SQL("INSERT IGNORE INTO sl_products_prior (ID_products,Model,Name,PayType,ID_packingopts, SmallDescription,Description,SPrice,FPPrice,Flexipago,Status,web_available,BelongsTo,valid_from,valid_to,Date,Time,ID_admin_users)
								SELECT ID_products,Model,Name,PayType,ID_packingopts,SmallDescription,Description,SPrice,FPPrice,Flexipago,Status,web_available,'$in{'new_belongsto'}','0000-00-00','0000-00-00',CURDATE(),CURTIME(),$usr{'id_admin_users'}
								FROM sl_products
								WHERE ID_products = '$in{'id_products'}';");

            #init promo price
            my $id_products_prior = $sth->{'mysql_insertid'};
            $sth = &Do_SQL("UPDATE sl_products_prior SET SPrice1=0.01, SPrice2=SPrice, SPrice3=SPrice, SPrice4=SPrice
            				/*
            				, ID_packingopts=9
            				, ID_packingopts2=ID_packingopts
            				, ID_packingopts3=ID_packingopts
            				, ID_packingopts4=ID_packingopts
            				*/
            				, SPriceName = IF(LENGTH(SPriceName) > 2, SPriceName,'Normal'),
							SPrice1Name = IF(LENGTH(SPrice1Name) > 2, SPrice1Name,'Prueba Gratis'),
							SPrice2Name = IF(LENGTH(SPrice2Name) > 2, SPrice2Name,'Especial Correo'),
							SPrice3Name = IF(LENGTH(SPrice3Name) > 2, SPrice3Name,'Revisita'),
							SPrice4Name = IF(LENGTH(SPrice4Name) > 2, SPrice4Name,'Facebook') 
							WHERE ID_products_prior = '$id_products_prior'");

			my ($sth) = &Do_SQL("INSERT IGNORE INTO sl_products_w(ID_products,Name,BelongsTo,Date,Time,ID_admin_users)
			SELECT ID_products, Name,'$in{'new_belongsto'}',CURDATE(),CURTIME(),$usr{'id_admin_users'}
			FROM sl_products WHERE ID_products = '$in{'id_products'}';");
                        
			&set_urlfixed_ecommerce;
			&auth_logging('mer_products_prioradded',$in{'id_products'});
		}  # End if add_new


		## Updating Product Data in sl_products_prior for Ecommerce Purposes
		if($in{'upd_item'}){
			my $id_products_prior = int($in{'upd_item'});
			my $paytype = $in{'prior_paytype'};
			(!$in{'prior_flexipago'}) and ($in{'prior_flexipago'}=1);
			(!$in{'prior_downpayment'}) and ($in{'prior_downpayment'}=1);
			
               	my $asin = $in{'asin'} ne '' ? ", Asin='".&filter_values($in{'asin'})."'" : '';
               	my $amazonsku = $in{'amazonsku'} ne '' ? ", Amazonsku='".&filter_values($in{'amazonsku'})."'" : '';
               	my $adwordsfile = $in{'adwordsfile'} ne '' ? ", Adwords_file='".&filter_values($in{'adwordsfile'})."'" : '';
               
			# my ($sth)=&Do_SQL("UPDATE sl_products_prior SET model = '".&filter_values($in{'prior_model'})."', name = '".&filter_values($in{'prior_name'})."', paytype = '".&filter_values($paytype)."', fpprice = '".&filter_values($in{'prior_fpprice'})."', Downpayment = '".&filter_values($in{'prior_downpayment'})."', flexipago = '".int($in{'prior_flexipago'})."', ID_services_related = '".int($in{'prior_id_noninventory_related'})."' $asin $amazonsku $adwordsfile WHERE ID_products_prior = '".$id_products_prior."';");
			my ($sth)=&Do_SQL("UPDATE sl_products_prior SET model = '".&filter_values($in{'prior_model'})."', name = '".&filter_values($in{'prior_name'})."', paytype = '".&filter_values($paytype)."', fpprice = '".&filter_values($in{'prior_fpprice'})."', Downpayment = '".&filter_values($in{'prior_downpayment'})."', flexipago = '".int($in{'prior_flexipago'})."' $asin $amazonsku $adwordsfile WHERE ID_products_prior = '".$id_products_prior."';");

			if($sth->rows() == 1){
				my ($sth) = &Do_SQL("INSERT INTO sl_products_notes SET ID_products='$in{'id_products'}',Notes='Ecommerce Data Edited\nWebsite: $in{'belongsto'}',Type='Low',Date=CURDATE(),Time=CURTIME(),ID_admin_users='$usr{'id_admin_users'}'");
				$in{'db'}='sl_products';
				$in{'cmd'}='mer_products';
				$va{'message'} .= 'Ecommerce Data Updated';
			}else{
				$va{'message'} .= "error:INSERT INTO sl_products_prior_notes SET ID_products_prior='$id_products_prior',Notes='model ".$in{'model'}." edited',Type='Low',Date=CURDATE(),Time=CURTIME(),ID_admin_users='$usr{'id_admin_users'}'";
			}
			 
			delete($in{'upd_item'});
		}  # End if upd_item


		## Update URL Product Name
		if($in{'upd_links'}){

			@pairs = split(/&/, $ENV{'QUERY_STRING'});
			foreach $pair (@pairs) {
				if ( $pair =~ /^ID_products_w_/ ) {
					($id_products_w, $name_w) = split(/\=/,$pair);
					$id_products_w =~ s/ID_products_w_//;
					$name_w =~ s/\+/-/g;
					$str_sql = "UPDATE sl_products_w SET Name = '".&filter_values($name_w)."' where ID_products_w = $id_products_w";
					$sth=&Do_SQL( $str_sql );
				}  # End if
			}  # End foreach
			my ($sth) = &Do_SQL("INSERT INTO sl_products_notes SET ID_products='$in{'id_products'}',Notes='Ecommerce Links Edited\nWebsite: $in{'belongsto'}',Type='Low',Date=CURDATE(),Time=CURTIME(),ID_admin_users='$usr{'id_admin_users'}'");

			if ($in{'another_name'}) {
				$in{'another_name'} =~ s/ /-/g;
				
				my ($sth)= &Do_SQL("INSERT IGNORE INTO sl_products_w (id_products, name, belongsto, date, time, id_admin_users) values ('".$in{'view'}."', '".&filter_values($in{'another_name'})."', '".$in{'belongsto'}."', CURDATE(), CURTIME(), '".$usr{'id_admin_users'}."');");
				my ($sth)= &Do_SQL("INSERT INTO sl_products_notes SET ID_products='$in{'id_products'}',Notes='Ecommerce Link Added\nWebsite: $in{'belongsto'}',Type='Low',Date=CURDATE(),Time=CURTIME(),ID_admin_users='$usr{'id_admin_users'}'");
			}  # End if another_name

			&set_urlfixed_ecommerce;
			&auth_logging('mer_products_ecommerce_linkupd',$in{'id_products'});
			delete($in{'upd_links'});

		}  # End if upd_links


		## Delete Product will take it off from website view
		if($in{'drop_item'}){
			my $sth = &Do_SQL("DELETE FROM sl_products_prior WHERE ID_products = '$in{'drop_item'}' AND BelongsTo = '$in{'belongsto'}'");		
			my $sth = &Do_SQL("DELETE FROM sl_products_w WHERE ID_products = '$in{'drop_item'}' AND BelongsTo = '$in{'belongsto'}'");

			my ($sth) = &Do_SQL("INSERT INTO sl_products_notes SET ID_products='$in{'id_products'}',Notes='Ecommerce Data Dropped\nWebsite: $in{'belongsto'}',Type='Low',Date=CURDATE(),Time=CURTIME(),ID_admin_users='$usr{'id_admin_users'}'");

			&auth_logging('mer_products_ecommerce_dropped',$in{'id_products'});
			delete($in{'drop_item'});

		}  # End if drop_item


		## Delete Link for a website
		if($in{'drop_link'}){
			my $sth = &Do_SQL("DELETE FROM sl_products_w WHERE ID_products_w = '$in{'drop_link'}';");
			my ($sth) = &Do_SQL("INSERT INTO sl_products_notes SET ID_products='$in{'id_products'}',Notes='Ecommerce Link Dropped\nWebsite: $in{'belongsto'}',Type='Low',Date=CURDATE(),Time=CURTIME(),ID_admin_users='$usr{'id_admin_users'}'");

			&auth_logging('mer_products_ecommerce_linkdropped',$in{'id_products'});
			delete($in{'drop_link'});

		}  # End if drop_item
        
        ## Updating Product Description
        if($in{'upd_desc'}){
            my $id_products_prior = int($in{'upd_desc'});
            my $qd;

            ($in{'description_fck'}) and ($qd .= " Description ='".&filter_values($in{'description_fck'})."',");
            ($in{'smalldescription_sp_fck'}) and ($qd .= " SmallDescription ='".&filter_values($in{'smalldescription_sp_fck'})."',");
            ($in{'smalldescription_en_fck'}) and ($qd .= " SmallDescription_en ='".&filter_values($in{'smalldescription_en_fck'})."',");
            chop($qd);	

            my ($sth)=&Do_SQL("UPDATE sl_products_prior SET $qd WHERE ID_products_prior = '".$id_products_prior."';");
            my ($sth) = &Do_SQL("INSERT INTO sl_products_notes SET ID_products='$in{'id_products'}',Notes='Ecommerce Description Updated\nWebsite: $in{'belongsto'}',Type='Low',Date=CURDATE(),Time=CURTIME(),ID_admin_users='$usr{'id_admin_users'}'");
            &auth_logging('mer_products_ecommerce_descupd',$in{'id_products'});
            delete($in{'upd_desc'});
        }  # End if upd_desc
        
        ## Updating Product Ecommerce Prices
        if($in{'upd_sprice'}){
            my $id_products_prior = int($in{'upd_sprice'});

            my $sprice =  $in{'psprice'}  ne '' ? " SPrice=".&filter_values($in{'psprice'}) : "SPrice='' ";
            my $sprice1 = $in{'psprice1'} ne '' ? ", SPrice1=".&filter_values($in{'psprice1'}) : '';
            my $sprice2 = $in{'psprice2'} ne '' ? ", SPrice2=".&filter_values($in{'psprice2'}) : '';
            my $sprice3 = $in{'psprice3'} ne '' ? ", SPrice3=".&filter_values($in{'psprice3'}) : '';
            my $sprice4 = $in{'psprice4'} ne '' ? ", SPrice4=".&filter_values($in{'psprice4'}) : '';
            
            my $sprice_name  = $in{'pspricename'}  ne '' ? ", SPriceName='".&filter_values($in{'pspricename'})."'" : '';
            my $sprice_name1 = $in{'psprice1name'} ne '' ? ", SPrice1Name='".&filter_values($in{'psprice1name'})."'" : '';
            my $sprice_name2 = $in{'psprice2name'} ne '' ? ", SPrice2Name='".&filter_values($in{'psprice2name'})."'" : '';
            my $sprice_name3 = $in{'psprice3name'} ne '' ? ", SPrice3Name='".&filter_values($in{'psprice3name'})."'" : '';
            my $sprice_name4 = $in{'psprice4name'} ne '' ? ", SPrice4Name='".&filter_values($in{'psprice4name'})."'" : '';
            
            my $prior_id_packingopts = $in{'prior_id_packingopts'} ne '' ? ", ID_packingopts=".&filter_values($in{'prior_id_packingopts'}) : '';
            my $prior_id_packingopts1 = $in{'prior_id_packingopts1'} ne '' ? ", ID_packingopts1=".&filter_values($in{'prior_id_packingopts1'}) : '';
            my $prior_id_packingopts2 = $in{'prior_id_packingopts2'} ne '' ? ", ID_packingopts2=".&filter_values($in{'prior_id_packingopts2'}) : '';
            my $prior_id_packingopts3 = $in{'prior_id_packingopts3'} ne '' ? ", ID_packingopts3=".&filter_values($in{'prior_id_packingopts3'}) : '';
            my $prior_id_packingopts4 = $in{'prior_id_packingopts4'} ne '' ? ", ID_packingopts4=".&filter_values($in{'prior_id_packingopts4'}) : '';
            $prior_id_packingopts .= $prior_id_packingopts1 . $prior_id_packingopts2 . $prior_id_packingopts3 . $prior_id_packingopts4;

            my ($sth)=&Do_SQL("UPDATE sl_products_prior SET $sprice $sprice1 $sprice2 $sprice3 $sprice4 $sprice_name $sprice_name1 $sprice_name2 $sprice_name3 $sprice_name4 $prior_id_packingopts WHERE ID_products_prior = '".$id_products_prior."';");
            my ($sth) = &Do_SQL("INSERT INTO sl_products_notes SET ID_products='$in{'id_products'}',Notes='Ecommerce Prices Updated\nWebsite: $in{'belongsto'}',Type='Low',Date=CURDATE(),Time=CURTIME(),ID_admin_users='$usr{'id_admin_users'}'");
            &auth_logging('mer_products_ecommerce_pricesupd',$in{'id_products'});
            delete($in{'upd_sprice'});
        }  # End if upd_sprice
      
      
		delete($in{'action'});
	}  # End if action


	## Listing
	$str_sql = "SELECT * FROM
(SELECT
	ID_products_prior,
	IF(sl_products_prior.SPrice > 0,sl_products_prior.SPrice,sl_products.SPrice)as SPrice,
	IF(NOT ISNULL(sl_products_w.Title) AND sl_products_w.Title!='',sl_products_w.Title,'Otro')as Title,
	IF(NOT ISNULL(sl_products_prior.Name) AND sl_products_prior.Name!='',sl_products_prior.Name,sl_products.Name) as Name,
	IF(NOT ISNULL(sl_products_prior.Model) AND sl_products_prior.Model!='',sl_products_prior.Model,sl_products.Model) as Model,
	IF(sl_products_prior.Flexipago > 0,sl_products_prior.Flexipago,sl_products.Flexipago) as Flexipago,
	IF(sl_products_prior.FPPrice > 0,sl_products_prior.FPPrice,sl_products.FPPrice) as FPPrice,
	IF(NOT ISNULL(sl_products_prior.PayType) AND sl_products_prior.PayType!='',sl_products_prior.PayType,sl_products.PayType) as PayType,
	IF(sl_products_prior.ID_packingopts > 0,sl_products_prior.ID_packingopts,sl_products.ID_packingopts) as ID_packingopts,
	/*IF(sl_products_prior.Downpayment > 0,sl_products_prior.Downpayment,sl_products.Downpayment) as Downpayment,*/
	valid_from, valid_to, sl_products_w.BelongsTo
FROM
	sl_products
INNER JOIN
	sl_products_prior
ON(sl_products.ID_products=sl_products_prior.ID_products)
INNER JOIN
	sl_products_w
ON(sl_products.ID_products=sl_products_w.ID_products)
AND sl_products_prior.BelongsTo = sl_products_w.BelongsTo
WHERE
	sl_products.ID_products = '$in{'id_products'}' AND sl_products.Status NOT IN('Testing','Inactive')
	GROUP BY sl_products_w.BelongsTo
)AS sl_products;";

	$sth=&Do_SQL($str_sql);
	$va{'matches'} = $sth->rows;

	if ($va{'matches'}>0){
		(!$in{'nh'}) and ($in{'nh'}=1);
		my $first = ($in{'nh'} - 1) * $usr{'pref_maxh'};
		($va{'pageslist'},$qs) = &pages_list($in{'nh'},"/cgi-bin/mod/$usr{'application'}/dbman",$va{'matches'},$usr{'pref_maxh'});

		my (@c) = split(/,/,$cfg{'srcolors'});

		## Using rel='#overlay' for anchor makes overlay popup
		while($rec=$sth->fetchrow_hashref()) {
			$d = 1 - $d;
			my $packingopts =  &format_price(&load_name('sl_packingopts','ID_packingopts',$rec->{'ID_packingopts'},'Shipping'),2);
			$va{'searchresults'} .= "<tr bgcolor='$c[$d]'>\n";
			$va{'searchresults'} .= "   <td class='smalltext' nowrap>";
			$va{'searchresults'} .= "		<a href=\"/cgi-bin/mod/$usr{'application'}/dbman?cmd=mer_products&view=$in{'id_products'}&tab=$in{'tab'}&action=1&belongsto=$rec->{'BelongsTo'}&drop_item=$in{'id_products'}\"><img src='$va{'imgurl'}/$usr{'pref_style'}/b_drop.png' alt='Delete' title='Delete' border='0'></a>&nbsp;&nbsp;";
			$va{'searchresults'} .= "   	 	<a href='/cgi-bin/common/apps/ajaxbuild?tab=$in{'tab'}&ajaxbuild=overlay_products_prior&id_row=$in{'id_products'}&belongsto=$rec->{'BelongsTo'}' rel='#overlay' style='text-decoration:none'><img src='$va{'imgurl'}/$usr{'pref_style'}/b_edit.png' alt='Edit' title='Edit' border='0'></a>&nbsp;&nbsp;";
			$va{'searchresults'} .= "        <a href='/cgi-bin/common/apps/ajaxbuild?tab=$in{'tab'}&ajaxbuild=overlay_products_prior_desc&id_row=$in{'id_products'}&belongsto=$rec->{'BelongsTo'}' rel='#overlay' style='text-decoration:none'><img src='$va{'imgurl'}/$usr{'pref_style'}/b_edit.png' alt='Edit Description' title='Edit Description' border='0'></a>&nbsp;&nbsp;";

			## URL Link Names
			if(lc($rec->{'BelongsTo'}) =~ /innovashop|naturaliv|naturistashop|allnatpro/) {
				$va{'searchresults'} .= "   <a href='/cgi-bin/common/apps/ajaxbuild?tab=$in{'tab'}&ajaxbuild=overlay_products_prior_links&id_row=$in{'id_products'}&belongsto=$rec->{'BelongsTo'}' rel='#overlay' style='text-decoration:none'><img src='$va{'imgurl'}/$usr{'pref_style'}/web_only.gif' alt='Link' title='Link' border='0'></a>";
			}
			
			$va{'searchresults'} .= "   &nbsp;&nbsp;<a href='/cgi-bin/common/apps/ajaxbuild?tab=$in{'tab'}&ajaxbuild=overlay_products_prior_promo&id_row=$in{'id_products'}&belongsto=$rec->{'BelongsTo'}' rel='#overlay' style='text-decoration:none'><img src='$va{'imgurl'}/$usr{'pref_style'}/b_adjtotals.gif' alt='Prices' title='Prices' border='0'></a>";
			$va{'searchresults'} .= qq|	&nbsp;&nbsp;<a href="/cgi-bin/common/apps/ajaxbuild?tab=$in{'tab'}&ajaxbuild=overlay_products_prior_links&id_row=$in{'id_products'}&belongsto=$rec->{'BelongsTo'}" rel="#overlay" style="text-decoration:none"><img src="$va{'imgurl'}/$usr{'pref_style'}/web_only.gif" alt="Link" title="Link" border="0"></a>|;

			$va{'searchresults'} .= "\n		</td>\n";
			$va{'searchresults'} .= "   <td class='smalltext' width='120px'><span id='BelongsTo'>$rec->{'BelongsTo'}</span>\n";
			$va{'searchresults'} .= "   <td class='smalltext' width='120px'><span id='SPrice'>".&format_price($rec->{'SPrice'})."</span></td>\n";
			$va{'searchresults'} .= "   <td class='smalltext' width='120px'><span id='SPrice1'>".&format_price($rec->{'SPrice1'})."</span></td>\n";
			$va{'searchresults'} .= "   <td class='smalltext' width='120px'><span id='FPPrice'>".&format_price($rec->{'FPPrice'})."</span></td>\n";
			$va{'searchresults'} .= "   <td class='smalltext' width='120px'><span id='Flexipago'>".$rec->{'Flexipago'}."</span></td>\n";
			$va{'searchresults'} .= "   <td class='smalltext' width='120px' nowrap><span id='ID_packingopts'>".$packingopts."</span></td>\n";
			$va{'searchresults'} .= "   <td  width='120px' id='from_date'>  <span id='valid_from'>".$rec->{'valid_from'}."</span></td>\n";
			$va{'searchresults'} .= "   <td  width='120px' id='to_date'>    <span id='valid_to'>".$rec->{'valid_to'}."</span></td>\n";
			$va{'searchresults'} .= "</tr>\n";
		}  # End while

	}else{
		$va{'pageslist'} = 1;
		$va{'searchresults'} = qq|
			<tr>
				<td colspan='8' align="center">|.&trans_txt('search_nomatches').qq|</td>
			</tr>\n|;
	}  # End if str_sql


}

#############################################################################
#############################################################################
#   Function: tab14 : PRICES
#
#       Es: Listado de Precios del Producto
#       En: Product Price List
#
#
#    Created on: 12/09/2013  13:20:10
#
#    Author: Alejandro Diaz
#
#    Modifications:
#
#        - Modified on
#
#   Parameters:
#
#
#
#  Returns:
#      - Muestra listado con precios del producto
#
#   See Also:
#
#
#
sub load_tabs14 {
##############################################################
##############################################################
	my (@c) = split(/,/,$cfg{'srcolors'});
	$sth = &Do_SQL("SELECT count(*)	FROM sl_products_prices WHERE Status='Active' AND ID_products='$in{'id_products'}';");
	$va{'matches'} = $sth->fetchrow;
	if ($va{'matches'}>0){
		(!$in{'nh'}) and ($in{'nh'}=1);
		$first = ($in{'nh'} - 1) * $usr{'pref_maxh'};			
		($va{'pageslist'},$qs) = &pages_list($in{'nh'},"/cgi-bin/mod/$usr{'application'}/dbman",$va{'matches'},$usr{'pref_maxh'});
		
		$sth = &Do_SQL("SELECT Name, Price, Downpayment, AuthCode, FP, PayType, Origins FROM sl_products_prices WHERE Status='Active' AND ID_products='$in{'id_products'}' ORDER BY Name,PayType,Price ASC;");
		while ($rec = $sth->fetchrow_hashref){
			$origins = $rec->{'Origins'};
			$origins =~ s/\|/\,/g;
			$origins = substr($origins,1) if(substr($origins,0,1) eq ',');
			$origins = substr($origins,0,(length($origins)-1)) if(substr($origins,-1) eq ',');
			my $add_sql = ($origins ne '')? " AND ID_salesorigins IN( $origins) ":"";
			my ($sth2) = &Do_SQL("SELECT group_concat(channel)as channel FROM sl_salesorigins WHERE 1 $add_sql ORDER BY channel;");
			my ($consoles)= $sth2->fetchrow();
			$d = 1 - $d;
			$va{'searchresults'} .= "<tr bgcolor='$c[$d]'>\n";
			$va{'searchresults'} .= "  <td class='smalltext'><img src='$va{'imgurl'}/main/list.png' alt='$consoles' title='$consoles' border='0'></td>";
			$va{'searchresults'} .= "   <td class='smalltext'>$rec->{'Name'}</td>\n";
			$va{'searchresults'} .= "   <td class='smalltext'>".$rec->{'PayType'}."</td>\n";
			$va{'searchresults'} .= "   <td class='smalltext' align='right'>".&format_price($rec->{'Price'})."</td>\n";
			$va{'searchresults'} .= "   <td class='smalltext' align='center'>".$rec->{'FP'}."</td>\n";
			$va{'searchresults'} .= "   <td class='smalltext'>".$rec->{'AuthCode'}."</td>\n";
			$va{'searchresults'} .= "</tr>\n";
		}
	}else{
		$va{'pageslist'} = 1;
		$va{'searchresults'} = qq|
			<tr>
				<td colspan='6' align="center">|.&trans_txt('search_nomatches').qq|</td>
			</tr>\n|;
	}
}


sub array_choices {
# --------------------------------------------------------
# Forms Involved: 
# Created on: 9/12/2007 11:29AM
# Last Modified on:
# Last Modified by:
# Author: Carlos Haas
# Description : Helper sub to the build_select_choices sub

	my (@choices);
	my($ID_products,$choice) = @_;
	my ($sth) = &Do_SQL("SELECT DISTINCT $choice FROM sl_skus WHERE ID_products=$ID_products AND $choice !='';");
	$i=0;
	while ($rec = $sth->fetchrow_hashref){		
		@choices[$i++]=$rec->{$choice};
	}
	return @choices;
}

sub check_tblchoices {
# --------------------------------------------------------
# Forms Involved: 
# Created on: 9/12/2007 11:29AM
# Last Modified on:
# Last Modified by:
# Author: Carlos Haas
# Description : Check if the Choice is in the table. Create it if not.
# Last Modified on: 01/12/09 09:18:50
# Last Modified by: MCC C. Gabriel Varela S: Anteriormente dec�a Insert into _sl_skus

	my ($id,@choices) = @_;
	my ($query1,$query2,$add,$upd);
	my ($sth) = &Do_SQL("SELECT ID_sku_products FROM sl_skus WHERE ID_products=$id ORDER BY ID_sku_products DESC;");
	my ($lastid) = substr($sth->fetchrow,0,3)+1;
	($lastid<100) and ($lastid=100);
	my ($test) = 0;
	for (0..3){
		if ($choices[$_]){
			$query1 .= " AND choice".($_+1)."='".&filter_values($choices[$_])."'";
			$query2 .= " AND (choice".($_+1)."='".&filter_values($choices[$_])."' OR choice".($_+1)."='' or ISNULL(choice".($_+1)."))";
			$add   .= " ,choice".($_+1)."='".&filter_values($choices[$_])."'";
		}
	}
	my ($sth) = &Do_SQL("SELECT COUNT(*) FROM sl_skus WHERE ID_products=$id $query2;");
	($test) and ($in{'aaa'} .= "<br>&nbsp;&nbsp;&nbsp; q1)$query1");
	($test) and ($in{'aaa'} .= "<br>&nbsp;&nbsp;&nbsp; q2)$query2");
	if ($sth->fetchrow > 0){
		my ($sth) = &Do_SQL("SELECT COUNT(*) FROM sl_skus WHERE ID_products=$id $query1;");
		if ($sth->fetchrow > 0){
			($test) and ($in{'aaa'} .= "<br>&nbsp;&nbsp;&nbsp; 1)Nothing $query1");
		}else{
			##########my ($sth) = &Do_SQL("INSERT INTO sl_skus SET ID_sku_products='$lastid$id', ID_products='$id' $add ,VendorSKU='".&filter_values($in{'choicesku'})."', IsSet='N',Status='Active',Date=NOW(),Time=NOW(),ID_admin_users='$usr{'id_admin_users'}';");
			(!$test) and (my ($sth) = &Do_SQL("UPDATE sl_skus SET ID_products='$id' $add WHERE ID_products=$id $query2;"));
			(!$test) and (&auth_logging('sku_updated',$id));
			($test) and ($in{'aaa'} .= "<br>&nbsp;&nbsp;&nbsp; 2)update? UPDATE sl_skus SET ID_products='$id' $add WHERE ID_products=$id $query2;");
		}		

	}else{
		my ($sth) = &Do_SQL("SELECT COUNT(*) FROM sl_skus WHERE ID_products=$id $query1;");
		if ($sth->fetchrow > 0){
			(!$test) and (my ($sth) = &Do_SQL("UPDATE sl_skus SET ID_products='$id' $add WHERE ID_products=$id $query2;"));
			(!$test) and (&auth_logging('sku_updated',$id));
			($test) and ($in{'aaa'} .= "<br>&nbsp;&nbsp;&nbsp; 3)update $add WHERE ID_products=$id $query2<br>");
		}else{
			(!$test) and (my ($sth) = &Do_SQL("INSERT INTO sl_skus SET ID_sku_products='$lastid$id', ID_products='$id' $add ,VendorSKU='".&filter_values($in{'choicesku'})."', IsSet='N',Status='Active',Date=Curdate(),Time=NOW(),ID_admin_users='$usr{'id_admin_users'}';"));
			(!$test) and (&auth_logging('sku_added',$sth->{'mysql_insertid'}));
			($test) and ($in{'aaa'} .= "<br>&nbsp;&nbsp;&nbsp; 4)insert $add");
		}
	}
	($test) and ($in{'aaa'} .= "<br>");
}

#############################################################################
#############################################################################
#   Function: tab15 : IMAGES
#
#       Es: Listado de Imagenes
#       En: 
#
#
#    Created on: 19/06/2014  13:20:10
#
#    Author: Arturo Hernandez
#
#    Modifications:
#
#        - Modified on
#
#   Parameters:
#
#
#
#  Returns:
#      - Lista las imagenes
#
#   See Also:
#
#
#
sub load_tabs15 {


##############################################################
##############################################################
	
	# Drop Image
	if($in{'action'}){
		if($in{'drop'} > 0){
			my ($sth) = &Do_SQL("SELECT * FROM sl_products_images WHERE ID_products_images = '".$in{'drop'}."'");
			$row = $sth->fetchrow_hashref;
			&Do_SQL("DELETE FROM sl_products_images WHERE ID_products_images = '$row->{'ID_products_images'}'");
			
		}
	}
	
	my ($sth) = &Do_SQL("SELECT COUNT(*) FROM sl_products_images WHERE ID_products='$in{'id_products'}';");
	$va{'matches'} = $sth->fetchrow;
	if ($va{'matches'}>0){	

		my ($sth) = &Do_SQL("SELECT ID_products_images, ID_products, Image, ListOrder FROM sl_products_images WHERE ID_products='$in{'id_products'}' ORDER BY ListOrder ASC;");
		while (my ($id_products_images, $id_products, $image, $listorder)= $sth->fetchrow() ){
			# $origins =~ s/\|/\,/g;
			# $origins = substr($origins,1) if(substr($origins,0,1) eq ',');
			# $origins = substr($origins,0,(length($origins)-1)) if(substr($origins,-1) eq ',');
			# $kits =~ s/\|/\,/g;
			my ($pathimage) = $cfg{'url_sftp'}.$id_products.'/thumb-'.$image;
			$d = 1 - $d;
			$va{'searchresults'} .= "<tr bgcolor='$c[$d]'>\n";
			$va{'searchresults'} .= " <td class='smalltext'><a href='/cgi-bin/mod/".$usr{'application'}."/dbman?cmd=".$in{'cmd'}."&view=".$in{'id_products'}."&tab=15&action=1&drop=".$id_products_images."'>
			<img src='$va{'imgurl'}/$usr{'pref_style'}/b_drop.png' title='Delete' alt='' border='0'></a>&nbsp;</td>";
			$va{'searchresults'} .= " <td class='smalltext'>$id_products_images</td>\n";
			$va{'searchresults'} .=  qq|<td class='smalltext'><img width="40" src="$pathimage" /></td>\n|;
			$va{'searchresults'} .= " <td class='smalltext'>$listorder</td>\n";
			$va{'searchresults'} .= "</tr>\n";

		}
	}
	

}

sub buildSkusTable{
	my $id_products = shift;
	$skus = &Do_SQL(qq|select * from sl_skus where id_products = $id_products|);
	my $response = '';
	while ($sku = $skus->fetchrow_hashref()) {
		my $linePart;
		$parts = &Do_SQL(qq|select * from sl_skus_parts inner join sl_parts on sl_skus_parts.id_parts = sl_parts.id_parts where id_sku_products = $sku->{'ID_sku_products'}|);


		
		while ($part = $parts->fetchrow_hashref()) {
			$linePart .= qq|
			<div data-id_skus_products="$sku->{'ID_sku_products'}" data-id_part="$part->{'ID_parts'}">
				<input name="qty" value="$part->{'Qty'}">
				
				( <a target="_blank" href="/cgi-bin/mod/admin/dbman?cmd=mer_parts&amp;view=$part->{'ID_parts'}">$part->{'ID_parts'}</a> ) $part->{'Name'} / $part->{'Model'} <img src="/sitimages/aqua/b_drop.png" class="borrarSku">
			</div>|;
		}
		$response .= qq|<tr data-id_skus_products="$sku->{'ID_sku_products'}">
			<td>$sku->{'ID_sku_products'}</td>
			<td>$sku->{'choice1'}</td>
			<td>$sku->{'choice2'}</td>
			<td>$sku->{'choice3'}</td>
			<td>$sku->{'choice4'}</td>
			<td>$linePart</td>
			
			<td><a href="/cgi-bin/common/apps/ajaxbuild?ajaxbuild=editproduct&id_skus_products=$sku->{'ID_sku_products'}&type=parts" class="fancy">
								<img border="0" alt="Add Parts" title="Add Parts" src="/sitimages/default/b_add.png" id="tabs">
								</a></td>
		</tr>|;
	}
	return $response;
}


1;