"""Local semantic-similarity embeddings for coarse course-candidate retrieval.

Uses `sentence-transformers` (all-MiniLM-L6-v2 by default) run locally — no extra API
key, no per-call cost. Trade-off vs. a hosted embeddings API (e.g. Voyage AI, Anthropic's
recommended embeddings partner): Voyage would likely produce higher-quality, more
discriminative embeddings, allowing a tighter similarity threshold with fewer false
positives/negatives, at the cost of a second paid API key and network dependency. The
function signatures below are the swap point — a future `embeddings_voyage.py`
implementing the same interface could replace this module without touching
`import_pipeline.py`.

Embeddings here are used ONLY for cheap candidate retrieval (narrowing which existing
courses to show the LLM). The final classification/structuring decision is always made
by Claude, which also sees the full untruncated source text.
"""

import json
from functools import lru_cache

from app.config import EMBEDDING_MODEL_NAME

# Character-length safety net applied before the embedding model's own internal
# tokenizer truncation (all-MiniLM-L6-v2 truncates at 256 tokens). This keeps the
# truncation deterministic and cheap regardless of how large the pasted text is.
# NOTE: this truncation only affects the *embedding* used for candidate retrieval —
# Claude always sees the full, untruncated text in import_pipeline.py.
_MAX_EMBED_CHARS = 3000


@lru_cache(maxsize=1)
def get_model():
    # Imported lazily so importing this module doesn't force torch to load until an
    # embedding is actually needed (keeps things like schema-only tooling fast).
    from sentence_transformers import SentenceTransformer

    return SentenceTransformer(EMBEDDING_MODEL_NAME)


def embed_text(title: str, text: str) -> list[float]:
    """Embed `title + text`, truncated to a safe character budget."""
    combined = f"{title}\n\n{text}"[:_MAX_EMBED_CHARS]
    vector = get_model().encode(combined, normalize_embeddings=True)
    return vector.tolist()


def embed_json(title: str, text: str) -> str:
    """Convenience wrapper: embed and return the JSON string ready for storage."""
    return json.dumps(embed_text(title, text))


def load_embedding(embedding_json: str | None) -> list[float] | None:
    if not embedding_json:
        return None
    return json.loads(embedding_json)


def cosine_similarity(a: list[float], b: list[float]) -> float:
    if not a or not b or len(a) != len(b):
        return 0.0
    dot = sum(x * y for x, y in zip(a, b))
    norm_a = sum(x * x for x in a) ** 0.5
    norm_b = sum(y * y for y in b) ** 0.5
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return dot / (norm_a * norm_b)


def compute_course_representative_embedding(title: str, description: str) -> list[float]:
    """A course's 'representative embedding' = embedding of its title + description.

    Chosen over an average-of-concepts centroid because it's far cheaper to keep
    fresh (only recomputed when the description changes, not on every concept
    insert) and the AI-authored description is already a compressed semantic
    summary of the course. Trade-off: this can go stale as concepts accumulate
    without the description being revisited — mitigated in import_pipeline.py by
    letting Claude optionally supply an `updated_course_description` when a new
    addition meaningfully shifts the course's scope, which triggers a recompute.
    """
    return embed_text(title, description)


def top_k_candidate_courses(
    new_embedding: list[float],
    courses: list,
    k: int,
    threshold: float,
) -> list[tuple[object, float]]:
    """Return up to `k` courses whose stored representative embedding has cosine
    similarity >= `threshold` against `new_embedding`, sorted by similarity
    descending. Courses with no stored embedding are skipped. An empty `courses`
    list or nothing clearing the threshold both simply return [] — the caller
    treats that as 'no adequate candidate, this is a new course.'

    NOTE: threshold=0.35 / k=3 are unvalidated starting defaults, not tuned
    values — see README / plan doc. all-MiniLM-L6-v2 cosine similarities for
    related-but-differently-worded text commonly land in 0.3-0.6; 0.35 is
    deliberately generous since missing a real candidate (false negative) is
    worse than showing Claude one it can simply ignore (false positive).
    """
    scored = []
    for course in courses:
        course_embedding = load_embedding(course.embedding)
        if course_embedding is None:
            continue
        score = cosine_similarity(new_embedding, course_embedding)
        if score >= threshold:
            scored.append((course, score))
    scored.sort(key=lambda pair: pair[1], reverse=True)
    return scored[:k]
