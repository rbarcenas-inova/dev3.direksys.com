<?php

namespace cfdiMx\properties;

use SimpleXMLElement;

/**
 *
 */
class conceptos
{
    final public static function extract(SimpleXMLElement $xml, array $namespace, $version)
    {
        $cfdi = $xml->children($namespace['cfdi']);

        $data = array();

        foreach ($cfdi->Conceptos->children($namespace['cfdi']) as $key => $value) {
            if(isset($value->InformacionAduanera)){
                $aduanas = (object)(array)$value;
                $aduanas = $aduanas->InformacionAduanera;
                $valAdd = null;
                if(is_array($aduanas)){
                    foreach ($aduanas as $key => $v) {
                        $valAdd[] = (array)$v->attributes();
                    }
                }else{
                    $valAdd[] = (array)$aduanas->attributes();
                }
                $data['Concepto']['@atributos'][] = array(
                    'cantidad'      => (float) $value->attributes()->cantidad,
                    'descripcion'   => (string) $value->attributes()->descripcion,
                    'importe'       => (float) $value->attributes()->importe,
                    'unidad'        => (string) $value->attributes()->unidad,
                    'valorUnitario' => (float) $value->attributes()->valorUnitario,
                    'aduanas'=>$valAdd
                );
            }else{
                $data['Concepto']['@atributos'][] = array(
                    'cantidad'      => (float) $value->attributes()->cantidad,
                    'descripcion'   => (string) $value->attributes()->descripcion,
                    'importe'       => (float) $value->attributes()->importe,
                    'unidad'        => (string) $value->attributes()->unidad,
                    'valorUnitario' => (float) $value->attributes()->valorUnitario,
                );
            }
            $aduanas = (object)(array)$value;
            if (isset($value->CuentaPredial)) {
                $data['Concepto']['@atributos'][count($data['Concepto']['@atributos'])-1]['CuentaPredial']['@atributos'] = array(
                    'numero' => (string) $value->CuentaPredial->attributes()->numero
                    );
            }
        }
        return (count($data) > 0) ? $data : null;
    }
}
