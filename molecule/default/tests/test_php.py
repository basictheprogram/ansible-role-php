"""Role-behavior tests for the php Molecule scenario.

Covers what this role actually manages: the rendered php.ini, PHP-FPM pool
config and service state, OpCache and APCu extension ini files, and a CLI
sanity check. Paths are derived per-OS rather than hardcoded, since the
Debian-family conf paths are templated with the installed PHP version
(e.g. /etc/php/8.2/fpm) which differs per distro/release.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from testinfra.host import Host

_REDHAT_DISTROS: frozenset[str] = frozenset({"redhat", "centos", "rocky", "almalinux", "fedora"})

# Matches molecule/default/converge.yml's vars block.
_EXPECTED_MEMORY_LIMIT = "192M"


def _is_redhat_family(host: Host) -> bool:
    return host.system_info.distribution.lower() in _REDHAT_DISTROS


def _installed_php_version(host: Host) -> str:
    cmd = host.run("php -r 'echo PHP_MAJOR_VERSION . \".\" . PHP_MINOR_VERSION;'")
    assert cmd.rc == 0
    return cmd.stdout.strip()


def _conf_paths(host: Host) -> list[str]:
    if _is_redhat_family(host):
        return ["/etc"]
    version = _installed_php_version(host)
    return [
        f"/etc/php/{version}/fpm",
        f"/etc/php/{version}/apache2",
        f"/etc/php/{version}/cli",
    ]


def _extension_conf_paths(host: Host) -> list[str]:
    if _is_redhat_family(host):
        return ["/etc/php.d"]
    version = _installed_php_version(host)
    return [
        f"/etc/php/{version}/fpm/conf.d",
        f"/etc/php/{version}/apache2/conf.d",
        f"/etc/php/{version}/cli/conf.d",
    ]


def test_php_cli_reports_a_version(host: Host) -> None:
    cmd = host.run("php --version")
    assert cmd.rc == 0
    assert "PHP" in cmd.stdout


def test_php_ini_exists_in_every_conf_path(host: Host) -> None:
    for conf_path in _conf_paths(host):
        f = host.file(f"{conf_path}/php.ini")
        assert f.exists
        assert f.is_file


def test_php_ini_has_managed_memory_limit(host: Host) -> None:
    conf_path = _conf_paths(host)[0]
    content = host.file(f"{conf_path}/php.ini").content_string
    assert f"memory_limit = {_EXPECTED_MEMORY_LIMIT}" in content


def test_opcache_ini_has_jit_buffer_size(host: Host) -> None:
    for ext_path in _extension_conf_paths(host):
        f = host.file(f"{ext_path}/10-opcache.ini")
        if not f.exists:
            continue
        assert "opcache.jit_buffer_size=100M" in f.content_string
        return
    msg = "No opcache ini file found in any extension conf path"
    raise AssertionError(msg)


def test_apcu_ini_present(host: Host) -> None:
    filename = "50-apc.ini" if _is_redhat_family(host) else "20-apcu.ini"
    found = any(host.file(f"{ext_path}/{filename}").exists for ext_path in _extension_conf_paths(host))
    assert found


def test_php_fpm_service_running(host: Host) -> None:
    # converge.yml sets php_enable_php_fpm: true. configure-fpm.yml only
    # explicitly manages service state on non-Debian hosts (Debian's
    # php-fpm package starts/enables itself on install), so this only
    # asserts the observable end state -- running -- on every family, and
    # only asserts boot-enablement where the role itself guarantees it.
    daemon = "php-fpm" if _is_redhat_family(host) else f"php{_installed_php_version(host)}-fpm"
    service = host.service(daemon)
    assert service.is_running
    if _is_redhat_family(host):
        assert service.is_enabled


def test_php_fpm_pool_conf_rendered(host: Host) -> None:
    if _is_redhat_family(host):
        pool_conf = "/etc/php-fpm.d/www.conf"
    else:
        pool_conf = f"/etc/php/{_installed_php_version(host)}/fpm/pool.d/www.conf"
    f = host.file(pool_conf)
    assert f.exists
    assert "listen = 127.0.0.1:9000" in f.content_string
