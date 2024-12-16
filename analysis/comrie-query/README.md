# Query one Wordlist Against Lexibank

Install dependencies:

```
pip install -r requirements.txt
```

Get Lexibank:

```
git clone https://github.com/lexibank/lexibank-analysed
cd lexibank-analysed
git checkout v1.0
cd ..
pip install pycldf
cldf createdb lexibank-analysed/cldf/Wordlist-metadata.json lexibank.sqlite3
```

Run the script:

```
python code.py
```

This modifies the file `coordinates.json` so if you check index.html, the leaflet map will change.
