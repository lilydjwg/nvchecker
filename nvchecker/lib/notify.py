# MIT licensed
# Copyright (c) 2013-2017 lilydjwg <lilydjwg@gmail.com>, et al.

'''
调用 libnotify
'''

__all__ = ["set", "show", "update", "set_timeout", "set_urgency"]

from ctypes import *
from threading import Lock
import atexit

NOTIFY_URGENCY_LOW = 0
NOTIFY_URGENCY_NORMAL = 1
NOTIFY_URGENCY_CRITICAL = 2
UrgencyLevel = {NOTIFY_URGENCY_LOW, NOTIFY_URGENCY_NORMAL, NOTIFY_URGENCY_CRITICAL}

libnotify = None
gobj = None
libnotify_lock = Lock()
libnotify_inited = False

class obj: pass
notify_st = obj()

def set(summary=None, body=None, icon_str=None):
  with libnotify_lock:
    init()

  if summary is not None:
    notify_st.summary = summary.encode()
  notify_st.body = notify_st.icon_str = None
  if body is not None:
    notify_st.body = body.encode()
  if icon_str is not None:
    notify_st.icon_str = icon_str.encode()

  libnotify.notify_notification_update(
    notify_st.notify,
    notify_st.summary,
    notify_st.body,
    notify_st.icon_str,
  )

def show():
  libnotify.notify_notification_show(notify_st.notify, c_void_p())

def update(summary=None, body=None, icon_str=None):
  if not any((summary, body)):
    raise TypeError('at least one argument please')

  set(summary, body, icon_str)
  show()

def set_timeout(self, timeout):
  '''set `timeout' in milliseconds'''
  libnotify.notify_notification_set_timeout(notify_st.notify, int(timeout))

def set_urgency(self, urgency):
  if urgency not in UrgencyLevel:
    raise ValueError
  libnotify.notify_notification_set_urgency(notify_st.notify, urgency)

def init():
  global libnotify_inited, libnotify, gobj
  if libnotify_inited:
    return

  try:
    libnotify = CDLL('libnotify.so')
  except OSError:
    libnotify = CDLL('libnotify.so.4')
  gobj = CDLL('libgobject-2.0.so')

  libnotify.notify_init('pynotify')
  libnotify_inited = True

  libnotify.notify_notification_new.restype = c_void_p
  notify_st.notify = c_void_p(libnotify.notify_notification_new(
    c_void_p(), c_void_p(), c_void_p(),
  ))
  atexit.register(uninit)

def uninit():
  global libnotify_inited
  try:
    if libnotify_inited:
      gobj.g_object_unref(notify_st.notify)
      libnotify.notify_uninit()
      libnotify_inited = False
  except AttributeError:
    # libnotify.so 已被卸载
    pass

if __name__ == '__main__':
  from time import sleep
  notify = __import__('__main__')
  notify.set('This is a test', '测试一下。')
  notify.show()
  sleep(1)
  notify.update(body='再测试一下。')
