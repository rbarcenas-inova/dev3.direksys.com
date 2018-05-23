/* Jquery */
$(document).ready(function() {
	
	
	/*AJAX Error handler*/
	$(document).ajaxError(function(e, xhr, settings, exception) {
		alert('error in: ' + settings.url + ' \n'+'error:\n' + xhr.responseText );
	}); 
	

	/* Start Decision Tree Code */
	var count = 0;
	$('#questions').hide();
	$('#answers').hide();
	$('#questions tr:nth-child(2)').attr('id','currow');
	var q1 = $('#currow td:nth-child(2)').html();
	var q3 = '<div id="d' + count + '"><p>' + q1 + '</p>' ;
	var a1 =  $('#currow td:nth-child(3)').html();
	var r1 = q3 + a1 +'</div>';
	$('#showquestion').html(r1);

	$('li').live('click',function(){
		$(this).addClass('selected').siblings().removeClass('selected');
		var target = $(this).attr('id');
		var parid = $(this).parent().parent().attr('id');
		var parnum = parseInt(parid.slice(1,3));
		count = count + 1;
		var ps = $('#showquestion div').length;
		$('#showquestion div').each(function() {
		var divid = $(this).attr('id');
		var divnum = parseInt(divid.slice(1,3));
		if(divnum > parnum)
			$(this).remove();
		})
		$('td' ).each(function(){
		var qnum = $(this).text();
		if(qnum == target) {
			var q = $(this).next('td').html();
			var q2 = '<div  id="d' + count + ' "><p>' + q + '</p>';
			var a = $(this).next('td').next('td').html();
			var qs = $('#showquestion').html();
			var r = qs + q2 + a +'</div>';
			$('#showquestion').html(r);
			window.scrollBy(0,400);
			}
		});
	});
	/* End Decision Tree Code */


	/*
	 * Start Product option chosen
	 * Length(7) - First digit indicates use of overwrite in the configuration file setup.e1.cfg(cc-inbound)
	 * Length(6) - No option sent, means no overwrite needed
	 */
	$('#productshow a').live('click',function(e) {
		var idp = $(this).attr('id');
		if(idp.length == 7){
			$('#overwrite_option').val(idp.substring(0,1));
			idp = idp.substring(1);
		}

		if(idp.length == 6){
			$('#id_products').val(idp);
			$('#productshow').submit();
		}else{
			alert('the product '+id_products+' esta mal formado');
			e.stopPropagation();
			return false;
		}
		
	});
	/* End Product option chosen */

	
});
/* Jquery */