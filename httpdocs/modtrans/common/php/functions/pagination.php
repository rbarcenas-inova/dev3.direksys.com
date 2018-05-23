<?php

/**
 * Description
 *
 * @author L.C.I Cesar Cedillo
 */
function createPaginator($totalResults, $per_page = 10, $url = '', $data_assoc = array(), $idContainer = 'pagination', $dataContainer = '') {
    $pages = ceil($totalResults / $per_page);

    $string_params = "";
    foreach ($data_assoc as $idx => $value) {
        $string_params .= "&" . $idx . "=" . $value;
    }

    $string_params = urldecode($string_params);
    ?> 

    <script type="text/javascript">
            
        var totalResults = parseInt(<?php echo $totalResults; ?>);
            
        if(totalResults > 0){
            $("#<?php echo $idContainer; ?>").show();
        }else{
            $("#<?php echo $idContainer; ?>").hide();
        }
                    
            
        $("#<?php echo $idContainer; ?> li:first")
        .css({'color' : '#FF0084'}).css({'border' : 'none'});
            
        $("#<?php echo $dataContainer; ?>").load("<?php echo $url; ?>?page=1<?php echo $string_params; ?>");
            
            
        $("#<?php echo $idContainer; ?> li").click(function(){
            
            
            $("#<?php echo $idContainer; ?> li")
            
            
            .css({'border' : 'none'})
            .css({'font-weight' : 'normal'})
            .css({'color' : '#000000'});

            $(this)
            .css({'color' : '#FF0084'})
            .css({'font-weight' : 'bold'})
            .css({'border' : 'none'});

                
            var pageNum = this.id;
                
            $("#<?php echo $dataContainer; ?>").load("<?php echo $url; ?>?page=" + pageNum + "<?php echo $string_params; ?>");
        });


    </script>

    <span style="float: left">
        <strong>Paginas:</strong>&nbsp;
    </span>
    <ul id="<?php echo $idContainer; ?>" style="	margin:0px;padding:0px;height:100%;overflow:hidden;font:12px 'Tahoma';list-style-type:none;" >
        <?php
        for ($i = 1; $i <= $pages; $i++) {
            echo '<li id="' . $i . '" style="float:left; margin:0px; padding:0px; margin-left:5px; min-width: 8px; max-width: 30px; cursor:pointer;">' . $i . '</li>';
        }
        ?>
    </ul>

    <?php
}
?>