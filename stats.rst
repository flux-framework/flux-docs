.. _stats:

=================
Stats Quick Start
=================

Flux includes an optional instrumentation facility to collect internal metrics, or "stats",
and send them to an aggregator for eventual display in a front end graphing tool such as Graphite.
The internal stats collection in Flux is built on the `statsd <https://github.com/statsd/statsd>`_ protocol and
follows the typing convention used by `brubeck <https://github.com/lukepalmer/brubeck>`_.
Flux stats supports three metric types: counters, gauges, and timings.

 * Counter - An integer value that will, on the back end (brubeck), send the count and reset to 0 at each flush. It calculates the change from the value sent at the previous flush. An example of where to use a counter is the builtin message counters that are part of each ``flux_t`` handle. The counts will continually increase and brubeck will handle calculating the count sent in the interval.
 * Gauge   - An integer that takes an arbitrary value and maintains its value until it is set again. Gauges can also take incremental values in the form of a + or - in front of the value which increments the previously stored value. An example of where to use a gauge is to track the current size of the broker's content-cache. At each point, the cache's sizes are independent of each other.
 * Timing  - A double value which represents the time taken for a given task in ms. An example of where to use a timer is timing the length of asynchronous loads in the broker's content-cache. The cache entry can keep track of when the load was started and then calculate and send the time taken once the entry is loaded.

For more information on statsd types see the `statsd docs <https://github.com/statsd/statsd/blob/master/docs/metric_types.md>`_.

--------------------------
Running Brubeck & Graphite
--------------------------

Two methods for starting brubeck for stats aggregation and Graphite for stats display are presented below.
If possible, it is recommended to use the docker method. Both methods configure brubeck to receive stats
from Flux on a udp port (Docker uses 8125 and the packages/source setup uses 8126), and
graphite to receive stats sent from brubeck and display them on a local web server which can be viewed
at ``http://127.0.0.1``.

^^^^^^^^^^^^
Using Docker
^^^^^^^^^^^^

.. code-block:: console

  $ docker pull graphiteapp/graphite-statsd
  $ docker run -d \
    --name graphite \
    --restart=always \
    -p 80:80 \
    -p 2003-2004:2003-2004 \
    -p 2023-2024:2023-2024 \
    -p 8125:8125/udp \
    -p 8126:8126 \
    -e BRUBECK=1 \
    graphiteapp/graphite-statsd

^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Installing From Packages and Source
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

**Installing Brubeck**

Brubeck is a statsd-compatible metric aggregator that sits in the middle of the stack between flux and a frontend tool like Graphite.

.. code-block:: console

  $ git clone git@github.com:lukepalmer/brubeck.git
  # or git clone  https://github.com/lukepalmer/brubeck.git
  $ cd brubeck
  $ ./script/bootstrap
  $ cp config.default.json.example config.default.json
  $ make test

If all of the tests pass then it's time to move on to the frontend and third piece of the stack, Graphite.

**Installing Graphite**

Install Graphite from your local package manager.

.. code-block:: console

  $ sudo apt-get update && sudo apt-get upgrade
  $ sudo apt-get install -y graphite-carbon graphite-web

  # or
  $ sudo yum update
  $ sudo yum install graphite-carbon graphite-web

Graphite installs many config files each at their own location, but they can all be found in the ``/etc/carbon/carbon.conf`` file.
Take a look, and keep note of these directories for later.

.. code-block:: console

  # print all enabled config options
  $ grep '^[^#]' /etc/carbon/carbon.conf

  # you should see something similar to this
  [cache]
  STORAGE_DIR    = /var/lib/graphite/
  LOCAL_DATA_DIR = /var/lib/graphite/whisper/
  CONF_DIR       = /etc/carbon/
  LOG_DIR        = /var/log/carbon/
  PID_DIR        = /var/run/

Next, in order to run the Graphite Web app, you will need to change the default secret key from ``MY_SECRET`` to something else.
It doesn't matter what you change it to, but you **MUST** change it or the web app will fail to launch.

.. code-block:: console

  $ sudo $EDITOR /etc/graphite/local_settings.py
  SECRET_KEY = 'MY_SECRET' # enter your own key

Next you will need to create the ``Whisper`` database for Graphite to use. However, there are a couple of known issues.
So, try creating the database.

.. code-block:: console

  $ sudo /usr/lib/python3/dist-packages/django/bin/django-admin.py migrate --settings=graphite.settings

The first error you may see is an ImportError from some of the Graphite files.

.. code-block:: console

  ...
  File "/usr/lib/python3/dist-packages/graphite/render/urls.py", line 16, in
  from . import views
  File "/usr/lib/python3/dist-packages/graphite/render/views.py", line 23, in
  from cgi import parse_qs
  ImportError: cannot import name 'parse_qs' from 'cgi' (/usr/lib/python3.8/cgi.py)

  # fix the ImportError
  $ sudo sed -i 's/from cgi import parse_qs/from urllib.parse import parse_qs/' \
    /usr/lib/python3/dist-packages/graphite/render/views.py

The second issue you may encounter is a SystemCheckError from django which can be fixed by changing the path in the ``app_settings.py`` file.

.. code-block:: console

  SystemCheckError: System check identified some issues:
  ERRORS:
  ?: (admin.E406) 'django.contrib.messages' must be in INSTALLED_APPS in order to use the admin application.

  # fix the SystemCheckError
  $ sudo sed -i -E "s/('django.contrib.contenttypes')/\1,\n  'django.contrib.messages'/" \
    $(find / -name app_settings.py 2>/dev/null)

Now you should be able to create the Whisper database.

.. code-block:: console

  $ sudo /usr/lib/python3/dist-packages/django/bin/django-admin.py migrate --settings=graphite.settings


And you'll have to give graphite (``_graphite``) access to some necessary files.

.. code-block:: console

  $ sudo chown -R _graphite:_graphite /var/lib/graphite/
  $ sudo chown -R _graphite:_graphite /var/log/graphite/

**Installing Apache2**

The next thing you need to run Graphite's Web app is a web server. Here I'll show you how to set up ``Apache2``.

.. code-block:: console

  $ sudo apt-get install -y apache2 libapache2-mod-wsgi-py3
  $ sudo cp /usr/share/graphite-web/apache2-graphite.conf /etc/apache2/sites-available
  $ sudo a2dissite 000-default
  Site 000-default disabled.
  $ sudo a2ensite apache2-graphite
  Enabling site apache2-graphite.
  $ sudo systemctl reload apache2

If everything went well you should be able to see the graphite dashboard by going to ``127.0.0.1`` or ``0.0.0.0`` in your web browser

-------------------------------
Configuring Graphite (Optional)
-------------------------------

By default Graphite will plot points once per minute. For use within flux, one minute is a long time and often causes some loss of information.
To increase the resolution and change the interval at which Graphite (really carbon) plots data there are a few things that need to be done.

^^^^^^
Docker
^^^^^^

.. code-block:: console

  $ docker stop graphite

  # find the configuration directory
  # listed as "Source"
  $ docker inspect graphite | jq '.[].Mounts[] | select(.Destination == "/opt/graphite/conf")'
  {
    "Type": "volume",
    "Name": "73025f5bcf4c9d761be5eec05cd8ed4169ef0028569ce130d84b69ce46f6d7c8",
    "Source": "/var/lib/docker/volumes/73025f5bcf4c9d761be5eec05cd8ed4169ef0028569ce130d84b69ce46f6d7c8/_data",
    "Destination": "/opt/graphite/conf",
    "Driver": "local",
    "Mode": "",
    "RW": true,
    "Propagation": ""
  }

  $ sudo vim $Source/storage-schemas.conf
  # comment out this default
  #[default_1min_for_1day]
  #pattern = .*
  #retentions = 60s:1d

  # catch all metrics that start with 'flux'
  # and retain each data point as 1s
  [flux]
  pattern = ^flux.*
  retentions = 1s:3d

  # remove the old whisper files
  $ cd $(docker inspect graphite | \
    jq '.[].Mounts[] | select(.Destination == "/opt/graphite/storage") | .Source' && \
    sudo rm -rf whisper/*

  # restart the docker image and the new configuration should take effect
  $ docker start graphite

^^^^^^^^^^^^^^^
Packages/Source
^^^^^^^^^^^^^^^

First make sure that the carbon cache is enable on boot.

.. code-block:: console

  $ sudo vim /etc/default/graphite-carbon
  # set to true
  CARBON_CACHE_ENABLED=true

Next, you will need to edit carbon's config file and set the specific you want. You can find specifics on the configurations `here <https://graphite.readthedocs.io/en/stable/config-carbon.html>`_.
The carbon config file is stored in the ``CONF_DIR`` that was found earlier.

.. code-block:: console

  $ sudo vim /etc/carbon/storage-schemas.conf
  # comment out this default
  #[default_1min_for_1day]
  #pattern = .*
  #retentions = 60s:1d

  # catch all metrics that start with 'flux'
  # and retain each data point as 1s
  [flux]
  pattern = ^flux.*
  retentions = 1s:3d

Then you will need to clear out any existing whisper files in the database which is store in the ``LOCAL_DATA_DIR`` found earlier.

.. code-block:: console

  $ sudo rm -rf /val/lib/graphite/whisper/*

Now restart the carbon daemon and the new configuration should take effect.

.. code-block:: console

  $ sudo systemctl restart carbon-cache

--------------------------------
Running Stats Collection in Flux
--------------------------------

Once you have brubeck and Graphite setup and Graphite running there are only two more things left to be able to get stats from Flux.
First you will need to set the ``FLUX_FRIPP_STATSD`` environment variable with the endpoint of the aggregator (brubeck in this case).
If you just used the default config for brubeck as suggested earlier, the endpoint is ``127.0.0.1:8126``. If you used the docker setup the
endpoint is ``127.0.0.1:8125``.

.. code-block:: console

  $ export FLUX_FRIPP_STATSD=ipaddr:port

The second thing needed is to have brubeck running. If you used the recommended docker setup, brubeck will already be running, but
if you installed from source you need to launch brubeck in order to receive stats from a running Flux instance.

