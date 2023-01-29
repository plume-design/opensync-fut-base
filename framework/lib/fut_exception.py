"""Module containing custom FUT exception."""


class FutException:
    """FutException class."""

    def __init__(self):
        self.exceptions = {}

    def fut_raise(self, cmd_res):
        """Raise custom FUT exception.

        Args:
            cmd_res (list): Command to raise exception on

        Raises:
            type: Exception type
            self.exceptions: Exception
        """
        cmd_ec = cmd_res[0]
        std_out = cmd_res[1]
        std_err = cmd_res[2]
        if type(std_out) == str:
            std_out = std_out.splitlines()

        for std_line in std_out:
            std_line = str(std_line)
            if 'FutShellException' not in std_line:
                continue
            try:
                # |FES| = Shell splitter string for Exception generation
                shell_exc_split = std_line.split('|FES|')
                # Mark all FutShellException-s as FAIL (no broken status in reports)
                shell_exc_type = AssertionError
                shell_exc_name = shell_exc_split[2]
                shell_exc_msg = shell_exc_split[3]
            except Exception as exception:
                exc_str = 'Invalid FutShellException line provided'
                raise type('ShellInvalidException', (Exception,), {})(f'{exc_str}\n{std_line}\n{exception}')

            if shell_exc_type.__name__ not in self.exceptions:
                self.exceptions[shell_exc_type.__name__] = {}
            if shell_exc_split[2] not in self.exceptions[shell_exc_type.__name__]:
                self.exceptions[shell_exc_type.__name__][shell_exc_name] = type(shell_exc_name, (shell_exc_type,), {})

            raise self.exceptions[shell_exc_type.__name__][shell_exc_name](f"{shell_exc_msg}\nec: {cmd_ec}\n std_err: {std_err}")
