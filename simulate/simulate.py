# SPDX-FileCopyrightText: 2026 Jordan Henshaw
#
# SPDX-License-Identifier: GPL-3.0-or-later

import bpy
import math

from .mach_angle import find_mach_angle
from .orient_cone import get_cone_orientation
from .scale_cone import get_cone_final_scale
from .scale_sphere import get_sphere_final_scale

DEG_TO_RAD = 0.0174533
SECONDS_PER_FRAME = 0.001
BASE_CONE_DEPTH = 2.0
BASE_SPHERE_RADIUS = 1.0
START_SCALE = 1e-4
KEYFRAME_INTERPOLATION = 'LINEAR'


class Simulate:
    '''
    Context: We want Blender to visualize a mach cone and muzzle blast from a rifle.

    Time Scaling: A viewport frame is too short a time. So we will say 1 Blender frame is .001 ms regardless of fps.

    Inputs: We receive an Algorithm object which contains the pre-calculated math data for the setup.

    Outputs: It just creates a cone, a sphere, and animates them to simulate how they move through the air.
    '''
    def __init__(self, scene, ao, Algorithm):
        self.scene = scene
        self.ao = ao
        self.Algorithm = Algorithm


    def execute(self):
        self.get_mach_angle()
        self.get_cone_orientation()
        self.get_cone_final_scale()
        self.get_sphere_final_scale()
        self.prepare_blender_timeline()
        self.create_objects()
        self.create_bullet()
        self.parent_cone_to_bullet()
        self.orient_cone()

        self.scale_objects_start()
        self.keyframe_objects_start()

        self.scale_objects_end()
        self.keyframe_objects_end()

        self.keyframe_bullet_start()
        self.keyframe_bullet_end()


    def get_mach_angle(self): 
        self.mach_angle = find_mach_angle(self.Algorithm)

    def get_cone_orientation(self):
        self.cone_rotation_euler = get_cone_orientation(self)

    def get_cone_final_scale(self):
        self.final_cone_scale = get_cone_final_scale(self)

    def get_sphere_final_scale(self):
        self.final_sphere_scale = get_sphere_final_scale(self)

    def prepare_blender_timeline(self):
        duration_flight = self.Algorithm.rifle.duration_flight
        frames = max(1, int(math.ceil(duration_flight / SECONDS_PER_FRAME)))

        self.start_frame = 1
        self.end_frame = self.start_frame + frames

        self.scene.frame_start = self.start_frame
        self.scene.frame_end = self.end_frame
        self.scene.frame_set(self.start_frame)

    def create_objects(self):
        origin = self.Algorithm.rifle_origin_world 
        mach_angle_rad = self.mach_angle * DEG_TO_RAD

        bpy.ops.mesh.primitive_cone_add(
            vertices=32,
            radius1=BASE_CONE_DEPTH * math.tan(mach_angle_rad),
            radius2=0.0,
            depth=BASE_CONE_DEPTH,
            enter_editmode=True,
            location=origin
        )

        self.cone_obj = bpy.context.active_object
        self.cone_obj.name = "Mach_Cone"

        bpy.ops.transform.translate(value=(0, 0, -BASE_CONE_DEPTH / 2.0))
        bpy.ops.object.mode_set(mode='OBJECT')

        bpy.ops.mesh.primitive_uv_sphere_add(
            segments=32,
            ring_count=16,
            radius=BASE_SPHERE_RADIUS,
            enter_editmode=False,
            location=origin
        )
        self.sphere_obj = bpy.context.active_object
        self.sphere_obj.name = "Muzzle_Blast"

        self.cone_obj.display_type = 'WIRE'
        self.sphere_obj.display_type = 'WIRE'

    def create_bullet(self):
        origin = self.Algorithm.rifle_origin_world
        self.bullet_obj = bpy.data.objects.new("Bullet_Apex", None)
        bpy.context.collection.objects.link(self.bullet_obj)
        self.bullet_obj.location = origin

    def parent_cone_to_bullet(self):
        self.cone_obj.parent = self.bullet_obj
        self.cone_obj.matrix_parent_inverse = self.bullet_obj.matrix_world.inverted()
        self.cone_obj.location = (0.0, 0.0, -BASE_CONE_DEPTH / 2.0)
        self.cone_obj.rotation_euler = (0.0, 0.0, 0.0)
        self.cone_obj.scale = (1.0, 1.0, 1.0)

    def orient_cone(self):
        self.bullet_obj.rotation_mode = 'XYZ'
        self.bullet_obj.rotation_euler = self.cone_rotation_euler

    def scale_objects_start(self):
        s = START_SCALE
        self.cone_obj.scale = (s, s, s)
        self.sphere_obj.scale = (s, s, s)

    def keyframe_objects_start(self):
        self.scene.frame_set(self.start_frame)

        self.cone_obj.keyframe_insert(data_path="scale", frame=self.start_frame)
        self.sphere_obj.keyframe_insert(data_path="scale", frame=self.start_frame)

        set_linear(self.cone_obj)
        set_linear(self.sphere_obj)

    def scale_objects_end(self):
        self.scene.frame_set(self.end_frame)
        s = self.final_cone_scale
        self.cone_obj.scale = (s, s, s)

        s = self.final_sphere_scale
        self.sphere_obj.scale = (s, s, s)

    def keyframe_objects_end(self):
        self.cone_obj.keyframe_insert(data_path="scale", frame=self.end_frame)
        self.sphere_obj.keyframe_insert(data_path="scale", frame=self.end_frame)

        set_linear(self.cone_obj)
        set_linear(self.sphere_obj)

    def keyframe_bullet_start(self):
        origin = self.Algorithm.rifle_origin_world
        self.scene.frame_set(self.start_frame)
        self.bullet_obj.location = origin
        self.bullet_obj.keyframe_insert(data_path="location", frame=self.start_frame)
        set_linear(self.bullet_obj)

    def keyframe_bullet_end(self):
        origin = self.Algorithm.rifle_origin_world
        duration_flight = self.Algorithm.rifle.duration_flight
        v = self.Algorithm.bullet_speed_mps
        bullet_distance = duration_flight * v

        self.scene.frame_set(self.end_frame)
        self.bullet_obj.location = origin + (self.dir_unit * bullet_distance)
        self.bullet_obj.keyframe_insert(data_path="location", frame=self.end_frame)
        set_linear(self.bullet_obj)


def set_linear(obj):
    if not obj.animation_data:
        return
    action = obj.animation_data.action
    if not action:
        return

    for fcurve in action.fcurves:
        for kp in fcurve.keyframe_points:
            kp.interpolation = KEYFRAME_INTERPOLATION