pkg_dnf = {
    'php-cli': {},
    'php-fpm': {},
}

svc_systemd = {
    'php-fpm': {
        'enabled': True,
        'needs': [
            'pkg_dnf:php-fpm',
        ],
    },
}

files = {
    '/etc/php-fpm.conf': {
        'source': "php-fpm.conf",
        'owner': "root",
        'group': "root",
        'mode': "0644",
        'content_type': "mako",
        'needs': [
            "pkg_dnf:php-fpm",
        ],
        'triggers': [
            "svc_systemd:php-fpm:restart",
        ],
    },
    '/etc/php.ini': {
        'source': 'php.ini',
        'owner': 'root',
        'group': 'root',
        'mode': '0644',
        'content_type': 'mako',
        'needs': [
            "pkg_dnf:php-cli",
        ],
    },
    '/etc/php-fpm.d/www.conf': {
        'delete': True,
        'needs': [
            "pkg_dnf:php-fpm",
        ],
    },
}

for pkg in node.metadata['php']['packages']:
    pkg_dnf["php-" + pkg] = {
        'needs': [
            "pkg_dnf:php-fpm",
            "pkg_dnf:php-cli",
        ],
    }

for pool_name, pool_options in sorted(node.metadata.get('php', {}).get('fpm_pools', {}).items()):
    files['/etc/php-fpm.d/{}.conf'.format(pool_name)] = {
        'source': 'fpm_pool_template',
        'owner': 'root',
        'group': 'root',
        'mode': '0644',
        'content_type': 'mako',
        'context': {
            'pool_name': pool_name,
            'pool_options': pool_options,
        },
        'needs': [
            "pkg_dnf:php-fpm",
        ],
        'triggers': [
            "svc_systemd:php-fpm:restart",
        ],
    }

if node.has_bundle("monit"):
    files['/etc/monit.d/php-fpm'] = {
        'source': "monit",
        'mode': "0640",
        'owner': "root",
        'group': "root",
        'content_type': "mako",
        'triggers': [
            "svc_systemd:monit:restart",
        ],
    }
