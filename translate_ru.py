import os
import re
import time
from deep_translator import GoogleTranslator

# --- 配置 ---
SOURCE_LANG = 'auto' # 自动检测，或指定 'ru'
TARGET_LANG = 'en'
# 每次翻译暂停时间，防止被 Google 封 IP
SLEEP_TIME = 0.5 

translator = GoogleTranslator(source=SOURCE_LANG, target=TARGET_LANG)

def do_translate(text):
    if not text or not text.strip():
        return text
    # 如果全是符号、数字或看起来像代码变量（包含$），则跳过，防止破坏脚本
    if re.match(r'^[\W\d]+$', text) or '$' in text:
        return text
    
    try:
        # 翻译
        res = translator.translate(text)
        time.sleep(SLEEP_TIME)
        print(f"[OK] {text[:10]}... -> {res[:10]}...")
        return res
    except Exception as e:
        print(f"[Error] Translating '{text}': {e}")
        return text

def process_sh_file(file_path):
    print(f"Checking SH: {file_path}")
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    new_lines = []
    # 匹配 echo "内容" 或 echo '内容'
    echo_pattern = re.compile(r'(echo\s+(?:-e\s+)?["\'])(.*?)(["\'])')
    # 匹配注释 #，但在 #!/bin/bash 之后
    comment_pattern = re.compile(r'^(\s*#\s+)(?!/|!)(.*)')

    for line in lines:
        # 1. 处理注释
        match_comment = comment_pattern.match(line)
        if match_comment:
            prefix, content = match_comment.groups()
            translated = do_translate(content)
            new_lines.append(f"{prefix}{translated}\n")
            continue
        
        # 2. 处理 echo 字符串
        def replace_echo(match):
            prefix, content, suffix = match.groups()
            # 如果内容包含 $ 变量，Google Translate 可能会破坏它，这里选择跳过
            if '$' in content: 
                return match.group(0)
            translated = do_translate(content)
            return f"{prefix}{translated}{suffix}"
        
        line = echo_pattern.sub(replace_echo, line)
        new_lines.append(line)

    with open(file_path, 'w', encoding='utf-8') as f:
        f.writelines(new_lines)

def process_md_file(file_path):
    print(f"Checking MD: {file_path}")
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    new_lines = []
    in_code_block = False
    
    for line in lines:
        stripped = line.strip()
        # 识别代码块 ```
        if stripped.startswith('```'):
            in_code_block = not in_code_block
            new_lines.append(line)
            continue
        
        # 跳过代码块、空行、HTML、链接引用
        if in_code_block or not stripped or stripped.startswith('<') or stripped.startswith('['):
            new_lines.append(line)
            continue
            
        # 简单的 Markdown 文本提取 (处理标题、列表等前缀)
        prefix_match = re.match(r'^(\s*(?:#+|\-|\*|\d+\.|>)\s+)?(.*)', line)
        if prefix_match:
            prefix, content = prefix_match.groups()
            if prefix is None: prefix = ""
            translated = do_translate(content)
            new_lines.append(f"{prefix}{translated}\n")
        else:
            new_lines.append(line)

    with open(file_path, 'w', encoding='utf-8') as f:
        f.writelines(new_lines)

def main():
    # 排除目录
    exclude_dirs = ['.git', '.github']
    for root, dirs, files in os.walk("."):
        dirs[:] = [d for d in dirs if d not in exclude_dirs]
        
        for file in files:
            file_path = os.path.join(root, file)
            if file.endswith(".sh"):
                process_sh_file(file_path)
            elif file.lower() == "readme.md":
                process_md_file(file_path)

if __name__ == "__main__":
    main()
