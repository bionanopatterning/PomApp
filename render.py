import json

def parse_feature_library(feature_library_path):
    with open(feature_library_path, 'r') as f:
        flist = json.load(f)
    feature_library = dict()
    for f in flist:
        feature_definition = FeatureLibraryFeature.from_dict(f)
        feature_library[feature_definition.title] = feature_definition
    return feature_library


class FeatureLibraryFeature:
    DEFAULT_COLOURS = [(66 / 255, 214 / 255, 164 / 255),
                       (255 / 255, 243 / 255, 0 / 255),
                       (255 / 255, 104 / 255, 0 / 255),
                       (255 / 255, 13 / 255, 0 / 255),
                       (174 / 255, 0 / 255, 255 / 255),
                       (21 / 255, 0 / 255, 255 / 255),
                       (0 / 255, 136 / 255, 266 / 255),
                       (0 / 255, 247 / 255, 255 / 255),
                       (0 / 255, 255 / 255, 0 / 255)]
    CLR_COUNTER = 0
    SORT_TITLE = "\n"

    def __init__(self):
        self.title = "New feature"
        self.colour = FeatureLibraryFeature.DEFAULT_COLOURS[FeatureLibraryFeature.CLR_COUNTER % len(FeatureLibraryFeature.DEFAULT_COLOURS)]
        self.box_size = 64
        self.brush_size = 10.0 # nm
        self.alpha = 1.0
        self.use = True
        self.dust = 1.0
        self.level = 128
        self.render_alpha = 1.0
        self.hide = False
        FeatureLibraryFeature.CLR_COUNTER += 1

    @property
    def rgb(self):
        r = (self.colour[0] * 255)
        g = (self.colour[1] * 255)
        b = (self.colour[2] * 255)
        return (r, g, b)

    def to_dict(self):
        return vars(self)

    @staticmethod
    def from_dict(data):
        ret = FeatureLibraryFeature()
        ret.title = data['title']
        ret.colour = data['colour']
        ret.box_size = data['box_size']
        ret.brush_size = data['brush_size']
        ret.alpha = data['alpha']
        ret.use = data['use']
        ret.dust = data['dust']
        ret.level = data['level']
        ret.render_alpha = data['render_alpha']
        ret.hide = data['hide']
        return ret

