============
Github-Tools
============

Github-tools works only with GitPython 0.1.7. Anything else is ok with 
0.3.1 so when deployment is needed just uninstall 0.1.7.

The discussion is going on here: https://github.com/dinoboff/github-tools/pull/20
In the meantime...

For deployment
--------------

	sudo rm /usr/local/lib/python2.6/dist-packages/git -rvd
	sudo rm /usr/local/lib/python2.6/dist-packages/GitPython-0.3.1.egg-info -rvd
	sudo pip install GitPython==0.1.7

For development
---------------

	sudo rm /usr/local/lib/python2.6/dist-packages/git -rvd
	sudo rm /usr/local/lib/python2.6/dist-packages/GitPython-0.1.7.egg-info -rvd
	sudo pip install GitPython==0.3.1-beta2


Creating the doc to preview them offline
----------------------------------------

	paver gh_pages_build_fix
	
Pushing the doc online
----------------------

	paver gh_pages_update -m "Updated the docs online"

Making the release and pushing on piPy
-------------------------------------

	paver sdist upload