import sigrokdecode as srd

class SignalPolarityError(Exception):
    pass

class Annotation:
    (L, M, H, X) = range(4)

class Pin:
    (SDO1, SDO2) = range(2)

class Decoder(srd.Decoder):
    api_version = 3
    id = '3slad'
    name = '3slad'
    longname = '3SLAD'
    desc = '3 State Logic Analyzer Decoder'
    license = 'mit'
    inputs = ['logic']
    outputs = ['empty']
    tags = ['Embedded/industrial']
    channels = (
        {'id': 'sdo1', 'name': 'SDO1', 'desc': 'Data1'},
        {'id': 'sdo2', 'name': 'SDO2', 'desc': 'Data2'}
    )
    options = (
        {'id': 'polarity', 'desc': 'Signal polarity', 'default': 'active-low',
            'values': ('active-low', 'active-high')},
    )
    annotations = (
        ('L', 'Low'),
        ('M', 'Medium'),
        ('H', 'High'),
        ('X', 'X'),
    )

    def __init__(self):
        self.out_ann = None
        self.h_block_s = None
        self.m_block_s = None
        self.l_block_s = None
        self.x_block_s = None

    def start(self):
        self.out_ann = self.register(srd.OUTPUT_ANN)

        if self.options['polarity'] == 'active-low':
            self.active_signal = 'l'
            self.passive_signal = 'h'
            self.front_edge = 'f'
            self.back_edge = 'r'
        elif self.options['polarity'] == 'active-high':
            self.active_signal = 'h'
            self.passive_signal = 'l'
            self.front_edge = 'r'
            self.back_edge = 'f'
        else:
            raise SignalPolarityError('Unexpected type of signal polarity')

    def reset(self):
        self.h_block_s = None
        self.m_block_s = None
        self.l_block_s = None
        self.x_block_s = None

    def decode(self):
        if not self.active_signal or not self.passive_signal or not self.front_edge or not self.back_edge:
            raise SignalPolarityError('Polarity of signal is not set')
    
        while True:
            # 0 x 0
            self.wait({Pin.SDO1: self.passive_signal, Pin.SDO2: self.passive_signal})
            self.l_block_s = self.samplenum

            pins = self.wait([{Pin.SDO1: self.front_edge, Pin.SDO2: self.front_edge},
                              {Pin.SDO1: self.front_edge},
                              {Pin.SDO2: self.front_edge}])
            # 1 x 1
            if self.matched[0]:
                self.put(self.l_block_s, self.samplenum, self.out_ann, [Annotation.L, ['Low', 'L']])

                self.h_block_s = self.samplenum

                pins = self.wait([{Pin.SDO1: self.back_edge, Pin.SDO2: self.back_edge},
                                  {Pin.SDO1: self.back_edge, Pin.SDO2: self.active_signal},
                                  {Pin.SDO1: self.active_signal, Pin.SDO2: self.back_edge}])
                # 0 x 0
                if self.matched[0]:
                    self.put(self.h_block_s, self.samplenum, self.out_ann, [Annotation.H, ['High', 'H']])
                # 0 x 1
                elif self.matched[1]:
                    self.put(self.h_block_s, self.samplenum, self.out_ann, [Annotation.H, ['High', 'H']])

                    self.m_block_s = self.samplenum

                    pins = self.wait([{Pin.SDO1: self.front_edge, Pin.SDO2: self.back_edge},
                                      {Pin.SDO1: self.front_edge, Pin.SDO2: self.active_signal},
                                      {Pin.SDO1: self.passive_signal, Pin.SDO2: self.back_edge}])
                    # 1 x 0
                    if self.matched[0]:
                        self.put(self.m_block_s, self.samplenum, self.out_ann, [Annotation.M, ['Medium', 'M']])

                        self.x_block_s = self.samplenum

                        pins = self.wait([{Pin.SDO1: self.back_edge, Pin.SDO2: self.front_edge},
                                          {Pin.SDO1: self.back_edge, Pin.SDO2: self.passive_signal},
                                          {Pin.SDO1: self.active_signal, Pin.SDO2: self.front_edge}])
                        # 0 x 1
                        if self.matched[0]:
                            self.put(self.x_block_s, self.samplenum, self.out_ann, [Annotation.X, ['X State', 'X']])
                        # 0 x 0
                        elif self.matched[1]:
                            self.put(self.x_block_s, self.samplenum, self.out_ann, [Annotation.X, ['X State', 'X']])
                        # 1 x 1
                        elif self.matched[2]:
                            self.put(self.x_block_s, self.samplenum, self.out_ann, [Annotation.X, ['X State', 'X']])

                    # 1 x 1
                    elif self.matched[1]:
                        self.put(self.m_block_s, self.samplenum, self.out_ann, [Annotation.M, ['Medium', 'M']])

                        self.h_block_s = self.samplenum

                        pins = self.wait([{Pin.SDO1: self.back_edge, Pin.SDO2: self.back_edge},
                                          {Pin.SDO1: self.back_edge, Pin.SDO2: self.active_signal},
                                          {Pin.SDO1: self.active_signal, Pin.SDO2: self.back_edge}])
                        # 0 x 0
                        if self.matched[0]:
                            self.put(self.h_block_s, self.samplenum, self.out_ann, [Annotation.H, ['High', 'H']])
                        # 0 x 1
                        elif self.matched[1]:
                            self.put(self.h_block_s, self.samplenum, self.out_ann, [Annotation.H, ['High', 'H']])
                        # 1 x 0
                        elif self.matched[2]:
                            self.put(self.h_block_s, self.samplenum, self.out_ann, [Annotation.H, ['High', 'H']])

                    # 0 x 0
                    elif self.matched[2]:
                        self.put(self.m_block_s, self.samplenum, self.out_ann, [Annotation.M, ['Medium', 'M']])

                # 1 x 0
                elif self.matched[2]:
                    self.put(self.h_block_s, self.samplenum, self.out_ann, [Annotation.H, ['High', 'H']])

                    self.x_block_s = self.samplenum

                    pins = self.wait([{Pin.SDO1: self.back_edge, Pin.SDO2: self.front_edge},
                                      {Pin.SDO1: self.back_edge, Pin.SDO2: self.passive_signal},
                                      {Pin.SDO1: self.active_signal, Pin.SDO2: self.front_edge}])
                    # 0 x 1
                    if self.matched[0]:
                        self.put(self.x_block_s, self.samplenum, self.out_ann, [Annotation.X, ['X State', 'X']])

                        self.m_block_s = self.samplenum

                        pins = self.wait([{Pin.SDO1: self.front_edge, Pin.SDO2: self.back_edge},
                                          {Pin.SDO1: self.front_edge, Pin.SDO2: self.active_signal},
                                          {Pin.SDO1: self.passive_signal, Pin.SDO2: self.back_edge}])
                        if self.matched[0]:
                            self.put(self.m_block_s, self.samplenum, self.out_ann, [Annotation.M, ['Medium', 'M']])
                        elif self.matched[1]:
                            self.put(self.m_block_s, self.samplenum, self.out_ann, [Annotation.M, ['Medium', 'M']])
                        elif self.matched[2]:
                            self.put(self.m_block_s, self.samplenum, self.out_ann, [Annotation.M, ['Medium', 'M']])

                    # 0 x 0
                    elif self.matched[1]:
                        self.put(self.x_block_s, self.samplenum, self.out_ann, [Annotation.X, ['X State', 'X']])

                    # 1 x 1
                    elif self.matched[2]:
                        self.put(self.x_block_s, self.samplenum, self.out_ann, [Annotation.X, ['X State', 'X']])

                        self.h_block_s = self.samplenum

                        pins = self.wait([{Pin.SDO1: self.back_edge, Pin.SDO2: self.back_edge},
                                          {Pin.SDO1: self.back_edge, Pin.SDO2: self.active_signal},
                                          {Pin.SDO1: self.active_signal, Pin.SDO2: self.back_edge}])
                        # 0 x 0
                        if self.matched[0]:
                            self.put(self.h_block_s, self.samplenum, self.out_ann, [Annotation.H, ['High', 'H']])
                        # 0 x 1
                        elif self.matched[1]:
                            self.put(self.h_block_s, self.samplenum, self.out_ann, [Annotation.H, ['High', 'H']])
                        # 1 x 0
                        elif self.matched[2]:
                            self.put(self.h_block_s, self.samplenum, self.out_ann, [Annotation.H, ['High', 'H']])




            # 1 x 0
            elif self.matched[1]:
                self.put(self.l_block_s, self.samplenum, self.out_ann, [Annotation.L, ['Low', 'L']])
                
                self.x_block_s = self.samplenum

                pins = self.wait([{Pin.SDO1: self.back_edge, Pin.SDO2: self.front_edge},
                                  {Pin.SDO1: self.back_edge, Pin.SDO2: self.passive_signal},
                                  {Pin.SDO1: self.active_signal, Pin.SDO2: self.front_edge}])
                # 0 x 1
                if self.matched[0]:
                    self.put(self.x_block_s, self.samplenum, self.out_ann, [Annotation.X, ['X State', 'X']])

                    self.m_block_s = self.samplenum

                    pins = self.wait([{Pin.SDO1: self.front_edge, Pin.SDO2: self.back_edge},
                                      {Pin.SDO1: self.front_edge, Pin.SDO2: self.active_signal},
                                      {Pin.SDO1: self.passive_signal, Pin.SDO2: self.back_edge}])
                    # 1 x 0
                    if self.matched[0]:
                        self.put(self.m_block_s, self.samplenum, self.out_ann, [Annotation.M, ['Medium', 'M']])

                        self.x_block_s = self.samplenum

                        pins = self.wait([{Pin.SDO1: self.back_edge, Pin.SDO2: self.front_edge},
                                          {Pin.SDO1: self.back_edge, Pin.SDO2: self.passive_signal},
                                          {Pin.SDO1: self.active_signal, Pin.SDO2: self.front_edge}])
                        # 0 x 1
                        if self.matched[0]:
                            self.put(self.x_block_s, self.samplenum, self.out_ann, [Annotation.X, ['X State', 'X']])
                        # 0 x 0
                        elif self.matched[1]:
                            self.put(self.x_block_s, self.samplenum, self.out_ann, [Annotation.X, ['X State', 'X']])
                        # 1 x 1
                        elif self.matched[2]:
                            self.put(self.x_block_s, self.samplenum, self.out_ann, [Annotation.X, ['X State', 'X']])

                # 0 x 0
                elif self.matched[1]:
                    self.put(self.x_block_s, self.samplenum, self.out_ann, [Annotation.X, ['X State', 'X']])

                # 1 x 1
                elif self.matched[2]:
                    self.put(self.x_block_s, self.samplenum, self.out_ann, [Annotation.X, ['X State', 'X']])

                    self.h_block_s = self.samplenum

                    pins = self.wait([{Pin.SDO1: self.back_edge, Pin.SDO2: self.back_edge},
                                      {Pin.SDO1: self.back_edge, Pin.SDO2: self.active_signal},
                                      {Pin.SDO1: self.active_signal, Pin.SDO2: self.back_edge}])
                    # 0 x 0
                    if self.matched[0]:
                        self.put(self.h_block_s, self.samplenum, self.out_ann, [Annotation.H, ['High', 'H']])

                    # 0 x 1
                    elif self.matched[1]:
                        self.put(self.h_block_s, self.samplenum, self.out_ann, [Annotation.H, ['High', 'H']])

                        self.m_block_s = self.samplenum

                        pins = self.wait([{Pin.SDO1: self.front_edge, Pin.SDO2: self.back_edge},
                                          {Pin.SDO1: self.front_edge, Pin.SDO2: self.active_signal},
                                          {Pin.SDO1: self.passive_signal, Pin.SDO2: self.back_edge}])
                        if self.matched[0]:
                            self.put(self.m_block_s, self.samplenum, self.out_ann, [Annotation.M, ['Medium', 'M']])
                        elif self.matched[1]:
                            self.put(self.m_block_s, self.samplenum, self.out_ann, [Annotation.M, ['Medium', 'M']])
                        elif self.matched[2]:
                            self.put(self.m_block_s, self.samplenum, self.out_ann, [Annotation.M, ['Medium', 'M']])

                    # 1 x 0
                    elif self.matched[2]:
                        self.put(self.h_block_s, self.samplenum, self.out_ann, [Annotation.H, ['High', 'H']])

                        self.x_block_s = self.samplenum

                        pins = self.wait([{Pin.SDO1: self.back_edge, Pin.SDO2: self.front_edge},
                                          {Pin.SDO1: self.back_edge, Pin.SDO2: self.passive_signal},
                                          {Pin.SDO1: self.active_signal, Pin.SDO2: self.front_edge}])
                        if self.matched[0]:
                            self.put(self.x_block_s, self.samplenum, self.out_ann, [Annotation.X, ['X State', 'X']])
                        elif self.matched[1]:
                            self.put(self.x_block_s, self.samplenum, self.out_ann, [Annotation.X, ['X State', 'X']])
                        elif self.matched[2]:
                            self.put(self.x_block_s, self.samplenum, self.out_ann, [Annotation.X, ['X State', 'X']])



            # 0 x 1
            elif self.matched[2]:
                self.put(self.l_block_s, self.samplenum, self.out_ann, [Annotation.L, ['Low', 'L']])

                self.m_block_s = self.samplenum

                pins = self.wait([{Pin.SDO1: self.front_edge, Pin.SDO2: self.back_edge},
                                  {Pin.SDO1: self.front_edge, Pin.SDO2: self.active_signal},
                                  {Pin.SDO1: self.passive_signal, Pin.SDO2: self.back_edge}])
                # 1 x 0
                if self.matched[0]:
                    self.put(self.m_block_s, self.samplenum, self.out_ann, [Annotation.M, ['Medium', 'M']])

                    self.x_block_s = self.samplenum

                    pins = self.wait([{Pin.SDO1: self.back_edge, Pin.SDO2: self.front_edge},
                                      {Pin.SDO1: self.back_edge, Pin.SDO2: self.passive_signal},
                                      {Pin.SDO1: self.active_signal, Pin.SDO2: self.front_edge}])
                    # 0 x 1
                    if self.matched[0]:
                        self.put(self.x_block_s, self.samplenum, self.out_ann, [Annotation.X, ['X State', 'X']])

                        self.m_block_s = self.samplenum

                        pins = self.wait([{Pin.SDO1: self.front_edge, Pin.SDO2: self.back_edge},
                                          {Pin.SDO1: self.front_edge, Pin.SDO2: self.active_signal},
                                          {Pin.SDO1: self.passive_signal, Pin.SDO2: self.back_edge}])
                        if self.matched[0]:
                            self.put(self.m_block_s, self.samplenum, self.out_ann, [Annotation.M, ['Medium', 'M']])
                        elif self.matched[1]:
                            self.put(self.m_block_s, self.samplenum, self.out_ann, [Annotation.M, ['Medium', 'M']])
                        elif self.matched[2]:
                            self.put(self.m_block_s, self.samplenum, self.out_ann, [Annotation.M, ['Medium', 'M']])

                    # 0 x 0
                    elif self.matched[1]:
                        self.put(self.x_block_s, self.samplenum, self.out_ann, [Annotation.X, ['X State', 'X']])

                    # 1 x 1
                    elif self.matched[2]:
                        self.put(self.x_block_s, self.samplenum, self.out_ann, [Annotation.X, ['X State', 'X']])

                        self.h_block_s = self.samplenum

                        pins = self.wait([{Pin.SDO1: self.back_edge, Pin.SDO2: self.back_edge},
                                          {Pin.SDO1: self.back_edge, Pin.SDO2: self.active_signal},
                                          {Pin.SDO1: self.active_signal, Pin.SDO2: self.back_edge}])
                        if self.matched[0]:
                            self.put(self.h_block_s, self.samplenum, self.out_ann, [Annotation.H, ['High', 'H']])
                        elif self.matched[1]:
                            self.put(self.h_block_s, self.samplenum, self.out_ann, [Annotation.H, ['High', 'H']])
                        elif self.matched[2]:
                            self.put(self.h_block_s, self.samplenum, self.out_ann, [Annotation.H, ['High', 'H']])


                # 1 x 1
                elif self.matched[1]:
                    self.put(self.m_block_s, self.samplenum, self.out_ann, [Annotation.M, ['Medium', 'M']])

                    self.h_block_s = self.samplenum

                    pins = self.wait([{Pin.SDO1: self.back_edge, Pin.SDO2: self.back_edge},
                                      {Pin.SDO1: self.back_edge, Pin.SDO2: self.active_signal},
                                      {Pin.SDO1: self.active_signal, Pin.SDO2: self.back_edge}])
                    # 0 x 0
                    if self.matched[0]:
                        self.put(self.h_block_s, self.samplenum, self.out_ann, [Annotation.H, ['High', 'H']])

                    # 0 x 1
                    elif self.matched[1]:
                        self.put(self.h_block_s, self.samplenum, self.out_ann, [Annotation.H, ['High', 'H']])

                        self.m_block_s = self.samplenum

                        pins = self.wait([{Pin.SDO1: self.front_edge, Pin.SDO2: self.back_edge},
                                          {Pin.SDO1: self.front_edge, Pin.SDO2: self.active_signal},
                                          {Pin.SDO1: self.passive_signal, Pin.SDO2: self.back_edge}])
                        if self.matched[0]:
                            self.put(self.m_block_s, self.samplenum, self.out_ann, [Annotation.M, ['Medium', 'M']])
                        elif self.matched[1]:
                            self.put(self.m_block_s, self.samplenum, self.out_ann, [Annotation.M, ['Medium', 'M']])
                        elif self.matched[2]:
                            self.put(self.m_block_s, self.samplenum, self.out_ann, [Annotation.M, ['Medium', 'M']])

                    # 1 x 0
                    elif self.matched[2]:
                        self.put(self.h_block_s, self.samplenum, self.out_ann, [Annotation.H, ['High', 'H']])

                        self.x_block_s = self.samplenum

                        pins = self.wait([{Pin.SDO1: self.back_edge, Pin.SDO2: self.front_edge},
                                          {Pin.SDO1: self.back_edge, Pin.SDO2: self.passive_signal},
                                          {Pin.SDO1: self.active_signal, Pin.SDO2: self.front_edge}])
                        if self.matched[0]:
                            self.put(self.x_block_s, self.samplenum, self.out_ann, [Annotation.X, ['X State', 'X']])
                        elif self.matched[1]:
                            self.put(self.x_block_s, self.samplenum, self.out_ann, [Annotation.X, ['X State', 'X']])
                        elif self.matched[2]:
                            self.put(self.x_block_s, self.samplenum, self.out_ann, [Annotation.X, ['X State', 'X']])

                # 0 x 0
                elif self.matched[2]:
                    self.put(self.m_block_s, self.samplenum, self.out_ann, [Annotation.M, ['Medium', 'M']])