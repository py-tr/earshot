# IBM Hackathon GitHub Project Template

This GitHub project template is for IBM Hackathon projects. It includes pre-configured security files to help prevent accidental credential commits and potential account suspension during the hackathon.

## 🚀 Quick Start

1. **Use this template to create your project:**
   - Click "Use this template" button above and select "Create a new repository"
   - Name your repository
   - Click "Create repository"

2. **Clone your new repository:**

   ```bash
   git clone https://github.com/HACKATHON-ORG/your-repo-name.git
   cd your-repo-name
   ```

3. **Set up environment variables:**

   ```bash
   # Copy the example file
   cp .env.example .env

   # Edit .env with your actual credentials
   # Use your preferred editor (nano, vim, code, etc.)
   nano .env
   ```

4. **Verify .gitignore is working:**

   ```bash
   # This should NOT show .env file
   git status

   # This should confirm .env is ignored
   git check-ignore -v .env
   ```

5. **Start developing!**

## 🔒 Security Features

This template includes:

- **`.gitignore`** - Prevents committing credentials and live session files
- **`.bobignore`** - Prevents AI assistants from logging credentials
- **`.env.example`** - Template for your environment variables

## 📋 Before Every Commit

Always run this checklist:

- [ ] Reviewed `git diff` for sensitive data
- [ ] No hardcoded API keys or passwords
- [ ] `.env` file is NOT in staged changes
- [ ] No files with "credential" or "secret" in name
- [ ] Used environment variables for all credentials

## 🆘 Need Help?

- Read [SECURITY.md](SECURITY.MD) for detailed guidelines
- Contact hackathon support through mentor channel
- Ask in the hackathon Slack workspace

---

**Remember:** Security is everyone's responsibility. When in doubt, ask for help!

---

## Earshot gate

The Earshot gate is a pre-commit hook that replays verified accessibility findings against a live NVDA instance and blocks commits that break what a screen reader hears.

### One-time setup

```bash
git config core.hooksPath .githooks
```

### What it runs

On every commit the hook executes:

```sh
.venv/Scripts/python.exe earshot_mcp/hear_tests.py --staged
```

`--staged` is a fast-path guard: if no file under `galaxium/booking_system_frontend/src/` is staged the script prints `earshot gate: no UI changes` and exits 0 immediately without touching the browser or NVDA.

When frontend files **are** staged it runs the tests defined in [`hear-tests.json`](hear-tests.json). Each test drives the browser with a key script from [`findings.md`](findings.md), captures NVDA speech via `earshot_mcp/driver.py` + `earshot_mcp/extract.py`, and asserts that every expected phrase appears (in order) and no forbidden phrase appears.

If any assertion fails the hook prints:

```
BLOCKED by Earshot: this change breaks what a screen reader hears.
```

and exits 1, preventing the commit.

### Timing

Each test takes **30–60 seconds** because a real screen reader (NVDA) must speak and be recorded. Plan accordingly when staging frontend changes.
