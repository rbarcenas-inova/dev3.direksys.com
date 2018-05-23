<?php
/**
 * @author Eduardo Cesar Cedillo Jiménez
 * @author Oscar Maldonado
 * @abstract Script para crear un paginador desde la pagina invocadora
 */
session_start();

$url = "";
if (isset($_GET["url"])) {
    $url = $_GET["url"];
} else {
    $url = $_POST["url"];
}
$page = isset($_POST['pagenum']) ? $_POST['pagenum'] : (isset($_GET['pagenum']) ? $_GET['pagenum'] : 1);

$total_paginas = $_SESSION['TOTAL_PAGINAS_CFDI'];

unset($_SESSION['TOTAL_PAGINAS_CFDI']);
?>
<?php
if ($total_paginas > 0) {
    ?>
    <script type="text/javascript">
        $(function() {
            $("#paginador").paginate({
                count 	: <?php echo $total_paginas ?>,
                //start 	: 1,
                start   : <?php echo $page ?>,
                display : 10,
                border	: false,
                text_color  : '#888',
                background_color    : '#EEE',
                text_hover_color    : 'black',
                background_hover_color	: '#CFCFCF',
                onChange:   function(page){
                    $.ajax({
                        type: 'POST',                    
                        url: '<?php echo $url ?>',
                        data: {pagenum: page},
                        success:function(data){
                            $("#resultados-consulta").html(data);
                        }
                    });
                }
            });
        });
    </script>
    <?php
}
?>
<div id=paginador style="left: 33%; right:33%;width: 500px"></div>