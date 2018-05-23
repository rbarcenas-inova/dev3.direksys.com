sub plist_er_opr_polls{
	$query  = "select customer_id, ID_polls_answers, ID_customers, ID_orders, ID_polls_questions, Answer, Status, `Date`, `Time`, ID_admin_users from cu_polls_answers group by customer_id;";
	$count = "select count(DISTINCT customer_id) from cu_polls_answers;";
	my @rs;
	my $results = &Do_SQL($query);
	while($row = $results->fetchrow_hashref()){
		foreach my $key ( @db_cols) {
			push(@rs, $row->{$key});
		}
	}
	$num_row = &Do_SQL($count)->fetchrow();
	use Data::Dumper;
	# print cgierr(Dumper \@rs);
	return ($num_row, @rs);
}

sub plist_opr_polls{
	return &plist_er_opr_polls()
	
}

sub view_opr_polls{
	$query = "select
		cu_polls_questions.Question
		, cu_polls_answers.Answer
	from
		cu_polls_answers inner join cu_polls_questions on
		cu_polls_answers.ID_polls_questions = cu_polls_questions.ID_polls_questions
	where 
		customer_id = '$in{'customer_id'}';";
	use Data::Dumper;
	$rs = &Do_SQL($query);
	$va{'content'} = '<table border="0" cellspacing="0" cellpadding="2" width="100%">';
	while($row = $rs->fetchrow_hashref()){
		if($row->{'Question'} ne 'empresa'){
			$va{'content'} .= qq|<tr>
			<td><strong>$row->{'Question'}</strong></td>
			</tr><tr>
			<td>$row->{'Answer'}</td>
			</tr>			|;
		}
	}
	$va{'content'} .= '</table>';


	
	# cgierr(Dumper $va{'content'});
}

1;