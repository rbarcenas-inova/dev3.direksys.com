/* Jquery */
$(document).ready(function() {
	
	/*AJAX Error handler*/
	$(document).ajaxError(function(e, xhr, settings, exception) {
		alert('error in: ' + settings.url + ' \n'+'error:\n' + xhr.responseText );
	}); 
	
	
	$(".scroll").click(function(event){
        //prevent the default action for the click event
        event.preventDefault();
 
        //get the top offset of the target anchor
        var target_top = $($(this).attr('href')).offset().top - 150;
 
        //goto that anchor by setting the body scroll top to anchor top
        $('html, body').animate({scrollTop:target_top}, 1500);
    });


});