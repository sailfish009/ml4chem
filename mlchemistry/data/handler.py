from collections import OrderedDict
from mlchemistry.utils import get_hash


class Data(object):
    """A Data class

    An adequate data structure is very important to develop machine-learning
    models. In general a model receives a data set (X) and a target vector (y).
    This class should in principle arrange this in a format that can be
    vectorized and operate not only with neural networks but also with support
    vector machines.

    The central object here is the data set.

    Parameters
    ----------
    images : list or object
        List of images.
    model : object
        The model can determine the data structure.
    purpose : str
        Are we needing the data for training or inferring?
    """
    def __init__(self, images, model=None, purpose=None):

        self.images = None
        self.targets = None
        self.unique_element_symbols = None

        if self.is_valid_structure(images) is False:
            self.prepare_images(images, purpose=purpose)

    def prepare_images(self, images, purpose=None):
        """Function to prepare images to operate with mlchemistry

        Parameters
        ----------
        images : list or object
            List of images.
        purpose : str
            The purpose of the data so that structure is prepared accordingly.
            Supported are: 'training', 'inference'

        Returns
        -------
        self.images : dict
            Ordered dictionary of images corresponding to order of self.targets
            list.
        self.targets : list
            Targets used for training the model.
        """
        print('Preparing images...')
        self.images = OrderedDict()

        if purpose == 'training':
            self.targets = []

        duplicates = 0

        for image in images:
            key = get_hash(image)
            if key in self.images.keys():
                duplicates += 1
            else:
                self.images[key] = image
                if purpose == 'training':
                    # When purpose is training then you also need targets
                    self.targets.append(image.get_potential_energy())

        print('Images hashed...')

    def is_valid_structure(self, images):
        """Check if the data has a valid structure

        Parameters
        ----------
        images : list of atoms
            List of images.

        Returns
        -------
        valid : bool
            Whether or not the structure is valid.
        """
        if isinstance(images, dict):
            valid = True
        else:
            valid = False

        return valid

    def get_unique_element_symbols(self, images, category=None):
        """Unique element symbol in data set


        Parameters
        ----------
        images : list of images.
            ASE object.
        category : str
            The supported categories are: 'trainingset', 'testset'.
        """

        supported_categories = ['trainingset', 'testset']

        symbols = {}

        if category in supported_categories:
            if category not in symbols.keys():
                symbols[category] = {}
                try:
                    symbols[category] = sorted(list(set([atom.symbol for image in
                                           images for atom in image])))
                except AttributeError:
                    symbols[category] = sorted(list(set([atom.symbol for key, image in
                                           images.items() for atom in image])))

            else:
                print('what happens in the following case?')    # FIXME
        else:
            print('The requested category is not supported...')
            symbols = None

        self.unique_element_symbols = symbols

        return self.unique_element_symbols

    def get_images(self, purpose=None):
        """
        Parameters
        ----------
        purpose : str
            The purpose of the data so that structure is prepared accordingly.
            Supported are: 'training', 'inference'
        model_name : str
            The model that is going to be used. Supported models are 'NeuralNetwork'.
        """

        if purpose == 'training':
            return self.images, self.targets
