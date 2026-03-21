# SPDX-FileCopyrightText: 2026 Jordan Henshaw
#
# SPDX-License-Identifier: GPL-3.0-or-later

import bpy
import math
from mathutils import Vector

from .scale_thump import get_sphere_final_scale
from .air_drag import distance_at_time

SECONDS_PER_FRAME = 0.001
FRAME_STEP = 5
DRAG_COEFF = 0.12
BASE_SPHERE_RADIUS = 1.0
START_SCALE = 1e-4
KEYFRAME_INTERPOLATION = 'LINEAR'


class SimulateAdvanced:
    '''
    Context: We want Blender to visualize a mach cone and muzzle blast from a rifle.

    Time Scaling: A viewport frame is too short a time. So we will say 1 Blender frame is 1 ms regardless of fps.

    Inputs: We receive an Algorithm object, which contains the pre-calculated math data for the setup.

    Outputs: It just creates a muzzle blast sphere, an empty representing the bullet, and spheres along the
    empty's path representing its sound. The mach cone naturally arises from this setup as the spheres grow at
    the speed of sound.
    '''
    def __init__(self, scene, ao, Algorithm):
        self.scene = scene
        self.ao = ao
        self.Algorithm = Algorithm

        self.origin = Vector(self.Algorithm.rifle_origin_world)
        self.endpoint = Vector(self.Algorithm.rifle_endpoint)

        direction = self.endpoint - self.origin
        if direction.length == 0.0:
            raise ValueError("rifle_endpoint is the same as rifle_origin_world")

        self.dir_unit = direction.normalized()

    def execute(self):
        self.get_sphere_final_scale()
        self.prepare_blender_timeline()
        self.create_muzzle_blast()
        self.create_bullet()
        self.create_frames_dict()

        self.scale_blast_start()
        self.keyframe_blast_start()

        self.scale_objects_end()
        self.keyframe_objects_end()

        self.keyframe_bullet_start()
        self.keyframe_bullet_end()

        self.process_bullet_frames()

    def get_sphere_final_scale(self):
        self.final_sphere_scale = get_sphere_final_scale(self)

    def prepare_blender_timeline(self):
        duration_flight = float(self.Algorithm.rifle.duration_flight)
        frames = max(1, int(math.ceil(duration_flight / SECONDS_PER_FRAME)))

        self.start_frame = 1
        self.end_frame = self.start_frame + frames

        self.scene.frame_start = self.start_frame
        self.scene.frame_end = self.end_frame
        self.scene.frame_set(self.start_frame)

    def create_muzzle_blast(self):
        bpy.ops.mesh.primitive_uv_sphere_add(
            segments=32,
            ring_count=16,
            radius=BASE_SPHERE_RADIUS,
            enter_editmode=False,
            location=self.origin
        )
        self.sphere_obj = bpy.context.active_object
        self.sphere_obj.name = "Muzzle_Blast"
        self.sphere_obj.display_type = 'WIRE'

    def create_bullet(self):
        self.bullet_obj = bpy.data.objects.new("Bullet_Apex", None)
        self.scene.collection.objects.link(self.bullet_obj)
        self.bullet_obj.location = self.origin

    def create_frames_dict(self):
        frames = {}

        for frame in range(self.start_frame + 1, self.end_frame + 1, FRAME_STEP):
            t_emit = self.frame_to_time(frame)
            new_pos = self.time_to_position(t_emit)

            remaining_time = self.frame_to_time(self.end_frame) - t_emit
            sphere_final_scale = self.time_to_scale_final(remaining_time)

            frames[frame] = (new_pos, sphere_final_scale)

        self.frames_dict = frames

    def scale_blast_start(self):
        s = START_SCALE
        self.sphere_obj.scale = (s, s, s)

    def keyframe_blast_start(self):
        self.scene.frame_set(self.start_frame)
        self.sphere_obj.keyframe_insert(data_path="scale", frame=self.start_frame)
        set_linear(self.sphere_obj)

    def process_bullet_frames(self):
        for frame, (location, final_scale) in self.frames_dict.items():
            self.sphere_add(frame, location, final_scale)

    def sphere_add(self, frame, location, final_scale):
        bpy.ops.mesh.primitive_uv_sphere_add(
            segments=24,
            ring_count=12,
            radius=BASE_SPHERE_RADIUS,
            enter_editmode=False,
            location=location
        )
        obj = bpy.context.active_object
        obj.name = f"Sound_{frame:04d}"
        obj.display_type = 'WIRE'

        self.scene.frame_set(frame)
        obj.scale = (START_SCALE, START_SCALE, START_SCALE)
        obj.keyframe_insert(data_path="scale", frame=frame)

        self.scene.frame_set(self.end_frame)
        obj.scale = (final_scale, final_scale, final_scale)
        obj.keyframe_insert(data_path="scale", frame=self.end_frame)

        set_linear(obj)

    def scale_objects_end(self):
        self.scene.frame_set(self.end_frame)
        s = self.final_sphere_scale
        self.sphere_obj.scale = (s, s, s)

    def keyframe_objects_end(self):
        self.sphere_obj.keyframe_insert(data_path="scale", frame=self.end_frame)
        set_linear(self.sphere_obj)

    def keyframe_bullet_start(self):
        self.scene.frame_set(self.start_frame)
        self.bullet_obj.location = self.origin
        self.bullet_obj.keyframe_insert(data_path="location", frame=self.start_frame)
        set_linear(self.bullet_obj)

    def keyframe_bullet_end(self):
        self.scene.frame_set(self.end_frame)
        self.bullet_obj.location = self.time_to_position(
            float(self.Algorithm.rifle.duration_flight)
        )
        self.bullet_obj.keyframe_insert(data_path="location", frame=self.end_frame)
        set_linear(self.bullet_obj)

    def frame_to_time(self, frame):
        return (frame - self.start_frame) * SECONDS_PER_FRAME

    def time_to_distance(self, t_seconds):
        return distance_at_time(t_seconds, self.Algorithm.bullet_speed_mps)

    def time_to_position(self, t_seconds):
        return self.origin + (self.dir_unit * self.time_to_distance(t_seconds))

    def time_to_scale_final(self, remaining_time):
        total_time = float(self.Algorithm.rifle.duration_flight)
        if total_time <= 0.0:
            return START_SCALE

        scale = self.final_sphere_scale * (remaining_time / total_time)
        return max(START_SCALE, scale)


def set_linear(obj):
    if not obj.animation_data:
        return
    action = obj.animation_data.action
    if not action:
        return

    for fcurve in action.fcurves:
        for kp in fcurve.keyframe_points:
            kp.interpolation = KEYFRAME_INTERPOLATION