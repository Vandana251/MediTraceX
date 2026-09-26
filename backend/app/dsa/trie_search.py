"""
=============================================================================
MediTraceX: Trie Prefix Search & Fuzzy Matching DSA Engine
=============================================================================
Module: backend.app.dsa.trie_search

Description:
    Implements an in-memory Trie (Prefix Tree) data structure for ultra-fast,
    sub-millisecond medicine search across full names, generic compounds,
    and brand aliases. Includes a Trie-branch Levenshtein DP algorithm for
    graceful typo and fuzzy search fallback.

Time Complexity:
    - Insertion: O(L) where L is the length of the medicine name/alias string.
    - Prefix Search: O(L + K) where L is query length and K is the number of
      retrieved subtree results.
    - Fuzzy/Typo Search: O(V * L) where V is the count of visited pruned Trie
      nodes within edit distance threshold, avoiding brute-force O(N * L) scans.

Space Complexity:
    - Trie Storage: O(Sigma * N * M) where N is total items, M is average string
      length, and Sigma is character alphabet size.
=============================================================================
"""

from typing import Dict, List, Optional, Set, Any
from dataclasses import dataclass, field


@dataclass
class SearchResult:
    """Represents a matched medicine from Trie or Fuzzy search."""
    id: int
    name: str
    generic_name: str
    brand_name: str
    dosage: str
    dosage_form: str
    category: str
    unit_price: float
    match_type: str = "prefix" # "exact", "prefix", "fuzzy"
    edit_distance: int = 0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "generic_name": self.generic_name,
            "brand_name": self.brand_name,
            "dosage": self.dosage,
            "dosage_form": self.dosage_form,
            "category": self.category,
            "unit_price": self.unit_price,
            "match_type": self.match_type,
            "edit_distance": self.edit_distance
        }


class TrieNode:
    """A Node in the Trie representing a single normalized character."""
    def __init__(self):
        self.children: Dict[str, "TrieNode"] = {}
        self.is_end_of_word: bool = False
        self.medicine_ids: Set[int] = set()


class MedicineTrieSearch:
    """
    High-performance Trie Search Engine for MediTraceX.
    Indexes medicine full names, brand names, generic active ingredients,
    and word tokens for fast autocomplete and typo tolerance.
    """

    def __init__(self):
        self.root = TrieNode()
        self.medicine_catalog: Dict[int, Dict[str, Any]] = {}
        self.total_indexed_terms: int = 0

    @staticmethod
    def _normalize(text: str) -> str:
        """Sanitizes and normalizes input text for case-insensitive indexing."""
        if not text:
            return ""
        # Keep alphanumeric, spaces, and hyphens/dots
        return "".join(ch.lower() for ch in text if ch.isalnum() or ch in " -./").strip()

    def insert_medicine(self, medicine_data: Dict[str, Any]) -> None:
        """
        Inserts a medicine and all its aliases (name, generic name, brand name,
        and individual keywords) into the Trie.
        
        Complexity: O(Total Tokens * Length)
        """
        med_id = int(medicine_data["id"])
        self.medicine_catalog[med_id] = medicine_data

        # Phrases and tokens to index
        terms_to_index: Set[str] = set()
        
        for key in ["name", "generic_name", "brand_name"]:
            val = medicine_data.get(key)
            if val:
                normalized = self._normalize(str(val))
                if normalized:
                    terms_to_index.add(normalized)
                    # Also index sub-words (e.g. "Paracetamol 650mg" -> "650mg", "Paracetamol")
                    for token in normalized.split():
                        if len(token) >= 2:
                            terms_to_index.add(token)

        for term in terms_to_index:
            self._insert_term(term, med_id)
            self.total_indexed_terms += 1

    def _insert_term(self, term: str, medicine_id: int) -> None:
        """Inserts a single normalized string into the Trie structure."""
        curr = self.root
        for char in term:
            if char not in curr.children:
                curr.children[char] = TrieNode()
            curr = curr.children[char]
            # Add medicine ID at intermediate nodes for fast prefix discovery
            curr.medicine_ids.add(medicine_id)
        curr.is_end_of_word = True

    def search_prefix(self, prefix: str, limit: int = 10) -> List[SearchResult]:
        """
        Performs sub-millisecond Prefix Search.
        
        Algorithm:
        1. Traverse down the Trie using query prefix characters.
        2. If prefix path is found, collect matching medicine IDs attached to the node.
        3. Lookup medicine metadata and format results.
        
        Time Complexity: O(L + K) where L = len(prefix), K = len(matched items).
        """
        normalized_query = self._normalize(prefix)
        if not normalized_query:
            return []

        curr = self.root
        for char in normalized_query:
            if char not in curr.children:
                return [] # No prefix match
            curr = curr.children[char]

        results: List[SearchResult] = []
        for med_id in curr.medicine_ids:
            if med_id in self.medicine_catalog:
                data = self.medicine_catalog[med_id]
                match_type = "exact" if self._normalize(data["name"]) == normalized_query else "prefix"
                results.append(SearchResult(
                    id=med_id,
                    name=data["name"],
                    generic_name=data["generic_name"],
                    brand_name=data["brand_name"],
                    dosage=data["dosage"],
                    dosage_form=data["dosage_form"],
                    category=data["category"],
                    unit_price=float(data["unit_price"]),
                    match_type=match_type,
                    edit_distance=0
                ))
                if len(results) >= limit:
                    break

        return results

    def fuzzy_search(self, query: str, max_distance: int = 2, limit: int = 10) -> List[SearchResult]:
        """
        Levenshtein Dynamic Programming directly over Trie branches.
        
        Prunes Trie branches whose edit distance exceeds max_distance,
        enabling instant typo recovery without scanning all database rows.
        
        Time Complexity: O(V * L) where V is visited pruned Trie vertices.
        """
        normalized_query = self._normalize(query)
        if not normalized_query:
            return []

        # Initial DP row: 0, 1, 2, 3, ... |query|
        initial_row = list(range(len(normalized_query) + 1))
        matched_med_ids: Dict[int, int] = {} # med_id -> minimum edit distance

        for char, child_node in self.root.children.items():
            self._fuzzy_search_recursive(
                child_node, char, normalized_query, initial_row,
                matched_med_ids, max_distance
            )

        # Sort matches by minimum edit distance ascending
        sorted_matches = sorted(matched_med_ids.items(), key=lambda item: item[1])
        
        results: List[SearchResult] = []
        for med_id, dist in sorted_matches[:limit]:
            if med_id in self.medicine_catalog:
                data = self.medicine_catalog[med_id]
                results.append(SearchResult(
                    id=med_id,
                    name=data["name"],
                    generic_name=data["generic_name"],
                    brand_name=data["brand_name"],
                    dosage=data["dosage"],
                    dosage_form=data["dosage_form"],
                    category=data["category"],
                    unit_price=float(data["unit_price"]),
                    match_type="fuzzy",
                    edit_distance=dist
                ))

        return results

    def _fuzzy_search_recursive(
        self,
        node: TrieNode,
        char: str,
        query: str,
        previous_row: List[int],
        matched_med_ids: Dict[int, int],
        max_distance: int
    ) -> None:
        """Recursive helper evaluating Levenshtein matrix on Trie edges."""
        cols = len(query) + 1
        current_row = [previous_row[0] + 1]

        for col in range(1, cols):
            insert_cost = current_row[col - 1] + 1
            delete_cost = previous_row[col] + 1
            replace_cost = previous_row[col - 1] if query[col - 1] == char else previous_row[col - 1] + 1

            current_row.append(min(insert_cost, delete_cost, replace_cost))

        # If current path matches word end or intermediate with acceptable distance
        if current_row[-1] <= max_distance and node.is_end_of_word:
            dist = current_row[-1]
            for med_id in node.medicine_ids:
                if med_id not in matched_med_ids or dist < matched_med_ids[med_id]:
                    matched_med_ids[med_id] = dist

        # Pruning condition: if min value in row <= max_distance, continue branch exploration
        if min(current_row) <= max_distance:
            for next_char, next_node in node.children.items():
                self._fuzzy_search_recursive(
                    next_node, next_char, query, current_row,
                    matched_med_ids, max_distance
                )

    def search(self, query: str, limit: int = 10) -> List[SearchResult]:
        """
        Unified Search Gateway:
        1. Executes sub-millisecond Prefix Search.
        2. If no prefix results found, triggers Levenshtein Fuzzy Search.
        3. Deduplicates and preserves optimal ranking.
        """
        clean_query = self._normalize(query)
        if not clean_query:
            return []

        # 1. Primary Prefix Search
        prefix_results = self.search_prefix(clean_query, limit=limit)
        if len(prefix_results) > 0:
            return prefix_results

        # 2. Fallback Fuzzy Search (only when prefix yields no direct hits)
        return self.fuzzy_search(clean_query, max_distance=2, limit=limit)
