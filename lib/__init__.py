import os

current_dir = os.path.basename(os.path.realpath(__file__))
ml_vfx_root = os.path.abspath(os.path.join(current_dir, '..'))
os.environ['ML_VFX_ROOT'] = ml_vfx_root
