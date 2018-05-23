##########################################################
##		OPERATIONS : INVOICES
##########################################################
sub view_opr_invoices {	
	use MIME::Base64 qw( encode_base64 );
	$output="";
	my($id_orders) = @_;
	my (@c) = split(/,/,$cfg{'srcolors'});
	my ($sth) = &Do_SQL("SELECT ID_orders, ID_invoices 
			    FROM cu_invoices_lines WHERE ID_invoices='$in{'id_invoices'}' group by ID_orders;");
	my $rec = $sth->fetchrow_hashref();
	my $id_invoices = $rec->{'ID_invoices'};
	my ($sth) = &Do_SQL("SELECT ID_orders,ID_orders_alias,Pterms,
						shp_Address1,shp_Address2,shp_Address3,
						shp_Urbanization,shp_City,shp_State,shp_Zip 
			    FROM sl_orders WHERE ID_orders='$rec->{'ID_orders'}'");	
	my $rec=$sth->fetchrow_hashref;
	
	#$va{'address'} = qq|
	#		$rec->{'shp_Address1'} <br>
	#		Col: $rec->{'shp_Urbanization'} <br>
	#		Del/Mun: $rec->{'shp_City'}, $rec->{'shp_State'} CP: $rec->{'shp_Zip'} <br>
	#		|;
			
	#my ($sth_terms) = &Do_SQL("SELECT CreditDays 
	#		FROM sl_terms WHERE Name='$rec->{'Pterms'}'");
	#my $rec_terms = $sth_terms->fetchrow_hashref();
			
	$va{'id_order'} = $rec->{'ID_orders'};
	$va{'id_order_alias'} = $rec->{'ID_orders_alias'};
	#$va{'credit_days'} = $rec_terms->{'CreditDays'};
	#$va{'terms'} = $rec->{'Pterms'};
	
	##############################################################################################################
	my ($sth_invoices) = &Do_SQL("SELECT * 
			    FROM cu_invoices WHERE ID_invoices='$in{'id_invoices'}';");
	my $rec_invoices = $sth_invoices->fetchrow_hashref();
	
	$va{'street'} = $rec_invoices->{'customer_shpaddress_street'};
	$va{'urbanization'} = $rec_invoices->{'customer_shpaddress_urbanization'};
	$va{'state'} = $rec_invoices->{'customer_shpaddress_state'};
	$va{'num'} = $rec_invoices->{'customer_shpaddress_num'};
	$va{'district'} = $rec_invoices->{'customer_shpaddress_district'};
	$va{'city'} = $rec_invoices->{'customer_shpaddress_city'};
	$va{'num2'} = $rec_invoices->{'customer_shpaddress_num2'};
	$va{'zipcode'} = $rec_invoices->{'customer_shpaddress_zipcode'};
	$va{'country'} = $rec_invoices->{'customer_shpaddress_country'};
	$va{'batch'} = $rec_invoices->{'batch_num'};
	$va{'serial'} = $rec_invoices->{'doc_serial'};
	$va{'exchange_receipt'} = $rec_invoices->{'exchange_receipt'};
	$va{'conditions'} = $rec_invoices->{'conditions'};
	$va{'credit_days'} = $rec_invoices->{'credit_days'};
	$va{'folio'} = $rec_invoices->{'doc_serial'}.'-'.$rec_invoices->{'doc_num'};
	$va{'uuid'} = $rec_invoices->{'xml_uuid'};
	$va{'xml_certificacion'} = $rec_invoices->{'xml_fecha_certificacion'};
	$va{'metodo'} = $rec_invoices->{'payment_method'};
	$va{'regimen'} = $rec_invoices->{'expediter_fregimen'};

	$va{'label'} = $rec_invoices->{'invoice_type'} == 'ingreso' ? 'Factura' : 'Nota de Crédito';


	my $pdf_name = $rec_invoices->{'doc_serial'}.'_'.$rec_invoices->{'doc_num'};
	# my $link_pdf = $in{'e'} == 4 ? "/finkok/Facturas/?action=showPDF&id_invoices=$in{'id_invoices'}&e=4" : "/cfdi/pages/cfdi/cfdi_doc.php?f=".encode_base64($pdf_name.".pdf")."&id=$in{'id_invoices'}&m=2&readXml=1&e=$in{'e'}";
	if ($rec_invoices->{'Status'} eq 'Certified') {
		my $link_pdf = "/finkok/Facturas/?action=showPDF&id_invoices=$in{'id_invoices'}&e=".$in{'e'};
		my $link_xml = "/finkok/Facturas/?action=downloadXML&id_invoices=$in{'id_invoices'}&e=".$in{'e'};
		$va{'link_to_pdf'} = qq|<a href='$link_pdf' target='_blank'><img src='/cfdi/common/img/pdf.gif' title='Ver PDF' alt='PDF' border='0'></a>|;
		$va{'link_to_xml'} = qq|<a href='$link_xml' target='_blank'><img src='/sitimages/default/xml_dwd.gif' title='Descargar XML' alt='XML' border='0' style='width: 18px;'></a>|;
	}
	##############################################################################################################
	
	
	my ($sth) = &Do_SQL("SELECT COUNT(*)
			    FROM cu_invoices_lines WHERE ID_invoices = '$in{'id_invoices'}'");	
	$va{'matches'} = $sth->fetchrow;
	if ($va{'matches'}>0){
		
		my($subtotal);
		my ($sth) = &Do_SQL("SELECT * 
				FROM cu_invoices_lines WHERE ID_invoices = '$in{'id_invoices'}'");
		while ($rec = $sth->fetchrow_hashref){
			$d = 1 - $d;	
			$va{'results'} .= qq| <tr bgcolor='$c[$d]'><td>
						<font class=info>$rec->{'quantity'}
						</td>
						<td style="border-left:1px solid #333333;">
							<font class=info>$rec->{'measuring_unit'}
						</td>
						<td style="border-left:1px solid #333333;">
							<font class=info>$rec->{'reference_id'} - $rec->{'description'}<br>
							<font class=info>PED: $rec->{'import_declaration_number'}<br>
							<font class=info>FECHA: $rec->{'import_declaration_date'}<br>
							<font class=info>$rec->{'customs'}<br>
							<font class=info>$rec->{'customs_broker'}
						</td>
						<td style="border-left:1px solid #333333;" align=right valign=top>
							<font class=info>|.&format_price($rec->{'unit_price'}).qq|
						</td>
						<td style="border-left:1px solid #333333;" align=right valign=top>
							<font class=info>|.&format_price($rec->{'amount'}).qq|
						</td>
						</tr>|;			
			$subtotal += $rec->{'amount'};
		}

		my ($total_taxes,$tax_name);
		my ($sth) = &Do_SQL("SELECT tax_name,tax_rate, SUM(tax) AS TotalV
					FROM cu_invoices_lines
					WHERE ID_invoices = '$in{'id_invoices'}'
					GROUP BY tax_name,tax_rate
					ORDER BY tax_rate ASC");			
		while ($rec = $sth->fetchrow_hashref){
			$tax_name .= $rec->{'tax_name'}." ".($rec->{'tax_rate'}*100)."% <BR>";
			$tax      .= $rec->{'TotalV'}."<BR>";
			$total_taxes += $rec->{'TotalV'};
		}

		$va{'total'}    	= &format_price($subtotal - $in{'discount'});
		$va{'gran_total'} 	= &format_price(($subtotal - $in{'discount'}) + $total_taxes);
		$va{'subtotal'} 	= &format_price($subtotal);		
		$in{'discount'} 	= &format_price($in{'discount'});			
		$va{'tax_names'} 	= $tax_name;
		$va{'taxes'} 	 	= $tax;
		$va{'taxes_total'}  = &format_price($total_taxes);
	}else{
		$va{'results'} = qq|
			<tr>
				<td colspan='6' align='center'>|.&trans_txt('search_nomatches').qq|</td>
			</tr>\n|;		
	}	
	my ($sth) = &Do_SQL("SELECT OrderNotes 
			    FROM cu_invoices_lines 
			    left join sl_orders using(ID_Orders)
			    WHERE ID_invoices='$in{'id_invoices'}' group by ID_orders;");
	my $rec_notes = $sth->fetchrow_hashref();
	$va{'ordernotes'} = $rec_notes->{'OrderNotes'};
}

1;