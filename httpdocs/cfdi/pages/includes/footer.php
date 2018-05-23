<table border="0" cellspacing="0" cellpadding="0"   width=98% bgcolor="#000000" align=center>
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

  $("#fly").hide();

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
      $('#fly').show();
    } else {
      $('#fly').hide();
    }
  

    if ($(this).scrollTop() > 75) {
      $('#fly2').show();
    } else {
      $('#fly2').hide();
    }
  



    var scroller_anchor = $(".scroller_anchor").offset().top;
     
    // Check if the user has scrolled and the current position is after the scroller start location and if its not already fixed at the top
    if ($(this).scrollTop() >= scroller_anchor && $('.scroller').css('position') != 'fixed')
    {    // Change the CSS of the scroller to hilight it and fix it at the top of the screen.
        $('.scroller').css({
            'background': '',
            'border': '0px solid #000',
            'position': 'fixed',
            'top': '0'
        });
        // Changing the height of the scroller anchor to that of scroller so that there is no change in the overall height of the page.
        $('.scroller_anchor').css('height', '50px');
    }
    else if ($(this).scrollTop() < scroller_anchor && $('.scroller').css('position') != 'relative')
    {    // If the user has scrolled back to the location above the scroller anchor place it back into the content.
         
        // Change the height of the scroller anchor to 0 and now we will be adding the scroller back to the content.
        $('.scroller_anchor').css('height', '0px');
         
        // Change the CSS and put it back to its original position.
        $('.scroller').css({
            'background': '',
            'border': '0px solid #CCC',
            'position': 'relative'
        });
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
            
