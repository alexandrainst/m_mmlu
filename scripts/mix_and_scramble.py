import json
from pathlib import Path
import random

def dir_to_file(json_dir:Path, output_file:Path):
    sample_list = []
    for path in json_dir.glob("*.json"):
        with open(path, "r") as f:
            samples = json.load(f)
            sample_list.extend(samples)
    random.shuffle(sample_list)

    print("Writing %d samples to %s" % (len(sample_list), output_file))
    with open(output_file, "w") as f:
        json.dump(sample_list, f, indent=2, ensure_ascii=False)


def main():
    for lang in ["nb"]:
        random.seed(7243)
        for split in ["dev", "val", "test"]:
            data_dir = Path(f"data_{lang}") / split
            output_path = Path(f"datasets/m_mmlu/{lang}_{split}.json")
            dir_to_file(data_dir, output_path)


if __name__ == "__main__":
    main()
