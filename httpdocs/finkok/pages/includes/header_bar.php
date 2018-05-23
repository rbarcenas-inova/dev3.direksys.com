<?php
global $COMMON_PATH;
global $cfg;
global $usr;


$user_full_name = $usr['firstname'];
if (trim($usr['middlename']) != "") {
    $user_full_name .= " " . $usr['middlename'];
}
$user_full_name .= " " . $usr['lastname'];
?>
<script type="text/javascript" src="<?php echo $COMMON_PATH ?>/common/js/functions.js"></script>

    <script type="text/javascript">
        function logoff(){
            if (confirm("Are you sure want to Exit?    ")){
                this.location.href = '/index.php?logoff=1';
            }
        }
        
        $(document).ready(function(){
            showTheTime('showtime');
        });
    </script>    





<div id="fly" >
  <table border="0" cellspacing="0" cellpadding="0" style="background-color:#ffffff;  -moz-border-radius: 0px 0px 10px 10px;border-radius: 0px 0px 10px 10px; position:fixed;top:0px;z-index:90;-moz-box-shadow: 0 0px 10px #bbbbbb;   -webkit-box-shadow: 0 0px 10px #bbbbbb;  box-shadow: 0 0px 10px #bbbbbb; height:40px; min-width:930px;">
    <tr>
      <td width=100% >
        <table border="0" cellspacing="0" cellpadding="0">
          <td valign=middle align=left nowrap>&nbsp; <a href='/'><img src=/sitimages/app_bar/mod/direksysRN.png border=0 height=25px></a></td>
          <td><img src="/sitimages/banderamexico.jpg" border=0></td>
          <td valign=middle align=left nowrap>
            <a href="/"  class="anchorclass compania" rel="submenu1[click]">
            <font class="compania"><?php echo $cfg['app_title']; ?> </font>
                <img src=/sitimages/app_bar/mod/v.jpg border=0>
            </a>
          </td>
          <td valign=middle align=left>
                  <img src=/sitimages/app_bar/mod/menubgdiv.png>
          </td>
          <td valign=middle align=left nowrap>
            <a href="/"  class="anchorclass modulo" rel="submenu2[click]">
            <font class="modulo1">CFDI</font>
              <img src=/sitimages/app_bar/mod/v.jpg border=0>
            </a>
          </td>
          <td valign=middle align=left>
            <img src=/sitimages/app_bar/mod/menubgdiv.png>
          </td>
        </table>


      </td>
      <td>

        <table border="0" cellspacing="0" cellpadding="0" align=right style="margin-right:15px;">
          <td valign=bottom nowrap>
          </td>
          <td nowrap>
            Hi <b><?php echo $user_full_name; ?></b><br>
            <font color=#777777> ID: <?php echo $usr['id_admin_users']; ?> | Ext: <?php echo $usr['extension']; ?>
              <!--<span id="showtime"></span>-->
          </td>
          <td width=15px nowrap>&nbsp;&nbsp;<td>
          <td valign=bottom nowrap>
                <a href="<?php echo $cfg['admin_url'] . $usr['application']; ?>/admin?cmd=home"><img border="0" alt="Home Page" title="Home Page" src="/sitimages/app_bar/mod/ico-home.jpg"></a> 
                <a href="/manuals/"><img border="0" alt="Manuals" title="Manuals" src="/sitimages/app_bar/mod/ico-manuals.jpg"></a> 
                <a href="javascript:logoff()"><img border="0" alt="Logoff" title="Logoff" src="/sitimages/app_bar/mod/ico-exit.jpg"></a>
          </td>
        </table>

      </td>
    </tr>
  </table>
</div>




<div style="height:25px;"></div>
