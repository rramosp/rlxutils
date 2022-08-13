from joblib import Parallel, delayed
import sys, hashlib, subprocess
import matplotlib.pyplot as plt
import numpy as np
from time import time
import types
import functools
import sys
import shlex
from subprocess import PIPE, Popen
from threading  import Thread
from time import sleep


def copy_func(f):
    """
    creates a new function object copying an existing one
    Based on http://stackoverflow.com/a/6528148/190597 (Glenn Maynard)
    """
    g = types.FunctionType(f.__code__, f.__globals__, name=f.__name__,
                           argdefs=f.__defaults__,
                           closure=f.__closure__)
    g = functools.update_wrapper(g, f)
    g.__kwdefaults__ = f.__kwdefaults__
    return g

class mParallel(Parallel):
    """
    substitutes joblib.Parallel with richer verbose progress information
    """
    def _print(self, msg, msg_args):
        if self.verbose > 10:
            fmsg = '[%s]: %s' % (self, msg % msg_args)
            sys.stdout.write('\r ' + fmsg)
            sys.stdout.flush()

def subplots(elems, n_cols=None, usizex=3, usizey=3 ):
    """
    generates grid with a subplot for each elem in elems. for instance:

       for ax,i in subplots(2):
           if i==0:
              ax.scatter(....)
           if i==1:
              ax.plot(...)


    elems: an iterable, or an integer 
    n_cols: the number of columns for the grid. If none it is set to min(num elems, 15)
    usizex, usizey: size of each subplot
    """
    
    if type(elems)==int:
        elems = np.arange(elems) 

    n_elems = len(elems)
    
    if n_cols is None:
        n_cols = n_elems if n_elems<=15 else 15
    
    n_rows = n_elems//n_cols + int(n_elems%n_cols!=0)
    fig = plt.figure(figsize=(n_cols*usizex, n_rows*usizey))
    
    for i in range(n_elems):
        ax = fig.add_subplot(n_rows, n_cols, i+1)
        yield ax, elems[i]

    plt.tight_layout()

class ElapsedTimes:
    """
    usage

    et = ElapsedTimes():

    with et("stage 1"):
       ... some python code...

    with et("stage 2"):
       ... other python code...

 
    print (et.elapsed_times)

    """
    def __init__(self):
        self.start_times = {}
        self.elapsed_times = {}

    def __enter__(self):
        self.start_times[self.current_key] = time()
        return self        
        
    def __exit__(self, exc_type, exc_value, exc_traceback):
        key = self.current_key
        if key not in self.elapsed_times.keys():
            self.elapsed_times[key] = 0

        if key in self.start_times.keys():
            self.elapsed_times[key] += time() - self.start_times[key]
        
    def __call__(self, key):
        self.current_key = key
        return self

    def __repr__(self):
        return str(self.elapsed_times)

split = lambda a, chunk_size: [a[x:x+chunk_size] for x in np.arange(0, len(a), chunk_size)]

def md5hash(s):
    """
    Parameters:
    -----------
    s : str
      a string 

    Returns:
    --------
    h : str
      a string containing the MD5 hash of 's'
    """

    m = hashlib.md5()
    m.update(bytes(s, "utf-8"))
    return m.hexdigest()

class Command:
    
    def __init__(self, cmd, print_out = False):
        """
        Runs a command in the underlying shell

        Parameters:
        -----------

        cmd : str
            string containing the command to run

        print_out : bool
            if True prints out stdout and stderr after capturing it     
            
            
        typical usage:
        
            # wait for command completion
            c = Command("ls -las").run().wait()
            print (c.stdout())
            print (c.stderr())
            
            # run in background
            c = Command("ls -las").run().wait()
            # at any time get stdout or stderr
            print (c.stdout())
            # at any time check if finished
            if c.isfinished():
                print ("finished")
            
        """
        self.cmd = cmd
        self.print_out = print_out
        
        self._stdout = []
        self._stderr = []
        
    def stdout(self):
        return "\n".join(self._stdout)
        
    def stderr(self):
        return "\n".join(self._stderr)
        
    def exitcode(self):
        return self.p.poll()
    
    def isrunning(self):
        return self.p.poll() is None    

    def isfinished(self):
        return not self.isrunning()        
    
    def wait(self, raise_exception_on_error=False):
        """
        waits until process is finished
        """
        self.p.wait()
        while self.tout.is_alive() or self.terr.is_alive():
            sleep(.1)

        if raise_exception_on_error and self.exitcode()!=0:
            msg = f"""command failed with exit code {self.exitcode()}
--- stdout ---
{self.stdout()}
--- stderr ---
{self.stderr()}
            """
            raise ValueError(msg)
        return self
        
    def append_stdout(self):
        for line in iter(self.p.stdout.readline, b''):
            line = str(line.decode()).strip()
            self._stdout.append(line)
            if self.print_out:
                print (line, flush=True)
        self.p.stdout.close()    

    def append_stderr(self):
        for line in iter(self.p.stderr.readline, b''):
            line = str(line.decode()).strip()
            self._stderr.append(line)
            if self.print_out:
                print (line, file=sys.stderr, flush=True)
        self.p.stderr.close()    
        
    def run(self):
        """
        executes the process
        """
        scmd = shlex.split(self.cmd)

        ON_POSIX = 'posix' in sys.builtin_module_names

        self.p = Popen(scmd, stdout=PIPE, stderr=PIPE, close_fds=ON_POSIX)

        self.tout = Thread(target=self.append_stdout, args=())
        self.tout.daemon = True # thread dies with the program
        self.tout.start()

        self.terr = Thread(target=self.append_stderr, args=())
        self.terr.daemon = True # thread dies with the program
        self.terr.start()

        return self


def command(cmd, print_out = False):
    """
    Runs a command in the underlying shell. Will be deprecated.

    Parameters:
    -----------

    cmd : str
        string containing the command to run

    print_out : bool
        if True prints out stdout and stderr after capturing it

    Returns:
    --------
    code:  int
        return code from the executed command

    stdout: str
        captured standard output from the command

    stderr: str
        captured standard error from the command

    """
    import sys
    import shlex
    from subprocess import PIPE, Popen
    from threading  import Thread
    from queue import Queue, Empty
    from time import sleep

    warn("This function is deprecated. Use the class Command instead", stacklevel=2)

    scmd = shlex.split(cmd)
    
    ON_POSIX = 'posix' in sys.builtin_module_names
    
    def enqueue_stdout(out, queue):
        for line in iter(out.readline, b''):
            line = str(line.decode()).strip()
            if print_out:
                print (line, flush=True)
            queue.put(line)
        out.close()

    def enqueue_stderr(out, queue):
        for line in iter(out.readline, b''):
            line = str(line.decode()).strip()
            if print_out:
                print (line, file=sys.stderr, flush=True)
            queue.put(line)
        out.close()    

    p = Popen(scmd, stdout=PIPE, stderr=PIPE, close_fds=ON_POSIX)
    
    qout = Queue()
    tout = Thread(target=enqueue_stdout, args=(p.stdout, qout))
    tout.daemon = True # thread dies with the program
    tout.start()

    qerr = Queue()
    terr = Thread(target=enqueue_stderr, args=(p.stderr, qerr))
    terr.daemon = True # thread dies with the program
    terr.start()

    p.wait()

    while tout.is_alive() or terr.is_alive():
        sleep(.1)
    
    strout = "\n".join([qout.get() for _ in range(qout.qsize())])
    strerr = "\n".join([qerr.get() for _ in range(qerr.qsize())])

    return p.returncode, strout, strerr



def qplot(x, pctles_clip=5, **kwargs):
    """
    makes a percentiles vs quantiles plot
    pctles_clip: if 5, will take percentiles from 5 to 95 in increments of 1%
    """
    pctls = np.linspace(0,100,101)[pctles_clip:-pctles_clip]
    qntls = np.percentile(x, pctls)
    plt.plot(pctls, qntls, **kwargs)
    plt.xlabel("percentiles")
    plt.ylabel("values")
