#!/usr/bin/env python3
"""
批量修复产品 MD 文件的 categories 字段
只修改类目相关字段（categories, category_1, category_2），不改动其他任何内容。

使用方法：
  python fix_categories.py

前提：在 Hugo 网站根目录（okgomike.github.io/）下运行
"""

import os
import sys

# ============================================================
# 产品分类映射表
# 格式：文件名 -> (二级slug, 三级slug)
# ============================================================

PRODUCT_CATEGORIES = {
    # ===== AT 系列 (automotive-repair-tools) =====
    'AT-001-12pcs-combination-wrench-set.md':                    ('automotive-repair-tools', 'socket-wrench-sets'),
    'AT-002-150pcs-comprehensive-socket-wrench-tool-set.md':     ('automotive-repair-tools', 'socket-wrench-sets'),
    'AT-003-40pcs-1-2-drive-socket-set.md':                      ('automotive-repair-tools', 'socket-wrench-sets'),
    'AT-004-46pcs-socket-wrench-set-ratchet.md':                  ('automotive-repair-tools', 'socket-wrench-sets'),
    'AT-005-combination-wrench-set-with-roll-up-pouch.md':        ('automotive-repair-tools', 'socket-wrench-sets'),
    'AT-006-t-handle-sliding-socket-wrench-set.md':               ('automotive-repair-tools', 'socket-wrench-sets'),
    'AT-007-precision-screwdriver-bit-set.md':                    ('automotive-repair-tools', 'screwdrivers-pliers'),
    'AT-008-digital-tire-tread-depth-gauge.md':                   ('automotive-repair-tools', 'diagnostic-tools'),
    'AT-009-spark-plug-socket-wrench-set.md':                     ('automotive-repair-tools', 'socket-wrench-sets'),
    'AT-010-hex-key-allen-wrench-set.md':                         ('automotive-repair-tools', 'screwdrivers-pliers'),

    # ===== CT 系列 =====
    # 园林工具 -> construction-tools / cutting-tools
    'CT-001-sk5-steel-bypass-pruning-shears.md':                  ('construction-tools', 'cutting-tools'),
    'CT-002-carbon-steel-anvil-pruning-shears.md':                ('construction-tools', 'cutting-tools'),
    'CT-003-professional-garden-scissors-3pcs-set.md':            ('construction-tools', 'cutting-tools'),
    'CT-004-heavy-duty-ratchet-pruning-shears.md':                ('construction-tools', 'cutting-tools'),
    'CT-005-garden-trowel-3pcs-set-wooden-handle.md':             ('construction-tools', 'cutting-tools'),
    'CT-006-garden-leaf-rake-adjustable-handle.md':               ('construction-tools', 'cutting-tools'),
    'CT-007-garden-fork-hoe-2pcs-set.md':                         ('construction-tools', 'cutting-tools'),
    'CT-008-6pcs-garden-tool-set-wooden-handle-gloves.md':        ('construction-tools', 'cutting-tools'),
    'CT-009-heavy-duty-bypass-lopper-with-fiberglass-handles.md': ('construction-tools', 'cutting-tools'),
    'CT-010-curved-blade-pruning-saw-with-safety-sheath.md':      ('construction-tools', 'cutting-tools'),
    'CT-011-carbon-steel-garden-spade-with-d-grip-handle.md':     ('construction-tools', 'cutting-tools'),
    'CT-012-professional-wavy-blade-hedge-shears-with-aluminum-handles.md': ('construction-tools', 'cutting-tools'),
    # 磨料/砂轮/打磨 -> construction-tools / welding-tools
    'CT-013-aluminum-oxide-flap-disc-assortment.md':              ('construction-tools', 'welding-tools'),
    'CT-014-nylon-abrasive-flap-wheel-brush-set.md':               ('construction-tools', 'welding-tools'),
    'CT-015-wool-felt-sponge-polishing-pad-kit.md':                ('construction-tools', 'welding-tools'),
    'CT-016-wire-wheel-brush-cup-brush-assortment.md':             ('construction-tools', 'welding-tools'),
    'CT-017-resin-bond-grinding-wheel-cutting-disc-set.md':       ('construction-tools', 'welding-tools'),
    'CT-018-tungsten-carbide-rotary-burr-mounted-point-set.md':    ('construction-tools', 'welding-tools'),
    # 扳手/套筒 -> automotive-repair-tools / socket-wrench-sets
    'CT-019-ratchet-wrench-socket-tool-set.md':                    ('automotive-repair-tools', 'socket-wrench-sets'),
    # 切割工具 -> construction-tools / cutting-tools
    'CT-020-pvc-pipe-cutter-tubing-cutter-set.md':                ('construction-tools', 'cutting-tools'),
    'CT-021-locking-pliers-adjustable-clamp-set.md':               ('construction-tools', 'cutting-tools'),
    'CT-022-tin-snips-aviation-snips-metal-shears-set.md':         ('construction-tools', 'cutting-tools'),
    'CT-023-multi-purpose-pliers-diagonal-pliers-long-nose-pliers-set.md': ('construction-tools', 'cutting-tools'),
    # 泥瓦工具 -> construction-tools / concrete-tools
    'CT-024-putty-knife-trowel-scraper-masonry-tool-set.md':       ('construction-tools', 'concrete-tools'),
    # 钉枪 -> construction-tools / hammers-mallets
    'CT-025-heavy-duty-staple-gun-tacker-assortment.md':           ('construction-tools', 'hammers-mallets'),
    # 切割工具
    'CT-026-utility-knife-box-cutter-replacement-blade-set.md':    ('construction-tools', 'cutting-tools'),
    'CT-027-glass-cutter-tile-cutter-folding-knife-set.md':        ('construction-tools', 'cutting-tools'),
    # 扳手 -> automotive-repair-tools
    'CT-028-socket-wrench-torque-wrench-tool-set.md':              ('automotive-repair-tools', 'socket-wrench-sets'),
    # 钻头 -> construction-tools / power-drills
    'CT-029-diamond-hole-saw-core-drill-bit-set.md':               ('construction-tools', 'power-drills'),
    # 套筒 -> automotive-repair-tools
    'CT-030-impact-socket-set-with-blow-mold-case.md':              ('automotive-repair-tools', 'socket-wrench-sets'),
    # 管钳 -> construction-tools / hammers-mallets
    'CT-031-heavy-duty-cast-iron-pipe-wrench-assortment.md':        ('construction-tools', 'hammers-mallets'),
    # 内六角 -> automotive-repair-tools / screwdrivers-pliers
    'CT-032-s2-steel-ball-end-hex-key-allen-wrench-set.md':         ('automotive-repair-tools', 'screwdrivers-pliers'),
    # 螺丝刀 -> automotive-repair-tools / screwdrivers-pliers
    'CT-033-chrome-vanadium-screwdriver-set-assortment.md':         ('automotive-repair-tools', 'screwdrivers-pliers'),
    # 钳子+锡剪 -> construction-tools / cutting-tools
    'CT-034-locking-plier-vice-grip-aviation-tin-snips-set.md':    ('construction-tools', 'cutting-tools'),
    # 钢锯 -> construction-tools / cutting-tools
    'CT-035-12-inch-professional-hacksaw-frame-with-blades.md':    ('construction-tools', 'cutting-tools'),
    # 水平尺 -> construction-tools / measuring-tools
    'CT-036-box-beam-spirit-level-with-magnified-vials.md':        ('construction-tools', 'measuring-tools'),
    # 气动钉枪 -> construction-tools / concrete-tools
    'CT-037-pneumatic-coil-nail-gun-framing-nailer.md':            ('construction-tools', 'concrete-tools'),
    'CT-038-pneumatic-brad-nailer-staple-gun-combo.md':            ('construction-tools', 'concrete-tools'),
    # 铁丝网 -> construction-tools / concrete-tools
    'CT-039-galvanized-welded-wire-mesh-roll.md':                  ('construction-tools', 'concrete-tools'),
    'CT-040-hexagonal-chicken-wire-mesh-roll.md':                  ('construction-tools', 'concrete-tools'),
    # 电钻 -> construction-tools / power-drills
    'CT-041-cordless-drill-driver-impact-wrench-combo-kit.md':     ('construction-tools', 'power-drills'),
    # 激光水平仪 -> construction-tools / measuring-tools
    'CT-042-self-leveling-laser-level-360-degree-cross-line.md':    ('construction-tools', 'measuring-tools'),
    # 电锯 -> construction-tools / cutting-tools
    'CT-043-mini-electric-chainsaw-portable-cordless-chain-saw.md': ('construction-tools', 'cutting-tools'),
    # 角磨机 -> construction-tools / welding-tools
    'CT-044-angle-grinder-electric-cutting-grinding-machine.md':   ('construction-tools', 'welding-tools'),
    # 电动螺丝刀 -> construction-tools / power-drills
    'CT-045-cordless-electric-screwdriver-set-rechargeable.md':    ('construction-tools', 'power-drills'),
    # 钻头套装 -> construction-tools / power-drills
    'CT-046-hss-drill-bit-set-masonry-wood-metal.md':              ('construction-tools', 'power-drills'),

    # ===== FH 系列 (fasteners-hardware) =====
    'FH-001-m6-m12-hex-bolt-assortment.md':                        ('fasteners-hardware', 'bolts-nuts'),
    'FH-002-expand-nail-screw-wall-anchor-set.md':                 ('fasteners-hardware', 'anchors'),
    'FH-003-aluminum-blind-rivets-pop-rivet-assortment.md':         ('fasteners-hardware', 'rivets-pins'),
    'FH-004-galvanized-l-bracket-corner-brace-assortment.md':       ('fasteners-hardware', 'bolts-nuts'),
    'FH-005-worm-gear-hose-clamp-assortment.md':                    ('fasteners-hardware', 'bolts-nuts'),
    'FH-006-pipe-clamp-split-ring-clamp-set.md':                    ('fasteners-hardware', 'bolts-nuts'),
    'FH-007-u-bolt-spring-clip-wire-clamp-collection.md':          ('fasteners-hardware', 'bolts-nuts'),
    # 门五金 -> locks-door-hardware / hinges-accessories
    'FH-008-hinge-barrel-bolt-door-hardware-set.md':               ('locks-door-hardware', 'hinges-accessories'),
    'FH-009-metal-bracket-corner-brace-connector-assortment.md':   ('fasteners-hardware', 'bolts-nuts'),
    'FH-010-rubber-lined-cushion-clamp-pipe-support-set.md':        ('fasteners-hardware', 'bolts-nuts'),
    'FH-011-expansion-sleeve-anchor-bolt-with-eye-hook-ring.md':   ('fasteners-hardware', 'anchors'),
    'FH-012-nylon-plastic-wall-plug-rawl-anchor-assortment.md':    ('fasteners-hardware', 'anchors'),
    'FH-013-self-adhesive-cable-clip-wire-fastener-assortment.md': ('fasteners-hardware', 'chain-wire-rope'),
    'FH-014-construction-staple-u-type-tacker-staple-assortment.md': ('fasteners-hardware', 'screws'),
    'FH-015-zinc-plated-hex-bolt-hex-nut-flat-washer-assortment.md': ('fasteners-hardware', 'bolts-nuts'),
    'FH-016-hardened-concrete-nail-masonry-nail-assortment.md':   ('fasteners-hardware', 'screws'),
    'FH-017-coil-collated-construction-nails-screw-nails.md':      ('fasteners-hardware', 'screws'),
    'FH-018-galvanized-common-nails-roofing-nails-assortment.md':  ('fasteners-hardware', 'screws'),
    'FH-019-expansion-bolt-wall-anchor-assortment-with-nuts-washers.md': ('fasteners-hardware', 'anchors'),
    'FH-020-eye-bolt-with-nut-lifting-ring-bolt-assortment.md':    ('fasteners-hardware', 'bolts-nuts'),
    'FH-021-chemical-anchor-bolt-expansion-bolt-bulk-construction-fastener-mix.md': ('fasteners-hardware', 'anchors'),
    'FH-022-eye-bolt-with-nut-lifting-ring-bolt-boxed-assortment.md': ('fasteners-hardware', 'bolts-nuts'),
    'FH-023-hex-bolt-nut-washer-self-tapping-screw-assortment-kit.md': ('fasteners-hardware', 'bolts-nuts'),
    'FH-024-expansion-anchor-bolt-u-bolt-hook-bolt-mix.md':       ('fasteners-hardware', 'bolts-nuts'),
    'FH-025-machine-screw-threaded-rod-nut-washer-assortment.md': ('fasteners-hardware', 'bolts-nuts'),
    'FH-026-stainless-steel-hose-clamp-assortment-worm-drive.md':  ('fasteners-hardware', 'bolts-nuts'),
    'FH-027-plastic-wall-plug-expansion-anchor-assortment.md':     ('fasteners-hardware', 'anchors'),
    'FH-028-self-tapping-screw-drywall-screw-fiberboard-screw-assortment.md': ('fasteners-hardware', 'screws'),
    'FH-029-nylon-cable-tie-zip-tie-assortment-color-coded.md':    ('fasteners-hardware', 'chain-wire-rope'),
    'FH-030-cable-clip-wire-clip-nail-clip-assortment.md':         ('fasteners-hardware', 'chain-wire-rope'),
    'FH-031-quick-release-hose-clamp-with-handle-assortment.md':   ('fasteners-hardware', 'bolts-nuts'),
    'FH-032-plastic-wall-plug-expansion-bolt-assortment-blister-pack.md': ('fasteners-hardware', 'anchors'),
    'FH-033-hex-bolt-nut-washer-assortment-blister-pack.md':       ('fasteners-hardware', 'bolts-nuts'),
    'FH-034-wood-screw-self-tapping-screw-assortment-blister-pack.md': ('fasteners-hardware', 'screws'),

    # ===== LD 系列 (locks-door-hardware) =====
    'LD-001-brass-butt-hinge-assortment.md':                       ('locks-door-hardware', 'hinges-accessories'),
    'LD-002-brass-door-handle-knob-lock-set.md':                   ('locks-door-hardware', 'door-handles-knobs'),
    'LD-003-brass-padlock-assortment.md':                          ('locks-door-hardware', 'padlocks'),
    'LD-004-stainless-steel-padlock-set.md':                       ('locks-door-hardware', 'padlocks'),
    'LD-005-color-coated-iron-padlock-collection.md':              ('locks-door-hardware', 'padlocks'),
    'LD-006-heavy-duty-security-padlock-with-hardened-shackle.md': ('locks-door-hardware', 'padlocks'),
    'LD-007-copper-padlock-key-set.md':                            ('locks-door-hardware', 'padlocks'),
    'LD-008-disc-tumbler-pin-tumbler-padlock-set.md':              ('locks-door-hardware', 'padlocks'),
    'LD-009-zinc-alloy-wall-mounted-multi-hook-coat-rack.md':      ('locks-door-hardware', 'door-handles-knobs'),
    'LD-010-stainless-steel-over-the-door-hook-hanger.md':         ('locks-door-hardware', 'door-handles-knobs'),
    'LD-011-brass-decorative-single-wall-hook.md':                 ('locks-door-hardware', 'door-handles-knobs'),
    'LD-012-aluminum-bathroom-towel-hook-rack.md':                 ('locks-door-hardware', 'door-handles-knobs'),
    'LD-013-wooden-base-wall-mounted-hook-rail.md':                 ('locks-door-hardware', 'door-handles-knobs'),
    'LD-014-chrome-plated-robe-and-hat-hook-set.md':               ('locks-door-hardware', 'door-handles-knobs'),
    'LD-015-stainless-steel-door-hinge-assortment.md':              ('locks-door-hardware', 'hinges-accessories'),
    'LD-016-brass-gold-plated-decorative-door-hinge-set.md':       ('locks-door-hardware', 'hinges-accessories'),
    'LD-017-hydraulic-door-closer-floor-spring-assortment.md':    ('locks-door-hardware', 'hinges-accessories'),
    'LD-018-ball-bearing-drawer-slide-rail-set.md':                ('locks-door-hardware', 'hinges-accessories'),
    'LD-019-door-handle-pull-handle-lock-cylinder-set.md':         ('locks-door-hardware', 'door-handles-knobs'),
    'LD-020-window-stay-casement-window-hinge-hardware.md':       ('locks-door-hardware', 'hinges-accessories'),
    'LD-021-heavy-duty-u-lock-motorcycle-bicycle-security-lock.md': ('locks-door-hardware', 'bike-locks'),
    'LD-022-flexible-steel-cable-lock-snake-bike-lock.md':         ('locks-door-hardware', 'bike-locks'),
    'LD-023-chain-lock-with-fabric-sleeve-bike-motorcycle.md':     ('locks-door-hardware', 'bike-locks'),
    'LD-024-combination-cable-lock-password-bike-lock.md':         ('locks-door-hardware', 'bike-locks'),
    'LD-025-hardened-steel-security-chain-padlock-set.md':         ('locks-door-hardware', 'padlocks'),
    'LD-026-metal-chain-spring-hook-hardware-assortment.md':       ('locks-door-hardware', 'hinges-accessories'),
    'LD-027-slide-bolt-tower-bolt-door-latch-security-bolt-assortment.md': ('locks-door-hardware', 'door-locks'),
    'LD-028-self-locking-hasp-lock-latch-padlock-hasp-assortment.md': ('locks-door-hardware', 'door-locks'),
    'LD-029-decorative-t-hinge-strap-hinge-gate-door-hinge-set.md': ('locks-door-hardware', 'hinges-accessories'),
    'LD-030-gate-hinge-door-latch-u-bolt-hardware-set.md':         ('locks-door-hardware', 'hinges-accessories'),
    'LD-031-heavy-duty-snap-hook-carabiner-clip-spring-link-set.md': ('locks-door-hardware', 'hinges-accessories'),
    'LD-032-steel-ball-bearing-drawer-slide-rail-set.md':          ('locks-door-hardware', 'hinges-accessories'),
    'LD-033-rubber-magnetic-door-stop-bumper-catch-set.md':         ('locks-door-hardware', 'hinges-accessories'),
    'LD-034-steel-v-groove-track-roller-wheel-gate-wheel.md':       ('locks-door-hardware', 'hinges-accessories'),
    'LD-035-nylon-coated-guide-roller-bearing-wheel.md':            ('locks-door-hardware', 'hinges-accessories'),
    'LD-036-door-bolt-slide-bolt-tower-bolt-assortment-blister-pack.md': ('locks-door-hardware', 'door-locks'),
    'LD-037-door-handle-pull-handle-assortment-blister-pack.md':   ('locks-door-hardware', 'door-handles-knobs'),
    'LD-038-door-hinge-butt-hinge-assortment-blister-pack.md':     ('locks-door-hardware', 'hinges-accessories'),
    'LD-039-stainless-steel-door-butt-hinges.md':                  ('locks-door-hardware', 'hinges-accessories'),
    'LD-040-double-action-spring-door-hinges.md':                  ('locks-door-hardware', 'hinges-accessories'),
    'LD-041-soft-close-concealed-cabinet-hinges.md':               ('locks-door-hardware', 'hinges-accessories'),
    'LD-042-continuous-piano-hinges.md':                           ('locks-door-hardware', 'hinges-accessories'),
    'LD-043-heavy-duty-hasp-staple-latch.md':                      ('locks-door-hardware', 'door-locks'),
    'LD-044-sliding-door-roller-track-hardware.md':                 ('locks-door-hardware', 'hinges-accessories'),

    # ===== LR 系列 (lifting-rigging-equipment) =====
    'LR-001-heavy-duty-ratchet-tie-down-strap-set.md':             ('lifting-rigging-equipment', 'ratchet-straps'),
    'LR-002-cargo-lashing-strap-with-s-hook-j-hook.md':           ('lifting-rigging-equipment', 'ratchet-straps'),
    'LR-003-polyester-webbing-sling-flat-sling.md':                ('lifting-rigging-equipment', 'wire-rope-slings'),
    'LR-004-endless-round-sling.md':                                ('lifting-rigging-equipment', 'wire-rope-slings'),
    'LR-005-cam-buckle-tie-down-strap.md':                         ('lifting-rigging-equipment', 'ratchet-straps'),
    'LR-006-ratchet-buckle-end-fitting-assortment.md':             ('lifting-rigging-equipment', 'ratchet-straps'),
    'LR-007-lifting-eye-hook-rigging-hook-safety-hook-set.md':    ('lifting-rigging-equipment', 'lifting-hooks'),
    'LR-008-carbon-steel-link-chain-assortment-welded-chain.md':  ('lifting-rigging-equipment', 'chain-slings'),
    'LR-009-decorative-brass-chrome-copper-plated-chain-spool.md': ('lifting-rigging-equipment', 'chain-slings'),
    'LR-010-electric-chain-hoist-220v-380v-industrial-lifting-05t-5t.md': ('lifting-rigging-equipment', 'chain-hoists'),
    'LR-011-metal-painted-safety-barrier-chain-color-coded-reel.md': ('lifting-rigging-equipment', 'chain-slings'),
    'LR-012-mini-electric-wire-rope-hoist-220v-300kg-portable-lifting.md': ('lifting-rigging-equipment', 'chain-hoists'),
    'LR-013-metal-pulley-hanging-roller-bearing-wheel-set.md':    ('lifting-rigging-equipment', 'chain-hoists'),
    'LR-014-industrial-nylon-pu-caster-wheel-heavy-duty.md':      ('lifting-rigging-equipment', 'chain-hoists'),
    'LR-015-carbon-steel-forged-lifting-eye-nut-din-582.md':     ('lifting-rigging-equipment', 'lifting-hooks'),
    'LR-016-forged-swivel-eye-bolt-rotating-lifting-point.md':    ('lifting-rigging-equipment', 'lifting-hooks'),
    'LR-017-welded-master-link-oblong-link-chain-sling.md':      ('lifting-rigging-equipment', 'shackles'),
    'LR-018-d-ring-delta-triangle-ring-welded-assortment.md':     ('lifting-rigging-equipment', 'shackles'),
    'LR-019-ratchet-load-binder-lever-binder-chain-tensioner.md': ('lifting-rigging-equipment', 'ratchet-straps'),
    'LR-020-quick-link-chain-repair-connecting-link.md':         ('lifting-rigging-equipment', 'shackles'),

    # ===== RD 系列 (renovation-decoration-tools) =====
    'RD-001-pure-bristle-paint-brush-10pcs-set.md':               ('renovation-decoration-tools', 'paint-rollers-brushes'),
    'RD-002-synthetic-filament-paint-brush-12pcs-set.md':         ('renovation-decoration-tools', 'paint-rollers-brushes'),
    'RD-003-angled-sash-paint-brush-5pcs-set.md':                 ('renovation-decoration-tools', 'paint-rollers-brushes'),
    'RD-004-microfiber-paint-roller-cover-9inch-6pcs.md':         ('renovation-decoration-tools', 'paint-rollers-brushes'),
    'RD-005-acrylic-paint-roller-cover-assorted-sizes.md':       ('renovation-decoration-tools', 'paint-rollers-brushes'),
    'RD-006-mini-foam-roller-set-4inch-10pcs.md':                 ('renovation-decoration-tools', 'paint-rollers-brushes'),

    # ===== 无 SKU 前缀的重复文件 =====
    'aluminum-blind-rivets-pop-rivet-assortment.md':              ('fasteners-hardware', 'rivets-pins'),
    'brass-butt-hinge-assortment.md':                             ('locks-door-hardware', 'hinges-accessories'),
    'brass-door-handle-knob-lock-set.md':                         ('locks-door-hardware', 'door-handles-knobs'),
    'expand-nail-screw-wall-anchor-set.md':                       ('fasteners-hardware', 'anchors'),
    'galvanized-l-bracket-corner-brace-assortment.md':            ('fasteners-hardware', 'bolts-nuts'),
    'm6-m12-hex-bolt-assortment.md':                              ('fasteners-hardware', 'bolts-nuts'),
}


def fix_file(filepath, l2_slug, l3_slug):
    """修改单个文件的 categories 字段，只改动类目相关行。"""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    lines = content.split('\n')

    # 1. 找到 front matter 边界
    fm_start = -1
    fm_end = -1
    for i, line in enumerate(lines):
        if line.strip() == '---':
            if fm_start == -1:
                fm_start = i
            else:
                fm_end = i
                break

    if fm_start == -1 or fm_end == -1:
        return False, 'NO FRONT MATTER'

    # 2. 找到 categories 块的位置
    cat_start = -1
    cat_end = -1
    for i in range(fm_start + 1, fm_end):
        if lines[i].startswith('categories:') or lines[i].startswith('categories :'):
            cat_start = i
            # 找到 categories 块的结束位置（下一个非数组项的行）
            for j in range(i + 1, fm_end):
                stripped = lines[j].lstrip()
                if stripped.startswith('- ') or stripped == '':
                    continue
                else:
                    cat_end = j
                    break
            else:
                cat_end = fm_end
            break

    # 3. 构建新的 categories 块
    new_cat_block = [
        'categories:',
        '- ' + l2_slug,
        '- ' + l3_slug,
    ]

    # 4. 替换或插入 categories 块
    if cat_start != -1:
        # 替换现有的 categories 块
        lines[cat_start:cat_end] = new_cat_block
    else:
        # 没有 categories 字段，需要插入
        # 找到插入位置：sku 行之后，没有 sku 则找 title 行
        insert_after = -1
        for i in range(fm_start + 1, fm_end):
            if lines[i].startswith('sku:') or lines[i].startswith('sku :'):
                insert_after = i
                break
        if insert_after == -1:
            for i in range(fm_start + 1, fm_end):
                if lines[i].startswith('title:'):
                    insert_after = i
                    break
        if insert_after == -1:
            insert_after = fm_start  # fallback: 插到 --- 后面

        # 插入新行
        for offset, new_line in enumerate(new_cat_block):
            lines.insert(insert_after + 1 + offset, new_line)

    # 5. 更新 front matter 索引（因为可能插入了行）
    fm_end_new = -1
    for i, line in enumerate(lines):
        if line.strip() == '---':
            if fm_start == -1:
                fm_start = i
            elif i > fm_start and fm_end_new == -1:
                fm_end_new = i
                break
    fm_end = fm_end_new if fm_end_new != -1 else fm_end

    # 6. 更新 category_1（如果存在）
    for i in range(fm_start + 1, fm_end):
        if lines[i].startswith('category_1:') or lines[i].startswith('category_1 :'):
            # 检查是单行值还是数组格式
            value_part = lines[i].split(':', 1)[1].strip() if ':' in lines[i] else ''
            if value_part:
                # 单行格式：category_1: Fasteners & Hardware
                lines[i] = 'category_1: ' + l2_slug
            else:
                # 数组格式：category_1:\n- value
                lines[i] = 'category_1: ' + l2_slug
                # 删除下一行的数组项
                if i + 1 < fm_end and lines[i + 1].lstrip().startswith('- '):
                    del lines[i + 1]
            break

    # 7. 更新 category_2（如果存在）
    for i in range(fm_start + 1, fm_end):
        if lines[i].startswith('category_2:') or lines[i].startswith('category_2 :'):
            lines[i] = 'category_2: ' + l3_slug
            break

    # 8. 写回文件（保持原始编码和行尾格式）
    new_content = '\n'.join(lines)
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(new_content)

    return True, 'OK'


def main():
    # 确定产品目录路径
    script_dir = os.path.dirname(os.path.abspath(__file__))
    products_dir = os.path.join(script_dir, 'content', 'products')

    if not os.path.isdir(products_dir):
        print('错误：找不到 content/products/ 目录')
        print('请确保脚本在网站根目录（okgomike.github.io/）下运行')
        sys.exit(1)

    # 统计
    total = 0
    fixed = 0
    skipped = 0
    errors = 0
    not_in_mapping = []

    # 遍历所有 .md 文件
    for filename in sorted(os.listdir(products_dir)):
        if not filename.endswith('.md') or filename == '_index.md':
            continue

        total += 1
        filepath = os.path.join(products_dir, filename)

        if filename not in PRODUCT_CATEGORIES:
            not_in_mapping.append(filename)
            skipped += 1
            continue

        l2, l3 = PRODUCT_CATEGORIES[filename]
        success, msg = fix_file(filepath, l2, l3)

        if success:
            fixed += 1
            print(f'  [OK]   {filename} -> {l2} / {l3}')
        else:
            errors += 1
            print(f'  [FAIL] {filename} -> {msg}')

    # 输出统计
    print('\n' + '=' * 60)
    print(f'总计: {total} 个文件')
    print(f'修复: {fixed} 个')
    print(f'跳过: {skipped} 个（不在映射表中）')
    print(f'失败: {errors} 个')
    print('=' * 60)

    if not_in_mapping:
        print('\n以下文件不在映射表中（需手动处理）:')
        for f in not_in_mapping:
            print(f'  - {f}')


if __name__ == '__main__':
    main()
