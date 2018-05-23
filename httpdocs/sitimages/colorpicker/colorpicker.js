	var color_fname;
	
	function startcolorpick(fname){
		if (document.all.colorpalet.innerHTML != '&nbsp;'){
			document.all.colorpalet.innerHTML = '&nbsp;';
		}else{
			document.all.colorpalet.innerHTML= "	<table>\n		  <tr>\n		  	<td><img border='0' src='/sitimages/colorpicker/palette2.gif' usemap='#Palette' width='128' height='113'></td>\n		  	<td><div id='colorsample'>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<br>&nbsp;<br>&nbsp;<br>&nbsp;<br>&nbsp;<br>&nbsp;<br>&nbsp;<br></span></td>\n		 </tr>\n		</table>\n";
		}
		color_fname = fname;
		
	}
	//Reusable background color change function
	function changeBc(color){
		document.all.colorsample.style.backgroundColor   = color;
	}

	function sampleCOL(field,color){
		eval('document.all.'+field+'.style.backgroundColor = color.value');
	}	
	
	function changeCOL(color){
		var fname;
		for (var i=0; i<self.document.sitform.length; i++){
			if (self.document.sitform.elements[i].name == color_fname){
				self.document.sitform.elements[i].value = color;
				sampleCOL(color_fname,self.document.sitform.elements[i]);
			}
		}
		
		changeBc(color);
		document.all.colorpalet.innerHTML ='';
		return;
	}
	
		// Load Colors Array
		var cc = new Array ("FF","CC","99","66","33","00");
		var dbcolors = new Array;
		var num=1;
		for( var x = 0; x <= 5; x++ ){
			for( var y = 0; y <= 5; y++ ){
				for( var z = 0; z <= 5; z++ ){
					dbcolors[num] = "#" + cc[x] + cc[y]+ cc[z];
					++num;
				}
			}
		}
		
	
		// Built Map
		var num=1;
		document.write( '<MAP NAME=Palette>' );
		for( var x = 1; x <= 14; x++ ){
			for( var i = 1; i <= 16; i++ ){
				if (num <=216){
				    document.write('<AREA href="javascript:changeCOL(\'' + dbcolors[num] + '\')" onMouseOver="javascript:changeBc(\'' + dbcolors[num] + '\')" shape="rect" COORDS="'+ (i*8-7) + ',' + (x*8-7) + ',' + (i*8) + ','+ (x*8) +'">');
				    ++num;
				}
			}
			
		}
		document.write( '</MAP>' );