# Ragnarok Origin Language Decrypter

This is the tool we are using back then when we first released the Ragnarok Origin Language Patcher. Now its a scrapped project and we are happy to share it with anyone.

### Usage:

#### To decrypt file:

1. Create a `main.py` file together with the `engine.py` file.
2. Open `main.py` and put these contents:
```
import engine

# Decrypt the file
decrypt_language = engine.database_read("2226754682.robytes");

# Read the decrypted data
with open("dump.tsv", "w", encoding="utf-8") as fh:
   for item in decrypt_language:
        id = item['_id_']
        name = item['text'].replace("\n","\\n")
        fh.write(f"{id}\t{name}\t\n")
```

#### To encrypt file:

1. Create a `main.py` file together with the `engine.py` file.
2. Open `main.py` and put these contents:
```
import engine

# Create a dictionary with ID as key and the translated text as the value.
my_translation = {
	"ID1": "This is my translation",
	"ID2": "This is another translation",
}

# Build the robyte file
build_language = database_build_up(my_translation)

# Write the content to a file
with open("2226754682_custom.robytes", "wb") as fp:
    fp.write(build_language)
```
