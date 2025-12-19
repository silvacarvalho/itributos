"""
Cache Manager - Gerenciamento de cache para consultas SQL
"""
import hashlib
import json
from typing import Any, Optional
from diskcache import Cache
from config import CACHE_DIR, CACHE_TTL_SECONDS
import os


class CacheManager:
    """Gerenciador de cache em disco para consultas SQL"""
    
    def __init__(self, cache_dir: Optional[str] = None, ttl: Optional[int] = None):
        """
        Inicializa o gerenciador de cache
        
        Args:
            cache_dir: Diretório para armazenar o cache (padrão: CACHE_DIR do config)
            ttl: Tempo de vida do cache em segundos (padrão: CACHE_TTL_SECONDS)
        """
        self.cache_dir = cache_dir or CACHE_DIR
        self.ttl = ttl or CACHE_TTL_SECONDS
        
        # Cria diretório se não existir
        os.makedirs(self.cache_dir, exist_ok=True)
        
        # Inicializa cache
        self.cache = Cache(self.cache_dir)
        print(f"📦 Cache inicializado em: {self.cache_dir}")
        print(f"⏱️  TTL: {self.ttl} segundos ({self.ttl/3600:.1f} horas)")
    
    def _generate_key(self, sql: str, params: Optional[dict] = None) -> str:
        """
        Gera chave única para a consulta SQL
        
        Args:
            sql: Query SQL
            params: Parâmetros da query (opcional)
        
        Returns:
            Hash MD5 da query + parâmetros
        """
        content = sql.strip().lower()
        if params:
            content += json.dumps(params, sort_keys=True)
        
        return hashlib.md5(content.encode()).hexdigest()
    
    def get(self, sql: str, params: Optional[dict] = None) -> Optional[Any]:
        """
        Recupera resultado do cache
        
        Args:
            sql: Query SQL
            params: Parâmetros da query (opcional)
        
        Returns:
            Resultado em cache ou None se não encontrado
        """
        key = self._generate_key(sql, params)
        result = self.cache.get(key)
        
        if result is not None:
            print(f"✅ Cache HIT: {key[:12]}...")
        else:
            print(f"❌ Cache MISS: {key[:12]}...")
        
        return result
    
    def set(self, sql: str, result: Any, params: Optional[dict] = None) -> None:
        """
        Armazena resultado no cache
        
        Args:
            sql: Query SQL
            result: Resultado da query
            params: Parâmetros da query (opcional)
        """
        key = self._generate_key(sql, params)
        self.cache.set(key, result, expire=self.ttl)
        print(f"💾 Resultado armazenado no cache: {key[:12]}...")
    
    def clear(self) -> None:
        """Limpa todo o cache"""
        self.cache.clear()
        print("🗑️  Cache limpo")
    
    def get_stats(self) -> dict:
        """Retorna estatísticas do cache"""
        return {
            'size': len(self.cache),
            'directory': self.cache_dir,
            'ttl_seconds': self.ttl,
            'ttl_hours': self.ttl / 3600
        }
    
    def invalidate_query(self, sql: str, params: Optional[dict] = None) -> bool:
        """
        Invalida uma query específica do cache
        
        Args:
            sql: Query SQL
            params: Parâmetros da query (opcional)
        
        Returns:
            True se a chave foi encontrada e removida
        """
        key = self._generate_key(sql, params)
        return self.cache.delete(key)


# Exemplo de uso
if __name__ == '__main__':
    # Teste do cache
    cache = CacheManager()
    
    # Armazenar dados
    test_sql = "SELECT * FROM payments WHERE id = 1"
    test_result = [{'id': 1, 'value': 100.00}]
    
    cache.set(test_sql, test_result)
    
    # Recuperar dados
    cached = cache.get(test_sql)
    print(f"Resultado recuperado: {cached}")
    
    # Estatísticas
    stats = cache.get_stats()
    print(f"Estatísticas: {stats}")
    
    # Limpar cache
    # cache.clear()
