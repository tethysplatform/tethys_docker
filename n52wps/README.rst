*******************
52 North WPS Docker
*******************

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

        $ sudo docker pull ciwater/n52wps

2. Build from source:

    ::

        $ git clone https://github.com/CI-WATER/tethys_docker.git
        $ cd tethys_docker/n52wps
        $ sudo docker build -t ciwater/n52wps .

Run Container
=============

Start the 52 North Docker container as follows:

::

    $ sudo docker run --rm -it -p 8080:8080 ciwater/n52wps

OR in deamon mode with a name:

::

    $ sudo docker run -d -p 8080:8080 --name n52wps ciwater/n52wps


Browse to `<http://localhost:8080/wps>`_ to see your instance of 52North WPS running.

.. note::

    The above command will map the Docker's port 8080 to the host 8080. If your port 8080 is not available, modify the command to use a port that works for you.

See `Docker Documentation <https://docs.docker.com/>`_ for more information about how to use Docker containers.

Configuration
=============

You may pass several environmental variables to set the service metadata and the admin username and password:

::

* -e USERNAME=<ADMIN_USERNAME>
* -e PASSWORD=<ADMIN_PASSWORD>
* -e NAME=<INDIVIDUAL_NAME>
* -e POSITION=<POSITION_NAME>
* -e PHONE=<VOICE>
* -e FAX=<FACSIMILE>
* -e ADDRESS=<DELIVERY_POINT>
* -e CITY=<CITY>
* -e STATE=<ADMINISTRATIVE_AREA>
* -e POSTAL_CODE=<POSTAL_CODE>
* -e COUNTRY=<COUNTRY>
* -e EMAIL=<ELECTRONIC_MAIL_ADDRESS>

For example:

::

    $ sudo docker run -d -p 8080:8080 -e USERNAME="foo" -e PASSWORD="bar" --name n52wps ciwater/n52wps

The default values that ship with 52North will be used if these variables are not set. It is highly recommended that you change the admin username and password for production installations.






