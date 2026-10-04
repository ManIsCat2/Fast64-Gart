import bpy
from .fix_bone import *
from .fix_cutouts import *
from bpy.utils import register_class, unregister_class

def coop_register():
    bone_fix_register()
    cutout_fix_register()

def coop_unregister():
    bone_fix_unregister()
    cutout_fix_unregister()