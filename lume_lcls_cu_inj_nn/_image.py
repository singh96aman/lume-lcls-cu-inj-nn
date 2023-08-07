from lume_lcls_cu_inj_nn import __version__# Stanford Container Registry image
import os

if 'STANFORD_USERNAME' in os.environ: 
    STANFORD_USERNAME = os.environ['STANFORD_USERNAME']
else:
    STANFORD_USERNAME = 'aman96' #Please commit and change to the correct Stanford Username

IMAGE = f"scr.svc.stanford.edu/{STANFORD_USERNAME}"/lume-lcls-cu-inj-nn:v{__version__}"

print('Image Loaded - ', IMAGE)

