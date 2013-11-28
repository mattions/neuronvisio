# -*- Import: -*-
from paver.easy import *
from paver.setuputils import setup
#from setuptools import setup
from setuptools import find_packages
import sys, os
import subprocess
import neuronvisio


try:
    # Optional tasks, only needed for development
    # -*- Optional import: -*-
    from paved import *
    from paved.docs import *
    import paver.virtual
    import paver.misctasks
    ALL_TASKS_LOADED = True
except ImportError, e:
    info("some tasks used for neuronvisio development could not not be imported.")
    debug(str(e))
    ALL_TASKS_LOADED = False



version = neuronvisio.__version__
authors = neuronvisio.__authors__
authors_email = neuronvisio.__authors_emails__

classifiers = [
    # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
    "Development Status :: 4 - Beta",
    "Programming Language :: Python",
    "Topic :: Scientific/Engineering :: Visualization"

    ]

install_requires = [
    # -*- Install requires: -*-
    'distribute==0.6.35',
    'pip'
    ]

entry_points="""
    # -*- Entry points: -*-
    """

# compatible with distutils of python 2.3+ or later
setup(
    name='neuronvisio',
    version=version,
    description='Neuronvisio is a Graphical User Interface for NEURON simulator environment',
    long_description=open('README.rst', 'r').read(),
    packages = ['neuronvisio', 'neuronvisio.modeldb'],
    package_dir={'neuronvisio': 'neuronvisio'},
    package_data=paver.setuputils.find_package_data(package="neuronvisio", ),
    scripts= ['bin/neuronvisio', 'bin/neuronvisio.bat', 
              'bin/neuronvisio-modeldb-updater', 'bin/neuronvisio-modeldb-updater.bat'],
    classifiers=classifiers,
    keywords='neuron, gui, pylab, 3D, visualization',
    author=authors,
    author_email=authors_email,
    url='http://neuronvisio.org',
    license='GPLv3',
    include_package_data=True,
    zip_safe=False,
    install_requires=install_requires,
    entry_points=entry_points,
    )

options(
    # -*- Paver options: -*-
    minilib=Bunch(
        extra_files=[
            # -*- Minilib extra files: -*-
            ]
        ),
    sphinx=Bunch(
        docroot='docs',
        builddir="_build",
        sourcedir=""
        ),
    )

#options.setup.package_data=paver.setuputils.find_package_data(
#    'src', package='neuronvisio', only_in_packages=False)

if ALL_TASKS_LOADED:
    @task
    @needs('generate_setup', 'minilib', 'distutils.command.sdist')
    def sdist():
        """Overrides sdist to make sure that our setup.py is generated."""
        print "Package baked."


@task
def install_dependencies():
    subprocess.call(['pip', 'install', '-r', 'requirements.txt'])


@task
@needs(['install_dependencies'])
def install():
    """We ovverride the install task, so we can use pip to install the dependencies
    """

@task
def create_CNAME():
    "creates the CNAME for the domain when deployed"
    filename = os.path.join('docs', '_build', 'html', "CNAME")
    if not os.path.exists(filename): 
        with open(filename, 'w') as f:
            f.write("neuronvisio.org\n")

@task
@needs(['docs', 'create_CNAME', 'ghpages'])
def update_docs():
    """Generate the website and updates pages on github
    """

#@task
#def upload_to_launchpad():
#    package_ver = neuronvisio.__version__
#    dist_dir = 'dist'
#    package_src_changes = 'neuronvisio_' + package_ver + '_source.changes'
#    call(['dput', 'neuronvisio-ppa', os.path.join('deb_dist', 
#                                                  package_src_changes)])
