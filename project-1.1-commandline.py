import sys
import os
import subprocess

class Shell:
    def __init__(self):
        self.builtins = {
            "echo": self.shell_echo,
            "/bye": self.shell_exit,
            "type": self.shell_type,
            "pwd": self.show_dir,
            "cd": self.move_dir,
            "ls": self.list_dir,
            "mkdir": self.make_dir,
            "rmdir": self.remove_dir,
            "touch": self.touch_file,  
            "rm": self.remove_file,    
        }

    def shell_echo(self, args):
        print(" ".join(args))

    def shell_exit(self, args):
        try:
            exit_code = int(args[0]) if args else 0
        except ValueError:
            exit_code = 0
        sys.exit(exit_code)

    def shell_type(self, args):
        if not args:
            return
        command = args[0]
        if command in self.builtins:
            print(f"{command} is a shell builtin")
        elif command_path := self.find_command_in_path(command):
            print(f"{command} is {command_path}")
        else:
            print(f"{command} not found")

    def show_dir(self, args):
        print(f"{os.getcwd()}")

    def move_dir(self, args):
        path = "".join(args)
        path = os.path.expanduser(path)
        try:
            os.chdir(path)
        except FileNotFoundError:
            print(f"cd: {path}: No such file or directory")

    def list_dir(self, args):
        path = args[0] if args else "."
        try:
            with os.scandir(path) as it:
                for entry in it:
                    if entry.is_dir():
                        print(f"{entry.name}/")
                    else:
                        print(entry.name)
        except FileNotFoundError:
            print(f"ls: {path}: No such file or directory")

    def make_dir(self, args):
        if not args:
            print("mkdir: missing operand")
            return
        for dir_name in args:
            try:
                os.mkdir(dir_name)
            except FileExistsError:
                print(f"mkdir: cannot create directory '{dir_name}': File exists")
            except FileNotFoundError:
                print(f"mkdir: cannot create directory '{dir_name}': No such file or directory")

    def remove_dir(self, args):
        if not args:
            print("rmdir: missing operand")
            return
        for dir_name in args:
            try:
                os.rmdir(dir_name)
            except FileNotFoundError:
                print(f"rmdir: failed to remove '{dir_name}': No such file or directory")
            except OSError:
                print(f"rmdir: failed to remove '{dir_name}': Directory not empty or other error")

    def touch_file(self, args):
        if not args:
            print("touch: missing operand")
            return
        for file_name in args:
            try:
                with open(file_name, 'a'):
                    os.utime(file_name, None)
            except FileNotFoundError:
                print(f"touch: cannot touch '{file_name}': No such file or directory")
            except Exception as e:
                print(f"touch: cannot touch '{file_name}': {e}")

    def remove_file(self, args):
        if not args:
            print("rm: missing operand")
            return
        for file_name in args:
            try:
                os.remove(file_name)
            except FileNotFoundError:
                print(f"rm: cannot remove '{file_name}': No such file")
            except IsADirectoryError:
                print(f"rm: cannot remove '{file_name}': Is a directory")
            except Exception as e:
                print(f"rm: cannot remove '{file_name}': {e}")

    def find_command_in_path(self, command):
        path_dirs = os.environ.get("PATH", "").split(os.pathsep)
        for dir in path_dirs:
            potential_path = os.path.join(dir, command)
            if os.path.isfile(potential_path) and os.access(potential_path, os.X_OK):
                return potential_path
        return None

    def execute_command(self, command_line):
        parts = command_line.split()
        if not parts:
            return
        cmd_name = parts[0]
        cmd_args = parts[1:]
        if cmd_name in self.builtins:
            self.builtins[cmd_name](cmd_args)
        else:
            self.run_external_program(cmd_name, cmd_args)

    def run_external_program(self, program_name, program_args):
        try:
            result = subprocess.run(
                [program_name] + program_args,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )
            if result.returncode == 0:
                for line in result.stdout.splitlines():
                    print(line)
            else:
                for line in result.stderr.splitlines():
                    print(line, end="")
        except FileNotFoundError:
            print(f"{program_name}: command not found")

    def run(self):
        while True:
            sys.stdout.write("$ ")
            sys.stdout.flush()
            try:
                command_line = input().strip()
                self.execute_command(command_line)
            except (EOFError, KeyboardInterrupt):
                print()
                break

if __name__ == "__main__":
    shell = Shell()
    shell.run()
