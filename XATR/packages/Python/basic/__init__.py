"""Basic MATS modules."""
import mats.log

version_ = "1.0"
developer_ = "NSWC PCD (S33)"
descriptions_ = {}

try:
    from .sensImageRGB import sensImageRGB
    descriptions_["sensImageRGB"] = "Image-RGB sensor."
except ImportError:
    mats.log.error('Failed to load sensImageRGB module from basic package.')

try:
    from .mshdf import rdrMSHDF
    descriptions_["rdrMSHDF"] = "MSHDF reader."
except ImportError:
    mats.log.error('Failed to load rdrMSHDF module from basic package.')

try:
    from .jpeg import rdrJPEG
    descriptions_["rdrJPEG"] = "JPEG reader."
except ImportError:
    mats.log.error('Failed to load rdrJPEG module from basic package.')

try:
    from .detFusion import detFusion
    descriptions_['detFusion'] = "Detector module for fusing other detector modules."
except ImportError:
    mats.log.error('Failed to load detFusion module from basic package.')

try:
    from .xatr_image_pipeline import XatrImagePipeline
    descriptions_['XatrImagePipeline'] = 'Image-RGB processing pipline.'
except ImportError:
    mats.log.error('Failed to load XatrImagePipeline module.')

# NOTE(Bradley): Put interface last because otherwise it doesn't seem to find
# other modules.
try:
    from .xatr import XATRCPP
    descriptions_["XATRCPP"] = "MATS_C interface for python."
except ImportError:
    mats.log.error('Failed to load XATRCPP module from basic package.')
