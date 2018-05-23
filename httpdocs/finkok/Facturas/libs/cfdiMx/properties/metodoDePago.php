<?php

namespace cfdiMx\properties;

use Exception;
use SimpleXMLElement;

/**
 *
 */
class metodoDePago
{
    final public static function extract(SimpleXMLElement $xml, array $namespace, $version)
    {
        switch ($version) {
            case 3:
            case 3.2:
                return (string) $xml['metodoDePago'];
                break;
            default:
                throw new Exception('Unkown document version ' . $version);
                break;
        }
    }
}
