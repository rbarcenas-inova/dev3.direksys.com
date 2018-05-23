<?php
session_start();

$url = "";
if (isset($_GET["url"])) {
    $url = $_GET["url"];
} else {
    $url = $_POST["url"];
}

$total_paginas = $_SESSION['TOTAL_PAGINAS_CFDI'];
unset($_SESSION['TOTAL_PAGINAS_CFDI']);
?>
<script type="text/javascript">
    $(function() {
        $("#paginador").paginate({
            count 	: <?php echo $total_paginas ?>,
            start 	: 1,
            display : 5,
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
<div id=paginador style="left: 42%;width: 350px"></div>