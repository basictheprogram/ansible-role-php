"""OS-aware SSH client package check for the php Molecule scenario."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from testinfra.host import Host

_REDHAT_DISTROS: frozenset[str] = frozenset({"redhat", "centos", "rocky", "almalinux", "fedora"})


def test_ssh_client_package_installed(host: Host) -> None:
    dist: str = host.system_info.distribution.lower()
    pkg = "openssh-clients" if dist in _REDHAT_DISTROS else "openssh-client"
    assert host.package(pkg).is_installed
