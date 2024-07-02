"""The goal is to create an OCIO config file that is compatible with ACES which is fast to generate and easy to maintain.

TODO:
    - [] Remove the views
    - [] Add the camera transforms
"""

import shutil

import opencolorio_config_aces
import PyOpenColorIO as OCIO
import yaml

generated_aces_config = opencolorio_config_aces.generate_config_aces()

studio_config = opencolorio_config_aces.generate_config_studio()

yaml_string = """
aliases:
  - &working_var "$working"
  - &reference_var "$reference"
  - &rrtodt_var "$rrtodt"
  - &rrtinput_var "$rrtinput"
  - &shaper_var "$shaper"
  - &lmt_var "$lmt"
  - &secondary_lmt_var "$lmt2"

search_paths:
  - /$DD_SHOWS_ROOT/$DD_SHOW/$DD_SEQ/$DD_SHOT/SHARED/COMP/scene/nukescript_avidlut/nuke_avidlut/main/avidlut
  - /$DD_SHOWS_ROOT/$DD_SHOW/$DD_SEQ/$DD_SHOT/SHARED/COMP/scene/nukescript_avidgrade/nuke_avidgrade/main/avidgrade
  - /$DD_SHOWS_ROOT/$DD_SHOW/$DD_SEQ/$DD_SHOT/SHARED/COMP/scene/nukescript_bakedgrade/nuke_bakedgrade/main/bakedgrade
  - /$DD_SHOWS_ROOT/$DD_SHOW/$DD_SEQ/$DD_SHOT/SHARED/COMP/scene/nukescript_grade/nuke_grade/main/grade
  - /$DD_SHOWS_ROOT/$DD_SHOW/$DD_SEQ/$DD_SHOT/SHARED/SCRIPTS/nuke/avidgrades/avidgrade
  - /$DD_SHOWS_ROOT/$DD_SHOW/$DD_SEQ/$DD_SHOT/SHARED/SCRIPTS/nuke/grades/grade
  - /$DD_SHOWS_ROOT/$DD_SHOW/$DD_SEQ/SHARED/COMP/scene/nukescript_avidlut/nuke_avidlut/main/avidlut
  - /$DD_SHOWS_ROOT/$DD_SHOW/$DD_SEQ/SHARED/COMP/scene/nukescript_avidgrade/nuke_avidgrade/main/avidgrade
  - /$DD_SHOWS_ROOT/$DD_SHOW/$DD_SEQ/SHARED/COMP/scene/nukescript_bakedgrade/nuke_bakedrade/main/bakedgrade
  - /$DD_SHOWS_ROOT/$DD_SHOW/$DD_SEQ/SHARED/COMP/scene/nukescript_grade/nuke_grade/main/grade
  - /$DD_SHOWS_ROOT/$DD_SHOW/$DD_SEQ/SHARED/SCRIPTS/nuke/avidgrades/avidgrade
  - /$DD_SHOWS_ROOT/$DD_SHOW/$DD_SEQ/SHARED/SCRIPTS/nuke/grades/grade
  - /$DD_SHOWS_ROOT/$DD_SHOW/SHARED/COMP/scene/nukescript_avidlut/nuke_avidlut/main/avidlut
  - /$DD_SHOWS_ROOT/$DD_SHOW/SHARED/COMP/scene/nukescript_avidgrade/nuke_avidgrade/main/avidgrade
  - /$DD_SHOWS_ROOT/$DD_SHOW/SHARED/COMP/scene/nukescript_grade/nuke_grade/main/grade
  - /$DD_SHOWS_ROOT/$DD_SHOW/SHARED/COMP/scene/nukescript_bakedgrade/nuke_bakedgrade/main/bakedgrade
  - /$DD_SHOWS_ROOT/$DD_SHOW/SHARED/SCRIPTS/nuke/avidgrades/avidgrades
  - /$DD_SHOWS_ROOT/$DD_SHOW/SHARED/SCRIPTS/nuke/grades/grade
  - /$DD_FACILITY_ROOT/color/luts/null_grade/
  - luts

rolesCreate:
  - Name: "color_picking"
    Space: *working_var
  - Name: "color_timing"
    Space: *shaper_var
  - Name: "compositing_linear"
    Space: *working_var
  - Name: "compositing_log"
    Space: *shaper_var
  - Name: "data"
    Space: "Utility - Raw"
  - Name: "default"
    Space: *working_var
  - Name: "matte_paint"
    Space: *shaper_var
  - Name: "reference"
    Space: *reference_var
  - Name: "rendering"
    Space: *working_var
  - Name: "scene_linear"
    Space: *working_var
  - Name: "texture_paint"
    Space: *rrtodt_var
  - Name: "output_transform"
    Space: "show_lut"
  - Name: "display_linear"
    Space: *rrtodt_var
  - Name: "sRGB_image"
    Space: "Utility - sRGB - Texture"
  - Name: "sRGB_primaries"
    Space: "Utility - Linear - sRGB"
  - Name: "sRGB_curve"
    Space: "sRGB-AP1"
  - Name: "cineon_curve"
    Space: "Cineon-1D"
  - Name: "cineon_image"
    Space: "Cineon-Rec709"
  - Name: "substance_3d_painter_standard_srgb"
    Space: "Utility - sRGB - Texture"
  - Name: "substance_3d_painter_bitmap_import_8bit"
    Space: "Utility - sRGB - Texture"
  - Name: "substance_3d_painter_bitmap_import_16bit"
    Space: "Utility - sRGB - Texture"
  - Name: "substance_3d_painter_bitmap_import_floating"
    Space: "ACES - ACEScg"
  - Name: "substance_3d_painter_substance_material"
    Space: "ACES - ACEScg"
  - Name: "substance_3d_painter_bitmap_export_8bit"
    Space: "sRGB-AP1"
  - Name: "substance_3d_painter_bitmap_export_16bit"
    Space: "sRGB-AP1"
  - Name: "substance_3d_painter_bitmap_export_floating"
    Space: "ACES - ACEScg"
  - Name: "mari_int8"
    Space: "Utility - sRGB - Texture"
  - Name: "mari_int16"
    Space: "Utility - sRGB - Texture"
  - Name: "mari_scalar8"
    Space: "Utility - Raw"
  - Name: "mari_float"
    Space: *working_var
  - Name: "mari_working"
    Space: *working_var
  - Name: "mari_monitor"
    Space: "Output - Rec.709"
  - Name: "mari_scalar_monitor"
    Space: "Utility - Raw"
  - Name: "mari_blending"
    Space: *working_var
  - Name: "mari_color_picker"
    Space: *working_var


active_displays: "sRGB"
active_views: "Comp, ShowLut, Raw, Reference"
"""
# Write this to a file

# Create a sample configuration
config = studio_config  # type: OCIO.Config()

# Clear the displays
# config.clearDisplays()
# Clear the shared views
# config.clearSharedViews()

# Serialize the configuration to a string

clean_ocio_config = OCIO.Config()
color_spaces_alias = []
# clean_ocio_config.setRole('scene_linear', 'ACES - ACEScg')


# Copy the colorspaces from the aces config
for colorspace in config.getColorSpaces():
    color_spaces_alias.extend(colorspace.getAliases())
    clean_ocio_config.addColorSpace(colorspace)


# Create custom views


# Play with the search paths
# Load the yaml from the string

magento_preference = yaml.safe_load(yaml_string)
search_paths = magento_preference.get("search_paths")

# Add the search paths
for path in search_paths:
    clean_ocio_config.addSearchPath(path)

# Create the custom roles



for role in magento_preference.get("rolesCreate"):
    # Check if the colorspace exists
    if role["Space"] not in color_spaces_alias:
        continue
    clean_ocio_config.setRole(role["Name"], role["Space"])




config.clearDisplays()
new_stereo_display = opencolorio_config_aces.generate_config_aces(
    describe=opencolorio_config_aces.DescriptionStyle.NONE
)
path = "/home/robert-v/dev/config.ocio"
# Write the serialized string to a file
with open(path, "w") as open_file:
    open_file.write(new_stereo_display.serialize())

print(f"Configuration written to {path}")

shutil.copyfile(path, "/vfx/config.ocio")