from lk_utils.subproc import compose_cmd

print(
    compose_cmd(
        'bore',
        'local',
        ('-t', '123.456.789'),
        ('-p', '8080'),
        ('-s', ''),
        '3000',
    )
)
