#Author: Jose Gallardo
#Description: Simple shell in pyhton
#Note: 
#fd0 is for standard input
#fd1 is for statndard output
#fd2 is for standard error

import sys, os, re 

pid = os.getpid()

def get_input():
    return os.read(0, 1024).decode()[:-1]

def change_directory(cmd):
    command, path = re.split(' ', cmd) #Because command is cd PATH
    if path != '..':
        path = os.getcwd() + '/' + path
    os.chdir(path)

def execute_command(cmd):
    rc = os.fork()

    if rc < 0:
        os.write(2,("fork failed, returning %d\n" % rc).encode())
        sys.exit(1)
    
    elif rc == 0:
        args = [i.strip() for i in re.split(" ", cmd)]
        if '/' in args[0]:
            exec_path(args)
        else:
            global_exec(args)
        os.write(2, ("Command %s not found\n" % args[0]).encode())
        sys.exit(1)
    
    else:
        r_child = os.waitpid(rc, 0)

def global_exec(args):
    for dir in re.split(":", os.environ['PATH']): # :
        program = "%s/%s" % (dir, args[0])
        try:
            os.execve(program, args, os.environ)
        except FileNotFoundError:
            pass 

def exec_path(args):
    try:
        os.execve(args[0], args, os.environ)
    except FileNotFoundError:
        pass   

def redirect_output(cmd):
    command, path = [i.strip() for i in re.split(">", cmd)] # splits by the > symbol
    path = os.getcwd() + '/' + path
    command = [i.strip() for i in re.split(" ", command)]

    rc = os.fork()
    if rc < 0:
        os.write(2, ("fork failed, returning %d\n").encode())
        sys.exit(1)
    elif rc == 0:
        os.close(1) #close stdout

        sys.stdout = open(path, "w+")
        fd = sys.stdout.fileno()
        os.set_inheritable(fd, True)
        os.dup(fd)

        global_exec(command)
        os.write(2, ("Command %s not found\n" % args[0]).encode())
        sys.exit(1)
    else:
        r_child = os.waitpid(rc, 0)

def redirect_input(cmd):
    command, path = [i.strip() for i in re.split("<", cmd)] # splits by the < symbol
    path = os.getcwd() + '/' + path
    command = [i.strip() for i in re.split(" ", command)]

    rc = os.fork()
    if rc < 0:
        os.write(2, ("fork failed, returning %d\n").encode())
        sys.exit(1)
    elif rc == 0:
        os.close(0) #close stdin

        sys.stdout = open(path, "r")
        fd = sys.stdout.fileno()
        os.set_inheritable(fd, True)
        os.dup(fd)

        global_exec(command)
        os.write(2, ("Command %s not found\n" % args[0]).encode())
        sys.exit(1)
    else:
        r_child = os.waitpid(rc, 0)

def simple_pipe_cmd(cmd):
    r,w = os.pipe()
    for fd in (r, w):
        os.set_inheritable(fd, True)
    
    commands = [i.strip() for i in re.split('[\x7c]', cmd)] # split by | had to use hex beacause "|" would split by char
    print("COMMANDS")
    print(commands)
    rc = os.fork()

    if rc < 0: #fork failed
        os.write(2, ("fork failed, returning %d\n" % rc).encode())
        sys.exit(1)

    if rc == 0: #child
        os.close(1) #close stdout
        os.dup(w)
        os.set_inheritable(1, True)
        for fd in (r, w):
            os.close(fd)
        global_exec(commands[0].split())
    else:
        os.close(0) #close stdin
        os.dup(r)
        os.set_inheritable(0, True)
        for fd in (w, r):
            os.close(fd)
        global_exec(commands[1].split())



#TODO
def run_in_background(cmd):
    print("IN THE BACKGROUND METHOD")
    command, amp= [i.strip() for i in re.split("&", cmd)]
    print("COMMAND IN BACKGROUND")
    print(command)
    command, task = [i.strip() for i in re.split(" ", command)]  
    pass


def process_user_input(cmd):
    if cmd == '':
        if not os.isatty(sys.stdin.fileno()): #checks if fd is open and connected to a tty
            sys.exit(0)
        return
    elif 'exit' in cmd:
        sys.exit(0)
    elif 'cd' in cmd:
        change_directory(cmd)
    elif '^C' in cmd:
        sys.exit(0)
    elif '>' in cmd:
        redirect_output(cmd)
    elif '<' in cmd:
        redirect_input(cmd)
    elif '|' in cmd:
        simple_pipe_cmd(cmd)
    elif '&' in cmd:
        run_in_background(cmd)
    else:
        execute_command(cmd)

try:
    sys.ps1 = os.environ['PS1']
except KeyError:
    sys.ps1 = '$ '

if sys.ps1 is None:
    sys.ps1 = '$ '

if __name__ == "__main__":
    while True:
        os.write(1, sys.ps1.encode())
        cmd = get_input()
        process_user_input(cmd)