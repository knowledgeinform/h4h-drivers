# DISTRIBUTION STATEMENT D. Distribution authorized to the Department of
# Defense and U.S. DoD contractors only; Administrative or Operational Use; 1
# Jan 2017. Other U.S. requests shall be referred to Naval Surface Warfare
# Center Panama City Division, ATTN: Technical Director NSWC PCD, 110 Vernon
# Ave, Panama City, FL 32407.
"""
mats.mod
--------

Contains base class definitions for MATS module types.
"""
from abc import ABCMeta, abstractmethod


class Detector(metaclass=ABCMeta):
    """
    Detector Module Base Class.

    A base class for modules that detect regions of interest in sensor data
    and output them in mats.Contact and mats.Ecdata structures.
    """

    @abstractmethod
    def configure(self, cfg):
        """
        Configure the module.

        :param cfg: Module configuration information.
        :type cfg: mats.Struct

        :return: None

        .. warning:: An exception should be raised upon error.
        """
        pass

    @abstractmethod
    def detect(self, input):
        """
        Detect contacts in the given input.

        This method should create a mats.ContactList and a mats.EcdataList
        and fill in the following contact/ecdata fields of each contact:
            @li mats.Contact['x']
            @li mats.Contact['y']
            @li mats.Ecdata['detscore']

        In addition, it may use mats.Contact.add_feature() to add a feature
        name and vector to the contacts. Feature vector should be a 1-D numpy
        array. Feature name should typically match the module name.

        Also, this method should ensure that each contact has a distinct UUID.
        (It is not necessary to do this for the ecdata, as the contact's UUID
        will be copied to the ecdata in the processing stream.)

        @param[in] input A mats.Input or mats.InputChunk containing data.

        @return (contacts, ecdata) tuple. contacts - A mats.ContactList
        containing the list of contacts detected. ecdata - A mats.EcdataList
        containing the extra contact data.
        @warning An exception should be raised upon error.
        """
        pass


class Feature(metaclass=ABCMeta):
    """
    Feature Module Base Class.

    A base class for modules that quantify contact information into a
    measurement or a series of measurements.
    """

    @abstractmethod
    def configure(self, cfg):
        """
        Configure the module.

        @param[in] cfg A mats.Struct containing the module configuration.

        @return No return value.
        @warning An exception should be raised upon error.
        """
        pass

    @abstractmethod
    def feature(self, contacts, ecdata):
        """
        Calculate feature vector for each contact.

        If it fails, it will add a feature vector containing all 0's to the
        contacts.

        This method should use mats.Contact.add_feature() to add a feature
        name and vector to each contact. Feature vector should be a 1-D numpy
        array. Feature name should typically match the module name.

        @param[in,out] contacts A mats.ContactList containing the contacts.
        @param[in] ecdata A mats.EcdataList containing the extra contact data.

        @return No return value. The input @p contacts is modified
        directly as an output parameter.
        @warning An exception should be raised upon error.
        """
        pass


class Tracker(metaclass=ABCMeta):
    """
    Tracker Module Base Class.

    A base class for modules that attempt to track the position of contacts
    across successive inputs.
    """

    @abstractmethod
    def configure(self, cfg):
        """
        Configure the module.

        @param[in] cfg A mats.Struct containing the module configuration.

        @return No return value.
        @warning An exception should be raised upon error.
        """
        pass

    @abstractmethod
    def track(self, inp, contacts, ecdata):
        """
        Notes new contacts for given input. Contacts identified from previous
        input that are not given are returned.

        This method should fill in the following contact field fields.

        :param inp: Input data.
        :type inp: mats.Input
        :param contacts: Contact list containing contacts identified for given
            input.
        :type contacts: mats.ContactList
        :param ecdata: Ecdata list containing extra contact data.
        :type ecdata: mats.EcdataList

        :return: Contact list with contact found from previous input data that
            is not in the given contact list.
        :rtype: (mats.ContactList, mats.EcdataList)
        """
        pass


class Classifier(metaclass=ABCMeta):
    """
    Classifier Module Base Class.

    A base class for modules that use feature information of contacts to
    discriminate between targets and non-targets.
    """

    @abstractmethod
    def configure(self, cfg):
        """
        Configure the module.

        @param[in] cfg A mats.Struct containing the module configuration.

        @return No return value.
        @warning An exception should be raised upon error.
        """
        pass

    @abstractmethod
    def classify(self, contacts, ecdata):
        """
        Classify contacts.

        This method should fill in the following contact/ecdata fields:
            @li mats.Contact['cls']
            @li mats.Contact['classconf']

        @param[in,out] contacts A mats.ContactList containing the contacts.
        @param[in,out] ecdata A mats.EcdataList containing the ecdata.

        @return No return value. The inputs @p contacts and @p ecdata are
        modified directly as output parameters.
        @warning An exception should be raised upon error.
        """
        pass

    @abstractmethod
    def tunable(self, val):
        """
        Returns whether it is possible to train this classifier module.

        Along with returning ability to retrain, method should preform any
        initial setup that is necessary for training.
        """
        pass

    @abstractmethod
    def train(self):
        pass


class Reader(metaclass=ABCMeta):
    """
    Reader Module Base Class.

    A base class for modules that read data from data files and load it into
    mats.Input structures.
    """

    @abstractmethod
    def configure(self, cfg):
        """
        Configure the module.

        @param[in] cfg A mats.Struct containing the module configuration.

        @return No return value.
        @warning An exception should be raised upon error.
        """
        pass

    @abstractmethod
    def read(self, filepath):
        """
        Import data from file to a mats.Input structure.

        Routine returns a list of mats.Input structures because some files
        may contain both port and starboard data in the same file. The
        navigation data in the file is interpolated to correspond with the
        along-track axis of the reference dataset.

        @param[in] filepath Full path location of file to load.

        @return input List of loaded mats.Input structures from file.
        @warning An exception should be raised upon error.
        """
        pass


class GtReader(metaclass=ABCMeta):
    """
    Groundtruth Reader Module Base Class.

    A base class for modules that read groundtruth files and load it into
    a list of mats.gt.GtContact object.
    """

    @abstractmethod
    def configure(self, cfg):
        """
        Configure the module.

        @param[in] cfg A mats.Struct containing the module configuration.

        @return No return value.
        @warning An exception should be raised upon error.
        """
        pass

    @abstractmethod
    def read(self, filepath):
        """
        Import groundtruth data from file to a mats.gt.GtContact list.

        @param[in] filepath Full path location of file to load.
        """
        pass


class Writer(metaclass=ABCMeta):
    """
    Writer Module Base Class

    A base class for modules that writes common data structures out in different
    formats.
    """

    @abstractmethod
    def configure(self, cfg):
        """
        Configure the module.

        @param[in] cfg A mats.Struct containing the module configuration.

        @return No return value.
        @warning An exception should be raised upon error.
        """
        pass

    @abstractmethod
    def write_input(self, filename, inp):
        """
        Writes MATS_input structure.

        :param filename: Full path location of file to save.
        :type filename: str
        :param inp: MATS_input structures to be written.
        :type inp: mats.Input
        """
        pass

    @abstractmethod
    def write_contacts(self, filename, con, ecd):
        """
        Writes contact information.

        :param filename: Name of output file.
        :param con: Contact list to be written.
        :param ecd: Extra contact list to be written.
        """
        pass


class Normalizer(metaclass=ABCMeta):
    """
    Normalizer Module Base Class.

    A base class for modules that standardize sensor data to remove variability
    and dynamic range changes.
    """

    @abstractmethod
    def configure(self, cfg):
        """
        Configure the module.

        @param[in] cfg A mats.Struct containing the module configuration.

        @return No return value.
        @warning An exception should be raised upon error.
        """
        pass

    @abstractmethod
    def normalize(self, inp):
        """
        Normalize data in the given input.

        :param inp: MATS Input to be processed.
        :type inp: mats.Input

        :return: None. The input is modified directly as an output parameter.

        .. warning:: An exception should be raised upon error.
        """
        pass


class Interface(metaclass=ABCMeta):
    """
    Interface / Processor Module Abstract Base Class.

    This class serves as an interface for using a particular language or engine
    for data processing.  It has two independent areas of functionality:

    1.  Package Management:  The interface can load, create, and manage modules
    for the engine, such as detector and classifier modules, that can be used
    as parts of an overall C++ processing stream.

    2.  Processing Stream:  The interface can use the engine to run the
    processing stream itself.
    """

    @abstractmethod
    def engine(self):
        """
        Return interface engine name.

        This is the name of the folder where the interface's packages are
        stored, not the name of the interface's derived class.
        """
        pass

    @abstractmethod
    def scan(self):
        """
        Scan for modules.
        """
        pass

    @abstractmethod
    def getType(self, mod_type):
        """
        Return all modules of a given type. Returned strings are in the format
        "<package name>/<module name>".

        :param mod_type: Requested MATS module type.
        :type mod_type: str
        :return: List of available module of requested type.
        :rtype: list
        """
        pass

    @abstractmethod
    def module(self, mod_name):
        """
        Return a wrapper for the given module.

        @param[in] modName The name of the module. Format may be either
        "<module name>" or "<package name>/<module name>". If no package name
        specified, the first module found with the given name will be used.
        """
        pass

    @abstractmethod
    def create(self, mod_type, mod_name):
        """
        Create instance of requested module.

        If an existing reader or interface module is requested, the pointer to
        the existing module is returned, and no module is dynamically
        allocated.

        :param mod_type: Name of the type of module.
        :type mod_type: str
        :param mod_name: The name of the module. Format may be either
          "<module name>" or "<package name>/<module name>". If no package name
          specified, the first module found with the given name will be used.
        :type mod_name: str
        :return: Created MATS module.

        .. warning:: The created module is owned by the interface and should not
                     be deleted.
        """
        pass

    @abstractmethod
    def configure(self, cfg):
        """
        Configure the interface's processing stream.

        Parameters
        ----------
        :param cfg:
        :type cfg: mats.AtrConfig
            Desired configuration.

        Returns
        -------
        None
        """
        pass

    @abstractmethod
    def process(self, inp):
        """
        Process input data with configured interface.

        Use the interface to run a complete processing stream on input data.
        Before calling this function, the interface should be configured using
        configure().

        Parameters
        ----------
        :param inp: Input structure containing data to be processed.
        :type inp: mats.Input

        :return: Contacts found during processing.
        :rtype: mats.ContactList, mats.EcdataList
        """
        pass


class GtData(metaclass=ABCMeta):
    def configure(self, cfg):
        """
        Configure the module.

        :param cfg: Module information for configuration.
        :type cfg: mats.Struct
        :return: None

        .. warning:: An exception should be raised upon error.
        """
        pass

    def load(self, fn):
        """
        Ground truth data loader.

        :param fn: Ground truth filename.
        :type fn: str

        :return: None
        """
        pass

