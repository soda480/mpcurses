def get_screen_layout():
    return {
        'task_header': {
            'position': (20, 0),
            'text': 'Tasks',
            'text_color': 244,
        },
        'task1_header': {
            'position': (21, 1),
            'text': '1: turn maintenance mode ON',
            'text_color': 15,
        },
        'task2_header': {
            'position': (22, 1),
            'text': '2: apply firmware update',
            'text_color': 15,
        },
        'task3_header': {
            'position': (23, 1),
            'text': '3: recycle server',
            'text_color': 15,
        },
        'task4_header': {
            'position': (24, 1),
            'text': '4: verify firmware update',
            'text_color': 15,
        },
        'task5_header': {
            'position': (25, 1),
            'text': '5: turn maintenance mode OFF',
            'text_color': 15,
        },
        'bay_header': {
            'position': (2, 1),
            'text': 'Bay',
            'text_color': 244,
        },
        'server_header': {
            'position': (2, 5),
            'text': 'Server Name',
            'text_color': 244,
        },
        'version_header': {
            'position': (2, 27),
            'text': 'Ver.',
            'text_color': 244,
        },
        'tasks_header1': {
            'position': (1, 32),
            'text': 'Tasks',
            'text_color': 244,
        },
        'tasks_header2': {
            'position': (2, 32),
            'text': '12345',
            'text_color': 244,
        },
        'message_header': {
            'position': (2, 38),
            'text': 'Messages',
            'text_color': 244,
        },
        '_indicator_on': {
            'position': (3, 0),
            'text': '',
            'replace_text': '=>',
            'color': 14,
            'regex': r'^executing firmware update on server at bay \d+$',
            'table': True
        },
        '_indicator_off': {
            'position': (3, 0),
            'text': '',
            'replace_text': '  ',
            'regex': r'^processing next bay$',
            'table': True
        },
        'bay': {
            'position': (3, 2),
            'text': '',
            'color': 243,
            'regex': r"^'bay' is '(?P<value>\d+)'$",
            'table': True
        },
        'servername': {
            'position': (3, 5),
            'text': '',
            'color': 15,
            'regex': r"^'servername' is '(?P<value>.*)'$",
            'table': True
        },
        'version': {
            'position': (3, 27),
            'text': '',
            'color': 243,
            'regex': r"^'firmware version' is '(?P<value>.*)'$",
            'effects': [
                {
                    'regex': r'.*2.64.*$',
                    'color': 2
                }
            ],
            'table': True
        },
        'task1': {
            'position': (3, 32),
            'text': '',
            'replace_text': '|',
            'regex': r'^.*turn.* maintenance mode ON for server at bay \d+$',
            'effects': [
                {
                    'regex': r'^turned maintenance mode ON for server at bay \d+$',
                    'color': 2
                }, {
                    'regex': r'^ERROR: .*$',
                    'color': 237
                }
            ],
            'table': True
        },
        'task2': {
            'position': (3, 33),
            'text': '',
            'replace_text': '|',
            'regex': r'^.*appl.* firmware update for server at bay \d+$',
            'effects': [
                {
                    'regex': r'^applied firmware update for server at bay \d+$',
                    'color': 2
                }, {
                    'regex': r'^ERROR: .*$',
                    'color': 237
                }
            ],
            'table': True
        },
        'task3': {
            'position': (3, 34),
            'text': '',
            'replace_text': '|',
            'regex': r'^.*recycl.* server at bay \d+$',
            'effects': [
                {
                    'regex': r'^recycled server at bay \d+$',
                    'color': 2
                }, {
                    'regex': r'^ERROR: .*$',
                    'color': 237
                }
            ],
            'table': True
        },
        'task4': {
            'position': (3, 35),
            'text': '',
            'replace_text': '|',
            'regex': r'^.*verif.* firmware update for server at bay \d+$',
            'effects': [
                {
                    'regex': r'^verified firmware update for server at bay \d+$',
                    'color': 2
                }, {
                    'regex': r'^ERROR: .*$',
                    'color': 237
                }
            ],
            'table': True
        },
        'task5': {
            'position': (3, 36),
            'text': '',
            'replace_text': '|',
            'regex': r'^.*turn.* maintenance mode OFF for server at bay \d+$',
            'effects': [
                {
                    'regex': r'^turned maintenance mode OFF for server at bay \d+$',
                    'color': 2
                }, {
                    'regex': r'^ERROR: .*$',
                    'color': 237
                }
            ],
            'table': True
        },
        'message': {
            'position': (3, 38),
            'text': '',
            'color': 14,  # 149,
            'clear': True,
            'regex': r'^(?!mpcurses:.*)(?!processing next bay)(?!DONE)(?!INFO:.*)(?P<value>.*)$',
            'effects': [
                {
                    'regex': r'^ERROR: .*$',
                    'color': 244
                }, {
                    'regex': r'^firmware update on server at bay \d+ was successful$',
                    'color': 15
                }
            ],
            'table': True
        }
    }
