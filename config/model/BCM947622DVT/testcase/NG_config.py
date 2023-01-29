test_cfg = {
    'telog_validate': [
        [
            ('Testcase', [
                ('server', {
                    'env': {
                        'dut': 'ssh plume@192.168.4.10 -- source /etc/profile && sh -axe',
                        'logno': '256',
                        'syslog_tail': 'logread -f',
                        'tmpdir': '/tmp',
                    },
                }),
            ]),
        ],
        [
            ('Testcase', [
                ('server', {
                    'env': {
                        'dut': 'ssh plume@192.168.4.10 -- source /etc/profile && sh -axe',
                        'logno': '1024',
                        'syslog_tail': 'logread -f',
                        'tmpdir': '/tmp',
                    },
                }),
            ]),
        ],
    ],
}
