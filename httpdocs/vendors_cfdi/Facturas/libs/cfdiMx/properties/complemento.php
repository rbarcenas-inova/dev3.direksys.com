<?php

namespace cfdiMx\properties;

use SimpleXMLElement;

/**
 *
 */
class complemento
{
    final public static function extract(SimpleXMLElement $xml, array $namespace, $version)
    {
        $data = array();
        $cfdi = $xml->children($namespace['cfdi']);

        // Donativos
        if (isset($namespace['donat'])) {
            $dna = $cfdi->Complemento->children($namespace['donat']);

            if (isset($dna->Donatarias)) {
                $data['Donatarias']['@atributos'] = array(
                    'noAutorizacion'    => $dna->Donatarias->attributes()->noAutorizacion,
                    'fechaAutorizacion' => $dna->Donatarias->attributes()->fechaAutorizacion,
                    'leyenda'           => $dna->Donatarias->attributes()->leyenda,
                    'version'           => $dna->Donatarias->attributes()->version
                    );
            }
        }

        // Impuesto local
        if (isset($namespace['implocal'])) {
            $imp = $cfdi->Complemento->children($namespace['implocal']);

            if (isset($imp->ImpuestosLocales)) {
                $data['ImpuestosLocales']['@atributos'] = array(
                    'TotaldeRetenciones' => (float) $imp->ImpuestosLocales->attributes()->TotaldeRetenciones,
                    'TotaldeTraslados'   => (float) $imp->ImpuestosLocales->attributes()->TotaldeTraslados,
                    'Version'            => (float) $imp->ImpuestosLocales->attributes()->Version,
                    );
            }

            if (isset($imp->ImpuestosLocales->RetencionesLocales)) {
                $data['ImpuestosLocales']['RetencionesLocales']['@atributos'] = array(
                    'ImpLocRetenido'  => (string) $imp->ImpuestosLocales->RetencionesLocales->attributes()->ImpLocRetenido,
                    'TasadeRetencion' => (float) $imp->ImpuestosLocales->RetencionesLocales->attributes()->TasadeRetencion,
                    'Importe'         => (float) $imp->ImpuestosLocales->RetencionesLocales->attributes()->Importe,
                    );
            }

            if (isset($imp->ImpuestosLocales->TrasladosLocales)) {
                $data['ImpuestosLocales']['TrasladosLocales']['@atributos'] = array(
                    'ImpLocTrasladado' => (string) $imp->ImpuestosLocales->TrasladosLocales->attributes()->ImpLocTrasladado,
                    'TasadeTraslado'   => (float) $imp->ImpuestosLocales->TrasladosLocales->attributes()->TasadeTraslado,
                    'Importe'          => (float) $imp->ImpuestosLocales->TrasladosLocales->attributes()->Importe,
                    );
            }
        }

        // Nomina
        if (isset($namespace['nomina'])) {
            $nomina = array();

            $nmd = $cfdi->Complemento->children($namespace['nomina']);

            // Atributos
            if (isset($nmd->Nomina)) {
                $data['Nomina']['@atributos'] = array(
                    'Antiguedad'             => (string) $nmd->Nomina->attributes()->Antiguedad,
                    'Banco'                  => (string) $nmd->Nomina->attributes()->Banco,
                    'CURP'                   => (string) $nmd->Nomina->attributes()->CURP,
                    'CLABE'                  => (string) $nmd->Nomina->attributes()->CLABE,
                    'Departamento'           => (string) $nmd->Nomina->attributes()->Departamento,
                    'FechaPago'              => (string) $nmd->Nomina->attributes()->FechaPago,
                    'FechaInicialPago'       => (string) $nmd->Nomina->attributes()->FechaInicialPago,
                    'FechaFinalPago'         => (string) $nmd->Nomina->attributes()->FechaFinalPago,
                    'FechaInicioRelLaboral'  => (string) $nmd->Nomina->attributes()->FechaInicioRelLaboral,
                    'NumDiasPagados'         => (string) $nmd->Nomina->attributes()->NumDiasPagados,
                    'NumEmpleado'            => (string) $nmd->Nomina->attributes()->NumEmpleado,
                    'NumSeguridadSocial'     => (string) $nmd->Nomina->attributes()->NumSeguridadSocial,
                    'PeriodicidadPago'       => (string) $nmd->Nomina->attributes()->PeriodicidadPago,
                    'Puesto'                 => (string) $nmd->Nomina->attributes()->Puesto,
                    'RegistroPatronal'       => (string) $nmd->Nomina->attributes()->RegistroPatronal,
                    'RiesgoPuesto'           => (string) $nmd->Nomina->attributes()->RiesgoPuesto,
                    'SalarioBaseCotApor'     => (string) $nmd->Nomina->attributes()->SalarioBaseCotApor,
                    'SalarioDiarioIntegrado' => (string) $nmd->Nomina->attributes()->SalarioDiarioIntegrado,
                    'TipoContrato'           => (string) $nmd->Nomina->attributes()->TipoContrato,
                    'TipoJornada'            => (string) $nmd->Nomina->attributes()->TipoJornada,
                    'TipoRegimen'            => (string) $nmd->Nomina->attributes()->TipoRegimen,
                    'Version'                => (float) $nmd->Nomina->attributes()->Version
                    );
            }

            // Percepciones
            if (isset($nmd->Nomina->Percepciones)) {
                $data['Nomina']['Percepciones']['@atributos'] = array(
                    'TotalGravado' => (float) $nmd->Nomina->Percepciones->attributes()->TotalGravado,
                    'TotalExento'  => (float) $nmd->Nomina->Percepciones->attributes()->TotalExento
                    );

                foreach ($nmd->Nomina->Percepciones->children($namespace['nomina']) as $key => $value) {
                    $data['Nomina']['Percepciones']['Percepcion']['@atributos'][] = array(
                        'TipoPercepcion' => (string) $value->attributes()->TipoPercepcion,
                        'Clave'          => (string) $value->attributes()->Clave,
                        'Concepto'       => (string) $value->attributes()->Concepto,
                        'ImporteGravado' => (float) $value->attributes()->ImporteGravado,
                        'ImporteExento'  => (float) $value->attributes()->ImporteExento
                        );
                }
            }

            // Deducciones
            if (isset($nmd->Nomina->Deducciones)) {
                $data['Nomina']['Deducciones']['@atributos'] = array(
                    'TotalGravado' => (float) $nmd->Nomina->Deducciones->attributes()->TotalGravado,
                    'TotalExento'  => (float) $nmd->Nomina->Deducciones->attributes()->TotalExento,
                    );

                foreach ($nmd->Nomina->Deducciones->children($namespace['nomina']) as $key => $value) {
                    $data['Nomina']['Deducciones']['Deduccion']['@atributos'][] = array(
                        'TipoDeduccion'  => (string) $value->attributes()->TipoDeduccion,
                        'Clave'          => (string) $value->attributes()->Clave,
                        'Concepto'       => (string) $value->attributes()->Concepto,
                        'ImporteGravado' => (float) $value->attributes()->ImporteGravado,
                        'ImporteExento'  => (float) $value->attributes()->ImporteExento
                        );
                }
            }

            // Incapacidades
            if (isset($nmd->Nomina->Incapacidades)) {
                foreach ($nmd->Nomina->Incapacidades->children($namespace['nomina']) as $key => $value) {
                    $data['Nomina']['Incapacidades']['Incapacidad']['@atributos'][] = array(
                        'DiasIncapacidad' => (float) $value->attributes()->DiasIncapacidad,
                        'TipoIncapacidad' => (string) $value->attributes()->TipoIncapacidad,
                        'Descuento'       => (float) $value->attributes()->Descuento
                        );
                }
            }

            // Horas Extra
            if (isset($nmd->Nomina->HorasExtras)) {
                foreach ($nmd->Nomina->HorasExtras->children($namespace['nomina']) as $key => $value) {
                    $data['Nomina']['HorasExtras']['@atributos'][] = array(
                        'Dias'          => (float) $value->attributes()->Dias,
                        'HorasExtra'    => (float) $value->attributes()->HorasExtra,
                        'ImportePagado' => (float) $value->attributes()->ImportePagado,
                        'TipoHoras'     => (string) $value->attributes()->TipoHoras
                        );
                }
            }
        }

        // Timbre Fiscal
        if (isset($namespace['tfd'])) {
            $tfd  = $cfdi->Complemento->children($namespace['tfd']);

            if (isset($tfd->TimbreFiscalDigital)) {
                $data['TimbreFiscalDigital']['@atributos'] = array(
                    'FechaTimbrado'    => (string) $tfd->TimbreFiscalDigital->attributes()->FechaTimbrado,
                    'noCertificadoSAT' => (string) $tfd->TimbreFiscalDigital->attributes()->noCertificadoSAT,
                    'selloCFD'         => (string) $tfd->TimbreFiscalDigital->attributes()->selloCFD,
                    'selloSAT'         => (string) $tfd->TimbreFiscalDigital->attributes()->selloSAT,
                    'UUID'             => (string) $tfd->TimbreFiscalDigital->attributes()->UUID,
                    'version'          => (float) $tfd->TimbreFiscalDigital->attributes()->version
                    );
            }
        }

        return (count($data) > 0) ? $data : null;
    }
}
