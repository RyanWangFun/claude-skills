#!/usr/bin/env python3
"""
检测 Context 目录中最近修改的 markdown 文件

混合检测策略：
1. 基础检测：始终使用时间戳扫描所有修改的文件（保证不漏掉）
2. Git增强（可选）：附加每个文件在指定时间段内的Git commits和diff信息

用法:
    # 基础模式：仅检测文件修改（最近24小时）
    python3 detect_changes.py --hours 24 --context-path /path/to/context

    # Git增强模式：检测文件修改 + Git commits详情（推荐用于日记生成）
    python3 detect_changes.py --use-git --date 2025-12-16 --context-path /path/to/context

    # 检测指定日期（当天 00:00 到 23:59）
    python3 detect_changes.py --date 2024-12-03 --context-path /path/to/context

    # 检测日期范围
    python3 detect_changes.py --start-date 2024-12-01 --end-date 2024-12-03 --context-path /path/to/context

Git增强模式的优势：
- 不仅知道"哪些文件被修改"，还能看到"具体改了什么"
- 显示commit messages，了解修改意图
- 即使文件已被commit也能检测到（不会漏掉）
"""

import os
import argparse
import subprocess
from datetime import datetime, timedelta
from pathlib import Path
import json


def parse_date(date_str: str) -> datetime:
    """
    解析日期字符串为 datetime 对象

    支持格式：
    - YYYY-MM-DD (如 2024-12-03)
    - YYYY/MM/DD (如 2024/12/03)
    """
    for fmt in ['%Y-%m-%d', '%Y/%m/%d']:
        try:
            return datetime.strptime(date_str, fmt)
        except ValueError:
            continue
    raise ValueError(f"无法解析日期: {date_str}。请使用格式: YYYY-MM-DD 或 YYYY/MM/DD")


def find_git_repo(file_path: Path) -> Path | None:
    """
    查找文件所属的Git仓库根目录

    Args:
        file_path: 文件路径

    Returns:
        Git仓库根目录路径，如果不在Git仓库中则返回None
    """
    current = file_path if file_path.is_dir() else file_path.parent

    # 向上查找.git目录
    while current != current.parent:
        git_dir = current / '.git'
        if git_dir.exists():
            return current
        current = current.parent

    return None


def get_file_git_diff_for_date_range(repo_path: Path, file_path: Path, start_time: datetime, end_time: datetime) -> dict | None:
    """
    获取某个文件在指定日期范围内的Git变更详情

    策略：
    1. 查找该时间段内涉及该文件的所有commits
    2. 获取这些commits的diff内容

    Args:
        repo_path: Git仓库根目录
        file_path: 文件的绝对路径
        start_time: 开始时间
        end_time: 结束时间

    Returns:
        包含Git diff信息的字典，如果无变更或获取失败则返回None
    """
    try:
        os.chdir(repo_path)

        # 计算文件相对于repo的路径
        relative_file = file_path.relative_to(repo_path)

        # 格式化时间为Git可接受的格式
        since_str = start_time.strftime('%Y-%m-%d %H:%M:%S')
        until_str = end_time.strftime('%Y-%m-%d %H:%M:%S')

        # 查找该时间段内涉及该文件的commits
        log_result = subprocess.run(
            ['git', 'log',
             '--since', since_str,
             '--until', until_str,
             '--format=%H|%ai|%s',  # commit hash | author date | subject
             '--', str(relative_file)],
            capture_output=True,
            text=True
        )

        if log_result.returncode != 0 or not log_result.stdout.strip():
            # 该时间段内没有commits涉及这个文件
            return None

        commits = []
        for line in log_result.stdout.strip().split('\n'):
            if not line:
                continue
            parts = line.split('|', 2)
            if len(parts) == 3:
                commit_hash, commit_date, commit_msg = parts
                commits.append({
                    'hash': commit_hash,
                    'date': commit_date,
                    'message': commit_msg
                })

        if not commits:
            return None

        # 获取这些commits的diff摘要
        diff_summary = []
        for commit in commits:
            # 获取该commit中这个文件的变更统计
            stat_result = subprocess.run(
                ['git', 'show', '--stat', '--format=', commit['hash'], '--', str(relative_file)],
                capture_output=True,
                text=True
            )

            if stat_result.returncode == 0 and stat_result.stdout.strip():
                diff_summary.append({
                    'commit': commit['hash'][:7],  # 短hash
                    'message': commit['message'],
                    'date': commit['date'],
                    'stats': stat_result.stdout.strip()
                })

        # 获取该时间段内该文件的完整diff（从最早的commit到最新）
        if len(commits) > 0:
            oldest_commit = commits[-1]['hash']
            newest_commit = commits[0]['hash']

            # 获取diff
            diff_result = subprocess.run(
                ['git', 'diff', f'{oldest_commit}^', newest_commit, '--', str(relative_file)],
                capture_output=True,
                text=True
            )

            full_diff = diff_result.stdout if diff_result.returncode == 0 else None
        else:
            full_diff = None

        return {
            'repo_name': repo_path.name,
            'repo_path': str(repo_path),
            'commits': commits,
            'diff_summary': diff_summary,
            'full_diff': full_diff,
            'commit_count': len(commits)
        }

    except Exception as e:
        print(f"Warning: Could not get git diff for {file_path}: {e}")
        return None


def get_git_changes(repo_path: Path, since: str = 'HEAD') -> dict | None:
    """
    获取Git仓库的变更信息（未commit的修改）

    Args:
        repo_path: Git仓库根目录
        since: 对比基准，默认'HEAD'（工作目录 vs 最后一次commit）

    Returns:
        包含Git变更信息的字典，如果获取失败则返回None
    """
    try:
        os.chdir(repo_path)

        # 检查是否有commit历史
        result = subprocess.run(
            ['git', 'rev-parse', 'HEAD'],
            capture_output=True,
            text=True
        )

        if result.returncode != 0:
            # 没有commit历史，返回None
            return None

        # 获取变更的文件列表（包括staged和unstaged）
        result = subprocess.run(
            ['git', 'diff', '--name-status', 'HEAD'],
            capture_output=True,
            text=True
        )

        if result.returncode != 0:
            return None

        changes = []
        for line in result.stdout.strip().split('\n'):
            if not line:
                continue
            parts = line.split('\t', 1)
            if len(parts) == 2:
                status, filepath = parts
                # 只关注.md文件
                if filepath.endswith('.md'):
                    changes.append({
                        'status': status,  # M=Modified, A=Added, D=Deleted
                        'file': filepath
                    })

        if not changes:
            return None

        # 获取统计信息
        stats_result = subprocess.run(
            ['git', 'diff', '--stat', 'HEAD', '--', '*.md'],
            capture_output=True,
            text=True
        )

        return {
            'repo_path': str(repo_path),
            'changes': changes,
            'stats': stats_result.stdout if stats_result.returncode == 0 else '',
            'has_uncommitted': len(changes) > 0
        }

    except Exception as e:
        print(f"Warning: Could not get git changes for {repo_path}: {e}")
        return None


def get_modified_files(directory: str, start_time: datetime = None, end_time: datetime = None, use_git: bool = False, context_path: Path = None) -> list[dict]:
    """
    获取指定目录下在时间范围内修改的 markdown 文件

    混合检测策略：
    1. 始终使用时间戳扫描所有修改的文件（保证不漏掉）
    2. 对于在Git仓库中的文件，附加该时间段内的Git diff信息

    Args:
        directory: 要扫描的目录路径
        start_time: 开始时间（包含）
        end_time: 结束时间（包含）
        use_git: 是否启用Git diff增强（附加具体修改内容）
        context_path: Context根目录路径（用于计算相对路径）

    Returns:
        包含文件信息的字典列表，每个字典包含:
        - path: 文件路径
        - modified_time: 修改时间（ISO 格式）
        - relative_path: 相对于 context 目录的路径
        - git_info: Git变更信息（如果use_git=True且文件在Git仓库中）
    """
    modified_files = []

    # 排除的目录（node_modules, .git 等）
    exclude_dirs = {'node_modules', '.git', '.obsidian', 'dist', 'build', '__pycache__'}

    directory_path = Path(directory)

    # 第一步：时间戳扫描所有.md文件
    for md_file in directory_path.rglob('*.md'):
        # 检查是否在排除目录中
        if any(excluded in md_file.parts for excluded in exclude_dirs):
            continue

        try:
            modified_timestamp = md_file.stat().st_mtime
            modified_datetime = datetime.fromtimestamp(modified_timestamp)

            # 检查是否在时间范围内
            if start_time and modified_datetime < start_time:
                continue
            if end_time and modified_datetime > end_time:
                continue

            relative_path = str(md_file.relative_to(context_path)) if context_path else str(md_file)

            file_info = {
                'path': str(md_file),
                'modified_time': modified_datetime.isoformat(),
                'relative_path': relative_path
            }

            # 第二步：如果启用Git增强，获取该文件的Git diff信息
            if use_git:
                git_repo = find_git_repo(md_file)
                if git_repo:
                    # 文件在Git仓库中，获取指定日期范围的diff
                    git_diff_info = get_file_git_diff_for_date_range(
                        git_repo, md_file, start_time, end_time
                    )

                    if git_diff_info:
                        # 有Git commits，附加详细信息
                        file_info['git_info'] = {
                            'in_git_repo': True,
                            'repo_name': git_diff_info['repo_name'],
                            'repo_path': git_diff_info['repo_path'],
                            'commits': git_diff_info['commits'],
                            'commit_count': git_diff_info['commit_count'],
                            'diff_summary': git_diff_info['diff_summary']
                        }
                    else:
                        # 在Git仓库中但该时间段无commits（可能只是文件时间戳更新）
                        file_info['git_info'] = {
                            'in_git_repo': True,
                            'repo_name': git_repo.name,
                            'repo_path': str(git_repo),
                            'commits': [],
                            'commit_count': 0,
                            'note': '文件在Git仓库中，但指定时间段内无相关commits'
                        }
                else:
                    # 不在Git仓库中
                    file_info['git_info'] = {
                        'in_git_repo': False
                    }

            modified_files.append(file_info)

        except (OSError, ValueError) as e:
            print(f"Warning: Could not process {md_file}: {e}")
            continue

    # 按修改时间排序（最新的在前）
    modified_files.sort(key=lambda x: x['modified_time'], reverse=True)

    return modified_files


def main():
    parser = argparse.ArgumentParser(
        description='检测 Context 目录中最近修改的 markdown 文件'
    )

    # 时间范围参数
    time_group = parser.add_argument_group('时间范围选项（三选一）')
    time_group.add_argument(
        '--hours',
        type=int,
        help='检测最近 N 小时内的变动（默认: 24）'
    )
    time_group.add_argument(
        '--date',
        type=str,
        help='检测指定日期的变动（格式: YYYY-MM-DD，如 2024-12-03）'
    )
    time_group.add_argument(
        '--start-date',
        type=str,
        help='开始日期（格式: YYYY-MM-DD）。需要配合 --end-date 使用'
    )
    time_group.add_argument(
        '--end-date',
        type=str,
        help='结束日期（格式: YYYY-MM-DD）。需要配合 --start-date 使用'
    )

    # 其他参数
    parser.add_argument(
        '--context-path',
        type=str,
        default='/path/to/context',
        help='Context 目录的路径'
    )
    parser.add_argument(
        '--projects-only',
        action='store_true',
        help='仅检测 01Projects 目录'
    )
    parser.add_argument(
        '--areas-only',
        action='store_true',
        help='仅检测 02Areas 目录'
    )
    parser.add_argument(
        '--use-git',
        action='store_true',
        help='使用Git diff检测变更（对有Git仓库的项目）'
    )
    parser.add_argument(
        '--output',
        choices=['json', 'text'],
        default='text',
        help='输出格式（默认: text）'
    )

    args = parser.parse_args()

    # 解析时间范围
    start_time = None
    end_time = None
    time_desc = ""

    try:
        if args.date:
            # 指定日期：当天 00:00 到 23:59
            target_date = parse_date(args.date)
            start_time = target_date.replace(hour=0, minute=0, second=0, microsecond=0)
            end_time = target_date.replace(hour=23, minute=59, second=59, microsecond=999999)
            time_desc = f"{args.date} (全天)"
        elif args.start_date and args.end_date:
            # 日期范围
            start_time = parse_date(args.start_date).replace(hour=0, minute=0, second=0, microsecond=0)
            end_time = parse_date(args.end_date).replace(hour=23, minute=59, second=59, microsecond=999999)
            time_desc = f"{args.start_date} 至 {args.end_date}"
        elif args.start_date or args.end_date:
            print("错误: --start-date 和 --end-date 必须同时使用")
            return 1
        else:
            # 默认使用 hours（向后兼容）
            hours = args.hours if args.hours else 24
            start_time = datetime.now() - timedelta(hours=hours)
            end_time = datetime.now()
            time_desc = f"最近 {hours} 小时"
    except ValueError as e:
        print(f"错误: {e}")
        return 1

    context_path = Path(args.context_path)

    if not context_path.exists():
        print(f"错误: Context 目录不存在: {context_path}")
        return 1

    results = {
        'projects': [],
        'areas': [],
        'time_range': {
            'start': start_time.isoformat(),
            'end': end_time.isoformat(),
            'description': time_desc
        },
        'use_git': args.use_git
    }

    # 检测 01Projects
    if not args.areas_only:
        projects_path = context_path / '01Projects'
        if projects_path.exists():
            results['projects'] = get_modified_files(
                str(projects_path),
                start_time,
                end_time,
                use_git=args.use_git,
                context_path=context_path
            )

    # 检测 02Areas
    if not args.projects_only:
        areas_path = context_path / '02Areas'
        if areas_path.exists():
            # 排除日记目录（因为是输出，不是输入）
            all_areas = get_modified_files(
                str(areas_path),
                start_time,
                end_time,
                use_git=args.use_git,
                context_path=context_path
            )
            results['areas'] = [
                f for f in all_areas
                if '/日记/' not in f['path']
            ]

    # 输出结果
    if args.output == 'json':
        print(json.dumps(results, indent=2, ensure_ascii=False))
    else:
        mode_indicator = " (Git模式)" if args.use_git else " (时间戳模式)"
        print(f"\n📊 检测时间范围: {time_desc}{mode_indicator}\n")

        if results['projects']:
            print(f"📁 01Projects 中的变动 ({len(results['projects'])} 个文件):")
            print("-" * 60)
            for file in results['projects']:
                print(f"  • {file['relative_path']}")
                print(f"    修改时间: {file['modified_time']}")

                if 'git_info' in file:
                    git_info = file['git_info']
                    if git_info.get('in_git_repo'):
                        print(f"    Git仓库: {git_info.get('repo_name', 'Unknown')}")

                        # 显示commits信息
                        commit_count = git_info.get('commit_count', 0)
                        if commit_count > 0:
                            print(f"    Commits: {commit_count} 个提交")
                            commits = git_info.get('commits', [])
                            for commit in commits[:3]:  # 最多显示3个
                                print(f"      - [{commit['hash'][:7]}] {commit['message']}")
                            if len(commits) > 3:
                                print(f"      - ...还有 {len(commits) - 3} 个提交")
                        else:
                            if 'note' in git_info:
                                print(f"    注: {git_info['note']}")
            print()
        else:
            print("📁 01Projects: 无变动\n")

        if results['areas']:
            print(f"📁 02Areas 中的变动 ({len(results['areas'])} 个文件):")
            print("-" * 60)
            for file in results['areas']:
                print(f"  • {file['relative_path']}")
                print(f"    修改时间: {file['modified_time']}")

                if 'git_info' in file:
                    git_info = file['git_info']
                    if git_info.get('in_git_repo'):
                        print(f"    Git仓库: {git_info.get('repo_name', 'Unknown')}")

                        # 显示commits信息
                        commit_count = git_info.get('commit_count', 0)
                        if commit_count > 0:
                            print(f"    Commits: {commit_count} 个提交")
                            commits = git_info.get('commits', [])
                            for commit in commits[:3]:  # 最多显示3个
                                print(f"      - [{commit['hash'][:7]}] {commit['message']}")
                            if len(commits) > 3:
                                print(f"      - ...还有 {len(commits) - 3} 个提交")
                        else:
                            if 'note' in git_info:
                                print(f"    注: {git_info['note']}")
            print()
        else:
            print("📁 02Areas: 无变动\n")

    return 0


if __name__ == '__main__':
    exit(main())
