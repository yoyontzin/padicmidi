# Examples

Each script in `examples/` is a small self-contained demonstration of one
capability. Run them with `python examples/<file>.py` after installing the
package in editable mode.

## `01_quickstart.py`

Analyses the BWV 1007 prelude with $p=2$ and prints the table of
$\mathrm{Coh}_\pi(2,n)$. Expected output: 0.500000 exact for all levels
(the architectural null floor).

## `02_suite_bach.py`

Runs the full suite BWV 1007 (six movements) with $p \in \{2, 3\}$ and
prints a piece × prime × level table.

## `03_compare_primes.py`

Compares $\mathrm{Coh}_\pi(p,n)$ against the floor $1/p$ for
$p \in \{2, 3, 5, 7\}$ on the BWV 1007 prelude. Demonstrates the architectural
floor for the binary case and the deviation for non-matching primes.

## `04_polyphonic_diagnostic.py`

Comparative analysis showing the texture discriminant: pieces that satisfy
the (SC) and (AI) hypotheses sit on the floor 0.500; deviations indicate
texture (polyphony, chromatic complexity).
