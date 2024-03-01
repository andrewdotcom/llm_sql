# LLM Tool for working with Duckdb LLM

This is a small utility to help working with the duckdb tuned [duckdb-nsql](https://ollama.com/library/duckdb-nsql) model with [Ollama](https://ollama.com).

### Example use:
```
./llmsql.py ./test.db -p "select all entries" -er
```

### Options:
```
usage: llmsql.py [-h] [-p PROMPT] [-e EXECUTE_QUERY] [-er EXECUTE_RESPONSE] database_path
```

This is very much a work in progress. Feel free to fork and send me a pull request.
