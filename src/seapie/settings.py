# State that will persist over different calls to prompt().
# These settings can be modified by anyone anywhere. they are not passed as
# arguments. these are as global of a variable as possible.
# this referenced to by various functions in this module randomly.
CURRENT_SETTINGS = {
    "show_bar": True,
    "callstack_escape_level": 0,
    "step_until_expression": None,
    "previous_bang": "!help",
    "echo_count": 0,
}


__DEFAULT_SETTINGS__ = {
    "show_bar": True,
    "callstack_escape_level": 0,
    "step_until_expression": None,
    "previous_bang": "!help",
    "echo_count": 0,
}
