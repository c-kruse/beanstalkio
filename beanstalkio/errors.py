class BeanstalkioError(Exception):
    pass


class BeanstalkdConnection(BeanstalkioError):
    pass


class CommandError(BeanstalkioError):
    def __init__(self, error_code, *args, **kwargs):
        self.error_code = error_code
        super(CommandError, self).__init__(*args, **kwargs)

    def __repr__(self):
        return f"CommandError({self.error_code})"
