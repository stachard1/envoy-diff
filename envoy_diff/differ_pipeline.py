"""Pipeline: chain multiple env transformations before diffing."""
from dataclasses import dataclass, field
from typing import Callable, Dict, List, Optional

from envoy_diff.differ import diff_envs, EnvDiffResult
from envoy_diff.transformer import apply_transforms, TransformRule
from envoy_diff.filter import filter_by_prefix, filter_by_pattern
from envoy_diff.redactor import redact_env

Env = Dict[str, str]
Step = Callable[[Env], Env]


@dataclass
class PipelineResult:
    before: Env
    after: Env
    diff: EnvDiffResult
    steps_applied: List[str] = field(default_factory=list)

    @property
    def has_changes(self) -> bool:
        return self.diff.has_changes

    def summary(self) -> str:
        parts = [f"Steps: {', '.join(self.steps_applied) if self.steps_applied else 'none'}"]
        parts.append(self.diff.summary())
        return " | ".join(parts)


@dataclass
class Pipeline:
    _steps: List[tuple] = field(default_factory=list)

    def filter_prefix(self, prefix: str) -> "Pipeline":
        self._steps.append(("filter_prefix", prefix))
        return self

    def filter_pattern(self, pattern: str) -> "Pipeline":
        self._steps.append(("filter_pattern", pattern))
        return self

    def transform(self, rules: List[TransformRule]) -> "Pipeline":
        self._steps.append(("transform", rules))
        return self

    def redact(self) -> "Pipeline":
        self._steps.append(("redact", None))
        return self

    def _apply(self, env: Env) -> tuple[Env, List[str]]:
        applied: List[str] = []
        for name, arg in self._steps:
            if name == "filter_prefix":
                env = filter_by_prefix(env, arg).matched
                applied.append(f"filter_prefix({arg})")
            elif name == "filter_pattern":
                env = filter_by_pattern(env, arg).matched
                applied.append(f"filter_pattern({arg})")
            elif name == "transform":
                env = apply_transforms(env, arg).env
                applied.append("transform")
            elif name == "redact":
                env = redact_env(env)
                applied.append("redact")
        return env, applied

    def run(self, before: Env, after: Env) -> PipelineResult:
        before_out, steps_a = self._apply(dict(before))
        after_out, steps_b = self._apply(dict(after))
        steps = list(dict.fromkeys(steps_a + steps_b))
        result = diff_envs(before_out, after_out)
        return PipelineResult(before=before_out, after=after_out, diff=result, steps_applied=steps)


def build_pipeline() -> Pipeline:
    """Return a fresh Pipeline builder."""
    return Pipeline()
