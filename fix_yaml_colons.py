#!/usr/bin/env python3
"""
修复 fix_products_seo.py 引入的 YAML 冒号转义问题
问题：值中包含冒号（如 "Color box"、"$2.00"）但未加引号，导致 Hugo 构建失败
"""

import os
import re
import yaml
from pathlib import Path


def main():
    products_dir = Path("content/products")
    if not products_dir.exists():
        print("请在仓库根目录运行此脚本")
        return

    md_files = sorted(products_dir.glob("*.md"))
    fixed = 0
    failed = 0

    for md_file in md_files:
        try:
            content = md_file.read_text(encoding="utf-8")
            match = re.match(r'^---\n(.*?)\n---', content, re.DOTALL)
            if not match:
                continue

            yaml_str = match.group(1)
            body = content[match.end():].strip()

            # 尝试解析 YAML，如果失败就说明有问题需要修
            fm = None
            error_msg = None
            try:
                fm = yaml.safe_load(yaml_str)
            except Exception as e:
                error_msg = str(e)

            if fm is None or error_msg:
                # 尝试用更宽松的方式解析，或直接用 pyyaml 的 safe_load 重新序列化
                # 策略：用 pyaml 重新 dump，确保格式正确
                print(f"⚠️  {md_file.name}: {error_msg}")
                failed += 1
                continue

            # 重新序列化确保格式安全
            lines = ['---']
            for key, value in fm.items():
                if value is None:
                    lines.append(f'{key}:')
                elif isinstance(value, bool):
                    lines.append(f'{key}: {str(value).lower()}')
                elif isinstance(value, list):
                    lines.append(f'{key}:')
                    for item in value:
                        if isinstance(item, str) and (':' in item or '"' in item or '#' in item):
                            lines.append(f'  - "{item}"')
                        else:
                            lines.append(f'  - {item}')
                elif isinstance(value, str):
                    # 关键修复：任何包含特殊字符的值都必须加引号
                    needs_quote = (
                        '\n' in value
                        or ':' in value[1:] if len(value) > 1 else False  # 跳过首字符的冒号（key: value）
                        or value.startswith('http')
                        or value.startswith('> ')
                        or '"' in value
                        or '#' in value
                        or '|' in value
                    )
                    if needs_quote:
                        if '\n' in value or value.startswith('>'):
                            lines.append(f'{key}: >')
                            for vline in value.split('\n'):
                                lines.append(f'  {vline}')
                        else:
                            escaped = value.replace('"', '\\"')
                            lines.append(f'{key}: "{escaped}"')
                    else:
                        lines.append(f'{key}: {value}')
                elif isinstance(value, (int, float)):
                    lines.append(f'{key}: {value}')
                else:
                    lines.append(f'{key}: {value}')

            lines.append('---')
            new_content = '\n'.join(lines) + '\n\n' + body

            # 验证新内容可以解析
            try:
                test_fm = yaml.safe_load('\n'.join(lines[1:-1]))
            except Exception as e:
                print(f"❌ {md_file.name}: 重写后仍无法解析: {e}")
                failed += 1
                continue

            md_file.write_text(new_content, encoding="utf-8")
            fixed += 1
            print(f"✅ {md_file.name}")

        except Exception as e:
            print(f"❌ {md_file.name}: 处理异常: {e}")
            failed += 1

    print(f"\n{'='*50}")
    print(f"修复完成: ✅{fixed} 个文件已重写, ❌{failed} 个文件失败")
    print(f"\n提交并推送后 GitHub Actions 会自动重新构建。")


if __name__ == "__main__":
    main()
