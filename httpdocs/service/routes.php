<?php
use	Symfony\Component\Routing\Route;
use	Symfony\Component\Routing\RouteCollection;

$routes = new RouteCollection();

$routes->add('main.index', new Route('/{tracking}', [
	'tracking' => '',
	'_controller' => function($request){
		$tracking = $request->attributes->get('tracking');
		if($tracking == '')
			return json_encode(new StdClass());
		$ups = new \Service\UPS\UPS();
		return json_encode($ups->get($tracking));
	}
]));

return $routes;
