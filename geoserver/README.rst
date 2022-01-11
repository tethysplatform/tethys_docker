****************
GeoServer Docker
****************

This Docker provides a GeoServer instance. The Dockerfile and context can be found in this repository:

::

    https://github.com/CI-WATER/tethys_docker

.. note::

    There are several Dockerfiles in this repository. The PostGIS Dockerfile is in the ``geoserver`` directory.

Installation
============

There are two ways to install this Docker:

1. Pull image from Docker repository:

    ::

        $ sudo docker pull ciwater/geoserver

2. Build from source:

    ::

        $ git clone https://github.com/CI-WATER/tethys_docker.git
        $ cd tethys_docker/geoserver
        $ sudo docker build -t ciwater/geoserver .

Run Container
=============

Start the GeoServer Docker container as follows:

::

    $ sudo docker run --rm -it -p 8080:8080 ciwater/geoserver

OR in deamon mode with a name:

::

    $ sudo docker run -d -p 8080:8080 --name postgis ciwater/geoserver

Browse to `<http://localhost:8080/geoserver/web/>`_ to see your running geoserver.

.. note::

    The above command will map the Docker's port 8080 to the host 8080. If your port 8080 is not available, modify the command to use a port that works for you. See `Docker Documentation <https://docs.docker.com/>`_ for more information about how to use Docker containers.


Build
-----

1. Download the latest 64-bit JDK 7 tarball for linux (e.g.: jdk-7u<version>-linux-x64.tar.gz) from here: https://www.oracle.com/java/technologies/javase/javase7-archive-downloads.html

2. Place the tarball in the `geoserver` directory, but do not commit.

3. Change into the `geoserver` directory:

::

    cd

4. Run the build command:

::

    docker build -t tethysplatform/geoserver .