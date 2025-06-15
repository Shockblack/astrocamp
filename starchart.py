import astropy.coordinates as coord
import astropy.units as u
from photutils.aperture import SkyCircularAperture
from astropy.io import fits
import subprocess as sp
from astropy.wcs import WCS
import os
import matplotlib.pyplot as plt


# Get an RA and DEC of target
center_coords = coord.SkyCoord(ra='20:00:10.98', dec='+21:44:26.2', unit=(u.hourangle, u.deg))

# Create a circular aperture around the target
aperture = SkyCircularAperture(center_coords, r=20 * u.arcsec)

ra_str = [str(int(center_coords.ra.hms.h)), str(int(center_coords.ra.hms.m)), round(center_coords.ra.hms.s, 3)]
dec_str = [int(center_coords.dec.dms.d), str(int(center_coords.dec.dms.m)), round(center_coords.dec.dms.s, 3)]

# Need seconds string to be of form xx.xx
ra_str[2] = str(ra_str[2]).rjust(5, '0')
dec_str[2] = str(dec_str[2]).rjust(5, '0')

if dec_str[0] > 0:
    dec_str[0] = '+' + str(dec_str[0])
else:
    dec_str[0] = str(dec_str[0])

temp_file = open('dss1_inputs.in', 'w')
exe_str = f"dssref {ra_str[0]} {ra_str[1]} {ra_str[2]} {dec_str[0]} {dec_str[1]} {dec_str[2]} 50 50"
temp_file.write(exe_str)
temp_file.close()

# run while suppressing output
sp.run(['dss1', '-i', 'dss1_inputs.in'], stdout=sp.DEVNULL, stderr=sp.DEVNULL)

# Get fits files with 'dssref' in the name
reference_fits = [f for f in os.listdir('.') if 'dssref' in f and f.endswith('.fits')][0]

reference_fit = fits.open(reference_fits)
wcs = WCS(reference_fit[0].header)
aperture = aperture.to_pixel(wcs)

# Add wcs projection to the aperture
plt.imshow(reference_fit[0].data, cmap='gray', origin='lower')
aperture.plot(color='red', lw=2, alpha=1)
plt.show()

os.remove('dss1_inputs.in')
os.remove(reference_fits)