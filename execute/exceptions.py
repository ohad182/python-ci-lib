class ExecuteException(Exception):
    def __init__(self, message=None, execute_result=None):
        self.execute_result = execute_result
        self.message = self.get_message() if message is None else message
        super(ExecuteException, self).__init__(self.message)

    def get_details(self):
        lines = self.execute_result.get_output_lines()
        return "\n".join(lines[-5:])

    def get_message(self):
        if self.message is None:
            return "'{}' returned exit code {}".format(' '.join(self.execute_result.command),
                                                       self.execute_result.return_code)
        else:
            return self.message

    def __str__(self):
        return self.message


class ExecuteTimeout(ExecuteException):
    def __init__(self, message=None, execute_result=None):
        super(ExecuteTimeout, self).__init__(message, execute_result)
        if self.message is None:
            self.message = "Script [Timed-out] {} returned exit code {}".format(' '.join(self.execute_result.command),
                                                                                self.execute_result.return_code)
