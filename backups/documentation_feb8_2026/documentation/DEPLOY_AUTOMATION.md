# Deploy Automation: GitHub + Railway

This project includes optional local automation to push commits to GitHub and trigger Railway deployments immediately after commits.

Files added
- `.githooks/post-commit` — local git hook that pushes the committed branch to `origin` and, if the Railway CLI and env vars are available, triggers a deploy.
- `scripts/setup-git-hooks.sh` — installer script to copy hook files into `.git/hooks/` for your local clone.
- `scripts/deploy.sh` — manual helper to push and trigger Railway deploy from the command line.

Why this exists
- You asked to ensure changes are committed to GitHub and deployed to Railway so you can test on the live site after updates. Local git hooks automate the push + deploy step for developers who want immediate deploys.

Setup (local developer)

1. Install Railway CLI (required for automatic deploys from local machine):

   - Follow instructions at https://railway.app/ or use their install script.

2. Configure environment variables (in your shell or CI secrets):

   - `RAILWAY_TOKEN` — your Railway auth token (keep secret)
   - `RAILWAY_PROJECT` — Railway project id or name to deploy to

3. Install the git hooks in your local clone (run once per clone):

```bash
cd /path/to/repo
chmod +x scripts/setup-git-hooks.sh
./scripts/setup-git-hooks.sh
```

Behavior

- After running `git commit`, the `post-commit` hook will `git push origin <branch>`.
- If Railway CLI is installed and `RAILWAY_TOKEN` and `RAILWAY_PROJECT` are set, the hook will call `railway up --project "$RAILWAY_PROJECT" --detach` to start a deploy.
- If Railway CLI is not present or env is missing, the hook still pushes to GitHub and prints a reminder.

CI / GitHub Actions

- We recommend connecting Railway to GitHub via Railway's native GitHub integration (preferred) or using CI to run `scripts/deploy.sh` using the Railway CLI (if you prefer to trigger deploys from CI).
- If you'd like, I can add a GitHub Actions workflow that runs tests on push and triggers Railway via the CLI using repository secrets — tell me if you want that and I will add it.

Security notes

- Do NOT commit or store `RAILWAY_TOKEN` in the repository. Use environment or CI secrets.
- Local hooks are not version-controlled by default; this repo provides `.githooks/` and `scripts/setup-git-hooks.sh` so each developer can install hooks locally.

Troubleshooting

- If the hook fails to push, check your branch permissions and remote `origin` URL.
- If Railway deploy fails, run `railway up --project "$RAILWAY_PROJECT"` manually to check error output.
