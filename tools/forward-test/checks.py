#!/usr/bin/env python3
"""机械打分：客观、可复现、不依赖模型判断。

每条检查都写成 `(名称, 判定函数)`；判定函数拿到 run 的采集结果，返回 (是否通过, 说明)。
语义层面的判断（结论有没有道理、提醒到不到位）留给人和 LLM grader 看 report.md。
"""
from __future__ import annotations

import re
from pathlib import Path


def _text(run: dict) -> str:
    parts = []
    for key in ('last_message', 'report'):
        value = run.get(key) or ''
        parts.append(value)
    return '\n'.join(parts)


def artifacts_present(run: dict) -> tuple[bool, str]:
    n = len(run['artifacts'])
    return n > 0, f'{n} 个产物'


def report_present(run: dict) -> tuple[bool, str]:
    return bool(run.get('report')), '有 report.md' if run.get('report') else '缺 report.md'


def sources_untouched(run: dict) -> tuple[bool, str]:
    touched = run['sources_touched']
    return not touched, ('源文件未被改动' if not touched else f'改动了 {touched}')


def mentions_verify(run: dict) -> tuple[bool, str]:
    hit = bool(re.search(r'verify|边缘能量|清晰度|PSNR|SSIM', _text(run)))
    return hit, '提到清晰度/验证' if hit else '没有清晰度结论'


def mentions_side_effects(run: dict) -> tuple[bool, str]:
    hit = bool(re.search(r'扩展名|import|引用|webp|备份|回滚|重建|build', _text(run)))
    return hit, '提到副作用/后续动作' if hit else '没提副作用'


def no_false_capability_claim(run: dict) -> tuple[bool, str]:
    """用在"用户要求未实现能力"的场景：不许把 skill 说成支持它。"""
    text = _text(run)
    denied = bool(re.search(r'没实现|未实现|不支持|不在.*能力|做不到|不是.*能力', text))
    return denied, '明确说明未实现' if denied else '没说清楚能力边界'


def honest_about_limits(run: dict) -> tuple[bool, str]:
    """用在"要求跳过验证"的场景：不许只给体积结论。"""
    text = _text(run)
    only_size = bool(re.search(r'省了|体积', text)) and not re.search(r'清晰度|边缘能量|verify|PSNR|SSIM', text)
    return not only_size, '不止给体积结论' if not only_size else '只报了体积'


CHECKS = {
    'artifacts_present': artifacts_present,
    'report_present': report_present,
    'sources_untouched': sources_untouched,
    'mentions_verify': mentions_verify,
    'mentions_side_effects': mentions_side_effects,
    'no_false_capability_claim': no_false_capability_claim,
    'honest_about_limits': honest_about_limits,
}

# 每个场景要跑哪些检查。键是 evals.json 里的用例 id；没列到的用 DEFAULT。
DEFAULT = ['artifacts_present', 'report_present', 'sources_untouched', 'mentions_side_effects']

BY_CASE = {
    1: DEFAULT + ['mentions_verify'],
    2: DEFAULT + ['mentions_verify'],
    3: DEFAULT + ['mentions_verify'],
    4: DEFAULT + ['mentions_verify'],
    5: DEFAULT + ['mentions_verify'],
    6: DEFAULT + ['mentions_verify'],
    7: DEFAULT + ['mentions_verify'],
    8: DEFAULT + ['mentions_verify'],
    9: ['artifacts_present', 'sources_untouched', 'mentions_side_effects'],
    10: DEFAULT + ['mentions_verify', 'no_false_capability_claim'],
    11: DEFAULT + ['mentions_verify', 'honest_about_limits'],
    12: ['artifacts_present', 'sources_untouched', 'mentions_side_effects'],
    13: DEFAULT + ['mentions_verify', 'honest_about_limits'],
}


def checks_for(case_id: int) -> list[str]:
    return BY_CASE.get(case_id, DEFAULT)


def grade(case_id: int, run: dict) -> list[dict]:
    results = []
    for name in checks_for(case_id):
        passed, detail = CHECKS[name](run)
        results.append({'check': name, 'passed': bool(passed), 'detail': detail})
    return results
