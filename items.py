pkg_dnf = {
    'php-cli': {},
    'php-fpm': {},
}

svc_systemd = {
    'php-fpm': {
        'needs': ['pkg_dnf:php-fpm'],
    },
}

files = {
    '/etc/php-fpm.conf': {
        'source': 'php-fpm.conf',
        'mode': '0644',
        'content_type': 'mako',
        'needs': ['pkg_dnf:php-fpm'],
        'triggers': ['svc_systemd:php-fpm:restart'],
    },
    '/etc/php.ini': {
        'source': 'php.ini',
        'mode': '0644',
        'content_type': 'mako',
        'needs': ['pkg_dnf:php-cli'],
    },
    '/etc/php-fpm.d/www.conf': {
        'delete': True,
        'needs': ['pkg_dnf:php-fpm'],
    },
}

directories = {
    '/var/lib/php/session': {
        'group': 'nginx',
        'mode': '0770',
    },
}

for pkg in node.metadata['php']['packages']:
    pkg_dnf['php-' + pkg] = {
        'needs': ['pkg_dnf:php-fpm', 'pkg_dnf:php-cli'],
        'triggers': ['svc_systemd:php-fpm:restart'],
    }

for pool_name, pool_options in sorted(node.metadata.get('php', {}).get('fpm_pools', {}).items()):
    files['/etc/php-fpm.d/{}.conf'.format(pool_name)] = {
        'source': 'fpm_pool_template',
        'mode': '0644',
        'content_type': 'mako',
        'context': {
            'pool_name': pool_name,
            'pool_options': pool_options,
        },
        'needs': ['pkg_dnf:php-fpm'],
        'triggers': ['svc_systemd:php-fpm:restart'],
    }

if node.has_bundle('monit'):
    files['/etc/monit.d/php-fpm'] = {
        'source': 'monit',
        'mode': '0640',
        'content_type': 'mako',
        'triggers': ['svc_systemd:monit:restart'],
    }
