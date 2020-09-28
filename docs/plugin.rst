How to develop a source plugin for nvchecker
============================================

.. contents::
   :local:

Source plugins enable nvchecker to discover software version strings in
additional ways.

Where to put the plugins
------------------------

They are Python modules put in any directories named ``nvchecker_source`` in
``sys.path``. This is called namespace packages introduced by `PEP 420 <https:
//www.python.org/dev/peps/pep-0420/>`_. For local use,
``~/.local/lib/pythonX.Y/site-packages/nvchecker_source`` is a good place, or
you can define the ``PYTHONPATH`` environment variable and put nvchecker source
plugins there inside a ``nvchecker_source`` directory.

Plugins are referenced by their names in the configuration file (``source = "xxx"``).
If multiple plugins have the same name, the first one in ``sys.path`` will be used.

How to write a simple plugin
----------------------------

For simple situations, you need to define an async function with the following signature::

  async def get_version(
    name: str, conf: Entry, *,
    cache: AsyncCache, keymanager: KeyManager,
    **kwargs,
  ) -> VersionResult:
    ...

Those types are imported from :mod:`nvchecker.api`.

``name`` is the table keys in the configuration file, and ``conf`` is a dict of
the content of that table. You should not modify this dict.

``cache`` is an :class:`AsyncCache <nvchecker.api.AsyncCache>` object that
caches results for you. Every plugin has its own ``cache`` object so that cache
keys won't conflict.

``keymanager`` is a :class:`KeyManager <nvchecker.api.KeyManager>` object that
you can call :meth:`.get_key(name) <nvchecker.api.KeyManager.get_key>` to get
the key (token) from the keyfile.

There may be additional keyword arguments in the future so ``**kwargs`` should be used.

If you want to send an HTTP request, it's preferred to use :meth:
`cache.get_json <nvchecker.api.AsyncCache.get_json>` or the :data:
`nvchecker.api.session` object. It will use the auto-selected HTTP backend and
handle the ``proxy`` option automatically.

For details about these objects, see :mod:`the API documentation <nvchecker.api>`,
or take existing source plugins as examples.

How to write a more powerful plugin
-----------------------------------

You may want more control in your source plugin, e.g. to do batch requests. To
do this, you provide a class instead::

  class Worker(BaseWorker):
    async def run(self) -> None:
      ...


You will have the following in the attributes::

  token_q: Queue[bool],
  result_q: Queue[RawResult],
  tasks: List[Tuple[str, Entry]],
  keymanager: KeyManager,

You are expected to process :attr:`tasks <nvchecker.api.BaseWorker.tasks>` and
put results in :attr:`result_q <nvchecker.api.BaseWorker.result_q>`. See
``nvchecker_source/none.py`` for the simplest example, and
``nvchecker_source/aur.py`` for a complete, batching example.

For details about these objects, see :mod:`the API documentation <nvchecker.api>`.

You can also receive a configuration section from the configuration as
``__config__.source.SOURCE_NAME``, where ``SOURCE_None`` is what your plugin is
called. This can be used to specify a mirror site for your plugin to use, e.g.
the ``npm`` plugin accepts the following config::

  [__config__.source.npm]
  registry = "https://registry.npm.taobao.org"

When such a configuration exists for your plugin, you need to define a function
named ``configure`` to receive it::

  def configure(config):
    '''use the "config" dict in some way'''
    ...
