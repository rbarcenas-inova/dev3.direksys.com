<?php


	/* ********************************************************************** */
	/* ** Functions                                                        ** */
	/* **                                                        03/31/04  ** */
	/* ********************************************************************** */
	

	#####################################################################
	################           USER MANAGER          ####################
	#####################################################################		
	function about(){
		global $in;
		global $sys;
		global $trs;
		global $va;
		$va['page_title'] = trans_txt("pageabout");
		echo build_page('about.html');
	}	
	function egw_home(){
		global $in;
		global $sys;
		global $trs;
		global $va;
		$va['page_title'] = trans_txt("pageegwhome");
		echo build_page('egw_home.html');
	}	

	


?>