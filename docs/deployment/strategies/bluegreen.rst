=====================
Blue/Green Deployment
=====================

.. autoclass:: shpkpr.deployment.BlueGreenDeployment
   :members: execute

.. _default-template-bluegreen:

---------------------------
Blue/Green default template
---------------------------

shpkpr includes a set of default templates which are used when a custom template is not supplied by the user at runtime. The default template used for blue/green deployments is included below for reference purposes.

.. seealso::

   :ref:`default-template-standard`
       Default template for standard deployments (from which this one extends).

.. literalinclude:: ../../../shpkpr/resources/templates/marathon/default/bluegreen.json.tmpl
   :language: jinja
