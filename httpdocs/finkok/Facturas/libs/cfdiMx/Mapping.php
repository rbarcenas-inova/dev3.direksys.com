<?php

namespace cfdiMx;

use SimpleXMLElement;

/**
 * Mapping class
 *
 * - Parse the XML file depending on whitch version is loaded
 */
class Mapping
{
    private $_namespaces;
    private $_xml;
    private $_version;

    /**
     * Construct
     * @param SimpleXMLElement $xml XML Data
     */
    final public function __construct(SimpleXMLElement $xml)
    {
        $this->_namespaces = $xml->getNamespaces(true);
        $this->_xml        = $xml;

        // Version
        $this->_version = $this->version();
    }

    /**
     * Gets class properties
     * @param  string $key Property name
     * @return any    Value
     */
    final public function __get($key)
    {
        $property = "\cfdiMx\properties\\" . $key;

        return $property::extract(
            $this->_xml,
            $this->_namespaces,
            $this->_version
            );
    }

    /**
     * Gets document version
     * @return float Version
     */
    final public function version()
    {
        return (float) $this->_xml['version'];
    }

    /**
     * Gets namespaces
     */
    final public function namespaces()
    {
        return $this->_namespaces;
    }
}
