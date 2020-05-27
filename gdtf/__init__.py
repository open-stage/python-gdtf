from xml.etree import ElementTree


class DmxAddress:

    def __init__(self, str_repr):
        if '.' in str_repr:
            self.universe = int(str_repr.split('.')[0])
            self.address = int(str_repr.split('.')[1])
        else:
            self.universe = 1
            self.address = int(str_repr)


class DmxValue:

    def __init__(self, str_repr):
        if str_repr == 'None':
            self.value = None
            self.byte_count = None
        else:
            self.value = int(str_repr.split('/')[0])
            self.byte_count = int(str_repr.split('/')[1])


class ColorCIE:

    def __init__(self, str_repr):
        self.x = float(str_repr.split(',')[0])
        self.y = float(str_repr.split(',')[1])
        self.Y = float(str_repr.split(',')[2])


class Rotation:

    def __init__(self, str_repr):
        str_repr = str_repr.replace('}{', ',')
        str_repr = str_repr.replace('{', '')
        str_repr = str_repr.replace('}', '')
        component = str_repr.split(',')
        component = [float(i) for i in component]
        self.matrix = [[component[0], component[1], component[2]],
                       [component[3], component[4], component[5]],
                       [component[6], component[7], component[8]]]


class Matrix:
    def __init__(self, str_repr):
        if str_repr == '0':
            self.matrix = [[1, 0, 0, 0],
                           [0, 1, 0, 0],
                           [0, 0, 1, 0],
                           [0, 0, 0, 1]]
        else:
            str_repr = str_repr.replace('}{', ',')
            str_repr = str_repr.replace('{', '')
            str_repr = str_repr.replace('}', '')
            component = str_repr.split(',')
            component = [float(i) for i in component]
            self.matrix = [[component[0], component[1], component[2], component[3]],
                           [component[4], component[5], component[6], component[7]],
                           [component[8], component[9], component[10], component[11]],
                           [component[12], component[13], component[14], component[15]]]


class FixtureType:

    def __init__(self, path):
        self._root = ElementTree.parse(path).getroot().find('FixtureType')
        self.name = self._root.get('Name')
        self.short_name = self._root.get('ShortName')
        self.long_name = self._root.get('LongName')
        self.manufacturer = self._root.get('Manufacturer')
        self.description = self._root.get('Description')
        self.fixture_type_id = self._root.get('FixtureTypeID')
        self.thumbnail = self._root.get('Thumbnail')
        self.ref_ft = self._root.get('RefFT')
        xactivation_groups = self._root.find('AttributeDefinitions').find('ActivationGroups').findall('ActivationGroup')
        self.activation_groups = [ActivationGroup(i) for i in xactivation_groups]
        xfeature_groups = self._root.find('AttributeDefinitions').find('FeatureGroups').findall('FeatureGroup')
        self.feature_groups = [FeatureGroup(i) for i in xfeature_groups]
        xattributes = self._root.find('AttributeDefinitions').find('Attributes').findall('Attribute')
        self.attributes = [Attribute(i) for i in xattributes]
        xwheels = self._root.find('Wheels').findall('Wheel')
        self.wheels = [Wheel(i) for i in xwheels]
        xemitters = self._root.find('PhysicalDescriptions').find('Emitters').findall('Emitter')
        self.emitters = [Emitter(i) for i in xemitters]
        xfilters = self._root.find('PhysicalDescriptions').find('Filters').findall('Filter')
        self.filters = [Filter(i) for i in xfilters]
        self.color_space = self._root.find('PhysicalDescriptions').find('ColorSpace')
        xdmx_profiles = self._root.find('PhysicalDescriptions').find('DMXProfiles').findall('DMXProfile')
        self.dmx_profiles = [DmxProfile(i) for i in xdmx_profiles]
        xcri_groups = self._root.find('PhysicalDescriptions').find('CRIs').findall('CRIGroup')
        self.cri_groups = [CriGroup(i) for i in xcri_groups]
        xmodels = self._root.find('Models').findall('Model')
        self.models = [Model(i) for i in xmodels]
        xgeometry_collect = self._root.find('Geometries')
        xgeometries = xgeometry_collect.findall('Geometry') + \
            xgeometry_collect.findall('Axis') + \
            xgeometry_collect.findall('FilterBeam') + \
            xgeometry_collect.findall('FilterColor') + \
            xgeometry_collect.findall('FilterGobo') + \
            xgeometry_collect.findall('FilterShaper') + \
            xgeometry_collect.findall('Beam')
        self.geometries = [Geometry(i) for i in xgeometries]
        for i in xgeometry_collect.findall('GeometryReference'):
            self.geometries.append(GeometryReference(i))
        xdmx_modes = self._root.find('DMXModes').findall('DMXMode')
        self.dmx_modes = [DmxMode(i) for i in xdmx_modes]
        xrevisions = self._root.find('Revisions').findall('Revision')
        self.revisions = [Revision(i) for i in xrevisions]


class ActivationGroup:

    def __init__(self, XActivationGroup):
        self.name = XActivationGroup.get('Name')


class FeatureGroup:

    def __init__(self, XFeatureGroup):
        self.name = XFeatureGroup.get('Name')
        self.pretty = XFeatureGroup.get('Pretty')
        self.features = [Feature(i) for i in XFeatureGroup.findall('Feature')]


class Feature:

    def __init__(self, XFeature):
        self.name = XFeature.get('Name')


class Attribute:

    def __init__(self, XAttribute):
        self.name = XAttribute.get('Name')
        self.pretty = XAttribute.get('Pretty')
        self.activation_group = XAttribute.get('ActivationGroup')
        self.feature = XAttribute.get('Feature')
        self.main_attribute = XAttribute.get('MainAttribute')
        self.physical_unit = XAttribute.get('PhysicalUnit')
        self.color = XAttribute.get('Color')


class Wheel:

    def __init__(self, XWheel):
        self.name = XWheel.get('Name')
        self.wheel_slots = [WheelSlot(i) for i in XWheel.findall('Slot')]


class WheelSlot:

    def __init__(self, XWheelSlot):
        self.name = XWheelSlot.get('Name')
        self.color = ColorCIE(XWheelSlot.get('Color'))
        self.filter = XWheelSlot.get('Filter')
        self.media_file_name = XWheelSlot.get('MediaFileName')
        self.facets = [PrismFacet(i) for i in XWheelSlot.findall('Facet')]


class PrismFacet:

    def __init__(self, XPrismFacet):
        self.color = ColorCIE(XPrismFacet.get('Color'))
        self.rotation = Rotation(XPrismFacet.get('Rotation'))


class Emitter:

    def __init__(self, XEmitter):
        self.name = XEmitter.get('Name')
        self.color = ColorCIE(XEmitter.get('Color'))
        try:
            self.dominant_wave_length = float(XEmitter.get('DominantWaveLength'))
        except TypeError:
            self.dominant_wave_length = None
        self.diode_part = XEmitter.get('DiodePart')
        self.measurements = [Measurement(i) for i in XEmitter.findall('Measurement')]


class Filter:

    def __init__(self, XFilter):
        self.name = XFilter.get('Name')
        self.color = ColorCIE(XFilter.get('Color'))
        self.measurements = [Measurement(i) for i in XFilter.findall('Measurement')]


class Measurement:

    def __init__(self, XMeasurement):
        self.physical = float(XMeasurement.get('Physical'))
        try:
            self.luminous_intensity = float(XMeasurement.get('LuminousIntensity'))
        except TypeError:
            self.luminous_intensity = None
        try:
            self.transmission = float(XMeasurement.get('Transmission'))
        except TypeError:
            self.transmission = None
        self.interpolation_to = XMeasurement.get('InterpolationTo', default='Linear')
        self.measurement_points = [MeasurementPoint(i) for i in XMeasurement.findall('MeasurementPoint')]


class MeasurementPoint:

    def __init__(self, XMeasurementPoint):
        self.wave_length = float(XMeasurementPoint.get('WaveLength'))
        self.energy = float(XMeasurementPoint.get('Energy'))


class ColorSpace:

    def __init__(self, XColorSpace):
        self.mode = XColorSpace.get('Mode', default='sRGB')
        if self.mode == 'Custom':
            self.red = ColorCIE(XColorSpace.get('Red'))
            self.green = ColorCIE(XColorSpace.get('Green'))
            self.blue = ColorCIE(XColorSpace.get('Blue'))
            self.white_point = ColorCIE(XColorSpace.get('WhitePoint'))


class DmxProfile:

    def __init__(self, XDMXProfile):
        self._xml = XDMXProfile


class CriGroup:

    def __init__(self, XCRIGroup):
        self.color_temperature = float(XCRIGroup.get('ColorTemperature', default=6000))
        self.cris = [Cri(i) for i in XCRIGroup.findall('CRI')]


class Cri:

    def __init__(self, XCRI):
        self.ces = XCRI.get('CES', default='CES01')
        self.color_temperature = int(XCRI.get('ColorTemperature', default=100))


class Model:

    def __init__(self, XModel):
        self.name = XModel.get('Name')
        self.length = float(XModel.get('Length', default=0))
        self.width = float(XModel.get('Width', default=0))
        self.height = float(XModel.get('Height', default=0))
        self.primitive_type = XModel.get('PrimitiveType', default='Undefined')
        self.file = XModel.get('File')


class Geometry:

    def __init__(self, XGeometry):
        self.geometry_type = XGeometry.tag
        self.name = XGeometry.get('Name')
        self.model = XGeometry.get('Model')
        self.position = Matrix(XGeometry.get('position', default='0'))
        if self.geometry_type == 'Beam':
            self.lamp_type = XGeometry.get('LampType', default='Discharge')
            self.power_consumption = float(XGeometry.get('PowerConsumption', default=1000))
            self.luminous_flux = float(XGeometry.get('LuminousFlux', default=10000))
            self.color_temperature = float(XGeometry.get('ColorTemperature', default=6000))
            self.beam_angle = float(XGeometry.get('BeamAngle', default=25))
            self.field_angle = float(XGeometry.get('FieldAngle', default=25))
            self.beam_radius = float(XGeometry.get('BeamRadius', default=0.05))
            self.beam_type = XGeometry.get('BeamType', default='Wash')
            self.color_rendering_index = int(XGeometry.get('ColorRenderingIndex', default=100))
        self.geometries = [Geometry(i) for i in
                           XGeometry.findall('Geometry') +
                           XGeometry.findall('Axis') +
                           XGeometry.findall('FilterBeam') +
                           XGeometry.findall('FilterColor') +
                           XGeometry.findall('FilterGobo') +
                           XGeometry.findall('FilterShaper') +
                           XGeometry.findall('Beam')]
        for i in XGeometry.findall('GeometryReference'):
            self.geometries.append(GeometryReference(i))


class GeometryReference:

    def __init__(self, XGeometryReference):
        self.name = XGeometryReference.get('Name')
        self.position = Matrix(XGeometryReference.get('Position', default='0'))
        self.geometry = XGeometryReference.get('Geometry')
        self.model = XGeometryReference.get('Model')
        self.breaks = [Break(i) for i in XGeometryReference.findall('Break')]


class Break:

    def __init__(self, XBreak):
        self.dmx_offset = DmxAddress(XBreak.get('DMXOffset'))
        self.dmx_break = int(XBreak.get('DMXBreak', default=1))


class DmxMode:

    def __init__(self, XDMXMode):
        self.name = XDMXMode.get('Name')
        self.geometry = XDMXMode.get('Geometry')
        self.dmx_channels = [DmxChannel(i) for i in XDMXMode.find('DMXChannels').findall('DMXChannel')]
        self.relations = [Relation(i) for i in XDMXMode.find('Relations').findall('Relation')]
        try:
            self.ft_macros = [Macro(i) for i in XDMXMode.find('FTMacros').findall('FTMacro')]
        except AttributeError:
            pass


class DmxChannel:

    def __init__(self, XDMXChannel):
        self.dmx_break = int(XDMXChannel.get('DMXBreak'))
        self.offset = [int(i) for i in XDMXChannel.get('Offset').split(',')]
        self.default = DmxValue(XDMXChannel.get('Default', default='0/1'))
        self.highlight = DmxValue(XDMXChannel.get('Highlight'))
        self.geometry = XDMXChannel.get('Geometry')
        self.logical_channels = [LogicalChannel(i) for i in XDMXChannel.findall('LogicalChannel')]


class LogicalChannel:

    def __init__(self, XLogicalChannel):
        self.attribute = XLogicalChannel.get('Attribute')
        self.snap = XLogicalChannel.get('Snap', default='No')
        self.master = XLogicalChannel.get('Master', default='None')
        self.mib_fade = float(XLogicalChannel.get('MibFade', default=0))
        self.dmx_change_time_limit = float(XLogicalChannel.get('DMXChangeTimeLimit', default=0))
        self.channel_functions = [ChannelFunction(i) for i in XLogicalChannel.findall('ChannelFunction')]


class ChannelFunction:

    def __init__(self, XChannelFunction):
        self.name = XChannelFunction.get('Name')
        self.attribute = XChannelFunction.get('Attribute', default='NoFeature')
        self.original_attribute = XChannelFunction.get('OriginalAttribute')
        self.dmx_from = DmxValue(XChannelFunction.get('DMXFrom', default='0/1'))
        self.physical_from = float(XChannelFunction.get('PhysicalFrom', default=0))
        self.physical_to = float(XChannelFunction.get('PhysicalTo', default=1))
        self.real_fade = float(XChannelFunction.get('RealFade', default=0))
        self.wheel = XChannelFunction.get('Wheel')
        self.emitter = XChannelFunction.get('Emitter')
        self.filter = XChannelFunction.get('Filter')
        self.dmx_invert = XChannelFunction.get('DMXInvert', default='No')
        self.mode_master = XChannelFunction.get('ModeMaster')
        self.mode_from = DmxValue(XChannelFunction.get('ModeFrom', default='0/1'))
        self.mode_to = DmxValue(XChannelFunction.get('ModeTo', default='0/1'))
        self.channel_sets = [ChannelSet(i) for i in XChannelFunction.findall('ChannelSet')]


class ChannelSet:

    def __init__(self, XChannelSet):
        self.name = XChannelSet.get('Name')
        self.dmx_from = DmxValue(XChannelSet.get('DMXFrom', default='0/1'))
        self.physical_from = float(XChannelSet.get('PhysicalFrom', default=0))
        self.physical_to = float(XChannelSet.get('PhysicalTo', default=1))
        self.wheel_slot_index = int(XChannelSet.get('WheelSlotIndex', default=1))


class Relation:

    def __init__(self, XRelation):
        self.name = XRelation.get('Name')
        self.master = XRelation.get('Master')
        self.follower = XRelation.get('Follower')
        self.type = XRelation.get('Type')


class Macro:

    def __init__(self, XMacro):
        self.name = XMacro.get('Name')
        try:
            self.dmx_steps = [MacroDmxStep(i) for i in XMacro.find('MacroDMX').findall('MacroDMXStep')]
        except AttributeError:
            pass
        try:
            self.visual_steps = [MacroVisualStep(i) for i in XMacro.find('MacroVisual').findall('MacroVisualStep')]
        except AttributeError:
            pass


class MacroDmxStep:

    def __init__(self, XMacroDMXStep):
        self.duration = int(XMacroDMXStep.get('Duration'))
        self.dmx_values = [MacroDmxValue(i) for i in XMacroDMXStep.findall('MacroDMXValue')]


class MacroDmxValue:

    def __init__(self, XMacroDMXValue):
        self.value = DmxValue(XMacroDMXValue.get('Value'))
        self.dmx_channel = XMacroDMXValue.get('DMXChannel')


class MacroVisualStep:

    def __init__(self, XMacroVisualStep):
        self.duration = int(XMacroVisualStep.get('Duration'))
        self.fade = float(XMacroVisualStep.get('Fade', default=0))
        self.delay = float(XMacroVisualStep.get('Delay', default=0))
        self.visual_values = [MacroVisualValue(i) for i in XMacroVisualStep.findall('MacroVisualValue')]


class MacroVisualValue:

    def __init__(self, XMacroVisualValue):
        self.value = DmxValue(XMacroVisualValue.get('Value'))
        self.channel_function = XMacroVisualValue.get('ChannelFunction')


class Revision:

    def __init__(self, XRevision):
        self.text = XRevision.get('Text')
        self.date = XRevision.get('Date')
        self.user_id = int(XRevision.get('UserID'))
