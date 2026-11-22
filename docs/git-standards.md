# Professional Git Standards & Engineering Workflow

This standard outlines version control rules, branch naming conventions, commit formats, and maintenance procedures designed for production environments and team collaboration.

---

## 1. Branch Strategy & Lifecycle

We use a **Trunk-Based Feature Branch** workflow. The `main` branch represents deployable, stable code at all times. Direct pushes to `main` are prohibited outside initial repository bootstrapping.

```text
main (protected, always deployable)
  │
  ├── feat/rag-hybrid-search ───────┐ (PR with squash or rebase merge)
  │                                 ▼
  ├── fix/connection-pool-leak ─────┘

```

### Branch Naming Conventions

Branch names must be lowercase, hyphen-separated, and prefixed with a standardized category:

| Prefix | Intent | Example |
| --- | --- | --- |
| `feat/` | New functionality or API endpoint | `feat/pgvector-indexing` |
| `fix/` | Bug fix in existing logic | `fix/session-rollback-leak` |
| `refactor/` | Code change that neither fixes a bug nor adds a feature | `refactor/pydantic-v2-migration` |
| `chore/` | Tooling, dependencies, or configuration changes | `chore/upgrade-asyncpg` |
| `docs/` | Documentation, READMEs, architecture specs | `docs/add-api-endpoints` |
| `test/` | Adding or updating test suites | `test/task-crud-assertions` |
| `perf/` | Performance optimizations | `perf/redis-caching-layer` |

### Branch Lifecycle Rules

1. **Branch off updated trunk:** Always branch off the latest `main`:
```bash
git checkout main
git pull origin main
git checkout -b feat/<feature-name>

```


2. **Keep branches short-lived:** Aim to merge branches within 1–3 days to prevent diverging diffs.
3. **Delete merged branches:** Delete both local and remote branches immediately after merging to keep the repository uncluttered:
```bash
git branch -d feat/<feature-name>
git push origin --delete feat/<feature-name>

```



---

## 2. Conventional Commits Specification

Every commit message must follow the [Conventional Commits v1.0.0](https://www.conventionalcommits.org/) format. This enables automated changelog generation and makes repository history readable.

### Commit Anatomy

```text
<type>(<scope>): <imperative summary>

[optional body explaining WHY the change was made, not WHAT]

[optional footer(s) for issue trackers or breaking changes]

```

### Structural Rules

* **Header Limit:** Under 50–72 characters.
* **Imperative Mood:** Use "add", not "added" or "adding"; use "fix", not "fixed".
* **No Trailing Period:** Do not end the subject line with a period.
* **Monorepo Scoping:** In a multi-module repository, always specify the affected module or subproject in the scope:
* `feat(backend-core): add asyncpg connection pool initialization`
* `refactor(lead-triage): migrate state graph to langgraph v0.2`
* `chore(infra): add pgvector extension to postgres compose`



### Breaking Changes

Mark breaking changes with an exclamation mark (`!`) before the colon and describe the impact in the footer:

```text
feat(api)!: change task response schema from snake_case to camelCase

BREAKING CHANGE: The TaskResponse model now returns camelCase JSON attributes
to align with frontend contract requirements.

```

---

## 3. Pull Requests & Code Reviews

### Atomic Pull Requests

* **Single Responsibility:** A Pull Request should solve one issue or introduce one cohesive capability.
* **Size Target:** Keep diffs under 300–400 lines of code. Large PRs hide bugs and delay reviews.

### Pull Request Description Template

Place this template at `.github/pull_request_template.md` to standardize every PR:

```markdown
## Summary of Changes
- Implemented ...
- Configured ...

## Motivation & Context
Why was this change required? What problem does it solve?

## Verification Steps
1. Start services: `docker compose up -d`
2. Run migration: `alembic upgrade head`
3. Execute test suite: `pytest modules/01-backend-core/tests`

## Impacted Modules
- [x] modules/01-backend-core
- [ ] modules/02-rag-vector-search
- [ ] infrastructure

```

### Merging Strategies

| Strategy | When to Use | Resulting Git History |
| --- | --- | --- |
| **Squash and Merge** | Multi-commit feature branches with intermediate "work in progress" steps. | Combines all branch commits into **one** clean commit on `main`. |
| **Rebase and Merge** | Branches with carefully structured, atomic, high-value commits. | Fast-forwards commits onto `main` with no merge commit. |
| **Merge Commit (`--no-ff`)** | Long-running release branches or audited merges. | Preserves the explicit branch diamond graph. |

*Recommendation:* Use **Squash and Merge** by default on GitHub to ensure `main` remains a clean, linear sequence of completed features.

---

## 4. Repository Security & Hygiene

### Strict `.gitignore` Rules

Never track build artifacts, virtual environments, or secrets:

```text
# Virtual Environments
.venv/
venv/
env/

# Python Cache
__pycache__/
*.py[cod]
.pytest_cache/

# Environment Files & Secrets
.env
*.env
!*.env.example

# Local Data Storage
postgres_data/
redis_data/
*.sqlite3
*.log

# IDE & OS Files
.DS_Store
Thumbs.db
.idea/
.vscode/

```

### Handling Leaked Secrets

If an API key or password is accidentally committed:

1. **Revoke the key immediately** at the provider dashboard (OpenAI, AWS, Database). Changing Git history alone does not neutralize a leaked credential.
2. Remove the file from Git cache without deleting it locally:
```bash
git rm --cached path/to/.env
git commit -m "chore(security): remove tracked credentials file"

```


3. If the commit was already pushed to remote, purge it from history using `git-filter-repo`:
```bash
pip install git-filter-repo
git-filter-repo --path path/to/sensitive-file --invert-paths
git push origin main --force

```



---

## 5. Day-to-Day Command Playbook

### Keeping Your Feature Branch Synchronized

Avoid pulling `main` into your feature branch with a merge commit. Instead, rebase your changes on top of `main`:

```bash
# 1. Update your local main
git checkout main
git pull origin main

# 2. Rebase feature branch on top of fresh main
git checkout feat/<your-branch>
git rebase main

# 3. If conflicts occur, resolve files and run:
git add <resolved-file>
git rebase --continue

```

### Polishing Local Commits (Interactive Rebase)

Combine, edit, or reword messy local commits before opening a PR:

```bash
# Inspect the last 3 commits
git rebase -i HEAD~3

```

In the editor that opens:

* `pick`: keep the commit as is.
* `reword`: keep the commit but modify the message.
* `squash`: melt the commit into the previous one.
* `drop`: remove the commit entirely.

### Stashing Unfinished Work

To switch contexts without making a messy checkpoint commit:

```bash
# Stash tracked and untracked changes with a descriptive label
git stash push -u -m "wip: incomplete postgres session wiring"

# View your stash stack
git stash list

# Re-apply and remove from stack
git stash pop

```

### Undoing Mistakes Safely

| Scenario | Command | Effect |
| --- | --- | --- |
| **Change the last commit message** | `git commit --amend -m "feat(api): correct message"` | Overwrites the previous commit metadata. |
| **Add a forgotten file to the last commit** | `git add <file> && git commit --amend --no-edit` | Merges file into the previous commit. |
| **Discard uncommitted local edits** | `git restore <file>` | Reverts file back to the last commit state. |
| **Unstage a file staged with `git add**` | `git restore --staged <file>` | Moves file back to untracked/unstaged working state. |
| **Undo a pushed commit safely** | `git revert <commit-hash>` | Creates a *new* commit that inverses the changes, keeping history intact. |
| **Hard reset local branch to remote** | `git reset --hard origin/main` | Destroys local divergent commits and matches remote state. |

---

## 6. Monorepo Automation with Pre-Commit Hooks

To automatically enforce formatting, syntax verification, and secret scanning before every commit, configure `pre-commit`.

### Installation & Setup

1. Add `pre-commit` to your root development dependencies:
```bash
pip install pre-commit

```


2. Create `.pre-commit-config.yaml` in your repository root:
```yaml
repos:
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.6.0
    hooks:
      - id: check-yaml
      - id: end-of-file-fixer
      - id: trailing-whitespace
      - id: check-added-large-files
        args: ['--maxkb=1000']
      - id: detect-private-key

  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.5.0
    hooks:
      - id: ruff
        args: [--fix]
      - id: ruff-format

```


3. Register the hook into your `.git/` folder:
```bash
pre-commit install

```



Now, every time you run `git commit`, your code is automatically verified against trailing whitespace, formatting standards, and leaked private keys before the commit is finalized.