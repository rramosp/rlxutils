from joblib import Parallel, delayed
import sys, hashlib, subprocess
import matplotlib.pyplot as plt
import numpy as np
from time import time

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

def command(cmd):
    """
    Runs a command in the underlying shell

    Parameters:
    -----------

    cmd : str
        string containing the command to run

    Returns:
    --------
    code:  int
        return code from the executed command

    stdout: str
        captured standard output from the command

    stderr: str
        captured standard error from the command

    """
    try:
        # search for single quoted args (just one such arg is accepted)
        init = cmd.find("'")
        end  = len(cmd)-cmd[::-1].find("'")
        if init>0 and init!=end-1:
            scmd = cmd[:init].split() + [cmd[init+1:end-1]] + cmd[end+1:].split()
        else:
            scmd = cmd.split()

        p = subprocess.Popen(scmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout,stderr = p.communicate()
        code = p.returncode
    except Exception as e:
        stderr = str(e)
        code = 127
        stdout = ""

    stdout = stdout.decode() if type(stdout)==bytes else stdout
    stderr = stderr.decode() if type(stderr)==bytes else stderr

    return code, stdout, stderr
