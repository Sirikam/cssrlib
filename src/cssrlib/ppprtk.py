"""
module for PPP-RTK positioning
"""
import sys

import numpy as np
from src.cssrlib.pppssr import pppos


class ppprtkpos(pppos):
    """ class for PPP-RTK processing """

    def __init__(self, nav, pos0=np.zeros(3), logfile=None):
        """ initialize variables for PPP-RTK """
        sys.stdout.write("values for ppprtkspos is set")

        # trop, iono from cssr
        # phase windup model is local/regional
        super().__init__(nav=nav, pos0=pos0, logfile=logfile,
                         trop_opt=2, iono_opt=2, phw_opt=2)

        #self.nav.ephopt = 5 #for use with ssrz
        self.nav.eratio = np.ones(self.nav.nf)*50  # [-] factor
        self.nav.err = [0, 0.01, 0.005]/np.sqrt(2)  # [m] sigma
        self.nav.sig_p0 = 30.0  # [m]
        self.nav.thresar = 2.0  # AR acceptance threshold
        self.nav.armode = 1     # AR is enabled

class ppprtkpos_test(pppos):
    """ class for PPP-RTK processing """

    def __init__(self, nav, pos0=np.zeros(3), logfile=None):
        """ initialize variables for PPP-RTK """
        sys.stdout.write("values for ppprtkspos is set")

        # trop, iono , phase wind up from ssrz
        super().__init__(nav=nav, pos0=pos0, logfile=logfile,
                         trop_opt=3, iono_opt=3, phw_opt=3)

        self.nav.ephopt = 5 #for use with ssrz
        self.nav.eratio = np.ones(self.nav.nf)*50  # [-] factor
        self.nav.err = [0, 0.01, 0.005]/np.sqrt(2)  # [m] sigma
        self.nav.sig_p0 = 30.0  # [m]
        self.nav.thresar = 2.0  # AR acceptance threshold
        self.nav.armode = 1     # AR is enabled
        self.nav.tidecorr = "SSRZ"

