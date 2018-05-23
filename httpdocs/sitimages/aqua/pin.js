/**
* Pin Up/Down prototype plugin - v alpha 1
* Written by Hatem <hatem@php.net>
*/
function ClickPin(event,field){
	var regex = /pin\.gif$/;
	var img = $('pinv'+field).src;

	if (regex.test(img)) { // Save status
		$('pinv'+field).src ='/sitimages/pin-h.gif';
		
		Cookie.set(field,$(field).value);
	} else { // Release status
		$('pinv'+field).src ='/sitimages/pin.gif';
		Cookie.erase(field);
	}	
}

function SavePin(event,field){
	var regex = /pin\.gif$/;
	var img = $('pinv'+field).src;

	if (!regex.test(img)) { // Save status
		$('pinv'+field).src ='/sitimages/pin-h.gif';
		Cookie.set(field,$(field).value);
	}
}

function AttachPin(field) {
	var vCookie = Cookie.get(field);
	if (!$('pinv'+field)) {
		new Insertion.After(field, '<nobr><img src="/sitimages/pin.gif" id="pinv'+field+'"></nobr> ');
		if (vCookie != null) {
			$(field).value = vCookie;
			$('pinv'+field).src ='/sitimages/pin-h.gif';
		}
		Event.observe('pinv'+field, 'click', ClickPin.bindAsEventListener(this,field));
		Event.observe(field, 'change', SavePin.bindAsEventListener(this,field));
	}
}