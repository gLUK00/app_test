#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Script d'automatisation pour créer une campagne couvrant toutes les actions disponibles."""

import argparse
import contextlib
import getpass
import io
import json
import sys
import tempfile
import textwrap
import threading
import time
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

import paramiko
import requests
import socketio
import yaml
from ftplib import FTP

# Ajouter le répertoire racine au PYTHONPATH pour accéder aux modules du projet
REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from utils.db import load_config  # type: ignore  # pylint: disable=import-error
from utils.webdav_utils import WebDAVClient  # type: ignore  # pylint: disable=import-error
from utils.workdir import get_campain_workdir  # type: ignore  # pylint: disable=import-error


class Colors:
    """Codes couleurs ANSI pour un affichage lisible."""

    HEADER = "\033[95m"
    BLUE = "\033[94m"
    CYAN = "\033[96m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    RED = "\033[91m"
    BOLD = "\033[1m"
    END = "\033[0m"


@dataclass
class TestBlueprint:
    """Représente un test à créer via l'API."""

    action_type: str
    variant: str
    name: str
    description: str
    value: Dict[str, Any]
    variables: List[str] = field(default_factory=list)


def prompt_with_default(message: str, default: str) -> str:
    """Demande une saisie utilisateur avec valeur par défaut."""

    entry = input(f"{message} [{default}]: ").strip()
    return entry or default


def prompt_yes_no(message: str, default_yes: bool = True) -> bool:
    """Demande une confirmation Oui/Non avec valeur par défaut."""

    default_txt = "O/n" if default_yes else "o/N"
    while True:
        entry = input(f"{message} ({default_txt}): ").strip().lower()
        if not entry:
            return default_yes
        if entry in {"o", "oui", "y", "yes"}:
            return True
        if entry in {"n", "non", "no"}:
            return False
        print(f"{Colors.YELLOW}Veuillez répondre par o/oui ou n/non.{Colors.END}")


class ApiError(RuntimeError):
    """Exception personnalisée pour les erreurs d'API."""


class ApiClient:
    """Client REST simplifié pour l'API TestGyver."""

    def __init__(self, base_url: str, verbose: bool = False) -> None:
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
        self.token: Optional[str] = None
        self.user: Optional[Dict[str, Any]] = None
        self.verbose = verbose

    def _url(self, path: str) -> str:
        if path.startswith('http://') or path.startswith('https://'):
            return path
        return f"{self.base_url}{path}"

    def login(self, email: str, password: str) -> Dict[str, Any]:
        response = self.session.post(self._url('/api/login'), json={'email': email, 'password': password})
        if response.status_code != 200:
            raise ApiError(f"Authentification échouée ({response.status_code}): {response.text}")
        data = response.json()
        self.token = data.get('token')
        self.user = data.get('user')
        if not self.token:
            raise ApiError('Token JWT absent de la réponse.')
        self.session.headers.update({'Authorization': f"Bearer {self.token}"})
        return data

    def get(self, path: str, **kwargs: Any) -> Any:
        response = self.session.get(self._url(path), **kwargs)
        self._raise_if_needed(response)
        return response.json()

    def post(self, path: str, **kwargs: Any) -> Any:
        response = self.session.post(self._url(path), **kwargs)
        self._raise_if_needed(response)
        if response.text:
            try:
                return response.json()
            except ValueError:
                return response.text
        return {}

    def delete(self, path: str, **kwargs: Any) -> Any:
        response = self.session.delete(self._url(path), **kwargs)
        self._raise_if_needed(response)
        if response.text:
            try:
                return response.json()
            except ValueError:
                return response.text
        return {}

    def get_all_pages(self, path: str, params: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        params = params.copy() if params else {}
        params.setdefault('page', 1)
        params.setdefault('page_size', 500)
        items: List[Dict[str, Any]] = []
        while True:
            payload = self.get(path, params=params)

            if isinstance(payload, list):
                items.extend(payload)
                break

            if isinstance(payload, dict):
                chunk = payload.get('items')
                if chunk is None:
                    chunk = payload.get('data', [])
                items.extend(chunk or [])

                pagination = payload.get('pagination') or {}
                has_next = pagination.get('has_next')
                current_page = pagination.get('current_page', params['page'])

                if has_next:
                    params['page'] = current_page + 1
                    continue

                total = pagination.get('total_items', payload.get('total', len(items)))
                if len(items) >= total:
                    break
                params['page'] = current_page + 1
            else:
                break
        return items

    def _raise_if_needed(self, response: requests.Response) -> None:
        if self.verbose:
            print(f"[API] {response.request.method} {response.url} -> {response.status_code}")
        if response.status_code >= 400:
            try:
                message = response.json().get('message', response.text)
            except ValueError:
                message = response.text
            raise ApiError(f"Erreur API ({response.status_code}): {message}")


class FullActionCampainCreator:
    """Met en place la campagne complète couvrant toutes les actions."""

    def __init__(self, args: argparse.Namespace) -> None:
        self.args = args
        self.repo_root = REPO_ROOT
        self.config = load_config()
        host = '127.0.0.1' if self.config['app']['host'] in {'0.0.0.0', '::'} else self.config['app']['host']
        default_base_url = f"http://{host}:{self.config['app']['port']}"
        self.base_url = args.api_url.rstrip('/') if args.api_url else default_base_url
        self.api = ApiClient(self.base_url, verbose=args.verbose)
        self.slug = datetime.utcnow().strftime('fullcamp_%Y%m%d_%H%M%S')
        self.compose_data = self._load_compose_file()
        self.env_info = self._build_env_info()
        self.available_actions: List[str] = []
        self.blueprints: List[TestBlueprint] = []
        self.remote_assets: Dict[str, Dict[str, str]] = {}
        self.summary_rows: List[Dict[str, Any]] = []
        self.created_tests: List[Dict[str, Any]] = []
        self.campain_id: Optional[str] = None
        self.campain_name: Optional[str] = None
        self.environment: Optional[str] = None
        self.mac_logo_name = 'mac_logo_test.png'
        self.sample_text = f"Contenu généré automatiquement ({self.slug})"
        self.var_samples = self._build_variable_samples()
        self.campain_workdir: Optional[Path] = None
        self.should_run: Optional[bool] = None
        self.should_cleanup: Optional[bool] = None
        self.rapport_id: Optional[str] = None
        self.run_result: Optional[str] = None

    # ------------------------------------------------------------------
    # Chargement configuration docker
    # ------------------------------------------------------------------
    def _load_compose_file(self) -> Dict[str, Any]:
        compose_path = self.repo_root / 'init' / 'test-docker-compose.yml'
        if not compose_path.exists():
            raise FileNotFoundError(f"Fichier {compose_path} introuvable.")
        with compose_path.open('r', encoding='utf-8') as handle:
            return yaml.safe_load(handle)

    def _parse_env_list(self, env_list: Optional[List[Any]]) -> Dict[str, str]:
        env_dict: Dict[str, str] = {}
        if not env_list:
            return env_dict
        for item in env_list:
            if isinstance(item, str) and '=' in item:
                key, value = item.split('=', 1)
                env_dict[key] = value
            elif isinstance(item, dict):
                env_dict.update({str(k): str(v) for k, v in item.items()})
        return env_dict

    def _extract_port(self, service: Dict[str, Any], container_port: int) -> int:
        for entry in service.get('ports', []):
            if not isinstance(entry, str) or ':' not in entry:
                continue
            host_part, container_part = entry.split(':', 1)
            container_part = container_part.split('/')[0]
            if '-' in container_part:
                continue
            if int(container_part) == container_port:
                host_segment = host_part.split('/')[0]
                if '-' in host_segment:
                    continue
                return int(host_segment)
        return container_port

    def _build_env_info(self) -> Dict[str, Dict[str, Any]]:
        services = self.compose_data.get('services', {})
        info: Dict[str, Dict[str, Any]] = {}

        ftp_service = services.get('ftp-server')
        if ftp_service:
            env = self._parse_env_list(ftp_service.get('environment'))
            info['ftp'] = {
                'host': '127.0.0.1',
                'port': self._extract_port(ftp_service, 21),
                'user': env.get('FTP_USER_NAME', 'testuser'),
                'password': env.get('FTP_USER_PASS', 'testpass')
            }

        sftp_service = services.get('sftp-server')
        if sftp_service:
            command = sftp_service.get('command', '')
            parts = command.split(':')
            info['sftp'] = {
                'host': '127.0.0.1',
                'port': self._extract_port(sftp_service, 22),
                'user': parts[0] if parts else 'testuser',
                'password': parts[1] if len(parts) > 1 else 'testpass',
                'home': f"/{parts[4]}" if len(parts) > 4 and parts[4] else '/upload'
            }

        webdav_service = services.get('webdav-server')
        if webdav_service:
            env = self._parse_env_list(webdav_service.get('environment'))
            info['webdav'] = {
                'base_url': f"http://127.0.0.1:{self._extract_port(webdav_service, 80)}",
                'user': env.get('USERNAME', 'testuser'),
                'password': env.get('PASSWORD', 'testpass')
            }

        http_service = services.get('http-api')
        if http_service:
            info['http'] = {
                'base_url': f"http://127.0.0.1:{self._extract_port(http_service, 80)}"
            }

        ssh_service = services.get('ssh-server')
        if ssh_service:
            env = self._parse_env_list(ssh_service.get('environment'))
            info['ssh'] = {
                'host': '127.0.0.1',
                'port': self._extract_port(ssh_service, 2222),
                'user': env.get('USER_NAME', 'testuser'),
                'password': env.get('USER_PASSWORD', 'testpass')
            }

        return info

    # ------------------------------------------------------------------
    # Variables multi-environnements
    # ------------------------------------------------------------------
    def _build_variable_samples(self) -> Dict[str, str]:
        return {
            'HTTP_SAMPLE_BODY': json.dumps({'message': f'ping {self.slug}'}),
            'FTP_SAMPLE_TEXT': f"FTP payload {self.slug}",
            'SFTP_SAMPLE_TEXT': f"SFTP payload {self.slug}",
            'IO_SAMPLE_TEXT': f"Fichier de travail généré {self.slug}",
            'VAR_SAMPLE_INT': '200',
            'VAR_SAMPLE_FLOAT': '42.5',
            'VAR_SAMPLE_BOOL': 'true',
            'VAR_SAMPLE_LIST': json.dumps(['admin', 'user', 'editor']),
            'VAR_SAMPLE_DICT': json.dumps({'id': 123, 'name': 'John Doe', 'active': True}),
            'VAR_SAMPLE_JSON': json.dumps({'status': 'ok', 'balance': '199.99'})
        }

    def _variable_blueprints(self) -> List[Dict[str, Any]]:
        definitions = [
            {'key': 'HTTP_BASE_URL', 'description': 'Endpoint HTTP bin local', 'value': self.env_info.get('http', {}).get('base_url', 'http://127.0.0.1:8082')},
            {'key': 'HTTP_SAMPLE_BODY', 'description': 'Payload JSON de test', 'value': self.var_samples['HTTP_SAMPLE_BODY']},
            {'key': 'FTP_HOST', 'description': 'Serveur FTP de test', 'value': self.env_info.get('ftp', {}).get('host', '127.0.0.1')},
            {'key': 'FTP_PORT', 'description': 'Port FTP de test', 'value': str(self.env_info.get('ftp', {}).get('port', 21))},
            {'key': 'FTP_USERNAME', 'description': 'Utilisateur FTP', 'value': self.env_info.get('ftp', {}).get('user', 'testuser')},
            {'key': 'FTP_PASSWORD', 'description': 'Mot de passe FTP', 'value': self.env_info.get('ftp', {}).get('password', 'testpass')},
            {'key': 'FTP_SAMPLE_TEXT', 'description': 'Contenu écrit lors des tests FTP', 'value': self.var_samples['FTP_SAMPLE_TEXT']},
            {'key': 'SFTP_HOST', 'description': 'Serveur SFTP', 'value': self.env_info.get('sftp', {}).get('host', '127.0.0.1')},
            {'key': 'SFTP_PORT', 'description': 'Port SFTP', 'value': str(self.env_info.get('sftp', {}).get('port', 22))},
            {'key': 'SFTP_USERNAME', 'description': 'Utilisateur SFTP', 'value': self.env_info.get('sftp', {}).get('user', 'testuser')},
            {'key': 'SFTP_PASSWORD', 'description': 'Mot de passe SFTP', 'value': self.env_info.get('sftp', {}).get('password', 'testpass')},
            {'key': 'SFTP_SAMPLE_TEXT', 'description': 'Contenu écrit lors des tests SFTP', 'value': self.var_samples['SFTP_SAMPLE_TEXT']},
            {'key': 'SSH_HOST', 'description': 'Serveur SSH de test', 'value': self.env_info.get('ssh', {}).get('host', '127.0.0.1')},
            {'key': 'SSH_PORT', 'description': 'Port SSH', 'value': str(self.env_info.get('ssh', {}).get('port', 2223))},
            {'key': 'SSH_USERNAME', 'description': 'Utilisateur SSH', 'value': self.env_info.get('ssh', {}).get('user', 'testuser')},
            {'key': 'SSH_PASSWORD', 'description': 'Mot de passe SSH', 'value': self.env_info.get('ssh', {}).get('password', 'testpass')},
            {'key': 'SSH_COMMAND', 'description': 'Commande exécutée lors du test SSH', 'value': 'ls -1 /'},
            {'key': 'WEBDAV_URL', 'description': 'Endpoint WebDAV de test', 'value': self.env_info.get('webdav', {}).get('base_url', 'http://127.0.0.1:8080')},
            {'key': 'WEBDAV_USERNAME', 'description': 'Utilisateur WebDAV', 'value': self.env_info.get('webdav', {}).get('user', 'testuser')},
            {'key': 'WEBDAV_PASSWORD', 'description': 'Mot de passe WebDAV', 'value': self.env_info.get('webdav', {}).get('password', 'testpass')},
            {'key': 'IO_SAMPLE_TEXT', 'description': 'Contenu des fichiers locaux', 'value': self.var_samples['IO_SAMPLE_TEXT']},
            {'key': 'VAR_SAMPLE_INT', 'description': 'Valeur string convertie en int', 'value': self.var_samples['VAR_SAMPLE_INT']},
            {'key': 'VAR_SAMPLE_FLOAT', 'description': 'Valeur string convertie en float', 'value': self.var_samples['VAR_SAMPLE_FLOAT']},
            {'key': 'VAR_SAMPLE_BOOL', 'description': 'Valeur string convertie en bool', 'value': self.var_samples['VAR_SAMPLE_BOOL']},
            {'key': 'VAR_SAMPLE_LIST', 'description': 'Liste JSON de test', 'value': self.var_samples['VAR_SAMPLE_LIST']},
            {'key': 'VAR_SAMPLE_DICT', 'description': 'Objet JSON pour conversion dict', 'value': self.var_samples['VAR_SAMPLE_DICT']},
            {'key': 'VAR_SAMPLE_JSON', 'description': 'Objet JSON complet', 'value': self.var_samples['VAR_SAMPLE_JSON']}
        ]
        return definitions

    def _fetch_existing_variables(self) -> Dict[str, Dict[str, Any]]:
        vars_map: Dict[str, Dict[str, Any]] = {}
        for variable in self.api.get_all_pages('/api/variables'):
            key = variable.get('key')
            filiere = variable.get('filiere') or ''
            vars_map[f"{key}|{filiere}"] = variable
        return vars_map

    def _ensure_variables(self, filiere: str) -> None:
        print(f"{Colors.BLUE}Initialisation des variables pour l'environnement '{filiere}'...{Colors.END}")
        existing = self._fetch_existing_variables()
        for definition in self._variable_blueprints():
            key = definition['key']
            description = definition['description']
            value = str(definition['value'])
            root_key = f"{key}|"
            if root_key not in existing:
                payload = {'key': key, 'isRoot': True, 'description': description}
                self.api.post('/api/variables', json=payload)
                existing[root_key] = payload | {'key': key, 'description': description, 'isRoot': True}
                print(f"  ✓ Variable racine {key}")
            else:
                print(f"  • Variable racine {key} déjà présente (description conservée)")

            env_key = f"{key}|{filiere}"
            if env_key not in existing:
                payload = {
                    'key': key,
                    'value': value,
                    'filiere': filiere,
                    'description': f"Valeur auto ({self.slug})",
                    'isRoot': False
                }
                self.api.post('/api/variables', json=payload)
                existing[env_key] = payload
                print(f"  ✓ Variable {key} ({filiere})")
            else:
                existing_value = str(existing[env_key].get('value', ''))
                if existing_value != value:
                    print(
                        f"{Colors.RED}  ! Valeur existante différente pour {key} ({filiere}) : "
                        f"{existing_value} != {value}{Colors.END}"
                    )
                else:
                    print(f"  • Variable {key} ({filiere}) déjà présente (valeur identique)")
        print(f"{Colors.GREEN}Variables prêtes.{Colors.END}")

    # ------------------------------------------------------------------
    # Gestion campagne/tests
    # ------------------------------------------------------------------
    def _load_available_actions(self) -> None:
        masks = self.api.get('/api/actions/masks')
        self.available_actions = sorted(masks.keys())

    def _ensure_campaign_name(self, base_name: str) -> str:
        existing_names = {c['name'] for c in self.api.get_all_pages('/api/campains')}
        candidate = base_name
        index = 1
        while candidate in existing_names:
            candidate = f"{base_name} ({index})"
            index += 1
        return candidate

    def _create_campain(self, name: str) -> str:
        description = f"Campagne générée automatiquement le {datetime.now():%d/%m/%Y %H:%M}"
        response = self.api.post('/api/campains', json={'name': name, 'description': description})
        campain_id = response.get('campain_id')
        if not campain_id:
            raise ApiError('ID de campagne non retourné par l\'API')
        self.campain_id = campain_id
        self.campain_name = name
        self.campain_workdir = Path(get_campain_workdir(campain_id))
        print(f"{Colors.GREEN}Campagne '{name}' créée (ID: {campain_id}).{Colors.END}")
        return campain_id

    def _upload_mac_logo(self) -> None:
        logo_path = self.repo_root / 'static' / 'images' / 'mac_logo.png'
        if not logo_path.exists():
            print(f"{Colors.YELLOW}mac_logo.png introuvable, saut de l'upload.{Colors.END}")
            return
        files = {'file': (self.mac_logo_name, logo_path.open('rb'), 'image/png')}
        data = {'customName': self.mac_logo_name}
        self.api.session.post(
            self.api._url(f"/api/campains/{self.campain_id}/files"),  # pylint: disable=protected-access
            files=files,
            data=data,
        ).raise_for_status()
        print(f"{Colors.GREEN}Fichier {self.mac_logo_name} uploadé dans le workdir.{Colors.END}")

    # ------------------------------------------------------------------
    # Préparation des services externes (FTP/SFTP/WebDAV)
    # ------------------------------------------------------------------
    def _prepare_external_services(self) -> None:
        self.remote_assets = {}
        if 'ftp' in self.available_actions:
            self._prepare_ftp_assets()
        if 'sftp' in self.available_actions:
            self._prepare_sftp_assets()
        if 'webdav' in self.available_actions:
            self._prepare_webdav_assets()

    def _prepare_ftp_assets(self) -> None:
        info = self.env_info.get('ftp')
        if not info:
            raise RuntimeError('Configuration FTP introuvable dans test-docker-compose.yml')
        assets: Dict[str, str] = {}
        base_dir = f"campaign_{self.slug}"
        try:
            with FTP() as ftp:
                ftp.connect(info['host'], info['port'], timeout=15)
                ftp.login(info['user'], info['password'])
                self._ftp_ensure_directory(ftp, base_dir)
                assets['base_dir'] = base_dir
                assets['get_path'] = f"{base_dir}/read_{self.slug}.txt"
                assets['delete_path'] = f"{base_dir}/{self.slug}.txt"
                assets['list_dir'] = f"{base_dir}/listing"
                self._ftp_upload_text(ftp, assets['get_path'], self.sample_text)
                self._ftp_upload_text(ftp, assets['delete_path'], "Temp file to delete")
                self._ftp_ensure_directory(ftp, assets['list_dir'])
                self._ftp_upload_text(ftp, f"{assets['list_dir']}/entry1.txt", 'entry1')
                self._ftp_upload_text(ftp, f"{assets['list_dir']}/entry2.log", 'entry2')
        except Exception as exc:
            raise RuntimeError('Impossible de préparer le serveur FTP. Lancez init/test-docker-compose.') from exc
        self.remote_assets['ftp'] = assets

    def _ftp_ensure_directory(self, ftp: FTP, path: str) -> None:
        original = ftp.pwd()
        parts = [p for p in path.split('/') if p]
        for idx in range(len(parts)):
            sub_path = '/'.join(parts[: idx + 1])
            with contextlib.suppress(Exception):
                ftp.mkd(sub_path)
        ftp.cwd(original)

    def _ftp_upload_text(self, ftp: FTP, path: str, content: str) -> None:
        directory, filename = path.rsplit('/', 1)
        self._ftp_ensure_directory(ftp, directory)
        ftp.storbinary(f"STOR {path}", io.BytesIO(content.encode('utf-8')))

    def _prepare_sftp_assets(self) -> None:
        info = self.env_info.get('sftp')
        if not info:
            raise RuntimeError('Configuration SFTP introuvable dans test-docker-compose.yml')
        assets: Dict[str, str] = {}
        home_dir = info.get('home', '/upload') or '/upload'
        base_dir = str(Path('/') / home_dir.lstrip('/') / self.slug)
        try:
            transport = paramiko.Transport((info['host'], info['port']))
            transport.connect(username=info['user'], password=info['password'])
            sftp = paramiko.SFTPClient.from_transport(transport)
            self._sftp_ensure_directory(sftp, base_dir)
            assets['get_path'] = f"{base_dir}/read_{self.slug}.txt"
            assets['delete_path'] = f"{base_dir}/{self.slug}.txt"
            assets['list_dir'] = f"{base_dir}/listing"
            self._sftp_write_text(sftp, assets['get_path'], self.sample_text)
            self._sftp_write_text(sftp, assets['delete_path'], 'Temp SFTP file')
            self._sftp_ensure_directory(sftp, assets['list_dir'])
            self._sftp_write_text(sftp, f"{assets['list_dir']}/entry1.txt", 'entry1')
            self._sftp_write_text(sftp, f"{assets['list_dir']}/entry2.log", 'entry2')
        except Exception as exc:
            raise RuntimeError('Impossible de préparer le serveur SFTP. Lancez init/test-docker-compose.') from exc
        finally:
            with contextlib.suppress(Exception):
                sftp.close()  # type: ignore  # pylint: disable=used-before-assignment
            with contextlib.suppress(Exception):
                transport.close()  # type: ignore  # pylint: disable=used-before-assignment
        self.remote_assets['sftp'] = assets

    def _sftp_ensure_directory(self, sftp: paramiko.SFTPClient, path: str) -> None:
        target = Path(path)
        current = ''
        for part in target.parts:
            if part in {'', '/'}:
                current = '/'
                continue
            if current in {'', '/'}:
                current = f"/{part}" if current == '/' else part
            else:
                current = f"{current}/{part}"
            try:
                sftp.stat(current)
            except IOError:
                try:
                    sftp.mkdir(current)
                except IOError:
                    pass

    def _sftp_write_text(self, sftp: paramiko.SFTPClient, path: str, content: str) -> None:
        directory = str(Path(path).parent)
        self._sftp_ensure_directory(sftp, directory)
        with sftp.file(path, 'w') as remote_file:
            remote_file.write(content)

    def _prepare_webdav_assets(self) -> None:
        info = self.env_info.get('webdav')
        if not info:
            raise RuntimeError('Configuration WebDAV introuvable dans test-docker-compose.yml')
        client = WebDAVClient(info['base_url'], info['user'], info['password'])
        base_path = f"/full_campaign_{self.slug}"
        assets: Dict[str, str] = {'base_path': base_path}
        try:
            client.mkdir(base_path)
            assets['check_path'] = f"{base_path}/check.txt"
            assets['info_path'] = f"{base_path}/info.json"
            assets['list_dir'] = f"{base_path}/listing"
            assets['remove_path'] = f"{base_path}/remove_me.txt"
            assets['move_src'] = f"{base_path}/move_source.txt"
            assets['move_dest'] = f"{base_path}/move_dest.txt"
            assets['download_src'] = f"{base_path}/download.bin"
            assets['upload_target'] = f"{base_path}/uploads/mac_logo.png"
            assets['mkdir_target'] = f"{base_path}/nested/new_dir"
            for path, payload in [
                (assets['check_path'], 'ping'),
                (assets['info_path'], json.dumps({'slug': self.slug})),
                (assets['remove_path'], 'temp'),
                (assets['move_src'], 'move me'),
            ]:
                self._webdav_upload_temp_file(client, path, payload)
            client.mkdir(assets['list_dir'])
            self._webdav_upload_temp_file(client, f"{assets['list_dir']}/file1.txt", 'file1')
            self._webdav_upload_temp_file(client, f"{assets['list_dir']}/file2.log", 'file2')
            self._webdav_upload_temp_file(client, assets['download_src'], 'binary-data')
        except Exception as exc:
            raise RuntimeError('Impossible de préparer WebDAV. Lancez init/test-docker-compose.') from exc
        self.remote_assets['webdav'] = assets

    def _webdav_upload_temp_file(self, client: WebDAVClient, remote_path: str, content: str) -> None:
        parent = str(Path(remote_path).parent)
        with contextlib.suppress(Exception):
            client.mkdir(parent)
        with tempfile.NamedTemporaryFile(delete=False) as tmp:
            tmp.write(content.encode('utf-8'))
            tmp_path = Path(tmp.name)
        try:
            client.upload_file(str(tmp_path), remote_path)
        finally:
            with contextlib.suppress(FileNotFoundError):
                tmp_path.unlink()

    # ------------------------------------------------------------------
    # Actifs locaux (workdir campagne)
    # ------------------------------------------------------------------
    def _prepare_local_assets(self) -> None:
        assert self.campain_id and self.campain_workdir
        work_dir = self.campain_workdir / 'work'
        work_dir.mkdir(parents=True, exist_ok=True)
        io_dir = work_dir / f"io_{self.slug}"
        (io_dir / 'list_ready').mkdir(parents=True, exist_ok=True)
        (io_dir / 'delete_dir').mkdir(parents=True, exist_ok=True)
        (io_dir / 'read_ready').mkdir(parents=True, exist_ok=True)
        (io_dir / 'delete_dir' / 'child.txt').write_text('to be deleted', encoding='utf-8')
        (io_dir / 'read_ready' / 'data.txt').write_text('sample to read', encoding='utf-8')
        for idx in range(1, 4):
            (io_dir / 'list_ready' / f'file_{idx}.txt').write_text(f'file_{idx}', encoding='utf-8')
        print(f"{Colors.GREEN}Actifs locaux préparés dans {io_dir}.{Colors.END}")

    # ------------------------------------------------------------------
    # Génération des tests
    # ------------------------------------------------------------------
    def _build_blueprints(self) -> None:
        builders = {
            'http': self._build_http_tests,
            'ftp': self._build_ftp_tests,
            'sftp': self._build_sftp_tests,
            'ssh': self._build_ssh_tests,
            'webdav': self._build_webdav_tests,
            'io': self._build_io_tests,
            'var': self._build_var_tests,
        }
        missing = [action for action in self.available_actions if action not in builders]
        if missing:
            raise RuntimeError(
                "Les actions suivantes n'ont pas de scénarios prédéfinis dans ce script : " + ", ".join(missing)
            )
        for action in self.available_actions:
            self.blueprints.extend(builders[action]())

    def _build_http_tests(self) -> List[TestBlueprint]:
        base_url = self.env_info.get('http', {}).get('base_url', 'http://127.0.0.1:8082')
        tests = [
            TestBlueprint(
                action_type='http',
                variant='GET',
                name='HTTP GET - healthcheck',
                description='Vérifie la réponse GET du service HTTP de test',
                value={
                    'method': 'GET',
                    'url': f"{base_url}/get?campaign={self.slug}",
                    'headers': {'Accept': 'application/json'},
                    'return_status_code': '200',
                    'output_mapping': {'http_status_code': 'http_get_status'}
                },
                variables=['http_get_status']
            ),
            TestBlueprint(
                action_type='http',
                variant='POST',
                name='HTTP POST - echo',
                description='Teste un POST avec payload JSON',
                value={
                    'method': 'POST',
                    'url': f"{base_url}/post",
                    'headers': {'Content-Type': 'application/json'},
                    'body': self.var_samples['HTTP_SAMPLE_BODY'],
                    'return_status_code': '200',
                    'output_mapping': {'http_response_time': 'http_post_time'}
                },
                variables=['http_post_time']
            ),
            TestBlueprint(
                action_type='http',
                variant='PUT',
                name='HTTP PUT - update',
                description='Teste une mise à jour via PUT',
                value={
                    'method': 'PUT',
                    'url': f"{base_url}/put",
                    'headers': {'Content-Type': 'application/json'},
                    'body': json.dumps({'slug': self.slug, 'action': 'put'}),
                    'return_status_code': '200'
                }
            ),
            TestBlueprint(
                action_type='http',
                variant='DELETE',
                name='HTTP DELETE - cleanup',
                description='Teste une suppression via DELETE',
                value={
                    'method': 'DELETE',
                    'url': f"{base_url}/delete",
                    'headers': {'Accept': 'application/json'},
                    'return_status_code': '200'
                }
            )
        ]
        return tests

    def _build_ftp_tests(self) -> List[TestBlueprint]:
        info = self.env_info['ftp']
        assets = self.remote_assets['ftp']
        base_value = {
            'host': '{{FTP_HOST}}',
            'port': int(info['port']),
            'username': '{{FTP_USERNAME}}',
            'password': '{{FTP_PASSWORD}}'
        }
        tests = [
            TestBlueprint(
                action_type='ftp',
                variant='PUT',
                name='FTP PUT - upload fichier de test',
                description='Dépose un fichier texte sur le serveur FTP',
                value={**base_value, 'method': 'PUT', 'remote_path': f"{assets['base_dir']}/upload_{self.slug}.txt", 'content': '{{FTP_SAMPLE_TEXT}}'}
            ),
            TestBlueprint(
                action_type='ftp',
                variant='GET',
                name='FTP GET - récupération de fichier',
                description='Télécharge un fichier existant sur le serveur FTP',
                value={**base_value, 'method': 'GET', 'remote_path': assets['get_path'], 'output_mapping': {'ftp_file_size': 'ftp_get_size'}},
                variables=['ftp_get_size']
            ),
            TestBlueprint(
                action_type='ftp',
                variant='LIST',
                name='FTP LIST - inventaire répertoire',
                description='Liste le contenu d\'un répertoire dédié',
                value={**base_value, 'method': 'LIST', 'remote_path': assets['list_dir']}
            ),
            TestBlueprint(
                action_type='ftp',
                variant='DELETE',
                name='FTP DELETE - suppression fichier',
                description='Supprime un fichier temporaire',
                value={**base_value, 'method': 'DELETE', 'remote_path': assets['delete_path']}
            )
        ]
        return tests

    def _build_sftp_tests(self) -> List[TestBlueprint]:
        info = self.env_info['sftp']
        assets = self.remote_assets['sftp']
        base_value = {
            'host': '{{SFTP_HOST}}',
            'port': int(info['port']),
            'username': '{{SFTP_USERNAME}}',
            'password': '{{SFTP_PASSWORD}}'
        }
        tests = [
            TestBlueprint(
                action_type='sftp',
                variant='PUT',
                name='SFTP PUT - upload fichier de test',
                description='Dépose un fichier texte via SFTP',
                value={**base_value, 'method': 'PUT', 'remote_path': f"{assets['list_dir']}/upload_{self.slug}.txt", 'content': '{{SFTP_SAMPLE_TEXT}}'}
            ),
            TestBlueprint(
                action_type='sftp',
                variant='GET',
                name='SFTP GET - récupération de fichier',
                description='Télécharge un fichier existant via SFTP',
                value={**base_value, 'method': 'GET', 'remote_path': assets['get_path']}
            ),
            TestBlueprint(
                action_type='sftp',
                variant='LIST',
                name='SFTP LIST - inventaire répertoire',
                description='Liste les fichiers du dossier dédié',
                value={**base_value, 'method': 'LIST', 'remote_path': assets['list_dir']}
            ),
            TestBlueprint(
                action_type='sftp',
                variant='DELETE',
                name='SFTP DELETE - suppression fichier',
                description='Supprime un fichier temporaire',
                value={**base_value, 'method': 'DELETE', 'remote_path': assets['delete_path']}
            )
        ]
        return tests

    def _build_ssh_tests(self) -> List[TestBlueprint]:
        return [
            TestBlueprint(
                action_type='ssh',
                variant='COMMAND',
                name='SSH - exécution distante',
                description='Exécute une commande simple via SSH',
                value={
                    'host': '{{SSH_HOST}}',
                    'port': int(self.env_info['ssh']['port']),
                    'username': '{{SSH_USERNAME}}',
                    'password': '{{SSH_PASSWORD}}',
                    'command': '{{SSH_COMMAND}}',
                    'output_mapping': {'ssh_output': 'ssh_last_output'}
                },
                variables=['ssh_last_output']
            )
        ]

    def _build_webdav_tests(self) -> List[TestBlueprint]:
        assets = self.remote_assets['webdav']
        base_value = {
            'url': '{{WEBDAV_URL}}',
            'username': '{{WEBDAV_USERNAME}}',
            'password': '{{WEBDAV_PASSWORD}}'
        }
        return [
            TestBlueprint('webdav', 'CHECK', 'WebDAV CHECK - existence ressource', 'Vérifie la présence du fichier de contrôle', {**base_value, 'action': 'CHECK', 'srcFile': assets['check_path']}),
            TestBlueprint('webdav', 'INFO', 'WebDAV INFO - métadonnées', 'Récupère les métadonnées d\'un fichier', {**base_value, 'action': 'INFO', 'srcFile': assets['info_path']}),
            TestBlueprint('webdav', 'LIST', 'WebDAV LIST - inventaire', 'Liste les éléments d\'un dossier', {**base_value, 'action': 'LIST', 'srcFile': assets['list_dir']}),
            TestBlueprint('webdav', 'MKDIR', 'WebDAV MKDIR - création dossier', 'Crée un sous-dossier imbriqué', {**base_value, 'action': 'MKDIR', 'srcFile': assets['mkdir_target']}),
            TestBlueprint('webdav', 'REMOVE', 'WebDAV REMOVE - suppression ressource', 'Supprime un fichier de test', {**base_value, 'action': 'REMOVE', 'srcFile': assets['remove_path']}),
            TestBlueprint('webdav', 'MOVE', 'WebDAV MOVE - déplacement', 'Déplace un fichier vers un autre dossier', {**base_value, 'action': 'MOVE', 'srcFile': assets['move_src'], 'targFile': assets['move_dest']}),
            TestBlueprint('webdav', 'DOWNLOAD', 'WebDAV DOWNLOAD - copie locale', 'Télécharge un fichier dans le workdir', {**base_value, 'action': 'DOWNLOAD', 'srcFile': assets['download_src'], 'targFile': f"{{{{test.files_dir}}}}/webdav_download_{self.slug}.bin"}),
            TestBlueprint('webdav', 'UPLOAD', 'WebDAV UPLOAD - depuis workdir', 'Upload le logo binaire vers WebDAV', {**base_value, 'action': 'UPLOAD', 'srcFile': f"{{{{test.files_dir}}}}/{self.mac_logo_name}", 'targFile': assets['upload_target']})
        ]

    def _build_io_tests(self) -> List[TestBlueprint]:
        base_path = f"{{{{test.work_dir}}}}/io_{self.slug}"
        return [
            TestBlueprint('io', 'create_dir', 'IO CREATE DIR', 'Crée un dossier dédié dans le workdir', {'operation': 'create_dir', 'path': f"{base_path}/created_dir"}),
            TestBlueprint('io', 'write_variable', 'IO WRITE FILE', 'Écrit un fichier texte dans le workdir', {'operation': 'write_variable', 'path': f"{base_path}/write/sample.txt", 'variable_value': '{{IO_SAMPLE_TEXT}}'}),
            TestBlueprint('io', 'list_files', 'IO LIST FILES', 'Liste les fichiers préparés', {'operation': 'list_files', 'path': f"{base_path}/list_ready", 'file_extension': '.txt'}),
            TestBlueprint('io', 'read_variable', 'IO READ FILE', 'Lit un fichier existant', {'operation': 'read_variable', 'path': f"{base_path}/read_ready/data.txt"}, variables=['io_last_read']),
            TestBlueprint('io', 'delete_file', 'IO DELETE FILE', 'Supprime un fichier préparé', {'operation': 'delete_file', 'path': f"{base_path}/delete_dir/child.txt"}),
            TestBlueprint('io', 'delete_dir', 'IO DELETE DIR', 'Supprime un dossier et son contenu', {'operation': 'delete_dir', 'path': f"{base_path}/delete_dir"})
        ]

    def _build_var_tests(self) -> List[TestBlueprint]:
        def blueprint(variable_name: str, target_type: str, source_variable: str, description: str) -> TestBlueprint:
            return TestBlueprint(
                action_type='var',
                variant=target_type,
                name=f"VarAction - {target_type} ({variable_name})",
                description=description,
                value={
                    'variable_name': variable_name,
                    'target_type': target_type,
                    'variables': {variable_name: f"{{{{{source_variable}}}}}"},
                    'output_mapping': {'converted_value': f'{variable_name}_{target_type}'}
                },
                variables=[variable_name, f'{variable_name}_{target_type}']
            )

        return [
            blueprint('http_status_raw', 'int', 'VAR_SAMPLE_INT', 'Convertit un code HTTP en entier'),
            blueprint('price_raw', 'float', 'VAR_SAMPLE_FLOAT', 'Convertit un prix en float'),
            blueprint('flag_raw', 'bool', 'VAR_SAMPLE_BOOL', 'Convertit un indicateur en booléen'),
            blueprint('tags_raw', 'list', 'VAR_SAMPLE_LIST', 'Transforme un JSON array en liste Python'),
            blueprint('user_raw', 'dict', 'VAR_SAMPLE_DICT', 'Transforme un JSON en dictionnaire'),
            blueprint('payload_raw', 'json', 'VAR_SAMPLE_JSON', 'Formate un dictionnaire en JSON indenté')
        ]

    def _create_tests(self) -> None:
        assert self.campain_id
        self.created_tests = []
        for blueprint in self.blueprints:
            payload = {
                'campain_id': self.campain_id,
                'name': blueprint.name,
                'description': blueprint.description,
                'actions': [{'type': blueprint.action_type, 'value': blueprint.value}],
                'variables': blueprint.variables
            }
            response = self.api.post('/api/tests', json=payload)
            test_id = response.get('test_id')
            self.created_tests.append({
                'id': test_id,
                'name': blueprint.name,
                'action': blueprint.action_type,
                'variant': blueprint.variant,
                'value': blueprint.value
            })
            print(f"  ✓ Test '{blueprint.name}' créé")
        print(f"{Colors.GREEN}{len(self.created_tests)} tests créés.{Colors.END}")

    # ------------------------------------------------------------------
    # Exécution de la campagne
    # ------------------------------------------------------------------
    def _run_campaign(self, filiere: str) -> None:
        assert self.campain_id
        rapport_name = self.api.get('/api/rapports/generate-name').get('name', f'Rapport {self.slug}')
        payload = {
            'campain_id': self.campain_id,
            'name': rapport_name,
            'filiere': filiere,
            'stop_on_failure': self.args.stop_on_failure
        }
        response = self.api.post('/api/rapports/execute', json=payload)
        self.rapport_id = response.get('rapport_id')
        if not self.rapport_id:
            raise ApiError('Impossible de récupérer le rapport créé')
        print(f"{Colors.BLUE}Rapport '{rapport_name}' lancé (ID: {self.rapport_id}).{Colors.END}")
        if not self.args.skip_websocket:
            self.run_result = self._monitor_via_websocket(self.rapport_id)
        else:
            self.run_result = self._poll_rapport_status(self.rapport_id)
        print(f"{Colors.GREEN if self.run_result == 'success' else Colors.RED}Résultat final: {self.run_result}{Colors.END}")

    def _monitor_via_websocket(self, rapport_id: str) -> str:
        finished = threading.Event()
        status_holder = {'result': 'pending'}
        sio = socketio.Client(reconnection=True, reconnection_attempts=5, reconnection_delay=2)

        @sio.event
        def connect() -> None:  # type: ignore
            print(f"{Colors.CYAN}[WebSocket] Connecté{Colors.END}")
            sio.emit('join_rapport', {'rapport_id': rapport_id})

        @sio.on('campain_progress')  # type: ignore
        def handle_progress(data: Dict[str, Any]) -> None:
            print(f"  → Progression: {data.get('progress', 0)}%")

        @sio.on('test_started')  # type: ignore
        def handle_test_started(data: Dict[str, Any]) -> None:
            print(f"  → Test {data.get('test_id')} démarré")

        @sio.on('test_completed')  # type: ignore
        def handle_test_completed(data: Dict[str, Any]) -> None:
            print(f"  → Test {data.get('test_id')} terminé ({data.get('status')})")

        @sio.on('campain_completed')  # type: ignore
        def handle_completed(data: Dict[str, Any]) -> None:
            status_holder['result'] = data.get('result', 'unknown')
            finished.set()

        @sio.on('campain_error')  # type: ignore
        def handle_error(data: Dict[str, Any]) -> None:
            print(f"{Colors.RED}Erreur campagne: {data.get('error')}{Colors.END}")
            status_holder['result'] = 'failure'
            finished.set()

        try:
            sio.connect(self.base_url, headers={'Authorization': f"Bearer {self.api.token}"}, transports=['websocket', 'polling'])
            finished.wait(timeout=self.args.run_timeout)
        except Exception as exc:  # pylint: disable=broad-except
            print(f"{Colors.YELLOW}WebSocket indisponible ({exc}), bascule sur polling HTTP...{Colors.END}")
            return self._poll_rapport_status(rapport_id)
        finally:
            with contextlib.suppress(Exception):
                sio.disconnect()
        if not finished.is_set():
            print(f"{Colors.YELLOW}Timeout WebSocket, bascule sur polling HTTP...{Colors.END}")
            return self._poll_rapport_status(rapport_id)
        return status_holder['result']

    def _poll_rapport_status(self, rapport_id: str) -> str:
        print(f"{Colors.CYAN}Suivi via HTTP polling...{Colors.END}")
        for _ in range(0, self.args.run_timeout or 300, 5):
            rapport = self.api.get(f"/api/rapports/{rapport_id}")
            status = rapport.get('status')
            progress = rapport.get('progress', 0)
            print(f"  → Statut: {status} ({progress}%)")
            if status in {'completed', 'failed'}:
                return rapport.get('result', 'failure')
            time.sleep(5)
        print(f"{Colors.YELLOW}Timeout de suivi atteinte.{Colors.END}")
        return 'unknown'

    # ------------------------------------------------------------------
    # Résumé & Nettoyage
    # ------------------------------------------------------------------
    def _sanitize_value(self, value: Dict[str, Any]) -> Dict[str, Any]:
        def _sanitize(obj: Any) -> Any:
            if isinstance(obj, dict):
                sanitized = {}
                for key, val in obj.items():
                    if 'password' in key.lower():
                        sanitized[key] = '***'
                    else:
                        sanitized[key] = _sanitize(val)
                return sanitized
            if isinstance(obj, list):
                return [_sanitize(item) for item in obj]
            return obj
        return _sanitize(value)

    def _print_summary(self) -> None:
        print(f"\n{Colors.BOLD}{Colors.BLUE}Résumé des tests générés:{Colors.END}")
        for test in self.created_tests:
            sanitized = self._sanitize_value(test['value'])
            print(f"- [{test['action'].upper()} / {test['variant']}] {test['name']}")
            print(textwrap.indent(json.dumps(sanitized, indent=2, ensure_ascii=False), prefix='    '))
        print(f"\nTotal: {len(self.created_tests)} tests")

    def _delete_campain(self) -> None:
        if not self.campain_id:
            return
        self.api.delete(f"/api/campains/{self.campain_id}")
        print(f"{Colors.GREEN}Campagne {self.campain_id} supprimée.{Colors.END}")
        self.campain_id = None

    # ------------------------------------------------------------------
    # Orchestration globale
    # ------------------------------------------------------------------
    def run(self) -> None:
        print(f"{Colors.HEADER}{Colors.BOLD}=== Création d'une campagne complète d'actions ==={Colors.END}")
        email = self.args.email or prompt_with_default('Email administrateur', 'admin@testgyver.local')
        password = self.args.password or getpass.getpass('Mot de passe: ')
        auth = self.api.login(email, password)
        if auth.get('user', {}).get('role') != 'admin':
            raise PermissionError('Ce script nécessite un utilisateur administrateur.')
        default_name = self.args.campain_name or 'Campagne de test complète'
        base_env = self.args.environment or 'test_env'
        name = self._ensure_campaign_name(prompt_with_default('Nom de la campagne', default_name))
        self.environment = prompt_with_default('Environnement cible', base_env)
        self._ensure_variables(self.environment)
        self._load_available_actions()
        self._create_campain(name)
        self._upload_mac_logo()
        self._prepare_external_services()
        self._prepare_local_assets()
        self._build_blueprints()
        self._create_tests()
        self._print_summary()
        if self.should_run is None:
            self.should_run = prompt_yes_no('Souhaitez-vous lancer la campagne maintenant ?', True)
        if self.should_run:
            self._run_campaign(self.environment)
        else:
            print(f"{Colors.YELLOW}Exécution manuelle possible plus tard via l'interface.{Colors.END}")
        if self.should_cleanup is None:
            self.should_cleanup = prompt_yes_no('Supprimer la campagne après exécution ?', True)
        if self.should_cleanup:
            self._delete_campain()
        print(f"{Colors.BOLD}{Colors.GREEN}Opérations terminées.{Colors.END}")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description='Crée une campagne de tests couvrant toutes les actions disponibles.',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument('--api-url', help='URL de base de l\'API (par exemple http://127.0.0.1:8080)')
    parser.add_argument('--email', help='Email administrateur utilisé pour l\'authentification')
    parser.add_argument('--password', help='Mot de passe administrateur (sinon questionné)')
    parser.add_argument('--campain-name', help='Nom initial proposé pour la campagne')
    parser.add_argument('--environment', help='Nom de l\'environnement (filière) à utiliser')
    parser.add_argument('--no-run', dest='should_run', action='store_false', help='Ne lance pas la campagne automatiquement')
    parser.add_argument('--run', dest='should_run', action='store_true', help='Lance la campagne sans confirmation')
    parser.set_defaults(should_run=None)
    parser.add_argument('--cleanup', dest='cleanup', action='store_true', help='Supprime la campagne sans confirmation')
    parser.add_argument('--keep', dest='cleanup', action='store_false', help='Conserve la campagne sans confirmation')
    parser.set_defaults(cleanup=None)
    parser.add_argument('--stop-on-failure', action='store_true', help='Arrête l\'exécution au premier échec de test')
    parser.add_argument('--skip-websocket', action='store_true', help='Désactive le suivi WebSocket et force le polling HTTP')
    parser.add_argument('--run-timeout', type=int, default=600, help='Timeout maximum (s) pour suivre l\'exécution')
    parser.add_argument('--verbose', action='store_true', help='Affiche les détails des requêtes API')
    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    creator = FullActionCampainCreator(args)
    if args.should_run is not None:
        creator.should_run = args.should_run
    if args.cleanup is not None:
        creator.should_cleanup = args.cleanup
    try:
        creator.run()
    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}Opération interrompue par l'utilisateur.{Colors.END}")
        if creator.campain_id and prompt_yes_no('Souhaitez-vous supprimer la campagne incomplète ?', True):
            creator._delete_campain()
    except Exception as exc:  # pylint: disable=broad-except
        print(f"{Colors.RED}Erreur critique: {exc}{Colors.END}")
        raise


if __name__ == '__main__':
    main()
