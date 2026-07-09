import bpy
from bpy.utils import register_class, unregister_class
from collections import defaultdict

#bl_info = {
#    "name": "SM64 Bone Fixer",
#    "author": "Baconator2558",
#    "version": (1, 1),
#    "blender": (3, 6, 4),
#    "location": "3DView",
#    "description": "Fix SM64 bones in Fast64 Gart",
#    "category": "Import-Export"
#}

# This script was made by Baconator2558, For fixing bones that don't work in blender
# Slightly modifed by me (Cat)


def fix_sm64_custom_bone(
    bone
):
    if "fast64" not in bone or "sm64" not in bone.fast64:
        print(f"  Non-SM64 Bone: {bone.name}")
    elif "custom_geo_cmd_args" in bone.fast64.sm64 or "custom_geo_cmd_macro" in bone.fast64.sm64:
        print(f"  SM64 Bone: {bone.name}")
        if (bone.geo_cmd == 15):
            bone.geo_cmd = "Custom"
        if "custom" in bone.fast64.sm64:
            if (not bone.geo_cmd == "Custom"):
                print(f" Formerly Custom Bone: {bone.name}")
            else:
                print(f" Custom Bone: {bone.name}")
                if "custom_geo_cmd_macro" in bone.fast64.sm64:
                    temp_cmd = bone.fast64.sm64.get("custom_geo_cmd_macro")
                    bone.fast64.sm64.custom.str_cmd = temp_cmd
                    if temp_cmd == "GEO_ASM":
                        bone.fast64.sm64.custom.dl_option = "NONE"
                    bone.fast64.sm64.custom.cmd_type = "Geo"
                if "custom_geo_cmd_args" in bone.fast64.sm64:
                    args_full = bone.fast64.sm64.get("custom_geo_cmd_args")
                    args_split = args_full.split(',')
                    bone.fast64.sm64.custom.args_tab = True
                    bone.fast64.sm64.custom.args.clear()
                    i = 0
                    for split_arg in args_split:
                        bone.fast64.sm64.custom.args.add()
                        bone.fast64.sm64.custom.args[i].arg_type = "PARAMETER"
                        bone.fast64.sm64.custom.args[i].parameter = split_arg.lstrip()
                        i = i + 1


class Coop_BoneFixOperator(bpy.types.Operator):
    bl_idname = "object.custom_sm64_bone_fix_function"
    bl_label = "BoneFixOperator"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        for obj in bpy.context.scene.objects:
            if obj.type == 'ARMATURE':
                print(f"Armature: {obj.name}")

                for bone in obj.data.bones:
                    fix_sm64_custom_bone(bone)
        return {'FINISHED'}

class Coop_BoneFixOperatorArmature(bpy.types.Operator):
    bl_idname = "object.custom_sm64_bone_fix_function_armature"
    bl_label = "BoneFixOperatorArmature"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        obj = bpy.context.active_object
        if obj and obj.type == 'ARMATURE':
            print(f"Armature: {obj.name}")

            for bone in obj.data.bones:
                fix_sm64_custom_bone(bone)
            return {'FINISHED'}
        else:
            self.report({'INFO'}, "No active armature")
            return {'CANCELLED'}

class Coop_BoneFixPanel(bpy.types.Panel):
    bl_idname = "VIEW3D_PT_BONEFIX"
    bl_label = "SM64 Custom Bone Fixer"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Coop"

    def draw(self, context):
        layout = self.layout

        split = layout.split()

        col = split.column()
        col.operator("object.custom_sm64_bone_fix_function", text="Fix All Custom SM64 Bones")
        if bpy.context.mode == 'EDIT_ARMATURE':
            col.label(text="Fix Active Armature's Bones", icon='LOCKED')
        else:
            col.operator("object.custom_sm64_bone_fix_function_armature", text="Fix Active Armature's Bones")

classes = (
    Coop_BoneFixOperator,
    Coop_BoneFixOperatorArmature,
    Coop_BoneFixPanel
)

def bone_fix_register():
    for cls in classes:
        register_class(cls)


def bone_fix_unregister():
    for cls in classes:
        unregister_class(cls)