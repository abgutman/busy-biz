# Busy Biz

**Tools to keep biz busy** — the standalone hub for business reporting dashboards,
separate from av-tools.

- **Live:** https://abgutman.github.io/busy-biz/ (password-gated, deindexed)
- **Repo:** `abgutman/busy-biz` (public, GitHub Pages from `main` / root)
- **Deploy clone:** `~/Desktop/claude_sandbox/.deploy/busy-biz/` (persistent — never `/tmp`)

## What's here

| Tile | Source | Where it lives |
|------|--------|----------------|
| Earnings Reports | `earnings-tracker` repo | external link |
| Business News Feed | `earnings-tracker` repo | external link |
| Bankruptcy Tracker | `bankruptcy-tracker` repo | external link |
| Executive Compensation | `business/comp/build_comp_dashboard.py` | hosted in this repo |

Earnings and bankruptcy keep their own repos and crons (split in June 2026 to stop
cron competition). Busy Biz only *links* to them — it does not run their scrapers.
Exec comp has no cron, so it is built and hosted here directly.

## Files

- `build_homepage.py` — generates `index.html` (dark fintech theme; tiles are data-driven).
- `auth_gate.py` — Busy Biz password gate. Distinct `sessionStorage` key (`busybiz_auth`)
  so a login here does **not** unlock av-tools, and vice versa (shared `abgutman.github.io`
  origin). Stores only the SHA-256 of the password, never the plaintext.
- `deploy_busy_biz.sh` — builds exec comp + homepage, copies built HTML into the deploy
  clone, commits, and pushes.
- `robots.txt` — `Disallow: /` (deindex; belt-and-suspenders with the `noindex` meta tag).

## Replicating a deploy

```bash
business/busy_biz/deploy_busy_biz.sh
```

That's it: it rebuilds both pages and pushes. To change the homepage, edit `TILES` in
`build_homepage.py`. To change the password, update `PASSWORD_HASH` in `auth_gate.py`
(`python3 -c "import hashlib; print(hashlib.sha256(b'NEWPASS').hexdigest())"`).
