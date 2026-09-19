#!/usr/bin/env python3
"""
NGK Sollai - Performance Optimizer
Caching, indexing, and efficiency improvements
"""

import json
import os
import time
from functools import lru_cache, wraps
from datetime import datetime, timedelta
import pickle

DATA_DIR = os.path.expanduser("~/NGK_Solai_Data")

class PerformanceOptimizer:
    def __init__(self):
        self.cache_dir = os.path.join(DATA_DIR, '.cache')
        os.makedirs(self.cache_dir, exist_ok=True)
        self.rule_cache = {}
        self.rule_index = {}
        self.stats = {
            'hits': 0,
            'misses': 0,
            'avg_lookup_time': 0
        }
    
    def cache_rules(self, rules_dict, cache_name='rules_cache'):
        """Cache rules to disk for faster loading"""
        print(f"💾 Caching {len(rules_dict)} rules...")
        
        cache_file = os.path.join(self.cache_dir, f"{cache_name}.pickle")
        
        try:
            with open(cache_file, 'wb') as f:
                pickle.dump(rules_dict, f)
            print(f"✅ Cache saved: {cache_file}")
            return cache_file
        except Exception as e:
            print(f"❌ Error caching rules: {e}")
            return None
    
    def load_cached_rules(self, cache_name='rules_cache'):
        """Load rules from cache"""
        cache_file = os.path.join(self.cache_dir, f"{cache_name}.pickle")
        
        if not os.path.exists(cache_file):
            return None
        
        try:
            with open(cache_file, 'rb') as f:
                rules = pickle.load(f)
            print(f"✅ Loaded from cache: {cache_file} ({len(rules)} rules)")
            return rules
        except Exception as e:
            print(f"⚠️  Error loading cache: {e}")
            return None
    
    def create_trie_index(self, words):
        """Create Trie data structure for O(1) prefix lookups"""
        print(f"🌳 Building Trie index for {len(words)} words...")
        
        trie = {}
        for word in words:
            node = trie
            for char in word:
                if char not in node:
                    node[char] = {}
                node = node[char]
            node['$'] = True  # Mark end of word
        
        print(f"✅ Trie index created with {len(words)} entries")
        return trie
    
    def lookup_in_trie(self, trie, prefix):
        """Fast prefix lookup in Trie"""
        node = trie
        for char in prefix:
            if char not in node:
                return []
            node = node[char]
        
        # Collect all words with this prefix
        words = []
        self._collect_words(node, prefix, words)
        return words
    
    def _collect_words(self, node, prefix, words):
        """Recursively collect words from trie"""
        if '$' in node:
            words.append(prefix)
        for char, child_node in node.items():
            if char != '$':
                self._collect_words(child_node, prefix + char, words)
    
    def create_bloom_filter(self, items, size=10000):
        """Create Bloom filter for membership testing"""
        print(f"🔍 Creating Bloom filter for {len(items)} items...")
        
        bloom = [False] * size
        
        for item in items:
            hash_val = hash(item) % size
            bloom[hash_val] = True
        
        print(f"✅ Bloom filter created (size: {size})")
        return bloom
    
    def check_bloom_filter(self, bloom, item):
        """Check if item might be in set (no false negatives)"""
        hash_val = hash(item) % len(bloom)
        return bloom[hash_val]
    
    def batch_process(self, items, func, batch_size=100):
        """Process items in batches for memory efficiency"""
        print(f"⚡ Processing {len(items)} items in batches of {batch_size}...")
        
        results = []
        for i in range(0, len(items), batch_size):
            batch = items[i:i + batch_size]
            batch_results = [func(item) for item in batch]
            results.extend(batch_results)
            
            # Progress indicator
            progress = min(i + batch_size, len(items))
            print(f"   Progress: {progress}/{len(items)}")
        
        return results
    
    def profile_function(self, func):
        """Decorator to profile function execution time"""
        @wraps(func)
        def wrapper(*args, **kwargs):
            start = time.time()
            result = func(*args, **kwargs)
            elapsed = time.time() - start
            print(f"⏱️  {func.__name__} took {elapsed:.4f}s")
            return result
        return wrapper
    
    def generate_performance_report(self, timing_data):
        """Generate performance analysis report"""
        print("\n📊 PERFORMANCE REPORT")
        print("="*60)
        
        if not timing_data:
            print("No timing data available")
            return
        
        for operation, times in timing_data.items():
            avg_time = sum(times) / len(times)
            min_time = min(times)
            max_time = max(times)
            
            print(f"\n{operation}:")
            print(f"  Average: {avg_time:.4f}s")
            print(f"  Min: {min_time:.4f}s")
            print(f"  Max: {max_time:.4f}s")
            print(f"  Calls: {len(times)}")
        
        print("="*60)
    
    def optimize_rules_for_lookup(self, rules):
        """Reorganize rules for faster lookups"""
        print(f"🔧 Optimizing {len(rules)} rules for lookups...")
        
        optimized = {
            'by_length': {},  # Group by word length
            'by_first_char': {},  # Group by first character
            'by_pattern': {},  # Group by pattern
            'direct': rules  # Direct lookup
        }
        
        for wrong, correct in rules.items():
            # By length
            length = len(wrong)
            if length not in optimized['by_length']:
                optimized['by_length'][length] = {}
            optimized['by_length'][length][wrong] = correct
            
            # By first character
            if wrong:
                first_char = wrong[0]
                if first_char not in optimized['by_first_char']:
                    optimized['by_first_char'][first_char] = {}
                optimized['by_first_char'][first_char][wrong] = correct
        
        print(f"✅ Rules optimized into {len(optimized['by_length'])} length groups")
        return optimized
    
    def estimate_memory_usage(self, rules):
        """Estimate memory usage of rules"""
        import sys
        
        total_size = 0
        for wrong, correct in rules.items():
            total_size += sys.getsizeof(wrong) + sys.getsizeof(correct)
        
        size_mb = total_size / (1024 * 1024)
        print(f"💾 Estimated memory usage: {size_mb:.2f} MB")
        
        return size_mb
    
    def generate_optimization_config(self):
        """Generate optimized configuration file"""
        print("\n⚙️  Generating optimization configuration...")
        
        config = {
            'metadata': {
                'created': datetime.now().isoformat(),
                'version': '1.0'
            },
            'performance': {
                'enable_caching': True,
                'cache_ttl_hours': 24,
                'batch_size': 100,
                'enable_bloom_filter': True,
                'enable_trie_index': True,
                'max_cache_size_mb': 500
            },
            'optimization': {
                'group_by_length': True,
                'group_by_first_char': True,
                'preload_common_words': True,
                'lazy_load_rules': False
            },
            'monitoring': {
                'log_lookup_times': True,
                'track_cache_hits': True,
                'generate_reports': True
            }
        }
        
        config_file = os.path.join(self.cache_dir, 'optimization_config.json')
        
        try:
            with open(config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2)
            print(f"✅ Config saved: {config_file}")
        except Exception as e:
            print(f"❌ Error saving config: {e}")
        
        return config

if __name__ == '__main__':
    optimizer = PerformanceOptimizer()
    print("✅ Performance Optimizer initialized")
    print("\nUsage in your code:")
    print("  from performance_optimizer import PerformanceOptimizer")
    print("  opt = PerformanceOptimizer()")
    print("  opt.cache_rules(rules_dict)")
    print("  opt.generate_optimization_config()")
