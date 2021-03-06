Separake: Echo-aware source separation
======================================

This repository contains all the code to reproduce the results of the paper
[*Separake: Source separation with a little help from echoes*](https://arxiv.org/abs/1711.06805).

We are available for any question or request relating to either the code
or the theory behind it. Just ask!

Abstract
--------

It is commonly believed that multipath hurts various audio processing
algorithms.  At odds with this belief, we show that multipath in fact helps
sound source separation, even with very simple propagation models.  Unlike most
existing methods, we neither ignore the room impulse responses, nor we attempt
to estimate them fully. We rather  assume  that  we  know  the  positions  of  a
few  virtual  microphones generated by echoes and we show how this gives us
enough spatial diversity to get a performance boost over the anechoic case. We
show improvements for two standard algorithms—one that uses only magnitudes of
the transfer functions, and one that also uses the phases. Concretely, we show
that multichannel non-negative matrix factorization aided with a small number of
echoes beats the vanilla variant of the same algorithm, and that with magnitude
information only, echoes enable separation where it was previously impossible.

Authors
-------

* Robin Scheibler (TMU)
* Diego Di Carlo (INRIA)
* Antoine Deleforge (INRIA)
* Ivan Dokmanić (UIUC)

#### Contact

[Robin Scheibler](mailto:robin[at]tmu[dot]ac[dot]jp) <br>
Ono Laboratory <br>
Graduate School of System Design <br>
Tokyo Metropolitan University <br>
6-6 Asahigaoka, Hino city, Tokyo <br>
191-0065 Japan

Summary of Files
----------------

* `separake_mu_early.py` uses the Ozerov and Fevotte MU algorithm. This is the orignal attempt by Robin.
* `separake_near_wall.py` implements the image microphone model and places the microphones close to a wall. No separation yet.
* `utilities.py` contains auxiliary methods.

Recreate the figures and sound samples
--------------------------------------

To recreate the figures from the original simulated data (stored in `data/paper_results/`), run

    ./make_figures.sh

To redo all the simulation, run

    [TBA]

Recorded Data
-------------

[TBA]

The recorded samples are stored in the `recordings` folder.
Detailed description and instructions are provided along the data.

Overview of results
-------------------

TBA

Acknowledgement
---------------

Authors of \cite{ozerov2010multichannel} generously provide a MATLAB
implementation of MU-NMF and EM-NMF methods for stereo separation. We ported
this code to Python 3 and extended it arbitrary number of input channels. We
think this implementation could be useful to the community and have released
the code\footnote{\textcolor{red}{}Link will go here after review}}.

Implementation Details
----------------------

First the original code was restricted to the 2-channel case, i.e.  $M = 2$.
Thus, in order to embrace the specifics of our scenario and for sake of
generalization, we extend it to the multi-channel case, that is $\forall M >
1$.

Secondly, the MU-NMF was modified to handle sparsity contraint as
described in \ref{sec:mu}.

Third, since EM method degenerates where
zero-valued entries are present in the dictionary matrix, $\mD$, all these
entries are initially set to a small constant value of \texttt{1e-6}.

Finally, the code was further modified to deal with fixed dictionary and
channel models matrices, which are normalized in order to avoid indeterminacy
issues \cite{ozerov2010multichannel}. 

Now to conclude with, no
\textit{simulated annealing} strategies are used in the final experiments.
In fact in some preliminary and informal investigations we noticed that this
yields better results than using annealing. In the experiments, the number
of iterations was set to $300$.

Dependencies
------------

* A working distribution of [Python 3.5](https://www.python.org/downloads/) (but 2.7 should work too).
* [Numpy](http://www.numpy.org/), [Scipy](http://www.scipy.org/)
* We use the distribution [anaconda](https://store.continuum.io/cshop/anaconda/) to simplify the setup of the environment.
* Computations are very heavy and we use the
  [MKL](https://store.continuum.io/cshop/mkl-optimizations/) extension of
  Anaconda to speed things up. There is a [free license](https://store.continuum.io/cshop/academicanaconda) for academics.
* We used ipyparallel and joblib for parallel computations.
* [matplotlib](http://matplotlib.org) and [seaborn](https://stanford.edu/~mwaskom/software/seaborn/index.html#) for plotting the results.
* [mir_eval](https://craffel.github.io/mir_eval) is used for the [BSS evaluation](https://craffel.github.io/mir_eval/#module-mir_eval.separation) routines it contains.

The pyroomacoustics is used for STFT, fractionnal delay filters, microphone arrays generation, and some more.

    pip install pyroomacoustics

List of standard packages needed

    numpy, scipy, pandas, ipyparallel, seaborn, zmq, joblib, samplerate, mir_eval


Systems Tested
--------------

TBA

License
-------

Copyright (c) 2016, Antoine Deleforge, Diego Di Carlo, Ivan Dokmanić, Robin Scheibler

All the code in this repository is under MIT License.

