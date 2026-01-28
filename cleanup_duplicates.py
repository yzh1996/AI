#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Remove duplicate function injections from index.html
"""

with open('templates/index.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Find all occurrences of the marker comment
marker = '// ==================== 配置管理函数（提前声明）===================='
occurrences = []
index = 0
while True:
    pos = content.find(marker, index)
    if pos == -1:
        break
    occurrences.append(pos)
    index = pos + 1

print(f'Found {len(occurrences)} instances of injected functions')

if len(occurrences) > 1:
    # Keep only the first occurrence, remove the rest
    # Find the end of each block (the closing of window.addEventListener)
    # Each block ends with "});\n" after the addEventListener

    # Strategy: Remove from the second marker to just before the first </script> tag
    # This will remove all duplicate blocks

    first_marker_pos = occurrences[0]
    second_marker_pos = occurrences[1]

    # Find the end of the first block (look for the pattern after addEventListener)
    # The block ends with the addEventListener closing
    search_start = first_marker_pos
    pattern = "        });\n"

    # Find the end of the first block
    end_pattern_pos = content.find(pattern, search_start)
    # Keep searching until we find the addEventListener closing
    count = 0
    while end_pattern_pos != -1 and count < 20:
        # Check if this is after "window.addEventListener('load'"
        check_back = content[max(0, end_pattern_pos-500):end_pattern_pos]
        if "window.addEventListener('load'" in check_back:
            first_block_end = end_pattern_pos + len(pattern)
            break
        end_pattern_pos = content.find(pattern, end_pattern_pos + 1)
        count += 1

    # Remove everything from second_marker_pos to just before first_block_end of the last block
    # Actually, simpler: remove from second marker to the end of the last block

    # Find where the last block ends (before the first </script>)
    script_end = content.find('</script>', second_marker_pos)

    # Remove from just before second marker (including whitespace) to just before </script>
    # Find the newline before second marker
    newline_before_second = content.rfind('\n', 0, second_marker_pos)

    # Remove the duplicate blocks
    cleaned_content = content[:newline_before_second+1] + content[script_end:]

    with open('templates/index.html', 'w', encoding='utf-8') as f:
        f.write(cleaned_content)

    print(f'Removed {len(occurrences)-1} duplicate blocks')
    print('HTML file cleaned successfully')
else:
    print('No duplicates found')
