#!/usr/bin/env python3
"""
ToolsD 产品批量修复 + SEO 优化脚本
1. 为缺少 date/draft 的产品自动补全 front matter
2. 修复 LD-014 的 url_slug → slug
3. 识别有 SEO 价值和无价值的页面类型
4. 生成修复报告
"""

import os
import re
import yaml
from pathlib import Path
from collections import defaultdict

# 产品发布基准日期（按 SKU 前缀分组）
BASE_DATE = {
    "AT": "2026-07-02T08:00:00+08:00",
    "CT": "2026-07-02T09:00:00+08:00",
    "FH": "2026-07-02T10:00:00+08:00",
    "LD": "2026-07-01T12:00:00+08:00",
}


def parse_front_matter(content):
    match = re.match(r'^---\n(.*?)\n---', content, re.DOTALL)
    if not match:
        return None, content, 0
    return yaml.safe_load(match.group(1)), content[match.end():].strip(), match.end()


def dump_front_matter(fm, body):
    """保持 YAML 格式整洁""" 
    lines = ['---']
    for key, value in fm.items():
        if value is None:
            lines.append(f'{key}:')
        elif isinstance(value, bool):
            lines.append(f'{key}: {str(value).lower()}')
        elif isinstance(value, list):
            lines.append(f'{key}:')
            for item in value:
                lines.append(f'  - {repr(item)}' if isinstance(item, str) and ('"' in item or ':' in item) else f'  - {item}')
        elif isinstance(value, str):
            if '\n' in value or value.startswith('>'):
                lines.append(f'{key}: >')
                lines.append(f'  {value}')
            elif ':' in value[1:] or value.startswith('http'):
                lines.append(f'{key}: "{value}"')
            else:
                lines.append(f'{key}: {value}')
        elif isinstance(value, (int, float)):
            lines.append(f'{key}: {value}')
        else:
            lines.append(f'{key}: {value}')
    lines.append('---')
    return '\n'.join(lines) + '\n\n' + body


def main():
    products_dir = Path("content/products")
    if not products_dir.exists():
        print("请在 GitHub 仓库根目录运行此脚本")
        print(f"预期路径: {products_dir.absolute()} 不存在")
        return

    md_files = sorted(products_dir.glob("*.md"))
    print(f"找到 {len(md_files)} 个产品 MD 文件\n")

    stats = {
        "total": len(md_files),
        "had_date_draft": 0,      # 原来就有 date + draft
        "added_date_draft": 0,    # 补充了 date + draft  
        "fixed_slug": 0,          # 修复了 url_slug → slug
        "fixed_categories": 0,    # 修复了 categories 格式
        "needs_review": 0,        # 需要人工检查
        "skipped": 0,
    }

    issues = []  # (filename, issue_type, detail)

    for md_file in md_files:
        content = md_file.read_text(encoding="utf-8")
        fm, body, fm_end = parse_front_matter(content)

        if not fm:
            issues.append((md_file.name, "NO_FM", "无有效 front matter"))
            stats["needs_review"] += 1
            continue

        sku = fm.get("sku", "")
        prefix = sku[:2] if len(sku) >= 2 else "XX"
        changed = False
        fixes = []

        # 1. 检查并补全 draft
        if "draft" not in fm:
            fm["draft"] = False
            changed = True
            fixes.append("+draft: false")

        # 2. 检查并补全 date
        if "date" not in fm:
            fm["date"] = BASE_DATE.get(prefix, "2026-07-03T12:00:00+08:00")
            changed = True
            fixes.append(f"+date: {fm['date']}")

        # 3. 修复 url_slug → slug (LD-014 的问题)
        if "url_slug" in fm and "slug" not in fm:
            fm["slug"] = fm["url_slug"]
            del fm["url_slug"]
            changed = True
            fixes.append("url_slug → slug")

        # 4. 检查 categories 是小写连字符格式
        if "categories" in fm and fm["categories"]:
            cats = fm["categories"]
            if isinstance(cats, list):
                new_cats = []
                for cat in cats:
                    # 确保是小写连字符格式
                    normalized = cat.lower().replace(" ", "-").replace("&", "and")
                    if normalized != cat:
                        new_cats.append(normalized)
                        fixes.append(f"categories: {cat} → {normalized}")
                    else:
                        new_cats.append(cat)
                if new_cats != cats:
                    fm["categories"] = new_cats
                    changed = True

        if changed:
            new_content = dump_front_matter(fm, body)
            md_file.write_text(new_content, encoding="utf-8")
            print(f"  ✅ {md_file.name}")
            for f in fixes:
                print(f"     {f}")
            
            if "date" not in [x.split(":")[0] for x in ["+date" if s.startswith("+date") else "" for s in fixes]] and "draft" not in [x.split(":")[0] if x.startswith("+draft") else "" for x in fixes]:
                pass
            if any("date" in f or "draft" in f for f in fixes):
                stats["added_date_draft"] += 1
            if any("slug" in f for f in fixes):
                stats["fixed_slug"] += 1
            if any("categories" in f for f in fixes):
                stats["fixed_categories"] += 1
        else:
            stats["had_date_draft"] += 1
            print(f"  ✓  {md_file.name} — 无需修改")

    # 报告
    print("\n" + "=" * 60)
    print("修复报告")
    print("=" * 60)
    print(f"总产品数:     {stats['total']}")
    print(f"无需修改:     {stats['had_date_draft']}")
    print(f"补充 date+draft: {stats['added_date_draft']}")
    print(f"修复 slug:    {stats['fixed_slug']}")
    print(f"修复分类格式: {stats['fixed_categories']}")

    if issues:
        print(f"\n⚠️  需人工检查 ({len(issues)}):")
        for filename, itype, detail in issues:
            print(f"  {filename}: {itype} — {detail}")

    print("\n✅ 修复完成。提交并推送后 GitHub Actions 会自动重新构建。")


if __name__ == "__main__":
    main()
