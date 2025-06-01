from copy import deepcopy
import matplotlib.pyplot as plt
import numpy as np
from sys import stdout
from binascii import unhexlify

import gnss as gn
from cssrlib.cssrlib import cssr
from gnss import ecef2pos, Nav, time2gpst, timediff, time2str, epoch2time
from gnss import rSigRnx, sys2str
from peph import atxdec, searchpcv
from ppprtk import ppprtkpos
from rinex import rnxdec

navfile = 'cssrlib-data/data/doy223/NAV223.23p'
obsfile = 'cssrlib-data/data/doy223/SEPT223Y.23O'  # PolaRX5'
atxfile = 'cssrlib-data/data/igs14.atx'

ep = [2023, 8, 11, 21, 0, 0]

dec = rn.rnxdec() # edit

nav = Nav()
nav = dec.decode_nav(navfile, nav)

atx = atxdec()
atx.readpcv(atxfile)

xyz_ref = [-3962108.7007, 3381309.5532, 3668678.6648]
pos_ref = ecef2pos(xyz_ref)

file_l6 = 'cssrlib-data/data/doy223/223v_qzsl6.txt'
prn_ref = 199  # QZSS PRN
l6_ch = 0  # 0:L6D, 1:L6E

griddef = 'cssrlib-data/data/clas_grid.def'
cs = cssr()
cs.monlevel = 1
time = epoch2time(ep)
cs.week = time2gpst(time)[0]
cs.read_griddef(griddef)

sigs = [rSigRnx("GC1C"), rSigRnx("GC2W"),
        rSigRnx("EC1C"), rSigRnx("EC5Q"),
        rSigRnx("JC1C"), rSigRnx("JC2L"),
        rSigRnx("GL1C"), rSigRnx("GL2W"),
        rSigRnx("EL1C"), rSigRnx("EL5Q"),
        rSigRnx("JL1C"), rSigRnx("JL2L"),
        rSigRnx("GS1C"), rSigRnx("GS2W"),
        rSigRnx("ES1C"), rSigRnx("ES5Q"),
        rSigRnx("JS1C"), rSigRnx("JS2L")]

rnx = rnxdec()
rnx.setSignals(sigs)

if rnx.decode_obsh(obsfile) >= 0:
    # Auto-substitute signals
    rnx.autoSubstituteSignals()

    # Initialize position
    ppprtk = ppprtkpos(nav, rnx.pos, 'test_ppprtk.log')

    # Set PCO/PCV information
    nav.rcv_ant = searchpcv(atx.pcvr, rnx.ant,  rnx.ts)

print("Available signals")
for sys, sigs in rnx.sig_map.items():
    txt = "{:7s} {}".format(sys2str(sys),
            ' '.join([sig.str() for sig in sigs.values()]))
    print(txt)

print("\nSelected signals")
for sys, tmp in rnx.sig_tab.items():
    txt = "{:7s} ".format(sys2str(sys))
    for _, sigs in tmp.items():
        txt += "{} ".format(' '.join([sig.str() for sig in sigs]))
    print(txt)

pos = ecef2pos(rnx.pos)
inet = cs.find_grid_index(pos)

dtype = [('wn', 'int'), ('tow', 'int'), ('prn', 'int'),
          ('type', 'int'), ('len', 'int'), ('nav', 'S500')]
v = np.genfromtxt(file_l6, dtype=dtype)

nep = 3*60  # 3 minutes, increase this for longer run

t = np.zeros(nep)
tc = np.zeros(nep)
enu = np.ones((nep, 3))*np.nan
sol = np.zeros((nep, 4))
dop = np.zeros((nep, 4))
smode = np.zeros(nep, dtype=int)

# Skip epoch until start time
obs = rnx.decode_obs()
while time > obs.t and obs.t.time != 0:
    obs = rnx.decode_obs()

for ne in range(nep):
    week, tow = time2gpst(obs.t)

    vi = v[(v['tow'] == tow) & (v['type'] == l6_ch)
           & (v['prn'] == prn_ref)]
    print(vi)
    if len(vi) > 0:
        cs.decode_l6msg(unhexlify(vi['nav'][0]), 0)
        if cs.fcnt == 5:  # end of sub-frame
            cs.decode_cssr(bytes(cs.buff), 0)
            print(cs.time)

    if ne == 0:
        nav.t = deepcopy(obs.t)
        t0 = deepcopy(obs.t)
        t0.time = t0.time // 30 * 30
        cs.time = obs.t
        nav.time_p = t0

    cstat = cs.chk_stat()
    if cstat:
        ppprtk.process(obs, cs=cs)

    t[ne] = timediff(nav.t, t0) / 60

    sol = nav.xa[0:3] if nav.smode == 4 else nav.x[0:3]
    enu[ne, :] = gn.ecef2enu(pos_ref, sol - xyz_ref)
    smode[ne] = nav.smode

    # Log to standard output
    stdout.write('\r {} ENU {:7.3f} {:7.3f} {:7.3f}, 2D {:6.3f}, mode {:1d}'
                 .format(time2str(obs.t),
                         enu[ne, 0], enu[ne, 1], enu[ne, 2],
                         np.sqrt(enu[ne, 0] ** 2 + enu[ne, 1] ** 2),
                         smode[ne]))

    # Get new epoch, exit after last epoch
    obs = rnx.decode_obs()
    if obs.t.time == 0:
        break

rnx.fobs.close()