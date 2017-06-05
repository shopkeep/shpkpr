===================
Standard Deployment
===================

.. autoclass:: shpkpr.deployment.StandardDeployment
   :members: execute

.. _default-template-standard:

-------------------------
Standard default template
-------------------------

shpkpr includes a set of default templates which are used when a custom template is not supplied by the user at runtime. The default template used for standard deployments is included below for reference purposes.

.. literalinclude:: ../../../shpkpr/resources/templates/marathon/default/standard.json.tmpl
   :language: yaml+jinja
