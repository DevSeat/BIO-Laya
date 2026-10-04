"""Optional DevSeat Context Optimizer integration.

This module intentionally does not add a hard package dependency. The context
optimizer is imported only when the helper is called.
"""


def with_context_optimizer(router, *, token_budget: int, **kwargs):
    """Wrap an existing Laya Router with DevSeat context optimization.

    Install devseat-cognitive-guard separately (for example from a sibling
    development checkout) before calling this helper.
    """

    try:
        from devseat_cognitive_guard.integrations.bio_laya import (
            OptimizingLayaRouter,
        )
    except ImportError as exc:
        raise ImportError(
            "devseat-cognitive-guard is required for context optimization; "
            "install it before calling with_context_optimizer"
        ) from exc

    return OptimizingLayaRouter(
        router,
        token_budget=token_budget,
        **kwargs,
    )
