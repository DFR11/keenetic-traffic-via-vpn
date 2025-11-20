import os
import re
import time
from deep_translator import GoogleTranslator

# --- 配置 ---
SOURCE_LANG = 'auto' 
TARGET_LANG = 'en'
SLEEP_TIME = 0.5 

translator = GoogleTranslator(source=SOURCE_LANG, target=TARGET_LANG)

def do_translate(text):
    if not text or not text.strip():
        return text
    # 仅跳过纯符号或纯数字
    if re.match(r'^[\W\d]+$', text):
        return text
    
    try:
        # 简单的保护：如果包含路径 /opt/ 或 IP地址，尽量不翻译（可选）
        if '/opt/' in text or re.search(r'\d+\.\d+\.\d+\.\d+', text):
            print(f"  [Skip] Path/IP detected: {text[:15]}...")
            return text

        res = translator.translate(text)
        time.sleep(SLEEP_TIME)
        # 简单的回显，防止日志过大，截取前20字符
        print(f"  [Trans] '{text[:20]}...' -> '{res[:20]}...'")
        return res
    except Exception as e:
        print(f"  [Error] Translating '{text}': {e}")
        return text

def read_file_content(file_path):
    """尝试多种编码读取文件"""
    encodings = ['utf-8', 'windows-1251', 'cp1251', 'latin1']
    for enc in encodings:
        try:
            with open(file_path, 'r', encoding=enc) as f:
                content = f.readlines()
            print(f"Opened {file_path} with encoding: {enc}")
            return content, enc
        except UnicodeDecodeError:
            continue
    print(f"[Fail] Could not determine encoding for {file_path}")
    return None, None

def process_sh_file(file_path):
    print(f"Processing SH: {file_path}")
    lines, encoding = read_file_content(file_path)
    if not lines:
        return

    new_lines = []
    modified = False

    # 1. 匹配字符串：支持 echo, printf, logger, log
    # 匹配双引号或单引号中的内容
    string_pattern = re.compile(r'((?:echo|printf|logger|log)\s+(?:-[a-zA-Z]+\s+)?["\'])(.*?)(["\'])')
    
    # 2. 匹配注释：支持行首 # 和 行内 # (前提是 # 前面有空格，避免匹配到 url 中的 #)
    # group(1) 是 # 前面的内容, group(2) 是 # 及其后空格, group(3) 是注释内容
    comment_pattern = re.compile(r'^(.*?)(#\s+)(.*)$')

    for line in lines:
        original_line = line
        
        # --- 处理注释 ---
        # 排除 shebang #!/bin/...
        if not line.strip().startswith("#!"):
            match_comment = comment_pattern.match(line)
            if match_comment:
                pre, hash_mark, content = match_comment.groups()
                # 只有当内容包含俄语字符时才翻译 (简单的西里尔字母判断)
                if re.search(r'[а-яА-Я]', content):
                    trans_content = do_translate(content)
                    line = f"{pre}{hash_mark}{trans_content}\n"
                    modified = True
        
        # --- 处理命令字符串 (echo等) ---
        # 如果这一行已经被注释处理过，用处理过的 line 继续匹配字符串
        def replace_str(match):
            prefix, content, suffix = match.groups()
            # 包含西里尔字母才翻译
            if re.search(r'[а-яА-Я]', content):
                nonlocal modified
                modified = True
                return f"{prefix}{do_translate(content)}{suffix}"
            return match.group(0)

        line = string_pattern.sub(replace_str, line)
        
        new_lines.append(line)

    if modified:
        print(f"Saving changes to {file_path}")
        with open(file_path, 'w', encoding=encoding) as f:
            f.writelines(new_lines)
    else:
        print(f"No Russian content found or translated in {file_path}")

def process_md_file(file_path):
    print(f"Processing MD: {file_path}")
    lines, encoding = read_file_content(file_path)
    if not lines:
        return

    new_lines = []
    in_code_block = False
    modified = False
    
    for line in lines:
        stripped = line.strip()
        if stripped.startswith('```'):
            in_code_block = not in_code_block
            new_lines.append(line)
            continue
        
        # 跳过代码块、空行、HTML
        if in_code_block or not stripped or stripped.startswith('<'):
            new_lines.append(line)
            continue
            
        # 只有包含西里尔字母才尝试翻译
        if re.search(r'[а-яА-Я]', line):
            # 简单处理：保留 Markdown 前缀
            prefix_match = re.match(r'^(\s*(?:#+|\-|\*|\d+\.|>)\s+)?(.*)', line)
            if prefix_match:
                prefix, content = prefix_match.groups()
                if prefix is None: prefix = ""
                translated = do_translate(content)
                new_lines.append(f"{prefix}{translated}\n")
                modified = True
                continue

        new_lines.append(line)

    if modified:
        with open(file_path, 'w', encoding=encoding) as f:
            f.writelines(new_lines)

def main():
    exclude_dirs = ['.git', '.github']
    # 目标文件扩展名，针对路由器脚本增加 .conf 或无后缀文件的判断逻辑比较复杂，
    # 这里主要针对 .sh 和 .md，如果你的脚本没有后缀，需要修改 logic。
    target_exts = ['.sh', '.cfg', '.conf'] 
    
    for root, dirs, files in os.walk("."):
        dirs[:] = [d for d in dirs if d not in exclude_dirs]
        
        for file in files:
            file_path = os.path.join(root, file)
            
            if any(file.endswith(ext) for ext in target_exts):
                process_sh_file(file_path)
            elif file.lower() == "readme.md":
                process_md_file(file_path)

if __name__ == "__main__":
    main()
