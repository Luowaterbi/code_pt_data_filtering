import hashlib
import os
import zipfile
import pandas as pd
from pathlib import Path
from io import BytesIO
import magic  # 需要安装 libmagic，使用 pip install python-magic
from docx import Document
from multiprocessing import Manager, Pool, cpu_count
import fasttext
from utils.preprocessing import get_program_lang, get_doc_type
import traceback
import csv
from functools import partial
import json
from tqdm import tqdm


# 定义需要排除的扩展名
EXCLUDED_EXTS = {
    "tar", "zip", "rar", "gz", "mp3", "7z",
    "exe", "dll", "jar", "png", "svg", "wav",
    "gif", "jpeg", "ppt", "pptx", "xlsx", "xls", "pdf"
}

def is_video_ts(file_bytes):
    """
    判断 ts 文件是否为视频文件。通过读取文件头的特征符号进行判断。
    这里只是一个简单的示例，实际情况可能需要更复杂的判断。
    """
    # 典型的 TS 文件开始字节为 0x47
    return file_bytes.startswith(b'\x47')

def extract_docx_content(file_bytes):
    """
    从 docx 文件中提取文本内容。
    """
    try:
        doc = Document(BytesIO(file_bytes))
        fullText = []
        for para in doc.paragraphs:
            fullText.append(para.text)
        return '\n'.join(fullText)
    except Exception as e:
        return ""

MAX_FILE_SIZE = 8 * 1024 * 1024  # 8 MB
MAX_NON_TEXT_FILE_SIZE = 1 * 1024 * 1024  # 1 MB
# lang_predictor = fasttext.load_model(f'/home/i-luoxianzhen/code_pt_data_filtering/artifacts/lang_predictor.bin') # fasttext language predictor

def process_zip(zip_path, seen_hashes, lock):
    """
    处理单个 zip 文件，返回符合条件的文件信息列表。
    """
    # 获取zip_path最后的文件夹
    date = Path(zip_path).parent.name
    repo_name = Path(zip_path).stem
    results = []
    try:
        with zipfile.ZipFile(zip_path, 'r') as z:
            # print("processing", zip_path)
                
            for zip_info in z.infolist():
                if zip_info.is_dir():
                    continue
                
                file_path = zip_info.filename
                filename = Path(file_path).name
                ext = Path(file_path).suffix.lower().lstrip('.')
                file_size = zip_info.file_size

                # 过滤文件大小
                if file_size > MAX_FILE_SIZE:
                    # print("Too Large File", file_size)
                    continue

                # 过滤指定扩展名
                if ext in EXCLUDED_EXTS:
                    # print("Excluded File", ext)
                    continue

                # 处理无扩展名的文件
                if not ext:
                    if file_size > MAX_NON_TEXT_FILE_SIZE:
                        # print("Non-Text File Too Large", file_size)
                        continue

                # 读取文件内容
                try:
                    with z.open(zip_info) as file:
                        file_bytes = file.read()
                except Exception as e:
                    traceback.print_exc()
                    print(e)
                    # print("Error reading file", file_path)
                    continue  # 如果文件无法读取，跳过

                # 特殊处理 ts 文件
                if ext == 'ts':
                    if is_video_ts(file_bytes):
                        # print("Video File", file_path)
                        continue
                
                file_hash = compute_hash(file_bytes)
                # 实时去重
                with lock:
                    if file_hash in seen_hashes:
                        # print("Duplicate File", file_path)
                        continue
                    seen_hashes[file_hash] = True  # 添加到哈希集合

                # 特殊处理 docx 文件
                if ext == 'docx':
                    content = extract_docx_content(file_bytes)
                else:
                    # 尝试解码为文本
                    try:
                        content = file_bytes.decode('utf-8', errors='replace')
                    except:
                        # print("Error decoding file", file_path)
                        continue

                # predictions = lang_predictor.predict(content.lower().replace("\n", " "))
                # lang = predictions[0][0].replace('__label__', '')
                # programming language
                program_lang = get_program_lang(filename, ext)

                # documentation type
                doc_type = get_doc_type(program_lang)

                
                results.append({
                    'repo_name': repo_name,
                    'file_path': file_path,
                    'filename': filename,
                    'content': content,
                    'ext': ext,
                    'file_size_in_byte': file_size,
                    # 'lang': lang,
                    'program_lang': program_lang,
                    'doc_type': doc_type,
                    'hash': file_hash,
                    'zip_path': zip_path
                })
    except zipfile.BadZipFile:
        print(f"Bad zip file: {zip_path}")
    except Exception as e:
        traceback.print_exc()
        print(f"Error processing {zip_path}: {e}")
    if not results:
        print(f"No files found in {zip_path}")
    else:
        json.dump(results, open(f"/mnt/shared-storage/users/luoxianzhen/{date}_{repo_name}.json", "w"))
        for r in results:
            del r['content']
        with lock:
            append_results_to_csv(output_csv, results)
    return results


def compute_hash(file_bytes):
    """
    计算文件内容的 SHA-256 哈希值。
    """
    sha256 = hashlib.sha256()
    sha256.update(file_bytes)
    return sha256.hexdigest()


def get_all_zips(dir_start=0, dir_end=200):
    input_path = "/mnt/spark-temp/github_repo_code/"
    sub_dirs = [os.path.join(input_path, d) for d in os.listdir(input_path)]
    sub_dirs = [d for d in sub_dirs if os.path.isdir(d)]
    sub_dirs.sort(reverse=True)
    sub_dirs = sub_dirs[dir_start:dir_end]
    return sub_dirs

def append_results_to_csv(output_csv, files):
    """
    将文件信息追加到 CSV 文件中。
    """
    if not files:
        return
    write_header = not os.path.exists(output_csv)
    with open(output_csv, 'a', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['repo_name', 'file_path', 'filename', 'ext', 'file_size_in_byte', 'program_lang', 'doc_type','hash','zip_path']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        if write_header:
            writer.writeheader()
        for file in files:
            writer.writerow(file)


def load_existing(output_csv):
    """
    从已有的 CSV 文件中加载已存在的哈希值和zip文件。
    """
    if not os.path.exists(output_csv):
        return dict(), dict()
    df = pd.read_csv(output_csv, usecols=['hash', 'zip_path'], dtype=str)
    return {row['hash']: True for _, row in df.iterrows() if pd.notna(row['hash'])}, {}
    # {row['zip_path']: True for _, row in df.iterrows() if pd.notna(row['zip_path'])}


if __name__ == "__main__":
    sub_dirs = get_all_zips(30, 60)
    print("sub_dirs", sub_dirs)
    zip_files = [os.path.join(sub_dir, f) for sub_dir in sub_dirs for f in os.listdir(sub_dir)]
    output_csv = '/mnt/shared-storage/users/luoxianzhen/output.csv'
    already_hashes, already_zips = load_existing(output_csv)
    # 过滤已经处理过的 zip 文件
    # zip_files_to_process = [z for z in zip_files if z not in already_zips]
    zip_files_to_process = zip_files
    total_zips = len(zip_files_to_process)
    print(f"{len(already_hashes)} have processed , rest zip files to process: {total_zips}")
    if total_zips >= 0:
        manager = Manager()
        seen_hashes = manager.dict()
        write_lock = manager.Lock()

        seen_hashes.update(already_hashes)

        worker = partial(process_zip, seen_hashes=seen_hashes, lock=write_lock)
        with Pool(cpu_count()) as pool:
            for _ in tqdm(pool.imap_unordered(worker, zip_files_to_process), total=total_zips):
                if _:
                    print(f"{_[0]['repo_name']} processed, {len(_)} files found.")

    print("All zip files have been processed.")