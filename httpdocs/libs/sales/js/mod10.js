/*
var aryImages = new Array(16);
aryImages[0] = "/sitimages/cc_images/CC_.gif";
aryImages[1] = "/sitimages/cc_images/CC_badcard.gif";
aryImages[2] = "/sitimages/cc_images/CC_visa.gif";
aryImages[3] = "/sitimages/cc_images/CC_maestro.gif";
aryImages[4] = "/sitimages/cc_images/CC_mastercard.gif";
aryImages[5] = "/sitimages/cc_images/CC_delta.gif";
aryImages[6] = "/sitimages/cc_images/CC_electron.gif";
aryImages[7] = "/sitimages/cc_images/CC_visapurchasing.gif";
aryImages[8] = "/sitimages/cc_images/CC_visaatmonly.gif";
aryImages[9] = "/sitimages/cc_images/CC_discover.gif";
aryImages[10] = "/sitimages/cc_images/CC_solo.gif";
aryImages[11] = "/sitimages/cc_images/CC_switch.gif";
aryImages[12] = "/sitimages/cc_images/CC_amex.gif";
aryImages[13] = "/sitimages/cc_images/CC_jcb.gif";
aryImages[14] = "/sitimages/cc_images/CC_dinersclub.gif";
aryImages[15] = "/sitimages/cc_images/CC_carteblanche.gif";
aryImages[16] = "/sitimages/cc_images/CC_enroute.gif";

var mdtImages = new Array(3);

mdtImages[0] = "/sitimages/cc_images/CC_mod10blank.gif";
mdtImages[1] = "/sitimages/cc_images/CC_mod10passed.gif";
mdtImages[2] = "/sitimages/cc_images/CC_mod10failed.gif";

var mdtxImages = new Array(3);

mdtxImages[0] = "/sitimages/cc_images/CC_mod10blank.gif";
mdtxImages[1] = "/sitimages/cc_images/CC_lengthpassed.gif";
mdtxImages[2] = "/sitimages/cc_images/CC_lengthfailed.gif";

*/
function mod10(ccno)
{
	if(ccno == '2728000000000000'){
		cc_type_id = 'Visa';
		cardimage='7';
		return cc_type_id;
	}

	vlengthgood=0;
	ccsum=0;
	cclen=ccno.length;
	if (cclen<13)
	{
		cardimage='1';
		cc_type_id='';
	}
	else
	{
		for (i=1; i<cclen; i++)
		{
			ccdig=parseInt(ccno.charAt(cclen-(i+1)));
			if (i%2==1)
			{
				ccdig*=2;
				if (ccdig.toString().length==2)
				{
					ccdig=(parseInt(ccdig.toString().charAt(0))+parseInt(ccdig.toString().charAt(1)));
				} 
			}
			ccsum+=ccdig;
		}
		ccsum+=parseInt(ccno.charAt(cclen-1));
		if(ccsum%10==0)
		{
			cc_type_id='NOT VALID TYPE';
			cardimage='1';
			vlength='99';
			if (ccno.match(/^4/) )
			{
				cc_type_id = 'Visa';
				cardimage='2';
				if (cclen==13 || cclen==16)
				{
					vlengthgood=1;
				}
				else
				{
					vlengthgood=0;
				}

				if (ccno.match(/^405501|^405502|^405503|^405504|^405550|^405551|^405552|^405553|^405554|^415928|^424604|^424604|^427533|^4288|^443085|^4484|^4485|^4486|^4715|^4716|^4804|^272800/) )
				{
					cc_type_id = 'Visa'; //visapurchasing
					cardimage='7';
					if (cclen==16) 
					{
						vlengthgood=1;
					}
					else 
					{
						vlengthgood=0;
					}
				}
				else if (ccno.match(/^490300|^490301|^49031|^49032|^490330|^490331|^490332|^490333|^490334|^49034|^49035|^49036|^49037|^49038|^49039|^49040|^490419|^490451|^490459|^490467|^490475|^490476|^490477|^490478|^4905|^491103|^491104|^491105|^491106|^491107|^491108|^491109|^49111|^49112|^49113|^49114|^49115|^49116|^491170|^491171|^491172|^491173|^491183|^491184|^491185|^491186|^491187|^491188|^491189|^49119|^4928|^4987/) )
				{
					cc_type_id = 'Visa'; //visaatmonly
					cardimage='8';
					if (cclen==16) 
					{
						vlengthgood=1;
					}
					else 
					{
						vlengthgood=0;
					}
				}

			}
			else if (ccno.match(/^51|^52|^53|^54|^55/) )
			{
				cc_type_id = 'Mastercard';
				cardimage='4';
				if (cclen==16)
				{
					vlengthgood=1;
				}
				else
				{
					vlengthgood=0;
				}
			}			
			else if (ccno.match(/^6011/) )
				{
				cc_type_id = 'Discover';
				cardimage='9';
				if (cclen==16) 
				{
					vlengthgood=1;
				}
				else 
				{
					vlengthgood=0;
				}
			}
			else if (ccno.match(/^36/) ) /* #RB Start - Add Diners Club Validation - apr2808 */
			{
				cc_type_id = 'Diners';
				cardimage='14';
				if (cclen==14) 
				{
					vlengthgood=1;
				}
				else 
				{
					vlengthgood=0;
				}
			}	/* #RB End */
			else if (ccno.match(/^34|^37/) )
			{
				cc_type_id = 'American Express';
				cardimage='12';
				if (cclen==13 || cclen==15) 
				{
					vlengthgood=1;
				}
				else 
				{
					vlengthgood=0;
				}
			}
			if (vlengthgood!=1)
			{
				cardimage='1';
				cc_type_id='';
			}
		}
		else
		{
			cardimage='1';
			cc_type_id='';
		}
	}	
	
	return cc_type_id;
}