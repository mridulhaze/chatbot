"""
National University Bangladesh AI Assistant — Officer Result Ranking Engine
Implements deterministic scoring, multi-constraint validation, and strict filter enforcement.
"""

import difflib
from typing import Dict, Any, List, Tuple
from .entity_extractor import OfficerQueryEntities
from .normalizer import normalize_text, normalize_phone, normalize_email
from .aliases import NAME_TRANSLITERATION_MAP

SCORE_EXACT_NAME = 100
SCORE_EXACT_DESIGNATION = 100
SCORE_EXACT_DEPARTMENT = 100

SCORE_NORMALIZED_NAME = 90
SCORE_NORMALIZED_DESIGNATION = 90
SCORE_NORMALIZED_DEPARTMENT = 90

SCORE_ALIAS_MATCH = 80
SCORE_TOKEN_MATCH = 70
SCORE_PHRASE_MATCH = 65
SCORE_PREFIX_MATCH = 50
SCORE_FUZZY_MATCH = 30


def score_officer_record(record: Dict[str, Any], entities: OfficerQueryEntities) -> Tuple[float, List[str]]:
    """
    Computes a deterministic match score for a single database record.
    Returns (score, match_reasons).
    If an explicit constraint is violated (e.g. wrong department when department was requested),
    the score drops to 0.0 to prevent false positives.
    """
    score = 0.0
    reasons = []

    rec_name = normalize_text(record.get("name") or "")
    rec_desig_en = normalize_text(record.get("designation_en") or "")
    rec_desig_bn = normalize_text(record.get("designation_bn") or "")
    rec_dept_slug = normalize_text(record.get("department_slug") or "")
    rec_dept_name = normalize_text(record.get("department_name") or "")
    rec_phone = normalize_phone(record.get("phone") or "")
    rec_email = normalize_email(record.get("email") or "")

    # --- 1. Email Search ---
    if entities.email:
        if entities.email == rec_email:
            score += 150
            reasons.append("exact_email_match")
            return score, reasons
        else:
            return 0.0, ["email_mismatch"]

    # --- 2. Phone Search ---
    if entities.phone:
        if entities.phone in rec_phone or (len(entities.phone) >= 7 and entities.phone[-7:] in rec_phone):
            score += 150
            reasons.append("exact_phone_match")
            return score, reasons
        else:
            return 0.0, ["phone_mismatch"]

    # --- 3. Department Constraint Enforcement ---
    dept_matched = False
    if entities.department_slug:
        if entities.department_slug == rec_dept_slug or entities.department_slug in rec_dept_slug:
            score += SCORE_EXACT_DEPARTMENT
            dept_matched = True
            reasons.append("exact_department_match")
        elif entities.department_name and (entities.department_name in rec_dept_name or rec_dept_name in entities.department_name):
            score += SCORE_NORMALIZED_DEPARTMENT
            dept_matched = True
            reasons.append("normalized_department_match")
        else:
            # Explicit department requested, but this record belongs to another department -> REJECT
            return 0.0, ["department_mismatch"]

    # --- 4. Designation Constraint Enforcement ---
    desig_matched = False
    if entities.designation:
        target_desig_en = normalize_text(entities.designation).lower()
        target_desig_bn = normalize_text(entities.designation_bn or "").lower()

        # Check Exact / Canonical Match
        if target_desig_en == rec_desig_en.lower() or (target_desig_bn and target_desig_bn == rec_desig_bn.lower()):
            score += SCORE_EXACT_DESIGNATION
            desig_matched = True
            reasons.append("exact_designation_match")
        # Check Substring / Phrase Match with guard against overmatching (e.g. Programmer vs Assistant Programmer)
        elif target_desig_en in rec_desig_en.lower() or (target_desig_bn and target_desig_bn in rec_desig_bn.lower()):
            # If user asked for "Programmer" specifically, do not give full points to "Assistant Programmer" or "Senior Programmer"
            if target_desig_en == "programmer" and ("assistant" in rec_desig_en.lower() or "senior" in rec_desig_en.lower()):
                score += SCORE_TOKEN_MATCH - 20
                reasons.append("weak_designation_containment")
            else:
                score += SCORE_NORMALIZED_DESIGNATION
                desig_matched = True
                reasons.append("normalized_designation_match")
        else:
            # Fuzzy match on designation
            ratio_en = difflib.SequenceMatcher(None, target_desig_en, rec_desig_en.lower()).ratio()
            if ratio_en >= 0.85:
                score += SCORE_FUZZY_MATCH
                desig_matched = True
                reasons.append(f"fuzzy_designation_match({ratio_en:.2f})")
            else:
                # Explicit designation requested, but this record is different -> REJECT
                return 0.0, ["designation_mismatch"]

    # --- 5. Name Constraint Enforcement ---
    name_matched = False
    if entities.name:
        target_name = normalize_text(entities.name).lower()
        rec_name_lower = rec_name.lower()

        if target_name == rec_name_lower:
            score += SCORE_EXACT_NAME
            name_matched = True
            reasons.append("exact_name_match")
        elif target_name in rec_name_lower:
            score += SCORE_NORMALIZED_NAME
            name_matched = True
            reasons.append("substring_name_match")
        else:
            # Check transliteration variants across name and email
            trans_matched = False
            for tok in target_name.split():
                tok_l = tok.lower()
                variants = NAME_TRANSLITERATION_MAP.get(tok_l, [])
                for v in variants:
                    if v.lower() in rec_name_lower or v.lower() in rec_email:
                        score += SCORE_NORMALIZED_NAME
                        name_matched = True
                        trans_matched = True
                        reasons.append(f"transliterated_name_match({tok}->{v})")
                        break
                if trans_matched:
                    break

            if not trans_matched:
                # Token match across parts of name (e.g. "Mridul" in "Mridul Roy")
                target_tokens = set(target_name.split())
                rec_tokens = set(rec_name_lower.split())
                common_tokens = target_tokens.intersection(rec_tokens)
                if common_tokens:
                    score += SCORE_TOKEN_MATCH * (len(common_tokens) / len(target_tokens))
                    name_matched = True
                    reasons.append(f"token_name_match({','.join(common_tokens)})")
                else:
                    # Fuzzy match on full name
                    ratio = difflib.SequenceMatcher(None, target_name, rec_name_lower).ratio()
                    if ratio >= 0.75:
                        score += SCORE_FUZZY_MATCH * ratio
                        name_matched = True
                        reasons.append(f"fuzzy_name_match({ratio:.2f})")
                    else:
                        if not (entities.department_slug or entities.designation):
                            return 0.0, ["name_mismatch"]

    # --- 6. Multi-Entity Synergy Bonus ---
    # If query had multiple constraints and they all matched, give high boost
    constraints_count = sum([bool(entities.department_slug), bool(entities.designation), bool(entities.name)])
    if constraints_count >= 2:
        matched_count = sum([dept_matched, desig_matched, name_matched])
        if matched_count == constraints_count:
            score += 50.0
            reasons.append("all_constraints_satisfied_bonus")

    # If it's an ALL query (e.g. ALL_OFFICERS or department officer list without filter)
    if entities.is_all_query:
        score = 100.0
        reasons.append("all_officers_query")
    elif entities.intent == "OFFICER_BY_DEPARTMENT" and dept_matched and not entities.designation and not entities.name:
        score = 100.0
        reasons.append("full_department_listing")

    return score, reasons


def rank_officer_records(records: List[Dict[str, Any]], entities: OfficerQueryEntities) -> List[Tuple[Dict[str, Any], float, List[str]]]:
    """Scores, filters, and ranks candidate records in descending order of relevance."""
    scored_records = []
    for rec in records:
        score, reasons = score_officer_record(rec, entities)
        if score > 0:
            scored_records.append((rec, score, reasons))

    # Sort primarily by score descending, secondarily by record ID ascending
    scored_records.sort(key=lambda x: (x[1], -x[0].get("id", 0)), reverse=True)
    return scored_records
