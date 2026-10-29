"""
Synthetic Clinical Gait Video Generator
Generates realistic articulated humanoid walking videos for testing and demonstration:
1. normal_gait.mp4: Healthy symmetrical adult gait (~110 steps/min, 62° knee flexion)
2. recurvatum_asymmetry.mp4: Right genu recurvatum (knee hyperextension) and antalgic stance asymmetry
3. stiff_knee_gait.mp4: Reduced swing-phase knee flexion and compensatory mechanics
"""

import os
import math
import cv2
import numpy as np

def draw_capsule(img, pt1, pt2, radius, color):
    """Draws a smooth anti-aliased limb segment capsule."""
    p1 = (int(pt1[0]), int(pt1[1]))
    p2 = (int(pt2[0]), int(pt2[1]))
    cv2.line(img, p1, p2, color, radius * 2, cv2.LINE_AA)
    cv2.circle(img, p1, radius, color, -1, cv2.LINE_AA)
    cv2.circle(img, p2, radius, color, -1, cv2.LINE_AA)

def generate_sample_video(output_path, gait_type="normal", fps=30, duration_sec=4.0):
    """
    Renders an articulated humanoid walking in sagittal/three-quarter view
    with natural biomechanical joint kinematics.
    """
    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    width, height = 720, 540
    total_frames = int(fps * duration_sec)
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    writer = cv2.VideoWriter(output_path, fourcc, fps, (width, height))

    cadence = 110.0  # steps / min
    cycle_duration = 60.0 / (cadence / 2.0)  # stride duration in seconds (~1.09s)
    frames_per_stride = int(fps * cycle_duration)

    # Base anatomy proportions (in pixels)
    trunk_len = 105
    thigh_len = 85
    shank_len = 80
    foot_len = 28
    arm_len = 70
    forearm_len = 65
    head_radius = 22

    # Visual colors (Healthcare lab setting)
    c_bg_top = (235, 240, 245)
    c_bg_floor = (195, 205, 215)
    c_wall_line = (180, 190, 205)
    floor_y = 440

    c_skin = (175, 195, 225)
    c_torso = (80, 70, 60)
    c_left_limb = (180, 90, 30)    # Blue tones
    c_right_limb = (30, 80, 190)   # Orange/Red tones for clear differentiation
    c_shoe = (40, 40, 40)

    for f in range(total_frames):
        img = np.zeros((height, width, 3), dtype=np.uint8)
        # Background gradient & clinical walking track
        img[:floor_y, :] = c_bg_top
        img[floor_y:, :] = c_bg_floor
        # Floor grid lines (treadmill / runway markers)
        cv2.line(img, (0, floor_y), (width, floor_y), c_wall_line, 2)
        grid_offset = int((f * 3.5) % 40)
        for gx in range(-40 + grid_offset, width + 40, 40):
            cv2.line(img, (gx, floor_y), (gx - 30, height), (170, 180, 195), 1)

        # Subtle clinic wall banner
        cv2.putText(img, "CLINICAL GAIT MOTION LAB - 3D ANALYSIS TRACK", (20, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (140, 150, 165), 1, cv2.LINE_AA)

        # Gait cycle phase calculation [0, 1)
        stride_phase = (f % frames_per_stride) / float(frames_per_stride)
        # Left leg phase is offset by 50% (anti-phase)
        r_phase = stride_phase
        l_phase = (stride_phase + 0.5) % 1.0

        # Kinematic Angle Generators (Sagittal Plane)
        def get_joint_angles(phase, is_right=False):
            # Normal angles
            # Hip: flexion at 0% (heel strike) -> extension at 50% (toe-off) -> flexion in swing
            hip_deg = 28.0 * math.cos(2.0 * math.pi * phase)
            
            # Normal Knee: Heel strike (5°), Loading (18° at 15%), Extension (2° at 40%), Peak Swing (64° at 75%)
            if phase < 0.15:
                # Initial contact to loading
                knee_deg = 4.0 + 14.0 * (phase / 0.15)
            elif phase < 0.45:
                # Loading to midstance extension
                knee_deg = 18.0 - 16.0 * ((phase - 0.15) / 0.30)
            elif phase < 0.60:
                # Terminal stance to pre-swing
                knee_deg = 2.0 + 28.0 * ((phase - 0.45) / 0.15)
            elif phase < 0.75:
                # Rapid swing flexion
                knee_deg = 30.0 + 34.0 * ((phase - 0.60) / 0.15)
            else:
                # Terminal swing extension
                knee_deg = 64.0 - 60.0 * ((phase - 0.75) / 0.25)

            # Ankle: plantarflexion at toe off, dorsiflexion in swing
            ankle_deg = 10.0 * math.sin(2.0 * math.pi * phase - 0.4)

            # Apply Pathological Gait Modifications
            if gait_type == "recurvatum" and is_right:
                # Hyperextension in midstance: knee snaps into negative angle (-7°) between 30% and 50%
                if 0.25 <= phase <= 0.50:
                    hyp_phase = (phase - 0.25) / 0.25
                    knee_deg = 2.0 - 9.0 * math.sin(math.pi * hyp_phase)

            if gait_type == "stiff_knee" and not is_right:
                # Reduced swing knee flexion (max only 40° instead of 64°)
                if phase > 0.60:
                    knee_deg = min(knee_deg, 38.0)

            return hip_deg, knee_deg, ankle_deg

        r_hip_ang, r_knee_ang, r_ankle_ang = get_joint_angles(r_phase, is_right=True)
        l_hip_ang, l_knee_ang, l_ankle_ang = get_joint_angles(l_phase, is_right=False)

        # Torso vertical bounce (center of mass sinusoidal translation)
        com_y_offset = -6.0 * math.cos(4.0 * math.pi * stride_phase)
        center_x = width // 2 - 20
        hip_center_y = floor_y - (thigh_len + shank_len) + 12 + com_y_offset

        # Slight trunk lean
        trunk_lean_deg = 3.5 if gait_type != "trunk_lean" else 11.0
        trunk_rad = math.radians(trunk_lean_deg)

        # Upper body coordinates
        shoulder_center_x = center_x + trunk_len * math.sin(trunk_rad)
        shoulder_center_y = hip_center_y - trunk_len * math.cos(trunk_rad)
        head_center_x = shoulder_center_x + 18 * math.sin(trunk_rad)
        head_center_y = shoulder_center_y - 28

        # Arm swing (counter-lateral to legs)
        r_shoulder_ang = -math.radians(24.0 * math.cos(2.0 * math.pi * r_phase))
        l_shoulder_ang = -math.radians(24.0 * math.cos(2.0 * math.pi * l_phase))

        # Helper to compute leg joints
        def solve_leg(hip_ang_deg, knee_flex_deg, ankle_ang_deg):
            hip_pt = (center_x, hip_center_y)
            # Thigh vector
            thigh_rad = math.radians(hip_ang_deg + trunk_lean_deg)
            knee_x = hip_pt[0] + thigh_len * math.sin(thigh_rad)
            knee_y = hip_pt[1] + thigh_len * math.cos(thigh_rad)

            # Shank vector (flexion bends knee posterior)
            shank_rad = thigh_rad - math.radians(knee_flex_deg)
            ankle_x = knee_x + shank_len * math.sin(shank_rad)
            ankle_y = knee_y + shank_len * math.cos(shank_rad)

            # Foot / Toe vector
            foot_rad = shank_rad + math.radians(90.0 + ankle_ang_deg)
            toe_x = ankle_x + foot_len * math.cos(foot_rad)
            toe_y = ankle_y + foot_len * math.sin(foot_rad)
            heel_x = ankle_x - 10 * math.cos(foot_rad)
            heel_y = ankle_y - 10 * math.sin(foot_rad)

            return hip_pt, (knee_x, knee_y), (ankle_x, ankle_y), (heel_x, heel_y), (toe_x, toe_y)

        r_hip, r_knee, r_ankle, r_heel, r_toe = solve_leg(r_hip_ang, r_knee_ang, r_ankle_ang)
        l_hip, l_knee, l_ankle, l_heel, l_toe = solve_leg(l_hip_ang, l_knee_ang, l_ankle_ang)

        # Arm coordinates
        r_elbow = (shoulder_center_x + arm_len * math.sin(r_shoulder_ang),
                   shoulder_center_y + arm_len * math.cos(r_shoulder_ang))
        r_hand = (r_elbow[0] + forearm_len * math.sin(r_shoulder_ang + 0.3),
                  r_elbow[1] + forearm_len * math.cos(r_shoulder_ang + 0.3))

        l_elbow = (shoulder_center_x + arm_len * math.sin(l_shoulder_ang),
                   shoulder_center_y + arm_len * math.cos(l_shoulder_ang))
        l_hand = (l_elbow[0] + forearm_len * math.sin(l_shoulder_ang + 0.3),
                  l_elbow[1] + forearm_len * math.cos(l_shoulder_ang + 0.3))

        # Render Left Limbs (background depth layer)
        draw_capsule(img, (shoulder_center_x, shoulder_center_y), l_elbow, 7, (120, 130, 145))
        draw_capsule(img, l_elbow, l_hand, 6, c_skin)
        draw_capsule(img, l_hip, l_knee, 13, c_left_limb)
        draw_capsule(img, l_knee, l_ankle, 10, c_left_limb)
        draw_capsule(img, l_heel, l_toe, 8, c_shoe)

        # Torso & Pelvis
        draw_capsule(img, (center_x, hip_center_y), (shoulder_center_x, shoulder_center_y), 19, c_torso)
        cv2.circle(img, (int(head_center_x), int(head_center_y)), head_radius, c_skin, -1, cv2.LINE_AA)

        # Render Right Limbs (foreground layer)
        draw_capsule(img, r_hip, r_knee, 14, c_right_limb)
        draw_capsule(img, r_knee, r_ankle, 11, c_right_limb)
        draw_capsule(img, r_heel, r_toe, 9, (20, 20, 20))
        draw_capsule(img, (shoulder_center_x, shoulder_center_y), r_elbow, 8, (70, 75, 85))
        draw_capsule(img, r_elbow, r_hand, 7, c_skin)

        # Frame counter & Gait condition badge
        badge_text = "SAMPLE A: Normal Symmetric Adult Gait" if gait_type == "normal" else \
                     "SAMPLE B: Right Genu Recurvatum & Stance Limp" if gait_type == "recurvatum" else \
                     "SAMPLE C: Left Stiff Knee Swing Deficiency"
        cv2.rectangle(img, (20, height - 42), (480, height - 12), (30, 35, 45), -1)
        cv2.putText(img, badge_text, (28, height - 23), cv2.FONT_HERSHEY_SIMPLEX, 0.48, (0, 235, 255), 1, cv2.LINE_AA)

        writer.write(img)

    writer.release()
    print(f"Generated sample video: {output_path} ({total_frames} frames)")
    return output_path

if __name__ == "__main__":
    base_dir = os.path.dirname(os.path.abspath(__file__))
    samples_dir = os.path.join(base_dir, "samples")
    generate_sample_video(os.path.join(samples_dir, "normal_gait.mp4"), "normal", fps=30, duration_sec=4.0)
    generate_sample_video(os.path.join(samples_dir, "recurvatum_asymmetry.mp4"), "recurvatum", fps=30, duration_sec=4.0)
    generate_sample_video(os.path.join(samples_dir, "stiff_knee_gait.mp4"), "stiff_knee", fps=30, duration_sec=4.0)
