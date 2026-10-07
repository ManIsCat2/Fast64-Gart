import bpy
from bpy.utils import register_class, unregister_class
from bpy.props import FloatProperty
from collections import defaultdict
from ..utility import prop_split

# The original script was made by Baconator2558, slightly modifed by Cat,
# then tweaked yet again by me (Coolio) to repurpose it

def fix_texture(tex):
    img = tex.tex
    w, h = img.size
    pixels = img.pixels
    threshold = bpy.context.scene.cutout_alpha_threshold

    visible = [x > threshold for i, x in enumerate(pixels) if i % 4 == 3]

    def clamp_dimension(n, size, axis):
        if n < 0:
            if axis.clamp:
                return 0
            elif axis.mirror:
                return -n - 1
            else:
                return n + size
        elif n >= size:
            if axis.mirror:
                return size * 2 - n - 1
            elif axis.clamp:
                return size - 1
            else:
                return n % size

        return n

    def try_copy_rgb(x, y, src):
        dst = (clamp_dimension(x, w, tex.S) + clamp_dimension(y, h, tex.T)*w)*img.channels

        if pixels[dst+3] > threshold:
            return
        for c in range(3):
            pixels[dst+c] = pixels[src+c]

    for y in range(h):
        for x in range(w):
            i = (x + y*w)*img.channels

            if visible[x + y*w]:
                dirs = {
                    (-1,-1):True,( 0,-1):True,( 1,-1):True,
                    (-1, 0):True,             ( 1, 0):True,
                    (-1, 1):True,( 0, 1):True,( 1, 1):True,
                }

                for dir in [x for x in dirs.keys() if 0 in x]:
                    pos = clamp_dimension(x+dir[0], w, tex.S) + clamp_dimension(y+dir[1], h, tex.T)*w
                    if visible[pos]:
                        dirs[dir] = False
                        if dir[0] == 0:
                            dirs[(-1,dir[1])] = False
                            dirs[( 1,dir[1])] = False
                        else:
                            dirs[(dir[0],-1)] = False
                            dirs[(dir[0], 1)] = False

                for dir, do in dirs.items():
                    if do:
                        try_copy_rgb(x+dir[0], y+dir[1], i)

    img.update()
    
def fix_cutout(mat, force=False):
    if not mat.is_f3d:
        print(f"  Non-Fast3D material: {mat.name}")
    elif mat.f3d_mat.draw_layer.sm64 == '4' or force:
        print(f"  Cutout material: {mat.name}")

        if mat.f3d_mat.tex0.tex is not None:
            fix_texture(mat.f3d_mat.tex0)
        if mat.f3d_mat.tex1.tex is not None:
            fix_texture(mat.f3d_mat.tex1)

class Coop_CutoutFixOperator(bpy.types.Operator):
    bl_idname = "object.custom_sm64_cutout_fix_function"
    bl_label = "CutoutFixOperator"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        for mat in bpy.data.materials:
            fix_cutout(mat)

        return {'FINISHED'}

class Coop_CutoutFixOperatorObject(bpy.types.Operator):
    bl_idname = "object.custom_sm64_cutout_fix_function_object"
    bl_label = "CutoutFixOperatorObject"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        obj = context.active_object
        if obj and obj.type == 'MESH':
            print(f"Mesh: {obj.name}")

            for mat in obj.data.materials:
                fix_cutout(mat)
            return {'FINISHED'}
        else:
            self.report({'INFO'}, "No active mesh")
            return {'CANCELLED'}

class Coop_CutoutFixOperatorMaterial(bpy.types.Operator):
    bl_idname = "object.custom_sm64_cutout_fix_function_material"
    bl_label = "CutoutFixOperatorMaterial"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        obj = context.active_object
        if obj and obj.type == 'MESH':
            print(f"Mesh: {obj.name}")

            if obj.active_material is not None:
                fix_cutout(obj.active_material, True)
            return {'FINISHED'}
        else:
            self.report({'INFO'}, "No active mesh")
            return {'CANCELLED'}

class Coop_CutoutFixPanel(bpy.types.Panel):
    bl_idname = "VIEW3D_PT_CUTOUTFIX"
    bl_label = "SM64 Cutout Fixer"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Coop"

    def draw(self, context):
        col = self.layout.column()
        prop_split(col, context.scene, "cutout_alpha_threshold", "Alpha Threshold")
        col.operator("object.custom_sm64_cutout_fix_function", text="Fix All Materials")
        col.operator("object.custom_sm64_cutout_fix_function_object", text="Fix Active Object Materials")
        col.operator("object.custom_sm64_cutout_fix_function_material", text="Fix Selected Material")

classes = (
    Coop_CutoutFixOperator,
    Coop_CutoutFixOperatorObject,
    Coop_CutoutFixOperatorMaterial,
    Coop_CutoutFixPanel
)

def cutout_fix_register():
    for cls in classes:
        register_class(cls)

    bpy.types.Scene.cutout_alpha_threshold = FloatProperty(
        name="cutout_alpha_threshold",
        default=0.125,
        soft_min=0, soft_max=1
    )


def cutout_fix_unregister():
    for cls in classes:
        unregister_class(cls)

    del bpy.types.Scene.cutout_alpha_threshold
