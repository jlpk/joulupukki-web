============
 V1 Web API
============

Builds
======

.. rest-controller:: joulupukki.controllers.v1.builds:BuildsController
      :webprefix: /v1/builds

.. rest-controller:: joulupukki.controllers.v1.builds:LogBuildController
      :webprefix: /v1/builds/(build)/log

.. rest-controller:: joulupukki.controllers.v1.builds:DistrosBuildController
      :webprefix: /v1/builds/(build)/distro

.. rest-controller:: joulupukki.controllers.v1.builds:DistroBuildController
      :webprefix: /v1/builds/(build)/distro/(distro)

.. rest-controller:: joulupukki.controllers.v1.builds:LogDistroBuildController
      :webprefix: /v1/builds/(build)/distro/(distro)/log

.. rest-controller:: joulupukki.controllers.v1.builds:DownloadDistroBuildController
      :webprefix: /v1/builds/(build)/distro/(distro)/download

.. autotype:: joulupukki.controllers.v1.datamodel.build.Build
      :members:
