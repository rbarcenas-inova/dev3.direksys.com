<?php
namespace Service\Tools;

use Doctrine\ORM\Tools\Setup,
	Doctrine\ORM\EntityManager,
	Doctrine\ORM\Configuration,
	Doctrine\Common\Cache\ArrayCache,
	Doctrine\ORM\Mapping\Driver\DatabaseDriver,
	Doctrine\ORM\Tools\DisconnectedClassMetadataFactory,
	Doctrine\ORM\Tools\EntityGenerator,
	Service\Tools\Config;

class DB{
	public static $em = null;

	public static function model($modelName){
		$em = self::getEntityManager();
		try{
			return $em->getRepository($modelName);
		}catch(Exception $e){
			error_log("ERROR ------------------- \n".$e->getTraceAsString(), 0);
			exit($e->getTraceAsString());
		}
	}
	public static function getConnection($connName = ''){
		$em = self::getEntityManager($connName);
		return $em->getConnection();
	}
	
	public static function generateEntities($tablename = '', $connName = ''){
		// $config = Config::getApplication();
		$config = Config::getDireksys();
		if($connName == ''){
			$connName = Config::getApplication('default_db');
		}
		$doctrineConfig = Config::getDoctrine();

		$em = self::getEntityManager();
		$conn = $em->getConnection();
		$conn->getDatabasePlatform()->registerDoctrineTypeMapping('enum', 'string');
		$em ->getConfiguration()
		  	->setMetadataDriverImpl(
				new DatabaseDriver(	$em->getConnection()->getSchemaManager())
			);
		if($tablename != '')
			$conn->getConfiguration()->setFilterSchemaAssetsExpression("/^".$tablename."/");
		$cmf = new DisconnectedClassMetadataFactory();
		$cmf->setEntityManager($em);
		$metadata = $cmf->getAllMetadata();   
		// $metadata = $cmf->doLoadMetadata('sl_entershipments');  
		// $metadata = $cmf->getMetadataFor('sl_entershipments');   
		$generator = new EntityGenerator();
		$generator->setUpdateEntityIfExists(true);
		$generator->setGenerateStubMethods(true);
		$generator->setGenerateAnnotations(true);

		$folderEntities = $doctrineConfig->entity_files. '/' . $connName;

		$generator->generate($metadata, $folderEntities);
	}

	// Controlador de Entidades de Doctrine ORM
	public static function getEntityManager($connName = ''){
		if(!is_null(self::$em))
			return self::$em;
		// Direksys Support
		$cfg = Config::getDireksys();
		if($connName == ''){
			$connName = Config::getApplication('default_db');
		}
		// $dbConfig = Config::getDatabases($connName);
		$doctrineConfig = Config::getDoctrine();

		$folderEntities = $doctrineConfig->entity_files. '/' . $connName;
		$folderProxy = $doctrineConfig->proxy_files. '/' . $connName;

		$paths = array($folderEntities);
		$isDevMode = false;
		$dbParams = array(
		    'driver'   => 'pdo_mysql',
		    'host'	   => $cfg->dbi_host,
		    'user'     => $cfg->dbi_user,
		    'password' => $cfg->dbi_pw,
		    'dbname'   => $cfg->dbi_db,
		);
	    $config = new Configuration();
	    $cache = new ArrayCache();
	    $config->setMetadataCacheImpl($cache);
	    $driverImpl = $config->newDefaultAnnotationDriver($folderEntities,false);
	    $config->setMetadataDriverImpl($driverImpl);
	    $config->setQueryCacheImpl($cache);
	 
	    // Proxy configuration
	    $config->setProxyDir($folderProxy);
	    $config->setProxyNamespace('Proxies');
 
		$entityManager = EntityManager::create($dbParams, $config);
		self::$em = $entityManager;
		return $entityManager;
	}
}