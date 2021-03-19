from multiprocessing import Queue, Process, cpu_count

def queue(cmd, qin, qout, *args):
    
    while True:
        # Get item from the queue
        pos, var = qin.get()
        
        # Exit if last item is None
        if pos is None:
            break

        # Execute command
        res = cmd(var, *args)

        # Put results to the queue
        qout.put((pos, res))

    return


def parallel(np, var, cmd):

    varcount = len(var)

    processes = []
    nprocs = np if np <= cpu_count() else cpu_count()
    
    qin = Queue(1)
    qout = Queue()
    
    # Create processes
    for n in range(nprocs):
        pargs = [cmd, qin, qout]

        p = Process(target = queue, args = tuple(pargs))

        processes.append(p)
    
    # Start processes
    for p in processes:
        p.daemon = True
        p.start()

    # Fill queue
    for n in range(varcount):
        qin.put((n, var[n]))

    for _ in range(nprocs):
        qin.put((None, None))
    
    # Get results
    results = [[] for n in range(varcount)]

    for n in range(varcount):
        index, res = qout.get()
        
        results[index] = res
    
    # Wait until each processor has finished
    for p in processes:
        p.join()

    return results

    

