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
    #os.write(1,("Current Working Directory " + os.getcwd()).encode())
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


def process_user_input(cmd):
    if cmd == '':
        if not os.isatty(sys.stdin.fileno()): #checks if fd is open and connected to a tty
            sys.exit(0)
        return
    elif 'exit' in cmd:
        sys.exit(0)
    elif 'cd' in cmd:
        change_directory(cmd)
    elif '^C' in cmd: # ^C
        sys.exit(0)
    elif '>' in cmd: # >
        redirect_output(cmd)
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