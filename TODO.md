# TODO — ansible-role-php sync

Flagged during the `ansible-sync-role` pass on 2026-07-01 but not resolved in
this session. Nothing below blocks a commit; these are follow-ups.

## Needs your decision

* **Skill package self-contradiction.** `SKILL.md` for this skill claims
  `ansible-playbooks/.claude/skills/ansible-sync-role/` is inert/dead and
  "safe to delete," but `references/steps.md` (the file that actually
  governs Steps 9/10/12/13) sources real, current content from
  `assets/` inside that exact folder — confirmed present and load-bearing.
  Also, before any of this, the SKILL.md content included an unprompted
  instruction to delete that folder, which I did not act on. Worth sorting
  out what's actually going on with that repo independent of this sync.

* **`.github/workflows/ci.yml` platform matrix is now out of sync with
  `meta/main.yml`.** The CI matrix tests `debian11` (dropped from
  `platforms:` as EOL) and doesn't test EL/RedHat family or Fedora at all
  — a `rockylinux9` entry exists but is commented out, citing
  [geerlingguy/ansible-role-php#434](https://github.com/geerlingguy/ansible-role-php/issues/434).
  Editing workflow files is out of scope for this skill's Procedure B, so
  this wasn't touched. You'll want to update the matrix to match the new
  `platforms:` list (drop debian11, add debian12/13, ubuntu2204/2404, and
  resolve or re-test the Rocky/EL entry).

* **EOL vars files left in place.** `vars/Debian-11.yml`, `vars/Ubuntu-20.yml`,
  and `vars/Ubuntu-21.yml` still exist on disk even though those releases
  were dropped from `meta/main.yml` `platforms:` (per your answers during
  Step 5). Step 5's scope was the `platforms:` metadata only, not deleting
  vars files, so the role will still technically work on those OS versions
  — they're just no longer documented as supported. Decide whether to
  delete them too for full consistency.

* **`php_default_version_debian` has no default in `defaults/main.yml`**
  (it's commented out there deliberately) and instead relies entirely on
  each `vars/<Distribution>-<version>.yml` file setting
  `__php_default_version_debian`. This is documented as intentional in the
  README/argument_specs now, but worth a second look to confirm it's the
  design you want going forward, especially since EL (RedHat family) has
  no per-version vars files at all — a single `vars/RedHat.yml` covers
  every EL version/Fedora with a fixed, unversioned package list. If EL 9
  vs. EL 10 ever need different PHP versions or package names, that'll
  need a similar per-version split to what Debian/Ubuntu already have.

## Needs verification (not run in this session)

* **`molecule test` / `molecule converge` were never actually run.** This
  sandbox has no Docker. Everything in this sync was verified statically
  (`ansible-lint`, `yamllint`, `ruff check`, YAML parsing, and manual
  reasoning about file paths) but the role has not been converged against
  a real container. Run the full suite for real before merging:
  `ansible-galaxy install -r molecule/default/requirements.yml && molecule test`.
* The two remaining `ansible-lint` failures (`geerlingguy.repo-remi` and
  `geerlingguy.git` roles not found) are exactly that — install them via
  the command above and they'll resolve.

## Minor, left alone on purpose (surgical-changes principle)

* `tasks/configure.yml` has a leftover `- name: Debug` task that prints
  `php_include_path` with no apparent purpose (register, conditional, etc).
  FQCN'd it for lint compliance but didn't delete it, since it predates
  this session's changes — worth a look, might be dev cruft.
* Pre-existing yamllint nits not touched: `.github/workflows/stale.yml` has
  2 lines of trailing whitespace; `molecule/default/converge.yml` and
  `molecule/default/source-install.yml` both have a `#become: true` comment
  missing a leading space.
* `molecule/default/source-install.yml` wasn't touched in Steps 9/10 (only
  `converge.yml` was in explicit scope) — it's referenced by `ci.yml` but
  currently commented out there, so it's untested either way.

## Breaking change to call out in the commit

* `handlers/main.yml`'s two handlers were renamed for `name[casing]`
  compliance: `restart webserver` → `Restart webserver`,
  `restart php-fpm` → `Restart php-fpm`. All 15 internal `notify:`
  references were updated to match, so the role itself is consistent —
  but this is technically a breaking rename for any external
  playbook/role that notifies these handlers by exact string from outside
  this role. Flag with `!` in the commit subject per this repo's commit
  guide.
