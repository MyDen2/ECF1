from abc import ABC, abstractmethod
import pandas as pd
import requests

# Classe de base pour les extracteurs

class BaseExtractor(ABC):
    """Classe de base pour les extracteurs"""

    def __init__(self, logger):
        # On garde une référence vers le logger pour tracer les opérations
        self.logger = logger

    @abstractmethod
    def extract(self):
        """Méthode à implémenter par les classes filles"""
        pass

# Extracteur CSV

# class CSVExtractor(BaseExtractor):
#     """Extracteur pour fichiers CSV"""

#     def extract(self, filepath):
#         """Extrait données d'un CSV"""
#         try:
#             self.logger.info(f"Extraction de {filepath}")
#             # Lecture du fichier CSV dans un DataFrame pandas
#             df = pd.read_csv(filepath)
#             self.logger.info(f"{len(df)} lignes extraites")
#             return df
#         except Exception as e:
#             self.logger.error(f"Erreur extraction CSV: {e}")
#             raise


# Extracteur API REST

class APIExtractor(BaseExtractor):
    """Extracteur pour API REST"""

    def __init__(self, logger, base_url, api_key=None):
        # On réutilise le constructeur de BaseExtractor
        super().__init__(logger)
        self.base_url = base_url
        self.api_key = api_key

    def extract(self, endpoint, params=None):
        """Extrait données d'une API"""
        try:
            self.logger.info(f"Extraction de {self.base_url}/{endpoint}")

            headers = {}
            # Si une clé d'API est fournie, on l'ajoute en header Authorization
            if self.api_key:
                headers['Authorization'] = f'Bearer {self.api_key}'

            # Appel HTTP GET
            response = requests.get(
                f"{self.base_url}/{endpoint}",
                params=params,
                headers=headers,
                timeout=30
            )
            # Lève une erreur si status code 4xx/5xx
            response.raise_for_status()

            data = response.json()
            self.logger.info(f"Données extraites")

            # Si l'API renvoie une liste, on la convertit en DataFrame
            return pd.DataFrame(data) if isinstance(data, list) else data

        except Exception as e:
            self.logger.error(f"Erreur extraction API: {e}")
            raise