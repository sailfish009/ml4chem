from mlchemistry.utils import get_neighborlist
from mlchemistry.data.handler import Data
from .cutoff import Cosine
import numpy as np


class Gaussian(object):
    """Behler-Parrinello symmetry functions

    This class builds local chemical environments for atoms based on the
    Behler-Parrinello Gaussian type symmetry functions. It is modular enough
    that can be used just for creating feature spaces.


    Parameters
    ----------
    cutoff : float
        Cutoff radius used for computing fingerprints.
    """
    def __init__(self, cutoff=6.5, normalized=True):
        self.cutoff = cutoff
        self.cutofffxn = Cosine(cutoff=cutoff)
        self.normalized = normalized
        self.data = Data()

    def calculate_features(self, images, defaults=True,
                           category='trainingset'):
        """Calculate the features per atom in an atoms objects

        Parameters
        ----------
        image : ase object, list
            A list of atoms.
        defaults : bool
            Are we creating default symmetry functions?
        category : str
            The supported categories are: 'trainingset', 'testset'.
        """

        if self.data.unique_element_symbols is None:
            print('Getting unique element symbols for {}' .format(category))
            unique_element_symbols = \
                self.data.get_unique_element_symbols(images, category=category)
            unique_element_symbols = unique_element_symbols[category]

        if defaults:
            self.GP = self.make_symmetry_functions(unique_element_symbols,
                                                   defaults=True)

        for image in images:
            for atom in image:
                index = atom.index
                symbol = atom.symbol

                nl = get_neighborlist(image, cutoff=self.cutoff)
                n_indices, n_offsets = nl[atom.index]
                n_symbols = [image[i].symbol for i in n_indices]
                neighborpositions = [image.positions[neighbor] +
                                     np.dot(offset, image.cell)
                                     for (neighbor, offset) in
                                     zip(n_indices, n_offsets)]

                print(self.get_atomic_fingerprint(atom, index, symbol, n_symbols,
                                            neighborpositions))

    def get_atomic_fingerprint(self, atom, index, symbol, n_symbols,
                               neighborpositions):
        """Class method to compute atomic fingerprints


        Parameters
        ----------
        image : ase object, list
            List of atoms in an image.
        index : int
            Index of atom in atoms object.
        symbol : str
            Chemical symbol of atom in atoms object.
        """

        num_symmetries = len(self.GP[symbol])
        Ri = atom.position
        fingerprint = [None] * num_symmetries

        for count in range(num_symmetries):
            GP = self.GP[symbol][count]

            if GP['type'] == 'G2':
                feature = calculate_G2(n_symbols, neighborpositions,
                                     GP['symbol'], GP['eta'],
                                     self.cutoff, self.cutofffxn, Ri,
                                     normalized=self.normalized)
            elif G['type'] == 'G3':
                feature = calculate_G4(n_symbols, neighborpositions,
                                     GP['elements'], GP['gamma'],
                                     GP['zeta'], GP['eta'], self.cutoff,
                                     self.cutofffxn, Ri)
            elif G['type'] == 'G4':
                feature = calculate_G5(n_symbols, neighborpositions,
                                     GP['elements'], GP['gamma'],
                                     GP['zeta'], GP['eta'], self.cutoff,
                                     self.cutofffxn, Ri)
            else:
                print('not implemented')
            fingerprint[count] = feature

        return symbol, fingerprint


    def make_symmetry_functions(self, symbols, defaults=True, type=None,
                                etas=None, zetas=None, gammas=None):
        """Function to make symmetry functions

        This method needs at least unique symbols and defaults set to true.

        Parameters
        ----------
        symbols : list
            List of strings with chemical symbols to create symmetry functions.

            >>> symbols = ['H', 'O']

        defaults : bool
            Are we building defaults symmetry functions or not?

        type : str
            The supported Gaussian type functions are 'G2', 'G3', and 'G4'.
        etas : list
            List of etas.
        zetas : list
            Lists of zeta values.
        gammas : list
            List of gammas.

        Return
        ------
        GP : dict
            Symmetry function parameters.

        """

        GP = {}

        if defaults:
            print('Making default symmetry functions')
            for symbol in symbols:
                # Radial
                etas = np.logspace(np.log10(0.05), np.log10(5.), num=4)
                _GP = self.get_symmetry_functions(type='G2', etas=etas, symbols=symbols)

                # Angular
                #####etas = [0.005]
                #####zetas = [1., 4.]
                #####gammas = [1., -1.]
                #####_GP += self.get_symmetry_functions(type='G3', symbols=symbols,
                #####                                   etas=etas, zetas=zetas,
                #####                                   gammas=gammas)

                GP[symbol] = _GP
        else:
            pass

        return GP

    def get_symmetry_functions(self, type, symbols, etas=None, zetas=None, gammas=None):
        """Get requested symmetry functions

        """

        supported_angular_symmetry_functions = ['G3', 'G4']

        if type == 'G2':
            GP = [{'type': 'G2', 'symbol': symbol, 'eta': eta}
                  for eta in etas for symbol in symbols]
            return GP

        elif type in supported_angular_symmetry_functions:
            GP = []
            for eta in etas:
                for zeta in zetas:
                    for gamma in gammas:
                        for idx1, sym1 in enumerate(symbols):
                            for sym2 in symbols[idx1:]:
                                pairs = sorted([sym1, sym2])
                                GP.append({'type': type,
                                           'elements': pairs,
                                           'eta': eta,
                                           'gamma': gamma,
                                           'zeta': zeta})
            return GP
        else:
            print('The requested type of angular symmetry function is not'
                  ' supported.')

def calculate_G2(neighborsymbols, neighborpositions, center_symbol, eta,
                 cutoff, cutofffxn, Ri, normalized=True):
    """Calculate G2 symmetry function.

    Parameters
    ----------
    neighborsymbols : list of str
        List of symbols of all neighbor atoms.
    neighborpositions : list of list of floats
        List of Cartesian atomic positions.
    center_symbol : str
        Chemical symbol of the center atom.
    eta : float
        Parameter of Gaussian symmetry functions.
    cutoff : float
        Cutoff radius.
    cutofffxn : object
        Cutoff function.
    Ri : list
        Position of the center atom. Should be fed as a list of three floats.
    normalized : bool
        Whether or not the symmetry function is normalized.

    Returns
    -------
    feature : float
        Radial feature.
    """
    feature = 0.

    num_neighbors = len(neighborpositions)

    for count in range(num_neighbors):
        symbol = neighborsymbols[count]
        Rj = neighborpositions[count]
        if symbol == center_symbol:
            Rij = np.linalg.norm(Rj - Ri)
            if normalized:
                Rc = cutoff
            else:
                Rc = 1.
            feature += (np.exp(-eta * (Rij ** 2.) / (Rc ** 2.)) *
                        cutofffxn(Rij))
    return feature
