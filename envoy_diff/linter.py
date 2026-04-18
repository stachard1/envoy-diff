"""Lint environment variable keys and values for style/convention issues."""
from dataclasses import dataclass, field
from typing import Dict, List
import re

@dataclass
class LintIssue:
    key: str
    message: str
    severity: str  # 'error' | 'warning'

@dataclass
class LintResult:
    issues: List[LintIssue] = field(default_factory=list)

def has_issues(result: LintResult) -> bool:
    return len(result.issues) > 0

def errors(result: LintResult) -> List[LintIssue]:
    return [i for i in result.issues if i.severity == 'error']

def warnings(result: LintResult) -> List[LintIssue]:
    return [i for i in result.issues if i.severity == 'warning']

def summary(result: LintResult) -> str:
    e = len(errors(result))
    w = len(warnings(result))
    return f"{e} error(s), {w} warning(s)"

_UPPER_SNAKE = re.compile(r'^[A-Z][A-Z0-9_]*$')
_NO_LEAD_DIGIT = re.compile(r'^[0-9]')

def lint_env(env: Dict[str, str], *, allow_lowercase: bool = False) -> LintResult:
    result = LintResult()
    for key, value in env.items():
        if _NO_LEAD_DIGIT.match(key):
            result.issues.append(LintIssue(key, "Key must not start with a digit", "error"))
        elif not allow_lowercase and not _UPPER_SNAKE.match(key):
            result.issues.append(LintIssue(key, "Key should be UPPER_SNAKE_CASE", "warning"))
        if '  ' in value:
            result.issues.append(LintIssue(key, "Value contains consecutive spaces", "warning"))
        if value != value.strip():
            result.issues.append(LintIssue(key, "Value has leading or trailing whitespace", "warning"))
        if len(value) == 0:
            result.issues.append(LintIssue(key, "Value is empty", "warning"))
    return result
