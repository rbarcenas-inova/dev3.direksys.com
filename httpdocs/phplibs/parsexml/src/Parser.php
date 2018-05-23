<?php

namespace cfdiMx;

use Exception;
use JsonSerializable;
use SimpleXMLElement;

/**
 *
 */
class Parser implements JsonSerializable
{
    private $_mapping;

    /**
     * Construct
     * @param string $file Path to the xml file
     */
    final public function __construct($file)
    {
        if (!is_file($file)) {
            $xml = new SimpleXMLElement($file);
        }else{
            $xml = new SimpleXMLElement(file_get_contents($file));
        }
        // Gets mapping object
        $this->_mapping = new Mapping($xml);
    }

    /**
     * JSON Serialize method
     * @return array XML Parse data
     */
    final public function jsonSerialize()
    {
        // print_r($this->_mapping->addenda);
        return array(
            'Comprobante' => array(
                '@atributos' => array(
                    'fecha'             => $this->_mapping->fecha,
                    'folio'             => $this->_mapping->folio,
                    'serie'             => $this->_mapping->serie,
                    'TipoDeComprobante' => $this->_mapping->TipoDeComprobante,
                    'subtotal'          => $this->_mapping->subTotal,
                    'descuento'         => $this->_mapping->descuento,
                    'total'             => $this->_mapping->total,
                    'moneda'            => $this->_mapping->moneda,
                    'TipoCambio'        => $this->_mapping->TipoCambio,
                    'condicionesDePago' => $this->_mapping->condicionesDePago,
                    'noCertificado'     => $this->_mapping->noCertificado,
                    'certificado'       => $this->_mapping->certificado,
                    'formaDePago'       => $this->_mapping->formaDePago,
                    'metodoDePago'      => $this->_mapping->metodoDePago,
                    'NumCtaPago'        => $this->_mapping->NumCtaPago,
                    'LugarExpedicion'   => $this->_mapping->LugarExpedicion,
                    'sello'             => $this->_mapping->sello,
                    'version'           => $this->_mapping->version()
                    ),
                '@namespaces' => $this->_mapping->namespaces(),
                'Emisor'      => $this->_mapping->emisor,
                'Receptor'    => $this->_mapping->receptor,
                'Conceptos'   => $this->_mapping->conceptos,
                'Impuestos'   => $this->_mapping->impuestos,
                'Complemento' => $this->_mapping->complemento,
                'Addenda'=>$this->_mapping->addenda
                )
            );
    }
}
