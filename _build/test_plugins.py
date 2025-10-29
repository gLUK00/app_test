#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Tests pour le système de plugins."""
import unittest
from plugins.plugin_manager import PluginManager
from plugins.actions.action_base import ActionBase
from plugins.reports.report_base import ReportBase
from plugins.auth.auth_base import AuthBase
from plugins import plugin_registry


class TestPluginManager(unittest.TestCase):
    """Tests pour le gestionnaire de plugins."""
    
    def test_plugin_manager_creation(self):
        """Test de création d'un gestionnaire de plugins."""
        manager = PluginManager('actions', ActionBase)
        self.assertIsNotNone(manager)
        self.assertEqual(manager.plugin_type, 'actions')
        self.assertEqual(manager.base_class, ActionBase)
    
    def test_discover_plugins(self):
        """Test de découverte des plugins."""
        manager = PluginManager('actions', ActionBase)
        plugins = manager.discover_plugins()
        
        self.assertIsInstance(plugins, dict)
        self.assertGreater(len(plugins), 0)
        
        # Vérifier que les plugins standards sont chargés
        self.assertIn('http', plugins)
        self.assertIn('ssh', plugins)
    
    def test_get_plugin(self):
        """Test de récupération d'un plugin."""
        manager = PluginManager('actions', ActionBase)
        manager.discover_plugins()
        
        http_action = manager.get_plugin('http')
        self.assertIsNotNone(http_action)
        self.assertIsInstance(http_action, ActionBase)
    
    def test_get_plugin_info(self):
        """Test de récupération des informations d'un plugin."""
        manager = PluginManager('actions', ActionBase)
        manager.discover_plugins()
        
        info = manager.get_plugin_info('http')
        self.assertIsNotNone(info)
        self.assertIn('name', info)
        self.assertIn('class', info)
    
    def test_list_plugins(self):
        """Test de listage des plugins."""
        manager = PluginManager('actions', ActionBase)
        manager.discover_plugins()
        
        plugins = manager.list_plugins()
        self.assertIsInstance(plugins, list)
        self.assertGreater(len(plugins), 0)


class TestActionPlugins(unittest.TestCase):
    """Tests pour les plugins d'actions."""
    
    def setUp(self):
        """Initialisation avant chaque test."""
        from plugins.actions import action_manager
        self.manager = action_manager
    
    def test_http_action_metadata(self):
        """Test des métadonnées de l'action HTTP."""
        http_action = self.manager.get_plugin('http')
        metadata = http_action.get_metadata()
        
        self.assertEqual(metadata['name'], 'http')
        self.assertIn('version', metadata)
        self.assertIn('author', metadata)
    
    def test_http_action_input_mask(self):
        """Test du masque de saisie de l'action HTTP."""
        http_action = self.manager.get_plugin('http')
        mask = http_action.get_input_mask()
        
        self.assertIsInstance(mask, list)
        self.assertGreater(len(mask), 0)
        
        # Vérifier que les champs essentiels sont présents
        field_names = [field['name'] for field in mask]
        self.assertIn('method', field_names)
        self.assertIn('url', field_names)
    
    def test_http_action_validation(self):
        """Test de la validation de configuration de l'action HTTP."""
        http_action = self.manager.get_plugin('http')
        
        # Configuration valide
        valid_config = {
            'method': 'GET',
            'url': 'https://example.com'
        }
        is_valid, message = http_action.validate_config(valid_config)
        self.assertTrue(is_valid)
        
        # Configuration invalide (pas d'URL)
        invalid_config = {
            'method': 'GET'
        }
        is_valid, message = http_action.validate_config(invalid_config)
        self.assertFalse(is_valid)
    
    def test_ssh_action_metadata(self):
        """Test des métadonnées de l'action SSH."""
        ssh_action = self.manager.get_plugin('ssh')
        metadata = ssh_action.get_metadata()
        
        self.assertEqual(metadata['name'], 'ssh')
        self.assertIn('version', metadata)


class TestReportPlugins(unittest.TestCase):
    """Tests pour les plugins de rapports."""
    
    def setUp(self):
        """Initialisation avant chaque test."""
        from plugins.reports import report_manager
        self.manager = report_manager
    
    def test_html_report_exists(self):
        """Test de l'existence du plugin de rapport HTML."""
        plugins = self.manager.get_all_plugins()
        self.assertIn('html', plugins)
    
    def test_html_report_metadata(self):
        """Test des métadonnées du rapport HTML."""
        html_report = self.manager.get_plugin('html')
        if html_report:
            metadata = html_report.get_metadata()
            
            self.assertEqual(metadata['name'], 'html')
            self.assertEqual(metadata['output_format'], 'html')
    
    def test_html_report_generation(self):
        """Test de génération d'un rapport HTML."""
        html_report = self.manager.get_plugin('html')
        if html_report:
            test_results = {
                'tests': [
                    {
                        'name': 'Test 1',
                        'status': 'passed',
                        'logs': 'Test réussi'
                    },
                    {
                        'name': 'Test 2',
                        'status': 'failed',
                        'logs': 'Test échoué'
                    }
                ]
            }
            
            result = html_report.generate(test_results)
            
            self.assertTrue(result['success'])
            self.assertIsNotNone(result['data'])
            self.assertIn('<!DOCTYPE html>', result['data'])


class TestAuthPlugins(unittest.TestCase):
    """Tests pour les plugins d'authentification."""
    
    def setUp(self):
        """Initialisation avant chaque test."""
        from plugins.auth import auth_manager
        self.manager = auth_manager
    
    def test_local_auth_exists(self):
        """Test de l'existence du plugin d'authentification locale."""
        plugins = self.manager.get_all_plugins()
        self.assertIn('local', plugins)
    
    def test_local_auth_metadata(self):
        """Test des métadonnées de l'authentification locale."""
        local_auth = self.manager.get_plugin('local')
        if local_auth:
            metadata = local_auth.get_metadata()
            
            self.assertEqual(metadata['name'], 'local')
            self.assertEqual(metadata['auth_type'], 'local')


class TestPluginRegistry(unittest.TestCase):
    """Tests pour le registre central de plugins."""
    
    def test_get_all_plugins(self):
        """Test de récupération de tous les plugins."""
        all_plugins = plugin_registry.get_all_plugins()
        
        self.assertIn('actions', all_plugins)
        self.assertIn('reports', all_plugins)
        self.assertIn('auth', all_plugins)
    
    def test_get_manager(self):
        """Test de récupération d'un gestionnaire."""
        action_manager = plugin_registry.get_manager('actions')
        self.assertIsNotNone(action_manager)
        self.assertIsInstance(action_manager, PluginManager)
    
    def test_get_plugin_count(self):
        """Test du comptage des plugins."""
        counts = plugin_registry.get_plugin_count()
        
        self.assertIn('actions', counts)
        self.assertIn('reports', counts)
        self.assertIn('auth', counts)
        
        self.assertGreater(counts['actions'], 0)


if __name__ == '__main__':
    unittest.main()
