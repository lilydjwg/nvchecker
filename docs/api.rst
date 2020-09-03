``nvchecker.api`` --- The source plugin API
===========================================

.. automodule:: nvchecker.api
   :members:
   :imported-members:
   :undoc-members:

.. py:data:: session
   :type: nvchecker.httpclient.base.BaseSession

   The object to send out HTTP requests, respecting various options in the configuration entry.

.. automodule:: nvchecker.httpclient.base
   :members: BaseSession, Response
   :undoc-members:

.. autodata:: nvchecker.api.proxy
.. autodata:: nvchecker.api.user_agent
.. autodata:: nvchecker.api.tries
