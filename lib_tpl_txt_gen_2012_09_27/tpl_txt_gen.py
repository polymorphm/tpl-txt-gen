# -*- mode: python; coding: utf-8 -*-
#
# Copyright 2012, 2013 Andrej A Antonov <polymorphm@gmail.com>.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

assert str is not bytes

import os, os.path, weakref, importlib
from mako import lookup as mako_lookup
from . import get_items

class TplTxtGenEnviron(object):
    pass

class ItemFunc(object):
    def __init__(self, get_iter):
        self._get_iter = get_iter
        self._group_map = {}
    
    def __call__(self, path, group=None):
        if group is None:
            return next(self._get_iter(path))
        
        try:
            text = self._group_map[group]
        except KeyError:
            self._group_map[group] = text = next(self._get_iter(path))
        
        return text

class ItemFuncFactory(object):
    def __init__(self, environ_ref):
        self._environ_ref = environ_ref
        self._iter_map = {}
    
    def __call__(self):
        return ItemFunc(self._get_iter)
    
    def _resolve_path(self, path):
        root_dir = self._environ_ref().root_dir
        return os.path.join(root_dir, path)
    
    def _get_iter(self, path):
        try:
            it = self._iter_map[path]
        except KeyError:
            self._iter_map[path] = it = \
                    get_items.get_random_infinite_items(self._resolve_path(path))
        
        return it

class CustomFunc(object):
    def __init__(self, get_impl):
        self._get_impl = get_impl
        self._impl_map = {}
       
    def __call__(self, custom_name):
        try:
            impl = self._impl_map[custom_name]
        except KeyError:
            self._impl_map[custom_name] = impl = self._get_impl(custom_name)()
        
        return impl

class CustomFuncFactory(object):
    def __init__(self, environ_ref):
        self._environ_ref = environ_ref
        self._impl_map = {}
    
    def __call__(self):
        return CustomFunc(self._get_impl)
    
    def _get_impl(self, custom_name):
        try:
            impl = self._impl_map[custom_name]
        except KeyError:
            func_name, module_name = custom_name.rsplit(':', 1)
            mod = importlib.import_module(module_name)
            factory = mod.FUNC_FACTORY_MAP[func_name]
            self._impl_map[custom_name] = impl = factory(self._environ_ref)
        
        return impl

FUNC_FACTORY_MAP = {
    'item': ItemFuncFactory,
    'custom': CustomFuncFactory,
}

DEFAULT_FUNC_FACTORY_MAP = FUNC_FACTORY_MAP

def count_iter(count):
    if count is not None:
        for i in range(count):
            # TODO: for Python-3.3+ -- need fix to PEP-0380
            yield i
    else:
        while True:
            yield

def tpl_txt_gen_iter(tpl_path, count=None,
            environ=None, func_factory_map=None):
    if environ is None:
        environ = TplTxtGenEnviron()
    
    environ.tpl_path = tpl_path
    environ.count = count
    
    environ.root_dir = os.path.dirname(environ.tpl_path)
    environ.tpl_name = os.path.basename(environ.tpl_path)
    environ.tpl_lookup = mako_lookup.TemplateLookup(directories=(environ.root_dir, ))
    environ.tpl = environ.tpl_lookup.get_template(environ.tpl_name)
    
    if func_factory_map is None:
        func_factory_map = DEFAULT_FUNC_FACTORY_MAP
    
    func_factories = {
        func_name:
                func_factory_map[func_name](weakref.ref(environ))
                        for func_name in func_factory_map
    }
    
    for i in count_iter(environ.count):
        tpl_kwargs = {
            func_name:
                    func_factories[func_name]()
                            for func_name in func_factories
        }
        
        yield environ.tpl.render(**tpl_kwargs)

def tpl_txt_gen(tpl_path, out_path, count):
    out_path_created = False
    
    for i, text in enumerate(tpl_txt_gen_iter(tpl_path, count=count)):
        if not out_path_created:
            os.mkdir(out_path)
            out_path_created = True
        
        out_name = 'out-{}.txt'.format(i)
        full_out_path = os.path.join(out_path, out_name)
        
        with open(full_out_path, 'w', encoding='utf-8', newline='\n') as fd:
            fd.write(text)
