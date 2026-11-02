"""Apply Simplified Chinese display text to the original webpack bundle."""
import json
import pathlib
import re
import shutil

ROOT = pathlib.Path(__file__).resolve().parent
BACKUP = ROOT / '.localization-backup'
BACKUP.mkdir(exist_ok=True)
if (BACKUP / 'manifest.json').exists():
    (BACKUP / 'manifest.json').rename(BACKUP / 'manifest.json.original')
for filename in ('index.js', 'index.html', 'manifest.json'):
    backup_name = 'manifest.json.original' if filename == 'manifest.json' else filename
    if not (BACKUP / backup_name).exists():
        shutil.copy2(ROOT / filename, BACKUP / backup_name)

TEXT = {
    'Quick Align': '快速排列',
    'Reset Plugin State': '重置插件设置',
    'General Settings': '常规设置', 'Duplicate': '复制', 'Align': '对齐',
    'Stack': '堆叠排列', 'Fit Size': '适配尺寸', 'Move to Corners': '移至四角',
    'Move To Corners': '移至四角', 'Swap': '交换位置', 'Arrange Circular': '环形排列',
    'Layer Order': '图层排序', 'by Position on Canvas': '按画布中的位置',
    'by Order in Layer Panel': '按图层面板中的顺序', 'Quick Access': '快捷操作',
    'Auto-Close Sections': '自动折叠其他分区', 'Show Advanced Options': '显示高级选项',
    'Show Sections': '显示功能分区', 'Padding': '内边距', 'Gap': '间距',
    'Align To Canvas': '对齐到画布', 'Copies': '副本数量', 'Keep Position': '保持原位',
    'Lock Other Axis': '锁定另一轴位置', 'Shrink': '缩小以适应', 'Wrap': '自动换行',
    'Keep Aspect Ratio': '保持宽高比', 'Move fully inside': '完全移入边界内',
    'Range': '角度范围', 'Start': '起始角度', 'Radius': '半径', 'Alignment': '对齐方式',
    'Center': '圆心', 'Pick Center': '拾取圆心', 'Doc Center': '画布中心',
    'Rotate Elements': '随圆周旋转图层', 'center': '居中', 'outside': '圆外', 'inside': '圆内',
    'Align Left': '左对齐', 'Align Center X': '水平居中', 'Align Right': '右对齐',
    'Align Top': '顶对齐', 'Align Center Y': '垂直居中', 'Align Bottom': '底对齐',
    'Align Center': '水平垂直居中', 'Align Top Left': '左上对齐', 'Align Top Right': '右上对齐',
    'Align Bottom Right': '右下对齐', 'Align Bottom Left': '左下对齐', 'Align Baseline': '基线对齐',
    'Align Space Between X': '水平等间距分布（两端贴边）',
    'Align Space Evenly X': '水平等间距分布（含两端）',
    'Align Space Around X': '水平等间距分布（两端半间距）',
    'Align Space Between Y': '垂直等间距分布（两端贴边）',
    'Align Space Evenly Y': '垂直等间距分布（含两端）',
    'Align Space Around Y': '垂直等间距分布（两端半间距）',
    'Stack Left': '纵向堆叠（左对齐）', 'Stack Center X': '纵向堆叠（水平居中）',
    'Stack Right': '纵向堆叠（右对齐）', 'Stack Top': '横向堆叠（顶对齐）',
    'Stack Center Y': '横向堆叠（垂直居中）', 'Stack Bottom': '横向堆叠（底对齐）',
    'Fit Width': '适配宽度', 'Fit Height': '适配高度', 'Fit to Width': '适配宽度',
    'to Corners (TopLeft)': '移至四角（从左上开始）',
    'to Corners (TopRight)': '移至四角（从右上开始）',
    'to Corners (BottomRight)': '移至四角（从右下开始）',
    'to Corners (BottomLeft)': '移至四角（从左下开始）',
    'To Corners (Start Top Left)': '移至四角（从左上开始）',
    'Swap X Positions': '交换水平位置', 'Swap Y Positions': '交换垂直位置',
    'Swap Positions': '交换位置',
    'An unexpected error occured': '发生意外错误',
    'Reset plugin and reload': '重置插件并重新加载',
    '(Plugin command)': '（插件操作）', 'Waiting for plugin command...': '正在执行插件操作…',
    'top': '上', 'left': '左', 'right': '右', 'bottom': '下',
}

def zh(value):
    return json.dumps(TEXT[value], ensure_ascii=False)

changed = []
def transform(match):
    source = json.loads(match[1])
    name = source.split('sourceURL=')[-1].strip()
    original = source
    if '/src/' in name:
        # Translate display properties only; command keys and saved enum values stay intact.
        def prop(m):
            return m[1] + zh(m[3]) if m[3] in TEXT else m[0]
        source = re.sub(r'((?:\btext|\blabel|\bheading|\bplaceholder):\s*)([\x27"])([^\x27"\n]*)\2', prop, source)
        source = re.sub(r'(, null, )([\x27"])([^\x27"\n]*)\2', prop, source)
        source = source.replace('}, "Reset plugin and reload")', '}, ' + zh('Reset plugin and reload') + ')')
        if '/PanelSection.tsx?' in name:
            source = source.replace(', null, heading)', ', null, quickAlignZh(heading))')
        if '/SPDropdown.tsx?' in name:
            source = source.replace('return selectedOption;', 'return quickAlignZh(selectedOption);')
            source = source.replace('return optionLabels && optionLabels[options.indexOf(opt)] || opt;', 'return quickAlignZh(optionLabels && optionLabels[options.indexOf(opt)] || opt);')
            source = source.replace('}, optionLabels && optionLabels[i] ? optionLabels[i] : opt)', '}, quickAlignZh(optionLabels && optionLabels[i] ? optionLabels[i] : opt))')
        if '/flyout-menu.tsx?' in name:
            source = source.replace('...otherProps,', '...otherProps,\n            label: quickAlignZh(otherProps.label),')
        if '/plugin-helpers.tsx?' in name:
            source = source.replace('label: type,', 'label: quickAlignZh(type),')
            source = source.replace('        label,', '        label: quickAlignZh(label),')
        if '/LayerPos.tsx?' in name:
            # Localize history display names without changing metadata / action dispatch keys.
            source = source.replace('`Duplicate ${opt.duplicates}x`', '`复制 ${opt.duplicates} 份`')
        if '/helpers.tsx?' in name:
            source = source.replace('historyName = "(Plugin command)"', 'historyName = ' + zh('(Plugin command)'))
            source = source.replace('commandName = "Waiting for plugin command..."', 'commandName = ' + zh('Waiting for plugin command...'))
            source = source.replace('"name": historyName,', '"name": quickAlignZh(historyName),')
    if '/uxp/manifest.json?' in name:
        source = 'module.exports = ' + json.dumps(manifest, ensure_ascii=False) + ';\n\n//# sourceURL=webpack:///./uxp/manifest.json?'
    if source != original:
        changed.append(name)
        return 'eval(' + json.dumps(source, ensure_ascii=False) + ');'
    return match[0]

manifest = json.loads((BACKUP / 'manifest.json.original').read_text(encoding='utf-8'))
manifest['name'] = '快速排列（Quick Align）'
for entry in manifest['entrypoints']:
    entry['label']['default'] = TEXT[entry['label']['default']]
(ROOT / 'manifest.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')

bundle = (BACKUP / 'index.js').read_text(encoding='utf-8')
bundle = re.sub(r'eval\(("(?:[^"\\]|\\.)*")\);', transform, bundle)
helper = ('// Simplified Chinese display localization; internal command IDs remain unchanged.\n'
          'var quickAlignZhText = ' + json.dumps(TEXT, ensure_ascii=False, indent=2) + ';\n'
          'function quickAlignZh(value) {\n'
          '    if (typeof value !== "string") return value;\n'
          '    if (Object.prototype.hasOwnProperty.call(quickAlignZhText, value)) return quickAlignZhText[value];\n'
          '    return value.replace(/^Point (\\d+)$/, "取样点 $1");\n'
          '}\n')
(ROOT / 'index.js').write_text(helper + bundle, encoding='utf-8')
html = (BACKUP / 'index.html').read_text(encoding='utf-8')
html = html.replace('<html>', '<html lang="zh-CN">').replace('<head>', '<head>\n    <meta charset="UTF-8">\n    <title>快速排列</title>')
(ROOT / 'index.html').write_text(html, encoding='utf-8')
print('Localized modules:', len(changed))
for name in changed:
    print(name)
