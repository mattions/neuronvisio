==========
Deployment
==========

To update the docs just do 

    paver docs
    
To submit it to github

    paver ghpages
    
In one go

    paver update_docs


Making the release and pushing on piPy
-------------------------------------

	paver sdist upload
	

Tools used for development
--------------------------

Paved==0.4.1
Paver==1.0.5
Sphinx==1.1.3
ghp-import==0.1.8
