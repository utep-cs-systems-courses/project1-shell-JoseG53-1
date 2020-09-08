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

#TODO:
#implement 
def change_directory(cmd):
    pass

def execute_command(cmd):
    rc = os.fork()

    if rc < 0:
        os.write(2,("fork failed, returning %d\n" % rc).encode())
        sys.exit(1)
    
    elif rc == 0:
        os.write(1, ("Child: My pid==%d. Parent's pid=%d\n" % (os.getpid(), pid)).encode())
        time.sleep(1)
        os.write(1, "Child .......terminating now with exit code 0\n".encode())
        sys.exit(0)
    
    else:
        os.write(1, ("Parent: My pid=%d. Child's pid=%d\n" % (pid, rc)).encode())
        childpidcode = os.wait()
        os.write(1, ("Parent: Child %d terminated with exit code %d\n" % childpidcode).encode())

def process_user_input(cmd):
    if cmd == '':
        if not os.isatty(sys.stdin.fileno()): #checks if fd is open and connected to a tty
            sys.exit(0)
        return
    elif 'exit' in cmd:
        sys.exit(0)
    elif 'cd' in cmd:
        change_directory(cmd)
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