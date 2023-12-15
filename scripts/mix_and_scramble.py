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

def dir_to_dict(json_dir:Path):
    sample_dict = {}
    for path in json_dir.glob("*.json"):
        with open(path, "r") as f:
            samples = json.load(f)
            for sample in samples:
                sample_dict[sample["id"]] = sample
    return sample_dict


def main():
    for lang in ["nb"]:
        random.seed(7243)
        for split in ["dev", "val", "test"]:
            data_dir = Path(f"data_{lang}") / split
            reference_path = Path(f"datasets/m_mmlu/de_{split}.json")
            with open(reference_path, "r") as f:
                reference_list = json.load(f)
                id_list = [r["id"] for r in reference_list]

            sample_dict = dir_to_dict(data_dir)
            sorted_list = [sample_dict[i] for i in id_list]

            output_path = Path(f"datasets/m_mmlu/{lang}_{split}.json")
            with open(output_path, "w") as f:
                json.dump(sorted_list, f, indent=2, ensure_ascii=False)


if __name__ == "__main__":
    main()
