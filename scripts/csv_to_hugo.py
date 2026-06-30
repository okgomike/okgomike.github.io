#!/usr/bin/env python3
"""
CSV to Hugo Markdown converter for second-branch-hardware.
Reads a product CSV and generates Hugo-compatible Markdown files.
Auto-creates categories based on CSV category columns.

Usage:
    python scripts/csv_to_hugo.py products.csv content/products/

Expected CSV columns:
    title, slug, summary, description, category_level1, category_level2,
    moq, price_range, material, standard, grade, size_range, surface,
    certification, packing, sample, customization, mixed_order,
    image, gallery, specifications, faq, weight, carton_qty, carton_size,
    gw_nw, internal_note
"""

import csv
import sys
import os
import re
import unicodedata
from pathlib import Path
from datetime import datetime


def slugify(text):
    """Convert text to URL-friendly slug."""
    if not text:
        return ""
    text = str(text).strip().lower()
    text = unicodedata.normalize('NFKD', text).encode('ascii', 'ignore').decode('ascii')
    text = re.sub(r'[^\w\s-]', '', text)
    text = re.sub(r'[-\s]+', '-', text)
    return text.strip('-')


def ensure_dir(path):
    """Create directory if it doesn't exist."""
    Path(path).mkdir(parents=True, exist_ok=True)


def generate_frontmatter(row):
    """Generate YAML frontmatter from CSV row."""
    fm = []
    fm.append("---")

    title = row.get('title', '').strip()
    fm.append(f'title: "{title}"')

    slug = row.get('slug', '').strip()
    if not slug:
        slug = slugify(title)
    fm.append(f'slug: "{slug}"')

    date_str = datetime.now().strftime('%Y-%m-%dT%H:%M:%S+08:00')
    fm.append(f'date: {date_str}')
    fm.append('draft: false')

    summary = row.get('summary', '').strip()
    if summary:
        fm.append(f'summary: "{summary}"')

    description = row.get('description', '').strip()
    if description:
        fm.append(f'description: "{description}"')

    image = row.get('image', '').strip()
    if image:
        fm.append(f'image: "{image}"')

    gallery = row.get('gallery', '').strip()
    if gallery:
        items = [x.strip() for x in gallery.split(',') if x.strip()]
        fm.append('gallery:')
        for item in items:
            fm.append(f'  - "{item}"')

    cat1 = row.get('category_level1', '').strip()
    cat2 = row.get('category_level2', '').strip()
    categories = []
    if cat1:
        categories.append(slugify(cat1))
    if cat2:
        categories.append(slugify(cat2))
    if categories:
        fm.append('categories:')
        for cat in categories:
            fm.append(f'  - {cat}')

    tags = row.get('tags', '').strip()
    if tags:
        items = [slugify(x) for x in tags.split(',') if x.strip()]
        fm.append('tags:')
        for item in items:
            fm.append(f'  - {item}')

    for field in ['moq', 'price_range', 'material', 'standard', 'grade',
                  'size_range', 'surface', 'certification', 'packing',
                  'sample', 'customization', 'mixed_order', 'weight',
                  'carton_qty', 'carton_size', 'gw_nw']:
        val = row.get(field, '').strip()
        if val:
            fm.append(f'{field}: "{val}"')

    internal = row.get('internal_note', '').strip()
    if internal:
        fm.append(f'internal_note: "{internal}"')

    fm.append("---")
    return '\n'.join(fm)


def generate_content(row):
    """Generate Markdown content body from CSV row."""
    parts = []

    desc = row.get('description', '').strip()
    if desc:
        parts.append(desc)
        parts.append("")

    specs = row.get('specifications', '').strip()
    if specs:
        parts.append("## Specifications")
        parts.append("")
        parts.append(specs)
        parts.append("")

    faq = row.get('faq', '').strip()
    if faq:
        parts.append("## FAQ")
        parts.append("")
        parts.append(faq)
        parts.append("")

    return '\n'.join(parts)


def generate_category_pages(csv_path, output_base):
    """Auto-generate category index pages from CSV data."""
    categories = {}
    with open(csv_path, 'r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        for row in reader:
            cat1 = row.get('category_level1', '').strip()
            cat2 = row.get('category_level2', '').strip()
            if cat1:
                slug1 = slugify(cat1)
                if slug1 not in categories:
                    categories[slug1] = {'name': cat1, 'children': {}}
                if cat2:
                    slug2 = slugify(cat2)
                    categories[slug1]['children'][slug2] = cat2

    for slug1, data in categories.items():
        cat_dir = os.path.join(output_base, '..', 'categories', slug1)
        ensure_dir(cat_dir)
        index_path = os.path.join(cat_dir, '_index.md')
        if not os.path.exists(index_path):
            with open(index_path, 'w', encoding='utf-8') as f:
                f.write(f"---\ntitle: \"{data['name']}\"\n")
                f.write(f"description: \"Browse wholesale {data['name'].lower()} from Yiwu China.\"\n")
                f.write("---\n")

        for slug2, name2 in data['children'].items():
            sub_dir = os.path.join(cat_dir, slug2)
            ensure_dir(sub_dir)
            sub_index_path = os.path.join(sub_dir, '_index.md')
            if not os.path.exists(sub_index_path):
                with open(sub_index_path, 'w', encoding='utf-8') as f:
                    f.write(f"---\ntitle: \"{name2}\"\n")
                    f.write(f"description: \"Wholesale {name2.lower()} from Yiwu China.\"\n")
                    f.write("---\n")

    print(f"[INFO] Auto-created {len(categories)} category pages.")


def main():
    if len(sys.argv) < 3:
        print("Usage: python csv_to_hugo.py <input.csv> <output_dir>")
        sys.exit(1)

    csv_path = sys.argv[1]
    output_dir = sys.argv[2]

    if not os.path.exists(csv_path):
        print(f"Error: CSV file not found: {csv_path}")
        sys.exit(1)

    ensure_dir(output_dir)

    count = 0
    with open(csv_path, 'r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        for row in reader:
            title = row.get('title', '').strip()
            if not title:
                continue

            slug = row.get('slug', '').strip()
            if not slug:
                slug = slugify(title)

            filename = f"{slug}.md"
            filepath = os.path.join(output_dir, filename)

            frontmatter = generate_frontmatter(row)
            content = generate_content(row)

            with open(filepath, 'w', encoding='utf-8') as out:
                out.write(frontmatter)
                out.write('\n\n')
                out.write(content)

            count += 1

    print(f"[OK] Generated {count} product Markdown files in {output_dir}")

    generate_category_pages(csv_path, output_dir)
    print("[OK] Done.")


if __name__ == '__main__':
    main()
