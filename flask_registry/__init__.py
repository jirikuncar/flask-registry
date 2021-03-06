# -*- coding: utf-8 -*-
##
## This file is part of Flask-Registry
## Copyright (C) 2013 CERN.
##
## Flask-Registry is free software; you can redistribute it and/or
## modify it under the terms of the GNU General Public License as
## published by the Free Software Foundation; either version 2 of the
## License, or (at your option) any later version.
##
## Flask-Registry is distributed in the hope that it will be useful, but
## WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
## General Public License for more details.
##
## You should have received a copy of the GNU General Public License
## along with Flask-Registry; if not, write to the Free Software Foundation,
## Inc., 59 Temple Place, Suite 330, Boston, MA 02111-1307, USA.
##
## In applying this licence, CERN does not waive the privileges and immunities
## granted to it by virtue of its status as an Intergovernmental Organization
## or submit itself to any jurisdiction.

"""
Flask-Registry extension
"""

from werkzeug.local import LocalProxy
from flask import current_app


class RegistryError(Exception):
    """ """
    pass


class Registry(object):
    """
    Flask-Registry
    """
    def __init__(self, app=None):
        self._registry = dict()
        self.app = app
        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        if not hasattr(app, 'extensions'):
            app.extensions = {}
        if 'registry' in app.extensions:
            raise RegistryError("Flask application already initialized")
        app.extensions['registry'] = self

    def __iter__(self):
        return self._registry.__iter__()

    def __len__(self):
        return self._registry.__len__()

    def __contains__(self, item):
        return self._registry.__contains__(item)

    def __getitem__(self, key):
        return self._registry[key]

    def __setitem__(self, key, value):
        if key in self._registry:
            raise RegistryError("Namespace %s already taken." % key)
        self._registry[key] = value
        self._registry[key]._namespace = key

    def items(self):
        return self._registry.items()


class RegistryBase(object):
    """
    Base class for all registries
    """
    @property
    def namespace(self):
        return self._namespace

    def register(self, *args, **kwargs):
        raise NotImplementedError()

    def unregister(self, *args, **kwargs):
        raise NotImplementedError()


class RegistryProxy(LocalProxy):
    """
    Proxy object to a registry in the current app. Allows you to define your
    registry in your module without needing to initialize it first (since you
    need the Flaks application).
    """
    def __init__(self, namespace, registry_class, *args, **kwargs):
        def _lookup():
            if not 'registry' in getattr(current_app, 'extensions', {}):
                raise RegistryError('Registry is not initialized.')
            if namespace not in current_app.extensions['registry']:
                current_app.extensions['registry'][namespace] = registry_class(
                    *args, **kwargs
                )
            return current_app.extensions['registry'][namespace]
        super(RegistryProxy, self).__init__(_lookup)


#
# API of registries
#
from flask_registry.registries.core import ListRegistry, DictRegistry, \
    ImportPathRegistry, ModuleRegistry
from flask_registry.registries.modulediscovery import \
    ModuleDiscoveryRegistry, ModuleAutoDiscoveryRegistry
from flask_registry.registries.pkgresources import EntryPointRegistry, \
    PkgResourcesDiscoveryRegistry
from flask_registry.registries.appdiscovery import PackageRegistry, \
    ExtensionRegistry, ConfigurationRegistry
