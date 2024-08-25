# Fenrir

This is a fork of the `fenrir` source code maintained by members of the Astrophysics Group at the University of Bristol.

Note:
- The original source code was written by Corbin Taylor. The code was published under GPL3.
- Our group is maintaining wrapper scripts and some modifications.
- On parallelization: the parallelization is achieved by starting multiple processes of one of the executables. The workload is then split into `NUM_PROCS` batches, and a given process will only execute its batch and then terminate. In this fork, that means passing `--procs=NUM_PROCS --proc-index N` where `N` should be incremented for each launch.

## Building

We're using a `build.zig` file to slowly bring all of the targets and run configurations together into one system. Targets will be compiled into `./zig-out/bin/`.

### diskimage_multi

```
zig build diskimage_multi

# use --help to see the arguments
./zig-out/bin/diskimg --help
    [-s/--size size]          Column / row size. The full image with be (size * size).
                                Default: 500.
    [--procs num_procs]       Number of processors to run on: Default: 1
    [--proc-id id]            Number of processors to run on: Default: 0
    <spin>                    Black hole spin (0-1).
    <inc>                     Observer inclination in degrees (0-90).
    <edd>                     Eddington ratio.
    [-o/--outfile prefix]     String to prefix the output file with. Defaults:
                                'diskimg-output'
```

Output file has the following format:

    x, y, g, final_t, final_r, final_theta, final_phi, disk_H, pseudo-cylindrical_r

### diskimage

```
zig build diskimage

# use --help to see the arguments
./zig-out/bin/diskimg --help
    [-s/--size size]          Column / row size. The full image with be (size * size).
                                Default: 500.
    [--procs num_procs]       Number of processors to run on: Default: 1
    [--proc-id id]            Number of processors to run on: Default: 0
    <spin>                    Black hole spin (0-1).
    <inc>                     Observer inclination in degrees (0-90).
    <edd>                     Eddington ratio.
    [-o/--outfile prefix]     String to prefix the output file with. Defaults:
                                'diskimg-output'
```

Output file has the following format:

    x, y, g, final_t, final_r, final_theta, final_phi, disk_H, pseudo-cylindrical_r

## Original readme:

> This is the codebase for Fenrir used for my thesis work, as supervised by [Chris Reynolds](https://www.astro.umd.edu/~chris/) (U of Maryland, U of Cambridge) and [Cole Miller](https://www.astro.umd.edu/~miller/) (U of Maryland).
>
> This was used in the research presented in Taylor & Reynolds ([2018a](https://iopscience.iop.org/article/10.3847/1538-4357/aaad63),[b](https://iopscience.iop.org/article/10.3847/1538-4357/aae9f2)) and spoken about at numerous conferences.
>
> This is a public archive. I am not maintaining this code.
