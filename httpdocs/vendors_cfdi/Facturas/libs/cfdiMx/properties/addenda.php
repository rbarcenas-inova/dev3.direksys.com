<?php

namespace cfdiMx\properties;

use SimpleXMLElement;
/**
 *
 */
class addenda{
    final public static function extract(SimpleXMLElement $xml, array $namespace, $version)
    {
        $data = array();
        $cfdi = $xml->children($namespace['cfdi']);
        $addenda = $cfdi->Addenda->children($namespace['ecfd']);
        $data = json_encode($addenda);
        $data = json_decode($data,true);
        return (count($data) > 0) ? $data : null;
    }
}
