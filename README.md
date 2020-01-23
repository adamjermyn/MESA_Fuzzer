# MESA_Fuzzer

The `fuzzer.py` script can be used to automatically test all options and combinations of options in the
stellar evolution code [Modules for Experiments in Stellar Astrophyics
(MESA)](http://mesa.sourceforge.net/). Note that there are many options, so testing all combinations thereof will likely take longer than the present age of the universe...

## Usage

Copy the current `controls.defaults` and `star_job.defaults` files from `$MESA_DIR/star/defaults` into the same directory as `fuzzer.py`.
Copy the current `$MESA_DIR/star/work` folder into the same directory and rename it `prototype`.
Run `fuzzer.py` and watch it test options.

Note that your system must have timeout, or gtimeout on Mac (part of coreutils on either ports or brew).

### What it's doing

MESA_Fuzzer runs through all possible combinations of controls, starting with the combinations with the fewest non-default values and working up. So it’ll write all possible inlists with just one control set, then all possible ones with two, and so on until it’s gone through all 2^1640 options (if there’s still a universe with MESA by that time!). The hope though is that most interesting/unexpected behavior happens with combinations of small numbers of related options so that we need to examine many fewer trials...

Each combination is tried five times, to allow for a few different random parameter values. The trials are each capped at 10 seconds of runtime. Note that your system must have timeout, or gtimeout on Mac (part of coreutils on either ports or brew).

After each trial the fuzzer looks for a list of bad_strings (set on line 118 to ‘failed’, ’nan’, ‘warning’, ‘error’, case-insensitive). If a bad string is found the offending string is printed along with the output from that trial and the options+values used. You may want to remove ‘warning’ because it turns out default MESA almost always issues a rel_run_E_err within 10 seconds.

Note that I’ve ensured that all inlists set report_ierr=.true. because that seems useful. You can put your own preferred mandatory controls in the mandatory_controls string.