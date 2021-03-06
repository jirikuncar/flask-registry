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

from unittest import TestCase
from flask import Flask

from flask.ext.registry import Registry, RegistryError, RegistryBase, \
    RegistryProxy


class FlaskTestCase(TestCase):
    """
    Mix-in class for creating the Flask application
    """

    def setUp(self):
        app = Flask(__name__)
        app.config['DEBUG'] = True
        app.config['TESTING'] = True
        app.logger.disabled = True
        self.app = app


class TestRegistry(FlaskTestCase):
    """
    Tests for the main registry class
    """
    def test_creation(self):
        assert 'registry' not in self.app.extensions
        Registry(app=self.app)
        assert isinstance(self.app.extensions['registry'], Registry)

    def test_creation_old_flask(self):
        # Simulate old Flask
        del self.app.extensions
        Registry(app=self.app)
        assert isinstance(self.app.extensions['registry'], Registry)

    def test_creation_init(self):
        assert 'registry' not in self.app.extensions
        r = Registry()
        r.init_app(app=self.app)
        assert isinstance(self.app.extensions['registry'], Registry)

    def test_double_creation(self):
        Registry(app=self.app)
        self.assertRaises(RegistryError, Registry, app=self.app)

    def test_registration_iter(self):
        Registry(app=self.app)
        self.app.extensions['registry']['mynamespace'] = RegistryBase()
        self.app.extensions['registry']['myothernamespace'] = RegistryBase()

        assert len(self.app.extensions['registry']) == 2
        assert 'mynamespace' in self.app.extensions['registry']
        assert 'myothernamespace' in self.app.extensions['registry']

        # Double registration
        try:
            self.app.extensions['registry']['mynamespace'] = RegistryBase()
            raise AssertionError("No exception raise for double registration")
        except RegistryError:
            pass

        # Registered object
        assert isinstance(
            self.app.extensions['registry']['mynamespace'],
            RegistryBase
        )
        assert isinstance(
            self.app.extensions['registry']['myothernamespace'],
            RegistryBase
        )

        # Iteration
        assert set(self.app.extensions['registry']) == \
            set(['myothernamespace', 'mynamespace', ])

        for ns, r in self.app.extensions['registry'].items():
            assert ns in ['mynamespace', 'myothernamespace']

    def test_namespace_injection(self):
        Registry(app=self.app)
        self.app.extensions['registry']['mynamespace'] = RegistryBase()
        assert self.app.extensions['registry']['mynamespace'].namespace == \
            'mynamespace'

    def test_registry_base(self):
        Registry(app=self.app)
        self.app.extensions['registry']['myns'] = RegistryBase()
        self.assertRaises(
            NotImplementedError,
            self.app.extensions['registry']['myns'].register
        )
        self.assertRaises(
            NotImplementedError,
            self.app.extensions['registry']['myns'].unregister
        )


class TestRegistryProxy(FlaskTestCase):
    def test_proxy(self):
        Registry(app=self.app)
        proxy = RegistryProxy('prxns', RegistryBase)

        assert 'prxns' not in self.app.extensions['registry']

        with self.app.app_context():
            self.assertRaises(
                NotImplementedError,
                proxy.register
            )
            assert 'prxns' in self.app.extensions['registry']
            assert isinstance(
                self.app.extensions['registry']['prxns'],
                RegistryBase
            )

    def test_proxy_noregistry(self):
        proxy = RegistryProxy('prxns', RegistryBase)
        with self.app.app_context():
            try:
                proxy.register()
                raise AssertionError("Registry is supposed not to be avialable")
            except RegistryError:
                pass
