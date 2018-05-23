<?php
/**
 * Description
 *
 * @author L.C.I Cesar Cedillo
 */
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
<div class="bar-header">
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
    <table width="100%" cellspacing="0" cellpadding="0" border="0" id="top1">
        <tbody>
            <tr>
                <td width="230px"><a href="<?php echo $cfg['admin_url'] . $usr['application']; ?>/admin?cmd=home"><img border="0" src="<?php echo $COMMON_PATH; ?>/common/img/direksys-logo.png"></a></td>
                <td align="left">
                    <font class="userinfo">  
                    <font class="username"><?php echo $user_full_name; ?></font><br>
                    ID: <?php echo $usr['id_admin_users']; ?>&nbsp;&nbsp;|&nbsp;&nbsp;
                    Exten: <?php echo $usr['extension']; ?>&nbsp;&nbsp;|&nbsp;&nbsp;
                    Time : <span id="showtime"></span>  
                    </font>
                </td>

                <td valign="top" align="right">
                    <table cellspacing="0" cellpadding="0">
                        <tbody>
                            <tr><td width="74px" valign="top" background="/sitimages/app_bar/mod/icobg1.png" align="center" onclick="helponoff()"><span id="helpleg_img"><img width="74px" height="30px" style="cursor:pointer;" src="/sitimages/app_bar/mod/helpOn.png" id="img_voxhelp"></span></td>
                                <td nowrap="" background="/sitimages/app_bar/mod/icobg2.png">
                                    <a href="<?php echo $cfg['admin_url'] . $usr['application']; ?>/admin?cmd=home"><img border="0" alt="Home Page" title="Home Page" src="/sitimages/app_bar/mod/ico-home.jpg"></a> 
                                    <a href="/manuals/"><img border="0" alt="Manuals" title="Manuals" src="/sitimages/app_bar/mod/ico-manuals.jpg"></a> 
                                    <a href="javascript:logoff()"><img border="0" alt="Logoff" title="Logoff" src="/sitimages/app_bar/mod/ico-exit.jpg"></a>
                                </td>
                                <td>
                                    <img src="/sitimages/app_bar/mod/icobg3.png">
                                </td>
                            </tr>
                        </tbody>
                    </table>                  
                </td>
            </tr>
        </tbody>
    </table>
    <table width="100%" cellspacing="0" cellpadding="0" border="0">
        <tbody>
            <tr>
                <td width="7px">
                    <img width="7px" height="100%" src="<?php echo $COMMON_PATH; ?>/common/img/menubg1.png">
                </td>
                <td width="100%" background="<?php echo $COMMON_PATH; ?>/common/img/menubg2.png">
                    <table cellspacing="0" cellpadding="0" border="0">
                        <tbody>
                            <tr>
                                <td valign="middle" align="left"><font class="menu1" style="cursor: pointer;" onclick="location.href='/modtrans/index.php'">&nbsp;&nbsp;<?php echo $cfg['app_title_trans'] ?></font></td>
                                <td valign="middle" align="left"><img src="<?php echo $COMMON_PATH; ?>/common/img/menubgdiv.png"></td>
                                <td valign="middle" nowrap="" align="left">
                                    <font class="menu2">Empresa: 
                                    <font class="compania"><?php echo $cfg['app_title']; ?></font>&nbsp;                                    
                                    </font>
                                </td>
                                <td valign="middle" align="left">
                                    <img src="<?php echo $COMMON_PATH; ?>/common/img/menubgdiv.png">
                                </td>
                                <td valign="middle" nowrap="" align="left">
                                    <font class="menu2">Modulo: 
                                    <font class="modulo1"><span id="spn-mod-name">Administration</span></font>&nbsp;
                                    </font>
                                </td>
                            </tr>
                        </tbody>
                    </table>
                </td>
                <td width="7px">
                    <img src="<?php echo $COMMON_PATH; ?>/common/img/menubg3.png">
                </td>
            </tr>
        </tbody>
    </table>

</div>