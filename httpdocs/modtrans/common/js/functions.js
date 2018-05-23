function showTheHours(theHour) {
	if (theHour > 0 && theHour < 13) { return (theHour)	}
	if (theHour == 0) { return (12)	}
	return (theHour-12)
}

function showZeroFilled(inValue) {
	if (inValue > 9) { return ":" + inValue }
	return ":0" + inValue
}

function showAmPm() {
	if (now.getHours() < 12) { return (" am") }
	return (" pm")
}

function showTheTime(elementId) {
	now = new Date
        $("#"+elementId).html(showTheHours(now.getHours()) +  showZeroFilled(now.getMinutes()) + showAmPm());	
	setTimeout("showTheTime('"+elementId+"')",1000)
}


