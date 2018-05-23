##################################################################
#         USER INTERFACE FOR EXTRACTED REPORTS IN BACKGROUND
##################################################################
sub extracted_reports {
## --------------------------------------------------------
	use JSON;

	my $sth = &Do_SQL("SELECT 
							sl_background_reports.cmd, 
							sl_background_reports.parameters,
							sl_background_reports.datetime_init,
							sl_background_reports.datetime_end,
							sl_background_reports.status,
							IF(
								sl_background_reports.cmd LIKE 'repmans%',
								( SELECT Name FROM admin_reports WHERE ID_admin_reports = SUBSTR( sl_background_reports.cmd, 8) ),
                                ( SELECT subcode FROM sl_vars_config WHERE Code = sl_background_reports.cmd)
                            ) name,
							sl_background_reports.file,
							sl_background_reports.date,
							sl_background_reports.time
						FROM 
							sl_background_reports
							INNER JOIN sl_reports_asked_by USING(ID_background_reports)
						WHERE  
							sl_reports_asked_by.id_admin_users = '".$usr{'id_admin_users'}."'
                        GROUP BY
                            sl_background_reports.id_background_reports
						ORDER BY 
							sl_background_reports.status, sl_background_reports.cmd;");

	my $pending, $finished;

	while($rec = $sth->fetchrow_hashref() )
	{
		my $param;
		my $parameters;

		$cad=$rec->{'parameters'};
		$cad =~ s/\r//g;
		$cad =~ s/\n//g;
		$cad =~ s/\t//g;
		$param = decode_json($cad);
		foreach $key ( keys %{$param} ){
			$value = $param->{$key};
			$key =~ s/_/ /g;
			$parameters .= '<tr><td class="keyparam">'.$key.':</td><td class="value">'.$value.'</td></tr>';
		}
		$parameters .= '<tr><td class="keyparam">Requested:</td><td class="value">'.$rec->{'date'}.' '.$rec->{'time'}.'</td></tr>';

		$parameters_table = '<table class="parameters">'.$parameters.'</table>';

		if( $rec->{'status'} =~ /^(New|Processing)$/ )
		{
			$pending .= '
						<div class="each_file">
							<div class="icon">
								<img src="/sitimages/loading-animation.gif" class="icon_files">
							</div>
							<div class="names">
								<div class="Report">'.$rec->{'name'}.'</div>
								<div>
									'.$parameters_table.'
								</div>
							</div>
						</div>';		
		}
		elsif( $rec->{'status'} eq 'Finished' )
		{
			$finished .= '
						<div class="each_file">
							<div class="icon">
                                <a href="/cgi-bin/common/apps/ajaxbuild?ajaxbuild=download_file&name='.$rec->{'file'}.'" download="'.$rec->{'file'}.'">
								    <img src="/sitimages/file.png" class="icon_files">
                                </a>
                            </div>
                            <div class="names">
                                <div class="Report">
                                    '.$rec->{'name'}.'
                                    <img src="/sitimages/aqua/delete.png" class="icon_delete" id="'.$rec->{'file'}.'">
                                </div>
                                <div class="File">'.$rec->{'file'}.'</div>
                                <div>
                                    '.$parameters_table.'
                                </div>
                            </div>
                        </div>';
		}
	}

	$va{'pending'} = $pending;
	$va{'finished'} = $finished;

	print "Content-type: text/html\n\n";
	print &build_page('extracted_reports.html');

}

1;