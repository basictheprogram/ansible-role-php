# TODO — ansible-role-php sync

Flagged during `ansible-sync-role` passes but not resolved. Nothing below
blocks a commit; these are follow-ups.

Original pass: 2026-07-01. Re-sync against current template: 2026-09-05.

## Needs your decision

* **Dropped / EOL vars files left in place.** `vars/Debian-11.yml`,
  `vars/Debian-12.yml`, `vars/Ubuntu-20.yml`, and `vars/Ubuntu-21.yml`
  still exist on disk even though those releases are no longer in the
  supported-platform statement (`meta/main.yml` `description:`, README,
  `molecule.yml`). Debian 12 was dropped in the 2026-09-05 re-sync
  (full-support EOL ~2026-08; Debian-LTS to 2028-06). The role still
  technically works on all four — they're just undocumented. Decide
  whether to delete them for full consistency.

* **`.github/workflows/ci.yml` is now well out of sync.** It still drives
  molecule with the `MOLECULE_DISTRO` env-var pattern that the 2026-09-05
  re-sync removed from `molecule.yml` (now an explicit 6-platform list:
  `debian-trixie`, `ubuntu-jammy`, `ubuntu-noble`, `ubuntu-resolute`,
  `el-9`, `el-10`). The CI matrix also tests `debian11`, doesn't test
  EL/RedHat family, and has a commented-out `rockylinux9` entry citing
  [geerlingguy/ansible-role-php#434](https://github.com/geerlingguy/ansible-role-php/issues/434).
  Workflow authoring is out of scope for the sync skill's Procedure B —
  rework the matrix by hand to match `molecule.yml`.

* **`php_default_version_debian` has no default in `defaults/main.yml`**
  (commented out deliberately); each `vars/<Distribution>-<version>.yml`
  supplies `__php_default_version_debian`. Documented as intentional in
  the README/argument_specs. EL (RedHat family) has no per-version vars
  files — a single `vars/RedHat.yml` covers every EL version/Fedora with
  a fixed, unversioned package list. If EL 9 vs. EL 10 ever need
  different PHP versions or package names, that'll need a per-version
  split like Debian/Ubuntu already have.

* **Skill package self-contradiction (upstream tooling, not this role).**
  `SKILL.md` for `ansible-sync-role` claims
  `ansible-playbooks/.claude/skills/ansible-sync-role/` is inert/dead and
  "safe to delete," but `references/steps.md` sources real content from
  `assets/` inside that folder. Worth sorting out independently.

## Minor, left alone on purpose (surgical-changes principle)

* **Dead Ubuntu 16.04 branch.** `tasks/main.yml` has a
  `php_opcache_conf_filename` `set_fact` gated on
  `ansible_facts.distribution_version == "16.04"`. Ubuntu 16.04 is long
  EOL and not a supported platform — the `when` can never be true.
  Pre-existing; not deleted without being asked.

* **testinfra suite nits.** `_REDHAT_DISTROS` is defined identically in
  both `molecule/default/tests/test_php.py` and `test_packages.py` — the
  skeleton convention is a shared `_data.py`. And `test_packages.py` only
  checks that `openssh-client`/`openssh-clients` is installed (a base
  image package, not role-managed) — it's really a testinfra-plumbing
  smoke test; consider asserting an actual PHP package instead.

* **`molecule/default/source-install.yml` not touched.** Step 10's scope
  was `converge.yml`. `source-install.yml` still pins `php_version:
  "7.4.8"` (PHP 7.4 is EOL) and has a `# become: true` comment missing a
  leading space (yamllint nit). It's referenced by `ci.yml` but
  currently commented out there.

* Pre-existing yamllint nits not touched: `.github/workflows/stale.yml`
  trailing whitespace.

## Needs verification (not run in this session)

* **`molecule test` / `molecule converge` have never actually run.** No
  Docker in the sync sandboxes. Everything was verified statically
  (YAML parsing, manual reasoning about paths and lint rules). Run the
  full suite before merging:
  `ansible-galaxy install -r molecule/default/requirements.yml && molecule test`.
* **`ansible-lint` / `yamllint` / `pre-commit` are not installed in the
  re-sync environment** — the 2026-09-05 pass reasoned about lint rules
  statically but could not run them. Run `pre-commit run --all-files`
  before committing.
* The `geerlingguy.repo-remi` and `geerlingguy.git` roles resolve once
  installed via `ansible-galaxy role install -r
  molecule/default/requirements.yml`.

## Breaking change already shipped (in 9de10d6, for reference)

* `handlers/main.yml` handlers were renamed for `name[casing]`:
  `restart webserver` → `Restart webserver`, `restart php-fpm` →
  `Restart php-fpm`. All internal `notify:` references were updated.
  External playbooks/roles notifying these handlers by exact string
  must update. `meta/main.yml` also dropped declared support for
  Debian 11, Ubuntu 20.04/21.x, and EL 8.
