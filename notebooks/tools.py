import re

from difflib import SequenceMatcher
from agents import function_tool
from rich import print as rprint


def _normalize(text: str) -> str:
    return text.lower()


def _fuzzy_contains(
    keywords: str, terms: tuple[str, ...], threshold: float = 0.72
) -> bool:
    if not keywords:
        return False

    haystack = _normalize(keywords)
    normalized_terms = tuple(_normalize(term) for term in terms)

    if any(term in haystack for term in normalized_terms):
        return True

    tokens = [token for token in re.split(r"[\s,、。]+", haystack) if token]
    for token in tokens:
        for term in normalized_terms:
            if SequenceMatcher(None, token, term).ratio() >= threshold:
                return True

    for term in normalized_terms:
        if SequenceMatcher(None, haystack, term).ratio() >= threshold:
            return True
    return False


TERMS_1 = ("ネクサス3000", "Nexus 3000")
RESPONSE_1 = "「ネクサス3000」の搭載CPUは「エクリプスプロセッサX7」です。"

TERMS_2 = ("エクリプスプロセッサX7", "eclipse")
RESPONSE_2 = "「エクリプスプロセッサX7」の製造元は「クオンタムチップ社」です。"

TERMS_3 = ("クオンタムチップ社", "Quantum")
RESPONSE_3 = "「クオンタムチップ社」の本社は「神奈川県横浜市」です。"

UNKNOWN_RESPONSE = "情報が見つかりませんでした。"

# 優先度の高いものから順に評価する
SEARCH_RULES: tuple[tuple[tuple[str, ...], str], ...] = (
    (TERMS_3, RESPONSE_3),
    (TERMS_2, RESPONSE_2),
    (TERMS_1, RESPONSE_1),
)


def _search_documents_impl(keywords: str) -> list[str]:
    response = next(
        (
            candidate_response
            for terms, candidate_response in SEARCH_RULES
            if _fuzzy_contains(keywords, terms)
        ),
        UNKNOWN_RESPONSE,
    )

    print(">>> search_documents called")
    rprint({"keywords": keywords, "response": response})
    return [response]


# ツール版
search_documents = function_tool(_search_documents_impl)

tools = [
    {
        "type": "function",
        "name": "search_documents",
        "description": "ドキュメントデータベースから情報を検索します",
        "parameters": {
            "type": "object",
            "properties": {
                "keywords": {
                    "type": "string",
                    "description": "検索キーワード",
                },
            },
            "required": ["keywords"],
        },
    },
]

# 通常の関数版
search_documents_raw = _search_documents_impl
