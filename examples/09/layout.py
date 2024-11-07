screen_layout = {
    'task_header': {
        'position': (20, 0),
        'text': 'Tasks',
        'text_color': 15,
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
        'text_color': 15,
    },
    'server_header': {
        'position': (2, 5),
        'text': 'ServerName',
        'text_color': 15,
    },
    'version_header': {
        'position': (2, 37),
        'text': 'Ver.',
        'text_color': 15,
    },
    'tasks_header1': {
        'position': (1, 42),
        'text': 'Tasks',
        'text_color': 15,
    },
    'tasks_header2': {
        'position': (2, 42),
        'text': '12345',
        'text_color': 15,
    },
    'message_header': {
        'position': (2, 48),
        'text': 'Messages',
        'text_color': 15,
    },
    '_indicator_on': {
        'position': (3, 0),
        'replace_text': chr(11208),
        'color': 3,
        'regex': r'^executing firmware update on server at bay \d+ at .*$',
        'table': True
    },
    '_indicator_off': {
        'position': (3, 0),
        'replace_text': '  ',
        'regex': r'^processing next bay$',
        'table': True
    },
    'bay': {
        'position': (3, 2),
        'color': 15,
        'regex': r"^'bay' is '(?P<value>\d+)'$",
        'table': True
    },
    'servername': {
        'position': (3, 5),
        'color': 243,
        'regex': r"^'servername' is '(?P<value>.*)'|EX5: firmware update on server (.*) at bay \d+ was successful$",
        'effects': [
            {
                'regex': r'^.* firmware update on server (.*) at bay \d+ was successful$',
                'color': 15
            }
        ],
        'table': True
    },
    'version': {
        'position': (3, 37),
        'color': 243,
        'regex': r"^'firmware version' is '(?P<value>.*)'$",
        'effects_use_matched_value': True,
        'effects': [
            {
                'regex': r'^2.64$',
                'color': 14
            }
        ],
        'table': True
    },
    'task1': {
        'position': (3, 42),
        'replace_text': chr(9632),
        'regex': r'^.*turn.* maintenance mode ON for server at bay \d+$',
        'effects': [
            {
                'regex': r'^.* turned maintenance mode ON .*$',
                'color': 2
            }, {
                'regex': r'^ERROR: .*$',
                'color': 1
            }
        ],
        'table': True
    },
    'task2': {
        'position': (3, 43),
        'replace_text': chr(9632),
        'regex': r'^.*appl.* firmware update for server at bay \d+$',
        'effects': [
            {
                'regex': r'^.* applied firmware update .*$',
                'color': 2
            }, {
                'regex': r'^ERROR: .*$',
                'color': 1
            }
        ],
        'table': True
    },
    'task3': {
        'position': (3, 44),
        'replace_text': chr(9632),
        'regex': r'^.*recycl.* server at bay \d+$',
        'effects': [
            {
                'regex': r'^.* recycled server .*$',
                'color': 2
            }, {
                'regex': r'^ERROR: .*$',
                'color': 1
            }
        ],
        'table': True
    },
    'task4': {
        'position': (3, 45),
        'replace_text': chr(9632),
        'regex': r'^.*verif.* firmware update for server at bay \d+$',
        'effects': [
            {
                'regex': r'^.* verified firmware update .*$',
                'color': 2
            }, {
                'regex': r'^ERROR: .*$',
                'color': 1
            }
        ],
        'table': True
    },
    'task5': {
        'position': (3, 46),
        'replace_text': chr(9632),
        'regex': r'^.*turn.* maintenance mode OFF for server at bay \d+$',
        'effects': [
            {
                'regex': r'^.* turned maintenance mode OFF .*$',
                'color': 2
            }, {
                'regex': r'^ERROR: .*$',
                'color': 1
            }
        ],
        'table': True
    },
    'message': {
        'position': (3, 48),
        'color': 243,
        'clear': True,
        'regex': r'^EX5: (.*)|ERROR: EX5: (.*)$',
        'effects_use_matched_value': True,
        'effects': [
            {
                'regex': r'^failed: .*$',
                'color': 1
            }, {
                'regex': r'^firmware update on server .* at bay \d+ was successful$',
                'color': 2
            }
        ],
        'table': True
    }
}
