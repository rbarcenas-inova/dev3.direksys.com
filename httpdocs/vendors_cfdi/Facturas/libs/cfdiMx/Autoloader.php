<?php

namespace cfdiMx;

/**
 * Autoloader class
 *
 * Example:
 * $loader = new loader();
 * $loader->register();
 */
class Autoloader
{
    private $_directories;
    private $_includePath;
    private $_namespace;
    private $_namespaceSeparator;

    /**
     * Constructor
     */
    final public function __construct()
    {

        $this->_directories        = array();
        $this->_includePath        = __DIR__;
        $this->_namespace          = 'cfdiMx';
        $this->_namespaceSeparator = '\\';
    }

    /**
     * Installs this class loader on the SPL autoload stack.
     */
    final public function register()
    {
        spl_autoload_register(array($this, 'loadClass'));
    }

    /**
     * Uninstalls this class loader from the SPL autoloader stack.
     */
    final public function unregister()
    {
        spl_autoload_unregister(array($this, 'loadClass'));
    }

    /**
     * Adds an include path.
     *
     * @param string $includePath
     */
    final public function addIncludePath($includePath)
    {
        $this->_directories[] = $includePath;
    }

    /**
     * Gets the include paths.
     *
     * @return array $_directories
     */
    final public function getIncludePath()
    {
        return $this->_directories;
    }

    /**
     * Loads the given class or interface.
     */
    final public function loadClass($className)
    {
        if (strlen($className) === 0) return false;

        $className = str_replace($this->_namespaceSeparator, DIRECTORY_SEPARATOR, $className);
        $className = str_replace($this->_namespace, '', $className);

        foreach ($this->_directories as $dir) {
            if (is_file($dir . DIRECTORY_SEPARATOR . $className . '.php')) {
                require_once $dir . DIRECTORY_SEPARATOR . $className . '.php';

                return true;
            }
        }

        return false;
    }
}
