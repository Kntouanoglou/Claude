from functools import lru_cache

import anthropic

from app.config import ANTHROPIC_API_KEY, CLAUDE_EFFORT, CLAUDE_MODEL

MODEL = CLAUDE_MODEL
EFFORT = CLAUDE_EFFORT
MAX_TOKENS = 8192


@lru_cache(maxsize=1)
def get_client() -> anthropic.Anthropic:
    # Anthropic() resolves ANTHROPIC_API_KEY from the environment on its own; passing
    # it explicitly here just gives us a clearer error message if it's unset.
    if not ANTHROPIC_API_KEY:
        raise RuntimeError(
            "ANTHROPIC_API_KEY is not set. Copy backend/.env.example to backend/.env "
            "and fill it in."
        )
    return anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
