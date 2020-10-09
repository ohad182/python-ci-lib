import os
import subprocess
import threading
import platform
import shlex
import time

from execute.exceptions import ExecuteTimeout
from execute.utils import create_dir_for_file

if platform.python_version().split(".")[0] == '2':
    from io import BytesIO as StringIO

    is_py_3 = False
else:
    from io import StringIO

    is_py_3 = True


def chomp(line):
    if isinstance(line, bytes):
        line = line.decode('utf-8')
    elif isinstance(line, list):
        line = " ".join(line)
    return line.rstrip("\r\n\r")


def read_stream_lines(stream, lines_count=1):
    lines = []
    for i in range(lines_count):
        line = stream.readline()
        if line:
            lines.append(line)
        else:
            break
    if len(lines) == 0:
        lines = None
    if lines:
        lines = b'\n'.join(lines).decode('utf-8')

        return lines


class Execute(object):
    def __init__(self, output=None, console=True):
        self.running_process = None
        self.command = None
        self.output_stream = None
        self.output_path = output
        self.console = console
        self.return_code = None
        self.output_content = None
        self.start_time = None
        self.end_time = None
        self.duration = 0
        self.exception = None

    def read_process(self, stream):
        if self.running_process is not None:
            while self.running_process.poll() is None:
                lines = read_stream_lines(stream, 2)
                self.write(lines)

            lines = read_stream_lines(stream, 20)
            while lines:
                self.write(lines)
                lines = read_stream_lines(stream, 20)
                if self.exception and isinstance(self.exception, ExecuteTimeout):
                    break

    def close(self):
        self.output_stream.close()

    def get_command_as_str(self):
        cmd = self.command
        if not isinstance(cmd, str):
            cmd = " ".join(cmd)
        return cmd

    def write(self, line):
        if line:
            if self.console:
                print(line)
            self.output_stream.write(line)
            self.output_stream.flush()

    def get_output(self, strip=True, exclude_command=False, exclude_cwd=False):
        if self.output_content is None:
            if isinstance(self.output_stream, StringIO):  # in case working with IO object
                self.output_content = self.output_stream.getvalue()
            elif self.output_path is not None:  # in case working with actual file
                with open(self.output_path, "r") as out:
                    self.output_content = out.read()
            self.output_content = str(self.output_content)
        output = self.output_content
        if exclude_command:
            cmd = self.get_command_as_str()
            output = output.replace(cmd, "", 1)
        if exclude_cwd and "running in " in output:
            first_newline_index = output.index("\n")
            output = output[first_newline_index + 1:]

        if strip:
            output = output.strip()
        return output

    def get_output_lines(self, strip=True, exclude_command=False, exclude_cwd=False):
        return self.get_output(strip=strip, exclude_command=exclude_command, exclude_cwd=exclude_cwd).splitlines()

    def kill(self):
        self.running_process.kill()

    def __kill_by_timeout__(self):
        self.kill()
        self.exception = ExecuteTimeout(execute_result=self)

    def execute(self, cmd, output_full_path=None, cwd=None, env=None, timeout_sec=7200):
        self.command = cmd
        if isinstance(cmd, str):
            if "\"" in self.command:
                self.command = shlex.split(self.command)
            else:
                self.command = cmd.split(" ")
        if self.output_stream is not None:
            self.close()

        if isinstance(output_full_path, StringIO):
            self.output_stream = output_full_path
        elif output_full_path is None:
            self.output_stream = StringIO()
        else:
            self.output_path = output_full_path
            create_dir_for_file(output_full_path)
            self.output_stream = open(output_full_path, "w")

        if cwd is None:
            cwd = os.getcwd()
        self.write("running in {}\n".format(cwd))

        self.write("{}\n".format(" ".join(self.command)))

        p_env = os.environ.copy()

        if env is not None and isinstance(env, dict):
            for k, v in env.items():
                p_env[k] = v
        timer = threading.Timer(timeout_sec, self.__kill_by_timeout__)

        self.start_time = time.time()

        try:
            self.running_process = subprocess.Popen(self.command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                                                    cwd=cwd, env=p_env)

            out_t = threading.Thread(target=self.read_process, args=(self.running_process.stdout,))
            timer.start()
            out_t.start()
            out_t.join()
        except Exception as e:
            print(e)
        finally:
            timer.cancel()

        self.end_time = time.time()
        self.duration = self.end_time - self.start_time
        self.return_code = self.running_process.returncode
        return self.return_code


def run(cmd, output_path=None, console=True, cwd=None, env=None, check_output=False, timeout_sec=7200):
    execute = Execute(console=console)
    execute.execute(cmd, output_path, cwd=cwd, env=env, timeout_sec=timeout_sec)
    if check_output and execute.return_code != 0 and execute.exception is not None:
        raise execute.exception
    return execute
