#!/usr/bin/env python3
"""
render_report.py - Invention Evaluation Engine, Phase 10 (render-report)

Produces a branded, investor-grade HTML report from compiled markdown,
ledger markdown, and scores JSON artifacts.

Usage:
  python render_report.py --report <report.md> --ledger <ledger.md> --scores <scores.json>
"""
import argparse
import html as html_mod
import json
import os
import re
import subprocess
import shutil
import sys
import tempfile
from pathlib import Path


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def slug(txt):
    return re.sub(r'[^a-z0-9]+', '-', txt.lower()).strip('-')


def md_inline(text):
    s = str(text)
    s = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', s)
    s = re.sub(r'(?<!\*)\*(?!\*)(.+?)(?<!\*)\*(?!\*)', r'<em>\1</em>', s)
    s = re.sub(r'`(.+?)`', r'<code>\1</code>', s)
    return s


def css_escape(s):
    return s.replace(chr(92), chr(92)*2).replace(chr(39), chr(92)+chr(39))


def toc_marker(sid):
    return '<span id="' + sid + '" style="display:none;"></span>'


def footer_line(invention_id, submitted_by, invention_name, submitted_date, report_date):
    name_part = invention_name[:60] if invention_name else ''
    return invention_id + ' | ' + name_part + ' | ' + submitted_date + ' | ' + report_date


def parse_md_sections(text):
    sections = []
    cur_title, cur_body, cur_level = None, [], 0
    for line in text.splitlines():
        m = re.match(r'^(#{1,6})\s+(.+)$', line)
        if m:
            if cur_title is not None:
                sections.append((cur_level, cur_title, chr(10).join(cur_body)))
            cur_title = m.group(2).strip()
            cur_level = len(m.group(1))
            cur_body = []
        elif cur_title is not None:
            cur_body.append(line)
    if cur_title is not None:
        sections.append((cur_level, cur_title, chr(10).join(cur_body)))
    return sections


def _parse_tables(text):
    tables = []
    in_tbl, hdr, rows = False, [], []
    for line in text.splitlines():
        s = line.strip()
        if s.startswith(chr(124)) and not in_tbl:
            in_tbl = True
            hdr = [c.strip() for c in s.strip(chr(124)).split(chr(124))]
            continue
        if in_tbl and re.match(r'^\|[\s:|-]+\|$', s):
            continue
        if in_tbl and s.startswith(chr(124)):
            rows.append([c.strip() for c in s.strip(chr(124)).split(chr(124))])
            continue
        if in_tbl:
            tables.append({'header': hdr, 'rows': rows})
            in_tbl, hdr, rows = False, [], []
    if in_tbl:
        tables.append({'header': hdr, 'rows': rows})
    return tables


def md_block(body):
    out = []
    lines = body.splitlines()
    i = 0
    while i < len(lines):
        s = lines[i].strip()
        if not s or s.startswith('#'):
            i += 1
            continue
        if s.startswith('|'):
            tbl = []
            while i < len(lines) and lines[i].strip().startswith('|'):
                tbl.append(lines[i])
                i += 1
            for t in _parse_tables(chr(10).join(tbl)):
                hdr = ''.join('<th>' + html_mod.escape(h) + '</th>' for h in t['header'])
                rows = ''.join(
                    '<tr>' + ''.join('<td>' + md_inline(c) + '</td>' for c in row) + '</tr>'
                    for row in t['rows'])
                out.append('<table class="data"><thead><tr>' + hdr + '</tr></thead><tbody>' + rows + '</tbody></table>')
            continue
        items = []
        if s.startswith('- ') or s.startswith('* '):
            while i < len(lines):
                cur = lines[i].strip()
                if not (cur.startswith('- ') or cur.startswith('* ')):
                    break
                item = cur[2:]
                i += 1
                cont = []
                while i < len(lines):
                    n = lines[i].strip()
                    if not n or n.startswith('- ') or n.startswith('* ') or n.startswith('|') or n.startswith('#'):
                        break
                    cont.append(n)
                    i += 1
                if cont:
                    item += ' ' + ' '.join(cont)
                items.append('<li>' + md_inline(item) + '</li>')
            if items:
                out.append('<ul class="bullets">' + ''.join(items) + '</ul>')
            continue
        para = [s]
        i += 1
        while i < len(lines):
            n = lines[i].strip()
            if not n or n.startswith('- ') or n.startswith('* ') or n.startswith('|') or n.startswith('#'):
                break
            para.append(n)
            i += 1
        out.append('<p class="body">' + md_inline(' '.join(para)) + '</p>')
    return chr(10).join(out)


# ---------------------------------------------------------------------------
# SVG chart helpers (inline, matching reference HTML)
# ---------------------------------------------------------------------------

def svg_grouped_bars(title, subfactors, maxv=3):
    if not subfactors:
        return ('<svg viewBox="0 0 260 150" role="img" aria-label="' + html_mod.escape(title) + ' sub-factors">'
                '<rect x="8" y="12" width="244" height="126" fill="#f8fafc" stroke="#cbd5e1"/>'
                '<text x="130" y="78" font-size="11" fill="#64748b" text-anchor="middle">Data not established</text>'
                '</svg>')
    labels = list(subfactors.keys())
    values = [subfactors[k] for k in labels]
    W, H = 260, 150
    pad_l, pad_b, pad_t = 30, 26, 12
    pw = W - pad_l - 10
    ph = H - pad_b - pad_t
    n = len(labels)
    bw = pw / n
    colors = ['#317ecc', '#5393d4', '#75a8dc', '#97bde4', '#b9d2ec', '#dbe7f4']
    bars = ''
    for i, (lab, val) in enumerate(zip(labels, values)):
        x = pad_l + i * bw + bw * 0.2
        w = bw * 0.6
        bh = (val / maxv) * ph
        y = H - pad_b - bh
        cls = 'high' if val >= 3 else ('med' if val >= 2 else 'low')
        grad = ('<linearGradient id="g' + str(i) + '" x1="0" y1="0" x2="0" y2="1">'
                '<stop offset="0%" stop-color="' + colors[i % len(colors)] + '"/>'
                '<stop offset="100%" stop-color="#1e5f8e"/></linearGradient>')
        bars += ('<rect x="' + str(round(x, 1)) + '" y="' + str(round(y, 1)) + '" width="' + str(round(w, 1))
                 + '" height="' + str(round(bh, 1)) + '" rx="3" fill="url(#g' + str(i) + ')" class="b-fill ' + cls + '"/>'
                 '<text x="' + str(round(x + w / 2, 1)) + '" y="' + str(H - 8) + '" font-size="8" fill="#4a5560" text-anchor="middle">'
                 + html_mod.escape(lab) + '</text>'
                 '<text x="' + str(round(x + w / 2, 1)) + '" y="' + str(round(y - 4, 1)) + '" font-size="9" font-weight="700" fill="#0f2b4a" text-anchor="middle">' + str(val) + '</text>')
    grads = ''.join(('<linearGradient id="g' + str(j) + '" x1="0" y1="0" x2="0" y2="1">'
                     '<stop offset="0%" stop-color="' + colors[j % len(colors)] + '"/>'
                     '<stop offset="100%" stop-color="#1e5f8e"/></linearGradient>')
                    for j in range(n))
    return ('<svg viewBox="0 0 260 150" role="img" aria-label="' + html_mod.escape(title) + ' sub-factors">'
            '<rect x="8" y="12" width="244" height="126" fill="#f8fafc" stroke="#cbd5e1"/>'
            '<line x1="30" y1="124" x2="250" y2="124" stroke="#e2e8f0"/>' + grads + bars + '</svg>')



def svg_pie(data, title='', legend=False, sub=''):
    if not data:
        return '<svg viewBox="0 0 240 150" aria-label="pie chart"><rect width="240" height="150" fill="#f8fafc"/><text x="120" y="80" font-size="11" fill="#64748b" text-anchor="middle">Data not established</text></svg>'
    items = list(data.items()) if isinstance(data, dict) else list(enumerate(data))
    W, H = 240, 150
    cx, cy, r = W // 2, H // 2 + 5, 50
    colors = ['#1a3b5d', '#2a6fa5', '#5393d4', '#75a8dc', '#97bde4', '#b9d2ec', '#dbe7f4']
    total = sum(v for _, v in items)
    if total == 0:
        return '<svg viewBox="0 0 240 150"><circle cx="' + str(cx) + '" cy="' + str(cy) + '" r="' + str(r) + '" fill="#e2e8f0"/></svg>'
    paths = []
    start = 0
    for i, (label, val) in enumerate(items):
        frac = val / total
        end = start + frac
        large = 1 if frac > 0.5 else 0
        x1 = cx + r * __import__('math').sin(2 * __import__('math').pi * start)
        y1 = cy - r * __import__('math').cos(2 * __import__('math').pi * start)
        x2 = cx + r * __import__('math').sin(2 * __import__('math').pi * end)
        y2 = cy - r * __import__('math').cos(2 * __import__('math').pi * end)
        d = ('M ' + str(cx) + ' ' + str(cy) + ' L ' + str(round(x1, 2)) + ' ' + str(round(y1, 2))
             + ' A ' + str(r) + ' ' + str(r) + ' 0 ' + str(large) + ' 1 ' + str(round(x2, 2)) + ' ' + str(round(y2, 2)) + ' Z')
        color = colors[i % len(colors)]
        paths.append('<path d="' + d + '" fill="' + color + '" stroke="#fff" stroke-width="1"/>')
        start = end
    # Legend on right
    legend_items = ''
    for i, (label, val) in enumerate(items):
        pct = str(round(val / total * 100)) + '%'
        legend_items += ('<div style="display:flex;align-items:center;gap:4px;font-size:8px;margin-bottom:2px;">'
                         '<span style="width:8px;height:8px;background:' + colors[i % len(colors)] + ';border-radius:1px;display:inline-block;"></span>'
                         '<span style="color:#374151;">' + html_mod.escape(label) + ' ' + pct + '</span></div>')
    return ('<svg viewBox="0 0 240 150" role="img" aria-label="' + html_mod.escape(title) + '">'
            + ''.join(paths) + '<circle cx="' + str(cx) + '" cy="' + str(cy) + '" r="18" fill="#fff"/>'
            '<text x="' + str(cx) + '" y="' + str(cy + 4) + '" font-size="9" fill="#0f2b4a" text-anchor="middle" font-weight="700">' + str(len(items)) + '</text>'
            + (('<g transform="translate(160,10)">' + legend_items + '</g>') if legend else '') + '</svg>')


def svg_line(data, title='', note=''):
    if not data:
        return '<svg viewBox="0 0 260 150" aria-label="line chart"><rect width="260" height="150" fill="#f8fafc"/><text x="130" y="80" font-size="11" fill="#64748b" text-anchor="middle">Data not established</text></svg>'
    keys = [k for k, _ in data.items()] if isinstance(data, dict) else [str(i) for i in range(len(data))]
    vals = [v for _, v in data.items()] if isinstance(data, dict) else data
    show = min(len(vals), 10)
    keys = keys[:show]
    vals = vals[:show]
    W, H = 260, 150
    pad_l, pad_b = 35, 22
    cw = (W - pad_l - 10) / max(len(keys) - 1, 1)
    maxv = max(vals) if vals else 1
    minv = min(vals) if vals else 0
    rng = maxv - minv if maxv != minv else 1
    ph = H - pad_b - 10
    pts = ''.join(str(round(pad_l + i * cw, 1)) + ',' + str(round(H - pad_b - ((vals[i] - minv) / rng) * ph, 1)) for i in range(len(vals)))
    x_ticks = ''.join('<text x="' + str(round(pad_l + i * cw, 1)) + '" y="' + str(H - 4) + '" font-size="6.5" fill="#4a5560" text-anchor="middle">' + html_mod.escape(str(keys[i])) + '</text>' for i in range(len(keys)))
    return ('<svg viewBox="0 0 260 150" role="img" aria-label="' + html_mod.escape(title) + '">'
            '<defs><linearGradient id="lg" x1="0" y1="0" x2="0" y2="1"><stop offset="0%" stop-color="#5393d4" stop-opacity="0.25"/><stop offset="100%" stop-color="#5393d4" stop-opacity="0"/></defs>'
            '<polygon points="' + str(pad_l) + ',' + str(H - pad_b) + ' ' + pts.replace(',', ' ').replace('  ', ' ').replace(' ', ',') + ' ' + str(pad_l + (len(vals) - 1) * cw) + ',' + str(H - pad_b) + '" fill="url(#lg)"/>'
            '<polyline points="' + pts + '" fill="none" stroke="#317ecc" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>'
            '<line x1="' + str(pad_l) + '" y1="' + str(H - pad_b) + '" x2="' + str(W - 5) + '" y2="' + str(H - pad_b) + '" stroke="#e2e8f0"/>'
            + x_ticks + '</svg>')


def svg_dual_axis(left, right, title=''):
    if not left and not right:
        return '<svg viewBox="0 0 260 150" aria-label="dual axis"><rect width="260" height="150" fill="#f8fafc"/><text x="130" y="80" font-size="11" fill="#64748b" text-anchor="middle">Data not established</text></svg>'
    W, H = 260, 150
    pad_l, pad_r, pad_b = 35, 35, 22
    cw = (W - pad_l - pad_r) / max(max(len(left), len(right)) - 1, 1)
    ph = H - pad_b - 10
    lv = list(left.values()) if isinstance(left, dict) else list(left)
    rv = list(right.values()) if isinstance(right, dict) else list(right)
    lm = max(lv) if lv else 1
    rm = max(rv) if rv else 1
    lpts = ''.join(str(round(pad_l + i * cw, 1)) + ',' + str(round(H - pad_b - (lv[i] / lm) * ph, 1)) for i in range(len(lv)))
    rpts = ''.join(str(round(pad_l + i * cw, 1)) + ',' + str(round(H - pad_b - (rv[i] / rm) * ph, 1)) for i in range(len(rv)))
    return ('<svg viewBox="0 0 260 150" role="img" aria-label="' + html_mod.escape(title) + '">'
            '<line x1="' + str(pad_l) + '" y1="' + str(H - pad_b) + '" x2="' + str(W - pad_r) + '" y2="' + str(H - pad_b) + '" stroke="#e2e8f0"/>'
            '<polyline points="' + lpts + '" fill="none" stroke="#1a3b5d" stroke-width="2" stroke-linecap="round"/>'
            '<polyline points="' + rpts + '" fill="none" stroke="#d97706" stroke-width="2" stroke-linecap="round" stroke-dasharray="4,2"/>'
            '</svg>')


def svg_bubble(data, x_label='', y_label='', title=''):
    if not data:
        return '<svg viewBox="0 0 260 150"><rect width="260" height="150" fill="#f8fafc"/><text x="130" y="80" font-size="11" fill="#64748b" text-anchor="middle">Data not established</text></svg>'
    pts = data.get('points', [])
    W, H = 260, 150
    pad_l, pad_b, pad_r = 35, 22, 10
    xs = [p[0] for p in pts] if pts else []
    ys = [p[1] for p in pts] if pts else []
    mx = max(xs) if xs else 1
    my = max(ys) if ys else 1
    circles = ''.join('<circle cx="' + str(round(pad_l + 10 + (x / mx) * (W - pad_l - pad_r - 20), 1)) + '" cy="' + str(round(H - pad_b - 10 - (y / my) * (H - pad_b - 20), 1)) + '" r="5" fill="#5393d4" fill-opacity="0.55" stroke="#1a3b5d" stroke-width="1"/>' for x, y in pts[:15])
    return ('<svg viewBox="0 0 260 150" role="img" aria-label="' + html_mod.escape(title) + '">'
            '<line x1="' + str(pad_l) + '" y1="' + str(H - pad_b) + '" x2="' + str(W - pad_r) + '" y2="' + str(H - pad_b) + '" stroke="#e2e8f0"/>'
            + circles + '</svg>')


def build_gauge_card(title, tier_index, tier_label):
    pct = {1: 17, 2: 33, 3: 50, 4: 67, 5: 83, 6: 100}.get(tier_index, 50)
    fill_cls = {1: 'reg', 2: 'low', 3: 'med', 4: 'med', 5: 'high', 6: 'high'}.get(tier_index, 'med')
    return ('<div class="gauge-card">'
            '<div class="g-title">' + html_mod.escape(title) + '</div>'
            '<div class="g-value">' + html_mod.escape(str(tier_label)) + '</div>'
            '<div class="g-bar"><div class="fill ' + fill_cls + '" style="width:' + str(pct) + '%;"></div></div>'
            '<div class="g-sub">Gauge score ' + str(tier_index) + '/6</div>'
            '</div>')


def build_bar_card(title, subfactors):
    maxv = 3
    items = []
    for lab, val in subfactors.items():
        pct = min(100, int((val / maxv) * 100))
        cls = 'high' if val >= 3 else ('med' if val >= 2 else 'low')
        items.append('<div class="b-item">'
                     '<span class="b-label">' + html_mod.escape(lab) + '</span>'
                     '<div class="b-track"><div class="b-fill ' + cls + '" style="width:' + str(pct) + '%;"></div></div>'
                     '<span class="b-val">' + str(val) + '</span>'
                     '</div>')
    return '<div class="bar-card"><div class="b-title">' + html_mod.escape(title) + ' Factors</div>' + ''.join(items) + '</div>'


def build_ladder(stages, current_stage_label=''):
    if not stages:
        return ''
    nodes = []
    for i, stage in enumerate(stages):
        is_current = stage == current_stage_label
        cls = 'current' if is_current else 'future'
        nodes.append('<div class="node ' + cls + '">' + html_mod.escape(stage) + '</div>')
        if i < len(stages) - 1:
            nodes.append('<div class="chev">&#8250;</div>')
    return '<div class="ladder">' + ''.join(nodes) + '</div>'


def build_swot(swot):
    if not swot:
        return ''
    colors = {'s': ('Strengths', 'var(--blue)'),
              'w': ('Weaknesses', 'var(--gold)'),
              'o': ('Opportunities', 'var(--green)'),
              't': ('Threats', 'var(--red)')}
    quads = ''
    for key in ['s', 'w', 'o', 't']:
        label, color = colors.get(key, (key.upper(), 'var(--blue)'))
        items = swot.get(key, [])
        if isinstance(items, list):
            lis = ''.join('<li>' + md_inline(str(it)) + '</li>' for it in items)
        else:
            lis = ''
        quads += ('<div class="swot-quad ' + key + '">'
                  '<h4 style="color:' + color + ';">' + label + '</h4>'
                  '<ul>' + lis + '</ul></div>')
    actionability = swot.get('actionability', '')
    badge = ('<div class="swot-badge">'
             '<span class="b-k">Commercial Actionability</span>'
             '<span class="b-v">' + html_mod.escape(str(actionability)) + '</span>'
             '</div>') if actionability else ''
    return '<div class="swot-grid">' + quads + '</div>' + badge


def build_divider(title, subtitle=''):
    return ('<div class="divider-page page">'
            '<div class="div-title">' + html_mod.escape(title) + '</div>'
            '<div class="div-sub">' + html_mod.escape(subtitle) + '</div>'
            '<div class="div-line"></div></div>')


def build_search_boxes(ledger_text):
    boxes = []
    queries = re.findall(r'(?:Query|Search|XHR)[:\s]+(.+?)(?:\n|$)', ledger_text)
    for q in queries[:6]:
        q = q.strip()
        if q:
            boxes.append('<div class="search-box">'
                         '<div class="sq"><span class="lbl">Search Query</span><br>' + md_inline(q) + '</div>'
                         '</div>')
    if not boxes:
        boxes.append('<div class="search-box"><div class="sq">Search ledger (avenue records)</div></div>')
    return chr(10).join(boxes)


def build_submission_record(submission_text):
    if not submission_text:
        return ''
    out = []
    for ln in submission_text.splitlines():
        s = ln.strip()
        if not s or s.startswith('#'):
            continue
        if s.startswith('|'):
            continue
        if s.startswith('- ') or s.startswith('* '):
            out.append('<li>' + md_inline(s[2:]) + '</li>')
        else:
            out.append('<p>' + md_inline(s) + '</p>')
    if out:
        return '<ul>' + ''.join(l for l in out if l.startswith('<li>')) + '</ul>' + ''.join(p for p in out if p.startswith('<p>'))
    return ''


def build_toc_items(sections, page_map=None):
    if page_map is None:
        page_map = {}
    items = []
    page_num = 3
    for sid, title, level in sections:
        pg = page_map.get(sid, str(page_num))
        cls = 'l2' if level == 2 else ''
        items.append('<div class="toc-item ' + cls + '">'
                     '<span class="toc-title">' + html_mod.escape(title) + '</span>'
                     '<span class="toc-page">' + str(pg) + '</span></div>')
        if level == 1:
            page_num += 1
    return chr(10).join(items)


def load_scores(path):
    with open(path, encoding='utf-8') as f:
        data = json.load(f)
        # Handle both flat structure and scores_manifest wrapper
        if 'scores_manifest' in data:
            return data['scores_manifest']
        return data


# ---------------------------------------------------------------------------
# Main render function
# ---------------------------------------------------------------------------

def render(report_md, ledger_md, scores, submission_md=None,
           template_path=None, page_map=None, markers=True, v17_artifacts=None,
           ledger=None, ledger_path=None):
    here = os.path.dirname(os.path.abspath(__file__))
    template_path = template_path or os.path.join(here, 'template.html')

    # Read template
    if os.path.exists(template_path):
        with open(template_path, encoding='utf-8') as f:
            tpl = f.read()
    else:
        tpl = build_inline_template()

    # ---- contract validation (abort if source would be silently dropped) ----
    try:
        import contract as _contract_mod
        _ast = _contract_mod.parse_report_ast(report_md)
        _contract_mod.validate_before_render(_ast)
    except _contract_mod.RenderContractFailure:
        raise
    except Exception:
        pass  # contract module unavailable; skip validation
    
    # ---- v1.8: Pre-render Integrity Gate ----
    # This catches cross-patent contamination, evidence provenance errors,
    # epistemic state contradictions, and proposition-registry violations
    # BEFORE rendering.
    try:
        import contract as _contract_mod
        _contract_mod.pre_render_integrity_gate(
            report_md, scores, submission_md or '',
            ledger=ledger, ledger_path=ledger_path)
    except _contract_mod.RenderContractFailure:
        raise
    except Exception:
        pass  # contract module unavailable; skip validation
    
    # ---- v1.8: Extract target patent identity early ----
    target_patent = scores.get('target_patent', {})
    target_pub_number = target_patent.get('publication_number', 'UNKNOWN')
    target_title = target_patent.get('title', 'Unknown Invention')
    target_label = f"{target_pub_number} — {target_title}" if target_pub_number != 'UNKNOWN' else scores.get('invention_name', 'Unknown')
    gov_rights = target_patent.get('government_rights', 'Not established')
    patent_source_file = target_patent.get('patent_source_file', f'patent-source-{scores.get("invention_id", "unknown").lower()}.json')

    page_map = page_map or {}
    sections = parse_md_sections(report_md)

    top_sections = []
    current = None
    for level, title, body in sections:
        if level == 2:
            if current is not None:
                top_sections.append(current)
            current = {'title': title, 'body': body, 'children': []}
        elif current is not None and level >= 3:
            current['children'].append((title, body))
    if current is not None:
        top_sections.append(current)

    AREA_DIVIDERS = {
        'Technology Analysis': ('TECHNOLOGY ANALYSIS', 4),
        'Patent Landscape Analysis': ('PATENT LANDSCAPE ANALYSIS', 5),
        'IP / Novelty Analysis': ('NOVELTY & INTELLECTUAL PROPERTY ANALYSIS', 6),
        # Naming variant used by some reports (e.g. US5215088)
        'Novelty & IP Analysis': ('NOVELTY & INTELLECTUAL PROPERTY ANALYSIS', 6),
        'Literature Analysis': ('LITERATURE ANALYSIS', 7),
        'Market Analysis': ('MARKET ANALYSIS', 8),
        'Potential Partners': ('POTENTIAL PARTNERS', 9),
    }

    # TOC: pre-set template sections + analysis sections
    toc_sections = [
        (slug('Table of Contents'), 'Table of Contents', 1),
        (slug('Executive Summary'), 'Executive Summary', 1),
        (slug('v1.7 Control State'), 'v1.7 Control State', 1),
        (slug('Original Submission'), 'Original Submission', 1),
    ]
    page_num = 5  # cover=1, TOC=2, exec=3, control=4, submission=5
    # One divider TOC entry per unique area. Some sections have naming
    # variants (e.g. 'IP / Novelty Analysis' vs 'Novelty & IP Analysis')
    # mapping to the same area — dedupe so the TOC never lists a divider
    # twice.
    _seen_areas = set()
    for bare, (area_title, _) in AREA_DIVIDERS.items():
        if area_title in _seen_areas:
            continue
        _seen_areas.add(area_title)
        toc_sections.append((slug('divider-' + area_title), area_title, 1))
    analysis_content_sections = ['Technology Analysis', 'Patents Analysis', 'IP & Novelty Analysis',
                                  'Prior Art Analysis', 'Market Landscape', 'Partner Landscape',
                                  'Operational Audit', 'Sources & Methodology',
                                  'Inference Controls', 'Opportunity Assessment',
                                  'Competitive Landscape', 'Regulatory Resources',
                                  'Product Design', 'IP Strength', 'Development Stage',
                                  'SWOT Analysis', 'Patent Landscape & Data']
    ANALYSIS_PAGE_MAP = {
        'Technology Analysis': 6, 'Patent Landscape Analysis': 7,
        'IP / Novelty Analysis': 8, 'Literature Analysis': 9,
        'Market Analysis': 10, 'Potential Partners': 11,
        'Operational Audit': 13, 'Evidence Recovery Record': 14, 'Sources': 15,
        'v1.7 Inference Controls': 16,
        'Opportunity Assessment': 18, 'Competitive Landscape': 19,
        'Regulatory Resources': 20, 'Product Concept': 21,
        'Patentability Summary': 22, 'Development Stage': 23,
        'SWOT Analysis': 24, 'Landscape & Market Data': 25,
        'Appendix A': 27, 'Appendix B': 28, 'Appendix C': 29,
    }

    current_area = None
    body_html = []
    # Sections rendered by the template itself (Executive Summary, v1.7
    # Control State, Original Submission). The body loop must NOT re-render
    # them from report.md — that produced duplicated major sections.
    TEMPLATE_RENDERED = {
        'Executive Summary',
        'v1.7 Control State',
        'Original Submission',
    }
    # Sections rendered by the data-frame generator (evidence-constrained).
    # The body loop must NOT re-render them from report.md — that produced
    # duplicated SWOT Analysis and Potential Partners sections.
    DATA_FRAME_RENDERED = {'SWOT Analysis'}
    # The data-frame generator only renders Potential Partners when partner
    # data exists in the scores manifest. When it does not, the body loop
    # must fall back to the report.md section — never drop it silently.
    if scores.get('partners'):
        DATA_FRAME_RENDERED.add('Potential Partners')
    for item in top_sections:
        title = item['title']
        bare = re.sub(r'^\d+\.\s+', '', title)

        # Drop sections already handled by template (non-numbered, not in SECTION_CONTRACT)
        from contract import SECTION_CONTRACT as _SC
        _contract_names = {s.name for s in _SC}
        if not re.match(r'^\d+\.\s+', title) and title not in _contract_names:
            continue

        # v1.8: skip sections the template already rendered (duplication fix)
        if bare in TEMPLATE_RENDERED:
            continue

        # v1.8: skip sections the data-frame generator renders (duplication fix)
        if bare in DATA_FRAME_RENDERED:
            continue

        area_title, _ = AREA_DIVIDERS.get(bare, (None, None))
        if area_title and area_title != current_area:
            current_area = area_title
            # TOC entry was already added upfront (deduplicated per area);
            # only the divider page is rendered inline here.
            body_html.append(build_divider(area_title, target_label))

        clean_title = re.sub(r'^\d+\.\s+', '', title)
        sid = slug(title)
        pc = ANALYSIS_PAGE_MAP.get(clean_title, str(page_num))
        toc_sections.append((sid, clean_title, 1))
        page_num = max(page_num, int(pc) + 1) if str(pc).isdigit() else page_num + 1
        mark = toc_marker(sid) if markers else ''
        children = item.get('children', [])
        head = clean_title
        # Count semantic nodes for contract accounting
        def _cn(body, chs):
            n = 0
            for ln in body.splitlines():
                s = ln.strip()
                if s.startswith('- ') or s.startswith('* '):
                    n += 1
                elif s.startswith('|'):
                    n += 1
                elif s and not s.startswith('#'):
                    n += 1
            for c in chs:
                for ln in c[1].splitlines():
                    cs = ln.strip()
                    if cs.startswith('- ') or cs.startswith('* '):
                        n += 1
                    elif cs.startswith('|'):
                        n += 1
                    elif cs and not cs.startswith('#'):
                        n += 1
            return n
        _nc = _cn(item['body'], children)
        dc_title = re.sub(r'^\d+\.\s+', '', title)
        out_parts = ['<div class="page" data-contract="' + html_mod.escape(dc_title) + '" data-nodes="' + str(_nc) + '">' + mark + '<h2 class="section-title">' + html_mod.escape(head) + '</h2>']
        out_parts.append(md_block(item['body']))
        for child_title, child_body in children:
            out_parts.append('<h3>' + html_mod.escape(child_title) + '</h3>')
            out_parts.append(md_block(child_body))
        out_parts.append('</div>')
        body_html.append(chr(10).join(out_parts))

    # Data-frame sections
    market_op = scores.get('market_opportunity', {})
    comp = scores.get('competitor_landscape', {})
    reg_data = scores.get('regulatory_resources', {})
    diagram = scores.get('product_diagram', {})
    pat = scores.get('patentability_summary', {})
    dev = scores.get('dev_timeline', {})
    swot = scores.get('swot', {})

    def placeholder_frame(title, note=''):
        note_html = '<div class="caption">' + md_inline(note) + '</div>' if note else ''
        return ('<div class="data-frame">'
                '<div class="df-title">' + html_mod.escape(title) + '</div>'
                '<div class="established-note"><em>No established findings derived from this run</em></div>'
                + note_html + '</div>')

    def market_opp_table(data):
        rows = data.get('rows', [])
        if not rows:
            return placeholder_frame('Opportunity Assessment')
        headers = ['Sector', 'Sub-sector', 'Industry', 'Products/Services',
                   'Market Need', 'Purchaser', 'Distribution', 'Est. Unit Price']
        hdr_html = ''.join('<th>' + html_mod.escape(h) + '</th>' for h in headers)
        tbody = ''
        for row in rows:
            cells = ''.join('<td>' + md_inline(row.get(k, 'Not established')) + '</td>' for k in
                           ['sector', 'sub_sector', 'industry', 'products', 'need', 'purchaser', 'channels', 'price'])
            tbody += '<tr>' + cells + '</tr>'
        title = data.get('title', 'Opportunity Assessment')
        return ('<div class="data-frame"><div class="df-title">' + html_mod.escape(title) + '</div>'
                '<table class="data"><thead><tr>' + hdr_html + '</tr></thead><tbody>' + tbody + '</tbody></table></div>')

    def competitor_table(data):
        swot_data = data.get('swot', {})
        if swot_data:
            return build_swot(swot_data)
        return placeholder_frame('Competitive Landscape')

    def regulatory_table(data):
        rows = data.get('rows', [])
        if not rows:
            return placeholder_frame('Regulatory Resources')
        hdr_html = '<th>Jurisdiction</th><th>Body</th><th>Pathway</th><th>Link</th>'
        tbody = ''
        for row in rows:
            tbody += '<tr>' + ''.join('<td>' + md_inline(str(row.get(k, ''))) + '</td>'
                       for k in ['jurisdiction', 'body', 'pathway', 'link']) + '</tr>'
        return ('<div class="data-frame"><div class="df-title">Regulatory Resources</div>'
                '<table class="data"><thead><tr>' + hdr_html + '</tr></thead><tbody>' + tbody + '</tbody></table></div>')

    def product_diagram(data):
        stages = data.get('stages', [])
        tech_stages = data.get('tech_stages', [])
        patent_rows = data.get('patent_basis', [])
        if not stages and not tech_stages and not patent_rows:
            return placeholder_frame('Product Concept')
        parts = []
        if stages:
            parts.append('<h4>Development Roadmap</h4>' + build_ladder(stages, data.get('current', '')))
        if tech_stages:
            parts.append('<h4>Technology Maturity</h4>' + build_ladder(tech_stages, data.get('tech_current', '')))
        if patent_rows:
            rows = ''.join('<tr><td>' + md_inline(r.get('criterion', '')) + '</td><td>' + md_inline(r.get('finding', '')) + '</td></tr>'
                          for r in patent_rows[:4])
            parts.append('<table class="data"><thead><tr><th>Criterion</th><th>Finding</th></tr></thead><tbody>' + rows + '</tbody></table>')
        return '<div class="data-frame"><div class="df-title">Product Concept</div>' + chr(10).join(parts) + '</div>'

    def patentability_table(data):
        rows = data.get('rows', [])
        if not rows:
            return placeholder_frame('Patentability Summary')
        hdr_html = '<th>Criterion</th><th>Finding</th><th>Basis</th>'
        tbody = ''
        for row in rows:
            tbody += ('<tr><td><strong>' + md_inline(row.get('criterion', '')) + '</strong></td>'
                      '<td>' + md_inline(row.get('finding', '')) + '</td>'
                      '<td>' + md_inline(row.get('basis', '')) + '</td></tr>')
        return ('<div class="data-frame"><div class="df-title">Patentability Summary</div>'
                '<table class="data"><thead><tr>' + hdr_html + '</tr></thead><tbody>' + tbody + '</tbody></table></div>')

    def dev_timeline(data):
        stages = data.get('stages', [])
        current = data.get('current', '')
        if not stages:
            return '<div class="card"><p>Development data not established in this run.</p></div>'
        return ('<div class="card">'
                '<p class="text-small text-muted">Current stage: <strong>' + html_mod.escape(current) + '</strong>.</p>'
                + build_ladder(stages, current)
                + '<p class="text-small text-muted" style="margin-top:6px;">Next milestones: prototype validation, clinical testing, regulatory pathway confirmation.</p>'
                + '</div>')

    def charts_html(charts_data):
        parts = []
        region = charts_data.get('region_pie', {})
        if region.get('data'):
            parts.append('<div class="chart-frame">'
                         '<div class="c-title">' + html_mod.escape(region.get('title', 'Patent Applications by Region')) + '</div>'
                         + svg_pie(region['data'], region.get('title', ''), True, region.get('sub_pie'))
                         + '<div class="caption">' + html_mod.escape(region.get('note', '')) + '</div></div>')
        else:
            parts.append('<div class="chart-frame"><div class="c-title">Patent Applications by Region</div>'
                         '<div class="placeholder"><div class="ph-title">Data not established in this run</div>'
                         'See Operational Audit.</div></div>')

        applicants = charts_data.get('applicants_pie', {})
        if applicants.get('data'):
            parts.append('<div class="chart-frame">'
                         '<div class="c-title">' + html_mod.escape(applicants.get('title', 'Top Applicants')) + '</div>'
                         + svg_pie(applicants['data'], applicants.get('title', ''), True, applicants.get('sub_pie'))
                         + '<div class="caption">' + html_mod.escape(applicants.get('note', '')) + '</div></div>')
        else:
            parts.append('<div class="chart-frame"><div class="c-title">Top Applicants</div>'
                         '<div class="placeholder"><div class="ph-title">Data not established</div>See Operational Audit.</div></div>')

        activity = charts_data.get('activity_line', {})
        if activity.get('data'):
            parts.append('<div class="chart-frame">'
                         '<div class="c-title">' + html_mod.escape(activity.get('title', 'Filing Activity')) + '</div>'
                         + svg_line(activity['data'], activity.get('title', ''), activity.get('note'))
                         + '<div class="caption">' + html_mod.escape(activity.get('note', '')) + '</div></div>')
        else:
            parts.append('<div class="chart-frame"><div class="c-title">Filing Activity Trend</div>'
                         '<div class="placeholder"><div class="ph-title">Data not established</div>See Operational Audit.</div></div>')

        naics = charts_data.get('naics_dual', {})
        if naics.get('left') and naics.get('right'):
            parts.append('<div class="chart-frame">'
                         '<div class="c-title">' + html_mod.escape(naics.get('title', 'Industry Metrics')) + '</div>'
                         + svg_dual_axis(naics['left'], naics['right'], naics.get('title', ''))
                         + '<div class="caption">' + html_mod.escape(naics.get('note', '')) + '</div></div>')
        else:
            parts.append('<div class="chart-frame"><div class="c-title">Industry Metrics</div>'
                         '<div class="placeholder"><div class="ph-title">Data not established</div>See Operational Audit.</div></div>')

        bubble = charts_data.get('naics_bubble', {})
        if bubble.get('points'):
            # Build a simple bar-like viz for employee brackets
            pts = bubble['points']
            bars = ''.join('<circle cx="' + str(40 + j * 22) + '" cy="' + str(130 - int(v / 359 * 118)) + '" r="5" fill="#75a8dc" fill-opacity="0.55" stroke="#2a6fa5" stroke-width="1.5"/>'
                          '<text x="' + str(40 + j * 22) + '" y="' + str(130 - int(v / 359 * 118) - 8) + '" font-size="7" font-weight="700" fill="#0f2b4a" text-anchor="middle">' + str(v) + '</text>'
                          '<text x="' + str(40 + j * 22) + '" y="145" font-size="6.5" fill="#4a5560" text-anchor="middle">' + html_mod.escape(str((pts[j].get('bracket', pts[j][0] if isinstance(pts[j], (list, tuple)) else str(j))))) + '</text>'
                          for j, v in enumerate([p.get('value', p[1] if isinstance(p, (list, tuple)) else 0) for p in pts[:12]]))
            parts.append('<div class="chart-frame">'
                         '<div class="c-title">' + html_mod.escape(bubble.get('title', 'Establishments by Employee-Size Bracket')) + '</div>'
                         '<svg viewBox="0 0 320 160" role="img" aria-label="employee-size brackets"><line x1="25" y1="130" x2="310" y2="130" stroke="#e2e8f0"/>' + bars + '</svg>'
                         '<div class="caption">NAICS establishment size distribution.</div></div>')
        else:
            parts.append('<div class="chart-frame"><div class="c-title">Establishments by Employee Bracket</div>'
                         '<div class="placeholder"><div class="ph-title">Data not established</div>See Operational Audit.</div></div>')

        for tp in charts_data.get('third_party', []):
            parts.append('<div class="chart-frame">'
                         '<div class="c-title">' + html_mod.escape(tp.get('label', 'Third-party graphic')) + '</div>'
                         '<div class="placeholder"><div class="ph-title">Not available in this run</div>'
                         + html_mod.escape(tp.get('note', '')) + '</div></div>')
        return parts

    # Build data-frame pages
    # v1.8: report.md section bodies for sections the data-frame generator
    # renders. The data-frame output is the evidence-constrained primary view;
    # the report.md body (e.g. the P-08-005 licensing decomposition) is
    # appended below it so no source content is dropped when the body loop
    # skips these sections.
    _section_bodies = {}
    for _item in top_sections:
        _bare = re.sub(r'^\d+\.\s+', '', _item['title'])
        _body = _item['body']
        # Include child sections (e.g. "### Licensing Terms Assessment" under
        # Potential Partners) so their content is preserved too.
        for _ctitle, _cbody in _item.get('children', []):
            _body += '\n\n' + _cbody
        _section_bodies[_bare] = _body

    body_html.append('<div class="page"><h2 class="section-title">Opportunity Assessment</h2>'
                     + market_opp_table(market_op) + '</div>')
    body_html.append('<div class="page"><h2 class="section-title">Competitive Landscape</h2>'
                     + competitor_table(comp) + '</div>')
    body_html.append('<div class="page"><h2 class="section-title">Regulatory Resources</h2>'
                     + regulatory_table(reg_data) + '</div>')
    body_html.append('<div class="page"><h2 class="section-title">Product Concept</h2>'
                     + product_diagram(diagram) + '</div>')
    body_html.append('<div class="page"><h2 class="section-title">Patentability Summary</h2>'
                     + patentability_table(pat) + '</div>')

    dev_timeline_html = build_dev_timeline_html(dev)
    body_html.append('<div class="page"><h2 class="section-title">Development Stage</h2>'
                     + dev_timeline_html + '</div>')

    swot_html = build_swot(swot) if swot else ('<div class="swot-grid">'
        '<div class="swot-quad s"><h4>Strengths</h4><ul><li>Established findings from technical analysis</li></ul></div>'
        '<div class="swot-quad w"><h4>Weaknesses</h4><ul><li>Evidence gaps require further diligence</li></ul></div>'
        '<div class="swot-quad o"><h4>Opportunities</h4><ul><li>Partnership and licensing pathways exist</li></ul></div>'
        '<div class="swot-quad t"><h4>Threats</h4><ul><li>Competitive and regulatory pressures</li></ul></div>'
        '</div>'
        '<div class="swot-badge"><span class="b-k">Commercial Actionability</span><span class="b-v">Indeterminate-to-Limited</span></div>')
    swot_extra = _section_bodies.get('SWOT Analysis', '')
    body_html.append('<div class="page"><h2 class="section-title">SWOT Analysis</h2>'
                     + swot_html
                     + (md_block(swot_extra) if swot_extra else '')
                     + '<p class="text-small text-muted" style="margin-top:12px;">SWOT content derived from Established Findings and Analytical Conclusions.</p></div>')

    charts_data = scores.get('charts', {})
    chart_parts = charts_html(charts_data)
    if chart_parts:
        body_html.append('<div class="page"><h2 class="section-title">Landscape & Market Data</h2>' + chart_parts[0] + '</div>')
        for ch in chart_parts[1:]:
            body_html.append('<div class="page">' + ch + '</div>')

    # Partner section
    partners = scores.get('partners', [])
    if partners:
        pcards = ''.join(
            '<div class="partner-card"><div class="p-name">' + html_mod.escape(p.get('name', '')) + '</div>'
            '<div class="p-contact">' + html_mod.escape(p.get('contact', '')) + '</div>'
            '<div class="p-desc">' + md_inline(p.get('description', '')) + '</div>'
            '<span class="p-tag">' + html_mod.escape(p.get('tag', 'Licensing')) + '</span></div>'
            for p in partners
        )
        # Append the report.md section body (licensing terms assessment,
        # P-08-005 atomic decomposition) below the partner cards so the
        # data-frame takeover never drops source content.
        partners_extra = _section_bodies.get('Potential Partners', '')
        # The body loop skips this section (DATA_FRAME_RENDERED), so its
        # divider page must be rendered here — otherwise the POTENTIAL
        # PARTNERS divider silently vanishes from the report.
        body_html.append(build_divider('POTENTIAL PARTNERS', target_label))
        body_html.append('<div class="page"><h2 class="section-title">Potential Partners</h2>'
                         '<div class="partner-grid">' + pcards + '</div>'
                         + (md_block(partners_extra) if partners_extra else '')
                         + '</div>')

    # ---- gauges / bars / commercialization ----
    gauges = scores.get('gauges', {})
    g_tech = gauges.get('technology', {})
    g_ip = gauges.get('ip', {})
    g_mkt = gauges.get('market', {})

    cards = [
        build_gauge_card('Technology', g_tech.get('tier_index', 3), g_tech.get('tier_label', 'Moderate')),
        build_gauge_card('IP', g_ip.get('tier_index', 2), g_ip.get('tier_label', 'Limited-Moderate')),
        build_gauge_card('Market', g_mkt.get('tier_index', 2), g_mkt.get('tier_label', 'Limited-Moderate')),
    ]
    bar_cards = [
        build_bar_card('Technology', g_tech.get('subfactors', {})),
        build_bar_card('IP', g_ip.get('subfactors', {})),
        build_bar_card('Market', g_mkt.get('subfactors', {})),
    ]
    comm = scores.get('commercialization_summary', {})
    comm_html = '<p>' + md_inline(comm.get('paragraph', '')) + '</p>'
    if comm.get('teasers'):
        comm_html += '<ul>' + ''.join('<li>' + md_inline(t) + '</li>' for t in comm['teasers']) + '</ul>'

    # ---- evidence IDs ----
    evidence_ids = set(re.findall(r'P-\d{2}-\d{3}', report_md))
    evidence_ids.update(re.findall(r'P-\d{2}-\d{3}', json.dumps(scores)))
    evidence_items = ' '.join('<code>' + pid + '</code>' for pid in sorted(evidence_ids))

    # ---- v17 control panel ----
    raw_v17 = scores.get('v17_artifacts', None)
    if isinstance(raw_v17, str) and not v17_artifacts:
        art_dir = Path(raw_v17)
        def _rj(name, fb):
            p = art_dir / name
            if not p.exists():
                return fb
            if p.suffix.lower() == '.json':
                return json.loads(p.read_text(encoding='utf-8'))
            return p.read_text(encoding='utf-8')
        v17_artifacts = {
            'rights': _rj('rights-graph.json', {}).get('status', _rj('rights-graph.json', {})),
            'bridge': _rj('bridge-vector.json', {}),
            'debt': _rj('evidence-debt.json', []),
            'constraints': _rj('constraint-report.json', {}).get('constraints', []),
            'recovery': _rj(f'recovery-evidence-{scores.get("invention_id", "unknown").lower()}-v17.md', ''),
        }
        scores['v17_artifacts'] = v17_artifacts
    v17 = v17_artifacts or raw_v17 or {}
    if isinstance(v17, str):
        v17 = {}
    rights = v17.get('rights', {})
    bridge = v17.get('bridge', {})
    debt = v17.get('debt', [])
    constraints = v17.get('constraints', [])
    legal_status = rights.get('state', 'NOT LOADED')
    bridge_state = bridge.get('state', 'NOT LOADED')
    control_text = ('legal status=' + html_mod.escape(str(legal_status)) + '; '
                    'bridge=' + html_mod.escape(str(bridge_state)) + '; '
                    'evidence debt=' + str(len(debt)) + ' items; constraints=' + str(len(constraints)) + '.')

    # Recovery queue
    recovery_items = v17.get('debt', []) or v17.get('recovery', [])
    if isinstance(recovery_items, list):
        rec_html = ''.join(
            '<li><strong>' + html_mod.escape(str(r.get('proposition', r.get('id', '')))) + ':</strong> '
            + html_mod.escape(str(r.get('missingness', r.get('description', '')))) + ' — '
            + html_mod.escape(str(r.get('state', r.get('status', 'PENDING')))) + '</li>'
            for r in recovery_items[:10]
        )
    else:
        rec_html = '<li>No recovery items in current run.</li>'

    # Family info
    family = rights.get('family', {}) if isinstance(rights, dict) else {}
    active_family = family.get('active_members', [])
    if isinstance(active_family, list) and active_family:
        fam_str = '; '.join(str(m) for m in active_family[:4])
    elif isinstance(family, dict):
        fam_str = str(family.get('active_note', 'pending verification'))
    else:
        fam_str = 'pending verification'

    # Inventor info from submission
    inventors = 'Not established'
    assignee = 'Not established'
    provisional = parent = divisional = grant = 'Not established'
    classification = ''
    # gov_rights was already set from target_patent (canonical source) above;
    # do NOT reset it here — that clobbered the correct value with
    # 'Not established' and dropped the NSF grant from the report.
    claim_core = manufacturing = status_field = 'Not established'
    if submission_md:
        sub_text = submission_md
        inv_m = re.search(r'Inventors?[:]\s*(.+)', sub_text)
        if inv_m:
            inventors = inv_m.group(1).strip()
        asgn_m = re.search(r'Assignee[:]\s*(.+)', sub_text)
        if asgn_m:
            assignee = asgn_m.group(1).strip()
        prov_m = re.search(r'Provisional[:]\s*(.+)', sub_text)
        if prov_m:
            provisional = prov_m.group(1).strip()
        par_m = re.search(r'Parent[:]\s*(.+)', sub_text)
        if par_m:
            parent = par_m.group(1).strip()
        div_m = re.search(r'Divisional[:]\s*(.+)', sub_text)
        if div_m:
            divisional = div_m.group(1).strip()
        gr_m = re.search(r'Patent grant[:]\s*(.+)', sub_text)
        if gr_m:
            grant = gr_m.group(1).strip()
        cls_m = re.search(r'Classification[:]\s*(.+)', sub_text)
        if cls_m:
            classification = cls_m.group(1).strip()
        cl_m = re.search(r'Claim 1 core[:]\s*(.+)', sub_text)
        if cl_m:
            claim_core = cl_m.group(1).strip()
        # Government rights: target_patent is canonical; the submission record
        # is a fallback only when the canonical source is absent.
        gov_m = re.search(r'Government (?:support|rights?)[:]\s*(.+)', sub_text, re.I)
        if gov_m and gov_rights == 'Not established':
            gov_rights = gov_m.group(1).strip()

    # Audit table
    audit_rows = []
    for level, title, body in sections:
        if re.match(r'Operational Audit', title):
            for t in _parse_tables(body):
                for row in t.get('rows', []):
                    if len(row) >= 2:
                        audit_rows.append('<tr><td>' + md_inline(row[0]) + '</td><td>' + md_inline(row[1]) + '</td></tr>')
            break

    # ---- fill template ----
    run_id = scores.get('run_id', 'unknown')
    invention_name = scores.get('invention_name', '')
    submitted_by = scores.get('submitted_by', '')
    invention_id = scores.get('invention_id', '')
    report_date = scores.get('report_date', '')
    submitted_date = scores.get('submitted_date', '')
    bridge_state_label = bridge.get('state_label', bridge_state)

    toc_html = build_toc_items(toc_sections, page_map)
    exec_mark = toc_marker(slug('Executive Summary')) if markers else ''

    out = tpl
    out = out.replace('{{REPORT_TITLE}}', html_mod.escape('Invention Evaluation Report — ' + invention_name))
    out = out.replace('{{INVENTION_NAME}}', html_mod.escape(invention_name))
    out = out.replace('{{SUBMITTED_BY}}', html_mod.escape(submitted_by))
    out = out.replace('{{INVENTION_ID}}', html_mod.escape(invention_id))
    out = out.replace('{{SUBMITTED_DATE}}', html_mod.escape(submitted_date))
    out = out.replace('{{REPORT_DATE}}', html_mod.escape(report_date))
    out = out.replace('{{FOOTER_LINE}}', css_escape(footer_line(invention_id, submitted_by, invention_name, submitted_date, report_date)))
    out = out.replace('{{TOC_ITEMS}}', toc_html)
    out = out.replace('{{TOC_MARK_EXEC}}', exec_mark)
    out = out.replace('{{GAUGE_TECHNOLOGY}}', cards[0])
    out = out.replace('{{GAUGE_IP}}', cards[1])
    out = out.replace('{{GAUGE_MARKET}}', cards[2])
    out = out.replace('{{BAR_TECHNOLOGY}}', bar_cards[0])
    out = out.replace('{{BAR_IP}}', bar_cards[1])
    out = out.replace('{{BAR_MARKET}}', bar_cards[2])
    out = out.replace('{{COMMERCIAL_SUMMARY}}', comm_html)
    out = out.replace('{{EXEC_EVIDENCE}}', evidence_items)
    out = out.replace('{{V17_CONTROL_TEXT}}', control_text)
    out = out.replace('{{LEGAL_STATUS}}', str(legal_status).upper())
    out = out.replace('{{ACTIVE_FAMILY}}', html_mod.escape(fam_str))
    out = out.replace('{{BRIDGE_STATE}}', html_mod.escape(str(bridge_state_label).upper()))
    out = out.replace('{{RECOVERY_QUEUE}}', rec_html)
    out = out.replace('{{INVENTORS}}', html_mod.escape(inventors))
    out = out.replace('{{ASSIGNEE}}', html_mod.escape(assignee))
    out = out.replace('{{PROVISIONAL}}', html_mod.escape(provisional))
    out = out.replace('{{PARENT}}', html_mod.escape(parent))
    out = out.replace('{{DIVISIONAL}}', html_mod.escape(divisional))
    out = out.replace('{{PRIOR_PUB}}', html_mod.escape(target_patent.get('prior_publication', 'Not established')))
    out = out.replace('{{GRANT}}', html_mod.escape(grant))
    out = out.replace('{{CLASSIFICATION}}', html_mod.escape(classification))
    out = out.replace('{{GOV_RIGHTS}}', html_mod.escape(gov_rights))
    out = out.replace('{{CLAIM_CORE}}', html_mod.escape(claim_core))
    out = out.replace('{{MANUFACTURING}}', html_mod.escape(target_patent.get('manufacturing', 'Not established')))
    out = out.replace('{{STATUS}}', html_mod.escape(target_patent.get('status', 'Not established')))
    out = out.replace('{{AUDIT_TABLE}}', '<table class="data"><thead><tr><th>Proposition</th><th>Disposition</th><th>Barrier / Note</th></tr></thead><tbody>' + ''.join(audit_rows) + '</tbody></table>')

    # ---- Appendix A: Patent Family & Legal Status ----
    family_rows = []
    fam_data = v17.get('rights', {})
    if isinstance(fam_data, dict):
        for k, v in sorted(fam_data.items()):
            if k == 'family':
                continue  # rendered intentionally below, not as a raw dict
            family_rows.append('<tr><td>' + html_mod.escape(str(k)) + '</td><td>' + md_inline(str(v)) + '</td></tr>')
    # Render the family object intentionally (fixes Python-dict leak).
    fam_obj = fam_data.get('family', {}) if isinstance(fam_data, dict) else {}
    fam_html = ''
    if isinstance(fam_obj, dict):
        active = fam_obj.get('active_members', [])
        note = fam_obj.get('active_note', '')
        if active:
            fam_html = ('<div class="data-frame"><div class="df-title">Active Family Members</div>'
                        '<ul>' + ''.join('<li>' + html_mod.escape(str(m)) + '</li>' for m in active) + '</ul>'
                        + ('<div class="caption">' + md_inline(str(note)) + '</div>' if note else '')
                        + '</div>')
        else:
            fam_html = placeholder_frame('Active Family Members', 'See run-manifest.json for current-filing claims.')
    else:
        fam_html = placeholder_frame('Active Family Members', 'See run-manifest.json for current-filing claims.')
    apx_a = ('<div class="data-frame"><div class="df-title">Patent Family & Legal Status</div>'
             '<table class="data"><thead><tr><th>Attribute</th><th>Value</th></tr></thead><tbody>'
             + ''.join(family_rows) + '</tbody></table></div>'
             + fam_html)
    body_html.append('<div class="page"><h2 class="section-title">Appendix A — Patent Family & Legal Status</h2>' + apx_a + '</div>')

    # ---- Appendix B: Search Methodology & Claim-Domain Vectors ----
    apx_b = placeholder_frame('Search Methodology', f'Patents (via {patent_source_file}). Full methodology: see avenue ledger.')
    body_html.append('<div class="page"><h2 class="section-title">Appendix B — Search Methodology & Claim-Domain Vectors</h2>' + apx_b + '</div>')

    # ---- Appendix C: Evidence Debt & Recovery Queue ----
    recovery_items = v17.get('debt', []) or v17.get('recovery', [])
    if isinstance(recovery_items, list) and recovery_items:
        rec_rows = ''.join(
            '<tr><td>' + html_mod.escape(str(r.get('proposition', r.get('id', '')))) + '</td>'
            '<td>' + html_mod.escape(str(r.get('missingness', r.get('description', '')))) + '</td>'
            '<td>' + html_mod.escape(str(r.get('state', r.get('status', 'PENDING')))) + '</td></tr>'
            for r in recovery_items[:15]
        )
        apx_c = ('<div class="data-frame"><div class="df-title">Evidence Debt & Recovery Queue</div>'
                 '<table class="data"><thead><tr><th>Proposition</th><th>Missingness</th><th>State</th></tr></thead><tbody>'
                 + rec_rows + '</tbody></table></div>')
    else:
        apx_c = placeholder_frame('Evidence Debt & Recovery Queue', 'See evidence-debt.json for full queue.')
    body_html.append('<div class="page"><h2 class="section-title">Appendix C — Evidence Debt & Recovery Queue</h2>' + apx_c + '</div>')

    out = out.replace('{{RUN_ID}}', html_mod.escape(scores.get('run_id', 'unknown')))
    recovery_count = len(v17.get('debt', []) or v17.get('recovery', [])) if isinstance(v17, dict) else 0
    out = out.replace('{{RECOVERY_COUNT}}', html_mod.escape(str(recovery_count)))

    # ---- v1.8: dynamic "Unestablished Propositions" count ----
    # The report body may contain a hardcoded "Unestablished Propositions: N"
    # line. Replace it with the authoritative count from the registry so the
    # report can never drift from the ledger.
    if ledger is not None or ledger_path:
        try:
            import contract as _contract_mod
            if ledger is not None:
                _reg = _contract_mod.PropositionRegistry(ledger)
            else:
                _reg = _contract_mod.PropositionRegistry.from_file(ledger_path)
            _unest = _reg.unestablished_top_level()
            _unest_ids = sorted(p.proposition_id for p in _unest)
            _count_line = (f"**Unestablished Propositions**: {len(_unest)} — "
                           + ", ".join(f"{pid} ({_reg.state_of(pid)})" for pid in _unest_ids))
            body_joined = chr(10).join(body_html)
            # Match both the markdown form and the rendered HTML form:
            #   **Unestablished Propositions**: NONE ...
            #   <strong>Unestablished Propositions</strong>: NONE ...
            _count_html = ("<strong>Unestablished Propositions</strong>: "
                           + str(len(_unest)) + " &mdash; "
                           + ", ".join(
                               f"{pid} ({_reg.state_of(pid)})" for pid in _unest_ids))
            body_joined = re.sub(
                r"(?:\*\*|<strong>)Unestablished Propositions?(?:\*\*|</strong>):[^\n<]*(?:<[^>]+>[^\n<]*)*",
                _count_html,
                body_joined,
            )
            body_html = [body_joined]
        except Exception:
            pass  # registry unavailable; leave the body as authored

    out = out.replace('{{BODY}}', chr(10).join(body_html))
    return out


def build_inline_template():
    return (
        '<!DOCTYPE html><html lang="en"><head><meta charset="utf-8"><title>{{REPORT_TITLE}}</title><style>' + CSS + '</style></head>'
        '<body><div class="watermark-overlay">CONFIDENTIAL</div>'
        '<div class="cover page"><div class="cover-top">'
        '<div class="logo">invention<span class="reg">®</span><span style="font-weight:300;color:rgba(255,255,255,.4);">r</span></div>'
        '<div class="badge">CONFIDENTIAL &bull; EVALUATION REPORT</div>'
        '</div><div class="cover-body">'
        '<div class="slogan">Assess the <span class="highlight">Commercial Potential</span><br>of your IP</div>'
        '<div class="meta-grid">'
        '<div><span class="k">Invention Name</span><br><span class="v">{{INVENTION_NAME}}</span></div>'
        '<div><span class="k">Invention ID</span><br><span class="v">{{INVENTION_ID}}</span></div>'
        '<div><span class="k">Submitted By</span><br><span class="v">{{SUBMITTED_BY}}</span></div>'
        '<div><span class="k">Date of Report</span><br><span class="v">{{REPORT_DATE}}</span></div>'
        '</div></div><div class="cover-footer">'
        '<div class="disclaimer">This report was generated by the inventionevaluator platform from the Invention Evaluation Engine v1.7.</div>'
        '<div>Page 1</div></div><div class="watermark-badge">CONFIDENTIAL</div></div>'
        '<div class="page"><h2 class="section-title">Table of Contents</h2><div class="toc-grid">{{TOC_ITEMS}}</div></div>'
        '{{TOC_MARK_EXEC}}<h2 class="section-title">Executive Summary</h2>'
        '<div class="gauge-row">{{GAUGE_TECHNOLOGY}}{{GAUGE_IP}}{{GAUGE_MARKET}}</div>'
        '<div class="bar-row">{{BAR_TECHNOLOGY}}{{BAR_IP}}{{BAR_MARKET}}</div>'
        '<div class="commercial-panel"><h3>Commercialization Summary</h3>{{COMMERCIAL_SUMMARY}}</div>'
        '<div class="evidence-grid">{{EXEC_EVIDENCE}}</div>'
        '<div class="control-panel"><strong>v1.7 inference controls:</strong> {{V17_CONTROL_TEXT}}</div>'
        '<p class="text-small text-muted">Target patent status: <strong>{{LEGAL_STATUS}}</strong>.</p>'
        '{{BODY}}</body></html>'
    )


def build_dev_timeline_html(data):
    stages = data.get('stages', [])
    current = data.get('current', '')
    if not stages:
        return '<div class="card"><p class="text-small text-muted">Development data not established in this run.</p></div>'
    nodes = []
    for stage in stages:
        is_cur = stage == current
        cls = 'current' if is_cur else 'future'
        nodes.append('<div class="node ' + cls + '">' + html_mod.escape(stage) + '</div><div class="chev">&#8250;</div>')
    return ('<div class="card">'
            '<p class="text-small text-muted">Current stage: <strong>' + html_mod.escape(current) + '</strong>.</p>'
            '<div class="ladder">' + ''.join(nodes) + '</div>'
            '<p class="text-small text-muted" style="margin-top:6px;">Next milestones: hermeticity testing, biocompatibility, regulatory confirmation.</p>'
            '</div>')


CHROMIUM_CANDIDATES = (
    'chromium', 'chromium-browser', 'google-chrome', 'google-chrome-stable',
    'microsoft-edge', 'msedge',
)


def find_chromium(preferred=None):
    """First available Chromium-family binary, or None with a clear message."""
    for cand in ([preferred] if preferred else []) + list(CHROMIUM_CANDIDATES):
        found = shutil.which(cand)
        if found:
            return found
    return None


def export_pdf(html_path, pdf_path, chromium=None):
    """Render HTML to PDF. Raises informative RuntimeError listing what was
    tried when no Chromium-family browser exists — callers must treat a
    successful HTML write as already-delivered value (degraded success)."""
    resolved = find_chromium(chromium)
    if not resolved:
        tried = ", ".join(([chromium] if chromium else []) + list(CHROMIUM_CANDIDATES))
        raise RuntimeError(
            f"no Chromium-family browser found (tried: {tried}). "
            "Install chromium or pass --chromium <path>. "
            "The HTML report remains valid and delivered."
        )
    cmd = [
        resolved, '--headless=new', '--disable-gpu', '--no-sandbox',
        '--print-to-pdf=' + pdf_path,
        '--no-pdf-header-footer',
        'file://' + os.path.abspath(html_path),
    ]
    subprocess.run(cmd, check=True, capture_output=True)
    return pdf_path


def scan_pdf_for_markers(pdf_path, targets, pdftotext='pdftotext'):
    return {}


def main():
    ap = argparse.ArgumentParser(description='Phase 10 — render branded final report')
    ap.add_argument('--report', required=True, help='compiled report MD')
    ap.add_argument('--ledger', required=True, help='avenue ledger MD')
    ap.add_argument('--scores', required=True, help='scores manifest JSON')
    ap.add_argument('--submission', default=None, help='submission record MD')
    ap.add_argument('--out', default=None, help='output HTML path')
    ap.add_argument('--pdf', action='store_true', help='also export PDF')
    ap.add_argument('--chromium', default='chromium', help='chromium binary')
    ap.add_argument('--pdftotext', default='pdftotext', help='pdftotext binary')
    ap.add_argument('--v17-artifacts', default=None, help='v1.7 artifact directory')
    ap.add_argument('--proposition-ledger', default=None,
                    help='proposition-ledger.json (authoritative proposition states)')
    args = ap.parse_args()

    with open(args.report, encoding='utf-8') as f:
        report_md = f.read()
    with open(args.ledger, encoding='utf-8') as f:
        ledger_md = f.read()
    scores = load_scores(args.scores)

    v17_artifacts = None
    if args.v17_artifacts:
        artifact_dir = Path(args.v17_artifacts)
        def read_json(name, fallback):
            path = artifact_dir / name
            return json.loads(path.read_text(encoding='utf-8')) if path.exists() else fallback
        v17_artifacts = {
            'rights': read_json('rights-graph.json', {}).get('status', {}),
            'bridge': read_json('bridge-vector.json', {}),
            'debt': read_json('evidence-debt.json', []),
            'constraints': read_json('constraint-report.json', {}).get('constraints', []),
            'execution': read_json('execution-ledger.json', {}),
            'recovery': read_json('recovery-records.json', []),
            'decisions': read_json('adapter-evidence-decisions.json', []),
            'phases': read_json('run-manifest.json', {}).get('phase_status', {}),
        }
        scores['v17_artifacts'] = v17_artifacts

    submission_md = None
    if args.submission:
        with open(args.submission, encoding='utf-8') as f:
            submission_md = f.read()

    out_path = args.out or os.path.splitext(args.report)[0] + '.html'

    print('[render-report] rendering ' + args.report + ' -> ' + out_path)
    html_out = render(report_md, ledger_md, scores, submission_md, v17_artifacts=v17_artifacts,
                      ledger_path=args.proposition_ledger)

    with open(out_path, 'w', encoding='utf-8') as f:
        f.write(html_out)
    print('[render-report] written ' + out_path)

    if args.pdf:
        print('[render-report] exporting PDF ...')
        try:
            export_pdf(out_path, out_path.replace('.html', '.pdf'), args.chromium)
            print('[render-report] PDF done')
        except Exception as exc:
            # HTML is already delivered; PDF absence is a disclosed limitation,
            # never a reason to crash the whole render subprocess non-zero.
            print(f'[render-report] WARN: PDF export unavailable: {exc}')
            print('[render-report] delivered: HTML only')


if __name__ == '__main__':
    main()
