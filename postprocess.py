from datasets import load_dataset,concatenate_datasets
import json
import os
from multiprocessing import freeze_support
from minhash_deduplication import DuplicationIndex, deduplicate_dataset


def get_all_json(raw_dir):
    """
    获取raw_dir下所有文件的路径
    """
    files = os.listdir(raw_dir)
    file_paths = [os.path.join(raw_dir, f) for f in files if f.endswith(".json")]
    return file_paths

def save_jsonl(dataset,file_path):
    with open(file_path,"w",encoding="utf-8") as jsonl_file:
        for data in dataset:
            json_line=json.dumps(data)
            jsonl_file.write(json_line+"\n")

if __name__ == "__main__":
    raw_dir = "/mnt/shared-storage/users/xzluo/filtered_data"
    save_dir = "/mnt/shared-storage/users/xzluo/dedup/"
    file_paths = get_all_json(raw_dir)
    print(file_paths)
    ds = concatenate_datasets([load_dataset("json", data_files=file_path, split="train", cache_dir="/mnt/shared-storage/users/xzluo/huggingface/datasets") for file_path in file_paths])
    ds = ds.rename_column("file_path", "path")
    print("Datasets Has", len(ds))

    duplication_index = DuplicationIndex()
    freeze_support()
    # Todo：继承之前的index和cluster还没有完全实现，目前有点bug
    # 在于新dataset的index会从0开始，跟之前的内容重复
    ds_filter, duplicate_clusters = deduplicate_dataset(ds, duplication_index)

    duplicate_clusters_path = os.path.join(save_dir, "duplicate_clusters.json")
    if os.path.exists(duplicate_clusters_path):
        already = json.load(open(duplicate_clusters_path, "r"))
        duplicate_clusters.extend(already)
    json.dump(duplicate_clusters, open(duplicate_clusters_path, "w"), indent=4)
    
    file_jsonls = [f for f in os.listdir(save_dir) if f.endswith(".jsonl")]
    file_number = len(file_jsonls)
    for index in range(0, len(ds_filter), 100000):
        file_path = os.path.join(save_dir, f"file-{file_number+1}.jsonl")
        end_index = min(len(ds_filter), index + 100000)
        save_jsonl(ds_filter.select(list(range(index, end_index))), file_path)
        file_number += 1


# ['/mnt/shared-storage/users/xzluo/filtered_data/0.json', '/mnt/shared-storage/users/xzluo/filtered_data/1.json', '/mnt/shared-storage/users/xzluo/filtered_data/10.json', '/mnt/shared-storage/users/xzluo/filtered_data/11.json', '/mnt/shared-storage/users/xzluo/filtered_data/12.json', '/mnt/shared-storage/users/xzluo/filtered_data/13.json', '/mnt/shared-storage/users/xzluo/filtered_data/14.json', '/mnt/shared-storage/users/xzluo/filtered_data/15.json', '/mnt/shared-storage/users/xzluo/filtered_data/16.json', '/mnt/shared-storage/users/xzluo/filtered_data/17.json', '/mnt/shared-storage/users/xzluo/filtered_data/18.json', '/mnt/shared-storage/users/xzluo/filtered_data/19.json', '/mnt/shared-storage/users/xzluo/filtered_data/2.json', '/mnt/shared-storage/users/xzluo/filtered_data/20.json', '/mnt/shared-storage/users/xzluo/filtered_data/21.json', '/mnt/shared-storage/users/xzluo/filtered_data/22.json', '/mnt/shared-storage/users/xzluo/filtered_data/23.json', '/mnt/shared-storage/users/xzluo/filtered_data/24.json', '/mnt/shared-storage/users/xzluo/filtered_data/25.json', '/mnt/shared-storage/users/xzluo/filtered_data/26.json', '/mnt/shared-storage/users/xzluo/filtered_data/27.json', '/mnt/shared-storage/users/xzluo/filtered_data/28.json', '/mnt/shared-storage/users/xzluo/filtered_data/29.json', '/mnt/shared-storage/users/xzluo/filtered_data/3.json', '/mnt/shared-storage/users/xzluo/filtered_data/30.json', '/mnt/shared-storage/users/xzluo/filtered_data/31.json', '/mnt/shared-storage/users/xzluo/filtered_data/32.json', '/mnt/shared-storage/users/xzluo/filtered_data/33.json', '/mnt/shared-storage/users/xzluo/filtered_data/34.json', '/mnt/shared-storage/users/xzluo/filtered_data/35.json', '/mnt/shared-storage/users/xzluo/filtered_data/36.json', '/mnt/shared-storage/users/xzluo/filtered_data/37.json', '/mnt/shared-storage/users/xzluo/filtered_data/38.json', '/mnt/shared-storage/users/xzluo/filtered_data/39.json', '/mnt/shared-storage/users/xzluo/filtered_data/4.json', '/mnt/shared-storage/users/xzluo/filtered_data/40.json', '/mnt/shared-storage/users/xzluo/filtered_data/41.json', '/mnt/shared-storage/users/xzluo/filtered_data/42.json', '/mnt/shared-storage/users/xzluo/filtered_data/43.json', '/mnt/shared-storage/users/xzluo/filtered_data/44.json', '/mnt/shared-storage/users/xzluo/filtered_data/45.json', '/mnt/shared-storage/users/xzluo/filtered_data/46.json', '/mnt/shared-storage/users/xzluo/filtered_data/47.json', '/mnt/shared-storage/users/xzluo/filtered_data/48.json', '/mnt/shared-storage/users/xzluo/filtered_data/49.json', '/mnt/shared-storage/users/xzluo/filtered_data/5.json', '/mnt/shared-storage/users/xzluo/filtered_data/50.json', '/mnt/shared-storage/users/xzluo/filtered_data/51.json', '/mnt/shared-storage/users/xzluo/filtered_data/52.json', '/mnt/shared-storage/users/xzluo/filtered_data/53.json', '/mnt/shared-storage/users/xzluo/filtered_data/54.json', '/mnt/shared-storage/users/xzluo/filtered_data/55.json', '/mnt/shared-storage/users/xzluo/filtered_data/56.json', '/mnt/shared-storage/users/xzluo/filtered_data/57.json', '/mnt/shared-storage/users/xzluo/filtered_data/58.json', '/mnt/shared-storage/users/xzluo/filtered_data/59.json', '/mnt/shared-storage/users/xzluo/filtered_data/6.json', '/mnt/shared-storage/users/xzluo/filtered_data/60.json', '/mnt/shared-storage/users/xzluo/filtered_data/61.json', '/mnt/shared-storage/users/xzluo/filtered_data/62.json', '/mnt/shared-storage/users/xzluo/filtered_data/63.json', '/mnt/shared-storage/users/xzluo/filtered_data/64.json', '/mnt/shared-storage/users/xzluo/filtered_data/65.json', '/mnt/shared-storage/users/xzluo/filtered_data/66.json', '/mnt/shared-storage/users/xzluo/filtered_data/67.json', '/mnt/shared-storage/users/xzluo/filtered_data/68.json', '/mnt/shared-storage/users/xzluo/filtered_data/69.json', '/mnt/shared-storage/users/xzluo/filtered_data/7.json', '/mnt/shared-storage/users/xzluo/filtered_data/70.json', '/mnt/shared-storage/users/xzluo/filtered_data/71.json', '/mnt/shared-storage/users/xzluo/filtered_data/72.json', '/mnt/shared-storage/users/xzluo/filtered_data/73.json', '/mnt/shared-storage/users/xzluo/filtered_data/8.json', '/mnt/shared-storage/users/xzluo/filtered_data/9.json']