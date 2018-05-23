

function chg_select(Name,Value) {
		for (var f=0; f<self.document.forms.length; f++){
    		for (var i=0; i<self.document.forms[f].length; i++){
        		if (self.document.forms[f].elements[i].name == Name){
                   self.document.forms[f].elements[i].value=Value;
            }
       	}

   	}
}

function chg_chkbox(Name,Value) {
	var aux=Value.split("|");
	for (var x=0; x<aux.length; x++){
		for (var f=0; f<self.document.forms.length; f++){
			for (var i=0; i<self.document.forms[f].length; i++){
				if (self.document.forms[f].elements[i].name == Name && self.document.forms[f].elements[i].value == aux[x]){
					self.document.forms[f].elements[i].click();
				}
			}
		}
  }
}
      
function chg_radio(Name,Value) {
		for (var f=0; f<self.document.forms.length; f++){
    		for (var i=0; i<self.document.forms[f].length; i++){
        		if (self.document.forms[f].elements[i].name.toLowerCase() == Name.toLowerCase() && self.document.forms[f].elements[i].value.toLowerCase() == Value.toLowerCase()){
            		self.document.forms[f].elements[i].click();
        		}
    		}
		}
}
