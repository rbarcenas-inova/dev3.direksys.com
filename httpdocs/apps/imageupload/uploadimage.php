<?php
    require("functions.php");
    #########################################################
    #### INIT System Data
    #########################################################
    $in  = array();
    $va  = array();
    $trs = array();
    $usr = array();
    $sys = array();
    $cfg = array();
    $tpl = array();
    $cses= array();
    $error= array();
    $device=array();

    define('DATE_FORMAT_LONG', '%A %d %B, %Y');

    ######################################################
    ##### Configuration File
    ######################################################
    get_values();
    load_custom_data($in['e']);
    // $ck_name  =  $cfg['ckname'];
    $sid="";
    switch($in['cmd']){
        default:
        $html .= formUploadImage();
            break;
        case 'process':
        $html .= processImage();
            break;
       
        
    }
     
    echo $html;
    
    /**
	 * Procesa las Imagenes y las envia por SFTP al repositorio de Imagenes
	 *
	 * @author Arturo Hernandez
     * 
	 */
    
    function processImage(){
    global $in, $cfg;

    include('Net/SFTP.php');
    require ("class.image.php");
    $error = 0;
        if(is_uploaded_file($_FILES['img']['tmp_name'])){  
            $sftp = new Net_SFTP($cfg['server_sftp']);
            if (!$sftp->login($cfg['user_sftp'], $cfg['pass_sftp'])) {
                exit('Login Failed');
            }
            $z = 0;
            foreach($sftp->nlist($cfg['path_sftp']) AS $key => $value){
                if($value == $in['id_products']){
                    $z++;
                }
                
            }
            if($z == 0){
                $sftp->mkdir($cfg['path_sftp'].$in['id_products']);
            }
            $path = $cfg['path_sftp'].$in['id_products'].'/';
            $rand = rand(1, 9999);
            $imagename = $rand.'-'.$in['id_products'].'.jpg';
            $image = new SimpleImage($_FILES['img']['tmp_name']);
            
            if($sftp->put($path.$imagename, $image->output_file())){
                $db = new PDO('mysql:host='.$cfg['dbi_host'].';dbname='.$cfg['dbi_db'].';', $cfg['dbi_user'], $cfg['dbi_pw']);
                if(empty($in['listorder'])){
                    $sqlConsult = "SELECT ListOrder+1 FROM sl_products_images 
                    WHERE  ID_products = '$in[id_products]'
                    ORDER by ID_products_images DESC LIMIT 1";
                    $stmt = $db->query($sqlConsult);
                    $listorder = $stmt->fetchAll();
                    $listorder = $listorder[0][0];
                }else{
                    
                    $listorder = $in['listorder'];
                }
                $sftp->put($path.'thumb-'.$imagename, $image->thumbnail(170, 170)->output_file());  
                $sql = "INSERT INTO sl_products_images 
                (ID_products, Image, ListOrder, Date, Time, ID_admin_users) 
                VALUES 
                ('$in[id_products]','$imagename','$listorder',NOW(), NOW(), 5)";
                $result = $db->exec($sql);
                $db = null;
            }else{
                
                $error++;
            }
             
        }else{
            $error++;
        }
        if($error == 0){
            $html .= '<div style="font-family:Verdana;">The image was uploaded successfully !</div><br><img width="100" src="'.$cfg['url_sftp'].$in['id_products'].'/thumb-'.$imagename.'" />';
        }
        return $html;
    }
    
    
    /**
	 * Formulario de Imagenes
	 *
	 * @author Arturo Hernandez
     * 
	 */
    
    function formUploadImage(){
         global $in, $cfg;
        $html .= '
        <div style="font-family:Arial;font-size:12px;">
        <div id="imageloading" style="display:none;"><img src="/modtrans/common/img/loader.gif" /> Uploading Image</div>
        <div id="imagediv" >
        <form method="post" enctype="multipart/form-data" id="imageform" onsubmit="return hideform()">
            <input type="hidden" value="'.$in['e'].'" name="e" />
            <input type="hidden" name="cmd" value="process" />
            <input type="hidden" name="id_products" value="'.$in['id_products'].'" />
            <table>
                <tr>
                    <td>Image: </td>
                    <td><input type="file" name="img" id="img" /></td>
                </tr>
                <tr>
                    <td>List Order: </td>
                    <td><input type="text" name="listorder" /></td>
                </tr>
                <tr>
                    <td>&nbsp;</td>
                    <td><input type="submit" value="Upload Image" /></td>
                </tr>
            </table>
        </form>
        </div>
        </div>
        <script>
            function hideform(){
                if(document.getElementById("img").value != ""){
                    var link = document.getElementById("imagediv");
                    link.style.display = "none"; 
                    document.getElementById("imageloading").style.display = "block";
                }else{
                    alert("Have not selected any images!");
                    return false;
                }
            }
        </script>';
        return $html;
        
    }
    
?>