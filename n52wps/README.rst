*******************
52 North WPS Docker
*******************

.. warning::

    This Docker is currently unstable. Use at your own risk.

This Docker provides a 52 North Web Processing Service instance with the GRASS and Sextante backends enabled. The Dockerfile and context can be found in this repository:

 ::

    https://github.com/CI-WATER/tethys_docker

.. note::

    There are several Dockerfiles in this repository. The 52 North Dockerfile is in the ``n52wps`` directory.

Installation
============

There are two ways to install this Docker:

1. Pull image from Docker repository:

    ::

        $ sudo docker pull ciwater/n52wps:unstable

2. Build from source:

::

    $ git clone https://github.com/CI-WATER/tethys_docker.git
    $ cd tethys_docker/n52wps
    $ sudo docker build -t ciwater/n52wps .

Run Container
=============

Start the 52 North Docker container as follows:

::

    $ sudo docker run --rm -it -p 8080:8080 ciwater/n52wps:unstable

.. note::

    The above command will map the Docker's port 8080 to the host 8080. If your port 8080 is not taken, modify the command to use a port that works for you.

The unstable version of the Docker does not start Tomcat automatically and it should give you a bash as the root user (for debugging). Start Tomcat as follows:

::

    # service tomcat7 start


