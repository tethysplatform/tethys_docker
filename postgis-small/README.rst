**************
PostGIS Docker
**************

This Docker provides a PostgreSQL instance with PostGIS enabled. The Dockerfile and context can be found in this repository:

::

    https://github.com/CI-WATER/tethys_docker

.. note::

    There are several Dockerfiles in this repository. The PostGIS Dockerfile is in the ``postgis`` directory.

Installation
============

There are two ways to install this Docker:

1. Pull image from Docker repository:

    ::

        $ sudo docker pull ciwater/postgis

2. Build from source:

    ::

        $ git clone https://github.com/CI-WATER/tethys_docker.git
        $ cd tethys_docker/postgis
        $ sudo docker build -t ciwater/postgis .

Run Container
=============

Start the PostGIS Docker container as follows:

::

    $ sudo docker run --rm -it -p 5432:5432 ciwater/postgis

OR in deamon mode with a name:

::

    $ sudo docker run -d -p 5432:5432 --name postgis ciwater/postgis

The database will be available on port 5432. A superuser is automatically created called "tethys_super" with password "pass". You can modify the password using environmental variables (see Configuration section).

.. note::

    The above command will map the Docker's port 5432 to the host 5432. If your port 5432 is not available, modify the command to use a port that works for you. See `Docker Documentation <https://docs.docker.com/>`_ for more information about how to use Docker containers.

Configuration
=============

The PostGIS Docker automatically initializes with the three database users that are needed for Tethys Platform:

* tethys_default
* tethys_db_manager
* tethys_super

The default password for each is "pass". For production, you will obviously want to change these passwords. Do so using the appropriate environmental variable:

::

* -e TETHYS_DEFAULT_PASS=<TETHYS_DEFAULT_PASS>
* -e TETHYS_DB_MANAGER_PASS=<TETHYS_DB_MANAGER_PASS>
* -e TETHYS_SUPER_PASS=<TETHYS_SUPER_PASS>

For example:

::

    $ sudo docker run -d -p 5432:5432 -e TETHYS_DEFAULT_PASS="pass" -e TETHYS_DB_MANAGER_PASS="pass" -e TETHYS_SUPER_PASS="pass" --name postgis ciwater/postgis






