import os


def get_new_run_id(outdir):
    last_run_id = 0
    run_names = [fname for fname in os.listdir(outdir) if "run" in fname]
    if len(run_names) is not 0:
        run_names.sort(key=lambda f: int(''.join(filter(str.isdigit, f))))
        last_run_id = int(''.join(filter(str.isdigit, run_names[-1])))

    return last_run_id + 1


def resolve_run_directory(args):
    if args.newrun:
        new_run_id = get_new_run_id(args.outdir)
        os.mkdir(os.path.join(args.outdir, 'run%03d' % new_run_id))
        args.ckptdir = os.path.join(args.outdir, 'run%03d' % new_run_id, 'checkpoints/')
        args.resultdir = os.path.join(args.outdir, 'run%03d' % new_run_id, 'results/')
        os.mkdir(args.ckptdir)
        os.mkdir(args.resultdir)
        # TODO: copy over gin config file
        # TODO: save git commit hash in result directory as well
    elif args.ckptdir is None or args.resultdir is None:
        raise ValueError("Please either specify the -newrun flag "
                         "or provide paths for both --ckptdir and --resultdir")
    return args

