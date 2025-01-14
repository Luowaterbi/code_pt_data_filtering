import os
import fasttext
import json
from pipeline.compute_quality_signals import ComputeCodeQualitySignal
from pipeline.compute_filtering import CodeFilter
import sys
import gzip
import tqdm
from multiprocessing import Manager, cpu_count, Pool
from functools import partial
import traceback

lang_predictor = fasttext.load_model(f'/home/i-luoxianzhen/code_pt_data_filtering/artifacts/lang_predictor.bin') # fasttext language predictor
ccqs = ComputeCodeQualitySignal()
code_filter = CodeFilter()


def test_fasttext():
    """
    之前fasttext总是爆numpy错误，测试一下能不能用
    可以用了，但是要将site-packages/fasttext/FastText.py的line239改成
    return labels, np.asarray(probs)
    """
    print(lang_predictor.predict("hello world"))
    print(lang_predictor.predict("你好，世界"))
    print(lang_predictor.predict("print('hello world')"))
    print(lang_predictor.predict("print('你好，世界')"))


def get_all_file_paths(raw_dir):
    """
    获取raw_dir下所有文件的路径
    """
    files = os.listdir(raw_dir)
    file_paths = [os.path.join(raw_dir, f) for f in tqdm.tqdm(files, desc="Get All Files:") if f.endswith(".json")]
    return file_paths

def compute_qs(row, ccqs: ComputeCodeQualitySignal):
    final_result = ccqs.evaluate(
                    text=row['text'],
                    filename=row['filename'],
                    lang=row['lang'],
                    ext=row['ext'],
                    file_size_in_byte=row['file_size_in_byte'],
                    program_lang=row['program_lang'],
                    doc_type=row['doc_type'],
                )
    return final_result


def filter_code(row, code_filter: CodeFilter):

    final_result = code_filter.evaluate(
                    doc_type=row['doc_type'],
                    lang=row['lang'],
                    program_lang=row['program_lang'],
                    quality_signal=row['quality_signal']
                )

    return final_result


def filter(file_path, save_json, lock):
    data = json.load(open(file_path, "r"))
    for d in data:
        d["text"] = d["content"]
        try:
            predictions = lang_predictor.predict(d["text"].lower().replace("\n", " "))
            d["lang"] = predictions[0][0].replace('__label__', '')
            final_result = compute_qs(d, ccqs)
            d["quality_signal"] = json.loads(final_result)["quality_signal"]
            d["filtered_result"] = json.loads(filter_code(d, code_filter))
            if d["filtered_result"]["effective"] == "1":
                with lock:
                    del d["text"], d["quality_signal"], d["filtered_result"]
                    save_json.append(d)
                    if len(save_json) > 100 * 1000:
                        print("Save json!")
                        output_path = f"/mnt/shared-storage/users/xzluo/filtered_data/{len(os.listdir('/mnt/shared-storage/users/xzluo/filtered_data/'))}.json"
                        json.dump(list(save_json), open(output_path, "w"), indent=4)
                        save_json[:] = []
        except Exception as e:
            print(f"Error: {e}")
            print(traceback.format_exc())
            continue
                

if __name__ == "__main__":
    raw_dir = "/mnt/shared-storage/users/luoxianzhen/"
    file_paths = get_all_file_paths(raw_dir)
    # file_paths = file_paths[:10]
    print(f"Total {len(file_paths)} files")

    manager = Manager()
    save_json = manager.list()
    write_lock = manager.Lock()
    work = partial(filter, save_json=save_json, lock=write_lock)
    with Pool(cpu_count()) as p:
        for _ in tqdm.tqdm(p.imap_unordered(work, file_paths), total=len(file_paths)):
            pass
    if save_json:
        output_path = f"/mnt/shared-storage/users/xzluo/filtered_data/{len(os.listdir('/mnt/shared-storage/users/xzluo/filtered_data/'))}.json"
        json.dump(save_json, open(output_path, "w"))
    