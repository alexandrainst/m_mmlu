import json

def main():
    """Reorder and reformat translated HellaSwag examples so they are in the same order as the
    other documents in the dataset"""
    for lang in ["is", "nb", "en"]:
        for subset in ["validation"]:
            examples_dict = {}
            with open(f"data_hellaswag/{lang}_{subset.replace('validation','valid')}.json", "r") as f:
                examples = json.load(f)

            with open(f"hellaswag-train-dev/{subset.replace('validation','valid')}-labels.lst", "r") as f:
                labels = f.read().split()
            for idx, (example, label) in enumerate(zip(examples, labels)):
                new_id = f"hellaswag/validation/{idx}"
                source_id = example["dataset"] + "~" + "10920"
                if subset == "validation":
                    split = "val"
                else:
                    split = subset

                # Format examples as in the already existing data
                formatted_example = {
                    "ctx_a": example["ctx_a"],
                    "ctx_b": example["ctx_b"],
                    "ctx": example["ctx"],
                    "endings": example["ending_options"],
                    "id": new_id,
                    "ind": example["ind"],
                    "activity_label": example["activity_label"],
                    "source_id": source_id,
                    "split": split,
                    "split_type": example["split_type"],
                    "label": label,

                }
                examples_dict[formatted_example["id"]] = formatted_example

            reference = f"datasets/m_hellaswag/de_{subset}.json"
            with open(reference, "r") as f:
                ref_json = json.load(f)

            ordered_examples = [examples_dict[ref["id"]] for ref in ref_json]

            with open(f"datasets/m_hellaswag/{lang}_{subset}.json", "w") as f:
                json.dump(ordered_examples, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    main()
