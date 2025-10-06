#!/usr/bin/env python3
"""
Unicode Character Fixer for CMD Compatibility
Removes emojis and Unicode box characters from all Python scripts
"""

import os
import re
from pathlib import Path

def fix_unicode_in_file(file_path):
    """Remove Unicode characters and emojis from a Python file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Replace Unicode box characters with ASCII
        unicode_replacements = {
            '╔': '=',
            '╗': '=',
            '╚': '=',
            '╝': '=',
            '║': ' ',
            '═': '=',
            '╠': '=',
            '╣': '=',
            '╦': '=',
            '╩': '=',
            '╬': '='
        }
        
        # Replace emoji patterns with text labels
        emoji_replacements = {
            '🎓': '[SCHOOL]',
            '🚀': '[START]',
            '📦': '[PACKAGE]',
            '🗄️': '[DATABASE]',
            '🔄': '[RESET]',
            '🧪': '[TEST]',
            '🛠️': '[FIX]',
            '📊': '[HEALTH]',
            '❌': '[ERROR]',
            '✅': '[OK]',
            '⚠️': '[WARN]',
            '💡': '[TIP]',
            '🔍': '[CHECK]',
            '🐍': '[PYTHON]',
            '🌐': '[NETWORK]',
            '💾': '[MEMORY]',
            '📁': '[FOLDER]',
            '🔧': '[TOOL]',
            '📋': '[LIST]',
            '🎉': '[SUCCESS]',
            '🛑': '[STOP]',
            '🚫': '[BLOCKED]',
            '📍': '[LOCATION]',
            '⏳': '[WAIT]',
            '🧹': '[CLEAN]',
            '📥': '[DOWNLOAD]',
            '📤': '[UPLOAD]',
            '🔒': '[SECURE]',
            '🖥️': '[COMPUTER]',
            '📈': '[CHART]',
            '🎯': '[TARGET]',
            '💻': '[SYSTEM]',
            '🌟': '[STAR]',
            '⭐': '[STAR]',
            '🔥': '[HOT]',
            '💪': '[STRONG]',
            '👍': '[GOOD]',
            '👎': '[BAD]',
            '🎪': '[CIRCUS]',
            '🎨': '[ART]',
            '🎵': '[MUSIC]',
            '🎬': '[MOVIE]',
            '🎮': '[GAME]',
            '🏆': '[TROPHY]',
            '🏅': '[MEDAL]',
            '🎖️': '[AWARD]',
            '🏃': '[RUN]',
            '🚶': '[WALK]',
            '🧑‍💻': '[DEVELOPER]',
            '👨‍💻': '[DEVELOPER]',
            '👩‍💻': '[DEVELOPER]',
            '🤖': '[ROBOT]',
            '🔬': '[SCIENCE]',
            '🧬': '[DNA]',
            '⚡': '[FAST]',
            '🌈': '[RAINBOW]',
            '☀️': '[SUN]',
            '🌙': '[MOON]',
            '⭐': '[STAR]',
            '🌍': '[EARTH]',
            '🌎': '[EARTH]',
            '🌏': '[EARTH]'
        }
        
        # Apply Unicode replacements
        for unicode_char, replacement in unicode_replacements.items():
            content = content.replace(unicode_char, replacement)
        
        # Apply emoji replacements
        for emoji, replacement in emoji_replacements.items():
            content = content.replace(emoji, replacement)
        
        # Remove any remaining emoji characters using regex
        emoji_pattern = re.compile(
            "["
            "\U0001F600-\U0001F64F"  # emoticons
            "\U0001F300-\U0001F5FF"  # symbols & pictographs
            "\U0001F680-\U0001F6FF"  # transport & map symbols
            "\U0001F1E0-\U0001F1FF"  # flags (iOS)
            "\U00002702-\U000027B0"
            "\U000024C2-\U0001F251"
            "]+", flags=re.UNICODE)
        
        content = emoji_pattern.sub('[EMOJI]', content)
        
        # Write back the cleaned content
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        return True
        
    except Exception as e:
        print(f"Error fixing {file_path}: {e}")
        return False

def main():
    """Fix all Python files in ImpScripts directory"""
    script_dir = Path(__file__).parent
    
    print("[INFO] Fixing Unicode characters in Python scripts...")
    
    python_files = list(script_dir.glob("*.py"))
    fixed_count = 0
    
    for py_file in python_files:
        if py_file.name == "fix_unicode.py":  # Skip this script
            continue
            
        print(f"[FIX] Processing {py_file.name}...")
        if fix_unicode_in_file(py_file):
            fixed_count += 1
            print(f"[OK] Fixed {py_file.name}")
        else:
            print(f"[ERROR] Failed to fix {py_file.name}")
    
    print(f"\n[COMPLETE] Fixed {fixed_count} Python files")
    print("[INFO] All scripts should now be CMD compatible!")

if __name__ == "__main__":
    main()