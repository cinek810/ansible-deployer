"""Module for formatting outputs from different sources"""

class Formatters:
    """Class handling formatting of ansible standard output and error streams"""

    def __init__(self, logger):
        self.logger = logger

    def positive_ansible_output(self, warning: list, output: list, command: str):
        """Log output for a positive case in ansible execution"""
        if warning:
            for line in warning:
                self.logger.warning(line)
        if output:
            for line in output:
                self.logger.info(line)
        self.logger.info("\"%s\" ran succesfully", " ".join(command))

    def negative_ansible_output(self, warning: list, error: list, command: str):
        """Log output for a negative case in ansible execution"""
        if warning:
            for line in warning:
                self.logger.warning(line)
        self.logger.error("\"%s\" failed due to:", " ".join(command))
        if error:
            for line in error:
                self.logger.error(line)

    @staticmethod
    def format_ansible_output(proces_output):
        """Group and format output from ansible execution"""
        std_out, std_err = proces_output
        std_output = []
        std_warning = []
        std_error = []
        for line in std_out.split(b"\n\n"):
            dec_line = line.decode("utf-8")
            if "fatal" in dec_line.lower() or "err" in dec_line.lower():
                std_error.append(dec_line)
            elif "warn" in dec_line.lower():
                std_warning.append(dec_line)
            else:
                std_output.append(dec_line)

        for line in std_err.split(b"\n\n"):
            dec_line = line.decode("utf-8")
            if "fatal" in dec_line.lower() or "err" in dec_line.lower():
                std_error.append(dec_line)
            elif "warn" in dec_line.lower():
                std_warning.append(dec_line)
            else:
                std_output.append(dec_line)

        return std_output, std_warning, std_error
