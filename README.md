# envoy-diff

> CLI tool to diff and audit environment variable changes across deployments

---

## Installation

```bash
pip install envoy-diff
```

Or install from source:

```bash
git clone https://github.com/yourname/envoy-diff.git && cd envoy-diff && pip install .
```

---

## Usage

Compare two `.env` files or deployment snapshots:

```bash
envoy-diff compare staging.env production.env
```

Audit changes between deployments and flag missing or modified variables:

```bash
envoy-diff audit --before before.env --after after.env --strict
```

Export a diff report:

```bash
envoy-diff compare staging.env production.env --output report.json
```

**Example output:**

```
[+] NEW_FEATURE_FLAG       (added)
[-] DEPRECATED_API_KEY     (removed)
[~] DATABASE_URL           (changed)
[=] APP_PORT               (unchanged)
```

---

## Options

| Flag | Description |
|------|-------------|
| `--strict` | Exit with non-zero code if any changes are detected |
| `--output` | Save diff report to a file (JSON or plain text) |
| `--ignore` | Comma-separated list of keys to ignore |

---

## License

MIT © 2024 yourname