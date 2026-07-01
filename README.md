# Ansible Role: PHP

Fork of [geerlingguy/ansible-role-php](https://github.com/geerlingguy/ansible-role-php) by Jeff Geerling. This fork lives at [basictheprogram/ansible-role-php](https://github.com/basictheprogram/ansible-role-php); bugs and pull requests go there, not upstream.

Installs and configures PHP (CLI, FPM, OpCache, APCu) on RedHat/CentOS and Debian/Ubuntu servers, either from distro packages or compiled from source.

## Requirements

* Ansible core >= 2.20.
* If you're using an older LTS release of Ubuntu or RHEL with an old/outdated version of PHP, you need to use a repo or PPA with a maintained PHP version, as this role only works with [PHP versions that are currently supported](http://php.net/supported-versions.php) by the PHP community.

## Supported Platforms

Matches `meta/main.yml`:

| OS family | Versions |
| --- | --- |
| Fedora | all |
| Debian | 12 (bookworm), 13 (trixie) |
| Ubuntu | 22.04 (jammy), 24.04 (noble) |
| EL (RHEL/CentOS/Rocky/AlmaLinux) | 9, 10 |

## Role Variables

Available variables are listed below, grouped as in `defaults/main.yml`, along with their default values.

### General

| Variable | Default | Description |
| --- | --- | --- |
| `php_enablerepo` | `""` | (RedHat/CentOS only) Comma-separated list of repos to enable when installing PHP packages, e.g. `remi-php82,epel`. |
| `php_packages_extra` | `[]` | Extra PHP packages to install without overriding the default list. |
| `php_default_version_debian` | *(unset)* | (Debian/Ubuntu only) Overrides the OS-specific default PHP version, e.g. `"8.2"`. See [OS-Specific Variables](#os-specific-variables) below for the per-release default. |
| `php_packages_state` | `present` | Package state; use `latest` to upgrade or switch versions using a new repo. |
| `php_install_recommends` | `true` | (Debian/Ubuntu only) Whether to install recommended packages alongside `php_packages`. |
| `php_enable_webserver` | `true` | Set to `false` if you're not tying PHP to a webserver (e.g. running FPM standalone). |
| `php_restart` | `true` | Whether the webserver handler actually restarts the webserver when notified. Set to `false` to suppress restarts even when `php_enable_webserver` is `true`. |
| `php_executable` | `php` | The executable to run when calling PHP from the command line. |

### PHP-FPM

PHP-FPM is a FastCGI process manager for PHP, and the normal way of running PHP behind Nginx (or Apache via `geerlingguy.apache-php-fpm`).

| Variable | Default | Description |
| --- | --- | --- |
| `php_enable_php_fpm` | `false` | Set to `true` when running PHP as `php-fpm` instead of inside the webserver process. |
| `php_fpm_state` | `started` | Desired running state of the php-fpm service. |
| `php_fpm_handler_state` | `restarted` | `reloaded` instead of `restarted` if you'd rather reload php-fpm on config changes. |
| `php_fpm_enabled_on_boot` | `true` | Whether php-fpm starts on boot. |
| `php_fpm_listen` | `127.0.0.1:9000` | Address/socket the default `www` pool listens on. |
| `php_fpm_listen_allowed_clients` | `127.0.0.1` | Clients allowed to connect to `php_fpm_listen`. |
| `php_fpm_pm_max_children` | `50` | Default `pm.max_children`. |
| `php_fpm_pm_start_servers` | `5` | Default `pm.start_servers`. |
| `php_fpm_pm_min_spare_servers` | `5` | Default `pm.min_spare_servers`. |
| `php_fpm_pm_max_spare_servers` | `5` | Default `pm.max_spare_servers`. |
| `php_fpm_pm_max_requests` | `0` | Default `pm.max_requests` (`0` = unlimited). |
| `php_fpm_pm_status_path` | `""` | Default FPM status page path (empty disables it). |

```yaml
php_fpm_pools:
  - pool_name: www
    pool_template: www.conf.j2
    pool_listen: "{{ php_fpm_listen }}"
    pool_listen_allowed_clients: "{{ php_fpm_listen_allowed_clients }}"
    pool_pm: dynamic
    pool_pm_max_children: "{{ php_fpm_pm_max_children }}"
    pool_pm_start_servers: "{{ php_fpm_pm_start_servers }}"
    pool_pm_min_spare_servers: "{{ php_fpm_pm_min_spare_servers }}"
    pool_pm_max_spare_servers: "{{ php_fpm_pm_max_spare_servers }}"
    pool_pm_max_requests: "{{ php_fpm_pm_max_requests }}"
    pool_pm_status_path: "{{ php_fpm_pm_status_path }}"
```

List of PHP-FPM pools to create; the `www` pool is created by default. To add a pool, append an item — each item may override any `pool_pm_*` key, or replace the whole pool config with a custom template via `pool_template`. `preflight.yml` asserts every pool entry defines a non-empty `pool_name` when `php_enable_php_fpm` is `true`.

### php.ini settings

| Variable | Default | Description |
| --- | --- | --- |
| `php_use_managed_ini` | `true` | Set to `false` to self-manage `php.ini` (all variables below are then ignored). |
| `php_expose_php` | `On` | |
| `php_memory_limit` | `256M` | |
| `php_max_execution_time` | `60` | |
| `php_max_input_time` | `60` | |
| `php_max_input_vars` | `1000` | |
| `php_realpath_cache_size` | `32K` | |
| `php_file_uploads` | `On` | |
| `php_upload_max_filesize` | `64M` | |
| `php_max_file_uploads` | `20` | |
| `php_post_max_size` | `32M` | |
| `php_date_timezone` | `America/Chicago` | |
| `php_allow_url_fopen` | `On` | |
| `php_sendmail_path` | `/usr/sbin/sendmail -t -i` | |
| `php_output_buffering` | `4096` | |
| `php_short_open_tag` | `Off` | |
| `php_disable_functions` | `[]` | |
| `php_precision` | `14` | |
| `php_serialize_precision` | `-1` | |
| `php_session_cookie_lifetime` | `0` | |
| `php_session_gc_probability` | `0` | |
| `php_session_gc_divisor` | `1000` | |
| `php_session_gc_maxlifetime` | `1440` | |
| `php_session_save_handler` | `files` | |
| `php_session_save_path` | `""` | |
| `php_error_reporting` | `E_ALL & ~E_DEPRECATED & ~E_STRICT` | |
| `php_display_errors` | `Off` | |
| `php_display_startup_errors` | `Off` | |

Only used when `php_use_managed_ini` is `true`.

### OpCache-related Variables

The OpCache is included in PHP starting in version 5.5.

| Variable | Default | Description |
| --- | --- | --- |
| `php_opcache_zend_extension` | `opcache.so` | Full path if `opcache.so` isn't already on the default extension path. |
| `php_opcache_enable` | `1` | |
| `php_opcache_enable_cli` | `0` | |
| `php_opcache_memory_consumption` | `96` | In MB — make sure this and `php_opcache_max_accelerated_files` are large enough to hold all the PHP code you're running. |
| `php_opcache_interned_strings_buffer` | `16` | |
| `php_opcache_max_accelerated_files` | `4096` | |
| `php_opcache_max_wasted_percentage` | `5` | |
| `php_opcache_validate_timestamps` | `1` | |
| `php_opcache_revalidate_path` | `0` | |
| `php_opcache_revalidate_freq` | `2` | |
| `php_opcache_max_file_size` | `0` | |
| `php_opcache_blacklist_filename` | `""` | |
| `php_opcache_jit_buffer_size` | `100M` | PHP 8+ only. |
| `php_opcache_conf_filename` | *(OS-specific)* | Generally the computed default works; override only if you need a different filename. |

### APCu-related Variables

| Variable | Default | Description |
| --- | --- | --- |
| `php_enable_apc` | `true` | Other `php_apc_*` variables have no effect when this is `false`. |
| `php_apc_shm_size` | `96M` | Size it to hold all cache entries with a little overhead — fragmentation or APC running out of memory will slow PHP down *dramatically*. |
| `php_apc_enable_cli` | `0` | |
| `php_apc_conf_filename` | *(OS-specific)* | Generally the computed default works; override only if you need a different filename. |

Make sure APCu is actually in your package list if you customize `php_packages`: `php-pecl-apcu` on RHEL/CentOS, `phpX.Y-apcu` on Debian/Ubuntu.

### Installing from Source

If you need a PHP version with no suitable package for your platform, you can compile from source. Source builds take *much* longer than installing packages (5+ minutes for PHP HEAD on a modern quad-core machine).

| Variable | Default | Description |
| --- | --- | --- |
| `php_install_from_source` | `false` | Set to `true` to install PHP from source instead of from packages. |
| `php_source_repo` | `https://github.com/php/php-src.git` | |
| `php_source_version` | `master` | A git branch, tag, or commit hash. |
| `php_source_clone_dir` | `~/php-src` | |
| `php_source_clone_depth` | `1` | |
| `php_source_install_path` | `/opt/php` | |
| `php_source_install_gmp_path` | `/usr/include/x86_64-linux-gnu/gmp.h` | Platform/distribution-specific GMP header location. |
| `php_source_mysql_config` | `/usr/bin/mysql_config` | May be `mariadb_config` on newer OS versions. |
| `php_source_make_command` | `make` | Set to `make --jobs=X` (X = core count) to speed up compilation. |
| `php_source_configure_command` | *(see `defaults/main.yml`)* | The full `./configure` invocation; edit to match your environment. |

A few notes for specific configurations:

* **Apache with `mpm_prefork`**: make sure `apxs2` is available (e.g. `apache2-prefork-dev` on Ubuntu) and `--with-apxs2` is in `php_source_configure_command`. Load `mpm_prefork`, not `mpm_worker`/`mpm_event`, and add a `phpX.conf` Apache module config.
* **Apache with `mpm_event`/`mpm_worker`**: compile PHP with FPM (`--enable-fpm`). Install CGI/event support (`apache2-mpm-event`, `libapache2-mod-fastcgi`) and load `mpm_event`.
* **Nginx**: compile PHP with FPM (`--enable-fpm`).

## OS-Specific Variables

These are loaded via `include_vars` from `vars/<OsFamily>.yml` and then `vars/<Distribution>-<MajorVersion>.yml` — they are computed per-OS, not meant to be overridden the way `defaults/` variables are (though you still can, by setting them directly).

| Variable | Debian family | RedHat family |
| --- | --- | --- |
| `php_webserver_daemon` | `apache2` | `httpd` |
| `php_conf_paths` | `/etc/php/<ver>/{fpm,apache2,cli}` | `/etc` |
| `php_extension_conf_paths` | `/etc/php/<ver>/{fpm,apache2,cli}/conf.d` | `/etc/php.d` |
| `php_apc_conf_filename` | `20-apcu.ini` | `50-apc.ini` |
| `php_opcache_conf_filename` | `10-opcache.ini` | `10-opcache.ini` |
| `php_fpm_daemon` | `php<ver>-fpm` | `php-fpm` |
| `php_fpm_conf_path` | `/etc/php/<ver>/fpm` | `/etc/fpm` |
| `php_fpm_pool_conf_path` | `<fpm_conf_path>/pool.d/www.conf` | `/etc/php-fpm.d/www.conf` |
| `php_fpm_pool_user` / `php_fpm_pool_group` | `www-data` | `apache` |
| `php_packages` | version-templated list, see `vars/Debian.yml` | fixed list, see `vars/RedHat.yml` |

Default PHP version per supported release (`__php_default_version_debian`, only applies to the Debian family — RedHat family packages are unversioned):

| Release | Default PHP version |
| --- | --- |
| Debian 12 (bookworm) | 8.2 |
| Debian 13 (trixie) | 8.4 |
| Ubuntu 22.04 (jammy) | 8.1 |
| Ubuntu 24.04 (noble) | 8.3 |

## Task Flow

1. **Preflight** (`tasks/preflight.yml`) — asserts ansible-core >= 2.20, that the target's OS family is supported, and (when `php_enable_php_fpm` is `true`) that every `php_fpm_pools` entry has a `pool_name`.
2. **Variable setup** — loads `vars/<OsFamily>.yml`, then `vars/<Distribution>-<MajorVersion>.yml` if present, and computes any `php_*` fact not already defined.
3. **Install** — `setup-RedHat.yml` or `setup-Debian.yml` (package install), or `install-from-source.yml` when `php_install_from_source` is `true`.
4. **Configure** — `configure.yml` (php.ini), `configure-apcu.yml`, `configure-opcache.yml`, `configure-fpm.yml`, each notifying the webserver/php-fpm restart handlers on change.

## Dependencies

None.

## Example Playbook

    - hosts: webservers
      vars_files:
        - vars/main.yml
      roles:
        - { role: php }

*Inside `vars/main.yml`*:

    php_memory_limit: "128M"
    php_max_execution_time: "90"
    php_upload_max_filesize: "256M"
    php_packages:
      - php
      - php-cli
      - php-common
      - php-devel
      - php-gd
      - php-mbstring
      - php-pdo
      - php-pecl-apcu
      - php-xml
      ...

## License

MIT / BSD

## Author Information

Originally created in 2014 by [Jeff Geerling](https://www.jeffgeerling.com/), author of [Ansible for DevOps](https://www.ansiblefordevops.com/). This fork is maintained by Bob Tanner / Real Time Enterprises, Inc.
