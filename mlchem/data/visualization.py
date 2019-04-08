import matplotlib.pyplot as plt
import numpy as np
from sklearn.metrics import mean_squared_error, r2_score, mean_absolute_error


def parity(predictions, true, scores=False, filename=None, **kwargs):
    """A parity plot function

    Parameters
    ----------
    predictions : list or numpy.array
        Model predictions in a list.
    true : list or numpy.array
        Targets or true values.
    scores : bool
        Print scores in parity plot.
    filename : str
        A name to save the plot to a file. If filename is non exisntent, we
        call plt.show().

    Notes
    -----
    kargs accepts all valid keyword arguments for matplotlib.pyplot.savefig.
    """

    min_val = min(true)
    max_val = max(true)
    fig = plt.figure(figsize=(6., 6.))
    ax = fig.add_subplot(111)
    ax.plot(true, predictions, 'r.')
    ax.plot([min_val, max_val], [min_val, max_val], 'k-', lw=0.3,)
    plt.xlabel('True Values')
    plt.ylabel('ML4Chem Predictions')

    if scores:
        rmse = np.sqrt(mean_squared_error(true, predictions))
        mae = mean_absolute_error(true, predictions)
        correlation = r2_score(true, predictions)
        plt.text(min_val, max_val, 'R-squared = {:.2f} \n'
                                   'RMSE = {:.2f}\n'
                                   'MAE = {:.2f}\n'
                                   .format(correlation, rmse, mae))

    if filename is None:
        plt.show()
    else:
        plt.savefig(filename, **kwargs)


def read_log(logfile):
    """Read the logfile

    Parameters
    ----------
    logfile : str
        Path to logfile.
    """

    f = open(logfile, 'r')

    check = 'Epoch'
    start = False
    epochs = []
    loss = []
    rmse = []

    for line in f.readlines():

        if check in line:
            start = True

        if start:
            try:
                line = line.split()
                epochs.append(int(line[0]))
                loss.append(float(line[3]))
                rmse.append(float(line[4]))
            except TypeError:
                pass

    plt.plot(epochs, rmse, label='rmse')
    plt.legend(loc='upper left')
    plt.show()
