"""
This is an extension of the cssrlib class to input corrections decoded from the ssrz module from geo++

"""

import numpy as np
import pandas as pd
from src.cssrlib.cssrlib import cssr,local_corr,sCType, sCSSRTYPE
from src.cssrlib.gnss import id2sat, gtime_t,gpst2time

class ssrz_lc(local_corr):

    def __init__(self):
        super(ssrz_lc, self).__init__()
        self.t0s = {}
        self.phw = {}
        self.state = {}
        self.trop = {}
        self.tide = {}
        sc_t = [sCType.CLOCK, sCType.ORBIT,
                     sCType.CBIAS, sCType.PBIAS,
                     sCType.TROP, sCType.STEC,
                     sCType.HCLOCK, sCType.VTEC]
        for sc in sc_t:
            self.t0s[sc] = gtime_t()

class cssr_ssrz(cssr):
    MAXNET = 0
    SYSMAX = 16
    def __init__(self):
        super(cssr_ssrz,self).__init__()
        #self.cssrmode = sCSSRTYPE.SSRZ
        self.sig_n_p = {}
        self._initialized_sat_signals = False
        self.lc =[]

        for inet in range(self.MAXNET+1):
            self.lc.append(ssrz_lc())
            self.lc[inet].inet = inet
            self.lc[inet].flg_trop = 0
            self.lc[inet].flg_stec = 0
            self.lc[inet].nsat_n = 0
            self.lc[inet].t0 = {}

        # maximum validty time for correction
        self.tmax = {sCType.CLOCK: 5.0, sCType.ORBIT: 5.0,
                     sCType.CBIAS: 5.0, sCType.PBIAS: 5.0,
                     sCType.TROP: 5.0, sCType.STEC: 5.0,
                     sCType.HCLOCK: 5.0, sCType.VTEC: 5.0}

    def insert_local_corr(self, ssrz_sec, inet, iodssr):

        #setting the variables in the cs class that needs updating, if any
        week = int(ssrz_sec.iloc[0, 0])  # First row, first column
        tow = float(ssrz_sec.iloc[0, 1])  # First row, second column
        gtime = gpst2time(week, tow)

        #updates to the current iodssr number, after storing the previous value
        self.iodssr_p = self.iodssr
        self.iodssr = iodssr

        satellites = 0  # zero indexed at start for the dictionary to put it in
        current_sat = None
        current_signals = []
        for index, row in ssrz_sec.iterrows():
            sat_id = row['SAT']
            sat = id2sat(sat_id)
            rsig = sat_id[0]+'L'+str(row.iloc[3]) #pbias code reference for dictionaries
            csig = sat_id[0]+'C'+str(row.iloc[3]) #cbias code reference for dictionaries

            if not self._initialized_sat_signals:
                if sat != current_sat:
                    # Save previous satellite’s data
                    if current_sat is not None:
                        self.sig_n_p[current_sat] = current_signals
                        self.nsig_n.append(len(current_signals))
                        self.sat_n.append(current_sat)

                    # Start new satellite
                    current_sat = sat
                    current_signals = [rsig]
                else:
                    if rsig not in current_signals:
                        current_signals.append(rsig)


            self.lc[inet].pbias.setdefault(sat, {})[rsig] = row.iloc[16]
            self.lc[inet].cbias.setdefault(sat, {})[csig] = row.iloc[15]
            if not hasattr(self.lc[inet], "iode") or self.lc[inet].iode is None:
                self.lc[inet].iode = {}  # Ensure it's a dictionary
            self.lc[inet].iode[sat] = row.iloc[37]

            if not hasattr(self.lc[inet], "dorb") or self.lc[inet].dorb is None:
                self.lc[inet].dorb = {}  # Ensure it's a dictionary
            self.lc[inet].dorb[sat] = np.array([row.iloc[38], row.iloc[39], row.iloc[40]])

            if not hasattr(self.lc[inet], "state") or self.lc[inet].state is None:
                self.lc[inet].state = {}  # Ensure it's a dictionary
            self.lc[inet].state[sat] = np.array([row.iloc[8], row.iloc[9], row.iloc[10]])

            if not hasattr(self.lc[inet], "dclk") or self.lc[inet].dclk is None:
                self.lc[inet].dclk = {}  # Ensure it's a dictionary
            self.lc[inet].dclk[sat] = row.iloc[12]

            if not hasattr(self.lc[inet], "hclk") or self.lc[inet].hclk is None:
                self.lc[inet].hclk = {}  # Ensure it's a dictionary
            self.lc[inet].hclk[sat] = row.iloc[13]

            if not hasattr(self.lc[inet], "stec") or self.lc[inet].stec is None:
                self.lc[inet].stec = {}  # Ensure it's a dictionary
            self.lc[inet].stec.setdefault(sat,{})[rsig] = row.iloc[17]

            if not hasattr(self.lc[inet], "trph") or self.lc[inet].trph is None:
                self.lc[inet].trph = {}  # Ensure it's a dictionary
            self.lc[inet].trph[sat] = row.iloc[27] #? read docu

            if not hasattr(self.lc[inet], "trpw") or self.lc[inet].trpw is None:
                self.lc[inet].trpw = {}  # Ensure it's a dictionary
            self.lc[inet].trpw[sat] = row.iloc[28]

            if not hasattr(self.lc[inet], "ci") or self.lc[inet].ci is None:
                self.lc[inet].ci = {}  # Ensure it's a dictionary
            self.lc[inet].ci[sat] = np.array([row.iloc[18], row.iloc[19],
                                              row.iloc[20],row.iloc[21],
                                              row.iloc[22]]) #check types in docu #todo

            if not hasattr(self.lc[inet], "ct") or self.lc[inet].ct is None:
                self.lc[inet].ct = {}  # Ensure it's a dictionary
            #self.lc[inet].ct[sat] = None #TODO
            #self.lc[inet].quality_trp[sat] = None #TODO
            #self.lc[inet].quality_stec[sat] = row[17] #these should be the same? only first pne is an actual field in lc
            #self.lc[inet].stec_quality[sat] = row[17]
            if self.lc[inet].sat_n is None:
                self.lc[inet].sat_n = []  # Initialize as an empty list

            if not hasattr(self.lc[inet], "phw") or self.lc[inet].stec is None:
                self.lc[inet].phw = {}  # Ensure it's a dictionary
            if sat not in self.lc[inet].phw:
                self.lc[inet].phw[sat]= row.iloc[31]

            if not hasattr(self.lc[inet], "trop") or self.lc[inet].trop is None:
                self.lc[inet].trop = {}  # Ensure it's a dictionary
            if sat not in self.lc[inet].trop:
                self.lc[inet].trop[sat] = row.iloc[23]

            if self.lc[inet].tide is None or len(self.lc[inet].tide) == 0: #only first iteration, as it is the same for all rows
                self.lc[inet].tide = np.array([row.iloc[33],row.iloc[34],row.iloc[35]])

                # Append only if the satellite is not already in the list
            if sat not in self.lc[inet].sat_n:
                self.lc[inet].sat_n.append(sat)

                # Apply for each correction type available
                for sc in [sCType.ORBIT, sCType.CLOCK, sCType.CBIAS, sCType.PBIAS, sCType.HCLOCK]:
                    self.set_t0(inet=inet, sat=sat, ctype=sc, t=gtime)

            #self.lc[inet].t0[sat] = None #TODO
            #self.lc[inet].cstat[sat] = None #TODO
            #self.lc[inet].t0s[sat] = None #TODO
            #self.lc[inet].flg_trop = None #TODO
            #self.lc[inet].flg_stec = None #if complete stec data, else needs calc from ci #TODO
            #self.lc[inet].dstec[sat] = None #not in lc, #TODO
            #self.lc[inet].ng = None #not in lc #TODO

        self.lc[inet].nsat_n = satellites+1 #zero indexed

        if not self._initialized_sat_signals:
            print("only this 1 time")
            # Don’t forget the last satellite!
            if current_sat is not None:
                self.sig_n_p[current_sat] = current_signals
                self.nsig_n.append(len(current_signals))
                self.sat_n.append(current_sat)

            # Final count
            self.sat_n_p = len(self.sat_n)

            self._initialized_sat_signals = True

        # inputing the iodssr value
        for sc in [sCType.ORBIT, sCType.CLOCK, sCType.CBIAS, sCType.PBIAS,
                   sCType.HCLOCK, sCType.STEC, sCType.VTEC, sCType.TROP]:
            self.iodssr_c[sc] = iodssr

        self.lc[inet].cstat |= (
                (1 << sCType.CLOCK) |
                (1 << sCType.ORBIT) |
                (1 << sCType.CBIAS) |
                (1 << sCType.PBIAS) |
                (1 << sCType.HCLOCK) |
                (1 << sCType.STEC) |
                (1 << sCType.VTEC) |
                (1 << sCType.TROP)
        )

    def set_t0(self, inet=0, sat=0, ctype=0, t=gtime_t()):
        """ set reference time for correction to check validity time """
        sc_t = [sCType.CLOCK, sCType.ORBIT, sCType.CBIAS, sCType.PBIAS,
                sCType.HCLOCK,sCType.STEC, sCType.VTEC, sCType.TROP]

        if sat not in self.lc[inet].t0:
            self.lc[inet].t0[sat] = {}
            for sc in sc_t:
                self.lc[inet].t0[sat][sc] = gtime_t()

        self.lc[inet].t0[sat][ctype] = t