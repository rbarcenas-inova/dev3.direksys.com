<?php

namespace cfdiMx\properties;

use SimpleXMLElement;

/**
 *
 */
class receptor
{
    final public static function extract(SimpleXMLElement $xml, array $namespace, $version)
    {
        $cfdi = $xml->children($namespace['cfdi']);

        $data = array(
            '@atributos' => array(
                'nombre' => (string) $cfdi->Receptor->attributes()->nombre,
                'rfc'    => (string) $cfdi->Receptor->attributes()->rfc
                )
            );

        if (isset($cfdi->Receptor->Domicilio)) {
            $data['DomicilioFiscal']['@atributos'] = array(
                'calle'        => (string) $cfdi->Receptor->Domicilio->attributes()->calle,
                'codigoPostal' => (string) $cfdi->Receptor->Domicilio->attributes()->codigoPostal,
                'colonia'      => (string) $cfdi->Receptor->Domicilio->attributes()->colonia,
                'estado'       => (string) $cfdi->Receptor->Domicilio->attributes()->estado,
                'municipio'    => (string) $cfdi->Receptor->Domicilio->attributes()->municipio,
                'noExterior'   => (string) $cfdi->Receptor->Domicilio->attributes()->noExterior,
                'pais'         => (string) $cfdi->Receptor->Domicilio->attributes()->pais
                );
        }

        return (count($data) > 0) ? $data : null;
    }
}
