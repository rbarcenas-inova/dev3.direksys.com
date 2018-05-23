<?php

//-- decodifica los acaracteres utf8 que existan en un array    
function decodeUTF8($array) {

    foreach ($array as $k => $postTmp) {
        if (is_array($postTmp)) {
            $array[$k] = decodeUTF8($postTmp);
        } else {
            $array[$k] = utf8_decode($postTmp);
        }
    }

    return $array;
}

?>