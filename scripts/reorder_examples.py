import json

def main():
    """Reorder translated ARC examples so they are in the same order as the
    other documents in the dataset"""
    for lang in ["is", "nb"]:
        for subset in ["train", "test", "validation"]:
            examples_dict = {}
            with open(f"data_arc/{lang}_{subset}.json", "r") as f:
                examples = json.load(f)
            for example in examples:
                examples_dict[example["id"]] = example
                # Fix answer that were accidentally put into lowercase
                examples_dict[example["id"]]["answer"] = example["answer"].upper()


            reference = f"datasets/m_arc/de_{subset}.json"
            with open(reference, "r") as f:
                ref_json = json.load(f)

            ordered_examples = [examples_dict[ref["id"]] for ref in ref_json]

            with open(f"datasets/m_arc/{lang}_{subset}.json", "w") as f:
                json.dump(ordered_examples, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    main()
