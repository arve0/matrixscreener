from multiprocessing import Pool, cpu_count

try:
    _pools = cpu_count()
except NotImplementedError:
    _pools = 4


def chop(list_, n):
    "Chop list_ into n chunks. Returns a list."
    # could look into itertools also, might be implemented there
    size = len(list_)
    each = size // n
    if each == 0: each = 1
    chopped = []
    for i in range(n):
        start = i * each
        end = (i+1) * each
        if i == (n - 1):
        # make sure we get all items, let last worker do a litte more
            end = size
        chopped.append(list_[start:end])
    return chopped


def apply_async(fn, **kwargs):
    """Call Pool.apply_async(fn, kwds) and return merged result.

    Parameters
    ----------
    fn : function
        Function to call async in several ``multiprocessing.Pools``.
    kwargs : tuples
        Arguments which is sent to ``apply_async``. Should be  in form
        ``kw=(arg, split)``. If split is truthy arg will be splitted into
        chunks before sending it to ``apply_async``.

    Returns
    -------
    list
        Merged list with all results.
    """
    # split work load
    n = _pools # number of Pools
    chopped = {k: (chop(v[0],n),v[1]) if v[1] else v for k,v in kwargs.items()}
    arglist = []
    for i in range(n):
        dict_ = {}
        add = True
        for k,v in chopped.items():
            if v[1]:
                # do not create item in arglist of splitted argument has lengt 0
                if len(v[0][i]) == 0:
                    add = False
                    break
                dict_[k] = v[0][i]
            elif v[1] == False:
                dict_[k] = v[0]
        if add:
            arglist.append(dict_)

    # run in multiple Pools
    promises = []
    results = []
    p = Pool(n)
    for args in arglist:
        res = p.apply_async(fn, kwds=args)
        promises.append(res)
    for res in promises:
        result = res.get()
        if hasattr(result, '__iter__'):
            results.extend(result)
        else:
            results.append(result)

    return results
