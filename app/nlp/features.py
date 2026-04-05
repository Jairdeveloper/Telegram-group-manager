import numpy as np
from typing import List, Dict, Optional
from sklearn.feature_extraction.text import TfidfVectorizer

from app.nlp.tokenizer import TokenizationResult


class FeatureExtractor:
    """Extrae features para ML classifier"""

    def __init__(self, max_features: int = 300, min_df: int = 1):
        self.max_features = max_features
        self.min_df = min_df
        self.tfidf_vectorizer = TfidfVectorizer(
            max_features=max_features,
            ngram_range=(1, 2),
            min_df=min_df,
            max_df=0.8,
            sublinear_tf=True
        )
        self.is_fitted = False

    def fit(self, textual_inputs: List[str], labels: List[str] = None):
        """Fit TF-IDF en los datos de entrenamiento"""
        self.tfidf_vectorizer.fit(textual_inputs)
        self.is_fitted = True
        return self

    def transform(self, textual_inputs: List[str]) -> np.ndarray:
        """Transform textual inputs to feature matrix"""
        if not self.is_fitted:
            raise ValueError("Fit extractor first!")
        return self.tfidf_vectorizer.transform(textual_inputs).toarray()

    def extract(self, tokenization_result: TokenizationResult) -> np.ndarray:
        """
        Extrae features de TokenizationResult

        Componentes:
        1. TF-IDF de lemmas (300 dims)
        2. POS patterns (20 dims)
        3. Dependency features (10 dims)
        4. Keyword presence (20 dims)

        Total: 350 dimensions
        """
        if not self.is_fitted:
            raise ValueError("Fit extractor first!")

        lemma_text = " ".join(tokenization_result.lemmas)
        tfidf_features = self.tfidf_vectorizer.transform([lemma_text]).toarray()[0]

        pos_patterns = self._extract_pos_patterns(tokenization_result)
        dep_features = self._extract_dependency_features(tokenization_result)
        keyword_features = self._extract_keyword_features(tokenization_result)

        features = np.concatenate([
            tfidf_features,
            pos_patterns,
            dep_features,
            keyword_features
        ])

        return features

    def _extract_pos_patterns(self, result: TokenizationResult) -> np.ndarray:
        """Extrae patrones de POS tags"""
        pos_counts = {}
        for _, pos in result.pos_tags:
            pos_counts[pos] = pos_counts.get(pos, 0) + 1

        total = len(result.tokens) if result.tokens else 1
        all_pos = ['VERB', 'NOUN', 'ADJ', 'ADV', 'ADP', 'DET', 'AUX', 'PRON', 'CCONJ', 'PROPN']

        features = np.array([
            pos_counts.get(pos, 0) / total for pos in all_pos
        ])

        return features

    def _extract_dependency_features(self, result: TokenizationResult) -> np.ndarray:
        """Extrae features de dependencias"""
        dep_counts = {}
        for _, dep in result.deps:
            dep_counts[dep] = dep_counts.get(dep, 0) + 1

        all_deps = ['ROOT', 'OBJ', 'NMOD', 'AMOD', 'DET', 'ADVMOD', 'CC', 'CONJ', 'AUX', 'MARK']

        features = np.array([
            dep_counts.get(dep, 0) for dep in all_deps
        ])

        return features

    def _extract_keyword_features(self, result: TokenizationResult) -> np.ndarray:
        """Extrae presencia de keywords importantes"""
        action_keywords = {
            'set_welcome': ['cambiar', 'configurar', 'bienvenida', 'set', 'change', 'welcome'],
            'set_goodbye': ['despedida', 'goodbye', 'farewell', 'salir', 'exit'],
            'toggle_feature': ['activar', 'desactivar', 'enable', 'disable', 'toggle', 'on', 'off'],
            'add_filter': ['bloquear', 'filtrar', 'agregar', 'block', 'filter', 'add'],
            'remove_filter': ['desbloquear', 'quitar', 'eliminar', 'unblock', 'remove'],
            'get_status': ['estado', 'status', 'verificar', 'check', 'estado'],
            'get_settings': ['configuracion', 'settings', 'opciones', 'ajustes', 'preferencias'],
            'update_config': ['actualizar', 'modificar', 'cambiar', 'update', 'modify', 'change'],
            'query_data': ['buscar', 'consultar', 'query', 'search', 'obtener', 'get'],
            'execute_action': ['ejecutar', 'iniciar', 'start', 'run', 'execute', 'perform'],
            'create_task': ['crear', 'nueva', 'nuevo', 'create', 'new', 'add'],
            'delete_task': ['eliminar', 'borrar', 'cancelar', 'delete', 'remove', 'cancel'],
            'assign_role': ['asignar', 'role', 'rol', 'assign', 'set'],
            'grant_permission': ['otorgar', 'permiso', 'grant', 'permission', 'allow'],
            'revoke_permission': ['revocar', 'revoke', 'deny', 'remove']
        }

        features = []
        lemmas_lower = [l.lower() for l in result.lemmas]

        for intent, keywords in action_keywords.items():
            has_keyword = any(kw in lemmas_lower for kw in keywords)
            features.append(float(has_keyword))

        return np.array(features)

    def get_feature_names(self) -> List[str]:
        """Retorna nombres de features"""
        tfidf_names = self.tfidf_vectorizer.get_feature_names_out().tolist()

        pos_names = [f'pos_{pos}' for pos in ['VERB', 'NOUN', 'ADJ', 'ADV', 'ADP', 'DET', 'AUX', 'PRON', 'CCONJ', 'PROPN']]
        dep_names = [f'dep_{dep}' for dep in ['ROOT', 'OBJ', 'NMOD', 'AMOD', 'DET', 'ADVMOD', 'CC', 'CONJ', 'AUX', 'MARK']]

        keyword_names = [
            'kw_set_welcome', 'kw_set_goodbye', 'kw_toggle_feature',
            'kw_add_filter', 'kw_remove_filter', 'kw_get_status',
            'kw_get_settings', 'kw_update_config', 'kw_query_data',
            'kw_execute_action', 'kw_create_task', 'kw_delete_task',
            'kw_assign_role', 'kw_grant_permission', 'kw_revoke_permission'
        ]

        return tfidf_names + pos_names + dep_names + keyword_names