import subprocess

failures = 0

def run(commands, shell=False, env={}):
    """ Runs commands passed as a list of lists."""
    for command in commands:
        for line in execute(command, shell=shell, env=env):
            print line


def execute(command, shell=False, env={}):
    global failures
    proc = subprocess.Popen(command, stderr=subprocess.STDOUT, shell=shell, env=env, universal_newlines=True)
    if proc.stdout:
        for line in iter(proc.stdout.readline, ""):
            yield line
        proc.stdout.close()
    return_code = proc.wait()
    if return_code:
        if failures < 2:
            failures = failures + 1
            execute(command, shell, env)
        else:
            raise subprocess.CalledProcessError(return_code, command)
    print '\n'
