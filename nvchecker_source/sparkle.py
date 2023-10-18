# MIT licensed
# Copyright (c) 2020 lilydjwg <lilydjwg@gmail.com>, et al.
# Copyright (c) 2020 Sunlei <guizaicn@gmail.com>

from xml.etree import ElementTree

from nvchecker.api import session, RichResult

XML_NAMESPACE = 'http://www.w3.org/XML/1998/namespace'
SPARKLE_NAMESPACE = 'http://www.andymatuschak.org/xml-namespaces/sparkle'

async def get_version(name, conf, *, cache, **kwargs):
  sparkle = conf['sparkle']
  release_notes_language = conf.get('release_notes_language', 'en')
  return await cache.get((sparkle, release_notes_language), get_version_impl)


async def get_version_impl(info):
  sparkle, release_notes_language = info
  res = await session.get(sparkle)
  root = ElementTree.fromstring(res.body).find('./channel/item[1]')
  item = root.find('./enclosure')

  version_string = item.get(f'{{{SPARKLE_NAMESPACE}}}shortVersionString')
  build_number = item.get(f'{{{SPARKLE_NAMESPACE}}}version')

  if (version_string and version_string.isdigit()) and (
    build_number and not build_number.isdigit()
  ):
    version_string, build_number = build_number, version_string

  version = []

  if version_string:
    version.append(version_string)
  if build_number and (build_number not in version):
    version.append(build_number)

  version_str = '-'.join(version) if version else None

  release_notes_link = None
  for release_notes in root.findall(f'./{{{SPARKLE_NAMESPACE}}}releaseNotesLink'):
    language = release_notes.get(f'{{{XML_NAMESPACE}}}lang')

    # If the release notes have no language set, store them, but keep looking for our preferred language
    if language is None:
      release_notes_link = release_notes.text.strip()

    # If the release notes match our preferred language, store them and stop looking
    if language == release_notes_language:
      release_notes_link = release_notes.text.strip()
      break

  if release_notes_link is not None:
    return RichResult(
      version = version_str,
      url = release_notes_link,
    )
  else:
    return version_str
