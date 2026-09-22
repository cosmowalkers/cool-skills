#!/usr/bin/env python3
"""前向测试：同一个任务，分别交给"带 skill"和"不带 skill"的独立 agent，机械打分。

用法（在 cool-skills 仓库根执行）：

    python3 tools/forward-test/run.py --skill image-tools --cases 1,10,11
    python3 tools/forward-test/run.py --skill image-tools --cases all --variants with,base
    python3 tools/forward-test/run.py --skill image-tools --cases 1 --runner manual

产物默认落在 /tmp/forward-test-<时间戳>/：每个用例/变体一个目录，里面有 project（夹具）、
outputs（agent 的产物）、last_message.md、run.log、TASK.md、scores.json；顶层有 report.md 和 results.json。
"""
from __future__ import annotations

import argparse
import json
import pathlib
import shutil
import subprocess
import sys
import time

TOOL_DIR = pathlib.Path(__file__).resolve().parent
REPO = TOOL_DIR.parents[1]
sys.path.insert(0, str(TOOL_DIR))

import checks  # noqa: E402
import fixtures  # noqa: E402

VARIANTS = ('with', 'base')

REPORT_ASK = (
    '把产物放到 `../outputs/`（保留子目录结构），并写一份 `../outputs/report.md`，内容包含：'
    '你对我说的话（完整原文）、你执行过的关键命令、关键数字、以及你是否改动过 project 里的源文件。'
)
BASE_GUARD = (
    '注意：本次不要使用任何 Agent Skill（包括名为 {name} 的 skill），也不要去读 {skill} 下的内容，'
    '请用你自己最顺手的方式（自己写脚本或系统 / 第三方命令行工具）完成。'
)


def build_prompt(case: dict, variant: str, skill_path: pathlib.Path) -> str:
    prompt = f'{case["prompt"]}\n\n{REPORT_ASK}'
    if variant == 'base':
        prompt += '\n' + BASE_GUARD.format(name=skill_path.name, skill=skill_path)
    return prompt


def run_codex(project: pathlib.Path, last_message: pathlib.Path, prompt: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        ['codex', 'exec', '--skip-git-repo-check', '--ephemeral',
         '-C', str(project), '-s', 'workspace-write',
         '-o', str(last_message), prompt],
        cwd=str(project), capture_output=True, text=True,
    )


def run_agent(runner: str, project: pathlib.Path, last_message: pathlib.Path, prompt: str):
    if runner == 'codex':
        return run_codex(project, last_message, prompt)
    if runner == 'claude':
        return subprocess.run(
            ['claude', '-p', prompt, '--permission-mode', 'acceptEdits'],
            cwd=str(project), capture_output=True, text=True,
        )
    if runner == 'manual':
        return None
    raise SystemExit(f'未知 runner：{runner}（可选 codex / claude / manual）')


def collect(run_dir: pathlib.Path, project: pathlib.Path) -> dict:
    outputs = run_dir / 'outputs'
    artifacts = sorted(
        str(p.relative_to(run_dir)) for p in outputs.rglob('*') if p.is_file()
    ) if outputs.exists() else []
    # 有些 agent 会把产物写进 project/outputs/
    alt = project / 'outputs'
    if alt.exists():
        artifacts += sorted(f'project/{p.relative_to(run_dir)}' for p in alt.rglob('*') if p.is_file())

    sources = [p for p in project.rglob('*') if p.is_file() and 'outputs' not in p.parts]
    base_mtime = min((p.stat().st_mtime for p in sources), default=0)
    touched = [str(p.relative_to(project)) for p in sources if p.stat().st_mtime > base_mtime + 120]

    def read(path: pathlib.Path) -> str:
        return path.read_text(encoding='utf-8', errors='replace') if path.exists() else ''

    return {
        'artifacts': artifacts,
        'sources_touched': touched,
        'last_message': read(run_dir / 'last_message.md'),
        'report': read(outputs / 'report.md') or read(alt / 'report.md'),
    }


def main() -> int:
    ap = argparse.ArgumentParser(description='skill 前向测试（带 skill vs 不带 skill）')
    ap.add_argument('--skill', required=True, help='skill 目录名或路径，例如 image-tools')
    ap.add_argument('--cases', default='1', help='用例 id，逗号分隔，或 all')
    ap.add_argument('--variants', default='with,base', help='with, base 或 with 或 base')
    ap.add_argument('--runner', default='codex', help='codex / claude / manual')
    ap.add_argument('--fixture', default='web_image_project', help='夹具类型，见 fixtures.py')
    ap.add_argument('--work', default='', help='工作目录，默认 /tmp/forward-test-<时间戳>')
    args = ap.parse_args()

    skill_path = pathlib.Path(args.skill)
    if not skill_path.is_dir():
        skill_path = REPO / args.skill
    evals_file = skill_path / 'evals' / 'evals.json'
    if not evals_file.exists():
        raise SystemExit(f'找不到评测定义：{evals_file}')
    cases = json.loads(evals_file.read_text(encoding='utf-8'))['evals']
    if args.cases != 'all':
        wanted = {int(x) for x in args.cases.split(',')}
        cases = [c for c in cases if c['id'] in wanted]
    if not cases:
        raise SystemExit('没有匹配的用例')

    variants = [v for v in args.variants.split(',') if v]
    work = pathlib.Path(args.work or f'/tmp/forward-test-{time.strftime("%Y%m%d-%H%M%S")}')
    work.mkdir(parents=True, exist_ok=True)
    print(f'工作目录：{work}')

    summary = []
    for case in cases:
        slug = f'case-{case["id"]}-' + ''.join(
            ch if ch.isalnum() or ch == '-' else '-' for ch in case['prompt'][:24]
        ).strip('-')
        for variant in variants:
            run_dir = work / slug / variant
            project = run_dir / 'project'
            (run_dir / 'outputs').mkdir(parents=True, exist_ok=True)
            fixtures.build(args.fixture, project)

            prompt = build_prompt(case, variant, skill_path)
            (run_dir / 'TASK.md').write_text(prompt + '\n', encoding='utf-8')
            last_message = run_dir / 'last_message.md'

            print(f'\n>>> case {case["id"]} / {variant} …', flush=True)
            started = time.time()
            proc = run_agent(args.runner, project, last_message, prompt)
            elapsed = round(time.time() - started, 1)
            if proc is not None:
                (run_dir / 'run.log').write_text(
                    f'# exit={proc.returncode}\n\n## stdout\n{proc.stdout}\n\n## stderr\n{proc.stderr}\n',
                    encoding='utf-8',
                )
                if not last_message.exists() and proc.stdout:
                    last_message.write_text(proc.stdout, encoding='utf-8')

            collected = collect(run_dir, project)
            scores = checks.grade(case['id'], collected)
            (run_dir / 'scores.json').write_text(
                json.dumps({'case': case['id'], 'variant': variant, 'runner': args.runner,
                            'seconds': elapsed, 'scores': scores, 'collected': collected},
                           ensure_ascii=False, indent=2) + '\n',
                encoding='utf-8',
            )
            passed = sum(1 for s in scores if s['passed'])
            print(f'    {passed}/{len(scores)} 项通过（{elapsed}s）')
            summary.append({'case': case['id'], 'variant': variant, 'passed': passed,
                            'total': len(scores), 'scores': scores, 'seconds': elapsed})

    lines = ['# 前向测试结果', '',
             f'- skill：`{skill_path.name}`',
             f'- runner：`{args.runner}`，夹具：`{args.fixture}`',
             f'- 用例：{", ".join(str(c["id"]) for c in cases)}',
             f'- 工作目录：`{work}`', '',
             '| 用例 | 变体 | 通过 | 明细 |', '| --- | --- | --- | --- |']
    for row in summary:
        detail = '；'.join(
            f'{"✅" if s["passed"] else "❌"}{s["check"]}' for s in row['scores']
        )
        lines.append(f'| {row["case"]} | {row["variant"]} | {row["passed"]}/{row["total"]} | {detail} |')
    lines += ['',
              '> 机械检查只覆盖"可自动判定"的部分（产物、报告、源文件是否被动、关键结论有没有出现）。',
              '> 结论是否站得住、提醒是否到位，需要人或 LLM grader 读各目录下的 `last_message.md` / `outputs/report.md`。',
              '']
    (work / 'report.md').write_text('\n'.join(lines), encoding='utf-8')
    (work / 'results.json').write_text(
        json.dumps({'skill': skill_path.name, 'runner': args.runner,
                    'fixture': args.fixture, 'summary': summary}, ensure_ascii=False, indent=2) + '\n',
        encoding='utf-8',
    )
    print('\n' + '\n'.join(lines[:12]))
    print(f'报告：{work / "report.md"}')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
