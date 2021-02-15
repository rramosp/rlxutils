from joblib import Parallel, delayed
import sys, hashlib, subprocess

class mParallel(Parallel):
    """
    substitutes joblib.Parallel with richer verbose progress information
    """
    def _print(self, msg, msg_args):
        if self.verbose > 10:
            fmsg = '[%s]: %s' % (self, msg % msg_args)
            sys.stdout.write('\r ' + fmsg)
            sys.stdout.flush()

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
