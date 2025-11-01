"""Utilitaire WebDAV pour gérer les opérations WebDAV avec requêtes HTTP directes."""
import requests
from requests.auth import HTTPBasicAuth
import xml.etree.ElementTree as ET
from urllib.parse import urljoin, quote, unquote


class WebDAVClient:
    """Client WebDAV utilisant directement les requêtes HTTP."""
    
    def __init__(self, base_url, username=None, password=None):
        """
        Initialise le client WebDAV.
        
        Args:
            base_url: URL de base du serveur WebDAV
            username: Nom d'utilisateur (optionnel)
            password: Mot de passe (optionnel)
        """
        self.base_url = base_url.rstrip('/')
        self.auth = HTTPBasicAuth(username, password) if username and password else None
        self.session = requests.Session()
        if self.auth:
            self.session.auth = self.auth
    
    def _get_full_url(self, path):
        """
        Construit l'URL complète à partir du chemin.
        
        Args:
            path: Chemin relatif ou absolu
            
        Returns:
            URL complète
        """
        if not path:
            return self.base_url
        
        # Si le path commence par /, l'utiliser tel quel
        if path.startswith('/'):
            # Extraire juste le domaine de base_url
            from urllib.parse import urlparse
            parsed = urlparse(self.base_url)
            base = f"{parsed.scheme}://{parsed.netloc}"
            return base + path
        
        # Sinon, joindre avec base_url
        return urljoin(self.base_url + '/', path)
    
    def exists(self, path):
        """
        Vérifie si une ressource existe.
        
        Args:
            path: Chemin de la ressource
            
        Returns:
            True si la ressource existe, False sinon
        """
        url = self._get_full_url(path)
        response = self.session.head(url, allow_redirects=True)
        return response.status_code in [200, 301, 302]
    
    def is_directory(self, path):
        """
        Vérifie si un chemin est un répertoire.
        
        Args:
            path: Chemin à vérifier
            
        Returns:
            True si c'est un répertoire, False sinon
        """
        # Normaliser avec slash final pour les répertoires
        dir_path = path.rstrip('/') + '/'
        url = self._get_full_url(dir_path)
        
        headers = {'Depth': '0'}
        response = self.session.request('PROPFIND', url, headers=headers, allow_redirects=True)
        
        if response.status_code not in [200, 207]:
            return False
        
        # Parser la réponse XML pour vérifier le type
        try:
            root = ET.fromstring(response.content)
            ns = {'D': 'DAV:'}
            
            for response_elem in root.findall('.//D:response', ns):
                resourcetype = response_elem.find('.//D:resourcetype', ns)
                if resourcetype is not None:
                    collection = resourcetype.find('D:collection', ns)
                    return collection is not None
            
            return False
        except Exception:
            return False
    
    def list_directory(self, path):
        """
        Liste le contenu d'un répertoire.
        
        Args:
            path: Chemin du répertoire
            
        Returns:
            Liste de dictionnaires avec 'name', 'type', 'href'
        """
        # Normaliser avec slash final
        dir_path = path.rstrip('/') + '/'
        url = self._get_full_url(dir_path)
        
        headers = {'Depth': '1'}
        response = self.session.request('PROPFIND', url, headers=headers, allow_redirects=True)
        
        if response.status_code not in [200, 207]:
            raise Exception(f"Erreur lors du listing de {path}: {response.status_code} {response.text}")
        
        items = []
        
        try:
            root = ET.fromstring(response.content)
            ns = {'D': 'DAV:'}
            
            # Extraire le chemin depuis l'URL finale après redirections
            from urllib.parse import urlparse
            final_parsed = urlparse(response.url)
            parent_path = unquote(final_parsed.path).rstrip('/')
            
            for response_elem in root.findall('.//D:response', ns):
                href_elem = response_elem.find('D:href', ns)
                if href_elem is None:
                    continue
                
                href = unquote(href_elem.text).rstrip('/')
                
                # Extraire juste le chemin depuis l'URL complète si nécessaire
                if href.startswith('http://') or href.startswith('https://'):
                    href = urlparse(href).path
                
                # Ignorer le répertoire parent lui-même
                # Comparer les chemins normalisés (sans slash final)
                if href == parent_path:
                    continue
                
                # Déterminer le type
                resourcetype = response_elem.find('.//D:resourcetype', ns)
                is_dir = False
                if resourcetype is not None:
                    collection = resourcetype.find('D:collection', ns)
                    is_dir = collection is not None
                
                item = {
                    'name': href,
                    'type': 'directory' if is_dir else 'file',
                    'href': href
                }
                
                items.append(item)
        
        except ET.ParseError as e:
            raise Exception(f"Erreur de parsing XML: {str(e)}")
        
        return items
    
    def remove(self, path):
        """
        Supprime une ressource (fichier ou répertoire vide).
        
        Args:
            path: Chemin de la ressource à supprimer
        """
        url = self._get_full_url(path)
        response = self.session.request('DELETE', url, allow_redirects=True)
        
        if response.status_code not in [200, 204, 404]:
            raise Exception(f"Erreur lors de la suppression de {path}: {response.status_code} {response.text}")
    
    def delete(self, path, recursive=False):
        """
        Supprime une ressource (fichier ou répertoire).
        
        Args:
            path: Chemin de la ressource à supprimer
            recursive: Si True, supprime récursivement le contenu des répertoires
        """
        # Si ce n'est pas récursif, utiliser simplement remove
        if not recursive:
            self.remove(path)
            return
        
        # Vérifier si c'est un répertoire
        if not self.is_directory(path):
            # C'est un fichier, le supprimer directement
            self.remove(path)
            return
        
        # C'est un répertoire, lister et supprimer récursivement
        try:
            items = self.list_directory(path)
            
            # Supprimer chaque élément
            for item in items:
                item_name = item['name']
                
                if item['type'] == 'directory':
                    # Appel récursif pour le sous-répertoire
                    self.delete(item_name, recursive=True)
                else:
                    # Supprimer le fichier
                    self.remove(item_name)
            
            # Une fois vide, supprimer le répertoire avec slash final
            dir_path = path.rstrip('/') + '/'
            self.remove(dir_path)
            
        except Exception as e:
            raise Exception(f"Erreur lors de la suppression récursive de {path}: {str(e)}")
    
    def mkdir(self, path):
        """
        Crée un répertoire.
        
        Args:
            path: Chemin du répertoire à créer
        """
        url = self._get_full_url(path)
        response = self.session.request('MKCOL', url, allow_redirects=True)
        
        if response.status_code not in [200, 201, 405]:  # 405 = déjà existe
            raise Exception(f"Erreur lors de la création de {path}: {response.status_code} {response.text}")
    
    def upload_file(self, local_path, remote_path):
        """
        Upload un fichier.
        
        Args:
            local_path: Chemin local du fichier
            remote_path: Chemin distant de destination
        """
        url = self._get_full_url(remote_path)
        
        with open(local_path, 'rb') as f:
            response = self.session.put(url, data=f, allow_redirects=True)
        
        if response.status_code not in [200, 201, 204]:
            raise Exception(f"Erreur lors de l'upload de {local_path}: {response.status_code} {response.text}")
    
    def download_file(self, remote_path, local_path):
        """
        Télécharge un fichier.
        
        Args:
            remote_path: Chemin distant du fichier
            local_path: Chemin local de destination
        """
        url = self._get_full_url(remote_path)
        response = self.session.get(url, allow_redirects=True, stream=True)
        
        if response.status_code not in [200]:
            raise Exception(f"Erreur lors du téléchargement de {remote_path}: {response.status_code}")
        
        with open(local_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
    
    def move(self, src_path, dest_path, overwrite=False):
        """
        Déplace/renomme une ressource.
        
        Args:
            src_path: Chemin source
            dest_path: Chemin destination
            overwrite: Écraser si existe
        """
        src_url = self._get_full_url(src_path)
        dest_url = self._get_full_url(dest_path)
        
        headers = {
            'Destination': dest_url,
            'Overwrite': 'T' if overwrite else 'F'
        }
        
        response = self.session.request('MOVE', src_url, headers=headers, allow_redirects=True)
        
        if response.status_code not in [200, 201, 204]:
            raise Exception(f"Erreur lors du déplacement de {src_path}: {response.status_code} {response.text}")
    
    def info(self, path):
        """
        Obtient les informations sur une ressource.
        
        Args:
            path: Chemin de la ressource
            
        Returns:
            Dictionnaire avec les propriétés
        """
        url = self._get_full_url(path)
        headers = {'Depth': '0'}
        response = self.session.request('PROPFIND', url, headers=headers, allow_redirects=True)
        
        if response.status_code not in [200, 207]:
            raise Exception(f"Erreur lors de la récupération des infos de {path}: {response.status_code}")
        
        try:
            root = ET.fromstring(response.content)
            ns = {'D': 'DAV:'}
            
            info = {}
            
            for response_elem in root.findall('.//D:response', ns):
                # Type
                resourcetype = response_elem.find('.//D:resourcetype', ns)
                if resourcetype is not None:
                    collection = resourcetype.find('D:collection', ns)
                    info['type'] = 'directory' if collection is not None else 'file'
                
                # Taille
                contentlength = response_elem.find('.//D:getcontentlength', ns)
                if contentlength is not None:
                    info['size'] = int(contentlength.text)
                
                # Date de modification
                lastmodified = response_elem.find('.//D:getlastmodified', ns)
                if lastmodified is not None:
                    info['modified'] = lastmodified.text
                
                break  # On prend juste le premier élément
            
            return info
            
        except ET.ParseError as e:
            raise Exception(f"Erreur de parsing XML: {str(e)}")
