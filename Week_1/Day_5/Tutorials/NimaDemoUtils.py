import numpy as np
import scipy.interpolate as interp
import os
from itertools import product,combinations
import matplotlib.pyplot as plt
from astropy.coordinates import SkyCoord
from astropy import units as u
from astropy.coordinates import ICRS
import corner
plt.style.use('dark_background')

def PulsarDistMaker(Npulsars, seed = None, skyplot = True, disttype = 'uniform'):
    '''
    This function creates a population of random pulsars distributed uniformly in the sky. The coordinates are reported in the Geocentric-true-ecliptic frame.

    :param: Npulsars: Number of pulsars to make
    :param: seed: sets the seed for the random number generator
    :param: skyplot: if set to true, a sky plot of the pulsar population will be displayed.
    :output: lam, beta, pname: Geocentric-true-ecliptic longitude, latitude, and pulsar names (if name is set to true)

    Author: Nima Laal
    '''
    if seed: np.random.seed(seed)
    if disttype == 'uniform':c = 2
    else: c = 1
    dec = np.arcsin(np.random.uniform(-1,1, size = Npulsars))
    ra = np.random.uniform(0, c*np.pi, size = Npulsars)

    x = np.cos(ra) * np.cos(dec)
    y = np.sin(ra) * np.cos(dec)
    z = np.sin(dec)
    pos_vec = np.column_stack((x, y, z))

    sc = SkyCoord(ra = ra , dec = dec, unit = 'rad', frame='icrs')
    lam = sc.geocentrictrueecliptic.lon.deg
    beta = sc.geocentrictrueecliptic.lat.deg

    if skyplot:
        plt.figure(dpi = 170, figsize=(8, 4))
        plt.subplot(projection="aitoff")

        c = SkyCoord(ra*180/np.pi, dec*180/np.pi, unit = 'deg', frame='icrs')
        ra_rad = c.ra.wrap_at(180 * u.deg).radian
        dec_rad = c.dec.radian
        plt.scatter(ra_rad  , dec_rad,marker=(5, 2),color = 'r',label = 'Npulsars = {}'.format(Npulsars))

        plt.xticks(ticks=np.radians([-150, -120, -90, -60, -30, 0, \
                                     30, 60, 90, 120, 150]),
                   labels=['10h', '8h', '6h', '4h', '2h', '0h', \
                           '22h', '20h', '18h', '16h', '14h'])

        plt.xlabel('Right Ascension in hours')
        plt.ylabel('Declination in deg.')
        plt.grid(True)
        plt.legend(loc = 'upper right')
        plt.tight_layout()
        plt.show()

        pname = []
        for ii in range(Npulsars):
            coo = ICRS(ra[ii]*u.rad, dec[ii]*u.rad)
            to_replace = ['h','m','s']
            ra_coo = coo.ra.to_string(u.hourangle)
            dec_coo = coo.dec.to_string(u.hourangle)
            for tr in to_replace:
                ra_coo = ra_coo.replace(tr, ':')
                dec_coo = dec_coo.replace(tr, ':')

            dec_str = dec_coo.split(':')
            ra_str = ra_coo.split(':')
            if len(ra_str[0]) == 1:
                ra_str[0] = '0' + ra_str[0]

            if float(dec_str[0]) < 0 or dec_str[0] == '-0':
                pname.append("J" + ra_str[0] + ra_str[1] + dec_str[0] + dec_str[1])
            else:
                pname.append("J" + ra_str[0] + ra_str[1] + "+" +  dec_str[0] + dec_str[1])

        return lam, beta, pname, np.arccos(np.dot(pos_vec, pos_vec.T))

def GWBInj(Amp, start_obs, end_obs, Npulsars, ang, seed, toas):
    '''
    This function injects a GWB to a set of toas.

    :param: Amp: the amplitude of GWB
    :param: start_obs: starting observation time
    :param: end_obs: ending observation time
    :param: Npulsars: the number of pulsars in your pta
    :param: ang: a flat list of angular separation between pulsars
    :param: seed: sets the seed for the random number generator
    :param: toas: an array of arrays containing pulsar toas
    :output: gw_res: "post-fit" GW residuals in time-domain

    Author: Nima Laal
    '''
    day = 24*3600
    year = 365.25 * day
    kpc_to_meter = 3.086*10**(19)
    p_distance = 1 #kpc
    light_speed = 299792458
    f_yr = 1/year #reference frequency in seconds
    alpha = -2/3 #alpha
    howml = 10 #pre factor to extend the observation time. Needed to make the residuals non-periodic with period of each pulsar's Tspan.

    # gw start and end times for entire data set
    start = start_obs * day  - day
    stop =  end_obs * day + day
    dur = stop - start
    npts = int(dur/(day*30))
    # make a vector of evenly sampled data points
    ut = np.linspace(start, stop, npts)
    # time resolution in seconds
    dt = dur/npts

    # Define frequencies spanning from DC to Nyquist.
    # This is a vector spanning these frequencies in increments of 1/(dur*howml).
    freqs = np.arange(0, 1/(2*dt), 1/(dur*howml))
    freqs[0] = freqs[1] # avoid divide by 0 warning
    Nf = len(freqs)
    auto_indx = np.arange(0, Npulsars*Npulsars + 1, Npulsars + 1, int)

    chi = HD(ang)
    chi[auto_indx] = 1
    chi = chi.reshape((Npulsars, Npulsars))
    '''
    plt.figure(dpi = 150)
    plt.scatter(ang,chi,s = 2, color = 'aqua')
    plt.xlabel('Angular Separation')
    plt.ylabel('ORF');
    '''
    H = np.linalg.cholesky(chi)
    # Create random frequency series from zero mean, unit variance, Gaussian distributions
    np.random.seed(seed)
    w = np.random.normal(loc = 0, scale = 1, size = (Npulsars, len(freqs))) + 1j*np.random.normal(loc = 0, scale = 1, size = (Npulsars, len(freqs)))
    C = (dur * howml  * Amp**2/(48 * np.pi**2 * f_yr**(2*alpha)) * freqs**(2*alpha - 3))
    Res_f = np.einsum('ij,jk->ik', H, w*np.sqrt(C))
    Res_f[:,0] = 0
    Res_f[:,-1] = 0
    # Now fill in bins after Nyquist (for fft data packing) and take inverse FT
    Res_f2 = np.zeros((Npulsars, 2*Nf-2), complex)
    Res_t = np.zeros((Npulsars, 2*Nf-2))
    Res_f2[:,0:Nf] = Res_f[:,0:Nf]
    Res_f2[:, Nf:(2*Nf-2)] = np.conj(Res_f[:,(Nf-2):0:-1])
    Res_t = np.real(np.fft.ifft(Res_f2)/dt)
    # shorten data and interpolate onto TOAs
    Res = np.zeros((Npulsars, npts))
    res_gw = []
    for ll in range(Npulsars):
        Res[ll,:] = Res_t[ll, 10:(npts+10)]
        f = interp.interp1d(ut, Res[ll,:], kind='linear')
        res_gw.append(f(toas[0]*day))

    DesignM = np.array([np.ones((len(t),3)) for t in toas])
    I = np.array([np.identity(len(t)) for t in toas])
    DesignM[:,:,1] = toas * day
    DesignM[:,:,2] = DesignM[:,:,1]**2
    QuadFitM = I - np.einsum('ikn,inm,ipm->ikp', DesignM, np.linalg.inv(np.einsum('ikm,ikn->inm',DesignM,DesignM)),DesignM) #also known as R-matrix
    return np.einsum('ikp,ip->ik',QuadFitM,res_gw)

def HD (angle):
    return 3/2*( (1/3 + ((1-np.cos(angle))/2) * (np.log((1-np.cos(angle))/2) - 1/6)))

def weightedavg(rho, sig):
    weights, avg = 0., 0.
    for r,s in zip(rho,sig):
        weights += 1./(s*s)
        avg += r/(s*s)
    return avg/weights, np.sqrt(1./weights)

def binned_corr_Maker(xi, rho, sig, nbins = 20):
    n_pulsars_per_bin,bin_loc = np.histogram(xi, density = False, bins = nbins, range = (0, np.pi))
    xi_mean = []; xi_err = []; rho_avg = []; sig_avg = []
    for ii in range (len(bin_loc) - 1):
        mask = np.logical_and(xi >= bin_loc[ii] , xi < bin_loc[ii+1])
        if not rho[mask].size == 0:
            r, s = weightedavg(rho[mask], sig[mask])
            rho_avg.append(r); sig_avg.append(s)
            xi_mean.append(np.mean(xi[mask]))
            xi_err.append(np.std(xi[mask]))
    return np.array(xi_mean), np.array(xi_err), np.array(rho_avg), np.array(sig_avg)

def binned_corr_Maker_forced(xi, rho, sig, npairs = 66):
    idx = np.argsort(xi)
    xi_sorted = xi[idx]
    rho_sorted = rho[idx]
    sig_sorted = sig[idx]
    xi_mean = []; xi_err = []; rho_avg = []; sig_avg = []
    i = 0
    while i < len(xi_sorted):
        xi_mean.append(np.mean(xi_sorted[i:npairs+i]))
        xi_err.append(np.std(xi_sorted[i:npairs+i]))
        r, s = weightedavg(rho_sorted[i:npairs+i], sig_sorted[i:npairs+i])
        rho_avg.append(r)
        sig_avg.append(s)
        i += npairs
    return np.array(xi_mean), np.array(xi_err), np.array(rho_avg), np.array(sig_avg)

def gt( x, tau, mono ) :
    '''
    A simple way to parameterize transverse ORFs!
    :param: x: angular separation
    :param: tau: the parameter needed to search for all mathematically possible transverse orfs.
    :param: mono: off-set of the orfs
    
    Author: Nima Laal
    '''
    if np.all(x) == 0:
        return 1 + mono
    else:
        cos_ang = np.cos(x)
        k = 1/2*(1-cos_ang)
        return 1/8 * (3+cos_ang) + (1-tau)*3/4*k*np.log(k) + mono

class CrossModel(object):

    def __init__(self, rho, sig, xi, pmin=[-5e-11, -2], model='gt',
                 pmax=[5e-11, 2]):
        """
        Model class contains calls to log-likelihood and
        log-prior functions. All calls to log-likelihood
        and log-prior functions take in parameter array
        in the order:

        :param rho: Data vector containg correlations
        :param sig: Data vector containg weight of correlations
        :param xi: angular separation
        :param pmin: Minimum values of desired orf model
        :param pmax: Maximum values of desired orf model
        """

        self.rho = rho
        self.sig = sig
        self.xi = xi
        self.pmin = np.array(pmin)
        self.pmax = np.array(pmax)
        self.model = model

    def get_loglike(self, pars):
        if self.model == 'gt':
            mod = pars[0] * gt(self.xi, pars[1], 0)
            sigma = self.sig
        elif self.model == 'bettersigma':
            mod = pars[0] * gt(self.xi, -1, 0)
            sigma = self.sig *pars[0]
        elif self.model == 'findhdnorm':
            mod = pars[0] * gt(self.xi, -1, 0)
            sigma = self.sig
        diff = self.rho - mod
        loglike = -0.5 * np.sum(np.log(2*np.pi*sigma**2) + diff**2/sigma**2)
        return loglike

    def get_logprior(self, pars):
        prior = 0
        if np.all(pars > self.pmin) and np.all(pars < self.pmax):
            prior += -np.sum(np.log(self.pmax-self.pmin))
        else:
            prior = -np.inf
        return prior

    def get_prior_transform(self, cube):
        return (self.pmax - self.pmin) * cube + self.pmin

def lam_beta_to_xyz(lam, beta):
    """
    lam, beta in radians. Returns unit vectors on the sphere.
    lam:  longitude (0 to 2*pi)
    beta: latitude (-pi/2 to pi/2)
    """
    x = np.cos(beta) * np.cos(lam)
    y = np.cos(beta) * np.sin(lam)
    z = np.sin(beta)
    return np.stack([x, y, z], axis=-1)

def Mmat(toas):
    '''
    Simplest timing design-matrix
    '''
    DesignM = np.ones((len(toas), 3))
    DesignM[:,1] = toas
    DesignM[:,2] = DesignM[:,1]**2
    return DesignM