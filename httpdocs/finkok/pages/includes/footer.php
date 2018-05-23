<table border="0" cellspacing="0" cellpadding="0"   width=98% bgcolor="#000000" align=center background="/sitimages/app_bar/mod/botbg.jpg">
    <tr>
      <td>
        <table cellpadding=0 cellspacing=0 width=100% border=0>
          <td width=150px>&nbsp;</td>
          <td valign=top align=center>
            <!-- <a id="img_direksys_footer" title="Go Home"  href="/cgi-bin/mod/[ur_application]/admin?cmd=home" /> -->
            <img src=/sitimages/app_bar/mod/logo2.png border=0 width=160px> 
            <!-- </a> -->
          </td>
          <td width=150px>&nbsp;</td>
        </table>
      </td>
    </tr>
   </table>
    <br>





 <script>


 
$(document).ready(function(){
   //$( ":submit" ).on('click', function(){
   // if ($(this).attr('loading') != 0){
   //   $('#blockscreen').fadeIn();
   // }
   //});

  // $( "form" ).submit(function( event ) {
  //  $('#blockscreen').fadeOut();
  // });

  


  // hide #scroll first
  $("#gotopfade").hide();

 
  if("[ur_application]" != "sales")
    $("#fly2").hide();
  // fade in #scroll
  $(function () {
    $(window).scroll(function () {
      if ($(this).scrollTop() > 100) {
        $('#gotopfade').fadeIn();
      } else {
        $('#gotopfade').fadeOut();
      }


 

    if ($(this).scrollTop() > 75) {
      $('#fly2').show();
    } else {
      $('#fly2').hide();
    }
  

 


    var scroller_anchormenu = $(".scroller_anchormenu").offset().top;
    if ($(this).scrollTop() >= scroller_anchormenu && $('.scrollermenu').css('position') != 'fixed')
    {    
        $('.scrollermenu').css({
            'background': '',
            'border': '0px solid #000',
            'position': 'fixed',
            'top': '0',
            'margin-top': '2px'
        });
        $('.scroller_anchormenu').css('height', '50px');
    }
    else if ($(this).scrollTop() < scroller_anchormenu && $('.scrollermenu').css('position') != 'relative')
    {    
      $('.scroller_anchormenu').css('height', '0px');
        $('.scrollermenu').css({
            'background': '',
            'border': '0px solid #CCC',
            'position': 'relative'
        });
    }



    });

    // scroll body to 0px on click
    $('#gotopfade a').click(function () {
      $('body,html').animate({
        scrollTop: 0
      }, 777);
      return false;
    });
  });




});
</script>

<STYLE TYPE="text/css"> 
 
a.scrolls img {
filter:alpha(opacity=90);   
-moz-opacity: 0.9;   
opacity: 0.9;
cursor: hand;-moz-border-radius: 50%;
border-radius: 50%;
}

a.scrolls:hover img {
filter:alpha(opacity=100); 
-moz-opacity: 1.0; 
opacity: 1.0;
}

</STYLE>

<p id=gotopfade  style="position:fixed;bottom:0px;right:5px;"><a  href="#top1" class="scrolls" id="topid1"><img id="img_top1" title="Go Up" src=/sitimages/gototop.png border=0></a></p>
            
