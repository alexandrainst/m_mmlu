# m_mmlu
`python -m venv venv`

`source venv/bin/activate`

`pip install -r requirements.txt`

`bash scripts/download_orig.sh`

`bash scripts/download_uoregon.sh`

`python scripts/translate.py`

`python scripts/mix_and_scramble.py`
