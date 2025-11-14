# OOCL Context Engineering

## Setup

### 1. Install dependencies

For macOS/Linux:
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

For Windows:

```bash
python -m venv .venv
.venv\Scripts\activate.bat
pip install -r requirements.txt
```

### 2. Configure environment variables

Edit the `.env` file to set your OpenAI API credentials and model preferences.

- `OPENAI_API_BASE`: Your OpenAI API base URL.  
- `OPENAI_API_KEY`: Your OpenAI API key.

And please check following model name are matched to your privider:

- `EMBEDDING_MODEL`: typically 'text-embedding-3-small' with no prefix.
- `LLM_MODEL`: typically 'gpt-4o-mini' with no prefix.

### 3. Test Setup

Run `test_embedding.py` and `test_llm.py` to verify your setup:

```bash
python test_embedding.py
```

You will see something like while succeeded:

```
✅Congratulations! Embedding created successfully.
```

```bash
python test_llm.py
```

You will see something like while succeeded:

```
✅Congratulations! LLM response created successfully.
```