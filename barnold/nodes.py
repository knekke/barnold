# -*- coding: utf-8 -*-

__author__ = "Ildar Nikolaev"
__email__ = "nildar@users.sourceforge.net"

import bpy
import nodeitems_utils
from bpy.props import BoolProperty

from . import ArnoldRenderEngine


@ArnoldRenderEngine.register_class
class ArnoldNodeOutput(bpy.types.Node):
    bl_label = "Output"
    bl_icon = 'MATERIAL'

    def _get_active(self):
        return not self.mute

    def _set_active(self, value=True):
        for node in self.id_data.nodes:
            if type(node) is ArnoldNodeOutput:
                node.mute = (self != node)

    is_active = BoolProperty(
        name="Active",
        description="Active Output",
        get=_get_active,
        set=_set_active
    )

    def init(self, context):
        self._set_active()
        sock = self.inputs.new("NodeSocketShader", "Shader")

    def draw_buttons(self, context, layout):
        layout.prop(self, "is_active", icon='RADIOBUT_ON' if self.is_active else 'RADIOBUT_OFF')


class ArnoldNode:
    @property
    def ai_properties(self):
        return {}


@ArnoldRenderEngine.register_class
class ArnoldNodeLambert(bpy.types.Node, ArnoldNode):
    bl_label = "Lambert"
    bl_icon = 'MATERIAL'

    AI_NAME = "lambert"

    def init(self, context):
        sock = self.inputs.new("NodeSocketFloat", "Kd")
        sock.default_value = 0.7
        sock = self.inputs.new("NodeSocketColor", "Kd_color")
        sock.default_value = (1, 1, 1, 1)
        sock = self.inputs.new("NodeSocketColor", "Opacity", "opacity")
        sock.default_value = (1, 1, 1, 1)

        self.outputs.new("NodeSocketShader", "RGB", "output")


@ArnoldRenderEngine.register_class
class ArnoldNodeStandard(bpy.types.Node, ArnoldNode):
    bl_label = "Standard"
    bl_icon = 'MATERIAL'

    AI_NAME = "standard"

    def init(self, context):
        # Diffuse
        sock = self.inputs.new("NodeSocketColor", "Diffuse", "Kd_color")
        sock.default_value = (1, 1, 1, 1)
        sock = self.inputs.new("NodeSocketFloat", "Weight", "Kd")
        sock.default_value = 0.7
        sock = self.inputs.new("NodeSocketFloat", "Roughness", "diffuse_roughness")
        sock.default_value = 0
        sock = self.inputs.new("NodeSocketFloat", "Backlight", "Kb")
        sock.default_value = 0
        sock = self.inputs.new("NodeSocketBool", "Fresnel", "Fresnel")
        sock.default_value = False
        # Specular
        sock = self.inputs.new("NodeSocketColor", "Specular", "Ks_color")
        sock.default_value = (1, 1, 1, 1)
        sock = self.inputs.new("NodeSocketFloat", "Weight", "Ks")
        sock.default_value = 0
        sock = self.inputs.new("NodeSocketFloat", "Roughness", "specular_roughness")
        sock.default_value = 0.466905
        sock = self.inputs.new("NodeSocketFloat", "Anisotropy", "specular_anisotropy")
        sock.default_value = 0.5
        sock = self.inputs.new("NodeSocketFloat", "Rotation", "specular_rotation")
        sock.default_value = 0
        sock = self.inputs.new("NodeSocketBool", "Fresnel", "specular_Fresnel")
        sock.default_value = False
        sock = self.inputs.new("NodeSocketFloat", "Reflectance at Normal", "Krn")
        sock.default_value = 0
        # Reflection
        sock = self.inputs.new("NodeSocketColor", "Reflection", "Kr_color")
        sock.default_value = (1, 1, 1, 1)
        sock = self.inputs.new("NodeSocketFloat", "Weight", "Kr")
        sock.default_value = 0
        sock = self.inputs.new("NodeSocketColor", "Exit Color", "reflection_exit_color")
        sock.default_value = (0, 0, 0, 1)
        sock = self.inputs.new("NodeSocketBool", "Exit Use Environment", "reflection_exit_use_environment")
        sock.default_value = False
        # Transparency (Refraction)
        sock = self.inputs.new("NodeSocketColor", "Transparency", "Kt_color")
        sock.default_value = (1, 1, 1, 1)
        sock = self.inputs.new("NodeSocketFloat", "Weight", "Kt")
        sock.default_value = 0
        sock = self.inputs.new("NodeSocketFloat", "IOR", "IOR")
        sock.default_value = 1
        sock = self.inputs.new("NodeSocketFloat", "Abbe", "dispersion_abbe")
        sock.default_value = 0
        sock = self.inputs.new("NodeSocketFloat", "Roughness", "refraction_roughness")
        sock.default_value = 0
        sock = self.inputs.new("NodeSocketColor", "Exit Color", "refraction_exit_color")
        sock.default_value = (0, 0, 0, 1)
        sock = self.inputs.new("NodeSocketBool", "Exit Use Environment", "refraction_exit_use_environment")
        sock.default_value = False
        sock = self.inputs.new("NodeSocketColor", "Transmittance", "transmittance")
        sock.default_value = (1, 1, 1, 1)

        self.outputs.new("NodeSocketShader", "RGB", "output")


@ArnoldRenderEngine.register_class
class ArnoldNodeUtility(bpy.types.Node, ArnoldNode):
    bl_label = "Utility"
    bl_icon = 'MATERIAL'

    AI_NAME = "utility"

    color_mode = bpy.props.EnumProperty(
        name="Color Mode",
        items=[
            ('color', "Color", "Single color output"),
            ('ng', "Geometric Normal", "Shader normals in world space."),
            ('ns', "Un-bumped Normal", "Smooth un-bumped normals in screen space."),
            ('n', "Normal", "Geometry normals in world space."),
            ('bary', "Barycentric Coords", "Barycentry coordinates (bu corresponds to red and bv to green) of the primitive."),
            ('uv', "UV Coords", "UV coordinates (u corresponds to red and v to green) of the primitive."),
            ('u', "U Coords", "U coordinate mapped to the red, green and blue channels."),
            ('v', "V Coords", "V coordinate mapped to the red, green and blue channels."),
            ('dpdu', "U Surface Derivative (dPdu)", "Surface derivative with respect to u coordinate."),
            ('dpdv', "V Surface Derivative (dPdv)", "Surface derivative with respect to v coordinate."),
            ('p', "Shading Point", "Shading point, relative to the Bounding Box."),
            ('prims', "Primitive ID", "Each primitive ID is represented as a different color."),
            ('uniformid', "Uniform ID", "Allows you to color by patch instad of by polygon and by curve instead of curve segments."),
            ('wire', "Triangle Wireframe", "Renders a triangulated wireframe of the mesh."),
            ('polywire', "Polygon Wireframe", "Renders a plygon wireframe of the mesh."),
            ('obj', "Object", "Object mode uses the name of the shapes to compute the color."),
            ('edgelength', "Edge Length", "Shows the edge length of the primitive as a heatmap."),
            ('floatgrid', "Floatgrid", "A color is mapped around a Hash function based on the Shading Point."),
            ('reflectline', "Reflection Lines", "Use to diagnose the contour lines of a mesh."),
            ('bad_uvs', "Bad UVs", "Returns magenta in the UV of the privitive that are degenerated."),
            ('nlights', "Number of lights", "Shows the relative number of lights considered at the shading point."),
            ('id', "Object ID", "Id mode uses the ID parameter shapes have in order to compute the color."),
            ('bumpdiff', "Bump Difference", "This mode shows how far the bump and autobump normals vary from the base smooth-shaded normals as a heatmap."),
            ('pixelerror', "Subdivision Pixel Error", "Shows as a heatmap mode, the edge lenth of the privitive based on how well the polygon matches the subdiv_pixel_error.")
        ],
        default='color'
    )
    shade_mode = bpy.props.EnumProperty(
        name="Shade Mode",
        items=[
            ('ndoteye', "Ndoteye", "Uses a dot product between the Normal and the Eye vector."),
            ('lambert', "Lambert", "Uses a Lambertian shading model."),
            ('flat', "Flat", "Renders the model as a pure, solid flatly lit and shaded color."),
            ('ambocc', "Ambocc", "Renders the model usgin an ambient occlusion technique."),
            ('plastic', "Plastic", "Has both diffuse (0.7) and specular (0.1) components.")
        ],
        default='ndoteye'
    )
    overlay_mode = bpy.props.EnumProperty(
        name="Overlay Mode",
        items=[
            ('none', "None", "None"),
            ('wire', "Wire", "Wire"),
            ('polywire', "Polywire", "Polywire")
        ],
        default='none'
    )

    def init(self, context):
        sock = self.inputs.new("NodeSocketColor", "Color", "color")
        sock.default_value = (1, 1, 1, 1)
        sock = self.inputs.new("NodeSocketFloat", "Opacity", "opacity")
        sock.default_value = 1
        sock = self.inputs.new("NodeSocketFloat", "AO Distance", "ao_distance")
        sock.default_value = 100

        self.outputs.new("NodeSocketShader", "RGB", "output")

    def draw_buttons(self, context, layout):
        layout.prop(self, "color_mode", text="")
        layout.prop(self, "shade_mode", text="")
        layout.prop(self, "overlay_mode", text="")

    @property
    def ai_properties(self):
        return {
            "color_mode": ('STRING', self.color_mode),
            "shade_mode": ('STRING', self.shade_mode),
            "overlay_mode": ('STRING', self.overlay_mode)
        }


@ArnoldRenderEngine.register_class
class ArnoldNodeFlat(bpy.types.Node, ArnoldNode):
    bl_label = "Flat"
    bl_icon = 'MATERIAL'

    AI_NAME = "flat"

    def init(self, context):
        sock = self.inputs.new("NodeSocketColor", "Color", "color")
        sock.default_value = (1, 1, 1, 1)
        sock = self.inputs.new("NodeSocketColor", "Opacity", "opacity")
        sock.default_value = (1, 1, 1, 1)

        self.outputs.new("NodeSocketShader", "RGB", "output")


@ArnoldRenderEngine.register_class
class ArnoldNodeImage(bpy.types.Node, ArnoldNode):
    bl_label = "Image"
    bl_icon = 'IMAGEFILE'

    AI_NAME = "image"

    texture = bpy.props.StringProperty(
        name="Texture"
    )

    def init(self, context):
        self.outputs.new("NodeSocketColor", "RGBA", "output")

    def draw_buttons(self, context, layout):
        layout.prop_search(self, "texture", context.blend_data, "textures", text="")

    @property
    def ai_properties(self):
        return {
            "filename": ('TEXTURE', self.texture)
        }


@ArnoldRenderEngine.register_class
class ArnoldNodeWireframe(bpy.types.Node, ArnoldNode):
    bl_label = "Wireframe"
    bl_icon = 'MATERIAL'

    AI_NAME = "wireframe"

    edge_type = bpy.props.EnumProperty(
        name="Edge Type",
        items=[
            ('polygons', "Polygons", "Polygons"),
            ('triangles', "Triangles", "Triangles")
        ],
        default='triangles'
    )

    def init(self, context):
        sock = self.inputs.new("NodeSocketFloat", "Line Width", "line_width")
        sock.default_value = 1
        sock = self.inputs.new("NodeSocketColor", "Fill Color", "fill_color")
        sock.default_value = (1, 1, 1, 1)
        sock = self.inputs.new("NodeSocketColor", "Line Color", "line_color")
        sock.default_value = (0, 0, 0, 1)
        sock = self.inputs.new("NodeSocketBool", "Raster space", "raster_space")
        sock.default_value = True

        self.outputs.new("NodeSocketShader", "RGB", "output")

    def draw_buttons(self, context, layout):
        layout.prop(self, "edge_type", text="")

    @property
    def ai_properties(self):
        return {
            "edge_type": ('STRING', self.edge_type)
        }


@ArnoldRenderEngine.register_class
class ArnoldNodeMixRGB(bpy.types.Node, ArnoldNode):
    bl_label = "Mix RGB"
    bl_icon = 'MATERIAL'

    AI_NAME = "BArnoldMixRGB"

    blend_type = bpy.props.EnumProperty(
        name="Blend Type",
        items=[
            ('mix', "Mix", "Mix"),
            ('add', "Add", "Add"),
            ('multiply', "Multiply", "Multiply"),
            ('screen', "Screen", "Screen"),
            ('overlay', "Overlay", "Overlay"),
            ('subtract', "Subtract", "Subtract"),
            ('divide', "Divide", "Divide"),
            ('difference', "Difference", "Difference"),
            ('darken', "Darken", "Darken Only"),
            ('lighten', "Lighten", "Lighten Only"),
            ('dodge', "Dodge", "Dodge"),
            ('burn', "Burn", "Burn"),
            ('hue', "Hue", "Hue"),
            ('saturation', "Saturation", "Saturation"),
            ('value', "Value", "Value"),
            ('color', "Color", "Color"),
            ('soft', "Soft Light", "Soft Light"),
            ('linear', "Linear Light", "Linear Light")
        ],
        default='mix'
    )

    def init(self, context):
        sock = self.inputs.new("NodeSocketColor", "Color1", "color1")
        sock.default_value = (0.8, 0.8, 0.8, 1)
        sock = self.inputs.new("NodeSocketColor", "Color2", "color2")
        sock.default_value = (0.8, 0.8, 0.8, 1)
        sock = self.inputs.new("NodeSocketFloat", "Factor", "factor")
        sock.default_value = 0.5

        self.outputs.new("NodeSocketColor", "Color", "output")

    def draw_buttons(self, context, layout):
        layout.prop(self, "blend_type", text="")

    @property
    def ai_properties(self):
        return {
            "blend": ('STRING', self.blend_type)
        }


class ArnoldNodeCategory(nodeitems_utils.NodeCategory):
    @classmethod
    def poll(cls, context):
        return (
            ArnoldRenderEngine.is_active(context) and
            context.space_data.tree_type == 'ShaderNodeTree'
        )


def register():
    from nodeitems_builtins import ShaderNewNodeCategory, ShaderOldNodeCategory

    # HACK: hide BI and Cycles nodes from 'Add' menu in Node editor
    def _poll(fn):
        @classmethod
        def _fn(cls, context):
            return (
                not ArnoldRenderEngine.is_active(context) and
                fn(context)
            )
        return _fn

    ShaderNewNodeCategory.poll = _poll(ShaderNewNodeCategory.poll)
    ShaderOldNodeCategory.poll = _poll(ShaderOldNodeCategory.poll)

    node_categories = [
        ArnoldNodeCategory("ARNOLD_OUTPUT_NODES", "Output", items=[
            nodeitems_utils.NodeItem("ArnoldNodeOutput")
        ]),
        ArnoldNodeCategory("ARNOLD_SHADERS_NODES", "Shaders", items=[
            nodeitems_utils.NodeItem("ArnoldNodeLambert"),
            nodeitems_utils.NodeItem("ArnoldNodeStandard"),
            nodeitems_utils.NodeItem("ArnoldNodeUtility"),
            nodeitems_utils.NodeItem("ArnoldNodeFlat"),
            nodeitems_utils.NodeItem("ArnoldNodeImage"),
            nodeitems_utils.NodeItem("ArnoldNodeWireframe"),
        ]),
        ArnoldNodeCategory("ARNOLD_COLOR_NODES", "Color", items=[
            nodeitems_utils.NodeItem("ArnoldNodeMixRGB")
        ]),
    ]
    nodeitems_utils.register_node_categories("ARNOLD_NODES", node_categories)


def unregister():
    nodeitems_utils.unregister_node_categories("ARNOLD_NODES")