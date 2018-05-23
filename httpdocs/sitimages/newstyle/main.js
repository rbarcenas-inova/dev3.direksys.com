/************************************************************
Nowsee JS
*************************************************************/
var notest = true;
var buildit = true;

function focusOn( field ) {
	field.style.backgroundColor  = "#FFFFCC";
	field.style.cursor = 'pointer';
}
function focusOff( field ) {
	field.style.backgroundColor  = "#FFFFFF";
	//field.style.cursor = '';
}

function m_over(o){
	if (typeof(o.style) != 'undefined'){
		o.style.backgroundColor = '';
		o.style.border = '';
		o.style.cursor = 'pointer';
	}
}
function m_out(o){
	if (typeof(o.style) != 'undefined'){
		o.style.backgroundColor = '';
		o.style.cursor = '';
		o.style.border = '';
	}
}

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

function showTheTime() {
	now = new Date
	showtime.innerHTML = showTheHours(now.getHours()) +  showZeroFilled(now.getMinutes()) + showAmPm();
	setTimeout("showTheTime()",1000)
}

function prnwin(link) {
	//var toprint = '';
	//for (var i=0; i<self.document.sitform.length; i++){
	//	if (self.document.sitform.elements[i].value == 'toprint' && self.document.sitform.elements[i].checked){
	//		toprint += self.document.sitform.elements[i].name + ',';
	//	}
	//}
	win = window.open("","extra","toolbar=no,width=50,height=50,directories=no,status=no,scrollbars=yes,resizable=yes,menubar=no");
	//win.location.href = link + "&toprint=" + toprint;
	win.location.href = link;
	win.focus();
}

function upwin() {
	win = window.open("","upwin","toolbar=no,width=200,height=200,directories=no,status=no,scrollbars=yes,resizable=yes,menubar=no")
	win.focus();
}

function newwin() {
	newwin=window.open(ns_admin + 'home=1','_blank','menubar=no,resizable=yes,status=no,scrollbars=yes');
}

function search_id(fname,app) {
	var data = '';
	for (var i=0; i<self.document.sitform.elements.length; i++){
		if (self.document.sitform.elements[i].name == fname){
			data = self.document.sitform.elements[i].value;
			break;
		}
	}
	
	newwin=window.open('','search_id','toolbar=no,width=420,height=300,directories=no,status=no,scrollbars=yes,resizable=yes,menubar=no');
	newwin.location.href = '/cgi-bin/common/apps/schid?'+app+'&fname=' + fname + '&value=' + data ;
	newwin.focus();
}

function search_extid() {
	newwin=window.open('','search_id','toolbar=no,width=420,height=300,directories=no,status=no,scrollbars=yes,resizable=yes,menubar=no');
	newwin.location.href = '/cgi-bin/administration/dbapp?cmd=search_extid';
}

function download(fname) {
	newwin=window.open('','download','toolbar=no,width=320,height=80,directories=no,status=no,scrollbars=yes,resizable=yes,menubar=no');
	newwin.location.href = '/download.php?fname=' + fname;
	newwin.focus();
}

function playsound(fname) {
	newwin=window.open('','playsound','toolbar=no,width=320,height=80,directories=no,status=no,scrollbars=yes,resizable=yes,menubar=no');
	newwin.location.href = '/playsound.php?fname=' + fname;
	newwin.focus();
}

function playmusic(fname) {
	newwin=window.open('','playsound','toolbar=no,width=320,height=80,directories=no,status=no,scrollbars=yes,resizable=yes,menubar=no');
	newwin.location.href = '/playmusic.php?fname=' + fname;
	newwin.focus();
}

function jumppage(link) {
	newwin=window.open(link,'_blank','menubar=yes,resizable=yes,status=yes,scrollbars=yes');
	newwin.location.href = link;
	newwin.focus();
}

function egwlogin() {
	newwin=window.open('','egw','toolbar=no,width=1,height=1,directories=no,status=no,scrollbars=no,resizable=no,menubar=no');
	newwin.location.href = '/index.php?egw=1';
}

function trjump(link) {
	parent.location.href = link;
}

function trnjump(link) {
	newwin=window.open('','_blank','toolbar=no,width=800,height=600,directories=no,status=yes,scrollbars=yes,resizableyes,menubar=no');
	newwin.location.href = link;
}

//function chg_select(Name,Value) {
//    for (var i=0; i<self.document.sitform.length; i++){
//       if (self.document.sitform.elements[i].name == Name){
//            self.document.sitform.elements[i].value=Value;
//
//        }
//    }
//}


function chg_select(Name,Value) {
		for (var f=0; f<self.document.forms.length; f++){
    		for (var i=0; i<self.document.forms[f].length; i++){
        		if (self.document.forms[f].elements[i].name == Name){
                   self.document.forms[f].elements[i].value=Value;
            }
       	}

   	}
}


function chg_select2(Name,Value) {
    for (var i=0; i<self.document.sitform2.length; i++){
       if (self.document.sitform2.elements[i].name == Name){
            self.document.sitform2.elements[i].value=Value;

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
      
function chg_chkbox2(Value,Name) {
	var aux=Name.split("|");
	for (var x=0; x<aux.length; x++){
		for (var i=0; i<self.document.sitform.length; i++){
			if (self.document.sitform.elements[i].name == "chk:"+aux[x] && self.document.sitform.elements[i].value == Value){
				self.document.sitform.elements[i].click();
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

function chg_radio2(Name,Value) {
    for (var i=0; i<self.document.sitform2.length; i++){
        if (self.document.sitform2.elements[i].name.toLowerCase() == Name.toLowerCase() && self.document.sitform2.elements[i].value.toLowerCase() == Value.toLowerCase()){
            self.document.sitform2.elements[i].click();
        }
    }
}

function disabling(suf,onoff) {
	//l = suf.length;
	for (var i=0; i<self.document.sitform.length; i++){
		var n = self.document.sitform.elements[i].name;
		if (n){
			if (n.indexOf(suf)==0 && onoff==0){
				self.document.sitform.elements[i].disabled=true;
			}else if (n.indexOf(suf)==0 && onoff==1){
				self.document.sitform.elements[i].disabled=false;
			}
		}
	}
}



function toggleBox(szDivID, iState) // 1 visible, 0 hidden
{
   var obj = document.layers ? document.layers[szDivID] :
   document.getElementById ?  document.getElementById(szDivID).style :
   document.all[szDivID].style;
   obj.visibility = document.layers ? (iState ? "show" : "hide") :
   (iState ? "visible" : "hidden");
}

var helpary = new Array()

function hidehelp() {
	var spans = document.getElementsByTagName('span');
	var numspans = spans.length;
	for (var a = 0; a < numspans; ++a) {
		if (spans[a].id == 'help'){
			helpary[a] = spans[a].innerHTML;
			if (helpleg.innerHTML=="On"){
				spans[a].innerHTML = "";
			}
		}
	}
}

function helponoff() {
	var spans = document.getElementsByTagName('span');
	var numspans = spans.length;
	if (helpleg.innerHTML == 'Off'){
		helpleg.innerHTML="On";
		for (var a = 0; a < numspans; ++a) {
			if (spans[a].id == 'help'){
				spans[a].visible=false;
				spans[a].innerHTML = "";
			}
		}

	}else{
		helpleg.innerHTML="Off";
		for (var a = 0; a < numspans; ++a) {
			if (spans[a].id == 'help'){
				//spans[a].visible=true;
				spans[a].innerHTML = helpary[a];
			}
		}
	}
	document.cookie= "voxhelp=" + helpleg.innerHTML + ";path=/;";

}

function warningmsg($msg){
	if ($msg == undefined){
		$msg = "Are you sure want to delete this record?";
	}
	if (notest){
		return true;
	}else{
	    if (confirm($msg)){
		    return true;
	    }else{
		    notest = true;
		    return false;
	    }
	}
}


function moveIt( fbox, tbox ) {
	for( var i=0; i<fbox.options.length; i++ ) {
		if( fbox.options[i].selected && fbox.options[i].value != "" ) {
			var no = new Option();
			no.value = fbox.options[i].value;
			no.text = fbox.options[i].text;
			tbox.options[tbox.options.length] = no;
			fbox.options[i].value = "";
			fbox.options[i].text = "";
		}
	}
	bumpUp( fbox );
	//if ( sortitems ) {
	//	sortIt( tbox );
	//}
}

function bumpUp( box )  {
	for( var i=0; i<box.options.length; i++ ) {
		if( box.options[i].value == "" )  {
			for( var j=i; j<box.options.length-1; j++ )  {
				box.options[j].value = box.options[j+1].value;
				box.options[j].text  = box.options[j+1].text;
			}
			var ln = i;
			break;
		}
	}
	if( ln < box.options.length )  {
		box.options.length -= 1;
		bumpUp( box );
	}
}


function sortIt( box )  {
	var temp_opts = new Array();
	var temp = new Object();
	for( var i=0; i<box.options.length; i++ )  {
		temp_opts[i] = box.options[i];
	}
	for( var x=0; x<temp_opts.length-1; x++ )  {
		for( var y=(x+1); y<temp_opts.length; y++ )  {
			if( temp_opts[x].text > temp_opts[y].text )  {
				temp = temp_opts[x].text;
				temp_opts[x].text = temp_opts[y].text;
				temp_opts[y].text = temp;
			}
		}
	}
	for( var i=0; i<box.options.length; i++ )  {
		box.options[i].value = temp_opts[i].value;
		box.options[i].text = temp_opts[i].text;
	}
}

function moveSort( index,select ) {
	//var select	= document.sitform.listTo;
	if( select.length >= 2 ) {
		var item	= select.selectedIndex;
 		if (item==0 && index==-1){
 			alert( "You can't moving this field up." );
 			return
 		}
 		if (item == select.length-1 && index==1){
 			alert( "You can't moving this field down." );
 			return
 		}
 		var value	= select[item+index].value;
		var text	= select[item+index].text;
		select[item + index].value = select[item].value;
		select[item + index].text  = select[item].text;
		select[item].value         = value;
		select[item].text          = text;
		select.selectedIndex      += index;
	} else {
 		alert( "You need at least two items, so you can change their order." );

	}
}
function saveIt( destfld, box ) {
	destfld.value = '';
	for( var i=0; i<box.options.length; i++ )  {
		//alert(box.options[i].value);
		destfld.value += box.options[i].value + "|";
	}
	destfld.value = destfld.value.substr(0,destfld.value.length-1);
	//alert(destfld.value);
}

function rebuildIt( fbox, tbox, srcfld ) {
	//alert ("fields:"+srcfld.value);
	var temp = new Object();
	temp = srcfld.value.split("|");
	for( var x=0; x<temp.length; x++ )  {
		//alert(temp[x]);
		if (temp[x] == '---'){
			insblank(tbox);
		}else if (temp[x].substr(0,1) == '_'){
			//alert(temp[x]);
			//inslegend(temp[x],tbox);
			var no = new Option();
			no.value = temp[x];
			no.text = temp[x].substr(1);
			tbox.options[tbox.options.length] = no;
		}else{
			reMoveIt(fbox, tbox, temp[x])
		}
	}
}

function reMoveIt( fbox, tbox, tmove ) {
	for( var i=0; i<fbox.options.length; i++ )  {
		if (fbox.options[i].value == tmove){
			//fbox.options[i].click();
			fbox.options[i].selected=true;
			moveIt( fbox, tbox );
			return;
		}
	}
}

function insblank( tbox ) {
	var no = new Option();
	no.value = '---';
	no.text = 'blank';
	tbox.options[tbox.options.length] = no;
}
function inslegend(fbox, tbox ) {
	if (fbox.value.indexOf('|') != -1 || fbox.value.indexOf(':') != -1){
		alert('Invalid Legend, Please use only letters and numbers');
		return;
	}
	if (fbox.value != ""){
		var no = new Option();
		no.value = '_'+fbox.value;
		no.text = fbox.value;
		tbox.options[tbox.options.length] = no;
		fbox.value = '';
	}
}

function vmhtml(onoff){
	self.document.sitform.submit();
}


var checkflag = "false";
function checkall() {
	if (checkflag == "false") {
		for (i = 0; i < self.document.sitform.length; i++) {
			self.document.sitform.elements[i].checked = true;
		}
		checkflag = "true";
	}else {
		for (i = 0; i < self.document.sitform.length; i++) {
			self.document.sitform.elements[i].checked = false;
		}
		checkflag = "false";
	}
}


function preview_img(fname){
	var effect='none';
	w = self.document.sitform.newwidth.value;
	if (w>600) w=600;
	if (w<300) w=300;
	h = self.document.sitform.newheight.value;
	if (h>800) h=800;
	if (h<300) h=300;
	for (var i=0; i<self.document.sitform.length; i++){
	   if (self.document.sitform.elements[i].name == 'effect' && self.document.sitform.elements[i].checked){
	       effect = self.document.sitform.elements[i].value;
	   }
	}
	//alert ('/cgi-bin/common/apps/img?fname='+fname+'&img_prn=1&w='+self.document.sitform.newwidth.value+'&h='+self.document.sitform.newheight.value+'&effect='+effect);
	newwin=window.open('','previewimg','toolbar=no,width='+w+',height='+h+',directories=no,status=no,scrollbars=yes,resizable=yes,menubar=no');
	newwin.location.href = '/cgi-bin/common/apps/img?fname='+fname+'&img_prn=1&w='+self.document.sitform.newwidth.value+'&h='+self.document.sitform.newheight.value+'&effect='+effect;
	newwin.focus();
}

var formObjs = document.forms;
function disableSubmits(formObj) {
	for(i=0;i<formObjs.length;i++) {
		for(j=0;j<formObjs[i].elements.length;j++) {
			if(formObjs[i].elements[j].type == null) { j++; } else {}
			var fieldName = formObjs[i].elements[j].name.toLowerCase();
			if((formObjs[i].elements[j].type == "submit") || ((formObjs[i].elements[j].type == "button") && (fieldName.indexOf("submit") != -1))) {
				formObjs[i].elements[j].disabled = true;
			}
		}
	}
	return true;
}


<!-- This script and many more are available free online at -->
<!-- The JavaScript Source!! http://javascript.internet.com -->
<!-- Original:  Roman Feldblum (web.developer@programmer.net) -->

<!-- Begin
var n;
var p;
var p1;
function ValidatePhone(){
	p=p1.value
	if(p.length==3){
		//d10=p.indexOf('(')
		pp=p;
		d4=p.indexOf('(')
		d5=p.indexOf(')')
		if(d4==-1){
			pp="("+pp;
		}
		if(d5==-1){
			pp=pp+")";
		}
		//pp="("+pp+")";
		document.sitform.phone1.value="";
		document.sitform.phone1.value=pp;
	}
	if(p.length>3){
		d1=p.indexOf('(')
		d2=p.indexOf(')')
		if (d2==-1){
			l30=p.length;
			p30=p.substring(0,4);
			//alert(p30);
			p30=p30+")"
			p31=p.substring(4,l30);
			pp=p30+p31;
			//alert(p31);
			document.sitform.phone1.value="";
			document.sitform.phone1.value=pp;
		}
		}
	if(p.length>5){
		p11=p.substring(d1+1,d2);
		if(p11.length>3){
		p12=p11;
		l12=p12.length;
		l15=p.length
		//l12=l12-3
		p13=p11.substring(0,3);
		p14=p11.substring(3,l12);
		p15=p.substring(d2+1,l15);
		document.sitform.phone1.value="";
		pp="("+p13+")"+p14+p15;
		document.sitform.phone1.value=pp;
		//obj1.value="";
		//obj1.value=pp;
		}
		l16=p.length;
		p16=p.substring(d2+1,l16);
		l17=p16.length;
		if(l17>3&&p16.indexOf('-')==-1){
			p17=p.substring(d2+1,d2+4);
			p18=p.substring(d2+4,l16);
			p19=p.substring(0,d2+1);
			//alert(p19);
		pp=p19+p17+"-"+p18;
		document.sitform.phone1.value="";
		document.sitform.phone1.value=pp;
		//obj1.value="";
		//obj1.value=pp;
		}
	}
	//}
	setTimeout(ValidatePhone,100)
}
function getIt(m){
	n=m.name;
	//p1=document.forms[0].elements[n]
	p1=m
	ValidatePhone()
	}
	function testphone(obj1){
	p=obj1.value
	//alert(p)
	p=p.replace("(","")
	p=p.replace(")","")
	p=p.replace("-","")
	p=p.replace("-","")
	//alert(isNaN(p))
	if (isNaN(p)==true){
	alert("Check phone");
	return false;
	}
}
//  End -->

var xmlhttp=false;


if (!xmlhttp && typeof XMLHttpRequest!='undefined') {

	try {
      xmlhttp = new XMLHttpRequest();
    } catch (e) {
      xmlhttp = false;
    }

}

function loadDoc(docname) {
	//alert(docname);
	if (xmlhttp) {
		var i = Math.round(10000*Math.random())
		docname = docname + '&rsid='+i;
		document.getElementById('ajaxcontent').innerHTML="<img src='/sitimages/processing.gif' border='0'>";
		//popup_show('ajax_windows', 'ajax_drag', 'ajax_exit', 'mouse-corner', -400, -1);
		//popup_show('ajax_windows', 'ajax_drag', 'ajax_exit', 'mouse-corner',100 ,300);
		
		xmlhttp.open("GET", docname,true); 
		xmlhttp.onreadystatechange=function() {
			if (xmlhttp.readyState==4) {
				// document.forms[0].ajaxcontent.value=xmlhttp.responseText;
				document.getElementById('ajaxcontent').innerHTML=xmlhttp.responseText;
			}
		}
		xmlhttp.send(null)	
	}
}


function testloadarray(docname) {
	var i = Math.round(10000*Math.random())
	docname = docname + '&rsid='+i;
	var rec = new Object();

 	xmlhttp=new XMLHttpRequest();
    xmlhttp.onreadystatechange= function() { 
        if (xmlhttp.readyState==4){
            if (xmlhttp.status==200){
				ajaxdata = xmlhttp.responseText;
				if (ajaxdata.length >20){
					// Load Data to rec object
					var aux=ajaxdata.split("|");
					var numdata = aux.length / 2;				
					for (var a = 0; a < numdata; ++a) {
						n = aux[a*2];
						v = aux[a*2+1];
						rec[n] = v;
					}
					// Load Data form ajax and replace it
					var divs = document.getElementsByTagName('div');
					var numdivs = divs.length;
					for (var a = 0; a < numdivs; ++a) {
						if (divs[a].id.substr(0,5) == 'ajax_'){
							n = trim( divs[a].id.substr(5));
							divs[a].innerHTML = rec[n];
						}
					}
				}
			}
		}
    }
    xmlhttp.open("GET",docname,true);
    xmlhttp.send(null);
}

function loadarray(docname) {
	if (xmlhttp) {
		var i = Math.round(10000*Math.random())
		docname = docname + '&rsid='+i;
		var rec = new Object();
		
		xmlhttp.open("GET", docname,true); 
		xmlhttp.onreadystatechange=function() {
			if (xmlhttp.readyState==4) {
				// document.forms[0].ajaxcontent.value=xmlhttp.responseText;
				ajaxdata = xmlhttp.responseText;
				if (ajaxdata.length >20){
					// Load Data to rec object
					var aux=ajaxdata.split("|");
					var numdata = aux.length / 2;				
					for (var a = 0; a < numdata; ++a) {
						n = aux[a*2];
						v = aux[a*2+1];
						rec[n] = v;
					}
					// Load Data form ajax and replace it
					var divs = document.getElementsByTagName('div');
					var numdivs = divs.length;
					for (var a = 0; a < numdivs; ++a) {
						if (divs[a].id.substr(0,5) == 'ajax_'){
							n = trim( divs[a].id.substr(5));
							divs[a].innerHTML = rec[n];
						}
					}
				}
			}
			xmlhttp.send(null);	
		}
	}
}

/**
 * Created by : Rafael Sobrino
 * Created on : 10/18/2007 11:21AM
 * Description : View the password entered by the user in myprefs_mypass
 */
function view_password() {
	
}

function trim(stringToTrim) {
	return stringToTrim.replace(/^\s+|\s+$/g,"");
}

var ajaxcmd = '';
function update_field(fname,fdata,cmd) {
	ajaxcmd = cmd;
	var divs = document.getElementsByTagName('div');
	var numdivs = divs.length;
	for (var a = 0; a < numdivs; ++a) {
		if (divs[a].id == fname){
			//n = trim(divs[a].id.substr(6));
			divs[a].innerHTML = "<input type='text' id='"+fname+"' onFocus='focusOn( this )' onBlur='focusOff( this )' onChange=\"save_field('"+fname+"')\" name='"+fname+"' value='"+fdata+"' style='width:100%' \">";
		}
	}
}

function save_field(fname) {
	ndata = 0;
	for (var i=0; i<self.document.sitform.length; i++){
        if (self.document.sitform.elements[i].name == fname){
            ndata = self.document.sitform.elements[i].value;
        }
    }

	var divs = document.getElementsByTagName('div');
	var numdivs = divs.length;	
	for (var a = 0; a < numdivs; ++a) {
		if (divs[a].id == fname){
			//alert(ajaxcmd+'&updvalue='+ndata);
			//ajaxbuild
			divs[a].innerHTML = ndata;
			
			docname = "/cgi-bin/common/apps/ajaxbuild?ajaxbuild=updfield&"+ajaxcmd+'&updvalue='+ndata;
			xmlhttp.open("GET", docname,true); 
			xmlhttp.onreadystatechange=function() {
				if (xmlhttp.readyState==4) {
					//alert(xmlhttp.responseText);
				}
			}
			xmlhttp.send(null)	
		}
	}
	//history.go(0);
}

function delete_div(fname) {
	var divs = document.getElementsByTagName('div');
	var numdivs = divs.length;
	for (var a = 0; a < numdivs; ++a) {
		if (divs[a].id == fname){
			divs[a].innerHTML = "";
		}
	}
}

function update_dbfield(ajaxcmd,ndata) {
	docname = "/cgi-bin/common/apps/ajaxbuild?ajaxbuild=updfield&"+ajaxcmd+'&updvalue='+ndata;
	xmlhttp.open("GET", docname,true); 
	xmlhttp.onreadystatechange=function() {
		if (xmlhttp.readyState==4) {
			//alert(xmlhttp.responseText);
		}
	}
	xmlhttp.send(null)	

}


function delete_div(fname) {
	var divs = document.getElementsByTagName('div');
	var numdivs = divs.length;
	for (var a = 0; a < numdivs; ++a) {
		if (divs[a].id == fname){
			divs[a].innerHTML = "";
		}
	}
}

function pageslist_in(plink,nh) {
	var divs = document.getElementsByTagName('div');
	var numdivs = divs.length;
	for (var a = 0; a < numdivs; ++a) {
		if (divs[a].id == 'pageslist'){
			pageshtml =  divs[a].innerHTML
			divs[a].innerHTML = pageshtml + "<select onChange='pageslist_out("+plink+","+nh+")'><option>1</option><option>2</option></select>";
			buildit==false;
		}
	}
}

function pageslist_out(plink,nh) {
	buildit == true;
	var divs = document.getElementsByTagName('div');
	var numdivs = divs.length;
	for (var a = 0; a < numdivs; ++a) {
		if (divs[a].id == 'pageslist'){
			divs[a].innerHTML = pageshtml;
		}
	}
}


function showDiv_checkbox(divID,eName){
	var displayDiv = 'Block';
	var checkb = '';
	var flag=0;


	for (var f=0; f<self.document.forms.length; f++){
		for (var i=0 ; i<self.document.forms[f].length && flag==0; i++){
			if (self.document.forms[f].elements[i].name == eName && self.document.forms[f].elements[i].value < 0){
				checkb = self.document.forms[f].elements[i];
				flag=1;
			}
		}
	}

	if(checkb.checked == true){
		displayDiv = 'None';
	}
	
	var divs = document.getElementsByTagName('div');
	var numdivs = divs.length;
	for (var a = 0; a < numdivs; ++a) {
		if (divs[a].id == divID){
			divs[a].style.display = displayDiv;
		}
	}
}


function confirm_changeto_cod(script_url,cmd,id_orders){
	var answer = confirm("Really want to change order "+id_orders+" to COD?");
	if(answer){
		window.location.href = script_url+"?cmd="+cmd+"&view="+id_orders+"&tocod=1";
	}else{
		return false;
	}
}


function passdownsale(field) {
/*-----------------------------------------
# Created on: 09/23/09  10:14:14 By  Roberto Barcenas
# Forms Involved: 
# Description : Compara el authcode ingresado para abrir la opcion de downsale en inbound
# Parameters :
# Last Modified RB: 09/23/09  10:30:49 -- Se cambia respuesta negativa "Invalid" por "" y se escribe la respuesta negativa
# Last Modified RB: 07/07/11  16:10:03 -- Se hace que al pasar el codigo, el radio con el downsale se quede seleccionado  	
--------------------------------------------*/

	var dfield = document.getElementById(field);
	var nfield = document.getElementById('span_'+field);
	
	if(dfield.value.length == 4){
		var flag=0;
		var rfield = field.substr(0,field.length-1);
		var xfield = field.substr(field.length-1);
		
		dfield.style.border='1px solid red';
		docname = "/cgi-bin/common/apps/ajaxbuild?ajaxbuild=passdownsale&authcode="+dfield.value;
		xmlhttp.open("GET", docname,true); 
		xmlhttp.onreadystatechange=function() {
			if (xmlhttp.readyState==4) {
				if(xmlhttp.responseText != ''){
					nfield.style.color='green';
					nfield.innerHTML = xmlhttp.responseText;
					for (var i=0 ; i<self.document.forms[0].length && flag==0; i++){
						if (self.document.forms[0].elements[i].name == rfield && self.document.forms[0].elements[i].value == xfield){
							self.document.forms[0].elements[i].disabled = false;
							flag=1;
							chg_radio('pricenumber',xfield);
						}
					}
				}else{
					dfield.value = 'Incorrecto';
				}
			}
		}
		xmlhttp.send(null)	
	}	
}


function fillOrderNote(picked){
/*
	Funcion de prellenado de datos en las notas de las ordenes view_orders
*/	
		picked = parseInt(picked);		
		var note = document.getElementById('notetxt');
	
		var aryNotes = new Array(11);
		aryNotes[0] = "Se confirma domicilio y Monto con el cliente Por $\nFecha de Entrega : \nProducto:";
	  aryNotes[1] = "Se confirma domicilio y Monto con el cliente Por $\nFecha de Entrega : \nProducto: \nError: N/A";
	  aryNotes[2] = "";
	  aryNotes[3] = "";
	  aryNotes[4] = "Se Valida Domicilio\nMoney Order por $\nFecha de Entrega: \nProducto:";
	  aryNotes[5] = "";
	  aryNotes[6] = "";
	  aryNotes[7] = "ATC-Rehsip";
	  aryNotes[8] = "Cliente solicita cambio fisico de su producto(s): \nNuevo Producto: \nTiempo de Entrega: 8 a 12 dias Habiles a partir de la recepcion de su producto.\nNota: ";
	  aryNotes[9] = "Cliente solicita Reembolso.\nMotivo: \nNombre del Cliente en ID:\nDireccion de Envio del Cheque (COD): \n Nombre del Cliente / Titular (TDC): \nNota:";
	  aryNotes[10] = "";
	  
	  note.value = aryNotes[picked];
}
