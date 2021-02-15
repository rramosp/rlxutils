import numpy as np
from scipy.optimize import minimize
from collections import namedtuple

def coordinate_descent_minimize(f, x0, max_iters=10, max_tol=1e-9, **kw_minimize_args):
    """
    coordinate descent minimization, using scipy.minimize for each coordinate in 
    consecutive order while fixing the rest.
    
    f,x0: just like scipy.minimize
    max_iter: maximum number of iterations. each iteration will loop over all coordinates
              calling scipy.minimize each time.
    max_tol:  maximum solution vector change under which iterations will continue until 
              reaching max_iter. if the change of the solution vector in consecutive 
              iterations is <max_tol optimization will finish.
              
    returns:  a dict object with optimization information. "x" will contain the final solution.
    
    """
    x = np.r_[x0].copy()
    x_hist = [x.copy()]
    message = "reached max_iters=%d"%max_iters
    for t in range(max_iters):        
        last_x = x.copy()
        rset = []
        for i in range(len(x)):
            def fi(xi):
                x[i] = xi
                return f(x)
            r = minimize(fi, x[i], **kw_minimize_args)
            x[i] = r.x
            rset.append(r)
        x_hist.append(x.copy())
        print (np.linalg.norm(x-last_x) )
        if np.linalg.norm(x-last_x) < max_tol:
            message = "finished after %s iterations and convergence reached at %1.e tol"%(t+1,max_tol)
            break
    ret = {"coord_success": [r.success for r in rset],
           "coord_messages": [r.message for r in rset],
           "x": x,
           "x_history": np.r_[x_hist],
           "success": np.alltrue([r.success for r in rset]),
           "message": message}

    rs = namedtuple("coordinate_descent_result",  " ".join(list(ret.keys())))
    ret = rs(**ret)
    return ret
    