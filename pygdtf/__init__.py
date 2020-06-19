from typing import List
from xml.etree import ElementTree
from xml.etree.ElementTree import Element
import zipfile
import pygdtf.type


# Standard predefined colour spaces: R, G, B, W-P
COLOR_SPACE_SRGB = pygdtf.type.ColorSpaceDefinition(
    pygdtf.type.ColorCIE(0.6400, 0.3300, 0.2126), pygdtf.type.ColorCIE(0.3000, 0.6000, 0.7152),
    pygdtf.type.ColorCIE(0.1500, 0.0600, 0.0722), pygdtf.type.ColorCIE(0.3127, 0.3290, 1.0000))
COLOR_SPACE_PROPHOTO = pygdtf.type.ColorSpaceDefinition(
    pygdtf.type.ColorCIE(0.7347, 0.2653), pygdtf.type.ColorCIE(0.1596, 0.8404),
    pygdtf.type.ColorCIE(0.0366, 0.0001), pygdtf.type.ColorCIE(0.3457, 0.3585))
COLOR_SPACE_ANSI = pygdtf.type.ColorSpaceDefinition(
    pygdtf.type.ColorCIE(0.7347, 0.2653), pygdtf.type.ColorCIE(0.1596, 0.8404),
    pygdtf.type.ColorCIE(0.0366, 0.001), pygdtf.type.ColorCIE(0.4254, 0.4044))


def _find_root(pkg: 'zipfile.ZipFile') -> 'ElementTree.Element':
    """Given a GDTF zip archive, find the FixtureType of the corresponding
    description.xml file. The root element of a GDTF description file is
    actually a GDTF node, however as the GDTF node only ever has one child, a
    FixtureType node, and the library functions have no use for the GDTF
    node, we simply return the FixtureType node here."""

    with pkg.open('description.xml', 'r') as f:
        description_str = f.read()
    return ElementTree.fromstring(description_str).find('FixtureType')


class FixtureType:

    def __init__(self, path=None):
        self._package = None
        self._root = None
        if path is not None:
            self._package = zipfile.ZipFile(path, 'r')
        if self._package is not None:
            self._root = _find_root(self._package)
        if self._root is not None:
            self._read_xml()

    def _read_xml(self):
        self.name = self._root.get('Name')
        self.short_name = self._root.get('ShortName')
        self.long_name = self._root.get('LongName')
        self.manufacturer = self._root.get('Manufacturer')
        self.description = self._root.get('Description')
        self.fixture_type_id = self._root.get('FixtureTypeID')
        self.thumbnail = self._root.get('Thumbnail')
        self.ref_ft = self._root.get('RefFT')
        xactivation_groups = self._root.find('AttributeDefinitions').find('ActivationGroups').findall('ActivationGroup')
        self.activation_groups = [ActivationGroup(xml_node=i) for i in xactivation_groups]
        xfeature_groups = self._root.find('AttributeDefinitions').find('FeatureGroups').findall('FeatureGroup')
        self.feature_groups = [FeatureGroup(xml_node=i) for i in xfeature_groups]
        xattributes = self._root.find('AttributeDefinitions').find('Attributes').findall('Attribute')
        self.attributes = [Attribute(xml_node=i) for i in xattributes]
        xwheels = self._root.find('Wheels').findall('Wheel')
        self.wheels = [Wheel(xml_node=i) for i in xwheels]
        xemitters = self._root.find('PhysicalDescriptions').find('Emitters').findall('Emitter')
        self.emitters = [Emitter(xml_node=i) for i in xemitters]
        xfilters = self._root.find('PhysicalDescriptions').find('Filters').findall('Filter')
        self.filters = [Filter(xml_node=i) for i in xfilters]
        self.color_space = self._root.find('PhysicalDescriptions').find('ColorSpace')
        xdmx_profiles = self._root.find('PhysicalDescriptions').find('DMXProfiles').findall('DMXProfile')
        self.dmx_profiles = [DmxProfile(xml_node=i) for i in xdmx_profiles]
        xcri_groups = self._root.find('PhysicalDescriptions').find('CRIs').findall('CRIGroup')
        self.cri_groups = [CriGroup(xml_node=i) for i in xcri_groups]
        xmodels = self._root.find('Models').findall('Model')
        self.models = [Model(xml_node=i) for i in xmodels]
        xgeometry_collect = self._root.find('Geometries')
        self.geometries = []
        for i in xgeometry_collect.findall('Geometry'):
            self.geometries.append(Geometry(xml_node=i))
        for i in xgeometry_collect.findall('Axis'):
            self.geometries.append(GeometryAxis(xml_node=i))
        for i in xgeometry_collect.findall('FilterBeam'):
            self.geometries.append(GeometryFilterBeam(xml_node=i))
        for i in xgeometry_collect.findall('FilterColor'):
            self.geometries.append(GeometryFilterColor(xml_node=i))
        for i in xgeometry_collect.findall('FilterGobo'):
            self.geometries.append(GeometryFilterGobo(xml_node=i))
        for i in xgeometry_collect.findall('FilterShaper'):
            self.geometries.append(GeometryFilterShaper(xml_node=i))
        for i in xgeometry_collect.findall('Beam'):
            self.geometries.append(GeometryBeam(xml_node=i))
        for i in xgeometry_collect.findall('GeometryReference'):
            self.geometries.append(GeometryReference(xml_node=i))
        xdmx_modes = self._root.find('DMXModes').findall('DMXMode')
        self.dmx_modes = [DmxMode(xml_node=i) for i in xdmx_modes]
        xrevisions = self._root.find('Revisions').findall('Revision')
        self.revisions = [Revision(xml_node=i) for i in xrevisions]

    def get_geometry_by_type(self, geometry_type):
        """Recursively find all geometries of a given type"""
        def iterate_geometries(collector):
            for g in collector.geometries:
                if g.geometry_type == geometry_type:
                    matched.append(g)
                iterate_geometries(g)
        matched = []
        iterate_geometries(self)
        return matched


class BaseNode:

    def __init__(self, xml_node: 'Element' = None):
        if xml_node is not None:
            self._read_xml(xml_node)

    def _read_xml(self, xml_node: 'Element'):
        pass


class ActivationGroup(BaseNode):

    def __init__(self, name: str = None, *args, **kwargs):
        self.name = name
        super().__init__(*args, **kwargs)

    def _read_xml(self, xml_node: 'Element'):
        self.name = xml_node.get('Name')


class FeatureGroup(BaseNode):

    def __init__(self, name: str = None, pretty: str = None,
                 features: List['Feature'] = None, *args, **kwargs):
        self.name = name
        self.pretty = pretty
        if features is not None:
            self.features = features
        else:
            self.features = []
        super().__init__(*args, **kwargs)

    def _read_xml(self, xml_node: 'Element'):
        self.name = xml_node.get('Name')
        self.pretty = xml_node.get('Pretty')
        self.features = [Feature(xml_node=i) for i in xml_node.findall('Feature')]


class Feature(BaseNode):

    def __init__(self, name: str = None, *args, **kwargs):
        self.name = name
        super().__init__(*args, **kwargs)

    def _read_xml(self, xml_node: 'Element'):
        self.name = xml_node.get('Name')


class Attribute(BaseNode):

    def __init__(self, name: str = None, pretty: str = None,
                 activation_group: 'NodeLink' = None, feature: 'NodeLink' = None,
                 main_attribute: 'NodeLink' = None, physical_unit: 'PhysicalUnit' = pygdtf.type.PhysicalUnit(None),
                 color: 'ColorCIE' = None, *args, **kwargs):
        self.name = name
        self.pretty = pretty
        self.activation_group = activation_group
        self.feature = feature
        self.main_attribute = main_attribute
        self.physical_unit = physical_unit
        self.color = color
        super().__init__(*args, **kwargs)

    def _read_xml(self, xml_node: 'Element'):
        self.name = xml_node.get('Name')
        self.pretty = xml_node.get('Pretty')
        self.activation_group = pygdtf.type.NodeLink('ActivationGroups', xml_node.get('ActivationGroup'))
        self.feature = pygdtf.type.NodeLink('FeatureGroups', xml_node.get('Feature'))
        self.main_attribute = pygdtf.type.NodeLink('Attribute', xml_node.get('MainAttribute'))
        self.physical_unit = pygdtf.type.PhysicalUnit(xml_node.get('PhysicalUnit'))
        self.color = pygdtf.type.ColorCIE(str_repr=xml_node.get('Color'))


class Wheel(BaseNode):

    def __init__(self, name: str = None, wheel_slots: List['WheelSlot'] = None, *args, **kwargs):
        self.name = name
        if wheel_slots is not None:
            self.wheel_slots = wheel_slots
        else:
            self.wheel_slots = []
        super().__init__(*args, **kwargs)

    def _read_xml(self, xml_node: 'Element'):
        self.name = xml_node.get('Name')
        self.wheel_slots = [WheelSlot(xml_node=i) for i in xml_node.findall('Slot')]


class WheelSlot(BaseNode):

    def __init__(self, name: str = None, color: 'ColorCIE' = None,
                 filter: 'NodeLink' = None, media_file_name: 'Resource' = None,
                 facets: List['PrismFacet'] = None, *args, **kwargs):
        self.name = name
        self.color = color
        self.filter = filter
        self.media_file_name = media_file_name
        if facets is not None:
            self.facets = facets
        else:
            self.facets = []
        super().__init__(*args, **kwargs)

    def _read_xml(self, xml_node: 'Element'):
        self.name = xml_node.get('Name')
        self.color = pygdtf.type.ColorCIE(str_repr=xml_node.get('Color'))
        self.filter = pygdtf.type.NodeLink('FilterCollect', xml_node.get('Filter'))
        self.media_file_name = pygdtf.type.Resource(xml_node.get('MediaFileName'), 'png')
        self.facets = [PrismFacet(xml_node=i) for i in xml_node.findall('Facet')]


class PrismFacet(BaseNode):

    def __init__(self, color: 'ColorCIE' = None, rotation: 'Rotation' = None, *args, **kwargs):
        self.color = color
        self.rotation = rotation
        super().__init__(*args, **kwargs)

    def _read_xml(self, xml_node: 'Element'):
        self.color = pygdtf.type.ColorCIE(str_repr=xml_node.get('Color'))
        self.rotation = pygdtf.type.Rotation(str_repr=xml_node.get('Rotation'))


class Emitter(BaseNode):

    def __init__(self, name: str = None, color: 'ColorCIE' = None,
                 dominant_wave_length: float = None, diode_part: str = None, *args, **kwargs):
        self.name = name
        self.color = color
        self.dominant_wave_length = dominant_wave_length
        self.diode_part = diode_part
        super().__init__(*args, **kwargs)

    def _read_xml(self, xml_node: 'Element'):
        self.name = xml_node.get('Name')
        self.color = pygdtf.type.ColorCIE(str_repr=xml_node.get('Color'))
        try:
            self.dominant_wave_length = float(xml_node.get('DominantWaveLength'))
        except TypeError:
            self.dominant_wave_length = None
        self.diode_part = xml_node.get('DiodePart')
        self.measurements = [Measurement(xml_node=i) for i in xml_node.findall('Measurement')]


class Filter(BaseNode):

    def __init__(self, name: str = None, color: 'ColorCIE' = None,
                 measurements: List['Measurement'] = None, *args, **kwargs):
        self.name = name
        self.color = color
        if measurements is not None:
            self.measurements = measurements
        else:
            self.measurements = []
        super().__init__(*args, **kwargs)

    def _read_xml(self, xml_node: 'Element'):
        self.name = xml_node.get('Name')
        self.color = pygdtf.type.ColorCIE(str_repr=xml_node.get('Color'))
        self.measurements = [Measurement(xml_node=i) for i in xml_node.findall('Measurement')]


class Measurement(BaseNode):

    def __init__(self, physical: float = None, luminous_intensity: float = None,
                 transmission: float = None, interpolation_to: 'InterpolationTo' = pygdtf.type.InterpolationTo(None),
                 *args, **kwargs):
        self.physical = physical
        self.luminous_intensity = luminous_intensity
        self.transmission = transmission
        self.interpolation_to = interpolation_to
        super().__init__(*args, **kwargs)

    def _read_xml(self, xml_node: 'Element'):
        self.physical = float(xml_node.get('Physical'))
        try:
            self.luminous_intensity = float(xml_node.get('LuminousIntensity'))
        except TypeError:
            self.luminous_intensity = None
        try:
            self.transmission = float(xml_node.get('Transmission'))
        except TypeError:
            self.transmission = None
        self.interpolation_to = pygdtf.type.InterpolationTo(xml_node.get('InterpolationTo'))
        self.measurement_points = [MeasurementPoint(xml_node=i) for i in xml_node.findall('MeasurementPoint')]


class MeasurementPoint(BaseNode):

    def __init__(self, wave_length: float = None, energy: float = None, *args, **kwargs):
        self.wave_length = wave_length
        self.energy = energy
        super().__init__(*args, **kwargs)

    def _read_xml(self, xml_node: 'Element'):
        self.wave_length = float(xml_node.get('WaveLength'))
        self.energy = float(xml_node.get('Energy'))


class ColorSpace(BaseNode):

    def __init__(self, mode: 'ColorSpaceMode' = pygdtf.type.ColorSpaceMode(None),
                 definition: 'ColorSpaceDefinition' = None, *args, **kwargs):
        self.mode = mode
        if definition is not None:
            self.definition = definition
        else:
            self._match_definition()
        super().__init__(*args, **kwargs)

    def _read_xml(self, xml_node: 'Element'):
        self.mode = pygdtf.type.ColorSpaceMode(xml_node.get('Mode'))
        if str(self.mode) == 'Custom':
            self.red = pygdtf.type.ColorCIE(str_repr=xml_node.get('Red'))
            self.green = pygdtf.type.ColorCIE(str_repr=xml_node.get('Green'))
            self.blue = pygdtf.type.ColorCIE(str_repr=xml_node.get('Blue'))
            self.white_point = pygdtf.type.ColorCIE(str_repr=xml_node.get('WhitePoint'))
        else:
            self._match_definition()

    def _match_definition(self):
        # Match the name of the color space mode with a color space definition,
        # this will only work for sRGB, ProPhoto and ANSI modes
        if self.mode is None or str(self.mode) == 'Custom':
            return
        elif str(self.mode) == 'sRGB':
            self.definition = COLOR_SPACE_SRGB
        elif str(self.mode) == 'ProPhoto':
            self.definition = COLOR_SPACE_PROPHOTO
        elif str(self.mode) == 'ANSI':
            self.definition = COLOR_SPACE_ANSI


class DmxProfile(BaseNode):
    pass


class CriGroup(BaseNode):

    def __init__(self, color_temperature: float = 6000, cris: List['Cri'] = None, *args, **kwargs):
        self.color_temperature = color_temperature
        if cris is not None:
            self.cris = cris
        else:
            self.cris = []
        super().__init__(*args, **kwargs)

    def _read_xml(self, xml_node: 'Element'):
        self.color_temperature = float(xml_node.get('ColorTemperature', default=6000))
        self.cris = [Cri(xml_node=i) for i in xml_node.findall('CRI')]


class Cri(BaseNode):

    def __init__(self, ces: 'Ces' = pygdtf.type.Ces(None), color_temperature: int = 100, *args, **kwargs):
        self.ces = ces
        self.color_temperature = color_temperature
        super().__init__(*args, **kwargs)

    def _read_xml(self, xml_node: 'Element'):
        self.ces = pygdtf.type.Ces(xml_node.get('CES'))
        self.color_temperature = int(xml_node.get('ColorTemperature', default=100))


class Model(BaseNode):

    def __init__(self, name: str = None, length: float = 0, width: float = 0,
                 height: float = 0, primitive_type: 'PrimitiveType' = pygdtf.type.PrimitiveType(None),
                 file: pygdtf.type.Resource = None, *args, **kwargs):
        self.name = name
        self.length = length
        self.width = width
        self.height = height
        self.primitive_type = primitive_type
        self.file = file
        super().__init__(*args, **kwargs)

    def _read_xml(self, xml_node: 'Element'):
        self.name = xml_node.get('Name')
        self.length = float(xml_node.get('Length', default=0))
        self.width = float(xml_node.get('Width', default=0))
        self.height = float(xml_node.get('Height', default=0))
        self.primitive_type = pygdtf.type.PrimitiveType(xml_node.get('PrimitiveType'))
        self.file = pygdtf.type.Resource(xml_node.get('File'))


class Geometry(BaseNode):

    def __init__(self, name: str = None, model: str = None,
                 position: 'Matrix' = pygdtf.type.Matrix(0), geometries: List = None, *args, **kwargs):
        self.name = name
        self.model = model
        self.position = position
        if geometries is not None:
            self.geometries = geometries
        else:
            self.geometries = []
        super().__init__(*args, **kwargs)

    def _read_xml(self, xml_node: 'Element'):
        self.name = xml_node.get('Name')
        self.model = xml_node.get('Model')
        self.position = pygdtf.type.Matrix(xml_node.get('Position', default=0))
        for i in xml_node.findall('Geometry'):
            self.geometries.append(Geometry(xml_node=i))
        for i in xml_node.findall('Axis'):
            self.geometries.append(GeometryAxis(xml_node=i))
        for i in xml_node.findall('FilterBeam'):
            self.geometries.append(GeometryFilterBeam(xml_node=i))
        for i in xml_node.findall('FilterColor'):
            self.geometries.append(GeometryFilterColor(xml_node=i))
        for i in xml_node.findall('FilterGobo'):
            self.geometries.append(GeometryFilterGobo(xml_node=i))
        for i in xml_node.findall('FilterShaper'):
            self.geometries.append(GeometryFilterShaper(xml_node=i))
        for i in xml_node.findall('Beam'):
            self.geometries.append(GeometryBeam(xml_node=i))
        for i in xml_node.findall('GeometryReference'):
            self.geometries.append(GeometryReference(xml_node=i))


class GeometryAxis(Geometry):
    pass


class GeometryFilterBeam(Geometry):
    pass


class GeometryFilterColor(Geometry):
    pass


class GeometryFilterGobo(Geometry):
    pass


class GeometryFilterShaper(Geometry):
    pass


class GeometryBeam(Geometry):

    def __init__(self, lamp_type: 'LampType' = pygdtf.type.LampType(None), power_consumption: float = 1000,
                 luminous_flux: float = 10000, color_temperature: float = 6000,
                 beam_angle: float = 25.0, field_angle: float = 25.0,
                 beam_radius: float = 0.05, beam_type: pygdtf.type.BeamType = pygdtf.type.BeamType(None),
                 color_rendering_index: int = 100, *args, **kwargs):
        self.lamp_type = lamp_type
        self.power_consumption = power_consumption
        self.luminous_flux = luminous_flux
        self.color_temperature = color_temperature
        self.beam_angle = beam_angle
        self.field_angle = field_angle
        self.beam_radius = beam_radius
        self.beam_type = beam_type
        self.color_rendering_index = color_rendering_index
        super().__init__(*args, **kwargs)

    def _read_xml(self, xml_node: 'Element'):
        super()._read_xml(xml_node)
        self.lamp_type = pygdtf.type.LampType(xml_node.get('LampType'))
        self.power_consumption = float(xml_node.get('PowerConsumption', default=1000))
        self.luminous_flux = float(xml_node.get('LuminousFlux', default=10000))
        self.color_temperature = float(xml_node.get('ColorTemperature', default=6000))
        self.beam_angle = float(xml_node.get('BeamAngle', default=25))
        self.field_angle = float(xml_node.get('FieldAngle', default=25))
        self.beam_radius = float(xml_node.get('BeamRadius', default=0.05))
        self.beam_type = pygdtf.type.BeamType(xml_node.get('BeamType'))
        self.color_rendering_index = int(xml_node.get('ColorRenderingIndex', default=100))


class GeometryReference(BaseNode):

    def __init__(self, name: str = None, position: 'Matrix' = pygdtf.type.Matrix(0),
                 geometry: str = None, model: str = None, *args, **kwargs):
        self.name = name
        self.position = position
        self.geometry = geometry
        self.model = model
        super().__init__(*args, **kwargs)

    def _read_xml(self, xml_node: 'Element'):
        self.name = xml_node.get('Name')
        self.position = pygdtf.type.Matrix(xml_node.get('Position', default=0))
        self.geometry = xml_node.get('Geometry')
        self.model = xml_node.get('Model')
        self.breaks = [Break(xml_node=i) for i in xml_node.findall('Break')]


class Break(BaseNode):

    def __init__(self, dmx_offset: 'DmxAddress' = pygdtf.type.DmxAddress('1'),
                 dmx_break: int = 1, *args, **kwargs):
        self.dmx_offset = dmx_offset
        self.dmx_break = dmx_break
        super().__init__(*args, **kwargs)

    def _read_xml(self, xml_node: 'Element'):
        self.dmx_offset = pygdtf.type.DmxAddress(xml_node.get('DMXOffset'))
        self.dmx_break = int(xml_node.get('DMXBreak', default=1))


class DmxMode(BaseNode):

    def __init__(self, name: str = None, geometry: str = None,
                 dmx_channels: List['DmxChannel'] = None,
                 relations: List['Relation'] = None, ft_macros: List['Macro'] = None,
                 *args, **kwargs):
        self.name = name
        self.geometry = geometry
        if dmx_channels is not None:
            self.dmx_channels = dmx_channels
        else:
            self.dmx_channels = []
        if relations is not None:
            self.relations = relations
        else:
            self.relations = []
        if ft_macros is not None:
            self.ft_macros = ft_macros
        else:
            self.ft_macros = []
        super().__init__(*args, **kwargs)

    def _read_xml(self, xml_node: 'Element'):
        self.name = xml_node.get('Name')
        self.geometry = xml_node.get('Geometry')
        self.dmx_channels = [DmxChannel(xml_node=i) for i in xml_node.find('DMXChannels').findall('DMXChannel')]
        self.relations = [Relation(xml_node=i) for i in xml_node.find('Relations').findall('Relation')]
        try:
            self.ft_macros = [Macro(xml_node=i) for i in xml_node.find('FTMacros').findall('FTMacro')]
        except AttributeError:
            pass


class DmxChannel(BaseNode):

    def __init__(self, dmx_break: int = 1, offset: List[int] = 'None',
                 default: 'DmxValue' = pygdtf.type.DmxValue('0/1'), highlight: 'DmxValue' = 'None',
                 geometry: str = None,
                 logical_channels: List['LogicalChannel'] = None, *args, **kwargs):
        self.dmx_break = dmx_break
        self.offset = offset
        self.default = default
        self.highlight = highlight
        self.geometry = geometry
        self.logical_channels = logical_channels
        super().__init__(*args, **kwargs)

    def _read_xml(self, xml_node: 'Element'):
        try:
            self.dmx_break = int(xml_node.get('DMXBreak'))
        except ValueError:
            self.dmx_break = 'Overwrite'
        try:
            self.offset = [int(i) for i in xml_node.get('Offset').split(',')]
        except ValueError:
            self.offset = 'None'
        self.default = pygdtf.type.DmxValue(xml_node.get('Default', default='0/1'))
        self.highlight = pygdtf.type.DmxValue(xml_node.get('Highlight'))
        self.geometry = xml_node.get('Geometry')
        self.logical_channels = [LogicalChannel(xml_node=i) for i in xml_node.findall('LogicalChannel')]


class LogicalChannel(BaseNode):

    def __init__(self, attribute: 'NodeLink' = None, snap: 'Snap' = pygdtf.type.Snap(None),
                 master: 'Master' = pygdtf.type.Master(None), mib_fade: float = 0,
                 dmx_change_time_limit: float = 0,
                 channel_functions: List['ChannelFunction'] = None, *args, **kwargs):
        self.attribute = attribute
        self.snap = snap
        self.master = master
        self.mib_fade = mib_fade
        self.dmx_change_time_limit = dmx_change_time_limit
        if channel_functions is not None:
            self.channel_functions = channel_functions
        else:
            self.channel_functions = []
        super().__init__(*args, **kwargs)

    def _read_xml(self, xml_node: 'Element'):
        self.attribute = pygdtf.type.NodeLink('Attributes', xml_node.get('Attribute'))
        self.snap = pygdtf.type.Snap(xml_node.get('Snap'))
        self.master = pygdtf.type.Master(xml_node.get('Master'))
        self.mib_fade = float(xml_node.get('MibFade', default=0))
        self.dmx_change_time_limit = float(xml_node.get('DMXChangeTimeLimit', default=0))
        self.channel_functions = [ChannelFunction(xml_node=i) for i in xml_node.findall('ChannelFunction')]


class ChannelFunction(BaseNode):

    def __init__(self, name: str = None, attribute: 'NodeLink' = 'NoFeature',
                 original_attribute: str = None, dmx_from: 'DmxValue' = pygdtf.type.DmxValue('0/1'),
                 physical_from: float = 0, physical_to: float = 1, real_fade: float = 0,
                 wheel: 'NodeLink' = None, emitter: 'NodeLink' = None, filter: 'NodeLink' = None,
                 dmx_invert: 'DmxInvert' = pygdtf.type.DmxInvert(None), mode_master: 'NodeLink' = None,
                 mode_from: 'DmxValue' = pygdtf.type.DmxValue('0/1'), mode_to: 'DmxValue' = pygdtf.type.DmxValue('0/1'),
                 channel_sets: List['ChannelSet'] = None, *args, **kwargs):
        self.name = name
        self.attribute = attribute
        self.original_attribute = original_attribute
        self.dmx_from = dmx_from
        self.physical_from = physical_from
        self.physical_to = physical_to
        self.real_fade = real_fade
        self.wheel = wheel
        self.emitter = emitter
        self.filter = filter
        self.dmx_invert = dmx_invert
        self.mode_master = mode_master
        self.mode_from = mode_from
        self.mode_to = mode_to
        if channel_sets is not None:
            self.channel_sets = channel_sets
        else:
            self.channel_sets = []
        super().__init__(*args, **kwargs)

    def _read_xml(self, xml_node: 'Element'):
        self.name = xml_node.get('Name')
        self.attribute = pygdtf.type.NodeLink('Attributes', xml_node.get('Attribute', default='NoFeature'))
        self.original_attribute = xml_node.get('OriginalAttribute')
        self.dmx_from = pygdtf.type.DmxValue(xml_node.get('DMXFrom', default='0/1'))
        self.physical_from = float(xml_node.get('PhysicalFrom', default=0))
        self.physical_to = float(xml_node.get('PhysicalTo', default=1))
        self.real_fade = float(xml_node.get('RealFade', default=0))
        self.wheel = pygdtf.type.NodeLink('WheelCollect', xml_node.get('Wheel'))
        self.emitter = pygdtf.type.NodeLink('EmitterCollect', xml_node.get('Emitter'))
        self.filter = pygdtf.type.NodeLink('FilterCollect', xml_node.get('Filter'))
        self.dmx_invert = pygdtf.type.DmxInvert(xml_node.get('DMXInvert'))
        self.mode_master = pygdtf.type.Master(xml_node.get('ModeMaster'))
        self.mode_from = pygdtf.type.DmxValue(xml_node.get('ModeFrom', default='0/1'))
        self.mode_to = pygdtf.type.DmxValue(xml_node.get('ModeTo', default='0/1'))
        self.channel_sets = [ChannelSet(xml_node=i) for i in xml_node.findall('ChannelSet')]


class ChannelSet(BaseNode):

    def __init__(self, name: str = None, dmx_from: 'DmxValue' = pygdtf.type.DmxValue('0/1'),
                 physical_from: float = 0, physical_to: float = 1,
                 wheel_slot_index: int = 1, *args, **kwargs):
        self.name = name
        self.dmx_from = dmx_from
        self.physical_from = physical_from
        self.physical_to = physical_to
        self.wheel_slot_index = wheel_slot_index
        super().__init__(*args, **kwargs)

    def _read_xml(self, xml_node: 'Element'):
        self.name = xml_node.get('Name')
        self.dmx_from = pygdtf.type.DmxValue(xml_node.get('DMXFrom', default='0/1'))
        self.physical_from = float(xml_node.get('PhysicalFrom', default=0))
        self.physical_to = float(xml_node.get('PhysicalTo', default=1))
        self.wheel_slot_index = int(xml_node.get('WheelSlotIndex', default=1))


class Relation(BaseNode):

    def __init__(self, name: str = None, master: 'NodeLink' = None,
                 follower: 'NodeLink' = None, type: 'RelationType' = pygdtf.type.RelationType(None),
                 *args, **kwargs):
        self.name = name
        self.master = master
        self.follower = follower
        self.type = type
        super().__init__(*args, **kwargs)

    def _read_xml(self, xml_node: 'Element'):
        self.name = xml_node.get('Name')
        self.master = pygdtf.type.NodeLink('DMXMode', xml_node.get('Master'))
        self.follower = pygdtf.type.NodeLink('DMXMode', xml_node.get('Follower'))
        self.type = pygdtf.type.RelationType(xml_node.get('Type'))


class Macro(BaseNode):

    def __init__(self, name: str = None, dmx_steps: List['MacroDmxStep'] = None,
                 visual_steps: List['MacroVisualStep'] = None, *args, **kwargs):
        self.name = name
        if dmx_steps is not None:
            self.dmx_steps = dmx_steps
        else:
            self.dmx_steps = []
        if visual_steps is not None:
            self.visual_steps = visual_steps
        super().__init__(*args, **kwargs)

    def _read_xml(self, xml_node: 'Element'):
        self.name = xml_node.get('Name')
        try:
            self.dmx_steps = [MacroDmxStep(xml_node=i) for i in xml_node.find('MacroDMX').findall('MacroDMXStep')]
        except AttributeError:
            pass
        try:
            self.visual_steps = [MacroVisualStep(xml_node=i) for i in xml_node.find('MacroVisual').findall('MacroVisualStep')]
        except AttributeError:
            pass


class MacroDmxStep(BaseNode):

    def __init__(self, duration: int = 1, dmx_values: List['MacroDmxValue'] = None,
                 *args, **kwargs):
        self.duration = duration
        if dmx_values is not None:
            self.dmx_values = dmx_values
        else:
            self.dmx_values = []
        super().__init__(*args, **kwargs)

    def _read_xml(self, xml_node: 'Element'):
        self.duration = int(xml_node.get('Duration'))
        self.dmx_values = [MacroDmxValue(xml_node=i) for i in xml_node.findall('MacroDMXValue')]


class MacroDmxValue(BaseNode):

    def __init__(self, value: 'DmxValue' = None, dmx_channel: 'NodeLink' = None, *args, **kwargs):
        self.value = value
        self.dmx_channel = dmx_channel
        super().__init__(*args, **kwargs)

    def _read_xml(self, xml_node: 'Element'):
        self.value = pygdtf.type.DmxValue(xml_node.get('Value'))
        self.dmx_channel = pygdtf.type.NodeLink('DMXChannelCollect', xml_node.get('DMXChannel'))


class MacroVisualStep(BaseNode):

    def __init__(self, duration: int = 1, fade: float = 0.0, delay: float = 0.0,
                 visual_values: List['MacroVisualValue'] = None, *args, **kwargs):
        self.duration = duration
        self.fade = fade
        self.delay = delay
        if visual_values is not None:
            self.visual_values = visual_values
        else:
            self.visual_values = []
        super().__init__(*args, **kwargs)

    def _read_xml(self, xml_node: 'Element'):
        self.duration = int(xml_node.get('Duration', default=1))
        self.fade = float(xml_node.get('Fade', default=0.0))
        self.delay = float(xml_node.get('Delay', default=0.0))
        self.visual_values = [MacroVisualValue(xml_node=i) for i in xml_node.findall('MacroVisualValue')]


class MacroVisualValue(BaseNode):

    def __init__(self, value: 'DmxValue' = None, channel_function: 'NodeLink' = None, *args, **kwargs):
        self.value = value
        self.channel_function = channel_function
        super().__init__(*args, **kwargs)

    def _read_xml(self, xml_node: 'Element'):
        self.value = pygdtf.type.DmxValue(xml_node.get('Value'))
        self.channel_function = pygdtf.type.NodeLink('DMXChannelCollect', xml_node.get('ChannelFunction'))


class Revision(BaseNode):

    def __init__(self, text: str = None, date: str = None, user_id: int = 0, *args, **kwargs):
        self.text = text
        self.date = date
        self.user_id = user_id
        super().__init__(*args, **kwargs)

    def _read_xml(self, xml_node: 'Element'):
        self.text = xml_node.get('Text')
        self.date = xml_node.get('Date')
        self.user_id = int(xml_node.get('UserID'))
