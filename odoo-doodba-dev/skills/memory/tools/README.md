# Memory Skill Shell Wrappers

These are convenience shell scripts that wrap the Python memory commands using `uv run`.

## Available Scripts

### store.sh
Store a memory item:
```bash
./store.sh "key" "value" --category decision --tags "tag1,tag2" --context "additional context"
```

### retrieve.sh
Retrieve a memory item by key:
```bash
./retrieve.sh "key"
```

### search.sh
Search memory items:
```bash
./search.sh "query"
./search.sh "query" --category decision
./search.sh --tags "tag1,tag2"
```

### list.sh
List all memory items:
```bash
./list.sh
./list.sh --stats
./list.sh --category decision
```

### clear.sh
Clear memory items:
```bash
./clear.sh --key "specific.key" --yes
./clear.sh --category temp --yes
./clear.sh --all --yes
```

### export.sh
Export memory to JSON:
```bash
./export.sh --output backup.json --pretty
```

### import.sh
Import memory from JSON:
```bash
./import.sh backup.json
./import.sh backup.json --overwrite
```

## Requirements

- `uv` package manager must be installed
- Run from the tools directory or adjust paths accordingly
