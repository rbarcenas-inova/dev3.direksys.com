<?php

namespace cfdiMx\properties;

use SimpleXMLElement;

/**
 *
 */
class emisor
{
    final public static function extract(SimpleXMLElement $xml, array $namespace, $version)
    {
        $cfdi = $xml->children($namespace['cfdi']);

        $data = array(
            '@atributos' => array(
                'nombre' => (string) $cfdi->Emisor->attributes()->nombre,
                'rfc'    => (string) $cfdi->Emisor->attributes()->rfc
                )
            );

        if (isset($cfdi->Emisor->DomicilioFiscal)) {
            $data['DomicilioFiscal']['@atributos'] = array(
                'calle'        => (string) $cfdi->Emisor->DomicilioFiscal->attributes()->calle,
                'codigoPostal' => (string) $cfdi->Emisor->DomicilioFiscal->attributes()->codigoPostal,
                'colonia'      => (string) $cfdi->Emisor->DomicilioFiscal->attributes()->colonia,
                'estado'       => (string) $cfdi->Emisor->DomicilioFiscal->attributes()->estado,
                'municipio'    => (string) $cfdi->Emisor->DomicilioFiscal->attributes()->municipio,
                'noExterior'   => (string) $cfdi->Emisor->DomicilioFiscal->attributes()->noExterior,
                'pais'         => (string) $cfdi->Emisor->DomicilioFiscal->attributes()->pais
                );
        }

        if (isset($cfdi->Emisor->ExpedidoEn)) {
            $data['ExpedidoEn']['@atributos'] = array(
                'calle'        => (string) $cfdi->Emisor->ExpedidoEn->attributes()->calle,
                'codigoPostal' => (string) $cfdi->Emisor->ExpedidoEn->attributes()->codigoPostal,
                'colonia'      => (string) $cfdi->Emisor->ExpedidoEn->attributes()->colonia,
                'estado'       => (string) $cfdi->Emisor->ExpedidoEn->attributes()->estado,
                'municipio'    => (string) $cfdi->Emisor->ExpedidoEn->attributes()->municipio,
                'noExterior'   => (string) $cfdi->Emisor->ExpedidoEn->attributes()->noExterior,
                'pais'         => (string) $cfdi->Emisor->ExpedidoEn->attributes()->pais
                );
        }

        if (isset($cfdi->Emisor->RegimenFiscal)) {
            $data['RegimenFiscal']['@atributos'] = array(
                'Regimen' => (string) $cfdi->Emisor->RegimenFiscal->attributes()->Regimen
                );
        }

        return (count($data) > 0) ? $data : null;
    }
}
