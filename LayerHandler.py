class LayerHandler(object):
    is_tool1_initialized = False
    is_tool2_initialized = False


    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(LayerHandler, cls).__new__(cls)
            return cls.instance


    def __init__(self, iface):
        self.iface = iface

    def init_tool1(self):
        if is_tool1_initialized:

