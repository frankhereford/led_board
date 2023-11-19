import bpy


for mat in bpy.data.materials:
    if mat.name.startswith("EmissionMaterial") and mat.users:
        pass

