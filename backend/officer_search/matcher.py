"""
National University Bangladesh AI Assistant — Officer Database Matcher
Executes multi-stage parameterized SQL queries and coordinates with the ranking engine.
"""

import sqlite3
import difflib
from typing import Dict, Any, List, Optional, Tuple

from db.sql_store import get_sql_store
from .entity_extractor import OfficerQueryEntities
from .ranking import rank_officer_records
from .normalizer import normalize_text, normalize_phone, normalize_email
from .aliases import DESIGNATION_ALIASES, DEPARTMENT_ALIASES, NAME_TRANSLITERATION_MAP


class OfficerMatcher:
    def __init__(self):
        self.sql_store = get_sql_store()

    def find_matching_officers(self, entities: OfficerQueryEntities) -> Tuple[List[Dict[str, Any]], str, List[str]]:
        """
        Executes multi-stage candidate retrieval and deterministic ranking.
        Returns (ranked_officers_list, match_strategy, suggestions_if_any).
        """
        # Strategy 1: Strict Parametric SQL Search
        candidates = self._execute_parametric_sql(entities)
        match_strategy = "strict_parametric_sql"

        # Strategy 2: If 0 results and a name was extracted, try token search across name
        if not candidates and entities.name:
            candidates = self._execute_name_token_sql(entities)
            match_strategy = "name_token_search"

        # Strategy 3: If 0 results and typo suspected, run controlled fuzzy search
        suggestions = []
        if not candidates:
            fuzzy_candidates, suggestions = self._execute_fuzzy_recovery(entities)
            if fuzzy_candidates:
                candidates = fuzzy_candidates
                match_strategy = "fuzzy_recovery"

        # If still no candidates and query is ALL_OFFICERS
        if not candidates and entities.is_all_query:
            conn = self.sql_store._get_connection()
            try:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM officers_directory ORDER BY id ASC")
                candidates = [dict(row) for row in cursor.fetchall()]
                match_strategy = "all_officers_dump"
            finally:
                conn.close()

        # Rank all candidates deterministically
        ranked_tuples = rank_officer_records(candidates, entities)
        final_officers = [item[0] for item in ranked_tuples]

        # Generate suggestions from actual database values if 0 results
        if not final_officers and not suggestions:
            suggestions = self._generate_suggestions_from_db(entities)

        return final_officers, match_strategy, suggestions

    def _execute_parametric_sql(self, entities: OfficerQueryEntities) -> List[Dict[str, Any]]:
        """Executes parameterized SQL queries combining active entity filters with strict AND logic."""
        conn = self.sql_store._get_connection()
        try:
            cursor = conn.cursor()
            conditions = []
            params = []

            # 1. Email constraint
            if entities.email:
                conditions.append("email LIKE ?")
                params.append(f"%{entities.email}%")

            # 2. Phone constraint
            elif entities.phone:
                conditions.append("(phone LIKE ? OR phone LIKE ?)")
                params.extend([f"%{entities.phone}%", f"%{entities.phone[-7:]}%" if len(entities.phone) >= 7 else f"%{entities.phone}%"])

            # 3. Department constraint
            if entities.department_slug:
                conditions.append("(department_slug = ? OR department_name LIKE ?)")
                params.extend([entities.department_slug, f"%{entities.department_slug}%"])

            # 4. Designation constraint
            if entities.designation:
                target_en = entities.designation
                target_bn = entities.designation_bn or ""
                conditions.append("(designation_en LIKE ? OR designation_bn LIKE ?)")
                params.extend([f"%{target_en}%", f"%{target_bn}%" if target_bn else f"%{target_en}%"])

            # 5. Name constraint
            if entities.name:
                conditions.append("(name LIKE ? OR raw_details LIKE ?)")
                params.extend([f"%{entities.name}%", f"%{entities.name}%"])

            if not conditions:
                if entities.is_all_query:
                    cursor.execute("SELECT * FROM officers_directory ORDER BY id ASC")
                    return [dict(row) for row in cursor.fetchall()]
                return []

            sql_query = f"SELECT * FROM officers_directory WHERE {' AND '.join(conditions)} ORDER BY id ASC"
            cursor.execute(sql_query, params)
            return [dict(row) for row in cursor.fetchall()]
        finally:
            conn.close()

    def _execute_name_token_sql(self, entities: OfficerQueryEntities) -> List[Dict[str, Any]]:
        """Splits name into tokens and searches for any matching employee in target department or universally."""
        if not entities.name:
            return []
        tokens = [t.strip() for t in entities.name.split() if len(t.strip()) > 1]
        if not tokens:
            return []

        expanded_tokens = list(tokens)
        for t in tokens:
            t_lower = t.lower()
            if t_lower in NAME_TRANSLITERATION_MAP:
                expanded_tokens.extend(NAME_TRANSLITERATION_MAP[t_lower])

        conn = self.sql_store._get_connection()
        try:
            cursor = conn.cursor()
            conditions = ["(name LIKE ? OR raw_details LIKE ?)" for _ in expanded_tokens]
            token_conditions = " OR ".join(conditions)
            params = []
            for t in expanded_tokens:
                params.extend([f"%{t}%", f"%{t}%"])

            if entities.department_slug:
                sql_query = f"SELECT * FROM officers_directory WHERE ({token_conditions}) AND department_slug = ? ORDER BY id ASC"
                params.append(entities.department_slug)
            else:
                sql_query = f"SELECT * FROM officers_directory WHERE {token_conditions} ORDER BY id ASC LIMIT 50"

            cursor.execute(sql_query, params)
            return [dict(row) for row in cursor.fetchall()]
        finally:
            conn.close()

    def _execute_fuzzy_recovery(self, entities: OfficerQueryEntities) -> Tuple[List[Dict[str, Any]], List[str]]:
        """Attempts fuzzy recovery against known designations, departments, or personnel names."""
        suggestions = []
        recovered_records = []
        raw_norm = entities.normalized_query.lower()

        # Check for fuzzy match against canonical designations
        best_desig = None
        best_desig_score = 0.0
        for d in DESIGNATION_ALIASES:
            for alias in d["aliases"]:
                ratio = difflib.SequenceMatcher(None, raw_norm, alias.lower()).ratio()
                if ratio > best_desig_score and ratio >= 0.78:
                    best_desig_score = ratio
                    best_desig = d

        if best_desig:
            suggestions.append(f"{best_desig['canonical_bn']} ({best_desig['canonical_en']})")
            # Query DB for this recovered designation
            conn = self.sql_store._get_connection()
            try:
                cursor = conn.cursor()
                if entities.department_slug:
                    cursor.execute("""
                        SELECT * FROM officers_directory 
                        WHERE (designation_en LIKE ? OR designation_bn LIKE ?) AND department_slug = ?
                    """, (f"%{best_desig['canonical_en']}%", f"%{best_desig['canonical_bn']}%", entities.department_slug))
                else:
                    cursor.execute("""
                        SELECT * FROM officers_directory 
                        WHERE designation_en LIKE ? OR designation_bn LIKE ?
                    """, (f"%{best_desig['canonical_en']}%", f"%{best_desig['canonical_bn']}%"))
                recovered_records = [dict(row) for row in cursor.fetchall()]
            finally:
                conn.close()

        return recovered_records, suggestions

    def _generate_suggestions_from_db(self, entities: OfficerQueryEntities) -> List[str]:
        """Generates real 'Did you mean' suggestions based on database values."""
        suggestions = []
        raw_norm = entities.normalized_query.lower()

        # Suggest top matching designations
        for d in DESIGNATION_ALIASES[:10]:
            for a in d["aliases"]:
                if any(tok in a.lower() for tok in raw_norm.split() if len(tok) > 3):
                    cand = f"💼 {d['canonical_bn']} ({d['canonical_en']})"
                    if cand not in suggestions:
                        suggestions.append(cand)

        # Suggest top matching departments
        for dept in DEPARTMENT_ALIASES[:8]:
            for a in dept["aliases"]:
                if any(tok in a.lower() for tok in raw_norm.split() if len(tok) > 2):
                    cand = f"🏛️ {dept['name_bn']} ({dept['name_en']})"
                    if cand not in suggestions:
                        suggestions.append(cand)

        return suggestions[:4]
