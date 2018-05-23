<?php

namespace cfdiMx\properties;

use SimpleXMLElement;
use DB;
use Session;

/**
 *
 */
class cfdirelacionados
{
    final public static function extract(SimpleXMLElement $xml, array $namespace, $version)
    {
        $data = array();

        $cfdi = $xml->children($namespace['cfdi']);

        switch ($version) {
            case 3:
            case 3.2:
                
                break;

            case 3.3:
                if (isset($cfdi->CfdiRelacionados->CfdiRelacionado)) {
                    $tipo_rel = cfdirelacionados::getDescription((int)$cfdi->CfdiRelacionados->attributes()->TipoRelacion);
                    $data = array(
                        '@atributos' => array(
                            'TipoRelacion' => (string) $cfdi->CfdiRelacionados->attributes()->TipoRelacion.' - '.$tipo_rel
                            )
                        );
                    
                    foreach ($cfdi->CfdiRelacionados->children($namespace['cfdi']) as $key => $value) {
                        $data['CfdiRelacionados'][]['UUID'] = (string) $value->attributes()->UUID;
                    }
                }

                break;
            default:
                throw new Exception('[cfdirelacionados] - Unkown document version ' . $version);
                break;
        }

        return (count($data) > 0) ? $data : null;
    }

    private static function getDescription($id)
    {
        $e = Session::get('e');
        $this_connection = 'direksys2_e'.$e;
        $description = DB::connection($this_connection)
                            ->table('cu_relacion_cfdi')
                            ->select('description')
                            ->where('ID_relacion_cfdi', $id)
                            ->value('description');

        return $description;
    }
}
